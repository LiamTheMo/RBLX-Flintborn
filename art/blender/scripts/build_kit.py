"""Build world-kit sheets (art/reference/kit) from one module per subject row.

    BLENDER_ARGS="W01" art/blender/run.sh scripts/build_kit.py art/blender/assets/kit/W01.blend
    BLENDER_ARGS="W01 --only boulder" art/blender/run.sh scripts/build_kit.py \
        art/blender/assets/kit/wip/W01_boulder.blend

Each subject (one row of a reference sheet) is a module
`scripts/kit/<SHEET>/<module>.py` that defines:

    SUBJECT = "Boulder"   # the sheet's row label, PascalCase
    ROW = 1               # 1-4, which row of the sheet it is
    PALETTE = {}          # optional extra colours, keys prefixed "<sheet>_" (lower case)
    def build(kit): ...   # build every asset of the row and return the objects

and tags every object it returns with `kit.tag(obj, role, ...)`. Roles:
hero (the assembled model), variant (the VARIATIONS column), part (the PARTS
column, each piece a reusable asset), depleted and drop (resource sheets).

The runner checks each asset (role tagged, origin at the bottom centre, palette
materials only, triangle budget), files it in a collection per sheet and
subject, saves the .blend, then renders, per subject, a strip laid out like the
reference row (hero, front, side, top, parts, then variants or drops and
depleted) and a compare image with the reference row above it:

    renders/kit/<SHEET>/<module>_row.png, <module>_compare.png, <module>_cells/
    assets/kit/<SHEET>.blend + <SHEET>_stats.json   (full sheet)
    assets/kit/wip/<SHEET>_<module>.blend + _stats.json   (--only)

`--no-render` skips the renders. FB_ONLY=Name,Name limits which assets are kept.
"""

import glob
import importlib.util
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER_DIR = os.path.dirname(HERE)
ART = os.path.dirname(BLENDER_DIR)
sys.path.insert(0, os.path.join(BLENDER_DIR, "lib"))
import flintkit  # noqa: E402
import vfx  # noqa: E402

KIT_DIR = os.path.join(HERE, "kit")
REF_DIR = os.path.join(ART, "reference", "kit")
# KIT_ASSET_DIR / KIT_RENDER_DIR redirect output, e.g. to test the runner away from live work
ASSET_DIR = os.environ.get("KIT_ASSET_DIR") or os.path.join(BLENDER_DIR, "assets", "kit")
RENDER_DIR = os.environ.get("KIT_RENDER_DIR") or os.path.join(BLENDER_DIR, "renders", "kit")

ROLES = ("hero", "variant", "part", "depleted", "drop")
# Default triangle budgets per role; a module may pass budget= for big pieces
# (cliffs, buildings, large trees: up to 8000). Roblox caps a mesh at ~20k.
BUDGET = {"hero": 3000, "variant": 3000, "part": 1500, "depleted": 2000, "drop": 300}
COLLISIONS = ("box", "hull", "precise", "none")
CELL = (320, 240)
SAMPLES = 48   # 16 left soft shadows speckled


class Kit:
    """What a module's build() gets: the libraries, the sheet id and `tag`."""

    flintkit = flintkit
    vfx = vfx

    def __init__(self, sheet, module):
        self.sheet = sheet
        self.module = module
        self.subject = module.SUBJECT

    def tag(self, obj, role, collision="hull", budget=None, notes=""):
        """Record what an asset is for. collision: box (simple block), hull
        (convex, the default), precise (walkable or hollow shapes: arches,
        stairs, ledges) or none (small scatter players walk through)."""
        assert role in ROLES, f"{obj.name}: role {role!r} not in {ROLES}"
        assert collision in COLLISIONS, f"{obj.name}: collision {collision!r} not in {COLLISIONS}"
        obj["kit_sheet"] = self.sheet
        obj["kit_subject"] = self.subject
        obj["kit_role"] = role
        obj["kit_collision"] = collision
        obj["kit_budget"] = int(budget or BUDGET[role])
        if notes:
            obj["kit_notes"] = notes
        if obj.asset_data is not None:
            for t in (self.sheet, self.subject, role):
                if t not in [x.name for x in obj.asset_data.tags]:
                    obj.asset_data.tags.new(t)
        return obj


