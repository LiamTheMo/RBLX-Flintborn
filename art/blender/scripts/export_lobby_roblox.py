"""Export the lobby map (lobby/FlintbornLobby.blend) for Roblox, built for fast loads.

Writes art/roblox/lobby/:

- meshes/<Part>.glb  one file per UNIQUE mesh piece. The lobby places 2,400+
  objects, but only ~150 different meshes, so Roblox downloads each shape once
  and the place clones it (scripts/roblox_lobby_map.py).
- palette.png        one small texture shared by every mesh: a cell per palette
  colour and Tint level, so faces keep their flat colour and hand-painted
  brightness variation with no per-asset textures.
- manifest.json      every placement (Roblox CFrame and Size), its collision
  profile, the VFX sockets (ParticleEmitter + PointLight specs), the arrival
  spawn and the NPC spots.

Each mesh is split by what Roblox needs to render it: textured faces ("solid"),
see-through water ("water"), and one Neon part per fire colour ("glow"), since a
MeshPart has a single material. Pieces over MAX_TRIS triangles are cut into
chunks (Roblox caps a mesh at ~20k). Each piece is recentred on its bounding box
so the MeshPart's centre is known exactly, and the placement sets Size, which
also makes the import's unit conversion irrelevant.

Axes: Blender is Z up with fronts facing -Y; glTF and Roblox are Y up. A point
(x, y, z) becomes (x, z, -y) in both, so a mesh's local frame and a placement
convert with the same matrix C.

Run through the wrapper:

    art/blender/run.sh scripts/export_lobby_roblox.py ../roblox/lobby/manifest.json
"""

import bisect
import json
import math
import os
import shutil
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER_DIR = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(BLENDER_DIR, "lib"))
import flintkit  # noqa: E402

LOBBY = os.path.join(BLENDER_DIR, "lobby", "FlintbornLobby.blend")
OUT = os.path.join(os.path.dirname(BLENDER_DIR), "roblox", "lobby")
MESH_DIR = os.path.join(OUT, "meshes")

MAX_TRIS = 10000
SKIP_COLLECTIONS = {"VFX Preview", "NPC Placeholders"}
WATER = {"water", "water_deep", "water_shallow"}
# Emissive keys bright enough to read as fire: Neon parts. Fainter glows (rune
# engravings) stay in the texture.
GLOW = {k for k, v in flintkit.PALETTE.items() if v[3] >= 1.0}
PALETTE_KEYS = list(flintkit.PALETTE)
TINT_LEVELS = 32
CELL = 16

# Collision and render profiles (applied by scripts/roblox_lobby_map.py).
PLANTS = {"FernLeafy", "GrassTuftLarge", "GrassClumpSmall", "WildflowerWhite", "BroadLeafHerb",
          "ShrubLowWide", "ShrubTallDense", "BerryBush", "Ground_GrassTufts", "Ground_Pebbles"}
TREES = {"BroadleafTreeStout", "BroadleafTreeTall", "BroadleafTreeWideOld", "BroadleafTreeLeaning",
         "PineTreeShortWide", "PineTreeTallNarrow", "PineTreeMature", "PineTreeYoung"}
WALKABLE = {"Ground_Plateau", "Ground_Lowland", "Ground_DirtPlazaPaths", "Ground_GateFlagstones",
            "Terrain_RimSkirt", "Forge_StoneStairs", "ForestFloor", "CliffSection", "CliffOuterCorner",
            "CliffInnerCorner", "RockShelfTwoLevels", "EarthSwitchback", "GrassRamp", "RockArch", "Riverbank",
            "WaterfallCliff", "FootbridgeSmall", "VaultHall_RedRug", "EldersTotem_StelaFootings"}
STRUCTURES = {"VaultHall", "AncestralForge", "DeployGate", "ThatchMarketStall", "HideMarketStall",
              "WatchtowerTall", "WatchtowerRoofed", "PalisadeSection", "PalisadeSectionLow", "PalisadeMainPost",
              "PalisadeMainPostBanner", "PalisadeMainPostTorch", "LogRailFence", "EldersTotemTall"}

C = Matrix(((1, 0, 0), (0, 0, 1), (0, -1, 0)))  # Blender -> Roblox/glTF axes


