"""025 Emberbloom (references/025.png): a squat lotus of six thick faceted red crystal leaves round a tall glowing
faceted orange seed, on a low ring of ten chunky brown-grey boulders round a faceted dirt slab.

    import importlib, kit_models, m025; importlib.reload(kit_models); importlib.reload(m025); m025.build()

Parts as on the sheet's Exploded Construction / Parts Breakdown, each built by its own function, all in one build frame
(studs; front -Y, +X right, ground z = 0, origin = the seed's axis on the ground). R08 owns Emberbloom*, so the names
are (M025_spec.md section 8, decision 12):
- EmberbloomPod (pod_part): the seed: an 8-sided gem of half-step offset rings (diamond facets), a long pointed top,
  a short lower cone ending in a blunt nub. Three Neon keys (deep / mid / hot) by a position field.
- EmberbloomPetal (petal_part): one leaf: a thick faceted bicone shard (the convex hull of a pointed 12-point outline,
  a top ridge and apex, and a keel), pointed at both ends, with its hexagonal joining peg.
- EmberbloomRockBase (rock_base_part): the dirt slab (14-sided, sloped sides, raised top, a shallow faceted recess in
  its underside) with ten squat dome boulders round its rim, three pebbles and the seed's 8-sided mount post.

The hero (EmberbloomNode) is built from the same builders: slab, boulders and pebbles, then the six leaves, then the
seed (whose hidden nub runs down into the slab), united one shell at a time (exact booleans, fine merge), floor-cut
flat at the ground with the recess kept open. Colour (stage 4) is painted by position fields inside the builders
before the union (the union and cleanup keep each face's key and Tint). Stages 5-6: the seed keys are Neon; the
finished hero carries a crystal_halo (inside the upper seed), a crystal_glow light above the tip and an embers socket
of yellow diamond crystals above the tip. See M025_spec.md.
"""
import json
import math
import random

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

NUM, TITLE, SHEET = 25, "Emberbloom", "M025"
OFF = "m025_offset"
HERO = "EmberbloomNode"
POD, PETAL, BASE = "EmberbloomPod", "EmberbloomPetal", "EmberbloomRockBase"

SEED_DEEP, SEED_MID, SEED_HOT = "m025_seed_deep", "m025_seed", "m025_seed_hot"
LEAF, LEAF_TIP, LEAF_DARK = "m025_leaf", "m025_leaf_tip", "m025_leaf_dark"
ROCK, ROCK_LIGHT, ROCK_DARK, DIRT = "m025_rock", "m025_rock_light", "m025_rock_dark", "m025_dirt"
SEED_KEYS = (SEED_DEEP, SEED_MID, SEED_HOT)

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0
NEON = 1.0              # the exporter's GLOW_EMISSION threshold: the three seed keys export as Neon pieces

# key -> (hex, roughness, emission, low specular). Stage 1 placeholders are the study's 5.4 starting hexes; stage 4
# writes the calibrated values here (targets in TARGETS, passes in M025_spec.md "Stage 4").
# Pass 1 (calibrate(), the kit's test dome, 2026-10-28; rendered sRGB against the target): leaf #981520 (191,46,51 /
# BE2930), leaf_tip #AE202C (219,53,60 / DC333B), leaf_dark #800310 (160,39,42 / A02229), rock #624D46 (123,94,82 /
# 7C5E51), rock_light #766058 (148,116,102 / 957465), dirt #4F3D37 (100,76,66 / 634B41), rock_dark #4A3C38 (its last
# dome sample fell out of the "brown" mask; the rock key's own linear gain gives the same value).
# Pass 2 (measure() on the hero's six sheet views against the sheet's medians, linear-light geometric-mean gains,
# round 1): leaves x (0.87, 0.60, 0.62) (front / rear / r34 medians #9F2227 / #972328 / #9B2529 against #85191D /
# #7F1A1F / #81191E, and less saturated; f34 / top 11-13 darker than the sheet's: the sheet lights its leaf tops harder
# than the studio does, which paint by facing may not copy); rock and dirt x 1.15 (front #6B554A against #70594E, the
# side / rear / r34 in the studio's shade 17-30 under the sheet, f34 11 over).
# Round 2 (verifier B2: the pass 2 leaf gain and the white sheen made the leaves a dull crimson): pass 2's leaf gain is
# dropped and the leaf keys are low-specular (no white glints on the lit facets); with low_spec the pass 1 hexes
# rendered dark and over-saturated (part #AC1018 against #BC2931), so the dome calibration was re-run with low_spec:
# leaf #9A252F (191,40,48 / BE2930), leaf_tip #B02F3A (221,51,60 / DC333B), leaf_dark #831C28 (160,31,41 / A02229).
# Then leaf x 1.03 and leaf_tip x 1.05 (part shot median #AF242E -> #B0252E against #BC2931, exploded lit #D6343C ->
# #E0363F against #F03A43); x 1.07 / 1.15 (tried) pushed the front median to +53 over the sheet and read pink.
PALETTE = {SEED_DEEP: ("#F24C18", 0.5, NEON, True), SEED_MID: ("#FC7425", 0.5, NEON, True),
           SEED_HOT: ("#FDA835", 0.5, NEON, True),
           LEAF: ("#9F2731", 0.65, 0.0, True), LEAF_TIP: ("#B8323D", 0.65, 0.0, True),
           LEAF_DARK: ("#831C28", 0.7, 0.0, True),
           ROCK: ("#69524B", 0.92, 0.0, False), ROCK_LIGHT: ("#886F66", 0.92, 0.0, False),
           ROCK_DARK: ("#4F403C", 0.92, 0.0, False), DIRT: ("#55413B", 0.95, 0.0, False)}

# calibration targets (spec 5.4: rendered medians of unshadowed regions on the sheet)
TARGETS = {LEAF: ((0xBE, 0x29, 0x30), "vivid"), LEAF_TIP: ((0xDC, 0x33, 0x3B), "vivid"),
           LEAF_DARK: ((0xA0, 0x22, 0x29), "vivid"),
           ROCK: ((0x7C, 0x5E, 0x51), "brown"), ROCK_LIGHT: ((0x95, 0x74, 0x65), "brown"),
           ROCK_DARK: ((0x5E, 0x4A, 0x42), "brown"), DIRT: ((0x63, 0x4B, 0x41), "brown")}


def palette():
    for k, (hexcol, rough, emit, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, emit=emit, low_spec=low)
        _restyle(k)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, emit=emit, low_spec=low)
    _glow_mats()


def _restyle(key):
    """Drop an FB_ material whose node set no longer matches its key's emission (flintkit builds emissive keys
    without the Tint node, and set_colour never clears an emission), so flintkit makes it afresh (m015)."""
    mat = bpy.data.materials.get("FB_" + key)
    if mat and mat.node_tree:
        tinted = any(n.type == "MIX" for n in mat.node_tree.nodes)
        if tinted == (K.fk().palette_entry(key)[3] > 0):
            mat.name = mat.name + "_restyle"
            new = K.fk().material(key)
            mat.user_remap(new)
            bpy.data.materials.remove(mat)
            return True
    return False


