"""Offline checks of the headless Luau spec runner (tests/luau/run.py)."""
import contextlib
import importlib.util
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

RUN_PY = Path(__file__).resolve().parent / "luau" / "run.py"
_spec = importlib.util.spec_from_file_location("luau_spec_runner", RUN_PY)
runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runner)


class JsonModuleTests(unittest.TestCase):
    """A JSON file under src/ is a module returning its table, as Rojo builds it."""

    VALUE = {
        "accent": "Caf\u00e9",
        "emoji": "\U0001F525",
        "control": "a\u0001b",
        "nested": {"\u00fcber": ["\u2014", 1, 2.5, True, None]},
    }

    def module_source(self, value):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "Strings.json").write_text(
                json.dumps(value, ensure_ascii=False), encoding="utf-8")
            with patch.object(runner, "MOUNTS", {("ReplicatedStorage", "Shared"): Path(tmp)}):
                entries = runner.module_entries()
        self.assertEqual([path for path, _ in entries], [["ReplicatedStorage", "Shared", "Strings"]])
        return entries[0][1]

    @unittest.skipIf(shutil.which("luau") is None, "luau CLI not on PATH")
    def test_non_ascii_strings_are_escaped_and_survive_luau(self):
        source = self.module_source(self.VALUE)
        self.assertTrue(source.isascii(), source)
        script = (
            "local value = (function()\n" + source + "\nend)()\n"
            "local function hex(s) return (s:gsub('.', function(c) return string.format('%02X', c:byte()) end)) end\n"
            "print(hex(value.accent), hex(value.emoji), hex(value.control))\n"
            "for k, v in value.nested do print(hex(k), hex(v[1]), v[2], v[3], v[4], v[5]) end\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "module.luau"
            path.write_text(script, encoding="utf-8")
            result = subprocess.run([shutil.which("luau"), str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        expected_first = "\t".join(s.encode("utf-8").hex().upper() for s in
                                   (self.VALUE["accent"], self.VALUE["emoji"], self.VALUE["control"]))
        lines = result.stdout.splitlines()
        self.assertEqual(lines[0], expected_first)
        self.assertEqual(lines[1], "\t".join([
            "\u00fcber".encode("utf-8").hex().upper(), "\u2014".encode("utf-8").hex().upper(),
            "1", "2.5", "true", "nil"]))


@unittest.skipIf(shutil.which("luau") is None, "luau CLI not on PATH")
class SummaryTests(unittest.TestCase):
    def test_require_cycle_fails_the_run_without_failing_a_spec(self):
        with tempfile.TemporaryDirectory() as tmp:
            here = Path(tmp)
            shutil.copy(runner.HERE / "prelude.luau", here / "prelude.luau")
            (here / "one.spec.luau").write_text("-- no cases\n", encoding="utf-8")
            out = io.StringIO()
            with patch.object(runner, "HERE", here), \
                    patch.object(runner, "require_cycles", return_value=["A -> B -> A"]), \
                    contextlib.redirect_stdout(out):
                code = runner.main()
        self.assertEqual(code, 1)
        self.assertIn("REQUIRE CYCLE: A -> B -> A", out.getvalue())
        self.assertIn("1/1 spec files passed", out.getvalue())


if __name__ == "__main__":
    unittest.main()
