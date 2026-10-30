"""052 Boardwalk (references/052.png): a long, level, raised timber walkway on square posts, a chunky handrail along
its back long side and across one end, open along its front long side, and four chunky two-board treads coming down
from the other end. Post centres W 8 across x 3 bays of 9.412 along, deck 32 x 9.5 with its top at 5.6, post tops
9.0, rail 6.85 -> 7.75; overall 37.80 L x 11.06 W x 9.0 H.

    import importlib, kit_models, m052; importlib.reload(kit_models); importlib.reload(m052); m052.build()

Build frame (studs): long axis X, the rail side +Y, the railed end +X, the stairs at -X, the open long side -Y (it
faces the f34 camera), ground z 0, the deck centred on x 0 / y 0. Not symmetric: the hero's origin is its bbox bottom
centre (STAGES), which puts the deck centre at x +2.90 in the object frame (`m052_offset` = (-2.90, 0, 0): object
coordinates + offset = build frame). W08 owns Boardwalk*: names TimberBoardwalk*, keys m052_*.

Seam contract (spec 2.1, binding; repeat it in the export notes):
- ground / leg feet / stair foot z 0, flat;
- deck top (walk surface) z 5.6 +- 0.02, 17 planks across the width, flat (M043 lower lawn, M048 / M050 / M051 decks);
- open long side y -4.75 (the plank ends): nothing above the deck between the corner posts except the rope tail lying
  on the planks at x 10.2 .. 13.3;
- railed long side +Y (rail on the post line y +4.0); railed end +X (deck end x +16.0, end rail on x +14.118);
- stairs end -X: deck end x -16.0, stairs x -15.96 .. -21.80, y +-4.0, four treads (risers 1.12, treads 1.46);
- sides: blocks to y +-5.25, bolt heads to +-5.53, rail stubs to +-5.10;
- post centres y +-4.0; x +-4.706, +-14.118 (the W 8 route width of M048 / M050).

Every piece is its own closed shell (no booleans), seated by contact or sunk 0.02 into what carries it:
- 6 full-height rail posts (cap chamfer 0.10, a brass peg dot inset in the cap) and 2 support posts under the open
  side's middle; 12 bolt blocks (every post's outer long face, the 4 corner posts' end faces) with brass hex bolts;
- 2 side beams on the posts' inner faces, 4 crossbeams on the post rows, 2 end headers;
- 17 crisp planks (1.742 wide, 0.14 gaps, 0.85 thick), the 8 at the rail-post rows notched round the posts;
- back rail (3 planks) and end rail butted into the post faces, 4 rail-end stubs;
- braces: 4 end V braces, 8 long-side knee braces, 2 X braces (4 boards) with a bolt at each crossing;
- stairs: 4 treads of two boards on 2 cut (sawtooth) stringers;
- a twisted orange-amber rope tie on the near-right corner post, its tail lying on the deck, ending in a knob.
Parts (key labels): TimberBoardwalkRailPost, TimberBoardwalkSupportPost, TimberBoardwalkRailPlank,
TimberBoardwalkFloorPlank, TimberBoardwalkStairs, TimberBoardwalkCrossbeam, TimberBoardwalkBrace.

Stages 5-6: nothing (decision 10: the sheet shows no water, glow, light or effect). See M052_spec.md.
Geometry helpers are imported from m048 (committed); no m048 constants, nothing from m050 / m051.
"""
import math
import os
import random
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M
import m012
import m033
import m040
from m048 import _solid, _brace_quad, _tube, _knob, _tri_ngons, winding_report

NUM, TITLE, SHEET = 52, "Boardwalk", "M052"
OFF = "m052_offset"
PFX = "_m052_"
HERO = "TimberBoardwalk"
RPOST_P, SPOST_P = "TimberBoardwalkRailPost", "TimberBoardwalkSupportPost"
RAIL_P, PLANK_P, STAIRS_P = "TimberBoardwalkRailPlank", "TimberBoardwalkFloorPlank", "TimberBoardwalkStairs"
CROSS_P, BRACE_P = "TimberBoardwalkCrossbeam", "TimberBoardwalkBrace"
PARTS = (RPOST_P, SPOST_P, RAIL_P, PLANK_P, STAIRS_P, CROSS_P, BRACE_P)

# ---- builder constants (decisions 1-6) ------------------------------------------------------------------------------
W = 8.0                 # post centres across (y)
NP = 17                 # planks
DECK_L = 32.0
DECK_X = DECK_L / 2     # 16.0: plank-end faces at x +-16
PITCH = DECK_L / NP     # 1.8824
BAY = 5 * PITCH         # 9.4118
ROWS = (-1.5 * BAY, -0.5 * BAY, 0.5 * BAY, 1.5 * BAY)     # post rows (x)
POST = 1.5
PH = POST / 2
DECK_TOP = 5.6
PLANK_T = 0.85
PLANK_BOT = DECK_TOP - PLANK_T          # 4.75
DECK_Y = 4.75           # plank ends
GAP = 0.14              # plank gaps (the spec's upper limit: a deck of separate blocks, not one slab)
TOP_JIT = 0.015
SINK = 0.02
BEAM_W = 0.9
BEAM_TOP = PLANK_BOT + SINK             # 4.77 (sunk into the planks)
BEAM_BOT = 3.45
BEAM_YO = W / 2 - PH + SINK             # 3.27: side beam outer face (into the posts' inner faces)
BEAM_YI = BEAM_YO - BEAM_W              # 2.37
BEAM_X = DECK_X - SINK                  # 15.98
POST_TOP = 9.0
CAP_CH = 0.10
CAP_LEVELS = (7.75, 8.35)               # cap colour bands above the rail
DOT, DOT_D = 0.44, 0.03                 # brass peg dot inset in the cap
SPOST_TOP = PLANK_BOT + SINK            # 4.77
BLOCK_PROUD, BLOCK_Z = 0.5, (3.52, 4.72)
BOLT_Z = (BLOCK_Z[0] + BLOCK_Z[1]) / 2  # 4.12
RAIL_Z = (6.85, 7.75)
RAIL_T = 0.6
STUB = 0.35
NT = 4
RISER = DECK_TOP / (NT + 1)             # 1.12
TREAD_B, TREAD_GAP, TREAD_T = 0.70, 0.06, 0.75     # chunky boards (the f34 / close-up A treads)
TREAD_D = 2 * TREAD_B + TREAD_GAP       # 1.46
STAIR_Y = 4.0
STAIR_X0 = -DECK_X + SINK + SINK        # -15.96: T1's back face (0.02 into the header / side-beam ends)
STR_Y = (2.60, 3.10)                    # stringers (|y|)
STR_THROAT = 0.60                       # stringer depth under the inner corners (perpendicular)
ROPE_R = 0.20                           # rope circumradius (Ø 0.40: the f34's rope is about a quarter of the post)
ROPE_SIDES = 6
ROPE_IN = ROPE_R * math.cos(math.pi / ROPE_SIDES)
WRAP_Z = 6.45
WRAP_D = PH + ROPE_IN - 0.015           # wrap centreline off the post axis on the flats (flats 0.015 into the shaft)
KNOB_R = 0.24
PINCH = 0.10            # every other rope ring this much thinner: the strand bumps of the twist
STAIRS, END_RAIL, RAIL_SIDES = True, True, ("+Y",)

RAIL_POSTS = [(x, W / 2) for x in ROWS] + [(ROWS[0], -W / 2), (ROWS[3], -W / 2)]
SUPPORT_POSTS = [(ROWS[1], -W / 2), (ROWS[2], -W / 2)]

WOOD, WOOD_LIGHT, WOOD_DEEP, WOOD_DARK = "m052_wood", "m052_wood_light", "m052_wood_deep", "m052_wood_dark"
ROPE, BRASS, MARK = "m052_rope", "m052_brass", "m052_marker"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, metal, low specular). Stage 4 (M052_spec.md "Stage 4"): start M050's timber family, then the
# hero renders (region_report) against the sheet's rendered regions.
PALETTE = {
    WOOD: ("#B26C2B", 0.85, 0.0, True),
    WOOD_LIGHT: ("#D88A40", 0.85, 0.0, True),
    WOOD_DEEP: ("#7E4315", 0.85, 0.0, True),
    WOOD_DARK: ("#5C3018", 0.9, 0.0, True),
    ROPE: ("#AD6F31", 0.95, 0.0, True),
    BRASS: ("#F2CC86", 0.35, 0.4, False),
    MARK: ("#7E7978", 0.7, 0.0, False),
}
# calibration targets (spec 5.4: rendered medians of unshadowed regions on the sheet)
TARGETS = {WOOD: ((0xDE, 0x83, 0x36), "brown"), WOOD_LIGHT: ((0xF2, 0x96, 0x3F), "brown"),
           WOOD_DEEP: ((0x9A, 0x4A, 0x16), "brown"), WOOD_DARK: ((0x65, 0x32, 0x1A), "brown"),
           ROPE: ((0xDA, 0x82, 0x31), "brown"), BRASS: ((0xF6, 0xC8, 0x86), "vivid")}


