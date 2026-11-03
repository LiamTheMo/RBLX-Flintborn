"""068 Timber Hut (references/068.png): a walk-in gable-roofed plank cabin with its dressing. A two-course plinth of
bevelled pale grey stone blocks with a two-tier block (grey under white) at each corner; a plank floor on it at 2.60
with a threshold through the doorway; walls of five rows of 0.40 planks (V seams from chamfered outer edges, staggered
butt joints) between four chamfered corner posts, a barred window with a light board frame in each long wall; the door
in the front gable between two tall door posts with golden foot caps, a lintel, a collar at eave level and the plank
door leaf standing open inward 95 deg; vertical gable boards; octagonal-ended wall plates that project past both
gables with iron bracket plates and golden pegs; rafters, purlins and a ridge beam under a cream canvas roof of two
closed slabs (5 x 2 sagging panels per slope, the +X slope cut round the chimney); crossed bargeboards with a golden
saddle at each gable and the ridge beam's banded end below them; golden U ties along both eaves; a square stone
chimney in two blocks with a flued cap; two-tread stairs (three equal 0.87 risers); three Neon lanterns (one on an
iron eave bracket, two on wall brackets flanking the door); a red swallowtail banner with a white diamond on a pole
with an X-lashed crossarm; two hooped barrels, an X-braced crate and two pale stones.

    import importlib, kit_models, m068; importlib.reload(kit_models); importlib.reload(m068); m068.build()

Build frame: studs, front -Y (the door gable), +X right, ground z 0, the walls' rectangle centred on x 0, y 0, ridge
along Y. Every object ends with its origin at its bbox bottom centre; o["m068_offset"] is that origin in the build
frame. Names (spec 8, decisions 9-10):
- TimberCabin (hero): everything above, one object of closed shells (no booleans). Collision precise.
- Parts: TimberCabinRoofPanel, ...RidgeBeam, ...Chimney, ...Banner, ...Lantern, ...WallPanel, ...WindowWall,
  ...DoorFrame (leaf closed, hinge stored), ...GableFrame, ...Floor, ...Stairs, ...Foundation.
The hero is assembled from the same part functions. Colour (stage 4) is painted by role and by position inside the
builders, never by facing. Stages 5-6: the lantern glass is m068_glow at emission 1.0 (Neon), one heat_glow socket per
lantern and a thin pale chimney_smoke socket at the flue. See M068_spec.md. Geometry helpers are copied from the
m064 / m066 builders (not imported) so this builder stands alone.
"""
import json
import math
import random
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M

NUM, TITLE, SHEET = 68, "Timber Hut", "M068"
OFF = "m068_offset"
PFX = "_m068_"
HERO = "TimberCabin"
ROOF_P, RIDGE_P, CHIMNEY_P = "TimberCabinRoofPanel", "TimberCabinRidgeBeam", "TimberCabinChimney"
BANNER_P, LANTERN_P, WALL_P = "TimberCabinBanner", "TimberCabinLantern", "TimberCabinWallPanel"
WINDOW_P, DOOR_P, GABLE_P = "TimberCabinWindowWall", "TimberCabinDoorFrame", "TimberCabinGableFrame"
FLOOR_P, STAIRS_P, FOUND_P = "TimberCabinFloor", "TimberCabinStairs", "TimberCabinFoundation"

TIMBER, TIMBER_END, TIMBER_DEEP = "m068_timber", "m068_timber_end", "m068_timber_deep"
CANVAS, CANVAS_DEEP = "m068_canvas", "m068_canvas_deep"
STONE, STONE_LIGHT, STONE_DARK, SOOT = "m068_stone", "m068_stone_light", "m068_stone_dark", "m068_soot"
IRON, GLOW, ROPE, ROPE_DEEP = "m068_iron", "m068_glow", "m068_rope", "m068_rope_deep"
BANNER, WHITE = "m068_banner", "m068_cloth_white"
NEON = 1.0

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
BURY = 0.05

# key -> (hex, roughness, metal, emission, low specular). Stage 4: sampled on the sheet (spec 5.1-5.2), run through
# K.calibrate on the studio dome, then re-measured on the hero renders against the same regions of the sheet.
PALETTE = {
    TIMBER: ("#9E5A2B", 0.85, 0.0, 0.0, True),
    TIMBER_END: ("#C08024", 0.8, 0.0, 0.0, True),
    TIMBER_DEEP: ("#653516", 0.9, 0.0, 0.0, True),
    CANVAS: ("#EADEBF", 0.95, 0.0, 0.0, True),
    CANVAS_DEEP: ("#BAA58F", 0.95, 0.0, 0.0, True),
    STONE: ("#969295", 0.9, 0.0, 0.0, True),
    STONE_LIGHT: ("#A39A9A", 0.9, 0.0, 0.0, True),
    STONE_DARK: ("#5E5C60", 0.9, 0.0, 0.0, True),
    SOOT: ("#2A2425", 1.0, 0.0, 0.0, True),
    IRON: ("#534E52", 0.55, 0.4, 0.0, False),
    GLOW: ("#EEB406", 0.5, 0.0, NEON, False),
    ROPE: ("#F2C45E", 0.95, 0.0, 0.0, True),
    ROPE_DEEP: ("#93712E", 0.95, 0.0, 0.0, True),
    BANNER: ("#C2191C", 0.9, 0.0, 0.0, True),
    WHITE: ("#F0EAE4", 0.9, 0.0, 0.0, True),
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions) and K.sample kinds ("all" = paper filtered)
TARGETS = {TIMBER: ((0xAB, 0x5C, 0x2A), "brown"), TIMBER_END: ((0xF9, 0xA5, 0x28), "vivid"),
           TIMBER_DEEP: ((0x7A, 0x3A, 0x16), "brown"), CANVAS: ((0xFE, 0xF0, 0xC9), "all"),
           CANVAS_DEEP: ((0xE6, 0xC8, 0xA2), "all"), STONE: ((0xA6, 0xA1, 0xA5), "all"),
           STONE_LIGHT: ((0xC4, 0xB6, 0xB2), "all"), STONE_DARK: ((0x6C, 0x6A, 0x70), "all"),
           SOOT: ((0x2A, 0x24, 0x25), "all"), IRON: ((0x58, 0x52, 0x55), "all"),
           GLOW: ((0xFB, 0xBD, 0x0A), "vivid"), ROPE: ((0xF4, 0xBD, 0x51), "vivid"),
           ROPE_DEEP: ((0xB8, 0x86, 0x2E), "brown"), BANNER: ((0xD7, 0x1A, 0x1E), "vivid"),
           WHITE: ((0xF6, 0xF0, 0xEA), "all")}


def _glow_mats():
    """Blender preview of the Neon key as Roblox shows Neon: its own colour, unshaded (m009)."""
    for mat in bpy.data.materials:
        if not (mat.name.startswith("FB_m068_glow") and mat.node_tree):
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
        key = m.name[3:] if m.name.startswith("FB_m068_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in (f"m068_{tail}", f"{k1}_{tail}") if k in PALETTE), None)
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
    """(m051) A convex faceted hull of points. Returns (verts, faces)."""
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
    return vs, fs


HEXA = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (0, 4, 7, 3), (1, 2, 6, 5)]


def _box_pts(lo, hi, m=None):
    pts = [Vector((x, y, z)) for z in (lo[2], hi[2]) for (x, y) in ((lo[0], lo[1]), (hi[0], lo[1]),
                                                                   (hi[0], hi[1]), (lo[0], hi[1]))]
    return [m @ p for p in pts] if m is not None else pts


def _box(a, lo, hi, key, tint=1.0, m=None):
    """Axis box lo..hi (optionally transformed by the 4x4 matrix m). Returns (verts, faces) in HEXA order (bottom,
    top, -y, +y, -x, +x for an untransformed box)."""
    return _shell(a, _box_pts(lo, hi, m), HEXA, key, tint)


def _prism(a, rings, key, tint=1.0, caps=(True, True)):
    """A closed prism / loft through rings of n points each. Returns (verts, faces, bands): bands[i] are the faces
    between ring i and i + 1; the caps (ring 0, last ring) are the last two faces."""
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


def _earclip(P):
    """Triangles (index triples, counter-clockwise) of a simple 2D polygon."""
    n = len(P)
    area = sum(P[i][0] * P[(i + 1) % n][1] - P[(i + 1) % n][0] * P[i][1] for i in range(n))
    idx = list(range(n)) if area > 0 else list(reversed(range(n)))

    def cross(o, p, q):
        return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])

    def inside(p, a_, b_, c_):
        if cross(a_, b_, p) > 1e-12 and cross(b_, c_, p) > 1e-12 and cross(c_, a_, p) > 1e-12:
            return True
        # a vertex lying on the new diagonal c_ -> a_ would leave a T-junction (and later a zero-area triangle)
        if abs(cross(c_, a_, p)) <= 1e-9:
            t = ((p[0] - c_[0]) * (a_[0] - c_[0]) + (p[1] - c_[1]) * (a_[1] - c_[1]))
            L2 = (a_[0] - c_[0]) ** 2 + (a_[1] - c_[1]) ** 2
            return 1e-9 < t < L2 - 1e-9
        return False
    tris = []
    guard = 0
    while len(idx) > 3 and guard < 4 * n * n:
        guard += 1
        m = len(idx)
        cut, best = None, -1.0
        for k in range(m):           # every valid ear; keep the one with the largest smallest corner (no slivers)
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % m]
            if cross(P[i0], P[i1], P[i2]) <= 1e-12:
                continue
            if any(inside(P[j], P[i0], P[i1], P[i2]) for j in idx if j not in (i0, i1, i2)):
                continue
            q = _min_angle([Vector((P[i][0], P[i][1], 0.0)) for i in (i0, i1, i2)])
            if q > best:
                cut, best = k, q
        if cut is None:          # only collinear corners left: drop one
            cut = 0
        k = cut
        tris.append((idx[k - 1], idx[k], idx[(k + 1) % m]))
        idx.pop(k)
    tris.append(tuple(idx))
    return [t for t in tris if len(set(t)) == 3]


def _ext(a, poly, to3, w0, w1, key, tint=1.0, cap_key=None, side_keys=None):
    """A closed prism of a simple 2D polygon (u, v) between w0 and w1; to3(u, v, w) -> Vector. Caps ear-clipped.
    Returns (verts, faces, cap faces, side faces)."""
    n = len(poly)
    pts = [to3(u, v, w0) for u, v in poly] + [to3(u, v, w1) for u, v in poly]
    faces, keys = [], []
    if n > 4:
        tris = _earclip(poly)
        faces += [list(t) for t in tris] + [[n + t[2], n + t[1], n + t[0]] for t in tris]
    else:
        faces += [list(range(n)), [n + i for i in reversed(range(n))]]
    ncap = len(faces)
    keys += [cap_key or key] * ncap
    for i in range(n):
        i1 = (i + 1) % n
        faces.append([i, i1, n + i1, n + i])
        keys.append(side_keys[i] if side_keys else key)
    vs, fs = _shell(a, pts, faces, key, tint)
    for f, k in zip(fs, keys):
        if k != key:
            f.material_index = a._mi(k)
    return vs, fs, fs[:ncap], fs[ncap:]


def _tube(a, path, r, sides, closed, key, groove=None, tint=1.0, up=(0, 0, 1), phase=0.0, twist=False):
    """(m048) A low-poly rope tube along `path`: rings of `sides` verts. twist=True: each ring turned half a side and
    joined as an antiprism strip (strand = side); twist=False: rings aligned. Bends are mitred so the tube keeps its
    thickness. Open tubes get flat end caps. `groove` = {strand: key}: those strands take that key (never by
    facing). Closed twisted paths need an even number of points."""
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
ROPES = []           # open rope runs and straps: name, end points, radius (both-ends contact check)
GEO = {}             # measured placements (report)
FX = []              # (kind, build-frame point, overrides) for the hero's sockets
PART_INFO = {}


def _reg(kind, name, vs):
    PIECES.append((kind, name, sum((v.co for v in vs), Vector()) / len(vs)))


def _clear():
    PIECES.clear()
    ROPES.clear()


def _groove(sides):
    """Strand roles by index round the twist (never by facing): one strand in four rope_deep; on 3-ply rope one
    strand half way to rope_deep."""
    return {0: ROPE_DEEP} if sides >= 4 else {0: _mix(ROPE, ROPE_DEEP, 0.5)}


