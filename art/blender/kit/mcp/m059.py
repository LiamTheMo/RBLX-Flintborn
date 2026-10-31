"""059 Grass Tuft (references/059.png): a broad-leaf grass clump. Six broad, thick, ridged lanceolate blades (one
tallest leaning right-back, two tall, a narrow dark back blade, two long low side blades) fan out of a brown cross +
post root base (hidden in the assembled views); three chunky gem-like base leaves and two tiny sprouts sit at the foot
with two warm-grey faceted rocks and two tan pebbles. No glow, no VFX.

    import importlib, kit_models, m059; importlib.reload(kit_models); importlib.reload(m059); m059.build()

Build frame: studs, front -Y, +X right, ground z 0, the root base's post on (0, 0). Every object ends with its origin
at its bbox bottom centre; o["m059_offset"] is that origin in the build frame. W07 owns every GrassTuft* name, so the
names are BroadGrassClump* (spec 8, decision 2):
- BroadGrassClump (hero): root base + six blades + three base leaves + two sprouts + Rocks A, B and pebbles C, C2, one
  object of separate closed shells (no booleans). Collision none (walk-through ground cover).
- BroadGrassClumpBladeCenter / LeftTall / RightTall / LeftShort / RightShort: blades B1-B5 alone, as they sit in the
  hero. BroadGrassClumpRootBase: post + four arms, joining faces bare. BroadGrassClumpRockLarge / RockMedium /
  RockSmall: Rocks A, B, C.
Colour (stage 4) is painted by blade role and position along each blade (station bands), rocks by height, inside the
builders (never by facing). Stages 5-6: none (the sheet shows no glow, light or effect). See M059_spec.md.
"""
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

NUM, TITLE, SHEET = 59, "Grass Tuft", "M059"
OFF = "m059_offset"
PFX = "_m059_"
HERO = "BroadGrassClump"
B1_P, B2_P, B3_P, B4_P, B5_P = ("BroadGrassClumpBladeCenter", "BroadGrassClumpBladeLeftTall",
                                "BroadGrassClumpBladeRightTall", "BroadGrassClumpBladeLeftShort",
                                "BroadGrassClumpBladeRightShort")
ROOT_P = "BroadGrassClumpRootBase"
ROCKA_P, ROCKB_P, ROCKC_P = "BroadGrassClumpRockLarge", "BroadGrassClumpRockMedium", "BroadGrassClumpRockSmall"

LIGHT, MID, DARK, DEEP = "m059_grass_light", "m059_grass_mid", "m059_grass_dark", "m059_grass_deep"
ROOT, ROOT_LIGHT = "m059_root", "m059_root_light"
PEBBLE = "m059_pebble"
ROCK, ROCK_LIGHT, ROCK_DEEP = "m059_rock", "m059_rock_light", "m059_rock_deep"
LADDER = (DEEP, DARK, MID, LIGHT)            # tone value 0..3 along a blade

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
BURY = 0.05
BURY_PLACE = 0.03
SINK = 0.02                                  # everything on the ground sinks this far (decision 10: at most 0.03)

# key -> (hex, roughness, low specular). Stage 4 writes the calibrated values here (spec "Stage 4").
PALETTE = {
    LIGHT: ("#80AD2A", 0.8, True),
    MID: ("#5D8F1C", 0.85, True),
    DARK: ("#325F19", 0.85, True),
    DEEP: ("#294F18", 0.9, True),
    ROOT: ("#7D5835", 0.9, False),
    ROOT_LIGHT: ("#A67B58", 0.85, False),
    PEBBLE: ("#8E7050", 0.9, False),
    ROCK: ("#99908D", 0.85, False),
    ROCK_LIGHT: ("#A69D9A", 0.85, False),
    ROCK_DEEP: ("#746C68", 0.9, False),
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions), K.sample kinds
TARGETS = {LIGHT: ((0xA1, 0xD1, 0x2B), "vivid"), MID: ((0x60, 0x96, 0x19), "green"),
           DARK: ((0x38, 0x6C, 0x19), "green"), DEEP: ((0x2E, 0x5A, 0x18), "green"),
           ROOT: ((0x9E, 0x6B, 0x40), "brown"), ROOT_LIGHT: ((0xCE, 0x97, 0x66), "brown"),
           PEBBLE: ((0xA0, 0x78, 0x50), "brown"), ROCK: ((0xAB, 0xA1, 0x96), "stone"),
           ROCK_LIGHT: ((0xC8, 0xBB, 0xB3), "stone"), ROCK_DEEP: ((0x8E, 0x85, 0x7C), "stone")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m059_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k == "m059_" + tail), None) or \
                next((k for k in PALETTE if k.startswith(k1) and k.endswith("_" + tail)), None)
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
_mottle = m033._mottle


def _mix(k1, k2, t):
    t = round(max(0.0, min(1.0, t)) * 4) / 4
    return K.mix_key(k1, k2, t)


def _tone(v):
    """Tone value on LADDER (0 deep, 1 dark, 2 mid, 3 light; fractions mix the neighbours in 25 % steps)."""
    v = max(0.0, min(3.0, v))
    i = min(2, int(v))
    return _mix(LADDER[i], LADDER[i + 1], v - i)


def _ramp(pts, s):
    """Piecewise-linear value of [(s, v), ...] at s."""
    if s <= pts[0][0]:
        return pts[0][1]
    for (s0, v0), (s1, v1) in zip(pts, pts[1:]):
        if s <= s1:
            return v0 + (v1 - v0) * (s - s0) / max(1e-9, s1 - s0)
    return pts[-1][1]


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


