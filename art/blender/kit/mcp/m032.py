"""032 Shoreline Corner (references/032.png): a riverbank shoreline corner tile (32 x 26 studs, W03's levels). A raised
grass-topped ridge whose seaward side is a row of big fat flat-faced grey cliff columns with bevelled flat tops; the
coast runs along the front on the left, then turns 45 degrees and runs to the back-right. A warm sand beach at the
cliff foot widens in the middle and pinches out at both ends; flat cyan water fills the front-right of the tile, edged
by a separate flat foam ribbon, with faceted boulders at the waterline and standing in the water in foam rings. On the
ridge: lime lawn, a sand path along the rim, three small pines, fan bushes, daisies and yellow flowers. At the left end
two low blocky grass boxes with tan sides.

    import importlib, kit_models, m032; importlib.reload(kit_models); importlib.reload(m032); m032.build()

Build frame (studs): front -Y, +X right, ground z 0 (the flat underside of the land and of the water bed). Tile X -16
.. 16, Y -13 .. 13. Levels (the W03 tile contract, M032_spec.md 2.1): bed 0.2, water 1.0, foam 1.03-1.07, beach
1.0 -> 1.8, grass top 10.4.

Parts (the sheet's Exploded Construction, decision 5), each from its own function:
- ShorelineCornerGrassTop (grass_top_part): the ridge's grass slab (turf, soil band, sand path) with its pines,
  bushes, flowers and lawn rocks.
- ShorelineCornerSandStrip (sand_strip_part): the beach slab.
- ShorelineCornerRockSlope (rock_slope_part): the front column row C0-C5, the foot boulder L1 and the waterline rocks.
- ShorelineCornerWaterPlane (water_plane_part): the water slab (with the boulder holes) over its bed.
- ShorelineCornerFoam (foam_part): the foam mesh alone.

The hero (ShorelineCorner, decision 9) is one object: one closed land shell (the ridge core, the front and back
column rows, the grass slab and its vegetation, the beach, the bed, the low boxes and every boulder: exact unions one
shell at a time, merge 0, then a floor cut at z 0), plus a closed water shell (m032_water) and a closed foam shell
(m032_water_foam), which never touch the land: the water's shore edge stands 0.04 off the beach's waterline wall, its
bottom 0.06 over the bed, and both water and foam are cut round every boulder by a 2D hole 0.04 outside the
boulder's section. Both water keys contain "water", so the exporter makes them two see-through, non-colliding water
pieces. Colour (stage 4) is painted by position inside the builders before the union. See M032_spec.md.
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
import m026

NUM, TITLE, SHEET = 32, "Shoreline Corner", "M032"
OFF = "m032_offset"
PFX = "_m032_"
HERO = "ShorelineCorner"

GRASS, LEAF, PINE, BARK = "m032_grass", "m032_leaf", "m032_pine", "m032_bark"
PETAL, POLLEN = "m032_petal", "m032_pollen"
SAND, SAND_LIGHT, SOIL, SOIL_DARK = "m032_sand", "m032_sand_light", "m032_soil", "m032_soil_dark"
ROCK, BED = "m032_rock", "m032_bed"
WATER, FOAM = "m032_water", "m032_water_foam"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0
POLISH_LONG = 1.0          # the last needle pass's longest collapsed edge (hidden column seams)

# key -> (hex, roughness, low_spec); the comment is the calibration target (spec 5.4: unshadowed rendered regions)
# Stage 4 pass 1 (K.calibrate on the kit dome, 2026-10-29): rendered medians grass (167,205,5), leaf (58,142,11), pine
# (10,106,45), bark (110,68,32), pollen (229,202,48), sand (255,206,131), sand_light (255,225,157), soil (185,134,68),
# soil_dark (147,102,49), rock (176,156,155), petal (255,252,237).
PALETTE = {GRASS: ("#88A900", 0.9, True),          # #A7CE09 exploded lawn
           LEAF: ("#215C0C", 0.9, True),           # #3A8E0C bush crowns; fix 1: x0.75 (f34 bush #359013 vs #1B5A03)
           PINE: ("#055D2D", 0.9, True),           # #07692D pine medians
           BARK: ("#573300", 0.9, False),          # #6E440A
           PETAL: ("#C8C8C4", 0.8, False),         # #F2F0E8
           POLLEN: ("#B5A51A", 0.8, False),        # #E6CA2F
           SAND: ("#F0C47E", 0.95, False),         # #FBCF83 exploded strip; pass 2 paler (f34 S #F6B46F, #E6BA7D vs #FAD58E)
           SAND_LIGHT: ("#F7E8B4", 0.95, False),   # #FCE29C open beach; pass 2 paler; fix 1: lit open beach renders #FFE49E (sheet #FCE59E)
           SOIL: ("#A8804A", 0.95, False),         # #B98745 tan sides; pass 2 lighter (shaded sides read as dark soil D)
           SOIL_DARK: ("#765424", 0.95, False),    # #936631 underside
           ROCK: ("#B0A4A1", 0.85, False),         # #B19C9A exploded rocks; pass 2 x1.2; fix 1: hue 330 -> 12 deg, no clipped lit faces
           BED: ("#054F6C", 0.9, False),           # tuned so the water median lands on #06DBFE
           WATER: ("#00C8F4", 0.15, False),        # #06DBFE (pass 2: f34 water read #26EBFF, then #25CEFA)
           FOAM: ("#D5FCFD", 0.6, False)}          # #D5FCFD
TRANSPARENCY = {WATER: 0.3, FOAM: 0.1}

TARGETS = {GRASS: ((0xA7, 0xCE, 0x09), "green"), LEAF: ((0x3A, 0x8E, 0x0C), "green"),
           PINE: ((0x07, 0x69, 0x2D), "green"), BARK: ((0x6E, 0x44, 0x0A), "brown"),
           POLLEN: ((0xE6, 0xCA, 0x2F), "vivid"),
           SAND: ((0xFB, 0xCF, 0x83), "all"), SAND_LIGHT: ((0xFC, 0xE2, 0x9C), "all"),
           SOIL: ((0xB9, 0x87, 0x45), "brown"), SOIL_DARK: ((0x93, 0x66, 0x31), "brown"),
           ROCK: ((0xB1, 0x9C, 0x9A), "stone"), PETAL: ((0xF2, 0xF0, 0xE8), "all")}


def palette():
    f = K.fk()
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        mat = f.material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        if k in TRANSPARENCY:
            f.set_water_transparency(mat, TRANSPARENCY[k])
            _refresh_water_texture(mat, k, hexcol)


def _refresh_water_texture(mat, key, hexcol):
    """The kit's water preview texture is painted from the key's colour when the material is first made; repaint it
    (and reload the image) when the colour has changed since, so the renders show the current key."""
    f = K.fk()
    nt = mat.node_tree
    tex = nt.nodes.get("FB_WaterTex") if nt else None
    if tex is None or mat.get("m032_tex_hex") == hexcol:
        mat["m032_tex_hex"] = hexcol
        return
    mapping = tex.inputs["Vector"].links[0].from_node if tex.inputs["Vector"].links else None
    coord = mapping.inputs["Vector"].links[0].from_node if mapping and mapping.inputs["Vector"].links else None
    img = tex.image
    for n in (tex, mapping, coord):
        if n is not None:
            nt.nodes.remove(n)
    f._water_texture(mat, key, hexcol)
    if img is not None:
        img.reload()
    mat["m032_tex_hex"] = hexcol


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


# ---- small helpers ---------------------------------------------------------------------------------------------------
STEPS = 4      # 25 / 50 / 75 % in-between keys


def _q(t):
    return round(min(1.0, max(0.0, t)) * STEPS) / STEPS


def _mix(k1, k2, t):
    return K.mix_key(k1, k2, _q(t))


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


def _paint(a, faces, key):
    mi = a._mi(key)
    for f in faces:
        f.material_index = mi


def _v2(p):
    return Vector((p[0], p[1]))


# ---- 2D geometry ---------------------------------------------------------------------------------------------------------
def _catmull(pts, step):
    """An open polyline through pts, Catmull-Rom smoothed and resampled about every `step` studs."""
    P = [_v2(p) for p in pts]
    P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    out = [P[1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        n = max(1, int(round((p2 - p1).length / step)))
        for k in range(1, n + 1):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    return out


def _offset_line(pts, d):
    """Offset an open polyline to the right of its travel direction by d (negative: to the left)."""
    P = [_v2(p) for p in pts]
    out = []
    for i, p in enumerate(P):
        a = P[max(0, i - 1)]
        b = P[min(len(P) - 1, i + 1)]
        t = (b - a).normalized()
        n = Vector((t.y, -t.x))
        out.append(p + n * d)
    return out


def _offset_poly(poly, d):
    """Offset a closed CCW polygon outward by d (mitred; negative insets)."""
    P = [_v2(p) for p in poly]
    n_ = len(P)
    out = []
    for i in range(n_):
        a, p, b = P[i - 1], P[i], P[(i + 1) % n_]
        t1, t2 = (p - a).normalized(), (b - p).normalized()
        n1, n2 = Vector((t1.y, -t1.x)), Vector((t2.y, -t2.x))
        m = (n1 + n2)
        m = m.normalized() if m.length > 1e-6 else n1
        out.append(p + m * (d / max(0.35, m.dot(n1))))
    return out


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
    ab = b - a
    t = 0.0 if ab.length_squared < 1e-12 else max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
    return (p - (a + ab * t)).length


def _dist_line(p, pts, closed=False):
    p = _v2(p)
    P = [_v2(q) for q in pts]
    segs = list(zip(P, P[1:] + ([P[0]] if closed else [])))
    return min(_seg_d(p, a, b) for a, b in segs)


def _hull2(pts):
    """2D convex hull (monotone chain), CCW."""
    P = sorted({(round(p[0], 5), round(p[1], 5)) for p in pts})
    if len(P) < 3:
        return [Vector(p) for p in P]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return [Vector(p) for p in lo[:-1] + hi[:-1]]


def _simplify_convex(poly, nmax=8):
    """Drop the vertices of a convex polygon that add least area until at most nmax remain (keeps it outside the
    original only if the caller offsets it afterwards by more than the loss; used for boulder holes)."""
    P = list(poly)
    while len(P) > nmax:
        best, bi = None, 0
        for i in range(len(P)):
            a, p, b = P[i - 1], P[i], P[(i + 1) % len(P)]
            area = abs((p.x - a.x) * (b.y - a.y) - (p.y - a.y) * (b.x - a.x)) / 2
            if best is None or area < best:
                best, bi = area, i
        P.pop(bi)
    return P


def _steiner(pos, neg, spacing, margin, seed):
    """Jittered grid points inside a pos polygon and no neg polygon, at least margin from every polygon edge."""
    rng = random.Random(seed)
    xs = [p[0] for poly in pos for p in poly]
    ys = [p[1] for poly in pos for p in poly]
    out = []
    y = min(ys) + spacing * 0.5
    j = 0
    while y < max(ys):
        x = min(xs) + spacing * (0.25 + 0.5 * (j % 2))
        while x < max(xs):
            p = Vector((x + rng.uniform(-0.25, 0.25) * spacing, y + rng.uniform(-0.25, 0.25) * spacing))
            if any(_inside(p, q) for q in pos) and not any(_inside(p, q) for q in neg):
                if min(_dist_line(p, q, True) for q in list(pos) + list(neg)) > margin:
                    out.append(p)
            x += spacing
        y += spacing
        j += 1
    return out


def cdt_region(pos, neg=(), steiner=(), tidy=True, min_island=0.0, merge=0.04):
    """2D triangulation of (union of pos polygons) minus (union of neg polygons), with optional interior points.
    tidy: merge points closer than 0.04, drop boundary points on near-straight runs, re-triangulate with the
    beauty fill (no needles where constraint edges cross). min_island: drop connected pieces smaller than this area.
    Returns (coords [Vector2], tris [(i, j, k)] CCW)."""
    verts, faces = [], []
    for poly in list(pos) + list(neg):
        idx = []
        for p in poly:
            idx.append(len(verts))
            verts.append(_v2(p))
        faces.append(idx)
    verts += [_v2(p) for p in steiner]
    co, _e, tf, _ov, _oe, of = delaunay_2d_cdt(verts, [], faces, 0, 1e-5, True)
    npos = len(pos)
    tris = []
    for f, orig in zip(tf, of):
        if any(i < npos for i in orig) and not any(i >= npos for i in orig) and len(f) == 3:
            a_, b_, c_ = (co[i] for i in f)
            ar = (b_.x - a_.x) * (c_.y - a_.y) - (b_.y - a_.y) * (c_.x - a_.x)
            if abs(ar) < 1e-7:
                continue
            tris.append(tuple(f) if ar > 0 else (f[0], f[2], f[1]))
    if tidy or min_island:
        co, tris = _tidy2d(co, tris, min_island=min_island, tidy=tidy, merge=merge)
    return co, tris


def _tidy2d(co, tris, merge=0.04, straight=172.0, min_island=0.0, tidy=True, max_edge=1.1):
    bm = bmesh.new()
    vs = {}
    for t in tris:
        for i in t:
            if i not in vs:
                vs[i] = bm.verts.new((co[i].x, co[i].y, 0.0))
    for t in tris:
        try:
            bm.faces.new([vs[i] for i in t])
        except ValueError:
            pass
    if tidy:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge)
        for _ in range(3):
            cand = []
            for v in bm.verts:
                be = [e for e in v.link_edges if e.is_boundary]
                if len(be) == 2 and len(v.link_edges) <= 3:
                    d1, d2 = (e.other_vert(v).co - v.co for e in be)
                    if (d1.length > 1e-6 and d2.length > 1e-6 and math.degrees(d1.angle(d2)) > straight
                            and d1.length + d2.length <= max_edge):
                        cand.append(v)
            if not cand:
                break
            bmesh.ops.dissolve_verts(bm, verts=cand)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=merge)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                              ngon_method="BEAUTY")
        inner = [e for e in bm.edges if len(e.link_faces) == 2]
        bmesh.ops.beautify_fill(bm, faces=bm.faces, edges=inner)
    if min_island:
        bm.faces.ensure_lookup_table()
        bm.faces.index_update()
        ids, n = M._shell_ids(bm)
        area = [0.0] * n
        for f in bm.faces:
            area[ids[f.index]] += f.calc_area()
        drop = [f for f in bm.faces if area[ids[f.index]] < min_island]
        if drop:
            bmesh.ops.delete(bm, geom=drop, context="FACES")
    # a 2D bowtie (two face fans meeting at one boundary point) would give a wall edge shared by four walls: split
    # it into one point per fan, each nudged 0.02 into its own fan
    for v in [v for v in bm.verts if sum(1 for e in v.link_edges if e.is_boundary) > 2]:
        for nv in bmesh.utils.vert_separate(v, []):
            if nv.link_faces:
                c = sum((f.calc_center_median() for f in nv.link_faces), Vector()) / len(nv.link_faces)
                d = c - nv.co
                if d.length > 1e-6:
                    nv.co += d.normalized() * min(0.02, 0.5 * d.length)
    bm.verts.index_update()
    co2 = [Vector((v.co.x, v.co.y)) for v in bm.verts]
    tris2 = []
    bm.normal_update()
    for f in bm.faces:
        ids_ = [v.index for v in f.verts]
        if len(ids_) != 3:
            continue
        tris2.append(tuple(ids_) if f.normal.z > 0 else (ids_[0], ids_[2], ids_[1]))
    bm.free()
    return co2, tris2


def slab(a, co, tris, ztop, zbot, mat, bands=(), quad_walls=False):
    """A closed slab over a 2D triangulation: the top surface at ztop(p), the bottom at zbot(p) (callables of a 2D
    point), walls round every boundary edge, with extra wall rings at ztop(p) - band for each band. Returns
    (top_faces, wall_faces, bottom_faces, verts)."""
    bm = a.bm
    used = sorted({i for t in tris for i in t})
    top = {i: bm.verts.new((co[i].x, co[i].y, ztop(co[i]))) for i in used}
    bot = {i: bm.verts.new((co[i].x, co[i].y, zbot(co[i]))) for i in used}
    tf, bf, wf = [], [], []
    directed = set()
    for i, j, k in tris:
        tf.append(bm.faces.new((top[i], top[j], top[k])))
        bf.append(bm.faces.new((bot[i], bot[k], bot[j])))
        directed |= {(i, j), (j, k), (k, i)}
    bnd = [(i, j) for i, j in directed if (j, i) not in directed]
    rings = {}
    for i in {i for e in bnd for i in e}:
        col = [bot[i]]
        for b in sorted(bands, reverse=True):
            z = ztop(co[i]) - b
            if z > zbot(co[i]) + 0.05:
                col.append(bm.verts.new((co[i].x, co[i].y, z)))
        col.append(top[i])
        rings[i] = col
    for i, j in bnd:
        ci, cj = rings[i], rings[j]
        n = min(len(ci), len(cj))
        # columns of equal length (bands that fit at both ends); otherwise one tall quad
        if len(ci) != len(cj):
            ci, cj = [ci[0], ci[-1]], [cj[0], cj[-1]]
            n = 2
        for k in range(n - 1):
            wf.append(bm.faces.new((ci[k], cj[k], cj[k + 1], ci[k + 1])))
    if not quad_walls:
        _tri(bm, wf)
    allv = list(top.values()) + list(bot.values()) + [v for c in rings.values() for v in c[1:-1]]
    wf = [f for f in K.faces_of(allv) if f not in set(tf) and f not in set(bf)]
    a._finish(allv, mat, tint=1.0)
    return tf, wf, bf, allv


# ---- layout (studs, build frame; tuned on the f34_sheet render against the sheet's hero, spec 2) ----------------------
# The ridge outline (RIDGE, CCW) is not hand-placed any more (fix round 1): it is the outer hull of the column tops
# (ridge_outline()), so the grass slab caps every column like the sheet's "flat joining surface between rock and top
# piece": its rim runs RIM_IN inside each column's top (shoulder) edge, the column tops sit SEAT under the turf.
RIDGE = []
GRASS_TOP = 10.4
GRASS_THICK = 1.05
SLAB_STEINER = 4.2         # the slab top's interior point spacing
TURF = 0.62                 # the green turf on the slab's side band (the exploded Grass Top's green sides); below it a brown soil line
CORE_OUT = 0.9
RIDGE_STEP = 2.6


def grass_z(p):
    """The ridge's turf height: 10.4, stepping down to 9.7 at the left end (C0, spec 2.2)."""
    x = p[0]
    t = min(1.0, max(0.0, (x + 11.0) / 4.5))
    return 9.7 + (GRASS_TOP - 9.7) * t