def to_rbx(v):
    return (v[0], v[2], -v[1])


def r(x, n=4):
    return round(float(x), n)


def srgb(c):
    c = max(0.0, c)
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def palette_key(material):
    name = material.name if material else ""
    return name[3:] if name.startswith("FB_") else None


# --- Palette texture -----------------------------------------------------------

def tint_levels(objects):
    """TINT_LEVELS brightness levels at the quantiles of every Tint value in use.

    Most tints sit within a few percent of 1.0 while a few special faces go far
    darker or brighter, so evenly spaced levels would flatten the subtle
    variation; quantiles keep it."""
    values = []
    for me in {o.data for o in objects}:
        attr = me.color_attributes.get("Tint")
        if attr:
            values.extend(d.color[0] for d in attr.data)
    if not values:
        return [1.0] * TINT_LEVELS
    values.sort()
    return [values[min(len(values) - 1, round(i * (len(values) - 1) / (TINT_LEVELS - 1)))]
            for i in range(TINT_LEVELS)]


def write_palette(path, levels):
    width = TINT_LEVELS * CELL
    rows = len(PALETTE_KEYS)
    height = 1 << math.ceil(math.log2(rows * CELL))
    pixels = [0.0] * (width * height * 4)
    for row, key in enumerate(PALETTE_KEYS):
        base = flintkit.hex_rgb(flintkit.PALETTE[key][0])
        for col in range(TINT_LEVELS):
            tint = 1.0 if key in flintkit.EMISSIVE else levels[col]
            rgb = [srgb(min(1.0, c * tint)) for c in base]
            # Blender images start at the bottom row; row 0 sits at the top.
            y0 = height - (row + 1) * CELL
            for y in range(y0, y0 + CELL):
                for x in range(col * CELL, (col + 1) * CELL):
                    i = (y * width + x) * 4
                    pixels[i:i + 4] = (*rgb, 1.0)
    image = bpy.data.images.new("LobbyPalette", width, height, alpha=False)
    image.colorspace_settings.name = "Non-Color"  # values above are already sRGB
    image.pixels[:] = pixels
    image.filepath_raw = path
    image.file_format = "PNG"
    image.save()
    return width, height


def cell_uv(key, tint, levels, height):
    row = PALETTE_KEYS.index(key)
    col = min(TINT_LEVELS - 1, bisect.bisect_left(levels, tint))
    if col > 0 and abs(levels[col - 1] - tint) <= abs(levels[col] - tint):
        col -= 1
    u = (col + 0.5) / TINT_LEVELS
    v = 1.0 - (row + 0.5) * CELL / height
    return u, v


# --- Mesh pieces ----------------------------------------------------------------

def face_groups(mesh):
    """Triangles grouped by render kind: {"solid": [...], "water": [...], "glow:<key>": [...]}."""
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    tint = bm.loops.layers.float_color.get("Tint")
    groups = {}
    for face in bm.faces:
        mat = mesh.materials[face.material_index] if face.material_index < len(mesh.materials) else None
        key = palette_key(mat)
        if key is None or key not in flintkit.PALETTE:
            continue  # preview-only materials
        value = sum(loop[tint][0] for loop in face.loops) / 3 if tint else 1.0
        kind = "water" if key in WATER else ("glow:" + key if key in GLOW else "solid")
        groups.setdefault(kind, []).append(([tuple(l.vert.co) for l in face.loops], key, value))
    bm.free()
    return groups


def split(tris):
    if len(tris) <= MAX_TRIS:
        return [tris]
    lo = [min(p[i] for t in tris for p in t[0]) for i in range(3)]
    hi = [max(p[i] for t in tris for p in t[0]) for i in range(3)]
    axis = max((0, 1), key=lambda i: hi[i] - lo[i])
    ordered = sorted(tris, key=lambda t: sum(p[axis] for p in t[0]))
    half = len(ordered) // 2
    return split(ordered[:half]) + split(ordered[half:])


def bounds(tris):
    lo = Vector([min(p[i] for t in tris for p in t[0]) for i in range(3)])
    hi = Vector([max(p[i] for t in tris for p in t[0]) for i in range(3)])
    return lo, hi