def _u(az):
    r = math.radians(az)
    return Vector((math.cos(r), math.sin(r), 0.0))


def _upside(u):
    """Unit normal to u in the vertical plane through u, on the upper side (world Z with u removed)."""
    z = Vector((0, 0, 1))
    n = z - u * z.dot(u)
    return n.normalized() if n.length > 1e-6 else Vector((1, 0, 0))


def _close(a, vs, fs, key, tint=1.0):
    bmesh.ops.recalc_face_normals(a.bm, faces=fs)
    a._finish(vs, key, tint=tint)


# ---- explode state (the exploded shot is a temp build with pieces drawn apart) ----------------------------------------
EXPLODE = {"on": False}


def _shift(vec):
    return Vector(vec) if EXPLODE["on"] else Vector()


# ---- root base (spec 2.2: post + four arms, closed shells, no booleans) -------------------------------------------------
POST_R = 0.18 / math.cos(math.pi / 8)       # 8-sided, 0.36 across the flats (flats face +X / +Y / ...)
POST_TOP, POST_CHAMFER = 0.36, 0.045
ARM_R = 0.08 / math.cos(math.pi / 6)        # 6-sided, 0.16 across the flats (spec 0.22: thinner, so the blade bases hide the arm ends)
ARM_IN, ARM_OUT, ARM_Z, ARM_RISE = 0.05, 0.34, 0.07, 10.0
ARMS = {"A166": 166.0, "A346": 346.0, "A76": 76.0, "A256": 256.0}   # each arm points at its blade (B4, B5, B6, B2)
JOIN = {}                                   # joining face name -> (centre, outward normal) in the build frame


def _arm_axis(az):
    t = math.tan(math.radians(ARM_RISE))
    d = _u(az) + Vector((0, 0, t))
    p0 = _u(az) * ARM_IN + Vector((0, 0, ARM_Z + ARM_IN * t))
    p1 = _u(az) * ARM_OUT + Vector((0, 0, ARM_Z + ARM_OUT * t))
    return p0, p1, d.normalized()


def _joins():
    JOIN.clear()
    JOIN["post_top"] = (Vector((0.0, 0.0, POST_TOP)), Vector((0, 0, 1)))
    JOIN["post_x"] = (Vector((0.18, 0.0, 0.17)), Vector((1, 0, 0)))
    for k, az in ARMS.items():
        p0, p1, d = _arm_axis(az)
        JOIN[k] = (p1, d)


def post(a):
    bm = a.bm
    rings = []
    for z, r in ((-SINK - 0.005, POST_R), (POST_TOP - POST_CHAMFER, POST_R), (POST_TOP, POST_R - POST_CHAMFER)):
        rings.append([bm.verts.new((math.cos(math.pi / 8 + k * math.pi / 4) * r,
                                    math.sin(math.pi / 8 + k * math.pi / 4) * r, z)) for k in range(8)])
    side = m047._band(bm, rings[0], rings[1])
    cham = m047._band(bm, rings[1], rings[2])
    bot = bm.faces.new(list(reversed(rings[0])))
    top = bm.faces.new(rings[2])
    vs = [v for r in rings for v in r]
    _close(a, vs, side + cham + [bot, top], ROOT)
    _paint(a, cham + [top], ROOT_LIGHT)
    # the +X flat carries B3's base: its upper half takes the joining colour (spec 5.3)
    for f in side:
        c = f.calc_center_median()
        if c.x > 0.15 and abs(c.y) < 0.05:
            _paint(a, [f], _mix(ROOT, ROOT_LIGHT, 0.5))
    return vs


def arm(a, name):
    az = ARMS[name]
    p0, p1, d = _arm_axis(az)
    u = _u(az + 90.0)
    v = d.cross(u).normalized()
    bm = a.bm
    r0 = [bm.verts.new(p0 + (u * math.cos(k * math.pi / 3) + v * math.sin(k * math.pi / 3)) * ARM_R) for k in range(6)]
    r1 = [bm.verts.new(p1 + (u * math.cos(k * math.pi / 3) + v * math.sin(k * math.pi / 3)) * ARM_R) for k in range(6)]
    side = m047._band(bm, r0, r1)
    inner = bm.faces.new(list(reversed(r0)))
    end = bm.faces.new(r1)
    vs = r0 + r1
    _close(a, vs, side + [inner, end], ROOT)
    _paint(a, [end], ROOT_LIGHT)
    return vs


def root_base(a, guard=None):
    _joins()
    out = {"post": post(a)}
    for k in ARMS:
        out[k] = arm(a, k)
    rng = random.Random(59101)
    for k, vs in out.items():
        _tint(a, _faces(vs), 1.0 + rng.uniform(-0.03, 0.03))
        if guard is not None:
            guard.add_vs(vs, "root_" + k)
    return out