# the waterline (front to back): the beach is at 1.0 on it, the water slab to the right of travel. Its last point is
# on the water's back cut (WATER_BACK): the hero shows the water's right edge only up to h .5 (Y about 8), with the
# tile's back-right corner empty
WATERLINE = [(-6.0, -13.0), (-3.6, -12.0), (-0.8, -10.9), (0.6, -7.2), (3.55, -3.95), (6.4, -1.4), (8.8, 0.4),
             (10.4, 2.0), (11.8, 3.8), (12.6, 5.6), (12.8, 7.2), (12.4, 8.3)]
WATER_BACK = [(16.0, 8.1), (14.0, 8.4)]
WL_STEP = 1.4
# the beach's inland edge (back to front), hidden inside the columns and the ridge core
BEACH_IN = [(10.2, 7.4), (9.6, 6.0), (7.8, 4.4), (5.6, 2.6), (2.0, -0.6), (-0.6, -2.6), (-2.6, -5.2), (-4.0, -7.4),
            (-6.6, -8.4), (-7.0, -10.6), (-6.8, -12.0)]
BEACH_TOP, BEACH_SLOPE = 1.8, 2.6        # the beach rises 1.0 -> 1.8 over BEACH_SLOPE studs from the waterline
BED_TOP = 0.2
# the water's shore edge and every boulder hole stand WATER_GAP off the land: more than the sliver cleanup's largest
# vertex move (0.08), so the water and foam never touch the land shell
WATER_TOP, WATER_BOT, WATER_GAP = 1.0, 0.26, 0.09
FOAM_Z = (1.03, 1.11)         # a thin flat sheet; its walls stay planar quads (no needle triangles)
TILE = (-16.0, -13.0, 16.0, 13.0)
CHAMFER = ((11.0, -13.0), (16.0, -8.0))

# columns: name -> (centre x, y, footprint w (along the face) x d, yaw deg (the face normal is (-sin yaw, -cos yaw):
# 0 faces -Y, -45 faces the diagonal water), seed). Every top sits SEAT under the turf above it (grass_z), inside the
# slab's soil band (grass_z - 1.05 .. grass_z - 0.62), so the slab swallows the tops and only the bevel shows
FRONT_COLS = {
    "C0": ((-10.1, -7.0), 5.6, 4.2, 8.0, 32001),
    "C1": ((-4.2, -8.8), 6.7, 3.8, -10.0, 32002),
    "C1b": ((-2.4, -6.0), 3.4, 3.0, -25.0, 32008),
    "C2": ((-1.9, -3.2), 4.6, 4.0, -40.0, 32003),
    "C3a": ((0.93, -0.63), 4.6, 4.0, -45.0, 32004),
    "C3b": ((3.73, 1.37), 3.6, 3.4, -45.0, 32005),
    "C4": ((6.8, 3.0), 4.8, 4.0, -45.0, 32006),
    "C5": ((9.0, 4.6), 3.6, 3.2, -55.0, 32007),
    "C6": ((10.6, 6.2), 3.0, 2.8, -70.0, 32009),
}
BACK_COLS = {
    "CL": ((-12.6, -3.9), 2.6, 2.8, 90.0, 32011),
    "BK1": ((-11.68, -0.64), 3.6, 3.6, 148.0, 32012),
    "BK2": ((-8.93, 1.60), 4.8, 4.0, 136.0, 32013),
    "BK3": ((-5.78, 4.39), 5.0, 4.0, 131.0, 32014),
    "BK4": ((-1.95, 8.60), 5.6, 3.8, 145.0, 32015),
    "BK6": ((3.27, 10.79), 5.6, 3.6, 172.0, 32017),
    "BK7": ((7.98, 9.52), 4.2, 3.4, -155.0, 32018),
    "BK8": ((9.55, 9.08), 3.0, 2.8, -170.0, 32019),
}
# the ring round the ridge (front left to right, then the back right to left): the slab outline bridges each
# neighbour pair
COL_RING = ("C0", "C1", "C1b", "C2", "C3a", "C3b", "C4", "C5", "C6", "BK8", "BK7", "BK6", "BK4", "BK3", "BK2", "BK1",
            "CL")
# sides per column: 8 for the big ones (front), 7 for the big back ones, fewer for the small ones so every side face
# is at least 1.2 wide (decision summary)
COL_SIDES_OF = {"C1b": 6, "C3a": 7, "C3b": 7, "C5": 7, "C6": 6, "CL": 6, "BK8": 6}
SEAT = 0.76                 # column top under the turf (inside the soil band 0.62 .. 1.05)
RIM_IN = {"front": 0.6, "back": 0.45}   # the slab rim inside each column's top (shoulder) edge
COL_FOOT = -0.42            # every column from below the ground (the floor cut makes it flat)

