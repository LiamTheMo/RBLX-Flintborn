"""020 Hardwood Stump (references/020.png): a squat, chunky chopped hardwood stump. A flared trunk with eight broad
vertical lobes carries a pale, faceted ringed cut top inset in a thin bark rim; four big angular buttress roots in a +
(front, left, right, back) grow out of its lower half as wedges that slope down to blunt tips on the ground; four
bright six-leaf clumps sit in the four notches between the roots.

    import importlib, kit_models, m020; importlib.reload(kit_models); importlib.reload(m020); m020.build()

Parts as on the sheet's Exploded Construction, each built by its own function, all in one build frame (studs; front
-Y, +X right, ground z = 0, origin = the trunk axis on the ground). R06 owns HardwoodStump*, so the names are
ChoppedHardwoodStump* (M020_spec.md section 8, decision 11):
- ChoppedHardwoodStumpBody (body_part): the trunk (16-vertex lofted rings: a crest on each root azimuth, a groove
  either side, a crest on each diagonal = 8 lobes lined up with the roots), the bark rim and the ringed cut face built
  into its top, and four short buttress stubs (the roots cut off at d 2.9 with flat bark_shadow ends; no sockets).
- ChoppedHardwoodStumpCutFace (cut_face_part): the 0.55-thick 13-sided disc, Ø 3.6, five stepped ring loops.
- ChoppedHardwoodStumpRoot (root_part): the left root module with its flat attach face.
- ChoppedHardwoodStumpLeafClump (clump_part): six broad kite leaves round a hidden hub, a short brown stem stub.

The hero (ChoppedHardwoodStump) is built from the same builders: trunk + 4 full roots + 4 clumps, one exact union of
each shell in turn (M.union_loose), a floor cut at the ground, the sliver cleanup. Colour (stage 4) is painted by
position fields inside the builders, before the union (the union and cleanup keep each face's key and Tint). See
M020_spec.md.
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M
import m004
import m011
import m012
import m016

NUM, TITLE, SHEET = 20, "Hardwood Stump", "M020"
OFF = "m020_offset"

BARK, BARK_LIGHT, BARK_SHADOW = "m020_bark", "m020_bark_light", "m020_bark_shadow"
CUT, CUT_LIGHT, CUT_RING, CUT_PALE = "m020_cut", "m020_cut_light", "m020_cut_ring", "m020_cut_pale"
LEAF, LEAF_TIP, LEAF_BASE, STEM = "m020_leaf", "m020_leaf_tip", "m020_leaf_base", "m020_stem"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low_spec). Stage 4 calibrated (calibrate(), "Stage 4" in M020_spec.md); the comment is the
# calibration target (the sheet's rendered median of an unshadowed region, spec 5.4).
# Round 2 (after the trunk / leaf reshape): pass 1 re-ran K.calibrate on the dome (bark #6A4933, bark_light #7C553B,
# bark_shadow #584033, cut keys as before, leaf #4D8814, tip #679E15, base #366B11, stem #4C3810 = renders #614926);
# pass 2 fitted the lit hero views in linear light: bark x1.18, bark_light x1.75 (the broad light patches carry the
# sheet's lit facets: f34 lit quartile), bark_shadow x1.0, leaves x(0.9, 1.12, 1.0) (f34 / top balance).
PALETTE = {BARK: ("#734F38", 0.9, False),            # #855A3F
           BARK_LIGHT: ("#A06F4E", 0.9, False),      # #9C6847
           BARK_SHADOW: ("#584033", 0.95, False),    # #6E4F3D
           CUT: ("#B09368", 0.85, False),            # #E1B27D
           CUT_LIGHT: ("#C3A880", 0.85, False),      # #F9CE9A
           CUT_RING: ("#C69A65", 0.85, False),       # #F6BC7A
           CUT_PALE: ("#C6AF8D", 0.85, False),       # #FDDFB3
           LEAF: ("#498F14", 0.8, True),             # #5AA515
           LEAF_TIP: ("#62A615", 0.8, True),         # #7CC216
           LEAF_BASE: ("#337111", 0.8, True),        # #3E8012
           STEM: ("#4C3810", 0.9, False)}            # #624921 (dome-calibrated: renders #614926)


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)


TARGETS = {BARK: ((0x85, 0x5A, 0x3F), "brown"), BARK_LIGHT: ((0x9C, 0x68, 0x47), "brown"),
           BARK_SHADOW: ((0x6E, 0x4F, 0x3D), "brown"),
           CUT: ((0xE1, 0xB2, 0x7D), "all"), CUT_LIGHT: ((0xF9, 0xCE, 0x9A), "all"),
           CUT_RING: ((0xF6, 0xBC, 0x7A), "all"), CUT_PALE: ((0xFD, 0xDF, 0xB3), "all"),
           LEAF: ((0x5A, 0xA5, 0x15), "green"), LEAF_TIP: ((0x7C, 0xC2, 0x16), "green"),
           LEAF_BASE: ((0x3E, 0x80, 0x12), "green"), STEM: ((0x62, 0x49, 0x21), "all")}


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome. "all" keys are sampled with the
    paper / floor dropped (M.sample). Returns {key: (hex, rendered)} and leaves the keys set."""
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
STEPS = 4


def _q(t):
    return round(min(1.0, max(0.0, t)) * STEPS) / STEPS


def _mix(k1, k2, t):
    return K.mix_key(k1, k2, _q(t))


def _mottle(a, faces, amp, scale, seed, jitter=0.0):
    """Broad Tint patches about 1/scale studs across, multiplied into each face's Tint (never per-face confetti)."""
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in faces:
        k = 1.0 + amp * 1.6 * noise.noise(f.calc_center_median() * scale + off) + \
            (rng.uniform(-jitter, jitter) if jitter else 0.0)
        for l in f.loops:
            t = l[a.tint_layer][0] * k
            l[a.tint_layer] = (t, t, t, 1.0)


def _faces(verts):
    return K.faces_of([v for v in verts if v.is_valid])


