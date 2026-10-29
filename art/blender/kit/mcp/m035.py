"""035 Boulder (references/035.png): a squat, broad-faceted warm grey-pink boulder made of two masses (A, the big
front-right mass; B, the lower left mass) whose union leaves a real cleft down the front-left face, a leafy lime moss
cap of five lobed rosette mounds on the crown (the left one draped onto B's shoulder), an olive moss stain in the
cleft's foot and low on B, five small faceted rocks and a pebble round the foot, and nine chunky round-leaf foliage
clusters round the left, back and right of the foot (three with a white five-petal flower). The front of the foot is
left open.

    import importlib, kit_models, m035; importlib.reload(kit_models); importlib.reload(m035); m035.build()

Build frame: studs, front -Y, +X right, ground z 0, origin = the main rock's base centre; every object ends with its
origin at its bbox bottom centre. W01 owns Boulder* and sheet 06 *Boulder, so the names are MossyBoulder* (spec 8):
- MossyBoulderMainRock (main_rock_part): A u B with the cleft and the moss stain, floor-cut flat. One closed shell.
- MossyBoulderMossCap (moss_cap_part): the five rosettes as conformed to the crown, united into one shell; a flat
  brown underside inside a lime rim.
- MossyBoulderSmallRock (small_rock_part): small rock variant A (1.8 across).
- MossyBoulderFoliage (foliage_part): the low foliage cluster with its flower (each leaf, petal and centre its own
  closed shell, as the sheet's "separate meshes").

The hero (MossyBoulder, decision 6) is one object of closed shells: the stone (A, B and the five rosettes, united one
shell at a time with merge-0 exact unions at the world origin, floor-cut), each small rock, and each leaf, petal and
flower centre. Colour (stage 4) is painted by position inside the builders before the union. Stages 5-6: nothing
(decision 8: the sheet shows no glow, light or effect). See M035_spec.md.
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
import m016
import m033

NUM, TITLE, SHEET = 35, "Boulder", "M035"
OFF = "m035_offset"
PFX = "_m035_"
HERO = "MossyBoulder"
ROCK_P, CAP_P, SMALL_P, FOL_P = ("MossyBoulderMainRock", "MossyBoulderMossCap", "MossyBoulderSmallRock",
                                 "MossyBoulderFoliage")

ROCK, ROCK_COOL, ROCK_LIGHT, STAIN = "m035_rock", "m035_rock_cool", "m035_rock_light", "m035_moss_stain"
MOSS, MOSS_SUN, MOSS_DEEP, MOSS_UNDER = "m035_moss", "m035_moss_sun", "m035_moss_deep", "m035_moss_under"
LEAF, LEAF_YOUNG, LEAF_DEEP = "m035_leaf", "m035_leaf_young", "m035_leaf_deep"
PETAL, POLLEN = "m035_petal", "m035_pollen"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low specular). Stage 4 (M035_spec.md "Stage 4"):
# Pass 1: K.calibrate on the kit test dome against TARGETS (rendered sRGB in brackets): rock #938380 (185,160,149),
# cool #6F6A70 (139,129,130), light #9E8D89 (200,172,159), stain #546330 (98,114,48), moss #7A911B (148,174,27), sun
# #A6AE07 (207,212,10; "vivid": the green filter drops it), deep #4E6C16 (90,125,22), under #5B4E3B (114,95,71), leaf
# #5E8B05 (111,166,9), young #9AAD05 (191,210,9), leaf deep #376204 (62,113,8), petal #C1C7CA (245,245,238), pollen
# #B1A100 (223,197,36).
# Pass 2 (f34_sheet / front_sheet render, floor hidden, against the sheet's f34 class medians; linear gains): rock
# x(1.37, 1.27, 1.24) (ours #A79086 against #BFA194) on rock, cool and light; cap x(1.09, 1.12, 0.5) (#9AAE17
# against #A1B809); leaf and leaf deep x(1.04, 1.35, 0.3), leaf young x(1.04, 1.15, 0.3) (foliage #5E6F14 against
# #608904: most of that gap is the leaves' own shade, so the young key gets less).
# Pass 3: moss_under x1.5 linear (#5B4E3B -> #6E5F49): the cap_under shot (from below, no fill light) rendered it
# near-black against the close-up's evenly lit #725E45; in the hero those faces are inside the rock or in shade.
# Fix round 1: leaves re-gained (linear R x0.9, G x0.62; young G x0.75): the new mound leaves face up into the key
# light, so the f34 foliage rendered #6EB30A against the sheet's #608904 with the old keys (#60A802, #9DB702,
# #387902). Moss x1.04 (#7F980E -> #849E0F): x1.08 (#89A40F) put the f34 cap 17 levels over the sheet while the rear,
# r34 and side caps stayed ~20 under (that gap is the studio key light behind the cap, not the key); rock light
# lifted (#B59D97 -> #C6AFA8) and mixed up to 35 % so its patches show (~10 levels over the base, was 3); petal a warm
# neutral white (#C1C7CA -> #D3D2CB; the old key was blue-grey); pollen brighter and a touch warmer (#B1A100 ->
# #CCAE00) with low specular, so the light's white share is smaller against it (it rendered at sat 0.76).
PALETTE = {
    ROCK: ("#A8928D", 0.9, False),
    ROCK_COOL: ("#81767C", 0.9, False),
    ROCK_LIGHT: ("#C6AFA8", 0.9, False),
    STAIN: ("#546330", 0.95, True),
    MOSS: ("#849E0F", 0.9, True),
    MOSS_SUN: ("#ABB604", 0.9, True),
    MOSS_DEEP: ("#51720B", 0.9, True),
    MOSS_UNDER: ("#6E5F49", 0.95, False),
    LEAF: ("#5B8702", 0.85, True),
    LEAF_YOUNG: ("#95A102", 0.85, True),
    LEAF_DEEP: ("#346002", 0.85, True),
    PETAL: ("#D3D2CB", 0.7, False),
    POLLEN: ("#CCAE00", 0.7, True),
}
# calibration targets (spec 5.4: rendered medians of unshadowed regions: the exploded parts, the part list and the
# close-ups). The rock keys use "all" (K.sample's stone filter drops sat > 0.18, and this warm rock is sat 0.20).
TARGETS = {ROCK: ((0xBC, 0xA1, 0x95), "all"), ROCK_COOL: ((0x8C, 0x81, 0x82), "all"),
           ROCK_LIGHT: ((0xC9, 0xAE, 0xA0), "all"), STAIN: ((0x64, 0x74, 0x30), "green"),
           MOSS: ((0x98, 0xB1, 0x1B), "green"), MOSS_SUN: ((0xCE, 0xD3, 0x09), "vivid"),
           MOSS_DEEP: ((0x5D, 0x80, 0x16), "green"), MOSS_UNDER: ((0x72, 0x5E, 0x45), "brown"),
           LEAF: ((0x72, 0xA9, 0x07), "green"), LEAF_YOUNG: ((0xBF, 0xD3, 0x08), "green"),
           LEAF_DEEP: ((0x3F, 0x73, 0x06), "green"), PETAL: ((0xF5, 0xF5, 0xEE), "all"),
           POLLEN: ((0xE0, 0xC4, 0x11), "vivid")}
SPEC = {}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    _spec()


def _spec():
    for m in bpy.data.materials:
        if not m.name.startswith("FB_m035_") or not m.node_tree:
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
_tri = m033._tri
_mottle = m033._mottle
_hull = m033._hull
_ring_pts = m033._ring_pts
_place = m033._place


def _q(t, steps=3):
    t = max(0.0, min(1.0, t))
    return round(t * steps) / steps


# ---- main rock: masses A and B (spec 1.4, 2.1, 2.2) --------------------------------------------------------------------
# rings (height fraction, radius fraction, points), bottom up. A: a barrel dome, widest at h .47, a broad level crown
# (the top ring is coplanar: one big crown polygon). B: the lower left mass.
# Fix round 1: the foot pulled in a little (A 0.66/0.85 -> 0.62/0.79, B 0.76/0.96 -> 0.70/0.89) toward 0.70-0.80 at
# h .1-.15, and the shoulder let out (A's 0.91 ring 0.82 -> 0.90, B's 0.80 ring 0.84 -> 0.93) toward >= 0.78 at h .8.
# Pulling the foot in further (A 0.60/0.74, B 0.66/0.82) turned the squat barrel into a ball on a stalk in the f34.
A_RINGS = ((0.0, 0.66, 8), (0.14, 0.85, 9), (0.46, 1.0, 9), (0.76, 0.97, 8), (0.91, 0.90, 6), (1.0, 0.50, 4))
B_RINGS = ((0.0, 0.76, 7), (0.2, 0.96, 8), (0.52, 1.0, 8), (0.80, 0.93, 6), (1.0, 0.48, 3))
# name -> base centre (x, y), size (W, D, height above z0), bottom z0, rings, jitter, lean (fraction of the radius the
# crown drifts), yaw (deg), cuts (plane normal, distance from (0, 0, 0.45 T): the cleft's two flat walls, A's left
# flank and B's front, meeting in a V about 105 deg open), seed
MASSES = {
    "A": dict(c=(0.6, -0.1), size=(7.6, 9.2, 6.45), z0=-0.05, rings=A_RINGS, jit=0.11, lean=(0.0, 0.0), yaw=0.0,
              cuts=(((-1.0, -0.12, 0.18), 3.0),), y_taper=(0.36, 0.16), seed=35101),
    "B": dict(c=(-2.3, 0.2), size=(4.8, 6.8, 5.5), z0=-0.08, rings=B_RINGS, jit=0.10, lean=(0.14, 0.0), yaw=0.0,
              cuts=(((-0.15, -1.0, 0.12), 2.4),), seed=35102),
}
ROCK_INFO = {}


def _cut(pts, cuts, zc):
    """Flatten a side of the point cloud: every point beyond a plane (unit normal n, distance d from (0, 0, zc)) is
    moved onto it, so the hull gets one big flat facet there (the cleft's two walls: A's left flank, B's front)."""
    for n, d in cuts:
        n = Vector(n).normalized()
        for p in pts:
            s = (p - Vector((0.0, 0.0, zc))).dot(n) - d
            if s > 0:
                p -= n * s
                p.z = max(0.0, p.z)
    return pts


def _mass(a, name):
    mp = MASSES[name]
    W, D, T = mp["size"]
    rng = random.Random(mp["seed"])
    pts = _ring_pts(rng, mp["rings"], W / 2, D / 2, T, mp["jit"], mp["lean"])
    # the side cell's trapezoid: the depth narrows toward the crown faster than the width; fix round 1: more at the
    # front than the back (the side cell's back shoulder stays broad: profile 0.77 / 0.61 at f .80 / .85)
    tp = mp.get("y_taper", 0.0)
    tf, tb = tp if isinstance(tp, tuple) else (tp, tp)
    for p in pts:
        p.y *= 1.0 - (tf if p.y < 0 else tb) * (p.z / T) ** 2
    pts = _cut(pts, mp.get("cuts", ()), 0.45 * T)
    vs = _hull(a, pts, ROCK)
    _place(a.bm, vs, Matrix.Translation((mp["c"][0], mp["c"][1], mp["z0"]))
           @ Matrix.Rotation(math.radians(mp["yaw"]), 4, "Z"))
    ROCK_INFO[name] = dict(faces=len(_faces(vs)), verts=len(vs))
    return vs


# Rock colour (spec 5.3, 5.5): whole facets, by position only. Broad noise patches -> rock_cool (mixed up to 33 %);
# patches on the upper half -> rock_light (up to 25 %); Tint mottling per original facet.
COOL = dict(scale=0.20, level=0.08, width=0.30, mix=0.33, seed=35111)
LIGHT = dict(scale=0.24, level=0.10, width=0.30, mix=0.35, z0=3.0, seed=35112)
ROCK_MOTTLE = dict(amp=0.04, scale=0.3, seed=35121)


def _paint_rock(a, faces, seed=0, tint=1.0):
    nc = K.noise_field(COOL["scale"], COOL["seed"] + seed)
    nl = K.noise_field(LIGHT["scale"], LIGHT["seed"] + seed)
    for f in faces:
        c = f.calc_center_median()
        tc = _q((nc(c) - COOL["level"]) / COOL["width"])
        tl = _q((nl(c) - LIGHT["level"]) / LIGHT["width"]) if c.z > LIGHT["z0"] else 0.0
        if tc >= tl and tc > 0:
            key = K.mix_key(ROCK, ROCK_COOL, round(tc * COOL["mix"], 2))
        elif tl > 0:
            key = K.mix_key(ROCK, ROCK_LIGHT, round(tl * LIGHT["mix"], 2))
        else:
            key = ROCK
        f.material_index = a._mi(key)
    _mottle(a, faces, ROCK_MOTTLE["amp"], ROCK_MOTTLE["scale"], ROCK_MOTTLE["seed"] + seed, tint=tint)


# Moss stain (spec 5.3): olive moss in the cleft's foot and two lobed patches low on B's front-left faces. Ellipsoid
# blobs (centre, radii) plus a little noise. The faces in reach are first cut by level planes (STAIN_BANDS): big
# facets painted whole read as tall green spikes, and refined ones as long slivers; banded, the stain stays low on
# the faces with a broken, stepped top edge that differs facet to facet.
STAIN_BLOBS = (((-2.45, -2.6, 0.7), (0.95, 0.95, 1.5)),
               ((-3.85, -1.85, 0.8), (0.85, 0.85, 1.0)),
               ((-4.35, -0.45, 0.55), (0.7, 0.8, 0.85)))
STAIN_NOISE = dict(amp=0.15, scale=0.9, seed=35131)
STAIN_LEVEL, STAIN_WIDTH = 0.10, 0.30
STAIN_MIX = 0.8
STAIN_BANDS = (0.55, 1.1, 1.65)
STAIN_TOP = 1.65


def _stain_v(c):
    v = -1.0
    for p, r in STAIN_BLOBS:
        d = Vector(((c.x - p[0]) / r[0], (c.y - p[1]) / r[1], (c.z - p[2]) / r[2])).length
        v = max(v, 1.0 - d)
    n = noise.noise(c * STAIN_NOISE["scale"] + Vector((STAIN_NOISE["seed"] % 97, 3.1, 7.7)))
    return v + STAIN_NOISE["amp"] * n


def _stain(a):
    """Cut the faces in reach of the stain into level bands, then blend the stain over the low bands in 2 steps
    (genuinely a different material, so a short blend)."""
    bm = a.bm
    rock = K.part(a, "A") + K.part(a, "B")

    def near():
        return [f for f in _faces(K.part(a, "A") + K.part(a, "B"))
                if _stain_v(f.calc_center_median()) > STAIN_LEVEL - 0.45 and
                min(v.co.z for v in f.verts) < STAIN_TOP]
    for z in STAIN_BANDS:
        fs = near()
        geom = list({e for f in fs for e in f.edges}) + fs + list({v for f in fs for v in f.verts})
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, z), plane_no=(0, 0, 1))
    ng = [f for f in bm.faces if len(f.verts) > 3]
    if ng:
        bmesh.ops.triangulate(bm, faces=ng, quad_method="BEAUTY", ngon_method="BEAUTY")
    n = 0
    for f in near():
        c = f.calc_center_median()
        if c.z > STAIN_TOP:
            continue
        t = _q((_stain_v(c) - STAIN_LEVEL) / STAIN_WIDTH, 2)
        if t > 0:
            f.material_index = a._mi(K.mix_key(ROCK, STAIN, round(STAIN_MIX * t, 2)))
            n += 1
    ROCK_INFO["stain_faces"] = n


