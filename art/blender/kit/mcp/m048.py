"""048 Dock (references/048.png): a raised timber pier on six tall square legs. Post centres W 8 across x 2 bays of 8
along, deck top 5.6, post tops 8.3; overall about 10.6 W (bolt heads) x 19.2 L (boards) x 8.3 H.

    import importlib, kit_models, m048; importlib.reload(kit_models); importlib.reload(m048); m048.build()

Build frame (studs): long axis Y, the open (walk-on) end at -Y, the roped end at +Y, +X right, ground z 0, centred on
x 0 / y 0. W08 owns Dock* and Boardwalk*: names TimberDock*, keys m048_*.

Seam contract (spec 2.1, binding):
- leg feet z 0, flat (the water tiles' bed bottom; legs rise through bed 0-0.2 and water 0.25-1.0);
- deck top (walk surface) z 5.6 +- 0.02, flat (flush with M043's lower lawn);
- open end y -9.6 (the end board's outer face): no rope and no brace above the deck there;
- roped end y +9.6; sides: boards to x +-5.1, bolt heads to x +-5.28, nothing past +-5.4;
- post centres x +-4.0, y -8 / 0 / +8.

Every piece is its own closed shell (no booleans), seated by contact or sunk 0.02 into what carries it:
- 6 posts, ground -> cap (one shell each, cap chamfer 0.12), legs darkened by colour below the beams (position only);
- 10 bolt blocks (each post's outer long face, plus the end face of the four corner posts) with brass bolt heads;
- 10 full-width chamfered boards across the width (1.83 x 0.85, 0.10 gaps, a seam at the middle posts); the boards
  that meet a post row are notched round the post (open notch to the deck edge, 0.02 clear of the post);
- 2 side beams (outer face on the posts' inner faces) and 3 crossbeams (y -8 / 0 / +8) between them;
- 4 knee braces on the long sides and 2 on the +Y end (leg face -> beam underside), an X brace on the -Y end with a
  bolt at the crossing;
- rope: 2 coils per post (twisted 6-sided tubes round the post), 5 swags (both long sides, the +Y end; none across the
  open -Y end) whose ends sit inside the coils, a two-loop knot on the +Y swag by the +X post.
Parts (exploded / key labels): TimberDockPost (the +X/-Y corner post with its blocks, bolts and coils),
TimberDockDeck, TimberDockBeam, TimberDockCrossbeam, TimberDockBrace, TimberDockRope (one long-side swag with knob ends).

Stages 5-6: nothing (decisions 9 / 11: the sheet shows no water, glow, light or effect). See M048_spec.md.
"""
import math
import random
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise

import kit_mcp as K
import kit_models as M
import m012
import m033
import m040

NUM, TITLE, SHEET = 48, "Dock", "M048"
OFF = "m048_offset"
PFX = "_m048_"
HERO = "TimberDock"
POST_P, DECK_P, BEAM_P = "TimberDockPost", "TimberDockDeck", "TimberDockBeam"
CROSS_P, BRACE_P, ROPE_P = "TimberDockCrossbeam", "TimberDockBrace", "TimberDockRope"
PARTS = (POST_P, DECK_P, BEAM_P, CROSS_P, BRACE_P, ROPE_P)

# ---- builder constants (decision 4) ---------------------------------------------------------------------------------
W = 8.0                 # post centres across (x)
BAY = 8.0               # post centres along (y): two bays
DECK_TOP = 5.6          # walk surface
POST_TOP = 8.3
POST = 1.3              # post section
PH = POST / 2
CAP_CH = 0.12           # cap chamfer
PLANK_T = 0.85
BOARD_W, GAP, NBOARDS = 1.83, 0.10, 10
DECK_X = 5.1            # board ends
DECK_Y = (NBOARDS * BOARD_W + (NBOARDS - 1) * GAP) / 2      # 9.6
BOARD_CH = 0.06
BEAM_W, BEAM_D = 0.9, 1.3
BEAM_TOP = DECK_TOP - PLANK_T          # 4.75
BEAM_BOT = BEAM_TOP - BEAM_D           # 3.45
BEAM_Y = 9.15
SINK = 0.02
BLOCK_PROUD, BLOCK_Z = 0.35, (3.55, 4.55)
BOLT_R, BOLT_H, BOLT_DOME = 0.275, 0.22, 0.06
ROPE_R = 0.22           # rope ring circumradius (6-sided coils read 0.38-0.44 thick, 5-sided swags 0.36-0.44)
ROPE_MEAN = 0.195       # the rope's mean radius (seating, knots)
ROPE_SIDES = 5          # swags and knots
COIL_SIDES = 6          # the coils (the most seen rope): rounder
COIL_Z = (6.52, 6.92)
COIL_D = PH + ROPE_MEAN - SINK            # coil centreline off the post axis on the flats
COIL_C = 0.56                          # octagon corner: where the flats end
SWAG_Z = 6.72                          # swag ends: between the two coils, at the coil centreline
SWAG_LOW = {"side": 6.15, "end": 6.05}
SWAG_SEGS = 12
PINCH = 0.08            # every other rope ring this much thinner: the strand bumps of the twist
POSTS = [(sx * W / 2, j * BAY) for j in (-1, 0, 1) for sx in (1, -1)]
LEG_DARK = (2.85, 3.15, BEAM_BOT)      # leg blend rings: full dark below 2.85, 2 steps to wood_deep at 3.45
CAP_RINGS = (7.2, 7.75)                # cap blend rings above the coils
POST_LEVELS = (0.0,) + LEG_DARK + CAP_RINGS + (POST_TOP - CAP_CH,)

WOOD, WOOD_LIGHT, WOOD_DEEP, WOOD_DARK = "m048_wood", "m048_wood_light", "m048_wood_deep", "m048_wood_dark"
ROPE, ROPE_DARK, BRASS, MARK = "m048_rope", "m048_rope_dark", "m048_brass", "m048_marker"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, metal, low specular). Stage 4 (M048_spec.md "Stage 4"): calibrated hexes.
PALETTE = {
    WOOD: ("#BB722E", 0.85, 0.0, True),
    WOOD_LIGHT: ("#C97E37", 0.85, 0.0, True),
    WOOD_DEEP: ("#88491A", 0.85, 0.0, True),
    WOOD_DARK: ("#633D20", 0.9, 0.0, True),
    ROPE: ("#F4CF80", 0.95, 0.0, True),
    ROPE_DARK: ("#99601A", 0.95, 0.0, True),
    BRASS: ("#EBC772", 0.4, 0.5, False),
    MARK: ("#7E7978", 0.7, 0.0, False),
}
# calibration targets (spec 5.4: rendered medians of unshadowed regions on the sheet)
# wood_deep: the front cell's post faces #8D4212 (the swatch #B56734 is flat paint; the studio lights the vertical
# faces brighter than the sheet does); wood_dark: the f34 / front legs #62371C-#764521; rope_dark: the sheet's groove
# strands (front swag lower quartile #BE7019; coil median #C2761A)
TARGETS = {WOOD: ((0xE1, 0x90, 0x44), "brown"), WOOD_LIGHT: ((0xED, 0xA0, 0x52), "brown"),
           WOOD_DEEP: ((0x8D, 0x42, 0x12), "brown"), WOOD_DARK: ((0x6C, 0x3D, 0x1E), "brown"),
           ROPE: ((0xF8, 0xD0, 0x88), "vivid"), ROPE_DARK: ((0xBE, 0x70, 0x19), "vivid"),
           BRASS: ((0xF7, 0xD8, 0x94), "vivid")}


