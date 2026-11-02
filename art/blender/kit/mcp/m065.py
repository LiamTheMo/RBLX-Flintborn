"""065 Forest Wildflowers (references/065.png): a repeated forest-floor flower clump. Three different chunky heads on
thick square stems over a rosette of 17 broad, thick, faceted kite leaves round a hidden hexagonal hub, with five
faceted stones tucked under the leaf tips:
- a six-sided purple bell with six flared pointed lobes and a real inside, hanging from a shepherd's crook (far left);
- a blue five-petal star of broad pointed lozenges round a pale-lemon octagonal bead, the tallest head;
- a pink cupped bloom of five outer and five inner petals round a golden bead, lowest, at the right.
No glow, no VFX.

    import importlib, kit_models, m065; importlib.reload(kit_models); importlib.reload(m065); m065.build()

Build frame: studs, front -Y, +X right, ground z 0, the hub axis on (0, 0). Every object ends with its origin at its
bbox bottom centre; o["m065_offset"] is that origin in the build frame. Names (spec 8, decision 2):
- ForestBlooms (hero): hub + 17 leaves + 3 square stems (the bell's with its crook) + bell and cap + star (5 petals,
  bead, calyx) + bloom (10 petals, bead, calyx) + 5 stones, one object of separate closed shells (no booleans).
- ForestBloomsPurpleBell, ForestBloomsBlueStar, ForestBloomsPinkBloom, ForestBloomsStem, ForestBloomsLeaf,
  ForestBloomsRockGrey, ForestBloomsRockBrown, ForestBloomsLeafBase (hub + fan F1-F5 + rim B1-B4).
Collision none everywhere (decision 8). Every head, petal and leaf is placed by growth (head normal, leaf azimuth /
pitch / a fixed roll), never turned toward a camera. Colour is painted by role and by position along each piece,
never by facing. Stages 5-6: none (the sheet shows no glow, light or effect). See M065_spec.md.
"""
import json
import math
import random
import time

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M
import m012
import m033
import m047

NUM, TITLE, SHEET = 65, "Forest Wildflowers", "M065"
OFF = "m065_offset"
PFX = "_m065_"
HERO = "ForestBlooms"
BELL_P, STAR_P, BLOOM_P = "ForestBloomsPurpleBell", "ForestBloomsBlueStar", "ForestBloomsPinkBloom"
STEM_P, LEAF_P, BASE_P = "ForestBloomsStem", "ForestBloomsLeaf", "ForestBloomsLeafBase"
ROCKG_P, ROCKB_P = "ForestBloomsRockGrey", "ForestBloomsRockBrown"

BELL, BELL_DEEP = "m065_bell", "m065_bell_deep"
STAR, STAR_DEEP, STAR_BEAD = "m065_star", "m065_star_deep", "m065_star_bead"
PINK, PINK_DEEP, BLOOM_BEAD = "m065_pink", "m065_pink_deep", "m065_bloom_bead"
LIGHT, MID, DARK, STEM = "m065_leaf_light", "m065_leaf_mid", "m065_leaf_dark", "m065_stem"
ROCK_G, ROCK_B = "m065_rock_grey", "m065_rock_brown"
LADDER = (DARK, MID, LIGHT)                  # leaf tone value 0..2

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
BURY = 0.05
SINK = 0.02                                  # the hub, the rim leaves and the stones sink this far (decision 10: <= 0.03)
Z = Vector((0, 0, 1))

# key -> (hex, roughness, low specular). Stage 4 writes the calibrated values here (spec "Stage 4").
# K.calibrate (6 rounds on the kit dome, 2026-11-01): key -> rendered median against the TARGETS below
PALETTE = {
    BELL: ("#7B57D0", 0.75, True),          # renders #9160F0 (target #9160F1) at #7855CC; raised a step for the rear
    BELL_DEEP: ("#5A3FB8", 0.8, True),      # #6A45D7 (#6A45D8)
    STAR: ("#7084F2", 0.75, True),          # #7F92FF (#7C8EFC) at #6A7CF0; raised: the hero front read #6B7BF6
    STAR_DEEP: ("#515FCF", 0.75, True),     # #5E6DF4 (#5D6CF4)
    STAR_BEAD: ("#ECC862", 0.6, False),     # #FFE66F (#FDE76F) at #ECBC60; star_cu read orange (#FFD568)
    PINK: ("#EC6F96", 0.75, True),          # #FF77A2 (#FB77A3) at #EC678E; raised: the hero front read #FF618C
    PINK_DEEP: ("#C33F6A", 0.75, True),     # #F64575 (#F64575)
    BLOOM_BEAD: ("#B49400", 0.6, False),    # #E2B422 (#E2B30D)
    LIGHT: ("#7DA428", 0.8, True),          # #98C628 (#97C728)
    MID: ("#537C16", 0.85, True),           # #619217 (#5F9117)
    DARK: ("#3A6A1E", 0.85, True),          # #478020 (#498025) at #3E6E20; a step deeper for the front tone shares
    STEM: ("#52871F", 0.85, True),          # #58951D (#57941D) at #4C7E1D; raised: the parts-shot stem read #477819
    # the dome sampler's "stone" filter (sat < 0.18) misses this warm grey (sat 0.19): set by the brown key's
    # measured transfer and checked on the parts shot instead, kept R > G > B (never lavender)
    ROCK_G: ("#817673", 0.9, True),
    ROCK_B: ("#8E5F3F", 0.9, True),         # #A7683F (#A8673E) at #885B3D; the parts shot read #945B37
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions), K.sample kinds
TARGETS = {BELL: ((0x91, 0x60, 0xF1), "vivid"), BELL_DEEP: ((0x6A, 0x45, 0xD8), "vivid"),
           STAR: ((0x7C, 0x8E, 0xFC), "vivid"), STAR_DEEP: ((0x5D, 0x6C, 0xF4), "vivid"),
           STAR_BEAD: ((0xFD, 0xE7, 0x6F), "vivid"),
           PINK: ((0xFB, 0x77, 0xA3), "vivid"), PINK_DEEP: ((0xF6, 0x45, 0x75), "vivid"),
           BLOOM_BEAD: ((0xE2, 0xB3, 0x0D), "vivid"),
           LIGHT: ((0x97, 0xC7, 0x28), "vivid"), MID: ((0x5F, 0x91, 0x17), "green"),
           DARK: ((0x49, 0x80, 0x25), "green"), STEM: ((0x57, 0x94, 0x1D), "green"),
           ROCK_G: ((0xA8, 0x93, 0x88), "stone"), ROCK_B: ((0xA8, 0x67, 0x3E), "brown")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m065_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k == "m065_" + tail), None)
            if k1 in PALETTE and k2 and pct.isdigit():
                K.fk().KIT_PALETTE.pop(key, None)
                K.mix_key(k1, k2, int(pct) / 100)


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
_band = m047._band


def _mix(k1, k2, t):
    t = round(max(0.0, min(1.0, t)) * 4) / 4
    return K.mix_key(k1, k2, t)


def _tone(v):
    """Leaf tone value on LADDER (0 dark, 1 mid, 2 light; fractions mix the neighbours in 25 % steps)."""
    v = max(0.0, min(2.0, v))
    i = min(1, int(v))
    return _mix(LADDER[i], LADDER[i + 1], v - i)


def _paint(a, faces, key):
    mi = a._mi(key)
    for f in faces:
        if f.is_valid:
            f.material_index = mi


def _tint(a, faces, k):
    for f in faces:
        for l in f.loops:
            t = l[a.tint_layer][0] * k
            l[a.tint_layer] = (t, t, t, 1.0)


def _close(a, vs, fs, key, tint=1.0):
    bmesh.ops.recalc_face_normals(a.bm, faces=fs)
    a._finish(vs, key, tint=tint)


def _dir(az, el):
    a, e = math.radians(az), math.radians(el)
    return Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))


def _bez(p0, p1, p2, t):
    return p0 * (1 - t) ** 2 + p1 * (2 * t * (1 - t)) + p2 * (t * t)


def _bezd(p0, p1, p2, t):
    return (p1 - p0) * (2 * (1 - t)) + (p2 - p1) * (2 * t)


def _ring(p, u, v, r, n, rot=0.0):
    return [p + (u * math.cos(rot + 2 * math.pi * k / n) + v * math.sin(rot + 2 * math.pi * k / n)) * r
            for k in range(n)]


def _perp(n):
    e1 = Z.cross(n)
    e1 = e1.normalized() if e1.length > 1e-6 else Vector((1, 0, 0))
    return e1, n.cross(e1).normalized()


def _rng(name, k=0):
    return random.Random(sum(map(ord, name)) * 31 + k * 7 + 65)


def _cam(az, el):
    """Unit vector from the target toward a camera at (az, el) (az 0 = the front, -Y; 90 = +X)."""
    a_, e_ = math.radians(az), math.radians(el)
    return Vector((math.sin(a_) * math.cos(e_), -math.cos(a_) * math.cos(e_), math.sin(e_)))


def _azel(v):
    v = v.normalized()
    return math.degrees(math.atan2(v.x, -v.y)), math.degrees(math.asin(max(-1.0, min(1.0, v.z))))


# ---- explode state and piece register -----------------------------------------------------------------------------------
EXPLODE = {"on": False}
PIECES = []                                  # (kind, name, centroid in the build frame) per shell, in build order


def _shift(vec):
    return Vector(vec) if EXPLODE["on"] else Vector()


def _reg(kind, name, vs):
    if not EXPLODE["on"]:
        PIECES.append((kind, name, sum((v.co for v in vs), Vector()) / len(vs)))


# ---- hub (spec 2.2: a 6-sided block with a low chamfer on top, closed, hidden by the leaves) ----------------------------
HUB_R0, HUB_R1, HUB_RC, HUB_ZC, HUB_TOP = 0.25, 0.215, 0.175, 0.15, 0.18


def hub(a):
    bm = a.bm
    rng = random.Random(65001)
    rings = []
    for z, r in ((-SINK, HUB_R0), (HUB_ZC, HUB_R1), (HUB_TOP, HUB_RC)):
        rings.append([bm.verts.new((math.cos(math.pi / 6 + k * math.pi / 3) * r * (1 + rng.uniform(-0.05, 0.05)),
                                    math.sin(math.pi / 6 + k * math.pi / 3) * r * (1 + rng.uniform(-0.05, 0.05)), z))
                      for k in range(6)])
    side = _band(bm, rings[0], rings[1]) + _band(bm, rings[1], rings[2])
    bot = bm.faces.new(list(reversed(rings[0])))
    top = bm.faces.new(rings[2])
    vs = [v for r in rings for v in r]
    _close(a, vs, side + [bot, top], DARK)
    _tint(a, side + [bot, top], 1.0 + rng.uniform(-0.03, 0.03))
    _reg("hub", "hub", vs)
    return vs


