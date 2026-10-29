"""038 Pebble Scatter (references/038.png): a loose ring of five separate warm grey-pink faceted rocks round an open
patch of ground: C, a big low flat slab at the front left (an extruded plan polygon: a quiet faceted top, a uniform
side band, a front vertex and a flat underside) with a lobed lime moss pad on its back-left corner; A, a tall blunt
bullet rock behind; B, a medium boxy rock at the right with a star-shaped lime moss pad on its top; D, a chunky wedge
with a tilted top at the front right; E, a small squat pebble in the A-B gap. Round-leaf plant clusters with white
five-petal flowers sit at their feet.

    import importlib, kit_models, m038; importlib.reload(kit_models); importlib.reload(m038); m038.build()

Build frame: studs, front -Y, +X right, ground z 0; every object ends with its origin at its bbox bottom centre.
W01 owns Pebble*, W07 GroundScatter*, so the names are StoneScatter* (spec 8):
- StoneScatterTallRock (tall_rock_part): rock A with its two foot clumps.
- StoneScatterMediumRock (medium_rock_part): rock B with its moss pad MB.
- StoneScatterFlatSlab (flat_slab_part): slab C with its moss pad MC, a back-edge clump and a left-foot cluster.
- StoneScatterWedgeRock (wedge_rock_part): rock D, bare.
- StoneScatterRoundRock (round_rock_part): pebble E, bare (the hero's 0.7 pebble, decision 4).
- StoneScatterFlowerClump (flower_clump_part): one loose clover cluster with a flower.

The hero (StoneScatter, decision 6) is one object of separate closed shells: each rock, each moss pad (a thick lobed
shell wrapped onto its rock), and each leaf, petal and flower centre. No booleans. Every leaf and flower is seated on
the ground, a rock or another leaf (contact <= 0.03, chained to the ground or a rock; STAGES "No floating dressing"),
and a settle pass drops any piece that still hangs. Colour (stage 4) is painted by position inside the builders, per
flat facet. Stages 5-6: nothing (decision 8: no emission, light or contact-shadow VFX). See M038_spec.md.
"""
import math
import random
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt

import kit_mcp as K
import kit_models as M
import m012
import m033
import m036

NUM, TITLE, SHEET = 38, "Pebble Scatter", "M038"
OFF = "m038_offset"
PFX = "_m038_"
HERO = "StoneScatter"
A_P, B_P, C_P = "StoneScatterTallRock", "StoneScatterMediumRock", "StoneScatterFlatSlab"
D_P, E_P, FC_P = "StoneScatterWedgeRock", "StoneScatterRoundRock", "StoneScatterFlowerClump"

ROCK, ROCK_LIGHT, ROCK_DEEP = "m038_rock", "m038_rock_light", "m038_rock_deep"
MOSS, MOSS_SUN, MOSS_DEEP = "m038_moss", "m038_moss_sun", "m038_moss_deep"
LEAF, LEAF_YOUNG, LEAF_DEEP = "m038_leaf", "m038_leaf_young", "m038_leaf_deep"
PETAL, POLLEN = "m038_petal", "m038_pollen"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low specular). Stage 4 (M038_spec.md "Stage 4") writes the calibrated values here.
PALETTE = {
    ROCK: ("#A28F84", 0.9, False),
    ROCK_LIGHT: ("#AC998E", 0.9, False),
    ROCK_DEEP: ("#917E73", 0.9, False),
    MOSS: ("#899E03", 0.9, True),
    MOSS_SUN: ("#ABAE07", 0.9, True),
    MOSS_DEEP: ("#627E04", 0.9, True),
    LEAF: ("#84A102", 0.85, True),
    LEAF_YOUNG: ("#A0AE0B", 0.85, True),
    LEAF_DEEP: ("#3F6C02", 0.85, True),
    PETAL: ("#C8C5BE", 0.7, False),
    POLLEN: ("#BE9F00", 0.7, False),
}
# calibration targets (spec 5.4: rendered medians of unshadowed regions: the exploded parts, the parts row). Kinds for
# K.sample: the warm rock is sat ~0.2 (the stone filter drops > 0.18) so "all"; the lime moss "vivid".
TARGETS = {ROCK: ((0xC9, 0xAC, 0x9C), "all"), ROCK_LIGHT: ((0xD8, 0xBF, 0xB2), "all"),
           ROCK_DEEP: ((0xB3, 0x9A, 0x8C), "all"),
           MOSS: ((0xAA, 0xC0, 0x05), "vivid"), MOSS_SUN: ((0xD8, 0xD5, 0x0A), "vivid"),
           MOSS_DEEP: ((0x73, 0x90, 0x05), "vivid"),
           LEAF: ((0x98, 0xB7, 0x04), "green"), LEAF_YOUNG: ((0xC9, 0xD6, 0x0D), "vivid"),
           LEAF_DEEP: ((0x4A, 0x7A, 0x03), "green"),
           PETAL: ((0xF6, 0xF2, 0xE8), "all"), POLLEN: ((0xF0, 0xC2, 0x0C), "vivid")}
SPEC = {}
ROCK_KEYS = (ROCK, ROCK_LIGHT, ROCK_DEEP)


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    _spec()


def _spec():
    for m in bpy.data.materials:
        if not m.name.startswith("FB_m038_") or not m.node_tree:
            continue
        key = m.name[3:]
        lvl = next((v for p, v in SPEC.items() if key.startswith(p)), None)
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if lvl is not None and bsdf and "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = lvl