def palette():
    for k, (hexcol, rough, metal, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, metal=metal, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, metal=metal, low_spec=low)


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS): the dome-rendered hexes (recorded in the spec)."""
    keys = keys or list(TARGETS)
    for k in keys:
        K.fk().material(k)
    try:
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)
        palette()


def _mix(k1, k2, t, step=0.05):
    t = round(max(0.0, min(1.0, t)) / step) * step
    return K.mix_key(k1, k2, round(t, 2))


# colour by role (spec 5.3); position bands are applied per piece below. Never by facing.
def _k_block():
    return _mix(WOOD_DEEP, WOOD, 0.4)


def _k_rail():
    return _mix(WOOD_DEEP, WOOD, 0.5)


def _k_frame():
    return _mix(WOOD_DEEP, WOOD_DARK, 0.35)


def _k_brace():
    return _mix(WOOD_DEEP, WOOD_DARK, 0.6)


GEO = {}


# ---- solid builders ---------------------------------------------------------------------------------------------------
def _rng(seed):
    return random.Random(seed)


def _tint(seed, amp=0.03):
    return 1.0 + _rng(seed).uniform(-amp, amp)


def _texture(a, vs, amp, seed, scale=0.3):
    K.texture(a, vs, amp=amp, scale=scale, jitter=0.0, seed=seed)


def _ext(a, pts2, caps, edges, w0, w1, mapf, key, tint=1.0):
    """A straight prism of a 2D region: pts2 [(u, v)], caps = CCW index lists covering the region (the cap faces),
    edges = the region's boundary as directed CCW index pairs. Extruded from w0 to w1 along the third axis and mapped
    to 3D by mapf(u, v, w). Caps and sides are wound one way by construction (the CCW cap at w1, its reverse at w0,
    each side quad [k, k1, k1', k'] facing out); _solid flips the whole shell if the mapping mirrored it."""
    n = len(pts2)
    pts = [mapf(u, v, w0) for u, v in pts2] + [mapf(u, v, w1) for u, v in pts2]
    faces = [list(reversed(c)) for c in caps] + [[n + i for i in c] for c in caps]
    for i, j in edges:
        faces.append([i, j, n + j, n + i])
    return _solid(a, pts, faces, key, tint)


def _cells(a, xs, ys, keep, z0, z1, key, tint=1.0):
    """A vertical prism over the grid cells (i, j) of breaks xs x ys for which keep(i, j): every cap a quad (no
    slivers, no fan of a non-convex outline), every boundary edge one side quad."""
    cells = [(i, j) for i in range(len(xs) - 1) for j in range(len(ys) - 1) if keep(i, j)]
    idx, pts2 = {}, []

    def vid(i, j):
        if (i, j) not in idx:
            idx[(i, j)] = len(pts2)
            pts2.append((xs[i], ys[j]))
        return idx[(i, j)]
    caps, dir_edges = [], set()
    for i, j in cells:
        q = [vid(i, j), vid(i + 1, j), vid(i + 1, j + 1), vid(i, j + 1)]
        caps.append(q)
        for k in range(4):
            dir_edges.add((q[k], q[(k + 1) % 4]))
    edges = [(u, v) for u, v in dir_edges if (v, u) not in dir_edges]
    return _ext(a, pts2, caps, edges, z0, z1, lambda u, v, w: (u, v, w), key, tint)


def _box(a, x0, y0, z0, x1, y1, z1, key, tint=1.0):
    return _cells(a, [x0, x1], [y0, y1], lambda i, j: True, z0, z1, key, tint)


def _earclip(poly):
    """Ear clipping of a simple CCW polygon, best ear (largest smallest angle) first: CCW triangles, no fan."""
    def a2(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    def angles(p, q, r):
        out = []
        for x, y, z in ((p, q, r), (q, r, p), (r, p, q)):
            u, v = Vector((y[0] - x[0], y[1] - x[1])), Vector((z[0] - x[0], z[1] - x[1]))
            out.append(math.degrees(u.angle(v)))
        return min(out)
    idx = list(range(len(poly)))
    tris = []
    while len(idx) > 3:
        best = None
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            p, q, r = poly[i0], poly[i1], poly[i2]
            if a2(p, q, r) <= 1e-9:
                continue
            if any(a2(p, q, poly[m]) >= -1e-9 and a2(q, r, poly[m]) >= -1e-9 and a2(r, p, poly[m]) >= -1e-9
                   for m in idx if m not in (i0, i1, i2)):
                continue
            s = angles(p, q, r)
            if best is None or s > best[0]:
                best = (s, k)
        if best is None:
            raise ValueError("ear clipping failed (not a simple CCW polygon)")
        k = best[1]
        tris.append([idx[k - 1], idx[k], idx[(k + 1) % len(idx)]])
        idx.pop(k)
    tris.append(idx)
    return tris


def _slab(a, poly, w0, w1, mapf, key, tint=1.0):
    """A prism of a simple CCW polygon (ear-clipped caps)."""
    area = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly)))
    if area < 0:
        poly = list(reversed(poly))
    n = len(poly)
    return _ext(a, poly, _earclip(poly), [(k, (k + 1) % n) for k in range(n)], w0, w1, mapf, key, tint)


def _plank2d(a, quad, w0, w1, axis, key, tint=1.0):
    """A board of 2D outline quad [(u, z)] extruded between w0 and w1 along x ("x": u runs along y) or y."""
    if axis == "x":
        return _slab(a, quad, w0, w1, lambda u, v, w: (w, u, v), key, tint)
    return _slab(a, quad, w0, w1, lambda u, v, w: (u, w, v), key, tint)


BOLT_R, BOLT_H, BOLT_DOME = 0.36, 0.24, 0.08


def _bolt(a, c, n, key=BRASS, tint=1.0, sides=6):
    """A brass hex bolt head on a face: centre c on the face, outward normal n; sunk 0.03, BOLT_H proud, a low dome
    (BOLT_DOME) to a centre point (m048._bolt with this sheet's larger head: the f34 / close-up A heads are about
    0.45 of the post's width)."""
    c, n = Vector(c), Vector(n).normalized()
    u = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = (u - u.dot(n) * n).normalized()
    v = n.cross(u)
    ring = [u * math.cos(2 * math.pi * (k + 0.5) / sides) + v * math.sin(2 * math.pi * (k + 0.5) / sides)
            for k in range(sides)]
    pts = [c - n * 0.03 + d * BOLT_R for d in ring] + [c + n * BOLT_H + d * BOLT_R for d in ring]
    pts.append(c + n * (BOLT_H + BOLT_DOME))
    faces = [list(reversed(range(sides)))]
    for k in range(sides):
        k1 = (k + 1) % sides
        faces.append([k, k1, sides + k1, sides + k])
        faces.append([sides + k, sides + k1, 2 * sides])
    return _solid(a, pts, faces, key, tint)


# ---- posts and blocks ---------------------------------------------------------------------------------------------------
LEG_LIFT = (2.85, BEAM_BOT)             # leg bands: 20 % toward wood below 2.85, 10 % up to the beam bottom


def _post_colour(a, fs):
    """Posts by face-centre height only: wood_deep from the beams to the rail top; the legs a touch LIGHTER below the
    beams (20 / 10 % toward wood: the sheet's front / side legs are the post faces' colour or lighter, spec 3.10, and
    the studio's under-deck shade darkens them; M048 finding 7); 20 / 40 % toward wood_light up the cap and 60 % on the
    chamfer and top. Never by facing."""
    for f in fs:
        z = f.calc_center_median().z
        if z < LEG_LIFT[0]:
            k = _mix(WOOD_DEEP, WOOD, 0.2)
        elif z < LEG_LIFT[1]:
            k = _mix(WOOD_DEEP, WOOD, 0.1)
        elif z < CAP_LEVELS[0]:
            k = WOOD_DEEP
        elif z < CAP_LEVELS[1]:
            k = _mix(WOOD_DEEP, WOOD_LIGHT, 0.2)
        elif z < POST_TOP - CAP_CH - 1e-4:
            k = _mix(WOOD_DEEP, WOOD_LIGHT, 0.45)
        else:
            k = _mix(WOOD_DEEP, WOOD_LIGHT, 0.75)
        f.material_index = a._mi(k)


def _post_solid(a, px, py, levels, top, cap):
    """A 1.5-square post prism: rings at `levels`; with cap, a 0.10 chamfer to `top` and a brass peg dot inset 0.03 in
    the top (a frame of 4 quads round the dot, 4 dot walls, the dot floor); without, a flat top at `top`."""
    sq = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    rings = [[(px + sx * PH, py + sy * PH, z) for sx, sy in sq] for z in levels]
    if cap:
        ti = PH - CAP_CH
        rings.append([(px + sx * ti, py + sy * ti, top) for sx, sy in sq])
        rings.append([(px + sx * DOT / 2, py + sy * DOT / 2, top) for sx, sy in sq])
        rings.append([(px + sx * DOT / 2, py + sy * DOT / 2, top - DOT_D) for sx, sy in sq])
    else:
        rings.append([(px + sx * PH, py + sy * PH, top) for sx, sy in sq])
    pts = [p for r in rings for p in r]
    nr = len(levels) + 1                      # rings joined by side / chamfer quads
    faces = [[3, 2, 1, 0]]
    for i in range(nr - 1):
        for k in range(4):
            k1 = (k + 1) % 4
            faces.append([i * 4 + k, i * 4 + k1, (i + 1) * 4 + k1, (i + 1) * 4 + k])
    if cap:
        o, d, f = 4 * (nr - 1), 4 * nr, 4 * (nr + 1)      # cap top outer ring, dot rim, dot floor
        for k in range(4):
            k1 = (k + 1) % 4
            faces.append([o + k, o + k1, d + k1, d + k])    # cap frame (faces up)
            faces.append([d + k, d + k1, f + k1, f + k])    # dot walls (face the dot centre)
        faces.append([f, f + 1, f + 2, f + 3])             # dot floor
    else:
        o = 4 * (nr - 1)
        faces.append([o, o + 1, o + 2, o + 3])
    return pts, faces


def rail_post_shell(a, px, py, seed):
    """A 1.5-square post, ground to a 9.0 cap with a 0.10 chamfer and a 0.44 brass peg dot inset 0.03 in its top."""
    levels = [0.0, LEG_LIFT[0], LEG_LIFT[1], CAP_LEVELS[0], CAP_LEVELS[1], POST_TOP - CAP_CH]
    pts, faces = _post_solid(a, px, py, levels, POST_TOP, True)
    vs, fs = _solid(a, pts, faces, WOOD_DEEP, _tint(seed))
    _post_colour(a, fs)
    for fc in fs:
        c = fc.calc_center_median()
        if c.z > POST_TOP - DOT_D - 1e-4 and abs(c.x - px) < DOT / 2 + 1e-4 and abs(c.y - py) < DOT / 2 + 1e-4:
            fc.material_index = a._mi(BRASS)
    _texture(a, vs, 0.03, seed)
    return vs


def support_post_shell(a, px, py, seed):
    pts, faces = _post_solid(a, px, py, [0.0, LEG_LIFT[0], LEG_LIFT[1]], SPOST_TOP, False)
    vs, fs = _solid(a, pts, faces, WOOD_DEEP, _tint(seed))
    _post_colour(a, fs)
    _texture(a, vs, 0.03, seed)
    return vs


def block(a, px, py, n, seed):
    """A bolt block on the post face with outward normal n (sunk 0.02), the post's width along the face, 1.2 tall,
    0.5 proud; a brass hex bolt head centred on its outer face."""
    nx, ny = n
    z0, z1 = BLOCK_Z
    if nx:
        f = px + nx * PH
        xa, xb = sorted((f - nx * SINK, f + nx * BLOCK_PROUD))
        vs, _ = _box(a, xa, py - PH, z0, xb, py + PH, z1, _k_block(), _tint(seed))
        c = (f + nx * BLOCK_PROUD, py, BOLT_Z)
    else:
        f = py + ny * PH
        ya, yb = sorted((f - ny * SINK, f + ny * BLOCK_PROUD))
        vs, _ = _box(a, px - PH, ya, z0, px + PH, yb, z1, _k_block(), _tint(seed))
        c = (px, f + ny * BLOCK_PROUD, BOLT_Z)
    _texture(a, vs, 0.03, seed)
    bv, _ = _bolt(a, c, (nx, ny, 0), key=BRASS, sides=6)
    return vs + bv


def _block_faces(px, py):
    """Outward normals of the faces carrying a block: the outer long face; also the end face of a corner post."""
    out = [(0, int(math.copysign(1, py)))]
    if abs(abs(px) - ROWS[3]) < 1e-6:
        out.append((int(math.copysign(1, px)), 0))
    return out


def post(a, px, py, seed, rail=True):
    vs = rail_post_shell(a, px, py, seed) if rail else support_post_shell(a, px, py, seed)
    for i, n in enumerate(_block_faces(px, py)):
        vs += block(a, px, py, n, seed + 11 * (i + 1))
    return vs


# ---- framing ------------------------------------------------------------------------------------------------------------
def side_beam(a, sy, seed):
    """A side beam the deck's length (x +-15.98), outer face 0.02 into the posts' inner faces, top 0.02 into the
    planks."""
    y0, y1 = sorted((sy * BEAM_YI, sy * BEAM_YO))
    vs, _ = _box(a, -BEAM_X, y0, BEAM_BOT, BEAM_X, y1, BEAM_TOP, _k_frame(), _tint(seed))
    _texture(a, vs, 0.03, seed)
    return vs


def crossbeam(a, x, seed):
    """A crossbeam on a post row between the side beams (end faces sunk 0.02 into them)."""
    yi = BEAM_YI + SINK
    vs, _ = _box(a, x - BEAM_W / 2, -yi, BEAM_BOT, x + BEAM_W / 2, yi, BEAM_TOP, _k_frame(), _tint(seed))
    _texture(a, vs, 0.03, seed)
    return vs


def header(a, sx, seed):
    """An end header under the end plank's outer edge, flush with the side-beam ends."""
    yi = BEAM_YI + SINK
    x0, x1 = sorted((sx * (BEAM_X - BEAM_W), sx * BEAM_X))
    vs, _ = _box(a, x0, -yi, BEAM_BOT, x1, yi, BEAM_TOP, _k_frame(), _tint(seed))
    _texture(a, vs, 0.03, seed)
    return vs


# ---- deck ---------------------------------------------------------------------------------------------------------------
def plank_x(i):
    x0 = -DECK_X + i * PITCH + GAP / 2
    x1 = -DECK_X + (i + 1) * PITCH - GAP / 2
    if i == 0:
        x0 = -DECK_X
    if i == NP - 1:
        x1 = DECK_X
    return x0, x1


def plank_cells(i):
    """Grid breaks and notch cells of plank i: an open L notch (0.02 clear of the post faces) wherever a rail post
    stands in the plank's row, from the post's inner face to the deck edge."""
    x0, x1 = plank_x(i)
    xs, ys, notches = {x0, x1}, {-DECK_Y, DECK_Y}, []
    for px, py in RAIL_POSTS:
        a_, b_ = px - PH - SINK, px + PH + SINK
        if b_ <= x0 or a_ >= x1:
            continue
        na, nb = max(a_, x0), min(b_, x1)
        ya, yb = (py - PH - SINK, DECK_Y) if py > 0 else (-DECK_Y, py + PH + SINK)
        xs |= {na, nb}
        ys |= {ya, yb}
        notches.append((na, nb, ya, yb))
    ys.add(0.0)                             # the mid-length value step (spec 3.6: the f34's "broken" planks)
    xs, ys = sorted(xs), sorted(ys)

    def keep(ii, jj):
        cx, cy = (xs[ii] + xs[ii + 1]) / 2, (ys[jj] + ys[jj + 1]) / 2
        return not any(na < cx < nb and ya < cy < yb for na, nb, ya, yb in notches)
    return xs, ys, keep, notches


DECK_INFO = {}


def plank(a, i, seed, jitter=True):
    rng = _rng(seed)
    xs, ys, keep, notches = plank_cells(i)
    top = DECK_TOP + (rng.uniform(-TOP_JIT, TOP_JIT) if jitter else 0.0)
    # colour by role (one plank key) and position: one broad lighter field along the deck (35 % toward wood_light,
    # strong enough to see: M050 finding 6), a few deeper planks; per-plank tint (the f34's plank-to-plank values)
    cx = (xs[0] + xs[-1]) / 2
    field = noise.noise(Vector((cx * 0.09, 0.0, 5.3)))
    key = WOOD
    if field > 0.10:
        key = _mix(WOOD, WOOD_LIGHT, 0.35)
    if i in (3, 9, 14):
        key = _mix(WOOD, WOOD_DEEP, 0.15)
    vs, fs = _cells(a, xs, ys, keep, PLANK_BOT, top, key, tint=_tint(seed, 0.04) if jitter else 1.0)
    step = None
    if jitter and rng.random() < 0.7:       # one half of most planks a value step deeper, by position (y side)
        side = 1 if (i + rng.randint(0, 1)) % 2 else -1
        step = _mix(key, WOOD_DEEP, 0.15) if key == WOOD or "light" in key else _mix(WOOD, WOOD_DEEP, 0.3)
        for f in fs:
            if f.calc_center_median().y * side > 1e-4:
                f.material_index = a._mi(step)
    if jitter:
        _texture(a, vs, 0.02, seed)
    DECK_INFO[i] = {"top": round(top, 3), "x": (round(xs[0], 3), round(xs[-1], 3)), "notches": len(notches),
                    "key": key.replace("m052_", ""), "tris": sum(len(f.verts) - 2 for f in fs)}
    return vs


def deck(a, seed=520):
    vs = []
    for i in range(NP):
        vs += plank(a, i, seed + 7 * i)
    return vs


# ---- rails --------------------------------------------------------------------------------------------------------------
def _rail_box(a, x0, y0, x1, y1, seed):
    vs, _ = _box(a, x0, y0, RAIL_Z[0], x1, y1, RAIL_Z[1], _k_rail(), _tint(seed))
    _texture(a, vs, 0.03, seed)
    return vs


def back_rail(a, j, seed):
    """Back rail plank j (0..2) between rail posts on y +4.0."""
    x0 = ROWS[j] + PH - SINK
    x1 = ROWS[j + 1] - PH + SINK
    return _rail_box(a, x0, W / 2 - RAIL_T / 2, x1, W / 2 + RAIL_T / 2, seed)


def end_rail(a, seed):
    x = ROWS[3]
    return _rail_box(a, x - RAIL_T / 2, -W / 2 + PH - SINK, x + RAIL_T / 2, W / 2 - PH + SINK, seed)


def stubs(a, seed):
    """Rail-end stubs: the rail runs' overlap past their end posts (far-left -X face, far-right +X and +Y faces,
    near-right -Y face), sunk 0.02."""
    xl, xr, yc = ROWS[0], ROWS[3], W / 2
    vs = []
    vs += _rail_box(a, xl - PH - STUB, yc - RAIL_T / 2, xl - PH + SINK, yc + RAIL_T / 2, seed)
    vs += _rail_box(a, xr + PH - SINK, yc - RAIL_T / 2, xr + PH + STUB, yc + RAIL_T / 2, seed + 1)
    vs += _rail_box(a, xr - RAIL_T / 2, yc + PH - SINK, xr + RAIL_T / 2, yc + PH + STUB, seed + 2)
    vs += _rail_box(a, xr - RAIL_T / 2, -yc - PH - STUB, xr + RAIL_T / 2, -yc - PH + SINK, seed + 3)
    return vs


# ---- braces -------------------------------------------------------------------------------------------------------------
KNEE_LO_Z, KNEE_HALF, KNEE_T = 1.70, 0.30, 0.45


def _brace(a, quad, w0, w1, axis, seed):
    vs, _ = _plank2d(a, quad, w0, w1, axis, _k_brace(), _tint(seed))
    _texture(a, vs, 0.03, seed)
    return vs


def v_brace(a, sx, sy, seed):
    """End V brace: from the end leg's inner face (y = sy * 3.25) at z 1.70 up to the end crossbeam's underside at
    y = sy * 1.15; 0.45 thick, centred in x on the post row."""
    face = sy * (W / 2 - PH)
    q = _brace_quad((face, KNEE_LO_Z), (sy * 1.15, BEAM_BOT), KNEE_HALF, face + sy * SINK, BEAM_BOT + SINK)
    xc = sx * ROWS[3]
    return _brace(a, q, xc - KNEE_T / 2, xc + KNEE_T / 2, "x", seed)


def knee(a, row, toward, sy, seed):
    """Long-side knee brace: from the leg's face toward `toward` (+-1 in x) at z 1.70 up to the side beam's underside
    1.4 + 0.7 further on; 0.45 thick, centred in y on the leg / beam line (y = sy * 3.25)."""
    face = row + toward * PH
    q = _brace_quad((face, KNEE_LO_Z), (face + toward * 2.10, BEAM_BOT), KNEE_HALF, face - toward * SINK,
                    BEAM_BOT + SINK)
    yc = sy * (W / 2 - PH)
    return _brace(a, q, yc - KNEE_T / 2, yc + KNEE_T / 2, "y", seed)


XB_LO, XB_HI, XB_H, XB_T = 0.45, 3.30, 0.60, 0.35


def _xboard_quad(s):
    """X-brace board in (y, z): its low end on one leg's inner face (sunk 0.02) at z 0.45, its high end on the other
    leg's inner face with its top at 3.30."""
    yc = W / 2 - PH + SINK
    span = 2 * yc
    th = 0.0
    for _ in range(30):
        th = math.atan((XB_HI - XB_LO - XB_H / math.cos(th)) / span)
    hh = XB_H / math.cos(th)
    lo, hi = -s * yc, s * yc
    return [(lo, XB_LO), (hi, XB_HI - hh), (hi, XB_HI), (lo, XB_LO + hh)]


def xbrace(a, row, seed):
    """X brace under a middle post row: two stacked boards between the legs (inside the legs' x range), overlapping
    0.02 at the crossing; a brass hex bolt at the crossing on the outer board (facing the nearer deck end)."""
    sx = 1 if row > 0 else -1
    va = _plank2d_yz(a, _xboard_quad(1), row - sx * (XB_T + 0.01), row + sx * 0.01, seed)
    vb = _plank2d_yz(a, _xboard_quad(-1), row - sx * 0.01, row + sx * (XB_T + 0.01), seed + 1)
    zc = (XB_LO + XB_HI) / 2
    GEO["xbrace_cross_z"] = round(zc, 3)
    bv, _ = _bolt(a, (row + sx * (XB_T + 0.01), 0.0, zc), (sx, 0, 0), key=BRASS, sides=6)
    return va + vb + bv


def _plank2d_yz(a, quad, x0, x1, seed):
    """A board of 2D outline [(y, z)] extruded along x between x0 and x1."""
    x0, x1 = sorted((x0, x1))
    vs, _ = _plank2d(a, quad, x0, x1, "x", _k_brace(), _tint(seed))
    _texture(a, vs, 0.03, seed)
    return vs


def braces(a, seed=440):
    vs = []
    for sx in (1, -1):
        for sy in (1, -1):
            vs += v_brace(a, sx, sy, seed + 3 * sx + sy)
            vs += knee(a, sx * ROWS[3], -sx, sy, seed + 10 + 3 * sx + sy)       # end legs, inward
            vs += knee(a, sx * ROWS[2], -sx, sy, seed + 20 + 3 * sx + sy)       # middle legs, toward the centre
    for row in (ROWS[1], ROWS[2]):
        vs += xbrace(a, row, seed + 40 + int(row > 0))
    return vs


# ---- stairs -------------------------------------------------------------------------------------------------------------
def tread_back(i):
    """Back face x of tread i (1 = top)."""
    return STAIR_X0 - TREAD_D * (i - 1)


def tread_top(i):
    return DECK_TOP - RISER * i


def stair_foot_x():
    return STAIR_X0 - TREAD_D * NT


def stringer_profile():
    """The cut stringer's (x, z) outline, CCW: the ground run, the sloped bottom edge (parallel to the line through
    the notch corners, STR_THROAT below it), the back face (0.02 into the side-beam end), then the sawtooth of seats
    (0.02 into the tread bottoms) and risers down to the foot."""
    seats = [tread_top(i) - TREAD_T + SINK for i in range(1, NT + 1)]
    xf = stair_foot_x()
    slope = RISER / TREAD_D
    corners = [(tread_back(i), seats[i - 1]) for i in range(1, NT + 1)]      # inner corners (seat meets riser)
    dz = STR_THROAT * math.sqrt(1 + slope * slope)

    def bottom(x):
        return corners[-1][1] - dz + (x - corners[-1][0]) * slope
    xg = corners[-1][0] - bottom(corners[-1][0]) / slope                     # where the bottom edge meets z 0
    xb = STAIR_X0
    pts = [(xf, 0.0), (xg, 0.0), (xb, bottom(xb)), (xb, seats[0])]
    for i in range(1, NT):
        x = tread_back(i + 1)
        pts += [(x, seats[i - 1]), (x, seats[i])]
    pts.append((xf, seats[-1]))
    GEO["stringer"] = {"foot": round(xf, 3), "ground_end": round(xg, 3), "back_bottom": round(bottom(xb), 3),
                       "seats": [round(s, 3) for s in seats]}
    return pts


def stringer(a, sy, seed):
    y0, y1 = sorted((sy * STR_Y[0], sy * STR_Y[1]))
    vs, _ = _slab(a, stringer_profile(), y0, y1, lambda u, v, w: (u, w, v), _k_frame(), _tint(seed))
    _texture(a, vs, 0.03, seed)
    return vs


def treads(a, seed=600):
    """Four treads of two 0.70 boards (0.06 gap), 8.0 wide, tops 4.48 / 3.36 / 2.24 / 1.12; T1's back face 0.02 into
    the -X header, the lower treads' back faces 0.01 clear of the risers."""
    vs = []
    for i in range(1, NT + 1):
        xb = tread_back(i) - (0.0 if i == 1 else 0.01)
        xf = tread_back(i) - TREAD_D
        zt = tread_top(i)
        for j, (x0, x1) in enumerate(((xb - TREAD_B, xb), (xf, xf + TREAD_B))):
            v, _ = _box(a, x0, -STAIR_Y, zt - TREAD_T, x1, STAIR_Y, zt, WOOD, _tint(seed + 2 * i + j))
            _texture(a, v, 0.02, seed + 2 * i + j)
            vs += v
    GEO["tread_tops"] = [round(tread_top(i), 3) for i in range(1, NT + 1)]
    return vs


def stairs(a, seed=600):
    vs = treads(a, seed)
    for sy in (1, -1):
        vs += stringer(a, sy, seed + 50 + sy)
    return vs


# ---- rope tie -----------------------------------------------------------------------------------------------------------
RP = (ROWS[3], -W / 2)                  # the near-right corner post


WRAP_RC = 0.24                          # corner bend radius (above the tube radius: no self-overlap at the bends)


def wrap_path():
    """A rounded square round the post: two points on each corner arc (22.5 / 67.5 deg), so the straight runs between
    them lie on the post faces' flats at WRAP_D and every bend turns 45 deg."""
    px, py = RP
    s = WRAP_D - WRAP_RC * math.cos(math.radians(22.5))
    pts = []
    for k in range(4):
        cx, cy = s * (1 if k in (0, 3) else -1), s * (1 if k in (0, 1) else -1)
        for t in (22.5, 67.5):
            ang = math.radians(90 * k + t)
            pts.append((cx + WRAP_RC * math.cos(ang), cy + WRAP_RC * math.sin(ang)))
    return _resample([(px + x, py + y, WRAP_Z) for x, y in pts], ROPE_STEP, True)


TAIL = [(-0.90, 0.10, 6.42), (-1.15, 0.13, 6.32), (-1.50, 0.18, 6.12), (-1.85, 0.24, 5.90), (-2.25, 0.30, 5.76),
        (-2.75, 0.38, 5.71), (-3.35, 0.46, 5.71), (-3.85, 0.52, 5.71)]


ROPE_STEP = 0.36        # rope rings at most this far apart: the twist and its groove strands spiral visibly


def _resample(path, step, closed):
    """Split every segment of a path into equal pieces no longer than `step` (closed paths keep an even count)."""
    P = [Vector(p) for p in path]
    segs = len(P) if closed else len(P) - 1
    out = []
    for i in range(segs):
        a_, b_ = P[i], P[(i + 1) % len(P)]
        n = max(1, math.ceil((b_ - a_).length / step))
        if closed and i == segs - 1 and (len(out) + n) % 2:
            n += 1
        out += [a_.lerp(b_, k / n) for k in range(n)]
    if not closed:
        out.append(P[-1])
    return [tuple(p) for p in out]


def _rope_groove():
    """Strand roles by the strand's place in the twist (never by the face's normal): strands 0 and 3 of six a
    deeper groove (70 % toward wood_deep), so two dark lines spiral round the tube."""
    g = _mix(ROPE, WOOD_DEEP, 0.7)
    return {0: g, 3: g}


def rope_tie(a, seed=700):
    """A twisted ring round the near-right post just under the end rail (inner surface 0.02 into the shaft), a tail
    from inside the ring curving down onto the planks toward -X (sunk ~0.03), and a knob at its end."""
    vs, _ = _tube(a, wrap_path(), ROPE_R, ROPE_SIDES, True, ROPE, groove=_rope_groove(), twist=True,
                  tint=_tint(seed, 0.02), pinch=PINCH)
    px, py = RP
    lie = DECK_TOP + ROPE_R - 0.035         # a ring vertex at most 0.035 (+ plank jitter) into the planks
    path = _resample([(px + x, py + y, lie if z <= 5.71 + 1e-6 else z) for x, y, z in TAIL], ROPE_STEP, False)
    tv, _ = _tube(a, path, ROPE_R, ROPE_SIDES, False, ROPE, groove=_rope_groove(), twist=True,
                  tint=_tint(seed + 1, 0.02), phase=0.4, pinch=PINCH)
    e = Vector(path[-1]) + (Vector(path[-1]) - Vector(path[-2])).normalized() * 0.12
    kv, _ = _knob(a, (e.x, e.y, DECK_TOP + KNOB_R - 0.03), KNOB_R, ROPE, tint=0.98, segs=6, rings=3)
    GEO["rope"] = {"wrap_z": WRAP_Z, "wrap_d": round(WRAP_D, 3), "tail_lie_z": round(lie, 3),
                   "tail_x": (round(path[-1][0], 2), round(path[0][0], 2)), "knob": [round(x, 2) for x in e]}
    return vs + tv + kv


# ---- parts and hero -----------------------------------------------------------------------------------------------------
def rail_post_part(a):
    """One full-height rail post with one block and bolt on its -Y face (the key's post)."""
    post(a, ROWS[1], -W / 2, 101)


def support_post_part(a):
    post(a, ROWS[1], -W / 2, 131, rail=False)


def rail_plank_part(a):
    back_rail(a, 1, 211)


def floor_plank_part(a):
    """One plain plank, square to its axes (no jitter: M050 finding 7)."""
    x0, x1 = -PITCH / 2 + GAP / 2, PITCH / 2 - GAP / 2
    vs, _ = _box(a, x0, -DECK_Y, PLANK_BOT, x1, DECK_Y, DECK_TOP, WOOD)


def stairs_part(a):
    stairs(a)


def crossbeam_part(a):
    crossbeam(a, 0.0, 311)


def brace_part(a):
    """The key's Brace: an L of a 2.4-tall leg piece (1.5 square) and one knee board rising from low on its face."""
    vs, _ = _box(a, -PH, -PH, 0.0, PH, PH, 2.4, WOOD_DEEP, _tint(401))
    face = PH
    q = _brace_quad((face, 0.75), (face + 1.6, 2.4), KNEE_HALF, face - SINK, 2.4)
    _brace(a, q, -KNEE_T / 2, KNEE_T / 2, "y", 402)


def hero_fn(a):
    GEO.clear()
    DECK_INFO.clear()
    for i, (px, py) in enumerate(RAIL_POSTS):
        post(a, px, py, 101 + 17 * i)
    for i, (px, py) in enumerate(SUPPORT_POSTS):
        post(a, px, py, 231 + 17 * i, rail=False)
    for sy in (1, -1):
        side_beam(a, sy, 301 + sy)
    for j, x in enumerate(ROWS):
        crossbeam(a, x, 311 + j)
    for sx in (1, -1):
        header(a, sx, 331 + sx)
    deck(a)
    for j in range(3):
        back_rail(a, j, 211 + j)
    end_rail(a, 221)
    stubs(a, 225)
    braces(a)
    stairs(a)
    rope_tie(a)


NOTES = {
    HERO: "Timber boardwalk (post centres 8 x 28.24, deck 32 x 9.5 with its top at 5.6, posts to 9.0; about 37.8 x "
          "11.1 x 9.0): a raised walkway of 17 chunky orange planks across the width (notched round the rail posts) on "
          "six full-height rail posts and two support posts, side beams, crossbeams and end headers; a chunky rail "
          "(6.85-7.75) along the +Y side and across the +X end, the -Y side open; four two-board treads on cut "
          "stringers down from the -X end (risers 1.12); bolt blocks with brass hex bolts, V / knee / X braces, a "
          "twisted rope tie on the near-right post. Origin at the bbox bottom centre: the deck centre is at x +2.90. "
          "Seams: feet z 0, deck top 5.6, open side y -4.75, deck ends x -16 / +16. No VFX",
    RPOST_P: "Rail Post (reusable): a 1.5-square post, ground to a 9.0 chamfered cap with a brass peg dot, a bolt block "
             "with a brass hex bolt",
    SPOST_P: "Support Post (reusable): a 1.5-square post to 4.77 (under the planks) with a bolt block and hex bolt",
    RAIL_P: "Rail Plank (reusable): a 0.6 x 0.9 rail plank, 7.95 long, butted into the post faces",
    PLANK_P: "Floor Plank (reusable): a 1.74 x 0.85 plank, 9.5 long, crisp edges",
    STAIRS_P: "Stairs (reusable): four 8.0-wide treads of two boards on two cut stringers, risers 1.12, treads 1.46",
    CROSS_P: "Crossbeam (reusable): a 0.9 x 1.32 crossbeam between the side beams",
    BRACE_P: "Brace (reusable): an L of a short leg piece and a knee board",
}
COLLISION = {HERO: "precise", RPOST_P: "hull", SPOST_P: "hull", RAIL_P: "box", PLANK_P: "box", STAIRS_P: "hull",
             CROSS_P: "box", BRACE_P: "hull"}


def _recentre(o):
    bc = m012._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


def _make_plain(name, fn, role="part", budget=1000):
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget,
             collision=COLLISION[name], tint_var=0.0)
    o[OFF] = list(M._build_offset(fn))
    o.location = (0.0, 0.0, 0.0)
    _tri_ngons(o)
    _recentre(o)
    keys = [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]
    for p in o.data.polygons:      # flat timber; the rope smooth-shaded so it reads round, not as faceted collars
        p.use_smooth = keys[p.material_index].startswith(ROPE)
    K.drop_unused_slots(o)
    M.smart_uv(o, **UV)
    lg = {"uv_cut": m012._uv_unfold(o), "bowties": M.fix_bowties(o)}
    return o, lg


