"""034 Streambed Section (references/034.png): a square, thin, flat-bottomed slab tile (32 x 32 studs) with a shallow
cyan stream running straight through it from the front seam to the back seam, between two flat warm-sand bank slabs.
The stream bed is a lower slab (top 0.7) under a thin flat see-through water plane (top 1.0); the banks (top 1.6) have
straight, jogged plank edges along the water, softened by a separate white foam ribbon. Big chunky grey boulders with
big flat facets and flat crowns stand on both waterlines, two mid rocks stand in the water near the edges, one rock
mid-stream; mid and small rocks and pebbles dot both banks.

    import importlib, kit_models, m034; importlib.reload(kit_models); importlib.reload(m034); m034.build()

Build frame (studs): front -Y, +X right, ground z 0 (the one flat underside). The stream runs along Y, downstream -Y.
Tile X -16 .. 16, Y -16 .. 16. Levels (M034_spec.md 2.1, decision 1): ground 0, bed top 0.7, water 0.76 -> 1.0, foam
1.03 -> 1.06, bank tops 1.6 (the right bank's middle plank 1.9), boulder tops 5.6 - 7.4 (B1 7.4 = the bbox top).
Fix round 1 (main session ruling): the channel widens to about 20-24 studs mid-tile (banks 4-5.5) while the seams keep
the contract (X -7 .. +7); chunky flat-crowned boulders; soft lobed foam hugging the rocks; a deep-tone bed.

The land is built as one closed "terrace" mesh without booleans: each flat region (left bank, channel, right bank
planks) is a 2D constrained triangulation lifted to its level, vertical walls stand wherever two regions of different
level meet and round the tile outline (down to the one flat bottom). The rocks and pebbles are convex hulls sunk 0.3
into the slab they stand on and united one shell at a time (merge-0 exact unions at the world origin).

Parts (the sheet's Parts Breakdown, decision 5), each from its own function:
- StreambedSectionBankSlab (bank_slab_part): the left bank slab with its small rocks and pebbles.
- StreambedSectionBedSlab (bed_slab_part): the channel slab (top 0.7, earth sides) with its in-stream small rocks.
- StreambedSectionWaterPlane (water_plane_part): the water shell alone (no rock holes), carrying the flow sockets.
- StreambedSectionRockLarge / RockMedium / RockSmall (rock_*_part): the reusable rock pieces (B4, M2 with a small
  rock at its foot, S1), flat-bottomed at z 0.

The hero (StreambedSection, decision 9) is one object: one closed land shell (terrace + every rock and pebble), plus a
closed water shell (m034_water) and a closed foam shell (m034_water_foam) that never touch the land: the water stands
0.06 off the bank walls and 0.06 over the bed, both are cut round every rock by a 2D hole 0.06 outside its section
at the foam's top (0.14 for the waterline straddlers).
Both water keys contain "water", so the exporter makes them two see-through, non-colliding water pieces. Colour
(stage 4) is painted by position inside the builders before the union. See M034_spec.md.
"""
import math
import random
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise
from mathutils.geometry import delaunay_2d_cdt

import kit_mcp as K
import kit_models as M
import m011
import m012
import m016

NUM, TITLE, SHEET = 34, "Streambed Section", "M034"
OFF = "m034_offset"
PFX = "_m034_"
HERO = "StreambedSection"
BANK_P, BED_P, WATER_P = "StreambedSectionBankSlab", "StreambedSectionBedSlab", "StreambedSectionWaterPlane"
ROCK_LP, ROCK_MP, ROCK_SP = "StreambedSectionRockLarge", "StreambedSectionRockMedium", "StreambedSectionRockSmall"

SAND, SAND_LIGHT, EARTH = "m034_sand", "m034_sand_light", "m034_earth"
ROCK, PEBBLE = "m034_rock", "m034_pebble"
BED, BED_LIGHT = "m034_bed", "m034_bed_light"
WATER, FOAM = "m034_water", "m034_water_foam"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low_spec); the comment is the calibration target (spec 5.4: unshadowed rendered regions)
PALETTE = {SAND: ("#DCB874", 0.95, False),          # #FBCE81 exploded bank top (f34 render median #FCCF7F)
           SAND_LIGHT: ("#E2BC86", 0.95, False),    # #FEE5A0 lit quartiles
           EARTH: ("#978C86", 0.95, False),         # #A39A97 bed cut face
           ROCK: ("#9C9898", 0.85, False),          # lit faces #C8BBBD, whole rock #998E9A; hue 0-20 (never B > G)
           PEBBLE: ("#715735", 0.9, False),         # #8E6B45
           BED: ("#0090E8", 0.9, False),            # the deep water tone #01C2FC (s >= .97)
           BED_LIGHT: ("#38C8EE", 0.9, False),      # the light water tone #3FE1FD
           WATER: ("#00ACDC", 0.3, False),         # rendered water median #08D1FD
           FOAM: ("#AAD0E6", 0.6, False)}           # rendered foam median #C2F2FC
TRANSPARENCY = {WATER: 0.3, FOAM: 0.22}
BED_PATCH_SCALE, BED_PATCH_LEVEL = 0.12, 0.0       # the bed's broad light patches (about 8 studs across)
WATER_SPEC = 0.0

TARGETS = {SAND: ((0xFB, 0xCE, 0x81), "all"), SAND_LIGHT: ((0xFE, 0xE5, 0xA0), "all"),
           EARTH: ((0xA3, 0x9A, 0x97), "stone"), ROCK: ((0xB4, 0xA8, 0xAB), "stone"),
           PEBBLE: ((0x8E, 0x6B, 0x45), "brown")}


def palette():
    f = K.fk()
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        mat = f.material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        if k in TRANSPARENCY:
            f.set_water_transparency(mat, TRANSPARENCY[k])
            _refresh_water_texture(mat, k, hexcol)
            # preview only (the exporter makes water SmoothPlastic): a low sheen, or the low kit cameras see the sky
            # sun glint mirrored white over the whole flat water
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf and "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = WATER_SPEC
    _bed_finish()


def _bed_finish():
    """Preview only: the bed (and its in-between keys) without a specular sheen. Seen through the 0.3-transparent
    water, the bed's sky glint lifted every water pixel's red (round 1: 0 % deep-tone pixels); the stream bed under
    water has no glint of its own (the water surface is SmoothPlastic in Roblox and carries it)."""
    for mat in bpy.data.materials:
        if mat.name.startswith("FB_" + BED) and mat.node_tree:
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf and "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = 0.0