def warm_ok(hexcol):
    """The mauve guard (decision 10): R > G > B, hue 12-26 deg, R - B >= 30."""
    r, g, b = (int(hexcol.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    if not (r > g > b) or r - b < 30:
        return False
    hue = 60.0 * (g - b) / (r - b)
    return 12.0 <= hue <= 26.0


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome. Returns {key: (hex, rendered)};
    a rock key that comes out of the mauve guard is flagged (and must not be written into PALETTE)."""
    keys = keys or list(TARGETS)
    for k in keys:
        K.fk().material(k)
    try:
        res = K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)
    for k in keys:
        if k in ROCK_KEYS and not warm_ok(res[k][0]):
            res[k] = (res[k][0], res[k][1], "REJECTED: fails the warm-stone guard")
    return res


# ---- small helpers -----------------------------------------------------------------------------------------------------
_faces = m033._faces
_place = m033._place
_hull_bm = m036._hull_bm
_regions = m036._regions
_centroid = m036._centroid
_tint_regions = m036._tint_regions


def _q(t, steps=3):
    t = max(0.0, min(1.0, t))
    return round(t * steps) / steps


def _mottle(a, faces, amp, scale, seed, tint=1.0):
    m033._mottle(a, faces, amp, scale, seed, tint)


def _tri(bm, faces):
    bmesh.ops.triangulate(bm, faces=[f for f in faces if f.is_valid and len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")


# ---- rocks A, B, D, E (spec 1.4, 2.1, 2.2) ----------------------------------------------------------------------------
# Point clouds: rings (height fraction, radius fraction, points) from the floor up, jittered, then flattened by cut
# planes (unit normal, distance from (0, 0, zc), zc) into a few big flat facets (m036). tilt: the top falls from the
# back-left to the front-right (D's wedge): z *= tilt[0] - tilt[1] * s, s = (x - y) / sqrt 2. The cloud is yawed and
# scaled to the rock's exact world size (an affine map keeps the hull).
CLOUDS = {
    # A: a blunt bullet, widest at h .35-.5, a small crown over the left of its width (lean), long sliver facets on the
    # right flank (more points there), a broad lit front facet and a broad shaded left facet
    "A": dict(rings=((0.0, 0.82, 8), (0.14, 0.93, 6), (0.30, 0.99, 8), (0.48, 1.0, 7), (0.68, 0.84, 8),
                     (0.86, 0.58, 6), (1.0, 0.30, 4)), jit=0.14, lean=(-0.42, 0.05), seed=38101,
              cuts=(((0.12, -1.0, 0.16), 0.76, 0.40),       # broad lit front facet
                    ((0.85, -0.55, 0.12), 0.80, 0.50),      # front-right facet
                    ((-1.0, -0.15, 0.22), 0.80, 0.45),      # broad shaded left flank
                    ((0.10, 1.0, 0.12), 0.82, 0.40),        # back
                    ((-0.30, 0.10, 1.0), 0.0, 0.985))),     # small blunt crown
    # B: a chunky rounded block, steep bulging sides, one broad near-flat top facet sloping to the front-right, a
    # big front-left face
    "B": dict(rings=((0.0, 0.86, 8), (0.25, 0.98, 7), (0.52, 1.0, 8), (0.80, 0.92, 7), (1.0, 0.70, 5)),
              jit=0.09, lean=(0.0, 0.0), seed=38102,
              cuts=(((0.10, -0.12, 1.0), 0.0, 0.93),         # broad top facet, sloping 8 deg to the front-right
                    ((-0.72, -0.70, 0.12), 0.86, 0.45),      # large front-left face
                    ((1.0, 0.12, 0.05), 0.88, 0.50))),       # steep right end
    # D: a chunky faceted wedge, apex over the back-left third, the top falling 20-25 deg to the front-right, many
    # facets of similar size (no dominant face)
    "D": dict(rings=((0.0, 0.85, 7), (0.26, 1.0, 7), (0.52, 0.97, 6), (0.78, 0.80, 6), (1.0, 0.48, 4)),
              jit=0.12, lean=(-0.25, 0.20), seed=38104, tilt=(0.80, 0.30),
              cuts=(((0.42, -0.42, 1.0), 0.0, 0.75),        # the tilted top facet, falling to the front-right
                    ((-1.0, 0.0, 0.25), 0.90, 0.35))),      # steep shaded left face
    # E: a squat pebble, one big top facet
    "E": dict(rings=((0.0, 0.86, 6), (0.40, 1.0, 6), (0.78, 0.76, 5), (1.0, 0.36, 3)), jit=0.12, lean=(0.0, 0.0),
              seed=38105, cuts=(((0.10, 0.05, 1.0), 0.0, 0.90),)),
}
# name -> cloud, centre (x, y), world size (W, D, H), yaw (deg)  (spec 2.1)
ROCKS = {
    "A": ("A", (0.72, 3.30), (3.1, 2.3, 3.0), 5.0),
    "B": ("B", (4.12, 1.30), (2.85, 2.4, 1.5), 15.0),
    "D": ("D", (2.39, -3.25), (2.7, 2.0, 1.5), -10.0),
    "E": ("E", (2.25, 1.75), (0.7, 0.6, 0.42), 30.0),
}
ROCK_INFO = {}


def _cloud(name):
    cp = CLOUDS[name]
    rng = random.Random(cp["seed"])
    pts = m033._ring_pts(rng, cp["rings"], 1.0, 1.0, 1.0, cp["jit"], cp["lean"], ang_jit=0.30)
    if cp.get("tilt"):
        t0, t1 = cp["tilt"]
        for p in pts:
            if p.z > 1e-6:
                p.z *= t0 - t1 * (p.x - p.y) / math.sqrt(2)
    for n, d, zc in cp["cuts"]:
        n = Vector(n).normalized()
        c = Vector((0.0, 0.0, zc))
        for p in pts:
            s = (p - c).dot(n) - d
            if s <= 0:
                continue
            if p.z < 1e-6:          # floor points slide horizontally: the floor stays flat
                nh = Vector((n.x, n.y, 0.0))
                if nh.length > 1e-6:
                    p -= nh.normalized() * (s / nh.length)
            else:
                p -= n * s
                p.z = max(0.0, p.z)
    return pts


def _rock_pts(name, centre=None):
    cloud, c, size, yaw = ROCKS[name]
    c = centre if centre is not None else c
    pts = [Matrix.Rotation(math.radians(yaw), 3, "Z") @ p for p in _cloud(cloud)]
    xs, ys, zs = [p.x for p in pts], [p.y for p in pts], [p.z for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    sx, sy, sz = size[0] / (max(xs) - min(xs)), size[1] / (max(ys) - min(ys)), size[2] / max(zs)
    return [Vector(((p.x - cx) * sx + c[0], (p.y - cy) * sy + c[1], p.z * sz)) for p in pts]


# Rock colour (spec 5.3, 5.5): per flat facet, by the facet centroid's position only. Broad noise patches on the upper
# half -> rock_light; broad patches low on the rock -> rock_deep; the floor plain rock; then Tint per facet.
LIGHT = dict(scale=0.42, level=0.05, width=0.30, mix=0.85, h0=0.45, seed=38111)
DEEP = dict(scale=0.40, level=0.10, width=0.30, mix=0.80, h1=0.40, seed=38112)
ROCK_MOTTLE = dict(amp=0.045, scale=0.30, seed=38121)
SLAB_TOP_LIGHT = 0.30       # C's top: a 30 % lift toward rock_light everywhere (spec 5.4: C's top at 30 %)


def _paint_rock(a, vs, seed, H, slab=False):
    fs = _faces(vs)
    floor = [f for f in fs if f.normal.z < -0.99 and f.calc_center_median().z < 1e-3]
    fl = set(floor)
    side = [f for f in fs if f not in fl]
    regs = _regions(side)
    nl = K.noise_field(LIGHT["scale"], LIGHT["seed"] + seed)
    nd = K.noise_field(DEEP["scale"], DEEP["seed"] + seed)
    for reg in regs:
        c = _centroid(reg)
        hf = c.z / H
        tl = _q((nl(c) - LIGHT["level"]) / LIGHT["width"]) if hf > LIGHT["h0"] else 0.0
        td = _q((nd(c) - DEEP["level"]) / DEEP["width"]) if hf < DEEP["h1"] else 0.0
        if slab and hf > 0.93:
            tl = max(tl * LIGHT["mix"], SLAB_TOP_LIGHT) / LIGHT["mix"]
        if td > 0 and td >= tl:
            key = K.mix_key(ROCK, ROCK_DEEP, round(td * DEEP["mix"], 2))
        elif tl > 0:
            key = K.mix_key(ROCK, ROCK_LIGHT, round(min(1.0, tl * LIGHT["mix"]), 2))
        else:
            key = ROCK
        mi = a._mi(key)
        for f in reg:
            f.material_index = mi
    mi = a._mi(ROCK)
    for f in floor:
        f.material_index = mi
    _tint_regions(a, regs, ROCK_MOTTLE["amp"], ROCK_MOTTLE["scale"], ROCK_MOTTLE["seed"] + seed,
                  tint=1.0 + random.Random(seed).uniform(-0.04, 0.04))
    return regs


def _rock(a, name, centre=None):
    """One rock shell: hull, painted, its shape metrics recorded. Returns its verts."""
    c = centre if centre is not None else ROCKS[name][1]
    vs = _hull_bm(a.bm, _rock_pts(name, c))
    a._finish(vs, ROCK, tint=1.0)
    _paint_rock(a, vs, sum(map(ord, name)) + 38000, ROCKS[name][2][2])
    ROCK_INFO[name] = dict(centre=[round(x, 2) for x in c], **rock_metrics(_faces(vs), c))
    return vs


# ---- slab C (spec 1.4 Rock C, 3.8): an extruded plan polygon, not a ring hull --------------------------------------------
# plan (x, y as fractions of L/2, D/2), a straight back edge, chamfered ends, a front vertex at 0.44 L from the left end
SLAB_PLAN = ((-0.80, 1.00), (-0.15, 0.98), (0.47, 0.93), (0.88, 0.42), (1.00, -0.10), (0.45, -0.56),
             (-0.12, -1.00), (-0.60, -0.58), (-1.00, -0.06), (-0.95, 0.52))
SLAB = dict(L=5.8, D=4.0, T=1.5, yaw=-8.0, centre=(-1.73, -1.60), seed=38103, jit=0.035)
# (z, inset): the lower chamfer tucks in 0.28 to the flat underside, the side band leans out 0.05, the top bevel
# tucks in 0.16 (~37 deg)
SLAB_RINGS = ((0.0, 0.28), (0.30, 0.0), (1.33, -0.05), (1.50, 0.16))
SLAB_TOP_IN = ((-0.42, 0.30, 0.13), (0.30, -0.12, 0.17))   # interior top verts (x, y fractions, lift)
SLAB_TILT = (-0.035, 0.030)       # z += T * (tx * x + ty * y) (fractions): highest at the back-left, ~1.5 deg
SLAB_TOP_JIT = 0.035


def _inset(poly, d):
    """Offset a closed 2D polygon inward by d (outward for d < 0): miter offset of each vertex."""
    n = len(poly)
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    sgn = 1.0 if area > 0 else -1.0          # CCW: the inward normal is the edge rotated left
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % n])
        e1, e2 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n1 = Vector((-e1.y, e1.x)) * sgn
        n2 = Vector((-e2.y, e2.x)) * sgn
        m = n1 + n2
        k = 1.0 + n1.dot(n2)
        out.append(p1 + m * (d / max(k, 0.2)))
    return out


def _slab(a, centre=None, yaw=None):
    """Slab C: four stacked rings of the plan polygon (chamfer, band, bevel), a flat bottom cap and a quiet top of
    12 broad facets (two interior verts lifted a little; no dome). Returns its verts."""
    sp = SLAB
    rng = random.Random(sp["seed"])
    bm = a.bm
    L, D, T = sp["L"], sp["D"], sp["T"]
    plan = [Vector((x * L / 2 + rng.uniform(-1, 1) * sp["jit"], y * D / 2 + rng.uniform(-1, 1) * sp["jit"]))
            for x, y in SLAB_PLAN]
    tx, ty = SLAB_TILT

    def zt(p, z):
        return z + (z / T) * T * (tx * p.x / (L / 2) + ty * p.y / (D / 2))
    rings = []
    for ri, (z, ins) in enumerate(SLAB_RINGS):
        pts = _inset(plan, ins) if abs(ins) > 1e-9 else plan
        ring = []
        for p in pts:
            jz = rng.uniform(-1, 1) * SLAB_TOP_JIT if 0 < ri else 0.0
            ring.append(bm.verts.new((p.x, p.y, max(0.0, zt(p, z) + (jz if z > 0 else 0.0)))))
        rings.append(ring)
    faces = []
    n = len(plan)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(n):
            j = (k + 1) % n
            faces.append(bm.faces.new((r0[k], r0[j], r1[j], r1[k])))
    # bottom: the plan triangulated flat (CDT of the ring)
    bot = rings[0]
    co = [(v.co.x, v.co.y) for v in bot]
    res = delaunay_2d_cdt(co, [(k, (k + 1) % n) for k in range(n)], [list(range(n))], 1, 1e-6)
    for f in res[2]:
        ids = [res[3][i][0] for i in f]
        faces.append(bm.faces.new([bot[i] for i in reversed(ids)]))
    # top: ring + interior verts, CDT inside the ring
    top = rings[-1]
    inner = []
    for x, y, lift in SLAB_TOP_IN:
        p = Vector((x * L / 2, y * D / 2))
        inner.append(bm.verts.new((p.x, p.y, zt(p, T) + lift)))
    allv = top + inner
    co = [(v.co.x, v.co.y) for v in allv]
    res = delaunay_2d_cdt(co, [(k, (k + 1) % n) for k in range(n)], [list(range(n))], 1, 1e-6)
    for f in res[2]:
        ids = [res[3][i][0] for i in f]
        faces.append(bm.faces.new([allv[i] for i in ids]))
    _tri(bm, faces)
    vs = [v for r in rings for v in r] + inner
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    c = centre if centre is not None else sp["centre"]
    _place(bm, vs, Matrix.Translation((c[0], c[1], 0.0)) @
           Matrix.Rotation(math.radians(sp["yaw"] if yaw is None else yaw), 4, "Z"))
    a._finish(vs, ROCK, tint=1.0)
    _paint_rock(a, vs, 38103, T, slab=True)
    ROCK_INFO["C"] = dict(centre=[round(x, 2) for x in c], **rock_metrics(_faces(vs), c), **slab_metrics(_faces(vs)))
    return vs


def slab_metrics(fs):
    """Spec 2.2 for C: top faces (normal z > 0.97) and their share of the top area, the steepest non-bevel top face,
    band heights round the plan."""
    zs = [v.co.z for f in fs for v in f.verts]
    T = max(zs)
    top = [f for f in fs if f.calc_center_median().z > T - 0.35 and f.normal.z > 0.5]
    flat = [f for f in top if f.normal.z > 0.97]
    a_top = sum(f.calc_area() for f in top)
    a_flat = sum(f.calc_area() for f in flat)
    bevel = [f for f in top if f.normal.z <= 0.97]
    steep = max((math.degrees(math.acos(min(1.0, f.normal.z))) for f in flat), default=0.0)
    return {"top_faces": len(flat), "top_flat_share": round(a_flat / max(a_top, 1e-9), 2),
            "top_steepest_deg": round(steep, 1), "bevel_faces": len(bevel),
            "bevel_deg": [round(min(math.degrees(math.acos(min(1.0, f.normal.z))) for f in bevel), 1),
                          round(max(math.degrees(math.acos(min(1.0, f.normal.z))) for f in bevel), 1)] if bevel else []}


def rock_metrics(fs, centre=(0.0, 0.0), view=(0.0, 27.0)):
    """m036.rock_metrics (spec 2.2) plus: triangles with a corner under 25 deg, flat regions at 7 deg seen from the parts
    camera (az 0, el 27) with the largest one's share, and the regular-ring count."""
    out = m036.rock_metrics(fs)
    side = [f for f in fs if not (f.normal.z < -0.99 and f.calc_center_median().z < 1e-3)]
    small = 0
    for f in side:
        p = [v.co for v in f.verts]
        angs = [(p[(i + 1) % 3] - p[i]).angle(p[(i + 2) % 3] - p[i], 0.0) for i in range(3)]
        small += min(angs) < math.radians(25)
    regs = _regions(side, ang=7.0)
    az, el = math.radians(view[0]), math.radians(view[1])
    vv = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    proj = [sum(g.calc_area() * max(0.0, g.normal.dot(vv)) for g in reg) for reg in regs]
    tot = sum(proj) or 1.0
    seen = sorted([p / tot for p in proj if p / tot >= 0.004], reverse=True)
    out.update({"small_angle_share": round(small / max(1, len(side)), 2), "facets7_seen": len(seen),
                "largest7_share": round(seen[0], 3) if seen else 0})
    return out


# ---- moss pads (spec 1.4 B / C, 2.3): thick lobed shells wrapped onto their rock ---------------------------------------
# name -> rock, centre (x, y) offset from the rock centre, radius (rx, ry), lobes, pointed (star) or blunt lobes,
# notch depth (fraction of r), thickness (rim, mid, centre), yaw (deg), depth of the wrap point below the top, seed
PADS = {
    "MB": dict(rock="B", at=(0.38, -0.24), r=(0.98, 0.80), lobes=7, pointed=True, notch=0.66,
               th=(0.09, 0.17, 0.27), yaw=20.0, wrap=0.34, seed=38201, sun=0.0),
    "MC": dict(rock="C", at=(-2.30, 1.25), r=(0.90, 0.70), lobes=7, pointed=False, notch=0.66,
               th=(0.08, 0.14, 0.20), yaw=-30.0, wrap=0.45, seed=38202, sun=0.34),
}
PAD_SINK = 0.03
PAD_MOTTLE = dict(amp=0.05, scale=0.8, seed=38211)
PAD_INFO = {}


def _pad(a, name, rock_vs, rock_centre, rock_yaw=0.0):
    """One moss pad: a lobed outline (pointed star lobes or blunt rounded ones, a notch between), a mid ring on the
    lobe axes and a centre, as a top layer and a bottom layer joined by a rim band. Each top / bottom pair is wrapped
    onto the rock along a ray toward a point inside the rock under the pad, so lobes past the edge drape down the side;
    the bottom sits PAD_SINK inside the surface, the top the pad's thickness out. Coloured by place on the pad: the
    raised centre and lobe ridges sun-yellow, the body moss, the notches and the rim deep. Returns its verts."""
    pp = PADS[name]
    rng = random.Random(pp["seed"])
    bm = a.bm
    tree = K.bvh_of(rock_vs)
    rx, ry = pp["r"]
    nl = pp["lobes"]
    step = 2 * math.pi / nl
    off = rng.uniform(0, 2 * math.pi)
    outline = []          # (angle, radius fraction, kind, lobe)
    for k in range(nl):
        th = off + k * step + rng.uniform(-0.08, 0.08) * step
        rl = rng.uniform(0.86, 1.06)
        if pp["pointed"]:
            outline.append((th - 0.30 * step, rl * 0.84, "tip", k))     # broad maple lobe, a pointed tip
            outline.append((th, rl * 1.04, "tip", k))
            outline.append((th + 0.30 * step, rl * 0.84, "tip", k))
        else:
            outline.append((th - 0.24 * step, rl * 0.96, "tip", k))
            outline.append((th, rl * 1.02, "tip", k))
            outline.append((th + 0.24 * step, rl * 0.96, "tip", k))
        outline.append((th + 0.5 * step, pp["notch"] * rng.uniform(0.92, 1.08), "notch", k))
    rot = Matrix.Rotation(math.radians(pp["yaw"] + rock_yaw), 2)
    c0 = Vector((rock_centre[0], rock_centre[1])) + Matrix.Rotation(math.radians(rock_yaw), 2) @ Vector(pp["at"])

    def plan(th, rf):
        return c0 + rot @ Vector((math.cos(th) * rf * rx, math.sin(th) * rf * ry))
    pts = [(plan(th, rf), pp["th"][0], kind, k) for th, rf, kind, k in outline]
    mids = [(plan(off + k * step, 0.48 * rng.uniform(0.92, 1.08)), pp["th"][1] * rng.uniform(0.9, 1.1), "mid", k)
            for k in range(nl)]
    cen = (plan(0.0, 0.0) + Vector((rng.uniform(-0.05, 0.05), rng.uniform(-0.05, 0.05))), pp["th"][2], "cen", -1)
    hz = tree.ray_cast(Vector((c0.x, c0.y, 60.0)), Vector((0, 0, -1)), 200)[0]
    ztop = hz.z if hz is not None else 1.0

    def wrap(p2, th):
        """Where the pad point p2 (plan) lands, continuously: o = how far the point at the pad's seat height lies
        off the rock (0 over the top, its overhang past an edge or a falling shoulder); the point then drops by o
        (at most pp['wrap']) and goes to the nearest rock surface. Over the top that is straight down; past an edge
        the lobe drapes down the side by about its overhang."""
        q0 = Vector((p2.x, p2.y, ztop - 0.06))
        o = tree.find_nearest(q0)[3]
        q1 = Vector((p2.x, p2.y, ztop - 0.06 - min(o, pp["wrap"])))
        loc, fn, _, d = tree.find_nearest(q1)
        nrm = fn
        if d > 0.02 and (q1 - loc).dot(fn) > 0:
            nrm = ((q1 - loc).normalized() + fn).normalized()   # outside an edge: lean the normal toward the point
        return bm.verts.new(loc - nrm * PAD_SINK), bm.verts.new(loc + nrm * (th - PAD_SINK)), nrm
    T, B = [], []
    for p2, th, kind, k in pts + mids + [cen]:
        b, t, _ = wrap(p2, th)
        B.append(b)
        T.append(t)
    n = len(pts)
    mid_i = list(range(n, n + nl))
    ci = n + nl
    owner = [k for _, _, _, k in pts]
    kinds = [kd for _, _, kd, _ in pts]
    top_f = {"cen": [], "ridge": [], "valley": [], "rim": []}
    bot_f = []

    def tri(L, i, j, k, top=True):
        f = bm.faces.new((L[i], L[j], L[k]) if top else (L[k], L[j], L[i]))
        return f
    for k in range(nl):
        top_f["cen"].append(tri(T, ci, mid_i[k], mid_i[(k + 1) % nl]))
        bot_f.append(tri(B, ci, mid_i[k], mid_i[(k + 1) % nl], top=False))
    for i in range(n):
        j = (i + 1) % n
        oi, oj = owner[i], owner[j]
        grp = "valley" if "notch" in (kinds[i], kinds[j]) else "ridge"
        if oi == oj:
            top_f[grp].append(tri(T, i, j, mid_i[oi]))
            bot_f.append(tri(B, i, j, mid_i[oi], top=False))
        else:
            top_f[grp].append(tri(T, i, j, mid_i[oj]))
            top_f["valley"].append(tri(T, i, mid_i[oj], mid_i[oi]))
            bot_f.append(tri(B, i, j, mid_i[oj], top=False))
            bot_f.append(tri(B, i, mid_i[oj], mid_i[oi], top=False))
        top_f["rim"].append(bm.faces.new((T[i], B[i], B[j])))
        top_f["rim"].append(bm.faces.new((T[i], B[j], T[j])))
    vs = T + B
    allf = [f for g in top_f.values() for f in g] + bot_f
    bmesh.ops.recalc_face_normals(bm, faces=allf)
    a._finish(vs, MOSS, tint=1.0)
    sun = pp["sun"]

    def key(t):           # t: 0 deep, 0.5 moss, 1 sun; MC shifted toward sun
        t = min(1.0, t + sun)
        if t < 0.5:
            return K.mix_key(MOSS, MOSS_DEEP, round((0.5 - t) * 2 * 0.9, 2))
        return K.mix_key(MOSS, MOSS_SUN, round((t - 0.5) * 2, 2))
    for f in top_f["cen"]:
        f.material_index = a._mi(key(0.9))
    for f in top_f["ridge"]:
        f.material_index = a._mi(key(0.7))
    for f in top_f["valley"]:
        f.material_index = a._mi(key(0.5 if len([v for v in f.verts if v in set(T[n:])]) == 2 else 0.25))
    for f in top_f["rim"] + bot_f:
        f.material_index = a._mi(key(0.0 if f in set(top_f["rim"]) else 0.5))
    _mottle(a, [f for g in top_f.values() for f in g], PAD_MOTTLE["amp"], PAD_MOTTLE["scale"],
            PAD_MOTTLE["seed"] + pp["seed"])
    xs, ys, zs = [v.co.x for v in vs], [v.co.y for v in vs], [v.co.z for v in vs]
    PAD_INFO[name] = dict(span=[round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2)],
                          z=[round(min(zs), 2), round(max(zs), 2)], drape=round(ztop - min(zs), 2), tris=len(allf))
    return vs


# ---- leaves, flowers, clusters (spec 1.4 Plants, 2.3) -------------------------------------------------------------------
# Leaves: broad round-tipped spatulate solids (narrow at the stem, widest at 0.5-0.8 L, a blunt round tip: two near-
# equal tip corners), a raised midrib ridge in two points (a lit half and a shaded half), the edges cupped up a little,
# the tip curling down, one back point underneath (17 tris).
LEAF_OUT = ((0.20, 0.50), (0.58, 1.0), (0.90, 0.74))
PETAL_OUT = ((0.30, 0.70), (0.66, 1.0), (0.92, 0.66))
LEAF_W = 1.0
LEAF_CAMBER, LEAF_FOLD, LEAF_CURL, LEAF_THICK = 0.11, 0.05, 0.12, 0.07
LEAF_MOTTLE = dict(amp=0.04, scale=0.9, seed=38411)
LEAF_L = 0.70                # leaf length / rosette width
OUT_PITCH = (0.45, 0.70)     # outer tier rise (rad)
IN_PITCH = (0.80, 1.05)      # inner tier rise (rad)
CL_TINT = 0.04
FLOWER_TILT = 0.25           # how far each flower tips toward its face direction (rad, front petals down)
FLOWER_UP = 0.85             # a flower's centre sits at least this fraction of the leaves' height round it
CONTACT = 0.03               # every leaf / flower ends within this of the ground, a rock or another leaf (STAGES)
DROP_DEPTH = 0.40            # a leaf this far inside a rock is left out (less is pushed out to touch it)
CLUSTER_INFO = {}


def _leaf(a, base, L, key, yaw, pitch, width=LEAF_W, outline=LEAF_OUT, camber=LEAF_CAMBER, thick=LEAF_THICK,
          fold=LEAF_FOLD, curl=LEAF_CURL, roll=0.0):
    """One chunky leaf (a closed solid). base = the stem end; yaw about Z; pitch = its rise (rad)."""
    bm = a.bm
    W = width * L / 2
    rot = Matrix.Rotation(yaw, 3, "Z") @ Matrix.Rotation(-pitch, 3, "Y") @ Matrix.Rotation(roll, 3, "X")
    B = Vector(base)

    def put(x, y, z):
        t = x / L
        return bm.verts.new(B + rot @ Vector((x, y, z + fold * abs(y) - curl * L * t * t)))
    ring = [(0.0, 0.0)] + [(f * L, -h * W) for f, h in outline] + [(L, 0.0)] + \
        [(f * L, h * W) for f, h in reversed(outline)]
    o = [put(x, y, 0.0) for x, y in ring]
    r1 = put(0.30 * L, 0.0, camber * L)
    r2 = put(0.66 * L, 0.0, camber * L * 0.85)
    bk = put(0.48 * L, 0.0, -thick * L)
    xs = [x for x, _ in ring]
    own = [r1 if x < 0.48 * L else r2 for x in xs]
    n = len(o)
    faces = []
    for i in range(n):
        j = (i + 1) % n
        if own[i] is own[j]:
            faces.append(bm.faces.new((o[i], o[j], own[i])))
        else:
            faces.append(bm.faces.new((o[i], o[j], own[j])))
            faces.append(bm.faces.new((o[i], own[j], own[i])))
    faces += [bm.faces.new((bk, o[(i + 1) % n], o[i])) for i in range(n)]
    vs = o + [r1, r2, bk]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    a._finish(vs, key, tint=1.0)
    return vs


def _flower(a, loc, diam, seed, face=-math.pi / 2):
    """Five broad round-tipped white petals round a domed golden centre (diam across), tipped toward the azimuth
    `face`. Each petal's base sits inside the centre, so every petal touches it; the centre's foot sits on the leaves
    under loc. Returns verts."""
    rng = random.Random(seed)
    r = diam / 2
    L = r * 0.92
    y0 = rng.uniform(0, 2 * math.pi)
    out = []
    cr = r * 0.34
    for k in range(5):
        yaw = y0 + 2 * math.pi * k / 5
        d = Vector((math.cos(yaw), math.sin(yaw), 0.0))
        pitch = 0.10 - FLOWER_TILT * math.cos(yaw - face)
        b = Vector(loc) + d * (0.35 * cr) + Vector((0, 0, 0.02 * diam + 0.003 * k))
        out += _leaf(a, tuple(b), L, PETAL, yaw, pitch, width=0.66, outline=PETAL_OUT, camber=0.06, thick=0.07,
                     fold=0.08, curl=0.06)
    cvs = a.cyl(cr, cr * 0.62, cr * 0.95, sides=6, loc=(loc[0], loc[1], loc[2] - 0.15 * cr), mat=POLLEN, tint=1.0)
    caps = [f for f in _faces(cvs) if len(f.verts) > 4]
    if caps:
        bmesh.ops.triangulate(a.bm, faces=caps, quad_method="BEAUTY", ngon_method="BEAUTY")
    # the face tilt: the centre tips the same way as the petals (rotate about its foot)
    tilt_ax = Vector((math.cos(face + math.pi / 2), math.sin(face + math.pi / 2), 0.0))
    cv = [v for v in cvs if v.is_valid]
    piv = Vector(loc)
    m = Matrix.Translation(piv) @ Matrix.Rotation(FLOWER_TILT * 0.8, 4, tilt_ax) @ Matrix.Translation(-piv)
    bmesh.ops.transform(a.bm, matrix=m, verts=cv)
    return out + cv


class _Guard(m036._Guard):
    """m036's guard: a leaf more than `allow` inside a rock is pushed out along the surface normal (it then still
    touches the rock); more than DROP_DEPTH inside, it is left out."""


def _lift(vs, floor=0.004):
    z = min(v.co.z for v in vs)
    if z < floor:
        for v in vs:
            v.co.z += floor - z


def _kill(a, vs):
    bmesh.ops.delete(a.bm, geom=[v for v in vs if v.is_valid], context="VERTS")


def _leaf_key(t):
    """t: 0 the outer low leaves (leaf_deep at 40 %), 0.5 the middle, 1 the inner upright (young)."""
    if t <= 0.0:
        return K.mix_key(LEAF, LEAF_DEEP, 0.2)
    if t < 0.4:
        return K.mix_key(LEAF, LEAF_DEEP, 0.2)
    if t < 0.75:
        return LEAF
    if t < 1.0:
        return K.mix_key(LEAF, LEAF_YOUNG, 0.5)
    return LEAF_YOUNG


def _rosette(a, root, w, n, seed, young=0.0, guard=None, tint=1.0, pitch_bias=0.0, avoid=None, info=None):
    """A clover rosette rooted at root (x, y, z): n = (outer, inner) leaves. The outer leaves splay low (deeper green),
    the inner ones rise (lighter); every stem end is within 0.05 of the root, so the leaves cross at the hub and touch.
    avoid: (x, y) a direction the rosette leans against (a rock): leaves pointing into it rise more steeply.
    Returns (verts, top z)."""
    rng = random.Random(seed)
    c0 = Vector(root)
    L0 = LEAF_L * w
    allv, top = [], c0.z
    yaw = rng.uniform(0, 2 * math.pi)
    av = Vector((avoid[0] - c0.x, avoid[1] - c0.y, 0.0)).normalized() if avoid else None
    plan = []
    for tier, cnt in enumerate(n):
        for i in range(cnt):
            yaw += 2 * math.pi / cnt + rng.uniform(-0.25, 0.25) + (0.5 if i == 0 else 0.0)
            if tier == 0:
                plan.append((L0 * rng.uniform(0.92, 1.06), rng.uniform(*OUT_PITCH) + pitch_bias, 0.0, yaw, 0.045))
            else:
                plan.append((L0 * rng.uniform(0.80, 0.94), rng.uniform(*IN_PITCH) + pitch_bias, 1.0, yaw, 0.02))
    for L, pitch, t, yw, rr in plan:
        d = Vector((math.cos(yw), math.sin(yw), 0.0))
        if av is not None and d.dot(av) > 0.3:
            pitch = max(pitch, 1.05 + 0.25 * d.dot(av))
        base = c0 + d * rr * w + Vector((0, 0, 0.01))
        vs = _leaf(a, tuple(base), L, _leaf_key(min(1.0, t + young)), yw, min(pitch, 1.35),
                   roll=rng.uniform(-0.3, 0.3))
        if guard is not None:
            dep, _ = guard.depth(vs)
            if dep > DROP_DEPTH:
                _kill(a, vs)
                if info is not None:
                    info["dropped"] = info.get("dropped", 0) + 1
                continue
            guard.push(vs, 0.05)
        _lift(vs)
        _mottle(a, _faces(vs), LEAF_MOTTLE["amp"], LEAF_MOTTLE["scale"], LEAF_MOTTLE["seed"] + seed, tint=tint)
        top = max(top, max(v.co.z for v in vs))
        allv += vs
        if info is not None:
            info["leaves"] = info.get("leaves", 0) + 1
    return allv, top


def _seat_z(tree, xy, z_from=12.0, sink=0.03):
    if tree is None:
        return 0.0
    h = tree.ray_cast(Vector((xy[0], xy[1], z_from)), Vector((0, 0, -1)), 200)
    return max(0.0, h[0].z - sink) if h[0] is not None else 0.0


def _all_tree(a):
    a.bm.verts.ensure_lookup_table()
    a.bm.faces.ensure_lookup_table()
    return BVHTree.FromBMesh(a.bm)


# Clusters: name -> rosettes [(x, y, seat, w, (outer, inner), pitch bias)], flowers [(x, y, diameter)], young shift,
# lean point (a rock the cluster presses against, or None), seed. seat: "g" ground; ("r", z_from) set on a rock (ray
# down from z_from); "l" set on whatever is already built under it (leaves or rock): the stacked rosettes of a tall
# mound each rest on the leaves below (no hidden stems).
CLUSTERS = (
    ("K1", ((-2.25, 1.00, "g", 1.45, (5, 3), 0.0), (-0.95, 1.30, "g", 1.45, (5, 3), 0.0),
            (-1.70, 1.95, "g", 1.35, (4, 2), 0.05), (-1.80, 1.35, "l", 1.20, (3, 2), 0.0),
            (-1.20, 1.55, "l", 1.20, (3, 2), 0.0), (-1.55, 1.50, "l", 1.05, (2, 3), 0.0)),
     ((-0.95, 1.10, 1.0), (-1.50, 1.70, 0.8, 90.0)), 0.0, (-0.6, 3.0), 38401),
    ("K1b", ((0.10, 1.75, "g", 1.40, (6, 4), 0.10),), (), 0.45, (0.6, 3.2), 38402),
    ("K5", ((2.80, 2.75, "g", 1.45, (6, 4), 0.10),), ((2.82, 2.72, 0.45, 90.0),), 0.15, None, 38403),
    ("K2", ((1.40, -0.65, "g", 1.25, (6, 4), 0.10),), ((1.42, -0.62, 0.42),), 0.0, None, 38404),
    ("K3", ((0.85, -3.70, "g", 1.15, (6, 3), 0.10),), ((0.86, -3.68, 0.37),), 0.0, None, 38405),
    ("K4", ((4.40, -2.30, "g", 1.40, (7, 4), 0.10),), ((4.45, -2.33, 0.60),), 0.0, None, 38406),
    ("L1", ((-4.70, -0.40, "g", 1.40, (5, 3), 0.15), (-4.65, -0.30, "l", 1.10, (4, 3), 0.10)), (), 0.10,
     (-3.8, -0.4), 38407),
    ("L2", ((-4.40, -1.80, "g", 1.30, (6, 4), 0.05), (-3.95, -2.40, "g", 1.15, (5, 3), 0.05)), (), 0.0,
     (-3.6, -1.7), 38408),
)


def _cluster(a, name, rosettes, flowers, young, lean, seed, guard, rock_tree, face=None):
    info = {"leaves": 0, "dropped": 0, "flowers": 0}
    rng = random.Random(seed)
    tint = 1.0 + rng.uniform(-CL_TINT, CL_TINT)
    allv = []
    for i, (x, y, seat, w, n, pb) in enumerate(rosettes):
        if seat == "g":
            z = 0.0
        elif seat == "l":
            # the highest leaf (or rock) surface over a small disk round the root: the rosette's hub rests on it
            t = _all_tree(a)
            z = max(_seat_z(t, (x + 0.12 * w * math.cos(k * 1.0472) * (k > 0), y + 0.12 * w * math.sin(k * 1.0472) *
                                (k > 0)), sink=0.05) for k in range(7))
        else:
            z = _seat_z(rock_tree, (x, y), z_from=seat[1], sink=0.05)
        vs, _ = _rosette(a, (x, y, z), w, n, seed + 13 * i, young=young, guard=guard, tint=tint, pitch_bias=pb,
                         avoid=lean, info=info)
        allv += vs
    for k, (x, y, d, *fz) in enumerate(flowers):
        tree = BVHTree.FromPolygons([v.co for v in allv], [[allv.index(v) for v in f.verts]
                                                           for f in _faces(allv)]) if allv else None
        z = _seat_z(tree, (x, y), sink=0.02)
        if z <= 0.0:
            z = _seat_z(_all_tree(a), (x, y), sink=0.02)
        # on top of the cluster, among the inner leaves: at least FLOWER_UP of the leaves' height round it
        near = [v.co.z for v in allv if v.is_valid and (v.co.xy - Vector((x, y))).length < 0.45 * d + 0.15]
        if near:
            z = max(z, FLOWER_UP * max(near))
        fa = face if face is not None else math.radians(fz[0] if fz else -90.0)
        fv = _flower(a, (x, y, z), d, seed + 7 + k, face=fa)
        _lift(fv)
        allv += fv
        info["flowers"] += 1
    xs, ys, zs = ([v.co[i] for v in allv if v.is_valid] for i in range(3))
    if xs:
        info.update(size=[round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2)], top=round(max(zs), 2))
    CLUSTER_INFO[name] = info
    return [v for v in allv if v.is_valid]


