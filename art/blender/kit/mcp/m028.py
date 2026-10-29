"""028 Frost Shrub (references/028.png): a small bare sapling on a snowy rock ring. A thick warm-brown 8-sided trunk
column rises out of a lumpy snow mound, splits low into a left branch (two stubs) and a short right limb, and forks
higher into a tall up-left limb with a flat cut top, a right branch rising to a flat cut end and a short centre limb
behind; three big dark-blue faceted hexagonal leaf shards (up-left, left, right), two pale faceted ice gems in the
crown (one on the right branch, one behind the up-left leaf), four mid-blue ice gems half-buried in the snow, and a
ring of eleven chunky warm and grey-brown rocks open at the front.

    import importlib, kit_models, m028; importlib.reload(kit_models); importlib.reload(m028); m028.build()

Parts as on the sheet's exploded view, each built by its own function (front -Y, +X right, ground z = 0, studs):
- FrostBushStem: the forked stem (trunk + five limbs + three stubs, flat 8-sided cut ends), floor-cut at the foot.
- FrostBushLeaf: one 6-sided hexagonal shard (the up-left leaf's size), 60 tris.
- FrostBushIceNodule: one faceted ice gem (the right nodule's size), a dissolved convex hull of staggered rings.
- FrostBushBase: the rock ring, the snow mound and the four base nodules, one shell with a flat underside.
The hero (FrostBushNode) uses the same builders, united one shell at a time (guarded exact booleans) and floor-cut.
M028_spec.md holds the study, the decisions and each stage's record.

Colour (stage 4) is painted by position fields inside the builders, before the union (the union keeps each face's key
and Tint): leaves deep base -> key -> light tip along each leaf's axis, nodules deep bottom -> ice -> pale crown along
theirs, snow bluer near the rocks / nodules / trunk, wood darker at the crotches and the snow collar with broad
patches, rocks warm or cool per rock with darker feet. Never by facing.
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise

import kit_mcp as K
import kit_models as M
import m004
import m011
import m012

NUM, TITLE, SHEET = 28, "Frost Shrub", "M028"

LEAF, LEAF_DEEP, LEAF_LIGHT = "m028_leaf", "m028_leaf_deep", "m028_leaf_light"
ICE, ICE_PALE, ICE_DEEP = "m028_ice", "m028_ice_pale", "m028_ice_deep"
SNOW, SNOW_BLUE = "m028_snow", "m028_snow_blue"
WOOD, WOOD_DARK, WOOD_CUT = "m028_wood", "m028_wood_dark", "m028_wood_cut"
ROCK, ROCK_COOL, ROCK_DARK = "m028_rock", "m028_rock_cool", "m028_rock_dark"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# ---- palette (stage 4) -------------------------------------------------------------------------------------------------
# (hex, roughness, low_spec). Pass 1: K.calibrate on the dome against the spec 5.4 targets (TARGETS) gave leaf #3A63A4,
# deep #284B84, light #436DAB, ice #87A8F5, pale #A7BCF9, ice deep #688CC6, snow #A7B8D5, snow blue #96A9C8, wood #6C5142,
# wood dark #4C392C, cut #8B694E, rock #685347, cool #5E5351, rock dark #534542 (the dome's ice and snow clipped at B 255,
# so their hues drifted purple). Pass 2: each family corrected in linear light by the sheet / ours ratio of the
# front_sheet (and rear_sheet; front 2 : rear 1) medians with the study's masks: leaves x(1.09, 1.24, 1.26), wood
# x(1.08, 1.14, 1.17), rocks x(1.29, 1.19, 1.26), snow x(1.02, 0.995, 0.92), canopy ice x(1.27, 1.45, 1.11), the deep
# ice (base nodule FL against the sheet's #7DA2E1) x(1.32, 1.24, 1.12). Pass 3: the snow's shaded lumps read grey: the snow
# blue key x(1.08, 1.10, 1.14) (bluer, not greyer); the snow key stays (x1.07-1.15 clipped the lit lumps to #D7EBFF-
# #DCF0FF against the sheet's #D1E0F4).
PALETTE = {
    LEAF: ("#3D6DB6", 0.55, False),
    LEAF_DEEP: ("#2A5393", 0.55, False),
    LEAF_LIGHT: ("#4678BE", 0.55, False),
    ICE: ("#9DCDFF", 0.3, False),
    ICE_PALE: ("#BADEFF", 0.3, False),
    ICE_DEEP: ("#769AD0", 0.3, False),
    SNOW: ("#A9B8CD", 0.85, False),
    SNOW_BLUE: ("#99ADC9", 0.85, False),
    WOOD: ("#705647", 0.9, False),
    WOOD_DARK: ("#4F3D30", 0.9, False),
    WOOD_CUT: ("#906F54", 0.85, False),
    # verifier round 1 minor 1: the cool key was mauve (hue 356) and the warm one too red (18 against 23.6), so the
    # sheet's warm / grey-brown two-tone read as one pinkish brown; both moved to the sheet's hues
    ROCK: ("#78594A", 0.92, False),
    ROCK_COOL: ("#6B5953", 0.92, False),
    ROCK_DARK: ("#5E4B4A", 0.95, False),
}
# calibration targets: the sheet's rendered medians of unshadowed regions (M028_spec.md 5.4). key -> (sRGB, kind)
TARGETS = {LEAF: ((0x48, 0x77, 0xC0), "vivid"), LEAF_DEEP: ((0x35, 0x5A, 0x99), "vivid"),
           LEAF_LIGHT: ((0x53, 0x83, 0xC8), "vivid"),
           ICE: ((0xA8, 0xCD, 0xFA), "all"), ICE_PALE: ((0xCF, 0xE5, 0xFD), "all"),
           ICE_DEEP: ((0x7E, 0xA6, 0xE6), "all"),
           SNOW: ((0xD3, 0xE2, 0xF6), "all"), SNOW_BLUE: ((0xBC, 0xCF, 0xEB), "all"),
           WOOD: ((0x87, 0x60, 0x4A), "brown"), WOOD_DARK: ((0x5E, 0x44, 0x33), "brown"),
           WOOD_CUT: ((0xB0, 0x7E, 0x58), "brown"),
           ROCK: ((0x82, 0x63, 0x4F), "brown"), ROCK_COOL: ((0x74, 0x62, 0x5C), "all"),
           ROCK_DARK: ((0x66, 0x52, 0x4A), "all")}
# Specular IOR Level per key family (mix keys included): leaves smooth and waxy, ice icy, snow and bark matte
SPEC = {"FB_m028_leaf": 0.35, "FB_m028_ice": 0.5, "FB_m028_snow": 0.3, "FB_m028_wood": 0.3, "FB_m028_rock": 0.3}


def palette():
    for k, (hx, rough, low) in PALETTE.items():
        K.set_colour(k, hx, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hx, rough=rough, low_spec=low)
    _restyle()


def _restyle():
    for m in bpy.data.materials:
        if not m.name.startswith("FB_m028_") or not m.node_tree:
            continue
        b = m.node_tree.nodes.get("Principled BSDF")
        if not (b and "Specular IOR Level" in b.inputs):
            continue
        for pre, s in SPEC.items():
            if m.name.startswith(pre):
                b.inputs["Specular IOR Level"].default_value = s
                break


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's test dome. Returns {key: (hex, rendered)}."""
    keys = keys or list(TARGETS)
    for k in keys:
        K.fk().material(k)
    _restyle()
    try:
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


# ---- small geometry helpers ------------------------------------------------------------------------------------------
def _frame_from(d):
    d = Vector(d).normalized()
    u = d.orthogonal().normalized()
    v = d.cross(u).normalized()
    return u, v, d


def _cap(bm, ring, flip=False):
    vs = list(reversed(ring)) if flip else list(ring)
    f = bm.faces.new(vs)
    return bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="BEAUTY")["faces"]


def _seed(name):
    return 28000 + sum((i + 1) * ord(ch) for i, ch in enumerate(name))


def tube(a, pts, radii, seed, sides=8, jitter=0.06, twist=8.0, knuckle=1.08, mat=WOOD):
    """A faceted limb along the polyline pts (straight segments; each inner point is a kink with a knuckle ring
    swollen by `knuckle`), ring radii +-jitter and +-twist degrees per inner ring, flat end caps square to the first
    and last segments. Returns (verts, rings, bottom cap faces, top cap faces). (M024's tube.)"""
    rng = random.Random(seed)
    bm = a.bm
    rings = []
    u0, _, _ = _frame_from(pts[1] - pts[0])
    ph = rng.uniform(0, 2 * math.pi)
    for i, p in enumerate(pts):
        if i == 0:
            d = pts[1] - pts[0]
        elif i == len(pts) - 1:
            d = pts[-1] - pts[-2]
        else:
            d = (pts[i + 1] - pts[i]).normalized() + (pts[i] - pts[i - 1]).normalized()
        d = d.normalized()
        u = (u0 - d * u0.dot(d)).normalized()
        v = d.cross(u).normalized()
        u0 = u
        inner = 0 < i < len(pts) - 1
        tw = ph + (math.radians(rng.uniform(-twist, twist)) if inner else 0.0)
        kn = knuckle if inner else 1.0
        ring = []
        for k in range(sides):
            t = tw + 2 * math.pi * k / sides
            r = radii[i] * kn * (1 + rng.uniform(-jitter, jitter) if inner else 1 + rng.uniform(-0.03, 0.03))
            ring.append(bm.verts.new(p + (u * math.cos(t) + v * math.sin(t)) * r))
        rings.append(ring)
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            faces.append(bm.faces.new((r0[k], r0[j], r1[j], r1[k])))
    bot = _cap(bm, rings[0], flip=True)
    top = _cap(bm, rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=faces + bot + top)
    vs = [v for r in rings for v in r]
    a._finish(vs, mat, tint=1.0)
    return vs, rings, bot, top


