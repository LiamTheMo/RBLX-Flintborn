"""018 Healing Herb (references/018.png): a low rosette of seven chunky faceted leaves round a squat brown root plug,
two upright inner leaves, two straight six-sided green stems carrying cream faceted closed buds (a tall one on the
axis, a shorter one leaning to the front-right).

    import importlib, kit_models, m018; importlib.reload(kit_models); importlib.reload(m018); m018.build()

Parts as on the sheet's Parts column, each built by its own function (front -Y, ground z = 0):
- HerbShrubBud: one faceted ovoid bud (5-ring, 30 tris): bottom point, ring A, ring B turned 36 degrees, ring C, apex.
- HerbShrubStem: a straight 6-sided prism with flat caps (decision 4).
- HerbShrubLeaf: one chunky pointed leaf along a cubic midline: a 12-point ovate outline whose edges droop below the
  midrib (the sheet's tent-shaped leaves), three ridge points on top (the pyramid apex and a ridge on to the tip) and
  three keel points below; closed, 32 tris.
- HerbShrubRootPlug: an ico-2 ball, W : H 1.11, its top pressed flat.
The hero (HerbShrubNode) is built from the same builders (M018_spec.md 2): plug + crown disc (decision 5), 2 stems,
2 buds (decision 2), 7 outer + 2 inner leaves (decision 3); one guarded exact union, floor-cut at the ground.
Sizes are kit studs (decision 1: 2.85 x 2.65 x 2.2). Colour (stage 4) is painted by position fields inside the
builders, before the union (the union and cleanup keep each face's key and Tint).
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise

import kit_mcp as K
import kit_models as M
import m004
import m011
import m012

NUM, TITLE, SHEET = 18, "Healing Herb", "M018"

LEAF, LEAF_TIP, LEAF_BASE = "m018_leaf", "m018_leaf_tip", "m018_leaf_base"
STEM = "m018_stem"
BUD, BUD_TIP, BUD_BASE = "m018_bud", "m018_bud_tip", "m018_bud_base"
PLUG, CROWN, SHADE = "m018_plug", "m018_plug_crown", "m018_plug_shade"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0
COLOUR = [True]          # stage 1 renders could switch the paint off (placeholder keys only)

# ---- palette --------------------------------------------------------------------------------------------------------
# (hex, roughness, specular IOR level or None for flintkit's default, low_spec)
PALETTE = {             # round 2: re-calibrated on the hero renders (M018_spec.md, "Round 2 fixes")
    LEAF: ("#5A8044", 0.85, None, True),
    LEAF_TIP: ("#7A9C48", 0.85, None, True),
    LEAF_BASE: ("#3A5A2E", 0.85, None, True),
    STEM: ("#57793B", 0.8, None, True),
    # the bud ladder runs by height in the bud, top palest -> base warmest (round 1 had it inverted, base brightest);
    # clipping is held off by the finish (specular 0.1, roughness 0.85), not by greying the paint. Round 3: all three
    # 6 % lower in value at the same hue and saturation (#EED3A0 / #E6D3B4 / #EED29A): the lit side clipped to lemon
    BUD: ("#E0C696", 0.85, 0.1, False),
    BUD_TIP: ("#D8C6A9", 0.85, 0.1, False),
    BUD_BASE: ("#E0C591", 0.85, 0.1, False),
    PLUG: ("#806A58", 0.95, None, False),
    CROWN: ("#715B47", 0.95, None, False),
    SHADE: ("#3A2D1F", 0.95, None, False),      # the plug soil in the hero, deep under the leaves (sheet #352A1C)
}


def palette():
    for k, (hx, rough, spec, low) in PALETTE.items():
        K.set_colour(k, hx, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hx, rough=rough, low_spec=low)
    _restyle()


def _restyle():
    """Bud keys (mix keys too) at their satin specular; leaf / stem mix keys at the foliage specular."""
    for m in bpy.data.materials:
        if not m.name.startswith("FB_m018_") or not m.node_tree:
            continue
        b = m.node_tree.nodes.get("Principled BSDF")
        if not b or "Specular IOR Level" not in b.inputs:
            continue
        key = m.name[3:]
        if key.startswith(BUD):
            b.inputs["Specular IOR Level"].default_value = PALETTE[BUD][2]
            b.inputs["Roughness"].default_value = PALETTE[BUD][1]
        elif key.startswith(("m018_leaf", STEM)):
            b.inputs["Specular IOR Level"].default_value = K.FOLIAGE_SPEC


# ---- small geometry helpers -------------------------------------------------------------------------------------------
def _frame_from(d):
    d = Vector(d).normalized()
    u = d.orthogonal().normalized()
    v = d.cross(u).normalized()
    return u, v, d


def _cap(bm, ring, flip=False):
    vs = list(reversed(ring)) if flip else list(ring)
    f = bm.faces.new(vs)
    return bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="BEAUTY")["faces"]


def _ico(bm, subdiv=2):
    """A unit ico sphere added to bm (built in a scratch bmesh and copied in). Pole at +Z."""
    tmp = bmesh.new()
    bmesh.ops.create_icosphere(tmp, subdivisions=subdiv, radius=1.0)
    vmap = {v: bm.verts.new(v.co) for v in tmp.verts}
    for f in tmp.faces:
        bm.faces.new([vmap[v] for v in f.verts])
    tmp.free()
    return list(vmap.values())


def _faces(verts):
    return K.faces_of(verts)


# ---- bud ------------------------------------------------------------------------------------------------------------
BUD_RINGS = ((0.30, 0.80, 0.0), (0.56, 1.00, 36.0), (0.80, 0.80, 0.0))   # (height frac, radius frac, turn degrees)


def bud_mesh(a, base, axis, width, height, seed):
    """One closed bud: bottom point at base, apex at base + axis * height (study 1.4). Returns (verts, {vert: height
    fraction})."""
    rng = random.Random(seed)
    bm = a.bm
    u, v, d = _frame_from(axis)
    R = width / 2
    ph = rng.uniform(0, 2 * math.pi)
    B = Vector(base)
    bot = bm.verts.new(B)
    top = bm.verts.new(B + d * height)
    hf = {bot: 0.0, top: 1.0}
    rings = []
    for zf, rf, turn in BUD_RINGS:
        tw = ph + math.radians(turn + rng.uniform(-6, 6))
        rr = R * rf * (1 + rng.uniform(-0.04, 0.04))
        ring = []
        for k in range(5):
            t = tw + 2 * math.pi * k / 5
            p = B + d * (zf * height) + (u * math.cos(t) + v * math.sin(t)) * rr * (1 + rng.uniform(-0.03, 0.03))
            x = bm.verts.new(p)
            hf[x] = zf
            ring.append(x)
        rings.append(ring)
    A, Bq, C = rings
    fs = []
    for i in range(5):
        j = (i + 1) % 5
        fs.append(bm.faces.new((bot, A[j], A[i])))
        fs.append(bm.faces.new((A[i], A[j], Bq[i])))
        fs.append(bm.faces.new((A[j], Bq[j], Bq[i])))
        fs.append(bm.faces.new((Bq[i], C[j], C[i])))
        fs.append(bm.faces.new((Bq[i], Bq[j], C[j])))
        fs.append(bm.faces.new((top, C[i], C[j])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    vs = [bot, top] + A + Bq + C
    a._finish(vs, BUD, tint=1.0)
    return vs, hf


# ---- stem -----------------------------------------------------------------------------------------------------------
def stem_mesh(a, p0, p1, radius, seed, sides=6):
    """A straight 6-sided prism from p0 to p1: 3 rings (radius 1.0 -> 0.88 taper; the middle ring +-5 % and +-8
    degrees), flat caps. Returns verts."""
    rng = random.Random(seed)
    bm = a.bm
    p0, p1 = Vector(p0), Vector(p1)
    u, v, d = _frame_from(p1 - p0)
    ph = rng.uniform(0, 2 * math.pi)
    rings = []
    for i, f in enumerate((0.0, 0.5, 1.0)):
        r = radius * (1.0 - 0.12 * f) * (1 + (rng.uniform(-0.05, 0.05) if i == 1 else 0.0))
        tw = ph + (math.radians(rng.uniform(-8, 8)) if i == 1 else 0.0)
        c = p0.lerp(p1, f)
        rings.append([bm.verts.new(c + (u * math.cos(tw + 2 * math.pi * k / sides) +
                                        v * math.sin(tw + 2 * math.pi * k / sides)) * r) for k in range(sides)])
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            faces.append(bm.faces.new((r0[k], r0[j], r1[j], r1[k])))
    faces += _cap(bm, rings[0], flip=True) + _cap(bm, rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    vs = [x for r in rings for x in r]
    a._finish(vs, STEM, tint=1.0)
    return vs


# ---- leaf -----------------------------------------------------------------------------------------------------------
OUTLINE = ((0.12, 0.30), (0.30, 0.45), (0.50, 0.50), (0.72, 0.46), (0.88, 0.32))   # (t, half width / W), base -> tip
# round 3: the outer half filled back out (round 2's 0.42 / 0.24 at t 0.72 / 0.88 made narrow horn tips; the sheet's
# leaves are broad lenses with full tips, the verifier's N1); round 1's 0.47 / 0.36 made spoon ends
RIDGE = ((0.30, 0.08), (0.50, 0.09), (0.72, 0.06))    # (t, camber / L): the pyramid apex, the ridge on to the tip
KEEL = ((0.30, 0.045), (0.50, 0.05), (0.72, 0.035))  # (t, depth / L): the underside follows the top's topology
                                                      # (round 2: 0.04-0.05 L, the study's 1.4 keel; was 0.02-0.03)
FOLD = 0.18        # the leaf edges droop this x their distance from the midrib (round 2: 0.42 made tents/umbrellas;
                   # the sheet's leaves are low pyramid-topped boards)
KEEL_GUARD = 0.7   # an edge never droops (along the leaf normal) past this x the keel line's depth at its t. An edge
                   # below the keel line turns that part of the leaf inside-out (the top and underside triangles at
                   # the base / tip fold over each other), and exact booleans then silently drop the leaf (found on
                   # M019, which reused this recipe)


class Path2(tuple):
    """Round 3: a two-segment midline (7 control points, two cubics sharing P[3]). The first segment is the short,
    narrow rise out of the crown (a stalk, hidden in the heart), the second the broad board out to the tip. Its leaf
    t is the arc-length fraction, so outline positions mean the same along the leaf whatever the handles; the joint
    sits at t = ts (the rise's share of the length)."""

    def setup(self, n=64):
        cum, segs = [0.0], []
        for k, Q in enumerate((self[:4], self[3:])):
            prev = _bez_raw(Q, 0.0)
            for i in range(1, n + 1):
                p = _bez_raw(Q, i / n)
                cum.append(cum[-1] + (p - prev).length)
                segs.append((k, i / n))
                prev = p
        self.cum, self.segs, self.L = cum, segs, cum[-1]
        self.ts = cum[n] / cum[-1]
        return self


def _seg(P, t):
    if len(P) == 7:
        s = min(max(t, 0.0), 1.0) * P.L
        cum = P.cum
        lo, hi = 0, len(cum) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if cum[mid] <= s:
                lo = mid
            else:
                hi = mid
        f = (s - cum[lo]) / max(cum[hi] - cum[lo], 1e-12)
        k, u1 = P.segs[hi - 1]
        u0 = 0.0 if lo == 0 or P.segs[lo - 1][0] != k else P.segs[lo - 1][1]
        u = u0 + (u1 - u0) * f
        return (P[:4] if k == 0 else P[3:]), u, 1.0
    return P, t, 1.0


def _bez_raw(P, t):
    p0, p1, p2, p3 = P
    s = 1 - t
    return p0 * s ** 3 + p1 * 3 * s * s * t + p2 * 3 * s * t * t + p3 * t ** 3


def _bez(P, t):
    (p0, p1, p2, p3), t, _ = _seg(P, t)
    s = 1 - t
    return p0 * s ** 3 + p1 * 3 * s * s * t + p2 * 3 * s * t * t + p3 * t ** 3


def _bez_d(P, t):
    (p0, p1, p2, p3), t, k = _seg(P, t)
    s = 1 - t
    return ((p1 - p0) * 3 * s * s + (p2 - p1) * 6 * s * t + (p3 - p2) * 3 * t * t) * k


HANDLES = (0.50, 0.42)          # base and tip handle lengths, fractions of the chord


def leaf_path(base, az, tip, pitch, slope, tip_turn=0.0, handles=HANDLES, peak=None):
    """The leaf's midline: a cubic Bezier from base, leaving at `pitch` (degrees above horizontal) toward azimuth az,
    arriving at the tip (r, z from the plant axis, toward az + tip_turn) at `slope` degrees (negative = drooping).
    A steep base and a gently drooping tip give the sheet's broad arch (rising out of the plug, then running out and
    down to the tip). With `peak`, both handles are scaled together so the midline's highest point is that z.
    Returns the 4 control points."""
    B = Vector(base)
    a1 = math.radians(az + tip_turn)
    T = Vector((math.cos(a1) * tip[0], math.sin(a1) * tip[0], tip[1]))
    chord = (T - B).length

    def dirn(a, p):
        a, p = math.radians(a), math.radians(p)
        return Vector((math.cos(a) * math.cos(p), math.sin(a) * math.cos(p), math.sin(p)))
    d0, d1 = dirn(az, pitch), dirn(az + tip_turn, slope)

    def ctrl(k):
        return (B, B + d0 * handles[0] * chord * k, T - d1 * handles[1] * chord * k, T)

    def top(k):
        P = ctrl(k)
        return max(_bez(P, i / 40).z for i in range(41))
    k = 1.0
    if peak is not None:
        # longer handles can loop the curve (a self-intersecting leaf breaks the union; build() reports leaf_self).
        # Round 2: 2.6, so a steep -50 deg tip still lets L1/L3 reach their z 1.36 humps
        lo, hi = 0.2, 2.6
        if top(hi) < peak:
            k = hi
        elif top(lo) > peak:
            k = lo
        else:
            for _ in range(40):
                k = (lo + hi) / 2
                if top(k) < peak:
                    lo = k
                else:
                    hi = k
    return ctrl(k)


def _dirn(a, p):
    a, p = math.radians(a), math.radians(p)
    return Vector((math.cos(a) * math.cos(p), math.sin(a) * math.cos(p), math.sin(p)))


def arch_path(base, az, joint, tip, slope, tip_turn=0.0, handles=(0.35, 0.40)):
    """Round 3: the outer leaves' midline in two cubics. A short straight stalk out of the crown up to the joint
    (r, z from the axis), then the visible blade: a broad board that leaves the joint along the stalk, turns over and
    runs out to the tip (r, z), arriving at `slope`. Round 2's single cubic rose steeply from the centre to a peak at
    t 0.43-0.63 and read as a narrow "^". handles: (board out, board in), fractions of the board's chord. (A turn at
    the joint itself, inside the narrow stalk, folded the ridge through the keel: 2 crossings per leaf.)"""
    B = Vector(base)
    aj, at = math.radians(az + tip_turn * 0.3), math.radians(az + tip_turn)
    J = Vector((math.cos(aj) * joint[0], math.sin(aj) * joint[0], joint[1]))
    T = Vector((math.cos(at) * tip[0], math.sin(at) * tip[0], tip[1]))
    dj = (J - B).normalized()
    d1 = _dirn(az + tip_turn, slope)
    c2 = (T - J).length
    return Path2((B, B.lerp(J, 1 / 3), B.lerp(J, 2 / 3), J,
                  J + dj * handles[0] * c2, T - d1 * handles[1] * c2, T)).setup()


# round 3: the outer leaves' outline, ridge and keel, laid out on the board (u 0 at the joint, 1 at the tip); the
# rise below the joint is a narrow stalk (half width STALK x W), so it hides in the heart instead of standing up as
# a wall (the first round-3 try, with the plain OUTLINE on the rise, made a green cup round the stems)
BOARD_OUTLINE = ((0.0, 0.26), (0.24, 0.45), (0.50, 0.50), (0.72, 0.40), (0.88, 0.18))
STALK = ((0.55, 0.11),)          # (t / ts, half width / W) on the rise
BOARD_RIDGE = ((0.22, 0.08), (0.45, 0.09), (0.72, 0.06))
BOARD_KEEL = ((0.22, 0.045), (0.45, 0.05), (0.72, 0.035))
STALK_RIDGE = ((0.55, 0.025), (1.0, 0.045))    # (t / ts, camber / L): the ridge and keel follow the bend at the joint
STALK_KEEL = ((0.55, 0.02), (1.0, 0.035))      # (a straight base -> board triangle cut through the bent leaf)


def arch_layout(P, board=BOARD_OUTLINE, stalk=STALK):
    """outline, ridge, keel (leaf-t positions) for an arch leaf on path P."""
    ts = P.ts
    on = lambda u: ts + u * (1 - ts)
    outline = tuple((f * ts, h) for f, h in stalk) + tuple((on(u), h) for u, h in board)
    ridge = tuple((f * ts, c) for f, c in STALK_RIDGE) + tuple((on(u), c) for u, c in BOARD_RIDGE)
    keel = tuple((f * ts, c) for f, c in STALK_KEEL) + tuple((on(u), c) for u, c in BOARD_KEEL)
    return outline, ridge, keel


def leaf_mesh(a, path, width, seed, roll=0.0, ridge=RIDGE, keel=KEEL, fold=FOLD, outline=OUTLINE):
    """One closed chunky leaf along path: a pointed ovate outline (5 points a side) whose edges droop below the midrib
    (FOLD), ridge points above the midline (the pyramid apex and a ridge on to the tip) and keel points below
    it (study 1.4); three of each so both follow a hard-arched leaf. 32 tris. Returns (verts, {vert: t along the leaf}, (keel verts))."""
    rng = random.Random(seed)
    bm = a.bm
    P = path
    L = sum((_bez(P, (i + 1) / 20) - _bez(P, i / 20)).length for i in range(20))
    W = width * (1 + rng.uniform(-0.05, 0.05))
    side0 = Vector((-(P[-1] - P[0]).y, (P[-1] - P[0]).x, 0.0)).normalized()   # left of the leaf, horizontal
    rl = math.radians(roll + rng.uniform(-5, 5))

    def frame(t):
        T = _bez_d(P, t).normalized()
        S = (side0 - T * side0.dot(T)).normalized()
        N = T.cross(S).normalized()
        if N.z < 0:
            N = -N
        S = N.cross(T).normalized()
        # roll about the midline
        S, N = S * math.cos(rl) + N * math.sin(rl), N * math.cos(rl) - S * math.sin(rl)
        return _bez(P, t), S, N

    tm = {}
    kline = [(0.0, 0.0)] + list(keel) + [(1.0, 0.0)]

    def vert(t, y, z, droop=0.0):
        c, S, N = frame(t)
        # the edges droop half along the leaf normal, half straight down: along the normal alone, a hard-arched leaf's
        # outer flanks swing in under its own inner half and the leaf cuts through itself
        D = (N + Vector((0, 0, 1))).normalized()
        if droop > 0:
            dn = max(D.dot(N), 1e-3)
            cap = KEEL_GUARD * _ladder(t, kline) * L       # stay above the keel line (KEEL_GUARD)
            droop = min(droop, cap / dn)
        x = bm.verts.new(c + S * y + N * z - D * droop)
        tm[x] = t
        return x
    jit = lambda: 1 + rng.uniform(-0.05, 0.05)
    base = vert(0.0, 0.0, 0.0)
    tip = vert(1.0, 0.0, 0.0)
    sides = []
    for sg in (-1, 1):
        row = []
        for t, h in outline:
            y = h * W * jit()
            row.append(vert(t, sg * y, 0.0, droop=fold * y))
        sides.append(row)
    ridge_v = [vert(t, 0.0, c * L) for t, c in ridge]
    keel_v = [vert(t, 0.0, -c * L) for t, c in keel]
    te = [t for t, _ in outline]
    fs = []
    # each side of the top (and of the underside) is the strip between the edge row and the ridge (keel) row, both
    # running base -> tip: zipped into triangles in order of t
    halves = []
    for mid, tmid in ((ridge_v, [t for t, _ in ridge]), (keel_v, [t for t, _ in keel])):
        halves.append(len(fs))
        for E in sides:
            fs.append(bm.faces.new((base, E[0], mid[0])))
            i = j = 0
            while i < len(E) - 1 or j < len(mid) - 1:
                if j == len(mid) - 1 or (i < len(E) - 1 and te[i + 1] <= tmid[j + 1]):
                    fs.append(bm.faces.new((E[i], E[i + 1], mid[j])))
                    i += 1
                else:
                    fs.append(bm.faces.new((E[i], mid[j + 1], mid[j])))
                    j += 1
            fs.append(bm.faces.new((E[-1], tip, mid[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    # inside-out test: every top face must face along the leaf normal and every underside face against it (an edge
    # drooping past the keel line flips the base / tip triangles, see KEEL_GUARD)
    flips = 0
    for i, f in enumerate(fs):
        f.normal_update()
        _, _, N = frame(sum(tm[v] for v in f.verts) / 3)
        top_face = i < halves[1]
        flips += (f.normal.dot(N) <= 0) if top_face else (f.normal.dot(N) >= 0)
    leaf_mesh.flips = flips
    below = 0                   # edge verts deeper (along the leaf normal) than the keel line at their t: must be 0
    for row in sides:
        for v in row:
            c, _, N = frame(tm[v])
            below += (v.co - c).dot(N) < -_ladder(tm[v], kline) * L
    leaf_mesh.below = below
    vs = [base, tip] + sides[0] + sides[1] + ridge_v + keel_v
    a._finish(vs, LEAF, tint=1.0)
    k1, k2 = keel_v[0], keel_v[-1]
    return vs, tm, (k1, k2)


# ---- plug -----------------------------------------------------------------------------------------------------------
def plug_mesh(a, centre, rx, rz, top_z, seed):
    """An ico-2 ball (80 tris) of radii (rx, rx, rz) at centre, two broad radius pulls (+-5 %), the top pressed to a
    plane at top_z (the flattened top). Returns verts."""
    rng = random.Random(seed)
    vs = _ico(a.bm, 2)
    pulls = []
    for _ in range(2):
        d = Vector((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1) * 0.5)).normalized()
        pulls.append((d, rng.uniform(-0.05, 0.05)))
    rot = Matrix.Rotation(rng.uniform(0, 2 * math.pi), 3, "Z")
    c = Vector(centre)
    for v in vs:
        d = v.co.normalized()
        r = 1.0
        for pd, kk in pulls:
            r *= 1 + kk * math.exp(-(d.angle(pd) / 0.8) ** 2)
        p = rot @ (d * r)
        v.co = c + Vector((p.x * rx, p.y * rx, p.z * rz))
        if v.co.z > top_z:
            v.co.z = top_z
    a._finish(vs, PLUG, tint=1.0)
    return vs


def crown_mesh(a, z0, r0, r1, h, seed, sides=8):
    """The exploded's crown disc: a flared 8-sided frustum from z0 (radius r0) to z0 + h (radius r1)."""
    rng = random.Random(seed)
    bm = a.bm
    ph = rng.uniform(0, 2 * math.pi)
    rings = [[bm.verts.new((math.cos(ph + 2 * math.pi * k / sides) * r * (1 + rng.uniform(-0.04, 0.04)),
                            math.sin(ph + 2 * math.pi * k / sides) * r * (1 + rng.uniform(-0.04, 0.04)), z))
              for k in range(sides)] for z, r in ((z0, r0), (z0 + h, r1))]
    faces = [bm.faces.new((rings[0][k], rings[0][(k + 1) % sides], rings[1][(k + 1) % sides], rings[1][k]))
             for k in range(sides)]
    faces += _cap(bm, rings[0], flip=True) + _cap(bm, rings[1])
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    vs = rings[0] + rings[1]
    a._finish(vs, CROWN, tint=1.0)
    return vs


# ---- parts ----------------------------------------------------------------------------------------------------------
PART_BUD = (0.55, 0.68, 18011)
PART_STEM = (0.16, 0.75, 18021)
PART_LEAF = dict(L=1.6, W=0.72, pitch=15.0, slope=-12.0, seed=18031)
PART_PLUG = (0.85, 0.77, 18041)


def bud_part(a):
    """HerbShrubBud: one 0.55 x 0.68 bud standing on its bottom point."""
    w, h, seed = PART_BUD
    vs, hf = bud_mesh(a, (0, 0, 0), (0, 0, 1), w, h, seed)
    if COLOUR[0]:
        paint_bud(a, vs, hf, seed)


def stem_part(a):
    """HerbShrubStem: a 0.16 x 0.75 six-sided prism."""
    d, L, seed = PART_STEM
    vs = stem_mesh(a, (0, 0, 0), (0, 0, L), d / 2, seed)
    if COLOUR[0]:
        paint_stem(a, vs, part=True)


def leaf_part(a):
    """HerbShrubLeaf: one leaf as the parts cell (L 1.6, W 0.68, base pitch 15 degrees, light curl)."""
    c = PART_LEAF
    path = leaf_path((0, 0, 0.1), 0.0, (c["L"] * 0.97, 0.12), c["pitch"], c["slope"])
    vs, tm, k = leaf_mesh(a, path, c["W"], c["seed"], roll=0.0)
    if COLOUR[0]:
        paint_leaf(a, vs, tm, k, "young", c["seed"], plug=None)


def plug_part(a):
    """HerbShrubRootPlug: an ico-2 ball 0.85 x 0.77 (W : H 1.11), its top pressed flat."""
    w, h, seed = PART_PLUG
    rz = h / (1.0 + 0.85)                     # the flat top at 0.85 of the unit sphere's height above its centre
    vs = plug_mesh(a, (0, 0, rz), w / 2, rz, rz + 0.85 * rz, seed)
    if COLOUR[0]:
        paint_plug(a, vs, top=rz + 0.85 * rz, ground=0.0)


# ---- hero layout (build frame: front -Y, +X right, ground z 0, origin = the plant axis) -----------------------------
# round 3: rx 0.45 -> 0.36 (N2: the plug showed as a dark pot under the rosette; the sheet shows only dark wedges)
PLUG_H = dict(centre=(0.0, 0.0, -0.08), rx=0.36, rz=0.24, top=0.13, seed=18101)
CROWN_H = dict(z0=0.07, r0=0.24, r1=0.28, h=0.10, seed=18102)
STEMS = {   # name: (base, direction (unit, from azimuth / lean), length, radius, seed)
    "main": ((0.0, 0.0, 0.06), (0.0, 0.0), 1.56, 0.075, 18111),
    # round 2: the short stem starts behind the axis low in the leaf heart, crosses the main stem inside the leaf
    # roots and leans 43 deg toward az -51, so it projects 30 deg in the front and 36 deg in the side_left
    # (sheet 25-30 / 35-39; round 1: 23 deg -> 15 / 18). Round 3: the base moved back-left (same lean), so the bud
    # sits nearer the axis in the top view (top r 0.84 -> ~0.6, the study's 0.62) with the same projected angles
    "short": ((-0.12, 0.25, 0.20), (-51.0, 43.0), 1.25, 0.07, 18112),
}
BUDS = {    # name: (stem, width, height, axis tilt from vertical toward the stem's azimuth (degrees), seed)
    "main": ("main", 0.55, 0.68, 0.0, 18121),
    "short": ("short", 0.45, 0.52, 15.0, 18122),
}
BUD_SINK = 0.10         # the stem's top end sits this far into the bud past its bottom point (spec 6)
LEAF_BASE_R = 0.06      # inner leaf roots start well inside the plug (their thick part must cut into it for the union)
ARCH_BASE_R = 0.21      # round 3: the outer leaf roots start out at the crown's rim, so their lower edges skirt the plug
# Round 3 (M018_spec.md "Round 3 fixes"): the outer leaves, each a short narrow stalk out of the crown (hidden in
# the heart) to the joint at leaf t 0.23-0.32, then a broad board out to the tip. Upper tier L1 / L3 (the side
# shoulders): boards carried out level at z ~1.0-1.07 with only the tip dropping; lower tier L2 / L4-L7: boards that
# peak early (z 0.73-0.87 near r 0.45) and fall 25-35 deg to tips on or near the ground. L2 is lower tier, not
# upper: the side cell wants its tip at h ~0.2 and the rear needs it over the plug. L1 / L7 sit at 354 / 28 deg so
# the f34's right end is the high L1 and the top view keeps seven separate tips.
# name: (azimuth, width, joint (r, z), tip (r, z), tip slope, base z, tip turn, maturity, seed)
ARCH = {
    "L1": (354.0, 0.90, (0.30, 0.72), (1.48, 1.00), -14.0, 0.10, -4.0, "young", 18131),
    "L2": (80.0, 0.82, (0.28, 0.55), (1.38, 0.08), -35.0, 0.12, -4.0, "young", 18132),
    "L3": (148.0, 0.90, (0.30, 0.72), (1.46, 0.98), -14.0, 0.12, 4.0, "mid", 18133),
    "L4": (194.0, 0.96, (0.30, 0.68), (1.51, 0.03), -35.0, 0.12, -6.0, "mid", 18134),
    "L5": (248.0, 0.70, (0.28, 0.30), (1.28, 0.05), -30.0, 0.12, 5.0, "old", 18135),
    "L6": (285.0, 0.80, (0.27, 0.70), (1.30, 0.00), -40.0, 0.12, -3.0, "young", 18136),
    "L7": (28.0, 0.96, (0.31, 0.66), (1.47, 0.18), -28.0, 0.12, -4.0, "mid", 18137),
}
# the two upright inner leaves (one cubic each)
# name: (azimuth, width, base pitch, tip slope, tip (r, z), base z, tip turn, maturity, seed, midline peak z or None)
LEAVES = {
    # round 3: W 0.52 / 0.50 -> 0.70 / 0.68 (the verifier's minor 4; W : L ~0.44, the sheet's inner leaf behind the
    # short bud). I1 at 335 deg (study 325): at 325 it stood in front of the short stem in the side_left view
    "I1": (335.0, 0.70, 76.0, 50.0, (0.62, 1.75), 0.26, 0.0, "mid", 18138, None),
    # I2 at 125 deg (study 150): at 150 it shared L3's vertical plane, and the union left L3's blade hanging on a
    # 0.005-stud pinch (a 0.5 deg needle whose collapse split the hero); front f 0.40 and rear screen-right as before
    "I2": (125.0, 0.68, 76.0, 50.0, (0.58, 1.62), 0.28, 0.0, "mid", 18139, None),
}


# per-leaf Bezier handle lengths (base, tip), fractions of the chord, where a leaf needs other than HANDLES
LEAF_HANDLES = {}
ARCH_KW = {"L1": dict(handles=(0.25, 0.55)), "L3": dict(handles=(0.25, 0.55)), "L2": dict(handles=(0.45, 0.30)),
           "L4": dict(handles=(0.45, 0.30)), "L7": dict(handles=(0.45, 0.30))}
KITE = ((0.0, 0.30), (0.22, 0.50), (0.48, 0.42), (0.72, 0.27), (0.88, 0.13))   # the front diamond leaf
SKIRT = ((0.55, 0.24),)        # the lower tier's broad leaf bases: they come down round the plug (N2)
ARCH_OPTS = {           # per-leaf roll (degrees about the midline, + lifts the leaf's left edge), board outline, stalk:
    "L1": dict(roll=15.0),      # the side leaves turn their faces toward the front, as every sheet cell draws them
    "L3": dict(roll=-15.0),
    "L2": dict(stalk=SKIRT),
    "L4": dict(roll=-15.0),
    "L6": dict(board=KITE),
    "L7": dict(roll=15.0),
}
# round 3: the upright inner leaves turned about their midlines so their faces look to the front (edge-on they read as
# the verifier's "upright spikes" in the front and f34; the sheet draws them broad)
INNER_ROLL = {"I1": 75.0, "I2": -25.0}
INFO = {}


def _stem_ends(name):
    base, (az, lean), L, r, seed = STEMS[name]
    B = Vector(base)
    d = Vector((math.sin(math.radians(lean)) * math.cos(math.radians(az)),
                math.sin(math.radians(lean)) * math.sin(math.radians(az)), math.cos(math.radians(lean))))
    return B, B + d * L, d


def _self_cross(vs):
    """Face pairs of one piece that cross each other (not sharing a vertex): must be 0 before the union."""
    from mathutils.bvhtree import BVHTree
    fs = K.faces_of(vs)
    idx = {v: i for i, v in enumerate(vs)}
    t = BVHTree.FromPolygons([v.co.copy() for v in vs], [[idx[v] for v in f.verts] for f in fs])
    return sum(1 for x, y in t.overlap(t) if x < y and not set(fs[x].verts) & set(fs[y].verts))


def _inverted_bm(verts, faces):
    """Faces that point into their own closed piece: a ray from just off the face along its normal crosses the piece
    an odd number of times. Must be 0 (an inside-out region makes exact booleans drop the piece)."""
    from mathutils.bvhtree import BVHTree
    idx = {v: i for i, v in enumerate(verts)}
    t = BVHTree.FromPolygons([v.co.copy() for v in verts], [[idx[v] for v in f.verts] for f in faces])
    bad = 0
    for f in faces:
        n = f.normal.normalized()
        o = f.calc_center_median() + n * 1e-4
        hits, d = 0, 0.0
        while True:
            loc, nn, i, dist = t.ray_cast(o, n)
            if loc is None:
                break
            hits += 1
            o = loc + n * 1e-5
            if hits > 50:
                break
        bad += hits % 2
    return bad


def _inverted(vs):
    fs = K.faces_of(vs)
    for f in fs:
        f.normal_update()
    return _inverted_bm(vs, fs)


def inverted(o):
    """_inverted_bm over a whole object."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.normal_update()
    n = _inverted_bm(list(bm.verts), list(bm.faces))
    bm.free()
    return n


def hero(a):
    """HerbShrubNode: plug + crown, 2 stems, 2 buds, 9 leaves (M018_spec.md 2)."""
    pc = PLUG_H
    plug = plug_mesh(a, pc["centre"], pc["rx"], pc["rz"], pc["top"], pc["seed"])
    cc = CROWN_H
    crown = crown_mesh(a, cc["z0"], cc["r0"], cc["r1"], cc["h"], cc["seed"])
    stems, buds = {}, {}
    for name, (base, (az, lean), L, r, seed) in STEMS.items():
        p0, p1, d = _stem_ends(name)
        stems[name] = dict(verts=stem_mesh(a, p0, p1, r, seed), p0=p0, p1=p1)
    for name, (sname, w, h, tilt, seed) in BUDS.items():
        p0, p1, d = _stem_ends(sname)
        az = STEMS[sname][1][0]
        ax = Vector((math.sin(math.radians(tilt)) * math.cos(math.radians(az)),
                     math.sin(math.radians(tilt)) * math.sin(math.radians(az)), math.cos(math.radians(tilt))))
        bottom = p1 - d * BUD_SINK
        vs, hf = bud_mesh(a, bottom, ax, w, h, seed)
        buds[name] = dict(verts=vs, hf=hf, bottom=bottom, axis=ax)
        INFO.setdefault("buds", {})[name] = dict(bottom=[round(x, 3) for x in bottom],
                                                 top=[round(x, 3) for x in bottom + ax * h])
    leaves = {}
    specs = []
    for name, (az, w, joint, tip, slope, z0, turn, mat_, seed) in ARCH.items():
        base = (math.cos(math.radians(az)) * ARCH_BASE_R, math.sin(math.radians(az)) * ARCH_BASE_R, z0)
        specs.append((name, arch_path(base, az, joint, tip, slope, tip_turn=turn, **ARCH_KW.get(name, {})),
                      w, mat_, seed))
    for name, (az, w, pitch, slope, tip, z0, turn, mat_, seed, pk) in LEAVES.items():
        base = (math.cos(math.radians(az)) * LEAF_BASE_R, math.sin(math.radians(az)) * LEAF_BASE_R, z0)
        specs.append((name, leaf_path(base, az, tip, pitch, slope, tip_turn=turn, peak=pk,
                                      handles=LEAF_HANDLES.get(name, HANDLES)), w, mat_, seed))
    for name, path, w, mat_, seed in specs:
        INFO.setdefault("leaf_peak", {})[name] = round(max(_bez(path, i / 30).z for i in range(31)), 2)
        INFO.setdefault("leaf_len", {})[name] = round(sum((_bez(path, (i + 1) / 30) - _bez(path, i / 30)).length
                                                          for i in range(30)), 2)
        if len(path) == 7:
            opt = ARCH_OPTS.get(name, {})
            ol, rg, kl = arch_layout(path, opt.get("board", BOARD_OUTLINE), opt.get("stalk", STALK))
            vs, tm, k = leaf_mesh(a, path, w, seed, roll=opt.get("roll", 0.0), outline=ol, ridge=rg, keel=kl)
            INFO.setdefault("leaf_joint_t", {})[name] = round(path.ts, 2)
        else:
            vs, tm, k = leaf_mesh(a, path, w, seed, roll=INNER_ROLL.get(name, 0.0))
        INFO.setdefault("leaf_self", {})[name] = _self_cross(vs)
        INFO.setdefault("leaf_inverted", {})[name] = (leaf_mesh.below, leaf_mesh.flips, _inverted(vs))
        leaves[name] = dict(verts=vs, tm=tm, keel=k, maturity=mat_, seed=seed)
    if COLOUR[0]:
        for name, L in leaves.items():
            paint_leaf(a, L["verts"], L["tm"], L["keel"], L["maturity"], L["seed"], plug=Vector((0, 0, 0.3)),
                       inner=name.startswith("I"))
        for name, b in buds.items():
            paint_bud(a, b["verts"], b["hf"], BUDS[name][4])
        for name, s in stems.items():
            paint_stem(a, s["verts"])
        paint_plug(a, plug, top=PLUG_H["top"], ground=0.0, shade=True)
        paint_plug(a, crown, top=PLUG_H["top"], ground=0.0, crown=True, shade=True)


# ---- stage 4: colour by position fields (never facing) ------------------------------------------------------------
STEPS = 4                       # quarter steps on each side of the leaf ladder
LEAF_LADDER = ((0.12, -1.0), (0.36, 0.0), (0.58, 0.0), (0.88, 1.0))   # (t, value): -1 base .. 0 leaf .. +1 tip
MATURITY = {"young": (0.12, 0.0), "mid": (0.0, 0.0), "old": (-0.2, 0.35)}   # (t shift, extra base mix in the middle)
KEEL_SHIFT = 0.25               # faces on the keel (underside) -> this much toward leaf_base
HEART = (0.95, 1.0)             # leaf faces within this radius of the axis -> up to this much toward leaf_base
HEART_Z = (0.7, 1.3)            # ... fading out between these heights on the inner leaves
HEART_TINT = (0.7, 0.72)        # outer leaves: Tint down to 0.72 at the axis, back to 1 at r 0.7
LEAF_NOISE = dict(amp=0.08, scale=1.1, seed=18201)
BUD_LADDER = ((0.20, -1.0), (0.42, 0.0), (0.62, 0.0), (0.86, 1.0))    # (height frac, value): -1 base .. +1 tip
STEM_LOW = (0.45, 0.80, 0.35)    # stems: below z 0.45 -> 35 % leaf_base, blended up to z 0.8
PLUG_FIELD = dict(top=0.10, ground=0.06, noise=0.3, level=0.3, seed=18211)
MOTTLE = {"leaf": dict(amp=0.035, scale=0.5, jitter=0.006), "stem": dict(amp=0.03, scale=0.8, jitter=0.004),
          "bud": dict(amp=0.02, scale=0.9, jitter=0.004), "plug": dict(amp=0.05, scale=0.3, jitter=0.006)}
PIECE_TINT = 0.04


def _ladder(x, pts):
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, v0), (x1, v1) in zip(pts, pts[1:]):
        if x <= x1:
            return v0 + (v1 - v0) * (x - x0) / max(x1 - x0, 1e-9)
    return pts[-1][1]


def _q(t, steps=STEPS):
    return round(max(-1.0, min(1.0, t)) * steps) / steps


def _key3(mid, low, high, v):
    v = _q(v)
    if v < 0:
        return K.mix_key(mid, low, -v)
    return K.mix_key(mid, high, v)


def _tint_mottle(a, verts, level, kind, seed):
    m = MOTTLE[kind]
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in _faces(verts):
        c = f.calc_center_median()
        k = level * (1.0 + m["amp"] * 1.6 * noise.noise(c * m["scale"] + off) + rng.uniform(-m["jitter"], m["jitter"]))
        for l in f.loops:
            l[a.tint_layer] = (k, k, k, 1.0)


def paint_leaf(a, vs, tm, keel, maturity, seed, plug=None, inner=False):
    """Base -> tip along the leaf's own length parameter t (from its construction, not world z), broad noise on t,
    the leaf's maturity shift, the keel (underside) faces a step toward leaf_base."""
    shift, old_mix = MATURITY[maturity]
    nz = LEAF_NOISE
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in _faces(vs):
        t = sum(tm[v] for v in f.verts) / len(f.verts)
        c = f.calc_center_median()
        t += nz["amp"] * 1.6 * noise.noise(c * nz["scale"] + off) + shift
        v = _ladder(t, LEAF_LADDER)
        if old_mix and abs(v) < 0.5:
            v -= old_mix
        if any(x in f.verts for x in keel):
            v -= KEEL_SHIFT
        if plug is not None:
            # the heart of the rosette is darker (the sheet's top view: #2B491B within 0.3 of the axis, #467033 to
            # 0.6): by horizontal distance from the plant axis, a position field, never facing
            r = math.hypot(c.x - plug.x, c.y - plug.y)
            # round 2: the heart fades out above z 0.5-0.9, so the upright inner leaves keep the `leaf` key up top
            # (they read as dark spikes) while the rosette's centre stays dark
            hz = min(1.0, max(0.0, (HEART_Z[1] - c.z) / (HEART_Z[1] - HEART_Z[0]))) if inner else 1.0
            v -= HEART[1] * max(0.0, 1.0 - r / HEART[0]) * hz
        f.material_index = a._mi(_key3(LEAF, LEAF_BASE, LEAF_TIP, v))
    _tint_mottle(a, vs, 1.0 + rng.uniform(-PIECE_TINT, PIECE_TINT), "leaf", seed + 7)
    if plug is not None and not inner:
        # round 2: the rosette's heart deeper still (the sheet's top view #2A481A within 0.2 of the radius): Tint
        # down to HEART_TINT by horizontal distance from the axis, a position field (never facing)
        for f in _faces(vs):
            c = f.calc_center_median()
            r = math.hypot(c.x - plug.x, c.y - plug.y)
            k = 1.0 - (1.0 - HEART_TINT[1]) * max(0.0, 1.0 - r / HEART_TINT[0])
            for l in f.loops:
                l[a.tint_layer] = tuple(x * k for x in l[a.tint_layer][:3]) + (1.0,)


def paint_bud(a, vs, hf, seed):
    """Bud base (warm) -> body -> pale tip by height within the bud."""
    rng = random.Random(seed)
    for f in _faces(vs):
        h = sum(hf[v] for v in f.verts) / len(f.verts)
        f.material_index = a._mi(_key3(BUD, BUD_BASE, BUD_TIP, _ladder(h, BUD_LADDER)))
    _tint_mottle(a, vs, 1.0 + rng.uniform(-PIECE_TINT * 0.5, PIECE_TINT * 0.5), "bud", seed + 7)


def paint_stem(a, vs, part=False):
    """Stem green; low down among the leaf bases a blend toward leaf_base."""
    z0, z1, amt = STEM_LOW
    for f in _faces(vs):
        c = f.calc_center_median()
        t = 0.0 if part else amt * min(1.0, max(0.0, (z1 - c.z) / (z1 - z0)))
        t = round(t / amt * 3) / 3 * amt if t else 0.0
        f.material_index = a._mi(K.mix_key(STEM, LEAF_BASE, t))
    _tint_mottle(a, vs, 1.0, "stem", 18221)


def paint_plug(a, vs, top, ground, crown=False, shade=False):
    """Plug body; its top and the crown -> plug_crown; the ground contact half-way; broad soil patches.
    shade (the hero): the plug sits deep under the leaves, where the sheet draws it almost black-brown (#352A1C), far
    darker than the studio lights it: plug_crown -> plug_shade by height (the top darkest) with the same patches."""
    pf = PLUG_FIELD
    nf = K.noise_field(scale=pf["noise"] * 3, seed=pf["seed"])
    for f in _faces(vs):
        c = f.calc_center_median()
        if shade:
            t = 1.0 if (crown or c.z > top - pf["top"]) else 0.75
            if nf(c) > pf["level"]:
                t -= 0.25
            f.material_index = a._mi(K.mix_key(CROWN, SHADE, t))
            continue
        if crown or c.z > top - pf["top"]:
            t = 1.0
        else:
            t = 0.0
            if c.z < ground + pf["ground"]:
                t = 0.5
            n = nf(c)
            if n > pf["level"]:
                t = max(t, 0.25 if n < pf["level"] + 0.15 else 0.5)
        f.material_index = a._mi(K.mix_key(PLUG, CROWN, t))
    _tint_mottle(a, vs, 1.0, "plug", 18231)


# ---- cleanup ------------------------------------------------------------------------------------------------------
def _volume(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    v = bm.calc_volume(signed=True)
    bm.free()
    return v


UNION_MERGE = 0.0005


def _union(o, tries=5):
    """Guarded union: each shell is unioned on with an exact boolean, one at a time, and the result is checked
    against the volumes going in (an exact union that loses track of inside/outside throws most of the mesh away).
    A bad result is undone and the shell retried nudged by a few thousandths of a stud; a shell that still fails is
    reported and left out. Stray verts are dropped before each union. Returns {"shells", "retried", "failed"}."""
    act = bpy.context.view_layer.objects.active
    if act and act.mode != "OBJECT":
        with bpy.context.temp_override(active_object=act, object=act):
            bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()     # split_loose copies o's matrix_world: it must not be stale (M019)
    others = M.split_loose(o)
    retried, failed = [], []
    rng = random.Random(18900)
    for i, p in enumerate(others):
        for ob in (o, p):
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            loose = [v for v in bm.verts if not v.link_faces]
            if loose:
                bmesh.ops.delete(bm, geom=loose, context="VERTS")
                bm.to_mesh(ob.data)
            bm.free()
        v0, vp = _volume(o.data), _volume(p.data)
        home = p.matrix_world.copy()
        ok = False
        for t in range(tries):
            keep = o.data.copy()
            if t:
                p.matrix_world = Matrix.Translation(Vector([rng.uniform(-1, 1) * 0.006 * t for _ in range(3)])) @ home
            bpy.context.view_layer.update()     # a stale matrix_world makes the boolean silently not union (M019)
            m = o.modifiers.new("U", "BOOLEAN")
            m.operation, m.solver, m.object = "UNION", "EXACT", p
            m.material_mode = "TRANSFER"
            with M._override(o):
                bpy.ops.object.modifier_apply(modifier=m.name)
            v1 = _volume(o.data)
            if v1 >= max(v0, vp) * 0.995 and v1 <= (v0 + vp) * 1.005:
                ok = True
                bpy.data.meshes.remove(keep)
                if t:
                    retried.append((i, t))
                break
            old = o.data
            o.data = keep
            bpy.data.meshes.remove(old)
        if not ok:
            failed.append(i)
        bpy.data.objects.remove(p, do_unlink=True)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    # a tight merge: at 0.004 the merge pinched thin leaf flanks into faces crossing their neighbours
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=UNION_MERGE)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=UNION_MERGE)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    M.drop_specks(bm, min_area=0.02)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    K.drop_unused_slots(o)
    return {"shells": len(others) + 1, "retried": retried, "failed": failed}


def _fix_floor(o):
    """Faces the floor cut made (flat, facing down at z 0): plug crown near the centre, leaf colour under the cut leaf
    tips; Tint 0.95."""
    p = m011._Paint(o, off=(0, 0, 0))
    lay = p.tint_layer
    bc = m011._bottom_centre(o)
    for f in p.bm.faces:
        c = f.calc_center_median()
        if f.normal.z < -0.99 and abs(c.z) < 1e-3:
            r = math.hypot(c.x - bc.x, c.y - bc.y)
            f.material_index = p._mi(K.mix_key(PLUG, CROWN, 0.5) if r < 0.6 else K.mix_key(LEAF, LEAF_BASE, 0.5))
            for l in f.loops:
                l[lay] = (0.95, 0.95, 0.95, 1.0)
    p.done()


def _finish(o):
    res = M.finish(o, union=False, uv=UV)
    for _ in range(3):
        crumbs = m012._drop_inner(o)
        if not (crumbs or res["nonmanifold_edges"] or res["boundary_edges"]):
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
        _guarded(o, lambda: m012._force_slivers(o))
        res = M.finish(o, union=False, uv=UV)
    return res


def _guarded(o, fn):
    """Run a cleanup step on o, and undo it if it leaves more crossing faces than before (collapsing a sliver's edge
    can fold a thin leaf flank through its neighbour). Returns fn's result, or None if undone."""
    before = (_self_hits(o)[0], len(_shell_report(o)))
    keep = o.data.copy()
    out = fn()
    after = (_self_hits(o)[0], len(_shell_report(o)))
    if after[0] > before[0] or after[1] > before[1]:     # round 2: a collapse that splits a shell is undone too
        old = o.data
        o.data = keep
        bpy.data.meshes.remove(old)
        return None
    bpy.data.meshes.remove(keep)
    return out


def _tri_quads(bm):
    """m012._tri_quads, but a quad that an earlier edge rotation already turned into a triangle is skipped (m012's
    version unpacks it as four verts and fails)."""
    n = 0
    for f in [f for f in bm.faces if len(f.verts) > 3]:
        if not f.is_valid or len(f.verts) < 4:
            continue
        if len(f.verts) > 4:
            bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="BEAUTY")
            n += 1
            continue
        a, b, c, d = f.verts
        opts = sorted(((min(m011._min_angle([p.co, q.co, r.co]), m011._min_angle([p.co, q.co, s.co])), p, q)
                       for p, q, r, s in ((a, c, b, d), (b, d, c, a))), key=lambda x: -x[0])
        for _, p, q in opts:
            e = bm.edges.get((p, q))
            if e is None or bmesh.ops.rotate_edges(bm, edges=[e], use_ccw=False)["edges"]:
                break
        else:
            continue
        if f.is_valid and len(f.verts) == 4:
            bmesh.ops.connect_verts(bm, verts=[p, q])
            n += 1
    leftover = [f for f in bm.faces if len(f.verts) > 3]
    if leftover:
        bmesh.ops.triangulate(bm, faces=leftover, quad_method="BEAUTY", ngon_method="BEAUTY")
    return n


def _collapse_needles(o, max_len=0.05, lim=POLISH_LIM):
    """Round 2: needle triangles (a corner under lim degrees) whose shortest edge is under max_len: that edge is
    collapsed to its midpoint (a move of at most max_len / 2, nothing visible). Run guarded. Returns the count."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = 0
    for _ in range(20):
        bad = None
        for f in bm.faces:
            if math.degrees(m011._min_angle([v.co for v in f.verts])) < lim:
                e = min(f.edges, key=lambda e: e.calc_length())
                if e.calc_length() < max_len and all(v.co.z > 1e-4 for v in e.verts):
                    bad = e
                    break
        if bad is None:
            break
        bmesh.ops.collapse(bm, edges=[bad], uvs=True)
        n += 1
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    return n


def _polish(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = _tri_quads(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = _guarded(o, lambda: m012._force_slivers(o, lim=POLISH_LIM))
    if forced is None:          # undone: try the worst needles alone, with short collapses only
        forced = _guarded(o, lambda: m012._force_slivers(o, lim=3.0, max_len=0.08))
    needles = _guarded(o, lambda: _collapse_needles(o))
    bc = m011._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
    o.data.update()
    M.smart_uv(o, **UV)
    return {"split": split, "forced": forced, "uv_cut": m012._uv_unfold(o)}


CLEAN_MOVE = 0.06      # sliver pass: no vertex moves further (m011's 0.18 folded two thin leaf flanks through each other)


def _clean_mesh(o, planes=(0.0,)):
    """The sliver pass, guarded (round 2): the narrower leaves leave more crossings of thin flanks in the heart, and
    an unguarded pass folded some through their neighbours. Each step is undone if it raises the number of crossing
    faces; the sliver pass is then retried with shorter moves."""
    pockets = m012._drop_inner(o)
    log = None
    for mv in (CLEAN_MOVE, CLEAN_MOVE / 2, CLEAN_MOVE / 4):
        log = _guarded(o, lambda: m011._clean(o, m011._plane_lock(planes), max_move=mv))
        if log is not None:
            log["max_move"] = mv
            break
    log = log or {"undone": True}
    pockets += m012._drop_inner(o)
    log["pockets"] = pockets
    log["forced"] = _guarded(o, lambda: m012._force_slivers(o))
    return log


def _shell_report(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    out = []
    for k in range(n):
        fs = [f for f in bm.faces if ids[f.index] == k]
        c = sum((f.calc_center_median() for f in fs), Vector()) / len(fs)
        out.append((sum(len(f.verts) - 2 for f in fs), [round(x, 2) for x in c]))
    bm.free()
    return sorted(out, reverse=True)


def _self_hits(o):
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    pairs = [(x, y) for x, y in tree.overlap(tree) if x < y and not set(bm.faces[x].verts) & set(bm.faces[y].verts)]
    where = [[round(c, 2) for c in bm.faces[x].calc_center_median()] for x, _ in pairs[:5]]
    bm.free()
    return len(pairs), where


PARTS = (("HerbShrubBud", bud_part), ("HerbShrubStem", stem_part), ("HerbShrubLeaf", leaf_part),
         ("HerbShrubRootPlug", plug_part))
HERO = "HerbShrubNode"
NOTES = {
    HERO: "healing herb forage node (HerbShrub): a low rosette of seven chunky faceted leaves round a squat brown root "
          "plug, two upright inner leaves, two six-sided green stems with cream faceted closed buds; one closed mesh, "
          "flat base",
    "HerbShrubBud": "Flower Bud (reusable): a cream faceted closed bud, five-facet apex, two bands, short bottom cone",
    "HerbShrubStem": "Stem (reusable): a straight six-sided green prism with flat ends",
    "HerbShrubLeaf": "Leaf (reusable): a chunky pointed leaf, kite outline, pyramid top with a ridge to the tip, keel",
    "HerbShrubRootPlug": "Root Plug (reusable): a squat faceted brown ball with a flattened top",
}


def _parts_union(o):
    """Parts are single closed shells (the plug's pressed top stays closed): only merge and tidy."""
    return {"shells": M._shells(_bm(o)), "retried": [], "failed": []}


def _bm(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    return bm


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    INFO.clear()
    objs, cleaned = {}, {}
    for name, fn in PARTS:
        o = M.mk(SHEET, name, fn, subject=TITLE, role="part", notes=NOTES[name], budget=1000, collision="hull",
                 tint_var=0.0)
        cleaned[name] = {"union": _parts_union(o)}
        cleaned[name].update(_clean_mesh(o))
        _finish(o)
        cleaned[name]["polish"] = _polish(o)
        objs[name] = o
    h = M.mk(SHEET, HERO, hero, subject=TITLE, role="hero", notes=NOTES[HERO], budget=4000, collision="hull",
             tint_var=0.0)
    hoff = M._build_offset(hero)
    un = _union(h)
    m004.floor_cut(h, z0=-hoff.z)
    _fix_floor(h)
    cleaned[HERO] = _clean_mesh(h)
    cleaned[HERO]["union"] = un
    _finish(h)
    cleaned[HERO]["polish"] = _polish(h)
    order = [h] + [objs[n] for n, _ in PARTS]
    _restyle()
    M.display(NUM, order, TITLE)
    dropped = _drop_unused(order)
    for o in order:         # flintkit stamps "studs" before the floor cut and cleanup: refresh it from the final mesh
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    out = {"audit": [{k: M.audit(o)[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges",
                                                     "boundary_edges", "normals", "ngons", "dup_verts")}
                     for o in order],
           "thin": {o.name: m012._thin(o, POLISH_LIM) for o in order}, "cleaned": cleaned, "dropped": dropped,
           "problems": K.check(order), "buds": INFO.get("buds"), "leaf_peak": INFO.get("leaf_peak"), "leaf_len": INFO.get("leaf_len"),
           "leaf_self": INFO.get("leaf_self"), "leaf_inverted": INFO.get("leaf_inverted"),
           "inverted": {o.name: inverted(o) for o in order},
           "shells": {o.name: _shell_report(o)[:4] for o in order}}
    out["self_hits"] = {o.name: _self_hits(o) for o in order}
    if render:
        out["views"] = render_views(order)
    return out


def _drop_unused(objs):
    names = {o.name for o in objs}
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.split(".")[0] in names]
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m018_")]
    out = {"meshes": len(meshes), "materials": len(mats)}
    for m in meshes:
        bpy.data.meshes.remove(m)
    for m in mats:
        bpy.data.materials.remove(m)
    for o in objs:
        if o.data.name != o.name and o.name not in bpy.data.meshes:
            o.data.name = o.name
    return out


# ---- renders ------------------------------------------------------------------------------------------------------
SHEET_VIEWS = {"front_sheet": (0, 8), "side_left": (270, 4), "side_left_sheet": (270, 8), "rear_sheet": (180, 8),
               "f34_sheet": (-28, 12), "r34_sheet": (152, 12), "top_sheet": (0, 89)}
SHEET_LENS = 3.0        # the sheet's cells are drawn almost orthographic: the *_sheet extras use a 3x longer lens (the
                        # camera backs off to keep the same fill), so near leaves are not blown up by perspective


def _long_lens(kit):
    """Wrap the kit's render_group so shots whose file name contains '_sheet' use the long lens."""
    orig = kit["render_group"]

    def rg(group, path, azimuth=-22, elevation=20):
        cam = bpy.data.objects["FB_Cam"].data
        lens = cam.lens
        if "_sheet" in path:
            cam.lens = lens * SHEET_LENS
        try:
            return orig(group, path, azimuth, elevation)
        finally:
            cam.lens = lens
    return orig, rg


def render_views(objs, names=None):
    h, bud, stem, leaf, plug = objs
    saved = M.explode(objs[1:], {})
    try:
        x0, y0 = h.location.x + 40, h.location.y
        # exploded, as the sheet: the plug low, the leaf out to the left, the stem above the plug, the bud on top
        plug.location = (x0, y0, 0.0)
        leaf.location = (x0 - 1.4, y0, 1.1)
        stem.location = (x0, y0, 1.3)
        bud.location = (x0, y0, 2.35)
        bpy.context.view_layer.update()
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        extra["exploded"] = ([plug, leaf, stem, bud], -16, 14)
        for o in objs[1:]:
            extra["part_" + o.name[9:].lower()] = ([o], -20, 35 if o is leaf else 15)
        kw = {"names": names} if names is not None else {}
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            return M.views(NUM, [h], extra=extra, **kw)
        finally:
            kit["render_group"] = orig
    finally:
        M.restore(saved)
        M.display(NUM, objs, TITLE)


# ---- measuring (the study's masks, numpy) -----------------------------------------------------------------------------
REF_VIEWS = {"f34": (25, 110, 522, 430), "r34": (530, 110, 1000, 430), "front": (22, 495, 268, 692),
             "side": (272, 495, 508, 692), "rear": (513, 495, 768, 692), "top": (772, 495, 1012, 700)}
OUR_VIEWS = {"front": "front_sheet", "side": "side_left_sheet", "rear": "rear_sheet", "f34": "f34_sheet",
             "r34": "r34_sheet", "top": "top_sheet"}
PAPER = (242, 236, 230)


def _classes(px):
    """px: (h, w, 3) sRGB 0-255, top row first -> 0 none, 1 L green, 2 U bud, 3 T plug, 4 O other (study masks)."""
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    mx, mn = px.max(-1), px.min(-1)
    v = mx / 255.0
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    d = np.maximum(mx - mn, 1e-6)
    hh = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    paper = np.abs(px - np.array(PAPER)).max(-1) <= 14
    out = np.full(r.shape, 4, np.uint8)
    out[v >= 0.88] = 0
    T = (s >= 0.18) & ((hh <= 40) | (hh >= 345)) & (v < 0.74)
    U = (hh >= 30) & (hh <= 60) & (s >= 0.10) & (s < 0.45) & (v >= 0.74)
    L = (s >= 0.22) & (hh >= 60) & (hh <= 140) & (g > 50)
    out[T] = 3
    out[U] = 2
    out[L] = 1
    out[paper] = 0
    return out


def _load(path, box=None):
    px = K.NS["KIT"]["load_px"](path)[::-1, :, :3] * 255.0      # top row first
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1]
    return np.clip(px, 0, 255)


def stats(px, flip=False):
    """Silhouette bbox, W:H, L/U/T shares, top profile (21 columns), width per height (11 rows), medians."""
    if flip:
        px = px[:, ::-1]
    c = _classes(px)
    obj = (c == 1) | (c == 2) | (c == 3)
    cols = np.nonzero(obj.sum(0) >= 3)[0]
    rows = np.nonzero(obj.sum(1) >= 3)[0]
    bx0, bx1, by0, by1 = cols.min(), cols.max(), rows.min(), rows.max()
    W, H = bx1 - bx0, by1 - by0
    sub = c[by0:by1 + 1, bx0:bx1 + 1]
    n = max(1, ((sub == 1) | (sub == 2) | (sub == 3)).sum())
    out = {"wh": round(W / H, 3), "L": round((sub == 1).sum() / n, 3), "U": round((sub == 2).sum() / n, 3),
           "T": round((sub == 3).sum() / n, 3)}
    top = []
    for i in range(21):
        x = bx0 + int(i * W / 20)
        ys = np.nonzero(obj[:, max(0, x - 1):x + 2].any(1))[0]
        top.append(round((by1 - ys.min()) / H, 2) if len(ys) else None)
    wid = []
    for i in range(11):
        y = by1 - int(i * H / 10)
        xs = np.nonzero(obj[y])[0]
        wid.append((round((xs.max() - xs.min()) / W, 2), round((xs.min() - bx0) / W, 2)) if len(xs) else None)
    hexs = lambda a: "#" + "".join(f"{int(x):02X}" for x in a)
    for k, lab in ((1, "L_med"), (2, "U_med"), (3, "T_med")):
        sel = px[c == k]
        if len(sel):
            out[lab] = hexs(np.median(sel, axis=0))
    out.update(top=top, width=wid)
    return out


def measure(views=("front", "side", "rear", "f34", "r34", "top")):
    """Sheet against our renders, per view (the study's masks on both). r34: ours flipped (spec 3.3)."""
    ref = M.ref(NUM)
    out = {}
    for v in views:
        a = stats(_load(ref, REF_VIEWS[v]))
        b = stats(_load(f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[v]}.png"), flip=(v == "r34"))
        out[v] = {"sheet": a, "ours": b}
    return out
