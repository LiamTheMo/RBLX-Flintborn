"""Offline checks of the UI sprite uploader: no credentials or network calls."""
import importlib
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
uploader = importlib.import_module("roblox_upload_ui_assets")


class InspectTests(unittest.TestCase):
    def run_inspect(self, value, key="test-key"):
        with patch.dict(os.environ, {"ROBLOX_API_KEY": key}), \
                patch.object(uploader.urllib.request, "urlopen",
                             side_effect=AssertionError("network call")) as urlopen:
            with self.assertRaises(ValueError):
                uploader.main(["--inspect", value])
        urlopen.assert_not_called()

    def test_inspect_refuses_a_non_numeric_id_before_any_request(self):
        for value in ("1/../../../v1/operations", "123?readMask=*", "12 3", "-5", "abc"):
            with self.subTest(value=value):
                self.run_inspect(value)

    def test_inspect_requires_a_key(self):
        self.run_inspect("123", key="")


if __name__ == "__main__":
    unittest.main()
