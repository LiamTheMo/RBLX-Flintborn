"""043 Terraced Ledge (references/043.png): a modular two-step terrain tile (20 x 14 studs). A broad block of pale warm
column rock steps up in two flat lime terraces: a lower step (a palisade of seven tall flat-faced columns across the
full width, z 0 -> 4.4) capped by a lower lawn shelf (turf top z 5.6) that wraps round both front corners of the upper
block; an upper block set back 6 studs (six columns, z 4.4 -> 9.2, its front corners cut back by leaning chamfers that
leave a pocket of lower lawn at each end) capped by an upper lawn (z 10.4, the plateau of M040 / M032 / M041); a flat
columnar back; a wedge corner filler in the -X pocket; a flat grey side-connector plate with slots and tabs on the +X
end. Round leafy dome bushes (dark green on brown trunks, lime, lime with broad yellow petals), boulders, sprigs and
pebbles on both lawns; a lime apron, foot bushes, a pointed foot rock and pebbles at the foot.

    import importlib, kit_models, m040, m043; importlib.reload(kit_models); importlib.reload(m043); m043.build()

Build frame (studs): front -Y, +X right, ground z 0. W02 owns TerracedLedge*, M040 StoneCliff*: names StoneTerrace*.
- StoneTerraceBase (base_part): the stepped rock body, built directly as ONE closed shell (the surface of the union
  of the lower block L and the upper block U, so no boolean is needed: lower front wall, upper front wall, back and
  end walls, the hidden flat tops at 4.4 / 9.2 and the flat bottom at z 0, all sharing vertices), plus the four foot
  rocks as separate closed shells standing on the ground.
- StoneTerraceLowerShelf (shelf_part): the lower lawn slab (turf over a pale rock rim with a bevel band) + its lawn
  dressing (some pieces hero-only to keep the part under 1000 tris).
- StoneTerraceUpperCap (cap_part): the upper lawn slab (flat recessed underside inside rim lobes) + its dressing.
- StoneTerraceCornerFiller (filler_part): a 5-sided wedge pillar with a sloping top and a notch step.
- StoneTerraceSideConnector (connector_part): the plate with three front slots, three back tabs and a top notch.
The hero (StoneTerrace) is one object of separate closed shells: body, foot rocks, shelf, cap, filler, plate and every
leaf, petal, heart, trunk, boulder, pebble and apron patch.

TILE CONTRACT (spec 2.1; record in the export notes). Build frame:
- seams x = -10.0 and x = +10.0 (pitch 20.0): no rock, slab or plate vertex past them. The body's -X end is planar on
  x = -10 (y -6.0 .. +7.0; z 0 .. 4.4 in front of y +1.0, z 0 .. 9.2 behind). Its +X end is planar on x = +10 from y
  -6.0 to +1.6, then steps in to x 9.62 behind the 0.2 groove (y 1.6 .. 1.8) in front of the plate.
- back plane y = +7.0 (column relief inward only, to y >= 6.5). Plate back tabs stand 0.35 behind it.
- lower column tops z 4.4 (flat); lower shelf bottom 4.37, bevel 5.0 -> 5.3, turf 5.3 -> lawn 5.6. Its ends are planar on
  x = +-10 from y -5.95 to +1.0 (z 4.37 .. 5.6).
- upper column tops z 9.2; cap bottom 9.17, bevel 9.8 -> 10.1, turf 10.1 -> lawn 10.4. Its ends are planar on x = +-10
  from y +0.9 to +7.0 (at +X: to y 1.3, then x 9.98 over the plate).
- the connector plate: +X end only, x 9.6 .. 10.0, y 1.8 .. 7.0, z 0 .. 10.05.
In the hero object the build frame is at the object's origin + hero["m043_offset"] (bottom centre of the bbox).
Tile N+1 sits 20 studs along +X with the same rotation; its flat -X end meets tile N's plate and +X end.

Stages 5-6: nothing (decision 11: the sheet shows no glow, light or effect). See M043_spec.md.
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
import m011
import m012
import m033
import m040
from m040 import (_area2, _beautify, _cap, _cdt, _clamp, _dome_heart, _hull_piece, _inside, _mottle, _poly_d,
                  _prism, _resample, _steiner, _touch, _tree_of, _tri, _v2)

NUM, TITLE, SHEET = 43, "Terraced Ledge", "M043"
OFF = "m043_offset"
PFX = "_m043_"
HERO = "StoneTerrace"
BASE_P, SHELF_P, CAP_P = "StoneTerraceBase", "StoneTerraceLowerShelf", "StoneTerraceUpperCap"
FILL_P, CONN_P = "StoneTerraceCornerFiller", "StoneTerraceSideConnector"
PARTS = (BASE_P, SHELF_P, CAP_P, FILL_P, CONN_P)

ROCK, ROCK_LIGHT, ROCK_DEEP = "m043_rock", "m043_rock_light", "m043_rock_deep"
GRASS, GRASS_LIGHT, GRASS_DEEP = "m043_grass", "m043_grass_light", "m043_grass_deep"
LEAF, LEAF_LIT, LEAF_DEEP, LEAF_LIME = "m043_leaf", "m043_leaf_lit", "m043_leaf_deep", "m043_leaf_lime"
FLOWER, TRUNK, CONN = "m043_flower", "m043_trunk", "m043_connector"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low specular). Stage 4 (M043_spec.md "Stage 4"). Pass 1: K.calibrate on the kit test dome
# against TARGETS (rendered sRGB in brackets): rock #A48D85 (208,172,155), light #B29F93 (226,195,172), deep #92837C
# (184,160,144), grass #A5B40C (206,219,14), grass light #B4BE12 (227,233,28), grass deep #8E9F01 (175,192,6), leaf
# #456E19 (79,128,25), lit #67982C (123,183,44), deep #255D1F (41,106,31), lime #89A203 (168,196,7), flower #B1AA2A
# (222,206,43), trunk #552200 (106,50,29), connector #7C777C (155,145,144). Mauve guard: the calibrated rock key came
# out at hue 15.5 deg (the edge) and is turned to hue 20 deg at the same value and saturation (#A48F85); rock_deep is
# given R - B 30 at hue 18 deg (#978279); the connector key #7C777C (B = R > G) is turned warm grey R > G > B
# (#7E7978). Every rock key is R > G > B, hue 18-23 deg, R - B >= 30.
# Pass 2: the lime key is lifted a step (#89A203 -> #8DA603, rendered about +6): the lime bushes share the lawn's hue
# family, and the darker lime leaves made the lower-shelf part's family brightness follow n.z (kit check 0.52 > 0.5).
PALETTE = {
    ROCK: ("#A48F85", 0.9, False),
    ROCK_LIGHT: ("#B29F93", 0.9, False),
    ROCK_DEEP: ("#978279", 0.9, False),
    GRASS: ("#A5B40C", 0.85, True),
    GRASS_LIGHT: ("#B4BE12", 0.85, True),
    GRASS_DEEP: ("#8E9F01", 0.85, True),
    LEAF: ("#456E19", 0.85, True),
    LEAF_LIT: ("#67982C", 0.85, True),
    LEAF_DEEP: ("#255D1F", 0.85, True),
    LEAF_LIME: ("#8DA603", 0.85, True),
    FLOWER: ("#B1AA2A", 0.8, True),
    TRUNK: ("#552200", 0.95, False),
    CONN: ("#7E7978", 0.7, False),
}
# calibration targets (spec 5.4: rendered medians of unshadowed regions on the sheet)
TARGETS = {ROCK: ((0xCF, 0xAD, 0x9B), "all"), ROCK_LIGHT: ((0xE2, 0xC3, 0xAC), "all"),
           ROCK_DEEP: ((0xBA, 0x9C, 0x8C), "all"),
           GRASS: ((0xCE, 0xDB, 0x12), "green"), GRASS_LIGHT: ((0xDE, 0xE7, 0x18), "vivid"),
           GRASS_DEEP: ((0xB0, 0xC1, 0x0B), "green"),
           LEAF: ((0x4F, 0x80, 0x1A), "green"), LEAF_LIT: ((0x7D, 0xB8, 0x31), "green"),
           LEAF_DEEP: ((0x2A, 0x6A, 0x20), "green"), LEAF_LIME: ((0xAA, 0xC3, 0x05), "green"),
           FLOWER: ((0xE0, 0xCF, 0x2C), "vivid"), TRUNK: ((0x6A, 0x32, 0x10), "brown"),
           CONN: ((0x9C, 0x90, 0x8F), "stone")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS); "all" keys sampled with the floor dropped (M.sample)."""
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


def _faces(verts):
    return K.faces_of([v for v in verts if v.is_valid])


def _mix(k1, k2, t, step=0.05):
    t = round(max(0.0, min(1.0, t)) / step) * step
    return K.mix_key(k1, k2, round(t, 2))


def _miter(P, i, closed=False):
    """Outward unit normal at point i of a chain (left-hand of travel is inside) and its miter scale."""
    n_ = len(P)
    nrm = []
    if closed or i > 0:
        a, b = _v2(P[i - 1]), _v2(P[i])
        t = (b - a).normalized()
        nrm.append(Vector((t.y, -t.x)))
    if closed or i < n_ - 1:
        a, b = _v2(P[i]), _v2(P[(i + 1) % n_])
        t = (b - a).normalized()
        nrm.append(Vector((t.y, -t.x)))
    n = sum(nrm, Vector((0, 0))).normalized()
    sc = 1.0 / max(0.5, min(x.dot(n) for x in nrm))
    return n, min(sc, 2.0)


def _chain_d(p, P):
    """Distance from p to an open chain."""
    return min(m040._seg_d(p, P[i], P[i + 1]) for i in range(len(P) - 1))


def _offset(P, d, closed=False):
    out = []
    for i in range(len(P)):
        n, sc = _miter(P, i, closed)
        out.append(_v2(P[i]) + n * d * sc)
    return out


# ---- body ------------------------------------------------------------------------------------------------------------
Z_L, Z_U = 4.4, 9.2
L_BOUNDS = [-10.0, -7.2, -4.4, -1.6, 1.4, 4.2, 7.2, 10.0]
U_BOUNDS = [-8.0, -5.4, -2.7, 0.0, 2.7, 5.4, 8.0]
BACK_BOUNDS = [9.62, 7.0, 4.2, 1.4, -1.4, -4.2, -7.0, -10.0]
GROOVE_Y, CORE_X, PLATE_Y0 = 1.6, 9.62, 1.8
SEAM_YL = -6.0             # the lower step's front corner on both seams (foot)
U_SEAM_Y = 1.0             # the upper block's front corner on both seams
BODY_INFO = {}