def _tri(bm, faces):
    bmesh.ops.triangulate(bm, faces=[f for f in faces if f.is_valid and len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")


def _interp(tab, x):
    if x <= tab[0][0]:
        return tab[0][1]
    for (x0, y0), (x1, y1) in zip(tab, tab[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return tab[-1][1]


def _ang(v, c=(0.0, 0.0)):
    return math.atan2(v.co.y - c[1], v.co.x - c[0])


def _wrap(t):
    return (t + math.pi) % (2 * math.pi) - math.pi


def _zip(bm, A, B, c=(0.0, 0.0)):
    """Triangles between two closed loops round the same centre c (both counter-clockwise, any vertex counts): the
    zipper advances on whichever loop's next vertex comes first by azimuth. len(A) + len(B) triangles."""
    a0 = _ang(A[0], c)
    k = min(range(len(B)), key=lambda j: abs(_wrap(_ang(B[j], c) - a0)))
    B = B[k:] + B[:k]

    def angles(L):
        out, prev = [], None
        for v in L:
            t = _wrap(_ang(v, c) - a0)
            if prev is not None:
                while t < prev:
                    t += 2 * math.pi
            out.append(t)
            prev = t
        return out + [out[0] + 2 * math.pi]
    ta, tb = angles(A), angles(B)
    nA, nB = len(A), len(B)
    i = j = 0
    fs = []
    while i < nA or j < nB:
        if j >= nB or (i < nA and ta[i + 1] <= tb[j + 1]):
            fs.append(bm.faces.new((A[i], A[(i + 1) % nA], B[j % nB])))
            i += 1
        else:
            fs.append(bm.faces.new((A[i % nA], B[(j + 1) % nB], B[j])))
            j += 1
    return fs


def _fan(bm, ring, c, flip=False):
    n = len(ring)
    return [bm.faces.new((ring[(k + 1) % n], ring[k], c) if not flip else (ring[k], ring[(k + 1) % n], c))
            for k in range(n)]


def _band(bm, r0, r1, rng, flip=0.3):
    """Two triangles per quad between equal rings, the diagonal chosen by seed (flat-shaded irregular facets)."""
    n = len(r0)
    fs = []
    for k in range(n):
        a, b, c, d = r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]
        if rng.random() < flip:
            fs += [bm.faces.new((a, b, d)), bm.faces.new((b, c, d))]
        else:
            fs += [bm.faces.new((a, b, c)), bm.faces.new((a, c, d))]
    return fs


# ---- layout (spec section 2) -------------------------------------------------------------------------------------------
# roots: name -> (azimuth deg, tip distance, height scale, width scale, centreline offset (x, y), tip bend (x, y) at
# the tip (grows with s^2), seed, bottom z). The left root is the profile root (spec 1.4).
ROOTS = {"F": (271.0, 4.55, 0.95, 1.15, (0.0, 0.0), (0.27, 0.0), 20011, -0.05),
         "L": (185.0, 4.60, 1.00, 1.00, (0.0, -0.4), (0.0, 0.0), 20012, -0.07),
         "R": (355.0, 4.40, 1.00, 0.88, (0.0, 0.0), (0.0, 0.0), 20013, -0.09),
         "B": (97.0, 3.95, 0.92, 0.95, (-0.4, 0.0), (0.0, 0.0), 20014, -0.11)}
REF_TIP = 4.55
# the profile root's ridge height and plan width by distance from the axis (spec 1.4; inside the trunk below 2.5)
PROF_H = ((1.3, 2.45), (2.0, 2.25), (2.5, 2.0), (2.9, 1.7), (3.4, 1.45), (3.8, 1.2), (4.2, 0.95))
PROF_W = ((1.3, 2.35), (2.0, 2.35), (2.5, 2.15), (2.9, 1.97), (3.4, 1.73), (3.8, 1.49), (4.2, 1.0))
STATIONS = (1.3, 2.0, 2.5, 2.9, 3.4, 3.8, 4.2)
END = (4.45, 0.72, 0.42)        # end ring: reference distance, width and height fractions of the 4.2 station
TIP = (0.22,)                   # tip point height (x the root's height scale)
HUMP = ((0.35, -0.06), (0.6, 0.06))

# trunk (spec 1.4): rings at these z; mean radius; groove depth; buttress bulge on the root azimuths
TRUNK_Z = (-0.15, 0.5, 1.2, 2.0, 2.8, 3.55)
RIM_Z = 4.15             # stage 1: 4.30 -> 4.15 (f34 W : H 1.585 -> sheet 1.688; decision 2 allows +-0.2)
MEAN_R = ((-0.15, 2.47), (0.0, 2.45), (0.5, 2.35), (1.0, 2.27), (1.6, 2.20), (2.3, 2.13), (3.0, 2.08), (3.65, 2.05))
# round 2 (verifier B1): deep V-grooves between broad lobes (was ((1.0, 0.16), (3.65, 0.10)), offset 22 deg), the
# diagonal crests standing out, the grooves carried through the rim as notches
GROOVE = ((1.0, 0.38), (2.5, 0.32), (3.65, 0.26))
BULGE = ((0.3, 1.25), (0.9, 1.0), (1.5, 0.7), (2.1, 0.4), (2.6, 0.2), (3.0, 0.08), (3.7, 0.0))
BULGE_SIGMA = 16.0
GROOVE_OFF = 18.0
CREST_OUT = 0.08         # the four diagonal crests stand this much proud of the mean radius
TRUNK_JIT = dict(r=0.035, z=0.03, twist=3.0, seed=20001)

# cut face (spec 1.4)
CUT_R = 1.8
CUT_SIDES = 13
CUT_TOP = 4.09
RIM_W = 0.22                # bark rim width outside the cut face's outline
RIM_DIP = 0.16              # the rim's outer edge dips this much where a groove meets it (round 2; was 0.06)
LOOPS = ((0.80, 12, 0.012), (0.60, 12, 0.018), (0.42, 11, 0.026), (0.22, 10, 0.030))   # (r / R, verts, lift)
CENTRE_LIFT = 0.035
# outline radius by azimuth (deg): (centre, half width, depth); the flattened front-left sector
OUTLINE_DIPS = ((240.0, 22.0, 0.13),)
# round 2: a stepped notch in the outline (and the rim) where a groove meets the top, depth / R by groove (sorted
# azimuth order: 13, 79, 115, 167, 203, 253, 289, 337; 0 = no notch, so 6 notches as the sheet's top and f34 show,
# incl. the f34's front-right (289) and right (337 / 13) ones). Each notch is a step: a steep jog NOTCH_W[0] deg
# wide on one side, a slope NOTCH_W[1] deg wide on the other. The inner rim edge and the cut face's outline loop step
# down NOTCH_STEP there.
NOTCH_DEPTH = (0.13, 0.12, 0.0, 0.14, 0.0, 0.12, 0.15, 0.14)
NOTCH_W = (4.0, 12.0)
NOTCH_STEP = 0.04
CUT_SEED = 20002
DISC_T = 0.55


def _notches():
    """[(groove azimuth deg, depth)], sorted by azimuth."""
    gs = sorted(a for a, kd, _ in _trunk_az() if kd == "groove")
    return [(g, NOTCH_DEPTH[i % len(NOTCH_DEPTH)]) for i, g in enumerate(gs)]


def _notch(az):
    """(depth / R, profile 0..1) of the stepped notch at azimuth az (0 away from every notch)."""
    for g, d in _notches():
        x = ((az - g + 180.0) % 360.0) - 180.0
        w = NOTCH_W[0] if x < 0 else NOTCH_W[1]
        if d > 0 and abs(x) < w:
            p = 1.0 - abs(x) / w
            return d * p, p
    return 0.0, 0.0


def outline(az):
    r = 1.0
    for c, w, d in OUTLINE_DIPS:
        x = abs(((az - c + 180.0) % 360.0) - 180.0)
        if x < w:
            r -= d * 0.5 * (1 + math.cos(math.pi * x / w))
    return r - _notch(az)[0]


def _outline_az(flanks=True):
    """The outline loop's azimuths: a notch vertex on every groove, a vertex either side where the notch ends (unless
    flanks is False), and one vertex in the middle of each lobe between (two on lobes wider than 50 deg)."""
    nts = _notches()
    out = []
    for i, (g, d) in enumerate(nts):
        nx, dn = nts[(i + 1) % len(nts)]
        nx += 360.0 if i == len(nts) - 1 else 0.0
        a0 = g + (NOTCH_W[1] if d > 0 else 0.0)
        a1 = nx - (NOTCH_W[0] if dn > 0 else 0.0)
        out += [g] + ([a0] if flanks and d > 0 else []) + ([a1] if flanks and dn > 0 else [])
        k = 2 if a1 - a0 > 50.0 else 1
        out += [a0 + (a1 - a0) * (j + 1) / (k + 1) for j in range(k)]
    return sorted(a % 360.0 for a in out)


def _trunk_az():
    """The 16 trunk azimuths: (deg, kind, root) - a crest on each root, a groove 22 deg either side, a crest on each
    diagonal midway between neighbouring roots."""
    roots = sorted(((v[0], k) for k, v in ROOTS.items()))
    out = []
    for i, (a, k) in enumerate(roots):
        nxt = roots[(i + 1) % 4][0] + (360.0 if i == 3 else 0.0)
        out += [(a, "crest", k), (a + GROOVE_OFF, "groove", k), ((a + nxt) / 2, "diag", None),
                (nxt - GROOVE_OFF, "groove", roots[(i + 1) % 4][1])]
    return sorted(((a % 360.0, kd, k) for a, kd, k in out))


def _bulge(z, az):
    b = _interp(BULGE, z)
    best = 0.0
    for ra, *_ in ROOTS.values():
        d = abs(((az - ra + 180.0) % 360.0) - 180.0)
        best = max(best, b * math.exp(-0.5 * (d / BULGE_SIGMA) ** 2))
    return best


GROOVES = []


def _cut_loops(bm, z_top, rng):
    """The cut face's top: the outline loop at z_top (13 verts on the outline), four inner ring loops (roundish,
    blending to the outline outwards, stepped up a little inwards) and the centre. Returns (loops outer -> inner,
    centre vert); every loop counter-clockwise."""
    out = []
    for az in _outline_az():
        p = _notch(az)[1]
        r = CUT_R * outline(az) * (rng.uniform(0.97, 1.03) if p == 0 else 1.0)
        out.append(bm.verts.new((r * math.cos(math.radians(az)), r * math.sin(math.radians(az)),
                                 z_top - NOTCH_STEP * p)))
    loops = [out]
    for i, (fr, n, lift) in enumerate(LOOPS):
        ph = rng.uniform(0, 360.0 / n)
        # the outermost ring loop echoes the notches (a vertex on each notch and in each lobe), so no zip triangle
        # between it and the notched outline can reach across a notch (round 2); the inner loops stay roundish
        azs = _outline_az(flanks=False) if i == 0 else \
            [ph + 360.0 * k / n for k in range(n)]
        L = []
        for az in azs:
            nd, p = _notch(az)
            r = CUT_R * fr * (1 + (outline(az) + nd - 1) * fr - nd * fr * fr) * \
                (rng.uniform(0.96, 1.04) if p == 0 else 1.0)
            L.append(bm.verts.new((r * math.cos(math.radians(az)), r * math.sin(math.radians(az)), z_top + lift)))
        loops.append(L)
    c = bm.verts.new((rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04), z_top + CENTRE_LIFT))
    return loops, c


CUT_BANDS = ((0.0, CUT_RING), (0.22, CUT_LIGHT), (0.42, CUT_RING), (0.60, CUT_LIGHT), (0.80, CUT_PALE))
CUT_BLEND = 0.05            # half width (r / R) of the soft step across each ring edge
CUT_MOTTLE = dict(amp=0.025, scale=0.7, seed=20061)


def _cut_key(rho, rng):
    """Ring colour by radius fraction: pith dark, light, ring dark, light, palest outer; each ring edge a half step
    (faces straddling an edge take the 50 % mix)."""
    rho += rng.uniform(-0.015, 0.015)
    k = 0
    for i, (r0, _) in enumerate(CUT_BANDS):
        if rho >= r0:
            k = i
    key = CUT_BANDS[k][1]
    for i, (r0, k2) in enumerate(CUT_BANDS[1:], 1):
        if abs(rho - r0) < CUT_BLEND:
            a, b = CUT_BANDS[i - 1][1], k2
            return a if a == b else K.mix_key(a, b, 0.5)
    return key


def _paint_cut(a, faces, seed):
    rng = random.Random(seed)
    for f in faces:
        c = f.calc_center_median()
        az = math.degrees(math.atan2(c.y, c.x)) % 360.0
        rho = Vector((c.x, c.y)).length / (CUT_R * outline(az))
        f.material_index = a._mi(_cut_key(rho, rng))
    _mottle(a, faces, CUT_MOTTLE["amp"], CUT_MOTTLE["scale"], CUT_MOTTLE["seed"] + seed)


# ---- trunk (body) --------------------------------------------------------------------------------------------------------
RIM_LIGHT = 0.25         # the rim's top faces: half way to bark_light (the lit lip)
BARK_FIELD = dict(base=(0.6, 1.2, 0.45), top=(3.2, 0.2), groove=(6.0, 3.0, 0.2), patch_scale=0.5, patch_level=0.15,
                  patch_mix=0.75, seed=20031)     # round 2: broader, lighter patches (were level 0.3, mix 0.35)
BARK_MOTTLE = dict(amp=0.05, scale=0.5, seed=20032, jitter=0.008)


def trunk(a):
    """The trunk: 16-vertex rings (8 lobes lined up with the roots), the bark rim at RIM_Z with a groove dip, the
    short inner wall and the ringed cut face inside it, a fan bottom below the ground. Painted by position: shadow
    bark low, lighter upper trunk and rim top, a light touch in the grooves, broad lighter patches. Returns verts."""
    rng = random.Random(TRUNK_JIT["seed"])
    bm = a.bm
    azs = _trunk_az()
    GROOVES[:] = [x[0] for x in azs if x[1] == "groove"]
    rings = []
    for i, z0 in enumerate(TRUNK_Z):
        tw = rng.uniform(-TRUNK_JIT["twist"], TRUNK_JIT["twist"]) if i else 0.0
        ring = []
        for az, kind, root in azs:
            r = _interp(MEAN_R, z0)
            if kind == "groove":
                r -= _interp(GROOVE, z0)
            elif kind == "diag":
                r += CREST_OUT
            r += _bulge(z0, az)
            r *= 1 + (rng.uniform(-1, 1) * TRUNK_JIT["r"] / 2.1 if i else 0.0)
            th = math.radians(az + tw)
            z = z0 + (rng.uniform(-TRUNK_JIT["z"], TRUNK_JIT["z"]) if i else 0.0)
            ring.append(bm.verts.new((r * math.cos(th), r * math.sin(th), z)))
        rings.append(ring)
    # rim ring (on the outline azimuths: notched at every groove): the outline radius + rim width, its outer edge
    # dipped RIM_DIP into each notch, so the lobes carry through the rim
    rim = []
    for az in _outline_az():
        p = _notch(az)[1]
        r = CUT_R * outline(az) + RIM_W
        z = RIM_Z - RIM_DIP * p + rng.uniform(-0.025, 0.025)
        rim.append(bm.verts.new((r * math.cos(math.radians(az)), r * math.sin(math.radians(az)), z)))
    fs = []
    for r0, r1 in zip(rings, rings[1:]):
        fs += _band(bm, r0, r1, rng, flip=0.15)
    fs += _zip(bm, rings[-1], rim)
    rings.append(rim)
    bot = bm.verts.new((0, 0, TRUNK_Z[0] - 0.02))
    fs += _fan(bm, rings[0], bot, flip=True)
    # rim top -> inner rim edge (on the cut face outline) -> wall down to the cut face -> ring loops
    crng = random.Random(CUT_SEED)
    loops, centre = _cut_loops(bm, CUT_TOP, crng)
    inner = [bm.verts.new((v.co.x / 0.985, v.co.y / 0.985, v.co.z + RIM_Z - 0.01 - CUT_TOP)) for v in loops[0]]
    rim_top = _band(bm, rim, inner, rng, flip=0.0)
    wall = _band(bm, inner, loops[0], rng, flip=0.0)
    face = []
    for l0, l1 in zip(loops, loops[1:]):
        face += _zip(bm, l0, l1)
    face += _fan(bm, loops[-1], centre)
    fs += rim_top + wall + face
    verts = [v for r in rings for v in r] + [bot] + inner + [v for l in loops for v in l] + [centre]
    a._finish(verts, BARK)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(verts))
    # colour
    special = set(face) | set(wall) | set(rim_top)
    _paint_trunk(a, [f for f in fs if f not in special], rim_top, wall)
    _paint_cut(a, face, 0)
    return verts


PATCH_RAMP = 0.08         # verifier round 2: the patch edge steps 25 % -> 50 % over this much noise, not a hard jump


def _patch(n, F):
    """The light-patch mix for noise value n: patch_mix inside the patch, then 50 % and 25 % rings across its edge, so
    the patches blend into the bark instead of showing as flat slabs."""
    lv = F["patch_level"]
    if n > lv + PATCH_RAMP:
        return F["patch_mix"]
    if n > lv:
        return 0.5
    if n > lv - PATCH_RAMP:
        return 0.25
    return 0.0


def _paint_trunk(a, side, rim_top, wall):
    F = BARK_FIELD
    nf = K.noise_field(scale=F["patch_scale"], seed=F["seed"])
    for f in side:
        c = f.calc_center_median()
        az = math.degrees(math.atan2(c.y, c.x)) % 360.0
        z0, z1, mx = F["base"]
        ts = mx * min(1.0, max(0.0, (z1 - c.z) / (z1 - z0)))
        gd = min(abs(((az - g + 180.0) % 360.0) - 180.0) for g in GROOVES)
        if c.z < F["groove"][1] and gd < F["groove"][0]:
            ts = max(ts, F["groove"][2])
        if _q(ts):
            f.material_index = a._mi(_mix(BARK, BARK_SHADOW, ts))
            continue
        tl = F["top"][1] * min(1.0, max(0.0, (c.z - F["top"][0]) / 0.5))
        tl = max(tl, _patch(nf(c), F))
        if _q(tl):
            f.material_index = a._mi(_mix(BARK, BARK_LIGHT, tl))
    for f in rim_top:
        f.material_index = a._mi(_mix(BARK, BARK_LIGHT, RIM_LIGHT))
    for f in wall:
        f.material_index = a._mi(_mix(BARK, BARK_SHADOW, 0.25))
    _mottle(a, side + rim_top + wall, BARK_MOTTLE["amp"], BARK_MOTTLE["scale"], BARK_MOTTLE["seed"],
            BARK_MOTTLE["jitter"])


# ---- roots ------------------------------------------------------------------------------------------------------------
ROOT_FIELD = dict(low=(0.4, 0.6, 0.55), tip=0.4, patch_scale=0.5, patch_level=0.15, patch_mix=0.75, seed=20041)


def root_frame(name):
    az, dtip, hs, ws, off, bend, seed, zb = ROOTS[name]
    u = Vector((math.cos(math.radians(az)), math.sin(math.radians(az)), 0.0))
    v = Vector((-u.y, u.x, 0.0))
    return u, v, Vector((off[0], off[1], 0.0)), Vector((bend[0], bend[1], 0.0))


def _map_d(name, ref):
    dtip = ROOTS[name][1]
    if ref <= 2.5:
        return ref
    return 2.5 + (ref - 2.5) * (dtip - 2.5) / (REF_TIP - 2.5)


def root_centre(name, d):
    u, v, off, bend = root_frame(name)
    dtip = ROOTS[name][1]
    s = min(1.0, max(0.0, (d - 2.5) / (dtip - 2.5)))
    return u * d + off + bend * s * s


def root_height(name, d):
    """The root's ridge height at plan distance d (for the colour field)."""
    hs = ROOTS[name][2]
    dtip = ROOTS[name][1]
    ref = d if d <= 2.5 else 2.5 + (d - 2.5) * (REF_TIP - 2.5) / (dtip - 2.5)
    if ref <= 4.2:
        return _interp(PROF_H, ref) * hs
    t = min(1.0, (ref - 4.2) / (REF_TIP - 4.2))
    return hs * (0.95 + (TIP[0] - 0.95) * t)


def _section(w, h, zb, ro):
    """The 7-sided 'house' section (lateral y, z): flat bottom, shoulders, upper flanks, the ridge."""
    return [(-0.45 * w, zb), (-0.5 * w, 0.45 * h), (-0.25 * w, 0.78 * h), (ro * w, h), (0.25 * w, 0.78 * h),
            (0.5 * w, 0.45 * h), (0.45 * w, zb)]


def _root(a, name, start=1.3, stop=None, flat_start=False, paint=True, hcap=None, hump=HUMP):
    """One root module: 7-sided sections at STATIONS (heights and widths from the profile, scaled per root, a subtle
    hump), jittered and twisted a little (the bottom stays flat), a sloped blunt end ring and a tip point (or, with
    stop, a flat stub end there). The start is a fan pushed back into the trunk (or a flat attach face). hcap (a
    profile like PROF_H) caps the ridge height (the Root part's attach end, which the hero buries in the trunk).
    Painted shadow bark on its lower part by height within the section. Returns (verts, end faces)."""
    az, dtip, hs, ws, off, bend, seed, zb = ROOTS[name]
    rng = random.Random(seed)
    bm = a.bm
    u, v, _, _ = root_frame(name)
    ro = rng.uniform(-0.08, 0.08)
    sts = [d for d in STATIONS if d >= start - 1e-6 and (stop is None or d <= stop + 1e-6)]
    if start < STATIONS[0] - 1e-6:
        sts.insert(0, start)
    if stop is not None and sts[-1] < stop - 1e-6:
        sts.append(stop)
    rings = []
    for ref in sts:
        d = _map_d(name, ref)
        s = min(1.0, max(0.0, (d - 2.5) / (dtip - 2.5)))
        h = _interp(PROF_H, ref) * hs
        if hcap:
            h = min(h, _interp(hcap, ref) * hs)
        for c0, k in hump:
            h *= 1 + k * math.exp(-((s - c0) / 0.12) ** 2)
        w = _interp(PROF_W, ref) * ws
        C = root_centre(name, d)
        tw = math.radians(rng.uniform(-5, 5)) if ref > 1.31 else 0.0
        ring = []
        for j, (y, z) in enumerate(_section(w, h, zb, ro)):
            if 0 < j < 6 and ref > 1.31:
                y += z * math.sin(tw) * 0.3 + rng.uniform(-0.05, 0.05)
                z += rng.uniform(-0.05, 0.05)
                fwd = rng.uniform(-0.05, 0.05)
            else:
                fwd = 0.0
            ring.append(bm.verts.new(C + v * y + u * fwd + Vector((0, 0, z))))
        rings.append(ring)
    fs = []
    for r0, r1 in zip(rings, rings[1:]):
        fs += _band(bm, r0, r1, rng)
    end_faces = []
    if stop is None:
        # blunt end: a smaller, lower ring then the tip point near the ground
        d = _map_d(name, END[0])
        w = _interp(PROF_W, 4.2) * ws * END[1]
        h = _interp(PROF_H, 4.2) * hs * END[2] / 0.95 * 0.95
        C = root_centre(name, d)
        er = [bm.verts.new(C + v * y + Vector((0, 0, z))) for y, z in _section(w, h, zb, ro * 0.5)]
        fs += _band(bm, rings[-1], er, rng)
        tip = bm.verts.new(root_centre(name, dtip) + Vector((0, 0, TIP[0] * hs)))
        end_faces = _fan(bm, er, tip)
        fs += end_faces
        rings.append(er)
        extra = [tip]
    else:
        C = sum((x.co for x in rings[-1]), Vector()) / len(rings[-1])
        cv = bm.verts.new(C)
        end_faces = _fan(bm, rings[-1], cv)
        fs += end_faces
        extra = [cv]
    if flat_start:
        C = sum((x.co for x in rings[0]), Vector()) / len(rings[0])
        sv = bm.verts.new(C)
    else:
        sv = bm.verts.new(root_centre(name, sts[0] - 0.3) + Vector((0, 0, _interp(PROF_H, sts[0]) * hs * 0.45)))
    start_faces = _fan(bm, rings[0], sv, flip=True)
    fs += start_faces
    verts = [x for r in rings for x in r] + extra + [sv]
    a._finish(verts, BARK)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(verts))
    if paint:
        _paint_root(a, name, [f for f in fs if f not in set(end_faces)] if stop is not None else fs)
        if stop is not None:
            for f in end_faces:      # the stub end (the socket face; no hole, decision 4)
                f.material_index = a._mi(_mix(BARK, BARK_SHADOW, 0.75))
    return verts, end_faces


