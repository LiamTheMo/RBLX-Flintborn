"""067 Table and Seating (references/067.png): a rugged trestle table set. A thick top of four lengthwise chamfered
planks (seven pieces, three staggered butt joints) on two A-frame trestles (cleat, two legs splayed 10 deg, a low tie
with a pegged through-tenon stub on the front leg, one diagonal brace), a crossbar under the top whose tenon stubs poke
out past both trestles, two 42 deg knee braces from the crossbar down to the ties, two long two-plank benches on splayed
leg frames (cleats, stretchers) either side, and one three-plank stool off the table's front-left end. Dark slate square
bolt heads at the joints (30).

    import importlib, kit_models, m067; importlib.reload(kit_models); importlib.reload(m067); m067.build()

Build frame: studs, front -Y (the near bench), +X right, ground z 0, the table centred on x 0, y 0. Every object ends
with its origin at its bbox bottom centre; o["m067_offset"] is that origin in the build frame. Names (spec 8):
- TrestleTableSet (hero): everything above, one object of closed shells (no booleans). Collision precise.
- TrestleTableSetTable (top, trestles, crossbar, knee braces), ...Top, ...Trestle, ...Crossbar, ...Bench, ...Stool.
Every piece is its own closed shell, touching its parent face to face (never through it). Colour (stage 4) is by role
and position (plank-end and streak bands along each plank, a grime band at each leg foot), never by facing; the dark
undersides on the sheet are lighting. Stages 5-6: nothing on the sheet glows or emits; no sockets. See M067_spec.md.
"""
import json
import math
import os
import random
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M

NUM, TITLE, SHEET = 67, "Table and Seating", "M067"
OFF = "m067_offset"
PFX = "_m067_"
HERO = "TrestleTableSet"
TABLE_P, TOP_P, TRESTLE_P = "TrestleTableSetTable", "TrestleTableSetTop", "TrestleTableSetTrestle"
CROSS_P, BENCH_P, STOOL_P = "TrestleTableSetCrossbar", "TrestleTableSetBench", "TrestleTableSetStool"

WOOD, WOOD_LIGHT, WOOD_DEEP, IRON = "m067_wood", "m067_wood_light", "m067_wood_deep", "m067_iron"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
BURY = 0.05

# key -> (hex, roughness, metal, emission, low specular). Stage 4 (spec "Stage 4"): see calibrate() and the spec for how
# these were reached (K.calibrate on the studio dome, then checked on the hero renders against the sheet's regions).
PALETTE = {
    WOOD: ("#B26C2B", 0.8, 0.0, 0.0, True),
    WOOD_LIGHT: ("#E59241", 0.8, 0.0, 0.0, True),
    WOOD_DEEP: ("#8E4A18", 0.85, 0.0, 0.0, True),
    IRON: ("#474E56", 0.45, 0.5, 0.0, False),
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions) and K.sample kinds ("all" = paper filtered)
TARGETS = {WOOD: ((0xB8, 0x67, 0x1F), "brown"), WOOD_LIGHT: ((0xE5, 0x92, 0x41), "brown"),
           WOOD_DEEP: ((0x8E, 0x4A, 0x18), "brown"), IRON: ((0x47, 0x4E, 0x56), "all")}

# colour bands (spec 5.3 / 5.5): blend fractions toward the partner key, by position
END_BAND = ((0.15, 0.24), (0.35, 0.12))            # (distance from the chosen plank end, t toward wood_deep)
LIGHT_BAND = ((0.15, 0.30), (0.45, 0.15))          # (distance from the streak centre, t toward wood_light)
LEG_BAND = (0.25, 0.20)                            # (height of the foot band, t toward wood_deep)
PIECE_TINT = 0.05
BOLT_TINT = 0.02


def palette():
    for k, (hexcol, rough, metal, emit, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, metal=metal, emit=emit, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, metal=metal, emit=emit, low_spec=low)
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m067_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k == "m067_" + tail), None)
            if k1 in PALETTE and k2 and pct.isdigit():
                K.fk().KIT_PALETTE.pop(key, None)
                K.mix_key(k1, k2, int(pct) / 100)


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS); "all" kinds are sampled with the studio paper dropped. Returns
    {key: (hex, rendered)}."""
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


# ---- small helpers -----------------------------------------------------------------------------------------------------
def _mix(k1, k2, t, step=0.02):
    t = round(round(max(0.0, min(1.0, t)) / step) * step, 2)
    return K.mix_key(k1, k2, t)


def _seed(name):
    return sum((i + 1) * ord(c) for i, c in enumerate(name))


def _rng(name):
    return random.Random(_seed(name))


def _rt(name, amp):
    return 1.0 + _rng(name).uniform(-amp, amp)


# ---- piece register and placement frame ------------------------------------------------------------------------------
PIECES = []          # (kind, name, centroid in the build frame) per shell, in build order
GEO = {}             # measured placements (report)
XF = [Matrix.Identity(4)]
TAG = [""]           # name prefix of the current sub-assembly (bench_f, bench_b, trestle_l, ...)


class _Frame:
    """Place the pieces built inside it by matrix m (and prefix their names with tag)."""

    def __init__(self, m, tag=""):
        self.m, self.tag = m, tag

    def __enter__(self):
        XF.append(XF[-1] @ self.m)
        TAG.append(TAG[-1] + self.tag)

    def __exit__(self, *exc):
        XF.pop()
        TAG.pop()


def _solid(a, pts, faces, key, tint=1.0):
    """One closed shell from points and faces of any winding: bmesh makes the winding consistent, then the shell is
    flipped as a whole if its signed volume is negative. Returns (verts, faces) in the order given."""
    bm = a.bm
    vs = [bm.verts.new(Vector(p)) for p in pts]
    fs = [bm.faces.new([vs[i] for i in f]) for f in faces]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    for f in fs:
        f.normal_update()
    vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs)
    if vol < 0:
        for f in fs:
            f.normal_flip()
            f.normal_update()
    a._finish(vs, key, tint=tint)
    return vs, fs


def _piece(a, pts, faces, kind, name, colour=None, key=WOOD, tint=None):
    """Add one shell built in local coordinates: placed by the current frame, registered, coloured per face by
    colour(local face centre) -> key (default: key)."""
    name = TAG[-1] + name
    m = XF[-1]
    wpts = [m @ Vector(p) for p in pts]
    if tint is None:
        tint = _rt(name, BOLT_TINT if kind == "bolt" else PIECE_TINT)
    vs, fs = _solid(a, wpts, faces, key, tint)
    if colour is not None:
        for f, idx in zip(fs, faces):
            c = sum((Vector(pts[i]) for i in idx), Vector()) / len(idx)
            f.material_index = a._mi(colour(c))
    PIECES.append((kind, name, sum((v.co for v in vs), Vector()) / len(vs)))
    return vs, fs


CAP = {4: [[0, 1, 2, 3]], 8: [[0, 1, 2, 7], [7, 2, 3, 6], [6, 3, 4, 5]]}


def _prism(a, rings, kind, name, colour=None, key=WOOD, tint=None):
    """Closed prism through rings of 4 or 8 points (same order in each ring); the end caps split into quads."""
    n = len(rings[0])
    pts = [Vector(p) for r in rings for p in r]
    faces = []
    for i in range(len(rings) - 1):
        for k in range(n):
            k1 = (k + 1) % n
            faces.append([i * n + k, i * n + k1, (i + 1) * n + k1, (i + 1) * n + k])
    last = (len(rings) - 1) * n
    faces += [list(reversed(c)) for c in CAP[n]] + [[last + i for i in c] for c in CAP[n]]
    return _piece(a, pts, faces, kind, name, colour, key, tint)


def _sec(hu, hv, c=0.04):
    """A rectangle section (half sizes hu, hv) with its four corners chamfered by c (8 points), or plain (c = 0)."""
    if c <= 0:
        return [(-hu, -hv), (hu, -hv), (hu, hv), (-hu, hv)]
    return [(-hu + c, -hv), (hu - c, -hv), (hu, -hv + c), (hu, hv - c), (hu - c, hv), (-hu + c, hv), (-hu, hv - c),
            (-hu, -hv + c)]


def _box(a, lo, hi, kind, name, colour=None, key=WOOD, tint=None):
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    r0 = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)]
    r1 = [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    return _prism(a, [r0, r1], kind, name, colour, key, tint)


# ---- the bolt (spec 1.4: a square head 0.18, 0.05 proud with a 0.02 low pyramid, sunk 0.03) ------------------------
BOLT_H, BOLT_PROUD, BOLT_DOME, BOLT_SINK = 0.09, 0.05, 0.02, 0.03


def _bolt(a, c, n, up, name):
    """A square bolt head on a wood face: c on the face, n its outward normal, up an in-face direction for the sides."""
    n = Vector(n).normalized()
    u = Vector(up) - n * Vector(up).dot(n)
    u.normalize()
    w = n.cross(u)
    c = Vector(c)
    sq = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    pts = [c - n * BOLT_SINK + (u * i + w * j) * BOLT_H for i, j in sq]
    pts += [c + n * BOLT_PROUD + (u * i + w * j) * BOLT_H for i, j in sq]
    pts.append(c + n * (BOLT_PROUD + BOLT_DOME))
    faces = [[3, 2, 1, 0], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 8], [5, 6, 8], [6, 7, 8],
             [7, 4, 8]]
    return _piece(a, pts, faces, "bolt", name, key=IRON)


# ---- planks (spec 1.4: 0.44 thick, a 0.04 chamfer on the four long edges, every piece its own shell) ---------------
CH = 0.04
PLANK_T = 0.44


def _plank(a, x0, x1, yc, zc, hw, name, light=None, end=None):
    """A plank along X: 8-sided section (half width hw, half thickness 0.22, chamfer CH), x0..x1. Colour by position
    along it: a darker band at one end (end = x0 or x1, END_BAND) and optionally a lighter streak centred at x =
    light (LIGHT_BAND); extra rings only where a band edge falls."""
    sec = _sec(hw, PLANK_T / 2, CH)
    L = x1 - x0
    cuts = set()
    if end is not None:
        sgn = 1 if end == x0 else -1
        for d, _ in END_BAND:
            if d < 0.45 * L:
                cuts.add(round(end + sgn * d, 4))
    if light is not None:
        for d, _ in LIGHT_BAND:
            for s in (-1, 1):
                cuts.add(round(light + s * d, 4))
    xs = [x0] + sorted(x for x in cuts if x0 + 0.08 < x < x1 - 0.08) + [x1]
    rings = [[(x, yc + u, zc + v) for u, v in sec] for x in xs]

    def colour(c):
        if end is not None:
            d = abs(c.x - end)
            for lim, t in END_BAND:
                if d < lim - 1e-6:
                    return _mix(WOOD, WOOD_DEEP, t)
        if light is not None:
            d = abs(c.x - light)
            for lim, t in LIGHT_BAND:
                if d < lim - 1e-6:
                    return _mix(WOOD, WOOD_LIGHT, t)
        return WOOD
    return _prism(a, rings, "plank", name, colour)


def _plank_bands(name, x0, x1, streak):
    """The seeded coin for a plank piece's darker end, and its lighter streak centre (or None)."""
    rng = _rng(name)
    end = x0 if rng.random() < 0.5 else x1
    light = None
    L = x1 - x0
    if streak and L > 2.0:
        light = (x0 + x1) / 2 + rng.uniform(-0.2, 0.2) * L
        light = max(x0 + 0.8, min(x1 - 0.8, light))
        # keep the streak clear of the end band
        if abs(light - end) < END_BAND[-1][0] + LIGHT_BAND[-1][0] + 0.1:
            light = None
    return end, light


