"""Export one world-kit .blend (built by build_kit.py) for Roblox.

    BLENDER_ARGS="art/blender/assets/kit/W01.blend" \
        art/blender/run.sh scripts/export_kit_roblox.py art/roblox/kit/W01/manifest.json
    BLENDER_ARGS="art/blender/assets/kit/wip/W01_boulder.blend" \
        art/blender/run.sh scripts/export_kit_roblox.py art/roblox/kit/wip/W01_boulder/manifest.json

Optional: `--out <dir>` after the .blend writes somewhere else (tests).
`--sheet W01` exports only that sheet's assets from the combined
assets/kit/FlintbornWorldKit.blend (modelled live through the Blender MCP),
into art/roblox/kit/W01/.
FB_RETINT=1 recomputes the palette layout instead of pinning the previous one.

Writes, for a full sheet art/roblox/kit/<SHEET>/, for a wip file
(assets/kit/wip/<SHEET>_<module>.blend) art/roblox/kit/wip/<SHEET>_<module>/:

- meshes/<Asset>.glb, <Asset>_water_<key>.glb, <Asset>_glow_<key>.glb (and _01,
  _02 ... when a piece is cut over MAX_TRIS). One asset is one mesh object; it is
  split by what a Roblox MeshPart can render: palette-textured faces ("solid"),
  see-through water, one piece per water key ("water"), and one Neon part per
  bright emissive colour ("glow"). Each piece is recentred on its bounding box.
- palette.png: a CELL x CELL cell per (palette colour, Tint level), only for the
  colours these assets use. Each row is one colour and holds that colour's own
  Tint levels, so faces keep their flat colour and hand-painted brightness
  variation; UVs point at cell centres. Colours come from each material's
  `flintkit_hex` (PALETTE, KIT_PALETTE or a module's extra palette alike).
- water/<key>.png: a 512 x 512 tileable stylised water texture per water key
  (the key's colour with lighter caustic lines and a few foam specks, painted
  with numpy on a torus so it wraps seamlessly). Water faces are the keys
  flintkit.is_water_key() accepts (water / water_deep / water_shallow or any key
  containing "water"). Their UVs are a box projection in studs from the asset
  origin, one tile per WATER_TILE studs (top faces: u = x / 16, v = y / 16 in
  Blender, i.e. u = X / 16, v = Z / 16 mod 1 in Roblox/glTF), so the texture runs
  on seamlessly across pieces and across assets placed on a 16-stud grid.
- manifest.json: per asset its size, tris, collision fields and pieces (offset
  of each piece's centre from the asset origin, which is the bottom centre of
  the footprint), and its VFX sockets (beam sockets with `end`, `axis` and
  `normal` in Roblox axes, `end` relative to the socket). Water pieces carry
  `texture`, `transparency` (0.3 deep, 0.5 shallow, 0.4 otherwise, or the
  material's `kit_transparency`), `material` SmoothPlastic, no collision and no
  shadow, and `flow` (direction and speed) when the asset has a water_flow socket.

Re-exports keep the previous palette layout (rows and levels stay where they
were, new ones are appended), so editing one asset does not move every other
asset's UVs and force a re-upload of all its meshes. Colours no longer used keep
their row, marked "used": false, until FB_RETINT=1 compacts the layout.

Axes: Blender is Z up with fronts facing -Y; glTF and Roblox are Y up. A point
(x, y, z) becomes (x, z, -y), so an asset's front faces Roblox +Z.
The object's rotation and scale are baked into the mesh; its location is not.
"""

import bisect
import json
import math
import os
import re
import shutil
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER_DIR = os.path.dirname(HERE)
ART = os.path.dirname(BLENDER_DIR)
REPO = os.path.dirname(ART)
OUT_ROOT = os.path.join(ART, "roblox", "kit")
sys.path.insert(0, os.path.join(BLENDER_DIR, "lib"))
import flintkit  # noqa: E402  (the shared water rule: is_water_key, water_transparency)
import kitwater  # noqa: E402  (the water texture, shared with the Blender preview)