def _glow_mats():
    """Blender preview of the Neon keys as Roblox shows Neon: the key's own colour, unshaded (the BSDF's base colour
    black, no specular, so only the emission shows). The exported hex is unchanged (m015)."""
    for mat in bpy.data.materials:
        if not (mat.name.startswith("FB_m025_") and mat.node_tree):
            continue
        if list(mat.get("flintkit_spec", [0, 0, 0]))[2] < NEON:
            continue
        b = mat.node_tree.nodes.get("Principled BSDF")
        for l in list(b.inputs["Base Color"].links):
            mat.node_tree.links.remove(l)
        b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        if "Specular IOR Level" in b.inputs:
            b.inputs["Specular IOR Level"].default_value = 0.0


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's solid keys (TARGETS) on the kit's faceted test dome. Returns {key: (hex, rendered)}
    and leaves the keys set (write them into PALETTE)."""
    keys = keys or list(TARGETS)
    for k in keys:
        K.fk().material(k)
    try:
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


# ---- small helpers ---------------------------------------------------------------------------------------------------
def _faces(verts):
    return K.faces_of([v for v in verts if v.is_valid])


def _tri(bm, faces):
    bmesh.ops.triangulate(bm, faces=[f for f in faces if f.is_valid and len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")


def _mottle(a, faces, amp, scale, seed, tint=1.0):
    """Broad Tint patches about 1/scale studs across, multiplied into each face's Tint (never per-face confetti);
    tint is a uniform per-piece factor."""
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in faces:
        k = (1.0 + amp * 1.6 * noise.noise(f.calc_center_median() * scale + off)) * tint
        for l in f.loops:
            t = l[a.tint_layer][0] * k
            l[a.tint_layer] = (t, t, t, 1.0)


def _ladder(lo, mid, hi):
    """lo, three lo->mid mixes, mid, three mid->hi mixes, hi (9 keys; index 4 = mid; 25 / 50 / 75 % steps)."""
    return ([lo] + [K.mix_key(lo, mid, t) for t in (0.25, 0.5, 0.75)] + [mid] +
            [K.mix_key(mid, hi, t) for t in (0.25, 0.5, 0.75)] + [hi])


def _key(lad, v):
    """v in -1..1 -> the ladder key (quantised to 25 % steps)."""
    v = max(-1.0, min(1.0, v))
    return lad[4 + int(round(v * 4))]


def _zip(bm, ra, rb):
    """Triangles between two closed rings ordered by increasing angle about +Z (verts with .co), walking both by angle
    (the half-step offset rings give the diamond facets). Returns faces."""
    def ang(v):
        return math.atan2(v.co.y, v.co.x)
    a0 = min(range(len(ra)), key=lambda i: ang(ra[i]) % (2 * math.pi))
    b0 = min(range(len(rb)), key=lambda i: ang(rb[i]) % (2 * math.pi))
    A = ra[a0:] + ra[:a0]
    B = rb[b0:] + rb[:b0]
    na, nb = len(A), len(B)

    def ua(i):
        return (ang(A[i % na]) - ang(A[0])) % (2 * math.pi) + (2 * math.pi if i >= na else 0.0)

    def ub(j):
        return (ang(B[j % nb]) - ang(A[0])) % (2 * math.pi) + (2 * math.pi if j >= nb else 0.0)
    i = j = 0
    out = []
    while i < na or j < nb:
        if j >= nb or (i < na and ua(i + 1) <= ub(j + 1)):
            out.append(bm.faces.new((A[i % na], A[(i + 1) % na], B[j % nb])))
            i += 1
        else:
            out.append(bm.faces.new((A[i % na], B[(j + 1) % nb], B[j % nb])))
            j += 1
    return out


# ---- seed (Seedpod) --------------------------------------------------------------------------------------------------
# rings (fraction of the seed height from its nub bottom, radius fraction), spec 1.4 / 2.1: widest at 0.48, a long
# pointed top cone (the hero profile), a short lower cone to the nub
# (round 1b: the upper rings follow the front cell's seed width per height: 0.88 at 0.70, 0.75 at 0.78, 0.50 at
# 0.85, 0.25 at 0.93; the study's 0.64 at 0.77 read as a blunt egg)
# (round 1d: 11 rings made small triangles that read as a smooth egg; the sheet's gem has about five rows of big
# diamond facets, four across)
# (round 2, verifier B1a: Ø 2.2 and rounder shoulders below the widest ring, so the seed reads as the sheet's plump
# gem, not a slim flame tongue)
SEED_RINGS = ((0.0, 0.11), (0.03, 0.11), (0.1, 0.45), (0.25, 0.9), (0.43, 1.0), (0.6, 0.96), (0.74, 0.78),
              (0.86, 0.47), (0.95, 0.18))
SEED = dict(z0=0.95, z1=5.5, r=1.15, n=8, jit=0.04, seed=25001)    # (r 1.1 gave visible W : H 0.58-0.59)
SEED_POST = 0.40         # the hero seed's lower cone runs down to this z (inside the slab, above the recess apex 0.3)
SEED_POST_R = 0.3       # its radius fraction there (round 2, B1c: 0.6 left orange slivers between the leaf bases)
# colour field (spec 5.5): u = height fraction + LAT x lateral toward (+X, -Y) + NZ x broad noise + CHK x a facet
# checker (+1 / -1 on alternate facets), so each band edge is a wide zone of alternating facets (the sheet's painted
# facet variety), not a stripe
# (round 2: the closed leaf cup hides the lower deep belt, so deep moves up to 0.58 to show round the visible belt; the
# verifier's lat 0.12 toward (+X, -Y) made the rear and r34 44-47 % deep with 10 % hot; a slight lean toward
# (-X, -Y) fits five of the seven views within +-9. Swept lat 0-0.12, four directions, deep 0.53-0.62, hot 0.76-0.81
# and five noise seeds: the side view stays deep-heavy in every variant, as a few big diamonds face it)
SEED_COL = dict(lat=0.03, dir=(-1.0, -0.3), nz=0.10, chk=0.18, deep=0.58, hot=0.78, seed=25011, cap_h=0.72, cap_k=0.3,
                lat_top=0.25)
SEED_FOOT_Z = 1.5        # (hero; 1.2 left one orange speck under P1 in the side view) seed diamonds centred below this z are the mount peg's dirt (round 2, B1c)
SEED_INFO = {}


def _seed(a, z0=None, post=None):
    """The gem: 8-sided rings, each turned half a step from the one below, +-4 % radius jitter, a flat-fanned nub cap
    and a tip vertex. Colour: the three Neon keys by the u field. Returns verts."""
    s = SEED
    z0 = s["z0"] if z0 is None else z0
    H = s["z1"] - s["z0"]
    rng = random.Random(s["seed"])
    bm = a.bm
    n = s["n"]
    rings = []
    ring_h = list(SEED_RINGS)
    if post is not None:
        # the hero seed sits down in the leaves: its lower cone runs on down into the slab (no nub)
        ring_h = [((post - s["z0"]) / H, SEED_POST_R)] + ring_h[2:]
    for i, (h, rf) in enumerate(ring_h):
        off = (i % 2) * math.pi / n
        row = []
        for k in range(n):
            th = math.radians(270) + 2 * math.pi * k / n + off
            r = rf * s["r"] * (1 + rng.uniform(-s["jit"], s["jit"]))
            z = z0 + h * H + (rng.uniform(-0.03, 0.03) * H if 0.05 < h < 0.95 else 0.0)
            row.append(bm.verts.new((math.cos(th) * r, math.sin(th) * r, z)))
        rings.append(row)
    tip = bm.verts.new((rng.uniform(-0.03, 0.03), rng.uniform(-0.03, 0.03), z0 + H))
    bot = bm.verts.new((0.0, 0.0, z0 + ring_h[0][0] * H - 0.02))
    faces = []
    for i in range(len(rings) - 1):
        faces += _zip(bm, rings[i], rings[i + 1])
    for k in range(n):
        faces.append(bm.faces.new((rings[-1][k], rings[-1][(k + 1) % n], tip)))
        faces.append(bm.faces.new((rings[0][(k + 1) % n], rings[0][k], bot)))
    vs = [v for r in rings for v in r] + [tip, bot]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    a._finish(vs, SEED_MID, tint=1.0)
    ring_of = {v: i for i, r in enumerate(rings) for v in r}
    _paint_seed(a, faces, ring_of, z0, H, foot=SEED_FOOT_Z if post is not None else None)
    return vs


def _paint_seed(a, faces, ring_of, z0, H, foot=None):
    """Neon keys on whole diamond facets (spec 5.5). Every triangle has exactly one edge on a ring; the two triangles
    sharing that edge (one from the band below, one from the band above) form one diamond and take one key. The key:
    u = height fraction + lateral bias toward (+X, -Y) + broad noise + a random +-chk per diamond; deep below
    c["deep"], hot above c["hot"]. The random term makes each band edge a wide zone of scattered facets (the sheet's
    painted facet variety), not a stripe. Never by facing."""
    c = SEED_COL
    nf = K.noise_field(scale=1.3, seed=c["seed"])
    rng = random.Random(c["seed"])
    lat_dir = Vector((*c.get("dir", (1.0, -1.0)), 0.0)).normalized()
    mis = {k: a._mi(k) for k in SEED_KEYS}
    cnt = {k: 0 for k in SEED_KEYS}
    groups = {}
    for f in faces:
        ring_e = [e for e in f.edges if all(v in ring_of for v in e.verts) and
                  ring_of[e.verts[0]] == ring_of[e.verts[1]]]
        key = ring_e[0] if ring_e else f
        groups.setdefault(key, []).append(f)
    order = sorted(groups.values(), key=lambda g: (round(sum((f.calc_center_median() for f in g), Vector()).z, 3),
                                                  round(math.atan2(*sum((f.calc_center_median() for f in g),
                                                                        Vector()).yx), 3)))
    for g in order:
        p = sum((f.calc_center_median() for f in g), Vector()) / len(g)
        par = rng.random() < 0.5
        hh = (p.z - z0) / H
        q = Vector((p.x, p.y, 0))
        lat = c["lat"] * q.dot(lat_dir) / SEED["r"]
        if hh > c["cap_h"]:
            # (round 2, minor 3) the tip cap: the height term flattens and the side term grows (by direction, not
            # radius), so from above it is mostly mid with hot toward (+X, -Y) and deep on the far side, as the
            # sheet's top cell draws it, not one hot disc
            hh = c["cap_h"] + (hh - c["cap_h"]) * c["cap_k"]
            lat = c["lat_top"] * (q.normalized().dot(lat_dir) if q.length > 1e-6 else 0.0)
        u = hh + lat + c["nz"] * nf(p) + c["chk"] * (1 if par else -1)
        k = SEED_DEEP if u < c["deep"] else SEED_MID if u < c["hot"] else SEED_HOT
        if foot is not None and p.z < foot:
            # (round 2, B1c) the hero seed's buried foot reads as the sheet's mount peg (Seedpod Mount close-up), not
            # as orange specks between the leaf bases and the slab: dirt, a solid key
            k = DIRT
        for f in g:
            f.material_index = mis[k] if k in mis else a._mi(k)
            for l in f.loops:
                l[a.tint_layer] = (1.0, 1.0, 1.0, 1.0)
        cnt[k] = cnt.get(k, 0) + 1
    SEED_INFO["diamonds"] = cnt


# ---- leaves ----------------------------------------------------------------------------------------------------------
# outline (fraction of L along the leaf, half-width as a fraction of L), base -> tip; both ends come to points
# (spec 1.4: widest at 0.45-0.55 L, W : L about 0.41, base and tip narrow)
LEAF_OUT = ((0.12, 0.062), (0.3, 0.155), (0.48, 0.21), (0.65, 0.18), (0.84, 0.088))
# top: ridge point at 0.2 L, the apex at 0.45 L and a shoulder at 0.68 L; bottom: keel points at 0.25, 0.5 and
# 0.72 L (fractions of T, the thickness as a fraction of L): the body stays thick into the outer half, so the leaf
# reads as a chunky shard from every side, not a needle
LEAF_TOP = ((0.18, 0.0, 0.38), (0.45, 0.0, 0.6), (0.68, 0.0, 0.4))
LEAF_KEEL = ((0.25, 0.0, -0.28), (0.5, 0.0, -0.4), (0.72, 0.0, -0.26))
LEAF_T = 0.34
LEAF_W = 1.0            # width scale on LEAF_OUT
# per-leaf width factor (round 1d tried 1.3 on the side pair for the side cell's broad near leaf: side leaves 39 -> 40 %,
# the top's rock share 17 -> 11 %, and the union came out inside-out; not kept)
# (round 2: P1 at 1.15 with roll 20 and a higher tip, so the near side leaf covers the seed's foot in the side view
# as the sheet's side cell draws it; LEAF_W 0.9 everywhere for the top cell's rock share cost 2-4 points of leaf in
# every elevation view, made 4 self-intersecting pairs and gained the top only 3 points: not kept)
LEAF_WS = {"P1": 1.15}
LEAF_BAND = 0.24         # half-height of the side band at mid-length (fraction of T)
BASE_R, BASE_Z = 0.35, 0.42     # (the base points sink into the slab top, z 0.47-0.53: never level with it)
LEAF_ROOT = (0.0, 0.0, 0.6)    # (hero) every leaf's hull reaches this point inside the seed's foot
# the six leaves (spec 2.2): name -> (tip (x, y, z), roll deg, cross, seed); base at BASE_R toward the tip's azimuth,
# BASE_Z, shifted `cross` studs sideways (across the leaf's azimuth).
# Roll turns the leaf about its own axis (positive raises its +tangent edge). The front and back pairs cross in front
# of / behind the seed's foot (the sheet's front and rear cells: "bases crossing in a V just under the seed") with
# their inner edges raised, so they cup the seed's lower half; the side pair turn their top faces toward the front.
# (round 2, verifier B1b: the seed showed from h .16-.31 through an open V down to the rocks. The front pair now
# cross much further (+-1.6: each base sits well past the mid-line, in front of the seed's foot), so their raised
# inner edges meet at h .43 in front of the seed; a smaller cross (+-0.2, tried) only lowers the V. The near side leaf
# P1 rises higher (tip z 3.3, roll 20) and is broader, closing the side view's V the same way. Raising every leaf
# base instead (z 0.9-1.3, tried) bared the seed's foot between the boulders.)
LEAVES = {
    "P1": ((3.52, 0.0, 3.25), 20.0, 0.0, 25101),      # right side
    "P2": ((-3.45, 0.0, 2.85), -38.0, 0.0, 25102),    # left side
    # (round 1c: the front pair 0.3 and the back pair 0.45 further out in depth: the side view's ends were rock only,
    # the sheet's side view has leaf tips over both ends)
    "P3": ((2.55, -2.9, 2.75), -48.0, -1.6, 25103),   # front right
    "P4": ((-2.55, -2.9, 2.75), 48.0, 1.6, 25104),    # front left
    "P5": ((2.0, 2.62, 3.65), 48.0, 0.5, 25105),      # back right
    "P6": ((-2.0, 2.62, 3.65), -48.0, -0.5, 25106),   # back left
}
LEAF_INFO = {}


PETAL_L = 3.9            # the Petal part's length (round 2; round 1 took P3's 4.2, the study planned 3.5)
LEAF_BASE = {}           # per-leaf (base r, base z) overrides of (BASE_R, BASE_Z)


def _leaf_frame(name):
    tip, roll, cross, seed = LEAVES[name]
    tip = Vector(tip)
    az = math.atan2(tip.y, tip.x)
    t0 = Vector((-math.sin(az), math.cos(az), 0.0))
    br, bz = LEAF_BASE.get(name, (BASE_R, BASE_Z))
    base = Vector((math.cos(az) * br, math.sin(az) * br, bz)) + t0 * cross
    d = (tip - base)
    L = d.length
    d.normalize()
    t = Vector((-math.sin(az), math.cos(az), 0.0))
    t = (t - d * t.dot(d)).normalized()
    n = d.cross(t).normalized()
    if n.z < 0:
        t, n = -t, -n
    r = Matrix.Rotation(math.radians(roll), 3, d)
    return base, L, d, r @ t, r @ n, seed


def _leaf_pts(L, seed, W=LEAF_W, T=LEAF_T, root=None):
    """The leaf's points in its own frame (x along the leaf from the base point, y across, z up from the top). root
    (local) adds a hidden point inside the seed's foot, so every hero leaf overlaps the seed and the union is one
    shell."""
    rng = random.Random(seed)
    j = lambda s: 1 + rng.uniform(-s, s)
    pts = [Vector((0.0, 0.0, 0.0)), Vector((L, rng.uniform(-0.02, 0.02) * L, rng.uniform(-0.01, 0.01) * L))]
    for side in (-1, 1):
        for f, hw in LEAF_OUT:
            # the outline is a short side band (an upper and a lower edge), so the section is a flattened hexagon
            # with a deep side face, as the exploded leaves show, not a thin diamond
            x = (f + rng.uniform(-0.02, 0.02)) * L
            y = side * hw * W * L * j(0.05)
            b = LEAF_BAND * T * L * (1 - abs(2 * f - 1) ** 2)
            pts.append(Vector((x, y, b + rng.uniform(-0.01, 0.01) * L)))
            pts.append(Vector((x + rng.uniform(-0.015, 0.015) * L, y * 0.93, -b + rng.uniform(-0.01, 0.01) * L)))
    for f, y, h in LEAF_TOP + LEAF_KEEL:
        pts.append(Vector(((f + rng.uniform(-0.02, 0.02)) * L, (y + rng.uniform(-0.015, 0.015)) * L,
                           h * T * L * j(0.05))))
    if root is not None:
        pts.append(root)
    return pts


def _hull(a, pts):
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    for v in vs:
        if v.is_valid and not v.link_faces:
            bm.verts.remove(v)
    vs = [v for v in vs if v.is_valid]
    _tri(bm, _faces(vs))
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    return vs


def _leaf(a, name, local=False):
    """One leaf: the convex hull of its points (a faceted bicone shard), placed from its base toward its tip."""
    base, L, d, t, n, seed = _leaf_frame(name)
    if local:
        L = PETAL_L      # the reusable part keeps its own length (the hero's crossed P3 runs 4.5 to its buried base)
    m = Matrix((d, t, n)).transposed()
    # each leaf's root point is its own (0.12 toward its azimuth): a vertex shared by two leaves' hulls made the
    # exact union drop the whole base (round 1c)
    az = math.atan2(d.y, d.x)
    root = Vector(LEAF_ROOT) + Vector((math.cos(az), math.sin(az), 0.0)) * 0.12
    pts = _leaf_pts(L, seed, W=LEAF_W * LEAF_WS.get(name, 1.0), root=None if local else m.transposed() @ (root - base))
    if not local:
        pts = [base + m @ p for p in pts]
    vs = _hull(a, pts)
    a._finish(vs, LEAF)
    LEAF_INFO[name] = dict(L=round(L, 2), el=round(math.degrees(math.asin(d.z)), 1),
                           az=round(math.degrees(math.atan2(d.y, d.x)) % 360, 1), faces=len(_faces(vs)))
    return vs, (base, L, d) if not local else (Vector(), L, Vector((1, 0, 0)))


# leaf colour (spec 5.5): t along the leaf; v = (t - 0.5) / LEAF_RAMP (dark base -> leaf -> bright tip), +-noise;
# faces near the seed get darker (occlusion); the back pair shift toward the tip
LEAF_RAMP = 0.28
LEAF_NOISE = dict(amp=0.08, scale=0.9, seed=25121)
LEAF_OCC = (0.45, 0.3)
LEAF_MOTTLE = dict(amp=0.03, scale=0.5, seed=25122)
LEAF_TINT = {"P1": 1.0, "P2": 1.02, "P3": 0.98, "P4": 1.01, "P5": 1.03, "P6": 0.99, "part": 1.0}


def _paint_leaf(a, name, vs, frame, seed_tree=None):
    base, L, d = frame
    lad = _ladder(LEAF_DARK, LEAF, LEAF_TIP)
    sid = sum(ord(ch) for ch in name)          # (never hash(): str hashes change per Blender process)
    nf = K.noise_field(scale=LEAF_NOISE["scale"], seed=LEAF_NOISE["seed"] + sid)
    shift = 0.05 if name in ("P5", "P6") else 0.0
    for f in _faces(vs):
        c = f.calc_center_median()
        t = (c - base).dot(d) / L + shift + LEAF_NOISE["amp"] * nf(c)
        v = (t - 0.5) / LEAF_RAMP
        if seed_tree is not None:
            loc = seed_tree.find_nearest(c)
            if loc[0] is not None and loc[3] < LEAF_OCC[0]:
                v -= LEAF_OCC[1] * 2
        f.material_index = a._mi(_key(lad, v))
    _mottle(a, _faces(vs), LEAF_MOTTLE["amp"], LEAF_MOTTLE["scale"], LEAF_MOTTLE["seed"] + sid,
            tint=LEAF_TINT.get(name, 1.0))


# ---- base: slab, boulders, pebbles -----------------------------------------------------------------------------------
SLAB = dict(rx=2.45, ry=2.15, n=14, seed=25201)
# rings (z, radius fraction, radial jitter, z jitter) from the bottom up; the bottom ring is under the ground (the
# floor cut flattens it); the recess rings come after (underside bowl)
SLAB_RINGS = ((-0.05, 1.0, 0.0, 0.0), (0.28, 0.96, 0.02, 0.03), (0.45, 0.84, 0.03, 0.03), (0.5, 0.55, 0.04, 0.03))
SLAB_TOP = 0.52
RECESS = ((-0.05, 0.62), (0.18, 0.42), (0.3, 0.0))     # (z, radius fraction): the underside bowl, rim to centre


def _slab(a):
    rng = random.Random(SLAB["seed"])
    bm = a.bm
    n = SLAB["n"]
    rx, ry = SLAB["rx"], SLAB["ry"]
    angs = [2 * math.pi * k / n + rng.uniform(-0.1, 0.1) * (2 * math.pi / n) for k in range(n)]
    rows = []
    for i, (z, rf, rj, zj) in enumerate(SLAB_RINGS):
        row = []
        for k, th in enumerate(angs):
            t = th + (math.pi / n if i >= 3 else 0.0)
            f = rf * (1 + rng.uniform(-rj, rj))
            row.append(bm.verts.new((math.cos(t) * rx * f, math.sin(t) * ry * f, z + rng.uniform(-zj, zj))))
        rows.append(row)
    top = bm.verts.new((rng.uniform(-0.1, 0.1), rng.uniform(-0.1, 0.1), SLAB_TOP))
    rec = []
    for i, (z, rf) in enumerate(RECESS[:-1]):
        row = []
        for k, th in enumerate(angs):
            t = th + (math.pi / n if i % 2 else 0.0)
            row.append(bm.verts.new((math.cos(t) * rx * rf * (1 + rng.uniform(-0.03, 0.03)),
                                     math.sin(t) * ry * rf * (1 + rng.uniform(-0.03, 0.03)), z)))
        rec.append(row)
    rc = bm.verts.new((0.0, 0.0, RECESS[-1][0]))
    faces = []
    for r0, r1 in zip(rows, rows[1:]):
        for k in range(n):
            j = (k + 1) % n
            a0, a1, b0, b1 = r0[k], r0[j], r1[k], r1[j]
            if rng.random() < 0.5:
                faces += [bm.faces.new((a0, a1, b1)), bm.faces.new((a0, b1, b0))]
            else:
                faces += [bm.faces.new((a0, a1, b0)), bm.faces.new((a1, b1, b0))]
    for k in range(n):
        faces.append(bm.faces.new((rows[-1][k], rows[-1][(k + 1) % n], top)))
    # the underside: the bottom annulus from the outer bottom ring to the recess rim, then the bowl up to its centre
    for k in range(n):
        j = (k + 1) % n
        faces += [bm.faces.new((rows[0][j], rows[0][k], rec[0][k])), bm.faces.new((rows[0][j], rec[0][k], rec[0][j]))]
    faces += _zip(bm, rec[0], rec[1])
    for k in range(n):
        faces.append(bm.faces.new((rec[-1][k], rec[-1][(k + 1) % n], rc)))
    vs = [v for r in rows + rec for v in r] + [top, rc]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    a._finish(vs, DIRT)
    return vs


ROCK_RINGS = ((0.0, 0.93, 6), (0.35, 1.0, 6), (0.72, 0.8, 5), (1.0, 0.4, 3))
RING = dict(rx=2.55, ry=2.2)
ROCK_Z0 = -0.1
# boulders (spec 2.3): (label, az deg, d, h, ring radius factor, seed)
BOULDERS = (
    # (round 1b: squatter and wider, a continuous low band as on the sheet; the study's domes read as separate balls)
    ("B1", 270.0, 2.1, 1.15, 0.96, 25301), ("B2", 305.0, 1.85, 1.0, 1.0, 25302), ("B3", 235.0, 1.8, 0.98, 1.0, 25303),
    ("B4", 340.0, 1.9, 1.08, 1.0, 25304), ("B5", 200.0, 1.9, 1.05, 1.0, 25305), ("B6", 20.0, 1.65, 1.0, 0.98, 25306),
    ("B7", 160.0, 1.7, 1.02, 0.98, 25307), ("B8", 60.0, 1.55, 0.95, 0.95, 25308), ("B9", 120.0, 1.55, 0.92, 0.95, 25309),
    ("B10", 90.0, 1.5, 0.95, 0.93, 25310),
)
# pebbles: (label, x, y, d, h, seed)
PEBBLES = (("Pa", 1.05, -2.62, 0.55, 0.35, 25321), ("Pb", 1.45, -2.48, 0.42, 0.28, 25322),
           ("Pc", -1.3, -2.62, 0.5, 0.32, 25323))
ROCK_INFO = {}


def _boulders(a):
    out = {}
    for lab, az, d, h, rf, seed in BOULDERS:
        th = math.radians(az)
        x, y = math.cos(th) * RING["rx"] * rf, math.sin(th) * RING["ry"] * rf
        vs = K.hull_rock(a, (d, d * 0.88, h - ROCK_Z0), loc=(x, y, ROCK_Z0), seed=seed, mat=ROCK, rings=ROCK_RINGS,
                         jitter=0.12, rot=th + math.pi / 2, keep_bottom=True)
        _tri(a.bm, _faces(vs))
        bmesh.ops.recalc_face_normals(a.bm, faces=_faces(vs))
        out[lab] = (vs, ROCK_Z0, h - ROCK_Z0)
        ROCK_INFO[lab] = dict(xy=(round(x, 2), round(y, 2)), d=d, h=h)
    for lab, x, y, d, h, seed in PEBBLES:
        vs = K.hull_rock(a, (d, d * 0.85, h - ROCK_Z0), loc=(x, y, ROCK_Z0), seed=seed, mat=ROCK_DARK,
                         rings=((0.0, 0.92, 5), (0.45, 1.0, 5), (1.0, 0.35, 3)), jitter=0.12,
                         rot=random.Random(seed).uniform(0, 6.28), keep_bottom=True)
        _tri(a.bm, _faces(vs))
        bmesh.ops.recalc_face_normals(a.bm, faces=_faces(vs))
        out[lab] = (vs, ROCK_Z0, h - ROCK_Z0)
    return out


def _mount(a):
    """The seed's mount post (RockBase part only): a short 8-sided post at the slab's centre."""
    bm = a.bm
    n, r, z0, z1 = 8, 0.28, 0.3, 0.95
    lo = [bm.verts.new((math.cos(2 * math.pi * k / n) * r, math.sin(2 * math.pi * k / n) * r, z0)) for k in range(n)]
    hi = [bm.verts.new((math.cos(2 * math.pi * k / n) * r, math.sin(2 * math.pi * k / n) * r, z1)) for k in range(n)]
    c0 = bm.verts.new((0, 0, z0))
    c1 = bm.verts.new((0, 0, z1 + 0.02))
    faces = []
    for k in range(n):
        j = (k + 1) % n
        faces += [bm.faces.new((lo[k], lo[j], hi[j])), bm.faces.new((lo[k], hi[j], hi[k])),
                  bm.faces.new((lo[j], lo[k], c0)), bm.faces.new((hi[k], hi[j], c1))]
    vs = lo + hi + [c0, c1]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    a._finish(vs, DIRT)
    return vs


# rock colour (spec 5.5): body rock; broad noise patches -> rock_light; the ground band and contact faces -> darker
ROCK_PATCH = dict(scale=0.55, level=0.12, width=0.3, mix=0.75, seed=25331)
ROCK_GROUND = (0.25, 0.5)        # height fraction under which, mix toward rock_dark (ramped to 0 at 2x)
ROCK_CONTACT = (0.25, 0.35)
ROCK_MOTTLE = dict(amp=0.06, scale=0.45, seed=25332)
DIRT_PATCH = dict(scale=0.6, level=0.2, seed=25341)
DIRT_MOTTLE = dict(amp=0.06, scale=0.45, seed=25342)


def _paint_rocks(a, rocks):
    lad = _ladder(ROCK_DARK, ROCK, ROCK_LIGHT)
    nf = K.noise_field(scale=ROCK_PATCH["scale"], seed=ROCK_PATCH["seed"])
    trees = {k: K.bvh_of(v[0]) for k, v in rocks.items()}
    for i, (lab, (vs, z0, H)) in enumerate(rocks.items()):
        peb = lab.startswith("P")
        for f in _faces(vs):
            c = f.calc_center_median()
            hf = (c.z - max(z0, 0.0)) / H
            if peb:
                v = -0.75 if nf(c) < 0.2 else -0.5
            else:
                hi = ROCK_PATCH["mix"] * min(1.0, max(0.0, (nf(c) - ROCK_PATCH["level"]) / ROCK_PATCH["width"]))
                lo = ROCK_GROUND[1] * min(1.0, max(0.0, (2 * ROCK_GROUND[0] - hf) / ROCK_GROUND[0]))
                v = hi - lo
                if hf < 0.7:
                    for j, t in trees.items():
                        if j == lab:
                            continue
                        loc = t.find_nearest(c)
                        if loc[0] is not None and loc[3] < ROCK_CONTACT[0]:
                            v = min(v, -ROCK_CONTACT[1])
                            break
            f.material_index = a._mi(_key(lad, v))
        _mottle(a, _faces(vs), ROCK_MOTTLE["amp"], ROCK_MOTTLE["scale"], ROCK_MOTTLE["seed"] + i,
                tint=1.0 + random.Random(i * 7 + 3).uniform(-0.04, 0.04))


def _paint_dirt(a, vs, rock_trees=()):
    lad = [DIRT, K.mix_key(DIRT, ROCK_DARK, 0.25)]
    nf = K.noise_field(scale=DIRT_PATCH["scale"], seed=DIRT_PATCH["seed"])
    for f in _faces(vs):
        c = f.calc_center_median()
        k = 0
        if nf(c) > DIRT_PATCH["level"]:
            for t in rock_trees:
                loc = t.find_nearest(c)
                if loc[0] is not None and loc[3] < 0.5:
                    k = 1
                    break
        f.material_index = a._mi(lad[k])
    _mottle(a, _faces(vs), DIRT_MOTTLE["amp"], DIRT_MOTTLE["scale"], DIRT_MOTTLE["seed"])


def _base(a):
    slab = _slab(a)
    rocks = _boulders(a)
    _paint_rocks(a, rocks)
    _paint_dirt(a, slab, [K.bvh_of(v[0]) for v in rocks.values()])
    return slab, rocks


# ---- parts -----------------------------------------------------------------------------------------------------------
POD_PART_BANDS = dict(deep=0.2, hot=0.74)   # verifier round 2 m3: the hero's deep 0.58 is tuned for a seed half hidden
                                             # in the cup; on the whole Pod part it gave 46/27/27 against the sheet's 22/55/23


def pod_part(a):
    global SEED_COL
    hero_col = SEED_COL
    SEED_COL = dict(hero_col, **POD_PART_BANDS)
    try:
        vs = _seed(a, z0=0.0)
    finally:
        SEED_COL = hero_col
    return vs


PEG = dict(r=0.21, n=6, x0=-0.42, x1=0.35)


def petal_part(a):
    """The leaf in its own frame (base point at the origin, along +X, top up) and its hexagonal peg under the base."""
    vs, frame = _leaf(a, "P3", local=True)
    bm = a.bm
    n, r = PEG["n"], PEG["r"]
    rows = []
    for x in (PEG["x0"], PEG["x1"]):
        rows.append([bm.verts.new((x, math.cos(2 * math.pi * k / n) * r, math.sin(2 * math.pi * k / n) * r - 0.02))
                     for k in range(n)])
    c0 = bm.verts.new((PEG["x0"] - 0.01, 0, -0.02))
    c1 = bm.verts.new((PEG["x1"] + 0.01, 0, -0.02))
    faces = []
    for k in range(n):
        j = (k + 1) % n
        faces += [bm.faces.new((rows[0][k], rows[0][j], rows[1][j])), bm.faces.new((rows[0][k], rows[1][j], rows[1][k])),
                  bm.faces.new((rows[0][j], rows[0][k], c0)), bm.faces.new((rows[1][k], rows[1][j], c1))]
    pv = rows[0] + rows[1] + [c0, c1]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    a._finish(pv, LEAF_DARK)
    _paint_leaf(a, "part", vs, frame)


def rock_base_part(a):
    slab, rocks = _base(a)
    mv = _mount(a)


# ---- hero ------------------------------------------------------------------------------------------------------------
def hero(a):
    LEAF_INFO.clear()
    ROCK_INFO.clear()
    slab, rocks = _base(a)
    sv = _seed_probe()
    leaves = {}
    for name in LEAVES:
        leaves[name] = _leaf(a, name)
    for name, (vs, frame) in leaves.items():
        _paint_leaf(a, name, vs, frame, sv)
    _seed(a, post=SEED_POST)


def _seed_probe():
    """A BVH of the hero seed (for the leaves' occlusion darkening), built on a throwaway Asset."""
    p = K.fk().Asset("_m025_probe", "probe")
    vs = _seed(p, post=SEED_POST)
    t = K.bvh_of(vs)
    p.bm.free()
    return t


NOTES = {
    HERO: "Emberbloom event node: a tall faceted 8-sided ember seed (Neon: deep red-orange, orange, hot amber facets) "
          "rising from a squat lotus of six thick faceted red crystal leaves pointed at both ends, on a ring of ten "
          "chunky brown-grey boulders and three pebbles round a faceted dirt slab with a shallow underside recess; "
          "one closed mesh. VFX: crystal_halo (warm halo round the upper seed), crystal_glow (warm light above the "
          "tip), embers (yellow diamond crystals floating above the tip)",
    POD: "Seedpod (reusable): elongated 8-sided faceted gem, diamond facets, long pointed top, short lower cone and "
         "blunt nub; Neon deep / mid / hot facets",
    PETAL: "Leaf (reusable): thick faceted red crystal shard, pointed at both ends, darker base to brighter tip, "
           "hexagonal joining peg under its base",
    BASE: "Base (Rock Cluster, reusable): faceted dirt slab with a shallow faceted underside recess, ten squat dome "
          "boulders round its rim, three pebbles, the seed's 8-sided mount post at the centre",
}


# ---- union, floor cut, cleanup -----------------------------------------------------------------------------------------
FINE_MERGE = 0.002
UNION_RETRIES = []


def _union_fine(o, merge=FINE_MERGE):
    """M.union_loose with a finer post-union merge (m021): the leaf hub's intersection curves converge closer than
    union_loose's 0.01 merge, which would leave bowtie vertices."""
    bpy.context.view_layer.update()
    act = bpy.context.view_layer.objects.active
    if act and act.mode != "OBJECT":
        with bpy.context.temp_override(active_object=act, object=act):
            bpy.ops.object.mode_set(mode="OBJECT")
    others = M.split_loose(o)
    bpy.context.view_layer.update()
    for p in others:
        # guard: an exact union that loses most of the mesh (a near-coincident contact) is undone and retried with the
        # piece nudged a few thousandths of a stud
        for attempt in range(4):
            keep = o.data.copy()
            n0 = len(o.data.polygons) + len(p.data.polygons)
            m = o.modifiers.new("U", "BOOLEAN")
            m.operation, m.solver, m.object = "UNION", "EXACT", p
            m.material_mode = "TRANSFER"
            with M._override(o):
                bpy.ops.object.modifier_apply(modifier=m.name)
            if len(o.data.polygons) >= 0.6 * n0 or attempt == 3:
                bpy.data.meshes.remove(keep)
                break
            bad = o.data
            o.data = keep
            bpy.data.meshes.remove(bad)
            UNION_RETRIES.append((p.name, attempt))
            p.location += Vector((0.004, 0.003, 0.002)) * (attempt + 1)
            bpy.context.view_layer.update()
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


def _floor_cut(o, z0=0.0):
    """m004.floor_cut, but the cap is a triangle fill of all the cut loops together, so the slab's underside recess
    (a loop inside the outer one) stays an open hole in the cap instead of being covered by a second face."""
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
    made = 0
    if bnd:
        res = bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=bnd, normal=(0, 0, -1))
        made = len(res["geom"])
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=0.004)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    return made


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