def dressing(a, rock_tree, clusters=CLUSTERS):
    CLUSTER_INFO.clear()
    guard = _Guard(rock_tree)
    for name, ros, fl, young, lean, seed in clusters:
        _cluster(a, name, ros, fl, young, lean, seed, guard, rock_tree)
    return guard.moved


# ---- settle: no floating dressing (STAGES) ------------------------------------------------------------------------------
def _shell_groups(bm):
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    bm.faces.index_update()
    ids, n = M._shell_ids(bm)
    fs = {}
    for f in bm.faces:
        fs.setdefault(ids[f.index], []).append(f)
    return ids, n, fs


def contacts(bm, base, tol=CONTACT):
    """Contact graph of a bmesh's shells. base: the shell ids that count as support (rocks, pads). Returns (n, zmin,
    gap to the nearest other shell or the ground per shell, the set of shells chained to the ground or a support at
    tol, shell -> faces)."""
    ids, n, fs = _shell_groups(bm)
    tree = BVHTree.FromBMesh(bm)
    fsh = [ids[f.index] for f in bm.faces]
    vsh = {}
    for f in bm.faces:
        for v in f.verts:
            vsh[v.index] = fsh[f.index]
    zmin = [1e9] * n
    for v in bm.verts:
        s = vsh.get(v.index)
        if s is not None:
            zmin[s] = min(zmin[s], v.co.z)
    near = {}
    for i, j in tree.overlap(tree):
        a_, b_ = fsh[i], fsh[j]
        if a_ != b_:
            near[(min(a_, b_), max(a_, b_))] = 0.0
    for v in bm.verts:
        s = vsh.get(v.index)
        if s is None:
            continue
        for loc, _, fi, d in tree.find_nearest_range(v.co, tol * 3):
            t = fsh[fi]
            if t != s:
                k = (min(s, t), max(s, t))
                near[k] = min(near.get(k, 1e9), d)
    gap = [max(0.0, z) for z in zmin]
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    adj = {k: set() for k in range(n)}
    for (a_, b_), d in near.items():
        if d <= tol:
            adj[a_].add(b_)
            adj[b_].add(a_)
    seen = {k for k in range(n) if zmin[k] <= tol} | set(base)
    stack = list(seen)
    while stack:
        k = stack.pop()
        for m_ in adj[k]:
            if m_ not in seen:
                seen.add(m_)
                stack.append(m_)
    return n, zmin, gap, seen, fs, adj