def palette():
    for k, (hexcol, rough, metal, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, metal=metal, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, metal=metal, low_spec=low)


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS)."""
    keys = keys or list(TARGETS)
    for k in keys:
        K.fk().material(k)
    try:
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


def _mix(k1, k2, t, step=0.05):
    t = round(max(0.0, min(1.0, t)) / step) * step
    return K.mix_key(k1, k2, round(t, 2))


GEO = {}                # measured levels and counts recorded while building (for the level check)


# ---- solid builders (each call adds one closed shell; winding fixed by construction, checked by volume) ------------
def _solid(a, pts, faces, key, tint=1.0):
    """One closed shell from points and face index lists (all wound one way); flipped as a whole if the signed volume
    comes out negative. Returns (verts, faces)."""
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


def _inset(poly, d):
    """A CCW polygon offset inward by d (mitred corners; works at reflex corners too)."""
    n = len(poly)
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % n])
        e0, e1 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n0, n1 = Vector((-e0.y, e0.x)), Vector((-e1.y, e1.x))
        det = n0.x * n1.y - n0.y * n1.x
        if abs(det) < 1e-9:
            q = p1 + n0 * d
        else:
            c0, c1 = p0.dot(n0) + d, p1.dot(n1) + d
            q = Vector(((c0 * n1.y - n0.y * c1) / det, (n0.x * c1 - c0 * n1.x) / det))
        out.append((q.x, q.y))
    return out


def _prism(a, poly, levels, top, ch, key, tint=1.0, splits=()):
    """A vertical prism of a CCW outline: full-outline rings at `levels` (ascending, the first is the bottom), then a
    top ring at `top`, inset by `ch` (a one-segment chamfer on the top edges) when ch > 0. `splits` = outline index
    pairs along which the top and bottom faces are cut (a notched outline into near-rectangles, so the n-gon fill
    leaves no sliver triangles)."""
    n = len(poly)
    rings = [[(x, y, z) for x, y in poly] for z in levels]
    rings.append([(x, y, top) for x, y in (_inset(poly, ch) if ch > 0 else poly)])
    pts = [p for r in rings for p in r]
    R = len(rings)
    faces = [list(reversed(range(n)))]
    for i in range(R - 1):
        for k in range(n):
            k1 = (k + 1) % n
            faces.append([i * n + k, i * n + k1, (i + 1) * n + k1, (i + 1) * n + k])
    faces.append([(R - 1) * n + k for k in range(n)])
    vs, fs = _solid(a, pts, faces, key, tint)
    for i, j in splits:
        for base in (0, (R - 1) * n):
            va, vb = vs[base + i], vs[base + j]
            f = next(f for f in va.link_faces if vb in f.verts)     # the cap (the two are never neighbours)
            nf, _ = bmesh.utils.face_split(f, va, vb)
            fs.append(nf)
    return vs, fs


def _rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _box(a, x0, y0, z0, x1, y1, z1, key, tint=1.0):
    return _prism(a, _rect(x0, y0, x1, y1), [z0], z1, 0.0, key, tint)


HEXA = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (0, 4, 7, 3), (1, 2, 6, 5)]


def _plank2d(a, quad, w0, w1, axis, key, tint=1.0):
    """A board whose outline is the 2D quad `quad` [(u, z)] extruded between w0 and w1 along the horizontal `axis`
    ("x": u runs along y, thickness along x; "y": u runs along x, thickness along y)."""
    pts = []
    for w in (w0, w1):
        for u, z in quad:
            pts.append((w, u, z) if axis == "x" else (u, w, z))
    return _solid(a, pts, HEXA, key, tint)


def _brace_quad(c_lo, c_hi, half, u_cut, z_cut):
    """The (u, z) outline of a brace with centreline c_lo -> c_hi and half-width `half`: its low end cut vertical at
    u = u_cut (against a leg face), its high end cut horizontal at z = z_cut (against a beam underside)."""
    c_lo, c_hi = Vector(c_lo), Vector(c_hi)
    d = (c_hi - c_lo).normalized()
    n = Vector((-d.y, d.x))
    pts = {}
    for s in (1, -1):
        c = c_lo + n * (half * s)
        pts[("lo", s)] = c + d * ((u_cut - c.x) / d.x)
        pts[("hi", s)] = c + d * ((z_cut - c.y) / d.y)
    return [tuple(pts[k]) for k in (("lo", -1), ("hi", -1), ("hi", 1), ("lo", 1))]


def _tube(a, path, r, sides, closed, key, groove=None, tint=1.0, up=(0, 0, 1), phase=0.0, pinch=0.0, twist=False):
    """A low-poly rope tube along `path`: rings of `sides` verts. twist=False (the rope): rings aligned, each quad
    split along the diagonal that climbs one side per ring, and the strands numbered (side - ring) mod sides, so a
    strand is a spiral band round the tube like the sheet's twisted rope. twist=True: each ring turned half a side
    and joined as an antiprism strip (strand = side). Every other ring is `pinch` thinner (the strand bumps). Bends
    are mitred so the tube keeps its thickness. Open tubes get flat end caps. `groove` = {strand: key}: those strands
    (by their place in the twist, never by facing) take that key; the rest keep `key`. Closed twisted paths need an
    even number of points."""
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
            off = (U * math.cos(ang) + V * math.sin(ang)) * (r * (1.0 - pinch * (i % 2)))
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


def _knob(a, c, r, key, tint=1.0, segs=8, rings=4):
    """A low-poly ball (rope knob end)."""
    c = Vector(c)
    pts = [c + Vector((0, 0, -r))]
    for i in range(1, rings):
        el = -math.pi / 2 + math.pi * i / rings
        for k in range(segs):
            az = 2 * math.pi * (k + 0.5 * (i % 2)) / segs
            pts.append(c + Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))) * r)
    pts.append(c + Vector((0, 0, r)))
    top = len(pts) - 1
    faces = []
    for k in range(segs):
        faces.append([0, 1 + (k + 1) % segs, 1 + k])
    for i in range(rings - 2):
        b0, b1 = 1 + i * segs, 1 + (i + 1) * segs
        for k in range(segs):
            k1 = (k + 1) % segs
            faces.append([b0 + k, b0 + k1, b1 + k1, b1 + k])
    last = 1 + (rings - 2) * segs
    for k in range(segs):
        faces.append([last + k, last + (k + 1) % segs, top])
    return _solid(a, pts, faces, key, tint)


def _bolt(a, c, n, key=BRASS, tint=1.0, sides=8):
    """A round brass bolt head on a face: centre c on the face, outward normal n. Sunk 0.03, BOLT_H proud, a low dome
    (BOLT_DOME) to a centre point."""
    c, n = Vector(c), Vector(n).normalized()
    u = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = (u - u.dot(n) * n).normalized()
    v = n.cross(u)
    ring = [u * math.cos(2 * math.pi * (k + 0.5) / sides) + v * math.sin(2 * math.pi * (k + 0.5) / sides)
            for k in range(sides)]
    pts = [c - n * 0.03 + d * BOLT_R for d in ring] + [c + n * BOLT_H + d * BOLT_R for d in ring]
    pts.append(c + n * (BOLT_H + BOLT_DOME))
    faces = [list(reversed(range(sides)))]
    for k in range(sides):
        k1 = (k + 1) % sides
        faces.append([k, k1, sides + k1, sides + k])
        faces.append([sides + k, sides + k1, 2 * sides])
    return _solid(a, pts, faces, key, tint)


# ---- pieces -----------------------------------------------------------------------------------------------------------
def _rng(seed):
    return random.Random(seed)


def _texture(a, vs, amp, seed, scale=0.3):
    K.texture(a, vs, amp=amp, scale=scale, jitter=0.0, seed=seed)


def _post_colour(a, fs):
    """Role and position only: wood_deep; the legs darker below the beams (full dark below 2.85, then 2 steps to
    wood_deep at the beam bottom 3.45); the cap lighter over the top (20 / 40 % above the coils, 60 % on the
    chamfer and top). By face-centre height, never by facing."""
    for f in fs:
        z = f.calc_center_median().z
        if z < LEG_DARK[0]:
            k = WOOD_DARK
        elif z < LEG_DARK[1]:
            k = _mix(WOOD_DEEP, WOOD_DARK, 0.67)
        elif z < LEG_DARK[2]:
            k = _mix(WOOD_DEEP, WOOD_DARK, 0.33)
        elif z < CAP_RINGS[0]:
            k = WOOD_DEEP
        elif z < CAP_RINGS[1]:
            k = _mix(WOOD_DEEP, WOOD_LIGHT, 0.2)
        elif z < POST_TOP - CAP_CH - 1e-4:
            k = _mix(WOOD_DEEP, WOOD_LIGHT, 0.4)
        else:
            k = _mix(WOOD_DEEP, WOOD_LIGHT, 0.6)
        f.material_index = a._mi(k)


def post_shell(a, px, py, seed):
    vs, fs = _prism(a, _rect(px - PH, py - PH, px + PH, py + PH), list(POST_LEVELS), POST_TOP, CAP_CH, WOOD_DEEP,
                    tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    _post_colour(a, fs)
    _texture(a, vs, 0.03, seed)
    return vs


def _faces_of_post(px, py):
    """Outward normals of the post faces that carry a bolt block: the outer long face, and the end face of a corner
    post."""
    out = [(math.copysign(1, px), 0)]
    if abs(py) > 1e-6:
        out.append((0, math.copysign(1, py)))
    return out


def block(a, px, py, n, seed):
    """A bolt block on the post face with outward normal n (sunk 0.02), 1.3 along the face, 1.0 tall, 0.35 proud;
    its brass bolt head centred on the outer face."""
    nx, ny = n
    z0, z1 = BLOCK_Z
    if nx:
        f = px + nx * PH
        xa, xb = sorted((f - nx * SINK, f + nx * BLOCK_PROUD))
        vs, _ = _box(a, xa, py - PH, z0, xb, py + PH, z1, WOOD_DEEP, tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
        c = (f + nx * BLOCK_PROUD, py, (z0 + z1) / 2)
    else:
        f = py + ny * PH
        ya, yb = sorted((f - ny * SINK, f + ny * BLOCK_PROUD))
        vs, _ = _box(a, px - PH, ya, z0, px + PH, yb, z1, WOOD_DEEP, tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
        c = (px, f + ny * BLOCK_PROUD, (z0 + z1) / 2)
    _texture(a, vs, 0.03, seed)
    bv, _ = _bolt(a, c, (nx, ny, 0))
    return vs + bv


def _strands(sides):
    """The rope's strand roles round the tube (spec 5.3: by the strand's place in the twist, never by the face's
    normal). Coils (6 sides, aligned rings): strands (side - ring) mod 3 = 0 / 1 / 2 are the deep groove, a 45 %
    amber and the golden lit strand, so they spiral like a three-ply rope (an even / odd split would checker). Swags
    (5 sides, twisted): strand 0 the deep groove, strand 2 amber (90 %), the rest golden. About half the rope reads
    amber, as the sheet's does (front swag quartiles #BE7019 / #E49530 / #F4C675)."""
    if sides % 3 == 0:              # the coils: three-ply, each ply dark groove -> amber -> golden lit strand
        return {k: (ROPE_DARK if k % 3 == 0 else _mix(ROPE, ROPE_DARK, 0.45)) for k in range(sides) if k % 3 != 2}
    out = {0: ROPE_DARK}
    for k in range(2, sides - 1, 2):
        out[k] = _mix(ROPE, ROPE_DARK, 0.9)
    return out


