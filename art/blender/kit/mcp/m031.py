"""031 Cave Mushroom (references/031.png): three chunky mushrooms with broad faceted rust-orange dome caps, a tan
underside drum and gill ring under each cap and fat cream stalks, standing in a lumpy ring of eleven warm-grey faceted
boulders. The big mushroom stands at the back-centre; a medium one at the front-left and a small one at the
front-right lean outward.

    import importlib, kit_models, m031; importlib.reload(kit_models); importlib.reload(m031); m031.build()

Parts as on the sheet's Exploded Construction, each built by its own function, all in one build frame (studs; front
-Y, +X right, ground z = 0, origin = the bbox bottom centre). R07 owns CaveMushroom*, so the names are CaveFungus*
(M031_spec.md section 8, decision 10):
- CaveFungusCap (cap_part): the big cap: a faceted dome (10 sectors; lip, rim, shoulder and upper rings, each turned
  half a step from the one below, so the facets are triangles and kites; a flat pentagon crown), closed underneath by
  a down-facing gill annulus and a shallow inner fan.
- CaveFungusUnderside (underside_part): the big underside drum: a 12-sided bevelled disc.
- CaveFungusStalk (stalk_part): the big stalk: a 10-sided squat bell of half-step rings, with a short 8-sided peg on
  top (the exploded's joinery peg; decision 5).
- CaveFungusRockBase (rock_base_part): the eleven rocks, united, floor-cut flat (no sockets; decision 5).

The hero (CaveFungusNode) is built from the same builders: the rocks, then each mushroom stalk -> drum -> cap (the two
small ones leaning outward about their stalk feet), united one shell at a time (exact booleans, fine merge), floor-cut
flat at the ground. Colour (stage 4) is painted by position inside the builders before the union (the union and
cleanup keep each face's key and Tint). Stages 5-6: nothing (decision 7: no emission, light or VFX). See M031_spec.md.
"""
import math
import random
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise

import kit_mcp as K
import kit_models as M
import m011
import m012
import m016

NUM, TITLE, SHEET = 31, "Cave Mushroom", "M031"
OFF = "m031_offset"
HERO = "CaveFungusNode"
CAP_P, UNDER_P, STALK_P, BASE_P = "CaveFungusCap", "CaveFungusUnderside", "CaveFungusStalk", "CaveFungusRockBase"

CAP, CAP_RIM, CAP_LIGHT = "m031_cap", "m031_cap_rim", "m031_cap_light"
GILL = "m031_gill"
STALK, STALK_LOW = "m031_stalk", "m031_stalk_low"
ROCK, ROCK_SMALL = "m031_rock", "m031_rock_small"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low specular). Stage 1 placeholders are the study's 5.4 calibration targets; stage 4 writes
# the calibrated values here (passes recorded in M031_spec.md "Stage 4").
# Pass 1 (K.calibrate on the kit's test dome against TARGETS, 2026-10-29; rendered sRGB in brackets): cap #8E5034
# (178,99,67 / B56240), cap_rim #70381A (141,74,48 / 8C4A2C), cap_light #9E5A3C (199,110,74 / C86E48), gill #856C52
# (167,131,96 / A8845F), stalk #B9AB9E (235,210,185 / EBD2B9), stalk_low #AA9A8A (215,189,161 / D8BDA0), rock #817B7E
# (162,149,146 / A49693), rock_small #6A6567 (133,122,119 / 867B78).
# Pass 2 (hero *_sheet renders, floor hidden, against the sheet's class-masked region medians, scratch reg.py; linear
# gains, geometric mean of front and f34): caps x (1.16, 1.01, 0.89) (big cap median #AD6245 / #AF6546 against
# #BA6441 / #BA6442: too dull); stalks x (1.13, 1.21, 1.32) (big stalk #DEC6AD / #DEC5AB against #EBD7C2 / #EAD7C3);
# rocks x 1.46, rock_small x 1.4 (central rock #8C827E against #A79A95, small rocks #786E6B / #695F56 against
# #82797A / #8C7E77: the hidden floor gives no bounce, so the rocks' sides render darker than on the dome); gill x 2.8
# (the underside band rendered #51402F / #493929 against #957252 / #9C7653: the drum's side sits in the cap's shadow;
# the lit Underside part then reads like the sheet's exploded disc, #BDA589 median).
# Round 2 of pass 2: the stalk gain above greyed the stalks (#C4BAB3: shaded stalk faces fell under the cream mask's
# sat 0.13 and the K share dropped to 10-14 %), so the stalks are pass 1's hue x 1.2 in linear (#CABBAA / #BAA995);
# the band still rendered #886B4D (v 0.53, under the mask's 0.55), so gill x 3.5 in all (#E8BF92).
# Round 2 (verifier round 1 blockers 1-2): the gill x 3.5 gain was painting light (the key went lighter than the stalk
# and the lit drum read butter-peach). Gill recalibrated from pass 1 (#856C52) by linear steps on the parts-shot drum
# against the exploded disc #BDA489 and the rear_sheet band against #AA8969 (the two pull R in opposite directions,
# so the key sits between them): #A08870 (hue 30, 47 % darker than the stalk key) renders #CDA782 / #9C816C.
# The rock keys were mauve (B > G, hue ~325). Warm keys (hue 11-13, sat 0.07; R > G > B) from #9E928C / #80766F,
# stepped on the part_rockbase median (#A19592 target) and the front / rear rock medians; the warm studio key light
# adds hue and saturation in the front, so the keys stay low-saturation: #9B9290 / #7E7775.
PALETTE = {CAP: ("#985031", 0.75, False), CAP_RIM: ("#783818", 0.75, False), CAP_LIGHT: ("#A95A38", 0.75, False),
           GILL: ("#A08870", 0.85, False),
           STALK: ("#CABBAA", 0.85, False), STALK_LOW: ("#BAA995", 0.85, False),
           ROCK: ("#9B9290", 0.92, False), ROCK_SMALL: ("#7E7775", 0.92, False)}