def parse_args():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    sheet, only, render = None, None, True
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--only":
            only = args[i + 1]
            i += 1
        elif a == "--no-render":
            render = False
        else:
            sheet = a
        i += 1
    assert sheet, "usage: build_kit.py <SHEET> [--only module] [--no-render]"
    return sheet, only, render


def load_modules(sheet, only):
    paths = sorted(glob.glob(os.path.join(KIT_DIR, sheet, "*.py")))
    paths = [p for p in paths if not os.path.basename(p).startswith("_")]
    if only:
        paths = [p for p in paths if os.path.splitext(os.path.basename(p))[0] == only]
        assert paths, f"no module {only!r} in {os.path.join(KIT_DIR, sheet)}"
    mods = []
    for p in paths:
        name = f"kit_{sheet}_{os.path.splitext(os.path.basename(p))[0]}"
        spec = importlib.util.spec_from_file_location(name, p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.MODULE = os.path.splitext(os.path.basename(p))[0]
        mods.append(mod)
    return sorted(mods, key=lambda m: getattr(m, "ROW", 9))


KEY_DIR = Vector((-0.45, -0.55, 0.7)).normalized()  # a typical sun: above, front-left
SHADE_LIMIT = 0.5
# Real material regions that sit on top faces by nature (cut post tops, lashings,
# cloth, straw): not painted lighting, so left out of the shading check.
REGION_KEYS = {"wood_end", "rope", "rope_dark", "bone", "parchment", "cloth_cream", "cloth_red",
               "thatch", "thatch_dark", "foam", "ink"}


def _hsv(hexcol):
    import colorsys
    h = hexcol.lstrip("#")
    return colorsys.rgb_to_hsv(*(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))


def _same_family(a, b):
    """Two palette colours are shades of one material when both are near-grey,
    or their hues and saturations are close (e.g. kit_rock vs kit_rock_dark)."""
    (h1, s1, _), (h2, s2, _) = a, b
    if s1 < 0.18 and s2 < 0.18:
        return True
    dh = min(abs(h1 - h2), 1 - abs(h1 - h2)) * 360
    return dh < 22 and abs(s1 - s2) < 0.3


def baked_shading(obj):
    """How strongly an asset paints lighting into its colours: the weighted
    correlation, within each family of shades of one material, between a face's
    colour brightness (palette value x Tint) and how much it faces up or toward
    the sun. Lighting in Roblox shades faces by their normals, so colours that
    already follow the normals get shaded twice. Returns (worst corr, family)."""
    me = obj.data
    if not me.polygons:
        return 0.0, None
    tint = me.color_attributes.get("Tint")
    keys = [m.get("flintkit_hex", "#808080") if m else "#808080" for m in me.materials] or ["#808080"]
    hsv = [_hsv(k) for k in keys]
    fam = []
    for i, c in enumerate(hsv):  # greedy clustering of the asset's palette into material families
        fam.append(next((fam[j] for j in range(i) if _same_family(hsv[j], c)), i))
    groups = {}
    skip = {i for i, m in enumerate(me.materials)
            if m is None or m.get("flintkit_key") in REGION_KEYS or (m.get("flintkit_spec") or [0, 0, 0])[2] > 0
            or _material_class(m.get("flintkit_key") or "") == "exempt"}
    for p in me.polygons:
        mi = min(p.material_index, len(keys) - 1)
        if mi in skip:
            continue
        t = 1.0
        if tint is not None and tint.domain == "CORNER":
            t = sum(tint.data[li].color[0] for li in p.loop_indices) / len(p.loop_indices)
        n = p.normal
        groups.setdefault(fam[mi], []).append((p.area, hsv[mi][2] * t, n.z, n.dot(KEY_DIR)))
    total = sum(p.area for p in me.polygons) or 1.0
    worst, worst_fam = 0.0, None
    for f, rows in groups.items():
        area = sum(r[0] for r in rows)
        if len(rows) < 12 or area < 0.1 * total:
            continue
        w = np.array([r[0] for r in rows])
        b = np.array([r[1] for r in rows])
        mb = np.average(b, weights=w)
        sb = math.sqrt(np.average((b - mb) ** 2, weights=w))
        if sb / max(mb, 1e-4) < 0.06:  # one flat colour: nothing baked
            continue
        for col in (2, 3):
            x = np.array([r[col] for r in rows])
            mx = np.average(x, weights=w)
            sx = math.sqrt(np.average((x - mx) ** 2, weights=w))
            if sx < 1e-4:
                continue
            corr = float(np.average((b - mb) * (x - mx), weights=w) / (sb * sx))
            if corr > worst:
                worst, worst_fam = corr, me.materials[next(i for i, v in enumerate(fam) if v == f)].get("flintkit_key")
    return worst, worst_fam


TINT_LIMIT = 1.25  # brightest / darkest Tint within one material (about +/-10%)


SHADE_WORDS = {"light", "dark", "lit", "shadow", "shade", "shaded", "deep", "cool", "warm", "pale", "mid",
               "highlight", "tip", "top", "side", "under", "lo", "hi"}
# Material classes by key word, most specific first. Two colours of one class
# that look alike are one material in different light.
MATERIAL_CLASSES = [
    ("exempt", ("water", "foam", "flower", "petal", "berry", "glow", "ember", "fire", "rune")),
    ("cutwood", ("heartwood", "wood_end", "ring", "hollow", "cut")),
    ("patina", ("patina", "verdigris")),
    ("copper", ("copper", "_cu_", "cu_")), ("coal", ("coal",)), ("flint", ("flint",)),
    ("limestone", ("limestone",)), ("moss", ("moss",)), ("grass", ("grass",)),
    ("foliage", ("leaf", "bush", "foliage", "needle", "canopy", "frond", "fern", "olive", "crown", "clump")),
    ("wood", ("bark", "wood", "trunk", "log", "branch", "root", "stump", "plank", "beam", "post")),
    ("ground", ("sand", "soil", "earth", "dirt", "path", "ground", "bed", "mud", "seam")),
    ("rock", ("rock", "stone", "boulder", "cliff", "slab", "pebble", "spire", "ledge", "connector")),
]


def _material_class(key):
    k = key.lower()
    for cls, words in MATERIAL_CLASSES:
        if any(w in k for w in words):
            return cls
    return "other:" + k


def _stem(key):
    parts = [p for p in key.lower().split("_") if p not in SHADE_WORDS]
    return "_".join(parts)


def shade_pairs(obj):
    """Pairs of the asset's colours that are one material in different light (a
    lit and a shadow shade), by either sign: the keys differ only by a shade word
    (rock / rock_cool, needle / needle_tip), or they are the same kind of
    material (MATERIAL_CLASSES) with a similar colour (same hue or both near-grey,
    brightness within 2x). Different materials (moss vs leaf, coal vs stone,
    copper vs patina, flowers, water) are not flagged."""
    keys = []
    for m in obj.data.materials:
        if m is None or m.get("flintkit_key") in REGION_KEYS or (m.get("flintkit_spec") or [0, 0, 0])[2] > 0:
            continue
        k = m.get("flintkit_key")
        cls = _material_class(k)
        if cls == "exempt":
            continue
        keys.append((k, cls, _hsv(m.get("flintkit_hex", "#808080"))))
    pairs = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            (ka, ca, (ha, sa, va)), (kb, cb, (hb, sb, vb)) = keys[i], keys[j]
            if _stem(ka) == _stem(kb):
                pairs.append(f"{ka}+{kb}")
                continue
            if ca != cb or ca.startswith("other:"):
                continue
            grey = sa < 0.2 and sb < 0.2
            dh = min(abs(ha - hb), 1 - abs(ha - hb)) * 360
            same_hue = grey or (sa >= 0.2 and sb >= 0.2 and dh < 28 and abs(sa - sb) < 0.35)
            if same_hue and min(va, vb) / max(va, vb, 1e-4) >= 0.5:
                pairs.append(f"{ka}+{kb}")
    return pairs


def tint_spread(obj):
    """Worst brightest/darkest Tint ratio within one material of the asset."""
    me = obj.data
    tint = me.color_attributes.get("Tint")
    if tint is None or tint.domain != "CORNER":
        return 1.0
    lo, hi = {}, {}
    for p in me.polygons:
        t = sum(tint.data[li].color[0] for li in p.loop_indices) / len(p.loop_indices)
        lo[p.material_index] = min(lo.get(p.material_index, 9), t)
        hi[p.material_index] = max(hi.get(p.material_index, 0), t)
    return max((hi[k] / max(lo[k], 1e-3) for k in lo), default=1.0)


def check(obj, problems):
    """Validate one built asset; returns its stats row."""
    me = obj.data
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    obj["tris"] = tris
    zs = [v.co.z for v in me.vertices]
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    role = obj.get("kit_role")
    if role is None:
        problems.append(f"{obj.name}: not tagged with kit.tag()")
    if not obj.name[:1].isupper() or not obj.name.replace("_", "").isalnum():
        problems.append(f"{obj.name}: name must be PascalCase")
    if zs and abs(min(zs)) > 0.02:
        problems.append(f"{obj.name}: lowest point at z={min(zs):.3f}, origin must be at the bottom")
    if xs and (abs(min(xs) + max(xs)) > 0.1 or abs(min(ys) + max(ys)) > 0.1):
        problems.append(f"{obj.name}: origin is not centred on the footprint")
    for m in me.materials:
        if m is None or "flintkit_key" not in m:
            problems.append(f"{obj.name}: material {m.name if m else None} is not a flintkit palette material")
    shade, shade_fam = baked_shading(obj)
    obj["kit_baked_shading"] = round(shade, 2)
    if shade > SHADE_LIMIT and not obj.get("kit_shading_ok"):
        problems.append(
            f"{obj.name}: lighting is painted into the colours ({shade_fam} shades follow face direction, "
            f"corr {shade:.2f} > {SHADE_LIMIT}). The reference's light tops and dark sides come from LIGHTING, "
            f"not paint: give each material ONE base colour and let geometry + Roblox lighting shade it. Keep "
            f"Tint variation small and random, never by face direction. A real material change (snow on top, "
            f"wet base) may set obj['kit_shading_ok'] = 'reason'.")
    # Several related shades of a material and per-face Tint variation are allowed (the owner wants
    # proper colouring and texture); both are only recorded for reference.
    pairs = shade_pairs(obj)
    obj["kit_shade_pairs"] = ", ".join(pairs)
    waived = obj.get("kit_two_tone_ok")
    spread = tint_spread(obj)
    obj["kit_tint_spread"] = round(spread, 2)
    if role == "drop":  # drops tumble under physics, so every side is seen: no holes
        uses = {}
        for p in me.polygons:
            for k in p.edge_keys:
                uses[k] = uses.get(k, 0) + 1
        open_edges = sum(1 for n in uses.values() if n == 1)
        if open_edges:
            problems.append(f"{obj.name}: drop mesh has {open_edges} open edges; close it (keep the bottom face)")
    budget = int(obj.get("kit_budget", BUDGET.get(role, 3000)))
    over = tris > budget
    d = obj.dimensions
    row = {"name": obj.name, "subject": obj.get("kit_subject"), "role": role, "tris": tris,
           "budget": budget, "studs": [round(d.x, 2), round(d.y, 2), round(d.z, 2)],
           "collision": obj.get("kit_collision"), "materials": [m.get("flintkit_key") for m in me.materials if m],
           "vfx": [s["vfx_kind"] for s in vfx.sockets(obj)], "baked_shading": round(shade, 2),
           "shade_pairs": pairs, "two_tone_ok": waived or "", "tint_spread": round(spread, 2),
           "notes": obj.get("kit_notes", "")}
    flag = "OVER BUDGET" if over else "ok"
    print(f"KITSTAT {obj.name:28s} {str(role):8s} {tris:6d}/{budget:<6d} "
          f"{d.x:6.1f} x {d.y:5.1f} x {d.z:5.1f}  {flag}")
    if over:
        problems.append(f"{obj.name}: {tris} tris OVER BUDGET {budget}")
    return row


def file_into(obj, coll):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    for s in vfx.sockets(obj):
        for e in [s] + list(s.children_recursive):  # beam sockets carry a <socket>_End Empty
            for c in list(e.users_collection):
                c.objects.unlink(e)
            coll.objects.link(e)


def collections(sheet, subject):
    root = bpy.data.collections.get("Kit") or bpy.data.collections.new("Kit")
    if root.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(root)
    sname = f"{sheet} {sheet_title(sheet)}"
    sc = bpy.data.collections.get(sname) or bpy.data.collections.new(sname)
    if sc.name not in root.children:
        root.children.link(sc)
    cname = f"{sheet} {subject}"
    cc = bpy.data.collections.get(cname) or bpy.data.collections.new(cname)
    if cc.name not in sc.children:
        sc.children.link(cc)
    return cc


def sheet_file(sheet):
    hits = glob.glob(os.path.join(REF_DIR, sheet + "_*.png"))
    assert hits, f"no reference sheet {sheet}_*.png in {REF_DIR}"
    return hits[0]


def sheet_title(sheet):
    base = os.path.splitext(os.path.basename(sheet_file(sheet)))[0]
    return base[len(sheet) + 1:].replace("_", " ").title()


ORDER = {"hero": 0, "variant": 1, "part": 2, "depleted": 3, "drop": 4}


def layout(groups, gap=3.0):
    """One subject per row (toward +Y going down the sheet), assets along +X."""
    y = 0.0
    for objs in groups:
        x = 0.0
        depth = 0.0
        for o in objs:
            o.location = (x + o.dimensions.x / 2, y, 0)
            x += o.dimensions.x + gap
            depth = max(depth, o.dimensions.y)
        y -= depth + gap * 3


# -- rendering -------------------------------------------------------------------


FILL = 0.88  # the subject fills this much of the cell's tighter side, like the sheet's crops
PAPER_HEX = "#F2EEE6"  # the reference sheets' paper
# Lighting tuned so flat, unshaded palette colours read like the sheets: a strong
# warm sun and modest sky ambient. Shading must come from this, never from paint.
KEY_ENERGY = float(os.environ.get("KIT_KEY", 4.5))
AMBIENT = float(os.environ.get("KIT_AMBIENT", 0.45))
FILL_ENERGY = float(os.environ.get("KIT_FILL", 2.5))   # rear fill sun (flintkit's FB_Fill was 0.8, shadowed)
AMBIENT_HEX = os.environ.get("KIT_AMBIENT_HEX", "#D2D0CC")
KIT_LOOK = os.environ.get("KIT_LOOK", "Medium High Contrast")
GROUND_ALBEDO = float(os.environ.get("KIT_GROUND", 0.68))  # lit floor ~ the paper, so only the shadow reads
BG_SCALE = (0.84, 0.80, 0.75)  # camera-ray background vs paper per channel, measured to match the lit floor


def kit_studio(scene):
    """flintkit's studio, but on the reference sheets' warm paper instead of grey."""
    flintkit._studio(scene)
    # Standard view washes saturated greens and cyans out against the sheets; a contrast look
    # brings water and foliage close to the reference without painting colours darker.
    scene.view_settings.look = KIT_LOOK
    nt = scene.world.node_tree
    for n in nt.nodes:
        if n.type == "BACKGROUND" and n.inputs["Strength"].default_value == 1.0:
            # the camera-ray background, dimmed so the contrast look renders it the same cream as the lit
            # floor (at full paper colour it blows out to a white band above the horizon in low views)
            n.inputs["Color"].default_value = (*(c * k for c, k in zip(flintkit.hex_rgb(PAPER_HEX), BG_SCALE)), 1)
        elif n.type == "BACKGROUND":  # the ambient that lights the asset: lower, so the sun models the facets
            n.inputs["Strength"].default_value = AMBIENT
            # neutral, like Roblox's grey ambient: the old blue-grey sky washed greens pale and bluish
            n.inputs["Color"].default_value = (*flintkit.hex_rgb(AMBIENT_HEX), 1)
    key = bpy.data.objects.get("FB_Key")
    if key:
        key.data.energy = KEY_ENERGY
        key.data.color = flintkit.hex_rgb("#FFF7EC")  # slightly warm sun, as on the sheets
    fill = bpy.data.objects.get("FB_Fill")
    if fill:
        # the sheets light their rear and side views too: a shadowless fill from behind brings those views to the
        # sheet's values (a 011 rear: #98857F against the sheet's #988580) without touching the front-lit views
        fill.data.energy = FILL_ENERGY
        fill.data.use_shadow = False
    gm = bpy.data.materials.get("FB_GroundMat")
    if gm:
        gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (
            *(c * GROUND_ALBEDO for c in flintkit.hex_rgb(PAPER_HEX)), 1)


def frame_box(corners, azimuth, elevation):
    """Aim the camera from (azimuth, elevation), then move it in or out and shift
    the lens until the projected corners fill FILL of the frame, centred."""
    from bpy_extras.object_utils import world_to_camera_view

    scene = bpy.context.scene
    cam = bpy.data.objects["FB_Cam"]
    cam.data.shift_x = cam.data.shift_y = 0.0
    centre = sum(corners, Vector()) / len(corners)
    radius = max(max((c - centre).length for c in corners), 0.05)
    az, el = math.radians(azimuth), math.radians(elevation)
    if elevation >= 80:  # straight down, front (-Y) at the bottom of the frame
        direction = Vector((0, 0, 1))
        cam.rotation_euler = (0, 0, 0)
    else:
        direction = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
        cam.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    aspect = scene.render.resolution_x / scene.render.resolution_y
    dist = radius * 3.0
    for _ in range(4):
        cam.location = centre + direction * dist
        bpy.context.view_layer.update()
        pts = [world_to_camera_view(scene, cam, c) for c in corners]
        xs, ys = [p.x for p in pts], [p.y for p in pts]
        w, h = max(xs) - min(xs), max(ys) - min(ys)
        # frame units: x spans 1 (the wide side), y spans 1 of the shorter side
        need = max(w, h) / FILL
        dist *= max(need, 1e-3) ** 0.9
    cam.location = centre + direction * dist
    bpy.context.view_layer.update()
    pts = [world_to_camera_view(scene, cam, c) for c in corners]
    xs, ys = [p.x for p in pts], [p.y for p in pts]
    # lens shift is in units of the wider side
    cam.data.shift_x = ((min(xs) + max(xs)) / 2 - 0.5)
    cam.data.shift_y = ((min(ys) + max(ys)) / 2 - 0.5) / aspect
    bpy.data.objects["FB_Ground"].location = (centre.x, centre.y, min(c.z for c in corners))


def render_group(objs, path, azimuth=flintkit.DEFAULT_AZIMUTH, elevation=flintkit.DEFAULT_ELEVATION):
    scene = bpy.context.scene
    kit_studio(scene)
    scene.render.resolution_x, scene.render.resolution_y = CELL
    scene.render.resolution_percentage = 100
    try:
        scene.eevee.taa_render_samples = SAMPLES
    except AttributeError:
        pass
    keep = set(o.name for o in objs)
    for o in objs:
        for s in vfx.sockets(o):
            keep.add(s.name)
            for p in s.children_recursive:
                keep.add(p.name)
    saved = {}
    for o in scene.objects:
        if o.type in ("MESH", "LIGHT") and o.name not in keep and not o.name.startswith("FB_"):
            saved[o.name] = o.hide_render
            o.hide_render = True
    # frame on the real vertices (bounding-box corners overshoot the silhouette and leave the subject small)
    corners = []
    for o in objs:
        if o.type == "MESH" and len(o.data.vertices):
            vs = o.data.vertices
            step = max(1, len(vs) // 4000)
            corners += [o.matrix_world @ vs[i].co for i in range(0, len(vs), step)]
        else:
            corners += [o.matrix_world @ Vector(c) for c in o.bound_box]
    frame_box(corners, azimuth, elevation)
    scene.render.filepath = path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    for n, h in saved.items():
        bpy.data.objects[n].hide_render = h
    return path


def load_px(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(img)
    return px  # bottom-up, as Blender stores it


def save_px(px, path):
    h, w = px.shape[:2]
    img = bpy.data.images.new("kit_tile", w, h, alpha=True)
    img.pixels = np.ascontiguousarray(px).ravel()
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def paper(h, w):
    px = np.ones((h, w, 4), dtype=np.float32)
    px[..., :3] = [int(PAPER_HEX[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return px


def hstack(paths):
    imgs = [load_px(p) for p in paths]
    h = max(i.shape[0] for i in imgs)
    out = paper(h, sum(i.shape[1] for i in imgs))
    x = 0
    for i in imgs:
        out[h - i.shape[0]:, x:x + i.shape[1]] = i
        x += i.shape[1]
    return out


def vstack(blocks):
    """Stack bottom-up pixel blocks top-to-bottom in the given order."""
    w = max(b.shape[1] for b in blocks)
    out = paper(sum(b.shape[0] for b in blocks), w)
    y = out.shape[0]
    for b in blocks:
        y -= b.shape[0]
        out[y:y + b.shape[0], :b.shape[1]] = b
    return out


def grid_parts(parts, gap=0.8):
    """Pack parts into a compact grid (largest first, rows about as wide as the
    biggest part x 2) for the parts cell, so small pieces are not lost beside a
    big one. Returns the original locations to restore after the render."""
    if len(parts) < 3:
        return {}
    orig = {o: o.location.copy() for o in parts}
    # first rows sit at the back: tallest first, so short flat parts in front stay visible
    items = sorted(parts, key=lambda o: (round(o.dimensions.z, 1), o.dimensions.x * o.dimensions.y), reverse=True)
    area = sum(o.dimensions.x * o.dimensions.y for o in items)
    row_w = max(items[0].dimensions.x * 1.6, math.sqrt(area) * 1.4)
    gap = max(gap, row_w * 0.08)  # keep pieces visibly apart at any scale
    base = orig[items[0]]
    x = y = 0.0
    depth = 0.0
    for o in items:
        if x > 0 and x + o.dimensions.x > row_w:
            x, y = 0.0, y + depth + gap
            depth = 0.0
        # later rows step toward the camera (-Y), so smaller pieces sit in front of the big one
        o.location = (base.x + x + o.dimensions.x / 2, base.y - y - o.dimensions.y / 2, 0)
        x += o.dimensions.x + gap
        depth = max(depth, o.dimensions.y)
    bpy.context.view_layer.update()
    return orig


def render_subject(sheet, mod, objs):
    """Strip laid out like the reference row, and a compare image above/below."""
    out = os.path.join(RENDER_DIR, sheet)
    cells = os.path.join(out, f"{mod.MODULE}_cells")
    by = {r: [o for o in objs if o.get("kit_role") == r] for r in ROLES}
    hero = by["hero"][:1] or objs[:1]
    # A module may match the sheet's camera: HERO_AZIMUTH (hero and variants, degrees,
    # default front-left -22) and SIDE_AZIMUTH (90 = right side; ~135 = rear three-quarter
    # for sheets whose SIDE/REAR cell shows the back).
    haz = getattr(mod, "HERO_AZIMUTH", flintkit.DEFAULT_AZIMUTH)
    hel = getattr(mod, "HERO_ELEVATION", flintkit.DEFAULT_ELEVATION)  # e.g. 32 for terrain drawn from higher
    saz = getattr(mod, "SIDE_AZIMUTH", 90)
    shots = [("1_hero", hero, haz, hel),
             ("2_front", hero, 0, 6), ("3_side", hero, saz, 6 if saz in (90, -90) else 18),
             ("4_top", hero, 0, 89)]
    if by["part"]:
        shots.append(("5_parts", by["part"], flintkit.DEFAULT_AZIMUTH, 24))
    for i, o in enumerate(by["variant"]):
        shots.append((f"6_variant{i + 1}_{o.name}", [o], haz, hel))
    if by["drop"]:
        shots.append(("7_drops", by["drop"], flintkit.DEFAULT_AZIMUTH, 28))
    for o in by["depleted"]:
        shots.append((f"8_depleted_{o.name}", [o], flintkit.DEFAULT_AZIMUTH, flintkit.DEFAULT_ELEVATION))
    paths = []
    for n, g, az, el in shots:
        moved = grid_parts(g) if n == "5_parts" else {}
        paths.append(render_group(g, os.path.join(cells, f"{n}.png"), az, el))
        for o, loc in moved.items():
            o.location = loc
        if moved:
            bpy.context.view_layer.update()
    strip = hstack(paths)
    row_path = os.path.join(out, f"{mod.MODULE}_row.png")
    save_px(strip, row_path)
    ref = os.path.join(REF_DIR, "rows", f"{sheet}_row{getattr(mod, 'ROW', 1)}.png")
    if os.path.exists(ref):
        save_px(vstack([load_px(ref), strip]), os.path.join(out, f"{mod.MODULE}_compare.png"))
    print(f"KITRENDER {row_path}")
    return row_path


def main():
    sheet, only, render = parse_args()
    flintkit.reset_file()
    mods = load_modules(sheet, only)
    keep = {n for n in os.environ.get("FB_ONLY", "").split(",") if n}
    problems, stats, groups = [], [], []
    for mod in mods:
        flintkit.KIT_PALETTE.update(getattr(mod, "PALETTE", {}))
        for k in getattr(mod, "PALETTE", {}):
            if not k.startswith(sheet.lower() + "_"):
                problems.append(f"{mod.MODULE}: extra palette key {k!r} must start with {sheet.lower()}_")
        objs = [o for o in mod.build(Kit(sheet, mod)) if o is not None]
        if keep:
            objs = [o for o in objs if o.name in keep]
        names = [o.name for o in objs]
        if len(set(names)) != len(names):
            problems.append(f"{mod.MODULE}: duplicate asset names {names}")
        if not any(o.get("kit_role") == "hero" for o in objs):
            problems.append(f"{mod.MODULE}: no hero asset")
        coll = collections(sheet, mod.SUBJECT)
        objs.sort(key=lambda o: ORDER.get(o.get("kit_role"), 9))
        for o in objs:
            file_into(o, coll)
            stats.append(dict(check(o, problems), module=mod.MODULE))
        groups.append((mod, objs))
    # drop the per-category collections Asset.finish made and left empty
    for c in list(bpy.data.collections):
        if not c.objects and not c.children and c.name != "Kit":
            bpy.data.collections.remove(c)
    layout([g for _, g in groups])
    bpy.context.view_layer.update()  # matrix_world must follow the new locations before framing
    base = os.path.join(ASSET_DIR, "wip", f"{sheet}_{only}") if only else os.path.join(ASSET_DIR, sheet)
    os.makedirs(os.path.dirname(base), exist_ok=True)
    with open(base + "_stats.json", "w", encoding="utf-8") as fh:
        json.dump({"sheet": sheet, "reference": os.path.relpath(sheet_file(sheet), ART).replace("\\", "/"),
                   "assets": stats, "problems": problems}, fh, indent=2)
    flintkit.save(base + ".blend")
    if render:
        vfx.realize(bpy.context.scene)
        for mod, objs in groups:
            render_subject(sheet, mod, objs)
    total = sum(s["tris"] for s in stats)
    for p in problems:
        print(f"KITPROBLEM {p}")
    print(f"STATS {sheet}{'/' + only if only else ''}: {len(stats)} assets, {total} tris, "
          f"{len(problems)} problems")


main()