def coil_path(px, py, z):
    d, c = COIL_D, COIL_C
    pts = [(d, -c), (d, 0.0), (d, c), (c, d), (0.0, d), (-c, d), (-d, c), (-d, 0.0), (-d, -c), (-c, -d), (0.0, -d),
           (c, -d)]
    return [(px + x, py + y, z) for x, y in pts]


def coil(a, px, py, z, seed, phase=0.0):
    vs, _ = _tube(a, coil_path(px, py, z), ROPE_R, COIL_SIDES, True, ROPE, groove=_strands(COIL_SIDES), pinch=PINCH,
                  tint=1.0 + _rng(seed).uniform(-0.02, 0.02), phase=phase)
    return vs


def post(a, px, py, seed, blocks=True, coils=True):
    """One post position: the post shell, its bolt block(s) with bolts, its two coils."""
    vs = post_shell(a, px, py, seed)
    if blocks:
        for i, n in enumerate(_faces_of_post(px, py)):
            vs += block(a, px, py, n, seed + 11 * (i + 1))
    if coils:
        for i, z in enumerate(COIL_Z):
            vs += coil(a, px, py, z, seed + 31 * (i + 1), phase=(0.0, math.pi / 3)[i])
    return vs


def board_outline(i):
    """Board i (0 at -Y): a 1.83-wide rectangle across the width, with an open notch (0.02 clear) round every post it
    meets (to the deck edge), so the post stands in the board row as on the sheet's junction close-up."""
    y0 = -DECK_Y + i * (BOARD_W + GAP)
    y1 = y0 + BOARD_W
    X = DECK_X
    xb = W / 2 - PH - SINK
    bites = {}
    for px, py in POSTS:
        lo, hi = py - PH - SINK, py + PH + SINK
        if hi <= y0 or lo >= y1:
            continue
        side = "r" if px > 0 else "l"
        if lo <= y0 and hi < y1:
            bites["b" + side] = hi          # touches the board's -Y edge
        elif lo > y0 and hi >= y1:
            bites["t" + side] = lo          # touches the board's +Y edge
        else:
            raise ValueError(f"board {i}: post at {py} not at a board edge")
    # each notch's inner corner also gets a partner point straight across the board (on the far long edge), and the
    # top / bottom faces are cut along that line: near-rectangles, no sliver triangles
    pts, corner, partner = [], {}, {}

    def add(p, tag=None, role=None):
        pts.append(p)
        if tag:
            (corner if role == "c" else partner)[tag] = len(pts) - 1
    if "bl" in bites:
        add((-X, bites["bl"])); add((-xb, bites["bl"]), "bl", "c"); add((-xb, y0))
    else:
        add((-X, y0))
        if "tl" in bites:
            add((-xb, y0), "tl", "p")
    if "br" in bites:
        add((xb, y0)); add((xb, bites["br"]), "br", "c"); add((X, bites["br"]))
    else:
        if "tr" in bites:
            add((xb, y0), "tr", "p")
        add((X, y0))
    if "tr" in bites:
        add((X, bites["tr"])); add((xb, bites["tr"]), "tr", "c"); add((xb, y1))
    else:
        add((X, y1))
        if "br" in bites:
            add((xb, y1), "br", "p")
    if "tl" in bites:
        add((-xb, y1)); add((-xb, bites["tl"]), "tl", "c"); add((-X, bites["tl"]))
    else:
        if "bl" in bites:
            add((-xb, y1), "bl", "p")
        add((-X, y1))
    splits = [(corner[t], partner[t]) for t in corner]
    for e in "bt":                          # notches at both ends of one edge: cut the strip between them off too
        if e + "l" in corner and e + "r" in corner:
            splits.append((corner[e + "l"], corner[e + "r"]))
    return pts, bool(bites), (y0, y1), splits