def _refresh_water_texture(mat, key, hexcol):
    """The kit's water preview texture is painted from the key's colour when the material is first made; repaint it
    (and reload the image) when the colour has changed since, so the renders show the current key. (m032)"""
    f = K.fk()
    nt = mat.node_tree
    tex = nt.nodes.get("FB_WaterTex") if nt else None
    if tex is None or mat.get("m034_tex_hex") == hexcol:
        mat["m034_tex_hex"] = hexcol
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
    mat["m034_tex_hex"] = hexcol


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome. "all" keys are sampled with the
    floor dropped (M.sample). Returns {key: (hex, rendered)} and leaves the keys set. (m032)"""
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


# ---- small helpers -------------------------------------------------------------------------------------------------
def _q(t):
    return round(min(1.0, max(0.0, t)) * 4) / 4


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


def _v2(p):
    return Vector((p[0], p[1]))


# ---- 2D geometry (m032) --------------------------------------------------------------------------------------------
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
            p = Vector((x + rng.uniform(-0.22, 0.22) * spacing, y + rng.uniform(-0.22, 0.22) * spacing))
            if any(_inside(p, q) for q in pos) and not any(_inside(p, q) for q in neg):
                if min(_dist_line(p, q, True) for q in list(pos) + list(neg)) > margin:
                    out.append(p)
            x += spacing
        y += spacing
        j += 1
    return out


def cdt_region(pos, neg=(), steiner=(), tidy=True, min_island=0.0):
    """2D triangulation of (union of pos polygons) minus (union of neg polygons), with optional interior points.
    Returns (coords [Vector2], tris [(i, j, k)] CCW). (m032)"""
    verts, faces = [], []
    for poly in list(pos) + list(neg):
        idx = []
        # every input polygon CCW: the CDT takes a clockwise one's outside as its inside
        if sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly))) < 0:
            poly = list(reversed(poly))
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
        co, tris = _tidy2d(co, tris, min_island=min_island, tidy=tidy, keep=list(neg) if tidy else None)
    return co, tris


def _tidy2d(co, tris, merge=0.04, straight=172.0, min_island=0.0, tidy=True, max_edge=1.1, keep=None):
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
        if keep is not None:
            _needles2d(bm, keep)
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


def _needles2d(bm, keep, lim=6.0, max_len=0.7):
    """Collapse the short edge of each needle triangle (a hole passing close to the outline): onto its end on a neg
    polygon (a rock hole) when it has one, so the hole never shrinks; otherwise onto the edge's midpoint."""
    def on_neg(v):
        p = Vector((v.co.x, v.co.y))
        return any(_dist_line(p, q, True) < 1e-4 for q in keep)
    def folds(v, co, e):
        """Moving v to co flips (or flattens) one of its faces that survive the collapse of e."""
        for f in v.link_faces:
            if e in f.edges:
                continue
            p = [co if x is v else x.co for x in f.verts]
            ar = sum(p[i].x * p[(i + 1) % len(p)].y - p[(i + 1) % len(p)].x * p[i].y for i in range(len(p)))
            if ar * (1 if f.normal.z >= 0 else -1) <= 1e-6:
                return True
        return False
    tried = set()
    for _ in range(30):
        bm.normal_update()
        bad = None
        for f in bm.faces:
            ls = list(f.loops)
            if len(ls) == 3 and min(l.calc_angle() for l in ls) < math.radians(lim):
                e = min(f.edges, key=lambda x: x.calc_length())
                if e.calc_length() <= max_len and e.index not in tried:
                    bad = e
                    break
        if bad is None:
            break
        a_, b_ = bad.verts
        na, nb = on_neg(a_), on_neg(b_)
        co = a_.co.copy() if na and not nb else b_.co.copy() if nb and not na else (a_.co + b_.co) / 2
        if folds(a_, co, bad) or folds(b_, co, bad):
            bm.edges.index_update()
            tried.add(bad.index)
            continue
        bmesh.ops.pointmerge(bm, verts=[a_, b_], merge_co=co)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-5)
        bm.edges.index_update()
        tried = set()
    # caps (no short edge, one corner near 180): flip the long edge when both new triangles are better
    def amin(pts):
        out = []
        for i in range(3):
            u, w = pts[(i + 1) % 3] - pts[i], pts[(i + 2) % 3] - pts[i]
            out.append(u.angle(w, 0.0))
        return min(out)
    for _ in range(3):
        flipped = 0
        bm.normal_update()
        for f in list(bm.faces):
            if not f.is_valid or len(f.verts) != 3:
                continue
            if amin([v.co for v in f.verts]) >= math.radians(lim):
                continue
            e = max(f.edges, key=lambda x: x.calc_length())
            if len(e.link_faces) == 1:
                # a sliver on the outline: drop it (the outline then runs through its third corner)
                bmesh.ops.delete(bm, geom=[f], context="FACES_ONLY")
                bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES")
                flipped += 1
                continue
            if len(e.link_faces) != 2:
                continue
            g = next(x for x in e.link_faces if x is not f)
            if len(g.verts) != 3:
                continue
            A, B = e.verts
            c = next(v for v in f.verts if v not in (A, B))
            d = next(v for v in g.verts if v not in (A, B))
            old = min(amin([v.co for v in f.verts]), amin([v.co for v in g.verts]))
            new = min(amin([A.co, c.co, d.co]), amin([c.co, B.co, d.co]))
            # the quad must be convex (the new diagonal inside it)
            side = lambda p, q, r: (q.x - p.x) * (r.y - p.y) - (q.y - p.y) * (r.x - p.x)
            if new > old + 1e-3 and side(c.co, d.co, A.co) * side(c.co, d.co, B.co) < 0:
                if bmesh.ops.rotate_edges(bm, edges=[e], use_ccw=False)["edges"]:
                    flipped += 1
        if not flipped:
            break


def slab(a, co, tris, ztop, zbot, mat):
    """A closed flat slab over a 2D triangulation (water, foam): top at ztop, bottom at zbot, quad walls round every
    boundary edge (planar quads, no needles). Returns its verts."""
    bm = a.bm
    used = sorted({i for t in tris for i in t})
    top = {i: bm.verts.new((co[i].x, co[i].y, ztop)) for i in used}
    bot = {i: bm.verts.new((co[i].x, co[i].y, zbot)) for i in used}
    directed = set()
    for i, j, k in tris:
        bm.faces.new((top[i], top[j], top[k]))
        bm.faces.new((bot[i], bot[k], bot[j]))
        directed |= {(i, j), (j, k), (k, i)}
    for i, j in [(i, j) for i, j in directed if (j, i) not in directed]:
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    allv = list(top.values()) + list(bot.values())
    a._finish(allv, mat, tint=1.0)
    return allv


def _resample_poly(poly, maxlen):
    out = []
    P = [_v2(p) for p in poly]
    for i, p in enumerate(P):
        q = P[(i + 1) % len(P)]
        n = max(1, int(math.ceil((q - p).length / maxlen)))
        out += [p.lerp(q, k / n) for k in range(n)]
    return out


def _rs(way, step):
    """A waypoint polyline resampled per segment (so the same waypoints reversed give the same points reversed),
    all points including both ends."""
    P = [_v2(p) for p in way]
    out = [P[0]]
    for p, q in zip(P, P[1:]):
        n = max(1, int(math.ceil((q - p).length / step - 1e-6)))
        out += [p.lerp(q, k / n) for k in range(1, n + 1)]
    return out


def _blob(c, r, n, rot, sq=1.0):
    return [Vector((c[0] + math.cos(rot + 2 * math.pi * k / n) * r, c[1] + math.sin(rot + 2 * math.pi * k / n) * r * sq))
            for k in range(n)]


# ---- layout (studs, build frame; spec 2) ---------------------------------------------------------------------------
TILE = 16.0
BANK_TOP, PLANK_TOP, BED_TOP = 1.6, 1.9, 0.7
WATER_TOP, WATER_BOT, WATER_GAP = 1.0, 0.76, 0.06
SEAM_INSET = 0.02
FOAM_Z = (1.03, 1.06)
TOP_STEP = 3.3            # the slab tops' point spacing (colour patches; spec 1.4 "gridded at about 2 studs"; 3.3 in
                          # fix round 1 for the foam's budget)
BOTTOM_STEP = 8.0
WALL_BANDS = (0.45, 1.04, 1.6)  # extra rings on the walls (the sand / earth colour bands; 1.6 on the plank walls)

# the bank inner edges (back y = 16 -> front y = -16), straight segments with 45 degree jogs (spec 2.2, amended by
# the main session after round 1: the seams keep the contract, X -7 .. +7, but the channel widens to about 20 studs
# mid-tile with banks about 5.5-6 there, the hero cell's broad stream); the right edge carries the plank cut points
L_EDGE = [(-7.0, 16.0), (-10.5, 12.5), (-10.5, 5.0), (-12.0, 3.5), (-12.0, -11.0), (-7.0, -16.0)]
R_BACK = [(7.0, 16.0), (10.5, 12.5), (10.5, 3.0), (12.0, 1.5), (12.0, -0.6)]
R_MID = [(12.0, -0.6), (12.0, -8.5)]
R_FRONT = [(12.0, -8.5), (12.0, -11.0), (7.0, -16.0)]
R_EDGE = R_BACK + R_MID[1:] + R_FRONT[1:]
CUT1 = [(12.0, -0.6), (16.0, -0.6)]
CUT2 = [(12.0, -8.5), (16.0, -8.5)]
CUT_STEP = 1.1          # the plank step walls are 0.3 tall: short segments keep their triangles above 5 degrees


def _poly(*pieces, step=TOP_STEP):
    """A closed polygon from waypoint pieces (each resampled on its own, the joint points not repeated)."""
    out = []
    for w in pieces:
        pts = _rs(w, CUT_STEP if w in (CUT1, CUT2, CUT1[::-1], CUT2[::-1]) else step)
        if out and (out[-1] - pts[0]).length < 1e-6:
            pts = pts[1:]
        out += pts
    if (out[-1] - out[0]).length < 1e-6:
        out.pop()
    return out


