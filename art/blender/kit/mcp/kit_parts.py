"""Shared parametric pieces for the numbered-model builders (art/blender/kit/mcp/mNNN.py). See STAGES.md, "Shared
library (2026-11-04)".

Every piece adds ONE closed, manifold, outward-wound, flat-shaded shell (or a few, each closed) to a flintkit Asset `a`
and returns a Piece: unpack it as `vs, fs = piece`, or read piece.vs / .fs / .bands / .caps / .name. Units are studs;
the build frame is front -Y, +X right, ground z 0. Defaults are the measured values of the passed model named in each
docstring. Colour is by role and position (keys passed in), never by facing.

    import kit_parts as P
    with P.frame(Matrix.Translation((0, -2.4, 0)), "bench_f_"):     # place and prefix everything built inside
        P.plank(a, (-2.9, 0.31, 1.28), (2.9, 0.31, 1.28), 0.58, 0.44, WOOD, name="seat")

Common keywords on every piece: name (registered in PIECES with `kind`, prefixed by the current frame's tag; the
Tint is seeded from it), kind, tint (a multiplier; None = 1 +- amp seeded by the name), amp (default TINT = 0.05).

Registers (kit_build.Model.make clears them per object and stores them on it as <key>_pieces / _ropes / _leaves):
    PIECES [(kind, name, centroid)], ROPES [{name, ends, rt}], LEAVES [{name, n, kind, ...}], GEO {} (free notes)
    reset(), frame(matrix, tag), here(p) (a local point in the current frame's world)

Helpers      seed rng rt mix ngon sec_rect sec_ngon earclip min_angle newell up_for hull2 mitre R tree_of Local
Core shells  shell hull prism box ext beam
Timber       plank butt_spans plank_wall post log leg bolt stairs
Rope         tube rope rect_loop hull_loop rope_turn rope_band x_lashing strap
Cloth        canvas banner emblem
Props        crate barrel pole crossarm sleeve banner_set lantern bracket
Stone        block rock stone moss
Foliage      leaf leaf_frame ivy (Wall, IVY settings)

Pieces that cast rays onto what is already built (moss, ivy) work in the build frame: call them outside frame().
Asset.finish welds vertices closer than 1e-5, so two pieces that share an exact corner or edge become one non-manifold
shell: seat pieces 0.003 off what they meet, or overlap them (the bury limit is 0.05).
Put genuinely new reusable pieces in here only through the main session; model-specific shapes stay in mNNN.py.
"""
import math
import random
from collections import namedtuple

import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_mcp as K

Z = Vector((0.0, 0.0, 1.0))
TINT = 0.05                     # default per-piece Tint amplitude (m067 PIECE_TINT)

# ---- registers and placement frames ------------------------------------------------------------------------------
PIECES = []                     # (kind, name, centroid in the build frame) per shell, in build order
ROPES = []                      # open rope runs: {name, ends, rt} (both-ends contact check)
LEAVES = []                     # placed leaves: {name, n, kind, c, tone, ...} (foliage sweep)
GEO = {}                        # measured placements for the report
XF = [Matrix.Identity(4)]
TAG = [""]


def reset():
    """Clear every register and frame (kit_build does this before each object)."""
    PIECES.clear()
    ROPES.clear()
    LEAVES.clear()
    GEO.clear()
    XF[:] = [Matrix.Identity(4)]
    TAG[:] = [""]


class frame:
    """with frame(m, tag): pieces built inside are placed by the 4x4 matrix m (composed with any outer frame) and their
    names get the prefix tag (m067 _Frame)."""

    def __init__(self, m=None, tag=""):
        self.m, self.tag = m if m is not None else Matrix.Identity(4), tag

    def __enter__(self):
        XF.append(XF[-1] @ self.m)
        TAG.append(TAG[-1] + self.tag)
        return self

    def __exit__(self, *exc):
        XF.pop()
        TAG.pop()


def here(p):
    """A point given in the current frame, in the build frame."""
    return XF[-1] @ Vector(p)


class Piece(tuple):
    """(vs, fs) plus .bands (faces between consecutive rings), .caps ([start faces, end faces]) and .name."""

    def __new__(cls, vs, fs, **extra):
        t = tuple.__new__(cls, (vs, fs))
        t.__dict__.update(dict(bands=[], caps=[[], []], name=None), **extra)
        return t

    vs = property(lambda s: s[0])
    fs = property(lambda s: s[1])


Local = namedtuple("Local", "s u v")      # a point in a beam's frame: s along from p0, u across, v up


# ---- small helpers -----------------------------------------------------------------------------------------------
def seed(name):
    """A stable integer from a name (the per-piece seed every builder uses)."""
    return sum((i + 1) * ord(c) for i, c in enumerate(name))


def rng(name):
    return random.Random(seed(name))


def rt(name, amp=TINT):
    """Per-piece Tint 1 +- amp, seeded by the name."""
    return 1.0 + rng(name).uniform(-amp, amp)


def mix(k1, k2, t, step=0.05):
    """K.mix_key with t rounded to `step` (so a model makes few in-between keys)."""
    t = round(round(max(0.0, min(1.0, t)) / step) * step, 2)
    return K.mix_key(k1, k2, t)


def paint(a, faces, key):
    """Put faces into palette key (by role or position, never by facing)."""
    mi = a._mi(key)
    for f in faces:
        if f.is_valid:
            f.material_index = mi


def tint(a, faces, k):
    """Multiply the faces' Tint by k."""
    for f in faces:
        for lp in f.loops:
            t = lp[a.tint_layer][0] * k
            lp[a.tint_layer] = (t, t, t, 1.0)


def texture(a, vs, amp=0.03, seed_=0, scale=0.3):
    """Broad Tint mottling (K.texture without per-face jitter)."""
    K.texture(a, vs, amp=amp, scale=scale, jitter=0.0, seed=seed_)


def R(c, rot_deg=0.0, z=0.0):
    """Matrix: rotate rot_deg about Z, then move to (c.x, c.y, z)."""
    return Matrix.Translation((c[0], c[1], z)) @ Matrix.Rotation(math.radians(rot_deg), 4, "Z")


def ngon(c, e1, e2, r, n, rot=0.0):
    """n points round c in the plane (e1, e2), radius r (to the corners), starting at angle rot."""
    c = Vector(c)
    return [c + (Vector(e1) * math.cos(rot + 2 * math.pi * k / n) + Vector(e2) * math.sin(rot + 2 * math.pi * k / n)) * r
            for k in range(n)]


def sec_rect(hu, hv, ch=0.0, corners=("-u-v", "+u-v", "+u+v", "-u+v")):
    """A rectangle section (half sizes hu, hv), counter-clockwise in (u, v); the listed corners chamfered by ch. All
    four: the 8-sided plank of m067 (ch 0.04); ("+u-v", "+u+v"): m068's wall plank, whose outer edges make V seams."""
    out = []
    for name, (su, sv) in (("-u-v", (-1, -1)), ("+u-v", (1, -1)), ("+u+v", (1, 1)), ("-u+v", (-1, 1))):
        if ch > 0 and name in corners:
            # entering along the edge that came before (counter-clockwise), then leaving along the next
            if (su, sv) == (-1, -1):
                out += [(-hu, -hv + ch), (-hu + ch, -hv)]
            elif (su, sv) == (1, -1):
                out += [(hu - ch, -hv), (hu, -hv + ch)]
            elif (su, sv) == (1, 1):
                out += [(hu, hv - ch), (hu - ch, hv)]
            else:
                out += [(-hu + ch, hv), (-hu, hv - ch)]
        else:
            out.append((su * hu, sv * hv))
    # start at the bottom edge's first point (m067 _sec order) so rings line up between sections
    if ch > 0 and "-u-v" in corners:
        out = out[1:] + out[:1]
    return out


def sec_ngon(r_flat, n=8, flat_bottom=True):
    """A regular n-gon section of flat radius r_flat (u, v); with a flat at the bottom (and on the axes for n = 8)."""
    rv = r_flat / math.cos(math.pi / n)
    rot = (math.pi / n if n % 4 == 0 else (-math.pi / 2 + math.pi / n)) if flat_bottom else 0.0
    return [(math.cos(rot + 2 * math.pi * k / n) * rv, math.sin(rot + 2 * math.pi * k / n) * rv) for k in range(n)]


def min_angle(pts):
    """Smallest corner angle (radians) of a polygon of Vectors."""
    out = math.pi
    for k, p in enumerate(pts):
        u, v = pts[k - 1] - p, pts[(k + 1) % len(pts)] - p
        out = min(out, u.angle(v) if u.length > 1e-9 and v.length > 1e-9 else 0.0)
    return out


def earclip(P):
    """Triangles (index triples, counter-clockwise) of a simple 2D polygon; at each step the ear with the largest
    smallest corner is cut (no slivers), and a vertex on the new diagonal blocks the ear (no T-junctions) (m068)."""
    n = len(P)
    area = sum(P[i][0] * P[(i + 1) % n][1] - P[(i + 1) % n][0] * P[i][1] for i in range(n))
    idx = list(range(n)) if area > 0 else list(reversed(range(n)))

    def cross(o, p, q):
        return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])

    def inside(p, a_, b_, c_):
        if cross(a_, b_, p) > 1e-12 and cross(b_, c_, p) > 1e-12 and cross(c_, a_, p) > 1e-12:
            return True
        if abs(cross(c_, a_, p)) <= 1e-9:
            t = (p[0] - c_[0]) * (a_[0] - c_[0]) + (p[1] - c_[1]) * (a_[1] - c_[1])
            L2 = (a_[0] - c_[0]) ** 2 + (a_[1] - c_[1]) ** 2
            return 1e-9 < t < L2 - 1e-9
        return False
    tris, guard = [], 0
    while len(idx) > 3 and guard < 4 * n * n:
        guard += 1
        m = len(idx)
        cut, best = None, -1.0
        for k in range(m):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % m]
            if cross(P[i0], P[i1], P[i2]) <= 1e-12:
                continue
            if any(inside(P[j], P[i0], P[i1], P[i2]) for j in idx if j not in (i0, i1, i2)):
                continue
            q = min_angle([Vector((P[i][0], P[i][1], 0.0)) for i in (i0, i1, i2)])
            if q > best:
                cut, best = k, q
        k = 0 if cut is None else cut          # only collinear corners left: drop one
        tris.append((idx[k - 1], idx[k], idx[(k + 1) % m]))
        idx.pop(k)
    tris.append(tuple(idx))
    return [t for t in tris if len(set(t)) == 3]


def newell(pts):
    """Newell normal (unnormalised) of a 3D polygon."""
    n = Vector()
    m = len(pts)
    for i in range(m):
        p, q = pts[i], pts[(i + 1) % m]
        n += Vector(((p.y - q.y) * (p.z + q.z), (p.z - q.z) * (p.x + q.x), (p.x - q.x) * (p.y + q.y)))
    return n


def up_for(path):
    """A sensible 'up' for a tube along path: the loop's plane normal, else square to the chord and Z."""
    path = [Vector(p) for p in path]
    n = newell(path)
    span = max((p - path[0]).length for p in path)
    if n.length > 1e-3 * max(span, 0.1) ** 2:
        return n.normalized()
    ch = path[-1] - path[0]
    u = ch.cross(Z)
    if u.length < 1e-4:
        u = ch.cross(Vector((1, 0, 0)))
    return u.normalized()


def hull2(pts):
    """Counter-clockwise convex hull of 2D points."""
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


def mitre(H, d):
    """The mitred offset polygon of a counter-clockwise convex polygon: every edge exactly d outside (m064)."""
    n = len(H)
    out = []
    for i in range(n):
        p0, p1, p2 = H[i - 1], H[i], H[(i + 1) % n]
        e_a = Vector((p1[0] - p0[0], p1[1] - p0[1])).normalized()
        e_b = Vector((p2[0] - p1[0], p2[1] - p1[1])).normalized()
        n_a, n_b = Vector((e_a.y, -e_a.x)), Vector((e_b.y, -e_b.x))
        bis = (n_a + n_b).normalized()
        out.append(Vector(p1) + bis * (d / max(bis.dot(n_a), 0.2)))
    return out


