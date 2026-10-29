"""022 Fiber Shrub (references/022.png): a chunky fan-shaped forage shrub. A short faceted brown stem foot splits low
into six stems; nine thick lens-shaped leaves (pointed at both ends, a raised centre vertex and a midrib ridge) fan
out from them; three pale tan fiber tufts (crowns of broad faceted blades) sit on flared brown collars at the stem
tops.

    import importlib, kit_models, m022; importlib.reload(kit_models); importlib.reload(m022); m022.build()

Parts as on the sheet's exploded view, each built by its own function (front -Y, +X right, ground z = 0, studs):
- FiberPlantStemFork: the exploded fork (8-sided trunk, two upper limbs and a low side branch, flat 8-sided ends).
- FiberPlantLeaf: one thick lens leaf (leaf_mesh).
- FiberPlantTuft: one fiber tuft (tuft_mesh: a 6-sided waist, 2 + 4 + 5 blades) with its short brown peg.
The hero (FiberPlantNode) uses the same builders: stems() (the foot + six limbs, three of them collared), nine
leaf_mesh() copies and three tuft_mesh() copies; united one shell at a time (guarded exact booleans), floor-cut at
the ground. M022_spec.md holds the study, the decisions and each stage's record.

Colour (stage 4) is painted by position fields inside the builders, before the union (the union and cleanup keep
each face's key and Tint): leaves base -> tip along each leaf, blades base -> tip along each blade, wood with a
darker core under the tufts. Never by facing.
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

NUM, TITLE, SHEET = 22, "Fiber Shrub", "M022"

LEAF, LEAF_TIP, LEAF_BASE = "m022_leaf", "m022_leaf_tip", "m022_leaf_base"
FIBER, FIBER_BASE, FIBER_TIP = "m022_fiber", "m022_fiber_base", "m022_fiber_tip"
WOOD, WOOD_DARK = "m022_wood", "m022_wood_dark"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0
COLOUR = [True]

# ---- palette (stage 4) -------------------------------------------------------------------------------------------------
# (hex, roughness, low_spec). Starting values = the spec's calibration targets; stage 4 writes the calibrated hexes.
# Pass 1 (K.calibrate on the test dome, 6 iterations): each key's dome median within 3 of its target (in the
# comment). fiber_tip clipped on the dome (it came back #F0B390, a pink cast): set instead from fiber's dome ratio in
# linear light (target tip / target fiber x calibrated fiber), which reproduces fiber_base's calibration within 1.
# Pass 2 (the hero renders): with the dome hexes the f34 / front / top medians read leaves #597B36 / #597B36 /
# #608337 (sheet #6B8E2D / #688B2D / #678C30), fiber #DAB883 (#F6C683) and wood #6B5235 (#704D2F): each family
# corrected in linear light by the mean sheet / ours ratio over those views (leaves x(1.34, 1.27, 0.73), fiber
# x(1.28, 1.12, 0.93), wood x(1.16, 0.93, 0.85)). leaf_base kept cool (hue ~100, spec 5.4). The side and rear are
# lit by the studio's fill and read darker on every model: reported, not fitted (M017's rule).
# Round 2 (new crowns and layout), two passes. Pass 1 on the f34 / front medians: leaves x(1.07, 1.04, 1.04); fiber
# x(0.91, 0.92, 1.04) (the open crowns read #FFCC7F, red clipped); wood moved to hue 27 (verifier m3) and x1.08 so the
# part fork stays within 8 of #885E3D while the hero stems reach #704D2F. Pass 2 re-measured every family within
# tolerance (f34 leaves #6A8D2D, fiber #FDC785, wood #6F4B2D), so no further change. Round-1 values in comments.
PALETTE = {
    LEAF: ("#638332", 0.8, True),           # r1 #608131; dome pass #53733A (dome #61863C, target #62893C)
    LEAF_TIP: ("#87A62F", 0.8, True),       # r1 #83A32E; dome pass #729236 (dome #8AAF38, #8CB238)
    LEAF_BASE: ("#426435", 0.8, True),      # r1 #406234; dome pass #395838 (dome #41643A, #42653A)
    # fiber, pass 2b: after the first hero correction the f34 / front read #EEB776 / #EEB877 (sheet #F6C683 /
    # #F4C380), a little too saturated: x(1.07, 1.17, 1.21) more. Pass 2c: the final crowns (blades turned to the
    # front) read #E6BB7A / #E4BA79: x(1.17, 1.12, 1.15) more
    FIBER: ("#E0B47E", 0.85, False),        # r1 #E9BB7C; dome pass #BE9D6E (dome #F2C180, #F2C180)
    FIBER_BASE: ("#CA9A65", 0.85, False),   # r1 #D2A063; dome pass #AA8758 (dome #D7A567, #D9A567)
    FIBER_TIP: ("#E8CDA6", 0.85, False),    # r1 #F1D5A3; dome pass #C4B491 by ratio (#FADDA8)
    WOOD: ("#785431", 0.9, False),          # r1 #73492D (hue 24); dome pass #6B4C31 (dome #865E3E, #875D3C)
    WOOD_DARK: ("#583B24", 0.9, False),     # r1 #553522 (hue 22); dome pass #4F3725 (dome #644734, #634530)
}
# calibration targets: the sheet's rendered medians of unshadowed regions (M022_spec.md 5.4). key -> (sRGB, kind)
TARGETS = {LEAF: ((0x62, 0x89, 0x3C), "green"), LEAF_TIP: ((0x8C, 0xB2, 0x38), "green"),
           LEAF_BASE: ((0x42, 0x65, 0x3A), "green"), FIBER: ((0xF2, 0xC1, 0x80), "all"),
           FIBER_BASE: ((0xD9, 0xA5, 0x67), "all"), FIBER_TIP: ((0xFA, 0xDD, 0xA8), "all"),
           WOOD: ((0x87, 0x5D, 0x3C), "brown"), WOOD_DARK: ((0x63, 0x45, 0x30), "brown")}


def palette():
    for k, (hx, rough, low) in PALETTE.items():
        K.set_colour(k, hx, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hx, rough=rough, low_spec=low)
    _restyle()


def _restyle():
    """Leaf keys (mix keys too) at the foliage specular."""
    for m in bpy.data.materials:
        if not m.name.startswith("FB_m022_leaf") or not m.node_tree:
            continue
        b = m.node_tree.nodes.get("Principled BSDF")
        if b and "Specular IOR Level" in b.inputs:
            b.inputs["Specular IOR Level"].default_value = K.FOLIAGE_SPEC


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's test dome. Returns {key: (hex, rendered)}."""
    keys = keys or list(TARGETS)
    for k in keys:
        K.fk().material(k)
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


def _dirn(az, el):
    a, e = math.radians(az), math.radians(el)
    return Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))


def _seed(name):
    return 22000 + sum((i + 1) * ord(ch) for i, ch in enumerate(name))


def tube(a, pts, radii, seed, sides=8, jitter=0.06, twist=8.0, mat=WOOD):
    """A faceted limb along pts with ring radii (+-jitter radius and +-twist degrees per inner ring), flat end caps.
    Returns (verts, rings, top cap faces)."""
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
            d = pts[i + 1] - pts[i - 1]
        d = d.normalized()
        u = (u0 - d * u0.dot(d)).normalized()
        v = d.cross(u).normalized()
        u0 = u
        inner = 0 < i < len(pts) - 1
        tw = ph + (math.radians(rng.uniform(-twist, twist)) if inner else 0.0)
        ring = []
        for k in range(sides):
            t = tw + 2 * math.pi * k / sides
            r = radii[i] * (1 + rng.uniform(-jitter, jitter) if inner else 1 + rng.uniform(-0.03, 0.03))
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
    return vs, rings, top


