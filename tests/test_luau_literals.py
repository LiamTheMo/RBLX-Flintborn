"""Offline checks of the Luau literals the place tools embed in their Luau tasks."""
import importlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
TOOLS = [importlib.import_module(name) for name in ("roblox_lobby_map", "roblox_character")]

VALUE = {"name": "Caf\u00e9 \U0001F525", "tab\tline\n": ["\u2014", "a\u0001b", 1, 2.5, True]}


def utf8_hex(text):
    return text.encode("utf-8").hex().upper()


@unittest.skipIf(shutil.which("luau") is None, "luau CLI not on PATH")
class LuaValueTests(unittest.TestCase):
    def run_luau(self, literal):
        script = (
            "local value = " + literal + "\n"
            "local function hex(s) return (s:gsub('.', function(c) return string.format('%02X', c:byte()) end)) end\n"
            "local list = value[\"tab\\tline\\n\"]\n"
            "print(hex(value.name), hex(list[1]), hex(list[2]), list[3], list[4], list[5])\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "literal.luau"
            path.write_text(script, encoding="utf-8")
            return subprocess.run([shutil.which("luau"), str(path)], capture_output=True, text=True)

    def test_non_ascii_text_survives_luau(self):
        expected = "\t".join([utf8_hex(VALUE["name"]), utf8_hex("\u2014"), utf8_hex("a\u0001b"), "1", "2.5", "true"])
        for tool in TOOLS:
            with self.subTest(tool=tool.__name__):
                result = self.run_luau(tool.lua_value(VALUE))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(result.stdout.strip(), expected)


if __name__ == "__main__":
    unittest.main()