def tree_of(*pieces):
    """A BVH of the given pieces' faces (build frame), e.g. the stone to drape moss or ivy on."""
    vs = [v for p in pieces for v in (p.vs if isinstance(p, Piece) else p)]
    return K.bvh_of(vs)


# ---- core shells ---------------------------------------------------------------------------------------------------
def shell(a, pts, faces, key, name=None, kind="piece", tint=None, amp=TINT, keys=None, colour=None, recalc=True):
    """One closed shell from points (in the current frame) and faces (index lists): winding made consistent (recalc)
    and the shell flipped whole if its signed volume is negative (m051 / m067). keys: a key per face (None keeps
    `key`); colour(local face centre) -> key. Registered as (kind, name) when named."""
    m = XF[-1]
    local = [Vector(p) for p in pts]
    bm = a.bm
    vs = [bm.verts.new(m @ p) for p in local]
    fs = [bm.faces.new([vs[i] for i in f]) for f in faces]
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=fs)
    for f in fs:
        f.normal_update()
    if sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) < 0:
        for f in fs:
            f.normal_flip()
            f.normal_update()
    full = TAG[-1] + name if name else None
    a._finish(vs, key, tint=tint if tint is not None else (rt(full, amp) if full else 1.0))
    if keys is not None:
        for f, k in zip(fs, keys):
            if k is not None and k != key:
                f.material_index = a._mi(k)
    if colour is not None:
        for f, idx in zip(fs, faces):
            f.material_index = a._mi(colour(sum((local[i] for i in idx), Vector()) / len(idx)))
    if full:
        PIECES.append((kind, full, sum((v.co for v in vs), Vector()) / len(vs)))
    return Piece(vs, fs, name=full)


def hull(a, pts, key, name=None, kind="piece", tint=None, amp=TINT):
    """A convex faceted hull of points: triangulated, flat neighbours beautified (m051 / m068). Returns a Piece."""
    m = XF[-1]
    bm = a.bm
    vs = [bm.verts.new(m @ Vector(p)) for p in pts]
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
    if sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) < 0:
        for f in fs:
            f.normal_flip()
            f.normal_update()
    full = TAG[-1] + name if name else None
    a._finish(vs, key, tint=tint if tint is not None else (rt(full, amp) if full else 1.0))
    if full:
        PIECES.append((kind, full, sum((v.co for v in vs), Vector()) / len(vs)))
    return Piece(vs, fs, name=full)


CAP8 = [[0, 1, 2, 7], [7, 2, 3, 6], [6, 3, 4, 5]]      # an 8-ring cap as three planar quads (m067)


def _cap(n):
    """A ring's cap as faces of ring indices: one quad, the 8-ring's three quads, quads across even rings, or one
    n-gon (kit_build's cleanup ear-clips it)."""
    if n <= 4:
        return [list(range(n))]
    if n == 8:
        return [list(c) for c in CAP8]
    if n % 2 == 0:
        h = n // 2
        return [[i, i + 1, n - 2 - i, (n - 1 - i) % n] for i in range(h - 1)]
    return [list(range(n))]


def prism(a, rings, key, caps=(True, True), band_keys=None, cap_keys=None, **kw):
    """A closed loft through rings of n points each (same order in every ring; planar end rings): side quads band by
    band, then the start cap, then the end cap. band_keys[i] colours the band between ring i and i + 1; cap_keys =
    (start, end). Returns a Piece with .bands and .caps."""
    n = len(rings[0])
    pts = [p for r in rings for p in r]
    faces, bands, keys = [], [], []
    for i in range(len(rings) - 1):
        bands.append(list(range(len(faces), len(faces) + n)))
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, (i + 1) * n + j1, (i + 1) * n + j])
            keys.append(band_keys[i] if band_keys and i < len(band_keys) else None)
    cap_idx = [[], []]
    last = (len(rings) - 1) * n
    if caps[0]:
        for c in _cap(n):
            cap_idx[0].append(len(faces))
            faces.append(list(reversed(c)))
            keys.append(cap_keys[0] if cap_keys else None)
    if caps[1]:
        for c in _cap(n):
            cap_idx[1].append(len(faces))
            faces.append([last + i for i in c])
            keys.append(cap_keys[1] if cap_keys else None)
    p = shell(a, pts, faces, key, keys=keys if any(k is not None for k in keys) else kw.pop("keys", None), **kw)
    p.bands = [[p.fs[k] for k in b] for b in bands]
    p.caps = [[p.fs[k] for k in c] for c in cap_idx]
    return p


def box(a, lo, hi, key, m=None, **kw):
    """Axis box lo..hi (optionally moved by matrix m inside the current frame). Faces: -Y, +X, +Y, -X sides, then the
    bottom, then the top."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    rings = [[(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)] for z in (z0, z1)]
    if m is not None:
        rings = [[m @ Vector(p) for p in r] for r in rings]
    return prism(a, rings, key, **kw)


def ext(a, poly, w0, w1, key, to3=None, cap_key=None, side_keys=None, **kw):
    """A closed prism of a simple 2D polygon (u, v) between w0 and w1; to3(u, v, w) -> point (default (u, v, w):
    XY extruded along Z). Caps ear-clipped. .caps = [w0 cap faces, w1 cap faces] (m068 _ext)."""
    to3 = to3 or (lambda u, v, w: Vector((u, v, w)))
    n = len(poly)
    pts = [to3(u, v, w0) for u, v in poly] + [to3(u, v, w1) for u, v in poly]
    if n > 4:
        tris = earclip(poly)
        faces = [list(t) for t in tris] + [[n + t[2], n + t[1], n + t[0]] for t in tris]
        nc = len(tris)
    else:
        faces = [list(range(n)), [n + i for i in reversed(range(n))]]
        nc = 1
    keys = [cap_key] * (2 * nc)
    for i in range(n):
        i1 = (i + 1) % n
        faces.append([i, i1, n + i1, n + i])
        keys.append(side_keys[i] if side_keys else None)
    p = shell(a, pts, faces, key, keys=keys, **kw)
    p.caps = [p.fs[:nc], p.fs[nc:2 * nc]]
    p.bands = [p.fs[2 * nc:]]
    return p


def _axes(p0, p1, up):
    x = (Vector(p1) - Vector(p0))
    L = x.length
    x.normalize()
    v = Vector(up) - x * Vector(up).dot(x)
    if v.length < 1e-6:
        v = x.orthogonal()
    v.normalize()
    u = v.cross(x)
    return x, u, v, L


def beam(a, p0, p1, sec, key, up=Z, stations=(), colour=None, band_keys=None, cap_keys=None, **kw):
    """A straight member of 2D section sec (u, v) from p0 to p1: u = up x axis, v = up (made square to the axis).
    stations: extra rings at these distances from p0 (colour bands). colour(Local(s, u, v)) -> key per face."""
    x, u, v, L = _axes(p0, p1, up)
    p0 = Vector(p0)
    ss = [0.0] + sorted(s for s in stations if 1e-4 < s < L - 1e-4) + [L]
    rings = [[p0 + x * s + u * su + v * sv for su, sv in sec] for s in ss]
    cfn = None
    if colour is not None:
        cfn = lambda c: colour(Local((c - p0).dot(x), (c - p0).dot(u), (c - p0).dot(v)))     # noqa: E731
    return prism(a, rings, key, colour=cfn, band_keys=band_keys, cap_keys=cap_keys, **kw)


# ---- timber ---------------------------------------------------------------------------------------------------------
CH = 0.04                       # plank / leg chamfer (m067)


def plank(a, p0, p1, width, thick, key, ch=CH, up=Z, vseam=False, **kw):
    """A plank from p0 to p1 (centreline), width across (u = up x axis) and thick along up: an 8-sided section with
    its four long edges chamfered ch (m067: 0.44 thick, ch 0.04), or with vseam only the two +u edges chamfered (the
    outer face of a wall plank: m068 ch 0.10 makes the dark V seam between rows). Takes beam()'s stations, colour,
    band_keys, cap_keys."""
    corners = ("+u-v", "+u+v") if vseam else ("-u-v", "+u-v", "+u+v", "-u+v")
    return beam(a, p0, p1, sec_rect(width / 2, thick / 2, ch, corners), key, up=up, **kw)


def butt_spans(t0, t1, joints, overlap=0.0, gap=0.0):
    """Board spans from t0 to t1 cut at the joint positions. overlap > 0: neighbours overlap 2 x overlap (nothing
    shows through the joint, m068); gap > 0: an open joint that wide (m067's 0.04 butt joints on a solid top)."""
    edges = [t0] + sorted(joints) + [t1]
    out = []
    for i in range(len(edges) - 1):
        a0 = edges[i] + (gap / 2 - overlap if i else 0.0)
        a1 = edges[i + 1] - (gap / 2 - overlap if i < len(edges) - 2 else 0.0)
        out.append((a0, a1))
    return out


def plank_wall(a, origin, along, out, span, rows, joints, thick, key, vseam=0.10, overlap=0.02, deep=None, band=0.30,
               name="plank", kind="plank", jitter=0.03, **kw):
    """A wall (or deck) of board rows that closes: boards run along `along` from origin + along x span[0] to span[1];
    rows = [(v0, v1)] heights up the wall (up = out x along); joints = {row: [t]} butt joints. Neighbouring rows
    overlap 2 x overlap at the back and joints overlap the same, so nothing is see-through; the outer (`out`) faces
    carry V seams (vseam chamfer; 0 for square boards). Each board's outer face is jittered inward up to `jitter`;
    boards over 2.0 long get a seeded end band (30 % long) toward deep (m068 wall planks: 0.37-0.40 thick, 20-32
    tris). The inner faces lie in the plane through origin."""
    origin, along, out = Vector(origin), Vector(along).normalized(), Vector(out).normalized()
    up = out.cross(along).normalized()
    t0, t1 = span
    pieces = []
    for i, (v0, v1) in enumerate(rows):
        v0 = v0 - (overlap if i else 0.0)
        v1 = v1 + (overlap if i < len(rows) - 1 else 0.0)
        for k, (s0, s1) in enumerate(butt_spans(t0, t1, joints.get(i, []), overlap=overlap)):
            nm = f"{name}{i}_{k}"
            r = rng(nm)
            uo = thick - (r.uniform(0.0, jitter) if jitter else 0.0)
            c = min(vseam, uo / 2, (v1 - v0) / 2 - 1e-3) if vseam else 0.0
            sec = [(0.0, 0.0), (uo - c, 0.0), (uo, c), (uo, v1 - v0 - c), (uo - c, v1 - v0), (0.0, v1 - v0)] if c else \
                [(0.0, 0.0), (uo, 0.0), (uo, v1 - v0), (0.0, v1 - v0)]
            st, bk = [], None
            if deep and s1 - s0 > 2.0:
                f = band * (s1 - s0)
                bk = 0 if r.random() < 0.5 else 1
                st = [f] if bk == 0 else [s1 - s0 - f]
            p0 = origin + along * s0 + up * v0
            ss = [0.0] + st + [s1 - s0]
            rings = [[p0 + along * s + out * u + up * v for u, v in sec] for s in ss]
            p = prism(a, rings, key, name=nm, kind=kind, **kw)
            if bk is not None:
                paint(a, p.bands[bk] + p.caps[bk], mix(key, deep, 0.25))
            texture(a, p.vs, 0.025, seed(nm), scale=0.5)
            pieces.append(p)
    return pieces


def post(a, xy, z0, z1, half, key, ch=0.05, half_y=None, zs=(), band_keys=None, top_key=None, tip=0.0, apex=(0, 0),
         tip_key=None, rot=0.0, **kw):
    """A square chamfered post (8-sided, m070: half 0.40-0.55, ch 0.05) from a flat-cut foot at z0 to z1, extra rings
    at heights zs (foot bands: band_keys from the foot up), a flat top (top_key) or a pyramid tip of length `tip` with
    its apex offset `apex` (m069 logs: 8 facets, tip_key = cut wood). rot turns it about Z."""
    hy = half if half_y is None else half_y
    sec = sec_rect(half, hy, ch)
    m = Matrix.Rotation(math.radians(rot), 3, "Z")
    c = Vector((xy[0], xy[1], 0.0))
    heights = [z0] + sorted(z for z in zs if z0 < z < z1) + [z1]
    rings = [[c + m @ Vector((u, v, z)) for u, v in sec] for z in heights]
    if tip <= 0:
        return prism(a, rings, key, band_keys=band_keys, cap_keys=(None, top_key), **kw)
    n = len(sec)
    pts = [p for r in rings for p in r] + [c + m @ Vector((apex[0], apex[1], z1 + tip))]
    ap = len(pts) - 1
    faces, keys = [], []
    for i in range(len(rings) - 1):
        for k in range(n):
            faces.append([i * n + k, i * n + (k + 1) % n, (i + 1) * n + (k + 1) % n, (i + 1) * n + k])
            keys.append(band_keys[i] if band_keys and i < len(band_keys) else None)
    top = (len(rings) - 1) * n
    for k in range(n):
        faces.append([top + k, top + (k + 1) % n, ap])
        keys.append(tip_key)
    for cf in _cap(n):
        faces.append(list(reversed(cf)))
        keys.append(None)
    return shell(a, pts, faces, key, keys=keys, **kw)


def log(a, p0, p1, r, key, sides=8, up=Z, stations=(), end_key=None, tip0=0.0, tip1=0.0, **kw):
    """A round log (n-gon section, flat radius r, a flat underneath) from p0 to p1; flat-cut ends (end_key, the pale
    cut wood) or pyramid tips tip0 / tip1 long. Takes beam()'s colour and band_keys."""
    sec = sec_ngon(r, sides)
    if not tip0 and not tip1:
        return beam(a, p0, p1, sec, key, up=up, stations=stations, cap_keys=(end_key, end_key), **kw)
    x, u, v, L = _axes(p0, p1, up)
    p0 = Vector(p0)
    s0, s1 = tip0, L - tip1
    ss = [s0] + sorted(s for s in stations if s0 < s < s1) + [s1]
    rings = [[p0 + x * s + u * su + v * sv for su, sv in sec] for s in ss]
    n = sides
    pts = [p for rg in rings for p in rg]
    faces, keys = [], []
    for i in range(len(rings) - 1):
        for k in range(n):
            faces.append([i * n + k, i * n + (k + 1) % n, (i + 1) * n + (k + 1) % n, (i + 1) * n + k])
            keys.append(None)
    for end, tl in ((0, tip0), (1, tip1)):
        base = 0 if end == 0 else (len(rings) - 1) * n
        if tl > 0:
            pts.append(p0 + x * (0.0 if end == 0 else L))
            ap = len(pts) - 1
            for k in range(n):
                faces.append([base + k, base + (k + 1) % n, ap])
                keys.append(end_key)
        else:
            for cf in _cap(n):
                faces.append([base + i for i in (reversed(cf) if end == 0 else cf)])
                keys.append(end_key)
    return shell(a, pts, faces, key, keys=keys, **kw)


def leg(a, foot, top, z1, hu, hv, key, ch=CH, z0=0.0, zs=(), colour=None, band_keys=None, **kw):
    """A splayed square leg (m067): chamfered section hu x hv kept horizontal, its centre running from foot (x, y) at z0
    to top (x, y) at z1 (horizontal, planar end caps); extra rings at heights zs (a grime band at the foot)."""
    sec = sec_rect(hu, hv, ch)
    heights = [z0] + sorted(z for z in zs if z0 < z < z1) + [z1]
    rings = []
    for z in heights:
        t = (z - z0) / (z1 - z0)
        cx, cy = foot[0] + (top[0] - foot[0]) * t, foot[1] + (top[1] - foot[1]) * t
        rings.append([(cx + u, cy + v, z) for u, v in sec])
    return prism(a, rings, key, colour=colour, band_keys=band_keys, **kw)


def bolt(a, c, n, up, key, h=0.09, proud=0.05, dome=0.02, sink=0.03, **kw):
    """A square bolt head on a face (m067): c on the face, n its outward normal, up an in-face direction; half size h,
    proud of the face, a low pyramid dome, sunk into the wood. 16 tris."""
    n = Vector(n).normalized()
    u = Vector(up) - n * Vector(up).dot(n)
    u.normalize()
    w = n.cross(u)
    c = Vector(c)
    sq = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    pts = [c - n * sink + (u * i + w * j) * h for i, j in sq]
    pts += [c + n * proud + (u * i + w * j) * h for i, j in sq]
    pts.append(c + n * (proud + dome))
    faces = [[3, 2, 1, 0], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 8], [5, 6, 8], [6, 7, 8],
             [7, 4, 8]]
    kw.setdefault("kind", "bolt")
    kw.setdefault("amp", 0.02)
    return shell(a, pts, faces, key, **kw)