# ---- blades (spec 2.3: closed 6-vert ridged lanceolates, flat base face on a joining face) -----------------------------
ST = (0.0, 0.18, 0.40, 0.62, 0.82)          # section stations (fraction of L); the tip point at 1.0
FOLD, THICK = 0.45, 0.12
SEAT = {"post": 0.045, "A166": 0.03, "A346": 0.03, "A76": 0.03, "A256": 0.03}   # base face this far inside its joining face
EXPL_BLADE = 0.9
# name -> joining face, tip, W, half-width per station (fraction of W/2), bends (deg, at 0.40-0.62 and 0.82; + = out
# and down), roll (0 = the natural face, up and in toward the centre, which reads in the top view and on diagonal
# blades; 1 = turned square to the front camera, for the blades leaning sideways), tone ramp [(s, tone)]
BLADES = {
    "B1": dict(join="post_top", tip=(0.85, 0.62, 2.40), W=0.72, hw=(0.62, 0.86, 1.0, 0.88, 0.56), bend=(5.0, 5.0),
               roll=0.35, tone=[(0.0, 2.0), (0.12, 2.0), (0.35, 3.0), (1.0, 3.0)], part=B1_P),
    "B2": dict(join="A256", tip=(-0.82, -1.34, 1.98), W=0.64, hw=(0.62, 0.88, 1.0, 0.90, 0.55), bend=(7.0, 8.0),
               roll=0.0, tone=[(0.0, 1.5), (0.15, 2.0), (0.4, 2.25), (0.6, 2.75), (1.0, 2.75)], part=B2_P),
    "B6": dict(join="A76", tip=(-0.40, 1.34, 2.14), W=0.55, hw=(0.68, 0.95, 1.0, 0.92, 0.60), bend=(5.0, 5.0),
               roll=0.0, tone=[(0.0, 0.75), (0.25, 1.0), (0.8, 1.25), (1.0, 1.75)]),
    "B3": dict(join="post_x", tip=(1.39, 0.15, 1.61), W=0.66, hw=(0.62, 0.84, 1.0, 0.86, 0.50), bend=(9.0, 10.0),
               roll=0.7, tone=[(0.0, 1.0), (0.5, 1.25), (1.0, 1.75)], part=B3_P),
    "B4": dict(join="A166", tip=(-1.45, 0.72, 1.44), W=0.68, hw=(0.50, 0.78, 1.0, 0.84, 0.48), bend=(10.0, 12.0),
               roll=0.7, tone=[(0.0, 0.75), (0.25, 1.0), (1.0, 1.5)], part=B4_P),
    "B5": dict(join="A346", tip=(1.52, -0.85, 0.94), W=0.62, hw=(0.60, 0.88, 1.0, 0.82, 0.47), bend=(8.0, -4.0),
               roll=0.5, tone=[(0.0, 2.25), (0.3, 3.0), (1.0, 3.0)], part=B5_P),
}
FRONT = Vector((0.0, -1.0, 0.15)).normalized()
BLADE_INFO = {}


def _blade_frame(name):
    """Station centres and tangents (build frame) of a blade: a polyline from the root to the tip with the bends,
    fitted so its end lands exactly on the tip."""
    s = BLADES[name]
    c, nrm = JOIN[s["join"]]
    root = c - nrm * SEAT[s["join"][:4]]
    tip = Vector(s["tip"])
    ch = tip - root
    L = ch.length
    u = ch.normalized()
    n = _upside(u)
    b1, b2 = (math.radians(x) for x in s["bend"])
    turn = {2: b1 / 2, 3: b1 / 2, 4: b2}
    stn = list(ST) + [1.0]
    phi, pts = 0.0, [(0.0, 0.0)]
    dirs = []
    for k in range(len(stn) - 1):
        phi -= turn.get(k, 0.0)
        ds = stn[k + 1] - stn[k]
        dirs.append(phi)
        x, y = pts[-1]
        pts.append((x + ds * math.cos(phi), y + ds * math.sin(phi)))
    ex, ey = pts[-1]
    rot = -math.atan2(ey, ex)
    sc = L / math.hypot(ex, ey)

    def w(x, y):
        return root + (u * (x * math.cos(rot) - y * math.sin(rot)) + n * (x * math.sin(rot) + y * math.cos(rot))) * sc
    P = [w(x, y) for x, y in pts]
    seg = [(P[k + 1] - P[k]).normalized() for k in range(len(P) - 1)]
    T = [seg[0]] + [(seg[k - 1] + seg[k]).normalized() for k in range(1, len(seg))]
    return root, tip, L, P, T, u