# ---- legs (sheared chamfered prisms with horizontal caps) -----------------------------------------------------------
def _lerp(foot, top, z1, z):
    t = z / z1
    return foot[0] + (top[0] - foot[0]) * t, foot[1] + (top[1] - foot[1]) * t


def _leg(a, foot, top, z1, hu, hv, name):
    """A square leg from foot (x, y) at z 0 to top (x, y) at z1: chamfered section hu (X) x hv (Y), horizontal end caps
    (planar), a ring at the foot band height for the grime band (LEG_BAND, by height)."""
    sec = _sec(hu, hv, CH)
    zb, tb = LEG_BAND
    rings = []
    for z in (0.0, zb, z1):
        cx, cy = _lerp(foot, top, z1, z)
        rings.append([(cx + u, cy + v, z) for u, v in sec])
    deep = _mix(WOOD, WOOD_DEEP, tb)
    return _prism(a, rings, "leg", name, lambda c: deep if c.z < zb - 1e-6 else WOOD)


def _between(a, lo_x, hi_x, z0, z1, y_of, kind, name, axis="y"):
    """A plain member between two slanted faces: section lo_x..hi_x by z0..z1 (in the cross plane), ends at y_of(z, -1)
    and y_of(z, +1) (axis "y"), or with x and y swapped (axis "x"). Each end lies on its neighbour's (planar) face."""
    sec = [(lo_x, z0), (hi_x, z0), (hi_x, z1), (lo_x, z1)]
    rings = []
    for s in (-1, 1):
        if axis == "y":
            rings.append([(u, y_of(z, s), z) for u, z in sec])
        else:
            rings.append([(y_of(z, s), u, z) for u, z in sec])
    return _prism(a, rings, kind, name)


# ---- top (spec 2.3) ---------------------------------------------------------------------------------------------------
TOP_Z0, TOP_Z1 = 2.16, 2.60
TOP_X = 3.00
ROW_HW = 0.33
ROWS = (1.08, 0.36, -0.36, -1.08)              # R1 (back) .. R4 (front), y centres
JOINTS = {0: -1.92, 2: 2.10, 3: -0.84}         # butt joint centres (R1 0.18 L, R3 0.85 L, R4 0.36 L)
JOINT_GAP = 0.04
END_JIT = 0.03
STREAK_ROWS = {"R2a", "R4b"}                   # pieces with a lighter streak (about one in three)


def top_pieces():
    out = []
    for i, yc in enumerate(ROWS):
        rng = _rng(f"row{i}")
        xa = -TOP_X + rng.uniform(-END_JIT, END_JIT)
        xb = TOP_X + rng.uniform(-END_JIT, END_JIT)
        if i in JOINTS:
            j = JOINTS[i]
            out += [(f"R{i + 1}a", xa, j - JOINT_GAP / 2, yc), (f"R{i + 1}b", j + JOINT_GAP / 2, xb, yc)]
        else:
            out.append((f"R{i + 1}a", xa, xb, yc))
    return out


def top(a):
    zc = (TOP_Z0 + TOP_Z1) / 2
    for nm, x0, x1, yc in top_pieces():
        end, light = _plank_bands("top" + nm, x0, x1, nm in STREAK_ROWS)
        _plank(a, x0, x1, yc, zc, ROW_HW, "top_" + nm, light=light, end=end)
    for yc in (ROWS[0], ROWS[3]):
        for x in (-TR_X, TR_X):
            _bolt(a, (x, yc, TOP_Z1), (0, 0, 1), (1, 0, 0), f"bolt_top_{x:+.1f}_{yc:+.2f}")


# ---- trestles (spec 2.2) -------------------------------------------------------------------------------------------------
TR_X = 2.20
CLEAT_HX, CLEAT_HY, CLEAT_Z0 = 0.225, 1.215, 1.86
CLEAT_ZC = (CLEAT_Z0 + TOP_Z0) / 2             # 2.01
LEG_HX, LEG_HY = 0.25, 0.23
LEG_TOP_Y, LEG_FOOT_Y = 0.86, 1.19             # 10 deg splay: atan(0.33 / 1.86)
TIE_Z = (0.40, 0.75)
TIE_HX = 0.17
TSTUB_HX, TSTUB_D = 0.15, 0.25
TSTUB_Z = (0.425, 0.725)
PEG = 0.20
DIAG_HX, DIAG_W = 0.15, 0.34
DIAG_TOP_Y = 0.0                               # the diagonal's centreline meets the cleat underside here


def leg_cy(z):
    """|y| of a trestle leg's centre at height z."""
    return _lerp((0.0, LEG_FOOT_Y), (0.0, LEG_TOP_Y), CLEAT_Z0, z)[1]


def diag_quad():
    """The diagonal's YZ outline: the lower long edge from the front leg's inner face at the tie top up to the cleat
    underside; cut along the leg's inner face (planar with it) and level under the cleat."""
    zt = TIE_Z[1]
    k = (LEG_TOP_Y - LEG_FOOT_Y) / CLEAT_Z0                     # dy/dz of the leg centre (front leg: -leg_cy)

    def leg_in(z):                                               # front leg inner face: y = -(leg_cy(z) - LEG_HY)
        return -(leg_cy(z) - LEG_HY)
    c0 = Vector((leg_in(zt), zt))
    y1 = 0.3
    for _ in range(40):                                          # centreline at the cleat on DIAG_TOP_Y
        th = math.atan2(CLEAT_Z0 - zt, y1 - c0.x)
        mid = y1 - (DIAG_W / 2) / math.sin(th)
        y1 += DIAG_TOP_Y - mid
    th = math.atan2(CLEAT_Z0 - zt, y1 - c0.x)
    d = Vector((math.cos(th), math.sin(th)))
    nrm = Vector((-d.y, d.x))                                    # toward the upper (leg-top) side
    c1 = Vector((y1, CLEAT_Z0))
    c2 = Vector((y1 - DIAG_W / math.sin(th), CLEAT_Z0))
    # upper edge meets the leg's inner face line y = leg_in(z) (linear in z)
    p = c0 + nrm * DIAG_W
    # solve p + d*s on y = leg_in(z): p.x + d.x s = -(LEG_FOOT_Y - LEG_HY) - (-k)... (linear): iterate
    s = 0.0
    for _ in range(60):
        q = p + d * s
        s += (leg_in(q.y) - q.x) / (d.x - (-k) * d.y) if abs(d.x + k * d.y) > 1e-9 else 0
    c3 = p + d * s
    GEO["diag_angle"] = round(math.degrees(th), 2)
    return [c0, c1, c2, c3]


