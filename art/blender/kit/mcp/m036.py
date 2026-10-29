"""036 Rock Cluster (references/036.png): a group of separate, big-faceted warm grey-pink rocks: A, a tall faceted
pillar-egg at the back right of centre with a lobed lime moss cap on its sloping crown; B, a squat upright block at the
front left with a flat lobed moss mat on its broad crown and a leaf sprig at its back right; C, a low faceted dome at
the front right; two more bare domes at the back (G, H: C's mesh reused); six small rocks and a pebble round the foot;
thirteen chunky round-leaf clover clusters (dense leaf mounds, seven white five-petal flowers) in the joints and round
the foot.

    import importlib, kit_models, m036; importlib.reload(kit_models); importlib.reload(m036); m036.build()

Build frame: studs, front -Y, +X right, ground z 0; every object ends with its origin at its bbox bottom centre.
W01 owns RockCluster*, so the names are MossyRockCluster* (spec 8):
- MossyRockClusterRockA (rock_a_part): rock A with its moss cap and olive smear.
- MossyRockClusterRockB (rock_b_part): rock B with its moss mat and sprig.
- MossyRockClusterRockC (rock_c_part): rock C with the exploded view's small moss tuft.
- MossyRockClusterSmallRock (small_rock_part): small rock D with its moss smear.
- MossyRockClusterFoliage (foliage_part): the plain clover cluster.
- MossyRockClusterFlowerCluster (flower_part): the clover cluster with a flower (and a bud at its foot).

The hero (MossyRockCluster, decision 6) is one object of closed shells: each rock (a convex hull of jittered point
rings, flattened by a few cut planes into big deliberate facets, with a flat floor), each moss cap, and each leaf,
petal and flower centre. No booleans. Colour (stage 4) is painted by position inside the builders, per flat facet.
Stages 5-6: nothing (decision 9: the sheet shows no glow, light or effect). See M036_spec.md.
"""
import math
import random
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M
import m011
import m012
import m033

NUM, TITLE, SHEET = 36, "Rock Cluster", "M036"
OFF = "m036_offset"
PFX = "_m036_"
HERO = "MossyRockCluster"
A_P, B_P, C_P = "MossyRockClusterRockA", "MossyRockClusterRockB", "MossyRockClusterRockC"
SMALL_P, FOL_P, FLW_P = "MossyRockClusterSmallRock", "MossyRockClusterFoliage", "MossyRockClusterFlowerCluster"

ROCK, ROCK_SHADOW, ROCK_LIGHT, SMEAR = "m036_rock", "m036_rock_shadow", "m036_rock_light", "m036_moss_smear"
MOSS, MOSS_SUN, MOSS_DEEP = "m036_moss", "m036_moss_sun", "m036_moss_deep"
LEAF, LEAF_YOUNG, LEAF_DEEP = "m036_leaf", "m036_leaf_young", "m036_leaf_deep"
PETAL, POLLEN = "m036_petal", "m036_pollen"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low specular). Stage 4 (M036_spec.md "Stage 4") writes the calibrated values here.
PALETTE = {
    ROCK: ("#AC9B94", 0.9, False),
    ROCK_SHADOW: ("#99897F", 0.9, False),
    ROCK_LIGHT: ("#CDBCB2", 0.9, False),
    SMEAR: ("#5E6737", 0.95, True),
    MOSS: ("#8E9C08", 0.9, True),
    MOSS_SUN: ("#A9B208", 0.9, True),
    MOSS_DEEP: ("#627606", 0.9, True),
    LEAF: ("#709601", 0.85, True),
    LEAF_YOUNG: ("#879904", 0.85, True),
    LEAF_DEEP: ("#447401", 0.85, True),
    PETAL: ("#D6D3CA", 0.7, False),
    POLLEN: ("#B1AC01", 0.7, False),
}
# calibration targets (spec 5.4: rendered medians of unshadowed regions: the exploded parts). Kinds for K.sample: the
# warm rock is sat ~0.2 (the stone filter drops > 0.18) so "all"; the lime moss and the olive smear have G - R < 8, so
# the green filter drops them: "vivid".
TARGETS = {ROCK: ((0xC0, 0xA5, 0x98), "all"), ROCK_SHADOW: ((0xA9, 0x96, 0x91), "all"),
           ROCK_LIGHT: ((0xD8, 0xBE, 0xAD), "all"), SMEAR: ((0x6F, 0x76, 0x37), "vivid"),
           MOSS: ((0xB3, 0xBA, 0x1B), "vivid"), MOSS_SUN: ((0xDA, 0xD6, 0x20), "vivid"),
           MOSS_DEEP: ((0x74, 0x8A, 0x13), "green"), LEAF: ((0x88, 0xB2, 0x05), "green"),
           LEAF_YOUNG: ((0xC0, 0xD5, 0x0E), "green"), LEAF_DEEP: ((0x4E, 0x83, 0x02), "green"),
           PETAL: ((0xF6, 0xF4, 0xEC), "all"), POLLEN: ((0xE0, 0xD2, 0x1F), "vivid")}
SPEC = {}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    _spec()


def _spec():
    for m in bpy.data.materials:
        if not m.name.startswith("FB_m036_") or not m.node_tree:
            continue
        key = m.name[3:]
        lvl = next((v for p, v in SPEC.items() if key.startswith(p)), None)
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if lvl is not None and bsdf and "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = lvl


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome. Returns {key: (hex, rendered)}."""
    keys = keys or list(TARGETS)
    for k in keys:
        K.fk().material(k)
    try:
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


# ---- small helpers -----------------------------------------------------------------------------------------------------
_faces = m033._faces
_place = m033._place


def _q(t, steps=3):
    t = max(0.0, min(1.0, t))
    return round(t * steps) / steps


def _hull_bm(bm, pts):
    """Convex hull of pts into bm as one closed triangulated shell; returns its verts."""
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    for v in vs:
        if v.is_valid and not v.link_faces:
            bm.verts.remove(v)
    vs = [v for v in vs if v.is_valid]
    fs = _faces(vs)
    bmesh.ops.triangulate(bm, faces=[f for f in fs if len(f.verts) > 3], quad_method="BEAUTY", ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    return vs


def _regions(faces, ang=2.0):
    """Flat facets: neighbouring triangles whose normals are within ang degrees, merged. Returns a list of lists."""
    fset = set(faces)
    seen = {}
    regs = []
    lim = math.radians(ang)
    for f in faces:
        if f in seen:
            continue
        r = len(regs)
        seen[f] = r
        stack, reg = [f], []
        while stack:
            g = stack.pop()
            reg.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h in fset and h not in seen and h.normal.angle(f.normal, 1.0) <= lim:
                        seen[h] = r
                        stack.append(h)
        regs.append(reg)
    return regs


def _centroid(reg):
    a = sum(f.calc_area() for f in reg)
    return sum((f.calc_center_median() * f.calc_area() for f in reg), Vector()) / max(a, 1e-9)


def _tint_regions(a, regs, amp, scale, seed, tint=1.0):
    """Broad Tint patches read at each flat facet's centroid (one tone per facet, never per-triangle confetti)."""
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for reg in regs:
        k = (1.0 + amp * 1.6 * noise.noise(_centroid(reg) * scale + off)) * tint
        for f in reg:
            for l in f.loops:
                t = l[a.tint_layer][0] * k
                l[a.tint_layer] = (t, t, t, 1.0)


def _mottle(a, faces, amp, scale, seed, tint=1.0):
    m033._mottle(a, faces, amp, scale, seed, tint)