# boulders: name -> (centre x, y, w, d, h, base z, yaw deg, seed, rings)
BIG = [(0.0, 0.94, 7), (0.32, 1.0, 7), (0.72, 0.82, 6), (1.0, 0.42, 4)]
DOME = [(0.0, 0.94, 6), (0.35, 1.0, 6), (0.75, 0.8, 5), (1.0, 0.4, 3)]
SQUAT = [(0.0, 0.95, 5), (0.42, 1.0, 5), (0.8, 0.7, 4), (1.0, 0.3, 2)]
PEB = [(0.0, 0.92, 5), (0.5, 1.0, 5), (1.0, 0.45, 3)]
BOULDERS = {
    "L1": ((-10.6, -8.4), 3.4, 3.0, 2.8, -0.2, 20.0, 32101, DOME),
    "W1": ((5.0, -10.4), 5.0, 4.5, 4.0, 0.0, 15.0, 32102, BIG),
    "W2": ((-4.4, -11.6), 2.6, 2.4, 2.2, -0.05, 40.0, 32103, DOME),
    "W3": ((0.6, -9.4), 2.2, 2.0, 1.9, 0.4, 70.0, 32104, SQUAT),
    "W4": ((8.8, -6.0), 1.8, 1.6, 1.6, 0.0, 10.0, 32105, SQUAT),
    "W5": ((9.4, -9.8), 0.9, 0.8, 0.8, 0.0, 30.0, 32106, PEB),
    "W6": ((10.6, 2.6), 3.6, 3.4, 3.2, -0.05, -20.0, 32107, DOME),
    "W7": ((12.9, 6.4), 1.8, 1.7, 1.6, -0.05, 50.0, 32108, SQUAT),
    "W8": ((14.4, 7.4), 1.6, 1.5, 1.4, 0.0, 80.0, 32109, SQUAT),
    "R1": ((0.0, -6.2), 1.3, 1.2, 1.0, 1.0, 0.0, 32110, SQUAT),
    "R2": ((3.0, -2.2), 1.8, 1.6, 1.4, 0.95, 60.0, 32111, SQUAT),
}
PEBBLES = [((-0.6, -7.4), 0.55), ((4.0, -1.4), 0.6), ((8.6, 3.0), 0.45)]
LAWN_ROCKS = [((-6.4, -2.4), 0.8), ((3.6, 10.2), 0.75), ((7.4, 6.0), 0.6)]
HOLES = {}                  # boulder name -> 2D hole polygon (its section below z 1.2, offset WATER_GAP)
IN_WATER = ("W1", "W2", "W4", "W5", "W6", "W7", "W8")

# low boxes: name -> (centre, w, d, top, yaw deg)
BOXES = {"B1": ((-14.4, -6.2), 2.3, 2.3, 2.4, 45.0), "B2": ((-7.6, -9.0), 3.2, 2.6, 2.4, 45.0)}

# vegetation: pines name -> (centre, height, scale, seed); bushes (centre, size, leaves, seed, on): on is None for
# the ridge (hero and the GrassTop part) or a name (the hero only: a column, a box, or "hero" to keep the GrassTop
# part under its 1000-tri budget). Spacing keeps every leaf clear of the other bushes and the pine tiers (a bush reaches about
# 0.93 x size; a pine tier 1.6 x scale): the vegetation shells never touch each other or the land
PINES = {"P1": ((-0.53, 5.63), 5.9, 1.1, 32201), "P2": ((-7.7, -4.2), 6.1, 1.2, 32202),
         "P3": ((-14.4, -6.2), 4.6, 0.55, 32203)}
BUSHES = [((-4.6, -6.4), 2.0, 6, 32301, None), ((-11.2, -3.2), 1.6, 6, 32302, None),
          ((-4.56, 2.98), 2.3, 7, 32303, None), ((6.3, 4.7), 2.0, 6, 32305, None),
          ((8.4, 6.9), 1.7, 6, 32306, None), ((2.0, 8.9), 2.4, 7, 32307, None), ((-7.6, -9.0), 1.8, 6, 32308, "B2"),
          ((-10.0, -5.0), 1.5, 5, 32309, "hero"), ((-3.6, 6.4), 1.6, 5, 32310, "hero"),
          # on the column tops along the rim, at the right end and at the cliff foot (on = the surface they stand on)
          ((-1.2, -4.0), 1.7, 5, 32321, "C2"), ((1.7, -1.4), 1.6, 5, 32322, "C3a"), ((7.6, 2.3), 1.7, 5, 32323, "C4"),
          ((10.9, 6.2), 1.6, 5, 32324, "C6"),
          # fix round 1: on the wider slab's front rim (C1) and its back edge (BK2, BK6/BK7)
          ((-6.2, -8.9), 1.8, 6, 32331, "hero"), ((-9.6, 0.6), 1.8, 6, 32332, "hero"),
          ((6.47, 10.18), 1.9, 6, 32333, "hero")]
DAISIES = [((-9.0, -2.4), 0.55), ((-6.0, -4.0), 0.6), ((-3.3, 3.9), 0.55)]
YELLOWS = [((-12.0, -4.8), None), ((-8.6, -5.0), None), ((-5.2, -1.6), None), ((1.62, 1.66), None), ((4.32, 4.04), None)]
# the sand path along the rim on the ridge (spec 1.3), a constrained region of the grass slab's top (widened by
# PATH_WIDEN; fix round 1 moved the plants that stood on the wider path just off it)
PATH = [(-3.6, -1.2), (-0.9, 1.35), (1.9, 3.35), (4.4, 5.85), (6.2, 7.6), (5.0, 8.9), (3.0, 7.2), (0.5, 4.5),
        (-2.3, 2.5), (-4.8, 0.0)]


# ---- columns -----------------------------------------------------------------------------------------------------------
COL_SIDES = 8
COL_EXP = 0.8            # superellipse exponent: < 1 pushes the octagon toward the footprint's rectangle
COL_BEVEL = (0.38, 0.42)  # the top chamfer: inset, drop


def col_spec(name):
    """(centre, w, d, yaw, seed, sides, row) of a column."""
    front = name in FRONT_COLS
    c, w, d, yaw, seed = (FRONT_COLS if front else BACK_COLS)[name]
    return c, w, d, yaw, seed, COL_SIDES_OF.get(name, COL_SIDES if front else 7), "front" if front else "back"


def column_pts(c, w, d, yaw, seed, z0=COL_FOOT, sides=COL_SIDES, seat=SEAT):
    """The points of one column: [foot ring, shoulder ring, top ring] (sides each). The top ring follows the turf
    above it (grass_z(p) - seat), so the slab swallows it wherever the ridge's height changes."""
    rng = random.Random(seed)
    yr = math.radians(yaw)
    u = Vector((math.cos(yr), -math.sin(yr)))
    n = Vector((-math.sin(yr), -math.cos(yr)))
    hw, hd = w / 2, d / 2
    ins, drop = COL_BEVEL
    ins = min(ins, 0.095 * min(w, d))       # small columns keep a flat top of at least 60 % (spec 9.2)
    ph = rng.uniform(-0.08, 0.08)
    lean = Vector((rng.uniform(-0.12, 0.12), rng.uniform(-0.1, 0.1)))
    ztop = grass_z(c) - seat
    h = ztop - z0

    def ring(sx, sy, j):
        out = []
        for k in range(sides):
            ang = 2 * math.pi * (k + 0.5) / sides + ph + rng.uniform(-0.06, 0.06)
            cx, cy = math.cos(ang), math.sin(ang)
            out.append((math.copysign(abs(cx) ** COL_EXP, cx) * sx * (1 + rng.uniform(-j, j)),
                        math.copysign(abs(cy) ** COL_EXP, cy) * sy * (1 + rng.uniform(-j, j))))
        return out

    def P(lu, lv, z):
        t = (z - z0) / h
        q = Vector(c) + u * (lu + lean.x * t) + n * (lv + lean.y * t)
        return Vector((q.x, q.y, z))

    def zt(lu, lv):
        return grass_z(P(lu, lv, ztop)) - seat
    pts = []
    # a slight taper (foot 1.04, shoulder 0.96): each side is one big flat facet from the foot to the shoulder (two
    # triangles), then the chamfer, then the flat top
    twist = rng.uniform(-0.12, 0.12)
    for top, sc, j, tw, zj in ((False, 1.04, 0.03, 0.0, 0.0), (True, 0.96, 0.03, twist, 0.35)):
        for lu, lv in ring(hw * sc, hd * sc, j):
            cu, su = math.cos(tw), math.sin(tw)
            lu2, lv2 = lu * cu - lv * su, lu * su + lv * cu
            z = zt(lu2, lv2) - drop if top else z0
            pts.append(P(lu2, lv2, z + rng.uniform(-zj, zj)))
    for lu, lv in ring(hw * 0.97 - ins, hd * 0.97 - ins, 0.02):
        pts.append(P(lu, lv, zt(lu, lv) + rng.uniform(-0.03, 0.03)))
    return pts


def column(a, name, z0=COL_FOOT):
    """One fat flat-faced cliff column: the convex hull of superellipse rings (foot, shoulder) and a flat top ring
    inset by the bevel. Big side faces (two triangles each), one chamfer ring, a flat top. Returns verts."""
    c, w, d, yaw, seed, sides, _row = col_spec(name)
    pts = column_pts(c, w, d, yaw, seed, z0=z0, sides=sides)
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    for v in vs:
        if v.is_valid and not v.link_faces:
            bm.verts.remove(v)
    vs = [v for v in vs if v.is_valid]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    _tri(bm, _faces(vs))
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, ROCK, tint=1.0)
    return vs


def _col_hull(name, ring=1, z0=COL_FOOT):
    """The 2D hull of one of a column's rings (0 foot, 1 shoulder, 2 top), CCW."""
    c, w, d, yaw, seed, sides, _row = col_spec(name)
    pts = column_pts(c, w, d, yaw, seed, z0=z0, sides=sides)
    return _hull2([(p.x, p.y) for p in pts[ring * sides:(ring + 1) * sides]])


def _area2(P):
    return 0.5 * sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P)))


def _rdp(P, tol):
    if len(P) < 3:
        return list(P)
    dmax, idx = max((_seg_d(P[i], P[0], P[-1]), i) for i in range(1, len(P) - 1))
    if dmax > tol:
        return _rdp(P[:idx + 1], tol)[:-1] + _rdp(P[idx:], tol)
    return [P[0], P[-1]]


def _rdp_closed(P, tol):
    i0 = max(range(len(P)), key=lambda i: P[i].x)
    P = P[i0:] + P[:i0]
    i1 = max(range(len(P)), key=lambda i: (P[i] - P[0]).length)
    return _rdp(P[:i1 + 1], tol)[:-1] + _rdp(P[i1:] + [P[0]], tol)[:-1]


def _union_outline(pos):
    """The outer boundary (CCW) of the union of 2D polygons, from their constrained triangulation."""
    co, tris = cdt_region(pos, tidy=False)
    directed = {}
    for t in tris:
        for k in range(3):
            directed[(t[k], t[(k + 1) % 3])] = True
    nxt = {}
    for (i, j) in directed:
        if (j, i) not in directed:
            nxt.setdefault(i, []).append(j)
    used = set()
    loops = []

    def turn(p, v, q):
        # the left-turn angle at v from p -> v to v -> q (a pinch point: take the rightmost turn, which keeps
        # touching loops apart)
        a_ = co[v] - co[p]
        b_ = co[q] - co[v]
        return math.atan2(a_.x * b_.y - a_.y * b_.x, a_.dot(b_))
    for s in list(nxt):
        for t0 in nxt[s]:
            if (s, t0) in used:
                continue
            loop, p, v = [s], s, t0
            used.add((s, t0))
            while v != s and len(loop) < 100000:
                loop.append(v)
                cand = [q for q in nxt.get(v, []) if (v, q) not in used]
                if not cand:
                    break
                q = min(cand, key=lambda q: turn(p, v, q))
                used.add((v, q))
                p, v = v, q
            loops.append([Vector(co[i]) for i in loop])
    return max(loops, key=lambda L: _area2(L))


def ridge_outline(tol=0.08):
    """RIDGE: the outer hull of the column tops round the ridge. The union of every column's top (shoulder) outline
    inset by RIM_IN, the hull of each neighbour pair (bridging the creases between columns) and the polygon through
    the column centres (the inside), simplified. The rim then runs RIM_IN inside every column's top edge."""
    if RIDGE:
        return RIDGE
    ins = {nm: _offset_poly(_col_hull(nm), -RIM_IN[col_spec(nm)[6]]) for nm in COL_RING}
    pos = list(ins.values())
    n_ = len(COL_RING)
    pos += [_hull2(ins[COL_RING[i]] + ins[COL_RING[(i + 1) % n_]]) for i in range(n_)]
    cen = [Vector(col_spec(nm)[0]) for nm in COL_RING]
    pos.append(cen if _area2(cen) > 0 else list(reversed(cen)))
    out = _rdp_closed(_union_outline(pos), tol)
    # no edge under 0.35 (thin wall quads): merge the closest neighbours
    while len(out) > 4:
        el = [(out[(i + 1) % len(out)] - out[i]).length for i in range(len(out))]
        i = min(range(len(out)), key=lambda k: el[k])
        if el[i] >= 0.35:
            break
        j = (i + 1) % len(out)
        out[i] = (out[i] + out[j]) / 2
        out.pop(j)
    # long straight runs (the bridged diagonal) get points every RIDGE_STEP so the top triangulates without needles
    RIDGE[:] = _resample_poly(out, RIDGE_STEP)
    return RIDGE


