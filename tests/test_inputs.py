"""Unit tests for LogSentinel input discovery (Phase 4.5; matrix TC-I01..TC-I04)."""

import builtins
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from logsentinel.events import ErrorEntry
from logsentinel import inputs as _inputs_module
from logsentinel.inputs import (
    DEFAULT_MAX_FILE_MB,
    LOG_EXTENSIONS,
    DiscoverResult,
    LogFile,
    discover_inputs,
)


class InputsTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def file(self, name, content="synthetic log line", subdir=None):
        directory = self.tmp / subdir if subdir else self.tmp
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / name
        path.write_text(content, encoding="utf-8")
        return path

    def paths_of(self, result):
        return [entry.path for entry in result.files]


class TestExplicitPaths(InputsTestCase):
    """Tests 1-3, 9: explicit files, ordering, deduplication, bypass."""

    def test_single_explicit_file(self):
        target = self.file("only.log")
        result = discover_inputs([str(target)])
        self.assertEqual(self.paths_of(result), [target])
        self.assertEqual(result.files[0].size_bytes, len("synthetic log line"))
        self.assertEqual(result.errors, [])

    def test_multiple_explicit_files_preserve_order(self):
        a = self.file("a.log")
        b = self.file("b.txt")
        c = self.file("c.dat")          # non-log extension, still accepted
        result = discover_inputs([str(c), str(a), str(b)])
        self.assertEqual(self.paths_of(result), [c, a, b])  # supplied order

    def test_duplicate_paths_deduplicated_first_occurrence(self):
        a = self.file("a.log")
        result = discover_inputs([str(a), str(a), str(a)])
        self.assertEqual(self.paths_of(result), [a])
        self.assertEqual(result.errors, [])

    def test_explicit_files_bypass_extension_filter(self):
        weird = self.file("notes.cfg")
        hidden = self.file(".secret.log")
        result = discover_inputs([str(weird), str(hidden)])
        self.assertEqual(self.paths_of(result), [weird, hidden])

    def test_dedup_is_exact_string_identity(self):
        a = self.file("a.log")
        # Same file referenced twice via distinct spellings: both are kept
        # (no case folding, no symlink/inode identity - documented policy).
        upper = discover_inputs([str(a), str(a).upper()])
        self.assertEqual(len(upper.files), 2)


class TestDirectoryDiscovery(InputsTestCase):
    """Tests 4-8: recursion, filtering, hidden entries, determinism."""

    def test_recursive_discovery_with_nested_directories(self):
        deep = self.file("deep.log", subdir="logs/2026/03")
        other = self.file("plain.txt", subdir="logs")
        result = discover_inputs([str(self.tmp / "logs")])
        self.assertEqual(self.paths_of(result), [deep, other])

    def test_extension_filtering(self):
        keep1 = self.file("keep.log")
        keep2 = self.file("keep.txt")
        self.file("skip.dat")
        self.file("skip.md")
        result = discover_inputs([str(self.tmp)])
        self.assertEqual(sorted(self.paths_of(result)), sorted([keep1, keep2]))

    def test_case_insensitive_extensions(self):
        upper = self.file("UPPER.LOG")
        mixed = self.file("mixed.TxT")
        result = discover_inputs([str(self.tmp)])
        self.assertEqual(sorted(self.paths_of(result)), sorted([upper, mixed]))

    def test_hidden_files_and_directories_ignored(self):
        self.file("visible.log")
        self.file(".hidden.log")
        self.file("inside.log", subdir=".hiddendir")
        self.file("buried.log", subdir="ok/.secret")
        result = discover_inputs([str(self.tmp)])
        self.assertEqual(self.paths_of(result), [self.tmp / "visible.log"])

    def test_extensions_constant(self):
        self.assertEqual(LOG_EXTENSIONS, frozenset({".log", ".txt"}))

    def test_deterministic_repeated_discovery(self):
        self.file("z.log", subdir="sub")
        self.file("a.log")
        self.file("m.log", subdir="sub")
        first = discover_inputs([str(self.tmp)])
        second = discover_inputs([str(self.tmp)])
        self.assertEqual(first, second)
        names = [entry.path.name for entry in first.files]
        self.assertEqual(names, ["a.log", "m.log", "z.log"])  # sorted walk


