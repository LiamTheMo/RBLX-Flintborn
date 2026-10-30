"""051 Rope Crossing (references/051.png): a sagging plank footbridge slung between two pairs of tall square timber
posts, each post on its own big faceted anchor stone. Post centres 18 along x 6 across, stone tops 5.6, post tops 11.0,
deck top 5.6 at the ends sagging to 4.5 at mid-span; overall about 26 L x 11.2 W x 11.0 H.

    import importlib, kit_models, m051; importlib.reload(kit_models); importlib.reload(m051); m051.build()

Build frame (studs): long axis X (the sheet's FRONT VIEW is the -Y long side), +Y back, ground z 0, centred on x 0 /
y 0; symmetric about x 0 and y 0 except the cloth. W08 owns RopeCrossing*: names RopeBridge*, keys m051_*.

Seam contract (spec 2.1, binding):
- ground z 0: stone bases and spurs flat;
- walk surface at the ends: stone tops z 5.6, |x| 7.26 .. 12.0, |y| 0.05 .. 4.9 (each pair 0.10 apart at y 0);
- deck ends: the end planks' top outer edges z 5.58-5.60 at |x| ~6.85 (0.41 gap to the stone's deck-side face);
- outer ends: stone outer faces x +-12.0 (top) -> +-13.0 (base); sides: stones to y +-5.6 at the base, spurs <= +-6.0;
- post centres (+-9.0, +-3.0).
Walkability (binding, decision 12): plank tilt <= 17 deg, steps between planks <= 0.08, the only raised step the 0.35
brace sill; no rope across either end (decision 6), so both ends are open.

Every piece is its own closed shell (no booleans), touching or sunk into what carries it:
- 4 anchor stones (convex faceted hulls: vertical deck-side face to z 3.8, cleft faces leaning apart into a V gap below
  a 0.10 seam, chamfered outer top edges) and 2-3 spurs each, seated 0.03 into their stone;
- 4 posts: a 2.0 base block on the stone, a 1.6 shaft stepping out to a 1.7 cap with a chamfer and a dark peg hole;
- 8 twisted rope coils (2 per post: 16 short twisted 3-ply segments), 4 L-shaped red cloth wraps with two tails and
  a knot lump;
- 2 low brace sills (the 0.35 step), 4 peg blocks with pegs;
- 10 tilted planks (U section: a 0.80 body with a 1.15 lug at each end, a pale peg dot on each lug's end face);
- 2 main ropes (twisted 5-sided, knot collars in the tube), 16 hangers (twisted 3-ply), 4 diagonals, 4 backstays
  with knobs on the stones, 18 foot-rope links between the lugs, 4 end ties from the end planks to the peg blocks
  (links and ties 3-ply);
- colour by role and position only (rope strands by index round the twist; never by facing).
Parts (key labels): RopeBridgeEndPost (bare post), RopeBridgeBrace, RopeBridgePegBlock, RopeBridgePlank,
RopeBridgeMainRope, RopeBridgeHangerRope, RopeBridgeAnchorStone.

Stages 5-6: nothing (the sheet shows no water, glow, light or effect). See M051_spec.md.
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
from m048 import _box, _knob, _solid, _tri_ngons, _tube, winding_report

NUM, TITLE, SHEET = 51, "Rope Crossing", "M051"
OFF = "m051_offset"
PFX = "_m051_"
HERO = "RopeBridge"
POST_P, BRACE_P, PEG_P = "RopeBridgeEndPost", "RopeBridgeBrace", "RopeBridgePegBlock"
PLANK_P, MAIN_P, HANG_P, STONE_P = "RopeBridgePlank", "RopeBridgeMainRope", "RopeBridgeHangerRope", "RopeBridgeAnchorStone"
PARTS = (POST_P, BRACE_P, PEG_P, PLANK_P, MAIN_P, HANG_P, STONE_P)

# ---- builder constants (decision 4) ---------------------------------------------------------------------------------
L = 18.0                # post centres along (x)
W = 6.0                 # post centres across (y)
PX, PY = L / 2, W / 2
STONE_TOP = 5.6
POST_TOP = 11.0
SINK = 0.02
# stones (local u = |x|, v = |y|)
ST_DECK = 7.26          # deck-side face, vertical from the top down to ST_DECK_Z
ST_DECK_Z = 3.8
ST_DECK_BASE = 6.8
ST_OUT_TOP, ST_OUT_BASE = 12.0, 12.85
ST_CLEFT_TOP, ST_CLEFT_BASE = 0.05, 1.3
ST_SIDE_TOP, ST_SIDE_BASE = 4.9, 5.35
ST_CH = 0.25            # chamfer on the outer top edges
# posts
BASE_H, BASE_Z = 1.0, (STONE_TOP - SINK, 6.70)
SHAFT_H, CAP_H = 0.8, 0.85
CAP_Z = 9.92
CAP_CH = 0.10
HOLE = 0.15             # peg-hole half size on the cap top
# brace sill and peg blocks
BRACE_X = (8.5, 9.5)
BRACE_TOP = 5.95
PEGB_X, PEGB_Y, PEGB_TOP = (7.31, 8.02), (2.30, 3.20), 6.38
PEG_Z, PEG_H, PEG_OUT = 6.15, 0.14, 0.10
# deck
NP = 10
PITCH = 1.40
PLANK_W, PLANK_T, LUG_T = 1.15, 0.80, 1.15
PLANK_HALF, LUG_IN = 3.10, 2.20
DOT = 0.13              # peg-dot half size on the lug end faces
LUG_DARK = 0.5          # lug faces this far toward wood_dark (position: the sheet's darker plank ends)
DECK_LOW = 4.50
SAG = 1.10
DECK_END = 6.875        # where the deck curve meets the stone-top level
# rope
ROPE_Y = 2.75
ROPE_END_X = 8.0
ROPE_END_Z = 9.42
ROPE_LOW = 6.86
MAIN_R, COLLAR_R = 0.225, 0.35
MAIN_SIDES = 5
COIL_Z = (9.22, 9.62)
COIL_D, COIL_C = 0.99, 0.93       # coil centreline off the post axis: on the flats, at the corners (each axis)
HANG_R, HANG_SIDES = 0.16, 3     # three-ply hangers: a twisted triangle section reads 0.24-0.28 thick
KNOT_R = 0.21                     # bottom knot bulge on the hangers and diagonals
DIAG_R = 0.15
BACK_R, KNOB_R = 0.18, 0.30
LINK_R, LINK_SIDES = 0.15, 3
LINK_Y = 2.65
# cloth
CLOTH_Z = (8.20, 9.00)
CLOTH_T = 0.08

WOOD, WOOD_DEEP, WOOD_DARK = "m051_wood", "m051_wood_deep", "m051_wood_dark"
ROPE, ROPE_DARK, PEG = "m051_rope", "m051_rope_dark", "m051_peg"
CLOTH, STONE, STONE_MID, MARK = "m051_cloth", "m051_stone", "m051_stone_mid", "m051_marker"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, metal, low specular). Start values from M048's calibrated wood / rope (spec 5.4); stage 4
# writes the calibrated hexes here.
PALETTE = {
    WOOD: ("#B66D2A", 0.85, 0.0, True),
    WOOD_DEEP: ("#894315", 0.85, 0.0, True),
    WOOD_DARK: ("#5C3014", 0.9, 0.0, True),
    ROPE: ("#CEA261", 0.95, 0.0, True),
    ROPE_DARK: ("#A16720", 0.95, 0.0, True),
    PEG: ("#C0A870", 0.55, 0.0, False),
    CLOTH: ("#8F2210", 0.9, 0.0, True),
    STONE: ("#ABA5A2", 0.92, 0.0, True),
    STONE_MID: ("#767A85", 0.92, 0.0, True),
    MARK: ("#7E7978", 0.7, 0.0, False),
}
# calibration targets (spec 5.4: medians of unshadowed rendered regions on the sheet)
TARGETS = {WOOD: ((0xD8, 0x7E, 0x34), "brown"), WOOD_DEEP: ((0x9D, 0x4D, 0x18), "brown"),
           WOOD_DARK: ((0x6E, 0x35, 0x14), "brown"), ROPE: ((0xF8, 0xC4, 0x6A), "vivid"),
           ROPE_DARK: ((0xC8, 0x76, 0x1F), "vivid"), PEG: ((0xF2, 0xCC, 0x80), "vivid"),
           CLOTH: ((0xB4, 0x24, 0x11), "vivid"), STONE: ((0xBC, 0xB5, 0xB0), "stone"),
           STONE_MID: ((0x93, 0x93, 0x98), "stone")}


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


GEO = {}                # levels and placements recorded while building (level and walk checks)


# ---- solid builders -------------------------------------------------------------------------------------------------
def _solid_rc(a, pts, faces, key, tint=1.0):
    """One closed shell from points and faces of any winding: bmesh makes the winding consistent, then the shell is
    flipped as a whole if its signed volume is negative. Returns (verts, faces)."""
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


def _hull(a, pts, key, tint=1.0):
    """A convex faceted hull of points. Returns (verts, faces, planes) with planes [(n, d)] (n.p <= d inside)."""
    bm = a.bm
    vs = [bm.verts.new(Vector(p)) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    for v in vs:
        if v.is_valid and not v.link_faces:
            bm.verts.remove(v)
    vs = [v for v in vs if v.is_valid]
    fs = list({f for v in vs for f in v.link_faces})
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    nt = [f for f in fs if len(f.verts) > 3]
    if nt:
        bmesh.ops.triangulate(bm, faces=nt, quad_method="BEAUTY", ngon_method="BEAUTY")
    fs = list({f for v in vs for f in v.link_faces})
    # even triangles inside each facet: flip only edges between (near-)coplanar triangles, under 5 deg, so slivers
    # between nearly coplanar hull points go (the hull moves by at most about 0.02)
    for f in fs:
        f.normal_update()
    flat = [e for e in {e for f in fs for e in f.edges}
            if len(e.link_faces) == 2 and e.link_faces[0].normal.angle(e.link_faces[1].normal, 0.0) < math.radians(5)]
    if flat:
        bmesh.ops.beautify_fill(bm, faces=fs, edges=flat)
    fs = list({f for v in vs for f in v.link_faces})
    for f in fs:
        f.normal_update()
    vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs)
    if vol < 0:
        for f in fs:
            f.normal_flip()
            f.normal_update()
    a._finish(vs, key, tint=tint)
    planes = [(f.normal.copy(), f.normal.dot(f.calc_center_median())) for f in fs if f.calc_area() > 1e-8]
    return vs, fs, planes


def _sd(planes, p):
    """Signed distance to a convex hull (negative inside)."""
    return max(n.dot(p) - d for n, d in planes)


def _frame(outer, inner):
    """Faces of a flat frame between a quad and a smaller quad inside it (same corner order), plus the inner quad."""
    fs = []
    for k in range(4):
        k1 = (k + 1) % 4
        fs.append([outer[k], outer[k1], inner[k1], inner[k]])
    return fs, list(inner)


def _rope(a, path, radii, sides, key, groove=None, tint=1.0, phase=0.0, up=(0, 0, 1)):
    """An open twisted rope tube (antiprism: each ring turned half a side) with a radius per ring, so knot collars
    and end bulges are rings of the same tube. Strands (by side index round the twist, never by facing) take the
    `groove` keys. Bends are mitred (m048._tube)."""
    P = [Vector(p) for p in path]
    N = len(P)
    upv = Vector(up)
    rings = []
    for i in range(N):
        prev, nxt = P[max(i - 1, 0)], P[min(i + 1, N - 1)]
        tin = (P[i] - prev) if (P[i] - prev).length > 1e-9 else (nxt - P[i])
        tout = (nxt - P[i]) if (nxt - P[i]).length > 1e-9 else tin
        tin, tout = tin.normalized(), tout.normalized()
        T = (tin + tout).normalized()
        U = upv - upv.dot(T) * T
        if U.length < 1e-6:
            U = Vector((1, 0, 0)) - Vector((1, 0, 0)).dot(T) * T
        U.normalize()
        V = T.cross(U)
        B = tout - tin
        bend = B.length > 1e-6
        if bend:
            B.normalize()
        sc = 1.0 / max(0.5, tin.dot(T)) - 1.0
        ring = []
        for k in range(sides):
            ang = phase + 2 * math.pi * (k + 0.5 * i) / sides
            off = (U * math.cos(ang) + V * math.sin(ang)) * radii[i]
            if bend:
                off += B * off.dot(B) * sc
            ring.append(P[i] + off)
        rings.append(ring)
    pts = [p for rg in rings for p in rg]
    faces, strand = [], []
    for i in range(N - 1):
        j = i + 1
        for k in range(sides):
            a0, a1 = i * sides + k, i * sides + (k + 1) % sides
            b0, b1 = j * sides + k, j * sides + (k + 1) % sides
            faces += [[a0, a1, b0], [a1, b1, b0]]
            strand += [k, k]
    faces.append(list(reversed(range(sides))))
    faces.append([(N - 1) * sides + k for k in range(sides)])
    strand += [-1, -1]
    vs, fs = _solid(a, pts, faces, key, tint)
    if groove:
        gi = {k: a._mi(v) for k, v in groove.items()}
        for f, s in zip(fs, strand):
            if s in gi:
                f.material_index = gi[s]
    return vs, fs


ROPE_BLEND = 0.6        # the blend strand: 60 % of the way to amber (stays amber-side, the sheet's W class)


GOLD_ROLES = {"coil", "main"}   # rope roles with a golden strand. The thin hangers and links are amber with one lighter
# blend strand (the sheet's hangers are mostly amber; with gold on them too the f34 gold share was 4.3, sheet 2.8)


def _strands(sides, role="main"):
    """Rope strand roles (spec 5.3, decision 8): by the strand's index round the twist, never by facing. Ropes in
    GOLD_ROLES keep golden `rope` (the tube's own key) on one strand of 3 (coils) or 5 (main ropes, diagonals,
    backstays), with one blend strand (ROPE_BLEND toward amber) and the rest amber `rope_dark`; the thin hangers and
    links are blend / amber only."""
    mid = _mix(ROPE, ROPE_DARK, ROPE_BLEND)
    if role not in GOLD_ROLES:
        return {k: (mid if k == 0 else ROPE_DARK) for k in range(sides)} if sides != 3 else {0: mid, 1: mid, 2: ROPE_DARK}
    if sides == 5:
        return {0: ROPE_DARK, 1: ROPE_DARK, 3: mid, 4: ROPE_DARK}
    if sides == 4:
        return {0: ROPE_DARK, 2: mid, 3: ROPE_DARK}
    if sides == 3:
        return {1: mid, 2: ROPE_DARK}
    return {k: ROPE_DARK for k in range(0, sides, 2)}


# ---- stones ---------------------------------------------------------------------------------------------------------
def _cleft(z):
    return ST_CLEFT_TOP + (STONE_TOP - z) / STONE_TOP * (ST_CLEFT_BASE - ST_CLEFT_TOP)


def _deck_u(z):
    return ST_DECK if z >= ST_DECK_Z else ST_DECK_BASE + (ST_DECK - ST_DECK_BASE) * z / ST_DECK_Z


def _out_u(z):
    return ST_OUT_BASE + (ST_OUT_TOP - ST_OUT_BASE) * min(z, 5.35) / 5.35


def _side_v(z):
    return ST_SIDE_BASE + (ST_SIDE_TOP - ST_SIDE_BASE) * min(z, 5.35) / 5.35


STONE_RINGS = (0.0, 1.3, ST_DECK_Z, 5.35)


def stone_rings(seed):
    """Local (u = |x|, v = |y|, z) rings of one anchor stone, 9 points each in the same order: deck/cleft corner,
    outer/cleft corner, two facet columns on the outer x face, the outer corner chamfer (2), two facet columns on the
    outer y face, deck/side corner. Rings at the ground, 1.3, 3.8 and 5.35, then the flat top inset 0.25 on the outer
    edges (the chamfer). Each facet column is pushed out (or in) by one amount from the ground to 3.8 (less above), so
    it stands as a vertical ridge (or groove): the sheet's vertical facet breaks, with broad flat faces between. The deck-side face
    is the vertical plane u 7.26 from 3.8 up (flaring to 6.8 at the ground) and the cleft face the plane v = cleft(z)
    (the pair's V gap)."""
    rng = _rng(seed)
    ox = [(rng.uniform(1.7, 2.5), rng.uniform(0.15, 0.32)), (rng.uniform(3.3, 4.1), rng.uniform(-0.28, -0.12))]
    oy = [(rng.uniform(10.0, 10.9), rng.uniform(-0.28, -0.12)), (rng.uniform(8.2, 9.0), rng.uniform(0.15, 0.32))]
    cut = rng.uniform(0.40, 0.60)          # outer corner chamfer
    rings = []
    for z in STONE_RINGS:
        f = 1.0 if z <= ST_DECK_Z else 0.45
        dk, ou, sv, cv = _deck_u(z), _out_u(z), _side_v(z), _cleft(z)
        c = cut * (1.0 if z <= ST_DECK_Z else 0.8)
        rings.append([(dk, cv, z), (ou, cv, z), (ou + ox[0][1] * f, ox[0][0], z), (ou + ox[1][1] * f, ox[1][0], z),
                      (ou, sv - c, z), (ou - c, sv, z), (oy[0][0], sv + oy[0][1] * f, z),
                      (oy[1][0], sv + oy[1][1] * f, z), (dk, sv, z)])
    t = STONE_TOP
    oi, si = ST_OUT_TOP - ST_CH, ST_SIDE_TOP - ST_CH
    c = cut * 0.6
    rings.append([(ST_DECK, ST_CLEFT_TOP, t), (oi, ST_CLEFT_TOP, t), (oi, ox[0][0], t), (oi, ox[1][0], t),
                  (oi, si - c, t), (oi - c, si, t), (oy[0][0], si, t), (oy[1][0], si, t), (ST_DECK, si, t)])
    return rings


def stone_points(seed):
    return [p for r in stone_rings(seed) for p in r]


def _place(pts, sx, sy):
    return [(sx * u, sy * v, z) for u, v, z in pts]


def _loft(a, rings, key, tint=1.0):
    """A closed shell lofted through rings of equal point count: quads between rings, a centroid fan on the bottom
    and top caps (no sliver triangles from the points along the straight top edges)."""
    n, R = len(rings[0]), len(rings)
    pts = [p for r in rings for p in r]
    cb = tuple(sum(p[i] for p in rings[0]) / n for i in range(3))
    ct = tuple(sum(p[i] for p in rings[-1]) / n for i in range(3))
    pts += [cb, ct]
    ib, it = len(pts) - 2, len(pts) - 1
    faces = []
    for k in range(n):
        k1 = (k + 1) % n
        faces.append([ib, k1, k])
        faces.append([(R - 1) * n + k, (R - 1) * n + k1, it])
        for i in range(R - 1):
            faces.append([i * n + k, i * n + k1, (i + 1) * n + k1, (i + 1) * n + k])
    return _solid_rc(a, pts, faces, key, tint)


SPURS = {   # per stone: (face, along, width along the face, height, seed); "ox" outer x face, "oy" outer y face
    (-1, -1): [("oy", 9.0, 1.7, 1.3, 1), ("ox", 3.4, 1.5, 1.1, 3)],
    (-1, 1): [("ox", 2.4, 1.4, 1.0, 4), ("oy", 10.4, 1.6, 1.2, 5)],
    (1, -1): [("oy", 10.8, 1.5, 1.0, 6), ("ox", 2.8, 1.7, 1.3, 7)],
    (1, 1): [("ox", 3.8, 1.4, 1.0, 8), ("oy", 9.2, 1.6, 1.2, 9)],
}
SPUR_SINK = 0.03
SPUR_DEPTH = 0.78       # a spur's extent out from the face (chunks lean on the stone, they don't stand off it)


def _spur_points(w, h, seed):
    """Local (along the face, out from the face, z) points: a ground ring, a mid ring and a ridge."""
    rng = _rng(seed * 31 + 7)
    pts = []
    for zf, rf, n in ((0.0, 1.0, 5), (0.6, 0.9, 4), (1.0, 0.55, 3)):        # a chunky block, flat-ish top
        off = rng.uniform(0, 2 * math.pi)
        for k in range(n):
            th = off + 2 * math.pi * k / n + rng.uniform(-0.3, 0.3)
            r = rf * rng.uniform(0.85, 1.05)
            z = h * zf * ((1 + rng.uniform(-0.08, 0.08)) if 0 < zf < 1 else 1)
            pts.append((math.cos(th) * r * w / 2, math.sin(th) * r * SPUR_DEPTH / 2, z))
    return pts


def _hull_samples(pts):
    """Planes and surface samples (verts, edge midpoints, face centres) of the convex hull of pts (a scratch bmesh)."""
    bm = bmesh.new()
    vs = [bm.verts.new(Vector(p)) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    fs = [f for f in bm.faces if f.calc_area() > 1e-8]
    ctr = sum((Vector(p) for p in pts), Vector()) / len(pts)          # inside the (convex) hull
    planes = []
    for f in fs:
        f.normal_update()
        n_, c_ = f.normal.copy(), f.calc_center_median()
        if n_.dot(ctr - c_) > 0:          # each plane oriented away from the interior on its own (collinear and
            n_ = -n_                      # coplanar input points can leave the hull's winding inconsistent)
        planes.append((n_, n_.dot(c_)))
    samp = ([v.co.copy() for v in bm.verts if v.link_faces] + [(e.verts[0].co + e.verts[1].co) / 2 for e in bm.edges]
            + [f.calc_center_median() for f in fs])
    bm.free()
    return planes, samp


def spur(a, stone_pts, sx, sy, face, along, w, h, seed, key):
    """A faceted chunk on the ground against a stone face, pushed out along the face normal until the two hulls
    overlap by exactly SPUR_SINK (bisection; the overlap is measured both ways on vertices, edge midpoints and face
    centres, since a stone corner can poke into a spur face between its vertices)."""
    if face == "ox":
        anchor, d, tg = Vector((sx * _out_u(0.0), sy * along, 0.0)), Vector((sx, 0.0, 0.0)), Vector((0, 1, 0))
    else:
        anchor, d, tg = Vector((sx * along, sy * _side_v(0.0), 0.0)), Vector((0.0, sy, 0.0)), Vector((1, 0, 0))
    base = [anchor + tg * pa + d * po + Vector((0, 0, z)) for pa, po, z in _spur_points(w, h, seed)]
    st_planes, st_samp = _hull_samples(stone_pts)
    sp_planes, sp_samp = _hull_samples(base)
    st_near = [q for q in st_samp if q.z < h + 0.5 and (q - anchor).length < w + 2.0]
    lo, hi = -w, w

    def depth(t):
        sh = d * t
        a_ = max(-_sd(st_planes, p + sh) for p in sp_samp)
        b_ = max(-max(n.dot(q - sh) - dd for n, dd in sp_planes) for q in st_near) if st_near else 0.0
        return max(0.0, a_, b_)
    for _ in range(40):
        mid = (lo + hi) / 2
        if depth(mid) > SPUR_SINK:
            lo = mid
        else:
            hi = mid
    t = hi
    pts = [p + d * t for p in base]
    vs, fs, _ = _hull(a, pts, key, tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    GEO.setdefault("spur_depth", []).append(round(depth(t), 3))
    return vs


def _stone_colour(a, fs):
    """Role and position (spec 5.3 / 5.5): warm `stone` base; cool `stone_mid` by height: 40 % on the ground band
    (faces centred below 1.2), 15 % on the band up to 3.8, none above; 30 % in the cleft (faces centred at |y| < 1.0).
    Never by facing."""
    for f in fs:
        c = f.calc_center_median()
        t = 0.4 if c.z < 1.2 else 0.15 if c.z < 3.0 else 0.0
        if abs(c.y) < 1.0 and c.z < 5.5:
            t = max(t, 0.3)
        if t > 0:
            f.material_index = a._mi(_mix(STONE, STONE_MID, t))


def stone(a, sx, sy, seed, spurs=True):
    rings = [_place(r, sx, sy) for r in stone_rings(seed)]
    sp = [p for r in rings for p in r]
    vs, fs = _loft(a, rings, STONE, tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    _stone_colour(a, fs)
    _texture(a, vs, 0.03, seed, scale=0.15)
    out = list(vs)
    if spurs:
        for face, along, w, h, s in SPURS[(sx, sy)]:
            sv = spur(a, sp, sx, sy, face, along, w, h, seed * 10 + s, _mix(STONE, STONE_MID, 0.5))
            _texture(a, sv, 0.03, seed + s, scale=0.15)
            out += sv
    return out


# ---- posts, brace, peg blocks ---------------------------------------------------------------------------------------
def _sq(cx, cy, h, z):
    return [(cx - h, cy - h, z), (cx + h, cy - h, z), (cx + h, cy + h, z), (cx - h, cy + h, z)]


def post_shaft(a, px, py, seed):
    """Shaft (1.6 square, sunk 0.02 into the base block) stepping out to the 1.7 cap with a 0.10 chamfer and a dark
    peg hole on top: one shell."""
    z0 = BASE_Z[1] - SINK
    rings = [_sq(px, py, SHAFT_H, z0), _sq(px, py, SHAFT_H, CAP_Z), _sq(px, py, CAP_H, CAP_Z),
             _sq(px, py, CAP_H, POST_TOP - CAP_CH), _sq(px, py, CAP_H - CAP_CH, POST_TOP), _sq(px, py, HOLE, POST_TOP)]
    pts = [p for r in rings for p in r]
    faces = [[3, 2, 1, 0]]
    for i in range(len(rings) - 1):
        for k in range(4):
            k1 = (k + 1) % 4
            faces.append([i * 4 + k, i * 4 + k1, (i + 1) * 4 + k1, (i + 1) * 4 + k])
    faces.append([20, 21, 22, 23])
    vs, fs = _solid(a, pts, faces, WOOD_DEEP, tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    fs[-1].material_index = a._mi(WOOD_DARK)            # the peg hole
    _texture(a, vs, 0.03, seed)
    return vs


def base_block(a, px, py, seed):
    vs, _ = _box(a, px - BASE_H, py - BASE_H, BASE_Z[0], px + BASE_H, py + BASE_H, BASE_Z[1],
                 _mix(WOOD_DEEP, WOOD_DARK, 0.15), tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    _texture(a, vs, 0.03, seed)
    return vs


def side_peg(a, px, py, sy, seed):
    """The key post's small square peg on the outer y face near the top (0.22 square, 0.10 proud, sunk 0.03)."""
    f = py + sy * CAP_H
    y0, y1 = sorted((f - sy * 0.03, f + sy * 0.10))
    vs, _ = _box(a, px - 0.11, y0, 10.29, px + 0.11, y1, 10.51, PEG)
    return vs


def post(a, sx, sy, seed, peg=False):
    px, py = sx * PX, sy * PY
    vs = base_block(a, px, py, seed) + post_shaft(a, px, py, seed + 1)
    if peg:
        vs += side_peg(a, px, py, sy, seed)
    return vs


COIL_STYLE = {"sides": 3, "n": 16, "r": 0.265, "pinch": 0.08}   # 16 short twisted 3-ply segments: the coil
# reads as wrapped rope, not as faceted collars (aligned octagon rings, M048) or stacked plates (long antiprisms)


def coil_path(px, py, z, n=8):
    """The coil's centreline round the shaft: a rounded square, COIL_D off the axis on the flats; n = 8 (corners
    and mid-flats) or 16 (corners, mid-flats and quarter points)."""
    d, c = COIL_D, COIL_C
    pts = [(d, 0.0), (c, c), (0.0, d), (-c, c), (-d, 0.0), (-c, -c), (0.0, -d), (c, -c)]
    if n == 16:
        pts = [(d, 0.0), (d, 0.5 * c), (c, c), (0.5 * c, d), (0.0, d), (-0.5 * c, d), (-c, c), (-d, 0.5 * c),
               (-d, 0.0), (-d, -0.5 * c), (-c, -c), (-0.5 * c, -d), (0.0, -d), (0.5 * c, -d), (c, -c), (d, -0.5 * c)]
    return [(px + x, py + y, z) for x, y in pts]


def coil(a, px, py, z, seed, phase=0.0):
    st = COIL_STYLE
    vs, _ = _tube(a, coil_path(px, py, z, st["n"]), st["r"], st["sides"], True, ROPE, groove=_strands(st["sides"], "coil"),
                  tint=1.0 + _rng(seed).uniform(-0.02, 0.02), phase=phase, twist=True, pinch=st.get("pinch", 0.0))
    return vs


def coils(a, sx, sy, seed):
    vs = []
    for i, z in enumerate(COIL_Z):
        vs += coil(a, sx * PX, sy * PY, z, seed + 31 * i, phase=(0.0, 0.6)[i])
    return vs


def brace(a, sx, seed):
    """The end sill: 1.0 (x) x 4.04 (y) x 0.37, ends sunk 0.02 into the base blocks' inner faces, bottom 0.02 into
    both stone tops (spans the 0.10 seam)."""
    x0, x1 = sorted((sx * BRACE_X[0], sx * BRACE_X[1]))
    y = PY - BASE_H + SINK
    vs, _ = _box(a, x0, -y, STONE_TOP - SINK, x1, y, BRACE_TOP, _mix(WOOD_DEEP, WOOD_DARK, 0.1),
                 tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    _texture(a, vs, 0.03, seed)
    return vs


def peg_block(a, sx, sy, seed):
    """A cube on the stone top beside the base block (outer face sunk 0.02 into it), a square peg on its span-facing
    face (sunk 0.03, 0.10 proud) that anchors the end tie."""
    xa, xb = sorted((sx * PEGB_X[0], sx * (PEGB_X[1])))
    ya, yb = sorted((sy * PEGB_Y[0], sy * PEGB_Y[1]))
    vs, _ = _box(a, xa, ya, STONE_TOP - SINK, xb, yb, PEGB_TOP, WOOD_DEEP, tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    _texture(a, vs, 0.03, seed)
    f = sx * PEGB_X[0]
    pa, pb = sorted((f + sx * 0.03, f - sx * PEG_OUT))
    yc = sy * (PEGB_Y[0] + PEGB_Y[1]) / 2
    pv, _ = _box(a, pa, yc - PEG_H, PEG_Z - PEG_H, pb, yc + PEG_H, PEG_Z + PEG_H, PEG)
    return vs + pv


# ---- deck -----------------------------------------------------------------------------------------------------------
def z_top(x):
    """The deck curve: plank top centres sit on it."""
    return DECK_LOW + SAG * (x / DECK_END) ** 2


def plank_x(i):
    return -(NP - 1) / 2 * PITCH + i * PITCH


# the U profile in (y, z), z 0 at the top
PROFILE = [(-PLANK_HALF, 0.0), (-PLANK_HALF, -LUG_T), (-LUG_IN, -LUG_T), (-LUG_IN, -PLANK_T), (LUG_IN, -PLANK_T),
           (LUG_IN, -LUG_T), (PLANK_HALF, -LUG_T), (PLANK_HALF, 0.0)]
CAP_TRIS = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 7), (4, 5, 6), (4, 6, 7)]   # ear-clipped U cap
LUG_TRIS = {0, 1, 4, 5}


END_STEEPEN = 0.55      # deg: the end planks pitched this much steeper about their outer top edge (walk steps)


def plank_matrix(i, seed):
    """Plank i on the curve: top centre on z_top, pitched to the curve's slope, a little yaw / roll jitter. The end
    planks are pitched END_STEEPEN steeper about their outer top edge (which stays at 5.585), so the step down to the
    next plank stays under 0.08 (it is the curve's rise across the widest gap)."""
    rng = _rng(seed)
    xc = plank_x(i)
    slope = math.atan(2 * SAG * xc / DECK_END ** 2)
    yaw = math.radians(rng.uniform(-0.4, 0.4))
    roll = math.radians(rng.uniform(-0.1, 0.1))
    c = Vector((xc, 0.0, z_top(xc)))
    if i in (0, NP - 1):
        s = 1 if xc > 0 else -1
        e = c + Matrix.Rotation(-slope, 3, "Y") @ Vector((s * PLANK_W / 2, 0, 0))
        slope += s * math.radians(END_STEEPEN)
        c = e - Matrix.Rotation(-slope, 3, "Y") @ Vector((s * PLANK_W / 2, 0, 0))
    return (Matrix.Translation(c) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Rotation(-slope, 4, "Y")
            @ Matrix.Rotation(roll, 4, "X"))


def plank_local(a, mat, key, seed, dots=True):
    """The U prism: 8-vertex profile extruded across the plank's width; ear-clipped caps; a pale peg dot (flush square
    in a frame) on each lug's end face. Lug faces 35 % wood_dark (position), the rest the plank key."""
    hw = PLANK_W / 2
    pts = [mat @ Vector((x, y, z)) for x in (-hw, hw) for (y, z) in PROFILE]
    n = len(PROFILE)
    faces, roles = [], []
    for t in CAP_TRIS:
        faces.append([t[2], t[1], t[0]])
        roles.append("lug" if CAP_TRIS.index(t) in LUG_TRIS else "body")
        faces.append([n + t[0], n + t[1], n + t[2]])
        roles.append(roles[-1])
    for k in range(n):
        k1 = (k + 1) % n
        if dots and k in (0, 6):                       # the lug end faces (y -3.1 and +3.1)
            q = [k, k1, n + k1, n + k]
            corners = [pts[j] for j in q]
            c = sum(corners, Vector()) / 4
            inner = []
            for p in corners:
                inner.append(len(pts))
                pts.append(c + (p - c) * (DOT * 2 / LUG_T))
            fr, dot = _frame(q, inner)
            faces += fr
            roles += ["lug"] * 4
            faces.append(dot)
            roles.append("dot")
        else:
            faces.append([k, k1, n + k1, n + k])
            low = min(PROFILE[k][1], PROFILE[k1][1])
            roles.append("lug" if low < -PLANK_T - 1e-6 else "body")      # lug bottoms, inner walls, end faces
    vs, fs = _solid_rc(a, pts, faces, key, tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    lug_key = _mix(WOOD, WOOD_DARK, LUG_DARK)
    for f, r in zip(fs, roles):
        if r == "lug":
            f.material_index = a._mi(lug_key)
        elif r == "dot":
            f.material_index = a._mi(PEG)
    _texture(a, vs, 0.02, seed)
    return vs, fs


PLANK_INFO = {}


def plank(a, i, seed):
    m = plank_matrix(i, seed)
    # colour by role and position: wood; planks 3 and 7 15 % wood_deep; a broad lighter field (noise along x)
    key = WOOD
    if i in (2, 7):
        key = _mix(WOOD, WOOD_DEEP, 0.15)
    elif noise.noise(Vector((plank_x(i) * 0.18, 0.0, 2.3))) > 0.15:
        key = _mix(WOOD, PEG, 0.1)
    vs, fs = plank_local(a, m, key, seed)
    PLANK_INFO[i] = {"m": m, "key": key}
    return vs


def deck(a, seed=510):
    PLANK_INFO.clear()
    vs = []
    for i in range(NP):
        vs += plank(a, i, seed + 7 * i)
    return vs


def lug_top(i, y):
    """World point on plank i's top at its centre line and y (the lug top for |y| > 2.2)."""
    return PLANK_INFO[i]["m"] @ Vector((0.0, y, 0.0))


# ---- rope -----------------------------------------------------------------------------------------------------------
def rope_z(x):
    """The main rope's catenary (m048._catenary's curve) through (+-8.0, 9.42) and 6.86 at x 0."""
    a_ = 1.3
    t = (x + ROPE_END_X) / (2 * ROPE_END_X)
    f = (math.cosh(a_) - math.cosh(a_ * (2 * t - 1))) / (math.cosh(a_) - 1)
    return ROPE_END_Z - (ROPE_END_Z - ROPE_LOW) * f


HANG_X = [plank_x(i) for i in range(1, NP - 1)]
COLLAR_W = 0.2


def main_rope_rings(x0, x1, knots, mids):
    """Ring stations (x, radius) from x0 to x1: a collar (fat ring between two normal rings COLLAR_W off) at every
    knot x, extra plain rings at `mids`."""
    st = [(x0, MAIN_R), (x1, MAIN_R)] + [(x, MAIN_R) for x in mids]
    for k in knots:
        st += [(k - COLLAR_W, MAIN_R), (k, COLLAR_R), (k + COLLAR_W, MAIN_R)]
    return sorted(st)


def main_rope(a, sy, seed):
    st = main_rope_rings(-ROPE_END_X, ROPE_END_X, HANG_X, (-6.45, 6.45))
    path = [(x, sy * ROPE_Y, rope_z(x)) for x, _ in st]
    vs, _ = _rope(a, path, [r for _, r in st], MAIN_SIDES, ROPE, groove=_strands(MAIN_SIDES),
                  tint=1.0 + _rng(seed).uniform(-0.02, 0.02), phase=_rng(seed).uniform(0, 1))
    GEO.setdefault("rope_low", []).append(round(min(p[2] for p in path), 3))
    return vs


def _end_knot_path(contact, toward, neck=0.36):
    """Ring stations for a rope that ends in a knot bulge seated on a surface at `contact`: the bottom ring sunk 0.03,
    the bulge, then a neck."""
    d = (Vector(toward) - Vector(contact)).normalized()
    c = Vector(contact)
    return [c - d * 0.03, c + d * 0.15, c + d * neck]


def hanger(a, i, sy, seed):
    """Hanger on plank i (1..8): vertical from the plank's lug top (bottom knot bulge seated 0.03 into it) up into the
    main rope's knot collar (top sunk 0.15)."""
    c = lug_top(i, sy * ROPE_Y)
    top = Vector((c.x, c.y, rope_z(c.x) - 0.15))
    knot = _end_knot_path(c, top)
    path = knot + [(knot[-1] + top) / 2, top]
    radii = [0.18, KNOT_R + 0.02, HANG_R, HANG_R * 0.92, HANG_R]
    vs, _ = _rope(a, path, radii, HANG_SIDES, ROPE, groove=_strands(HANG_SIDES, "thin"),
                  tint=1.0 + _rng(seed).uniform(-0.02, 0.02), phase=_rng(seed).uniform(0, 1), up=(1, 0, 0))
    GEO.setdefault("hanger_len", []).append(round(top.z - c.z, 2))
    return vs


def diagonal(a, sx, sy, seed):
    """From the lower coil's span side down to the end plank's lug top, ending in a knot bulge."""
    i = 0 if sx < 0 else NP - 1
    c = lug_top(i, sy * ROPE_Y)
    s = Vector((sx * ROPE_END_X, sy * 2.9, 9.1))
    knot = _end_knot_path(c, s, neck=0.45)
    path = knot + [knot[-1].lerp(s, 0.5), s]
    radii = [0.17, KNOT_R + 0.01, DIAG_R, DIAG_R * 0.9, DIAG_R]
    vs, _ = _rope(a, list(reversed(path)), list(reversed(radii)), 5, ROPE, groove=_strands(5),
                  tint=1.0 + _rng(seed).uniform(-0.02, 0.02), phase=_rng(seed).uniform(0, 1))
    return vs


BACK_KNOB = (10.7, 4.3)


def backstay(a, sx, sy, seed):
    """From the lower coil's outer corner down and outward to a knot knob sunk 0.03 into the stone top."""
    s = Vector((sx * (PX + COIL_C), sy * (PY + COIL_C), COIL_Z[0]))
    k = Vector((sx * BACK_KNOB[0], sy * BACK_KNOB[1], STONE_TOP + KNOB_R - 0.03))
    path = [s, s.lerp(k, 0.35), s.lerp(k, 0.7), k]
    radii = [BACK_R, BACK_R * 0.9, BACK_R, BACK_R]
    vs, _ = _rope(a, path, radii, 5, ROPE, groove=_strands(5), tint=1.0 + _rng(seed).uniform(-0.02, 0.02),
                  phase=_rng(seed).uniform(0, 1))
    kv, _ = _knob(a, k, KNOB_R, _mix(ROPE, ROPE_DARK, 0.5), tint=0.98, segs=6, rings=3)
    return vs + kv


def link(a, i, sy, seed):
    """A short rope piece between plank i's and plank i+1's lugs at |y| 2.65, mid-lug height, each end sunk 0.08."""
    hw = PLANK_W / 2
    p0 = PLANK_INFO[i]["m"] @ Vector((hw - 0.08, sy * LINK_Y, -LUG_T / 2))
    p1 = PLANK_INFO[i + 1]["m"] @ Vector((-hw + 0.08, sy * LINK_Y, -LUG_T / 2))
    vs, _ = _rope(a, [p0, p1], [LINK_R, LINK_R], LINK_SIDES, ROPE, groove=_strands(LINK_SIDES, "thin"),
                  tint=1.0 + _rng(seed).uniform(-0.02, 0.02), phase=_rng(seed).uniform(0, 1))
    return vs


def end_tie(a, sx, sy, seed):
    """From the end plank's lug top (|y| 2.65, sunk 0.03) to the peg block's span-facing face (sunk 0.08), over the
    stone's top corner."""
    i = 0 if sx < 0 else NP - 1
    p0 = PLANK_INFO[i]["m"] @ Vector((sx * 0.35, sy * LINK_Y, LINK_R - 0.03))
    p1 = Vector((sx * (PEGB_X[0] + 0.08), sy * LINK_Y, 5.85))
    vs, _ = _rope(a, [p0, p1], [LINK_R, LINK_R], LINK_SIDES, ROPE, groove=_strands(LINK_SIDES, "thin"),
                  tint=1.0 + _rng(seed).uniform(-0.02, 0.02), phase=_rng(seed).uniform(0, 1))
    # clearance over the stone's deck-side top corner (x 7.26, z 5.6)
    t = (sx * ST_DECK - p0.x) / (p1.x - p0.x)
    GEO.setdefault("tie_clear", []).append(round(p0.z + (p1.z - p0.z) * t - LINK_R - STONE_TOP, 3))
    return vs


# ---- cloth ----------------------------------------------------------------------------------------------------------
def cloth(a, sx, sy, seed):
    """An L-shaped wrap round the post's -X / +Y corner (inner face sunk 0.01 into the shaft) at z 8.55-9.00, a knot
    lump on the -X face near that corner and two tails (one on each face) hanging to about z 7.0-7.2."""
    px, py = sx * PX, sy * PY
    rng = _rng(seed)
    h = SHAFT_H
    i_, o_ = h - 0.01, h - 0.01 + CLOTH_T
    e = h + 0.03                                       # the wrap's ends run a hair past the shaft edges
    plan = [(px - o_, py - e), (px - o_, py + o_), (px + e, py + o_), (px + e, py + i_), (px - i_, py + i_),
            (px - i_, py - e)]
    z0, z1 = CLOTH_Z
    pts = [(x, y, z0) for x, y in plan] + [(x, y, z1) for x, y in plan]
    cap = [(0, 1, 4, 5), (1, 2, 3, 4)]                 # two quads (no sliver triangles on the thin legs)
    faces = [list(reversed(c)) for c in cap] + [[6 + j for j in c] for c in cap]
    for k in range(6):
        k1 = (k + 1) % 6
        faces.append([k, k1, 6 + k1, 6 + k])
    tint = 1.0 + rng.uniform(-0.02, 0.02)
    vs, _ = _solid_rc(a, pts, faces, CLOTH, tint=tint)
    out = list(vs)
    # knot lump on the -X face near the corner
    kx, ky, kz = px - o_ - 0.10, py + 0.50, 8.80
    lump = [(kx - 0.13 + 0.05, ky - 0.20, kz - 0.17), (kx + 0.13, ky - 0.20, kz - 0.17), (kx + 0.13, ky + 0.20, kz - 0.17),
            (kx - 0.13 + 0.05, ky + 0.20, kz - 0.17), (kx - 0.13, ky - 0.17, kz + 0.17), (kx + 0.13, ky - 0.17, kz + 0.17),
            (kx + 0.13, ky + 0.17, kz + 0.17), (kx - 0.13, ky + 0.17, kz + 0.17)]
    lv, _ = _solid_rc(a, lump, [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [0, 4, 7, 3], [1, 2, 6, 5]],
                      CLOTH, tint=tint * 0.97)
    out += lv
    # tails: tapered slabs with a pointed foot, 0.08 thick, 0.02 off the shaft, their tops in the wrap / lump
    for face, (u0, u1), (b0, b1), zb in (("x", (0.12, 0.70), (0.22, 0.64), 6.9 + rng.uniform(-0.1, 0.1)),
                                         ("y", (-0.68, -0.26), (-0.62, -0.32), 7.25 + rng.uniform(-0.1, 0.1))):
        zt = 8.95
        outline = [(u0, zt), (u1, zt), (b1, zb + 0.14), ((b0 + b1) / 2, zb), (b0, zb + 0.14)]
        if face == "x":
            w0, w1 = px - h - 0.02 - CLOTH_T, px - h - 0.02
            P = [(w, py + u, z) for w in (w0, w1) for u, z in outline]
        else:
            w0, w1 = py + h + 0.02, py + h + 0.02 + CLOTH_T
            P = [(px + u, w, z) for w in (w0, w1) for u, z in outline]
        tri = [(0, 1, 2, 4), (2, 3, 4)]
        fs_ = [list(reversed(t)) for t in tri] + [[5 + j for j in t] for t in tri]
        for k in range(5):
            k1 = (k + 1) % 5
            fs_.append([k, k1, 5 + k1, 5 + k])
        tv, _ = _solid_rc(a, P, fs_, CLOTH, tint=tint * 0.95)
        out += tv
    return out


# ---- parts and hero -------------------------------------------------------------------------------------------------
STONES = [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def post_part(a):
    post(a, -1, -1, 201, peg=True)


def brace_part(a):
    brace(a, -1, 301)


def peg_part(a):
    peg_block(a, -1, -1, 401)


def plank_part(a):
    plank_local(a, Matrix.Identity(4), WOOD, 501)


def main_part(a):
    """One main rope as the key draws it: a short sagging length (ends 8 apart) with a knot collar near each end and
    round knob ends (each rope end sunk into its knob)."""
    st = main_rope_rings(-4.0, 4.0, (-3.1, 3.1), (-1.6, 0.0, 1.6))
    zf = lambda x: 1.0 - 0.6 * (1 - (x / 4.0) ** 2)
    path = [(x, 0.0, zf(x)) for x, _ in st]
    vs, _ = _rope(a, path, [r for _, r in st], MAIN_SIDES, ROPE, groove=_strands(MAIN_SIDES), phase=0.3)
    for x in (-4.0, 4.0):
        _knob(a, (x, 0.0, zf(x)), 0.3, _mix(ROPE, ROPE_DARK, 0.5), tint=0.98, segs=6, rings=3)


def hanger_part(a):
    """One hanger, 3.0 long, with the key's three knot nodes (top, a third of the way down, bottom)."""
    zs = [0.0, 0.18, 0.36, 0.7, 1.0, 1.15, 1.30, 1.9, 2.5, 2.64, 2.82, 3.0]
    radii = [0.18, KNOT_R + 0.02, HANG_R, HANG_R * 0.92, HANG_R, KNOT_R + 0.02, HANG_R, HANG_R * 0.92, HANG_R,
             KNOT_R + 0.02, KNOT_R * 0.85, 0.16]
    _rope(a, [(0.0, 0.0, z) for z in zs], radii, HANG_SIDES, ROPE, groove=_strands(HANG_SIDES, "thin"), up=(1, 0, 0))


def stone_part(a):
    stone(a, -1, -1, 601)


def hero_fn(a):
    GEO.clear()
    for k, (sx, sy) in enumerate(STONES):
        stone(a, sx, sy, 601 + 13 * k)
        post(a, sx, sy, 201 + 17 * k)
        coils(a, sx, sy, 701 + 11 * k)
        cloth(a, sx, sy, 801 + 7 * k)
        peg_block(a, sx, sy, 401 + 5 * k)
    for sx in (-1, 1):
        brace(a, sx, 301 + sx)
    deck(a)
    for sy in (-1, 1):
        main_rope(a, sy, 901 + sy)
        for i in range(1, NP - 1):
            hanger(a, i, sy, 1001 + 3 * i + sy)
        for i in range(NP - 1):
            link(a, i, sy, 1101 + 3 * i + sy)
        for sx in (-1, 1):
            diagonal(a, sx, sy, 1201 + 2 * sx + sy)
            backstay(a, sx, sy, 1301 + 2 * sx + sy)
            end_tie(a, sx, sy, 1401 + 2 * sx + sy)


NOTES = {
    HERO: "Rope crossing (post centres 18 x 6, stone tops 5.6, posts to 11.0, deck sagging from 5.6 to 4.5; about 26 x "
          "11.2 x 11): a sagging plank footbridge between two pairs of square timber posts on four faceted anchor "
          "stones; twisted rope coils and red cloth wraps on the posts, two main ropes with knot collars, hangers to "
          "ten tilted planks with lugs, diagonals, backstays to the stones, rope links between the lugs, low brace "
          "sills and peg blocks at the ends. Seams: stone tops and deck ends 5.6, ground 0, both ends open. No VFX",
    POST_P: "End Post (reusable): a 1.6-square timber post on a 2.0 base block, a 1.7 chamfered cap with a peg hole and "
            "a side peg",
    BRACE_P: "Brace (reusable): the 1.0 x 4.0 x 0.37 end sill between the base blocks",
    PEG_P: "Peg Block (reusable): a timber block with a square peg that anchors a rope",
    PLANK_P: "Plank (reusable): a 1.15 x 0.80 x 6.2 plank with a deeper lug at each end and pale peg dots",
    MAIN_P: "Main Rope (reusable): a sagging twisted rope with knot collars and round knob ends",
    HANG_P: "Hanger Rope (reusable): a 3.0 twisted hanger rope with three knots",
    STONE_P: "Anchor Stone (reusable): a tapered faceted anchor stone with a flat 5.6 top and loose chunks at its foot",
}
COLLISION = {HERO: "precise", POST_P: "hull", BRACE_P: "box", PEG_P: "box", PLANK_P: "box", MAIN_P: "none",
             HANG_P: "none", STONE_P: "hull"}


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


# ---- checks ---------------------------------------------------------------------------------------------------------
def _keys(o):
    return [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]


def _kind(ks):
    ks = set(ks)
    if all(k.startswith("m051_stone") for k in ks):
        return "stone"
    if all(k.startswith("m051_rope") for k in ks):
        return "rope"
    if all(k.startswith("m051_cloth") for k in ks):
        return "cloth"
    if all(k == PEG for k in ks):
        return "peg"
    if all(k.startswith("m051_wood") or k == PEG for k in ks):
        return "wood"           # timber with its inlaid peg dots / hole
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
    r["floating_kinds"] = [k.replace("m051_", "") for k in r["floating_kinds"]]
    return r


_PDIRS = (Vector((1.0, 0.0131, 0.0217)).normalized(), Vector((-0.0173, 1.0, 0.0119)).normalized(),
          Vector((0.0109, -0.0207, 1.0)).normalized())


def _parity_in(tree, p):
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


# how deep (beyond which a shell counts as buried) a shell of one kind may sit inside a shell of another: the stated
# sinks (spec 6) + 0.05. Rope ends inside coils / collars / knobs are joins, judged by the full-burial test only.
SINK_LIMIT = {("stone", "stone"): 0.08, ("wood", "stone"): 0.07, ("wood", "wood"): 0.07, ("peg", "wood"): 0.08,
              ("cloth", "wood"): 0.06, ("cloth", "cloth"): 0.30, ("rope", "wood"): 0.20, ("rope", "stone"): 0.10,
              ("rope", "cloth"): 0.10, ("wood", "rope"): 0.05, ("stone", "wood"): 0.05, ("cloth", "rope"): 0.05}


def bury_report(o):
    """STAGES 'No floating dressing ... nothing buried': per shell, the deepest vertex / face centre inside every
    other shell (ray parity on that shell, depth = distance to its surface), judged against SINK_LIMIT; and shells
    whose every point is inside other shells (fully hidden)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = _keys(o)
    sf = {}
    for f in bm.faces:
        sf.setdefault(ids[f.index], []).append(f)
    info = []
    for s in range(n):
        fs = sf[s]
        vs = list({v for f in fs for v in f.verts})
        idx = {v: i for i, v in enumerate(vs)}
        co = [v.co.copy() for v in vs]
        lo = Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co)))
        hi = Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co)))
        tree = BVHTree.FromPolygons(co, [[idx[v] for v in f.verts] for f in fs])
        pts = co + [f.calc_center_median() for f in fs]
        info.append({"kind": _kind({keys[f.material_index] for f in fs}), "lo": lo, "hi": hi, "tree": tree,
                     "pts": pts})
    worst, over, hidden = {}, [], []
    for s, A in enumerate(info):
        inside_any = [False] * len(A["pts"])
        for t, B in enumerate(info):
            if s == t:
                continue
            if any(A["hi"][k] < B["lo"][k] - 1e-4 or A["lo"][k] > B["hi"][k] + 1e-4 for k in range(3)):
                continue
            dmax = 0.0
            for j, p in enumerate(A["pts"]):
                if not all(B["lo"][k] - 1e-4 <= p[k] <= B["hi"][k] + 1e-4 for k in range(3)):
                    continue
                if _parity_in(B["tree"], p):
                    inside_any[j] = True
                    dmax = max(dmax, B["tree"].find_nearest(p)[3])
            if dmax <= 0:
                continue
            pair = (A["kind"], B["kind"])
            worst[pair] = max(worst.get(pair, 0.0), dmax)
            lim = SINK_LIMIT.get(pair)
            if lim is not None and dmax > lim + 1e-3:
                over.append({"shell": s, "kind": A["kind"], "in": t, "in_kind": B["kind"], "depth": round(dmax, 3),
                             "at": [round(x, 2) for x in (A["lo"] + A["hi"]) / 2]})
        if all(inside_any):
            hidden.append({"shell": s, "kind": A["kind"], "at": [round(x, 2) for x in (A["lo"] + A["hi"]) / 2]})
    bm.free()
    return {"worst_depth": {f"{a_}>{b_}": round(d, 3) for (a_, b_), d in sorted(worst.items())},
            "over_limit": over, "fully_hidden": hidden, "buried": len(over) + len(hidden)}


def _plank_top(i, x_local, y):
    return PLANK_INFO[i]["m"] @ Vector((x_local, y, 0.0))


def walk_report():
    """Spec 2.1 walkability on the built planks: each plank's top tilt (deg), the steps between neighbouring planks'
    facing top edges across the walk band (|y| <= 2.2), the gaps, the end step from the stone top, the sill."""
    hw = PLANK_W / 2
    tilts, steps, gaps = [], [], []
    for i in range(NP):
        m = PLANK_INFO[i]["m"]
        nrm = (m.to_3x3() @ Vector((0, 0, 1))).normalized()
        tilts.append(round(math.degrees(math.acos(max(-1.0, min(1.0, nrm.z)))), 2))
    for i in range(NP - 1):
        worst, gap = 0.0, 9.0
        for y in (-LUG_IN, -1.1, 0.0, 1.1, LUG_IN):
            a_, b_ = _plank_top(i, hw, y), _plank_top(i + 1, -hw, y)
            worst = max(worst, abs(a_.z - b_.z))
            gap = min(gap, b_.x - a_.x)
        steps.append(round(worst, 3))
        gaps.append(round(gap, 3))
    ends = []
    for i, sx in ((0, -1), (NP - 1, 1)):
        for y in (-LUG_IN, 0.0, LUG_IN):
            p = _plank_top(i, sx * hw, y)
            ends.append({"edge_z": round(p.z, 3), "step": round(STONE_TOP - p.z, 3), "gap": round(ST_DECK - abs(p.x), 3)})
    return {"tilt_deg": tilts, "tilt_max": max(tilts), "steps": steps, "step_max": max(steps), "gaps": gaps,
            "ends": ends, "end_step_max": max(abs(e["step"]) for e in ends),
            "end_gap_max": max(e["gap"] for e in ends), "sill": round(BRACE_TOP - STONE_TOP, 3),
            "clear_width_bases": round(2 * (PY - BASE_H), 2), "clear_width_shafts": round(2 * (PY - SHAFT_H), 2),
            "tie_clear": GEO.get("tie_clear")}


def levels_report(h):
    """Spec 4.2.3 levels on the hero mesh (build frame = mesh + offset), plus the open-end check: no rope crossing an
    end between the two posts (|x| > 7.3, |y| < 2.0, above the stone tops)."""
    off = Vector(h[OFF])
    keys = _keys(h)
    bm = bmesh.new()
    bm.from_mesh(h.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    groups = {}
    for f in bm.faces:
        groups.setdefault(ids[f.index], []).append(f)
    stone_tops, posts, open_end = [], [], 0
    for k, fs in groups.items():
        vs = {v for f in fs for v in f.verts}
        co = [v.co + off for v in vs]
        kind = _kind({keys[f.material_index] for f in fs})
        if kind == "stone" and max(c.z for c in co) > 5.0:
            stone_tops.append(round(max(c.z for c in co), 3))
        if kind == "wood" and max(c.z for c in co) > 10.0:
            posts.append(round(max(c.z for c in co), 3))
        if kind == "rope":
            for c in co:
                if abs(c.x) > 7.3 and abs(c.y) < 1.5 and c.z > STONE_TOP + 0.4:
                    open_end += 1
                    break
    bm.free()
    mid = [PLANK_INFO[i]["m"] @ Vector((0, 0, 0)) for i in (4, 5)]
    ends = [PLANK_INFO[i]["m"] @ Vector((s * PLANK_W / 2, 0, 0)) for i, s in ((0, -1), (NP - 1, 1))]
    return {"stone_tops": sorted(stone_tops), "post_tops": sorted(posts), "coil_z": list(COIL_Z),
            "rope_low": GEO.get("rope_low"), "deck_mid_top": [round(p.z, 3) for p in mid],
            "deck_mid_curve": round(DECK_LOW, 3), "end_plank_outer_top": [round(p.z, 3) for p in ends],
            "brace_top": BRACE_TOP, "base_blocks": list(BASE_Z), "hanger_len": GEO.get("hanger_len"),
            "spur_depth": GEO.get("spur_depth"), "rope_across_open_end": open_end}


# ---- render measurement (spec "Pixel boxes and masks": W lit wood, K dark wood, Y rope, R cloth, S stone) ------------
SHEET_REF = {
    "f34": {"wh": 1.894, "W": 22.6, "K": 23.8, "Y": 2.8, "R": 1.7, "S": 49.0, "Yfifths": [0, 0.6, 28.8, 56.5, 14.2],
            "top": [.19, .52, .63, .86, .77, .85, .71, .68, .67, .65, .66, .67, .70, .72, .75, .80, .98, .99, .99, .76,
                    .47]},
    "r34": {"wh": 1.61, "W": 21.8, "K": 23.4, "Y": 2.9, "R": 1.6, "S": 50.3,
            "top": [.15, .52, .62, .84, .77, .81, .74, .69, .68, .67, .67, .69, .72, .76, .80, .86, .99, .89, .97, .72,
                    .44]},
    "front": {"wh": 2.431, "W": 19.0, "K": 19.4, "Y": 4.4, "R": 0.1, "S": 57.2,
              "top": [.05, .52, .64, .99, .93, .77, .72, .69, .65, .65, .63, .65, .65, .69, .71, .77, .81, .99, .98, .53,
                      .04]},
    "side": {"wh": 1.016, "W": 26.3, "K": 21.0, "Y": 1.8, "R": 0.0, "S": 50.9,
             "top": [.06, .08, .41, .45, .98, .99, .99, .98, .80, .78, .77, .77, .78, .83, .88, .99, .99, .98, .45, .43,
                     .05]},
    "rear": {"wh": 1.984, "W": 19.8, "K": 15.6, "Y": 3.7, "R": 3.6, "S": 57.4,
             "top": [.05, .53, .98, .99, .81, .77, .72, .69, .66, .65, .63, .63, .64, .67, .70, .74, .80, .98, .99, .57,
                     .04]},
    "top": {"wh": 2.096, "W": 41.5, "K": 20.7, "Y": 0.7, "R": 0.0, "S": 37.2},
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
    """The study's masks (m051_study/m.py cls) on 0-1 sRGB rows: dict of W, K, Y, R, S, B boolean arrays."""
    h, s, v = _hsv(px)
    T = (v < 0.16) | ((s < 0.25) & (v < 0.35)) | ((h > 200) & (h < 250) & (s > 0.25) & (v < 0.45))
    R_ = ~T & ((h < 12) | (h > 340)) & (s >= 0.45) & (v >= 0.35)
    Y = ~T & ~R_ & (((h >= 36) & (h <= 62) & (s >= 0.18) & (v >= 0.60)) |
                    ((h >= 33) & (h < 36) & (s >= 0.18) & (s < 0.62) & (v >= 0.75)))
    Wm = ~T & ~R_ & ~Y & ((h < 40) | (h > 345)) & (s >= 0.35) & (v >= 0.62)
    Km = ~T & ~R_ & ~Y & ~Wm & ((h < 40) | (h > 340)) & (s >= 0.25) & (v >= 0.16)
    grey = ~T & ~R_ & ~Y & ~Wm & ~Km & (s < 0.25)
    B = grey & (v >= 0.78) & (px[..., 2] - px[..., 0] >= 6 / 255) & (s < 0.09)
    S = grey & ~B & (v >= 0.30)
    return {"W": Wm, "K": Km, "Y": Y, "R": R_, "S": S, "B": B}


def measure(path, tol=18 / 255):
    kit = K.NS["KIT"]
    raw = kit["load_px"](path)[::-1]
    px = np.clip(raw[..., :3], 0, 1)
    bg = np.median(np.concatenate([px[:4, :4].reshape(-1, 3), px[:4, -4:].reshape(-1, 3)]), axis=0)
    sil = (np.abs(px - bg).max(-1) > tol) & (raw[..., 3] > 0.5)
    cl = {k: m & sil for k, m in classify(px).items()}
    ys, xs = np.nonzero(sil & ~cl["B"])
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    H, Wd = y1 - y0 + 1, x1 - x0 + 1
    tot = max(1, int(sum(cl[k].sum() for k in "WKYRS")))
    res = {"wh": round(Wd / H, 3)}
    for k in "WKYRS":
        res[k] = round(100 * cl[k].sum() / tot, 1)
    fr = [0] * 5
    for yy in np.nonzero(cl["Y"])[0]:
        fr[min(4, int((y1 - yy) / H * 5))] += 1
    res["Yfifths"] = [round(100 * f / max(1, sum(fr)), 1) for f in fr]
    obj = sil & ~cl["B"]
    prof = []
    for f in np.linspace(0, 1, 21):
        col = int(round(x0 + f * (Wd - 1)))
        on = np.nonzero(obj[:, col])[0]
        prof.append(round(float((y1 - on.min()) / (H - 1)), 2) if len(on) else 0.0)
    res["top"] = prof
    rgb = px * 255
    for k in "WKYRS":
        sel = rgb[cl[k]]
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


# ---- build ----------------------------------------------------------------------------------------------------------
TARGET_SIZE = ((27.2, 0.4), (12.0, 0.4), (11.0, 0.3))     # spec 1.1: with the stone spurs


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me is not None and isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m051_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", "RopeBridge"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


PART_FNS = ((POST_P, post_part), (BRACE_P, brace_part), (PEG_P, peg_part), (PLANK_P, plank_part),
            (MAIN_P, main_part), (HANG_P, hanger_part), (STONE_P, stone_part))


def build_objects(parts=True):
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in PART_FNS:
            objs[name], log[name] = _make_plain(name, fn)
    h, log["hero"] = _make_plain(HERO, hero_fn, role="hero", budget=4000)   # last: GEO / PLANK_INFO are the hero's
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
                  "zero_area_faces", "ngons", "dup_verts"):
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
    bury = {o.name: bury_report(o) for o in order if len(shells[o.name]) > 1}
    for n_, b in bury.items():
        if b["buried"]:
            problems.append(f"{n_}: {len(b['over_limit'])} shells sunk past their limit, {len(b['fully_hidden'])} "
                            f"fully hidden")
    levels = levels_report(h)
    walk = walk_report()
    if walk["tilt_max"] > 17.0:
        problems.append(f"{HERO}: plank tilt {walk['tilt_max']} > 17")
    if walk["step_max"] > 0.08:
        problems.append(f"{HERO}: step between planks {walk['step_max']} > 0.08")
    if walk["end_step_max"] > 0.08:
        problems.append(f"{HERO}: end step {walk['end_step_max']} > 0.08")
    if abs(walk["sill"] - 0.35) > 0.005:
        problems.append(f"{HERO}: sill {walk['sill']} != 0.35")
    if min(walk["tie_clear"] or [1.0]) < 0.02:
        problems.append(f"{HERO}: end tie within 0.02 of the stone corner {walk['tie_clear']}")
    if levels["rope_across_open_end"]:
        problems.append(f"{HERO}: rope across an open end")
    if any(abs(z - STONE_TOP) > 0.011 for z in levels["stone_tops"]) or len(levels["stone_tops"]) != 4:
        problems.append(f"{HERO}: stone tops {levels['stone_tops']}")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "LWH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (none planned)")
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
            "shells": kinds, "winding": winding, "contact": contact, "bury": bury, "levels": levels, "walk": walk,
            "thin": thin, "problems": problems, "uv": uv,
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


# ---- renders --------------------------------------------------------------------------------------------------------
# decision 14: f34_sheet (-20, 15) governs; r34_sheet (160, 22) (probe of e 18 / 22 / 25: W : H 1.68 in the 1.53-1.69 band); front_sheet (0, 0) the -Y side; side_sheet (90, 0)
# the +X end; rear_sheet (180, 0); top_sheet (0, 89.9). Floor hidden on every *_sheet shot.
SHEET_VIEWS = {"f34_sheet": (-20, 15), "r34_sheet": (160, 22), "front_sheet": (0, 0), "side_sheet": (90, 0),
               "rear_sheet": (180, 0), "top_sheet": (0, 89.9)}
# lens factor per shot (probe, Stage 1 notes): the sheet's three-quarters are near-orthographic; f34 at 6x gives W : H
# 1.855 (sheet 1.894) and W / K / S within a point of the sheet. The level orthos use 8x
LENS = {"f34_sheet": 6.0, "r34_sheet": 6.0}
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
    """Copies of the parts laid out like the sheet's Exploded Construction: the two stone ends apart, the posts lifted
    above their stones, the planks in a row between them with the main rope and hangers above, peg blocks and the
    brace at the post feet."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    o0 = Matrix.Translation((objs[0].location.x + 80, objs[0].location.y, 0))
    shown = []

    def put(tag, name, d, rot=0.0):
        if name not in by:
            return
        o = by[name]
        m = Matrix.Translation(Vector(o[OFF]))
        if rot:
            m = Matrix.Rotation(rot, 4, "Z") @ m
        shown.append(_copy(f"expl_{tag}", o, o0 @ Matrix.Translation(Vector(d)) @ m, coll))
    # parts are built in the hero frame (stone, post, brace, peg block at their -X / -Y places); plank and ropes at the
    # origin. Each end: two stones pulled apart, the posts lifted off them, the peg blocks and brace beside; the planks
    # in a row between, lifted; a main rope with hangers above. (The +X stones are the part turned half round, so the
    # +X / -Y one shows its cleft on the far side.)
    gap = 2.5
    put("stone_a", STONE_P, (-gap, -0.5, 0))
    put("stone_b", STONE_P, (-gap, 2 * PY + 0.5, 0))
    put("stone_c", STONE_P, (gap, 0.5, 0), math.pi)
    put("stone_d", STONE_P, (gap, -2 * PY - 0.5, 0), math.pi)
    put("post_a", POST_P, (-gap, -0.5, 2.6))
    put("post_b", POST_P, (-gap, 2 * PY + 0.5, 3.4))
    put("post_c", POST_P, (gap + 2 * PX, 2 * PY + 0.5, 3.4))
    put("post_d", POST_P, (gap + 2 * PX, -0.5, 2.6))
    put("brace_a", BRACE_P, (-gap, PY, 1.6))
    put("brace_b", BRACE_P, (gap + 2 * PX - 0.0, PY, 1.6))
    put("peg_a", PEG_P, (-gap + 1.2, -1.0, 1.0))
    put("peg_b", PEG_P, (gap + 2 * PX - 1.2, -1.0, 1.0))
    for i in range(NP):
        put(f"plank{i}", PLANK_P, (plank_x(i) * 1.15, 0, 5.4 + 0.05 * abs(plank_x(i))))
    put("main", MAIN_P, (0, -ROPE_Y, 9.4))
    for j, x in enumerate((-3.1, -1.4, 0.0, 1.4, 3.1)):
        put(f"hang{j}", HANG_P, (x, -ROPE_Y, 6.3))
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
    """5.5-stud character stand-ins: at mid-span on the deck, on an end plank, on the stone top between the brace and
    the deck (an end), and on the ground beside a stone."""
    mid = PLANK_INFO[4]["m"] @ Vector((0, 0, 0))
    endp = PLANK_INFO[NP - 1]["m"] @ Vector((0, 0, 0))
    return [_marker(h, (mid.x + 0.7, 0.0, mid.z), "char_mid"), _marker(h, (endp.x, 0.6, endp.z), "char_end_plank"),
            _marker(h, (-7.9, -0.5, STONE_TOP), "char_end"), _marker(h, (-15.0, -4.0, 0.0), "char_ground")]


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
            extra["part_" + o.name.replace("RopeBridge", "").lower()] = ([o], *PARTS_SHOT)
        if shown:
            extra["exploded"] = (shown, -25, 22)
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
            out["junc_cu"] = _close([h], f"{d}/junc_cu.png", -35, 18, fr @ Vector((-8.6, -3.0, 9.0)), 2.2)
            out["plank_cu"] = _close([h], f"{d}/plank_cu.png", -30, 35, fr @ Vector((-3.0, -2.6, 4.9)), 2.4)
            out["under_cu"] = _close([h], f"{d}/under_cu.png", 0, -60, fr @ Vector((0.0, 0.0, 4.0)), 4.2)
            out["rope_cu"] = _close([h], f"{d}/rope_cu.png", -10, 10, fr @ Vector((-2.8, -2.75, 7.2)), 1.6)
            out["knot_cu"] = _close([h], f"{d}/knot_cu.png", -60, 20, fr @ Vector((-10.4, -4.1, 6.2)), 1.3)
            out["cloth_cu"] = _close([h], f"{d}/cloth_cu.png", -45, 12, fr @ Vector((-9.6, 3.2, 8.4)), 1.4)
            out["stone_cu"] = _close([h], f"{d}/stone_cu.png", -30, 18, fr @ Vector((-10.5, -3.0, 2.8)), 4.0)
            out["end_cu"] = _close([h], f"{d}/end_cu.png", 60, 30, fr @ Vector((-8.0, 0.0, 5.8)), 3.0)
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
    "f34_sheet": {"plank_top": [(plank_x(i), y, None) for i in range(1, 9) for y in (-1.2, 0.0, 1.2)],
                  "post_face": [(-9.8, -3.0, 7.8), (-9.0, -3.8, 7.8)], "cap_top": [(-9.0, -3.0, POST_TOP)],
                  "stone_face": [(-11.0, -5.2, 3.0), (-12.5, -3.0, 2.5)], "stone_top": [(-11.2, -0.9, STONE_TOP), (-11.0, 1.2, STONE_TOP)],
                  "cloth": [(-9.87, -3.4, 8.45), (8.13, 2.6, 8.45)], "lug_side": [(plank_x(i), -2.65, None) for i in range(2, 8)]},
    "front_sheet": {"post_face": [(-9.0, -3.8, 7.8), (9.0, -3.8, 7.8)], "stone_face": [(-10.0, -5.3, 2.5),
                                                                                     (10.0, -5.3, 2.5)],
                    "lug_end": [(plank_x(i), -3.1, None) for i in range(1, 9)]},
}
SHEET_REGION = {"f34_sheet": {"plank_top": "#DA7E31", "post_face": "#9D4A16", "cap_top": "#A6521C",
                              "stone_face": "#C1B7AF", "stone_top": "#F3E8DB", "cloth": "#98200F",
                              "lug_side": "#6B3413"},
                "front_sheet": {"post_face": "#9D4D17", "stone_face": "#B9B1AC", "lug_end": "#9D4B1B"}}


def _region_pt(p):
    x, y, z = p
    if z is None:            # on a plank: its top at (x, y), or mid-lug on the lug end face
        i = min(range(NP), key=lambda k: abs(plank_x(k) - x))
        if abs(y) >= PLANK_HALF - 1e-6:
            return PLANK_INFO[i]["m"] @ Vector((0.0, y, -LUG_T * 0.3))
        if abs(y) > LUG_IN:
            return PLANK_INFO[i]["m"] @ Vector((-PLANK_W / 2, y, -LUG_T / 2))
        return PLANK_INFO[i]["m"] @ Vector((0.0, y, 0.0))
    return Vector(p)


def region_report():
    """Render f34_sheet and front_sheet again and sample each region (spec 5.4 warnings) against the sheet."""
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
            lens0 = cam.data.lens
            cam.data.lens = lens0 * LENS.get(view, SHEET_LENS)
            bpy.context.view_layer.update()
            qs = {name: [world_to_camera_view(sc, cam, fr @ _region_pt(p)) for p in pts] for name, pts in regs.items()}
            cam.data.lens = lens0
            res = {}
            for name in regs:
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


def preview(names=("f34_sheet", "front_sheet", "side_sheet", "top_sheet"), vfx=False, measure_too=True):
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = _lens(kit)
    try:
        sheet = M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig
    return {"sheet": sheet, "measure": measure_views() if measure_too else None}