def stairs(a, x0, x1, y_top, z_top, n, rise, run, key, tread_t=0.30, boards=2, gap=0.04, support="blocks",
           support_key=None, throat=0.45, name="stair", **kw):
    """Steps down toward -Y: n treads (each of `boards` chamfered boards, `gap` apart) from the top tread's back edge
    at y_top with its top at z_top, each step `rise` lower and `run` further forward. support "blocks": a block under
    each tread down to the ground, 0.003 under it (m068); "stringers": a cut stringer 0.20 thick under each end of
    the treads with a sloped underside `throat` below the step corners (m052). Returns the pieces."""
    out = []
    sk = support_key or key
    w = x1 - x0
    seats = [z_top - rise * i - tread_t - 0.003 for i in range(n)]
    for i in range(n):
        zt = z_top - rise * i
        yb = y_top - run * i
        bw = (run - gap * (boards - 1)) / boards
        for k in range(boards):
            ya = yb - (k + 1) * bw - k * gap
            nm = f"{name}_tread{i}_{k}"
            out.append(plank(a, (x0, ya + bw / 2, zt - tread_t / 2), (x1, ya + bw / 2, zt - tread_t / 2), bw, tread_t,
                             key, ch=min(0.04, tread_t / 4), name=nm, kind="plank", **kw))
        if support == "blocks":
            out.append(box(a, (x0 + 0.1 * w, yb - run + 0.1, 0.0), (x1 - 0.1 * w, yb - 0.1, seats[i]), sk,
                           name=f"{name}_block{i}", kind="beam", **kw))
    if support == "stringers":
        yF = y_top - run * n
        slope = rise / run
        dz = throat * math.sqrt(1 + slope * slope)
        cy = y_top - run * (n - 1)
        if dz < seats[0] and seats[-1] - dz > 0:          # the sloped underside fits: a cut stringer
            yg = cy - (seats[-1] - dz) / slope
            prof = [(yF, 0.0), (yg, 0.0), (y_top, seats[0] - dz), (y_top, seats[0])]
        else:                                             # too short for a slope: a solid side slab
            prof = [(yF, 0.0), (y_top, 0.0), (y_top, seats[0])]
        for i in range(1, n):
            prof += [(y_top - run * i, seats[i - 1]), (y_top - run * i, seats[i])]
        prof.append((yF, seats[-1]))
        for s, xa in ((-1, x0 + 0.05), (1, x1 - 0.25)):        # under the tread ends, 0.003 below them
            nm = f"{name}_stringer{'lr'[s > 0]}"
            out.append(ext(a, prof, xa, xa + 0.20, sk, to3=lambda u, v, w_: Vector((w_, u, v)), name=nm, kind="beam",
                           **kw))
    GEO.setdefault("stairs", {})[name] = {"tops": [round(z_top - rise * i, 3) for i in range(n)], "rise": rise,
                                          "run": run}
    return out


# ---- rope ------------------------------------------------------------------------------------------------------------
TURN_SIDES = 5
SINK = 0.02                     # rope sunk into what it hugs (m066 / m070)


def tube(a, path, r, sides, closed, key, groove=None, up=(0, 0, 1), phase=0.0, twist=False, **kw):
    """A low-poly tube along path (m048 / m070): rings of `sides`; twist=True turns each ring half a side (an antiprism
    strip, a twisted rope); bends are mitred so the tube keeps its thickness; open tubes get flat end caps. groove =
    {strand: key} colours those strands (by place in the twist, never by facing). Closed twisted paths need an even
    point count."""
    P = [Vector(p) for p in path]
    N = len(P)
    if closed and twist and N % 2:
        raise ValueError("closed twisted rope path needs an even point count")
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
    for i in range(N if closed else N - 1):
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
    keys = [groove.get(s) for s in strand] if groove else None
    return shell(a, pts, faces, key, keys=keys, recalc=False, **kw)


def rope(a, path, r, key, deep=None, sides=4, closed=False, twist=True, up=None, name=None, kind="rope", amp=0.03,
         **kw):
    """A rope (m066 / m070): twist=True an antiprism twisted tube (diagonals, tails); twist=False rings aligned with
    spiral strands (turns round square timber, 5 sides). One strand in four `deep` (3-sided: half way). Open ropes are
    registered in ROPES for the both-ends contact check."""
    path = [Vector(p) for p in path]
    up = up if up is not None else up_for(path)
    groove = None
    if deep:
        groove = {0: deep} if (sides >= 4 or not twist) else {0: mix(key, deep, 0.5)}
    p = tube(a, path, r, sides, closed, key, groove=groove, up=tuple(up), twist=twist,
             phase=0.0 if twist else math.pi / sides, name=name, kind=kind, amp=amp, **kw)
    if not closed and name:
        ROPES.append({"name": p.name, "ends": [list(XF[-1] @ path[0]), list(XF[-1] @ path[-1])], "rt": r})
    return p


def turn_ext(sides=TURN_SIDES):
    """A twist=False turn's section extents as fractions of its radius: (inward, downward, upward) (m070)."""
    th = [math.pi / sides + 2 * math.pi * k / sides for k in range(sides)]
    return max(-math.sin(t) for t in th), max(-math.cos(t) for t in th), max(math.cos(t) for t in th)


def rect_loop(lo, hi, z, off):
    """Four points round the axis rectangle lo..hi (x, y) at height z, every side `off` outside (a mitred square)."""
    return [Vector((lo[0] - off, lo[1] - off, z)), Vector((hi[0] + off, lo[1] - off, z)),
            Vector((hi[0] + off, hi[1] + off, z)), Vector((lo[0] - off, hi[1] + off, z))]


def hull_loop(pts3, c, m, ref, offset, n):
    """A loop round the convex hull of section points in the plane (c, normal m): the hull's mitred offset at
    `offset`, corners kept, the longest edges split until there are n points (m064 / m066)."""
    m = Vector(m).normalized()
    c, ref = Vector(c), Vector(ref)
    e1 = (ref - m * ref.dot(m)).normalized()
    e2 = m.cross(e1)
    P2 = [((Vector(p) - c).dot(e1), (Vector(p) - c).dot(e2)) for p in pts3]
    H = hull2(P2)
    Hm = []
    for p in H:
        if not Hm or math.hypot(p[0] - Hm[-1][0], p[1] - Hm[-1][1]) > 0.06:
            Hm.append(p)
    if len(Hm) > 2 and math.hypot(Hm[0][0] - Hm[-1][0], Hm[0][1] - Hm[-1][1]) <= 0.06:
        Hm.pop()
    O = mitre(Hm, offset)
    while len(O) > n:
        k = min(range(len(O)), key=lambda i: abs((O[i] - O[i - 1]).to_3d().cross((O[(i + 1) % len(O)] - O[i]).to_3d()).z))
        del O[k]
    while len(O) < n:
        k = max(range(len(O)), key=lambda i: (O[(i + 1) % len(O)] - O[i]).length)
        O.insert(k + 1, (O[k] + O[(k + 1) % len(O)]) / 2)
    return [c + e1 * p.x + e2 * p.y for p in O]


def rope_turn(a, lo, hi, z, r, key, deep=None, sink=SINK, sides=TURN_SIDES, name=None, **kw):
    """A horizontal turn round the axis rectangle lo..hi (x, y) at height z (centreline), its inner flat sunk `sink`
    into the faces it hugs (m070 post_turn: r 0.13, 5 sides, spiral strands). Returns the Piece."""
    off = r * turn_ext(sides)[0] - sink
    return rope(a, rect_loop(lo, hi, z, off), r, key, deep, sides=sides, closed=True, twist=False, up=Z, name=name,
                **kw)