MAX_TRIS = 10000      # Roblox caps a mesh at ~20k triangles
CELL = 16             # pixels per palette cell
COLUMNS = 32          # tint levels per colour row (fixed, so the width never changes)
TINT_EPS = 0.002      # tints closer than this share a level (8-bit sRGB step is ~0.004)
GLOW_EMISSION = 1.0   # emission at or above this renders as a Neon part (fire, lava)
WATER = {"water", "water_deep", "water_shallow"}
WATER_KEY = re.compile(r"[a-z]\d+_water(_[a-z0-9_]+)?")  # sheet-prefixed module water keys
WATER_TRANSPARENCY = 0.25  # the lobby's flat water (roblox_lobby_map.py); kit water uses flintkit.water_transparency
WATER_TILE = kitwater.TILE_STUDS  # studs per water texture tile (16)
WATER_TEX = kitwater.SIZE         # water texture size in pixels (512)
# SmoothPlastic, not Glass: Glass tints and reflects the sky, so the stylised
# texture colours wash out; it hides transparent things behind it (beams,
# particles, other water), which would hide a waterfall's Beam seen through its
# pool; and it looks different at each graphics quality level. SmoothPlastic with
# Transparency shows the texture exactly, the same on every device.
WATER_MATERIAL = "SmoothPlastic"

COLLISION = {
    "box": {"CollisionFidelity": "Box", "CanCollide": True, "CanQuery": True, "CanTouch": True},
    "hull": {"CollisionFidelity": "Hull", "CanCollide": True, "CanQuery": True, "CanTouch": True},
    "precise": {"CollisionFidelity": "PreciseConvexDecomposition", "CanCollide": True, "CanQuery": True,
                "CanTouch": True},
    # Box fidelity too: with collisions off it is only the cheapest geometry to keep.
    "none": {"CollisionFidelity": "Box", "CanCollide": False, "CanQuery": False, "CanTouch": False},
}
# Water and glow pieces never collide, whatever the asset's profile (as in the lobby).
NO_COLLIDE = {"CollisionFidelity": "Box", "CanCollide": False, "CanQuery": False, "CanTouch": False,
              "CastShadow": False}


def to_rbx(v):
    return (v[0], v[2], -v[1])


def r(x, n=4):
    return round(float(x), n) + 0.0  # + 0.0 turns -0.0 into 0.0


def srgb(c):
    c = max(0.0, c)
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_linear(h):
    h = h.lstrip("#")
    return [linear(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)]


def safe(name):
    return "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in name)


def rel(path):
    """Repo-relative path, or the absolute one for a file outside the repo."""
    try:
        path = os.path.relpath(path, REPO) if os.path.commonpath([path, REPO]) == REPO else path
    except ValueError:  # another drive
        pass
    return path.replace("\\", "/")


# --- Arguments and output location ----------------------------------------------

def parse_args():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    blend, out, only_sheet = None, None, None
    i = 0
    while i < len(args):
        if args[i] == "--out":
            out = args[i + 1]
            i += 1
        elif args[i] == "--sheet":  # one sheet out of the combined FlintbornWorldKit.blend
            only_sheet = args[i + 1]
            i += 1
        else:
            blend = args[i]
        i += 1
    assert blend, "usage: BLENDER_ARGS=\"<kit .blend> [--out <dir>]\" run.sh scripts/export_kit_roblox.py <manifest>"
    blend = os.path.abspath(blend if os.path.isabs(blend) or os.path.exists(blend) else os.path.join(REPO, blend))
    assert os.path.isfile(blend), f"no such .blend: {blend}"
    name = os.path.splitext(os.path.basename(blend))[0]
    wip = os.path.basename(os.path.dirname(blend)) == "wip"
    if wip:
        sheet, _, module = name.partition("_")
        default_out = os.path.join(OUT_ROOT, "wip", name)
    elif only_sheet:
        sheet, module = only_sheet, None
        default_out = os.path.join(OUT_ROOT, only_sheet)
    else:
        sheet, module = name, None
        default_out = os.path.join(OUT_ROOT, name)
    parse_args.only_sheet = only_sheet
    return blend, sheet, module or None, os.path.abspath(out) if out else default_out


