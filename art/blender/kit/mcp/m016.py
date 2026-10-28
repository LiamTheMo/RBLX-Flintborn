"""016 Stormglass (references/016.png): one chunky faceted teal crystal "tree" - a thick upright trunk and two thick
arms, every limb ending in a flat octagonal cap - standing in a real hexagonal socket pit in a low lumpy faceted sand
mound, with a ring of grey-brown faceted rocks round the mound's foot and two more on its upper slope.

    import importlib, kit_models, m016; importlib.reload(kit_models); importlib.reload(m016); m016.build()

Parts as on the sheet's exploded view / Parts Breakdown, each built by its own function, all in one shared build
frame (studs; front -Y, +X right, ground z = 0, mound centre at the origin). The R04 kit sheet owns Stormglass /
StormglassMainBranch / StormglassSideBranch / StormglassSandBase, hence (M016_spec.md §8, main-session decision 7):
- StormglassBranch (branch): the Crystal Assembly (Main Branch). Three solid faceted tube limbs (`_limb`: 8-sided
  rings along a polyline, parallel-transported, each ring turned and scaled a little) - the trunk with a buried blunt
  root, the right arm (front-right) and the left arm (back-left) - each ending in a flat octagonal cap (bevel ring and
  a low fan centre). The arms start inside the trunk; one exact union per arm.
- StormglassSprig (sprig): the Crystal Branch (Side Branch), a short Y twig of the same limbs. Not in the hero.
- StormglassMound (mound): the Sand Base (with sockets). A low lumpy ring dome; a raised bevelled collar unioned round
  each socket, then each socket pit carved (hexagonal, chamfered rim, steep walls, flat floor); three blind hex
  pockets carved into the flat bottom.
- StormglassStone (stone A): the Base Rock (Reusable), a faceted boulder with a flat bottom. Variants B (dome),
  C (peaked dome) and D (cobble) are build-only meshes for the hero's rocks.

The hero (StormglassNode) is pasted together from the finished part meshes (m011._paste), unioned into one closed
shell, floor-cut flat at the ground, then the three underside pockets are carved. See M016_spec.md.
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M
import m011
import m012

NUM, TITLE, SHEET = 16, "Stormglass", "M016"
OFF = "m016_offset"
GLASS, GLASS_ROOT, GLASS_CAP = "m016_glass", "m016_glass_root", "m016_glass_cap"
SAND, SAND_PIT, SAND_RIM = "m016_sand", "m016_sand_pit", "m016_sand_rim"
ROCK = "m016_rock"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
UV_ANGLE = {}


def _uv(o):
    a = UV_ANGLE.get(o.name, UV["angle"])
    return dict(UV, angle=a, min_angle=a)


POLISH_LIM = 5.0

GLASS_LIGHT, GLASS_GLINT, GLASS_DEEP = "m016_glass_light", "m016_glass_glint", "m016_glass_deep"
SAND_LIGHT, SAND_DARK = "m016_sand_light", "m016_sand_dark"
ROCK_ACCENT, ROCK_DARK = "m016_rock_accent", "m016_rock_dark"
GLASS_ROUGH, SAND_ROUGH, ROCK_ROUGH = 0.3, 0.95, 0.9
GLASS_SPEC = 0.25       # Specular IOR Level on every crystal key, mix keys too (flintkit makes new keys at 0.5;
# 0.4 clipped the up-facing cap tops to white in the top and junction views)
# key -> (hex, roughness). Stage 1 placeholders were the spec §5.4 starting hexes; stage 4 calibrates them (see
# "Stage 4" in M016_spec.md and calibrate()).
PALETTE = {GLASS: ("#17B8B4", GLASS_ROUGH), GLASS_LIGHT: ("#22CFC7", GLASS_ROUGH), GLASS_GLINT: ("#4EE4E5", GLASS_ROUGH),
           GLASS_DEEP: ("#0AA9A3", GLASS_ROUGH), GLASS_ROOT: ("#3F9493", 0.5), GLASS_CAP: ("#22CFC7", GLASS_ROUGH),
           SAND: ("#C1A283", SAND_ROUGH), SAND_LIGHT: ("#C9AD8F", SAND_ROUGH), SAND_DARK: ("#B99175", SAND_ROUGH),
           SAND_PIT: ("#745842", SAND_ROUGH), SAND_RIM: ("#A5886D", SAND_ROUGH),
           ROCK: ("#6A6262", ROCK_ROUGH), ROCK_ACCENT: ("#7D716E", ROCK_ROUGH), ROCK_DARK: ("#534C4B", ROCK_ROUGH)}


def palette():
    for k, (hexcol, rough) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough)
        K.fk().material(k)
    _glass_spec()


def _glass_spec():
    """GLASS_SPEC on every crystal material, the in-between keys too."""
    for m in bpy.data.materials:
        if m.name.startswith("FB_m016_glass") and m.node_tree:
            b = m.node_tree.nodes.get("Principled BSDF")
            if b and "Specular IOR Level" in b.inputs:
                b.inputs["Specular IOR Level"].default_value = GLASS_SPEC


# calibration targets: the sheet's rendered medians (M016_spec.md §5.4), not the swatches. key -> (sRGB, kind)
TARGETS = {GLASS: ((0x20, 0xC0, 0xB7), "vivid"), GLASS_LIGHT: ((0x2C, 0xD6, 0xCC), "vivid"),
           GLASS_GLINT: ((0x5D, 0xEF, 0xE9), "vivid"), GLASS_DEEP: ((0x18, 0xAC, 0xA2), "vivid"),
           GLASS_ROOT: ((0x4E, 0x9A, 0x94), "stone"),
           SAND: ((0xDF, 0xB6, 0x8E), "stone"), SAND_LIGHT: ((0xEA, 0xC4, 0x9C), "stone"),
           SAND_DARK: ((0xD0, 0xA5, 0x7E), "stone"), SAND_PIT: ((0xA0, 0x7C, 0x5C), "stone"),
           ROCK: ((0x77, 0x6C, 0x68), "stone"), ROCK_ACCENT: ((0x8E, 0x7D, 0x76), "stone"),
           ROCK_DARK: ((0x5E, 0x54, 0x50), "stone")}


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS), as m013 / m014: non-crystal keys sampled unfiltered (the test box
    lies wholly on the dome), the crystal keys at GLASS_SPEC every round. Returns {key: (hex, rendered)}."""
    keys = keys or list(TARGETS)
    set0, sample0 = K.set_colour, K.sample

    def set_colour(key, hexcol, **kw):
        set0(key, hexcol, **kw)
        _glass_spec()

    def sample(src, box, kind="green"):
        return M.sample(src, box, "all", paper=(255, 253, 240), tol=6) if kind == "stone" else \
            sample0(src, box, kind)
    K.set_colour, K.sample = set_colour, sample
    try:
        for k in keys:
            K.fk().material(k)
        _glass_spec()
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        K.set_colour, K.sample = set0, sample0
        gone = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")
                and all(x is None or x.name.startswith("FB_m016_") for x in m.materials)]
        for m in gone:
            bpy.data.meshes.remove(m)


# ---- shared geometry helpers ---------------------------------------------------------------------------------------
def _perp(t):
    a = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
    return (a - t * a.dot(t)).normalized()


def _tangents(pts):
    out = []
    for i in range(len(pts)):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        out.append((b - a).normalized())
    return out


def _strip(bm, r0, r1):
    """Quads between two closed rings of equal length (as triangles, BEAUTY later)."""
    n = len(r0)
    out = []
    for k in range(n):
        j = (k + 1) % n
        out.append(bm.faces.new((r0[k], r0[j], r1[j], r1[k])))
    return out


def _fan(bm, ring, c, flip=False):
    out = []
    n = len(ring)
    for k in range(n):
        j = (k + 1) % n
        vs = (ring[j], ring[k], c) if not flip else (ring[k], ring[j], c)
        out.append(bm.faces.new(vs))
    return out


# ---- limbs ----------------------------------------------------------------------------------------------------------
LIMB_SIDES = 8
CAP_BEVEL = (0.22, 0.72)     # the cap's bevel ring: this far along the axis past the last ring, at this radius fraction
CAP_FAN = 0.08              # ... and the fan centre this much further (a low faceted dome on the octagon)