def blade(a, name, guard=None):
    """One blade: five 6-vert folded-plate sections (left edge front, front ridge, right edge front, right edge back,
    back ridge, left edge back) along the bent axis, a flat hexagonal base face and a tip point; 58 tris. Each station band takes one tone
    by the blade's role and its position along the blade (spec 5.3), never by facing."""
    s = BLADES[name]
    root, tip, L, P, T, u = _blade_frame(name)
    nat = _upside(u)
    F = (nat * (1.0 - s["roll"]) + FRONT * s["roll"]).normalized()
    W = s["W"]
    sh = _shift(u * EXPL_BLADE)
    bm = a.bm
    rings, frames = [], []
    nrm = JOIN[s["join"]][1]
    for k, (p, t) in enumerate(zip(P[:-1], T)):
        if k == 0:                  # the base face leans half-way to its joining face, so it covers the arm end / post top
            t = (t + nrm).normalized()
        f = F - t * F.dot(t)
        f.normalize()
        wv = t.cross(f).normalized()
        hw = s["hw"][k] * W / 2
        # a folded plate of even thickness (close-up 2): two broad front planes meet at the midrib, which rises FOLD x hw
        # over the edges, so one plane catches the light and one falls in shade; the back follows the fold THICK x W
        # behind it (a V groove), and each edge is a narrow band THICK x W wide (the "consistent thickness" band). The
        # base station is a thick convex sheath that covers the arm end.
        e = THICK * W / 2
        if k == 0:
            rf, rb, e = 0.19 * W, -0.12 * W, 0.07 * W
        else:
            rf = FOLD * hw + 0.01
            rb = rf - THICK * W
        pts = [p - wv * hw + f * e, p + f * rf, p + wv * hw + f * e, p + wv * hw - f * e, p + f * rb,
               p - wv * hw - f * e]
        rings.append([bm.verts.new(q + sh) for q in pts])
        frames.append((f, wv, hw, rf))
    apex = bm.verts.new(P[-1] + sh)
    bands = [m047._band(bm, rings[k], rings[k + 1]) for k in range(len(rings) - 1)]
    tipf = [bm.faces.new((rings[-1][i], rings[-1][(i + 1) % 6], apex)) for i in range(6)]
    cap = bm.faces.new(list(reversed(rings[0])))
    vs = [v for r in rings for v in r] + [apex]
    allf = [f for b in bands for f in b] + tipf + [cap]
    rng = random.Random(sum(map(ord, name)) * 7 + 59)
    _close(a, vs, allf, LIGHT, tint=1.0 + rng.uniform(-0.04, 0.04))
    # tones per station band (band k spans ST[k] .. ST[k+1]; the tip fan the last band)
    stn = list(ST) + [1.0]
    groups = bands + [tipf]
    for k, fs in enumerate(groups):
        sm = (stn[k] + stn[k + 1]) / 2
        key = _tone(_ramp(s["tone"], sm))
        _paint(a, fs + ([cap] if k == 0 else []), key)
        _tint(a, fs + ([cap] if k == 0 else []), 1.0 + rng.uniform(-0.02, 0.02))
    BLADE_INFO[name] = {"root": [round(x, 3) for x in root], "tip": [round(x, 3) for x in tip], "L": round(L, 3),
                        "W": W, "LW": round(L / W, 2), "join": s["join"],
                        "fold_depth": round(max(fr[3] + 0.0 for fr in frames[1:]), 3), "thick": round(THICK * W, 3),
                        "lean_deg": round(math.degrees(u.angle(Vector((0, 0, 1)))), 1),
                        "az_deg": round(math.degrees(math.atan2(u.y, u.x)) % 360, 1),
                        "w_mid": list(frames[2][1]), "f_mid": list(frames[2][0]),
                        "low_z_past_015L": round(min(v.co.z for r in rings[1:] for v in r), 3)}
    return vs


# ---- base leaves and sprouts (spec 2.4) ---------------------------------------------------------------------------------
# name -> root, tip, W, thickness, tone ramp, tint seed
LEAVES = {
    "N1": dict(root=(-0.62, 0.22), tip=(-1.50, 0.28, 0.48), W=0.60, T=0.27, tone=[(0.0, 2.0), (0.5, 2.5), (1.0, 3.0)],
               lift=(0.0, 0.0, 0.7)),
    "N2": dict(root=(0.04, -0.66), tip=(0.08, -0.94, 0.42), W=0.50, T=0.30, tone=[(0.0, 2.0), (0.4, 3.0), (1.0, 3.0)],
               lift=(0.0, -0.3, 0.6)),
    "N3": dict(root=(1.00, 0.80), tip=(1.58, 0.92, 0.45), W=0.52, T=0.24, tone=[(0.0, 1.0), (0.4, 2.0), (1.0, 2.0)],
               lift=(0.0, 0.0, 0.7)),
}
SPROUTS = {"S1": dict(at=(-0.45, -0.55), H=0.18, W=0.16, tone=2.0, yaw=20.0),
           "S2": dict(at=(0.40, -0.98), H=0.15, W=0.14, tone=3.0, yaw=-30.0)}
LEAF_INFO = {}


def _gem(a, root, tip, W, T, ramp, seed, sh=Vector()):
    """A chunky leaf gem: a 5-sided section (flat underside, two flanks, a top ridge) at three stations (0, 0.4,
    0.75 L) and a tip point; the underside starts on the ground at the root. 28 tris."""
    root, tip = Vector(root), Vector(tip)
    u = (tip - root).normalized()
    L = (tip - root).length
    n = _upside(u)
    wv = u.cross(n).normalized()
    bm = a.bm
    rings = []
    for s_, wf, tf in ((0.0, 0.62, 0.75), (0.4, 1.0, 1.0), (0.75, 0.58, 0.8)):
        p = root + u * (s_ * L)
        hw, t = wf * W / 2, tf * T
        pts = [p - wv * 0.8 * hw, p - wv * hw + n * 0.45 * t, p + n * t, p + wv * hw + n * 0.45 * t, p + wv * 0.8 * hw]
        rings.append([bm.verts.new(q + sh) for q in pts])
    apex = bm.verts.new(tip + n * 0.15 * T + sh)
    bands = [m047._band(bm, rings[k], rings[k + 1]) for k in range(2)]
    tipf = [bm.faces.new((rings[-1][i], rings[-1][(i + 1) % 5], apex)) for i in range(5)]
    cap = bm.faces.new(list(reversed(rings[0])))
    vs = [v for r in rings for v in r] + [apex]
    rng = random.Random(seed)
    _close(a, vs, bands[0] + bands[1] + tipf + [cap], MID, tint=1.0 + rng.uniform(-0.04, 0.04))
    for k, (fs, sm) in enumerate(((bands[0] + [cap], 0.2), (bands[1], 0.57), (tipf, 0.88))):
        _paint(a, fs, _tone(_ramp(ramp, sm)))
        _tint(a, fs, 1.0 + rng.uniform(-0.02, 0.02))
    return vs