# --- Materials -------------------------------------------------------------------

class Colour:
    """One palette colour, read back from a flintkit material."""

    def __init__(self, mat):
        self.key = mat["flintkit_key"]
        self.hex = mat["flintkit_hex"].upper()
        spec = list(mat.get("flintkit_spec", [0.9, 0.0, 0.0]))
        self.emission = float(spec[2]) if len(spec) > 2 else 0.0
        self.emissive = self.emission > 0  # the material ignores Tint
        self.glow = self.emission >= GLOW_EMISSION
        self.water = (self.key in WATER or bool(WATER_KEY.fullmatch(self.key))
                      or flintkit.is_water_key(self.key))
        self.transparency = flintkit.water_transparency(self.key, mat) if self.water else None


def colours_of(mesh, colours, problems, owner):
    out = []
    for mat in mesh.materials:
        if mat is None or "flintkit_key" not in mat or "flintkit_hex" not in mat:
            problems.append(f"{owner}: material {mat.name if mat else None} is not a flintkit palette material, "
                            f"its faces are skipped")
            out.append(None)
            continue
        c = Colour(mat)
        known = colours.get(c.key)
        if known and known.hex != c.hex:
            problems.append(f"{owner}: palette key {c.key} is {c.hex} here but {known.hex} elsewhere")
        colours.setdefault(c.key, c)
        out.append(colours[c.key])
    return out


# --- Geometry --------------------------------------------------------------------

def triangles(obj, depsgraph, colours, problems):
    """The asset's triangles as (points, key, tint, kind) in its local frame with
    the object's rotation and scale applied; kind is solid, water:<key> or glow:<key>."""
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    slots = colours_of(mesh, colours, problems, obj.name)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    basis = obj.matrix_world.to_3x3()
    if basis.determinant() < 0:
        problems.append(f"{obj.name}: negative scale, faces come out inside-out")
    bmesh.ops.transform(bm, matrix=basis.to_4x4(), verts=bm.verts)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    loop_tint = bm.loops.layers.float_color.get("Tint")
    vert_tint = None if loop_tint else bm.verts.layers.float_color.get("Tint")
    if loop_tint is None and vert_tint is None:
        problems.append(f"{obj.name}: no Tint attribute, every face exports at tint 1.0")
    tris = []
    skipped = 0
    for face in bm.faces:
        c = slots[face.material_index] if face.material_index < len(slots) else None
        if c is None:
            skipped += 1
            continue
        if c.emissive:
            tint = 1.0
        elif loop_tint:
            tint = sum(loop[loop_tint][0] for loop in face.loops) / 3
        elif vert_tint:
            tint = sum(loop.vert[vert_tint][0] for loop in face.loops) / 3
        else:
            tint = 1.0
        kind = "water:" + c.key if c.water else ("glow:" + c.key if c.glow else "solid")
        tris.append(([tuple(l.vert.co) for l in face.loops], c.key, tint, kind))
    bm.free()
    evaluated.to_mesh_clear()
    if skipped:
        problems.append(f"{obj.name}: {skipped} faces without a palette material skipped")
    return tris


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


def rbx_size(lo, hi):
    d = hi - lo
    return [r(max(d.x, 0.01)), r(max(d.z, 0.01)), r(max(d.y, 0.01))]


# --- Palette ---------------------------------------------------------------------

def clusters(values):
    """Distinct tint levels: values within TINT_EPS of a cluster's first value
    join it; each level is its cluster's mean."""
    out, group = [], []
    for v in sorted(values):
        if group and v - group[0] > TINT_EPS:
            out.append(sum(group) / len(group))
            group = []
        group.append(v)
    if group:
        out.append(sum(group) / len(group))
    return out


def fit_levels(values):
    """At most COLUMNS levels for one colour: the clusters, or their quantiles
    when there are more (most tints sit near 1.0, so quantiles keep the subtle
    variation that evenly spaced levels would flatten). A quantised row is
    always full, so a pinned re-export maps its tints to the nearest level
    instead of appending to it."""
    levels = clusters(values)
    if len(levels) <= COLUMNS:
        return [r(v, 5) for v in levels]
    values = sorted(values)
    return [r(values[min(len(values) - 1, round(i * (len(values) - 1) / (COLUMNS - 1)))], 5)
            for i in range(COLUMNS)]


