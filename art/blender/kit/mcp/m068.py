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
    TIMBER_END: ("#E89A2A", 0.8, 0.0, 0.0, True),
    TIMBER_DEEP: ("#703816", 0.9, 0.0, 0.0, True),
    CANVAS: ("#FDECC6", 0.95, 0.0, 0.0, True),
    CANVAS_DEEP: ("#E6C49C", 0.95, 0.0, 0.0, True),
    STONE: ("#9A9597", 0.9, 0.0, 0.0, True),
    STONE_LIGHT: ("#B8ABA7", 0.9, 0.0, 0.0, True),
    STONE_DARK: ("#666264", 0.9, 0.0, 0.0, True),
    SOOT: ("#2A2425", 1.0, 0.0, 0.0, True),
    IRON: ("#524C4E", 0.55, 0.4, 0.0, False),
    GLOW: ("#EAB00E", 0.5, 0.0, NEON, False),
    ROPE: ("#DDBB5A", 0.95, 0.0, 0.0, True),
    ROPE_DEEP: ("#A7842F", 0.95, 0.0, 0.0, True),
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
        return cross(a_, b_, p) > 1e-12 and cross(b_, c_, p) > 1e-12 and cross(c_, a_, p) > 1e-12
    tris = []
    guard = 0
    while len(idx) > 3 and guard < 4 * n * n:
        guard += 1
        m = len(idx)
        cut = None
        for k in range(m):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % m]
            if cross(P[i0], P[i1], P[i2]) <= 1e-12:
                continue
            if any(inside(P[j], P[i0], P[i1], P[i2]) for j in idx if j not in (i0, i1, i2)):
                continue
            cut = k
            break
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
PLATE = (6.30, 7.20, 10.40, 11.20, 10.20, 0.12)   # x0, x1, z0, z1, |y| end, chamfer
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
CHIMNEY = (2.20, -3.45)                          # chimney centre (f34, decision 4; y nudged 0.05 off the rafter)
CH_W, CH_Z0, CH_JOINT, CH_Z1, CH_TOP = 2.60, 13.60, 16.60, 18.60, 19.40
HOLE = (0.87, 3.53, -4.78, -2.12)                # canvas cut round the chimney (0.03 clear)


def zt(x):
    """Canvas top (unsagged) at x."""
    return RIDGE_Z - P * abs(x)


def zu(x):
    """Canvas underside (unsagged) at x."""
    return zt(x) - CTV


def row_z(i):
    """Wall plank row i (0..4): bottom, top (0.005 seams between rows, the bottom row 0.003 off the plinth)."""
    z0 = ROW_Z0 + ROW_PITCH * i + (0.003 if i == 0 else 0.0)
    return z0, ROW_Z0 + ROW_PITCH * (i + 1) - 0.005


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


def floor(a, feet=False):
    """Ten deck planks along Y (1.26 wide, 0.06 seams) on the front and back courses and two hidden sleepers; the
    three threshold planks run out through the doorway onto the threshold beam between the door posts. feet: the
    Floor part's short dark feet (the exploded) instead of the sleepers."""
    x0 = -(FLOOR_N * FLOOR_W + (FLOOR_N - 1) * FLOOR_GAP) / 2
    for i in range(FLOOR_N):
        xa = x0 + i * (FLOOR_W + FLOOR_GAP)
        xb = xa + FLOOR_W
        y1 = 7.09 if max(abs(xa), abs(xb)) > CORNER_BLOCK[0] - 0.005 else WALL_IN_Y - 0.01
        nm = f"deck_{i}"
        vs, _ = _box(a, (xa, -y1, 2.303), (xb, y1, FLOOR_Z), TIMBER, _rt(nm, 0.05))
        _texture(a, vs, 0.03, _seed(nm), scale=0.35)
        _reg("plank", nm, vs)
    for i, (xa, xb) in enumerate(THRESH):
        nm = f"thresh_{i}"
        vs, _ = _box(a, (xa, DPOST[2], 2.303), (xb, -WALL_IN_Y - 0.02, FLOOR_Z), TIMBER, _rt(nm, 0.05))
        _reg("plank", nm, vs)
    vs, _ = _box(a, (-DOOR_X + 0.015, -9.48, 1.733), (DOOR_X - 0.015, -8.405, 2.297), TIMBER_DEEP, 0.97)
    _reg("beam", "thresh_beam", vs)
    if feet:
        for i, (x, y) in enumerate(((-5.0, -6.0), (5.0, -6.0), (-5.0, 0.0), (5.0, 0.0), (-5.0, 6.0), (5.0, 6.0))):
            vs, _ = _box(a, (x - 0.35, y - 0.35, 1.70), (x + 0.35, y + 0.35, 2.297), TIMBER_DEEP, _rt(f"ft{i}", 0.04))
            _reg("beam", f"floor_foot{i}", vs)
    else:
        for i, y in enumerate((-3.5, 3.5)):
            vs, _ = _box(a, (-6.395, y - 0.5, 1.70), (6.395, y + 0.5, 2.297), TIMBER_DEEP, 0.95)
            _reg("beam", f"sleeper_{i}", vs)