def trestle(a, sx):
    """One A-frame trestle centred on x = sx * TR_X: cleat, two legs, tie, the tie's through-tenon stub with its peg on
    the front leg, the diagonal, and its six bolts (cleat ends, outer face at cleat and tie height). Identical for both
    trestles (translated, not mirrored); only the bolts go on the face away from the table."""
    xc = sx * TR_X
    for s, nm in ((-1, "front"), (1, "back")):
        _leg(a, (xc, s * LEG_FOOT_Y), (xc, s * LEG_TOP_Y), CLEAT_Z0, LEG_HX, LEG_HY, f"leg_{nm}")
    sec = _sec(CLEAT_HX, (TOP_Z0 - CLEAT_Z0) / 2, CH)
    _prism(a, [[(xc + u, y, CLEAT_ZC + v) for u, v in sec] for y in (-CLEAT_HY, CLEAT_HY)], "cleat", "cleat")
    # the low tie between the legs' inner faces
    _between(a, xc - TIE_HX, xc + TIE_HX, TIE_Z[0], TIE_Z[1], lambda z, s: s * (leg_cy(z) - LEG_HY), "tie", "tie")
    # the tie's through-tenon stub on the front leg's outer face (-Y), and its peg on top
    zm = sum(TSTUB_Z) / 2
    y_out = -(leg_cy(zm) + LEG_HY + TSTUB_D)
    _between(a, xc - TSTUB_HX, xc + TSTUB_HX, TSTUB_Z[0], TSTUB_Z[1],
             lambda z, s: -(leg_cy(z) + LEG_HY) if s > 0 else y_out, "stub", "tie_stub")
    y_leg_top = -(leg_cy(TSTUB_Z[1]) + LEG_HY)
    yp1 = y_leg_top - 0.03
    _box(a, (xc - PEG / 2, yp1 - PEG, TSTUB_Z[1]), (xc + PEG / 2, yp1, TSTUB_Z[1] + PEG), "peg", "peg")
    GEO["tie_stub_out"] = round(y_out, 3)
    # the diagonal (YZ outline, 0.30 thick in X)
    q = diag_quad()
    rings = [[(xc + s * DIAG_HX, p.x, p.y) for p in q] for s in (-1, 1)]
    _prism(a, rings, "diag", "diag")
    # bolts: cleat end faces, the outer face over each leg at cleat height and at tie height
    for s in (-1, 1):
        _bolt(a, (xc, s * CLEAT_HY, CLEAT_ZC), (0, s, 0), (1, 0, 0), f"bolt_cleat_end{s:+d}")
        _bolt(a, (xc + sx * CLEAT_HX, s * LEG_TOP_Y, CLEAT_ZC), (sx, 0, 0), (0, 0, 1), f"bolt_cleat_face{s:+d}")
        _bolt(a, (xc + sx * LEG_HX, s * leg_cy(zm), zm), (sx, 0, 0), (0, 0, 1), f"bolt_leg{s:+d}")


# ---- crossbar and knee braces (spec 2.3) ------------------------------------------------------------------------------
CB_HY, CB_HZ = 0.18, 0.15
CB_X = TR_X - CLEAT_HX                          # 1.975: the cleats' inner faces
CSTUB_HY, CSTUB_Z, CSTUB_L = 0.13, (1.89, 2.13), 0.30
KNEE_HY = 0.14
KNEE_BOT = (2.03, 2.37)                         # on the tie top (z 0.75)
KNEE_TOP_C, KNEE_TOP_HW = 1.00, 0.17            # under the crossbar (z 1.86)


def crossbar(a, bolts=True):
    sec = _sec(CB_HY, CB_HZ, CH)
    _prism(a, [[(x, u, CLEAT_ZC + v) for u, v in sec] for x in (-CB_X, CB_X)], "cross", "crossbar")
    x_out = TR_X + CLEAT_HX
    for s in (-1, 1):
        lo, hi = sorted((s * x_out, s * (x_out + CSTUB_L)))
        _box(a, (lo, -CSTUB_HY, CSTUB_Z[0]), (hi, CSTUB_HY, CSTUB_Z[1]), "cstub", f"cross_stub{s:+d}")
        if bolts:
            _bolt(a, (s * (x_out + CSTUB_L), 0.0, sum(CSTUB_Z) / 2), (s, 0, 0), (0, 0, 1), f"bolt_cstub{s:+d}")


def knee_quad(sx):
    zt = TIE_Z[1]
    b0, b1 = KNEE_BOT
    t0, t1 = KNEE_TOP_C - KNEE_TOP_HW, KNEE_TOP_C + KNEE_TOP_HW
    q = [(sx * b0, zt), (sx * b1, zt), (sx * t1, CLEAT_Z0), (sx * t0, CLEAT_Z0)]
    dx = (b0 + b1) / 2 - KNEE_TOP_C
    GEO["knee_angle"] = round(math.degrees(math.atan2(CLEAT_Z0 - zt, dx)), 2)
    return q


def knee(a, sx):
    q = knee_quad(sx)
    _prism(a, [[(x, s * KNEE_HY, z) for x, z in q] for s in (-1, 1)], "knee", f"knee{sx:+d}")


# ---- benches (spec 2.4) ----------------------------------------------------------------------------------------------
BENCH_Y = 2.40
BENCH_HL = 2.90
SEAT_Z0, SEAT_Z1 = 1.06, 1.50
SEAT_ROW_HW = 0.29
SEAT_ROWS = (0.31, -0.31)                       # inner (toward the table: +y local), outer
BENCH_JOINT = -2.03                             # inner row butt joint (0.15 L from -X)
BCLEAT_HX, BCLEAT_HY, BCLEAT_Z0 = 0.17, 0.55, 0.80
BLEG_X, BLEG_Y, BLEG_H = 2.45, 0.36, 0.21
BLEG_SPLAY_X, BLEG_SPLAY_Y = 5.0, 4.0           # deg outward
BSTR_HX, BSTR_Z = 0.10, (0.30, 0.54)


def bleg_c(sx, sy, z):
    """Bench leg centre (x, y) at height z (bench-local)."""
    fx = BLEG_X + BCLEAT_Z0 * math.tan(math.radians(BLEG_SPLAY_X))
    fy = BLEG_Y + BCLEAT_Z0 * math.tan(math.radians(BLEG_SPLAY_Y))
    cx, cy = _lerp((fx, fy), (BLEG_X, BLEG_Y), BCLEAT_Z0, z)
    return sx * cx, sy * cy


def bench(a):
    """One bench in bench-local coordinates (centre 0, inner row toward +y)."""
    zc = (SEAT_Z0 + SEAT_Z1) / 2
    for r, yc in enumerate(SEAT_ROWS):
        if r == 0:
            spans = [("in_a", -BENCH_HL, BENCH_JOINT - JOINT_GAP / 2), ("in_b", BENCH_JOINT + JOINT_GAP / 2, BENCH_HL)]
        else:
            spans = [("out", -BENCH_HL, BENCH_HL)]
        for nm, x0, x1 in spans:
            end, light = _plank_bands(TAG[-1] + nm, x0, x1, nm == "out")
            _plank(a, x0, x1, yc, zc, SEAT_ROW_HW, "seat_" + nm, light=light, end=end)
    for sx in (-1, 1):
        x = sx * BLEG_X
        _box(a, (x - BCLEAT_HX, -BCLEAT_HY, BCLEAT_Z0), (x + BCLEAT_HX, BCLEAT_HY, SEAT_Z0), "bcleat", f"bcleat{sx:+d}")
        for sy in (-1, 1):
            _leg(a, bleg_c(sx, sy, 0.0), bleg_c(sx, sy, BCLEAT_Z0), BCLEAT_Z0, BLEG_H, BLEG_H, f"bleg{sx:+d}{sy:+d}")
        xm = bleg_c(sx, 1, sum(BSTR_Z) / 2)[0]
        _between(a, xm - BSTR_HX, xm + BSTR_HX, BSTR_Z[0], BSTR_Z[1],
                 lambda z, s, sx=sx: s * (bleg_c(sx, 1, z)[1] - BLEG_H), "stretch", f"bstretch{sx:+d}")
        _bolt(a, (x, 0.0, SEAT_Z1), (0, 0, 1), (1, 0, 0), f"bolt_seat{sx:+d}")
        _bolt(a, (x, SEAT_ROWS[1] - SEAT_ROW_HW, zc), (0, -1, 0), (0, 0, 1), f"bolt_bface{sx:+d}")


