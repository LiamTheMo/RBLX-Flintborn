"""051 Rope Crossing (references/051.png, remade 2026-11-03), on the shared library (kit_parts / kit_build): a short
plank footbridge hung between two pairs of square timber end posts, each post on a chunky faceted anchor stone. Eight
chunky planks across the width hang on vertical hanger ropes from a sagging upper rope rail on each side and are tied
together by a lower rope rail through their ends. See M051_spec.md.

    import importlib, kit_parts, kit_build, m051
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m051); m051.build()

Build frame (studs): long axis X (the sheet's FRONT VIEW is the -Y long side), front -Y, ground z 0, centred on x 0 /
y 0, symmetric about both axes but for the stones' facets and chunks. Seam contract (binding):
- stone bases and chunks flat on z 0; walk surface at the ends = the stone tops, z ST = 3.47 (four 0.8675 risers;
  the sheet's character scale gives 3.3-3.8; spec "Departures");
- each end's stone pair meets in a 0.10 seam at y 0 on top, the cleft faces lean apart into a V gap below;
- the end planks' outer top edges at z ST, x +-4.72 (0.28 gap); the stones' deck-side faces at x +-5.00, vertical
  down to z 2.75 (clear of the end planks' feet), flaring to +-4.20 at the ground;
- post centres (+-6.10, +-2.30); stone tops x +-5.00 .. +-7.95, y +-0.05 .. +-3.35; deck low point 2.67 at x 0.
Walkability: both ends open (no rope across the entrance), 3.16 between the base blocks, 2.98 between the rope turns;
the deck a chain of tilted planks whose top edges lie on one sag curve, the end edges flush with the stone tops.

Every piece is its own closed shell (no booleans), seated 0.003-0.05 into what carries it:
- 4 anchor stones (lofted faceted shells with broad planar faces: deck-side face, leaning cleft face, facet ridges
  and grooves, chamfered outer top edges) with 2-4 boxy chunks each against their faces, stacked on the front stones;
- 4 posts: a chamfered base block, a shaft stepping out to a cap with a bevel and a dark peg hole; two twisted rope
  turns under each cap (m050 wraps), a red cloth wrap round the post's outer end under them, a bunched knot at both
  of its end corners with two splayed ribbon tails on the long face under each;
- 8 planks across the width (1.00 x 0.62 x 4.70, top edges on the sag curve), a square peg on each end face;
- per side: an upper rope rail (catenary, coil to coil) with a knot bulge at every hanger, 6 hangers (middle knot,
  knot foot on the plank), 2 diagonals from the coils to knot feet on the end planks, 2 backstays from the coils to
  knot feet on the stone tops, a lower rope rail of 7 links between the plank sides just inside the plank ends
  (|y| 2.22, seen between them). Knots are bulges of the rope
  itself (vrope), so no knot shell crosses a rope inside it.
Parts: RopeBridgeEndPost, RopeBridgePlank, RopeBridgeMainRope, RopeBridgeLowerRope, RopeBridgeHangerRope,
RopeBridgeAnchorStone. Stages 5-6: nothing (no glow, light or effect on the sheet).
"""
import math

import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_build as B
import kit_parts as P

NUM, TITLE = 51, "Rope Crossing"
HERO = "RopeBridge"
POST_P, PLANK_P, MAIN_P = "RopeBridgeEndPost", "RopeBridgePlank", "RopeBridgeMainRope"
LOWER_P, HANG_P, STONE_P = "RopeBridgeLowerRope", "RopeBridgeHangerRope", "RopeBridgeAnchorStone"

WOOD, WOOD_LIGHT, WOOD_DEEP, WOOD_DARK = "m051_wood", "m051_wood_light", "m051_wood_deep", "m051_wood_dark"
ROPE, ROPE_DARK, PEG = "m051_rope", "m051_rope_dark", "m051_peg"
CLOTH, CLOTH_DARK, STONE, STONE_MID = "m051_cloth", "m051_cloth_dark", "m051_stone", "m051_stone_mid"

# key -> (hex, roughness, metal, emission, low specular). Stage 4: calibrated against the sheet (spec "Stage 4").
PALETTE = {WOOD: ("#B06825", 0.85, 0.0, 0.0, True), WOOD_LIGHT: ("#E37D2C", 0.85, 0.0, 0.0, True),
           WOOD_DEEP: ("#9C4C15", 0.85, 0.0, 0.0, True), WOOD_DARK: ("#5E2909", 0.9, 0.0, 0.0, True),
           ROPE: ("#E09A36", 0.95, 0.0, 0.0, True), ROPE_DARK: ("#C78328", 0.95, 0.0, 0.0, True),
           PEG: ("#EDB641", 0.55, 0.0, 0.0, False), CLOTH: ("#B82418", 0.9, 0.0, 0.0, True),
           CLOTH_DARK: ("#951B11", 0.9, 0.0, 0.0, True), STONE: ("#ADAEB1", 0.92, 0.0, 0.0, True),
           STONE_MID: ("#84878F", 0.92, 0.0, 0.0, True)}
TARGETS = {}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)