def lower_chain(seed=43101):
    """[(foot2d, top2d, kind, col)] of the lower front wall, -X seam to +X seam (spec 2.2): the front-corner chamfers
    (c 1.0 at z 0 -> 1.4 at 4.4) and seven columns, each a dark left return face, two lit front faces either side of
    its ridge and a right return into the crease; a 0.32 batter."""
    rng = random.Random(seed)
    pts = [((-10.0, SEAM_YL), (-10.0, SEAM_YL + 0.15), "seam", 0),
           ((-9.0, -7.0), (-8.6, -6.72), "chamfer", 0)]
    nc = len(L_BOUNDS) - 1
    for j in range(nc):
        xa, xb = L_BOUNDS[j], L_BOUNDS[j + 1]
        w = xb - xa
        yf = -7.0 + rng.uniform(-0.12, 0.12)
        cols = []
        if j == 0:
            cols += [(xa + 0.66 * w, yf - 0.16, "ridge")]
        elif j == nc - 1:
            cols += [(xa + 0.17 * w, yf + 0.03, "face"), (xa + 0.36 * w, yf - 0.16, "ridge")]
        else:
            cols += [(xa + 0.17 * w, yf + 0.03, "face"), (xa + (0.5 + rng.uniform(-0.06, 0.06)) * w, yf - 0.22, "ridge"),
                     (xa + 0.83 * w, yf + rng.uniform(-0.04, 0.04), "face")]
        if j < nc - 1:
            cols.append((xb, yf + 0.52 + rng.uniform(-0.05, 0.05), "crease"))
        for x, y, k in cols:
            dy = 0.12 if k == "crease" else 0.32
            pts.append(((x, y), (x, y + dy), k, j))
    pts += [((9.0, -7.0), (8.6, -6.72), "chamfer", nc - 1), ((10.0, SEAM_YL), (10.0, SEAM_YL + 0.15), "seam", nc - 1)]
    return pts


def upper_chain(seed=43102):
    """The upper front wall, (-10, 1) -> (+10, 1): the leaning front-corner chamfers ((+-8, -1) -> (+-10, +1) at z 4.4,
    from (+-7.4, -0.72) at 9.2), each split by a mid vertex into two tall facets, and six columns."""
    rng = random.Random(seed)
    pts = [((-10.0, U_SEAM_Y), (-10.0, U_SEAM_Y), "seam", 0),
           ((-9.16, -0.16), (-8.86, -0.02), "chamfer_mid", 0),     # pushed 0.22 out: two tall facets
           ((-8.0, -1.0), (-7.4, -0.72), "chamfer", 0)]
    nc = len(U_BOUNDS) - 1
    for j in range(nc):
        xa, xb = U_BOUNDS[j], U_BOUNDS[j + 1]
        w = xb - xa
        yf = -1.0 + rng.uniform(-0.1, 0.1)
        cols = []
        if j == 0:
            cols += [(xa + 0.5 * w, yf - 0.22, "ridge"), (xa + 0.83 * w, yf + 0.02, "face")]
        elif j == nc - 1:
            cols += [(xa + 0.17 * w, yf + 0.03, "face"), (xa + 0.5 * w, yf - 0.22, "ridge")]
        else:
            cols += [(xa + 0.17 * w, yf + 0.03, "face"), (xa + (0.5 + rng.uniform(-0.06, 0.06)) * w, yf - 0.22, "ridge"),
                     (xa + 0.83 * w, yf + rng.uniform(-0.04, 0.04), "face")]
        if j < nc - 1:
            cols.append((xb, yf + 0.5 + rng.uniform(-0.05, 0.05), "crease"))
        for x, y, k in cols:
            dy = 0.12 if k == "crease" else 0.3
            pts.append(((x, y), (x, y + dy), k, j))
    pts += [((8.0, -1.0), (7.4, -0.72), "chamfer", nc - 1), ((9.16, -0.16), (8.86, -0.02), "chamfer_mid", nc - 1),
            ((10.0, U_SEAM_Y), (10.0, U_SEAM_Y), "seam", nc - 1)]
    return pts


def back_chain():
    """The rest of the outline, +X end to -X end along the back: (10, 1.6), the groove step to x 9.62, the flat +X end
    behind the plate, the back columns (ridge faces on y 7.0, creases at 6.62), the -X back corner."""
    pts = [((10.0, GROOVE_Y), "end", "E"), ((CORE_X, GROOVE_Y), "end", "E"), ((CORE_X, 7.0), "corner", "E")]
    nb = len(BACK_BOUNDS) - 1
    for j in range(nb):
        xa, xb = BACK_BOUNDS[j], BACK_BOUNDS[j + 1]
        w = xa - xb
        if j > 0:
            pts.append(((xa - 0.2 * w, 7.0), "ridge", j))
        pts.append(((xb + 0.22 * w, 7.0), "ridge", j))
        if j < nb - 1:
            pts.append(((xb, 6.62), "crease", j))
    pts.append(((-10.0, 7.0), "corner", nb - 1))
    return pts


def _ring_lower(seed=43111):
    """Per lower-chain point: verts' 3D positions [foot z 0, mid, top z 4.4]."""
    rng = random.Random(seed)
    P = lower_chain()
    out = []
    sgn = 1.0
    for i, (f2, t2, kind, col) in enumerate(P):
        foot = Vector((f2[0], f2[1], 0.0))
        top = Vector((t2[0], t2[1], Z_L))
        zm = rng.uniform(1.5, 2.9)
        mid = foot.lerp(top, zm / Z_L)
        if kind == "seam":
            mid.y += sgn * rng.uniform(0.06, 0.12)
        else:
            n, _ = _miter([p[0] for p in P], i)
            push = rng.uniform(0.04, 0.08) if kind == "crease" else rng.uniform(0.1, 0.2)
            mid += Vector((n.x, n.y, 0.0)) * push * sgn
        sgn = -sgn
        out.append((foot, mid, top))
    return out


def _ring_upper(seed=43112):
    rng = random.Random(seed)
    P = upper_chain()
    out = []
    sgn = 1.0
    for i, (f2, t2, kind, col) in enumerate(P):
        foot = Vector((f2[0], f2[1], Z_L))
        top = Vector((t2[0], t2[1], Z_U))
        row = [foot]
        for zc in (rng.uniform(5.9, 6.7), rng.uniform(7.4, 8.2)):
            m = foot.lerp(top, (zc - Z_L) / (Z_U - Z_L))
            if kind != "seam":
                n, _ = _miter([p[0] for p in P], i)
                push = rng.uniform(0.04, 0.08) if kind == "crease" else rng.uniform(0.1, 0.2)
                m += Vector((n.x, n.y, 0.0)) * push * sgn
                sgn = -sgn
            row.append(m)
        row.append(top)
        out.append(tuple(row))
    return out


def _ring_back(seed=43113):
    rng = random.Random(seed)
    P = back_chain()
    out = []
    for (xy, kind, col) in P:
        row = [Vector((xy[0], xy[1], 0.0))]
        for zc in (rng.uniform(2.6, 3.6), rng.uniform(5.8, 6.8)):
            m = Vector((xy[0], xy[1], zc))
            if kind == "ridge":
                m.y -= rng.uniform(0.0, 0.28)
            elif kind == "crease":
                m.y -= rng.uniform(0.0, 0.1)
            row.append(m)
        row.append(Vector((xy[0], xy[1], Z_U)))
        out.append(tuple(row))
    return out


def top_rings():
    """2D top rings the slabs must cap: the lower chain at 4.4 and the upper chain at 9.2 (and the upper foot)."""
    RL, RU = _ring_lower(), _ring_upper()
    return ([_v2(r[-1]) for r in RL], [_v2(r[-1]) for r in RU], [_v2(r[0]) for r in RU],
            [p[2] for p in lower_chain()], [p[2] for p in upper_chain()])


def body(a):
    """The stepped rock body as one closed shell (spec 2.2, decision 5: the union of L and U, built directly)."""
    bm = a.bm
    before = set(bm.verts)
    lay = bm.faces.layers.int.get("m043_band") or bm.faces.layers.int.new("m043_band")
    colay = bm.faces.layers.int.get("m043_col") or bm.faces.layers.int.new("m043_col")
    LP, UP, CP = lower_chain(), upper_chain(), back_chain()
    RL, RU, RC = _ring_lower(), _ring_upper(), _ring_back()
    VA = [[bm.verts.new(p) for p in r] for r in RL]
    VB = [[bm.verts.new(p) for p in r] for r in RU]
    VC = [[bm.verts.new(p) for p in r] for r in RC]
    S0p = bm.verts.new((10.0, U_SEAM_Y, 0.0))
    S0m = bm.verts.new((-10.0, U_SEAM_Y, 0.0))
    n, m = len(VA) - 1, len(VB) - 1
    faces = []

    def add(vs, band, col=0):
        f = bm.faces.new(vs)
        f[lay] = band
        f[colay] = col
        faces.append(f)
        return f
    # walls
    for i in range(n):
        for k in range(len(VA[i]) - 1):
            add((VA[i][k], VA[i + 1][k], VA[i + 1][k + 1], VA[i][k + 1]), 1, LP[i][3] + 1)
    for i in range(m):
        for k in range(len(VB[i]) - 1):
            add((VB[i][k], VB[i + 1][k], VB[i + 1][k + 1], VB[i][k + 1]), 2, UP[i][3] + 11)
    colsC = [[S0p] + VB[m]] + VC + [[S0m] + VB[0]]
    for j in range(len(colsC) - 1):
        ci, cj = colsC[j], colsC[j + 1]
        cc = CP[min(j, len(CP) - 1)][2]
        cid = 30 if cc == "E" else 21 + cc
        if len(ci) == len(cj):
            for k in range(len(ci) - 1):
                add((ci[k], cj[k], cj[k + 1], ci[k + 1]), 3, cid)
        else:
            add([ci[0], cj[0]] + list(cj[1:]) + list(reversed(ci[1:])), 3, 30)
    # the lower step's end faces on the seams (z 0 .. 4.4, in front of y +1)
    add([VA[n][0], S0p, VB[m][0], VA[n][2], VA[n][1]], 4)
    add([S0m, VA[0][0], VA[0][1], VA[0][2], VB[0][0]], 4)
    # hidden flat tops and the flat bottom: CDT with interior points
    for poly_v, z, sp, seed, band in (
            ([r[2] for r in VA] + [VB[i][0] for i in range(m, -1, -1)], Z_L, 3.6, 43121, 5),
            ([r[-1] for r in VB] + [r[-1] for r in VC], Z_U, 3.6, 43122, 5),
            ([r[0] for r in VA] + [S0p] + [r[0] for r in VC] + [S0m], 0.0, 3.6, 43123, 6)):
        P2 = [_v2(v.co) for v in poly_v]
        co, tris = _cdt(P2, (), _steiner(P2, sp, 0.9, seed))
        cf, _vm = _cap(bm, co, tris, z, True, {i: poly_v[i] for i in range(len(poly_v))})
        _beautify(bm, cf)
        for f in cf:
            if f.is_valid:
                f[lay] = band
                f[colay] = 0
    _tri(bm, [f for f in faces if f.is_valid])
    vs = [v for v in bm.verts if v not in before]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, ROCK, tint=1.0)
    _paint_body(a, vs, lay, colay)
    BODY_INFO["tris"] = sum(len(f.verts) - 2 for f in _faces(vs))
    return vs