def col_gaps():
    """The smallest 2D gap between each ring neighbour pair's shoulder outlines (negative: overlap is not measured,
    0)."""
    out = {}
    n_ = len(COL_RING)
    for i in range(n_):
        a_, b_ = COL_RING[i], COL_RING[(i + 1) % n_]
        A, B = _col_hull(a_), _col_hull(b_)
        if any(_inside(p, B) for p in A) or any(_inside(p, A) for p in B):
            out[a_ + "-" + b_] = 0.0
            continue
        d = min(min(_seg_d(p, B[k], B[(k + 1) % len(B)]) for k in range(len(B))) for p in A)
        d = min(d, min(min(_seg_d(p, A[k], A[(k + 1) % len(A)]) for k in range(len(A))) for p in B))
        out[a_ + "-" + b_] = round(d, 2)
    return out


def _paint_column(a, vs, seed, beach_z=1.8):
    """Rock with a per-column Tint; the foot band (within 0.5 above the beach) 25 % toward the dark soil (contact);
    nothing by facing."""
    tint = random.Random(seed).uniform(0.95, 1.05)
    k_foot = _mix(ROCK, SOIL_DARK, 0.25)
    for f in _faces(vs):
        c = f.calc_center_median()
        f.material_index = a._mi(k_foot if c.z < beach_z + 0.4 else ROCK)
    _mottle(a, _faces(vs), 0.04, 0.5, seed, tint=tint)


# ---- boulders --------------------------------------------------------------------------------------------------------------
def boulder(a, name, at_origin=False):
    (cx, cy), w, d, h, z0, yaw, seed, rings = BOULDERS[name]
    if at_origin:
        cx, cy, z0 = 0.0, 0.0, 0.0
    vs = K.hull_rock(a, (w, d, h), loc=(cx, cy, z0), seed=seed, mat=ROCK, rings=rings, jitter=0.08,
                     rot=math.radians(yaw), keep_bottom=True)
    bmesh.ops.dissolve_limit(a.bm, angle_limit=math.radians(5.0), verts=vs,
                             edges=list({e for f in _faces(vs) for e in f.edges}))
    vs = [v for v in vs if v.is_valid]
    _tri(a.bm, _faces(vs))
    bmesh.ops.recalc_face_normals(a.bm, faces=_faces(vs))
    if not at_origin:
        HOLES[name] = _hole_of(vs)
    return vs


def _hole_of(vs, zcut=1.2, margin=WATER_GAP):
    """The 2D hole a boulder makes in the water and foam: the convex hull of its section below zcut (verts below
    and edge crossings at zcut), at most 9 corners, offset by margin."""
    pts = [v.co.copy() for v in vs if v.co.z <= zcut]
    for e in {e for v in vs for e in v.link_edges}:
        p, q = e.verts[0].co, e.verts[1].co
        if (p.z - zcut) * (q.z - zcut) < 0:
            t = (zcut - p.z) / (q.z - p.z)
            pts.append(p + (q - p) * t)
    hull = _hull2([(p.x, p.y) for p in pts])
    simp = _simplify_convex(hull, 9)
    # no short edges (needles in the water's triangulation): drop the corner with the shortest edge until every edge
    # is at least 0.6 (or five corners remain)
    while len(simp) > 5:
        el = [(simp[(i + 1) % len(simp)] - simp[i]).length for i in range(len(simp))]
        i = min(range(len(simp)), key=lambda k: el[k])
        if el[i] >= 0.6:
            break
        simp.pop((i + 1) % len(simp) if el[i - 1] > el[(i + 1) % len(simp)] else i)
    # the simplified polygon can cut inside the hull by the dropped corners' depth: offset by that plus margin
    loss = max(min(_seg_d(q, simp[i], simp[(i + 1) % len(simp)]) for i in range(len(simp))) if not any(
        (q - s).length < 1e-6 for s in simp) else 0.0 for q in hull)
    return _offset_poly(simp, margin + loss)


def _paint_boulder(a, vs, seed, wet=False):
    """Rock with a per-boulder Tint; a boulder standing in the water takes the bed colour below the waterline (a
    hard edge, submerged: W03's submerge)."""
    tint = random.Random(seed).uniform(0.94, 1.06)
    for f in _faces(vs):
        c = f.calc_center_median()
        f.material_index = a._mi(BED if (wet and c.z < WATER_TOP - 0.02) else ROCK)
    _mottle(a, _faces(vs), 0.04, 0.6, seed, tint=tint)


def boulders(a):
    out = {}
    for name in BOULDERS:
        vs = boulder(a, name)
        _paint_boulder(a, vs, BOULDERS[name][6], wet=name in IN_WATER)
        out[name] = vs
    return out


def _pebble(a, size, loc, seed):
    """A small faceted stone, closed (keep_bottom: K.pebble leaves its bottom open)."""
    vs = K.hull_rock(a, size, loc=loc, seed=seed, mat=ROCK, rings=PEB, jitter=0.12,
                     rot=random.Random(seed).uniform(0, 6.28), keep_bottom=True)
    bmesh.ops.recalc_face_normals(a.bm, faces=_faces(vs))
    return vs


def pebbles(a, beach_z):
    for i, ((x, y), s) in enumerate(PEBBLES):
        z = beach_z((x, y)) - 0.15
        vs = _pebble(a, (s, s * 0.85, s * 0.55), (x, y, z), 32401 + i)
        _tri(a.bm, _faces(vs))
        _mottle(a, _faces(vs), 0.03, 0.8, 32401 + i, tint=random.Random(i).uniform(0.95, 1.05))


# ---- ridge core, grass slab, beach, bed ------------------------------------------------------------------------------
def ridge_core(a):
    """The ridge's solid core (hidden inside the column rows; its walls show only as the dark crease floors between
    columns): the ridge outline inset, from below the ground up into the grass slab."""
    poly = core_poly()
    keep = [poly[0]]
    for p in poly[1:]:
        if (p - keep[-1]).length >= 1.6:
            keep.append(p)
    if (keep[-1] - keep[0]).length < 1.6:
        keep.pop()
    co, tris = cdt_region([keep], tidy=False)
    tf, wf, bf, vs = slab(a, co, tris, lambda p: grass_z(p) - GRASS_THICK + 0.3, lambda p: -0.45,
                          _mix(ROCK, SOIL_DARK, 0.25))
    return vs


def core_poly():
    """The ridge core's outline: the polygon through the column centres, offset CORE_OUT outward (it fills the
    inside of the ridge and closes the creases between columns well behind their faces)."""
    cen = [Vector(col_spec(nm)[0]) for nm in COL_RING]
    if _area2(cen) < 0:
        cen.reverse()
    out = _offset_poly(cen, CORE_OUT)
    ridge = ridge_outline()
    # at the ridge's ends the mitred offset pokes out past the rim: pull those corners back toward their column
    for i, (p, q) in enumerate(zip(cen, out)):
        t = 1.0
        while t > 0 and not (_inside(q, ridge) and _dist_line(q, ridge, True) >= 0.5):
            t -= 0.1
            q = p.lerp(out[i], max(0.0, t))
        out[i] = q
    return out


def _path_poly():
    # fix round 1: PATH_WIDEN wider each side (the sheet's path is a broad sand band along the ridge)
    return _offset_poly([Vector(p) for p in PATH], PATH_WIDEN)


PATH_WIDEN = 0.45


def grass_slab(a, with_path=True):
    """The ridge's grass top: a thick slab over the ridge outline (turf over a soil band), the sand path along the
    rim as its own constrained region of the top. Returns (top faces, verts)."""
    path = _path_poly()
    ridge = ridge_outline()
    pos = [ridge]
    st = _steiner(pos, [path] if with_path else [], SLAB_STEINER, 1.3, 32502)
    if with_path:
        co, tris = cdt_region([ridge, path], [], st, tidy=False)
    else:
        co, tris = cdt_region([ridge], [], st, tidy=False)
    rng = random.Random(32503)
    jit = {}

    def zt(p):
        k = (round(p.x, 3), round(p.y, 3))
        if k not in jit:
            jit[k] = rng.uniform(-0.05, 0.05)
        return grass_z(p) + jit[k]
    tf, wf, bf, vs = slab(a, co, tris, zt, lambda p: grass_z(p) - GRASS_THICK, GRASS, bands=(TURF,))
    # paint: the top lawn (broad patches toward the bush green), the path sand, the side band turf over soil, the
    # hidden bottom soil
    nf = K.noise_field(scale=0.18, seed=32504)
    lawn_mix = _mix(GRASS, LEAF, 0.25)
    for f in tf:
        c = f.calc_center_median()
        if with_path and _inside(c, path):
            f.material_index = a._mi(SAND)
        else:
            f.material_index = a._mi(lawn_mix if nf(c) > 0.28 else GRASS)
    for f in wf:
        c = f.calc_center_median()
        f.material_index = a._mi(GRASS if c.z > grass_z(c) - TURF + 0.02 else SOIL)
    _paint(a, bf, SOIL)
    _mottle(a, tf, 0.04, 0.5, 32505)
    return tf, vs


def beach_poly():
    wl = _catmull(WATERLINE, WL_STEP)
    return wl, wl + [Vector(p) for p in BEACH_IN]


def beach_z(p, wl=None):
    wl = wl or _catmull(WATERLINE, WL_STEP)
    d = _dist_line(p, wl)
    t = min(1.0, d / BEACH_SLOPE)
    t = t * t * (3 - 2 * t)
    return WATER_TOP + (BEACH_TOP - WATER_TOP) * t


def beach(a):
    """The beach slab between the waterline (z 1.0) and the cliff foot (1.8), down to below the ground. Paint: sand,
    the open flat beach 50 % toward the light sand, a darker contact band at the column feet; the seaward wall
    (under the water) the bed colour."""
    wl, poly = beach_poly()
    st = _steiner([poly], [], 3.2, 1.0, 32601)
    co, tris = cdt_region([poly], [], st)
    tf, wf, bf, vs = slab(a, co, tris, lambda p: beach_z(p, wl), lambda p: -0.35, SAND)
    feet = [Vector(p) for p in BEACH_IN]
    k_light = [_mix(SAND, SAND_LIGHT, t) for t in (0.0, 0.25, 0.5)]
    k_contact = _mix(SAND, SOIL_DARK, 0.25)
    for f in tf:
        c = f.calc_center_median()
        dw = _dist_line(c, wl)
        df = _dist_line(c, feet)
        if df < 1.2:
            f.material_index = a._mi(k_contact)
        elif df < 1.5 or dw < 0.5:
            # the step between the contact band (or the wet edge) and the open beach
            f.material_index = a._mi(k_light[1])
        else:
            # the open beach (fix round 1: 50 % light sand; the sheet's lit beach is #FCE59E)
            f.material_index = a._mi(k_light[2])
    for f in wf:
        c = f.calc_center_median()
        near_water = _dist_line(c, wl) < 0.05
        f.material_index = a._mi(BED if near_water else SOIL)
    _paint(a, bf, SOIL_DARK)
    _mottle(a, tf, 0.03, 0.6, 32602)
    return vs


def water_outline(off, step=WL_STEP):
    """The water's outline (CCW): the front edge from the waterline's start, the chamfer, the right edge up to the
    back cut, the back cut, then the waterline back to the front, offset seaward by off."""
    wl = _offset_line(_catmull(WATERLINE, step), off)
    x0, y0, x1, y1 = TILE
    for p in wl:
        p.x = min(x1, max(x0, p.x))
        p.y = min(y1, max(y0, p.y))
    out = [Vector((wl[0].x, y0)), Vector(CHAMFER[0]), Vector(CHAMFER[1])] + [Vector(p) for p in WATER_BACK]
    return out + [p for p in reversed(wl[1:])]