def nearest(levels, tint):
    return min(range(len(levels)), key=lambda i: abs(levels[i] - tint))


def palette_layout(used, colours, previous, problems):
    """Rows [{key, hex, levels, used}] for the tints each key uses; keeps the
    previous layout's rows and levels in place when there is one."""
    rows = []
    if previous and not os.environ.get("FB_RETINT"):
        for row in previous:
            key = row["key"]
            if key not in used:
                rows.append({"key": key, "hex": row["hex"], "levels": list(row["levels"]), "used": False})
                continue
            levels = list(row["levels"])
            # New tints fill the row's free cells, farthest from an existing level first;
            # once it is full they take the nearest level, so no existing UV moves.
            fresh = [v for v in used[key] if min(abs(v - l) for l in levels) > TINT_EPS]
            extra = sorted(clusters(fresh), key=lambda v: -min(abs(v - l) for l in levels))
            levels += [r(v, 5) for v in extra[:COLUMNS - len(levels)]]
            worst = max(min(abs(v - l) for l in levels) for v in used[key])
            if worst > 0.05:
                problems.append(f"palette: {key} row is full, a tint lands {worst:.3f} from its level "
                                f"(FB_RETINT=1 recomputes the layout)")
            rows.append({"key": key, "hex": colours[key].hex, "levels": levels, "used": True})
    have = {row["key"] for row in rows}
    for key in sorted(k for k in used if k not in have):
        rows.append({"key": key, "hex": colours[key].hex, "levels": fit_levels(used[key]), "used": True})
    return rows


def write_palette(path, rows):
    width = COLUMNS * CELL
    height = max(CELL, 1 << math.ceil(math.log2(len(rows) * CELL)))
    px = np.zeros((height, width, 4), dtype=np.float32)
    px[..., 3] = 1.0
    for index, row in enumerate(rows):
        base = hex_linear(row["hex"])
        # Blender images start at the bottom row; row 0 sits at the top.
        y1 = height - index * CELL
        for col in range(COLUMNS):
            tint = row["levels"][min(col, len(row["levels"]) - 1)]  # spare cells repeat the last level
            px[y1 - CELL:y1, col * CELL:(col + 1) * CELL, :3] = [srgb(min(1.0, c * tint)) for c in base]
    image = bpy.data.images.new("KitPalette", width, height, alpha=False)
    image.colorspace_settings.name = "Non-Color"  # values above are already sRGB
    image.pixels.foreach_set(px.ravel())
    image.filepath_raw = path
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)
    return width, height


def cell_uv(row, col, height):
    return (col + 0.5) / COLUMNS, 1.0 - (row + 0.5) * CELL / height


# --- Water -------------------------------------------------------------------------

def water_uvs(points):
    """Box projection in studs, one tile per WATER_TILE: faces that face up or down
    take (x, y), faces toward +-Y take (x, z), faces toward +-X take (y, z). Points
    are asset-local (before a piece is recentred), so tiles line up across pieces
    and across assets placed on a WATER_TILE grid."""
    a, b, c = (Vector(p) for p in points)
    n = (b - a).cross(c - a)
    ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
    if az >= ax and az >= ay:
        pick = (0, 1)
    elif ay >= ax:
        pick = (0, 2)
    else:
        pick = (1, 2)
    return [(p[pick[0]] / WATER_TILE, p[pick[1]] / WATER_TILE) for p in points]


def water_texture(hexcol, seed, size=WATER_TEX):
    """Tileable stylised water (sRGB floats, size x size x 3, top row first); the
    painter lives in lib/kitwater.py, shared with the Blender preview."""
    return kitwater.pixels(hexcol, seed=seed, size=size)


def write_water_texture(path, hexcol, key):
    kitwater.write_png(path, hexcol, key)


# --- Export ----------------------------------------------------------------------