def rope(a, path, rt, sides, closed, name, up=None, kind="rope", twist=True):
    path = [Vector(p) for p in path]
    up = up if up is not None else _up_for(path)
    groove = _groove(sides) if twist else {0: ROPE_DEEP, sides // 2: _mix(ROPE, ROPE_DEEP, 0.5)}
    vs, fs = _tube(a, path, rt, sides, closed, ROPE, groove=groove, tint=_rt(name, 0.03), up=tuple(up),
                   twist=twist, phase=0.0 if twist else math.pi / sides)
    _reg(kind, name, vs)
    if not closed:
        ROPES.append({"name": name, "ends": [list(path[0]), list(path[-1])], "rt": rt})
    return vs


# ---- the frame of the hut (spec 2) -------------------------------------------------------------------------------------
PITCH = 32.0                      # spec 2.6 asks 34 +- 3: at 34 the canvas line passes through the 11.20 plates
P = math.tan(math.radians(PITCH))
COS, SIN = math.cos(math.radians(PITCH)), math.sin(math.radians(PITCH))
RIDGE_Z = 16.00                   # canvas top at the apex
CT = 0.12                         # canvas thickness (perpendicular)
CTV = CT / COS                    # ... vertical
EAVE = 7.45                       # canvas eave edge |x|: 0.25 past the plates' outer faces, at plate-top height
CAN_Y = 9.247                     # canvas gable ends |y| (0.003 inside the bargeboards' inner faces)
FLOOR_Z = 2.60
# |y| end 10.80 (round-1 minor 3): the octagonal end, iron plate and peg stand clear of the bargeboard heel (10.15)
PLATE = (6.30, 7.20, 10.40, 11.20, 10.80, 0.12)   # x0, x1, z0, z1, |y| end, chamfer
OVL = 0.002                                      # closed joints (round-1 fix): neighbours sink this far into each
                                                 # other, so no seam goes through and no verts coincide
EAVE_BLK = (6.85, 7.08)                          # eave blocking on the plate top (x range; the canvas is unsagged
                                                 # over it), closing the slit between plate and canvas
WALL_IN_X, WALL_IN_Y = 6.60, 7.60                # long / end walls' inner faces
WALL_T = 0.40
ROW_PITCH, ROW_Z0, N_ROWS = 1.62, 2.30, 5
POST = (6.10, 7.20, 7.10, 8.20)                  # corner post |x| and |y| ranges
CORNER_BLOCK = (6.11, 7.75, 7.11, 8.75, 1.30, 2.60)
DOOR_X = 1.80                                    # door clear half width (3.60)
DOOR_TOP = 9.60
DPOST = (1.80, 2.90, -9.50, -8.405)              # door post |x| range, y range
BB_Y = (9.25, 10.15)                             # bargeboards |y|
BB_D = 0.92                                      # bargeboard depth (perpendicular): 0.12 under, 0.80 over the canvas
RAFTER_Y = (-5.82, -1.94, 1.94, 5.82)
RAFTER_W, RAFTER_D = 0.50, 0.60
RIDGE_W, RIDGE_END, RIDGE_Z0 = 1.00, 10.75, 14.536
PURLIN_X, PURLIN_W, PURLIN_H = 4.10, 0.50, 0.50
SINK_TOP = 0.015                                 # rafter / purlin tops under the canvas underside (its sag is 0.01 there)
CHIMNEY = (2.20, -3.50)                          # chimney centre (f34, decision 4; y 0.10 back so its +Y face
                                                 # clears the rafter at y -1.94 by 0.01)
CH_W, CH_Z0, CH_JOINT, CH_Z1, CH_TOP = 2.60, 13.60, 16.60, 18.60, 19.40
# canvas cut round the chimney, OVL clear (round-1 fix: the 0.03 ring let light in; a flashing collar on the canvas
# now covers the cut, chimney())
HOLE = (CHIMNEY[0] - CH_W / 2 - OVL, CHIMNEY[0] + CH_W / 2 + OVL, CHIMNEY[1] - CH_W / 2 - OVL,
        CHIMNEY[1] + CH_W / 2 + OVL)
COLLAR = (0.12, 0.10)                            # flashing collar width past the stack, height over the canvas


def zt(x):
    """Canvas top (unsagged) at x."""
    return RIDGE_Z - P * abs(x)


def zu(x):
    """Canvas underside (unsagged) at x."""
    return zt(x) - CTV


def row_z(i):
    """Wall plank row i (0..4): bottom, top. Neighbouring rows overlap 2 * OVL at the back (round-1 fix: no seam
    goes through; the 0.10 outer chamfers still draw the dark V seam); the bottom row 0.003 off the plinth, the top
    row OVL into the plate (end walls: under the gable boards)."""
    z0 = ROW_Z0 + ROW_PITCH * i + (0.003 if i == 0 else -OVL)
    return z0, ROW_Z0 + ROW_PITCH * (i + 1) + OVL


def _jit_face(name):
    """A plank's outer face offset (0.37-0.40 thick): hand-made, only ever inward so mounted pieces always touch."""
    return WALL_T - random.Random(_seed(name) + 3).uniform(0.0, 0.03)


# ---- foundation (spec 2.2) ----------------------------------------------------------------------------------------------
COURSES = ((0.0, 1.10), (1.103, 2.30))
RUNS = {"R": (-7.08, 7.08, 7), "L": (-7.08, 7.08, 7), "F": (-6.08, 6.08, 6), "B": (-6.08, 6.08, 6)}
RUN_SEED = {"R": 6801, "L": 6802, "F": 6803, "B": 6804}


def _run_map(side):
    """(along, depth from the inner face, z) -> Vector for a foundation run."""
    if side == "R":
        return lambda t, d, z: Vector((6.40 + d, t, z))
    if side == "L":
        return lambda t, d, z: Vector((-6.40 - d, t, z))
    if side == "F":
        return lambda t, d, z: Vector((t, -7.40 - d, z))
    return lambda t, d, z: Vector((t, 7.40 + d, z))


def _split(a0, a1, n, rng, gap=0.06):
    """n block extents over [a0, a1] with gaps, lengths varying (no two neighbours equal)."""
    w = [rng.uniform(0.78, 1.25) for _ in range(n)]
    L = a1 - a0 - gap * (n - 1)
    s = sum(w)
    out, t = [], a0
    for x in w:
        ln = L * x / s
        out.append((t, t + ln))
        t += ln + gap
    out[-1] = (out[-1][0], a1)
    return out


def _course_joints(side):
    a0, a1, n = RUNS[side]
    rng = random.Random(RUN_SEED[side])
    lower = _split(a0, a1, n, rng)
    jl = [b for _, b in lower[:-1]]
    for k in range(60):
        r2 = random.Random(RUN_SEED[side] * 31 + k)
        upper = _split(a0, a1, n, r2)
        ju = [b for _, b in upper[:-1]]
        if min(abs(x - y) for x in ju for y in jl) > 0.40:
            return lower, upper
    return lower, upper


def block(a, side, t0, t1, z0, z1, name, broken=0, key=STONE):
    """One plinth block: an axis box (1.00 deep) with its outer top edge chamfered 0.10; a broken corner (broken = -1
    or +1: that end's chamfer opens to 0.32). A convex hull: 16 tris."""
    mp = _run_map(side)
    pts = []
    for e, t in ((-1, t0), (1, t1)):
        ch = 0.32 if broken == e else 0.10
        pts += [mp(t, 0.0, z0), mp(t, 1.0, z0), mp(t, 0.0, z1), mp(t, 1.0 - ch, z1), mp(t, 1.0, z1 - ch)]
    vs, fs = _hull(a, pts, key, _rt(name, 0.04))
    _texture(a, vs, 0.03, _seed(name), scale=0.8)
    _reg("stone", name, vs)
    return vs


def foundation_run(a, side):
    """Spec 2.2: one side's two courses of bevelled blocks between the corner blocks, joints offset course to course,
    one broken corner per course; the lower course one step toward stone_dark (ground grime, by course)."""
    lower, upper = _course_joints(side)
    rng = random.Random(RUN_SEED[side] + 5)
    for ci, (blocks, (z0, z1)) in enumerate(((lower, COURSES[0]), (upper, COURSES[1]))):
        bk = rng.randrange(len(blocks))
        key = _mix(STONE, STONE_DARK, 0.25) if ci == 0 else STONE
        for i, (t0, t1) in enumerate(blocks):
            block(a, side, t0, t1, z0, z1, f"blk_{side}{ci}_{i}", broken=(rng.choice((-1, 1)) if i == bk else 0),
                  key=key)


def corner_block(a, sx, sy):
    """Spec 2.2, close-up B: a grey lower tier under a white upper tier with bevelled top edges and one broken outer
    corner, under the corner post, proud of the course by 0.35."""
    x0, x1, y0, y1, zs, ztop = CORNER_BLOCK
    tag = f"{'L' if sx < 0 else 'R'}{'F' if sy < 0 else 'B'}"
    lo = (min(sx * x0, sx * x1), min(sy * y0, sy * y1), 0.0)
    hi = (max(sx * x0, sx * x1), max(sy * y0, sy * y1), zs)
    vs, _ = _box(a, lo, hi, _mix(STONE, STONE_DARK, 0.25), _rt(f"cbl{tag}", 0.04))
    _texture(a, vs, 0.03, _seed(f"cbl{tag}"), scale=0.8)
    _reg("corner", f"corner_{tag}_low", vs)
    bv = 0.12
    z0 = zs + 0.003
    pts = []
    for cx, cy in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        outer = cx == x1 and cy == y1
        X, Y = sx * cx, sy * cy
        ix, iy = sx * (cx - bv if cx == x1 else cx + bv), sy * (cy - bv if cy == y1 else cy + bv)
        pts.append(Vector((X, Y, z0)))
        if outer:      # the broken corner
            pts += [Vector((X, Y, ztop - 0.48)), Vector((sx * (cx - 0.42), Y, ztop - bv)),
                    Vector((X, sy * (cy - 0.42), ztop - bv)), Vector((sx * (cx - 0.42), sy * (cy - 0.42), ztop))]
        else:
            pts += [Vector((X, Y, ztop - bv)), Vector((ix, iy, ztop))]
    vs, _ = _hull(a, pts, STONE_LIGHT, _rt(f"cbu{tag}", 0.03))
    _texture(a, vs, 0.03, _seed(f"cbu{tag}"), scale=0.8)
    _reg("corner", f"corner_{tag}_top", vs)


# ---- floor (spec 2.3) ----------------------------------------------------------------------------------------------------
FLOOR_W, FLOOR_GAP, FLOOR_N = 1.26, 0.06, 10
THRESH = ((-1.78, -0.62), (-0.58, 0.58), (0.62, 1.78))


UNDER = (5.40, WALL_IN_Y - 0.20 + OVL, 2.20)     # underlay half x, half y (into the end courses), bottom z


def floor(a, feet=False):
    """Ten deck planks along Y (1.26 wide, 0.06 seams) on the front and back courses; the three threshold planks run
    out through the doorway onto the threshold beam between the door posts. Round-1 fix (no ground seen from
    inside): the planks run OVL into the walls' inner faces; the two outer planks are notched round the corner posts
    and blocks (they cover the corners down to the posts' faces); a dark underlay board under the seams (into the
    end courses' inner faces) shows in them as the dark gap and stops every ray; the threshold planks run OVL onto
    the deck. The underlay rests on two hidden sleepers; feet: the Floor part's short dark feet (the exploded)
    instead of the sleepers."""
    x0 = -(FLOOR_N * FLOOR_W + (FLOOR_N - 1) * FLOOR_GAP) / 2
    ye = WALL_IN_Y + OVL
    cx, cy = CORNER_BLOCK[0] + OVL, CORNER_BLOCK[2] + OVL       # notch corner (just over the block's inner faces)
    for i in range(FLOOR_N):
        xa = x0 + i * (FLOOR_W + FLOOR_GAP)
        xb = xa + FLOOR_W
        nm = f"deck_{i}"
        if i in (0, FLOOR_N - 1):
            s = -1 if i == 0 else 1
            xi, xo = (xb, xa) if s < 0 else (xa, xb)
            xo = s * (WALL_IN_X + OVL)
            poly = [(xi, -ye), (s * cx, -ye), (s * cx, -cy), (xo, -cy), (xo, cy), (s * cx, cy), (s * cx, ye), (xi, ye)]
            vs, _, _, _ = _ext(a, poly, lambda u, v, w: Vector((u, v, w)), 2.300 - OVL, FLOOR_Z, TIMBER,
                               _rt(nm, 0.05))
        else:            # bottoms OVL into the underlay and courses (seated, and the contact check sees it)
            vs, _ = _box(a, (xa, -ye, 2.300 - OVL), (xb, ye, FLOOR_Z), TIMBER, _rt(nm, 0.05))
        _texture(a, vs, 0.03, _seed(nm), scale=0.35)
        _reg("plank", nm, vs)
    for i, (xa, xb) in enumerate(THRESH):
        nm = f"thresh_{i}"
        vs, _ = _box(a, (xa, DPOST[2], 2.303), (xb, -WALL_IN_Y + OVL, FLOOR_Z), TIMBER, _rt(nm, 0.05))
        _reg("plank", nm, vs)
    vs, _ = _box(a, (-DOOR_X + 0.015, -9.48, 1.70 if feet else 1.733), (DOOR_X - 0.015, -8.405, 2.297), TIMBER_DEEP,
                 0.97)
    _reg("beam", "thresh_beam", vs)
    ux, uy, uz = UNDER
    vs, _ = _box(a, (-ux, -uy, uz), (ux, uy, 2.300), _mix(TIMBER_DEEP, SOOT, 0.4), 0.97)
    _reg("board", "floor_under", vs)
    if feet:                 # the Floor part: two short dark feet under every deck plank (the exploded's feet)
        for i in range(FLOOR_N):
            xc = x0 + i * (FLOOR_W + FLOOR_GAP) + FLOOR_W / 2
            ztop = uz - 0.003 if abs(xc) + 0.30 < ux else 2.297
            for k, y in enumerate((-5.0, 5.0)):
                vs, _ = _box(a, (xc - 0.30, y - 0.30, 1.70), (xc + 0.30, y + 0.30, ztop), TIMBER_DEEP,
                             _rt(f"ft{i}{k}", 0.04))
                _reg("beam", f"floor_foot{i}_{k}", vs)
    else:
        for i, y in enumerate((-3.5, 3.5)):
            vs, _ = _box(a, (-6.395, y - 0.5, 1.70), (6.395, y + 0.5, uz - 0.003), TIMBER_DEEP, 0.95)
            _reg("beam", f"sleeper_{i}", vs)


# ---- walls (spec 2.4) ----------------------------------------------------------------------------------------------------
# butt joints (staggered y -2.60 / +3.40, back x -2.00 / +2.60): the two plank ends overlap 2 * OVL (round-1 fix)
LONG_SEGS = {0: [(-7.10, -2.60 + OVL), (-2.60 - OVL, 7.10)], 1: [(-7.10, 3.40 + OVL), (3.40 - OVL, 7.10)],
             2: [(-7.10, -2.60 + OVL), (-2.60 - OVL, -1.50), (1.50, 7.10)],
             3: [(-7.10, -1.50), (1.50, 3.40 + OVL), (3.40 - OVL, 7.10)],
             4: [(-7.10, -2.60 + OVL), (-2.60 - OVL, 7.10)]}
BACK_SEGS = {i: ([(-6.10, -2.00 + OVL), (-2.00 - OVL, 6.10)] if i % 2 == 0 else
                 [(-6.10, 2.60 + OVL), (2.60 - OVL, 6.10)]) for i in range(N_ROWS)}
FRONT_SEGS = {i: [(-6.10, -DOOR_X), (DOOR_X, 6.10)] for i in range(N_ROWS)}
PLANK_CH = 0.10                  # outer edge chamfers: the dark V seams between rows (sheet)


def _wall_map(wall, s, z0):
    if wall == "long":
        return lambda u, v, t: Vector((s * (WALL_IN_X + u), t, z0 + v))
    return lambda u, v, t: Vector((t, s * (WALL_IN_Y + u), z0 + v))


def plank(a, wall, s, t0, t1, z0, z1, name, band=True):
    """One wall plank (spec 2.4): a 6-sided section 0.37-0.40 thick with its outer top and bottom edges chamfered
    0.10 (neighbouring rows touch at the back, so the chamfers make the dark V seams and nothing is see-through).
    Planks over 2.0 long get a ring 30 % from a seeded end: that end band one step toward timber_deep (by position).
    20 tris (32 with the band)."""
    rng = random.Random(_seed(name))
    uo = _jit_face(name)
    H = z1 - z0
    c = PLANK_CH
    sec = [(0.0, 0.0), (uo - c, 0.0), (uo, c), (uo, H - c), (uo - c, H), (0.0, H)]
    mp = _wall_map(wall, s, z0)
    ts, bk = [t0, t1], None
    if band and t1 - t0 > 2.0:
        f = 0.30 * (t1 - t0)
        if rng.random() < 0.5:
            ts, bk = [t0, t0 + f, t1], 0
        else:
            ts, bk = [t0, t1 - f, t1], 1
    rings = [[mp(u, v, t) for u, v in sec] for t in ts]
    vs, fs, bands = _prism(a, rings, TIMBER, _rt(name, 0.05))
    if bk is not None:
        deep = _mix(TIMBER, TIMBER_DEEP, 0.25)
        _paint(a, bands[bk] + [fs[-2] if bk == 0 else fs[-1]], deep)
    _texture(a, vs, 0.025, _seed(name), scale=0.5)
    _reg("plank", name, vs)
    return vs


def wall_long(a, s, window=True):
    """A long wall (s = -1: -X, +1: +X): five rows between the corner posts' inner faces, one staggered butt joint
    per row, rows 3-4 cut by the centred window opening (y -1.50 .. 1.50, z 5.54 .. 8.78)."""
    tag = "L" if s < 0 else "R"
    for i in range(N_ROWS):
        z0, z1 = row_z(i)
        segs = LONG_SEGS[i] if window else [LONG_SEGS[0][0], LONG_SEGS[0][1]] if i % 2 == 0 else LONG_SEGS[1]
        for k, (t0, t1) in enumerate(segs):
            plank(a, "long", s, t0, t1, z0, z1, f"pl_{tag}{i}_{k}")


def wall_end(a, s, door=False):
    """An end wall (s = -1: front, +1: back): five rows between the posts; at the front the rows stop at the door
    jambs (x +-1.80)."""
    tag = "F" if s < 0 else "B"
    segs = FRONT_SEGS if door else BACK_SEGS
    for i in range(N_ROWS):
        z0, z1 = row_z(i)
        for k, (t0, t1) in enumerate(segs[i]):
            plank(a, "end", s, t0, t1, z0, z1, f"pl_{tag}{i}_{k}")


WIN = (1.50, 5.54, 8.78, 0.50, 0.20)          # opening half width, bottom, top; frame board width, proud


def window(a, s):
    """The barred window frame (spec 2.4): jambs, head and a sill (0.25 past the jambs, 0.30 out) of light boards
    0.20 proud on the outer face, two 0.22 iron bars standing in the opening on the plank below."""
    tag = "L" if s < 0 else "R"
    hw, zb, ztp, bw, pr = WIN
    xo = WALL_IN_X + WALL_T + 0.003
    key = _mix(TIMBER, TIMBER_END, 0.3)

    def bx(y0, y1, z0, z1, out, nm):
        lo = (min(s * xo, s * (xo + out)), y0, z0)
        hi = (max(s * xo, s * (xo + out)), y1, z1)
        vs, _ = _box(a, lo, hi, key, _rt(nm, 0.04))
        _reg("frame", nm, vs)
    bx(-hw - bw, hw + bw, ztp + 0.003, ztp + bw, pr, f"win_{tag}_head")
    bx(-hw - bw - 0.25, hw + bw + 0.25, zb - bw, zb - 0.003, pr + 0.10, f"win_{tag}_sill")
    for e in (-1, 1):
        y0, y1 = sorted((e * hw, e * (hw + bw)))
        bx(y0, y1, zb, ztp, pr, f"win_{tag}_jamb{e}")
    xc = s * (WALL_IN_X + 0.20)
    for e in (-1, 1):
        vs, _ = _box(a, (xc - 0.11, e * 0.50 - 0.11, row_z(1)[1] + 0.002), (xc + 0.11, e * 0.50 + 0.11, row_z(4)[0] - 0.002),
                     IRON, _rt(f"bar{tag}{e}", 0.03))
        _reg("bar", f"win_{tag}_bar{e}", vs)
    shutter(a, s)


SHUT = (0.20, 0.12, 0.14, 0.01)              # overlap round the opening, leaf thicknesses, second leaf set-back


def shutter(a, s):
    """Round-1 fix (minor 1): a closed inner shutter of two dark board leaves against the planks' inner face, 0.20
    past the opening all round, so the window reads dark (the sheet's #201717) and square-on views no longer look
    through the hut. The leaves overlap 2 * OVL where they meet; the second is set 0.01 back and is thicker, so no
    two faces are coplanar."""
    tag = "L" if s < 0 else "R"
    hw, zb, ztp = WIN[0], WIN[1], WIN[2]
    m, t_side, t_mid, back = SHUT
    xo = WALL_IN_X - 0.003
    y0, y1 = -hw - m, hw + m
    w = (y1 - y0) / 2
    key = _mix(TIMBER_DEEP, SOOT, 0.55)
    for i in range(2):
        ya, yb = y0 + i * w - (OVL if i else 0.0), y0 + (i + 1) * w + (OVL if i < 1 else 0.0)
        xa, xb = (xo - back - t_mid, xo - back) if i == 1 else (xo - t_side, xo)
        nm = f"shutter_{tag}{i}"
        lo, hi = (min(s * xa, s * xb), ya, zb - m), (max(s * xa, s * xb), yb, ztp + m)
        vs, _ = _box(a, lo, hi, key, _rt(nm, 0.05))
        _texture(a, vs, 0.03, _seed(nm), scale=0.5)
        _reg("board", nm, vs)


def _oct_rect(x0, x1, y0, y1, ch):
    return [(x0 + ch, y0), (x1 - ch, y0), (x1, y0 + ch), (x1, y1 - ch), (x1 - ch, y1), (x0 + ch, y1), (x0, y1 - ch),
            (x0, y0 + ch)]


def post(a, x0, x1, y0, y1, z0, z1, name, ch=0.06, foot=0.40, end_key=TIMBER_END):
    """A chamfered square post (8-sided prism): a ring `foot` above its base (the weathered foot one step toward
    timber_deep, by height), pale golden end faces (by role)."""
    rings = [[Vector((x, y, z)) for x, y in _oct_rect(x0, x1, y0, y1, ch)] for z in (z0, z0 + foot, z1)]
    vs, fs, bands = _prism(a, rings, TIMBER, _rt(name, 0.05))
    _paint(a, bands[0], _mix(TIMBER, TIMBER_DEEP, 0.25))
    _paint(a, fs[-2:], end_key)
    _texture(a, vs, 0.03, _seed(name), scale=0.45)
    _reg("post", name, vs)
    return vs


def corner_post(a, sx, sy):
    x0, x1, y0, y1 = POST
    tag = f"{'L' if sx < 0 else 'R'}{'F' if sy < 0 else 'B'}"
    xs, ys = sorted((sx * x0, sx * x1)), sorted((sy * y0, sy * y1))
    # OVL into the corner block and the plate (round-1 fix: no slit under the foot or over the top)
    post(a, xs[0], xs[1], ys[0], ys[1], CORNER_BLOCK[5] - OVL, PLATE[2] + OVL, f"post_{tag}")


# ---- roof frame (spec 2.6) ---------------------------------------------------------------------------------------------
def plate(a, s, y_end=None):
    """A wall plate / eave beam (0.90 x 0.80, chamfered 0.12: octagonal pale end faces, close-up A) along Y over the
    long wall, projecting past both gables under the bargeboards."""
    x0, x1, z0, z1, ye, ch = PLATE
    ye = y_end or ye
    oc = _oct_rect(x0, x1, z0, z1, ch)
    tag = "L" if s < 0 else "R"
    vs, fs, caps, sides = _ext(a, oc, lambda u, v, w: Vector((s * u, w, v)), -ye, ye, TIMBER, _rt(f"plate{tag}", 0.04),
                               cap_key=TIMBER_END)
    _texture(a, vs, 0.03, _seed(f"plate{tag}"), scale=0.4)
    _reg("beam", f"plate_{tag}", vs)
    return vs


def bracket_plate(a, sx, e):
    """Close-up A: a dark iron plate with two rivets on the plate's outer face 0.7 in from its end, a golden square
    peg on it."""
    tag = f"{'L' if sx < 0 else 'R'}{'F' if e < 0 else 'B'}"
    yc = e * (PLATE[4] - 0.70)
    x0 = PLATE[1] + 0.005

    def bx(xa, xb, y0, y1, z0, z1, key, kind, nm):
        lo = (min(sx * xa, sx * xb), y0, z0)
        hi = (max(sx * xa, sx * xb), y1, z1)
        vs, _ = _box(a, lo, hi, key, _rt(nm, 0.04))
        _reg(kind, nm, vs)
    # z 10.53 .. 11.07: on the plate's flat outer face, inside its 0.12 chamfers (so the plate touches it face to face)
    bx(x0, x0 + 0.08, yc - 0.42, yc + 0.42, 10.53, 11.07, IRON, "iron", f"bplate_{tag}")
    bx(x0 + 0.085, x0 + 0.44, yc - 0.18, yc + 0.18, 10.62, 10.98, TIMBER_END, "peg", f"bpeg_{tag}")
    for k, dy in enumerate((-0.31, 0.31)):
        bx(x0 + 0.085, x0 + 0.19, yc + dy - 0.06, yc + dy + 0.06, 10.74, 10.86, IRON, "iron", f"rivet_{tag}{k}")


def rafter(a, sx, y):
    """A common rafter (0.50 x 0.60) from the ridge beam's side down onto the plate (horizontal seat cut), its top
    0.015 under the canvas; ends plumb at the plate's outer face. A 5-sided prism: 16 tris."""
    top = lambda x: zu(x) - SINK_TOP
    rv = RAFTER_D / COS
    seat = PLATE[3] + 0.003
    xs = (zu(0.0) - SINK_TOP - rv - seat) / P
    xe = EAVE_BLK[0] - OVL          # the tail stops at the eave blocking (round-1 fix), still seated on the plate
    poly = [(RIDGE_W / 2 + 0.005, top(RIDGE_W / 2 + 0.005)), (xe, top(xe)), (xe, seat), (xs, seat),
            (RIDGE_W / 2 + 0.005, top(RIDGE_W / 2 + 0.005) - rv)]
    nm = f"rafter_{'L' if sx < 0 else 'R'}{y:+.2f}"
    vs, fs, _, _ = _ext(a, poly, lambda u, v, w: Vector((sx * u, w, v)), y - RAFTER_W / 2, y + RAFTER_W / 2, TIMBER,
                        _rt(nm, 0.05))
    _texture(a, vs, 0.03, _seed(nm), scale=0.4)
    _reg("beam", nm, vs)


PURLIN_SEGS = ((-CAN_Y + 0.006, -8.002), (-7.598, -6.072), (-5.568, -2.192), (-1.688, 1.688), (2.192, 5.568),
               (6.072, 7.598), (8.002, CAN_Y - 0.006))


def purlins(a, sx):
    """The mid-slope purlin (spec 2.6) in segments between the rafters (and the gable boards), flush under the
    canvas like the rafters."""
    x0, x1 = PURLIN_X - PURLIN_W / 2, PURLIN_X + PURLIN_W / 2
    top = lambda x: zu(x) - SINK_TOP
    poly = [(x0, top(x0) - PURLIN_H), (x1, top(x1) - PURLIN_H), (x1, top(x1)), (x0, top(x0))]
    for i, (y0, y1) in enumerate(PURLIN_SEGS):
        nm = f"purlin_{'L' if sx < 0 else 'R'}{i}"
        vs, _, _, _ = _ext(a, poly, lambda u, v, w: Vector((sx * u, w, v)), y0, y1, TIMBER, _rt(nm, 0.05))
        _reg("beam", nm, vs)


def eave_block(a, s):
    """Round-1 fix: eave blocking, one continuous timber on the plate top along the eave between the gable planes
    (x 6.85-7.08, OVL into the plate and into the unsagged canvas there), closing the slit between plate and canvas
    that let light into the roof space. The rafter tails stop against it."""
    x0, x1 = EAVE_BLK
    zb = PLATE[3] - OVL
    poly = [(x0, zb), (x1, zb), (x1, zu(x1) + OVL), (x0, zu(x0) + OVL)]
    yy = WALL_IN_Y + WALL_T - 0.015              # inside the gable boards' faces (no coplanar ends)
    nm = f"eaveblk_{'L' if s < 0 else 'R'}"
    vs, _, _, _ = _ext(a, poly, lambda u, v, w: Vector((s * u, w, v)), -yy, yy, TIMBER, _rt(nm, 0.04))
    _texture(a, vs, 0.03, _seed(nm), scale=0.4)
    _reg("beam", nm, vs)


def _trim_top(x):
    """Rafter / trimmer top line (0.015 under the canvas underside)."""
    return zu(x) - SINK_TOP


def trimmers(a):
    """Two short timbers between the rafters at y -5.82 and -1.94, in the rafters' own band (tops 0.015 under the
    canvas, 0.60 deep), under the chimney's two long edges (close-up C): the chimney's sloped foot sits on them."""
    cx, cy = CHIMNEY
    h = CH_W / 2
    rv = RAFTER_D / COS
    for i, (x0, x1) in enumerate(((cx - h, cx - h + RAFTER_W), (cx + h - RAFTER_W, cx + h))):
        nm = f"trimmer_{i}"
        poly = [(x0, _trim_top(x0) - rv), (x1, _trim_top(x1) - rv), (x1, _trim_top(x1)), (x0, _trim_top(x0))]
        vs, _, _, _ = _ext(a, poly, lambda u, v, w: Vector((u, w, v)), RAFTER_Y[0] + RAFTER_W / 2 + 0.002,
                           RAFTER_Y[1] - RAFTER_W / 2 - 0.002, TIMBER, _rt(nm, 0.05))
        _reg("beam", nm, vs)


def ridge_section():
    """The ridge beam's 7-sided section (x, z): chamfered bottom corners, the top following both canvas slopes 0.01
    under the canvas underside."""
    h = RIDGE_W / 2
    # 0.01 under the canvas at the apex; at its edges also under the panel sag there (the first grid column sags up
    # to SAG * x / 2.05 in mid-bay), so its top edges never cross the canvas underside
    ztop = lambda x: zu(x) - 0.01 - SAG * abs(x) / CXI[1] - 0.005 * (abs(x) > 0)
    ch = 0.10
    return [(-h + ch, RIDGE_Z0), (h - ch, RIDGE_Z0), (h, RIDGE_Z0 + ch), (h, ztop(h)), (0.0, ztop(0.0)),
            (-h, ztop(h)), (-h, RIDGE_Z0 + ch)]


RT_RB = 0.10
RIDGE_BANDS = (10.36, 10.58)


def ridge_beam(a):
    """The ridge beam (1.00 wide) under the canvas apex, its pale ends 0.60 past the bargeboards, two golden rope
    turns round each end (spec 2.6, the exploded's golden band)."""
    sec = ridge_section()
    vs, fs, caps, sides = _ext(a, sec, lambda u, v, w: Vector((u, w, v)), -RIDGE_END, RIDGE_END, TIMBER,
                               _rt("ridge", 0.04), cap_key=TIMBER_END)
    _texture(a, vs, 0.03, 6810, scale=0.4)
    _reg("beam", "ridge", vs)
    for e in (-1, 1):
        for k, yb in enumerate(RIDGE_BANDS):
            y = e * yb
            pts = [Vector((u, y, v)) for u, v in sec]
            c = Vector((0.0, y, (RIDGE_Z0 + zu(0.0)) / 2))
            path = hull_loop(pts, c, Vector((0, 1, 0)), Vector((1, 0, 0)), RT_RB - 0.02, 8)
            rope(a, path, RT_RB, 4, True, f"ridgeband_{'F' if e < 0 else 'B'}{k}", up=Vector((0, 1, 0)))


# ---- gable frames (spec 2.5-2.6) ---------------------------------------------------------------------------------------
BB_FOOT, BB_TIP, BB_HEEL = 8.20, 1.60, (6.40, 7.20)   # tips 1.6 out: the sheet's big X
DV = BB_D / COS


def _bb_bottom(sx, x, lift=0.0):
    """Bottom line of the bargeboard whose foot is on side sx (the canvas underside on its own slope)."""
    return RIDGE_Z - CTV - sx * P * x + lift


def _isect(sa, la, sb, lb):
    """x, z where the lines z = c - s * P * x (+ offsets) meet: (slope sign, offset) pairs."""
    # z = RIDGE_Z - CTV - s * P * x + l
    x = (lb - la) / ((sb - sa) * P) if sa != sb else 0.0
    return x, RIDGE_Z - CTV - sa * P * x + la


def bargeboards(a, e):
    """Spec 2.6: the gable's crossed bargeboards (0.90 x 0.92, 0.80 proud of the canvas), both in one plane like a
    half-lap X: board A (foot on -X) whole, board B (foot on +X) in two pieces butting A's faces (below it and the
    tip above it), so nothing interpenetrates. Each foot has a heel seated on its plate, the feet and tips cut square
    to the board. A golden saddle block sits in the V between the tips."""
    g = 0.003
    tag = "F" if e < 0 else "B"
    y0, y1 = sorted((e * BB_Y[0], e * BB_Y[1]))
    mp = lambda u, v, w: Vector((u, w, v))
    end_key = TIMBER_END
    n = lambda sx: Vector((sx * SIN, COS))
    pieces = {}
    for sx in (-1, 1):
        bf = Vector((sx * BB_FOOT, _bb_bottom(sx, sx * BB_FOOT)))
        tf = bf + n(sx) * BB_D
        h0, h1 = BB_HEEL
        heel = [(sx * h1, _bb_bottom(sx, sx * h1)), (sx * h1, PLATE[3] + g), (sx * h0, PLATE[3] + g),
                (sx * h0, _bb_bottom(sx, sx * h0))]
        if sx < 0:
            bt = Vector((-sx * BB_TIP, _bb_bottom(sx, -sx * BB_TIP)))
            tt = bt + n(sx) * BB_D
            poly = [tuple(bf)] + heel + [tuple(bt), tuple(tt), tuple(tf)]
            pieces["A"] = (poly, [len(poly) - 1, 5])             # foot and tip faces (indices of side faces)
        else:
            # lower piece: under A's bottom line (lowered by g)
            xi0, zi0 = _isect(1, 0.0, -1, -g)                    # B bottom meets A bottom - g
            xi1, zi1 = _isect(1, DV, -1, -g)                     # B top meets A bottom - g
            poly = [tuple(bf)] + heel + [(xi0, zi0), (xi1, zi1), tuple(tf)]
            pieces["B"] = (poly, [len(poly) - 1])
            # tip piece: above A's top line (lifted by g)
            xt0, zt0 = _isect(1, DV, -1, DV + g)                 # B top meets A top + g
            xt1, zt1 = _isect(1, 0.0, -1, DV + g)                # B bottom meets A top + g
            bt = Vector((-sx * BB_TIP, _bb_bottom(sx, -sx * BB_TIP)))
            tt = bt + n(sx) * BB_D
            poly = [(xt0, zt0), (xt1, zt1), tuple(bt), tuple(tt)]
            pieces["Bt"] = (poly, [2])
    for k, (poly, ends) in pieces.items():
        nm = f"bb_{tag}_{k}"
        sk = [end_key if i in ends else TIMBER for i in range(len(poly))]
        vs, fs, _, _ = _ext(a, poly, mp, y0, y1, TIMBER, _rt(nm, 0.05), side_keys=sk)
        _texture(a, vs, 0.03, _seed(nm), scale=0.4)
        _reg("board", nm, vs)
    # saddle in the V between the tips (on A's top for x > 0 and on B's tip top for x < 0)
    ztopA = lambda x: _bb_bottom(-1, x) + DV
    sw, stop = 0.35, 17.42
    poly = [(0.0, ztopA(0.0) + g), (sw, ztopA(sw) + g), (sw, stop), (-sw, stop), (-sw, ztopA(sw) + g)]
    vs, _, _, _ = _ext(a, poly, mp, y0 + 0.02, y1 - 0.02, TIMBER_END, _rt(f"saddle{tag}", 0.03))
    _reg("board", f"saddle_{tag}", vs)
    GEO.setdefault("bargeboard_tip_top", round(tt.y, 3))
    cleats(a, e)


CLEAT = (0.40, 0.30, 1.40)            # along the board, thick, across (spec 2.6)


def cleats(a, e):
    """Round-1 fix (minor 2): two cleats per bargeboard at 1/3 and 2/3 of the way from the foot to the apex, across
    the board's top face (OVL into it), overhanging both faces by 0.25 so they cross the canvas edge (top cell,
    f34). Light timber, one step toward the pale ends (by role)."""
    tag = "F" if e < 0 else "B"
    L, T, Wc = CLEAT
    yc = e * (BB_Y[0] + BB_Y[1]) / 2
    key = _mix(TIMBER, TIMBER_END, 0.25)
    for sx in (-1, 1):
        t = Vector((COS, 0.0, -sx * SIN))
        n = Vector((sx * SIN, 0.0, COS))
        for k, f in enumerate((1 / 3, 2 / 3)):
            xc = sx * BB_FOOT * (1.0 - f)
            c = Vector((xc, yc, _bb_bottom(sx, xc) + DV))
            m = Matrix(((t.x, 0.0, n.x, c.x), (0.0, 1.0, 0.0, c.y), (t.z, 0.0, n.z, c.z), (0.0, 0.0, 0.0, 1.0)))
            nm = f"cleat_{tag}{'L' if sx < 0 else 'R'}{k}"
            vs, _ = _box(a, (-L / 2, -Wc / 2, -OVL), (L / 2, Wc / 2, T), key, _rt(nm, 0.04), m=m)
            _texture(a, vs, 0.03, _seed(nm), scale=0.4)
            _reg("board", nm, vs)


def collar(a, e):
    """Front (e = -1): the collar beam at eave level in front of the gable, between the plates over the lintel.
    Back: the collar on the back wall's outer face over the two frame posts."""
    if e < 0:
        vs, _ = _box(a, (-PLATE[0] + 0.003, DPOST[2], PLATE[2]), (PLATE[0] - 0.003, -8.40, PLATE[3] - 0.003), TIMBER,
                     _rt("collarF", 0.04))
        _reg("beam", "collar_F", vs)
    else:
        y0 = WALL_IN_Y + WALL_T + 0.003
        vs, _ = _box(a, (-PLATE[0] + 0.003, y0, PLATE[2]), (PLATE[0] - 0.003, y0 + 0.80, PLATE[3] - 0.003), TIMBER,
                     _rt("collarB", 0.04))
        _reg("beam", "collar_B", vs)


def back_frame_posts(a):
    """Spec 2.4: two frame posts (1.10 x 0.50) on the back wall's outer face (the r34's vertical post)."""
    y0 = WALL_IN_Y + WALL_T + 0.003
    for sx in (-1, 1):
        nm = f"framepost_{'L' if sx < 0 else 'R'}"
        x0, x1 = sorted((sx * 1.80, sx * 2.90))
        vs, _ = _box(a, (x0, y0, ROW_Z0 + 0.003), (x1, y0 + 0.50, PLATE[2] - 0.003), TIMBER, _rt(nm, 0.05))
        _reg("post", nm, vs)


def gable_infill(a, e):
    """Vertical boards (0.97 wide) in the end-wall plane above the top plank row, closed for the round-1 fix:
    - neighbouring boards overlap 2 * OVL edge to edge, every other board 0.01 thinner on both faces (no coplanar
      faces; the steps still read as boards);
    - the bottoms OVL * 2 into the top plank row and the posts' tops; the tops OVL into the canvas underside (the end
      bays sag SAG_END, so the deepest sink stays under BURY);
    - a board under the ridge beam (into its chamfered underside) and an apex block over it, from the ridge top into
      the canvas, its peak in the slabs' apex seam;
    - the outer boards wrap the plate's inner chamfers and face and run over the plate top onto the eave blocking."""
    tag = "F" if e < 0 else "B"
    zb = row_z(4)[1] - 2 * OVL
    h = RIDGE_W / 2
    mp = lambda u, v, w: Vector((u, w, v))
    yin, yout = WALL_IN_Y + 0.01, WALL_IN_Y + WALL_T - 0.01

    def ys(odd):
        d = 0.01 if odd else 0.0
        return sorted((e * (yin + d), e * (yout - d)))

    def put(poly, odd, nm, faces=None):
        y0, y1 = ys(odd)
        if faces is None:
            vs, _, _, _ = _ext(a, poly, mp, y0, y1, TIMBER, _rt(nm, 0.05))
        else:
            n = len(poly)
            pts = [mp(u, v, y0) for u, v in poly] + [mp(u, v, y1) for u, v in poly]
            fl = [list(f) for f in faces] + [[n + f[2], n + f[1], n + f[0]] for f in faces]
            fl += [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
            vs, _ = _shell(a, pts, fl, TIMBER, _rt(nm, 0.05))
        _texture(a, vs, 0.03, _seed(nm), scale=0.5)
        _reg("plank", nm, vs)
    # under the ridge beam: the top OVL into its flat underside and chamfers
    rb, ch = RIDGE_Z0 + OVL, 0.10
    zr = lambda x: RIDGE_Z0 + max(0.0, abs(x) - (h - ch)) + OVL        # ridge underside + OVL (vertical)
    put([(-h - OVL, zb), (h + OVL, zb), (h + OVL, zr(h) + OVL), (h - ch - 0.001, rb), (-h + ch + 0.001, rb),
         (-h - OVL, zr(h) + OVL)], False, f"gboard_{tag}_mid")
    # apex block: the ridge's pitched top - OVL up to the canvas underside + OVL, its peak in the apex seam between
    # the two slabs (explicit fan from the bottom middle, so no edge crosses a slab twice)
    sec = ridge_section()
    zt_h, zt_0 = sec[3][1], sec[4][1]
    hb = h + OVL
    poly = [(-hb, zt_h - OVL), (0.0, zt_0 - OVL), (hb, zt_h - OVL), (hb, zu(hb) + OVL), (0.0, zu(0.0) + 0.05),
            (-hb, zu(hb) + OVL)]
    put(poly, False, f"gboard_{tag}_apex", faces=[(0, 1, 5), (1, 4, 5), (1, 2, 3), (1, 3, 4)])
    # six boards a side from the ridge's faces to the plates' inner faces
    W = (PLATE[0] - h) / 6
    x0p, z0p, z1p = PLATE[0], PLATE[2], PLATE[3]
    pch = PLATE[5]
    for sx in (-1, 1):
        for k in range(6):
            xa, xb = h + k * W - OVL, h + (k + 1) * W + OVL
            if k < 5:
                poly = [(xa, zb), (xb, zb), (xb, zu(xb) + OVL), (xa, zu(xa) + OVL)]
            else:          # wrap the plate (chamfer lines moved 0.003 into it) and run over it to the eave block
                lb = x0p + z0p + pch + 0.003                      # bottom inner chamfer: x + z = lb
                lt = z1p - pch - x0p - 0.003                      # top inner chamfer: z - x = lt
                xf = EAVE_BLK[0] + OVL
                poly = [(xa, zb), (lb - zb, zb), (x0p + OVL, lb - x0p - OVL), (x0p + OVL, lt + x0p + OVL),
                        (z1p - OVL - lt, z1p - OVL), (xf, z1p - OVL), (xf, zu(xf) + OVL), (xa, zu(xa) + OVL)]
            if sx < 0:
                poly = [(-u, v) for u, v in reversed(poly)]
            put(poly, k % 2 == 0, f"gboard_{tag}{'L' if sx < 0 else 'R'}{k}")


def gable_frame(a, e, part=False):
    """GableFrame (exploded "Front Gable Frame"): the collar, the crossed bargeboards and their saddle; the part
    carries the two plate ends the boards sit on."""
    collar(a, e)
    bargeboards(a, e)
    if part:
        for s in (-1, 1):
            x0, x1, z0, z1, ye, ch = PLATE
            oc = _oct_rect(x0, x1, z0, z1, ch)
            ya, yb = sorted((e * 8.40, e * ye))
            vs, _, _, _ = _ext(a, oc, lambda u, v, w, s=s: Vector((s * u, w, v)), ya, yb, TIMBER, 0.98,
                               cap_key=TIMBER_END)
            _reg("beam", f"plate_end_{s}", vs)


# ---- door frame and leaf (spec 2.5) ------------------------------------------------------------------------------------
LEAF = (3.56, 2.62, 9.58)            # width, bottom, top
HINGE = (-DOOR_X, -WALL_IN_Y + 0.01)
OPEN_DEG = 95.0


def door_leaf(a, theta_deg):
    """The plank door (spec 2.5): four vertical planks with 0.04 seams, two inner battens, two iron strap hinges on
    the hinge side and an iron ring handle, hinged on the inner face of the left jamb (x -1.80); theta 0 closed
    (behind the opening), 95 open inward. The whole leaf one step toward timber_deep (by role)."""
    th = math.radians(theta_deg)
    R = Matrix.Translation((HINGE[0], HINGE[1], 0.0)) @ Matrix.Rotation(th, 4, "Z")
    W, z0, z1 = LEAF
    deep = _mix(TIMBER, TIMBER_DEEP, 0.25)
    pw = (W - 3 * 0.04) / 4
    for i in range(4):
        u0 = i * (pw + 0.04) + 0.003
        nm = f"leaf_plank{i}"
        vs, _ = _box(a, (u0, 0.003, z0), (u0 + pw, 0.203, z1), deep, _rt(nm, 0.05), R)
        _reg("door", nm, vs)
    for i, zc in enumerate((3.90, 8.10)):
        nm = f"leaf_batten{i}"
        vs, _ = _box(a, (0.18, 0.206, zc - 0.30), (W - 0.18, 0.306, zc + 0.30), deep, _rt(nm, 0.04), R)
        _reg("door", nm, vs)
    for i, zc in enumerate((3.90, 8.10)):
        nm = f"leaf_hinge{i}"
        vs, _ = _box(a, (0.05, -0.057, zc - 0.15), (1.85, 0.0, zc + 0.15), IRON, _rt(nm, 0.03), R)
        _reg("iron", nm, vs)
    uc, zc = W - 0.50, 6.00
    vs, _ = _box(a, (uc - 0.14, -0.043, zc - 0.14), (uc + 0.14, 0.0, zc + 0.14), IRON, 0.95, R)
    _reg("iron", "leaf_ringplate", vs)
    ring = [R @ Vector((uc + math.cos(2 * math.pi * k / 6) * 0.26, -0.043 - 0.05, zc - 0.20 + math.sin(2 * math.pi * k / 6) * 0.26))
            for k in range(6)]
    vs, _ = _tube(a, ring, 0.05, 3, True, IRON, tint=0.92, up=tuple(R.to_3x3() @ Vector((0, 1, 0))), twist=True)
    _reg("iron", "leaf_ring", vs)
    GEO["hinge"] = {"axis_bottom": [HINGE[0], HINGE[1], z0], "closed_yaw": 0.0, "open_yaw": OPEN_DEG}


def doorframe(a, theta_deg=OPEN_DEG):
    """DoorFrame: the two door posts (1.10, chamfered) on golden foot caps, the lintel (its pale ends 0.40 past the
    posts), the header plank in the wall plane over the opening and the leaf."""
    x0, x1, y0, y1 = DPOST
    for sx in (-1, 1):
        tag = "L" if sx < 0 else "R"
        xa, xb = sorted((sx * x0, sx * x1))
        vs, _ = _box(a, (xa - 0.03, y0 - 0.03, 0.0), (xb + 0.03, y1 - 0.005, 0.40), TIMBER_END, _rt(f"cap{tag}", 0.03))
        _reg("peg", f"dcap_{tag}", vs)
        post(a, xa, xb, y0, y1, 0.403, DOOR_TOP - 0.003, f"dpost_{tag}")
    vs, fs = _box(a, (-3.30, y0, DOOR_TOP), (3.30, -WALL_IN_Y - WALL_T - 0.005, PLATE[2] - 0.003), TIMBER,
                  _rt("lintel", 0.04))
    _paint(a, [fs[4], fs[5]], TIMBER_END)
    _reg("beam", "lintel", vs)
    # the header's ends run OVL into the top rows' ends at the jambs (round-1 fix)
    plank(a, "end", -1, -DOOR_X - OVL, DOOR_X + OVL, DOOR_TOP + 0.003, row_z(4)[1], "header", band=False)
    door_leaf(a, theta_deg)


# ---- canvas (spec 2.7) ---------------------------------------------------------------------------------------------------
CXI = (0.001, 2.05, 4.10, 5.775, 6.85, EAVE)
CYS = (-CAN_Y, -7.535, -5.82, -3.88, -1.94, 0.0, 1.94, 3.88, 5.82, 7.535, CAN_Y)
SAG = 0.08
SAG_END = 0.05                         # the two end bays (round-1 fix): the gable boards' straight tops run OVL into
                                       # the canvas underside; at 0.08 the sag over the gable plane sank them past BURY
SAG_XI = (2.05, 5.775)
SAG_Y = (-7.535, -3.88, 0.0, 3.88, 7.535)
HEM = ((6.85, 0.5), (5.775, 0.25))     # faces outside xi: canvas_deep share (hem blend, by position)


def roof_panel(a, s, hole=False):
    """One closed canvas slab (0.12 thick) over one slope: a grid of 5 bays along Y (the rafter lines) x 2 rows (the
    purlin line), each panel sagging 0.08 at its centre (X creases from the triangulation), from the apex (0.001 off
    the ridge line: the two slabs meet face to face) to the eave 0.25 past the plate. hole: cut round the chimney
    (0.03 clear). Hem bands toward canvas_deep along the eave (by position), and round the cut."""
    tag = "L" if s < 0 else "R"
    nx, ny = len(CXI), len(CYS)

    def sag(i, j):
        if not (CXI[i] in SAG_XI and CYS[j] in SAG_Y):
            return 0.0
        return SAG_END if abs(CYS[j]) == SAG_Y[-1] else SAG
    top = {}
    for i in range(nx):
        for j in range(ny):
            top[(i, j)] = Vector((s * CXI[i], CYS[j], zt(CXI[i]) - sag(i, j)))
    hole_q = set()
    if hole:
        hole_q = {(i, j) for i in (0, 1) for j in (2, 3)}
    keys_t = list(top.keys())
    pts = [top[k] for k in keys_t]
    idx = {k: n for n, k in enumerate(keys_t)}
    inner = []
    if hole:
        x0, x1, y0, y1 = HOLE
        for xx, yy in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            inner.append(len(pts))
            pts.append(Vector((s * xx, yy, zt(xx))))
    nt = len(pts)
    pts += [p - Vector((0, 0, CTV)) for p in pts]
    tris, tkeys = [], []

    def hem_key(xi_c):
        for lim, t in HEM:
            if xi_c > lim:
                return _mix(CANVAS, CANVAS_DEEP, t)
        return CANVAS
    for i in range(nx - 1):
        for j in range(ny - 1):
            if (i, j) in hole_q:
                continue
            q = [idx[(i, j)], idx[(i + 1, j)], idx[(i + 1, j + 1)], idx[(i, j + 1)]]
            sg = [sag(*k) for k in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))]
            k0 = next((k for k in range(4) if sg[k] > 0), 0)          # split through the sagged corner (X creases)
            q = q[k0:] + q[:k0]
            key = hem_key((CXI[i] + CXI[i + 1]) / 2)
            tris += [(q[0], q[1], q[2]), (q[0], q[2], q[3])]
            tkeys += [key, key]
    if hole:
        O = [idx[(0, 2)], idx[(1, 2)], idx[(2, 2)], idx[(2, 3)], idx[(2, 4)], idx[(1, 4)], idx[(0, 4)], idx[(0, 3)]]
        I = inner
        ring = [(O[0], O[1], I[0]), (O[1], I[1], I[0]), (O[1], O[2], I[1]), (O[2], O[3], I[1]), (O[3], I[2], I[1]),
                (O[3], O[4], I[2]), (O[4], O[5], I[2]), (O[5], I[3], I[2]), (O[5], O[6], I[3]), (O[6], O[7], I[3]),
                (O[7], I[0], I[3]), (O[7], O[0], I[0])]
        tris += ring
        tkeys += [_mix(CANVAS, CANVAS_DEEP, 0.5)] * len(ring)
    faces = [list(t) for t in tris] + [[nt + t[2], nt + t[1], nt + t[0]] for t in tris]
    keys = tkeys + tkeys
    if hole:                     # grid points inside the cut (the sagged (1, 3) node) would be loose verts
        used = {i for t in tris for i in t}
        loop_pts = ({idx[(i, 0)] for i in range(nx)} | {idx[(nx - 1, j)] for j in range(ny)} |
                    {idx[(i, ny - 1)] for i in range(nx)} | {idx[(0, j)] for j in range(ny)})
        drop = sorted(set(range(nt)) - used - loop_pts)
        if drop:
            keep = [i for i in range(nt) if i not in drop]
            remap = {old: new for new, old in enumerate(keep)}
            remap.update({nt + old: len(keep) + new for new, old in enumerate(keep)})
            pts = [pts[i] for i in keep] + [pts[nt + i] for i in keep]
            faces = [[remap[i] for i in f] for f in faces]
            idx = {k: remap[v] for k, v in idx.items() if v in remap}
            inner = [remap[i] for i in inner]
            nt = len(keep)
    # rims: the outer boundary and the hole
    loop = ([idx[(i, 0)] for i in range(nx)] + [idx[(nx - 1, j)] for j in range(1, ny)] +
            [idx[(i, ny - 1)] for i in range(nx - 2, -1, -1)] + [idx[(0, j)] for j in range(ny - 2, 0, -1)])
    for k in range(len(loop)):
        u, v = loop[k], loop[(k + 1) % len(loop)]
        faces.append([u, v, nt + v, nt + u])
        xc = abs((pts[u].x + pts[v].x) / 2)
        keys.append(_mix(CANVAS, CANVAS_DEEP, 0.75) if xc > EAVE - 0.01 else hem_key(xc))
    if hole:
        for k in range(4):
            u, v = inner[k], inner[(k + 1) % 4]
            faces.append([u, v, nt + v, nt + u])
            keys.append(_mix(CANVAS, CANVAS_DEEP, 0.75))
    vs, fs = _shell(a, pts, faces, CANVAS, _rt(f"canvas{tag}", 0.02))
    for f, k in zip(fs, keys):
        if k != CANVAS:
            f.material_index = a._mi(k)
    _texture(a, vs, 0.03, _seed(f"canvas{tag}"), scale=0.22)
    _reg("canvas", f"canvas_{tag}", vs)
    return vs


TIE_W, TIE_T, TIE_G = 0.24, 0.08, 0.005


def _offset_path(prof, d):
    """Mitred offset of an open 2D polyline to its left by d: (points, unit offset directions scaled by the mitre)."""
    out = []
    n = len(prof)
    for i in range(n):
        dirs = []
        if i > 0:
            dirs.append(Vector((prof[i][0] - prof[i - 1][0], prof[i][1] - prof[i - 1][1])).normalized())
        if i < n - 1:
            dirs.append(Vector((prof[i + 1][0] - prof[i][0], prof[i + 1][1] - prof[i][1])).normalized())
        nrm = [Vector((-t.y, t.x)) for t in dirs]
        if len(nrm) == 1:
            m = nrm[0]
        else:
            bis = (nrm[0] + nrm[1]).normalized()
            m = bis / max(bis.dot(nrm[0]), 0.3)
        out.append(m)
    return out


def tie(a, s, y, name, short=False):
    """A golden U tie (spec 2.7): a flat strap 0.24 x 0.08 over the canvas top near the eave, round the canvas edge,
    across to the plate and down its outer face, its end under the plate against the wall (both ends touch).
    short (the RoofPanel part, which has no plate): a U clip round the canvas edge only."""
    x0, x1, z0, z1, _, ch = PLATE
    if short:
        prof = [(6.85, zt(6.85)), (EAVE, zt(EAVE)), (EAVE, zt(EAVE) - CTV), (6.85, zt(6.85) - CTV)]
    else:
        prof = [(6.85, zt(6.85)), (EAVE, zt(EAVE)), (EAVE, zt(EAVE) - CTV), (x1, z1 - ch), (x1, z0 + ch),
                (x1 - ch, z0), (WALL_IN_X + WALL_T + 0.03, z0)]
    mv = _offset_path(prof, 1.0)
    rings = []
    cl = []
    for (u, v), m in zip(prof, mv):
        p = Vector((u, v))
        q0, q1 = p + m * TIE_G, p + m * (TIE_G + TIE_T)
        cl.append(p + m * (TIE_G + TIE_T / 2))
        rings.append([Vector((s * q0.x, y - TIE_W / 2, q0.y)), Vector((s * q0.x, y + TIE_W / 2, q0.y)),
                      Vector((s * q1.x, y + TIE_W / 2, q1.y)), Vector((s * q1.x, y - TIE_W / 2, q1.y))])
    vs, fs, bands = _prism(a, rings, ROPE, _rt(name, 0.04))
    for b in bands:
        _paint(a, [b[1]], _mix(ROPE, ROPE_DEEP, 0.5))      # one edge strand of the strap (by index, not facing)
    _reg("rope", name, vs)
    ROPES.append({"name": name, "ends": [[s * cl[0].x, y, cl[0].y], [s * cl[-1].x, y, cl[-1].y]],
                  "rt": TIE_G + TIE_T / 2})


def ties(a, s, short=False):
    for i, y in enumerate(RAFTER_Y):
        tie(a, s, y, f"tie_{'L' if s < 0 else 'R'}{i}", short=short)


# ---- chimney (spec 2.8) --------------------------------------------------------------------------------------------------
def chimney(a):
    """A square stone stack in two blocks (the upper set in 0.10: the notched joint), a 3.00 cap with a 1.40 flue
    recess 0.60 deep (soot). The sheet draws the whole stack a mid grey (f34 #887F84, darker than the plinth): the
    lower block half way to stone_dark, the upper block and the cap a quarter of the way (by role)."""
    cx, cy = CHIMNEY
    h = CH_W / 2
    foot = lambda x: _trim_top(x) + 0.003          # the lower block's foot follows the roof pitch on the trimmers
    pts = [Vector((x, y, foot(x))) for x, y in ((cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h))]
    pts += [Vector((p.x, p.y, CH_JOINT)) for p in pts]
    vs, _ = _shell(a, pts, HEXA, _mix(STONE, STONE_DARK, 0.5), _rt("chim_lo", 0.03))
    GEO["chimney_foot"] = [round(foot(cx - h), 3), round(foot(cx + h), 3)]
    _texture(a, vs, 0.04, 6820, scale=0.8)
    _reg("chimney", "chim_lo", vs)
    # round-1 fix: a flashing collar on the canvas round the stack (OVL into the canvas top and the stack), over the
    # cut's OVL clearance, so no light comes in round the chimney; the darker mortar grey of the stack's joint
    fw, fh = COLLAR
    ri, ro = h - OVL, h + fw
    sq = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    ring = lambda r, dz: [Vector((cx + x * r, cy + y * r, zt(cx + x * r) + dz)) for x, y in sq]
    pts = ring(ro, -OVL) + ring(ri, -OVL) + ring(ro, fh) + ring(ri, fh)
    faces = []
    for k in range(4):
        k1 = (k + 1) % 4
        faces += [[8 + k, 8 + k1, 12 + k1, 12 + k], [k1, k, 4 + k, 4 + k1], [k, k1, 8 + k1, 8 + k],
                  [4 + k1, 4 + k, 12 + k, 12 + k1]]
    vs, _ = _shell(a, pts, faces, _mix(STONE, STONE_DARK, 0.6), _rt("chim_collar", 0.03))
    _reg("chimney", "chim_collar", vs)
    h2 = h - 0.10
    cap = _mix(STONE, STONE_DARK, 0.25)
    vs, _ = _box(a, (cx - h2, cy - h2, CH_JOINT + 0.003), (cx + h2, cy + h2, CH_Z1), cap, _rt("chim_up", 0.03))
    _texture(a, vs, 0.04, 6821, scale=0.8)
    _reg("chimney", "chim_up", vs)
    hc, hf, zc0, zf = 1.50, 0.70, CH_Z1 + 0.003, CH_TOP - 0.60
    o0 = [Vector((cx + x * hc, cy + y * hc, zc0)) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    o1 = [p + Vector((0, 0, CH_TOP - zc0)) for p in o0]
    i1 = [Vector((cx + x * hf, cy + y * hf, CH_TOP)) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    i0 = [p - Vector((0, 0, CH_TOP - zf)) for p in i1]
    pts = o0 + o1 + i1 + i0
    faces = [[3, 2, 1, 0]]
    keys = [cap]
    for k in range(4):
        k1 = (k + 1) % 4
        faces.append([k, k1, 4 + k1, 4 + k])
        keys.append(cap)
        faces.append([4 + k, 4 + k1, 8 + k1, 8 + k])
        keys.append(cap)
        faces.append([8 + k, 8 + k1, 12 + k1, 12 + k])
        keys.append(SOOT)
    faces.append([12, 13, 14, 15])
    keys.append(SOOT)
    vs, fs = _shell(a, pts, faces, cap, _rt("chim_cap", 0.03))
    for f, k in zip(fs, keys):
        if k != cap:
            f.material_index = a._mi(k)
    _reg("chimney", "chim_cap", vs)
    GEO["flue"] = [cx, cy, CH_TOP - 0.10]


SMOKE = {"emitters": [{"name": "Smoke", "texture": "smoke_puff", "color": ["#BDB8B4", "#E4E0DC"], "size": [1.0, 3.5],
                       "transparency": [0.6, 1.0], "lifetime": [3, 5], "rate": 2, "speed": [1.5, 2.5], "spread": 6,
                       "light_emission": 0.0, "acceleration": [0.4, 0.3, 0], "drag": 0.3, "rotation": [0, 360],
                       "rot_speed": [-15, 15]}], "light": None}


# ---- stairs (spec 2.9) ---------------------------------------------------------------------------------------------------
STAIR_X = 2.40
TREADS = ((-11.10, -9.503, 1.73), (-12.70, -11.10, 0.87))       # y0, y1, top


def stairs(a):
    """Two treads of two planks (0.78 wide, 0.04 gap, 0.30 thick): the upper on two blocks against the door posts,
    the lower on two feet; three equal 0.87 risers to the threshold."""
    for ti, (y0, y1, ztop) in enumerate(TREADS):
        w = (y1 - y0 - 0.04) / 2
        for k in range(2):
            ya = y0 + k * (w + 0.04)
            nm = f"tread{ti}_{k}"
            vs, _ = _box(a, (-STAIR_X, ya, ztop - 0.30), (STAIR_X, ya + w, ztop), TIMBER, _rt(nm, 0.05))
            _texture(a, vs, 0.03, _seed(nm), scale=0.5)
            _reg("plank", nm, vs)
        for k, sx in enumerate((-1, 1)):
            nm = f"tblock{ti}_{k}"
            xa, xb = sorted((sx * 1.50, sx * 2.10))
            vs, _ = _box(a, (xa, y0 + 0.10, 0.0), (xb, y1 - 0.10, ztop - 0.303), _mix(TIMBER, TIMBER_DEEP, 0.4),
                         _rt(nm, 0.05))
            _reg("beam", nm, vs)
    GEO["risers"] = [TREADS[1][2], round(TREADS[0][2] - TREADS[1][2], 3), round(FLOOR_Z - TREADS[0][2], 3)]


# ---- lanterns (spec 2.9, lighting / VFX) ---------------------------------------------------------------------------------
L_W, L_PLATE, L_GW, L_GH, L_BAND, L_ROOF, L_FIN, L_BAR = 1.40, 0.20, 1.00, 1.60, 0.25, 0.40, 0.15, 0.16
L_BODY = L_PLATE + L_GH + L_BAND + L_ROOF + L_FIN          # 2.60
RING_R, RING_T = 0.20, 0.06
L1 = (-8.30, -6.60, 6.40)                                   # eave lantern base
L23 = ((-4.70, -9.10, 6.20), (4.70, -9.10, 6.20))           # door lanterns


def lantern(a, base, tag, ring_axis=(1, 0, 0)):
    """A square dark-iron lantern (2.60 body): base plate, Neon glass block, four corner bars, top band, pyramid
    roof, finial and a hanging ring on top. Returns (glass centre, ring top)."""
    c = Vector(base)
    h = L_W / 2
    vs, _ = _box(a, c + Vector((-h, -h, 0)), c + Vector((h, h, L_PLATE)), IRON, _rt(tag + "p", 0.03))
    _reg("lmetal", f"{tag}_plate", vs)
    g = L_GW / 2
    vs, _ = _box(a, c + Vector((-g, -g, L_PLATE - 0.005)), c + Vector((g, g, L_PLATE + L_GH + 0.005)), GLOW, 1.0)
    _reg("glass", f"{tag}_glass", vs)
    bh = L_BAR / 2
    bc = h - bh - 0.005
    for i, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        vs, _ = _box(a, c + Vector((sx * bc - bh, sy * bc - bh, L_PLATE + 0.003)),
                     c + Vector((sx * bc + bh, sy * bc + bh, L_PLATE + L_GH - 0.003)), IRON, 0.95)
        _reg("lmetal", f"{tag}_bar{i}", vs)
    zb = L_PLATE + L_GH
    vs, _ = _box(a, c + Vector((-h, -h, zb)), c + Vector((h, h, zb + L_BAND)), IRON, 1.0)
    _reg("lmetal", f"{tag}_band", vs)
    zr = zb + L_BAND + 0.003
    rb, rt_ = 0.75, 0.25
    pts = [c + Vector(p) for p in ((-rb, -rb, zr), (rb, -rb, zr), (rb, rb, zr), (-rb, rb, zr),
                                   (-rt_, -rt_, zr + L_ROOF), (rt_, -rt_, zr + L_ROOF), (rt_, rt_, zr + L_ROOF),
                                   (-rt_, rt_, zr + L_ROOF))]
    vs, _ = _shell(a, pts, HEXA, IRON, 1.04)
    _reg("lmetal", f"{tag}_roof", vs)
    zf = zr + L_ROOF + 0.003
    vs, _ = _box(a, c + Vector((-0.15, -0.15, zf)), c + Vector((0.15, 0.15, zf + L_FIN - 0.006)), IRON, 0.96)
    _reg("lmetal", f"{tag}_finial", vs)
    top = zf + L_FIN - 0.006
    cz = top - 0.01 + RING_R + RING_T
    ax = Vector(ring_axis).normalized()
    ring = [c + Vector((0, 0, cz)) + ax * (math.cos(2 * math.pi * k / 6) * RING_R) +
            Vector((0, 0, 1)) * (math.sin(2 * math.pi * k / 6) * RING_R) for k in range(6)]
    nrm = ax.cross(Vector((0, 0, 1)))
    vs = _tube(a, ring, RING_T, 3, True, IRON, tint=0.9, up=tuple(nrm), twist=True)[0]
    _reg("lmetal", f"{tag}_ring", vs)
    gc = c + Vector((0, 0, L_PLATE + L_GH / 2))
    return gc, c + Vector((0, 0, cz + RING_R + RING_T))


ARM_Z = (9.75, 10.00)


def bracket(a, kind, at, ring_top, tag):
    """An iron bracket: a strap on the wall face up to the plate (eave) or on the front wall (door), an arm out
    from it and a hook down to the lantern's ring. kind "eave": on the -X long wall; "door": on the front wall."""
    x, y = at
    w = 0.125
    if kind == "eave":
        xf = -(WALL_IN_X + WALL_T + 0.003)
        boxes = [((xf - 0.12, y - w, ARM_Z[0] - 0.10), (xf, y + w, PLATE[2] - 0.003), "strap"),
                 ((x - 0.12, y - w, ARM_Z[0]), (xf - 0.123, y + w, ARM_Z[1]), "arm")]
    else:
        yf = -(WALL_IN_Y + WALL_T + 0.003)
        boxes = [((x - w, yf - 0.12, ARM_Z[0] - 0.10), (x + w, yf, PLATE[2] - 0.003), "strap"),
                 ((x - w, y - 0.12, ARM_Z[0]), (x + w, yf - 0.123, ARM_Z[1]), "arm")]
    boxes.append(((x - 0.05, y - 0.05, ring_top - 0.025), (x + 0.05, y + 0.05, ARM_Z[0] + 0.003), "hook"))
    for lo, hi, nm in boxes:
        vs, _ = _box(a, lo, hi, IRON, _rt(f"{tag}{nm}", 0.03))
        _reg("iron", f"{tag}_{nm}", vs)


def _fx_spec(rng=12):
    """Decision 13 of M064 reused (spec 7): heat_glow overridden to a steady warm lantern halo."""
    return {"emitters": [{"name": "Halo", "texture": "glow_soft", "color": ["#FFC23A", "#FF9A1E"], "size": [1.4, 1.7],
                          "transparency": [0.65, 1.0], "lifetime": [1.0, 1.5], "rate": 2, "speed": [0, 0.05],
                          "spread": 0, "light_emission": 1.0}],
            "light": {"color": "#FFB347", "brightness": 1.0, "range": rng, "flicker": True}}


def lantern_set(a, kind, base, tag):
    """A lantern on its bracket. Returns (glass centre, ring top)."""
    gc, rt = lantern(a, base, tag, ring_axis=(0, 1, 0) if kind == "eave" else (1, 0, 0))
    bracket(a, kind, (base[0], base[1]), rt.z, tag)
    GEO.setdefault("lanterns", {})[tag] = {"bottom": round(base[2], 3), "glass": [round(x, 3) for x in gc],
                                           "ring_top": round(rt.z, 3)}
    return gc, rt


# ---- banner (spec 2.9) ----------------------------------------------------------------------------------------------------
POLE = (-9.55, 10.55)
POLE_R, POLE_TOP = 0.42, 15.20
ARM_ZC, ARM_R = 14.40, 0.18
ARM_PROF = ((9.70, 0.26), (9.95, 0.26), (9.95, ARM_R), (11.05, ARM_R), (11.05, 0.23), (11.22, 0.23), (11.22, ARM_R),
            (13.55, ARM_R), (13.55, 0.26), (13.80, 0.26))
SLEEVE = (11.30, 13.45, 0.30, ARM_R + 0.003)
BAN_T, BAN_TIP, BAN_SIDE, BAN_NOTCH = 0.08, 6.40, 6.80, 7.55
EMB_W, EMB_H, EMB_S = 1.20, 2.00, 0.17
EMB_IW, EMB_IH, DOT_W, DOT_H, DOT_Y = 0.40, 0.60, 0.20, 0.30, 0.78
EMB_T = 0.015
RT_X = 0.10


def banner_set(a):
    """Banner Pole + Banner: an 8-sided pole with a golden foot band and a block top; a 6-sided crossarm along Y
    through it (knob ends, an iron band) at z 14.4; a golden X lashing (two loops in crossing 45-deg planes, the second
    lying over the first); a sleeve hem round the arm and the red swallowtail banner (a closed 0.08 slab) with the
    white emblem on both faces (diamond ring, inner diamond, two side points)."""
    px, py = POLE
    e1, e2 = Vector((1, 0, 0)), Vector((0, 1, 0))
    prof = ((0.0, POLE_R), (0.40, POLE_R), (0.40, POLE_R + 0.05), (0.70, POLE_R + 0.05), (0.70, POLE_R),
            (POLE_TOP, POLE_R))
    rings = [_ngon(Vector((px, py, z)), e1, e2, r, 8, math.pi / 8) for z, r in prof]
    vs, fs, bands = _prism(a, rings, TIMBER, _rt("pole", 0.04))
    _paint(a, bands[1] + bands[2] + bands[3], TIMBER_END)
    _texture(a, vs, 0.03, 6830, scale=0.4)
    _reg("pole", "pole", vs)
    vs, _ = _box(a, (px - 0.50, py - 0.50, POLE_TOP + 0.003), (px + 0.50, py + 0.50, POLE_TOP + 0.60), TIMBER,
                 _rt("poletop", 0.04))
    _reg("pole", "pole_top", vs)
    ex, ez = Vector((1, 0, 0)), Vector((0, 0, 1))
    # the crossarm "through" the pole in two pieces butting the pole's flat -Y / +Y faces (nothing buried): a short
    # knobbed stub behind it and the long arm in front
    pf = POLE_R * math.cos(math.pi / 8) + 0.003
    stub = [p for p in ARM_PROF if p[0] < py] + [(py - pf, ARM_R)]
    arm = [(py + pf, ARM_R)] + [p for p in ARM_PROF if p[0] > py]
    rings = [_ngon(Vector((px, y, ARM_ZC)), ex, ez, r, 6, math.pi / 6) for y, r in stub]
    vs, fs, bands = _prism(a, rings, TIMBER, _rt("armstub", 0.04))
    _paint(a, [fs[-2]], TIMBER_END)
    _reg("pole", "crossarm_stub", vs)
    rings = [_ngon(Vector((px, y, ARM_ZC)), ex, ez, r, 6, math.pi / 6) for y, r in arm]
    vs, fs, bands = _prism(a, rings, TIMBER, _rt("arm", 0.04))
    k0 = next(i for i, (y, r) in enumerate(arm) if r > ARM_R + 1e-6 and y < 12.0)   # the iron band's first ring
    _paint(a, bands[k0 - 1] + bands[k0] + bands[k0 + 1], IRON)
    _paint(a, [fs[-1]], TIMBER_END)
    _reg("pole", "crossarm", vs)
    # X lashing: hull loops round the pole and arm in the planes z - zc = -+(y - py)
    c = Vector((px, py, ARM_ZC))
    pole_lines = _ngon(Vector((px, py, 0)), e1, e2, POLE_R, 8, math.pi / 8)
    arm_lines = _ngon(Vector((px, 0, ARM_ZC)), ex, ez, ARM_R, 6, math.pi / 6)
    for k, (sg, off) in enumerate(((1, RT_X - 0.02), (-1, RT_X - 0.02 + 2 * RT_X - 0.04))):
        m = Vector((0, sg, 1)).normalized()
        pts = [Vector((q.x, q.y, ARM_ZC - sg * (q.y - py))) for q in pole_lines]
        pts += [Vector((q.x, py - sg * (q.z - ARM_ZC), q.z)) for q in arm_lines]
        path = hull_loop(pts, c, m, Vector((1, 0, 0)), off, 8)
        rope(a, path, RT_X, 4, True, f"xlash_{k}", up=m)
    # sleeve hem round the arm (hex annulus)
    y0, y1, ro, ri = SLEEVE
    o0 = _ngon(Vector((px, y0, ARM_ZC)), ex, ez, ro, 6, math.pi / 6)
    o1 = _ngon(Vector((px, y1, ARM_ZC)), ex, ez, ro, 6, math.pi / 6)
    i0 = _ngon(Vector((px, y0, ARM_ZC)), ex, ez, ri, 6, math.pi / 6)
    i1 = _ngon(Vector((px, y1, ARM_ZC)), ex, ez, ri, 6, math.pi / 6)
    pts = o0 + o1 + i0 + i1
    faces = []
    for j in range(6):
        j1 = (j + 1) % 6
        faces += [[j, j1, 6 + j1, 6 + j], [12 + j1, 12 + j, 18 + j, 18 + j1], [j1, j, 12 + j, 12 + j1],
                  [6 + j, 6 + j1, 18 + j1, 18 + j]]
    hem = _mix(BANNER, IRON, 0.15)
    vs, _ = _shell(a, pts, faces, hem, _rt("sleeve", 0.02))
    _reg("banner", "sleeve", vs)
    zt_ = ARM_ZC - ro * math.cos(math.pi / 6) + 0.007
    ya, yb = y0 + 0.02, y1 - 0.02
    w = yb - ya
    zh = zt_ - 0.45
    outline = [(ya, zt_), (yb, zt_), (yb, zh), (yb, BAN_SIDE), (ya + 2 * w / 3, BAN_NOTCH), (ya + w / 2, BAN_TIP),
               (ya + w / 3, BAN_NOTCH), (ya, BAN_SIDE), (ya, zh)]
    body = [8, 2, 3, 4, 5, 6, 7]
    tris = [(0, 1, 2), (0, 2, 8)] + [tuple(body[k] for k in t) for t in _earclip([outline[i] for i in body])]
    n = len(outline)
    xa, xb = px - BAN_T / 2, px + BAN_T / 2
    pts = [Vector((xa, y, z)) for y, z in outline] + [Vector((xb, y, z)) for y, z in outline]
    faces = [list(t) for t in tris] + [[n + t[2], n + t[1], n + t[0]] for t in tris]
    for i in range(n):
        faces.append([i, (i + 1) % n, n + (i + 1) % n, n + i])
    vs, fs = _shell(a, pts, faces, BANNER, _rt("banner", 0.02))
    for f in fs:
        if f.calc_center_median().z > zh + 0.01:
            f.material_index = a._mi(_mix(BANNER, IRON, 0.10))
    _texture(a, vs, 0.02, 6831, scale=0.4)
    _reg("banner", "banner", vs)
    cy_, cz_ = (ya + yb) / 2, (zh + BAN_NOTCH) / 2 + 0.25
    for side in (-1, 1):
        emblem(a, cy_, cz_, px + side * BAN_T / 2, side)
    GEO["banner"] = {"w": round(w, 3), "top": round(zt_, 3), "tip": BAN_TIP, "emblem": [px, round(cy_, 3), round(cz_, 3)]}
    PART_INFO["banner_hang"] = Vector((px, py, POLE_TOP + 0.60))


def emblem(a, cy, cz, xf, side):
    """The white emblem on one banner face: a diamond ring slab, an inner diamond and two side points, each 0.005
    into the face and 0.015 proud."""
    x0, x1 = xf - side * 0.005, xf + side * EMB_T
    hw, hh = EMB_W / 2, EMB_H / 2
    k = EMB_S * math.hypot(hw, hh) / hw
    kx = EMB_S * math.hypot(hw, hh) / hh
    outer = [(cy, cz + hh), (cy + hw, cz), (cy, cz - hh), (cy - hw, cz)]
    inner = [(cy, cz + hh - k), (cy + hw - kx, cz), (cy, cz - hh + k), (cy - hw + kx, cz)]
    pts = [Vector((x0, y, z)) for y, z in outer + inner] + [Vector((x1, y, z)) for y, z in outer + inner]
    faces = []
    for i in range(4):
        i1 = (i + 1) % 4
        faces += [[i, i1, 4 + i1, 4 + i], [12 + i, 12 + i1, 8 + i1, 8 + i], [i1, i, 8 + i, 8 + i1],
                  [4 + i, 4 + i1, 12 + i1, 12 + i]]
    tag = "L" if side < 0 else "R"
    vs, _ = _shell(a, pts, faces, WHITE, _rt("emb" + tag, 0.02))
    _reg("emblem", f"emblem_{tag}", vs)
    for nm, (ey, ez, w2, h2) in (("in", (cy, cz, EMB_IW / 2, EMB_IH / 2)), ("dl", (cy - DOT_Y, cz, DOT_W / 2, DOT_H / 2)),
                                 ("dr", (cy + DOT_Y, cz, DOT_W / 2, DOT_H / 2))):
        d = [(ey, ez + h2), (ey + w2, ez), (ey, ez - h2), (ey - w2, ez)]
        vs, _, _, _ = _ext(a, d, lambda u, v, w: Vector((w, u, v)), min(x0, x1), max(x0, x1), WHITE,
                           _rt(nm + tag, 0.02))
        _reg("emblem", f"emblem_{tag}_{nm}", vs)


# ---- barrels, crate, stones (m064's shapes under this model's names, spec 2.9) -------------------------------------------
BARREL_R0, BARREL_R1, BARREL_H, HOOP = 1.00, 1.10, 2.80, 0.05
BARRELS = {"A": ((-9.20, 7.60), 0.0), "B": ((9.20, -5.60), 20.0)}
CRATE = {"c": (-9.10, 3.40), "rot": 8.0, "W": 2.30, "H": 2.20}
CR_FW, CR_RD, CR_PT, CR_PL, CR_PH, CR_BW, CR_BT = 0.24, 0.05, 0.04, 0.42, 0.32, 0.20, 0.05
STONES = {"S1": ((-9.00, 1.40), (1.10, 1.00, 0.90), 25.0, 681), "S2": ((3.60, -11.60), (0.90, 0.80, 0.70), 40.0, 682)}


def _R(c, rot_deg=0.0):
    return Matrix.Translation((c[0], c[1], 0)) @ Matrix.Rotation(math.radians(rot_deg), 4, "Z")


def barrel(a, c, rot_deg, tag):
    """(m064) A banded barrel: 8 staves (per-stave tint) bulging from 2.0 to 2.2, two iron hoops proud 0.05 (rings of
    the body), a pale grey lid inset 0.06 with an iron bung."""
    n = 8
    R = _R(c, rot_deg + 22.5)

    def r_at(z):
        return BARREL_R0 + (BARREL_R1 - BARREL_R0) * (1 - ((z - BARREL_H / 2) / (BARREL_H / 2)) ** 2)
    prof = [(0.0, 0), (0.20, 0), (0.20, 1), (0.43, 1), (0.43, 0), (BARREL_H / 2, 0), (2.37, 0), (2.37, 1),
            (2.60, 1), (2.60, 0), (BARREL_H, 0)]
    ang = [2 * math.pi * k / n for k in range(n)]
    rings = []
    for z, hoop in prof:
        r = r_at(z) + (HOOP if hoop else 0.0)
        rings.append([Vector((math.cos(t) * r, math.sin(t) * r, z)) for t in ang])
    rin = 0.88 * BARREL_R0
    rings.append([Vector((math.cos(t) * rin, math.sin(t) * rin, BARREL_H)) for t in ang])
    rings.append([Vector((math.cos(t) * rin, math.sin(t) * rin, BARREL_H - 0.06)) for t in ang])
    pts = [R @ p for r in rings for p in r]
    faces, keys, stave = [], [], []
    nr = len(prof)
    for i in range(nr - 1):
        hoop = prof[i][1] or prof[i + 1][1]
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, (i + 1) * n + j1, (i + 1) * n + j])
            keys.append(IRON if hoop else TIMBER)
            stave.append(j)
    for i in (nr - 1, nr):
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, (i + 1) * n + j1, (i + 1) * n + j])
            keys.append(_mix(TIMBER, TIMBER_DEEP, 0.4) if i == nr else TIMBER)
            stave.append(j)
    faces.append([(nr + 1) * n + j for j in range(n)])
    keys.append("lid")
    stave.append(-1)
    faces.append(list(reversed(range(n))))
    keys.append(TIMBER)
    stave.append(-1)
    vs, fs = _shell(a, pts, faces, TIMBER, 1.0)
    rng = random.Random(_seed(tag))
    st = [1.0 + rng.uniform(-0.06, 0.06) for _ in range(n)]
    lid_key = _mix(IRON, WHITE, 0.6)
    for f, k, s_ in zip(fs, keys, stave):
        if k == "lid":
            f.material_index = a._mi(lid_key)
        elif k != TIMBER:
            f.material_index = a._mi(k)
        if s_ >= 0 and k == TIMBER:
            _tint(a, [f], st[s_])
    _reg("barrel", f"barrel_{tag}", vs)
    bc = R @ Vector((0.35, -0.25, BARREL_H - 0.06))
    br = 0.175
    bp = [Vector((bc.x + math.cos(2 * math.pi * k / 6) * br, bc.y + math.sin(2 * math.pi * k / 6) * br, bc.z + z))
          for z in (0.003, 0.09) for k in range(6)]
    bfa = [list(reversed(range(6))), list(range(6, 12))] + [[k, (k + 1) % 6, 6 + (k + 1) % 6, 6 + k] for k in range(6)]
    vs, _ = _shell(a, bp, bfa, IRON, 0.95)
    _reg("bung", f"barrel_{tag}_bung", vs)


def crate(a, c=None, rot=None):
    """(m064) Storage crate: a box whose four sides have a 0.24 frame round a panel recessed 0.05, an X brace of three
    boards on each panel, a plank lid (two seams), dark iron L plates at the eight corners."""
    cx, cy = c or CRATE["c"]
    R = _R((cx, cy), rot if rot is not None else CRATE["rot"])
    W, H = CRATE["W"], CRATE["H"]
    h = W / 2
    cor = [Vector((-h, -h, 0)), Vector((h, -h, 0)), Vector((h, h, 0)), Vector((-h, h, 0)),
           Vector((-h, -h, H)), Vector((h, -h, H)), Vector((h, h, H)), Vector((-h, h, H))]
    pts = list(cor)
    faces, keys = [], []
    frame_key = TIMBER
    panel_key = _mix(TIMBER, TIMBER_DEEP, 0.5)
    s1, s2 = -W / 6, W / 6
    f1 = len(pts)
    pts += [Vector((s1, -h, H)), Vector((s2, -h, H)), Vector((s2, h, H)), Vector((s1, h, H))]
    faces += [[4, f1, f1 + 3, 7], [f1, f1 + 1, f1 + 2, f1 + 3], [f1 + 1, 5, 6, f1 + 2]]
    keys += ["lid0", "lid1", "lid2"]
    faces.append([3, 2, 1, 0])
    keys.append(panel_key)
    sides = [((0, 1, 5, 4), [f1 + 1, f1], Vector((0, -1, 0))), ((1, 2, 6, 5), [], Vector((1, 0, 0))),
             ((2, 3, 7, 6), [f1 + 3, f1 + 2], Vector((0, 1, 0))), ((3, 0, 4, 7), [], Vector((-1, 0, 0)))]
    panels = []
    for (b0, b1, t1, t0), extra, nrm in sides:
        P0, P1, P2, P3 = pts[b0], pts[b1], pts[t1], pts[t0]
        U = (P1 - P0).normalized()
        V = Vector((0, 0, 1))
        q = [P0 + U * CR_FW + V * CR_FW, P1 - U * CR_FW + V * CR_FW, P2 - U * CR_FW - V * CR_FW,
             P3 + U * CR_FW - V * CR_FW]
        qi = len(pts)
        pts += q
        ri = len(pts)
        pts += [p - nrm * CR_RD for p in q]
        faces.append([b0, b1, qi + 1, qi])
        faces.append([b1, t1, qi + 2, qi + 1])
        faces.append([t1] + extra + [t0, qi + 3, qi + 2])
        faces.append([t0, b0, qi, qi + 3])
        keys += [frame_key] * 4
        for k in range(4):
            k1 = (k + 1) % 4
            faces.append([qi + k, qi + k1, ri + k1, ri + k])
            keys.append(panel_key)
        faces.append([ri, ri + 1, ri + 2, ri + 3])
        keys.append(panel_key)
        panels.append((q, nrm, U))
    pts = [R @ p for p in pts]
    vs, fs = _shell(a, pts, faces, TIMBER, 1.0)
    rng = random.Random(6840)
    for f, k in zip(fs, keys):
        if k.startswith("lid"):
            _tint(a, [f], 1.0 + (0.06, -0.05, 0.03)[int(k[-1])])
        elif k != TIMBER:
            f.material_index = a._mi(k)
            _tint(a, [f], 1.0 + rng.uniform(-0.04, 0.04))
    _reg("crate", "crate_body", vs)
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
        vs, _ = _shell(a, hexa2d([(p.x, p.y) for p in quadA]), HEXA, frame_key, _rt(f"crA{si}", 0.04))
        _reg("plank", f"crate_A{si}", vs)
        for hi, sg in enumerate((1, -1)):
            sgnA = 1 if nA.dot(dB * sg) > 0 else -1
            corners = []
            for e in (-1, 1):
                t_in = (sgnA * hw - e * hw * nA.dot(nB)) / nA.dot(dB)
                corners.append((dB * t_in + nB * (e * hw), dB * (sg * LB) + nB * (e * hw)))
            quad = [corners[0][0], corners[0][1], corners[1][1], corners[1][0]]
            vs, _ = _shell(a, hexa2d([(p.x, p.y) for p in quad]), HEXA, frame_key, _rt(f"crB{si}{hi}", 0.04))
            _reg("plank", f"crate_B{si}_{hi}", vs)
    g = 0.004
    for ci, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        for zi, (z0, z1) in enumerate(((0.0, CR_PH), (H - CR_PH, H))):
            ox, oy = sx * (h + g), sy * (h + g)
            L2 = [(ox + sx * CR_PT, oy - sy * CR_PL), (ox + sx * CR_PT, oy + sy * CR_PT), (ox - sx * CR_PL, oy + sy * CR_PT),
                  (ox - sx * CR_PL, oy), (ox, oy), (ox, oy - sy * CR_PL)]
            area = sum(L2[i][0] * L2[(i + 1) % 6][1] - L2[(i + 1) % 6][0] * L2[i][1] for i in range(6))
            if area < 0:
                L2 = L2[::-1]
            ppts = [R @ Vector((x, y, z0)) for x, y in L2] + [R @ Vector((x, y, z1)) for x, y in L2]
            pf = [list(reversed(range(6))), list(range(6, 12))]
            for i in range(6):
                pf.append([i, (i + 1) % 6, 6 + (i + 1) % 6, 6 + i])
            vs, _ = _shell(a, ppts, pf, IRON, _rt(f"pl{ci}{zi}", 0.04))
            _reg("cplate", f"crate_plate{ci}{zi}", vs)


def stone(a, c, size, rot_deg, seed, tag):
    """(m064) A chunky pale faceted block: a box with two top corners broken off, a flat bottom; its lowest 30 %
    one step toward stone (by height)."""
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
    vs, fs = _hull(a, pts, STONE_LIGHT, _rt(tag, 0.03))
    for f in fs:
        if f.is_valid and f.calc_center_median().z < 0.30 * sz:
            f.material_index = a._mi(_mix(STONE_LIGHT, STONE, 0.5))
    _texture(a, vs, 0.05, seed, scale=1.2)
    _reg("pstone", f"stone_{tag}", vs)


# ---- hero assembly (spec 4.1 item 15) -------------------------------------------------------------------------------------
def hero_all(a):
    """TimberCabin: every part function placed by spec 2 (leaf open inward), one object of closed shells."""
    _clear()
    GEO.clear()
    FX.clear()
    for side in RUNS:
        foundation_run(a, side)
    for sx in (-1, 1):
        for sy in (-1, 1):
            corner_block(a, sx, sy)
            corner_post(a, sx, sy)
    floor(a)
    for s in (-1, 1):
        wall_long(a, s)
        window(a, s)
        plate(a, s)
        for e in (-1, 1):
            bracket_plate(a, s, e)
        for y in RAFTER_Y:
            rafter(a, s, y)
        purlins(a, s)
        eave_block(a, s)
    wall_end(a, -1, door=True)
    wall_end(a, 1)
    back_frame_posts(a)
    for e in (-1, 1):
        gable_frame(a, e)
        gable_infill(a, e)
    doorframe(a, OPEN_DEG)
    trimmers(a)
    ridge_beam(a)
    roof_panel(a, -1)
    roof_panel(a, 1, hole=True)
    ties(a, -1)
    ties(a, 1)
    chimney(a)
    FX.append(("chimney_smoke", Vector(GEO["flue"]), SMOKE))
    stairs(a)
    gc, _ = lantern_set(a, "eave", L1, "L1")
    FX.append(("heat_glow", gc, _fx_spec(10)))
    for tag, base in zip(("L2", "L3"), L23):
        gc, _ = lantern_set(a, "door", base, tag)
        FX.append(("heat_glow", gc, _fx_spec(12)))
    banner_set(a)
    for tag, (c, rot) in BARRELS.items():
        barrel(a, c, rot, tag)
    crate(a)
    for tag, (c, size, r, seed) in STONES.items():
        stone(a, c, size, r, seed, tag)


# ---- parts (spec 8; each from the same part functions, square to its axes) -------------------------------------------------
def roof_part(a):
    """TimberCabinRoofPanel: the +X canvas slab (uncut) with its four U ties clipped round the canvas edge (the hero's
    ties run on round the plate, which is not in this part; the left slope is this mesh mirrored)."""
    _clear()
    roof_panel(a, 1)
    ties(a, 1, short=True)


def ridge_part(a):
    _clear()
    ridge_beam(a)


def chimney_part(a):
    _clear()
    chimney(a)
    PART_INFO["flue"] = Vector(GEO["flue"])


def banner_part(a):
    _clear()
    banner_set(a)


def lantern_part(a):
    """TimberCabinLantern: one door lantern with its wall bracket (the strap's back face is the wall face)."""
    _clear()
    gc, rt = lantern_set(a, "door", (0.0, -9.10, 6.20), "L")
    PART_INFO["glass"] = gc
    PART_INFO["hang"] = rt
    PART_INFO["mount"] = Vector((0.0, -(WALL_IN_Y + WALL_T + 0.003), (ARM_Z[0] - 0.10 + PLATE[2]) / 2))


def wall_part(a):
    """TimberCabinWallPanel: the back wall's five plank rows between its two corner posts."""
    _clear()
    wall_end(a, 1)
    for sx in (-1, 1):
        corner_post(a, sx, 1)


def window_part(a):
    """TimberCabinWindowWall: the +X long wall with its window between its two corner posts."""
    _clear()
    wall_long(a, 1)
    window(a, 1)
    for sy in (-1, 1):
        corner_post(a, 1, sy)


def door_part(a):
    """TimberCabinDoorFrame: door posts with caps, lintel, header and the leaf closed (hinge stored)."""
    _clear()
    doorframe(a, 0.0)
    PART_INFO["hinge"] = GEO["hinge"]


def gable_part(a):
    _clear()
    gable_frame(a, -1, part=True)


def floor_part(a):
    _clear()
    floor(a, feet=True)


def stairs_part(a):
    _clear()
    stairs(a)


def foundation_part(a):
    """TimberCabinFoundation: the +X side's two-course run with its back corner block."""
    _clear()
    foundation_run(a, "R")
    corner_block(a, 1, 1)


NOTES = {
    HERO: "Walk-in gable-roofed timber cabin (door 3.60 x 7.00 clear on a 2.60 floor, three 0.87 risers): two-course "
          "stone plinth with white corner blocks, plank floor, five rows of planks between chamfered corner posts, "
          "a barred window in each long wall, the door between tall posts with golden caps under a lintel and collar "
          "(leaf open inward 95 deg), octagonal-ended eave beams with iron brackets, rafters, purlins and a ridge "
          "beam under two closed cream canvas slabs with golden U ties, crossed bargeboards with golden saddles, a "
          "stone chimney (thin pale chimney_smoke), two-tread stairs, three Neon lanterns (heat_glow halos), a red "
          "banner on an X-lashed pole, two barrels, a crate and two stones. Collision precise: Requires Manual "
          "Validation in Studio (walk in, turn round, walk out). Sheet header 67/132.",
    ROOF_P: "Roof Panel (Left / Right): one closed 0.12 canvas slab, 5 x 2 sagging panels, four golden U ties "
            "(mirror for the other slope)",
    RIDGE_P: "Ridge Beam: 1.00 beam with a pitched top, pale octagonal ends and two golden rope turns at each end",
    CHIMNEY_P: "Chimney: square stone stack in two blocks with a notched joint, a flued cap (chimney_smoke socket); "
               "its foot is cut to the 32 deg roof pitch",
    BANNER_P: "Banner Pole + Banner: 8-sided pole with a golden foot band and block top, crossarm with an X lashing, "
              "red swallowtail banner with the white diamond emblem on both faces",
    LANTERN_P: "Lantern (x2): square dark-iron lantern with Neon amber glass (heat_glow halo) on its iron wall bracket",
    WALL_P: "Wall Panel (Left / Rear): five rows of 0.40 V-seamed planks with staggered joints between two corner "
            "posts",
    WINDOW_P: "Wall Panel with window: a long plank wall with the centred barred window frame and its corner posts",
    DOOR_P: "Doorframe: two chamfered door posts on golden caps, lintel, header plank and the plank door (closed; "
            "hinge stored as m068_hinge for a scripted door)",
    GABLE_P: "Front Gable Frame: collar, crossed bargeboards (half-lap X) with a golden saddle, on the two plate ends",
    FLOOR_P: "Floor: ten deck planks and the threshold on short dark feet (top 2.60)",
    STAIRS_P: "Stairs: two two-plank treads on blocks (three equal 0.87 risers to a 2.60 floor)",
    FOUND_P: "Stone Foundation (x4): one side's two-course run of bevelled blocks with a two-tier corner block",
}
COLLISION = {HERO: "precise", ROOF_P: "box", RIDGE_P: "box", CHIMNEY_P: "box", BANNER_P: "none", LANTERN_P: "none",
             WALL_P: "box", WINDOW_P: "precise", DOOR_P: "precise", GABLE_P: "hull", FLOOR_P: "box",
             STAIRS_P: "precise", FOUND_P: "box"}


# ---- objects, stage 2-3 pass (m066) ------------------------------------------------------------------------------------------
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
    o["m068_pieces"] = json.dumps([[k, n_, [round(x, 5) for x in c]] for k, n_, c in PIECES])
    o["m068_ropes"] = json.dumps(ROPES)
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


# ---- checks (m064 / m066) --------------------------------------------------------------------------------------------------
CAT = {"plank": "wood", "beam": "wood", "frame": "wood", "post": "wood", "peg": "wood", "board": "wood",
       "door": "wood", "pole": "wood", "barrel": "wood", "crate": "wood", "stone": "stone", "corner": "stone",
       "chimney": "stone", "pstone": "stone", "bar": "metal", "iron": "metal", "lmetal": "metal", "bung": "metal",
       "cplate": "metal", "canvas": "canvas", "rope": "rope", "glass": "glass", "banner": "banner",
       "emblem": "banner"}
SINK_LIMIT = {("rope", "rope"): 0.08}
THIN_KINDS = ("canvas", "banner", "emblem")


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
    reg = [(k, nm, Vector(c)) for k, nm, c in json.loads(o.get("m068_pieces", "[]"))]
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