def bed(a):
    """The water's bed: a thin slab under the water outline, its shore edge 0.7 inland (under the beach)."""
    poly = _resample_poly(water_outline(-0.7, step=3.0), 4.0)
    co, tris = cdt_region([poly], [], _steiner([poly], [], 4.5, 2.0, 32701))
    tf, wf, bf, vs = slab(a, co, tris, lambda p: BED_TOP, lambda p: -0.3, BED)
    return vs


# ---- low boxes ---------------------------------------------------------------------------------------------------------
def low_box(a, name):
    """A low blocky box with tan sides and a grass cap slab overhanging a little (the turf lip)."""
    (cx, cy), w, d, top, yaw = BOXES[name]
    rot = (0, 0, math.radians(yaw))
    v1 = a.box((w, d, top - 0.05 + 0.25), loc=(cx, cy, -0.25), rot=rot, mat=SOIL, base=True)
    _tri(a.bm, _faces(v1))
    v2 = a.box((w + 0.24, d + 0.24, 0.42), loc=(cx, cy, top - 0.32), rot=rot, mat=GRASS, base=True)
    _tri(a.bm, _faces(v2))
    _mottle(a, _faces(v1), 0.04, 0.6, 32801)
    _mottle(a, _faces(v2), 0.04, 0.6, 32802)
    return v1 + v2


# ---- vegetation ------------------------------------------------------------------------------------------------------------
def _star_tier(a, c, z, r, h, pts, rot, rng, mat, top=None):
    """One pine tier: a star outline (pts drooping points) rising to an apex at z + h, or, with top = (z_top, r_top),
    to a small flat cap there (a frustum that stops just under the next tier's skirt); closed underneath by a fan to
    a centre point raised 0.1 h."""
    bm = a.bm
    ring = []
    for k in range(2 * pts):
        ang = rot + math.pi * k / pts
        rr = r * (1.0 if k % 2 == 0 else 0.66) * rng.uniform(0.94, 1.06)
        dz = -0.3 * r * (1.0 if k % 2 == 0 else 0.25)
        ring.append(bm.verts.new((c[0] + math.cos(ang) * rr, c[1] + math.sin(ang) * rr, z + dz)))
    cen = bm.verts.new((c[0], c[1], z + h * 0.1))
    m = len(ring)
    if top is None:
        apex = bm.verts.new((c[0], c[1], z + h))
        for k in range(m):
            bm.faces.new((ring[k], ring[(k + 1) % m], apex))
        cap = [apex]
    else:
        zt, rt = top
        cap = [bm.verts.new((c[0] + math.cos(rot + 2 * math.pi * k / pts) * rt,
                             c[1] + math.sin(rot + 2 * math.pi * k / pts) * rt, zt)) for k in range(pts)]
        for k in range(pts):
            p0, p1, p2 = ring[2 * k], ring[2 * k + 1], ring[(2 * k + 2) % m]
            bm.faces.new((p0, p1, cap[k]))
            bm.faces.new((p1, cap[(k + 1) % pts], cap[k]))
            bm.faces.new((p1, p2, cap[(k + 1) % pts]))
        bm.faces.new(cap)
    for k in range(m):
        bm.faces.new((ring[(k + 1) % m], ring[k], cen))
    vs = ring + [cen] + cap
    _tri(bm, _faces(vs))
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, mat, tint=rng.uniform(0.95, 1.05))
    return vs


VEG_GAP = 0.05             # vegetation stands this far above the finished land surface (separate shells, decision 9)


def _ground_max(ground, pts):
    """The highest land surface under a set of 2D points, or None if any point misses the land."""
    zs = [ground(p) for p in pts]
    if any(z is None for z in zs):
        return None
    return max(zs)


def pine(a, name, ground):
    """A small pine: a 5-sided trunk and three drooping star tiers, each its own closed shell and none touching
    another: the trunk stops under the first tier's skirt, the lower tiers are frustums whose flat caps stop just
    under the next tier's skirt (which hides them). No union, no needles."""
    (x, y), height, s, seed = PINES[name]
    rng = random.Random(seed)
    rt = 0.32 * s
    foot = [(x + math.cos(k * 1.2566) * rt, y + math.sin(k * 1.2566) * rt) for k in range(5)] + [(x, y)]
    z = _ground_max(ground, foot)
    z = (z if z is not None else grass_z((x, y))) + 0.03
    # four tiers (fix round 1: wider and fuller crowns, the sheet's pines read 4 % of the f34 cell)
    rs = PINE_TIERS
    nt = len(rs)
    tier_h = height / 3.2
    zs = [z + 1.1 * s + k * height * 0.18 for k in range(nt)]
    vs = a.cyl(rt, 0.24 * s, zs[0] - z, sides=5, loc=(x, y, z), mat=BARK)
    _tri(a.bm, _faces(vs))
    for k in range(nt):
        rot = rng.uniform(0, 6.3)
        h = tier_h if k < nt - 1 else height - (zs[k] - z)
        top = None if k == nt - 1 else (zs[k + 1] + 0.02, 0.22 * s)
        vs += _star_tier(a, (x, y), zs[k], rs[k] * s, h, 5, rot, rng, PINE, top=top)
    return vs


PINE_TIERS = (1.8, 1.46, 1.1, 0.74)