def _rock(a, stain=True):
    """A and B, painted, tagged (K.part) and stained. Returns the verts of both."""
    for name in ("A", "B"):
        vs = _mass(a, name)
        _paint_rock(a, _faces(vs), seed=0 if name == "A" else 7)
        K.tag_part(a, vs, name)
    if stain:
        _stain(a)
    return K.part(a, "A") + K.part(a, "B")


# ---- moss cap rosettes (spec 1.4 Moss Cap, 2.1) ------------------------------------------------------------------------
# Each rosette: an outline of `lobes` broad lobes (two corners each at 0.90-1.04 r, a shallow notch between lobes at
# 0.70-0.80 r); a top of radial ridges (a mid point on each lobe's axis at 0.55 r, 0.62 of the way up) rising to a
# raised centre, the notches dipping into valleys; a thin rim band; a flat underside fan. name -> centre (x, y), r, h
# (peak above the base), lobes, sink into what it sits on, the rosettes it sits on, yaw, seed. Conformed in this order.
ROSETTES = (
    ("M1", (-0.55, -0.62), 1.58, 1.10, 8, 0.06, (), 10.0, 35201),
    ("M3", (1.45, 0.10), 1.40, 0.95, 8, 0.07, (), 25.0, 35203),
    ("M4", (-1.60, 0.65), 1.18, 0.82, 7, 0.08, (), 5.0, 35204),
    ("M2", (0.35, 1.30), 1.40, 0.95, 8, 0.09, ("M1", "M3"), 40.0, 35202),
    ("M5", (0.10, 0.15), 1.05, 0.82, 7, 0.10, ("M1", "M2", "M3"), 15.0, 35205),
)
ROS_BAND = 0.18
ROS_MID = (0.55, 0.62)        # mid point radius fraction, height fraction of (h - band)
ROS_NOTCH_Z = 0.10            # notch top: this fraction of (h - band) above the band (a valley)
ROS_TIP_Z = 1.45              # lobe corners sit at this fraction of the band (fix round 1: 0.85 -> 1.45, no droop:
#                               the corners level with the notch tops, so the cap reads as low scalloped mats)
ROS_CORNER = 0.28             # lobe corners this fraction of a lobe step either side of the lobe axis (fix round 1:
#                               0.20 -> 0.28, blunter, broader lobe ends)
ROS_SCALE = 1.06              # fix round 1: rosette radii x this (a slightly larger footprint; f34 cap share 0.087)
CAP_MOTTLE = dict(amp=0.05, scale=0.8, seed=35211)
CAP_INFO = {}
ROS_PARTS = {}
PART_SINK_STEP = 0.09
ROS_DROP = 1.1               # no part of a rosette drapes more than this below its centre's seat