BENCHES = (("bench_f_", Matrix.Translation((0.0, -BENCH_Y, 0.0))),
           ("bench_b_", Matrix.Translation((0.0, BENCH_Y, 0.0)) @ Matrix.Rotation(math.pi, 4, "Z")))


# ---- stool (spec 2.5) ------------------------------------------------------------------------------------------------
STOOL_C = (-4.95, -1.30)
STOOL_HL = 0.70
STOOL_ROWS = ((-0.70, -0.26), (-0.24, 0.24), (0.26, 0.70))
STOOL_SEAM = 0.03                               # the cross seam across the middle plank (f34)
SLEG_C, SLEG_H, SLEG_SPLAY = 0.47, 0.19, 7.0
APRON_T, APRON_IN, APRON_Z = 0.14, 0.05, (0.84, 1.06)
SSTR_HX, SSTR_Z = 0.07, (0.30, 0.50)


def sleg_c(sx, sy, z):
    f = SLEG_C + SEAT_Z0 * math.tan(math.radians(SLEG_SPLAY))
    cx, cy = _lerp((f, f), (SLEG_C, SLEG_C), SEAT_Z0, z)
    return sx * cx, sy * cy


def stool(a):
    """The stool in stool-local coordinates (centre 0): three seat planks along X (the middle one in two halves), four
    legs splayed 7 deg both ways, aprons on all four sides, stretchers on the +-X sides, a bolt on each seat side."""
    zc = (SEAT_Z0 + SEAT_Z1) / 2
    for r, (y0, y1) in enumerate(STOOL_ROWS):
        yc, hw = (y0 + y1) / 2, (y1 - y0) / 2
        spans = [(-STOOL_HL, -STOOL_SEAM / 2), (STOOL_SEAM / 2, STOOL_HL)] if r == 1 else [(-STOOL_HL, STOOL_HL)]
        for k, (x0, x1) in enumerate(spans):
            nm = f"seat{r}{'ab'[k]}"
            end, _ = _plank_bands(TAG[-1] + nm, x0, x1, False)
            _plank(a, x0, x1, yc, zc, hw, nm, end=end)
    for sx in (-1, 1):
        for sy in (-1, 1):
            _leg(a, sleg_c(sx, sy, 0.0), sleg_c(sx, sy, SEAT_Z0), SEAT_Z0, SLEG_H, SLEG_H, f"sleg{sx:+d}{sy:+d}")
    yo = SLEG_C + SLEG_H - APRON_IN
    for s in (-1, 1):
        # +-Y aprons run along X between the legs' inner X faces; +-X aprons along Y
        lo, hi = sorted((s * yo, s * (yo - APRON_T)))
        _between(a, lo, hi, APRON_Z[0], APRON_Z[1], lambda z, e: e * (sleg_c(1, 1, z)[0] - SLEG_H), "apron",
                 f"apron_y{s:+d}", axis="x")
        _between(a, lo, hi, APRON_Z[0], APRON_Z[1], lambda z, e: e * (sleg_c(1, 1, z)[1] - SLEG_H), "apron",
                 f"apron_x{s:+d}", axis="y")
        xm = sleg_c(s, 1, sum(SSTR_Z) / 2)[0]
        _between(a, xm - SSTR_HX, xm + SSTR_HX, SSTR_Z[0], SSTR_Z[1], lambda z, e: e * (sleg_c(1, 1, z)[1] - SLEG_H),
                 "stretch", f"sstretch{s:+d}")
        _bolt(a, (0.0, s * STOOL_HL, zc), (0, s, 0), (0, 0, 1), f"bolt_sy{s:+d}")
        _bolt(a, (s * STOOL_HL, 0.0, zc), (s, 0, 0), (0, 0, 1), f"bolt_sx{s:+d}")


# _between's axis "x" builds the member along X (ends at x = y_of(z, -+1)), its section given as y (lo..hi) by z
# ---- assemblies -----------------------------------------------------------------------------------------------------------
def table_all(a):
    top(a)
    for sx, tg in ((-1, "trestle_l_"), (1, "trestle_r_")):
        with _Frame(Matrix.Identity(4), tg):
            trestle(a, sx)
    crossbar(a)
    knee(a, -1)
    knee(a, 1)


def hero_all(a, with_stool=True):
    table_all(a)
    for tg, m in BENCHES:
        with _Frame(m, tg):
            bench(a)
    if with_stool:
        with _Frame(Matrix.Translation((STOOL_C[0], STOOL_C[1], 0.0)), "stool_"):
            stool(a)


def hero_nostool(a):
    hero_all(a, with_stool=False)


def top_part(a):
    top(a)


def trestle_part(a):
    trestle(a, 1)


def crossbar_part(a):
    crossbar(a)


def bench_part(a):
    bench(a)


def stool_part(a):
    stool(a)


# ---- seats (spec 2.8) ------------------------------------------------------------------------------------------------------
SEATS_PTS = {"m067_seat_f1": ((-1.20, -BENCH_Y, SEAT_Z1), (0, 1, 0)), "m067_seat_f2": ((1.20, -BENCH_Y, SEAT_Z1), (0, 1, 0)),
             "m067_seat_b1": ((-1.20, BENCH_Y, SEAT_Z1), (0, -1, 0)), "m067_seat_b2": ((1.20, BENCH_Y, SEAT_Z1), (0, -1, 0)),
             "m067_seat_stool": ((STOOL_C[0], STOOL_C[1], SEAT_Z1), (1, 0, 0))}
PART_SEATS = {TABLE_P: {k: v for k, v in SEATS_PTS.items() if "stool" not in k},
              BENCH_P: {"m067_seat_1": ((-1.20, 0.0, SEAT_Z1), (0, 1, 0)), "m067_seat_2": ((1.20, 0.0, SEAT_Z1), (0, 1, 0))},
              STOOL_P: {"m067_seat": ((0.0, 0.0, SEAT_Z1), (1, 0, 0))}}


def _store_points(o, pts):
    off = Vector(o[OFF])
    for k, (p, f) in pts.items():
        o[k] = [round(x, 4) for x in Vector(p) - off]
        o[k + "_facing"] = [float(x) for x in f]


NOTES = {
    HERO: "Trestle table set: a thick four-plank top (seven pieces, three butt joints) on two A-frame trestles (10 deg "
          "splay, cleat, low tie with a pegged through-tenon stub, diagonal), a crossbar under the top with tenon stubs "
          "past both trestles, two 42 deg knee braces, two two-plank benches on splayed leg frames, a three-plank stool "
          "at the front-left; 30 dark slate square bolts. Table top 2.60, seats 1.50; five seat points stored "
          "(m067_seat_*, with facings) for Studio Seat parts (Requires Manual Validation). Sheet header 69/132.",
    TABLE_P: "The table alone: top, two trestles, crossbar with stubs, two knee braces and their bolts (bench seat points "
             "stored relative to it)",
    TOP_P: "Table Top (Planks): four rows of 0.44 chamfered planks, seven pieces, four bolts",
    TRESTLE_P: "Leg / Trestle: cleat, two 10 deg splayed legs, low tie with a pegged through-tenon stub, diagonal, six "
               "bolts (the left trestle is the same mesh, translated)",
    CROSS_P: "Crossbar: chamfered beam with a tenon stub and bolt at each end",
    BENCH_P: "Bench Seat (Planks): two-plank seat (one butt joint) on two splayed leg frames with cleats and stretchers; "
             "two seat points stored",
    STOOL_P: "Stool: three-plank seat with a cross seam, four 7 deg splayed legs, aprons and stretchers; one seat point",
}
COLLISION = {HERO: "precise", TABLE_P: "box", TOP_P: "box", TRESTLE_P: "hull", CROSS_P: "box", BENCH_P: "box",
             STOOL_P: "box"}


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
    PIECES.clear()
    XF[:] = [Matrix.Identity(4)]
    TAG[:] = [""]
    fn(a)
    o = a.finish(collection=M.coll(NUM, TITLE), mark_asset=not temp, origin=None)
    K.drop_unused_slots(o)
    if not temp:
        K.tag(o, SHEET, TITLE, role, COLLISION[name], budget, NOTES[name])
    o[OFF] = [0.0, 0.0, 0.0]
    o.location = (0, 0, 0)
    o["m067_pieces"] = json.dumps([[k, n_, [round(x, 5) for x in c]] for k, n_, c in PIECES])
    bpy.context.view_layer.update()
    return o