# ---- leaves (spec 2.4: closed faceted kites with a ridge V and a keel, along an arched spine) ---------------------
# fan leaves: Bezier parameter of the section stations (tip point at 1.0) and half-width per station (fraction of W).
# The widest station sits at half the length, where the fan has spread apart (wider low down, five leaves round a
# 0.2-radius hub cut through each other)
LEAF_ST = (0.0, 0.50, 0.79)
LEAF_HW = (0.22, 0.50, 0.35)                # fix round 1: broad from low down (0.15 read as shard wedges)
PET_ST, PET_HW = (0.0, 0.42, 0.76), (0.14, 0.50, 0.36)   # spreading leaves: blade stations after the petiole
PET_LEN, PET_HWABS = 0.20, 0.055             # petiole stub length, its half-width (a 0.11-wide stub)
RIM_ST, RIM_HW = (0.0, 0.52), (0.24, 0.50)
SPINE_HW = (0.14, 0.36, 0.50)              # drooping leaves: base on the hub, the blade's upper end, its widest
EDGE = {"fan": 0.03, "spread": 0.03, "droop": 0.03, "rim": 0.05}   # half the edge thickness (rim edges 0.10)
RIDGE = {"fan": 19.0, "spread": 18.0, "droop": 17.0, "rim": 15.0}  # each half rises this much to the ridge
KEEL = 0.025
FAN_Z, RING_Z, BASE_R = 0.13, 0.08, 0.11     # leaf base points on the hub (inside it)
FAN_BR = 0.19                                # fan leaf base radius (per leaf "br"): the fan rises from the hub's rim
# name -> tier, azimuth (growth direction: its face turns up and out along it), tip, W, spine: pitch (Bezier control
# along az / pitch at half the chord) or ctrl, or spine (drooping leaves: the blade's upper end and its widest point);
# roll (a fixed growth twist, deg); tone per band (base, body, tip) on LADDER; base (rim leaves: on the ground)
LEAVES = {
    # leaf base: the five-leaf upright fan behind the stems
    # (the top faces turn up and in toward the axis, as a rosette leaf's upper side does; the fixed growth rolls tip
    # neighbours' planes apart: no two leaves of a tier within 20 deg of one plane)
    # Fix round 1: the fan rises from the hub's rim (FAN_BR 0.19), clear of the stems that leave its centre, spaced
    # 36-40 deg apart (160 / 128 / 92 / 52 / 22) and 10 % narrower, the outer pair leaning out lower (pitch 50): the
    # star stem rises in the gap between F3 and F4, F2 is off the bell stem, no leaf is more than 13 % inside another
    "F1": dict(tier="fan", az=160, tip=(-0.908, 0.331, 1.02), W=0.594, pitch=50, roll=24, tone=(0.25, 1.0, 1.75)),
    "F2": dict(tier="fan", az=128, tip=(-0.438, 0.561, 1.25), W=0.594, pitch=64, roll=20, tone=(0.25, 1.0, 1.75)),
    "F3": dict(tier="fan", az=92, tip=(-0.025, 0.704, 1.04), W=0.504, pitch=64, roll=28, tone=(0.5, 0.75, 1.25)),
    "F4": dict(tier="fan", az=52, tip=(0.511, 0.654, 1.27), W=0.63, pitch=60, roll=22, tone=(0.75, 1.0, 1.75)),
    "F5": dict(tier="fan", az=22, tip=(0.937, 0.379, 1.02), W=0.594, pitch=50, roll=-20, tone=(1.0, 1.5, 2.0)),
    # spreading leaves on petiole stubs (the exploded's "Leaf (Reusable)")
    # (fix round 1: the raised pair S1 / S3 twist along their length, the base half turned to the front and the outer
    # half to the rear, so neither the front nor the rear sees a narrow underside spike)
    "S1": dict(tier="spread", az=178, tip=(-1.57, 0.06, 0.70), W=0.78, ctrl=(-0.90, 0.03, 0.80), roll=-30,
               roll_tip=30, tone=(0.25, 0.75, 1.25)),
    "S2": dict(tier="spread", az=206, tip=(-1.36, -0.52, 0.17), W=0.70, ctrl=(-0.84, -0.34, 0.50), roll=24,
               tone=(0.25, 1.0, 1.0)),
    "S3": dict(tier="spread", az=4, tip=(1.59, 0.10, 0.64), W=0.78, ctrl=(0.92, 0.07, 0.76), roll=30,
               roll_tip=-30, tone=(1.0, 1.75, 2.0)),
    "S4": dict(tier="spread", az=334, tip=(1.40, -0.60, 0.17), W=0.70, ctrl=(0.86, -0.36, 0.50), roll=0,
               tone=(0.25, 1.0, 1.25)),
    # big drooping lime leaves, front and back: rise off the hub, then lay their tips on the ground
    "N1": dict(tier="droop", az=250, tip=(-0.40, -1.06, 0.02), W=0.82, roll=14, tone=(1.25, 2.0, 2.0),
               spine=((-0.10, -0.30, 0.46), (-0.24, -0.66, 0.36))),
    "N2": dict(tier="droop", az=282, tip=(0.364, -1.098, 0.02), W=0.86, roll=-12, tone=(1.25, 2.0, 2.0),
               spine=((0.058, -0.315, 0.62), (0.203, -0.686, 0.44))),   # fix round 1: 4 deg off the bloom stem
    # (fix round 1: the back pair rise lower, under the fan, N3 turned to az 68 between F3 and F4)
    "N3": dict(tier="droop", az=68, tip=(0.40, 1.08, 0.02), W=0.82, roll=-28, tone=(1.25, 2.0, 2.0),
               spine=((0.155, 0.382, 0.36), (0.281, 0.708, 0.276))),
    "N4": dict(tier="droop", az=124, tip=(-0.55, 0.92, 0.02), W=0.72, roll=4, tone=(1.0, 1.75, 2.0),
               spine=((-0.16, 0.27, 0.30), (-0.34, 0.57, 0.236))),
    # rim: short chunky kites lying low round the hub, their bases on the ground against the hub (r RIM_R)
    # (the rolls tip their faces toward az 136 / 226 / 62 / 298: four different planes)
    "B1": dict(tier="rim", az=226, tip=(-0.80, -0.64, 0.06), W=0.50, roll=24, arch=0.34, tone=(0.0, 0.25)),
    "B2": dict(tier="rim", az=308, tip=(0.68, -0.80, 0.06), W=0.46, roll=32, arch=0.28, tone=(1.0, 1.75)),
    "B3": dict(tier="rim", az=152, tip=(-0.96, 0.50, 0.06), W=0.48, roll=22, arch=0.30, tone=(0.0, 0.25)),
    "B4": dict(tier="rim", az=28, tip=(0.86, 0.54, 0.06), W=0.48, roll=22, arch=0.36, tone=(0.0, 0.75)),
}
RIM_R = 0.30                                 # rim leaf bases this far from the hub axis (their inner edge in the hub)
FAN = ("F1", "F2", "F3", "F4", "F5")
RIM = ("B1", "B2", "B3", "B4")
CLUSTERS = {"fan": FAN, "spread": ("S1", "S2", "S3", "S4"), "droop": ("N1", "N2", "N3", "N4"), "rim": RIM}
RIM_ARCH = 0.34                              # rim leaves arch up (top z ~0.2) and lay their tips back on the ground
LEAF_INFO = {}


def _leaf_spine(name):
    """Station points with tangents, the tip, the half-width fractions and a fine polyline of a leaf."""
    s = LEAVES[name]
    az = math.radians(s["az"])
    tip = Vector(s["tip"])
    tier = s["tier"]
    if tier == "droop":
        base = Vector((math.cos(az) * BASE_R, math.sin(az) * BASE_R, RING_Z))
        P = [base] + [Vector(q) for q in s["spine"]]
        Q = P + [tip]
        T = [(Q[1] - Q[0]).normalized()] + [((Q[i] - Q[i - 1]).normalized() + (Q[i + 1] - Q[i]).normalized())
                                           .normalized() for i in range(1, len(P))]
        return list(zip(P, T)), tip, [f * s["W"] for f in SPINE_HW], Q
    if tier == "rim":
        base = Vector((math.cos(az) * RIM_R, math.sin(az) * RIM_R, s.get("bz", -SINK + EDGE["rim"] + KEEL)))
        ctrl = (base + tip) / 2 + Vector((0, 0, s.get("arch", RIM_ARCH)))
        pts = [(_bez(base, ctrl, tip, t), _bezd(base, ctrl, tip, t).normalized()) for t in RIM_ST]
        return pts, tip, [f * s["W"] for f in RIM_HW], [_bez(base, ctrl, tip, i / 20) for i in range(21)]
    z0 = FAN_Z if tier == "fan" else RING_Z + 0.04
    br = s.get("br", FAN_BR if tier == "fan" else BASE_R)
    base = Vector((math.cos(az) * br, math.sin(az) * br, z0))
    if tier == "spread":
        d = Vector((math.cos(az), math.sin(az), 0.18)).normalized()
        b1 = base + d * PET_LEN                         # petiole end: the blade starts here
        ctrl = Vector(s["ctrl"])
        pts = [(base, d)]
        hws = [PET_HWABS]
        for t, f in zip(PET_ST, PET_HW):
            pts.append((_bez(b1, ctrl, tip, t), _bezd(b1, ctrl, tip, t).normalized()))
            hws.append(max(PET_HWABS, f * s["W"]))
        poly = [base] + [_bez(b1, ctrl, tip, i / 20) for i in range(21)]
        return pts, tip, hws, poly
    ctrl = Vector(s["ctrl"]) if "ctrl" in s else base + _dir(s["az"], s["pitch"]) * ((tip - base).length * 0.5)
    pts = [(_bez(base, ctrl, tip, t), _bezd(base, ctrl, tip, t).normalized()) for t in LEAF_ST]
    return pts, tip, [f * s["W"] for f in LEAF_HW], [_bez(base, ctrl, tip, i / 20) for i in range(21)]


def leaf(a, name):
    """One leaf: 6-vert sections (left edge top, ridge, right edge top, right edge bottom, keel, left edge bottom)
    along the arched spine, the face turned up and radially outward along its azimuth (growth, never a camera) with
    a fixed growth roll, a base cap and a tip point. Fan / drooping 34 tris, spreading (petiole) 58, rim 22. Each
    station band takes one tone by role and position along the leaf."""
    s = LEAVES[name]
    tier = s["tier"]
    az = math.radians(s["az"])
    w0 = Vector((-math.sin(az), math.cos(az), 0.0))
    out = Vector((math.cos(az), math.sin(az), 0))
    sh = _shift(out * (0.60 if tier == "spread" else 0.36 if tier in ("droop", "rim") else 0.0))
    E, RD = EDGE[tier], math.radians(RIDGE[tier])

    def sections():
        st, tp, hw_, pl = _leaf_spine(name)
        rr = []
        for i, ((p, T), hw) in enumerate(zip(st, hw_)):
            w = (w0 - T * T.dot(w0)).normalized()
            n = T.cross(w).normalized()
            # a fixed growth twist about the leaf's own axis (never per camera); with "roll_tip" the twist runs from
            # `roll` at the base to `roll_tip` at the last station (a leaf twisting along its length)
            rl = s.get("roll", 0.0)
            if "roll_tip" in s:
                rl += (s["roll_tip"] - rl) * i / max(1, len(st) - 1)
            if rl:
                q = Matrix.Rotation(math.radians(rl), 3, T)
                w, n = q @ w, q @ n
            e = min(E, 0.45 * hw)
            rf = e + hw * math.tan(RD)
            rk = e + KEEL
            rr.append([p - w * hw + n * e, p + n * rf, p + w * hw + n * e, p + w * hw - n * e, p - n * rk,
                       p - w * hw - n * e])
        return st, tp, hw_, pl, rr
    stations, tip, hws, poly, pts_r = sections()
    if tier == "rim":                       # the base section rests on the ground: its lowest point at z -SINK + 0.004
        for _ in range(3):
            dz = (-SINK + 0.004) - min(q_.z for q_ in pts_r[0])
            if abs(dz) < 1e-4:
                break
            s["bz"] = s.get("bz", -SINK + EDGE["rim"] + KEEL) + dz
            stations, tip, hws, poly, pts_r = sections()
    bm = a.bm
    rings = [[bm.verts.new(q_ + sh) for q_ in pts] for pts in pts_r]
    apex = bm.verts.new(tip + sh)
    bands = [_band(bm, rings[k], rings[k + 1]) for k in range(len(rings) - 1)]
    tipf = [bm.faces.new((rings[-1][i], rings[-1][(i + 1) % 6], apex)) for i in range(6)]
    cap = bm.faces.new(list(reversed(rings[0])))
    vs = [v for r in rings for v in r] + [apex]
    rng = _rng(name)
    _close(a, vs, [f for b in bands for f in b] + tipf + [cap], MID, tint=1.0 + rng.uniform(-0.035, 0.035))
    tones = s["tone"]
    if tier == "rim":                       # base band, tip fan
        groups = [bands[0] + [cap], tipf]
    elif tier == "spread":                  # petiole, blade body, outer band + tip
        groups = [bands[0] + [cap], bands[1], bands[2] + tipf]
    else:
        groups = [bands[0] + [cap], bands[1], tipf]
    for fs, tv in zip(groups, tones):
        _paint(a, fs, _tone(tv))
        _tint(a, fs, 1.0 + rng.uniform(-0.025, 0.025))
    L = sum((poly[i + 1] - poly[i]).length for i in range(len(poly) - 1))
    last = (tip - stations[-1][0]).length
    top = max(v.co.z for v in vs)
    LEAF_INFO[name] = {"L": round(L, 3), "W": s["W"], "LW": round(L / s["W"], 2), "top_z": round(top, 3),
                       "tip": [round(x, 3) for x in tip], "min_z": round(min(v.co.z for v in vs), 3),
                       "tip_deg": round(math.degrees(2 * math.atan2(hws[-1], last)), 1),
                       "edge": round(2 * E, 3)}
    _reg("rim" if tier == "rim" else "leaf", name, vs)
    return vs


# ---- plates (star and bloom petals) ------------------------------------------------------------------------------------
def _plate(a, c0, r, n, L, W, st, hwf, lifts, thick, crease, roll, apex, sh):
    """A closed petal plate from c0 outward along r (in the head plane, normal n), each station lifted out of the
    plane by lifts[i] deg (a curved cup when they grow), 5-vert sections (two top edges, a raised centre crease, two
    bottom edges), an optional tip point `apex` (fraction of L past the last station) or a flat blunt end cap.
    Returns (verts, bands, base cap, end faces)."""
    w = n.cross(r).normalized()
    bm = a.bm
    rings = []
    c = c0.copy()
    us = []
    for i, (s_, f) in enumerate(zip(st, hwf)):
        lf = math.radians(lifts[i])
        u = (r * math.cos(lf) + n * math.sin(lf)).normalized()
        if i > 0:
            lm = math.radians((lifts[i] + lifts[i - 1]) / 2)
            c = c + (r * math.cos(lm) + n * math.sin(lm)).normalized() * ((s_ - st[i - 1]) * L)
        p = u.cross(w).normalized()
        q = Matrix.Rotation(math.radians(roll), 3, u)
        ww, pp = q @ w, q @ p
        hw = f * W
        t = thick / 2
        pts = [c - ww * hw + pp * t, c + pp * (t + crease), c + ww * hw + pp * t, c + ww * hw - pp * t,
               c - ww * hw - pp * t]
        rings.append([bm.verts.new(x + sh) for x in pts])
        us.append(u)
    bands = [_band(bm, rings[i], rings[i + 1]) for i in range(len(rings) - 1)]
    cap0 = bm.faces.new(list(reversed(rings[0])))
    if apex:
        tp = bm.verts.new(c + us[-1] * (apex * L) + sh)
        end = [bm.faces.new((rings[-1][i], rings[-1][(i + 1) % 5], tp)) for i in range(5)]
        vs = [v for rr in rings for v in rr] + [tp]
    else:
        end = [bm.faces.new(rings[-1])]
        vs = [v for rr in rings for v in rr]
    return vs, bands, cap0, end