def _hull(a, pts, merge):
    """Convex hull of pts in a's bmesh, hull triangles within `merge` degrees of coplanar merged into broad facets,
    then BEAUTY-triangulated (M014's _hull). Returns (verts, facet count before triangulation)."""
    vs = [a.bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(a.bm, input=vs)
    for v in vs:
        if v.is_valid and not v.link_faces:
            a.bm.verts.remove(v)
    vs = [v for v in vs if v.is_valid]
    faces = K.faces_of(vs)
    bmesh.ops.recalc_face_normals(a.bm, faces=faces)
    if merge:
        bmesh.ops.dissolve_limit(a.bm, angle_limit=math.radians(merge), verts=vs,
                                 edges=list({e for f in faces for e in f.edges}))
        vs = [v for v in vs if v.is_valid]
    facets = len(K.faces_of(vs))
    bmesh.ops.triangulate(a.bm, faces=[f for f in K.faces_of(vs) if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
    return vs, facets


def _sector(seed, amp=0.06):
    """Broad radius jitter by angle (sectors, never per vertex)."""
    r = random.Random(seed)
    p1, p2 = r.uniform(0, 6.3), r.uniform(0, 6.3)
    return lambda th: 1.0 + amp * math.sin(th + p1) + 0.6 * amp * math.sin(2 * th + p2)


INFO = {}


# ---- leaf (spec 1.4): a 6-sided hexagonal shard ------------------------------------------------------------------------
# section: a flattened hexagon (width x 0.7 width) with a ridge vertex on each broad face and a flat facet on each
# side edge; (across, through) in half-width / half-thickness units
LEAF_SEC = ((1.0, 0.35), (0.0, 1.0), (-1.0, 0.35), (-1.0, -0.35), (0.0, -1.0), (1.0, -0.35))
# rings (t along the leaf from its base apex, half-width fraction, twist deg); a lerp ring between B and C gives the
# colour ramp one more band without changing the outline
LEAF_RINGS = ((0.10, 0.55, 0.0), (0.30, 1.0, 2.0), (0.62, 0.98, 6.0), (0.82, 0.60, 3.0))
LEAF_MID = 0.5          # the extra ring halfway between B and C
LEAF_THICK = 0.7
LEAF_SINK = 0.15


def leaf_mesh(a, base, tip, width, face, seed, sink=LEAF_SINK):
    """One leaf shard from base (sunk `sink` back into its limb end) to tip, outline width `width`, its broad face
    toward `face`. Returns (verts, {vert: t})."""
    rng = random.Random(seed)
    bm = a.bm
    B, T = Vector(base), Vector(tip)
    d = (T - B).normalized()
    B = B - d * sink
    L = (T - B).length
    n = Vector(face)
    n = (n - d * n.dot(d)).normalized()
    w = d.cross(n).normalized()
    hw, ht = width / 2, width / 2 * LEAF_THICK
    tm = {}
    bot = bm.verts.new(B + w * rng.uniform(-0.02, 0.02) * width)
    tm[bot] = 0.0
    rings = []
    for t, rf, tw in LEAF_RINGS:
        ang = math.radians(tw * rng.uniform(-1, 1))
        ca, sa = math.cos(ang), math.sin(ang)
        jr = 1 + rng.uniform(-0.05, 0.05)
        ring = []
        for sx, sy in LEAF_SEC:
            x, y = sx * hw * rf * jr, sy * ht * rf * jr
            x, y = x * ca - y * sa, x * sa + y * ca
            ring.append(B + d * (t * L) + w * x + n * y)
        rings.append((t, ring))
    # the lerp ring between B (index 1) and C (index 2)
    (tb, rb), (tc, rc) = rings[1], rings[2]
    mid = (tb + (tc - tb) * LEAF_MID, [p.lerp(q, LEAF_MID) for p, q in zip(rb, rc)])
    rings.insert(2, mid)
    vrings = []
    for t, ring in rings:
        vr = [bm.verts.new(p) for p in ring]
        for x in vr:
            tm[x] = t
        vrings.append(vr)
    off = (w * rng.uniform(-1, 1) + n * rng.uniform(-0.5, 0.5)) * 0.03 * L
    top = bm.verts.new(T + off)
    tm[top] = 1.0
    fs = []
    k6 = len(LEAF_SEC)
    r0 = vrings[0]
    for k in range(k6):
        fs.append(bm.faces.new((bot, r0[(k + 1) % k6], r0[k])))
    for r1, r2 in zip(vrings, vrings[1:]):
        for k in range(k6):
            j = (k + 1) % k6
            fs.append(bm.faces.new((r1[k], r1[j], r2[k])))
            fs.append(bm.faces.new((r2[k], r1[j], r2[j])))
    rl = vrings[-1]
    for k in range(k6):
        fs.append(bm.faces.new((rl[k], rl[(k + 1) % k6], top)))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    vs = [bot] + [x for r in vrings for x in r] + [top]
    a._finish(vs, LEAF, tint=1.0)
    INFO.setdefault("piece_inverted", []).append(_inverted_piece(vs))
    return vs, tm


# ---- ice nodule (spec 1.4): a faceted gem, the dissolved hull of staggered rings ---------------------------------------
# (t, radius fraction, ring phase in steps)
NOD_RINGS = ((0.15, 0.45, 0.25), (0.38, 0.95, 0.0), (0.62, 1.0, 0.5), (0.84, 0.64, 0.25))
NOD_SIDES = 6
NOD_MERGE = 12.0


def nodule_mesh(a, bottom, top, width, seed, flat=1.0, sides=NOD_SIDES, merge=NOD_MERGE):
    """One ice gem from its bottom apex to its top apex, belt width `width` (flat squashes one cross axis).
    Returns (verts, {vert: t}, facets)."""
    rng = random.Random(seed)
    B, T = Vector(bottom), Vector(top)
    d = (T - B).normalized()
    L = (T - B).length
    u, v, _ = _frame_from(d)
    sec = _sector(seed + 1)
    ph = rng.uniform(0, 2 * math.pi)
    hw = width / 2
    pts = [B]
    for t, rf, step in NOD_RINGS:
        for k in range(sides):
            th = ph + 2 * math.pi * (k + step + rng.uniform(-0.12, 0.12)) / sides
            r = hw * rf * sec(th)
            tt = t * (1 + rng.uniform(-0.03, 0.03))
            pts.append(B + d * (tt * L) + (u * math.cos(th) + v * math.sin(th) * flat) * r)
    pts.append(T + (u * rng.uniform(-1, 1) + v * rng.uniform(-1, 1)) * 0.05 * L)
    vs, facets = _hull(a, pts, merge)
    tm = {x: max(0.0, min(1.0, (x.co - B).dot(d) / L)) for x in vs}
    a._finish(vs, ICE, tint=1.0)
    INFO.setdefault("piece_inverted", []).append(_inverted_piece(vs))
    INFO.setdefault("facets", []).append(facets)
    return vs, tm, facets


# ---- skeleton (spec 2.1) ----------------------------------------------------------------------------------------------
# The trunk is a column: 8-sided, Ø 0.95 at the flare -> 0.8 -> 0.75 -> 0.68 at the fork (z 2.05), then a short
# taper into the crotch (its small cap ends inside the tall limb). Low limbs leave at z 1.15-1.3; the fork at 2.05.
TRUNK = (((0.0, 0.0, -0.1), (0.0, 0.0, 0.2), (0.02, 0.0, 0.6), (0.08, 0.02, 1.25), (0.25, 0.05, 2.05),
          (0.2, 0.02, 2.3)),
         (0.47, 0.47, 0.40, 0.375, 0.34, 0.2))
# name: (polyline from inside the parent -> kinks -> flat end, radius start, radius end)
LIMBS = {
    "LB": (((0.0, -0.05, 1.3), (-0.55, -0.2, 1.5), (-0.95, -0.35, 1.66)), 0.225, 0.2),
    "LBup": (((-0.72, -0.25, 1.58), (-0.82, 0.17, 1.94)), 0.18, 0.17),
    "LBfr": (((-0.66, -0.28, 1.56), (-0.78, -0.48, 1.95)), 0.18, 0.17),
    "RB": (((0.15, -0.05, 1.15), (0.58, -0.3, 1.42)), 0.21, 0.19),
    "RBup": (((0.36, -0.17, 1.25), (0.43, -0.22, 1.52)), 0.13, 0.12),
    "TL": (((0.22, 0.05, 1.95), (0.1, -0.05, 2.45), (-0.3, -0.1, 3.42)), 0.22, 0.19),
    "RBr": (((0.22, 0.05, 2.0), (0.75, 0.0, 2.2), (1.7, -0.05, 2.62)), 0.21, 0.18),
    "NRs": (((0.6, 0.0, 2.12), (0.66, 0.0, 2.42)), 0.16, 0.15),
    "CS": (((0.24, 0.08, 2.05), (0.45, 0.32, 2.62), (0.64, 0.55, 2.98)), 0.18, 0.16),
}
# limbs whose end carries a leaf or a nodule: in the hero the end is a hidden joining surface, bark-coloured (a pale
# cut cap peeked out beside the up-left leaf's base); the exported stem shows them as pale cut ends, as the exploded does
JOINS = {"LB", "LBup", "LBfr", "RB", "NRs"}
# the fork and split points (the dark crotch fields)
CROTCHES = ((0.25, 0.05, 2.08), (0.08, -0.05, 1.25), (0.15, -0.05, 1.18), (-0.72, -0.28, 1.65), (0.62, 0.0, 2.3))


def limb_points(name, table=None):
    pts, r0, r1 = (table or LIMBS)[name]
    pts = [Vector(p) for p in pts]
    acc = [0.0]
    for p, q in zip(pts, pts[1:]):
        acc.append(acc[-1] + (q - p).length)
    rad = [r0 + (r1 - r0) * s / acc[-1] for s in acc]
    return pts, rad


def skeleton(a):
    """The trunk (8-sided column) and the limbs (8-sided kinked tubes). Returns {name: (verts, caps)} with caps the
    limb's flat end-cap faces (the cut ends)."""
    out = {}
    pts, rad = TRUNK
    vs, _, bot, top = tube(a, [Vector(p) for p in pts], list(rad), _seed("trunk"), sides=8, jitter=0.05,
                           knuckle=1.0)
    out["trunk"] = (vs, [])
    for name in LIMBS:
        pts, rad = limb_points(name)
        vs, _, bot, top = tube(a, pts, rad, _seed(name), sides=8, jitter=0.06, twist=8.0)
        out[name] = (vs, top)
    return out


# ---- leaves and nodules (spec 2.2, 2.3) ----------------------------------------------------------------------------------
# name: (base, tip, outline width, broad face toward, light mix at the tip)
LEAVES = {
    "UL": ((-0.78, -0.48, 1.95), (-1.55, -0.62, 3.3), 0.85, (0.15, -1.0, 0.1), 0.5),
    "LL": ((-0.95, -0.35, 1.66), (-2.26, -0.3, 1.4), 0.66, (0.0, -1.0, 0.36), 0.75),
    "R": ((0.58, -0.3, 1.42), (2.26, -0.9, 2.05), 0.88, (0.0, -1.0, 0.47), 0.5),
}
# name: (bottom apex, top apex, belt width, flat, tier)
NODULES = {
    "NR": ((0.6, 0.0, 2.32), (1.33, 0.05, 3.6), 0.92, 0.92, "canopy"),
    "NB": ((-0.8, 0.14, 1.9), (-1.28, 0.44, 3.08), 0.88, 0.92, "canopy"),
}
BASE_NODULES = {
    "FL": ((-0.95, -0.55, 0.2), (-1.13, -0.8, 1.22), 0.9, 0.9, "deep"),
    "FR": ((0.95, -0.5, 0.2), (1.1, -0.74, 1.16), 0.86, 0.9, "base"),
    "BL": ((-0.9, 0.65, 0.28), (-1.1, 0.92, 1.12), 0.78, 0.9, "base"),
    "BR": ((0.9, 0.6, 0.28), (1.1, 0.88, 1.12), 0.78, 0.9, "base"),
}

# the base gems: 5 points per ring, so their facets read as big as the sheet's (6 rendered as many-faceted balls)
BASE_NOD_SIDES = 5

# ---- base (spec 2.4) ------------------------------------------------------------------------------------------------------
RING = (1.58, 1.28)
ROCK_SINK = 0.08
ROCK_RINGS = [(0.0, 0.92, 6), (0.45, 1.0, 6), (0.86, 0.68, 4)]
# name: (az deg, d (tangential width), h, warm?)
ROCKS = (("K1", 235, 0.75, 0.42, True), ("K11", 258, 0.45, 0.3, True), ("K3", 205, 0.62, 0.45, False),
         ("K4", 178, 0.68, 0.5, False), ("K10", 145, 0.62, 0.45, False), ("K9", 112, 0.62, 0.42, True),
         ("K8", 78, 0.62, 0.42, True), ("K7", 43, 0.62, 0.45, True), ("K6", 12, 0.62, 0.5, False),
         ("K5", 340, 0.68, 0.58, False), ("K2", 305, 0.85, 0.55, True))
SNOW_SINK = 0.1
SNOW_RINGS = [(0.0, 0.95, 6), (0.45, 1.0, 6), (0.82, 0.74, 5), (1.0, 0.32, 2)]
PAD_RINGS = [(0.0, 1.0, 8), (0.55, 0.95, 8), (1.0, 0.68, 5)]
# name: (centre x, y, radius x, radius y, top z)
SNOW_LUMPS = (("S1", -0.5, -0.6, 0.78, 0.66, 0.62), ("S2", 0.5, -0.62, 0.78, 0.66, 0.6),
              ("S3", 0.0, 0.3, 0.85, 0.68, 0.8), ("S4", -0.8, 0.45, 0.62, 0.55, 0.62),
              ("S5", 0.8, 0.45, 0.62, 0.55, 0.6))
PAD = (0.0, 0.0, 1.42, 1.2, 0.45)


def _dome(a, centre, rx, ry, hz, rings, seed, merge, rot=0.0, jitter=0.09, lean=(0.0, 0.0), mat=ROCK):
    """A closed faceted dome: the convex hull of jittered point rings (height frac, radius frac, points) from its
    flat bottom at centre.z, near-coplanar hull triangles merged into broad facets (merge deg)."""
    rng = random.Random(seed)
    C = Vector(centre)
    cr, sr = math.cos(rot), math.sin(rot)
    pts = []
    for hf, rf, n in rings:
        off = rng.uniform(0, 2 * math.pi)
        for k in range(n):
            th = off + 2 * math.pi * (k + rng.uniform(-0.22, 0.22)) / n
            r = rf * (1 + rng.uniform(-jitter, jitter))
            z = hf * hz * (1 + (rng.uniform(-jitter, jitter) if 0 < hf < 1 else 0))
            x = math.cos(th) * rx * r + lean[0] * rx * hf
            y = math.sin(th) * ry * r + lean[1] * ry * hf
            pts.append(C + Vector((x * cr - y * sr, x * sr + y * cr, z)))
    vs, facets = _hull(a, pts, merge)
    a._finish(vs, mat, tint=1.0)
    return vs


ROCK_MERGE = 8.0
SNOW_MERGE = 5.0


def rock_mesh(a, name, az, d, h, seed):
    ang = math.radians(az)
    loc = (RING[0] * math.cos(ang), RING[1] * math.sin(ang), -ROCK_SINK)
    rng = random.Random(seed)
    return _dome(a, loc, 0.46 * d, 0.58 * d, h + ROCK_SINK, ROCK_RINGS, seed, ROCK_MERGE,
                 rot=ang + rng.uniform(-0.2, 0.2), lean=(rng.uniform(-0.12, 0.12), rng.uniform(-0.12, 0.12)))


def snow_mesh(a, x, y, rx, ry, top, seed, rings=SNOW_RINGS):
    return _dome(a, (x, y, -SNOW_SINK), rx, ry, top + SNOW_SINK, rings, seed, SNOW_MERGE,
                 rot=random.Random(seed).uniform(0, 6.28), jitter=0.07, mat=SNOW)


def base_pieces(a):
    """The snow pad and lumps, the four base nodules and the eleven rocks. Returns dict of piece lists."""
    snow = [snow_mesh(a, *PAD, _seed("pad"), rings=PAD_RINGS)]
    for name, x, y, rx, ry, top in SNOW_LUMPS:
        snow.append(snow_mesh(a, x, y, rx, ry, top, _seed(name)))
    nods = []
    for name, (b, t, w, fl, tier) in BASE_NODULES.items():
        vs, tm, _ = nodule_mesh(a, b, t, w, _seed(name), flat=fl, sides=BASE_NOD_SIDES)
        nods.append((name, vs, tm, tier))
    rocks = []
    for name, az, d, h, warm in ROCKS:
        rocks.append((name, rock_mesh(a, name, az, d, h, _seed(name)), warm, h))
    return {"snow": snow, "nods": nods, "rocks": rocks}


def canopy_pieces(a):
    leaves = []
    for name, (b, t, w, face, light) in LEAVES.items():
        vs, tm = leaf_mesh(a, b, t, w, face, _seed(name))
        leaves.append((name, vs, tm, light))
    nods = []
    for name, (b, t, w, fl, tier) in NODULES.items():
        vs, tm, _ = nodule_mesh(a, b, t, w, _seed(name), flat=fl)
        nods.append((name, vs, tm, tier))
    return leaves, nods


def hero(a):
    """FrostBushNode: skeleton first (the union's starting shell), then the canopy, then the base."""
    INFO.clear()
    sk = skeleton(a)
    leaves, cnods = canopy_pieces(a)
    base = base_pieces(a)
    paint_skeleton(a, sk)
    for name, vs, tm, light in leaves:
        paint_leaf(a, vs, tm, light, _seed(name) + 3)
    for name, vs, tm, tier in cnods + base["nods"]:
        paint_nodule(a, vs, tm, tier, _seed(name) + 3)
    paint_base(a, base, trunk_vs=sk["trunk"][0])


# ---- parts --------------------------------------------------------------------------------------------------------------
def stem_part(a):
    """FrostBushStem: the hero skeleton alone (floor-cut at the foot)."""
    paint_skeleton(a, skeleton(a), hero=False)


def leaf_part(a):
    """FrostBushLeaf: the up-left leaf's size (1.65 x 0.85 x 0.6), lying along +X, broad face toward -Y."""
    vs, tm = leaf_mesh(a, (0.0, 0.0, 0.5), (1.65, 0.0, 0.5), 0.85, (0.0, -1.0, 0.0), _seed("part_leaf"), sink=0.0)
    paint_leaf(a, vs, tm, 0.5, _seed("part_leaf") + 3)


def nodule_part(a):
    """FrostBushIceNodule: the right nodule's size (1.45 x 0.92), upright."""
    vs, tm, _ = nodule_mesh(a, (0.0, 0.0, 0.0), (0.0, 0.0, 1.45), 0.92, _seed("NR"), flat=0.92)
    paint_nodule(a, vs, tm, "soft", _seed("part_nod"))


def base_part(a):
    """FrostBushBase: rock ring, snow mound and four base nodules (the trunk foot's socket left solid)."""
    base = base_pieces(a)
    for name, vs, tm, tier in base["nods"]:
        paint_nodule(a, vs, tm, tier, _seed(name) + 3)
    paint_base(a, base)


# ---- stage 4: colour by position fields (never facing) ---------------------------------------------------------------
MOTTLE = {"leaf": dict(amp=0.02, scale=0.5, jitter=0.003), "ice": dict(amp=0.02, scale=0.5, jitter=0.003),
          "snow": dict(amp=0.02, scale=0.5, jitter=0.003), "wood": dict(amp=0.04, scale=0.35, jitter=0.004),
          "rock": dict(amp=0.05, scale=0.45, jitter=0.005)}
PIECE_TINT = 0.03
WOOD_FIELD = dict(crotch_r=(0.22, 0.38), collar=(0.95, 1.12), leaf_r=(0.22, 0.36), mix=0.5, patch_scale=0.6,
                  patch_level=0.38, patch_mix=0.25, ramp=0.06)


def _q4(t):
    return round(max(0.0, min(1.0, t)) * 4) / 4


def _mix(k1, k2, t):
    t = _q4(t)
    return k1 if t <= 0 else k2 if t >= 1 else K.mix_key(k1, k2, t)


def _mottle(a, faces, level, kind, seed):
    m = MOTTLE[kind]
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in faces:
        c = f.calc_center_median()
        k = level * (1.0 + m["amp"] * 1.6 * noise.noise(c * m["scale"] + off) + rng.uniform(-m["jitter"], m["jitter"]))
        for lo in f.loops:
            lo[a.tint_layer] = (k, k, k, 1.0)


def leaf_key(t, light):
    """deep at the base (100 / 75 / 50 / 25 % over t 0 .. 0.42), the key across the belt, toward light at the tip."""
    deep = (0.42 - t) / 0.30
    if deep > 0.125:
        return _mix(LEAF, LEAF_DEEP, deep)
    return _mix(LEAF, LEAF_LIGHT, light * (t - 0.6) / 0.3)


def paint_leaf(a, vs, tm, light, seed):
    rng = random.Random(seed)
    nf = K.noise_field(scale=0.9, seed=seed)
    fs = K.faces_of(vs)
    for f in fs:
        c = f.calc_center_median()
        t = sum(tm[v] for v in f.verts) / len(f.verts) + 0.06 * 1.6 * nf(c)
        f.material_index = a._mi(leaf_key(t, light))
    _mottle(a, fs, 1.0 + rng.uniform(-PIECE_TINT, PIECE_TINT), "leaf", seed + 1)


def nodule_key(t, tier):
    """deep at the bottom (fading to the key by t 0.45), pale over the crown; FL deep with a 25 % ice crown. The
    upright exported part ("soft") keeps only 25 % mixes at its ends: the full ramp on an upright gem follows the
    face direction (K.check corr 0.79)."""
    if tier == "soft":
        return _mix(ICE, ICE_DEEP, 0.25) if t < 0.3 else _mix(ICE, ICE_PALE, 0.25) if t > 0.7 else ICE
    if tier == "deep":
        return _mix(ICE_DEEP, ICE, (t - 0.55) / 0.4 * 0.5)
    deep = (0.38 - t) / 0.28
    if tier == "base":
        # the half-buried base gems read mid blue on the sheet (FR #A6C9F6, the back pair alike): a deeper bottom
        # half and only a 25 % pale crown
        deep = (0.5 - t) / 0.3
        if deep > 0.125:
            return _mix(ICE, ICE_DEEP, deep)
        return _mix(ICE, ICE_PALE, 0.25 if t > 0.78 else 0.0)
    if deep > 0.125:
        return _mix(ICE, ICE_DEEP, deep)
    return _mix(ICE, ICE_PALE, (t - 0.52) / 0.3)


def paint_nodule(a, vs, tm, tier, seed):
    rng = random.Random(seed)
    nf = K.noise_field(scale=0.9, seed=seed)
    fs = K.faces_of(vs)
    for f in fs:
        c = f.calc_center_median()
        t = sum(tm[v] for v in f.verts) / len(f.verts) + 0.05 * 1.6 * nf(c)
        f.material_index = a._mi(nodule_key(t, tier))
    _mottle(a, fs, 1.0 + rng.uniform(-PIECE_TINT, PIECE_TINT), "ice", seed + 1)


def _near(d, r):
    return 1.0 if d < r[0] else 0.5 if d < r[1] else 0.0


def _ramp(n, F):
    lv = F["patch_level"]
    if n > lv + F["ramp"]:
        return F["patch_mix"]
    if n > lv:
        return F["patch_mix"] * 0.5
    return 0.0


def paint_skeleton(a, sk, hero=True):
    """Bark by position: dark mixes at the forks, (hero only) at the snow collar and under the leaf bases, broad
    patches; flat cut ends pale. The exported stem part has no snow or leaves, so it keeps only the forks and patches
    (with the hero's fields its parts shot rendered #795946 against the sheet's exploded stem #855D44)."""
    W = WOOD_FIELD
    pf = K.noise_field(scale=W["patch_scale"], seed=28090)
    crot = [Vector(c) for c in CROTCHES]
    lbase = [Vector(v[0]) for v in LEAVES.values()]
    for name, (vs, caps) in sk.items():
        capset = set() if hero and name in JOINS else set(caps)
        fs = K.faces_of(vs)
        for f in fs:
            if f in capset:
                f.material_index = a._mi(WOOD_CUT)
                continue
            c = f.calc_center_median()
            t = W["mix"] * max(_near((c - p).length, W["crotch_r"]) for p in crot)
            if hero:
                t = max(t, W["mix"] * max(_near((c - p).length, W["leaf_r"]) for p in lbase))
            if hero and name == "trunk":
                t = max(t, W["mix"] * (1.0 if c.z < W["collar"][0] else 0.5 if c.z < W["collar"][1] else 0.0))
            t = max(t, _ramp(pf(c), W))
            f.material_index = a._mi(_mix(WOOD, WOOD_DARK, t))
        _mottle(a, [f for f in fs if f not in capset], 1.0, "wood", _seed(name) + 9)
        _mottle(a, [f for f in fs if f in capset], 1.0, "leaf", _seed(name) + 10)


def paint_base(a, base, trunk_vs=None):
    contact = [vs for _, vs, _, _ in base["nods"]] + [vs for _, vs, _, _ in base["rocks"]]
    if trunk_vs:
        contact.append(trunk_vs)
    trees = [K.bvh_of(vs) for vs in contact]

    def dist(c):
        return min(t.find_nearest(c)[3] or 9.0 for t in trees)

    for i, vs in enumerate(base["snow"]):
        fs = K.faces_of(vs)
        for f in fs:
            dd = dist(f.calc_center_median())
            f.material_index = a._mi(_mix(SNOW, SNOW_BLUE, 0.75 if dd < 0.12 else 0.5 if dd < 0.25 else
                                          0.25 if dd < 0.32 else 0.0))
        _mottle(a, fs, 1.0, "snow", _seed("snow") + i)
    rtrees = [K.bvh_of(vs) for _, vs, _, _ in base["rocks"]]
    for i, (name, vs, warm, h) in enumerate(base["rocks"]):
        key = ROCK if warm else ROCK_COOL
        others = [t for j, t in enumerate(rtrees) if j != i]
        fs = K.faces_of(vs)
        for f in fs:
            c = f.calc_center_median()
            zr = (c.z + ROCK_SINK) / (h + ROCK_SINK)
            t = 0.5 if zr < 0.18 else 0.25 if zr < 0.32 else 0.0
            dn = min(tt.find_nearest(c)[3] or 9.0 for tt in others)
            t = max(t, 0.5 if dn < 0.06 else 0.25 if dn < 0.14 else 0.0)
            f.material_index = a._mi(_mix(key, ROCK_DARK, t))
        _mottle(a, fs, 1.0 + random.Random(_seed(name)).uniform(-0.04, 0.04), "rock", _seed(name) + 2)


# ---- checks on pieces ----------------------------------------------------------------------------------------------------
def _inverted_piece(vs):
    """Faces of one closed piece whose normal points into the piece (ray parity). Must be 0."""
    from mathutils.bvhtree import BVHTree
    fs = K.faces_of(vs)
    idx = {v: i for i, v in enumerate(vs)}
    for f in fs:
        f.normal_update()
    t = BVHTree.FromPolygons([v.co.copy() for v in vs], [[idx[v] for v in f.verts] for f in fs])
    bad = 0
    for f in fs:
        n = f.normal.normalized()
        o = f.calc_center_median() + n * 1e-4
        hits = 0
        while hits < 50:
            loc = t.ray_cast(o, n)[0]
            if loc is None:
                break
            hits += 1
            o = loc + n * 1e-5
        bad += hits % 2
    return bad


# ---- cleanup (M024's guarded procedure, copied: the other builders change in parallel) ---------------------------------
def _volume(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    v = bm.calc_volume(signed=True)
    bm.free()
    return v


UNION_MERGE = 0.0005


def _union(o, tries=4):
    """Guarded union: each shell is unioned on with an exact boolean, one at a time, the result checked against the
    volumes going in; a bad result is undone and the shell retried nudged a few thousandths of a stud; a shell that
    still fails is tried once more at the end, then reported and left out. Returns {"shells", "retried", "failed"}."""
    act = bpy.context.view_layer.objects.active
    if act and act.mode != "OBJECT":
        with bpy.context.temp_override(active_object=act, object=act):
            bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()
    others = M.split_loose(o)
    bpy.context.view_layer.update()
    retried, failed = [], []
    rng = random.Random(28900)
    queue = [(i, p, False) for i, p in enumerate(others)]
    while queue:
        i, p, late = queue.pop(0)
        for ob in (o, p):
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            loose = [v for v in bm.verts if not v.link_faces]
            if loose:
                bmesh.ops.delete(bm, geom=loose, context="VERTS")
                bm.to_mesh(ob.data)
            bm.free()
        v0, vp = _volume(o.data), _volume(p.data)
        home = p.matrix_world.copy()
        ok = False
        for t in range(tries if late else 2):
            keep = o.data.copy()
            if t:
                p.matrix_world = Matrix.Translation(Vector([rng.uniform(-1, 1) * 0.006 * t for _ in range(3)])) @ home
            bpy.context.view_layer.update()
            m = o.modifiers.new("U", "BOOLEAN")
            m.operation, m.solver, m.object = "UNION", "EXACT", p
            m.material_mode = "TRANSFER"
            with M._override(o):
                bpy.ops.object.modifier_apply(modifier=m.name)
            v1 = _volume(o.data)
            if v1 >= max(v0, vp) * 0.995 and v1 <= (v0 + vp) * 1.005 and _nshells(o) == 1:
                ok = True
                bpy.data.meshes.remove(keep)
                if t or late:
                    retried.append((i, t, late))
                break
            old = o.data
            o.data = keep
            bpy.data.meshes.remove(old)
        if not ok and not late:
            p.matrix_world = home
            queue.append((i, p, True))
            continue
        if not ok:
            ctr = sum((p.matrix_world @ v.co for v in p.data.vertices), Vector()) / max(1, len(p.data.vertices))
            failed.append((i, [round(c, 2) for c in ctr], round(v0, 3), round(vp, 3)))
        pm = p.data
        bpy.data.objects.remove(p, do_unlink=True)
        if pm.users == 0:
            bpy.data.meshes.remove(pm)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=UNION_MERGE)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=UNION_MERGE)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    M.drop_specks(bm, min_area=0.02)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    K.drop_unused_slots(o)
    return {"shells": len(others) + 1, "retried": retried, "failed": failed}


def _nshells(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = M._shell_ids(bm)[1]
    bm.free()
    return n


def _shell_report(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    out = []
    for k in range(n):
        fs = [f for f in bm.faces if ids[f.index] == k]
        c = sum((f.calc_center_median() for f in fs), Vector()) / len(fs)
        out.append((sum(len(f.verts) - 2 for f in fs), [round(x, 2) for x in c]))
    bm.free()
    return sorted(out, reverse=True)


def _self_hits(o):
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    pairs = [(x, y) for x, y in tree.overlap(tree) if x < y and not set(bm.faces[x].verts) & set(bm.faces[y].verts)]
    where = [[round(c, 2) for c in bm.faces[x].calc_center_median()] for x, _ in pairs[:5]]
    bm.free()
    return len(pairs), where


def inverted(o):
    return len(_inverted_ids(o))


def _inverted_ids(o):
    """Face indices whose front side is solid (ray parity along the normal is odd)."""
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.normal_update()
    t = BVHTree.FromBMesh(bm)
    out = []
    for f in bm.faces:
        if f.calc_area() < 1e-12:
            continue
        n = f.normal.normalized()
        p = f.calc_center_median() + n * 1e-4
        hits = 0
        while hits < 60:
            loc = t.ray_cast(p, n)[0]
            if loc is None:
                break
            hits += 1
            p = loc + n * 1e-5
        if hits % 2:
            out.append(f.index)
    bm.free()
    return out


def _guarded(o, fn):
    """Run a cleanup step on o; undo it if it leaves more crossing faces or more shells than before."""
    before = (_self_hits(o)[0], len(_shell_report(o)))
    keep = o.data.copy()
    out = fn()
    after = (_self_hits(o)[0], len(_shell_report(o)))
    if after[0] > before[0] or after[1] > before[1]:
        old = o.data
        o.data = keep
        bpy.data.meshes.remove(old)
        return None
    bpy.data.meshes.remove(keep)
    return out


def _finish(o):
    res = M.finish(o, union=False, uv=UV)
    for _ in range(3):
        crumbs = m012._drop_inner(o)
        if not (crumbs or res["nonmanifold_edges"] or res["boundary_edges"]):
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
        _guarded(o, lambda: m012._force_slivers(o))
        res = M.finish(o, union=False, uv=UV)
    return res


def _tri_quads(bm):
    n = 0
    for f in [f for f in bm.faces if len(f.verts) > 3]:
        if not f.is_valid or len(f.verts) < 4:
            continue
        if len(f.verts) > 4:
            bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="BEAUTY")
            n += 1
            continue
        a, b, c, d = f.verts
        opts = sorted(((min(m011._min_angle([p.co, q.co, r.co]), m011._min_angle([p.co, q.co, s.co])), p, q)
                       for p, q, r, s in ((a, c, b, d), (b, d, c, a))), key=lambda x: -x[0])
        for _, p, q in opts:
            e = bm.edges.get((p, q))
            if e is None or bmesh.ops.rotate_edges(bm, edges=[e], use_ccw=False)["edges"]:
                break
        else:
            continue
        if f.is_valid and len(f.verts) == 4:
            bmesh.ops.connect_verts(bm, verts=[p, q])
            n += 1
    leftover = [f for f in bm.faces if len(f.verts) > 3]
    if leftover:
        bmesh.ops.triangulate(bm, faces=leftover, quad_method="BEAUTY", ngon_method="BEAUTY")
    return n


def _collapse_needles(o, max_len=0.05, lim=POLISH_LIM):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = 0
    for _ in range(30):
        bad = None
        for f in bm.faces:
            if math.degrees(m011._min_angle([v.co for v in f.verts])) < lim:
                e = min(f.edges, key=lambda e: e.calc_length())
                if e.calc_length() < max_len and all(v.co.z > 1e-4 for v in e.verts):
                    bad = e
                    break
        if bad is None:
            break
        bmesh.ops.collapse(bm, edges=[bad], uvs=True)
        n += 1
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    return n


def _flip_thin(o, lim=POLISH_LIM, max_bend=20.0):
    """Needles with no short edge: rotate the needle's longest edge when both new triangles are fatter and the two
    faces are nearly coplanar. Returns flips."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = 0
    for _ in range(20):
        done = False
        for f in list(bm.faces):
            if not f.is_valid or len(f.verts) != 3:
                continue
            if math.degrees(m011._min_angle([v.co for v in f.verts])) >= lim:
                continue
            e = max(f.edges, key=lambda e: e.calc_length())
            if len(e.link_faces) != 2:
                continue
            g = e.link_faces[0] if e.link_faces[1] is f else e.link_faces[1]
            if math.degrees(f.normal.angle(g.normal, 0.0)) > max_bend:
                continue
            a, b = e.verts
            c = next(v for v in f.verts if v not in (a, b))
            d = next(v for v in g.verts if v not in (a, b))
            if bm.edges.get((c, d)):
                continue
            new = min(m011._min_angle([a.co, c.co, d.co]), m011._min_angle([b.co, c.co, d.co]))
            old = min(m011._min_angle([v.co for v in f.verts]), m011._min_angle([v.co for v in g.verts]))
            if new <= old:
                continue
            if bmesh.ops.rotate_edges(bm, edges=[e], use_ccw=False)["edges"]:
                n += 1
                done = True
                break
        if not done:
            break
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    return n


def _loops(edges):
    nbr = {}
    for e in edges:
        a, b = e.verts
        nbr.setdefault(a, []).append(b)
        nbr.setdefault(b, []).append(a)
    seen, out = set(), []
    for v0 in nbr:
        if v0 in seen or len(nbr[v0]) != 2:
            continue
        loop, prev, v = [v0], None, v0
        seen.add(v0)
        while True:
            nxt = next((w for w in nbr[v] if w is not prev), None)
            if nxt is None or nxt is v0 or nxt in seen or len(nbr[nxt]) != 2:
                break
            loop.append(nxt)
            seen.add(nxt)
            prev, v = v, nxt
        if len(loop) >= 3:
            out.append(loop)
    return out


def _fan_fill(bm, bnd):
    made = 0
    for loop in _loops(bnd):
        k = len(loop)
        for s0 in range(k):
            vs = loop[s0:] + loop[:s0]
            if any(bm.edges.get((vs[0], vs[i])) for i in range(2, k - 1)):
                continue
            for i in range(1, k - 1):
                try:
                    bm.faces.new((vs[0], vs[i], vs[i + 1]))
                    made += 1
                except ValueError:
                    pass
            break
    return made


def _seal(o, rounds=3):
    n = 0
    for _ in range(rounds):
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bnd = [e for e in bm.edges if e.is_boundary]
        if not bnd:
            bm.free()
            break
        n += _fan_fill(bm, bnd)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY")
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(o.data)
        bm.free()
        M.repair_nonmanifold(o)
    return n


def _polish(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = _tri_quads(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = _guarded(o, lambda: m012._force_slivers(o, lim=POLISH_LIM))
    if forced is None:
        forced = _guarded(o, lambda: m012._force_slivers(o, lim=3.0, max_len=0.08))
    needles = _guarded(o, lambda: _collapse_needles(o))
    removed = []
    for _ in range(4):
        bad = _inverted_ids(o)
        if not bad:
            break
        removed.append(len(bad))
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.faces[i] for i in bad], context="FACES")
        bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bm.to_mesh(o.data)
        bm.free()
        _seal(o)
        _guarded(o, lambda: m012._force_slivers(o, lim=POLISH_LIM))
    late = []
    for ml in (0.15, 0.3, 0.5):
        if not m012._thin(o, POLISH_LIM)["under"]:
            break
        late.append(_guarded(o, lambda: m012._force_slivers(o, lim=POLISH_LIM, max_len=ml)))
    if m012._thin(o, POLISH_LIM)["under"]:
        late.append(_guarded(o, lambda: _flip_thin(o)))
    bc = m011._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
    o.data.update()
    M.smart_uv(o, **UV)
    return {"split": split, "forced": forced, "needles": needles, "late": late, "inverted_removed": removed,
            "uv_cut": m012._uv_unfold(o)}


CLEAN_MOVE = 0.05


def _clean_mesh(o, planes=(0.0,)):
    pockets = m012._drop_inner(o)
    log = None
    for mv in (CLEAN_MOVE, CLEAN_MOVE / 2, CLEAN_MOVE / 4):
        log = _guarded(o, lambda: m011._clean(o, m011._plane_lock(planes), max_move=mv))
        if log is not None:
            log["max_move"] = mv
            break
    log = log or {"undone": True}
    pockets += m012._drop_inner(o)
    log["pockets"] = pockets
    log["forced"] = _guarded(o, lambda: m012._force_slivers(o))
    return log


def _floor_cut(o, z0):
    """Cut everything below z0 and cap the cut flat at z 0 (M004's floor_cut, but the cap is a scanfill of every
    cut loop at once, so a loop nested inside another (a pocket between rocks and snow) stays a hole instead of
    being filled twice: holes_fill made overlapping floor faces here)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), plane_co=(0, 0, z0),
                           plane_no=(0, 0, -1), clear_outer=True)
    below = [v for v in bm.verts if v.co.z < z0 - 1e-4]
    if below:
        bmesh.ops.delete(bm, geom=below, context="VERTS")
    for v in bm.verts:
        if v.co.z < z0 + 0.004:
            v.co.z = z0
        v.co.z -= z0
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bnd = [e for e in bm.edges if e.is_boundary]
    made = 0
    if bnd:
        made = len(bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=bnd,
                                           normal=(0, 0, -1))["geom"])
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    return made


