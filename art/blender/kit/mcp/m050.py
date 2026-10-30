"""050 Timber Bridge (references/050.png): a long, level timber trestle footbridge on eight square posts. Post centres
W 8 across x 3 bays of 9.143 along, deck 32.0 long, deck top 5.6, post tops 8.85; overall about 32.0 L x 11.0 W (pegs)
x 8.85 H.

    import importlib, kit_models, m050; importlib.reload(kit_models); importlib.reload(m050); m050.build()

Build frame (studs): long axis X, +Y back, ground z 0, centred on x 0 / y 0, symmetric about both axes, both ends
open. W08 owns Footbridge*: names TimberBridge*, keys m050_*.

Seam contract (spec 2.1, binding):
- leg feet z 0, flat (a water tile's plate; legs pass through the bed and the see-through water like the dock's);
- deck top (walk surface) z 5.6 +- 0.01 on every board, flat (flush with M048's dock deck and M043's lower lawn);
- both ends x +-16.0 (the end boards' outer faces): no rope and no brace above the deck there;
- sides: boards to y +-4.75 (the posts' outer faces), blocks to +-5.25, pegs to +-5.5; nothing past +-5.6;
- post centres y +-4.0, x +-4.571 / +-13.714; under the deck nothing past x +-15.26 (the stringer ends).

Every piece is its own closed shell (no booleans), seated by contact or sunk 0.02 into what carries it:
- 8 posts, ground -> 8.85 (one shell each, cap chamfer 0.10, a flat dark peg dot on the cap); legs darkened by colour
  below the stringers (position only);
- 8 peg blocks (each post's outer long face) with round wooden peg heads;
- 14 crisp full-width boards across the width (2.186 x 0.85, 0.10 gaps, seams on the four post rows); the 8 boards
  that meet a post row are L-notched round the post (open notch to the deck edge, 0.02 clear of the post);
- 2 stringer lines on the post lines (|y| 3.55-4.45, under the plank ends), each a span between every pair of posts
  plus an end stub 0.8 past each end post carrying a peg on its end face (the sheet's stringer end with a peg dot);
  4 crossbeams between each row's posts;
- 4 knee braces in the end bays (end leg's inner face -> stringer underside), an X brace at each end (two stacked
  boards) with a peg at the crossing; nothing at the middle legs;
- rope: 2 wraps per post and 6 swags along the long sides (none across the ends). Both are 6-sided three-ply tubes
  whose ply crowns bulge and whose grooves pinch, the plies spiralling round the tube (a geometric twist), coloured
  golden / amber / deep by ply index (the place in the twist, never by facing).
Parts (key labels): TimberBridgePost (the -X/-Y corner post with its blocks, pegs and wraps), TimberBridgePlank,
TimberBridgeStringer, TimberBridgeCrossbeam, TimberBridgeBrace (a knee brace), TimberBridgeRope (one swag with knob
ends).

Geometry helpers are imported from m048 (Dock, verified); none of its constants. Stages 5-6: nothing (the sheet shows
no water, glow, light or effect). See M050_spec.md.
"""
import math
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
import m048
from m048 import _brace_quad, _catenary, _knob, _plank2d, _prism, _rect, _solid, _tri_ngons, winding_report

NUM, TITLE, SHEET = 50, "Timber Bridge", "M050"
OFF = "m050_offset"
PFX = "_m050_"
HERO = "TimberBridge"
POST_P, PLANK_P, STR_P = "TimberBridgePost", "TimberBridgePlank", "TimberBridgeStringer"
CROSS_P, BRACE_P, ROPE_P = "TimberBridgeCrossbeam", "TimberBridgeBrace", "TimberBridgeRope"
PARTS = (POST_P, PLANK_P, STR_P, CROSS_P, BRACE_P, ROPE_P)

# ---- builder constants (decision 4) ---------------------------------------------------------------------------------
W = 8.0                     # post centres across (y)
NB = 14                     # boards
DECK_X = 16.0               # deck half length: the end boards' outer faces
BOARD = 2 * DECK_X / NB     # 2.2857 board pitch
BAY = 4 * BOARD             # 9.1429 post centres along (x)
GAP = 0.10                  # board gaps (the yaw keeps them 0.08-0.12)
DECK_TOP = 5.6
PLANK_T = 0.85
PLANK_BOT = DECK_TOP - PLANK_T          # 4.75
POST = 1.5
PH = POST / 2
POST_TOP = 8.85
CAP_CH = 0.10
DOT = 0.11                  # cap peg dot half size (flat, coloured)
SINK = 0.02
DECK_Y = W / 2 + PH         # 4.75: the boards' ends = the posts' outer faces
BEAM_W = 0.9
BEAM_BOT = 3.45
BEAM_TOP = PLANK_BOT + SINK             # 4.77 (sunk into the boards)
STR_X = 15.26               # stringer ends (0.8 past the end posts' outer faces)
STR_Y = (3.55, 4.45)                    # stringer |y| (on the post line, 0.3 behind the board ends)
POST_XS = (BAY / 2, 1.5 * BAY)          # 4.571, 13.714
POSTS = [(sx * x, sy * W / 2) for x in POST_XS for sx in (-1, 1) for sy in (-1, 1)]
POSTS.sort()
BLOCK_HALF, BLOCK_PROUD, BLOCK_Z = 0.85, 0.5, (3.50, 4.74)
PEG_R, PEG_H, PEG_DOME, PEG_SIDES = 0.275, 0.19, 0.06, 8
PEG_Z = 4.12
LEG_RINGS = (2.85, 3.15, BEAM_BOT)      # leg blend rings: 50 % dark below 2.85, 2 steps to wood_deep at 3.45
POST_LEVELS = (0.0,) + LEG_RINGS + (POST_TOP - CAP_CH,)
CAP_T = 1.0                 # the cap's chamfer and top toward wood_light (clearly lighter than the boards)

# rope (spec 2.5; decision 6): wraps Ø 0.40, swags Ø 0.45; the crowns bulge `BUMP` and the grooves pinch as much
ROPE_SIDES = 6
WRAP_R, WRAP_BUMP = 0.205, 0.10         # crown 0.226 / groove 0.185: reads 0.38-0.44
SWAG_R, SWAG_BUMP = 0.23, 0.0           # a round cord (the plies are carried by colour): reads 0.43-0.46
WRAP_Z = (7.06, 7.46)
WRAP_D = 0.82               # wrap centreline off the post axis on the flats: sunk 0.13, 0.27 proud (snug, spec 1.1)
WRAP_E = 0.80               # the diagonal ring points (e, e): 0.27 proud of the post corner (radius 1.06)
SWAG_Z = 7.26               # swag ends: between the two wraps, on the wrap centreline
SWAG_LOW = 6.20
SWAG_SEGS = 10
AMBER_T, AMBER2_T, DEEP_T = 0.45, 0.70, 0.85     # strand-band mixes toward rope_dark (by band index)

