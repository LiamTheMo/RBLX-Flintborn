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
PALETTE = {
    BELL: ("#8455E0", 0.75, True),
    BELL_DEEP: ("#5A36C0", 0.8, True),
    STAR: ("#6A7CF0", 0.75, True),
    STAR_DEEP: ("#4F5EE0", 0.75, True),
    STAR_BEAD: ("#F0D860", 0.6, False),
    PINK: ("#F06898", 0.75, True),
    PINK_DEEP: ("#E03868", 0.75, True),
    BLOOM_BEAD: ("#E0A800", 0.6, False),
    LIGHT: ("#7AA622", 0.8, True),
    MID: ("#467A14", 0.85, True),
    DARK: ("#3E6E20", 0.85, True),
    STEM: ("#447A18", 0.85, True),
    ROCK_G: ("#8C7B72", 0.9, True),
    ROCK_B: ("#8E5530", 0.9, True),
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
LEAF_ST = (0.0, 0.45, 0.76)                  # Bezier parameter of the section stations (tip point at 1.0)
LEAF_HW = (0.17, 0.50, 0.34)                 # half-width per station, fraction of W
PET_ST, PET_HW = (0.0, 0.10, 0.48, 0.78), (0.11, 0.24, 0.50, 0.33)   # spreading leaves: the petiole neck first
PET_LEN, PET_HWABS = 0.20, 0.055             # petiole stub length, its half-width (a 0.11-wide stub)
RIM_ST, RIM_HW = (0.0, 0.52), (0.22, 0.50)
SPINE_HW = (0.13, 0.36, 0.50)                # drooping leaves: base on the hub, the blade's upper end, its widest
EDGE = {"fan": 0.03, "spread": 0.03, "droop": 0.03, "rim": 0.05}   # half the edge thickness (rim edges 0.10)
RIDGE = {"fan": 19.0, "spread": 18.0, "droop": 17.0, "rim": 15.0}  # each half rises this much to the ridge
KEEL = 0.025
FAN_Z, RING_Z, BASE_R = 0.13, 0.08, 0.11     # leaf base points on the hub (inside it)
# name -> tier, azimuth (growth direction: its face turns up and out along it), tip, W, spine: pitch (Bezier control
# along az / pitch at half the chord) or ctrl, or spine (drooping leaves: the blade's upper end and its widest point);
# roll (a fixed growth twist, deg); tone per band (base, body, tip) on LADDER; base (rim leaves: on the ground)
LEAVES = {
    # leaf base: the five-leaf upright fan behind the stems
    "F1": dict(tier="fan", az=158, tip=(-0.74, 0.34, 1.04), W=0.46, pitch=64, roll=24, tone=(0.5, 1.0, 1.75)),
    "F2": dict(tier="fan", az=112, tip=(-0.30, 0.56, 1.26), W=0.48, pitch=74, roll=-22, tone=(0.5, 1.0, 1.75)),
    "F3": dict(tier="fan", az=76, tip=(0.12, 0.58, 1.04), W=0.46, pitch=70, roll=26, tone=(0.75, 1.0, 1.25)),
    "F4": dict(tier="fan", az=40, tip=(0.62, 0.48, 1.27), W=0.50, pitch=66, roll=-24, tone=(0.75, 1.0, 1.75)),
    "F5": dict(tier="fan", az=352, tip=(0.84, 0.02, 1.04), W=0.46, pitch=58, roll=22, tone=(1.0, 1.5, 2.0)),
    # spreading leaves on petiole stubs (the exploded's "Leaf (Reusable)")
    "S1": dict(tier="spread", az=178, tip=(-1.48, 0.06, 0.72), W=0.56, ctrl=(-0.86, 0.03, 0.80), roll=10,
               tone=(0.5, 1.0, 1.25)),
    "S2": dict(tier="spread", az=204, tip=(-1.36, -0.50, 0.17), W=0.52, ctrl=(-0.84, -0.32, 0.50), roll=-12,
               tone=(0.25, 1.0, 1.0)),
    "S3": dict(tier="spread", az=4, tip=(1.52, 0.10, 0.66), W=0.56, ctrl=(0.90, 0.07, 0.76), roll=-10,
               tone=(1.0, 1.75, 2.0)),
    "S4": dict(tier="spread", az=334, tip=(1.40, -0.60, 0.17), W=0.52, ctrl=(0.86, -0.36, 0.50), roll=12,
               tone=(0.5, 1.0, 1.25)),
    # big drooping lime leaves, front and back: rise off the hub, then lay their tips on the ground
    "N1": dict(tier="droop", az=250, tip=(-0.40, -1.06, 0.035), W=0.62, roll=8, tone=(1.25, 2.0, 2.0),
               spine=((-0.10, -0.30, 0.46), (-0.24, -0.66, 0.36))),
    "N2": dict(tier="droop", az=290, tip=(0.48, -1.06, 0.035), W=0.66, roll=-8, tone=(1.25, 2.0, 2.0),
               spine=((0.11, -0.30, 0.62), (0.29, -0.66, 0.44))),
    "N3": dict(tier="droop", az=82, tip=(0.16, 1.08, 0.035), W=0.62, roll=-6, tone=(1.25, 2.0, 2.0),
               spine=((0.04, 0.30, 0.58), (0.10, 0.68, 0.42))),
    "N4": dict(tier="droop", az=124, tip=(-0.55, 0.92, 0.035), W=0.54, roll=10, tone=(1.0, 1.75, 2.0),
               spine=((-0.16, 0.27, 0.44), (-0.34, 0.57, 0.32))),
    # rim: short chunky kites lying low on the ground round the hub
    "B1": dict(tier="rim", az=226, base=(-0.27, -0.27), tip=(-0.80, -0.64, 0.06), W=0.40, roll=8,
               tone=(0.0, 0.25)),
    "B2": dict(tier="rim", az=316, base=(0.27, -0.27), tip=(0.82, -0.62, 0.06), W=0.40, roll=-8, tone=(1.0, 1.75)),
    "B3": dict(tier="rim", az=152, base=(-0.29, 0.22), tip=(-0.86, 0.54, 0.06), W=0.38, roll=-6, tone=(0.0, 0.25)),
    "B4": dict(tier="rim", az=28, base=(0.29, 0.22), tip=(0.86, 0.54, 0.06), W=0.38, roll=6, tone=(0.0, 0.75)),
}
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
        base = Vector((s["base"][0], s["base"][1], -SINK + EDGE["rim"] + KEEL))
        ctrl = (base + tip) / 2 + Vector((0, 0, RIM_ARCH))
        pts = [(_bez(base, ctrl, tip, t), _bezd(base, ctrl, tip, t).normalized()) for t in RIM_ST]
        return pts, tip, [f * s["W"] for f in RIM_HW], [_bez(base, ctrl, tip, i / 20) for i in range(21)]
    z0 = FAN_Z if tier == "fan" else RING_Z + 0.04
    base = Vector((math.cos(az) * BASE_R, math.sin(az) * BASE_R, z0))
    if tier == "spread":
        d = Vector((math.cos(az), math.sin(az), 0.18)).normalized()
        b1 = base + d * PET_LEN                         # petiole end: the blade starts here
        ctrl = Vector(s["ctrl"])
        pts = [(base, d)]
        hws = [PET_HWABS]
        for t, f in zip(PET_ST, PET_HW):
            pts.append((_bez(b1, ctrl, tip, t), _bezd(b1, ctrl, tip, t).normalized()))
            hws.append(PET_HWABS if t == 0.0 else f * s["W"])
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
    stations, tip, hws, poly = _leaf_spine(name)
    az = math.radians(s["az"])
    w0 = Vector((-math.sin(az), math.cos(az), 0.0))
    out = Vector((math.cos(az), math.sin(az), 0))
    sh = _shift(out * (0.35 if tier == "spread" else 0.22 if tier in ("droop", "rim") else 0.0))
    bm = a.bm
    rings = []
    E, RD = EDGE[tier], math.radians(RIDGE[tier])
    for (p, T), hw in zip(stations, hws):
        w = (w0 - T * T.dot(w0)).normalized()
        n = T.cross(w).normalized()
        if s.get("roll"):                   # a fixed growth twist about the leaf's own axis (never per camera)
            q = Matrix.Rotation(math.radians(s["roll"]), 3, T)
            w, n = q @ w, q @ n
        e = min(E, 0.45 * hw)
        rf = e + hw * math.tan(RD)
        rk = e + KEEL
        pts = [p - w * hw + n * e, p + n * rf, p + w * hw + n * e, p + w * hw - n * e, p - n * rk, p - w * hw - n * e]
        rings.append([bm.verts.new(q_ + sh) for q_ in pts])
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
    elif tier == "spread":                  # petiole + blade base, body, outer band + tip
        groups = [bands[0] + bands[1] + [cap], bands[2], bands[3] + tipf]
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
    "star": dict(c=(0.40, 0.30, 1.96), az=300, tilt=45, phase=96, foot=(0.07, 0.07),
                 via=[(0.27, 0.22, 0.90), (0.36, 0.36, 1.58)]),
    "bloom": dict(c=(1.10, -0.28, 1.36), az=255, tilt=42, phase=92, foot=(0.07, -0.07),
                  via=[(0.45, -0.11, 0.62), (0.80, -0.14, 0.96)]),
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
BL_OUT = dict(L=0.46, W=0.38, st=(0.0, 0.55, 1.0), hw=(0.20, 0.50, 0.40), lift=(28, 46, 62), T=0.05)
BL_IN = dict(L=0.30, W=0.28, st=(0.0, 0.55, 1.0), hw=(0.22, 0.50, 0.38), lift=(54, 68, 80), T=0.05)
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
    sh = sh if sh is not None else _shift(n * 0.45 + Vector((0, 0, 0.30)))
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
    sh = sh if sh is not None else _shift(n * 0.45 + Vector((0, 0, 0.30)))
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
                                          (4.0 if k % 2 else -4.0), None,
                                          sh + _shift(r * (0.16 if ring == "o" else 0.06)))
            rng = _rng("bloom" + ring, k)
            _close(a, vs, bands[0] + bands[1] + [cap0] + end, PINK, tint=1.0 + rng.uniform(-0.025, 0.025))
            if ring == "o":                 # outer petals: a deep-rose inner band, pink body (position along it)
                _paint(a, bands[0] + [cap0], _mix(PINK_DEEP, PINK, 0.25))
                _paint(a, bands[1] + end, PINK)
            else:                           # inner petals: deep throat at the base -> pink at the tips
                _paint(a, bands[0] + [cap0], PINK_DEEP)
                _paint(a, bands[1] + end, _mix(PINK_DEEP, PINK, 0.5))
            _reg("petal", f"bloom_{ring}{k}", vs)
            zs += [v.co.z for v in vs]
    if flat is None:
        HEAD_INFO["bloom"] = {"centre": [round(x, 3) for x in C], "normal": [round(x, 3) for x in n],
                              "z_range": [round(min(zs), 3), round(max(zs), 3)]}