def settle(a, support_parts, rounds=4):
    """Drop every group of dressing shells that is not chained to the ground or a rock at CONTACT: the group (a leaf,
    or a whole flower) moves straight down until its lowest-clearance vertex is 0.01 above whatever is under it.
    support_parts: the K.tag_part names of the rocks and pads. Returns the number of groups moved per round."""
    bm = a.bm
    lay = bm.faces.layers.int.get("kit_part")
    pid = {v for k, v in a.__dict__.get("_parts", {}).items() if k in support_parts}
    moved = []
    for _ in range(rounds):
        ids, n, fs = _shell_groups(bm)
        base = {ids[f.index] for f in bm.faces if lay is not None and f[lay] in pid}
        n, zmin, gap, seen, fs, adj = contacts(bm, base)
        loose = [k for k in range(n) if k not in seen]
        if not loose:
            moved.append(0)
            break
        # groups of loose shells connected to each other (a flower: petals + centre)
        grp, gid = [], {}
        for k in loose:
            if k in gid:
                continue
            g, st = [], [k]
            gid[k] = len(grp)
            while st:
                x = st.pop()
                g.append(x)
                for y in adj[x]:
                    if y not in seen and y not in gid:
                        gid[y] = len(grp)
                        st.append(y)
            grp.append(g)
        cnt = 0
        for g in grp:
            gs = set(g)
            others = [f for f in bm.faces if ids[f.index] not in gs]
            ov = list({v for f in others for v in f.verts})
            vi = {v: i for i, v in enumerate(ov)}
            t = BVHTree.FromPolygons([v.co for v in ov], [[vi[v] for v in f.verts] for f in others])
            gv = list({v for k in g for f in fs[k] for v in f.verts})
            best = min(v.co.z for v in gv)              # the ground
            for v in gv:
                h = t.ray_cast(v.co + Vector((0, 0, 1e-4)), Vector((0, 0, -1)), 50)
                if h[0] is not None:
                    best = min(best, v.co.z - h[0].z)
            if best > 0.01:
                for v in gv:
                    v.co.z -= best - 0.01
                cnt += 1
        moved.append(cnt)
        if not cnt:
            break
    return moved