# ---- layout (spec "Brief" and "Stage 1") -------------------------------------------------------------------------
ST = 3.47                               # stone tops = walk surface at the ends (4 risers of 0.8675; spec departure)
PX, PY = 6.10, 2.30                     # post centres (+-x, +-y)
POSTS = [(sx * PX, sy * PY) for sx in (-1, 1) for sy in (-1, 1)]
SEAT = 0.02                             # how far pieces sink into what carries them
BASE_H, BASE_Z1, BASE_CH = 0.72, ST + 0.80, 0.05        # base block half width, top, chamfer
SH, SH_CH = 0.55, 0.04                  # shaft half width, chamfer
CAP_H, CAP_TOP, CAP_T, CAP_BEV = 0.63, ST + 3.73, 0.75, 0.07
CAP_Z0 = CAP_TOP - CAP_T
HOLE, HOLE_D = 0.10, 0.06               # peg hole half size and depth on the cap top
WRAP_R, WRAP_SIDES, WRAP_PTS, WRAP_RC = 0.14, 6, 12, 0.10
WRAP_STEP = 2 * WRAP_R - 0.02
WRAP_Z = (CAP_Z0 - WRAP_R - 0.004, CAP_Z0 - WRAP_R - 0.004 - WRAP_STEP)     # upper, lower turn centres
WRAP_MID = (WRAP_Z[0] + WRAP_Z[1]) / 2
WRAP_OFF = SH + WRAP_R - 0.02           # turn centreline off the post axis (on the straight runs)
CLOTH_Z = (WRAP_Z[1] - WRAP_R - 0.46, WRAP_Z[1] - WRAP_R - 0.003)         # band, 0.003 under the lower turn
CLOTH_T, CLOTH_GAP = 0.05, 0.004
KNOT_C, KNOT_RP, KNOT_RZ = 0.10, 0.16, 0.15     # cloth knot lump: centre out of the corner (both ways), radii
TAIL_T = 0.05
# the two tails of a knot, side by side on the long face: (near edge from the corner, width, tip z, lean at the tip).
# The pair is 0.36 across under the knot (the sheet's front / rear / close-up 5 draw two narrow ribbons about that
# wide together) and splays to about 0.48 at the tips: the first leans toward the corner, the second away from it.
# Tips 0.09 / 0.21 over the base block top (4.27).
TAILS = ((0.03, 0.19, ST + 0.89, 0.03), (0.23, 0.16, ST + 1.01, -0.08))

NPL, PITCH, PL_W, PL_T, PL_Y = 8, 1.205, 1.00, 0.62, 2.35     # planks: count, pitch, width (x), thick, half length
PL_CH = 0.04
PLANK_X = [(i - (NPL - 1) / 2) * PITCH for i in range(NPL)]
D_END = PLANK_X[-1] + PL_W / 2          # 4.7175: the end planks' outer top edges
SAG = 0.80                              # deck top: ST at +-D_END, ST - SAG at mid-span
PEG_H, PEG_PROUD, PEG_DOME = 0.08, 0.06, 0.025

RY = 2.00                               # rope plane (upper rail, hangers) |y|
LOW_Y = 2.22                            # lower rail links |y|: just inside the plank ends, seen between them
MAIN_R, MAIN_SIDES, MAIN_N = 0.095, 6, 13
ROPE_LOW = ST + 0.90                    # upper rail centre at mid-span
MAIN_X = PX - WRAP_OFF - WRAP_R + 0.03  # upper rail ends: 0.03 into the turns' span side
KNOT_R = 0.18                           # knot bulges on the upper rail
HANG_R = 0.07
DIAG_R, BACK_R, LINK_R = 0.10, 0.11, 0.09
BACK_X = 7.35                           # backstay feet on the stone tops (|x|)

# stones (local u = |x|, v = |y|)
ST_DECK, ST_DECK_Z, ST_DECK_BASE = 5.00, ST - 0.72, 4.20       # vertical past the end plank's foot, then flaring in
ST_OUT_TOP, ST_OUT_BASE = 7.95, 8.30
ST_CL_TOP, ST_CL_BASE = 0.05, 0.80
ST_SIDE_TOP, ST_SIDE_BASE = 3.35, 3.60
ST_CH = 0.20
STONE_RINGS = (0.0, 0.30 * ST, ST_DECK_Z, ST - ST_CH)   # ring 1 only breaks the colour bands (faces stay planar)
STONE_BANDS = (0.45, 0.15)              # toward stone_mid below ring 1, between rings 1 and 2


def mix(k1, k2, t):
    return P.mix(k1, k2, t, step=0.05)


# ---- deck curve ------------------------------------------------------------------------------------------------------
def z_top(x):
    return ST - SAG + SAG * (x / D_END) ** 2


def plank_frame(x):
    """(centre of the plank's section, up normal, along-x direction) of the plank centred at x: its two top edges lie
    on the sag curve (a chord)."""
    h = PL_W / 2
    a, b = Vector((x - h, 0, z_top(x - h))), Vector((x + h, 0, z_top(x + h)))
    d = (b - a).normalized()
    n = Vector((-d.z, 0.0, d.x))
    c = (a + b) / 2 - n * (PL_T / 2)
    return c, n, d


def rope_z(x):
    """Upper rail centreline height: a catenary from WRAP_MID at x = +-MAIN_X to ROPE_LOW at 0."""
    c, sag = MAIN_X, WRAP_MID - ROPE_LOW
    lo, hi = 0.05, 100.0
    for _ in range(80):
        k = (lo + hi) / 2
        lo, hi = (k, hi) if k * (math.cosh(c / k) - 1) > sag else (lo, k)
    return ROPE_LOW + k * (math.cosh(x / k) - 1)


# ---- stones ----------------------------------------------------------------------------------------------------------
def _lerp(a, b, t):
    return a + (b - a) * t


def _deck_u(z):
    return ST_DECK if z >= ST_DECK_Z else _lerp(ST_DECK_BASE, ST_DECK, z / ST_DECK_Z)


def _out_u(z):
    return _lerp(ST_OUT_BASE, ST_OUT_TOP, min(z, ST) / ST)


def _side_v(z):
    return _lerp(ST_SIDE_BASE, ST_SIDE_TOP, min(z, ST) / ST)


def _cleft(z):
    return _lerp(ST_CL_BASE, ST_CL_TOP, min(z, ST) / ST)


def _isect(p, d, q, e):
    """The 2D intersection of the lines p + t d and q + s e."""
    den = d[0] * e[1] - d[1] * e[0]
    t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    return p[0] + t * d[0], p[1] + t * d[1]


# the base outline's edge roles (edge k runs from point k to k + 1): cleft, 3 outer x, corner cut, 3 outer y, deck
STONE_ROLES = ("cl", "ox", "ox", "ox", "cut", "oy", "oy", "oy", "dk")