# bell (spec 1.4): a lathed 6-sided closed shell hanging from a 6-sided cap, six pointed flared lobes, an inner wall
BELL_SEAT = (-0.87, -0.23, 1.93)            # the bell's dome seat (top), in the cap
BELL_TILT, BELL_TILT_AZ = 15.0, 215.0       # the bell's axis: down, tilted toward the front-left
BELL_L = 0.80
# outer (fraction of L, radius): seat, dome shoulder, flank, mouth (the lobes' notches and tips follow)
BELL_OUT = ((0.0, 0.085), (0.13, 0.18), (0.55, 0.245), (0.80, 0.31))
BELL_NOTCH = (0.88, 0.335)                  # between the lobes (mid-panel), higher
BELL_TIP = (1.00, 0.42, 0.04)               # lobe tips on the ribs: L fraction, radius, curl up (studs)
BELL_WALL = 0.05
BELL_IN = ((0.62, 0.20), (0.33, 0.0))       # inner flank ring, the inner dome apex
CAP = ((-0.04, 0.10), (0.06, 0.115), (0.10, 0.075))   # cap rings: (height above the seat along -axis, radius)
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
    """The bell: outer rings seat -> dome shoulder -> flank -> mouth, a 12-vert zigzag mouth (six pointed lobe tips on
    the ribs, flared out and curled a little up, six notches between them), a rim band, an inner zigzag 0.05 inside,
    an inner flank ring and an inner dome apex: one closed shell with a real inside. 106 tris. Outer shell `bell`, its
    dome band a step lighter toward the swatch by height in the bell's frame; the inner wall and the rim `bell_deep`
    (a region: the sheet's deep violet under the lobes and in the mouth)."""
    seat, ax, e1, e2 = _bell_frame(flat)
    sh = sh if sh is not None else _shift(Vector((-0.25, -0.15, 0.75)))
    bm = a.bm
    ph = math.radians(BELL_PHASE)
    L = BELL_L

    def at(fr, r, ang, lift=0.0):
        return seat + ax * (fr * L - lift) + (e1 * math.cos(ang) + e2 * math.sin(ang)) * r

    outer = [[bm.verts.new(at(fr, r, ph + k * math.pi / 3) + sh) for k in range(6)] for fr, r in BELL_OUT]
    zig_o, zig_i = [], []
    for k in range(6):
        a0 = ph + k * math.pi / 3
        zig_o.append(bm.verts.new(at(BELL_TIP[0], BELL_TIP[1], a0, BELL_TIP[2]) + sh))
        zig_o.append(bm.verts.new(at(BELL_NOTCH[0], BELL_NOTCH[1], a0 + math.pi / 6) + sh))
        zig_i.append(bm.verts.new(at(BELL_TIP[0] - 0.035, BELL_TIP[1] - BELL_WALL * 1.3, a0, BELL_TIP[2]) + sh))
        zig_i.append(bm.verts.new(at(BELL_NOTCH[0] - 0.02, BELL_NOTCH[1] - BELL_WALL, a0 + math.pi / 6) + sh))
    inner = [bm.verts.new(at(BELL_IN[0][0], BELL_IN[0][1], ph + k * math.pi / 3) + sh) for k in range(6)]
    apex = bm.verts.new(seat + ax * (BELL_IN[1][0] * L) + sh)
    seat_cap = bm.faces.new(list(reversed(outer[0])))
    dome = _band(bm, outer[0], outer[1])
    flank = _band(bm, outer[1], outer[2]) + _band(bm, outer[2], outer[3])
    mouth = []
    m = outer[-1]
    for k in range(6):
        j = (k + 1) % 6
        t0, nt, t1 = zig_o[2 * k], zig_o[2 * k + 1], zig_o[(2 * k + 2) % 12]
        mouth += [bm.faces.new((m[k], t0, nt)), bm.faces.new((m[k], nt, m[j])), bm.faces.new((m[j], nt, t1))]
    rim = _band(bm, zig_o, zig_i)
    inside = []
    for k in range(6):
        j = (k + 1) % 6
        t0, nt, t1 = zig_i[2 * k], zig_i[2 * k + 1], zig_i[(2 * k + 2) % 12]
        inside += [bm.faces.new((inner[k], nt, t0)), bm.faces.new((inner[k], inner[j], nt)),
                   bm.faces.new((inner[j], t1, nt))]
    inside += [bm.faces.new((inner[(k + 1) % 6], inner[k], apex)) for k in range(6)]
    vs = [v for r in outer for v in r] + zig_o + zig_i + inner + [apex]
    _close(a, vs, [seat_cap] + dome + flank + mouth + rim + inside, BELL, tint=1.0 + _rng("bell").uniform(-0.02, 0.02))
    _paint(a, dome + [seat_cap], _mix(BELL, BELL_DEEP, 0.0))
    _paint(a, rim + inside, BELL_DEEP)
    for k in range(6):                      # broad tint per lobe panel (never per triangle)
        _tint(a, mouth[3 * k:3 * k + 3] + [flank[k], flank[6 + k]], 1.0 + _rng("bell", k).uniform(-0.03, 0.03))
    _reg("bell", "bell", vs)
    return vs