DECK_INFO = {}


def board(a, i, seed):
    rng = _rng(seed)
    poly, notched, (y0, y1), splits = board_outline(i)
    top = DECK_TOP + rng.uniform(-0.02, 0.02)
    if not notched:                         # a small yaw on the free boards (no gap opens: <= 0.04 at the ends)
        yaw = math.radians(rng.uniform(-0.4, 0.4))
        cy = (y0 + y1) / 2
        poly = [(x * math.cos(yaw) - (y - cy) * math.sin(yaw), cy + x * math.sin(yaw) + (y - cy) * math.cos(yaw))
                for x, y in poly]
    # colour by role (one board key) and position: a broad lighter field over the deck, a few deeper boards
    field = noise.noise(Vector((0.0, (y0 + y1) / 2 * 0.12, 3.7)))
    key = WOOD
    if field > 0.12:
        key = _mix(WOOD, WOOD_LIGHT, 0.15)
    if i in (2, 7):
        key = _mix(WOOD, WOOD_DEEP, 0.15)
    vs, fs = _prism(a, poly, [BEAM_TOP - SINK, top - BOARD_CH], top, BOARD_CH, key,
                    tint=1.0 + rng.uniform(-0.03, 0.03), splits=splits)
    _texture(a, vs, 0.02, seed)
    DECK_INFO[i] = {"top": round(top, 3), "notched": notched, "y": (round(y0, 3), round(y1, 3)), "key": key}
    return vs


def deck(a, seed=480):
    vs = []
    for i in range(NBOARDS):
        vs += board(a, i, seed + 7 * i)
    return vs


