"""040 Cliff Wall (references/040.png): a modular straight cliff-wall tile (16 x 8 studs, lawn top at z 10.4, the
plateau level of M032 Shoreline Corner). Its front is a palisade of five tall flat-faced rock columns (each a shaded
left face and a lit front face, dark full-height creases between them, all tops on one level line under the lip),
three pointed shards leaning on the lower face and a group of flat-topped boulder blocks at the front-left foot. A
separate grass top lip (a flat lime lawn over a blocky rock rim, flat recessed underside) caps every column; a flat
grey back-connector plate with three tabs on each long edge stands on the +X end. Lawn: two dark-green round bushes
with brown trunks, three lime bushes, two small boulders, pebbles and pale stepping patches. Foot: a lime grass
apron, a foot bush, a bush on the big boulder, lime sprigs at both ends, pebbles.

    import importlib, kit_models, m040; importlib.reload(kit_models); importlib.reload(m040); m040.build()

Build frame (studs): front -Y, +X right, ground z 0. W02 owns CliffWall*, so the names are StoneCliff* (spec 8):
- StoneCliffBody (body_part): the palisade (core and columns C1-C5, one lofted solid: each column an explicit
  prism front of 4-5 faces whose back corners are the core) with the shards A-C and the foot boulders Bb/Bs/Bf united
  into it (merge-0 exact unions at the world origin, then a floor cut at z 0). One closed shell.
- StoneCliffGrassLip (lip_part): the lip slab (turf over the rock rim, recessed underside) plus its lawn dressing,
  every leaf, trunk, pebble and patch its own closed shell. L4 (a lime bush) and the two lawn sprigs are hero-only
  (decision 8: the part stays under 1000 tris).
- StoneCliffBackConnector (connector_part): the plate with six tabs and the front-top notch. One closed shell.

The hero (StoneCliff, decision 5) is one object of separate closed shells: the body shell, the lip slab, the plate,
and each leaf, trunk, bush heart, pebble, patch, lawn boulder and apron patch.

TILE CONTRACT (spec 2.1; record in the export notes). Build frame:
- seams x = -8.0 and x = +8.0 (pitch 16.0): no rock or plate vertex past them; the core's -X end face is planar on
  x = -8 from z 0 to 9.2, its +X end on x = +8 in front of the plate (y -3.35 .. -0.2); the plate's outer face is on
  x = +8 (y 0.1 .. 4.0, z 0 .. 10.05). Foliage overhangs both seams by up to 0.8, symmetrically.
- back plane y = +4.0 (shallow facets inward only, to y >= 3.6). Back tabs stand 0.35 behind it.
- column tops z 9.2 (flat); lip bottom 9.17 (sunk 0.03 onto them); lip recess 9.5; turf 10.1 -> lawn top 10.4 (flat).
- lip front at the seams y -4.2 at x = +-8; the lip's -X end planar on x = -8 (z 9.17 .. 10.4); its +X end on x = +8
  in front of y -0.65 and at x = 7.98 over the plate (never coplanar with the plate's outer face).
- the +X end of the core steps in to x 7.62 behind y -0.2 (the plate overlaps it by 0.02); the 0.3-wide groove in
  front of the plate's front edge is the side cell's dark edge strip, with the front tabs crossing it.
In the hero object the build frame is at the object's origin + hero["m040_offset"] (bottom centre of the bbox).
Tile N+1 sits 16 studs along +X with the same rotation; its flat -X core end meets tile N's plate and +X core end.

Stages 5-6: nothing (decision 9: the sheet shows no glow, light or effect). See M040_spec.md.
"""
import math
import random
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt

import kit_mcp as K
import kit_models as M
import m011
import m012
import m016
import m033

NUM, TITLE, SHEET = 40, "Cliff Wall", "M040"
OFF = "m040_offset"
PFX = "_m040_"
HERO = "StoneCliff"
BODY_P, LIP_P, CONN_P = "StoneCliffBody", "StoneCliffGrassLip", "StoneCliffBackConnector"