def _polish(o):
    """Quads split, slivers forced open, origin back at the bottom centre, UVs redone (m023's polish without the floor
    re-fan: the recess makes the floor an annulus, which the triangle fill already fans)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = m012._tri_quads(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = m012._force_slivers(o, lim=POLISH_LIM)
    if m012._thin(o, POLISH_LIM)["under"]:
        forced += m012._force_slivers(o, lim=POLISH_LIM, max_len=0.5)
    bc = m012._bottom_centre(o)
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
    """Faces lying on the ground plane (the floor cut's cap, under the boulders and the slab's rim): the plain rock key
    (the Base Underside close-up's brown ring round the hollow; one even colour). Not the dark dirt: a large dark
    down-facing area would make the rock/dirt family's colour follow facing (K.check corr 0.54)."""
    p = m011._Paint(o, off=o[OFF])
    n = 0
    for f in p.bm.faces:
        if all(abs(v.co.z) < 1e-3 for v in f.verts):
            f.material_index = p._mi(ROCK)
            n += 1
    p.done()
    return n


def _seed_tint(o):
    """Neon keys must stay one flat colour: Tint 1 on every seed-key face (the union can average loop colours)."""
    tint = o.data.color_attributes.get("Tint")
    if tint is None:
        return 0
    idx = {i for i, m in enumerate(o.data.materials) if m and m.get("flintkit_key") in SEED_KEYS}
    n = 0
    for p in o.data.polygons:
        if p.material_index in idx:
            for li in p.loop_indices:
                if abs(tint.data[li].color[0] - 1.0) > 1e-4:
                    n += 1
                tint.data[li].color = (1.0, 1.0, 1.0, 1.0)
    return n


def _nm_verts(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = sum(1 for v in bm.verts if v.link_faces and not v.is_manifold)
    bm.free()
    return n


def _sane(o, limit=30.0):
    co = [v.co for v in o.data.vertices]
    ext = max(max(abs(c[i]) for c in co) for i in range(3))
    if ext > limit:
        raise RuntimeError(f"{o.name}: a vertex {ext:.1f} studs from its origin; not unioning it")


def _make(name, fn, role, budget, union=False, ground=False):
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget, collision="hull",
             tint_var=0.03)
    off = M._build_offset(fn)
    o[OFF] = list(off)
    lg = {}
    if union:
        _sane(o)
        lg["shells_merged"] = _union_fine(o)
    if ground:
        lg["cap"] = _floor_cut(o, z0=-off.z)
        o[OFF] = [off.x, off.y, 0.0]
        lg["clean"] = {k: v for k, v in m016._clean_mesh(o, (0.0,)).items() if not isinstance(v, (list, dict))}
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    if ground:
        lg["ground_faces"] = _ground_faces(o)
    lg["bowties"] = M.fix_bowties(o)
    lg["seed_tint_reset"] = _seed_tint(o)
    K.drop_unused_slots(o)
    return o, lg


def _fused_ok(o):
    a = M.audit(o)
    return (a["shells"] == 1 and not a["nonmanifold_edges"] and not a.get("nonmanifold_verts") and
            not a["boundary_edges"] and a["normals"] == "outward"
            and not m016._self_hits(o)[0] and not m012._thin(o, POLISH_LIM)["under"])


# ---- stages 5 + 6 (spec section 7) -------------------------------------------------------------------------------------
# Stage 5: the three seed keys are Neon (emission NEON, previewed unlit by _glow_mats); one warm steady PointLight in
# the open above the tip and a little in front (crystal_glow). Stage 6: crystal_halo inside the upper seed (the mesh
# hides the billboard's middle; the glow shows round the silhouette) and embers re-textured as the VFX panel's floating
# yellow 4-point diamond crystals, spawned in the open above and beside the tip.
GLOW_LIGHT = dict(pos=(0.0, -1.2, 6.0), color="#FF8A2A", brightness=0.6, range=9.0, flicker=False, shadows=True)
HALO_POS = (0.0, 0.3, 4.4)
HALO_SCALE = 0.45
HALO_COLOR = ["#FFD9A8", "#FF9A3C"]
CRYSTALS_POS = (0.0, 0.0, 6.2)
CRYSTALS_FX = {"name": "Crystals", "texture": "spark_diamond", "color": ["#FFE34A", "#FECE16"], "size": [0.8, 0.3],
               "transparency": [0.1, 1.0], "lifetime": [1.8, 3.0], "rate": 1.5, "speed": [0.3, 0.8], "spread": 40,
               "light_emission": 1.0, "drag": 0.6, "acceleration": [0, 0.3, 0], "shape": [2.0, 0.6, 2.0]}


def _vfx(h):
    """The hero's three sockets (replacing any it has), at build-frame points - h[OFF] (hero-local studs)."""
    import vfx as V
    for c in [c for c in h.children if c.get("vfx_kind")]:
        bpy.data.objects.remove(c, do_unlink=True)
    off = Vector(h[OFF])
    halo = dict(V.KINDS["crystal_halo"]["emitters"][0], color=HALO_COLOR)
    light = {k: GLOW_LIGHT[k] for k in ("color", "brightness", "range", "flicker", "shadows")}
    return [K.socket(h, "crystal_glow", Vector(GLOW_LIGHT["pos"]) - off, light=light),
            K.socket(h, "crystal_halo", Vector(HALO_POS) - off, scale=HALO_SCALE, emitters=[halo]),
            K.socket(h, "embers", Vector(CRYSTALS_POS) - off, emitters=[dict(CRYSTALS_FX)])]


def _inside_fn(tree):
    dirs = [Vector(d).normalized() for d in ((0.31, 0.17, 0.93), (-0.62, 0.71, 0.33), (0.45, -0.83, -0.32))]

    def inside(q):
        k = 0
        for d in dirs:
            n, x = 0, q.copy()
            for _ in range(200):
                hit = tree.ray_cast(x, d)
                if hit[0] is None:
                    break
                n += 1
                x = hit[0] + d * 1e-5
            k += n % 2
        return k >= 2
    return inside


def fx_check(h=None):
    """Each socket: the nearest hero surface, whether the socket point is inside the hero (ray parity), and how many
    of its spawn box's 5^3 grid points lie inside (m015)."""
    h = h or bpy.data.objects[HERO]
    bm = bmesh.new()
    bm.from_mesh(h.data)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    inside = _inside_fn(tree)
    out = []
    for s in [c for c in h.children if c.get("vfx_kind")]:
        spec = json.loads(s["roblox"])
        loc = Vector(s.location)
        sh = (spec.get("emitters") or [{}])[0].get("shape")
        bad = 0
        if sh:
            for i in range(5):
                for j in range(5):
                    for k in range(5):
                        q = loc + Vector(((i / 4 - 0.5) * sh[0], (k / 4 - 0.5) * sh[2], (j / 4 - 0.5) * sh[1]))
                        bad += inside(q)
        out.append({"name": s.name, "kind": s["vfx_kind"], "at_build": [round(c, 2) for c in loc + Vector(h[OFF])],
                    "clear": round(tree.find_nearest(loc)[3], 2), "inside": inside(loc), "box_inside": bad,
                    "roblox_xyz": [round(loc.x, 2), round(loc.z, 2), round(-loc.y, 2)]})
    bm.free()
    return out


# ---- build -----------------------------------------------------------------------------------------------------------
PARTS = ((POD, pod_part, False, False), (PETAL, petal_part, True, False), (BASE, rock_base_part, True, True))
TARGET_SIZE = ((7.0, 0.35), (5.7, 0.4), (5.5, 0.25))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith("_m025_"):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m025_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and (m.name.startswith(("_m025", "_probe", "T_Calib",
                                                                                  "Emberbloom")))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build(render=True, parts=True):
    M.coll(NUM, TITLE)
    UNION_RETRIES.clear()
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn, union, ground in PARTS:
            objs[name], log[name] = _make(name, fn, "part", 1000, union=union, ground=ground)
    h, log["hero"] = _make(HERO, hero, "hero", 4000, union=True, ground=True)
    log["leaves"] = dict(LEAF_INFO)
    log["rocks"] = dict(ROCK_INFO)
    log["seed"] = dict(SEED_INFO)
    log["union_retries"] = list(UNION_RETRIES)
    socks = _vfx(h)
    _glow_mats()
    _cleanup_tmp()
    order = [h] + [objs[n] for n, *_ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    audits = [M.audit(o) for o in order]
    self_hits = {o.name: m016._self_hits(o)[0] for o in order}
    thin = {o.name: m012._thin(o, POLISH_LIM) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = 4000 if o is h else 1000
        if au["tris"] > lim:
            problems.append(f"{o.name}: {au['tris']} tris over {lim}")
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "wire_edges", "loose_verts",
                  "zero_area_faces", "ngons"):
            if au[k]:
                problems.append(f"{o.name}: {k} {au[k]}")
        if au["shells"] != 1:
            problems.append(f"{o.name}: {au['shells']} shells")
        if au["normals"] != "outward":
            problems.append(f"{o.name}: normals {au['normals']}")
        if self_hits[o.name]:
            problems.append(f"{o.name}: {self_hits[o.name]} self-intersecting face pairs")
        if thin[o.name]["under"]:
            problems.append(f"{o.name}: {thin[o.name]['under']} faces with a corner under {POLISH_LIM} deg")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    fx = fx_check(h)
    for s in fx:
        if s["inside"] != (s["kind"] == "crystal_halo") or s["box_inside"]:
            problems.append(f"{s['name']}: socket placement (inside {s['inside']}, spawn points inside "
                            f"{s['box_inside']})")
    # the seed must survive the union (its centre inside the hero)
    bm = bmesh.new()
    bm.from_mesh(h.data)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    if not _inside_fn(tree)(Vector((0, 0, 3.2)) - Vector(h[OFF])):
        problems.append(f"{HERO}: the seed is missing")
    neon = [m.name for m in h.data.materials if m and list(m.get("flintkit_spec", [0, 0, 0]))[2] >= NEON]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts")} for au in audits],
           "thin": thin, "self_hits": self_hits, "log": log, "problems": problems, "fx": fx, "neon": neon,
           "sockets": [(s.name, s["vfx_kind"]) for s in socks],
           "uv": {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped",
                                                                            "min_gap", "border", "density",
                                                                            "stretch_conformal_p95")}
                  for o in order}}
    if render:
        out["views"] = render_views(order)
    return out