KNEE_LO_Z, KNEE_HI_X, KNEE_HALF, KNEE_T = 1.10, 1.5 * BAY - PH - 2.6, 0.30, 0.45      # top at x +-10.36
XB_LO, XB_HI, XB_H = 0.45, 3.30, 0.60

WOOD, WOOD_LIGHT, WOOD_DEEP, WOOD_DARK = "m050_wood", "m050_wood_light", "m050_wood_deep", "m050_wood_dark"
ROPE, ROPE_DARK, PEG, MARK = "m050_rope", "m050_rope_dark", "m050_peg", "m050_marker"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, metal, low specular). Stage 4 (M050_spec.md "Stage 4"): calibrated hexes.
PALETTE = {
    WOOD: ("#BB722E", 0.85, 0.0, True),
    WOOD_LIGHT: ("#C57A35", 0.85, 0.0, True),
    WOOD_DEEP: ("#80410F", 0.85, 0.0, True),
    WOOD_DARK: ("#65361A", 0.9, 0.0, True),
    ROPE: ("#EEC677", 0.95, 0.0, True),
    ROPE_DARK: ("#99601A", 0.95, 0.0, True),
    PEG: ("#E8C47E", 0.55, 0.0, False),
    MARK: ("#7E7978", 0.7, 0.0, False),
}
# calibration targets (spec 5.4: rendered medians of unshadowed regions on the sheet)
TARGETS = {WOOD: ((0xDE, 0x83, 0x3B), "brown"), WOOD_LIGHT: ((0xF2, 0x93, 0x3F), "brown"),
           WOOD_DEEP: ((0x8B, 0x3D, 0x10), "brown"), WOOD_DARK: ((0x6F, 0x35, 0x18), "brown"),
           ROPE: ((0xF8, 0xD0, 0x88), "vivid"), ROPE_DARK: ((0xBE, 0x70, 0x19), "vivid"),
           PEG: ((0xF6, 0xD4, 0x8E), "vivid")}