def rope_band(a, section, z0, r, key, deep=None, turns=3, step=None, off=None, pts=8, sides=5, name="band", **kw):
    """`turns` closed twisted turns stacked from z0 (bottom of the band) round a convex section (2D points in the
    build frame, e.g. a post's octagon), each the mitred hull offset by `off` (default r - 0.02: sunk 0.02) and
    touching the next (m069 bands: r 0.18, step 0.34, 8 points, 5 sides)."""
    step = step if step is not None else 2 * r - 0.02
    off = off if off is not None else r - 0.02
    cx = sum(p[0] for p in section) / len(section)
    cy = sum(p[1] for p in section) / len(section)
    out = []
    for t in range(turns):
        z = z0 + r + t * step
        loop = hull_loop([Vector((p[0], p[1], z)) for p in section], (cx, cy, z), Z, Vector((1, 0, 0)), off, pts)
        out.append(rope(a, loop, r, key, deep, sides=sides, closed=True, twist=True, up=Z, name=f"{name}_{t}", **kw))
    return out


def x_lashing(a, centre, half, z_lo, z_hi, face, key, deep=None, rt=0.13, rd=0.12, sink=SINK, lift=0.20, over=None,
              name="lash", half_y=None):
    """An X-lashing on a square post (m070 close-up A): turns round the post at z_lo and z_hi and two diagonals
    crossing on the post face `face` (unit (x, y) outward), the second lifted `lift` at the crossing. over = (face
    distance from the post centre, top z, bottom z) of a timber lying on that face: the diagonals round its top and
    bottom edges. Each diagonal starts and ends just inside its turn. Returns the pieces."""
    hx, hy = half, half if half_y is None else half_y
    cx, cy = centre
    lo, hi = (cx - hx, cy - hy), (cx + hx, cy + hy)
    flat = turn_ext()[0]
    out = [rope_turn(a, lo, hi, z_lo, rt, key, deep, sink=sink, name=f"{name}_lo"),
           rope_turn(a, lo, hi, z_hi, rt, key, deep, sink=sink, name=f"{name}_hi")]
    n = Vector((face[0], face[1], 0.0)).normalized()
    ax = Vector((-n.y, n.x, 0.0))
    c = Vector((cx, cy, 0.0))
    h = abs(n.x) * hx + abs(n.y) * hy
    hw = abs(ax.x) * hx + abs(ax.y) * hy
    dt = h + rt * flat - sink
    d0 = h + 0.8 * rd - sink
    xh = hw - 0.10
    for k, sg in enumerate((1, -1)):
        S = c + n * dt + ax * (-sg * xh)
        S.z = z_hi
        E = c + n * dt + ax * (sg * xh)
        E.z = z_lo
        lf = lift if k else 0.0
        if over:
            fd, top, bot = over
            o = 0.8 * rd - sink
            B1 = c + n * (fd + o) + ax * (-sg * 0.18)
            B1.z = top + o
            B2 = c + n * (fd + o) + ax * (sg * 0.18)
            B2.z = bot - o
            mid = c + n * (fd + o + lf)
            mid.z = (top + bot) / 2
            inner = [B1, mid, B2] if k else [B1, B2]
        else:
            mid = c + n * (d0 + lf)
            mid.z = (z_lo + z_hi) / 2
            inner = [mid]
        S0 = S + (inner[0] - S).normalized() * (1.4 * rt * flat)
        E0 = E + (inner[-1] - E).normalized() * (1.4 * rt * flat)
        out.append(rope(a, [S0] + inner + [E0], rd, key, deep, sides=4, up=n, name=f"{name}_x{k}"))
    return out


def strap(a, section, centre, normal, width, thick, key, gap=0.004, pts=None, name=None, kind="strap", **kw):
    """A flat tie strap (iron band, leather strap) wrapped round a convex section: the section points' hull offset
    `gap` (inner face) and gap + thick (outer face), `width` wide along `normal`, as one closed band shell (m064 hoop /
    strap). section: 3D points of the bound shape near the band; centre on the band's mid plane."""
    c, nrm = Vector(centre), Vector(normal).normalized()
    ref = nrm.orthogonal()
    n = pts or max(4, len(section))
    inner = hull_loop(section, c, nrm, ref, gap, n)
    outer = hull_loop(section, c, nrm, ref, gap + thick, n)
    rings = []
    for d, loop in ((-width / 2, inner), (-width / 2, outer), (width / 2, outer), (width / 2, inner)):
        rings.append([p + nrm * d for p in loop])
    allp = [p for rg in rings for p in rg]
    faces = []
    for r_ in range(4):
        r1 = (r_ + 1) % 4
        for k in range(n):
            k1 = (k + 1) % n
            faces.append([r_ * n + k, r_ * n + k1, r1 * n + k1, r1 * n + k])
    return shell(a, allp, faces, key, name=name, kind=kind, **kw)


# ---- cloth -------------------------------------------------------------------------------------------------------------
def canvas(a, corners, key, deep, nu=5, nv=5, sag=None, hem=0.35, ct=0.10, hole=(), tied=("C1", "C2", "C3", "C4"),
           name="canvas", kind="canvas", **kw):
    """A sagging canvas sheet with real thickness (m070 canvas_sheet): one closed ct slab. corners = {C1..C4} of the TOP
    surface (u runs C1 -> C4, v runs C1 -> C2; C3 is the u = v = 1 corner). An nu x nv top grid inset `hem` from the
    edges, each quad split along the diagonal pointing at the grid centre (the X of creases), a hem strip to the true
    edge, the underside ct below along the vertex normals (straight down at the tied corners), rim faces round every
    open edge. hole = {(i, j)} grid cells left open (a smoke hole, a door flap). sag = dict(v0, u1, v1, u0, c): the
    sag at each edge's middle and at the centre (m070: 0.28 front, 0.50 back, 0.75 centre). Hem colour by distance
    from the edge toward deep (rim 75 %, hem 50 %, the inner grid's border 20 %). Returns the Piece with .top (grid
    points)."""
    C = {k: Vector(v) for k, v in corners.items()}
    s = dict(v0=0.28, u1=0.28, v1=0.50, u0=0.50, c=0.75)
    s.update(sag or {})
    e = s["c"] - 0.5 * (s["v0"] + s["v1"] + s["u0"] + s["u1"])

    def top(u, v):
        p = C["C1"] * (1 - u) * (1 - v) + C["C4"] * u * (1 - v) + C["C2"] * (1 - u) * v + C["C3"] * u * v
        bu, bv = 4 * u * (1 - u), 4 * v * (1 - v)
        p.z -= (1 - v) * s["v0"] * bu + v * s["v1"] * bu + (1 - u) * s["u0"] * bv + u * s["u1"] * bv + e * bu * bv
        return p
    du = hem / max((C["C4"] - C["C1"]).length, 1e-6)
    dv = hem / max((C["C2"] - C["C1"]).length, 1e-6)
    T = {(i, j): top(du + (1 - 2 * du) * i / (nu - 1), dv + (1 - 2 * dv) * j / (nv - 1)) for i in range(nu)
         for j in range(nv)}
    loop = ([(i, 0) for i in range(nu)] + [(nu - 1, j) for j in range(1, nv)] +
            [(i, nv - 1) for i in range(nu - 2, -1, -1)] + [(0, j) for j in range(nv - 2, 0, -1)])
    O = {("o", k): top(k[0] / (nu - 1), k[1] / (nv - 1)) for k in loop}
    Pm = dict(T)
    Pm.update(O)
    ci, cj = (nu - 1) / 2, (nv - 1) / 2
    ring = {(i, j) for i in range(nu) for j in range(nv) if i in (0, nu - 1) or j in (0, nv - 1)}
    tris = []
    for i in range(nu - 1):
        for j in range(nv - 1):
            if (i, j) in hole:
                continue
            a_, b_, c_, d_ = (i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)
            pair = [(a_, b_, c_), (a_, c_, d_)] if (i + 0.5 < ci) == (j + 0.5 < cj) else [(a_, b_, d_), (b_, c_, d_)]
            for t in pair:
                tris.append((t, mix(key, deep, 0.20) if sum(1 for k in t if k in ring) == 3 else key))
    hk = mix(key, deep, 0.50)
    for k in range(len(loop)):
        a0, a1 = ("o", loop[k]), ("o", loop[(k + 1) % len(loop)])
        b0, b1 = loop[k], loop[(k + 1) % len(loop)]
        if (Pm[a0] - Pm[b1]).length <= (Pm[a1] - Pm[b0]).length:
            tris += [((a0, a1, b1), hk), ((a0, b1, b0), hk)]
        else:
            tris += [((a0, a1, b0), hk), ((a1, b1, b0), hk)]
    nrm = {k: Vector() for k in Pm}
    for t, _ in tris:
        p0, p1, p2 = (Pm[k] for k in t)
        n = (p1 - p0).cross(p2 - p0)
        if n.z < 0:
            n = -n
        for k in t:
            nrm[k] += n
    keys_ = [k for k in Pm if nrm[k].length > 0]
    idx = {k: i for i, k in enumerate(keys_)}
    cmap = {"C1": ("o", (0, 0)), "C4": ("o", (nu - 1, 0)), "C2": ("o", (0, nv - 1)), "C3": ("o", (nu - 1, nv - 1))}
    flat = {cmap[c] for c in tied}
    under = [Pm[k] - (Vector((0, 0, ct)) if k in flat else nrm[k].normalized() * (ct / max(nrm[k].normalized().z, 0.5)))
             for k in keys_]
    pts = [Pm[k] for k in keys_] + under
    nb = len(keys_)
    faces, fkeys = [], []
    count = {}
    for t, k in tris:
        faces.append([idx[q] for q in t])
        fkeys.append(k)
        faces.append([nb + idx[q] for q in reversed(t)])
        fkeys.append(k)
        for x in range(3):
            ed = (t[x], t[(x + 1) % 3])
            count[frozenset(ed)] = count.get(frozenset(ed), []) + [ed]
    rim = mix(key, deep, 0.75)
    for eds in count.values():
        if len(eds) == 1:                                   # an open edge (outer hem or the hole): a rim face
            u_, v_ = eds[0]
            faces.append([idx[u_], idx[v_], nb + idx[v_], nb + idx[u_]])
            fkeys.append(rim)
    p = shell(a, pts, faces, key, keys=[k if k != key else None for k in fkeys], name=name, kind=kind,
              amp=kw.pop("amp", 0.02), **kw)
    texture(a, p.vs, 0.03, seed(name), scale=0.18)
    p.top = T
    GEO.setdefault("canvas", {})[name] = {"low_top": round(min(q.z for q in Pm.values()), 3),
                                          "low_under": round(min(q.z for q in under), 3)}
    return p


def emblem(a, cx, cz, y_face, side, key, w=1.10, h=1.60, ring=0.15, inner=(0.36, 0.52), dots=(0.12, 0.80), t=0.015,
           name="emblem"):
    """The white emblem on one cloth face (m070 / m068): a diamond ring slab, an inner diamond and two side points,
    each 0.005 into the face and t proud; side = -1 on the -Y face, +1 on the +Y face. The cloth lies in an XZ plane."""
    y0, y1 = y_face - side * 0.005, y_face + side * t
    hw, hh = w / 2, h / 2
    k = ring * math.hypot(hw, hh) / hw
    kx = ring * math.hypot(hw, hh) / hh
    outer = [(cx, cz + hh), (cx + hw, cz), (cx, cz - hh), (cx - hw, cz)]
    inn = [(cx, cz + hh - k), (cx + hw - kx, cz), (cx, cz - hh + k), (cx - hw + kx, cz)]
    pts = [Vector((x, y0, z)) for x, z in outer + inn] + [Vector((x, y1, z)) for x, z in outer + inn]
    faces = []
    for i in range(4):
        i1 = (i + 1) % 4
        faces += [[i, i1, 4 + i1, 4 + i], [12 + i, 12 + i1, 8 + i1, 8 + i], [i1, i, 8 + i, 8 + i1],
                  [4 + i, 4 + i1, 12 + i1, 12 + i]]
    tag = "f" if side < 0 else "b"
    out = [shell(a, pts, faces, key, name=f"{name}_{tag}", kind="emblem", amp=0.02)]
    shapes = [("in", (cx, cz, inner[0] / 2, inner[1] / 2))]
    if dots:
        shapes += [("dl", (cx - dots[1], cz, dots[0], dots[0] * 1.3)), ("dr", (cx + dots[1], cz, dots[0], dots[0] * 1.3))]
    for nm, (ex, ez, w2, h2) in shapes:
        d = [(ex, ez + h2), (ex + w2, ez), (ex, ez - h2), (ex - w2, ez)]
        out.append(ext(a, d, min(y0, y1), max(y0, y1), key, to3=lambda u, v, w_: Vector((u, w_, v)),
                       name=f"{name}_{tag}_{nm}", kind="emblem", amp=0.02))
    return out