def winding_parity(o):
    """Spec 4.5: per shell, faces whose normal points inward by a ray-parity test (a point just off the face along
    its normal must be outside the shell). Returns {shell name: count} for shells with any."""
    bm, ids, n, groups, labels = _shells(o)
    out = {}
    for k in range(n):
        fs = groups[k]
        vs = list({v for f in fs for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        bad = 0
        for f in fs:
            if f.calc_area() < 1e-5:
                continue
            p = f.calc_center_median() + f.normal * 1e-3
            bad += _parity_in(tree, p)
        if bad:
            out[f"{labels[k][1]}#{k}"] = bad
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
    """(m064) Thin slabs hide pass-throughs from the bury report (the 0.12 canvas is at most 0.06 deep anywhere):
    count the edges of every other shell that cross a thin surface (canvas, banner, emblem) twice."""
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
    """(m064) Every open rope / strap touches what it ties at both ends: each end point's gap to the nearest other
    shell (surface distance minus the rope radius, 0 when the end is inside another shell)."""
    bm, ids, n, groups, labels = _shells(o)
    off = Vector(o[OFF])
    fsh = [ids[f.index] for f in bm.faces]
    tree = BVHTree.FromBMesh(bm)
    byname = {labels[k][1]: k for k in range(n)}
    out, bad = {}, []
    for r in json.loads(o.get("m068_ropes", "[]")):
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


def _hero_tree(o, skip=lambda kind, name: False):
    """BVH of the hero's shells in the build frame (skip(kind, name) leaves a shell out); owner name per polygon."""
    bm, ids, n, groups, labels = _shells(o)
    off = Vector(o[OFF])
    cos, polys, owner = [], [], []
    for k in range(n):
        if skip(*labels[k]):
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


def _boxes(o):
    """Per named shell: [lo, hi] in the build frame."""
    bm, ids, n, groups, labels = _shells(o)
    off = Vector(o[OFF])
    out = {}
    for k in range(n):
        co = [v.co + off for v in {v for f in groups[k] for v in f.verts}]
        out[labels[k][1]] = [Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co))),
                             Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co)))]
    bm.free()
    return out


PROXY = ((1.0, 0.5, 0.0, 4.4), (0.55, 0.5, 4.4, 5.5))     # (half x, half y, z0, z1): body, head (spec 2.10)
WALK_Y = (-15.0, 0.0)
WALK_LIFT = 0.10                                           # proxy feet above the surface it stands on
FLOOR_NAMES = ("tread", "deck_", "thresh_", "floor_under")     # the underlay lies under the deck


def _proxy_samples(yaw=0.0):
    R = Matrix.Rotation(math.radians(yaw), 3, "Z")
    out = []
    for hx, hy, z0, z1 in PROXY:
        for i in range(9):
            for j in range(9):
                u, w = -1 + 2 * i / 8, -1 + 2 * j / 8
                z = z0 + (z1 - z0) * j / 8
                out += [R @ Vector((hx * u, -hy, z)), R @ Vector((hx * u, hy, z)), R @ Vector((-hx, hy * u, z)),
                        R @ Vector((hx, hy * u, z)), R @ Vector((hx * u, hy * w, z1))]
    return out


def walk_report(o):
    """Spec 2.10: a 5.5 proxy (2 x 1 body to 4.4, a 1.1-wide head to 5.5) walks from (0, -15) up the stairs, over the
    threshold, through the doorway to (0, 0) and turns round there. Its feet ride WALK_LIFT above the highest surface
    under its footprint; the clearance is the nearest hero surface that is not a walking surface (treads, deck,
    threshold). Also the riser heights met on the way, the door's clear width and height, the interior's lowest
    overhead member and the lanterns' bottoms."""
    tree, owner = _hero_tree(o)
    skip_floor = lambda kind, name: name.startswith(FLOOR_NAMES)
    ctree, cown = _hero_tree(o, skip_floor)
    samples = _proxy_samples()
    feet = [Vector((x, y, 0)) for x in (-0.95, 0.0, 0.95) for y in (-0.45, 0.0, 0.45)]

    def base_at(x, y):
        z = 0.0
        for f in feet:
            h = tree.ray_cast(Vector((x + f.x, y + f.y, 8.0)), Vector((0, 0, -1)), 9.0)
            if h[0] is not None:
                z = max(z, h[0].z)
        return z
    worst, at, who, prof = 9.0, None, None, []
    steps = int((WALK_Y[1] - WALK_Y[0]) / 0.1)
    for s in range(steps + 1):
        y = WALK_Y[0] + 0.1 * s
        zb = base_at(0.0, y)
        if not prof or abs(prof[-1][1] - zb) > 1e-3:
            prof.append((round(y, 2), round(zb, 3)))
        for p0 in samples:
            p = p0 + Vector((0.0, y, zb + WALK_LIFT))
            loc, nrm, fi, d = ctree.find_nearest(p)
            if loc is not None and d < worst:
                worst, at, who = d, round(y, 2), cown[fi]
    turn = (9.0, None, None)
    zb = base_at(0.0, 0.0)
    for yaw in range(0, 181, 15):
        for p0 in _proxy_samples(yaw):
            loc, nrm, fi, d = ctree.find_nearest(p0 + Vector((0, 0, zb + WALK_LIFT)))
            if loc is not None and d < turn[0]:
                turn = (d, yaw, cown[fi])
    rises = [round(prof[i][1] - prof[i - 1][1], 3) for i in range(1, len(prof))]
    # door clear width (horizontal rays both ways from the centre line) and height (ray up), at the posts' plane and
    # the wall plane
    door = {}
    for nm, y in (("posts", -8.95), ("wall", -7.80)):
        widths = []
        for k in range(14):
            z = FLOOR_Z + 0.05 + k * 0.5
            hl = ctree.ray_cast(Vector((0, y, z)), Vector((-1, 0, 0)), 20.0)
            hr = ctree.ray_cast(Vector((0, y, z)), Vector((1, 0, 0)), 20.0)
            if hl[0] is not None and hr[0] is not None:
                widths.append(hr[0].x - hl[0].x)
        up = ctree.ray_cast(Vector((0, y, FLOOR_Z + 0.02)), Vector((0, 0, 1)), 20.0)
        door[nm] = {"min_width": round(min(widths), 3) if widths else None,
                    "clear_height": round(up[0].z - FLOOR_Z, 3) if up[0] is not None else None,
                    "head": cown[up[2]] if up[0] is not None else None}
    # interior: the lowest member over the floor (rays up from 0.05 above the deck, the open leaf left out)
    itree, iown = _hero_tree(o, lambda kind, name: name.startswith(("leaf_", "post_")) or skip_floor(kind, name))
    low, low_at, low_who = 99.0, None, None
    x = -WALL_IN_X + 0.2
    while x <= WALL_IN_X - 0.2 + 1e-6:
        y = -WALL_IN_Y + 0.2
        while y <= WALL_IN_Y - 0.2 + 1e-6:
            h = itree.ray_cast(Vector((x, y, FLOOR_Z + 0.05)), Vector((0, 0, 1)), 30.0)
            if h[0] is not None and h[0].z < low:
                low, low_at, low_who = h[0].z, (round(x, 2), round(y, 2)), iown[h[2]]
            y += 0.4
        x += 0.4
    lan = GEO.get("lanterns", {})
    return {"min_clearance": round(worst, 3), "at_y": at, "nearest": who,
            "turn_min_clearance": round(turn[0], 3), "turn_yaw": turn[1], "turn_nearest": turn[2],
            "surface_profile": prof, "rises": rises, "door": door,
            "interior_overhead_min": round(low, 3), "overhead_above_floor": round(low - FLOOR_Z, 3),
            "overhead_at": low_at, "overhead_member": low_who,
            "lantern_bottoms": {k: v["bottom"] for k, v in lan.items()}}


ESC_PLANES = {"R": (0, 1), "L": (0, -1), "B": (1, 1), "F": (1, -1)}     # wall: (axis, sign) of its outward normal
ESC_ALLOWED = ("door",)


def _fib(n, lower=False):
    """n unit directions spread evenly over the sphere (lower: over the lower hemisphere)."""
    ga = math.pi * (3.0 - math.sqrt(5.0))
    out = []
    for i in range(n):
        z = -(i + 0.5) / n if lower else 1.0 - 2.0 * (i + 0.5) / n
        r = math.sqrt(max(0.0, 1.0 - z * z))
        out.append(Vector((r * math.cos(ga * i), r * math.sin(ga * i), z)))
    return out


def _leak_where(p, d):
    """Where an escaping ray (it hit nothing) leaves the hut's envelope: the walls' outer planes (|x| 7.00, |y|
    8.00), the floor's underside (z 2.30) or the canvas top. Returns (region, point)."""
    t = 0.0
    while t < 40.0:
        q = p + d * t
        if abs(q.x) < DOOR_X and -(WALL_IN_Y + WALL_T) < q.y < -WALL_IN_Y and FLOOR_Z < q.z < DOOR_TOP:
            return "door", q                                # through the doorway in the wall plane
        if q.z < 2.30:
            return "floor", q
        if q.z > zt(q.x) + 0.02:
            return "roof", q
        if q.y < -(WALL_IN_Y + WALL_T):
            if abs(q.x) < DOOR_X + 0.05 and q.z < DOOR_TOP + 0.05:      # (one 0.01 march step of slack)
                return "door", q
            return ("gable_F" if q.z > PLATE[2] else "wall_F"), q
        if q.y > WALL_IN_Y + WALL_T:
            return ("gable_B" if q.z > PLATE[2] else "wall_B"), q
        if abs(q.x) > WALL_IN_X + WALL_T:
            s = "R" if q.x > 0 else "L"
            if abs(q.y) < WIN[0] and WIN[1] < q.z < WIN[2]:
                return "window_" + s, q
            return ("eave_" if q.z > PLATE[2] else "wall_") + s, q
        t += 0.01
    return "far", p + d * t


def escape_report(o, n_dirs=320, step=0.10, offs=(-0.0007, 0.0007)):
    """Inside escape scan (round 1 blocker): rays that leave the room without hitting anything, by where they leave.
    1. Rays in n_dirs directions from a grid of points inside the room and up into the roof space (each at least
       0.15 off every surface).
    2. The same from just above the floor (z 2.65), the lower hemisphere only.
    3. Seam rays: through every wall, the gables and the floor, along lines at each distinct vertex coordinate of the
       pieces in that plane (where joints between shells lie) +- 0.0007, square to the plane and slanted along the
       seam.
    4. Rays over the upper hemisphere from a 0.04 grid of points just under the canvas round the chimney's cut.
    Only the door opening may let rays out."""
    tree, owner = _hero_tree(o)
    off = Vector(o[OFF])
    bm = bmesh.new()
    bm.from_mesh(o.data)
    vco = [v.co + off for v in bm.verts]
    bm.free()
    out = {"rays": 0, "escapes": {}, "examples": {}}

    def cast(p, d):
        out["rays"] += 1
        if tree.ray_cast(p, d, 200.0)[0] is not None:
            return
        reg, q = _leak_where(p, d)
        out["escapes"][reg] = out["escapes"].get(reg, 0) + 1
        ex = out["examples"].setdefault(reg, [])
        if len(ex) < 6:
            ex.append([round(c, 3) for c in q])
    # 1-2: interior points
    dirs, down = _fib(n_dirs), _fib(n_dirs // 2, lower=True)
    pts = []
    for i in range(9):
        x = -6.30 + 12.6 * i / 8
        for j in range(9):
            y = -7.30 + 14.6 * j / 8
            for z in (3.2, 4.6, 6.0, 7.4, 8.8, 10.2, 11.6, 13.0, 14.4):
                if z < zu(x) - 0.25:
                    pts.append(Vector((x, y, z)))
    pts = [p for p in pts if tree.find_nearest(p)[3] > 0.15]
    for p in pts:
        for d in dirs:
            cast(p, d)
    for i in range(13):
        for j in range(15):
            p = Vector((-6.30 + 12.6 * i / 12, -7.30 + 14.6 * j / 14, FLOOR_Z + 0.05))
            if tree.find_nearest(p)[3] > 0.02:
                for d in down:
                    cast(p, d)
    # 3: seam rays
    def coords(sel, k):
        return sorted({round(c[k], 4) for c in vco if sel(c)})
    for wall, (ax, sg) in ESC_PLANES.items():
        inner = WALL_IN_X if ax == 0 else WALL_IN_Y
        along = 1 - ax                                    # in-plane horizontal axis (y for long walls, x for ends)
        half = WALL_IN_Y if ax == 0 else WALL_IN_X
        sel = lambda c, ax=ax, sg=sg, inner=inner: inner - 0.05 <= sg * c[ax] <= inner + WALL_T + 0.05
        zs = [z for z in coords(sel, 2) if FLOOR_Z - 0.4 < z < 16.0]
        ts = [t for t in coords(sel, along) if abs(t) < half + 0.3]
        n = Vector((0, 0, 0))
        n[ax] = sg

        def start(t, z):
            p = Vector((0, 0, z))
            p[ax] = sg * (inner - 0.30)
            p[along] = t
            return p
        top = lambda t: zu(t) - 0.05 if ax == 1 else zu(inner) - 0.05
        sl = Vector((0, 0, 0))
        sl[along] = 0.5
        for zc in zs:                                     # horizontal seams: square and slanted along the seam
            for dz in offs:
                z = zc + dz
                t = -half
                while t <= half:
                    if FLOOR_Z < z < top(t):
                        for d in (n, (n + sl).normalized(), (n - sl).normalized()):
                            cast(start(t, z), d)
                    t += step
        up = Vector((0, 0, 0.5))
        for tc in ts:                                     # vertical seams
            for dt in offs:
                t = tc + dt
                z = FLOOR_Z + 0.02
                while z < top(t):
                    for d in (n, (n + up).normalized(), (n - up).normalized()):
                        cast(start(t, z), d)
                    z += step
    sel = lambda c: abs(c[0]) < WALL_IN_X and abs(c[1]) < WALL_IN_Y + 0.1 and 1.6 < c[2] < FLOOR_Z + 0.01
    for ax in (0, 1):                                     # floor seams: rays down along both deck axes
        along = 1 - ax
        half_a, half_b = (WALL_IN_X, WALL_IN_Y) if ax == 0 else (WALL_IN_Y, WALL_IN_X)
        sl = Vector((0, 0, 0))
        sl[along] = 0.5
        dn = Vector((0, 0, -1))
        for c in coords(sel, ax):
            if abs(c) > half_a:
                continue
            for dc in offs:
                u = -half_b + 0.02
                while u < half_b:
                    p = Vector((0, 0, FLOOR_Z + 0.05))
                    p[ax] = c + dc
                    p[along] = u
                    for d in (dn, (dn + sl).normalized(), (dn - sl).normalized()):
                        cast(p, d)
                    u += step
    # 4: round the chimney's cut: points 0.03 under the canvas within 0.3 of the cut, rays over the upper hemisphere
    x0, x1, y0, y1 = HOLE
    ups = [-d for d in _fib(48, lower=True)]
    u = x0 - 0.30
    while u <= x1 + 0.30:
        v = y0 - 0.30
        while v <= y1 + 0.30:
            inside = x0 + 0.30 < u < x1 - 0.30 and y0 + 0.30 < v < y1 - 0.30
            if not inside:
                p = Vector((u, v, zu(u) - 0.03))
                if tree.find_nearest(p)[3] > 0.004:
                    for d in ups:
                        cast(p, d)
            v += 0.04
        u += 0.04
    leaks = {k: v for k, v in out["escapes"].items() if k not in ESC_ALLOWED}
    out["points"] = len(pts)
    out["leaks"] = sum(leaks.values())
    out["leak_regions"] = leaks
    return out


def placement_report(o):
    """Measured targets (spec 4.4): floor, plates, ridge, chimney, walls, bargeboards, ridge-beam ends, stairs,
    lanterns, banner, extents, all from the built shells in the build frame."""
    B = _boxes(o)

    def mx(prefix, k, hi=True):
        vals = [(b[1] if hi else b[0])[k] for nm, b in B.items() if nm.startswith(prefix)]
        return round(max(vals) if hi else min(vals), 3) if vals else None
    deck = [round(b[1].z, 3) for nm, b in B.items() if nm.startswith(("deck_", "thresh_"))]
    posts = [b for nm, b in B.items() if nm.startswith("post_")]
    out = {"floor_top": [min(deck), max(deck)] if deck else None,
           "plate_top": mx("plate_", 2), "canvas_top": mx("canvas_", 2), "canvas_eave_x": mx("canvas_R", 0),
           "chimney_top": mx("chim_cap", 2), "chimney_foot": GEO.get("chimney_foot"),
           "walls": [round(max(b[1].x for b in posts) - min(b[0].x for b in posts), 3),
                     round(max(b[1].y for b in posts) - min(b[0].y for b in posts), 3)] if posts else None,
           "pitch_deg": PITCH, "bargeboard_tip_top": mx("bb_", 2),
           "tips_above_apex": round(mx("bb_", 2) - RIDGE_Z, 3) if mx("bb_", 2) else None,
           "ridge_beam_y": [mx("ridge", 1, False), mx("ridge", 1)],
           "ridge_past_bargeboards": round(RIDGE_END - BB_Y[1], 3),
           "lintel_underside": mx("lintel", 2, False), "risers": GEO.get("risers"),
           "lanterns": GEO.get("lanterns"), "banner": GEO.get("banner"), "flue": GEO.get("flue"),
           "size": [round(d, 3) for d in o.dimensions]}
    return out


# ---- build -----------------------------------------------------------------------------------------------------------------
PARTS = ((ROOF_P, roof_part), (RIDGE_P, ridge_part), (CHIMNEY_P, chimney_part), (BANNER_P, banner_part),
         (LANTERN_P, lantern_part), (WALL_P, wall_part), (WINDOW_P, window_part), (DOOR_P, door_part),
         (GABLE_P, gable_part), (FLOOR_P, floor_part), (STAIRS_P, stairs_part), (FOUND_P, foundation_part))
# hero W (X), D (Y), H (Z) +- tolerance: spec 2.11's 20.6 x 26.1 x 19.4 with the ruled banner pole (-9.55, 10.55),
# whose crossarm now ends at y 13.80
TARGET_SIZE = ((20.7, 0.4), (26.5, 0.5), (19.4, 0.2))
HERO_BUDGET = 8000
THIN_FLOOR = 0.3
SEATS = [("post_LF", "corner_LF_top"), ("plate_L", "post_LF"), ("plate_R", "post_RB"), ("collar_F", "lintel"),
         ("lintel", "dpost_L"), ("header", "lintel"), ("bb_F_A", "plate_L"), ("bb_F_B", "plate_R"),
         ("saddle_F", "bb_F_A"), ("ridge", "bb_F_A"), ("rafter_L-1.94", "plate_L"), ("canvas_L", "rafter_L-1.94"),
         ("canvas_R", "ridge"), ("tie_L0", "canvas_L"), ("tie_L0", "plate_L"), ("bplate_LF", "plate_L"),
         ("bpeg_LF", "bplate_LF"), ("trimmer_0", "rafter_R-1.94"), ("chim_lo", "trimmer_0"),
         ("chim_lo", "trimmer_1"), ("L1_hook", "L1_ring"), ("L1_strap", "plate_L"), ("L2_strap", "pl_F4_0"),
         ("crossarm", "pole"), ("sleeve", "crossarm"), ("banner", "sleeve"), ("thresh_beam", "dpost_L"),
         ("deck_1", "floor_under"), ("floor_under", "sleeper_0"), ("leaf_plank0", "deck_3"), ("tread0_1", "dpost_L"),
         ("eaveblk_L", "plate_L"), ("eaveblk_L", "canvas_L"), ("shutter_L0", "pl_L2_1"), ("shutter_R1", "shutter_R0"),
         ("cleat_FL0", "bb_F_A"), ("cleat_BR1", "bb_B_B"), ("gboard_F_apex", "ridge"), ("gboard_BL5", "plate_L")]
LANTERN_MIN = {"L1": 6.3, "L2": 6.0, "L3": 6.0}


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m068_")]
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
        out[o.name] = {"vfx_sockets": len(socks), "kinds": sorted(c["vfx_kind"] for c in socks), "glow_keys": glow}
    return out


def _rel(p, o):
    return [round(x, 3) for x in Vector(p) - Vector(o[OFF])]


def _store(h, objs):
    h["m068_centre"] = _rel((0.0, 0.0, FLOOR_Z), h)
    h["m068_door"] = {"threshold": _rel((0.0, -(WALL_IN_Y + WALL_T), FLOOR_Z), h), "facing": [0.0, -1.0, 0.0]}
    hg = GEO["hinge"]
    h["m068_hinge"] = {"axis_bottom": _rel(hg["axis_bottom"], h), "closed_yaw": hg["closed_yaw"],
                       "open_yaw": hg["open_yaw"]}
    h["m068_chimney"] = _rel(GEO["flue"], h)
    if DOOR_P in objs:
        dp = objs[DOOR_P]
        hg = PART_INFO["hinge"]
        dp["m068_hinge"] = {"axis_bottom": _rel(hg["axis_bottom"], dp), "closed_yaw": hg["closed_yaw"],
                            "open_yaw": hg["open_yaw"]}
    if LANTERN_P in objs:
        lp = objs[LANTERN_P]
        lp["m068_hang"] = _rel(PART_INFO["hang"], lp)
        lp["m068_mount"] = _rel(PART_INFO["mount"], lp)
        for c in [c for c in lp.children if c.get("vfx_kind")]:
            bpy.data.objects.remove(c, do_unlink=True)
        K.socket(lp, "heat_glow", Vector(_rel(PART_INFO["glass"], lp)), **_fx_spec(12))
    if CHIMNEY_P in objs:
        cp = objs[CHIMNEY_P]
        for c in [c for c in cp.children if c.get("vfx_kind")]:
            bpy.data.objects.remove(c, do_unlink=True)
        K.socket(cp, "chimney_smoke", Vector(_rel(PART_INFO["flue"], cp)), **SMOKE)
        cp["m068_flue"] = _rel(PART_INFO["flue"], cp)
    if BANNER_P in objs:
        bp = objs[BANNER_P]
        bp["m068_top"] = _rel(PART_INFO["banner_hang"], bp)


def build(render=True, parts=True, close=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn)
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
    out = {"build_s": round(time.time() - t0, 1)}
    out.update(report(h, order, log, geo))
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


def _idp(v):
    if v is None:
        return None
    if hasattr(v, "to_dict"):
        return v.to_dict()
    if hasattr(v, "to_list"):
        return v.to_list()
    return v


def report(h=None, order=None, log=None, geo=None):
    """Every stage 2 check on the hero and its parts; problems lists whatever misses a target."""
    h = h or bpy.data.objects[HERO]
    order = order or [h] + [bpy.data.objects[n] for n, _ in PARTS if n in bpy.data.objects]
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
    parity = {o.name: winding_parity(o) for o in order}
    for n_, p in parity.items():
        if p:
            problems.append(f"{n_}: inward faces by ray parity {p}")
    contact = {o.name: contact_report(o, seats=SEATS if o is h else ()) for o in order}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: floating {c['floating_names']}, unchained {c['unchained_names']}")
        if n_ == HERO and c["sink"] < -0.051:
            problems.append(f"{n_}: sinks {c['sink']} below the ground")
    for k, g in contact[h.name]["seats"].items():
        if g is None or g > CONTACT:
            problems.append(f"{HERO}: seat {k} gap {g}")
    bury = {o.name: bury_report(o) for o in order}
    for n_, b in bury.items():
        if b["buried"]:
            problems.append(f"{n_}: buried {b['over_limit']} hidden {b['fully_hidden']}")
    pierce = {o.name: pierce_report(o) for o in order}
    for n_, p in pierce.items():
        if p:
            problems.append(f"{n_}: edges passing through thin canvas / banner {p}")
    ropes = {o.name: rope_ends_report(o) for o in order if json.loads(o.get("m068_ropes", "[]"))}
    for n_, r in ropes.items():
        if r["loose"]:
            problems.append(f"{n_}: rope ends not touching {r['loose']}")
    walk = walk_report(h)
    if walk["min_clearance"] < 0.10:
        problems.append(f"{HERO}: walk clearance {walk['min_clearance']} at y {walk['at_y']} ({walk['nearest']})")
    if walk["turn_min_clearance"] < 0.10:
        problems.append(f"{HERO}: turn clearance {walk['turn_min_clearance']} ({walk['turn_nearest']})")
    if len(walk["rises"]) != 3 or any(abs(r - 0.87) > 0.02 for r in walk["rises"]):
        problems.append(f"{HERO}: risers {walk['rises']} (three of 0.87 +- 0.02 wanted)")
    for nm, d in walk["door"].items():
        if (d["min_width"] or 0) < 3.5 or (d["clear_height"] or 0) < 6.9:
            problems.append(f"{HERO}: door at the {nm} {d}")
    if walk["overhead_above_floor"] < 7.8 - 1e-3:
        problems.append(f"{HERO}: interior overhead {walk['overhead_above_floor']} above the floor (7.8 wanted)")
    for k, z in walk["lantern_bottoms"].items():
        if z < LANTERN_MIN.get(k, 0.0):
            problems.append(f"{HERO}: lantern {k} bottom {z}")
    escape = escape_report(h)
    if escape["leaks"]:
        problems.append(f"{HERO}: inside escape scan: {escape['leaks']} rays out of the room outside the door "
                        f"{escape['leak_regions']}")
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
    want = {HERO: ["chimney_smoke", "heat_glow", "heat_glow", "heat_glow"], LANTERN_P: ["heat_glow"],
            CHIMNEY_P: ["chimney_smoke"]}
    for n_, kinds in want.items():
        if n_ in stats and stats[n_]["kinds"] != kinds:
            problems.append(f"{n_}: sockets {stats[n_]['kinds']} ({kinds} wanted)")
    kinds = {}
    for s in shells[h.name]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    return {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                          "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                          "ngons", "dup_verts", "origin_offset", "transforms_applied")}
                      for au in audits],
            "hero_shells": kinds, "contact": contact, "bury": bury, "rope_ends": ropes, "walk": walk, "escape": escape,
            "placement": place, "winding": winding, "parity": parity, "bowties": bowties, "thin": thin,
            "log": log, "geo": geo, "problems": problems, "uv": uv, "export_stats": stats, "pierce": pierce,
            "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
            "stored": {k: _idp(h.get(k)) for k in ("m068_centre", "m068_door", "m068_hinge", "m068_chimney")},
            "sockets": {o.name: [{"kind": c["vfx_kind"], "local": [round(x, 3) for x in c.location]}
                                 for c in o.children if c.get("vfx_kind")] for o in order},
            "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order}}


# ---- renders (spec 2.12, 4.2; decision 11: mirrored renders for the cells drawn mirrored front-to-back) ----------------
SHEET_LENS = 3.0
SHEET_VIEWS = {"side_sheet": (90, 3), "f34_sheet": (-40, 15), "front3q_low_sheet": (-45, 5), "rear_sheet": (-90, 3),
               "r34_sheet": (-135, 15), "top_sheet": (0, 89.9)}
# the side, rear, r34 and top cells draw the chimney and dressing mirrored front-to-back (spec 3.6, decision 11):
# these are rendered again with the hero mirrored along Y (scale y -1) -> M068_mirror.png
MIRROR_VIEWS = ("side_sheet", "rear_sheet", "r34_sheet", "top_sheet")
VIEW_NAMES = ("front34", "rear34", "front", "side", "rear", "top")
PARTS_SHOT = (-30, 15)
PART_SHOTS = {ROOF_P: (60, 35), BANNER_P: (-60, 8), WALL_P: (160, 12), WINDOW_P: (60, 12), DOOR_P: (-20, 10),
              GABLE_P: (-20, 10), STAIRS_P: (-35, 20)}
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
    """A build-frame point in world space for object o (mirrors and moves with it)."""
    return o.matrix_world @ (Vector(p) - Vector(o[OFF]))


def _exploded(objs):
    """Linked copies of the parts laid out like the sheet's Exploded Construction: the roof panels (one mirrored) and
    ridge beam lifted, the chimney and banner at the left, the wall panels, door frame and gable frame in a row, the
    floor, foundation and stairs in front."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []
    x0 = objs[0].location.x + 70
    o0 = Matrix.Translation((x0, objs[0].location.y, 0))

    def put(tag, part, m):
        if part not in by:
            return
        c = bpy.data.objects.new(f"{PFX}expl_{tag}", by[part].data)
        coll.objects.link(c)
        c.matrix_world = o0 @ m
        shown.append(c)
    rz = lambda d: Matrix.Rotation(math.radians(d), 4, "Z")
    put("roof_r", ROOF_P, Matrix.Translation((5.0, 4.0, 17.0)))
    put("roof_l", ROOF_P, Matrix.Translation((-5.0, 4.0, 17.0)) @ Matrix.Diagonal((-1, 1, 1, 1)))
    put("ridge", RIDGE_P, Matrix.Translation((0.0, 4.0, 24.0)))
    put("chimney", CHIMNEY_P, Matrix.Translation((-15.0, 6.0, 14.0)))
    put("banner", BANNER_P, Matrix.Translation((-22.0, -2.0, 0.0)))
    put("lantern", LANTERN_P, Matrix.Translation((-22.0, -12.0, 3.0)))
    put("wall_l", WALL_P, Matrix.Translation((-12.0, 4.0, 3.0)) @ rz(90))
    put("wall_rear", WALL_P, Matrix.Translation((-2.0, 12.0, 3.0)))
    put("window", WINDOW_P, Matrix.Translation((6.0, 10.0, 3.0)) @ rz(90))
    put("door", DOOR_P, Matrix.Translation((12.0, -4.0, 0.0)))
    put("gable", GABLE_P, Matrix.Translation((24.0, 2.0, 2.0)))
    put("floor", FLOOR_P, Matrix.Translation((-1.0, -4.0, 0.0)))
    put("found_f", FOUND_P, Matrix.Translation((-10.0, -14.0, 0.0)) @ rz(90))
    put("found_s", FOUND_P, Matrix.Translation((-14.0, -6.0, 0.0)))
    put("stairs", STAIRS_P, Matrix.Translation((14.0, -16.0, 0.0)))
    bpy.context.view_layer.update()
    return shown


def _marker(h, at, name, proxy=False):
    """A 5.5-stud character stand-in (proxy: the spec 2.10 walk box, body 2 x 1 to 4.4, head 1.1 wide to 5.5)."""
    a = K.fk().Asset(PFX + name, "probe", seed=1, tint_var=0.0)
    if proxy:
        for hx, hy, z0, z1 in PROXY:
            _box(a, (-hx, -hy, z0), (hx, hy, z1), IRON, 0.8)
    else:
        a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=IRON, tint=0.7)
        a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=IRON, tint=0.7)
        a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=IRON, tint=0.7)
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
    markers = [_marker(h, (-3.0, -11.2, 0.0), "char"), _marker(h, (0.0, -2.0, FLOOR_Z), "char2", proxy=True)]
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        for o in objs[1:]:
            extra["part_" + o.name.replace(HERO, "").lower()] = ([o], *PART_SHOTS.get(o.name, PARTS_SHOT))
        if shown:
            extra["exploded"] = (shown, -25, 18)
        extra["scale"] = ([h] + markers, -30, 8)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            sheet = M.views(NUM, [h], names=VIEW_NAMES, extra=extra, vfx=True)
            spin = render_spin(h)
            mirror = render_mirror(h)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet, "spin": spin, "mirror": mirror}
        if close:
            out.update(render_close_ups(objs))
        return out
    finally:
        _remove(shown + markers)
        M.display(NUM, objs, TITLE)


def _stack(paths, out, cols=4):
    kit = K.NS["KIT"]
    rows = [kit["hstack"](paths[i:i + cols]) for i in range(0, len(paths), cols)]
    w = max(r.shape[1] for r in rows)
    rows = [np.concatenate([r, np.ones((r.shape[0], w - r.shape[1], 4), np.float32)], axis=1) if r.shape[1] < w else r
            for r in rows]
    kit["save_px"](kit["vstack"](rows), out)
    return out


def render_spin(h):
    """The eight-azimuth contact sheet: az 0, 45 ... 315 at e 10, long lens, floor hidden -> M068_spin.png."""
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
    return _stack(paths, f"{d}/M068_spin.png")


def render_mirror(h):
    """Decision 11: the side, rear, r34 and top cells with the hero mirrored front-to-back (scale y -1 about its
    origin), so the chimney and dressing sit where those cells draw them -> <view>_mirror.png, M068_mirror.png."""
    kit = K.NS["KIT"]
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    sc = bpy.context.scene
    old = kit["CELL"]
    kit["CELL"] = (480, 400)
    sy = h.scale.y
    h.scale.y = -sy
    bpy.context.view_layer.update()
    try:
        kit["vfx"].clear(sc)
        kit["vfx"].realize(sc, [h])
        paths = [kit["render_group"]([h], f"{d}/{k.replace('_sheet', '')}_mirror_sheet.png", *SHEET_VIEWS[k])
                 for k in MIRROR_VIEWS]
    finally:
        h.scale.y = sy
        bpy.context.view_layer.update()
        kit["CELL"] = old
        kit["vfx"].clear(sc)
    return _stack(paths, f"{d}/M068_mirror.png")


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
    """Spec 4.2: junction_cu (close-up A, the front-left plate end), base_cu (close-up B, the front-left corner),
    apex_cu (the front apex), door_cu (from the stairs), lantern_cu, underside_cu (close-up C, from inside looking up
    at the +X slope), inside_cu (from the doorway looking in), door_walk (the 5.5 proxy on the stairs, in the doorway
    and inside: front, side, three-quarter), thumb (the f34 at about 140 px)."""
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    h = objs[0]
    out = {}
    rc = render_close
    kit = K.NS["KIT"]
    sc = bpy.context.scene
    kit["vfx"].clear(sc)
    kit["vfx"].realize(sc, [h])
    try:
        out["junction_cu"] = rc([h], f"{d}/junction_cu.png", -30, 12, _at(h, (-7.0, -10.1, 10.9)), 1.6)
        out["base_cu"] = rc([h], f"{d}/base_cu.png", -40, 18, _at(h, (-7.0, -8.0, 1.6)), 2.0)
        out["apex_cu"] = rc([h], f"{d}/apex_cu.png", -20, 10, _at(h, (0.0, -9.8, 16.3)), 2.0)
        out["door_cu"] = rc([h], f"{d}/door_cu.png", -12, 8, _at(h, (0.0, -9.0, 6.0)), 5.2)
        out["lantern_cu"] = rc([h], f"{d}/lantern_cu.png", -35, 6, _at(h, (-6.5, -8.0, 8.0)), 2.6)
        out["chimney_cu"] = rc([h], f"{d}/chimney_cu.png", -40, 20, _at(h, (2.2, -3.5, 16.5)), 3.2)
    finally:
        kit["vfx"].clear(sc)
    out["underside_cu"] = render_cam([h], f"{d}/underside_cu.png", _at(h, (-1.0, 0.5, 4.5)),
                                     _at(h, (3.5, -3.0, 13.5)), lens=14.0)
    out["inside_cu"] = render_cam([h], f"{d}/inside_cu.png", _at(h, (0.0, -9.5, 7.0)), _at(h, (0.0, 4.0, 6.0)),
                                  lens=14.0)
    lanes = [_marker(h, (0.0, y, z), f"proxy{i}", proxy=True)
             for i, (y, z) in enumerate(((-11.9, TREADS[1][2]), (-8.6, FLOOR_Z), (-3.0, FLOOR_Z)))]
    try:
        old = kit["CELL"]
        kit["CELL"] = (420, 360)
        try:
            p1 = kit["render_group"]([h] + lanes, f"{d}/walk_front.png", 0, 4)
            p2 = kit["render_group"]([h] + lanes, f"{d}/walk_side.png", 90, 4)
            p3 = rc([h] + lanes, f"{d}/walk_f34.png", -35, 10, _at(h, (0.0, -8.0, 5.0)), 6.5, cell=(420, 360))
        finally:
            kit["CELL"] = old
        out["door_walk"] = _stack([p1, p2, p3], f"{d}/door_walk.png")
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


def preview(names=("side_sheet", "f34_sheet", "rear_sheet", "r34_sheet"), vfx=False, spin=False):
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
    hg = GEO["hinge"]
    h["m068_hinge"] = {"axis_bottom": _rel(hg["axis_bottom"], h), "closed_yaw": hg["closed_yaw"],
                       "open_yaw": hg["open_yaw"]}
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, _ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"hero": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                        "boundary_edges", "normals", "dup_verts")}, "log": lg,
            "geo": json.loads(json.dumps(GEO, default=lambda v: [round(x, 3) for x in v])),
            "offset": [round(x, 3) for x in h[OFF]]}