def contact_report(o, support=("rock", "moss"), tol=CONTACT):
    """Floating dressing on a built object: shells whose nearest other shell (or the ground) is farther than tol, the
    worst such gap, and the shells with no chain of contact to the ground or a rock / pad at tol and at 0.05."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    keys = [m.get("flintkit_key", m.name) if m else "" for m in o.data.materials]
    ids, n, fs = _shell_groups(bm)
    kind = {k: _kind({keys[f.material_index] for f in fs[k]}) for k in range(n)}
    base = {k for k in range(n) if kind[k] in support}
    n, zmin, gap, seen, _, adj = contacts(bm, base, tol)
    floating = [k for k in range(n) if gap[k] > tol and k not in base]
    _, _, _, seen5, _, _ = contacts(bm, base, 0.05)
    bm.free()
    kinds = {}
    for k in range(n):
        kinds[kind[k]] = kinds.get(kind[k], 0) + 1
    return {"shells": n, "kinds": kinds, "floating": len(floating),
            "floating_kinds": sorted({kind[k] for k in floating}),
            "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
            "max_gap_dressing": round(max([gap[k] for k in range(n) if k not in base], default=0.0), 3),
            "unchained": n - len(seen), "unchained_005": n - len(seen5)}


def _kind(ks):
    if any(x.startswith("m038_rock") for x in ks):
        return "rock"
    if any(x.startswith("m038_moss") for x in ks):
        return "moss"
    if all(x.startswith("m038_leaf") for x in ks):
        return "leaf"
    if ks == {PETAL}:
        return "petal"
    if ks == {POLLEN}:
        return "pollen"
    return "other"


def shells_report(o):
    """m036.shells_report with this model's kinds."""
    out = m036.shells_report(o)
    keys = [m.get("flintkit_key", m.name) if m else "" for m in o.data.materials]
    bm = bmesh.new()
    bm.from_mesh(o.data)
    ids, n, fs = _shell_groups(bm)
    for k in range(n):
        out[k]["kind"] = _kind({keys[f.material_index] for f in fs[k]})
    bm.free()
    return out