def bell_cap(a, flat=False, sh=None):
    """The bell's 6-sided green cap on the bell's axis (spec 1.4: Ø 0.18-0.23 x 0.14), stem colour, the top ring
    half mid (by position). 20 tris."""
    seat, ax, e1, e2 = _bell_frame(flat)
    sh = sh if sh is not None else _shift(Vector((-0.25, -0.15, 0.85)))
    bm = a.bm
    rings = [[bm.verts.new(x + sh) for x in _ring(seat - ax * h, e1, e2, r, 6, math.radians(BELL_PHASE + 30 * i))]
             for i, (h, r) in enumerate(CAP)]
    bands = [_band(bm, rings[i], rings[i + 1]) for i in range(len(rings) - 1)]
    bot = bm.faces.new(list(reversed(rings[0])))
    top = bm.faces.new(rings[-1])
    vs = [v for r in rings for v in r]
    _close(a, vs, bands[0] + bands[1] + [bot, top], STEM, tint=1.0 + _rng("cap").uniform(-0.02, 0.02))
    _paint(a, bands[1] + [top], _mix(STEM, MID, 0.5))
    _reg("cap", "bell_cap", vs)
    return vs


# ---- stems (spec 2.3, 3.5: square prisms, straight segments, crisp mitred bends) ----------------------------------------
def _crook_path():
    seat, ax, e1, e2 = _bell_frame()
    ctop = seat - ax * CAP[-1][0]           # the cap's top centre
    end = ctop + ax * STEM_IN               # the hook's end, inside the cap
    return [Vector((-0.08, 0.02, STEM_FOOT_Z)), Vector((-0.27, -0.03, 0.80)), Vector((-0.42, -0.07, 1.40)),
            Vector((-0.55, -0.10, 1.90)), Vector((-0.62, -0.13, 2.10)), Vector((-0.74, -0.19, 2.14)), end]