def frustum(a, base, axis, r0, r1, h, seed, mat, sides=6, phase=None):
    """A sides-gon frustum from base along axis: radius r0 at the base, r1 at the far end. Returns verts."""
    rng = random.Random(seed)
    u, v, d = _frame_from(axis)
    ph = rng.uniform(0, 2 * math.pi) if phase is None else phase
    bm = a.bm
    rings = []
    for z, r in ((0.0, r0), (h, r1)):
        rings.append([bm.verts.new(Vector(base) + d * z + (u * math.cos(ph + 2 * math.pi * k / sides) +
                                                         v * math.sin(ph + 2 * math.pi * k / sides)) * r
                                   * (1 + rng.uniform(-0.04, 0.04))) for k in range(sides)])
    faces = [bm.faces.new((rings[0][k], rings[0][(k + 1) % sides], rings[1][(k + 1) % sides], rings[1][k]))
             for k in range(sides)]
    faces += _cap(bm, rings[0], flip=True) + _cap(bm, rings[1])
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    vs = rings[0] + rings[1]
    a._finish(vs, mat, tint=1.0)
    return vs


def _zip(bm, outer, inner, c, flip=False):
    """Triangulate the band between two closed loops (both in the same rotational order round c in the plane of
    the leaf): walk both loops by angle. Returns faces."""
    def ang(p):
        return math.atan2(p[1] - c[1], p[0] - c[0])

    def ordered(loop):
        k = min(range(len(loop)), key=lambda i: ang(loop[i][1]) % (2 * math.pi))
        return loop[k:] + loop[:k]
    O, I = ordered(outer), ordered(inner)
    ao = [ang(p) % (2 * math.pi) for _, p in O] + [2 * math.pi + ang(O[0][1]) % (2 * math.pi)]
    ai = [ang(p) % (2 * math.pi) for _, p in I] + [2 * math.pi + ang(I[0][1]) % (2 * math.pi)]
    O = O + [O[0]]
    I = I + [I[0]]
    i = j = 0
    fs = []
    while i < len(O) - 1 or j < len(I) - 1:
        if j == len(I) - 1 or (i < len(O) - 1 and ao[i + 1] <= ai[j + 1]):
            tri = (O[i][0], O[i + 1][0], I[j][0])
            i += 1
        else:
            tri = (O[i][0], I[j + 1][0], I[j][0])
            j += 1
        fs.append(bm.faces.new(tri[::-1] if flip else tri))
    return fs


# ---- leaf -------------------------------------------------------------------------------------------------------------
# outline (t along the leaf, half width / W), base -> tip, each side; the base and tip are points (pointed both ends)
LEAF_OUT = ((0.15, 0.31), (0.37, 0.48), (0.58, 0.47), (0.80, 0.27))   # round 3: sharper tips (0.50 / 0.32 read oval)
# front: a ring of 6 points at RING_H x the front thickness round a raised apex (the close-up's centre vertex) at
# APEX_T along the leaf; the ring's two midline points make the midrib ridge, its side points sit RING_IN of the way
# out to the outline
RING = ((0.20, 0.0), (0.38, 0.52), (0.70, 0.50), (0.86, 0.0))      # (t, fraction of the half width; 0 = midline)
RING_H = 0.55
APEX_T = 0.53
BACK = ((0.24, 0.0), (0.50, 0.50), (0.78, 0.0))                   # the back ring (t, fraction); back apex at 0.5
BACK_H = 0.55
THICK = (0.095, 0.06)           # front / back thickness, fractions of L (spec 1.4: 0.15 L in all, 0.6 / 0.4)
INFO = {}


