"""021 Root Cluster (references/021.png): a low lumpy faceted dirt/rock mound with three thick warm-orange root
modules draped over it from a crown just behind the centre - root A an inverted J/V whose knee lies on the crown and
whose two legs run down the front-left and the left flank, roots B and C one forked module (a blunt bark stub at the
crown, C down the front-right, B arching off C's back and down the back-right) - every root end that reaches the
ground a tapered pale cut-wood tip with a slanted collar and a ringed end face, and three bright eight-leaf modules
in the crevices at the crown.

    import importlib, kit_models, m021; importlib.reload(kit_models); importlib.reload(m021); m021.build()

Parts as on the sheet's Exploded Construction, each built by its own function, all in one shared build frame (studs;
front -Y, +X right, ground z = 0, the mound's plan centre at the origin). R06 owns RootCluster*, so the names are
ArchedRootCluster* (M021_spec.md section 8, main-session decision 11):
- ArchedRootClusterMound: Dirt Mound (Base). One lofted 22-gon dome (a broad rounded dome with sloping flanks)
  whose dirt lumps are broad deliberate swellings (every LUMPS entry not in ROCK_LUMPS), three small crevice stones
  bedded along the dome's normal (STONES: crown, upper-left, front-shoulder, each about 0.3 proud), three foot
  boulders (front foot, pebble, left foot) and any root SUPPORTS (low pads, at most SUPPORT_MAX proud; with the
  round-2 conform none are needed), fused by exact unions, cut flat at the ground, near-coplanar faces dissolved.
  Round 2 (M021_spec.md "Round 2 fixes"): the round-1 build's flank hull rocks read as a rock pile.
- ArchedRootClusterRootA: Root Module (A), one 10-sided faceted tube along a Catmull-Rom path from tip to tip, the
  knee on the crown; each end a tapered pale cut tip (slanted collar, small flat end face with one cut_ring loop).
- ArchedRootClusterRootFork: Root Modules (B) + (C), one forked piece: C from a blunt domed bark stub at the crown to
  its tip, B (9 sides) springing from C just past the stub, arching up and down to its own tip.
- ArchedRootClusterLeafModule: eight broad kite leaves round a small dark hub.

The roots' centre lines are read off the sheet's hero view. They are laid on the fused mound: each ring station that
lies on (or within CONFORM_REACH of) the mound is moved along the root's own local down until its underside sinks
ROOT_SINK of its diameter into it; where a root would float, plan_supports() adds a flat-topped support under it and
the mound is fused again ("Roots sit on flat joining surfaces on the rock base", spec section 3.6). The hero (ArchedRootCluster) pastes the fused mound, root A, the fused fork and three fused leaf
modules and unions them one shell at a time, then cuts the floor and cleans up. Colour (stage 4) is painted by
position fields inside the builders (and the root-contact darkening on the fused mound), before the union; the
union and cleanup keep each face's key and Tint. See M021_spec.md.
"""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M
import m004
import m011
import m012
import m016

NUM, TITLE, SHEET = 21, "Root Cluster", "M021"
OFF = "m021_offset"
PFX = "_m021_"

BARK, BARK_DARK, BARK_LIGHT = "m021_bark", "m021_bark_dark", "m021_bark_light"
CUT, CUT_RING = "m021_cut", "m021_cut_ring"
MOUND, STONE, MOUND_DARK = "m021_mound", "m021_stone", "m021_mound_dark"
LEAF, LEAF_TIP, LEAF_BASE, STEM = "m021_leaf", "m021_leaf_tip", "m021_leaf_base", "m021_stem"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low_spec). Stage 4: calibrate() pass 1 on the kit dome against TARGETS, then pass 2 on the
# hero renders against the sheet's f34 region medians ("Stage 4" in M021_spec.md).
PALETTE = {BARK: ("#875736", 0.9, False), BARK_DARK: ("#694025", 0.92, False), BARK_LIGHT: ("#A66C46", 0.9, False),
           CUT: ("#B69B7E", 0.85, False), CUT_RING: ("#B1926C", 0.85, False),
           MOUND: ("#694E42", 0.95, False), STONE: ("#8C7971", 0.9, False), MOUND_DARK: ("#594139", 0.95, False),
           LEAF: ("#558B1B", 0.8, True), LEAF_TIP: ("#74A525", 0.8, True), LEAF_BASE: ("#467D11", 0.8, True),
           STEM: ("#2A1406", 0.9, False)}

# calibration targets: the sheet's rendered medians of unshadowed regions (spec section 5.4). key -> (sRGB, kind)
TARGETS = {BARK: ((0x96, 0x5C, 0x3C), "brown"), BARK_DARK: ((0x83, 0x51, 0x33), "brown"),
           BARK_LIGHT: ((0xA5, 0x68, 0x45), "brown"),
           CUT: ((0xE4, 0xBA, 0x8B), "all"), CUT_RING: ((0xE2, 0xAE, 0x76), "all"),
           MOUND: ((0x7F, 0x5F, 0x50), "all"), STONE: ((0x8A, 0x6E, 0x62), "all"),
           MOUND_DARK: ((0x6B, 0x51, 0x45), "all"),
           LEAF: ((0x52, 0x90, 0x20), "green"), LEAF_TIP: ((0x74, 0xAE, 0x2C), "green"),
           LEAF_BASE: ((0x42, 0x81, 0x16), "green"), STEM: ((0x3A, 0x23, 0x12), "all")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)


def calibrate(keys=None, iters=6, out_dir=None):
    """Pass 1: K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome. "all" keys are sampled with
    the paper/floor dropped (M.sample). Returns {key: (hex, rendered)}."""
    keys = keys or list(TARGETS)
    sample0 = K.sample

    def sample(src, box, kind="green"):
        return M.sample(src, box, "all", paper=(242, 238, 230), tol=14) if kind == "all" else sample0(src, box, kind)
    K.sample = sample
    try:
        for k in keys:
            K.fk().material(k)
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        K.sample = sample0
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


# ---- colour helpers ---------------------------------------------------------------------------------------------------
STEPS = 3


def _q(t):
    return round(min(1.0, max(0.0, t)) * (STEPS + 1)) / (STEPS + 1)


def _ladder(lo, mid, hi):
    """lo, three lo->mid mixes, mid, three mid->hi mixes, hi (9 keys)."""
    return ([lo] + [K.mix_key(lo, mid, t) for t in (0.25, 0.5, 0.75)] + [mid] +
            [K.mix_key(mid, hi, t) for t in (0.25, 0.5, 0.75)] + [hi])


def _pick(lad, v, low, high):
    if v < (low[1] + high[0]) / 2:
        return lad[round(_q((v - low[0]) / (low[1] - low[0])) * 4)]
    return lad[4 + round(_q((v - high[0]) / (high[1] - high[0])) * 4)]


def _mottle(a, faces, amp, scale, seed, jitter=0.0, at=None):
    """Broad Tint patches about 1/scale studs across (never per-triangle confetti). at(f) -> build-frame centre."""
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in faces:
        c = at(f) if at else f.calc_center_median()
        k = 1.0 + amp * 1.6 * noise.noise(c * scale + off) + (rng.uniform(-jitter, jitter) if jitter else 0.0)
        for l in f.loops:
            t = l[a.tint_layer][0] * k
            l[a.tint_layer] = (t, t, t, 1.0)


# ---- geometry helpers -------------------------------------------------------------------------------------------------
def _perp(t):
    a = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
    return (a - t * a.dot(t)).normalized()


def _strip(bm, r0, r1):
    n = len(r0)
    return [bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k])) for k in range(n)]


def _fan(bm, ring, c, flip=False):
    n = len(ring)
    return [bm.faces.new((ring[(k + 1) % n], ring[k], c) if not flip else (ring[k], ring[(k + 1) % n], c))
            for k in range(n)]