def banner(a, x0, x1, y, z_top, tip, notch, key, hem_key=None, t=0.08, hem=0.45, points=2, emblem_key=None,
           emblem_z=None, name="banner", **emb):
    """A swallowtail cloth hanging in the XZ plane at y (m070: 2.10 wide, 0.08 thick): its top at z_top, the side
    tips at `tip`, the notch up to `notch` (points=2: one notch in the middle; 3: three points, m068); the top hem band
    in hem_key; the emblem on both faces when emblem_key is given (centred at emblem_z)."""
    xm = (x0 + x1) / 2
    zb = z_top - hem
    if points == 3:
        w = x1 - x0
        outline = [(x0, z_top), (x1, z_top), (x1, zb), (x1, tip + 0.4), (x0 + 2 * w / 3, notch), (xm, tip),
                   (x0 + w / 3, notch), (x0, tip + 0.4), (x0, zb)]
    else:
        outline = [(x0, z_top), (x1, z_top), (x1, zb), (x1, tip), (xm, notch), (x0, tip), (x0, zb)]
    p = ext(a, outline, y - t / 2, y + t / 2, key, to3=lambda u, v, w_: Vector((u, w_, v)), name=name, kind="banner",
            amp=0.02)
    if hem_key:
        paint(a, [f for f in p.fs if f.calc_center_median().z > zb + 0.01], hem_key)
    texture(a, p.vs, 0.02, seed(name), scale=0.4)
    out = [p]
    if emblem_key:
        cz = emblem_z if emblem_z is not None else (zb + notch) / 2
        for side in (-1, 1):
            out += emblem(a, xm, cz, y + side * t / 2, side, emblem_key, name=f"{name}_emblem", **emb)
    return out


# ---- props ---------------------------------------------------------------------------------------------------------------
def sleeve(a, p0, p1, ri, ro, key, sides=6, up=Z, **kw):
    """A closed annular sleeve (ferrule, cloth hem round a pole) from p0 to p1: n-gon rings of flat radii ri (inner)
    and ro (outer), flats on the axes (m070 _annulus_x)."""
    x, u, v, L = _axes(p0, p1, up)
    p0 = Vector(p0)
    rot = math.pi / sides if sides % 4 == 0 else 0.0
    ra, rb = ri / math.cos(math.pi / sides), ro / math.cos(math.pi / sides)
    o0 = ngon(p0, u, v, rb, sides, rot)
    o1 = ngon(p0 + x * L, u, v, rb, sides, rot)
    i0 = ngon(p0, u, v, ra, sides, rot)
    i1 = ngon(p0 + x * L, u, v, ra, sides, rot)
    n = sides
    faces = []
    for j in range(n):
        j1 = (j + 1) % n
        faces += [[j, j1, n + j1, n + j], [2 * n + j1, 2 * n + j, 3 * n + j, 3 * n + j1], [j1, j, 2 * n + j, 2 * n + j1],
                  [n + j, n + j1, 3 * n + j1, 3 * n + j]]
    return shell(a, o0 + o1 + i0 + i1, faces, key, **kw)


def pole(a, xy, z0, z1, r, key, sides=8, zs=(), band_keys=None, top_key=None, **kw):
    """An upright round pole (n-gon, flat radius r) from z0 to z1; rings at zs (a golden foot band: band_keys)."""
    heights = [z0] + sorted(z for z in zs if z0 < z < z1) + [z1]
    rings = [[(xy[0] + u, xy[1] + v, z) for u, v in sec_ngon(r, sides)] for z in heights]
    kw.setdefault("kind", "pole")
    return prism(a, rings, key, band_keys=band_keys, cap_keys=(None, top_key), **kw)


def crossarm(a, p0, p1, r, key, end_key=None, knob=(0.30, 0.25), sides=8, up=Z, name="crossarm", **kw):
    """A round crossarm from p0 to p1 with pale cut ends and an end knob past p1 (radius, length; 0.003 off it) (m070:
    r 0.225, knob 0.30 x 0.25). Returns [arm, knob]."""
    out = [log(a, p0, p1, r, key, sides=sides, up=up, end_key=end_key, name=name, kind="arm", **kw)]
    if knob:
        x = (Vector(p1) - Vector(p0)).normalized()
        q0 = Vector(p1) + x * 0.003
        out.append(log(a, q0, q0 + x * knob[1], knob[0], key, sides=sides, up=up, end_key=end_key, name=name + "_knob",
                       kind="arm", **kw))
    return out


def banner_set(a, base, height, arm_len, key, cloth, white=None, iron=None, end_key=None, pole_r=0.25, arm_r=0.225,
               drop=6.6, width=2.1, name="bset"):
    """A banner pole with a crossarm and a hanging swallowtail (m070 / m068 layout): an 8-sided pole at base (x, y)
    to `height`, a crossarm along +X from the pole's face at height - 0.6 with a knob, a 6-sided cloth hem sleeve round
    the arm and the cloth `drop` long below it, the emblem in white on both faces, an iron collar where the arm meets
    the pole. Returns {pieces, arm_z, cloth_x}."""
    x, y = base
    out = [pole(a, (x, y), 0.0, height, pole_r, key, top_key=end_key, name=f"{name}_pole")]
    az = height - 0.6
    xa = x + pole_r + 0.003
    out += crossarm(a, (xa, y, az), (xa + arm_len, y, az), arm_r, key, end_key=end_key, name=f"{name}_arm")
    if iron:
        out.append(sleeve(a, (xa - 0.002, y, az), (xa + 0.25, y, az), arm_r / math.cos(math.pi / 8) + 0.008,
                          arm_r + 0.12, iron, name=f"{name}_collar", kind="iron"))
    c0 = xa + max(0.35, (arm_len - width) / 2)
    hem_ri, hem_ro = arm_r / math.cos(math.pi / 8) + 0.008, arm_r + 0.10
    out.append(sleeve(a, (c0, y, az), (c0 + width, y, az), hem_ri, hem_ro, mix(cloth, iron or key, 0.15),
                      name=f"{name}_hem", kind="banner", amp=0.02))
    zt = az - hem_ro + 0.007
    out += banner(a, c0, c0 + width, y, zt, zt - drop, zt - drop + 0.8, cloth, hem_key=mix(cloth, iron or key, 0.10),
                  emblem_key=white, emblem_z=zt - drop * 0.5, name=f"{name}_cloth", w=width * 0.52, h=width * 0.76,
                  dots=(0.12, width * 0.38))
    return {"pieces": out, "arm_z": az, "cloth_x": (c0, c0 + width)}


def crate(a, c, key, deep, rot=0.0, W=2.30, H=2.20, frame_t=(0.25, 0.45), floor_key=None, braces=True, open_top=True,
          name="crate"):
    """An X-braced crate (m070 / m066): four framed sides with recessed panels and an X brace of three boards on each,
    an open top whose rim is the frame width and a dark inner floor 0.60 down (open_top), or a closed lid. Colours:
    frame mix(key, deep, frame_t[0]), panels frame_t[1], inside deep. Returns the pieces."""
    Rm = R(c, rot)
    FW, RD, BW, BT, IN = 0.26, 0.05, 0.20, 0.05, (0.60 if open_top else 0.0)
    h = W / 2
    hi_ = h - FW
    zf = H - IN
    pts = [Vector((-h, -h, 0)), Vector((h, -h, 0)), Vector((h, h, 0)), Vector((-h, h, 0)),
           Vector((-h, -h, H)), Vector((h, -h, H)), Vector((h, h, H)), Vector((-h, h, H))]
    faces, keys = [[3, 2, 1, 0]], [deep]
    fk_, pk = mix(key, deep, frame_t[0]), mix(key, deep, frame_t[1])
    if open_top:
        pts += [Vector((-hi_, -hi_, H)), Vector((hi_, -hi_, H)), Vector((hi_, hi_, H)), Vector((-hi_, hi_, H)),
                Vector((-hi_, -hi_, zf)), Vector((hi_, -hi_, zf)), Vector((hi_, hi_, zf)), Vector((-hi_, hi_, zf))]
        for k in range(4):
            k1 = (k + 1) % 4
            faces += [[4 + k, 4 + k1, 8 + k1, 8 + k], [8 + k, 8 + k1, 12 + k1, 12 + k]]
            keys += [fk_, deep]
        faces.append([12, 13, 14, 15])
        keys.append(floor_key or deep)
    else:
        faces.append([4, 5, 6, 7])
        keys.append(fk_)
    sides = [((0, 1, 5, 4), Vector((0, -1, 0))), ((1, 2, 6, 5), Vector((1, 0, 0))),
             ((2, 3, 7, 6), Vector((0, 1, 0))), ((3, 0, 4, 7), Vector((-1, 0, 0)))]
    panels = []
    for (b0, b1, t1, t0), nrm in sides:
        P0, P1, P2, P3 = pts[b0], pts[b1], pts[t1], pts[t0]
        U = (P1 - P0).normalized()
        q = [P0 + U * FW + Z * FW, P1 - U * FW + Z * FW, P2 - U * FW - Z * FW, P3 + U * FW - Z * FW]
        qi = len(pts)
        pts += q
        ri = len(pts)
        pts += [p - nrm * RD for p in q]
        faces += [[b0, b1, qi + 1, qi], [b1, t1, qi + 2, qi + 1], [t1, t0, qi + 3, qi + 2], [t0, b0, qi, qi + 3]]
        keys += [fk_] * 4
        for k in range(4):
            faces.append([qi + k, qi + (k + 1) % 4, ri + (k + 1) % 4, ri + k])
            keys.append(pk)
        faces.append([ri, ri + 1, ri + 2, ri + 3])
        keys.append(pk)
        panels.append((q, nrm, U))
    body = shell(a, [Rm @ p for p in pts], faces, pk, keys=keys, name=name, kind="crate", tint=1.0)
    r_ = rng(name)
    for f in body.fs:
        tint(a, [f], 1.0 + r_.uniform(-0.04, 0.04))
    out = [body]
    if not braces:
        return out
    A_, B_ = W / 2 - FW, H / 2 - FW
    hw = BW / 2
    for si, (q, nrm, U) in enumerate(panels):
        cen = sum(q, Vector()) / 4 - nrm * RD

        def fit(dv, nv):
            return min((A_ - hw * abs(nv[0])) / max(abs(dv[0]), 1e-6), (B_ - hw * abs(nv[1])) / max(abs(dv[1]), 1e-6))
        dA = Vector((A_, B_)).normalized()
        nA = Vector((-dA.y, dA.x))
        LA = fit(dA, nA)
        dB = Vector((-A_, B_)).normalized()
        nB = Vector((-dB.y, dB.x))
        LB = fit(dB, nB)

        def hexa2d(quad, cen=cen, nrm=nrm, U=U):
            return [Rm @ (cen + U * u + Z * v + nrm * w) for w in (-0.005, BT - 0.005) for u, v in quad]
        quadA = [dA * -LA + nA * -hw, dA * LA + nA * -hw, dA * LA + nA * hw, dA * -LA + nA * hw]
        out.append(box_pts(a, hexa2d([(p.x, p.y) for p in quadA]), fk_, name=f"{name}_A{si}", kind="brace", amp=0.04))
        for hi, sg in enumerate((1, -1)):
            sgnA = 1 if nA.dot(dB * sg) > 0 else -1
            cs = []
            for e_ in (-1, 1):
                t_in = (sgnA * hw - e_ * hw * nA.dot(nB)) / nA.dot(dB)
                cs.append((dB * t_in + nB * (e_ * hw), dB * (sg * LB) + nB * (e_ * hw)))
            quad = [cs[0][0], cs[0][1], cs[1][1], cs[1][0]]
            out.append(box_pts(a, hexa2d([(p.x, p.y) for p in quad]), fk_, name=f"{name}_B{si}_{hi}", kind="brace",
                               amp=0.04))
    return out