COL_TINT = {1: 1.02, 2: 0.97, 3: 1.03, 4: 0.985, 5: 1.02, 6: 0.97, 7: 1.01,
            11: 0.98, 12: 1.03, 13: 0.97, 14: 1.02, 15: 0.985, 16: 1.03}


def _rock_key(c, z0, z1, nf, light_max=0.4, deep=0.15):
    """Stone by position only (spec 5.5): lighter in the top 40 % of the face band, broad deeper patches in the
    lowest 1.5 studs, a noise drift. Never by facing."""
    h = z1 - z0
    t = light_max * _clamp((c.z - (z0 + 0.6 * h)) / (0.4 * h)) + 0.08 * nf(c)
    if c.z < 1.5 and z0 < 0.5 and nf(c) > -0.05:
        return _mix(ROCK, ROCK_DEEP, deep)
    if t >= 0.05:
        return _mix(ROCK, ROCK_LIGHT, t, step=0.1)
    return ROCK


def _paint_body(a, vs, lay, colay):
    nf = K.noise_field(scale=0.2, seed=43131)
    fs = _faces(vs)
    by_col = {}
    for f in fs:
        band = f[lay]
        c = f.calc_center_median()
        if band == 1:
            key = _rock_key(c, 0.0, Z_L, nf)
        elif band == 2:
            key = _rock_key(c, Z_L, Z_U, nf)
        elif band in (3, 4):
            key = _rock_key(c, 0.0, Z_U, nf, light_max=0.3)
        else:
            key = ROCK                          # hidden tops and the ground: one plain stone
        f.material_index = a._mi(key)
        if band in (1, 2, 3, 4):
            by_col.setdefault(f[colay], []).append(f)
    for col, cf in by_col.items():
        _mottle(a, cf, 0.04, 0.3, 43140 + col, tint=COL_TINT.get(col, 1.0))


# ---- foot rocks, lawn boulders, filler --------------------------------------------------------------------------------
ROCK_INFO = {}
FOOT_ROCKS = {
    # name: (centre, w, d, h, lean (dx, dy) of the apex, seed)
    "FR1": ((-2.6, -7.55), 2.4, 1.6, 2.3, (0.1, 0.4), 43201),
    "FR2": ((-5.9, -7.8), 1.0, 0.9, 0.8, None, 43202),
    "FR3": ((1.2, -7.85), 0.8, 0.7, 0.6, None, 43203),
    "FR4": ((7.0, -7.8), 0.75, 0.7, 0.6, None, 43204),
}


def pointed_rock(a, name, c, w, d, h, lean, seed, z0=0.0):
    """A pointed foot rock (FR1, spec 2.2): a 5-sided base, a bulging mid ring, an apex leaning into the face."""
    rng = random.Random(seed)
    ph = rng.uniform(0, 1)
    base = [Vector((c[0] + math.cos(ph + k * 2 * math.pi / 5) * w / 2 * rng.uniform(0.85, 1.0),
                    c[1] + math.sin(ph + k * 2 * math.pi / 5) * d / 2 * rng.uniform(0.85, 1.0), z0)) for k in range(5)]
    apex = Vector((c[0] + lean[0], c[1] + lean[1], z0 + h))
    cen = sum(base, Vector()) / 5
    mid = []
    for p in base:
        t = rng.uniform(0.36, 0.48)
        q = p.lerp(apex, t)
        dd = q - cen.lerp(apex, t)
        dd.z = 0
        mid.append(q + dd * rng.uniform(0.12, 0.2))
    vs = _hull_piece(a, base + mid + [apex], ROCK)
    nf = K.noise_field(scale=0.3, seed=seed)
    for f in _faces(vs):
        cc = f.calc_center_median()
        f.material_index = a._mi(_mix(ROCK, ROCK_DEEP, 0.15) if cc.z < z0 + 0.35 * h and nf(cc) > -0.1 else
                                 _mix(ROCK, ROCK_LIGHT, 0.2 if cc.z > z0 + 0.6 * h else 0.0))
    _mottle(a, _faces(vs), 0.04, 0.4, seed, tint=rng.uniform(0.97, 1.04))
    ROCK_INFO[name] = {"tris": sum(len(f.verts) - 2 for f in _faces(vs))}
    return vs


def block_rock(a, name, c, w, d, h, seed, z0=0.0, n=5, sink=0.0):
    """A rounded-angular rock with a flat-ish crown (spec 1.4, never an egg): the hull of a foot ring, a shoulder ring
    and an inset crown ring."""
    rng = random.Random(seed)
    yr = rng.uniform(0, math.pi)
    ph = rng.uniform(0, 2 * math.pi / n)

    def ring(sc, jit):
        out = []
        for k in range(n):
            ang = ph + 2 * math.pi * k / n + rng.uniform(-0.12, 0.12)
            cx_, cy_ = math.cos(ang), math.sin(ang)
            lx = math.copysign(abs(cx_) ** 0.75, cx_) * w / 2 * sc * (1 + rng.uniform(-jit, jit))
            ly = math.copysign(abs(cy_) ** 0.75, cy_) * d / 2 * sc * (1 + rng.uniform(-jit, jit))
            out.append((c[0] + lx * math.cos(yr) - ly * math.sin(yr), c[1] + lx * math.sin(yr) + ly * math.cos(yr)))
        return out
    pts = [Vector((x, y, z0 - sink)) for x, y in ring(0.92, 0.05)]
    pts += [Vector((x, y, z0 + h * 0.55 + rng.uniform(-0.06, 0.06))) for x, y in ring(1.0, 0.05)]
    pts += [Vector((x, y, z0 + h + rng.uniform(-0.05, 0.03))) for x, y in ring(0.62, 0.05)]
    vs = _hull_piece(a, pts, ROCK)
    for f in _faces(vs):
        cc = f.calc_center_median()
        f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.45) if cc.z > z0 + 0.8 * h else
                                 _mix(ROCK, ROCK_LIGHT, 0.2) if cc.z > z0 + 0.4 * h else ROCK)
    _mottle(a, _faces(vs), 0.04, 0.6, seed, tint=rng.uniform(0.97, 1.04))
    ROCK_INFO[name] = {"tris": sum(len(f.verts) - 2 for f in _faces(vs))}
    return vs


def foot_rocks(a):
    out = []
    for nm, (c, w, d, h, lean, seed) in FOOT_ROCKS.items():
        if lean:
            out += pointed_rock(a, nm, c, w, d, h, lean, seed)
        else:
            out += block_rock(a, nm, c, w, d, h, seed, n=4)
    return out


FILLER = dict(c=(-8.95, -0.35), w=2.2, d=2.0, z0=5.5, z_lo=8.4, z_hi=9.0, notch_z=(7.05, 7.3), seed=43221)


def filler(a):
    """The Corner Filler Rock (spec 2.3): a 5-sided wedge pillar standing in the -X pocket on the lower lawn, leaning
    into the -X chamfer face; near-vertical broad faces, a notch step on its front flank at about 7.2 and a sloping top
    facet (8.4 at the outer front -> 9.0 at the inner back, under the cap's 9.17)."""
    s = FILLER
    rng = random.Random(s["seed"])
    cx, cy = s["c"]
    # the pentagon (plan): a broad front, the back corner tucked into the chamfer
    plan = [(-0.98, -0.55), (0.25, -1.0), (1.02, -0.2), (0.45, 0.95), (-0.85, 0.7)]
    plan = [(cx + x * s["w"] / 2 * 0.95, cy + y * s["d"] / 2 * 0.95) for x, y in plan]
    plan = [(max(x, -9.95), y) for x, y in plan]

    def top_z(x, y):
        # high at the inner back (+x, +y), low at the outer front (-x, -y)
        u = _clamp(((x - cx) * 0.55 + (y - cy) * 0.75) / 1.6 * 0.5 + 0.5)
        return s["z_lo"] + (s["z_hi"] - s["z_lo"]) * u
    lean = Vector((0.25, 0.2, 0.0))                     # into the chamfer (toward +x, +y)
    z0 = s["z0"]
    rings = []
    zs = (z0, s["notch_z"][0], s["notch_z"][1])
    for k, z in enumerate(zs):
        r = []
        for i, (x, y) in enumerate(plan):
            p = Vector((x, y, z)) + lean * ((z - z0) / 3.5)
            if k == 2 and i in (0, 1):                  # the notch step: the front flank steps in 0.22
                p += (Vector((cx, cy, z)) - Vector((p.x, p.y, z))).normalized() * 0.22
            if k == 1 and i in (0, 1):
                pass
            r.append(p)
        rings.append(r)
    top = []
    for i, (x, y) in enumerate(plan):
        p = Vector((x, y, 0)) + lean
        if i in (0, 1):
            p += (Vector((cx, cy, 0)) - Vector((p.x, p.y, 0))).normalized() * 0.22
        p.x = max(p.x, -9.95)
        p.z = top_z(p.x, p.y)
        top.append(p)
    rings.append(top)
    bm = a.bm
    V = [[bm.verts.new(p) for p in r] for r in rings]
    fs = []
    for k in range(len(V) - 1):
        for i in range(5):
            j = (i + 1) % 5
            fs.append(bm.faces.new((V[k][i], V[k][j], V[k + 1][j], V[k + 1][i])))
    fs.append(bm.faces.new(list(reversed(V[0]))))
    fs.append(bm.faces.new(V[-1]))
    _tri(bm, fs)
    vs = [v for r in V for v in r]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, ROCK, tint=1.0)
    for f in _faces(vs):
        cc = f.calc_center_median()
        f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.4) if cc.z > 8.2 else
                                 _mix(ROCK, ROCK_LIGHT, 0.2) if cc.z > 7.3 else ROCK)
    _mottle(a, _faces(vs), 0.04, 0.4, s["seed"], tint=0.99)
    ROCK_INFO["filler"] = {"tris": sum(len(f.verts) - 2 for f in _faces(vs)),
                           "x_min": round(min(v.co.x for v in vs), 3), "z_top": round(max(v.co.z for v in vs), 3)}
    return vs