def _tri(bm, faces):
    bmesh.ops.triangulate(bm, faces=[f for f in faces if f.is_valid and len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")


def _faces(verts):
    return K.faces_of([v for v in verts if v.is_valid])


def _align(z_axis, yaw=0.0):
    z = Vector(z_axis).normalized()
    return z.to_track_quat("Z", "Y").to_matrix() @ Matrix.Rotation(math.radians(yaw), 3, "Z")


# ---- Dirt Mound (Base) ------------------------------------------------------------------------------------------------
CORE = dict(c=(0.0, 0.2), rx=3.8, ry=3.4, n=10, seed=21001, top=3.45, jit=0.06)
# (z, radius fraction) from the buried base up; the top vertex at CORE["top"]. A full dome: the roots lie on it
# everywhere (they sag into the valleys of a low one)
CORE_RINGS = ((-0.3, 1.0), (0.5, 0.98), (1.35, 0.9), (2.2, 0.75), (2.9, 0.5))
# lumps: (centre x, y, footprint x, y, top z, height, seed, yaw deg, stone fraction (0 dirt, 1 stone top), lean).
# Broad hull rocks (the sheet's mound is a dome of overlapping big lumps with broad facets), each standing only
# 0.3-0.55 proud of the core's envelope and leaning outward with the slope (lean x the plan radius, radians), so the
# dome's outline stays round and the lumps show as broad faceted swellings with shallow creases between them.
# Base z = top - height: all differ (no coplanar buried bottoms); bases under the ground go with the floor cut.
LUMPS = {
    "crown": ((0.1, 0.5), (3.0, 2.6), 3.75, 1.5, 21011, 10.0, 1.0, 0.0),
    "upper_left": ((-1.85, -1.65), (1.7, 1.5), 3.4, 1.15, 21012, 35.0, 1.0, 0.45),
    "upper_right": ((2.2, 1.0), (2.4, 2.3), 2.9, 1.52, 21022, 70.0, 0.0, 0.45),
    "left_foot": ((-4.0, -0.95), (2.0, 1.8), 1.45, 1.62, 21025, 60.0, 0.0, 0.0),
    "front_shoulder": ((1.35, -1.55), (1.4, 1.2), 2.9, 0.95, 21013, 5.0, 1.0, 0.9),
    "front_left": ((-1.9, -2.0), (2.4, 2.2), 2.15, 2.26, 21023, 20.0, 0.0, 0.5),
    "front_right": ((2.3, -1.9), (2.4, 2.2), 1.95, 2.08, 21024, 45.0, 0.0, 0.5),
    "front_foot": ((0.0, -3.45), (2.2, 1.5), 1.0, 1.25, 21014, 0.0, 0.25, 0.0),
    "pebble": ((-3.4, -2.45), (1.1, 1.0), 0.7, 0.9, 21015, 20.0, 1.0, 0.0),
    "left_shoulder": ((-2.9, -0.35), (2.2, 2.2), 1.75, 1.93, 21016, 15.0, 0.0, 0.45),
    "left_back_foot": ((-3.4, 1.9), (1.4, 1.4), 0.9, 1.12, 21017, 40.0, 0.0, 0.0),
    "right_front": ((3.4, -0.4), (2.2, 2.2), 1.65, 1.83, 21018, 25.0, 0.0, 0.35),
    "right_back": ((3.3, 1.3), (2.0, 2.0), 1.15, 1.42, 21019, 55.0, 0.0, 0.3),
    "back_left": ((-1.2, 2.6), (2.6, 2.4), 2.45, 2.69, 21020, 30.0, 0.0, 0.35),
    "back_right": ((1.4, 2.8), (2.2, 2.0), 2.0, 2.21, 21021, 50.0, 0.0, 0.35),
}
# the whole mound's plan scaled about the core centre (lump centres, core radii) and the lumps' footprints: the root
# tips run out past the base outline as on the sheet's underside view
MOUND_SXY, MOUND_SY, MOUND_SIZE = 0.96, 0.97, 0.95   # round 2: x 0.9 -> 0.96 (the hero's width, 9.4 +- 0.4)     # plan scale in x, in y, lump footprints
LUMP_RINGS = [(0.0, 1.0, 5), (0.38, 0.88, 5), (0.74, 0.64, 4), (1.0, 0.32, 3)]
SMALL_RINGS = [(0.0, 1.0, 5), (0.5, 0.84, 4), (1.0, 0.42, 3)]
# the front foot boulder is a flat-topped trapezoid on the sheet (broad top facet, sloping sides)
LUMP_SHAPE = {"front_foot": [(0.0, 1.0, 7), (0.5, 0.86, 6), (1.0, 0.58, 5)],
              # round 2: the small crevice stone between A and C, a low rounded top (no point)
              "front_shoulder": [(0.0, 1.0, 6), (0.5, 0.92, 6), (0.85, 0.7, 5), (1.0, 0.4, 3)],
              "crown": [(0.0, 1.0, 6), (0.45, 0.9, 6), (0.8, 0.7, 5), (1.0, 0.45, 4)]}
MOUND_INFO = {}


def _sector(th, seed):
    r = random.Random(seed)
    p1, p2, p3 = r.uniform(0, 6.3), r.uniform(0, 6.3), r.uniform(0, 6.3)
    return 1.0 + 0.035 * math.sin(3 * th + p1) + 0.025 * math.sin(5 * th + p2) + 0.02 * math.sin(2 * th + p3)


def _core(a):
    m = CORE
    rng = random.Random(m["seed"])
    bm = a.bm
    cx, cy = m["c"]
    rings = []
    for i, (z, rf) in enumerate(CORE_RINGS):
        n = m["n"]
        off = (math.pi / n) * (i % 2) + rng.uniform(-0.05, 0.05)
        ox, oy = (0.0, 0.0) if i == 0 else (rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15))
        ring = []
        for k in range(n):
            th = off + 2 * math.pi * k / n + rng.uniform(-0.07, 0.07)
            j = _sector(th, m["seed"] + i // 2) * (1 + rng.uniform(-m["jit"], m["jit"]))
            dz = 0.0 if i == 0 else rng.uniform(-0.08, 0.08)
            ring.append(bm.verts.new((cx + ox + math.cos(th) * m["rx"] * MOUND_SXY * rf * j,
                                      cy + oy + math.sin(th) * m["ry"] * MOUND_SY * rf * j, z + dz)))
        rings.append(ring)
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        faces += _strip(bm, r0, r1)
    bot = bm.verts.new((cx, cy, CORE_RINGS[0][0] - 0.02))
    top = bm.verts.new((cx + 0.1, cy - 0.05, m["top"]))
    faces += _fan(bm, rings[0], bot, flip=True)
    faces += _fan(bm, rings[-1], top)
    _tri(bm, faces)
    vs = [v for r in rings for v in r] + [bot, top]
    a._finish(vs, MOUND)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    return vs


def _lump(a, name):
    (x, y), (sx, sy), top, height, seed, yaw, stone, lean = LUMPS[name]
    cx, cy = CORE["c"]
    x, y = cx + (x - cx) * MOUND_SXY, cy + (y - cy) * MOUND_SY
    sx, sy = sx * MOUND_SIZE, sy * MOUND_SIZE
    base = top - height
    rings = LUMP_SHAPE.get(name) or (SMALL_RINGS if max(sx, sy) < 1.5 else LUMP_RINGS)
    d = Vector((x - cx, y - cy))
    rho = math.hypot(d.x / (CORE["rx"] * MOUND_SXY), d.y / (CORE["ry"] * MOUND_SY))
    d = d.normalized() if d.length > 1e-6 else Vector((0, 0))
    ang = lean * rho
    # hull_rock builds at the origin (base z 0), rotates (yaw, then the tilt) and then translates to loc
    vs = K.hull_rock(a, (sx, sy, height), loc=(x, y, base), seed=seed, mat=MOUND, rings=rings, jitter=0.12,
                     rot=math.radians(yaw), keep_bottom=True, tilt=(-ang * d.y, ang * d.x))
    MOUND_INFO[name] = {"centre": (x, y), "top": max(v.co.z for v in vs), "base": max(base, 0.0), "stone": stone}
    return vs


# mound colour fields (spec section 5.5)
MOUND_FIELD = dict(stone_from=0.4, stone_to=0.75, ground=0.35, ground_mix=0.4, patch_scale=0.55, patch_level=0.22,
                   patch_mix=0.25, seed=21031, upper_z=2.4)
TOP_GREY = (2.75, 3.3)
MOUND_MOTTLE = dict(amp=0.06, scale=0.6, seed=21032, jitter=0.012)


def _paint_lump(a, vs, name):
    info = MOUND_INFO[name]
    if not info["stone"]:
        return
    z0, z1 = info["base"], info["top"]
    lim = info["stone"]
    for f in _faces(vs):
        h = (f.calc_center_median().z - z0) / max(1e-3, z1 - z0)
        t = (h - MOUND_FIELD["stone_from"]) / (MOUND_FIELD["stone_to"] - MOUND_FIELD["stone_from"])
        t = _q(min(lim, max(0.0, t)))
        if t:
            f.material_index = a._mi(K.mix_key(MOUND, STONE, t))


def _paint_mound(a, vs):
    """Ground band darker (dirt meeting the ground), broad lighter stone-mix patches on the upper dome."""
    nf = K.noise_field(scale=MOUND_FIELD["patch_scale"], seed=MOUND_FIELD["seed"])
    mi_mound = a._mi(MOUND)
    for f in _faces(vs):
        if f.material_index != mi_mound:
            continue
        c = f.calc_center_median()
        if c.z < MOUND_FIELD["ground"]:
            f.material_index = a._mi(K.mix_key(MOUND, MOUND_DARK, _q(MOUND_FIELD["ground_mix"])))
            continue
        # round 2: the dome's upper part greys toward the stone key with height (the sheet's exploded mound: top
        # fifth sat .30 against .38 in the middle), 25 % from TOP_GREY[0] up to 50 % at TOP_GREY[1]
        tg = 0.0
        if c.z > TOP_GREY[0]:
            tg = _q(0.25 + 0.25 * min(1.0, (c.z - TOP_GREY[0]) / (TOP_GREY[1] - TOP_GREY[0])))
        if c.z > MOUND_FIELD["upper_z"] * 0.6 and nf(c) > MOUND_FIELD["patch_level"]:
            tg = max(tg, _q(MOUND_FIELD["patch_mix"]))
        if tg:
            f.material_index = a._mi(K.mix_key(MOUND, STONE, tg))


# The dome: one lofted shell whose dirt lumps are broad deliberate swellings (each LUMPS entry not in ROCK_LUMPS
# becomes a bump of DOME_BUMP studs, about its footprint across), so the mound reads as the sheet's rounded lumpy
# earth dome with broad facets instead of a pile of separate boulders; only the stones and foot rocks stay hull rocks.
# round 2: a finer loft (22 around, 9 rings: facets about 0.7-1.0 stud as on the sheet) with a little more radial and
# height jitter, so the broad facets break into slightly different planes
DOME = dict(n=22, seed=21002, top=3.45, jit=0.06, dz=0.12, src=(0.0, 0.2, -1.5))
DOME_RINGS = ((-0.3, 1.0), (0.25, 0.975), (0.7, 0.93), (1.15, 0.87), (1.6, 0.79), (2.05, 0.7), (2.5, 0.59),
              (2.9, 0.46), (3.2, 0.31), (3.4, 0.15))     # round 2: a broad rounded dome with sloping flanks
DOME_BUMP = 0.65
# the flank swellings at the sheet's left and right edges (f34 f .0-.1 and .9-1.0, h .2-.5) stand out further
BUMP_AMP = {"right_front": 0.85, "left_shoulder": 0.95}
# round 2: only the two crevice stones, the small front-shoulder crevice stone and the three foot boulders stay hull
# rocks; front_left, front_right, left_shoulder and right_front became dome bumps (the verifier's "rock pile")
ROCK_LUMPS = ("crown", "upper_left", "front_shoulder", "front_foot", "pebble", "left_foot")


def _bumps():
    cx, cy = CORE["c"]
    out = []
    for name, ((x, y), (sx, sy), top, height, seed, yaw, stone, lean) in LUMPS.items():
        if name in ROCK_LUMPS:
            continue
        x, y = cx + (x - cx) * MOUND_SXY, cy + (y - cy) * MOUND_SY
        out.append((Vector((x, y)), 0.36 * min(sx, sy) * MOUND_SIZE, BUMP_AMP.get(name, DOME_BUMP)))
    return out


def _dome(a):
    m = DOME
    rng = random.Random(m["seed"])
    bm = a.bm
    cx, cy = CORE["c"]
    src = Vector(m["src"])
    bumps = _bumps()
    rings = []
    for i, (z, rf) in enumerate(DOME_RINGS):
        n = m["n"]
        off = (math.pi / n) * (i % 2) + rng.uniform(-0.04, 0.04)
        ring = []
        for k in range(n):
            th = off + 2 * math.pi * k / n + rng.uniform(-0.06, 0.06)
            j = _sector(th, CORE["seed"] + i // 3) * (1 + rng.uniform(-m["jit"], m["jit"]))
            p = Vector((cx + math.cos(th) * CORE["rx"] * MOUND_SXY * rf * j,
                        cy + math.sin(th) * CORE["ry"] * MOUND_SY * rf * j,
                        z + (0.0 if i == 0 else rng.uniform(-m["dz"], m["dz"]))))
            amp = sum(A * math.exp(-((p.xy - c).length_squared) / (2 * s * s)) for c, s, A in bumps)
            d = (p - src).normalized()
            if i == 0:
                d = Vector((d.x, d.y, 0.0)).normalized()
            ring.append(bm.verts.new(p + d * amp))
        rings.append(ring)
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        faces += _strip(bm, r0, r1)
    bot = bm.verts.new((cx, cy, DOME_RINGS[0][0] - 0.02))
    top = bm.verts.new((cx + 0.1, cy - 0.05, m["top"]))
    faces += _fan(bm, rings[0], bot, flip=True)
    faces += _fan(bm, rings[-1], top)
    _tri(bm, faces)
    vs = [v for r in rings for v in r] + [bot, top]
    a._finish(vs, MOUND)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    return vs


MOUND_STYLE = "dome"     # "dome": lofted lumpy dome + stone/foot hull rocks; "lumps": core + all LUMPS as hull rocks


# Round 2: the crevice stones sit on the dome along its own surface normal, standing STONES[name] proud of it (their
# LUMPS top is ignored), so they read as small stones bedded in the dome on any dome profile, not as tall rocks.
STONES = {"crown": 0.22, "upper_left": 0.31, "front_shoulder": 0.29}
STONE_DEPTH = 0.8        # how far each stone reaches into the dome below the surface


def _dome_tree(vs):
    fs = _faces(vs)
    idx = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[idx[v] for v in f.verts] for f in fs])


def _stone(a, name, tree):
    (x, y), (sx, sy), top, height, seed, yaw, stone, lean = LUMPS[name]
    cx, cy = CORE["c"]
    x, y = cx + (x - cx) * MOUND_SXY, cy + (y - cy) * MOUND_SY
    sx, sy = sx * MOUND_SIZE, sy * MOUND_SIZE
    # the dome's surface point and its normal averaged over the stone's footprint
    pts, nrm = [], Vector()
    for dx, dy in ((0, 0), (0.35, 0), (-0.35, 0), (0, 0.35), (0, -0.35)):
        loc, n, _, _ = tree.ray_cast(Vector((x + dx * sx, y + dy * sy, 20.0)), Vector((0, 0, -1)))
        if loc is not None:
            pts.append(loc)
            nrm += n
    p = pts[0] if pts else Vector((x, y, 0.0))
    nrm = nrm.normalized() if nrm.length > 1e-6 else Vector((0, 0, 1))
    h = STONES[name] + STONE_DEPTH
    rings = LUMP_SHAPE.get(name) or (SMALL_RINGS if max(sx, sy) < 1.5 else LUMP_RINGS)
    vs = K.hull_rock(a, (sx, sy, h), loc=(0, 0, 0), seed=seed, mat=MOUND, rings=rings, jitter=0.12,
                     rot=math.radians(yaw), keep_bottom=True)
    m = Matrix.Translation(p - nrm * STONE_DEPTH) @ _align(nrm).to_4x4()
    bmesh.ops.transform(a.bm, matrix=m, verts=vs)
    zs = [v.co.z for v in vs]
    MOUND_INFO[name] = {"centre": (x, y), "top": max(zs), "base": max(min(zs), 0.0), "stone": stone,
                        "surf": tuple(round(c, 2) for c in p), "proud": STONES[name]}
    # the proud part is stone, fading into the dirt key just below the dome's surface (position along the normal)
    for f in _faces(vs):
        u = (f.calc_center_median() - p).dot(nrm)
        t = _q(min(stone, max(0.0, (u + 0.35) / 0.35)))
        if t:
            f.material_index = a._mi(K.mix_key(MOUND, STONE, t))
    return vs


def mound_raw(a):
    """Core + lumps + the root supports, separate closed shells (fused by the caller), painted."""
    MOUND_INFO.clear()
    vs = _dome(a) if MOUND_STYLE == "dome" else _core(a)
    tree = _dome_tree(vs) if MOUND_STYLE == "dome" else None
    for name in LUMPS:
        if MOUND_STYLE == "dome" and name not in ROCK_LUMPS:
            continue
        if tree is not None and name in STONES:
            vs += _stone(a, name, tree)
            continue
        lv = _lump(a, name)
        _paint_lump(a, lv, name)
        vs += lv
    for i, sp in enumerate(SUPPORTS):
        vs += _support(a, sp, 21200 + i + SUPPORT_SEED[0])
    _paint_mound(a, vs)
    _mottle(a, _faces(vs), MOUND_MOTTLE["amp"], MOUND_MOTTLE["scale"], MOUND_MOTTLE["seed"], MOUND_MOTTLE["jitter"])
    return vs


# ---- roots ------------------------------------------------------------------------------------------------------------
# Centre-line control points (build frame, studs) and diameters per control point (spec section 2.2).
# Centre lines read off the sheet's hero (front, elevation 20) with depths from the plan (spec section 2.2), so each
# root's screen path matches the drawing; the conform then lays them on the mound and SUPPORTS raise the mound
# under any that would float.
ROOTS = {
    # A: from the front tip's end, up the front leg (bulging toward the centre at mid-height), over the knee on the
    # crown, down the left leg over the left shoulder to the left tip (pointing back-left, behind the left foot)
    "A": dict(ctrl=[(-1.95, -3.25, 0.3), (-1.45, -2.95, 1.05), (-0.85, -2.6, 1.86), (-0.3, -2.1, 2.53),
                    (-0.22, -1.5, 3.02), (-0.4, -0.7, 3.8), (-0.95, -0.25, 4.15), (-1.75, 0.2, 4.0),
                    (-2.85, 0.3, 3.0), (-3.65, 0.55, 1.85), (-4.1, 0.95, 1.0), (-4.35, 1.6, 0.25)],
              diam=[1.15, 1.17, 1.2, 1.23, 1.26, 1.3, 1.32, 1.32, 1.28, 1.22, 1.18, 1.15], sides=10, seed=21041,
              start="tip", end="tip", crown=6.5),
    # C: from the blunt stub end at the crown (facing front-left), back to the fork (an elbow), then forward and
    # down the front-right to its tip
    "C": dict(ctrl=[(0.25, -0.5, 3.85), (0.85, -0.2, 3.95), (1.45, -0.5, 3.55), (1.92, -1.0, 3.06), (2.48, -1.5, 2.46),
                    (2.95, -2.0, 1.79), (3.5, -2.45, 1.12), (4.2, -2.95, 0.22)],
              diam=[1.2, 1.2, 1.18, 1.15, 1.12, 1.09, 1.06, 1.05], sides=10, seed=21042, start="stub", end="tip",
              crown=0, dark_from=0.62, dark_max=0.6),     # round 2: the fork read darker than the sheet's B+C
    # B: springs from C at the fork (its start is moved onto C's conformed centre line), continues the stub's line
    # up and back, arches over the crown's back-right and runs down the back-right to its tip
    "B": dict(ctrl=[(0.85, -0.2, 3.95), (1.05, 0.5, 4.2), (1.9, 0.95, 3.55), (2.7, 1.35, 2.75), (3.35, 1.7, 1.85),
                    (3.85, 2.3, 1.0), (4.15, 2.95, 0.3)],
              diam=[1.0, 1.0, 0.98, 0.96, 0.93, 0.91, 0.9], sides=9, seed=21043, start="buried", end="tip", crown=0,
              dark_from=0.62, dark_max=0.6),
}
ROOT_SCALE = 1.15       # round 2: every root diameter x this (the roots lie on the dome now; at the drawn 1.0-1.3 they
#                          read thinner against the mound than the sheet's, and the f34 bark share fell to 32 %)
ROOT_SINK = 0.2          # each root's underside this fraction of its diameter into the mound where it lies on it
CONFORM_REACH = 1.6      # stations whose underside is within this of the mound (above it) are pulled down onto it;
#                          higher ones keep their drawn height and get a SUPPORTS lump under them. Round 2: 0.12 -> 1.6,
#                          so the roots lie on the dome (A's arch no longer a hoop over a hollow) and the supports
#                          (round 1's flat-topped "rock pile" lumps) are rarely needed
STEP, STEP_BEND = 0.62, 0.42      # ring spacing along the root (studs), and round tight bends
TIP_LEN = 1.35           # cut tip length, in diameters (round 2: 1.2 -> 1.35, the sheet's long pale tips)
TIP_PROFILE = ((0.0, 1.0), (0.5, 0.94), (0.8, 0.74), (1.0, 0.46))   # (fraction along the tip, radius fraction)
COLLAR_SLANT = 0.35      # collar ring: axial offset = r * (COLLAR_SLANT cos(th - phi) +- COLLAR_ZIG)
COLLAR_ZIG = 0.1
END_LOOPS = (0.62, 0.3)  # end-face loops (fraction of the end rim): rim -> 0.62 cut, 0.62 -> 0.3 cut_ring, centre cut
MIN_GAP, COLLAR_GAP = 0.3, 0.5
TIP_TURN = 32.0          # a tip bends at most this many degrees off its root's run at the collar
ROOT_INFO = {}


def _catmull(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)


class _Path:
    """A Catmull-Rom curve through control points, sampled densely, queried by arc length."""

    def __init__(self, ctrl, diam, dense=24):
        P = [Vector(p) for p in ctrl]
        ext = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
        pts, ds, ci = [], [], []
        for i in range(len(P) - 1):
            for j in range(dense):
                t = j / dense
                pts.append(_catmull(ext[i], ext[i + 1], ext[i + 2], ext[i + 3], t))
                ds.append(diam[i] + (diam[i + 1] - diam[i]) * t)
                ci.append(i + t)
        pts.append(P[-1].copy())
        ds.append(diam[-1])
        ci.append(len(P) - 1)
        acc = [0.0]
        for a_, b_ in zip(pts, pts[1:]):
            acc.append(acc[-1] + (b_ - a_).length)
        self.pts, self.ds, self.acc, self.ci = pts, ds, acc, ci
        self.L = acc[-1]

    def _idx(self, s):
        s = min(self.L, max(0.0, s))
        lo, hi = 0, len(self.acc) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if self.acc[m] <= s:
                lo = m
            else:
                hi = m
        seg = self.acc[hi] - self.acc[lo]
        return lo, hi, (s - self.acc[lo]) / seg if seg > 1e-9 else 0.0

    def at(self, s):
        lo, hi, u = self._idx(s)
        return self.pts[lo].lerp(self.pts[hi], u)

    def tan(self, s, h=0.08):
        return (self.at(min(self.L, s + h)) - self.at(max(0.0, s - h))).normalized()

    def diam(self, s):
        lo, hi, u = self._idx(s)
        return self.ds[lo] + (self.ds[hi] - self.ds[lo]) * u

    def s_of_ctrl(self, i):
        return self.acc[min(range(len(self.ci)), key=lambda k: abs(self.ci[k] - i))]


def _stations(path, s0, s1):
    """Body ring arc lengths from s0 to s1: about STEP apart, STEP_BEND round tight bends."""
    n = max(1, round((s1 - s0) / STEP))
    base = [s0 + (s1 - s0) * i / n for i in range(n + 1)]
    out = [base[0]]
    for a_, b_ in zip(base, base[1:]):
        turn = path.tan(a_).angle(path.tan(b_))
        k = max(1, math.ceil((b_ - a_) / STEP_BEND)) if turn > math.radians(22) else 1
        out += [a_ + (b_ - a_) * j / k for j in range(1, k + 1)]
    return out


_MOUND_TREE = [None]


def _mound_tree():
    """BVH of the fused mound in the build frame (the temporary fused object if built, else a fresh fuse)."""
    if _MOUND_TREE[0] is None:
        o = bpy.data.objects.get(PFX + "mound")
        if o is None:
            o = fuse_mound()
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(o[OFF]))
        _MOUND_TREE[0] = BVHTree.FromBMesh(bm)
        bm.free()
    return _MOUND_TREE[0]