def _dissolve_flat(o, angle):
    """Limited dissolve of near-coplanar faces (union seams cut broad facets into fans), keeping every colour edge,
    then BEAUTY triangulation: the same shape in fewer triangles (M021's)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n0 = len(bm.faces)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(angle), verts=list(bm.verts), edges=list(bm.edges),
                             delimit={"MATERIAL"})
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    n1 = len(bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    return [n0, n1]


DISSOLVE = 4.0


def _floor_needles(o, lim=POLISH_LIM, max_len=0.06):
    """Needle triangles in the flat floor cap (the shared passes leave verts at z 0 alone): flip a floor-floor edge
    when that makes both triangles fatter (merging short rim edges instead bent the wall faces into a 0.4 deg fold).
    The floor stays one flat plane; needles fanned from a rim vertex with no better diagonal are left (hidden under
    the asset). Returns [flips, 0]."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    flips = merges = 0

    def floor(f):
        return f.normal.z < -0.99 and abs(f.calc_center_median().z) < 1e-3

    def ang(f):
        return math.degrees(m011._min_angle([v.co for v in f.verts]))

    skip = set()
    for _ in range(40):
        bm.normal_update()
        bad = next((f for f in bm.faces if f not in skip and len(f.verts) == 3 and floor(f) and ang(f) < lim), None)
        if bad is None:
            break
        best = None
        for e in bad.edges:
            if len(e.link_faces) != 2:
                continue
            g = e.link_faces[0] if e.link_faces[1] is bad else e.link_faces[1]
            if not floor(g) or len(g.verts) != 3:
                continue
            a, b = e.verts
            c = next(v for v in bad.verts if v not in (a, b))
            d = next(v for v in g.verts if v not in (a, b))
            if bm.edges.get((c, d)):
                continue
            # the flipped pair must stay convex (both new triangles on the same side as before)
            n1 = (a.co - c.co).cross(d.co - c.co)
            n2 = (d.co - c.co).cross(b.co - c.co)
            if n1.z * n2.z <= 0:
                continue
            new = min(m011._min_angle([a.co, c.co, d.co]), m011._min_angle([b.co, c.co, d.co]))
            if new > m011._min_angle([v.co for v in bad.verts]) and (best is None or new > best[0]):
                best = (new, e)
        if best and bmesh.ops.rotate_edges(bm, edges=[best[1]], use_ccw=False)["edges"]:
            flips += 1
            continue
        skip.add(bad)
        if len(skip) > 20:
            break
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    return [flips, merges]