# ---- renders ---------------------------------------------------------------------------------------------------------
# the sheet's comparison cameras (decision 11; spec 3.1): the three-quarter cells are near-front / near-rear views from
# higher up; the side camera at +X (screen right = the back)
SHEET_VIEWS = {"front_sheet": (0, 8), "side_sheet": (90, 8), "rear_sheet": (180, 8), "f34_sheet": (-20, 14),
               "r34_sheet": (200, 14), "top_sheet": (0, 89), "top_tilt": (0, 70)}
SHEET_LENS = 3.0        # near-orthographic sheet cells: the *_sheet shots use a 3x longer lens (M018/M020/M023)
PARTS_SHOT = (-20, 25)


def _long_lens(kit):
    orig = kit["render_group"]

    def rg(group, path, azimuth=-22, elevation=20):
        cam = bpy.data.objects["FB_Cam"].data
        lens = cam.lens
        name = path.rsplit("/", 1)[-1]
        if "_sheet" in name or "top_tilt" in name:
            cam.lens = lens * SHEET_LENS
        # the halo's preview stand-in (a few big faceted blobs) veils the model, where a Roblox billboard inside the
        # seed would not: shown only in shots named *halo*
        show = "halo" in name
        for o in bpy.data.objects:
            if o.name.startswith(kit["vfx"].PREVIEW_PREFIX) and "crystal_halo" in str(o.get("vfx_socket", "")):
                o.hide_render = not show
        try:
            return orig(group, path, azimuth, elevation)
        finally:
            cam.lens = lens
    return orig, rg