def _bottom_centre(o):
    xs = [v.co.x for v in o.data.vertices]
    ys = [v.co.y for v in o.data.vertices]
    zs = [v.co.z for v in o.data.vertices]
    return Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))


def _recentre(o):
    bc = _bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


def _uv_overlaps(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    uv = bm.loops.layers.uv.active
    tris = []
    for f in bm.faces:
        ls = [(l[uv].uv.x, l[uv].uv.y) for l in f.loops]
        for i in range(1, len(ls) - 1):
            tris.append((f.index, [ls[0], ls[i], ls[i + 1]]))
    bm.free()
    boxes = [(min(p[0] for p in t), min(p[1] for p in t), max(p[0] for p in t), max(p[1] for p in t)) for _, t in tris]
    grid = {}
    for k, b in enumerate(boxes):
        for i in range(int(b[0] // 0.05), int(b[2] // 0.05) + 1):
            for j in range(int(b[1] // 0.05), int(b[3] // 0.05) + 1):
                grid.setdefault((i, j), []).append(k)
    pairs = {(a_, b_) for lst in grid.values() for i, a_ in enumerate(lst) for b_ in lst[i + 1:]
             if tris[a_][0] != tris[b_][0]}
    return [(tris[a_][0], tris[b_][0]) for a_, b_ in pairs if M._tri_overlap(tris[a_][1], tris[b_][1])]


def _uv_unfold(o, rounds=4):
    """Cut the smaller face of each UV-overlapping pair free along seams and unwrap again (m012). Returns faces cut."""
    cut = 0
    for _ in range(rounds):
        bad = _uv_overlaps(o)
        if not bad:
            break
        polys = o.data.polygons
        free = {min((a_, b_), key=lambda i: polys[i].area) for a_, b_ in bad}
        keys = {tuple(sorted(e)) for i in free for e in polys[i].edge_keys}
        for e in o.data.edges:
            if tuple(sorted(e.vertices)) in keys:
                e.use_seam = True
        cut += len(free)
        with M._override(o):
            bpy.ops.object.mode_set(mode="EDIT")
            try:
                bpy.ops.mesh.select_all(action="SELECT")
                bpy.ops.uv.unwrap(method=UV["method"], fill_holes=False, correct_aspect=True,
                                  margin_method="FRACTION", margin=UV["margin"])
            finally:
                bpy.ops.object.mode_set(mode="OBJECT")
    return cut


def _post(o):
    """Stage 2-3 pass: normals outward per shell, flat shading, no custom normals, origin at the bbox bottom centre,
    bowties split, UVs (angle-based islands, overlaps cut free). Faces stay planar quads and triangles (the caps of the
    8-sided sections are split into quads at build time): no n-gons."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    ng = [f for f in bm.faces if len(f.verts) > 4]
    if ng:
        bmesh.ops.triangulate(bm, faces=ng, quad_method="BEAUTY", ngon_method="BEAUTY")
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
    lg["uv_cut"] = _uv_unfold(o)
    K.drop_unused_slots(o)
    return lg


def _make(name, fn, role="part", budget=1000, temp=False):
    t0 = time.time()
    o = _new(name, fn, role, budget, temp=temp)
    lg = _post(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


# ---- checks ---------------------------------------------------------------------------------------------------------------
_PDIRS = (Vector((1.0, 0.0131, 0.0217)).normalized(), Vector((-0.0173, 1.0, 0.0119)).normalized(),
          Vector((0.0109, -0.0207, 1.0)).normalized())


def _parity_in(tree, p):
    """Ray parity (m046 / m047): inside a closed shell if at least two of three skewed rays cross it an odd number of
    times."""
    votes = 0
    for d in _PDIRS:
        n, q = 0, p.copy()
        for _ in range(64):
            h = tree.ray_cast(q, d, 1000.0)
            if h[0] is None:
                break
            n += 1
            q = h[0] + d * 1e-4
        votes += n % 2
    return votes >= 2


def _shells(o):
    """bmesh, shell id per face, shell count, faces per shell, and (kind, name) per shell matched to the register."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    groups = [[] for _ in range(n)]
    for f in bm.faces:
        groups[ids[f.index]].append(f)
    off = Vector(o[OFF]) if OFF in o else Vector()
    reg = [(k, nm, Vector(c)) for k, nm, c in json.loads(o.get("m067_pieces", "[]"))]
    labels, used = [], set()
    for fs in groups:
        vs = list({v for f in fs for v in f.verts})
        c = sum((v.co for v in vs), Vector()) / len(vs) + off
        best = min(((i, (rc - c).length) for i, (_, _, rc) in enumerate(reg) if i not in used),
                   key=lambda x: x[1], default=(None, 0))
        if best[0] is not None and best[1] < 0.02:
            used.add(best[0])
            labels.append(reg[best[0]][:2])
        else:
            labels.append(("?", "?"))
    return bm, ids, n, groups, labels


def _fmin(f):
    """Smallest corner angle of a face (radians)."""
    vs = [v.co for v in f.verts]
    m = len(vs)
    out = math.pi
    for i in range(m):
        e1, e2 = vs[i - 1] - vs[i], vs[(i + 1) % m] - vs[i]
        if e1.length > 1e-9 and e2.length > 1e-9:
            out = min(out, e1.angle(e2))
    return out


def thin_report(o, lim=3.0):
    """Faces with a corner under lim degrees, and the smallest corner on the mesh (quads as built)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    angs = [_fmin(f) for f in bm.faces]
    nonplanar = sum(1 for f in bm.faces if len(f.verts) == 4 and
                    abs((f.verts[3].co - f.verts[0].co).dot((f.verts[1].co - f.verts[0].co).cross(
                        f.verts[2].co - f.verts[0].co).normalized())) > 1e-4)
    bm.free()
    return {"under": sum(1 for x in angs if x < math.radians(lim)), "min_deg": round(math.degrees(min(angs)), 2),
            "nonplanar_quads": nonplanar}


def shells_report(o):
    """Per shell: kind, name, tris, non-manifold edges and verts, boundary edges, winding errors (manifold edges whose
    two faces run the same way round), self-intersecting face pairs, signed volume."""
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
        out.append({"kind": labels[k][0], "name": labels[k][1], "tris": sum(len(f.verts) - 2 for f in fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary),
                    "winding_errors": sum(1 for e in es if e.is_manifold and not e.is_contiguous),
                    "self_hits": hits, "volume": round(vol, 5), "parity_out": _parity_check(fs)})
    bm.free()
    return out


def _parity_check(fs):
    """Winding by parity (044's wedge): from each face centre step 0.002 along its normal; the point must be outside
    the shell by ray parity. Returns the number of faces whose normal points inward."""
    vs = list({v for f in fs for v in f.verts})
    vi = {v: i for i, v in enumerate(vs)}
    tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
    bad = 0
    for f in fs:
        if f.calc_area() < 1e-8:
            continue
        p = f.calc_center_median() + f.normal * 0.002
        if _parity_in(tree, p):
            bad += 1
    return bad


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating pieces (STAGES): per shell its nearest gap to another shell (0 where triangles intersect or touch)
    or the ground, and whether it chains by contact to the ground."""
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
    ground = {k for k in range(n) if zmin[k] - z0 <= 0.005}
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
    unch = chained(tol)
    res = {"shells": n, "floating": len(floating), "floating_names": [labels[k][1] for k in floating],
           "worst_gap": round(max([gap[k] for k in range(n)], default=0.0), 4),
           "unchained": len(unch), "unchained_names": unch,
           "on_ground": sorted({labels[k][0] for k in ground}),
           "feet_z": round(z0 + (o[OFF][2] if OFF in o else 0.0), 4),
           "kinds": {k: [lb[0] for lb in labels].count(k) for k in sorted({lb[0] for lb in labels})}}
    bm.free()
    return res


CAT = {"bolt": "iron"}


def bury_report(o):
    """Nothing buried (STAGES): per shell pair, the deepest vert / face centre of one inside the other (ray parity,
    depth to its surface), judged against BURY; shells wholly inside others; the worst sink per kind pair."""
    bm, ids, n, groups, labels = _shells(o)
    info = []
    for s in range(n):
        fs = groups[s]
        vs = list({v for f in fs for v in f.verts})
        idx = {v: i for i, v in enumerate(vs)}
        co = [v.co.copy() for v in vs]
        lo = Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co)))
        hi = Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co)))
        tree = BVHTree.FromPolygons(co, [[idx[v] for v in f.verts] for f in fs])
        info.append({"kind": labels[s][0], "name": labels[s][1], "lo": lo, "hi": hi, "tree": tree,
                     "pts": co + [f.calc_center_median() for f in fs]})
    worst, over, hidden = {}, [], []
    for s, A in enumerate(info):
        inside_any = [False] * len(A["pts"])
        for t, B in enumerate(info):
            if s == t or any(A["hi"][k] < B["lo"][k] - 1e-4 or A["lo"][k] > B["hi"][k] + 1e-4 for k in range(3)):
                continue
            dmax = 0.0
            for j, p in enumerate(A["pts"]):
                if not all(B["lo"][k] - 1e-4 <= p[k] <= B["hi"][k] + 1e-4 for k in range(3)):
                    continue
                d = B["tree"].find_nearest(p)[3]
                if d < 1e-4:
                    continue                                    # on the surface: touching, not inside
                if _parity_in(B["tree"], p):
                    inside_any[j] = True
                    dmax = max(dmax, d)
            if dmax <= 0:
                continue
            pair = (A["kind"], B["kind"])
            worst[pair] = max(worst.get(pair, 0.0), dmax)
            if dmax > BURY + 1e-3:
                over.append({"shell": A["name"], "in": B["name"], "depth": round(dmax, 3)})
        if all(inside_any):
            hidden.append(A["name"])
    bm.free()
    return {"worst_depth": {f"{a_}>{b_}": round(d, 3) for (a_, b_), d in sorted(worst.items())},
            "over_limit": over, "fully_hidden": hidden, "buried": len(over) + len(hidden)}