def leaf(a, name, guard=None):
    s = LEAVES[name]
    rx, ry = s["root"]
    tip = Vector(s["tip"])
    info = {"moved": 0.0}
    for attempt in range(8):
        shift = Vector((rx, ry, 0)).normalized() * (0.04 * attempt) if attempt else Vector()
        root = Vector((rx, ry, -SINK)) + shift
        vs = _gem(a, root, tip + shift, s["W"], s["T"], s["tone"], 59300 + sum(map(ord, name)), _shift(s["lift"]))
        d = guard.depth(vs) if guard is not None and not EXPLODE["on"] else 0.0
        if d <= BURY_PLACE or attempt == 7:
            info.update(moved=round(shift.length, 3), depth=round(d, 3))
            break
        bmesh.ops.delete(a.bm, geom=vs, context="VERTS")
    LEAF_INFO[name] = info
    return vs


def sprout(a, name, guard=None):
    """A tiny two-stage spear (a flattened 4-sided section at the ground and at 0.45 H, then a point): 14 tris."""
    s = SPROUTS[name]
    info = {}
    for attempt in range(8):
        x, y = s["at"]
        sh = Vector((x, y, 0)).normalized() * (0.03 * attempt) if attempt else Vector()
        c = Vector((x, y, -SINK)) + sh
        yaw = math.radians(s["yaw"])
        ex, ey = Vector((math.cos(yaw), math.sin(yaw), 0)), Vector((-math.sin(yaw), math.cos(yaw), 0))
        bm = a.bm
        rings = []
        for z, f in ((0.0, 1.0), (0.45 * s["H"], 0.7)):
            hw = s["W"] / 2 * f
            rings.append([bm.verts.new(c + Vector((0, 0, z)) + q) for q in
                          (ex * hw, ey * hw * 0.5, -ex * hw, -ey * hw * 0.5)])
        apex = bm.verts.new(c + Vector((0.02, 0.01, s["H"] + SINK)))
        fs = m047._band(bm, rings[0], rings[1]) + [bm.faces.new((rings[1][i], rings[1][(i + 1) % 4], apex))
                                                    for i in range(4)] + [bm.faces.new(list(reversed(rings[0])))]
        vs = rings[0] + rings[1] + [apex]
        _close(a, vs, fs, _tone(s["tone"]), tint=1.0)
        d = guard.depth(vs) if guard is not None and not EXPLODE["on"] else 0.0
        if d <= BURY_PLACE or attempt == 7:
            info = {"moved": round(sh.length, 3), "depth": round(d, 3)}
            break
        bmesh.ops.delete(a.bm, geom=vs, context="VERTS")
    LEAF_INFO[name] = info
    return vs


# ---- rocks and pebbles (spec 2.5) --------------------------------------------------------------------------------------
# name -> centre, (W, D, H), yaw, rings, seed, kind
ROCK_RINGS = ((0.0, 0.92, 6), (0.35, 1.0, 6), (0.75, 0.75, 5), (1.0, 0.40, 4))
PEB_RINGS = ((0.0, 0.92, 5), (0.5, 1.0, 5), (1.0, 0.45, 3))
ROCKS = {
    "A": dict(c=(-0.95, -0.45), size=(0.85, 0.65, 0.40), yaw=20.0, rings=ROCK_RINGS, seed=59501, kind="rock",
              expl=(-0.35, -0.2, 0.0)),
    "B": dict(c=(0.85, 0.35), size=(0.65, 0.50, 0.32), yaw=-35.0, rings=ROCK_RINGS, seed=59502, kind="rock",
              expl=(0.35, 0.0, 0.0)),
    "C": dict(c=(-0.50, -0.80), size=(0.36, 0.30, 0.17), yaw=10.0, rings=PEB_RINGS, seed=59503, kind="pebble",
              expl=(0.0, -0.3, 0.0)),
    "C2": dict(c=(0.62, -0.75), size=(0.25, 0.22, 0.14), yaw=50.0, rings=PEB_RINGS, seed=59504, kind="pebble",
               expl=(0.1, -0.3, 0.0)),
}


def rock(a, name, guard=None):
    """An angular faceted block: the hull of jittered ring stacks (flat base sunk SINK, widest at 0.35 h, a shoulder,
    a sloping top). Grey rocks: rock with broad rock_light / rock_deep patches blended in by position; pebbles: tan
    with warm brown patches."""
    s = ROCKS[name]
    rng = random.Random(s["seed"])
    W, D, H = s["size"]
    pts = m033._ring_pts(rng, s["rings"], W / 2, D / 2, H, 0.08, lean=(rng.uniform(-0.12, 0.12), rng.uniform(-0.1, 0.1)))
    for p in pts:                    # a sloping top: higher toward the upper right, as the sheet's lit tops
        p.z += 0.10 * p.x * (p.z / H)
    m = Matrix.Rotation(math.radians(s["yaw"]), 3, "Z")
    z0 = -SINK
    pts = [m @ p + Vector((s["c"][0], s["c"][1], z0)) + _shift(s["expl"]) for p in pts]
    base = ROCK if s["kind"] == "rock" else PEBBLE
    vs = m033._hull(a, pts, base)
    fs = _faces(vs)
    # broad stone variation by position (noise patches a few facets across), never by height or facing: on a squat
    # block the top faces are the up-facing ones, so height bands would paint the lighting in (K.check corr 0.92)
    fld = K.noise_field(scale=2.2, seed=s["seed"])
    for f in fs:
        v = fld(f.calc_center_median())
        if s["kind"] == "rock":
            key = (ROCK_LIGHT if v > 0.30 else _mix(ROCK, ROCK_LIGHT, 0.5) if v > 0.10 else
                   ROCK_DEEP if v < -0.32 else _mix(ROCK, ROCK_DEEP, 0.5) if v < -0.12 else ROCK)
        else:
            key = _mix(PEBBLE, ROOT, 0.5) if v < -0.3 else PEBBLE
        _paint(a, [f], key)
    for f in fs:                     # per-facet Tint (0.04 rocks, 0.03 pebbles), broad, not per triangle
        k = 1.0 + rng.uniform(-1, 1) * (0.04 if s["kind"] == "rock" else 0.03)
        _tint(a, [f], k)
    if guard is not None:
        guard.add_vs(vs, "rock_" + name)
    return vs


