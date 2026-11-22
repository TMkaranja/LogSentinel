"""Unit tests for the LogSentinel reporting engine (Phase 4.4).

Covers the ten approved test categories from the final reporting contract.
Deterministic throughout: no sleeps, no wall-clock reads (generated_at is
a fixed literal), no external resources.
"""

import json
import tempfile
import unittest
from pathlib import Path

from logsentinel.config import AppConfig
from logsentinel.events import ErrorEntry, Finding
from logsentinel.report import (
    MAX_EVIDENCE_LENGTH,
    MAX_REPORTED_ERRORS,
    REPORT_VERSION,
    RunStatistics,
    render_console,
    render_json,
    write_report,
)

GENERATED_AT = "2026-03-10T12:00:00Z"
BACKSLASH = chr(92)


def finding(rule="LS-RULE-001", severity="high", ip="192.0.2.7",
            first=100, last=200, evidence=(), summary=None):
    return Finding(rule_id=rule, severity=severity, src_ip=ip,
                   first_seen=first, last_seen=last,
                   evidence=tuple(evidence),
                   summary=summary if summary is not None else {})


def stats(**overrides):
    values = {"files_scanned": 3, "lines_read": 1204, "events_parsed": 981,
              "malformed": 18, "duplicates": 6, "othersyslog": 12,
              "othersyslog_dropped": 2, "cross_file_duplicates": 4}
    values.update(overrides)
    return RunStatistics(**values)


def err(number, reason="bad line", kind="parse", source=None):
    return ErrorEntry(source_file=source or f"log{number}.txt",
                      line_number=number, reason=reason, kind=kind)


def error_entries(count):
    return [err(i + 1) for i in range(count)]


class TestConstants(unittest.TestCase):
    def test_contract_constants(self):
        self.assertEqual(REPORT_VERSION, 1)
        self.assertEqual(MAX_EVIDENCE_LENGTH, 256)
        self.assertEqual(MAX_REPORTED_ERRORS, 100)


class TestJsonSchema(unittest.TestCase):
    """Category 1/3: schema, determinism, effective configuration."""

    def setUp(self):
        self.findings = [finding()]
        self.config = AppConfig(ssh_threshold=5, strict=True, max_file_mb=64)

    def render(self, findings=None, generated_at=GENERATED_AT, errors=None):
        return render_json(self.findings if findings is None else findings,
                           stats(), self.config, generated_at, errors=errors)

    def test_schema_keys_exact(self):
        payload = json.loads(self.render())
        self.assertEqual(
            set(payload),
            {"report_version", "generated_at", "config_used", "statistics",
             "findings", "errors"})

    def test_report_version(self):
        self.assertEqual(json.loads(self.render())["report_version"], 1)

    def test_config_used_contains_all_seven_settings(self):
        used = json.loads(self.render())["config_used"]
        self.assertEqual(used, {
            "ssh_threshold": 5,
            "ssh_window_seconds": 300,
            "portscan_threshold": 10,
            "http_4xx_threshold": 8,
            "strict": True,
            "max_line_length": 8192,
            "max_file_mb": 64,
        })

    def test_statistics_rendered_field_for_field(self):
        statistics = stats(cross_file_duplicates=7)
        block = json.loads(render_json(self.findings, statistics,
                                       self.config, GENERATED_AT))["statistics"]
        self.assertEqual(block["files_scanned"], 3)
        self.assertEqual(block["lines_read"], 1204)
        self.assertEqual(block["events_parsed"], 981)
        self.assertEqual(block["malformed"], 18)
        self.assertEqual(block["duplicates"], 6)
        self.assertEqual(block["othersyslog"], 12)
        self.assertEqual(block["othersyslog_dropped"], 2)
        self.assertEqual(block["cross_file_duplicates"], 7)  # accepted as-is
        self.assertEqual(block["findings"], 1)               # computed count

    def test_deterministic_for_identical_inputs(self):
        self.assertEqual(self.render(), self.render())

    def test_only_generated_at_varies(self):
        first = json.loads(self.render(generated_at="2026-03-10T12:00:00Z"))
        second = json.loads(self.render(generated_at="2026-03-10T12:00:01Z"))
        self.assertNotEqual(first["generated_at"], second["generated_at"])
        first.pop("generated_at")
        second.pop("generated_at")
        self.assertEqual(first, second)

    def test_findings_sorted_rule_severity_ip(self):
        findings = [finding(rule="LS-RULE-003", severity="medium",
                            ip="203.0.113.9"),
                    finding(rule="LS-RULE-001", severity="high",
                            ip="192.0.2.9"),
                    finding(rule="LS-RULE-001", severity="high",
                            ip="192.0.2.7")]
        rendered = json.loads(self.render(findings=findings))["findings"]
        self.assertEqual(
            [(f["rule_id"], f["src_ip"]) for f in rendered],
            [("LS-RULE-001", "192.0.2.7"), ("LS-RULE-001", "192.0.2.9"),
             ("LS-RULE-003", "203.0.113.9")])

    def test_ensure_ascii_false_preserves_unicode(self):
        findings = [finding(evidence=("café attempt from 192.0.2.7",))]
        rendered = render_json(findings, stats(), AppConfig(), GENERATED_AT)
        self.assertIn("café", rendered)
        self.assertNotIn(BACKSLASH + "u00e9", rendered)

    def test_input_errors_not_mutated(self):
        entries = error_entries(3)
        snapshot = [(e.source_file, e.line_number, e.reason, e.kind)
                    for e in entries]
        self.render(errors=entries)
        self.assertEqual([(e.source_file, e.line_number, e.reason, e.kind)
                          for e in entries], snapshot)

    def test_statistics_type_enforced(self):
        with self.assertRaises(TypeError):
            self.render() if False else render_json(
                self.findings, {"lines_read": 1}, self.config, GENERATED_AT)