def _hw(t, out=LEAF_OUT):
    pts = [(0.0, 0.0)] + list(out) + [(1.0, 0.0)]
    for (t0, h0), (t1, h1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            return h0 + (h1 - h0) * (t - t0) / (t1 - t0)
    return 0.0


def leaf_frame(base, az, el, face):
    """(d, s, n): d along the leaf (azimuth az, elevation el), n the front face's normal (the part of `face`
    square to d), s = n x d."""
    d = _dirn(az, el)
    f = Vector(face).normalized()
    n = (f - d * f.dot(d))
    if n.length < 1e-4:
        n = Vector((0, 0, 1)) - d * d.z
    n.normalize()
    s = n.cross(d).normalized()
    return d, s, n


def leaf_mesh(a, base, az, el, L, W, face, seed, droop=0.0, curl=0.0):
    """One thick lens leaf: a 10-point outline pointed at both ends (LEAF_OUT), a front of a 6-point ring round a
    raised apex (midrib ridge + centre vertex, the close-up's 'broad flat facets'), a back of a 4-point ring round a
    lower back apex. droop bends the leaf down by droop x L x t^2 (world -Z, a function of t only, so the leaf never
    folds through itself); curl lifts both edges by curl x L x (|y| / W). Returns (verts, {vert: t})."""
    rng = random.Random(seed)
    bm = a.bm
    d, s, n = leaf_frame(base, az, el, face)
    B = Vector(base)
    Wj = W * (1 + rng.uniform(-0.03, 0.03))
    tf, tb = THICK[0] * L, THICK[1] * L
    tm = {}

    def vert(t, y, z):
        p = B + d * (t * L) + s * y + n * z
        p += Vector((0, 0, -droop * L * t * t))
        p += n * (curl * L * abs(y) / max(W, 1e-6))
        v = bm.verts.new(p)
        tm[v] = t
        return v
    jit = lambda: 1 + rng.uniform(-0.04, 0.04)
    right = [(t, -h * Wj * jit()) for t, h in LEAF_OUT]
    left = [(t, h * Wj * jit()) for t, h in LEAF_OUT]
    out_pts = [(0.0, 0.0)] + right + [(1.0, 0.0)] + left[::-1]
    outline = [(vert(t, y, 0.0), (t, y)) for t, y in out_pts]
    # front ring (same order as the outline: base, right side, tip, left side)
    fr = []
    ring_pts = [(RING[0][0], 0.0), (RING[1][0], -RING[1][1] * _hw(RING[1][0]) * Wj),
                (RING[2][0], -RING[2][1] * _hw(RING[2][0]) * Wj), (RING[3][0], 0.0),
                (RING[2][0], RING[2][1] * _hw(RING[2][0]) * Wj), (RING[1][0], RING[1][1] * _hw(RING[1][0]) * Wj)]
    for t, y in ring_pts:
        fr.append((vert(t, y, tf * RING_H * rng.uniform(0.9, 1.1)), (t, y)))
    apex = vert(APEX_T, 0.0, tf)
    back_pts = [(BACK[0][0], 0.0), (BACK[1][0], -BACK[1][1] * _hw(BACK[1][0]) * Wj), (BACK[2][0], 0.0),
                (BACK[1][0], BACK[1][1] * _hw(BACK[1][0]) * Wj)]
    br = [(vert(t, y, -tb * BACK_H), (t, y)) for t, y in back_pts]
    bapex = vert(0.5, 0.0, -tb)
    # 2D coordinates in the leaf plane (x = t L, y): zip by angle round the apex
    to2 = lambda ty: (ty[0] * L, ty[1])
    O = [(v, to2(ty)) for v, ty in outline]
    Fr = [(v, to2(ty)) for v, ty in fr]
    Br = [(v, to2(ty)) for v, ty in br]
    fs = []
    fs += _zip(bm, O, Fr, (APEX_T * L, 0.0))
    for k in range(len(Fr)):
        fs.append(bm.faces.new((Fr[k][0], Fr[(k + 1) % len(Fr)][0], apex)))
    fs += _zip(bm, O, Br, (0.5 * L, 0.0), flip=True)
    for k in range(len(Br)):
        fs.append(bm.faces.new((Br[(k + 1) % len(Br)][0], Br[k][0], bapex)))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    vs = [v for v, _ in outline] + [v for v, _ in fr] + [apex] + [v for v, _ in br] + [bapex]
    a._finish(vs, LEAF, tint=1.0)
    INFO.setdefault("leaf_inverted", []).append(_inverted_piece(vs))
    return vs, tm


# ---- tuft ---------------------------------------------------------------------------------------------------------------
BLADE_RINGS = ((0.0, 0.38, 0.6), (0.36, 1.0, 1.0), (0.70, 0.62, 0.7))   # (t, width frac, thickness frac)


def blade_mesh(a, base, axis, side, L, W, T, seed):
    """One fiber blade: a diamond section (two width points, two midrib points front and back), three rings
    (narrow base, widest at 0.36 L, 0.7 L) and a sharp tip. 22 tris. Returns (verts, {vert: t})."""
    rng = random.Random(seed)
    bm = a.bm
    d = Vector(axis).normalized()
    u = (Vector(side) - d * Vector(side).dot(d)).normalized()
    v = d.cross(u).normalized()
    tm = {}
    rings = []
    for t, wf, tf in BLADE_RINGS:
        c = Vector(base) + d * (t * L)
        w = W * wf * 0.5 * (1 + rng.uniform(-0.05, 0.05))
        th = T * tf * 0.5
        ring = [bm.verts.new(c + u * w), bm.verts.new(c + v * th), bm.verts.new(c - u * w), bm.verts.new(c - v * th)]
        for x in ring:
            tm[x] = t
        rings.append(ring)
    tip = bm.verts.new(Vector(base) + d * L)
    tm[tip] = 1.0
    fs = []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(4):
            j = (k + 1) % 4
            fs.append(bm.faces.new((r0[k], r0[j], r1[j], r1[k])))
    for k in range(4):
        fs.append(bm.faces.new((rings[-1][k], rings[-1][(k + 1) % 4], tip)))
    fs += _cap(bm, rings[0], flip=True)
    quads = [f for f in fs if len(f.verts) == 4]
    bmesh.ops.triangulate(bm, faces=quads, quad_method="SHORT_EDGE")
    vs = [x for r in rings for x in r] + [tip]
    bmesh.ops.recalc_face_normals(bm, faces=K.faces_of(vs))
    a._finish(vs, FIBER, tint=1.0)
    return vs, tm


# tuft blades: (count, elevation from the tuft plane (deg), length / H, width / L) per ring
# stage 1 round 3: three rings of broad lances (round 1's 0.27 / 0.30 wide blades read as spikes and round 2's tall
# inner pair over short low outer blades as a fountain; the sheet's crown is a full cup about as wide as tall)
# (count, elevation range (deg), length / crown height, width / length, base radius / diameter)
# stage 4 round: the crown opened up (mid 60-70 / outer 50-58 made a closed cone whose shaded inside read as a
# dark brown hollow: the f34 fiber share 0.12 against the sheet's 0.19, and the dark tan fell into the wood mask)
# (round 4: outer 36-46 deg turned the outer blades' broad faces up, so every side view saw them edge-on as needles:
# 44-54 shows them as the close-up's broad splayed lances)
# round 2 (verifier B1): the crowns read as closed shadowed balls in front and needle fans from the side; the sheet's
# are open flames of 7-10 pale lances: inner 75-85, middle 50-60, outer 30-45 deg, fewer and longer blades
TUFT_RINGS = ((2, (75.0, 85.0), 0.98, 0.32, 0.03),
              (3, (50.0, 60.0), 0.90, 0.36, 0.07),
              (4, (30.0, 45.0), 0.80, 0.40, 0.11))       # stage 2: base radii inside the narrower waist
FRONT_LEAN = 30.0       # hero blades: no blade leans toward -Y (the f34 camera) more than this from vertical
# hero: world azimuths (deg, 270 = front) per ring (inner, middle, outer), first `count` used: the inner pair upright
# front and back, the middle ring to the front diagonals and the back, the outer ring out to both sides and the back
# diagonals (the sheet's flame: low lances splaying left and right, upright ones in the middle)
WORLD_AZ = ((180.0, 0.0), (205.0, 335.0, 90.0), (175.0, 5.0, 130.0, 50.0))
BLADE_ROLL = 70.0      # degrees the blade's width turns from tangential toward its radial plane
BLADE_T = 0.08          # blade thickness / L
# waist bottom radius, top radius (fractions of the crown diameter), height (studs, x H/1.35). Stage 2: the bottom
# narrower (0.30 left the waist wall a hair inside the collar's rim on T1: two inverted slivers and a crossing pair)
WAIST = (0.18, 0.40, 0.22)


FACE_TURN = 0.2        # hero blades: how far each blade's width axis turns toward square-on to the front (round 2:
                       # 0.4 turned every blade face to the front, so the side view saw needles)


def tuft_mesh(a, foot, axis, diam, height, seed, counts=None, waist_sink=0.12, face=None, front_lean=None,
              roll=None):
    """One fiber tuft: a 6-sided waist cone (its bottom waist_sink below `foot`, the collar top) and a crown of
    broad pointed blades in three rings (TUFT_RINGS: 75-85, 50-60, 30-45 deg), each blade yawed +-10 deg, its width
    rolled BLADE_ROLL toward its radial plane, and as long as both the crown's height and its diameter allow. With
    front_lean (hero) the blades sit at WORLD_AZ and none leans toward -Y more than front_lean from vertical. Built
    round +Z and turned to `axis`.
    Returns {"waist": verts, "blades": [(verts, tm)], "frame": matrix}."""
    rng = random.Random(seed)
    counts = counts or [r[0] for r in TUFT_RINGS]
    rot = Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized()).to_matrix().to_4x4()
    F = Matrix.Translation(Vector(foot)) @ rot @ Matrix.Rotation(rng.uniform(0, 2 * math.pi), 4, "Z")
    hk = height / 1.35
    wh = WAIST[2] * hk
    z0 = -waist_sink
    waist = frustum(a, Vector((0, 0, z0)), (0, 0, 1), WAIST[0] * diam / 2, WAIST[1] * diam / 2, waist_sink + wh,
                    seed + 1, FIBER_BASE, sides=6)
    blades = []
    zt = wh                                 # the waist top
    lx = F.to_3x3() @ Vector((1, 0, 0))
    off = math.atan2(lx.y, lx.x)            # world azimuth of the tuft frame's local x
    for ri, (cnt, ((_, (e0, e1), lk, wk, rk))) in enumerate(zip(counts, TUFT_RINGS)):
        ph = rng.uniform(0, 2 * math.pi)
        for k in range(cnt):
            az = ph + 2 * math.pi * (k + rng.uniform(-0.12, 0.12)) / cnt
            if front_lean is not None:
                # round 2 (hero): each blade at a set world azimuth (WORLD_AZ, +-8 deg) so the crown fans out to both
                # sides like the sheet's flame and no low blade points at the front camera
                az = math.radians(WORLD_AZ[ri][k % len(WORLD_AZ[ri])] + rng.uniform(-8, 8)) - off
            el = math.radians(rng.uniform(e0, e1))
            yaw = math.radians(rng.uniform(-10, 10))
            radial = Vector((math.cos(az), math.sin(az), 0.0))
            tang = Vector((-math.sin(az), math.cos(az), 0.0))
            for _ in range(30):
                dvec = (radial * math.cos(el) + Vector((0, 0, 1)) * math.sin(el))
                dvec = (dvec + tang * math.tan(yaw) * 0.6).normalized()        # the blade yawed sideways
                # round 2: a blade pointing at the front camera foreshortens into a dark stub: steepen it until its
                # lean toward world -Y is at most front_lean from vertical
                if front_lean is None or el >= math.radians(86.0):
                    break
                if -(F.to_3x3() @ dvec).normalized().y <= math.sin(math.radians(front_lean)):
                    break
                el += math.radians(3.0)
            r0 = rk * diam
            b0 = Vector((math.cos(az) * r0, math.sin(az) * r0, zt * 0.5))
            # as long as the crown height allows (x lk) and no wider than the crown's diameter
            Lh = (height - b0.z) / max(dvec.z, 0.3) * lk
            Ld = (diam / 2 - r0) / max(math.hypot(dvec.x, dvec.y), 0.1)
            L = min(Lh, Ld) * rng.uniform(0.94, 1.06)
            # round 2: the broad face rolled BLADE_ROLL from the agave-like tangential width toward the blade's own
            # radial plane, so a blade splaying to either side of any view shows its face (the sheet's crowns read as
            # broad lances from the front, side and rear alike)
            inplane = (Vector((0, 0, 1)) * math.cos(el) - radial * math.sin(el)).normalized()
            rr = math.radians(BLADE_ROLL if roll is None else roll)
            side = (tang * math.cos(rr) + inplane * math.sin(rr)).normalized()
            tang = side
            if face is not None:
                # turn the blade's broad face part way toward `face` (tuft frame): sideways blades otherwise show the
                # front camera only their edge, as needles
                uf = dvec.cross(F.to_3x3().inverted() @ Vector(face)).normalized()
                if uf.dot(tang) < 0:
                    uf = -uf
                side = (tang * (1 - FACE_TURN) + uf * FACE_TURN).normalized()
            vs, tm = blade_mesh(a, b0, dvec, side, L, L * wk, L * BLADE_T, seed + 10 + k + 40 * ri)
            blades.append((vs, tm))
    allv = waist + [v for vs, _ in blades for v in vs]
    bmesh.ops.transform(a.bm, matrix=F, verts=allv)
    return {"waist": waist, "blades": blades, "frame": F}