def _fix_floor(o, key):
    """Faces the floor cut made (flat, facing down at z 0): the given key, Tint 0.95."""
    p = m011._Paint(o, off=(0, 0, 0))
    lay = p.tint_layer
    for f in p.bm.faces:
        if f.normal.z < -0.99 and abs(f.calc_center_median().z) < 1e-3:
            f.material_index = p._mi(key)
            for lo in f.loops:
                lo[lay] = (0.95, 0.95, 0.95, 1.0)
    p.done()


# ---- stages 5 + 6 ---------------------------------------------------------------------------------------------------------
# Stage 5: nothing. The sheet shows a sunlit sapling on snow: no emissive key, no light (decision 7). The ice nodules
# are not self-lit (their shade facets keep the leaves' lit / shade ratio).
# Stage 6: nothing. No glow, sparkle, frost mist or particles on the sheet: no socket (decision 7).

# ---- build ---------------------------------------------------------------------------------------------------------------
PARTS = (("FrostBushStem", stem_part), ("FrostBushLeaf", leaf_part), ("FrostBushIceNodule", nodule_part),
         ("FrostBushBase", base_part))
HERO = "FrostBushNode"
UNION_PARTS = {"FrostBushStem", "FrostBushBase"}
FLOOR_PARTS = {"FrostBushStem": WOOD, "FrostBushBase": ROCK}
# the flat underside is never seen in game; a mid rock tone keeps its big down-facing area out of the shading check
FLOOR_KEY = ROCK
NOTES = {
    HERO: "frost shrub (forage shrub): a bare brown sapling (8-sided trunk column forking into a tall up-left limb, "
          "a right branch and a centre limb, flat cut ends) with three dark-blue hexagonal leaf shards and two pale "
          "faceted ice gems, on a snow mound with four ice gems inside a ring of eleven warm and grey-brown rocks; "
          "one closed mesh, flat base",
    "FrostBushStem": "Forked Stem (reusable): 8-sided trunk column, left branch with two stubs, right limb, tall "
                     "up-left limb, right branch and centre limb, flat pale cut ends",
    "FrostBushLeaf": "Leaf (reusable): a dark-blue 6-sided hexagonal shard (1.65 x 0.85 x 0.6), deep base to light tip",
    "FrostBushIceNodule": "Ice Nodule (reusable): a pale faceted ice gem (1.45 x 0.92), deep bottom to pale crown",
    "FrostBushBase": "Base (reusable): eleven warm and grey-brown rocks round a lumpy snow mound with four ice gems, "
                     "flat underside",
}