def regions(which=("left", "chan", "rb", "rm", "rf")):
    T = TILE
    rev = lambda w: list(reversed(w))
    R = {
        "left": (_poly([(-T, T), (-T, -T)], [(-T, -T), (-7.0, -T)], rev(L_EDGE), [(-7.0, T), (-T, T)]), BANK_TOP),
        "chan": (_poly(L_EDGE, [(-7.0, -T), (7.0, -T)], rev(R_EDGE), [(7.0, T), (-7.0, T)]), BED_TOP),
        "rb": (_poly(R_BACK, CUT1, [(T, -0.6), (T, T)], [(T, T), (7.0, T)]), BANK_TOP),
        "rm": (_poly(R_MID, CUT2, [(T, -8.5), (T, -0.6)], CUT1[::-1]), PLANK_TOP),
        "rf": (_poly(R_FRONT, [(7.0, -T), (T, -T)], [(T, -T), (T, -8.5)], CUT2[::-1]), BANK_TOP),
    }
    return {k: R[k] for k in which}


# rocks: name -> (centre x, y, footprint w x d, base z, top z, yaw deg, kind, ground) -- spec 2.3; ground = the
# surface round its foot ("sand", "water" or "edge" for the waterline straddlers)
# fix round 1: chunky, flat-crowned boulders (near-vertical upper sides, a crown about 0.75 of the width), not eggs
BIG_R = [(0.0, 0.95, 7), (0.45, 1.0, 7), (0.85, 0.92, 6), (1.0, 0.74, 5)]
MED_R = [(0.0, 0.96, 7), (0.3, 1.0, 7), (0.7, 0.93, 6), (1.0, 0.72, 5)]
SMALL_R = [(0.0, 0.95, 6), (0.4, 1.0, 6), (1.0, 0.5, 4)]
TINY_R = [(0.0, 0.95, 5), (0.45, 1.0, 5), (1.0, 0.5, 3)]
PEB_R = [(0.0, 1.0, 4), (1.0, 0.6, 3)]
KINDS = {"big": BIG_R, "med": MED_R, "small": SMALL_R, "tiny": TINY_R, "peb": PEB_R}
ROCKS = {
    # fix round 1: the top view's footprints (6.6-7.3), flat-crowned and squat (B2-B4 tops 5.6-6.0, H : W about
    # 0.75); B1 keeps the 7.4 top (decision 1); the waterline boulders stand mostly in the widened stream
    "B1": ((-9.4, 11.0), 7.3, 7.3, 0.4, 7.4, -55.0, "big", "edge"),
    "B2": ((9.9, 7.0), 6.9, 7.1, 0.4, 5.6, -20.0, "big", "edge"),
    "B3": ((11.3, -5.2), 7.1, 6.8, 0.4, 5.8, 40.0, "big", "edge"),
    "B4": ((-11.2, -9.4), 7.3, 6.9, 0.4, 5.9, 35.0, "big", "edge"),
    "M1": ((7.0, -10.6), 4.8, 4.6, 0.4, 3.9, 10.0, "med", "water"),
    "M2": ((-6.8, -2.6), 4.6, 4.4, 0.4, 3.8, -25.0, "med", "water"),
    "S1": ((-3.8, 2.1), 2.8, 2.4, 0.4, 2.4, 30.0, "small", "water"),
    # bank rocks (on the sand; their base follows the plank level under them)
    "K1": ((13.6, -13.2), 2.98, 2.72, 1.3, 1.3 + 0.6 * 2.98, 20.0, "med", "sand"),
    "K2": ((-14.0, -2.4), 3.3, 2.9, 1.3, 1.3 + 0.6 * 3.3, 70.0, "med", "sand"),
    "K3": ((13.3, 13.6), 2.38, 2.21, 1.3, 1.3 + 0.6 * 2.38, 5.0, "small", "sand"),
    "K4": ((13.7, 5.9), 2.29, 2.12, 1.3, 1.3 + 0.6 * 2.29, 50.0, "small", "sand"),
    "K5": ((-13.8, -14.0), 3.0, 2.6, 1.3, 1.3 + 0.6 * 3.0, 110.0, "small", "sand"),
    "K6": ((-14.0, 5.9), 3.0, 2.7, 1.3, 1.3 + 0.6 * 3.0, 160.0, "small", "sand"),
    "K8": ((14.4, -10.6), 2.04, 1.87, 1.3, 1.3 + 0.6 * 2.04, 140.0, "small", "sand"),
    "K9": ((12.6, 10.4), 2.04, 1.87, 1.3, 1.3 + 0.6 * 2.04, 75.0, "small", "sand"),
    # small rocks
    "s1": ((13.2, 1.6), 2.0, 1.8, 1.3, 1.6 + 0.6 * 2.0, 10.0, "tiny", "sand"),
    "s2": ((11.3, 0.6), 1.7, 1.5, 0.4, 1.3 + 0.6 * 1.7, 60.0, "tiny", "edge"),
    "s3": ((2.6, -12.2), 1.9, 1.7, 0.4, 1.0 + 0.6 * 1.9, 100.0, "tiny", "water"),
    "s4": ((-13.0, 11.6), 1.9, 1.7, 1.3, 1.6 + 0.6 * 1.9, 35.0, "tiny", "sand"),
    "s5": ((-10.4, 5.8), 1.7, 1.5, 0.4, 1.3 + 0.6 * 1.7, 15.0, "tiny", "edge"),
    "s6": ((-13.6, 0.6), 1.6, 1.4, 1.3, 1.6 + 0.6 * 1.6, 80.0, "tiny", "sand"),
    "s7": ((8.6, -14.6), 1.6, 1.4, 0.4, 1.3 + 0.6 * 1.6, 130.0, "tiny", "edge"),
    "s8": ((4.6, 12.4), 1.3, 1.2, 0.4, 1.0 + 0.6 * 1.3, 45.0, "tiny", "water"),
    "s10": ((-13.0, 8.4), 1.3, 1.2, 1.3, 1.6 + 0.6 * 1.3, 120.0, "tiny", "sand"),
    "s11": ((10.6, 14.4), 1.1, 1.0, 1.3, 1.6 + 0.6 * 1.1, 20.0, "tiny", "sand"),
}
ROCK_SEED = {k: 34000 + i * 37 for i, k in enumerate(ROCKS)}
IN_WATER = [k for k, r in ROCKS.items() if r[7] in ("edge", "water")]

# pebbles on the banks: (x, y, size, brown); fix round 1: 6 brown, 11 grey (the sheet's mix)
PEBBLES = [((-12.0, 14.4), 0.9, False), ((-14.6, 9.4), 0.9, True), ((15.0, 8.2), 0.8, False),
           ((-12.9, 2.6), 1.0, True), ((-15.0, 2.4), 0.7, False), ((-14.5, -10.6), 0.95, False),
           ((-13.2, -11.2), 0.8, True), ((-10.6, -14.9), 0.8, False), ((-14.6, -4.6), 0.75, False),
           ((11.2, 14.6), 0.9, False), ((15.0, 9.8), 0.8, True), ((11.6, 3.8), 1.0, False),
           ((14.9, 0.4), 0.75, True), ((15.2, -8.8), 0.9, False), ((11.2, -12.6), 0.75, True),
           ((-14.2, 13.6), 0.8, False), ((10.6, -15.0), 0.8, False)]


# ---- terrace (the land without booleans) ---------------------------------------------------------------------------
def _key(p):
    return (round(p[0], 3), round(p[1], 3))