def bead(a, name, C, n, e1, e2, R, key, sh):
    """A squat octagonal gem: a bottom point (sunk among the petal bases), an 8-sided equator, an 8-sided top ring
    turned half a step (antiprism facets) and a flat octagonal top. 30 tris. One key (a band on a gem follows its
    facing whatever drives it: 061 deviation 1)."""
    bm = a.bm
    eq = [bm.verts.new(x + sh) for x in _ring(C + n * 0.03, e1, e2, R, 8, math.radians(7))]
    top = [bm.verts.new(x + sh) for x in _ring(C + n * 0.095, e1, e2, R * 0.66, 8, math.radians(7 + 22.5))]
    bot = bm.verts.new(C - n * 0.06 + sh)
    lower = [bm.faces.new((eq[(i + 1) % 8], eq[i], bot)) for i in range(8)]
    up = []
    for i in range(8):
        up.append(bm.faces.new((eq[i], eq[(i + 1) % 8], top[i])))
        up.append(bm.faces.new((top[i], eq[(i + 1) % 8], top[(i + 1) % 8])))
    cap = bm.faces.new(top)
    vs = eq + top + [bot]
    _close(a, vs, lower + up + [cap], key, tint=1.0 + _rng(name).uniform(-0.02, 0.02))
    _reg("bead", name, vs)
    return vs


def calyx(a, name, C, n, e1, e2, rings_hr, sides, sepal, sh, key_body=None, key_rim=None):
    """A flared green cup on the head axis: `rings_hr` [(height along n, radius)] bottom -> top, `sides`-sided
    (turned half a step per ring for facets), closed by a flat bottom; with `sepal` = (radius, rise) the top ring has
    pointed sepal tips between its verts (2 x sides verts) and a fan cap to a centre vert. Body leaf_dark, the top ring
    of faces half stem (by position)."""
    bm = a.bm
    rings = []
    for i, (h, r) in enumerate(rings_hr):
        rings.append([bm.verts.new(x + sh) for x in _ring(C + n * h, e1, e2, r, sides, math.pi / sides * (i % 2))])
    fs = []
    for i in range(len(rings) - 1):
        fs += _band(bm, rings[i], rings[i + 1])
    rim_fs = list(fs[-sides:])
    vs = [v for rr in rings for v in rr]
    bot = bm.faces.new(list(reversed(rings[0])))
    fs.append(bot)
    if sepal:
        h_top, r_top = rings_hr[-1]
        rot = math.pi / sides * ((len(rings) - 1) % 2)
        tips = [bm.verts.new(x + sh) for x in _ring(C + n * (h_top + sepal[1]), e1, e2, sepal[0], sides,
                                                     rot + math.pi / sides)]
        cen = bm.verts.new(C + n * (h_top - 0.01) + sh)
        top = rings[-1]
        sep = []
        for i in range(sides):
            j = (i + 1) % sides
            sep.append(bm.faces.new((top[i], top[j], tips[i])))
            sep.append(bm.faces.new((top[i], tips[i], cen)))
            sep.append(bm.faces.new((tips[i], top[j], cen)))
        fs += sep
        rim_fs += sep
        vs += tips + [cen]
    else:
        fs.append(bm.faces.new(rings[-1]))
        rim_fs.append(fs[-1])
    _close(a, vs, fs, key_body or DARK, tint=1.0 + _rng(name).uniform(-0.02, 0.02))
    _paint(a, rim_fs, key_rim or _mix(DARK, STEM, 0.5))
    _reg("calyx", name, vs)
    return vs


# ---- heads (spec 2.3) -------------------------------------------------------------------------------------------------
# name -> petal-plane centre, normal (az, tilt from vertical), petal phase (deg from e1), stem foot on the hub top and
# the stem's via points
HEADS = {
    "star": dict(c=(0.40, 0.30, 1.96), az=300, tilt=45, phase=96, foot=(0.07, 0.07), via=[]),
    # the bloom faces front-right (az 295, not the study's 255): on the sheet's front its calyx and stem meet the cup at
    # its lower LEFT and its bead sits left of the rim centre, which only a cup facing out to the right gives
    "bloom": dict(c=(1.06, -0.48, 1.36), az=295, tilt=44, phase=92, foot=(0.07, -0.07), via=[(0.50, -0.15, 0.62)]),
}
# star (spec 1.4): 5 pointed lozenges L 0.50, W 0.32 from r 0.07, a near-flat ring; calyx a 5-sided cone; bead Ø 0.26
STAR_R0, STAR_L, STAR_W, STAR_T = 0.07, 0.48, 0.32, 0.055
STAR_ST, STAR_HW, STAR_APEX = (0.0, 0.56, 0.86), (0.17, 0.50, 0.20), 0.14
STAR_LIFT = ((8, 9, 6), (10, 11, 8), (7, 8, 5), (11, 10, 7), (9, 10, 6))
STAR_ROLL = (5.0, -6.0, 4.0, -5.0, 6.0)
STAR_CALYX = ((-0.24, 0.085), (-0.13, 0.115), (-0.03, 0.15))
STAR_BEAD_R = 0.13
# bloom (spec 1.4): 5 outer petals L 0.44, W 0.36, cupped up; 5 inner L 0.30, W 0.28, steeper; bead Ø 0.20
BL_R0 = 0.06
# blunt rounded ends: a wide last station and a short apex (an obtuse point, never a square end or a needle)
BL_OUT = dict(L=0.46, W=0.44, st=(0.0, 0.50, 0.84), hw=(0.20, 0.50, 0.42), lift=(24, 40, 52), T=0.05, apex=0.16)
BL_IN = dict(L=0.26, W=0.30, st=(0.0, 0.74), hw=(0.24, 0.50), lift=(42, 60), T=0.05, apex=0.26)
BL_CALYX = ((-0.24, 0.085), (-0.13, 0.13), (-0.04, 0.16))
BL_SEPAL = (0.24, 0.07)
BLOOM_BEAD_R = 0.10
STEM_IN = 0.065                             # a stem's top end this far inside its calyx / cap
CROOK = 0.10                                # a short straight run on the calyx axis under the calyx
STEM_SIDE = (0.135, 0.12)                   # square stem side at the foot and the top (spec 2.3)
STEM_FOOT_Z = HUB_TOP - 0.07
STEM_TWIST = 20.0                           # stem faces turned this far off the front (spec 3.5)
HEAD_INFO = {}


def _hframe(name, flat=None):
    s = HEADS[name]
    if flat is not None:                    # part shots: the head at the origin facing (az, tilt) = flat
        a_, t_ = math.radians(flat[0]), math.radians(flat[1])
        C = Vector()
    else:
        a_, t_ = math.radians(s["az"]), math.radians(s["tilt"])
        C = Vector(s["c"])
    n = Vector((math.cos(a_) * math.sin(t_), math.sin(a_) * math.sin(t_), math.cos(t_)))
    e1, e2 = _perp(n)
    return C, e1, e2, n


def star_head(a, flat=None, sh=None):
    C, e1, e2, n = _hframe("star", flat)
    sh = sh if sh is not None else _shift(n * 0.50 + Vector((0, 0, 0.75)))
    calyx(a, "star_calyx", C, n, e1, e2, STAR_CALYX, 5, None, sh + _shift(-n * 0.12))
    bead(a, "star_bead", C + n * 0.02, n, e1, e2, STAR_BEAD_R, STAR_BEAD, sh + _shift(n * 0.18))
    tips = []
    for k in range(5):
        ang = math.radians(HEADS["star"]["phase"] + 72 * k)
        r = e1 * math.cos(ang) + e2 * math.sin(ang)
        vs, bands, cap0, end = _plate(a, C + r * STAR_R0 + n * (0.005 * (k % 2)), r, n, STAR_L, STAR_W, STAR_ST,
                                      STAR_HW, STAR_LIFT[k], STAR_T, 0.016, STAR_ROLL[k], STAR_APEX,
                                      sh + _shift(r * 0.12))
        rng = _rng("star", k)
        _close(a, vs, bands[0] + bands[1] + [cap0] + end, STAR, tint=1.0 + rng.uniform(-0.025, 0.025))
        _paint(a, bands[0] + [cap0], _mix(STAR_DEEP, STAR, 0.5))
        _reg("petal", f"star_p{k}", vs)
        tips.append(max(v.co.z for v in vs))
    if flat is None:
        HEAD_INFO["star"] = {"centre": [round(x, 3) for x in C], "normal": [round(x, 3) for x in n],
                             "top_z": round(max(tips), 3), "low_tip_z": round(min(tips), 3)}


def bloom_head(a, flat=None, sh=None):
    C, e1, e2, n = _hframe("bloom", flat)
    sh = sh if sh is not None else _shift(n * 0.50 + Vector((0, 0, 0.75)))
    calyx(a, "bloom_calyx", C, n, e1, e2, BL_CALYX, 5, BL_SEPAL, sh + _shift(-n * 0.14))
    bead(a, "bloom_bead", C - n * 0.01, n, e1, e2, BLOOM_BEAD_R, BLOOM_BEAD, sh + _shift(n * 0.30))
    zs = []
    for ring, spec, ph, kind in (("o", BL_OUT, 0.0, PINK), ("i", BL_IN, 36.0, PINK_DEEP)):
        for k in range(5):
            ang = math.radians(HEADS["bloom"]["phase"] + ph + 72 * k)
            r = e1 * math.cos(ang) + e2 * math.sin(ang)
            lift = tuple(x + (2.5 if k % 2 else -2.5) for x in spec["lift"])
            vs, bands, cap0, end = _plate(a, C + r * BL_R0 - n * (0.03 if ring == "o" else 0.0), r, n, spec["L"],
                                          spec["W"], spec["st"], spec["hw"], lift, spec["T"], 0.014,
                                          (4.0 if k % 2 else -4.0), spec["apex"],
                                          sh + _shift(r * (0.16 if ring == "o" else 0.06)))
            rng = _rng("bloom" + ring, k)
            rest = [f for b in bands[1:] for f in b] + end
            _close(a, vs, bands[0] + [cap0] + rest, PINK, tint=1.0 + rng.uniform(-0.025, 0.025))
            if ring == "o":                 # outer petals: a deep-rose inner band, pink body (position along it)
                _paint(a, bands[0] + [cap0], _mix(PINK_DEEP, PINK, 0.75))
                _paint(a, rest, PINK)
            else:                           # inner petals: deep throat at the base -> pink at the tips
                _paint(a, bands[0] + [cap0], _mix(PINK_DEEP, PINK, 0.25))
                _paint(a, end, PINK)
            _reg("petal", f"bloom_{ring}{k}", vs)
            zs += [v.co.z for v in vs]
    if flat is None:
        HEAD_INFO["bloom"] = {"centre": [round(x, 3) for x in C], "normal": [round(x, 3) for x in n],
                              "z_range": [round(min(zs), 3), round(max(zs), 3)]}


# bell (spec 1.4): a lathed 6-sided closed shell hanging from a 6-sided cap, six pointed flared lobes, an inner wall
BELL_SEAT = (-0.86, -0.28, 1.93)            # the bell's dome seat (top), in the cap
BELL_TILT, BELL_TILT_AZ = 15.0, 222.0       # the bell's axis: down, tilted toward the front-left
BELL_L = 0.76
# outer (fraction of L, radius): seat, dome shoulder, flank, mouth (the lobes' notches and tips follow). The sheet's
# bell is about as wide as long (front 62 x 60 px, parts row 76 x 73): a round dome, full flanks, a flared mouth.
# Fix round 1: the mouth was a flat flared brim (lobe tips 0.021 below the notches). Now a rounded dome (Ø 0.41 across
# the flats at 0.15 L), convex flanks to the lobe bases at 0.645 L, and six pointed petal lobes from notches at 0.68 L
# (r 0.30, mid-panel) to tips at 1.0 L (r 0.46 on the ribs): each lobe about 0.33 L long, pointing down and out about
# 25 deg off the axis, curled up only 0.02.
BELL_OUT = ((0.0, 0.09), (0.05, 0.178), (0.15, 0.238), (0.34, 0.296), (0.50, 0.323), (0.645, 0.335))
BELL_NOTCH = (0.68, 0.30)                   # between the lobes (mid-panel, just outside the flat, just below the
                                            # last ring so the rim never cuts back through the flank): the notches
