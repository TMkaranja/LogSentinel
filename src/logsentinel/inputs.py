"""Input discovery for LogSentinel (Phase 4.5, review-corrected).

Implements docs/ARCHITECTURE.md section 5 and docs/REQUIREMENTS.md
FR-002/FR-004/FR-100/FR-101/FR-102 (as amended in REQUIREMENTS section 20):

- Explicit file paths are accepted regardless of extension (user override).
- Directories are recursed for non-hidden ``*.log`` / ``*.txt`` files,
  extension matching is case-insensitive, and traversal is deterministic.
- Duplicate paths are de-duplicated by exact string identity (first
  occurrence wins); no case folding, symlink resolution, or inode identity
  is used (known Windows aliasing limitation, documented).
- Missing, unreadable, invalid, and oversized paths become
  ``ErrorEntry(kind="input")`` data (AR-012); discovery never raises for
  ordinary failures and never implements strict-mode abortion (that is the
  orchestrator's decision, FR-152).
- An empty result is valid: no files, no artificial error, no exception.
- File contents are never read; only filesystem metadata and a read-only
  openability probe (open + immediate close, zero bytes read) are used.

Symbolic-link policy (Phase 4.5 review):
- Traversal never follows symlinked directories (a symlink pointing to a
  parent would otherwise recurse forever). Discovered symlink directories
  are skipped; explicitly supplied symlink directories are refused with an
  error entry rather than expanded.
- Symlinked *files* are accepted through their target's metadata
  (os.stat); the recorded path stays exactly as supplied. Broken symlinks
  produce an error entry.
- Deduplication remains exact-string based; no resolved-path or inode
  identity is introduced.

Leaf module: imports only the standard library and the event model's
ErrorEntry structure.
"""

from __future__ import annotations

import os
import stat as stat_module
from dataclasses import dataclass, field
from pathlib import Path

from .events import ErrorEntry

__all__ = [
    "DEFAULT_MAX_FILE_MB",
    "LOG_EXTENSIONS",
    "LogFile",
    "DiscoverResult",
    "discover_inputs",
]

#: Default safety cap in MiB (FR-102 / FR-140). The orchestrator supplies
#: the effective value from AppConfig.max_file_mb.
DEFAULT_MAX_FILE_MB = 512

#: Extensions accepted during directory discovery (FR-002); case-insensitive.
LOG_EXTENSIONS = frozenset({".log", ".txt"})


@dataclass(frozen=True, slots=True)
class LogFile:
    """One discovered, validated input file (Phase 3 contract)."""

    path: Path
    size_bytes: int


@dataclass(frozen=True, slots=True)
class DiscoverResult:
    """Outcome of input discovery: files plus errors-as-data (FR-100)."""

    files: list[LogFile] = field(default_factory=list)
    errors: list[ErrorEntry] = field(default_factory=list)


def _validate_max_file_mb(max_file_mb: int) -> int:
    """max_file_mb must be a strictly positive integer (bools rejected)."""
    if type(max_file_mb) is not int or max_file_mb <= 0:
        raise ValueError(
            f"max_file_mb must be a positive integer, got {max_file_mb!r}")
    return max_file_mb


def _describe(exc: BaseException) -> str:
    """Format any exception for an error entry, never raising itself.

    Not every exception carries ``strerror`` (e.g. ValueError); the
    formatter therefore falls back to ``str(exc)`` and survives even
    unprintable exceptions.
    """
    try:
        strerror = getattr(exc, "strerror", None)
        detail = strerror or str(exc)
    except Exception:  # pragma: no cover - defensive only
        detail = "<unprintable exception>"
    return f"{exc.__class__.__name__}: {detail}"