def terrace(a, regs, seed=34100):
    """One closed multi-level slab: each region (polygon, level) a flat top; walls where regions of different level
    meet and round the outline (down to z 0); one flat bottom. Returns {"top": {tag: faces}, "wall": [(face, tag,
    neighbour tag or None)], "bottom": faces, "verts": all verts}."""
    bm = a.bm
    vmap = {}

    def V(k, z):
        kk = (k[0], k[1], round(z, 4))
        v = vmap.get(kk)
        if v is None:
            v = vmap[kk] = bm.verts.new((k[0], k[1], z))
        return v
    tops, bnd = {}, {}
    level = {tag: z for tag, (poly, z) in regs.items()}
    tri_keys = {}
    for i, (tag, (poly, z)) in enumerate(regs.items()):
        st = _steiner([poly], [], TOP_STEP, TOP_STEP * 0.42, seed + i)
        co, tris = cdt_region([poly], [], st, tidy=False)
        ks = [_key(c) for c in co]
        tri_keys[tag] = [(ks[i_], ks[j_], ks[k_]) for i_, j_, k_ in tris]
        d = set()
        for t in tri_keys[tag]:
            d |= {(t[0], t[1]), (t[1], t[2]), (t[2], t[0])}
        bnd[tag] = [e for e in d if (e[1], e[0]) not in d]
    owner = {}
    for tag, es in bnd.items():
        for e in es:
            owner[e] = tag
    # every boundary point's levels: its regions' tops, 0 on the outline, plus the colour bands in between
    lv = {}
    outline = []
    for tag, es in bnd.items():
        for e in es:
            nb = owner.get((e[1], e[0]))
            for p in e:
                lv.setdefault(p, set()).add(level[tag])
            if nb is None:
                outline.append(e)
                for p in e:
                    lv[p].add(0.0)
    for p, s in lv.items():
        lo, hi = min(s), max(s)
        s |= {b for b in WALL_BANDS if lo + 0.05 < b < hi - 0.05}
    top_f = {}
    for tag, tris in tri_keys.items():
        z = level[tag]
        top_f[tag] = [bm.faces.new((V(i, z), V(j, z), V(k, z))) for i, j, k in tris]
    walls = []
    for tag, es in bnd.items():
        for e in es:
            nb = owner.get((e[1], e[0]))
            if nb is not None and level[nb] >= level[tag]:
                continue
            lo, hi = (0.0 if nb is None else level[nb]), level[tag]
            ci = [V(e[0], z) for z in sorted(z for z in lv[e[0]] if lo - 1e-6 <= z <= hi + 1e-6)]
            cj = [V(e[1], z) for z in sorted(z for z in lv[e[1]] if lo - 1e-6 <= z <= hi + 1e-6)]
            ia = ib = 0
            while ia < len(ci) - 1 or ib < len(cj) - 1:
                if ib == len(cj) - 1 or (ia < len(ci) - 1 and ci[ia + 1].co.z <= cj[ib + 1].co.z + 1e-6):
                    f = bm.faces.new((ci[ia], cj[ib], ci[ia + 1]))
                    ia += 1
                else:
                    f = bm.faces.new((ci[ia], cj[ib], cj[ib + 1]))
                    ib += 1
                walls.append((f, tag, nb))
    # the bottom: the outline loop (CCW from above) triangulated with a few interior points
    nxt = {e[0]: e[1] for e in outline}
    start = next(iter(nxt))
    loop = [start]
    while nxt[loop[-1]] != start:
        loop.append(nxt[loop[-1]])
    poly = [Vector(k) for k in loop]
    st = _steiner([poly], [], BOTTOM_STEP, BOTTOM_STEP * 0.4, seed + 50)
    co, tris = cdt_region([poly], [], st, tidy=False)
    ks = [_key(c) for c in co]
    bot_f = [bm.faces.new((V(ks[i], 0.0), V(ks[k], 0.0), V(ks[j], 0.0))) for i, j, k in tris]
    allv = list(vmap.values())
    bmesh.ops.recalc_face_normals(bm, faces=_faces(allv))
    a._finish(allv, EARTH, tint=1.0)
    return {"top": top_f, "wall": walls, "bottom": bot_f, "verts": allv}


def _paint_terrace(a, T, seed):
    """Sand tops with broad light patches and a pale shore band, darker contact round rock feet; the bed top deep
    blue with broad light patches; walls sand over an earth band; the bottom earth. By position only."""
    nf_s = K.noise_field(scale=0.2, seed=seed)
    nf_b = K.noise_field(scale=BED_PATCH_SCALE, seed=seed + 1)
    # fix round 1: the light fraction is smoothed over each face's neighbours before it is quantised, so the
    # sand / bed patches change over bands of faces (no lone triangle shards); the dark pebble contact ring round
    # the rock feet is gone (it read as dark wedges in the top view)
    tval = {}
    for tag, faces in T["top"].items():
        for f in faces:
            c = f.calc_center_median()
            if tag == "chan":
                tval[f] = min(1.0, max(0.0, (nf_b(c) - BED_PATCH_LEVEL) / 0.2))
            else:
                d = min(_dist_line(c, L_EDGE), _dist_line(c, R_EDGE))
                shore = 0.5 if d < 1.1 else 0.25 if d < 1.9 else 0.0
                tval[f] = max(min(1.0, max(0.0, (nf_s(c) - 0.05) / 0.22)), shore)
    for _ in range(2):
        nxt = {}
        for f, t in tval.items():
            nb = [tval[g] for e in f.edges for g in e.link_faces if g is not f and g in tval]
            nxt[f] = 0.5 * t + 0.5 * (sum(nb) / len(nb)) if nb else t
        tval = nxt
    for tag, faces in T["top"].items():
        for f in faces:
            key = _mix(BED, BED_LIGHT, tval[f]) if tag == "chan" else _mix(SAND, SAND_LIGHT, tval[f])
            f.material_index = a._mi(key)
    for f, tag, nb in T["wall"]:
        z = f.calc_center_median().z
        if tag == "chan":
            key = EARTH
        elif nb == "chan":            # the inner wall: sand above the water, earth-blended below
            key = SAND if z > WALL_BANDS[1] else _mix(SAND, EARTH, 0.5)
        elif nb is None:              # outer walls (spec 5.5, the cross-section's sand over grey): sand above
            # 0.65 h, a 50 % band, an earth-leaning foot (fix round 1; was sand down to 0.45)
            key = SAND if z > WALL_BANDS[1] else _mix(SAND, EARTH, 0.5) if z > WALL_BANDS[0] else _mix(SAND, EARTH, 0.75)
        else:                         # plank steps
            key = SAND
        f.material_index = a._mi(key)
    for f in T["bottom"]:
        f.material_index = a._mi(EARTH)
    tops_s = [f for tag, fs in T["top"].items() if tag != "chan" for f in fs]
    tops_b = T["top"].get("chan", [])
    _mottle(a, tops_s, 0.03, 0.15, seed + 2)        # broad (about 6-stud) Tint patches, never per triangle
    _mottle(a, tops_b, 0.03, 0.2, seed + 3)
    _mottle(a, [w[0] for w in T["wall"]] + T["bottom"], 0.03, 0.8, seed + 4)


# ---- rocks -----------------------------------------------------------------------------------------------------------
def rock(a, name, at_origin=False):
    """One faceted rock: the convex hull of jittered rings (flat bottom, widest low, a flat crown), its facets merged
    where near-coplanar and re-triangulated. Rocks in the hero sink into the slab they stand on."""
    (cx, cy), w, d, z0, z1, yaw, kind, ground = ROCKS[name]
    seed = ROCK_SEED[name]
    if ground == "sand":              # sunk 0.3 into the plank under it (the middle right plank is 0.3 higher)
        dz = _bank_level(cx, cy) - 0.3 - z0
        z0, z1 = z0 + dz, z1 + dz
    if at_origin:
        cx, cy, z1, z0 = 0.0, 0.0, z1 - z0, 0.0
    vs = K.hull_rock(a, (w, d, z1 - z0), loc=(cx, cy, z0), seed=seed, mat=ROCK, rings=KINDS[kind], jitter=0.07,
                     rot=math.radians(yaw), keep_bottom=True)
    bmesh.ops.dissolve_limit(a.bm, angle_limit=math.radians(4.0), verts=vs,
                             edges=list({e for f in _faces(vs) for e in f.edges}))
    vs = [v for v in vs if v.is_valid]
    _tri(a.bm, _faces(vs))
    bmesh.ops.recalc_face_normals(a.bm, faces=_faces(vs))
    _paint_rock(a, vs, seed)
    return vs


def _paint_rock(a, vs, seed):
    """Rock with a per-rock Tint; the wet foot (face centres below the water top) 25 % toward the earth."""
    tint = random.Random(seed).uniform(0.95, 1.05)
    k_wet = _mix(ROCK, EARTH, 0.25)
    for f in _faces(vs):
        f.material_index = a._mi(k_wet if f.calc_center_median().z < WATER_TOP else ROCK)
    _mottle(a, _faces(vs), 0.04, 0.5, seed, tint=tint)


def pebble(a, i):
    (x, y), s, brown = PEBBLES[i]
    seed = 34500 + i * 13
    rng = random.Random(seed)
    vs = K.hull_rock(a, (s, s * rng.uniform(0.75, 0.9), 0.15 + s * 0.55), loc=(x, y, _bank_level(x, y) - 0.15), seed=seed,
                     mat=PEBBLE if brown else ROCK, rings=PEB_R, jitter=0.1, rot=rng.uniform(0, 6.28),
                     keep_bottom=True)
    _tri(a.bm, _faces(vs))
    bmesh.ops.recalc_face_normals(a.bm, faces=_faces(vs))
    _mottle(a, _faces(vs), 0.03, 0.8, seed, tint=rng.uniform(0.94, 1.06))
    return vs