def export_piece(name, tris, levels, height, scene):
    lo, hi = bounds(tris)
    centre = (lo + hi) / 2
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    verts = {}
    for points, key, tint in tris:
        face_verts = []
        for p in points:
            q = (round(p[0] - centre.x, 5), round(p[1] - centre.y, 5), round(p[2] - centre.z, 5))
            if q not in verts:
                verts[q] = bm.verts.new(q)
            face_verts.append(verts[q])
        if len(set(face_verts)) < 3:
            continue
        try:
            face = bm.faces.new(face_verts)
        except ValueError:
            face = bm.faces.new([bm.verts.new(v.co) for v in face_verts])  # duplicate face: own verts
        face.smooth = False
        u, v = cell_uv(key, tint, levels, height)
        for loop in face.loops:
            loop[uv].uv = (u, v)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    path = os.path.join(MESH_DIR, name + ".glb")
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=True, export_yup=True, export_apply=False,
        export_texcoords=True, export_normals=True, export_materials="NONE", export_animations=False,
        export_skins=False, export_morph=False, export_cameras=False, export_lights=False, export_extras=False,
    )
    scene.collection.objects.unlink(obj)
    triangles = len(mesh.polygons)
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    dims = hi - lo
    return {"file": "meshes/" + name + ".glb", "tris": triangles,
            "size": [r(max(dims.x, 0.01)), r(max(dims.z, 0.01)), r(max(dims.y, 0.01))]}, centre


def safe(name):
    return "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in name)


# --- Placements -----------------------------------------------------------------

def cframe(matrix, local_centre):
    loc, rot, scale = matrix.decompose()
    position = to_rbx(matrix @ local_centre)
    rr = C @ rot.to_matrix() @ C.transposed()
    return [r(position[0]), r(position[1]), r(position[2])] + [r(rr[i][j], 6) for i in range(3) for j in range(3)], scale


def profile(asset, collection, kind, reachable, size):
    if kind == "water":
        return "water"
    if kind.startswith("glow"):
        return "glow"
    if asset in PLANTS or max(size) < 1.2:
        return "decor"
    if asset in TREES:
        return "tree" if reachable else "scenery"
    if asset in WALKABLE or asset.startswith("Ground_"):
        return "ground"
    if not reachable and collection in ("Forest", "Terrain", "River"):
        return "scenery"
    if asset in STRUCTURES:
        return "structure"
    return "prop"