# ---- slabs: the lower shelf and the upper cap --------------------------------------------------------------------------
LOW = dict(bot=4.37, rim=5.12, turf=5.42, top=5.6, recess=None)
UPP = dict(bot=9.17, rim=9.92, turf=10.22, top=10.4, recess=9.55)
END_N = 4                  # the lower shelf's planar ends: segments (the 0.18 turf band stays >= 5 deg)
PROUD = 0.1                # the rim stands this far in front of the column top ring (it follows every crease)
INSET = 0.24               # the turf edge sits this far behind the column top ring: the pale bevel band between
TUCK = 0.22                # the lower shelf's back edge tucks this far into the upper face
CAP_X1 = 9.98              # the cap's +X end over the plate
SLAB_INFO = {}


def slab_outline(level):
    """[(bottom_xy, top_xy, kind)] of a slab, CCW. kind front: rim (bottom .. rim at the outer line), bevel (rim ..
    turf, inset), turf band; end: planar (bottom, turf, top on one line); back: hidden (bottom, top)."""
    tl, tu, fu, kl, ku = top_rings()
    out = []
    if level == "lower":
        P = tl
        for i, p in enumerate(P):
            if kl[i] == "seam":
                q = Vector((p.x, p.y - PROUD))
                out.append((q, q, "front"))
            else:
                n, sc = _miter(P, i)
                out.append((p + n * PROUD * sc, p - n * INSET * sc, "front"))
        ys = out[-1][0].y
        ends = [Vector((10.0, ys + (U_SEAM_Y - ys) * k / END_N)) for k in range(1, END_N + 1)]
        for q in ends:
            out.append((q, q, "end"))
        Q = fu
        for i in range(len(Q) - 2, 0, -1):
            n, sc = _miter(Q, i)
            q = Q[i] - n * TUCK * sc
            out.append((q, q, "back"))
        for q in reversed(ends[:-1] + [ends[-1]]):
            q = Vector((-10.0, q.y))
            out.append((q, q, "end"))
    else:
        P = tu
        for i, p in enumerate(P):
            if ku[i] == "seam":
                q = Vector((p.x, p.y - PROUD))
                out.append((q, q, "front"))
            else:
                n, sc = _miter(P, i)
                out.append((p + n * PROUD * sc, p - n * INSET * sc, "front"))
        rest = [(10.0, GROOVE_Y + 0.02)] + [tuple(p) for p in _resample([(CAP_X1, 1.95), (CAP_X1, 7.0)], 1.6,
                                                                         closed=False)]
        rest += [tuple(p) for p in _resample([(CAP_X1, 7.0), (-10.0, 7.0)], 1.6, closed=False)[1:]]
        rest += [tuple(p) for p in _resample([(-10.0, 7.0), (-10.0, 1.0 - PROUD)], 1.6, closed=False)[1:-1]]
        for xy in rest:
            out.append((Vector(xy), Vector(xy), "end"))
    return out


def _slab_inner():
    """The cap's recess outline (the flat joining face inside the rim lobes), CCW."""
    return [Vector((p.x, p.y)) for p in _resample([(-6.9, -0.2), (6.9, -0.2), (8.85, 1.7), (8.85, 6.0), (-8.85, 6.0),
                                                     (-8.85, 1.7)], 2.2)]


def slab(a, level, seed):
    """One closed slab: lawn top (CDT with interior points), the outer wall (front: rim, pale bevel band inset to the
    turf edge, turf band; ends and back: rock up to the turf band), the bottom (lower: flat; upper: an annulus round a
    flat recessed joining face)."""
    Z = LOW if level == "lower" else UPP
    bm = a.bm
    before = set(bm.verts)
    O = slab_outline(level)
    n_ = len(O)
    cols = []
    for b2, t2, kind in O:
        if kind == "front":
            zs = [(b2, Z["bot"]), (b2, Z["rim"]), (t2, Z["turf"]), (t2, Z["top"])]
        elif kind == "end":
            zs = [(b2, Z["bot"]), (b2, Z["turf"]), (b2, Z["top"])]
        else:
            zs = [(b2, Z["bot"]), (b2, Z["top"])]
        cols.append([bm.verts.new((p.x, p.y, z)) for p, z in zs])
    wall = []
    for i in range(n_):
        j = (i + 1) % n_
        ci, cj = cols[i], cols[j]
        if len(ci) == len(cj):
            for k in range(len(ci) - 1):
                wall.append(bm.faces.new((ci[k], cj[k], cj[k + 1], ci[k + 1])))
        else:
            wall.append(bm.faces.new([ci[0], cj[0]] + list(cj[1:]) + list(reversed(ci[1:]))))
    T = [_v2(c[-1].co) for c in cols]
    st = [p for p in _steiner(T, 2.5, 0.65, seed)]
    co, tris = _cdt(T, (), st)
    top_f, _ = _cap(bm, co, tris, Z["top"], True, {i: cols[i][-1] for i in range(n_)})
    _beautify(bm, top_f)
    B = [_v2(c[0].co) for c in cols]
    if Z["recess"] is None:
        co, tris = _cdt(B, (), _steiner(B, 2.6, 0.8, seed + 1))
        bot_f, _ = _cap(bm, co, tris, Z["bot"], False, {i: cols[i][0] for i in range(n_)})
        _beautify(bm, bot_f)
        rec_f = []
    else:
        I = _slab_inner()
        co, tris = _cdt(B, [I])
        bmap = {i: cols[i][0] for i in range(n_)}
        bot_f, bmap = _cap(bm, co, tris, Z["bot"], False, bmap)
        _beautify(bm, bot_f)
        ib = [bmap[n_ + k] if (n_ + k) in bmap else bm.verts.new((I[k].x, I[k].y, Z["bot"])) for k in range(len(I))]
        cen = sum(I, Vector((0, 0))) / len(I)
        I2 = [p + (cen - p).normalized() * 0.3 for p in I]          # the inner rim wall slopes in to the recess
        it = [bm.verts.new((p.x, p.y, Z["recess"])) for p in I2]
        rec_f = []
        m_ = len(I)
        for k in range(m_):
            l = (k + 1) % m_
            rec_f.append(bm.faces.new((ib[k], it[k], it[l], ib[l])))
        co2, tris2 = _cdt(I2, (), _steiner(I2, 3.0, 1.0, seed + 3))
        rf, _ = _cap(bm, co2, tris2, Z["recess"], False, {k: it[k] for k in range(m_)})
        _beautify(bm, rf)
        rec_f += rf
    _tri(bm, [f for f in wall + rec_f if f.is_valid])
    vs = [v for v in bm.verts if v not in before]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    bm.normal_update()
    a._finish(vs, ROCK, tint=1.0)
    _paint_slab(a, vs, Z, level, [_v2(p[0]) for p in O])
    SLAB_INFO[level] = {"tris": sum(len(f.verts) - 2 for f in _faces(vs)), "outline_pts": n_}
    return vs


ROOTS = {"lower": [], "upper": []}     # (x, y, r) bush roots and boulders per lawn: the lawn deepens round them


def _paint_slab(a, vs, Z, level, Obot):
    nf = K.noise_field(scale=0.25, seed=43321 if level == "lower" else 43322)
    nr = K.noise_field(scale=0.6, seed=43323)
    _tl, _tu, fu, _kl, _ku = top_rings()
    lawn_f, rim_f = [], []
    for f in _faces(vs):
        c = f.calc_center_median()
        zlo = min(v.co.z for v in f.verts)
        if (f.normal.z > 0.95 and c.z > Z["top"] - 0.01) or (zlo > Z["turf"] - 0.01 and f.normal.z > -0.5):
            # the lawn and the turf band round its edge: one lawn colour by position (patches, deeper near roots)
            near = min([math.hypot(c.x - x, c.y - y) - r for x, y, r in ROOTS[level]] or [9.0])
            face = _chain_d(c, fu) if level == "lower" else 9.0
            if near < 0.0 or face < 0.35:
                key = _mix(GRASS, GRASS_DEEP, 0.2)
            elif near < 0.6 or face < 0.7:
                key = _mix(GRASS, GRASS_DEEP, 0.1)
            elif nf(c) > 0.3:
                key = _mix(GRASS, GRASS_LIGHT, 0.15)
            elif nf(c) > 0.12:
                key = _mix(GRASS, GRASS_LIGHT, 0.05)
            else:
                key = GRASS
            f.material_index = a._mi(key)
            lawn_f.append(f)
            continue
        zlo = min(v.co.z for v in f.verts)
        zhi = max(v.co.z for v in f.verts)
        if f.normal.z < -0.5 or zhi < Z["bot"] + 0.01:
            f.material_index = a._mi(ROCK)                       # underside, recess: plain stone
        elif zlo > Z["turf"] - 0.01:
            f.material_index = a._mi(GRASS)                      # the turf band
        elif zlo > Z["rim"] - 0.01 and f.normal.z > 0.2:
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.6))  # the pale bevel band (position: under the turf)
            rim_f.append(f)
        else:
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.4 + 0.1 * nr(c), step=0.1))   # the rim
            rim_f.append(f)
    _mottle(a, lawn_f, 0.035, 0.4, 43331)
    _mottle(a, rim_f, 0.04, 0.3, 43332)


# ---- plants: rounded leafy domes, sprigs, petals --------------------------------------------------------------------------
def _rleaf(a, base, L, W, key, yaw, pitch, roll=0.0, cup=0.2, curl=0.06, cam=0.1, th=0.05):
    """A broad rounded leaf (10 tris, closed): a blunt five-point outline (widest at 0.42 L, a two-corner blunt tip,
    tip corners about 116 deg), cupped up at the sides, a raised midrib point on top and one point underneath."""
    bm = a.bm
    rot = Matrix.Rotation(yaw, 3, "Z") @ Matrix.Rotation(-pitch, 3, "Y") @ Matrix.Rotation(roll, 3, "X")
    B = Vector(base)

    def P(x, y, z):
        t = x / L
        return bm.verts.new(B + rot @ Vector((x, y, z + cup * abs(y) - curl * L * t * t)))
    o = [P(0, 0, 0), P(0.42 * L, -W / 2, 0), P(L, -0.22 * W, 0), P(L, 0.22 * W, 0), P(0.42 * L, W / 2, 0)]
    up = P(0.5 * L, 0, cam * L)
    dn = P(0.5 * L, 0, -th * L)
    fs = []
    for i in range(5):
        j = (i + 1) % 5
        fs.append(bm.faces.new((o[i], o[j], up)))
        fs.append(bm.faces.new((o[j], o[i], dn)))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    vs = o + [up, dn]
    a._finish(vs, key)
    return vs