def _stem_path(name):
    if name == "bell":
        return _crook_path()
    s = HEADS[name]
    C, e1, e2, n = _hframe(name)
    cb = C + n * (STAR_CALYX if name == "star" else BL_CALYX)[0][0]
    foot = Vector((s["foot"][0], s["foot"][1], STEM_FOOT_Z))
    return [foot] + [Vector(v) for v in s["via"]] + [cb - n * CROOK, cb + n * STEM_IN]


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
    sh = _shift((0, 0, 0.30))
    vs, bands, c0, c1 = square_tube(a, pts, STEM_SIDE, STEM, name + "_stem", sh=sh)
    _paint(a, bands[0] + [c0], _mix(STEM, DARK, 0.5))    # the foot a step deeper where it enters the leaves
    _reg("stem", f"{name}_stem", vs)
    return vs


# ---- stones (spec 2.5: squat faceted nuggets, flat base) ---------------------------------------------------------------
# name -> centre (x, y), W, D, H, yaw (deg), sides, key
ROCKS = {
    "R1": dict(c=(-1.02, -0.58), W=0.48, D=0.40, H=0.27, yaw=20, n=6, key=ROCK_G),
    "R2": dict(c=(0.93, -0.66), W=0.36, D=0.30, H=0.23, yaw=-30, n=6, key=ROCK_B),
    "R3": dict(c=(0.70, 0.68), W=0.36, D=0.30, H=0.22, yaw=45, n=6, key=ROCK_B),
    "R4": dict(c=(-0.76, 0.66), W=0.44, D=0.36, H=0.26, yaw=-15, n=6, key=ROCK_G),
    "R5": dict(c=(-1.16, 0.34), W=0.26, D=0.22, H=0.15, yaw=70, n=5, key=ROCK_B),
}
ROCK_INFO = {}


