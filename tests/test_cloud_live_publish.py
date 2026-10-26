"""Offline release checks: no Roblox credentials, network calls or live mutations."""
import importlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
cloud = importlib.import_module("roblox_live_publish")
sync = importlib.import_module("roblox_cloud_sync")


class CloudPublishSafetyTests(unittest.TestCase):
    def test_only_script_roots(self):
        with patch.object(cloud, "discover", return_value={
            ("Workspace", "Danger"): (Path(__file__), "ModuleScript")
        }):
            with self.assertRaisesRegex(ValueError, "outside approved"):
                cloud.spec_list()

    def test_safe_task_and_live_publish(self):
        source = "-- plain script\\nreturn {success=true}"
        script = cloud.make_script([
            (("ReplicatedStorage", "Shared", "Sample"), "ModuleScript", source)
        ])
        self.assertIn("SavePlaceAsync({ SaveWithoutPublish = false })", script)
        self.assertIn(cloud.SAVE_PLACE, script)
        self.assertIn("Managed Studio root is missing", script)
        self.assertIn("Script class mismatch", script)
        # The only removals: the save's (the engine's runtime copies of its default
        # player scripts) and scripts retired from Git, at their exact paths.
        self.assertEqual(script.replace(cloud.SAVE_PLACE, "").count("Destroy()"), 1)
        self.assertIn('if obj and obj:IsA("LuaSourceContainer") then\n    obj:Destroy()', script)
        self.assertIn('"AssetProbeController"', script)
        self.assertEqual(cloud.SAVE_PLACE.count("Destroy()"), 2)
        self.assertIn('child.Name == "PlayerModule" and child:IsA("ModuleScript")', cloud.SAVE_PLACE)
        self.assertIn('child.Name == "RbxCharacterSounds" and child:IsA("LocalScript")', cloud.SAVE_PLACE)
        self.assertNotIn("versionType=Published", script)

    def test_retired_paths_stay_inside_managed_roots(self):
        with patch.object(cloud, "RETIRED", (("Workspace", "Map", "Danger"),)):
            with self.assertRaisesRegex(ValueError, "outside the managed"):
                cloud.retired_paths([])
        with patch.object(cloud, "RETIRED", (("ReplicatedStorage", "Shared"),)):
            with self.assertRaisesRegex(ValueError, "outside the managed"):
                cloud.retired_paths([])  # a whole root, not one script
        live = ("ReplicatedStorage", "Shared", "Core", "Loader")
        with patch.object(cloud, "RETIRED", (live,)):
            with self.assertRaisesRegex(ValueError, "still published"):
                cloud.retired_paths([(live, "ModuleScript", "return {}")])
        self.assertNotIn("Destroy", cloud.make_script([(live, "ModuleScript", "return {}")], verify=True))

    def test_every_cloud_save_strips_engine_copies(self):
        root = Path(__file__).resolve().parents[1] / "scripts"
        for name in ("roblox_live_publish.py", "roblox_character.py", "roblox_lobby_map.py"):
            text = (root / name).read_text(encoding="utf-8")
            outside = text.split("SAVE_PLACE = r'''", 1)
            body = outside[0] + (outside[1].split("'''", 1)[1] if len(outside) > 1 else "")
            self.assertNotIn("SavePlaceAsync(", body, name + " saves without SAVE_PLACE")

    def test_post_publish_source_verification(self):
        script = cloud.make_script([
            (("ServerScriptService", "Server", "Sample"), "ModuleScript", "return 3")
        ], verify=True)
        self.assertIn("LIVE PUBLISH verification failed", script)
        self.assertNotIn("SavePlaceAsync", script)

    def test_reject_oversized_release(self):
        with self.assertRaisesRegex(ValueError, "too large"):
            cloud.make_script([
                (("ReplicatedStorage", "Shared", "Sample"), "ModuleScript", "x"*3001000)
            ])


_TOKEN = re.compile(r'''\s+|--[^\n]*|(?P<str>"(?:[^"\\\n]|\\.)*")|(?P<num>-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)'''
                    r'''|(?P<word>[A-Za-z_]\w*)|(?P<sym>[{}\[\]=,])''')
_SIMPLE_ESCAPES = {'"': '"', "\\": "\\", "n": "\n", "r": "\r", "t": "\t"}


