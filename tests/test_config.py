"""Unit tests for LogSentinel configuration (Phase 4.2; Phase 3 matrix TC-C01..TC-C04)."""

import json
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

from logsentinel.config import CONFIG_KEYS, DEFAULTS, AppConfig, load_config
from logsentinel.exceptions import ConfigError


def write_config(tmp, name, payload):
    path = Path(tmp) / name
    path.write_text(payload, encoding="utf-8")
    return str(path)


class TestDefaults(unittest.TestCase):
    """TC-C01: built-in defaults are the base layer (FR-140)."""

    def test_defaults_values(self):
        self.assertEqual(DEFAULTS, {
            "ssh_threshold": 8,
            "ssh_window_seconds": 300,
            "portscan_threshold": 10,
            "http_4xx_threshold": 8,
            "strict": False,
            "max_line_length": 8192,
            "max_file_mb": 512,
        })

    def test_load_config_without_inputs_returns_defaults(self):
        config = load_config({}, None)
        for key in CONFIG_KEYS:
            self.assertEqual(getattr(config, key), DEFAULTS[key])

    def test_appconfig_field_defaults_match_defaults(self):
        config = AppConfig()
        for key in CONFIG_KEYS:
            self.assertEqual(getattr(config, key), DEFAULTS[key])


class TestJsonConfiguration(unittest.TestCase):
    """TC-C02/TC-C04: JSON file layer, validation, and error cases."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_valid_json_overrides_defaults(self):
        path = write_config(self.tmp, "cfg.json", json.dumps({
            "ssh_threshold": 5,
            "ssh_window_seconds": 120,
            "strict": True,
        }))
        config = load_config({}, path)
        self.assertEqual(config.ssh_threshold, 5)
        self.assertEqual(config.ssh_window_seconds, 120)
        self.assertIs(config.strict, True)
        self.assertEqual(config.portscan_threshold, 10)  # untouched default

    def test_empty_json_configuration(self):
        path = write_config(self.tmp, "empty.json", "{}")
        config = load_config({}, path)
        for key in CONFIG_KEYS:
            self.assertEqual(getattr(config, key), DEFAULTS[key])

    def test_all_keys_via_json(self):
        payload = {key: DEFAULTS[key] for key in CONFIG_KEYS}
        payload["max_file_mb"] = 1024
        path = write_config(self.tmp, "all.json", json.dumps(payload))
        config = load_config({}, path)
        self.assertEqual(config.max_file_mb, 1024)

    def test_unknown_json_key_rejected(self):
        path = write_config(self.tmp, "bad.json",
                            json.dumps({"ssh_threshold": 8, "nope": 1}))
        with self.assertRaises(ConfigError) as ctx:
            load_config({}, path)
        self.assertIn("unknown configuration key", str(ctx.exception))
        self.assertIn("nope", str(ctx.exception))

    def test_invalid_json_rejected(self):
        path = write_config(self.tmp, "broken.json", "{not json")
        with self.assertRaises(ConfigError) as ctx:
            load_config({}, path)
        self.assertIn("invalid JSON", str(ctx.exception))

    def test_non_object_roots_rejected(self):
        for payload in ("[1, 2]", '"text"', "42", "null", "true"):
            with self.subTest(payload=payload):
                path = write_config(self.tmp, "root.json", payload)
                with self.assertRaises(ConfigError) as ctx:
                    load_config({}, path)
                self.assertIn("JSON object", str(ctx.exception))

    def test_invalid_utf8_config_file_rejected(self):
        # Phase 4.2 review correction: undecodable bytes must raise
        # ConfigError, not leak UnicodeDecodeError.
        path = Path(self.tmp) / "latin.json"
        path.write_bytes(bytes([0x7B, 0xFF, 0xFE]) + b" invalid utf-8 }")
        with self.assertRaises(ConfigError) as ctx:
            load_config({}, str(path))
        self.assertIn("not valid UTF-8", str(ctx.exception))

    def test_missing_config_file_rejected(self):
        with self.assertRaises(ConfigError) as ctx:
            load_config({}, str(Path(self.tmp) / "missing.json"))
        self.assertIn("cannot read configuration file", str(ctx.exception))

    def test_directory_as_config_file_rejected(self):
        # Unreadable-as-file case that works on every platform (FR-060).
        with self.assertRaises(ConfigError) as ctx:
            load_config({}, self.tmp)
        self.assertIn("cannot read configuration file", str(ctx.exception))

    def test_zero_and_negative_integer_settings_rejected(self):
        for key in ("ssh_threshold", "ssh_window_seconds", "portscan_threshold",
                    "http_4xx_threshold", "max_line_length", "max_file_mb"):
            for value in (0, -1):
                with self.subTest(key=key, value=value):
                    path = write_config(self.tmp, "neg.json",
                                        json.dumps({key: value}))
                    with self.assertRaises(ConfigError):
                        load_config({}, path)

    def test_boolean_for_integer_setting_rejected(self):
        for key in ("ssh_threshold", "ssh_window_seconds", "portscan_threshold",
                    "http_4xx_threshold", "max_line_length", "max_file_mb"):
            with self.subTest(key=key):
                path = write_config(self.tmp, "bool.json",
                                    json.dumps({key: True}))
                with self.assertRaises(ConfigError) as ctx:
                    load_config({}, path)
                self.assertIn("positive integer", str(ctx.exception))

    def test_float_and_string_integer_settings_rejected(self):
        for bad in (8.0, "8", None, [8]):
            with self.subTest(bad=bad):
                path = write_config(self.tmp, "type.json",
                                    json.dumps({"ssh_threshold": bad}))
                with self.assertRaises(ConfigError):
                    load_config({}, path)

    def test_invalid_strict_values_rejected(self):
        for bad in ("yes", 1, 0, None, [], 1.0):
            with self.subTest(bad=bad):
                path = write_config(self.tmp, "strict.json",
                                    json.dumps({"strict": bad}))
                with self.assertRaises(ConfigError) as ctx:
                    load_config({}, path)
                self.assertIn("strict", str(ctx.exception))

    def test_defaults_not_mutated_by_loading(self):
        path = write_config(self.tmp, "cfg.json",
                            json.dumps({"ssh_threshold": 3}))
        load_config({}, path)
        self.assertEqual(DEFAULTS["ssh_threshold"], 8)


class TestCliOverrides(unittest.TestCase):
    """TC-C02: CLI override layer and precedence (AR-008)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_cli_overrides_without_config_file(self):
        config = load_config({"ssh_threshold": 4, "strict": True}, None)
        self.assertEqual(config.ssh_threshold, 4)
        self.assertIs(config.strict, True)
        self.assertEqual(config.ssh_window_seconds, 300)

    def test_full_precedence_cli_over_json_over_defaults(self):
        path = write_config(self.tmp, "cfg.json", json.dumps({
            "ssh_threshold": 5,
            "portscan_threshold": 20,
        }))
        config = load_config({"ssh_threshold": 3}, path)
        self.assertEqual(config.ssh_threshold, 3)        # CLI wins
        self.assertEqual(config.portscan_threshold, 20)  # JSON wins
        self.assertEqual(config.http_4xx_threshold, 8)   # default

    def test_none_overrides_preserve_lower_precedence(self):
        path = write_config(self.tmp, "cfg.json",
                            json.dumps({"ssh_threshold": 5}))
        config = load_config({"ssh_threshold": None, "strict": None}, path)
        self.assertEqual(config.ssh_threshold, 5)
        self.assertIs(config.strict, False)

    def test_unknown_override_key_rejected(self):
        with self.assertRaises(ConfigError) as ctx:
            load_config({"bogus": 1}, None)
        self.assertIn("unknown CLI override", str(ctx.exception))
        self.assertIn("bogus", str(ctx.exception))

    def test_invalid_override_value_rejected(self):
        with self.assertRaises(ConfigError):
            load_config({"ssh_threshold": 0}, None)
        with self.assertRaises(ConfigError):
            load_config({"ssh_threshold": True}, None)
        with self.assertRaises(ConfigError):
            load_config({"strict": "yes"}, None)

    def test_overrides_validated_even_when_json_would_supply_value(self):
        path = write_config(self.tmp, "cfg.json",
                            json.dumps({"ssh_threshold": 5}))
        with self.assertRaises(ConfigError):
            load_config({"ssh_threshold": -2}, path)


class TestAppConfigDataclass(unittest.TestCase):
    """TC-E-style model checks for the frozen slotted AppConfig."""

    def test_frozen(self):
        config = AppConfig()
        with self.assertRaises(FrozenInstanceError):
            config.ssh_threshold = 99

    def test_slotted(self):
        config = AppConfig()
        self.assertFalse(hasattr(config, "__dict__"))

    def test_exactly_seven_settings(self):
        import dataclasses
        self.assertEqual(len(CONFIG_KEYS), 7)
        self.assertEqual(
            {f.name for f in dataclasses.fields(AppConfig)},
            set(CONFIG_KEYS))

    def test_direct_construction_validated(self):
        for kwargs in ({"ssh_threshold": 0}, {"ssh_threshold": True},
                       {"max_file_mb": -5}, {"strict": 1}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ConfigError):
                    AppConfig(**kwargs)


if __name__ == "__main__":
    unittest.main()