class _Guard:
    """Keeps every vegetation shell clear of the land (and the pines) and of the vegetation already placed: a piece is
    only emitted if its triangles overlap none of them (so the hero has no self-intersections)."""

    def __init__(self, o=None):
        self.land = None
        if o is not None:
            off = Vector(o[OFF])
            me = o.data
            self.land = BVHTree.FromPolygons([v.co + off for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
        self.pts, self.faces, self.tree = [], [], None
        self.dropped = 0

    def ok(self, pts, faces):
        t = BVHTree.FromPolygons(pts, faces)
        if self.land is not None and t.overlap(self.land):
            return False
        return not (self.tree is not None and t.overlap(self.tree))

    def add(self, pts, faces):
        n = len(self.pts)
        self.pts += [Vector(p) for p in pts]
        self.faces += [tuple(i + n for i in f) for f in faces]
        self.tree = BVHTree.FromPolygons(self.pts, self.faces)


def _emit(a, pts, faces, mat):
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    for f in faces:
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, mat)
    return vs


def _leaf_geo(base, yaw, pitch, L, W, curl=0.22, thick=0.05):
    """A broad pointed leaf: a 4-point outline, its top folded along the midrib, its back a fan to one point (6 tris,
    closed)."""
    rot = Matrix.Rotation(yaw, 3, "Z") @ Matrix.Rotation(-pitch, 3, "Y")
    B = Vector(base)

    def P(x, y_, z):
        t = x / L
        return B + rot @ Vector((x, y_, z - curl * L * t * t))
    # the top folds along the midrib (the outline's sides lifted a little), the back is a shallow fan to one point
    pts = [P(0, 0, 0), P(0.42 * L, -W / 2, 0.08 * W), P(L, 0, 0), P(0.42 * L, W / 2, 0.08 * W),
           P(0.45 * L, 0, -thick)]
    faces = [(0, 1, 2), (0, 2, 3)] + [(4, (i + 1) % 4, i) for i in range(4)]
    return pts, faces


def _place(a, guard, tries, mat):
    """Emit the first candidate (pts, faces) the guard accepts; returns its verts or [] (dropped)."""
    for pts, faces in tries:
        if guard is None or guard.ok(pts, faces):
            if guard is not None:
                guard.add(pts, faces)
            return _emit(a, pts, faces, mat)
    if guard is not None:
        guard.dropped += 1
    return []


def bush(a, c, size, n, seed, ground, guard=None):
    """A fan bush: n broad pointed leaves rising from round a hub, each its own closed shell standing just above the
    ground, steep in the middle, wider outside (spec 2.4). A leaf that would touch the land or another plant is
    tried shorter and steeper, then left out."""
    rng = random.Random(seed)
    vs = []
    y0 = rng.uniform(0, 6.3)
    for k in range(n):
        yaw = y0 + 2 * math.pi * k / n + rng.uniform(-0.08, 0.08)
        L0 = size * rng.uniform(0.85, 1.1)
        pitch0 = rng.uniform(0.8, 1.2)
        tries = []
        for L, pitch in ((L0, pitch0), (L0 * 0.8, pitch0 + 0.2), (L0 * 0.62, pitch0 + 0.35)):
            W = L * 0.44
            off = 0.3 * size
            bx, by = c[0] + math.cos(yaw) * off, c[1] + math.sin(yaw) * off
            cy, sy = math.cos(yaw), math.sin(yaw)
            foot = [(bx, by)] + [(bx + cy * L * f - sy * w, by + sy * L * f + cy * w) for f in (0.2, 0.42)
                                 for w in (-W / 2, W / 2)]
            z = _ground_max(ground, foot)
            if z is not None:
                tries.append(_leaf_geo((bx, by, z + VEG_GAP), yaw, pitch, L, W))
        vs += _place(a, guard, tries, LEAF)
    return vs


def _daisy_geo(c, r, ph, rng, ground):
    pts2 = []
    for k in range(10):
        ang = ph + math.pi * k / 5
        rr = r * (1.0 if k % 2 == 0 else 0.42)
        pts2.append((c[0] + math.cos(ang) * rr, c[1] + math.sin(ang) * rr))
    z = _ground_max(ground, pts2 + [tuple(c)])
    if z is None:
        return None, None, None
    z += VEG_GAP
    pts = [Vector((x, y, z + rng.uniform(0.0, 0.03))) for x, y in pts2] + [Vector((c[0], c[1], z + 0.12)),
                                                                          Vector((c[0], c[1], z))]
    faces = []
    for k in range(10):
        j = (k + 1) % 10
        faces += [(10, k, j), (11, j, k)]
    return pts, faces, z


def _pyramid_geo(base, r, h, rot):
    pts = [Vector((base[0] + math.cos(rot + k * math.pi / 2) * r, base[1] + math.sin(rot + k * math.pi / 2) * r,
                   base[2])) for k in range(4)] + [Vector((base[0], base[1], base[2] + h))]
    faces = [(k, (k + 1) % 4, 4) for k in range(4)] + [(0, 3, 2), (0, 2, 1)]
    return pts, faces


def daisy(a, c, r, seed, ground, guard=None):
    """A flat white five-petal daisy: a star lens (a raised centre, a flat underside) standing just above the grass,
    with a separate small yellow pyramid centre just above its peak."""
    rng = random.Random(seed)
    ph = rng.uniform(0, 6.3)
    for rr in (r, r * 0.75):
        pts, faces, z = _daisy_geo(c, rr, ph, rng, ground)
        if pts is None:
            continue
        cpts, cfaces = _pyramid_geo((c[0], c[1], z + 0.13), rr * 0.3, 0.12, ph)
        if guard is None or (guard.ok(pts, faces) and guard.ok(cpts, cfaces)):
            if guard is not None:
                guard.add(pts, faces)
                guard.add(cpts, cfaces)
            return _emit(a, pts, faces, PETAL) + _emit(a, cpts, cfaces, POLLEN)
    if guard is not None:
        guard.dropped += 1
    return []


def _pyramid(a, base, r, h, mat, rot):
    pts, faces = _pyramid_geo(base, r, h, rot)
    return _emit(a, pts, faces, mat)


def yellow_flower(a, c, seed, ground, guard=None):
    rng = random.Random(seed)
    rot = rng.uniform(0, 1.5)
    foot = [(c[0] + math.cos(rot + k * 1.571) * 0.2, c[1] + math.sin(rot + k * 1.571) * 0.2) for k in range(4)]
    z = _ground_max(ground, foot + [tuple(c)])
    if z is None:
        return []
    return _place(a, guard, [_pyramid_geo((c[0], c[1], z + VEG_GAP), 0.2, 0.3, rot)], POLLEN)


def lawn_rocks(a):
    for i, ((x, y), s) in enumerate(LAWN_ROCKS):
        vs = _pebble(a, (s, s * 0.85, s * 0.6), (x, y, grass_z((x, y)) - 0.12), 32451 + i)
        _tri(a.bm, _faces(vs))
        _mottle(a, _faces(vs), 0.03, 0.8, 32451 + i, tint=1.04)


def vegetation(a, ground, ridge_only=False, guard=None):
    """Every leaf, flower and flower centre as its own closed shell set just above the finished land (ground(xy) ->
    the top surface's z), kept clear of everything else by the guard. The pines are built first (pine())."""
    for c, size, n, seed, on in BUSHES:
        if on is None or not ridge_only:
            bush(a, c, size, n, seed, ground, guard)
    for i, (c, r) in enumerate(DAISIES):
        daisy(a, c, r, 32901 + i, ground, guard)
    for i, (c, on) in enumerate(YELLOWS):
        if on is None or not ridge_only:
            yellow_flower(a, c, 32951 + i, ground, guard)


def ground_of(o):
    """ground(xy) -> the top surface z of o's mesh in the build frame (o[OFF] is the build point at o's origin)."""
    off = Vector(o[OFF])
    me = o.data
    tree = BVHTree.FromPolygons([v.co + off for v in me.vertices], [tuple(p.vertices) for p in me.polygons])

    def ground(p):
        h = tree.ray_cast(Vector((p[0], p[1], 80.0)), Vector((0, 0, -1)), 200)
        return h[0].z if h[0] is not None else None
    return ground


# ---- water and foam --------------------------------------------------------------------------------------------------------
def holes():
    """The boulder holes (computed once from a throwaway build of the boulders)."""
    if not HOLES:
        a = K.fk().Asset("_m032_probe", "probe")
        for name in BOULDERS:
            boulder(a, name)
        a.bm.free()
    return HOLES


def _water_holes(poly):
    out = []
    for name, hp in holes().items():
        if any(_inside(p, poly) for p in hp) or any(_inside(p, hp) for p in poly):
            out.append(hp)
    return out


def water(a):
    """The water slab: top z 1.0, bottom 0.26 (0.06 over the bed), its shore edge WATER_GAP seaward of the beach's
    waterline wall, cut round every boulder by its hole. Flat top: no shallow band, no ripple geometry (spec 6)."""
    poly = _resample_poly(water_outline(WATER_GAP), 2.6)
    neg = _water_holes(poly)
    st = _steiner([poly], neg, 4.2, 1.6, 33001)
    co, tris = cdt_region([poly], neg, st, min_island=1.0)
    tf, wf, bf, vs = slab(a, co, tris, lambda p: WATER_TOP, lambda p: WATER_BOT, WATER, quad_walls=True)
    return vs


def _resample_poly(poly, maxlen):
    """A closed polygon with extra points so no edge is longer than maxlen."""
    out = []
    P = [_v2(p) for p in poly]
    for i, p in enumerate(P):
        q = P[(i + 1) % len(P)]
        n = max(1, int(math.ceil((q - p).length / maxlen)))
        out += [p.lerp(q, k / n) for k in range(n)]
    return out


def _blob(c, r, n, rot, sq=1.0):
    return [Vector((c[0] + math.cos(rot + 2 * math.pi * k / n) * r, c[1] + math.sin(rot + 2 * math.pi * k / n) * r * sq))
            for k in range(n)]


FOAM_WIDTH = (0.75, 1.55)
FOAM_HOLES = 0.42           # the ribbon's round holes (diameter)
FOAM_RINGS = {"W1": 0.6, "W4": 0.45}
FOAM_BLOBS = [((7.6, -11.4), 0.42), ((2.2, -12.2), 0.4), ((12.6, -5.0), 0.42), ((10.2, -9.8), 0.45)]


def foam_regions():
    """(pos, neg) 2D polygons of the foam: the shore ribbon (a wavy band seaward of the waterline, 0.75-1.55 wide),
    a ring round each boulder standing clear in the water, a few loose blobs; holes: the ribbon's round holes and the
    boulder holes."""
    wl = _offset_line(_catmull(WATERLINE, 1.9), WATER_GAP + 0.08)   # the tidy's merge moves points <= 0.1
    # end the ribbon's shore edge where it meets the water's back cut (clamping it there instead slid it onto the
    # beach: 0.019 clearance in round 1)
    ymax = WATER_BACK[0][1] - 0.15
    for i in range(1, len(wl)):
        if wl[i].y > ymax >= wl[i - 1].y:
            t = (ymax - wl[i - 1].y) / (wl[i].y - wl[i - 1].y)
            wl = wl[:i] + [wl[i - 1].lerp(wl[i], t)]
            break
    rng = random.Random(33101)
    widths = []
    for i, p in enumerate(wl):
        w = FOAM_WIDTH[0] + (FOAM_WIDTH[1] - FOAM_WIDTH[0]) * (0.5 + 0.5 * math.sin(i * 1.3 + 0.7))
        widths.append(w * rng.uniform(0.92, 1.08))
    outer = []
    P = [_v2(p) for p in wl]
    for i, p in enumerate(P):
        t = (P[min(len(P) - 1, i + 1)] - P[max(0, i - 1)]).normalized()
        outer.append(p + Vector((t.y, -t.x)) * widths[i])
    x0, y0, x1, y1 = TILE
    for p in outer + P:
        p.x = min(x1 - 0.02, max(x0, p.x))
        p.y = min(WATER_BACK[0][1] - 0.15, max(y0 + 0.02, p.y))
    ribbon = P + list(reversed(outer))
    # ribbon is CW (P runs front -> back, the seaward side to its right): make it CCW
    if sum((ribbon[i].x * ribbon[(i + 1) % len(ribbon)].y - ribbon[(i + 1) % len(ribbon)].x * ribbon[i].y)
           for i in range(len(ribbon))) < 0:
        ribbon = list(reversed(ribbon))
    pos = [ribbon]
    neg = []
    # round holes along the ribbon's middle, every third or fourth sample
    for i in range(2, len(P) - 2, 5):
        c = (P[i] + outer[i]) / 2 + (outer[i] - P[i]).normalized() * rng.uniform(-0.1, 0.1)
        if widths[i] > 0.95:
            neg.append(_blob(c, FOAM_HOLES / 2 * rng.uniform(0.85, 1.2), 4, rng.uniform(0, 6.3), 0.8))
    hs = holes()
    for name, w in FOAM_RINGS.items():
        pos.append(_offset_poly(hs[name], w))
    for c, r in FOAM_BLOBS:
        pos.append(_blob(c, r, 4, rng.uniform(0, 6.3), 0.75))
    for name, hp in hs.items():
        neg.append(hp)
    return pos, neg


def foam(a):
    pos, neg = foam_regions()
    co, tris = cdt_region(pos, neg, min_island=0.25, merge=0.2)
    tf, wf, bf, vs = slab(a, co, tris, lambda p: FOAM_Z[1], lambda p: FOAM_Z[0], FOAM, quad_walls=True)
    return vs


# ---- parts -------------------------------------------------------------------------------------------------------------------
def grass_top_part(a):
    """The Grass Top (vegetation cluster): the ridge's grass slab and lawn rocks (its pines, bushes and flowers are
    joined after the cleanup, set on the finished slab: _add_vegetation)."""
    grass_slab(a)
    lawn_rocks(a)


def sand_strip_part(a):
    beach(a)


def rock_slope_part(a):
    for name in FRONT_COLS:
        vs = column(a, name)
        _paint_column(a, vs, col_spec(name)[4])
    for name in ("L1", "W2", "W3"):
        vs = boulder(a, name)
        _paint_boulder(a, vs, BOULDERS[name][6])


def water_plane_part(a):
    bed(a)
    water(a)


def foam_part(a):
    foam(a)


# ---- hero --------------------------------------------------------------------------------------------------------------------
def hero_land(a):
    """Every solid land piece of the hero, each a closed shell (the union fuses them): bed, beach, ridge core, the
    column rows, the grass slab, the low boxes, boulders, pebbles, lawn rocks. The vegetation is added afterwards on
    the finished land (_add_vegetation)."""
    bed(a)
    wl = _catmull(WATERLINE, WL_STEP)
    beach(a)
    ridge_core(a)
    for name in list(FRONT_COLS) + list(BACK_COLS):
        vs = column(a, name)
        _paint_column(a, vs, col_spec(name)[4], beach_z=1.8 if name in FRONT_COLS else -1.0)
    grass_slab(a)
    for name in BOXES:
        low_box(a, name)
    boulders(a)
    pebbles(a, lambda p: beach_z(p, wl))
    lawn_rocks(a)


def hero_water(a):
    water(a)
    foam(a)


NOTES = {
    HERO: "riverbank shoreline corner terrain tile (32 x 26, W03 levels: bed 0.2, water 1.0, beach 1.0-1.8, grass "
          "10.4): a grass-topped ridge with a row of big flat-faced cliff columns turning 45 degrees from the "
          "front-left to the back-right, a sand beach at the cliff foot, see-through water at the front-right with a "
          "separate flat foam ribbon and rings round the boulders; one closed land shell plus closed water and foam "
          "shells (exported as two see-through water pieces). 8 water_foam sockets",
    "ShorelineCornerGrassTop": "Grass Top (reusable): thick lime grass slab with a soil band, a sand path along the "
                               "rim, two pines, fan bushes, daisies, yellow flowers, small lawn rocks",
    "ShorelineCornerSandStrip": "Dirt / Sand Strip (reusable): the beach slab, sloping from the cliff foot (1.8) to "
                                "the waterline (1.0)",
    "ShorelineCornerRockSlope": "Rock Slope (reusable): the front row of big flat-faced bevelled cliff columns with "
                                "their foot boulders",
    "ShorelineCornerWaterPlane": "Water Plane (reusable): the see-through water slab (top 1.0) over its dark bed (0.2), "
                                 "with holes for the boulders",
    "ShorelineCornerFoam": "Foam (reusable): the separate flat foam mesh (shore ribbon with round holes, boulder "
                           "rings, blobs) 0.03 over the water",
}

# ---- stages 5 + 6 (spec section 7) -------------------------------------------------------------------------------------------
# Stage 5: nothing glows (decision 8): no emissive key, no light. The water and foam are see-through water pieces.
# Stage 6: water_foam sockets (decision 6): five along the waterline every 5-6 studs at z 1.05 and one per boulder
# standing in the water.
FX = [("water_foam", (-3.6, -12.4, 1.05), 0.7), ("water_foam", (0.2, -9.4, 1.05), 0.7),
      ("water_foam", (5.1, -2.8, 1.05), 0.75), ("water_foam", (9.8, 2.5, 1.05), 0.7),
      ("water_foam", (12.4, 6.4, 1.05), 0.65),
      ("water_foam", (5.0, -10.4, 1.05), 1.0), ("water_foam", (8.8, -6.0, 1.05), 0.6),
      ("water_foam", (10.6, 2.6, 1.05), 0.8)]


# ---- cleanup -------------------------------------------------------------------------------------------------------------------
def _union_fine(o):
    return m026._union_fine(o, 0.0)


def _bottom_centre(o):
    return m012._bottom_centre(o)


def _clean(o, ground):
    m016._weld(o)
    ears = m016._dissolve_ears(o)
    pockets = m012._drop_inner(o)
    log = m026._clean_guarded(o, m026._lock((0.0,) if ground else ()), max_move=0.08)
    pockets += m012._drop_inner(o)
    log["ears"] = ears
    log["pockets"] = pockets
    log["forced"] = _safe_force(o)
    return log


def _force_guarded(o, lim=5.0, max_len=0.4, rounds=12, flips=True):
    """m012._force_slivers' needle collapse (each needle's shortest edge merged onto its better-connected end, link
    condition kept, the ground kept flat), but a collapse is only made if moving the dropped end to the kept one
    makes no face cross another (m026._crosses). Returns the number collapsed."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = 0
    lim_r = math.radians(lim)
    for _ in range(rounds):
        bad = [f for f in bm.faces if len(f.verts) == 3 and m011._fmin(f) < lim_r]
        done = False
        for f in bad:
            if not f.is_valid or len(f.verts) != 3 or m011._fmin(f) >= lim_r:
                continue
            # a cap (no short edge): flip its long edge if both new triangles are better and cross nothing
            long_ = max(f.edges, key=lambda x: x.calc_length())
            if flips and len(long_.link_faces) == 2:
                g = next(x for x in long_.link_faces if x is not f)
                if len(g.verts) == 3:
                    A, B = long_.verts
                    c = next(v for v in f.verts if v not in (A, B))
                    d = next(v for v in g.verts if v not in (A, B))
                    old = min(m011._fmin(f), m011._fmin(g))
                    t1, t2 = [A.co, c.co, d.co], [c.co, B.co, d.co]
                    new = min(m011._min_angle(t1), m011._min_angle(t2))
                    if new > old + 1e-3 and d not in {x.other_vert(c) for x in c.link_edges}:
                        bm.faces.ensure_lookup_table()
                        full = BVHTree.FromBMesh(bm)
                        cand = m026._shrunk_tree([[p.copy() for p in t1], [p.copy() for p in t2]])
                        hits = [j for _, j in cand.overlap(full) if bm.faces[j] not in (f, g)]
                        if not hits and bmesh.ops.rotate_edges(bm, edges=[long_], use_ccw=False)["edges"]:
                            n += 1
                            done = True
                            continue
            for e in sorted(f.edges, key=lambda x: x.calc_length()):
                if e.calc_length() > max_len or len(e.link_faces) != 2:
                    continue
                a, b = e.verts
                na = {x.other_vert(a) for x in a.link_edges}
                nb = {x.other_vert(b) for x in b.link_edges}
                if len(na & nb) != 2:
                    continue
                on_a, on_b = abs(a.co.z) < 1e-4, abs(b.co.z) < 1e-4
                if on_a and on_b:
                    keep = max((a, b), key=lambda v: len(v.link_edges))
                elif on_a or on_b:
                    keep = a if on_a else b
                else:
                    keep = max((a, b), key=lambda v: len(v.link_edges))
                drop = b if keep is a else a
                if m026._crosses(bm, drop, keep.co.copy()):
                    continue
                bmesh.ops.pointmerge(bm, verts=[a, b], merge_co=keep.co.copy())
                n += 1
                done = True
                break
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-5)
        if not done:
            break
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    return n


def _undo_if_folds(o, fn):
    """Run fn() on o; if it leaves more self-intersecting face pairs than before, put the mesh back and return
    None, else fn's result."""
    before = m016._self_hits(o)[0]
    keep = o.data.copy()
    r = fn()
    if m016._self_hits(o)[0] > before:
        old = o.data
        o.data = keep
        bpy.data.meshes.remove(old)
        return None
    bpy.data.meshes.remove(keep)
    return r


def _safe_force(o, lim=3.0, max_len=0.25):
    """m012._force_slivers in growing edge-length batches, each undone if its collapses fold the surface through
    itself (more self-intersecting face pairs than before)."""
    total = 0
    # triangulate first with the crossing-aware splitter (bmesh's beauty split of the desliver's non-planar n-gons
    # was what folded the surface)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    if any(len(f.verts) > 3 for f in bm.faces):
        m026._tri_safe(bm)
        bm.to_mesh(o.data)
    bm.free()
    k = _undo_if_folds(o, lambda: _force_guarded(o, lim=max(lim, POLISH_LIM), max_len=max(max_len, 0.6)))
    if k is None:
        k = _undo_if_folds(o, lambda: _force_guarded(o, lim=max(lim, POLISH_LIM), max_len=max(max_len, 0.6),
                                                     flips=False)) or 0
    total += k
    for ml in (0.06, 0.12, 0.2, max_len):
        if ml > max_len:
            continue
        before = m016._self_hits(o)[0]
        keep = o.data.copy()
        n = m012._force_slivers(o, lim=lim, max_len=ml)
        if m016._self_hits(o)[0] > before:
            old = o.data
            o.data = keep
            bpy.data.meshes.remove(old)
            continue
        bpy.data.meshes.remove(keep)
        total += n
    return total


def _finish(o):
    o[OFF] = list(Vector(o[OFF]) + _bottom_centre(o))
    res = M.finish(o, union=False, uv=False)
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
        _safe_force(o)
        o[OFF] = list(Vector(o[OFF]) + _bottom_centre(o))
        res = M.finish(o, union=False, uv=False)
    return res


def _polish(o):
    """Quads split, the floor cap re-fanned (no needles), slivers forced open (m023 / m026's polish)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = m012._tri_quads(bm)
    zmin = min(v.co.z for v in bm.verts)
    floor = [f for f in bm.faces if f.normal.z < -0.999 and all(abs(v.co.z - zmin) < 1e-4 for v in f.verts)]
    big = [f for f in floor if f.calc_area() > 0.8 and m011._fmin(f) < math.radians(12)]
    if big:
        made = bmesh.ops.poke(bm, faces=big)["faces"]
        floor = [f for f in floor if f.is_valid] + list(made)
    fset = set(floor)
    inner = [e for e in {e for f in floor for e in f.edges} if all(g in fset for g in e.link_faces)]
    if inner:
        bmesh.ops.beautify_fill(bm, faces=floor, edges=inner)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = _safe_force(o, lim=POLISH_LIM)
    if m012._thin(o, POLISH_LIM)["under"]:
        forced += _safe_force(o, lim=POLISH_LIM, max_len=0.5)
    if m012._thin(o, POLISH_LIM)["under"]:
        # fix round 1: the seam needles where two column faces cross at a shallow angle have no edge under 0.5
        forced += _safe_force(o, lim=POLISH_LIM, max_len=POLISH_LONG)
    o.data.update()
    return {"split": split, "forced": forced}


def _ground_faces(o):
    """Faces on the ground plane (the floor cut's cap): the underside's dark soil (one flat even bottom; spec 1.3
    close-up 2), the bed's own colour under the water."""
    from m011 import _Paint
    p = _Paint(o, off=o[OFF])
    n = 0
    for f in p.bm.faces:
        if all(abs(v.co.z) < 1e-3 for v in f.verts):
            f.material_index = p._mi(SOIL_DARK)
            n += 1
    p.done()
    return n


def _recentre(o):
    bc = _bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


def _join_built(o, fn, name, union=False):
    """Build fn into a temporary object in the same build frame as o (o[OFF] is the build point at o's origin),
    union its shells first if asked, and join it into o."""
    a = K.fk().Asset(PFX + name, "probe", seed=7, tint_var=0.0)
    fn(a)
    c = a.finish(collection=o.users_collection[0], mark_asset=False, origin=None)
    c.matrix_world = o.matrix_world @ Matrix.Translation(-Vector(o[OFF]))
    bpy.context.view_layer.update()
    if union:
        _union_fine(c)
        M.fix_bowties(c)
    bm = bmesh.new()
    bm.from_mesh(c.data)
    ng = [f for f in bm.faces if len(f.verts) > 4]
    if ng:
        bmesh.ops.triangulate(bm, faces=ng, quad_method="BEAUTY", ngon_method="BEAUTY")
        bm.to_mesh(c.data)
    bm.free()
    with M._override(o):
        c.select_set(True)
        with bpy.context.temp_override(selected_objects=[o, c], selected_editable_objects=[o, c]):
            bpy.ops.object.join()
    return o


def _add_vegetation(o, ridge_only=False):
    """The pines (each one exact union of trunk and tiers) and the leaves and flowers (each its own closed shell),
    set VEG_GAP above o's finished surface."""
    ground = ground_of(o)
    for name in PINES:
        if ridge_only and name == "P3":
            continue
        _join_built(o, lambda a, n=name: pine(a, n, ground), "pine_" + name)
    guard = _Guard(o)
    _join_built(o, lambda a: vegetation(a, ground, ridge_only, guard), "veg")
    return guard.dropped


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)


PARTS = (("ShorelineCornerGrassTop", grass_top_part), ("ShorelineCornerSandStrip", sand_strip_part),
         ("ShorelineCornerRockSlope", rock_slope_part), ("ShorelineCornerWaterPlane", water_plane_part),
         ("ShorelineCornerFoam", foam_part))
UNION_PARTS = {"ShorelineCornerGrassTop", "ShorelineCornerRockSlope"}
VEG_PARTS = {"ShorelineCornerGrassTop"}
GROUND_PARTS = {"ShorelineCornerRockSlope", "ShorelineCornerSandStrip"}
WATER_PARTS = {"ShorelineCornerWaterPlane", "ShorelineCornerFoam"}
TARGET_SIZE = ((32.0, 0.5), (26.0, 1.5), (17.0, 1.2))


def _make_part(name, fn):
    o = M.mk(SHEET, name, fn, subject=TITLE, role="part", notes=NOTES[name], budget=1000,
             collision="none" if name in WATER_PARTS else "hull", tint_var=0.0)
    off = M._build_offset(fn)
    o[OFF] = list(off)
    lg = {}
    if name in UNION_PARTS:
        lg["shells_merged"] = _union_fine(o)
    if name in GROUND_PARTS:
        m016._floor_cut(o, -off.z)
        o[OFF] = [off.x, off.y, 0.0]
    if name not in WATER_PARTS:
        lg["clean"] = _clean(o, name in GROUND_PARTS)
        lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
        lg["polish"] = _polish(o)
    else:
        _recentre(o)
        m016._weld(o, 1e-4)
    lg["bowties"] = M.fix_bowties(o)
    if name in VEG_PARTS:
        lg["veg_dropped"] = _add_vegetation(o, ridge_only=True)
    _recentre(o)
    for p in o.data.polygons:
        p.use_smooth = False
    M.smart_uv(o, **UV)
    lg["uv_cut"] = m012._uv_unfold(o)
    return o, lg


def _make_hero():
    t0 = time.time()
    lg = {}
    o = M.mk(SHEET, HERO, hero_land, subject=TITLE, role="hero", notes=NOTES[HERO], budget=4000, collision="precise",
             tint_var=0.0)
    off = M._build_offset(hero_land)
    o[OFF] = list(off)
    lg["t_build"] = round(time.time() - t0, 1)
    lg["shells_merged"] = _union_fine(o)
    lg["t_union"] = round(time.time() - t0, 1)
    m016._floor_cut(o, -off.z)
    o[OFF] = [off.x, off.y, 0.0]
    lg["clean"] = _clean(o, True)
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    lg["ground_faces"] = _ground_faces(o)
    lg["bowties_land"] = M.fix_bowties(o)
    lg["land"] = {k: v for k, v in M.audit(o).items() if k in ("tris", "shells", "nonmanifold_edges",
                                                                  "nonmanifold_verts", "boundary_edges")}
    # the vegetation shells on the finished land, then the water and foam shells (never unioned with the land)
    lg["veg_dropped"] = _add_vegetation(o)
    _join_built(o, hero_water, "water")
    lg["bowties_water"] = M.fix_bowties(o)
    _recentre(o)
    K.drop_unused_slots(o)
    for p in o.data.polygons:
        p.use_smooth = False
    M.smart_uv(o, **UV)
    lg["uv_cut"] = m012._uv_unfold(o)
    for kind, p, sc in FX:
        K.socket(o, kind, Vector(p) - Vector(o[OFF]), scale=sc)
    lg["t_total"] = round(time.time() - t0, 1)
    return o, lg


def shells_report(o):
    """Per shell: its keys (land / water / foam), tris, non-manifold edges and verts, boundary edges."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = [m.get("flintkit_key", m.name) if m else None for m in o.data.materials]
    out = []
    for k in range(n):
        fs = [f for f in bm.faces if ids[f.index] == k]
        es = {e for f in fs for e in f.edges}
        vs = {v for f in fs for v in f.verts}
        ks = sorted({keys[f.material_index] for f in fs})
        kind = ("foam" if ks == [FOAM] else "water" if ks == [WATER] else
                "veg" if set(ks) <= {LEAF, PINE, BARK, PETAL, POLLEN} else "land")
        out.append({"kind": kind, "tris": sum(len(f.verts) - 2 for f in fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary)})
    bm.free()
    return out


def build(render=True, parts=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    RIDGE.clear()
    HOLES.clear()
    holes()
    log = {}
    objs = {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make_part(name, fn)
    h, log["hero"] = _make_hero()
    _cleanup_tmp()
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    audits = [M.audit(o) for o in order]
    self_hits = {o.name: m016._self_hits(o)[0] for o in order}
    thin = {o.name: m012._thin(o, POLISH_LIM) for o in order}
    for o in order:
        if o.name in SHADING_OK:
            o["kit_shading_ok"] = SHADING_OK[o.name]
    problems = list(K.check(order))
    shells = shells_report(h)
    kinds = [s["kind"] for s in shells]
    if kinds.count("land") != 1 or "water" not in kinds or "foam" not in kinds:
        problems.append(f"{HERO}: shells {sorted(set(kinds))} ({kinds.count('land')} land), expected one land shell "
                        f"plus water, foam and vegetation shells")
    for s in shells:
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges"):
            if s[k]:
                problems.append(f"{HERO} {s['kind']} shell: {k} {s[k]}")
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
        if self_hits[o.name]:
            problems.append(f"{o.name}: {self_hits[o.name]} self-intersecting face pairs")
        if thin[o.name]["under"]:
            problems.append(f"{o.name}: {thin[o.name]['under']} faces with a corner under {POLISH_LIM} deg")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    socks = [c.get("vfx_kind") for c in h.children if c.get("vfx_kind")]
    if len(socks) != 8:
        problems.append(f"{HERO}: {len(socks)} sockets, expected 8")
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts")} for au in audits],
           "shells": {k: {"n": sum(1 for x in shells if x["kind"] == k),
                          "tris": sum(x["tris"] for x in shells if x["kind"] == k),
                          "bad": sum(x["nonmanifold_edges"] + x["nonmanifold_verts"] + x["boundary_edges"]
                                     for x in shells if x["kind"] == k)} for k in ("land", "veg", "water", "foam")},
           "thin": thin, "self_hits": self_hits, "log": log, "problems": problems, "uv": uv,
           "sockets": socks, "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order)
        out["total_s"] = round(time.time() - t0, 1)
    return out


# The kit's shading check groups sand, tan soil and dark soil as one family (hue 31-37 deg) and finds the bright sand
# on top faces and the soil on the side bands and the underside. These are real material regions of the sheet, not
# painted light: the beach and path sand (#FBCF83), the tan dirt sides of the slabs and boxes (#B98745, "tan side
# band" in the underside close-up) and the brown flat bottom (#936631, "Clean flat bottom surface").
SHADING_OK = {HERO: "sand beach/path vs tan dirt slab sides vs brown underside: the sheet's own material regions "
                    "(underside close-up #C69B51 rim, #936631 bottom; exploded sand strip #FBCF83)",
              "ShorelineCornerGrassTop": "sand path on the turf vs the tan soil band and dirt underside of the slab "
                                         "(exploded Grass Top: green-sided slab with a brown soil line)",
              "ShorelineCornerSandStrip": "sand top vs tan dirt sides (exploded Dirt / Sand Strip)"}


# ---- renders -------------------------------------------------------------------------------------------------------------------
# the sheet's comparison cameras (decision 3): the f34 cell is an elevated front view (az 0) of the 45-degree coast;
# the r34 and rear cells are real views from behind; the side cell is the kit +X camera; *_sheet shots use a 3x
# longer lens and hide the studio floor (the sheet draws no ground shadow)
SHEET_VIEWS = {"f34_sheet": (0, 32), "front_sheet": (0, 26), "r34_sheet": (180, 30), "rear_sheet": (180, 18),
               "side_sheet": (90, 12), "top_sheet": (0, 89)}
SHEET_LENS = 3.0
JUNC_CU = (-30, 15, (-0.4, -1.6, 8.6), 3.8)      # close-up 1: C2 / C3a under the grass slab
WATER_CU = (-25, 35, (5.0, -10.4, 1.5), 4.2)    # close-up 3: W1 in its foam ring
PARTS_SHOT = (-20, 25)


def _long_lens(kit):
    orig = kit["render_group"]

    def rg(group, path, azimuth=-22, elevation=20):
        cam = bpy.data.objects["FB_Cam"].data
        lens = cam.lens
        ground = bpy.data.objects.get("FB_Ground")
        sheet = "_sheet" in path
        if sheet:
            cam.lens = lens * SHEET_LENS
            if ground:
                ground.hide_render = True
        try:
            return orig(group, path, azimuth, elevation)
        finally:
            cam.lens = lens
            if ground and sheet:
                ground.hide_render = False
    return orig, rg


def _part_matrix(o):
    return Matrix.Translation(Vector(o[OFF]))


EXPL = {"ShorelineCornerWaterPlane": (4.0, -4.0, 0.0), "ShorelineCornerFoam": (4.0, -4.0, 0.0),
        "ShorelineCornerRockSlope": (0.0, 0.0, 2.5), "ShorelineCornerSandStrip": (-3.0, 3.0, 11.0),
        "ShorelineCornerGrassTop": (-6.0, 6.0, 13.0)}


def _exploded(objs):
    """Copies of the parts in their build positions, lifted apart like the sheet's Exploded Construction (water and
    foam at the bottom, then the rock slope, the sand strip, the grass top)."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []
    x0 = objs[0].location.x + 60
    base = Matrix.Translation((x0, objs[0].location.y, 0))
    for name, d in EXPL.items():
        if name not in by:
            continue
        c = bpy.data.objects.new(f"{PFX}expl_{name[15:]}", by[name].data)
        coll.objects.link(c)
        c.matrix_world = base @ Matrix.Translation(d) @ _part_matrix(by[name])
        shown.append(c)
    bpy.context.view_layer.update()
    return shown