def _bank_level(x, y):
    """The bank top under a point (the right bank's middle plank is 0.15 higher)."""
    return PLANK_TOP if (x > 0 and -8.5 < y < -0.6) else BANK_TOP


# ---- water and foam ----------------------------------------------------------------------------------------------------
HOLES = {}
HOLE_CORNERS = {"big": 9, "med": 8}     # small rocks: 6
HOLE_GAP = 0.06            # fix round 1: the water / foam stand this far off the rock (was 0.09 + up to 0.3 of
                           # simplification loss: the dark ring round every rock)
HOLE_GAP_EDGE = 0.14


def _hole_of(vs, zcut=1.06, margin=HOLE_GAP, nmax=6):
    """The 2D hole a rock makes in the water and foam: the convex hull of its section at the foam's top (the rock
    widens upward there, so this also clears the water below), at most 10 corners with no edge under 0.35, offset by
    margin plus what the simplification cut off."""
    pts = [v.co.copy() for v in vs if v.co.z <= zcut]
    for e in {e for v in vs for e in v.link_edges}:
        p, q = e.verts[0].co, e.verts[1].co
        if (p.z - zcut) * (q.z - zcut) < 0:
            t = (zcut - p.z) / (q.z - p.z)
            pts.append(p + (q - p) * t)
    hull = _hull2([(p.x, p.y) for p in pts])
    simp = _simplify_convex(hull, nmax)
    while len(simp) > 5:
        el = [(simp[(i + 1) % len(simp)] - simp[i]).length for i in range(len(simp))]
        i = min(range(len(simp)), key=lambda k: el[k])
        if el[i] >= 0.35:
            break
        simp.pop((i + 1) % len(simp) if el[i - 1] > el[(i + 1) % len(simp)] else i)
    loss = max(min(_seg_d(q, simp[i], simp[(i + 1) % len(simp)]) for i in range(len(simp))) if not any(
        (q - s).length < 1e-6 for s in simp) else 0.0 for q in hull)
    return _offset_poly(simp, margin + loss)


def holes():
    """Every in-water / waterline rock's hole (from a throwaway build of the rocks)."""
    if not HOLES:
        a = K.fk().Asset("_m034_probe", "probe")
        for name in IN_WATER:
            # the waterline straddlers get a wider margin: the union and cleanup at the bank top (1.6) move their
            # faces by up to about 0.1 (a 0.06 hole let B1 cut the water)
            HOLES[name] = _hole_of(rock(a, name), nmax=HOLE_CORNERS.get(ROCKS[name][6], 6),
                                   margin=HOLE_GAP_EDGE if ROCKS[name][7] == "edge" else HOLE_GAP)
        a.bm.free()
    return HOLES


def water_outline():
    """The channel polygon inset WATER_GAP off the bank walls, its seam faces SEAM_INSET inside the tile."""
    T = TILE
    chan = _poly(L_EDGE, [(-7.0, -T), (7.0, -T)], list(reversed(R_EDGE)), [(7.0, T), (-7.0, T)], step=100.0)
    out = _offset_poly(chan, -WATER_GAP)
    for p in out:
        p.y = max(-T + SEAM_INSET, min(T - SEAM_INSET, p.y))
    return out


def water(a, with_holes=True):
    """The water slab: top 1.0, bottom 0.76 (0.06 over the bed), 0.06 off the bank walls, cut round every rock in
    it. Flat top: no ripples, no stripes ("Water is a separate plane (no baked details)")."""
    poly = _resample_poly(water_outline(), 6.0)
    neg = list(holes().values()) if with_holes else []
    co, tris = cdt_region([poly], neg, (), min_island=1.0)
    return slab(a, co, tris, WATER_TOP, WATER_BOT, WATER)


FOAM_GAP = 0.07            # the foam stands this far off the bank walls (>= 0.05 off the land)
FOAM_RIB_W = {"L": (0.6, 1.35), "R": (0.2, 0.5)}   # the shore ribbons' width past FOAM_GAP (lobed)
FOAM_CAP = 0.9             # the rounded end of each ribbon segment
# fix round 1: each bank ribbon is broken into segments (arclength from the back seam: start, end), gaps between
FOAM_SEGS = {"L": [(0.6, 7.4), (8.8, 16.0), (17.6, 25.2), (26.6, 34.6)],
             "R": [(0.8, 6.6), (8.2, 15.4), (16.8, 23.4), (24.8, 30.0), (31.4, 34.4)]}
FOAM_RIB_HOLES = {"L": (11.6, 21.0), "R": (11.0, 26.8)}   # a few round holes (arclength)
# collars: lobed blobs (10-12 corners, +-30 % jitter) whose inner edge is the rock's hole (no gap) and whose outer
# edge stands 0.8-1.4 off the rock
FOAM_WAKE = 0.3
FOAM_RING = {"B1": 0.85, "B2": 0.85, "B3": 0.85, "B4": 0.85, "M1": 0.85, "M2": 0.85, "S1": 0.8, "s3": 0.8,
             "s8": 0.8}
FOAM_BLOBS = [((-3.6, 10.6), 0.42), ((2.0, 6.6), 0.38), ((-1.4, -7.8), 0.4), ((1.0, 13.6), 0.36),
              ((-4.4, -14.2), 0.42), ((5.6, 0.8), 0.36)]


def _cum(way):
    P = [_v2(p) for p in way]
    cum = [0.0]
    for p, q in zip(P, P[1:]):
        cum.append(cum[-1] + (q - p).length)
    return P, cum


def _at(way, s):
    """The point at arclength s along a polyline and the unit tangent there."""
    P, cum = _cum(way)
    s = max(0.0, min(cum[-1], s))
    for i in range(len(P) - 1):
        if s <= cum[i + 1] + 1e-9:
            t = (s - cum[i]) / max(1e-9, cum[i + 1] - cum[i])
            return P[i].lerp(P[i + 1], t), (P[i + 1] - P[i]).normalized()
    return P[-1], (P[-1] - P[-2]).normalized()


def _arc_pts(way, s0, s1, step):
    """Points (arclength, point, tangent) along a polyline between arclengths s0 and s1, every <= step, plus extra
    points in the end caps and at the jog corners. Returns (points, total length)."""
    P, cum = _cum(way)

    def at(s):
        # the tangent across +-0.6 (so a jog corner offsets along its bisector and the outer edge never crosses)
        p, _t = _at(way, s)
        q0, q1 = _at(way, s - 0.6)[0], _at(way, s + 0.6)[0]
        return p, (q1 - q0).normalized()
    ss = {s0, s1, s0 + 0.3, s0 + FOAM_CAP * 0.75, s1 - 0.3, s1 - FOAM_CAP * 0.75}
    ss |= {c for c in cum if s0 + FOAM_CAP < c < s1 - FOAM_CAP}          # the jog corners
    n = max(1, int(math.ceil((s1 - s0) / step)))
    ss |= {s0 + (s1 - s0) * k / n for k in range(n + 1)}
    ss = sorted(ss)
    out = [ss[0]]
    for s in ss[1:]:
        if s - out[-1] > 0.25:
            out.append(s)
    return [(s, *at(s)) for s in out], cum[-1]


def _ray_poly(c, d, poly):
    """Distance from c along unit d to the boundary of a convex polygon containing c."""
    best = None
    n_ = len(poly)
    for i in range(n_):
        a, b = poly[i], poly[(i + 1) % n_]
        e = b - a
        den = d.x * e.y - d.y * e.x
        if abs(den) < 1e-12:
            continue
        w = a - c
        t = (w.x * e.y - w.y * e.x) / den
        u = (w.x * d.y - w.y * d.x) / den
        if t > 0 and -1e-9 <= u <= 1 + 1e-9:
            best = t if best is None else min(best, t)
    return best or 0.0


def _collar(hole, w, n, rng):
    """A lobed foam blob round a rock hole: n corners, each w * (1 +- 0.3) out from the hole, the wake side
    (downstream, -Y) FOAM_WAKE wider and the upstream side as much narrower (the foam trails the rock)."""
    c = sum(hole, Vector((0.0, 0.0))) / len(hole)
    th0 = rng.uniform(0, 2 * math.pi)
    out = []
    for k in range(n):
        th = th0 + 2 * math.pi * (k + rng.uniform(-0.15, 0.15)) / n
        d = Vector((math.cos(th), math.sin(th)))
        out.append(c + d * (_ray_poly(c, d, hole) + w * (1.0 - FOAM_WAKE * d.y) * rng.uniform(0.7, 1.3)))
    return out