# Specular IOR Level per key prefix (the default is 0.5): the sheet's stalks and undersides are matte, and 0.5 gave the
# stalks' lit faces a gold glossy sheen (verifier round 1 minor)
SPEC = {STALK: 0.2, GILL: 0.2}

# calibration targets (spec 5.4: rendered medians of unshadowed regions on the sheet)
TARGETS = {CAP: ((0xB5, 0x62, 0x40), "vivid"), CAP_RIM: ((0x8C, 0x4A, 0x2C), "vivid"),
           CAP_LIGHT: ((0xC8, 0x6E, 0x48), "vivid"), GILL: ((0xA8, 0x84, 0x5F), "brown"),
           STALK: ((0xEB, 0xD2, 0xB9), "all"), STALK_LOW: ((0xD8, 0xBD, 0xA0), "all"),
           ROCK: ((0xA4, 0x96, 0x93), "stone"), ROCK_SMALL: ((0x86, 0x7B, 0x78), "stone")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    _spec()


def _spec():
    """Specular per SPEC prefix on every m031 material, mixes included (m031_stalk_x_low_50 etc.)."""
    for m in bpy.data.materials:
        if not m.name.startswith("FB_m031_") or not m.node_tree:
            continue
        key = m.name[3:]
        lvl = next((v for p, v in SPEC.items() if key.startswith(p)), None)
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if lvl is not None and bsdf and "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = lvl


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome. Returns {key: (hex, rendered)} and
    leaves the keys set (write them into PALETTE)."""
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


def _mix(k1, k2, t):
    """k1 -> k2 at t quantised to 25 % steps."""
    t = round(max(0.0, min(1.0, t)) * 4) / 4
    return K.mix_key(k1, k2, t)


def _zip(bm, ra, rb):
    """Triangles between two closed rings ordered by increasing angle about +Z (local frame), walking both by angle
    (half-step offset rings give triangles and kites). Returns faces. (m025)"""
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


def _ring(bm, n, r, z, off, rng=None, rj=0.0, zj=0.0):
    out = []
    for k in range(n):
        th = off + 2 * math.pi * k / n
        rr = r * (1 + (rng.uniform(-rj, rj) if rng and rj else 0.0))
        zz = z + (rng.uniform(-zj, zj) if rng and zj else 0.0)
        out.append(bm.verts.new((math.cos(th) * rr, math.sin(th) * rr, zz)))
    return out


def _fan(bm, ring, centre):
    n = len(ring)
    return [bm.faces.new((ring[k], ring[(k + 1) % n], centre)) for k in range(n)]


# ---- cap (Mushroom Cap) ----------------------------------------------------------------------------------------------
# rings (fraction of the cap height H above the lip, radius fraction of R), spec 1.4: lip, rim (widest), shoulder, upper;
# then a flat crown polygon. Each ring turned half a step from the one below.
CAP_RINGS = ((0.0, 0.90), (0.16, 1.0), (0.42, 0.94), (0.72, 0.64))
# each ring's turn in half-steps: the lip and rim aligned (a band of narrow quads: the dark lip band), the shoulder
# half a step round (triangles), the upper ring back (diamonds and kites with the shoulder row)
CAP_OFFS = (0, 0, 1, 0)
CROWN = (1.0, 0.22, 5)             # (z fraction, radius fraction, sides): the flat crown pentagon
GILL_IN = (0.04, 0.62)             # the gill annulus's inner ring (z fraction above the lip, radius fraction of R)
GILL_TOP = 0.10                    # the shallow inner fan's centre (z fraction)
CAP_JIT = (0.035, 0.015)             # radius, height jitter (fractions of R, H)
CAP_PATCH = dict(scale=0.8, level=0.15, seed=31011)
CAP_MOTTLE = dict(amp=0.03, scale=0.6, seed=31012)


def _cap(a, R, H, n, seed, az0, mat=None, tint=1.0):
    """The cap in its local frame (axis +Z, lip ring at z 0), painted: dome faces CAP with the lip band toward CAP_RIM
    (50 %, 25 % on the rim band) and broad lighter patches on the upper half; the gill annulus and inner fan GILL.
    Returns (verts, dome faces, underside faces)."""
    rng = random.Random(seed)
    bm = a.bm
    rings = []
    for i, (h, rf) in enumerate(CAP_RINGS):
        rings.append(_ring(bm, n, rf * R, h * H, az0 + CAP_OFFS[i] * math.pi / n, rng, CAP_JIT[0],
                           CAP_JIT[1] * H if i else 0.01 * H))
    zc, rc, nc = CROWN
    crown = _ring(bm, nc, rc * R, zc * H, az0 + rng.uniform(0, 2 * math.pi / nc), rng, CAP_JIT[0], 0.0)
    dome = []
    for i in range(len(rings) - 1):
        dome += _zip(bm, rings[i], rings[i + 1])
    dome += _zip(bm, rings[-1], crown)
    top = bm.faces.new(crown)
    zi, ri = GILL_IN
    inner = _ring(bm, n, ri * R, zi * H, az0 + math.pi / n, rng, 0.03, 0.0)
    under = _zip(bm, rings[0], inner)
    c = bm.verts.new((0.0, 0.0, GILL_TOP * H))
    under += _fan(bm, inner, c)
    vs = [v for r in rings for v in r] + crown + inner + [c]
    res = bmesh.ops.triangulate(bm, faces=[top], quad_method="BEAUTY", ngon_method="BEAUTY")
    dome += list(res["faces"])
    bmesh.ops.recalc_face_normals(bm, faces=dome + under)
    a._finish(vs, CAP, tint=tint)
    nf = K.noise_field(scale=CAP_PATCH["scale"], seed=CAP_PATCH["seed"] + seed)
    for f in dome:
        hf = f.calc_center_median().z / H
        if hf < 0.12:
            k = _mix(CAP, CAP_RIM, 0.5)
        elif hf < 0.36:
            k = _mix(CAP, CAP_RIM, 0.25)
        elif hf > 0.5 and nf(f.calc_center_median()) > CAP_PATCH["level"]:
            k = _mix(CAP, CAP_LIGHT, 0.5)
        elif hf > 0.5 and nf(f.calc_center_median()) > CAP_PATCH["level"] - 0.15:
            k = _mix(CAP, CAP_LIGHT, 0.25)
        else:
            k = CAP
        f.material_index = a._mi(mat or k)
    for f in under:
        f.material_index = a._mi(GILL)
    _mottle(a, dome, CAP_MOTTLE["amp"], CAP_MOTTLE["scale"], CAP_MOTTLE["seed"] + seed)
    _mottle(a, under, 0.025, 0.6, CAP_MOTTLE["seed"] + seed + 1)
    return vs, dome, under


# ---- underside drum (Cap Underside) ----------------------------------------------------------------------------------
DRUM_BEVEL = 0.07        # (x the mushroom's scale) bottom bevel height
DRUM_RB = 0.86           # bottom ring radius fraction
DRUM_RT = 0.90           # top ring radius fraction


def _drum(a, r, t, side_top, n, seed, s=1.0, az0=0.0):
    """The bevelled disc in its local frame (bottom at z 0): rings (0, 0.86 r), (bevel, r), (side_top, r), (t, 0.9 r),
    a shallow radial cone underneath and a flat top (hidden inside the cap). All GILL."""
    rng = random.Random(seed)
    bm = a.bm
    rings = [_ring(bm, n, DRUM_RB * r, 0.0, az0),
             _ring(bm, n, r, DRUM_BEVEL * s, az0, rng, 0.02, 0.0),
             _ring(bm, n, r, side_top, az0, rng, 0.02, 0.01 * s),
             _ring(bm, n, DRUM_RT * r, t, az0)]
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(n):
            j = (k + 1) % n
            faces += [bm.faces.new((r0[k], r0[j], r1[j])), bm.faces.new((r0[k], r1[j], r1[k]))]
    c = bm.verts.new((0.0, 0.0, 0.025 * s))
    faces += _fan(bm, rings[0], c)
    top = bm.faces.new(rings[-1])
    res = bmesh.ops.triangulate(bm, faces=[top], quad_method="BEAUTY", ngon_method="BEAUTY")
    faces += list(res["faces"])
    vs = [v for rr in rings for v in rr] + [c]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    a._finish(vs, GILL)
    _mottle(a, faces, 0.025, 0.6, seed + 7)
    return vs


# ---- stalk (Mushroom Stalk) ------------------------------------------------------------------------------------------
# rings (fraction of the stalk length L, radius fraction of r_max), spec 1.4: a squat bell, widest at 0.32 L
STALK_RINGS = ((0.0, 0.90), (0.30, 1.0), (0.64, 0.84), (1.0, 0.67))     # 4 rings (spec 1.4): big kites
PEG = (0.10, 0.15, 8)      # (radius, height, sides) of the Stalk part's top peg
STALK_MOTTLE = dict(amp=0.025, scale=0.6, seed=31031)


def _stalk(a, rmax, L, n, seed, az0=0.0, peg=False, low_from=0.0):
    """The bell in its local frame (bottom at z 0). Colour: STALK, the lowest part (from low_from: the hero's visible
    foot) toward STALK_LOW at 50 % / 25 %."""
    rng = random.Random(seed)
    bm = a.bm
    rings = [_ring(bm, n, rf * rmax, h * L, az0 + (i % 2) * math.pi / n, rng, 0.03, 0.02 * L if 0 < i < len(STALK_RINGS) - 1 else 0.0)
             for i, (h, rf) in enumerate(STALK_RINGS)]
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        faces += _zip(bm, r0, r1)
    faces += _fan(bm, rings[0], bm.verts.new((0.0, 0.0, 0.0)))
    extra = []
    if peg:
        pr, ph, pn = PEG
        lo = _ring(bm, pn, pr, L, az0 + math.pi / pn)
        hi = _ring(bm, pn, pr, L + ph, az0 + math.pi / pn)
        faces += _zip(bm, rings[-1], lo)
        for k in range(pn):
            j = (k + 1) % pn
            faces += [bm.faces.new((lo[k], lo[j], hi[j])), bm.faces.new((lo[k], hi[j], hi[k]))]
        ct = bm.verts.new((0.0, 0.0, L + ph))
        faces += _fan(bm, hi, ct)
        extra = lo + hi + [ct]
    else:
        faces += _fan(bm, rings[-1], bm.verts.new((0.0, 0.0, L)))
    vs = list({v for f in faces for v in f.verts})
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    a._finish(vs, STALK)
    span = max(1e-6, L - low_from)
    for f in faces:
        hf = (f.calc_center_median().z - low_from) / span
        if hf < 0.15:
            f.material_index = a._mi(_mix(STALK, STALK_LOW, 0.5))
        elif hf < 0.32:
            f.material_index = a._mi(_mix(STALK, STALK_LOW, 0.25))
    if extra:
        for f in K.faces_of(extra):
            f.material_index = a._mi(STALK_LOW)
    _mottle(a, faces, STALK_MOTTLE["amp"], STALK_MOTTLE["scale"], STALK_MOTTLE["seed"] + seed)
    return vs


# ---- the three mushrooms (spec 2.1) ----------------------------------------------------------------------------------
# name -> foot (x, y, z), lean (deg, toward azimuth deg from +X), stalk r_max, cap R, cap H, crown z target, sectors
# (cap, drum, stalk), drop (lip above the drum bottom), seed. The stalk length follows from the crown target.
SHROOMS = {
    "big": dict(foot=(0.32, 0.30, 0.25), lean=(0.0, 0.0), rmax=0.75, R=1.50, H=1.48, crown=3.60, n=(10, 12, 10),
                drum=1.0, drop=0.38, seed=31101, az0=0.0),
    "medium": dict(foot=(-0.95, -0.58, 0.12), lean=(18.0, 205.0), rmax=0.47, R=0.78, H=0.78, crown=2.25,
                   n=(9, 10, 8), drum=0.525, drop=0.20, seed=31102, az0=250.0),
    "small": dict(foot=(1.36, -0.72, 0.10), lean=(20.0, 315.0), rmax=0.40, R=0.65, H=0.55, crown=1.69,
                  n=(8, 10, 8), drum=0.44, drop=0.17, seed=31103, az0=290.0),
}
STALK_IN = 0.08          # (x scale) the stalk's top sinks this far into the drum
SHROOM_INFO = {}


def _stack(sp):
    """Local-axis heights for one mushroom (from the stalk foot): stalk length, drum bottom / side top / top, lip."""
    s = sp["R"] / 1.5
    th, _ = sp["lean"]
    D = (sp["crown"] - sp["foot"][2]) / math.cos(math.radians(th))
    L = D - sp["H"] - sp["drop"] + STALK_IN * s
    d0 = L - STALK_IN * s
    lip = d0 + sp["drop"]
    t = sp["drop"] + GILL_TOP * sp["H"] + 0.05 * s
    side_top = sp["drop"] - 0.03 * s
    return dict(s=s, L=L, d0=d0, lip=lip, t=t, side_top=side_top)


def _shroom_matrix(sp):
    th, az = sp["lean"]
    m = Matrix.Translation(Vector(sp["foot"]))
    if th:
        d = Vector((math.cos(math.radians(az)), math.sin(math.radians(az)), 0.0))
        axis = Vector((0.0, 0.0, 1.0)).cross(d)
        m = m @ Matrix.Rotation(math.radians(th), 4, axis)
    return m


def _place(bm, vs, m):
    bmesh.ops.transform(bm, matrix=m, verts=[v for v in vs if v.is_valid])


def _shroom(a, name, low_from=None):
    """One assembled mushroom (stalk, drum, cap), each piece its own closed shell, built in the local frame and
    leaned about the stalk foot."""
    sp = SHROOMS[name]
    st = _stack(sp)
    m = _shroom_matrix(sp)
    nc, nd, ns = sp["n"]
    az0 = math.radians(sp["az0"])
    lf = low_from if low_from is not None else 0.0
    sv = _stalk(a, sp["rmax"], st["L"], ns, sp["seed"], az0=az0, low_from=lf)
    _place(a.bm, sv, m)
    dv = _drum(a, sp["drum"], st["t"], st["side_top"], nd, sp["seed"] + 1, s=st["s"], az0=az0)
    _place(a.bm, dv, m @ Matrix.Translation((0, 0, st["d0"])))
    cv, _, _ = _cap(a, sp["R"], sp["H"], nc, sp["seed"] + 2, az0)
    _place(a.bm, cv, m @ Matrix.Translation((0, 0, st["lip"])))
    SHROOM_INFO[name] = {k: round(v, 3) for k, v in st.items()}
    return sv, dv, cv


# ---- rocks (Rock Base, spec 2.3) -------------------------------------------------------------------------------------
ROCK_Z0 = -0.06          # rock bottoms below the ground (the floor cut makes one flat underside)
# round 2: a bulged dome (widest at 0.3 h, a small 3-point crown) so the small rocks read as squat boulders, not the
# round-1 upright slabs ((0, 1.0) -> (0.4, 0.9) -> (0.78, 0.64) -> (1.0, 0.38 x 4): near-vertical walls, flat tops)
ROCK_RINGS = ((0.0, 0.92, 7), (0.3, 1.0, 7), (0.62, 0.84, 7), (0.86, 0.5, 6), (1.0, 0.15, 3))
ROCK_RINGS_BIG = ((0.0, 1.0, 8), (0.3, 0.95, 8), (0.6, 0.8, 8), (0.85, 0.5, 6), (1.0, 0.2, 3))
# (label, x, y, w, d, h, key, seed). The back rocks R2 / R3 and the side pebbles P3 / P6 sit out beyond the big
# cap's plan outline, so the top view shows rock round the rim (spec 3.3); R1 runs forward past the cap's front edge.
ROCKS = (
    ("R1", 0.15, 0.00, 2.40, 2.45, 1.00, ROCK, 31201),
    ("R2", 1.30, 1.00, 1.40, 1.20, 0.88, ROCK, 31202),
    ("R3", -1.02, 1.08, 1.20, 1.15, 0.82, ROCK, 31203),
    ("R4", -1.00, -0.52, 1.10, 1.00, 0.62, ROCK_SMALL, 31204),
    ("R5", 1.18, -0.56, 1.05, 0.95, 0.40, ROCK_SMALL, 31205),
    ("P1", -1.12, -1.16, 0.82, 0.74, 0.54, ROCK_SMALL, 31206),
    ("P2", -1.78, -0.38, 0.96, 0.96, 0.72, ROCK_SMALL, 31207),
    ("P3", -1.68, 0.52, 0.80, 0.75, 0.55, ROCK_SMALL, 31208),
    ("P4", 1.24, -1.18, 0.78, 0.75, 0.56, ROCK_SMALL, 31209),
    ("P5", 1.90, -0.40, 0.70, 0.70, 0.50, ROCK_SMALL, 31210),
    ("P6", 1.82, 0.42, 0.75, 0.70, 0.52, ROCK_SMALL, 31211),
    ("R6", 0.25, 1.30, 1.35, 1.00, 0.78, ROCK, 31212),        # back-centre: the rear cell's rock behind the stalk
)
ROCK_YAW_JIT = [0.0]
ROCK_PATCH = dict(scale=0.9, level=0.12, seed=31221)
ROCK_MOTTLE = dict(amp=0.05, scale=0.5, seed=31222)
ROCK_INFO = {}


def _rocks(a):
    out = {}
    for lab, x, y, w, d, h, key, seed in ROCKS:
        rings = ROCK_RINGS_BIG if lab == "R1" else ROCK_RINGS
        yaw = random.Random(seed).uniform(0, 2 * math.pi) + math.radians(ROCK_YAW_JIT[0])
        vs = K.hull_rock(a, (w, d, h - ROCK_Z0), loc=(x, y, ROCK_Z0), seed=seed, mat=key, rings=rings, jitter=0.10,
                         rot=yaw, keep_bottom=True)
        _tri(a.bm, _faces(vs))
        bmesh.ops.recalc_face_normals(a.bm, faces=_faces(vs))
        out[lab] = (vs, key, h)
        ROCK_INFO[lab] = dict(xy=(x, y), size=(w, d, h), faces=len(_faces(vs)))
    _paint_rocks(a, out)
    trees = {k: K.bvh_of(v[0]) for k, v in out.items()}
    for k, t in trees.items():
        ROCK_INFO[k]["touch"] = [j for j, u in trees.items() if j != k and t.overlap(u)]
    return out


def _paint_rocks(a, rocks):
    """Big rocks: ROCK, the ground band toward ROCK_SMALL (50 % under 0.15 h, 25 % under 0.32 h), contact faces
    near a neighbour 25 %. Small rocks: ROCK_SMALL with broad patches 25 % toward ROCK. Position only."""
    nf = K.noise_field(scale=ROCK_PATCH["scale"], seed=ROCK_PATCH["seed"])
    trees = {k: K.bvh_of(v[0]) for k, v in rocks.items()}
    for i, (lab, (vs, key, h)) in enumerate(rocks.items()):
        for f in _faces(vs):
            c = f.calc_center_median()
            hf = c.z / h
            if key == ROCK:
                t = 0.5 if hf < 0.15 else 0.25 if hf < 0.32 else 0.0
                if not t and hf < 0.7:
                    for j, tr in trees.items():
                        if j == lab:
                            continue
                        loc = tr.find_nearest(c)
                        if loc[0] is not None and loc[3] < 0.2:
                            t = 0.25
                            break
                k = _mix(ROCK, ROCK_SMALL, t)
            else:
                k = _mix(ROCK_SMALL, ROCK, 0.25) if nf(c) > ROCK_PATCH["level"] else ROCK_SMALL
            f.material_index = a._mi(k)
        _mottle(a, _faces(vs), ROCK_MOTTLE["amp"], ROCK_MOTTLE["scale"], ROCK_MOTTLE["seed"] + i,
                tint=1.0 + random.Random(i * 7 + 3).uniform(-0.04, 0.04))


# ---- parts -----------------------------------------------------------------------------------------------------------
def cap_part(a):
    sp = SHROOMS["big"]
    _cap(a, sp["R"], sp["H"], sp["n"][0], sp["seed"] + 2, math.radians(sp["az0"]))


def underside_part(a):
    sp = SHROOMS["big"]
    st = _stack(sp)
    _drum(a, sp["drum"], st["t"], st["side_top"], sp["n"][1], sp["seed"] + 1, s=st["s"],
          az0=math.radians(sp["az0"]))


def stalk_part(a):
    sp = SHROOMS["big"]
    st = _stack(sp)
    _stalk(a, sp["rmax"], st["L"], sp["n"][2], sp["seed"], az0=math.radians(sp["az0"]), peg=True)


def rock_base_part(a):
    _rocks(a)


# ---- hero ------------------------------------------------------------------------------------------------------------
# each stalk's paint ramp starts where it leaves the rocks (the visible foot)
STALK_VISIBLE = {"big": 0.85, "medium": 0.35, "small": 0.30}


def hero(a):
    ROCK_INFO.clear()
    SHROOM_INFO.clear()
    _rocks(a)
    caps = {}
    for name in ("big", "medium", "small"):
        sp = SHROOMS[name]
        th = math.radians(sp["lean"][0])
        lf = max(0.0, (STALK_VISIBLE[name] - sp["foot"][2]) / math.cos(th))
        caps[name] = _shroom(a, name, low_from=lf)[2]
    trees = {k: K.bvh_of(v) for k, v in caps.items()}
    SHROOM_INFO["cap_touch"] = [(i, j) for i in trees for j in trees if i < j and trees[i].overlap(trees[j])]


NOTES = {
    HERO: "Cave mushroom patch (CaveMushroomPatch node): three chunky mushrooms with broad faceted rust-orange dome "
          "caps (dark lip, tan underside drum and gill ring) on fat cream stalks, the big one at the back-centre, a "
          "medium one front-left and a small one front-right leaning outward, in a lumpy ring of eleven warm-grey "
          "faceted boulders; one closed mesh, flat underside. No VFX",
    CAP_P: "Mushroom Cap (reusable): faceted rust-orange dome cap, 10 sectors and 4 facet rows, flat crown polygon, "
           "dark lip band, closed by a tan down-facing gill annulus",
    UNDER_P: "Cap Underside (reusable): 12-sided bevelled tan disc that hangs under the cap",
    STALK_P: "Mushroom Stalk (reusable): 10-sided faceted cream bell stalk with a short top peg",
    BASE_P: "Rock Base (reusable): eleven faceted warm-grey boulders, a wide low central dome among them, flat "
            "underside",
}


# ---- union, floor cut, cleanup (m025 / m023) -------------------------------------------------------------------------
FINE_MERGE = 0.002
UNION_RETRIES = []


def _union_fine(o, merge=FINE_MERGE):
    """M.union_loose with a finer post-union merge and a guard against a union that drops most of the mesh (m025)."""
    bpy.context.view_layer.update()
    act = bpy.context.view_layer.objects.active
    if act and act.mode != "OBJECT":
        with bpy.context.temp_override(active_object=act, object=act):
            bpy.ops.object.mode_set(mode="OBJECT")
    others = M.split_loose(o)
    bpy.context.view_layer.update()
    for p in others:
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
        me = p.data
        bpy.data.objects.remove(p, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
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
    """m004.floor_cut with a triangle fill of the cut loops (no n-gon cap)."""
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
    """Quads split, slivers forced open, origin back at the bottom centre, UVs redone (m025)."""
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
    """Faces on the ground plane (the floor cut's cap): one even ROCK (the Base Underside close-up's flat grey bottom;
    its darker look there is shade). Not ROCK_SMALL: a large dark down-facing area made the rock family's colour
    follow facing (K.check corr 0.50 on the RockBase part)."""
    p = m011._Paint(o, off=o[OFF])
    n = 0
    for f in p.bm.faces:
        if all(abs(v.co.z) < 1e-3 for v in f.verts):
            f.material_index = p._mi(ROCK)
            n += 1
    p.done()
    return n


def _make(name, fn, role, budget, union=False, ground=False):
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget, collision="hull",
             tint_var=0.03)
    off = M._build_offset(fn)
    o[OFF] = list(off)
    lg = {}
    if union:
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
    K.drop_unused_slots(o)
    return o, lg


def _fused_ok(o):
    a = M.audit(o)
    return (a["shells"] == 1 and not a["nonmanifold_edges"] and not a.get("nonmanifold_verts") and
            not a["boundary_edges"] and a["normals"] == "outward"
            and not m016._self_hits(o)[0] and not m012._thin(o, POLISH_LIM)["under"])


def _inverted(o):
    """Faces whose normal points into the solid (a ray from just outside the face, along its normal, that hits the
    mesh an odd number of times). 0 on a clean closed mesh."""
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    bad = 0
    for f in bm.faces:
        p = f.calc_center_median() + f.normal * 1e-4
        n, x = 0, p.copy()
        for _ in range(50):
            hit = tree.ray_cast(x, f.normal)
            if hit[0] is None:
                break
            n += 1
            x = hit[0] + f.normal * 1e-5
        bad += n % 2
    bm.free()
    return bad


# ---- stages 5 + 6 (spec section 7) -------------------------------------------------------------------------------------
# Stage 5: nothing. The sheet shows ordinary sunlit mushrooms: no emissive key, no light (decision 7; WorldModeling 9:
# cave mushrooms get their visibility from shape and placed lighting, not emission).
# Stage 6: nothing. The sheet says "No additional details, variants, or effects" and shows none (decision 7).


# ---- build -----------------------------------------------------------------------------------------------------------
PARTS = ((CAP_P, cap_part, False, False), (UNDER_P, underside_part, False, False),
         (STALK_P, stalk_part, False, False), (BASE_P, rock_base_part, True, True))
TARGET_SIZE = ((4.4, 0.25), (3.5, 0.3), (3.6, 0.2))
HERO_TRIES = 4
HERO_YAW_STEP = 13.0


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith("_m031_"):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m031_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith(("_m031", "_probe", "T_Calib",
                                                                                 "CaveFungus"))]
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
        for name, fn, union, ground in PARTS:
            for attempt in range(HERO_TRIES if union else 1):
                ROCK_YAW_JIT[0] = attempt * HERO_YAW_STEP
                objs[name], log[name] = _make(name, fn, "part", 1000, union=union, ground=ground)
                if not union or _fused_ok(objs[name]):
                    break
            log[name]["attempt"] = attempt
    # the hero guard: a rock grazing a stalk or another rock can leave a sliver pair after the union; then every rock
    # turns HERO_YAW_STEP degrees about its own axis and the hero is rebuilt
    for attempt in range(HERO_TRIES):
        ROCK_YAW_JIT[0] = attempt * HERO_YAW_STEP
        h, log["hero"] = _make(HERO, hero, "hero", 4000, union=True, ground=True)
        if _fused_ok(h):
            break
    log["hero"]["attempt"] = attempt if _fused_ok(h) else -1
    log["shrooms"] = dict(SHROOM_INFO)
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
    self_hits = {o.name: m016._self_hits(o)[0] for o in order}
    thin = {o.name: m012._thin(o, POLISH_LIM) for o in order}
    inverted = {o.name: _inverted(o) for o in order}
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
        if inverted[o.name]:
            problems.append(f"{o.name}: {inverted[o.name]} inverted faces")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 7: none)")
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts")} for au in audits],
           "thin": thin, "self_hits": self_hits, "inverted": inverted, "log": log, "problems": problems,
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "uv": {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped",
                                                                            "min_gap", "border", "density",
                                                                            "stretch_conformal_p95")}
                  for o in order}}
    out["build_s"] = round(time.time() - t0, 1)
    if render:
        out["views"] = render_views(order)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders ---------------------------------------------------------------------------------------------------------
# the sheet's comparison cameras (decision 9): front / side / rear at 9 deg; the f34 cell (and, unflipped, the r34
# cell) an aligned front view from 14 deg; the kit top judged by counts and shares
SHEET_VIEWS = {"front_sheet": (0, 9), "side_sheet": (90, 9), "rear_sheet": (180, 9), "f34_sheet": (0, 14),
               "top_sheet": (0, 89)}
SHEET_LENS = 3.0        # the sheet's cells are near-orthographic: the *_sheet shots use a 3x longer lens (M018/M020)
PARTS_SHOT = (-20, 15)


def _long_lens(kit):
    """render_group with a long lens and the studio floor hidden for the *_sheet shots (measured shots: no floor, no
    ground shadow in the silhouette)."""
    orig = kit["render_group"]

    def rg(group, path, azimuth=-22, elevation=20):
        cam = bpy.data.objects["FB_Cam"].data
        lens = cam.lens
        ground = bpy.data.objects.get("FB_Ground")
        gh = ground.hide_render if ground else None
        name = path.rsplit("/", 1)[-1]
        if "_sheet" in name:
            cam.lens = lens * SHEET_LENS
            if ground:
                ground.hide_render = True
        try:
            return orig(group, path, azimuth, elevation)
        finally:
            cam.lens = lens
            if ground:
                ground.hide_render = gh
    return orig, rg


def _part_matrix(o):
    return Matrix.Translation(Vector(o[OFF]))


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded Construction: the rock base at the bottom, the big
    stalk, drum and cap stacked above it with gaps, and a mid-size set (the same parts at 0.55) at the right."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []

    def put(tag, part, m):
        c = bpy.data.objects.new(f"_m031_expl_{tag}", by[part].data)
        coll.objects.link(c)
        c.matrix_world = m @ _part_matrix(by[part])
        shown.append(c)
    x0 = objs[0].location.x + 40
    base = Matrix.Translation((x0, objs[0].location.y, 0))
    sp = SHROOMS["big"]
    st = _stack(sp)
    put("base", BASE_P, base)
    bx, by_ = sp["foot"][0] - 0.5, sp["foot"][1]
    g = 0.55                     # the gap between the stacked parts (the sheet's dashed arrows)
    z = 1.25
    put("stalk", STALK_P, base @ Matrix.Translation((bx, by_, z)))
    put("drum", UNDER_P, base @ Matrix.Translation((bx, by_, z + st["L"] + g)))
    put("cap", CAP_P, base @ Matrix.Translation((bx, by_, z + st["L"] + g + st["t"] + g)))
    s = 0.55
    sm = Matrix.Diagonal((s, s, s, 1))
    mx, my, mz = bx + 2.6, sp["foot"][1], 0.9
    put("stalk_m", STALK_P, base @ Matrix.Translation((mx, my, mz)) @ sm)
    put("drum_m", UNDER_P, base @ Matrix.Translation((mx, my, mz + s * st["L"] + 0.4)) @ sm)
    put("cap_m", CAP_P, base @ Matrix.Translation((mx, my, mz + s * (st["L"] + st["t"]) + 0.8)) @ sm)
    bpy.context.view_layer.update()
    return shown


def render_close(objs, path, az, el, centre, radius):
    """A close-up from (az, el), framed on a sphere (centre, radius) (m023)."""
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


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        if shown:
            extra["exploded"] = (shown, -10, 12)
        for o in objs[1:]:
            extra["part_" + o.name.replace("CaveFungus", "").lower()] = ([o], *PARTS_SHOT)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            sheet = M.views(NUM, [h], extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet}
        if close:
            d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
            off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
            sp = SHROOMS["big"]
            st = _stack(sp)
            cu = Vector((sp["foot"][0], sp["foot"][1], sp["foot"][2] + st["lip"]))
            # the Cap Underside close-up: the big cap's gill ring and drum from below and in front
            out["under_cu"] = render_close([h], f"{d}/cap_under_cu.png", 10, -25, off @ cu, 1.7)
            co = objs[1] if len(objs) > 1 else None
            if co is not None:
                out["cap_part_under"] = render_close([co], f"{d}/part_cap_under.png", 15, -35,
                                                     co.matrix_world @ Vector((0, 0, 0.5)), 1.6)
        return out
    finally:
        for o in shown:
            bpy.data.objects.remove(o, do_unlink=True)
        M.display(NUM, objs, TITLE)


def preview(names=("front_sheet", "f34_sheet", "side_sheet", "rear_sheet", "top_sheet"), vfx=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = _long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig
