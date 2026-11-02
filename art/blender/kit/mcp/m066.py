"""066 Canvas Shelter (references/066.png): an open walk-under camp shelter. Four chunky chamfered square timber posts
on faceted pale stone bases (the right pair 12.0 tall, the left pair 10.4), a square ridge pole lashed level along the
inner faces of the two tall posts, short crossbars on the outer faces of FL, BL and FR, and one cream canvas sheet (a
closed 0.10 slab on a 7 x 5 grid, sagging 2.3 at the centre, X creases from the triangulation) tied by its four corners:
L-shaped canvas tabs wrap the inner corners of FL, BL and FR under the corner lashings, and at BR the apex tab folds
over the ridge pole. Fat twisted gold rope: an X-lashing at every junction (loops round the post above and below the
timber it binds, two diagonals crossing over that timber), tails, foot collars, peg bands and peg ropes. Square pegs
lean on the stone bases. A red swallowtail banner with a white diamond emblem (both faces) hangs from an iron rod
under the FR crossbar; one hexagonal lantern with Neon glass hangs from that crossbar's inner end. Under the canopy:
a plank table with two Neon candle jars, a bottle, a paper and a pot; a long bench, a short bench and a stool; round
the edges two open straw-filled crates, an open hooped barrel and two pale stones.

    import importlib, kit_models, m066; importlib.reload(kit_models); importlib.reload(m066); m066.build()

Build frame: studs, front -Y (banner and lantern at the front-right post), +X right (the tall side with the ridge
pole), ground z 0, the post rectangle centred on x 0, y 0. Every object ends with its origin at its bbox bottom centre;
o["m066_offset"] is that origin in the build frame. Names (spec 8, decision 14):
- CanvasShelter (hero): everything above, one object of closed shells (no booleans). Collision precise.
- Parts: CanvasShelterPost, ...RidgePole, ...Canopy, ...Banner, ...Lantern, ...Table, ...Bench, ...Stool, ...Crate,
  ...Barrel, ...Peg.
Colour (stage 4) is painted by role and by position inside the builders, never by facing. Stages 5-6: the lantern
glass and the candle jars are m066_glow at emission 1.0 (Neon); one heat_glow socket at the lantern. See M066_spec.md.
Geometry helpers are copied from m048 / m051 / m047 / m012 / m033 / m064 (not imported) so this builder stands alone.
"""
import json
import math
import random
import time

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M

NUM, TITLE, SHEET = 66, "Canvas Shelter", "M066"
OFF = "m066_offset"
PFX = "_m066_"
HERO = "CanvasShelter"
POST_P, RIDGE_P, CANOPY_P = "CanvasShelterPost", "CanvasShelterRidgePole", "CanvasShelterCanopy"
BANNER_P, LANTERN_P, TABLE_P = "CanvasShelterBanner", "CanvasShelterLantern", "CanvasShelterTable"
BENCH_P, STOOL_P, CRATE_P = "CanvasShelterBench", "CanvasShelterStool", "CanvasShelterCrate"
BARREL_P, PEG_P = "CanvasShelterBarrel", "CanvasShelterPeg"

TIMBER, PLANK, WOOD_DARK, END_GRAIN = "m066_timber", "m066_plank", "m066_wood_dark", "m066_end_grain"
CANVAS, CANVAS_DEEP = "m066_canvas", "m066_canvas_deep"
ROPE, ROPE_DEEP = "m066_rope", "m066_rope_deep"
STRAW, STRAW_DEEP = "m066_straw", "m066_straw_deep"
STONE, STONE_DEEP = "m066_stone", "m066_stone_deep"
BANNER, BANNER_WHITE = "m066_banner", "m066_banner_white"
METAL, IRON, GLOW, PALE, BOTTLE = "m066_metal", "m066_iron", "m066_glow", "m066_pale", "m066_bottle"
NEON = 1.0

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
BURY = 0.05

# key -> (hex, roughness, metal, emission, low specular). Stage 4 (spec "Stage 4"): sampled on the sheet, run through
# K.calibrate on the studio dome, then checked on the hero and part renders against the same regions of the sheet.
PALETTE = {
    TIMBER: ("#9A4C17", 0.85, 0.0, 0.0, True),
    PLANK: ("#9C582B", 0.85, 0.0, 0.0, True),
    WOOD_DARK: ("#6E3A20", 0.9, 0.0, 0.0, True),
    END_GRAIN: ("#C9B08E", 0.9, 0.0, 0.0, True),
    CANVAS: ("#FDE8C0", 0.95, 0.0, 0.0, True),
    CANVAS_DEEP: ("#E6C49C", 0.95, 0.0, 0.0, True),
    ROPE: ("#C99E50", 0.95, 0.0, 0.0, True),
    ROPE_DEEP: ("#A6732E", 0.95, 0.0, 0.0, True),
    STRAW: ("#F5D398", 0.95, 0.0, 0.0, True),
    STRAW_DEEP: ("#E5BE7C", 0.95, 0.0, 0.0, True),
    STONE: ("#A09594", 0.92, 0.0, 0.0, True),
    STONE_DEEP: ("#807674", 0.92, 0.0, 0.0, True),
    BANNER: ("#C01417", 0.9, 0.0, 0.0, True),
    BANNER_WHITE: ("#F2EAE6", 0.9, 0.0, 0.0, True),
    METAL: ("#4E3F3A", 0.55, 0.4, 0.0, False),
    IRON: ("#7F7F88", 0.5, 0.5, 0.0, False),
    GLOW: ("#E8AA0A", 0.5, 0.0, NEON, False),
    PALE: ("#C9C1B8", 0.6, 0.0, 0.0, True),
    BOTTLE: ("#5D6930", 0.4, 0.0, 0.0, False),
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions) and K.sample kinds ("all" = paper filtered)
TARGETS = {TIMBER: ((0xA8, 0x4D, 0x16), "brown"), PLANK: ((0xA8, 0x5A, 0x26), "brown"),
           WOOD_DARK: ((0x7C, 0x3E, 0x20), "brown"), END_GRAIN: ((0xD8, 0xBC, 0x98), "all"),
           CANVAS: ((0xFE, 0xED, 0xC2), "all"), CANVAS_DEEP: ((0xE6, 0xC4, 0x9C), "all"),
           ROPE: ((0xDD, 0xA0, 0x48), "brown"), ROPE_DEEP: ((0xBC, 0x7A, 0x2C), "brown"),
           STRAW: ((0xF7, 0xD5, 0x98), "all"), STRAW_DEEP: ((0xEA, 0xC2, 0x7F), "all"),
           STONE: ((0xAE, 0x9C, 0x98), "all"), STONE_DEEP: ((0x8C, 0x7E, 0x7C), "all"),
           BANNER: ((0xD5, 0x15, 0x18), "vivid"), BANNER_WHITE: ((0xF8, 0xF0, 0xEC), "all"),
           METAL: ((0x54, 0x42, 0x3A), "all"), IRON: ((0x82, 0x7D, 0x80), "all"),
           GLOW: ((0xF9, 0xB8, 0x06), "vivid"), PALE: ((0xD6, 0xCE, 0xC6), "all"),
           BOTTLE: ((0x72, 0x7D, 0x3A), "all")}


def _glow_mats():
    """Blender preview of the Neon key as Roblox shows Neon: its own colour, unshaded (m009)."""
    for mat in bpy.data.materials:
        if not (mat.name.startswith("FB_m066_glow") and mat.node_tree):
            continue
        if list(mat.get("flintkit_spec", [0, 0, 0]))[2] < NEON:
            continue
        b = mat.node_tree.nodes.get("Principled BSDF")
        for lk in list(b.inputs["Base Color"].links):
            mat.node_tree.links.remove(lk)
        b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        if "Specular IOR Level" in b.inputs:
            b.inputs["Specular IOR Level"].default_value = 0.0


def palette():
    for k, (hexcol, rough, metal, emit, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, metal=metal, emit=emit, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, metal=metal, emit=emit, low_spec=low)
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m066_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k == "m066_" + tail), None)
            if k1 in PALETTE and k2 and pct.isdigit():
                K.fk().KIT_PALETTE.pop(key, None)
                K.mix_key(k1, k2, int(pct) / 100)
    _glow_mats()


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS); "all" kinds are sampled with the studio paper dropped, the Neon
    preview kept on every round. Returns {key: (hex, rendered)}."""
    keys = keys or list(TARGETS)
    set0, sample0 = K.set_colour, K.sample

    def set_colour(key, hexcol, **kw):
        set0(key, hexcol, **kw)
        _glow_mats()

    def sample(src, box, kind="green"):
        return M.sample(src, box, "all", paper=(242, 238, 230), tol=14) if kind == "all" else sample0(src, box, kind)
    K.set_colour, K.sample = set_colour, sample
    try:
        for k in keys:
            K.fk().material(k)
        _glow_mats()
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        K.set_colour, K.sample = set0, sample0
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


# ---- small helpers -----------------------------------------------------------------------------------------------------
def _mix(k1, k2, t, step=0.05):
    t = round(round(max(0.0, min(1.0, t)) / step) * step, 2)
    return K.mix_key(k1, k2, t)


def _paint(a, faces, key):
    mi = a._mi(key)
    for f in faces:
        if f.is_valid:
            f.material_index = mi


def _tint(a, faces, k):
    for f in faces:
        for lp in f.loops:
            t = lp[a.tint_layer][0] * k
            lp[a.tint_layer] = (t, t, t, 1.0)


def _seed(name):
    return sum((i + 1) * ord(c) for i, c in enumerate(name))


def _rt(name, amp):
    return 1.0 + random.Random(_seed(name)).uniform(-amp, amp)


def _texture(a, vs, amp, seed, scale=0.3):
    K.texture(a, vs, amp=amp, scale=scale, jitter=0.0, seed=seed)


def _solid(a, pts, faces, key, tint=1.0):
    """(m048) One closed shell from points and faces all wound one way; flipped as a whole if the signed volume comes
    out negative. Returns (verts, faces)."""
    bm = a.bm
    vs = [bm.verts.new(Vector(p)) for p in pts]
    fs = [bm.faces.new([vs[i] for i in f]) for f in faces]
    for f in fs:
        f.normal_update()
    vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs)
    if vol < 0:
        for f in fs:
            f.normal_flip()
            f.normal_update()
    a._finish(vs, key, tint=tint)
    return vs, fs


def _shell(a, pts, faces, key, tint=1.0):
    """(m051 _solid_rc) One closed shell from points and faces of any winding: bmesh makes the winding consistent,
    then the shell is flipped as a whole if its signed volume is negative. Returns (verts, faces)."""
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
    """(m051) A convex faceted hull of points. Returns (verts, faces, planes) with planes [(n, d)] (n.p <= d inside)."""
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
    return max(n.dot(p) - d for n, d in planes)


HEXA = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (0, 4, 7, 3), (1, 2, 6, 5)]


def _box_pts(lo, hi, m=None):
    pts = [Vector((x, y, z)) for z in (lo[2], hi[2]) for (x, y) in ((lo[0], lo[1]), (hi[0], lo[1]),
                                                                   (hi[0], hi[1]), (lo[0], hi[1]))]
    return [m @ p for p in pts] if m is not None else pts


def _box(a, lo, hi, key, tint=1.0, m=None):
    """Axis box lo..hi (optionally transformed by the 4x4 matrix m). Returns (verts, faces)."""
    return _shell(a, _box_pts(lo, hi, m), HEXA, key, tint)


def _prism(a, rings, key, tint=1.0, caps=(True, True)):
    """A closed prism / loft through rings of n points each (all rings the same count). Returns (verts, faces,
    band index lists): bands[i] are the faces between ring i and i + 1."""
    n = len(rings[0])
    pts = [p for r in rings for p in r]
    faces, bands = [], []
    for i in range(len(rings) - 1):
        bands.append(list(range(len(faces), len(faces) + n)))
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, (i + 1) * n + j1, (i + 1) * n + j])
    if caps[0]:
        faces.append(list(reversed(range(n))))
    if caps[1]:
        faces.append([(len(rings) - 1) * n + j for j in range(n)])
    vs, fs = _shell(a, pts, faces, key, tint)
    return vs, fs, [[fs[k] for k in b] for b in bands]


def _ngon(c, e1, e2, r, n, rot=0.0):
    return [c + (e1 * math.cos(rot + 2 * math.pi * k / n) + e2 * math.sin(rot + 2 * math.pi * k / n)) * r
            for k in range(n)]


def _cyl(a, c, axis, r, h, n, key, tint=1.0, rot=0.0, r_top=None):
    """An n-sided closed prism from c along the unit axis, length h. Returns (verts, faces)."""
    ax = Vector(axis).normalized()
    e1 = ax.orthogonal().normalized()
    e2 = ax.cross(e1)
    c = Vector(c)
    rings = [_ngon(c, e1, e2, r, n, rot), _ngon(c + ax * h, e1, e2, r if r_top is None else r_top, n, rot)]
    vs, fs, _ = _prism(a, rings, key, tint)
    return vs, fs


def _tube(a, path, r, sides, closed, key, groove=None, tint=1.0, up=(0, 0, 1), phase=0.0, twist=False):
    """(m048) A low-poly rope tube along `path`: rings of `sides` verts. twist=True: each ring turned half a side and
    joined as an antiprism strip (strand = side); twist=False: rings aligned, quads split along the diagonal that
    climbs one side per ring (strand = (side - ring) mod sides). Bends are mitred so the tube keeps its thickness. Open
    tubes get flat end caps. `groove` = {strand: key}: those strands (by their place in the twist, never by facing)
    take that key. Closed twisted paths need an even number of points."""
    P = [Vector(p) for p in path]
    N = len(P)
    if closed and twist and N % 2:
        raise ValueError("closed rope path needs an even point count")
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
        for k in range(sides):
            ang = phase + 2 * math.pi * (k + (0.5 * i if twist else 0.0)) / sides
            off = (U * math.cos(ang) + V * math.sin(ang)) * r
            if bend:
                off += B * off.dot(B) * sc
            ring.append(P[i] + off)
        rings.append(ring)
    pts = [p for rg in rings for p in rg]
    faces, strand = [], []
    segs = N if closed else N - 1
    for i in range(segs):
        j = (i + 1) % N
        shift = (N // 2) % sides if (twist and closed and j == 0) else 0
        for k in range(sides):
            a0, a1 = i * sides + k, i * sides + (k + 1) % sides
            b0, b1 = j * sides + (k + shift) % sides, j * sides + (k + 1 + shift) % sides
            if twist:
                faces += [[a0, a1, b0], [a1, b1, b0]]
                strand += [k, k]
            else:
                faces += [[a0, a1, b1], [a0, b1, b0]]
                strand += [(k - i) % sides] * 2
    if not closed:
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


_PDIRS = (Vector((1.0, 0.0131, 0.0217)).normalized(), Vector((-0.0173, 1.0, 0.0119)).normalized(),
          Vector((0.0151, -0.0191, 1.0)).normalized())


def _parity_in(tree, p):
    """(m047) Ray parity: p is inside the closed shell if at least two of three skewed rays cross it an odd number of
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


def _newell(pts):
    n = Vector()
    m = len(pts)
    for i in range(m):
        p, q = pts[i], pts[(i + 1) % m]
        n += Vector(((p.y - q.y) * (p.z + q.z), (p.z - q.z) * (p.x + q.x), (p.x - q.x) * (p.y + q.y)))
    return n


def _up_for(path):
    n = _newell(path)
    span = max((p - path[0]).length for p in path)
    if n.length > 1e-3 * max(span, 0.1) ** 2:
        return n.normalized()
    ch = path[-1] - path[0]
    u = ch.cross(Vector((0, 0, 1)))
    if u.length < 1e-4:
        u = ch.cross(Vector((1, 0, 0)))
    return u.normalized()


def _hull2(pts):
    pts = sorted(set((round(x, 7), round(y, 7)) for x, y in pts))

    def cross(o, p, q):
        return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def _mitre(H, d):
    """(m064) The mitred offset polygon of a counter-clockwise convex polygon: every edge exactly d outside."""
    n = len(H)
    out = []
    for i in range(n):
        p0, p1, p2 = H[i - 1], H[i], H[(i + 1) % n]
        e_a = Vector((p1[0] - p0[0], p1[1] - p0[1])).normalized()
        e_b = Vector((p2[0] - p1[0], p2[1] - p1[1])).normalized()
        n_a = Vector((e_a.y, -e_a.x))
        n_b = Vector((e_b.y, -e_b.x))
        bis = (n_a + n_b).normalized()
        out.append(Vector(p1) + bis * (d / max(bis.dot(n_a), 0.2)))
    return out


def hull_loop(pts3, c, m, ref, offset, n):
    """(m064) A rope loop round the convex hull of section points in the plane (c, m): the hull's mitred offset at
    `offset`, its corners kept (nearly straight corners merged), the longest edges split until there are n points."""
    m = m.normalized()
    e1 = (ref - m * ref.dot(m)).normalized()
    e2 = m.cross(e1)
    P = [((p - c).dot(e1), (p - c).dot(e2)) for p in pts3]
    H = _hull2(P)
    Hm = []
    for p in H:
        if not Hm or math.hypot(p[0] - Hm[-1][0], p[1] - Hm[-1][1]) > 0.06:
            Hm.append(p)
    if len(Hm) > 2 and math.hypot(Hm[0][0] - Hm[-1][0], Hm[0][1] - Hm[-1][1]) <= 0.06:
        Hm.pop()
    O = _mitre(Hm, offset)
    while len(O) > n:
        k = min(range(len(O)), key=lambda i: abs((O[i] - O[i - 1]).to_3d().cross((O[(i + 1) % len(O)] - O[i]).to_3d()).z))
        del O[k]
    while len(O) < n:
        k = max(range(len(O)), key=lambda i: (O[(i + 1) % len(O)] - O[i]).length)
        O.insert(k + 1, (O[k] + O[(k + 1) % len(O)]) / 2)
    return [c + e1 * p.x + e2 * p.y for p in O]


# ---- piece register --------------------------------------------------------------------------------------------------
PIECES = []          # (kind, name, centroid in the build frame) per shell, in build order
ROPES = []           # open rope runs: name, end points, radius (both-ends contact check)
GEO = {}             # measured placements (report)
FX = []              # (kind, build-frame point, overrides) for the hero's sockets


def _reg(kind, name, vs):
    PIECES.append((kind, name, sum((v.co for v in vs), Vector()) / len(vs)))


# ---- rope (twisted tubes, spec 2.7) ------------------------------------------------------------------------------------
RT_L, RT_C, RT_T, RT_PB, RT_PR, RT_RB = 0.12, 0.11, 0.10, 0.07, 0.08, 0.06    # lashing, collar, tail, peg band ...
SINK = 0.02                                                                   # rope sunk into what it hugs


def _groove(sides):
    """Strand roles by index round the twist (never by facing): one strand in four rope_deep; on 3-ply rope one
    strand half way to rope_deep."""
    return {0: ROPE_DEEP} if sides >= 4 else {0: _mix(ROPE, ROPE_DEEP, 0.5)}


