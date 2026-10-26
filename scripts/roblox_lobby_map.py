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
  --diagnose compare how Roblox stored a few meshes (vertex extremes, centroid,
             winding, UV range) with the exported .glb files, plus the placed
             parts' TextureID, to find import orientation or texture problems
  --lighting set the lobby's Lighting to match the Blender scene (sun angle and
             colour, ambient, atmosphere, bloom, colour grade, sun rays) and save

Loading fast: each unique mesh is loaded ONCE and cloned for every placement, so
a client downloads ~130 meshes and one palette texture for 2,400+ parts. Small
dressing and unreachable scenery never collide, query or touch, so physics skips
them; ground keeps precise collision so players walk on the real surface.

--place replaces Workspace.LobbyMap as a whole. It never deletes anything else:
the template's Baseplate and top-level SpawnLocations move to
ServerStorage.DisabledByLobbyMap, and any other SpawnLocation is disabled, so
players arrive at the map's arrival stones.
Like scripts/roblox_live_publish.py it needs a closed Team Create session.

Environment: ROBLOX_API_KEY, plus ROBLOX_CREATOR_GROUP_ID or ROBLOX_CREATOR_USER_ID
for --upload, and ROBLOX_UNIVERSE_ID with ROBLOX_PLACE_ID (the lobby) for
--inspect and --place.
"""
import argparse
import hashlib
import json
import struct
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import roblox_upload_ui_assets as uploader
from roblox_live_publish import SAVE_PLACE, Cloud as PlaceCloud

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


# In-game tuning on top of the Blender VFX specs (owner feedback: the campfire was
# too big and every light far too bright under Realistic lighting). Per kind:
# size scales the whole effect, rate the particle count, light its PointLight.
VFX_TUNING = {
    "campfire": {"size": 0.5, "rate": 0.7, "light": 0.8},
    "brazier_fire": {"size": 0.8},
    "forge_fire": {"size": 0.8},
    "heat_glow": {"size": 0.8, "rate": 0.7},
}
LIGHT_BRIGHTNESS = 0.35  # every PointLight's brightness
LIGHT_RANGE = 0.75  # every PointLight's range
PARTICLE_GLOW = 0.6  # every emitter's LightEmission
GLOW_DIM = 0.25  # Neon flame colours darkened toward black, which softens their glow


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
    -- Neon glows by its colour's brightness: dimmed so flames read without blowing out.
    mesh.Color = Color3.fromHex(part.color):Lerp(Color3.new(0, 0, 0), data.glowDim)
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

-- Roblox's glTF import turns every mesh half a turn about Y relative to the
-- file: a vertex at (x, y, z) is stored at (-x, y, -z) (measured with
-- --diagnose; nothing is mirrored). Each placement turns it back.
local IMPORT_TURN = CFrame.Angles(0, math.pi, 0)

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
    part.CFrame = CFrame.new(n[1], n[2], n[3], n[4], n[5], n[6], n[7], n[8], n[9], n[10], n[11], n[12]) * IMPORT_TURN
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

-- The camp's boundary: invisible walls just outside the palisade, closing its gaps
-- too, so players cannot leave. Fully transparent, so the camera sees through them.
for _, b in data.barriers do
  local wall = marker("Barrier", CFrame.new(b[1][1], b[1][2], b[1][3], table.unpack(b[1], 4, 12)),
    Vector3.new(b[2][1], b[2][2], b[2][3]), group("barriers"))
  wall.CanCollide = true
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
  local kind, position, socketScale = socket[1], socket[2], socket[3]
  local spec = data.vfxKinds[kind]
  -- In-game tuning on top of the Blender spec (VFX_TUNING): size scales the whole
  -- effect (sizes, speeds, accelerations, emitter box), rate the particle count.
  local tune = data.vfxTuning[kind] or {}
  local scale = socketScale * (tune.size or 1)
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
    if e.rate then emitter.Rate = e.rate * (tune.rate or 1) end
    if e.speed then emitter.Speed = range(e.speed, scale) end
    if e.spread then emitter.SpreadAngle = Vector2.new(e.spread, e.spread) end
    if e.light_emission then emitter.LightEmission = e.light_emission * data.particleGlow end
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
    light.Brightness = (spec.light.brightness or 1) * data.lightBrightness * (tune.light or 1)
    light.Range = math.min(40, (spec.light.range or 8) * socketScale * data.lightRange)
    light.Shadows = false
    if spec.light.flicker then
      -- LightFlickerController animates these on each client (nothing replicates).
      light:SetAttribute("BaseBrightness", light.Brightness)
      CollectionService:AddTag(light, "FlickerLight")
    end
    light.Parent = attachment
  end
end
for _, l in data.lights do
  local holder = marker(l.name, CFrame.new(l.position[1], l.position[2], l.position[3]), Vector3.new(0.2, 0.2, 0.2), vfxFolder)
  local light = Instance.new("PointLight")
  light.Color = Color3.fromHex(l.color)
  light.Brightness = 1.2 * data.lightBrightness
  light.Range = l.range * data.lightRange
  light.Shadows = false
  light.Parent = holder
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
-- The template's Baseplate (top at Y = 0) would cut through the map's ground,
-- and players must arrive at the map: both move to ServerStorage (kept, not
-- deleted, so they can be put back). Other spawns elsewhere are disabled.
local shelf = game:GetService("ServerStorage"):FindFirstChild("DisabledByLobbyMap")
if not shelf then
  shelf = Instance.new("Folder")
  shelf.Name = "DisabledByLobbyMap"
  shelf.Parent = game:GetService("ServerStorage")
end
local disabled = {}
for _, child in workspace:GetChildren() do
  if (child.Name == "Baseplate" and child:IsA("BasePart")) or child:IsA("SpawnLocation") then
    child.Parent = shelf
    table.insert(disabled, "moved " .. child.Name .. " to ServerStorage.DisabledByLobbyMap")
  end
end
for _, d in workspace:GetDescendants() do
  if d:IsA("SpawnLocation") and d ~= spawn and d.Enabled then
    d.Enabled = false
    table.insert(disabled, "disabled " .. d:GetFullName())
  end
end
local templateCount = 0
for _ in templates do templateCount += 1 end
%SAVE_PLACE%
return HttpService:JSONEncode({ placed = placed, templates = templateCount, emitters = emitters,
  disabledSpawns = disabled, warnings = warnings })
'''.replace("%SAVE_PLACE%", SAVE_PLACE)

# The lobby's look, matched to the Blender scene (art/blender/lobby): a warm
# afternoon sun from the west-southwest about 40 degrees up, a cool sky fill,
# soft haze, and bloom so the Neon flames glow. Colours are sRGB hex.
LIGHTING_STYLE = {
    "brightness": 2.0,
    "exposure": -0.2,
    "ambient": "#5C5046",
    "outdoorAmbient": "#8F8C7E",
    "colorShiftBottom": "#2B261F",
    "environmentDiffuse": 1.0,
    "environmentSpecular": 0.3,
    "shadowSoftness": 0.25,
    "atmosphere": {"density": 0.28, "offset": 0.2, "color": "#CBC3A6", "decay": "#9C8466", "glare": 0.15,
                   "haze": 1.4},
    "bloom": {"intensity": 0.3, "size": 18, "threshold": 2.2},
    "colorCorrection": {"brightness": 0.0, "contrast": 0.1, "saturation": 0.15, "tint": "#FFF6EA"},
    "sunRays": {"intensity": 0.03, "spread": 0.5},
    "sunAngularSize": 12,
}

LIGHTING = r'''
local HttpService = game:GetService("HttpService")
local Lighting = game:GetService("Lighting")
local cfg = %DATA%
local report = { warnings = {} }

-- The sun: the clock time and latitude whose sun direction is nearest the scene's.
local target = Vector3.new(cfg.sun.direction[1], cfg.sun.direction[2], cfg.sun.direction[3]).Unit
local best, bestTime, bestLatitude = -2, 14, 41.7
local function try(latitude, clock)
  Lighting.GeographicLatitude = latitude
  Lighting.ClockTime = clock
  local dot = Lighting:GetSunDirection():Dot(target)
  if dot > best then best, bestTime, bestLatitude = dot, clock, latitude end
end
for latitude = -66, 66, 3 do
  for clock = 6, 18, 0.25 do try(latitude, clock) end
end
local coarseLatitude, coarseTime = bestLatitude, bestTime
for latitude = coarseLatitude - 3, coarseLatitude + 3, 0.5 do
  for clock = coarseTime - 0.25, coarseTime + 0.25, 0.02 do try(latitude, clock) end
end
Lighting.GeographicLatitude = bestLatitude
Lighting.ClockTime = bestTime
report.clockTime = bestTime
report.latitude = bestLatitude
report.sunErrorDegrees = math.deg(math.acos(math.clamp(best, -1, 1)))
if report.sunErrorDegrees > 10 then table.insert(report.warnings, "sun direction is off by more than 10 degrees") end

local style = cfg.style
-- Realistic lighting (Studio's Lighting > LightingStyle, which replaced
-- Technology). Cloud scripts may not be allowed to set it; then it stays as set
-- in Studio.
local ok, err = pcall(function() Lighting.LightingStyle = Enum.LightingStyle.Realistic end)
report.lightingStyle = if ok then "Realistic" else ("unchanged (set it in Studio): " .. tostring(err))
Lighting.Brightness = style.brightness
Lighting.ExposureCompensation = style.exposure
Lighting.Ambient = Color3.fromHex(style.ambient)
Lighting.OutdoorAmbient = Color3.fromHex(style.outdoorAmbient)
-- Sunlit faces take the scene sun's warm colour, softened toward white.
Lighting.ColorShift_Top = Color3.new(1, 1, 1):Lerp(Color3.fromHex(cfg.sun.color), 0.6)
Lighting.ColorShift_Bottom = Color3.fromHex(style.colorShiftBottom)
Lighting.EnvironmentDiffuseScale = style.environmentDiffuse
Lighting.EnvironmentSpecularScale = style.environmentSpecular
Lighting.GlobalShadows = true
Lighting.ShadowSoftness = style.shadowSoftness

-- One of each effect: the first existing one is reused, otherwise one is made.
local function single(className)
  local object = Lighting:FindFirstChildWhichIsA(className)
  if not object then
    object = Instance.new(className)
    object.Parent = Lighting
  end
  return object
end
local atmosphere = single("Atmosphere")
atmosphere.Density = style.atmosphere.density
atmosphere.Offset = style.atmosphere.offset
atmosphere.Color = Color3.fromHex(style.atmosphere.color)
atmosphere.Decay = Color3.fromHex(style.atmosphere.decay)
atmosphere.Glare = style.atmosphere.glare
atmosphere.Haze = style.atmosphere.haze
local sky = single("Sky")
sky.SunAngularSize = style.sunAngularSize
sky.CelestialBodiesShown = true
local bloom = single("BloomEffect")
bloom.Enabled = true
bloom.Intensity = style.bloom.intensity
bloom.Size = style.bloom.size
bloom.Threshold = style.bloom.threshold
local grade = single("ColorCorrectionEffect")
grade.Enabled = true
grade.Brightness = style.colorCorrection.brightness
grade.Contrast = style.colorCorrection.contrast
grade.Saturation = style.colorCorrection.saturation
grade.TintColor = Color3.fromHex(style.colorCorrection.tint)
local rays = single("SunRaysEffect")
rays.Enabled = true
rays.Intensity = style.sunRays.intensity
rays.Spread = style.sunRays.spread

%SAVE_PLACE%
return HttpService:JSONEncode(report)
'''.replace("%SAVE_PLACE%", SAVE_PLACE)

DIAGNOSE = r'''
local AssetService = game:GetService("AssetService")
local HttpService = game:GetService("HttpService")
local InsertService = game:GetService("InsertService")
local parts = %DATA%
local out = {}
for name, id in parts do
  local entry = {}
  out[name] = entry
  local ok, err = pcall(function()
    local model = InsertService:LoadAsset(id)
    local mesh = model:FindFirstChildWhichIsA("MeshPart", true)
    entry.size = { mesh.Size.X, mesh.Size.Y, mesh.Size.Z }
    entry.meshSize = { mesh.MeshSize.X, mesh.MeshSize.Y, mesh.MeshSize.Z }
    entry.textureId = mesh.TextureID
    local kids = {}
    for _, d in model:GetDescendants() do table.insert(kids, d.ClassName .. ":" .. d.Name) end
    entry.descendants = kids
    local editable = AssetService:CreateEditableMeshAsync(mesh.MeshContent)
    local verts = editable:GetVertices()
    local sum, n = Vector3.zero, 0
    local lo, hi = Vector3.new(math.huge, math.huge, math.huge), Vector3.new(-math.huge, -math.huge, -math.huge)
    local far = {}
    for _, v in verts do
      local p = editable:GetPosition(v)
      sum += p
      n += 1
      lo = lo:Min(p)
      hi = hi:Max(p)
    end
    local c = sum / n
    entry.vertices = n
    entry.min = { lo.X, lo.Y, lo.Z }
    entry.max = { hi.X, hi.Y, hi.Z }
    entry.centroid = { c.X, c.Y, c.Z }
    -- Mirroring flips winding: compare each face's geometric normal with its stored normals.
    local agree, against = 0, 0
    local faces = editable:GetFaces()
    entry.faces = #faces
    for i = 1, math.min(#faces, 400) do
      local fv = editable:GetFaceVertices(faces[i])
      local a, b, cc = editable:GetPosition(fv[1]), editable:GetPosition(fv[2]), editable:GetPosition(fv[3])
      local geometric = (b - a):Cross(cc - a)
      local normals = editable:GetFaceNormals(faces[i])
      if #normals > 0 and geometric.Magnitude > 1e-9 then
        if geometric:Dot(editable:GetNormal(normals[1])) >= 0 then agree += 1 else against += 1 end
      end
    end
    entry.windingAgree = agree
    entry.windingAgainst = against
    local uvlo, uvhi = Vector2.new(math.huge, math.huge), Vector2.new(-math.huge, -math.huge)
    local uvs = editable:GetUVs()
    for i = 1, math.min(#uvs, 2000) do
      local uv = editable:GetUV(uvs[i])
      uvlo = uvlo:Min(uv)
      uvhi = uvhi:Max(uv)
    end
    entry.uvs = #uvs
    entry.uvMin = { uvlo.X, uvlo.Y }
    entry.uvMax = { uvhi.X, uvhi.Y }
  end)
  if not ok then entry.error = tostring(err) end
end
local map = workspace:FindFirstChild("LobbyMap")
local placed = {}
if map then
  for _, d in map:GetDescendants() do
    if d:IsA("MeshPart") and parts[d.Name] and not placed[d.Name] then
      placed[d.Name] = { textureId = d.TextureID, size = tostring(d.Size), cframe = tostring(d.CFrame),
        material = d.Material.Name, color = d.Color:ToHex(), transparency = d.Transparency }
    end
  end
end
return HttpService:JSONEncode({ meshes = out, placed = placed })
'''

# Builds the lobby HUD inside the place (server side, never parented to a
# player) with the deployed modules and reports what each navigation button and
# the currency icons hold, to debug sprites that do not show.
UI_PROBE = r'''
local HttpService = game:GetService("HttpService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local StarterPlayer = game:GetService("StarterPlayer")
local report = {}
local ok, err = pcall(function()
  local UiAssets = require(ReplicatedStorage.Shared.UI.UiAssets)
  report.idCount = 0
  for _ in UiAssets.Ids do report.idCount += 1 end
  report.backpackId = UiAssets.image("icon_backpack")
  report.frameSlotId = UiAssets.image("frame_slot")
  local hudFolder = StarterPlayer.StarterPlayerScripts.Client.Hud
  local Layout = require(hudFolder.Layout)
  local LobbyHud = require(hudFolder.LobbyHud)
  local holder = Instance.new("ScreenGui")
  holder.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
  local hud = LobbyHud.new(holder, Layout.Get(), function() return true end)
  local function describe(object)
    local items = {}
    for _, child in object:GetChildren() do
      local entry = { name = child.Name, class = child.ClassName }
      if child:IsA("GuiObject") then
        entry.z = child.ZIndex
        entry.size = tostring(child.AbsoluteSize) .. " / " .. tostring(child.Size)
        entry.visible = child.Visible
      end
      if child:IsA("ImageLabel") or child:IsA("ImageButton") then
        entry.image = child.Image
        entry.scaleType = child.ScaleType.Name
        entry.transparency = child.ImageTransparency
      end
      if child:IsA("TextLabel") or child:IsA("TextButton") then entry.text = child.Text end
      table.insert(items, entry)
    end
    return items
  end
  local nav = hud.root:FindFirstChild("Navigation")
  report.inventory = describe(nav:FindFirstChild("Inventory"))
  report.currency = describe(hud.root:FindFirstChild("Currency"))
  holder:Destroy()
  -- Can the place load the image content? EditableImage loads respect asset
  -- permissions, and PreloadAsync reports each asset's fetch status.
  local AssetService = game:GetService("AssetService")
  local ContentProvider = game:GetService("ContentProvider")
  report.loads = {}
  for _, name in { "icon_backpack", "icon_coin", "icon_mountain", "icon_chest", "icon_scroll", "icon_coin_bag", "icon_anvil", "icon_swap", "icon_gear", "icon_gem", "icon_group", "icon_crown", "icon_add_friend", "icon_down" } do
    local id = UiAssets.image(name)
    local entry = { id = id }
    local okImage, result = pcall(function()
      return AssetService:CreateEditableImageAsync(Content.fromUri(id))
    end)
    entry.editable = if okImage then tostring(result.Size) else tostring(result)
    pcall(function()
      ContentProvider:PreloadAsync({ id }, function(_, status)
        entry.preload = status.Name
      end)
    end)
    report.loads[name] = entry
  end
end)
report.ok = ok
report.err = if ok then nil else tostring(err)
return HttpService:JSONEncode(report)
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
-- The floor: raycast the ground parts at the export's probe points and compare
-- the hit height with the Blender surface (a turned or missing chunk misses or
-- lands far off).
local probes = %PROBES%
local params = RaycastParams.new()
params.FilterType = Enum.RaycastFilterType.Include
params.FilterDescendantsInstances = { map:FindFirstChild("ground") }
local floor = { probes = #probes, within1 = 0, within3 = 0, missed = 0, worst = {} }
for _, p in probes do
  local hit = workspace:Raycast(Vector3.new(p[1], 300, p[3]), Vector3.new(0, -600, 0), params)
  if not hit then
    floor.missed += 1
    table.insert(floor.worst, { p[1], p[3], "miss" })
  else
    local off = math.abs(hit.Position.Y - p[2])
    if off <= 1 then floor.within1 += 1 end
    if off <= 3 then floor.within3 += 1 else table.insert(floor.worst, { p[1], p[3], off, hit.Instance.Name }) end
  end
end
while #floor.worst > 12 do table.remove(floor.worst) end
-- The boundary is closed: rays from the arrival spawn outward every 10 degrees,
-- at walking and jumping height, must all hit a barrier.
local barriers = map:FindFirstChild("barriers")
local boundary = { rays = 0, hits = 0, open = {} }
local arrival = CollectionService:GetTagged("LobbyArrival")[1]
if barriers and arrival then
  local wallParams = RaycastParams.new()
  wallParams.FilterType = Enum.RaycastFilterType.Include
  wallParams.FilterDescendantsInstances = { barriers }
  for _, height in { 3, 12 } do
    for degrees = 0, 350, 10 do
      local direction = Vector3.new(math.cos(math.rad(degrees)), 0, math.sin(math.rad(degrees)))
      boundary.rays += 1
      if workspace:Raycast(arrival.Position + Vector3.new(0, height, 0), direction * 400, wallParams) then
        boundary.hits += 1
      elseif #boundary.open < 12 then
        table.insert(boundary.open, degrees .. "@" .. height)
      end
    end
  end
end
return HttpService:JSONEncode({ version = map:GetAttribute("ExportSha1"), folders = counts, meshParts = meshParts,
  untextured = untextured, arrival = #CollectionService:GetTagged("LobbyArrival"),
  deployGate = #CollectionService:GetTagged("DeployGate"), npcSpots = #CollectionService:GetTagged("LobbyNPCSpot"),
  enabledSpawns = enabledSpawns, floor = floor, boundary = boundary })
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
        "vfxTuning": VFX_TUNING,
        "particleGlow": PARTICLE_GLOW,
        "lightBrightness": LIGHT_BRIGHTNESS,
        "lightRange": LIGHT_RANGE,
        "glowDim": GLOW_DIM,
        "colliders": m["colliders"],
        "barriers": m.get("barriers", []),
        "vfxKinds": m["vfxKinds"],
        "vfx": m["vfx"],
        "spawn": m["spawn"],
        "deployGate": m["deployGate"],
        "npcSpots": m["npcSpots"],
        "lights": (m.get("lighting") or {}).get("lights", []),
    }
    body = lua_value(data)
    # The placements are one long string, parsed in Luau, so the script stays small.
    body = body[:-1] + ',["instances"]=' + lua_str("\n".join(instance_lines)) + "}"
    script = PLACE.replace("%DATA%", body)
    size = len(script.encode("utf-8"))
    if size > MAX_SCRIPT_BYTES:
        raise ValueError(f"Placement script is {size} bytes; too large for one Luau task")
    return script


def lighting_script(m):
    sun = (m.get("lighting") or {}).get("sun")
    if not sun:
        raise ValueError("manifest has no lighting.sun; re-run the export")
    return LIGHTING.replace("%DATA%", lua_value({"sun": sun, "style": LIGHTING_STYLE}))


def glb_stats(path):
    """Vertex extremes and centroid of a .glb's first primitive (glTF axes = Roblox axes)."""
    data = path.read_bytes()
    length = struct.unpack_from("<I", data, 12)[0]
    doc = json.loads(data[20:20 + length])
    binary = data[20 + length + 8:]
    primitive = doc["meshes"][0]["primitives"][0]
    accessor = doc["accessors"][primitive["attributes"]["POSITION"]]
    view = doc["bufferViews"][accessor["bufferView"]]
    offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    count = accessor["count"]
    points = [struct.unpack_from("<3f", binary, offset + 12 * i) for i in range(count)]
    uv_acc = doc["accessors"][primitive["attributes"]["TEXCOORD_0"]]
    uv_view = doc["bufferViews"][uv_acc["bufferView"]]
    uv_off = uv_view.get("byteOffset", 0) + uv_acc.get("byteOffset", 0)
    uvs = [struct.unpack_from("<2f", binary, uv_off + 8 * i) for i in range(uv_acc["count"])]
    return {
        "vertices": count,
        "min": [round(min(p[i] for p in points), 3) for i in range(3)],
        "max": [round(max(p[i] for p in points), 3) for i in range(3)],
        "centroid": [round(sum(p[i] for p in points) / count, 3) for i in range(3)],
        "uvMin": [round(min(u[i] for u in uvs), 3) for i in range(2)],
        "uvMax": [round(max(u[i] for u in uvs), 3) for i in range(2)],
    }