ROCK, ROCK_LIGHT, ROCK_DEEP = "m040_rock", "m040_rock_light", "m040_rock_deep"
GRASS, GRASS_LIGHT, GRASS_DEEP = "m040_grass", "m040_grass_light", "m040_grass_deep"
LEAF, LEAF_LIT, LEAF_DEEP, LEAF_LIME = "m040_leaf", "m040_leaf_lit", "m040_leaf_deep", "m040_leaf_light"
TRUNK, CONN = "m040_trunk", "m040_connector"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low specular). Stage 4 (M040_spec.md "Stage 4"):
# Pass 1, K.calibrate on the kit test dome against TARGETS (rendered sRGB in brackets): rock #A38C86 (206,171,156),
# light #AD9E95 (219,194,174), deep #92807A (184,156,141), grass #9CAE14 (194,212,21), grass light #AEB923 ("vivid":
# the green filter drops it; 218,226,35), grass deep #879C06 (166,188,10), leaf #336922 (57,121,34), lit #68A038
# (124,193,58), deep #1A4611 (29,78,18), lime #89A203 (168,196,7), trunk #502401 (101,52,29), connector #74737B
# (145,140,142). The calibrated rock and rock_deep keys came out at hue 12-15 deg (the mauve edge, spec 3.8): both are
# turned to hue 19 deg at the same value and saturation (#A38F86, #928279), so every rock key is R > G > B, 19-23 deg.
# The connector key is warm grey, R > B (#797476; the earlier #76737A had B > R).
# Pass 2 (front_sheet / f34_sheet renders against the sheet's cells): the rock medians came out a little more
# saturated than the sheet's (front #BCA08E against #BEA59B, B 13 under): rock and rock_deep lose a little saturation at
# the same hue 19 deg (#A3938B, #92837C). The lawn's broad patches were softened to 10-20 % toward grass_light and
# 20-35 % toward grass_deep (the top view showed the big lawn triangles as patches).
PALETTE = {
    ROCK: ("#A3938B", 0.9, False),
    ROCK_LIGHT: ("#AD9E95", 0.9, False),
    ROCK_DEEP: ("#92837C", 0.9, False),
    GRASS: ("#9DAF06", 0.85, True),
    GRASS_LIGHT: ("#B0BA12", 0.85, True),
    GRASS_DEEP: ("#879C02", 0.85, True),
    LEAF: ("#336922", 0.85, True),
    LEAF_LIT: ("#68A038", 0.85, True),
    LEAF_DEEP: ("#1A4611", 0.85, True),
    LEAF_LIME: ("#89A203", 0.85, True),
    TRUNK: ("#502401", 0.95, False),
    CONN: ("#797476", 0.7, False),
}
# calibration targets (spec 5.4: rendered medians of unshadowed regions). Rock uses "all" (K.sample's stone filter
# drops sat > 0.18 and this warm stone is sat 0.23).
TARGETS = {ROCK: ((0xCC, 0xAD, 0x9D), "all"), ROCK_LIGHT: ((0xDD, 0xC1, 0xAE), "all"),
           ROCK_DEEP: ((0xBA, 0x9E, 0x8E), "all"),
           GRASS: ((0xC4, 0xD6, 0x14), "green"), GRASS_LIGHT: ((0xDB, 0xE3, 0x23), "vivid"),
           GRASS_DEEP: ((0xAA, 0xC0, 0x08), "green"),
           LEAF: ((0x3A, 0x7C, 0x22), "green"), LEAF_LIT: ((0x7F, 0xC4, 0x3A), "green"),
           LEAF_DEEP: ((0x1E, 0x4F, 0x12), "green"), LEAF_LIME: ((0xAC, 0xC7, 0x05), "green"),
           TRUNK: ((0x65, 0x34, 0x16), "brown"), CONN: ((0x93, 0x8C, 0x8F), "stone")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome. "all" keys are sampled with the
    floor dropped (M.sample). Returns {key: (hex, rendered)} and leaves the keys set."""
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
def _faces(verts):
    return K.faces_of([v for v in verts if v.is_valid])


def _tri(bm, faces):
    bmesh.ops.triangulate(bm, faces=[f for f in faces if f.is_valid and len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")


def _mottle(a, faces, amp, scale, seed, tint=1.0):
    """Broad Tint patches about 1/scale studs across (never per-face confetti); tint is a uniform per-piece factor."""
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in faces:
        k = (1.0 + amp * 1.6 * noise.noise(f.calc_center_median() * scale + off)) * tint
        for l in f.loops:
            t = l[a.tint_layer][0] * k
            l[a.tint_layer] = (t, t, t, 1.0)


def _mix(k1, k2, t, step=0.1):
    t = round(max(0.0, min(1.0, t)) / step) * step
    return K.mix_key(k1, k2, round(t, 2))


def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def _v2(p):
    return Vector((p[0], p[1]))


def _area2(P):
    return 0.5 * sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P)))


def _inside(p, poly):
    x, y = p[0], p[1]
    c = False
    n_ = len(poly)
    for i in range(n_):
        x1, y1 = poly[i][0], poly[i][1]
        x2, y2 = poly[(i + 1) % n_][0], poly[(i + 1) % n_][1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def _seg_d(p, a, b):
    ax, ay = a[0], a[1]
    bx, by = b[0], b[1]
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
    return math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)


def _poly_d(p, poly):
    return min(_seg_d(p, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))


def _resample(P, step, closed=True):
    """Points every <= step along a polyline (original corners kept)."""
    out = []
    n_ = len(P)
    rng_ = range(n_) if closed else range(n_ - 1)
    for i in rng_:
        a, b = _v2(P[i]), _v2(P[(i + 1) % n_])
        k = max(1, int(math.ceil((b - a).length / step)))
        for j in range(k):
            out.append(a.lerp(b, j / k))
    if not closed:
        out.append(_v2(P[-1]))
    return out


def _steiner(poly, spacing, margin, seed, holes=()):
    rng = random.Random(seed)
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    out = []
    y = min(ys) + spacing * 0.5
    j = 0
    while y < max(ys):
        x = min(xs) + spacing * (0.25 + 0.5 * (j % 2))
        while x < max(xs):
            p = Vector((x + rng.uniform(-0.2, 0.2) * spacing, y + rng.uniform(-0.2, 0.2) * spacing))
            if _inside(p, poly) and not any(_inside(p, h) for h in holes):
                if _poly_d(p, poly) > margin and all(_poly_d(p, h) > margin for h in holes):
                    out.append(p)
            x += spacing
        y += spacing
        j += 1
    return out


def _cdt(outer, holes=(), steiner=()):
    """Constrained triangulation of outer minus holes, plus interior points. Returns (coords [Vector2], tris CCW)
    where the first len(outer) coords are outer's points in order, then each hole's, then the Steiner points."""
    verts, faces = [], []
    for poly in [outer] + list(holes):
        idx = []
        for p in poly:
            idx.append(len(verts))
            verts.append(_v2(p))
        faces.append(idx)
    verts += [_v2(p) for p in steiner]
    co, _e, tf, ov, _oe, of = delaunay_2d_cdt(verts, [], faces, 0, 1e-6, True)
    # map output verts back to input indices (the CDT keeps input points; new points would mean crossings)
    back = {}
    for i, orig in enumerate(ov):
        if orig:
            back[i] = orig[0]
    tris = []
    for f, orig in zip(tf, of):
        if len(f) != 3 or not orig:
            continue
        if any(o_ >= 1 for o_ in orig) and len(holes):
            continue                         # a hole face
        if 0 not in orig:
            continue
        ids = [back.get(i) for i in f]
        if None in ids:
            raise RuntimeError("CDT added a point: the outline crosses itself")
        a_, b_, c_ = (verts[i] for i in ids)
        ar = (b_.x - a_.x) * (c_.y - a_.y) - (b_.y - a_.y) * (c_.x - a_.x)
        if abs(ar) < 1e-9:
            continue
        tris.append(tuple(ids) if ar > 0 else (ids[0], ids[2], ids[1]))
    return verts, tris


def _beautify(bm, faces):
    inner = [e for e in {e for f in faces for e in f.edges} if len(e.link_faces) == 2
             and all(g in faces for g in e.link_faces)]
    if inner:
        bmesh.ops.beautify_fill(bm, faces=faces, edges=inner)


def _cap(bm, verts2d, tris, z, up, vmap=None):
    """Faces over a 2D triangulation at height z (callable or number); vmap reuses existing verts by index."""
    vmap = dict(vmap or {})
    zf = z if callable(z) else (lambda p: z)
    for t in tris:
        for i in t:
            if i not in vmap:
                p = verts2d[i]
                vmap[i] = bm.verts.new((p.x, p.y, zf(p)))
    out = []
    for i, j, k in tris:
        q = (vmap[i], vmap[j], vmap[k]) if up else (vmap[i], vmap[k], vmap[j])
        out.append(bm.faces.new(q))
    return out, vmap


# ---- body: the palisade loft (core + columns C1-C5) -----------------------------------------------------------------------
Z_FOOT = -0.4              # the loft starts under the ground (floor cut at z 0 after the unions)
Z_TOP = 9.2                # column tops (flat, under the lip)
# the foot outline, CCW from the -X seam's front corner: the columns' explicit fronts (spec 1.3 / 2.2), then the +X
# end (stepping in to 7.62 behind the plate's groove), the flat back, the -X end. kind: seam (on a seam plane),
# chamfer, face, ridge, crease (between two columns), end (+X end behind the groove), back.
FRONT = [
    (-8.0, -3.2, "seam", "C1"),
    (-7.0, -4.18, "chamfer", "C1"),     # C1's dark left face = the -X end chamfer (1.0 x 1.0)
    (-6.05, -4.38, "ridge", "C1"),
    (-5.25, -4.2, "face", "C1"),
    (-4.8, -3.35, "crease", "C1"),      # C1 / C2
    (-4.25, -4.25, "face", "C2"),       # C2 dark left face
    (-3.4, -4.42, "face", "C2"),
    (-2.6, -4.52, "ridge", "C2"),       # C2: two big lit faces either side of its ridge
    (-1.7, -4.38, "face", "C2"),
    (-1.0, -4.15, "face", "C2"),
    (-0.55, -3.15, "crease", "C2"),     # C2 / C3 (C3 set back 0.4)
    (0.25, -3.95, "face", "C3"),
    (1.1, -4.08, "ridge", "C3"),
    (1.85, -3.92, "face", "C3"),
    (2.45, -3.2, "crease", "C3"),       # C3 / C4
    (3.3, -4.1, "face", "C4"),
    (4.2, -4.25, "ridge", "C4"),
    (4.85, -4.05, "face", "C4"),
    (5.25, -3.25, "crease", "C4"),      # C4 / C5
    (6.1, -4.0, "face", "C5"),
    (6.9, -4.12, "ridge", "C5"),
    (7.45, -3.98, "chamfer", "C5"),     # +X end chamfer 0.55 x 0.6
    (8.0, -3.35, "seam", "C5"),
]
GROOVE_Y = -0.2            # the core's +X end steps in here (the plate's front edge is at y 0.1)
CORE_X = 7.62              # the core's +X end behind the groove (the plate's inner face is at 7.6)
REST = [
    (8.0, GROOVE_Y, "seam", "E"),
    (CORE_X, GROOVE_Y, "end", "E"),
    (CORE_X, 1.9, "end", "E"),
    (CORE_X, 4.0, "back", "E"),
    (5.4, 3.75, "back", "B"),
    (3.0, 4.0, "back", "B"),
    (0.6, 3.7, "back", "B"),
    (-1.8, 3.95, "back", "B"),
    (-4.4, 3.72, "back", "B"),
    (-6.4, 3.95, "back", "B"),
    (-8.0, 4.0, "seam", "B"),
    (-8.0, 0.4, "seam", "B"),
]
COLUMNS = ("C1", "C2", "C3", "C4", "C5")
FRONT_KINDS = ("chamfer", "face", "ridge", "crease")
MID_Z = ((3.0, 0.75), (6.2, 0.75))   # the two mid rings: centre, +- spread (per vertex: staggered facet breaks)
PUSH = (0.14, 0.3)                   # mid-ring vertices pushed out / in (alternating rings) along the outline normal
SETBACK = {"ridge": 0.2, "face": 0.2, "chamfer": 0.2, "crease": 0.1}   # the batter: top ring back from the foot
BODY_INFO = {}


def outline():
    return FRONT + REST


def _normals2(P):
    out = []
    n_ = len(P)
    for i in range(n_):
        a, b, c = _v2(P[i - 1]), _v2(P[i]), _v2(P[(i + 1) % n_])
        t1, t2 = (b - a).normalized(), (c - b).normalized()
        nn = Vector((t1.y, -t1.x)) + Vector((t2.y, -t2.x))
        out.append(nn.normalized() if nn.length > 1e-6 else Vector((t1.y, -t1.x)))
    return out


def body_rings(seed=40101):
    """[(foot, mid1, mid2, top)] 3D points per outline vertex: the foot, two staggered mid rings (each vertex pushed
    in or out a little, so every column face breaks into tall strip facets about 3 studs high) and the flat top."""
    rng = random.Random(seed)
    P = outline()
    nrm = _normals2(P)
    rings = []
    for (x, y, kind, col), n in zip(P, nrm):
        foot = Vector((x, y, Z_FOOT))
        top = Vector((x, y, Z_TOP))
        if kind in SETBACK:
            top.y += SETBACK[kind]
        if kind == "chamfer":
            top.x += 0.12 if x < 0 else -0.12
        if kind == "seam" and y < -3.0:            # the seam's front corner leans back with the chamfer
            top.y += 0.15
        # a ring exactly on the ground: the floor cut then runs through ring vertices and adds no cut points along
        # the bottom edge (cut points on a straight run left needles in the underside)
        gnd = foot.lerp(top, -Z_FOOT / (Z_TOP - Z_FOOT))
        gnd.z = 0.0
        row = [foot, gnd]
        sgn = rng.choice((-1.0, 1.0))
        for zc, zs in MID_Z:
            zm = zc + rng.uniform(-zs, zs)
            t = (zm - Z_FOOT) / (Z_TOP - Z_FOOT)
            mid = foot.lerp(top, t)
            mid.z = zm
            if kind in FRONT_KINDS:
                push = sgn * (rng.uniform(*PUSH) if kind != "crease" else rng.uniform(0.08, 0.16))
                sgn = -sgn
                mid += Vector((n.x, n.y, 0.0)) * push
            elif kind == "seam" and y < -3.0:      # the seam's front corner: along the seam plane only
                mid.y -= sgn * rng.uniform(0.1, 0.2)
                sgn = -sgn
            elif kind == "back":
                mid.y -= rng.uniform(0.0, 0.3)       # relief inward only (<= 0.4)
            row.append(mid)
        row.append(top)
        rings.append(tuple(row))
    return rings


def top_front():
    """The body's top-ring front chain [(x, y, kind)] (what the lip has to cap)."""
    R = body_rings()
    return [(R[i][-1].x, R[i][-1].y, FRONT[i][2]) for i in range(len(FRONT))]


def palisade(a):
    """The core and columns: one closed lofted solid over the outline (foot, mid, top rings), flat top at Z_TOP and
    flat bottom at Z_FOOT. Each column's front faces are explicit planes (a dark left face turned toward -X, a lit
    front face turned a little toward +X), split twice along their height at two staggered mid rings (tall strip facets about 3 studs high)."""
    bm = a.bm
    before = set(bm.verts)
    P = outline()
    R = body_rings()
    n_ = len(P)
    lay = bm.faces.layers.int.get("m040_col") or bm.faces.layers.int.new("m040_col")
    cidx = {c: k + 1 for k, c in enumerate(("C1", "C2", "C3", "C4", "C5", "E", "B"))}
    ring = [[bm.verts.new(r[k]) for r in R] for k in range(len(R[0]))]
    foot, top = ring[0], ring[-1]
    side = []
    for i in range(n_):
        j = (i + 1) % n_
        col = P[i][3] if P[i][3] == P[j][3] else (P[i][3] if P[i][2] != "crease" else P[j][3])
        for lo, hi in zip(ring, ring[1:]):
            f = bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
            f[lay] = cidx[col]
            side.append(f)
    # split each quad along the diagonal that keeps the larger smallest corner (new faces keep the column tag)
    bmesh.ops.triangulate(bm, faces=side, quad_method="BEAUTY")
    # caps: CDT with interior points
    t2 = [_v2(r[-1]) for r in R]
    f2 = [_v2(r[0]) for r in R]
    co, tris = _cdt(t2, (), _steiner(t2, 2.6, 0.9, 40111))
    top_f, _ = _cap(bm, co, tris, Z_TOP, True, {i: top[i] for i in range(n_)})
    for f in top_f:
        f[lay] = 0
    co, tris = _cdt(f2, (), _steiner(f2, 2.6, 0.9, 40112))
    bot_f, _ = _cap(bm, co, tris, Z_FOOT, False, {i: foot[i] for i in range(n_)})
    for f in bot_f:
        f[lay] = 0
    _beautify(bm, top_f)
    _beautify(bm, [f for f in bot_f if f.is_valid])
    vs = [v for v in bm.verts if v not in before]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, ROCK, tint=1.0)
    mine = _faces(vs)
    caps = [f for f in mine if f[lay] == 0]
    owner = {f: next(c for c, k in cidx.items() if k == f[lay]) for f in mine if f[lay] > 0}
    _paint_columns(a, list(owner), caps, owner)
    BODY_INFO["palisade_tris"] = sum(len(f.verts) - 2 for f in mine)
    return vs


COL_TINT = {"C1": 1.02, "C2": 0.97, "C3": 1.03, "C4": 0.98, "C5": 1.01, "E": 1.0, "B": 1.0}
LIGHT_Z0 = 0.65 * Z_TOP      # rock_light rises from here to 40 % at the top (spec 5.5)
DEEP_Z = 1.5                 # rock_deep patches below this (15 %)


def _rock_key(c, nf, light_max=0.4, deep=0.15):
    """Stone colour by position only: lighter high up, broad deeper patches low down, a noise drift."""
    t = light_max * _clamp((c.z - LIGHT_Z0) / (Z_TOP - LIGHT_Z0))
    t += 0.08 * nf(c)
    if c.z < DEEP_Z and nf(c) > -0.05:
        return _mix(ROCK, ROCK_DEEP, deep, step=0.05)
    if t >= 0.05:
        return _mix(ROCK, ROCK_LIGHT, t)
    return ROCK


def _paint_columns(a, side, caps, owner):
    nf = K.noise_field(scale=0.2, seed=40121)
    for f in side:
        f.material_index = a._mi(_rock_key(f.calc_center_median(), nf))
    for f in caps:
        f.material_index = a._mi(ROCK)          # hidden tops and the ground: one plain stone (never by facing)
    for k, col in enumerate(("C1", "C2", "C3", "C4", "C5", "E", "B")):
        fs = [f for f in side if owner.get(f) == col]
        _mottle(a, fs, 0.04, 0.3, 40131 + k, tint=COL_TINT.get(col, 1.0))


# ---- shards and foot boulders --------------------------------------------------------------------------------------------
SHARDS = {
    # base polygon (z -0.25), apex; the mid ring bulges out a little so each side shows 2-3 long faces
    "A": dict(base=[(-1.4, -4.3), (-1.0, -5.0), (-0.2, -4.95), (0.05, -4.25), (-0.6, -3.7)],
              apex=(-0.6, -3.65, 6.5), seed=40201),
    "B": dict(base=[(1.85, -4.2), (2.5, -5.2), (4.0, -5.4), (5.4, -5.25), (6.0, -4.35), (4.2, -3.7)],
              apex=(4.2, -3.95, 7.0), seed=40202),
    "C": dict(base=[(6.2, -4.2), (6.6, -4.9), (7.4, -4.85), (7.7, -4.1), (7.0, -3.75)],
              apex=(7.05, -3.95, 4.1), seed=40203),
}
BLOCKS = {
    # centre, w, d, h, yaw (deg), top tilt (deg, down toward the front), sides, seed
    "Bb": ((-4.1, -5.0), 3.4, 2.4, 3.6, 8.0, 8.0, 6, 40211),
    "Bs": ((-6.0, -4.5), 2.0, 1.8, 3.2, -12.0, 6.0, 5, 40212),
    "Bf": ((-7.15, -5.0), 1.5, 1.4, 1.7, 20.0, 9.0, 5, 40213),
}
PIECE_FOOT = -0.25
ROCK_INFO = {}


def _hull_piece(a, pts, key):
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    for v in vs:
        if v.is_valid and not v.link_faces:
            bm.verts.remove(v)
    vs = [v for v in vs if v.is_valid]
    fs = _faces(vs)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=vs, edges=list({e for f in fs for e in f.edges}))
    vs = [v for v in vs if v.is_valid]
    _tri(bm, _faces(vs))
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, key, tint=1.0)
    return vs


