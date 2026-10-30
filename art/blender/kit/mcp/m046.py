"""046 Natural Arch (references/046.png): a free-standing modular rock arch (rock 24 W x 12 D, lawn top 14.0) with a
7.0-wide walk-through opening (jambs vertical to 5.4, a haunch to the flat seat ledges at 8.0, a three-facet soffit to a
sharp apex at 9.4; 9.0 clear over the 0.4 sand floor). Two columnar rock masses (bottom-heavy: skirt blocks and faceted
foot boulders), a lumpy top span seated on the masses' ledges, a lime lawn dome capping every rock top (one cap per
part, seams at x = +-6.7), round two-tone dome bushes, pebbles and yellow flowers on the lawn, a sand flagstone floor
through the tunnel, a lime apron with foot bushes, sprigs, flowers and pebbles round the foot.

    import importlib, kit_models, m046; importlib.reload(kit_models); importlib.reload(m046); m046.build()

Build frame (studs): the opening's axis along Y (front face -Y, back +Y), Left mass at -X, Right mass at +X, ground z 0,
the opening's centre on the ground at the origin. W02 owns NaturalArch*, W16 StoneArch*: names StoneGate*.
- StoneGateSpan ("Top Span"): ONE closed shell built directly as a loft of 15 rings along X (front / back lumps as ring
  offsets, seat bottoms flat at 7.98 for |x| >= 2.3, the soffit facets to the apex at 9.4), its ends embedded 0.05 in
  the masses; plus its lawn cap and rim dressing.
- StoneGateMassL / StoneGateMassR ("Left / Right Rock Mass"): each core ONE closed shell built directly (no boolean):
  a ring of column chain points (creases, faces, ridges), each a vertical column of verts; the jamb face (vertical to
  5.4), the haunch to the tip x +-2.25 at z 8.0, the hidden flat ledge at 8.0, the hidden flat joining face at x +-6.7,
  the hidden top under the lawn and the flat bottom at z 0. Skirt blocks and foot boulders are their own closed shells.
  Plus the mass's lawn cap, its rim bushes and turfed skirt pads.
- StoneGateSill ("Ground Sill (Floor)"): 12 sand flagstones (Voronoi cells, square-edged slabs, tops at 0.40 +- 0.02) and floor
  pebbles.
The hero (StoneGate) is one object of separate closed shells: the four parts plus the hero-only apron, foot bushes,
sprigs, flowers, pebbles and the lime strips along the tunnel's wall feet. In the hero object the build frame is at the
object's origin + hero["m046_offset"].

Stages 5-6: nothing (decision 11: the sheet shows no glow, light or effect). See M046_spec.md.
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
import m011
import m040
from m040 import (_area2, _beautify, _cdt, _clamp, _dome_heart, _hull_piece, _inside, _mottle, _poly_d, _prism,
                  _resample, _steiner, _touch, _tree_of, _tri, _v2, _bipyramid)
from m043 import _rleaf, _tleaf

NUM, TITLE, SHEET = 46, "Natural Arch", "M046"
OFF = "m046_offset"
PFX = "_m046_"
HERO = "StoneGate"
SPAN_P, MASSL_P, MASSR_P, SILL_P = "StoneGateSpan", "StoneGateMassL", "StoneGateMassR", "StoneGateSill"
PARTS = (SPAN_P, MASSL_P, MASSR_P, SILL_P)

ROCK, ROCK_LIGHT, ROCK_DEEP = "m046_rock", "m046_rock_light", "m046_rock_deep"
FLOOR, FLOOR_DEEP = "m046_floor", "m046_floor_deep"
GRASS, GRASS_LIGHT, GRASS_DEEP = "m046_grass", "m046_grass_light", "m046_grass_deep"
LEAF, LEAF_LIT, LEAF_DEEP = "m046_leaf", "m046_leaf_lit", "m046_leaf_deep"
FLOWER, PEBBLE, TRUNK = "m046_flower", "m046_pebble", "m046_trunk"
MARK = "m046_marker"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low specular). Stage 4 (M046_spec.md "Stage 4").
PALETTE = {
    ROCK: ("#A08B81", 0.9, False),
    ROCK_LIGHT: ("#B6A498", 0.9, False),
    ROCK_DEEP: ("#8F7A70", 0.9, False),
    FLOOR: ("#C39D75", 0.9, True),
    FLOOR_DEEP: ("#A08470", 0.9, True),
    GRASS: ("#A3B300", 0.85, True),
    GRASS_LIGHT: ("#AFBA06", 0.85, True),
    GRASS_DEEP: ("#8D9D00", 0.85, True),
    LEAF: ("#3A6815", 0.85, True),
    LEAF_LIT: ("#6C9F32", 0.85, True),
    LEAF_DEEP: ("#205D1F", 0.85, True),
    FLOWER: ("#B5B21A", 0.8, True),
    PEBBLE: ("#AEAEA7", 0.9, False),
    TRUNK: ("#381000", 0.95, False),
    MARK: ("#7E7978", 0.7, False),
}
# calibration targets (spec 5.4: rendered medians of unshadowed regions on the sheet)
TARGETS = {ROCK: ((0xC9, 0xAA, 0x9A), "all"), ROCK_LIGHT: ((0xE6, 0xCB, 0xB7), "all"),
           ROCK_DEEP: ((0xB3, 0x95, 0x87), "all"),
           FLOOR: ((0xF6, 0xBC, 0x82), "brown"), FLOOR_DEEP: ((0xC6, 0x9C, 0x7A), "brown"),
           GRASS: ((0xCC, 0xD6, 0x0A), "vivid"), GRASS_LIGHT: ((0xD9, 0xE3, 0x0F), "vivid"),
           GRASS_DEEP: ((0xAD, 0xBC, 0x09), "vivid"),
           LEAF: ((0x40, 0x76, 0x16), "green"), LEAF_LIT: ((0x82, 0xC0, 0x32), "green"),
           LEAF_DEEP: ((0x1F, 0x6A, 0x21), "green"),
           FLOWER: ((0xE2, 0xDB, 0x1A), "vivid"), PEBBLE: ((0xDD, 0xD6, 0xC3), "all"),
           TRUNK: ((0x4A, 0x26, 0x07), "brown")}


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


def _pl(tab, x):
    """Piecewise-linear lookup (extrapolates past the last point)."""
    if x <= tab[0][0]:
        return tab[0][1]
    for (x0, y0), (x1, y1) in zip(tab, tab[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    (x0, y0), (x1, y1) = tab[-2], tab[-1]
    return y1 + (y1 - y0) * (x - x1) / (x1 - x0)


# ---- the dome: the rock top under the lawn (spec 2.1 / 2.3) --------------------------------------------------------------
ZT0 = 13.4
A_X = [(0.0, 0.0), (5.0, 0.0), (6.7, 0.15), (7.4, 0.4), (8.6, 1.05), (9.5, 2.05), (10.0, 2.85), (10.6, 3.6), (12.0, 5.5)]
B_Y = [(0.0, 0.0), (3.0, 0.0), (4.4, 0.25), (5.0, 0.7), (5.6, 1.4), (7.0, 3.0)]
LAWN_T = 0.6                # lawn thickness over the rock top inside the cap


def zt(x, y):
    """Rock top height under the lawn: 13.4 over the middle, the shoulders falling over both ends, the rims front and
    back rounding over."""
    return ZT0 - _pl(A_X, abs(x)) - _pl(B_Y, abs(y))


# ---- the masses ---------------------------------------------------------------------------------------------------------
# batter (setback of a face from its foot) by height: front / back faces, and the end faces (spec 2.3 table)
S_FRONT = [(0.0, 0.0), (5.4, 0.1), (8.0, 0.2), (10.3, 0.3), (11.4, 0.5), (12.4, 0.8), (13.0, 1.15), (14.0, 1.6)]
S_END = [(0.0, 0.0), (5.4, 0.8), (8.0, 1.2), (10.3, 1.8), (11.4, 2.3), (12.4, 2.9), (14.0, 3.8)]
HAUNCH = [(5.4, 0.0), (6.2, 0.24), (7.0, 0.52), (7.6, 0.76), (8.0, 1.0)]
JAMB_X, TIP, LEDGE_Z, JOINT_X = 3.5, 2.25, 8.0, 6.7
JOINT_Z = (8.0, 10.0, 11.8)   # the joint line's levels above the ledge (shared with the span's end rings)
ACROSS_Y = (-2.0, 2.0)        # the joining face's interior points (x = +-6.7)
Y0, XE, RC = 5.6, 11.8, 3.2
X_FRONT1 = XE - RC
SEG = [X_FRONT1 - JAMB_X, math.pi * RC / 2, 2 * (Y0 - RC), math.pi * RC / 2, X_FRONT1 - JAMB_X]
PATH_L = sum(SEG)
# column boundaries (creases) along the outer path, by arc length from the front jamb corner (the joints at x = 6.7)
CREASES = {1: (3.2, 5.75, 8.3, 10.85, 13.2, 15.75, 18.3, PATH_L - 3.2),
           -1: (3.2, 5.9, 8.15, 10.7, 13.35, 15.6, 18.45, PATH_L - 3.2)}
# the jamb face's interior points (y, x offset into the rock), back to front
JAMB = {1: ((3.0, 0.25), (0.2, 0.05), (-2.8, 0.2)), -1: ((3.2, 0.12), (0.4, 0.26), (-2.6, 0.06))}
GEO = {}


def _path(s):
    """Point and outward normal on the right mass's base path (front jamb corner -> front -> corner -> end -> corner
    -> back -> back jamb corner) at arc length s."""
    s = max(0.0, min(PATH_L, s))
    a = SEG[0]
    if s <= a:
        return Vector((JAMB_X + s, -Y0)), Vector((0.0, -1.0))
    s -= a
    if s <= SEG[1]:
        t = -math.pi / 2 + s / RC
        return Vector((X_FRONT1 + RC * math.cos(t), -(Y0 - RC) + RC * math.sin(t))), Vector((math.cos(t), math.sin(t)))
    s -= SEG[1]
    if s <= SEG[2]:
        return Vector((XE, -(Y0 - RC) + s)), Vector((1.0, 0.0))
    s -= SEG[2]
    if s <= SEG[3]:
        t = s / RC
        return Vector((X_FRONT1 + RC * math.cos(t), (Y0 - RC) + RC * math.sin(t))), Vector((math.cos(t), math.sin(t)))
    s -= SEG[3]
    return Vector((X_FRONT1 - s, Y0)), Vector((0.0, 1.0))


def _setback(z, w):
    return (1.0 - w) * _pl(S_FRONT, z) + w * _pl(S_END, z)


def _solve_top(foot, n, w):
    """The height where a column (foot, inward batter) meets the dome zt."""
    def f(z):
        p = foot - n * _setback(z, w)
        return z - zt(p.x, p.y)
    lo, hi = 3.0, 15.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def mass_geo(sx):
    """Positions of one mass core (right frame mirrored by sx): the chain of column points round the outline, each with
    its column of 3D points; the joint columns; the across points. Pure and cached."""
    if sx in GEO:
        return GEO[sx]
    rng = random.Random(46100 if sx > 0 else 46200)
    bounds = [0.0] + list(CREASES[sx]) + [PATH_L]
    nb = len(bounds) - 1
    chain = []

    def add(kind, s, push, col, zone):
        p, n = _path(s)
        chain.append(dict(kind=kind, s=s, foot=p + n * push, n=n, push=push, cid=col, zone=zone))
    add("jcorner", 0.0, 0.0, 0, "hz")
    for j in range(nb):
        sa, sb = bounds[j], bounds[j + 1]
        w = sb - sa
        if j > 0:
            joint = j in (1, nb - 1)
            add("joint" if joint else "crease", sa, -0.3 if joint else -(0.74 + rng.uniform(-0.1, 0.1)), j,
                "joint" if joint else "outer")
        zone = "hz" if j in (0, nb - 1) else "outer"
        # fix round 1 (finding 5, "broad flat faces, chunky"): each column face is TWO broad facets meeting at a
        # mid ridge (spec 2.3), no third "face" strip; the rng draws stay so the other columns keep their values
        rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04)
        add("ridge", sa + (0.52 + rng.uniform(-0.05, 0.05)) * w, 0.36 + rng.uniform(-0.06, 0.06), j, zone)
    add("jcorner", PATH_L, 0.0, nb - 1, "hz")
    for y, xo in JAMB[sx]:
        chain.append(dict(kind="jamb", s=None, foot=Vector((JAMB_X + xo, y)), n=Vector((-1.0, 0.0)), push=0.0, cid=nb,
                          zone="jamb"))
    # stacked blocks: per column, a lower block bulging at m1, a block joint (set back) at m2, an upper bulge at m3
    # (the sheet's lumpy columns); every point of a column shares its levels, so the breaks run across the column
    levels = {}
    for j in range(nb + 1):
        levels[j] = (rng.uniform(1.9, 3.1), rng.uniform(4.4, 6.2), rng.uniform(7.4, 9.6),
                     rng.uniform(0.24, 0.36), rng.uniform(0.12, 0.22), rng.uniform(0.2, 0.32))
    for c in chain:
        kind, n, foot = c["kind"], c["n"], c["foot"]
        w = abs(n.x) if kind not in ("jamb", "jcorner", "joint") else 0.0
        if kind in ("crease", "joint", "face", "ridge"):
            # the hz columns and the joints share the levels of the outer column beside the joint (no slivers)
            cid = 1 if c["cid"] == 0 else nb - 2 if c["cid"] == nb - 1 else c["cid"]
            m1, m2, m3, b1, j2, b3 = levels[cid]
            bulge = {m1: b1, m2: -j2, m3: b3}
            if kind in ("crease", "joint"):
                bulge = {m1: 0.06, m2: -0.08, m3: 0.05}
            if kind == "joint":
                top = _solve_top(foot, n, 0.0)
                zs = [0.0, m1, min(m2, 6.6), LEDGE_Z] + list(JOINT_Z[1:]) + [top]
                bulge[min(m2, 6.6)] = -0.08
            elif c["zone"] == "hz":
                zs = [0.0, m1, 5.4, LEDGE_Z]
                bulge[5.4] = -j2
            else:
                top = _solve_top(foot - n * c["push"], n, w)
                zs = [z for z in (0.0, m1, m2, m3) if z < top - 0.8] + [top]
            col = []
            for k, z in enumerate(zs):
                p = foot - n * _setback(z, w)
                if 0 < k < len(zs) - 1 and z in bulge:
                    p = p + n * bulge[z]
                col.append(Vector((p.x, p.y, z)))
            c["col"] = col
            continue
        if kind in ("jcorner", "jamb"):            # the jamb: vertical to the spring, then the haunch
            zm = rng.uniform(2.4, 3.0)
            col = []
            for z in (0.0, zm, 5.4, 6.2, 7.0, 7.6, LEDGE_Z):
                y = foot.y - n.y * _pl(S_FRONT, z) if kind == "jcorner" else foot.y
                xs = JAMB_X if kind == "jcorner" else foot.x
                x = xs + (0.06 if z == zm else 0.0) if z <= 5.4 else xs + (TIP - xs) * _pl(HAUNCH, z)
                col.append(Vector((x, y, z)))
        c["col"] = col
    # mirror into place
    for c in chain:
        c["col"] = [Vector((sx * p.x, p.y, p.z)) for p in c["col"]]
        c["foot"] = Vector((sx * c["foot"].x, c["foot"].y))
        c["n"] = Vector((sx * c["n"].x, c["n"].y))
    ij = [i for i, c in enumerate(chain) if c["kind"] == "joint"]
    g = {"chain": chain, "jf": ij[0], "jb": ij[1],
         "ta": [Vector((sx * JOINT_X, y, zt(JOINT_X, y))) for y in ACROSS_Y],
         "ba": [Vector((sx * JOINT_X, y, LEDGE_Z)) for y in ACROSS_Y]}
    GEO[sx] = g
    return g


def _col_ids(sx):
    """Column number per chain point (creases belong to the column they start)."""
    rng_ids = []
    bounds = [0.0] + list(CREASES[sx]) + [PATH_L]
    for c in mass_geo(sx)["chain"]:
        if c["kind"] == "jamb":
            rng_ids.append(len(bounds))
            continue
        s = c["s"]
        j = max(0, min(len(bounds) - 2, max(k for k in range(len(bounds) - 1) if bounds[k] <= s + 1e-6)))
        rng_ids.append(j)
    return rng_ids


def _zip(bm, A, B, out):
    """Fill the strip between two vertical columns of verts (bottom -> top) with quads / tris, laddered by each
    column's normalised height."""
    def ts(C):
        z0, z1 = C[0].co.z, C[-1].co.z
        return [(v.co.z - z0) / max(1e-6, z1 - z0) for v in C]
    ta, tb = ts(A), ts(B)
    i = j = 0
    while i < len(A) - 1 or j < len(B) - 1:
        if i < len(A) - 1 and j < len(B) - 1 and abs(ta[i + 1] - tb[j + 1]) < 0.1:
            out.append(bm.faces.new((A[i], B[j], B[j + 1], A[i + 1])))
            i += 1
            j += 1
        elif j == len(B) - 1 or (i < len(A) - 1 and ta[i + 1] <= tb[j + 1]):
            out.append(bm.faces.new((A[i], B[j], A[i + 1])))
            i += 1
        else:
            out.append(bm.faces.new((A[i], B[j], B[j + 1])))
            j += 1