def _paint_root(a, name, faces):
    F = ROOT_FIELD
    u, v, off, _ = root_frame(name)
    dtip = ROOTS[name][1]
    nf = K.noise_field(scale=F["patch_scale"], seed=F["seed"])
    lo, hi, mx = F["low"]
    for f in faces:
        c = f.calc_center_median()
        d = (c - off).dot(u)
        hh = max(0.2, root_height(name, d))
        frac = c.z / hh
        ts = mx * min(1.0, max(0.0, (hi - frac) / (hi - lo)))
        if d > dtip - F["tip"]:
            ts *= 0.5
        if d < 2.3:          # inside / at the trunk: the trunk's own base field
            ts = min(ts, 0.45 * min(1.0, max(0.0, (1.2 - c.z) / 0.6)))
        if _q(ts):
            f.material_index = a._mi(_mix(BARK, BARK_SHADOW, ts))
            continue
        tl = _patch(nf(c), F)
        if _q(tl):
            f.material_index = a._mi(_mix(BARK, BARK_LIGHT, tl))
    _mottle(a, faces, BARK_MOTTLE["amp"], BARK_MOTTLE["scale"], BARK_MOTTLE["seed"] + 7, BARK_MOTTLE["jitter"])


# ---- leaf clumps (the M018 / M019 broad kite recipe) ------------------------------------------------------------------
KITE = ((0.25, 0.40), (0.55, 0.50), (0.82, 0.28))     # (t, half width / W): shoulder, belly, pre-tip
RIDGE = ((0.42, 0.075), (0.76, 0.035))                # (t, camber / L): the midrib ridge (round 2; was 0.08 / 0.04)
KEEL = (0.50, 0.035)
FOLD = 0.14                                           # round 2: a near-flat kite with a midrib crease (was 0.3)
HANDLES = (0.48, 0.38)
LEAF_BANDS = ((0.12, 0.40), (0.60, 0.88))
LEAF_NOISE = 0.08
# round 2: the sheet's leaves are two-tone across the midrib (a lit half, a darker half; the verifier's top-view
# check). The near-flat leaves no longer turn a half from the studio light, so each leaf's right half (in its own
# frame: a position field, the same on every leaf whichever way it faces) reads this much further toward the base
LEAF_HALF = 0.35
KEEL_TOWARD_BASE = 0.0      # round 2: the undersides read mid-green (were 0.5 toward the base), so the f34, which
                            # sees them, isn't darker than the top view, which doesn't