def render_close(objs, path, az, el, centre, radius_):
    kit = K.NS["KIT"]
    fb = kit["frame_box"]
    c = Vector(centre)
    box = [c + Vector((dx, dy, dz)) * radius_ for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    kit["frame_box"] = lambda corners, a_, e_: fb(box, a_, e_)
    ground = bpy.data.objects.get("FB_Ground")
    if ground:
        ground.hide_render = el < 0
    cell = kit["CELL"]
    kit["CELL"] = (480, 400)
    try:
        return kit["render_group"](objs, path, az, el)
    finally:
        kit["CELL"] = cell
        kit["frame_box"] = fb
        if ground:
            ground.hide_render = False


def render_views(objs, close=True, sheet_only=False):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 and not sheet_only else []
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        if shown:
            extra["exploded"] = (shown, -15, 22)
        if not sheet_only:
            for o in objs[1:]:
                extra["part_" + o.name.replace("ShorelineCorner", "").lower()] = ([o], *PARTS_SHOT)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            sheet = M.views(NUM, [h], names=() if sheet_only else ("front34", "rear34", "front", "side", "rear", "top",
                                                                   "underside"), extra=extra)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet}
        if close and not sheet_only:
            d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
            off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
            cl = lambda tag, az, el, c, r: render_close([h], f"{d}/{tag}.png", az, el, off @ Vector(c), r)
            out["junc_cu"] = cl("junc_cu", *JUNC_CU)
            out["water_cu"] = cl("water_cu", *WATER_CU)
            out["under_cu"] = render_close([h], f"{d}/under_cu.png", 20, -40, off @ Vector((-2, -2, 0.5)), 9.0)
        return out
    finally:
        for o in shown:
            bpy.data.objects.remove(o, do_unlink=True)
        M.display(NUM, objs, TITLE)