def _down(p_prev, p_next):
    """The root's local down at a station: world -Z made perpendicular to the centre line there."""
    t = (p_next - p_prev).normalized()
    z = Vector((0, 0, 1))
    d = -(z - t * z.dot(t))
    return d.normalized() if d.length > 1e-4 else Vector((0, 0, -1))


def _under_gap(tree, p, d, r):
    """The root underside's gap to the mound along its local down d (negative: sunk in), or None if the line misses.
    Cast from 4 studs above the station, so a station inside the mound still finds the top surface."""
    start = p - d * 4.0
    loc, n, _, dist = tree.ray_cast(start, d, 12.0)
    if loc is None:
        return None
    h = (loc - p).dot(d)          # surface below the centre by h (negative: the surface is above the centre)
    return h - r


def _conform(pts, radii, free=()):
    """Drop each station along the root's own local down (perpendicular to its centre line, so the root never slides
    sideways over the lumps' facets) until its underside sinks ROOT_SINK x diameter into the mound where it lies on
    (or within CONFORM_REACH above) it; lift it where it sinks deeper than 0.4 x diameter. Smooth, relax tight bends
    and repeat. Stations in `free` are left alone. Returns the new points and the per-station underside gaps."""
    tree = _mound_tree()
    orig = [p.copy() for p in pts]
    n = len(orig)
    delta = [Vector() for _ in orig]
    # which stations lie on the mound is decided once, on the drawn centre line: those within CONFORM_REACH of it
    # (or sunk into it). Only they are moved; the rest keep their drawn height (plan_supports beds them). Deciding it
    # again after each move let the pull-down cascade along the root until the whole root sagged onto the mound.
    on = set()
    for rnd in range(3):
        cur = [orig[i] + delta[i] for i in range(n)]
        for i in range(n):
            if i in free:
                continue
            r = radii[i]
            d = _down(cur[max(0, i - 1)], cur[min(n - 1, i + 1)])
            under = _under_gap(tree, cur[i], d, r)
            if under is None:
                continue
            if rnd == 0 and under < CONFORM_REACH:
                on.add(i)
            want = -ROOT_SINK * 2 * r
            if i in on and (want < under or under < -0.4 * 2 * r):
                delta[i] = delta[i] + d * (under - want)
        if rnd == 0:
            # smooth the displacements once (not the positions: smoothing positions flattened the knee's arch)
            delta = [delta[0]] + [(delta[i - 1] + delta[i] * 2 + delta[i + 1]) / 4 for i in range(1, n - 1)] + \
                [delta[-1]]
            delta = [Vector() if i in free else delta[i] for i in range(n)]
    out = _relax([orig[i] + delta[i] for i in range(n)], radii, free)
    gaps = []
    for i in range(n):
        d = _down(out[max(0, i - 1)], out[min(n - 1, i + 1)])
        u = _under_gap(tree, out[i], d, radii[i])
        gaps.append(None if u is None else round(u / (2 * radii[i]), 2))
    return out, gaps