def shard(a, name):
    s = SHARDS[name]
    rng = random.Random(s["seed"])
    base = [Vector((x, y, PIECE_FOOT)) for x, y in s["base"]]
    apex = Vector(s["apex"])
    cen = sum(base, Vector()) / len(base)
    pts = list(base) + [apex]
    for p in base:
        t = rng.uniform(0.38, 0.5)
        q = p.lerp(apex, t)
        axis = cen.lerp(apex, t)
        d = q - axis
        d.z = 0
        q += d * rng.uniform(0.12, 0.22)
        pts.append(q)
    vs = _hull_piece(a, pts, ROCK)
    nf = K.noise_field(scale=0.3, seed=s["seed"])
    for f in _faces(vs):
        c = f.calc_center_median()
        f.material_index = a._mi(_mix(ROCK, ROCK_DEEP, 0.1, step=0.05) if c.z < apex.z * 0.5 and nf(c) > -0.2
                                 else _rock_key(c, nf, light_max=0.25))
    _mottle(a, _faces(vs), 0.04, 0.4, s["seed"], tint=rng.uniform(0.97, 1.04))
    ROCK_INFO[name] = {"tris": sum(len(f.verts) - 2 for f in _faces(vs)), "apex": list(s["apex"])}
    return vs


def block_rock(a, name):
    """A flat-topped chunky block like a short column (spec 2.5: near-vertical sides, a flat top tilted to the front,
    never an egg): the hull of a foot ring, a shoulder ring and an inset top ring."""
    (cx, cy), w, d, h, yaw, tilt, n, seed = BLOCKS[name]
    rng = random.Random(seed)
    yr = math.radians(yaw)
    sl = math.tan(math.radians(tilt))
    ph = rng.uniform(0, 2 * math.pi / n)

    def ring(sc, jit):
        out = []
        for k in range(n):
            ang = ph + 2 * math.pi * k / n + rng.uniform(-0.12, 0.12)
            cx_, cy_ = math.cos(ang), math.sin(ang)
            lx = math.copysign(abs(cx_) ** 0.7, cx_) * w / 2 * sc * (1 + rng.uniform(-jit, jit))
            ly = math.copysign(abs(cy_) ** 0.7, cy_) * d / 2 * sc * (1 + rng.uniform(-jit, jit))
            out.append((cx + lx * math.cos(yr) - ly * math.sin(yr), cy + lx * math.sin(yr) + ly * math.cos(yr)))
        return out
    pts = []
    for x, y in ring(1.0, 0.05):
        pts.append(Vector((max(x, -7.93), y, PIECE_FOOT)))
    for x, y in ring(0.95, 0.05):
        pts.append(Vector((max(x, -7.93), y, h * 0.8 + (y - cy) * sl * 0.8 + rng.uniform(-0.08, 0.08))))
    for x, y in ring(0.68, 0.04):
        pts.append(Vector((max(x, -7.93), y, h + (y - cy) * sl)))
    vs = _hull_piece(a, pts, ROCK)
    nf = K.noise_field(scale=0.3, seed=seed)
    for f in _faces(vs):
        c = f.calc_center_median()
        f.material_index = a._mi(_mix(ROCK, ROCK_DEEP, 0.15, step=0.05) if c.z < DEEP_Z and nf(c) > -0.05
                                 else ROCK if c.z < h * 0.75 else _mix(ROCK, ROCK_LIGHT, 0.2))
    _mottle(a, _faces(vs), 0.04, 0.4, seed, tint=rng.uniform(0.96, 1.04))
    ROCK_INFO[name] = {"tris": sum(len(f.verts) - 2 for f in _faces(vs)), "h": h}
    return vs


def body_part(a):
    BODY_INFO.clear()
    palisade(a)
    for nm in ("Bs", "Bb", "Bf"):
        block_rock(a, nm)
    for nm in ("A", "B", "C"):
        shard(a, nm)


# ---- grass top lip ------------------------------------------------------------------------------------------------------
LIP_TOP, LIP_TURF, LIP_BOT, LIP_RECESS = 10.4, 10.1, 9.17, 9.5
SEAM_Y = -4.2
LIP_X1 = 7.98              # the lip's +X end over the plate
BLOCK_X = [-8.0, -6.5, -5.0, -3.55, -2.05, -0.55, 1.0, 2.5, 4.0, 5.5, 6.9, 8.0]
PROUD = (0.13, 0.22)       # the rim stands this far in front of the most forward column point under each block
DRIPS = (-6.6, -3.3, 0.3, 3.6, 6.4)
DRIP_Z, DRIP_LOW = 9.88, 9.62
STEP = 0.14                # half the length of a step between two rim blocks
RIM_W = (1.3, 1.0)         # rim width at the front, and at the ends / back (the flat recess inside it)
LIP_INFO = {}


def lip_outline(seed=40301):
    """(outline [(x, y)], kinds) of the lip, CCW: front blocks (each standing PROUD in front of the most forward
    column point under it, steps between blocks), the +X end (x 8.0, then 7.98 over the plate), back, -X end."""
    rng = random.Random(seed)
    tf = top_front()
    poly_front = [(x, y) for x, y, _k in tf]

    def most_forward(x0, x1):
        ys = []
        for i in range(len(poly_front) - 1):
            (ax, ay), (bx, by) = poly_front[i], poly_front[i + 1]
            for s in np.linspace(0, 1, 9):
                x = ax + (bx - ax) * s
                if x0 - 1e-6 <= x <= x1 + 1e-6:
                    ys.append(ay + (by - ay) * s)
        return min(ys)
    blocks = []
    for i in range(len(BLOCK_X) - 1):
        x0, x1 = BLOCK_X[i], BLOCK_X[i + 1]
        y = most_forward(x0 - 0.25, x1 + 0.25) - rng.uniform(*PROUD)
        blocks.append((x0, x1, y))
    pts, kinds = [(-8.0, SEAM_Y)], ["front_seam"]
    for i, (x0, x1, y) in enumerate(blocks):
        if i > 0:
            py = blocks[i - 1][2]
            if abs(py - y) < 0.09:
                pts[-1] = (x0, (py + y) / 2)          # merge: one corner, no step
            else:
                pts.append((x0 + STEP, y))            # a short step between two blocks
                kinds.append("front")
        if i < len(blocks) - 1:
            pts.append((x1 - STEP, y))
            kinds.append("front")
    pts.append((8.0, SEAM_Y))                         # the last block runs to the +X seam corner
    kinds.append("front_seam")
    end =[(8.0, -1.9), (8.0, -0.65), (LIP_X1, -0.25), (LIP_X1, 1.6), (LIP_X1, 4.0)]
    pts += end
    kinds += ["end"] * len(end)
    back = _resample([(LIP_X1, 4.0), (-8.0, 4.0)], 2.0, closed=False)[1:]
    pts += [(p.x, p.y) for p in back]
    kinds += ["back"] * len(back)
    mx = _resample([(-8.0, 4.0), (-8.0, SEAM_Y)], 1.65, closed=False)[1:-1]
    pts += [(p.x, p.y) for p in mx]
    kinds += ["end"] * len(mx)
    return pts, kinds


def lip_inner():
    """The rim's inner edge (the recess outline), CCW, resampled every <= 1.4."""
    x0, x1 = -8.0 + RIM_W[1], LIP_X1 - RIM_W[1]
    y0, y1 = SEAM_Y + RIM_W[0] + 0.1, 4.0 - RIM_W[1]
    return [Vector((p.x, p.y)) for p in _resample([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 1.9)]


def lip_slab(a, seed=40311):
    """The lip as one closed solid: lawn top (10.4, CDT with interior points), outer wall rings at 10.4 / 10.1 (turf
    over rim) / the drip line (front only) / 9.17, a flat rim bottom (annulus) at 9.17, an inner wall up to the flat
    recess at 9.5."""
    bm = a.bm
    before = set(bm.verts)
    O, kinds = lip_outline()
    O = [_v2(p) for p in O]
    I = lip_inner()
    n_ = len(O)
    rng = random.Random(seed)
    # top
    # interior points: a row 0.85 inside each front block (keeps the triangles at the blocky edge open) and a
    # coarse grid
    row = [Vector(((BLOCK_X[i] + BLOCK_X[i + 1]) / 2, -3.55)) for i in range(len(BLOCK_X) - 1)]
    st = row + [p for p in _steiner(O, 2.5, 0.75, seed + 1) if p.y > -2.4]
    co, tris = _cdt(O, (), st)
    top_f, tmap = _cap(bm, co, tris, LIP_TOP, True)
    _beautify(bm, top_f)
    top_v = [tmap[i] for i in range(n_)]
    # wall columns
    cols = []
    for i, (p, k) in enumerate(zip(O, kinds)):
        c = [None, bm.verts.new((p.x, p.y, LIP_BOT))]
        if k.startswith("front"):
            dz = DRIP_LOW if _drip_block(p.x) and k == "front" else DRIP_Z
            c.append(bm.verts.new((p.x, p.y, dz + rng.uniform(-0.03, 0.03))))
        c.append(bm.verts.new((p.x, p.y, LIP_TURF)))
        c.append(top_v[i])
        cols.append(c[1:])
    wall_f = []
    for i in range(n_):
        j = (i + 1) % n_
        ci, cj = cols[i], cols[j]
        if len(ci) == len(cj):
            for k in range(len(ci) - 1):
                wall_f.append(bm.faces.new((ci[k], cj[k], cj[k + 1], ci[k + 1])))
        else:
            # one face round both columns (a front corner meets an end wall), triangulated below
            wall_f.append(bm.faces.new([ci[0], cj[0]] + list(cj[1:]) + list(reversed(ci[1:]))))
    # bottom annulus at LIP_BOT and the inner wall / recess
    co, tris = _cdt(O, [I])
    bmap = {i: cols[i][0] for i in range(n_)}
    bot_f, bmap = _cap(bm, co, tris, LIP_BOT, False, bmap)
    _beautify(bm, bot_f)
    ib = [bmap[n_ + k] if (n_ + k) in bmap else bm.verts.new((I[k].x, I[k].y, LIP_BOT)) for k in range(len(I))]
    it = [bm.verts.new((p.x, p.y, LIP_RECESS)) for p in I]
    in_f = []
    m_ = len(I)
    for k in range(m_):
        l = (k + 1) % m_
        in_f.append(bm.faces.new((ib[k], it[k], it[l], ib[l])))
    co2, tris2 = _cdt(I, (), _steiner(I, 3.2, 1.2, seed + 3))
    rec_f, _ = _cap(bm, co2, tris2, LIP_RECESS, False, {k: it[k] for k in range(m_)})
    _beautify(bm, rec_f)
    _tri(bm, [f for f in wall_f + in_f if f.is_valid])
    vs = [v for v in bm.verts if v not in before]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    bm.normal_update()
    a._finish(vs, ROCK, tint=1.0)
    _paint_lip(a, vs, O)
    LIP_INFO["outline"] = [(round(p.x, 3), round(p.y, 3)) for p in O]
    LIP_INFO["tris"] = sum(len(f.verts) - 2 for f in _faces(vs))
    return vs


def _drip_block(x):
    """Whether x lies on one of the front rim blocks the turf drips over (the block nearest each DRIPS x)."""
    for d in DRIPS:
        i = min(range(len(BLOCK_X) - 1), key=lambda k: abs((BLOCK_X[k] + BLOCK_X[k + 1]) / 2 - d))
        if BLOCK_X[i] + STEP * 0.5 <= x <= BLOCK_X[i + 1] - STEP * 0.5:
            return True
    return False


ROOTS = []                  # (x, y, r) bush roots and lawn boulders: the lawn deepens round them (filled by lawn())


def _paint_lip(a, vs, O):
    nf = K.noise_field(scale=0.22, seed=40321)
    nr = K.noise_field(scale=0.6, seed=40322)
    rim_faces = []
    for f in _faces(vs):
        c = f.calc_center_median()
        if f.normal.z > 0.95 and c.z > LIP_TOP - 0.01:
            # lawn: base, broad lighter patches, deeper round roots and boulders
            near = min([math.hypot(c.x - x, c.y - y) - r for x, y, r in ROOTS] or [9.0])
            if near < 0.6:
                key = _mix(GRASS, GRASS_DEEP, 0.35 if near < 0.1 else 0.2, step=0.05)
            elif nf(c) > 0.12:
                key = _mix(GRASS, GRASS_LIGHT, 0.2 if nf(c) > 0.3 else 0.1, step=0.05)
            else:
                key = GRASS
            f.material_index = a._mi(key)
            continue
        zlo = min(v.co.z for v in f.verts)
        wall = abs(f.normal.z) < 0.5 and _poly_d(c, O) < 0.05
        if wall and zlo > LIP_TURF - 0.01:
            f.material_index = a._mi(GRASS)                       # the turf band on the outer wall
        elif wall and zlo > DRIP_LOW - 0.05 and _drip_block(c.x) and c.y < -3.0:
            f.material_index = a._mi(GRASS_DEEP)                  # a green drip over the rim
        elif wall:
            # the rim: the lightest stone (spec 5.5, 45 % toward rock_light), a per-block drift
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.25 + 0.15 * nr(c)))
            rim_faces.append(f)
        else:
            f.material_index = a._mi(ROCK)                        # underside, recess, inner wall: plain stone
    _mottle(a, [f for f in _faces(vs) if f.normal.z > 0.95], 0.04, 0.4, 40323)
    _mottle(a, rim_faces, 0.04, 0.5, 40324)