def rock(a, name, fit=None):
    """A faceted nugget: an n-sided base ring (r +-10 %), the widest ring at 0.38 H, a shoulder ring at 0.76 H pulled in
    and turned half a step, a sloping n-sided top; flat base sunk SINK. 4n + 2(n-2) tris (32 for n 6). `fit` (a BVH of
    the leaves) lowers or raises the top so the leaf above just touches it (spec 6: stones touch a leaf within 0.03,
    no leaf more than 0.05 inside). The lowest band 25 % deeper (contact), broad tint per stone."""
    s = ROCKS[name]
    rng = _rng(name)
    n = s["n"]
    yaw = math.radians(s["yaw"])
    cx, cy = s["c"]
    H = s["H"]
    sh = _shift(Vector((cx, cy, 0)).normalized() * 0.30 if (cx or cy) else Vector())
    jit = [1.0 + rng.uniform(-0.10, 0.10) for _ in range(n)]

    def ring(fr, rf, z, rot):
        out = []
        for k in range(n):
            ang = yaw + rot + 2 * math.pi * k / n
            out.append(Vector((cx + math.cos(ang) * s["W"] / 2 * rf * jit[k],
                               cy + math.sin(ang) * s["D"] / 2 * rf * jit[k], z)))
        return out
    rows = [ring(0, 0.86, -SINK, 0.0), ring(0, 1.0, 0.38 * H, 0.0), ring(0, 0.74, 0.76 * H, math.pi / n)]
    tilt = Vector((math.cos(yaw + 0.7), math.sin(yaw + 0.7), 0))
    top = [Vector((p.x * 0.62 + cx * 0.38, p.y * 0.62 + cy * 0.38, H)) for p in ring(0, 1.0, H, 0.0)]
    for p in top:                           # a sloping top
        p.z += (p - Vector((cx, cy, H))).dot(tilt) * 0.22
    rows.append(top)
    if fit is not None:
        gaps = []
        for p in rows[2] + rows[3]:
            hit = fit.ray_cast(p + Vector((0, 0, -0.001)), Vector((0, 0, 1)), 0.35)
            if hit[0] is not None:
                gaps.append(hit[3])
            back = fit.ray_cast(p + Vector((0, 0, 0.30)), Vector((0, 0, -1)), 0.30)
            if back[0] is not None and back[3] < 0.30:       # the leaf surface is below this vert: inside a leaf
                gaps.append(-(0.30 - back[3]))
        if gaps:
            g = min(gaps)
            zt = max(p.z for p in rows[3])
            f = max(0.65, min(1.45, (zt + g + 0.012) / zt))
            for r in rows[1:]:
                for p in r:
                    p.z *= f
            ROCK_INFO[name] = {"fit": round(f, 3), "gap0": round(g, 3)}
    bm = a.bm
    vr = [[bm.verts.new(p + sh) for p in r] for r in rows]
    bands = [_band(bm, vr[i], vr[i + 1]) for i in range(3)]
    bot = bm.faces.new(list(reversed(vr[0])))
    topf = bm.faces.new(vr[3])
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
    fit = None if EXPLODE["on"] else _leaf_bvh(a, set(LEAVES))
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