def _fill(bm, loop, proj, steiner=(), lift=None):
    """Faces over a planar-ish loop of existing verts: a CDT of their 2D projections plus Steiner points (lifted to
    3D by lift(Vector2))."""
    loop = list(loop)
    P2 = [proj(v.co) for v in loop]
    if _area2(P2) < 0:                     # the CDT keeps only counter-clockwise outlines' insides
        loop.reverse()
        P2.reverse()
    co, tris = _cdt(P2, (), list(steiner))
    vm = {i: loop[i] for i in range(len(loop))}
    out = []
    for t in tris:
        for i in t:
            if i not in vm:
                vm[i] = bm.verts.new(lift(co[i]))
        out.append(bm.faces.new([vm[i] for i in t]))
    return out


MASS_INFO = {}


def mass_core(a, sx):
    """One mass core as ONE closed shell (decision 7, built directly; no boolean)."""
    g = mass_geo(sx)
    ch = g["chain"]
    n_ = len(ch)
    bm = a.bm
    before = set(bm.verts)
    lay = bm.faces.layers.int.get("m046_band") or bm.faces.layers.int.new("m046_band")
    cols = [[bm.verts.new(p) for p in c["col"]] for c in ch]
    ta = [bm.verts.new(p) for p in g["ta"]]
    ba = [bm.verts.new(p) for p in g["ba"]]
    ids = _col_ids(sx)
    walls = []
    for i in range(n_):
        j = (i + 1) % n_
        A, B = cols[i], cols[j]
        ka, kb = ch[i]["kind"], ch[j]["kind"]
        za, zb_ = ch[i]["zone"], ch[j]["zone"]
        if ka == "joint" and zb_ in ("hz",):
            A = A[:4]
        if kb == "joint" and za in ("hz",):
            B = B[:4]
        fs = []
        _zip(bm, A, B, fs)
        for f in fs:
            f[lay] = 100 + ids[i] if ch[i]["kind"] != "crease" else 100 + ids[j]
        walls += fs
    jf, jb = g["jf"], g["jb"]
    # the flat ledge at 8.0 (hidden under the span's seat)
    ledge_loop = [cols[jf][3]] + [cols[k][-1] for k in range(jf - 1, -1, -1)] + \
                 [cols[k][-1] for k in range(n_ - 1, jb, -1)] + [cols[jb][3], ba[1], ba[0]]
    caps = _fill(bm, ledge_loop, lambda p: Vector((p.x, p.y)))
    # the flat joining face at x = +-6.7 (hidden under the span's end)
    join_loop = cols[jf][3:] + [ta[0], ta[1]] + list(reversed(cols[jb][3:])) + [ba[1], ba[0]]
    caps += _fill(bm, join_loop, lambda p: Vector((p.y, p.z)))
    # the top under the lawn
    top_loop = [cols[k][-1] for k in range(jf, jb + 1)] + [ta[1], ta[0]]
    P2 = [_v2(v.co) for v in top_loop]
    st = _steiner(P2, 2.3, 0.7, 46300 + sx)
    top_f = _fill(bm, top_loop, lambda p: Vector((p.x, p.y)), st, lambda q: Vector((q.x, q.y, zt(q.x, q.y))))
    _beautify(bm, top_f)
    # the flat bottom
    bot_loop = [c[0] for c in cols]
    P2 = [_v2(v.co) for v in bot_loop]
    bot_f = _fill(bm, bot_loop, lambda p: Vector((p.x, p.y)), _steiner(P2, 4.5, 1.2, 46310 + sx),
                  lambda q: Vector((q.x, q.y, 0.0)))
    _beautify(bm, bot_f)
    for f in caps + top_f + bot_f:
        if f.is_valid:
            f[lay] = 0
    _tri(bm, [f for f in walls if f.is_valid])
    vs = [v for v in bm.verts if v not in before]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, ROCK, tint=1.0)
    _paint_rock(a, vs, lay, 46320 + sx)
    MASS_INFO[sx] = {"tris": sum(len(f.verts) - 2 for f in _faces(vs)), "chain": n_}
    return vs


COL_TINT = [1.02, 0.97, 1.03, 0.985, 1.02, 0.97, 1.01, 0.98, 1.03, 0.99, 1.0, 1.02]


def _paint_rock(a, vs, lay, seed, top_fn=None):
    """Stone by position only (spec 5.5): lighter in the upper part of each column (by height under its own top),
    broad deeper patches in the lowest 1.5 studs, a noise drift, per-column Tint. Hidden caps plain stone."""
    nf = K.noise_field(scale=0.2, seed=seed)
    by = {}
    fs = _faces(vs)
    tops = {}
    for f in fs:
        b = f[lay]
        if b:
            tops[b] = max(tops.get(b, 0.0), max(v.co.z for v in f.verts))
    for f in fs:
        b = f[lay]
        c = f.calc_center_median()
        if not b:
            f.material_index = a._mi(ROCK)
            continue
        top = tops[b]
        t = 0.4 * _clamp((c.z - 0.6 * top) / (0.4 * top)) + 0.08 * nf(c)
        if c.z < 1.5 and nf(c) > -0.05:
            key = _mix(ROCK, ROCK_DEEP, 0.15)
        elif t >= 0.05:
            key = _mix(ROCK, ROCK_LIGHT, t, step=0.1)
        else:
            key = ROCK
        f.material_index = a._mi(key)
        by.setdefault(b, []).append(f)
    for b, cf in by.items():
        _mottle(a, cf, 0.04, 0.3, seed + b, tint=COL_TINT[b % len(COL_TINT)])


# ---- the span -----------------------------------------------------------------------------------------------------------
# fix round 1 (finding 5): four big rounded boulder lumps a face. The outer lumps gain rings at +-5.9 / +-4.15 (rounded
# flanks, not a tent); peaks bulge 0.85 x GZ 1.25 = 1.06 proud at z 10, creases 0.5-0.55 x 1.25 = 0.6-0.7 in.
SPAN_X = (-6.75, -5.9, -5.0, -4.15, -3.35, -2.3, -1.85, -1.2, 0.0, 1.2, 1.85, 2.3, 3.35, 4.15, 5.0, 5.9, 6.75)
SEAT_Z = 7.98
ZB = [(0.0, 9.4), (1.2, 8.7), (1.85, 8.3), (2.3, SEAT_Z)]
YF = [(7.9, 5.15), (10.0, 5.05), (11.8, 4.72), (13.4, 4.3)]
GZ = [(7.9, 0.3), (10.0, 1.25), (11.8, 1.05), (13.4, 0.35)]
BUMP_F = {-5.9: 0.52, -5.0: 0.86, -4.15: 0.6, -3.35: -0.52, -2.3: 0.42, -1.85: 0.68, -1.2: 0.84, 0.0: -0.5,
          1.2: 0.8, 1.85: 0.66, 2.3: 0.4, 3.35: -0.55, 4.15: 0.56, 5.0: 0.88, 5.9: 0.5}
BUMP_B = {-5.9: 0.62, -5.0: 0.82, -4.15: 0.42, -3.35: -0.5, -2.3: 0.5, -1.85: 0.74, -1.2: 0.62, 0.0: -0.55,
          1.2: 0.6, 1.85: 0.84, 2.3: 0.62, 3.35: -0.52, 4.15: 0.44, 5.0: 0.8, 5.9: 0.64}
SPAN_INFO = {}


def _ledge_edge(sx, sy):
    """The seat ledge's outer edge at z 8.0 on one face (sy -1 front, +1 back) of one mass: [(|x|, |y|)] sorted."""
    g = mass_geo(sx)
    pts = []
    for k, c in enumerate(g["chain"]):
        if c["zone"] == "hz" or k in (g["jf"], g["jb"]):
            for p in c["col"]:
                if abs(p.z - LEDGE_Z) < 1e-6 and p.y * sy > 0:
                    pts.append((abs(p.x), abs(p.y)))
    return sorted(pts)


def _ledge_need(ax, sy, lo, hi):
    """How far out (|y|) the span's bottom edge must reach over |x| in [lo, hi] to hide the ledge (finding 9)."""
    need = 0.0
    for sx in (-1, 1):
        E = _ledge_edge(sx, sy)
        for (x0, y0), (x1, y1) in zip(E, E[1:]):
            for t in np.linspace(0, 1, 9):
                x = x0 + (x1 - x0) * t
                if lo - 1e-6 <= x <= hi + 1e-6:
                    need = max(need, y0 + (y1 - y0) * t)
    return need + 0.07 if need else 0.0


def span_rings():
    """Per ring (x): 10 points: front bottom, front 10.0, front 11.8, front top, back top, back 11.8,
    back 10.0, back bottom, bottom back (+1.8), bottom front (-1.8)."""
    rng = random.Random(46401)
    rings = []
    for x in SPAN_X:
        ax = abs(x)
        if ax > 6.7:
            sx = 1 if x > 0 else -1
            g = mass_geo(sx)
            jf = g["chain"][g["jf"]]["col"][3:]
            jb = g["chain"][g["jb"]]["col"][3:]
            front = [Vector((x, p.y + 0.03, SEAT_Z if k == 0 else p.z)) for k, p in enumerate(jf)]
            back = [Vector((x, p.y - 0.03, SEAT_Z if k == 0 else p.z)) for k, p in enumerate(jb)]
            zb = SEAT_Z
            ub = [Vector((x, 1.8, SEAT_Z)), Vector((x, -1.8, SEAT_Z))]
        else:
            zb = _pl(ZB, ax) if ax < 2.3 else SEAT_Z
            soffit = ax < 2.3
            front, back = [], []
            for side, bump in ((-1, BUMP_F[x]), (1, BUMP_B[x])):
                pts = []
                for k, z in enumerate((zb, 10.0, 11.8, None)):
                    if z is None:
                        y = YF[-1][1] - 0.05 + bump * _pl(GZ, 13.0) + rng.uniform(-0.04, 0.04)
                        z = zt(x, y)
                    else:
                        y = _pl(YF, z) + bump * _pl(GZ, z) + rng.uniform(-0.05, 0.05)
                        if k == 0 and soffit:
                            z = zb + (rng.uniform(0.02, 0.08) if ax < 0.01 else rng.uniform(-0.06, 0.06))
                        if k == 0 and ax >= 2.29:
                            # the bottom edge reaches past the ledge's outer edge (no flat seat sliver shows)
                            i = SPAN_X.index(x)
                            y = max(y, _ledge_need(ax, side, min(abs(SPAN_X[i - 1]), abs(SPAN_X[i + 1])),
                                                   max(abs(SPAN_X[i - 1]), abs(SPAN_X[i + 1]))))
                    pts.append(Vector((x, side * y, z)))
                (front if side < 0 else back).extend(pts)
            ub = [Vector((x, 1.8, zb + (rng.uniform(-0.12, 0.12) if soffit and ax > 0.01 else
                                        rng.uniform(0.04, 0.12) if soffit else 0.0))),
                  Vector((x, -1.8, zb + (rng.uniform(-0.12, 0.12) if soffit and ax > 0.01 else
                                         rng.uniform(0.04, 0.12) if soffit else 0.0)))]
        rings.append(front + list(reversed(back)) + ub)
    return rings


def span(a):
    """The top span as ONE closed shell (decision 6)."""
    bm = a.bm
    before = set(bm.verts)
    lay = bm.faces.layers.int.get("m046_band") or bm.faces.layers.int.new("m046_band")
    R = span_rings()
    V = [[bm.verts.new(p) for p in r] for r in R]
    m_ = len(R[0])
    fs = []
    for i in range(len(V) - 1):
        mid = 0.5 * (SPAN_X[i] + SPAN_X[i + 1])
        lump = 0 if mid < -3.35 else 1 if mid < 0 else 2 if mid < 3.35 else 3
        for k in range(m_):
            if k == 3:                          # the top (front top -> back top) is one CDT cap below
                continue
            l = (k + 1) % m_
            f = bm.faces.new((V[i][k], V[i + 1][k], V[i + 1][l], V[i][l]))
            f[lay] = 200 + lump
            fs.append(f)
    ends = []
    for r in (V[0], V[-1]):
        ends += _fill(bm, r, lambda p: Vector((p.y, p.z)))
    # the top under the lawn: a CDT over the front and back top points with interior points on the dome
    loop = [r[3] for r in V] + [r[4] for r in reversed(V)]
    P2 = [_v2(v.co) for v in loop]
    top = _fill(bm, loop, lambda p: Vector((p.x, p.y)), _steiner(P2, 2.2, 0.8, 46402),
                lambda q: Vector((q.x, q.y, zt(q.x, q.y))))
    top_vs = [v for f in top for v in f.verts]
    _beautify(bm, top)
    top = list({f for v in top_vs for f in v.link_faces if f.is_valid and f not in fs})
    for f in ends + top:
        if f.is_valid:
            f[lay] = 0
    _tri(bm, fs)
    vs = [v for r in V for v in r] + top_vs
    vs = list(dict.fromkeys(vs))
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, ROCK, tint=1.0)
    _paint_span(a, vs, lay)
    SPAN_INFO["tris"] = sum(len(f.verts) - 2 for f in _faces(vs))
    return vs


def _paint_span(a, vs, lay):
    nf = K.noise_field(scale=0.22, seed=46410)
    by = {}
    for f in _faces(vs):
        b = f[lay]
        c = f.calc_center_median()
        if not b or c.z < SEAT_Z + 0.05:
            f.material_index = a._mi(ROCK)          # hidden seats and end faces
            continue
        if abs(c.x) < 2.35 and c.z < 9.8 and abs(c.y) < 4.9:
            key = _mix(ROCK, ROCK_DEEP, 0.1) if nf(c) > 0.1 else ROCK      # the soffit: plain stone
        else:
            t = 0.4 * _clamp((c.z - 10.6) / 2.4) + 0.08 * nf(c)
            key = _mix(ROCK, ROCK_LIGHT, t, step=0.1) if t >= 0.05 else ROCK
        f.material_index = a._mi(key)
        by.setdefault(b, []).append(f)
    for b, cf in by.items():
        _mottle(a, cf, 0.04, 0.3, 46420 + b, tint=COL_TINT[(b + 5) % len(COL_TINT)])


# ---- lawn caps ----------------------------------------------------------------------------------------------------------
OV_SEAM = 0.16             # fix round 1 (finding 6): the lip overhangs <= 0.2 and drops 0.25-0.35 below the rim
LIP_IN = 0.15               # the lawn's top edge stands this far outside the rock rim; the lip slopes out and down to O


SEAM_LAP = 0.015            # each cap reaches this far past x = +-6.7 into its neighbour (the kit merges coincident verts)


def _seam(sx, which, span_side):
    """A seam point of the lawn caps near x = sx * 6.7: (O xy, z bottom, z top). The span cap's seam sits SEAM_LAP
    outboard of 6.7 and the mass cap's SEAM_LAP inboard, so the two overlap 0.03 (no crack, no merged verts)."""
    g = mass_geo(sx)
    x = sx * (JOINT_X + (SEAM_LAP if span_side else -SEAM_LAP))
    if which in ("mid", "fq", "bq"):
        o = Vector((x, {"mid": 0.0, "fq": -3.3, "bq": 3.3}[which]))
        z = zt(o.x, o.y)
        return o, z - 0.1, z + LAWN_T, o
    J = g["chain"][g["jf" if which == "front" else "jb"]]["col"][-1]
    sy = -1.0 if which == "front" else 1.0
    o = Vector((x, J.y + sy * OV_SEAM))
    tp = Vector((x, J.y + sy * LIP_IN))
    return o, J.z - 0.3, max(zt(tp.x, tp.y) + 0.22, J.z + 0.16), tp


def cap_entries(part):
    """[(kind, R or None, seam tuple or None)] round a cap: ring points (rock top ring) and seam points."""
    E = []
    if part == "span":
        R = span_rings()
        E.append(("seam", None, _seam(-1, "front", True)))
        for r in R[1:-1]:
            E.append(("ring", r[3], None))
        E += [("seam", None, _seam(1, w, True)) for w in ("front", "fq", "mid", "bq", "back")]
        for r in reversed(R[1:-1]):
            E.append(("ring", r[4], None))
        E += [("seam", None, _seam(-1, w, True)) for w in ("back", "bq", "mid", "fq")]
    else:
        sx = 1 if part == "R" else -1
        g = mass_geo(sx)
        E.append(("seam", None, _seam(sx, "front", False)))
        for k in range(g["jf"] + 1, g["jb"]):
            E.append(("ring", g["chain"][k]["col"][-1], None))
        E += [("seam", None, _seam(sx, w, False)) for w in ("back", "bq", "mid", "fq")]
    return E


def cap_outline(part, seed):
    """The cap outline O: ring points pushed out (0.24-0.38, scalloped) along the ring's outward normal; seam points
    as given. Returns [(O xy, z bottom, z top, R or None)]."""
    rng = random.Random(seed)
    E = cap_entries(part)
    P = [e[1].xy if e[0] == "ring" else e[2][0] for e in E]
    ccw = _area2(P) > 0
    out = []
    n_ = len(E)
    for i, (kind, R, sm) in enumerate(E):
        if kind == "seam":
            out.append((sm[0], sm[1], sm[2], None, sm[3]))
            continue
        # a miter offset (fix round 1): the outline's edges stand parallel to the rim's at the offset, so every rim
        # point stays inside even at the sharper scallops of the two-facet columns
        t1 = (P[i] - P[i - 1]).normalized()
        t2 = (P[(i + 1) % n_] - P[i]).normalized()
        n1 = Vector((t1.y, -t1.x)) if ccw else Vector((-t1.y, t1.x))
        n2 = Vector((t2.y, -t2.x)) if ccw else Vector((-t2.y, t2.x))
        nrm = (n1 + n2).normalized()
        k = 1.0 / max(0.5, nrm.dot(n1))
        o = R.xy + nrm * rng.uniform(0.15, 0.19) * k
        tp = R.xy + nrm * LIP_IN * k
        zb = R.z - rng.uniform(0.25, 0.35)
        ztp = max(zt(tp.x, tp.y) + 0.22 + rng.uniform(-0.03, 0.03), R.z + 0.16)
        out.append((o, zb, ztp, R, tp))
    return out


CAP_INFO = {}


def _inner_ring(P, d, spacing):
    """Points d inside a closed outline (along each point's inward normal), thinned to >= spacing apart and kept only
    where they lie inside with >= 0.6 clearance: the lawn's edge rounds over between the rim and this ring."""
    ccw = _area2(P) > 0
    n_ = len(P)
    out = []
    for i in range(n_):
        t = (P[(i + 1) % n_] - P[i - 1])
        if t.length < 1e-6:
            continue
        t.normalize()
        nin = Vector((-t.y, t.x)) if ccw else Vector((t.y, -t.x))
        q = P[i] + nin * d
        if _inside(q, P) and _poly_d(q, P) > 0.6 and all((q - r).length >= spacing for r in out):
            out.append(q)
    if len(out) > 1 and (out[0] - out[-1]).length < spacing:
        out.pop()
    return out


def lawn_cap(a, part, seed):
    """One closed lawn cap (decision 8): lip walls round the outline, a domed top (CDT with interior points, 14.0 in
    the middle), an underside that dips below the rock rim all round (so no crack shows between lawn and rock)."""
    bm = a.bm
    before = set(bm.verts)
    O = cap_outline(part, seed)
    cols = [(bm.verts.new((o.x, o.y, zb)), bm.verts.new((tp.x, tp.y, ztp))) for o, zb, ztp, R, tp in O]
    n_ = len(cols)
    walls = []
    for i in range(n_):
        j = (i + 1) % n_
        walls.append(bm.faces.new((cols[i][0], cols[j][0], cols[j][1], cols[i][1])))
    P2 = [o for o, zb, ztp, R, tp in O]
    T2 = [tp for o, zb, ztp, R, tp in O]
    nf = K.noise_field(scale=0.35, seed=seed)
    ring = _inner_ring(T2, 0.95, 2.0)
    if part != "span":
        # support points where the walkable lawn meets the shoulders (x +-7.0 .. 7.6), so the CDT top holds >= 13.6
        # over the central 14 x 6 (fix round 1: the two-facet columns left a coarser rim ring)
        sx = 1 if part == "R" else -1
        for q in (Vector((sx * 7.05, -3.05)), Vector((sx * 7.05, 3.05)), Vector((sx * 7.1, 0.0))):
            if _inside(q, T2) and _poly_d(q, T2) > 0.35 and all((q - r).length > 0.7 for r in ring):
                ring.append(q)
    top_f = _fill(bm, [c[1] for c in cols], lambda p: Vector((p.x, p.y)), ring + _steiner(T2, 2.4, 1.75, seed + 1),
                  lambda q: Vector((q.x, q.y, zt(q.x, q.y) + LAWN_T + 0.06 * nf(Vector((q.x, q.y, 0))))))
    _beautify(bm, top_f)
    bot_f = _fill(bm, [c[0] for c in cols], lambda p: Vector((p.x, p.y)),
                  _inner_ring(P2, 1.1, 1.9) + _steiner(P2, 3.6, 2.2, seed + 2),
                  lambda q: Vector((q.x, q.y, zt(q.x, q.y) - 0.08)))
    _beautify(bm, bot_f)
    _tri(bm, walls)
    vs = [v for v in bm.verts if v not in before]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, GRASS, tint=1.0)
    _paint_lawn(a, vs, seed)
    CAP_INFO[part] = {"tris": sum(len(f.verts) - 2 for f in _faces(vs)), "outline": n_,
                      "top_z_max": round(max(v.co.z for v in vs), 3)}
    return vs


ROOTS = []      # (x, y, r): bush roots; the lawn deepens round them


def _paint_lawn(a, vs, seed, apron=False):
    """One lawn colour by position: broad lighter patches by a noise field (vertex values averaged per face, so the
    patches follow no triangle), deeper round the bush roots. Never by facing."""
    nf = K.noise_field(scale=0.25, seed=46500)          # one field for every cap: no colour step at the seams
    fs = _faces(vs)
    for f in fs:
        c = f.calc_center_median()
        v = sum(nf(p.co) for p in f.verts) / len(f.verts)
        near = min([math.hypot(c.x - x, c.y - y) - r for x, y, r in ROOTS] or [9.0])
        if near < 0.0:
            key = _mix(GRASS, GRASS_DEEP, 0.25)
        elif near < 0.8:
            key = _mix(GRASS, GRASS_DEEP, 0.1)
        elif v > 0.28:
            key = _mix(GRASS, GRASS_LIGHT, 0.2)
        elif v > 0.12:
            key = _mix(GRASS, GRASS_LIGHT, 0.1)
        else:
            key = GRASS
        f.material_index = a._mi(key)
    _mottle(a, fs, 0.04, 0.4, seed)


def _slab(a, poly, z0, z1, key, top_fn=None, steiner=None, bevel=0.0):
    """A closed flat slab over a 2D polygon (aprons, ledge pads, tunnel strips); bevel insets the top outline so a
    thin slab's edge is a sloped band, not a sliver wall."""
    bm = a.bm
    P = [Vector(p) for p in poly]
    if _area2(P) < 0:
        P.reverse()
    Q = _inset(P, bevel) if bevel else P
    lo = [bm.verts.new((p.x, p.y, z0)) for p in P]
    hi = [bm.verts.new((p.x, p.y, top_fn(p) if top_fn else z1)) for p in Q]
    n_ = len(P)
    fs = []
    for i in range(n_):
        j = (i + 1) % n_
        fs.append(bm.faces.new((lo[i], lo[j], hi[j], hi[i])))
    top = _fill(bm, hi, lambda p: Vector((p.x, p.y)), steiner or (), lambda q: Vector((q.x, q.y, top_fn(q) if top_fn
                                                                                       else z1)))
    _beautify(bm, top)
    bot = _fill(bm, lo, lambda p: Vector((p.x, p.y)))
    _beautify(bm, bot)
    _tri(bm, fs)
    vs = lo + hi + [v for f in top for v in f.verts if v not in hi]
    vs = list(dict.fromkeys(vs))
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, key)
    return vs


# ---- skirts, foot boulders ----------------------------------------------------------------------------------------------
ROCK_INFO = {}
# name: (centre, w (along the face), d, h, yaw deg (the face's tangent), seed, pad)
SKIRTS = {
    "SK_L1": ((-7.9, -5.75), 3.2, 1.7, 4.8, 0, 46601, True),
    "SK_L2": ((-10.75, -4.75), 2.8, 1.7, 4.3, -42, 46602, True),
    # fix round 1 (finding 3): the end skirts are lower, pitched, with no perched pad bush (no "potted plant on a spike")
    "SK_L3": ((-11.85, -0.6), 3.2, 1.7, 3.5, 90, 46603, False),
    "SK_L4": ((-8.7, 5.75), 3.2, 1.7, 4.6, 0, 46604, False),
    "SK_R1": ((10.85, -4.8), 3.0, 1.7, 4.4, 42, 46611, True),
    "SK_R2": ((11.85, 1.3), 3.0, 1.7, 3.4, 90, 46612, False),
    "SK_R3": ((8.5, 5.75), 3.2, 1.7, 4.8, 0, 46613, False),
    "SK_R4": ((5.35, 5.75), 2.6, 1.6, 4.0, 0, 46614, False),
}
# name: (centre, w, d, h, seed)
BOULDERS = {
    "B_L1": ((-5.35, -5.85), 1.8, 1.5, 1.9, 46621),
    "B_L2": ((-11.75, 3.3), 2.4, 1.9, 2.4, 46622),
    "B_L3": ((-5.3, 5.85), 2.0, 1.6, 2.0, 46623),
    "B_L4": ((-10.6, 5.35), 2.3, 1.8, 2.3, 46624),
    "B_R1": ((6.55, -5.8), 2.8, 2.0, 3.1, 46631),
    "B_R2": ((9.15, -5.75), 2.3, 1.8, 2.3, 46632),
    "B_R3": ((11.0, 4.6), 2.4, 1.9, 2.4, 46633),
    "B_R4": ((12.0, -2.3), 2.1, 1.7, 2.1, 46634),
}
PADS = {}


def _min_deg(vs):
    return min(math.degrees(m011._fmin(f)) for f in _faces(vs))


def _retry(a, build, seed, tries=6):
    """Build a hull piece, and rebuild it with the next seed while any of its faces has a corner under 5 degrees."""
    for k in range(tries):
        vs = build(seed + 100 * k)
        if _min_deg(vs) >= POLISH_LIM + 0.2 or k == tries - 1:
            return vs
        bmesh.ops.delete(a.bm, geom=[v for v in vs if v.is_valid], context="VERTS")


def skirt(a, name, c, w, d, h, yaw, seed, pad):
    return _retry(a, lambda sd: _skirt(a, name, c, w, d, h, yaw, sd, pad), seed)


def boulder(a, name, c, w, d, h, seed):
    return _retry(a, lambda sd: _boulder(a, name, c, w, d, h, sd), seed)


def _skirt(a, name, c, w, d, h, yaw, seed, pad):
    """A tall chunky skirt block leaning on the columns (spec 1.4): a 6-sided foot, the widest ring at 0.3 h, a
    shoulder ring at 0.72 h, a pitched ridge top (two points) or, for a ledge pad, a small flat crown (<= 1.2)."""
    rng = random.Random(seed)
    yr = math.radians(yaw)
    cx, cy = c

    def ring(sc, z, n=5, jit=0.06, ph=0.0):
        out = []
        for k in range(n):
            ang = ph + 2 * math.pi * k / n + rng.uniform(-0.1, 0.1)
            lx = math.cos(ang) * w / 2 * sc * (1 + rng.uniform(-jit, jit))
            ly = math.sin(ang) * d / 2 * sc * (1 + rng.uniform(-jit, jit))
            out.append(Vector((cx + lx * math.cos(yr) - ly * math.sin(yr), cy + lx * math.sin(yr) + ly * math.cos(yr),
                               z + rng.uniform(-0.05, 0.05) * h)))
        return out
    pts = ring(0.92, 0.0, ph=0.3)
    for p in pts:
        p.z = 0.0
    pts += ring(1.05, 0.32 * h, ph=0.6)
    pts += ring(0.82, 0.68 * h, n=4, ph=0.4)
    if pad:
        crown = ring(0.36, h, n=4, jit=0.03, ph=0.4)
        for p in crown:
            p.z = h
        pts += crown
    else:
        for s in (-1, 1):
            lx = s * 0.28 * w
            pts.append(Vector((cx + lx * math.cos(yr), cy + lx * math.sin(yr), h + rng.uniform(-0.1, 0.1))))
    vs = _hull_piece(a, pts, ROCK)
    nf = K.noise_field(scale=0.3, seed=seed)
    for f in _faces(vs):
        cc = f.calc_center_median()
        f.material_index = a._mi(_mix(ROCK, ROCK_DEEP, 0.15) if cc.z < 1.4 and nf(cc) > -0.05 else
                                 _mix(ROCK, ROCK_LIGHT, 0.3) if cc.z > 0.72 * h else
                                 _mix(ROCK, ROCK_LIGHT, 0.1) if cc.z > 0.4 * h else ROCK)
    _mottle(a, _faces(vs), 0.04, 0.4, seed, tint=rng.uniform(0.97, 1.03))
    ROCK_INFO[name] = {"tris": sum(len(f.verts) - 2 for f in _faces(vs)), "h": round(max(v.co.z for v in vs), 2)}
    if pad:
        top = [v for v in vs if v.co.z > h - 0.02]
        PADS[name] = (Vector((cx, cy)), [v.co.copy() for v in top], h)
    return vs


def _boulder(a, name, c, w, d, h, seed):
    """A faceted foot boulder (a chunky gem, not an egg): 5-sided foot, the widest ring at 0.42 h, a 4-point crown
    ring at 0.8 h (>= 0.5 W) and an off-centre apex (a pitched 3-4-facet crown)."""
    rng = random.Random(seed)
    cx, cy = c
    # the long axis along the face it stands against (front / back: x, ends: y), turned a little
    yr = (0.0 if abs(cy) > 4.5 else math.pi / 2) + rng.uniform(-0.3, 0.3)

    def ring(sc, z, n, ph):
        out = []
        for k in range(n):
            ang = ph + 2 * math.pi * k / n + rng.uniform(-0.12, 0.12)
            lx = math.cos(ang) * w / 2 * sc * rng.uniform(0.92, 1.05)
            ly = math.sin(ang) * d / 2 * sc * rng.uniform(0.92, 1.05)
            out.append(Vector((cx + lx * math.cos(yr) - ly * math.sin(yr), cy + lx * math.sin(yr) + ly * math.cos(yr),
                               z)))
        return out
    pts = ring(0.86, 0.0, 5, 0.0)
    pts += [p + Vector((0, 0, rng.uniform(-0.08, 0.08) * h)) for p in ring(1.0, 0.42 * h, 5, 0.6)]
    pts += [p + Vector((0, 0, rng.uniform(-0.05, 0.05) * h)) for p in ring(0.64, 0.8 * h, 3, 0.2)]
    pts.append(Vector((cx + rng.uniform(-0.12, 0.12) * w, cy + rng.uniform(-0.12, 0.12) * d, h)))
    vs = _hull_piece(a, pts, ROCK)
    for f in _faces(vs):
        cc = f.calc_center_median()
        f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.3) if cc.z > 0.78 * h else
                                 _mix(ROCK, ROCK_LIGHT, 0.1) if cc.z > 0.45 * h else
                                 _mix(ROCK, ROCK_DEEP, 0.15) if cc.z < 0.25 * h else ROCK)
    _mottle(a, _faces(vs), 0.04, 0.6, seed, tint=rng.uniform(0.97, 1.04))
    xs, ys = [v.co.x for v in vs], [v.co.y for v in vs]
    ROCK_INFO[name] = {"tris": sum(len(f.verts) - 2 for f in _faces(vs)),
                       "h_over_w": round(h / max(max(xs) - min(xs), max(ys) - min(ys)), 2)}
    return vs


def pad(a, name, seed):
    """A lime ledge pad over a skirt's flat crown (overhanging 0.15)."""
    c, top, h = PADS[name]
    P = [p.xy for p in top]
    cen = sum(P, Vector((0, 0))) / len(P)
    P.sort(key=lambda p: math.atan2(p.y - cen.y, p.x - cen.x))
    P = [p + (p - cen).normalized() * 0.3 for p in P]
    return _slab(a, P, h - 0.06, h + 0.13, GRASS)


# ---- the sill ------------------------------------------------------------------------------------------------------------
FLOOR_TOP = 0.4
SILL_PIECES = [
    ([(-5.8, -6.8), (5.8, -6.8), (3.7, -4.8), (-3.7, -4.8)], [(-3.9, -6.0), (0.1, -5.9), (3.9, -5.95)]),
    ([(-3.7, -4.8), (3.7, -4.8), (3.7, 4.8), (-3.7, 4.8)],
     [(-1.9, -3.1), (1.8, -2.9), (-1.7, 0.4), (2.0, 0.9), (-1.3, 3.6), (2.2, 3.7)]),
    ([(-3.7, 4.8), (3.7, 4.8), (5.8, 6.8), (-5.8, 6.8)], [(-3.6, 5.9), (0.0, 5.8), (4.0, 5.95)]),
]
SILL_INFO = {}


def _clip(poly, a_, b_):
    """Keep the side of the half-plane nearer seed a_ than seed b_ (Sutherland-Hodgman)."""
    m = (a_ + b_) / 2
    n = (b_ - a_)
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        dp, dq = (p - m).dot(n), (q - m).dot(n)
        if dp <= 0:
            out.append(p)
        if dp * dq < 0:
            out.append(p + (q - p) * (dp / (dp - dq)))
    return out


def tile_polys():
    rng = random.Random(46701)
    out = []
    for poly, seeds in SILL_PIECES:
        P = [Vector(p) for p in poly]
        S = [Vector((x + rng.uniform(-0.15, 0.15), y + rng.uniform(-0.1, 0.1))) for x, y in seeds]
        for i, s in enumerate(S):
            cell = list(P)
            for j, t in enumerate(S):
                if i != j:
                    cell = _clip(cell, s, t)
            out.append(_inset(_clean(cell), 0.025))                          # seams about 0.05
    return out


def _clean(P, short=0.35, straight=158.0):
    """Drop corners closer than `short` to the previous one and corners straighter than `straight` degrees (they
    would make sliver triangles)."""
    P = [Vector(p) for p in P]
    changed = True
    while changed and len(P) > 3:
        changed = False
        for i in range(len(P)):
            a_, b_, c_ = P[i - 1], P[i], P[(i + 1) % len(P)]
            u, v = a_ - b_, c_ - b_
            if u.length < short or (u.length > 1e-9 and v.length > 1e-9 and
                                    math.degrees(u.angle(v)) > straight):
                P.pop(i)
                changed = True
                break
    return P


def _inset(P, d):
    """Offset a convex-ish polygon inward by d (miter)."""
    ccw = _area2(P) > 0
    out = []
    n_ = len(P)
    for i in range(n_):
        a_, b_, c_ = P[i - 1], P[i], P[(i + 1) % n_]
        t1, t2 = (b_ - a_).normalized(), (c_ - b_).normalized()
        n1 = Vector((-t1.y, t1.x)) if ccw else Vector((t1.y, -t1.x))
        n2 = Vector((-t2.y, t2.x)) if ccw else Vector((t2.y, -t2.x))
        m = (n1 + n2).normalized()
        out.append(b_ + m * d / max(0.4, m.dot(n1)))
    return out


def tile(a, poly, seed):
    """One flagstone: a closed slab, its top at 0.40 +- 0.02. (No top bevel ring: on the 2-4-stud tile edges a 0.06
    bevel band can only be built from sub-5-degree slivers; the darker sand band is the 0.4 side itself.)"""
    rng = random.Random(seed)
    bm = a.bm
    P = list(poly)
    if _area2(P) < 0:
        P.reverse()
    top = FLOOR_TOP + rng.uniform(-0.02, 0.02)
    lo = [bm.verts.new((p.x, p.y, 0.0)) for p in P]
    hi = [bm.verts.new((p.x, p.y, top)) for p in P]
    n_ = len(P)
    side = []
    for i in range(n_):
        j = (i + 1) % n_
        side.append(bm.faces.new((lo[i], lo[j], hi[j], hi[i])))
    tf = bm.faces.new(hi)
    bf = bm.faces.new(list(reversed(lo)))
    _tri(bm, side + [tf, bf])
    vs = lo + hi
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, FLOOR, tint=1.0)
    nf = K.noise_field(scale=0.4, seed=46710)
    tint = 1.0 + rng.uniform(-0.04, 0.04)
    for f in _faces(vs):
        c = f.calc_center_median()
        zs = [v.co.z for v in f.verts]
        if min(zs) > top - 0.01:            # the top: sand with broad deeper patches
            f.material_index = a._mi(_mix(FLOOR, FLOOR_DEEP, 0.1) if nf(c) > 0.3 else FLOOR)
        elif max(zs) < 0.01:                # the hidden bottom: plain sand
            f.material_index = a._mi(FLOOR)
        else:                               # the side band below the top edge (by role, its place in the tile)
            f.material_index = a._mi(FLOOR_DEEP)
    _mottle(a, _faces(vs), 0.03, 0.4, seed, tint=tint)
    return vs


def sill(a):
    out = []
    for i, p in enumerate(tile_polys()):
        out += tile(a, p, 46720 + i)
    SILL_INFO["tiles"] = len(tile_polys())
    return out


# ---- plants -------------------------------------------------------------------------------------------------------------
PLANT_INFO = {}
# dome tiers, crown first: (polar angle from the top in deg, count, azimuth phase in turns, length frac of R, width frac,
# outward flare)
# fix round 1 (finding 4): dense rounded clumps of 9-10 smaller leaves (0.62-0.74 R): a crown of 3-4 flat leaves and a
# ring of 4-6 upright side leaves (tips curled in). Leaves within 12 deg of edge-on from the f34 (e 18) are those tilted
# 6-60 deg, so crown leaves droop <= 1.5 deg and side leaves stand at -78 deg (axis up). (polar deg, count, phase,
# length / R, width / length, droop of the axis below horizontal in deg (negative: up), role 0 crown / 2 side)
TIERS = {
    "dark": ((30, 4, 0.0, 0.64, 1.0, 1.5, 0), (94, 6, 0.08, 0.64, 0.9, -78, 2)),
    "dark9": ((30, 3, 0.0, 0.68, 1.0, 1.5, 0), (94, 6, 0.08, 0.64, 0.9, -78, 2)),
    "small": ((32, 2, 0.0, 0.74, 1.0, 1.5, 0), (94, 4, 0.12, 0.7, 0.9, -78, 2)),
}
SURF = {"tree": None}       # BVH of the walkable surfaces (caps, apron, tiles, pads): leaves stay above them
ROCKTREE = {"tree": None}


def _surface_z(x, y, z_from=40.0):
    t = SURF["tree"]
    if t is None:
        return None
    h = t.ray_cast(Vector((x, y, z_from)), Vector((0, 0, -1)), 100)
    return h[0].z if h[0] is not None else None


def _keep_up(vs, slack=0.06):
    """Lift a leaf whose verts go more than `slack` under the surface below them (on sloped lawns)."""
    t = SURF["tree"]
    if t is None:
        return
    worst = 0.0
    for v in vs:
        h = t.ray_cast(Vector((v.co.x, v.co.y, v.co.z + 1.2)), Vector((0, 0, -1)), 3.0)
        if h[0] is not None:
            worst = max(worst, h[0].z - slack - v.co.z)
    if worst > 0:
        for v in vs:
            v.co.z += worst


class _Guard(m040._Guard):
    pass


# ---- rock containment by ray parity (fix round 1, the blocker) ------------------------------------------------------------
# m040._Guard judges "inside" by the nearest face's normal, which fails where a skirt or boulder is sunk into a core (the
# nearest surface is the skirt's outside while the point is deep in the core). These helpers test each closed rock shell
# on its own by ray parity, so a point is in the rock when it is inside any shell, its depth that shell's surface distance.
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


class _Rocks:
    """The rock as separate closed shells (span, cores, skirts, boulders), each with its bbox and BVH."""

    def __init__(self, shells):
        self.items = []
        for vs in shells:
            vs = [v for v in vs if v.is_valid]
            if not vs:
                continue
            co = [v.co for v in vs]
            lo = Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co)))
            hi = Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co)))
            self.items.append((lo, hi, _tree_of(vs)))

    @classmethod
    def from_trees(cls, items):
        r = cls([])
        r.items = items
        return r

    def depth(self, p):
        worst = 0.0
        for lo, hi, t in self.items:
            if not (lo.x - 1e-4 <= p.x <= hi.x + 1e-4 and lo.y - 1e-4 <= p.y <= hi.y + 1e-4 and
                    lo.z - 1e-4 <= p.z <= hi.z + 1e-4):
                continue
            if _parity_in(t, p):
                worst = max(worst, t.find_nearest(p)[3])
        return worst

    def piece_depth(self, vs):
        """The deepest point of a piece (its verts and face centres) inside the rock."""
        pts = [v.co for v in vs if v.is_valid] + [f.calc_center_median() for f in _faces(vs)]
        return max([self.depth(p) for p in pts] or [0.0])

    def clearance(self, x, y, zs):
        """Horizontal room round (x, y): the least distance to the rock over the heights zs (negative inside)."""
        best = 9.0
        for z in zs:
            p = Vector((x, y, z))
            for lo, hi, t in self.items:
                if p.z < lo.z - 0.05 or p.z > hi.z + 0.05:
                    continue
                q = t.find_nearest(p)
                if q[0] is None:
                    continue
                d = Vector((q[0].x - x, q[0].y - y)).length
                if lo.x <= x <= hi.x and lo.y <= y <= hi.y and _parity_in(t, p):
                    d = -d
                best = min(best, d)
        return best


ROCKS = {"set": None}


def bury_report(o):
    """Spec pitfall 13 / decision 7 on a finished object: every dressing shell (leaves, petals, flowers, pebbles,
    hearts) tested against every rock shell by ray parity; depth = distance to that rock shell's surface."""
    bm, ids, n = _shell_faces(o)
    keys = _keys(o)
    sk, sf = {}, {}
    for f in bm.faces:
        sk.setdefault(ids[f.index], set()).add(keys[f.material_index])
        sf.setdefault(ids[f.index], []).append(f)
    kinds = {k: _kind(v) for k, v in sk.items()}
    items = []
    for s, fs in sf.items():
        if kinds[s] != "rock":
            continue
        vs = list({v for f in fs for v in f.verts})
        idx = {v: i for i, v in enumerate(vs)}
        co = [v.co.copy() for v in vs]
        lo = Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co)))
        hi = Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co)))
        items.append((lo, hi, BVHTree.FromPolygons(co, [[idx[v] for v in f.verts] for f in fs])))
    rocks = _Rocks.from_trees(items)
    off = Vector(o[OFF]) if OFF in o else Vector()
    res = []
    for s, fs in sf.items():
        if kinds[s] not in ("leaf", "pebble", "trunk", "mixed"):
            continue
        pts = list({v.co.copy().freeze() for f in fs for v in f.verts}) + [f.calc_center_median() for f in fs]
        d = max(rocks.depth(Vector(p)) for p in pts)
        if d > 0.0:
            c = sum((f.calc_center_median() for f in fs), Vector()) / len(fs) + off
            res.append((round(d, 3), [round(x, 2) for x in c]))
    bm.free()
    res.sort(reverse=True)
    return {"over_0.05": sum(1 for d, _ in res if d > 0.05), "over_0.1": sum(1 for d, _ in res if d > 0.1),
            "over_0.2": sum(1 for d, _ in res if d > 0.2), "max": res[0][0] if res else 0.0, "worst": res[:6],
            "dressing_shells": sum(1 for k in kinds.values() if k in ("leaf", "pebble", "trunk", "mixed")),
            "rock_shells": len(items)}


def _cleaf(a, B, x, z, L, W, key, cup=0.16, curl=0.1, cam=0.09):
    """A broad rounded leaf (8 tris, closed; fix round 1): the blunt five-point outline of m043's leaves (widest at
    0.42 L, a two-corner blunt tip) from its stem B along x, its face toward z; the sides cup up, the tip curls in, a
    raised midrib point on top and a flat underside (the m043 leaf's under-point cost 2 tris that never show)."""
    bm = a.bm
    x = Vector(x).normalized()
    z = Vector(z) - x * Vector(z).dot(x)
    z = z.normalized() if z.length > 1e-6 else x.orthogonal().normalized()
    y = z.cross(x)
    B = Vector(B)

    def P(lx, ly, lz):
        t = lx / L
        return bm.verts.new(B + x * lx + y * ly + z * (lz + cup * abs(ly) - curl * L * t * t))
    o = [P(0, 0, 0), P(0.42 * L, -W / 2, 0), P(L, -0.22 * W, 0), P(L, 0.22 * W, 0), P(0.42 * L, W / 2, 0)]
    up = P(0.5 * L, 0, cam * L + curl * L * 0.25)
    fs = [bm.faces.new((o[i], o[(i + 1) % 5], up)) for i in range(5)]
    fs += [bm.faces.new((o[0], o[i + 1], o[i])) for i in (1, 2, 3)]     # the underside fanned from the stem
    vs = o + [up]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, key, tint=1.0)
    return vs


def _ground_fix(vs, z0):
    """Keep a leaf above the surface under it, and (for a plant on the ground) above z 0."""
    _keep_up(vs)
    if z0 < 0.5:
        zmin = min(v.co.z for v in vs)
        if zmin < 0.0:
            for v in vs:
                v.co.z -= zmin


def _rock_depth(vs):
    r = ROCKS["set"]
    return r.piece_depth(vs) if r is not None else 0.0


def _kill(a, vs):
    bmesh.ops.delete(a.bm, geom=[v for v in vs if v.is_valid], context="VERTS")


def bush(a, name, c, z0, R, H, kind, seed, guard=None):
    """A dense rounded clump (decision 10; fix round 1, finding 4): a hidden-in-plain-sight heart (foliage-coloured by
    height: fresh above, emerald below, never the soil colour), a ring of upright side leaves standing round it with
    their tips curled in over it (no hanging flap), and a crown of flat leaves fanning out from the dome's top (half
    sunk in the heart). Only near-flat (>= 84 deg normals) and near-upright leaves stay clear of edge-on at the f34's
    e 18, so the clump uses those two. Every leaf is placed (slid onto the heart, kept above the turf / ground) and
    THEN tested against every rock shell by ray parity; a leaf more than 0.05 in climbs the dome and, if it still cuts
    in, is dropped. A heart that cuts into the rock is narrowed."""
    rng = random.Random(seed)
    tint = 1.0 + rng.uniform(-0.04, 0.04)
    tiers = TIERS[kind]
    out = []
    if kind.startswith("dark"):
        keys = (_mix(LEAF, LEAF_LIT, 0.8), _mix(LEAF, LEAF_LIT, 0.2), _mix(LEAF, LEAF_DEEP, 0.45))
        heart = _mix(LEAF, LEAF_DEEP, 0.6)
    else:
        keys = (LEAF_LIT, _mix(LEAF_LIT, LEAF, 0.4), _mix(LEAF, LEAF_DEEP, 0.4))
        heart = _mix(LEAF, LEAF_DEEP, 0.5)
    C = Vector((c[0], c[1], z0 + 0.3 * H))
    rx, rz = 0.74 * R, 0.62 * H
    for _try in range(6):
        if kind.startswith("dark"):
            hvs = _dome_heart(a, C, rx, rz, z0 - 0.03 if z0 > 0.5 else 0.0, heart, seed + 1, n=3)
        else:                               # a small bush's heart: a 6-tri bipyramid
            hvs = _bipyramid(a, tuple(C), rx, rz, C.z - (z0 - 0.03 if z0 > 0.5 else 0.0), heart, seed + 1, n=3)
        if _rock_depth(hvs) <= 0.05:
            for f in _faces(hvs):           # the heart shows between the leaves: foliage, fresh above, deep below
                f.material_index = a._mi(_mix(LEAF, LEAF_LIT, 0.45) if f.calc_center_median().z > C.z + 0.3 * rz
                                         else heart)
            break
        if _try == 5:
            break
        _kill(a, hvs)                       # the heart cuts into the rock (a pad bush against its core): narrower
        rx *= 0.82
    out += hvs
    tree = _tree_of(hvs)
    off = rng.uniform(0, 2 * math.pi)
    nleaves, dropped, climbed = 0, 0, 0

    def place(t_deg, phi, lf, wf, droop, key, role):
        t = math.radians(t_deg)
        u = Vector((math.cos(phi), math.sin(phi), 0.0))
        P = C + u * (rx * math.sin(t)) + Vector((0, 0, rz * math.cos(t) * (1.0 if t < math.pi / 2 else 0.8)))
        d = math.radians(droop)
        x = u * math.cos(d) - Vector((0, 0, math.sin(d)))         # the leaf's axis: out (crown) or up (sides)
        flat = droop >= 0
        if flat:
            n = u * math.sin(d) + Vector((0, 0, math.cos(d)))     # a crown leaf lies flat, its face up
        else:
            n = (u - x * u.dot(x)).normalized()                   # a side leaf stands up, its face out
        L = R * lf
        vs = _cleaf(a, P - x * (0.45 * L if flat else 0.04 * L), x, n, L, L * wf, key, cup=0.0 if flat else 0.12,
                    curl=0.0 if flat else 0.16, cam=0.025 if flat else 0.08)
        _touch(vs, tree)
        _ground_fix(vs, z0)
        return vs

    for th, cnt, ph, lf, wf, droop, role in tiers:
        key = keys[role]
        for k in range(cnt):
            phi = off + 2 * math.pi * (k + ph) / cnt + rng.uniform(-0.18, 0.18)
            t_deg = th + rng.uniform(-4, 4)
            lfk = lf * rng.uniform(0.94, 1.06)
            while True:
                vs = place(t_deg, phi, lfk, wf, droop + rng.uniform(-1.5, 1.5), key, role)
                deep = _rock_depth(vs)
                if deep <= 0.05 or t_deg < 8:
                    break
                _kill(a, vs)            # it cuts into the rock: climb the dome and try again
                t_deg -= 10.0
                climbed += 1
            if deep > 0.05:
                _kill(a, vs)            # still in the rock at the crown: that side is the rock's; drop it
                dropped += 1
                continue
            out += vs
            nleaves += 1
    out = [v for v in out if v.is_valid]
    _mottle(a, _faces(out), 0.04, 0.9, seed, tint=tint)
    xs, ys, zs = ([v.co[i] for v in out] for i in range(3))
    PLANT_INFO[name] = {"centre": [round(c[0], 2), round(c[1], 2)], "z0": round(z0, 2),
                        "size": [round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2), round(max(zs) - z0, 2)],
                        "leaves": nleaves, "climbed": climbed, "dropped": dropped,
                        "rock_depth": round(_rock_depth(out), 3)}
    return out


def sprig(a, name, c, z0, R, n, seed, guard=None, buds=0):
    """3-4 rounded lime-green leaves from one root (stem ends sunk into the turf), optional yellow buds. Each leaf is
    tested against the rock by ray parity after placement and turned away (or dropped) if it cuts in."""
    rng = random.Random(seed)
    out = []
    y0 = rng.uniform(0, 2 * math.pi)
    tips = []
    for k in range(n):
        yaw = y0 + 2 * math.pi * k / n + rng.uniform(-0.25, 0.25)
        L = R * rng.uniform(0.85, 1.1)
        kk = _mix(LEAF_LIT, GRASS, 0.3) if k % 3 else LEAF_LIT
        pitch, roll = rng.uniform(0.55, 0.95), rng.uniform(-0.3, 0.3)
        vs = None
        for turn in (0.0, 0.6, -0.6, 1.2, -1.2, 1.8, -1.8):
            yw = yaw + turn
            rot = Matrix.Rotation(yw, 3, "Z") @ Matrix.Rotation(-pitch, 3, "Y") @ Matrix.Rotation(roll, 3, "X")
            base = (c[0] + math.cos(yw) * 0.04, c[1] + math.sin(yw) * 0.04, z0)
            vs = _cleaf(a, base, rot @ Vector((1, 0, 0)), rot @ Vector((0, 0, 1)), L, L * 0.8, kk, cup=0.2, curl=0.12,
                        cam=0.1)
            _ground_fix(vs, z0)
            if _rock_depth(vs) <= 0.05:
                break
            _kill(a, vs)
            vs = None
        if vs is None:
            continue
        tips.append((vs[2].co + vs[3].co) / 2)
        out += vs
    for k in range(min(buds, len(tips))):
        out += _bipyramid(a, tuple(tips[k]), 0.13, 0.12, 0.08, FLOWER, seed + 10 + k, n=4)
    _mottle(a, _faces(out), 0.04, 0.9, seed, tint=1.0 + rng.uniform(-0.04, 0.04))
    PLANT_INFO[name] = {"centre": [round(c[0], 2), round(c[1], 2)], "z0": round(z0, 2), "leaves": len(tips),
                        "buds": buds, "rock_depth": round(_rock_depth(out), 3)}
    return out


def flower(a, c, z0, r, seed):
    """A small five-petal yellow flower lying on the turf: a flat 5-point star bipyramid (sunk 0.03)."""
    rng = random.Random(seed)
    bm = a.bm
    off = rng.uniform(0, math.pi)
    ring = []
    for k in range(5):
        ang = off + k * 2 * math.pi / 5
        ring.append(bm.verts.new((c[0] + math.cos(ang) * r, c[1] + math.sin(ang) * r, z0 + 0.06)))
    top = bm.verts.new((c[0], c[1], z0 + 0.14))
    bot = bm.verts.new((c[0], c[1], z0 - 0.03))
    fs = []
    for k in range(5):
        j = (k + 1) % 5
        fs.append(bm.faces.new((ring[k], ring[j], top)))
        fs.append(bm.faces.new((ring[j], ring[k], bot)))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    vs = ring + [top, bot]
    a._finish(vs, FLOWER)
    return vs


def pebble(a, c, z0, s, seed, n=3):
    rng = random.Random(seed)
    vs = _prism(a, c, z0, z0 + s * rng.uniform(0.38, 0.5), s * 0.55, s * 0.36, PEBBLE, seed, n=n,
                sq=(1.0, rng.uniform(0.7, 0.9)))
    _mottle(a, _faces(vs), 0.03, 0.8, seed, tint=rng.uniform(0.96, 1.04))
    return vs


# ---- dressing (spec 2.4 / 2.5) -------------------------------------------------------------------------------------------
# bushes: name -> (centre, R, H, kind, seed, owner); owner span / L / R / hero
# fix round 1 (findings 1-4): rim bushes are smaller dense clumps (sheet: 2.4-2.8 across, 1.6-2.0 tall), the shoulder
# ones down the drape near x +-9.5 (spec 2.4); hero foot bushes give a DESIRED spot at the foot, which _foot_spot moves
# out onto the apron until the rock is at least FOOT_NEED x R away at every height of the bush.
BUSHES = {
    "S1": ((-4.4, -3.35), 1.85, 1.3, "dark9", 46801, "span"),
    "S2": ((-0.6, 3.25), 1.85, 2.35, "dark9", 46802, "span"),
    "S3": ((1.2, -3.45), 1.85, 2.35, "dark9", 46803, "span"),
    "S4": ((5.4, 2.75), 1.85, 1.3, "dark9", 46804, "span"),
    "L1": ((-9.3, -0.6), 1.45, 1.3, "dark9", 46805, "L"),
    "L2": ((-7.0, 2.7), 1.85, 1.3, "dark", 46806, "L"),
    "R1": ((7.3, -2.8), 1.85, 1.3, "dark", 46807, "R"),
    "R2": ((9.3, -0.5), 1.45, 1.3, "dark9", 46808, "R"),
    "J1": ((-6.3, -6.6), 1.75, 1.75, "dark9", 46809, "hero"),
    "F1": ((-10.3, -6.0), 1.5, 1.5, "small", 46811, "hero"),
    "F2": ((8.0, -6.5), 1.45, 1.45, "small", 46812, "hero"),
    "F4": ((-8.2, 6.5), 1.2, 1.35, "small", 46814, "hero"),
    "F5": ((7.1, 6.5), 1.2, 1.35, "small", 46815, "hero"),
    "F3": ((10.6, -6.0), 1.35, 1.35, "small", 46813, "hero"),
    "F8": ((-8.3, -6.9), 1.3, 1.3, "small", 46818, "hero"),
    "F9": ((-10.8, 5.9), 1.1, 1.25, "small", 46819, "hero"),
    "F10": ((9.9, 6.4), 1.1, 1.25, "small", 46820, "hero"),
}
FOOT_REACH = (13.0, 7.4)    # a hero foot bush shrinks (to 0.62 of its R at most) to keep its leaves inside |x|, |y|
FOOT_NEED = 0.7               # x R; the clump's leaves reach about 0.75 R, so they just meet the rock
# small bushes on the turfed skirt pads: skirt -> (name, R, H, kind, seed). Only the front-left corner skirt keeps a pad
# (the sheet's f34 ledge pads); the tall end skirts lost theirs (fix round 1, finding 3).
PAD_BUSHES = {"SK_L2": ("P1", 1.0, 1.2, "small", 46821), "SK_R1": ("P3", 0.95, 1.15, "small", 46823),
              "SK_L1": ("P2", 1.0, 1.2, "small", 46822)}
# sprigs: name -> (centre, R, n, seed, buds, owner); hero ones are desired spots (FOOT_NEED / 2 x R clear)
SPRIGS = {
    "SP1": ((-11.7, -3.9), 0.55, 3, 46831, 1, "hero"),
    "SP2": ((-3.4, -6.7), 0.5, 3, 46832, 1, "hero"),
    "SP4": ((9.8, -6.5), 0.55, 3, 46834, 1, "hero"),
    "SP3": ((-11.4, -5.4), 0.6, 3, 46833, 0, "hero"),
    "SP9": ((6.6, -7.0), 0.6, 3, 46839, 1, "hero"),
    "SP7": ((-12.6, 1.4), 0.55, 3, 46837, 0, "hero"),
    "SP8": ((12.6, -0.8), 0.55, 3, 46838, 1, "hero"),
    "SP5": ((-3.2, 2.0), 0.45, 3, 46835, 0, "tunnel"),
    "SP6": ((3.25, -1.4), 0.45, 3, 46836, 0, "tunnel"),
}
# pebbles: (centre, size, owner)
PEBBLES = [((-2.6, -2.2), 0.45, "span"), ((0.4, -0.8), 0.35, "span"), ((2.8, 1.2), 0.42, "span"),
           ((8.4, 0.2), 0.4, "R"), ((-8.4, -0.4), 0.4, "L"),
           ((-9.4, -6.4), 0.45, "hero"), ((10.4, -6.4), 0.42, "hero"),
           ((-2.8, -4.3), 0.3, "sill"), ((2.9, 3.6), 0.34, "sill"), ((2.4, -5.9), 0.3, "sill")]
# flowers: (centre, r, owner)
FLOWERS = [((-2.0, 1.1), 0.24, "span"), ((2.0, -1.6), 0.22, "span"), ((4.2, 0.4), 0.22, "hero"),
           ((-11.0, -6.0), 0.24, "hero"), ((-4.1, -6.5), 0.22, "hero"), ((6.9, -6.7), 0.24, "hero"),
           ((-12.6, -1.0), 0.22, "hero")]


def _roots():
    ROOTS[:] = [(x, y, R * 0.55) for (x, y), R, H, k, s, o in BUSHES.values()]


def _z_on(x, y, fallback=0.0, z_from=40.0):
    z = _surface_z(x, y, z_from)
    return fallback if z is None else z


def _foot_spot(x, y, R, H, need, z0=0.0, max_move=9.0):
    """Move a foot plant's centre out from the rock (horizontally, away from the nearest rock point) until the rock is
    at least `need` away at the heights 0.15 .. 0.85 H (fix round 1, the blocker: the bushes sat inside the cores)."""
    r = ROCKS["set"]
    p = Vector((x, y))
    if r is None:
        return p
    zs = (z0 + 0.15, z0 + 0.45 * H, z0 + 0.85 * H)
    p0 = p.copy()
    for _ in range(80):
        best = None
        for z in zs:
            P3 = Vector((p.x, p.y, z))
            for lo, hi, t in r.items:
                if z < lo.z - 0.05 or z > hi.z + 0.05:
                    continue
                q = t.find_nearest(P3)
                if q[0] is None:
                    continue
                d2 = Vector((q[0].x - p.x, q[0].y - p.y))
                inside = lo.x <= p.x <= hi.x and lo.y <= p.y <= hi.y and _parity_in(t, P3)
                dist = -d2.length if inside else d2.length
                if best is None or dist < best[0]:
                    best = (dist, d2, inside)
        if best is None or best[0] >= need:
            break
        dist, d2, inside = best
        if d2.length < 1e-6:
            away = Vector((p.x, p.y * 2.0)).normalized()
        else:
            away = d2.normalized() if inside else -d2.normalized()
        p = p + away * max(0.04, 0.5 * (need - dist))
        if (p - p0).length > max_move:
            p = p0 + (p - p0).normalized() * max_move
            break
    return p


def dressing(a, owners, guard=None):
    """The listed owners' dressing (span / L / R / sill / hero / tunnel), every piece its own closed shell set into
    the surface under it (ray-cast). Hero foot plants are moved out onto the apron first (_foot_spot); every leaf is
    checked against the rock by ray parity after its final placement (bush, sprig)."""
    for nm, ((x, y), R, H, kind, seed, owner) in BUSHES.items():
        if owner in owners:
            if owner == "hero":
                R0 = R
                while True:
                    p = _foot_spot(x, y, R, H, FOOT_NEED * R)
                    if (abs(p.x) + 0.75 * R <= FOOT_REACH[0] and abs(p.y) + 0.75 * R <= FOOT_REACH[1]) or R < 0.62 * R0:
                        break
                    R *= 0.92
                    H *= 0.96
                x, y = p.x, p.y
            z0 = _z_on(x, y) - 0.03
            bush(a, nm, (x, y), z0 if z0 > 0.2 else 0.0, R, H, kind, seed)
    for sk, (nm, R, H, kind, seed) in PAD_BUSHES.items():
        owner = "L" if sk.startswith("SK_L") else "R"
        if owner in owners and sk in PADS:
            c, _top, h = PADS[sk]
            # off the core a little (it stays on its pad), so the clump's heart stays out of the rock
            p = _foot_spot(c.x, c.y, R, H, 0.6 * R, z0=h, max_move=0.45)
            bush(a, nm, (p.x, p.y), _z_on(p.x, p.y) - 0.03, R, H, kind, seed)
    for nm, ((x, y), R, n, seed, buds, owner) in SPRIGS.items():
        if owner in owners:
            if owner == "hero":
                p = _foot_spot(x, y, R, 0.6, 0.5 * FOOT_NEED * R)
                x, y = p.x, p.y
            z0 = _z_on(x, y, z_from=3.0 if owner == "tunnel" else 40.0) - 0.03
            sprig(a, nm, (x, y), z0 if z0 > 0.2 else 0.0, R, n, seed, buds=buds)
    for i, ((x, y), s, owner) in enumerate(PEBBLES):
        if owner in owners:
            if owner == "hero":
                p = _foot_spot(x, y, s, 0.3, 0.6 * s)
                x, y = p.x, p.y
            z0 = _z_on(x, y) - 0.04
            pebble(a, (x, y), z0 if z0 > 0.15 else 0.0, s, 46850 + i)
    for i, ((x, y), r, owner) in enumerate(FLOWERS):
        if owner in owners:
            if owner == "hero":
                p = _foot_spot(x, y, r, 0.2, r + 0.05)
                x, y = p.x, p.y
            z0 = _z_on(x, y) - 0.02
            flower(a, (x, y), z0 if z0 > 0.15 else 0.04, r, 46870 + i)


def apron_poly(sx, seed):
    """The apron round one mass: a strip from the floor flare's outer corner round to the back flare's, its outer edge
    the base path pushed out 1.2-1.5 (jagged, by a noise field), its inner edge tucked 0.45 under the rock."""
    rng = random.Random(seed)
    nf = K.noise_field(scale=0.35, seed=seed)
    pts, inner = [], []
    s0, s1 = 2.25, PATH_L - 2.25
    k = int(math.ceil((s1 - s0) / 2.15))
    for i in range(k + 1):
        s = s0 + (s1 - s0) * i / k
        p, n = _path(s)
        # fix round 1 (finding 2): 1.2-1.5 wide round the foot (was 0.7-1.25; 2.0 would push the bbox past
        # 13.8 +- 0.7 deep), jagged by a field
        w = 1.32 - 0.1 * abs(n.x) + 0.25 * nf(Vector((p.x, p.y, 0))) + rng.uniform(-0.05, 0.05)
        w = max(1.2, min(1.5, w))
        if s < 3.0 or s > PATH_L - 3.0:
            w = min(w, 0.95)
        q = p + n * w
        pts.append(Vector((sx * q.x, q.y)))
        q = p - n * 0.45
        inner.append(Vector((sx * q.x, q.y)))
    return pts + list(reversed(inner))


def apron(a, sx):
    P = apron_poly(sx, 46900 + (sx > 0))
    vs = _slab(a, P, 0.0, 0.1, GRASS, top_fn=lambda p: 0.1 + 0.012 * math.sin(p.x * 3.1 + p.y * 2.3), bevel=0.28)
    nf = K.noise_field(scale=0.25, seed=46500)
    foot = [Vector((sx * q.x, q.y)) for q in (_path(s)[0] for s in np.linspace(0, PATH_L, 40))]
    for f in _faces(vs):
        c = f.calc_center_median()
        d = min(_poly_d(c.xy, foot), 9.0)
        f.material_index = a._mi(_mix(GRASS, GRASS_DEEP, 0.3) if d < 0.45 else
                                 _mix(GRASS, GRASS_LIGHT, 0.15) if nf(c) > 0.25 else GRASS)
    _mottle(a, _faces(vs), 0.04, 0.5, 46910 + sx)
    return vs


def tunnel_strips(a):
    """Lime strips along both wall feet inside the tunnel (on the floor margin, 0.08 thick, into the jamb 0.15)."""
    out = []
    for sx in (-1, 1):
        rng = random.Random(46920 + sx)
        ys = np.linspace(-5.0, 5.0, 7)
        inner = [Vector((sx * (3.05 + rng.uniform(0.0, 0.25)), y)) for y in ys]
        P = inner + [Vector((sx * 3.65, y)) for y in reversed(ys)]
        vs = _slab(a, P, FLOOR_TOP - 0.04, FLOOR_TOP + 0.1, GRASS, bevel=0.08)
        _mottle(a, _faces(vs), 0.04, 0.5, 46930 + sx)
        for f in _faces(vs):
            f.material_index = a._mi(_mix(GRASS, GRASS_DEEP, 0.25))
        out += vs
    return out


# ---- part and hero builders ---------------------------------------------------------------------------------------------
def _surf_tree(vs_lists):
    vs = [v for L in vs_lists for v in L if v.is_valid]
    SURF["tree"] = _tree_of(vs) if vs else None


def span_part(a):
    PLANT_INFO.clear()
    _roots()
    rvs = span(a)
    ROCKS["set"] = _Rocks([rvs])
    cvs = lawn_cap(a, "span", 46501)
    _surf_tree([cvs])
    dressing(a, {"span"})


def _mass_rock(a, sx):
    """One mass's rock as a list of closed shells: the core, its skirts and its foot boulders."""
    side = "R" if sx > 0 else "L"
    shells = [mass_core(a, sx)]
    for nm, (c, w, d, h, yaw, seed, pd) in SKIRTS.items():
        if nm.startswith(f"SK_{side}"):
            shells.append(skirt(a, nm, c, w, d, h, yaw, seed, pd))
    for nm, (c, w, d, h, seed) in BOULDERS.items():
        if nm.startswith(f"B_{side}"):
            shells.append(boulder(a, nm, c, w, d, h, seed))
    return shells


def mass_part(a, sx):
    PLANT_INFO.clear()
    _roots()
    side = "R" if sx > 0 else "L"
    shells = _mass_rock(a, sx)
    ROCKS["set"] = _Rocks(shells)
    cvs = lawn_cap(a, side, 46502 + (sx > 0))
    pvs = []
    for nm in PADS:
        if nm.startswith(f"SK_{side}"):
            pvs += pad(a, nm, 0)
    _surf_tree([cvs, pvs])
    dressing(a, {side})


def mass_l_part(a):
    mass_part(a, -1)


def mass_r_part(a):
    mass_part(a, 1)


def sill_part(a):
    ROCKS["set"] = None
    tvs = sill(a)
    _surf_tree([tvs])
    dressing(a, {"sill"})


HERO_INFO = {}


def hero_fn(a):
    """Everything in one object of closed shells (decision 7): the four parts plus the hero-only foot dressing."""
    PLANT_INFO.clear()
    _roots()
    shells = [span(a)]
    for sx in (-1, 1):
        shells += _mass_rock(a, sx)
    ROCKS["set"] = _Rocks(shells)
    surf = [lawn_cap(a, "span", 46501), lawn_cap(a, "L", 46502), lawn_cap(a, "R", 46503)]
    for nm in PADS:
        surf.append(pad(a, nm, 0))
    surf.append(sill(a))
    surf.append(apron(a, -1))
    surf.append(apron(a, 1))
    surf.append(tunnel_strips(a))
    _surf_tree(surf)
    dressing(a, {"span", "L", "R", "sill", "hero", "tunnel"})
    HERO_INFO["rock_shells"] = len(ROCKS["set"].items)


NOTES = {
    HERO: "Natural arch (rock 24 W x 12 D, lawn top 14.0): a free-standing arch of pale warm columnar rock with a 7.0 x "
          "9.0-clear walk-through opening (vertical jambs to 5.4, haunch to flat seat ledges at 8.0, a three-facet "
          "soffit to a sharp apex at 9.4 over a 0.4 sand-flagstone floor), bottom-heavy pillars with skirt blocks and "
          "faceted foot boulders, a lumpy top span, a lime lawn dome capping every rock top with round two-tone "
          "bushes, pebbles and yellow flowers, a lime apron with foot bushes and flowers. Walkable top and tunnel. "
          "Free-standing (no seam contract). No VFX",
    SPAN_P: "Top Span (reusable): a lumpy faceted rock lintel (4 lumps a face) with flat seat faces at both ends "
            "(z 8.0, x 2.3-6.7), a three-facet soffit to a sharp apex, and its lawn cap with dark dome bushes",
    MASSL_P: "Left Rock Mass (reusable): a columnar rock pillar with a vertical jamb face, a haunch to a flat seat ledge "
             "at z 8.0 and a flat joining face at x 6.7, skirt blocks, foot boulders, its lawn cap and bushes",
    MASSR_P: "Right Rock Mass (reusable): the mirror of the Left Rock Mass with varied columns and dressing",
    SILL_P: "Ground Sill (Floor): 12 sand flagstones 0.4 thick (square-edged slabs, darker sand sides) through the "
            "tunnel, flaring at both mouths, with a few pebbles",
}
COLLISION = {HERO: "precise", SPAN_P: "hull", MASSL_P: "hull", MASSR_P: "hull", SILL_P: "box"}


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
    if all(k.startswith(("m046_leaf", "m046_flower", "m046_trunk")) for k in ks):
        return "leaf"
    if ks == {TRUNK}:
        return "trunk"
    if all(k.startswith("m046_pebble") for k in ks):
        return "pebble"
    if all(k.startswith("m046_floor") for k in ks):
        return "tile"
    if all(k.startswith("m046_grass") for k in ks):
        return "lawn"
    if all(k.startswith("m046_rock") for k in ks):
        return "rock"
    return "mixed"


def shells_report(o):
    old = m040._kind
    m040._kind = _kind
    old_keys = m040._keys
    m040._keys = _keys
    try:
        return m040.shells_report(o)
    finally:
        m040._kind = old
        m040._keys = old_keys


def contact_report(o, tol=0.03):
    old_keys = m040._keys
    m040._keys = _keys
    try:
        r = m040.contact_report(o, tol=tol)
    finally:
        m040._keys = old_keys
    r["floating_kinds"] = [k.replace("m046_", "") for k in r["floating_kinds"]]
    return r


def winding_report(o):
    """Faces wound against their neighbours: directed edges used twice (both faces run the edge the same way), and
    edges with no partner (open)."""
    seen = {}
    for p in o.data.polygons:
        vs = list(p.vertices)
        for i in range(len(vs)):
            e = (vs[i], vs[(i + 1) % len(vs)])
            seen[e] = seen.get(e, 0) + 1
    twice = sum(1 for e, n in seen.items() if n > 1)
    unpaired = sum(1 for (u, v), n in seen.items() if (v, u) not in seen)
    return {"winding_errors": twice, "unpaired_edges": unpaired}