BEND_MIN = 1.3     # the centre line's bend radius at least this many tube radii (or the inner side folds through)


def _bend_radius(a_, b_, c_):
    ab, bc, ca = (b_ - a_).length, (c_ - b_).length, (a_ - c_).length
    cr = (b_ - a_).cross(c_ - a_).length
    return ab * bc * ca / (2 * cr) if cr > 1e-9 else 1e9


def _relax(pts, radii, free=(), rounds=40):
    """Ease every station whose three-point bend radius is under BEND_MIN x its tube radius toward its neighbours'
    midpoint, until none is (a tight knee rounds out instead of folding the tube's inner side through itself)."""
    out = [p.copy() for p in pts]
    for _ in range(rounds):
        moved = False
        for i in range(1, len(out) - 1):
            if i in free:
                continue
            if _bend_radius(out[i - 1], out[i], out[i + 1]) < BEND_MIN * radii[i]:
                out[i] = out[i].lerp((out[i - 1] + out[i + 1]) / 2, 0.35)
                moved = True
        if not moved:
            break
    return out


def _root_layout(name):
    """Ring stations for one root: [(point, tangent, radius, kind, s)] from start to end; kind 'body', 'collar',
    'tip' or 'end'. The body stations are conformed onto the mound."""
    R = ROOTS[name]
    ctrl = [Vector(p) for p in R["ctrl"]]
    if R["start"] == "buried" and "C" in ROOT_INFO:
        # B's start on C's conformed centre line, nearest its own fork point
        sts = [Vector(s[0]) for s in ROOT_INFO["C"]["stations"]]
        best = None
        for a_, b_ in zip(sts, sts[1:]):
            ab = b_ - a_
            u = max(0.0, min(1.0, (ctrl[0] - a_).dot(ab) / max(1e-9, ab.dot(ab))))
            q = a_ + ab * u
            if best is None or (q - ctrl[0]).length < (best - ctrl[0]).length:
                best = q
        ctrl[0] = best
    diam = [d * ROOT_SCALE for d in R["diam"]]
    path = _Path(ctrl, diam)
    L = path.L
    st = []
    # start tip (A only) and end tip, measured along the path
    tl0 = TIP_LEN * diam[0] if R["start"] == "tip" else 0.0
    tl1 = TIP_LEN * diam[-1]
    b0 = tl0 if R["start"] == "tip" else 0.0
    b1 = L - tl1
    body = _stations(path, b0, b1)
    pts = [path.at(s) for s in body]
    rad = [path.diam(s) / 2 for s in body]
    free = {0} if R["start"] == "buried" else set()
    cp, gaps = _conform(pts, rad, free=free)
    # the collars sit at the conformed body ends; the tips follow their original direction from there. A body
    # station bunched up against its neighbour (under MIN_GAP) or a collar (under COLLAR_GAP, whose slanted ring
    # would cross it) is dropped.
    keep = []
    for i, s in enumerate(body):
        kind = "collar" if (i == 0 and R["start"] == "tip") or i == len(body) - 1 else "body"
        if kind == "body" and i > 0:
            near_c = [cp[j] for j in (0, len(body) - 1) if (j == 0 and R["start"] == "tip") or j == len(body) - 1]
            if (cp[i] - keep[-1][0]).length < MIN_GAP or any((cp[i] - c).length < COLLAR_GAP for c in near_c):
                continue
        keep.append([cp[i], None, rad[i], kind, s])
    st = keep
    # tangents from the conformed points
    for i in range(len(st)):
        a_ = st[max(0, i - 1)][0]
        b_ = st[min(len(st) - 1, i + 1)][0]
        st[i][1] = (b_ - a_).normalized()

    def tip(at_collar, outward, s_dir):
        c0, t0, r0 = at_collar[0], at_collar[1] * s_dir, at_collar[2]
        # the tip continues the path's own direction past the collar (blended with the conformed tangent)
        s_c = at_collar[4]
        s_end = L if s_dir > 0 else 0.0
        # aimed from the conformed collar at the path's own end (the tip reaches down to the ground there),
        # blended a little with the root's run so it doesn't kink
        e_path = path.at(s_end) - c0
        d = (e_path.normalized() * 0.9 + t0 * 0.1).normalized()
        turn = d.angle(t0) if t0.length > 1e-6 else 0.0
        if turn > math.radians(TIP_TURN):
            # never bend the tip more than TIP_TURN off the root's run (its rings would fold through the collar)
            d = t0.slerp(d, math.radians(TIP_TURN) / turn).normalized()
        tl = (path.at(s_end) - path.at(s_c)).length
        ln = min(1.3 * tl, max(0.85 * tl, e_path.length))
        out = []
        for f, rf in TIP_PROFILE[1:]:
            out.append([c0 + d * ln * f, d * s_dir, r0 * rf, "end" if f == 1.0 else "tip", s_c + s_dir * ln * f])
        return out
    end_tip = tip(st[-1], 1, 1)
    st = st + end_tip
    if R["start"] == "tip":
        start_tip = tip(st[0], -1, -1)
        st = list(reversed(start_tip)) + st
    ROOT_INFO[name] = {"L": round(L, 2), "rings": len(st), "gaps": gaps,
                       "crown_s": path.s_of_ctrl(R["crown"]), "stations": [(tuple(p), r, k, s) for p, t, r, k, s in st]}
    return st, path


# bark colour fields (spec section 5.5)
BARK_FIELD = dict(dark_from=0.45, dark_to=1.0, dark_max=0.75, under=0.35, under_mix=0.35, crown=1.5, crown_mix=0.4,
                  patch_scale=0.8, patch_level=0.3, patch_mix=0.3, seed=21051)
BARK_MOTTLE = dict(amp=0.05, scale=0.5, seed=21052, jitter=0.01)
CUT_MOTTLE = dict(amp=0.025, scale=0.9, seed=21053)