# ---- parts ---------------------------------------------------------------------------------------------------------------
def _new_parts(a):
    a.bm.faces.layers.int.new("kit_part")


PART_CL = {
    # A's foot clumps (parts row: left 8-10 leaves, right 4-6, no flower)
    "A": (("Af1", ((-1.45, -0.35, "g", 1.15, (6, 3), 0.2),), (), 0.35, (0.0, 0.0), 38431),
          ("Af2", ((1.45, -0.20, "g", 0.90, (3, 2), 0.2),), (), 0.35, (0.0, 0.0), 38432)),
    # C: a 6-leaf clump on the back edge (on the slab top), a cluster at the left foot
    "C": (("Cb", ((0.40, 1.55, ("r", 6.0), 1.0, (4, 2), 0.0),), (), 0.25, None, 38433),
          ("Cl", ((-3.15, -0.30, "g", 1.25, (5, 3), 0.2),), (), 0.10, (-2.0, -0.3), 38434)),
}


def tall_rock_part(a):
    ROCK_INFO.clear()
    _new_parts(a)
    K.tag_part(a, _rock(a, "A", (0.0, 0.0)), "A")
    tree = K.bvh_of(K.part(a, "A"))
    for name, ros, fl, young, lean, seed in PART_CL["A"]:
        _cluster(a, name, ros, fl, young, lean, seed, _Guard(tree), tree)
    PART_LOG[A_P] = {"settle": settle(a, ("A",))}


def medium_rock_part(a):
    ROCK_INFO.clear()
    PAD_INFO.clear()
    _new_parts(a)
    K.tag_part(a, _rock(a, "B", (0.0, 0.0)), "B")
    K.tag_part(a, _pad(a, "MB", K.part(a, "B"), (0.0, 0.0)), "MB")


def flat_slab_part(a):
    ROCK_INFO.clear()
    PAD_INFO.clear()
    _new_parts(a)
    K.tag_part(a, _slab(a, (0.0, 0.0), 0.0), "C")
    K.tag_part(a, _pad(a, "MC", K.part(a, "C"), (0.0, 0.0), rock_yaw=0.0), "MC")
    tree = K.bvh_of(K.part(a, "C"))
    for name, ros, fl, young, lean, seed in PART_CL["C"]:
        _cluster(a, name, ros, fl, young, lean, seed, _Guard(tree), tree)
    PART_LOG[C_P] = {"settle": settle(a, ("C", "MC"))}


def wedge_rock_part(a):
    ROCK_INFO.clear()
    _rock(a, "D", (0.0, 0.0))


def round_rock_part(a):
    ROCK_INFO.clear()
    _rock(a, "E", (0.0, 0.0))


def flower_clump_part(a):
    _new_parts(a)
    _cluster(a, "part_clump", ((0.0, 0.0, "g", 1.05, (4, 3), 0.15),), ((0.02, 0.02, 0.45),), 0.0, None, 38441,
             None, None, face=-math.pi / 2)
    PART_LOG[FC_P] = {"settle": settle(a, ())}


PART_LOG = {}


# ---- hero ----------------------------------------------------------------------------------------------------------------
LAYOUT = {}


def hero(a):
    ROCK_INFO.clear()
    PAD_INFO.clear()
    _new_parts(a)
    K.tag_part(a, _slab(a), "C")
    for name in ("A", "B", "D", "E"):
        K.tag_part(a, _rock(a, name), name)
    K.tag_part(a, _pad(a, "MB", K.part(a, "B"), ROCKS["B"][1]), "MB")
    K.tag_part(a, _pad(a, "MC", K.part(a, "C"), SLAB["centre"], rock_yaw=SLAB["yaw"]), "MC")
    rocks = {k: K.part(a, k) for k in ("A", "B", "C", "D", "E")}
    LAYOUT["gaps"] = _gaps(rocks)
    support = [v for k in ("A", "B", "C", "D", "E", "MB", "MC") for v in K.part(a, k)]
    tree = K.bvh_of(support)
    LAYOUT["guard_moves"] = dressing(a, tree)
    LAYOUT["settle"] = settle(a, ("A", "B", "C", "D", "E", "MB", "MC"))


