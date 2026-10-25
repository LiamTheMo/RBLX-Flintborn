#!/usr/bin/env python3
"""Upload the default player character and install it as everyone's character.

art/blender/scripts/build_09_character.py exports art/roblox/character/ (one .glb
per R6 part and clothing piece, manifest.json with sizes, clothing offsets and
the standard R6 Motor6D values) and art/character/textures/ (shirt and pants
maps, ten tribe pants colours, the face). This script:

  --check    validate the export and the recorded ids (offline)
  --upload   upload what is new or changed: meshes as Models, textures as Decals
             resolved to Image ids; ids go to art/roblox/character/asset_ids.json
  --install  in the place ROBLOX_PLACE_ID: build StarterPlayer.StarterCharacter
             (an R6 rig: HumanoidRootPart, the six rounded MeshParts, Humanoid
             RigType R6, Roblox's default Motor6Ds, the face decal, and the
             clothing welded to its parts), put one pants look per tribe colour in
             ReplicatedStorage.CharacterOutfits (OutfitService applies them), turn
             off StarterPlayer.LoadCharacterAppearance so avatars don't load on
             top, save the place, and verify in a fresh session

The StarterCharacter and CharacterOutfits are replaced as a whole; nothing else
is touched. Run --install once per place (the workflow does lobby and world).

Environment: ROBLOX_API_KEY, ROBLOX_CREATOR_GROUP_ID (or _USER_ID) for --upload,
ROBLOX_UNIVERSE_ID and ROBLOX_PLACE_ID for --install.
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
EXPORT = ROOT / "art" / "roblox" / "character"
MANIFEST = EXPORT / "manifest.json"
IDS_FILE = EXPORT / "asset_ids.json"
UPLOAD_WORKERS = 4


def sha1(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()


def manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def load_ids():
    data = uploader.load_json(IDS_FILE)
    data.setdefault("images", {})
    data.setdefault("models", {})
    return data


def mesh_files(m):
    files = {name: EXPORT / info["file"] for name, info in m["parts"].items()}
    files.update({name: EXPORT / info["file"] for name, info in m["clothing"].items()})
    return files


def image_files(m):
    folder = ROOT / m["textureDir"]
    wanted = ["shirt_color", "shirt_normal", "shirt_roughness", "pants_normal", "pants_roughness", "face"]
    wanted += ["pants_color_" + name.lower() for name in m["colors"]["tribes"]]
    return {key: folder / m["textures"][key] for key in wanted}


def check(m, ids, need_ids=False):
    problems = []
    for name, path in list(mesh_files(m).items()) + list(image_files(m).items()):
        if not path.is_file():
            problems.append(f"missing {path.relative_to(ROOT)}")
    for name, info in list(m["parts"].items()) + list(m["clothing"].items()):
        if info["tris"] > 20000:
            problems.append(f"{name} has {info['tris']} triangles (Roblox limit ~20k)")
    if need_ids:
        for name, path in mesh_files(m).items():
            if (ids["models"].get(name) or {}).get("sha1") != sha1(path):
                problems.append(f"mesh {name} is not uploaded (or changed)")
        for key, path in image_files(m).items():
            record = ids["images"].get(key) or {}
            if record.get("sha1") != sha1(path) or not record.get("image"):
                problems.append(f"image {key} has no resolved image id")
    return problems


def upload(m, ids):
    key = os.environ.get("ROBLOX_API_KEY", "").strip()
    if not key:
        raise ValueError("ROBLOX_API_KEY is required for --upload")
    uploader.POLL_LIMIT_SECONDS = 600
    cloud = uploader.Cloud(key, uploader.creator_from_env())
    lock = threading.Lock()

    def save():
        uploader.write_json(IDS_FILE, ids)

    def send_image(item):
        name, path = item
        digest = sha1(path)
        record = ids["images"].get(name) or {}
        if record.get("sha1") != digest:
            decal = cloud.wait(cloud.upload(path, name=f"Flintborn character {name}", description="Flintborn character"))
            record = {"decal": decal, "sha1": digest}
        if not record.get("image"):
            image, how = cloud.image_id(record["decal"])
            if how in ("resolved from decal", "already an image"):
                record["image"] = image
            else:
                print(f"image {name}: decal {record['decal']} unresolved ({how[:160]})", flush=True)
        with lock:
            ids["images"][name] = record
            save()
            print(f"image {name} -> {record.get('image')}", flush=True)

    def send_mesh(item):
        name, path = item
        if (ids["models"].get(name) or {}).get("sha1") == sha1(path):
            return
        asset = cloud.wait(cloud.upload(path, asset_type="Model", content_type="model/gltf-binary",
                                        name=f"Flintborn character {name}", description="Flintborn character mesh"))
        with lock:
            ids["models"][name] = {"id": asset, "sha1": sha1(path)}
            save()
            print(f"mesh {name} -> model {asset}", flush=True)

    with ThreadPoolExecutor(UPLOAD_WORKERS) as pool:
        jobs = [pool.submit(send_image, item) for item in image_files(m).items()]
        jobs += [pool.submit(send_mesh, item) for item in mesh_files(m).items()]
        for job in jobs:
            job.result()


def lua_str(text):
    return json.dumps(text, ensure_ascii=True)


def lua_value(value):
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


INSTALL = r'''
local AssetService = game:GetService("AssetService")
local HttpService = game:GetService("HttpService")
local InsertService = game:GetService("InsertService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local StarterPlayer = game:GetService("StarterPlayer")

local data = %DATA%
local report = { warnings = {} }
local function warnf(...) table.insert(report.warnings, string.format(...)) end
local function image(key) return "rbxassetid://" .. tostring(data.images[key]) end

-- Each mesh model loaded once (in parallel), then a MeshPart made from it.
local sources, pending = {}, 0
for name, id in data.models do
  pending += 1
  task.spawn(function()
    local ok, err = pcall(function()
      local model = InsertService:LoadAsset(id)
      sources[name] = model:FindFirstChildWhichIsA("MeshPart", true)
    end)
    if not ok then warnf("%s: %s", name, tostring(err)) end
    pending -= 1
  end)
end
local started = os.clock()
while pending > 0 and os.clock() - started < 120 do task.wait(0.1) end
for name in data.models do assert(sources[name], "mesh model did not load: " .. name) end

local function meshPart(name, fidelity)
  local source = sources[name]
  local part
  local ok = pcall(function()
    part = AssetService:CreateMeshPartAsync(source.MeshContent, {
      CollisionFidelity = fidelity, RenderFidelity = Enum.RenderFidelity.Automatic })
  end)
  if not ok or not part then
    part = source:Clone()
    for _, child in part:GetChildren() do child:Destroy() end
    warnf("%s kept the import's collision", name)
  end
  part.Name = name
  part.Anchored = false
  part.Material = Enum.Material.SmoothPlastic
  return part
end

-- A pants or shirt look: a SurfaceAppearance (colour, normal, roughness maps), or
-- a texture id when SurfaceAppearance maps cannot be set here.
local surfaceOk = pcall(function()
  local probe = Instance.new("SurfaceAppearance")
  probe.ColorMap = image("shirt_color")
  probe:Destroy()
end)
report.surfaceAppearance = surfaceOk
local function look(name, colorKey, normalKey, roughKey)
  if surfaceOk then
    local appearance = Instance.new("SurfaceAppearance")
    appearance.Name = name
    appearance.ColorMap = image(colorKey)
    appearance.NormalMap = image(normalKey)
    appearance.RoughnessMap = image(roughKey)
    return appearance
  end
  local holder = Instance.new("Folder")
  holder.Name = name
  holder:SetAttribute("TextureId", image(colorKey))
  return holder
end
local function wear(part, source)
  if source:IsA("SurfaceAppearance") then
    source:Clone().Parent = part
  else
    part.TextureID = source:GetAttribute("TextureId")
  end
end

-- The rig: standard R6 positions around the HumanoidRootPart at (0, 3, 0).
local model = Instance.new("Model")
model.Name = "StarterCharacter"
local root = Instance.new("Part")
root.Name = "HumanoidRootPart"
root.Size = Vector3.new(2, 2, 1)
root.Transparency = 1
root.CanCollide = false
root.CFrame = CFrame.new(0, 3, 0)
root.Parent = model
model.PrimaryPart = root

local positions = {
  Torso = Vector3.new(0, 3, 0), Head = Vector3.new(0, 4.5, 0),
  ["Right Arm"] = Vector3.new(1.5, 3, 0), ["Left Arm"] = Vector3.new(-1.5, 3, 0),
  ["Right Leg"] = Vector3.new(0.5, 1, 0), ["Left Leg"] = Vector3.new(-0.5, 1, 0),
}
local skin = Color3.fromHex(data.colors.skin)
local parts = { HumanoidRootPart = root }
for name, info in data.parts do
  local part = meshPart(name, Enum.CollisionFidelity.Box)
  -- The rounded body meshes are symmetric, so the import's half turn changes nothing.
  part.Size = Vector3.new(info.size[1], info.size[2], info.size[3])
  part.CFrame = CFrame.new(positions[name])
  part.Color = skin
  part.CanCollide = name == "Torso" or name == "Head"
  part.Parent = model
  parts[name] = part
end
local face = Instance.new("Decal")
face.Name = "face"
face.Face = Enum.NormalId.Front
face.Texture = image("face")
face.Parent = parts.Head

local humanoid = Instance.new("Humanoid")
humanoid.RigType = Enum.HumanoidRigType.R6
humanoid.Parent = model

for name, motor in data.motors do
  local joint = Instance.new("Motor6D")
  joint.Name = name
  joint.Part0 = parts[motor.part0]
  joint.Part1 = parts[motor.part1]
  joint.C0 = CFrame.new(table.unpack(motor.c0))
  joint.C1 = CFrame.new(table.unpack(motor.c1))
  joint.Parent = parts[motor.part0]
end

-- Clothing: welded to its part. Offsets were exported facing +Z, so they turn
-- half a turn to match the rig, which faces -Z; the imported meshes already do.
local outfits = Instance.new("Folder")
outfits.Name = "CharacterOutfits"
for colorName in data.colors.tribes do
  look("Pants_" .. colorName, "pants_color_" .. string.lower(colorName), "pants_normal", "pants_roughness").Parent = outfits
end
local shirtLook = look("Shirt", "shirt_color", "shirt_normal", "shirt_roughness")
for name, info in data.clothing do
  local piece = meshPart(name, Enum.CollisionFidelity.Box)
  piece.Size = Vector3.new(info.size[1], info.size[2], info.size[3])
  local base = parts[info.part]
  piece.CFrame = base.CFrame * CFrame.new(-info.offset[1], info.offset[2], -info.offset[3])
  piece.Massless = true
  piece.CanCollide = false
  piece.CanQuery = false
  piece.CanTouch = false
  piece.Color = Color3.new(1, 1, 1)
  wear(piece, if name == "Shirt" then shirtLook else outfits:FindFirstChild("Pants_" .. data.defaultPants))
  local weld = Instance.new("Weld")
  weld.Name = name .. "Weld"
  weld.Part0 = base
  weld.Part1 = piece
  weld.C0 = base.CFrame:ToObjectSpace(piece.CFrame)
  weld.Parent = piece
  piece.Parent = model
end

local old = StarterPlayer:FindFirstChild("StarterCharacter")
if old then old:Destroy() end
model.Parent = StarterPlayer
local oldOutfits = ReplicatedStorage:FindFirstChild("CharacterOutfits")
if oldOutfits then oldOutfits:Destroy() end
outfits.Parent = ReplicatedStorage
local okAppearance, appearanceErr = pcall(function() StarterPlayer.LoadCharacterAppearance = false end)
report.loadCharacterAppearance = if okAppearance then "off" else ("unchanged: " .. tostring(appearanceErr))
AssetService:SavePlaceAsync({ SaveWithoutPublish = false })
report.parts = #model:GetChildren()
return HttpService:JSONEncode(report)
'''

# What the installed character actually wears, and whether the place can load each
# image (EditableImage loads respect asset permissions).
PROBE = r'''
local AssetService = game:GetService("AssetService")
local HttpService = game:GetService("HttpService")
local character = game:GetService("StarterPlayer"):FindFirstChild("StarterCharacter")
assert(character, "StarterCharacter missing")
local report = { pieces = {}, loads = {} }
local seen = {}
local function test(id)
  if id == nil or id == "" or seen[id] then return end
  seen[id] = true
  local ok, result = pcall(function()
    return AssetService:CreateEditableImageAsync(Content.fromUri(id))
  end)
  report.loads[id] = if ok then tostring(result.Size) else tostring(result)
end
for _, d in character:GetDescendants() do
  if d:IsA("MeshPart") then
    local appearance = d:FindFirstChildWhichIsA("SurfaceAppearance")
    report.pieces[d.Name] = { textureId = d.TextureID, color = d.Color:ToHex(), material = d.Material.Name,
      surface = appearance and appearance.ColorMap or nil }
    test(d.TextureID)
  elseif d:IsA("Decal") then
    report.pieces["decal:" .. d.Name] = { texture = d.Texture, face = d.Face.Name, parent = d.Parent.Name }
    test(d.Texture)
  end
end
return HttpService:JSONEncode(report)
'''

VERIFY = r'''
local HttpService = game:GetService("HttpService")
local character = game:GetService("StarterPlayer"):FindFirstChild("StarterCharacter")
assert(character, "StarterCharacter missing after save")
local report = { motors = {}, parts = {}, clothing = {} }
for _, d in character:GetDescendants() do
  if d:IsA("Motor6D") then report.motors[d.Name] = d.Part0.Name .. " -> " .. d.Part1.Name end
  if d:IsA("Weld") then report.clothing[d.Part1.Name] = d.Part0.Name end
end
for _, child in character:GetChildren() do
  if child:IsA("BasePart") then report.parts[child.Name] = tostring(child.Size) end
end
local humanoid = character:FindFirstChildOfClass("Humanoid")
report.rigType = humanoid and humanoid.RigType.Name
report.face = character.Head:FindFirstChild("face") ~= nil
local outfits = game:GetService("ReplicatedStorage"):FindFirstChild("CharacterOutfits")
report.outfits = outfits and #outfits:GetChildren() or 0
report.loadCharacterAppearance = game:GetService("StarterPlayer").LoadCharacterAppearance
return HttpService:JSONEncode(report)
'''


def install_script(m, ids):
    data = {
        "models": {name: ids["models"][name]["id"] for name in mesh_files(m)},
        "images": {key: ids["images"][key]["image"] for key in image_files(m)},
        "parts": {name: {"size": info["size"]} for name, info in m["parts"].items()},
        "clothing": {name: {"size": info["size"], "part": info["part"], "offset": info["offset"]}
                     for name, info in m["clothing"].items()},
        "motors": m["motors"],
        "colors": m["colors"],
        "defaultPants": next(iter(m["colors"]["tribes"])),
    }
    return INSTALL.replace("%DATA%", lua_value(data))


def show(task):
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
    for flag in ("--check", "--upload", "--install", "--probe"):
        mode.add_argument(flag, action="store_true")
    args = parser.parse_args()
    m = manifest()
    ids = load_ids()
    if args.check:
        problems = check(m, ids)
        for problem in problems:
            print("PROBLEM: " + problem)
        print(f"{len(ids['models'])}/{len(mesh_files(m))} meshes and "
              f"{len(ids['images'])}/{len(image_files(m))} images recorded")
        return 1 if problems else 0
    if args.upload:
        problems = check(m, ids)
        if problems:
            raise ValueError("; ".join(problems))
        upload(m, ids)
        return 0
    problems = check(m, ids, need_ids=True)
    if problems:
        raise ValueError("; ".join(problems[:8]))
    cloud = PlaceCloud()
    if args.probe:
        show(cloud.task(PROBE))
        return 0
    show(cloud.task(install_script(m, ids)))
    show(cloud.task(VERIFY))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError, KeyError) as error:
        print("SAFE STOP: " + str(error), file=sys.stderr)
        sys.exit(1)