LEAF_MOTTLE = dict(amp=0.035, scale=0.5, seed=20071)


def _ladder(lo, mid, hi):
    return ([lo] + [K.mix_key(lo, mid, t) for t in (0.25, 0.5, 0.75)] + [mid] +
            [K.mix_key(mid, hi, t) for t in (0.25, 0.5, 0.75)] + [hi])


def _pick(lad, v, low, high):
    if v < (low[1] + high[0]) / 2:
        return lad[round(_q((v - low[0]) / (low[1] - low[0])) * 4)]
    return lad[4 + round(_q((v - high[0]) / (high[1] - high[0])) * 4)]


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
    """One closed broad pointed leaf along path (local clump frame): an 8-point kite outline, two midrib ridge points
    above (lit and shaded halves), a keel below. Painted base -> mid -> tip along its length. Returns verts."""
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
    k = vert(KEEL[0], 0.0, -KEEL[1] * L)
    tm[k] = KEEL[0] - KEEL_TOWARD_BASE   # keel (underside) faces read this much toward the base
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
    half = set(fs[:5])                  # the leaf's right half (its own frame, the same side on every leaf)
    for f in fs:
        t = sum(tm[v] for v in f.verts) / len(f.verts) + shift + rng.uniform(-LEAF_NOISE, LEAF_NOISE)
        if f in half:
            t -= LEAF_HALF
        f.material_index = a._mi(_pick(lad, t, LEAF_BANDS[0], LEAF_BANDS[1]))
    return vs