BELL_TIP = (1.0, 0.46, 0.02)                # lobe tips on the ribs: L fraction, radius, curl up (studs)
BELL_WALL = 0.05
BELL_TIP_IN = (0.965, 0.06)                 # the inner tip: L fraction, inset (the lobe's thickness at its point)
BELL_NOTCH_IN = (0.66, 0.065)               # the inner notch: L fraction, inset
# each lobe's two shoulders (L fraction, radius, deg off its rib): the lobe edges bulge out into a broad rounded-pointed
# petal (the sheet's f34 and parts row), leaving a narrow V notch between neighbours, never a spike
BELL_SHOULDER = (0.85, 0.415, 19.0)
BELL_SHOULDER_IN = (0.83, 0.06)
BELL_IN = ((0.52, 0.235), (0.26, 0.0))      # inner flank ring (on the ribs), the inner dome apex: the inner wall
                                            # follows the outer about 0.05-0.07 inside
CAP = ((-0.03, 0.165), (0.10, 0.075))       # cap rings: (height above the seat along -axis, radius): a flared collar
BELL_PHASE = 15.0


def _bell_frame(flat=False):
    if flat:
        ax = Vector((0, 0, -1))
        seat = Vector()
    else:
        t, az = math.radians(BELL_TILT), math.radians(BELL_TILT_AZ)
        ax = Vector((math.cos(az) * math.sin(t), math.sin(az) * math.sin(t), -math.cos(t)))
        seat = Vector(BELL_SEAT)
    e1, e2 = _perp(ax)
    return seat, ax, e1, e2


def bell(a, flat=False, sh=None):
    """The bell: outer rings seat -> dome shoulder -> flank -> mouth, a 24-vert hem (six pointed lobe tips on the
    ribs pointing down and out, two bulging shoulders per lobe, six notches between them), a rim band, an inner hem
    0.06 inside, an inner flank ring and an inner dome apex: one closed shell with a real inside. 178 tris. Outer
    shell `bell`, its dome band a step lighter toward the swatch by height in the bell's frame; the inner wall and
    the rim `bell_deep` (a region: the sheet's deep violet under the lobes and in the mouth)."""
    seat, ax, e1, e2 = _bell_frame(flat)
    sh = sh if sh is not None else _shift(Vector((-0.30, -0.20, 0.90)))
    bm = a.bm
    ph = math.radians(BELL_PHASE)
    L = BELL_L

    def at(fr, r, ang, lift=0.0):
        return seat + ax * (fr * L - lift) + (e1 * math.cos(ang) + e2 * math.sin(ang)) * r

    outer = [[bm.verts.new(at(fr, r, ph + k * math.pi / 3) + sh) for k in range(6)] for fr, r in BELL_OUT]
    zig_o, zig_i = [], []
    sa = math.radians(BELL_SHOULDER[2])
    for k in range(6):                      # per lobe step: tip, right shoulder, notch, next lobe's left shoulder
        a0 = ph + k * math.pi / 3
        zig_o.append(bm.verts.new(at(BELL_TIP[0], BELL_TIP[1], a0, BELL_TIP[2]) + sh))
        zig_o.append(bm.verts.new(at(BELL_SHOULDER[0], BELL_SHOULDER[1], a0 + sa) + sh))
        zig_o.append(bm.verts.new(at(BELL_NOTCH[0], BELL_NOTCH[1], a0 + math.pi / 6) + sh))
        zig_o.append(bm.verts.new(at(BELL_SHOULDER[0], BELL_SHOULDER[1], a0 + math.pi / 3 - sa) + sh))
        zig_i.append(bm.verts.new(at(BELL_TIP_IN[0], BELL_TIP[1] - BELL_TIP_IN[1], a0, BELL_TIP[2]) + sh))
        zig_i.append(bm.verts.new(at(BELL_SHOULDER_IN[0], BELL_SHOULDER[1] - BELL_SHOULDER_IN[1], a0 + sa) + sh))
        zig_i.append(bm.verts.new(at(BELL_NOTCH_IN[0], BELL_NOTCH[1] - BELL_NOTCH_IN[1], a0 + math.pi / 6) + sh))
        zig_i.append(bm.verts.new(at(BELL_SHOULDER_IN[0], BELL_SHOULDER[1] - BELL_SHOULDER_IN[1],
                                     a0 + math.pi / 3 - sa) + sh))
    inner = [bm.verts.new(at(BELL_IN[0][0], BELL_IN[0][1], ph + k * math.pi / 3) + sh) for k in range(6)]
    apex = bm.verts.new(seat + ax * (BELL_IN[1][0] * L) + sh)
    seat_cap = bm.faces.new(list(reversed(outer[0])))
    dome = _band(bm, outer[0], outer[1]) + _band(bm, outer[1], outer[2])
    flank = []
    for i in range(2, len(outer) - 1):
        flank += _band(bm, outer[i], outer[i + 1])
    mouth = []
    m = outer[-1]
    for k in range(6):                      # each panel: half of lobe k, the notch, half of lobe k + 1
        j = (k + 1) % 6
        t0, s0, nt, s1, t1 = [zig_o[(4 * k + i) % 24] for i in range(5)]
        mouth += [bm.faces.new((m[k], t0, s0)), bm.faces.new((m[k], s0, nt)), bm.faces.new((m[k], nt, m[j])),
                  bm.faces.new((m[j], nt, s1)), bm.faces.new((m[j], s1, t1))]
    rim = _band(bm, zig_o, zig_i)
    inside = []
    for k in range(6):
        j = (k + 1) % 6
        t0, s0, nt, s1, t1 = [zig_i[(4 * k + i) % 24] for i in range(5)]
        inside += [bm.faces.new((inner[k], s0, t0)), bm.faces.new((inner[k], nt, s0)),
                   bm.faces.new((inner[k], inner[j], nt)), bm.faces.new((inner[j], s1, nt)),
                   bm.faces.new((inner[j], t1, s1))]
    inside += [bm.faces.new((inner[(k + 1) % 6], inner[k], apex)) for k in range(6)]
    vs = [v for r in outer for v in r] + zig_o + zig_i + inner + [apex]
    _close(a, vs, [seat_cap] + dome + flank + mouth + rim + inside, BELL, tint=1.0 + _rng("bell").uniform(-0.02, 0.02))
    _paint(a, dome + [seat_cap], _mix(BELL, BELL_DEEP, 0.0))
    _paint(a, rim + inside, BELL_DEEP)
    for k in range(6):                      # broad tint per lobe panel (never per triangle)
        _tint(a, mouth[5 * k:5 * k + 5] + flank[k::6], 1.0 + _rng("bell", k).uniform(-0.03, 0.03))
    _reg("bell", "bell", vs)
    return vs


def bell_cap(a, flat=False, sh=None):
    """The bell's 6-sided green cap on the bell's axis (spec 1.4: Ø 0.18-0.23 x 0.14), stem colour, the top ring
    half mid (by position). 20 tris."""
    seat, ax, e1, e2 = _bell_frame(flat)
    sh = sh if sh is not None else _shift(Vector((-0.30, -0.20, 1.10)))
    bm = a.bm
    rings = [[bm.verts.new(x + sh) for x in _ring(seat - ax * h, e1, e2, r, 6, math.radians(BELL_PHASE + 30 * i))]
             for i, (h, r) in enumerate(CAP)]
    bands = [_band(bm, rings[i], rings[i + 1]) for i in range(len(rings) - 1)]
    bot = bm.faces.new(list(reversed(rings[0])))
    top = bm.faces.new(rings[-1])
    vs = [v for r in rings for v in r]
    _close(a, vs, bands[0] + [bot, top], STEM, tint=1.0 + _rng("cap").uniform(-0.02, 0.02))
    _paint(a, [bot], _mix(STEM, MID, 0.5))
    _reg("cap", "bell_cap", vs)
    return vs


# ---- stems (spec 2.3, 3.5: square prisms, straight segments, crisp mitred bends) ----------------------------------------
def _crook_path():
    seat, ax, e1, e2 = _bell_frame()
    ctop = seat - ax * CAP[-1][0]           # the cap's top centre
    end = ctop + ax * STEM_IN               # the hook's end, inside the cap
    # the sheet's front: x -0.36 at z 0.82, -0.57 at z 1.85, the apex (-0.65, 2.12), a short descending hook to the cap
    return [Vector((-0.08, 0.02, STEM_FOOT_Z)), Vector((-0.34, -0.05, 0.82)), Vector((-0.56, -0.10, 1.88)),
            Vector((-0.65, -0.15, 2.12)), Vector((-0.78, -0.23, 2.10)), end]


def _stem_path(name):
    if name == "bell":
        return _crook_path()
    s = HEADS[name]
    C, e1, e2, n = _hframe(name)
    cb = C + n * (STAR_CALYX if name == "star" else BL_CALYX)[0][0]
    foot = Vector((s["foot"][0], s["foot"][1], STEM_FOOT_Z))
    return [foot] + [Vector(v) for v in s["via"]] + [cb - n * CROOK, cb + n * STEM_IN]   # straight runs, one crisp bend