# the sheet's Exploded Construction: the pod above the base's centre, three leaves fanned out on each side (x, y, z,
# yaw, pitch: the tip up), the base below
EXPL = dict(pod=(0.0, 0.0, 2.6),
            leaves=((-3.1, 0.3, 5.6, 150, 38), (-3.9, 0.0, 4.0, 172, 22), (-3.6, -0.3, 2.5, 192, 8),
                    (3.1, 0.3, 5.6, 30, 38), (3.9, 0.0, 4.0, 8, 22), (3.6, -0.3, 2.5, -12, 8)))


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded Construction: the base at the bottom, the pod above it,
    six leaves fanned round it (each tilted up toward its tip)."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []

    def put(tag, part, m):
        c = bpy.data.objects.new(f"_m025_expl_{tag}", by[part].data)
        coll.objects.link(c)
        c.matrix_world = m
        shown.append(c)
    x0 = objs[0].location.x + 40
    base = Matrix.Translation((x0, objs[0].location.y, 0))
    put("base", BASE, base)
    put("pod", POD, base @ Matrix.Translation(EXPL["pod"]))
    for i, (x, y, z, yaw, pitch) in enumerate(EXPL["leaves"]):
        put(f"leaf{i}", PETAL, base @ Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @
            Matrix.Rotation(math.radians(-pitch), 4, "Y"))
    bpy.context.view_layer.update()
    return shown


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        extra["vfx_halo"] = ([h], 0, 10)
        if shown:
            extra["exploded"] = (shown, -12, 16)
        for o in objs[1:]:
            extra["part_" + o.name.replace("Emberbloom", "").lower()] = ([o], *PARTS_SHOT)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            sheet = M.views(NUM, [h], extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        return {"sheet": sheet}
    finally:
        for o in shown:
            bpy.data.objects.remove(o, do_unlink=True)
        M.display(NUM, objs, TITLE)


def preview(names=("front_sheet", "f34_sheet", "side_sheet", "rear_sheet", "top_sheet", "r34_sheet", "top_tilt"),
            vfx=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = _long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig
        M.display(NUM, [h] + [bpy.data.objects[n] for n in (POD, PETAL, BASE) if n in bpy.data.objects], TITLE)


# ---- measuring (the study's masks, numpy) ------------------------------------------------------------------------------
REF_VIEWS = {"f34": (14, 92, 520, 420), "r34": (530, 92, 1010, 420), "front": (14, 458, 270, 660),
             "side": (275, 458, 505, 660), "rear": (510, 458, 762, 660), "top": (768, 462, 1010, 660)}
LABELS = ((22, 95, 205, 117), (538, 95, 708, 117))        # the three-quarter cells' titles, blanked to paper
OUR_VIEWS = {"f34": "f34_sheet", "front": "front_sheet", "rear": "rear_sheet", "side": "side_sheet",
             "r34": "r34_sheet", "top": "top_sheet", "top_tilt": "top_tilt"}


def _hsv(px):
    a = px / 255.0
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-9), 0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    dd = np.maximum(d, 1e-9)
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60
    return np.where(d == 0, 0, h), s, mx


def _classes(px, paper, ours=False):
    """The study's m.py cls(): S seed, L leaves, R rock (and dirt), O other; 0 background. On our renders the studio
    floor and its pale shadow count as background (rock needs sat >= 0.12, the shadow is a cream grey at sat < 0.1)."""
    h, s, v = _hsv(px)
    bg = np.abs(px - np.array(paper, float)).max(-1) <= 18
    S = ~bg & (h >= 10) & (h <= 62) & (s >= 0.55) & (v >= 0.60)
    L = ~bg & ((h >= 330) | (h < 10)) & (s >= 0.45) & ~S
    R = ~bg & ~S & ~L & (v < 0.74)
    if ours:
        R &= (s >= 0.12)
    out = np.zeros(px.shape[:2], np.uint8)
    out[~bg] = 4
    out[S] = 1
    out[L] = 2
    out[R] = 3
    return out, v, h


def _load(path, box=None):
    px = K.NS["KIT"]["load_px"](path)[::-1, :, :3] * 255.0
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1]
    return np.clip(px, 0, 255)