def discover_inputs(
    paths, *, max_file_mb: int = DEFAULT_MAX_FILE_MB
) -> DiscoverResult:
    """Turn user-supplied paths into an ordered, de-duplicated file list.

    Behaviour (FR-002, FR-004, FR-100, FR-101, FR-102):
    - explicit file paths keep their supplied order and bypass the
      extension/hidden-name filters (deliberately named by the user);
    - directory paths are traversed in deterministic (sorted) order;
    - paths are de-duplicated by exact string identity, first occurrence
      wins;
    - every problem becomes ``ErrorEntry(kind="input")`` data; processing
      continues with the remaining inputs where possible.

    Deterministic and side-effect free apart from filesystem metadata
    lookups and the read-only openability probe.
    """
    limit_bytes = _validate_max_file_mb(max_file_mb) * 1024 * 1024
    # Top-level argument normalization (final review fix 2): a bare bytes or
    # bytearray argument is ONE invalid argument (never exploded into integer
    # "paths"), a single string is a one-element input, non-iterable objects
    # (e.g. None) become error data instead of raising TypeError.
    captured_error: tuple[str, str] | None = None
    if isinstance(paths, str):
        items: list[object] | None = [paths]
    elif isinstance(paths, (bytes, bytearray)):
        items = None
        captured_error = ("unsupported path type: bytes path",
                          _safe_repr(paths))
    else:
        try:
            items = list(paths)
        except TypeError as exc:
            items = None
            captured_error = (f"unsupported path type: {_describe(exc)}",
                              _safe_repr(paths))

    seen: set[str] = set()
    files: list[LogFile] = []
    errors: list[ErrorEntry] = []

    def record_error(source: str, reason: str) -> None:
        errors.append(ErrorEntry(source_file=source, line_number=None,
                                 reason=reason, kind="input"))

    if captured_error is not None:
        record_error(captured_error[1], captured_error[0])
        items = []

    def accept(candidate: Path) -> None:
        key = str(candidate)
        if key in seen:
            return  # exact-string dedup: first occurrence wins (FR-004)
        seen.add(key)
        try:
            # os.lstat distinguishes genuine missing paths (FileNotFoundError)
            # from inaccessible paths (other OSError); Path.exists() would
            # silently collapse both into False (Phase 4.5 review fix).
            target_stat = os.lstat(candidate)
        except FileNotFoundError:
            record_error(key, "path does not exist")
            return
        except (OSError, ValueError) as exc:
            # ValueError covers embedded-null paths (no strerror attribute).
            record_error(key, f"cannot access path: {_describe(exc)}")
            return
        is_link = stat_module.S_ISLNK(target_stat.st_mode)
        if is_link:
            try:
                # Symlinked files are accepted through their target metadata;
                # the recorded path stays exactly as supplied.
                target_stat = os.stat(candidate)
            except OSError as exc:
                record_error(
                    key, f"broken symbolic link: {_describe(exc)}")
                return
        if stat_module.S_ISDIR(target_stat.st_mode):
            if is_link:
                # Cycle guard: symlinked directories are never followed,
                # not even when supplied explicitly (review correction 2).
                record_error(
                    key, "symbolic link to directory is not followed")
                return
            expand(candidate)
            return
        if not stat_module.S_ISREG(target_stat.st_mode):
            record_error(key, "not a regular file")
            return
        if target_stat.st_size > limit_bytes:
            record_error(
                key,
                f"file exceeds max_file_mb cap of {max_file_mb} MiB "
                f"(size {target_stat.st_size} bytes)")
            return
        try:
            with open(candidate, "rb"):  # openability probe; no bytes read
                pass
        except (OSError, ValueError) as exc:
            record_error(key, f"cannot open file: {_describe(exc)}")
            return
        files.append(LogFile(path=candidate, size_bytes=target_stat.st_size))

    def expand(directory: Path) -> None:
        try:
            entries = sorted(directory.iterdir(), key=lambda entry: str(entry))
        except OSError as exc:
            record_error(
                str(directory),
                f"cannot list directory: {_describe(exc)}")
            return
        for entry in entries:
            if entry.name.startswith("."):
                continue  # hidden file or hidden directory (FR-002)
            try:
                entry_stat = os.lstat(entry)
            except (OSError, ValueError) as exc:
                record_error(
                    str(entry), f"cannot inspect entry: {_describe(exc)}")
                continue
            if stat_module.S_ISLNK(entry_stat.st_mode):
                try:
                    followed = os.stat(entry)
                except OSError as exc:
                    record_error(
                        str(entry),
                        f"broken symbolic link: {_describe(exc)}")
                    continue
                if stat_module.S_ISDIR(followed.st_mode):
                    # Cycle guard: symlinked directories are silently
                    # skipped; only ordinary directories are expanded.
                    continue
                entry_stat = followed
            if stat_module.S_ISDIR(entry_stat.st_mode):
                expand(entry)
                continue
            if not stat_module.S_ISREG(entry_stat.st_mode):
                continue
            if entry.suffix.lower() not in LOG_EXTENSIONS:
                continue
            accept(entry)

    for item in items:
        # Strict argument validation: only strings and os.PathLike objects
        # whose __fspath__ yields a string are accepted; bytes, integers and
        # malformed path-likes become error data, never silent successes.
        if isinstance(item, bytes) or isinstance(item, bytearray):
            record_error(
                _safe_repr(item), "unsupported path type: bytes path")
            continue
        try:
            candidate = Path(os.fspath(item))
        except (TypeError, ValueError) as exc:
            record_error(
                _safe_repr(item), f"unsupported path type: {_describe(exc)}")
            continue
        accept(candidate)

    return DiscoverResult(files=files, errors=errors)


def _safe_repr(value: object) -> str:
    """Best-effort repr for error entries; never raises."""
    try:
        return repr(value)
    except Exception:  # pragma: no cover - defensive only
        return "<unrepresentable>"