def _root(a, name):
    """One root tube (rings along its stations), both ends closed: a cut tip (collar -> taper -> ringed end face), a
    domed bark stub, or a buried fan. Painted by position: bark darker toward each collar and on the lower part of
    each section, lighter round the crown, broad patches; cut caps; the ring loop on each end face. Returns verts."""
    R = ROOTS[name]
    st, path = _root_layout(name)
    rng = random.Random(R["seed"] + ROOT_SEED[0])
    bm = a.bm
    sides = R["sides"]
    phase = rng.uniform(0, 2 * math.pi)
    t0 = st[0][1]
    n = _perp(t0)
    prev_t = t0
    rings, ring_kind, ring_s, ring_r = [], [], [], []
    vdown = {}
    phi_slant = rng.uniform(0, 2 * math.pi)
    for i, (c, t, r, kind, s) in enumerate(st):
        n = prev_t.rotation_difference(t) @ n
        n = (n - t * n.dot(t)).normalized()
        prev_t = t
        b = t.cross(n)
        tw = phase + math.radians(rng.uniform(-8, 8))
        body = kind == "body"
        sc = 1.0 + (rng.uniform(-0.06, 0.06) if body else 0.0)
        ring = []
        for k in range(sides):
            th = tw + 2 * math.pi * k / sides
            radial = n * math.cos(th) + b * math.sin(th)
            rr = r * sc + (rng.uniform(-0.04, 0.04) if kind in ("body", "collar") else rng.uniform(-0.015, 0.015))
            q = c + radial * rr
            if kind == "collar":
                # slanted, zig-zag bark/cut boundary (spec: not a square ring)
                tip_dir = 1 if i > len(st) / 2 else -1
                q = q + t * tip_dir * r * (COLLAR_SLANT * math.cos(th - phi_slant) +
                                           COLLAR_ZIG * (1 if k % 2 else -1))
            elif body and 0 < i < len(st) - 1:
                q = q + t * rng.uniform(-0.06, 0.06)
            v = bm.verts.new(q)
            # section height: how far down this vertex sits in the ring (position, not the normal)
            dn = Vector((0, 0, -1))
            dn = (dn - t * dn.dot(t))
            vdown[v] = radial.dot(dn.normalized()) if dn.length > 1e-6 else 0.0
            ring.append(v)
        rings.append(ring)
        ring_kind.append(kind)
        ring_s.append(s)
        ring_r.append(r)
    verts = [v for r in rings for v in r]
    cut_faces, ring_faces, bark_faces = [], [], []
    tipish = ("tip", "end")
    for i in range(len(rings) - 1):
        fs = _strip(bm, rings[i], rings[i + 1])
        # a strip is cut wood when either of its rings belongs to a tip (collar -> end)
        (cut_faces if ring_kind[i] in tipish or ring_kind[i + 1] in tipish else bark_faces).extend(fs)

    def end_face(ring, centre, axis):
        """Flat end face: loops at END_LOOPS, a centre fan raised a hair."""
        loops = [ring]
        for f in END_LOOPS:
            loops.append([bm.verts.new(centre + (v.co - centre) * f) for v in ring])
        cv = bm.verts.new(centre + axis * 0.02)
        fs_out = _strip(bm, loops[1], loops[0])
        fs_ring = _strip(bm, loops[2], loops[1])
        fs_c = _fan(bm, loops[2], cv)
        return fs_out + fs_c, fs_ring, [v for l in loops[1:] for v in l] + [cv]

    def ring_centre(ring):
        return sum((v.co for v in ring), Vector()) / len(ring)
    # end
    ce = ring_centre(rings[-1])
    ax = st[-1][1]
    if R["end"] == "tip":
        fo, fr, nv = end_face(rings[-1], ce, ax)
        cut_faces += fo
        ring_faces += fr
        verts += nv
    # start
    c0 = ring_centre(rings[0])
    ax0 = -st[0][1]
    if R["start"] == "tip":
        fo, fr, nv = end_face(list(reversed(rings[0])), c0, ax0)
        cut_faces += fo
        ring_faces += fr
        verts += nv
    elif R["start"] == "stub":
        # domed bark end: a smaller ring proud of the end, then a raised centre
        r0 = st[0][2]
        dome = [bm.verts.new(c0 + (v.co - c0) * 0.72 + ax0 * r0 * 0.28) for v in rings[0]]
        cv = bm.verts.new(c0 + ax0 * r0 * 0.42)
        fs = _strip(bm, dome, rings[0]) + _fan(bm, list(reversed(dome)), cv)
        bark_faces += fs
        verts += dome + [cv]
        for v in dome:
            vdown[v] = 0.0
        vdown[cv] = 0.0
    else:
        cv = bm.verts.new(c0 + ax0 * 0.15)
        fs = _fan(bm, list(reversed(rings[0])), cv)
        bark_faces += fs
        verts.append(cv)
        vdown[cv] = 0.0
    a._finish(verts, BARK)
    mi_cut, mi_ring = a._mi(CUT), a._mi(CUT_RING)
    for f in cut_faces:
        f.material_index = mi_cut
    for f in ring_faces:
        f.material_index = mi_ring
    _tri(bm, cut_faces + ring_faces + bark_faces)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(verts))
    # paint the bark by position
    ROOT_INFO[name]["collars"] = [tuple(ring_centre(rings[i])) for i, k in enumerate(ring_kind) if k == "collar"]
    s_ring = {v: ring_s[i] for i, r in enumerate(rings) for v in r}
    crown_s = ROOT_INFO[name]["crown_s"]
    collar_s = [ring_s[i] for i, k in enumerate(ring_kind) if k == "collar"]
    nf = K.noise_field(scale=BARK_FIELD["patch_scale"], seed=BARK_FIELD["seed"] + R["seed"])
    mi_bark = a._mi(BARK)
    bark, cut = [], []
    for f in _faces(verts):
        if f.material_index != mi_bark:
            cut.append(f)
            continue
        bark.append(f)
        c = f.calc_center_median()
        ss = [s_ring[v] for v in f.verts if v in s_ring]
        s = sum(ss) / len(ss) if ss else 0.0
        # fraction from the crown toward the nearer collar
        if R["start"] == "tip":
            leg_end = collar_s[0] if s < crown_s else collar_s[-1]
        else:
            leg_end = collar_s[-1]
        u = abs(s - crown_s) / max(1e-3, abs(leg_end - crown_s))
        down = sum(vdown.get(v, 0.0) for v in f.verts) / len(f.verts)
        td = 0.0
        d_from = R.get("dark_from", BARK_FIELD["dark_from"])
        if u > d_from:
            td = R.get("dark_max", BARK_FIELD["dark_max"]) * min(1.0, (u - d_from) / (BARK_FIELD["dark_to"] - d_from))
        if down > math.cos(math.pi * BARK_FIELD["under"]):
            td = max(td, BARK_FIELD["under_mix"])
        tl = 0.0
        if abs(s - crown_s) < BARK_FIELD["crown"] and td < 0.2:
            tl = BARK_FIELD["crown_mix"] * (1 - abs(s - crown_s) / BARK_FIELD["crown"]) * 1.6
            tl = min(tl, BARK_FIELD["crown_mix"])
        if nf(c) > BARK_FIELD["patch_level"] and td < 0.3:
            tl = max(tl, BARK_FIELD["patch_mix"])
        if _q(td):
            f.material_index = a._mi(K.mix_key(BARK, BARK_DARK, _q(td)))
        elif _q(tl):
            f.material_index = a._mi(K.mix_key(BARK, BARK_LIGHT, _q(tl)))
    _mottle(a, bark, BARK_MOTTLE["amp"], BARK_MOTTLE["scale"], BARK_MOTTLE["seed"] + R["seed"], BARK_MOTTLE["jitter"])
    _mottle(a, cut, CUT_MOTTLE["amp"], CUT_MOTTLE["scale"], CUT_MOTTLE["seed"] + R["seed"])
    return verts


def _self_hits_bm(bm):
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    return sum(1 for i, j in tree.overlap(tree) if i < j and not set(bm.faces[i].verts) & set(bm.faces[j].verts))


BEND_TRIES = (1.3, 1.6, 2.0, 2.5)
ROOT_TRIES = {}


def _root_checked(a, name):
    """_root, guarded: each tube is first built on its own and checked for self-intersections (a tight elbow can fold
    its inner side through itself, and an exact union of such a tube fails); on a hit the bend limit BEND_MIN is
    raised and the tube rebuilt, then the clean one goes into the asset."""
    global BEND_MIN
    keep = BEND_MIN
    try:
        for bmin in BEND_TRIES:
            BEND_MIN = bmin
            probe = K.fk().Asset(PFX + "probe", "probe")
            _root(probe, name)
            hits = _self_hits_bm(probe.bm)
            probe.bm.free()
            if not hits:
                break
        ROOT_TRIES[name] = {"bend_min": BEND_MIN, "hits": hits}
        return _root(a, name)
    finally:
        BEND_MIN = keep


def root_a(a):
    return _root_checked(a, "A")


def root_fork(a):
    return _root_checked(a, "C") + _root_checked(a, "B")


# ---- leaf module ------------------------------------------------------------------------------------------------------
KITE = ((0.25, 0.40), (0.55, 0.50), (0.82, 0.28))     # (t, half width / W): shoulder, belly, pre-tip
RIDGE = ((0.42, 0.08), (0.76, 0.04))                  # (t, camber / L): the midrib ridge
KEEL = (0.50, 0.04)
FOLD = 0.45
HANDLES = (0.48, 0.38)
LEAF_BANDS = ((0.12, 0.32), (0.6, 0.82))
LEAF_NOISE = 0.08
LEAF_MOTTLE = dict(amp=0.035, scale=0.5, seed=21071)


def _bez(P, t):
    p0, p1, p2, p3 = P
    s = 1 - t
    return p0 * s ** 3 + p1 * 3 * s * s * t + p2 * 3 * s * t * t + p3 * t ** 3


def _bez_d(P, t):
    p0, p1, p2, p3 = P
    s = 1 - t
    return (p1 - p0) * 3 * s * s + (p2 - p1) * 6 * s * t + (p3 - p2) * 3 * t * t


def _leaf_path(base, az, tip, pitch, slope):
    B = Vector(base)
    a1 = math.radians(az)
    T = Vector((math.cos(a1) * tip[0], math.sin(a1) * tip[0], tip[1]))
    chord = (T - B).length

    def dirn(p):
        p = math.radians(p)
        return Vector((math.cos(a1) * math.cos(p), math.sin(a1) * math.cos(p), math.sin(p)))
    return (B, B + dirn(pitch) * HANDLES[0] * chord, T - dirn(slope) * HANDLES[1] * chord, T)


def _leaf(a, path, width, seed, roll=0.0, shift=0.0):
    """One closed broad pointed leaf (M019 recipe): an 8-point kite outline, two midrib ridge points above, a keel
    below. Painted base -> mid -> tip along its own length. Returns verts."""
    rng = random.Random(seed)
    bm = a.bm
    P = [Vector(p) for p in path]
    L = sum((_bez(P, (i + 1) / 20) - _bez(P, i / 20)).length for i in range(20))
    W = width
    side0 = Vector((-(P[3] - P[0]).y, (P[3] - P[0]).x, 0.0)).normalized()
    rl = math.radians(roll)

    def frame(t):
        T = _bez_d(P, t).normalized()
        S = (side0 - T * side0.dot(T)).normalized()
        N = T.cross(S).normalized()
        if N.z < 0:
            N = -N
        S = N.cross(T).normalized()
        S, N = S * math.cos(rl) + N * math.sin(rl), N * math.cos(rl) - S * math.sin(rl)
        return _bez(P, t), S, N
    tm = {}

    def vert(t, y, z):
        c, S, N = frame(t)
        x = bm.verts.new(c + S * y + N * z)
        tm[x] = t
        return x
    base = vert(0.0, 0.0, 0.0)
    tip = vert(1.0, 0.0, 0.0)
    right, left = [], []
    for t, h in KITE:
        y = h * W * (1 + rng.uniform(-0.06, 0.06))
        right.append(vert(t, -y, -FOLD * y * 0.5))
    for t, h in KITE:
        y = h * W * (1 + rng.uniform(-0.06, 0.06))
        left.append(vert(t, y, -FOLD * y * 0.5))
    r1 = vert(RIDGE[0][0], 0.0, RIDGE[0][1] * L)
    r2 = vert(RIDGE[1][0], 0.0, RIDGE[1][1] * L)
    # the keel below the lowest (drooped) outline point, so the bottom fan never folds up through the top
    k = vert(KEEL[0], 0.0, -(FOLD * 0.5 * max(KITE[1][1], KITE[0][1]) * W * 1.07 + KEEL[1] * L))
    tm[k] = KEEL[0] - 0.5        # keel faces read toward the base
    ring = [base] + right + [tip] + list(reversed(left))
    fs = []
    for sd in (right, left):
        s, b, p = sd
        fs += [bm.faces.new((base, s, r1)), bm.faces.new((s, b, r1)), bm.faces.new((b, r2, r1)),
               bm.faces.new((b, p, r2)), bm.faces.new((p, tip, r2))]
    for i in range(len(ring)):
        fs.append(bm.faces.new((k, ring[(i + 1) % len(ring)], ring[i])))
    vs = ring + [r1, r2, k]
    a._finish(vs, LEAF)
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    lad = _ladder(LEAF_BASE, LEAF, LEAF_TIP)
    for f in fs:
        t = sum(tm[v] for v in f.verts) / len(f.verts) + shift + rng.uniform(-LEAF_NOISE, LEAF_NOISE)
        f.material_index = a._mi(_pick(lad, t, LEAF_BANDS[0], LEAF_BANDS[1]))
    return vs