def _inset(role, z, top=False):
    """How far the edge of that role stands in from its ground position at height z (negative: out). Linear in z on
    each face (the deck face kinks once, at ST_DECK_Z), so every face is one plane from the ground to the chamfer."""
    zz = min(z, ST)
    d = {"cl": _cleft(zz) - ST_CL_BASE, "ox": ST_OUT_BASE - _out_u(zz), "oy": ST_SIDE_BASE - _side_v(zz),
         "dk": _deck_u(zz) - ST_DECK_BASE}
    d["cut"] = (d["ox"] + d["oy"]) / 2
    return d[role] + (ST_CH if top and role in ("ox", "oy", "cut") else 0.0)


def stone_rings(name):
    """Local (u, v, z) rings of one anchor stone, 9 points each in the same order: deck/cleft corner, outer/cleft
    corner, two facet columns on the outer x face, the outer corner chamfer (2), two facet columns on the outer y face,
    deck/side corner. The ground outline carries the facet columns (each pushed out or in: a vertical ridge or groove,
    the sheet's facet breaks); every higher ring is that outline with each edge line moved in by its face's taper
    (_inset) and the corners re-intersected, so each side quad is a planar trapezoid: broad flat faces from the ground
    to the chamfer instead of a crumpled triangle pattern. The last ring is the flat top, inset ST_CH on the outer
    edges (the chamfer)."""
    r = P.rng(name)
    ox = [(r.uniform(0.9, 1.4), r.uniform(0.10, 0.22)), (r.uniform(2.2, 2.8), r.uniform(-0.20, -0.08))]
    oy = [(r.uniform(6.8, 7.2), r.uniform(-0.20, -0.08)), (r.uniform(5.6, 6.0), r.uniform(0.10, 0.22))]
    cut = r.uniform(0.35, 0.50)
    dk, ou, sv, cv = ST_DECK_BASE, ST_OUT_BASE, ST_SIDE_BASE, ST_CL_BASE
    base = [(dk, cv), (ou, cv), (ou + ox[0][1], ox[0][0]), (ou + ox[1][1], ox[1][0]), (ou, sv - cut), (ou - cut, sv),
            (oy[0][0], sv + oy[0][1]), (oy[1][0], sv + oy[1][1]), (dk, sv)]
    n = len(base)
    lines = []                          # (point, direction, inward unit normal) per edge; the outline runs CCW
    for k in range(n):
        p, q = base[k], base[(k + 1) % n]
        d = (q[0] - p[0], q[1] - p[1])
        L = math.hypot(*d)
        lines.append((p, d, (-d[1] / L, d[0] / L)))
    rings = []
    for z, top in [(z, False) for z in STONE_RINGS] + [(ST, True)]:
        moved = []
        for k, (p, d, nrm) in enumerate(lines):
            s = _inset(STONE_ROLES[k], z, top)
            moved.append(((p[0] + nrm[0] * s, p[1] + nrm[1] * s), d))
        ring = []
        for k in range(n):              # point k = edge k-1 meets edge k
            (p0, d0), (p1, d1) = moved[k - 1], moved[k]
            u, v = _isect(p0, d0, p1, d1)
            ring.append((u, v, z))
        rings.append(ring)
    return rings


def _loft(a, rings, key, name, kind):
    """A closed shell through rings of equal point count: quads between rings, centroid fans on the flat bottom and
    top (no slivers from the points along the straight top edges)."""
    n, R = len(rings[0]), len(rings)
    pts = [Vector(p) for r in rings for p in r]
    pts += [sum((Vector(p) for p in rings[0]), Vector()) / n, sum((Vector(p) for p in rings[-1]), Vector()) / n]
    ib, it = len(pts) - 2, len(pts) - 1
    faces = []
    for k in range(n):
        k1 = (k + 1) % n
        faces.append([ib, k1, k])
        faces.append([(R - 1) * n + k, (R - 1) * n + k1, it])
        for i in range(R - 1):          # triangles on the shorter diagonal (the facet quads are not planar)
            q = [i * n + k, i * n + k1, (i + 1) * n + k1, (i + 1) * n + k]
            if (pts[q[0]] - pts[q[2]]).length <= (pts[q[1]] - pts[q[3]]).length:
                faces += [[q[0], q[1], q[2]], [q[0], q[2], q[3]]]
            else:
                faces += [[q[0], q[1], q[3]], [q[1], q[2], q[3]]]
    return P.shell(a, pts, faces, key, name=name, kind=kind, amp=0.03)