class TestErrorHandling(InputsTestCase):
    """Tests 10-12, 15, 19: errors-as-data, continue-on-failure."""

    def test_missing_path_error_entry(self):
        result = discover_inputs([str(self.tmp / "missing.log")])
        self.assertEqual(result.files, [])
        self.assertEqual(len(result.errors), 1)
        entry = result.errors[0]
        self.assertEqual(entry.kind, "input")
        self.assertEqual(entry.line_number, None)
        self.assertIn("does not exist", entry.reason)

    def test_directory_as_file_argument_expands(self):
        result = discover_inputs([str(self.tmp)])  # directory given directly
        self.assertEqual(result.errors, [])

    def test_invalid_path_types(self):
        result = discover_inputs([123])
        self.assertEqual(result.files, [])
        self.assertTrue(result.errors[0].reason.startswith(
            "unsupported path type"))
        self.assertEqual(result.errors[0].kind, "input")

    def test_null_byte_path_is_error_not_crash(self):
        result = discover_inputs([str(self.tmp) + chr(0) + "bad.log"])
        self.assertEqual(result.files, [])
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].kind, "input")

    def test_oversized_file_rejected(self):
        big = self.tmp / "big.log"
        big.write_bytes(bytes(1024 * 1024 + 1))  # max_file_mb=1 -> too large
        result = discover_inputs([str(big)], max_file_mb=1)
        self.assertEqual(result.files, [])
        self.assertEqual(result.errors[0].kind, "input")
        self.assertIn("exceeds max_file_mb cap", result.errors[0].reason)

    def test_file_exactly_at_size_limit_accepted(self):
        exact = self.tmp / "exact.log"
        exact.write_bytes(bytes(1024 * 1024))    # exactly 1 MiB
        result = discover_inputs([str(exact)], max_file_mb=1)
        self.assertEqual(self.paths_of(result), [exact])
        self.assertEqual(result.errors, [])
        self.assertEqual(result.files[0].size_bytes, 1024 * 1024)

    def test_oversized_file_inside_directory_skipped_others_kept(self):
        self.file("good.log")
        big = self.tmp / "big.txt"
        big.write_bytes(bytes(1024 * 1024 + 1))
        result = discover_inputs([str(self.tmp)], max_file_mb=1)
        self.assertEqual(self.paths_of(result), [self.tmp / "good.log"])
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].kind, "input")

    def test_mixed_valid_and_invalid_inputs_continue(self):
        good = self.file("good.log")
        result = discover_inputs([
            str(self.tmp / "ghost.log"),   # missing
            42,                            # invalid type
            str(good),                     # valid
            str(self.tmp / "ghost.log"),   # duplicate invalid: deduped
        ])
        self.assertEqual(self.paths_of(result), [good])
        self.assertEqual(len(result.errors), 2)  # dedup suppressed the repeat
        self.assertTrue(all(e.kind == "input" for e in result.errors))

    def test_errors_are_data_not_exceptions(self):
        try:
            result = discover_inputs([str(self.tmp / "nope.log")])
        except Exception as exc:  # pragma: no cover - failure path
            self.fail(f"discovery raised instead of returning data: {exc}")
        self.assertIsInstance(result, DiscoverResult)


class TestEmptyDiscovery(InputsTestCase):
    """Test 14: empty results are valid (FR-101)."""

    def test_empty_input_list(self):
        result = discover_inputs([])
        self.assertEqual(result, DiscoverResult())
        self.assertEqual(result.files, [])
        self.assertEqual(result.errors, [])

    def test_empty_directory(self):
        result = discover_inputs([str(self.tmp)])
        self.assertEqual(result.files, [])
        self.assertEqual(result.errors, [])   # no artificial error (FR-101)

    def test_directory_with_only_filtered_files(self):
        self.file("notes.dat")
        result = discover_inputs([str(self.tmp)])
        self.assertEqual(result.files, [])
        self.assertEqual(result.errors, [])