def _build_tree(o, keep):
    """BVH (build frame) of the shells whose (kind, name) passes keep."""
    bm, ids, n, groups, labels = _shells(o)
    off = Vector(o[OFF])
    cos, polys = [], []
    for k in range(n):
        if not keep(*labels[k]):
            continue
        vs = list({v for f in groups[k] for v in f.verts})
        vi = {v: i + len(cos) for i, v in enumerate(vs)}
        cos += [v.co + off for v in vs]
        polys += [[vi[v] for v in f.verts] for f in groups[k]]
    bm.free()
    return (BVHTree.FromPolygons(cos, polys) if polys else None), cos


def _box_clear(tree, cos, lo, hi, step=0.1):
    """Smallest distance between an axis box (lo, hi) and the geometry: geometry vertices to the box, and points on
    the box's faces to the geometry (0 if a vertex is inside the box)."""
    best = 9.0
    for c in cos:
        d = Vector((max(lo[i] - c[i], 0.0, c[i] - hi[i]) for i in range(3))).length
        best = min(best, d)
    for ax in range(3):
        for side in (lo[ax], hi[ax]):
            u, w = [i for i in range(3) if i != ax]
            nu = max(2, int((hi[u] - lo[u]) / step) + 1)
            nw = max(2, int((hi[w] - lo[w]) / step) + 1)
            for i in range(nu):
                for j in range(nw):
                    p = [0.0, 0.0, 0.0]
                    p[ax] = side
                    p[u] = lo[u] + (hi[u] - lo[u]) * i / (nu - 1)
                    p[w] = lo[w] + (hi[w] - lo[w]) * j / (nw - 1)
                    h = tree.find_nearest(Vector(p))
                    if h[0] is not None:
                        best = min(best, h[3])
    return round(best, 3)


def seat_report(o):
    """Spec 2.8: seat plank tops (benches and stool) and the table top level; the knee room under the table for each
    bench seat point (a 1.2 x 1.2 seated-legs box from the seat's front edge toward the table, z 0-1.75: its nearest
    distance to anything of the table); the stored seat points."""
    bm, ids, n, groups, labels = _shells(o)
    off = Vector(o[OFF])
    tops = {}
    for k in range(n):
        kind, name = labels[k]
        if kind != "plank":
            continue
        zt = max(v.co.z for f in groups[k] for v in f.verts) + off.z
        grp = "table" if name.startswith("top_") else "stool" if name.startswith("stool_") else "bench"
        tops.setdefault(grp, []).append(round(zt, 4))
    bm.free()
    tree, cos = _build_tree(o, lambda kind, name: not name.startswith(("bench_", "stool_")))
    knee = {}
    for k, (p, f) in SEATS_PTS.items():
        if "stool" in k:
            continue
        edge = p[1] + f[1] * (SEAT_ROWS[0] + SEAT_ROW_HW)        # the seat's inner edge (toward the table)
        y0, y1 = sorted((edge, edge + f[1] * 1.2))
        knee[k] = _box_clear(tree, cos, (p[0] - 0.6, y0, 0.0), (p[0] + 0.6, y1, 1.75))
    stored = {k: o.get(k) for k in SEATS_PTS if k in o}
    return {"seat_tops": {g: [min(v), max(v)] for g, v in tops.items()}, "knee_clearance": knee,
            "knee_min": min(knee.values()) if knee else None, "stored": stored}


def walk_report(o):
    """Spec 2.8 walk-around: a 2 x 1 x 5.5 proxy walks a loop round the set's footprint at 0.3 from its outline (the
    bbox, expanded): nearest hero surface along the way; plus the gaps a character could stand in."""
    tree, cos = _build_tree(o, lambda kind, name: True)
    xs = [c.x for c in cos]
    ys = [c.y for c in cos]
    x0, x1, y0, y1 = min(xs) - 0.3, max(xs) + 0.3, min(ys) - 0.3, max(ys) + 0.3
    worst = 9.0
    path = []
    for i in range(41):
        t = i / 40
        path += [(x0 - 1.0, y0 + (y1 - y0) * t), (x1 + 1.0, y0 + (y1 - y0) * t),
                 (x0 + (x1 - x0) * t, y0 - 0.5), (x0 + (x1 - x0) * t, y1 + 0.5)]
    for px, py in path:
        for z in (0.1, 1.0, 2.0, 3.0, 4.4, 5.5):
            h = tree.find_nearest(Vector((px, py, z)))
            if h[0] is not None:
                worst = min(worst, h[3] - (1.0 if abs(px - x0 + 1.0) < 1e-6 or abs(px - x1 - 1.0) < 1e-6 else 0.5))
    bench_gap = round(BENCH_Y - (SEAT_ROWS[0] + SEAT_ROW_HW) - (ROWS[0] + ROW_HW), 3)
    stool_gap = round((-TOP_X) - (STOOL_C[0] + STOOL_HL), 3)
    stool_bench_gap = round(-BENCH_HL - (STOOL_C[0] + sleg_c(1, 1, 0.0)[0] + SLEG_H), 3)
    return {"loop_min_clearance": round(worst, 3), "bench_to_top_gap": bench_gap, "stool_to_table_end": stool_gap,
            "stool_to_bench_end": stool_bench_gap}


def placement_report(o):
    """Spec 4.4 shape targets, measured from the build constants and the mesh."""
    out = {"top": [round(2 * TOP_X, 3), round(2 * (ROWS[0] + ROW_HW), 3), TOP_Z1], "plank_t": PLANK_T,
           "leg_splay_deg": round(math.degrees(math.atan2(LEG_FOOT_Y - LEG_TOP_Y, CLEAT_Z0)), 2),
           "trestle_feet_outer_y": round(LEG_FOOT_Y + LEG_HY, 3), "cleat_len": 2 * CLEAT_HY,
           "cross_stub_protrusion": CSTUB_L, "knee_angle": GEO.get("knee_angle"), "diag_angle": GEO.get("diag_angle"),
           "bench": [2 * BENCH_HL, round(2 * (SEAT_ROWS[0] + SEAT_ROW_HW), 3), BENCH_Y],
           "stool": [2 * STOOL_HL, STOOL_ROWS[-1][1] - STOOL_ROWS[0][0]],
           "bench_leg_splay_deg": [BLEG_SPLAY_X, BLEG_SPLAY_Y], "stool_leg_splay_deg": SLEG_SPLAY,
           "bolt_head": [2 * BOLT_H, BOLT_PROUD, BOLT_DOME, BOLT_SINK], "size": [round(d, 3) for d in o.dimensions]}
    return out


# ---- build ---------------------------------------------------------------------------------------------------------------
PARTS = ((TABLE_P, table_all), (TOP_P, top_part), (TRESTLE_P, trestle_part), (CROSS_P, crossbar_part),
         (BENCH_P, bench_part), (STOOL_P, stool_part))
