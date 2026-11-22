"""Detection engine for LogSentinel (Phases 4.3 and 5).

Implements docs/DETECTION_RULES.md (LS-RULE-001/002/003) over the validated
event model:

- Detectors are pure functions of (events, thresholds): no I/O, no printing,
  no network access, no environment access, no wall-clock reads (AR-010).
- Thresholds are supplied via ``AppConfig`` through ``run_all_detectors``;
  this module defines no duplicate defaults (FR-142).
- At most one Finding per (rule, source IP); detectors never deduplicate
  events (Phase 4.1 owns that policy) and never mutate their input.
- ``SyslogEvent`` and unrelated event types never contribute.

Phase 5 (NFR-004/FR-110): every detector exposes an incremental
``observe(event)`` / ``results()`` pair backed by bounded per-IP aggregation
state (the memory envelope NFR-004 explicitly permits). ``detect(events)``
remains the batch compatibility API and is implemented on top of the very
same ``observe``/``results`` code path, so incremental and batch results are
identical by construction. Detector instances reset their state at the
start of ``detect()``; the streaming CLI drives one instance per rule
across a whole run via ``observe`` and reads ``results()`` once at the end.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from .events import (
    FirewallEvent,
    Finding,
    HTTPRequestEvent,
    SSHAuthEvent,
    SecurityEvent,
)

if TYPE_CHECKING:
    from .config import AppConfig

__all__ = [
    "BaseDetector",
    "SSHBruteForceDetector",
    "PortScanDetector",
    "HTTP4xxAbuseDetector",
    "run_all_detectors",
]


class BaseDetector:
    """Common detector contract: threshold plus incremental aggregation.

    ``observe(event)`` feeds one event into bounded per-IP state;
    ``results()`` finalizes and returns the findings in deterministic
    ascending source-IP order. ``detect(events)`` is the batch equivalent:
    reset, observe every event, finalize - one shared algorithm.
    """

    rule_id: ClassVar[str]
    severity: ClassVar[str]

    def __init__(self, threshold: int) -> None:
        if type(threshold) is not int or threshold <= 0:
            raise ValueError(f"threshold must be a positive integer, got {threshold!r}")
        self.threshold = threshold

    def observe(self, event: SecurityEvent) -> None:
        raise NotImplementedError  # pragma: no cover - overridden

    def results(self) -> list[Finding]:
        raise NotImplementedError  # pragma: no cover - overridden

    def _reset(self) -> None:
        raise NotImplementedError  # pragma: no cover - overridden

    def detect(self, events: list[SecurityEvent]) -> list[Finding]:
        """Batch compatibility API (identical results to observe/results)."""
        self._reset()
        for event in events:
            self.observe(event)
        return self.results()


class SSHBruteForceDetector(BaseDetector):
    """LS-RULE-001: SSH brute-force detection (high severity).

    Sliding window with exact half-open semantics ``(t_latest - window,
    t_latest]`` over failed ``SSHAuthEvent`` instances grouped by source IP
    (FR-030, FR-033, FR-121). Successful authentications never count toward
    the threshold and never reset or interrupt the window; they are attached
    to findings as contextual evidence and counted run-wide as
    ``successful_followups``.
    """

    rule_id: ClassVar[str] = "LS-RULE-001"
    severity: ClassVar[str] = "high"

    def __init__(self, threshold: int, window_seconds: int) -> None:
        super().__init__(threshold)
        if type(window_seconds) is not int or window_seconds <= 0:
            raise ValueError(
                f"window_seconds must be a positive integer, got {window_seconds!r}")
        self.window_seconds = window_seconds
        self._reset()

    def _reset(self) -> None:
        self._failures: dict[str, list[SSHAuthEvent]] = {}
        self._success_lines: dict[str, list[str]] = {}
        self._success_counts: dict[str, int] = {}

    def observe(self, event: SecurityEvent) -> None:
        """Accumulate one event into bounded per-IP state (Phase 5)."""
        if not isinstance(event, SSHAuthEvent):
            return
        ip = event.src_ip
        if event.success:
            self._success_counts[ip] = self._success_counts.get(ip, 0) + 1
            self._success_lines.setdefault(ip, []).append(event.raw_line)
        else:
            self._failures.setdefault(ip, []).append(event)

    def results(self) -> list[Finding]:
        findings: list[Finding] = []
        for ip in sorted(self._failures):
            # Chronological (stable (timestamp, kind) sort, FR-111) - the
            # same ordering ``events_by_src_ip`` produced for the batch API.
            window = sorted(
                self._failures[ip], key=lambda e: (e.timestamp, e.kind))
            qualifying = self._qualifying_indices_union(window)
            if not qualifying:
                continue
            first_seen = qualifying[0].timestamp
            last_seen = qualifying[-1].timestamp
            usernames = {event.username for event in qualifying}
            evidence = tuple(event.raw_line for event in qualifying)
            evidence += tuple(self._success_lines.get(ip, ()))
            summary = {
                "failed_count": len(qualifying),
                "distinct_usernames": len(usernames),
                "window_seconds": self.window_seconds,
                "successful_followups": self._success_counts.get(ip, 0),
            }
            findings.append(Finding(
                rule_id=self.rule_id,
                severity=self.severity,
                src_ip=ip,
                first_seen=first_seen,
                last_seen=last_seen,
                evidence=evidence,
                summary=summary,
            ))
        return findings

    def _qualifying_indices_union(
        self, failures: list[SSHAuthEvent]
    ) -> list[SSHAuthEvent]:
        """Union of all failures inside at least one qualifying window, O(n).

        Two-pointer scan over the timestamp-sorted failures; qualifying
        index ranges are merged so overlapping windows aggregate into one
        contiguous qualifying set (FR-122).
        """
        n = len(failures)
        if n < self.threshold:
            return []
        intervals: list[tuple[int, int]] = []
        left = 0
        for right in range(n):
            lower_bound = failures[right].timestamp - self.window_seconds
            while failures[left].timestamp <= lower_bound:
                left += 1
            if right - left + 1 >= self.threshold:
                intervals.append((left, right))
        qualifying: list[SSHAuthEvent] = []
        merge_start = -1
        merge_end = -1
        # ``intervals`` is generated with nondecreasing (left, right) bounds,
        # so no sorting is required before the linear merge below.
        for lo, hi in intervals:
            if lo <= merge_end:  # overlapping or adjacent ranges unite
                merge_end = max(merge_end, hi)
                continue
            if merge_start >= 0:
                qualifying.extend(failures[merge_start:merge_end + 1])
            merge_start, merge_end = lo, hi
        if merge_start >= 0:
            qualifying.extend(failures[merge_start:merge_end + 1])
        return qualifying


class PortScanDetector(BaseDetector):
    """LS-RULE-002: network port-scan detection (medium severity).

    Counts distinct destination ports per source IP across the entire run;
    no time window (FR-031, FR-123). Distinctness is by destination port
    only - destination IP and protocol are irrelevant. Evidence carries
    exactly one first-seen raw line per distinct port.
    """

    rule_id: ClassVar[str] = "LS-RULE-002"
    severity: ClassVar[str] = "medium"

    def __init__(self, threshold: int) -> None:
        super().__init__(threshold)
        self._reset()

    def _reset(self) -> None:
        # ip -> {"ports": set, "first_line": dict, "protocols": set,
        #        "first": ts, "last": ts}  (bounded aggregation state)
        self._state: dict[str, dict[str, object]] = {}

    def observe(self, event: SecurityEvent) -> None:
        if not isinstance(event, FirewallEvent):
            return
        state = self._state.get(event.src_ip)
        if state is None:
            state = {
                "ports": set(), "first_line": {}, "protocols": set(),
                "first": event.timestamp, "last": event.timestamp,
            }
            self._state[event.src_ip] = state
        ports: set[int] = state["ports"]  # type: ignore[assignment]
        first_line: dict[int, str] = state["first_line"]  # type: ignore[assignment]
        protocols: set[str] = state["protocols"]  # type: ignore[assignment]
        ports.add(event.dst_port)
        if event.dst_port not in first_line:
            first_line[event.dst_port] = event.raw_line
        protocols.add(event.protocol)
        state["first"] = min(state["first"], event.timestamp)  # type: ignore[call-overload]
        state["last"] = max(state["last"], event.timestamp)  # type: ignore[call-overload]

    def results(self) -> list[Finding]:
        findings: list[Finding] = []
        for ip in sorted(self._state):
            state = self._state[ip]
            ports: set[int] = state["ports"]  # type: ignore[assignment]
            if len(ports) < self.threshold:
                continue
            first_line: dict[int, str] = state["first_line"]  # type: ignore[assignment]
            protocols: set[str] = state["protocols"]  # type: ignore[assignment]
            evidence = tuple(first_line[port] for port in sorted(ports))
            summary = {
                "distinct_ports": len(ports),
                "ports_sample": sorted(ports)[:20],
                "protocols": sorted(protocols),
            }
            findings.append(Finding(
                rule_id=self.rule_id,
                severity=self.severity,
                src_ip=ip,
                first_seen=state["first"],  # type: ignore[arg-type]
                last_seen=state["last"],  # type: ignore[arg-type]
                evidence=evidence,
                summary=summary,
            ))
        return findings


class HTTP4xxAbuseDetector(BaseDetector):
    """LS-RULE-003: HTTP 4xx abuse detection (medium severity).

    Counts responses with status 400-499 inclusive per source IP across the
    entire run; no time window (FR-032, FR-124). 1xx/2xx/3xx/5xx events never
    contribute. Timestamps span qualifying 4xx events only. Every qualifying
    event's raw line is retained per source IP (bounded aggregation, NFR-004)
    so evidence is never capped.
    """

    rule_id: ClassVar[str] = "LS-RULE-003"
    severity: ClassVar[str] = "medium"

    def __init__(self, threshold: int) -> None:
        super().__init__(threshold)
        self._reset()

    def _reset(self) -> None:
        # ip -> {"lines": [(timestamp, kind, raw_line), ...] in arrival
        #        order, "histogram": {}, "paths": set, "first": ts,
        #        "last": ts}
        self._state: dict[str, dict[str, object]] = {}

    def observe(self, event: SecurityEvent) -> None:
        if not isinstance(event, HTTPRequestEvent):
            return
        if not 400 <= event.status_code <= 499:
            return
        state = self._state.get(event.src_ip)
        if state is None:
            state = {
                "lines": [], "histogram": {}, "paths": set(),
                "first": event.timestamp, "last": event.timestamp,
            }
            self._state[event.src_ip] = state
        lines: list[tuple[int, str, str]] = state["lines"]  # type: ignore[assignment]
        lines.append((event.timestamp, event.kind, event.raw_line))
        histogram: dict[str, int] = state["histogram"]  # type: ignore[assignment]
        key = str(event.status_code)
        histogram[key] = histogram.get(key, 0) + 1
        paths: set[str] = state["paths"]  # type: ignore[assignment]
        paths.add(event.path)
        state["first"] = min(state["first"], event.timestamp)  # type: ignore[call-overload]
        state["last"] = max(state["last"], event.timestamp)  # type: ignore[call-overload]

    def results(self) -> list[Finding]:
        findings: list[Finding] = []
        for ip in sorted(self._state):
            state = self._state[ip]
            lines: list[tuple[int, str, str]] = state["lines"]  # type: ignore[assignment]
            if len(lines) < self.threshold:
                continue
            # Chronological with stable tie order (FR-111): the batch API
            # relied on ``events_by_src_ip``'s stable (timestamp, kind) sort;
            # arrival order equals ingestion order, so a stable sort here
            # reproduces it exactly.
            ordered = sorted(lines, key=lambda item: (item[0], item[1]))
            histogram: dict[str, int] = state["histogram"]  # type: ignore[assignment]
            paths: set[str] = state["paths"]  # type: ignore[assignment]
            summary = {
                "http_4xx_count": len(ordered),
                "status_histogram": {code: histogram[code]
                                     for code in sorted(histogram)},
                "distinct_paths": len(paths),
            }
            findings.append(Finding(
                rule_id=self.rule_id,
                severity=self.severity,
                src_ip=ip,
                first_seen=state["first"],  # type: ignore[arg-type]
                last_seen=state["last"],  # type: ignore[arg-type]
                evidence=tuple(line for _, _, line in ordered),
                summary=summary,
            ))
        return findings


def run_all_detectors(
    events: list[SecurityEvent], config: AppConfig
) -> list[Finding]:
    """Run all three rules with thresholds from ``AppConfig`` (FR-036).

    Batch compatibility API (Phase 4.3 contract preserved). Findings are
    returned in deterministic rule order (LS-RULE-001/002/003), each
    detector emitting at most one finding per source IP in ascending IP
    order. The streaming CLI drives the same detector classes via
    ``observe``/``results`` instead.
    """
    findings: list[Finding] = []
    findings.extend(SSHBruteForceDetector(
        config.ssh_threshold, config.ssh_window_seconds).detect(events))
    findings.extend(PortScanDetector(config.portscan_threshold).detect(events))
    findings.extend(HTTP4xxAbuseDetector(config.http_4xx_threshold).detect(events))
    return findings