# round 2 (verifier B2): low flat star rosettes, not upright tulips (was pitch 38-66 + 8 deg handle, slope -14..4,
# width 0.64)
LEAF_PITCH = (24.0, 46.0)
LEAF_HANDLE = 2.0               # the path's start handle rises this much above the leaf's pitch
LEAF_SLOPE = (-18.0, -4.0)
LEAF_ROLL = 12.0                # +- roll per leaf (deg): one half turned to the light, the other away
LEAF_L, LEAF_W = 1.35, 0.70     # leaf length and width per unit of half-span
HUB = dict(r=0.14, apex=0.08, sink=0.20, stem_r=0.07, stem_l=0.22)


def _clump(a, hub, normal, out, span, seed, fan=360.0, shift=0.0, sink=None, pitch=LEAF_PITCH, stem_l=None):
    """A six-leaf star round a hidden 5-sided hub cone with a short brown stem stub under it: local frame hub at the
    origin, +Z along normal, local +X toward `out`. Leaves 60 deg apart (+-12) inside `fan` degrees centred on +X,
    rising `pitch` deg off the hub's plane, tips drooping; per leaf +-8 % L, +-6 % W, +-6 deg roll. span = the
    clump's tip-to-tip width. Returns verts."""
    rng = random.Random(seed)
    bm = a.bm
    s = span / 2.0
    sink = HUB["sink"] * s if sink is None else sink
    out_v = []
    hr = HUB["r"] * s
    ph = rng.uniform(0, 2 * math.pi)
    foot = [bm.verts.new((math.cos(ph + 2 * math.pi * k / 5) * hr * 0.6, math.sin(ph + 2 * math.pi * k / 5) * hr * 0.6,
                          -sink))
            for k in range(5)]
    mid = [bm.verts.new((math.cos(ph + 2 * math.pi * k / 5) * hr * 0.8, math.sin(ph + 2 * math.pi * k / 5) * hr * 0.8,
                         0.02)) for k in range(5)]
    apex = bm.verts.new((0, 0, HUB["apex"] * s))
    fb = bm.verts.new((0, 0, -sink - 0.02))
    fs = []
    for k in range(5):
        fs.append(bm.faces.new((foot[k], foot[(k + 1) % 5], mid[(k + 1) % 5], mid[k])))
    fs += _fan(bm, mid, apex) + _fan(bm, foot, fb, flip=True)
    _tri(bm, fs)
    hub_v = foot + mid + [apex, fb]
    a._finish(hub_v, LEAF_BASE)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(hub_v))
    out_v += hub_v                   # the whole hub (its foot too) stays leaf_base (round 2: no brown stalk above ground)
    # stem stub: a thin 5-sided peg from inside the hub down into the support
    sr, sl = HUB["stem_r"], HUB["stem_l"] if stem_l is None else stem_l
    st = [[bm.verts.new((math.cos(ph + 0.3 + 2 * math.pi * k / 5) * sr * sc,
                         math.sin(ph + 0.3 + 2 * math.pi * k / 5) * sr * sc, z)) for k in range(5)]
          for z, sc in ((-sink + 0.05, 1.0), (-sink - sl, 0.85))]
    c0 = bm.verts.new((0, 0, -sink + 0.06))
    c1 = bm.verts.new((0, 0, -sink - sl - 0.01))
    sf = []
    for k in range(5):
        sf.append(bm.faces.new((st[0][k], st[0][(k + 1) % 5], st[1][(k + 1) % 5], st[1][k])))
    sf += _fan(bm, st[0], c0) + _fan(bm, st[1], c1, flip=True)
    _tri(bm, sf)
    stem_v = st[0] + st[1] + [c0, c1]
    a._finish(stem_v, STEM)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(stem_v))
    out_v += stem_v
    n = 6
    step = fan / n if fan < 360.0 else 60.0
    az0 = -fan / 2 + step / 2 if fan < 360.0 else rng.uniform(0, 360)
    for k in range(n):
        az = az0 + step * k + rng.uniform(-12, 12) * (step / 60.0)
        L = LEAF_L * s * (1 + rng.uniform(-0.08, 0.08))
        W = LEAF_W * s * (1 + rng.uniform(-0.06, 0.06))
        b0 = Vector((0.0, 0.0, -0.05 * s))       # every leaf starts at the hub centre, under the low crown
        # alternate low / high leaves (the lower or upper third of the pitch range), so neighbours overlap stacked,
        # one above the other, instead of cutting through each other near-coplanar (round 2: the flat leaves crossed
        # edge-on and the exact union left crossings)
        lo, hi = pitch
        p = rng.uniform(lo, lo + (hi - lo) / 3) if k % 2 == 0 else rng.uniform(hi - (hi - lo) / 3, hi)
        tipr = L * math.cos(math.radians(p)) * 0.95
        tipz = L * math.sin(math.radians(p)) * 0.95
        path = _leaf_path(b0, az, (tipr, tipz), p + LEAF_HANDLE, rng.uniform(*LEAF_SLOPE))
        out_v += _leaf(a, path, W, seed * 10 + k, roll=rng.uniform(-LEAF_ROLL, LEAF_ROLL), shift=shift)
    N = Vector(normal).normalized()
    X = Vector(out)
    X = (X - N * X.dot(N))
    X = X.normalized() if X.length > 1e-6 else N.orthogonal().normalized()
    Y = N.cross(X)
    R = Matrix((X, Y, N)).transposed().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(hub)) @ R, verts=out_v)
    _mottle(a, _faces(out_v), LEAF_MOTTLE["amp"], LEAF_MOTTLE["scale"], LEAF_MOTTLE["seed"] + seed)
    return out_v


# hero clumps (spec 2.2): name -> (hub target, normal, outward direction, span, seed, fan, colour shift to the tips)
CLUMPS = {"FL": ((-1.9, -2.0, 0.22), (-0.25, -0.25, 1.0), (-1.0, -1.0, 0.0), 2.7, 20091, 300.0, 0.1),
          "FR": ((1.5, -2.3, 0.2), (0.2, -0.25, 1.0), (1.0, -1.0, 0.0), 2.2, 20092, 240.0, 0.0),
          "BL": ((-3.0, 0.0, 9.0), (-0.2, 0.25, 1.0), (-0.5, 1.0, 0.0), 2.2, 20083, 260.0, 0.0),
          "BR": ((2.8, 0.35, 9.0), (0.2, 0.25, 1.0), (0.8, 1.0, 0.0), 2.7, 20094, 260.0, 0.1)}
CLUMP_REACH = 1.5
CLUMP_SINK = 0.10
CLUMP_SINK_GROUND = 0.15        # ground clumps slide this much past their first contact with a root / the trunk
                                # (round 2: 0.10 left FR's low leaves grazing the front root)
CLUMP_INFO = {}


def _inside(tree, p, d=Vector((0.31, 0.17, 0.93)).normalized()):
    """Ray parity: p inside the closed surface(s) in tree."""
    hits, q = 0, Vector(p)
    while True:
        loc = tree.ray_cast(q, d)[0]
        if loc is None:
            return hits % 2 == 1
        hits += 1
        q = loc + d * 1e-4


def _overlaps(tree, hub, normal, out, span, seed, fan):
    """A clump built at hub (in a scratch mesh) has leaves crossing the surfaces in tree."""
    t = K.fk().Asset("_m020_probe", "probe")
    _clump(t, hub, normal, out, span, seed, fan=fan)
    t.bm.verts.ensure_lookup_table()
    t.bm.faces.ensure_lookup_table()
    hit = bool(BVHTree.FromBMesh(t.bm).overlap(tree))
    t.bm.free()
    return hit


def clumps(a):
    """The four clumps. BL and BR slide back along -normal onto the root / trunk built so far (hub sunk CLUMP_SINK);
    FL and FR sit at their ground hubs (their cones run into the ground and the roots' flanks)."""
    a.bm.verts.ensure_lookup_table()
    a.bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(a.bm)
    out = []
    CLUMP_INFO.clear()
    for k, (hub, nrm, outd, span, seed, fan, shift) in CLUMPS.items():
        H, N = Vector(hub), Vector(nrm).normalized()
        P = H
        if hub[2] > 0.5:      # on a root: dropped straight down onto its top / back flank, the hub sunk a little
            hit = tree.ray_cast(Vector((H.x, H.y, 8.0)), Vector((0, 0, -1)), 12.0)
            if hit[0] is not None:
                P = hit[0] - N * CLUMP_SINK
        else:                 # on the ground: slid in toward the trunk axis just until its leaves cut into a root or
            d = -Vector((H.x, H.y, 0.0)).normalized()     # the trunk (so the hero stays one shell)
            for step in range(41):
                q = H + d * (0.05 * step)
                if _overlaps(tree, q, N, outd, span, seed, fan):
                    P = q + d * CLUMP_SINK_GROUND
                    break
        CLUMP_INFO[k] = {"hub": [round(c, 2) for c in P], "moved": round((P - H).length, 2)}
        out += _clump(a, P, N, outd, span, seed, fan=fan, shift=shift)
    return out