# ---- assemblies ----------------------------------------------------------------------------------------------------------
def _guard():
    return m047._Solids()


def hero_all(a):
    BLADE_INFO.clear()
    LEAF_INFO.clear()
    g = _guard()
    root_base(a, g)
    for k in ROCKS:
        rock(a, k, g)
    blade_vs = {}
    for k in BLADES:
        blade_vs[k] = blade(a, k)
    for k in LEAVES:
        leaf(a, k, g)
    for k in SPROUTS:
        sprout(a, k, g)
    if not EXPLODE["on"]:
        _blade_checks(blade_vs, g)


def _blade_checks(blade_vs, g):
    """Per blade: the seat (base-face centre inside its joining member, depth to its surface), the deepest point in a
    rock, and the share of its verts inside another blade (spec 2.3: <= 30 %)."""
    sol = {}
    for k, vs in blade_vs.items():
        s = m047._Solids()
        s.add_vs(vs, k)
        sol[k] = s
    for k, vs in blade_vs.items():
        info = BLADE_INFO[k]
        ring0 = vs[:6]
        bc = sum((v.co for v in ring0), Vector()) / 6
        member = "root_post" if BLADES[k]["join"].startswith("post") else "root_" + BLADES[k]["join"]
        d, who = g.point(bc)
        info["seat_depth"] = round(d, 3) if who == member else (0.0 if who is None else round(-d, 3))
        info["seat_member"] = who
        info["in_rock"] = round(g.depth(vs, skip=tuple(n for n, *_ in g.items if n.startswith("root_"))), 3)
        worst = 0.0
        for j, sj in sol.items():
            if j == k:
                continue
            inside = sum(1 for v in vs if sj.point(v.co)[0] > 0)
            worst = max(worst, inside / len(vs))
        info["max_inside_other"] = round(worst, 2)


def blade_part(name):
    def fn(a):
        _joins()
        blade(a, name)
    return fn


def root_part(a):
    root_base(a)


def rock_part(name):
    def fn(a):
        rock(a, name)
    return fn


NOTES = {
    HERO: "Broad grass clump: six broad ridged lanceolate blades (1 tallest leaning right-back, 2 tall, 1 narrow dark back "
          "blade, 2 long low side blades) on a hidden cross + post root base, three chunky base leaves, two sprouts, "
          "two warm-grey rocks and two tan pebbles. Walk-through ground cover (collision none). Sheet page 61/132.",
    B1_P: "Blade 1 (Center, Tallest): ridged lanceolate solid, lime upper half over a mid-green body",
    B2_P: "Blade 2 (Left Tall): ridged lanceolate solid, dark base, mid body, lime upper part",
    B3_P: "Blade 3 (Right Tall): ridged lanceolate solid, dark with a mid tip",
    B4_P: "Blade 4 (Left Short): ridged lanceolate solid, deep base, dark body",
    B5_P: "Blade 5 (Right Short): ridged lanceolate solid, mid body, lime tip",
    ROOT_P: "Root Base (5-way join): 8-sided post with a chamfered top + four 6-sided arms, flat joining faces bare",
    ROCKA_P: "Rock A (Large): warm-grey faceted block, lighter top, deeper foot",
    ROCKB_P: "Rock B (Medium): warm-grey faceted block",
    ROCKC_P: "Rock C (Small): tan faceted pebble with a warm brown foot",
}
COLLISION = {HERO: "none", B1_P: "none", B2_P: "none", B3_P: "none", B4_P: "none", B5_P: "none", ROOT_P: "none",
             ROCKA_P: "hull", ROCKB_P: "hull", ROCKC_P: "none"}


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
def _keys(o):
    return [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]


def _kind(ks, nf):
    if any(k.startswith("m059_rock") for k in ks):
        return "rock"
    if any(k.startswith("m059_pebble") for k in ks):
        return "pebble"
    if any(k.startswith("m059_grass") for k in ks):
        return "blade" if nf >= 40 else "leaf" if nf >= 20 else "sprout"
    return "root"