# ---- rocks (spec 1.4, 2.1, 2.2) -----------------------------------------------------------------------------------------
# Point clouds: rings (height fraction, radius fraction, points) from the floor up, jittered, then flattened by cut
# planes (unit normal, distance from (0, 0, zc * H), zc): every point beyond a plane is moved onto it, so the hull gets
# one big flat facet there (A's front shield and sloping crown, B's steep left flank and tilted crown, the domes'
# crowns). The cloud is then yawed and scaled to the rock's exact world size (an affine map keeps the hull).
CLOUDS = {
    "A": dict(rings=((0.0, 0.80, 10), (0.13, 0.93, 6), (0.34, 1.0, 7), (0.58, 0.95, 6), (0.79, 0.80, 6),
                     (0.93, 0.60, 5), (1.0, 0.46, 4)), jit=0.09,
              lean=(-0.04, -0.03), seed=36101,
              cuts=(((-0.08, -0.08, 1.0), 0.0, 0.96),        # crown, sloping down to the front-left (fix 1: -0.10)
                    ((0.10, -1.0, 0.10), 0.80, 0.42),        # the lit front shield
                    ((-1.0, 0.25, 0.08), 0.86, 0.40),        # left flank (shaded)
                    ((0.75, 0.70, 0.0), 0.86, 0.35))),       # back right
    "B": dict(rings=((0.0, 0.76, 10), (0.15, 0.88, 6), (0.38, 0.97, 7), (0.60, 1.0, 6), (0.82, 0.88, 5),
                     (1.0, 0.64, 4)), jit=0.09,
              lean=(0.04, 0.02), seed=36102,
              cuts=(((0.0, -0.18, 1.0), 0.0, 0.93),         # broad crown tilted to the front
                    ((-1.0, -0.08, 0.0), 0.86, 0.5),         # near-vertical left flank
                    ((-0.25, -1.0, 0.35), 0.86, 0.45),       # front, leaning back
                    ((0.85, 0.55, 0.0), 0.84, 0.5))),        # back right, against A
    "C": dict(rings=((0.0, 0.82, 10), (0.20, 0.97, 6), (0.44, 1.0, 7), (0.68, 0.86, 6), (0.87, 0.60, 4),
                     (1.0, 0.32, 3)), jit=0.10,
              lean=(0.0, 0.0), seed=36103,
              cuts=(((0.10, -0.12, 1.0), 0.0, 0.94),        # crown polygon
                    ((0.55, -0.80, 0.30), 0.82, 0.30),       # front right
                    ((-0.65, 0.75, 0.10), 0.84, 0.30),       # back left, against A
                    ((-0.85, -0.45, 0.35), 0.80, 0.30),      # front left
                    ((0.90, 0.30, 0.25), 0.84, 0.35))),      # right
    "D": dict(rings=((0.0, 0.82, 6), (0.35, 1.0, 6), (0.75, 0.75, 5), (1.0, 0.35, 3)), jit=0.12, lean=(0, 0),
              seed=36104, cuts=(((0.3, -1.0, 0.4), 0.80, 0.4), ((-0.9, 0.3, 0.6), 0.78, 0.4))),
    "E": dict(rings=((0.0, 0.82, 6), (0.35, 1.0, 6), (0.75, 0.75, 5), (1.0, 0.40, 3)), jit=0.12, lean=(0, 0),
              seed=36105, cuts=(((0.0, 0.0, 1.0), 0.0, 0.92), ((0.4, -1.0, 0.5), 0.78, 0.4))),
    "F": dict(rings=((0.0, 0.82, 6), (0.35, 1.0, 6), (0.75, 0.75, 5), (1.0, 0.35, 3)), jit=0.12, lean=(0, 0),
              seed=36106, cuts=(((-0.5, -1.0, 0.3), 0.80, 0.4), ((0.8, 0.6, 0.7), 0.74, 0.4))),
    "P": dict(rings=((0.0, 0.9, 4), (0.48, 1.0, 4), (1.0, 0.42, 2)), jit=0.12, lean=(0, 0), seed=36107, cuts=()),
}
# name -> cloud, centre (x, y), world size (W, D, H), yaw (deg)
ROCKS = {
    "A": ("A", (1.4, 1.2), (5.0, 5.4, 7.6), 0.0),      # fix round 1: 7.3 -> 7.6 (the flat cap, H 8.0 - 0.3)
    "B": ("B", (-2.2, -1.8), (4.8, 4.4, 4.7), 0.0),
    "C": ("C", (2.8, -2.75), (4.5, 4.8, 3.2), 0.0),
    "G": ("C", (3.4, 3.1), (4.2, 4.2, 3.35), 150.0),
    "H": ("C", (-1.8, 3.4), (4.7, 3.8, 2.8), 70.0),
    "D": ("D", (-5.5, -1.8), (1.0, 0.9, 0.8), 0.0),
    "E": ("E", (-0.5, -4.5), (1.7, 1.4, 1.0), 0.0),
    "F": ("F", (5.5, -0.6), (1.4, 1.3, 1.2), 0.0),
    "D2": ("D", (-4.6, 3.6), (1.0, 0.9, 0.8), 120.0),
    "E2": ("E", (0.8, 4.5), (1.4, 1.2, 0.8), 200.0),
    "F2": ("F", (5.2, 4.6), (1.1, 1.0, 0.9), 60.0),
    "P": ("P", (6.1, -1.3), (0.5, 0.45, 0.3), 30.0),
}
BIG = ("A", "B", "C", "G", "H")
SMALL = ("D", "E", "F", "D2", "E2", "F2", "P")
MAX_PEN = 0.15            # rocks may overlap by up to this (spec 6)
PEN_LIMIT = {"G": 1.3}      # G tucks in behind A's back-right flank (the rear views), the joint hidden
MAX_PEN_BIG = 0.60        # ... except two main rocks, whose joints are hidden (the sheet's rocks nestle into A's foot)
ROCK_INFO = {}


def _cloud(name):
    cp = CLOUDS[name]
    rng = random.Random(cp["seed"])
    pts = m033._ring_pts(rng, cp["rings"], 1.0, 1.0, 1.0, cp["jit"], cp["lean"], ang_jit=0.30)
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


def _planes(pts):
    """Outward face planes (n, d) of the convex hull of pts (a scratch bmesh)."""
    bm = bmesh.new()
    vs = _hull_bm(bm, pts)
    out = [(f.normal.copy(), f.normal.dot(f.calc_center_median())) for f in _faces(vs)]
    hv = [v.co.copy() for v in vs]
    bm.free()
    return out, hv


def _pen(pa, pb):
    """Penetration of two convex hulls (max depth of either's verts inside the other)."""
    best = 0.0
    for (planes, _), (_, verts) in ((pa, pb), (pb, pa)):
        for v in verts:
            d = min(dd - n.dot(v) for n, dd in planes)
            best = max(best, d)
    return best


def layout():
    """Rock centres after separation: big rocks pushed horizontally away from those placed before them (A fixed)
    until they overlap by at most MAX_PEN, then the small rocks pushed off everything. Returns {name: (x, y)}."""
    centres = {k: ROCKS[k][1] for k in ROCKS}
    placed = {}
    moves = {}
    for name in BIG + SMALL:
        c = Vector((*centres[name], 0.0))
        for _ in range(40):
            hull = _planes(_rock_pts(name, (c.x, c.y)))
            worst, push = 0.0, None
            for other, oh in placed.items():
                p = _pen(hull, oh)
                if p > worst:
                    worst = p
                    oc = Vector((*centres[other], 0.0))
                    push = (c - oc).normalized()
            lim = PEN_LIMIT.get(name, MAX_PEN_BIG if name in BIG else MAX_PEN)
            if worst <= lim or push is None:
                break
            c += push * (worst - lim + 0.04) * 0.6
        centres[name] = (round(c.x, 3), round(c.y, 3))
        placed[name] = _planes(_rock_pts(name, centres[name]))
        moves[name] = round((Vector(centres[name]) - Vector(ROCKS[name][1])).length, 2)
    LAYOUT["centres"], LAYOUT["moves"] = centres, moves
    return centres


LAYOUT = {}
# Rock colour (spec 5.3, 5.5): per flat facet, by the facet centroid's position only. Broad noise patches ->
# rock_shadow (mixed up to 40 %, ~25-30 % of the facets); patches on each rock's upper third -> rock_light (mixed up to
# 50 %); then Tint per facet. The floor stays plain rock.
SHADOW = dict(scale=0.30, level=0.12, width=0.30, mix=0.50, seed=36111)   # fix round 1: mix 0.40
LIGHT = dict(scale=0.34, level=0.02, width=0.30, mix=0.50, h0=0.60, seed=36112)
ROCK_MOTTLE = dict(amp=0.05, scale=0.35, seed=36121)


def _paint_rock(a, vs, seed, H):
    fs = _faces(vs)
    floor = [f for f in fs if f.normal.z < -0.99 and f.calc_center_median().z < 1e-3]
    side = [f for f in fs if f not in set(floor)]
    regs = _regions(side)
    ns = K.noise_field(SHADOW["scale"], SHADOW["seed"] + seed)
    nl = K.noise_field(LIGHT["scale"], LIGHT["seed"] + seed)
    for reg in regs:
        c = _centroid(reg)
        ts = _q((ns(c) - SHADOW["level"]) / SHADOW["width"])
        # light patches on a big rock's upper part only; none on the small rocks (on a lump under 2 studs "upper"
        # is the same faces as "facing up", which K.check rightly reads as baked shading)
        tl = _q((nl(c) - LIGHT["level"]) / LIGHT["width"]) if (H >= 2.0 and c.z > LIGHT["h0"] * H) else 0.0
        if ts > 0 and ts >= tl:
            key = K.mix_key(ROCK, ROCK_SHADOW, round(ts * SHADOW["mix"], 2))
        elif tl > 0:
            key = K.mix_key(ROCK, ROCK_LIGHT, round(tl * LIGHT["mix"], 2))
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
    """One rock shell: hull, painted, its shape metrics recorded (before any refine). Returns its verts."""
    c = centre if centre is not None else LAYOUT.get("centres", {}).get(name, ROCKS[name][1])
    vs = _hull_bm(a.bm, _rock_pts(name, c))
    a._finish(vs, ROCK, tint=1.0)
    H = ROCKS[name][2][2]
    _paint_rock(a, vs, sum(map(ord, name)), H)
    ROCK_INFO[name] = dict(centre=[round(x, 2) for x in c], **rock_metrics(_faces(vs), name))
    return vs


# Olive moss smears (spec 3.6, 5.3): A's upper-left face (a patch about 0.5 x 0.8, offsets from A's centre as
# fractions of its W, D, H) and D's left foot. The faces in reach are refined so the patch has its own lobed edge.
SMEARS = {"A": dict(at=(-0.40, -0.18, 0.74), r=(0.32, 0.32, 0.48), reach=1.3, cuts=2, mix=(0.55, 0.9), seed=36131),
          "D": dict(at=(-0.48, -0.10, 0.12), r=(0.22, 0.32, 0.22), reach=0.45, cuts=1, mix=(0.35, 0.6), seed=36132)}