def _shell_faces(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    return bm, ids, n


def edge_on_report(o, views=(("f34", -28, 18), ("front", 0, 4), ("top", 0, 60)), deg=12.0):
    """Leaf faces within `deg` of edge-on from each sheet camera, as a share of leaf area (spec pitfall 4: <= 12 % at
    the f34). Leaves are the 6-vert leaf-keyed shells (hearts, petals and buds left out)."""
    bm, ids, n = _shell_faces(o)
    keys = _keys(o)
    sf, sv = {}, {}
    for f in bm.faces:
        sf.setdefault(ids[f.index], []).append(f)
        for v in f.verts:
            sv.setdefault(ids[f.index], set()).add(v.index)
    leaf = [f for s_, fs in sf.items() if len(sv[s_]) == 6 and
            all(keys[f.material_index].startswith("m046_leaf") for f in fs) for f in fs]
    out = {}
    lim = math.sin(math.radians(deg))
    tot = sum(f.calc_area() for f in leaf) or 1.0
    tree = BVHTree.FromBMesh(bm)
    for nm, az, el in views:
        a_, e_ = math.radians(az), math.radians(el)
        v = Vector((math.sin(a_) * math.cos(e_), -math.cos(a_) * math.cos(e_), math.sin(e_)))
        out[nm] = round(100 * sum(f.calc_area() for f in leaf if abs(f.normal.dot(v)) < lim) / tot, 1)
        # the same over the leaf faces the camera sees (front side toward it, nothing in the way of the centre)
        seen = [f for f in leaf if f.normal.dot(v) > 0 and
                tree.ray_cast(f.calc_center_median() + v * 0.004, v, 80.0)[0] is None]
        st = sum(f.calc_area() for f in seen) or 1.0
        out[nm + "_visible"] = round(100 * sum(f.calc_area() for f in seen if f.normal.dot(v) < lim) / st, 1)
    out["leaf_shells"] = sum(1 for s_, fs in sf.items() if len(sv[s_]) == 6 and
                             all(keys[f.material_index].startswith("m046_leaf") for f in fs))
    bm.free()
    return out


def capping_report(h):
    """Spec 6 on the hero (build frame): rock-only shell faces with n.z > 0.85 seen from straight above (a downward
    ray through 9 points of the face hits that face first): above z 12 (the tops: must be 0) and anywhere above the
    ground; then everything seen from straight above inside the rock footprint (a 0.1 grid over x -12.4..12.4,
    y -6.2..6.2) by kind."""
    off = Vector(h[OFF])
    bm, ids, n = _shell_faces(h)
    keys = _keys(h)
    sk = {}
    for f in bm.faces:
        sk.setdefault(ids[f.index], set()).add(keys[f.material_index])
    kinds = {k: _kind(v) for k, v in sk.items()}
    tree = BVHTree.FromBMesh(bm)
    exposed_hi, exposed_any = 0.0, 0.0
    for f in bm.faces:
        if kinds[ids[f.index]] != "rock" or f.normal.z <= 0.85:
            continue
        c = f.calc_center_median()
        if c.z + off.z < 0.05:
            continue
        pts = [c] + [c.lerp(v.co, 0.85) for v in f.verts] + [c.lerp(v.co, 0.45) for v in f.verts]
        seen = 0
        for p in pts:
            hh = tree.ray_cast(Vector((p.x, p.y, 60.0)), Vector((0, 0, -1)), 200)
            if hh[0] is not None and hh[2] == f.index:
                seen += 1
        a_ = f.calc_area() * seen / len(pts)
        exposed_any += a_
        if c.z + off.z > 12.0:
            exposed_hi += a_
    above = {}
    step = 0.1
    for xi in range(int(24.8 / step)):
        x = -12.4 + (xi + 0.5) * step - off.x
        for yi in range(int(12.4 / step)):
            y = -6.2 + (yi + 0.5) * step - off.y
            hh = tree.ray_cast(Vector((x, y, 60.0)), Vector((0, 0, -1)), 200)
            if hh[0] is None:
                continue
            k = kinds[ids[hh[2]]]
            where = "rock (z>12)" if k == "rock" and hh[0].z + off.z > 12 else k
            above[where] = above.get(where, 0) + step * step
    bm.free()
    return {"flat_rock_top_exposed_above_12": round(exposed_hi, 3), "flat_rock_exposed_any": round(exposed_any, 3),
            "from_above": {k: round(v, 1) for k, v in sorted(above.items())}}


def cover_report():
    """Every rock top-ring point inside its cap's outline (with the distance), and the lip's bottom below the ring."""
    out = {}
    for part in ("span", "L", "R"):
        O = cap_outline(part, {"span": 46501, "L": 46502, "R": 46503}[part])
        P = [tp for o, zb, ztp, R, tp in O]
        ring = [R for o, zb, ztp, R, tp in O if R is not None]
        d = [(_poly_d(r.xy, P) if _inside(r.xy, P) else -_poly_d(r.xy, P)) for r in ring]
        drop = [R.z - zb for o, zb, ztp, R, tp in O if R is not None]
        out[part] = {"inside": all(x > 0 for x in d), "proud_min": round(min(d), 3), "proud_max": round(max(d), 3),
                     "lip_drop_min": round(min(drop), 3)}
    # the span and mass top rings (all points) inside the union of the caps
    return out


def opening_report(h):
    """The walk test (spec 4.2.3) by ray casts in the build frame, against the rock only (the wall-foot strips and
    sprigs allowed in the tunnel are measured separately): the clear width at heights over the floor, the clear height
    over the floor across the tunnel, the floor top, the apex, and the tallest dressing standing on the floor."""
    off = Vector(h[OFF])
    bm, ids, n = _shell_faces(h)
    keys = _keys(h)
    sk = {}
    for f in bm.faces:
        sk.setdefault(ids[f.index], set()).add(keys[f.material_index])
    kinds = {k: _kind(v) for k, v in sk.items()}
    tree = BVHTree.FromBMesh(bm)

    def cast(p, d, want):
        """First hit whose shell kind is in want (other shells are passed through)."""
        p = Vector(p) - off
        d = Vector(d)
        for _ in range(40):
            hh = tree.ray_cast(p, d, 60)
            if hh[0] is None:
                return None
            if kinds[ids[hh[2]]] in want:
                return hh[0] + off
            p = hh[0] + d * 1e-4
        return None
    widths = {}
    for z in (0.6, 2.0, 4.0, 5.4, 6.2, 7.0, 7.6, 8.0, 8.3, 8.7):
        ws = []
        for y in np.linspace(-5.0, 5.0, 21):
            hl = cast((0, y, z), (-1, 0, 0), {"rock"})
            hr = cast((0, y, z), (1, 0, 0), {"rock"})
            if hl is not None and hr is not None:
                ws.append(hr.x - hl.x)
        widths[str(z)] = round(min(ws), 3) if ws else None
    heights, floor = {}, []
    for x in (-3.4, -3.2, -2.0, -1.0, 0.0, 1.0, 2.0, 3.2, 3.4):
        hs = []
        for y in np.linspace(-5.0, 5.0, 21):
            up = cast((x, y, 0.6), (0, 0, 1), {"rock"})
            dn = cast((x, y, 0.6), (0, 0, -1), {"tile"})
            if dn is not None:
                floor.append(dn.z)
            if up is not None and dn is not None:
                hs.append(up.z - dn.z)
        heights[str(x)] = round(min(hs), 3) if hs else None
    apex = [cast((0, y, 0.6), (0, 0, 1), {"rock"}) for y in np.linspace(-5.0, 5.0, 21)]
    apex = [p.z for p in apex if p is not None]
    tall = 0.0
    for x in np.linspace(-3.4, 3.4, 18):
        for y in np.linspace(-5.0, 5.0, 26):
            hh = tree.ray_cast(Vector((x, y, 5.0)) - off, Vector((0, 0, -1)), 30)
            if hh[0] is not None and kinds[ids[hh[2]]] not in ("rock", "tile"):
                tall = max(tall, hh[0].z + off.z - FLOOR_TOP)
    bm.free()
    return {"clear_width_min_at_z": widths, "clear_height_over_floor_at_x": heights,
            "floor_top_p5_p95": [round(float(np.percentile(floor, 5)), 3), round(float(np.percentile(floor, 95)), 3)]
            if floor else None,
            "apex_z": [round(min(apex), 3), round(max(apex), 3)] if apex else None,
            "tallest_dressing_on_floor": round(tall, 3)}


def crack_report(h):
    """See-through test at the joints (decision 4): from each sheet camera direction, rays aimed at points along the
    span / mass joints (the seat line at z 8.0 and the joint lines at x = +-6.7 on the front and back faces), the lawn
    cap seams (x = +-6.7) and the floor / jamb joins. The targets sit 0.15 inside the solid, so a ray that runs more
    than 0.2 past its target without a hit has passed through a gap (see-through if it then escapes the model)."""
    off = Vector(h[OFF])
    bm = bmesh.new()
    bm.from_mesh(h.data)
    tree = BVHTree.FromBMesh(bm)
    pts = []
    for sx in (-1, 1):
        g = mass_geo(sx)
        for jk in ("jf", "jb"):
            col = g["chain"][g[jk]]["col"]
            for k in range(3, len(col) - 1):
                for t in np.linspace(0, 1, 5):
                    p = col[k].lerp(col[k + 1], t)
                    pts.append(p + (Vector((sx * 8.0, 0.0, p.z)) - p).normalized() * 0.15)   # just inside
        for k in range(len(g["chain"])):
            c = g["chain"][k]
            if c["zone"] == "hz":
                p = c["col"][-1]
                pts.append(p + (Vector((sx * 5.0, 0.0, 7.9)) - p).normalized() * 0.15)
        for y in np.linspace(-3.0, 3.0, 7):
            pts.append(Vector((sx * JOINT_X, y, zt(JOINT_X, y) + 0.4)))
        for y in np.linspace(-5.0, 5.0, 11):
            pts.append(Vector((sx * 3.55, y, FLOOR_TOP - 0.02)))
    dirs = []
    for az, el in list(SHEET_VIEWS.values()) + [(-90, 8), (0, 30), (180, 30)]:
        a_, e_ = math.radians(az), math.radians(el)
        dirs.append(-Vector((math.sin(a_) * math.cos(e_), -math.cos(a_) * math.cos(e_), math.sin(e_))))
    leaks, tested = [], 0
    for p in pts:
        q = p - off
        for d in dirs:
            o = q - d * 40.0
            hh = tree.ray_cast(o, d, 80.0)
            if hh[0] is None:
                continue                                   # misses: the target point is not on this side's silhouette
            dist = (hh[0] - o).length
            tested += 1
            if dist > 40.2:
                # the ray ran past its target point on the surface: a gap at the joint (see-through if it then
                # escapes the model, a crack into the solid otherwise)
                back = tree.ray_cast(q + d * 0.2, d, 80.0)
                leaks.append(([round(x, 2) for x in p], "through" if back[0] is None else "into"))
    bm.free()
    return {"rays": tested, "leaks": len(leaks), "see_through": sum(1 for _, k in leaks if k == "through"),
            "leak_points": leaks[:8]}


def lawn_report(h):
    """The walkable top: lawn height and slope over the central 14 x 6 (build frame)."""
    off = Vector(h[OFF])
    me = h.data
    bm = bmesh.new()
    bm.from_mesh(me)
    tree = BVHTree.FromBMesh(bm)
    zs, slopes, where = [], [], []
    keys = _keys(h)
    for x in np.linspace(-7.0, 7.0, 29):
        for y in np.linspace(-3.0, 3.0, 13):
            # cast down; skip bushes by taking hits on lawn faces only (grass material)
            p = Vector((x, y, 40.0)) - off
            hh = tree.ray_cast(p, Vector((0, 0, -1)), 100)
            if hh[0] is not None and not keys[me.polygons[hh[2]].material_index].startswith(("m046_grass",
                                                                                            "m046_pebble")):
                continue                    # under a bush, a flower or a sprig: not walkable, not counted
            k = 0
            while hh[0] is not None and k < 6:
                mat = keys[me.polygons[hh[2]].material_index]
                if mat.startswith("m046_grass"):
                    zs.append(hh[0].z + off.z)
                    where.append((round(float(x), 2), round(float(y), 2)))
                    slopes.append(math.degrees(math.acos(max(-1, min(1, abs(hh[1].z))))))
                    break
                hh = tree.ray_cast(hh[0] - Vector((0, 0, 0.001)), Vector((0, 0, -1)), 100)
                k += 1
    bm.free()
    return {"lawn_z_min": round(min(zs), 3), "lawn_z_min_at": where[int(np.argmin(zs))],
            "lawn_z_max": round(max(zs), 3),
            "slope_p95": round(float(np.percentile(slopes, 95)), 1), "slope_max": round(max(slopes), 1),
            "samples": len(zs)}


def rock_metrics(o):
    old = m040.OFF
    m040.OFF = OFF
    try:
        return m040.rock_metrics(o)
    finally:
        m040.OFF = old


# ---- render measurement (the study's masks, spec "Pixel boxes and masks") ------------------------------------------------
SHEET_REF = {
    "f34": {"wh": 1.295, "R": 64.5, "P": 6.6, "L": 15.2, "F": 13.3, "G": 28.5, "D": 0.4,
            "fifths": [20.9, 20.7, 1.3, 19.8, 37.3],
            "top": [.18, .35, .54, .74, .85, .86, .85, .92, .92, .96, .97, .95, 1.0, .93, .93, .92, .94, .85, .82, .54,
                    .27], "warm": "#C7A99A", "floor": "#F6BA80", "lawn": "#CFD809", "bush": "#407616"},
    "front": {"wh": 1.508, "R": 68.1, "P": 4.7, "L": 14.8, "F": 12.1, "G": 26.9, "D": 0.3,
              "fifths": [30.3, 6.2, 0.3, 23.3, 39.9],
              "top": [.09, .28, .69, .81, .89, .87, .91, .91, .97, .92, .99, .97, .97, .92, .89, .90, .88, .78, .70,
                      .39, .09], "hole": {"w": 0.264, "h": 0.475, "top": 0.580, "bottom": 0.110},
              "warm": "#CCAC9B", "lawn": "#C9D30A"},
    "side": {"wh": 0.785, "R": 74.7, "P": 1.2, "L": 11.8, "F": 11.9, "G": 23.7, "D": 0.5,
             "fifths": [24.8, 6.4, 1.5, 28.2, 39.1],
             "top": [.12, .18, .64, .87, .92, .95, .96, .93, .97, .98, .98, .96, .91, .87, .88, .86, .75, .74, .68, .23,
                     .12]},
    "rear": {"wh": 1.450, "R": 67.9, "P": 4.6, "L": 15.1, "F": 12.1, "G": 27.2, "D": 0.3,
             "top": [.07, .26, .69, .81, .90, .87, .87, .96, .94, .92, .97, .97, .97, .96, .89, .90, .91, .84, .69, .30,
                     .07], "hole": {"w": 0.264, "h": 0.444, "top": 0.550, "bottom": 0.111}},
    "r34": {"wh": 1.262, "R": 67.1, "P": 3.6, "L": 15.4, "F": 13.4, "G": 28.8, "D": 0.5},
    "top": {"wh": 1.356, "R": 41.3, "P": 1.4, "L": 38.7, "F": 18.1, "G": 56.8, "D": 0.5,
            "top": [.16, .71, .84, .87, .89, .95, .96, .92, .91, .92, .93, .97, .98, .91, .92, .88, .92, .89, .82, .72,
                    .23]},
}


def classify(px):
    """The study's cls(): 1 R rock, 2 P floor sand, 3 L lawn / lime / yellow, 4 F foliage, 5 D trunk / dirt,
    6 T dark text-like, 0 else."""
    h, s, v = m040._hsv(px)
    G = (h >= 45) & (h <= 170) & (s >= 0.28) & (v >= 0.12)
    Lw = G & (h < 80) & (v >= 0.62)
    F = G & ~Lw
    T = (v < 0.25) & (s < 0.35)
    Pa = ~G & (h >= 15) & (h <= 42) & (s >= 0.33) & (v >= 0.62)
    D = ~G & ~Pa & (h <= 40) & (s >= 0.40) & (v >= 0.15) & (v < 0.62)
    R = ~G & ~T & ~D & ~Pa & (((h <= 50) | (h >= 190)) & (s < 0.40) & (v >= 0.25))
    out = np.zeros(v.shape, np.int8)
    out[R] = 1
    out[Pa] = 2
    out[Lw] = 3
    out[F] = 4
    out[D] = 5
    out[T] = 6
    return out, h, s, v


def _flood(mask, seed_mask):
    cur = seed_mask & mask
    while True:
        nxt = cur.copy()
        nxt[1:] |= cur[:-1]
        nxt[:-1] |= cur[1:]
        nxt[:, 1:] |= cur[:, :-1]
        nxt[:, :-1] |= cur[:, 1:]
        nxt &= mask
        if (nxt == cur).all():
            return cur
        cur = nxt


def measure(path, bg_tol=0.04):
    """Silhouette bbox, W:H, shares (R / P / L / F / D of their sum, G = L + F), green by height fifths, the top
    profile (21 columns), medians (rock, lit-half rock, floor, lawn, bush), and the see-through opening (enclosed
    background inside the silhouette: the largest region) with its size and the other enclosed specks."""
    kit = K.NS["KIT"]
    px = np.clip(kit["load_px"](path)[::-1, :, :3], 0, 1)
    bg = np.median(np.concatenate([px[:4, :4].reshape(-1, 3), px[:4, -4:].reshape(-1, 3)]), axis=0)
    sil = np.abs(px - bg).max(-1) > bg_tol
    cls, h, s, v = classify(px)
    ys, xs = np.nonzero(sil)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    H, W = y1 - y0 + 1, x1 - x0 + 1
    c = np.where(sil, cls, 0)
    cnt = {k: int((c == i).sum()) for k, i in (("R", 1), ("P", 2), ("L", 3), ("F", 4), ("D", 5))}
    tot = max(1, sum(cnt.values()))
    gy = np.nonzero((c == 3) | (c == 4))[0]
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
    res = {"wh": round(W / H, 3)}
    for k in ("R", "P", "L", "F", "D"):
        res[k] = round(100 * cnt[k] / tot, 1)
    res["G"] = round(res["L"] + res["F"], 1)
    res["fifths"] = [round(100 * f / gsum, 1) for f in fifths]
    res["top"] = prof
    res["rock"] = med(c == 1)
    rk = c == 1
    if rk.any():
        lum = px[rk].mean(axis=1)
        sel = rgb[rk][lum >= np.median(lum)]
        res["warm"] = "#" + "".join(f"{int(x):02X}" for x in np.median(sel, axis=0))
    res["floor"] = med(c == 2)
    res["lawn"] = med(c == 3)
    res["bush"] = med(c == 4)
    # the opening: background enclosed by the silhouette inside its bbox
    box = np.zeros_like(sil)
    box[y0:y1 + 1, x0:x1 + 1] = True
    bgm = ~sil & box
    edge = np.zeros_like(sil)
    edge[y0, :] = edge[y1, :] = True
    edge[:, x0] = edge[:, x1] = True
    outside = _flood(bgm, edge & bgm)
    enclosed = bgm & ~outside
    if enclosed.any():
        ey, ex = np.nonzero(enclosed)
        cx = (x0 + x1) / 2
        k = int(np.argmin(np.abs(ex - cx) + 0.2 * np.abs(ey - (y0 + y1) / 2)))
        seed = np.zeros_like(sil)
        seed[ey[k], ex[k]] = True
        hole = _flood(enclosed, seed)
        hy, hx = np.nonzero(hole)
        res["hole"] = {"w": round((hx.max() - hx.min() + 1) / W, 3), "h": round((hy.max() - hy.min() + 1) / H, 3),
                       "top": round(float((y1 - hy.min()) / (H - 1)), 3),
                       "bottom": round(float((y1 - hy.max()) / (H - 1)), 3),
                       "cx": round(float((hx.mean() - x0) / (W - 1)), 3), "px": int(hole.sum())}
        rows = {}
        hh_ = hy.max() - hy.min() + 1
        for f in (0.1, 0.3, 0.5, 0.7, 0.9):
            yy = int(hy.max() - f * (hh_ - 1))
            r = np.nonzero(hole[yy])[0]
            rows[str(f)] = round((r.max() - r.min() + 1) / W, 3) if len(r) else 0.0
        res["hole"]["width_by_height"] = rows
        res["specks_px"] = int((enclosed & ~hole).sum())
    else:
        res["hole"] = None
        res["specks_px"] = 0
    return res


def measure_views(out_dir=None):
    d = out_dir or f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    res = {}
    for k, f in (("f34", "f34_sheet"), ("front", "front_sheet"), ("side", "side_sheet"), ("rear", "rear_sheet"),
                 ("r34", "r34_sheet"), ("top", "top_sheet"), ("front_e8", "front_e8_sheet"),
                 ("f34_see", "f34_see_sheet")):
        try:
            m = measure(f"{d}/{f}.png")
        except Exception as e:
            res[k] = str(e)
            continue
        ref = SHEET_REF[k.split("_")[0]]
        if "top" in ref:
            m["top_err_mean"] = round(float(np.mean(np.abs(np.array(m["top"]) - np.array(ref["top"])))), 3)
            m["top_err_max"] = round(float(np.max(np.abs(np.array(m["top"]) - np.array(ref["top"])))), 3)
        m.pop("top", None)
        m["sheet"] = {kk: vv for kk, vv in ref.items() if kk != "top"}
        res[k] = m
    return res


# ---- build ------------------------------------------------------------------------------------------------------------
# fix round 1: the depth target moved from 13.8 +- 0.7 to 15.0 +- 0.6. The rock alone is 13.4 deep (boulders at
# y +-6.7); the round-1 ruling's foot bushes, kept 0.7 R clear of the rock, stand in front of it to y +-7.7.
TARGET_SIZE = ((25.6, 0.8), (15.0, 0.6), (15.9, 0.6))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me is not None and isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m046_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib",
                                                                                 "StoneGate"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build_objects(parts=True):
    GEO.clear()
    M.coll(NUM, TITLE)
    ROCK_INFO.clear()
    PADS.clear()
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in ((SPAN_P, span_part), (MASSL_P, mass_l_part), (MASSR_P, mass_r_part), (SILL_P, sill_part)):
            objs[name], log[name] = _make_plain(name, fn)
    h, log["hero"] = _make_plain(HERO, hero_fn, role="hero", budget=4000)
    log["hero"]["rock_shells"] = HERO_INFO.get("rock_shells")
    log["plants"] = {k: dict(v) for k, v in PLANT_INFO.items()}
    log["rocks"] = {k: dict(v) for k, v in ROCK_INFO.items()}
    log["mass"] = {str(k): dict(v) for k, v in MASS_INFO.items()}
    log["span"] = dict(SPAN_INFO)
    log["caps"] = {k: dict(v) for k, v in CAP_INFO.items()}
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
    contact = {o.name: contact_report(o) for o in order if o.name in (HERO, SPAN_P, MASSL_P, MASSR_P, SILL_P)}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} shells touch nothing within 0.03, {c['unchained']} have no chain "
                            f"of contact to the ground")
    bury = {o.name: bury_report(o) for o in order if o.name != SILL_P}
    for n_, b in bury.items():
        if b["over_0.05"]:
            problems.append(f"{n_}: {b['over_0.05']} dressing shells more than 0.05 inside rock (max {b['max']}, "
                            f"ray parity)")
    edge = edge_on_report(h)
    cap = capping_report(h)
    if cap["flat_rock_top_exposed_above_12"] > 0.0:
        problems.append(f"{HERO}: exposed flat rock top above z 12: {cap['flat_rock_top_exposed_above_12']}")
    cover = cover_report()
    for part, cv in cover.items():
        if not cv["inside"] or cv["proud_min"] < 0.05 or cv["lip_drop_min"] < 0.18:
            problems.append(f"{HERO}: the {part} cap does not cap its rock ring ({cv})")
    opening = opening_report(h)
    w = opening["clear_width_min_at_z"]
    if (w.get("0.6") or 0) < 6.8 or (w.get("5.4") or 0) < 6.8 or (w.get("7.0") or 0) < 5.6:
        problems.append(f"{HERO}: opening too narrow {w}")
    hh = opening["clear_height_over_floor_at_x"]
    if (hh.get("0.0") or 0) < 9.0 or (hh.get("3.2") or 0) < 5.6 or (hh.get("3.4") or 0) < 4.6:
        problems.append(f"{HERO}: opening too low {hh}")
    if opening["tallest_dressing_on_floor"] > 0.6:
        problems.append(f"{HERO}: dressing taller than 0.6 inside the tunnel ({opening['tallest_dressing_on_floor']})")
    crack = crack_report(h)
    if crack["leaks"]:
        problems.append(f"{HERO}: light leaks through joints {crack}")
    lawn = lawn_report(h)
    if lawn["lawn_z_min"] < 13.6:
        problems.append(f"{HERO}: lawn under 13.6 over the central 14 x 6 ({lawn})")
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
            "shells": kinds, "winding": winding, "contact": contact, "capping": cap, "cover": cover,
            "bury": bury, "edge_on": edge,
            "opening": opening, "cracks": crack, "lawn": lawn, "thin": thin, "problems": problems, "uv": uv,
            "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
            "rock_metrics": {n_: rock_metrics(by[n_]) for n_ in (MASSL_P, MASSR_P, SPAN_P) if n_ in by},
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
# decision 9 and the main session's ruling after round 1: f34_sheet (-28, 18) governs (from the probe set); front_sheet
# (0, 4) is strict on the hole (the sheet's hole bottom matches e 4); side (90, 8); top about (0, 60); rear (180, 8)
# and r34 (145, 18) as repeats. Floor hidden and a long lens on the *_sheet shots (m033._long_lens).
SHEET_VIEWS = {"f34_sheet": (-28, 18), "front_sheet": (0, 4), "side_sheet": (90, 8), "rear_sheet": (180, 8),
               "r34_sheet": (145, 18), "top_sheet": (0, 60)}