def _tleaf(a, mid, xdir, ndir, L, W, key, cup=0.16, curl=0.1, cam=0.09, th=0.06):
    """A broad rounded leaf (10 tris, closed; the same blunt five-point outline as _rleaf) laid on a dome: its middle
    at `mid`, its length along xdir, its face turned to ndir (outward). The sides cup out, the tip curls in."""
    bm = a.bm
    x = Vector(xdir).normalized()
    z = Vector(ndir) - x * Vector(ndir).dot(x)
    z = z.normalized() if z.length > 1e-6 else x.orthogonal().normalized()
    y = z.cross(x)
    B = Vector(mid) - x * 0.48 * L

    def P(lx, ly, lz):
        t = lx / L
        return bm.verts.new(B + x * lx + y * ly + z * (lz + cup * abs(ly) - curl * L * t * t))
    o = [P(0, 0, 0), P(0.42 * L, -W / 2, 0), P(L, -0.22 * W, 0), P(L, 0.22 * W, 0), P(0.42 * L, W / 2, 0)]
    up = P(0.5 * L, 0, cam * L)
    dn = P(0.5 * L, 0, -th * L)
    fs = []
    for i in range(5):
        j = (i + 1) % 5
        fs.append(bm.faces.new((o[i], o[j], up)))
        fs.append(bm.faces.new((o[j], o[i], dn)))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    vs = o + [up, dn]
    a._finish(vs, key)
    return vs


PLANT_INFO = {}
BUSH_SCALE, BUSH_SCALE_H = 1.3, 1.18     # the sheet's bushes read a little bigger than the study's sizes
# dome tiers, crown first: (polar angle from the top in deg, count, azimuth phase in turns, length frac of R,
# width frac of length, outward flare of the leaf's direction: 0 = down the dome's meridian, 1 = half out)
TIERS = {
    "dark": ((24, 3, 0.0, 1.12, 0.95, 0.0), (64, 3, 0.5, 1.18, 0.95, 0.25), (98, 3, 0.0, 1.12, 0.95, 0.7)),
    "lime": ((30, 3, 0.0, 1.12, 1.0, 0.0), (84, 4, 0.5, 1.1, 1.0, 0.85)),
    "small": ((32, 2, 0.0, 1.15, 1.0, 0.0), (84, 3, 0.25, 1.1, 1.0, 0.85)),
}


def _floor(vs, z0):
    floor = 0.0 if z0 < 0.5 else z0 - 0.05
    zmin = min(v.co.z for v in vs)
    if zmin < floor:
        for v in vs:
            v.co.z += floor - zmin


def bush(a, name, c, z0, R, H, kind, seed, guard=None, petals=0, tiers=None):
    """A round leafy dome (spec 1.4, decision: rounded domes, not palm stars): a hidden heart dome, a skirt tier of
    broad rounded leaves drooping out almost to the turf, an upper tier pitched up and out, a crown tier; the dark kind
    on a short brown trunk that shows at most about 0.2. Leaves touch the heart (no floating leaf). Colour by role in
    the bush (crown lit, skirt deep), never by facing. petals: broad yellow petals laid on the crown."""
    rng = random.Random(seed)
    tint = 1.0 + rng.uniform(-0.04, 0.04)
    dark = kind == "dark"
    R, H = R * BUSH_SCALE, H * BUSH_SCALE_H
    tiers = tiers or TIERS[kind if kind in TIERS else "lime"]
    out = []
    if dark:
        keys = (_mix(LEAF, LEAF_LIT, 0.4), LEAF, _mix(LEAF, LEAF_DEEP, 0.4))
        heart = _mix(LEAF, LEAF_DEEP, 0.6)
    else:
        keys = (LEAF_LIME, LEAF_LIME, LEAF_LIME)
        heart = _mix(TRUNK, LEAF_DEEP, 0.4) if petals else _mix(LEAF_LIME, LEAF_DEEP, 0.35)
    # the heart: a faceted dome (ring at C, radius rx; top rz above C), its point down to the turf
    C = Vector((c[0], c[1], z0 + 0.36 * H))
    rx, rz = 0.62 * R, 0.56 * H
    hvs = _dome_heart(a, C, rx, rz, z0 - 0.02 if z0 > 0.5 else z0, heart, seed + 1, n=4)
    out += hvs
    tree = _tree_of(hvs)
    if dark:
        out += _prism(a, c, z0 - 0.03 if z0 > 0.5 else z0, C.z, 0.14 * R, 0.1 * R, TRUNK, seed + 2, n=3)
    off = rng.uniform(0, 2 * math.pi)
    nleaves = 0
    nt = len(tiers)
    for ti, (th, cnt, ph, lf, wf, flare) in enumerate(tiers):
        key = keys[0] if ti == 0 else keys[2] if ti == nt - 1 else keys[1]
        for k in range(cnt):
            phi = off + 2 * math.pi * (k + ph) / cnt + rng.uniform(-0.18, 0.18)
            t = math.radians(th + rng.uniform(-6, 6))
            u = Vector((math.cos(phi), math.sin(phi), 0.0))
            # a point on the dome (ellipsoid rx, rz; below the equator it narrows to the foot)
            P = C + u * (rx * 1.02 * math.sin(t)) + Vector((0, 0, rz * math.cos(t) * (1.0 if t < math.pi / 2 else 0.8)))
            nrm = (u * (math.sin(t) / rx) + Vector((0, 0, math.cos(t) / rz))).normalized()
            down = (u * (rx * math.cos(t)) - Vector((0, 0, rz * math.sin(t)))).normalized()
            xdir = (down + u * flare).normalized()
            L = R * lf * rng.uniform(0.92, 1.06)
            vs = _tleaf(a, P + xdir * 0.12 * L, xdir, nrm, L, L * wf, key, curl=0.12 if ti < nt - 1 else 0.06)
            _touch(vs, tree)
            if guard:
                guard.push(vs)
            _floor(vs, z0)
            out += vs
            nleaves += 1
    for k in range(petals):
        phi = off + math.pi / max(1, petals) + 2 * math.pi * k / petals + rng.uniform(-0.15, 0.15)
        t = math.radians(20 + rng.uniform(-5, 5))
        u = Vector((math.cos(phi), math.sin(phi), 0.0))
        P = C + u * (rx * 1.1 * math.sin(t)) + Vector((0, 0, rz * 1.12 * math.cos(t)))
        nrm = (u * (math.sin(t) / rx) + Vector((0, 0, math.cos(t) / rz))).normalized()
        xdir = (u * 0.85 + Vector((0, 0, 0.15))).normalized()
        L = R * 0.62 * rng.uniform(0.92, 1.05)
        vs = _tleaf(a, P + xdir * 0.2 * L, xdir, nrm + Vector((0, 0, 0.6)), L, L * 0.98, FLOWER, cup=0.1, curl=0.04)
        _touch(vs, tree)
        out += vs
    _mottle(a, _faces(out), 0.04, 0.9, seed, tint=tint)
    xs, ys, zs = ([v.co[i] for v in out] for i in range(3))
    PLANT_INFO[name] = {"centre": [round(c[0], 2), round(c[1], 2)], "z0": round(z0, 2),
                        "size": [round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2), round(max(zs) - z0, 2)],
                        "leaves": nleaves, "petals": petals}
    return out


def sprig(a, name, c, z0, R, n, seed, guard=None, buds=0):
    """3-4 rounded lime leaves from one root (stem ends sunk into the turf), optional small yellow buds on leaf tips."""
    rng = random.Random(seed)
    out = []
    y0 = rng.uniform(0, 2 * math.pi)
    tips = []
    for k in range(n):
        yaw = y0 + 2 * math.pi * k / n + rng.uniform(-0.25, 0.25)
        L = R * rng.uniform(0.85, 1.1)
        kk = LEAF_LIME if k % 3 else _mix(LEAF_LIME, LEAF, 0.25)
        base = (c[0] + math.cos(yaw) * 0.04, c[1] + math.sin(yaw) * 0.04, z0)
        vs = _rleaf(a, base, L, L * 0.8, kk, yaw, rng.uniform(0.55, 0.95), roll=rng.uniform(-0.3, 0.3), curl=0.12)
        _floor(vs, z0)
        if guard:
            guard.push(vs)
        tips.append((vs[2].co + vs[3].co) / 2)
        out += vs
    for k in range(min(buds, len(tips))):
        out += m040._bipyramid(a, tuple(tips[k]), 0.13, 0.12, 0.08, FLOWER, seed + 10 + k, n=4)
    _mottle(a, _faces(out), 0.04, 0.9, seed, tint=1.0 + rng.uniform(-0.04, 0.04))
    PLANT_INFO[name] = {"centre": [round(c[0], 2), round(c[1], 2)], "z0": round(z0, 2), "leaves": n, "buds": buds}
    return out


def pebble(a, c, z0, s, seed, n=3):
    rng = random.Random(seed)
    vs = _prism(a, c, z0, z0 + s * rng.uniform(0.38, 0.5), s * 0.55, s * 0.36, _mix(ROCK, ROCK_LIGHT, 0.5), seed, n=n,
                sq=(1.0, rng.uniform(0.7, 0.9)))
    _mottle(a, _faces(vs), 0.03, 0.8, seed, tint=rng.uniform(0.96, 1.04))
    return vs


def apron(a, name, poly, seed):
    """A flat lime grass strip on the ground (0.14 thick), its jagged outline tucked under the rock face."""
    rng = random.Random(seed)
    P = [Vector((x + rng.uniform(-0.12, 0.12), y + rng.uniform(-0.12, 0.12))) for x, y in poly]
    if _area2(P) < 0:
        P.reverse()
    P = _resample(P, 1.45)
    bm = a.bm
    co, tris = _cdt(P)
    top_f, tm = _cap(bm, co, tris, lambda p: 0.17 + rng.uniform(-0.012, 0.012), True)
    _beautify(bm, top_f)
    bot_f, bm_ = _cap(bm, co, tris, 0.0, False)
    _beautify(bm, bot_f)
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
        cc = f.calc_center_median()
        if f.normal.z > 0.5 and cc.y > -7.35:
            f.material_index = a._mi(_mix(GRASS, GRASS_DEEP, 0.3))      # deeper where it tucks under the face
    _mottle(a, _faces(vs), 0.04, 0.5, seed)
    PLANT_INFO[name] = {"verts": n_}
    return vs


class _Guard(m040._Guard):
    pass


# dressing (spec 2.3). bushes: name -> (centre, R, H, kind, seed, petals); kind dark / lime / small
UP_Z, LOW_Z = UPP["top"] - 0.03, LOW["top"] - 0.03
UPPER_BUSHES = {
    "UL1": ((-6.6, 5.0), 0.95, 1.7, "dark", 43401, 0),
    "UL2": ((-4.4, 1.0), 1.05, 1.8, "dark", 43402, 0),
    "UL3": ((5.2, 5.4), 1.1, 1.9, "dark", 43403, 0),
    "UL4": ((6.6, 1.2), 0.8, 1.3, "lime", 43404, 0),
    "UL6": ((-6.3, 0.5), 0.72, 1.2, "lime", 43406, 0),
}
UPPER_SPRIGS = {"UL5": ((1.6, 5.8), 0.58, 3, 43405, 0)}
UPPER_ROCKS = {"UB1": ((-2.0, 1.6), 1.8, 1.6, 1.5, 43411), "UB2": ((3.0, 5.6), 1.5, 1.3, 1.2, 43412),
               "UB3": ((4.6, 0.4), 0.9, 0.8, 0.6, 43413)}