# ---- checks -------------------------------------------------------------------------------------------------------------
def _keys(o):
    return [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]


def _kind(ks):
    ks = set(ks)
    if all(k.startswith("m052_rope") for k in ks):
        return "rope"
    if all(k.startswith("m052_brass") for k in ks):
        return "bolt"
    if all(k.startswith("m052_wood") for k in ks):
        return "wood"
    if all(k.startswith(("m052_wood", "m052_brass")) for k in ks):
        return "post"           # a rail post with its brass peg dot inset in the cap
    return "mixed"


def shells_report(o):
    old, old_keys = m040._kind, m040._keys
    m040._kind, m040._keys = _kind, _keys
    try:
        return m040.shells_report(o)
    finally:
        m040._kind, m040._keys = old, old_keys


def contact_report(o, tol=0.03):
    old_keys = m040._keys
    m040._keys = _keys
    try:
        r = m040.contact_report(o, tol=tol)
    finally:
        m040._keys = old_keys
    r["floating_kinds"] = [k.replace("m052_", "") for k in r["floating_kinds"]]
    return r


def _groups(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    groups = {}
    for f in bm.faces:
        groups.setdefault(ids[f.index], []).append(f)
    return bm, groups


def buried_report(o, deep=0.05):
    """Shells buried in others beyond their stated sinks (STAGES; spec 6): for every shell, the share of its verts
    lying more than `deep` inside another shell (ray parity + nearest distance). Lists shells with any such vert."""
    bm, groups = _groups(o)
    keys = _keys(o)
    trees = {}
    for k, fs in groups.items():
        vs = list({v for f in fs for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        trees[k] = (BVHTree.FromPolygons([v.co.copy() for v in vs], [[vi[v] for v in f.verts] for f in fs]),
                    Vector([min(v.co[i] for v in vs) for i in range(3)]), Vector([max(v.co[i] for v in vs) for i in range(3)]))
    out, worst = [], 0.0
    dirs = [Vector((0.31, 0.52, 0.79)).normalized(), Vector((-0.6, 0.27, -0.75)).normalized()]
    for k, fs in groups.items():
        vs = list({v for f in fs for v in f.verts})
        n_deep, dmax = 0, 0.0
        for v in vs:
            p = v.co
            for k2, (t, lo, hi) in trees.items():
                if k2 == k or any(p[i] < lo[i] - 1e-4 or p[i] > hi[i] + 1e-4 for i in range(3)):
                    continue
                inside = True
                for dv in dirs:
                    cnt, x = 0, p.copy()
                    for _ in range(20):
                        h = t.ray_cast(x, dv)
                        if h[0] is None:
                            break
                        cnt += 1
                        x = h[0] + dv * 1e-5
                    inside &= cnt % 2 == 1
                if not inside:
                    continue
                d = t.find_nearest(p)[3]
                if d > deep:
                    n_deep += 1
                    dmax = max(dmax, d)
                    break
        if n_deep:
            kind = _kind({keys[f.material_index] for f in fs})
            out.append({"shell": k, "kind": kind, "deep_verts": n_deep, "of": len(vs), "max_depth": round(dmax, 3)})
            worst = max(worst, dmax)
    bm.free()
    fully = [s for s in out if s["deep_verts"] == s["of"]]
    return {"shells_with_deep_verts": len(out), "fully_buried": len(fully), "worst_depth": round(worst, 3),
            "list": out[:20]}


def levels_report(h):
    """Spec 4.2.3 on the hero mesh (build frame = mesh + offset)."""
    off = Vector(h[OFF])
    keys = _keys(h)
    bm, groups = _groups(h)
    tops, posts, treads_, beams = [], [], [], set()
    above_open = 0
    for k, fs in groups.items():
        vs = {v for f in fs for v in f.verts}
        xs = [v.co.x + off.x for v in vs]
        ys = [v.co.y + off.y for v in vs]
        zs = [v.co.z + off.z for v in vs]
        kind = _kind({keys[f.material_index] for f in fs})
        if kind == "wood" and max(ys) - min(ys) > 9.0 and abs(max(zs) - DECK_TOP) < 0.1 and min(zs) > 4.5:
            tops.append(round(max(zs), 3))
        if kind == "wood" and max(ys) - min(ys) > 7.9 and max(zs) < DECK_TOP - 0.5 and min(xs) < -DECK_X:
            treads_.append(round(max(zs), 3))
        if kind in ("wood", "post") and min(zs) < 0.01 and max(zs) > 4.0 and max(xs) - min(xs) < 1.6:
            posts.append((round(min(zs), 3), round(max(zs), 3)))
        if kind == "wood" and min(zs) > 3.4 and max(zs) < 4.8 and max(zs) > 4.75:
            beams.add((round(min(zs), 3), round(max(zs), 3)))
        # anything above the deck over the open side between the corner posts, other than the rope
        if kind != "rope" and max(zs) > DECK_TOP + 0.05 and min(ys) < -W / 2 + PH and \
                max(xs) > ROWS[0] + PH + 0.05 and min(xs) < ROWS[3] - PH - 0.05:
            above_open += 1
    bm.free()
    return {"plank_tops": sorted(tops), "plank_top_range": [min(tops), max(tops)] if tops else None,
            "tread_tops": sorted(set(treads_), reverse=True), "posts_z": sorted(set(posts)),
            "beam_band": sorted(beams), "open_side_above_deck": above_open, "rope": GEO.get("rope"),
            "stringer": GEO.get("stringer"), "xbrace_cross_z": GEO.get("xbrace_cross_z")}


def walk_report(h):
    """Walkability with downward rays on the hero (build frame): the deck's top over a grid clear of the posts (largest
    step between neighbouring samples), the treads' tops along y = 0 (risers, runs), the clear widths."""
    off = Vector(h[OFF])
    bm = bmesh.new()
    bm.from_mesh(h.data)
    tree = BVHTree.FromBMesh(bm)

    def top(x, y):
        hit = tree.ray_cast(Vector((x, y, 20.0)) - off, Vector((0, 0, -1)))
        return None if hit[0] is None else hit[0].z + off.z
    xs = np.linspace(-DECK_X + 0.05, ROWS[3] - RAIL_T / 2 - 0.05, 301)      # up to the end rail
    ys = np.linspace(-DECK_Y + 0.05, W / 2 - RAIL_T / 2 - 0.05, 41)
    grid = np.full((len(xs), len(ys)), np.nan)
    blocked = 0
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            if any(abs(x - px) < PH + 0.05 and abs(y - py) < PH + 0.05 for px, py in RAIL_POSTS):
                continue
            z = top(x, y)
            if z is None:
                continue
            if z > DECK_TOP + 0.1 and not (x > 10 and y < -3):      # the rope tail lies by the near-right post
                blocked += 1
                continue
            if z > DECK_TOP + 0.1:
                continue
            grid[i, j] = z
    deckz = grid[~np.isnan(grid)]
    # a gap is a hole in the deck (ray falls through to the frame or the ground): neighbour steps between deck tops
    on = (grid > DECK_TOP - 0.1)
    steps = []
    for di, dj in ((1, 0), (0, 1)):
        a_ = grid[:grid.shape[0] - di, :grid.shape[1] - dj]
        b_ = grid[di:, dj:]
        m = on[:on.shape[0] - di, :on.shape[1] - dj] & on[di:, dj:]
        if m.any():
            steps.append(float(np.abs(a_[m] - b_[m]).max()))
    tops = [round(top(x, 0.0) or 0.0, 3) for x in [tread_back(i) - 0.35 for i in range(1, NT + 1)]]
    bm.free()
    on_deck = deckz[deckz > DECK_TOP - 0.1]
    return {"deck_top_min_max": [round(float(on_deck.min()), 3), round(float(on_deck.max()), 3)],
            "deck_largest_step": round(max(steps), 3), "deck_samples": int(on.sum()),
            "deck_obstacles": blocked,
            "tread_tops": tops, "risers": [round(a_ - b_, 3) for a_, b_ in zip([DECK_TOP] + tops, tops)] + [tops[-1]],
            "tread_run": TREAD_D, "stair_width": 2 * STAIR_Y, "flight_deg": round(math.degrees(math.atan(RISER / TREAD_D)), 1),
            "clear_width_open_edge_to_rail": round(DECK_Y + W / 2 - RAIL_T / 2, 2),
            "clear_width_between_corner_posts": round(W - POST, 2)}


# ---- render measurement (the study's masks, spec "Pixel boxes and masks") -----------------------------------------------
SHEET_REF = {
    "f34": {"wh": 1.958, "W": 52.7, "K": 45.2, "Y": 2.1,
            "top": [.20, .32, .71, .65, .67, .69, .71, .81, .75, .78, .80, .82, .91, .86, .89, .91, 1.0, .92, .89, .94,
                    .72]},
    "r34": {"wh": 1.982, "W": 52.8, "K": 45.5, "Y": 1.8,
            "top": [.50, .77, .70, .72, .74, .83, .78, .80, .82, .84, .93, .88, .89, .91, .99, .93, .89, .93, .72, .62,
                    .54]},
    "front": {"wh": 3.288, "W": 40.9, "K": 57.4, "Y": 1.7,
              "top": [.12, .29, .84, .99, .84, .84, .84, .99, .84, .84, .84, .84, .99, .84, .84, .84, .84, .84, .84,
                      .99, .54]},
    "side": {"wh": 1.588, "W": 31.2, "K": 67.5, "Y": 1.2,
             "top": [.58, .84, .99, .99, .89, .79, .79, .79, .79, .79, .79, .79, .79, .79, .79, .79, .89, .99, .99, .85,
                     .58]},
    "rear": {"wh": 2.862, "W": 37.7, "K": 60.7, "Y": 1.5,
             "top": [.54, .99, .84, .84, .84, .84, .84, .84, .99, .84, .84, .84, .84, .92, .99, .84, .84, .84, .84, .99,
                     .55]},
    "top": {"wh": 1.992, "W": 70.3, "K": 28.9, "Y": 0.8},
}


def _hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0)
    return h, s, mx


def classify(px):
    """The study's masks (spec "Pixel boxes and masks"): T, Y, W, K in that order; B / O the rest."""
    h, s, v = _hsv(px)
    T = (v < 0.16) | ((s < 0.25) & (v < 0.35)) | ((h > 200) & (h < 250) & (s > 0.25) & (v < 0.45))
    Y = ~T & (((h >= 36) & (h <= 62) & (s >= 0.18) & (v >= 0.60)) |
              ((h >= 33) & (h < 36) & (s >= 0.18) & (s < 0.62) & (v >= 0.75)))
    Wm = ~T & ~Y & ((h < 40) | (h > 345)) & (s >= 0.35) & (v >= 0.62)
    Km = ~T & ~Y & ~Wm & ((h < 40) | (h > 340)) & (s >= 0.25) & (v >= 0.16)
    B = ~T & ~Y & ~Wm & ~Km & (s < 0.25)
    return Wm, Km, Y, T, B


def measure(path, tol=18 / 255):
    kit = K.NS["KIT"]
    raw = kit["load_px"](path)[::-1]
    px = np.clip(raw[..., :3], 0, 1)
    bg = np.median(np.concatenate([px[:4, :4].reshape(-1, 3), px[:4, -4:].reshape(-1, 3)]), axis=0)
    paper = (np.abs(px - bg).max(-1) <= tol) | (raw[..., 3] < 0.5)
    Wm, Km, Y, T, B = classify(px)
    sil = ~paper & ~T & ~B
    Wm, Km, Y = Wm & sil, Km & sil, Y & sil
    ys, xs = np.nonzero(sil)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    H, Wd = y1 - y0 + 1, x1 - x0 + 1
    tot = max(1, int(Wm.sum() + Km.sum() + Y.sum()))
    res = {"wh": round(Wd / H, 3), "W": round(100 * Wm.sum() / tot, 1), "K": round(100 * Km.sum() / tot, 1),
           "Y": round(100 * Y.sum() / tot, 1)}
    prof = []
    for f in np.linspace(0, 1, 21):
        col = int(x0 + f * (Wd - 1))
        on = np.nonzero(sil[:, col])[0]
        prof.append(round(float((y1 - on.min()) / H), 2) if len(on) else 0.0)
    res["top"] = prof
    rgb = px * 255
    for k, m in (("W", Wm), ("K", Km), ("Y", Y)):
        sel = rgb[m]
        res[k + "_med"] = "#" + "".join(f"{int(x):02X}" for x in np.median(sel, axis=0)) if len(sel) else None
    return res


def measure_views(out_dir=None):
    d = out_dir or f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    res = {}
    for k, f in (("f34", "f34_sheet"), ("r34", "r34_sheet"), ("front", "front_sheet"), ("side", "side_sheet"),
                 ("rear", "rear_sheet"), ("top", "top_sheet")):
        try:
            m = measure(f"{d}/{f}.png")
        except Exception as e:      # noqa: BLE001 - report, don't fail the build
            res[k] = str(e)
            continue
        ref = SHEET_REF[k]
        if "top" in ref:
            err = np.abs(np.array(m["top"]) - np.array(ref["top"]))
            m["top_err_mean"], m["top_err_max"] = round(float(err.mean()), 3), round(float(err.max()), 3)
        m.pop("top", None)
        m["sheet"] = {kk: vv for kk, vv in ref.items() if kk != "top"}
        res[k] = m
    return res


# ---- build --------------------------------------------------------------------------------------------------------------
TARGET_SIZE = ((37.80, 0.4), (11.14, 0.4), (9.0, 0.3))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me is not None and isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m052_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", HERO))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


PART_FNS = ((RPOST_P, rail_post_part), (SPOST_P, support_post_part), (RAIL_P, rail_plank_part),
            (PLANK_P, floor_plank_part), (STAIRS_P, stairs_part), (CROSS_P, crossbeam_part), (BRACE_P, brace_part))


def build_objects(parts=True):
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in PART_FNS:
            objs[name], log[name] = _make_plain(name, fn)
    h, log["hero"] = _make_plain(HERO, hero_fn, role="hero", budget=4000)
    log["deck"] = {str(k): v for k, v in DECK_INFO.items()}
    _cleanup_tmp()
    order = [h] + [objs[n] for n in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    return order, log


def checks(order):
    h = order[0]
    audits = [M.audit(o) for o in order]
    thin = {o.name: m012._thin(o, POLISH_LIM) for o in order}
    shells = {o.name: shells_report(o) for o in order}
    winding = {o.name: winding_report(o) for o in order}
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
        if winding[o.name]["winding_errors"] or winding[o.name]["unpaired_edges"]:
            problems.append(f"{o.name}: winding {winding[o.name]}")
        for i, s in enumerate(shells[o.name]):
            for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "self_hits", "inverted"):
                if s[k]:
                    problems.append(f"{o.name} shell {i} ({s['kind']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['kind']}): not closed outward (volume {s['volume']})")
            if s["kind"] == "mixed":
                problems.append(f"{o.name} shell {i}: mixed materials")
    contact = {o.name: contact_report(o) for o in order if len(shells[o.name]) > 1}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} shells touch nothing within 0.03, {c['unchained']} have no chain "
                            f"of contact to the ground")
    buried = buried_report(h)
    # the rope tail's first ring starts inside the wrap by design (spec 6); anything more is a problem
    deep = [s for s in buried["list"] if s["deep_verts"] > 0.25 * s["of"] or s["kind"] != "rope"]
    if deep or buried["fully_buried"]:
        problems.append(f"{HERO}: buried shells {deep}")
    levels = levels_report(h)
    tr = levels["plank_top_range"]
    if not tr or tr[0] < DECK_TOP - 0.021 or tr[1] > DECK_TOP + 0.021 or len(levels["plank_tops"]) != NP:
        problems.append(f"{HERO}: plank tops {levels['plank_tops']}")
    if levels["open_side_above_deck"]:
        problems.append(f"{HERO}: {levels['open_side_above_deck']} pieces above the deck on the open side")
    walk = walk_report(h)
    if walk["deck_largest_step"] > 0.035:
        problems.append(f"{HERO}: deck step {walk['deck_largest_step']}")
    if any(abs(r - RISER) > 0.02 for r in walk["risers"]):
        problems.append(f"{HERO}: risers {walk['risers']}")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "LWH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 10: none)")
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
    return {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                          "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                          "ngons", "dup_verts", "transforms_applied")} for au in audits],
            "shells": kinds, "winding": winding, "contact": contact, "buried": buried, "levels": levels,
            "walk": walk, "thin": thin, "problems": problems, "uv": uv,
            "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
            "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
            "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order}}


def build(render=True, parts=True, close=True):
    t0 = time.time()
    order, log = build_objects(parts)
    out = checks(order)
    out["log"] = log
    out["build_s"] = round(time.time() - t0, 1)
    if render:
        out["views"] = render_views(order, close=close)
        out["measure"] = measure_views()
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders ------------------------------------------------------------------------------------------------------------
# decision 12: f34_sheet (-46, 14) governs; r34_sheet (134, 15) content only; front_sheet (0, 0) the open -Y side;
# side_sheet (90, 0) the +X end; rear_sheet (180, 0) the +Y side; top_sheet (0, 89.9). Floor hidden on every *_sheet.
SHEET_VIEWS = {"f34_sheet": (-46, 14), "r34_sheet": (134, 15), "front_sheet": (0, 0), "side_sheet": (90, 0),
               "rear_sheet": (180, 0), "top_sheet": (0, 89.9)}
LENS = {"f34_sheet": 3.0, "r34_sheet": 3.0}
SHEET_LENS = 8.0
PARTS_SHOT = (-35, 25)


def _lens(kit):
    orig = kit["render_group"]

    def rg(group, path, azimuth=-22, elevation=20):
        cam = bpy.data.objects["FB_Cam"].data
        lens = cam.lens
        ground = bpy.data.objects.get("FB_Ground")
        gh = ground.hide_render if ground else None
        name = path.rsplit("/", 1)[-1][:-4]
        if name.endswith("_sheet"):
            cam.lens = lens * LENS.get(name, SHEET_LENS)
            if ground:
                ground.hide_render = True
        try:
            return orig(group, path, azimuth, elevation)
        finally:
            cam.lens = lens
            if ground:
                ground.hide_render = gh
    return orig, rg


def _copy(tag, src, m, coll):
    c = bpy.data.objects.new(f"{PFX}{tag}", src.data)
    coll.objects.link(c)
    c.matrix_world = m
    return c


def _frame_of(h):
    return h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded Construction: a rail post and a support post, a group of
    five floor planks lifted, loose rail planks, the crossbeam on two support posts with a brace, the stairs."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    o0 = Matrix.Translation((objs[0].location.x + 80, objs[0].location.y, 0))
    shown = []

    def put(tag, name, d, rot=0.0):
        if name not in by:
            return
        m = Matrix.Translation(Vector(d)) @ Matrix.Rotation(rot, 4, "Z")
        shown.append(_copy(f"expl_{tag}", by[name], o0 @ m, coll))
    put("rpost", RPOST_P, (-14, 6, 2.0))
    for k in range(5):
        put(f"plank{k}", PLANK_P, (-6 + k * PITCH, 4, 6.0))
    for k in range(5):
        put(f"plank_b{k}", PLANK_P, (6 + k * PITCH, 9, 7.5))
    put("rail_a", RAIL_P, (-6, 12, 9.0))
    put("rail_b", RAIL_P, (10, 15, 10.5))
    put("cross", CROSS_P, (4, -4, 4.0), math.pi / 2)
    put("spost_a", SPOST_P, (-1, -4, 0.0))
    put("spost_b", SPOST_P, (9, -4, 0.0))
    put("brace", BRACE_P, (16, -4, 0.0))
    put("stairs", STAIRS_P, (-16, -6, 0.0))
    bpy.context.view_layer.update()
    return shown


def _marker(h, at, tag):
    """A 5.5-stud character stand-in (legs / torso / head)."""
    a = K.fk().Asset(PFX + tag, "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=MARK, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=MARK, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=MARK, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    c.matrix_world = _frame_of(h) @ Matrix.Translation(at)
    bpy.context.view_layer.update()
    return c


def _scale_markers(h):
    """Character stand-ins: on the deck by the open edge and by the rail, on tread T2, on the ground at the stair
    foot."""
    return [_marker(h, (0.0, -2.5, DECK_TOP), "char_deck"), _marker(h, (8.0, 2.4, DECK_TOP), "char_rail"),
            _marker(h, (tread_back(2) - 0.73, 1.0, tread_top(2)), "char_stair"),
            _marker(h, (stair_foot_x() - 1.2, -1.5, 0.0), "char_ground")]


def _close(objs, path, az, el, centre, radius):
    kit = K.NS["KIT"]
    ground = bpy.data.objects.get("FB_Ground")
    orig = kit["render_group"]

    def rg(group, path_, azimuth=-22, elevation=20):
        if ground:
            ground.hide_render = True
        return orig(group, path_, azimuth, elevation)
    kit["render_group"] = rg
    try:
        return m033.render_close(objs, path, az, el, centre, radius)
    finally:
        kit["render_group"] = orig
        if ground:
            ground.hide_render = False


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    markers = _scale_markers(h)
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        for o in objs[1:]:
            extra["part_" + o.name.replace("TimberBoardwalk", "").lower()] = ([o], *PARTS_SHOT)
        if shown:
            extra["exploded"] = (shown, -35, 25)
        extra["scale"] = ([h] + markers, -40, 12)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _lens(kit)
        try:
            sheet = M.views(NUM, [h], extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet}
        if close:
            d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
            fr = _frame_of(h)
            out["stair_cu"] = _close([h], f"{d}/stair_cu.png", -40, 18, fr @ Vector((-17.5, -2.5, 3.6)), 4.2)
            out["under_cu"] = _close([h], f"{d}/under_cu.png", -30, -35, fr @ Vector((-4.7, -1.5, 3.0)), 3.6)
            out["rail_cu"] = _close([h], f"{d}/rail_cu.png", -35, 20, fr @ Vector((14.1, 3.2, 7.4)), 2.2)
            out["bolt_cu"] = _close([h], f"{d}/bolt_cu.png", -25, 6, fr @ Vector((4.7, -5.0, 4.1)), 1.0)
            out["rope_cu"] = _close([h], f"{d}/rope_cu.png", -50, 20, fr @ Vector((12.9, -3.9, 6.0)), 1.6)
            out["xbrace_cu"] = _close([h], f"{d}/xbrace_cu.png", 90, 4, fr @ Vector((4.7, 0.0, 2.2)), 3.6)
        return out
    finally:
        for o in shown + markers:
            me = o.data
            mine = o in markers
            bpy.data.objects.remove(o, do_unlink=True)
            if mine and me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


# spec 5.4 calibration warnings, sampled on our renders at known build-frame points (5 x 5 px medians)
REGIONS = {
    "f34_sheet": {"plank_top": [(-16 + PITCH * (i + 0.5), y, DECK_TOP) for i in range(2, 16, 2) for y in (-2.0, 0.0, 2.0)],
                  "cap_top": [(x - 0.42, 4.0 - 0.42, POST_TOP) for x in ROWS] + [(ROWS[3] - 0.42, -4.42, POST_TOP)],
                  "post_face": [(ROWS[3] - 0.3, -4.75, 8.2), (ROWS[0] - 0.3, -4.75, 8.2)],
                  "leg": [(ROWS[1], -4.75, 1.5), (ROWS[2], -4.75, 1.5)],
                  "tread_top": [(tread_back(i) - 0.35, 0.0, tread_top(i)) for i in range(1, NT + 1)]},
    "front_sheet": {"plank_end": [(-16 + PITCH * (i + 0.5), -4.75, 5.17) for i in range(1, 16, 2)],
                    "post_face": [(ROWS[0], -4.75, 8.0), (ROWS[3], -4.75, 8.0)],
                    "leg": [(x, -4.75, 1.5) for x in ROWS], "rail": [(x, 3.7, 7.3) for x in (-9.4, 0.0, 9.4)],
                    "block": [(x + 0.45, -5.25, 3.8) for x in ROWS], "beam": [(x, -3.27, 4.0) for x in (-9.4, 0.0, 9.4)],
                    "brace": [(3.3, -3.476, 2.2), (-3.3, -3.476, 2.2)]},
    "side_sheet": {"post_face": [(14.87, 4.0, 8.0), (14.87, -4.0, 8.0)], "leg": [(14.87, 4.0, 1.5), (14.87, -4.0, 1.5)]},
    "top_sheet": {"plank_top": [(-16 + PITCH * (i + 0.5), 0.0, DECK_TOP) for i in range(1, 16, 2)],
                  "cap_top": [(x + 0.4, 4.0, POST_TOP) for x in ROWS]},
}
SHEET_REGION = {"f34_sheet": {"plank_top": "#DB8133", "cap_top": "#F59B48", "post_face": "#9C4B16", "leg": "#AE581E",
                              "tread_top": "#E88F40"},
                "front_sheet": {"plank_end": "#C36726", "post_face": "#9D4D19", "leg": "#A2511B", "rail": "#B25D20",
                                "block": "#AF5D1D", "beam": "#7D3D18", "brace": "#602F14"},
                "side_sheet": {"post_face": "#984D1C", "leg": "#9A4E1E"},
                "top_sheet": {"plank_top": "#D87E37", "cap_top": "#CA702A"}}


def region_report(views=None):
    """Render the sheet views again and sample each region (spec 5.4 warnings) against the sheet."""
    from bpy_extras.object_utils import world_to_camera_view
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    sc = bpy.context.scene
    fr = _frame_of(h)
    out = {}
    orig, kit["render_group"] = _lens(kit)
    try:
        for view, regs in REGIONS.items():
            if views and view not in views:
                continue
            az, el = SHEET_VIEWS[view]
            os.makedirs(f"{d}/regions", exist_ok=True)
            path = kit["render_group"]([h], f"{d}/regions/{view}.png", az, el)      # keeps the build's renders
            px = kit["load_px"](path)
            H_, W_ = px.shape[:2]
            cam = bpy.data.objects["FB_Cam"]
            lens0 = cam.data.lens
            cam.data.lens = lens0 * LENS.get(view, SHEET_LENS)
            bpy.context.view_layer.update()
            qs = {name: [world_to_camera_view(sc, cam, fr @ Vector(p)) for p in pts] for name, pts in regs.items()}
            cam.data.lens = lens0
            res = {}
            for name, pts in regs.items():
                cols = []
                for q in qs[name]:
                    cx, cy = int(q.x * W_), int(q.y * H_)
                    box = px[max(0, cy - 2):cy + 3, max(0, cx - 2):cx + 3, :3].reshape(-1, 3)
                    cols.append(np.median(box, axis=0))
                c = np.clip(np.median(np.array(cols), axis=0), 0, 1) * 255
                hexc = "#" + "".join(f"{int(round(x)):02X}" for x in c)
                ref = SHEET_REGION[view].get(name)
                row = {"ours": hexc}
                if ref:
                    rc = np.array([int(ref[i:i + 2], 16) for i in (1, 3, 5)])
                    row["sheet"] = ref
                    row["max_diff"] = int(np.abs(rc - c).max())
                hh, ss, vv = _hsv(c[None] / 255.0)
                row["hsv"] = [round(float(hh[0])), round(float(ss[0]), 2), round(float(vv[0]), 2)]
                res[name] = row
            out[view] = res
    finally:
        kit["render_group"] = orig
    return out


def preview(names=("f34_sheet", "front_sheet", "side_sheet", "top_sheet"), vfx=False, measure_too=True, extra=None):
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = _lens(kit)
    ex = {k: ([h], *SHEET_VIEWS[k]) for k in names if k in SHEET_VIEWS}
    ex.update(extra or {})
    try:
        sheet = M.views(NUM, [h], names=(), extra=ex, vfx=vfx)
    finally:
        kit["render_group"] = orig
    return {"sheet": sheet, "measure": measure_views() if measure_too else None}