HEXA = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (0, 4, 7, 3), (1, 2, 6, 5)]


def box_pts(a, pts8, key, **kw):
    """A hexahedron from 8 points: bottom quad then top quad, same order (m070 HEXA). Faces: bottom, top, then the
    sides from the first edge."""
    return shell(a, pts8, [list(f) for f in HEXA], key, **kw)


def barrel(a, c, key, deep, iron, rot=0.0, r0=1.00, r1=1.10, h=2.72, n=8, hoop=0.05, open_top=True, lid_key=None,
           name="barrel"):
    """A hooped barrel (m070 / m064): n staves (per-stave Tint) bulging from r0 at the ends to r1 at the middle, two
    iron hoops proud `hoop`; open (a dark inner rim and floor 0.15 down) or lidded (a lid 0.06 down in lid_key)."""
    Rm = R(c, rot + 180 / n)
    s = h / 2.80

    def r_at(z):
        return r0 + (r1 - r0) * (1 - ((z - h / 2) / (h / 2)) ** 2)
    prof = [(0.0, 0), (0.24 * s, 0), (0.24 * s, 1), (0.46 * s, 1), (0.46 * s, 0), (h / 2, 0), (2.34 * s, 0),
            (2.34 * s, 1), (2.56 * s, 1), (2.56 * s, 0), (h, 0)]
    ang = [2 * math.pi * k / n for k in range(n)]
    rings = [[Vector((math.cos(t) * (r_at(z) + (hoop if hp else 0.0)), math.sin(t) * (r_at(z) + (hoop if hp else 0.0)),
                      z)) for t in ang] for z, hp in prof]
    rin = 0.86 * r0
    depth = 0.15 if open_top else 0.06
    rings.append([Vector((math.cos(t) * rin, math.sin(t) * rin, h)) for t in ang])
    rings.append([Vector((math.cos(t) * rin, math.sin(t) * rin, h - depth)) for t in ang])
    pts = [Rm @ p for r_ in rings for p in r_]
    faces, keys, stave = [], [], []
    nr = len(prof)
    for i in range(nr - 1):
        hp = prof[i][1] or prof[i + 1][1]
        for j in range(n):
            faces.append([i * n + j, i * n + (j + 1) % n, (i + 1) * n + (j + 1) % n, (i + 1) * n + j])
            keys.append(iron if hp else None)
            stave.append(-1 if hp else j)
    for i in (nr - 1, nr):
        for j in range(n):
            faces.append([i * n + j, i * n + (j + 1) % n, (i + 1) * n + (j + 1) % n, (i + 1) * n + j])
            keys.append(mix(key, deep, 0.5) if i == nr - 1 else (deep if open_top else lid_key or mix(key, deep, 0.3)))
            stave.append(-1)
    faces.append([(nr + 1) * n + j for j in range(n)])
    keys.append(mix(deep, iron, 0.5) if open_top else (lid_key or mix(key, deep, 0.3)))
    stave.append(-1)
    faces.append(list(reversed(range(n))))
    keys.append(deep)
    stave.append(-1)
    p = shell(a, pts, faces, key, keys=keys, name=name, kind="barrel", tint=1.0)
    r_ = rng(name)
    st = [1.0 + r_.uniform(-0.06, 0.06) for _ in range(n)]
    for f, sv in zip(p.fs, stave):
        if sv >= 0:
            tint(a, [f], st[sv])
    return p


def lantern(a, base, iron, glass, rot=0.0, w=1.40, plate=0.20, gw=1.00, gh=1.60, band=0.25, roof=0.40, fin=0.15,
            bar=0.16, ring_axis=(1, 0, 0), hook=True, name="lantern"):
    """A square dark-iron lantern (m068: 2.60 body): base plate, a glass block in the `glass` key (give it emission >= 1
    so it exports as Neon), four corner bars, top band, pyramid roof, finial and a hanging ring (hook) or a bail
    handle. Returns {pieces, glass (centre, build frame), ring_top}."""
    Rm = Matrix.Translation(Vector(base)) @ Matrix.Rotation(math.radians(rot), 4, "Z")
    h = w / 2
    out = [box(a, (-h, -h, 0), (h, h, plate), iron, m=Rm, name=f"{name}_plate", kind="lmetal", amp=0.03)]
    g = gw / 2
    out.append(box(a, (-g, -g, plate - 0.005), (g, g, plate + gh + 0.005), glass, m=Rm, name=f"{name}_glass",
                   kind="glass", tint=1.0))
    bh = bar / 2
    bc = h - bh - 0.005
    for i, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        out.append(box(a, (sx * bc - bh, sy * bc - bh, plate + 0.003), (sx * bc + bh, sy * bc + bh, plate + gh - 0.003),
                       iron, m=Rm, name=f"{name}_bar{i}", kind="lmetal", amp=0.03))
    zb = plate + gh
    out.append(box(a, (-h, -h, zb), (h, h, zb + band), iron, m=Rm, name=f"{name}_band", kind="lmetal", amp=0.03))
    zr = zb + band + 0.003
    rb, rt_ = h * 1.07, h * 0.36
    q = [(-rb, -rb, zr), (rb, -rb, zr), (rb, rb, zr), (-rb, rb, zr),
         (-rt_, -rt_, zr + roof), (rt_, -rt_, zr + roof), (rt_, rt_, zr + roof), (-rt_, rt_, zr + roof)]
    out.append(box_pts(a, [Rm @ Vector(p) for p in q], iron, name=f"{name}_roof", kind="lmetal", amp=0.03))
    zf = zr + roof + 0.003
    out.append(box(a, (-0.15, -0.15, zf), (0.15, 0.15, zf + fin - 0.006), iron, m=Rm, name=f"{name}_finial",
                   kind="lmetal", amp=0.03))
    top = zf + fin - 0.006
    RR, RT = 0.20, 0.06
    if hook:
        cz = top - 0.01 + RR + RT
        ax = (Rm.to_3x3() @ Vector(ring_axis)).normalized()
        cen = Rm @ Vector((0, 0, cz))
        ring = [cen + ax * (math.cos(2 * math.pi * k / 6) * RR) + Z * (math.sin(2 * math.pi * k / 6) * RR)
                for k in range(6)]
        out.append(tube(a, ring, RT, 3, True, iron, up=tuple(ax.cross(Z)), twist=True, name=f"{name}_ring",
                        kind="lmetal", tint=0.9))
        ring_top = Rm @ Vector((0, 0, cz + RR + RT))
    else:
        arc = [Rm @ Vector((math.cos(t) * 0.42, 0.0, zr + 0.06 + math.sin(t) * 0.55))
               for t in [math.radians(x_) for x_ in (0, 36, 72, 108, 144, 180)]]
        out.append(tube(a, arc, 0.035, 3, False, iron, up=tuple(Rm.to_3x3() @ Vector((0, 1, 0))), twist=True,
                        name=f"{name}_bail", kind="lmetal", tint=0.9))
        ring_top = Rm @ Vector((0, 0, top + 0.40))
    return {"pieces": out, "glass": Rm @ Vector((0, 0, plate + gh / 2)), "ring_top": ring_top}


def bracket(a, hang, wall, n, z_arm, ring_top, key, w=0.125, strap=1.2, arm_t=0.25, name="bracket"):
    """An iron wall bracket for a hanging lantern (m068): a strap on the wall face (the plane through `wall` with
    outward normal n, horizontal) from z_arm - 0.10 up `strap`, an arm out from it to above `hang` (x, y), and a hook
    down to the lantern's ring top. 0.003 gaps where pieces meet."""
    n = Vector((n[0], n[1], 0.0)).normalized()
    u = Vector((-n.y, n.x, 0.0))
    H = Vector((hang[0], hang[1], 0.0))
    W = Vector(wall)
    d = (H - W).dot(n)                       # how far the hang point stands off the wall face
    s = (H - W).dot(u)
    base = Vector((W.x, W.y, 0.0)) + u * s

    def piece(n0, n1, u0, u1, z0, z1, nm):
        pts = [base + n * nn + u * uu + Vector((0, 0, zz)) for zz in (z0, z1)
               for nn, uu in ((n0, u0), (n1, u0), (n1, u1), (n0, u1))]
        return box_pts(a, pts, key, name=f"{name}_{nm}", kind="iron", amp=0.03)
    out = [piece(0.0, 0.12, -w, w, z_arm - 0.10, z_arm - 0.10 + strap, "strap"),
           piece(0.123, d + 0.12, -w, w, z_arm, z_arm + arm_t, "arm"),
           piece(d - 0.05, d + 0.05, -0.05, 0.05, ring_top - 0.025, z_arm + 0.003, "hook")]
    return out


# ---- stone --------------------------------------------------------------------------------------------------------------
CHIP_DIRS = {"+x-y": ((7, 0), 0, (-1, 1)), "-x+y": ((3, 4), 2, (1, -1)), "+x+y": ((1, 2), 1, (-1, -1)),
             "-x-y": ((5, 6), 3, (1, 1))}


def block(a, L, D, H, key, m=None, ch=0.16, crease=True, chips=(), chip_key=None, top_key=None, mottle=0.02,
          name=None, kind="block", **kw):
    """A chamfered stone block (m070 / m056 brick: 36 tris), local x along L, y along D, base z 0, moved by matrix m:
    an octagon section (ch on the four vertical edges), a top band chamfered to a flat top, square bottom edges.
    crease folds each long face along its diagonal (one bottom corner in 0.03). chips = [(corner, size)] with corner
    in "+x-y", "-x+y", "+x+y", "-x-y" breaks those top corners (chip_key on the broken facets)."""
    hl, hd, e = L / 2, D / 2, ch
    oct_ = [(hl, -hd + e), (hl, hd - e), (hl - e, hd), (-hl + e, hd), (-hl, hd - e), (-hl, -hd + e), (-hl + e, -hd),
            (hl - e, -hd)]
    r0 = [Vector((x, y, 0.0)) for x, y in oct_]
    r1 = [Vector((x, y, H - e)) for x, y in oct_]
    top = [Vector((hl - e, -hd + e, H)), Vector((hl - e, hd - e, H)), Vector((-hl + e, hd - e, H)),
           Vector((-hl + e, -hd + e, H))]
    if crease:
        r0[7].y += 0.03
        r0[3].y -= 0.03
    chip_vs = []
    for corner, s in chips:
        ring_i, top_i, inward = CHIP_DIRS[corner]
        for i in ring_i:
            r1[i].z -= s * 0.85
        top[top_i] += Vector((inward[0], inward[1], 0.0)).normalized() * s * 0.55 + Vector((0, 0, -s * 0.45))
        chip_vs += [8 + ring_i[0], 8 + ring_i[1], 16 + top_i]
    pts = r0 + r1 + top
    if m is not None:
        pts = [m @ p for p in pts]
    polys = [list(reversed(range(8)))]
    polys += [[k, (k + 1) % 8, 8 + (k + 1) % 8, 8 + k] for k in range(8)]
    polys += [[8, 9, 17, 16], [9, 10, 17], [10, 11, 18, 17], [11, 12, 18], [12, 13, 19, 18], [13, 14, 19],
              [14, 15, 16, 19], [15, 8, 16], [16, 17, 18, 19]]
    p = shell(a, pts, polys, key, name=name, kind=kind, **kw)
    if chip_vs:
        cv = {p.vs[i] for i in chip_vs}
        paint(a, [f for f in p.fs if any(v in cv for v in f.verts)], chip_key or key)
    if top_key:
        paint(a, [p.fs[-1]], top_key)
    if mottle:
        texture(a, p.vs, mottle, seed(name or "block"), scale=0.35)
    return p