def _bank_neg(edge_way, side, grow):
    """The bank region beside an inner edge, grown `grow` toward the water (a neg polygon for the foam)."""
    T = TILE + 1.0
    line = _offset_line(_rs(edge_way, 0.8), -grow if side < 0 else grow)
    return [Vector((side * T, T))] + line + [Vector((side * T, -T))]


def foam_regions():
    """(pos, neg) 2D polygons of the foam (fix round 1: soft, lobed and broken, hugging the rocks and the sand):
    each bank's shore ribbon in 4-5 segments with lobed widths and rounded ends, a lobed collar round each rock in the
    water, a few loose blobs; neg: the rock holes (HOLE_GAP off the rock), both banks (grown FOAM_GAP into the water),
    a few round holes in the ribbons, and everything past the seams."""
    rng = random.Random(34701)
    pos, neg = [], []
    for tag, way, side in (("L", L_EDGE, -1), ("R", R_EDGE, 1)):
        ph = 0.4 if side < 0 else 2.1
        for s0, s1 in FOAM_SEGS[tag]:
            pts, L = _arc_pts(way, s0, s1, 2.4)
            inner, outer = [], []
            for s, p, t in pts:
                # the water side of travel: L runs -Y with the water on its left (+X), R with it on its right
                nrm = Vector((-t.y, t.x)) if side < 0 else Vector((t.y, -t.x))
                w0, w1 = FOAM_RIB_W[tag]
                w = w0 + (w1 - w0) * (0.5 + 0.5 * math.sin(s * 0.85 + ph))
                w *= rng.uniform(0.85, 1.15)
                d = min(s - s0, s1 - s)
                if d < FOAM_CAP:                 # a rounded (quarter-ellipse) end, blunt at the tip
                    w *= max(0.3, math.sqrt(max(0.0, 1.0 - (1.0 - d / FOAM_CAP) ** 2)))
                inner.append(p)
                outer.append(p + nrm * (FOAM_GAP + w))
            rib = inner + list(reversed(outer))
            if sum(rib[i].x * rib[(i + 1) % len(rib)].y - rib[(i + 1) % len(rib)].x * rib[i].y
                   for i in range(len(rib))) < 0:
                rib = list(reversed(rib))
            pos.append(rib)
            for sh in FOAM_RIB_HOLES[tag]:
                if s0 + FOAM_CAP < sh < s1 - FOAM_CAP:
                    p, t = _at(way, sh)
                    nrm = Vector((-t.y, t.x)) if side < 0 else Vector((t.y, -t.x))
                    neg.append(_blob(p + nrm * (FOAM_GAP + 0.55), 0.2, 5, rng.uniform(0, 6.3), 0.85))
        neg.append(_bank_neg(way, side, FOAM_GAP))
    hs = holes()
    for name, w in FOAM_RING.items():
        n = 11 if ROCKS[name][6] == "big" else 10
        pos.append(_collar(hs[name], w, n, rng))
    for c, r in FOAM_BLOBS:
        a0 = rng.uniform(0, 6.3)
        pos.append([Vector(c) + Vector((math.cos(a_), math.sin(a_) * 0.8)) * r * rng.uniform(0.75, 1.25)
                    for a_ in [a0 + 2 * math.pi * k / 6 for k in range(6)]])
    neg += list(hs.values())
    T = TILE + 1.0
    s = TILE - SEAM_INSET - 0.03
    neg.append([Vector((-T, s)), Vector((T, s)), Vector((T, T)), Vector((-T, T))])
    neg.append([Vector((-T, -T)), Vector((T, -T)), Vector((T, -s)), Vector((-T, -s))])
    return pos, neg


def foam(a):
    pos, neg = foam_regions()
    co, tris = cdt_region(pos, neg, min_island=0.08)
    return slab(a, co, tris, FOAM_Z[1], FOAM_Z[0], FOAM)


# ---- parts -----------------------------------------------------------------------------------------------------------
def _on_left_bank(name):
    (x, y), w, d, z0, z1, yaw, kind, ground = ROCKS[name]
    return ground == "sand" and x < 0


def _in_channel(name):
    return ROCKS[name][7] == "water" and ROCKS[name][6] in ("small", "tiny")


def bank_slab_part(a):
    """Sand / Bank Slab (Base): the left bank as built in the hero, with its small rocks and pebbles."""
    T = terrace(a, regions(("left",)), seed=34110)
    _paint_terrace(a, T, 34120)
    for name in ROCKS:
        if _on_left_bank(name):
            rock(a, name)
    for i, (p, s, b) in enumerate(PEBBLES):
        if p[0] < 0:
            pebble(a, i)


def bed_slab_part(a):
    """Stream Bed Slab (Sand/Rock): the channel slab with its in-stream small rocks."""
    T = terrace(a, regions(("chan",)), seed=34130)
    _paint_terrace(a, T, 34140)
    for name in ROCKS:
        if _in_channel(name):
            rock(a, name)


def water_plane_part(a):
    water(a, with_holes=False)


def rock_large_part(a):
    rock(a, "B4", at_origin=True)


def rock_medium_part(a):
    rock(a, "M2", at_origin=True)
    # the small rock lodged at its foot (the parts breakdown)
    vs = K.hull_rock(a, (1.5, 1.3, 1.0), loc=(1.9, -1.5, -0.05), seed=34901, mat=ROCK, rings=TINY_R, jitter=0.07,
                     rot=0.6, keep_bottom=True)
    _tri(a.bm, _faces(vs))
    bmesh.ops.recalc_face_normals(a.bm, faces=_faces(vs))
    _paint_rock(a, vs, 34901)


def rock_small_part(a):
    rock(a, "S1", at_origin=True)


# ---- hero ------------------------------------------------------------------------------------------------------------
def hero_land(a):
    """The terrace (banks, planks, channel) first, then the rocks largest first, then the pebbles: closed shells the
    union fuses one at a time."""
    T = terrace(a, regions(), seed=34150)
    _paint_terrace(a, T, 34160)
    for name in sorted(ROCKS, key=lambda n: -ROCKS[n][1] * ROCKS[n][2]):
        rock(a, name)
    for i in range(len(PEBBLES)):
        pebble(a, i)


def hero_water(a):
    water(a)
    foam(a)


NOTES = {
    HERO: "streambed section terrain tile (32 x 32; ground 0, bed 0.7, water 1.0, banks 1.6): two flat sand bank "
          "slabs with jogged plank edges, a broad recessed bed slab under a thin see-through water plane, soft lobed "
          "foam ribbons and rock collars, four chunky flat-crowned boulders on the waterlines, two mid rocks in the "
          "water, one mid-stream rock, bank "
          "rocks and pebbles; one closed land shell plus closed water and foam shells (two water pieces). Flow "
          "+Y -> -Y. 14 water_foam + 3 water_flow sockets",
    BANK_P: "Sand / Bank Slab (reusable): the left bank plank slab (top 1.6) with its small rocks and pebbles",
    BED_P: "Stream Bed Slab (reusable): the channel slab (top 0.7, earth sides) with its in-stream small rocks",
    WATER_P: "Water Plane (reusable): the thin see-through water slab (top 1.0) with the 3 flow-strip sockets",
    ROCK_LP: "Rock Piece Large (reusable): a big flat-faceted boulder with a flat crown (B4)",
    ROCK_MP: "Rock Piece Medium (reusable): a squat chunky rock with a small rock at its foot (M2)",
    ROCK_SP: "Rock Piece Small (reusable): a small flat-topped rock (S1)",
}

# ---- stages 5 + 6 (spec section 7) -------------------------------------------------------------------------------------
# Stage 5: nothing glows (decision 8): no emissive key, no light. The water and foam are see-through water pieces.
# Stage 6 (decision 6): 3 water_flow beams (the sheet's "Flow Strips" overlay, +Y -> -Y) and 14 water_foam sockets
# (one per rock standing in or straddling the water, scaled by size, plus 4 along the bank edges).
# fix round 1: the strips run in the clear lanes of the widened stream, every strip edge >= 0.5 off every rock in
# the water (flow_clearance()): the centre lane between S1 / M2 and s3, a back-left lane between B1 and S1, a
# right lane between s8 / B2 / B3 / M1 and s3
FLOW = [((-0.4, 15.5, 1.03), (-0.4, -15.5, 1.03), 2.6), ((-3.8, 15.5, 1.03), (-3.8, 4.6, 1.03), 1.2),
        ((2.6, 15.5, 1.03), (2.6, -9.6, 1.03), 1.4)]