TARGET_SIZE = ((8.75, 0.15), (6.10, 0.12), (2.64, 0.02))   # hero W (X), D (Y), H (Z) +- tolerance (spec 2.7)
HERO_BUDGET = 4000


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m067_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", HERO))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def export_stats(objs):
    """What the exporter's STATS line would report: VFX sockets and glow (Neon) keys (none on this sheet)."""
    out = {}
    for o in objs:
        socks = [c for c in o.children_recursive if c.get("vfx_kind")]
        glow = sorted({m.name[3:] for m in o.data.materials if list(m.get("flintkit_spec", [0, 0, 0]))[2] > 0})
        out[o.name] = {"vfx_sockets": len(socks), "glow_keys": glow}
    return out


def build(render=True, parts=True, close=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn)
            if name in PART_SEATS:
                _store_points(objs[name], PART_SEATS[name])
    h, log["hero"] = _make(HERO, hero_all, "hero", HERO_BUDGET)
    geo = json.loads(json.dumps(GEO, default=lambda v: [round(x, 3) for x in v]))
    _store_points(h, SEATS_PTS)
    off = Vector(h[OFF])
    h["m067_centre"] = [round(x, 4) for x in Vector((0.0, 0.0, 0.0)) - off]
    _cleanup_tmp()
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.2f} x {d.y:.2f} x {d.z:.2f}"
    audits = [M.audit(o) for o in order]
    thin = {o.name: thin_report(o) for o in order}
    shells = {o.name: shells_report(o) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = HERO_BUDGET if o is h else 999
        if au["tris"] > lim:
            problems.append(f"{o.name}: {au['tris']} tris over {lim}")
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "wire_edges", "loose_verts",
                  "zero_area_faces", "ngons", "dup_verts"):
            if au[k]:
                problems.append(f"{o.name}: {k} {au[k]}")
        if au["normals"] != "outward":
            problems.append(f"{o.name}: normals {au['normals']}")
        for i, s in enumerate(shells[o.name]):
            for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "winding_errors", "self_hits",
                      "parity_out"):
                if s[k]:
                    problems.append(f"{o.name} shell {i} ({s['name']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['name']}): not closed outward (volume {s['volume']})")
            if s["kind"] == "?":
                problems.append(f"{o.name} shell {i}: not matched to a built piece")
        if thin[o.name]["nonplanar_quads"]:
            problems.append(f"{o.name}: {thin[o.name]['nonplanar_quads']} non-planar quads")
    contact = {o.name: contact_report(o) for o in order}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: floating {c['floating_names']}, unchained {c['unchained_names']}")
        if abs(c["feet_z"]) > 0.005 and n_ == HERO:
            problems.append(f"{n_}: feet at z {c['feet_z']}")
    bury = {o.name: bury_report(o) for o in order}
    for n_, b in bury.items():
        if b["buried"]:
            problems.append(f"{n_}: buried {b['over_limit']} hidden {b['fully_hidden']}")
    seats = seat_report(h)
    for g, (lo, hi) in seats["seat_tops"].items():
        want = TOP_Z1 if g == "table" else SEAT_Z1
        if lo < want - 0.01 or hi > want + 0.01:
            problems.append(f"{HERO}: {g} plank tops {lo}..{hi} not level at {want}")
    if seats["knee_min"] is None or seats["knee_min"] < 0.10:
        problems.append(f"{HERO}: knee clearance {seats['knee_min']} under 0.10")
    walk = walk_report(h)
    if walk["loop_min_clearance"] < 0.25:
        problems.append(f"{HERO}: walk loop clearance {walk['loop_min_clearance']}")
    place = placement_report(h)
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    winding = {o.name: sum(s["winding_errors"] + s["parity_out"] for s in shells[o.name]) for o in order}
    bowties = {o.name: au["nonmanifold_verts"] for o, au in zip(order, audits)}
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
        if u.get("min_gap") is not None and u["min_gap"] < 0.008:
            problems.append(f"{n_}: UV island gap {u['min_gap']} under 0.008")
    stats = export_stats(order)
    for n_, s in stats.items():
        if s["vfx_sockets"] or s["glow_keys"]:
            problems.append(f"{n_}: sockets / glow on a sheet with none {s}")
    kinds = {}
    for s in shells[HERO]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts", "origin_offset", "transforms_applied")} for au in audits],
           "hero_shells": kinds, "contact": contact, "bury": bury, "seats": seats, "walk": walk, "placement": place,
           "winding": winding, "bowties": bowties, "thin": thin, "log": log, "geo": geo, "problems": problems,
           "uv": uv, "export_stats": stats,
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders -------------------------------------------------------------------------------------------------------------
# spec 2.9: front_sheet (0, 0) and rear_sheet (180, 0) with the stool hidden, side_sheet (90, 0), f34_sheet (-35, 20),
# r34_sheet (145, 20), top_sheet (0, 89.9); floor hidden and a 3x lens in every *_sheet shot
SHEET_VIEWS = {"front_sheet": (0, 0), "side_sheet": (90, 0), "rear_sheet": (180, 0), "f34_sheet": (-35, 20),
               "r34_sheet": (145, 20), "top_sheet": (0, 89.9)}
NOSTOOL = ("front_sheet", "rear_sheet")
VIEW_NAMES = ("front34", "rear34", "front", "side", "rear", "top")
SHEET_LENS = 3.0
PARTS_SHOT = (-20, 15)
SPIN = tuple(range(0, 360, 45))
SPIN_EL = 10


def _long_lens(kit):
    """render_group with a long lens and the studio floor hidden for the *_sheet shots (m033 / m031)."""
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


def _at(o, p):
    return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)


def _linked(o, tag, m):
    c = bpy.data.objects.new(f"{PFX}{tag}", o.data)
    o.users_collection[0].objects.link(c)
    c.matrix_world = m
    return c


def _exploded(objs):
    """Linked copies of the parts laid out like the sheet's Exploded Construction: the top lifted, a trestle at each
    side with the crossbar between them, a bench in front and the stool at the left."""
    by = {o.name: o for o in objs}
    h = objs[0]
    o0 = Matrix.Translation((h.location.x + 40, h.location.y, 0))
    shown = []

    def put(tag, part, loc):
        if part in by:
            shown.append(_linked(by[part], "expl_" + tag, o0 @ Matrix.Translation(loc)))
    put("top", TOP_P, (0.0, 0.6, 4.4))
    put("trestle_l", TRESTLE_P, (-3.6, 0.0, 0.6))
    put("trestle_r", TRESTLE_P, (3.6, 0.0, 0.6))
    put("crossbar", CROSS_P, (0.0, -0.3, 2.3))
    put("bench", BENCH_P, (1.8, -4.6, 0.0))
    put("stool", STOOL_P, (-6.6, -2.6, 0.0))
    bpy.context.view_layer.update()
    return shown


def _seated(h, tag, p, facing):
    """A seated 5.5 proxy at seat point p (build frame) facing `facing`: hips on the seat, thighs forward, lower legs
    down to the floor, torso and head above."""
    a = K.fk().Asset(PFX + tag, "probe", seed=1, tint_var=0.0)
    f = Vector(facing)
    sd = Vector((-f.y, f.x, 0))
    base = Vector(p)

    def box(c0, c1, z0, z1, hw):
        pts = []
        for z in (z0, z1):
            for s, t in ((-1, c0), (1, c0), (1, c1), (-1, c1)):
                q = base + f * t + sd * (s * hw)
                pts.append((q.x, q.y, z))
        _solid(a, pts, [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]], IRON, 0.8)
    box(-0.30, 0.30, base.z + 0.01, base.z + 2.10, 0.50)          # torso
    box(-0.25, 0.25, base.z + 2.10, base.z + 2.95, 0.30)          # head
    box(0.30, 1.05, base.z + 0.02, base.z + 0.40, 0.45)           # thighs
    box(0.75, 1.10, 0.0, base.z + 0.02, 0.40)                     # lower legs
    c = a.finish(collection=h.users_collection[0], mark_asset=False, origin=None)
    c.matrix_world = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
    bpy.context.view_layer.update()
    return c