# ---- dressing: leaves, bushes, sprigs, rocks, pebbles, patches, apron -----------------------------------------------------
def _leaf(a, base, L, W, key, yaw, pitch, fold=0.16, curl=0.14, cam=0.11, th=0.06, roll=0.0):
    """A broad diamond leaf with a pointed tip (8 tris, closed): a 4-point outline cupped up at the sides, a raised
    midrib point on top and one point underneath."""
    bm = a.bm
    rot = Matrix.Rotation(yaw, 3, "Z") @ Matrix.Rotation(-pitch, 3, "Y") @ Matrix.Rotation(roll, 3, "X")
    B = Vector(base)

    def P(x, y, z):
        t = x / L
        return bm.verts.new(B + rot @ Vector((x, y, z + fold * abs(y) - curl * L * t * t)))
    o = [P(0, 0, 0), P(0.45 * L, -W / 2, 0), P(L, 0, 0), P(0.45 * L, W / 2, 0)]
    up = P(0.45 * L, 0, cam * L)
    dn = P(0.45 * L, 0, -th * L)
    fs = []
    for i in range(4):
        j = (i + 1) % 4
        fs.append(bm.faces.new((o[i], o[j], up)))
        fs.append(bm.faces.new((o[j], o[i], dn)))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    vs = o + [up, dn]
    a._finish(vs, key)
    return vs


def _bipyramid(a, centre, r, hu, hd, key, seed, n=6):
    rng = random.Random(seed)
    bm = a.bm
    off = rng.uniform(0, math.pi)
    ring = [bm.verts.new(Vector(centre) + Vector((math.cos(off + k * 2 * math.pi / n) * r * rng.uniform(0.9, 1.05),
                                                  math.sin(off + k * 2 * math.pi / n) * r * rng.uniform(0.9, 1.05),
                                                  rng.uniform(-0.06, 0.06) * r))) for k in range(n)]
    top = bm.verts.new(Vector(centre) + Vector((0, 0, hu)))
    bot = bm.verts.new(Vector(centre) + Vector((0, 0, -hd)))
    fs = []
    for k in range(n):
        j = (k + 1) % n
        fs.append(bm.faces.new((ring[k], ring[j], top)))
        fs.append(bm.faces.new((ring[j], ring[k], bot)))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    vs = ring + [top, bot]
    a._finish(vs, key)
    return vs


def _tree_of(vs):
    fs = _faces(vs)
    idx = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[idx[v] for v in f.verts] for f in fs])


def _touch(vs, tree, gap=0.012):
    """Slide a leaf toward the heart until it touches it (its nearest vertex `gap` from the heart's surface), unless
    it already cuts into it."""
    if _tree_of(vs).overlap(tree):
        return 0.0
    best = None
    for v in vs:
        q, _n, _i, d = tree.find_nearest(v.co)
        if q is not None and (best is None or d < best[0]):
            best = (d, v.co.copy(), q)
    if best is None or best[0] <= gap:
        return 0.0
    d, p_, q = best
    mv = (q - p_) * (1.0 - gap / d) + (q - p_).normalized() * 0.03     # and 0.03 into it
    for v in vs:
        v.co += mv
    return d


def _dome_heart(a, C, r, h, zbot, key, seed, n=5):
    """A bush's hidden heart: a low closed dome (a ring at C, a smaller ring 0.6 h up, a top point; underneath a point
    down to zbot, or 0.6 h below C when zbot is None), 20 tris."""
    rng = random.Random(seed)
    bm = a.bm
    off = rng.uniform(0, math.pi)
    r1 = [bm.verts.new(C + Vector((math.cos(off + 2 * math.pi * k / n) * r, math.sin(off + 2 * math.pi * k / n) * r,
                                   rng.uniform(-0.05, 0.05) * h))) for k in range(n)]
    r2 = [bm.verts.new(C + Vector((math.cos(off + math.pi / n + 2 * math.pi * k / n) * r * 0.62,
                                   math.sin(off + math.pi / n + 2 * math.pi * k / n) * r * 0.62, 0.62 * h)))
          for k in range(n)]
    top = bm.verts.new(C + Vector((0, 0, h)))
    bot = bm.verts.new(Vector((C.x, C.y, zbot if zbot is not None else C.z - 0.6 * h)))
    fs = []
    for k in range(n):
        j = (k + 1) % n
        fs.append(bm.faces.new((r1[k], r1[j], r2[k])))
        fs.append(bm.faces.new((r1[j], r2[j], r2[k])))
        fs.append(bm.faces.new((r2[k], r2[j], top)))
        fs.append(bm.faces.new((r1[j], r1[k], bot)))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    vs = r1 + r2 + [top, bot]
    a._finish(vs, key)
    return vs


def _prism(a, centre, z0, z1, r0, r1, key, seed, n=5, sq=(1.0, 1.0)):
    """A closed tapered n-sided prism (trunks, pebbles): flat bottom and top."""
    rng = random.Random(seed)
    bm = a.bm
    off = rng.uniform(0, 2 * math.pi)
    angs = [off + 2 * math.pi * k / n + rng.uniform(-0.15, 0.15) for k in range(n)]
    lo = [bm.verts.new((centre[0] + math.cos(t) * r0 * sq[0], centre[1] + math.sin(t) * r0 * sq[1], z0)) for t in angs]
    hi = [bm.verts.new((centre[0] + math.cos(t) * r1 * sq[0], centre[1] + math.sin(t) * r1 * sq[1], z1)) for t in angs]
    fs = []
    for k in range(n):
        j = (k + 1) % n
        fs.append(bm.faces.new((lo[k], lo[j], hi[j], hi[k])))
    fs.append(bm.faces.new(list(reversed(lo))))
    fs.append(bm.faces.new(hi))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    _tri(bm, fs)
    vs = lo + hi
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, key)
    return vs


PLANT_INFO = {}


def bush(a, name, c, z0, R, H, kind, seed, trunk=None, guard=None):
    """A round leafy bush (spec 1.4): a dome of broad pointed leaves laid like shingles over a deep-green heart (a
    low dome solid, so the clump reads as one rounded mass and its gaps look like the shaded inside), the dark kind on
    a short brown trunk. Leaves sit on a golden spiral over the dome, each pointing outward and down along it with its
    face out of the dome: from above a rosette with a dark centre, from the side a rounded leafy dome. Colour by
    height on the dome (crown lit, skirt deep), never by facing. Returns all verts."""
    rng = random.Random(seed)
    tint = 1.0 + rng.uniform(-0.04, 0.04)
    dark = kind == "dark"
    out = []
    if dark:
        n, zc, Rd, Hd, Lf, th = 14, 0.54, 0.80, 0.42, 0.62, (12.0, 108.0)
        keys = (_mix(LEAF, LEAF_LIT, 0.4), LEAF, _mix(LEAF, LEAF_DEEP, 0.4))
        heart = _mix(LEAF, LEAF_DEEP, 0.6)
    else:
        n, zc, Rd, Hd, Lf, th = 8, 0.42, 0.80, 0.50, 0.70, (12.0, 100.0)
        keys = (LEAF_LIME, LEAF_LIME, _mix(LEAF_LIME, LEAF, 0.25))
        heart = _mix(LEAF_LIME, LEAF_DEEP, 0.3)
    C = Vector((c[0], c[1], z0 + zc * H))
    rx, hz = Rd * R, Hd * H
    hvs = _dome_heart(a, C, 0.86 * rx, 0.86 * hz, (z0 - 0.02) if z0 > 0.5 else (z0 if not dark else None), heart,
                      seed + 1)
    out += hvs
    heart_tree = _tree_of(hvs)
    if dark:
        out += _prism(a, c, z0 - 0.03 if z0 > 0.5 else max(0.0, z0 - 0.03), C.z, 0.15 * R, 0.10 * R, TRUNK, seed + 2)
    c0, c1 = math.cos(math.radians(th[0])), math.cos(math.radians(th[1]))
    off = rng.random()
    for i in range(n):
        f_ = (i + 0.5) / n
        theta = math.acos(c0 + (c1 - c0) * f_)
        phi = 2 * math.pi * ((i * 0.618034 + off) % 1.0) + rng.uniform(-0.1, 0.1)
        nrm = Vector((math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)))
        p = C + Vector((nrm.x * rx, nrm.y * rx, nrm.z * hz)) * rng.uniform(0.92, 1.02)
        pitch = -min(theta * 0.55, math.radians(55))           # outward and down along the dome
        L = R * Lf * rng.uniform(0.9, 1.06)
        t = Vector((math.cos(phi) * math.cos(pitch), math.sin(phi) * math.cos(pitch), math.sin(pitch)))
        base = p - t * L * 0.42 - Vector((nrm.x, nrm.y, 0.0)) * 0.12 * rx
        h_ = 1.0 - (theta - math.radians(th[0])) / math.radians(th[1] - th[0])
        key = keys[0] if h_ > 0.66 else keys[1] if h_ > 0.3 else keys[2]
        vs = _leaf(a, tuple(base), L, L * rng.uniform(0.85, 0.95), key, phi, pitch, roll=rng.uniform(-0.2, 0.2),
                   curl=0.08, fold=0.2)
        _touch(vs, heart_tree)                 # no floating leaf: its stem end touches the heart
        if guard:
            guard.push(vs)                     # a leaf cuts at most 0.05 into the rock (the hidden heart may)
        floor = 0.0 if z0 < 0.5 else z0 - 0.05
        zmin = min(v.co.z for v in vs)
        if zmin < floor:
            for v in vs:
                v.co.z += floor - zmin
        out += vs
    tiers = ((n,),)
    allf = _faces(out)
    _mottle(a, allf, 0.04, 0.9, seed, tint=tint)
    xs, ys, zs = ([v.co[i] for v in out] for i in range(3))
    PLANT_INFO[name] = {"centre": [round(c[0], 2), round(c[1], 2)], "z0": round(z0, 2),
                        "size": [round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2),
                                 round(max(zs) - z0, 2)], "leaves": sum(t[0] for t in tiers)}
    return out


def sprig(a, name, c, z0, R, n, seed, guard=None, key=LEAF_LIME):
    """3-5 leaves from one root (no stem): steep leaves fanning out, the stem ends sunk into the ground."""
    rng = random.Random(seed)
    out = []
    y0 = rng.uniform(0, 2 * math.pi)
    for k in range(n):
        yaw = y0 + 2 * math.pi * k / n + rng.uniform(-0.25, 0.25)
        L = R * rng.uniform(0.85, 1.1)
        kk = key if k % 3 else _mix(key, LEAF, 0.3)
        base = (c[0] + math.cos(yaw) * 0.04, c[1] + math.sin(yaw) * 0.04, z0)
        vs = _leaf(a, base, L, L * 0.75, kk, yaw, rng.uniform(0.6, 1.05), curl=0.2, roll=rng.uniform(-0.3, 0.3))
        zmin = min(v.co.z for v in vs)
        floor = 0.0 if z0 < 0.5 else z0 - 0.05
        if zmin < floor:
            for v in vs:
                v.co.z += floor - zmin
        if guard:
            guard.push(vs)
        out += vs
    _mottle(a, _faces(out), 0.04, 0.9, seed, tint=1.0 + rng.uniform(-0.04, 0.04))
    PLANT_INFO[name] = {"centre": [round(c[0], 2), round(c[1], 2)], "z0": round(z0, 2), "leaves": n}
    return out


def pebble(a, c, z0, s, seed, key=None):
    """A low flat-topped pebble (a 4-5-sided tapered prism, 12-16 tris)."""
    rng = random.Random(seed)
    vs = _prism(a, c, z0, z0 + s * rng.uniform(0.38, 0.5), s * 0.55, s * 0.36, key or _mix(ROCK, ROCK_LIGHT, 0.5),
                seed, n=3 if z0 > 5.0 else 4, sq=(1.0, rng.uniform(0.7, 0.9)))
    _mottle(a, _faces(vs), 0.03, 0.8, seed, tint=rng.uniform(0.96, 1.04))
    return vs


def patch(a, c, z0, r, seed):
    """A flat pale stepping slab 0.08 proud of the lawn."""
    return _prism(a, c, z0 - 0.03, z0 + 0.08, r, r * 0.92, ROCK_LIGHT, seed, n=4, sq=(1.0, 0.8))