def _limb(a, stations, seed, start="fan", cap=True, twist=10.0, rjit=0.07, vjit=0.035, ajit=0.05, sides=LIMB_SIDES,
          key=GLASS, cap_key=GLASS_CAP, info=None, yscale=1.0):
    """One solid faceted tube limb. stations = [(point, radius)], base to end. Rings are parallel-transported along
    the polyline; each ring turned (+-twist deg) and scaled (+-rjit) a little, each vertex jittered (vjit radial,
    ajit along the axis), so the facets come out irregular and triangulated, as the sheet's. start: "fan" closes the
    first ring with a centre fan pushed back along the axis (an arm root buried in the trunk), ("point", tip) tapers to
    a tip vertex. cap: the end gets the flat octagonal cap (a bevel ring and a low fan centre). Returns verts."""
    rng = random.Random(seed)
    bm = a.bm
    pts = [Vector(p) for p, _ in stations]
    rad = [r for _, r in stations]
    tans = _tangents(pts)
    n0 = _perp(tans[0])
    frames = [n0]
    for i in range(1, len(pts)):
        q = tans[i - 1].rotation_difference(tans[i])
        n = q @ frames[-1]
        frames.append((n - tans[i] * n.dot(tans[i])).normalized())
    rings = []
    phase = rng.uniform(0, 2 * math.pi)
    for i, (p, r, t, n) in enumerate(zip(pts, rad, tans, frames)):
        b = t.cross(n)
        tw = phase + math.radians(rng.uniform(-twist, twist))
        sc = 1.0 + rng.uniform(-rjit, rjit)
        ring = []
        for k in range(sides):
            th = tw + 2 * math.pi * k / sides
            rr = r * sc * (1.0 + rng.uniform(-vjit, vjit))
            ax = rng.uniform(-ajit, ajit) if 0 < i < len(pts) - 1 else 0.0
            off = (n * math.cos(th) + b * math.sin(th)) * rr
            off.y *= yscale
            ring.append(bm.verts.new(p + off + t * ax))
        rings.append((ring, tw, n, b))
    verts = [v for r in rings for v in r[0]]
    faces = []
    for (r0, *_), (r1, *_) in zip(rings, rings[1:]):
        faces += _strip(bm, r0, r1)
    # base
    if start == "fan":
        c = bm.verts.new(pts[0] - tans[0] * 0.15)
        faces += _fan(bm, rings[0][0], c, flip=True)
        verts.append(c)
    else:
        tip = bm.verts.new(Vector(start[1]))
        faces += _fan(bm, rings[0][0], tip, flip=True)
        verts.append(tip)
    # cap: a bevel ring half a step turned, then the fan centre
    ring, tw, n, b = rings[-1]
    t, p, r = tans[-1], pts[-1], rad[-1]
    cap_faces = []
    if cap:
        bev = []
        for k in range(sides):
            th = tw + 2 * math.pi * (k + 0.5) / sides
            rr = r * CAP_BEVEL[1] * (1.0 + rng.uniform(-0.04, 0.04))
            off = (n * math.cos(th) + b * math.sin(th)) * rr
            off.y *= yscale
            bev.append(bm.verts.new(p + off + t * (CAP_BEVEL[0] * (1.0 + rng.uniform(-0.12, 0.12)))))
        for k in range(sides):
            j = (k + 1) % sides
            cap_faces.append(bm.faces.new((ring[k], ring[j], bev[k])))
            cap_faces.append(bm.faces.new((ring[k], bev[k], bev[(k - 1) % sides])))
        top = bm.verts.new(p + t * (CAP_BEVEL[0] + CAP_FAN) + n * r * 0.06)
        fan = _fan(bm, bev, top)
        cap_faces += fan
        verts += bev + [top]
        if info is not None:
            info.setdefault("caps", []).append({"centre": tuple(p + t * (CAP_BEVEL[0] + CAP_FAN)), "axis": tuple(t),
                                                "radius": r})
    else:
        c = bm.verts.new(p + t * 0.15)
        cap_faces += _fan(bm, ring, c)
        verts.append(c)
    bmesh.ops.triangulate(bm, faces=[f for f in faces + cap_faces if f.is_valid and len(f.verts) > 3],
                          quad_method="BEAUTY", ngon_method="BEAUTY")
    a._finish(verts, key)
    bmesh.ops.recalc_face_normals(bm, faces=K.faces_of(verts))
    if cap:
        ci = a._mi(cap_key)
        cs = {v for v in bev + [top]}
        for f in K.faces_of(verts):
            if all(v in cs or v in ring for v in f.verts) and any(v in cs for v in f.verts):
                f.material_index = ci
    return verts


# ---- Main Branch (Crystal Assembly) ---------------------------------------------------------------------------------
# Trunk axis at (TX, TY); stations bottom (root tip) -> cap. (point, radius). The sand line (socket 1's rim) is at
# about z 1.95: the trunk there is 2.36 wide, in a pit 3.5 across the corners (spec §6.1).
TX, TY = 0.2, -0.5
TRUNK = ((0.75, 0.38), (1.25, 0.84), (1.95, 1.13), (2.65, 1.34), (3.4, 1.32), (4.25, 1.22), (5.15, 1.2),
         (6.05, 1.22), (6.9, 1.25), (7.6, 1.28))
TRUNK_TIP = 0.42
TRUNK_YSCALE = 1.1          # the trunk's section is a little deeper than wide (side view 2.5 against front 2.3)
# arms: (point, radius) from inside the trunk out to the cap ring (the cap adds CAP_BEVEL + CAP_FAN along the axis)
# arms: (distance from the trunk axis along the arm's heading, z, radius) from inside the trunk out to the cap ring
# (the cap adds CAP_BEVEL + CAP_FAN along the axis). The first run is shallow (25-30 deg), the elbow turns the end run
# up to the cap, as the sheet's front and exploded views draw them.
ARM_R_HEAD = (3.4, -1.25)       # heading in plan from the trunk axis: front-right
ARM_L_HEAD = (-3.35, 2.55)      # back-left
ARM_R_ST = ((0.0, 3.0, 0.85), (1.2, 3.55, 1.08), (2.1, 4.15, 0.98), (2.8, 4.68, 0.96), (3.3, 5.12, 1.04),
            (3.55, 5.5, 1.1))
ARM_L_ST = ((0.0, 3.05, 0.82), (1.25, 3.55, 1.05), (2.3, 4.12, 0.95), (3.15, 4.58, 0.93), (3.75, 4.92, 1.0),
            (4.0, 5.22, 1.06))


def _arm(head, st):
    d = Vector((head[0], head[1], 0)).normalized()
    return tuple(((TX + d.x * h, TY + d.y * h, z), r) for h, z, r in st)


ARM_R = _arm(ARM_R_HEAD, ARM_R_ST)
ARM_L = _arm(ARM_L_HEAD, ARM_L_ST)
SEEDS = {"trunk": 16001, "right": 16002, "left": 16003, "sprig_stem": 16004, "sprig_arm": 16005}
BRANCH_INFO = {}


def limbs():
    """The three limbs' stations in the build frame (for colour and VFX)."""
    trunk = [((TX, TY, z), r) for z, r in TRUNK]
    return {"trunk": trunk, "right": list(ARM_R), "left": list(ARM_L)}


def branch(a):
    BRANCH_INFO.clear()
    L = limbs()
    _limb(a, L["trunk"], SEEDS["trunk"], start=("point", (TX, TY, TRUNK_TIP)), info=BRANCH_INFO, rjit=0.05,
          yscale=TRUNK_YSCALE)
    _limb(a, L["right"], SEEDS["right"], info=BRANCH_INFO)
    _limb(a, L["left"], SEEDS["left"], info=BRANCH_INFO)


# ---- Side Branch (sprig) --------------------------------------------------------------------------------------------
SX = 7.0          # built off to the side in the build frame (not in the hero)
SPRIG_STEM = (((0.2, 0, 0.45), 0.3), ((0.05, 0, 1.0), 0.55), ((-0.1, 0, 1.7), 0.7), ((-0.3, 0, 2.45), 0.66),
              ((-0.5, 0, 3.05), 0.7))
SPRIG_TIP = (0.3, 0, 0.0)
SPRIG_ARM = (((-0.1, 0, 1.75), 0.48), ((0.55, 0, 2.1), 0.64), ((1.15, 0, 2.5), 0.62), ((1.5, 0, 2.85), 0.7))


def sprig(a):
    st = [((SX + x, y, z), r) for (x, y, z), r in SPRIG_STEM]
    _limb(a, st, SEEDS["sprig_stem"], start=("point", (SX + SPRIG_TIP[0], SPRIG_TIP[1], SPRIG_TIP[2])))
    _limb(a, [((SX + x, y, z), r) for (x, y, z), r in SPRIG_ARM], SEEDS["sprig_arm"])


# ---- Sand Base (mound) ----------------------------------------------------------------------------------------------
MOUND = dict(rx=4.2, ry=3.65, n=16, seed=16011, base=-0.05)
# rings: (z, radius fraction); the top centre vertex at MOUND_TOP
MOUND_RINGS = ((-0.05, 1.0), (0.5, 0.95), (1.2, 0.82), (1.75, 0.64), (2.02, 0.42), (2.12, 0.2))
MOUND_TOP = 2.15
# sockets: (centre x, y, circumradius, depth below the lowest rim corner, collar width, rotation deg)
SOCKETS = {"main": (TX, TY, 1.65, 0.68, 0.32, 0.0), "side": (-1.9, 1.5, 0.75, 0.45, 0.22, 15.0)}
# how far each pit floor follows its rim's slope (0 level, 1 parallel to the rim): the side socket sits on the slope
FLOOR_TILT = {"main": 0.5, "side": 1.0}
POCKETS = ((-1.8, 1.2), (1.9, 0.6), (-0.2, -2.0))
POCKET_R, POCKET_D = 0.7, 0.45
WALL_TAPER = math.radians(5.0)
MOUND_INFO = {}


def _lobe(th, seed):
    r = random.Random(seed)
    p1, p2, p3 = r.uniform(0, 6.3), r.uniform(0, 6.3), r.uniform(0, 6.3)
    return 1.0 + 0.045 * math.sin(8 * th + p1) + 0.03 * math.sin(3 * th + p2) + 0.02 * math.sin(5 * th + p3)