def _luau_unescape(body):
    out, i = [], 0
    while i < len(body):
        ch = body[i]
        if ch != "\\":
            out.append(ch)
            i += 1
            continue
        nxt = body[i + 1]
        if nxt in _SIMPLE_ESCAPES:
            out.append(_SIMPLE_ESCAPES[nxt])
            i += 2
        elif nxt == "x":
            out.append(chr(int(body[i + 2:i + 4], 16)))
            i += 4
        elif nxt == "u":
            end = body.index("}", i)
            assert body[i + 2] == "{", body[i:end + 1]
            out.append(chr(int(body[i + 3:end], 16)))
            i = end + 1
        else:
            raise AssertionError("escape the converter must not emit: \\" + nxt)
    return "".join(out)


def eval_luau_module(source):
    """Evaluate the `return <literal>` subset json_to_luau emits. Tables with
    only positional items become lists, keyed tables become dicts."""
    tokens = []
    for match in _TOKEN.finditer(source):
        kind = match.lastgroup
        if kind:
            tokens.append((kind, match.group(kind)))
    assert "".join(m.group(0) for m in _TOKEN.finditer(source)) == source, "unlexable output"
    assert tokens[0] == ("word", "return"), tokens[:1]
    pos = 1

    def value():
        nonlocal pos
        kind, text = tokens[pos]
        pos += 1
        if kind == "str":
            return _luau_unescape(text[1:-1])
        if kind == "num":
            return float(text) if re.search(r"[.eE]", text) else int(text)
        if kind == "word":
            return {"true": True, "false": False, "nil": None}[text]
        assert text == "{", text
        items, keyed = [], {}
        while tokens[pos][1] != "}":
            if tokens[pos][1] == "[":
                key = value_at_key()
                keyed[key] = value()
            else:
                items.append(value())
            if tokens[pos][1] == ",":
                pos += 1
        pos += 1
        assert not (items and keyed), "mixed table"
        return keyed if keyed else items

    def value_at_key():
        nonlocal pos
        assert tokens[pos][1] == "["
        pos += 1
        key = value()
        assert isinstance(key, str) and tokens[pos][1] == "]" and tokens[pos + 1][1] == "="
        pos += 2
        return key

    result = value()
    assert pos == len(tokens), "trailing tokens"
    return result


def _normalise(value):
    """Lua cannot tell {} from [], so compare both as an empty list."""
    if isinstance(value, dict):
        return {k: _normalise(v) for k, v in value.items()} if value else []
    if isinstance(value, list):
        return [_normalise(v) for v in value]
    return value