UPPER_PEBBLES = [((-7.8, 2.6), 0.4), ((-3.0, 4.6), 0.35), ((-0.2, 0.0), 0.45), ((2.4, 0.9), 0.4), ((7.6, 3.6), 0.35)]
LOWER_BUSHES = {
    "LL1": ((-8.7, -3.0), 0.95, 1.7, "dark", 43421, 0),
    "LL2": ((-6.6, -2.3), 0.8, 1.3, "lime", 43422, 4),
    "LL3": ((-0.6, -5.0), 0.6, 1.0, "dark", 43423, 0),
    "LL4": ((2.6, -2.0), 1.0, 1.8, "dark", 43424, 0),
    "LL5": ((8.3, -2.0), 0.9, 1.4, "lime", 43425, 0),
}
LOWER_SPRIGS = {"LS1": ((-2.0, -2.4), 0.55, 3, 43431, 2), "LS2": ((1.0, -4.2), 0.5, 3, 43432, 0),
                "LS3": ((4.8, -2.8), 0.55, 3, 43433, 0), "LS4": ((-4.6, -5.4), 0.5, 3, 43434, 1)}
LOWER_ROCKS = {"LB1": ((-2.9, -4.4), 1.8, 1.5, 1.4, 43441), "LB2": ((5.6, -4.6), 1.2, 1.0, 0.9, 43442)}
LOWER_PEBBLES = [((-7.2, -5.0), 0.35), ((-4.0, -3.6), 0.4), ((0.6, -2.6), 0.3), ((3.6, -5.2), 0.4), ((6.8, -3.2), 0.35)]
FOOT_BUSHES = {
    "F1": ((-9.4, -7.4), 0.75, 1.45, "dark", 43451, 0),
    "F2": ((-6.2, -7.5), 0.7, 0.9, "small", 43452, 4),
    "F4": ((2.2, -7.5), 0.52, 0.9, "small", 43454, 0),
    "F5": ((5.1, -7.45), 0.52, 0.9, "small", 43455, 0),
    "F6": ((8.7, -7.4), 0.65, 1.15, "lime", 43456, 0),
}
FOOT_SPRIGS = {"F3": ((-0.5, -7.5), 0.5, 3, 43461, 0)}
FOOT_PEBBLES = [((-7.6, -7.9), 0.45), ((0.4, -7.9), 0.5), ((3.6, -7.9), 0.4), ((6.1, -7.8), 0.45)]
APRONS = {"A_left": [(-9.9, -6.2), (-9.9, -7.3), (-9.0, -7.95), (-7.0, -8.1), (-5.0, -8.05), (-3.9, -7.8), (-4.1, -7.0),
                     (-6.0, -6.8), (-8.4, -6.8)],
          "A_mid": [(-1.9, -6.9), (-2.0, -7.9), (-0.4, -8.1), (1.4, -8.05), (3.0, -7.85), (3.0, -6.9), (0.6, -6.8)],
          "A_right": [(4.2, -6.9), (4.1, -7.85), (5.8, -8.1), (7.8, -8.05), (9.1, -7.85), (9.9, -7.2), (9.9, -6.2),
                      (8.4, -6.8)]}
# hero-only pieces (the parts stay under 1000 tris, spec 4.3)
HERO_ONLY = {"LS2", "LS3", "LS4", "LL3", "UL5", "UL6", "UB3", "lp4", "up1", "up2", "up4"}


def _roots():
    ROOTS["upper"] = ([(x, y, R * 0.5) for (x, y), R, H, k, s, p in UPPER_BUSHES.values()] +
                      [(x, y, 0.75 * w) for (x, y), w, d, h, s in UPPER_ROCKS.values()])
    ROOTS["lower"] = ([(x, y, R * 0.5) for (x, y), R, H, k, s, p in LOWER_BUSHES.values()] +
                      [(x, y, 0.75 * w) for (x, y), w, d, h, s in LOWER_ROCKS.values()] +
                      [((FILLER["c"][0]), FILLER["c"][1], 1.3)])


def lawn(a, level, part=False, guard=None):
    """A lawn's dressing; every leaf, heart, trunk, petal, rock and pebble its own closed shell, set into the turf."""
    if level == "upper":
        z, bushes, sprigs, rocks, pebbles, pk = UP_Z, UPPER_BUSHES, UPPER_SPRIGS, UPPER_ROCKS, UPPER_PEBBLES, "up"
        top = UPP["top"]
    else:
        z, bushes, sprigs, rocks, pebbles, pk = LOW_Z, LOWER_BUSHES, LOWER_SPRIGS, LOWER_ROCKS, LOWER_PEBBLES, "lp"
        top = LOW["top"]
    for nm, ((x, y), R, H, kind, seed, petals) in bushes.items():
        if part and nm in HERO_ONLY:
            continue
        bush(a, nm, (x, y), z, R, H, kind, seed, guard=guard, petals=petals)
    for nm, ((x, y), R, n, seed, buds) in sprigs.items():
        if part and nm in HERO_ONLY:
            continue
        sprig(a, nm, (x, y), z, R, n, seed, guard=guard, buds=buds)
    for nm, ((x, y), w, d, h, seed) in rocks.items():
        if part and nm in HERO_ONLY:
            continue
        block_rock(a, nm, (x, y), w, d, h, seed, z0=top, sink=0.1)
    for i, ((x, y), s) in enumerate(pebbles):
        if part and f"{pk}{i}" in HERO_ONLY:
            continue
        pebble(a, (x, y), top - 0.04, s, 43471 + i + (0 if level == "upper" else 20))


def foot(a, guard):
    for nm, ((x, y), R, H, kind, seed, petals) in FOOT_BUSHES.items():
        bush(a, nm, (x, y), 0.0, R, H, kind, seed, guard=guard, petals=petals)
    for nm, ((x, y), R, n, seed, buds) in FOOT_SPRIGS.items():
        sprig(a, nm, (x, y), 0.0, R, n, seed, guard=guard, buds=buds)
    for i, ((x, y), s) in enumerate(FOOT_PEBBLES):
        vs = pebble(a, (x, y), 0.0, s, 43491 + i, n=3)
        guard.push(vs)
    for nm, poly in APRONS.items():
        apron(a, nm, poly, 43481 + len(nm))


# ---- the side connector plate -----------------------------------------------------------------------------------------
PLATE_X = (9.6, 10.0)
PLATE_Y = (PLATE_Y0, 7.0)
PLATE_TOP = 10.05
FRONT_SLOTS = ((0.8, 1.6), (3.0, 3.8), (6.4, 7.2))         # z ranges, cut SLOT_D into the front edge
BACK_TABS = ((1.4, 2.4), (4.8, 5.8), (8.0, 9.0))
SLOT_D, TAB_BACK = 0.35, 7.35
NOTCH = (PLATE_Y0 + 0.4, PLATE_TOP - 0.35)


def plate_profile():
    y0, y1 = PLATE_Y
    pts = [(y0, 0.0)]
    for za, zb in FRONT_SLOTS:
        pts += [(y0, za), (y0 + SLOT_D, za), (y0 + SLOT_D, zb), (y0, zb)]
    pts += [(y0, NOTCH[1]), (NOTCH[0], NOTCH[1]), (NOTCH[0], PLATE_TOP), (y1, PLATE_TOP)]
    for za, zb in reversed(BACK_TABS):
        pts += [(y1, zb), (TAB_BACK, zb), (TAB_BACK, za), (y1, za)]
    pts += [(y1, 0.0)]
    if _area2(pts) < 0:
        pts.reverse()
    return pts


def plate(a):
    bm = a.bm
    P = plate_profile()
    n_ = len(P)
    P = [(p.x, p.y) for p in _resample(P, 1.9)]
    n_ = len(P)
    co, tris = _cdt(P)
    sides = {}
    for x in PLATE_X:
        vm = {i: bm.verts.new((x, co[i].x, co[i].y)) for i in range(len(co))}
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
    _mottle(a, _faces(vs), 0.02, 0.3, 43501)
    return vs


# ---- part and hero builders -------------------------------------------------------------------------------------------
def base_part(a):
    BODY_INFO.clear()
    body(a)
    foot_rocks(a)


def shelf_part(a):
    PLANT_INFO.clear()
    _roots()
    slab(a, "lower", 43311)
    lawn(a, "lower", part=True)


def cap_part(a):
    PLANT_INFO.clear()
    _roots()
    slab(a, "upper", 43312)
    lawn(a, "upper", part=True)


def filler_part(a):
    filler(a)


def connector_part(a):
    plate(a)


HERO_INFO = {}


def hero_fn(a):
    """Everything in one object of closed shells (decision 5)."""
    PLANT_INFO.clear()
    BODY_INFO.clear()
    _roots()
    bvs = body(a)
    rvs = foot_rocks(a)
    tree = _tree_of(bvs)
    guard = _Guard(tree)
    slab(a, "lower", 43311)
    slab(a, "upper", 43312)
    filler(a)
    plate(a)
    lawn(a, "lower", guard=guard)
    lawn(a, "upper", guard=guard)
    foot(a, guard)
    HERO_INFO["guard_moves"] = guard.moved


NOTES = {
    HERO: "Terraced ledge tile (20 x 14, lower lawn z 5.6, upper lawn z 10.4): a broad block of pale warm peach column "
          "rock stepping up in two flat lime terraces (seven lower and six upper flat-faced columns with dark creases, "
          "leaning front-corner chamfers leaving lower-lawn pockets at both ends), a flat columnar back, a corner "
          "filler wedge in the -X pocket, a grey side-connector plate with slots and tabs on the +X end, round leafy "
          "dark / lime / yellow-flowered bushes, boulders, sprigs and pebbles on both lawns, a lime apron, foot bushes "
          "and a pointed foot rock. Tile contract: seams x = +-10 from the build frame (see m043.py), back plane "
          "y +7 flat, lawns exactly 5.6 / 10.4 at both seams, plate on +X only. No VFX",
    BASE_P: "Terrace Base (Main Cliff Base, reusable): the stepped columnar rock body (lower step to z 4.4, upper "
            "block to z 9.2, flat back and seam ends, flat bottom) with four foot rocks",
    SHELF_P: "Lower Ledge Shelf (reusable): flat lime lawn slab (turf top z 5.6) on a pale rock rim with a bevel band, "
             "wrapping the upper block's front corners; dark, lime and yellow-flowered bushes, boulders, sprigs",
    CAP_P: "Upper Ledge Cap (reusable): flat lime lawn slab (turf top z 10.4) on a pale rock rim with a bevel band and "
           "a flat recessed joining underside; dark and lime bushes, boulders, pebbles",
    FILL_P: "Corner Filler Rock (reusable): a 5-sided wedge pillar with a sloping top and a notch step",
    CONN_P: "Side Connector (Flat Back): a flat grey plate with three slots in its front edge, three tabs on its back "
            "edge and a notch at the front-top corner",
}
COLLISION = {HERO: "precise", BASE_P: "precise", SHELF_P: "precise", CAP_P: "precise", FILL_P: "hull", CONN_P: "box"}
SEAMS = (-10.0, 10.0)