def mound(a):
    """The bare dome: lofted lobed rings, flat bottom (fan), fan top."""
    m = MOUND
    rng = random.Random(m["seed"])
    bm = a.bm
    rings = []
    for i, (z, rf) in enumerate(MOUND_RINGS):
        n = m["n"]
        off = (math.pi / n) * (i % 2) + rng.uniform(-0.05, 0.05)
        ring = []
        for k in range(n):
            th = off + 2 * math.pi * k / n + rng.uniform(-0.08, 0.08)
            j = _lobe(th, m["seed"] + i // 2) * (1 + rng.uniform(-0.025, 0.025))
            dz = 0.0 if i == 0 else rng.uniform(-0.07, 0.07)
            ring.append(bm.verts.new((math.cos(th) * m["rx"] * rf * j, math.sin(th) * m["ry"] * rf * j, z + dz)))
        rings.append(ring)
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        faces += _strip(bm, r0, r1)
    bot = bm.verts.new((0, 0, m["base"]))
    top = bm.verts.new((0.15, -0.1, MOUND_TOP))
    faces += _fan(bm, rings[0], bot, flip=True)
    faces += _fan(bm, rings[-1], top)
    bmesh.ops.triangulate(bm, faces=[f for f in faces if len(f.verts) > 3], quad_method="BEAUTY")
    vs = [v for r in rings for v in r] + [bot, top]
    a._finish(vs, SAND)
    bmesh.ops.recalc_face_normals(bm, faces=K.faces_of(vs))
    return vs


def _sand_tree():
    """BVH of the bare mound in the build frame (a throwaway build)."""
    a = K.fk().Asset("_m016_probe", "probe")
    mound(a)
    a.bm.verts.ensure_lookup_table()
    a.bm.faces.ensure_lookup_table()
    t = BVHTree.FromBMesh(a.bm)
    a.bm.free()
    return t


def _sand_z(tree, x, y):
    h = tree.ray_cast(Vector((x, y, 30.0)), Vector((0, 0, -1)), 60)
    return h[0].z if h[0] is not None else 0.0


def _hex(cx, cy, r, rot):
    return [(cx + r * math.cos(math.radians(rot + 60 * k)), cy + r * math.sin(math.radians(rot + 60 * k)))
            for k in range(6)]


def _socket_geo(name):
    """Per-socket heights from the bare mound: the sand z at each rim corner, the rim (lowest corner) and the floor."""
    tree = _sand_tree()
    cx, cy, R, depth, w, rot = SOCKETS[name]
    s = [_sand_z(tree, x, y) for x, y in _hex(cx, cy, R + 0.12, rot)]
    so = [_sand_z(tree, x, y) for x, y in _hex(cx, cy, R + w + 0.05, rot)]
    t = FLOOR_TILT[name]
    floor = [min(s) + t * (z - min(s)) - depth for z in s]
    MOUND_INFO[name] = {"rim": [round(z, 3) for z in s], "floor": [round(z, 3) for z in floor]}
    return s, so, floor


def _closed_rings(a, rings, mat, top_c, bot_c):
    """A closed solid from stacked hex rings (bottom to top) with fan caps; returns verts."""
    bm = a.bm
    vr = [[bm.verts.new(p) for p in r] for r in rings]
    faces = []
    for r0, r1 in zip(vr, vr[1:]):
        faces += _strip(bm, r0, r1)
    b = bm.verts.new(bot_c)
    t = bm.verts.new(top_c)
    faces += _fan(bm, vr[0], b, flip=True)
    faces += _fan(bm, vr[-1], t)
    bmesh.ops.triangulate(bm, faces=[f for f in faces if len(f.verts) > 3], quad_method="BEAUTY")
    vs = [v for r in vr for v in r] + [b, t]
    a._finish(vs, mat)
    bmesh.ops.recalc_face_normals(bm, faces=K.faces_of(vs))
    return vs


def collar(a, name):
    """The raised bevelled lip round a socket: a closed hex cake whose sloped top rises 0.08 above the sand at the
    rim, its outer edge just under the sand; the pit carve removes its middle."""
    cx, cy, R, depth, w, rot = SOCKETS[name]
    s, so, floor = _socket_geo(name)
    outer = _hex(cx, cy, R + w, rot)
    lip = _hex(cx, cy, R + 0.12, rot)
    rings = [[(x, y, min(floor) - 0.25) for x, y in outer],
             [(x, y, z - 0.07) for (x, y), z in zip(outer, so)],
             [(x, y, z + 0.08) for (x, y), z in zip(lip, s)]]
    return _closed_rings(a, rings, SAND, (cx, cy, max(s) + 0.1), (cx, cy, min(floor) - 0.25))


def pit(a, name):
    """The socket's cutter: a 50-degree chamfer cone from above the lip down to the rim line (SAND_RIM), steep walls
    tapering in WALL_TAPER down to a flat floor (SAND_PIT)."""
    cx, cy, R, depth, w, rot = SOCKETS[name]
    s, so, floor = _socket_geo(name)
    rf = R - math.tan(WALL_TAPER) * depth
    top = [(x, y, z + 0.55) for (x, y), z in zip(_hex(cx, cy, R + 0.46, rot), s)]
    rim = [(x, y, z - 0.12) for (x, y), z in zip(_hex(cx, cy, R, rot), s)]
    flo = [(x, y, z) for (x, y), z in zip(_hex(cx, cy, rf, rot), floor)]
    bm = a.bm
    vt = [bm.verts.new(p) for p in top]
    vr = [bm.verts.new(p) for p in rim]
    vf = [bm.verts.new(p) for p in flo]
    tc = bm.verts.new((cx, cy, max(s) + 0.6))
    fc = bm.verts.new((cx, cy, sum(floor) / 6))
    walls = _strip(bm, vf, vr)
    cone = _strip(bm, vr, vt)
    caps = _fan(bm, vt, tc) + _fan(bm, vf, fc, flip=True)
    bmesh.ops.triangulate(bm, faces=[f for f in walls + cone if len(f.verts) > 3], quad_method="BEAUTY")
    vs = vt + vr + vf + [tc, fc]
    a._finish(vs, SAND_PIT)
    bmesh.ops.recalc_face_normals(bm, faces=K.faces_of(vs))
    ri = a._mi(SAND_RIM)
    rs = set(vt) | set(vr)
    for f in K.faces_of(vs):
        if all(v in rs for v in f.verts):
            f.material_index = ri
    return vs


def pockets(a):
    """The three blind hex pockets under the base (cutters from below the ground up to POCKET_D)."""
    out = []
    for k, (x, y) in enumerate(POCKETS):
        h = _hex(x, y, POCKET_R, 30.0 + 17 * k)
        rings = [[(px, py, -0.6) for px, py in h], [(px, py, POCKET_D) for px, py in h]]
        out += _closed_rings(a, rings, SAND_PIT, (x, y, POCKET_D + 0.08), (x, y, -0.6))
    return out


# ---- Base Rock (stone, variants) -------------------------------------------------------------------------------------
STONES = {
    "A": dict(size=(2.8, 2.3, 1.7), seed=16031, lean=(0.08, 0.05),
              rings=[(0.0, 0.92, 8), (0.25, 1.0, 8), (0.55, 0.88, 7), (0.82, 0.6, 6), (1.0, 0.22, 3)]),
    "B": dict(size=(2.0, 1.8, 1.45), seed=16032, lean=(0.05, -0.05),
              rings=[(0.0, 0.92, 8), (0.28, 1.0, 7), (0.6, 0.82, 7), (0.85, 0.48, 5), (1.0, 0.15, 2)]),
    "C": dict(size=(1.7, 1.6, 1.5), seed=16033, lean=(0.18, 0.08),
              rings=[(0.0, 0.95, 7), (0.28, 1.0, 7), (0.58, 0.8, 6), (0.82, 0.48, 4), (1.0, 0.16, 2)]),
    "D": dict(size=(1.6, 1.4, 0.95), seed=16034, lean=(0.05, 0.0),
              rings=[(0.0, 0.94, 7), (0.32, 1.0, 7), (0.68, 0.8, 6), (1.0, 0.36, 4)]),
}
STONE_MERGE = 3.0
STONE_INFO = {}


def _stone(a, v, loc=(0, 0, 0)):
    s = STONES[v]
    vs = K.hull_rock(a, s["size"], loc=loc, seed=s["seed"], mat=ROCK, rings=s["rings"], jitter=0.08,
                     lean=s["lean"], keep_bottom=True)
    faces = K.faces_of(vs)
    bmesh.ops.dissolve_limit(a.bm, angle_limit=math.radians(STONE_MERGE), verts=vs,
                             edges=list({e for f in faces for e in f.edges}))
    vs = [x for x in vs if x.is_valid]
    STONE_INFO[v] = len(K.faces_of(vs))
    bmesh.ops.triangulate(a.bm, faces=[f for f in K.faces_of(vs) if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
    return vs


def stone(a):
    return _stone(a, "A")


def stone_b(a):
    return _stone(a, "B")


def stone_c(a):
    return _stone(a, "C")


def stone_d(a):
    return _stone(a, "D")


VARIANT_FN = {"A": stone, "B": stone_b, "C": stone_c, "D": stone_d}

# ---- hero layout -----------------------------------------------------------------------------------------------------
# rocks: (label, centre x, y, W, D, H (top above the ground, or absolute top z for the mound rocks), yaw deg,
#         variant, mirror, sink)
ROCKS = (
    ("R1", -2.75, -2.75, 2.7, 2.15, 1.55, 20.0, "A", False, 0.3),      # the big front-left boulder
    ("R2", 0.2, -3.5, 1.62, 1.26, 0.93, -10.0, "B", False, 0.27),
    ("R3", 2.3, -3.1, 1.44, 1.17, 0.84, 35.0, "D", True, 0.33),
    ("R4", 3.65, -2.0, 1.44, 1.53, 1.21, 60.0, "C", False, 0.29),
    ("R5", 4.25, -0.3, 1.17, 1.44, 1.02, 95.0, "B", True, 0.31),
    ("R6", 3.65, 1.55, 1.35, 1.53, 1.26, 130.0, "C", True, 0.26),
    ("R7", 2.1, 3.0, 1.53, 1.17, 1.26, 160.0, "B", False, 0.34),
    ("R8", -0.4, 3.45, 1.80, 1.17, 1.12, 185.0, "A", True, 0.28),
    ("R9", -3.05, 2.3, 2.07, 1.80, 1.40, 220.0, "A", False, 0.32),
    ("R10", -4.3, 0.1, 1.35, 1.53, 1.40, 265.0, "C", False, 0.3),
    ("R11", -3.85, -1.65, 1.44, 1.62, 1.21, 300.0, "B", True, 0.35),
)
# rocks on the mound's upper slope: (label, x, y, W, D, height above the sand, yaw, variant, mirror, sink). Each
# sits on the slope, its flat bottom turned TOP_TILT of the way towards the sand's normal there, so it reads as a
# squat stone bedded in the slope, not a spike.
TOP_ROCKS = (
    ("T1", 0.45, -2.62, 1.4, 0.95, 0.95, 10.0, "D", False, 0.3),
    ("T2", -0.2, 2.75, 1.5, 1.2, 0.85, 200.0, "B", True, 0.3),
)
TOP_TILT = 0.7
MOUND_SINK = 0.0


def _frame(o):
    """Part mesh coordinates -> the shared build frame."""
    return Matrix.Translation(Vector(o[OFF]))


def _part_dims(o):
    m = _frame(o)
    ps = [m @ v.co for v in o.data.vertices]
    return Vector([max(p[i] for p in ps) - min(p[i] for p in ps) for i in range(3)])


def _part_lo(o):
    m = _frame(o)
    ps = [m @ v.co for v in o.data.vertices]
    return Vector([min(p[i] for p in ps) for i in range(3)]), Vector([max(p[i] for p in ps) for i in range(3)])


def _rock_matrix(x, y, w, d, z0, z1, yaw, mirror, part):
    lo, hi = _part_lo(part)
    pd = hi - lo
    c = Matrix.Translation(-Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)))
    pre = Matrix.Diagonal((-1.0, 1.0, 1.0, 1.0)) if mirror else Matrix.Identity(4)
    return (Matrix.Translation((x, y, z0)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @
            Matrix.Diagonal((w / pd.x, d / pd.y, (z1 - z0) / pd.z, 1.0)) @ pre @ c @ _frame(part))


def _variant_obj(v):
    return bpy.data.objects["StormglassStone"] if v == "A" else bpy.data.objects[f"_m016_stone_{v.lower()}"]


def placements():
    """label -> (part object name, matrix from the part's mesh coordinates into the hero's build frame)."""
    br = bpy.data.objects["StormglassBranch"]
    mo = bpy.data.objects["StormglassMound"]
    out = {"Mound": (mo.name, Matrix.Translation((0, 0, -MOUND_SINK)) @ _frame(mo)),
           "Branch": (br.name, _frame(br))}
    for lab, x, y, w, d, h, yaw, v, mir, sink in ROCKS:
        p = _variant_obj(v)
        out[lab] = (p.name, _rock_matrix(x, y, w, d, -sink, h, yaw, mir, p))
    tree = _sand_tree()
    for lab, x, y, w, d, hv, yaw, v, mir, sink in TOP_ROCKS:
        p = _variant_obj(v)
        hit, n = _sand_hit(tree, x, y)
        up = Vector((0, 0, 1)).lerp(n, TOP_TILT).normalized()
        tilt = Vector((0, 0, 1)).rotation_difference(up).to_matrix().to_4x4()
        m = _rock_matrix(0.0, 0.0, w, d, -sink, hv, yaw, mir, p)
        out[lab] = (p.name, Matrix.Translation(hit) @ tilt @ m)
    return out


def _sand_hit(tree, x, y, r=0.5):
    """The sand point under (x, y) and the mean sand normal round it (5 rays)."""
    p, ns = None, Vector()
    for dx, dy in ((0, 0), (r, 0), (-r, 0), (0, r), (0, -r)):
        h = tree.ray_cast(Vector((x + dx, y + dy, 30.0)), Vector((0, 0, -1)), 60)
        if h[0] is not None:
            ns += h[1]
            if p is None:
                p = h[0]
    return p, ns.normalized()


def hero(a):
    for name, (part, m) in placements().items():
        m011._paste(a, bpy.data.objects[part], m)


NOTES = {
    "StormglassNode": "stormglass resource node: a chunky faceted teal crystal tree (thick trunk, two thick arms, flat "
                      "octagonal caps) standing in a hexagonal socket pit in a low lumpy sand mound, a ring of "
                      "grey-brown faceted rocks round the foot and two on the upper slope, a second small empty "
                      "socket behind the trunk, three blind pockets under the base; one closed mesh, flat base",
    "StormglassBranch": "Crystal Assembly (Main Branch, reusable): faceted teal tube tree, a thick trunk with a buried "
                        "blunt root and two thick arms, every limb ending in a flat octagonal cap",
    "StormglassSprig": "Crystal Branch (Side Branch, reusable): a short faceted Y twig of the same limbs and caps",
    "StormglassMound": "Sand Base (with sockets, reusable): low lumpy faceted sand dome, a big hexagonal socket pit and "
                       "a small one on top (raised bevelled rims, steep walls, flat floors), three blind hex pockets "
                       "in the flat bottom",
    "StormglassStone": "Base Rock (reusable): faceted boulder, broad top facet, flat bottom",
}


# ---- object-level booleans (in the build frame through OFF) ----------------------------------------------------------
def _tmp_obj(o, fn, name):
    a = K.fk().Asset(name, "probe")
    fn(a)
    c = a.finish(collection=o.users_collection[0], mark_asset=False, origin=None)
    c.matrix_world = o.matrix_world @ Matrix.Translation(-Vector(o[OFF]))
    return c


def _bool(o, c, op):
    m = o.modifiers.new("B", "BOOLEAN")
    m.operation, m.solver, m.object = op, "EXACT", c
    m.use_self = op == "DIFFERENCE"
    m.material_mode = "TRANSFER"
    with M._override(o):
        bpy.ops.object.modifier_apply(modifier=m.name)
    me = c.data
    bpy.data.objects.remove(c, do_unlink=True)
    bpy.data.meshes.remove(me)
    K.drop_unused_slots(o)


def _union_fn(o, fn, name="_m016_add"):
    _bool(o, _tmp_obj(o, fn, name), "UNION")


def _carve_fn(o, fn, name="_m016_cut"):
    _bool(o, _tmp_obj(o, fn, name), "DIFFERENCE")


def _sockets(o):
    """Collar then pit for each socket, one boolean at a time."""
    for name in SOCKETS:
        _union_fn(o, lambda a, n=name: collar(a, n))
        _carve_fn(o, lambda a, n=name: pit(a, n))


# ---- cleanup -----------------------------------------------------------------------------------------------------
def _bottom_centre(o):
    return m012._bottom_centre(o)


def _finish(o):
    o[OFF] = list(Vector(o[OFF]) + _bottom_centre(o))
    res = M.finish(o, union=False, uv=_uv(o))
    for _ in range(3):
        crumbs = m012._drop_inner(o)
        if not (crumbs or m012._thin(o)["under"] or res["nonmanifold_edges"] or res["boundary_edges"]):
            break
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bnd = [e for e in bm.edges if e.is_boundary]
        if bnd:
            if not bmesh.ops.holes_fill(bm, edges=bnd)["faces"]:
                bmesh.ops.contextual_create(bm, geom=bnd)
            bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY")
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(o.data)
        bm.free()
        M.repair_nonmanifold(o)
        m012._force_slivers(o)
        o[OFF] = list(Vector(o[OFF]) + _bottom_centre(o))
        res = M.finish(o, union=False, uv=_uv(o))
    return res


def _polish(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = m012._tri_quads(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = m012._force_slivers(o, lim=POLISH_LIM)
    if m012._thin(o, POLISH_LIM)["under"]:
        # a sliver whose shortest edge is over the default 0.25 (one on the hero, at a rock / mound crease): allow a
        # longer collapse (still link-checked and keeping the ground flat)
        forced += m012._force_slivers(o, lim=POLISH_LIM, max_len=0.5)
    bc = _bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()
    M.smart_uv(o, **_uv(o))
    return {"split": split, "forced": forced, "uv_cut": m012._uv_unfold(o)}


def _dissolve_ears(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    ears = [v for v in bm.verts if len(v.link_edges) == 2 and len(v.link_faces) == 2
            and any(len(f.verts) == 3 for f in v.link_faces)]
    if ears:
        bmesh.ops.dissolve_verts(bm, verts=ears)
        bm.to_mesh(o.data)
    bm.free()
    return len(ears)


def _weld(o, dist=1e-4):
    """Zero-length edges and degenerate faces the booleans can leave (m011._desliver divides by edge length)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=dist)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(o.data)
    bm.free()


def _clean_mesh(o, planes):
    _weld(o)
    ears = _dissolve_ears(o)
    pockets_ = m012._drop_inner(o)
    log = m011._clean(o, m011._plane_lock(planes), max_move=m011.CLEAN_MOVE)
    pockets_ += m012._drop_inner(o)
    log["ears"] = ears
    log["pockets"] = pockets_
    log["forced"] = m012._force_slivers(o)
    return log


def _self_hits(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    off = Vector(o.get(OFF, (0.0, 0.0, 0.0)))
    pairs = [(a, b) for a, b in tree.overlap(tree)
             if a < b and not set(bm.faces[a].verts) & set(bm.faces[b].verts)]
    where = [(a, b, [round(c, 2) for c in bm.faces[a].calc_center_median() + off]) for a, b in pairs[:5]]
    bm.free()
    return len(pairs), where


def _floor_cut(o, z0):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), plane_co=(0, 0, z0),
                           plane_no=(0, 0, -1), clear_outer=True)
    below = [v for v in bm.verts if v.co.z < z0 - 1e-4]
    if below:
        bmesh.ops.delete(bm, geom=below, context="VERTS")
    for v in bm.verts:
        if v.co.z < z0 + 0.02:
            v.co.z = z0
        v.co.z -= z0
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    bnd = [e for e in bm.edges if e.is_boundary]
    if bnd:
        bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=bnd, normal=(0.0, 0.0, -1.0))
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=0.004)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()


# ---- measurement: silhouettes against the study's tables (M016_spec.md §1.2) ----------------------------------------
SHEET_PROFILES = {
    "front": (.09, .21, .25, .74, .76, .78, .75, .61, .94, .99, .99, .99, .97, .63, .65, .71, .78, .79, .78, .73, .08),
    "side": (.07, .16, .20, .24, .71, .78, .93, .97, .99, 1.0, .99, .99, .94, .61, .68, .69, .68, .67, .20, .14, .06),
    "rear": (.07, .68, .72, .74, .74, .71, .60, .95, .99, .99, .99, .98, .93, .60, .64, .75, .76, .76, .75, .65, .07),
}
SHEET_SHARES = {"front": (0.526, 0.264, 0.210), "side": (0.545, 0.237, 0.218), "rear": (0.570, 0.213, 0.217),
                "top": (0.343, 0.443, 0.214), "f34": (0.460, 0.294, 0.246), "r34": (0.520, 0.260, 0.220)}
SHEET_SPANS = {"front": ((0.12, 0.94), (0.26, 1.0)), "side": ((0.21, 0.86), (0.26, 1.0)),
               "rear": ((0.04, 0.94), (0.26, 1.0))}
SHEET_VIEWS = {"front": (0.0, 9.0), "side": (90.0, 9.0), "rear": (180.0, 9.0), "top": (0.0, 89.0),
               "f34": (-15.0, 12.0), "r34": (165.0, 12.0)}


def _region(key):
    return 2 if key.startswith("m016_glass") else 3 if key.startswith("m016_rock") else 1


def _raster(o, az, el, res=240):
    """Orthographic label image of o from (azimuth, elevation): 0 empty, 1 sand, 2 crystal, 3 rock (z-buffered)."""
    a, e = math.radians(az), math.radians(el)
    if el >= 80:
        dirv, right, up = Vector((0, 0, 1)), Vector((1, 0, 0)), Vector((0, 1, 0))
    else:
        dirv = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
        right = Vector((math.cos(a), math.sin(a), 0.0))
        up = dirv.cross(right).normalized()
    me = o.data
    co = np.array([tuple(o.matrix_world @ v.co) for v in me.vertices])
    P = np.stack([co @ np.array(right), co @ np.array(up), co @ np.array(dirv)], axis=1)
    u0, u1, v0, v1 = P[:, 0].min(), P[:, 0].max(), P[:, 1].min(), P[:, 1].max()
    s = res / (u1 - u0)
    W, H = res + 1, int((v1 - v0) * s) + 1
    zb = np.full((H, W), -1e9)
    lab = np.zeros((H, W), np.uint8)
    keys = [(m.get("flintkit_key") or m.name[3:]) if m else "" for m in me.materials]
    for p in me.polygons:
        lb = _region(keys[p.material_index])
        idx = list(p.vertices)
        for k in range(1, len(idx) - 1):
            t = P[[idx[0], idx[k], idx[k + 1]]]
            x = (t[:, 0] - u0) * s
            y = (t[:, 1] - v0) * s
            xa, xb = int(max(0, math.floor(x.min()))), int(min(W - 1, math.ceil(x.max())))
            ya, yb = int(max(0, math.floor(y.min()))), int(min(H - 1, math.ceil(y.max())))
            den = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
            if abs(den) < 1e-12:
                continue
            gx, gy = np.meshgrid(np.arange(xa, xb + 1) + 0.0, np.arange(ya, yb + 1) + 0.0)
            l1 = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / den
            l2 = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / den
            l3 = 1 - l1 - l2
            inside = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
            d = l1 * t[0, 2] + l2 * t[1, 2] + l3 * t[2, 2]
            sub = zb[ya:yb + 1, xa:xb + 1]
            upd = inside & (d > sub)
            sub[upd] = d[upd]
            lab[ya:yb + 1, xa:xb + 1][upd] = lb
    return lab


def silhouette(o, az, el, res=240):
    lab = _raster(o, az, el, res)
    H, W = lab.shape
    filled = lab > 0
    prof, cbot = [], []
    for k in range(21):
        c = min(W - 1, int(round(k / 20 * (W - 1))))
        rows = np.nonzero(filled[:, c])[0]
        prof.append(round(float(rows.max() / (H - 1)), 2) if len(rows) else 0.0)
        cr = np.nonzero(lab[:, c] == 2)[0]
        cbot.append(round(float(cr.min() / (H - 1)), 2) if len(cr) else None)
    n = filled.sum()
    out = {"aspect": round(W / H, 2), "profile": prof, "crystal_bottom": cbot,
           "shares": tuple(round(float((lab == k).sum() / n), 3) for k in (2, 1, 3))}
    cr = lab == 2
    if cr.any():
        cols, rows = np.nonzero(cr.any(axis=0))[0], np.nonzero(cr.any(axis=1))[0]
        out["span_w"] = (round(cols.min() / (W - 1), 2), round(cols.max() / (W - 1), 2))
        out["span_h"] = (round(rows.min() / (H - 1), 2), round(rows.max() / (H - 1), 2))
    return out


def measure(o=None):
    o = o or bpy.data.objects["StormglassNode"]
    out = {}
    for v, (az, el) in SHEET_VIEWS.items():
        s = silhouette(o, az, el)
        if v in SHEET_PROFILES:
            err = [abs(a - b) for a, b in zip(s["profile"], SHEET_PROFILES[v])]
            s["prof_err"] = (round(sum(err) / len(err), 3), round(max(err), 2))
            s["sheet_span"] = SHEET_SPANS[v]
        s["sheet_shares"] = SHEET_SHARES[v]
        out[v] = s
    return out


def socket_gap(o=None):
    """Spec §6.1 check: rays from the trunk axis outward at the rim height and 0.5 below, 6 stations each: distance
    from the crystal surface to the pit wall. Also the pit depth (rim min - floor)."""
    o = o or bpy.data.objects["StormglassNode"]
    off = Vector(o[OFF])
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    keys = [(m.get("flintkit_key") or m.name[3:]) for m in o.data.materials]
    vs = [v.co + off for v in bm.verts]
    vi = {v: i for i, v in enumerate(bm.verts)}
    cf = [[vi[v] for v in f.verts] for f in bm.faces if _region(keys[f.material_index]) == 2]
    sf = [[vi[v] for v in f.verts] for f in bm.faces if _region(keys[f.material_index]) != 2]
    bm.free()
    ct, st = BVHTree.FromPolygons(vs, cf), BVHTree.FromPolygons(vs, sf)
    info = MOUND_INFO.get("main") or {}
    rim = min(info.get("rim", [1.95]))
    out = {}
    for dz, lab in ((-0.05, "rim"), (-0.5, "below")):
        z = rim + dz
        gaps = []
        for k in range(6):
            th = math.radians(30 + 60 * k)
            d = Vector((math.cos(th), math.sin(th), 0))
            p0 = Vector((TX, TY, z))
            hc = ct.ray_cast(p0 + d * 3.0, -d, 3.0)          # crystal surface from outside
            hs = st.ray_cast(p0, d, 4.0)                     # first sand / rock wall from the axis outward
            if hc[0] is None or hs[0] is None:
                gaps.append(None)
                continue
            gaps.append(round((hs[0] - p0).length - (hc[0] - p0).length, 2))
        out[lab] = gaps
    out["depth"] = [round(a - b, 2) for a, b in zip(info["rim"], info["floor"])] if info else None
    return out


# ---- stage 4: colour regions, blends and Tint ---------------------------------------------------------------------
# colour() rewrites only the face keys and the Tint layer of a freshly built mesh (geometry and UVs untouched). A face's
# region comes from its placeholder key (m016_glass* crystal, m016_sand* sand, m016_rock* rock; the pit walls / floor
# carry SAND_PIT, the rim chamfer SAND_RIM, the caps GLASS_CAP from the builders). Every field is a position in the
# shared build frame (a rock's own part frame for the rocks); no colour is ever chosen by facing (M016_spec.md §5.5).
STEPS = 3
SAND_LINE, TRUNK_TOP = 2.0, 8.0          # the trunk's u runs from the sand line to the cap top
EXIT_R = 1.3                             # an arm's u starts where it leaves the trunk (this far from the trunk axis)
# crystal ladder bands on u: deep below DEEP_BAND[0], deep -> body across DEEP_BAND, body, body -> light across
# LIGHT_BAND, light above; broad noise CRYS_NOISE on u so the bands don't read as rings
DEEP_BAND, LIGHT_BAND = (0.04, 0.3), (0.6, 0.86)
CRYS_NOISE, CRYS_SCALE, CRYS_SEED = 0.08, 0.45, 16061
CROTCH = 0.4                             # within this of another limb's surface: no lighter than ladder step 2
FAN_PROJ = 0.17                          # cap faces whose centre is this far past the last ring along the axis: fan
# the cap fans are GLASS_GLINT on the hero (3 caps among ~1800 faces); on the branch / sprig parts, where the caps are
# a large share of the faces and K.check's facing correlation came out 0.52 (limit 0.5), they are half way from
# GLASS_LIGHT to GLASS_GLINT (spec §5.4's fallback), so the sun makes up the rest of their pallor
GLINT_KINDS = ("hero",)
# sand: height field (z) towards SAND_LIGHT, foot band and rock contact towards SAND_DARK, broad noise patches
SAND_HEIGHT = (1.3, 2.0, 0.75)           # from z0 to z1, up to this mix
SAND_FOOT = ((0.35, 0.5), (0.7, 0.25))
SAND_CONTACT = (0.25, 0.5)
SAND_NOISE = dict(scale=0.38, level=0.18, add=0.25, seed=16062)
# rocks: accent patches (noise above level -> 50 %, above level2 -> 100 %), ACCENT_ROCKS mostly accent, the ground
# row and the sand contact towards ROCK_DARK (never on the crown)
ROCK_NOISE = dict(scale=0.55, level=0.12, level2=0.32, seed=16063)
ACCENT_ROCKS = {"R1": 0.5, "R6": 0.5, "R10": 0.5}
ROCK_GROUND, ROCK_CONTACT, ROCK_CROWN = 0.15, 0.2, 0.7     # (0.22 / 0.3: 60 % of the hero's rock faces went dark
# and K.check's facing correlation for the rock family reached 0.50)
MOTTLE = {"sand": dict(amp=0.05, scale=0.4, jitter=0.015, seed=16065),
          "rock": dict(amp=0.06, scale=0.45, jitter=0.015, seed=16066),
          "glass": dict(amp=0.025, scale=0.5, jitter=0.0, seed=16067)}
PIECE_TINT = {"R1": 1.02, "R2": 0.97, "R3": 1.03, "R4": 0.98, "R5": 1.02, "R6": 0.97, "R7": 1.01, "R8": 0.98,
              "R9": 1.03, "R10": 0.99, "R11": 1.02, "T1": 0.97, "T2": 1.02}


def _q(t):
    return round(min(1.0, max(0.0, t)) * (STEPS + 1)) / (STEPS + 1)


def _crys_ladder():
    return ([GLASS_DEEP] + [K.mix_key(GLASS_DEEP, GLASS, t) for t in (0.25, 0.5, 0.75)] + [GLASS] +
            [K.mix_key(GLASS, GLASS_LIGHT, t) for t in (0.25, 0.5, 0.75)] + [GLASS_LIGHT])


def _key_region(key):
    return "glass" if key.startswith("m016_glass") else "rock" if key.startswith("m016_rock") else "sand"


def _seg_param(c, pts):
    """Nearest point of polyline pts to c: (distance, arc length there, total length, segment index, t)."""
    best, acc = None, 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        ab = b - a
        L = ab.length
        t = max(0.0, min(1.0, (c - a).dot(ab) / (L * L)))
        d = (a + ab * t - c).length
        if best is None or d < best[0]:
            best = (d, acc + t * L, i, t)
        acc += L
    return best[0], best[1], acc, best[2], best[3]


class _Limbs:
    """The crystal's limbs (stations in the build frame) and their u fields."""

    def __init__(self, limbs_, trunk=None):
        self.L = {k: ([Vector(p) for p, _ in st], [r for _, r in st]) for k, st in limbs_.items()}
        self.trunk = trunk
        self.exit = {}
        for k, (pts, rad) in self.L.items():
            if trunk is None or k == trunk:
                self.exit[k] = 0.0
                continue
            ax = Vector(self.L[trunk][0][0].xy)
            acc, s0 = 0.0, None
            for a, b in zip(pts, pts[1:]):
                for j in range(20):
                    q = a.lerp(b, j / 20)
                    if s0 is None and (Vector(q.xy) - ax).length >= EXIT_R:
                        s0 = acc + (b - a).length * j / 20
                acc += (b - a).length
            self.exit[k] = s0 or 0.0

    def nearest(self, c):
        out = None
        for k, (pts, rad) in self.L.items():
            d, s, tot, i, t = _seg_param(c, pts)
            r = rad[i] + (rad[i + 1] - rad[i]) * t
            if out is None or d - r < out[1]:
                out = (k, d - r, s, tot)
        return out

    def u(self, k, c, s, tot):
        if k == self.trunk:
            return (c.z - SAND_LINE) / (TRUNK_TOP - SAND_LINE)
        if self.trunk is None:          # the sprig: along each limb from its root end
            return (s + 0.4) / (tot + CAP_BEVEL[0] + CAP_FAN + 0.4)
        e = self.exit[k]
        return (s - e) / max(1e-3, tot + CAP_BEVEL[0] + CAP_FAN - e)

    def cap_proj(self, k, c):
        pts, rad = self.L[k]
        t = (pts[-1] - pts[-2]).normalized()
        return (c - pts[-1]).dot(t)

    def gap_other(self, k, c):
        """Distance from c to the nearest OTHER limb's surface (negative inside)."""
        best = 9.0
        for j, (pts, rad) in self.L.items():
            if j == k:
                continue
            d, s, tot, i, t = _seg_param(c, pts)
            best = min(best, d - (rad[i] + (rad[i + 1] - rad[i]) * t))
        return best


def _sprig_limbs():
    st = [((SX + x, y, z), r) for (x, y, z), r in SPRIG_STEM]
    arm = [((SX + x, y, z), r) for (x, y, z), r in SPRIG_ARM]
    return {"stem": st, "arm": arm}


def _rim_z(c):
    """Socket 1's rim height round its edge, at the angle of c (interpolated between the hex corners)."""
    if "main" not in MOUND_INFO:
        _socket_geo("main")
    s = MOUND_INFO["main"]["rim"]
    cx, cy, R, depth, w, rot = SOCKETS["main"]
    ang = (math.degrees(math.atan2(c.y - cy, c.x - cx)) - rot) % 360.0
    k = int(ang // 60) % 6
    f = (ang - 60 * k) / 60
    return s[k] + (s[(k + 1) % 6] - s[k]) * f


class _RockPiece:
    """One placed rock: build frame -> its part's own frame, with the part's bounds there."""

    def __init__(self, label, part, m, seed):
        self.label = label
        self.inv = _frame(part) @ m.inverted()
        ps = [_frame(part) @ v.co for v in part.data.vertices]
        self.lo = Vector([min(p[i] for p in ps) for i in range(3)])
        self.hi = Vector([max(p[i] for p in ps) for i in range(3)])
        r = random.Random(seed)
        self.off = Vector((r.uniform(0, 50), r.uniform(0, 50), r.uniform(0, 50)))

    def local(self, c):
        return self.inv @ c

    def norm(self, c):
        q = self.local(c)
        mid, half = (self.lo + self.hi) / 2, (self.hi - self.lo) / 2
        return max(abs(q[i] - mid[i]) / max(half[i], 1e-6) for i in range(3))

    def u(self, c):
        q = self.local(c)
        return (q.z - self.lo.z) / (self.hi.z - self.lo.z)


def _tint(p, f, level, mottle, pos):
    """Tint = the piece's level x broad mottling (patches about 1/scale studs) x a little per-face jitter."""
    from mathutils import noise
    m = MOTTLE[mottle]
    r = random.Random(m["seed"])
    off = Vector((r.uniform(0, 100), r.uniform(0, 100), r.uniform(0, 100)))
    jit = random.Random(hash((round(pos.x, 3), round(pos.y, 3), round(pos.z, 3)))).uniform(-m["jitter"], m["jitter"]) \
        if m["jitter"] else 0.0
    k = level * (1.0 + m["amp"] * 1.6 * noise.noise(pos * m["scale"] + off) + jit)
    for l in f.loops:
        l[p.tint_layer] = (k, k, k, 1.0)


def _trees(p):
    """BVHs of the mesh's rock faces and sand faces (build frame)."""
    vs = [v.co + p.off for v in p.bm.verts]
    vi = {v: i for i, v in enumerate(p.bm.verts)}
    rock = [[vi[v] for v in f.verts] for f in p.bm.faces if _key_region(p.key(f)) == "rock"]
    sand = [[vi[v] for v in f.verts] for f in p.bm.faces if _key_region(p.key(f)) == "sand"]
    return (BVHTree.FromPolygons(vs, rock) if rock else None, BVHTree.FromPolygons(vs, sand) if sand else None)


def _rock_pieces():
    out = {}
    for k, (lab, (part, m)) in enumerate(placements().items()):
        if lab in ("Mound", "Branch"):
            continue
        out[lab] = _RockPiece(lab, bpy.data.objects[part], m, 16070 + k)
    return out


def colour(o, kind):
    """Stage 4 on a freshly built M016 object (its placeholder keys mark the regions). kind: hero, branch, sprig,
    mound, stone. Returns the face count per key."""
    from mathutils import noise
    p = m011._Paint(o, off=o[OFF])
    rock_t, sand_t = _trees(p)
    lm = _Limbs(_sprig_limbs()) if kind == "sprig" else _Limbs(limbs(), trunk="trunk")
    pieces = _rock_pieces() if kind == "hero" else {}
    generic = _RockPiece("stone", o, Matrix.Identity(4) @ _frame(o), 16069) if kind == "stone" else None
    lad = _crys_ladder()
    nf_c = K.noise_field(scale=CRYS_SCALE, seed=CRYS_SEED)
    nf_s = K.noise_field(scale=SAND_NOISE["scale"], seed=SAND_NOISE["seed"])
    keys0 = [(f, p.key(f)) for f in p.bm.faces]
    for f, key in keys0:
        reg = _key_region(key)
        c = p.at(f)
        floor = kind in ("hero", "mound", "stone") and all(abs(v.co.z) < 1e-3 for v in f.verts)
        if reg == "glass":
            k, gap, s, tot = lm.nearest(c)
            if kind in ("hero", "branch") and k == "trunk" and c.z < _rim_z(c) - 0.02:
                # in the pit: the dull root key; the buried root below the pit floor (the branch part only) half
                # way back to the deep crystal, so the part's root taper still reads as crystal
                below = c.z < min(MOUND_INFO["main"]["floor"]) - 0.1
                f.material_index = p._mi(K.mix_key(GLASS_ROOT, GLASS_DEEP, 0.5) if below else GLASS_ROOT)
            elif key == GLASS_CAP:
                fan = lm.cap_proj(k, c) > FAN_PROJ
                f.material_index = p._mi((GLASS_GLINT if kind in GLINT_KINDS else K.mix_key(GLASS_LIGHT, GLASS_GLINT,
                                                                                            0.5)) if fan else GLASS_LIGHT)
            else:
                u = lm.u(k, c, s, tot) + CRYS_NOISE * nf_c(c)
                if u < DEEP_BAND[1]:
                    i = round(_q((u - DEEP_BAND[0]) / (DEEP_BAND[1] - DEEP_BAND[0])) * 4)
                else:
                    i = 4 + round(_q((u - LIGHT_BAND[0]) / (LIGHT_BAND[1] - LIGHT_BAND[0])) * 4)
                if lm.gap_other(k, c) < CROTCH:
                    i = min(i, 2)
                f.material_index = p._mi(lad[i])
            _tint(p, f, 1.0, "glass", c)
            continue
        if reg == "sand":
            if key == SAND_PIT:
                f.material_index = p._mi(SAND_PIT)
            elif key == SAND_RIM:
                f.material_index = p._mi(K.mix_key(SAND, SAND_PIT, 0.5))
            elif floor:
                f.material_index = p._mi(SAND_DARK)
            else:
                td = 0.0
                for lim, t in SAND_FOOT:
                    if c.z < lim:
                        td = t
                        break
                if rock_t is not None:
                    d = rock_t.find_nearest(c)[3]
                    if d is not None and d < SAND_CONTACT[0]:
                        td = max(td, SAND_CONTACT[1])
                if td:
                    f.material_index = p._mi(K.mix_key(SAND, SAND_DARK, td))
                else:
                    tl = SAND_HEIGHT[2] * min(1.0, max(0.0, (c.z - SAND_HEIGHT[0]) / (SAND_HEIGHT[1] - SAND_HEIGHT[0])))
                    if nf_s(c) > SAND_NOISE["level"]:
                        tl += SAND_NOISE["add"]
                    f.material_index = p._mi(K.mix_key(SAND, SAND_LIGHT, _q(tl)))
            _tint(p, f, 1.0, "sand", c)
            continue
        # rock
        pc = generic or min(pieces.values(), key=lambda x: x.norm(c))
        u = pc.u(c)
        q = pc.local(c)
        if floor:
            f.material_index = p._mi(ROCK_DARK)
        else:
            td = 0.5 if u < ROCK_GROUND and sand_t is not None else 0.0
            if sand_t is not None and u < ROCK_CROWN:
                d = sand_t.find_nearest(c)[3]
                if d is not None and d < ROCK_CONTACT:
                    td = 0.5
            if td:
                f.material_index = p._mi(K.mix_key(ROCK, ROCK_DARK, td))
            else:
                nv = noise.noise(q * ROCK_NOISE["scale"] + pc.off)
                ta = ACCENT_ROCKS.get(pc.label, 0.0)
                if nv > ROCK_NOISE["level2"]:
                    ta += 1.0
                elif nv > ROCK_NOISE["level"]:
                    ta += 0.5
                f.material_index = p._mi(K.mix_key(ROCK, ROCK_ACCENT, _q(ta)))
        _tint(p, f, PIECE_TINT.get(pc.label, 1.0), "rock", q + pc.off)
    counts = {}
    for f in p.bm.faces:
        counts[p.key(f)] = counts.get(p.key(f), 0) + 1
    p.done()
    _glass_spec()
    return counts


SHADING_OK = {"StormglassStone": "the flat underside is the rock's ground-contact tone (ROCK_DARK), chosen by "
                                   "position (the part's flat bottom, z = 0), not by light; the hero's floor cap is "
                                   "the same"}
KINDS = {"StormglassNode": "hero", "StormglassBranch": "branch", "StormglassSprig": "sprig",
         "StormglassMound": "mound", "StormglassStone": "stone"}


def colour_all(objs):
    out = {o.name: colour(o, KINDS.get(o.name, "stone")) for o in objs}
    for o in objs:
        if o.name in SHADING_OK:
            o["kit_shading_ok"] = SHADING_OK[o.name]
        elif "kit_shading_ok" in o:
            del o["kit_shading_ok"]
    return out


# ---- stage 4 measurement: our renders against the sheet, per region --------------------------------------------------
SHEET_PATH = "D:/Projects/Roblox/RBLX-Flintborn/art/blender/assets/references/016.png"
SHEET_BOXES = {"f34": (25, 131, 450, 468), "r34": (452, 110, 795, 468), "front": (30, 545, 279, 728),
               "side": (283, 545, 510, 728), "rear": (513, 545, 762, 728), "top": (766, 545, 1018, 728)}
REPORT_VIEWS = {"front": ("front_sheet", 0, 9), "side": ("side_sheet", 90, 9), "rear": ("rear_sheet", 180, 9),
                "f34": ("f34_near", -15, 12), "r34": ("r34_near", 165, 12), "top": ("top", 0, 89)}
LABEL_RGB = {"crystal": (0.0, 0.0, 1.0), "sand": (1.0, 0.0, 0.0), "pit": (0.0, 1.0, 0.0), "rock": (1.0, 0.0, 1.0)}
REPORT_DIR = "C:/Users/Orang/AppData/Local/Temp/claude/D--Projects-Roblox-RBLX-Flintborn/m016_s4"


def _label_of(key):
    r = _key_region(key)
    if r == "sand" and "pit" in key:
        return "pit"
    return {"glass": "crystal", "sand": "sand", "rock": "rock"}[r]


def _label_render(o, path, az, el):
    """o rendered with flat emission label colours (same verts, so the same framing as its colour render)."""
    keys = [(m.get("flintkit_key") or m.name[3:]) for m in o.data.materials]
    me = o.data.copy()
    tmp = bpy.data.objects.new("_m016_labels", me)
    o.users_collection[0].objects.link(tmp)
    tmp.matrix_world = o.matrix_world
    names = list(LABEL_RGB)
    idx = [names.index(_label_of(keys[p.material_index])) for p in me.polygons]
    mats = []
    try:
        me.materials.clear()
        for name, rgb in LABEL_RGB.items():
            m = bpy.data.materials.new("_m016_label_" + name)
            m.use_nodes = True
            nt = m.node_tree
            nt.nodes.clear()
            em = nt.nodes.new("ShaderNodeEmission")
            em.inputs["Color"].default_value = (*rgb, 1.0)
            out = nt.nodes.new("ShaderNodeOutputMaterial")
            nt.links.new(em.outputs[0], out.inputs[0])
            me.materials.append(m)
            mats.append(m)
        me.polygons.foreach_set("material_index", idx)
        return K.NS["KIT"]["render_group"]([tmp], path, az, el)
    finally:
        bpy.data.objects.remove(tmp, do_unlink=True)
        bpy.data.meshes.remove(me)
        for m in mats:
            bpy.data.materials.remove(m)


def _label_mask(px):
    c = px[..., :3]
    mx = c.max(axis=2)
    n = c / np.maximum(mx, 1e-4)[..., None]
    sat = (mx - c.min(axis=2)) / np.maximum(mx, 1e-4)
    best, bd = np.full(mx.shape, -1), np.full(mx.shape, 9.0)
    for i, rgb in enumerate(LABEL_RGB.values()):
        d = np.abs(n - np.array(rgb)).max(axis=2)
        upd = d < bd
        best[upd], bd[upd] = i, d[upd]
    ok = (mx > 0.15) & (sat > 0.6) & (bd < 0.45)
    out = {}
    for i, name in enumerate(LABEL_RGB):
        m = ok & (best == i)
        e = m.copy()
        e[1:, :] &= m[:-1, :]
        e[:-1, :] &= m[1:, :]
        e[:, 1:] &= m[:, :-1]
        e[:, :-1] &= m[:, 1:]
        out[name] = e
    return out


def _hexs(c):
    return "#" + "".join(f"{int(round(x)):02X}" for x in c)


def _stats(sel):
    if len(sel) < 20:
        return None
    lum = sel.mean(axis=1)
    lo, hi = np.percentile(lum, 25), np.percentile(lum, 75)
    return (_hexs(np.median(sel, axis=0)), _hexs(np.median(sel[lum >= hi], axis=0)),
            _hexs(np.median(sel[lum <= lo], axis=0)), int(len(sel)))


def _bands(img, mask, n=5):
    rows = np.nonzero(mask.any(axis=1))[0]
    if not len(rows):
        return []
    r0, r1 = rows.min(), rows.max() + 1
    out = []
    for k in range(n):
        a, b = r0 + (r1 - r0) * k // n, r0 + (r1 - r0) * (k + 1) // n
        sel = img[a:b][mask[a:b]]
        out.append(_hexs(np.median(sel, axis=0)) if len(sel) else None)
    return out


def _top_down(px):
    return (np.clip(px[::-1, :, :3], 0, 1) * 255).astype(np.float64)


def _sheet_masks(c):
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    mx, mn = c.max(axis=2), c.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1)
    mean = c.mean(axis=2)
    cr = (g > r + 35) & (b > r + 30)
    sd = ~cr & (r - b >= 36) & (sat >= 0.2) & (mean >= 95)
    rk = ~cr & ~sd & (mean < 225)
    return {"crystal": cr, "sand": sd, "rock": rk}


def sheet_stats():
    img = _top_down(K.NS["KIT"]["load_px"](SHEET_PATH))
    out = {}
    for v, (x0, y0, x1, y1) in SHEET_BOXES.items():
        c = img[y0:y1, x0:x1]
        m = _sheet_masks(c)
        out[v] = {k: _stats(c[mk]) for k, mk in m.items()}
        out[v]["crystal_bands"] = _bands(c, m["crystal"])
    return out


def report(views=None, out_dir=None):
    """Render the hero (colour + labels) at the sheet's views and measure each region (median, lit, shade, n) against
    the sheet's same region (study masks). Returns {view: {region: (ours, sheet)}}."""
    import os
    h = bpy.data.objects["StormglassNode"]
    out_dir = out_dir or REPORT_DIR
    os.makedirs(out_dir, exist_ok=True)
    kit = K.NS["KIT"]
    old = kit["CELL"]
    kit["CELL"] = (480, 400)
    sh = sheet_stats()
    out = {}
    try:
        for v, (name, az, el) in (views or REPORT_VIEWS).items():
            pc = kit["render_group"]([h], f"{out_dir}/{name}.png", az, el)
            pl = _label_render(h, f"{out_dir}/{name}_lab.png", az, el)
            img = _top_down(kit["load_px"](pc))
            masks = _label_mask(kit["load_px"](pl)[::-1])
            r = {k: (_stats(img[m]), sh[v].get(k)) for k, m in masks.items()}
            r["crystal_bands"] = (_bands(img, masks["crystal"]), sh[v]["crystal_bands"])
            out[v] = r
    finally:
        kit["CELL"] = old
    return out


# ---- stages 5 + 6: lighting and VFX (M016_spec.md §7 and the main session's decision 6) ----------------------------
# Stage 5: nothing. The sheet's crystal is lit, not luminous (its shade facets go dark teal, no spill on the sand), so no
# key has emission (no Neon: it would flatten the deep -> body -> light gradient into one unlit colour) and no light.
# Stage 6: three low-rate ore_glint sockets, one just above each cap's fan centre (the sheet's palest facets), the
# resource-node sparkle every crystal node carries. A flat box over the cap (Roblox XYZ: x, height, depth).
GLINT = {"name": "Glint", "texture": "spark_diamond", "color": ["#E8FFFC", "#62EAEC"], "size": [0, 0.45, 0],
         "transparency": [0.1, 1.0], "lifetime": [0.5, 0.8], "speed": [0, 0], "spread": 0, "light_emission": 1.0,
         "rotation": [0, 90], "shape": [1.2, 0.3, 1.2]}
GLINT_RATE = (0.4, 0.3, 0.3)            # trunk cap, right cap, left cap (the trunk's cap is the biggest)
# the box centre this far above the fan centre, along the cap's axis: the boxes are world-flat but the caps tilt
# 33-41 deg, so at 0.12 with a 1.6 x 0.6 box 272 of 1029 grid points sat inside the crystal; 0.6 with 1.2 x 0.3 leaves 1
GLINT_LIFT = 0.6


def glint_points():
    """The three cap fan centres plus GLINT_LIFT along each cap's axis, in the build frame (trunk, right, left)."""
    L = limbs()
    out = []
    for k in ("trunk", "right", "left"):
        pts = [Vector(p) for p, _ in L[k]]
        t = (pts[-1] - pts[-2]).normalized()
        out.append(pts[-1] + t * (CAP_BEVEL[0] + CAP_FAN + GLINT_LIFT))
    return out


def _vfx(h):
    off = Vector(h[OFF])
    made = []
    for p, rate in zip(glint_points(), GLINT_RATE):
        made.append(K.socket(h, "ore_glint", [round(c, 3) for c in p - off], emitters=[dict(GLINT, rate=rate)]))
    return made


# ---- build ------------------------------------------------------------------------------------------------------
PARTS = (("StormglassBranch", branch), ("StormglassSprig", sprig), ("StormglassMound", mound),
         ("StormglassStone", stone))


def _variants():
    """The build-only rock variants B-D as throwaway objects in _wip (their meshes are pasted into the hero)."""
    out = {}
    for v in ("B", "C", "D"):
        name = f"_m016_stone_{v.lower()}"
        o = K.test_asset(name, VARIANT_FN[v])
        o.location = (0, 0, 0)
        o[OFF] = list(M._build_offset(VARIANT_FN[v]))
        out[v] = o
    return out


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith("_m016_"):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)


def build(render=True, stage=1):
    M.coll(NUM, TITLE)
    palette()
    MOUND_INFO.clear()
    objs, log = {}, {}
    for name, fn in PARTS:
        o = M.mk(SHEET, name, fn, subject=TITLE, role="part", notes=NOTES[name], budget=1000, collision="hull")
        o[OFF] = list(M._build_offset(fn))
        lg = {}
        if fn in (branch, sprig):
            M.union_loose(o)
            lg["clean"] = _clean_mesh(o, ())
        if fn is mound:
            _sockets(o)
            _carve_fn(o, pockets)
            lg["clean"] = _clean_mesh(o, (0.0,))          # the flat bottom (mesh z 0)
        lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
        lg["polish"] = _polish(o)
        log[name] = lg
        objs[name] = o
    _variants()
    h = M.mk(SHEET, "StormglassNode", hero, subject=TITLE, role="hero", notes=NOTES["StormglassNode"], budget=4000,
             collision="hull")
    hoff = M._build_offset(hero)
    h[OFF] = list(hoff)
    M.union_loose(h)
    _floor_cut(h, -hoff.z)
    h[OFF] = list(Vector((hoff.x, hoff.y, 0.0)))
    _carve_fn(h, pockets)
    log["hero"] = {"clean": _clean_mesh(h, (0.0,))}
    log["hero"]["finish"] = {k: v for k, v in _finish(h).items() if k in ("tris", "nonmanifold_edges")}
    log["hero"]["polish"] = _polish(h)
    order = [h] + [objs[n] for n, _ in PARTS]
    coloured = colour_all(order)        # stage 4 (colour only), the hero first, while the rock variants exist
    sockets = _vfx(h)                   # stage 6, on the finished hero (the parts carry none)
    _cleanup_tmp()
    M.display(NUM, order, TITLE)
    out = {"audit": [{k: M.audit(o)[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges",
                                                     "boundary_edges", "normals", "ngons", "materials")}
                     for o in order],
           "thin": {o.name: m012._thin(o, 3.0) for o in order}, "log": log, "mound": dict(MOUND_INFO),
           "stones": dict(STONE_INFO), "self_hits": {o.name: _self_hits(o)[0] for o in order},
           "measure": measure(h), "socket": socket_gap(h), "colour": coloured, "problems": K.check(order),
           "sockets": [(s.name, s["vfx_kind"], [round(c, 3) for c in s.location]) for s in sockets],
           "uv": {o.name: M.uv_stats(o) for o in order}}
    if render:
        out["views"] = render_views(order)
    return out


EXPLODE = {"Branch": (0.0, 0.0, 4.5), "R1": (-1.6, -1.8, 0.6), "R9": (-1.4, 1.2, 1.4), "R4": (1.6, -1.0, 0.4),
           "R6": (1.6, 0.6, 1.2), "T1": (0.4, -1.6, 2.0), "T2": (-0.4, 1.0, 2.6), "R11": (-1.8, -0.4, 0.3)}


def render_views(objs):
    h = objs[0]
    parts = objs[1:]
    saved = M.explode(parts, {})
    shown = []
    try:
        x0, y0 = h.location.x + 40, h.location.y
        for o in _variants().values():
            colour(o, "stone")
        for name, (part, m) in placements().items():
            src = bpy.data.objects[part]
            c = bpy.data.objects.new(f"_m016_expl_{name}", src.data)
            h.users_collection[0].objects.link(c)
            c.matrix_world = Matrix.Translation(Vector((x0, y0, 0.0)) + Vector(EXPLODE.get(name, (0, 0, 0)))) @ m
            shown.append(c)
        for v in ("b", "c", "d"):
            o = bpy.data.objects.get(f"_m016_stone_{v}")
            if o:
                o.hide_render = True
        bpy.context.view_layer.update()
        extra = {"front_sheet": ([h], 0, 9), "side_sheet": ([h], 90, 9), "rear_sheet": ([h], 180, 9),
                 "f34_near": ([h], -15, 12), "r34_near": ([h], 165, 12), "top_tilt": ([h], -20, 70),
                 "junction": ([h], -20, 35), "exploded": (shown, -12, 14)}
        for o in parts:
            extra["part_" + o.name.replace("Stormglass", "").lower()] = ([o], -20, 15)
        return M.views(NUM, [h], extra=extra)
    finally:
        for c in shown:
            bpy.data.objects.remove(c, do_unlink=True)
        _cleanup_tmp()
        M.restore(saved)
        M.display(NUM, objs, TITLE)