class TestParameterValidation(InputsTestCase):
    """Test 17: max_file_mb validation."""

    def test_default_value(self):
        self.assertEqual(DEFAULT_MAX_FILE_MB, 512)

    def test_invalid_max_file_mb_rejected(self):
        target = self.file("a.log")
        for bad in (True, False, 1.5, 0, -1, "1", None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    discover_inputs([str(target)], max_file_mb=bad)


class TestPurity(InputsTestCase):
    """Tests 16, 18: no content reads; structural purity."""

    def test_no_content_reads_source_scan(self):
        import logsentinel.inputs as module
        with open(module.__file__, encoding="utf-8") as source_file:
            source = source_file.read()
        for banned in ("read_text", "read_bytes", ".read(", "readline",
                       "readlines", "import cli", "import config",
                       "import parsers", "import detectors", "import report"):
            self.assertNotIn(banned, source)

    def test_discovery_does_not_interpret_content(self):
        # A file of undecodable garbage is discovered like any other:
        # discovery never decodes or reads the content.
        garbage = self.tmp / "binary.log"
        garbage.write_bytes(bytes([0xFF, 0x00, 0xFE, 0x00] * 16))
        result = discover_inputs([str(garbage)])
        self.assertEqual(self.paths_of(result), [garbage])

    def test_repeated_discovery_is_deterministic(self):
        a = self.file("a.log")
        b = self.file("b.txt")
        one = discover_inputs([str(b), str(a)])
        two = discover_inputs([str(b), str(a)])
        self.assertEqual(one, two)

    def test_logfile_and_result_are_frozen(self):
        from dataclasses import FrozenInstanceError
        target = self.file("a.log")
        entry = LogFile(path=target, size_bytes=10)
        with self.assertRaises(FrozenInstanceError):
            entry.size_bytes = 99
        result = discover_inputs([str(target)])
        with self.assertRaises(FrozenInstanceError):
            result.files = []      # attribute reassignment is frozen;
        # note: the list *contents* are orchestrator-managed and treated as
        # read-only downstream (Phase 3 contract keeps list types).


if __name__ == "__main__":
    unittest.main()


#: Test-local handle on the module's exception formatter (review test 7).
logsentinel_inputs_describe = _inputs_module._describe


def _symlinks_available():
    try:
        with tempfile.TemporaryDirectory() as tmp:
            os.symlink(tmp, str(Path(tmp) / "probe"))
        return True
    except (OSError, NotImplementedError):
        return False


SYMLINKS_OK = _symlinks_available()
POSIX_LIKE = os.name == "posix"
NOT_ROOT = POSIX_LIKE and getattr(os, "geteuid", lambda: -1)() != 0


class TestSymlinkSafety(InputsTestCase):
    """Review tests 1-2: symlink directory cycles and broken links."""

    @unittest.skipUnless(SYMLINKS_OK, "symlink creation not permitted")
    def test_symlink_directory_to_parent_not_followed(self):
        self.file("visible.log")
        # loop -> tmp (its own parent): unguarded traversal would recurse.
        os.symlink(self.tmp, str(self.tmp / "loop"))
        result = discover_inputs([str(self.tmp)])
        self.assertEqual(self.paths_of(result), [self.tmp / "visible.log"])
        self.assertEqual(result.errors, [])  # silently skipped during walk

    @unittest.skipUnless(SYMLINKS_OK, "symlink creation not permitted")
    def test_explicit_symlink_directory_refused_with_error(self):
        os.symlink(self.tmp, str(self.tmp / "linked"))
        result = discover_inputs([str(self.tmp / "linked")])
        self.assertEqual(result.files, [])
        self.assertEqual(result.errors[0].kind, "input")
        self.assertIn("not followed", result.errors[0].reason)

    @unittest.skipUnless(SYMLINKS_OK, "symlink creation not permitted")
    def test_explicit_symlink_file_followed_to_target(self):
        target = self.file("real.log")
        link = self.tmp / "link.log"
        os.symlink(target, str(link))
        result = discover_inputs([str(link)])
        self.assertEqual(self.paths_of(result), [link])  # path kept as given
        self.assertEqual(result.files[0].size_bytes,
                         target.stat().st_size)
        self.assertEqual(result.errors, [])

    @unittest.skipUnless(SYMLINKS_OK, "symlink creation not permitted")
    def test_broken_symbolic_link_explicit(self):
        broken = self.tmp / "broken.log"
        os.symlink(self.tmp / "ghost.log", str(broken))
        result = discover_inputs([str(broken)])
        self.assertEqual(result.files, [])
        self.assertEqual(result.errors[0].kind, "input")
        self.assertIn("broken symbolic link", result.errors[0].reason)

    @unittest.skipUnless(SYMLINKS_OK, "symlink creation not permitted")
    def test_broken_symbolic_link_inside_directory(self):
        self.file("good.log")
        broken = self.tmp / "broken.log"
        os.symlink(self.tmp / "ghost.log", str(broken))
        result = discover_inputs([str(self.tmp)])
        self.assertEqual(self.paths_of(result), [self.tmp / "good.log"])
        self.assertEqual(len(result.errors), 1)
        self.assertIn("broken symbolic link", result.errors[0].reason)

    @unittest.skipUnless(SYMLINKS_OK, "symlink creation not permitted")
    def test_symlink_to_sibling_directory_not_descended(self):
        # tmp/real/{a.log, b.log}; tmp/other/inside.log; real/uplink -> other
        self.file("a.log", subdir="real")
        self.file("b.log", subdir="real")
        self.file("inside.log", subdir="other")
        os.symlink(self.tmp / "other", str(self.tmp / "real" / "uplink"))
        result = discover_inputs([str(self.tmp / "real")])
        # The symlinked sibling directory must not be descended into:
        # inside.log stays undiscovered, no cycle, no error.
        self.assertEqual(sorted(self.paths_of(result)),
                         sorted([self.tmp / "real" / "a.log",
                                 self.tmp / "real" / "b.log"]))
        self.assertEqual(result.errors, [])

    @unittest.skipUnless(SYMLINKS_OK, "symlink creation not permitted")
    def test_symlink_directory_inside_tree_skipped_siblings_kept(self):
        self.file("a.log", subdir="real")
        self.file("b.log", subdir="real")
        linked = self.tmp / "real" / "uplink"
        os.symlink(self.tmp / "real", str(linked))
        result = discover_inputs([str(self.tmp / "real")])
        self.assertEqual(len(result.files), 2)
        self.assertEqual(result.errors, [])


class TestInaccessiblePaths(InputsTestCase):
    """Review test 3: inaccessible paths where reliably testable (POSIX)."""

    @unittest.skipUnless(POSIX_LIKE and NOT_ROOT,
                         "requires POSIX with drop-able permissions")
    def test_unreadable_file_probe_fails(self):
        target = self.file("locked.log")
        os.chmod(target, 0)
        try:
            result = discover_inputs([str(target)])
        finally:
            os.chmod(target, 0o644)
        self.assertEqual(result.files, [])
        self.assertEqual(result.errors[0].kind, "input")
        self.assertIn("cannot open file", result.errors[0].reason)

    @unittest.skipUnless(POSIX_LIKE and NOT_ROOT,
                         "requires POSIX with drop-able permissions")
    def test_unlistable_directory_reports_and_continues(self):
        keep = self.file("kept.log")
        locked = self.tmp / "locked"
        locked.mkdir()
        os.chmod(locked, 0)
        try:
            result = discover_inputs([str(locked), str(keep)])
        finally:
            os.chmod(locked, 0o755)
        self.assertEqual(self.paths_of(result), [keep])
        self.assertEqual(len(result.errors), 1)
        self.assertIn("cannot list directory", result.errors[0].reason)


class TestPathArgumentValidation(InputsTestCase):
    """Review tests 4-5: byte paths and malformed path-likes."""

    def test_bytes_path_rejected_as_data(self):
        result = discover_inputs([b"some.log"])
        self.assertEqual(result.files, [])
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].kind, "input")
        self.assertIn("unsupported path type", result.errors[0].reason)

    def test_bytearray_path_rejected_as_data(self):
        result = discover_inputs([bytearray(b"some.log")])
        self.assertEqual(result.files, [])
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].kind, "input")

    def test_fspath_object_supported(self):
        target = self.file("via-fspath.log")

        class Named:
            def __fspath__(self):
                return str(target)

        result = discover_inputs([Named()])
        self.assertEqual(len(result.files), 1)
        self.assertEqual(result.errors, [])

    def test_fspath_object_returning_bytes_rejected(self):
        class BadFspath:
            def __fspath__(self):
                return b"bytes-path"

        result = discover_inputs([BadFspath()])
        self.assertEqual(result.files, [])
        self.assertEqual(result.errors[0].kind, "input")
        self.assertIn("unsupported path type", result.errors[0].reason)

    def test_fspath_object_returning_int_rejected(self):
        class WorseFspath:
            def __fspath__(self):
                return 123

        result = discover_inputs([WorseFspath()])
        self.assertEqual(result.files, [])
        self.assertEqual(result.errors[0].kind, "input")