def export_piece(path, tris, uv_of, scene, loop_uvs=None):
    """Write one piece as a .glb. UVs come from uv_of(key, tint) per face, or with
    `loop_uvs` from loop_uvs(points) per corner (asset-local points)."""
    lo, hi = bounds(tris)
    centre = (lo + hi) / 2
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    verts = {}
    for points, key, tint, _ in tris:
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
        if loop_uvs is not None:
            for loop, co in zip(face.loops, loop_uvs(points)):
                loop[uv].uv = co
            continue
        u, v = uv_of(key, tint)
        for loop in face.loops:
            loop[uv].uv = (u, v)
    name = os.path.splitext(os.path.basename(path))[0]
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=True, export_yup=True, export_apply=False,
        export_texcoords=True, export_normals=True, export_materials="NONE", export_animations=False,
        export_skins=False, export_morph=False, export_cameras=False, export_lights=False, export_extras=False,
    )
    count = len(mesh.polygons)
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    return count, lo, hi, centre


def sockets(obj):
    out = []
    origin = obj.matrix_world.translation
    for s in sorted(obj.children_recursive, key=lambda o: o.name):
        if not s.get("vfx_kind"):
            continue
        try:
            spec = json.loads(s.get("roblox", "{}"))
        except ValueError:
            spec = {}
        scale = float(s.get("vfx_scale", 1.0)) * (sum(s.matrix_world.to_scale()) / 3)
        entry = {"name": s.name, "kind": s["vfx_kind"],
                 "position": [r(c) for c in to_rbx(s.matrix_world.translation - origin)],
                 "vfx_scale": r(scale), "trigger": spec.get("trigger"), "spec": spec}
        if spec.get("beams"):
            entry.update(beam_ends(obj, s, spec))
        out.append(entry)
    return out


def beam_ends(obj, s, spec):
    """A beam socket's end point (relative to the socket) and attachment axes, in
    Roblox axes, with the asset's rotation applied like the mesh's."""
    tip = next((c for c in s.children if c.get("vfx_end_of")), None)
    basis = obj.matrix_world.to_3x3().normalized()
    if tip is not None:
        end = tip.matrix_world.translation - s.matrix_world.translation
    elif s.get("vfx_end") is not None:
        end = obj.matrix_world @ Vector(s["vfx_end"]) - s.matrix_world.translation
    else:
        end = None
    out = {"end": [r(c) for c in to_rbx(end)] if end is not None else spec.get("end")}
    for key in ("axis", "normal"):
        local = s.get("vfx_" + key)
        out[key] = ([r(c) for c in to_rbx((basis @ Vector(local)).normalized())] if local is not None
                    else spec.get(key))
    return out


def flow_of(entries_vfx):
    """Water flow from the asset's first water_flow socket: unit direction in
    Roblox X/Z and speed in studs/s (the beam's texture_speed)."""
    for v in entries_vfx:
        if v["kind"] != "water_flow" or not v.get("end"):
            continue
        dx, dz = v["end"][0], v["end"][2]
        length = math.hypot(dx, dz)
        if length < 1e-6:
            continue
        beam = (v["spec"].get("beams") or [{}])[0]
        return {"direction": [r(dx / length), 0.0, r(dz / length)],
                "speed": r(float(beam.get("texture_speed", 0.0))),
                "socket": v["name"]}
    return None