LEAF_N = 8
LEAF_LW = (1.1, 0.66)         # leaf length and width per stud of (span / 2)
LEAF_RISE = (25, 50)          # chord rise of a leaf above the hub plane, degrees (round 2: upright stars, spec 1.4)
LEAF_PITCH = (15, 30)         # the base leaves this much steeper than the chord, degrees
PITCH_MAX = 84.0              # ... but never past upright
LEAF_ALT = True
HUB_IN = 0.6                  # each leaf's base starts inside the hub cone at this fraction of its radius (round 2:
#                               leaves meeting at the hub's axis left bowtie vertices after the union)
LEAF_BURY = -0.1              # leaf base depth below the hub point (per stud of span / 2)
HUB_R, HUB_H = 0.17, 0.16     # hub cone radius and apex height (per stud of span / 2)


def _leaf_module(a, hub, normal, span, seed, yaw=0.0, sink=0.3, rise=LEAF_RISE, fan=360.0, back_up=0.0):
    """An eight-leaf star round a small dark 5-sided hub cone (local frame: hub at the origin, +Z along normal).
    Leaves about 360/8 deg apart (+-12), each chord rising `rise` deg off the hub plane (leaves toward local +Y
    rise back_up deg more: the back of the clump stands up), base steeper, tip drooping below the chord; per leaf
    +-8 % L, +-6 % W, +-6 deg roll. span = the clump's tip-to-tip width."""
    rng = random.Random(seed)
    bm = a.bm
    s = span / 2.0
    out = []
    hr = HUB_R * s
    ph = rng.uniform(0, 2 * math.pi)
    foot = [bm.verts.new((math.cos(ph + 2 * math.pi * k / 5) * hr, math.sin(ph + 2 * math.pi * k / 5) * hr, -sink))
            for k in range(5)]
    mid = [bm.verts.new((math.cos(ph + 2 * math.pi * k / 5) * hr * 0.85,
                         math.sin(ph + 2 * math.pi * k / 5) * hr * 0.85, 0.04 * s)) for k in range(5)]
    apex = bm.verts.new((0, 0, HUB_H * s))
    fb = bm.verts.new((0, 0, -sink - 0.02))
    side = _strip(bm, foot, mid)
    fs = side + _fan(bm, mid, apex) + _fan(bm, foot, fb, flip=True)
    hub_v = foot + mid + [apex, fb]
    a._finish(hub_v, STEM)
    if sink > 0.25:
        # a module standing up out of a crevice (CLUMP_FLOAT): its long hub stalk is the stub's bark (the sheet's
        # brown crown knob), not the near-black hub
        for f in side:
            f.material_index = a._mi(BARK_DARK)
    _tri(bm, fs)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(hub_v))
    out += hub_v
    az0 = rng.uniform(0, 360)
    step = fan / LEAF_N if fan < 360 else 360.0 / LEAF_N
    for k in range(LEAF_N):
        az = az0 + step * k + rng.uniform(-12, 12) * (step / 45.0)
        L = LEAF_LW[0] * s * (1 + rng.uniform(-0.08, 0.08))
        W = LEAF_LW[1] * s * (1 + rng.uniform(-0.06, 0.06))
        b0 = Vector((math.cos(math.radians(az)) * HUB_IN * hr, math.sin(math.radians(az)) * HUB_IN * hr,
                     (LEAF_BURY + 0.01 * k) * s))
        up = back_up * max(0.0, math.sin(math.radians(az)))
        r_ = rng.uniform(*rise)
        if LEAF_ALT:
            # alternate low and high leaves round the hub: neighbours rise LEAF_ALT apart, so two leaves never
            # graze each other (near-equal rises left slivers and folds after the union)
            r_ = rise[0] + (rise[1] - rise[0]) * (0.12 if k % 2 == 0 else 0.88) + (r_ - sum(rise) / 2) * 0.15
        ch = math.radians(min(75.0, r_ + up))
        path = _leaf_path(b0, az, (L * 0.92 * math.cos(ch), L * 0.92 * math.sin(ch)),
                          min(PITCH_MAX, math.degrees(ch) + rng.uniform(*LEAF_PITCH)),
                          math.degrees(ch) + rng.uniform(-26, -10))
        out += _leaf(a, path, W, seed * 10 + k, roll=rng.uniform(-6, 6))
    m = Matrix.Translation(Vector(hub)) @ _align(normal, yaw).to_4x4()
    bmesh.ops.transform(bm, matrix=m, verts=out)
    _mottle(a, _faces(out), LEAF_MOTTLE["amp"], LEAF_MOTTLE["scale"], LEAF_MOTTLE["seed"] + seed)
    return out


# hero leaf modules: hub target (build frame), normal, span, seed, yaw, rise, back_up (spec section 2.3)
# round 2: left and right rise as the crown does (upright stars) with their axes tilted toward +Z (no hub faces the
# camera); the left module moved out of the hollow under A's arch onto the front flank of A's left leg (sheet f34
# (.197, .631))
CLUMPS = {"left": ((-2.55, -0.55, 2.6), (-0.25, -0.25, 0.93), 2.45, 22081, 0.0, (25, 50), 12.0),
          "top": ((0.25, 0.6, 4.6), (0.0, -0.3, 0.95), 2.3, 24082, 0.0, (28, 48), 15.0),
          "right": ((2.05, -0.2, 3.9), (0.25, -0.3, 0.92), 2.4, 22083, 0.0, (25, 50), 15.0)}
CLUMP_LIFT = -0.04
# the crown module stands this far up out of its crevice on its (deeper-sunk) hub cone, so it tops the silhouette
# (verifier round 2: 0.35 -> 0.15, the bark stalk under it read as a thin stick from the rear)
CLUMP_FLOAT = {"top": 0.15}
CLUMP_YAW_JIT = [0.0]      # extra yaw on every hero leaf module; the hero guard turns them a little on a retry
HERO_TRIES, HERO_YAW_STEP = 10, 9.0
HERO_YAW0 = 27.0           # round 2: the first hero attempt already uses the yaw that fuses clean (build time)
CLUMP_SNAP = 0.7
CLUMP_INFO = {}
PART_SPAN, PART_SINK = 1.9, 0.12


PART_SEED = 21089


def _leaf_part_raw(a, seed=PART_SEED):
    _leaf_module(a, (0, 0, PART_SINK), (0, 0, 1), PART_SPAN, seed, sink=PART_SINK)


def leaf_part(a):
    """ArchedRootClusterLeafModule: one module, hub up (the clean fused module from fuse_leaf_part)."""
    o = bpy.data.objects.get(PFX + "leafpart") or fuse_leaf_part()
    _paste_obj(a, o)


# ---- fusing (temporary objects in the build frame) ---------------------------------------------------------------------
def _tmp(name, fn):
    """fn built into a temporary object whose mesh stays in the build frame (OFF = 0)."""
    old = bpy.data.objects.get(name)
    if old:
        me = old.data
        bpy.data.objects.remove(old, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    coll = M.coll(NUM, TITLE)
    a = K.fk().Asset(name, "wip", seed=7, tint_var=0.04)
    fn(a)
    o = a.finish(collection=coll, mark_asset=False, origin=None)
    o.location = (0, 0, 0)
    bpy.context.view_layer.update()      # split_loose copies matrix_world: it must not be stale
    o[OFF] = [0.0, 0.0, 0.0]
    return o


def _fused_ok(o):
    a = M.audit(o)
    return (a["shells"] == 1 and not a["nonmanifold_edges"] and not a.get("nonmanifold_verts", 0)
            and not a["boundary_edges"] and a["normals"] == "outward"
            and not m016._self_hits(o)[0] and not m012._thin(o, POLISH_LIM)["under"])


def _dissolve_flat(o, angle):
    """Limited dissolve of near-coplanar faces (the union seams cut broad facets into slivers and fans), keeping
    every colour edge, then BEAUTY triangulation: the same shape in fewer triangles."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n0 = sum(len(f.verts) - 2 for f in bm.faces)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(angle), verts=list(bm.verts), edges=list(bm.edges),
                             delimit={"MATERIAL"})
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    n1 = len(bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    return [n0, n1]


FINE_MERGE = 0.0         # round 2: the exact union's output is clean; any merge distance (union_loose: 0.01) welds
#                          the leaves' converging intersection curves at a hub into bowties and folds
HERO_MERGE = 0.0


def _union_fine(o, merge=FINE_MERGE):
    """M.union_loose with a finer post-union merge. union_loose merges vertices within 0.01, and at a leaf hub the
    eight leaves' intersection curves converge closer than that: merging them left bowtie vertices and folds."""
    act = bpy.context.view_layer.objects.active
    if act and act.mode != "OBJECT":
        with bpy.context.temp_override(active_object=act, object=act):
            bpy.ops.object.mode_set(mode="OBJECT")
    others = M.split_loose(o)
    for p in others:
        m = o.modifiers.new("U", "BOOLEAN")
        m.operation, m.solver, m.object = "UNION", "EXACT", p
        m.material_mode = "TRANSFER"
        with M._override(o):
            bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.data.objects.remove(p, do_unlink=True)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=merge)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    M.drop_specks(bm, min_area=0.05)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    K.drop_unused_slots(o)
    return len(others)


BOWTIE_NUDGE = 0.004