# ---- walls (spec 2.4) ----------------------------------------------------------------------------------------------------
LONG_SEGS = {0: [(-7.10, -2.62), (-2.58, 7.10)], 1: [(-7.10, 3.38), (3.42, 7.10)],
             2: [(-7.10, -2.62), (-2.58, -1.50), (1.50, 7.10)], 3: [(-7.10, -1.50), (1.50, 3.38), (3.42, 7.10)],
             4: [(-7.10, -2.62), (-2.58, 7.10)]}
BACK_SEGS = {0: [(-6.10, -2.02), (-1.98, 6.10)], 1: [(-6.10, 2.58), (2.62, 6.10)],
             2: [(-6.10, -2.02), (-1.98, 6.10)], 3: [(-6.10, 2.58), (2.62, 6.10)],
             4: [(-6.10, -2.02), (-1.98, 6.10)]}
FRONT_SEGS = {i: [(-6.10, -DOOR_X), (DOOR_X, 6.10)] for i in range(N_ROWS)}
PLANK_CH = 0.07


def _wall_map(wall, s, z0):
    if wall == "long":
        return lambda u, v, t: Vector((s * (WALL_IN_X + u), t, z0 + v))
    return lambda u, v, t: Vector((t, s * (WALL_IN_Y + u), z0 + v))