def side_beam(a, sx, seed):
    """A side beam: outer face on the posts' inner faces (sunk 0.02), ends 0.5 past the corner posts."""
    xi = W / 2 - PH + SINK            # 3.37 (into the posts)
    xo = xi - SINK - BEAM_W           # 2.45
    x0, x1 = sorted((sx * xo, sx * xi))
    vs, _ = _box(a, x0, -BEAM_Y, BEAM_BOT, x1, BEAM_Y, BEAM_TOP, WOOD_DEEP, tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    _texture(a, vs, 0.03, seed)
    return vs


def crossbeam(a, y, seed):
    """A crossbeam between the side beams (end faces sunk 0.02 into them)."""
    xi = W / 2 - PH - BEAM_W + SINK   # 2.47
    vs, _ = _box(a, -xi, y - BEAM_W / 2, BEAM_BOT, xi, y + BEAM_W / 2, BEAM_TOP, WOOD_DEEP,
                 tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    _texture(a, vs, 0.03, seed)
    return vs


def _brace_key():
    return _mix(WOOD_DEEP, WOOD_DARK, 0.6)


KNEE_LO_Z, KNEE_HI_U, KNEE_HALF, KNEE_T = 1.1, 4.6, 0.3, 0.45


def knee_long(a, sx, sy, seed):
    """Knee brace on a long side: from the corner leg's inner face (y = sy * 7.35) at z 1.1 up to the side beam's
    underside at y = sy * 4.6; 0.45 thick, centred in x on the leg / beam line (x = sx * 3.35)."""
    face = sy * (BAY - PH)                       # leg inner face
    u_cut = face + sy * SINK                     # sunk into the leg
    q = _brace_quad((face, KNEE_LO_Z), (sy * KNEE_HI_U, BEAM_BOT), KNEE_HALF, u_cut, BEAM_BOT + SINK)
    xc = sx * (W / 2 - PH)
    vs, _ = _plank2d(a, q, xc - KNEE_T / 2, xc + KNEE_T / 2, "x", _brace_key(),
                     tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    _texture(a, vs, 0.03, seed)
    return vs


def knee_end(a, sx, seed):
    """Knee brace on the +Y end: from the corner leg's inner face (x = sx * 3.35) at z 1.1 up to C+Y's underside at
    x = sx * 0.9; y 7.6 .. 8.05."""
    face = sx * (W / 2 - PH)
    q = _brace_quad((face, KNEE_LO_Z), (sx * 0.9, BEAM_BOT), KNEE_HALF, face + sx * SINK, BEAM_BOT + SINK)
    vs, _ = _plank2d(a, q, BAY - 0.4, BAY + 0.05, "y", _brace_key(), tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    _texture(a, vs, 0.03, seed)
    return vs


XB_LO, XB_HI, XB_H = 0.45, 3.40, 0.6


def _xboard_quad(s):
    """X-brace board in (x, z): low end on the leg at x = -s * 3.37, high end on the other leg, top at 3.40."""
    xc = W / 2 - PH + SINK
    span = 2 * xc
    th = 0.0
    for _ in range(30):                          # solve span * tan(th) + h / cos(th) = hi - lo
        th = math.atan((XB_HI - XB_LO - XB_H / math.cos(th)) / span)
    hh = XB_H / math.cos(th)
    lo_x, hi_x = -s * xc, s * xc
    return [(lo_x, XB_LO), (hi_x, XB_HI - hh), (hi_x, XB_HI), (lo_x, XB_LO + hh)]


def xbrace(a, seed):
    """X brace on the -Y end: two stacked boards between the corner legs (inside the legs' y range), touching at the
    crossing (sunk 0.02), and a brass bolt at the crossing on the outer board."""
    yb = -BAY
    vs = []
    va, _ = _plank2d(a, _xboard_quad(1), yb + 0.25, yb - 0.11, "y", _brace_key(), tint=1.0 + _rng(seed).uniform(-0.03, 0.03))
    vb, _ = _plank2d(a, _xboard_quad(-1), yb - 0.09, yb - 0.45, "y", _brace_key(),
                     tint=1.0 + _rng(seed + 1).uniform(-0.03, 0.03))
    _texture(a, va, 0.03, seed)
    _texture(a, vb, 0.03, seed + 1)
    zc = (XB_LO + XB_HI) / 2
    bv, _ = _bolt(a, (0.0, yb - 0.45, zc), (0, -1, 0))
    GEO["xbrace_cross_z"] = round(zc, 3)
    return va + vb + bv


def _catenary(s, e, low, n, a_=1.3):
    s, e = Vector(s), Vector(e)
    sag = s.z - low
    pts = []
    for i in range(n + 1):
        t = i / n
        f = (math.cosh(a_) - math.cosh(a_ * (2 * t - 1))) / (math.cosh(a_) - 1)
        p = s.lerp(e, t)
        p.z = s.z + (e.z - s.z) * t - sag * f
        pts.append(p)
    return pts


def swag_ends(p0, p1):
    """Swag end points: on the facing coil flats (the coil centreline), between the two coils (z 6.72)."""
    (x0, y0), (x1, y1) = p0, p1
    d = Vector((x1 - x0, y1 - y0, 0)).normalized()
    s = Vector((x0, y0, SWAG_Z)) + d * COIL_D
    e = Vector((x1, y1, SWAG_Z)) - d * COIL_D
    return s, e


SWAGS = [((W / 2, -BAY), (W / 2, 0.0), "side"), ((W / 2, 0.0), (W / 2, BAY), "side"),
         ((-W / 2, -BAY), (-W / 2, 0.0), "side"), ((-W / 2, 0.0), (-W / 2, BAY), "side"),
         ((W / 2, BAY), (-W / 2, BAY), "end")]


def swag(a, p0, p1, kind, seed, knobs=False):
    s, e = swag_ends(p0, p1)
    path = _catenary(s, e, SWAG_LOW[kind], SWAG_SEGS)
    vs, _ = _tube(a, path, ROPE_R, ROPE_SIDES, False, ROPE, groove=_strands(ROPE_SIDES), twist=True,
                  tint=1.0 + _rng(seed).uniform(-0.02, 0.02), phase=_rng(seed).uniform(0, 1.0))
    GEO.setdefault("swag_low", []).append(round(min(p.z for p in path), 3))
    if knobs:
        for p in (path[0], path[-1]):
            kv, _ = _knob(a, p, 0.3, ROPE, tint=0.98)
            vs += kv
    return vs, path


KNOT_X = (2.78, 2.46)


def knot(a, seed):
    """Two fat loops wrapped round the +Y swag beside the +X corner post's coils (each sunk 0.05 into the swag; the
    first touches the coil, the second the first)."""
    s, e = swag_ends(SWAGS[4][0], SWAGS[4][1])
    path = _catenary(s, e, SWAG_LOW["end"], 200)
    vs = []
    for j, xk in enumerate(KNOT_X):
        i = min(range(len(path)), key=lambda k: abs(path[k].x - xk))
        c = path[i]
        t = (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()
        u = Vector((0, 0, 1)) - Vector((0, 0, 1)).dot(t) * t
        u.normalize()
        v = t.cross(u)
        R, r = ROPE_MEAN + 0.15 - 0.05, 0.15
        ring = [c + (u * math.cos(2 * math.pi * k / 6) + v * math.sin(2 * math.pi * k / 6)) * R for k in range(6)]
        kv, _ = _tube(a, ring, r, 5, True, ROPE, groove=_strands(5),
                      tint=1.0 + _rng(seed + j).uniform(-0.02, 0.02), up=tuple(t), phase=0.3 * j)
        vs += kv
    return vs


# ---- parts and hero ---------------------------------------------------------------------------------------------------
def post_part(a):
    post(a, W / 2, -BAY, 101)


def deck_part(a):
    deck(a)


def beam_part(a):
    side_beam(a, 1, 301)


def cross_part(a):
    crossbeam(a, 0.0, 311)


def brace_part(a):
    knee_long(a, 1, -1, 401)


def rope_part(a):
    swag(a, SWAGS[0][0], SWAGS[0][1], "side", 501, knobs=True)


def hero_fn(a):
    GEO.clear()
    for i, (px, py) in enumerate(POSTS):
        post(a, px, py, 101 + 17 * i)
    deck(a)
    for sx in (1, -1):
        side_beam(a, sx, 301 + sx)
    for j, y in enumerate((-BAY, 0.0, BAY)):
        crossbeam(a, y, 311 + j)
    for sx in (1, -1):
        for sy in (1, -1):
            knee_long(a, sx, sy, 401 + 3 * sx + sy)
        knee_end(a, sx, 421 + sx)
    xbrace(a, 431)
    for j, (p0, p1, kind) in enumerate(SWAGS):
        swag(a, p0, p1, kind, 501 + j)
    knot(a, 551)


NOTES = {
    HERO: "Timber dock (post centres 8 x 16, deck top 5.6, posts to 8.3; about 10.6 x 19.2 x 8.3): a raised pier on "
          "six tall square legs, ten chunky orange boards across the width (notched round the posts), side beams and "
          "crossbeams under the deck, bolt blocks with brass bolt heads, knee braces on the long sides and the +Y end, "
          "an X brace on the open -Y end, two fat rope coils on every post and five low twisted rope swags (none "
          "across the open -Y end). Seams: feet z 0, deck top 5.6 (M043 lower lawn), open end y -9.6. No VFX",
    POST_P: "Mooring Post (reusable): a 1.3-square post, ground to an 8.3 chamfered cap, with two bolt blocks and brass "
            "bolts and two twisted rope coils; legs darker below the beams",
    DECK_P: "Deck (reusable): ten chunky 1.83 x 0.85 boards across the width with chamfered tops, notched round the "
            "posts, a seam at the middle posts",
    BEAM_P: "Beam (reusable): a 0.9 x 1.3 side beam, 18.3 long",
    CROSS_P: "Crossbeam (reusable): a 0.9 x 1.3 crossbeam between the side beams",
    BRACE_P: "Brace (reusable): a knee brace, ends cut to the leg face and the beam underside",
    ROPE_P: "Rope Segment (reusable): one sagging twisted rope swag with round knob ends",
}
COLLISION = {HERO: "precise", POST_P: "hull", DECK_P: "box", BEAM_P: "hull", CROSS_P: "hull", BRACE_P: "hull",
             ROPE_P: "none"}


def _tri_ngons(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    ng = [f for f in bm.faces if len(f.verts) > 4]
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
    if all(k.startswith("m048_rope") for k in ks):
        return "rope"
    if all(k.startswith("m048_brass") for k in ks):
        return "bolt"
    if all(k.startswith("m048_wood") for k in ks):
        return "wood"
    return "mixed"


def shells_report(o):
    old, old_keys = m040._kind, m040._keys
    m040._kind, m040._keys = _kind, _keys
    try:
        return m040.shells_report(o)
    finally:
        m040._kind, m040._keys = old, old_keys


def contact_report(o, tol=0.03):
    old_keys = m040._keys
    m040._keys = _keys
    try:
        r = m040.contact_report(o, tol=tol)
    finally:
        m040._keys = old_keys
    r["floating_kinds"] = [k.replace("m048_", "") for k in r["floating_kinds"]]
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


def levels_report(h):
    """Spec 4.2.3 on the hero mesh (build frame = mesh + offset): feet, beam band, every board top, coil centres,
    swag lows, post tops; and the open end clear of rope / brace above the deck."""
    off = Vector(h[OFF])
    keys = _keys(h)
    bm = bmesh.new()
    bm.from_mesh(h.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    groups = {}
    for f in bm.faces:
        groups.setdefault(ids[f.index], []).append(f)
    tops, posts, ropes = [], [], []
    open_end = 0
    for k, fs in groups.items():
        vs = {v for f in fs for v in f.verts}
        zs = [v.co.z + off.z for v in vs]
        ys = [v.co.y + off.y for v in vs]
        xs = [v.co.x + off.x for v in vs]
        kind = _kind({keys[f.material_index] for f in fs})
        if kind == "wood" and max(xs) - min(xs) > 10 and max(zs) - min(zs) < 1.0:
            tops.append(round(max(zs), 3))
        if kind == "wood" and min(zs) < 0.01 and max(zs) > 8.0:
            posts.append((round(min(zs), 3), round(max(zs), 3)))
        if kind == "rope" and max(ys) < -BAY + PH and max(xs) - min(xs) > 4.0:
            open_end += 1           # a rope running across the open -Y end
    bm.free()
    return {"board_tops": sorted(tops), "board_top_range": [min(tops), max(tops)] if tops else None,
            "posts_z": sorted(set(posts)), "swag_low": GEO.get("swag_low"), "coil_z": list(COIL_Z),
            "beam_band": [BEAM_BOT, BEAM_TOP], "open_end_rope_or_bolt_above_deck": open_end,
            "xbrace_cross_z": GEO.get("xbrace_cross_z")}


# ---- render measurement (the study's W / K / Y masks, spec "Pixel boxes and masks") ------------------------------------
SHEET_REF = {
    "f34": {"wh": 1.575, "W": 35.9, "K": 58.2, "Y": 5.9, "Yfifths": [0, 5.4, 25.8, 50.9, 17.9],
            "top": [.46, .73, .74, .66, .67, .69, .72, .76, .90, .89, .82, .84, .92, .99, .86, .82, .80, .79, .87, .87,
                    .66]},
    "r34": {"wh": 1.543, "W": 30.7, "K": 63.2, "Y": 6.1,
            "top": [.67, .89, .89, .77, .77, .78, .82, .92, .99, .85, .81, .81, .90, .81, .72, .69, .67, .65, .74, .73,
                    .48]},
    "front": {"wh": 1.871, "W": 24.1, "K": 69.9, "Y": 5.9,
              "top": [.64, .89, .99, .98, .81, .77, .76, .77, .79, .86, .99, .99, .80, .77, .76, .77, .80, .89, .99,
                      .99, .64]},
    "side": {"wh": 1.560, "W": 22.2, "K": 72.2, "Y": 5.6,
             "top": [.62, .88, .99, .99, .91, .82, .79, .77, .76, .75, .74, .74, .75, .77, .79, .81, .87, .99, .99, .87,
                     .64]},
    "rear": {"wh": 1.526, "W": 16.3, "K": 79.6, "Y": 4.1},
    "top": {"wh": 0.575, "W": 72.8, "K": 26.8, "Y": 0.4},
}


def _hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0)
    return h, s, mx


def classify(px):
    """W lit wood, K dark wood, Y rope / brass, B pale shadow, T dark outline (0-1 sRGB rows top-down)."""
    h, s, v = _hsv(px)
    T = (v < 0.16) | ((s < 0.25) & (v < 0.35))
    B = ~T & (s < 0.12) & (v >= 0.70)
    Y = ~T & ~B & (((h >= 36) & (h <= 62) & (s >= 0.18) & (v >= 0.60)) | ((h >= 33) & (h < 36) & (s < 0.62) & (v >= 0.75)))
    Wm = ~T & ~B & ~Y & ((h < 40) | (h > 345)) & (s >= 0.35) & (v >= 0.62)
    Km = ~T & ~B & ~Y & ~Wm & ((h < 40) | (h > 340)) & (s >= 0.25) & (v >= 0.16)
    return Wm, Km, Y


def measure(path, tol=18 / 255):
    kit = K.NS["KIT"]
    raw = kit["load_px"](path)[::-1]
    px = np.clip(raw[..., :3], 0, 1)
    bg = np.median(np.concatenate([px[:4, :4].reshape(-1, 3), px[:4, -4:].reshape(-1, 3)]), axis=0)
    sil = (np.abs(px - bg).max(-1) > tol) & (raw[..., 3] > 0.5)
    Wm, Km, Y = classify(px)
    Wm, Km, Y = Wm & sil, Km & sil, Y & sil
    ys, xs = np.nonzero(sil)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    H, Wd = y1 - y0 + 1, x1 - x0 + 1
    tot = max(1, int(Wm.sum() + Km.sum() + Y.sum()))
    res = {"wh": round(Wd / H, 3), "W": round(100 * Wm.sum() / tot, 1), "K": round(100 * Km.sum() / tot, 1),
           "Y": round(100 * Y.sum() / tot, 1)}
    fr = [0] * 5
    for yy in np.nonzero(Y)[0]:
        fr[min(4, int((y1 - yy) / H * 5))] += 1
    res["Yfifths"] = [round(100 * f / max(1, sum(fr)), 1) for f in fr]
    prof = []
    for f in np.linspace(0, 1, 21):
        col = int(round(x0 + f * (Wd - 1)))
        on = np.nonzero(sil[:, col])[0]
        prof.append(round(float((y1 - on.min()) / (H - 1)), 2) if len(on) else 0.0)
    res["top"] = prof
    rgb = px * 255
    for k, m in (("W", Wm), ("K", Km), ("Y", Y)):
        sel = rgb[m]
        res[k + "_med"] = "#" + "".join(f"{int(x):02X}" for x in np.median(sel, axis=0)) if len(sel) else None
    return res


def measure_views(out_dir=None):
    d = out_dir or f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    res = {}
    for k, f in (("f34", "f34_sheet"), ("r34", "r34_sheet"), ("front", "front_sheet"), ("side", "side_sheet"),
                 ("rear", "rear_sheet"), ("top", "top_sheet")):
        try:
            m = measure(f"{d}/{f}.png")
        except Exception as e:      # noqa: BLE001 - report, don't fail the build
            res[k] = str(e)
            continue
        ref = SHEET_REF[k]
        if "top" in ref:
            err = np.abs(np.array(m["top"]) - np.array(ref["top"]))
            m["top_err_mean"], m["top_err_max"] = round(float(err.mean()), 3), round(float(err.max()), 3)
        m.pop("top", None)
        m["sheet"] = {kk: vv for kk, vv in ref.items() if kk != "top"}
        res[k] = m
    return res


# ---- build ------------------------------------------------------------------------------------------------------------
TARGET_SIZE = ((10.56, 0.4), (19.2, 0.4), (8.3, 0.3))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me is not None and isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m048_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", "TimberDock"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


PART_FNS = ((POST_P, post_part), (DECK_P, deck_part), (BEAM_P, beam_part), (CROSS_P, cross_part),
            (BRACE_P, brace_part), (ROPE_P, rope_part))


def build_objects(parts=True):
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in PART_FNS:
            objs[name], log[name] = _make_plain(name, fn)
    h, log["hero"] = _make_plain(HERO, hero_fn, role="hero", budget=4000)
    log["deck"] = {str(k): v for k, v in DECK_INFO.items()}
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
            if s["kind"] == "mixed":
                problems.append(f"{o.name} shell {i}: mixed materials")
    contact = {o.name: contact_report(o) for o in order if len(shells[o.name]) > 1}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} shells touch nothing within 0.03, {c['unchained']} have no chain "
                            f"of contact to the ground")
    levels = levels_report(h)
    tr = levels["board_top_range"]
    if not tr or tr[0] < DECK_TOP - 0.021 or tr[1] > DECK_TOP + 0.021 or len(levels["board_tops"]) != NBOARDS:
        problems.append(f"{HERO}: board tops {levels['board_tops']}")
    if levels["open_end_rope_or_bolt_above_deck"]:
        problems.append(f"{HERO}: rope or bolt above the deck past the open end")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WLH"):
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
    for s in shells[HERO]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    return {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                          "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                          "ngons", "dup_verts", "transforms_applied")} for au in audits],
            "shells": kinds, "winding": winding, "contact": contact, "levels": levels, "thin": thin,
            "problems": problems, "uv": uv,
            "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
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
# decision 10 / 11: f34_sheet (47, 16.5) governs; r34_sheet (-41, 17); front_sheet (90, 3) the +X side; side_sheet
# (180, 3) the +Y end; rear_sheet (-90, 6) the -X side; top_sheet (0, 89). Floor hidden on every *_sheet shot.
SHEET_VIEWS = {"f34_sheet": (47, 16.5), "r34_sheet": (-41, 17), "front_sheet": (90, 3), "side_sheet": (180, 3),
               "rear_sheet": (-90, 6), "top_sheet": (0, 89)}
# lens factor per shot: the sheet's cells are near-orthographic. The f34 probe (lens 1 / 1.8 / 3 x az 47 / 54 x e 16.5 /
# 21) fits best at 3x, (47, 16.5): W:H 1.558 (sheet 1.575), top profile error mean 0.033. The level orthos use 8x
# so the far post row hides behind the near one, as drawn
LENS = {"f34_sheet": 3.0, "r34_sheet": 3.0}
SHEET_LENS = 8.0
PARTS_SHOT = (-35, 25)


def _lens(kit):
    orig = kit["render_group"]

    def rg(group, path, azimuth=-22, elevation=20):
        cam = bpy.data.objects["FB_Cam"].data
        lens = cam.lens
        ground = bpy.data.objects.get("FB_Ground")
        gh = ground.hide_render if ground else None
        name = path.rsplit("/", 1)[-1][:-4]
        if name.endswith("_sheet"):
            cam.lens = lens * LENS.get(name, SHEET_LENS)
            if ground:
                ground.hide_render = True
        try:
            return orig(group, path, azimuth, elevation)
        finally:
            cam.lens = lens
            if ground:
                ground.hide_render = gh
    return orig, rg


def _copy(tag, src, m, coll):
    c = bpy.data.objects.new(f"{PFX}{tag}", src.data)
    coll.objects.link(c)
    c.matrix_world = m
    return c


def _frame_of(h):
    return h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded View: the deck lifted above the frame, the corner posts
    pulled outward (each turned so its blocks face out), the side beams pulled apart below, crossbeams and braces in
    front, the rope above."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    o0 = Matrix.Translation((objs[0].location.x + 60, objs[0].location.y, 0))
    shown = []

    def put(tag, name, d, rot=0.0, pivot=None):
        if name not in by:
            return
        o = by[name]
        m = Matrix.Translation(Vector(o[OFF]))
        if rot:
            p = Vector(pivot)
            m = Matrix.Translation(p) @ Matrix.Rotation(rot, 4, "Z") @ Matrix.Translation(-p) @ m
        shown.append(_copy(f"expl_{tag}", o, o0 @ Matrix.Translation(Vector(d)) @ m, coll))
    pc = (W / 2, -BAY, 0)
    put("post_a", POST_P, (3.5, -3.5, 0))
    put("post_b", POST_P, (-W - 3.5, -3.5, 0), -math.pi / 2, pc)
    put("post_c", POST_P, (3.5, 2 * BAY + 3.5, 0), math.pi / 2, pc)
    put("post_d", POST_P, (-W - 3.5, 2 * BAY + 3.5, 0), math.pi, pc)
    put("deck", DECK_P, (0, 0, 5.0))
    beam_cx = W / 2 - PH - BEAM_W / 2 + SINK / 2
    put("beam_r", BEAM_P, (2.0, 0, -0.3))
    put("beam_l", BEAM_P, (-2 * beam_cx - 2.0, 0, -0.3))
    for j, y in enumerate((-BAY, 0.0, BAY)):
        put(f"cross{j}", CROSS_P, (0, y, -2.2))
    put("brace", BRACE_P, (3.5, -5.0, -0.7))
    put("rope", ROPE_P, (3.0, 4.0, 5.2))
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
    """5.5-stud character stand-ins: on the deck at y 0, and on the ground beside a +X leg."""
    return [_marker(h, (0.0, 0.0, DECK_TOP), "char_deck"), _marker(h, (6.6, -4.0, 0.0), "char_ground")]


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
    markers = _scale_markers(h)
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        for o in objs[1:]:
            extra["part_" + o.name.replace("TimberDock", "").lower()] = ([o], *PARTS_SHOT)
        if shown:
            extra["exploded"] = (shown, -35, 25)
        extra["scale"] = ([h] + markers, 40, 12)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _lens(kit)
        try:
            sheet = M.views(NUM, [h], extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet}
        if close:
            d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
            fr = _frame_of(h)
            out["junc_cu"] = _close([h], f"{d}/junc_cu.png", 60, 20, fr @ Vector((4.3, -8.0, 5.9)), 2.3)
            out["rope_cu"] = _close([h], f"{d}/rope_cu.png", 70, 14, fr @ Vector((4.4, -0.2, 6.6)), 1.5)
            out["bolt_cu"] = _close([h], f"{d}/bolt_cu.png", 70, 6, fr @ Vector((5.0, -8.0, 4.05)), 0.9)
            out["under_cu"] = _close([h], f"{d}/under_cu.png", 35, -30, fr @ Vector((3.0, -5.5, 3.2)), 3.2)
            out["knot_cu"] = _close([h], f"{d}/knot_cu.png", 165, 10, fr @ Vector((3.1, 8.0, 6.6)), 1.3)
            out["xbrace_cu"] = _close([h], f"{d}/xbrace_cu.png", -15, 6, fr @ Vector((0.0, -8.4, 2.4)), 3.8)
        return out
    finally:
        for o in shown + markers:
            me = o.data
            mine = o in markers
            bpy.data.objects.remove(o, do_unlink=True)
            if mine and me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


# spec 5.4 calibration warnings, sampled on our renders at known build-frame points (5 x 5 px medians). The twisted
# rope and the small bolts are judged by the Y-class median of measure() instead (a spot lands on one strand)
REGIONS = {
    "f34_sheet": {"board_top": [(x, -DECK_Y + 0.96 + i * (BOARD_W + GAP), 5.6) for x in (-2.5, 0.0, 2.5)
                                for i in range(1, 9)], "cap_top": [(4.0, 0.0, 8.3)],
                  "leg": [(4.4, -8.66, 1.5), (4.66, 0.3, 1.5)], "post_face": [(4.66, 0.3, 5.95)]},
    "front_sheet": {"board_end": [(5.1, -4.8, 5.15), (5.1, 3.0, 5.15)], "post_face": [(4.66, 0.0, 5.95)],
                    "leg": [(4.66, 0.0, 1.5), (4.66, -8.0, 1.5)], "beam": [(3.37, -4.2, 4.1)]},
}
SHEET_REGION = {"f34_sheet": {"board_top": "#DF8C3E", "cap_top": "#D07C4A", "leg": "#62371C", "swag": "#F8D07C",
                              "bolt": "#FAD584"},
                "front_sheet": {"board_end": "#A95015", "post_face": "#8D4212", "leg": "#764521", "beam": "#89451B",
                                "swag": "#F8D088", "bolt": "#F7E0A8"}}


def region_report():
    """Render f34_sheet and front_sheet again and sample each region (spec 5.4 warnings) against the sheet."""
    from bpy_extras.object_utils import world_to_camera_view
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    sc = bpy.context.scene
    fr = _frame_of(h)
    out = {}
    orig, kit["render_group"] = _lens(kit)
    try:
        for view, regs in REGIONS.items():
            az, el = SHEET_VIEWS[view]
            path = kit["render_group"]([h], f"{d}/{view}.png", az, el)
            px = kit["load_px"](path)
            H_, W_ = px.shape[:2]
            cam = bpy.data.objects["FB_Cam"]
            lens0 = cam.data.lens                   # _lens restores the lens after the shot: project with the shot's
            cam.data.lens = lens0 * LENS.get(view, SHEET_LENS)
            bpy.context.view_layer.update()
            qs = {name: [world_to_camera_view(sc, cam, fr @ Vector(p)) for p in pts] for name, pts in regs.items()}
            cam.data.lens = lens0
            res = {}
            for name, pts in regs.items():
                cols = []
                for q in qs[name]:
                    cx, cy = int(q.x * W_), int(q.y * H_)
                    box = px[max(0, cy - 2):cy + 3, max(0, cx - 2):cx + 3, :3].reshape(-1, 3)
                    cols.append(np.median(box, axis=0))
                c = np.clip(np.median(np.array(cols), axis=0), 0, 1) * 255
                hexc = "#" + "".join(f"{int(round(x)):02X}" for x in c)
                ref = SHEET_REGION[view].get(name)
                row = {"ours": hexc}
                if ref:
                    rc = np.array([int(ref[i:i + 2], 16) for i in (1, 3, 5)])
                    row["sheet"] = ref
                    row["max_diff"] = int(np.abs(rc - c).max())
                hh, ss, vv = _hsv(c[None] / 255.0)
                row["hsv"] = [round(float(hh[0])), round(float(ss[0]), 2), round(float(vv[0]), 2)]
                res[name] = row
            out[view] = res
    finally:
        kit["render_group"] = orig
    return out


def preview(names=("f34_sheet", "front_sheet", "side_sheet", "top_sheet"), vfx=False, measure_too=True):
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = _lens(kit)
    try:
        sheet = M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig
    return {"sheet": sheet, "measure": measure_views() if measure_too else None}