def _split_bowties(o, nudge=BOWTIE_NUDGE):
    """A bowtie vertex (two closed face fans touching at one point, every edge manifold) is split into one vertex per
    fan, each moved `nudge` toward its own fan, so the two surfaces no longer touch. Returns how many were split."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bad = [v for v in bm.verts if v.link_faces and not v.is_manifold and all(len(e.link_faces) == 2 for e in v.link_edges)]
    n = 0
    for v in bad:
        if not v.is_valid:
            continue
        parts = bmesh.utils.vert_separate(v, [])
        if len(parts) < 2:
            continue
        n += 1
        for p in parts:
            nb = [e.other_vert(p).co for e in p.link_edges]
            if nb:
                c = sum(nb, Vector()) / len(nb)
                d = c - p.co
                if d.length > 1e-9:
                    p.co += d.normalized() * min(nudge, d.length * 0.25)
    if n:
        bm.to_mesh(o.data)
        o.data.update()
    bm.free()
    return n


def _fuse(name, fn, ground=False, dissolve=0.0, fine=False):
    o = _tmp(name, fn)
    log = {"shells_merged": _union_fine(o) if fine else M.union_loose(o)}
    if ground:
        m016._floor_cut(o, 0.0)
    if dissolve:
        log["dissolve"] = _dissolve_flat(o, dissolve)
    log["clean"] = m016._clean_mesh(o, (0.0,) if ground else ())
    log["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    log["polish"] = _polish(o)
    log["bowties"] = _split_bowties(o)
    log["ok"] = _fused_ok(o)
    return o, log


FUSE_LOG = {}


# (support seed offset, dissolve angle) tried in turn until the fused mound is clean
MOUND_RETRY = ((0, 10.0), (100, 10.0), (200, 10.0), (0, 8.0), (300, 10.0), (100, 12.0), (400, 9.0), (500, 11.0))
SUPPORT_SEED = [0]


def fuse_mound():
    """The mound fused (exact union of core, lumps and supports, floor cut, dissolve, cleanup). A union seam can
    leave a fold (a self-intersection) that breaks the hero's union later; the guard tries the next dissolve angle
    until the result is clean."""
    _MOUND_TREE[0] = None
    for seed_off, ang in MOUND_RETRY:
        SUPPORT_SEED[0] = seed_off
        o, FUSE_LOG["mound"] = _fuse(PFX + "mound", mound_raw, ground=True, dissolve=ang)
        FUSE_LOG["mound"]["retry"] = [seed_off, ang]
        if FUSE_LOG["mound"]["ok"]:
            break
    return o


# ---- root supports ("Roots sit on flat joining surfaces on the rock base") --------------------------------------------
MOUND_DISSOLVE = 10.0    # degrees: the fused mound's near-coplanar faces merged (fewer union slivers)
SUPPORTS = []            # [(top centre (x, y, z), up axis, along axis, width)], filled by plan_supports()
SUPPORT_FLOAT = -0.12    # a station whose underside gap (fraction of its diameter) is above this needs a support
SUPPORT_SPACING = 1.6    # at most one support per this much centre line
SUPPORT_ROUNDS = 2
SUPPORT_W = 1.7          # support footprint across the root, in root diameters
SUPPORT_LEN = 2.0        # ... and along it
SUPPORT_DEPTH = 1.4      # a support reaches this far below its top (into the mound)
SUPPORT_STONE = 0.5      # its upper part blends up to this mix of the stone key
SUPPORT_RINGS = [(0.0, 1.0, 5), (0.6, 0.92, 5), (1.0, 0.6, 4)]
SUPPORT_MAX = 0.15       # round 2: a support's top stands at most this far proud of the mound (the root then conforms
#                          down onto it), so no support shows as a flat-topped rock


def _support(a, sp, seed):
    """A flat-topped hull lump, its top facet lying under the root (tilted with the root's slope and turned along
    it), ROOT_SINK x diameter above the root's underside, its body reaching SUPPORT_DEPTH down into the mound."""
    top, up, along, w = (Vector(sp[0]), Vector(sp[1]), Vector(sp[2]), sp[3])
    vs = K.hull_rock(a, (w * SUPPORT_LEN / SUPPORT_W, w, SUPPORT_DEPTH), loc=(0, 0, 0), seed=seed, mat=MOUND,
                     rings=SUPPORT_RINGS, jitter=0.1, keep_bottom=True)
    x = (along - up * along.dot(up)).normalized()
    y = up.cross(x)
    R = Matrix((x, y, up)).transposed().to_4x4()
    m = Matrix.Translation(top) @ R @ Matrix.Translation((0, 0, -SUPPORT_DEPTH))
    bmesh.ops.transform(a.bm, matrix=m, verts=vs)
    # the joining surface is rock: its upper part (along its own axis) blends into the stone key
    for f in _faces(vs):
        h = (f.calc_center_median() - top).dot(up) / SUPPORT_DEPTH + 1.0
        t = _q(SUPPORT_STONE * min(1.0, max(0.0, (h - 0.45) / 0.4)))
        if t:
            f.material_index = a._mi(K.mix_key(MOUND, STONE, t))
    return vs


def plan_supports():
    """One flat-topped hull lump under each stretch of root that floats above the mound (its underside gap above
    SUPPORT_FLOAT x diameter), bedding the root ROOT_SINK x diameter into it. Adds to SUPPORTS; returns how many."""
    tree = _mound_tree()
    added = 0
    for name in ("A", "C", "B"):
        last = None
        sts = [s for s in ROOT_INFO[name]["stations"] if s[2] in ("body", "collar")]
        for i, (p, r, kind, s) in enumerate(sts):
            p = Vector(p)
            q0 = Vector(sts[max(0, i - 1)][0])
            q1 = Vector(sts[min(len(sts) - 1, i + 1)][0])
            d = _down(q0, q1)
            under = _under_gap(tree, p, d, r)
            if under is None or under < SUPPORT_FLOAT * 2 * r:
                continue
            u = p + d * r
            if last is not None and (u - last).length < SUPPORT_SPACING:
                continue
            last = u
            top = u - d * ROOT_SINK * 2 * r
            surf = p + d * (r + under)                 # the mound's surface below the station, along d
            if (surf - top).dot(-d) > SUPPORT_MAX:
                top = surf - d * SUPPORT_MAX
            SUPPORTS.append((tuple(round(c, 3) for c in top), tuple(round(c, 4) for c in -d),
                             tuple(round(c, 4) for c in (q1 - q0).normalized()), round(SUPPORT_W * 2 * r, 3)))
            added += 1
    return added


def _contact_paint(o):
    """Darken the fused mound's faces near a root's underside contact (the sheet's dark crevices under the roots;
    Roblox casts no self-shadow), by distance from each face centre to the roots' conformed centre lines."""
    p = m011._Paint(o, off=o[OFF])
    segs = []
    for name, info in ROOT_INFO.items():
        sts = info["stations"]
        for (p0, r0, k0, s0), (p1, r1, k1, s1) in zip(sts, sts[1:]):
            segs.append((Vector(p0), Vector(p1), (r0 + r1) / 2))
    n = 0
    dark = {MOUND_DARK} | {K.mix_key(MOUND, MOUND_DARK, t) for t in (0.25, 0.5, 0.75)}
    # stones (and half-stone faces) keep their light grey; a 25 % stone tint on the dome darkens like dirt
    stony = {STONE} | {K.mix_key(MOUND, STONE, t) for t in (0.5, 0.75)}
    for f in p.bm.faces:
        key = p.key(f)
        if not key.startswith(MOUND) or key in dark or key in stony:
            continue          # stone faces keep their light grey (the sheet's crevice stones read lighter)
        c = p.at(f)
        best = 9.0
        for a_, b_, r in segs:
            ab = b_ - a_
            u = max(0.0, min(1.0, (c - a_).dot(ab) / max(1e-9, ab.dot(ab))))
            d = (c - (a_ + ab * u)).length - r
            best = min(best, d)
        if best < CONTACT[0]:
            t = _q(CONTACT[1] * (1 - max(0.0, best) / CONTACT[0]))
            if t:
                f.material_index = p._mi(K.mix_key(MOUND, MOUND_DARK, t))
                n += 1
    p.done()
    return n


CONTACT = (0.5, 0.45)     # within this of a root's surface: up to this mix of mound_dark


ROOT_SEED = [0]
ROOT_FUSE_TRIES = 5


def fuse_roots():
    """Root A and the fork fused (the fork's B into C), floor cut and cleaned. The sliver cleanup can fold a thin
    facet through a neighbour (a self-intersection that breaks the hero's union); the guard rebuilds the tube with
    the next facet-jitter seed until the fused piece is clean."""
    ROOT_INFO.clear()
    out = []
    for key, name, fn in (("A", "rootA", root_a), ("fork", "fork", root_fork)):
        for attempt in range(ROOT_FUSE_TRIES):
            ROOT_SEED[0] = 7 * attempt
            o, FUSE_LOG[key] = _fuse(PFX + name, fn, ground=True)
            FUSE_LOG[key]["seed_off"] = ROOT_SEED[0]
            if FUSE_LOG[key]["ok"]:
                break
        ROOT_SEED[0] = 0
        out.append(o)
    return tuple(out)


def _clump_fn(k, attempt=0):
    hub, nrm, span, seed, yaw, rise, back_up = CLUMPS[k]
    return lambda a: _leaf_module(a, (0, 0, 0), (0, 0, 1), span, seed + 1000 * attempt, 0.0,
                                  sink=0.14 + CLUMP_FLOAT.get(k, 0.0), rise=rise, back_up=back_up)


def fuse_clumps(tries=8):
    out = {}
    for k in CLUMPS:
        for attempt in range(tries):
            o, lg = _fuse(PFX + "clump_" + k, _clump_fn(k, attempt), fine=True)
            if lg["ok"]:
                break
        lg["attempt"] = attempt
        FUSE_LOG["clump_" + k] = lg
        out[k] = o
    return out


def fuse_leaf_part(tries=8):
    """The leaf part fused on its own, guarded like the hero clumps: leaves crossing at the hub can leave a bowtie
    vertex after the union and cleanup; then the next seed is tried."""
    for attempt in range(tries):
        o, lg = _fuse(PFX + "leafpart", lambda a, sd=PART_SEED + 1000 * attempt: _leaf_part_raw(a, sd), fine=True)
        if lg["ok"]:
            break
    lg["attempt"] = attempt
    FUSE_LOG["leafpart"] = lg
    return o


def _clump_matrices():
    """Each hero leaf module's matrix: its hub snapped onto the nearest surface of the mound and roots."""
    bm = bmesh.new()
    for nm in ("mound", "rootA", "fork"):
        o = bpy.data.objects[PFX + nm]
        tmp = o.data.copy()
        tmp.transform(Matrix.Translation(Vector(o[OFF])))
        bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    out = {}
    CLUMP_INFO.clear()
    for k, (hub, nrm, span, seed, yaw, rise, back_up) in CLUMPS.items():
        H, N = Vector(hub), Vector(nrm).normalized()
        # the hub drops along its own axis onto the first surface below the target (never left floating)
        loc, sn, _, dist = tree.ray_cast(H + N * 2.0, -N, 8.0)
        if loc is None:
            loc, sn, _, dist = tree.find_nearest(H)
        P = loc + sn * CLUMP_LIFT + N * CLUMP_FLOAT.get(k, 0.0)
        CLUMP_INFO[k] = {"moved": round((P - H).length, 2), "hub": [round(c, 2) for c in P]}
        out[k] = Matrix.Translation(P) @ _align(N, yaw + CLUMP_YAW_JIT[0]).to_4x4()
    return out


# ---- hero -------------------------------------------------------------------------------------------------------------
def _paste_obj(a, o, m=None):
    mat = (m if m is not None else Matrix.Identity(4)) @ Matrix.Translation(Vector(o[OFF]))
    return m011._paste(a, o, mat)