def _shells(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = _keys(o)
    groups = [[] for _ in range(n)]
    for f in bm.faces:
        groups[ids[f.index]].append(f)
    kinds = [_kind({keys[f.material_index] for f in fs}, len(fs)) for fs in groups]
    return bm, ids, n, groups, kinds


def shells_report(o):
    """Per shell: kind, tris, non-manifold edges and verts, boundary edges, winding errors (manifold edges whose two
    faces don't run the same way round), self-intersecting face pairs, signed volume."""
    bm, ids, n, groups, kinds = _shells(o)
    out = []
    for k in range(n):
        fs = groups[k]
        es = {e for f in fs for e in f.edges}
        vs = list({v for f in fs for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        hits = sum(1 for a_, b_ in tree.overlap(tree) if a_ < b_ and not set(fs[a_].verts) & set(fs[b_].verts))
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) / 3.0
        out.append({"kind": kinds[k], "tris": len(fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary),
                    "winding_errors": sum(1 for e in es if e.is_manifold and not e.is_contiguous),
                    "self_hits": hits, "volume": round(vol, 5), "zmin": round(min(v.co.z for v in vs), 3)})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating pieces (STAGES): per shell, whether it touches another shell (triangles intersect, or a vertex
    within `tol` of another shell's surface) or the ground, and whether it chains by contact to the ground (blade ->
    root member -> ground; leaf, sprout, rock -> ground). A single-shell part is its own anchor."""
    bm, ids, n, groups, kinds = _shells(o)
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
    on_ground = {kinds[k]: 0 for k in range(n)}
    for k in ground:
        on_ground[kinds[k]] = on_ground.get(kinds[k], 0) + 1
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
        return n - len(seen)
    floating = [k for k in range(n) if gap[k] > tol]
    res = {"shells": n, "floating": len(floating), "floating_kinds": sorted({kinds[k] for k in floating}),
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "unchained": chained(tol), "unchained_chain_tol": chained(chain_tol),
           "on_ground": on_ground, "sink": round(z0 + (o[OFF][2] if OFF in o else 0.0), 3),
           "kinds": {k: kinds.count(k) for k in sorted(set(kinds))}}
    bm.free()
    return res


def bury_report(o):
    """STAGES "nothing buried": every leaf, sprout and pebble shell tested by ray parity against every rock and root
    shell, every blade against the rocks (blades sit in their root member by design: SEAT), every rock against the
    root base (no attachment: spec 2.5). depth = distance from its deepest vert or face centre inside to that shell's
    surface."""
    bm, ids, n, groups, kinds = _shells(o)
    rocks, root = m047._Solids(), m047._Solids()
    for k in range(n):
        if kinds[k] in ("rock", "root", "pebble"):
            vs = list({v for f in groups[k] for v in f.verts})
            vi = {v: i for i, v in enumerate(vs)}
            (root if kinds[k] == "root" else rocks).add([v.co for v in vs], [[vi[v] for v in f.verts] for f in groups[k]],
                                                        f"{kinds[k]}{k}")
    res, rk = [], []
    for k in range(n):
        fs = groups[k]
        pts = list({v.co.copy().freeze() for f in fs for v in f.verts}) + [f.calc_center_median() for f in fs]
        if kinds[k] == "root":
            continue
        if kinds[k] in ("rock", "pebble"):
            d, w = max((root.point(Vector(p)) for p in pts), key=lambda r: r[0])
            d2, w2 = max((rocks.point(Vector(p), skip=(f"{kinds[k]}{k}",)) for p in pts), key=lambda r: r[0])
            if max(d, d2) > 0:
                rk.append((round(max(d, d2), 3), kinds[k], w if d >= d2 else w2))
            continue
        d, w = max((rocks.point(Vector(p)) for p in pts), key=lambda r: r[0])
        if kinds[k] != "blade":
            d2, w2 = max((root.point(Vector(p)) for p in pts), key=lambda r: r[0])
            if d2 > d:
                d, w = d2, w2
        if d > 0:
            c = sum((f.calc_center_median() for f in fs), Vector()) / len(fs)
            res.append((round(d, 3), kinds[k], w, [round(x, 2) for x in c]))
    bm.free()
    res.sort(key=lambda r: -r[0])
    rk.sort(key=lambda r: -r[0])
    return {"dressing_shells": sum(1 for k in kinds if k in ("blade", "leaf", "sprout")),
            "over_0.05": sum(1 for r in res if r[0] > BURY), "max": res[0][0] if res else 0.0, "worst": res[:6],
            "rocks_over_0.05": sum(1 for r in rk if r[0] > BURY), "rocks": rk[:6]}


def root_clearance(o):
    """Spec 2.5 / close-up 3: every rock and pebble at least 0.05 clear of the root base (no attachment)."""
    bm, ids, n, groups, kinds = _shells(o)
    rs = [k for k in range(n) if kinds[k] == "root"]
    vs = list({v for k in rs for f in groups[k] for v in f.verts})
    vi = {v: i for i, v in enumerate(vs)}
    tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for k in rs for f in groups[k]])
    out = []
    for k in range(n):
        if kinds[k] in ("rock", "pebble"):
            d = min(tree.find_nearest(v.co)[3] for f in groups[k] for v in f.verts)
            out.append((kinds[k], round(d, 3)))
    bm.free()
    return out


# ---- build ---------------------------------------------------------------------------------------------------------------
PARTS = ((B1_P, blade_part("B1")), (B2_P, blade_part("B2")), (B3_P, blade_part("B3")), (B4_P, blade_part("B4")),
         (B5_P, blade_part("B5")), (ROOT_P, root_part), (ROCKA_P, rock_part("A")), (ROCKB_P, rock_part("B")),
         (ROCKC_P, rock_part("C")))
TARGET_SIZE = ((3.0, 0.2), (2.55, 0.2), (2.4, 0.1))      # hero W (X), D (Y), H (Z) +- tolerance (decision 1)
HERO_BUDGET = 900


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m059_")]
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
    blades = {k: dict(v) for k, v in BLADE_INFO.items()}
    leaves = {k: dict(v) for k, v in LEAF_INFO.items()}
    _cleanup_tmp()
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
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
                    problems.append(f"{o.name} shell {i} ({s['kind']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['kind']}): not closed outward (volume {s['volume']})")
    contact = {o.name: contact_report(o) for o in order}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} shells touch nothing within {CONTACT}, {c['unchained']} have no "
                            f"chain of contact to the ground")
        if c["sink"] < -0.031:
            problems.append(f"{n_}: sinks {c['sink']} below the ground (decision 10: at most 0.03)")
    bury = {h.name: bury_report(h)}
    for n_, b in bury.items():
        if b["over_0.05"]:
            problems.append(f"{n_}: {b['over_0.05']} shells more than {BURY} inside a rock or the root (worst "
                            f"{b['worst'][:3]})")
        if b["rocks_over_0.05"]:
            problems.append(f"{n_}: {b['rocks_over_0.05']} rocks more than {BURY} into the root or another rock")
    clear = root_clearance(h)
    for kind, d in clear:
        if d < 0.05:
            problems.append(f"{HERO}: a {kind} only {d} from the root base (spec 2.5: >= 0.05)")
    for k, b in blades.items():
        if not (0.025 <= b.get("seat_depth", 0) <= 0.065):
            problems.append(f"{HERO}: blade {k} seat depth {b.get('seat_depth')} in {b.get('seat_member')} "
                            f"(0.03-0.06 wanted)")
        if b.get("in_rock", 0) > 0.0:
            problems.append(f"{HERO}: blade {k} {b['in_rock']} inside a rock")
        if b.get("max_inside_other", 0) > 0.30:
            problems.append(f"{HERO}: blade {k} {b['max_inside_other']} of its verts inside another blade")
        if b["low_z_past_015L"] < 0.05:
            problems.append(f"{HERO}: blade {k} dips to z {b['low_z_past_015L']} past 0.15 L")
    for k, lf in leaves.items():
        if lf.get("depth", 0) > BURY_PLACE:
            problems.append(f"{HERO}: {k} still {lf['depth']} inside a rock / the root after its retries")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 11: none)")
    for n_, t in thin.items():
        if t["under"]:
            problems.append(f"{n_}: {t['under']} faces with a corner under 2 deg (min {t['min_deg']})")
    winding = {o.name: sum(s["winding_errors"] for s in shells[o.name]) for o in order}
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
           "hero_shells": kinds, "contact": contact, "bury": bury, "root_clearance": clear, "winding": winding,
           "blades": {k: {kk: v for kk, v in b.items() if kk not in ("w_mid", "f_mid")} for k, b in blades.items()},
           "leaves": leaves, "thin": thin, "log": log, "problems": problems, "uv": uv,
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
SHEET_VIEWS = {"f34_sheet": (-8, 10), "r34_sheet": (172, 10), "front_sheet": (0, 5), "side_sheet": (90, 5),
               "rear_sheet": (180, 5), "top_sheet": (0, 89)}
VIEW_NAMES = ("front", "side", "rear", "top", "underside")
PARTS_SHOT = (0, 15)
PART_SHOTS = {ROOT_P: (-25, 30)}


def _exploded(objs):
    """A temp build laid out like the sheet's exploded view: the root base in the middle, every blade drawn 0.6 off
    its joining face along its axis, the base leaves lifted over the rocks, rocks and pebbles drawn out."""
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
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=ROCK_DEEP, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=ROCK_DEEP, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=ROCK_DEEP, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
    c.location = off @ Vector(at)
    bpy.context.view_layer.update()
    return c


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    markers = [_scale_marker(h, (2.9, 0.0, 0.0))]
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        extra["front34"] = ([h], -8, 10)
        extra["rear34"] = ([h], 172, 10)
        for o in objs[1:]:
            extra["part_" + o.name.replace(HERO, "").lower()] = ([o], *PART_SHOTS.get(o.name, PARTS_SHOT))
        if shown:
            extra["exploded"] = (shown, 0, 12)
        extra["scale"] = ([h] + markers, -20, 6)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = m033._long_lens(kit)
        try:
            sheet = M.views(NUM, [h], names=VIEW_NAMES, extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet}
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


def render_close_ups(objs):
    """blade_cu (B1's upper half, close-up 2), blade_edge (Blade Center edge-on: its thickness), edge_side (the hero
    side-on at eye level: every blade's thickness), root_under (the root base part from below, close-up 1), root_cu
    (the hero's foot, close-up 3)."""
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    by = {o.name: o for o in objs}
    h = objs[0]
    out = {}

    def at(o, p):
        return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)
    rc = m033.render_close
    _joins()
    root, tip, L, P, T, u = _blade_frame("B1")
    out["blade_cu"] = rc([h], f"{d}/blade_cu.png", -30, 20, at(h, (P[3] + P[5]) / 2), 0.75)
    if B1_P in by:
        b = by[B1_P]
        w = Vector(BLADE_INFO.get("B1", {}).get("w_mid", (1, 0, 0)))
        az = math.degrees(math.atan2(w.x, -w.y))          # camera along the width axis: the blade edge-on
        out["blade_edge"] = rc([b], f"{d}/blade_edge.png", az, 8, at(b, (P[2] + P[3]) / 2), 0.9)
    out["edge_side"] = rc([h], f"{d}/edge_side.png", 90, 0, at(h, (0.0, 0.0, 1.2)), 1.25)
    if ROOT_P in by:
        r = by[ROOT_P]
        out["root_under"] = rc([r], f"{d}/root_under.png", -20, -55, at(r, (0, 0, 0.15)), 0.4)
    out["root_cu"] = rc([h], f"{d}/root_cu.png", -15, 15, at(h, (0.0, -0.4, 0.35)), 0.75)
    return out


def preview(names=("front_sheet", "f34_sheet", "rear_sheet", "side_sheet", "top_sheet"), vfx=False):
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
    EXPLODE["on"] = False
    h, lg = _make(HERO, hero_all, "hero", HERO_BUDGET)
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, _ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"hero": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                        "boundary_edges", "normals")}, "log": lg,
            "blades": {k: {kk: v for kk, v in b.items() if kk not in ("w_mid", "f_mid")} for k, b in BLADE_INFO.items()},
            "leaves": dict(LEAF_INFO), "offset": [round(x, 3) for x in h[OFF]]}