def _make(name, fn, role, budget):
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget, collision="hull",
             tint_var=0.0)
    lg = {}
    if role == "hero" or name in UNION_PARTS:
        lg["union"] = _union(o)
    if role == "hero" or name in FLOOR_PARTS:
        hoff = M._build_offset(fn)
        lg["floor"] = _floor_cut(o, -hoff.z)
        _fix_floor(o, FLOOR_KEY if role == "hero" else FLOOR_PARTS[name])
        lg["dissolve"] = _guarded(o, lambda: _dissolve_flat(o, DISSOLVE))
        lg["clean"] = _clean_mesh(o, (0.0,))
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    if role == "hero" or name in FLOOR_PARTS:
        lg["floor_needles"] = _guarded(o, lambda: _floor_needles(o))
        if lg["floor_needles"] and any(lg["floor_needles"]):
            M.smart_uv(o, **UV)
            m012._uv_unfold(o)
    lg["bowties"] = M.fix_bowties(o)
    return o, lg


def build(render=True, parts=True):
    import time
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn, "part", 1000)
    info_parts = {k: list(v) for k, v in INFO.items()}
    h, log["hero"] = _make(HERO, hero, "hero", 4000)
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    _restyle()
    M.display(NUM, order, TITLE)
    dropped = _drop_unused(order)
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    out = {"audit": [{k: M.audit(o)[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges",
                                                     "boundary_edges", "nonmanifold_verts", "wire_edges", "loose_verts",
                                                     "zero_area_faces", "normals", "ngons", "dup_verts")}
                     for o in order],
           "thin": {o.name: m012._thin(o, POLISH_LIM) for o in order}, "log": log, "dropped": dropped,
           "problems": K.check(order),
           "inverted": {o.name: inverted(o) for o in order},
           "self_hits": {o.name: _self_hits(o) for o in order},
           "nodule_facets": list(info_parts.get("facets", [])) + list(INFO.get("facets", [])),
           "uv": {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped",
                                                                            "min_gap", "density",
                                                                            "stretch_conformal_p95")}
                  for o in order}}
    out["problems"] = list(out["problems"])
    out["problems"] += [f"{a_['name']}: {a_['shells']} shells" for a_ in out["audit"] if a_["shells"] != 1]
    out["problems"] += [f"{a_['name']}: {a_['nonmanifold_edges']} non-manifold / {a_['boundary_edges']} boundary"
                        for a_ in out["audit"] if a_["nonmanifold_edges"] or a_["boundary_edges"]]
    out["problems"] += [f"{a_['name']}: {a_['nonmanifold_verts']} non-manifold (bowtie) verts" for a_ in out["audit"]
                        if a_["nonmanifold_verts"]]
    out["problems"] += [f"{n}: {c} inverted faces" for n, c in out["inverted"].items() if c]
    out["problems"] += [f"{n}: {c} crossing face pairs {w}" for n, (c, w) in out["self_hits"].items() if c]
    out["problems"] += [f"{n}: union left out shells {v['union']['failed']}" for n, v in log.items()
                        if isinstance(v, dict) and v.get("union", {}).get("failed")]
    inv = list(info_parts.get("piece_inverted", [])) + list(INFO.get("piece_inverted", []))
    if any(inv):
        out["problems"].append(f"pieces with inverted faces: {sum(1 for x in inv if x)}")
    for o in order:
        if o.get("kit_role") == "part" and M.audit(o)["tris"] > 1000:
            out["problems"].append(f"{o.name}: over the part budget")
    if M.audit(h)["tris"] > 4000:
        out["problems"].append(f"{h.name}: over the hero budget")
    out["build_s"] = round(time.time() - t0, 1)
    if render:
        out["views"] = render_views(order)
    out["total_s"] = round(time.time() - t0, 1)
    return out