def _hex(q):
    return "#" + "".join(f"{int(round(x)):02X}" for x in q)


def stats(px, paper, ours=False):
    c, v, hue = _classes(px, paper, ours)
    obj = (c >= 1) & (c <= 3)
    cols = np.nonzero(obj.sum(0) >= 2)[0]
    rows = np.nonzero(obj.sum(1) >= 2)[0]
    bx0, bx1, by0, by1 = cols.min(), cols.max(), rows.min(), rows.max()
    W, H = bx1 - bx0, by1 - by0
    sub = c[by0:by1 + 1, bx0:bx1 + 1]
    n = max(1, ((sub >= 1) & (sub <= 3)).sum())
    out = {"wh": round(W / H, 3), "S": round((sub == 1).sum() / n, 3), "L": round((sub == 2).sum() / n, 3),
           "R": round((sub == 3).sum() / n, 3)}
    vs = v[by0:by1 + 1, bx0:bx1 + 1]
    hs = hue[by0:by1 + 1, bx0:bx1 + 1]
    sv = vs[sub == 1]
    sh = hs[sub == 1]
    if len(sv):
        out["S_bright"] = round(float((sv >= 0.9).mean()), 3)
        out["S_deep_mid_hot"] = [round(float((sh < 17).mean()), 3), round(float(((sh >= 17) & (sh < 30)).mean()), 3),
                                 round(float((sh >= 30).mean()), 3)]
    # bottom 20 %: rock share of the object pixels there
    b0 = int(round(H * 0.8))
    bot = sub[b0:]
    nb = max(1, ((bot >= 1) & (bot <= 3)).sum())
    out["bottom20_R"] = round((bot == 3).sum() / nb, 3)
    top = []
    for i in range(21):
        x = bx0 + int(i * W / 20)
        ys = np.nonzero(obj[:, max(0, x - 1):x + 2].any(1))[0]
        top.append(round((by1 - ys.min()) / H, 2) if len(ys) else None)
    out["top"] = top
    wid = []
    for i in range(11):
        y = by1 - int(i * H / 10)
        xs = np.nonzero(obj[max(0, y - 1):y + 2].any(0))[0]
        wid.append(round((xs.max() - xs.min()) / W, 2) if len(xs) else 0.0)
    out["width"] = wid
    pxs = px[by0:by1 + 1, bx0:bx1 + 1]
    for k, lab in ((1, "S"), (2, "L"), (3, "R")):
        sel = pxs[sub == k]
        if len(sel) >= 8:
            srt = sel[np.argsort(sel.sum(1))]
            q = len(srt) // 4
            out[lab + "med"] = _hex(np.median(sel, axis=0))
            out[lab + "lit"] = _hex(np.median(srt[-q:], axis=0))
            out[lab + "shade"] = _hex(np.median(srt[:q], axis=0))
    return out