# ---- measuring (the study's masks: M032_spec.md, m.py cls()) -------------------------------------------------------------
REF_VIEWS = {"f34": (16, 142, 508, 480), "r34": (517, 142, 1008, 480), "front": (16, 548, 271, 737),
             "side": (275, 548, 495, 737), "rear": (514, 548, 768, 737), "top": (772, 548, 1008, 737)}
TITLES = [(16, 142, 215, 187), (517, 142, 715, 187)]
OUR_VIEWS = {"f34": "f34_sheet", "front": "front_sheet", "r34": "r34_sheet", "rear": "rear_sheet",
             "side": "side_sheet", "top": "top_sheet"}
SHEET_PAPER = (253, 250, 242)


def _hsv(px):
    r, g, b = px[..., 0] / 255, px[..., 1] / 255, px[..., 2] / 255
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0)
    return h, s, mx


LABELS = "GDSRWFO"


def classes(px, paper=SHEET_PAPER, ptol=14):
    """The study's masks: '' paper, G vegetation, D dark soil / bark, S sand / tan, R rock, W water, F foam, O other."""
    h, s, v = _hsv(px)
    paper_m = np.abs(px - np.array(paper, float)).max(-1) <= ptol
    G = (h >= 52) & (h <= 165) & (s >= 0.30) & (v >= 0.06)
    Y = (h >= 40) & (h < 52) & (s >= 0.55) & (v >= 0.75)
    W = (h >= 182) & (h <= 215) & (s >= 0.45) & (v >= 0.45)
    F = (h >= 165) & (h <= 225) & (s >= 0.03) & (s < 0.45) & (v >= 0.86)
    S = (h >= 28) & (h < 52) & (s >= 0.28) & (s < 0.72) & (v >= 0.66) & ~Y
    D = (h >= 10) & (h < 45) & (s >= 0.30) & (v >= 0.18) & (v < 0.66)
    Rk = (((s < 0.20) & (v >= 0.25) & (v < 0.93))
          | ((h >= 200) & (h <= 290) & (s < 0.45) & (v >= 0.20) & (v < 0.86))
          | (((h < 28) | (h >= 320)) & (s < 0.30) & (v >= 0.25) & (v < 0.93))) & ~F
    out = np.zeros(px.shape[:2], np.uint8)       # 0 paper
    for k, m in ((2, D), (3, S), (4, Rk), (6, F), (5, W), (1, G | Y)):
        out[m & (out == 0)] = k
    out[(~paper_m) & (out == 0)] = 7
    out[paper_m] = 0
    return out


def _load(path, box=None):
    px = K.NS["KIT"]["load_px"](path)[::-1, :, :3] * 255.0
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1].copy()
    return np.clip(px, 0, 255)


def _hex(q):
    return "#" + "".join(f"{int(round(x)):02X}" for x in q)


def stats(px, paper=SHEET_PAPER, ptol=14):
    c = classes(px, paper, ptol)
    sil = c > 0
    ys, xs = np.nonzero(sil)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    W, H = x1 - x0 + 1, y1 - y0 + 1
    n = sil.sum()
    out = {"wh": round(W / H, 3), "shares": {L: round(float((c == i + 1).sum() / n), 3) for i, L in enumerate(LABELS)}}
    top, bot = [], []
    for f in np.round(np.arange(0, 1.0001, 0.05), 2):
        x = int(round(x0 + f * (W - 1)))
        col = np.nonzero(sil[:, max(x - 1, x0):x + 2].any(1))[0]
        top.append(round((y1 - col.min()) / (H - 1), 2) if len(col) else None)
        bot.append(round((y1 - col.max()) / (H - 1), 2) if len(col) else None)
    out["top"], out["bot"] = top, bot
    w = []
    for hh in np.arange(0, 1.0001, 0.1):
        y = int(round(y1 - hh * (H - 1)))
        row = np.nonzero(sil[max(y - 1, y0):y + 2].any(0))[0]
        w.append((round((row.max() - row.min() + 1) / W, 2), round((row.min() - x0) / W, 2)) if len(row) else None)
    out["wph"] = w
    sub = px[y0:y1 + 1, x0:x1 + 1]
    cs = c[y0:y1 + 1, x0:x1 + 1]
    for i, L in enumerate(LABELS[:-1]):
        sel = sub[cs == i + 1]
        if len(sel) >= 8:
            out[L + "med"] = _hex(np.median(sel, axis=0))
    return out


def measure(views=("f34", "front", "r34", "rear", "side", "top")):
    """Sheet against our renders, per view, with the study's masks on both (our background is the paper)."""
    ref = M.ref(NUM)
    sheet = _load(ref)
    for (tx0, ty0, tx1, ty1) in TITLES:
        sheet[ty0:ty1, tx0:tx1] = SHEET_PAPER
    out = {}
    for vname in views:
        x0, y0, x1, y1 = REF_VIEWS[vname]
        a = stats(sheet[y0:y1, x0:x1].copy())
        ours = _load(f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[vname]}.png")
        corner = tuple(float(x) for x in np.median(ours[:6, :6].reshape(-1, 3), axis=0))
        b = stats(ours, paper=corner, ptol=18)
        err = [abs(x - y) for x, y in zip(a["top"], b["top"]) if x is not None and y is not None]
        berr = [abs(x - y) for x, y in zip(a["bot"], b["bot"]) if x is not None and y is not None]
        out[vname] = {"sheet": a, "ours": b, "top_err_mean_max": (round(sum(err) / len(err), 3), round(max(err), 2)),
                      "bot_err_mean_max": (round(sum(berr) / len(berr), 3), round(max(berr), 2))}
    return out