def _drop_unused(objs):
    names = {o.name for o in objs}
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.split(".")[0] in names]
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m028_")]
    out = {"meshes": len(meshes), "materials": len(mats)}
    for m in meshes:
        bpy.data.meshes.remove(m)
    for m in mats:
        bpy.data.materials.remove(m)
    for o in objs:
        if o.data.name != o.name and o.name not in bpy.data.meshes:
            o.data.name = o.name
    return out


# ---- renders -------------------------------------------------------------------------------------------------------------
# the sheet's comparison cameras (decision 9): floor hidden, long lens
SHEET_VIEWS = {"f34_sheet": (0, 12), "front_sheet": (0, 12), "rear_sheet": (180, 12), "side_sheet": (90, 12),
               "r34_sheet": (180, 14), "top_sheet": (0, 89), "top_tilt_sheet": (0, 70)}
SHEET_LENS = 3.0


def _long_lens(kit):
    orig = kit["render_group"]

    def rg(group, path, azimuth=-22, elevation=20):
        cam = bpy.data.objects["FB_Cam"].data
        lens = cam.lens
        ground = bpy.data.objects.get("FB_Ground")
        hid = ground.hide_render if ground else None
        if "_sheet" in path:
            cam.lens = lens * SHEET_LENS
            if ground:
                ground.hide_render = True
        try:
            return orig(group, path, azimuth, elevation)
        finally:
            cam.lens = lens
            if ground:
                ground.hide_render = hid
    return orig, rg