class TestRedactionAndCapping(unittest.TestCase):
    """Category 5: adversarial credential fixtures; redaction before cap."""

    FIXTURES = [
        "GET /login?password=hunter2 HTTP/1.1",
        "GET /login?passwd=x&next=1 HTTP/1.1",
        "auth pwd=plain",
        "GET /api?token=abc123 HTTP/1.1",
        "GET /api?access_token=zzz HTTP/1.1",
        "POST refresh_token=rrr",
        "GET /api?api_key=K1 HTTP/1.1",
        "GET /api?apikey=K2 HTTP/1.1",
        "GET /api?my_api_key=K3&x=1 HTTP/1.1",
        "vault secret=topsecret",
        "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig",
        'credentials {"password":"hunter2"}',
        "auth 'token'='quoted'",
        "GET /api?token=T%6Fken%20enc HTTP/1.1",
        "password=a1 token=b2 secret=c3",
        # R5 narrow vocabulary extension (explicit key families only).
        "GET /api?access_key=AK1 HTTP/1.1",
        "private_key=pk-data-42",
        "session_key=sk-777",
        "credential=credval9",
        "auth credentials=credpair8",
        # R5 approved fixes: session identifiers, passphrase/pass_word,
        # signature, and credential-bearing headers (opaque values).
        "session=abcdef123456",
        "sessionid: xyz789",
        "sess=zz9876",
        "GET /api?session_id=qqq321 HTTP/1.1",
        "passphrase=secretphrase",
        "auth pass_word=pw00099",
        "auth pass-word=pw11110",
        "signature=t0psecret99",
        "Cookie: session=abcdef123456; Path=/",
        "Set-Cookie: SESSIONID=xyz789; Path=/",
        "proxy-authorization: Basic dXNlcjpwYXNz",
        "proxy_authentication: Basic cHJveHk6cGFzcw==",
    ]

    def assert_redacted(self, rendered):
        self.assertIn("<REDACTED>", rendered)
        for secret in ("hunter2", "abc123", "zzz", "rrr", "K1", "K2", "K3",
                       "topsecret", "eyJhbGciOiJIUzI1NiJ9", "T%6Fken",
                       "quoted", "plain", "b2", "c3", "a1",
                       "AK1", "pk-data-42", "sk-777", "credval9",
                       "credpair8",
                       "abcdef123456", "xyz789", "zz9876", "qqq321",
                       "secretphrase", "pw00099", "pw11110", "t0psecret99",
                       "dXNlcjpwYXNz", "cHJveHk6cGFzcw=="):
            self.assertNotIn(secret, rendered)

    def test_json_redaction_matrix(self):
        for fixture in self.FIXTURES:
            with self.subTest(fixture=fixture):
                findings = [finding(evidence=(fixture,))]
                self.assert_redacted(
                    render_json(findings, stats(), AppConfig(), GENERATED_AT))

    def test_console_redaction_matrix(self):
        for fixture in self.FIXTURES:
            with self.subTest(fixture=fixture):
                findings = [finding(evidence=(fixture,))]
                self.assert_redacted(
                    render_console(findings, stats(), AppConfig()))

    def test_header_redaction_families(self):
        """R5: Cookie/Set-Cookie/Proxy-Authentication headers redact the
        whole remainder, exactly like Authorization; the Authorization
        behaviour is unchanged.
        """
        for header in ("Cookie: session=abc; Path=/", "Cookie:none",
                       "Set-Cookie: SESSIONID=xyz; HttpOnly",
                       "proxy-authorization: Basic abc",
                       "proxy_authentication: Basic def"):
            with self.subTest(header=header):
                rendered = self._render(header)
                self.assertIn("<REDACTED>", rendered)
                self.assertNotIn("session=abc", rendered)
                self.assertNotIn("SESSIONID", rendered)
                self.assertNotIn("Basic", rendered)
                self.assertNotIn("abc", rendered.replace("<REDACTED>", ""))
        # Authorization unchanged.
        rendered = self._render("Authorization: Bearer eyJ.aaa.bbb")
        self.assertIn("<REDACTED>", rendered)
        self.assertNotIn("eyJ", rendered)

    def _render(self, evidence):
        findings = [finding(evidence=(evidence,))]
        return render_json(findings, stats(), AppConfig(), GENERATED_AT)

    def test_boundary_and_false_positive_regressions(self):
        """R5 regressions: compound words that merely contain vocabulary
        fragments stay unredacted; approved conservative redactions are
        documented.
        """
        must_not_redact = [
            "account_password_reset=1",     # boundary: reset follows
            "client_id=ID123",              # excluded by policy
            "ssh_key=kdata",                # excluded by policy
            "key=abc123",                   # generic key: excluded
            "pin=1234",                     # excluded
            "keyboard=layout",              # ordinary word
            "monkey=ordinary",              # ordinary word
            "signature_algorithm=sha256",   # boundary: algorithm follows
        ]
        for evidence in must_not_redact:
            with self.subTest(evidence=evidence):
                rendered = self._render(evidence)
                self.assertNotIn("<REDACTED>", rendered)
                self.assertIn(evidence, rendered)
        # Documented conservative behaviour: a bare `session=` key value is
        # redacted even if the value is not a real session identifier.
        rendered = self._render("session=planning-meeting")
        self.assertIn("<REDACTED>", rendered)

    def test_normal_values_not_redacted(self):
        findings = [finding(evidence=("Failed password for admin from "
                                      "192.0.2.7 port 1",))]
        rendered = render_json(findings, stats(), AppConfig(), GENERATED_AT)
        self.assertIn("admin", rendered)      # usernames are not credentials
        self.assertNotIn("<REDACTED>", rendered)
        # R5 regression: ordinary fields sharing word prefixes with the
        # extended vocabulary are never redacted.
        ordinary = [finding(evidence=("client_id=ID123 monkey=ordinary "
                                      "keyboard=layout",))]
        excluded = [finding(evidence=("ssh_key=kdata client_id=C9",))]
        for fixtures, expected in (
                (ordinary, ("client_id=ID123", "monkey=ordinary",
                            "keyboard=layout")),
                (excluded, ("ssh_key=kdata", "client_id=C9"))):
            for renderer in (
                    lambda f: render_json(f, stats(), AppConfig(),
                                          GENERATED_AT),
                    lambda f: render_console(f, stats(), AppConfig())):
                rendered = renderer(fixtures)
                for fragment in expected:
                    self.assertIn(fragment, rendered)
                self.assertNotIn("<REDACTED>", rendered)

    def test_redaction_before_truncation(self):
        # Secret well inside the cap: marker intact, value gone.
        fixture = "x" * 200 + " password=verylongsecretvalue continues"
        findings = [finding(evidence=(fixture,))]
        evidence = json.loads(
            render_json(findings, stats(), AppConfig(), GENERATED_AT)
        )["findings"][0]["evidence"][0]
        self.assertIn("<REDACTED>", evidence)
        self.assertNotIn("verylongsecretvalue", evidence)
        self.assertLess(len(evidence), MAX_EVIDENCE_LENGTH + 30)

    def test_secret_straddling_cap_boundary_still_absent(self):
        # Security property of redact-before-cap: even when the redacted
        # value would straddle the truncation point, no secret fragment and
        # no recognizable partial marker of the VALUE survives.
        prefix = "x" * 250
        fixture = prefix + " password=verylongsecretvalue continues"
        findings = [finding(evidence=(fixture,))]
        evidence = json.loads(
            render_json(findings, stats(), AppConfig(), GENERATED_AT)
        )["findings"][0]["evidence"][0]
        self.assertNotIn("verylongsecretvalue", evidence)
        self.assertNotIn("verylongsec", evidence)

    def test_error_reason_redacted_and_capped(self):
        # Verified leakage path: parsers embed str(exc) in reasons, and
        # ipaddress errors embed the offending token from the log line.
        entry = ErrorEntry(source_file="log.txt", line_number=3,
                           reason="'token=abc123' does not appear to be "
                                  "an IPv4 address", kind="parse")
        payload = json.loads(
            render_json([finding()], stats(), AppConfig(), GENERATED_AT,
                        errors=[entry]))
        reason = payload["errors"][0]["reason"]
        self.assertIn("<REDACTED>", reason)
        self.assertNotIn("abc123", reason)

    def test_source_path_redacted_in_json(self):
        """R4 regression (would fail under the previous capping-only
        implementation, which echoed the truncated path): externally
        visible error entries replace the source path with the neutral
        marker - absolute directories, usernames, directory structure and
        filenames never reach the JSON report.
        """
        # Windows absolute path with a username and sensitive directory.
        win = ErrorEntry(
            source_file=r"C:\Users\alice\secret\creds.log",
            line_number=1, reason="bad", kind="input")
        payload = json.loads(
            render_json([finding()], stats(), AppConfig(), GENERATED_AT,
                        errors=[win]))
        self.assertEqual(payload["errors"][0]["source_file"],
                         "[REDACTED_PATH]")
        for fragment in ("alice", "C:\\", "Users", "secret", "creds.log"):
            self.assertNotIn(fragment, json.dumps(payload))
        # POSIX absolute path, likewise.
        posix = ErrorEntry(source_file="/home/bob/.ssh/id_rsa.log",
                           line_number=2, reason="bad", kind="input")
        payload = json.loads(
            render_json([finding()], stats(), AppConfig(), GENERATED_AT,
                        errors=[posix]))
        self.assertEqual(payload["errors"][0]["source_file"],
                         "[REDACTED_PATH]")
        self.assertNotIn("bob", json.dumps(payload))
        self.assertNotIn("id_rsa", json.dumps(payload))
        # The internal entry keeps its path for association/processing.
        self.assertEqual(win.source_file, r"C:\Users\alice\secret\creds.log")
        self.assertEqual(posix.source_file, "/home/bob/.ssh/id_rsa.log")
        # The marker is consistent across entries.
        payload = json.loads(
            render_json([finding()], stats(), AppConfig(), GENERATED_AT,
                        errors=[win, posix]))
        self.assertEqual(
            [e["source_file"] for e in payload["errors"]],
            ["[REDACTED_PATH]", "[REDACTED_PATH]"])