def rope(a, path, rt, sides, closed, name, up=None, kind="rope", twist=True):
    """A rope piece. twist=True: an antiprism twisted tube (diagonals, tails, ropes). twist=False: a round 6-sided
    tube with spiral strands (the turns round square timber: a twisted 4-sided tube on a four-point loop read as a
    flat plate in the close-ups); one strand in six rope_deep and the opposite one half way."""
    path = [Vector(p) for p in path]
    up = up if up is not None else _up_for(path)
    groove = _groove(sides) if twist else {0: ROPE_DEEP, sides // 2: _mix(ROPE, ROPE_DEEP, 0.5)}
    vs, fs = _tube(a, path, rt, sides, closed, ROPE, groove=groove, tint=_rt(name, 0.03), up=tuple(up),
                   twist=twist, phase=0.0 if twist else math.pi / sides)
    _reg(kind, name, vs)
    if not closed:
        ROPES.append({"name": name, "ends": [list(path[0]), list(path[-1])], "rt": rt})
    return vs


def rect_loop(lo, hi, z, off):
    """Four points round the axis rectangle lo..hi (x, y) at height z, every side `off` outside (a mitred square)."""
    return [Vector((lo[0] - off, lo[1] - off, z)), Vector((hi[0] + off, lo[1] - off, z)),
            Vector((hi[0] + off, hi[1] + off, z)), Vector((lo[0] - off, hi[1] + off, z))]


# ---- posts, stone bases (spec 2.2) ------------------------------------------------------------------------------------
POSTS = {"FL": (-6.4, -4.6, 10.4), "BL": (-6.4, 4.6, 10.4), "FR": (6.4, -4.6, 12.0), "BR": (6.4, 4.6, 12.0)}
PH, PCH = 0.5, 0.08                 # post half width, chamfer
BASE_TOP, BASE_H, BASE_TOPH = 1.20, 0.80, 0.72    # base top z, base half width, flat top half width
FOOT_RINGS = (1.75, 2.30)           # weathered feet bands (by height)
BASE_SEED = {"FL": 6601, "BL": 6602, "FR": 6603, "BR": 6604}


def _oct(h, ch):
    return [(h - ch, -h), (h, -h + ch), (h, h - ch), (h - ch, h), (-h + ch, h), (-h, h - ch), (-h, -h + ch),
            (-h + ch, -h)]


def _inner(tag):
    """Unit signs toward the shelter's inside from a post: (sx, sy)."""
    px, py, _ = POSTS[tag]
    return (-1.0 if px > 0 else 1.0), (-1.0 if py > 0 else 1.0)


def post(a, tag, at=None, top=None):
    """One chamfered square post (spec 1.4): an 8-sided prism standing on its base's flat top, two horizontal rings
    near the foot (weathered feet blend by height), a flat square-cut top. 60 tris."""
    px, py, ztop = POSTS[tag]
    if at is not None:
        px, py = at
    ztop = top or ztop
    rings = [[Vector((px + x, py + y, z)) for x, y in _oct(PH, PCH)] for z in (BASE_TOP,) + FOOT_RINGS + (ztop,)]
    nm = f"post_{tag}"
    vs, fs, bands = _prism(a, rings, TIMBER, _rt(nm, 0.04))
    _paint(a, bands[0], _mix(TIMBER, WOOD_DARK, 0.5))
    _paint(a, bands[1], _mix(TIMBER, WOOD_DARK, 0.25))
    _texture(a, vs, 0.03, _seed(nm), scale=0.45)
    _reg("post", nm, vs)
    return vs


def stone_base(a, tag, at=None):
    """The faceted stone base (spec 1.4, close-up 2): a convex hull of a jittered bottom square, a ring of eight
    points at 0.82-0.95 with broken corners and a flat level top (an octagon, half width 0.72) under the post. The
    lowest band blended toward stone_deep by height. Returns its hull planes."""
    px, py, _ = POSTS[tag]
    if at is not None:
        px, py = at
    rng = random.Random(BASE_SEED[tag])
    h = BASE_H
    pts = []
    for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        pts.append(Vector((px + sx * h * rng.uniform(0.96, 1.0), py + sy * h * rng.uniform(0.96, 1.0), 0.0)))
        z = rng.uniform(0.82, 0.95)
        cut = rng.uniform(0.16, 0.30)
        pts.append(Vector((px + sx * h * rng.uniform(0.97, 1.0), py + sy * (h - cut), z + rng.uniform(-0.04, 0.04))))
        pts.append(Vector((px + sx * (h - cut), py + sy * h * rng.uniform(0.97, 1.0), z + rng.uniform(-0.04, 0.04))))
        t = BASE_TOPH
        pts.append(Vector((px + sx * t, py + sy * (t - 0.10), BASE_TOP)))
        pts.append(Vector((px + sx * (t - 0.10), py + sy * t, BASE_TOP)))
    nm = f"base_{tag}"
    vs, fs, planes = _hull(a, pts, STONE, _rt(nm, 0.03))
    for f in fs:
        if f.is_valid:
            zc = f.calc_center_median().z
            if zc < 0.35:
                f.material_index = a._mi(_mix(STONE, STONE_DEEP, 0.5))
            elif zc < 0.60:
                f.material_index = a._mi(_mix(STONE, STONE_DEEP, 0.25))
    _texture(a, vs, 0.05, _seed(nm), scale=1.2)
    _reg("base", nm, vs)
    return planes


def collar(a, tag, at=None):
    """Two chunky turns round the post foot on the base top (spec 2.7)."""
    px, py, _ = POSTS[tag]
    if at is not None:
        px, py = at
    out = []
    for i, z in enumerate((BASE_TOP + RT_C - 0.01, BASE_TOP + 3 * RT_C - 0.03)):
        path = rect_loop((px - PH, py - PH), (px + PH, py + PH), z, RT_C - SINK)
        rope(a, path, RT_C, 5, True, f"collar_{tag}_{i}", up=Vector((0, 0, 1)), twist=False)
        out.append(path)
    return out


# ---- ridge pole and crossbars (spec 2.3) -------------------------------------------------------------------------------
RIDGE_X, RIDGE_Z0, RIDGE_Z1, RIDGE_Y = 5.50, 10.40, 11.20, 5.90
RIDGE_H, RIDGE_CH = 0.40, 0.06
CROSSBARS = {"FL": ((-7.20, -5.60, 8.45), (-4.60, -5.10, 8.95)),
             "BL": ((-7.20, 5.10, 8.45), (-4.60, 5.60, 8.95)),
             "FR": ((4.60, -5.60, 9.60), (7.30, -5.10, 10.10))}


def ridge(a, y0=-RIDGE_Y, y1=RIDGE_Y, x=RIDGE_X):
    """The 0.80 square ridge pole with 0.06 chamfers, along Y on the tall posts' inner faces, ends cut square."""
    zc = (RIDGE_Z0 + RIDGE_Z1) / 2
    rings = [[Vector((x + sx, y, zc + sz)) for sx, sz in _oct(RIDGE_H, RIDGE_CH)] for y in (y0, y1)]
    vs, fs, _ = _prism(a, rings, TIMBER, _rt("ridge", 0.04))
    _texture(a, vs, 0.03, 6610, scale=0.45)
    _reg("ridge", "ridge", vs)
    return vs


def crossbar(a, tag):
    lo, hi = CROSSBARS[tag]
    nm = f"crossbar_{tag}"
    vs, _ = _box(a, lo, hi, TIMBER, _rt(nm, 0.05))
    _texture(a, vs, 0.03, _seed(nm), scale=0.6)
    _reg("crossbar", nm, vs)
    return vs


# ---- canvas (spec 2.4) ------------------------------------------------------------------------------------------------
CT = 0.10                   # canvas thickness
TAB_T = 0.06                # tab thickness
TAB_GAP = 0.003             # tabs stand this far off the timber faces (no coplanar faces between shells)
SAG = 1.15                  # edge sag at the middle (centre 2 x SAG)
NU, NV = 7, 5
HEM = 0.35                  # hem strip width (spec 5.3: faces within 0.35 of the sheet's outer edge)
CORNER_Z = {"FL": 9.00, "BL": 9.00, "FR": 9.10, "BR": 10.60}
TAB_DZ = (-0.15, 0.40)      # tab z range round the canvas corner height
BR_TAB_Y = (3.98, 5.10)
BR_TAB_Z0 = 10.45


def corner_xy(tag):
    """The canvas corner (top surface) in plan: 0.004 inside the tab's outer corner (no coincident verts)."""
    px, py, _ = POSTS[tag]
    sx, sy = _inner(tag)
    if tag == "BR":
        return Vector((RIDGE_X - RIDGE_H - TAB_GAP - TAB_T - 0.004, py + sy * (PH + TAB_T), 0.0))
    d = PH + TAB_GAP + TAB_T + 0.004
    return Vector((px + sx * d, py + sy * d, 0.0))


def canvas_corners():
    return {t: corner_xy(t) + Vector((0, 0, CORNER_Z[t])) for t in ("FL", "FR", "BL", "BR")}


def canvas_top(u, v, C=None):
    C = C or canvas_corners()
    p = (C["FL"] * (1 - u) * (1 - v) + C["FR"] * u * (1 - v) + C["BL"] * (1 - u) * v + C["BR"] * u * v)
    p.z -= SAG * (4 * u * (1 - u) + 4 * v * (1 - v))
    return p


def _canvas_tris():
    tris = []
    ci, cj = (NU - 1) / 2, (NV - 1) / 2
    for i in range(NU - 1):
        for j in range(NV - 1):
            a_, b_, c_, d_ = (i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)
            if (i + 0.5 < ci) == (j + 0.5 < cj):
                tris += [(a_, b_, c_), (a_, c_, d_)]
            else:
                tris += [(a_, b_, d_), (b_, c_, d_)]
    return tris


def canvas_sheet(a, corners=None, name="canvas"):
    """The canvas: one closed slab (spec 2.4). A 7 x 5 top grid bilinear between the corner anchors, sagging SAG at
    each edge middle and 2 SAG at the centre; each quad split along the diagonal pointing at the grid centre (the
    sheet's X of creases), set HEM inside the outer edge; a hem strip of quads (split into two tris each) between
    that grid's border and the true edge; the underside CT below along the vertex normals; rim faces round the
    edge. Hem colour by distance from the edge, three steps toward canvas_deep (close-up 3's darker rim strip): rim
    75 %, hem strip 50 %, the inner grid's corner facets 20 %. 216 tris."""
    C = corners or canvas_corners()
    du = HEM / (C["FR"] - C["FL"]).length
    dv = HEM / (C["BL"] - C["FL"]).length
    T = {(i, j): canvas_top(du + (1 - 2 * du) * i / (NU - 1), dv + (1 - 2 * dv) * j / (NV - 1), C)
         for i in range(NU) for j in range(NV)}
    loop = ([(i, 0) for i in range(NU)] + [(NU - 1, j) for j in range(1, NV)] +
            [(i, NV - 1) for i in range(NU - 2, -1, -1)] + [(0, j) for j in range(NV - 2, 0, -1)])
    O = {("o", k): canvas_top(k[0] / (NU - 1), k[1] / (NV - 1), C) for k in loop}
    P = dict(T)
    P.update(O)
    tris = [(t, CANVAS) for t in _canvas_tris()]
    ring = {(i, j) for i in range(NU) for j in range(NV) if i in (0, NU - 1) or j in (0, NV - 1)}
    tris = [(t, _mix(CANVAS, CANVAS_DEEP, 0.20) if sum(1 for k in t if k in ring) == 3 else key) for t, key in tris]
    hem = _mix(CANVAS, CANVAS_DEEP, 0.50)
    for k in range(len(loop)):
        a0, a1 = ("o", loop[k]), ("o", loop[(k + 1) % len(loop)])
        b0, b1 = loop[k], loop[(k + 1) % len(loop)]
        if (P[a0] - P[b1]).length <= (P[a1] - P[b0]).length:
            tris += [((a0, a1, b1), hem), ((a0, b1, b0), hem)]
        else:
            tris += [((a0, a1, b0), hem), ((a1, b1, b0), hem)]
    nrm = {k: Vector() for k in P}
    for t, _ in tris:
        p0, p1, p2 = (P[k] for k in t)
        n = (p1 - p0).cross(p2 - p0)
        if n.z < 0:
            n = -n
        for k in t:
            nrm[k] += n
    keys = list(P)
    idx = {k: i for i, k in enumerate(keys)}
    pts = [P[k] for k in keys] + [P[k] - nrm[k].normalized() * CT for k in keys]
    nb = len(keys)
    faces, fkeys = [], []
    for t, key in tris:
        faces.append([idx[k] for k in t])
        fkeys.append(key)
        faces.append([nb + idx[k] for k in reversed(t)])
        fkeys.append(key)
    for k in range(len(loop)):
        u_, v_ = ("o", loop[k]), ("o", loop[(k + 1) % len(loop)])
        faces.append([idx[u_], idx[v_], nb + idx[v_], nb + idx[u_]])
        fkeys.append(_mix(CANVAS, CANVAS_DEEP, 0.75))
    vs, fs = _shell(a, pts, faces, CANVAS, _rt(name, 0.02))
    for f, k in zip(fs, fkeys):
        if k != CANVAS:
            f.material_index = a._mi(k)
    _texture(a, vs, 0.03, 6620, scale=0.18)
    _reg("canvas", name, vs)
    GEO["canvas_low_top"] = round(min(p.z for p in P.values()), 3)
    GEO["canvas_low_under"] = round(min(p.z for p in pts[nb:]), 3)
    GEO["canvas_centre_top"] = round(T[((NU - 1) // 2, (NV - 1) // 2)].z, 3)
    return vs, T


def nub(a, T):
    """The small rope knot at the middle of the sheet (f34, exploded): a 6-sided nub on the top face."""
    c = T[((NU - 1) // 2, (NV - 1) // 2)] - Vector((0, 0, 0.012))
    vs, _ = _cyl(a, c, (0, 0, 1), 0.16, 0.13, 6, ROPE, _rt("nub", 0.03), r_top=0.11)
    _reg("rope", "nub", vs)


def corner_tab(a, tag, at=None, z=None):
    """An L-shaped canvas tab wrapping the post's two inner faces under the corner lashing (spec 2.1, 2.4): 0.06 thick,
    from 0.15 below the canvas corner to 0.40 above it. 20 tris."""
    px, py, _ = POSTS[tag]
    if at is not None:
        px, py = at
    sx, sy = _inner(tag)
    zc = CORNER_Z[tag] if z is None else z
    xi, yi = px + sx * (PH + TAB_GAP), py + sy * (PH + TAB_GAP)        # the inner faces (TAB_GAP off them)
    xo, yo = xi + sx * TAB_T, yi + sy * TAB_T
    xf, yf = px - sx * (PH - 0.01), py - sy * (PH - 0.01)              # 0.01 short of the far edges
    prof = [(xo, yf), (xo, yo), (xf, yo), (xf, yi), (xi, yi), (xi, yf)]
    z0, z1 = zc + TAB_DZ[0], zc + TAB_DZ[1]
    pts = [Vector((x, y, z0)) for x, y in prof] + [Vector((x, y, z1)) for x, y in prof]
    caps = [(0, 1, 4), (0, 4, 5), (1, 2, 3), (1, 3, 4)]
    faces = [list(t) for t in caps] + [[6 + t[2], 6 + t[1], 6 + t[0]] for t in caps]
    for i in range(6):
        i1 = (i + 1) % 6
        faces.append([i, i1, 6 + i1, 6 + i])
    nm = f"tab_{tag}"
    vs, fs = _shell(a, pts, faces, _mix(CANVAS, CANVAS_DEEP, 0.25), _rt(nm, 0.02))
    _reg("tab", nm, vs)
    return (min(xo, xf), min(yo, yf)), (max(xo, xf), max(yo, yf))


def ridge_tab(a):
    """The BR apex tab (close-up 1: the canvas loops over the ridge pole): a folded 0.06 slab up the ridge's inner face
    from z 10.45 and over its top to the post, along y 3.98-5.10. 20 tris."""
    xi = RIDGE_X - RIDGE_H - TAB_GAP
    xo = xi - TAB_T
    xr = RIDGE_X + RIDGE_H - 0.05
    zt = RIDGE_Z1 + TAB_GAP
    prof = [(xo, BR_TAB_Z0), (xo, zt + TAB_T), (xr, zt + TAB_T), (xr, zt), (xi, zt), (xi, BR_TAB_Z0)]
    pts = [Vector((x, BR_TAB_Y[0], z)) for x, z in prof] + [Vector((x, BR_TAB_Y[1], z)) for x, z in prof]
    caps = [(0, 1, 4), (0, 4, 5), (1, 2, 3), (1, 3, 4)]
    faces = [list(t) for t in caps] + [[6 + t[2], 6 + t[1], 6 + t[0]] for t in caps]
    for i in range(6):
        i1 = (i + 1) % 6
        faces.append([i, i1, 6 + i1, 6 + i])
    vs, fs = _shell(a, pts, faces, _mix(CANVAS, CANVAS_DEEP, 0.25), _rt("tab_BR", 0.02))
    _reg("tab", "tab_BR", vs)


class _Thin:
    """Canvas shells as solids: signed distance (+ outside) by nearest surface and ray parity (m064 _Canvas)."""

    def __init__(self):
        self.items, self.cos, self.polys = [], [], []
        self.tree = None

    def add(self, vs):
        fs = K.faces_of(vs)
        idx = {v: i for i, v in enumerate(vs)}
        cos = [v.co.copy() for v in vs]
        polys = [[idx[v] for v in f.verts] for f in fs]
        lo = Vector((min(c.x for c in cos), min(c.y for c in cos), min(c.z for c in cos)))
        hi = Vector((max(c.x for c in cos), max(c.y for c in cos), max(c.z for c in cos)))
        self.items.append((BVHTree.FromPolygons(cos, polys), lo, hi))
        base = len(self.cos)
        self.cos += cos
        self.polys += [[base + i for i in p] for p in polys]
        self.tree = None

    def build(self):
        self.tree = BVHTree.FromPolygons(self.cos, self.polys)
        return self


# ---- lashings (spec 2.7; close-up 1) ----------------------------------------------------------------------------------
# z of the loops round each post (canvas corner + 0.15 above the corner for the tab loop)
LOOPS = {"FL": {"tab": 9.15, "low": 8.30}, "BL": {"tab": 9.15, "low": 8.30},
         "FR": {"tab": 9.25, "mid": 10.25, "up": 11.40}, "BR": {"low": 10.25, "up": 11.40}}
X_HALF, X_EDGE, X_OFF, X_LIFT = 0.40, 0.15, 0.09, 0.20


def post_loop(a, tag, z, name, box=None, at=None):
    """A horizontal turn round the post (and its canvas tab), every side SINK into the timber it hugs."""
    px, py, _ = POSTS[tag]
    if at is not None:
        px, py = at
    lo, hi = (px - PH, py - PH), (px + PH, py + PH)
    if box is not None:
        lo = (min(lo[0], box[0][0]), min(lo[1], box[0][1]))
        hi = (max(hi[0], box[1][0]), max(hi[1], box[1][1]))
    path = rect_loop(lo, hi, z, RT_L - SINK)
    rope(a, path, RT_L, 5, True, name, up=Vector((0, 0, 1)), twist=False)
    return {"lo": lo, "hi": hi, "z": z, "path": path}


def x_diagonals(a, tag, upper, lower, n, ax, face, top, bot, centre, name, off=X_OFF):
    """The X of a lashing (close-up 1): two open ropes from the upper turn down across the bound timber's outer face
    to the lower turn, crossing at the middle; the second lifted X_LIFT over the first. n = the face's outward unit
    normal (horizontal), ax = the timber's axis (horizontal), face = n . p on the timber's outer face, top / bot = its
    top and bottom z, centre = the post centre (x, y), off = the rope centre's distance off the face (RT_L - off is
    how far it sinks into the timber)."""
    n, ax = Vector(n), Vector(ax)
    c = Vector((centre[0], centre[1], 0.0))
    side = n * (PH + RT_L - SINK)          # the turns' centreline on the post face toward the timber

    def on_face(s, z, extra=0.0):
        p = c + ax * s
        p = p + n * (face - p.dot(n) + off + extra)
        p.z = z
        return p
    out = []
    for k, sg in enumerate((1, -1)):
        S = c + side + ax * (-sg * X_HALF)
        S.z = upper
        E = c + side + ax * (sg * X_HALF)
        E.z = lower
        B1 = on_face(-sg * X_EDGE, top + off)
        B2 = on_face(sg * X_EDGE, bot - off)
        S0 = S + (B1 - S).normalized() * (RT_L - 0.03)
        E0 = E + (B2 - E).normalized() * (RT_L - 0.03)
        path = [S0, B1, B2, E0]
        if k == 1:
            path = [S0, B1, on_face(0.0, (top + bot) / 2, X_LIFT), B2, E0]
        rope(a, path, RT_L, 4, False, f"{name}_x{k}", up=n)
        out.append(path)
    return out


def lashing_crossbar(a, tag):
    """FL / BL: the tab turn above the crossbar (round the post and its canvas tab), a turn below it, and the X over
    the crossbar's outer face. FR: the same with the tab turn below the crossbar and the shared middle turn above."""
    px, py, _ = POSTS[tag]
    sx, sy = _inner(tag)
    lo, hi = CROSSBARS[tag]
    n = Vector((0.0, -sy, 0.0))             # the crossbar sits on the post's outer Y face
    face = n.y * (hi[1] if n.y > 0 else lo[1])
    L = LOOPS[tag]
    box = corner_tab(a, tag)
    if tag == "FR":
        t = post_loop(a, tag, L["tab"], f"lash_{tag}_tab", box)
        m = post_loop(a, tag, L["mid"], f"lash_{tag}_mid")
        x_diagonals(a, tag, L["mid"], L["tab"], n, (1, 0, 0), face, hi[2], lo[2], (px, py), f"lash_{tag}")
        return t, m
    t = post_loop(a, tag, L["tab"], f"lash_{tag}_tab", box)
    lw = post_loop(a, tag, L["low"], f"lash_{tag}_low")
    x_diagonals(a, tag, L["tab"], L["low"], n, (1, 0, 0), face, hi[2], lo[2], (px, py), f"lash_{tag}")
    return t, lw


def lashing_ridge(a, tag):
    """FR upper / BR: turns round the post above and below the ridge pole, and the X over the ridge's inner face (at
    BR over the apex tab folded onto it)."""
    px, py, _ = POSTS[tag]
    L = LOOPS[tag]
    out = {}
    if tag == "BR":
        out["low"] = post_loop(a, tag, L["low"], f"lash_{tag}_low")
    out["up"] = post_loop(a, tag, L["up"], f"lash_{tag}_up")
    n = Vector((-1.0, 0.0, 0.0))
    xin = RIDGE_X - RIDGE_H - (TAB_T + TAB_GAP if tag == "BR" else 0.0)
    top = RIDGE_Z1 + (TAB_T + TAB_GAP if tag == "BR" else 0.0)
    lower = L["low"] if tag == "BR" else L["mid"]
    x_diagonals(a, tag, L["up"], lower, n, (0, 1, 0), -xin, top, RIDGE_Z0, (px, py), f"lash_{tag}_r",
                off=RT_L + 0.005 if tag == "BR" else X_OFF)     # over the thin apex tab: resting on it, not sunk
    return out


def tail(a, tag):
    """A dangling tail from the lower turn of L1 / L2 down the post's outer (-X) face (f34 L, r34)."""
    px, py, _ = POSTS[tag]
    sx, sy = _inner(tag)
    z = LOOPS[tag]["low"]
    xo = px - sx * (PH + RT_T - SINK)
    y = py - sy * 0.20
    path = [Vector((px - sx * (PH + RT_L - SINK), y, z - (RT_L - 0.04))), Vector((xo, y - sy * 0.04, z - 0.50)),
            Vector((xo, y - sy * 0.10, z - 0.95))]
    rope(a, path, RT_T, 4, False, f"tail_{tag}", up=Vector((-sx, 0, 0)))


# ---- pegs (spec 2.8) ----------------------------------------------------------------------------------------------------
PEG_HW, PEG_L, PEG_TILT, PEG_BAND = 0.18, 1.25, math.radians(35), 0.25


def peg_geometry(px, py, s, planes=None):
    """The stake's axis frame leaning toward the base's outer X face (s = +1 for the right posts): its top inner edge
    0.005 off the base hull (found by bisection on the hull planes), its foot cut level on the ground."""
    d = Vector((-s * math.sin(PEG_TILT), 0.0, math.cos(PEG_TILT)))
    e1 = Vector((s * math.cos(PEG_TILT), 0.0, math.sin(PEG_TILT)))        # out and up (away from the base)
    e2 = Vector((0.0, 1.0, 0.0))

    def frame(xf):
        F = Vector((xf, py, PEG_HW * math.sin(PEG_TILT)))
        return F, F + d * PEG_L
    if planes is None:
        xf = px + s * (BASE_H + 0.86)
    else:
        lo_, hi_ = px + s * BASE_H, px + s * (BASE_H + 2.0)
        for _ in range(40):
            mid = (lo_ + hi_) / 2
            F, T = frame(mid)
            corners = [T - e1 * PEG_HW + e2 * w for w in (-PEG_HW, PEG_HW)]
            gap = min(_sd(planes, p) for p in corners)
            if gap > 0.005:
                hi_ = mid
            else:
                lo_ = mid
        xf = hi_
    F, T = frame(xf)
    return {"F": F, "T": T, "d": d, "e1": e1, "e2": e2, "s": s}


def peg(a, G, tag):
    """A square 0.36 stake (close-up 2), leaning 35 deg on the base, its foot cut level on the ground, a pale end-grain
    top, a rope band 0.25 below the top. Returns the band path."""
    F, d, e1, e2 = G["F"], G["d"], G["e1"], G["e2"]
    cs = [e1 * u + e2 * w for u, w in ((-PEG_HW, -PEG_HW), (PEG_HW, -PEG_HW), (PEG_HW, PEG_HW), (-PEG_HW, PEG_HW))]
    bot = []
    for c in cs:
        q = F + c
        t0 = -q.z / d.z
        bot.append(q + d * t0)
    top = [G["T"] + c for c in cs]
    vs, fs = _shell(a, bot + top, HEXA, _mix(TIMBER, WOOD_DARK, 0.35), _rt(tag, 0.05))
    for f in fs:
        if all(v.co.z > G["T"].z - PEG_HW - 1e-4 and (v.co - G["T"]).dot(d) > -1e-4 for v in f.verts):
            f.material_index = a._mi(END_GRAIN)
    _texture(a, vs, 0.03, _seed(tag), scale=1.0)
    _reg("peg", f"{tag}_stake", vs)
    c = G["T"] - d * PEG_BAND
    sq = [c + e1 * u + e2 * w for u, w in ((-PEG_HW, -PEG_HW), (PEG_HW, -PEG_HW), (PEG_HW, PEG_HW), (-PEG_HW, PEG_HW))]
    path = hull_loop(sq, c, d, e1, RT_PB - SINK, 4)
    rope(a, path, RT_PB, 4, True, f"{tag}_band", up=d, twist=False)
    return path


def peg_rope(a, tag, band, collar_path, planes):
    """From the peg band up over the base's top outer edge to the lower collar turn (close-up 2); ends sunk 0.03 into
    the band and the collar; the middle point lifted until the rope clears the base hull."""
    def along(path):
        n = len(path)
        return [path[i].lerp(path[(i + 1) % n], t / 12) for i in range(n) for t in range(12)]
    bc = sum(band, Vector()) / len(band)
    cpt = min(along(collar_path), key=lambda p: (p - bc).length)
    bpt = min(along(band), key=lambda p: (p - cpt).length)
    s0 = bpt + (cpt - bpt).normalized() * (RT_PB - 0.03)
    e0 = cpt + (bpt - cpt).normalized() * (RT_C - 0.03)
    mid = s0.lerp(e0, 0.5)
    for _ in range(40):
        samples = [s0.lerp(mid, t / 6) for t in range(1, 7)] + [mid.lerp(e0, t / 6) for t in range(0, 6)]
        if min(_sd(planes, p) for p in samples) >= RT_PR - 0.02:
            break
        mid = mid + Vector((0, 0, 0.02))
    rope(a, [s0, mid, e0], RT_PR, 4, False, f"pegrope_{tag}")


# ---- banner and rod (spec 2.5) ----------------------------------------------------------------------------------------
ROD_X0, ROD_X1, ROD_Y, ROD_R = 6.98, 9.40, -5.35, 0.09
ROD_Z = CROSSBARS["FR"][0][2] - ROD_R * math.cos(math.pi / 6)        # flat top on the crossbar bottom
KNOB_R, KNOB_L = 0.15, 0.22
SLEEVE_X0, SLEEVE_X1, SLEEVE_R, SLEEVE_RI = 7.40, 9.30, 0.16, 0.105
BAN_T, BAN_TIP, BAN_NOTCH = 0.08, 3.30, 0.90
ROD_BAND_X = 7.14


def rod(a, x0=ROD_X0, x1=ROD_X1, y=ROD_Y, z=ROD_Z):
    """The iron banner rod (6-sided, flats top and bottom) with a 6-sided knob on its outer end."""
    e1, e2 = Vector((0, 1, 0)), Vector((0, 0, 1))
    rings = [_ngon(Vector((x, y, z)), e1, e2, ROD_R, 6) for x in (x0, x1)]
    vs, _, _ = _prism(a, rings, IRON, _rt("rod", 0.03))
    _reg("rod", "rod", vs)
    rings = [_ngon(Vector((x, y, z)), e1, e2, KNOB_R, 6, math.pi / 6) for x in (x1, x1 + KNOB_L)]
    vs, _, _ = _prism(a, rings, METAL, _rt("knob", 0.03))
    _reg("rod", "knob", vs)


def sleeve(a, y=ROD_Y, z=ROD_Z):
    """The banner's top hem: a 6-sided annular sleeve round the rod (the hem wraps it, spec 2.5). 48 tris."""
    e1, e2 = Vector((0, 1, 0)), Vector((0, 0, 1))
    o0 = _ngon(Vector((SLEEVE_X0, y, z)), e1, e2, SLEEVE_R, 6)
    o1 = _ngon(Vector((SLEEVE_X1, y, z)), e1, e2, SLEEVE_R, 6)
    i0 = _ngon(Vector((SLEEVE_X0, y, z)), e1, e2, SLEEVE_RI, 6)
    i1 = _ngon(Vector((SLEEVE_X1, y, z)), e1, e2, SLEEVE_RI, 6)
    pts = o0 + o1 + i0 + i1
    faces = []
    for j in range(6):
        j1 = (j + 1) % 6
        faces.append([j, j1, 6 + j1, 6 + j])                  # outer
        faces.append([12 + j1, 12 + j, 18 + j, 18 + j1])      # inner
        faces.append([j1, j, 12 + j, 12 + j1])                # x0 end
        faces.append([6 + j, 6 + j1, 18 + j1, 18 + j])        # x1 end
    vs, _ = _shell(a, pts, faces, _mix(BANNER, METAL, 0.15), _rt("sleeve", 0.02))
    _reg("banner", "sleeve", vs)
    return z - SLEEVE_R * math.cos(math.pi / 6)


def _slab(a, outline, tris, y0, y1, key, name, kind, tint=1.0):
    """A closed slab from a 2D outline (x, z) between the planes y0 and y1, explicit cap triangles."""
    n = len(outline)
    pts = [Vector((x, y0, z)) for x, z in outline] + [Vector((x, y1, z)) for x, z in outline]
    faces = [list(t) for t in tris] + [[n + t[2], n + t[1], n + t[0]] for t in tris]
    for i in range(n):
        i1 = (i + 1) % n
        faces.append([i, i1, n + i1, n + i])
    vs, fs = _shell(a, pts, faces, key, tint)
    _reg(kind, name, vs)
    return vs, fs


def banner(a, top, y=ROD_Y):
    """The red swallowtail banner (2.0 x 5.9 nominal): a 0.08 slab hanging from the sleeve (its top 0.007 into it),
    three tongues 0.9 deep, the emblem on both faces (a white diamond outline, a small inner diamond and two dots,
    0.015 proud). Returns the emblem centre."""
    x0, x1 = SLEEVE_X0, SLEEVE_X1
    w = x1 - x0
    zt = top + 0.007
    zn = BAN_TIP + BAN_NOTCH
    P = [(x0, zt), (x1, zt), (x1, BAN_TIP), (x0 + 2 * w / 3, zn), (x0 + w / 2, BAN_TIP), (x0 + w / 3, zn),
         (x0, BAN_TIP), (x0, zn), (x1, zn)]
    # outline order for the rim: 0 1 8 2 3 4 5 6 7
    order = [0, 1, 8, 2, 3, 4, 5, 6, 7]
    remap = {o: i for i, o in enumerate(order)}
    outline = [P[o] for o in order]
    tri_src = [(7, 5, 0), (5, 3, 0), (3, 1, 0), (3, 8, 1), (6, 5, 7), (5, 4, 3), (3, 2, 8)]
    tris = [tuple(remap[k] for k in t) for t in tri_src]
    vs, fs = _slab(a, outline, tris, y - BAN_T / 2, y + BAN_T / 2, BANNER, "banner", "banner", _rt("banner", 0.02))
    for f in fs:
        if f.calc_center_median().z > zt - 0.45:
            f.material_index = a._mi(_mix(BANNER, METAL, 0.10))       # the hem band under the sleeve, one step deeper
    _texture(a, vs, 0.02, 6630, scale=0.4)
    cx, cz = (x0 + x1) / 2, (zt + zn) / 2 + 0.15
    for side in (-1, 1):
        yf = y + side * BAN_T / 2
        emblem(a, cx, cz, yf, side)
    GEO["banner"] = {"w": round(w, 3), "h": round(zt - BAN_TIP, 3), "top": round(zt, 3), "tip": BAN_TIP}
    return Vector((cx, y, cz))


EMB_W, EMB_H, EMB_S = 1.10, 1.60, 0.15
EMB_IW, EMB_IH, DOT_R, DOT_X = 0.35, 0.50, 0.11, 0.80
EMB_T = 0.015


def emblem(a, cx, cz, yf, side):
    """The white emblem on one banner face: a diamond outline slab (8 points), an inner diamond, two side dots; each
    0.005 into the face and 0.015 proud."""
    y0, y1 = yf - side * 0.005, yf + side * EMB_T
    hw, hh = EMB_W / 2, EMB_H / 2
    k = EMB_S * math.hypot(hw, hh) / hw          # vertical inset that keeps the stroke EMB_S thick
    kx = EMB_S * math.hypot(hw, hh) / hh
    outer = [(cx, cz + hh), (cx + hw, cz), (cx, cz - hh), (cx - hw, cz)]
    inner = [(cx, cz + hh - k), (cx + hw - kx, cz), (cx, cz - hh + k), (cx - hw + kx, cz)]
    pts = [Vector((x, y0, z)) for x, z in outer + inner] + [Vector((x, y1, z)) for x, z in outer + inner]
    faces = []
    for i in range(4):
        i1 = (i + 1) % 4
        faces.append([i, i1, 4 + i1, 4 + i])                    # back face ring
        faces.append([8 + 4 + i, 8 + 4 + i1, 8 + i1, 8 + i])     # front face ring
        faces.append([i1, i, 8 + i, 8 + i1])                     # outer rim
        faces.append([4 + i, 4 + i1, 12 + i1, 12 + i])           # inner rim
    tag = "f" if side < 0 else "b"
    vs, _ = _shell(a, pts, faces, BANNER_WHITE, _rt("emb" + tag, 0.02))
    _reg("emblem", f"emblem_{tag}", vs)
    for nm, (ex, ez, w2, h2) in (("in", (cx, cz, EMB_IW / 2, EMB_IH / 2)), ("dl", (cx - DOT_X, cz, DOT_R, DOT_R)),
                                 ("dr", (cx + DOT_X, cz, DOT_R, DOT_R))):
        d = [(ex, ez + h2), (ex + w2, ez), (ex, ez - h2), (ex - w2, ez)]
        vs, _ = _slab(a, d, [(0, 1, 2), (0, 2, 3)], y0, y1, BANNER_WHITE, f"emblem_{tag}_{nm}", "emblem",
                      _rt(nm + tag, 0.02))


def rod_band(a):
    """A rope band round the rod and the FR crossbar's outer end (spec 2.5)."""
    lo, hi = CROSSBARS["FR"]
    c = Vector((ROD_BAND_X, ROD_Y, (lo[2] + hi[2]) / 2))
    pts = [Vector((ROD_BAND_X, y, z)) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
    pts += _ngon(Vector((ROD_BAND_X, ROD_Y, ROD_Z)), Vector((0, 1, 0)), Vector((0, 0, 1)), ROD_R, 6)
    path = hull_loop(pts, c, Vector((1, 0, 0)), Vector((0, 1, 0)), RT_RB - SINK, 6)
    rope(a, path, RT_RB, 3, True, "rod_band", up=Vector((1, 0, 0)))


# ---- lantern (spec 1.4, VFX panel) ------------------------------------------------------------------------------------
LAN_X = 4.85
L_PLATE, L_GLASS, L_BAND = 0.15, 1.20, 0.12
L_R_PLATE, L_R_GLASS, L_R_BAND = 0.60, 0.50, 0.575
L_ROOF = ((0.575, 0.0), (0.36, 0.25), (0.15, 0.45), (0.15, 0.57))       # (r, dz) rings of the domed roof and cap
RING_R, RING_T = 0.15, 0.06
L_BODY = L_PLATE + L_GLASS + L_BAND + L_ROOF[-1][1]


def lantern(a, base, tag="lantern"):
    """The hexagonal lantern (VFX panel): a flared base plate, a Neon glass core, six triangular corner bars, a band,
    a domed roof with its cap and a ring on top. Returns (glass centre, ring top)."""
    c = Vector(base)
    z0 = c.z
    e1, e2 = Vector((1, 0, 0)), Vector((0, 1, 0))
    up = Vector((0, 0, 1))
    rings = [_ngon(c, e1, e2, L_R_PLATE, 6), _ngon(c + up * L_PLATE, e1, e2, L_R_PLATE - 0.06, 6)]
    vs, _, _ = _prism(a, rings, METAL, _rt(tag + "p", 0.03))
    _reg("lmetal", f"{tag}_plate", vs)
    g0 = c + up * L_PLATE
    rings = [_ngon(g0 - up * 0.005, e1, e2, L_R_GLASS, 6), _ngon(g0 + up * (L_GLASS + 0.005), e1, e2, L_R_GLASS, 6)]
    vs, _, _ = _prism(a, rings, GLOW, 1.0)
    _reg("glass", f"{tag}_glass", vs)
    for k in range(6):
        ang = 2 * math.pi * k / 6
        rad = Vector((math.cos(ang), math.sin(ang), 0))
        tan = Vector((-math.sin(ang), math.cos(ang), 0))
        p0 = c + rad * (L_R_GLASS - 0.02)
        tri = [p0 + rad * 0.10, p0 + tan * 0.055, p0 - tan * 0.055]
        rings = [[p + up * L_PLATE for p in tri], [p + up * (L_PLATE + L_GLASS) for p in tri]]
        vs, _, _ = _prism(a, rings, METAL, 0.95)
        _reg("lmetal", f"{tag}_bar{k}", vs)
    zb = L_PLATE + L_GLASS
    rings = [_ngon(c + up * zb, e1, e2, L_R_BAND, 6), _ngon(c + up * (zb + L_BAND), e1, e2, L_R_BAND, 6)]
    vs, _, _ = _prism(a, rings, METAL, 1.0)
    _reg("lmetal", f"{tag}_band", vs)
    zr = zb + L_BAND - 0.005
    rings = [_ngon(c + up * (zr + dz), e1, e2, r, 6) for r, dz in L_ROOF]
    vs, _, _ = _prism(a, rings, METAL, 1.04)
    _reg("lmetal", f"{tag}_roof", vs)
    top = zr + L_ROOF[-1][1]
    cz = top - 0.01 + RING_R + RING_T
    ring = [c + Vector((0, math.cos(2 * math.pi * k / 6) * RING_R, cz + math.sin(2 * math.pi * k / 6) * RING_R))
            for k in range(6)]
    vs = _tube(a, ring, RING_T, 3, True, METAL, tint=0.9, up=(1, 0, 0), twist=True)[0]
    _reg("lmetal", f"{tag}_ring", vs)
    gc = c + up * (L_PLATE + L_GLASS / 2)
    return gc, c + up * (cz + RING_R + RING_T)


def lantern_drop():
    """The lantern base z so its ring top touches the FR crossbar's bottom (0.01 into it)."""
    zbot = CROSSBARS["FR"][0][2]
    zr = L_PLATE + L_GLASS + L_BAND - 0.005
    ring_top = zr + L_ROOF[-1][1] - 0.01 + 2 * (RING_R + RING_T)
    return zbot + 0.01 - ring_top


# ---- furniture (spec 1.4, 2.9) -----------------------------------------------------------------------------------------
TABLE = {"c": (-0.80, 0.40), "L": 7.20, "top": 2.60}
PL_W, PL_T, PL_GAP = 0.70, 0.25, 0.02
LONG_BENCH = {"c": (-0.80, 2.70), "L": 6.00}
SHORT_BENCH = {"c": (0.20, -1.90), "L": 3.60}
STOOL = {"c": (3.90, 0.40), "rot": 8.0}
SEAT = 1.50


def _R(c, rot_deg=0.0):
    return Matrix.Translation((c[0], c[1], 0)) @ Matrix.Rotation(math.radians(rot_deg), 4, "Z")


def table(a, c=None, rot=0.0):
    """The plank table (7.20 x 2.86 x 2.60): four lengthwise planks with 0.02 gaps, two cleats under them, four square
    legs, two end stretchers and a long stretcher between them. 156 tris."""
    R = _R(c or TABLE["c"], rot)
    L, top = TABLE["L"], TABLE["top"]
    hw = (4 * PL_W + 3 * PL_GAP) / 2
    rng = random.Random(6640)
    for i in range(4):
        y0 = -hw + i * (PL_W + PL_GAP)
        vs, _ = _box(a, (-L / 2, y0, top - PL_T), (L / 2, y0 + PL_W, top), PLANK, 1.0 + rng.uniform(-0.05, 0.05), R)
        _texture(a, vs, 0.03, 6641 + i, scale=0.6)
        _reg("plank", f"table_plank{i}", vs)
    lx = L / 2 - 0.60
    leg_key = _mix(PLANK, TIMBER, 0.35)
    zc0 = top - PL_T - 0.20
    for i, x in enumerate((-lx, lx)):
        vs, _ = _box(a, (x - 0.16, -hw + 0.06, zc0), (x + 0.16, hw - 0.06, top - PL_T), leg_key, _rt(f"cl{i}", 0.04), R)
        _reg("plank", f"table_cleat{i}", vs)
    ly = hw - 0.36
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        x, y = sx * lx, sy * ly
        vs, _ = _box(a, (x - 0.225 + 0.003, y - 0.225, 0.0), (x + 0.225 - 0.003, y + 0.225, zc0), leg_key,
                     _rt(f"tl{i}", 0.04), R)
        _reg("plank", f"table_leg{i}", vs)
    for i, x in enumerate((-lx, lx)):
        vs, _ = _box(a, (x - 0.13, -ly + 0.225, 0.40), (x + 0.13, ly - 0.225, 0.70), leg_key, _rt(f"ts{i}", 0.04), R)
        _reg("plank", f"table_end{i}", vs)
    vs, _ = _box(a, (-lx + 0.13, -0.12, 0.42), (lx - 0.13, 0.12, 0.68), leg_key, _rt("tsl", 0.04), R)
    _reg("plank", "table_long", vs)
    GEO["table"] = {"L": L, "W": round(2 * hw, 3), "top": top}


def bench(a, c, L, tag, rot=0.0):
    """A bench (1.22 deep, seat 1.50): two seat planks 0.60 x 0.22 with a 0.02 gap on four square legs, an end rail
    across each pair of legs. 96 tris."""
    R = _R(c, rot)
    hw = 0.61
    for i, y0 in enumerate((-hw, 0.01)):
        vs, _ = _box(a, (-L / 2, y0, SEAT - 0.22), (L / 2, y0 + 0.60, SEAT), PLANK, _rt(f"{tag}p{i}", 0.05), R)
        _texture(a, vs, 0.03, _seed(tag) + i, scale=0.6)
        _reg("plank", f"{tag}_plank{i}", vs)
    lx, ly = L / 2 - 0.40, 0.33
    leg_key = _mix(PLANK, TIMBER, 0.35)
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        x, y = sx * lx, sy * ly
        vs, _ = _box(a, (x - 0.175, y - 0.175, 0.0), (x + 0.175, y + 0.175, SEAT - 0.22), leg_key,
                     _rt(f"{tag}l{i}", 0.04), R)
        _reg("plank", f"{tag}_leg{i}", vs)
    for i, x in enumerate((-lx, lx)):
        vs, _ = _box(a, (x - 0.11, -ly + 0.175, 0.35), (x + 0.11, ly - 0.175, 0.60), leg_key, _rt(f"{tag}r{i}", 0.04), R)
        _reg("plank", f"{tag}_rail{i}", vs)


def stool(a, c=None, rot=None):
    """The stool (1.22 x 1.20 x 1.50): a two-plank seat on four 0.30 legs. 72 tris."""
    R = _R(c or STOOL["c"], STOOL["rot"] if rot is None else rot)
    for i, y0 in enumerate((-0.61, 0.01)):
        vs, _ = _box(a, (-0.60, y0, SEAT - 0.20), (0.60, y0 + 0.60, SEAT), PLANK, _rt(f"stp{i}", 0.05), R)
        _reg("plank", f"stool_plank{i}", vs)
    leg_key = _mix(PLANK, TIMBER, 0.35)
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        x, y = sx * 0.38, sy * 0.33
        vs, _ = _box(a, (x - 0.15, y - 0.15, 0.0), (x + 0.15, y + 0.15, SEAT - 0.20), leg_key, _rt(f"stl{i}", 0.04), R)
        _reg("plank", f"stool_leg{i}", vs)


ITEMS = {"J1": (0.30, 0.70), "J2": (0.90, 0.50), "bottle": (-2.40, 0.90), "paper": (-0.90, 0.20), "pot": (-3.60, 0.80)}


def items(a, top=None, dx=0.0, dy=0.0):
    """The table items (f34): two Neon candle jars with dark lids, a green bottle, a paper and a pot. Each stands on a
    plank (bottom on the top, 0.002 off)."""
    z = (top or TABLE["top"]) + 0.002
    up = (0, 0, 1)
    for j in ("J1", "J2"):
        x, y = ITEMS[j]
        vs, _ = _cyl(a, (x + dx, y + dy, z), up, 0.225, 0.60, 6, GLOW, 1.0)
        _reg("jar", f"jar_{j}", vs)
        vs, _ = _cyl(a, (x + dx, y + dy, z + 0.60), up, 0.20, 0.08, 6, METAL, 0.95, rot=0.3)
        _reg("lid", f"lid_{j}", vs)
    x, y = ITEMS["bottle"]
    vs, _ = _cyl(a, (x + dx, y + dy, z), up, 0.21, 0.70, 6, BOTTLE, 1.0, r_top=0.17)
    _reg("item", "bottle", vs)
    vs, _ = _cyl(a, (x + dx, y + dy, z + 0.70), up, 0.085, 0.32, 6, BOTTLE, 1.05, rot=0.4)
    _reg("item", "bottle_neck", vs)
    x, y = ITEMS["paper"]
    R = Matrix.Translation((x + dx, y + dy, 0)) @ Matrix.Rotation(math.radians(10), 4, "Z")
    vs, _ = _box(a, (-0.70, -0.50, z), (0.70, 0.50, z + 0.04), _mix(CANVAS, STRAW, 0.35), 1.0, R)
    _reg("item", "paper", vs)
    x, y = ITEMS["pot"]
    vs, _ = _cyl(a, (x + dx, y + dy, z), up, 0.30, 0.50, 6, METAL, 1.0, r_top=0.26)
    _reg("lid", "pot", vs)


# ---- barrel, crates, stones (spec 1.4) ----------------------------------------------------------------------------------
BARREL = {"c": (-6.00, 2.00), "rot": 10.0}
BARREL_R0, BARREL_R1, BARREL_H, HOOP = 1.00, 1.10, 2.80, 0.05
BARREL_N = 8


def barrel(a, c=None, rot=None, tag="barrel"):
    """An open hooped barrel: 8 staves (per-stave tint) bulging from 2.0 to 2.2, two iron hoops 0.22 tall proud 0.05
    (rings of the body), an open top whose pale contents sit 0.15 below the rim."""
    c = c or BARREL["c"]
    n = BARREL_N
    R = _R(c, (BARREL["rot"] if rot is None else rot) + 180 / n)

    def r_at(z):
        return BARREL_R0 + (BARREL_R1 - BARREL_R0) * (1 - ((z - BARREL_H / 2) / (BARREL_H / 2)) ** 2)
    prof = [(0.0, 0), (0.24, 0), (0.24, 1), (0.46, 1), (0.46, 0), (BARREL_H / 2, 0), (2.34, 0), (2.34, 1),
            (2.56, 1), (2.56, 0), (BARREL_H, 0)]
    ang = [2 * math.pi * k / n for k in range(n)]
    rings = []
    for z, hoop in prof:
        r = r_at(z) + (HOOP if hoop else 0.0)
        rings.append([Vector((math.cos(t) * r, math.sin(t) * r, z)) for t in ang])
    rin = 0.86 * BARREL_R0
    rings.append([Vector((math.cos(t) * rin, math.sin(t) * rin, BARREL_H)) for t in ang])
    rings.append([Vector((math.cos(t) * rin, math.sin(t) * rin, BARREL_H - 0.15)) for t in ang])
    pts = [R @ p for r in rings for p in r]
    faces, keys, stave = [], [], []
    nr = len(prof)
    for i in range(nr - 1):
        hoop = prof[i][1] or prof[i + 1][1]
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, (i + 1) * n + j1, (i + 1) * n + j])
            keys.append(IRON if hoop else WOOD_DARK)
            stave.append(j)
    for i in (nr - 1, nr):
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, (i + 1) * n + j1, (i + 1) * n + j])
            keys.append(_mix(WOOD_DARK, PLANK, 0.25) if i == nr - 1 else WOOD_DARK)
            stave.append(j)
    faces.append([(nr + 1) * n + j for j in range(n)])
    keys.append(PALE)
    stave.append(-1)
    faces.append(list(reversed(range(n))))
    keys.append(WOOD_DARK)
    stave.append(-1)
    vs, fs = _shell(a, pts, faces, WOOD_DARK, 1.0)
    rng = random.Random(_seed(tag))
    st = [1.0 + rng.uniform(-0.06, 0.06) for _ in range(n)]
    for f, k, s in zip(fs, keys, stave):
        if k != WOOD_DARK:
            f.material_index = a._mi(k)
        if s >= 0 and k == WOOD_DARK:
            _tint(a, [f], st[s])
    _reg("barrel", tag, vs)


CRATES = {"A": ((4.50, -2.50), 0.0), "B": ((4.40, 2.60), 90.0)}
CR_W, CR_H, CR_FW, CR_RD, CR_BW, CR_BT, CR_IN = 2.30, 2.10, 0.26, 0.05, 0.20, 0.05, 0.25


def crate(a, c, rot, tag):
    """An open crate (spec 1.4): four sides with a 0.26 frame round a panel recessed 0.05 and an X brace of three
    boards on each panel, an open top whose rim walls are the frame width, an inner floor 0.25 below the rim with a
    heaped straw mound on it."""
    R = _R(c, rot)
    W, H = CR_W, CR_H
    h = W / 2
    hi_ = h - CR_FW
    zf = H - CR_IN
    cor = [Vector((-h, -h, 0)), Vector((h, -h, 0)), Vector((h, h, 0)), Vector((-h, h, 0)),
           Vector((-h, -h, H)), Vector((h, -h, H)), Vector((h, h, H)), Vector((-h, h, H)),
           Vector((-hi_, -hi_, H)), Vector((hi_, -hi_, H)), Vector((hi_, hi_, H)), Vector((-hi_, hi_, H)),
           Vector((-hi_, -hi_, zf)), Vector((hi_, -hi_, zf)), Vector((hi_, hi_, zf)), Vector((-hi_, hi_, zf))]
    pts = list(cor)
    faces, keys = [], []
    frame_key = _mix(WOOD_DARK, PLANK, 0.35)
    faces.append([3, 2, 1, 0])
    keys.append(WOOD_DARK)
    for k in range(4):
        k1 = (k + 1) % 4
        faces.append([4 + k, 4 + k1, 8 + k1, 8 + k])            # rim
        keys.append(frame_key)
        faces.append([8 + k, 8 + k1, 12 + k1, 12 + k])          # inner wall
        keys.append(WOOD_DARK)
    faces.append([12, 13, 14, 15])
    keys.append(WOOD_DARK)
    sides = [((0, 1, 5, 4), Vector((0, -1, 0))), ((1, 2, 6, 5), Vector((1, 0, 0))),
             ((2, 3, 7, 6), Vector((0, 1, 0))), ((3, 0, 4, 7), Vector((-1, 0, 0)))]
    panels = []
    for (b0, b1, t1, t0), nrm in sides:
        P0, P1, P2, P3 = pts[b0], pts[b1], pts[t1], pts[t0]
        U = (P1 - P0).normalized()
        V = Vector((0, 0, 1))
        q = [P0 + U * CR_FW + V * CR_FW, P1 - U * CR_FW + V * CR_FW, P2 - U * CR_FW - V * CR_FW,
             P3 + U * CR_FW - V * CR_FW]
        qi = len(pts)
        pts += q
        ri = len(pts)
        pts += [p - nrm * CR_RD for p in q]
        faces += [[b0, b1, qi + 1, qi], [b1, t1, qi + 2, qi + 1], [t1, t0, qi + 3, qi + 2], [t0, b0, qi, qi + 3]]
        keys += [frame_key] * 4
        for k in range(4):
            k1 = (k + 1) % 4
            faces.append([qi + k, qi + k1, ri + k1, ri + k])
            keys.append(WOOD_DARK)
        faces.append([ri, ri + 1, ri + 2, ri + 3])
        keys.append(WOOD_DARK)
        panels.append((q, nrm, U))
    pts = [R @ p for p in pts]
    vs, fs = _shell(a, pts, faces, WOOD_DARK, 1.0)
    rng = random.Random(_seed(tag))
    for f, k in zip(fs, keys):
        if k != WOOD_DARK:
            f.material_index = a._mi(k)
        else:
            _tint(a, [f], 1.0 + rng.uniform(-0.05, 0.05))
    _reg("crate", f"crate_{tag}", vs)
    for si, (q, nrm, U) in enumerate(panels):
        cen = sum(q, Vector()) / 4 - nrm * CR_RD
        A_, B_ = W / 2 - CR_FW, H / 2 - CR_FW
        hw = CR_BW / 2
        V = Vector((0, 0, 1))

        def fit(dv, nv):
            return min((A_ - hw * abs(nv[0])) / max(abs(dv[0]), 1e-6), (B_ - hw * abs(nv[1])) / max(abs(dv[1]), 1e-6))
        dA = Vector((A_, B_)).normalized()
        nA = Vector((-dA.y, dA.x))
        LA = fit(dA, nA)
        dB = Vector((-A_, B_)).normalized()
        nB = Vector((-dB.y, dB.x))
        LB = fit(dB, nB)

        def to3(u, v, w):
            return R @ (cen + U * u + V * v + nrm * w)

        def hexa2d(quad):
            return [to3(u, v, -0.005) for u, v in quad] + [to3(u, v, CR_BT - 0.005) for u, v in quad]
        quadA = [dA * -LA + nA * -hw, dA * LA + nA * -hw, dA * LA + nA * hw, dA * -LA + nA * hw]
        vs, _ = _shell(a, hexa2d([(p.x, p.y) for p in quadA]), HEXA, frame_key, _rt(f"{tag}A{si}", 0.04))
        _reg("plank", f"crate_{tag}_A{si}", vs)
        for hi, sg in enumerate((1, -1)):
            sgnA = 1 if nA.dot(dB * sg) > 0 else -1
            corners = []
            for e in (-1, 1):
                t_in = (sgnA * hw - e * hw * nA.dot(nB)) / nA.dot(dB)
                corners.append((dB * t_in + nB * (e * hw), dB * (sg * LB) + nB * (e * hw)))
            quad = [corners[0][0], corners[0][1], corners[1][1], corners[1][0]]
            vs, _ = _shell(a, hexa2d([(p.x, p.y) for p in quad]), HEXA, frame_key, _rt(f"{tag}B{si}{hi}", 0.04))
            _reg("plank", f"crate_{tag}_B{si}_{hi}", vs)
    straw(a, R, tag)


def straw(a, R, tag):
    """The heaped straw (exploded crates): a convex mound on the inner floor, its foot 0.04 clear of the rim walls,
    0.45 above the rim; blended toward straw_deep at its foot (by height)."""
    rng = random.Random(_seed(tag) + 7)
    zf = CR_H - CR_IN
    ri = CR_W / 2 - CR_FW - 0.04
    pts = []
    for k in range(7):
        t = 2 * math.pi * k / 7 + rng.uniform(-0.15, 0.15)
        rr = ri * rng.uniform(0.94, 1.0) / max(abs(math.cos(t)), abs(math.sin(t)), 0.75) * 0.82
        pts.append(Vector((math.cos(t) * min(rr, ri), math.sin(t) * min(rr, ri), zf + 0.002)))
    for k in range(5):
        t = 2 * math.pi * k / 5 + rng.uniform(-0.2, 0.2) + 0.3
        rr = ri * rng.uniform(0.68, 0.80)
        pts.append(Vector((math.cos(t) * rr, math.sin(t) * rr, CR_H + rng.uniform(0.12, 0.20))))
    for k in range(2):
        pts.append(Vector((rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25), CR_H + rng.uniform(0.38, 0.45))))
    pts = [R @ p for p in pts]
    vs, fs, _ = _hull(a, pts, STRAW, _rt(tag + "s", 0.03))
    for f in fs:
        if f.is_valid:
            zc = f.calc_center_median().z
            if zc < CR_H - 0.05:
                f.material_index = a._mi(_mix(STRAW, STRAW_DEEP, 0.75))
            elif zc < CR_H + 0.12:
                f.material_index = a._mi(_mix(STRAW, STRAW_DEEP, 0.40))
    _texture(a, vs, 0.04, _seed(tag) + 9, scale=1.2)
    _reg("straw", f"straw_{tag}", vs)


STONES = {"S1": ((-4.60, -5.90), (1.00, 0.90, 0.80), 20.0, 661), "S2": ((2.40, -5.50), (0.80, 0.75, 0.65), 35.0, 662)}


def stone(a, c, size, rot_deg, seed, tag):
    """(m064) A chunky pale faceted block: a box with two top corners broken off and a little jitter, a flat bottom;
    its lowest 30 % blended toward stone_deep by height."""
    rng = random.Random(seed)
    sx, sy, sz = size[0] / 2, size[1] / 2, size[2]
    R = _R(c, rot_deg)
    pts = [Vector((x * sx * rng.uniform(0.92, 1.0), y * sy * rng.uniform(0.92, 1.0), 0.0))
           for x, y in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
    for k, (x, y) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        top = Vector((x * sx * rng.uniform(0.85, 0.95), y * sy * rng.uniform(0.85, 0.95), sz * rng.uniform(0.92, 1.0)))
        if k in (0, 2):
            cut = rng.uniform(0.28, 0.38)
            pts += [top - Vector((x * sx * cut, 0, 0)), top - Vector((0, y * sy * cut, 0)),
                    top - Vector((0, 0, sz * cut * 1.1))]
        else:
            pts.append(top)
    pts = [R @ p for p in pts]
    vs, fs, _ = _hull(a, pts, STONE, _rt(tag, 0.03))
    for f in fs:
        if f.is_valid and f.calc_center_median().z < 0.30 * sz:
            f.material_index = a._mi(_mix(STONE, STONE_DEEP, 0.5))
    _texture(a, vs, 0.05, seed, scale=1.2)
    _reg("stone", f"stone_{tag}", vs)


# ---- assemblies -----------------------------------------------------------------------------------------------------------
def _fx_spec(rng=14):
    """Decision 13: heat_glow overridden to a steady warm lantern halo (M064's settings), PointLight range 14."""
    return {"emitters": [{"name": "Halo", "texture": "glow_soft", "color": ["#FFC23A", "#FF9A1E"], "size": [1.4, 1.7],
                          "transparency": [0.65, 1.0], "lifetime": [1.0, 1.5], "rate": 2, "speed": [0, 0.05],
                          "spread": 0, "light_emission": 1.0}],
            "light": {"color": "#FFB347", "brightness": 1.0, "range": rng, "flicker": True}}


def _clear():
    PIECES.clear()
    ROPES.clear()


def hero_all(a):
    _clear()
    GEO.clear()
    FX.clear()
    planes = {}
    collars = {}
    for tag in POSTS:
        planes[tag] = stone_base(a, tag)
        post(a, tag)
        collars[tag] = collar(a, tag)
    ridge(a)
    for tag in CROSSBARS:
        crossbar(a, tag)
    _, T = canvas_sheet(a)
    nub(a, T)
    ridge_tab(a)
    for tag in ("FL", "BL", "FR"):
        lashing_crossbar(a, tag)
    for tag in ("FR", "BR"):
        lashing_ridge(a, tag)
    for tag in ("FL", "BL"):
        tail(a, tag)
    for tag, (px, py, _) in POSTS.items():
        s = 1.0 if px > 0 else -1.0
        G = peg_geometry(px, py, s, planes[tag])
        band = peg(a, G, f"peg_{tag}")
        peg_rope(a, tag, band, collars[tag][0], planes[tag])
        GEO.setdefault("peg_foot", {})[tag] = [round(x, 3) for x in G["F"]]
    rod(a)
    rod_band(a)
    top = sleeve(a)
    ec = banner(a, top)
    GEO["emblem_centre"] = [round(x, 3) for x in ec]
    base = Vector((LAN_X, ROD_Y, lantern_drop()))
    gc, ring_top = lantern(a, base)
    FX.append(("heat_glow", gc, _fx_spec(14)))
    GEO["lantern"] = {"base_z": round(base.z, 3), "body_top": round(base.z + L_BODY, 3),
                      "ring_top": round(ring_top.z, 3), "glass": [round(x, 3) for x in gc]}
    table(a)
    items(a)
    bench(a, LONG_BENCH["c"], LONG_BENCH["L"], "bench_long")
    bench(a, SHORT_BENCH["c"], SHORT_BENCH["L"], "bench_short")
    stool(a)
    barrel(a)
    for tag, (c, rot) in CRATES.items():
        crate(a, c, rot, tag)
    for tag, (c, size, r, seed) in STONES.items():
        stone(a, c, size, r, seed, tag)


PART_INFO = {}


def post_part(a):
    """CanvasShelterPost: the 12.0 post on its stone base with its two-turn foot collar (close-up 2)."""
    _clear()
    stone_base(a, "FR", at=(0.0, 0.0))
    post(a, "FR", at=(0.0, 0.0))
    collar(a, "FR", at=(0.0, 0.0))
    PART_INFO["post_top"] = Vector((0.0, 0.0, POSTS["FR"][2]))


def ridge_part(a):
    """CanvasShelterRidgePole: the ridge with a rope band where each lashing sits (spec 3.17)."""
    _clear()
    ridge(a, x=0.0)
    zc = (RIDGE_Z0 + RIDGE_Z1) / 2
    e = RIDGE_H + RT_L - SINK
    for i, y in enumerate((-4.6, 4.6)):
        path = [Vector((sx * e, y, zc + sz * e)) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        rope(a, path, RT_L, 6, True, f"ridge_band{i}", up=Vector((0, 1, 0)), twist=False)


def canopy_part(a):
    """CanvasShelterCanopy: the sagging sheet with its centre nub (the corner tabs belong to the posts)."""
    _clear()
    _, T = canvas_sheet(a)
    nub(a, T)


def banner_part(a):
    """CanvasShelterBanner: rod, knob, sleeve, banner and emblems."""
    _clear()
    rod(a)
    top = sleeve(a)
    banner(a, top)
    PART_INFO["banner_hang"] = Vector((ROD_X0, ROD_Y, ROD_Z + ROD_R * math.cos(math.pi / 6)))


def lantern_part(a):
    _clear()
    gc, top = lantern(a, (0.0, 0.0, 0.0))
    PART_INFO["glass"] = gc
    PART_INFO["hang"] = top


def table_part(a):
    _clear()
    table(a, (0.0, 0.0))


def bench_part(a):
    _clear()
    bench(a, (0.0, 0.0), LONG_BENCH["L"], "bench_long")


def stool_part(a):
    _clear()
    stool(a, (0.0, 0.0), 0.0)


def crate_part(a):
    _clear()
    crate(a, (0.0, 0.0), 0.0, "A")


def barrel_part(a):
    _clear()
    barrel(a, (0.0, 0.0), 0.0)


def peg_part(a):
    _clear()
    G = peg_geometry(0.0, 0.0, 1.0, None)
    peg(a, G, "peg")


NOTES = {
    HERO: "Open walk-under camp shelter: four chamfered square posts on faceted stone bases (12.0 right, 10.4 left), "
          "a ridge pole lashed level along the tall side, crossbars, one sagging cream canvas slab tied at its corners "
          "with gold X-lashings, foot collars, leaning pegs, a red swallowtail banner on an iron rod, a hexagonal Neon "
          "lantern (heat_glow halo); a plank table with Neon candle jars, a bottle, a paper and a pot, two benches, a "
          "stool, two open straw crates, an open barrel and two stones. Walk-under (Requires Manual Validation in "
          "Studio). Sheet header 65/132.",
    POST_P: "Wood Post (x4): a 12.0 chamfered square post on its faceted stone base with a two-turn rope collar "
            "(the 10.4 posts are this mesh scaled in Studio or cut)",
    RIDGE_P: "Ridge Pole: 0.80 chamfered square timber, 11.8 long, with the two rope bands where it is lashed",
    CANOPY_P: "Canvas Canopy: the sagging 0.10 canvas sheet with X creases and its centre knot",
    BANNER_P: "Banner & Rod (x1): red swallowtail banner with a white diamond emblem on both faces, iron rod and knob",
    LANTERN_P: "Lantern: hexagonal dark-metal lantern with Neon amber glass and a hanging ring (heat_glow halo)",
    TABLE_P: "Table: four-plank table on square legs with cleats and stretchers (top 2.60)",
    BENCH_P: "Bench: two-plank bench on four legs with end rails (seat 1.50; the short bench is this one cut)",
    STOOL_P: "Stool: two-plank square stool on four legs (seat 1.50)",
    CRATE_P: "Crate: open framed crate with X braces, heaped with straw",
    BARREL_P: "Barrel: eight-stave open barrel with two iron hoops and pale contents",
    PEG_P: "Peg (x4): square stake with a pale end-grain top and a rope band",
}
COLLISION = {HERO: "precise", POST_P: "hull", RIDGE_P: "box", CANOPY_P: "none", BANNER_P: "none",
             LANTERN_P: "none", TABLE_P: "box", BENCH_P: "box", STOOL_P: "box", CRATE_P: "box", BARREL_P: "hull",
             PEG_P: "none"}


def _bottom_centre(o):
    xs = [v.co.x for v in o.data.vertices]
    ys = [v.co.y for v in o.data.vertices]
    zs = [v.co.z for v in o.data.vertices]
    return Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))


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
    _clear()
    fn(a)
    o = a.finish(collection=M.coll(NUM, TITLE), mark_asset=not temp, origin=None)
    K.drop_unused_slots(o)
    if not temp:
        K.tag(o, SHEET, TITLE, role, COLLISION[name], budget, NOTES[name])
    o[OFF] = [0.0, 0.0, 0.0]
    o.location = (0, 0, 0)
    o["m066_pieces"] = json.dumps([[k, n_, [round(x, 5) for x in c]] for k, n_, c in PIECES])
    o["m066_ropes"] = json.dumps(ROPES)
    bpy.context.view_layer.update()
    return o


def _recentre(o):
    bc = _bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


def _min_angle(pts):
    out = math.pi
    for k, p in enumerate(pts):
        u, v = pts[k - 1] - p, pts[(k + 1) % len(pts)] - p
        out = min(out, u.angle(v) if u.length > 1e-9 and v.length > 1e-9 else 0.0)
    return out


def _thin(o, lim=3.0):
    """(m012) Faces with a corner under lim degrees, and the smallest corner angle on the mesh."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    angs = [_min_angle([v.co for v in f.verts]) for f in bm.faces]
    bm.free()
    return {"under": sum(1 for x in angs if x < math.radians(lim)), "min_deg": round(math.degrees(min(angs)), 2)}


def _uv_overlaps(o):
    """(m012) Pairs of faces whose UV triangles overlap (as M.uv_stats counts them)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    uv = bm.loops.layers.uv.active
    tris = [[(l[uv].uv.x, l[uv].uv.y) for l in f.loops] for f in bm.faces]
    bm.free()
    boxes = [(min(p[0] for p in t), min(p[1] for p in t), max(p[0] for p in t), max(p[1] for p in t)) for t in tris]
    grid = {}
    for k, b in enumerate(boxes):
        for i in range(int(b[0] // 0.05), int(b[2] // 0.05) + 1):
            for j in range(int(b[1] // 0.05), int(b[3] // 0.05) + 1):
                grid.setdefault((i, j), []).append(k)
    pairs = {(a_, b_) for lst in grid.values() for i, a_ in enumerate(lst) for b_ in lst[i + 1:]}
    return [(a_, b_) for a_, b_ in pairs if M._tri_overlap(tris[a_], tris[b_])]


def _uv_unfold(o, rounds=4):
    """(m012) Cut the smaller face of each UV-overlapping pair free along seams and unwrap again."""
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
    """Stage 2-3 pass: every face a triangle, normals outward per shell, flat shading, origin at the bbox bottom centre,
    UVs (angle-based islands, overlaps cut free), bowties split."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
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
CAT = {"post": "wood", "ridge": "wood", "crossbar": "wood", "peg": "wood", "plank": "wood", "crate": "wood",
       "barrel": "wood", "base": "stone", "stone": "stone", "canvas": "canvas", "tab": "canvas", "rope": "rope",
       "lmetal": "metal", "rod": "metal", "lid": "metal", "glass": "glass", "jar": "glass", "banner": "banner",
       "emblem": "banner", "straw": "straw", "item": "item"}
SINK_LIMIT = {("rope", "rope"): 0.08}
THIN_KINDS = ("canvas", "tab", "banner")


def _shells(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    groups = [[] for _ in range(n)]
    for f in bm.faces:
        groups[ids[f.index]].append(f)
    off = Vector(o[OFF]) if OFF in o else Vector()
    reg = [(k, nm, Vector(c)) for k, nm, c in json.loads(o.get("m066_pieces", "[]"))]
    labels, used = [], set()
    for fs in groups:
        vs = list({v for f in fs for v in f.verts})
        c = sum((v.co for v in vs), Vector()) / len(vs) + off
        best = min(((i, (rc - c).length) for i, (_, _, rc) in enumerate(reg) if i not in used),
                   key=lambda x: x[1], default=(None, 0))
        if best[0] is not None and best[1] < 0.06:
            used.add(best[0])
            labels.append(reg[best[0]][:2])
        else:
            labels.append(("?", "?"))
    return bm, ids, n, groups, labels


def shells_report(o):
    """(m064) Per shell: kind, name, tris, non-manifold edges and verts, boundary edges, winding errors (manifold edges
    whose two faces run the same way round), self-intersecting face pairs, signed volume."""
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
        out.append({"kind": labels[k][0], "name": labels[k][1], "tris": len(fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary),
                    "winding_errors": sum(1 for e in es if e.is_manifold and not e.is_contiguous),
                    "self_hits": hits, "volume": round(vol, 5)})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1, seats=()):
    """(m064) No floating pieces (STAGES): per shell its nearest gap to another shell (0 where triangles intersect) or
    the ground, and whether it chains by contact to the ground. seats = [(name, name)] pair gaps to report."""
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
    ground = {k for k in range(n) if zmin[k] - z0 <= tol}
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
    idx = {labels[k][1]: k for k in range(n)}

    def pair_gap(x, y):
        if x not in idx or y not in idx:
            return None
        a_, b_ = idx[x], idx[y]
        best = near.get((min(a_, b_), max(a_, b_)), 9.0)
        trees = []
        for k in (a_, b_):
            vs = list({v for f in groups[k] for v in f.verts})
            vi = {v: i for i, v in enumerate(vs)}
            trees.append(BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in groups[k]]))
        for src, tr in ((groups[a_], trees[1]), (groups[b_], trees[0])):
            for f in src:
                cs = [v.co for v in f.verts]
                if len(cs) != 3:
                    continue
                for i in range(13):
                    for j in range(13 - i):
                        w = (i / 12, j / 12, 1 - i / 12 - j / 12)
                        p = cs[0] * w[0] + cs[1] * w[1] + cs[2] * w[2]
                        hit = tr.find_nearest(p)
                        if hit[0] is not None:
                            best = min(best, hit[3])
        return round(best, 3)
    unch = chained(tol)
    res = {"shells": n, "floating": len(floating), "floating_names": [labels[k][1] for k in floating],
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "unchained": len(unch), "unchained_names": unch, "unchained_chain_tol": len(chained(chain_tol)),
           "on_ground": sorted({labels[k][0] for k in ground}),
           "sink": round(z0 + (o[OFF][2] if OFF in o else 0.0), 3),
           "kinds": {k: [lb[0] for lb in labels].count(k) for k in sorted({lb[0] for lb in labels})},
           "seats": {f"{x}|{y}": pair_gap(x, y) for x, y in seats}}
    bm.free()
    return res


def bury_report(o):
    """(m064) Nothing buried (STAGES): per shell pair, the deepest vert / face centre of one inside the other (ray
    parity, depth to its surface), judged against BURY (SINK_LIMIT for rope joins); and shells wholly inside others."""
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
        info.append({"cat": CAT.get(labels[s][0], "?"), "name": labels[s][1], "lo": lo, "hi": hi, "tree": tree,
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
                if _parity_in(B["tree"], p):
                    inside_any[j] = True
                    dmax = max(dmax, B["tree"].find_nearest(p)[3])
            if dmax <= 0:
                continue
            pair = (A["cat"], B["cat"])
            worst[pair] = max(worst.get(pair, 0.0), dmax)
            lim = SINK_LIMIT.get(pair, BURY)
            if dmax > lim + 1e-3:
                over.append({"shell": A["name"], "in": B["name"], "depth": round(dmax, 3)})
        if all(inside_any):
            hidden.append(A["name"])
    bm.free()
    return {"worst_depth": {f"{a_}>{b_}": round(d, 3) for (a_, b_), d in sorted(worst.items())},
            "over_limit": over, "fully_hidden": hidden, "buried": len(over) + len(hidden)}


def pierce_report(o):
    """(m064) Thin slabs hide pass-throughs from the bury report (a 0.10 canvas is at most 0.05 deep anywhere): count
    the edges of every other shell that cross a thin surface (canvas, tabs, banner) twice."""
    bm, ids, n, groups, labels = _shells(o)
    cos, polys = [], []
    for k in range(n):
        if labels[k][0] not in THIN_KINDS:
            continue
        vs = list({v for f in groups[k] for v in f.verts})
        vi = {v: i + len(cos) for i, v in enumerate(vs)}
        cos += [v.co.copy() for v in vs]
        polys += [[vi[v] for v in f.verts] for f in groups[k]]
    out = {}
    if polys:
        tree = BVHTree.FromPolygons(cos, polys)
        for k in range(n):
            if labels[k][0] in THIN_KINDS:
                continue
            bad = 0
            for e in {e for f in groups[k] for e in f.edges}:
                p, q = e.verts[0].co, e.verts[1].co
                d = q - p
                L = d.length
                if L < 1e-6:
                    continue
                d = d / L
                hits, t0 = 0, 0.0
                while t0 < L and hits < 2:
                    h = tree.ray_cast(p + d * (t0 + 1e-4), d, L - t0 - 1e-4)
                    if h[0] is None:
                        break
                    hits += 1
                    t0 = (h[0] - p).length + 1e-4
                bad += hits >= 2
            if bad:
                out[labels[k][1]] = bad
    bm.free()
    return out


def rope_ends_report(o):
    """(m064) Decision 6: every open rope touches what it ties at both ends: each end point's gap to the nearest other
    shell (surface distance minus the rope radius, 0 when the end is inside another shell)."""
    bm, ids, n, groups, labels = _shells(o)
    off = Vector(o[OFF])
    fsh = [ids[f.index] for f in bm.faces]
    tree = BVHTree.FromBMesh(bm)
    byname = {labels[k][1]: k for k in range(n)}
    out, bad = {}, []
    for r in json.loads(o.get("m066_ropes", "[]")):
        k = byname.get(r["name"])
        if k is None:
            continue
        gaps = []
        for p in r["ends"]:
            q = Vector(p) - off
            best = 9.0
            for loc, nrm, fi, d in tree.find_nearest_range(q, r["rt"] + 0.3):
                if fsh[fi] != k:
                    best = min(best, d)
            gaps.append(round(max(0.0, best - r["rt"]), 3) if best < 9 else None)
        out[r["name"]] = gaps
        if any(g is None or g > CONTACT for g in gaps):
            bad.append(r["name"])
    bm.free()
    return {"ends": out, "loose": bad}


def _hero_tree(o, skip_kinds=()):
    bm, ids, n, groups, labels = _shells(o)
    off = Vector(o[OFF])
    cos, polys, owner = [], [], []
    for k in range(n):
        if labels[k][0] in skip_kinds:
            continue
        vs = list({v for f in groups[k] for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        co = [v.co + off for v in vs]
        pl = [[vi[v] for v in f.verts] for f in groups[k]]
        base = len(cos)
        cos += co
        polys += [[base + i for i in p] for p in pl]
        owner += [labels[k][1]] * len(pl)
    bm.free()
    return BVHTree.FromPolygons(cos, polys), owner


PROXY = ((1.0, 0.5, 0.0, 4.4), (0.55, 0.5, 4.4, 5.5))     # (half x, half y, z0, z1): body, head (spec 2.10)
LANES = {"front_x-2.0": (-2.0, -8.0, -1), "front_x+0.2": (0.2, -8.0, -1), "back_x-2.0": (-2.0, 8.0, 1),
         "back_x+0.2": (0.2, 8.0, 1)}


def walk_report(o):
    """Spec 2.10: a 2 x 1 x 5.5 proxy (head 1.1 wide above 4.4) walks in from the front (y -8) to the short bench's
    front and from the back (y +8) to the long bench's back, in two lanes each: the nearest hero surface to its sampled
    surface along the way. Also the canvas underside's lowest point over the floor inside the posts (sampled by rays
    straight up) and the lantern bottom."""
    tree, owner = _hero_tree(o)
    samples = []
    for hx, hy, z0, z1 in PROXY:
        for i in range(9):
            for j in range(9):
                u, w = -1 + 2 * i / 8, -1 + 2 * j / 8
                z = max(z0, 0.02) + (z1 - max(z0, 0.02)) * j / 8
                samples += [Vector((hx * u, -hy, z)), Vector((hx * u, hy, z)), Vector((-hx, hy * u, z)),
                            Vector((hx, hy * u, z)), Vector((hx * u, hy * w, z1))]
    sb = SHORT_BENCH["c"][1] - 0.61 - 0.5 - 0.05
    lb = LONG_BENCH["c"][1] + 0.61 + 0.5 + 0.05
    res = {}
    worst_all = (9.0, None, None)
    for lane, (x, y0, sgn) in LANES.items():
        y1 = sb if sgn < 0 else lb
        worst, at, who = 9.0, None, None
        y = y0
        steps = int(abs(y1 - y0) / 0.1) + 1
        for s in range(steps + 1):
            y = y0 + (y1 - y0) * s / steps
            for p0 in samples:
                p = p0 + Vector((x, y, 0))
                loc, nrm, fi, d = tree.find_nearest(p)
                if d < worst:
                    worst, at, who = d, round(y, 2), owner[fi]
        res[lane] = {"min_clearance": round(worst, 3), "at_y": at, "nearest": who, "end_y": round(y1, 2)}
        if worst < worst_all[0]:
            worst_all = (worst, lane, who)
    # canvas underside over the floor inside the posts (rays up from z 0.05 at a 0.25 grid, canvas faces only)
    ctree, cown = _hero_tree(o, skip_kinds=tuple(k for k in CAT if k not in ("canvas",)) + ("?",))
    low, at = 99.0, None
    x = -5.85
    while x <= 5.85:
        y = -4.05
        while y <= 4.05:
            h = ctree.ray_cast(Vector((x, y, 0.05)), Vector((0, 0, 1)), 30.0)
            if h[0] is not None and h[0].z < low:
                low, at = h[0].z, (round(x, 2), round(y, 2))
            y += 0.25
        x += 0.25
    res["min_clearance"] = round(worst_all[0], 3)
    res["worst_lane"] = worst_all[1]
    res["canvas_under_min"] = round(low, 3)
    res["canvas_under_min_at"] = at
    res["head_room_over_5.5"] = round(low - 5.5, 3)
    res["lantern_bottom"] = (GEO.get("lantern") or {}).get("base_z")
    return res


def placement_report(o):
    """Measured targets (spec 4.4): post tops and spacing, canvas corner heights and lowest point, ridge, banner,
    lantern, table, extents."""
    out = {"post_tops": {t: z for t, (_, _, z) in POSTS.items()},
           "post_spacing": [round(POSTS["FR"][0] - POSTS["FL"][0], 3), round(POSTS["BL"][1] - POSTS["FL"][1], 3)],
           "canvas_corners_top": {t: round(p.z, 3) for t, p in canvas_corners().items()},
           "canvas_low_top": GEO.get("canvas_low_top"), "canvas_low_under": GEO.get("canvas_low_under"),
           "canvas_centre_top": GEO.get("canvas_centre_top"),
           "ridge_z": [RIDGE_Z0, RIDGE_Z1], "ridge_len": round(2 * RIDGE_Y, 3),
           "tip_above_ridge": round(POSTS["FR"][2] - RIDGE_Z1, 3),
           "banner": GEO.get("banner"), "lantern": GEO.get("lantern"), "table": GEO.get("table"),
           "size": [round(d, 3) for d in o.dimensions], "peg_foot": GEO.get("peg_foot")}
    return out


# ---- build ---------------------------------------------------------------------------------------------------------------
PARTS = ((POST_P, post_part), (RIDGE_P, ridge_part), (CANOPY_P, canopy_part), (BANNER_P, banner_part),
         (LANTERN_P, lantern_part), (TABLE_P, table_part), (BENCH_P, bench_part), (STOOL_P, stool_part),
         (CRATE_P, crate_part), (BARREL_P, barrel_part), (PEG_P, peg_part))
TARGET_SIZE = ((17.6, 0.5), (12.3, 0.4), (12.0, 0.3))    # hero W (X), D (Y), H (Z) +- tolerance (decision 1)
HERO_BUDGET = 4000
THIN_FLOOR = 0.3
SEATS = [("post_FL", "base_FL"), ("post_FR", "base_FR"), ("ridge", "post_FR"), ("ridge", "post_BR"),
         ("crossbar_FL", "post_FL"), ("crossbar_BL", "post_BL"), ("crossbar_FR", "post_FR"),
         ("tab_FL", "post_FL"), ("tab_BL", "post_BL"), ("tab_FR", "post_FR"), ("tab_BR", "ridge"),
         ("canvas", "tab_FL"), ("canvas", "tab_BL"), ("canvas", "tab_FR"), ("canvas", "tab_BR"),
         ("rod", "crossbar_FR"), ("sleeve", "rod"), ("banner", "sleeve"), ("lantern_ring", "crossbar_FR"),
         ("peg_FL_stake", "base_FL"), ("peg_FR_stake", "base_FR"), ("peg_BL_stake", "base_BL"),
         ("peg_BR_stake", "base_BR"), ("jar_J1", "table_plank2"), ("straw_A", "crate_A"), ("nub", "canvas")]


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m066_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", HERO))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def _sockets(h):
    for c in [c for c in h.children if c.get("vfx_kind")]:
        bpy.data.objects.remove(c, do_unlink=True)
    off = Vector(h[OFF])
    return [K.socket(h, kind, Vector(p) - off, **kw) for kind, p, kw in FX]


def export_stats(objs):
    out = {}
    for o in objs:
        socks = [c for c in o.children_recursive if c.get("vfx_kind")]
        glow = sorted({m.name[3:] for m in o.data.materials if list(m.get("flintkit_spec", [0, 0, 0]))[2] >= NEON})
        out[o.name] = {"vfx_sockets": len(socks), "kinds": [c["vfx_kind"] for c in socks], "glow_keys": glow}
    return out


def _store(h, objs):
    off = Vector(h[OFF])
    h["m066_centre"] = [round(x, 3) for x in Vector((0, 0, 0)) - off]
    h["m066_seat_back"] = [round(x, 3) for x in Vector((*LONG_BENCH["c"], SEAT)) - off]
    h["m066_seat_front"] = [round(x, 3) for x in Vector((*SHORT_BENCH["c"], SEAT)) - off]
    h["m066_seat_stool"] = [round(x, 3) for x in Vector((*STOOL["c"], SEAT)) - off]
    h["m066_lantern"] = [round(x, 3) for x in Vector(GEO["lantern"]["glass"]) - off]
    if LANTERN_P in objs:
        lp = objs[LANTERN_P]
        lp["m066_hang"] = [round(x, 3) for x in PART_INFO["hang"] - Vector(lp[OFF])]
        for c in [c for c in lp.children if c.get("vfx_kind")]:
            bpy.data.objects.remove(c, do_unlink=True)
        K.socket(lp, "heat_glow", PART_INFO["glass"] - Vector(lp[OFF]), **_fx_spec(14))
    if BANNER_P in objs:
        bp = objs[BANNER_P]
        bp["m066_hang"] = [round(x, 3) for x in PART_INFO["banner_hang"] - Vector(bp[OFF])]
    if POST_P in objs:
        pp = objs[POST_P]
        pp["m066_top"] = [round(x, 3) for x in PART_INFO["post_top"] - Vector(pp[OFF])]


def build(render=True, parts=True, close=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn)
        objs[BARREL_P]["kit_shading_ok"] = ("the pale contents disc and the iron hoops are two materials that both "
                                            "fall in the near-grey family")
    h, log["hero"] = _make(HERO, hero_all, "hero", HERO_BUDGET)
    geo = json.loads(json.dumps(GEO, default=lambda v: [round(x, 3) for x in v]))
    _sockets(h)
    _store(h, objs)
    _cleanup_tmp()
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.2f} x {d.y:.2f} x {d.z:.2f}"
    audits = [M.audit(o) for o in order]
    thin = {o.name: _thin(o, 3.0) for o in order}
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
            for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "winding_errors", "self_hits"):
                if s[k]:
                    problems.append(f"{o.name} shell {i} ({s['name']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['name']}): not closed outward (volume {s['volume']})")
            if s["kind"] == "?":
                problems.append(f"{o.name} shell {i}: not matched to a built piece")
    contact = {o.name: contact_report(o, seats=SEATS if o is h else ()) for o in order}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: floating {c['floating_names']}, unchained {c['unchained_names']}")
        if n_ == HERO and c["sink"] < -0.051:
            problems.append(f"{n_}: sinks {c['sink']} below the ground")
    for k, g in contact[HERO]["seats"].items():
        if g is None or g > CONTACT:
            problems.append(f"{HERO}: seat {k} gap {g}")
    bury = {o.name: bury_report(o) for o in order}
    for n_, b in bury.items():
        if b["buried"]:
            problems.append(f"{n_}: buried {b['over_limit']} hidden {b['fully_hidden']}")
    pierce = pierce_report(h)
    if pierce:
        problems.append(f"{HERO}: edges passing through thin canvas / banner {pierce}")
    ropes = {o.name: rope_ends_report(o) for o in order if json.loads(o.get("m066_ropes", "[]"))}
    for n_, r in ropes.items():
        if r["loose"]:
            problems.append(f"{n_}: rope ends not touching {r['loose']}")
    walk = walk_report(h)
    if walk["min_clearance"] < 0.05:
        problems.append(f"{HERO}: walk proxy clearance {walk['min_clearance']} ({walk['worst_lane']})")
    if walk["canvas_under_min"] < 6.9:
        problems.append(f"{HERO}: canvas underside {walk['canvas_under_min']} under 6.9")
    place = placement_report(h)
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    for n_, t in thin.items():
        if t["min_deg"] < THIN_FLOOR:
            problems.append(f"{n_}: a face corner of {t['min_deg']} deg (floor {THIN_FLOOR})")
    winding = {o.name: sum(s["winding_errors"] for s in shells[o.name]) for o in order}
    bowties = {o.name: au["nonmanifold_verts"] for o, au in zip(order, audits)}
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
        if u.get("min_gap") is not None and u["min_gap"] < 0.0159:
            problems.append(f"{n_}: UV island gap {u['min_gap']} (margin 0.008)")
    stats = export_stats(order)
    if stats[HERO]["vfx_sockets"] != 1:
        problems.append(f"{HERO}: {stats[HERO]['vfx_sockets']} sockets (1 wanted)")
    if LANTERN_P in stats and stats[LANTERN_P]["vfx_sockets"] != 1:
        problems.append(f"{LANTERN_P}: {stats[LANTERN_P]['vfx_sockets']} sockets (1 wanted)")
    kinds = {}
    for s in shells[HERO]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts", "origin_offset", "transforms_applied")} for au in audits],
           "hero_shells": kinds, "contact": contact, "bury": bury, "rope_ends": ropes, "walk": walk,
           "placement": place, "winding": winding, "bowties": bowties, "thin": thin, "log": log, "geo": geo,
           "problems": problems, "uv": uv, "export_stats": stats, "pierce": pierce,
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "stored": {k: h.get(k) for k in ("m066_centre", "m066_seat_back", "m066_seat_front", "m066_seat_stool",
                                            "m066_lantern")},
           "stored_parts": {n_: objs[n_].get(k) for n_, k in ((LANTERN_P, "m066_hang"), (BANNER_P, "m066_hang"),
                                                              (POST_P, "m066_top")) if n_ in objs},
           "sockets": {o.name: [{"kind": c["vfx_kind"], "local": [round(x, 3) for x in c.location]}
                                for c in o.children if c.get("vfx_kind")] for o in order},
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders -------------------------------------------------------------------------------------------------------------
SHEET_LENS = 3.0
# f34_sheet: probed az -25 ... -45 x e 15 / 20 / 25 (spec 2.13, Stage 4 record); (-30, 15) gives the sheet's front
# edge : left edge ratio (about 2.3) and W : H 1.31 (sheet 1.33-1.37)
SHEET_VIEWS = {"front_sheet": (0, 3), "side_sheet": (90, 0), "rear_sheet": (180, 0), "f34_sheet": (-30, 15),
               "r34_sheet": (135, 20), "top_sheet": (0, 89.9)}
VIEW_NAMES = ("front34", "rear34", "front", "side", "rear", "top")
PARTS_SHOT = (-20, 15)
PART_SHOTS = {CANOPY_P: (-30, 35), BANNER_P: (-15, 8)}
SPIN = tuple(range(0, 360, 45))
SPIN_EL = 10


def _long_lens(kit):
    """(m033) render_group with a long lens and the studio floor hidden for the *_sheet shots."""
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


def render_close(objs, path, az, el, centre, radius, cell=(480, 400)):
    """(m033) A close-up from (az, el), framed on a sphere (centre, radius)."""
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


def _at(o, p):
    return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)


def _exploded(objs):
    """Linked copies of the parts laid out like the sheet's Exploded Construction: the ridge pole lifted over the
    canopy, the canopy over the furniture, a post at each side, lantern and banner to the right, crates, barrel and
    pegs below."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []
    x0 = objs[0].location.x + 50
    o0 = Matrix.Translation((x0, objs[0].location.y, 0))

    def put(tag, part, m):
        if part not in by:
            return
        c = bpy.data.objects.new(f"{PFX}expl_{tag}", by[part].data)
        coll.objects.link(c)
        c.matrix_world = o0 @ m
        shown.append(c)
    put("ridge", RIDGE_P, Matrix.Translation((1.5, 2.0, 11.0)) @ Matrix.Rotation(math.radians(70), 4, "Z"))
    put("canopy", CANOPY_P, Matrix.Translation((0.0, 0.5, 6.5)))
    put("post_l", POST_P, Matrix.Translation((-9.5, 0.0, 0.0)) @ Matrix.Diagonal((1, 1, 0.87, 1)))
    put("post_r", POST_P, Matrix.Translation((9.0, 2.0, 0.0)))
    put("lantern_l", LANTERN_P, Matrix.Translation((-7.0, -1.5, 8.0)))
    put("banner", BANNER_P, Matrix.Translation((12.5, -1.0, 4.0)))
    put("lantern_r", LANTERN_P, Matrix.Translation((7.0, -1.0, 7.0)))
    put("table", TABLE_P, Matrix.Translation((-1.0, 0.5, 0.0)))
    put("bench", BENCH_P, Matrix.Translation((1.5, -2.8, 0.0)))
    put("bench2", BENCH_P, Matrix.Translation((4.0, -6.0, 0.0)) @ Matrix.Diagonal((0.6, 1, 1, 1)))
    put("stool", STOOL_P, Matrix.Translation((6.2, -8.0, 0.0)))
    put("barrel", BARREL_P, Matrix.Translation((-9.0, -4.0, 0.0)))
    put("crate_l", CRATE_P, Matrix.Translation((-5.5, -6.5, 0.0)))
    put("crate_r", CRATE_P, Matrix.Translation((10.0, -4.5, 0.0)))
    put("peg", PEG_P, Matrix.Translation((-8.5, -9.0, 0.0)))
    bpy.context.view_layer.update()
    return shown


def _marker(h, at, name, proxy=False):
    """A 5.5-stud character stand-in (proxy: the spec 2.10 walk box, body 2 x 1 to 4.4, head 1.1 wide to 5.5)."""
    a = K.fk().Asset(PFX + name, "probe", seed=1, tint_var=0.0)
    if proxy:
        for hx, hy, z0, z1 in PROXY:
            _box(a, (-hx, -hy, z0), (hx, hy, z1), METAL, 0.8)
    else:
        a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=METAL, tint=0.7)
        a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=METAL, tint=0.7)
        a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=METAL, tint=0.7)
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


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    markers = [_marker(h, (-1.5, -6.6, 0.0), "char"), _marker(h, (0.0, 0.0, 0.0), "char2", proxy=True)]
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        for o in objs[1:]:
            extra["part_" + o.name.replace(HERO, "").lower()] = ([o], *PART_SHOTS.get(o.name, PARTS_SHOT))
        if shown:
            extra["exploded"] = (shown, -15, 18)
        extra["scale"] = ([h] + markers, -25, 8)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            sheet = M.views(NUM, [h], names=VIEW_NAMES, extra=extra, vfx=True)
            spin = render_spin(h)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet, "spin": spin}
        if close:
            out.update(render_close_ups(objs))
        return out
    finally:
        _remove(shown + markers)
        M.display(NUM, objs, TITLE)


def render_spin(h):
    """The eight-azimuth contact sheet: az 0, 45 ... 315 at e 10, long lens, floor hidden -> M066_spin.png."""
    kit = K.NS["KIT"]
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    old = kit["CELL"]
    kit["CELL"] = (420, 360)
    sc = bpy.context.scene
    try:
        kit["vfx"].clear(sc)
        kit["vfx"].realize(sc, [h])
        paths = [kit["render_group"]([h], f"{d}/spin{az:03d}_sheet.png", az, SPIN_EL) for az in SPIN]
    finally:
        kit["CELL"] = old
        kit["vfx"].clear(sc)
    rows = [kit["hstack"](paths[i:i + 4]) for i in (0, 4)]
    out = f"{d}/M066_spin.png"
    kit["save_px"](kit["vstack"](rows), out)
    return out


def render_cam(objs, path, loc, look, lens=18.0, cell=(560, 420), vfx=True):
    """(m064) A render from a fixed camera (loc looking at look)."""
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
    sc = bpy.context.scene
    try:
        if vfx:
            kit["vfx"].clear(sc)
            kit["vfx"].realize(sc, objs)
        return kit["render_group"](objs, path, 0, 10)
    finally:
        kit["frame_box"] = fb
        kit["CELL"] = old
        cam.data.lens = lens0
        if vfx:
            kit["vfx"].clear(sc)


def render_close_ups(objs):
    """junction_cu (close-up 1: the BR ridge junction from the front-left), base_cu (close-up 2: the FR base, collar
    and peg from the front-right), lantern_cu (the VFX panel), lash_cu (the FL lashing and its tab), underside_cu
    (close-up 3: from under the canopy looking up), walk (the 5.5 proxy in the lanes, front and side), thumb (the f34
    at about 140 px)."""
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    by = {o.name: o for o in objs}
    h = objs[0]
    out = {}
    rc = render_close
    kit = K.NS["KIT"]
    sc = bpy.context.scene
    kit["vfx"].clear(sc)
    kit["vfx"].realize(sc, [h])
    try:
        out["junction_cu"] = rc([h], f"{d}/junction_cu.png", -35, 12, _at(h, (5.9, 4.6, 10.8)), 1.5)
        out["junction_fr_cu"] = rc([h], f"{d}/junction_fr_cu.png", -30, 10, _at(h, (6.1, -4.9, 10.2)), 1.9)
        out["base_cu"] = rc([h], f"{d}/base_cu.png", 40, 15, _at(h, (7.1, -4.6, 0.9)), 1.3)
        out["lash_cu"] = rc([h], f"{d}/lash_cu.png", -25, 12, _at(h, (-6.2, -4.9, 8.75)), 1.3)
        out["lantern_cu"] = rc([h], f"{d}/lantern_cu.png", -10, 6, _at(h, (LAN_X, ROD_Y, 8.4)), 1.5)
    finally:
        kit["vfx"].clear(sc)
    out["underside_cu"] = render_cam([h], f"{d}/underside_cu.png", _at(h, (1.5, -3.4, 1.9)), _at(h, (3.5, 2.5, 9.0)),
                                     lens=14.0)
    lanes = [_marker(h, (x, y, 0.0), f"proxy{i}", proxy=True)
             for i, (x, y) in enumerate(((-2.0, -3.17), (0.2, -6.0), (-2.0, 3.97)))]
    try:
        old = kit["CELL"]
        kit["CELL"] = (420, 360)
        try:
            p1 = kit["render_group"]([h] + lanes, f"{d}/walk_front.png", 0, 4)
            p2 = kit["render_group"]([h] + lanes, f"{d}/walk_side.png", 90, 4)
            p3 = rc([h] + lanes, f"{d}/walk_f34.png", -35, 10, _at(h, (-1.0, -2.0, 4.0)), 6.0, cell=(420, 360))
        finally:
            kit["CELL"] = old
        path = f"{d}/walk.png"
        kit["save_px"](kit["hstack"]([p1, p2, p3]), path)
        out["walk"] = path
    finally:
        _remove(lanes)
    old = kit["CELL"]
    kit["CELL"] = (180, 150)
    try:
        orig, kit["render_group"] = _long_lens(kit)
        try:
            out["thumb"] = kit["render_group"]([h], f"{d}/thumb_sheet.png", *SHEET_VIEWS["f34_sheet"])
        finally:
            kit["render_group"] = orig
    finally:
        kit["CELL"] = old
    return out


def preview(names=("front_sheet", "side_sheet", "f34_sheet", "rear_sheet"), vfx=False, spin=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = _long_lens(kit)
    try:
        r = M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
        if spin:
            r = [r, render_spin(h)]
        return r
    finally:
        kit["render_group"] = orig


def hero_only():
    """Rebuild just the hero (tuning loop)."""
    M.coll(NUM, TITLE)
    palette()
    h, lg = _make(HERO, hero_all, "hero", HERO_BUDGET)
    _sockets(h)
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, _ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"hero": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                        "boundary_edges", "normals", "dup_verts")}, "log": lg,
            "geo": json.loads(json.dumps(GEO, default=lambda v: [round(x, 3) for x in v])),
            "offset": [round(x, 3) for x in h[OFF]]}