# ---- parts ---------------------------------------------------------------------------------------------------------------
def body_part(a):
    """ChoppedHardwoodStumpBody: the trunk with its ringed top and four buttress stubs (flat bark_shadow ends)."""
    trunk(a)
    for name in ROOTS:
        _root(a, name, stop=2.9)


def cut_face_part(a):
    """ChoppedHardwoodStumpCutFace: the 0.55-thick 13-sided disc, its top the same stepped ring loops as the body's."""
    bm = a.bm
    crng = random.Random(CUT_SEED)
    loops, centre = _cut_loops(bm, DISC_T, crng)
    face = []
    for l0, l1 in zip(loops, loops[1:]):
        face += _zip(bm, l0, l1)
    face += _fan(bm, loops[-1], centre)
    rng = random.Random(CUT_SEED + 1)
    low = [bm.verts.new((v.co.x * 0.985, v.co.y * 0.985, 0.0)) for v in loops[0]]
    side = _band(bm, low, loops[0], rng, flip=0.0)
    bc = bm.verts.new((0, 0, 0))
    bot = _fan(bm, low, bc, flip=True)
    vs = [v for l in loops for v in l] + [centre] + low + [bc]
    a._finish(vs, CUT)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    _paint_cut(a, face, 0)
    for f in side + bot:
        f.material_index = a._mi(CUT)
    _mottle(a, side + bot, CUT_MOTTLE["amp"], CUT_MOTTLE["scale"], CUT_MOTTLE["seed"] + 5)


def root_part(a):
    """ChoppedHardwoodStumpRoot: the left (profile) root from d 1.0, with a flat attach face. Round 2 (verifier B3):
    started at d 2.0 it was 2.68 long x 2.24 high (L : H 1.2, a boulder); the module now runs from d 1.0 with its
    attach end capped at the trunk-edge height and a clearer hump-dip-bulge ridge (L : H about 1.7, as drawn)."""
    _root(a, "L", start=PART_ROOT_START, flat_start=True, hcap=PART_ROOT_CAP, hump=PART_HUMP)


PART_ROOT_START = 1.0
PART_ROOT_CAP = ((1.0, 2.1), (2.0, 2.05), (2.5, 2.0))
PART_HUMP = ((0.35, -0.10), (0.6, 0.10))


def clump_part(a):
    """ChoppedHardwoodStumpLeafClump: one clump (span 2.0), hub up, only a short stem stub below (round 2: the stub at
    most 0.1 of the clump's height; the hub sits just above its bottom)."""
    _clump(a, (0, 0, CLUMP_PART_STEM[0] + CLUMP_PART_STEM[1] + 0.01), (0, 0, 1), (1, 0, 0), 2.0, 20104, shift=0.05,
           sink=CLUMP_PART_STEM[0], stem_l=CLUMP_PART_STEM[1], pitch=CLUMP_PART_PITCH)


CLUMP_PART_STEM = (0.06, 0.06)      # (hub sink, stem length) of the LeafClump part
CLUMP_PART_PITCH = (15.0, 33.0)     # the exploded cell's clump lies flatter than the hero's (a near-flat star)


def hero(a):
    trunk(a)
    for name in ROOTS:
        _root(a, name)
    clumps(a)


NOTES = {
    "ChoppedHardwoodStump": "hardwood stump: a squat flared trunk with eight broad lobes and a pale faceted ringed cut "
                            "top inset in a thin bark rim, four angular buttress roots in a + sloping to blunt tips, "
                            "four bright six-leaf clumps in the notches; one closed mesh, flat base. No VFX, no glow",
    "ChoppedHardwoodStumpBody": "Stump Body (reusable): lobed trunk with the ringed cut top and four short buttress "
                                "stubs with flat ends",
    "ChoppedHardwoodStumpCutFace": "Cut Face (reusable): 0.55-thick 13-sided pale disc, faceted stepped rings",
    "ChoppedHardwoodStumpRoot": "Root Module (reusable): chunky angular buttress wedge with a flat attach face and a "
                                "blunt sloped tip",
    "ChoppedHardwoodStumpLeafClump": "Leaf Clump (reusable): six broad pointed kite leaves round a hidden hub, dark "
                                     "bases to lime tips, short brown stem stub",
}


# ---- cleanup (m016 / m019 procedure, this model's offset key) ---------------------------------------------------------
def _crosses(bm, v, co):
    """Moving v to co would make one of its faces cut through a face outside v's one-ring (the flat round-2 leaves lie
    close over each other and over the roots, and m011's sliver collapses could push one through another)."""
    bm.faces.ensure_lookup_table()
    tris = []
    for f in v.link_faces:
        ps = [co if w is v else w.co for w in f.verts]
        if len(ps) == 3 and ((ps[1] - ps[0]).cross(ps[2] - ps[0])).length > 1e-12:
            tris.append(ps)
    if not tris:
        return False
    moved = _shrunk_tree(tris)
    full = BVHTree.FromBMesh(bm)
    return any(v not in bm.faces[j].verts for _, j in moved.overlap(full))


def _shrunk_tree(tris, k=0.995):
    """A BVH of triangles pulled a hair toward their centroids, so faces that only touch them at a shared corner or
    edge don't count as overlapping, while a real crossing still does."""
    pts = []
    for t in tris:
        c = (t[0] + t[1] + t[2]) / 3
        pts += [c + (p - c) * k for p in t]
    return BVHTree.FromPolygons(pts, [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(len(tris))], epsilon=0.0)


def _tri_safe(bm):
    """Triangulate the quads and n-gons as fans, choosing for each face the fan corner whose triangles cross no other
    face and have the best smallest angle (the booleans leave bent n-gons where leaves lie close over each other or
    a root; BEAUTY split some of them straight through a neighbour: +10 crossings on the round-2 hero)."""
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    flist = list(bm.faces)
    for f in [f for f in bm.faces if len(f.verts) > 3]:
        if not f.is_valid:
            continue
        vs = list(f.verts)
        n = len(vs)
        fn = f.normal.copy()
        best = None
        for k in range(n):
            tris = [(vs[k].co, vs[(k + i) % n].co, vs[(k + i + 1) % n].co) for i in range(1, n - 1)]
            nrm = [(b - a).cross(c - a) for a, b, c in tris]
            if min(x.length for x in nrm) < 1e-12 or any(x.dot(fn) <= 0 for x in nrm):
                continue
            cand = _shrunk_tree([[p.copy() for p in t] for t in tris])
            cross = sum(1 for _, j in cand.overlap(tree) if flist[j].is_valid and flist[j] is not f)
            ang = min(m011._min_angle(list(t)) for t in tris)
            score = (cross, -ang)
            if best is None or score < best[0]:
                best = (score, k)
        if best is None:
            bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="BEAUTY")
            continue
        k = best[1]
        for i in range(2, n - 1):
            bmesh.ops.connect_verts(bm, verts=[vs[k], vs[(k + i) % n]])
    left = [f for f in bm.faces if len(f.verts) > 3]
    if left:
        bmesh.ops.triangulate(bm, faces=left, quad_method="BEAUTY", ngon_method="BEAUTY")


def _clean_guarded(o, movable, max_move):
    """m011._clean (dissolve the two-edge crease points, triangulate, _desliver) with every vertex move refused if it
    would push a face through a non-neighbouring one (round 2: the shared clean left 11 such crossings at the flat
    leaf clumps). Same log."""
    from mathutils.geometry import intersect_point_line
    bm = bmesh.new()
    bm.from_mesh(o.data)
    v2 = []
    for v in bm.verts:
        if len(v.link_edges) == 2 and all(len(f.verts) > 3 for f in v.link_faces) and movable(v, v.co):
            a_, c_ = (e.other_vert(v) for e in v.link_edges)
            p, _ = intersect_point_line(v.co, a_.co, c_.co)
            if (p - v.co).length < max_move and (p.z == v.co.z or movable(v, p)):
                v2.append(v)
    bmesh.ops.dissolve_verts(bm, verts=v2)
    _tri_safe(bm)

    def guarded(v, co):
        if not movable(v, co):
            return False
        return (co - v.co).length < 1e-9 or not _crosses(bm, v, co)
    log = m011._desliver(bm, guarded, min_angle=5.0, max_move=max_move)
    log["dissolved_v2"] = len(v2)
    bm.to_mesh(o.data)
    bm.free()
    return log