def palette():
    for k, (hexcol, rough, metal, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, metal=metal, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, metal=metal, low_spec=low)


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS)."""
    keys = keys or list(TARGETS)
    for k in keys:
        K.fk().material(k)
    try:
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


def _mix(k1, k2, t, step=0.05):
    t = round(max(0.0, min(1.0, t)) / step) * step
    return K.mix_key(k1, k2, round(t, 2))


def _rng(seed):
    return random.Random(seed)


def _texture(a, vs, amp, seed, scale=0.3):
    K.texture(a, vs, amp=amp, scale=scale, jitter=0.0, seed=seed)


GEO = {}                    # measured levels and counts recorded while building (for the level check)


# ---- solids ---------------------------------------------------------------------------------------------------------
def _box(a, x0, y0, z0, x1, y1, z1, key, tint=1.0):
    return _prism(a, _rect(x0, y0, x1, y1), [z0], z1, 0.0, key, tint)


def _peg(a, c, n, sides=PEG_SIDES):
    """A round wooden peg head on a face: centre c on the face, outward normal n. Sunk 0.03, PEG_H of straight side,
    a low dome (PEG_DOME) to a centre point: 0.25 proud in all."""
    c, n = Vector(c), Vector(n).normalized()
    u = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = (u - u.dot(n) * n).normalized()
    v = n.cross(u)
    ring = [u * math.cos(2 * math.pi * (k + 0.5) / sides) + v * math.sin(2 * math.pi * (k + 0.5) / sides)
            for k in range(sides)]
    pts = [c - n * 0.03 + d * PEG_R for d in ring] + [c + n * PEG_H + d * PEG_R for d in ring]
    pts.append(c + n * (PEG_H + PEG_DOME))
    faces = [list(reversed(range(sides)))]
    for k in range(sides):
        k1 = (k + 1) % sides
        faces.append([k, k1, sides + k1, sides + k])
        faces.append([sides + k, sides + k1, 2 * sides])
    return _solid(a, pts, faces, PEG)


def _advances(N, S, closed):
    """Cumulative spiral advance per ring (0 or 1 side a step). Open: one side every step. Closed: the loop's total
    must be a multiple of S, so a few evenly spread steps don't advance (N 8, S 6: 1 1 1 0 1 1 1 0)."""
    if not closed:
        return list(range(N))
    total = (N // S) * S
    steps = [1 if (j * total) // N != ((j + 1) * total) // N else 0 for j in range(N)]
    adv = [0]
    for st in steps[:-1]:
        adv.append(adv[-1] + st)
    return adv, steps


def _rope(a, path, r, sides, closed, bump, tint=1.0, up=(0, 0, 1), phase=0.0):
    """A low-poly three-ply rope along `path` (sides even). The rings stay aligned (vertex 0 on `up`: a ridge on top,
    never a flat lid), and the ply crowns spiral round them: ring i's vertex k sits on spiral line (k - adv_i), where
    adv_i advances one side a ring. Even lines are crowns (radius r * (1 + bump)), odd lines grooves
    (r * (1 - bump)), so the outline is broken into diagonal facets that follow the twist (a geometric twist, not only
    colour). Quads are split along the spiral line, so the triangles form spiral bands; band b runs from line b to
    b + 1 (ply ((b + 1) mod sides) // 2: a ply = the two bands either side of its crown). A closed loop skips a
    few advances (spread evenly) so the spiral closes on itself with no seam. Bends are mitred so the tube keeps its
    thickness; open tubes get flat end caps (band -1). Returns (verts, faces, band per face)."""
    P = [Vector(p) for p in path]
    N = len(P)
    S = sides
    if closed:
        adv, steps = _advances(N, S, True)
    else:
        adv, steps = _advances(N, S, False), [1] * N
    upv = Vector(up)
    rings = []
    for i in range(N):
        prev = P[i - 1] if closed else P[max(i - 1, 0)]
        nxt = P[(i + 1) % N] if closed else P[min(i + 1, N - 1)]
        tin = (P[i] - prev) if (P[i] - prev).length > 1e-9 else (nxt - P[i])
        tout = (nxt - P[i]) if (nxt - P[i]).length > 1e-9 else tin
        tin, tout = tin.normalized(), tout.normalized()
        T = (tin + tout).normalized()
        U = (upv - upv.dot(T) * T).normalized()
        V = T.cross(U)
        B = tout - tin
        bend = B.length > 1e-6
        if bend:
            B.normalize()
        sc = 1.0 / max(0.5, tin.dot(T)) - 1.0
        ring = []
        for k in range(S):
            ang = phase + 2 * math.pi * k / S
            rad = r * ((1.0 + bump) if (k - adv[i]) % 2 == 0 else (1.0 - bump))
            off = (U * math.cos(ang) + V * math.sin(ang)) * rad
            if bend:
                off += B * off.dot(B) * sc
            ring.append(P[i] + off)
        rings.append(ring)
    pts = [p for rg in rings for p in rg]
    faces, plies = [], []
    segs = N if closed else N - 1
    for i in range(segs):
        j = (i + 1) % N
        for k in range(S):
            a0, a1 = i * S + k, i * S + (k + 1) % S
            b0, b1 = j * S + k, j * S + (k + 1) % S
            faces += [[a0, a1, b1], [a0, b1, b0]]
            band = (k - adv[i]) % S
            plies += [band, (band - steps[i]) % S]
    if not closed:
        faces.append(list(reversed(range(S))))
        faces.append([(N - 1) * S + k for k in range(S)])
        plies += [-1, -1]
    vs, fs = _solid(a, pts, faces, ROPE, tint)
    return vs, fs, plies


def _ply_keys():
    """Rope strand roles by spiral band (spec 5.3: by the band's place in the twist, never by the face's normal).
    Six thin spiral bands, two per ply: golden on bands 0 / 3, light amber on 1, amber on 2 / 4 and the deep groove
    on 5, so the rope reads golden with thin amber and deep twist lines (the sheet's: front swag quartiles #BE7019 /
    #E49530 / #F4C675) rather than three broad ribbons, and the gold share stays on the sheet's."""
    light, amber, deep = _mix(ROPE, ROPE_DARK, AMBER_T), _mix(ROPE, ROPE_DARK, AMBER2_T), _mix(ROPE, ROPE_DARK, DEEP_T)
    return {0: ROPE, 3: ROPE, 1: light, 4: amber, 2: amber, 5: deep, -1: ROPE}


def _colour_rope(a, fs, plies):
    keys = _ply_keys()
    mi = {p: a._mi(k) for p, k in keys.items()}
    for f, p in zip(fs, plies):
        f.material_index = mi[p]


# ---- posts, blocks, pegs ----------------------------------------------------------------------------------------------
def _post_colour(z, top=False, dot=False):
    """Role and position only (by face-centre height, never by facing): wood_deep; legs darker below the stringers
    (50 % dark below 2.85, then 35 / 15 % up to 3.45); the cap lighter (35 % light above the wraps, 60 % on the
    chamfer and top); the cap's peg dot wood_dark."""
    if dot:
        return WOOD_DARK
    if top:
        return _mix(WOOD_DEEP, WOOD_LIGHT, CAP_T)
    if z < LEG_RINGS[0]:
        return _mix(WOOD_DEEP, WOOD_DARK, 0.5)
    if z < LEG_RINGS[1]:
        return _mix(WOOD_DEEP, WOOD_DARK, 0.35)
    if z < LEG_RINGS[2]:
        return _mix(WOOD_DEEP, WOOD_DARK, 0.15)
    return WOOD_DEEP


def post_shell(a, px, py, seed):
    """One post: a 1.5-square prism z 0 -> 8.85 with colour rings, a 0.10 cap chamfer and a flat square peg dot in the
    middle of the cap (4 trapezoids round it: no recess)."""
    poly = _rect(px - PH, py - PH, px + PH, py + PH)
    rings = [[(x, y, z) for x, y in poly] for z in POST_LEVELS]
    ins = [(x + (CAP_CH if x < px else -CAP_CH), y + (CAP_CH if y < py else -CAP_CH)) for x, y in poly]
    rings.append([(x, y, POST_TOP) for x, y in ins])
    dot = [(x, y, POST_TOP) for x, y in _rect(px - DOT, py - DOT, px + DOT, py + DOT)]
    pts = [p for r in rings for p in r] + dot
    R = len(rings)
    faces = [[3, 2, 1, 0]]
    for i in range(R - 1):
        for k in range(4):
            k1 = (k + 1) % 4
            faces.append([i * 4 + k, i * 4 + k1, (i + 1) * 4 + k1, (i + 1) * 4 + k])
    t0, d0 = (R - 1) * 4, R * 4
    for k in range(4):
        k1 = (k + 1) % 4
        faces.append([t0 + k, t0 + k1, d0 + k1, d0 + k])
    faces.append([d0, d0 + 1, d0 + 2, d0 + 3])
    vs, fs = _solid(a, pts, faces, WOOD_DEEP, tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    for i, f in enumerate(fs):           # the last face is the dot (faces keep their list order)
        c = f.calc_center_median()
        f.material_index = a._mi(_post_colour(c.z, top=c.z > POST_TOP - CAP_CH - 1e-4, dot=i == len(fs) - 1))
    _texture(a, vs, 0.03, seed)
    return vs


def _block_faces(px, py):
    """Outward normals of the post faces that carry a peg block: the outer long face (+-Y). (The corner posts' end
    faces carry the stringer end stubs, with their pegs.)"""
    return [(0, math.copysign(1, py))]


def block(a, px, py, n, seed):
    """A peg block (crisp box) sunk 0.02 into the post's outer long face (outward normal n), 1.7 along x, 1.24 tall,
    0.5 proud (the top view's ears; open sky above, outside the board ends), and its peg head centred on the block's
    outer face at z 4.12."""
    nx, ny = n
    key = _mix(WOOD_DEEP, WOOD, 0.15)
    tint = 1.0 + _rng(seed).uniform(-0.03, 0.03)
    f = py + ny * PH
    ya, yb = sorted((f - ny * SINK, f + ny * BLOCK_PROUD))
    z0, z1 = BLOCK_Z
    vs, _ = _box(a, px - BLOCK_HALF, ya, z0, px + BLOCK_HALF, yb, z1, key, tint)
    c = (px, f + ny * BLOCK_PROUD, PEG_Z)
    _texture(a, vs, 0.03, seed)
    pv, _ = _peg(a, c, (nx, ny, 0))
    return vs + pv


def wrap_path(px, py, z):
    """The wrap centreline: an 8-point ring (flat midpoints at WRAP_D, diagonal points at (e, e)) round the post."""
    d, e = WRAP_D, WRAP_E
    pts = [(d, 0.0), (e, e), (0.0, d), (-e, e), (-d, 0.0), (-e, -e), (0.0, -d), (e, -e)]
    return [(px + x, py + y, z) for x, y in pts]


def wrap(a, px, py, z, seed, phase=0.0):
    vs, fs, plies = _rope(a, wrap_path(px, py, z), WRAP_R, ROPE_SIDES, True, WRAP_BUMP,
                          tint=1.0 + _rng(seed).uniform(-0.02, 0.02), phase=phase)
    _colour_rope(a, fs, plies)
    return vs


def post(a, px, py, seed, blocks=True, wraps=True):
    """One post position: the post shell, its peg block(s) with pegs, its two wraps."""
    vs = post_shell(a, px, py, seed)
    if blocks:
        for i, n in enumerate(_block_faces(px, py)):
            vs += block(a, px, py, n, seed + 11 * (i + 1))
    if wraps:
        for i, z in enumerate(WRAP_Z):
            vs += wrap(a, px, py, z, seed + 31 * (i + 1), phase=(0.0, math.pi / 3)[i])
    return vs


# ---- deck -------------------------------------------------------------------------------------------------------------
def board_span(i):
    x0 = -DECK_X + i * BOARD + (GAP / 2 if i > 0 else 0.0)
    x1 = -DECK_X + (i + 1) * BOARD - (GAP / 2 if i < NB - 1 else 0.0)
    return x0, x1


def board_outline(i):
    """Board i (0 at -X): a rectangle across the width (y +-4.75). A board with a post row on one of its x edges gets
    an open L notch at both ends of that edge (|y| 3.23 -> 4.75, to 0.02 clear of the post's face), so the post stands
    in the board row as on the junction close-up. The far edge gets partner points at |y| 3.23 and the caps are cut
    along them into three near-rectangles (no sliver triangles). Returns (CCW poly, notched, (x0, x1), splits)."""
    x0, x1 = board_span(i)
    Y, yb = DECK_Y, W / 2 - PH - SINK
    edge = None
    for px in sorted({p[0] for p in POSTS}):
        if abs(px - x1 - GAP / 2) < 1e-6:
            edge = (1, px - PH - SINK)
        elif abs(px - x0 + GAP / 2) < 1e-6:
            edge = (-1, px + PH + SINK)
    if edge is None:
        return _rect(x0, -Y, x1, Y), False, (x0, x1), []
    s, xn = edge
    if s > 0:   # notch on the +x edge
        poly = [(x0, -Y), (xn, -Y), (xn, -yb), (x1, -yb), (x1, yb), (xn, yb), (xn, Y), (x0, Y), (x0, yb), (x0, -yb)]
        splits = [(2, 9), (5, 8), (2, 5)]
    else:       # notch on the -x edge
        poly = [(xn, -Y), (x1, -Y), (x1, -yb), (x1, yb), (x1, Y), (xn, Y), (xn, yb), (x0, yb), (x0, -yb), (xn, -yb)]
        splits = [(9, 2), (6, 3), (9, 6)]
    return poly, True, (x0, x1), splits


DECK_INFO = {}
DEEP_BOARDS = (3, 7, 11)


def board(a, i, seed, plain=False):
    rng = _rng(seed)
    poly, notched, (x0, x1), splits = board_outline(i)
    if plain:
        poly, notched, splits = _rect(x0, -DECK_Y, x1, DECK_Y), False, []
    top = DECK_TOP + rng.uniform(-0.01, 0.01)
    if not notched:                     # a small yaw on the free boards (<= 0.01 at the ends: gaps 0.08-0.12)
        yaw = math.radians(rng.uniform(-0.12, 0.12))
        cx = (x0 + x1) / 2
        poly = [(cx + (x - cx) * math.cos(yaw) - y * math.sin(yaw), (x - cx) * math.sin(yaw) + y * math.cos(yaw))
                for x, y in poly]
    # colour by role (one board key) and position: a broad lighter field along the deck, a few deeper boards
    field = noise.noise(Vector(((x0 + x1) / 2 * 0.09, 0.0, 3.7)))
    key = WOOD
    if field > 0.10:
        key = _mix(WOOD, WOOD_LIGHT, 0.15)
    if i in DEEP_BOARDS:
        key = _mix(WOOD, WOOD_DEEP, 0.15)
    vs, fs = _prism(a, poly, [PLANK_BOT], top, 0.0, key, tint=1.0 + rng.uniform(-0.03, 0.03), splits=splits)
    _texture(a, vs, 0.02, seed)
    DECK_INFO[i] = {"top": round(top, 3), "notched": notched, "x": (round(x0, 3), round(x1, 3)), "key": key}
    return vs


def deck(a, seed=500):
    vs = []
    for i in range(NB):
        vs += board(a, i, seed + 7 * i)
    return vs


# ---- framing ----------------------------------------------------------------------------------------------------------
def _frame_key():
    return _mix(WOOD_DEEP, WOOD_DARK, 0.35)


def stringer_spans():
    """The stringer line's pieces along x: an end stub past each end post (to x +-15.26) and a span between each pair
    of posts, every piece sunk 0.02 into the post faces it meets."""
    xs = [x for x in ROW]
    spans = [(-STR_X, xs[0] - PH + SINK)]
    for x0, x1 in zip(xs, xs[1:]):
        spans.append((x0 + PH - SINK, x1 - PH + SINK))
    spans.append((xs[-1] + PH - SINK, STR_X))
    return spans


def stringer_piece(a, sy, x0, x1, seed, peg_end=0):
    """One stringer piece on the post line (|y| 3.55 -> 4.45, 0.3 behind the board ends: the dark band under the
    plank ends on the sheet), z 3.45 -> 4.77 (top sunk into the boards). An end stub (peg_end +-1) carries a peg on
    its end face (the sheet's stringer end with a peg dot; the side cell's end blocks)."""
    y0, y1 = sorted((sy * STR_Y[0], sy * STR_Y[1]))
    vs, _ = _box(a, x0, y0, BEAM_BOT, x1, y1, BEAM_TOP, _frame_key(), tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    _texture(a, vs, 0.03, seed)
    if peg_end:
        pv, _ = _peg(a, (peg_end * STR_X, sy * W / 2, PEG_Z), (peg_end, 0, 0))
        vs = vs + pv
    return vs


def stringer(a, sy, seed):
    """The stringer line under one long edge (decision 5 stringers; placed on the post line, see the spec's Stage 1)."""
    vs = []
    spans = stringer_spans()
    for j, (x0, x1) in enumerate(spans):
        end = -1 if j == 0 else (1 if j == len(spans) - 1 else 0)
        vs += stringer_piece(a, sy, x0, x1, seed + 5 * j, peg_end=end)
    return vs


def crossbeam(a, x, seed):
    """A crossbeam at a post row, between the row's two posts (end faces sunk 0.02 into the posts' inner faces)."""
    yi = W / 2 - PH + SINK
    vs, _ = _box(a, x - BEAM_W / 2, -yi, BEAM_BOT, x + BEAM_W / 2, yi, BEAM_TOP, _frame_key(),
                 tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    _texture(a, vs, 0.03, seed)
    return vs


def _brace_key():
    return _mix(WOOD_DEEP, WOOD_DARK, 0.6)


def knee(a, sx, sy, seed):
    """Knee brace in an end bay: from the end leg's inner face (|x| 12.964) at z 1.10 up to the stringer's underside
    at |x| 10.36; 0.6 in its plane, 0.45 thick, centred in y on the post / stringer line (|y| 4.0)."""
    face = sx * (POST_XS[1] - PH)
    q = _brace_quad((face, KNEE_LO_Z), (sx * KNEE_HI_X, BEAM_BOT), KNEE_HALF, face + sx * SINK, BEAM_BOT + SINK)
    yc = sy * W / 2
    vs, _ = _plank2d(a, q, yc - KNEE_T / 2, yc + KNEE_T / 2, "y", _brace_key(),
                     tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    _texture(a, vs, 0.03, seed)
    return vs


def _xboard_quad(s):
    """X-brace board in (y, z): low end on the leg at y = -s * 3.27 (sunk), high end on the other leg, top at 3.30."""
    yc = W / 2 - PH + SINK
    span = 2 * yc
    th = 0.0
    for _ in range(30):                          # solve span * tan(th) + h / cos(th) = hi - lo
        th = math.atan((XB_HI - XB_LO - XB_H / math.cos(th)) / span)
    hh = XB_H / math.cos(th)
    lo_y, hi_y = -s * yc, s * yc
    return [(lo_y, XB_LO), (hi_y, XB_HI - hh), (hi_y, XB_HI), (lo_y, XB_LO + hh)]


def xbrace(a, sx, seed):
    """X brace at an end: two stacked boards between the corner legs (inside the legs' x range), touching at the
    crossing (sunk 0.02); the outer board flush with the legs' end faces, a peg at the crossing on it."""
    xe = POST_XS[1] + PH                         # 14.464 legs' end faces
    xa0, xa1 = sorted((sx * (xe - 0.70), sx * (xe - 0.34)))
    xb0, xb1 = sorted((sx * (xe - 0.36), sx * xe))
    va, _ = _plank2d(a, _xboard_quad(1), xa0, xa1, "x", _brace_key(), tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    vb, _ = _plank2d(a, _xboard_quad(-1), xb0, xb1, "x", _brace_key(), tint=1.0 + _rng(seed + 1).uniform(-0.03, 0.03))
    _texture(a, va, 0.03, seed)
    _texture(a, vb, 0.03, seed + 1)
    zc = (XB_LO + XB_HI) / 2
    pv, _ = _peg(a, (sx * xe, 0.0, zc), (sx, 0, 0))
    GEO["xbrace_cross_z"] = round(zc, 3)
    return va + vb + pv


# ---- rope -------------------------------------------------------------------------------------------------------------
def swag_ends(p0, p1):
    """Swag end points: on the facing wrap flats (the wrap centreline), between the two wraps (z 7.26)."""
    (x0, y0), (x1, y1) = p0, p1
    d = Vector((x1 - x0, y1 - y0, 0)).normalized()
    s = Vector((x0, y0, SWAG_Z)) + d * WRAP_D
    e = Vector((x1, y1, SWAG_Z)) - d * WRAP_D
    return s, e


ROW = sorted({p[0] for p in POSTS})
SWAGS = [((ROW[j], sy * W / 2), (ROW[j + 1], sy * W / 2)) for sy in (-1, 1) for j in range(3)]


def swag(a, p0, p1, seed, knobs=False):
    s, e = swag_ends(p0, p1)
    path = _catenary(s, e, SWAG_LOW, SWAG_SEGS)
    vs, fs, plies = _rope(a, path, SWAG_R, ROPE_SIDES, False, SWAG_BUMP,
                          tint=1.0 + _rng(seed).uniform(-0.02, 0.02), phase=_rng(seed).uniform(0, 1.0))
    _colour_rope(a, fs, plies)
    GEO.setdefault("swag_low", []).append(round(min(p.z for p in path), 3))
    if knobs:
        for p in (path[0], path[-1]):
            kv, _ = _knob(a, p, 0.3, ROPE, tint=0.98)
            vs += kv
    return vs, path


# ---- parts and hero ---------------------------------------------------------------------------------------------------
CORNER = (-POST_XS[1], -W / 2)


def post_part(a):
    post(a, *CORNER, 101)


def plank_part(a):
    board(a, 2, 900, plain=True)


def stringer_part(a):
    x0, x1 = stringer_spans()[1]
    stringer_piece(a, -1, x0, x1, 301)


def cross_part(a):
    crossbeam(a, -POST_XS[0], 311)


def brace_part(a):
    knee(a, -1, -1, 401)


def rope_part(a):
    swag(a, SWAGS[0][0], SWAGS[0][1], 501, knobs=True)


def hero_fn(a):
    GEO.clear()
    for i, (px, py) in enumerate(POSTS):
        post(a, px, py, 101 + 17 * i)
    deck(a)
    for sy in (1, -1):
        stringer(a, sy, 301 + sy)
    for j, x in enumerate(ROW):
        crossbeam(a, x, 311 + j)
    for sx in (1, -1):
        for sy in (1, -1):
            knee(a, sx, sy, 401 + 3 * sx + sy)
        xbrace(a, sx, 431 + sx)
    for j, (p0, p1) in enumerate(SWAGS):
        swag(a, p0, p1, 501 + j)


NOTES = {
    HERO: "Timber bridge (post centres 8 across x 3 bays of 9.14, deck 32 long, top 5.6, posts to 8.85; about 32.0 x "
          "11.0 x 8.85): a level trestle footbridge on eight square posts, fourteen crisp orange boards across the "
          "width (notched round the posts), stringers and crossbeams under the deck, peg blocks with pale-gold wooden "
          "pegs, knee braces in the end bays and an X brace at each end, two twisted rope wraps on every post and six "
          "low twisted swags along the long sides (both ends open). Seams: feet z 0, deck top 5.6 (M048's dock deck, "
          "M043's lower lawn), open ends x +-16. No VFX",
    POST_P: "Post (reusable): a 1.5-square post, ground to an 8.85 chamfered cap with a peg dot, two peg blocks with "
            "wooden pegs and two twisted rope wraps; legs darker below the stringers",
    PLANK_P: "Plank (reusable): one crisp 2.19 x 0.85 x 9.5 deck board",
    STR_P: "Stringer (reusable): a 0.9 x 1.32 stringer span between two posts, 7.7 long",
    CROSS_P: "Crossbeam (reusable): a 0.9 x 1.32 crossbeam between the stringers",
    BRACE_P: "Brace (reusable): a knee brace, ends cut to the leg face and the stringer underside",
    ROPE_P: "Rope Segment (reusable): one sagging three-ply twisted rope swag with round knob ends",
}
COLLISION = {HERO: "precise", POST_P: "hull", PLANK_P: "box", STR_P: "hull", CROSS_P: "hull", BRACE_P: "hull",
             ROPE_P: "none"}


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
    for p in o.data.polygons:
        p.use_smooth = False
    K.drop_unused_slots(o)
    M.smart_uv(o, **UV)
    lg = {"uv_cut": m012._uv_unfold(o), "bowties": M.fix_bowties(o)}
    return o, lg


# ---- checks -------------------------------------------------------------------------------------------------------------
def _keys(o):
    return [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]


def _kind(ks):
    if all(k.startswith("m050_rope") for k in ks):
        return "rope"
    if all(k.startswith("m050_peg") for k in ks):
        return "peg"
    if all(k.startswith("m050_wood") for k in ks):
        return "wood"
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
    r["floating_kinds"] = [k.replace("m050_", "") for k in r["floating_kinds"]]
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


def _inside(tree, p, dirs=((0, 0, 1), (0.31, 0.17, 0.93), (-0.2, 0.4, 0.89))):
    """Ray parity (majority of three directions): is p inside the closed shell `tree`?"""
    votes = 0
    for d in dirs:
        d = Vector(d).normalized()
        q, n = p.copy(), 0
        for _ in range(64):
            hit = tree.ray_cast(q, d)
            if hit[0] is None:
                break
            n += 1
            q = hit[0] + d * 1e-4
        votes += n % 2
    return votes >= 2


def buried_report(o, depth=0.05):
    """STAGES 'no buried dressing': for every peg, rope and small wood shell (blocks, braces, beams), the share of its
    verts more than `depth` inside a post or a board (ray parity + nearest distance). A shell is buried when over half
    of it is. (A wrap's centroid is the post axis, so a centroid test can't be used; wraps are sunk round the post
    corners by design, about a fifth of their verts.) Returns the count and the worst share per kind."""
    keys = _keys(o)
    bm, groups = _groups(o)
    carriers, small = [], []
    for k, fs in groups.items():
        vs = list({v for f in fs for v in f.verts})
        kind = _kind({keys[f.material_index] for f in fs})
        zs = [v.co.z for v in vs]
        ys = [v.co.y for v in vs]
        big = kind == "wood" and ((max(zs) - min(zs) > 8.0) or (max(ys) - min(ys) > 9.0 and max(zs) - min(zs) < 1.0))
        (carriers if big else small).append((k, kind, vs, fs))
    trees = []
    for k, kind, vs, fs in carriers:
        idx = {v: i for i, v in enumerate(vs)}
        trees.append(BVHTree.FromPolygons([v.co.copy() for v in vs], [[idx[v] for v in f.verts] for f in fs]))
    buried, worst = [], {}
    for k, kind, vs, fs in small:
        deep = 0
        for v in vs:
            for t in trees:
                if _inside(t, v.co) and t.find_nearest(v.co)[3] > depth:
                    deep += 1
                    break
        share = deep / len(vs)
        worst[kind] = max(worst.get(kind, 0.0), round(share, 3))
        if share > 0.5:         # most of the shell more than `depth` inside a post or board
            c = sum((v.co for v in vs), Vector()) / len(vs)
            buried.append((k, kind, round(share, 2), [round(x, 2) for x in c]))
    bm.free()
    return {"buried": len(buried), "buried_list": buried[:10], "carriers": len(carriers), "checked": len(small),
            "deep_vert_share_max": worst}


def levels_report(h):
    """Spec 4.2.3 on the hero mesh (build frame = mesh + offset): feet, stringer band, every board top, wrap centres,
    swag lows, post tops; the ends clear of rope across them; the largest step between neighbouring board tops."""
    off = Vector(h[OFF])
    keys = _keys(h)
    bm, groups = _groups(h)
    tops, posts = [], []
    end_rope = 0
    for k, fs in groups.items():
        vs = {v for f in fs for v in f.verts}
        zs = [v.co.z + off.z for v in vs]
        ys = [v.co.y + off.y for v in vs]
        xs = [v.co.x + off.x for v in vs]
        kind = _kind({keys[f.material_index] for f in fs})
        if kind == "wood" and max(ys) - min(ys) > 9.0 and max(zs) - min(zs) < 1.0:
            tops.append((round((min(xs) + max(xs)) / 2, 2), round(max(zs), 3)))
        if kind == "wood" and min(zs) < 0.01 and max(zs) > 8.0:
            posts.append((round(min(zs), 3), round(max(zs), 3)))
        if kind == "rope" and max(ys) - min(ys) > 3.0:
            end_rope += 1           # a rope running across an end
    bm.free()
    tops.sort()
    tz = [t for _, t in tops]
    steps = [abs(tz[i + 1] - tz[i]) for i in range(len(tz) - 1)]
    return {"board_tops": tz, "board_top_range": [min(tz), max(tz)] if tz else None,
            "max_neighbour_step": round(max(steps), 3) if steps else None,
            "posts_z": sorted(set(posts)), "swag_low": GEO.get("swag_low"), "wrap_z": list(WRAP_Z),
            "stringer_band": [BEAM_BOT, BEAM_TOP], "rope_across_ends": end_rope,
            "xbrace_cross_z": GEO.get("xbrace_cross_z")}


# ---- render measurement (the study's W / K / Y masks, spec "Pixel boxes and masks") ------------------------------------
SHEET_REF = {
    "f34": {"wh": 1.670, "W": 41.7, "K": 52.4, "Y": 5.9, "Yfifths": [0.2, 9.4, 33.2, 38.3, 18.9],
            "top": [.38, .61, .55, .57, .61, .66, .79, .73, .74, .76, .80, .92, .85, .84, .86, .89, .99, .79, .79, .89,
                    .71]},
    "r34": {"wh": 1.577, "W": 45.1, "K": 48.8, "Y": 6.0, "Yfifths": [0.6, 13.2, 30.2, 39.3, 16.7],
            "top": [.36, .57, .51, .55, .61, .74, .67, .68, .71, .75, .80, .91, .84, .84, .86, .89, .99, .80, .78, .88,
                    .69]},
    "front": {"wh": 2.825, "W": 44.4, "K": 49.1, "Y": 6.4,
              "top": [.63, .99, .98, .76, .72, .74, .80, .99, .79, .73, .72, .74, .79, .99, .79, .74, .72, .75, .96,
                      .99, .62]},
    "side": {"wh": 1.221, "W": 28.8, "K": 67.1, "Y": 4.2,
             "top": [.61, .63, .99, .99, .98, .81, .79, .77, .75, .74, .74, .74, .75, .76, .79, .82, .96, .99, .99, .86,
                     .61]},
    "rear": {"wh": 2.732, "W": 44.0, "K": 49.9, "Y": 6.2,
             "top": [.63, .99, .98, .77, .74, .75, .81, .99, .80, .74, .72, .73, .79, .99, .86, .74, .73, .76, .96, .99,
                     .63]},
    "top": {"wh": 0.602, "W": 68.9, "K": 30.9, "Y": 0.1},
}


def measure_views(out_dir=None):
    d = out_dir or f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    res = {}
    for k, f in (("f34", "f34_sheet"), ("f34_probe", "f34_probe_sheet"), ("r34", "r34_sheet"), ("front", "front_sheet"),
                 ("side", "side_sheet"), ("rear", "rear_sheet"), ("top", "top_sheet")):
        try:
            m = m048.measure(f"{d}/{f}.png")
        except Exception as e:      # noqa: BLE001 - report, don't fail the build
            res[k] = str(e)
            continue
        ref = SHEET_REF[k.replace("_probe", "")]
        if k == "top":              # the sheet draws the long axis vertical: compare W : L
            m["wh"] = round(1.0 / m["wh"], 3)
        if "top" in ref:
            err = np.abs(np.array(m["top"]) - np.array(ref["top"]))
            m["top_err_mean"], m["top_err_max"] = round(float(err.mean()), 3), round(float(err.max()), 3)
        m.pop("top", None)
        m["sheet"] = {kk: vv for kk, vv in ref.items() if kk != "top"}
        res[k] = m
    return res


# ---- build ------------------------------------------------------------------------------------------------------------
TARGET_SIZE = ((32.0, 0.4), (11.0, 0.4), (8.85, 0.3))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me is not None and isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m050_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", "TimberBridge"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


PART_FNS = ((POST_P, post_part), (PLANK_P, plank_part), (STR_P, stringer_part), (CROSS_P, cross_part),
            (BRACE_P, brace_part), (ROPE_P, rope_part))


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
    if buried["buried"]:
        problems.append(f"{HERO}: {buried['buried']} shells buried > 0.05 inside a post or board")
    levels = levels_report(h)
    tr = levels["board_top_range"]
    if not tr or tr[0] < DECK_TOP - 0.021 or tr[1] > DECK_TOP + 0.021 or len(levels["board_tops"]) != NB:
        problems.append(f"{HERO}: board tops {levels['board_tops']}")
    if levels["max_neighbour_step"] is None or levels["max_neighbour_step"] > 0.02:
        problems.append(f"{HERO}: deck step {levels['max_neighbour_step']} over 0.02")
    if levels["rope_across_ends"]:
        problems.append(f"{HERO}: rope across an end")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "LWH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (the sheet shows none)")
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
            "shells": kinds, "winding": winding, "contact": contact, "buried": buried, "levels": levels, "thin": thin,
            "problems": problems, "uv": uv,
            "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
            "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
            "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order}}


def build(render=True, parts=True):
    t0 = time.time()
    order, log = build_objects(parts)
    out = checks(order)
    out["log"] = log
    out["build_s"] = round(time.time() - t0, 1)
    if render:
        out["views"] = render_views(order)
        out["measure"] = measure_views()
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders ----------------------------------------------------------------------------------------------------------
# decision 12: f34_sheet governs, probed over az -35 / -40 / -45 x e 20 / 23 / 26 and kept the best: (-45, 20) (W : H
# 1.656, shares closest; (-40, 23) gives the same W : H 1.669 with W +10 / K -11). r34_sheet (140, 26); front_sheet
# (0, 0) the -Y side; side_sheet (90, 0) the +X end; rear_sheet (180, 0); top_sheet (0, 89.9). Floor hidden on every
# *_sheet shot. f34_probe (-50, 16): the low camera at which all three f34 shares land in band (spec Stage 4).
SHEET_VIEWS = {"f34_sheet": (-45, 20), "r34_sheet": (140, 26), "front_sheet": (0, 0), "side_sheet": (90, 0),
               "rear_sheet": (180, 0), "top_sheet": (0, 89.9)}
LENS = {"f34_sheet": 3.0, "r34_sheet": 3.0, "f34_probe_sheet": 3.0}
PROBE_VIEW = (-50, 16)
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
    """Copies of the parts laid out like the sheet's Exploded Construction: the 14 planks lifted above the frame, the
    corner posts pulled outward (each turned so its blocks face out), the stringers pulled apart below the deck, the
    crossbeams lower, the braces by the end legs, two rope segments above the posts."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    o0 = Matrix.Translation((objs[0].location.x, objs[0].location.y + 40, 0))
    shown = []

    def put(tag, name, d, rot=0.0, pivot=None):
        if name not in by:
            return
        o = by[name]
        m = Matrix.Translation(Vector(o[OFF]))
        if rot:
            p = Vector(pivot)
            m = Matrix.Translation(p) @ Matrix.Rotation(rot, 4, "Z") @ Matrix.Translation(-p) @ m
        shown.append(_copy(f"expl_{tag}", o, o0 @ Matrix.Translation(Vector(d)) @ m, coll))
    pc = (CORNER[0], CORNER[1], 0)
    lift = 3.0
    put("post_a", POST_P, (-4.0, -4.0, lift))
    put("post_b", POST_P, (-4.0, W + 4.0, lift), -math.pi / 2, pc)
    put("post_c", POST_P, (2 * POST_XS[1] + 4.0, W + 4.0, lift), math.pi, pc)
    put("post_d", POST_P, (2 * POST_XS[1] + 4.0, -4.0, lift), math.pi / 2, pc)
    x2 = sum(board_span(2)) / 2
    for i in range(NB):                          # two groups (5 + 9 on the sheet), spread a little
        xi = sum(board_span(i)) / 2
        put(f"plank{i}", PLANK_P, (xi - x2 + 0.25 * (i - 6.5) + (-1.0 if i < 5 else 1.0), 0, 5.5))
    sp = stringer_spans()
    for j in (1, 2, 3):                          # the stringer part is one span: a copy in every span, both sides
        dx = (sp[j][0] + sp[j][1]) / 2 - (sp[1][0] + sp[1][1]) / 2
        put(f"str_a{j}", STR_P, (dx, -3.0, 0.0))
        put(f"str_b{j}", STR_P, (-dx, 3.0, 0.0), math.pi, (0, 0, 0))
    for j, x in enumerate(ROW):
        put(f"cross{j}", CROSS_P, (x + POST_XS[0], 0, -2.6))
    put("brace_a", BRACE_P, (-1.5, -5.0, -1.2))
    put("brace_b", BRACE_P, (1.5, 5.0, -1.2), math.pi, (0, 0, 0))
    put("rope_a", ROPE_P, (0, -4.0, 6.5))
    put("rope_b", ROPE_P, (2 * BAY, W + 4.0, 6.5))
    bpy.context.view_layer.update()
    return shown


def _marker(h, at, tag):
    a = K.fk().Asset(PFX + tag, "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=MARK, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=MARK, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=MARK, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    c.matrix_world = _frame_of(h) @ Matrix.Translation(at)
    bpy.context.view_layer.update()
    return c


def _scale_markers(h):
    """5.5-stud character stand-ins: on the deck at x 0, and on the ground beside a -Y leg."""
    return [_marker(h, (0.0, 0.0, DECK_TOP), "char_deck"), _marker(h, (-POST_XS[0] - 2.6, -W / 2 - 2.4, 0.0),
                                                                    "char_ground")]


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


CLOSE = {   # name: (az, el, build-frame centre, radius)
    "junc_cu": (-60, 15, (-POST_XS[1], -W / 2 - 0.3, 6.0), 2.6),
    "rope_cu": (-20, 10, (-POST_XS[0] - 1.2, -W / 2, 7.0), 1.7),
    "peg_cu": (-25, 8, (-POST_XS[0], -W / 2 - 1.0, 4.1), 1.1),
    "under_cu": (-35, -30, (-10.5, -2.0, 3.0), 4.0),
    "xbrace_cu": (-90, 6, (-POST_XS[1] - 0.8, 0.0, 2.6), 4.4),
}


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    markers = _scale_markers(h)
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        extra["f34_probe_sheet"] = ([h], *PROBE_VIEW)
        for o in objs[1:]:
            extra["part_" + o.name.replace("TimberBridge", "").lower()] = ([o], *PARTS_SHOT)
        if shown:
            extra["exploded"] = (shown, -35, 25)
        extra["scale"] = ([h] + markers, -30, 12)
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
            for name, (az, el, c, r) in CLOSE.items():
                out[name] = _close([h], f"{d}/{name}.png", az, el, fr @ Vector(c), r)
        return out
    finally:
        for o in shown + markers:
            me = o.data
            mine = o in markers
            bpy.data.objects.remove(o, do_unlink=True)
            if mine and me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


# spec 5.4 calibration warnings, sampled on our renders at known build-frame points (5 x 5 px medians). The twisted
# rope and the small pegs are judged by the Y-class median of measure() instead (a spot lands on one ply)
def _board_mid(i):
    return sum(board_span(i)) / 2


REGIONS = {
    "f34_sheet": {"board_top": [(_board_mid(i), y, DECK_TOP) for i in (2, 3, 6, 7, 10, 11) for y in (-2.0, 0.0, 2.0)],
                  "cap_top": [(px, py, POST_TOP) for px, py in POSTS],
                  "leg": [(-POST_XS[0], -DECK_Y, 1.5), (POST_XS[0], -DECK_Y, 1.5), (-POST_XS[1], -DECK_Y, 1.5)],
                  "post_face": [(-POST_XS[0], -DECK_Y, 6.3), (POST_XS[0], -DECK_Y, 6.3)]},
    "front_sheet": {"board_end": [(_board_mid(i), -DECK_Y, 5.17) for i in (2, 3, 6, 7, 10, 11)],
                    "post_face": [(px, -DECK_Y, 6.3) for px in ROW],
                    "leg": [(px, -DECK_Y, 1.5) for px in ROW],
                    "stringer": [(x, -(W / 2 - PH), 4.0) for x in (-9.14, 0.0, 9.14)]},
    "top_sheet": {"board_top": [(_board_mid(i), y, DECK_TOP) for i in (2, 3, 6, 7, 10, 11) for y in (-2.0, 2.0)],
                  "cap_top": [(px + 0.4, py + 0.4, POST_TOP) for px, py in POSTS]},
}
SHEET_REGION = {"f34_sheet": {"board_top": "#DE833B", "cap_top": "#F4903E", "leg": "#7E3911", "post_face": "#8A3D0A"},
                "front_sheet": {"board_end": "#B25415", "post_face": "#A64E13", "leg": "#A3511C",
                                "stringer": "#954B1F"},
                "top_sheet": {"board_top": "#D47935", "cap_top": "#F39641"}}


def region_report():
    """Render the region views again and sample each region (spec 5.4 warnings) against the sheet."""
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
            az, el = SHEET_VIEWS[view]
            path = kit["render_group"]([h], f"{d}/{view}.png", az, el)
            px = kit["load_px"](path)
            H_, W_ = px.shape[:2]
            cam = bpy.data.objects["FB_Cam"]
            lens0 = cam.data.lens                   # _lens restores the lens after the shot: project with the shot's
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
                hh, ss, vv = m048._hsv(c[None] / 255.0)
                row["hsv"] = [round(float(hh[0])), round(float(ss[0]), 2), round(float(vv[0]), 2)]
                res[name] = row
            out[view] = res
    finally:
        kit["render_group"] = orig
    return out


def preview(names=("f34_sheet", "front_sheet", "side_sheet", "top_sheet"), vfx=False, measure_too=True):
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = _lens(kit)
    try:
        sheet = M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig
    return {"sheet": sheet, "measure": measure_views() if measure_too else None}