def _gaps(rocks):
    """Clearance between each pair of rocks: the smallest vertex-to-surface distance either way (negative: one has a
    vertex inside the other, by the hull-plane depth)."""
    hulls = {k: m036._planes([v.co.copy() for v in vs if v.is_valid]) for k, vs in rocks.items()}
    trees = {k: K.bvh_of(vs) for k, vs in rocks.items()}
    out = {}
    names = list(hulls)
    for i, a_ in enumerate(names):
        for b_ in names[i + 1:]:
            pen = m036._pen(hulls[a_], hulls[b_])
            if pen > 1e-4:
                out[f"{a_}{b_}"] = round(-pen, 2)
                continue
            d = min(min(trees[b_].find_nearest(v.co)[3] for v in rocks[a_] if v.is_valid),
                    min(trees[a_].find_nearest(v.co)[3] for v in rocks[b_] if v.is_valid))
            out[f"{a_}{b_}"] = round(d, 2)
    return out


NOTES = {
    HERO: "Stone scatter (pebble scatter): five separate warm grey-pink faceted rocks in a loose ring - a big low flat "
          "slab with a lime moss pad, a tall blunt rock, a medium boxy rock with a star moss pad, a wedge rock and a "
          "small pebble - with round-leaf clover clusters and six white five-petal flowers at their feet; every rock, "
          "pad, leaf, petal and flower centre its own closed shell. Ground detail. No VFX",
    A_P: "Tall Rock: tall blunt faceted warm grey-pink rock (flat base) with two leaf clumps at its foot",
    B_P: "Medium Rock: chunky faceted warm grey-pink block with a broad top and a star-shaped lime moss pad",
    C_P: "Flat Slab: low faceted warm grey-pink slab of uniform thickness (flat underside) with a lime moss pad on "
         "its back-left corner, a leaf clump on its back edge and a cluster at its left foot",
    D_P: "Wedge Rock: chunky faceted warm grey-pink wedge with a tilted top; flat bottom",
    E_P: "Round Rock: small squat faceted warm grey-pink pebble; flat bottom",
    FC_P: "Flower Clump (reusable): round-leaf clover cluster with one white five-petal flower",
}
COLLISION = {HERO: "none", A_P: "hull", B_P: "hull", C_P: "hull", D_P: "hull", E_P: "none", FC_P: "none"}


# ---- make / finish (no unions: closed shells) ----------------------------------------------------------------------------
def _recentre(o):
    bc = m012._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


def _make(name, fn, role, budget):
    t0 = time.time()
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget,
             collision=COLLISION[name], tint_var=0.0)
    o[OFF] = list(M._build_offset(fn))
    o.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    lg = {"split": m036._tri_all(o)}
    if o.data.has_custom_normals:
        with M._override(o):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
    lg["forced"] = m012._force_slivers(o, lim=POLISH_LIM) if m012._thin(o, POLISH_LIM)["under"] else 0
    _recentre(o)
    for p in o.data.polygons:
        p.use_smooth = False
    M.smart_uv(o, **UV)
    lg["uv_cut"] = m012._uv_unfold(o)
    lg["bowties"] = M.fix_bowties(o)
    K.drop_unused_slots(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


# ---- render measurement (the study's masks, spec "Pixel boxes and masks") ---------------------------------------------
def classify(px, sheet=True):
    """px: (h, w, 3) sRGB 0-1. Returns (class map: 1 rock, 2 green, 3 flower; ground-shadow mask). The study's cls():
    R hue <= 48 or >= 190, sat .04-.42, v .22-.985; G hue 48-150, sat >= .28, v >= .15; F white (sat < .10, v >= .96)
    or gold (hue 25-48, sat >= .55, v >= .7); B (sheet only) sat < .06, v .55-.955."""
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    mx, mn = px.max(-1), px.min(-1)
    v = mx
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    d = mx - mn
    hue = np.zeros_like(mx)
    m = d > 1e-6
    rr = m & (mx == r)
    gg = m & (mx == g) & ~rr
    bb = m & ~rr & ~gg
    hue[rr] = (60 * ((g - b)[rr] / d[rr])) % 360
    hue[gg] = 60 * ((b - r)[gg] / d[gg]) + 120
    hue[bb] = 60 * ((r - g)[bb] / d[bb]) + 240
    G = (hue >= 48) & (hue <= 150) & (s >= 0.28) & (v >= 0.15)
    F = ((s < 0.10) & (v >= 0.96)) | ((hue >= 25) & (hue < 48) & (s >= 0.55) & (v >= 0.7))
    B = (s < 0.06) & (v >= 0.55) & (v <= 0.955) if sheet else np.zeros(mx.shape, bool)
    R = ((hue <= 48) | (hue >= 190)) & (s >= 0.04) & (s <= 0.42) & (v >= 0.22) & (v <= 0.985) & ~G & ~F & ~B
    out = np.zeros(mx.shape, np.int8)
    out[R] = 1
    out[G & ~F] = 2
    out[F] = 3
    return out, B


def measure(path, box=None, bg_tol=0.05):
    """Silhouette bbox, W:H, shares (rock / green / flower; on the sheet the ground shadow is excluded), 21-column top
    profile and the class medians of a render (or a box of the sheet) whose background is the corner colour."""
    kit = K.NS["KIT"]
    px = np.clip(kit["load_px"](path)[::-1, :, :3], 0, 1)
    sheet = box is not None
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1]
    bg = np.median(np.concatenate([px[:4, :4].reshape(-1, 3), px[:4, -4:].reshape(-1, 3)]), axis=0)
    sil = np.abs(px - bg).max(-1) > bg_tol
    cls, B = classify(px, sheet)
    sil &= ~B
    ys, xs = np.nonzero(sil)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    H, W = y1 - y0 + 1, x1 - x0 + 1
    c = cls * sil
    rock, green, flower = int((c == 1).sum()), int((c == 2).sum()), int((c == 3).sum())
    tot = max(1, rock + green + flower)
    prof = []
    for f in np.linspace(0, 1, 21):
        col = int(round(x0 + f * (W - 1)))
        on = np.nonzero(sil[:, col])[0]
        prof.append(round(float((y1 - on.min()) / (H - 1)), 2) if len(on) else 0.0)
    rgb = px * 255

    def med(mask):
        sel = rgb[mask]
        return "#" + "".join(f"{int(x):02X}" for x in np.median(sel, axis=0)) if len(sel) else None
    return {"wh": round(W / H, 3), "rock": round(rock / tot, 3), "green": round(green / tot, 3),
            "flower": round(flower / tot, 3), "profile": prof, "rock_med": med(c == 1), "green_med": med(c == 2),
            "flower_med": med(c == 3)}


SHEET_CELLS = {"f34_sheet": (14, 160, 518, 452), "r34_sheet": (521, 162, 1009, 452),
               "front_sheet": (14, 485, 270, 664), "side_sheet": (272, 485, 510, 664),
               "rear_sheet": (513, 485, 760, 664), "top_sheet": (763, 476, 1009, 664)}
PART_TARGETS = {"parts_row": {"rock_med": "#C9AC9C"}, "part_flowerclump": {"green_med": "#9ABB03"},
                "part_tallrock": {"rock_med": "#C3A493"}, "part_flatslab": {"rock_med": "#D6B9AC"},
                "part_wedgerock": {"rock_med": "#C7AA9D"}, "part_roundrock": {"rock_med": "#B9A196"},
                "part_mediumrock": {"green_med": "#B0C306"}}


def compare(names=None):
    """Our *_sheet renders against the sheet's cells: shares, W:H, mean / max top-profile difference, medians."""
    out = {}
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    for k, box in SHEET_CELLS.items():
        if names and k not in names:
            continue
        try:
            s = measure(M.ref(NUM), box)
            r = measure(f"{d}/{k}.png")
        except Exception as e:      # a render not made yet
            out[k] = str(e)
            continue
        pd = [abs(x - y) for x, y in zip(s["profile"], r["profile"])]
        out[k] = {"sheet": {x: s[x] for x in ("wh", "rock", "green", "flower", "rock_med", "green_med")},
                  "ours": {x: r[x] for x in ("wh", "rock", "green", "flower", "rock_med", "green_med")},
                  "profile_mean": round(sum(pd) / len(pd), 3), "profile_max": round(max(pd), 2),
                  "profile_ours": r["profile"], "profile_sheet": s["profile"]}
    for k, tgt in PART_TARGETS.items():
        if names and k not in names:
            continue
        try:
            r = measure(f"{d}/{k}.png")
        except Exception as e:
            out[k] = str(e)
            continue
        out[k] = {"ours": {x: r[x] for x in ("rock", "green", "flower", "rock_med", "green_med", "flower_med")},
                  "target": tgt}
    return out


# ---- build -------------------------------------------------------------------------------------------------------------
PARTS = ((A_P, tall_rock_part), (B_P, medium_rock_part), (C_P, flat_slab_part), (D_P, wedge_rock_part),
         (E_P, round_rock_part), (FC_P, flower_clump_part))