# ---- stems --------------------------------------------------------------------------------------------------------------
# stage 1, round 2: the first foot (r 0.70 to z 0.62) read as a pot under the stems; the sheet's stems part right at
# the ground (z_f34_base): a low flare only, the limbs start near the ground
FOOT = ((0.0, 0.0, -0.15), (0.0, 0.05, 0.12), (0.0, 0.05, 0.30)), (0.56, 0.50, 0.36)
# name: (start (inside the foot), end, radius at start, radius at end, collar (True: flared cup for a tuft))
LIMBS = {
    "SL": ((-0.15, 0.0, 0.2), (-0.95, -0.2, 0.34), 0.22, 0.20, False),
    "SR": ((0.15, 0.0, 0.2), (0.95, -0.15, 0.32), 0.22, 0.20, False),
    # stage 4: thinner (wood share 0.26 / sheet 0.17); end x -0.6 -> -0.5 (T1's crown sat 0.07 W left of the sheet's)
    # stage 4 measure: the bases spread apart and S4 thinner, so the front's h .3 row shows separate stem runs with
    # paper between (sheet .36-.46 / .48-.53 / .55-.58; it read one run .35-.56)
    # round 2 (verifier m2): S1 / S2 lean out further (about 26 / 33 deg from vertical; were about 15 / 17 seen from
    # the front), S3 out to x 1.15 so T3 tops the right shoulder (f34 f .8 h .79; sheet .75)
    "S1": ((-0.2, -0.05, 0.05), (-0.65, -0.5, 1.38), 0.24, 0.22, True),
    "S2": ((0.2, -0.05, 0.05), (0.62, -0.55, 1.05), 0.24, 0.22, True),
    # round 3: T3 further back (at y 0.35 its blades grazed LE's upper flank: crossing faces after the union); the
    # sheet draws T3 behind LE anyway
    "S3": ((0.12, 0.15, 0.2), (1.15, 0.65, 1.75), 0.18, 0.16, True),
    "S4": ((0.0, 0.15, 0.08), (0.0, 0.45, 1.2), 0.19, 0.17, False),
}
COLLAR = (0.30, 1.3, 0.06)      # flare length, top radius x the stem's, rim height (round 2: 0.32 / 1.4 / 0.08 read
                                # as a ringed cup, verifier m2)


def limb_points(name):
    p0, p1, r0, r1, collar = LIMBS[name]
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0)
    n = max(3, round(d.length / 0.4)) + 1
    if not collar:
        pts = [p0.lerp(p1, i / (n - 1)) for i in range(n)]
        rad = [r0 + (r1 - r0) * i / (n - 1) for i in range(n)]
        return pts, rad
    dn = d.normalized()
    fl, k, rim = COLLAR
    q = p1 - dn * fl            # where the flare starts
    m = max(2, round((q - p0).length / 0.4)) + 1
    pts = [p0.lerp(q, i / (m - 1)) for i in range(m)]
    rad = [r0 + (r1 - r0) * i / (m - 1) for i in range(m)]
    pts += [p1 - dn * rim, p1]
    rad += [r1 * k, r1 * k * 1.03]
    return pts, rad


def stems(a, which=None):
    """The hero's stem cluster: the foot (an 8-sided flared trunk to z 0.62) and the six limbs of LIMBS (the collared
    three flare into cups for the tufts). Returns {name: verts} (with "foot")."""
    out = {}
    pts, rad = FOOT
    vs, _, _ = tube(a, [Vector(p) for p in pts], list(rad), _seed("foot"), sides=8, jitter=0.05)
    out["foot"] = vs
    for name in (which or LIMBS):
        pts, rad = limb_points(name)
        vs, _, _ = tube(a, pts, rad, _seed(name), sides=8, jitter=0.06, twist=8.0)
        out[name] = vs
    return out


def collar_top(name):
    p0, p1, r0, r1, collar = LIMBS[name]
    return Vector(p1), (Vector(p1) - Vector(p0)).normalized()