class TestErrorOverflow(unittest.TestCase):
    """Category 7: cap behaviour at 0/100/101/250 and structure."""

    def render_errors(self, count):
        return json.loads(
            render_json([finding()], stats(), AppConfig(), GENERATED_AT,
                        errors=error_entries(count)))

    def test_zero_errors(self):
        payload = self.render_errors(0)
        self.assertEqual(payload["errors"], [])
        self.assertNotIn("errors_overflow", payload)

    def test_exactly_hundred_errors_no_overflow(self):
        payload = self.render_errors(100)
        self.assertEqual(len(payload["errors"]), 100)
        self.assertNotIn("errors_overflow", payload)

    def test_hundred_one_errors(self):
        payload = self.render_errors(101)
        self.assertEqual(len(payload["errors"]), 100)
        self.assertEqual(payload["errors_overflow"],
                         {"shown": 100, "total": 101})

    def test_two_hundred_fifty_errors(self):
        payload = self.render_errors(250)
        self.assertEqual(len(payload["errors"]), 100)
        self.assertEqual(payload["errors_overflow"],
                         {"shown": 100, "total": 250})

    def test_error_entry_structure(self):
        payload = self.render_errors(1)
        self.assertEqual(set(payload["errors"][0]),
                         {"source_file", "line_number", "reason", "kind"})
        self.assertEqual(payload["errors"][0]["line_number"], 1)

    def test_console_overflow_line(self):
        text = render_console([finding()], stats(), AppConfig(),
                              errors=error_entries(143))
        self.assertIn("errors: 100 of 143 shown (43 omitted)", text)
        small = render_console([finding()], stats(), AppConfig(),
                               errors=error_entries(3))
        self.assertNotIn("shown (", small)

    def test_deterministic_error_ordering_preserved(self):
        entries = [err(3, reason="third"), err(1, reason="first")]
        payload = json.loads(
            render_json([finding()], stats(), AppConfig(), GENERATED_AT,
                        errors=entries))
        self.assertEqual([e["reason"] for e in payload["errors"]],
                         ["third", "first"])