def _hull_planes(pts):
    """Outward planes and surface samples (verts, edge midpoints, face centres) of the convex hull of pts."""
    bm = bmesh.new()
    vs = [bm.verts.new(Vector(p)) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    fs = [f for f in bm.faces if f.calc_area() > 1e-8]
    ctr = sum((Vector(p) for p in pts), Vector()) / len(pts)
    planes = []
    for f in fs:
        f.normal_update()
        n_, c_ = f.normal.copy(), f.calc_center_median()
        if n_.dot(ctr - c_) > 0:
            n_ = -n_
        if max(n_.dot(Vector(p)) - n_.dot(c_) for p in pts) < 1e-3:     # sliver faces give no reliable plane
            planes.append((n_, n_.dot(c_)))
    samp = []
    G = 5                               # a barycentric grid on every face: a face across a corner of the other hull
    for f in fs:                        # is deepest between its vertices
        a_, b_, c_ = (v.co.copy() for v in f.verts)
        samp += [(a_ * i + b_ * j + c_ * (G - i - j)) / G for i in range(G + 1) for j in range(G + 1 - i)]
    bm.free()
    return planes, samp


def _sd(planes, p):
    return max(n.dot(p) - d for n, d in planes)


# per stone (by name): (face, along, width along the face, height, depth out); "ox" outer x face, "oy" outer y face,
# "dk" the deck-side face. In order: a chunk listed where an earlier one stands comes to rest in front of it (stacked).
# The two front (-Y) stones carry the sheet's big stacked base blocks (up to 1.40 = 40 % of the stone height).
SPURS = {"stone-1-1": [("oy", 6.7, 1.7, 1.40, 0.8), ("oy", 6.3, 0.9, 0.55, 0.5), ("oy", 4.9, 1.0, 0.8, 0.55),
                       ("ox", 2.6, 1.2, 0.95, 0.55)],
         "stone-1+1": [("ox", 1.4, 0.9, 0.6, 0.35), ("oy", 6.4, 1.2, 0.7, 0.55)],
         "stone+1-1": [("oy", 6.5, 1.6, 1.25, 0.75), ("oy", 6.9, 0.8, 0.5, 0.45), ("ox", 2.6, 0.9, 0.6, 0.4)],
         "stone+1+1": [("ox", 2.7, 0.9, 0.55, 0.35), ("oy", 6.0, 1.4, 0.95, 0.6)]}
SPUR_SINK = 0.02


def _spur_points(w, h, dep, seed_name):
    """Local (along the face, out from the face, z) points: a boxy block (the sheet's base blocks) with near-vertical
    sides, a softened shoulder and one top corner broken down."""
    r = P.rng(seed_name)
    pts = []
    broken = r.randrange(4)
    for zf, rf in ((0.0, 1.0), (0.78, 0.97), (1.0, 0.80)):
        for k, (cx, cy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
            z = h * zf * ((1 + r.uniform(-0.05, 0.05)) if 0 < zf < 1 else 1)
            if zf == 1.0 and k == broken:
                z = h * r.uniform(0.80, 0.88)
            pts.append((cx * rf * r.uniform(0.90, 1.0) * w / 2, cy * rf * r.uniform(0.90, 1.0) * dep / 2, z))
    return pts


def spur(a, hulls, sx, sy, face, along, w, h, dep, name):
    """A faceted chunk on the ground against a stone face, pushed out along the face normal until it overlaps the
    nearest of `hulls` (the stone's points, then the chunks already placed against it) by SPUR_SINK (bisection,
    measured both ways on verts, edge midpoints and face centres). A chunk placed where a bigger one stands comes to
    rest against it, in front: the sheet's stacked base blocks. Returns its points."""
    if face == "ox":
        anchor, d, tg = Vector((sx * _out_u(0.0), sy * along, 0.0)), Vector((sx, 0.0, 0.0)), Vector((0, 1, 0))
    elif face == "oy":
        anchor, d, tg = Vector((sx * along, sy * _side_v(0.0), 0.0)), Vector((0.0, sy, 0.0)), Vector((1, 0, 0))
    else:
        anchor, d, tg = Vector((sx * _deck_u(0.0), sy * along, 0.0)), Vector((-sx, 0.0, 0.0)), Vector((0, 1, 0))
    base = [anchor + tg * pa + d * po + Vector((0, 0, z)) for pa, po, z in _spur_points(w, h, dep, name)]
    sp_planes, sp_samp = _hull_planes(base)
    others = []
    for pts in hulls:
        planes, samp = _hull_planes(pts)
        near = [q for q in samp if q.z < h + 0.5 and (q - anchor).length < w + 3.0]
        others.append((planes, near))

    def depth(t):
        sh = d * t
        worst = 0.0
        for planes, near in others:
            a_ = max(-_sd(planes, p + sh) for p in sp_samp)
            b_ = max(-max(n.dot(q - sh) - dd for n, dd in sp_planes) for q in near) if near else 0.0
            worst = max(worst, a_, b_)
        return worst
    lo, hi = -1.5, 4.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if depth(mid) > SPUR_SINK else (lo, mid)
    pts = [q + d * hi for q in base]
    p = P.hull(a, pts, mix(STONE, STONE_MID, 0.45), name=name, kind="stone_chunk", amp=0.03)
    P.texture(a, p.vs, 0.03, P.seed(name), scale=0.25)
    return pts


def stone(a, sx, sy, spurs=True):
    """One anchor stone under the post at (sx * PX, sy * PY), and its chunks. Colour by height and place: the warm
    light stone above, toward stone_mid in the two lower bands (ring to ring, so no break runs across a flat face)
    and in the cleft (never by facing)."""
    name = f"stone{sx:+d}{sy:+d}"
    rings = [[(sx * u, sy * v, z) for u, v, z in rg] for rg in stone_rings(name)]
    p = _loft(a, rings, STONE, name, "stone")
    for f in p.fs:
        c = f.calc_center_median()
        t = STONE_BANDS[0] if c.z < STONE_RINGS[1] else STONE_BANDS[1] if c.z < STONE_RINGS[2] else 0.0
        if abs(c.y) < 0.6 and c.z < ST - 0.01:
            t = max(t, 0.35)
        if t:
            f.material_index = a._mi(mix(STONE, STONE_MID, t))
    P.texture(a, p.vs, 0.035, P.seed(name), scale=0.18)
    if spurs:
        hulls = [[Vector(q) for rg in rings for q in rg]]
        for k, (face, along, w, h, dep) in enumerate(SPURS.get(name, ())):
            hulls.append(spur(a, hulls, sx, sy, face, along, w, h, dep, f"{name}_chunk{k}"))
    return p


# ---- posts -----------------------------------------------------------------------------------------------------------
def post(a, x, y, name):
    """Base block on the stone top, then one shell for the shaft and its cap: shaft 1.10 square stepping out to a 1.26
    cap, a bevel to the flat top, a dark peg hole in the top."""
    P.post(a, (x, y), ST - SEAT, BASE_Z1, BASE_H, mix(WOOD_DEEP, WOOD_DARK, 0.25), ch=BASE_CH,
           top_key=mix(WOOD_DEEP, WOOD_LIGHT, 0.3), name=name + "_base", kind="post_base")
    sh, cap, top = P.sec_rect(SH, SH, SH_CH), P.sec_rect(CAP_H, CAP_H, SH_CH), P.sec_rect(CAP_H - CAP_BEV,
                                                                                        CAP_H - CAP_BEV, SH_CH)
    hole = P.sec_rect(HOLE, HOLE, 0.02)
    ring = lambda sec, z: [(x + u, y + v, z) for u, v in sec]          # noqa: E731
    rings = [ring(sh, BASE_Z1 - SEAT), ring(sh, CAP_Z0), ring(cap, CAP_Z0), ring(cap, CAP_TOP - CAP_BEV),
             ring(top, CAP_TOP), ring(hole, CAP_TOP), ring(hole, CAP_TOP - HOLE_D)]
    light = mix(WOOD_DEEP, WOOD_LIGHT, 0.5)
    return P.prism(a, rings, WOOD_DEEP, caps=(True, True),
                   band_keys=[WOOD_DEEP, WOOD_DEEP, WOOD_DEEP, light, WOOD_LIGHT, WOOD_DARK],
                   cap_keys=(WOOD_DEEP, WOOD_DARK), name=name, kind="post")


def wraps(a, x, y, name):
    """Two round rope turns stacked under the cap (m050 wraps: straight runs, corners rounded on three points about a
    point WRAP_RC inside the shaft corner, 6-sided tubes with a groove strand), sunk 0.02 into the shaft, touching
    each other."""
    d = WRAP_R - 0.02
    out = []
    for t, z in enumerate(WRAP_Z):
        loop = []
        c, rc = SH - WRAP_RC, d + WRAP_RC
        for cx, cy, a0 in ((c, -c, -90), (c, c, 0), (-c, c, 90), (-c, -c, 180)):
            for k in range(WRAP_PTS // 4):
                ang = math.radians(a0 + 90 * k / (WRAP_PTS // 4 - 1))
                loop.append(Vector((x + cx + rc * math.cos(ang), y + cy + rc * math.sin(ang), z)))
        out.append(P.rope(a, loop, WRAP_R, ROPE, ROPE_DARK, sides=WRAP_SIDES, closed=True, twist=True, up=(0, 0, 1),
                          name=f"{name}_{t}", kind="rope_wrap"))
    return out


def knot_points(name):
    """Local (a, b, dz) points of a cloth knot at a band corner (a = out of the end face, b = out of the long face):
    a bunched lump about 0.35 across and 0.30 tall standing out of the corner, plus two anchors inside the band's
    0.05 thickness either side of the corner (their chord passes 0.046 inside the band's outer corner and clear of
    its inner one), so no knot edge cuts across the band (a thin sheet) and the band sits under 0.05 inside it."""
    r = P.rng(name)
    pts = [(a_, b_, dz) for a_, b_ in ((-0.005, -0.06), (-0.06, -0.005)) for dz in (-0.11, 0.11)]
    for zf, rf, n in ((-1.0, 0.62, 4), (0.0, 1.0, 5), (1.0, 0.62, 4)):
        off = r.uniform(0, 2 * math.pi)
        for k in range(n):
            th = off + 2 * math.pi * k / n + r.uniform(-0.25, 0.25)
            rr = KNOT_RP * rf * r.uniform(0.85, 1.08)
            pts.append((KNOT_C + rr * math.cos(th), KNOT_C + rr * math.sin(th), KNOT_RZ * zf * r.uniform(0.85, 1.0)))
    return pts


def cloth(a, x, y, name):
    """The red cloth: a wrap round the post's outer end (the end face and the outer halves of both long faces, 0.004
    off the shaft, 0.003 under the lower turn) and, at BOTH of its end corners, a bunched knot and two ribbon tails
    side by side on the long face (close-up 5). The tails hang from just under the knot over the wrap, settle 0.004
    off the shaft and splay at the tip (0.05 off the shaft, the second leaning away from the first, a little wider),
    down to 0.09-0.21 over the base block. So both long faces carry ribbons at the post's outer end, as the front, rear
    and f34 cells draw them; the end face shows only the wrap and the knots (the side cell shows no ribbons)."""
    sx = 1 if x > 0 else -1
    zc = sum(CLOTH_Z) / 2
    g, t, xm = CLOTH_GAP, CLOTH_T, x - sx * 0.12      # the wrap's open ends: 0.12 past the middle of the long faces
    xi, xo = x + sx * (SH + g), x + sx * (SH + g + t)
    yi, yo = SH + g, SH + g + t
    poly = [(xm, y - yo), (xo, y - yo), (xo, y + yo), (xm, y + yo), (xm, y + yi), (xi, y + yi), (xi, y - yi),
            (xm, y - yi)]
    if sx < 0:
        poly = list(reversed(poly))
    P.ext(a, poly, CLOTH_Z[0], CLOTH_Z[1], CLOTH, name=name + "_band", kind="cloth")
    kz = zc + 0.02
    top, below, inner = kz - KNOT_RZ - 0.02, CLOTH_Z[0] - 0.03, -(g + t) + 0.004   # inner: 0.004 off the shaft
    for s in (-1, 1):                                   # the (end, -Y) and (end, +Y) corners
        cn = "m" if s < 0 else "p"

        def at(a_, b_, z):
            return Vector((xo + sx * a_, y + s * (yo + b_), z))
        P.hull(a, [at(a_, b_, kz + dz) for a_, b_, dz in knot_points(f"{name}_knot{cn}")], CLOTH_DARK,
               name=f"{name}_knot{cn}", kind="cloth_knot")
        for k, (near, wid, low, lean) in enumerate(TAILS):
            hw, rings = wid / 2, []
            # (z, out from the face, half width, lean share): every ring level and at one offset, so each quad is a
            # planar trapezoid (a twisted or slanted tip gave non-planar quads that fail the parity check)
            for zz, o, w, ls in ((top, 0.003, hw, 0.0), (below, 0.003, hw, 0.15),
                                 ((below + low) / 2, inner, hw * 1.02, 0.5), (low, inner + 0.05, hw * 1.06, 1.0)):
                c = -(near + hw) + lean * ls             # along the long face from the corner (negative: toward the span)
                # across = a (along the long face), out = b
                rings.append([at(c + w, o, zz), at(c + w, o + TAIL_T, zz), at(c - w, o + TAIL_T, zz), at(c - w, o, zz)])
            P.prism(a, rings, CLOTH, name=f"{name}_tail{cn}{k}", kind="cloth_tail")


def post_set(a, x, y, tag):
    post(a, x, y, tag + "post")
    wraps(a, x, y, tag + "wrap")
    cloth(a, x, y, tag + "cloth")


# ---- deck ------------------------------------------------------------------------------------------------------------
def plank(a, x, name, level=False):
    """One plank across the width: a chamfered 1.00 x 0.62 beam, its two top edges on the sag curve; a square peg on
    each end face. level=True: lying flat with its top at ST (the part)."""
    if level:
        c, n = Vector((x, 0.0, ST - PL_T / 2)), Vector((0, 0, 1))
    else:
        c, n, _ = plank_frame(x)
    end = mix(WOOD, WOOD_DEEP, 0.3)
    p = P.plank(a, (c.x, -PL_Y, c.z), (c.x, PL_Y, c.z), PL_W, PL_T, WOOD, ch=PL_CH, up=n, cap_keys=(end, end),
                name=name, kind="plank", amp=0.06)
    for s in (-1, 1):
        P.bolt(a, (c.x, s * PL_Y, c.z), (0, s, 0), n, PEG, h=PEG_H, proud=PEG_PROUD, dome=PEG_DOME,
               name=f"{name}_peg{s:+d}", kind="peg")
    return p


def deck(a):
    for i, x in enumerate(PLANK_X):
        plank(a, x, f"plank{i}")


def plank_top(x):
    """The plank top's height at the plank centre x (on its chord)."""
    c, n, _ = plank_frame(x)
    return (c + n * (PL_T / 2)).z


# ---- rope ------------------------------------------------------------------------------------------------------------
def vrope(a, path, radii, sides=4, twist=True, name=None, kind="rope", deep=ROPE_DARK, up=None):
    """An open twisted rope whose radius changes along the path (P.tube with a radius per point): knots are bulges
    of the rope itself (rings of a larger radius), so no knot shell crosses the rope inside it. One strand in four
    (sides >= 4) in `deep`, by place in the twist (never by facing). Flat end caps; registered in P.ROPES."""
    Pp = [Vector(p) for p in path]
    N = len(Pp)
    upv = Vector(up) if up is not None else P.up_for(Pp)
    rings = []
    for i in range(N):
        tin = (Pp[i] - Pp[max(i - 1, 0)]) if i else (Pp[1] - Pp[0])
        tout = (Pp[min(i + 1, N - 1)] - Pp[i]) if i < N - 1 else tin
        tin, tout = tin.normalized(), tout.normalized()
        T = (tin + tout).normalized()
        U = (upv - upv.dot(T) * T)
        if U.length < 1e-6:
            U = T.orthogonal()
        U.normalize()
        V = T.cross(U)
        Bv = tout - tin
        bend = Bv.length > 1e-6
        if bend:
            Bv.normalize()
        sc = 1.0 / max(0.5, tin.dot(T)) - 1.0
        ring = []
        for k in range(sides):
            ang = 2 * math.pi * (k + (0.5 * i if twist else 0.0)) / sides
            off = (U * math.cos(ang) + V * math.sin(ang)) * radii[i]
            if bend:
                off += Bv * off.dot(Bv) * sc
            ring.append(Pp[i] + off)
        rings.append(ring)
    pts = [p for rg in rings for p in rg]
    faces, keys = [], []
    for i in range(N - 1):
        for k in range(sides):
            a0, a1 = i * sides + k, i * sides + (k + 1) % sides
            b0, b1 = (i + 1) * sides + k, (i + 1) * sides + (k + 1) % sides
            st = k if twist else (k - i) % sides
            if twist:
                faces += [[a0, a1, b0], [a1, b1, b0]]
            else:
                faces += [[a0, a1, b1], [a0, b1, b0]]
            keys += [deep if (deep and st == 0) else None] * 2
    faces.append(list(reversed(range(sides))))
    faces.append([(N - 1) * sides + k for k in range(sides)])
    keys += [None, None]
    p = P.shell(a, pts, faces, ROPE, keys=keys, recalc=False, name=name, kind=kind, amp=0.03)
    if name:
        P.ROPES.append({"name": p.name, "ends": [list(P.XF[-1] @ Pp[0]), list(P.XF[-1] @ Pp[-1])], "rt": radii[0]})
    return p


MAIN_KNOT = ((0.25, MAIN_R), (0.14, 0.158), (0.0, KNOT_R))          # (distance from the knot, radius) both ways
FOOT_KNOT = ((0.0, 0.112), (0.065, 0.135), (0.17, 0.14), (0.26, None))  # (height along the plank normal, radius)
MID_KNOT = ((-0.10, None), (0.0, 0.125), (0.10, None))


def hanger_xs():
    return PLANK_X[1:-1]


def main_rope(a, sy, name, knots=True):
    """The upper rope rail on side sy: a twisted 6-sided catenary from the coils' span sides, a knot bulge (rings of
    0.175 / 0.20 / 0.175) where each hanger hangs."""
    y = sy * RY
    kx = hanger_xs() if knots else []
    xs = {round(-MAIN_X + 2 * MAIN_X * i / (MAIN_N - 1), 4): MAIN_R for i in range(MAIN_N)}
    xs = {x: r for x, r in xs.items() if all(abs(x - k) > MAIN_KNOT[0][0] + 0.05 for k in kx)}
    for k in kx:
        for d, r in MAIN_KNOT:
            for s in ((-1, 1) if d else (1,)):
                xs[round(k + s * d, 4)] = r
    order = sorted(xs)
    return vrope(a, [(x, y, rope_z(x)) for x in order], [xs[x] for x in order], sides=MAIN_SIDES, name=name,
                 kind="rope_main", up=(0, 0, 1))


def foot(top_pt, n, r_rope):
    """Path points and radii of a rope's foot knot on a surface point top_pt with normal n, from the rope down: the
    last ring is the flat foot sunk SEAT."""
    base = Vector(top_pt) - Vector(n) * SEAT
    pts, rad = [], []
    for h, r in reversed(FOOT_KNOT):
        pts.append(base + Vector(n) * h)
        rad.append(r if r is not None else r_rope)
    return pts, rad


def hanger(a, x, y, top_pt, n, z_top_, name):
    """A hanger from inside a rail knot (0.05 up into its underside) down to a plank top: a 4-sided twisted rope with a
    knot bulge 38 % of the way up and a knot foot on the plank (along the plank's normal, sunk 0.02)."""
    fp, fr = foot(top_pt, n, HANG_R)
    zb = fp[0].z
    zm = zb + (z_top_ - zb) * 0.38
    pts, rad = [Vector((x, y, z_top_))], [HANG_R]
    for d, r in reversed(MID_KNOT):
        pts.append(Vector((x, y, zm + d)))
        rad.append(r if r is not None else HANG_R)
    return vrope(a, pts + fp, rad + fr, sides=4, name=name, kind="rope_hanger")


def plank_top_pt(x, y):
    """(point on the plank top at (x, y), the plank's up normal) for the plank centred at x."""
    c, n, _ = plank_frame(x)
    p = c + n * (PL_T / 2)
    return Vector((p.x, y, p.z)), n


def hang_top(x):
    return rope_z(x) - KNOT_R * 0.93 + 0.05


def hangers(a, sy, tag):
    for k, x in enumerate(hanger_xs()):
        tp, n = plank_top_pt(x, sy * RY)
        hanger(a, x, sy * RY, tp, n, hang_top(x), f"{tag}hanger{k}")


def coil_start(x, y, side, toward):
    """The start of a rope leaving the lower turn downward: under the turn, 0.05 outside its centreline on side `side`
    (+-1 along x), 0.04 above its underside, shifted along y by `toward` (the end disc lies about 0.03 into the turn)."""
    return Vector((x + side * (WRAP_OFF + 0.05), y + toward, WRAP_Z[1] - WRAP_R + 0.04))


def diagonal(a, x, y, name):
    """From under the lower turn on the post's span side down to a knot foot on the end plank's top."""
    sx, sy = (1 if x > 0 else -1), (1 if y > 0 else -1)
    tp, n = plank_top_pt(sx * PLANK_X[-1], sy * RY)
    fp, fr = foot(tp, n, DIAG_R)
    s = coil_start(x, y, -sx, sy * 0.20)
    return vrope(a, [s] + fp, [DIAG_R] + fr, sides=5, name=name, kind="rope_diag")


def backstay(a, x, y, name):
    """From under the lower turn on the post's end side down and outward to a knot foot on the stone top."""
    sx, sy = (1 if x > 0 else -1), (1 if y > 0 else -1)
    yy = y - sy * 0.20
    s = coil_start(x, y, sx, -sy * 0.20)
    pts, rad = [s], [BACK_R]
    for h, r in ((0.40, None), (0.28, 0.18), (0.13, 0.195), (0.0, 0.145)):
        pts.append(Vector((sx * BACK_X, yy, ST - SEAT + h)))
        rad.append(r if r is not None else BACK_R)
    return vrope(a, pts, rad, sides=5, name=name, kind="rope_back")


def lower_points(x_a, x_b, sy):
    """The lower rail's link between the planks centred at x_a and x_b on side sy, at |y| LOW_Y (just inside the
    plank ends, so it shows between them): from mid-height on plank a's face toward b to the same on b, each end 0.03
    inside its plank."""
    ca, na, da = plank_frame(x_a)
    cb, nb, db = plank_frame(x_b)
    pa = ca + da * (PL_W / 2)
    pb = cb - db * (PL_W / 2)
    dd = (pb - pa).normalized()
    pa, pb = pa - dd * 0.03, pb + dd * 0.03
    pa.y = pb.y = sy * LOW_Y
    return pa, pb


def lower_rope(a, sy, tag):
    for k in range(NPL - 1):
        pa, pb = lower_points(PLANK_X[k], PLANK_X[k + 1], sy)
        P.rope(a, [pa, pb], LINK_R, ROPE, ROPE_DARK, sides=4, twist=True, name=f"{tag}link{k}", kind="rope_link")


# ---- assemblies ------------------------------------------------------------------------------------------------------
def hero_fn(a):
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * PX, sy * PY
            tag = f"p{sx:+d}{sy:+d}_"
            stone(a, sx, sy)
            post_set(a, x, y, tag)
            diagonal(a, x, y, tag + "diag")
            backstay(a, x, y, tag + "back")
    deck(a)
    for sy in (-1, 1):
        tag = f"side{sy:+d}_"
        main_rope(a, sy, tag + "main")
        hangers(a, sy, tag)
        lower_rope(a, sy, tag)


def post_part(a):
    """The -X / -Y end post with its rope turns and cloth, standing on z ST (as in the hero)."""
    post_set(a, -PX, -PY, "")


def plank_part(a):
    plank(a, 0.0, "plank", level=True)


def main_part(a):
    """One upper rope rail between the coils, with its six knots."""
    main_rope(a, -1, "main")


def lower_part(a):
    """The hero's -Y lower rail links, end to end: every span between two plank faces is exactly a hero link
    (lower_points); the links are joined through the plank positions into one rope so the part is a single piece."""
    pts = []
    for k in range(NPL - 1):
        pts += list(lower_points(PLANK_X[k], PLANK_X[k + 1], -1))
    P.rope(a, pts, LINK_R, ROPE, ROPE_DARK, sides=4, twist=True, name="lower", kind="rope_lower")


def hanger_part(a):
    x = PLANK_X[3]
    tp, n = plank_top_pt(x, -RY)
    hanger(a, x, -RY, tp, n, hang_top(x), "hanger")


def stone_part(a):
    stone(a, -1, -1)


PARTS = ((POST_P, post_part), (PLANK_P, plank_part), (MAIN_P, main_part), (LOWER_P, lower_part),
         (HANG_P, hanger_part), (STONE_P, stone_part))
NOTES = {
    HERO: "Rope crossing (sheet 051, remade): 8 tilted planks across the width hung by hangers from two sagging upper "
          "rope rails and tied by lower rope rails, between two pairs of square end posts (rope turns, red cloth) on "
          "faceted anchor stones; stone tops 3.47 (walk surface at both ends, open ends), deck sagging to 2.67.",
    POST_P: "End Post: base block, 1.10 shaft and 1.26 cap with a peg hole, two rope turns and the red cloth lashing",
    PLANK_P: "Plank: one 1.00 x 0.62 x 4.70 plank with a square peg on each end face",
    MAIN_P: "Upper Rope Rail (Main Rope): one sagging twisted rope coil to coil with six knots",
    LOWER_P: "Lower Rope Rail: the hero's seven links between the plank ends, joined end to end into one rope",
    HANG_P: "Hanger Rope: one hanger with its middle and foot knots",
    STONE_P: "Anchor Stone: one faceted anchor stone with its chunks",
}
COLLISION = {HERO: "precise", POST_P: "hull", PLANK_P: "box", MAIN_P: "none", LOWER_P: "none", HANG_P: "none",
             STONE_P: "hull"}
BUDGETS = {HERO: 6000}
TARGET_SIZE = None
VIEWS = {"f34_sheet": (-20, 20), "r34_sheet": (160, 20), "front_sheet": (0, 0), "side_sheet": (90, 0),
         "rear_sheet": (180, 0), "top_sheet": (0, 89.9)}
EXPLODED = {POST_P: (-9.0, 1.5, 0.0), STONE_P: (-5.0, 0.0, 0.0), PLANK_P: (-1.0, 0.0, 0.0), HANG_P: (1.5, 0.0, 0.0),
            MAIN_P: (4.5, 4.0, 2.0), LOWER_P: (4.5, -4.0, 0.0)}
CLOSE = {"lash_cu": dict(at=(-6.1, -2.3, 5.2), r=2.4, az=-30, el=18),
         "hanger_cu": dict(at=(-3.0, -2.0, 3.3), r=2.2, az=-30, el=28)}
WALK = {"paths": [[(-7.6, 0.0), (7.6, 0.0)], [(-7.6, -0.3), (7.6, -0.3)], [(-7.6, 0.3), (7.6, 0.3)]],
        "feet_z": ST - SAG - 0.05, "skip": ("plank", "stone"), "turn": [(0.0, 0.0, ST - SAG), (-6.9, 0.0, ST)]}
# feet_z is the floor the proxy never sinks below: under the deck's low point, so it rides down the sag
VERIFY = dict(cls="structure", walk=WALK)
COMPARE = {"f34": {"box": (18, 140, 562, 440), "view": (-20, 20)},
           "r34": {"box": (570, 140, 1008, 440), "view": (160, 20)},
           "front": {"box": (20, 505, 312, 655), "view": (0, 0)},
           "side": {"box": (318, 505, 440, 655), "view": (90, 0)},
           "rear": {"box": (512, 505, 764, 655), "view": (180, 0)},
           "top": {"box": (768, 505, 1006, 655), "view": (0, 89.9)}}


def deck_check(objs):
    """Walk surface: the stone tops at ST, the end planks' outer top edges within 0.02 of ST, every plank top on the
    curve (rays down at each plank centre at y 0 and +-1.5)."""
    h = objs[HERO]
    me = h.data
    tree = BVHTree.FromPolygons([h.matrix_world @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])
    down = Vector((0, 0, -1))

    def z_at(x, y):
        hit = tree.ray_cast(MODEL.at(h, (x, y, 12.0)), down)[0]
        return round(hit.z - h.matrix_world.translation.z + h[MODEL.OFF][2], 3) if hit else None
    planks = {round(x, 3): [z_at(x, y) for y in (-1.5, 0.0, 1.5)] for x in PLANK_X}
    stones = [z_at(sx * 7.2, y) for sx in (-1, 1) for y in (-1.0, 0.6, 1.0)]
    edge = [z_at(sx * (D_END - 0.06), 0.0) for sx in (-1, 1)]       # inside the 0.04 chamfer
    rep = {"plank_tops": planks, "stone_tops": stones, "end_edges": edge, "rope_low": round(rope_z(0.0), 3),
           "deck_mid": round(plank_top(PLANK_X[NPL // 2]), 3)}
    pr = []
    for x, zs in planks.items():
        want = round(plank_top(x), 3)
        if any(z is None or abs(z - want) > 0.03 for z in zs):
            pr.append(f"{HERO}: plank at x {x} tops {zs} off {want}")
    if any(z is None or abs(z - ST) > 0.01 for z in stones):
        pr.append(f"{HERO}: stone tops {stones} off {ST}")
    if any(z is None or abs(z - ST) > 0.03 for z in edge):
        pr.append(f"{HERO}: end plank edges {edge} off {ST}")
    return rep, pr


def build(render=True, close=False):
    return MODEL.run(hero=(HERO, hero_fn), parts=PARTS, notes=NOTES, collision=COLLISION, budgets=BUDGETS,
                     target_size=TARGET_SIZE, views=VIEWS, close=CLOSE if close else None, verify=VERIFY,
                     checks=[deck_check], render=render, exploded=EXPLODED, scale=(0.0, -6.0, 0.0))


def preview(names=("f34_sheet", "side_sheet", "front_sheet")):
    return MODEL.preview(HERO, VIEWS, names)


def compare(cells=None, out_dir=None):
    import importlib
    import compare as C
    importlib.reload(C)
    return C.compare(NUM, {k: COMPARE[k] for k in (cells or COMPARE)}, out_dir=out_dir)