def lawn_rock(a, name, c, z0, pointed, seed):
    rng = random.Random(seed)
    if pointed:      # R1: a pointed 4-5-sided small rock (1.5 x 1.3 x 1.2)
        w, d, h = 1.5, 1.3, 1.2
        base = [Vector((c[0] + math.cos(t) * w / 2 * rng.uniform(0.85, 1.0), c[1] + math.sin(t) * d / 2 *
                        rng.uniform(0.85, 1.0), z0 - 0.1)) for t in [rng.uniform(0, 1) + k * 2 * math.pi / 5
                                                                   for k in range(5)]]
        apex = Vector((c[0] + 0.15, c[1] + 0.1, z0 + h - 0.1))
        mid = [p.lerp(apex, 0.45) + (p - Vector((c[0], c[1], p.z))) * 0.15 for p in base]
        vs = _hull_piece(a, base + mid + [apex], ROCK)
    else:            # R2: a low flat block (1.6 x 1.3 x 1.1)
        w, d, h = 1.6, 1.3, 1.1
        pts = []
        for sc, z in ((1.0, z0 - 0.1), (0.94, z0 + h * 0.62), (0.66, z0 + h - 0.1)):
            for k in range(5):
                t = 0.4 + k * 2 * math.pi / 5 + rng.uniform(-0.1, 0.1)
                pts.append(Vector((c[0] + math.cos(t) * w / 2 * sc, c[1] + math.sin(t) * d / 2 * sc,
                                   z + rng.uniform(-0.04, 0.04))))
        vs = _hull_piece(a, pts, ROCK)
    for f in _faces(vs):
        f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.3) if f.calc_center_median().z > z0 + 0.5 * 1.1 else ROCK)
    _mottle(a, _faces(vs), 0.04, 0.6, seed, tint=rng.uniform(0.97, 1.04))
    ROCK_INFO[name] = {"tris": sum(len(f.verts) - 2 for f in _faces(vs))}
    return vs


def apron(a, name, poly, seed):
    """A flat lime grass patch on the ground (0.1 thick), its jagged outline tucked under the rock face."""
    rng = random.Random(seed)
    P = [Vector((x + rng.uniform(-0.08, 0.08), y + rng.uniform(-0.08, 0.08))) for x, y in poly]
    if _area2(P) < 0:
        P.reverse()
    P = _resample(P, 0.6)            # short wall edges: the 0.12-high walls stay free of needle triangles
    bm = a.bm
    co, tris = _cdt(P, (), _steiner(P, 1.6, 0.6, seed))
    top_f, tm = _cap(bm, co, tris, lambda p: 0.12 + rng.uniform(-0.015, 0.015), True)
    bot_f, bm_ = _cap(bm, co, tris, 0.005, False)
    n_ = len(P)
    wf = []
    for i in range(n_):
        j = (i + 1) % n_
        wf.append(bm.faces.new((bm_[i], bm_[j], tm[j], tm[i])))
    _tri(bm, wf)
    vs = list(tm.values()) + list(bm_.values())
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, GRASS)
    for f in _faces(vs):
        c = f.calc_center_median()
        if f.normal.z > 0.5 and c.y > -4.4:
            f.material_index = a._mi(_mix(GRASS, GRASS_DEEP, 0.5))      # deeper where it tucks under the face
    _mottle(a, _faces(vs), 0.04, 0.5, seed)
    PLANT_INFO[name] = {"verts": n_}
    return vs


class _Guard:
    """Keeps a plant out of the rock: a plant whose verts go more than `allow` inside the rock is moved out along the
    surface normal at its deepest vert (horizontally, never down) until no vert is deeper than allow."""

    def __init__(self, tree, allow=0.05):
        self.tree = tree
        self.allow = allow
        self.moved = 0

    def push(self, vs):
        if self.tree is None:
            return
        moved = self._out(vs)
        if moved:
            # pushed clear of the rock: slide back until the leaf just touches it again (no floating leaf)
            best = None
            for v in vs:
                q, _n, _i, d = self.tree.find_nearest(v.co)
                if q is not None and (best is None or d < best[0]):
                    best = (d, v.co.copy(), q)
            if best and best[0] > 0.015:
                d, p_, q = best
                mv = (q - p_) * (1.0 - 0.01 / d)
                for v in vs:
                    v.co += mv

    def _out(self, vs):
        moved = False
        for _ in range(6):
            worst, nrm = 0.0, None
            for v in vs:
                loc, n, _, d = self.tree.find_nearest(v.co)
                if loc is None or n is None:
                    continue
                if (v.co - loc).dot(n) < 0 and d > worst:
                    worst, nrm = d, n
            if worst <= self.allow or nrm is None:
                return moved
            m = Vector((nrm.x, nrm.y, max(0.0, nrm.z)))     # out of the rock, never down
            if m.length < 1e-6:
                return moved
            m.normalize()
            for v in vs:
                v.co += m * (worst - self.allow + 0.02)
            self.moved += 1
            moved = True
        return moved


# lawn dressing (spec 2.3): name -> (centre, R, H, kind, seed)
LAWN_BUSHES = {"L1": ((-5.6, 1.0), 1.05, 1.8, "dark", 40401), "L2": ((3.6, 2.4), 1.05, 1.8, "dark", 40402),
               "L3": ((-3.9, -2.5), 0.65, 1.1, "lime", 40403), "L4": ((0.9, 3.3), 0.65, 1.1, "lime", 40404),
               "L5": ((6.3, -2.4), 0.65, 1.1, "lime", 40405)}
HERO_ONLY = {"L4", "S_l1", "S_l2"}
LAWN_SPRIGS = {"S_l1": ((-7.2, 3.2), 0.42, 4, 40411), "S_l2": ((7.0, 3.4), 0.42, 4, 40412)}
LAWN_ROCKS = {"R1": ((-2.2, 2.4), True, 40421), "R2": ((2.6, -0.6), False, 40422)}
LAWN_PEBBLES = [((-6.6, -1.6), 0.45), ((-4.6, 2.9), 0.35), ((-1.2, -1.4), 0.5), ((-0.4, 1.0), 0.3), ((1.6, -2.6), 0.4),
                ((4.6, -0.6), 0.55), ((5.6, 1.2), 0.35), ((-7.0, -3.2), 0.3)]
LAWN_PATCHES = [((-2.6, -0.4), 0.42), ((3.8, 0.2), 0.38), ((-6.6, 2.6), 0.36)]
# foot dressing
FOOT_BUSHES = {"F1": ((0.1, -5.4), 1.0, 1.8, "lime", 40431),
               "F_l": ((-7.95, -5.4), 0.85, 1.8, "dark", 40433),        # the end clumps overhang both seams alike
               "F_r": ((7.95, -5.3), 0.85, 1.8, "lime", 40434)}
# bushes standing on the foot boulders' flat tops (the sheet's boulder-top bush, and one on Bs behind it)
TOP_BUSHES = (("FB", (-4.5, -5.05), 1.3, 1.7, "lime", 40432), ("FBs", (-6.1, -4.65), 0.85, 1.4, "dark", 40435),
              ("FBf", (-7.2, -5.1), 0.8, 1.3, "lime", 40436),
              ("FC", (7.3, -4.5), 0.7, 1.2, "lime", 40437),          # on shard C's flank
              ("FA", (-1.05, -4.7), 0.6, 1.0, "lime", 40438),        # on shard A's foot
              ("FBr", (5.7, -4.85), 0.75, 1.2, "lime", 40439))       # on shard B's right foot       # on Bb's top
FOOT_SPRIGS = {"S_f2": ((-6.5, -5.55), 0.48, 4, 40442),
               "S_f3": ((5.85, -5.45), 0.48, 4, 40443),
               "S_f5": ((-2.4, -5.6), 0.45, 4, 40445), "S_f6": ((2.9, -5.6), 0.42, 4, 40446)}
FOOT_PEBBLES = [((-0.9, -5.6), 0.55), ((0.95, -5.6), 0.6), ((4.6, -5.6), 0.7), ((5.35, -5.8), 0.45),
                ((-5.3, -5.9), 0.45), ((6.9, -5.3), 0.75), ((-2.7, -5.85), 0.4)]
APRONS = {"A_mid": [(-1.6, -3.9), (-1.0, -5.5), (0.4, -6.0), (2.0, -5.75), (3.4, -5.95), (4.8, -5.7), (5.6, -4.9),
                    (5.4, -3.9), (3.2, -3.6), (1.0, -3.7)],
          "A_left": [(-7.9, -4.2), (-7.9, -5.6), (-6.6, -5.95), (-5.0, -6.05), (-3.0, -6.0), (-2.2, -5.4), (-2.8, -4.4),
                     (-5.0, -4.1)],
          "A_right": [(5.9, -4.0), (5.8, -5.2), (6.6, -5.75), (7.9, -5.45), (7.9, -4.0), (7.0, -3.7)]}


def lawn(a, part=False):
    """The lawn dressing on the lip (spec 2.3): bushes, sprigs, boulders, pebbles, stepping patches. Every leaf,
    heart, trunk, rock, pebble and patch its own closed shell, each set into the turf (sunk 0.03-0.1)."""
    z = LIP_TOP - 0.03
    for nm, ((x, y), R, H, kind, seed) in LAWN_BUSHES.items():
        if part and nm in HERO_ONLY:
            continue
        bush(a, nm, (x, y), z, R, H, kind, seed)
    for nm, ((x, y), R, n, seed) in LAWN_SPRIGS.items():
        if part and nm in HERO_ONLY:
            continue
        sprig(a, nm, (x, y), z, R, n, seed)
    for nm, ((x, y), pointed, seed) in LAWN_ROCKS.items():
        lawn_rock(a, nm, (x, y), LIP_TOP, pointed, seed)
    for i, ((x, y), s) in enumerate(LAWN_PEBBLES):
        pebble(a, (x, y), LIP_TOP - 0.04, s, 40451 + i)
    for i, ((x, y), r) in enumerate(LAWN_PATCHES):
        patch(a, (x, y), LIP_TOP, r, 40461 + i)


def _roots():
    ROOTS[:] = ([(x, y, R * 0.55) for (x, y), R, H, k, s in LAWN_BUSHES.values()] +
                [(x, y, 0.8) for (x, y), _p, _s in LAWN_ROCKS.values()])


def lip_part(a):
    PLANT_INFO.clear()
    _roots()
    lip_slab(a)
    lawn(a, part=True)


# ---- flat back connector ------------------------------------------------------------------------------------------------
PLATE_X = (7.6, 8.0)
PLATE_Y = (0.1, 4.0)
PLATE_TOP = 10.05
FRONT_TABS = ((0.7, 1.7), (4.1, 5.1), (7.8, 8.8))          # z ranges; front tabs reach y TAB_FRONT
BACK_TABS = ((1.6, 2.6), (4.7, 5.7), (8.1, 9.1))
TAB_FRONT, TAB_BACK = GROOVE_Y - 0.02, 4.35
NOTCH = (0.42, 9.72)                                       # the front-top corner notch: to y 0.42, down to z 9.72


def plate_profile():
    """The plate's (y, z) outline, CCW seen from +X: the front edge with its tabs and the top notch, the top, the back
    edge with its tabs."""
    y0, y1 = PLATE_Y
    pts = [(y0, 0.0)]
    for za, zb in FRONT_TABS:
        pts += [(y0, za), (TAB_FRONT, za), (TAB_FRONT, zb), (y0, zb)]
    pts += [(y0, NOTCH[1]), (NOTCH[0], NOTCH[1]), (NOTCH[0], PLATE_TOP), (y1, PLATE_TOP)]
    for za, zb in reversed(BACK_TABS):
        pts += [(y1, zb), (TAB_BACK, zb), (TAB_BACK, za), (y1, za)]
    pts += [(y1, 0.0)]
    # CCW in the (y, z) plane seen from +X means going down the back and up the front: reverse if needed
    if _area2(pts) < 0:
        pts.reverse()
    return pts


def plate(a):
    bm = a.bm
    P = plate_profile()
    n_ = len(P)
    co, tris = _cdt(P)
    sides = {}
    for x, up in ((PLATE_X[0], False), (PLATE_X[1], True)):
        vm = {i: bm.verts.new((x, P[i][0], P[i][1])) for i in range(n_)}
        for i, j, k in tris:
            bm.faces.new((vm[i], vm[j], vm[k]))
        sides[x] = vm
    a_, b_ = sides[PLATE_X[0]], sides[PLATE_X[1]]
    fs = []
    for i in range(n_):
        j = (i + 1) % n_
        fs.append(bm.faces.new((a_[i], a_[j], b_[j], b_[i])))
    _tri(bm, fs)
    vs = list(a_.values()) + list(b_.values())
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, CONN, tint=1.0)
    _mottle(a, _faces(vs), 0.02, 0.3, 40501)
    return vs