def plank(a, wall, s, t0, t1, z0, z1, name, band=True):
    """One wall plank (spec 2.4): a 6-sided section 0.37-0.40 thick with its outer top and bottom edges chamfered
    0.07 (neighbouring rows touch at the back, so the chamfers make the dark V seams and nothing is see-through).
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
    post(a, xs[0], xs[1], ys[0], ys[1], CORNER_BLOCK[5] + 0.003, PLATE[2] - 0.003, f"post_{tag}")


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
    bx(x0, x0 + 0.08, yc - 0.42, yc + 0.42, 10.47, 11.13, IRON, "iron", f"bplate_{tag}")
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
    poly = [(RIDGE_W / 2 + 0.005, top(RIDGE_W / 2 + 0.005)), (PLATE[1], top(PLATE[1])), (PLATE[1], seat), (xs, seat),
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


def trimmers(a):
    """Two short timbers between the rafters at y -5.82 and -1.94 under the chimney (close-up C): its seat."""
    cx, cy = CHIMNEY
    for i, x in enumerate((cx - 1.0, cx + 1.0)):
        nm = f"trimmer_{i}"
        vs, _ = _box(a, (x - 0.25, RAFTER_Y[0] + RAFTER_W / 2 + 0.002, CH_Z0 - 0.703),
                     (x + 0.25, RAFTER_Y[1] - RAFTER_W / 2 - 0.002, CH_Z0 - 0.003), TIMBER, _rt(nm, 0.05))
        _reg("beam", nm, vs)


def ridge_section():
    """The ridge beam's 7-sided section (x, z): chamfered bottom corners, the top following both canvas slopes 0.01
    under the canvas underside."""
    h = RIDGE_W / 2
    ztop = lambda x: zu(x) - 0.01
    return [(-h + 0.08, RIDGE_Z0), (h - 0.08, RIDGE_Z0), (h, RIDGE_Z0 + 0.08), (h, ztop(h)), (0.0, ztop(0.0)),
            (-h, ztop(h)), (-h, RIDGE_Z0 + 0.08)]


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
BB_FOOT, BB_TIP, BB_HEEL = 8.20, 1.00, (6.40, 7.20)
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
    """Vertical boards (0.94 wide, 0.03 seams) in the end-wall plane above the top plank row, their tops 0.10 under
    the canvas line; the middle board stops under the ridge beam."""
    tag = "F" if e < 0 else "B"
    y0, y1 = sorted((e * (WALL_IN_Y + 0.01), e * (WALL_IN_Y + WALL_T - 0.01)))
    zb = row_z(4)[1] + 0.003
    mp = lambda u, v, w: Vector((u, w, v))
    h = RIDGE_W / 2
    boards = [(-h + 0.005, h - 0.005, None)]
    w, gap, x = 0.9375, 0.03, h + 0.005
    for k in range(6):
        boards.append((x, x + w, k))
        boards.append((-x - w, -x, k))
        x += w + gap
    for xa, xb, k in boards:
        if k is None:
            poly = [(xa, zb), (xb, zb), (xb, RIDGE_Z0 - 0.004), (xa, RIDGE_Z0 - 0.004)]
        else:
            poly = [(xa, zb), (xb, zb), (xb, zu(xb) - 0.10), (xa, zu(xa) - 0.10)]
        nm = f"gboard_{tag}{xa:+.2f}"
        vs, _, _, _ = _ext(a, poly, mp, y0, y1, TIMBER, _rt(nm, 0.05))
        _texture(a, vs, 0.03, _seed(nm), scale=0.5)
        _reg("plank", nm, vs)


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
    plank(a, "end", -1, -DOOR_X + 0.005, DOOR_X - 0.005, DOOR_TOP + 0.003, row_z(4)[1], "header", band=False)
    door_leaf(a, theta_deg)


# ---- canvas (spec 2.7) ---------------------------------------------------------------------------------------------------
CXI = (0.001, 2.05, 4.10, 5.775, 6.85, EAVE)
CYS = (-CAN_Y, -7.535, -5.82, -3.88, -1.94, 0.0, 1.94, 3.88, 5.82, 7.535, CAN_Y)
SAG = 0.08
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
        return SAG if (CXI[i] in SAG_XI and CYS[j] in SAG_Y) else 0.0
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


def tie(a, s, y, name):
    """A golden U tie (spec 2.7): a flat strap 0.24 x 0.08 over the canvas top near the eave, round the canvas edge,
    across to the plate and down its outer face, its end under the plate against the wall (both ends touch)."""
    x0, x1, z0, z1, _, ch = PLATE
    prof = [(6.85, zt(6.85)), (EAVE, zt(EAVE)), (EAVE, zt(EAVE) - CTV), (x1, z1 - ch), (x1, z0 + ch), (x1 - ch, z0),
            (WALL_IN_X + WALL_T + 0.03, z0)]
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


def ties(a, s):
    for i, y in enumerate(RAFTER_Y):
        tie(a, s, y, f"tie_{'L' if s < 0 else 'R'}{i}")


# ---- chimney (spec 2.8) --------------------------------------------------------------------------------------------------
def chimney(a):
    """A square stone stack in two blocks (the upper set in 0.10: the notched joint), a 3.00 cap with a 1.40 flue
    recess 0.60 deep (soot); the lower block one step toward stone_dark, the cap stone_light (by role)."""
    cx, cy = CHIMNEY
    h = CH_W / 2
    vs, _ = _box(a, (cx - h, cy - h, CH_Z0), (cx + h, cy + h, CH_JOINT), _mix(STONE, STONE_DARK, 0.25),
                 _rt("chim_lo", 0.03))
    _texture(a, vs, 0.04, 6820, scale=0.8)
    _reg("chimney", "chim_lo", vs)
    h2 = h - 0.10
    vs, _ = _box(a, (cx - h2, cy - h2, CH_JOINT + 0.003), (cx + h2, cy + h2, CH_Z1), STONE, _rt("chim_up", 0.03))
    _texture(a, vs, 0.04, 6821, scale=0.8)
    _reg("chimney", "chim_up", vs)
    hc, hf, zc0, zf = 1.50, 0.70, CH_Z1 + 0.003, CH_TOP - 0.60
    o0 = [Vector((cx + x * hc, cy + y * hc, zc0)) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    o1 = [p + Vector((0, 0, CH_TOP - zc0)) for p in o0]
    i1 = [Vector((cx + x * hf, cy + y * hf, CH_TOP)) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    i0 = [p - Vector((0, 0, CH_TOP - zf)) for p in i1]
    pts = o0 + o1 + i1 + i0
    faces = [[3, 2, 1, 0]]
    keys = [STONE_LIGHT]
    for k in range(4):
        k1 = (k + 1) % 4
        faces.append([k, k1, 4 + k1, 4 + k])
        keys.append(STONE_LIGHT)
        faces.append([4 + k, 4 + k1, 8 + k1, 8 + k])
        keys.append(STONE_LIGHT)
        faces.append([8 + k, 8 + k1, 12 + k1, 12 + k])
        keys.append(SOOT)
    faces.append([12, 13, 14, 15])
    keys.append(SOOT)
    vs, fs = _shell(a, pts, faces, STONE_LIGHT, _rt("chim_cap", 0.03))
    for f, k in zip(fs, keys):
        if k != STONE_LIGHT:
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
    rings = [_ngon(Vector((px, y, ARM_ZC)), ex, ez, r, 6, math.pi / 6) for y, r in ARM_PROF]
    vs, fs, bands = _prism(a, rings, TIMBER, _rt("arm", 0.04))
    _paint(a, bands[3] + bands[4] + bands[5], IRON)
    _paint(a, fs[-2:], TIMBER_END)
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