# ---- hero layout (spec 2.2, 2.3) ----------------------------------------------------------------------------------------
# name: (base, host stem, azimuth, elevation, L, W, face toward (x, y, z), droop, maturity shift, seed)
LEAVES = {
    # stage 1 round 3: the side and low leaves turned to face the front camera more (the low pair read edge-on), a
    # little broader; LG's base lower (the rear cell's centre leaf spans h .20-.61); LH / LI face the back
    # stage 4 measure: the upper side leaves longer and lower, the low pair shorter and higher, so both tiers reach the
    # silhouette's sides (sheet top profile .75 / .69 at f 0 / 1 and widths .91 at h .2, .92 at h .6; ours had the low
    # tips alone out at the sides, at h .21 / .17, and a pinch to .54 at h .3)
    # round 2 (verifier B2): the upper tier steeper (LA 34 -> 43, LE 32 -> 35) and longer so their tips stay at the
    # silhouette's corners (f34 h .73 / .68 at f 0 / 1; sheet .75 / .69); the low pair higher (25 / 23), longer and
    # turned a little forward (216 / 326) so their upper edges fill h .3 (width .89; sheet .92) and the depth holds
    # 3.64 now that LH / LI are shorter. LA lower on S1 and narrower so T1 shows above it from the back
    "LA": ((-0.4, 0.05, 0.95), "S1", 172.0, 43.0, 2.63, 0.95, (0.0, -0.8, 1.0), 0.04, 0.0),
    "LB": ((-0.45, -0.25, 0.55), "SL", 216.0, 25.0, 2.3, 1.1, (0.0, -1.0, 0.7), 0.03, -0.1),
    # round 3: the tall pair spread (sheet tips at f .29 / .67, the V notch down to h .54-.67)
    # verifier round 2 (S1): LC / LD faces turned out to the sides, so they aren't edge-on from the side camera
    "LC": ((-0.12, 0.3, 1.15), "S4", 164.0, 70.0, 2.5, 0.84, (-0.45, -1.0, 0.25), 0.0, 0.1),
    "LD": ((0.12, 0.3, 1.15), "S4", 16.0, 70.0, 2.45, 0.88, (0.45, -1.0, 0.25), 0.0, 0.1),
    "LE": ((0.55, 0.1, 1.1), "S3", 8.0, 35.0, 2.4, 1.12, (0.0, -1.0, 0.8), 0.04, 0.0),
    "LF": ((0.45, -0.25, 0.55), "SR", 326.0, 23.0, 2.3, 1.1, (0.0, -1.0, 0.7), 0.03, -0.1),
    # round 2 (verifier B3, the rear a green wall): LG rounder and smaller (1.5 x 1.0), LH / LI shorter (2.15) and laid
    # low and nearly flat (el 13, face mostly up) so the rear shows the stems at h .1-.4 over them; their reach back
    # keeps the depth inside the decided 3.9 +- 0.35. LC narrower so T1 shows beside it from the back
    # verifier round 2 (S2 / S1): LG stands up facing the rear camera (the sheet's face-on centre leaf, h .20-.61);
    # LH / LI steeper and longer, faces out to the sides, so the back half isn't a flat skirt (tips at y ~2.28, D holds)
    "LG": ((0.05, 0.45, 0.75), "S4", 90.0, 75.0, 1.5, 1.05, (0.0, 1.0, 0.0), 0.0, 0.0),
    "LH": ((-0.2, 0.4, 0.4), "S4", 125.0, 28.0, 2.6, 0.95, (-1.0, 0.4, 0.8), 0.04, -0.1),
    "LI": ((0.2, 0.4, 0.4), "S4", 55.0, 28.0, 2.6, 0.95, (1.0, 0.4, 0.8), 0.04, -0.1),
}
TUFT_DEPTH = 0.95      # hero tufts' depth (world Y) scale about their foot (round 2: 0.72 made side-view needles)
LEAF_SINK = 0.6        # a leaf base further than this x the host's radius from its axis is pulled in to it
# name: (stem, axis tilt (deg), tilt azimuth (deg), crown diameter, height, blades per ring (inner, middle, outer))
TUFTS = {
    # round 3: fewer, bigger blades (the sheet's crowns show 7-10 tips; 14 read bushy and self-shadowed dark)
    # stage 4 measure: the fiber share read 0.086 against the sheet's 0.19 in the f34: the crowns bigger
    # round 2: fewer, longer blades (2, 3, 4) / (2, 2, 3), the open flame of the sheet; T1 smaller (1.5 x 1.45) and
    # tilted toward az 205 so its crown sits at the sheet's f .16-.47; T3 out on S3 (x 1.15) at 1.05 x 1.0
    "T1": ("S1", 14.0, 205.0, 1.5, 1.45, (2, 3, 4)),
    "T2": ("S2", 24.0, 338.0, 1.5, 1.4, (2, 3, 4)),    # stage 2: 345 / 342 left union needles / a pocket face
    "T3": ("S3", 15.0, 10.0, 1.05, 1.0, (2, 2, 3)),
}


def _nearest_on(pts, p):
    best = None
    for q0, q1 in zip(pts, pts[1:]):
        dd = q1 - q0
        t = max(0.0, min(1.0, (p - q0).dot(dd) / max(dd.length_squared, 1e-12)))
        c = q0 + dd * t
        if best is None or (c - p).length < (best - p).length:
            best = c
    return best


def _host_r(name, p):
    pts, rad = (limb_points(name) if name in LIMBS else ([Vector(x) for x in FOOT[0]], list(FOOT[1])))
    c = _nearest_on(pts, p)
    i = min(range(len(pts)), key=lambda k: (pts[k] - c).length)
    return c, rad[i]


def place_leaf(name):
    base, host, az, el, L, W, face, droop, shift = LEAVES[name]
    B = Vector(base)
    pts = limb_points(host)[0]
    c, r = _host_r(host, B)
    if (B - c).length > LEAF_SINK * r:
        B = c + (B - c).normalized() * LEAF_SINK * r
    return B


def hero(a):
    """FiberPlantNode: stems (foot + six limbs), three tufts on the collars, nine leaves (spec 2)."""
    INFO.clear()
    st = stems(a)
    tufts = {}
    for name, (stem, tilt, taz, diam, height, counts) in TUFTS.items():
        top, d = collar_top(stem)
        axis = (Vector((0, 0, 1)) * math.cos(math.radians(tilt)) +
                Vector((math.cos(math.radians(taz)), math.sin(math.radians(taz)), 0)) * math.sin(math.radians(tilt)))
        tufts[name] = tuft_mesh(a, top + d * 0.01, axis, diam, height, _seed(name), counts, face=(0.0, -1.0, 0.3),
                                front_lean=FRONT_LEAN)
        # stage 4 round: the hero crowns pressed in depth (world Y) about their foot, so they fan out to the sides
        # like the sheet's crowns instead of pointing blades at the front camera (those read foreshortened and dark)
        tv = tufts[name]["waist"] + [v for vs, _ in tufts[name]["blades"] for v in vs]
        c = top + d * 0.01
        bmesh.ops.transform(a.bm, verts=tv, matrix=Matrix.Translation(c) @ Matrix.Diagonal((1.0, TUFT_DEPTH, 1.0, 1.0))
                            @ Matrix.Translation(-c))
    leaves = {}
    for name, (base, host, az, el, L, W, face, droop, shift) in LEAVES.items():
        B = place_leaf(name)
        vs, tm = leaf_mesh(a, B, az, el, L, W, face, _seed(name), droop=droop)
        leaves[name] = (vs, tm, shift)
        INFO.setdefault("leaf_base", {})[name] = [round(x, 2) for x in B]
    if COLOUR[0]:
        for name, (vs, tm, shift) in leaves.items():
            paint_leaf(a, vs, tm, shift, _seed(name) + 5)
        for name, t in tufts.items():
            paint_tuft(a, t, _seed(name) + 7, shift=0.1 if name == "T3" else 0.0)
        for name, vs in st.items():
            paint_wood(a, vs, _seed(name) + 9)


# ---- parts --------------------------------------------------------------------------------------------------------------
# exploded fork (spec 1.4): an 8-sided trunk splitting at 0.45 H into a near-vertical left limb and a right limb
# leaning 30-35 deg, plus a low side branch out to the left; flat 8-sided ends. (start, end, r start, r end)
FORK = {
    "trunk": ((0.0, 0.0, -0.05), (0.0, 0.0, 1.45), 0.40, 0.36),
    "left": ((-0.04, 0.0, 1.05), (-0.36, 0.05, 3.0), 0.26, 0.24),
    "right": ((0.05, 0.0, 1.05), (1.0, -0.05, 2.6), 0.26, 0.24),
    "side": ((-0.05, 0.02, 0.55), (-1.05, -0.1, 1.2), 0.23, 0.21),
}