class JsonModuleTests(unittest.TestCase):
    def round_trip(self, text):
        luau = sync.json_to_luau(text)
        self.assertTrue(luau.isascii(), luau)
        self.assertEqual(_normalise(eval_luau_module(luau)), _normalise(json.loads(text)))
        return luau

    def test_expected_literals(self):
        self.assertEqual(sync.json_to_luau('{"a": [1, null, true], "b": {}, "c": [], "d": -2.5e3}'),
                         'return {\n\t["a"] = {\n\t\t1,\n\t\tnil,\n\t\ttrue,\n\t},\n'
                         '\t["b"] = {},\n\t["c"] = {},\n\t["d"] = -2.5e3,\n}\n')
        self.assertEqual(sync.json_to_luau('false'), "return false\n")
        self.assertEqual(sync.json_to_luau('null'), "return nil\n")

    def test_strings_are_luau_safe(self):
        luau = self.round_trip(json.dumps({
            'quo"te': 'say "hi"', "back\\slash": "C:\\path\\", "ctrl": "a\nb\tc\rd\u0000e\u001f\u007f",
            "unicode": "caf\u00e9 \u2028 \U0001F600 \u4e2d", "": "",
        }))
        self.assertIn(r'["quo\"te"] = "say \"hi\""', luau)
        self.assertIn(r'["back\\slash"] = "C:\\path\\"', luau)
        self.assertIn(r'"a\nb\tc\rd\x00e\x1F\x7F"', luau)
        self.assertIn(r'"caf\u{E9} \u{2028} \u{1F600} \u{4E2D}"', luau)
        self.assertNotRegex(luau, r"\\u[0-9A-Fa-f]{4}")  # JSON-style escapes are not Luau

    def test_nested_and_numbers_round_trip(self):
        self.round_trip('{"x": [[1, 2], [3, [4, {"y": [null, false]}]]], "big": 12345678901234567890,'
                        ' "neg": -0, "exp": 1E+5, "frac": 0.125, "dup": 1, "dup": 2}')
        self.assertIn('["exp"] = 1E+5', sync.json_to_luau('{"exp": 1E+5}'))

    def test_deep_and_large_nesting(self):
        depth = 600
        text = "[" * depth + '{"k": "v"}' + "]" * depth
        luau = self.round_trip(text)
        self.assertLess(len(luau), 100000)  # indentation is capped, not quadratic
        self.round_trip(json.dumps({"rows": [{"id": i, "tags": ["a", str(i)]} for i in range(5000)]}))

    def test_invalid_json_is_rejected(self):
        for text in ('{"a": NaN}', '[Infinity]', '{"a": 1', '["\\ud800"]'):
            with self.assertRaises(ValueError, msg=text):
                sync.json_to_luau(text)

    def make_project(self, files):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        (root / "default.project.json").write_text(json.dumps({"tree": {
            "$className": "DataModel",
            "ReplicatedStorage": {"$className": "ReplicatedStorage", "Shared": {"$path": "src/shared"}},
        }}), encoding="utf-8")
        for relative, text in files.items():
            path = root / "src" / "shared" / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return root

    def test_json_files_are_discovered_like_rojo(self):
        root = self.make_project({
            "UI/HudLayout.json": '{"a": 1}', "UI/Widget.luau": "return {}",
            "Data/init.json": "[1]", "Data/Names.server.json": "{}",
            "Nested.project.json": "{}", "UI/Widget.meta.json": "{}", "Prop.model.json": "{}",
        })
        with patch.object(sync, "ROOT", root):
            entries = sync.discover()
        shared = ("ReplicatedStorage", "Shared")
        found = {path: (file.relative_to(root).as_posix(), cls) for path, (file, cls) in entries.items()}
        self.assertEqual(found, {
            shared + ("UI", "HudLayout"): ("src/shared/UI/HudLayout.json", "ModuleScript"),
            shared + ("UI", "Widget"): ("src/shared/UI/Widget.luau", "ModuleScript"),
            # Rojo has no init rule for JSON: init.json is a module named "init".
            shared + ("Data", "init"): ("src/shared/Data/init.json", "ModuleScript"),
            shared + ("Data", "Names.server"): ("src/shared/Data/Names.server.json", "ModuleScript"),
        })
        self.assertEqual(sync.local_source(root / "src/shared/UI/HudLayout.json"),
                         '-- Generated from HudLayout.json by the release scripts. Edit the JSON in Git.\n'
                         'return {\n\t["a"] = 1,\n}\n')

    def test_json_module_conflicting_with_script_is_rejected(self):
        root = self.make_project({"UI/Hud.json": "{}", "UI/Hud.luau": "return {}"})
        with patch.object(sync, "ROOT", root), self.assertRaisesRegex(ValueError, "Ambiguous"):
            sync.discover()

    def test_repo_json_modules_publish_and_verify_as_luau(self):
        entries = sync.discover()
        modules = {path[-1]: file for path, (file, cls) in entries.items()
                   if file.suffix == ".json" and cls == "ModuleScript"}
        for name in ("HudLayout", "UiAssetIds", "UiSprites"):
            self.assertIn(("ReplicatedStorage", "Shared", "UI", name),
                          {path for path in entries if path[-1] == name})
            self.assertIn(name, modules)
        specs = {path: source for path, _, source in cloud.spec_list()}
        for name, file in modules.items():
            source = specs[("ReplicatedStorage", "Shared", "UI", name)]
            self.assertEqual(source, sync.json_to_luau(file.read_text(encoding="utf-8"), origin=file.name))
            luau_value = eval_luau_module(source)
            self.assertEqual(_normalise(luau_value), _normalise(json.loads(file.read_text(encoding="utf-8"))))
            for verify in (False, True):
                script = cloud.make_script([(("ReplicatedStorage", "Shared", "UI", name), "ModuleScript", source)],
                                           verify=verify)
                self.assertIn("source=" + cloud.lua_string(source), script)

    def test_cloud_sync_preflight_compares_converted_source(self):
        root = self.make_project({"UI/HudLayout.json": '{"a": [1]}'})
        with patch.object(sync, "ROOT", root):
            entries = sync.discover()
        expected = sync.local_source(root / "src/shared/UI/HudLayout.json")

        class FakeCloud:
            def children(self, parent):
                names = {"root": "ReplicatedStorage", "id-rs": "Shared", "id-sh": "UI", "id-ui": "HudLayout"}
                ids = {"root": "id-rs", "id-rs": "id-sh", "id-sh": "id-ui", "id-ui": "id-hud"}
                return [{"engineInstance": {"Name": names[parent], "Id": ids[parent]}}]

            def instance(self, instance_id):
                return {"Details": {"ModuleScript": {"Source": expected}}}

        selected = sync.preflight(FakeCloud(), entries)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0][3], selected[0][4])  # unchanged: no write needed