def rock(a, size, loc, key, seed_=1, rings=None, jitter=0.09, rot=0.0, lean=(0.0, 0.0), tilt=(0.0, 0.0),
         facet_var=0.0, name=None, kind="rock"):
    """A big-faceted rock or rubble lump: K.hull_rock with its flat bottom KEPT (a closed shell), placed by the current
    frame and registered. size = full (x, y, z) extent, base at loc.z; rings default K.DOME."""
    vs = K.hull_rock(a, size, loc=loc, seed=seed_, mat=key, rings=rings or K.DOME, jitter=jitter, rot=rot, lean=lean,
                     tilt=tilt, keep_bottom=True, facet_var=facet_var)
    if XF[-1] != Matrix.Identity(4):
        bmesh.ops.transform(a.bm, matrix=XF[-1], verts=vs)
    full = TAG[-1] + name if name else None
    if full:
        PIECES.append((kind, full, sum((v.co for v in vs), Vector()) / len(vs)))
    return Piece(vs, K.faces_of(vs), name=full)


def stone(a, c, size, key, rot=0.0, seed_=1, low_key=None, name="stone", kind="stone"):
    """A chunky faceted block (m064 / m068): a jittered box hull with two top corners broken off and a flat bottom;
    its lowest 30 % in low_key (by height)."""
    r_ = random.Random(seed_)
    sx, sy, sz = size[0] / 2, size[1] / 2, size[2]
    Rm = R(c, rot)
    pts = [Vector((x * sx * r_.uniform(0.92, 1.0), y * sy * r_.uniform(0.92, 1.0), 0.0))
           for x, y in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
    for k, (x, y) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        t = Vector((x * sx * r_.uniform(0.85, 0.95), y * sy * r_.uniform(0.85, 0.95), sz * r_.uniform(0.92, 1.0)))
        if k in (0, 2):
            cut = r_.uniform(0.28, 0.38)
            pts += [t - Vector((x * sx * cut, 0, 0)), t - Vector((0, y * sy * cut, 0)), t - Vector((0, 0, sz * cut * 1.1))]
        else:
            pts.append(t)
    p = hull(a, [Rm @ q for q in pts], key, name=name, kind=kind, amp=0.03)
    if low_key:
        z0 = min(v.co.z for v in p.vs)
        paint(a, [f for f in p.fs if f.is_valid and f.calc_center_median().z < z0 + 0.30 * sz], low_key)
    texture(a, p.vs, 0.05, seed_, scale=1.2)
    return p


def moss(a, xy, r, h, tree, keys, seed_=1, n=7, name="moss", kind="moss"):
    """A flat lumpy moss patch (H : W <= 0.2, never a ball) draped on a top surface found by rays down `tree` (m070,
    26 tris): a lobed base ring of n points sunk 0.015, a shoulder ring at 0.6 h, a crown; the radius shrunk until the
    whole rim lies on the same top (never hanging over an edge). keys = (dark base, mid shoulder, light crown).
    Returns the Piece or None if nothing is under xy. Build-frame coordinates (outside frame())."""
    rg = random.Random(seed_)
    down = Vector((0, 0, -1))

    def hz(x, y):
        q = tree.ray_cast(Vector((x, y, 200.0)), down, 400.0)
        return q[0].z if q[0] is not None else None
    z = hz(*xy)
    if z is None:
        return None
    ph = rg.uniform(0, 2 * math.pi)
    fr = [rg.uniform(0.94, 1.0) if k % 2 == 0 else rg.uniform(0.62, 0.80) for k in range(n)]
    fm = [rg.uniform(0.60, 0.76) for _ in range(n)]
    hm = [rg.uniform(0.50, 0.72) for _ in range(n)]
    sq, rot = rg.uniform(0.55, 0.75), rg.uniform(0, math.pi)

    def at(t, rr):
        u, v = math.cos(t) * rr, math.sin(t) * rr * sq
        return (xy[0] + u * math.cos(rot) - v * math.sin(rot), xy[1] + u * math.sin(rot) + v * math.cos(rot))
    for _ in range(14):
        base = [at(ph + 2 * math.pi * k / n, r * fr[k]) for k in range(n)]
        zs = [hz(x, y) for x, y in base]
        if all(q is not None and abs(q - z) <= 0.06 for q in zs):
            break
        r *= 0.9
    else:
        return None
    h = min(h, 0.4 * r)
    pts = [Vector((x, y, q - 0.015)) for (x, y), q in zip(base, zs)]
    for k in range(n):
        x, y = at(ph + 2 * math.pi * (k + 0.5) / n, r * fm[k])
        pts.append(Vector((x, y, (hz(x, y) or z) + h * hm[k])))
    pts.append(Vector((xy[0] + rg.uniform(-0.1, 0.1) * r, xy[1] + rg.uniform(-0.1, 0.1) * r, z + h)))
    polys = [list(reversed(range(n)))]
    for k in range(n):
        k1 = (k + 1) % n
        polys += [[k, k1, n + k], [k1, n + k1, n + k]]
    for k in range(n):
        polys.append([n + k, n + (k + 1) % n, 2 * n])
    dark, midk, light = keys
    fkeys = [dark] + [midk] * (2 * n) + [light] * n
    p = shell(a, pts, polys, midk, keys=fkeys, name=name, kind=kind, amp=0.03)
    GEO.setdefault("moss", []).append({"name": p.name, "r": round(r, 3), "h": round(h, 3), "z": round(z, 3)})
    return p


# ---- foliage: the tent leaf and ivy ---------------------------------------------------------------------------------------
# the five-point ivy outline (m056 / m070): (lateral, along the blade) from the stalk notch, tip first
LEAF_OUT = ((0.0, 0.92), (0.22, 0.60), (0.56, 0.50), (0.40, 0.05), (0.0, 0.0), (-0.40, 0.05), (-0.56, 0.50),
            (-0.22, 0.60))
LEAF_POLYS = [[8, i, (i + 1) % 8] for i in range(8)] + [[9, (i + 1) % 8, i] for i in range(8)]
IVY = dict(
    clr=0.012,          # stem and leaf clearance off the stone
    keep=0.10,          # leaves keep this far from the keep-out pieces (posts, ropes, canvas)
    r_main=0.12, r_branch=0.08, pad_w=0.55, pad_t=0.10,
    leaf_ct=0.38,       # the tent's centre along the blade
    rise=0.22,          # the top centre raised rise x size: eight facets about 25 deg round it (a low tent)
    fold=0.0, curl=0.10,
    tone_depth={"dark": (-0.7, -0.35), "green": (-0.2, 0.3), "lime": (0.35, 0.7)},   # notch depth / r off the stem
    tone_tilt={"dark": (16.0, 26.0), "green": (20.0, 32.0), "lime": (26.0, 40.0)},
    roll=(16.0, 34.0),
    tones=(0.32, 0.40),  # shares of lime, then green (the rest dark), by height rank
)


def leaf_points(N, d, nL, size, s=None):
    """The 16-tri five-point leaf as a low tent (m070): its top centre raised rise x size (midrib and vein crease) so
    its eight facets tilt about 25 deg each round it and never all turn edge-on together from any side (STAGES' 5 deg
    sweep); the tip curled back; a bottom centre 0.03 under. N = stalk notch, d = blade direction, nL = face normal."""
    s = s or IVY
    x = Vector(d).cross(Vector(nL)).normalized()
    nL = x.cross(Vector(d)).normalized()
    d = Vector(d)
    out = [N + (x * u + d * v) * size + nL * ((s["fold"] * abs(u) - s["curl"] * v * v) * size) for u, v in LEAF_OUT]
    c = N + d * s["leaf_ct"] * size + nL * (-s["curl"] * s["leaf_ct"] ** 2 * size)
    return out + [c + nL * s["rise"] * size, c - nL * 0.03 * size]


def leaf(a, N, d, nL, size, key, name=None, kind="leaf", s=None, **kw):
    """One tent leaf (leaf_points) as a closed shell; registered in LEAVES with its face normal for the sweep."""
    p = shell(a, leaf_points(Vector(N), d, nL, size, s), LEAF_POLYS, key, name=name, kind=kind, amp=kw.pop("amp", 0.04),
              **kw)
    if p.name:
        LEAVES.append({"name": p.name, "n": [round(x, 5) for x in (XF[-1].to_3x3() @ Vector(nL)).normalized()],
                       "kind": kind, "size": size})
    return p


def leaf_frame(n, u, g, side, tone="green", kind="wall", rg=None, s=None):
    """Blade direction and face normal for a leaf on a surface with outward normal n, along-direction u and hanging
    direction g (m070): the blade turned from g toward the side (phi), tilted out of the surface (tau, lime outermost
    and steepest) and rolled about itself, so leaves face out along many azimuths, never all edge-on from one side."""
    s = s or IVY
    rg = rg or random.Random(0)
    n, u, g = Vector(n), Vector(u), Vector(g)
    if kind == "lip":
        phi, tau = math.radians(rg.uniform(5.0, 35.0)), math.radians(rg.uniform(5.0, 18.0))
    else:
        phi, tau = math.radians(rg.uniform(15.0, 62.0)), math.radians(rg.uniform(*s["tone_tilt"][tone]))
    perp = (u - g * u.dot(g)).normalized() * side
    dw = (g * math.cos(phi) + perp * math.sin(phi)).normalized()
    d = dw * math.cos(tau) + n * math.sin(tau)
    nL = n * math.cos(tau) - dw * math.sin(tau)
    rho = math.radians(rg.uniform(*s["roll"])) * (side if rg.random() < 0.75 else -side)
    nL = (nL * math.cos(rho) + d.cross(nL) * math.sin(rho)).normalized()
    return d.normalized(), nL


_PDIRS = (Vector((1.0, 0.0131, 0.0217)).normalized(), Vector((-0.0173, 1.0, 0.0119)).normalized(),
          Vector((0.0151, -0.0191, 1.0)).normalized())


def parity_in(tree, p):
    """Ray parity: p is inside the closed shell(s) of tree if two of three skewed rays cross an odd number of times."""
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


class Wall:
    """A stone face for ivy: o on the face plane at s = 0, z = 0; n outward; u along the face (horizontal)."""

    def __init__(self, name, o, n, u):
        self.name, self.o, self.n, self.u = name, Vector(o), Vector(n), Vector(u)

    def p(self, s, z, d=0.0):
        return self.o + self.u * s + Z * z + self.n * d


def _surf(w, s, z, tree):
    h = tree.ray_cast(w.p(s, z, 1.0), -w.n, 1.6)
    return -0.3 if h[0] is None else 1.0 - h[3]


def _wall_points(w, sz, r, tree, clr):
    n = len(sz)
    seg = []
    for i in range(n - 1):
        (s0, z0), (s1, z1) = sz[i], sz[i + 1]
        m = max(2, int(math.hypot(s1 - s0, z1 - z0) / 0.08) + 1)
        best = -0.3
        for k in range(m + 1):
            f = k / m
            s, z = s0 + (s1 - s0) * f, z0 + (z1 - z0) * f
            for ds, dz in ((0, 0), (r, 0), (-r, 0), (0, r), (0, -r)):
                best = max(best, _surf(w, s + ds, z + dz, tree))
        seg.append(best)
    out = []
    for i, (s, z) in enumerate(sz):
        m_ = _surf(w, s, z, tree) if n == 1 else max(seg[max(i - 1, 0)], seg[min(i, n - 2)])
        out.append(w.p(s, z, max(m_, 0.0) + clr + r))
    return out


def _point_at_z(pts, z):
    for p, q in zip(pts, pts[1:]):
        if (p.z - z) * (q.z - z) <= 0 and abs(p.z - q.z) > 1e-6:
            return p + (q - p) * ((z - p.z) / (q.z - p.z))
    return min(pts, key=lambda p: abs(p.z - z))


def stem_points(pts, normals, r):
    """A square-section stem (one closed shell, m056): a ring of 4 at every point in the mitre plane of its kink, one
    face toward the surface normal, flat end caps. Returns (points, polys)."""
    n = len(pts)
    rings = []
    for i in range(n):
        if i == 0 or i == n - 1:
            t = (pts[1] - pts[0]).normalized() if i == 0 else (pts[-1] - pts[-2]).normalized()
            d1 = d2 = t
        else:
            d1, d2 = (pts[i] - pts[i - 1]).normalized(), (pts[i + 1] - pts[i]).normalized()
            t = (d1 + d2).normalized()
        sv = Vector(normals[i]).cross(t)
        if sv.length < 1e-5:
            sv = t.orthogonal()
        sv.normalize()
        w = t.cross(sv).normalized()
        kd, sc = d2 - d1, 1.0
        if kd.length > 1e-5:
            kd.normalize()
            sc = 1.0 / max(math.cos(d1.angle(d2) / 2), 0.35)
        ring = []
        for a_, b_ in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
            off = (sv * a_ + w * b_) * r
            if sc != 1.0:
                off += kd * off.dot(kd) * (sc - 1.0)
            ring.append(pts[i] + off)
        rings.append(ring)
    allp = [p for rg in rings for p in rg]
    polys = [[0, 1, 2, 3]]
    for i in range(n - 1):
        b0, b1 = 4 * i, 4 * (i + 1)
        polys += [[b0 + k, b0 + (k + 1) % 4, b1 + (k + 1) % 4, b1 + k] for k in range(4)]
    polys.append([4 * (n - 1) + k for k in (3, 2, 1, 0)])
    return allp, polys


def _leaf_samples(pts):
    o = pts[:8]
    return pts + [(o[i] + o[(i + 1) % 8]) / 2 for i in range(8)] + [(pts[8] + o[i]) / 2 for i in range(8)] + \
        [(c + o[i] + o[(i + 1) % 8]) / 3 for c in pts[8:10] for i in range(8)]


def _sd(p, tree):
    h = tree.find_nearest(p)
    d = h[3] if h[0] is not None else 9.0
    if d < 0.6 and parity_in(tree, p):
        return -d
    return min(d, p.z)


def _push_clear(pts, nL, tree, clr, max_push=0.3):
    push = 0.0
    for _ in range(8):
        m = min(_sd(p, tree) for p in _leaf_samples(pts))
        if m >= clr - 1e-4:
            return pts, round(push, 3)
        dv = clr - m + 0.003
        push += dv
        if push > max_push:
            return None
        pts = [p + nL * dv for p in pts]
    return None


def _depth_in(pts, stems):
    if stems is None:
        return 0.0
    worst = 0.0
    for p in _leaf_samples(pts):
        h = stems.find_nearest(p, 0.3)
        if h[0] is not None and parity_in(stems, p):
            worst = max(worst, h[3])
    return worst


def _swallow(pts, spts):
    if not spts:
        return 0.0
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))) - Vector((0.01, 0.01, 0.01))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))) + Vector((0.01, 0.01, 0.01))
    cand = [q for q in spts if lo.x <= q.x <= hi.x and lo.y <= q.y <= hi.y and lo.z <= q.z <= hi.z]
    if not cand:
        return 0.0
    t = BVHTree.FromPolygons(pts, LEAF_POLYS)
    return max([t.find_nearest(q)[3] for q in cand if parity_in(t, q)] or [0.0])