def _neck(a, name, rings_hr):
    C, e1, e2, n = _hframe(name, (270, 30))
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
    bloom_head(a, flat=(270, 34), sh=Vector())
    _neck(a, "bloom", BL_CALYX)


def stem_part(a):
    """'Stem (Example)': a straight square prism 0.13 x 0.75 with a slanted top cut (the exploded 'Stem (Blue)')."""
    PIECES.clear()
    vs, bands, c0, c1 = square_tube(a, [Vector((0, 0, 0)), Vector((0, 0, 0.38)), Vector((0, 0, 0.75))],
                                    (0.13, 0.125), STEM, "stem_part", slant=0.45)
    _paint(a, bands[0] + [c0], _mix(STEM, DARK, 0.5))
    _reg("stem", "stem", vs)


def leaf_part(a):
    PIECES.clear()
    leaf(a, "S1")


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
        share = 0.0
        for j in leaves:
            if j == k:
                continue
            inside = sum(1 for v in vs if sol[labels[j][1]].point(v.co)[0] > 0)
            share = max(share, inside / max(1, len(vs)))
        res["leaves"][nm] = {"hub": round(hub_d, 3), "stem_cut": round(stem_d, 3), "junction": round(junc_d, 3),
                             "max_inside_leaf": round(share, 2), "in_rock": round(rock_d, 3)}
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