DIAGNOSE_PARTS = ["Ground_Plateau_01", "Ground_DirtPlazaPaths_01", "VaultHall", "DeployGate", "CliffSection",
                  "Barrel", "PalisadeSection", "LogBench"]


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
    for flag in ("--check", "--upload", "--inspect", "--place", "--lighting", "--diagnose", "--uiprobe"):
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
    if args.uiprobe:
        show(cloud.task(UI_PROBE))
        return 0
    if args.diagnose:
        names = [n for n in DIAGNOSE_PARTS if n in m["parts"] and n in ids["models"]]
        for name in names:
            print(name, "EXPORT", json.dumps(glb_stats(EXPORT / m["parts"][name]["file"])), flush=True)
        script = DIAGNOSE.replace("%DATA%", lua_value({n: ids["models"][n]["id"] for n in names}))
        show(cloud.task(script))
        return 0
    if args.lighting:
        show(cloud.task(lighting_script(m)))
        return 0
    problems = check(m, ids, need_ids=True)
    if problems:
        raise ValueError("; ".join(problems[:10]))
    script = place_script(m, ids)
    print(f"Placement script: {len(script.encode('utf-8')) / 1e6:.2f} MB", flush=True)
    show(cloud.task(script))
    show(cloud.task(VERIFY.replace("%PROBES%", lua_value(m.get("groundProbes", [])))))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError, KeyError) as error:
        print("SAFE STOP: " + str(error), file=sys.stderr)
        sys.exit(1)