FOAM_FX_ROCKS = (("B1", 1.0), ("B2", 1.0), ("B3", 1.0), ("B4", 1.0), ("M1", 0.8), ("M2", 0.8),
                 ("S1", 0.6), ("s3", 0.4), ("s8", 0.4), ("s2", 0.4))
FOAM_FX = [(ROCKS[n][0], sc) for n, sc in FOAM_FX_ROCKS] + [
    ((-9.9, 0.8), 0.7), ((-9.9, -4.8), 0.7), ((9.4, 12.0), 0.7), ((7.3, -13.4), 0.7)]


def flow_clearance():
    """Per flow strip: the smallest distance from its edge (centre line +- width / 2) to any rock hole."""
    out = []
    for p, e, w in FLOW:
        a_, b_ = _v2(p), _v2(e)
        best = 1e9
        n = int((b_ - a_).length / 0.2) + 1
        for name, hp in holes().items():
            for k in range(n + 1):
                q = a_.lerp(b_, k / n)
                d = -1.0 if _inside(q, hp) else _dist_line(q, hp, True)
                best = min(best, d - w / 2)
        out.append(round(best, 2))
    return out


def _sockets(o, hero=True):
    off = Vector(o[OFF])
    for p, e, w in FLOW:
        K.socket(o, "water_flow", Vector(p) - off, end=tuple(Vector(e) - off), width=w)
    if hero:
        for (x, y), sc in FOAM_FX:
            K.socket(o, "water_foam", Vector((x, y, 1.05)) - off, scale=sc)


# ---- union, cleanup (m033 / m031) ------------------------------------------------------------------------------------
UNION_RETRIES = []