def hero(a):
    _paste_obj(a, bpy.data.objects[PFX + "mound"])
    _paste_obj(a, bpy.data.objects[PFX + "rootA"])
    _paste_obj(a, bpy.data.objects[PFX + "fork"])
    for k, m in _clump_matrices().items():
        _paste_obj(a, bpy.data.objects[PFX + "clump_" + k], m)


def mound_part(a):
    # round 2: the part takes the mound as fused, before the hero's root-contact darkening (on a bare mound those
    # dark bands read as smears where no root lies; the sheet's exploded mound has none)
    _paste_obj(a, bpy.data.objects.get(PFX + "mound_bare") or bpy.data.objects[PFX + "mound"])


def root_a_part(a):
    _paste_obj(a, bpy.data.objects[PFX + "rootA"])


def fork_part(a):
    _paste_obj(a, bpy.data.objects[PFX + "fork"])


NOTES = {
    "ArchedRootCluster": "root cluster resource node: a low lumpy faceted dirt/rock mound (lighter grey-brown stones "
                         "in the crevices, boulders round its foot) with three thick warm-orange faceted roots lying "
                         "over it from the crown - an inverted-J root and a forked root with a blunt bark stub - every "
                         "ground end a tapered pale cut tip with a ringed end face, three bright eight-leaf modules in "
                         "the crown crevices; one closed mesh, flat base. No VFX",
    "ArchedRootClusterMound": "Dirt Mound (Base, reusable): a lumpy faceted dirt dome of overlapping hull lumps, "
                              "lighter stone tops on the crown and upper-left lumps and the foot boulders, flat base",
    "ArchedRootClusterRootA": "Root Module (A, reusable): a thick faceted inverted-J root, both legs ending in pale "
                              "tapered cut tips (slanted collar, ringed end face)",
    "ArchedRootClusterRootFork": "Root Modules (B + C, reusable): one forked root - a blunt bark stub, the main limb "
                                 "C to a pale cut tip, branch B arching off its back to its own tip",
    "ArchedRootClusterLeafModule": "Leaf Module (reusable): eight broad pointed leaves in a star round a small dark "
                                   "hub, dark bases to lime tips",
}


# ---- cleanup (m019's procedure, this model's offset key) ---------------------------------------------------------------
def _bottom_centre(o):
    return m012._bottom_centre(o)


def _finish(o):
    o[OFF] = list(Vector(o[OFF]) + _bottom_centre(o))
    res = M.finish(o, union=False, uv=UV)
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
        res = M.finish(o, union=False, uv=UV)
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
        forced += m012._force_slivers(o, lim=POLISH_LIM, max_len=0.5)
    bc = _bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()
    M.smart_uv(o, **UV)
    return {"split": split, "forced": forced, "uv_cut": m012._uv_unfold(o)}


def _ground_faces(o):
    """Faces lying on the ground plane (the floor cut's caps): the plain mound key under the mound (a dark underside
    is a face-direction colour, which K.check rejects; it is never seen in game), cut under a tip, bark_dark under
    bark, by their neighbours' keys."""
    p = m011._Paint(o, off=o[OFF])
    n = 0
    for f in p.bm.faces:
        if all(abs(v.co.z) < 1e-3 for v in f.verts):
            nb = [p.key(g) for e in f.edges for g in e.link_faces if g is not f]
            if any(k.startswith("m021_cut") for k in nb):
                key = CUT
            elif any(k.startswith("m021_bark") for k in nb) and not any(k.startswith(MOUND) for k in nb):
                key = BARK_DARK
            else:
                key = MOUND
            f.material_index = p._mi(key)
            n += 1
    p.done()
    return n


# ---- build -------------------------------------------------------------------------------------------------------------
PARTS = (("ArchedRootClusterMound", mound_part), ("ArchedRootClusterRootA", root_a_part),
         ("ArchedRootClusterRootFork", fork_part), ("ArchedRootClusterLeafModule", leaf_part))
UNION_PARTS = {"ArchedRootClusterLeafModule"}
HERO = "ArchedRootCluster"


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)


def _make(name, fn, role, budget):
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget, collision="hull",
             tint_var=0.04)
    off = M._build_offset(fn)
    o[OFF] = list(off)
    lg = {}
    if name in UNION_PARTS or role == "hero":
        lg["shells_merged"] = _union_fine(o, HERO_MERGE)
    if role == "hero":
        m016._floor_cut(o, -off.z)
        o[OFF] = [off.x, off.y, 0.0]
        lg["clean"] = m016._clean_mesh(o, (0.0,))
    elif name in UNION_PARTS:
        lg["clean"] = m016._clean_mesh(o, ())
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    lg["bowties"] = _split_bowties(o)
    if role == "hero" or name in ("ArchedRootClusterMound", "ArchedRootClusterRootA", "ArchedRootClusterRootFork"):
        lg["ground_faces"] = _ground_faces(o)
    return o, lg


def prepare():
    """The fused temporary pieces: mound, roots conformed on it, contact paint, leaf modules."""
    palette()
    FUSE_LOG.clear()
    SUPPORTS.clear()
    fuse_mound()
    # supports in two rounds: the roots laid on the bare mound, supports under what floats; then laid again on the
    # supported mound (B's start follows C, which may have moved) and supports added under anything still floating
    FUSE_LOG["supports"] = []
    for _ in range(SUPPORT_ROUNDS):
        ROOT_INFO.clear()
        for name in ("A", "C", "B"):
            _root_layout(name)
        added = plan_supports()
        FUSE_LOG["supports"].append(added)
        if not added:
            break
        m = fuse_mound()
    m = bpy.data.objects[PFX + "mound"]
    fuse_roots()
    old = bpy.data.objects.get(PFX + "mound_bare")
    if old:
        me = old.data
        bpy.data.objects.remove(old, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    bare = m.copy()
    bare.data = m.data.copy()
    bare.name = PFX + "mound_bare"
    for c in m.users_collection:
        c.objects.link(bare)
    FUSE_LOG["contact_faces"] = _contact_paint(m)
    FUSE_LOG["root_tries"] = dict(ROOT_TRIES)
    fuse_clumps()
    fuse_leaf_part()
    return dict(FUSE_LOG)


def build(render=True, parts=True, keep_tmp=False):
    M.coll(NUM, TITLE)
    log = {"prepare": prepare()}
    objs = {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn, "part", 1000)
    # the hero guard: a leaf grazing a root or a crease can leave a hole or a fold after the union and cleanup; then
    # every leaf module turns HERO_YAW_STEP degrees about its own axis and the hero is rebuilt (m019's guard)
    for attempt in range(HERO_TRIES):
        CLUMP_YAW_JIT[0] = HERO_YAW0 + attempt * HERO_YAW_STEP
        h, log["hero"] = _make(HERO, hero, "hero", 4000)
        if _fused_ok(h):
            break
    log["hero"]["ok"] = _fused_ok(h)
    log["hero"]["attempt"] = attempt
    log["clumps"] = dict(CLUMP_INFO)
    log["roots"] = {k: {kk: v[kk] for kk in ("L", "rings", "gaps")} for k, v in ROOT_INFO.items()}
    if not keep_tmp:
        _cleanup_tmp()
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    out = {"audit": [{k: M.audit(o)[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges",
                                                     "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces",
                                                     "normals", "ngons")}
                     for o in order],
           "thin": {o.name: m012._thin(o, POLISH_LIM) for o in order}, "log": log,
           "self_hits": {o.name: m016._self_hits(o)[0] for o in order}, "problems": K.check(order),
           "uv": {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped",
                                                                            "min_gap", "density",
                                                                            "stretch_conformal_p95")}
                  for o in order}}
    if render:
        out["views"] = render_views(order)
    return out


# ---- renders ----------------------------------------------------------------------------------------------------------
SHEET_CAMS = {"f34_sheet": (0, 20), "r34_sheet": (-12, 15), "side_sheet": (90, 8), "top_sheet": (0, 50)}
EXPL = {"ArchedRootClusterMound": (0, 0, 0), "ArchedRootClusterRootA": (-2.4, -0.4, 2.6),
        "ArchedRootClusterRootFork": (2.4, -0.2, 2.8), "ArchedRootClusterLeafModule": (0.3, 0.4, 7.0)}
# round 2: the fork turned about its own origin in the exploded shot, so B and C read as two limbs (not end-on)
EXPL_ROT = {"ArchedRootClusterRootFork": -45.0}
# part shots: the fork from the front-right, so B shows beside C instead of hiding behind it
PART_CAMS = {"ArchedRootClusterRootFork": (40, 28), "ArchedRootClusterLeafModule": (-20, 30)}


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded Construction; returns the temporary objects."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []
    x0 = objs[0].location.x + 40
    base = Matrix.Translation((x0, objs[0].location.y, 0))
    for name, dv in EXPL.items():
        if name not in by:
            continue
        o = by[name]
        c = bpy.data.objects.new(f"{PFX}expl_{name}", o.data)
        coll.objects.link(c)
        if name == "ArchedRootClusterLeafModule":
            m = Matrix.Translation(Vector(dv))
        else:
            m = (Matrix.Translation(Vector(dv)) @ Matrix.Translation(Vector(o[OFF])) @
                 Matrix.Rotation(math.radians(EXPL_ROT.get(name, 0.0)), 4, "Z"))
        c.matrix_world = base @ m
        shown.append(c)
    bpy.context.view_layer.update()
    return shown


def render_close(objs, path, az, el, centre, radius):
    kit = K.NS["KIT"]
    fb = kit["frame_box"]
    c = Vector(centre)
    box = [c + Vector((dx, dy, dz)) * radius for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    kit["frame_box"] = lambda corners, a_, e_: fb(box, a_, e_)
    ground = bpy.data.objects.get("FB_Ground")
    if ground:
        ground.hide_render = el < 0
    old = kit["CELL"]
    kit["CELL"] = (480, 400)
    try:
        return kit["render_group"](objs, path, az, el)
    finally:
        kit["frame_box"] = fb
        kit["CELL"] = old
        if ground:
            ground.hide_render = False


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_CAMS.items()}
        if shown:
            extra["exploded"] = (shown, -20, 15)
        for o in objs[1:]:
            az, el = PART_CAMS.get(o.name, (-20, 15))
            extra["part_" + o.name.replace("ArchedRootCluster", "").lower()] = ([o], az, el)
        sheet = M.views(NUM, [h], extra=extra)
        out = {"sheet": sheet}
        if close:
            d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
            off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
            out["junction_cu"] = render_close([h], f"{d}/junction_cu.png", -20, 25,
                                              off @ Vector((2.9, -1.4, 2.2)), 1.5)
            sts = [s for s in ROOT_INFO.get("A", {}).get("stations", []) if s[2] == "end"]
            tip = Vector(sts[0][0]) if sts else Vector((-2.15, -3.75, 0.5))
            out["tip_cu"] = render_close([h], f"{d}/tip_cu.png", -30, 10, off @ tip, 0.9)
        return out
    finally:
        for o in shown:
            bpy.data.objects.remove(o, do_unlink=True)
        M.display(NUM, objs, TITLE)
