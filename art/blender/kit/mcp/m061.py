"""061 Meadow Herb (references/061.png): a common meadow plant. Three chunky white daisies on thick hexagonal stems
(tallest near the centre facing front-up, a lower one at the left facing front-left, a middle one at the right turned
toward +X) over a rosette of 17 broad, thick, faceted kite leaves round a hidden octagonal hub. Each head is five broad
blunt cream lozenge petals with real thickness round a faceted golden bead, on a faceted green cup with a crook in the
stem under it. No glow, no VFX.

    import importlib, kit_models, m061; importlib.reload(kit_models); importlib.reload(m061); m061.build()

Build frame: studs, front -Y, +X right, ground z 0, the hub axis on (0, 0). Every object ends with its origin at its
bbox bottom centre; o["m061_offset"] is that origin in the build frame. Names (spec 8, decision 2):
- MeadowHerb (hero): hub + 17 leaves + 3 stems + 3 cups + 3 beads + 15 petals, one object of separate closed shells
  (no booleans). Collision none (walk-through meadow cover).
- MeadowHerbPetal (one petal, lying in its own frame), MeadowHerbCenter (one bead), MeadowHerbStem (H_M's stem with its
  crook and cup), MeadowHerbLeaf (N1's big kite), MeadowHerbLeafBase (hub + the five-leaf fan F1-F5).
Every head, petal and leaf is placed by growth (head normal, leaf azimuth / pitch), never turned toward a camera.
Colour (stage 4) is painted by role and by position along each piece inside the builders, never by facing.
Stages 5-6: none (the sheet shows no glow, light or effect). See M061_spec.md.
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

NUM, TITLE, SHEET = 61, "Meadow Herb", "M061"
OFF = "m061_offset"
PFX = "_m061_"
HERO = "MeadowHerb"
PETAL_P, CENTER_P, STEM_P = "MeadowHerbPetal", "MeadowHerbCenter", "MeadowHerbStem"
LEAF_P, BASE_P = "MeadowHerbLeaf", "MeadowHerbLeafBase"

PETAL, PETAL_BASE = "m061_petal", "m061_petal_base"
CENTRE = "m061_centre"
LIGHT, MID, DARK, STEM = "m061_leaf_light", "m061_leaf_mid", "m061_leaf_dark", "m061_stem"
LADDER = (DARK, MID, LIGHT)                  # leaf tone value 0..2

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
BURY = 0.05
SINK = 0.02                                  # the hub and the rim leaves sink this far (decision 10: at most 0.03)

# key -> (hex, roughness, low specular). Stage 4 writes the calibrated values here (spec "Stage 4").
PALETTE = {
    PETAL: ("#E8E0CC", 0.8, True),       # raised from #D6D0C3: the shaded rear petals read grey (verifier R1 minor 1)
    PETAL_BASE: ("#DED2B8", 0.8, True),  # raised from #CFC6B5 with it
    CENTRE: ("#EDB600", 0.6, False),
    LIGHT: ("#80A533", 0.8, True),
    MID: ("#44751C", 0.85, True),
    DARK: ("#43702B", 0.85, True),
    STEM: ("#3F681E", 0.85, True),
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions), K.sample kinds
TARGETS = {PETAL: ((0xF5, 0xEF, 0xDF), "all"), PETAL_BASE: ((0xEF, 0xE5, 0xCF), "all"),
           CENTRE: ((0xFC, 0xCE, 0x0B), "vivid"),
           LIGHT: ((0x9E, 0xCB, 0x34), "vivid"), MID: ((0x59, 0x8E, 0x1C), "green"),
           DARK: ((0x4D, 0x83, 0x2B), "green"), STEM: ((0x48, 0x7A, 0x1E), "green")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m061_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k == "m061_" + tail), None)
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
_faces = m033._faces
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


# ---- explode state and piece register -----------------------------------------------------------------------------------
EXPLODE = {"on": False}
PIECES = []                                  # (kind, name, centroid in the build frame) per shell, in build order


def _shift(vec):
    return Vector(vec) if EXPLODE["on"] else Vector()


def _reg(kind, name, vs):
    if not EXPLODE["on"]:
        PIECES.append((kind, name, sum((v.co for v in vs), Vector()) / len(vs)))


# ---- hub (spec 2.2: an 8-sided collar, closed, hidden by the leaves) -----------------------------------------------------
HUB_R0, HUB_R1, HUB_TOP = 0.21, 0.18, 0.18


def hub(a):
    bm = a.bm
    rng = random.Random(61001)
    rings = []
    for z, r in ((-SINK, HUB_R0), (HUB_TOP, HUB_R1)):
        rings.append([bm.verts.new((math.cos(math.pi / 8 + k * math.pi / 4) * r * (1 + rng.uniform(-0.04, 0.04)),
                                    math.sin(math.pi / 8 + k * math.pi / 4) * r * (1 + rng.uniform(-0.04, 0.04)), z))
                      for k in range(8)])
    side = _band(bm, rings[0], rings[1])
    bot = bm.faces.new(list(reversed(rings[0])))
    top = bm.faces.new(rings[1])
    vs = rings[0] + rings[1]
    _close(a, vs, side + [bot, top], DARK)
    _tint(a, side + [bot, top], 1.0 + rng.uniform(-0.03, 0.03))
    _reg("hub", "hub", vs)
    return vs


# ---- leaves (spec 2.4: closed faceted kites with a ridge V and a keel, along an arched spine) ---------------------
LEAF_ST = (0.0, 0.42, 0.74)                  # Bezier parameter of the section stations (tip point at 1.0)
LEAF_HW = (0.17, 0.50, 0.36)                 # half-width per station, fraction of W (base 0.34 W, widest W, 0.72 W)
RIM_ST, RIM_HW = (0.0, 0.50), (0.16, 0.50)
RIM_ARCH = 0.40                              # rim leaves arch up and lay their tips back on the ground
SPINE_HW = (0.12, 0.30, 0.50)                # hanging leaves: petiole on the hub, the blade's upper end, its widest
EDGE = 0.03                                  # half the edge thickness (edges 0.06 thick)
RIDGE_DEG = 13.0                             # each half rises this much to the ridge (dihedral ~26 deg: one half lit)
KEEL = 0.02
FAN_Z, RING_Z, BASE_R = 0.14, 0.08, 0.11     # leaf base points on the hub (inside it by >= 0.07)
# name -> tier, azimuth (the leaf's growth direction: its face turns up and out along it), tip, W, and the spine:
# pitch (Bezier control along az / pitch at half the chord), ctrl (explicit Bezier control point) or spine (hanging
# leaves: the blade's upper end and its widest point; see _leaf_spine); roll (a fixed growth twist, deg); tone per
# band (base, body, tip) on LADDER; base (rim leaves: the base point on the ground)
LEAVES = {
    # leaf base: the five-leaf fan (three upright, two spreading and drooping at the tips)
    "F1": dict(tier="fan", az=72, tip=(0.18, 0.52, 1.30), W=0.60, pitch=66, roll=32, tone=(0.5, 1.0, 1.75)),
    "F2": dict(tier="fan", az=140, tip=(-0.38, 0.34, 1.32), W=0.60, pitch=66, roll=-30, tone=(0.5, 1.0, 1.75)),
    "F3": dict(tier="fan", az=18, tip=(0.42, 0.08, 1.26), W=0.58, pitch=66, roll=30, tone=(1.0, 1.25, 2.0)),
    "F4": dict(tier="fan", az=194, tip=(-1.30, -0.26, 0.62), W=0.74, roll=-30, tone=(0.5, 1.0, 1.75),
               spine=((-0.30, -0.24, 0.56), (-0.80, -0.27, 0.84))),
    "F5": dict(tier="fan", az=6, tip=(1.30, 0.06, 0.66), W=0.74, roll=30, tone=(1.0, 1.25, 2.0),
               spine=((0.30, 0.10, 0.58), (0.80, 0.07, 0.88))),
    # ring: big hanging kites (front and back), rising leaves, small diamonds
    "N1": dict(tier="ring", az=240, tip=(-0.55, -1.05, 0.02), W=0.74, roll=0, tone=(1.0, 1.5, 2.0),
               spine=((-0.20, -0.30, 0.74), (-0.38, -0.62, 0.42))),
    "N2": dict(tier="ring", az=305, tip=(0.72, -1.0, 0.02), W=0.74, roll=0, tone=(1.0, 1.5, 2.0),
               spine=((0.20, -0.28, 0.74), (0.45, -0.60, 0.42))),
    "N3": dict(tier="ring", az=125, tip=(-0.62, 0.98, 0.03), W=0.70, roll=0, tone=(1.25, 2.0, 2.0),
               spine=((-0.20, 0.28, 0.70), (-0.40, 0.60, 0.40))),
    "N4": dict(tier="ring", az=55, tip=(0.62, 0.98, 0.03), W=0.70, roll=0, tone=(1.0, 1.75, 2.0),
               spine=((0.20, 0.28, 0.70), (0.40, 0.60, 0.40))),
    "N5": dict(tier="ring", az=342, tip=(0.86, -0.26, 1.02), W=0.58, pitch=50, roll=0, tone=(1.0, 1.75, 2.0)),
    "N6": dict(tier="ring", az=150, tip=(-0.70, 0.42, 0.98), W=0.58, pitch=55, roll=0, tone=(0.5, 1.0, 1.5)),
    "N7": dict(tier="ring", az=272, tip=(0.02, -0.70, 0.03), W=0.48, roll=0, tone=(1.0, 1.25, 1.75),
               spine=((0.0, -0.28, 0.42), (0.01, -0.46, 0.26))),
    "N8": dict(tier="ring", az=88, tip=(0.0, 0.70, 0.03), W=0.46, roll=0, tone=(1.25, 2.0, 2.0),
               spine=((0.0, 0.28, 0.40), (0.0, 0.46, 0.25))),
    # rim: small dark leaves arching low at the rim, their bases on the ground under the ring leaves
    "K1": dict(tier="rim", az=205, base=(-0.34, -0.20), tip=(-1.06, -0.46, 0.05), W=0.52, tone=(0.0, 0.0, 0.25)),
    "K2": dict(tier="rim", az=335, base=(0.36, -0.18), tip=(1.08, -0.46, 0.05), W=0.52, tone=(0.0, 0.0, 0.25)),
    "K3": dict(tier="rim", az=150, base=(-0.34, 0.22), tip=(-1.0, 0.64, 0.05), W=0.50, tone=(0.0, 0.0, 0.25)),
    "K4": dict(tier="rim", az=30, base=(0.34, 0.22), tip=(1.02, 0.64, 0.05), W=0.50, tone=(0.0, 0.0, 0.25)),
}
FAN = ("F1", "F2", "F3", "F4", "F5")
LEAF_INFO = {}


def _leaf_pts(name):
    s = LEAVES[name]
    az = math.radians(s["az"])
    tip = Vector(s["tip"])
    if s["tier"] == "rim":
        base = Vector((s["base"][0], s["base"][1], -SINK + EDGE + KEEL))
        ctrl = (base + tip) / 2 + Vector((0, 0, RIM_ARCH))
        return base, ctrl, tip
    z0 = FAN_Z if s["tier"] == "fan" else RING_Z
    base = Vector((math.cos(az) * BASE_R, math.sin(az) * BASE_R, z0))
    if "ctrl" in s:
        ctrl = Vector(s["ctrl"])
    else:
        ctrl = base + _dir(s["az"], s["pitch"]) * ((tip - base).length * 0.5)
    return base, ctrl, tip


def _leaf_spine(name):
    """Station points with tangents, the tip, and the half-width fractions of a leaf. Bezier leaves: stations on the
    quadratic Bezier (base on the hub, control, tip). Hanging leaves ("spine"): base on the hub, the blade's narrow
    upper end high near the centre, its widest point on the way down, the tip on the ground; the rising petiole part
    hides behind the blade."""
    s = LEAVES[name]
    if "spine" in s:
        az = math.radians(s["az"])
        base = Vector((math.cos(az) * BASE_R, math.sin(az) * BASE_R, FAN_Z if s["tier"] == "fan" else RING_Z))
        P = [base] + [Vector(q) for q in s["spine"]]
        tip = Vector(s["tip"])
        Q = P + [tip]
        T = [(Q[1] - Q[0]).normalized()] + [((Q[i] - Q[i - 1]).normalized() + (Q[i + 1] - Q[i]).normalized())
                                           .normalized() for i in range(1, len(P))]
        return list(zip(P, T)), tip, SPINE_HW, Q
    base, ctrl, tip = _leaf_pts(name)
    st, hwf = (RIM_ST, RIM_HW) if s["tier"] == "rim" else (LEAF_ST, LEAF_HW)
    pts = [(_bez(base, ctrl, tip, t), _bezd(base, ctrl, tip, t).normalized()) for t in st]
    return pts, tip, hwf, [_bez(base, ctrl, tip, i / 20) for i in range(21)]


def leaf(a, name):
    """One leaf: 6-vert sections (left edge top, ridge, right edge top, right edge bottom, keel, left edge bottom)
    along the arched spine, the face turned up and radially outward along its azimuth (growth, never a camera) with
    a fixed growth twist, a base cap and a tip point. 34 tris (rim leaves 22). Each station band takes one tone by
    role and position along the leaf."""
    s = LEAVES[name]
    stations, tip, hwf, poly = _leaf_spine(name)
    az = math.radians(s["az"])
    w0 = Vector((-math.sin(az), math.cos(az), 0.0))
    W = s["W"]
    sh = _shift(Vector((math.cos(az), math.sin(az), 0)) * (0.35 if s["tier"] != "fan" else 0.0))
    bm = a.bm
    rings = []
    for (p, T), f in zip(stations, hwf):
        w = (w0 - T * T.dot(w0)).normalized()
        n = T.cross(w).normalized()
        if s.get("roll"):                   # a fixed growth twist about the leaf's own axis (never per camera)
            q = Matrix.Rotation(math.radians(s["roll"]), 3, T)
            w, n = q @ w, q @ n
        hw = f * W
        e = min(EDGE, 0.4 * hw)
        rf = e + hw * math.tan(math.radians(RIDGE_DEG))
        rk = e + KEEL
        pts = [p - w * hw + n * e, p + n * rf, p + w * hw + n * e, p + w * hw - n * e, p - n * rk, p - w * hw - n * e]
        rings.append([bm.verts.new(q + sh) for q in pts])
    apex = bm.verts.new(tip + sh)
    bands = [_band(bm, rings[k], rings[k + 1]) for k in range(len(rings) - 1)]
    tipf = [bm.faces.new((rings[-1][i], rings[-1][(i + 1) % 6], apex)) for i in range(6)]
    cap = bm.faces.new(list(reversed(rings[0])))
    vs = [v for r in rings for v in r] + [apex]
    rng = random.Random(sum(map(ord, name)) * 7 + 61)
    _close(a, vs, [f for b in bands for f in b] + tipf + [cap], MID, tint=1.0 + rng.uniform(-0.03, 0.03))
    groups = ([bands[0] + [cap], bands[1], tipf] if len(bands) == 2 else [bands[0] + [cap], tipf, tipf])
    tones = s["tone"]
    if len(bands) == 1:                     # rim leaf: base band, tip fan
        groups = [bands[0] + [cap], tipf]
        tones = (tones[0], tones[2])
    for fs, tv in zip(groups, tones):
        _paint(a, fs, _tone(tv))
        _tint(a, fs, 1.0 + rng.uniform(-0.02, 0.02))
    L = sum((poly[i + 1] - poly[i]).length for i in range(len(poly) - 1))
    last = (tip - stations[-1][0]).length
    top = max(v.co.z for v in vs)
    LEAF_INFO[name] = {"L": round(L, 3), "W": W, "LW": round(L / W, 2), "top_z": round(top, 3),
                       "tip": [round(x, 3) for x in tip], "min_z": round(min(v.co.z for v in vs), 3),
                       "tip_deg": round(math.degrees(2 * math.atan2(hwf[len(stations) - 1] * W, last)), 1)}
    _reg("rim" if s["tier"] == "rim" else "leaf", name, vs)
    return vs


# ---- heads: petals, bead, cup (spec 2.3) ---------------------------------------------------------------------------------
PET_R0 = 0.06                               # petal base radius from the head centre (under the bead)
PET_ST = (0.0, 0.58, 1.0)                   # stations along the petal (fraction of its length)
PET_HW = (0.15, 0.50, 0.28)                 # half-width per station, fraction of W: base 0.30 W, widest W, blunt end 0.56 W
PET_T, PET_CREASE = 0.05, 0.012             # plate thickness; the centre line rises this much over the edges
PET_LIFT = (11.0, 14.0, 11.5, 14.5, 12.5)   # deg out of the head plane per petal (a shallow cup; no two coplanar)
PET_ROLL = (4.0, -5.0, 3.0, -4.0, 5.0)      # deg about the petal's own axis
BEAD_R, BEAD_EQ, BEAD_TOP, BEAD_TOPR, BEAD_BOT = 0.20, 0.04, 0.145, 0.13, -0.08
CUP = ((-0.18, 0.08), (-0.09, 0.13), (-0.01, 0.175))   # (height along the normal, radius) bottom -> top
STEM_IN = 0.06                              # the stem's top end this far inside the cup's bottom
CROOK = 0.09                                # the crook this far below the cup bottom, on the cup axis
STEM_R = (0.075, 0.065)                     # foot, top (hex, Ø 0.15 -> 0.13)
STEM_FOOT_Z = HUB_TOP - 0.07
# name -> petal-plane centre, normal (az, tilt from vertical), petal phase (deg from the horizontal in-plane axis),
# petal tip radius, petal W, stem foot on the hub top and the stem's via points
HEADS = {
    "H_M": dict(c=(0.10, 0.30, 1.73), az=300, tilt=45, phase=54, R=0.56, W=0.37, foot=(0.04, 0.05),
                via=[(0.03, 0.12, 0.62), (0.02, 0.27, 1.18)]),
    "H_R": dict(c=(0.89, -0.165, 1.60), az=330, tilt=60, phase=40, R=0.54, W=0.36, foot=(0.07, -0.03),
                via=[(0.28, -0.06, 0.72), (0.53, -0.07, 1.22)]),
    "H_L": dict(c=(-0.81, -0.06, 1.37), az=250, tilt=55, phase=25, R=0.50, W=0.36, foot=(-0.06, 0.0),
                via=[(-0.33, 0.03, 0.60), (-0.60, 0.09, 0.98)]),
}
HEAD_INFO = {}


def _hframe(name, flat=False):
    s = HEADS[name]
    if flat:
        return Vector(), Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    a_, t_ = math.radians(s["az"]), math.radians(s["tilt"])
    n = Vector((math.cos(a_) * math.sin(t_), math.sin(a_) * math.sin(t_), math.cos(t_)))
    e1 = Vector((0, 0, 1)).cross(n).normalized()
    e2 = n.cross(e1).normalized()
    return Vector(s["c"]), e1, e2, n


def petal(a, name, k, flat=False):
    """Petal k of head `name`: a closed blunt lozenge plate (5-vert section: two top edges, a raised centre crease,
    two bottom edges) at three stations from under the bead out to the blunt end, lifted out of the head plane.
    26 tris. Inner band petal_base, the rest petal (position along the petal)."""
    s = HEADS[name]
    C, e1, e2, n = _hframe(name, flat)
    ang = math.radians(s["phase"] + 72 * k)
    r = e1 * math.cos(ang) + e2 * math.sin(ang)
    lift = math.radians(PET_LIFT[k])
    u = (r * math.cos(lift) + n * math.sin(lift)).normalized()
    w = n.cross(r).normalized()
    p = u.cross(w).normalized()
    q = Matrix.Rotation(math.radians(PET_ROLL[k]), 3, u)
    w, p = q @ w, q @ p
    L = s["R"] - PET_R0
    W = s["W"]
    sh = _shift(r * 0.25 + n * 0.55)
    bm = a.bm
    rings = []
    c0 = C + r * PET_R0 + n * (0.004 * (k % 2))
    for st, f in zip(PET_ST, PET_HW):
        c = c0 + u * (st * L)
        hw = f * W
        t = PET_T / 2
        pts = [c - w * hw + p * t, c + p * (t + PET_CREASE), c + w * hw + p * t, c + w * hw - p * t, c - w * hw - p * t]
        rings.append([bm.verts.new(x + sh) for x in pts])
    bands = [_band(bm, rings[i], rings[i + 1]) for i in range(len(rings) - 1)]
    cap0 = bm.faces.new(list(reversed(rings[0])))
    cap1 = bm.faces.new(rings[-1])
    vs = [v for rr in rings for v in rr]
    rng = random.Random(sum(map(ord, name)) * 13 + k)
    _close(a, vs, bands[0] + bands[1] + [cap0, cap1], PETAL, tint=1.0 + rng.uniform(-0.02, 0.02))
    _paint(a, bands[0], _mix(PETAL_BASE, PETAL, 0.5))
    _paint(a, [cap0], PETAL_BASE)
    _reg("petal", f"{name}_p{k}", vs)
    return vs


def bead(a, name, flat=False):
    """The centre: a squat faceted gem: a bottom point (sunk in the cup), an 8-sided equator just above the petals,
    an 8-sided top ring turned half a step (antiprism facets) and a flat octagonal top. 30 tris. One golden key: an
    orange-gold lower band (spec 5.3) correlates with facing on a gem whatever drives it (K.check corr 0.95-0.98 on
    the Center part), and in the hero the bead's lower half sits inside the petal ring and cup, so the sheet's orange
    lower band is left to the lighting."""
    C, e1, e2, n = _hframe(name, flat)
    sh = _shift(n * 0.85)
    bm = a.bm
    eq = [bm.verts.new(x + sh) for x in _ring(C + n * BEAD_EQ, e1, e2, BEAD_R, 8, math.radians(7))]
    top = [bm.verts.new(x + sh) for x in _ring(C + n * BEAD_TOP, e1, e2, BEAD_TOPR, 8, math.radians(7 + 22.5))]
    bot = bm.verts.new(C + n * BEAD_BOT + sh)
    lower = [bm.faces.new((eq[(i + 1) % 8], eq[i], bot)) for i in range(8)]
    up = []
    for i in range(8):
        up.append(bm.faces.new((eq[i], eq[(i + 1) % 8], top[i])))
        up.append(bm.faces.new((top[i], eq[(i + 1) % 8], top[(i + 1) % 8])))
    cap = bm.faces.new(top)
    vs = eq + top + [bot]
    _close(a, vs, lower + up + [cap], CENTRE, tint=1.0 + random.Random(sum(map(ord, name))).uniform(-0.02, 0.02))
    _reg("bead", f"{name}_bead", vs)
    return vs


def cup(a, name, flat=False):
    """The calyx: an 8-sided flared cup on the head's axis (two rings of outer faces), a flat top under the petals and
    a flat bottom. 44 tris. Stem colour, the upper ring of faces a step lighter (close-up 1's lit rim, by position)."""
    C, e1, e2, n = _hframe(name, flat)
    sh = _shift(n * 0.30)
    bm = a.bm
    rings = [[bm.verts.new(x + sh) for x in _ring(C + n * h, e1, e2, r, 8)] for h, r in CUP]
    bands = [_band(bm, rings[i], rings[i + 1]) for i in range(len(rings) - 1)]
    bot = bm.faces.new(list(reversed(rings[0])))
    top = bm.faces.new(rings[-1])
    vs = [v for rr in rings for v in rr]
    _close(a, vs, [f for b in bands for f in b] + [bot, top], STEM,
           tint=1.0 + random.Random(sum(map(ord, name)) + 5).uniform(-0.02, 0.02))
    _paint(a, bands[-1] + [top], _mix(STEM, MID, 0.5))
    _reg("cup", f"{name}_cup", vs)
    return vs


def _stem_path(name):
    s = HEADS[name]
    C, e1, e2, n = _hframe(name)
    cb = C + n * CUP[0][0]
    foot = Vector((s["foot"][0], s["foot"][1], STEM_FOOT_Z))
    return [foot] + [Vector(v) for v in s["via"]] + [cb - n * CROOK, cb + n * STEM_IN]


def stem(a, name):
    """A hexagonal prism along the stem path (foot inside the hub top, via points, the crook on the cup axis, the top
    end inside the cup), rings mitred at each bend, flat caps. 6 x 2 per segment + 8 tris. Stem colour, the lowest
    segment a step deeper where it enters the leaves (by position)."""
    pts = _stem_path(name)
    nseg = len(pts) - 1
    radii = [STEM_R[0] + (STEM_R[1] - STEM_R[0]) * i / nseg for i in range(len(pts))]
    fr = m047._frames(pts, Vector((1, 0, 0)))
    sh = _shift((0, 0, 0.30))
    bm = a.bm
    rings = []
    for i, (p, rr, (t, u, v)) in enumerate(zip(pts, radii, fr)):
        if 0 < i < nseg:                    # mitre: widen the ring across the bend so the prism keeps its width
            d0, d1 = (pts[i] - pts[i - 1]).normalized(), (pts[i + 1] - pts[i]).normalized()
            rr /= max(0.75, math.cos(d0.angle(d1) / 2))
        rings.append([bm.verts.new(x + sh) for x in _ring(p, u, v, rr, 6)])
    bands = [_band(bm, rings[i], rings[i + 1]) for i in range(nseg)]
    c0 = bm.faces.new(list(reversed(rings[0])))
    c1 = bm.faces.new(rings[-1])
    vs = [v for rr in rings for v in rr]
    _close(a, vs, [f for b in bands for f in b] + [c0, c1], STEM,
           tint=1.0 + random.Random(sum(map(ord, name)) + 9).uniform(-0.02, 0.02))
    _paint(a, bands[0] + [c0], _mix(STEM, DARK, 0.5))
    _reg("stem", f"{name}_stem", vs)
    return vs


def head(a, name, flat=False):
    out = {"cup": cup(a, name, flat), "bead": bead(a, name, flat)}
    out["petals"] = [petal(a, name, k, flat) for k in range(5)]
    if not flat:
        C, e1, e2, n = _hframe(name)
        tips = [max(v.co.z for v in vs) for vs in out["petals"]]
        HEAD_INFO[name] = {"centre": [round(x, 3) for x in C],
                           "bead_centre": [round(x, 3) for x in C + n * ((BEAD_EQ + BEAD_TOP) / 2)],
                           "normal": [round(x, 3) for x in n], "top_z": round(max(tips), 3),
                           "ring_d": round(2 * HEADS[name]["R"], 2)}
    return out


def flower(a, name):
    head(a, name)
    stem(a, name)


# ---- assemblies ----------------------------------------------------------------------------------------------------------
def hero_all(a):
    PIECES.clear()
    LEAF_INFO.clear()
    HEAD_INFO.clear()
    hub(a)
    for k in LEAVES:
        leaf(a, k)
    for k in HEADS:
        flower(a, k)


def petal_part(a):
    PIECES.clear()
    petal(a, "H_M", 0, flat=True)


def center_part(a):
    PIECES.clear()
    bead(a, "H_M", flat=True)


def stem_part(a):
    PIECES.clear()
    cup(a, "H_M")
    stem(a, "H_M")


def leaf_part(a):
    PIECES.clear()
    leaf(a, "N1")


def base_part(a):
    PIECES.clear()
    hub(a)
    for k in FAN:
        leaf(a, k)


NOTES = {
    HERO: "Meadow herb: three chunky white five-petal daisies (golden faceted beads, faceted green cups) on thick hex "
          "stems over a rosette of 17 thick faceted kite leaves round a hidden octagonal hub. Walk-through meadow "
          "cover (collision none). Sheet header 62/132.",
    PETAL_P: "Petal (x5): broad blunt cream lozenge plate with a centre crease and real thickness",
    CENTER_P: "Center (x1): squat faceted golden bead with an orange-gold lower band",
    STEM_P: "Stem (x1): thick hexagonal stem with a crook under a flared 8-sided green cup",
    LEAF_P: "Leaf (x1): big thick faceted kite with a ridge and keel, lime over a mid base",
    BASE_P: "Leaf Base (x1): octagonal hub with the five-leaf fan (three upright, two spreading)",
}
COLLISION = {HERO: "none", PETAL_P: "none", CENTER_P: "none", STEM_P: "none", LEAF_P: "none", BASE_P: "none"}


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
    o["m061_pieces"] = json.dumps([[k, n_, [round(x, 5) for x in c]] for k, n_, c in PIECES])
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
    reg = [(k, nm, Vector(c)) for k, nm, c in json.loads(o.get("m061_pieces", "[]"))]
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


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating pieces (STAGES): per shell, its nearest gap to another shell (0 when the triangles intersect) or the
    ground, and whether it chains by contact to the ground (petal -> cup / bead -> stem -> hub -> ground; leaf -> hub
    -> ground; rim leaf -> ground). A single-shell part is its own anchor. Also each petal's seat on its own cup / bead
    and each stem's contact with its own cup and the hub."""
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
    seats = {}
    for hn in HEADS:
        if f"{hn}_cup" in idx:
            seats[hn] = {"petal_to_cup": [pair_gap(f"{hn}_p{k}", f"{hn}_cup") for k in range(5)],
                         "petal_to_bead": [pair_gap(f"{hn}_p{k}", f"{hn}_bead") for k in range(5)],
                         "bead_to_cup": pair_gap(f"{hn}_bead", f"{hn}_cup"),
                         "stem_to_cup": pair_gap(f"{hn}_stem", f"{hn}_cup"),
                         "stem_to_hub": pair_gap(f"{hn}_stem", "hub")}
    on_ground = {}
    for k in ground:
        on_ground[labels[k][0]] = on_ground.get(labels[k][0], 0) + 1
    unch = chained(tol)
    res = {"shells": n, "floating": len(floating), "floating_names": [labels[k][1] for k in floating],
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "unchained": len(unch), "unchained_names": unch, "unchained_chain_tol": len(chained(chain_tol)),
           "on_ground": on_ground, "sink": round(z0 + (o[OFF][2] if OFF in o else 0.0), 3),
           "kinds": {k: [lb[0] for lb in labels].count(k) for k in sorted({lb[0] for lb in labels})},
           "seats": seats}
    bm.free()
    return res


def _solid(groups, k):
    vs = list({v for f in groups[k] for v in f.verts})
    vi = {v: i for i, v in enumerate(vs)}
    return [v.co.copy() for v in vs], [[vi[v] for v in f.verts] for f in groups[k]]


def bury_report(o):
    """STAGES "nothing buried", by ray parity (m047._Solids) after the final placement:
    - petals: depth inside their bead / cup outside the seat (points further than 0.22 from the head axis must be
      clear); the seat depth (points under the bead) is reported apart;
    - leaves: depth inside the hub outside their base (points further than 0.24 from the hub axis), depth inside any
      stem outside the leaf junction (spec: a leaf cuts a stem by at most 0.03; inside JUNCTION_R / JUNCTION_Z, where
      petioles and stem feet crowd out of the hub with butt joins, the depth is reported as "junction"), and the
      share of their verts outside the hub region inside another leaf (spec: at most 25 %);
    - stems: seat depth in the hub (spec 0.06-0.08) and top depth in the cup;
    - beads: depth inside their cup (spec: the lower 35-45 % sunk, <= 0.12)."""
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
    res = {"petals": {}, "leaves": {}, "stems": {}, "beads": {}}
    over = []
    for hn in HEADS:
        if f"{hn}_cup" not in by:
            continue
        C, e1, e2, nrm = _hframe(hn)
        for k in range(5):
            nm = f"{hn}_p{k}"
            if nm not in by:
                continue
            seat, beyond = 0.0, 0.0
            for p in pts(by[nm]):
                pw = p + off
                rad = ((pw - C) - nrm * (pw - C).dot(nrm)).length
                d = max(sol[f"{hn}_bead"].point(p)[0], sol[f"{hn}_cup"].point(p)[0])
                if rad > 0.22:
                    beyond = max(beyond, d)
                else:
                    seat = max(seat, d)
            res["petals"][nm] = (round(seat, 3), round(beyond, 3))
            if beyond > BURY:
                over.append((nm, round(beyond, 3)))
        st = f"{hn}_stem"
        if st in by:
            P = _stem_path(hn)
            dh = sol.get("hub").point(P[0] - off)[0] if "hub" in sol else None
            dc = sol[f"{hn}_cup"].point(P[-1] - off)[0]
            res["stems"][st] = {"foot_in_hub": round(dh, 3) if dh is not None else None, "top_in_cup": round(dc, 3)}
        bd = f"{hn}_bead"
        res["beads"][bd] = round(max(sol[f"{hn}_cup"].point(p)[0] for p in pts(by[bd])), 3)
        if res["beads"][bd] > 0.12:
            over.append((bd, res["beads"][bd]))
    leaves = [k for k in range(n) if labels[k][0] in ("leaf", "rim")]
    stems = [labels[k][1] for k in range(n) if labels[k][0] == "stem"]
    for k in leaves:
        nm = labels[k][1]
        P = pts(k)
        hub_d = 0.0
        stem_d = 0.0
        junc_d = 0.0
        for p in P:
            pw = p + off
            if "hub" in sol and math.hypot(pw.x, pw.y) > 0.24:
                hub_d = max(hub_d, sol["hub"].point(p)[0])
            if pw.z > HUB_TOP + 0.02:
                for s in stems:
                    d = sol[s].point(p)[0]
                    if math.hypot(pw.x, pw.y) > JUNCTION_R or pw.z > JUNCTION_Z:
                        stem_d = max(stem_d, d)
                    else:
                        junc_d = max(junc_d, d)
        vs = [v for v in {v for f in groups[k] for v in f.verts}
              if math.hypot((v.co + off).x, (v.co + off).y) > 0.24]          # the bases crowd in the hub by design
        share = 0.0
        for j in leaves:
            if j == k:
                continue
            inside = sum(1 for v in vs if sol[labels[j][1]].point(v.co)[0] > 0)
            share = max(share, inside / max(1, len(vs)))
        res["leaves"][nm] = {"hub": round(hub_d, 3), "stem_cut": round(stem_d, 3), "junction": round(junc_d, 3),
                             "max_inside_leaf": round(share, 2)}
        if hub_d > BURY or share > 0.25:
            over.append((nm, round(hub_d, 3), round(share, 2)))
    bm.free()
    res["over"] = over
    return res


JUNCTION_R, JUNCTION_Z = 0.30, 0.50          # the leaf junction (close-up 2): petioles and stem feet crowd together here

# ---- build ---------------------------------------------------------------------------------------------------------------
PARTS = ((PETAL_P, petal_part), (CENTER_P, center_part), (STEM_P, stem_part), (LEAF_P, leaf_part), (BASE_P, base_part))
TARGET_SIZE = ((2.55, 0.15), (2.1, 0.15), (2.2, 0.08))   # hero W (X), D (Y), H (Z) +- tolerance (decision 1)
HERO_BUDGET = 1400


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m061_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", HERO))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


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
        if n_ == HERO and c["sink"] < -0.031:
            problems.append(f"{n_}: sinks {c['sink']} below the ground (decision 10: at most 0.03)")
    bury = {h.name: bury_report(h)}
    for n_, b in bury.items():
        if b["over"]:
            problems.append(f"{n_}: buried pieces {b['over']}")
        for st, d in b["stems"].items():
            if d["foot_in_hub"] is not None and not (0.05 <= d["foot_in_hub"] <= 0.085):
                problems.append(f"{n_}: {st} foot {d['foot_in_hub']} inside the hub (0.06-0.08 wanted)")
            if not (0.04 <= d["top_in_cup"] <= 0.085):
                problems.append(f"{n_}: {st} top {d['top_in_cup']} inside its cup (0.05-0.08 wanted)")
        for lf, d in b["leaves"].items():
            if d["stem_cut"] > 0.03:
                problems.append(f"{n_}: leaf {lf} cuts a stem by {d['stem_cut']} (<= 0.03)")
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
    kinds = {}
    for s in shells[HERO]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts", "origin_offset", "transforms_applied")} for au in audits],
           "hero_shells": kinds, "contact": contact, "bury": bury, "winding": winding, "bowties": bowties,
           "leaves": leaves, "heads": heads, "thin": thin, "log": log, "problems": problems, "uv": uv,
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders -------------------------------------------------------------------------------------------------------------
# decision 9: front_sheet (0, 5) governs positions, f34_sheet the read (probed: spec 3.2); floor hidden, 3x lens
SHEET_VIEWS = {"f34_sheet": (-10, 12), "r34_sheet": (170, 12), "front_sheet": (0, 5), "side_sheet": (90, 5),
               "side270_sheet": (270, 5), "rear_sheet": (180, 5), "top_sheet": (0, 85)}
VIEW_NAMES = ("front", "side", "rear", "top", "underside")
PARTS_SHOT = (0, 15)
PART_SHOTS = {PETAL_P: (-20, 35), CENTER_P: (0, 20), LEAF_P: (-30, 20), BASE_P: (0, 15)}
SPIN = tuple(range(0, 360, 45))
SPIN_EL = 10


def _exploded(objs):
    """A temp build with the pieces drawn apart: heads lifted along their normals (petals spread out, the bead over
    them, the cup under), the stems lifted 0.3, the ring and rim leaves pulled 0.35 out along their azimuths."""
    EXPLODE["on"] = True
    try:
        o = _new(PFX + "exploded", hero_all, "part", 1000, temp=True)
    finally:
        EXPLODE["on"] = False
    o.location = (objs[0].location.x + 30, objs[0].location.y, 0)
    bpy.context.view_layer.update()
    return [o]


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
    markers = [_scale_marker(h, (2.4, 0.0, 0.0)), _scale_marker(h, (-2.4, 0.0, 0.0), "char2")]
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        extra["front34"] = ([h], -10, 12)
        extra["rear34"] = ([h], 170, 12)
        for o in objs[1:]:
            extra["part_" + o.name.replace(HERO, "").lower()] = ([o], *PART_SHOTS.get(o.name, PARTS_SHOT))
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
        for o in shown + markers:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
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
    out = f"{d}/spin.png"
    kit["save_px"](kit["vstack"](rows), out)
    return out


def render_close_ups(objs):
    """head_cu (H_M from the front and above: five petals, the bead), head_edge (H_M edge-on in its own plane: petal
    and bead thickness), petal_edge (the Petal part edge-on), head_under (H_M from below: the cup and the stem entering
    it, close-up 1), rosette_cu (the rosette from above-front), junction_cu (the leaf bases at the hub, close-up 2),
    base_under (the LeafBase part from below: the octagonal collar, close-up 3), edge_side (the hero side-on at eye
    level: every leaf's thickness), thumb (the front at about 120 px)."""
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    by = {o.name: o for o in objs}
    h = objs[0]
    out = {}

    def at(o, p):
        return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)
    rc = m033.render_close
    C, e1, e2, n = _hframe("H_M")
    out["head_cu"] = rc([h], f"{d}/head_cu.png", -10, 30, at(h, C + n * 0.05), 0.85)
    az_edge = math.degrees(math.atan2(n.x, -n.y)) + 90.0      # camera in the head plane: H_M edge-on
    out["head_edge"] = rc([h], f"{d}/head_edge.png", az_edge, 0, at(h, C), 0.62)
    if PETAL_P in by:
        p = by[PETAL_P]
        out["petal_edge"] = rc([p], f"{d}/petal_edge.png", 0, 0, at(p, (0.3, 0.0, 0.05)), 0.32)
    out["head_under"] = rc([h], f"{d}/head_under.png", 20, -30, at(h, C - n * 0.12), 0.75)
    out["rosette_cu"] = rc([h], f"{d}/rosette_cu.png", -15, 40, at(h, (0.0, -0.05, 0.45)), 1.25)
    out["junction_cu"] = rc([h], f"{d}/junction_cu.png", -5, 12, at(h, (0.0, -0.2, 0.35)), 0.55)
    if BASE_P in by:
        b = by[BASE_P]
        out["base_under"] = rc([b], f"{d}/base_under.png", 0, -60, at(b, (0, 0, 0.1)), 0.45)
    out["edge_side"] = rc([h], f"{d}/edge_side.png", 90, 0, at(h, (0.0, 0.0, 1.1)), 1.25)
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
            "leaves": dict(LEAF_INFO), "heads": dict(HEAD_INFO), "offset": [round(x, 3) for x in h[OFF]]}