def _sheet_px():
    px = _load(M.ref(NUM))
    p = px[125, 30].copy()
    for x0, y0, x1, y1 in LABELS:
        px[y0:y1, x0:x1] = p
    return px


def measure(views=("front", "f34", "side", "rear", "r34", "top", "top_tilt"), tag=""):
    """Sheet against our renders, per view (the study's masks on both). Returns {view: {sheet, ours, prof_err}}."""
    ref = _sheet_px()
    out = {}
    for vname in views:
        x0, y0, x1, y1 = REF_VIEWS["top" if vname == "top_tilt" else vname]
        rp = ref[y0:y1, x0:x1]
        paper = np.median(np.concatenate([rp[:4].reshape(-1, 3), rp[-4:].reshape(-1, 3)]), axis=0)
        a = stats(rp, paper)
        ours = _load(f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[vname]}{tag}.png")
        corner = np.median(ours[:8, :8].reshape(-1, 3), axis=0)
        b = stats(ours, corner, ours=True)
        err = [abs(x - y) for x, y in zip(a["top"], b["top"]) if x is not None and y is not None]
        werr = [abs(x - y) for x, y in zip(a["width"], b["width"])]
        out[vname] = {"sheet": a, "ours": b, "prof_err_mean_max": (round(sum(err) / len(err), 3), round(max(err), 2)),
                      "width_err_max": round(max(werr), 2)}
    return out