def main():
    bpy.ops.wm.open_mainfile(filepath=LOBBY)
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    objects = [o for o in scene.objects if o.type == "MESH" and not o.hide_render
               and not (o.users_collection and o.users_collection[0].name in SKIP_COLLECTIONS)]

    if os.path.isdir(MESH_DIR):
        shutil.rmtree(MESH_DIR)
    os.makedirs(MESH_DIR)
    levels = tint_levels(objects)
    _, height = write_palette(os.path.join(OUT, "palette.png"), levels)

    # The palisade's footprint decides what players can reach.
    wall = [o.matrix_world.translation for o in objects
            if o.users_collection and o.users_collection[0].name == "Palisade"
            and o.data.name.startswith("Palisade")]
    wx = (min(p.x for p in wall), max(p.x for p in wall))
    wy = (min(p.y for p in wall), max(p.y for p in wall))
    cx, cy = (wx[0] + wx[1]) / 2, (wy[0] + wy[1]) / 2
    rx, ry = (wx[1] - wx[0]) / 2 + 6, (wy[1] - wy[0]) / 2 + 6

    def reachable(p):
        return ((p.x - cx) / rx) ** 2 + ((p.y - cy) / ry) ** 2 <= 1

    # Pieces export from this scene with only the piece selected.
    export = scene
    for o in scene.objects:
        o.select_set(False)
    parts = {}
    pieces_of = {}  # mesh key -> [(part name, local centre, kind)]
    instances = []
    colliders = []
    for obj in objects:
        mesh = obj.data
        key = (mesh.library.name if mesh.library else "", mesh.name)
        asset = mesh.name
        if key not in pieces_of:
            evaluated = obj.evaluated_get(depsgraph).to_mesh()
            pieces = []
            for kind, tris in sorted(face_groups(evaluated).items()):
                chunks = split(tris)
                for index, chunk in enumerate(chunks):
                    suffix = "" if kind == "solid" else "_" + kind.replace(":", "_")
                    suffix += "" if len(chunks) == 1 else "_%02d" % (index + 1)
                    name = safe(asset + suffix)
                    while name in parts:
                        name += "_"
                    info, centre = export_piece(name, chunk, levels, height, export)
                    info["kind"] = "water" if kind == "water" else ("glow" if kind != "solid" else "solid")
                    if kind.startswith("glow:"):
                        info["color"] = flintkit.PALETTE[kind[5:]][0]
                    parts[name] = info
                    pieces.append((name, centre, info["kind"]))
            obj.evaluated_get(depsgraph).to_mesh_clear()
            pieces_of[key] = pieces
        collection = obj.users_collection[0].name if obj.users_collection else ""
        here = reachable(obj.matrix_world.translation)
        for name, centre, kind in pieces_of[key]:
            cf, scale = cframe(obj.matrix_world, centre)
            base = parts[name]["size"]
            size = [r(base[0] * abs(scale.x)), r(base[1] * abs(scale.z)), r(base[2] * abs(scale.y))]
            prof = profile(asset, collection, kind, here, size)
            instances.append([name, cf, size, prof])
        if asset in TREES and here:
            # Trees in reach collide on an invisible trunk box, not the canopy.
            lo, hi = Vector(obj.bound_box[0]), Vector(obj.bound_box[6])
            s = obj.matrix_world.to_scale()
            width = max(1.2, 0.12 * min(hi.x - lo.x, hi.y - lo.y) * s.x)
            tall = min(10.0, (hi.z - lo.z) * s.z * 0.45)
            cf, _ = cframe(obj.matrix_world, Vector((0, 0, tall / (2 * s.z))))
            colliders.append([cf, [r(width), r(tall), r(width)]])

    vfx, kinds, npcs = [], {}, []
    for o in scene.objects:
        if o.type != "EMPTY":
            continue
        p = o.matrix_world.translation
        if o.get("vfx_kind"):
            kind = o["vfx_kind"]
            kinds.setdefault(kind, json.loads(o["roblox"]))
            scale = float(o.get("vfx_scale", 1.0)) * (sum(o.matrix_world.to_scale()) / 3)
            vfx.append([kind, [r(c) for c in to_rbx(p)], r(scale)])
        elif o.get("npc_role"):
            yaw = o.matrix_world.to_euler().z
            npcs.append({"role": o["npc_role"], "position": [r(c) for c in to_rbx(p)], "yaw": r(math.degrees(yaw), 2)})

    # Arrival spawn: on top of the arrival rune stone (or the plaza edge if absent).
    stone = scene.objects.get("ArrivalStones_LargeRuneStone")
    if stone:
        top = max((stone.matrix_world @ Vector(c)).z for c in stone.bound_box)
        spawn = to_rbx(Vector((stone.matrix_world.translation.x, stone.matrix_world.translation.y, top)))
    else:
        spawn = (0.0, 2.0, 30.0)
    gate = scene.objects.get("DeployGate")

    manifest = {
        "version": 1,
        "source": "art/blender/lobby/FlintbornLobby.blend",
        "palette": {"file": "palette.png", "tintLevels": [r(t) for t in levels]},
        "parts": parts,
        "instances": instances,
        "colliders": colliders,
        "vfxKinds": kinds,
        "vfx": vfx,
        "spawn": [r(c) for c in spawn],
        "deployGate": [r(c) for c in to_rbx(gate.matrix_world.translation)] if gate else None,
        "npcSpots": npcs,
        "stats": {
            "uniqueParts": len(parts),
            "uniqueTris": sum(p["tris"] for p in parts.values()),
            "placedParts": len(instances),
            "placedTris": sum(parts[i[0]]["tris"] for i in instances),
            "colliders": len(colliders),
            "meshBytes": sum(os.path.getsize(os.path.join(OUT, p["file"])) for p in parts.values()),
        },
    }
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, separators=(",", ":"))
    print("LOBBY EXPORT", json.dumps(manifest["stats"]))
    profiles = {}
    for item in instances:
        profiles[item[3]] = profiles.get(item[3], 0) + 1
    print("PROFILES", json.dumps(profiles))


main()