def fork_part(a):
    """FiberPlantStemFork: the exploded fork."""
    pieces = []
    for name, (p0, p1, r0, r1) in FORK.items():
        p0, p1 = Vector(p0), Vector(p1)
        n = max(3, round((p1 - p0).length / 0.45)) + 1
        pts = [p0.lerp(p1, i / (n - 1)) for i in range(n)]
        rad = [r0 + (r1 - r0) * i / (n - 1) for i in range(n)]
        if name == "trunk":
            rad[0] *= 1.12              # the slight flare at the foot
        vs, _, _ = tube(a, pts, rad, _seed("fork_" + name), sides=8)
        pieces.append(vs)
    if COLOUR[0]:
        for vs in pieces:
            paint_wood(a, vs, _seed("forkpaint"), part=True)


PART_LEAF = dict(L=2.3, W=1.05, az=0.0, el=28.0, face=(0.0, -0.5, 1.0), droop=0.04)


def leaf_part(a):
    """FiberPlantLeaf: one thick lens leaf (L 2.3, W 1.05)."""
    p = PART_LEAF
    vs, tm = leaf_mesh(a, (0, 0, 0), p["az"], p["el"], p["L"], p["W"], p["face"], _seed("part_leaf"),
                       droop=p["droop"])
    if COLOUR[0]:
        # round 2 (verifier m4): the hero's low-leaf shift, so the part's base reads dark and cool like the close-up
        paint_leaf(a, vs, tm, -0.3, _seed("part_leaf") + 5)


PART_TUFT = (1.95, 1.45, (2, 4, 5))   # crown diameter, height (studs), blades per ring
PART_ROLL = 70.0        # the part's blade roll (40 tried: no broader, and the base band read 16 dark)
PART_PEG = (0.13, 0.30, 0.12)       # radius, length (below the waist bottom), overlap into the waist


def tuft_part(a):
    """FiberPlantTuft: T1's tuft with its short 8-sided brown peg under the waist."""
    name, (stem, tilt, taz, diam, height, counts) = "T1", TUFTS["T1"]
    diam, height, counts = PART_TUFT  # round 2: the close-up's crown (about 11 blades), W : H about 1.0 with the peg
    t = tuft_mesh(a, (0, 0, 0), (0, 0, 1), diam, height, _seed("part_tuft"), counts, roll=PART_ROLL)
    r, l, ov = PART_PEG
    peg = frustum(a, Vector((0, 0, -0.12 - l)), (0, 0, 1), r, r * 0.96, l + ov, _seed("peg"), WOOD, sides=8)
    if COLOUR[0]:
        paint_tuft(a, t, _seed("part_tuft") + 7)
        paint_wood(a, peg, _seed("peg") + 1, part=True)


# ---- stage 4: colour by position fields (never facing) ---------------------------------------------------------------
STEPS = 4
LEAF_BANDS = ((0.06, 0.40), (0.56, 0.90))     # t: base -> leaf over the first band, leaf -> tip over the second
LEAF_NOISE = 0.06
FIBER_BANDS = ((-0.1, 0.24), (0.46, 0.84))   # stage 4: the base band shorter (blade bases sit in the crown's shade)
MOTTLE = {"leaf": dict(amp=0.035, scale=0.5, jitter=0.004), "fiber": dict(amp=0.025, scale=0.6, jitter=0.003),
          "wood": dict(amp=0.05, scale=0.35, jitter=0.005)}
PIECE_TINT = 0.04
WOOD_CORE = dict(z=(0.55, 1.1), fade=0.3, r=0.35, mix=0.25, patch_scale=0.6, patch_level=0.3, patch_mix=0.25)


def _q(t):
    return round(max(0.0, min(1.0, t)) * STEPS) / STEPS


def _ladder(lo, mid, hi, v, bands):
    """v (a position along the piece) -> a key: lo below bands[0][0], lo -> mid across bands[0], mid, mid -> hi
    across bands[1], hi above, in quarter steps."""
    (a0, a1), (b0, b1) = bands
    if v < (a1 + b0) / 2:
        return K.mix_key(lo, mid, _q((v - a0) / (a1 - a0)))
    return K.mix_key(mid, hi, _q((v - b0) / (b1 - b0)))


def _mottle(a, faces, level, kind, seed):
    m = MOTTLE[kind]
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in faces:
        c = f.calc_center_median()
        k = level * (1.0 + m["amp"] * 1.6 * noise.noise(c * m["scale"] + off) + rng.uniform(-m["jitter"], m["jitter"]))
        for lo in f.loops:
            lo[a.tint_layer] = (k, k, k, 1.0)


def paint_leaf(a, vs, tm, shift, seed):
    """Leaf base -> leaf -> tip along its own length t (+ shift; broad noise), quarter steps."""
    rng = random.Random(seed)
    nf = K.noise_field(scale=0.9, seed=seed)
    fs = K.faces_of(vs)
    for f in fs:
        c = f.calc_center_median()
        t = sum(tm[v] for v in f.verts) / len(f.verts) + shift + LEAF_NOISE * 1.6 * nf(c)
        f.material_index = a._mi(_ladder(LEAF_BASE, LEAF, LEAF_TIP, t, LEAF_BANDS))
    _mottle(a, fs, 1.0 + rng.uniform(-PIECE_TINT, PIECE_TINT), "leaf", seed + 1)


def paint_tuft(a, t, seed, shift=0.0):
    """Blades fiber_base -> fiber -> fiber_tip along each blade; the waist fiber_base."""
    rng = random.Random(seed)
    for f in K.faces_of(t["waist"]):
        f.material_index = a._mi(FIBER_BASE)
    _mottle(a, K.faces_of(t["waist"]), 1.0, "fiber", seed)
    for i, (vs, tm) in enumerate(t["blades"]):
        fs = K.faces_of(vs)
        for f in fs:
            v = sum(tm[x] for x in f.verts) / len(f.verts) - shift + rng.uniform(-0.03, 0.03)
            f.material_index = a._mi(_ladder(FIBER_BASE, FIBER, FIBER_TIP, v, FIBER_BANDS))
        _mottle(a, fs, 1.0 + rng.uniform(-PIECE_TINT * 0.6, PIECE_TINT * 0.6), "fiber", seed + 3 + i)


def paint_wood(a, vs, seed, part=False):
    """Wood: plain wood; on the hero a darker core under the tufts (z 0.55-1.1 near the foot axis, faded over 0.3)
    and broad patches toward wood_dark; quarter steps."""
    W = WOOD_CORE
    pf = K.noise_field(scale=W["patch_scale"], seed=22090)
    fs = K.faces_of(vs)
    for f in fs:
        c = f.calc_center_median()
        t = 0.0
        if not part:
            r = math.hypot(c.x, c.y)
            z0, z1 = W["z"]
            inz = min(1.0, max(0.0, min(c.z - (z0 - W["fade"]), (z1 + W["fade"]) - c.z) / W["fade"]))
            inr = min(1.0, max(0.0, (W["r"] + W["fade"] - r) / W["fade"]))
            t = W["mix"] * inz * inr
        nv = pf(c)
        if nv > W["patch_level"]:
            t = max(t, W["patch_mix"] * min(1.0, (nv - W["patch_level"]) / 0.15))
        f.material_index = a._mi(K.mix_key(WOOD, WOOD_DARK, _q(t)))
    _mottle(a, fs, 1.0, "wood", seed)


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