class TestTopLevelArgument(InputsTestCase):
    """Final-review tests: top-level argument normalization."""

    def test_top_level_bytes_argument_single_error(self):
        result = discover_inputs(b"some.log")
        self.assertEqual(result.files, [])
        self.assertEqual(len(result.errors), 1)  # exactly one, not per byte
        self.assertEqual(result.errors[0].kind, "input")
        self.assertIn("unsupported path type", result.errors[0].reason)

    def test_top_level_bytearray_argument_single_error(self):
        result = discover_inputs(bytearray(b"some.log"))
        self.assertEqual(result.files, [])
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].kind, "input")
        self.assertIn("unsupported path type", result.errors[0].reason)

    def test_top_level_none_argument_error_not_exception(self):
        try:
            result = discover_inputs(None)
        except TypeError as exc:  # pragma: no cover - failure path
            self.fail(f"None raised instead of error data: {exc}")
        self.assertEqual(result.files, [])
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].kind, "input")
        self.assertIn("unsupported path type", result.errors[0].reason)

    def test_single_string_still_supported(self):
        target = self.file("single.log")
        result = discover_inputs(str(target))
        self.assertEqual(self.paths_of(result), [target])
        self.assertEqual(result.errors, [])


class TestExceptionFormatting(unittest.TestCase):
    """Review test 7: formatting never assumes strerror, never raises."""

    def test_describe_uses_strerror_when_available(self):
        exc = FileNotFoundError(2, "no such file or directory")
        text = logsentinel_inputs_describe(exc)
        self.assertEqual(text, "FileNotFoundError: no such file or directory")

    def test_describe_without_strerror(self):
        class Opaque(Exception):
            pass

        exc = Opaque("mysterious failure")
        self.assertEqual(logsentinel_inputs_describe(exc),
                         "Opaque: mysterious failure")

    def test_describe_with_unprintable_exception(self):
        class Hostile(Exception):
            def __str__(self):
                raise RuntimeError("cannot print me")

        self.assertTrue(logsentinel_inputs_describe(Hostile()).startswith(
            "Hostile:"))

    def test_null_byte_reason_formatted_without_strerror(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = discover_inputs([tmp + chr(0) + "bad.log"])
        self.assertEqual(result.files, [])
        self.assertEqual(result.errors[0].kind, "input")
        self.assertIn("ValueError:", result.errors[0].reason)


if __name__ == "__main__":
    unittest.main()