def _tri_ngons(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    ng = [f for f in bm.faces if len(f.verts) > 3]
    if ng:
        bmesh.ops.triangulate(bm, faces=ng, quad_method="BEAUTY", ngon_method="BEAUTY")
        bm.to_mesh(o.data)
    bm.free()


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
    """A piece made of separate clean closed shells (no union): n-gons triangulated, origin at the bottom centre,
    flat shading, UVs, bowties split."""
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


# ---- checks -----------------------------------------------------------------------------------------------------------
def _keys(o):
    return [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]


def _kind(ks):
    if all(k.startswith(("m043_leaf", "m043_flower")) or k.startswith("m043_trunk_x") for k in ks):
        return "leaf"
    if ks == {TRUNK}:
        return "trunk"
    if ks == {CONN}:
        return "plate"
    if any(k.startswith("m043_grass") for k in ks) and any(k.startswith("m043_rock") for k in ks):
        return "slab"
    if all(k.startswith("m043_grass") for k in ks):
        return "apron"
    return "rock"


def shells_report(o):
    """m040.shells_report with this model's kinds."""
    old = m040._kind
    m040._kind = _kind
    try:
        return m040.shells_report(o)
    finally:
        m040._kind = old


def contact_report(o, tol=0.03):
    r = m040.contact_report(o, tol=tol)
    r["floating_kinds"] = [k.replace("m043_", "") for k in r["floating_kinds"]]
    return r


def _shell_faces(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    return bm, ids, n


def capping_report(h):
    """Spec 6 on the hero: body faces with n.z > 0.5 above z 4.0 (build frame) seen from straight above (a downward
    ray through 9 points of the face hits that face first): the exposed column-top area; then everything seen from
    straight above inside the tile (a 0.1 grid over x -10..10, y -7..7) by kind: lawn, bevel / rim, body, rocks."""
    off = Vector(h[OFF])
    bm, ids, n = _shell_faces(h)
    keys = _keys(h)
    area = {}
    for f in bm.faces:
        area[ids[f.index]] = area.get(ids[f.index], 0.0) + f.calc_area()
    # the body is the largest all-rock shell
    rock_shells = {}
    for f in bm.faces:
        rock_shells.setdefault(ids[f.index], set()).add(keys[f.material_index])
    body_id = max((k for k, ks in rock_shells.items() if all(x.startswith("m043_rock") for x in ks)),
                  key=lambda k: area[k])
    sk = {k: _kind(v) for k, v in rock_shells.items()}
    tree = BVHTree.FromBMesh(bm)
    exposed, cand = 0.0, 0
    for f in bm.faces:
        if ids[f.index] != body_id or f.normal.z <= 0.5:
            continue
        c = f.calc_center_median()
        if c.z + off.z < 4.0:
            continue
        cand += 1
        pts = [c] + [c.lerp(v.co, 0.85) for v in f.verts] + [c.lerp(v.co, 0.45) for v in f.verts]
        seen = 0
        for p in pts:
            hh = tree.ray_cast(Vector((p.x, p.y, 60.0)), Vector((0, 0, -1)), 200)
            if hh[0] is not None and ids[hh[2]] == body_id and abs(hh[0].z - p.z) < 0.02:
                seen += 1
        exposed += f.calc_area() * seen / len(pts)
    seen_from_above = {}
    step = 0.1
    for xi in range(int(20 / step)):
        x = -10.0 + (xi + 0.5) * step - off.x
        for yi in range(int(14 / step)):
            y = -7.0 + (yi + 0.5) * step - off.y
            hh = tree.ray_cast(Vector((x, y, 60.0)), Vector((0, 0, -1)), 200)
            if hh[0] is None:
                continue
            k = keys[bm.faces[hh[2]].material_index]
            s_ = ids[hh[2]]
            if s_ == body_id:
                where = "body"
            elif sk[s_] == "slab":
                where = "lawn" if k.startswith("m043_grass") else "slab_rock (bevel / rim)"
            elif k.startswith("m043_rock"):
                where = "rocks (boulders, pebbles, filler, foot rocks)"
            elif k == CONN:
                where = "plate"
            else:
                where = "plants"
            seen_from_above[where] = seen_from_above.get(where, 0) + step * step
    bm.free()
    return {"exposed_column_top": round(exposed, 3), "candidates": cand,
            "from_above": {k: round(v, 2) for k, v in seen_from_above.items()}}


def cover_report():
    """Every column top-ring vertex inside its slab's bottom outline; the rim's distance in front of each column's
    front points; the turf edge behind the top ring (the bevel band width)."""
    tl, tu, fu, kl, ku = top_rings()
    out = {}
    for level, P in (("lower", tl), ("upper", tu)):
        O = slab_outline(level)
        Ob = [p[0] for p in O]
        inside = all(_inside(p, Ob) or abs(p.x) > 9.99 for p in P)
        d = [round(_poly_d(p, Ob), 3) for p in P if abs(p.x) < 9.99]
        out[level] = {"top_ring_inside": inside, "proud_min": min(d), "proud_max": max(d)}
    # the lower shelf's back edge inside the upper wall
    O = slab_outline("lower")
    back = [p[0] for p in O if p[2] == "back"]
    poly = [Vector((p.x, p.y)) for p in fu] + [Vector((10.0, 7.0)), Vector((-10.0, 7.0))]
    out["shelf_back_inside_upper"] = all(_inside(p, poly) for p in back)
    return out


def seam_report(h):
    """Tile contract on the hero (build frame): rock, slab and plate verts never past the seams; how many lie on each
    seam plane and the worst distance; the slabs' turf height and front y at both seams."""
    off = Vector(h[OFF])
    bm, ids, n = _shell_faces(h)
    keys = _keys(h)
    sk = {}
    for f in bm.faces:
        sk.setdefault(ids[f.index], set()).add(keys[f.material_index])
    kinds = {k: _kind(v) for k, v in sk.items()}
    vk = {}
    for f in bm.faces:
        for v in f.verts:
            vk[v.index] = kinds[ids[f.index]]
    past, on, worst = 0, {-10.0: 0, 10.0: 0}, 0.0
    turf = {"lower": [], "upper": []}
    front = {}
    over = {"-X": 0.0, "+X": 0.0}
    for v in bm.verts:
        k = vk.get(v.index)
        p = v.co + off
        if k in ("rock", "slab", "plate"):
            if p.x < -10.0005 or p.x > 10.0005:
                past += 1
            for s in SEAMS:
                if abs(p.x - s) < 0.015:
                    on[s] += 1
                    worst = max(worst, abs(p.x - s))
        else:
            over["-X"] = max(over["-X"], -10.0 - p.x)
            over["+X"] = max(over["+X"], p.x - 10.0)
        if k == "slab":
            for s in SEAMS:
                if abs(p.x - s) < 1e-3:
                    lvl = "lower" if p.z < 7 else "upper"
                    front[(lvl, s)] = min(front.get((lvl, s), 99), p.y)
            if abs(p.x) > 9.0:
                for lvl, zt in (("lower", LOW["top"]), ("upper", UPP["top"])):
                    if abs(p.z - zt) < 0.06:
                        turf[lvl].append(p.z)
    bm.free()
    return {"verts_past_seams": past, "verts_on_seams": {str(k): v for k, v in on.items()},
            "seam_plane_worst": round(worst, 4),
            "slab_front_y_at_seams": {f"{k[0]} {k[1]}": round(v, 3) for k, v in sorted(front.items())},
            "turf_z_within_1_of_seams": {k: [round(min(v), 3), round(max(v), 3)] for k, v in turf.items() if v},
            "foliage_overhang": {k: round(v, 3) for k, v in over.items()},
            "seams_x_object": [round(-10 - off.x, 3), round(10 - off.x, 3)],
            "back_plane_y_object": round(7.0 - off.y, 3)}


def rock_metrics(o):
    old = m040.OFF
    m040.OFF = OFF
    try:
        return m040.rock_metrics(o)
    finally:
        m040.OFF = old


# ---- render measurement ------------------------------------------------------------------------------------------------
SHEET_REF = {
    "f34": {"wh": 1.375, "R": 64.8, "G": 34.8, "L": 23.6, "F": 11.2, "D": 0.4,
            "fifths": [13.8, 8.4, 43.3, 14.3, 20.2],
            "top": [.21, .31, .46, .56, .78, .83, .86, .89, .86, .88, .89, .94, .95, .98, .97, .97, .88, .67, .68, .55,
                    .22], "rock": "#C1A393", "warm": "#D7B09C", "lawn": "#D7E10F", "bush": "#4D7E19"},
    "front": {"wh": 1.359, "R": 72.0, "G": 27.7, "L": 19.1, "F": 8.6, "D": 0.3,
              "fifths": [18.2, 0.8, 42.8, 3.1, 35.1],
              "top": [.12, .43, .60, .83, .90, .91, .96, .89, .92, .90, .90, .91, .96, .96, .99, .92, .96, .86, .58,
                      .51, .14], "rock": "#BB9E92", "warm": "#D4AE98", "lawn": "#D6DE0B"},
    "side": {"wh": 0.995, "R": 50.0, "G": 12.8, "C": 36.5,
             "top": [.11, .43, .50, .53, .59, .57, .55, .59, .62, .67, .80, .84, .86, .89, .92, .90, .96, .98, .98, .94,
                     .77], "plate": "#9C908F"},
    "rear": {"wh": 1.238, "R": 84.0, "G": 15.8, "fifths": [33.2, 0.0, 10.4, 1.4, 55.0], "rock": "#B09992"},
    "r34": {"wh": 1.146, "R": 74.4, "G": 25.3, "fifths": [21.1, 9.9, 3.3, 39.6, 26.2], "rock": "#837D89"},
    "top": {"wh": 1.026, "R": 33.2, "G": 66.3, "lawn": "#BCD11B"},
}


def measure(path, bg_tol=0.04):
    """m040.measure plus the lawn / bush split (L, F), the lit-half rock median ("warm": the brighter half of the rock
    pixels, the sheet's lit warm faces) and the grey-plate median."""
    res = m040.measure(path, bg_tol)
    kit = K.NS["KIT"]
    px = np.clip(kit["load_px"](path)[::-1, :, :3], 0, 1)
    bg = np.median(np.concatenate([px[:4, :4].reshape(-1, 3), px[:4, -4:].reshape(-1, 3)]), axis=0)
    sil = np.abs(px - bg).max(-1) > bg_tol
    cls, h, s, v = m040.classify(px)
    c = np.where(sil, cls, 0)
    lawn = (c == 2) & (h < 80) & (v >= 0.6)
    bushm = (c == 2) & ~lawn
    tot = max(1, int(((c >= 1) & (c <= 4)).sum()))
    res["L"] = round(100 * float(lawn.sum()) / tot, 1)
    res["F"] = round(100 * float(bushm.sum()) / tot, 1)
    rk = c == 1
    if rk.any():
        lum = px[rk].mean(axis=1)
        hi = lum >= np.median(lum)
        sel = px[rk][hi] * 255
        res["warm"] = "#" + "".join(f"{int(x):02X}" for x in np.median(sel, axis=0))
    return res


def measure_views(out_dir=None):
    d = out_dir or f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    res = {}
    for k, f in (("f34", "f34_sheet"), ("front", "front_sheet"), ("side", "side_sheet"), ("rear", "rear_sheet"),
                 ("r34", "r34_sheet"), ("top", "top_sheet")):
        try:
            m = measure(f"{d}/{f}.png")
        except Exception as e:
            res[k] = str(e)
            continue
        ref = SHEET_REF[k]
        if "top" in ref:
            m["top_err_mean"] = round(float(np.mean(np.abs(np.array(m["top"]) - np.array(ref["top"])))), 3)
            m["top_err_max"] = round(float(np.max(np.abs(np.array(m["top"]) - np.array(ref["top"])))), 3)
        m.pop("top", None)
        m["sheet"] = {kk: vv for kk, vv in ref.items() if kk != "top"}
        res[k] = m
    return res


# ---- build ------------------------------------------------------------------------------------------------------------
TARGET_SIZE = ((20.6, 0.6), (15.5, 0.5), (12.3, 0.4))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me is not None and isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m043_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib",
                                                                                 "StoneTerrace"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build_objects(parts=True):
    M.coll(NUM, TITLE)
    ROCK_INFO.clear()
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in ((BASE_P, base_part), (SHELF_P, shelf_part), (CAP_P, cap_part), (FILL_P, filler_part),
                         (CONN_P, connector_part)):
            objs[name], log[name] = _make_plain(name, fn)
            if name == SHELF_P:
                log["shelf_plants"] = {k: dict(v) for k, v in PLANT_INFO.items()}
            if name == CAP_P:
                log["cap_plants"] = {k: dict(v) for k, v in PLANT_INFO.items()}
    h, log["hero"] = _make_plain(HERO, hero_fn, role="hero", budget=4000)
    log["hero"]["guard_moves"] = HERO_INFO.get("guard_moves")
    log["plants"] = {k: dict(v) for k, v in PLANT_INFO.items()}
    log["rocks"] = {k: dict(v) for k, v in ROCK_INFO.items()}
    log["body"] = dict(BODY_INFO)
    log["slabs"] = {k: dict(v) for k, v in SLAB_INFO.items()}
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
    by = {o.name: o for o in order}
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
    for nm in (FILL_P, CONN_P):
        if nm in shells and len(shells[nm]) != 1:
            problems.append(f"{nm}: {len(shells[nm])} shells, expected 1")
    contact = {o.name: contact_report(o) for o in order if o.name in (HERO, SHELF_P, CAP_P, BASE_P)}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} shells touch nothing within 0.03, {c['unchained']} have no chain "
                            f"of contact to the ground")
    cap = capping_report(h)
    if cap["exposed_column_top"] > 0.0:
        problems.append(f"{HERO}: exposed column-top area {cap['exposed_column_top']}")
    cover = cover_report()
    for lvl in ("lower", "upper"):
        if not cover[lvl]["top_ring_inside"] or cover[lvl]["proud_min"] < 0.08:
            problems.append(f"{HERO}: the {lvl} slab does not cap its column tops ({cover[lvl]})")
    if not cover["shelf_back_inside_upper"]:
        problems.append(f"{HERO}: the lower shelf's back edge is not tucked into the upper face")
    seam = seam_report(h)
    if seam["verts_past_seams"] or seam["seam_plane_worst"] > 0.001:
        problems.append(f"{HERO}: seam contract broken {seam}")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 11: none)")
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
            "shells": kinds, "contact": contact, "capping": cap, "cover": cover, "seams": seam, "thin": thin,
            "problems": problems, "uv": uv,
            "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
            "rock_metrics": rock_metrics(by[BASE_P]) if BASE_P in by else None,
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
# decision 9: f34_sheet governs (probed az -8 / -12 / -15 / -20 x e 16 / 18 / 20 / 24: (-20, 18) best, spec stage 1);
# front_sheet (probed e 12 / 16 / 20: 12 best) and side_sheet (90, 8) strict; rear_sheet (180, 14),
# r34_sheet (215, 20) and top_sheet (0, 89) loosely. Floor hidden and a 3x lens on the *_sheet shots (m033._long_lens).
SHEET_VIEWS = {"f34_sheet": (-20, 18), "front_sheet": (0, 12), "side_sheet": (90, 8), "rear_sheet": (180, 14),
               "r34_sheet": (215, 20), "top_sheet": (0, 89)}