def _clean_mesh(o, planes):
    """m016._clean_mesh with the guarded sliver clean."""
    m016._weld(o)
    ears = m016._dissolve_ears(o)
    pockets = m012._drop_inner(o)
    log = _clean_guarded(o, m011._plane_lock(planes), max_move=m011.CLEAN_MOVE)
    pockets += m012._drop_inner(o)
    log["ears"] = ears
    log["pockets"] = pockets
    log["forced"] = m012._force_slivers(o)
    return log


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
    # the floor cap (flat, at the bottom): re-fan its triangles for the best angles (the hole fill leaves needles)
    zmin = min(v.co.z for v in bm.verts)
    floor = [f for f in bm.faces if f.normal.z < -0.999 and all(abs(v.co.z - zmin) < 1e-4 for v in f.verts)]
    big = [f for f in floor if f.calc_area() > 0.8 and m011._fmin(f) < math.radians(12)]
    if big:      # a Steiner point in each big needle, so the re-fan has somewhere to go
        made = bmesh.ops.poke(bm, faces=big)["faces"]
        floor = [f for f in floor if f.is_valid] + list(made)
    fset = set(floor)
    inner = [e for e in {e for f in floor for e in f.edges} if all(g in fset for g in e.link_faces)]
    if inner:
        bmesh.ops.beautify_fill(bm, faces=floor, edges=inner)
    # a needle left on the floor (a short perimeter edge where a clump's hub meets the ground, fanned from far away):
    # split its long interior edges at their midpoints (flat, so nothing moves), which doubles the needle's angle
    for _ in range(4):
        bad = [f for f in bm.faces if f.is_valid and f.normal.z < -0.999 and m011._fmin(f) < math.radians(POLISH_LIM)
               and all(abs(v.co.z - zmin) < 1e-4 for v in f.verts)]
        if not bad:
            break
        longs = list({max((e for e in f.edges if len(e.link_faces) == 2 and all(
            g.normal.z < -0.999 for g in e.link_faces)), key=lambda x: x.calc_length(), default=None) for f in bad} - {None})
        if not longs:
            break
        res = bmesh.ops.subdivide_edges(bm, edges=longs, cuts=1)
        touched = {f for v in res["geom_inner"] if isinstance(v, bmesh.types.BMVert) for f in v.link_faces}
        bmesh.ops.triangulate(bm, faces=[f for f in touched if len(f.verts) > 3], quad_method="BEAUTY",
                              ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = m012._force_slivers(o, lim=POLISH_LIM)
    if m012._thin(o, POLISH_LIM)["under"]:
        forced += m012._force_slivers(o, lim=POLISH_LIM, max_len=0.5)
    if m012._thin(o, POLISH_LIM)["under"]:
        forced += m012._force_slivers(o, lim=POLISH_LIM, max_len=0.9)
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


# The floor (a large down-facing area) takes the plain bark key: a darker key there makes the bark family's colour
# follow face direction (K.check corr 0.6-0.7); the underside reads darker from the lighting anyway.
FLOOR_KEY = BARK
TIP_PALE = 1.0     # (round 2; was 0.7) floor faces within this of a root's tip (along the root) are its pale cut-wood end (decision 3)


def _ground_faces(o):
    """Faces lying on the ground plane (the floor cut's caps): cut wood at the root tips (the underside view's pale
    ends; decision 3: the one deliberate down-facing selection), leaf base under a leaf, shadow bark elsewhere."""
    from m011 import _Paint
    p = _Paint(o, off=o[OFF])
    n = {"cut": 0, "leaf": 0, "bark": 0}
    for f in p.bm.faces:
        if not all(abs(v.co.z) < 1e-3 for v in f.verts):
            continue
        c = p.at(f)
        key = None
        for name in ROOTS:
            u, v, off, _ = root_frame(name)
            d = (c - off).dot(u)
            lat = abs((c - root_centre(name, d)).dot(v))
            if d > ROOTS[name][1] - TIP_PALE and lat < 0.6:
                key = CUT
        nb = {p.key(g) for e in f.edges for g in e.link_faces if g is not f}
        if key is None:      # leaf base only on the small caps where a leaf meets the ground (round 2: not the long
            key = LEAF_BASE if any(k.startswith("m020_leaf") for k in nb) and f.calc_area() < 0.06 else FLOOR_KEY
            # floor fans that merely touch a leaf, which showed as green streaks in the underside view)
        f.material_index = p._mi(key)
        n["cut" if key == CUT else "leaf" if key == LEAF_BASE else "bark"] += 1
    p.done()
    return n


# ---- stages 5 + 6 (spec section 7) -----------------------------------------------------------------------------------
# Stage 5: nothing. The sheet shows an ordinary sunlit stump: no emissive key, no light (decision 8).
# Stage 6: nothing. The sheet shows no glow, sparkle, dust or chips: no socket (decision 8).


# ---- build ---------------------------------------------------------------------------------------------------------------
HERO = "ChoppedHardwoodStump"
PARTS = (("ChoppedHardwoodStumpBody", body_part), ("ChoppedHardwoodStumpCutFace", cut_face_part),
         ("ChoppedHardwoodStumpRoot", root_part), ("ChoppedHardwoodStumpLeafClump", clump_part))
UNION_PARTS = {"ChoppedHardwoodStumpBody", "ChoppedHardwoodStumpLeafClump"}
GROUND_PARTS = {"ChoppedHardwoodStumpBody", "ChoppedHardwoodStumpRoot"}


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith("_m020_"):
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
        lg["shells_merged"] = M.union_loose(o)
    if name in GROUND_PARTS or role == "hero":
        m004.floor_cut(o, z0=-off.z)
        o[OFF] = [off.x, off.y, 0.0]
    if name in UNION_PARTS or name in GROUND_PARTS or role == "hero":
        lg["clean"] = _clean_mesh(o, (0.0,) if (name in GROUND_PARTS or role == "hero") else ())
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    lg["bowties"] = M.fix_bowties(o)      # leaf hubs left pinch verts (9 on the hero, 2 on the clump part)
    if name in GROUND_PARTS or role == "hero":
        lg["ground_faces"] = _ground_faces(o)
    if name == "ChoppedHardwoodStumpBody" or role == "hero":
        # K.check's family clustering puts the cut-wood keys (hue 30-36) in the bark family (hue 22-24): the pale sawn
        # top is a separate material on the up-facing cut, so the bark family's brightness follows facing (Body corr
        # 0.50 with the cut keys, 0.15 with the bark keys alone, measured 2026-10-28)
        o["kit_shading_ok"] = "cut-wood top is its own material (sawn face), grouped with bark by hue"
    return o, lg


def build(render=True, parts=True):
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn, "part", 1000)
    h, log["hero"] = _make(HERO, hero, "hero", 4000)
    log["clumps"] = dict(CLUMP_INFO)
    _cleanup_tmp()
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    for o in order:     # M.mk stamps "studs" before the floor cut and polish: refresh it from the final mesh (round 2)
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    out = {"audit": [{k: M.audit(o)[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                                     "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces",
                                                     "normals", "ngons", "dup_verts")}
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


# ---- renders -------------------------------------------------------------------------------------------------------------
def _part_matrix(o):
    return Matrix.Translation(Vector(o[OFF]))


# the sheet's comparison cameras (decision 9) and close-ups
SHEET_VIEWS = {"f34_sheet": (0, 12), "front_sheet": (0, 10), "diag_sheet": (45, 8), "diag34_sheet": (45, 12),
               "top_sheet": (0, 89), "f34_e15_sheet": (0, 15)}     # e15: the sheet's cut-top openness (spec 3.1)
SHEET_LENS = 3.0        # the sheet's cells are drawn almost orthographic: the *_sheet shots use a 3x longer lens (the
                        # camera backs off to keep the same fill; M018's procedure), so the near front root is not
                        # blown up by perspective and the cut top opens as on the sheet


def _long_lens(kit):
    orig = kit["render_group"]

    def rg(group, path, azimuth=-22, elevation=20):
        cam = bpy.data.objects["FB_Cam"].data
        lens = cam.lens
        if "_sheet" in path:
            cam.lens = lens * SHEET_LENS
        try:
            return orig(group, path, azimuth, elevation)
        finally:
            cam.lens = lens
    return orig, rg
EXPL_LIFT = 2.0         # the exploded cut face this far above the body's top
EXPL_OUT = 3.4          # the exploded roots and clumps pulled out this far from their places


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded Construction: the body, the cut face lifted above it,
    four root modules pulled out on their azimuths, four clumps pulled out in the notches."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []

    def put(tag, part, m):
        c = bpy.data.objects.new(f"_m020_expl_{tag}", by[part].data)
        coll.objects.link(c)
        c.matrix_world = m @ _part_matrix(by[part])
        shown.append(c)
    x0 = objs[0].location.x + 40
    base = Matrix.Translation((x0, objs[0].location.y, 0))
    put("body", "ChoppedHardwoodStumpBody", base)
    put("cut", "ChoppedHardwoodStumpCutFace", base @ Matrix.Translation((0, 0, CUT_TOP + EXPL_LIFT - DISC_T)))
    for name in ROOTS:
        u, v, off, _ = root_frame(name)
        rot = Matrix.Rotation(math.radians(ROOTS[name][0] - ROOTS["L"][0]), 4, "Z")
        put("root_" + name, "ChoppedHardwoodStumpRoot", base @ Matrix.Translation(u * EXPL_OUT) @ rot @
            Matrix.Translation(-Vector((ROOTS["L"][4][0], ROOTS["L"][4][1], 0.0))))
    for k, (hub, nrm, outd, span, seed, fan, shift) in CLUMPS.items():
        P = Vector(CLUMP_INFO.get(k, {}).get("hub", hub))
        d = Vector((P.x, P.y, 0)).normalized()
        sc = span / 2.0
        m = (Matrix.Translation(P + d * EXPL_OUT + Vector((0, 0, 0.6))) @ Matrix.Diagonal((sc, sc, sc, 1.0)) @
             Matrix.Translation((0, 0, -0.6)))
        put("clump_" + k, "ChoppedHardwoodStumpLeafClump", base @ m)
    bpy.context.view_layer.update()
    return shown


# close-ups (az, el, centre in the build frame, framing radius), round 2: tightened like the sheet's close-ups - the
# cut face filling the frame from above-front, the right root's junction with the trunk at the left
CUT_CU = (-15, 35, (0.3, -0.3, 3.9), 1.45)
ROOT_CU = (0, 14, (2.8, -0.4, 1.3), 1.6)


def render_close(objs, path, az, el, centre, radius):
    """A close-up: the kit studio and camera aimed from (az, el), framed on a sphere (centre, radius)."""
    kit = K.NS["KIT"]
    fb = kit["frame_box"]
    c = Vector(centre)
    box = [c + Vector((dx, dy, dz)) * radius for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    kit["frame_box"] = lambda corners, a_, e_: fb(box, a_, e_)
    ground = bpy.data.objects.get("FB_Ground")
    if ground:
        ground.hide_render = el < 0
    cell = kit["CELL"]
    kit["CELL"] = (480, 400)
    try:
        return kit["render_group"](objs, path, az, el)
    finally:
        kit["CELL"] = cell
        kit["frame_box"] = fb
        if ground:
            ground.hide_render = False


def render_views(objs):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        if shown:
            extra["exploded"] = (shown, -20, 20)
        for o in objs[1:]:
            extra["part_" + o.name.replace("ChoppedHardwoodStump", "").lower()] = ([o], -25, 15)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            sheet = M.views(NUM, [h], extra=extra)
        finally:
            kit["render_group"] = orig
        d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
        off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
        cl = lambda tag, az, el, c, r: render_close([h], f"{d}/{tag}.png", az, el, off @ Vector(c), r)
        close = {"cut_cu": cl("cut_cu", *CUT_CU), "root_cu": cl("root_cu", *ROOT_CU),
                 "under_cu": render_close([h], f"{d}/under_cu.png", 20, -50, off @ Vector((0, 0, 0.5)), 3.0)}
        return {"sheet": sheet, **close}
    finally:
        for o in shown:
            bpy.data.objects.remove(o, do_unlink=True)
        M.display(NUM, objs, TITLE)


# ---- measuring (the study's masks, numpy) -------------------------------------------------------------------------------
REF_VIEWS = {"f34": (15, 112, 540, 412), "r34": (545, 112, 1010, 412), "front": (12, 476, 264, 662),
             "side": (264, 476, 512, 662), "rear": (512, 476, 764, 662), "top": (764, 456, 1012, 664)}
OUR_VIEWS = {"f34": "f34_sheet", "front": "front_sheet", "side": "diag_sheet", "rear": "diag_sheet",
             "r34": "diag34_sheet", "top": "top_sheet"}


def _classes(px, paper=(242, 238, 232)):
    """px (h, w, 3) sRGB 0-255 -> class map 0 none, 1 L leaves, 2 W cut wood, 3 B bark, 4 O other (study's m.py)."""
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    mx, mn = px.max(-1), px.min(-1)
    v = mx / 255.0
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    d = np.maximum(mx - mn, 1e-6)
    hh = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    near = np.abs(px - np.array(paper)).max(-1) <= 14
    out = np.full(r.shape, 4, np.uint8)
    out[v >= 0.86] = 0
    B = (s >= 0.18) & ((hh <= 45) | (hh >= 340)) & (v < 0.97)
    W = (hh >= 27) & (hh <= 52) & (s >= 0.12) & (s < 0.60) & (v >= 0.80)
    L = (s >= 0.30) & (hh >= 62) & (hh <= 160) & (g > 50)
    out[B] = 3
    out[W] = 2
    out[L] = 1
    out[near] = 0
    return out


def _load(path, box=None):
    px = K.NS["KIT"]["load_px"](path)[::-1, :, :3] * 255.0
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1]
    return np.clip(px, 0, 255)


def stats(px, paper=(242, 238, 232)):
    c = _classes(px, paper)
    obj = (c >= 1) & (c <= 3)
    cols = np.nonzero(obj.sum(0) >= 3)[0]
    rows = np.nonzero(obj.sum(1) >= 3)[0]
    bx0, bx1, by0, by1 = cols.min(), cols.max(), rows.min(), rows.max()
    W, H = bx1 - bx0, by1 - by0
    sub = c[by0:by1 + 1, bx0:bx1 + 1]
    n = max(1, ((sub >= 1) & (sub <= 3)).sum())
    out = {"wh": round(W / H, 3), "L": round((sub == 1).sum() / n, 3), "W": round((sub == 2).sum() / n, 3),
           "B": round((sub == 3).sum() / n, 3)}
    top = []
    for i in range(21):
        x = bx0 + int(i * W / 20)
        ys = np.nonzero(obj[:, max(0, x - 1):x + 2].any(1))[0]
        top.append(round((by1 - ys.min()) / H, 2) if len(ys) else None)
    wid = []
    for i in range(11):
        y = by1 - int(i * H / 10)
        xs = np.nonzero(obj[y])[0]
        wid.append((round((xs.max() - xs.min()) / W, 2), round((xs.min() - bx0) / W, 2)) if len(xs) else None)
    out.update(top=top, width=wid)
    pxs = px[by0:by1 + 1, bx0:bx1 + 1]
    hexs = lambda q: "#" + "".join(f"{int(round(x)):02X}" for x in q)
    for k, lab in ((1, "Lmed"), (2, "Wmed"), (3, "Bmed")):
        sel = pxs[sub == k]
        out[lab] = hexs(np.median(sel, axis=0)) if len(sel) else None
        if len(sel) >= 8:      # the study's lit / shade quartiles: channel medians of the brightest / darkest quarter
            srt = sel[np.argsort(sel.sum(1))]
            q = len(srt) // 4
            out[lab[0] + "lit"] = hexs(np.median(srt[-q:], axis=0))
            out[lab[0] + "shade"] = hexs(np.median(srt[:q], axis=0))
    # cut-face extent (W component bbox) and bark by height fifths
    ys, xs = np.nonzero(sub == 2)
    if len(xs):
        out["cut_f"] = (round(xs.min() / W, 2), round(xs.max() / W, 2))
        out["cut_wpx"] = round((xs.max() - xs.min()) / W, 3)
    bands = []
    for i in range(5):
        r0, r1 = by1 - int((i + 1) * H / 5), by1 - int(i * H / 5)
        sel = px[r0:r1 + 1, bx0:bx1 + 1][c[r0:r1 + 1, bx0:bx1 + 1] == 3]
        bands.append(hexs(np.median(sel, axis=0)) if len(sel) > 20 else None)
    out["Bbands"] = bands
    return out


def measure(views=("f34", "front", "side", "r34", "top")):
    """Sheet against our renders, per view (the study's masks on both; the studio floor counts as paper)."""
    ref = M.ref(NUM)
    out = {}
    for vname in views:
        a = stats(_load(ref, REF_VIEWS[vname]))
        ours = _load(f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[vname]}.png")
        corner = tuple(int(x) for x in np.median(ours[:8, :8].reshape(-1, 3), axis=0))
        b = stats(ours, paper=corner)
        out[vname] = {"sheet": a, "ours": b}
    return out