# the exploded shot as the sheet lays it out (studs from the stem's foot; x right, z up; 80 px per stud on the sheet):
# the stem at the centre, the base below, two leaves out left and right, two nodules high left and right, two smaller
# loose nodules low left and right. (part, location, rotation XYZ (deg), scale)
EXPL = (("FrostBushStem", (0.0, 0.0, 0.0), (0, 0, 0), 1.0),
        ("FrostBushBase", (0.0, 0.0, -2.1), (0, 0, 0), 1.0),
        ("FrostBushLeaf", (-1.3, 0.0, 1.5), (0, 170, 0), 1.0),
        ("FrostBushLeaf", (1.55, 0.0, 1.15), (0, -28, 0), 0.9),
        ("FrostBushIceNodule", (-1.85, 0.0, 2.15), (0, -18, 0), 0.85),
        ("FrostBushIceNodule", (2.3, 0.0, 2.05), (0, 22, 0), 0.8),
        ("FrostBushIceNodule", (-2.6, 0.0, -0.3), (0, -65, 0), 0.6),
        ("FrostBushIceNodule", (2.2, 0.0, -0.45), (0, 55, 0), 0.55))


def render_views(objs):
    h = objs[0]
    by = {o.name: o for o in objs}
    shown = []
    saved = M.explode(objs[1:], {})
    try:
        if len(objs) > 1:
            base = Vector((h.location.x + 40, h.location.y, 0.0))
            for k, (part, loc, rot, sc) in enumerate(EXPL):
                c = bpy.data.objects.new(f"_m028_expl_{k}", by[part].data)
                by[part].users_collection[0].objects.link(c)
                r = (Matrix.Rotation(math.radians(rot[1]), 4, "Y") @ Matrix.Rotation(math.radians(rot[0]), 4, "X")
                     @ Matrix.Rotation(math.radians(rot[2]), 4, "Z"))
                c.matrix_world = Matrix.Translation(base + Vector(loc)) @ r @ Matrix.Scale(sc, 4)
                shown.append(c)
            bpy.context.view_layer.update()
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        if shown:
            extra["exploded"] = (shown, -12, 12)
        for o in objs[1:]:
            extra["part_" + o.name.replace("FrostBush", "").lower()] = ([o], -20, 15)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            return M.views(NUM, [h], extra=extra)
        finally:
            kit["render_group"] = orig
    finally:
        for c in shown:
            bpy.data.objects.remove(c, do_unlink=True)
        M.restore(saved)
        M.display(NUM, objs, TITLE)


# ---- measuring (the study's masks, cls3 in m028_study/m.py, numpy) -----------------------------------------------------
REF_VIEWS = {"f34": (19, 85, 518, 538), "r34": (522, 85, 1005, 538), "front": (19, 542, 305, 799),
             "side": (309, 542, 518, 799), "rear": (522, 542, 782, 799), "top": (786, 542, 1005, 799)}