def _clear_of(pts, tree, lim):
    return tree is None or all(tree.find_nearest(p, lim)[0] is None for p in _leaf_samples(pts))


def _place_leaf(st, tone, rg, tree, keep, stems, spts, s):
    d, nL = leaf_frame(st["n"], st["u"], st["g"], st["side"], tone, st["kind"], rg, s)
    C, r, n, side = st["c"], st["r"], st["n"], st["side"]
    sdir = st["u"] * side
    N = C + sdir * (r - 0.03) + n * (rg.uniform(*s["tone_depth"][tone]) * r)
    size = rg.uniform(0.86, 0.95)
    res = _push_clear(leaf_points(N, d, nL, size, s), nL, tree, s["clr"])
    if res is None:
        return None
    pts, push = res
    for _ in range(5):
        dep = _depth_in(pts, stems)
        if dep <= 0.03:
            break
        pts = [p + sdir * (dep - 0.015) for p in pts]
        res = _push_clear(pts, nL, tree, s["clr"])
        if res is None:
            return None
        pts, p2 = res
        push += p2
    else:
        return None
    for _ in range(4):
        sw = _swallow(pts, spts)
        if sw <= 0.03:
            break
        pts = [p + nL * (sw - 0.015) for p in pts]
        push += sw - 0.015
    else:
        return None
    if _depth_in(pts, stems) > 0.03 or not _clear_of(pts, keep, s["keep"]):
        return None
    return {"pts": pts, "n": nL, "size": size, "push": round(push, 3)}


def ivy(a, runs, walls, tree, keys, keep=None, seed_=1, s=None, name="ivy"):
    """Ivy runs over stone (m070 / m056): per run a wall face it climbs and the top it lips over; per stem a square
    stem shell (lip = (s, pad (x, y)) starts it from a pad on the top; parent = (stem id, z) branches it off another
    stem's side), its leaves at stations along it, each a tent leaf turned by leaf_frame, pushed clear of the stone,
    slid off the stems and kept `keep` off the keep-out tree; of 12 tries per station the one farthest from the run's
    leaves so far is kept. Tones by height rank (32 % lime, 40 % green, the rest dark). keys = {lime, green, dark,
    stem}. runs = {run: dict(wall, top, stems=[dict(id, r, sz=[(s, z)], n, lip=(s, (x, y)), lipn, parent=(id, z))])},
    walls = {name: Wall}. Build frame (outside frame()). Returns {leaves, dropped}."""
    s = s or IVY
    rg = random.Random(seed_)
    stations, scos, spolys, dropped = [], [], [], []
    for rn, run in runs.items():
        w = walls[run["wall"]]
        top = run["top"]
        geo = {}
        for st in run["stems"]:
            r = st["r"]
            pts, nrm, seg, pad = [], [], [], None
            if "lip" in st:
                sl, pxy = st["lip"]
                p0 = Vector((pxy[0], pxy[1], top + 0.005 + s["pad_t"] + r - 0.06))
                e = w.p(sl, 0.0, 0.0) - w.n * 0.22
                p1 = Vector((e.x, e.y, top + s["clr"] + r))
                pc = w.p(sl, top + s["clr"] + r, max(_surf(w, sl, top - 0.3, tree), 0.0) + s["clr"] + r)
                pts += [p0, p1, pc]
                nrm += [Z, Z, (Z + w.n).normalized()]
                seg += [("lip", Z), ("lip", Z), ("wall", w.n)]
                pad = Vector((pxy[0], pxy[1], top + 0.005))
            wp = _wall_points(w, st["sz"], r, tree, s["clr"])
            if "parent" in st:
                pid, at = st["parent"]
                pp = geo[pid]["pts"]
                p = _point_at_z(pp, at)
                tp = min(zip(pp, pp[1:]), key=lambda q: abs((q[0].z + q[1].z) / 2 - at))
                t = (tp[1] - tp[0]).normalized()
                dv = wp[0] - p
                perp = (dv - t * dv.dot(t) - w.n * dv.dot(w.n)).normalized()
                pts.append(p + perp * (geo[pid]["r"] + r - 0.03))
                pts.append(p + perp * (geo[pid]["r"] + r + 0.12) + (dv - perp * dv.dot(perp)) * 0.15)
                nrm += [w.n, w.n]
            pts += wp
            nrm += [w.n] * len(wp)
            seg += [("wall", w.n)] * (len(pts) - 1 - len(seg))
            geo[st["id"]] = {"pts": pts, "r": r, "seg": seg, "spec": st}
            ps, pl = stem_points(pts, nrm, r)
            o_ = len(scos)
            scos += [Vector(q) for q in ps]
            spolys += [[o_ + i for i in q] for q in pl]
            sp = shell(a, ps, pl, keys["stem"], name=f"{name}_stem_{rn}_{st['id']}", kind="stem", amp=0.03)
            texture(a, sp.vs, 0.03, len(spolys), scale=0.8)
            if pad is not None:
                u, v = w.u, Z.cross(w.u)
                hw, ht = s["pad_w"] / 2, s["pad_t"]
                sq = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
                pp_ = [pad + (u * a_ + v * b_) * hw for a_, b_ in sq] + \
                      [pad + Z * ht + (u * a_ + v * b_) * (hw - 0.06) for a_, b_ in sq]
                shell(a, pp_, [[3, 2, 1, 0], [4, 5, 6, 7]] + [[k, (k + 1) % 4, 4 + (k + 1) % 4, 4 + k] for k in range(4)],
                      mix(keys["stem"], keys["dark"], 0.3), name=f"{name}_pad_{rn}_{st['id']}", kind="pad", amp=0.02)
        for sid, g in geo.items():
            st, pts, seg = g["spec"], g["pts"], g["seg"]
            for kind, count in (("lip", st.get("lipn", 0)), ("wall", st.get("n", 0))):
                segs = [i for i, (k, _) in enumerate(seg) if k == kind]
                if not count or not segs:
                    continue
                lens = [(pts[i + 1] - pts[i]).length for i in segs]
                total = sum(lens)
                start = 0.25 if (kind == "wall" and "parent" in st) else 0.12
                usable, acc = [], 0.0
                for i, ln in zip(segs, lens):
                    usable.append((acc, i, ln))
                    acc += ln
                for j in range(count):
                    uu = start + (total - start - 0.1) * (j + 0.5) / count
                    i, f = usable[-1][1], 1.0
                    for a0, ii, ln in usable:
                        if a0 <= uu <= a0 + ln + 1e-6:
                            i, f = ii, (uu - a0) / max(ln, 1e-6)
                            break
                    p = pts[i] + (pts[i + 1] - pts[i]) * f
                    if kind == "lip":
                        nn, gdir = (Z * 0.5 + w.n * 0.866).normalized(), (w.n * 0.5 - Z * 0.866).normalized()
                    else:
                        nn, gdir = w.n, -Z
                    stations.append({"c": p, "n": nn, "u": w.u, "g": gdir, "r": g["r"], "kind": kind,
                                     "side": 1 if (j + len(stations)) % 2 == 0 else -1,
                                     "h": 1.2 if kind == "lip" else p.z / top, "run": rn, "stem": sid})
    stems = BVHTree.FromPolygons(scos, spolys) if spolys else None
    spts = scos + [sum((scos[i] for i in p), Vector()) / len(p) for p in spolys] + \
        [(scos[p[i]] + scos[p[(i + 1) % len(p)]]) / 2 for p in spolys for i in range(len(p))]
    order = sorted(range(len(stations)), key=lambda i: -(stations[i]["h"] + rg.uniform(-0.25, 0.25)))
    nl, ng = round(s["tones"][0] * len(stations)), round(s["tones"][1] * len(stations))
    tone = {i: ("lime" if rank < nl else "green" if rank < nl + ng else "dark") for rank, i in enumerate(order)}
    placed, n_leaves = {}, 0
    for i, st in enumerate(stations):
        mine = placed.setdefault(st["run"], [])
        cands = []
        for k in range(12):
            res = _place_leaf(dict(st, side=st["side"] if k % 2 == 0 else -st["side"]), tone[i], rg, tree, keep,
                              stems, spts, s)
            if res is not None:
                ctr = sum(res["pts"][:8], Vector()) / 8
                cands.append((min([(ctr - q).length for q in mine] or [9.0]), res))
        if not cands:
            dropped.append((st["run"], st["stem"], [round(v, 2) for v in st["c"]]))
            continue
        res = max(cands, key=lambda x: x[0])[1]
        nm = f"{name}_leaf_{st['run']}_{n_leaves}"
        lp = shell(a, res["pts"], LEAF_POLYS, keys[tone[i]], name=nm, kind="leaf", amp=0.04)
        LEAVES.append({"name": lp.name, "n": [round(x, 5) for x in res["n"]], "kind": st["kind"], "tone": tone[i],
                       "run": st["run"], "size": res["size"], "push": res["push"]})
        mine.append(sum(res["pts"][:8], Vector()) / 8)
        n_leaves += 1
    GEO.setdefault("ivy", {})[name] = {"leaves": n_leaves, "dropped": len(dropped)}
    return {"leaves": n_leaves, "dropped": dropped}