def connector_part(a):
    plate(a)


# ---- hero ---------------------------------------------------------------------------------------------------------------
def _top_z(tree, x, y, z_from=40.0):
    h = tree.ray_cast(Vector((x, y, z_from)), Vector((0, 0, -1)), 100)
    return h[0].z if h[0] is not None else 0.0


def hero_rest(a, body_tree):
    """Everything on the hero but the body shell: the lip, the plate and all the dressing (build frame)."""
    PLANT_INFO.clear()
    _roots()
    lip_slab(a)
    plate(a)
    lawn(a, part=False)
    guard = _Guard(body_tree)
    for nm, ((x, y), R, H, kind, seed) in FOOT_BUSHES.items():
        bush(a, nm, (x, y), 0.0, R, H, kind, seed, guard=guard)
    for nm, (x, y), R, H, kind, seed in TOP_BUSHES:
        zt = _top_z(body_tree, x, y)
        bush(a, nm, (x, y), zt - 0.03 if zt > 0.1 else 0.0, R, H, kind, seed, guard=guard)   # missed: on the ground
    for nm, ((x, y), R, n, seed) in FOOT_SPRIGS.items():
        sprig(a, nm, (x, y), 0.0, R, n, seed, guard=guard)
    for i, ((x, y), s) in enumerate(FOOT_PEBBLES):
        vs = pebble(a, (x, y), 0.0, s, 40471 + i, key=_mix(ROCK, ROCK_LIGHT, 0.3))
        guard.push(vs)
    for nm, poly in APRONS.items():
        apron(a, nm, poly, 40481 + len(nm))
    return guard.moved


# ---- make / finish (m033 / m035 pipeline with this model's offset key) ---------------------------------------------------
NOTES = {
    HERO: "Stone cliff wall tile (16 x 8, lawn top z 10.4): a palisade of five tall flat-faced warm peach-grey rock "
          "columns with dark creases, three pointed shards and a flat-topped boulder group at the front-left foot, "
          "capped by a separate flat lime lawn lip on a blocky rock rim (two dark-green bushes, three lime bushes, "
          "boulders, pebbles), a grey back-connector plate with tabs on the +X end, a lime grass apron, a foot bush "
          "and sprigs. Tile contract: seams x = +-8 from the bbox centre (see m040.py), back plane flat, lip front "
          "y -4.2 at both seams, turf z 10.4. Body one closed shell, lip one, plate one, every leaf/pebble its own. "
          "No VFX",
    BODY_P: "Cliff Wall Body (reusable): five tall flat-faced rock columns (palisade), three pointed shards and a "
            "flat-topped boulder group at the front-left foot; flat top at z 9.2 (sits under the grass lip); flat "
            "back and seam ends; flat underside",
    LIP_P: "Grass Top Lip (reusable): flat lime lawn slab on a blocky rock rim with a flat recessed underside, two "
           "dark-green bushes, two lime bushes, two small boulders, pebbles and stepping patches",
    CONN_P: "Flat Back Connector (modular join): a flat grey plate with three tabs on each long edge and a notch at "
            "the front-top corner",
}
COLLISION = {HERO: "precise", BODY_P: "hull", LIP_P: "precise", CONN_P: "box"}
UNION_RETRIES = m033.UNION_RETRIES
SEAMS = (-8.0, 8.0)


def _snap_seams(o, tol=0.05):
    """Booleans and sliver passes can move a seam vertex by a hair: put every vertex within tol of a seam plane (build
    frame) back on it, so the tile's ends stay exactly planar."""
    off = Vector(o[OFF])
    n = 0
    for v in o.data.vertices:
        x = v.co.x + off.x
        for s in SEAMS:
            if 1e-7 < abs(x - s) < tol or (s < 0 and x < s) or (s > 0 and x > s):
                v.co.x = s - off.x
                n += 1
    o.data.update()
    return n


def _finish(o):
    o[OFF] = list(Vector(o[OFF]) + m012._bottom_centre(o))
    res = M.finish(o, union=False, uv=UV)
    for _ in range(3):
        crumbs = m012._drop_inner(o)
        if not (crumbs or m012._thin(o)["under"] or res["nonmanifold_edges"] or res["boundary_edges"]):
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
        m012._force_slivers(o)
        o[OFF] = list(Vector(o[OFF]) + m012._bottom_centre(o))
        res = M.finish(o, union=False, uv=UV)
    return res


def _recentre(o):
    bc = m012._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