# ---- cleanup (M018's guarded procedure, copied: m018.py is being edited in parallel) ----------------------------------
def _volume(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    v = bm.calc_volume(signed=True)
    bm.free()
    return v


UNION_MERGE = 0.0005


def _union(o, tries=5):
    """Guarded union: each shell is unioned on with an exact boolean, one at a time, the result checked against the
    volumes going in; a bad result is undone and the shell retried nudged a few thousandths of a stud; a shell that
    still fails is reported and left out. Returns {"shells", "retried", "failed"}."""
    act = bpy.context.view_layer.objects.active
    if act and act.mode != "OBJECT":
        with bpy.context.temp_override(active_object=act, object=act):
            bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()
    others = M.split_loose(o)
    retried, failed = [], []
    rng = random.Random(22900)
    for i, p in enumerate(others):
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
        for t in range(tries):
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
            if v1 >= max(v0, vp) * 0.995 and v1 <= (v0 + vp) * 1.005:
                ok = True
                bpy.data.meshes.remove(keep)
                if t:
                    retried.append((i, t))
                break
            old = o.data
            o.data = keep
            bpy.data.meshes.remove(old)
        if not ok:
            failed.append(i)
        bpy.data.objects.remove(p, do_unlink=True)
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
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.normal_update()
    vs = list(bm.verts)
    from mathutils.bvhtree import BVHTree
    t = BVHTree.FromBMesh(bm)
    bad = 0
    for f in bm.faces:
        if f.calc_area() < 1e-10:
            continue
        n = f.normal.normalized()
        o_ = f.calc_center_median() + n * 1e-4
        hits = 0
        while hits < 60:
            loc = t.ray_cast(o_, n)[0]
            if loc is None:
                break
            hits += 1
            o_ = loc + n * 1e-5
        bad += hits % 2
    bm.free()
    return bad


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
    # tiny inside-out slivers the unions leave where blade bases cross a waist rim or a neighbour (M017's recipe):
    # delete every face whose front side is solid, re-seal the pinholes with a fan fill, repeat
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
    for ml in (0.15, 0.3, 0.5):         # needles left: longer collapses, each still guarded (M020's pass)
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


def _flip_thin(o, lim=POLISH_LIM, max_bend=20.0):
    """Needles with no short edge (a long thin triangle on a blade's underside where the union cut it): rotate the
    needle's longest edge when both new triangles are fatter and the two faces are nearly coplanar (at most max_bend
    degrees apart, so the silhouette doesn't change). Returns the flips made."""
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
    """Close the holes left by deleted slivers (fan fill), triangulate, repair edges on more than two faces."""
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


CLEAN_MOVE = 0.05


def _clean_mesh(o, planes=(0.0,)):
    """The shared sliver pass, guarded (thin leaf flanks and blades must not fold through each other)."""
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


def _fix_floor(o):
    """Faces the floor cut made (flat, facing down at z 0): plain wood, Tint 0.95."""
    p = m011._Paint(o, off=(0, 0, 0))
    lay = p.tint_layer
    for f in p.bm.faces:
        if f.normal.z < -0.99 and abs(f.calc_center_median().z) < 1e-3:
            f.material_index = p._mi(WOOD)
            for lo in f.loops:
                lo[lay] = (0.95, 0.95, 0.95, 1.0)
    p.done()


# ---- stages 5 + 6 ---------------------------------------------------------------------------------------------------------
# Stage 5: nothing. The sheet shows an ordinary sunlit shrub: no emissive key, no light (decision 7).
# Stage 6: nothing. No glow, sparkle, floating fibres or dust on the sheet: no socket (decision 7).

# ---- build ---------------------------------------------------------------------------------------------------------------
PARTS = (("FiberPlantStemFork", fork_part), ("FiberPlantLeaf", leaf_part), ("FiberPlantTuft", tuft_part))
HERO = "FiberPlantNode"
UNION_PARTS = {"FiberPlantStemFork", "FiberPlantTuft"}
NOTES = {
    HERO: "fiber shrub forage node (FiberPlant): a short faceted brown stem foot splitting into six stems, nine thick "
          "lens-shaped leaves in a fan, three pale tan fiber tufts on flared brown collars; one closed mesh, flat base",
    "FiberPlantStemFork": "Stem Fork (reusable): an 8-sided trunk splitting into two limbs and a low side branch, "
                          "flat 8-sided join ends",
    "FiberPlantLeaf": "Leaf (reusable): a thick faceted lens pointed at both ends, raised centre vertex and midrib",
    "FiberPlantTuft": "Fiber Tuft (reusable): a crown of pointed faceted tan blades on a waist, short brown peg",
}


def _make(name, fn, role, budget):
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget, collision="hull",
             tint_var=0.0)
    lg = {}
    if role == "hero" or name in UNION_PARTS:
        lg["union"] = _union(o)
    if role == "hero":
        hoff = M._build_offset(fn)
        m004.floor_cut(o, z0=-hoff.z)
        _fix_floor(o)
        lg["clean"] = _clean_mesh(o, (0.0,))
    elif name in UNION_PARTS:
        lg["clean"] = _clean_mesh(o, ())
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    # bowtie vertices (two closed fans meeting at one point) left by the unions: split per fan (shared helper)
    lg["bowties"] = M.fix_bowties(o)
    return o, lg


def build(render=True, parts=True):
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn, "part", 1000)
    info_parts = dict(INFO)
    h, log["hero"] = _make(HERO, hero, "hero", 4000)
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    _restyle()
    M.display(NUM, order, TITLE)
    dropped = _drop_unused(order)
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    out = {"audit": [{k: M.audit(o)[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges",
                                                     "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces",
                                                     "normals", "ngons", "dup_verts", "nonmanifold_verts")}
                     for o in order],
           "thin": {o.name: m012._thin(o, POLISH_LIM) for o in order}, "log": log, "dropped": dropped,
           "problems": K.check(order), "info": {k: v for k, v in INFO.items()},
           "inverted": {o.name: inverted(o) for o in order},
           "self_hits": {o.name: _self_hits(o) for o in order},
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
    out["problems"] += [f"leaf piece inverted faces {INFO.get('leaf_inverted')}"
                        for _ in [0] if any(INFO.get("leaf_inverted", []))]
    if render:
        out["views"] = render_views(order)
    return out


def _drop_unused(objs):
    names = {o.name for o in objs}
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.split(".")[0] in names]
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m022_")]
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
# the sheet's comparison cameras (decision 9)
SHEET_VIEWS = {"f34_sheet": (0, 14), "front_sheet": (0, 10), "rear_sheet": (180, 10), "side_sheet": (90, 10),
               "r34_sheet": (152, 12), "top_sheet": (0, 89), "top_tilt_sheet": (0, 65)}
SHEET_LENS = 3.0        # the sheet's cells are drawn almost orthographic: the *_sheet shots use a 3x longer lens


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


# the exploded shot as the sheet lays it out (studs from the fork's foot; x right, z up): the fork at the centre, two
# leaves left, one top centre, two right; two tufts above (upper left and right). (part, location, rotation (deg))
EXPL = (("FiberPlantStemFork", (0.0, 0.0, 0.0), (0, 0, 0)),
        ("FiberPlantTuft", (-1.6, 0.0, 4.4), (0, -25, 0)),
        ("FiberPlantTuft", (2.1, 0.0, 3.7), (0, 25, 0)),
        ("FiberPlantLeaf", (-3.6, 0.2, 2.9), (0, 0, 0)),
        ("FiberPlantLeaf", (-3.7, 0.2, 0.8), (0, 0, 0)),
        ("FiberPlantLeaf", (0.2, 0.3, 4.3), (0, -55, 0)),
        ("FiberPlantLeaf", (2.2, 0.2, 2.0), (0, 0, 0)),
        ("FiberPlantLeaf", (2.3, 0.2, 0.3), (0, 0, 0)))