def _refine(bm, faces, cuts):
    """K.refine without its face-tag layer (adding a layer makes every Python vertex reference in the bmesh stale):
    the faces' edges split `cuts` times, every touched face triangulated (coplanar pieces, so the facets and the
    silhouette don't change). Returns the verts of the touched faces."""
    edges = list({e for f in faces for e in f.edges})
    res = bmesh.ops.subdivide_edges(bm, edges=edges, cuts=cuts, use_grid_fill=True)
    new_v = [g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)]
    fs = list({f for v in new_v for f in v.link_faces})
    bmesh.ops.triangulate(bm, faces=[f for f in fs if f.is_valid and len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    return list({v for x in new_v for f in x.link_faces for v in f.verts})


def _smear(a, vs, name, centre):
    sp = SMEARS[name]
    W, D, H = ROCKS[name][2]
    p = Vector((centre[0] + sp["at"][0] * W, centre[1] + sp["at"][1] * D, sp["at"][2] * H))
    near = [f for f in _faces(vs) if (f.calc_center_median() - p).length < sp["reach"] and f.normal.z > -0.9]
    rv = list({v for f in near for v in f.verts})
    if near and sp["cuts"]:
        rv = _refine(a.bm, near, sp["cuts"])
    rng = random.Random(sp["seed"])
    off = Vector((rng.uniform(0, 50), rng.uniform(0, 50), rng.uniform(0, 50)))
    n = 0
    for f in _faces(rv):
        c = f.calc_center_median()
        d = Vector(((c.x - p.x) / sp["r"][0], (c.y - p.y) / sp["r"][1], (c.z - p.z) / sp["r"][2])).length
        d += 0.25 * noise.noise(c * 2.2 + off)
        t = 2 if d < 0.75 else 1 if d < 1.05 else 0
        if t:
            f.material_index = a._mi(K.mix_key(ROCK, SMEAR, sp["mix"][t - 1]))
            n += 1
    ROCK_INFO.setdefault(name, {})["smear_faces"] = n


# ---- moss caps (spec 1.4, 2.3): lobed rosette mats conformed to the crowns ----------------------------------------------
# A cap is a clump of a few overlapping lobed mats (each its own closed shell), so its outline is irregular and
# oak-leaf lobed and it has real depth. name -> rock, sink, [(offset of the mat's centre from the rock's centre
# (studs), r, h, lobes, squash (x, y), yaw, seed), ...]
CAPS = {"A": ("A", 0.05, (((0.28, 0.38), 1.08, 0.45, 9, (1.0, 0.88), 15.0, 36201),     # fix round 1: a flat mat
                          ((0.62, 0.78), 0.50, 0.36, 5, (1.0, 0.9), 70.0, 36202))),   # (0.88 thick), on the high side
        "B": ("B", 0.05, (((-0.70, -0.55), 1.22, 0.48, 8, (1.0, 0.70), -8.0, 36211),
                          ((0.15, -0.20), 0.50, 0.34, 5, (1.0, 0.9), 40.0, 36212))),
        "Ctuft": ("C", 0.05, (((0.0, 0.0), 0.55, 0.40, 6, (1.0, 1.0), 0.0, 36221),))}
ROS_BAND = 0.14
ROS_MID = (0.55, 0.60)
ROS_NOTCH_Z = 0.12
ROS_TIP_Z = 1.2         # fix round 1 (0.85): lobe corners nearer the notch tops, a flat lobed mat
ROS_CORNER = 0.22
ROS_DROP = 0.7
CAP_MOTTLE = dict(amp=0.05, scale=0.8, seed=36211)
CAP_SUN = {"B": 0.5}      # fix round 1: B's mat takes half the sun mixes (it read paler and yellower than the sheet)
CAP_INFO = {}


def _rosette(a, r, h, lobes, squash, seed, sun=1.0):
    """One lobed moss mat in its local frame, base at z 0 (m035's rosette): a lobed outline (two corners per lobe and
    a notch between), radial ridges up to a raised centre, a thin rim band and a flat underside fan. Coloured by place
    on the mat: centre sun-yellow, ridges toward it, notch valleys and the rim deep. Returns (verts, parts)."""
    rng = random.Random(seed)
    bm = a.bm
    off = rng.uniform(0, 2 * math.pi)
    step = 2 * math.pi / lobes
    sx, sy = squash
    outline, axes = [], []
    for k in range(lobes):
        th = off + k * step + rng.uniform(-0.07, 0.07) * step
        axes.append(th)
        rl = r * rng.uniform(0.90, 1.06)
        for s_ in (-1, 1):
            outline.append((th + s_ * ROS_CORNER * step * rng.uniform(0.85, 1.15), rl * rng.uniform(0.94, 1.0), "tip"))
        outline.append((th + 0.5 * step + rng.uniform(-0.05, 0.05) * step, r * rng.uniform(0.62, 0.74), "notch"))
    top, bot = [], []
    for th, rr, kind in outline:
        zt = ROS_BAND + (h - ROS_BAND) * ROS_NOTCH_Z if kind == "notch" else ROS_BAND * ROS_TIP_Z * rng.uniform(0.9, 1.1)
        x, y = math.cos(th) * rr * sx, math.sin(th) * rr * sy
        top.append(bm.verts.new((x, y, zt)))
        bot.append(bm.verts.new((x * 0.95, y * 0.95, 0.0)))
    mids = []
    for th in axes:
        mr = r * ROS_MID[0] * rng.uniform(0.92, 1.08)
        mids.append(bm.verts.new((math.cos(th) * mr * sx, math.sin(th) * mr * sy,
                                  ROS_BAND + (h - ROS_BAND) * ROS_MID[1] * rng.uniform(0.92, 1.08))))
    centre = bm.verts.new((rng.uniform(-0.06, 0.06) * r, rng.uniform(-0.06, 0.06) * r, h))
    bc = bm.verts.new((0.0, 0.0, 0.0))
    n = len(top)
    ridge_f, valley_f, cen_f, rim_f, und_f = [], [], [], [], []
    for k in range(lobes):
        c1, c2, nk, nprev = 3 * k, 3 * k + 1, 3 * k + 2, (3 * k - 1) % n
        m0, m1 = mids[k], mids[(k + 1) % lobes]
        cen_f.append(bm.faces.new((centre, m0, m1)))
        valley_f.append(bm.faces.new((m0, top[nprev], top[c1])))
        ridge_f.append(bm.faces.new((m0, top[c1], top[c2])))
        valley_f.append(bm.faces.new((m0, top[c2], top[nk])))
        valley_f.append(bm.faces.new((m0, top[nk], m1)))
    for i in range(n):
        j = (i + 1) % n
        rim_f.append(bm.faces.new((top[i], bot[i], bot[j])))
        rim_f.append(bm.faces.new((top[i], bot[j], top[j])))
        und_f.append(bm.faces.new((bot[j], bot[i], bc)))
    vs = top + bot + mids + [centre, bc]
    bmesh.ops.recalc_face_normals(bm, faces=cen_f + ridge_f + valley_f + rim_f + und_f)
    a._finish(vs, MOSS, tint=1.0)
    sh = [round(rng.choice((0.0, 0.25, 0.5)) * sun, 2) for _ in range(lobes)]
    for f in cen_f:
        f.material_index = a._mi(K.mix_key(MOSS, MOSS_SUN, round(0.5 * sun, 2)))
    for k, f in enumerate(ridge_f):
        f.material_index = a._mi(K.mix_key(MOSS, MOSS_SUN, sh[k]))
    for i, f in enumerate(valley_f):
        k = i // 3
        f.material_index = a._mi(K.mix_key(MOSS, MOSS_SUN, round(sh[k] / 2, 2)) if i % 3 != 2
                                 else K.mix_key(MOSS, MOSS_DEEP, 0.5))
    # the rim band and the hidden underside take their lobe's shade (a darker rim would follow face direction)
    for i, f in enumerate(rim_f):
        f.material_index = a._mi(K.mix_key(MOSS, MOSS_SUN, round(sh[(i // 2) // 3 % lobes] / 2, 2)))
    for f in und_f:
        f.material_index = a._mi(MOSS)
    _mottle(a, cen_f + ridge_f + valley_f + rim_f, CAP_MOTTLE["amp"], CAP_MOTTLE["scale"], CAP_MOTTLE["seed"] + seed)
    return vs, dict(pairs=list(zip(top, bot)), mids=mids, centre=centre, bc=bc)


def _conform_rosette(rp, tree, c, sink):
    """Drop the mat onto the surface under it (m035): each rim corner's top and bottom drop by the same amount, and
    nothing drapes more than ROS_DROP below the seat under the centre (so a lobe hanging over an edge can't fold)."""
    def surf(x, y):
        h = tree.ray_cast(Vector((x, y, 60.0)), Vector((0, 0, -1)), 200)
        return h[0].z if h[0] is not None else None
    zc = surf(c.x, c.y)
    zc = 0.0 if zc is None else zc

    def drop(v):
        z = surf(v.co.x, v.co.y)
        return max((zc if z is None else z) - sink, zc - sink - ROS_DROP)
    for t, b in rp["pairs"]:
        d = drop(t)
        t.co.z += d
        b.co.z += d
    for v in rp["mids"] + [rp["centre"]]:
        v.co.z += drop(v)
    rp["bc"].co.z += zc - sink


def _cap(a, name, rock_vs, rock_centre):
    rk, sink, mats = CAPS[name]
    tree = K.bvh_of(rock_vs)
    allv = []
    for (dx, dy), r, h, lobes, squash, yaw, seed in mats:
        vs, rp = _rosette(a, r, h, lobes, squash, seed, CAP_SUN.get(name, 1.0))
        c = Vector((rock_centre[0] + dx, rock_centre[1] + dy, 0.0))
        _place(a.bm, vs, Matrix.Translation(c) @ Matrix.Rotation(math.radians(yaw), 4, "Z"))
        _conform_rosette(rp, tree, c, sink)
        allv += vs
    zs = [v.co.z for v in allv]
    xs, ys = [v.co.x for v in allv], [v.co.y for v in allv]
    CAP_INFO[name] = dict(z=(round(min(zs), 2), round(max(zs), 2)), faces=len(_faces(allv)),
                          span=(round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2)))
    return allv


# ---- clover clusters and flowers (spec 1.4 Foliage / Flower Cluster, 2.3) -----------------------------------------------
# Fix round 1 (after m035's fix): every cluster is built from dense rounded leaf mounds. Leaves are laid over a dome,
# faces out and up, tips up (_mound), round a deep-green core (_core); a tall cluster is 2-3 overlapping mounds stacked
# up the flank of the rock it leans on (no hidden stem). Every leaf, core and flower is slid into contact with what is
# already placed (the ground, the rocks, the moss and earlier leaves: _Contact), so every shell chains down to the
# ground or a rock. Leaves are round spoons: a short stalk, widest at 0.55 L and a broad blunt rounded tip made of two
# near-equal tip corners (no tip point); a cupped top with a two-point midrib and a flat underside (12 tris).
LEAF_OUT = ((0.55, 1.0), (0.92, 0.74))   # (fraction along, fraction of the half-width) per side, stalk to tip
LEAF_STEM = 0.22         # the stalk end is this fraction of the half-width either side (two stalk corners)
PETAL_OUT = ((0.45, 1.0), (0.88, 0.62))  # rounded petals, no tip point either
LEAF_W = 1.0             # width / length (fix round 1: 0.95 -> 1.0)
LEAF_FOLD, LEAF_CURL, LEAF_THICK, LEAF_CAMBER = 0.16, 0.10, 0.0, 0.24   # flat underside (fix round 1, m035)
LEAF_ROLL = 0.35
CL_TINT = 0.04
LEAF_MOTTLE = dict(amp=0.04, scale=0.9, seed=36411)
FLOWER_R = 0.30          # petal length (flower about 0.6 across)
FLOWER_TILT = 0.55       # the flower's face tips toward its facing direction by this much (rad)
DROP_DEPTH = 0.45        # a leaf this far inside a rock is left out (less is pushed out)
# kind -> leaves, leaf length range (studs), mound radius (fraction of w)
KINDS = {"low": dict(n=9, L=(0.78, 0.94), R=0.38),
         "small": dict(n=6, L=(0.56, 0.68), R=0.36),
         "tall": dict(n=0, L=(0.78, 0.94), R=0.42)}
MOUND_Z = 0.40           # a mound's centre is this fraction of its radius above its seat
MOUND_TH = (4.0, 98.0)   # the dome band the leaves are laid over (deg from the top)
LEAF_UP = 0.65           # a leaf's face is tilted from straight out of the dome this much of the way to straight up
CORE_R = 0.70            # each low or tall mound has a deep-green heart this fraction of its radius (_core)
TALL_MOUNDS = ((1.0, 9), (0.85, 8), (0.72, 6))   # tall cluster mounds bottom up: (radius frac of R, leaves)
HUG_STRETCH = 1.3        # a tall cluster's ground mound is drawn out this much along the rock
UPPER_LEAN = 0.45        # an upper mound sits this far of the way from straight over the ground mound to the flank
UPPER_OFF = 0.70         # an upper mound's centre stands this fraction of its radius off the rock surface
OPEN_ARC = 110.0         # a leaning mound's leaves lie within this many degrees of straight out from the rock
CONTACT = 0.03           # every leaf / core / flower ends within this of the ground, a rock, the moss or a leaf
CLUSTER_INFO = {}
CONTACT_INFO = {}
GROUP_MID = (0.8, 0.6)   # roughly A's foot


def _leaf(a, base, L, key, yaw, pitch, width=None, outline=LEAF_OUT, stem=LEAF_STEM, camber=None, thick=None,
          fold=None, curl=None, roll=0.0, tip_key=None):
    """One chunky round leaf (a closed solid): a spoon outline (a short stalk edge, widest at 0.55 L, a broad blunt
    tip edge 0.74 of the width), its edges cupped up (fold), a raised two-point midrib on top and a flat underside fan (12 tris; a petal
    with a single stalk point 10). base = the stalk end; yaw about Z; pitch = its rise (rad). tip_key colours the outer
    40 % of the top (the sheet's lime tips), by place along the leaf."""
    bm = a.bm
    W = (width or LEAF_W) * L / 2
    cam = (camber if camber is not None else LEAF_CAMBER) * L
    th = (thick if thick is not None else LEAF_THICK) * L
    fo = fold if fold is not None else LEAF_FOLD
    cu = curl if curl is not None else LEAF_CURL
    rot = Matrix.Rotation(yaw, 3, "Z") @ Matrix.Rotation(-pitch, 3, "Y") @ Matrix.Rotation(roll, 3, "X")
    B = Vector(base)

    def put(x, y, z):
        t = x / L
        return bm.verts.new(B + rot @ Vector((x, y, z + fo * abs(y) - cu * L * t * t)))
    ring = ([(0.0, -stem * W)] if stem else [(0.0, 0.0)]) + [(f * L, -h * W) for f, h in outline] + \
        [(f * L, h * W) for f, h in reversed(outline)] + ([(0.0, stem * W)] if stem else [])
    o = [put(x, y, 0.0) for x, y in ring]
    r1 = put(0.30 * L, 0.0, cam)
    r2 = put(0.68 * L, 0.0, cam * 0.8)
    xs = [x for x, _ in ring]
    own = [r1 if x < 0.5 * L else r2 for x in xs]
    n = len(o)
    top = []
    for i in range(n):
        j = (i + 1) % n
        if own[i] is own[j]:
            top.append(bm.faces.new((o[i], o[j], own[i])))
        else:
            top.append(bm.faces.new((o[i], o[j], own[j])))
            top.append(bm.faces.new((o[i], own[j], own[i])))
    if th > 0:
        bk = put(0.5 * L, 0.0, -th)
        faces = top + [bm.faces.new((bk, o[(i + 1) % n], o[i])) for i in range(n)]
        vs = o + [r1, r2, bk]
    else:
        faces = top + [bm.faces.new((o[0], o[i + 1], o[i])) for i in range(1, n - 1)]
        vs = o + [r1, r2]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    a._finish(vs, key, tint=1.0)
    if tip_key:
        mi = a._mi(tip_key)
        for f in top:
            if (f.calc_center_median() - B).length > 0.62 * L:
                f.material_index = mi
    return vs


def _flower(a, loc, r, seed, face=-math.pi / 2):
    """Five broad round white petals round a domed yellow centre, its face tipped toward `face` (an azimuth; the front
    by default). Each petal and the centre are their own closed shells (bases 0.03 out along their own directions, so
    no two coincide; each petal's base sits inside the centre dome, so the flower is one touching group)."""
    rng = random.Random(seed)
    y0 = rng.uniform(0, 2 * math.pi)
    out = []
    for k in range(5):
        yaw = y0 + 2 * math.pi * k / 5
        d = Vector((math.cos(yaw), math.sin(yaw), 0.0))
        pitch = 0.12 - FLOWER_TILT * math.cos(yaw - face)
        b = Vector(loc) + d * 0.03 + Vector((0, 0, 0.004 * k))
        out += _leaf(a, tuple(b), r, PETAL, yaw, pitch, width=1.0, outline=PETAL_OUT, stem=0.0, camber=0.08,
                     thick=0.0, fold=0.06, curl=0.08)
    cvs = a.cyl(r * 0.40, r * 0.24, r * 0.36, sides=6, loc=(loc[0], loc[1], loc[2] - 0.05), mat=POLLEN, tint=1.0)
    caps = [f for f in _faces(cvs) if len(f.verts) > 4]
    if caps:
        bmesh.ops.triangulate(a.bm, faces=caps, quad_method="BEAUTY", ngon_method="BEAUTY")
    out += [v for v in cvs if v.is_valid]
    return out


class _Guard:
    """Keeps a dressing piece out of the rocks: a piece more than `allow` inside is moved out along the surface normal
    at its deepest vert (horizontal part, never down); a leaf more than `drop` inside is left out instead."""

    def __init__(self, tree):
        self.tree = tree
        self.moved = 0

    def depth(self, vs):
        worst, nrm = 0.0, None
        for v in vs:
            loc, n, _, d = self.tree.find_nearest(v.co)
            if loc is None or n is None:
                continue
            if (v.co - loc).dot(n) < 0 and d > worst:
                worst, nrm = d, n
        return worst, nrm

    def push(self, vs, allow, clearance=0.02):
        if self.tree is None:
            return
        for _ in range(5):
            worst, nrm = self.depth(vs)
            if worst <= allow or nrm is None:
                return
            m = Vector((nrm.x, nrm.y, max(0.0, nrm.z)))
            if m.length < 1e-6:
                m = Vector((nrm.x, nrm.y, 0.0))
            m.normalize()
            for v in vs:
                v.co += m * (worst - allow + clearance)
            self.moved += 1


def _lift(vs, floor=0.004):
    z = min(v.co.z for v in vs)
    if z < floor:
        for v in vs:
            v.co.z += floor - z


def _kill(a, vs):
    bmesh.ops.delete(a.bm, geom=[v for v in vs if v.is_valid], context="VERTS")


def _leaf_key(t):
    if t <= 0.0:
        return K.mix_key(LEAF, LEAF_DEEP, 0.4)
    if t < 0.5:
        return K.mix_key(LEAF, LEAF_DEEP, 0.2)
    if t < 0.75:
        return LEAF
    if t < 1.0:
        return K.mix_key(LEAF, LEAF_YOUNG, 0.5)
    return LEAF_YOUNG


def _tip_key(t):
    return None if t < 0.5 else K.mix_key(LEAF, LEAF_YOUNG, 0.5) if t < 1.0 else LEAF_YOUNG


def _mound(rng, centre, R, n, Lr, ct, out=None, th=MOUND_TH, stretch=1.0):
    """One dense rounded mound (m035 fix round 1): n leaves laid over a dome of radius R round `centre`: each leaf's
    middle on the dome, its face pointing out of the dome (tilted LEAF_UP toward straight up) and its tip up toward the
    dome's top, flared out a little, so the clump shows leaf faces from every side and reads as one rounded mass.
    Points by a golden-angle spiral, even in area over the band th; a mound against a rock (`out`) keeps to OPEN_ARC
    either side of straight out and is drawn out `stretch` times along the rock. Returns [(base, L, yaw, pitch, t)]
    with t the colour by height on the dome (low deep, top young), never by facing."""
    plan = []
    off = rng.random()
    oang = math.atan2(out.y, out.x) if out is not None else rng.uniform(0, 2 * math.pi)
    side = Vector((-math.sin(oang), math.cos(oang), 0.0))
    c0, c1 = math.cos(math.radians(th[0])), math.cos(math.radians(th[1]))
    for i in range(n):
        fi = (i + 0.5) / n
        theta = math.acos(c0 + (c1 - c0) * fi)
        u = (i * 0.6180339 + off) % 1.0
        phi = oang + (math.radians(OPEN_ARC) * (2.0 * u - 1.0) if out is not None else 2.0 * math.pi * u)
        phi += rng.uniform(-0.12, 0.12)
        theta += rng.uniform(-0.08, 0.08)
        nrm = Vector((math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)))
        tl = theta * LEAF_UP
        tan = Vector((-math.cos(tl) * math.cos(phi), -math.cos(tl) * math.sin(phi), math.sin(tl)))
        L = rng.uniform(*Lr)
        pitch = tl + rng.uniform(0.0, 0.25)
        p = nrm * R * rng.uniform(0.9, 1.05)
        if stretch != 1.0 and out is not None:
            p += side * (p.dot(side) * (stretch - 1.0))
        base = centre + p - tan * L * 0.45
        t = ct[0] + (ct[1] - ct[0]) * (1.0 - (theta - math.radians(th[0])) / math.radians(th[1] - th[0]))
        plan.append((base, L, phi + math.pi, pitch, max(0.0, min(1.0, t))))
    return plan


def _core(a, centre, r, seed, side=None, stretch=1.0):
    """A mound's hidden heart (12 tris, a closed hexagonal bipyramid in deep leaf green, m035): seen through the gaps
    between the leaves it reads as the clump's shaded inside, as on the sheet, instead of rock or sky."""
    rng = random.Random(seed)
    bm = a.bm
    off = rng.uniform(0, math.pi)
    ring = []
    for k in range(6):
        d = Vector((math.cos(off + k * math.pi / 3) * r * rng.uniform(0.9, 1.05),
                    math.sin(off + k * math.pi / 3) * r * rng.uniform(0.9, 1.05), rng.uniform(-0.08, 0.08) * r))
        if side is not None:
            d += side * (d.dot(side) * (stretch - 1.0))
        ring.append(bm.verts.new(centre + d))
    top = bm.verts.new(centre + Vector((0, 0, 0.85 * r)))
    bot = bm.verts.new(centre + Vector((0, 0, -0.7 * r)))
    fs = []
    for k in range(6):
        j = (k + 1) % 6
        fs.append(bm.faces.new((ring[k], ring[j], top)))
        fs.append(bm.faces.new((ring[j], ring[k], bot)))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    vs = ring + [top, bot]
    a._finish(vs, K.mix_key(LEAF, LEAF_DEEP, 0.6), tint=1.0)
    for f in fs[0::2]:          # its upper cone (by position) shows through the crown's gaps from above
        f.material_index = a._mi(K.mix_key(LEAF, LEAF_DEEP, 0.2))
    return vs


class _Contact:
    """Keeps every leaf, core and flower touching what is already placed (m035): the ground, the rocks, the moss and
    the pieces accepted before it, so every shell has a chain of contact down to the ground or a rock. A piece further
    than CONTACT from all of that is slid toward its nearest point until it is 0.015 away."""

    def __init__(self, coords, polys):
        self.coords = list(coords) + [Vector((-30, -30, 0)), Vector((30, -30, 0)), Vector((30, 30, 0)),
                                      Vector((-30, 30, 0))]
        k = len(self.coords)
        self.polys = list(polys) + [[k - 4, k - 3, k - 2, k - 1]]
        self.moved = 0
        self.worst = 0.0

    @classmethod
    def of(cls, vs):
        """From the faces of the given (rock / moss) verts."""
        coords, polys, idx = [], [], {}
        for f in _faces([v for v in vs if v.is_valid]):
            p = []
            for v in f.verts:
                if v not in idx:
                    idx[v] = len(coords)
                    coords.append(v.co.copy())
                p.append(idx[v])
            polys.append(p)
        return cls(coords, polys)

    def _gap(self, tree, vs):
        best = (1e9, None, None)
        for v in vs:
            loc, _, _, d = tree.find_nearest(v.co)
            if loc is not None and d < best[0]:
                best = (d, v.co.copy(), loc)
        if best[0] > CONTACT:
            fs = _faces(vs)
            vi = {v: i for i, v in enumerate(vs)}
            mine = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
            if mine.overlap(tree):
                return (0.0, None, None)
        return best

    def attach(self, vs, guard=None):
        for _ in range(4):
            tree = BVHTree.FromPolygons(self.coords, self.polys)
            d, p, q = self._gap(tree, vs)
            if d <= CONTACT:
                break
            self.worst = max(self.worst, d)
            mv = (q - p) * (1.0 - 0.015 / d)
            for v in vs:
                v.co += mv
            if guard:
                guard.push(vs, 0.05)
            _lift(vs)
            self.moved += 1
        idx = {}
        for f in _faces(vs):
            pl = []
            for v in f.verts:
                if v not in idx:
                    idx[v] = len(self.coords)
                    self.coords.append(v.co.copy())
                pl.append(idx[v])
            self.polys.append(pl)


def _surface(tree, c0, out, z, fallback):
    """Where a horizontal ray at height z, coming back along -out from just outside the cluster, meets a rock."""
    if tree is None or out is None:
        return fallback
    o = Vector((c0.x, c0.y, z)) + out * 2.5
    hit = tree.ray_cast(o, -out, 9.0)
    return Vector((hit[0].x, hit[0].y, z)) if hit[0] is not None else fallback


def _cluster(a, name, root, w, h, seed, kind="low", flower=0, lean_to=None, guard=None, rocks=None, contact=None,
             face=None, bud=False):
    """A clover cluster of dense rounded leaf mounds seated at root (x, y, z). kind: low / small (one mound) or tall
    (2-3 mounds stacked up the flank of the rock toward lean_to). flower: flowers on the top mound's shoulder (a second
    one on the mound below), facing the azimuth `face`. Returns verts."""
    rng = random.Random(seed)
    kp = KINDS[kind]
    tint = 1.0 + rng.uniform(-CL_TINT, CL_TINT)
    c0 = Vector(root)
    R0 = kp["R"] * w
    out = None
    if lean_to is not None:
        out = Vector((c0.x - lean_to[0], c0.y - lean_to[1], 0.0))
        out = out.normalized() if out.length > 1e-6 else None
    plan, mounds = [], []
    if kind == "tall":
        nm = 2 if h < 2.4 else 3
        rs = [R0 * TALL_MOUNDS[j][0] for j in range(nm)]
        z0, z1 = c0.z + MOUND_Z * rs[0], c0.z + h - rs[-1] - 0.22
        for j in range(nm):
            fj = j / (nm - 1)
            z = z0 + (z1 - z0) * fj
            up = Vector((c0.x, c0.y, z))
            if j == 0:
                centre = up
            else:
                # stacked over the ground mound, leaning UPPER_LEAN of the way in to rest against the flank; where the
                # flank bulges out past the column, on the flank
                s = _surface(rocks, c0, out, z, up)
                rest = Vector((s.x, s.y, z)) + (out * rs[j] * UPPER_OFF if out is not None else Vector())
                centre = rest if (out is not None and (rest - up).dot(out) > 0) else up.lerp(rest, UPPER_LEAN)
            nj = TALL_MOUNDS[j][1]
            st = HUG_STRETCH if (j == 0 and out is not None) else 1.0
            mounds.append((centre, nj, rs[j], st))
            plan += _mound(rng, centre, rs[j], nj, kp["L"], (0.5 * fj, min(1.0, 0.5 * fj + 0.75)), out, stretch=st)
    else:
        centre = c0 + Vector((0, 0, MOUND_Z * R0))
        mounds.append((centre, kp["n"], R0, 1.0))
        plan = _mound(rng, centre, R0, kp["n"], kp["L"], (0.0, 1.0), out)
    side = Vector((-out.y, out.x, 0.0)) if out is not None else None
    allv, leaves, dropped, cores = [], 0, 0, 0
    if CORE_R and kind != "small":
        for k, (centre, _, r, st) in enumerate(mounds):
            vs = _core(a, centre, CORE_R * r, seed + 31 * k, side, st)
            if guard:
                guard.push(vs, 0.05)
            _lift(vs)
            if contact:
                contact.attach(vs, guard)
            _mottle(a, _faces(vs), LEAF_MOTTLE["amp"], LEAF_MOTTLE["scale"], LEAF_MOTTLE["seed"] + seed, tint=tint)
            allv += vs
            cores += 1
    for base, L, yaw, pitch, t in plan:
        tq = round(_q(t, 4), 2)
        vs = _leaf(a, tuple(base), L, _leaf_key(tq), yaw, pitch, roll=rng.uniform(-LEAF_ROLL, LEAF_ROLL),
                   tip_key=_tip_key(tq))
        if guard:
            dep, _ = guard.depth(vs)
            if dep > DROP_DEPTH:
                _kill(a, vs)
                dropped += 1
                continue
            guard.push(vs, 0.05)
        _lift(vs)
        if contact:
            contact.attach(vs, guard)
        _mottle(a, _faces(vs), LEAF_MOTTLE["amp"], LEAF_MOTTLE["scale"], LEAF_MOTTLE["seed"] + seed, tint=tint)
        allv += vs
        leaves += 1
    if face is None:
        # out of the group (away from its middle) and toward the front (front half) or the back (back half)
        od = Vector((c0.x - GROUP_MID[0], c0.y - GROUP_MID[1], 0.0))
        od = od.normalized() if od.length > 0.5 else Vector((0.0, -1.0, 0.0))
        od = (od + Vector((0.0, -1.0 if c0.y < 2.5 else 1.0, 0.0))).normalized()
        face = math.atan2(od.y, od.x)
    fd = Vector((math.cos(face), math.sin(face), 0.0))
    fcs = []
    for k in range(flower):
        # on a mound's shoulder on the side it faces (and out from the rock), sitting on the leaves: the sheet's
        # flowers show whole, not sunk among the leaves or floating above them
        mt, _, rt, _ = mounds[-1 - k] if k < len(mounds) else mounds[-1]
        p = mt + fd * 0.45 * rt + (out * 0.25 * rt if out is not None else Vector())
        p.z = mt.z + 0.95 * rt
        fv = _flower(a, tuple(p), FLOWER_R, seed + 7 + k, face=face)
        if guard:
            guard.push(fv, 0.02)
        if contact:
            contact.attach(fv, guard)
        allv += fv
        fcs.append([round(x, 2) for x in sum((v.co for v in fv), Vector()) / len(fv)])
    if bud:
        m0, _, r0, _ = mounds[0]
        p = m0 + Vector((0.75 * r0, -0.85 * r0, -0.1 * r0))
        fv = _flower(a, tuple(p), FLOWER_R * 0.7, seed + 19, face=face)
        if guard:
            guard.push(fv, 0.02)
        _lift(fv)
        if contact:
            contact.attach(fv, guard)
        allv += fv
        fcs.append([round(x, 2) for x in sum((v.co for v in fv), Vector()) / len(fv)])
    allv = [v for v in allv if v.is_valid]
    xs, ys, zs = ([v.co[i] for v in allv] for i in range(3))
    CLUSTER_INFO[name] = dict(leaves=leaves, dropped=dropped, cores=cores, mounds=len(mounds), flowers=fcs,
                              size=[round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2),
                                    round(max(zs) - min(zs), 2)], top=round(max(zs), 2))
    return allv


# name -> root (x, y), seat ("ground" or (rock or "any", ray-from z)), kind, w, h, flowers, lean toward (x, y) or None,
# flower facing azimuth (None: out of the group), seed. Fix round 1: the tall columns (FL1, FL6, FL9, FL10, FL13) are
# stacked mounds leaning on their rock; FL8, FL9 and FL10 face their flowers to the back views.
BACK = math.pi / 2
BACK_LEFT = math.radians(118.0)      # toward the r34 camera (az 208, at the back left)
CLUSTERS = (
    ("FL1", (-4.7, -1.5), "ground", "tall", 2.6, 2.8, 1, (-2.2, -1.5), None, 36401),
    ("FL2", (-0.7, -0.6), ("B", 60.0), "small", 1.2, 0.8, 0, None, None, 36402),
    ("FL3", (0.45, -2.5), "ground", "tall", 2.2, 3.6, 1, (1.4, 1.2), -math.pi / 2, 36403),
    ("FL4", (-1.6, -4.0), "ground", "low", 1.9, 0.9, 0, None, None, 36404),
    ("FL5", (0.9, -4.55), "ground", "low", 1.9, 0.9, 0, None, None, 36405),
    ("FL6", (4.85, -0.05), "ground", "tall", 2.6, 4.2, 2, (1.4, 1.2), -1.25, 36406),
    ("FL7", (5.45, -1.95), "ground", "small", 1.2, 0.6, 0, None, None, 36407),
    ("FL8", (3.1, 4.1), ("G", 60.0), "low", 2.2, 1.4, 1, None, BACK, 36408),
    ("FL9", (1.0, 4.2), "ground", "tall", 3.0, 3.4, 1, (1.3, 1.4), BACK, 36409),
    ("FL10", (-4.1, 1.3), "ground", "tall", 2.8, 4.4, 1, (-2.2, -1.5), BACK_LEFT, 36410),
    ("FL11", (-5.35, 2.5), "ground", "low", 1.8, 0.9, 0, None, None, 36411),
    ("FL12", (-3.95, -3.85), "ground", "low", 1.9, 0.9, 0, None, None, 36412),
    ("FL13", (5.15, 2.1), "ground", "tall", 2.2, 2.2, 0, (3.6, 3.3), None, 36413),
)
SEAT_SINK = 0.10


def dressing(a, rock_tree, rocks_vs, contact):
    CLUSTER_INFO.clear()
    guard = _Guard(rock_tree)
    for name, xy, seat, kind, w, h, fl, lean, face, seed in CLUSTERS:
        z = 0.0
        if seat != "ground":
            rk, z_from = seat
            tree = rock_tree if rk == "any" else K.bvh_of(rocks_vs[rk])
            hit = tree.ray_cast(Vector((xy[0], xy[1], z_from)), Vector((0, 0, -1)), 200)
            z = (hit[0].z - SEAT_SINK) if hit[0] is not None else 0.0
        _cluster(a, name, (xy[0], xy[1], z), w, h, seed, kind=kind, flower=fl, lean_to=lean, guard=guard,
                 rocks=rock_tree, contact=contact, face=face)
    CONTACT_INFO.update(moved=contact.moved, worst_gap=round(contact.worst, 3), guard_moves=guard.moved)
    return guard.moved


# ---- parts -------------------------------------------------------------------------------------------------------------
def rock_a_part(a):
    ROCK_INFO.clear()
    CAP_INFO.clear()
    a.bm.faces.layers.int.new("kit_part")
    K.tag_part(a, _rock(a, "A", (0.0, 0.0)), "A")
    _smear(a, K.part(a, "A"), "A", (0.0, 0.0))
    _cap(a, "A", K.part(a, "A"), (0.0, 0.0))


def rock_b_part(a):
    ROCK_INFO.clear()
    CAP_INFO.clear()
    vs = _rock(a, "B", (0.0, 0.0))
    cap = _cap(a, "B", vs, (0.0, 0.0))
    tree = K.bvh_of(vs)
    hit = tree.ray_cast(Vector((1.5, 1.2, 60.0)), Vector((0, 0, -1)), 200)
    z = hit[0].z - SEAT_SINK if hit[0] is not None else 4.0
    _cluster(a, "sprigB", (1.5, 1.2, z), 1.2, 0.8, 36402, kind="small", guard=_Guard(tree), rocks=tree,
             contact=_Contact.of(vs + cap))


def rock_c_part(a):
    ROCK_INFO.clear()
    CAP_INFO.clear()
    vs = _rock(a, "C", (0.0, 0.0))
    _cap(a, "Ctuft", vs, (0.0, 0.0))


def small_rock_part(a):
    ROCK_INFO.clear()
    a.bm.faces.layers.int.new("kit_part")
    K.tag_part(a, _rock(a, "D", (0.0, 0.0)), "D")
    _smear(a, K.part(a, "D"), "D", (0.0, 0.0))


def foliage_part(a):
    _cluster(a, "part_plain", (0.0, 0.0, 0.0), 1.7, 1.0, 36421, contact=_Contact([], []))


def flower_part(a):
    _cluster(a, "part_flower", (0.0, 0.0, 0.0), 1.8, 1.1, 36422, flower=1, bud=True, contact=_Contact([], []))


# ---- hero --------------------------------------------------------------------------------------------------------------
def hero(a):
    ROCK_INFO.clear()
    CAP_INFO.clear()
    cen = LAYOUT.get("centres") or layout()
    # the face-tag layer first, while the bmesh is empty: adding a layer (and subdivide_edges in the smears) makes
    # every Python vertex reference stale, so each rock is found again by its tag after the smears
    a.bm.faces.layers.int.new("kit_part")
    for name in BIG + SMALL:
        K.tag_part(a, _rock(a, name, cen[name]), name)
    _smear(a, K.part(a, "A"), "A", cen["A"])
    _smear(a, K.part(a, "D"), "D", cen["D"])
    rocks = {name: K.part(a, name) for name in BIG + SMALL}
    moss = _cap(a, "A", rocks["A"], cen["A"]) + _cap(a, "B", rocks["B"], cen["B"])
    allrock = [v for vs in rocks.values() for v in vs if v.is_valid]
    tree = K.bvh_of(allrock)
    LAYOUT["guard_moves"] = dressing(a, tree, rocks, _Contact.of(allrock + moss))
    LAYOUT["touch"] = _touches(rocks)


def _shell_of(a, centre, z):
    """The verts of the rock shell containing the point nearest (centre, z) (refine replaces vertex references)."""
    bm = a.bm
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    p = Vector((centre[0], centre[1], z))
    loc, n, idx, d = tree.find_nearest(p)
    f = bm.faces[idx]
    seen, stack = {f}, [f]
    while stack:
        g = stack.pop()
        for e in g.edges:
            for h in e.link_faces:
                if h not in seen:
                    seen.add(h)
                    stack.append(h)
    return list({v for g in seen for v in g.verts})


def _touches(rocks):
    """Which rocks each rock touches or overlaps, and the deepest overlap of any pair."""
    hulls = {k: _planes([v.co.copy() for v in vs if v.is_valid]) for k, vs in rocks.items()}
    out, worst = {}, 0.0
    names = list(hulls)
    for i, a_ in enumerate(names):
        for b_ in names[i + 1:]:
            p = _pen(hulls[a_], hulls[b_])
            if p > -0.05:
                out.setdefault(a_, []).append(b_)
                out.setdefault(b_, []).append(a_)
            worst = max(worst, p)
    return {"pairs": out, "max_overlap": round(worst, 3)}


NOTES = {
    HERO: "Mossy rock cluster: a group of separate big-faceted warm grey-pink rocks (a tall pillar A with a lobed lime "
          "moss cap, a squat block B with a moss mat, a low dome C, two back domes, six small rocks and a pebble) with "
          "thirteen round-leaf clover clusters (seven white flowers) in the joints and round the foot; every rock, moss "
          "cap, leaf, petal and flower centre its own closed shell. No VFX",
    A_P: "Rock A (tall, main): tall faceted warm grey-pink pillar with a sloping crown, a lobed lime moss cap and an "
         "olive moss smear; flat bottom",
    B_P: "Rock B (medium): squat upright faceted block with a broad tilted crown, a flat lobed moss mat and a clover "
         "sprig; flat bottom",
    C_P: "Rock C (medium): low faceted warm grey-pink dome with a small moss tuft; flat bottom",
    SMALL_P: "Small Rock (reusable): chunky faceted warm grey-pink lump with an olive moss smear at its foot",
    FOL_P: "Foliage Cluster (reusable): clover rosette of round spoon leaves (deep outer, lime inner); every leaf its "
           "own closed piece",
    FLW_P: "Flower Cluster (reusable): clover rosette with a white five-petal flower and a small bud",
}
COLLISION = {HERO: "hull", A_P: "hull", B_P: "hull", C_P: "hull", SMALL_P: "hull", FOL_P: "none", FLW_P: "none"}


# ---- make / finish (no unions: closed shells) ----------------------------------------------------------------------------
def _tri_all(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = m012._tri_quads(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    return n


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
    lg = {"split": _tri_all(o)}
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


# ---- checks ------------------------------------------------------------------------------------------------------------
def _kind(ks, nf):
    if any(x.startswith("m036_rock") for x in ks):
        return "rock"
    if any(x.startswith("m036_moss") and not x.startswith("m036_moss_smear") for x in ks):
        return "moss"
    if all(x.startswith("m036_leaf") for x in ks):
        return "leaf"
    if ks == {PETAL}:
        return "petal"
    if ks == {POLLEN}:
        return "pollen"
    return "other"


def shells_report(o):
    """Per shell: kind, tris, non-manifold edges and verts, boundary edges, self-intersecting face pairs inside the
    shell, inverted faces (ray parity inside the shell), signed volume. (m035)"""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = [m.get("flintkit_key", m.name) if m else "" for m in o.data.materials]
    groups = {}
    for f in bm.faces:
        groups.setdefault(ids[f.index], []).append(f)
    out = []
    for k in range(n):
        fs = groups[k]
        es = {e for f in fs for e in f.edges}
        vs = list({v for f in fs for v in f.verts})
        ks = {keys[f.material_index] for f in fs}
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        hits = sum(1 for a_, b_ in tree.overlap(tree) if a_ < b_ and not set(fs[a_].verts) & set(fs[b_].verts))
        inv = 0
        for f in fs:
            odd = 0
            for dv in (f.normal, (f.normal + f.normal.orthogonal().normalized() * 0.21).normalized(),
                       (f.normal - f.normal.orthogonal().normalized() * 0.17).normalized()):
                p = f.calc_center_median() + dv * 1e-4
                cnt, x, last = 0, p.copy(), None
                for _ in range(40):
                    h = tree.ray_cast(x, dv)
                    if h[0] is None:
                        break
                    if last is None or (h[0] - last).length > 1e-4:
                        cnt += 1
                    last = h[0]
                    x = h[0] + dv * 1e-5
                odd += cnt % 2
            inv += odd == 3
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) / 3.0
        out.append({"kind": _kind(ks, len(fs)), "tris": sum(len(f.verts) - 2 for f in fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary), "self_hits": hits, "inverted": inv,
                    "volume": round(vol, 4)})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """Floating dressing (fix round 1, after m035): per shell, whether it touches another shell (triangles overlap, or
    a vert within `tol` of another shell's surface) or the ground (z <= tol, the object's own bottom). Returns the
    count of shells touching nothing at `tol` and their kinds, the worst such gap, the largest nearest-neighbour gap of
    any non-rock shell, and the shells with no chain of contact down to the ground or a rock at `tol` and at
    `chain_tol`."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = [m.get("flintkit_key", m.name) if m else "" for m in o.data.materials]
    fsh = [ids[f.index] for f in bm.faces]
    vsh = {}
    for f in bm.faces:
        for v in f.verts:
            vsh[v.index] = fsh[f.index]
    tree = BVHTree.FromBMesh(bm)
    z0 = min(v.co.z for v in bm.verts)
    zmin = [1e9] * n
    for v in bm.verts:
        if v.index in vsh:
            zmin[vsh[v.index]] = min(zmin[vsh[v.index]], v.co.z - z0)
    ks = [set() for _ in range(n)]
    for f in bm.faces:
        ks[fsh[f.index]].add(keys[f.material_index])
    kind = [_kind(ks[k], 0) for k in range(n)]
    anchors = {k for k in range(n) if kind[k] == "rock"}
    pairs = set()
    for i, j in tree.overlap(tree):
        a_, b_ = fsh[i], fsh[j]
        if a_ != b_:
            pairs.add((min(a_, b_), max(a_, b_)))
    near = {}
    for v in bm.verts:
        s = vsh.get(v.index)
        if s is None:
            continue
        for loc, _, fi, d in tree.find_nearest_range(v.co, chain_tol):
            t = fsh[fi]
            if t != s:
                k = (min(s, t), max(s, t))
                near[k] = min(near.get(k, 1e9), d)
    for p in pairs:
        near[p] = 0.0
    gap = [1e9] * n
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    for k in range(n):
        gap[k] = min(gap[k], max(0.0, zmin[k]))

    def chained(t):
        adj = {k: set() for k in range(n)}
        for (a_, b_), d in near.items():
            if d <= t:
                adj[a_].add(b_)
                adj[b_].add(a_)
        seen = {k for k in range(n) if zmin[k] <= t} | anchors
        stack = list(seen)
        while stack:
            k = stack.pop()
            for m_ in adj[k]:
                if m_ not in seen:
                    seen.add(m_)
                    stack.append(m_)
        return [k for k in range(n) if k not in seen]
    floating = [k for k in range(n) if gap[k] > tol and k not in anchors]
    un, un2 = chained(tol), chained(chain_tol)
    dress = [k for k in range(n) if k not in anchors]
    res = {"shells": n, "anchors": len(anchors), "floating": len(floating),
           "floating_kinds": sorted({kind[k] for k in floating}),
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "max_gap_all": round(max([gap[k] for k in dress], default=0.0), 3),
           "unchained": len(un), "unchained_kinds": sorted({kind[k] for k in un}),
           "unchained_chain_tol": len(un2)}
    bm.free()
    return res


def rock_metrics(fs, name=""):
    """Spec 2.2 shape targets for one rock's faces (bmesh, build frame): tris, area and edge CV (floor excluded),
    valence, H/W, widest height, flat facets seen from the front (az 0, el 6; coplanar neighbours merged, share of the
    projected area), crown faces (normal z > 0.8 in the top fifth) and their span, wall-facing share, floor span and
    corners, and regular-pattern vertices."""
    ground = [f for f in fs if f.normal.z < -0.99 and f.calc_center_median().z < 1e-3]
    side = [f for f in fs if f not in set(ground)]
    areas = np.array([f.calc_area() for f in side])
    edges = list({e for f in side for e in f.edges})
    el = np.array([e.calc_length() for e in edges])
    vs = [v for v in {v for f in side for v in f.verts} if v.co.z > 1e-3]
    val = np.array([len(v.link_edges) for v in vs])
    allv = list({v for f in fs for v in f.verts})
    xs, ys, zs = [v.co.x for v in allv], [v.co.y for v in allv], [v.co.z for v in allv]
    W, D, H = max(xs) - min(xs), max(ys) - min(ys), max(zs)

    def width(z):
        pts = []
        for e in edges:
            a_, b_ = e.verts
            if (a_.co.z - z) * (b_.co.z - z) < 0:
                t = (z - a_.co.z) / (b_.co.z - a_.co.z)
                pts.append(a_.co.lerp(b_.co, t).x)
        return (max(pts) - min(pts)) if pts else 0.0
    hs = np.linspace(0.05, 0.95, 10)
    widths = [width(h * H) for h in hs]
    wmax = max(widths)
    regs = _regions(side)
    vv = Vector((0.0, -math.cos(math.radians(6)), math.sin(math.radians(6))))
    proj = [sum(g.calc_area() * max(0.0, g.normal.dot(vv)) for g in reg) for reg in regs]
    tot = sum(proj)
    seen = sorted([p / tot for p in proj if p / tot >= 0.004], reverse=True)
    reg_area = sorted([sum(g.calc_area() for g in reg) for reg in regs], reverse=True)
    crown = [f for f in side if f.normal.z > 0.8 and f.calc_center_median().z > 0.8 * H]
    cx = [v.co.x for f in crown for v in f.verts]
    cyy = [v.co.y for f in crown for v in f.verts]
    crown_regs = _regions(crown) if crown else []
    wall = sum(f.calc_area() for f in side if abs(f.normal.z) < math.sin(math.radians(15)))
    gx = [v.co.x for f in ground for v in f.verts]
    gy = [v.co.y for f in ground for v in f.verts]
    gverts = {v for f in ground for v in f.verts}
    corners = sum(1 for v in gverts if any(e.is_manifold and len([f for f in e.link_faces if f in set(side)]) == 1
                                          and e.other_vert(v) in gverts for e in v.link_edges)) if ground else 0
    # regular pattern: a vertex ringed by 5-6 triangles whose areas are within 15 % of their mean
    reg_v = 0
    for v in vs:
        lf = [f for f in v.link_faces if f in set(side)]
        if 5 <= len(lf) <= 6:
            ar = [f.calc_area() for f in lf]
            m = sum(ar) / len(ar)
            if all(abs(x - m) <= 0.15 * m for x in ar):
                reg_v += 1
    tilt = 0.0
    if crown:
        nsum = sum((f.normal * f.calc_area() for f in crown), Vector()).normalized()
        tilt = math.degrees(math.acos(max(-1.0, min(1.0, nsum.z))))
    med = float(np.median(areas)) if len(areas) else 1.0
    return {"tris": len(side), "floor_tris": len(ground), "size": [round(W, 2), round(D, 2), round(H, 2)],
            "h_w": round(H / W, 2), "area_cv": round(float(areas.std() / areas.mean()), 2),
            "edge_cv": round(float(el.std() / el.mean()), 2),
            "valence": [int(val.min()), int(val.max()), round(float(val.mean()), 2),
                        round(float(np.bincount(val).max() / len(val)), 2)],
            "widths": [round(w / wmax, 2) for w in widths], "widest_h": round(float(hs[int(np.argmax(widths))]), 2),
            "facets_seen": len(seen), "largest_facet_share": round(seen[0], 3) if seen else 0,
            "largest_facet_area": round(reg_area[0], 2), "largest_over_median": round(reg_area[0] / med, 1),
            "flat_regions": len(regs), "crown_faces": len(crown), "crown_regions": len(crown_regs),
            "crown_span": [round(max(cx) - min(cx), 2) if cx else 0, round(max(cyy) - min(cyy), 2) if cyy else 0],
            "crown_tilt_deg": round(tilt, 1), "wall_share": round(wall / max(1e-9, sum(areas)), 2),
            "floor_span": [round((max(gx) - min(gx)) / W, 2) if gx else 0, round((max(gy) - min(gy)) / D, 2) if gy else 0],
            "floor_corners": corners, "regular_verts": reg_v}


# ---- render measurement (the study's masks, spec "Pixel boxes and masks") ---------------------------------------------
def classify(px):
    """px: (h, w, 3) sRGB 0-1. Returns (class map: 1 rock, 2 green, 3 flower, else 0; ground-shadow mask). (m035)"""
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
    G = (hue >= 45) & (hue <= 150) & (s >= 0.28) & (v >= 0.12)
    F = ((s < 0.10) & (v >= 0.95)) | ((hue >= 36) & (hue < 56) & (s >= 0.55) & (v >= 0.7))
    B = (s < 0.03) & (v >= 0.45) & (v <= 0.95)
    R = ((hue <= 45) | (hue >= 190)) & (s >= 0.03) & (s <= 0.42) & (v >= 0.22) & (v <= 0.985) & ~G & ~F & ~B
    out = np.zeros(mx.shape, np.int8)
    out[R] = 1
    out[G & ~F] = 2
    out[F] = 3
    return out, B


def measure(path, box=None, bg_tol=0.05):
    """Silhouette bbox, W:H, shares (rock / green / flower, ground shadow excluded), 21-column top profile and the
    class medians of a render (or a box of the sheet) whose background is the corner colour."""
    kit = K.NS["KIT"]
    px = np.clip(kit["load_px"](path)[::-1, :, :3], 0, 1)
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1]
    bg = np.median(np.concatenate([px[:4, :4].reshape(-1, 3), px[:4, -4:].reshape(-1, 3)]), axis=0)
    sil = np.abs(px - bg).max(-1) > bg_tol
    cls, B = classify(px)
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


SHEET_CELLS = {"f34_sheet": (17, 108, 530, 430), "r34_sheet": (530, 108, 1007, 430), "front_sheet": (17, 512, 283, 708),
               "side_sheet": (285, 512, 511, 708), "rear_sheet": (513, 512, 764, 708), "top_sheet": (766, 512, 1007, 708)}


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
    # the parts shots against the exploded view's unshadowed medians (spec 5.7)
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


PART_TARGETS = {"part_rocka": {"rock_med": "#C0A598", "green_med": "#B3BA1B"},
                "part_rockb": {"rock_med": "#BFA598", "green_med": "#AEB916"},
                "part_rockc": {"rock_med": "#B09992", "green_med": "#B7BE17"},
                "part_smallrock": {"rock_med": "#B4998C"},
                "part_foliage": {"green_med": "#88B205"},
                "part_flowercluster": {"green_med": "#90B508", "flower_med": "#FEFEFC"}}


# ---- build -------------------------------------------------------------------------------------------------------------
PARTS = ((A_P, rock_a_part), (B_P, rock_b_part), (C_P, rock_c_part), (SMALL_P, small_rock_part),
         (FOL_P, foliage_part), (FLW_P, flower_part))
TARGET_SIZE = ((12.6, 0.5), (10.8, 0.6), (8.0, 0.3))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m036_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib",
                                                                                 "MossyRockCluster"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build(render=True, parts=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    LAYOUT.clear()
    layout()
    objs, log = {}, {}
    part_rocks = {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn, "part", 1000)
            if ROCK_INFO:
                part_rocks[name] = {k: dict(v) for k, v in ROCK_INFO.items()}
    h, log["hero"] = _make(HERO, hero, "hero", 4000)
    log["layout"] = {k: v for k, v in LAYOUT.items()}
    log["caps"] = {k: dict(v) for k, v in CAP_INFO.items()}
    log["clusters"] = {k: dict(v) for k, v in CLUSTER_INFO.items()}
    log["contact_moves"] = dict(CONTACT_INFO)
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
    # no floating dressing (STAGES): every leaf, core, petal, flower centre and moss shell within CONTACT of a
    # neighbour, a rock or the ground, and chained by contact to the ground or a rock
    contact = {o.name: contact_report(o) for o in order}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} shells touch nothing within {CONTACT} ({c['floating_kinds']}, "
                            f"worst {c['worst_gap']}), {c['unchained']} have no chain of contact to the ground or a "
                            f"rock")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 9: none)")
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
           "rocks": rocks,
           "part_rocks": part_rocks,
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order)
        out["compare"] = compare()
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders -----------------------------------------------------------------------------------------------------------
# decision 5: the hero cell is a front view near 12 deg, the front cell about 8, the rear three-quarter a back-LEFT
# camera at azimuth 208, the rear 180, the side the kit side camera (90); floor hidden and a 3x lens on *_sheet shots.
SHEET_VIEWS = {"f34_sheet": (0, 12), "front_sheet": (0, 8), "r34_sheet": (208, 12), "rear_sheet": (180, 8),
               "side_sheet": (90, 8), "top_sheet": (0, 89)}
PARTS_SHOT = (-20, 20)


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded Construction: A high in the middle, B at the left, C at
    the right, small rocks low, the foliage and flower clusters along the bottom."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []

    def put(tag, part, m):
        c = bpy.data.objects.new(f"{PFX}expl_{tag}", by[part].data)
        coll.objects.link(c)
        c.matrix_world = m
        shown.append(c)
    S = Matrix.Diagonal
    o0 = Matrix.Translation((objs[0].location.x + 60, objs[0].location.y, 0))
    put("A", A_P, o0 @ Matrix.Translation((0.3, 1.5, 4.6)))
    put("B", B_P, o0 @ Matrix.Translation((-4.4, 0.0, 2.4)))
    put("C", C_P, o0 @ Matrix.Translation((4.6, 0.3, 2.0)))
    put("D", SMALL_P, o0 @ Matrix.Translation((-7.4, -1.6, 0.6)))
    put("E", SMALL_P, o0 @ Matrix.Translation((0.2, -0.4, 1.2)) @ Matrix.Rotation(1.2, 4, "Z") @ S((1.6, 1.5, 1.25, 1)))
    put("F", SMALL_P, o0 @ Matrix.Translation((7.6, -1.2, 0.5)) @ Matrix.Rotation(2.4, 4, "Z") @ S((1.3, 1.3, 1.4, 1)))
    for i, (x, y, part) in enumerate(((-5.4, -4.0, FOL_P), (-3.1, -4.6, FOL_P), (-1.6, -2.6, FOL_P), (0.4, -5.0, FLW_P),
                                      (3.0, -3.8, FLW_P), (1.6, -2.4, FOL_P), (5.2, -4.2, FLW_P))):
        put(f"cl{i}", part, o0 @ Matrix.Translation((x, y, 0.0)) @ Matrix.Rotation(i * 1.1, 4, "Z"))
    bpy.context.view_layer.update()
    return shown


def _scale_marker(h):
    """A 5.5-stud character stand-in (a plain grey column) beside the hero, for the scale shot."""
    a = K.fk().Asset(PFX + "char", "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=ROCK_SHADOW, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=ROCK_SHADOW, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=ROCK_SHADOW, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    c.location = h.location + Vector((h.dimensions.x / 2 + 1.5, -2.0, 0))
    bpy.context.view_layer.update()
    return c


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    marker = _scale_marker(h)
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        by = {o.name: o for o in objs}
        for o in objs[1:]:
            extra["part_" + o.name.replace("MossyRockCluster", "").lower()] = ([o], *PARTS_SHOT)
        if B_P in by:
            extra["under_cu"] = ([by[B_P]], 0, -35)
        if shown:
            extra["exploded"] = (shown, 0, 20)
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
            # Rock / Rock Junction: A's lit flank meeting C's top with FL3 in the joint
            out["junc_cu"] = m033.render_close([h], f"{d}/junc_cu.png", 15, 10, off @ Vector((1.0, -1.3, 2.0)), 1.9)
        return out
    finally:
        for o in shown + [marker]:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if o is marker and me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def preview(names=("f34_sheet", "front_sheet", "r34_sheet", "rear_sheet", "side_sheet", "top_sheet"), vfx=False,
            extra=None):
    """Just the sheet comparison shots of the hero (fast tuning loop), then compare()."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    ex = {k: ([h], *SHEET_VIEWS[k]) for k in names}
    ex.update(extra or {})
    try:
        M.views(NUM, [h], names=(), extra=ex, vfx=vfx)
    finally:
        kit["render_group"] = orig
    return compare([n for n in names if n in SHEET_CELLS])


def hero_only():
    """Rebuild just the hero (tuning loop)."""
    M.coll(NUM, TITLE)
    palette()
    LAYOUT.clear()
    layout()
    h, lg = _make(HERO, hero, "hero", 4000)
    _cleanup_tmp()
    _spec()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, _ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals")}, "log": lg, "layout": dict(LAYOUT),
            "thin": m012._thin(h, POLISH_LIM),
            "caps": {k: dict(v) for k, v in CAP_INFO.items()},
            "clusters": {k: dict(v) for k, v in CLUSTER_INFO.items()}, "contact": contact_report(h),
            "contact_moves": dict(CONTACT_INFO),
            "shells": {k: sum(1 for s in shells_report(h) if s["kind"] == k) for k in ("rock", "moss", "leaf", "petal",
                                                                                      "pollen", "other")},
            "shell_problems": [(i, s["kind"]) for i, s in enumerate(shells_report(h))
                               if s["self_hits"] or s["inverted"] or s["boundary_edges"] or s["nonmanifold_verts"]
                               or s["volume"] <= 0]}