class TestConsole(unittest.TestCase):
    """Category 2: grouping, ordering, statistics, language."""

    def test_empty_findings_message(self):
        text = render_console([], stats(), AppConfig())
        self.assertIn("No findings.", text)
        self.assertNotIn("Findings:", text.split("Statistics:")[0].split(
            "No findings.")[-1] if "Findings:" in text else "")

    def test_grouping_and_ordering(self):
        findings = [finding(rule="LS-RULE-002", severity="medium",
                            ip="198.51.100.1"),
                    finding(rule="LS-RULE-001", severity="high",
                            ip="192.0.2.9"),
                    finding(rule="LS-RULE-001", severity="high",
                            ip="192.0.2.7")]
        text = render_console(findings, stats(), AppConfig())
        positions = [text.index(marker) for marker in
                     ("  LS-RULE-001:", "192.0.2.7", "192.0.2.9",
                      "  LS-RULE-002:", "198.51.100.1")]
        self.assertEqual(positions, sorted(positions))

    def test_statistics_block(self):
        text = render_console([], stats(cross_file_duplicates=7), AppConfig())
        self.assertIn("files_scanned: 3", text)
        self.assertIn("cross_file_duplicates: 7", text)
        self.assertIn("findings: 0", text)

    def test_evidence_rendered_redacted_and_capped(self):
        findings = [finding(evidence=("GET /api?token=abc HTTP/1.1",))]
        text = render_console(findings, stats(), AppConfig())
        self.assertIn("evidence: GET /api?token=<REDACTED> HTTP/1.1", text)
        self.assertNotIn("token=abc", text)

    def test_console_mentions_version_and_rule_headers(self):
        text = render_console([finding()], stats(), AppConfig())
        self.assertIn("LogSentinel report (version 1)", text)
        self.assertIn("LS-RULE-001:", text)