def _polish(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = m012._tri_quads(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = m012._force_slivers(o, lim=POLISH_LIM)
    if m012._thin(o, POLISH_LIM)["under"]:
        forced += m012._force_slivers(o, lim=POLISH_LIM, max_len=0.5)
    _recentre(o)
    M.smart_uv(o, **UV)
    return {"split": split, "forced": forced, "uv_cut": m012._uv_unfold(o)}


def _ground_beautify(o):
    """The floor cut's cap (all faces on z 0): flip its inner edges to the Delaunay triangulation, so no needle
    triangle is left across the flat underside. Returns the edges rotated."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    # a cut point left on a straight edge of the underside (where a side face's diagonal crossed z 0 on a flat end
    # face) forces a needle into the cap: dissolve it when every face round it lies in the ground plane or in one
    # vertical plane, then re-triangulate those faces
    for _ in range(3):
        drop = []
        for v in bm.verts:
            if abs(v.co.z) > 1e-4:
                continue
            nb = [e.other_vert(v) for e in v.link_edges if abs(e.other_vert(v).co.z) < 1e-4]
            side = [f for f in v.link_faces if not all(abs(x.co.z) < 1e-4 for x in f.verts)]
            if len(nb) != 3 or not side:
                continue
            n0 = side[0].normal
            if any(f.normal.angle(n0, 1.0) > math.radians(0.5) for f in side):
                continue
            bnd = [w for w in nb if any(not all(abs(x.co.z) < 1e-4 for x in f.verts) for f in v.link_faces
                                         if w in f.verts)]
            if len(bnd) == 2 and (bnd[0].co - v.co).angle(bnd[1].co - v.co, 0.0) > math.radians(179.0):
                drop.append(v)
        if not drop:
            break
        bmesh.ops.dissolve_verts(bm, verts=drop)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                              ngon_method="BEAUTY")
    g = [f for f in bm.faces if all(abs(v.co.z) < 1e-4 for v in f.verts)]
    gs = set(g)
    inner = [e for e in {e for f in g for e in f.edges} if len(e.link_faces) == 2 and all(x in gs for x in e.link_faces)]
    n = 0
    if inner:
        r = bmesh.ops.beautify_fill(bm, faces=g, edges=inner)
        n = len(r["geom"])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    o.data.update()
    return n


def _ground_faces(o):
    p = m011._Paint(o, off=o[OFF])
    n = 0
    for f in p.bm.faces:
        if all(abs(v.co.z) < 1e-3 for v in f.verts):
            f.material_index = p._mi(ROCK)
            n += 1
    p.done()
    return n


def _make(name, fn, role, budget, union=False, ground=False):
    t0 = time.time()
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget,
             collision=COLLISION[name], tint_var=0.0)
    off = M._build_offset(fn)
    o[OFF] = list(off)
    o.location = (0.0, 0.0, 0.0)          # booleans at the world origin (m030)
    bpy.context.view_layer.update()
    lg = {}
    if union:
        m033._sane(o)
        lg["shells_merged"] = m033._union_fine(o)
    if ground:
        lg["cap"] = m033._floor_cut(o, z0=-off.z)
        o[OFF] = [off.x, off.y, 0.0]
        lg["clean"] = {k: v for k, v in m016._clean_mesh(o, (0.0,)).items() if not isinstance(v, (list, dict))}
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    lg["seam_snap"] = _snap_seams(o)
    if ground:
        lg["ground_beautify"] = _ground_beautify(o)
        lg["ground_faces"] = _ground_faces(o)
        M.smart_uv(o, **UV)
        lg["uv_cut2"] = m012._uv_unfold(o)
    lg["bowties"] = M.fix_bowties(o)
    K.drop_unused_slots(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


def _tri_ngons(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    ng = [f for f in bm.faces if len(f.verts) > 3]
    if ng:
        bmesh.ops.triangulate(bm, faces=ng, quad_method="BEAUTY", ngon_method="BEAUTY")
        bm.to_mesh(o.data)
    bm.free()


def _make_plain(name, fn, role="part", budget=1000):
    """A part made of separate clean closed shells (no union, no speck pass, which would delete pebbles and leaves):
    n-gons triangulated, origin at the bottom centre, flat shading, UVs."""
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget,
             collision=COLLISION[name], tint_var=0.0)
    o[OFF] = list(M._build_offset(fn))
    o.location = (0.0, 0.0, 0.0)
    _tri_ngons(o)
    _recentre(o)
    for p in o.data.polygons:
        p.use_smooth = False
    M.smart_uv(o, **UV)
    lg = {"uv_cut": m012._uv_unfold(o), "bowties": M.fix_bowties(o)}
    K.drop_unused_slots(o)
    return o, lg


def _fused_ok(o):
    a = M.audit(o)
    return (a["shells"] == 1 and not a["nonmanifold_edges"] and not a.get("nonmanifold_verts") and
            not a["boundary_edges"] and a["normals"] == "outward"
            and not m016._self_hits(o)[0] and not m012._thin(o, POLISH_LIM)["under"])


BODY_TRIES = 4


def _jitter_pieces(attempt):
    """A union that grazes leaves a sliver pair: nudge the shards and boulders a hair and rebuild."""
    for nm, s in SHARDS.items():
        s["base"] = [(x + 0.007 * attempt, y - 0.005 * attempt) for x, y in BASE_SHARDS[nm]]
    for nm, b in BLOCKS.items():
        (cx, cy), *rest = BASE_BLOCKS[nm]
        BLOCKS[nm] = ((cx + 0.009 * attempt, cy + 0.006 * attempt), *rest)


BASE_SHARDS = {k: list(v["base"]) for k, v in SHARDS.items()}
BASE_BLOCKS = dict(BLOCKS)


def _body_obj(name, role, budget):
    for attempt in range(BODY_TRIES):
        _jitter_pieces(attempt)
        o, lg = _make(name, body_part, role, budget, union=True, ground=True)
        if _fused_ok(o) and o.dimensions.x > 15.9:
            break
    _jitter_pieces(0)
    lg["attempt"] = attempt
    return o, lg


def _body_tree(o):
    off = Vector(o[OFF])
    coords = [v.co + off for v in o.data.vertices]
    polys = [list(p.vertices) for p in o.data.polygons]
    return BVHTree.FromPolygons(coords, polys)


def _make_hero():
    t0 = time.time()
    o, lg = _body_obj(HERO, "hero", 4000)
    lg["body"] = {k: v for k, v in M.audit(o).items() if k in ("tris", "shells", "nonmanifold_edges",
                                                              "nonmanifold_verts", "boundary_edges", "size")}
    tree = _body_tree(o)
    a = K.fk().Asset(PFX + "rest", "probe", seed=7, tint_var=0.0)
    lg["guard_moves"] = hero_rest(a, tree)
    c = a.finish(collection=o.users_collection[0], mark_asset=False, origin=None)
    c.matrix_world = o.matrix_world @ Matrix.Translation(-Vector(o[OFF]))
    bpy.context.view_layer.update()
    _tri_ngons(c)
    with M._override(o):
        c.select_set(True)
        with bpy.context.temp_override(selected_objects=[o, c], selected_editable_objects=[o, c]):
            bpy.ops.object.join()
    _recentre(o)
    K.drop_unused_slots(o)
    for p in o.data.polygons:
        p.use_smooth = False
    M.smart_uv(o, **UV)
    lg["uv_cut"] = m012._uv_unfold(o)
    lg["bowties"] = M.fix_bowties(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


# ---- checks ---------------------------------------------------------------------------------------------------------------
def _keys(o):
    return [m.get("flintkit_key", m.name) if m else "" for m in o.data.materials]


def _kind(ks):
    if all(k.startswith("m040_leaf") for k in ks):
        return "leaf"
    if ks == {TRUNK}:
        return "trunk"
    if ks == {CONN}:
        return "plate"
    if any(k.startswith("m040_grass") for k in ks) and any(k.startswith("m040_rock") for k in ks):
        return "lip"
    if all(k.startswith("m040_grass") for k in ks):
        return "apron"
    return "rock"


def shells_report(o):
    """Per shell: kind, tris, non-manifold edges and verts, boundary edges, self-intersecting face pairs inside the
    shell, inverted faces (ray parity inside the shell), volume."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = _keys(o)
    groups = {}
    for f in bm.faces:
        groups.setdefault(ids[f.index], []).append(f)
    out = []
    for k in range(n):
        fs = groups[k]
        es = {e for f in fs for e in f.edges}
        vs = list({v for f in fs for v in f.verts})
        ks = {keys[f.material_index] for f in fs}
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        hits = sum(1 for a_, b_ in tree.overlap(tree) if a_ < b_ and not set(fs[a_].verts) & set(fs[b_].verts))
        inv = 0
        for f in fs:
            odd = 0
            o1 = f.normal.orthogonal().normalized()
            o2 = f.normal.cross(o1)
            for dv in (f.normal, (f.normal + o1 * 0.21).normalized(), (f.normal - o1 * 0.17).normalized(),
                       (f.normal + o2 * 0.19).normalized(), (f.normal - o2 * 0.23).normalized()):
                p = f.calc_center_median() + dv * 1e-4
                cnt, x, last = 0, p.copy(), None
                for _ in range(40):
                    h = tree.ray_cast(x, dv)
                    if h[0] is None:
                        break
                    if (last is None or (h[0] - last).length > 1e-4) and fs[h[2]] is not f:
                        cnt += 1
                    last = h[0]
                    x = h[0] + dv * 1e-5
                odd += cnt % 2
            inv += odd == 5
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) / 3.0
        out.append({"kind": _kind(ks), "tris": sum(len(f.verts) - 2 for f in fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary), "self_hits": hits, "inverted": inv,
                    "volume": round(vol, 4)})
    bm.free()
    return out


CONTACT = 0.03


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """Floating dressing: per shell, whether it touches another shell (triangles overlap, or a vert within `tol` of
    another shell's surface) or the ground (z <= tol). Returns the shells touching nothing at `tol`, the worst such
    gap, and the shells with no chain of contact down to the ground (at tol and at chain_tol). (m035)"""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = _keys(o)
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
    area = [0.0] * n
    for f in bm.faces:
        area[fsh[f.index]] += f.calc_area()
    stone = max(range(n), key=lambda k: area[k])
    pairs = set()
    for i, j in tree.overlap(tree):
        a_, b_ = fsh[i], fsh[j]
        if a_ != b_:
            pairs.add((min(a_, b_), max(a_, b_)))
    near = {}
    gap = [1e9] * n
    for v in bm.verts:
        s = vsh.get(v.index)
        if s is None:
            continue
        for loc, _, fi, d in tree.find_nearest_range(v.co, chain_tol):
            t = fsh[fi]
            if t != s:
                k = (min(s, t), max(s, t))
                near[k] = min(near.get(k, 1e9), d)
    for (a_, b_) in pairs:
        near[(a_, b_)] = 0.0
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    ground = min(zmin)
    for k in range(n):
        gap[k] = min(gap[k], max(0.0, zmin[k] - ground))

    def chained(t):
        adj = {k: set() for k in range(n)}
        for (a_, b_), d in near.items():
            if d <= t:
                adj[a_].add(b_)
                adj[b_].add(a_)
        seen = {k for k in range(n) if zmin[k] - ground <= t} | {stone}
        stack = list(seen)
        while stack:
            k = stack.pop()
            for m_ in adj[k]:
                if m_ not in seen:
                    seen.add(m_)
                    stack.append(m_)
        return n - len(seen)
    kind = {}
    for f in bm.faces:
        kind.setdefault(fsh[f.index], keys[f.material_index])
    floating = [k for k in range(n) if gap[k] > tol and k != stone]
    res = {"shells": n, "floating": len(floating),
           "floating_kinds": sorted({kind[k].replace("m040_", "") for k in floating}),
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "max_gap_all": round(max(gap[k] for k in range(n) if k != stone), 3),
           "unchained": chained(tol), "unchained_chain_tol": chained(chain_tol)}
    bm.free()
    return res


def _shell_faces(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    return bm, ids, n


def capping_report(h):
    """Spec 2.5 capping on the hero: body faces with n.z > 0.5 above z 8.0 (build frame) seen from straight above
    (the first hit of a downward ray through 5 points on the face is that body face): exposed area; and all rock
    seen from straight above inside the tile (a 0.1 grid over x -8..8, y -6.4..4.4), by kind."""
    off = Vector(h[OFF])
    bm, ids, n = _shell_faces(h)
    keys = _keys(h)
    sk = {}
    for f in bm.faces:
        sk.setdefault(ids[f.index], set()).add(keys[f.material_index])
    skind = {k: _kind(v) for k, v in sk.items()}
    tree = BVHTree.FromBMesh(bm)
    body = ids[0]
    exposed = 0.0
    cand = 0
    for f in bm.faces:
        if ids[f.index] != body or f.normal.z <= 0.5:
            continue
        c = f.calc_center_median()
        if c.z + off.z < 8.0:
            continue
        cand += 1
        pts = [c] + [c.lerp(v.co, 0.8) for v in f.verts] + [c.lerp(v.co, 0.4) for v in f.verts]
        seen = 0
        for p in pts:
            hh = tree.ray_cast(Vector((p.x, p.y, 60.0)), Vector((0, 0, -1)), 200)
            if hh[0] is not None and ids[hh[2]] == body and abs(hh[0].z - p.z) < 0.02:
                seen += 1
        exposed += f.calc_area() * seen / len(pts)
    rock_top = {}
    step = 0.1
    for xi in range(int(16 / step)):
        x = -8.0 + (xi + 0.5) * step - off.x
        for yi in range(int(10.8 / step)):
            y = -6.4 + (yi + 0.5) * step - off.y
            hh = tree.ray_cast(Vector((x, y, 60.0)), Vector((0, 0, -1)), 200)
            if hh[0] is None:
                continue
            k = keys[bm.faces[hh[2]].material_index]
            if k.startswith("m040_rock"):
                s_ = ids[hh[2]]
                where = "body" if s_ == body else "lip" if skind[s_] == "lip" else "rocks"
                rock_top[where] = rock_top.get(where, 0) + step * step
    bm.free()
    return {"exposed_column_top": round(exposed, 3), "candidates_above_8": cand,
            "rock_from_above": {k: round(v, 2) for k, v in rock_top.items()},
            "rock_from_above_total": round(sum(rock_top.values()), 2)}


def proud_report():
    """The lip outline against the body's top front: every body top-ring vertex inside the lip outline; the rim's
    distance in front of each column's front corners (ridge and face vertices)."""
    O = [_v2(p) for p in lip_outline()[0]]
    tf = top_front()
    inside = all(_inside((x, y), O) or abs(x) > 7.99 for x, y, k in tf)
    R = body_rings()
    all_in = all(_inside((r[-1].x, r[-1].y), O) or abs(r[-1].x) > 7.99 or r[-1].y > 3.99 for r in R)
    d = {}
    for (x, y, k), (_x, _y, _k, col) in zip(tf, FRONT):
        if k in ("ridge", "face"):
            d.setdefault(col, []).append(round(_poly_d((x, y), O), 3))
    ridges = [min(v) for v in d.values()]
    return {"front_inside": inside, "top_ring_inside": all_in, "per_column_min_proud": d,
            "proud_min": min(ridges), "proud_max_of_column_minima": max(ridges)}


def seam_report(h):
    """Tile contract on the hero mesh (build frame): rock and plate verts never past the seams; the verts on each seam
    plane exactly on it; the lip's front at the seams; the turf level at the seams."""
    off = Vector(h[OFF])
    bm, ids, n = _shell_faces(h)
    keys = _keys(h)
    shell_kind = {}
    for f in bm.faces:
        shell_kind.setdefault(ids[f.index], set()).add(keys[f.material_index])
    kinds = {k: _kind(v) for k, v in shell_kind.items()}
    vk = {}
    for f in bm.faces:
        for v in f.verts:
            vk[v.index] = kinds[ids[f.index]]
    past, on, worst = 0, {-8.0: 0, 8.0: 0}, 0.0
    lip_front = {}
    turf = []
    for v in bm.verts:
        k = vk.get(v.index)
        p = v.co + off
        if k in ("rock", "lip", "plate"):
            if p.x < -8.0005 or p.x > 8.0005:
                past += 1
            for s in SEAMS:
                if abs(p.x - s) < 0.015:
                    on[s] += 1
                    worst = max(worst, abs(p.x - s))
        if k == "lip":
            for s in SEAMS:
                if abs(p.x - s) < 1e-3:
                    lip_front[s] = min(lip_front.get(s, 9), p.y)
            if abs(p.z - LIP_TOP) < 0.06 and (abs(p.x + 8) < 1.0 or abs(p.x - 8) < 1.0):
                turf.append(p.z)
    bm.free()
    return {"verts_past_seams": past, "verts_on_seams": {str(k): v for k, v in on.items()},
            "seam_plane_worst": round(worst, 4), "lip_front_y_at_seams": {str(k): round(v, 3) for k, v in
                                                                          lip_front.items()},
            "turf_z_near_seams": [round(min(turf), 3), round(max(turf), 3)] if turf else None,
            "back_plane_y_object": round(4.0 - off.y, 3), "seams_x_object": [round(-8 - off.x, 3),
                                                                               round(8 - off.x, 3)]}


def rock_metrics(o):
    """Spec 2.5 on the body part: triangle area CV, side faces within 20 deg of vertical, the largest flat facets
    (coplanar neighbours within 3 deg merged) with their height / width, the tallest-strip elongations."""
    off = Vector(o[OFF])
    bm = bmesh.new()
    bm.from_mesh(o.data)
    fs = [f for f in bm.faces if abs(f.normal.z) < 0.95]
    areas = np.array([f.calc_area() for f in fs])
    vert = sum(f.calc_area() for f in fs if abs(f.normal.z) < math.sin(math.radians(20))) / areas.sum()
    fid = {}
    regs = []
    sset = set(fs)
    for f in fs:
        if f in fid:
            continue
        r = len(regs)
        stack, reg = [f], []
        fid[f] = r
        while stack:
            g = stack.pop()
            reg.append(g)
            for e in g.edges:
                for hh in e.link_faces:
                    if hh in fid or hh not in sset or hh.normal.angle(f.normal, 1.0) > math.radians(3.0):
                        continue
                    fid[hh] = r
                    stack.append(hh)
        regs.append(reg)
    rows = []
    for reg in regs:
        vs = {v for g in reg for v in g.verts}
        nrm = reg[0].normal
        hz = Vector((-nrm.y, nrm.x, 0.0))
        if hz.length < 1e-6:
            continue
        hz.normalize()
        ws = [v.co.dot(hz) for v in vs]
        zs = [v.co.z for v in vs]
        area = sum(g.calc_area() for g in reg)
        w, hgt = max(ws) - min(ws), max(zs) - min(zs)
        front = nrm.y < -0.3
        rows.append((area, hgt / max(w, 1e-3), front, round(w, 2), round(hgt, 2)))
    rows.sort(key=lambda r: -r[0])
    fr = [r for r in rows if r[2]]
    bm.free()
    return {"side_tris": len(fs), "area_cv": round(float(areas.std() / areas.mean()), 2),
            "side_within_20deg_vertical": round(vert, 3), "facets": len(rows),
            "front_facets_top5_h_over_w": [round(r[1], 2) for r in fr[:5]],
            "front_facets_top5_size": [(r[3], r[4]) for r in fr[:5]]}


# ---- render measurement (the study's masks, spec "Pixel boxes and masks") ------------------------------------------------
SHEET_REF = {
    "f34": {"wh": 1.320, "R": 75.5, "G": 24.2, "C": 0.0, "fifths": [16.1, 13.6, 0.0, 28.7, 41.7],
            "top": [.14, .31, .76, .81, .87, .84, .90, .86, .91, .90, .93, .97, .97, .94, .99, .99, .93, .95, .87, .32,
                    .21], "rock": "#C3A598", "lawn": "#D2DD14"},
    "front": {"wh": 1.358, "R": 78.6, "G": 21.3, "C": 0.0, "fifths": [24.9, 8.5, 0.0, 23.3, 43.4],
              "top": [.20, .52, .82, .89, .89, .88, .84, .89, .91, .86, .88, .94, .90, .96, .97, .94, .87, .92, .85,
                      .58, .15], "rock": "#BEA59B", "lawn": "#CDD817"},
    "side": {"wh": 0.672, "R": 42.9, "G": 16.9, "C": 40.0},
    "rear": {"wh": 1.305, "R": 78.0, "G": 21.8, "C": 0.0, "fifths": [21.2, 5.7, 0.0, 28.4, 44.7], "rock": "#B79C93"},
    "r34": {"wh": 1.452, "R": 78.4, "G": 21.3, "C": 0.0, "fifths": [22.2, 9.1, 4.0, 15.5, 49.2], "rock": "#C1A295"},
    "top": {"wh": 1.182, "R": 29.0, "G": 70.6, "C": 0.0, "lawn": "#C2D512"},
}


def _hsv(px):
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0)
    return h, s, mx


def classify(px):
    """The study's cls() on an sRGB 0-1 image: 1 rock R, 2 green G, 3 dirt D, 4 connector C (neutral grey), 0 else."""
    h, s, v = _hsv(px)
    G = (h >= 45) & (h <= 150) & (s >= 0.28) & (v >= 0.12)
    T = (v < 0.30) & (s < 0.30)
    D = ~G & (h >= 8) & (h <= 40) & (s >= 0.42) & (v >= 0.25)
    C = ~G & ~T & (s < 0.075) & (v >= 0.3) & (v <= 0.75)
    R = ~G & ~T & ~D & ~C & (((h <= 45) | (h >= 190)) & (s < 0.45) & (v >= 0.28))
    out = np.zeros(v.shape, np.int8)
    out[R] = 1
    out[G] = 2
    out[D] = 3
    out[C] = 4
    return out, h, s, v


def measure(path, bg_tol=0.04):
    """Silhouette bbox, W:H, shares (R / G / D / C of their sum), green by height fifths (bottom up), the top profile
    (21 columns), medians of rock, lawn (hue < 80, v >= 0.6) and bush green, of a render with a flat background."""
    kit = K.NS["KIT"]
    px = np.clip(kit["load_px"](path)[::-1, :, :3], 0, 1)
    bg = np.median(np.concatenate([px[:4, :4].reshape(-1, 3), px[:4, -4:].reshape(-1, 3)]), axis=0)
    sil = np.abs(px - bg).max(-1) > bg_tol
    cls, h, s, v = classify(px)
    ys, xs = np.nonzero(sil)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    H, W = y1 - y0 + 1, x1 - x0 + 1
    c = np.where(sil, cls, 0)
    cnt = {k: int((c == i).sum()) for k, i in (("R", 1), ("G", 2), ("D", 3), ("C", 4))}
    tot = max(1, sum(cnt.values()))
    gy = np.nonzero(c == 2)[0]
    fifths = [0] * 5
    for y in gy:
        fifths[min(4, int((y1 - y) / H * 5))] += 1
    gsum = max(1, sum(fifths))
    prof = []
    for f in np.linspace(0, 1, 21):
        col = int(round(x0 + f * (W - 1)))
        on = np.nonzero(sil[:, col])[0]
        prof.append(round(float((y1 - on.min()) / (H - 1)), 2) if len(on) else 0.0)
    rgb = px * 255

    def med(mask):
        sel = rgb[mask]
        return "#" + "".join(f"{int(x):02X}" for x in np.median(sel, axis=0)) if len(sel) else None
    lawn = (c == 2) & (h < 80) & (v >= 0.6)
    bushm = (c == 2) & ~lawn
    return {"wh": round(W / H, 3), "R": round(100 * cnt["R"] / tot, 1), "G": round(100 * cnt["G"] / tot, 1),
            "D": round(100 * cnt["D"] / tot, 1), "C": round(100 * cnt["C"] / tot, 1),
            "fifths": [round(100 * f / gsum, 1) for f in fifths], "top": prof,
            "rock": med(c == 1), "lawn": med(lawn), "bush": med(bushm), "conn": med(c == 4)}


def measure_views(out_dir=None):
    d = out_dir or f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    res = {}
    for k, f in (("f34", "f34_sheet"), ("front", "front_sheet"), ("side", "side_sheet"), ("rear", "rear_sheet"),
                 ("r34", "r34_sheet"), ("top", "top_sheet")):
        try:
            m = measure(f"{d}/{f}.png")
        except Exception as e:      # a view not rendered yet
            res[k] = str(e)
            continue
        ref = SHEET_REF[k]
        if "top" in ref and "top" in m:
            m["top_err_mean"] = round(float(np.mean(np.abs(np.array(m["top"]) - np.array(ref["top"])))), 3)
            m["top_err_max"] = round(float(np.max(np.abs(np.array(m["top"]) - np.array(ref["top"])))), 3)
        m["sheet"] = {kk: vv for kk, vv in ref.items() if kk != "top"}
        res[k] = m
    return res


# ---- build ----------------------------------------------------------------------------------------------------------------
TARGET_SIZE = ((17.6, 0.4), (10.35, 0.5), (12.3, 0.4))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me is not None and isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m040_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib",
                                                                                 "StoneCliff"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build(render=True, parts=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    UNION_RETRIES.clear()
    ROCK_INFO.clear()
    palette()
    objs, log = {}, {}
    if parts:
        objs[BODY_P], log[BODY_P] = _body_obj(BODY_P, "part", 1000)
        objs[LIP_P], log[LIP_P] = _make_plain(LIP_P, lip_part)
        log["lip_plants"] = {k: dict(v) for k, v in PLANT_INFO.items()}
        objs[CONN_P], log[CONN_P] = _make_plain(CONN_P, connector_part)
    h, log["hero"] = _make_hero()
    log["plants"] = {k: dict(v) for k, v in PLANT_INFO.items()}
    log["rocks"] = {k: dict(v) for k, v in ROCK_INFO.items()}
    log["body"] = dict(BODY_INFO)
    log["lip"] = {k: v for k, v in LIP_INFO.items() if k != "outline"}
    log["union_retries"] = list(UNION_RETRIES)
    _cleanup_tmp()
    order = [h] + [objs[n] for n in (BODY_P, LIP_P, CONN_P) if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    audits = [M.audit(o) for o in order]
    thin = {o.name: m012._thin(o, POLISH_LIM) for o in order}
    shells = {o.name: shells_report(o) for o in order}
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
        for i, s in enumerate(shells[o.name]):
            for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "self_hits", "inverted"):
                if s[k]:
                    problems.append(f"{o.name} shell {i} ({s['kind']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['kind']}): not closed outward (volume {s['volume']})")
    hs = shells[HERO]
    if hs[0]["kind"] != "rock" or sum(1 for s in hs if s["tris"] > 150 and s["kind"] == "rock") != 1:
        problems.append(f"{HERO}: expected one big body rock shell first")
    for nm in (BODY_P, CONN_P):
        if nm in shells and len(shells[nm]) != 1:
            problems.append(f"{nm}: {len(shells[nm])} shells, expected 1")
    contact = {o.name: contact_report(o) for o in order if o is h or o.name == LIP_P}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} shells touch nothing within {CONTACT}, {c['unchained']} have no "
                            f"chain of contact to the ground")
    cap = capping_report(h)
    if cap["exposed_column_top"] > 0.0:
        problems.append(f"{HERO}: exposed column-top area {cap['exposed_column_top']}")
    proud = proud_report()
    if not (proud["front_inside"] and proud["top_ring_inside"]) or proud["proud_min"] < 0.1:
        problems.append(f"{HERO}: the lip does not cap the columns 0.1+ proud ({proud['proud_min']})")
    seam = seam_report(h)
    if seam["verts_past_seams"] or seam["seam_plane_worst"] > 0.001:
        problems.append(f"{HERO}: seam contract broken {seam}")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 9: none)")
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    kinds = {}
    for s in hs:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts", "transforms_applied")} for au in audits],
           "shells": kinds, "contact": contact, "capping": cap, "proud": proud, "seams": seam, "thin": thin,
           "log": log, "problems": problems, "uv": uv,
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "rock_metrics": rock_metrics(objs[BODY_P]) if BODY_P in objs else None,
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order)
        out["measure"] = measure_views()
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders --------------------------------------------------------------------------------------------------------------
# decision 10: front_sheet (0, 12) and f34_sheet (-10, 16) govern; side_sheet (90, 10); rear_sheet (180, 12), r34_sheet
# (150, 16) and top_sheet (0, 89) judged loosely; floor hidden and a 3x lens on the *_sheet shots (m033._long_lens)
SHEET_VIEWS = {"f34_sheet": (-5, 16), "front_sheet": (0, 12), "side_sheet": (90, 10), "rear_sheet": (180, 12),
               "r34_sheet": (150, 16), "top_sheet": (0, 89)}