# extra sheet-style shots: the front at the old e 8 (for comparison with round 1) and the f34 at az -22, where the
# tunnel shows the paper through it as the sheet draws
EXTRA_SHEET = {"front_e8_sheet": (0, 8), "f34_see_sheet": (-22, 18)}
PARTS_SHOT = (-30, 25)


def _copy(tag, src, m, coll):
    c = bpy.data.objects.new(f"{PFX}{tag}", src.data)
    coll.objects.link(c)
    c.matrix_world = m
    return c


def _frame_of(h):
    return h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))


def _exploded(objs, lift=None, tag="expl"):
    """Copies of the parts laid out like the sheet's Exploded Construction: the span lifted above, the masses pulled
    apart left and right, the sill pulled forward between them."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []
    o0 = Matrix.Translation((objs[0].location.x + 120, objs[0].location.y, 0))
    moves = lift or {SPAN_P: (0, 0, 6.0), MASSL_P: (-5.0, 0, 0), MASSR_P: (5.0, 0, 0), SILL_P: (0, -9.0, 0)}
    for nm, d in moves.items():
        if nm in by:
            shown.append(_copy(f"{tag}_{nm}", by[nm], o0 @ Matrix.Translation(Vector(by[nm][OFF]) + Vector(d)), coll))
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
    """5.5-stud character stand-ins: walking through the tunnel, on the apron beside a pillar, on the lawn top."""
    return [_marker(h, (0.0, -1.0, FLOOR_TOP), "char_tunnel"), _marker(h, (-13.8, -3.2, 0.1), "char_apron"),
            _marker(h, (2.6, 0.4, 13.95), "char_lawn")]


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
    by = {o.name: o for o in objs}
    shown = _exploded(objs) if len(objs) > 1 else []
    junc = _exploded(objs, {SPAN_P: (0, 0, 0.8), MASSL_P: (0, 0, 0)}, "junc") if SPAN_P in by and MASSL_P in by else []
    for o in junc:
        o.matrix_world = Matrix.Translation((0, 60, 0)) @ o.matrix_world
    markers = _scale_markers(h)
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        for o in objs[1:]:
            extra["part_" + o.name.replace("StoneGate", "").lower()] = ([o], *PARTS_SHOT)
        if SPAN_P in by:
            extra["span_underside"] = ([by[SPAN_P]], -20, -30)
        if shown:
            extra["exploded"] = (shown, -25, 22)
        extra["scale"] = ([h] + markers, -20, 8)
        for k, (az, el) in EXTRA_SHEET.items():
            extra[k] = ([h], az, el)
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
            out["tunnel"] = _close([h] + markers[:1], f"{d}/tunnel.png", -12, 6, fr @ Vector((0.0, -2.0, 4.8)), 6.5)
            out["floor_cu"] = _close([h], f"{d}/floor_cu.png", -25, 24, fr @ Vector((3.0, -6.0, 0.4)), 2.4)
            out["hole_cu"] = _close([h], f"{d}/hole_cu.png", 0, 4, fr @ Vector((0.0, -6.0, 5.2)), 5.6)
            if junc:
                jm = next(o for o in junc if MASSL_P in o.name)
                jf = jm.matrix_world @ Matrix.Translation(-Vector(by[MASSL_P][OFF]))
                out["junc_cu"] = _close(junc, f"{d}/junc_cu.png", -35, 18, jf @ Vector((-4.4, -5.0, 8.4)), 3.0)
        return out
    finally:
        for o in shown + junc + markers:
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
    GEO.clear()
    PADS.clear()
    M.coll(NUM, TITLE)
    palette()
    h, lg = _make_plain(HERO, hero_fn, role="hero", budget=4000)
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals")}, "log": lg, "winding": winding_report(h),
            "mass": {str(k): dict(v) for k, v in MASS_INFO.items()}, "span": dict(SPAN_INFO),
            "caps": {k: dict(v) for k, v in CAP_INFO.items()}, "rocks": dict(ROCK_INFO),
            "plants": {k: dict(v) for k, v in PLANT_INFO.items()}}