class TestWriteReport(unittest.TestCase):
    """Category 8: atomic writes, encoding, failure translation."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_round_trip_utf8(self):
        target = self.tmp / "report.json"
        write_report(str(target), '{"note": "café –日志"}')
        self.assertEqual(target.read_text(encoding="utf-8"),
                         '{"note": "café –日志"}')

    def test_replaces_existing_content(self):
        target = self.tmp / "report.json"
        target.write_text("old", encoding="utf-8")
        write_report(str(target), "new content")
        self.assertEqual(target.read_text(encoding="utf-8"), "new content")

    def test_no_temp_leftovers(self):
        target = self.tmp / "report.json"
        write_report(str(target), "x")
        leftovers = [p.name for p in self.tmp.iterdir()
                     if p.name.startswith(".logsentinel-")]
        self.assertEqual(leftovers, [])

    def test_missing_directory_reporterror(self):
        with self.assertRaises(Exception) as ctx:
            write_report(str(self.tmp / "nope" / "report.json"), "x")
        self.assertIn("cannot write report", str(ctx.exception))

    def test_directory_as_target_reporterror(self):
        with self.assertRaises(Exception) as ctx:
            write_report(str(self.tmp), "x")
        self.assertIn("cannot write report", str(ctx.exception))

    def test_original_preserved_on_failure(self):
        target = self.tmp / "report.json"
        target.write_text("original", encoding="utf-8")
        blocker = self.tmp / "sub"          # a FILE, not a directory:
        blocker.write_text("", encoding="utf-8")
        with self.assertRaises(Exception):
            write_report(str(blocker / "report.json"), "x")
        self.assertEqual(target.read_text(encoding="utf-8"), "original")


class TestPurityAndCompatibility(unittest.TestCase):
    """Category 9/10: purity, no mutation, signature compatibility."""

    def test_errors_parameter_is_keyword_only(self):
        with self.assertRaises(TypeError):
            render_json([finding()], stats(), AppConfig(), GENERATED_AT,
                        error_entries(1))  # positional -> TypeError

    def test_renderers_do_not_mutate_findings(self):
        f = finding(evidence=("GET /api?token=abc",),
                    summary={"failed_count": 8})
        snapshot = (f.rule_id, f.severity, f.src_ip, f.first_seen,
                    f.last_seen, f.evidence, dict(f.summary))
        render_console([f], stats(), AppConfig())
        render_json([f], stats(), AppConfig(), GENERATED_AT)
        self.assertEqual(
            (f.rule_id, f.severity, f.src_ip, f.first_seen, f.last_seen,
             f.evidence, dict(f.summary)), snapshot)

    def test_statistics_not_mutated(self):
        s = stats()
        render_console([], s, AppConfig())
        render_json([], s, AppConfig(), GENERATED_AT)
        self.assertEqual(
            (s.files_scanned, s.lines_read, s.events_parsed, s.malformed,
             s.duplicates, s.othersyslog, s.othersyslog_dropped,
             s.cross_file_duplicates),
            (3, 1204, 981, 18, 6, 12, 2, 4))

    def test_runstatistics_validation(self):
        s = RunStatistics()
        self.assertFalse(hasattr(s, "__dict__"))  # slotted
        with self.assertRaises(Exception):
            RunStatistics(files_scanned=-1)
        for bad in (True, 1.5, "3"):
            with self.subTest(bad=bad):
                with self.assertRaises(Exception):
                    RunStatistics(lines_read=bad)
        with self.assertRaises(Exception):
            s.lines_read = 5  # frozen

    def test_module_purity_no_clock_no_print(self):
        import logsentinel.report as module
        with open(module.__file__, encoding="utf-8") as source_file:
            source = source_file.read()
        for banned in ("import time", "import datetime", "time.time",
                       "os.environ", "print(", "socket", "attack",
                       "compromised"):
            self.assertNotIn(banned, source)
        self.assertIn("import os", source)   # needed for atomic replace only

    def test_rule_and_severity_passthrough(self):
        for rule, severity in (("LS-RULE-002", "medium"),
                               ("LS-RULE-003", "medium")):
            with self.subTest(rule=rule):
                f = finding(rule=rule, severity=severity)
                payload = json.loads(
                    render_json([f], stats(), AppConfig(), GENERATED_AT))
                self.assertEqual(
                    (payload["findings"][0]["rule_id"],
                     payload["findings"][0]["severity"]),
                    (rule, severity))


if __name__ == "__main__":
    unittest.main()
