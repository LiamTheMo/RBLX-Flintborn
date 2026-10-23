"""Offline release checks: no Roblox credentials, network calls or live mutations."""
import importlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
cloud = importlib.import_module("roblox_live_publish")


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
        self.assertIn("Managed Studio root is missing", script)
        self.assertIn("Script class mismatch", script)
        self.assertNotIn("Destroy()", script)
        self.assertNotIn("versionType=Published", script)

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


if __name__ == "__main__":
    unittest.main()