def _marker(h, at, name):
    """A 5.5-stud character stand-in."""
    a = K.fk().Asset(PFX + name, "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=IRON, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=IRON, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=IRON, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    c.location = _at(h, at)
    bpy.context.view_layer.update()
    return c


def _remove(objs):
    for o in objs:
        me = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(me, bpy.types.Mesh) and me.users == 0:
            bpy.data.meshes.remove(me)


def _nostool(h):
    """The hero without the stool (the sheet's front and rear cells draw none), lined up with the hero."""
    o, _ = _make(PFX + "nostool", hero_nostool, temp=True)
    o.location = h.location + Vector(o[OFF]) - Vector(h[OFF])
    bpy.context.view_layer.update()
    return o


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    ns = _nostool(h)
    markers = [_marker(h, (0.0, -4.6, 0.0), "char"), _seated(h, "sit", *SEATS_PTS["m067_seat_f1"])]
    try:
        extra = {k: ([ns] if k in NOSTOOL else [h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        for o in objs[1:]:
            extra["part_" + o.name.replace(HERO, "").lower()] = ([o], *PARTS_SHOT)
        if shown:
            extra["exploded"] = (shown, -20, 15)
        extra["scale"] = ([h] + markers, -25, 8)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            sheet = M.views(NUM, [h], names=VIEW_NAMES, extra=extra, vfx=False)
            spin = render_spin(h)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet, "spin": spin}
        if close:
            out.update(render_close_ups(objs))
        return out
    finally:
        _remove(shown + markers + [ns])
        M.display(NUM, objs, TITLE)


def render_spin(h):
    """The eight-azimuth contact sheet: az 0, 45 ... 315 at e 10, long lens, floor hidden -> M067_spin.png."""
    kit = K.NS["KIT"]
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    old = kit["CELL"]
    kit["CELL"] = (420, 360)
    try:
        paths = [kit["render_group"]([h], f"{d}/spin{az:03d}_sheet.png", az, SPIN_EL) for az in SPIN]
    finally:
        kit["CELL"] = old
    rows = [kit["hstack"](paths[i:i + 4]) for i in (0, 4)]
    out = f"{d}/M067_spin.png"
    kit["save_px"](kit["vstack"](rows), out)
    return out


def render_close(objs, path, az, el, centre, radius, cell=(480, 400)):
    """A close-up from (az, el), framed on a sphere (centre, radius) (m023 / m031 / m033)."""
    kit = K.NS["KIT"]
    fb = kit["frame_box"]
    c = Vector(centre)
    box = [c + Vector((dx, dy, dz)) * radius for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    kit["frame_box"] = lambda corners, a_, e_: fb(box, a_, e_)
    ground = bpy.data.objects.get("FB_Ground")
    if ground:
        ground.hide_render = el < 0
    old = kit["CELL"]
    kit["CELL"] = cell
    try:
        return kit["render_group"](objs, path, az, el)
    finally:
        kit["CELL"] = old
        kit["frame_box"] = fb
        if ground:
            ground.hide_render = False


def render_cam(objs, path, loc, look, lens=18.0, cell=(560, 420)):
    """A render from a fixed camera (loc looking at look), e.g. from under the table."""
    kit = K.NS["KIT"]
    fb = kit["frame_box"]
    cam = bpy.data.objects["FB_Cam"]
    lens0 = cam.data.lens
    ground = bpy.data.objects.get("FB_Ground")
    loc, look = Vector(loc), Vector(look)
    z0 = objs[0].matrix_world.translation.z

    def fixed(corners, az, el):
        cam.data.shift_x = cam.data.shift_y = 0.0
        cam.location = loc
        cam.rotation_euler = (look - loc).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lens
        if ground:
            ground.location = (loc.x, loc.y, z0)
    kit["frame_box"] = fixed
    old = kit["CELL"]
    kit["CELL"] = cell
    try:
        return kit["render_group"](objs, path, 0, 10)
    finally:
        kit["frame_box"] = fb
        kit["CELL"] = old
        cam.data.lens = lens0


def render_close_ups(objs):
    """join_cu (close-up A: the +X trestle head, cleat end and bolt, crossbar stub), tie_cu (the -X trestle's tie stub
    and peg), plank_cu (close-up B: the top's front-right corner), under_cu (close-up C: from under the table), stool_cu,
    seat (seated proxies at every seat point, front and side), thumb (the f34 at about 140 px)."""
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    h = objs[0]
    out = {}
    out["join_cu"] = render_close([h], f"{d}/join_cu.png", 35, 12, _at(h, (2.45, -0.6, 1.9)), 0.95)
    out["tie_cu"] = render_close([h], f"{d}/tie_cu.png", -40, 14, _at(h, (-2.25, -1.30, 0.65)), 0.75)
    out["plank_cu"] = render_close([h], f"{d}/plank_cu.png", 30, 24, _at(h, (2.65, -1.15, 2.25)), 0.8)
    out["stool_cu"] = render_close([h], f"{d}/stool_cu.png", -35, 20, _at(h, (STOOL_C[0], STOOL_C[1], 0.85)), 1.1)
    out["under_cu"] = render_cam([h], f"{d}/under_cu.png", _at(h, (0.0, -1.1, 0.35)), _at(h, (0.0, 0.3, 2.2)),
                                 lens=13.0)
    sat = [_seated(h, "sit_" + k[-2:], *SEATS_PTS[k]) for k in SEATS_PTS]
    try:
        kit = K.NS["KIT"]
        old = kit["CELL"]
        kit["CELL"] = (480, 360)
        try:
            p1 = kit["render_group"]([h] + sat, f"{d}/seat_front.png", 0, 4)
            p2 = kit["render_group"]([h] + sat, f"{d}/seat_side.png", 90, 4)
        finally:
            kit["CELL"] = old
        path = f"{d}/seat.png"
        kit["save_px"](kit["hstack"]([p1, p2]), path)
        out["seat"] = path
    finally:
        _remove(sat)
    kit = K.NS["KIT"]
    old = kit["CELL"]
    kit["CELL"] = (170, 140)
    try:
        orig, kit["render_group"] = _long_lens(kit)
        try:
            out["thumb"] = kit["render_group"]([h], f"{d}/thumb_sheet.png", -35, 20)
        finally:
            kit["render_group"] = orig
    finally:
        kit["CELL"] = old
    return out


def preview(names=("front_sheet", "side_sheet", "f34_sheet", "r34_sheet", "top_sheet")):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    ns = _nostool(h) if any(n in NOSTOOL for n in names) else None
    kit = K.NS["KIT"]
    orig, kit["render_group"] = _long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([ns] if k in NOSTOOL else [h], *SHEET_VIEWS[k]) for k in names},
                       vfx=False)
    finally:
        kit["render_group"] = orig
        if ns:
            _remove([ns])


# ---- measuring renders against the sheet (spec 1.2 masks) ---------------------------------------------------------------
def _hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(axis=-1), rgb.min(axis=-1)
    d = mx - mn
    h = np.zeros_like(mx)
    nz = d > 1e-6
    rm = nz & (mx == r)
    gm = nz & (mx == g) & ~rm
    bm_ = nz & ~rm & ~gm
    h[rm] = (60 * ((g[rm] - b[rm]) / d[rm])) % 360
    h[gm] = 60 * ((b[gm] - r[gm]) / d[gm]) + 120
    h[bm_] = 60 * ((r[bm_] - g[bm_]) / d[bm_]) + 240
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def measure(path, box=None):
    """The spec's masks on an image (sheet cell or our render): object bbox W : H, wood lit / mid / shade shares,
    dark (K) share, wood median / lit quartile / shade quartile hex."""
    px = K.NS["KIT"]["load_px"](path)[::-1, :, :3]          # top-down rows
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1]
    rgb = np.clip(px, 0, 1)
    h, s, v = _hsv(rgb)
    W = ((h < 45) | (h > 350)) & (s >= 0.35) & (v >= 0.18)
    Kd = (v < 0.30) & ~W
    warm = ((h < 60) | (h > 330)) & (s >= 0.25) & (v < 0.6)
    obj = W | Kd | warm
    ys, xs = np.nonzero(obj)
    hexs = lambda c: "#" + "".join(f"{int(round(x)):02X}" for x in c)
    w = rgb[W] * 255
    lum = w.mean(axis=1)
    lo, hi = np.percentile(lum, 25), np.percentile(lum, 75)
    vw = v[W]
    return {"bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
            "wh": round((xs.max() - xs.min() + 1) / (ys.max() - ys.min() + 1), 3),
            "lit_mid_shade": [round(100 * float((vw >= 0.85).mean())), round(100 * float(((vw >= 0.55) & (vw < 0.85)).mean())),
                              round(100 * float((vw < 0.55).mean()))],
            "K_pct": round(100 * float(Kd.sum()) / max(1, int(obj.sum())), 1),
            "wood_median": hexs(np.median(w, axis=0)), "wood_lit_q": hexs(np.median(w[lum >= hi], axis=0)),
            "wood_shade_q": hexs(np.median(w[lum <= lo], axis=0)),
            "wood_hue_sat": [round(float(np.median(h[W])), 1), round(float(np.median(s[W])), 2)]}
