#!/usr/bin/env python3
"""Upload the exported lobby map and build it in the lobby place.

art/blender/scripts/export_lobby_roblox.py writes art/roblox/lobby/ (one .glb per
unique mesh, palette.png, manifest.json). This script:

  --check    validate the export and the recorded asset ids (offline, no key)
  --upload   upload what is not uploaded yet: palette.png and the particle
             textures as Decals (resolved to Image ids), every .glb as a Model.
             Ids go to art/roblox/lobby/asset_ids.json after each upload.
  --inspect  read-only report on the lobby place (creator, Workspace contents,
             spawn locations, an existing LobbyMap)
  --place    rebuild Workspace.LobbyMap in the lobby place from the manifest and
             the recorded ids, save the place, then verify it in a fresh session

Loading fast: each unique mesh is loaded ONCE and cloned for every placement, so
a client downloads ~130 meshes and one palette texture for 2,400+ parts. Small
dressing and unreachable scenery never collide, query or touch, so physics skips
them; ground keeps precise collision so players walk on the real surface.

--place only touches Workspace.LobbyMap (replaced as a whole) and disables, never
deletes, any other SpawnLocation so players arrive at the map's arrival stones.
Like scripts/roblox_live_publish.py it needs a closed Team Create session.

Environment: ROBLOX_API_KEY, plus ROBLOX_CREATOR_GROUP_ID or ROBLOX_CREATOR_USER_ID
for --upload, and ROBLOX_UNIVERSE_ID with ROBLOX_PLACE_ID (the lobby) for
--inspect and --place.
"""
import argparse
import hashlib
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import roblox_upload_ui_assets as uploader
from roblox_live_publish import Cloud as PlaceCloud

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "art" / "roblox" / "lobby"
MANIFEST = EXPORT / "manifest.json"
IDS_FILE = EXPORT / "asset_ids.json"
VFX_TEXTURES = ROOT / "art" / "vfx" / "textures"
MAX_SCRIPT_BYTES = 3_500_000
UPLOAD_WORKERS = 4

# Per-profile render and physics settings (profiles come from the export).
PROFILES = {
    "ground": {"collide": True, "query": True, "shadow": False, "fidelity": "PreciseConvexDecomposition"},
    "structure": {"collide": True, "query": True, "shadow": True, "fidelity": "Default"},
    "prop": {"collide": True, "query": True, "shadow": True, "fidelity": "Hull"},
    "tree": {"collide": False, "query": False, "shadow": True, "fidelity": "Box"},
    "scenery": {"collide": False, "query": False, "shadow": True, "fidelity": "Box"},
    "decor": {"collide": False, "query": False, "shadow": False, "fidelity": "Box"},
    "glow": {"collide": False, "query": False, "shadow": False, "fidelity": "Box"},
    "water": {"collide": False, "query": False, "shadow": False, "fidelity": "Box"},
}