# A stand-in for the place's instance tree, matching what Rojo creates: the
# managed roots sit under engine containers such as StarterPlayerScripts.
MOCK_PLACE = r'''
local function node(name, class, children)
  local n = { Name = name, ClassName = class, _children = {} }
  for _, c in ipairs(children or {}) do n._children[c.Name] = c end
  function n:FindFirstChild(x) return self._children[x] end
  function n:IsA(c)
    if c == "LuaSourceContainer" then
      return self.ClassName == "Script" or self.ClassName == "LocalScript" or self.ClassName == "ModuleScript"
    end
    return self.ClassName == c
  end
  return n
end
local tree = {
  ServerScriptService = node("ServerScriptService", "ServerScriptService", { node("Server", "Script") }),
  ReplicatedStorage = node("ReplicatedStorage", "ReplicatedStorage", { %SHARED% }),
  StarterPlayer = node("StarterPlayer", "StarterPlayer", {
    node("StarterPlayerScripts", "%SPS_CLASS%", { node("Client", "LocalScript") }) }),
}
game = { GetService = function(_, s) return tree[s] end }
'''


@unittest.skipUnless(shutil.which("luau"), "luau CLI not installed")
class PreflightExecutionTests(unittest.TestCase):
    """Runs the real preflight Luau against a mock place in the luau CLI."""

    def run_preflight(self, shared, sps_class="StarterPlayerScripts"):
        specs = cloud.spec_list()
        script = cloud.make_script(specs)
        preflight = script[: script.index(cloud.APPLY)]
        place = MOCK_PLACE.replace("%SHARED%", shared).replace("%SPS_CLASS%", sps_class)
        source = place + preflight + '\nprint("PREFLIGHT_OK")\n'
        with tempfile.NamedTemporaryFile("w", suffix=".luau", delete=False) as handle:
            handle.write(source)
        result = subprocess.run(["luau", handle.name], capture_output=True, text=True)
        Path(handle.name).unlink()
        return result.stdout + result.stderr

    def test_engine_containers_on_root_paths_are_allowed(self):
        # Regression: StarterPlayerScripts used to trip the code-only check.
        self.assertIn("PREFLIGHT_OK", self.run_preflight('node("Shared", "Folder")'))

    def test_non_code_ancestor_inside_managed_tree_is_rejected(self):
        output = self.run_preflight('node("Shared", "Folder", { node("Core", "Part") })')
        self.assertIn("Non-code ancestor collision at ReplicatedStorage/Shared/Core", output)
        self.assertNotIn("PREFLIGHT_OK", output)

    def test_impostor_engine_container_is_rejected(self):
        # The exemption is by name AND class: a Part named StarterPlayerScripts
        # must not let scripts publish under it.
        output = self.run_preflight('node("Shared", "Folder")', sps_class="Part")
        self.assertIn("Engine container class mismatch at StarterPlayer/StarterPlayerScripts", output)
        self.assertNotIn("PREFLIGHT_OK", output)

    def test_converted_json_modules_run_in_luau(self):
        sample = sync.json_to_luau(json.dumps({
            "s": 'q"b\\n\né\U0001F600', "arr": [1, None, 3], "deep": [[{"x": -2.5e3}]], "empty": {},
        }), origin="Sample.json")
        checks = ('assert(m.s == "q\\"b\\\\n\\n\\u{E9}\\u{1F600}") assert(m.arr[1] == 1 and m.arr[2] == nil '
                  'and m.arr[3] == 3) assert(m.deep[1][1].x == -2500) assert(next(m.empty) == nil)')
        chunks = ["local m = (function()\n" + sample + "end)()\n" + checks]
        for file in sorted((Path(__file__).resolve().parents[1] / "src").rglob("*.json")):
            if sync.is_json_module(file):
                chunks.append("assert(type((function()\n" + sync.local_source(file) + "end)()) == 'table')")
        with tempfile.NamedTemporaryFile("w", suffix=".luau", delete=False, encoding="utf-8") as handle:
            handle.write("\n".join(chunks) + '\nprint("JSON_MODULES_OK")\n')
        result = subprocess.run(["luau", handle.name], capture_output=True, text=True)
        Path(handle.name).unlink()
        self.assertIn("JSON_MODULES_OK", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