TARGET_SIZE = ((11.1, 0.5), (8.9, 0.6), (3.0, 0.2))
ROCK_SIZE_TOL = 0.15


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m038_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib",
                                                                                 "StoneScatter"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build(render=True, parts=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    LAYOUT.clear()
    PART_LOG.clear()
    objs, log = {}, {}
    part_rocks = {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn, "part", 1000)
            if ROCK_INFO:
                part_rocks[name] = {k: dict(v) for k, v in ROCK_INFO.items()}
        log["part_settle"] = dict(PART_LOG)
    h, log["hero"] = _make(HERO, hero, "hero", 4000)
    log["layout"] = {k: v for k, v in LAYOUT.items()}
    log["pads"] = {k: dict(v) for k, v in PAD_INFO.items()}
    log["clusters"] = {k: dict(v) for k, v in CLUSTER_INFO.items()}
    rocks = {k: dict(v) for k, v in ROCK_INFO.items()}
    _cleanup_tmp()
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    _spec()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    audits = [M.audit(o) for o in order]
    thin = {o.name: m012._thin(o, POLISH_LIM) for o in order}
    shells = {o.name: shells_report(o) for o in order}
    contact = {o.name: contact_report(o) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = 4000 if o is h else 1000
        if au["tris"] > lim:
            problems.append(f"{o.name}: {au['tris']} tris over {lim}")
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "wire_edges", "loose_verts",
                  "zero_area_faces", "ngons"):
            if au[k]:
                problems.append(f"{o.name}: {k} {au[k]}")
        if au["normals"] != "outward":
            problems.append(f"{o.name}: normals {au['normals']}")
        if thin[o.name]["under"]:
            problems.append(f"{o.name}: {thin[o.name]['under']} faces with a corner under {POLISH_LIM} deg")
        for i, s in enumerate(shells[o.name]):
            for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "self_hits", "inverted"):
                if s[k]:
                    problems.append(f"{o.name} shell {i} ({s['kind']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['kind']}): not closed outward (volume {s['volume']})")
        cr = contact[o.name]
        if cr["floating"] or cr["unchained"]:
            problems.append(f"{o.name}: {cr['floating']} floating shells, {cr['unchained']} unchained "
                            f"(worst gap {cr['worst_gap']})")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    for k, info in rocks.items():
        want = ROCKS[k][2] if k in ROCKS else (SLAB["L"], SLAB["D"], SLAB["T"])
        if k != "C" and any(abs(g - w) > ROCK_SIZE_TOL for g, w in zip(info["size"], want)):
            problems.append(f"rock {k}: size {info['size']} against {list(want)}")
    for pair, g in LAYOUT.get("gaps", {}).items():
        if g < 0.0:
            problems.append(f"rocks {pair} overlap by {-g}")
    for key, (hexcol, _, _) in PALETTE.items():
        if key in ROCK_KEYS and not warm_ok(hexcol):
            problems.append(f"{key} {hexcol} fails the warm-stone guard")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 8: none)")
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95",
                                                                    "texels_per_stud_1024")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    kinds = {}
    for s in shells[HERO]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts", "transforms_applied", "custom_normals")}
                     for au in audits],
           "shells": kinds, "contact": contact, "thin": thin, "log": log, "problems": problems, "uv": uv,
           "rocks": rocks, "part_rocks": part_rocks,
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order)
        out["compare"] = compare()
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders -----------------------------------------------------------------------------------------------------------
# decision 5: the f34, front and top cells are one aligned front-facing composition: f34_sheet (0, 32), front_sheet
# (0, 28), top_sheet (0, 72); side (90, 8), rear (180, 12) and r34 (150, 25) are compact re-compositions, judged loosely.
# Floor hidden and a 3x lens on *_sheet shots (m033._long_lens).
SHEET_VIEWS = {"f34_sheet": (0, 32), "front_sheet": (0, 28), "top_sheet": (0, 72), "side_sheet": (90, 8),
               "rear_sheet": (180, 12), "r34_sheet": (150, 25)}
PARTS_SHOT = (0, 27)


def _copy(tag, src, m, coll):
    c = bpy.data.objects.new(f"{PFX}{tag}", src.data)
    coll.objects.link(c)
    c.matrix_world = m
    return c


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded View: A high in the middle, B high at the right, C low at
    the left, D and E low at the right, five loose flower clumps between them."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    o0 = Matrix.Translation((objs[0].location.x + 60, objs[0].location.y, 0))
    shown = [_copy("expl_A", by[A_P], o0 @ Matrix.Translation((-1.0, 2.5, 2.6)), coll),
             _copy("expl_B", by[B_P], o0 @ Matrix.Translation((3.6, 2.0, 2.8)), coll),
             _copy("expl_C", by[C_P], o0 @ Matrix.Translation((-4.2, -1.0, 0.6)), coll),
             _copy("expl_D", by[D_P], o0 @ Matrix.Translation((4.6, -0.8, 0.9)), coll),
             _copy("expl_E", by[E_P], o0 @ Matrix.Translation((5.2, -3.6, 0.0)) @ Matrix.Diagonal((2.2, 2.2, 2.2, 1)),
                   coll)]
    for i, (x, y, z) in enumerate(((1.0, -0.4, 1.8), (1.4, -2.6, 0.6), (0.8, -4.6, 0.0), (2.0, 1.0, 2.3),
                                   (1.8, 3.4, 3.4))):
        shown.append(_copy(f"expl_cl{i}", by[FC_P], o0 @ Matrix.Translation((x, y, z)) @ Matrix.Rotation(i * 1.3, 4, "Z"),
                           coll))
    bpy.context.view_layer.update()
    return shown


def _parts_row(objs):
    """The five rock parts in a row, left to right A, B, C, D, E at one scale (the sheet's Parts Breakdown)."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    x = objs[0].location.x + 120
    shown = []
    for n_ in (A_P, B_P, C_P, D_P, E_P):
        o = by[n_]
        w = o.dimensions.x
        shown.append(_copy("row_" + n_[12:], o, Matrix.Translation((x + w / 2, objs[0].location.y, 0)), coll))
        x += w + 1.6
    bpy.context.view_layer.update()
    return shown


def _scale_marker(h):
    """A 5.5-stud character stand-in (a plain column) beside the hero, for the scale shot."""
    a = K.fk().Asset(PFX + "char", "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=ROCK_DEEP, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=ROCK_DEEP, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=ROCK_DEEP, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    c.location = h.location + Vector((h.dimensions.x / 2 + 1.5, -2.0, 0))
    bpy.context.view_layer.update()
    return c


def render_views(objs, close=True):
    h = objs[0]
    by = {o.name: o for o in objs}
    shown = _exploded(objs) if FC_P in by else []
    row = _parts_row(objs) if E_P in by else []
    marker = _scale_marker(h)
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        for o in objs[1:]:
            extra["part_" + o.name.replace("StoneScatter", "").lower()] = ([o], *PARTS_SHOT)
        if row:
            extra["parts_row"] = (row, *PARTS_SHOT)
        if C_P in by:
            extra["slab_under"] = ([by[C_P]], 20, -35)
            extra["slab_cu"] = ([by[C_P]], 70, 6)          # Slab Thickness: the FlatSlab part's right end, low
        if A_P in by:
            extra["part_tallrock_side"] = ([by[A_P]], 90, 27)
        if shown:
            extra["exploded"] = (shown, -10, 22)
        extra["scale"] = ([h, marker], -20, 8)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = m033._long_lens(kit)
        try:
            sheet = M.views(NUM, [h], extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet}
        if close:
            d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
            off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
            # Rock / Plant Junction: K1 between C's back edge and A's left foot, from above C's top
            out["junc_cu"] = m033.render_close([h], f"{d}/junc_cu.png", -15, 28, off @ Vector((-1.2, 1.6, 1.3)), 1.5)
        return out
    finally:
        for o in shown + row + [marker]:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if o is marker and me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def preview(names=("f34_sheet", "front_sheet", "top_sheet"), vfx=False, extra=None, views=None, cell=(480, 400)):
    """Just the sheet comparison shots of the hero (fast tuning loop), then compare(). views overrides cameras."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    cams = dict(SHEET_VIEWS)
    cams.update(views or {})
    ex = {k: ([h], *cams[k]) for k in names}
    ex.update(extra or {})
    try:
        M.views(NUM, [h], names=(), extra=ex, vfx=vfx, cell=cell)
    finally:
        kit["render_group"] = orig
    return compare([n for n in names if n in SHEET_CELLS])


def hero_only():
    """Rebuild just the hero (tuning loop)."""
    M.coll(NUM, TITLE)
    palette()
    LAYOUT.clear()
    h, lg = _make(HERO, hero, "hero", 4000)
    _cleanup_tmp()
    _spec()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, _ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals")}, "log": lg, "layout": dict(LAYOUT),
            "thin": m012._thin(h, POLISH_LIM), "contact": contact_report(h),
            "rocks": {k: dict(v) for k, v in ROCK_INFO.items()}, "pads": {k: dict(v) for k, v in PAD_INFO.items()},
            "clusters": {k: dict(v) for k, v in CLUSTER_INFO.items()}}