def sha1(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()


def load_ids():
    data = uploader.load_json(IDS_FILE)
    data.setdefault("images", {})
    data.setdefault("models", {})
    return data


def save_ids(data):
    uploader.write_json(IDS_FILE, data)


def manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def texture_names(m):
    names = {e["texture"] for spec in m["vfxKinds"].values() for e in spec.get("emitters", []) if e.get("texture")}
    return sorted(names)


def image_files(m):
    files = {"palette": EXPORT / m["palette"]["file"]}
    for name in texture_names(m):
        files["vfx_" + name] = VFX_TEXTURES / (name + ".png")
    return files


def check(m, ids, need_ids=False):
    problems = []
    for name, part in m["parts"].items():
        path = EXPORT / part["file"]
        if not path.is_file():
            problems.append(f"missing mesh file {part['file']}")
        elif path.stat().st_size > uploader.MAX_BYTES:
            problems.append(f"{part['file']} is over 20 MB")
        if part["tris"] > 20000:
            problems.append(f"{name} has {part['tris']} triangles (Roblox limit ~20k)")
    for item in m["instances"]:
        if item[0] not in m["parts"]:
            problems.append(f"placement of unknown part {item[0]}")
        if item[3] not in PROFILES:
            problems.append(f"unknown profile {item[3]}")
    for key, path in image_files(m).items():
        if not path.is_file():
            problems.append(f"missing image {path.relative_to(ROOT)}")
    if need_ids:
        for name, part in m["parts"].items():
            record = ids["models"].get(name)
            if not record or record.get("sha1") != sha1(EXPORT / part["file"]):
                problems.append(f"{name} is not uploaded (or changed since upload)")
        for key in image_files(m):
            if not (ids["images"].get(key) or {}).get("image"):
                problems.append(f"image {key} has no resolved image id")
    return problems


# --- Upload ---------------------------------------------------------------------

def upload(m, ids):
    key = os.environ.get("ROBLOX_API_KEY", "").strip()
    if not key:
        raise ValueError("ROBLOX_API_KEY is required for --upload")
    uploader.POLL_LIMIT_SECONDS = 600
    cloud = uploader.Cloud(key, uploader.creator_from_env())
    for name, path in image_files(m).items():
        record = ids["images"].get(name) or {}
        digest = sha1(path)
        if record.get("sha1") != digest:
            decal = cloud.wait(cloud.upload(path, name=f"Flintborn lobby {name}", description="Flintborn lobby map"))
            record = {"decal": decal, "sha1": digest}
            ids["images"][name] = record
            save_ids(ids)
            print(f"image {name} -> decal {decal}", flush=True)
        if not record.get("image"):
            image, how = cloud.image_id(record["decal"])
            if how in ("resolved from decal", "already an image"):
                record["image"] = image
                save_ids(ids)
                print(f"image {name} -> image {image}", flush=True)
            else:
                print(f"image {name}: decal {record['decal']} unresolved ({how[:160]})", flush=True)
    todo = [(name, part) for name, part in m["parts"].items()
            if (ids["models"].get(name) or {}).get("sha1") != sha1(EXPORT / part["file"])]
    lock = threading.Lock()
    done = []

    def send(item):
        name, part = item
        path = EXPORT / part["file"]
        asset = cloud.wait(cloud.upload(path, asset_type="Model", content_type="model/gltf-binary",
                                        name=f"Flintborn lobby {name}", description="Flintborn lobby map mesh"))
        with lock:
            # Saved after every upload so an interrupted run never repeats one.
            ids["models"][name] = {"id": asset, "sha1": sha1(path)}
            save_ids(ids)
            done.append(name)
            print(f"[{len(done)}/{len(todo)}] {name} -> model {asset}", flush=True)

    with ThreadPoolExecutor(UPLOAD_WORKERS) as pool:
        for future in [pool.submit(send, item) for item in todo]:
            future.result()
    print(f"Uploaded {len(todo)} meshes; {len(ids['models'])} recorded", flush=True)


# --- Luau -----------------------------------------------------------------------

def lua_str(text):
    return json.dumps(text, ensure_ascii=True)


def lua_value(value):
    """JSON-compatible data as a Luau literal."""
    if isinstance(value, dict):
        return "{" + ",".join(f"[{lua_str(k)}]={lua_value(v)}" for k, v in value.items()) + "}"
    if isinstance(value, list):
        return "{" + ",".join(lua_value(v) for v in value) + "}"
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "nil"
    if isinstance(value, str):
        return lua_str(value)
    return repr(value)


INSPECT = r'''
local HttpService = game:GetService("HttpService")
local report = { creatorType = tostring(game.CreatorType), creatorId = game.CreatorId, placeId = game.PlaceId,
  streaming = workspace.StreamingEnabled, children = {}, spawns = {}, lobbyMap = nil }
for _, child in workspace:GetChildren() do
  if not child:IsA("Terrain") and not child:IsA("Camera") then
    local count = 0
    for _, d in child:GetDescendants() do if d:IsA("BasePart") then count += 1 end end
    local entry = { name = child.Name, class = child.ClassName, parts = count }
    if child:IsA("BasePart") then entry.size = tostring(child.Size); entry.position = tostring(child.Position) end
    table.insert(report.children, entry)
  end
end
for _, d in workspace:GetDescendants() do
  if d:IsA("SpawnLocation") then
    table.insert(report.spawns, { path = d:GetFullName(), enabled = d.Enabled, position = tostring(d.Position) })
  end
end
local map = workspace:FindFirstChild("LobbyMap")
if map then report.lobbyMap = { parts = #map:GetDescendants(), version = map:GetAttribute("ExportSha1") } end
local terrainCells = 0
pcall(function() terrainCells = workspace.Terrain:CountCells() end)
report.terrainCells = terrainCells
return HttpService:JSONEncode(report)
'''

PLACE = r'''
local AssetService = game:GetService("AssetService")
local CollectionService = game:GetService("CollectionService")
local HttpService = game:GetService("HttpService")
local InsertService = game:GetService("InsertService")

local data = %DATA%
local warnings = {}
local function warnf(...) table.insert(warnings, string.format(...)) end

-- 1. One template per (mesh, collision fidelity): load each Model asset once.
local meshIds, templates, pending = {}, {}, 0
for name, part in data.parts do
  pending += 1
  task.spawn(function()
    local ok, err = pcall(function()
      local model = InsertService:LoadAsset(part.id)
      local mesh = model:FindFirstChildWhichIsA("MeshPart", true)
      assert(mesh, "no MeshPart in model " .. part.id)
      meshIds[name] = mesh
      local want, got = part.size, mesh.Size
      -- The import may scale the mesh; Size is set per placement. Its proportions
      -- must match, or the axes were converted differently than expected.
      local a = { got.X / want[1], got.Y / want[2], got.Z / want[3] }
      if math.max(a[1], a[2], a[3]) / math.min(a[1], a[2], a[3]) > 1.05 then
        warnf("%s proportions differ: got %s want %.2f, %.2f, %.2f", name, tostring(got), want[1], want[2], want[3])
      end
    end)
    if not ok then warnf("%s: %s", name, tostring(err)) end
    pending -= 1
  end)
end
local started = os.clock()
while pending > 0 and os.clock() - started < 150 do task.wait(0.1) end
assert(pending == 0, "timed out loading mesh models")

local function template(name, profileName)
  local key = name .. "|" .. profileName
  if templates[key] then return templates[key] end
  local source = meshIds[name]
  if not source then return nil end
  local part = data.parts[name]
  local profile = data.profiles[profileName]
  local mesh
  local options = {
    CollisionFidelity = Enum.CollisionFidelity[profile.fidelity],
    RenderFidelity = Enum.RenderFidelity.Automatic,
  }
  local ok = pcall(function()
    mesh = AssetService:CreateMeshPartAsync(source.MeshContent, options)
  end)
  if not ok or not mesh then
    ok = pcall(function()
      mesh = AssetService:CreateMeshPartAsync(source.MeshId, options)
    end)
  end
  if not ok or not mesh then
    mesh = source:Clone()
    warnf("%s: kept the import's collision (CreateMeshPartAsync failed)", key)
  end
  mesh.Name = name
  mesh.Anchored = true
  mesh.CanCollide = profile.collide
  mesh.CanQuery = profile.query
  mesh.CanTouch = false
  mesh.CastShadow = profile.shadow
  if part.kind == "glow" then
    mesh.Material = Enum.Material.Neon
    mesh.Color = Color3.fromHex(part.color)
    mesh.TextureID = ""
  else
    mesh.Material = Enum.Material.SmoothPlastic
    mesh.Color = Color3.new(1, 1, 1)
    mesh.TextureID = data.palette
    if part.kind == "water" then
      mesh.Transparency = 0.25
      mesh.Reflectance = 0.05
    end
  end
  for _, child in mesh:GetChildren() do child:Destroy() end
  templates[key] = mesh
  return mesh
end

-- 2. Replace the map as a whole.
local old = workspace:FindFirstChild("LobbyMap")
if old then old:Destroy() end
local map = Instance.new("Model")
map.Name = "LobbyMap"
map:SetAttribute("ExportSha1", data.exportSha1)
local groups = {}
local function group(name)
  if not groups[name] then
    local folder = Instance.new("Folder")
    folder.Name = name
    folder.Parent = map
    groups[name] = folder
  end
  return groups[name]
end

local placed = 0
for line in string.gmatch(data.instances, "[^\n]+") do
  local fields = string.split(line, "|")
  local name, profileName = fields[1], fields[2]
  local n = string.split(fields[3], ",")
  for i = 1, #n do n[i] = tonumber(n[i]) end
  local source = template(name, profileName)
  if source then
    local part = source:Clone()
    part.Size = Vector3.new(n[13], n[14], n[15])
    part.CFrame = CFrame.new(n[1], n[2], n[3], n[4], n[5], n[6], n[7], n[8], n[9], n[10], n[11], n[12])
    part.Parent = group(profileName)
    placed += 1
  end
end

local function marker(name, cf, size, parent)
  local part = Instance.new("Part")
  part.Name = name
  part.Anchored = true
  part.CanCollide = false
  part.CanQuery = false
  part.CanTouch = false
  part.CastShadow = false
  part.Transparency = 1
  part.Size = size
  part.CFrame = cf
  part.Parent = parent
  return part
end

for _, c in data.colliders do
  local box = marker("TrunkCollider", CFrame.new(c[1][1], c[1][2], c[1][3], table.unpack(c[1], 4, 12)),
    Vector3.new(c[2][1], c[2][2], c[2][3]), group("colliders"))
  box.CanCollide = true
  box.CanQuery = true
end

-- 3. Live VFX from the export's sockets (ParticleEmitters and PointLights).
local function numberSequence(values, scale)
  if type(values) == "number" then return NumberSequence.new(values * scale) end
  if #values == 1 then return NumberSequence.new(values[1] * scale) end
  local keys = {}
  for i, v in values do keys[i] = NumberSequenceKeypoint.new((i - 1) / (#values - 1), v * scale) end
  return NumberSequence.new(keys)
end
local function colorSequence(values)
  if type(values) == "string" then return ColorSequence.new(Color3.fromHex(values)) end
  if #values == 1 then return ColorSequence.new(Color3.fromHex(values[1])) end
  local keys = {}
  for i, v in values do keys[i] = ColorSequenceKeypoint.new((i - 1) / (#values - 1), Color3.fromHex(v)) end
  return ColorSequence.new(keys)
end
local function range(values, scale)
  scale = scale or 1
  if type(values) == "number" then return NumberRange.new(values * scale) end
  local a, b = values[1] * scale, (values[2] or values[1]) * scale
  return NumberRange.new(math.min(a, b), math.max(a, b))
end
local vfxFolder = group("vfx")
local emitters = 0
for _, socket in data.vfx do
  local kind, position, scale = socket[1], socket[2], socket[3]
  local spec = data.vfxKinds[kind]
  local holder = marker("VFX_" .. kind, CFrame.new(position[1], position[2], position[3]), Vector3.new(0.2, 0.2, 0.2), vfxFolder)
  local attachment = Instance.new("Attachment")
  attachment.Parent = holder
  for _, e in spec.emitters or {} do
    local parent = attachment
    if e.shape then
      local box = marker(e.name .. "Shape", holder.CFrame,
        Vector3.new(e.shape[1] * scale, math.max(0.05, e.shape[2] * scale), e.shape[3] * scale), holder)
      parent = box
    end
    local emitter = Instance.new("ParticleEmitter")
    emitter.Name = e.name
    emitter.Texture = data.textures[e.texture] or ""
    if emitter.Texture == "" then warnf("no texture for %s", tostring(e.texture)) end
    if e.color then emitter.Color = colorSequence(e.color) end
    if e.size then emitter.Size = numberSequence(e.size, scale) end
    if e.transparency then emitter.Transparency = numberSequence(e.transparency, 1) end
    if e.lifetime then emitter.Lifetime = range(e.lifetime) end
    if e.rate then emitter.Rate = e.rate end
    if e.speed then emitter.Speed = range(e.speed, scale) end
    if e.spread then emitter.SpreadAngle = Vector2.new(e.spread, e.spread) end
    if e.light_emission then emitter.LightEmission = e.light_emission end
    if e.light_influence then emitter.LightInfluence = e.light_influence end
    if e.drag then emitter.Drag = e.drag end
    if e.rotation then emitter.Rotation = range(e.rotation) end
    if e.rot_speed then emitter.RotSpeed = range(e.rot_speed) end
    if e.acceleration then
      emitter.Acceleration = Vector3.new(e.acceleration[1], e.acceleration[2], e.acceleration[3]) * scale
    end
    if e.orientation == "flat" then emitter.Orientation = Enum.ParticleOrientation.VelocityPerpendicular end
    if e.flipbook then
      emitter.FlipbookLayout = Enum.ParticleFlipbookLayout["Grid" .. e.flipbook]
      emitter.FlipbookMode = Enum.ParticleFlipbookMode.OneShot
    end
    emitter.Parent = parent
    emitters += 1
  end
  if spec.light then
    local light = Instance.new("PointLight")
    light.Color = Color3.fromHex(spec.light.color)
    light.Brightness = spec.light.brightness or 1
    light.Range = math.min(60, (spec.light.range or 8) * scale)
    light.Shadows = false
    light.Parent = attachment
  end
end

-- 4. Arrival spawn, the Deploy gate and NPC spots (CollectionService tags, docs/maps).
local markers = group("markers")
local spawn = Instance.new("SpawnLocation")
spawn.Name = "LobbyArrival"
spawn.Anchored = true
spawn.CanCollide = false
spawn.CanQuery = false
spawn.CanTouch = false
spawn.Transparency = 1
spawn.Neutral = true
spawn.Duration = 0
spawn.Size = Vector3.new(6, 1, 6)
spawn.CFrame = CFrame.new(data.spawn[1], data.spawn[2] + 0.5, data.spawn[3])
for _, child in spawn:GetChildren() do child:Destroy() end
spawn.Parent = markers
CollectionService:AddTag(spawn, "LobbyArrival")
if data.deployGate then
  local gate = marker("DeployGate", CFrame.new(data.deployGate[1], data.deployGate[2] + 4, data.deployGate[3]),
    Vector3.new(10, 8, 4), markers)
  CollectionService:AddTag(gate, "DeployGate")
end
for _, spot in data.npcSpots do
  local p = spot.position
  local part = marker("NPC_" .. spot.role, CFrame.new(p[1], p[2] + 3, p[3]) * CFrame.Angles(0, math.rad(spot.yaw), 0),
    Vector3.new(2, 6, 2), markers)
  part:SetAttribute("Role", spot.role)
  CollectionService:AddTag(part, "LobbyNPCSpot")
end

map.Parent = workspace
-- Players arrive at the map: any other spawn is disabled (kept, not deleted).
local disabled = {}
for _, d in workspace:GetDescendants() do
  if d:IsA("SpawnLocation") and d ~= spawn and d.Enabled then
    d.Enabled = false
    table.insert(disabled, d:GetFullName())
  end
end
local templateCount = 0
for _ in templates do templateCount += 1 end
AssetService:SavePlaceAsync({ SaveWithoutPublish = false })
return HttpService:JSONEncode({ placed = placed, templates = templateCount, emitters = emitters,
  disabledSpawns = disabled, warnings = warnings })
'''

VERIFY = r'''
local HttpService = game:GetService("HttpService")
local CollectionService = game:GetService("CollectionService")
local map = workspace:FindFirstChild("LobbyMap")
assert(map, "LobbyMap missing after save")
local counts, meshParts, untextured = {}, 0, 0
for _, folder in map:GetChildren() do
  local n = 0
  for _, d in folder:GetDescendants() do
    if d:IsA("BasePart") then n += 1 end
    if d:IsA("MeshPart") then
      meshParts += 1
      if d.Material ~= Enum.Material.Neon and d.TextureID == "" then untextured += 1 end
    end
  end
  counts[folder.Name] = n
end
local enabledSpawns = 0
for _, d in workspace:GetDescendants() do
  if d:IsA("SpawnLocation") and d.Enabled then enabledSpawns += 1 end
end
return HttpService:JSONEncode({ version = map:GetAttribute("ExportSha1"), folders = counts, meshParts = meshParts,
  untextured = untextured, arrival = #CollectionService:GetTagged("LobbyArrival"),
  deployGate = #CollectionService:GetTagged("DeployGate"), npcSpots = #CollectionService:GetTagged("LobbyNPCSpot"),
  enabledSpawns = enabledSpawns })
'''


def place_script(m, ids):
    instance_lines = []
    for name, cf, size, prof in m["instances"]:
        numbers = ",".join(repr(v) for v in cf + size)
        instance_lines.append(f"{name}|{prof}|{numbers}")
    data = {
        "exportSha1": sha1(MANIFEST),
        "palette": f"rbxassetid://{ids['images']['palette']['image']}",
        "textures": {name: f"rbxassetid://{ids['images']['vfx_' + name]['image']}" for name in texture_names(m)},
        "parts": {name: {"id": ids["models"][name]["id"], "size": part["size"], "kind": part["kind"],
                         **({"color": part["color"]} if "color" in part else {})}
                  for name, part in m["parts"].items()},
        "profiles": PROFILES,
        "colliders": m["colliders"],
        "vfxKinds": m["vfxKinds"],
        "vfx": m["vfx"],
        "spawn": m["spawn"],
        "deployGate": m["deployGate"],
        "npcSpots": m["npcSpots"],
    }
    body = lua_value(data)
    # The placements are one long string, parsed in Luau, so the script stays small.
    body = body[:-1] + ',["instances"]=' + lua_str("\n".join(instance_lines)) + "}"
    script = PLACE.replace("%DATA%", body)
    size = len(script.encode("utf-8"))
    if size > MAX_SCRIPT_BYTES:
        raise ValueError(f"Placement script is {size} bytes; too large for one Luau task")
    return script


def show(task):
    """Prints a task's JSON return value (or the raw output if it is not JSON)."""
    output = task.get("output") or {}
    values = output.get("results") or []
    value = values[0] if values else output
    try:
        value = json.loads(value)
    except (TypeError, ValueError):
        pass
    print(json.dumps(value, indent=1), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    for flag in ("--check", "--upload", "--inspect", "--place"):
        mode.add_argument(flag, action="store_true")
    args = parser.parse_args()
    m = manifest()
    ids = load_ids()
    stats = m["stats"]
    print(f"Lobby export: {stats['uniqueParts']} unique meshes ({stats['uniqueTris']} tris, "
          f"{stats['meshBytes'] / 1e6:.1f} MB) placed {stats['placedParts']} times", flush=True)
    if args.check:
        problems = check(m, ids)
        for problem in problems:
            print("PROBLEM: " + problem)
        uploaded = sum(1 for name in m["parts"] if name in ids["models"])
        print(f"{uploaded}/{len(m['parts'])} meshes recorded as uploaded")
        return 1 if problems else 0
    if args.upload:
        problems = check(m, ids)
        if problems:
            raise ValueError("; ".join(problems))
        upload(m, ids)
        return 0
    cloud = PlaceCloud()
    if args.inspect:
        show(cloud.task(INSPECT))
        return 0
    problems = check(m, ids, need_ids=True)
    if problems:
        raise ValueError("; ".join(problems[:10]))
    script = place_script(m, ids)
    print(f"Placement script: {len(script.encode('utf-8')) / 1e6:.2f} MB", flush=True)
    show(cloud.task(script))
    show(cloud.task(VERIFY))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError, KeyError) as error:
        print("SAFE STOP: " + str(error), file=sys.stderr)
        sys.exit(1)