def main():
    blend, sheet, module, out = parse_args()
    bpy.ops.wm.open_mainfile(filepath=blend)
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    problems = []
    only = getattr(parse_args, "only_sheet", None)
    assets = sorted((o for o in scene.objects if o.type == "MESH" and o.get("kit_role")
                     and (not only or o.get("kit_sheet") == only)), key=lambda o: o.name)
    for o in scene.objects:
        if o.type == "MESH" and not o.get("kit_role") and not o.name.startswith(("FB_", "REF_")):
            problems.append(f"{o.name}: mesh without kit_role, not exported")
        o.select_set(False)
    assert assets, f"no kit assets (mesh objects with kit_role) in {blend}"

    previous = None
    try:
        with open(os.path.join(out, "manifest.json"), encoding="utf-8") as f:
            prev = json.load(f)["palette"]
        if prev.get("columns") == COLUMNS and prev.get("cell") == CELL:
            previous = prev["rows"]
    except (OSError, KeyError, ValueError):
        pass

    # Gather every asset's triangles first: the palette needs every tint in use.
    colours, gathered, used = {}, [], {}
    for obj in assets:
        tris = triangles(obj, depsgraph, colours, problems)
        if not tris:
            problems.append(f"{obj.name}: no exportable faces")
            continue
        gathered.append((obj, obj.name, tris))
        for _, key, tint, _ in tris:
            used.setdefault(key, []).append(tint)

    # Free the asset names, so each exported mesh is named exactly like its file
    # (otherwise Blender calls the piece "StubRock.001" inside the .glb).
    for obj in assets:
        obj.name = obj.name + "__src"
        if obj.data.users == 1:
            obj.data.name = obj.name

    rows = palette_layout(used, colours, previous, problems)
    row_of = {row["key"]: i for i, row in enumerate(rows)}
    mesh_dir = os.path.join(out, "meshes")
    if os.path.isdir(mesh_dir):
        shutil.rmtree(mesh_dir)
    os.makedirs(mesh_dir)
    width, height = write_palette(os.path.join(out, "palette.png"), rows)
    water_dir = os.path.join(out, "water")
    if os.path.isdir(water_dir):
        shutil.rmtree(water_dir)
    water_keys = sorted({t[3][6:] for _, _, tris in gathered for t in tris if t[3].startswith("water:")})
    if water_keys:
        os.makedirs(water_dir)
    for key in water_keys:
        write_water_texture(os.path.join(water_dir, safe(key) + ".png"), colours[key].hex, key)

    def uv_of(key, tint):
        row = row_of[key]
        return cell_uv(row, nearest(rows[row]["levels"], tint), height)

    files = set()
    entries = []
    for obj, asset, tris in gathered:
        groups = {}
        for t in tris:
            groups.setdefault(t[3], []).append(t)
        pieces = []
        vfx = sockets(obj)
        flow = flow_of(vfx)
        order = sorted(groups, key=lambda k: (k != "solid", k))
        for kind in order:
            chunks = split(groups[kind])
            water = kind.startswith("water:")
            for index, chunk in enumerate(chunks):
                suffix = "" if kind == "solid" else "_" + kind.replace(":", "_")
                suffix += "" if len(chunks) == 1 else "_%02d" % (index + 1)
                name = safe(asset + suffix)
                while name.lower() in files:
                    name += "_"
                files.add(name.lower())
                count, lo, hi, centre = export_piece(os.path.join(mesh_dir, name + ".glb"), chunk, uv_of, scene,
                                                     loop_uvs=water_uvs if water else None)
                piece = {"file": "meshes/" + name + ".glb", "kind": kind.split(":")[0], "tris": count,
                         "offset": [r(c) for c in to_rbx(centre)], "size": rbx_size(lo, hi)}
                if kind.startswith("glow:"):
                    piece["key"] = kind[5:]
                    piece["color"] = colours[kind[5:]].hex
                    piece["material"] = "Neon"
                    piece["collision"] = NO_COLLIDE
                elif water:
                    c = colours[kind[6:]]
                    piece["key"] = c.key
                    piece["color"] = c.hex
                    piece["texture"] = "water/" + safe(c.key) + ".png"
                    piece["tile_studs"] = WATER_TILE
                    piece["transparency"] = r(c.transparency, 3)
                    piece["material"] = WATER_MATERIAL
                    piece["cast_shadow"] = False
                    piece["collision"] = NO_COLLIDE
                    if flow:
                        piece["flow"] = flow
                pieces.append(piece)
        lo, hi = bounds(tris)
        total = sum(p["tris"] for p in pieces)
        if obj.get("tris") is not None and int(obj["tris"]) != total:
            problems.append(f"{asset}: exported {total} tris, the .blend records {obj['tris']}")
        if abs(lo.z) > 0.02:
            problems.append(f"{asset}: lowest point at z={lo.z:.3f}, the origin is not at the bottom")
        collision = obj.get("kit_collision", "hull")
        if collision not in COLLISION:
            problems.append(f"{asset}: unknown kit_collision {collision!r}, using hull")
            collision = "hull"
        entry = {"name": asset,"sheet": obj.get("kit_sheet", sheet), "subject": obj.get("kit_subject"),
                 "role": obj.get("kit_role"), "size": rbx_size(lo, hi), "tris": total,
                 "budget": int(obj.get("kit_budget", 0)) or None,
                 "collision": dict(COLLISION[collision], profile=collision),
                 "pieces": pieces, "vfx": vfx}
        if obj.get("kit_notes"):
            entry["notes"] = obj["kit_notes"]
        entries.append(entry)

    pieces = [p for a in entries for p in a["pieces"]]
    kinds = {k: sum(1 for p in pieces if p["kind"] == k) for k in ("solid", "water", "glow")}
    stats = {"assets": len(entries), "pieces": len(pieces), "solid": kinds["solid"], "water": kinds["water"],
             "glow": kinds["glow"], "tris": sum(p["tris"] for p in pieces),
             "vfxSockets": sum(len(a["vfx"]) for a in entries),
             "paletteColours": sum(1 for row in rows if row["used"]),
             "paletteLevels": sum(len(row["levels"]) for row in rows if row["used"]),
             "meshBytes": sum(os.path.getsize(os.path.join(out, p["file"])) for p in pieces)}
    manifest = {
        "version": 1,
        "source": rel(blend),
        "sheet": sheet,
        "module": module,
        "units": "1 stud = 1 Blender unit. Sizes and offsets are in studs; set each MeshPart's Size from 'size'.",
        "axes": "Roblox axes (Y up). Blender (x, y, z) -> Roblox (x, z, -y); an asset's front (Blender -Y) faces "
                "Roblox +Z. The asset origin is the bottom centre of its footprint: a piece's MeshPart sits at "
                "origin CFrame * CFrame.new(offset); VFX positions are relative to the same origin.",
        "palette": {
            "file": "palette.png", "width": width, "height": height, "cell": CELL, "columns": COLUMNS,
            "uv": "row i, level j: u = (j + 0.5) / columns, v = 1 - (i + 0.5) * cell / height "
                  "(v up from the bottom of the image); a row's spare cells repeat its last level",
            "rows": rows,
        },
        "water": {
            "keys": {k: {"hex": colours[k].hex, "texture": "water/" + safe(k) + ".png",
                         "transparency": r(colours[k].transparency, 3)} for k in water_keys},
            "material": WATER_MATERIAL,
            "tile_studs": WATER_TILE,
            "uv": "Water pieces carry their own UVs (not palette cells): a box projection in studs from the asset "
                  "origin, one texture tile per tile_studs. Up-facing faces: u = X / tile, v = Z / tile (mod 1, "
                  "Roblox axes); faces toward +-Z use (X, -Y), toward +-X use (-Z, -Y). Set MeshPart.TextureID to the "
                  "uploaded texture (it wraps), Transparency from the piece, Material SmoothPlastic, CastShadow "
                  "false. Assets placed on a tile_studs grid continue the pattern seamlessly.",
            "flow": "Pieces of an asset with a water_flow socket carry flow = {direction (unit, Roblox X/Z), speed "
                    "(studs/s), socket}. To animate, use a Texture (Face Top, StudsPerTileU/V = tile_studs) on the "
                    "piece instead of TextureID and move OffsetStudsU/V along direction * speed each frame.",
        },
        "assets": entries,
        "stats": stats,
        "problems": problems,
    }
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=1)
    for p in problems:
        print(f"KITEXPORT PROBLEM {p}")
    print(f"KITEXPORT {rel(out)}")
    print(f"STATS {sheet}{'/' + module if module else ''}: {stats['assets']} assets, {stats['pieces']} pieces "
          f"({stats['solid']} solid, {stats['water']} water, {stats['glow']} glow), {stats['tris']} tris, "
          f"{stats['vfxSockets']} vfx sockets, palette {stats['paletteColours']} colours / "
          f"{stats['paletteLevels']} levels ({width}x{height}), {len(problems)} problems")


main()