PARTS_SHOT = (-20, 25)


def _copy(tag, src, m, coll):
    c = bpy.data.objects.new(f"{PFX}{tag}", src.data)
    coll.objects.link(c)
    c.matrix_world = m
    return c


def _frame_of(h):
    return h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded Construction: the base, the shelf lifted above it, the cap
    above that, the plate pulled out to the left (turned to the viewer), the filler to the right."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []
    o0 = Matrix.Translation((objs[0].location.x + 100, objs[0].location.y, 0))
    lift = {BASE_P: 0.0, SHELF_P: 3.0, CAP_P: 6.5}
    for nm, dz in lift.items():
        if nm in by:
            shown.append(_copy(f"expl_{nm}", by[nm], o0 @ Matrix.Translation(Vector(by[nm][OFF]) + Vector((0, 0, dz))),
                               coll))
    if CONN_P in by:
        p = Vector(by[CONN_P][OFF])
        shown.append(_copy("expl_plate", by[CONN_P], o0 @ Matrix.Translation((-16.0, -2.0, 0.0)) @
                           Matrix.Rotation(math.radians(-75), 4, "Z") @ Matrix.Translation((0, 0, p.z)), coll))
    if FILL_P in by:
        p = Vector(by[FILL_P][OFF])
        shown.append(_copy("expl_filler", by[FILL_P], o0 @ Matrix.Translation((15.0, -3.0, 0.0)), coll))
    bpy.context.view_layer.update()
    return shown


def _tiles(h):
    coll = h.users_collection[0]
    out = []
    for dx in (-20.0, 20.0):
        out.append(_copy(f"tile_{int(dx)}", h, h.matrix_world @ Matrix.Translation((dx, 0, 0)), coll))
    bpy.context.view_layer.update()
    return out


def _m040_joint(h):
    """M040's StoneCliff placed at this tile's +X end with the back planes aligned (spec 2.1): its build frame at
    (10 + 8, 7 - 4) of ours."""
    src = bpy.data.objects.get("StoneCliff")
    if not src or "m040_offset" not in src:
        return []
    m = _frame_of(h) @ Matrix.Translation((18.0, 3.0, 0.0)) @ Matrix.Translation(Vector(src["m040_offset"]))
    c = _copy("m040_joint", src, m, h.users_collection[0])
    bpy.context.view_layer.update()
    return [c]


def _marker(h, at, tag):
    a = K.fk().Asset(PFX + tag, "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=CONN, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=CONN, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=CONN, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    c.matrix_world = _frame_of(h) @ Matrix.Translation(at)
    bpy.context.view_layer.update()
    return c


def _scale_markers(h):
    """Three 5.5-stud character stand-ins: on the ground in front, on the lower lawn, on the upper lawn."""
    return [_marker(h, (-4.6, -9.6, 0.0), "char_ground"), _marker(h, (-4.4, -3.6, LOW["top"]), "char_lower"),
            _marker(h, (0.6, 3.6, UPP["top"]), "char_upper")]


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
    tiles = _tiles(h)
    joint = _m040_joint(h)
    markers = _scale_markers(h)
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        by = {o.name: o for o in objs}
        for o in objs[1:]:
            extra["part_" + o.name.replace("StoneTerrace", "").lower()] = ([o], *PARTS_SHOT)
        if CAP_P in by:
            extra["cap_underside"] = ([by[CAP_P]], -20, -30)
        if BASE_P in by:
            extra["base_bottom"] = ([by[BASE_P]], -20, -35)
        if CONN_P in by:
            extra["part_connector_face"] = ([by[CONN_P]], 60, 12)
        if shown:
            extra["exploded"] = (shown, -20, 22)
        extra["tiling_f34"] = ([h] + tiles, -28, 16)
        extra["tiling_top"] = ([h] + tiles, 0, 89)
        if joint:
            extra["tiling_m040"] = ([h, tiles[0]] + joint, -30, 18)
        extra["scale"] = ([h] + markers, -20, 10)
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
            out["junc_cu"] = _close([h], f"{d}/junc_cu.png", -35, 12, fr @ Vector((-3.0, -2.2, 6.6)), 2.8)
            out["thick_cu"] = _close([h], f"{d}/thick_cu.png", -20, 22, fr @ Vector((3.0, -6.4, 4.9)), 2.6)
            out["conn_cu"] = _close([h], f"{d}/conn_cu.png", 60, 15, fr @ Vector((9.8, 1.6, 6.0)), 3.6)
        return out
    finally:
        for o in shown + tiles + joint + markers:
            me = o.data
            mine = o in markers
            bpy.data.objects.remove(o, do_unlink=True)
            if mine and me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def preview(names=("f34_sheet", "front_sheet", "side_sheet", "top_sheet"), vfx=False, measure_too=True):
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        sheet = M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig
    return {"sheet": sheet, "measure": measure_views() if measure_too else None}


def hero_only():
    M.coll(NUM, TITLE)
    palette()
    h, lg = _make_plain(HERO, hero_fn, role="hero", budget=4000)
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals")}, "log": lg,
            "plants": {k: dict(v) for k, v in PLANT_INFO.items()}, "rocks": dict(ROCK_INFO),
            "body": dict(BODY_INFO), "slabs": {k: dict(v) for k, v in SLAB_INFO.items()}}