PARTS_SHOT = (-20, 22)


def _copy(tag, src, m, coll):
    c = bpy.data.objects.new(f"{PFX}{tag}", src.data)
    coll.objects.link(c)
    c.matrix_world = m
    return c


def _frame_of(h):
    """The hero's build frame in world space."""
    return h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))


def _exploded(objs):
    """Copies of the three parts laid out like the sheet's Exploded Construction: the body, the lip lifted above it,
    the plate pulled out to the right and turned to face the viewer."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []
    o0 = Matrix.Translation((objs[0].location.x + 80, objs[0].location.y, 0))
    if BODY_P in by:
        shown.append(_copy("expl_body", by[BODY_P], o0 @ Matrix.Translation(Vector(by[BODY_P][OFF])), coll))
    if LIP_P in by:
        shown.append(_copy("expl_lip", by[LIP_P], o0 @ Matrix.Translation(Vector(by[LIP_P][OFF]) + Vector((0, 0, 3.5))),
                           coll))
    if CONN_P in by:
        p = Vector(by[CONN_P][OFF])
        shown.append(_copy("expl_plate", by[CONN_P], o0 @ Matrix.Translation((11.0, -1.0, 0.0)) @
                           Matrix.Rotation(math.radians(-70), 4, "Z") @ Matrix.Translation((0, 0, p.z)), coll))
    bpy.context.view_layer.update()
    return shown


def _tiles(h):
    """Two more copies of the hero at -16 and +16 studs along X (the tile pitch), for the tiling shots."""
    coll = h.users_collection[0]
    out = []
    for dx in (-16.0, 16.0):
        out.append(_copy(f"tile_{int(dx)}", h, h.matrix_world @ Matrix.Translation((dx, 0, 0)), coll))
    bpy.context.view_layer.update()
    return out


def _scale_marker(h):
    """A 5.5-stud character stand-in (a plain grey figure) beside the hero, for the scale shot."""
    a = K.fk().Asset(PFX + "char", "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=CONN, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=CONN, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=CONN, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    c.location = h.location + Vector((-h.dimensions.x / 2 - 1.5, -3.0, 0))
    bpy.context.view_layer.update()
    return c


def _close(objs, path, az, el, centre, radius):
    """m033.render_close with the studio floor hidden (it is put at the framing sphere's bottom, which would cut
    through the cliff halfway up)."""
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
    tiles = _tiles(h)
    marker = _scale_marker(h)
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        by = {o.name: o for o in objs}
        for o in objs[1:]:
            extra["part_" + o.name.replace("StoneCliff", "").lower()] = ([o], *PARTS_SHOT)
        if CONN_P in by:
            extra["part_connector_face"] = ([by[CONN_P]], 60, 12)
        if LIP_P in by:
            extra["lip_underside"] = ([by[LIP_P]], -20, -30)
        if shown:
            extra["exploded"] = (shown, -14, 20)
        extra["tiling_f34"] = ([h] + tiles, -28, 16)
        extra["tiling_top"] = ([h] + tiles, 0, 89)
        extra["scale"] = ([h, marker], -20, 8)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = m033._long_lens(kit)
        try:
            sheet = M.views(NUM, [h], extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet}
        if close:
            d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
            fr = _frame_of(h)
            # Top Lip to Body Junction: the lip's rim blocks on the C2 / C3 column tops, from the front-left
            out["junc_cu"] = _close([h], f"{d}/junc_cu.png", -20, 25, fr @ Vector((-1.2, -4.2, 8.9)), 2.6)
            # Back Connector Detail: the +X end column, the plate behind it and a front tab, from the front-right
            out["conn_cu"] = _close([h], f"{d}/conn_cu.png", 35, 18, fr @ Vector((7.9, -1.2, 7.6)), 2.6)
        return out
    finally:
        for o in shown + tiles + [marker]:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if o is marker and me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def preview(names=("f34_sheet", "front_sheet", "side_sheet", "top_sheet"), vfx=False, measure_too=True):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        sheet = M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig
    return {"sheet": sheet, "measure": measure_views() if measure_too else None}


def hero_only():
    """Rebuild just the hero (tuning loop)."""
    M.coll(NUM, TITLE)
    palette()
    h, lg = _make_hero()
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n in (BODY_P, LIP_P, CONN_P) if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals")}, "log": lg,
            "plants": {k: dict(v) for k, v in PLANT_INFO.items()}, "rocks": dict(ROCK_INFO)}