def _union_fine(o):
    """M.union_loose with no post-union weld and a guard against a union that drops most of the mesh (m033). Shells
    are added one at a time in face order (terrace, rocks largest first, pebbles)."""
    bpy.context.view_layer.update()
    others = M.split_loose(o)
    bpy.context.view_layer.update()
    for p in others:
        for attempt in range(4):
            keep = o.data.copy()
            n0 = len(o.data.polygons) + len(p.data.polygons)
            m = o.modifiers.new("U", "BOOLEAN")
            m.operation, m.solver, m.object = "UNION", "EXACT", p
            m.material_mode = "TRANSFER"
            with M._override(o):
                bpy.ops.object.modifier_apply(modifier=m.name)
            if len(o.data.polygons) >= 0.6 * n0 or attempt == 3:
                bpy.data.meshes.remove(keep)
                break
            bad = o.data
            o.data = keep
            bpy.data.meshes.remove(bad)
            UNION_RETRIES.append((p.name, attempt))
            p.location += Vector((0.004, 0.003, 0.002)) * (attempt + 1)
            bpy.context.view_layer.update()
        me = p.data
        bpy.data.objects.remove(p, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    M.drop_specks(bm, min_area=0.02)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    K.drop_unused_slots(o)
    return len(others)


PLANES = (0.0, BED_TOP, BANK_TOP, PLANK_TOP)


def _finish(o):
    o[OFF] = list(Vector(o[OFF]) + m012._bottom_centre(o))
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
        m012._force_slivers(o)
        o[OFF] = list(Vector(o[OFF]) + m012._bottom_centre(o))
        res = M.finish(o, union=False, uv=False)
    return res


def _polish(o):
    """Quads split, slivers forced open, origin back at the bottom centre. (m033)"""
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
    return {"split": split, "forced": forced}


def _recentre(o):
    bc = m012._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


def _uv(o):
    for p in o.data.polygons:
        p.use_smooth = False
    M.smart_uv(o, **UV)
    return m012._uv_unfold(o)


def _join_built(o, fn, name):
    """Build fn into a temporary object in the same build frame as o and join it into o (no union)."""
    a = K.fk().Asset(PFX + name, "probe", seed=7, tint_var=0.0)
    fn(a)
    c = a.finish(collection=o.users_collection[0], mark_asset=False, origin=None)
    c.matrix_world = o.matrix_world @ Matrix.Translation(-Vector(o[OFF]))
    bpy.context.view_layer.update()
    with M._override(o):
        c.select_set(True)
        with bpy.context.temp_override(selected_objects=[o, c], selected_editable_objects=[o, c]):
            bpy.ops.object.join()
    return o


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m034_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith(("_m034", "_probe", "T_Calib",
                                                                                 "StreambedSection"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


# K.check's baked-shading test puts the grey rock and the grey-taupe earth in one family (both near-grey), and the earth
# covers the whole flat underside, which faces down: a real material region, not light painted in
SHADING_OK = ("earth is the sheet's grey-taupe slab material (Underside View, Thickness / Cross-Section, the front "
              "cell's bed face): the flat underside, the bed slab's sides and the walls' foot band, painted by "
              "position; the K.check family lumps it with the grey rock")
SHADING_OK_OBJS = (HERO, BANK_P)     # fix round 1: BedSlab measures 0.0 without it (verifier), so no waiver there

# name, builder, role, union, collision
PARTS = ((BANK_P, bank_slab_part, True, "precise"), (BED_P, bed_slab_part, True, "precise"),
         (WATER_P, water_plane_part, False, "none"), (ROCK_LP, rock_large_part, False, "hull"),
         (ROCK_MP, rock_medium_part, True, "hull"), (ROCK_SP, rock_small_part, False, "hull"))
TARGET_SIZE = ((32.0, 0.3), (32.0, 0.3), (8.0, 0.6))


def _make(name, fn, role, budget, union, collision):
    t0 = time.time()
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget, collision=collision,
             tint_var=0.0)
    off = M._build_offset(fn)
    o[OFF] = list(off)
    # booleans at the world origin (m030): M.display puts it back in its slot
    o.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    lg = {}
    if name == WATER_P:
        _recentre(o)
        m016._weld(o, 1e-4)
        lg["uv_cut"] = _uv(o)
        _sockets(o, hero=False)
        return o, lg
    if union:
        lg["shells_merged"] = _union_fine(o)
        lg["clean"] = {k: v for k, v in m016._clean_mesh(o, tuple(z - off.z for z in PLANES)).items()
                       if not isinstance(v, (list, dict))}
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    lg["bowties"] = M.fix_bowties(o)
    K.drop_unused_slots(o)
    lg["uv_cut"] = _uv(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


def _make_hero():
    t0 = time.time()
    o, lg = None, {}
    o = M.mk(SHEET, HERO, hero_land, subject=TITLE, role="hero", notes=NOTES[HERO], budget=4000, collision="precise",
             tint_var=0.0)
    off = M._build_offset(hero_land)
    o[OFF] = list(off)
    o.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    lg["t_build"] = round(time.time() - t0, 1)
    lg["shells_merged"] = _union_fine(o)
    lg["t_union"] = round(time.time() - t0, 1)
    lg["clean"] = {k: v for k, v in m016._clean_mesh(o, PLANES).items() if not isinstance(v, (list, dict))}
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    lg["bowties_land"] = M.fix_bowties(o)
    lg["land"] = {k: v for k, v in M.audit(o).items() if k in ("tris", "shells", "nonmanifold_edges",
                                                                  "nonmanifold_verts", "boundary_edges")}
    lg["land_self_hits"] = m016._self_hits(o)[0]
    _join_built(o, hero_water, "water")
    lg["bowties_water"] = M.fix_bowties(o)
    _recentre(o)
    K.drop_unused_slots(o)
    lg["uv_cut"] = _uv(o)
    _sockets(o)
    lg["t_total"] = round(time.time() - t0, 1)
    return o, lg


def shells_report(o):
    """Per shell: its kind (land / water / foam), tris, non-manifold edges and verts, boundary edges."""
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
        kind = "foam" if ks == [FOAM] else "water" if ks == [WATER] else "land"
        out.append({"kind": kind, "tris": sum(len(f.verts) - 2 for f in fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary)})
    bm.free()
    return out


def _inverted(o):
    """Faces whose normal points into their own shell's solid (odd ray parity from just outside the face, counted
    against that shell only: the water and foam shells are stacked over the land on purpose). (m033)"""
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n_sh = M._shell_ids(bm)
    bad = 0
    for k in range(n_sh):
        fs = [f for f in bm.faces if ids[f.index] == k]
        vs = list({v for f in fs for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        for f in fs:
            # a ray tilted a little off the normal (a ray along it can run through an edge and count both of its
            # faces), hits at one point counted once
            d = (f.normal + Vector((0.031, 0.017, 0.023))).normalized()
            p = f.calc_center_median() + d * 1e-4
            n, x, last = 0, p.copy(), None
            for _ in range(50):
                hit = tree.ray_cast(x, d)
                if hit[0] is None:
                    break
                if last is None or (hit[0] - last).length > 1e-4:
                    n += 1
                last = hit[0].copy()
                x = hit[0] + d * 1e-4
            bad += n % 2
    bm.free()
    return bad


def build(render=True, parts=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    UNION_RETRIES.clear()
    palette()
    HOLES.clear()
    holes()
    objs, log = {}, {}
    if parts:
        for name, fn, union, coll in PARTS:
            objs[name], log[name] = _make(name, fn, "part", 1000, union, coll)
    h, log["hero"] = _make_hero()
    log["union_retries"] = list(UNION_RETRIES)
    _cleanup_tmp()
    _bed_finish()
    order = [h] + [objs[n] for n, *_ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
        if o.name in SHADING_OK_OBJS:
            o["kit_shading_ok"] = SHADING_OK
        elif "kit_shading_ok" in o:
            del o["kit_shading_ok"]
    out = report(order)
    out["log"] = log
    out["build_s"] = round(time.time() - t0, 1)
    if render:
        out["views"] = render_views(order)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


def report(order):
    h = order[0]
    audits = [M.audit(o) for o in order]
    self_hits = {o.name: m016._self_hits(o)[0] for o in order}
    thin = {o.name: m012._thin(o, POLISH_LIM) for o in order}
    inverted = {o.name: _inverted(o) for o in order}
    problems = list(K.check(order))
    shells = shells_report(h)
    kinds = [s["kind"] for s in shells]
    if kinds.count("land") != 1 or kinds.count("water") != 1 or "foam" not in kinds:
        problems.append(f"{HERO}: shells {kinds.count('land')} land / {kinds.count('water')} water / "
                        f"{kinds.count('foam')} foam, expected one land and one water shell plus foam")
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
        if o is not h and au["shells"] != 1:
            problems.append(f"{o.name}: {au['shells']} shells")
        if au["normals"] != "outward":
            problems.append(f"{o.name}: normals {au['normals']}")
        if self_hits[o.name]:
            problems.append(f"{o.name}: {self_hits[o.name]} self-intersecting face pairs")
        if thin[o.name]["under"]:
            problems.append(f"{o.name}: {thin[o.name]['under']} faces with a corner under {POLISH_LIM} deg")
        if inverted[o.name]:
            problems.append(f"{o.name}: {inverted[o.name]} inverted faces")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    socks = [c.get("vfx_kind") for c in h.children if c.get("vfx_kind")]
    if socks.count("water_foam") != 14 or socks.count("water_flow") != 3:
        problems.append(f"{HERO}: sockets {socks.count('water_foam')} foam / {socks.count('water_flow')} flow, "
                        f"expected 14 / 3")
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    return {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                          "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                          "ngons", "dup_verts")} for au in audits],
            "shells": {k: {"n": sum(1 for x in shells if x["kind"] == k),
                           "tris": sum(x["tris"] for x in shells if x["kind"] == k),
                           "bad": sum(x["nonmanifold_edges"] + x["nonmanifold_verts"] + x["boundary_edges"]
                                      for x in shells if x["kind"] == k)} for k in ("land", "water", "foam")},
            "thin": thin, "self_hits": self_hits, "inverted": inverted, "problems": problems, "uv": uv,
            "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
            "sockets": {k: socks.count(k) for k in set(socks)}}


# ---- renders -----------------------------------------------------------------------------------------------------------
# the sheet's comparison cameras (decision 3): the hero is a front-right camera (35, 28), the r34 a back-left one
# (225, 32), the side cell a -X camera; the *_sheet shots use a 3x longer lens and hide the studio floor (the sheet
# draws no ground shadow)
SHEET_VIEWS = {"f34_sheet": (35, 28), "r34_sheet": (225, 32), "front_sheet": (0, 5), "side_sheet": (270, 5),
               "rear_sheet": (180, 5), "top_sheet": (0, 89)}
SHEET_LENS = 3.0
JUNC_CU = (-40, 22, (9.6, -5.6, 2.4), 4.6)      # close-up 2: B3 half on the right bank, half in the water
SECT_CU = (0, 12, (-8.0, -16.0, 1.6), 6.0)      # close-up 3: the front seam face, the left bank and the channel
PARTS_SHOT = (35, 28)


def _long_lens(kit):
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


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded Construction: the water plane at the bottom, the two
    bank slabs (the right one mirrored) and the bed slab above it, the rock pieces flying over their spots."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []

    def put(tag, part, m):
        if part not in by:
            return
        c = bpy.data.objects.new(f"{PFX}expl_{tag}", by[part].data)
        coll.objects.link(c)
        c.matrix_world = m
        shown.append(c)
    x0 = objs[0].location.x + 70
    o0 = Matrix.Translation((x0, objs[0].location.y, 0))
    tr = lambda o, d: o0 @ Matrix.Translation(d) @ Matrix.Translation(Vector(by[o][OFF]))
    put("water", WATER_P, tr(WATER_P, (0, 0, -3.0)))
    put("bed", BED_P, tr(BED_P, (0, 0, 2.0)))
    put("bank_l", BANK_P, tr(BANK_P, (-2.5, 0, 2.0)))
    if BANK_P in by:
        put("bank_r", BANK_P, o0 @ Matrix.Translation((2.5, 0, 2.0)) @ Matrix.Diagonal((-1, 1, 1, 1))
            @ Matrix.Translation(Vector(by[BANK_P][OFF])))
    for tag, part, (x, y), z, s in (("rl1", ROCK_LP, (-9.5, 4.0), 9.0, 1.0), ("rl2", ROCK_LP, (9.5, -6.0), 10.0, 0.9),
                                    ("rm1", ROCK_MP, (-10.5, -9.0), 7.5, 0.8), ("rm2", ROCK_MP, (11.0, 8.0), 8.0, 0.7),
                                    ("rs1", ROCK_SP, (-3.0, 2.0), 6.0, 1.0), ("rs2", ROCK_SP, (3.0, -8.0), 6.5, 0.8),
                                    ("rs3", ROCK_SP, (-13.0, 12.0), 6.0, 0.7), ("rs4", ROCK_SP, (13.0, -13.0), 6.0, 0.7)):
        if part in by:
            put(tag, part, o0 @ Matrix.Translation((x, y, z)) @ Matrix.Diagonal((s, s, s, 1)))
    bpy.context.view_layer.update()
    return shown


def render_close(objs, path, az, el, centre, radius):
    """A close-up from (az, el), framed on a sphere (centre, radius) (m023 / m031)."""
    kit = K.NS["KIT"]
    fb = kit["frame_box"]
    c = Vector(centre)
    box = [c + Vector((dx, dy, dz)) * radius for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
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


def render_views(objs, close=True):
    h = objs[0]
    _bed_finish()
    shown = _exploded(objs) if len(objs) > 1 else []
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        if shown:
            extra["exploded"] = (shown, 35, 28)
        for o in objs[1:]:
            extra["part_" + o.name.replace("StreambedSection", "").lower()] = ([o], *PARTS_SHOT)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            sheet = M.views(NUM, [h], extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet}
        if close:
            d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
            off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
            out["junc_cu"] = render_close([h], f"{d}/junc_cu.png", JUNC_CU[0], JUNC_CU[1], off @ Vector(JUNC_CU[2]),
                                          JUNC_CU[3])
            out["sect_cu"] = render_close([h], f"{d}/sect_cu.png", SECT_CU[0], SECT_CU[1], off @ Vector(SECT_CU[2]),
                                          SECT_CU[3])
            out["under_cu"] = render_close([h], f"{d}/under_cu.png", 20, -40, off @ Vector((0.0, 0.0, 0.5)), 14.0)
        return out
    finally:
        for o in shown:
            bpy.data.objects.remove(o, do_unlink=True)
        M.display(NUM, objs, TITLE)


def preview(names=("f34_sheet", "front_sheet", "side_sheet", "top_sheet"), vfx=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    _bed_finish()
    kit = K.NS["KIT"]
    orig, kit["render_group"] = _long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig


def hero_only():
    """Rebuild just the hero (tuning loop): returns its report."""
    M.coll(NUM, TITLE)
    palette()
    HOLES.clear()
    holes()
    h, lg = _make_hero()
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, *_ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals")}, "log": lg,
            "self_hits": m016._self_hits(h)[0], "thin": m012._thin(h, POLISH_LIM)["under"],
            "shells": shells_report(h)}