REF_LABELS = [(19, 85, 260, 120), (522, 85, 750, 120), (19, 542, 110, 580), (309, 542, 380, 580),
              (522, 542, 600, 580), (786, 542, 850, 580)]
OUR_VIEWS = {"f34": "f34_sheet", "r34": "r34_sheet", "front": "front_sheet", "side": "side_sheet",
             "rear": "rear_sheet", "top": "top_tilt_sheet"}
CLASSES = ("L", "I", "S", "W", "R")


def _hsv(a):
    a = a / 255.0
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-9), 0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    dd = np.maximum(d, 1e-9)
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60
    return np.where(d == 0, 0, h), s, mx


def _label(mask):
    """4-connected components by max-label propagation. Returns (labels, ids)."""
    H, W = mask.shape
    lab = np.where(mask, np.arange(1, H * W + 1).reshape(H, W), 0)
    for _ in range(4000):
        m = lab.copy()
        m[1:] = np.maximum(m[1:], lab[:-1])
        m[:-1] = np.maximum(m[:-1], lab[1:])
        m[:, 1:] = np.maximum(m[:, 1:], lab[:, :-1])
        m[:, :-1] = np.maximum(m[:, :-1], lab[:, 1:])
        m = np.where(mask, m, 0)
        if np.array_equal(m, lab):
            break
        lab = m
    return lab, [i for i in np.unique(lab) if i]


def classes(px, paper):
    """px (h, w, 3) sRGB 0-255 top-down -> {L, I, S, W, R} masks (cls3 of the study)."""
    h, s, v = _hsv(px)
    bg = np.abs(px - np.array(paper)).max(-1) <= 14
    cool = (px[..., 2] - px[..., 0]) >= 6
    blue = (~bg) & cool & (h >= 185) & (h <= 245) & (v >= 0.45)
    S = blue & (s < 0.20) & (v >= 0.70)
    G = blue & (s >= 0.40)
    lab, ids = _label(G)
    L = np.zeros_like(G)
    for i in ids:
        m = lab == i
        if m.sum() >= 60 and np.median(s[m]) >= 0.555 and np.median(v[m]) <= 0.80:
            L |= m
    I = blue & ~L & ~S
    BR = (~bg) & ~blue & ((h < 48) | (h >= 330)) & (s >= 0.14) & (v < 0.86)
    lab, ids = _label(BR)
    if ids:
        cnt = [(lab == i).sum() for i in ids]
        W = lab == ids[int(np.argmax(cnt))]
    else:
        W = np.zeros_like(BR)
    return {"L": L, "I": I, "S": S, "W": W, "R": BR & ~W}


def _load(path, box=None, labels=()):
    px = K.NS["KIT"]["load_px"](path)[::-1, :, :3] * 255.0
    px = np.clip(px, 0, 255)
    for x0, y0, x1, y1 in labels:
        px[y0:y1, x0:x1] = np.median(px[y1:y1 + 3, x0:x1].reshape(-1, 3), 0)
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1]
    return px


def _paper(px):
    c = np.concatenate([px[2:6, 2:-2].reshape(-1, 3), px[-6:-2, 2:-2].reshape(-1, 3)])
    return tuple(np.median(c, 0))


def _runs(row, W, x0, minw=2):
    seg, start = [], None
    for x in range(len(row) + 1):
        on = x < len(row) and row[x]
        if on and start is None:
            start = x
        if not on and start is not None:
            if x - start >= minw:
                seg.append((round((start - x0) / W, 2), round((x - x0) / W, 2)))
            start = None
    return seg


def stats(px):
    c = classes(px, _paper(px))
    obj = c["L"] | c["I"] | c["S"] | c["W"] | c["R"]
    cols = np.nonzero(obj.sum(0) >= 2)[0]
    rows = np.nonzero(obj.sum(1) >= 2)[0]
    bx0, bx1, by0, by1 = cols.min(), cols.max(), rows.min(), rows.max()
    W, H = bx1 - bx0, by1 - by0
    n = max(1, obj[by0:by1 + 1, bx0:bx1 + 1].sum())
    out = {"wh": round(W / H, 3)}
    out.update({k: round(c[k][by0:by1 + 1, bx0:bx1 + 1].sum() / n, 3) for k in CLASSES})
    out["IS"] = round(out["I"] + out["S"], 3)
    top = []
    for i in range(21):
        x = bx0 + int(i * W / 20)
        ys = np.nonzero(obj[:, max(0, x - 1):x + 2].any(1))[0]
        top.append(round((by1 - ys.min()) / H, 2) if len(ys) else None)
    out["top"] = top
    wid = []
    for i in range(11):
        y = by1 - int(i * H / 10)
        xs = np.nonzero(obj[min(y, obj.shape[0] - 1)])[0]
        wid.append((round((xs.max() - xs.min()) / W, 2), round((xs.min() - bx0) / W, 2)) if len(xs) else None)
    out["width"] = wid
    runs = []
    for hh_ in (0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95):
        r = by1 - int(hh_ * H)
        row = c["W"][max(0, r - 1):r + 2].sum(0) >= 2
        runs.append((hh_, _runs(row, W, bx0)))
    out["wood_runs"] = runs
    hexs = lambda q: "#" + "".join(f"{int(round(x)):02X}" for x in q)
    for k in CLASSES:
        sel = px[c[k]]
        if len(sel) >= 8:
            out[k + "med"] = hexs(np.median(sel, axis=0))
    canopy = np.zeros_like(obj)
    canopy[:by1 - int(0.45 * H)] = True
    sel = px[(c["I"] | c["S"]) & canopy]
    if len(sel) > 20:
        out["ICEcanopy_med"] = hexs(np.median(sel, axis=0))
    sel = px[c["S"] & ~canopy]
    if len(sel) > 20:
        out["SNOWbase_med"] = hexs(np.median(sel, axis=0))
    lab, ids = _label(c["L"])
    out["leaf_comps"] = sum(1 for i in ids if (lab == i).sum() >= 0.004 * n)
    return out


def measure(views=("f34", "front", "side", "rear", "r34", "top")):
    """Sheet against our renders, per view (the study's masks on both; paper from each image's top/bottom rows)."""
    ref = M.ref(NUM)
    out = {}
    for vname in views:
        a = stats(_load(ref, REF_VIEWS[vname], REF_LABELS))
        b = stats(_load(f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[vname]}.png"))
        out[vname] = {"sheet": a, "ours": b}
    return out


def _fit(px, h):
    ys = (np.arange(h) * px.shape[0] / h).astype(int)
    w = max(1, int(round(px.shape[1] * h / px.shape[0])))
    xs = (np.arange(w) * px.shape[1] / w).astype(int)
    return px[ys][:, xs]


def _crop_obj(px, pad=0.06):
    """Crop a bottom-up RGBA render / sheet cell to its object silhouette (+pad)."""
    top = np.clip(px[::-1, :, :3] * 255.0, 0, 255)
    c = classes(top, _paper(top))
    obj = c["L"] | c["I"] | c["S"] | c["W"] | c["R"]
    ys, xs = np.nonzero(obj)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    p = int(pad * max(y1 - y0, x1 - x0))
    H, W = obj.shape
    y0, y1, x0, x1 = max(0, y0 - p), min(H, y1 + p), max(0, x0 - p), min(W, x1 + p)
    return px[H - y1:H - y0, x0:x1]


def compare(views=("f34", "front", "side", "rear", "r34", "top"), h=360):
    """Sheet cell (left) beside our long-lens render (right), each cropped to the silhouette and scaled to the same
    height; one row per view -> M028_sheet_compare.png."""
    kit = K.NS["KIT"]
    ref = kit["load_px"](M.ref(NUM))
    H = ref.shape[0]
    rows = []
    for v in views:
        x0, y0, x1, y1 = REF_VIEWS[v]
        cell = ref[H - y1:H - y0, x0:x1].copy()
        for lx0, ly0, lx1, ly1 in REF_LABELS:     # blank the view label (sheet px -> this cell, bottom-up)
            if lx0 >= x0 and ly0 >= y0 and lx1 <= x1 and ly1 <= y1:
                cy0, cy1 = (y1 - ly1), (y1 - ly0)
                cell[cy0:cy1, lx0 - x0:lx1 - x0] = np.median(cell[cy0 - 3:cy0, lx0 - x0:lx1 - x0].reshape(-1, 4), 0)
        a = _fit(_crop_obj(cell), h)
        b = _fit(_crop_obj(kit["load_px"](f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[v]}.png")), h)
        gap = np.ones((h, 20, 4), np.float32)
        rows.append(np.concatenate([a, gap, b], axis=1))
    w = max(r.shape[1] for r in rows)
    rows = [np.concatenate([r, np.ones((h, w - r.shape[1], 4), np.float32)], axis=1) if r.shape[1] < w else r
            for r in rows]
    out = f"{M.MODEL_RENDERS}/{M.code(NUM)}/{M.code(NUM)}_sheet_compare.png"
    kit["save_px"](kit["vstack"](rows), out)
    return out