# ---- foliage visibility (STAGES "Foliage reads from every azimuth" and "Check between the eight views too") ------------
SPIN = tuple(range(0, 360, 45))
SPIN_EL = 10
EDGE15 = math.sin(math.radians(15.0))
EDGE12 = math.sin(math.radians(12.0))
SWEEP_AZ = tuple(range(0, 360, 5))


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
        out.append(dict(name=labels[k][1], cluster=cl.get(labels[k][1], "?"), A=A, n=nd,
                        face_on=0.5 * sum(abs(v.dot(nd)) for v in A)))
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
        worst = {"sliver_n": 0, "sliver_area": 0.0, "plane_n": 0, "plane_area": 0.0, "comb": 0}
        at = {}
        steps = {}
        for az in SWEEP_AZ:
            d = _cam(az, el)
            sl = [l for l in lv if 0.5 * sum(abs(v.dot(d)) for v in l["A"]) < EDGE15 * l["face_on"]]
            pl = [l for l in lv if abs(l["n"].dot(d)) < EDGE15]
            per = {}
            for l in pl:
                per[l["cluster"]] = per.get(l["cluster"], 0) + 1
            s = {"sliver_n": len(sl), "sliver_area": round(100 * sum(l["face_on"] for l in sl) / tot, 1),
                 "plane_n": len(pl), "plane_area": round(100 * sum(l["face_on"] for l in pl) / tot, 1),
                 "comb": max(per.values(), default=0)}
            steps[az] = (s["sliver_n"], s["sliver_area"], [l["name"] for l in sl])
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
                if head[fi]:
                    hp[head[fi]] = hp.get(head[fi], 0) + 1
                if kd in ("leaf", "rim"):
                    leafpx += 1
                    if abs(nrm.dot(d)) < EDGE12:
                        edge += 1
        core = cnt.get("stem", 0) + cnt.get("hub", 0)
        fol = leafpx
        out[az] = {"core_share": round(100 * core / max(1, fol), 1), "edge12_leaf": round(100 * edge / max(1, fol), 1),
                   "heads_px": hp, "rock_share": round(100 * cnt.get("rock", 0) / max(1, sum(cnt.values())), 1)}
    best = {h: max(v["heads_px"].get(h, 0) for v in out.values()) for h in ("star", "bloom", "bell")}
    for az, v in out.items():
        v["heads_rel"] = {h: round(v["heads_px"].get(h, 0) / max(1, best[h]), 2) for h in best}
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
    w = sw.get(10, {}).get("worst", {})
    if w.get("sliver_area", 0) > 10:
        out.append(f"{HERO}: edge-on (15 deg) leaves {w['sliver_area']} % of the leaf area at e 10 az "
                   f"{sw[10]['worst_at'].get('sliver_area')} (target <= 10)")
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
        if v["core_share"] > 30:
            problems.append(f"{HERO}: view {az} bare core {v['core_share']} % of the foliage (<= 30)")
        low = {k: x for k, x in v["heads_rel"].items() if x < 0.35}
        if low:
            problems.append(f"{HERO}: view {az} heads nearly edge-on or hidden {low}")
    kinds = {}
    for s in shells[HERO]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts", "origin_offset", "transforms_applied")} for au in audits],
           "hero_shells": kinds, "contact": contact, "bury": bury, "winding": winding, "bowties": bowties,
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