def square_tube(a, pts, sides, key, name, twist=STEM_TWIST, sh=Vector(), slant=None):
    """A square prism along a polyline: parallel-transported frames, the faces turned `twist` deg off the front, each
    interior ring on the bisector plane of its bend (an exact mitre: stretched only across the bend), flat end caps.
    8 tris per segment + 4. `slant` tilts the top cap (part shot)."""
    n = len(pts)
    ds = [(pts[i + 1] - pts[i]).normalized() for i in range(n - 1)]
    ts = [ds[0]] + [(ds[i - 1] + ds[i]).normalized() for i in range(1, n - 1)] + [ds[-1]]
    tw = math.radians(twist)
    u = Vector((math.sin(tw), -math.cos(tw), 0.0))
    bm = a.bm
    rings = []
    for i, (p, t) in enumerate(zip(pts, ts)):
        u = u - t * u.dot(t)
        u = u.normalized() if u.length > 1e-6 else _perp(t)[0]
        v = t.cross(u)
        hs = sides[0] + (sides[1] - sides[0]) * i / (n - 1)
        offs = [(u * cx + v * cy) * (hs / 2) for cx, cy in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
        if 0 < i < n - 1:
            th = ds[i - 1].angle(ds[i])
            b = ds[i] - ds[i - 1]
            b = b - t * b.dot(t)
            if b.length > 1e-6 and th > 1e-4:
                b.normalize()
                k = 1.0 / max(0.4, math.cos(th / 2)) - 1.0
                offs = [o + b * (o.dot(b) * k) for o in offs]
        if slant and i == n - 1:
            offs = [o + t * (o.dot(u) * slant) for o in offs]
        rings.append([bm.verts.new(p + o + sh) for o in offs])
    bands = [_band(bm, rings[i], rings[i + 1]) for i in range(n - 1)]
    c0 = bm.faces.new(list(reversed(rings[0])))
    c1 = bm.faces.new(rings[-1])
    vs = [v for rr in rings for v in rr]
    _close(a, vs, [f for b in bands for f in b] + [c0, c1], key, tint=1.0 + _rng(name).uniform(-0.02, 0.02))
    return vs, bands, c0, c1


def stem(a, name):
    pts = _stem_path(name)
    f = (0.42 - pts[0].z) / (pts[1].z - pts[0].z)          # a ring where the stem leaves the rosette's base (z 0.42):
    pts.insert(1, pts[0].lerp(pts[1], max(0.1, min(0.6, f))))   # only the foot below it takes the deeper green
    sh = _shift((0, 0, 0.45))
    vs, bands, c0, c1 = square_tube(a, pts, STEM_SIDE, STEM, name + "_stem", sh=sh)
    _paint(a, bands[0] + [c0], _mix(STEM, DARK, 0.5))    # the foot a step deeper where it enters the leaves
    _reg("stem", f"{name}_stem", vs)
    return vs


# ---- stones (spec 2.5: squat faceted nuggets, flat base) ---------------------------------------------------------------
# name -> centre (x, y), W, D, H, yaw (deg), sides, key
# (fix round 1: 0.82 of the round-1 sizes, a 0.3 slide at most: the sheet's stones peep out at the foot, about
# 2.5 % of the front, 4 % of the rear, none from the side)
ROCKS = {
    "R1": dict(c=(-1.02, -0.60), W=0.377, D=0.312, H=0.197, yaw=20, n=6, key=ROCK_G),
    "R2": dict(c=(1.02, -0.52), W=0.279, D=0.23, H=0.164, yaw=-30, n=5, key=ROCK_B),
    "R3": dict(c=(0.66, 0.64), W=0.262, D=0.213, H=0.148, yaw=45, n=5, key=ROCK_B),
    "R4": dict(c=(-0.74, 0.64), W=0.328, D=0.262, H=0.18, yaw=-15, n=6, key=ROCK_G),
    "R5": dict(c=(-1.12, 0.34), W=0.197, D=0.164, H=0.107, yaw=70, n=5, key=ROCK_B),
}
ROCK_INFO = {}
SLIDE_N = 20                                 # slide steps of 0.015 toward the hub at most
ROCK_FIT = {}                              # name -> (cx, cy, height factor) from the last hero build


def rock(a, name, fit=None):
    """A faceted nugget: an n-sided base ring (r +-10 %, sunk SINK), the widest ring at 0.40 H, and a sloping top ring
    pulled in to 0.64 and turned half a step (the shoulder facets run from the widest ring up to it), closed by the
    flat top. 4n + 2(n-2) tris (32 for n 6, 26 for n 5). With `fit` (a BVH of the leaves and the hub): the stone first
    slides toward the hub axis until it is within 0.02 of a leaf or the hub (spec 6: every stone touches a leaf or the
    hub), then its top is lowered or raised so the leaf above just touches it (no leaf more than 0.05 inside). The
    lowest band a step deeper (contact), broad tint per stone."""
    s = ROCKS[name]
    rng = _rng(name)
    n = s["n"]
    yaw = math.radians(s["yaw"])
    cx0, cy0 = s["c"]
    H = s["H"]
    sh = _shift(Vector((cx0, cy0, 0)).normalized() * 0.45 if (cx0 or cy0) else Vector())
    jit = [1.0 + rng.uniform(-0.10, 0.10) for _ in range(n)]

    def make(cx, cy):
        def ring(rf, z, rot):
            return [Vector((cx + math.cos(yaw + rot + 2 * math.pi * k / n) * s["W"] / 2 * rf * jit[k],
                            cy + math.sin(yaw + rot + 2 * math.pi * k / n) * s["D"] / 2 * rf * jit[k], z))
                    for k in range(n)]
        rows = [ring(0.86, -SINK, 0.0), ring(1.0, 0.40 * H, 0.0)]
        tilt = Vector((math.cos(yaw + 0.7), math.sin(yaw + 0.7), 0))
        top = ring(0.64, H, math.pi / n)
        for p in top:                       # a sloping top
            p.z += (p - Vector((cx, cy, H))).dot(tilt) * 0.24
        rows.append(top)
        return rows
    cx, cy = cx0, cy0
    rows = make(cx, cy)
    if fit is None and EXPLODE["on"] and name in ROCK_FIT:     # the exploded view: the hero's fitted stone
        cx, cy, f = ROCK_FIT[name]
        rows = make(cx, cy)
        for r in rows[1:]:
            for p in r:
                p.z *= f
    if fit is not None:
        u = Vector((cx, cy, 0)).normalized()
        slid = 0.0
        for _ in range(SLIDE_N):
            d = min(fit.find_nearest(p)[3] for r in rows for p in r)
            if d <= 0.02:
                break
            slid += 0.015
            cx, cy = cx0 - u.x * slid, cy0 - u.y * slid
            rows = make(cx, cy)
        touch = min(fit.find_nearest(p)[3] for r in rows for p in r) <= 0.02
        ROCK_INFO[name] = {"slid": round(slid, 3), "c": [round(cx, 3), round(cy, 3)]}
        gaps, fv = [], []
        up, dn = Vector((0, 0, 1)), Vector((0, 0, -1))
        for p in rows[1] + rows[2]:
            if p.z < 0.03:
                continue
            hit = fit.ray_cast(p, up, 0.4)
            if hit[0] is None:
                continue
            if hit[1].z < 0:                # a leaf's underside above the vert: raise the vert to touch it
                g = hit[3]
            else:                           # the vert is inside a leaf: lower it to the leaf's underside
                low = fit.ray_cast(p, dn, 0.4)
                g = -(low[3] if low[0] is not None else 0.0)
            gaps.append(g)
            if g < 0.15:                    # only a leaf close above (or through) the stone shapes its top
                fv.append((p.z + g + 0.008) / p.z)
        if fv:
            g = min(gaps)
            # only ever lowered when the slide found contact; a stone that slid its full run without touching is
            # raised (at most 1.3) until the leaf above it just rests on its top
            f = max(0.6, min(1.0 if touch else 1.3, min(fv)))
            for r in rows[1:]:
                for p in r:
                    p.z *= f
            ROCK_INFO[name].update({"fit": round(f, 3), "gap0": round(g, 3)})
        ROCK_FIT[name] = (cx, cy, ROCK_INFO[name].get("fit", 1.0))
    bm = a.bm
    vr = [[bm.verts.new(p + sh) for p in r] for r in rows]
    bands = [_band(bm, vr[i], vr[i + 1]) for i in range(2)]
    bot = bm.faces.new(list(reversed(vr[0])))
    topf = bm.faces.new(vr[2])
    vs = [v for r in vr for v in r]
    _close(a, vs, [f for b in bands for f in b] + [bot, topf], s["key"], tint=1.0 + rng.uniform(-0.04, 0.04))
    _paint(a, bands[0] + [bot], _mix(s["key"], DARK if s["key"] == ROCK_G else ROCK_B, 0.0))
    for i, b in enumerate(bands):           # broad facet groups (one per band), never per triangle
        _tint(a, b, (0.88 if i == 0 else 1.0) + rng.uniform(-0.025, 0.025))
    ROCK_INFO.setdefault(name, {})["H"] = round(max(v.co.z for v in vs) - min(v.co.z for v in vs), 3)
    _reg("rock", name, vs)
    return vs


# ---- assemblies ----------------------------------------------------------------------------------------------------------
def _leaf_bvh(a, names):
    """BVH of the leaves already built (by register name) in a.bm."""
    want = {n for k, n, c in PIECES if n in names}
    if not want:
        return None
    bm = a.bm
    bm.verts.ensure_lookup_table()
    ids, ns = M._shell_ids(bm)
    groups = {}
    for f in bm.faces:
        groups.setdefault(ids[f.index], []).append(f)
    cents = {n: c for k, n, c in PIECES if n in want}
    cos, polys, idx = [], [], {}
    for sid, fs in groups.items():
        vs = list({v for f in fs for v in f.verts})
        c = sum((v.co for v in vs), Vector()) / len(vs)
        if any((c - cc).length < 1e-4 for cc in cents.values()):
            for f in fs:
                poly = []
                for v in f.verts:
                    if v not in idx:
                        idx[v] = len(cos)
                        cos.append(v.co.copy())
                    poly.append(idx[v])
                polys.append(poly)
    return BVHTree.FromPolygons(cos, polys) if polys else None


def hero_all(a):
    PIECES.clear()
    LEAF_INFO.clear()
    HEAD_INFO.clear()
    ROCK_INFO.clear()
    hub(a)
    for k in LEAVES:
        leaf(a, k)
    fit = None if EXPLODE["on"] else _leaf_bvh(a, set(LEAVES) | {"hub"})
    for k in ROCKS:
        rock(a, k, fit)
    stem(a, "star")
    star_head(a)
    stem(a, "bloom")
    bloom_head(a)
    stem(a, "bell")
    bell_cap(a)
    bell(a)


def bell_part(a):
    PIECES.clear()
    bell_cap(a, flat=True, sh=Vector())
    bell(a, flat=True, sh=Vector())


NECK = 0.22                                  # the head parts' neck stub below the calyx


BLOOM_PART_FLAT = (270, 12)                  # fix round 1: the part stands nearly upright, read from the parts row's
                                             # low camera as a deep cup (it was tilted 34 deg and read as a flat rose)


def _neck(a, name, rings_hr, flat=(270, 30)):
    C, e1, e2, n = _hframe(name, flat)
    cb = C + n * rings_hr[0][0]
    vs, bands, c0, c1 = square_tube(a, [cb - n * NECK, cb + n * STEM_IN], (0.125, 0.12), STEM, name + "_neck")
    _paint(a, [c0], _mix(STEM, DARK, 0.5))
    _reg("stem", f"{name}_stem", vs)


def star_part(a):
    PIECES.clear()
    star_head(a, flat=(270, 30), sh=Vector())
    _neck(a, "star", STAR_CALYX)


def bloom_part(a):
    PIECES.clear()
    bloom_head(a, flat=BLOOM_PART_FLAT, sh=Vector())
    _neck(a, "bloom", BL_CALYX, BLOOM_PART_FLAT)


def stem_part(a):
    """'Stem (Example)': a straight square prism 0.13 x 0.75 with a slanted top cut (the exploded 'Stem (Blue)')."""
    PIECES.clear()
    vs, bands, c0, c1 = square_tube(a, [Vector((0, 0, 0)), Vector((0, 0, 0.15)), Vector((0, 0, 0.75))],
                                    (0.13, 0.125), STEM, "stem_part", slant=0.45)
    _paint(a, bands[0] + [c0], _mix(STEM, DARK, 0.5))
    _reg("stem", "stem", vs)


def leaf_part(a):
    """'Leaf (Example)': the reusable petiole leaf as a flat kite (S1's shape with a plain roll, not the hero's
    along-the-length twist, which reads as a twisted strap on its own)."""
    PIECES.clear()
    s = LEAVES["S1"]
    keep = {k: s[k] for k in ("roll", "roll_tip") if k in s}
    s.pop("roll_tip", None)
    s["roll"] = -18
    try:
        leaf(a, "S1")
    finally:
        s.pop("roll", None)
        s.update(keep)


def rock_grey_part(a):
    PIECES.clear()
    rock(a, "R1")


def rock_brown_part(a):
    PIECES.clear()
    rock(a, "R2")


def base_part(a):
    PIECES.clear()
    hub(a)
    for k in FAN + RIM:
        leaf(a, k)


NOTES = {
    HERO: "Forest wildflowers: a purple six-lobed bell hanging from a square crook stem, a blue five-petal star with a "
          "pale-lemon bead, a pink cupped two-ring bloom with a golden bead, on thick square stems over a rosette of 17 "
          "thick faceted kite leaves round a hidden hexagonal hub, five faceted stones at the foot. Walk-through "
          "forest-floor cover (collision none). Sheet header 63/132.",
    BELL_P: "Purple Bell Head: six-sided faceted bell with six flared pointed lobes and a dark-violet inside, green cap",
    STAR_P: "Blue Star Head: five broad pointed periwinkle lozenge petals round a pale-lemon octagonal bead, green "
            "five-sided calyx and a square neck stub",
    BLOOM_P: "Pink Bloom Head: five outer and five inner cupped pink petals round a golden bead, a dark calyx with "
             "pointed sepals and a square neck stub",
    STEM_P: "Stem (Example): straight square green stem prism with a slanted top cut",
    LEAF_P: "Leaf (Reusable): broad thick faceted kite with a ridge, keel and a square petiole stub",
    ROCKG_P: "Rock (Gray): squat faceted warm-grey stone",
    ROCKB_P: "Rock (Brown): squat faceted warm-brown stone",
    BASE_P: "Leaf Cluster Base: hexagonal hub with the five-leaf upright fan and four chunky rim leaves",
}
COLLISION = {k: "none" for k in NOTES}
# the bell alone is mostly its own inside: bell_deep is the inner wall and rim (a region, the sheet's deep violet in
# the mouth), which faces inward by construction, so the facing correlation is the region, not painted light
SHADING_OK = {BELL_P: "bell_deep is the bell's inner wall and rim (the inside of the mouth: a region), not a facing"}


def _new(name, fn, role, budget, temp=False):
    old = bpy.data.objects.get(name)
    if old:
        if old.get("kit_sheet") not in (None, SHEET) and not temp:
            raise RuntimeError(f"{name} belongs to {old.get('kit_sheet')}")
        for c in list(old.children_recursive):
            bpy.data.objects.remove(c, do_unlink=True)
        me = old.data
        bpy.data.objects.remove(old, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    a = K.fk().Asset(name, f"{SHEET} {TITLE}", seed=7, tint_var=0.0)
    fn(a)
    o = a.finish(collection=M.coll(NUM, TITLE), mark_asset=not temp, origin=None)
    K.drop_unused_slots(o)
    if not temp:
        K.tag(o, SHEET, TITLE, role, COLLISION[name], budget, NOTES[name])
        if name in SHADING_OK:
            o["kit_shading_ok"] = SHADING_OK[name]
    o[OFF] = [0.0, 0.0, 0.0]
    o.location = (0, 0, 0)
    o["m065_pieces"] = json.dumps([[k, n_, [round(x, 5) for x in c]] for k, n_, c in PIECES])
    bpy.context.view_layer.update()
    return o


def _recentre(o):
    bc = m012._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


def _post(o):
    """Stage 2-3 pass for an object of closed shells: every face a triangle, normals outward per shell, flat shading,
    origin at the bbox bottom centre, UVs (angle-based islands, overlaps cut free), bowties split."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = False
    if o.data.has_custom_normals:
        with M._override(o):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
    _recentre(o)
    lg = {"bowties": M.fix_bowties(o)}
    M.smart_uv(o, **UV)
    lg["uv_cut"] = m012._uv_unfold(o)
    K.drop_unused_slots(o)
    return lg


def _make(name, fn, role="part", budget=1000, temp=False):
    t0 = time.time()
    o = _new(name, fn, role, budget, temp=temp)
    lg = _post(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


# ---- checks ---------------------------------------------------------------------------------------------------------------
def _shells(o):
    """bmesh, shell id per face, shell count, faces per shell, and (kind, name) per shell matched to the build
    register by centroid."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    groups = [[] for _ in range(n)]
    for f in bm.faces:
        groups[ids[f.index]].append(f)
    off = Vector(o[OFF]) if OFF in o else Vector()
    reg = [(k, nm, Vector(c)) for k, nm, c in json.loads(o.get("m065_pieces", "[]"))]
    labels = []
    used = set()
    for fs in groups:
        vs = list({v for f in fs for v in f.verts})
        c = sum((v.co for v in vs), Vector()) / len(vs) + off
        best = min(((i, (rc - c).length) for i, (_, _, rc) in enumerate(reg) if i not in used),
                   key=lambda x: x[1], default=(None, 0))
        if best[0] is not None and best[1] < 0.05:
            used.add(best[0])
            labels.append(reg[best[0]][:2])
        else:
            labels.append(("?", "?"))
    return bm, ids, n, groups, labels


def shells_report(o):
    """Per shell: kind, name, tris, non-manifold edges and verts, boundary edges, winding errors (manifold edges whose
    two faces don't run the same way round), self-intersecting face pairs, signed volume."""
    bm, ids, n, groups, labels = _shells(o)
    out = []
    for k in range(n):
        fs = groups[k]
        es = {e for f in fs for e in f.edges}
        vs = list({v for f in fs for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        hits = sum(1 for a_, b_ in tree.overlap(tree) if a_ < b_ and not set(fs[a_].verts) & set(fs[b_].verts))
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) / 3.0
        out.append({"kind": labels[k][0], "name": labels[k][1], "tris": len(fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary),
                    "winding_errors": sum(1 for e in es if e.is_manifold and not e.is_contiguous),
                    "self_hits": hits, "volume": round(vol, 5), "zmin": round(min(v.co.z for v in vs), 3)})
    bm.free()
    return out


# expected seats (spec 2.1 / 6): pairs that must touch (gap <= CONTACT)
def _seat_pairs():
    p = [(f"star_p{k}", "star_calyx") for k in range(5)] + [("star_bead", "star_calyx"), ("star_stem", "star_calyx"),
                                                            ("star_stem", "hub")]
    p += [(f"bloom_o{k}", "bloom_calyx") for k in range(5)] + [(f"bloom_i{k}", "bloom_calyx") for k in range(5)]
    p += [("bloom_bead", "bloom_calyx"), ("bloom_stem", "bloom_calyx"), ("bloom_stem", "hub")]
    p += [("bell", "bell_cap"), ("bell_stem", "bell_cap"), ("bell_stem", "hub")]
    p += [(k, "hub") for k in LEAVES if LEAVES[k]["tier"] != "rim"]
    return p


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating pieces (STAGES): per shell, its nearest gap to another shell (0 when the triangles intersect) or the
    ground, and whether it chains by contact to the ground. A single-shell part is its own anchor. Also the expected
    seats (petal -> calyx, bead -> calyx, stem -> calyx / cap / hub, bell -> cap, leaf -> hub) and each stone's gap to
    the nearest leaf (spec 6: a leaf above it or the hub within 0.03)."""
    bm, ids, n, groups, labels = _shells(o)
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
    z0 = min(zmin)
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
                kk = (min(s, t), max(s, t))
                near[kk] = min(near.get(kk, 1e9), d)
    for kk in pairs:
        near[kk] = 0.0
    gap = [1e9] * n
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    ground = {k for k in range(n) if zmin[k] - z0 <= tol}
    if n == 1:
        gap = [0.0]
    for k in ground:
        gap[k] = 0.0

    def chained(t):
        adj = {k: set() for k in range(n)}
        for (a_, b_), d in near.items():
            if d <= t:
                adj[a_].add(b_)
                adj[b_].add(a_)
        seen = set(ground) if n > 1 else {0}
        stack = list(seen)
        while stack:
            k = stack.pop()
            for m_ in adj[k]:
                if m_ not in seen:
                    seen.add(m_)
                    stack.append(m_)
        return [labels[k][1] for k in range(n) if k not in seen]
    floating = [k for k in range(n) if gap[k] > tol]
    idx = {labels[k][1]: k for k in range(n)}

    def pair_gap(x, y):
        if x not in idx or y not in idx:
            return None
        a_, b_ = idx[x], idx[y]
        return round(near.get((min(a_, b_), max(a_, b_)), 1e9), 3)
    seats = {f"{x}>{y}": pair_gap(x, y) for x, y in _seat_pairs() if x in idx and y in idx}
    bad_seats = {k: v for k, v in seats.items() if v is None or v > tol}
    leaves = [k for k in range(n) if labels[k][0] in ("leaf", "rim")]
    stones = {}
    for k in range(n):
        if labels[k][0] == "rock":
            g = min([near.get((min(k, j), max(k, j)), 1e9) for j in leaves + [idx.get("hub", -1)] if j >= 0] or [1e9])
            stones[labels[k][1]] = round(g, 3)
    on_ground = {}
    for k in ground:
        on_ground[labels[k][0]] = on_ground.get(labels[k][0], 0) + 1
    unch = chained(tol)
    res = {"shells": n, "floating": len(floating), "floating_names": [labels[k][1] for k in floating],
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "unchained": len(unch), "unchained_names": unch, "unchained_chain_tol": len(chained(chain_tol)),
           "on_ground": on_ground, "sink": round(z0 + (o[OFF][2] if OFF in o else 0.0), 3),
           "kinds": {k: [lb[0] for lb in labels].count(k) for k in sorted({lb[0] for lb in labels})},
           "seats_bad": bad_seats, "seats_n": len(seats), "stone_to_leaf": stones}
    bm.free()
    return res


def _solid(groups, k):
    vs = list({v for f in groups[k] for v in f.verts})
    vi = {v: i for i, v in enumerate(vs)}
    return [v.co.copy() for v in vs], [[vi[v] for v in f.verts] for f in groups[k]]


JUNCTION_R, JUNCTION_Z = 0.32, 0.50          # the leaf junction (close-up 2): petioles and stem feet crowd together here


def bury_report(o):
    """STAGES "nothing buried", by ray parity (m047._Solids) after the final placement:
    - petals: depth inside their bead / calyx beyond the seat (points further than 0.20 from the head axis must be
      clear); the seat depth is reported apart;
    - stems: foot depth in the hub (0.06-0.08), top depth in the calyx / cap;
    - bell: depth in its cap (the seat, 0.03-0.05); beads: depth in their calyx;
    - leaves: depth inside the hub outside their base, inside any stem outside the junction (<= 0.03), share of their
      verts inside another leaf (<= 25 %), depth inside a stone (<= 0.05);
    - stones: deepest leaf point inside each stone."""
    bm, ids, n, groups, labels = _shells(o)
    off = Vector(o[OFF]) if OFF in o else Vector()
    by = {labels[k][1]: k for k in range(n)}
    sol = {}
    for k in range(n):
        s = m047._Solids()
        cos, polys = _solid(groups, k)
        s.add(cos, polys, labels[k][1])
        sol[labels[k][1]] = s

    def pts(k):
        fs = groups[k]
        return [v.co.copy() for v in {v for f in fs for v in f.verts}] + [f.calc_center_median() for f in fs]
    res = {"petals": {}, "leaves": {}, "stems": {}, "beads": {}, "stones": {}}
    over = []
    for hn in HEADS:
        cal, bd = f"{hn}_calyx", f"{hn}_bead"
        if cal not in by:
            continue
        C, e1, e2, nrm = _hframe(hn)
        for k in range(n):
            nm = labels[k][1]
            if labels[k][0] != "petal" or not nm.startswith(hn):
                continue
            seat, beyond = 0.0, 0.0
            for p in pts(k):
                pw = p + off
                rad = ((pw - C) - nrm * (pw - C).dot(nrm)).length
                d = max(sol[bd].point(p)[0], sol[cal].point(p)[0])
                if rad > 0.20:
                    beyond = max(beyond, d)
                else:
                    seat = max(seat, d)
            res["petals"][nm] = (round(seat, 3), round(beyond, 3))
            if beyond > BURY:
                over.append((nm, round(beyond, 3)))
        res["beads"][bd] = round(max(sol[cal].point(p)[0] for p in pts(by[bd])), 3)
        if res["beads"][bd] > 0.10:
            over.append((bd, res["beads"][bd]))
    for hn in ("star", "bloom", "bell"):
        st = f"{hn}_stem"
        if st not in by:
            continue
        P = _stem_path(hn)
        top = "bell_cap" if hn == "bell" else f"{hn}_calyx"
        dh = sol["hub"].point(P[0] - off)[0] if "hub" in sol else None
        dc = sol[top].point(P[-1] - off)[0] if top in sol else None
        res["stems"][st] = {"foot_in_hub": None if dh is None else round(dh, 3),
                            "top_in": None if dc is None else round(dc, 3)}
    if "bell" in by and "bell_cap" in by:
        seat, ax, e1, e2 = _bell_frame()
        res["bell_seat_in_cap"] = round(sol["bell_cap"].point(seat - off)[0], 3)
        res["bell_beyond_cap"] = round(max(sol["bell_cap"].point(p)[0] for p in pts(by["bell"])
                                           if (p + off - seat).dot(ax) > 0.06), 3)
    leaves = [k for k in range(n) if labels[k][0] in ("leaf", "rim")]
    stems = [labels[k][1] for k in range(n) if labels[k][0] == "stem"]
    rocks = [labels[k][1] for k in range(n) if labels[k][0] == "rock"]
    for k in leaves:
        nm = labels[k][1]
        P = pts(k)
        hub_d = stem_d = junc_d = rock_d = 0.0
        for p in P:
            pw = p + off
            r_ = math.hypot(pw.x, pw.y)
            if "hub" in sol and r_ > 0.26:
                hub_d = max(hub_d, sol["hub"].point(p)[0])
            if pw.z > HUB_TOP + 0.02:
                for s in stems:
                    d = sol[s].point(p)[0]
                    if r_ > JUNCTION_R or pw.z > JUNCTION_Z:
                        stem_d = max(stem_d, d)
                    else:
                        junc_d = max(junc_d, d)
            for rk in rocks:
                rock_d = max(rock_d, sol[rk].point(p)[0])
        vs = [v for v in {v for f in groups[k] for v in f.verts}
              if math.hypot((v.co + off).x, (v.co + off).y) > 0.26]          # the bases crowd in the hub by design
        share, of = 0.0, None
        for j in leaves:
            if j == k:
                continue
            inside = sum(1 for v in vs if sol[labels[j][1]].point(v.co)[0] > 0)
            if inside / max(1, len(vs)) > share:
                share, of = inside / max(1, len(vs)), labels[j][1]
        res["leaves"][nm] = {"hub": round(hub_d, 3), "stem_cut": round(stem_d, 3), "junction": round(junc_d, 3),
                             "max_inside_leaf": round(share, 2), "inside_of": of, "in_rock": round(rock_d, 3)}
        if hub_d > BURY or share > 0.25 or rock_d > BURY:
            over.append((nm, round(hub_d, 3), round(share, 2), round(rock_d, 3)))
    for rk in rocks:
        k = by[rk]
        d = 0.0
        for j in leaves:
            d = max(d, max(sol[rk].point(p)[0] for p in pts(j)))
        res["stones"][rk] = round(d, 3)
    bm.free()
    res["over"] = over
    return res


# ---- volume overlap (fix round 1: the round-1 verifier's volumetric sample-point test) ----------------------------------
VOL_N = 1500                                 # sample points inside each leaf / stem shell
LEAF_IN_LEAF = 0.25                          # spec 2.4: no leaf more than 25 % inside another (its whole volume)
STEM_CUT = 0.03                              # spec 2.4: no leaf cuts a stem by more than 0.03 outside the junction


def _vol_points(tree, lo, hi, n, seed, cap=200000):
    """Uniform random points inside a closed shell (rejection in its bbox, ray parity), so a straight stem run with no
    vertex inside a leaf still counts (the round-1 vertex test missed exactly that)."""
    rng = random.Random(seed)
    pts, tries = [], 0
    while len(pts) < n and tries < cap:
        tries += 1
        p = Vector((rng.uniform(lo.x, hi.x), rng.uniform(lo.y, hi.y), rng.uniform(lo.z, hi.z)))
        if m047._parity_in(tree, p):
            pts.append(p)
    return pts


def volume_report(o, n=VOL_N):
    """Leaf-in-leaf and leaf-through-stem by volume (build frame): per leaf, the share of its sample points inside each
    other leaf (whole leaf, and outside the hub junction r > 0.26); per stem, the share of its points inside each leaf
    outside the junction (r > JUNCTION_R or z > JUNCTION_Z), the worst 0.1-tall slice of its cross-section, and the
    cut depth (the deepest such point's distance to the stem's surface). Feeds `problems` through build()."""
    bm, ids, nsh, groups, labels = _shells(o)
    off = Vector(o[OFF]) if OFF in o else Vector()
    sh = {}
    for k in range(nsh):
        kind, nm = labels[k]
        if kind not in ("leaf", "rim", "stem"):
            continue
        cos, polys = _solid(groups, k)
        cos = [c + off for c in cos]
        lo = Vector((min(c.x for c in cos), min(c.y for c in cos), min(c.z for c in cos)))
        hi = Vector((max(c.x for c in cos), max(c.y for c in cos), max(c.z for c in cos)))
        t = BVHTree.FromPolygons(cos, polys)
        sh[nm] = dict(kind=kind, tree=t, lo=lo, hi=hi, pts=_vol_points(t, lo, hi, n, sum(map(ord, nm))))
    bm.free()

    def inside(p, s):
        lo, hi = s["lo"], s["hi"]
        return (lo.x <= p.x <= hi.x and lo.y <= p.y <= hi.y and lo.z <= p.z <= hi.z) and m047._parity_in(s["tree"], p)

    def boxes(a_, b_):
        return all(a_["lo"][i] <= b_["hi"][i] and b_["lo"][i] <= a_["hi"][i] for i in range(3))
    leaves = [k for k, s in sh.items() if s["kind"] in ("leaf", "rim")]
    stems = [k for k, s in sh.items() if s["kind"] == "stem"]
    res = {"leaf_in_leaf": {}, "stem_in_leaf": {}, "pairs": []}
    problems = []
    for a_ in leaves:
        A = sh[a_]
        P = A["pts"]
        outer = [p for p in P if math.hypot(p.x, p.y) > 0.26]
        best = (0.0, 0.0, None)
        for b_ in leaves:
            if b_ == a_ or not boxes(A, sh[b_]):
                continue
            hit = [p for p in P if inside(p, sh[b_])]
            if not hit:
                continue
            w = len(hit) / max(1, len(P))
            wo = sum(1 for p in hit if math.hypot(p.x, p.y) > 0.26) / max(1, len(outer))
            if w >= 0.05:
                res["pairs"].append((a_, b_, round(w, 3), round(wo, 3)))
            if w > best[0]:
                best = (w, wo, b_)
        res["leaf_in_leaf"][a_] = {"share": round(best[0], 3), "outside_junction": round(best[1], 3), "of": best[2],
                                   "pts": len(P)}
        if best[0] > LEAF_IN_LEAF:
            problems.append(f"{o.name}: leaf {a_} {100 * best[0]:.0f} % inside {best[2]} by volume (<= 25)")
    for s_ in stems:
        S = sh[s_]
        P = [p for p in S["pts"] if math.hypot(p.x, p.y) > JUNCTION_R or p.z > JUNCTION_Z]
        worst = {"share": 0.0, "slice": 0.0, "slice_z": None, "cut": 0.0, "by": None}
        for lf in leaves:
            if not boxes(S, sh[lf]):
                continue
            hit = [p for p in P if inside(p, sh[lf])]
            if not hit:
                continue
            cut = max(S["tree"].find_nearest(p)[3] for p in hit)
            sl = {}
            for p in P:
                b = int(p.z / 0.1)
                sl.setdefault(b, [0, 0])[1] += 1
            for p in hit:
                sl[int(p.z / 0.1)][0] += 1
            bz, (hn, tn) = max(sl.items(), key=lambda kv: kv[1][0] / max(1, kv[1][1]))
            share = len(hit) / max(1, len(P))
            if cut > worst["cut"]:
                worst = {"share": round(share, 3), "slice": round(hn / max(1, tn), 3),
                         "slice_z": round(bz * 0.1, 1), "cut": round(cut, 3), "by": lf}
        res["stem_in_leaf"][s_] = worst
        if worst["cut"] > STEM_CUT:
            problems.append(f"{o.name}: leaf {worst['by']} cuts {s_} by {worst['cut']} outside the junction "
                            f"({100 * worst['slice']:.0f} % of its section at z {worst['slice_z']}; <= {STEM_CUT})")
    res["pairs"].sort(key=lambda x: -x[2])
    return res, problems


# ---- foliage visibility (STAGES "Foliage reads from every azimuth" and "Check between the eight views too") ------------
SPIN = tuple(range(0, 360, 45))
# The flower stalks above the rosette (z >= 1.0, the fan's tip height) are what the sheet draws in every view: the
# 15-30 % bare-core limit binds on the core below that (hub and stems rising among the leaves); the whole share is
# reported beside it
STALK_Z = 1.0
SPIN_EL = 10
EDGE15 = math.sin(math.radians(15.0))
EDGE12 = math.sin(math.radians(12.0))
SWEEP_AZ = tuple(range(0, 360, 5))
WHOLE = 0.75        # STAGES: a leaf is wholly edge-on when >= 75 % of its lobe (top) facets are within 15 deg of edge-on
SWEEP_BIND = (10, 20)   # elevations whose whole / sliver limits bind (the spin sheet's e 10 and a standing player's e 20)


def _leaf_records(o):
    """Per leaf shell: name, cluster, area vectors of its faces, its dominant plane normal (the principal axis of its
    area-weighted face normals) and its face-on projected area."""
    import numpy as np
    bm, ids, n, groups, labels = _shells(o)
    cl = {nm: c for c, ns in CLUSTERS.items() for nm in ns}
    out = []
    for k in range(n):
        if labels[k][0] not in ("leaf", "rim"):
            continue
        A = [f.normal * f.calc_area() for f in groups[k]]
        Mx = np.zeros((3, 3))
        for v in A:
            vv = np.array(v)
            Mx += np.outer(vv, vv) / max(1e-9, np.linalg.norm(vv))
        w, V = np.linalg.eigh(Mx)
        nd = Vector(V[:, -1])
        if nd.z < 0:
            nd = -nd
        # the lobe facets: the top surface (both ridge halves, every station band), not the thin edges or the keel
        top = [v for v in A if v.length > 1e-9 and v.normalized().dot(nd) > 0.5]
        out.append(dict(name=labels[k][1], cluster=cl.get(labels[k][1], "?"), A=A, n=nd, top=top,
                        top_area=sum(v.length for v in top), face_on=0.5 * sum(abs(v.dot(nd)) for v in A)))
    bm.free()
    return out


def edge_sweep(o, els=(5, 10, 20)):
    """Azimuth sweep in 5 deg steps (0 ... 355) at each elevation. Per step:
    - sliver: whole leaves seen within 15 deg of edge-on: the leaf's projected area under sin 15 of its face-on area
      (exactly "within 15 deg of edge-on" for a flat card; the ridge V, the keel and the arch count as they show).
      STAGES target: at most about 10 % of the leaf area at any step;
    - plane: leaves whose dominant plane is within 15 deg of edge-on (|n.d| < sin 15), reported (a flat-lying leaf
      seen from a low camera is in this band at every azimuth, so this measure has a floor);
    - comb: most leaves of one cluster in the plane band together.
    Also the closest pair of leaf planes in each cluster (no two leaves of a cluster on one plane: >= 20 deg)."""
    lv = _leaf_records(o)
    tot = sum(l["face_on"] for l in lv)
    res = {}
    for el in els:
        worst = {"whole_n": 0, "whole_area": 0.0, "sliver_n": 0, "sliver_area": 0.0, "plane_n": 0,
                 "plane_area": 0.0, "comb": 0}
        at = {}
        steps = {}
        for az in SWEEP_AZ:
            d = _cam(az, el)
            sl = [l for l in lv if 0.5 * sum(abs(v.dot(d)) for v in l["A"]) < EDGE15 * l["face_on"]]
            wh = [l for l in lv if sum(v.length for v in l["top"] if abs(v.normalized().dot(d)) < EDGE15)
                  >= WHOLE * l["top_area"]]
            pl = [l for l in lv if abs(l["n"].dot(d)) < EDGE15]
            per = {}
            for l in pl:
                per[l["cluster"]] = per.get(l["cluster"], 0) + 1
            s = {"whole_n": len(wh), "whole_area": round(100 * sum(l["face_on"] for l in wh) / tot, 1),
                 "sliver_n": len(sl), "sliver_area": round(100 * sum(l["face_on"] for l in sl) / tot, 1),
                 "plane_n": len(pl), "plane_area": round(100 * sum(l["face_on"] for l in pl) / tot, 1),
                 "comb": max(per.values(), default=0)}
            names = sorted({l["name"] for l in sl + wh})
            steps[az] = (max(s["sliver_n"], s["whole_n"]), max(s["sliver_area"], s["whole_area"]), names)
            for k in worst:
                if s[k] > worst[k]:
                    worst[k] = s[k]
                    at[k] = az
        res[el] = {"worst": worst, "worst_at": at,
                   "sliver_steps": {az: v for az, v in steps.items() if v[0]}}
    planes = {}
    by = {l["name"]: l for l in lv}
    for c, ns in CLUSTERS.items():
        nn = [by[x]["n"] for x in ns if x in by]
        if len(nn) > 1:
            planes[c] = round(min(math.degrees(math.acos(min(1.0, abs(nn[i].dot(nn[j])))))
                                  for i in range(len(nn)) for j in range(i + 1, len(nn))), 1)
    res["min_plane_angle"] = planes
    res["leaves"] = len(lv)
    return res


def vis_report(o, el=SPIN_EL, step=0.02):
    """Eight-azimuth ray-grid visibility (vis.py): per view, the bare core (hub + stems) as a share of the visible
    foliage, the share of visible leaf pixels on facets within 12 deg of edge-on, and the visible share of each head
    (pixels of the head against its best view, so a head turning edge-on shows)."""
    bm, ids, n, groups, labels = _shells(o)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    kind = [labels[ids[f.index]][0] for f in bm.faces]
    nm = [labels[ids[f.index]][1] for f in bm.faces]
    head = []
    for x in nm:
        head.append("star" if x.startswith("star") and not x.endswith("stem") else
                    "bloom" if x.startswith("bloom") and not x.endswith("stem") else
                    "bell" if x in ("bell", "bell_cap") else None)
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    c = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2))
    R = max(max(xs) - min(xs), max(ys) - min(ys)) * 0.6 + 0.1
    Hh = (max(zs) - min(zs)) / 2 + 0.25
    out = {}
    for az in SPIN:
        d = _cam(az, el)
        u = Z.cross(d).normalized()
        w = d.cross(u).normalized()
        cnt, hp = {}, {}
        edge = leafpx = 0
        ni, nj = int(R / step), int(Hh / step)
        for i in range(-ni, ni + 1):
            for j in range(-nj, nj + 1):
                p = c + u * (i * step) + w * (j * step) + d * 20.0
                loc, nrm, fi, dist = tree.ray_cast(p, -d, 60.0)
                if loc is None:
                    continue
                kd = kind[fi]
                cnt[kd] = cnt.get(kd, 0) + 1
                if kd == "stem" and loc.z >= STALK_Z:
                    cnt["stalk"] = cnt.get("stalk", 0) + 1
                if head[fi]:
                    hp[head[fi]] = hp.get(head[fi], 0) + 1
                if kd in ("leaf", "rim"):
                    leafpx += 1
                    if abs(nrm.dot(d)) < EDGE12:
                        edge += 1
        core = cnt.get("stem", 0) + cnt.get("hub", 0)
        fol = leafpx
        out[az] = {"core_share": round(100 * core / max(1, fol), 1),
                   "core_low": round(100 * (core - cnt.get("stalk", 0)) / max(1, fol), 1),
                   "edge12_leaf": round(100 * edge / max(1, fol), 1),
                   "heads_px": hp, "rock_share": round(100 * cnt.get("rock", 0) / max(1, sum(cnt.values())), 1)}
    best = {h: max(v["heads_px"].get(h, 0) for v in out.values()) for h in ("star", "bloom", "bell")}
    # geometric edge-on-ness of the two open heads (occlusion apart): projected area of the head's faces along the
    # view against its face-on projection (along the head normal)
    av = {"star": [], "bloom": []}
    for f in bm.faces:
        if head[f.index] in av:
            av[head[f.index]].append(f.normal * f.calc_area())
    face_on = {h: 0.5 * sum(abs(v.dot(_hframe(h)[3])) for v in vv) for h, vv in av.items()}
    for az, v in out.items():
        v["heads_rel"] = {h: round(v["heads_px"].get(h, 0) / max(1, best[h]), 2) for h in best}
        d = _cam(az, el)
        v["heads_proj"] = {h: round(0.5 * sum(abs(x.dot(d)) for x in vv) / max(1e-9, face_on[h]), 2)
                           for h, vv in av.items()}
        del v["heads_px"]
    bm.free()
    return out


# ---- build ---------------------------------------------------------------------------------------------------------------
PARTS = ((BELL_P, bell_part), (STAR_P, star_part), (BLOOM_P, bloom_part), (STEM_P, stem_part), (LEAF_P, leaf_part),
         (ROCKG_P, rock_grey_part), (ROCKB_P, rock_brown_part), (BASE_P, base_part))
TARGET_SIZE = ((3.0, 0.2), (2.3, 0.2), (2.4, 0.08))   # hero W (X), D (Y), H (Z) +- tolerance (decision 1)
HERO_BUDGET = 1600


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m065_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", HERO))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def sweep_problems(sw):
    out = []
    for el in SWEEP_BIND:
        w = sw.get(el, {}).get("worst", {})
        for k in ("whole", "sliver"):
            if w.get(k + "_area", 0) > 10:
                out.append(f"{HERO}: {k} edge-on (15 deg) leaves {w[k + '_area']} % of the leaf area at e {el} az "
                           f"{sw[el]['worst_at'].get(k + '_area')} (target <= 10)")
    flat = {c: a for c, a in sw.get("min_plane_angle", {}).items() if a < 20}
    if flat:
        out.append(f"{HERO}: leaves of one cluster on (nearly) one plane {flat}")
    return out


def build(render=True, parts=True, close=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    EXPLODE["on"] = False
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn)
    h, log["hero"] = _make(HERO, hero_all, "hero", HERO_BUDGET)
    leaves = {k: dict(v) for k, v in LEAF_INFO.items()}
    heads = {k: dict(v) for k, v in HEAD_INFO.items()}
    rocks = {k: dict(v) for k, v in ROCK_INFO.items()}
    _cleanup_tmp()
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.2f} x {d.y:.2f} x {d.z:.2f}"
    audits = [M.audit(o) for o in order]
    thin = {o.name: m012._thin(o, 2.0) for o in order}
    shells = {o.name: shells_report(o) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = HERO_BUDGET if o is h else 999
        if au["tris"] > lim:
            problems.append(f"{o.name}: {au['tris']} tris over {lim}")
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "wire_edges", "loose_verts",
                  "zero_area_faces", "ngons"):
            if au[k]:
                problems.append(f"{o.name}: {k} {au[k]}")
        if au["normals"] != "outward":
            problems.append(f"{o.name}: normals {au['normals']}")
        for i, s in enumerate(shells[o.name]):
            for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "winding_errors", "self_hits"):
                if s[k]:
                    problems.append(f"{o.name} shell {i} ({s['name']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['name']}): not closed outward (volume {s['volume']})")
            if s["kind"] == "?":
                problems.append(f"{o.name} shell {i}: not matched to a built piece")
    contact = {o.name: contact_report(o) for o in order}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: floating {c['floating_names']}, unchained {c['unchained_names']}")
        if c["seats_bad"]:
            problems.append(f"{n_}: seats not touching {c['seats_bad']}")
        far = {k: v for k, v in c["stone_to_leaf"].items() if v > CONTACT}
        if n_ == HERO and far:
            problems.append(f"{n_}: stones not touching a leaf or the hub {far}")
        if n_ == HERO and c["sink"] < -0.031:
            problems.append(f"{n_}: sinks {c['sink']} below the ground (decision 10: at most 0.03)")
    bury = {h.name: bury_report(h)}
    for n_, b in bury.items():
        if b["over"]:
            problems.append(f"{n_}: buried pieces {b['over']}")
        for st, d in b["stems"].items():
            if d["foot_in_hub"] is not None and not (0.05 <= d["foot_in_hub"] <= 0.085):
                problems.append(f"{n_}: {st} foot {d['foot_in_hub']} inside the hub (0.06-0.08 wanted)")
            if d["top_in"] is not None and not (0.03 <= d["top_in"] <= 0.085):
                problems.append(f"{n_}: {st} top {d['top_in']} inside its calyx / cap (0.04-0.08 wanted)")
        for lf, d in b["leaves"].items():
            if d["stem_cut"] > 0.03:
                problems.append(f"{n_}: leaf {lf} cuts a stem by {d['stem_cut']} (<= 0.03)")
        if b.get("bell_beyond_cap", 0) > BURY:
            problems.append(f"{n_}: bell {b['bell_beyond_cap']} inside its cap beyond the seat")
    # fix round 1: leaf-in-leaf and leaf-through-stem by volume (sample points inside each shell), binding
    volume = {}
    for o in [h] + [objs[n_] for n_ in (BASE_P,) if n_ in objs]:
        volume[o.name], vp = volume_report(o)
        problems += vp
    for k, lf in leaves.items():
        if lf["min_z"] < -SINK - 0.011:
            problems.append(f"{HERO}: leaf {k} dips to z {lf['min_z']}")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 11: none)")
    for n_, t in thin.items():
        if t["under"]:
            problems.append(f"{n_}: {t['under']} faces with a corner under 2 deg (min {t['min_deg']})")
    winding = {o.name: sum(s["winding_errors"] for s in shells[o.name]) for o in order}
    bowties = {o.name: au["nonmanifold_verts"] for o, au in zip(order, audits)}
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    sweep = edge_sweep(h)
    problems += sweep_problems(sweep)
    vis = vis_report(h)
    for az, v in vis.items():
        if v["edge12_leaf"] > 10:
            problems.append(f"{HERO}: view {az} edge-on (12 deg) {v['edge12_leaf']} % of the visible leaves (<= 10)")
        if v["core_low"] > 30:
            problems.append(f"{HERO}: view {az} bare core below the stalks {v['core_low']} % of the foliage (<= 30)")
        low = {k: x for k, x in v["heads_proj"].items() if x < 0.30}
        if len(low) > 1:                    # spec 4.2: no more than one head near edge-on at once
            problems.append(f"{HERO}: view {az} two heads nearly edge-on {low}")
    kinds = {}
    for s in shells[HERO]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts", "origin_offset", "transforms_applied")} for au in audits],
           "hero_shells": kinds, "contact": contact, "bury": bury, "volume": volume, "winding": winding,
           "bowties": bowties,
           "leaves": leaves, "heads": heads, "rocks": rocks, "thin": thin, "log": log, "problems": problems, "uv": uv,
           "sweep": sweep, "vis": vis,
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders -------------------------------------------------------------------------------------------------------------
# decision 9: front_sheet (0, 5) governs positions, f34_sheet the read (probed: spec "Stage 1"); floor hidden, 3x lens
SHEET_VIEWS = {"f34_sheet": (-10, 14), "r34_sheet": (170, 12), "front_sheet": (0, 5), "side_sheet": (90, 5),
               "side270_sheet": (270, 5), "rear_sheet": (180, 5), "top_sheet": (0, 85)}
VIEW_NAMES = ("front", "side", "rear", "top", "underside")
PARTS_SHOT = (0, 15)
PART_SHOTS = {BELL_P: (-20, 10), STAR_P: (0, 15), BLOOM_P: (0, 15), STEM_P: (-25, 10), LEAF_P: (-20, 30),
              ROCKG_P: (-20, 20), ROCKB_P: (-20, 20), BASE_P: (-10, 15)}


def _exploded(objs):
    """A temp build with the pieces drawn apart: heads lifted along their stems (petals spread, bead above, calyx
    below), the bell lifted with its cap, stems lifted 0.3, the spreading leaves pulled 0.35 out, drooping and rim
    leaves 0.22, the stones 0.3."""
    EXPLODE["on"] = True
    try:
        o = _new(PFX + "exploded", hero_all, "part", 1000, temp=True)
    finally:
        EXPLODE["on"] = False
    o.location = (objs[0].location.x + 30, objs[0].location.y, 0)
    bpy.context.view_layer.update()
    return [o]


def _parts_row(objs):
    """Linked copies of the parts in a row like the sheet's PARTS (ISOLATED) strip, then the leaf base."""
    coll = objs[0].users_collection[0]
    out = []
    x = objs[0].location.x + 60
    for o in objs[1:]:
        c = bpy.data.objects.new(PFX + "row_" + o.name, o.data)
        coll.objects.link(c)
        w = o.dimensions.x
        c.location = (x + w / 2, objs[0].location.y, 0)
        x += w + 0.3
        out.append(c)
    bpy.context.view_layer.update()
    return out


def _scale_marker(h, at, name="char"):
    """A 5.5-stud character stand-in at build-frame point `at`."""
    a = K.fk().Asset(PFX + name, "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=DARK, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=DARK, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=DARK, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
    c.location = off @ Vector(at)
    bpy.context.view_layer.update()
    return c


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    row = _parts_row(objs) if len(objs) > 1 else []
    markers = [_scale_marker(h, (2.6, 0.0, 0.0)), _scale_marker(h, (-2.6, 0.0, 0.0), "char2")]
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        extra["front34"] = ([h], -10, 14)
        extra["rear34"] = ([h], 170, 12)
        for o in objs[1:]:
            extra["part_" + o.name.replace(HERO, "").lower()] = ([o], *PART_SHOTS.get(o.name, PARTS_SHOT))
        if row:
            extra["parts_row"] = (row, 0, 15)
        if shown:
            extra["exploded"] = (shown, -10, 15)
        extra["scale"] = ([h] + markers, -20, 6)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = m033._long_lens(kit)
        try:
            sheet = M.views(NUM, [h], names=VIEW_NAMES, extra=extra, vfx=True)
            spin = render_spin(h)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet, "spin": spin}
        if close:
            out.update(render_close_ups(objs))
        return out
    finally:
        for o in shown + markers + row:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0 and me.name.startswith(PFX):
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def render_spin(h):
    """The eight-azimuth contact sheet (STAGES "Foliage reads from every azimuth"): az 0, 45 ... 315 at e 10, the
    long lens and the floor hidden, two rows of four -> spin.png. Call with the long-lens render_group installed."""
    kit = K.NS["KIT"]
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    old = kit["CELL"]
    kit["CELL"] = (420, 360)
    try:
        paths = [kit["render_group"]([h], f"{d}/spin_{az:03d}_sheet.png", az, SPIN_EL) for az in SPIN]
    finally:
        kit["CELL"] = old
    rows = [kit["hstack"](paths[i:i + 4]) for i in (0, 4)]
    out = f"{d}/M065_spin.png"
    kit["save_px"](kit["vstack"](rows), out)
    return out


def render_close_ups(objs):
    """star_cu (face-on to the star: close-up 1), star_edge (the star edge-on in its own plane: petal and bead
    thickness), bell_under (from below and in front: lobes, rim, the dark inside), bell_cu, bloom_cu (into the cup),
    bloom_edge (the bloom side-on: a cup, not a saucer), rosette_cu, junction_cu (close-up 2), base_under (the hero
    from below, close-up 3) and base_part_under (the LeafBase part), edge_side (90, 0) / edge_front (0, 0), petal_edge
    (the BlueStar part edge-on), thumb (the front at about 120 px)."""
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    by = {o.name: o for o in objs}
    h = objs[0]
    out = {}

    def at(o, p):
        return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)
    rc = m033.render_close
    C, e1, e2, n = _hframe("star")
    az, el = _azel(n)
    out["star_cu"] = rc([h], f"{d}/star_cu.png", az, el, at(h, C + n * 0.05), 0.7)
    az_e = math.degrees(math.atan2(e1.x, -e1.y))
    el_e = math.degrees(math.asin(max(-1, min(1, e1.z))))
    out["star_edge"] = rc([h], f"{d}/star_edge.png", az_e, el_e, at(h, C), 0.62)
    seat, ax, b1, b2 = _bell_frame()
    mouth = seat + ax * 0.8
    out["bell_under"] = rc([h], f"{d}/bell_under.png", -30, -40, at(h, mouth), 0.6)
    out["bell_cu"] = rc([h], f"{d}/bell_cu.png", -25, 8, at(h, seat + ax * 0.42), 0.62)
    C2, f1, f2, n2 = _hframe("bloom")
    az2, el2 = _azel(n2)
    out["bloom_cu"] = rc([h], f"{d}/bloom_cu.png", az2, el2, at(h, C2 + n2 * 0.1), 0.6)
    az3 = math.degrees(math.atan2(f1.x, -f1.y))
    out["bloom_edge"] = rc([h], f"{d}/bloom_edge.png", az3, 0, at(h, C2 + n2 * 0.12), 0.6)
    out["rosette_cu"] = rc([h], f"{d}/rosette_cu.png", -15, 40, at(h, (0.0, -0.05, 0.40)), 1.5)
    out["junction_cu"] = rc([h], f"{d}/junction_cu.png", -5, 14, at(h, (0.0, -0.15, 0.35)), 0.6)
    out["base_under"] = rc([h], f"{d}/base_under.png", 0, -60, at(h, (0, 0, 0.1)), 1.4)
    if BASE_P in by:
        b = by[BASE_P]
        out["base_part_under"] = rc([b], f"{d}/base_part_under.png", 0, -60, at(b, (0, 0, 0.1)), 0.9)
    if STAR_P in by:
        p = by[STAR_P]
        Cp, g1, g2, gn = _hframe("star", (270, 30))
        out["petal_edge"] = rc([p], f"{d}/petal_edge.png", 90, -30 + 0.0, at(p, Cp), 0.55)
    out["edge_side"] = rc([h], f"{d}/edge_side.png", 90, 0, at(h, (0.0, 0.0, 1.1)), 1.5)
    out["edge_front"] = rc([h], f"{d}/edge_front.png", 0, 0, at(h, (0.0, 0.0, 1.1)), 1.6)
    kit = K.NS["KIT"]
    old = kit["CELL"]
    kit["CELL"] = (150, 125)
    try:
        orig, kit["render_group"] = m033._long_lens(kit)
        try:
            out["thumb"] = kit["render_group"]([h], f"{d}/thumb_sheet.png", 0, 5)
        finally:
            kit["render_group"] = orig
    finally:
        kit["CELL"] = old
    return out


def preview(names=("front_sheet", "f34_sheet", "rear_sheet", "side_sheet", "top_sheet"), vfx=False, spin=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        r = M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
        if spin:
            r = [r, render_spin(h)]
        return r
    finally:
        kit["render_group"] = orig


def hero_only():
    """Rebuild just the hero (tuning loop)."""
    M.coll(NUM, TITLE)
    palette()
    EXPLODE["on"] = False
    h, lg = _make(HERO, hero_all, "hero", HERO_BUDGET)
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, _ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"hero": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                        "boundary_edges", "normals")}, "log": lg,
            "leaves": dict(LEAF_INFO), "heads": dict(HEAD_INFO), "rocks": dict(ROCK_INFO),
            "offset": [round(x, 3) for x in h[OFF]]}