def _rosette(a, r, h, lobes, seed):
    """One rosette in its local frame, base at z 0. Returns its verts."""
    rng = random.Random(seed)
    bm = a.bm
    off = rng.uniform(0, 2 * math.pi)
    step = 2 * math.pi / lobes
    outline, axes = [], []
    for k in range(lobes):
        th = off + k * step + rng.uniform(-0.07, 0.07) * step
        axes.append(th)
        rl = r * rng.uniform(0.93, 1.04)
        for s_ in (-1, 1):
            outline.append((th + s_ * ROS_CORNER * step * rng.uniform(0.85, 1.15), rl * rng.uniform(0.94, 1.0), "tip"))
        outline.append((th + 0.5 * step + rng.uniform(-0.05, 0.05) * step, r * rng.uniform(0.70, 0.80), "notch"))
    top, bot = [], []
    for th, rr, kind in outline:
        if kind == "notch":
            zt = ROS_BAND + (h - ROS_BAND) * ROS_NOTCH_Z
        else:
            zt = ROS_BAND * ROS_TIP_Z * rng.uniform(0.9, 1.1)
        top.append(bm.verts.new((math.cos(th) * rr, math.sin(th) * rr, zt)))
        bot.append(bm.verts.new((math.cos(th) * rr * 0.95, math.sin(th) * rr * 0.95, 0.0)))
    mids = []
    for th in axes:
        mr = r * ROS_MID[0] * rng.uniform(0.92, 1.08)
        mids.append(bm.verts.new((math.cos(th) * mr, math.sin(th) * mr,
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
    ROS_PARTS[seed] = dict(pairs=list(zip(top, bot)), mids=mids, centre=centre, bc=bc)
    bmesh.ops.recalc_face_normals(bm, faces=cen_f + ridge_f + valley_f + rim_f + und_f)
    a._finish(vs, MOSS)
    # colour by place on the rosette (never by facing): the raised centre sun-yellow, the lobe ridges toward it, the
    # notch valleys deep green, the rim band half deep; the flat underside brown (a hard material edge). Each lobe gets
    # one of three shades along the rosette so neighbours differ (the sheet's lobes vary lime to yellow).
    sh = [rng.choice((0.0, 0.33, 0.67)) for _ in range(lobes)]
    for f in cen_f:
        f.material_index = a._mi(K.mix_key(MOSS, MOSS_SUN, 0.67))
    for k, f in enumerate(ridge_f):
        f.material_index = a._mi(K.mix_key(MOSS, MOSS_SUN, sh[k]))
    for i, f in enumerate(valley_f):
        k = i // 3
        f.material_index = a._mi(K.mix_key(MOSS, MOSS_SUN, round(sh[k] / 2, 2)) if i % 3 != 2
                                 else K.mix_key(MOSS_DEEP, MOSS, 0.5))
    for f in rim_f:
        f.material_index = a._mi(MOSS)
    for f in und_f:
        f.material_index = a._mi(MOSS_UNDER)
    _mottle(a, cen_f + ridge_f + valley_f + rim_f, CAP_MOTTLE["amp"], CAP_MOTTLE["scale"], CAP_MOTTLE["seed"] + seed)
    return vs


def _conform_rosette(rp, tree, fallback, c, sink):
    """K.conform for a rosette, without folds: each rim corner's top and bottom verts drop by the same amount (read
    under the top vert), and nothing drops more than ROS_DROP below the seat under the centre (so a lobe hanging over
    a steep flank or the cleft can't fold back through itself)."""
    def surf(x, y):
        o, d = Vector((x, y, 60.0)), Vector((0, 0, -1))
        h = tree.ray_cast(o, d, 200)
        if h[0] is None:
            h = fallback.ray_cast(o, d, 200)
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


def _cap(a, rock_vs, part=False):
    """The rosettes conformed one by one onto the rock and the rosettes under them. part: the MossCap part, whose
    rosettes have no rock to sink into: the ones seated on the rock are staggered PART_SINK_STEP apart in depth, so
    their flat undersides never lie a few hundredths apart (the union left slivers there)."""
    placed = {}
    for i, (name, (x, y), r, h, lobes, sink, on, yaw, seed) in enumerate(ROSETTES):
        if part and not on:
            sink += PART_SINK_STEP * i
        vs = _rosette(a, r * ROS_SCALE, h, lobes, seed)
        _place(a.bm, vs, Matrix.Translation((x, y, 0.0)) @ Matrix.Rotation(math.radians(yaw), 4, "Z"))
        tree = K.bvh_of(rock_vs + [v for k in on for v in placed[k]])
        _conform_rosette(ROS_PARTS[seed], tree, K.bvh_of(rock_vs), Vector((x, y, 0.0)), sink)
        placed[name] = vs
        zs = [v.co.z for v in vs]
        CAP_INFO[name] = dict(z=(round(min(zs), 2), round(max(zs), 2)), faces=len(_faces(vs)))
    return [v for vs in placed.values() for v in vs]


# ---- parts -------------------------------------------------------------------------------------------------------------
def main_rock_part(a):
    ROCK_INFO.clear()
    _rock(a)


def moss_cap_part(a):
    """The cap as it lies on the crown (the exploded draws it draped like an umbrella): conformed to the rock, then
    the rock is taken away."""
    CAP_INFO.clear()
    for name in ("A", "B"):
        _mass(a, name)
    rock = list(a.bm.verts)
    _cap(a, rock, part=True)
    bmesh.ops.delete(a.bm, geom=[v for v in rock if v.is_valid], context="VERTS")


def hero_stone(a):
    ROCK_INFO.clear()
    CAP_INFO.clear()
    rock = _rock(a)
    _cap(a, rock)


# ---- small rocks (spec 1.4 Small Rock, 2.3) ----------------------------------------------------------------------------
SR_RINGS = ((0.0, 0.88, 6), (0.33, 1.0, 7), (0.72, 0.78, 5), (1.0, 0.34, 3))
PEB_RINGS = ((0.0, 0.88, 5), (0.42, 1.0, 5), (1.0, 0.36, 3))
SR_HW = 0.66
VARIANT = {"A": 1.8, "B": 1.5, "C": 1.2, "P": 0.5}
# label -> variant, centre (x, y), width, yaw (deg), moss on top, seed
SMALL_ROCKS = (
    ("R1", "A", (-4.6, -2.2), 1.8, 15.0, False, 35301),
    ("R2", "A", (3.4, -3.6), 1.7, 40.0, True, 35302),
    ("R3", "C", (5.2, -3.3), 1.2, 70.0, False, 35303),     # fix round 1: (5.0, -2.4), out of F6's new seat
    ("R4", "B", (3.0, 4.2), 1.5, 0.0, True, 35304),      # fix round 1: (3.6, 3.6), out of F5b's seat
    ("R5", "B", (-3.4, 3.8), 1.5, 110.0, True, 35305),
    ("P1", "P", (-3.3, -3.6), 0.5, 30.0, False, 35306),
)
SR_MOSS = dict(level=0.62, width=0.22, amp=0.12, scale=1.2)
SR_INFO = {}


def _small_rock(a, var, w, seed, xy=(0.0, 0.0), yaw=0.0, moss=False):
    rng = random.Random(seed)
    rings = PEB_RINGS if var == "P" else SR_RINGS
    h = w * SR_HW * (0.9 if var == "P" else 1.0)
    pts = _ring_pts(rng, rings, w / 2, w * 0.46, h, 0.12)
    vs = _hull(a, pts, ROCK)
    _place(a.bm, vs, Matrix.Translation((xy[0], xy[1], 0.0)) @ Matrix.Rotation(math.radians(yaw), 4, "Z"))
    _paint_rock(a, _faces(vs), seed=seed % 50, tint=1.0 + rng.uniform(-0.06, 0.06))
    if moss:
        # whole top facets (the rock's facets are already small against a patch): stain on the crown, half-mixed on
        # the faces round it, by height plus a little noise
        nf = K.noise_field(SR_MOSS["scale"], seed)
        for f in _faces(vs):
            c = f.calc_center_median()
            t = _q((c.z / h + SR_MOSS["amp"] * nf(c) - SR_MOSS["level"]) / SR_MOSS["width"], 2)
            if t > 0:
                f.material_index = a._mi(K.mix_key(ROCK, STAIN, t))
    return vs


def small_rock_part(a):
    _small_rock(a, "A", VARIANT["A"], 35301)


# ---- foliage clusters (spec 1.4 Foliage Cluster, 2.3) ------------------------------------------------------------------
# Leaves: own closed round leaves (_leaf, 12 tris: cupped top with a raised midrib, flat underside), 0.5-0.75 long.
# A cluster is one dense rounded mound (low, small) or 3 overlapping mounds stacked up the flank (tall): leaves laid
# over a dome, faces out and up, tips up (_mound), round a deep-green core (_core); colour by height on the dome (low
# deep -> leaf -> top young). Every piece touches the ground, the stone, a rock or a leaf (_Contact). Fix round 1.
LEAF_W = 1.0             # width / length (fix round 1: 0.86 -> 1.0, plump round leaves like the part list's)
LEAF_FOLD, LEAF_CURL, LEAF_THICK, LEAF_CAMBER = 0.16, 0.10, 0.0, 0.24   # fix round 1: flat underside (12 tris)
LEAF_ROLL = 0.40          # each leaf rolls up to this much (rad) about its own axis, so side-on leaves still show a face
# kind -> leaf count, leaf length (studs), mound radius (frac of w). Every cluster is built from dense rounded mounds
# (_mound); a tall cluster is 2-3 mounds stacked up the rock's flank (TALL_MOUNDS).
KINDS = {"low": dict(n=12, L=(0.62, 0.76), R=0.36),
         "small": dict(n=7, L=(0.48, 0.58), R=0.34),
         "tall": dict(n=0, L=(0.62, 0.76), R=0.40)}
# name -> kind, centre (x, y), w, h, flower, hugs the rock (a ring round the base: the centre is slid along the line
# from ROCK_CENTRE until it sits HUG_MIN-HUG_MAX x its mound radius off the rock; tall ones stack their mounds up the
# flank), seed.
# Fix round 1: F6 moved forward to the front-right corner (the side cell's mid-flank is bare rock); the back and left
# clusters hug the base (the top view's ring).
CLUSTERS = (
    ("F1", "low", (-1.8, -4.3), 2.09, 1.3, True, False, 35401),
    ("F2", "low", (-3.4, -3.0), 1.76, 1.4, False, False, 35402),
    ("F3", "tall", (-5.1, -0.6), 2.0, 2.6, True, True, 35403),
    ("F4", "tall", (-4.2, 2.6), 1.9, 2.3, False, True, 35404),
    ("F5a", "tall", (1.8, 4.6), 2.1, 2.8, True, True, 35405),
    ("F5b", "tall", (4.0, 3.3), 1.7, 3.0, False, True, 35406),
    ("F6", "tall", (5.0, -2.3), 1.85, 3.2, False, True, 35407),
    ("F7", "small", (2.6, -3.7), 1.10, 0.8, False, False, 35408),
    ("F8", "low", (-1.6, 4.6), 1.9, 1.4, False, True, 35409),
    ("F9", "small", (-2.55, -2.65), 1.2, 1.0, False, False, 35410),     # the moss tuft in the cleft's foot
)
ROCK_CENTRE = (-0.4, 0.0)
DRESS_DY = -0.3           # the dressing sits a little forward of the layout table (the side cell's rock stands centred in it)
HUG_MIN, HUG_MAX = 0.3, 1.0   # a hugging cluster's ground mound centre stands between these x its radius out from
HUG_Z = (0.45, 1.2, 2.0, 2.8, 3.4)   # the rock's widest section along its azimuth (sampled at these heights)
HUG_MAX_OF = {"F3": 2.0, "F6": 2.0}  # the columns at the ends of the front silhouette keep their table place
MOUND_Z = 0.40            # a ground mound's centre is this fraction of its radius above the ground
MOUND_TH = (4.0, 98.0)    # the dome band the leaves are laid over (deg from the top)
LEAF_UP = 0.65            # a leaf's face is tilted from straight out of the dome this much of the way to straight up
CORE_R = 0.62             # each low or tall mound has a deep-green heart this fraction of its radius (_core)
TALL_MOUNDS = ((1.0, 9), (0.85, 8), (0.72, 7))   # tall cluster mounds bottom up: (radius frac of R, leaves)
HUG_STRETCH = 1.3         # a hugging cluster's ground mound is drawn out this much along the rock (the top view's ring)
UPPER_LEAN = 0.45         # an upper mound sits this far of the way from straight over the ground mound to the flank
UPPER_OFF = 0.70         # an upper mound's centre stands this fraction of its radius off the rock surface
OPEN_ARC = 110.0          # a hugging mound's leaves lie within this many degrees of straight out from the rock
CONTACT = 0.03            # every leaf / flower ends within this of the ground, the stone, a small rock or a leaf
CLUSTER_TINT = 0.04
LEAF_MOTTLE = dict(amp=0.04, scale=0.9, seed=35411)
FLOWER_R = 0.24          # petal length (flower about 0.45-0.5 across)
FLOWER_TILT = 0.50       # the flower's face tips toward its facing direction by this much (rad; fix round 1: 0.30)
FLOWER_FACE = {"F5a": math.pi / 2}       # flowers face the front (-Y) unless named here (F5a faces the rear, +Y)
CLUSTER_INFO = {}
CONTACT_INFO = {}


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


class _Guard:
    """Keeps a dressing piece out of the stone (and the small rocks): a piece whose verts go more than `allow` inside
    is moved out along the surface normal at its deepest vert (horizontal part, never down); then lifted to stand on
    or above the ground."""

    def __init__(self, tree):
        self.tree = tree
        self.moved = 0

    def push(self, vs, allow, clearance=0.02):
        if self.tree is None:
            return
        for _ in range(5):
            worst, nrm = 0.0, None
            for v in vs:
                loc, n, _, d = self.tree.find_nearest(v.co)
                if loc is None or n is None:
                    continue
                if (v.co - loc).dot(n) < 0 and d > worst:
                    worst, nrm = d, n
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


# leaf outline (fraction of the length along, fraction of the half-width across) from the stem to the tip on one side
LEAF_OUTLINE = ((0.16, 0.74), (0.66, 1.0))    # fix round 1: widest further out, so the tip is blunt (about 115 deg)
LEAF_RIDGE = ((0.30, 1.0), (0.70, 0.75))      # midrib points (fraction along, fraction of the camber)


def _leaf(a, base, L, key, yaw, pitch, width=None, camber=None, thick=None, fold=None, curl=None, roll=0.0):
    """One chunky leaf (14 tris, a closed solid): a broad ovate outline with a pointed tip, its edges cupped up (fold),
    a raised two-point midrib on top (so the top reads as two broad facets either side of a ridge, not a pyramid), and
    one point underneath for its thickness. base = the stem end; yaw about Z; pitch = rise of the leaf (rad)."""
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
    ring = [(0.0, 0.0)] + [(f * L, -h * W) for f, h in LEAF_OUTLINE] + [(L, 0.0)] +            [(f * L, h * W) for f, h in reversed(LEAF_OUTLINE)]
    o = [put(x, y, 0.0) for x, y in ring]
    f1 = put(LEAF_RIDGE[0][0] * L, 0.0, cam * LEAF_RIDGE[0][1])
    f2 = put(LEAF_RIDGE[1][0] * L, 0.0, cam * LEAF_RIDGE[1][1])
    fs = [(o[0], o[1], f1), (o[1], o[2], f1), (f1, o[2], f2), (o[2], o[3], f2), (o[3], o[4], f2), (f2, o[4], f1),
          (o[4], o[5], f1), (o[5], o[0], f1)]
    faces = [bm.faces.new(q) for q in fs]
    n = len(o)
    if th > 0:
        bk = put(0.5 * L, 0.0, -th)
        faces += [bm.faces.new((bk, o[(i + 1) % n], o[i])) for i in range(n)]
        vs = o + [f1, f2, bk]
    else:
        # fix round 1 (budget): a flat underside fan from the stem point (12 tris a leaf, not 14); the cupped top and
        # its raised midrib still give the leaf its body
        faces += [bm.faces.new((o[0], o[i + 1], o[i])) for i in range(1, n - 1)]
        vs = o + [f1, f2]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    a._finish(vs, key)
    return vs


def _flower(a, loc, r, seed, guard=None, face=-math.pi / 2):
    """Five broad white petals round a domed yellow centre, the face tipped toward `face` (an azimuth; the front by
    default). Each petal and the centre are their own closed shells (each petal's base set 0.03 out along its own
    direction, so no two coincide)."""
    rng = random.Random(seed)
    y0 = rng.uniform(0, 2 * math.pi)
    out = []
    for k in range(5):
        yaw = y0 + 2 * math.pi * k / 5
        d = Vector((math.cos(yaw), math.sin(yaw), 0.0))
        pitch = 0.10 - FLOWER_TILT * math.cos(yaw - face)
        b = Vector(loc) + d * 0.03 + Vector((0, 0, 0.004 * k))
        vs = _leaf(a, tuple(b), r, PETAL, yaw, pitch, width=1.0, camber=0.08, thick=0.08, fold=0.06, curl=0.08)
        out += vs
    cvs = a.cyl(r * 0.36, r * 0.22, r * 0.34, sides=6, loc=(loc[0], loc[1], loc[2] - 0.05), mat=POLLEN, tint=1.0)
    caps = [f for f in _faces(cvs) if len(f.verts) > 4]
    if caps:
        bmesh.ops.triangulate(a.bm, faces=caps, quad_method="BEAUTY", ngon_method="BEAUTY")
    out += [v for v in cvs if v.is_valid]
    return out


def _surface(stone, xy, out, z, fallback):
    """Where the line through xy along -out (horizontal) first meets the stone at height z, coming in from outside."""
    if stone is None or out is None:
        return fallback
    o = Vector((xy[0], xy[1], z)) + out * 9.0
    hit = stone.ray_cast(o, -out, 20.0)
    return Vector((hit[0].x, hit[0].y, z)) if hit[0] is not None else fallback


def _mound(rng, centre, R, n, Lr, ct, out=None, th=MOUND_TH, stretch=1.0):
    """One dense rounded mound (fix round 1): n leaves laid over a dome of radius R round `centre`, like the sheet's
    clumps: each leaf's middle on the dome, its face pointing out of the dome and its tip up toward the dome's top
    (flared out a little), so the clump shows leaf faces from every side and reads as one solid rounded mass. Points
    by a golden-angle spiral over polar angles th (deg from the top, spaced evenly in angle so the crown is covered
    too); a mound against the rock (`out`) keeps to OPEN_ARC either side of straight out and is drawn out `stretch`
    times along the rock (the top view's ring). Returns [(base, L, yaw, pitch, colour t)]: low leaves deep, top ones
    young."""
    plan = []
    off = rng.random()
    oang = math.atan2(out.y, out.x) if out is not None else rng.uniform(0, 2 * math.pi)
    side = Vector((-math.sin(oang), math.cos(oang), 0.0))
    c0, c1 = math.cos(math.radians(th[0])), math.cos(math.radians(th[1]))
    for i in range(n):
        fi = (i + 0.5) / n
        theta = math.acos(c0 + (c1 - c0) * fi)          # even area over the band
        u = (i * 0.6180339 + off) % 1.0
        phi = oang + (math.radians(OPEN_ARC) * (2.0 * u - 1.0) if out is not None else 2.0 * math.pi * u)
        phi += rng.uniform(-0.12, 0.12)
        theta += rng.uniform(-0.08, 0.08)
        nrm = Vector((math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)))
        # the leaf's face turns partly up as well as out (LEAF_UP), so the clump shows leaf faces from above as well
        # as from the side; the tip flares out a little
        tl = theta * LEAF_UP
        tan = Vector((-math.cos(tl) * math.cos(phi), -math.cos(tl) * math.sin(phi), math.sin(tl)))
        L = rng.uniform(*Lr)
        pitch = tl + rng.uniform(0.0, 0.25)
        p = nrm * R * rng.uniform(0.9, 1.05)
        if stretch != 1.0 and out is not None:
            p += side * (p.dot(side) * (stretch - 1.0))
        base = centre + p - tan * L * 0.45
        # colour by height on the dome (low outer leaves deep, top ones young), never by facing
        t = ct[0] + (ct[1] - ct[0]) * (1.0 - (theta - math.radians(th[0])) / math.radians(th[1] - th[0]))
        plan.append((base, L, phi + math.pi, pitch, max(0.0, min(1.0, t))))
    return plan


def _core(a, centre, r, seed, side=None, stretch=1.0):
    """A mound's hidden heart (12 tris, a closed hexagonal bipyramid in deep leaf green): seen through the gaps
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
    a._finish(vs, K.mix_key(LEAF, LEAF_DEEP, 0.6))
    # its upper cone (above the ring, by position) shows through the crown's gaps from above: plain leaf there
    for f in fs[0::2]:
        f.material_index = a._mi(K.mix_key(LEAF, LEAF_DEEP, 0.2))
    return vs


class _Contact:
    """Keeps every leaf and flower touching what is already placed: the ground, the stone, the small rocks and the
    leaves accepted before it (so every shell has a chain of contact down to the ground or the stone). A piece further
    than CONTACT from all of that is slid toward its nearest point until it is 0.015 away."""

    def __init__(self, coords, polys):
        self.coords = list(coords) + [Vector((-30, -30, 0)), Vector((30, -30, 0)), Vector((30, 30, 0)),
                                      Vector((-30, 30, 0))]
        k = len(self.coords)
        self.polys = list(polys) + [[k - 4, k - 3, k - 2, k - 1]]
        self.moved = 0
        self.worst = 0.0

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


def _cluster(a, name, kind, xy, w, h, flower, hug, seed, guard=None, stone=None, contact=None):
    """A cluster of dense rounded leaf mounds. hug: a cluster in the ring round the base: its centre is slid to sit
    HUG_MIN-HUG_MAX x its radius off the rock; a tall one stacks its upper mounds up the flank (UPPER_LEAN), their
    leaves spread over the open side (never into the rock)."""
    rng = random.Random(seed)
    kp = KINDS[kind]
    tint = 1.0 + rng.uniform(-CLUSTER_TINT, CLUSTER_TINT)
    c0 = Vector((xy[0], xy[1], 0.0))
    R0 = kp["R"] * w
    out = None
    if hug:
        # seat the bottom mound against the rock's outline as seen from above (its widest section along this
        # azimuth), so the ring shows round the rock in the top view and the clumps tuck under the bulge
        out = Vector((xy[0] - ROCK_CENTRE[0], xy[1] - ROCK_CENTRE[1], 0.0)).normalized()
        best = None
        for z in HUG_Z:
            s = _surface(stone, ROCK_CENTRE, out, z, None)
            if s is not None:
                d = (s - Vector((ROCK_CENTRE[0], ROCK_CENTRE[1], z))).length
                best = d if best is None else max(best, d)
        if best is not None:
            # keep the layout table's place, but no further out than HUG_MAX x R0 beyond the outline (a ring hugging
            # the base) and no further in than HUG_MIN x R0 (the ground mound mustn't bury itself in the rock)
            rc = Vector((ROCK_CENTRE[0], ROCK_CENTRE[1], 0.0))
            d = (c0 - rc).length - best
            c0 = rc + out * (best + max(HUG_MIN * R0, min(HUG_MAX_OF.get(name, HUG_MAX) * R0, d)))
    plan, mounds = [], []
    if kind == "tall":
        nm = 2 if h < 2.3 else 3
        rs = [R0 * TALL_MOUNDS[j][0] for j in range(nm)]
        z0, z1 = MOUND_Z * rs[0], h - rs[-1] - 0.22
        for j in range(nm):
            fj = j / (nm - 1)
            z = z0 + (z1 - z0) * fj
            if j == 0:
                centre = c0 + Vector((0, 0, z))
            else:
                # stacked over the ground mound, leaning UPPER_LEAN of the way in to rest against the flank (the
                # sheet's columns stand at the silhouette's ends, not pressed flat on the rock)
                s = _surface(stone, c0, out, z, c0 + Vector((0, 0, z)))
                rest = Vector((s.x, s.y, z)) + (out * rs[j] * UPPER_OFF if out is not None else Vector())
                up = c0 + Vector((0, 0, z))
                if out is not None and (rest - up).dot(out) > 0:
                    centre = rest            # the flank bulges out past the column here: rest on it
                else:
                    centre = up.lerp(rest, UPPER_LEAN)
            nj = TALL_MOUNDS[j][1]
            st = HUG_STRETCH if (j == 0 and out is not None) else 1.0
            nj += 1 if st > 1.0 else 0
            mounds.append((centre, nj, rs[j], st))
            plan += _mound(rng, centre, rs[j], nj, kp["L"], (0.5 * fj, min(1.0, 0.5 * fj + 0.75)), out, stretch=st)
    else:
        centre = c0 + Vector((0, 0, MOUND_Z * R0))
        st = HUG_STRETCH if out is not None else 1.0
        n = kp["n"] + (1 if st > 1.0 else 0)
        mounds.append((centre, n, R0, st))
        plan = _mound(rng, centre, R0, n, kp["L"], (0.0, 1.0), out, stretch=st)
    side = Vector((-out.y, out.x, 0.0)) if out is not None else None
    leaves, top = [], 0.0
    if CORE_R and kind != "small":
        for k, (centre, _, r, st) in enumerate(mounds):
            vs = _core(a, centre, CORE_R * r, seed + 31 * k, side, st)
            if guard:
                guard.push(vs, 0.05)
            _lift(vs)
            if contact:
                contact.attach(vs, guard)
            _mottle(a, _faces(vs), LEAF_MOTTLE["amp"], LEAF_MOTTLE["scale"], LEAF_MOTTLE["seed"] + seed, tint=tint)
    for base, L, yaw, pitch, ct in plan:
        vs = _leaf(a, tuple(base), L, _leaf_key(round(_q(ct, 4), 2)), yaw, pitch,
                   roll=rng.uniform(-LEAF_ROLL, LEAF_ROLL))
        if guard:
            guard.push(vs, 0.05)
        _lift(vs)
        if contact:
            contact.attach(vs, guard)
        _mottle(a, _faces(vs), LEAF_MOTTLE["amp"], LEAF_MOTTLE["scale"], LEAF_MOTTLE["seed"] + seed, tint=tint)
        top = max(top, max(v.co.z for v in vs))
        leaves.append(vs)
    fl = None
    if flower:
        face = FLOWER_FACE.get(name, -math.pi / 2)
        # on the top mound's shoulder on the side it faces (and out from the rock), sitting on the leaves: the sheet's
        # flowers show whole, not sunk among the leaves
        mt, nt, rt, _ = mounds[-1]
        fd = Vector((math.cos(face), math.sin(face), 0.0))
        p = mt + fd * 0.45 * rt + (out * 0.25 * rt if out is not None else Vector())
        p.z = mt.z + 0.95 * rt
        fl = _flower(a, tuple(p), FLOWER_R, seed + 7, face=face)
        if guard:
            guard.push(fl, 0.02)
        if contact:
            contact.attach(fl, guard)
    allv = [v for vs in leaves for v in vs] + (fl or [])
    xs, ys, zs = ([v.co[i] for v in allv] for i in range(3))
    fc = None
    if fl:
        fc = sum((v.co for v in fl), Vector()) / len(fl)
        fc = [round(fc.x, 2), round(fc.y, 2), round(fc.z, 2)]
    CLUSTER_INFO[name] = dict(leaves=len(leaves), mounds=len(mounds), flower=fc,
                              centre=[round(c0.x, 2), round(c0.y, 2)],
                              size=[round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2), round(max(zs), 2)])
    return allv


def foliage_part(a):
    CLUSTER_INFO.clear()
    _cluster(a, "part", "low", (0.0, 0.0), 1.9, 1.3, True, None, 35401, contact=_Contact([], []))


def dressing(a, stone_tree):
    """Small rocks first (kept clear of the stone), then the clusters (kept out of the stone and the rocks, every leaf
    and flower touching the ground, the stone, a rock or a leaf already placed)."""
    SR_INFO.clear()
    CLUSTER_INFO.clear()
    guard = _Guard(stone_tree)
    rocks = []
    for lab, var, xy, w, yaw, moss, seed in SMALL_ROCKS:
        xy = (xy[0], xy[1] + DRESS_DY)
        vs = _small_rock(a, var, w, seed, xy, yaw, moss)
        guard.push(vs, 0.0, clearance=0.03)
        zs = [v.co.z for v in vs]
        c = sum((v.co for v in vs), Vector()) / len(vs)
        SR_INFO[lab] = dict(xy=(round(c.x, 2), round(c.y, 2)), h=round(max(zs), 2), faces=len(_faces(vs)))
        rocks += vs
    # leaves are kept out of the stone and of the small rocks
    coords, polys = _tree_data(stone_tree, rocks)
    sb = BVHTree.FromPolygons(coords, polys)
    g2 = _Guard(sb)
    con = _Contact(coords, polys)
    for name, kind, xy, w, h, flower, hug, seed in CLUSTERS:
        xy = (xy[0], xy[1] + DRESS_DY)
        _cluster(a, name, kind, xy, w, h, flower, hug, seed, g2, stone_tree, con)
    CONTACT_INFO.update(moved=con.moved, worst_gap=round(con.worst, 3))
    return guard.moved + g2.moved


STONE_POLYS = {}


def _tree_data(tree, extra_vs):
    coords, polys = [Vector(c) for c in STONE_POLYS["coords"]], [list(p) for p in STONE_POLYS["polys"]]
    idx = {}
    for f in _faces(extra_vs):
        p = []
        for v in f.verts:
            if v not in idx:
                idx[v] = len(coords)
                coords.append(v.co.copy())
            p.append(idx[v])
        polys.append(p)
    return coords, polys


def _stone_tree(o):
    """BVH of the finished stone in the build frame (mesh coords + o[OFF])."""
    off = Vector(o[OFF])
    coords = [v.co + off for v in o.data.vertices]
    polys = [list(p.vertices) for p in o.data.polygons]
    STONE_POLYS["coords"], STONE_POLYS["polys"] = coords, polys
    return BVHTree.FromPolygons(coords, polys)


# ---- make / finish (m033's pipeline with this model's offset key) ------------------------------------------------------
NOTES = {
    HERO: "Mossy boulder: squat broad-faceted warm grey-pink boulder of two masses with a deep cleft down the front-left "
          "face, a leafy lime moss cap of five lobed rosettes on the crown, an olive moss stain in the cleft, five small "
          "faceted rocks and a pebble and nine round-leaf foliage clusters (three white flowers) round the left, back and "
          "right of the foot; the stone is one closed shell, every rock, leaf, petal and flower centre its own. No VFX",
    ROCK_P: "Main Rock (reusable): squat barrel-dome warm grey-pink boulder of two faceted masses with a cleft down the "
            "front-left and a low olive moss stain; flat underside",
    CAP_P: "Moss Cap (reusable): five lobed lime moss rosettes as they lie on a boulder crown; flat brown underside",
    SMALL_P: "Small Rock (reusable): squat faceted warm grey-pink rock, broad flat faces, flat underside",
    FOL_P: "Foliage Cluster (reusable): chunky round-leaf plant in tiers (deep outer, lime inner leaves) with one white "
           "five-petal flower; every leaf and petal its own closed piece",
}
COLLISION = {HERO: "hull", ROCK_P: "hull", CAP_P: "none", SMALL_P: "hull", FOL_P: "none"}
UNION_RETRIES = m033.UNION_RETRIES


def _finish(o):
    o[OFF] = list(Vector(o[OFF]) + m012._bottom_centre(o))
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
        o[OFF] = list(Vector(o[OFF]) + m012._bottom_centre(o))
        res = M.finish(o, union=False, uv=UV)
    return res


def _recentre(o):
    bc = m012._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


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
    _recentre(o)
    M.smart_uv(o, **UV)
    return {"split": split, "forced": forced, "uv_cut": m012._uv_unfold(o)}


def _kill_slivers(o, lim=POLISH_LIM):
    """Last resort after _polish for a sliver its flips, collapses and nudges couldn't open (a cap seam where three
    rosettes meet): collapse each one's shortest edge; keep the result only if the mesh stays closed and manifold
    with no new sliver. Returns how many went."""
    import m011 as _m
    n = 0
    for _ in range(6):
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bad = [f for f in bm.faces if _m._fmin(f) < math.radians(lim)]
        if not bad:
            bm.free()
            break
        ok = False
        for how in ("rotate", "collapse", "dissolve"):
            b2 = bm.copy()
            b2.faces.ensure_lookup_table()
            f = [x for x in b2.faces if _m._fmin(x) < math.radians(lim)][0]
            es = sorted(f.edges, key=lambda x: x.calc_length())
            if how == "rotate":
                bmesh.ops.rotate_edges(b2, edges=[es[-1]], use_ccw=False)
            elif how == "collapse":
                bmesh.ops.collapse(b2, edges=[es[0]], uvs=True)
            else:
                # the sliver's far corner sits on the long edge's line: dissolve that edge (the two triangles become a
                # quad with a straight-angle corner) and re-triangulate the quad the better way
                r = bmesh.ops.dissolve_edges(b2, edges=[es[-1]])
                bmesh.ops.triangulate(b2, faces=[x for x in r["region"] if x.is_valid], quad_method="BEAUTY")
            bmesh.ops.dissolve_degenerate(b2, edges=b2.edges, dist=1e-5)
            q = [x for x in b2.faces if len(x.verts) > 3]
            if q:
                bmesh.ops.triangulate(b2, faces=q, quad_method="BEAUTY", ngon_method="BEAUTY")
            if (all(x.is_manifold for x in b2.edges) and all(v.is_manifold for v in b2.verts if v.link_faces)
                    and sum(1 for x in b2.faces if _m._fmin(x) < math.radians(lim)) < len(bad)):
                bmesh.ops.recalc_face_normals(b2, faces=b2.faces)
                b2.to_mesh(o.data)
                n += 1
                ok = True
            b2.free()
            if ok:
                break
        bm.free()
        if not ok:
            break
    o.data.update()
    return n


def _ground_faces(o):
    """Faces on the ground plane (the floor cut's cap): plain rock (its darker look on the sheet is shade)."""
    p = m011._Paint(o, off=o[OFF])
    n = 0
    for f in p.bm.faces:
        if all(abs(v.co.z) < 1e-3 for v in f.verts):
            f.material_index = p._mi(ROCK)
            n += 1
    p.done()
    return n


def _make(name, fn, role, budget, union=False, ground=False):
    t0 = time.time()
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget,
             collision=COLLISION[name], tint_var=0.0)
    off = M._build_offset(fn)
    o[OFF] = list(off)
    o.location = (0.0, 0.0, 0.0)          # booleans at the world origin (m030)
    bpy.context.view_layer.update()
    lg = {}
    if union:
        m033._sane(o)
        lg["shells_merged"] = m033._union_fine(o)
    if ground:
        lg["cap"] = m033._floor_cut(o, z0=-off.z)
        o[OFF] = [off.x, off.y, 0.0]
        lg["clean"] = {k: v for k, v in m016._clean_mesh(o, (0.0,)).items() if not isinstance(v, (list, dict))}
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    if m012._thin(o, POLISH_LIM)["under"]:
        lg["killed"] = _kill_slivers(o)
        M.smart_uv(o, **UV)
        lg["polish"]["uv_cut2"] = m012._uv_unfold(o)
    if ground:
        lg["ground_faces"] = _ground_faces(o)
    lg["bowties"] = M.fix_bowties(o)
    K.drop_unused_slots(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


def _make_veg(name, fn):
    """A part made of separate closed shells (leaves, petals): no union, no finish (its speck pass would delete the
    petals); n-gons triangulated, origin at the bottom centre, flat shading, UVs."""
    o = M.mk(SHEET, name, fn, subject=TITLE, role="part", notes=NOTES[name], budget=1000,
             collision=COLLISION[name], tint_var=0.0)
    o[OFF] = list(M._build_offset(fn))
    o.location = (0.0, 0.0, 0.0)
    _tri_ngons(o)
    _recentre(o)
    for p in o.data.polygons:
        p.use_smooth = False
    M.smart_uv(o, **UV)
    lg = {"uv_cut": m012._uv_unfold(o), "bowties": M.fix_bowties(o)}
    K.drop_unused_slots(o)
    return o, lg


def _tri_ngons(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    ng = [f for f in bm.faces if len(f.verts) > 4]
    if ng:
        bmesh.ops.triangulate(bm, faces=ng, quad_method="BEAUTY", ngon_method="BEAUTY")
        bm.to_mesh(o.data)
    bm.free()


def _fused_ok(o):
    a = M.audit(o)
    return (a["shells"] == 1 and not a["nonmanifold_edges"] and not a.get("nonmanifold_verts") and
            not a["boundary_edges"] and a["normals"] == "outward"
            and not m016._self_hits(o)[0] and not m012._thin(o, POLISH_LIM)["under"])


HERO_TRIES = 3
PART_TRIES = 6


def _nudge_rosettes():
    global ROSETTES
    ROSETTES = tuple((n, (x + 0.011, y - 0.009), r, h, lb, s + 0.004, on, yaw + 7.0, sd)
                     for n, (x, y), r, h, lb, s, on, yaw, sd in ROSETTES)


def _set_rosettes(r):
    global ROSETTES
    ROSETTES = r


def _make_hero():
    global ROSETTES
    t0 = time.time()
    base_ros = ROSETTES
    for attempt in range(HERO_TRIES):
        o, lg = _make(HERO, hero_stone, "hero", 4000, union=True, ground=True)
        # a union that silently lost the rock still leaves one closed shell: check the stone kept the rock's size
        if _fused_ok(o) and o.dimensions.x > 8.5 and o.dimensions.z > 7.0:
            break
        _nudge_rosettes()        # a grazing union or a sliver: nudge the cap a hair and rebuild
    ROSETTES = base_ros
    lg["attempt"] = attempt
    lg["stone"] = {k: v for k, v in M.audit(o).items() if k in ("tris", "shells", "nonmanifold_edges",
                                                                  "nonmanifold_verts", "boundary_edges", "size")}
    lg["stone_self_hits"] = m016._self_hits(o)[0]
    tree = _stone_tree(o)
    a = K.fk().Asset(PFX + "dress", "probe", seed=7, tint_var=0.0)
    lg["guard_moves"] = dressing(a, tree)
    c = a.finish(collection=o.users_collection[0], mark_asset=False, origin=None)
    c.matrix_world = o.matrix_world @ Matrix.Translation(-Vector(o[OFF]))
    bpy.context.view_layer.update()
    _tri_ngons(c)
    with M._override(o):
        c.select_set(True)
        with bpy.context.temp_override(selected_objects=[o, c], selected_editable_objects=[o, c]):
            bpy.ops.object.join()
    _recentre(o)
    K.drop_unused_slots(o)
    for p in o.data.polygons:
        p.use_smooth = False
    M.smart_uv(o, **UV)
    lg["uv_cut"] = m012._uv_unfold(o)
    lg["bowties"] = M.fix_bowties(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


# ---- checks ------------------------------------------------------------------------------------------------------------
STONE_KEYS = ("m035_rock", "m035_moss")      # prefixes of the stone shell's keys (rock, stain, cap)


def shells_report(o):
    """Per shell: kind (stone / rock / leaf / petal / pollen), tris, non-manifold edges and verts, boundary edges,
    self-intersecting face pairs inside the shell, inverted faces (ray parity inside the shell)."""
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
        kind = ("stone" if any(x.startswith("m035_moss") and not x.startswith("m035_moss_stain") for x in ks)
                or len(fs) > 150 else
                "leaf" if all(x.startswith("m035_leaf") for x in ks) else
                "petal" if ks == {PETAL} else "pollen" if ks == {POLLEN} else "rock")
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        hits = sum(1 for a_, b_ in tree.overlap(tree) if a_ < b_ and not set(fs[a_].verts) & set(fs[b_].verts))
        inv = 0
        for f in fs:
            # a face is inverted only if rays along its normal and four tilted ones all cross the shell an odd number
            # of times (a ray through an edge counts that edge twice; hits closer than 1e-4 are merged)
            odd = 0
            o1 = f.normal.orthogonal().normalized()
            o2 = f.normal.cross(o1)
            for dv in (f.normal, (f.normal + o1 * 0.21).normalized(), (f.normal - o1 * 0.17).normalized(),
                       (f.normal + o2 * 0.19).normalized(), (f.normal - o2 * 0.23).normalized()):
                p = f.calc_center_median() + dv * 1e-4
                cnt, x, last = 0, p.copy(), None
                for _ in range(40):
                    h = tree.ray_cast(x, dv)
                    if h[0] is None:
                        break
                    if (last is None or (h[0] - last).length > 1e-4) and fs[h[2]] is not f:
                        cnt += 1
                    last = h[0]
                    x = h[0] + dv * 1e-5
                odd += cnt % 2
            inv += odd == 5
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) / 3.0
        out.append({"kind": kind, "tris": sum(len(f.verts) - 2 for f in fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary), "self_hits": hits, "inverted": inv,
                    "volume": round(vol, 4)})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """Floating dressing (fix round 1): per shell, whether it touches another shell (triangles overlap, or a vert
    within `tol` of another shell's surface) or the ground (z <= tol). Returns the counts of shells touching nothing at
    `tol`, the worst such gap, and the shells with no chain of contact down to the ground or the stone at `tol` and at
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
    zmin = [1e9] * n
    for v in bm.verts:
        if v.index in vsh:
            zmin[vsh[v.index]] = min(zmin[vsh[v.index]], v.co.z)
    area = [0.0] * n
    for f in bm.faces:
        area[fsh[f.index]] += f.calc_area()
    stone = max(range(n), key=lambda k: area[k])
    pairs = set()
    for i, j in tree.overlap(tree):
        a_, b_ = fsh[i], fsh[j]
        if a_ != b_:
            pairs.add((min(a_, b_), max(a_, b_)))
    near = {}           # (a, b) -> smallest vert-to-surface gap
    gap = [1e9] * n
    for v in bm.verts:
        s = vsh.get(v.index)
        if s is None:
            continue
        for loc, _, fi, d in tree.find_nearest_range(v.co, chain_tol):
            t = fsh[fi]
            if t != s:
                k = (min(s, t), max(s, t))
                near[k] = min(near.get(k, 1e9), d)
    for (a_, b_) in pairs:
        near[(a_, b_)] = 0.0
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
        seen = {k for k in range(n) if zmin[k] <= t} | {stone}
        stack = list(seen)
        while stack:
            k = stack.pop()
            for m_ in adj[k]:
                if m_ not in seen:
                    seen.add(m_)
                    stack.append(m_)
        return n - len(seen)
    kind = {}
    for f in bm.faces:
        kind.setdefault(fsh[f.index], keys[f.material_index])
    floating = [k for k in range(n) if gap[k] > tol and k != stone]
    res = {"shells": n, "floating": len(floating),
           "floating_kinds": sorted({kind[k].replace("m035_", "") for k in floating}),
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "max_gap_all": round(max(gap[k] for k in range(n) if k != stone), 3),
           "unchained": chained(tol), "unchained_chain_tol": chained(chain_tol)}
    bm.free()
    return res


def rock_metrics(o, view=(0.0, 6.0)):
    """Spec 2.2 rock-shape targets on the rock faces of o (the stone shell's rock-keyed faces, or a MainRock part):
    tris, triangle-area and edge-length CV, valence, crown faces, base span, widths per height, flat facets seen from
    `view` (coplanar neighbours merged, projected area), and the cleft depth (horizontal section against its convex
    hull, front half) at 0.5 of the height and at z 0.5."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    keys = [m.get("flintkit_key", m.name) if m else "" for m in o.data.materials]
    ids, n = M._shell_ids(bm)
    area = {}
    for f in bm.faces:
        area[ids[f.index]] = area.get(ids[f.index], 0.0) + f.calc_area()
    main = max(area, key=area.get)
    fs = [f for f in bm.faces if ids[f.index] == main and keys[f.material_index].startswith(("m035_rock", "m035_moss_stain"))]
    ground = [f for f in fs if f.normal.z < -0.99 and f.calc_center_median().z < 0.01]
    side = [f for f in fs if f not in set(ground)]
    areas = np.array([f.calc_area() for f in side])
    edges = list({e for f in side for e in f.edges})
    el = np.array([e.calc_length() for e in edges])
    vs = [v for v in {v for f in side for v in f.verts} if v.co.z > 0.01]
    val = np.array([len(v.link_edges) for v in vs])
    H = max(v.co.z for f in fs for v in f.verts)
    zs = np.linspace(0.05, 0.95, 10) * H

    def section(z):
        pts = []
        for e in {e for f in fs for e in f.edges}:
            a_, b_ = e.verts
            if (a_.co.z - z) * (b_.co.z - z) < 0:
                t = (z - a_.co.z) / (b_.co.z - a_.co.z)
                pts.append(a_.co.lerp(b_.co, t))
        return pts
    widths = []
    for z in zs:
        p = section(z)
        widths.append(max(q.x for q in p) - min(q.x for q in p) if p else 0.0)
    wmax = max(widths)

    def hull2(pts):
        P = sorted({(round(p.x, 5), round(p.y, 5)) for p in pts})
        if len(P) < 3:
            return P

        def cr(o_, a_, b_):
            return (a_[0] - o_[0]) * (b_[1] - o_[1]) - (a_[1] - o_[1]) * (b_[0] - o_[0])
        lo, up = [], []
        for p in P:
            while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0:
                lo.pop()
            lo.append(p)
        for p in reversed(P):
            while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0:
                up.pop()
            up.append(p)
        return lo[:-1] + up[:-1]

    def depth(z, back=False):
        p = section(z)
        if len(p) < 3:
            return 0.0, None
        hl = hull2(p)
        cy = sum(q.y for q in p) / len(p)
        best, where = 0.0, None
        for q in p:
            if (q.y > cy) != back:
                continue
            d = min(_seg_d((q.x, q.y), hl[i], hl[(i + 1) % len(hl)]) for i in range(len(hl)))
            if d > best:
                best, where = d, (round(q.x, 2), round(q.y, 2))
        return best, where
    # flat facets: coplanar neighbours (normals within 3 deg) merged
    fid = {}
    regs = []
    for f in side:
        if f in fid:
            continue
        r = len(regs)
        stack, reg = [f], []
        fid[f] = r
        while stack:
            g = stack.pop()
            reg.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h in fid or h not in set(side) or h.normal.angle(f.normal, 1.0) > math.radians(3.0):
                        continue
                    fid[h] = r
                    stack.append(h)
        regs.append(reg)
    az, elv = math.radians(view[0]), math.radians(view[1])
    vv = Vector((math.sin(az) * math.cos(elv), -math.cos(az) * math.cos(elv), math.sin(elv)))
    proj = [sum(g.calc_area() * max(0.0, g.normal.dot(vv)) for g in reg) for reg in regs]
    tot = sum(proj)
    vis = sorted([p / tot for p in proj if p / tot >= 0.004], reverse=True)
    crown = [f for f in side if f.normal.z > 0.9 and f.calc_center_median().z > 0.8 * H]
    cx = [v.co.x for f in crown for v in f.verts]
    cyy = [v.co.y for f in crown for v in f.verts]
    gx = [v.co.x for f in ground for v in f.verts]
    gy = [v.co.y for f in ground for v in f.verts]
    allx = [v.co.x for f in fs for v in f.verts]
    ally = [v.co.y for f in fs for v in f.verts]
    d_mid = depth(0.5 * H)
    d_low = depth(0.5)
    res = {"tris": sum(len(f.verts) - 2 for f in side), "ground_tris": len(ground),
           "area_cv": round(float(areas.std() / areas.mean()), 2), "edge_cv": round(float(el.std() / el.mean()), 2),
           "valence": [int(val.min()), int(val.max()), round(float(val.mean()), 2),
                       round(float(np.bincount(val).max() / len(val)), 2)],
           "height": round(H, 2), "width_x": round(max(allx) - min(allx), 2), "depth_y": round(max(ally) - min(ally), 2),
           "widths": [round(w / wmax, 2) for w in widths],
           "widest_h": round(float(zs[int(np.argmax(widths))] / H), 2),
           "crown_faces": len(crown), "crown_span": [round(max(cx) - min(cx), 2) if cx else 0,
                                                     round(max(cyy) - min(cyy), 2) if cyy else 0],
           "base_span": [round((max(gx) - min(gx)) / (max(allx) - min(allx)), 2) if gx else 0,
                         round((max(gy) - min(gy)) / (max(ally) - min(ally)), 2) if gy else 0],
           "facets_seen": len(vis), "largest_facet": round(vis[0], 3) if vis else 0,
           "cleft_mid": [round(d_mid[0], 2), d_mid[1]], "cleft_z05": [round(d_low[0], 2), d_low[1]],
           "rear_crease_mid": round(depth(0.5 * H, back=True)[0], 2)}
    bm.free()
    return res


def _seg_d(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
    return math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)


# ---- render measurement (the study's masks, spec "Pixel boxes and masks") ---------------------------------------------
def classify(px):
    """px: (h, w, 3) sRGB 0-1. Returns int class map: 0 bg/other, 1 rock, 2 green, 3 flower, 4 other-in-silhouette."""
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
    G = (hue >= 48) & (hue <= 140) & (s >= 0.30) & (v >= 0.15)
    F = ((s < 0.12) & (v >= 0.95)) | ((hue >= 38) & (hue < 48) & (s >= 0.55))
    B = (s < 0.035) & (v >= 0.45) & (v <= 0.95)
    R = ((hue <= 48) | (hue >= 190)) & (s >= 0.035) & (s <= 0.40) & (v >= 0.25) & (v <= 0.97) & ~G & ~F & ~B
    out = np.zeros(mx.shape, np.int8)
    out[R] = 1
    out[G] = 2
    out[F & ~G] = 3
    return out, B


def measure(path, bg_tol=0.05):
    """Silhouette bbox, W:H, shares (rock / green with cap above 0.55 H / flower) and the top profile (21 columns) of a
    render whose background is the corner colour."""
    kit = K.NS["KIT"]
    px = kit["load_px"](path)[::-1, :, :3]
    px = np.clip(px, 0, 1)
    bg = np.median(np.concatenate([px[:4, :4].reshape(-1, 3), px[:4, -4:].reshape(-1, 3)]), axis=0)
    sil = np.abs(px - bg).max(-1) > bg_tol
    cls, B = classify(px)
    sil &= ~B
    ys, xs = np.nonzero(sil)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    H, W = y1 - y0 + 1, x1 - x0 + 1
    c = cls * sil
    rock, green, flower = (c == 1).sum(), (c == 2).sum(), (c == 3).sum()
    tot = max(1, rock + green + flower)
    ycap = y0 + 0.45 * H
    gy = np.nonzero(c == 2)[0]
    cap = (gy < ycap).sum()
    prof = []
    for f in np.linspace(0, 1, 21):
        col = int(round(x0 + f * (W - 1)))
        on = np.nonzero(sil[:, col])[0]
        prof.append(round(float((y1 - on.min()) / (H - 1)), 2) if len(on) else 0.0)
    rgb = px * 255

    def med(mask):
        sel = rgb[mask]
        return "#" + "".join(f"{int(x):02X}" for x in np.median(sel, axis=0)) if len(sel) else None
    rows = np.arange(px.shape[0])[:, None]
    return {"bbox": [int(x0), int(y0), int(x1), int(y1)], "wh": round(W / H, 3),
            "rock": round(rock / tot, 3), "green": round(green / tot, 3), "cap": round(cap / tot, 3),
            "foliage": round((green - cap) / tot, 3), "flower": round(flower / tot, 3), "profile": prof,
            "rock_med": med((c == 1)), "cap_med": med((c == 2) & (rows < ycap)),
            "fol_med": med((c == 2) & (rows >= ycap))}


# ---- build -------------------------------------------------------------------------------------------------------------
PARTS = ((ROCK_P, main_rock_part, "union_ground"), (CAP_P, moss_cap_part, "union"),
         (SMALL_P, small_rock_part, "plain"), (FOL_P, foliage_part, "veg"))
TARGET_SIZE = ((12.0, 0.5), (11.1, 0.6), (7.8, 0.3))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and getattr(me, "users", 1) == 0:
                if isinstance(me, bpy.types.Mesh):
                    bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m035_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib",
                                                                                 "MossyBoulder"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build(render=True, parts=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    UNION_RETRIES.clear()
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn, how in PARTS:
            if how == "veg":
                objs[name], log[name] = _make_veg(name, fn)
                continue
            base_ros = ROSETTES
            for attempt in range(PART_TRIES):
                objs[name], log[name] = _make(name, fn, "part", 1000, union=how.startswith("union"),
                                              ground=how.endswith("ground"))
                if _fused_ok(objs[name]) and not any(x["inverted"] for x in shells_report(objs[name])):
                    break
                _nudge_rosettes()
            _set_rosettes(base_ros)
            log[name]["attempt"] = attempt
    log["cap_info_part"] = {k: dict(v) for k, v in CAP_INFO.items()}
    h, log["hero"] = _make_hero()
    log["rock"] = dict(ROCK_INFO)
    log["cap"] = {k: dict(v) for k, v in CAP_INFO.items()}
    log["small_rocks"] = {k: dict(v) for k, v in SR_INFO.items()}
    log["clusters"] = {k: dict(v) for k, v in CLUSTER_INFO.items()}
    log["contact_moves"] = dict(CONTACT_INFO)
    log["union_retries"] = list(UNION_RETRIES)
    _cleanup_tmp()
    order = [h] + [objs[n] for n, *_ in PARTS if n in objs]
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
    hs = shells[HERO]
    contact = {o.name: contact_report(o) for o in order if o is h or o.name == FOL_P}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} shells touch nothing within {CONTACT}, {c['unchained']} have no "
                            f"chain of contact to the ground or the stone")
    if sum(1 for s in hs if s["kind"] == "stone") != 1:
        problems.append(f"{HERO}: {sum(1 for s in hs if s['kind'] == 'stone')} stone shells, expected 1")
    for nm in (ROCK_P, CAP_P, SMALL_P):
        if nm in shells and len(shells[nm]) != 1:
            problems.append(f"{nm}: {len(shells[nm])} shells, expected 1")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 8: none)")
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    kinds = {}
    for s in hs:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts")} for au in audits],
           "shells": kinds, "contact": contact, "thin": thin, "log": log, "problems": problems, "uv": uv,
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "rock_metrics": {"part": rock_metrics(objs[ROCK_P]) if ROCK_P in objs else None},
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders -----------------------------------------------------------------------------------------------------------
# decision 9: f34_sheet (0, 10) for the hero cell, front_sheet (0, 6) for the front cell, r34_sheet (150, 9) beside the
# kit rear34, rear_sheet (180, 6), side_sheet (90, 5) beside the kit side; floor hidden and a 3x lens on *_sheet shots
SHEET_VIEWS = {"f34_sheet": (0, 10), "front_sheet": (0, 6), "r34_sheet": (150, 9), "rear_sheet": (180, 6),
               "side_sheet": (90, 5), "top_sheet": (0, 89)}
PARTS_SHOT = (-20, 20)


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Parts (Exploded View): the main rock in the middle, the cap
    floating above it, small rocks at the left and front, foliage clusters at the left and right."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []

    def put(tag, part, m):
        c = bpy.data.objects.new(f"{PFX}expl_{tag}", by[part].data)
        coll.objects.link(c)
        c.matrix_world = m
        shown.append(c)
    x0 = objs[0].location.x + 60
    o0 = Matrix.Translation((x0, objs[0].location.y, 0))
    put("rock", ROCK_P, o0)
    put("cap", CAP_P, o0 @ Matrix.Translation((0.0, 0.0, 8.6)))
    S = Matrix.Diagonal
    put("sr1", SMALL_P, o0 @ Matrix.Translation((-8.6, -1.0, 0)))
    put("sr2", SMALL_P, o0 @ Matrix.Translation((-6.6, -4.4, 0)) @ Matrix.Rotation(1.1, 4, "Z") @ S((0.8, 0.8, 0.8, 1)))
    put("sr3", SMALL_P, o0 @ Matrix.Translation((-3.9, -5.6, 0)) @ Matrix.Rotation(2.0, 4, "Z") @ S((0.95, 0.95, 0.95, 1)))
    put("sr4", SMALL_P, o0 @ Matrix.Translation((-1.5, -6.0, 0)) @ Matrix.Rotation(0.4, 4, "Z") @ S((0.6, 0.6, 0.6, 1)))
    put("sr5", SMALL_P, o0 @ Matrix.Translation((3.2, -6.0, 0)) @ Matrix.Rotation(2.6, 4, "Z") @ S((0.75, 0.75, 0.75, 1)))
    for i, (x, y, z, sc) in enumerate(((-6.8, 1.5, 5.0, 1.0), (-8.2, -0.3, 2.6, 1.05), (7.6, 1.0, 3.2, 0.85),
                                       (9.0, -0.2, 1.5, 1.05), (7.4, -4.6, 0.0, 1.1), (-5.2, 3.0, 0.0, 0.9))):
        put(f"fol{i}", FOL_P, o0 @ Matrix.Translation((x, y, z)) @ Matrix.Rotation(i * 1.3, 4, "Z")
            @ S((sc, sc, sc, 1)))
    bpy.context.view_layer.update()
    return shown


def _scale_marker(h):
    """A 5.5-stud character stand-in (a plain grey column) beside the hero, for the scale shot."""
    a = K.fk().Asset(PFX + "char", "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=ROCK_COOL, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=ROCK_COOL, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=ROCK_COOL, tint=0.7)
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
        if CAP_P in by:
            extra["cap_under"] = ([by[CAP_P]], 0, -35)
        for o in objs[1:]:
            extra["part_" + o.name.replace("MossyBoulder", "").lower()] = ([o], *PARTS_SHOT)
        if shown:
            extra["exploded"] = (shown, -12, 18)
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
            # Rock / Foliage Junction: the cleft's foot with F2 and R1, from the front-left
            out["junc_cu"] = m033.render_close([h], f"{d}/junc_cu.png", -35, 12, off @ Vector((-3.6, -2.8, 1.1)), 1.7)
        return out
    finally:
        for o in shown + [marker]:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if o is marker and me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def preview(names=("f34_sheet", "rear_sheet", "side_sheet", "top_sheet"), vfx=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig


def hero_only():
    """Rebuild just the hero (tuning loop)."""
    M.coll(NUM, TITLE)
    palette()
    h, lg = _make_hero()
    _cleanup_tmp()
    _spec()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, *_ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals")}, "log": lg,
            "rock": dict(ROCK_INFO), "cap": {k: dict(v) for k, v in CAP_INFO.items()},
            "small_rocks": {k: dict(v) for k, v in SR_INFO.items()},
            "clusters": {k: dict(v) for k, v in CLUSTER_INFO.items()}}
