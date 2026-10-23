#!/usr/bin/env python3
"""Publish Git-managed scripts into the EXISTING Roblox place using Luau Execution.

The task never uploads a Rojo-generated place or deletes Studio objects.
Requires Roblox's Save Place API permission and a closed Team Create session.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

from roblox_cloud_sync import discover

ANCHORS = (
    ("ServerScriptService", "Server"),
    ("ReplicatedStorage", "Shared"),
    ("StarterPlayer", "StarterPlayerScripts", "Client"),
)
PREAMBLE = r'''
local specs = %SPECS%
local services = {
  ServerScriptService = game:GetService("ServerScriptService"),
  ReplicatedStorage = game:GetService("ReplicatedStorage"),
  StarterPlayer = game:GetService("StarterPlayer")
}
local anchors = {
  ["ServerScriptService/Server"] = true,
  ["ReplicatedStorage/Shared"] = true,
  ["StarterPlayer/StarterPlayerScripts/Client"] = true
}
local declarations = {}
for _, spec in ipairs(specs) do
  declarations[table.concat(spec.path, "/")] = spec
end
-- Never synthesize missing managed roots: initialize once with Rojo in Studio.
-- The engine containers on the way to a root are verified here, by name AND
-- class, and are then exempt from the code-only ancestor check below.
local engineContainerClasses = {
  ["StarterPlayer/StarterPlayerScripts"] = "StarterPlayerScripts"
}
local engineContainers = {}
for anchor in pairs(anchors) do
  local components = string.split(anchor, "/")
  local obj = services[components[1]]
  for i = 2, #components do
    obj = obj and obj:FindFirstChild(components[i])
    assert(obj, "Managed Studio root is missing: " .. anchor)
    if i < #components then
      local key = table.concat(components, "/", 1, i)
      local expected = engineContainerClasses[key]
      assert(expected, "Undeclared engine container on managed root path: " .. key)
      assert(obj.ClassName == expected, "Engine container class mismatch at " .. key)
      engineContainers[key] = true
    end
  end
end
-- Entire mapping is checked BEFORE any write.
for _, spec in ipairs(specs) do
  local obj = services[spec.path[1]]
  for i = 2, #spec.path do
    local child = obj and obj:FindFirstChild(spec.path[i])
    if child == nil then break end
    local key = table.concat(spec.path, "/", 1, i)
    local declared = declarations[key]
    if declared then
      assert(child.ClassName == declared.kind, "Script class mismatch at " .. key)
    elseif i == #spec.path then
      assert(child.ClassName == spec.kind, "Script class mismatch at " .. key)
    elseif not engineContainers[key] then
      assert(child:IsA("Folder") or child:IsA("LuaSourceContainer"),
        "Non-code ancestor collision at " .. key)
    end
    obj = child
  end
end
'''
APPLY = r'''
local created = {}
local changed = 0
for _, spec in ipairs(specs) do
  local obj = services[spec.path[1]]
  for i = 2, #spec.path do
    local child = obj:FindFirstChild(spec.path[i])
    if not child then
      local key = table.concat(spec.path, "/", 1, i)
      local declared = declarations[key]
      child = Instance.new(declared and declared.kind or "Folder")
      child.Name = spec.path[i]
      if child:IsA("BaseScript") then
        child.Enabled = false
        table.insert(created, child)
      end
      child.Parent = obj
      changed += 1
    end
    obj = child
  end
  if obj.Source ~= spec.source then
    obj.Source = spec.source
    changed += 1
  end
end
for _, scriptObject in ipairs(created) do scriptObject.Enabled = true end
for _, spec in ipairs(specs) do
  local obj = services[spec.path[1]]
  for i = 2, #spec.path do obj = obj:FindFirstChild(spec.path[i]) end
  assert(obj and obj.ClassName == spec.kind and obj.Source == spec.source,
    "Pre-publish source verification failed for " .. table.concat(spec.path, "/"))
end
if changed > 0 then
  game:GetService("AssetService"):SavePlaceAsync({ SaveWithoutPublish = false })
end
print("ROBLOX_GITHUB_LIVE_PUBLISH_COMPLETE", changed, #specs)
return "PUBLISHED"
'''
VERIFY = r'''
for _, spec in ipairs(specs) do
  local obj = services[spec.path[1]]
  for i = 2, #spec.path do obj = obj and obj:FindFirstChild(spec.path[i]) end
  assert(obj and obj.ClassName == spec.kind and obj.Source == spec.source,
    "LIVE PUBLISH verification failed for " .. table.concat(spec.path, "/"))
end
print("ROBLOX_GITHUB_LIVE_VERIFIED", #specs)
return "VERIFIED"
'''


def spec_list():
    found = []
    for path, (file, kind) in sorted(discover().items()):
        if not any(path[:len(anchor)] == anchor for anchor in ANCHORS):
            raise ValueError("Target outside approved script containers: " + "/".join(path))
        if kind not in ("Script", "LocalScript", "ModuleScript"):
            raise ValueError("Unsupported script type: " + str(kind))
        source = file.read_text(encoding="utf-8")
        if any(ord(ch) < 32 and ch not in "\n\r\t" for ch in source):
            raise ValueError("Unsupported control characters in " + str(file))
        found.append((path, kind, source))
    if not found:
        raise ValueError("No Git-managed scripts found")
    return found


def lua_string(s):
    return json.dumps(s, ensure_ascii=False)


def make_script(specs, verify=False):
    records = []
    for path, kind, source in specs:
        paths = "{" + ",".join(lua_string(p) for p in path) + "}"
        records.append("{path=" + paths + ",kind=" + lua_string(kind) +
                       ",source=" + lua_string(source) + "}")
    script = PREAMBLE.replace("%SPECS%", "{\n" + ",\n".join(records) + "\n}") + (VERIFY if verify else APPLY)
    if len(script.encode("utf-8")) > 3000000:
        raise ValueError("Cloud task too large; publishing safely needs batching")
    return script


class Cloud:
    def __init__(self):
        self.key = os.environ.get("ROBLOX_API_KEY", "")
        self.universe = os.environ.get("ROBLOX_UNIVERSE_ID", "")
        self.place = os.environ.get("ROBLOX_PLACE_ID", "")
        if not self.key or not self.universe.isdecimal() or not self.place.isdecimal():
            raise ValueError("ROBLOX_API_KEY, ROBLOX_UNIVERSE_ID, ROBLOX_PLACE_ID required")
        self.base = f"https://apis.roblox.com/cloud/v2/universes/{self.universe}/places/{self.place}/"

    def request(self, method, url, body=None):
        if not url.startswith(self.base):
            raise ValueError("Unexpected Roblox API path")
        data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        for retry in range(4):
            req = urllib.request.Request(url, data=data, method=method, headers={
                "x-api-key": self.key, "Content-Type": "application/json"
            })
            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                if exc.code in (429, 500, 502, 503, 504) and retry < 3:
                    time.sleep(3 * (2 ** retry))
                    continue
                raise RuntimeError(f"Roblox API HTTP {exc.code}: " +
                                   exc.read(800).decode("utf-8", errors="replace")) from None
        raise RuntimeError("Cloud request exhausted retries")

    def task(self, source):
        result = self.request("POST", self.base + "luau-execution-session-tasks", {"script": source})
        path = result.get("path", "")
        prefix = f"universes/{self.universe}/places/{self.place}/versions/"
        if not path.startswith(prefix) or "/luau-execution-sessions/" not in path or "/tasks/" not in path:
            raise RuntimeError("Unexpected Luau task identifier")
        url = "https://apis.roblox.com/cloud/v2/" + path
        start = time.monotonic()
        while result.get("state") not in ("COMPLETE", "FAILED", "CANCELLED"):
            if time.monotonic() - start > 350:
                raise RuntimeError("Luau execution timed out; check task state before retrying")
            time.sleep(5)
            result = self.request("GET", url)
        if result["state"] != "COMPLETE":
            raise RuntimeError("Luau task failed: " + str(result.get("error", result["state"])))
        return result


def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--deploy", action="store_true")
    args = parser.parse_args()
    records = spec_list()
    publish = make_script(records)
    verify = make_script(records, verify=True)
    print(f"Validated {len(records)} mapped scripts; no full-place upload", flush=True)
    if args.check:
        return
    cloud = Cloud()
    cloud.task(publish)
    cloud.task(verify)
    print("Post-publication source verification PASSED", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, KeyError) as error:
        print("SAFE STOP: " + str(error), file=sys.stderr)
        sys.exit(1)