def render_views(objs):
    h = objs[0]
    by = {o.name: o for o in objs}
    shown = []
    saved = M.explode(objs[1:], {})
    try:
        if len(objs) > 1:
            base = Vector((h.location.x + 40, h.location.y, 0.0))
            for k, (part, loc, rot) in enumerate(EXPL):
                c = bpy.data.objects.new(f"_m022_expl_{k}", by[part].data)
                by[part].users_collection[0].objects.link(c)
                r = Matrix.Rotation(math.radians(rot[1]), 4, "Y") @ Matrix.Rotation(math.radians(rot[2]), 4, "Z")
                c.matrix_world = Matrix.Translation(base + Vector(loc)) @ r
                shown.append(c)
            bpy.context.view_layer.update()
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        if shown:
            extra["exploded"] = (shown, -16, 14)
        for o in objs[1:]:
            extra["part_" + o.name.replace("FiberPlant", "").lower()] = ([o], -20, 15)
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


# ---- measuring (the study's masks, numpy) ----------------------------------------------------------------------------------
REF_VIEWS = {"f34": (305, 104, 690, 398), "r34": (690, 104, 1010, 398), "front": (14, 452, 274, 662),
             "side": (278, 452, 500, 662), "rear": (504, 452, 760, 662), "top": (764, 452, 1010, 662)}
OUR_VIEWS = {"f34": "f34_sheet", "r34": "r34_sheet", "front": "front_sheet", "side": "side_sheet",
             "rear": "rear_sheet", "top": "top_tilt_sheet"}


def _classes(px, paper=(241, 238, 233)):
    """px (h, w, 3) sRGB 0-255 -> 0 none, 1 L leaves, 2 T fiber, 3 W wood, 4 O other (the study's cls())."""
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    mx, mn = px.max(-1), px.min(-1)
    v = mx / 255.0
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    d = np.maximum(mx - mn, 1e-6)
    hh = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    near = np.abs(px - np.array(paper)).max(-1) <= 16
    out = np.full(r.shape, 4, np.uint8)
    L = (s >= 0.28) & (hh >= 62) & (hh <= 165) & (g > 45)
    T = (hh >= 30) & (hh <= 52) & (s >= 0.12) & (s <= 0.62) & (v >= 0.74)
    W = ((s >= 0.25) & ((hh < 30) | (hh >= 340)) & (v < 0.86)) | ((hh >= 30) & (hh <= 45) & (v < 0.62) & (s >= 0.25))
    out[W] = 3
    out[T] = 2
    out[L] = 1
    out[near] = 0
    return out


def _load(path, box=None):
    px = K.NS["KIT"]["load_px"](path)[::-1, :, :3] * 255.0
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1]
    return np.clip(px, 0, 255)


def stats(px, paper=(241, 238, 233)):
    c = _classes(px, paper)
    obj = (c >= 1) & (c <= 3)
    cols = np.nonzero(obj.sum(0) >= 3)[0]
    rows = np.nonzero(obj.sum(1) >= 3)[0]
    bx0, bx1, by0, by1 = cols.min(), cols.max(), rows.min(), rows.max()
    W, H = bx1 - bx0, by1 - by0
    sub = c[by0:by1 + 1, bx0:bx1 + 1]
    n = max(1, ((sub >= 1) & (sub <= 3)).sum())
    out = {"wh": round(W / H, 3), "L": round((sub == 1).sum() / n, 3), "T": round((sub == 2).sum() / n, 3),
           "W": round((sub == 3).sum() / n, 3)}
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
    for k, lab in ((1, "L"), (2, "T"), (3, "W")):
        sel = pxs[sub == k]
        if len(sel) >= 8:
            srt = sel[np.argsort(sel.sum(1))]
            q = len(srt) // 4
            out[lab + "med"] = hexs(np.median(sel, axis=0))
            out[lab + "lit"] = hexs(np.median(srt[-q:], axis=0))
            out[lab + "shade"] = hexs(np.median(srt[:q], axis=0))
    # wood runs at h .25-.35 (stem gaps), leaf bands by height fifths
    runs = []
    for hh_ in (0.1, 0.2, 0.3):
        y = by1 - int(hh_ * H)
        row = sub[by1 - by0 - int(hh_ * H)] == 3
        xs = np.nonzero(row)[0]
        seg, start = [], None
        for x in range(len(row) + 1):
            on = x < len(row) and row[x]
            if on and start is None:
                start = x
            if not on and start is not None:
                if x - start >= 3:
                    seg.append((round(start / W, 2), round(x / W, 2)))
                start = None
        runs.append((hh_, seg))
    out["wood_runs"] = runs
    bands = []
    for i in range(5):
        r0, r1 = by1 - int((i + 1) * H / 5), by1 - int(i * H / 5)
        sel = px[r0:r1 + 1, bx0:bx1 + 1][c[r0:r1 + 1, bx0:bx1 + 1] == 1]
        bands.append(hexs(np.median(sel, axis=0)) if len(sel) > 20 else None)
    out["Lbands"] = bands
    return out


def _fit(px, h):
    """Nearest-neighbour resize of a bottom-up RGBA block to height h."""
    ys = (np.arange(h) * px.shape[0] / h).astype(int)
    w = max(1, int(round(px.shape[1] * h / px.shape[0])))
    xs = (np.arange(w) * px.shape[1] / w).astype(int)
    return px[ys][:, xs]


def _crop_obj(px, pad=0.06):
    """Crop a bottom-up RGBA render / sheet cell to its object silhouette (+pad)."""
    top = px[::-1, :, :3] * 255.0
    corner = np.median(top[:6, :6].reshape(-1, 3), axis=0)
    c = _classes(np.clip(top, 0, 255), tuple(int(x) for x in corner))
    obj = (c >= 1) & (c <= 3)
    ys, xs = np.nonzero(obj)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    p = int(pad * max(y1 - y0, x1 - x0))
    H, W = obj.shape
    y0, y1, x0, x1 = max(0, y0 - p), min(H, y1 + p), max(0, x0 - p), min(W, x1 + p)
    return px[H - y1:H - y0, x0:x1]


def compare(views=("f34", "front", "side", "rear", "r34", "top"), h=360):
    """Sheet cell (left) beside our long-lens render (right), each cropped to the silhouette and scaled to the same
    height; one row per view -> M022_sheet_compare.png."""
    kit = K.NS["KIT"]
    ref = kit["load_px"](M.ref(NUM))
    H = ref.shape[0]
    rows = []
    for v in views:
        x0, y0, x1, y1 = REF_VIEWS[v]
        a = _fit(_crop_obj(ref[H - y1:H - y0, x0:x1]), h)
        b = _fit(_crop_obj(kit["load_px"](f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[v]}.png")), h)
        gap = np.ones((h, 20, 4), np.float32)
        rows.append(np.concatenate([a, gap, b], axis=1))
    out = f"{M.MODEL_RENDERS}/{M.code(NUM)}/{M.code(NUM)}_sheet_compare.png"
    kit["save_px"](kit["vstack"](rows), out)
    return out


def measure(views=("f34", "front", "side", "rear", "r34", "top")):
    """Sheet against our renders, per view (the study's masks on both; our studio paper from the corner)."""
    ref = M.ref(NUM)
    out = {}
    for vname in views:
        a = stats(_load(ref, REF_VIEWS[vname]))
        ours = _load(f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[vname]}.png")
        corner = tuple(int(x) for x in np.median(ours[:8, :8].reshape(-1, 3), axis=0))
        b = stats(ours, paper=corner)
        out[vname] = {"sheet": a, "ours": b}
    return out
