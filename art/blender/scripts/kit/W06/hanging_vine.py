"""W06 row 3: HANGING VINE - thick braided vines with 3-leaf ivy clusters.

Hero "HangingVine" (~7 x 4 x 7 studs): a chunk of ruined wall of chunky,
bevelled light-grey blocks (4 courses, broken stepped top, the top-right block
overhanging a missing corner block) overgrown by two thick vines that hang from
the top edge to the ground, one at the left and one wrapping the right-front
corner. Each vine is two strands twisted round a gently swinging centre line;
every ~0.8 studs a cluster of three pointed ivy leaves sits on it, alternating
left and right. Leaves spill over the wall top and pile at the foot, with moss
specks in the joints, a few rubble stones and soil patches at the roots.

Parts (collision none unless noted): VineLeafCluster, VineSegmentStraight,
VineFork, VineAttachmentPad (box). Variants (standalone vines for cliffs, ruins
and trees, front -Y, the wall side +Y): StraightVine, BranchedVine,
CurvedDraping, each starting at a grey stone attachment pad.

Technique: centre lines are Catmull-Rom curves resampled by arc length; each
strand is a helix round the centre line (rotation-minimising frames) swept as a
pentagonal tube, so the two strands cross like a braid. A leaf is a closed,
flat diamond-faceted solid: a pointed 3-lobed outline fanned to a raised centre
on top and a lowered centre below (16 tris), which gives the midrib crease.
Modularity: every strand, segment, fork arm and pad stub has radius 0.17 and
the one bark colour. One base colour per material; Tint is a small random
per-part variation, never lighting.
"""

import math

import bmesh
from mathutils import Matrix, Vector

SUBJECT = "HangingVine"
ROW = 3
PALETTE = {
    "w06_ivy": ("#66A828", 0.8, 0, 0),  # Vine leaves (row 3) and ivy leaves (row 4): pointed 3-lobed ivy leaves. One key for both rows so vines and ivy match on the map.
    "w06_moss": ("#ACC722", 0.9, 0, 0),  # Moss cushions and moss tufts (row 4 mainly, small tufts at the base of rows 1-3): the bright yellow-green of sheet swatch 3.
    "w06_stone": ("#B1ADA9", 0.9, 0, 0),  # Light warm-grey stone: ruin wall blocks (rows 3-4), vine attachment pads, the RockCap boulder and the small base rocks around bushes and ferns (sheet swatch 4). One key; facets do the shading.
    "w06_bark": ("#8D6237", 0.9, 0, 0),  # Brown woody material: bush branch stems and trunks, fern root clusters, vine and ivy stems/tendrils (sheet swatch 5).
    "w06_soil": ("#6E4B2B", 0.95, 0, 0),  # Dark earth mounds under the ferns and bushes and around vine/ivy roots on the ground. Small patches only.
}

IVY, MOSS, STONE, BARK, SOIL = "w06_ivy", "w06_moss", "w06_stone", "w06_bark", "w06_soil"
CAT = "Kit"
Z = Vector((0, 0, 1))
OUT = Vector((0, -1, 0))  # away from the wall, toward the camera

STRAND_R = 0.17  # every strand, segment, fork arm and pad stub (modular joins)
TWIST_R = 0.21   # strand offset from the vine centre line: a loose braid with gaps between strands
PITCH = 2.4      # studs per full twist of the braid
LEAF_L = 0.9     # ivy leaf length on the standalone vines (big, as drawn)
HERO_LEAF = 1.1  # the hero's leaves (~1.1 studs on the reference wall)

# broad, pointed 3-lobed ivy leaf outline: x across, y along the leaf (base at 0, tip at 1)
LEAF_OUT = [(0.0, 0.0), (0.30, 0.0), (0.56, 0.38), (0.36, 0.52), (0.27, 0.75), (0.0, 1.0),
            (-0.27, 0.75), (-0.36, 0.52), (-0.56, 0.38), (-0.30, 0.0)]


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------


def new_asset(kit, name, seed):
    return kit.flintkit.Asset(name, CAT, seed=seed, tint_var=0.06)


def curve(ctrl, step):
    """Catmull-Rom through ctrl, resampled to ~even spacing `step`. Returns points."""
    P = [Vector(p) for p in ctrl]
    if len(P) == 2:
        P = [P[0], P[0].lerp(P[1], 0.5), P[1]]
    ext = [P[0] + (P[0] - P[1])] + P + [P[-1] + (P[-1] - P[-2])]
    dense = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1:i + 3]
        for k in range(20):
            t = k / 20
            dense.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                                + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    dense.append(P[-1])
    cum = [0.0]
    for a, b in zip(dense, dense[1:]):
        cum.append(cum[-1] + (b - a).length)
    total = cum[-1]
    n = max(2, round(total / step))
    out, j = [], 0
    for i in range(n + 1):
        s = total * i / n
        while j < len(cum) - 2 and cum[j + 1] < s:
            j += 1
        seg = cum[j + 1] - cum[j]
        f = 0.0 if seg < 1e-9 else (s - cum[j]) / seg
        out.append(dense[j].lerp(dense[j + 1], min(max(f, 0.0), 1.0)))
    return out


def frames(pts, ref=OUT):
    """Tangents and rotation-minimising normal/binormal along a polyline."""
    n = len(pts)
    T = [(pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized() for i in range(n)]
    ref = Vector(ref)
    N0 = ref - ref.dot(T[0]) * T[0]
    if N0.length < 1e-3:
        N0 = Vector((1, 0, 0)) - T[0].x * T[0]
    N = [N0.normalized()]
    for i in range(1, n):
        v = N[-1] - N[-1].dot(T[i]) * T[i]
        N.append(v.normalized() if v.length > 1e-6 else N[-1])
    B = [N[i].cross(T[i]) for i in range(n)]
    s = [0.0]
    for a, b in zip(pts, pts[1:]):
        s.append(s[-1] + (b - a).length)
    return T, N, B, s


def sweep(a, pts, r, mat, sides=5, rfun=None, caps=True, ref=OUT, tint=None, phase=0.0):
    """Faceted tube along pts (radius r * rfun(u), u in 0..1). Returns rings."""
    bm = a.bm
    T, N, B, _ = frames(pts, ref)
    n = len(pts)
    rings = []
    for i in range(n):
        rr = r * (rfun(i / (n - 1)) if rfun else 1.0)
        ring = []
        for j in range(sides):
            ang = 2 * math.pi * j / sides + phase
            ring.append(bm.verts.new(pts[i] + rr * (math.cos(ang) * N[i] + math.sin(ang) * B[i])))
        rings.append(ring)
    for i in range(n - 1):
        for j in range(sides):
            bm.faces.new((rings[i][j], rings[i + 1][j], rings[i + 1][(j + 1) % sides], rings[i][(j + 1) % sides]))
    if caps:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    a._finish([v for rg in rings for v in rg], mat, tint)
    return rings, T


def cut_cap(a, ring, inward, inset=0.62, depth=0.035, mat=BARK):
    """Flat cut end with an inset ring (the reference's hollow-looking cut)."""
    bm = a.bm
    c = sum((v.co for v in ring), Vector()) / len(ring)
    inner = [bm.verts.new(c + (v.co - c) * inset + inward * depth) for v in ring]
    n = len(ring)
    for j in range(n):
        bm.faces.new((ring[j], ring[(j + 1) % n], inner[(j + 1) % n], inner[j]))
    bm.faces.new(inner)
    a._finish(inner + list(ring), mat, 1.0 + a.rng.uniform(-0.04, 0.04))


def leaf(a, base, d, nrm, L, mat=IVY, cup=0.13, thick=0.05, lift=0.07):
    """Closed flat-faceted 3-lobed ivy leaf from `base` pointing along d, face normal ~nrm."""
    d = Vector(d).normalized()
    n = Vector(nrm) - Vector(nrm).dot(d) * d
    if n.length < 1e-4:
        n = Z - Z.dot(d) * d
    n.normalize()
    x = d.cross(n)
    bm = a.bm
    base = Vector(base)
    rim = []
    for px, py in LEAF_OUT:
        up = lift * L * (abs(px) * 1.6 - py * py * 0.8)  # lobes curl up, the tip droops
        rim.append(bm.verts.new(base + L * (px * x + py * d) + n * up))
    ct = bm.verts.new(base + L * 0.42 * d + n * cup * L)
    m = len(rim)
    for i in range(m):
        bm.faces.new((ct, rim[i], rim[(i + 1) % m]))
    bm.faces.new(list(reversed(rim)))  # flat underside: closed leaf, few tris
    a._finish(rim + [ct], mat)


def cluster(a, origin, d, nrm, L=LEAF_L, spread=54, jit=10):
    """Three ivy leaves fanned from one point: a centre leaf and two smaller side leaves."""
    d = Vector(d).normalized()
    n = Vector(nrm) - Vector(nrm).dot(d) * d
    if n.length < 1e-4:
        n = Z.copy()
    n.normalize()
    k = a.rng.uniform(0.9, 1.08)
    for ang, sc in ((-spread, 0.84), (0, 1.0), (spread, 0.84)):
        r = Matrix.Rotation(math.radians(ang + a.rng.uniform(-jit, jit)), 3, n)
        dd = (r @ d + n * a.rng.uniform(0.05, 0.25)).normalized()
        leaf(a, Vector(origin) + dd * 0.04, dd, n, L * sc * k)


def braid(a, ctrl, step=0.36, sides=5, out=OUT, tail=True, head_merge=True, phase=0.0):
    """Two strands twisted round the curve through ctrl. Returns (centre pts, T, s)."""
    C = curve(ctrl, step)
    T, N, B, s = frames(C, out)
    total = s[-1]
    for k in range(2):
        pts, rad = [], []
        for i, p in enumerate(C):
            tw = TWIST_R
            if head_merge:
                tw *= min(1.0, 0.45 + s[i] / 0.8)
            if tail:
                tw *= min(1.0, 0.25 + (total - s[i]) / 1.0)
            ph = 2 * math.pi * s[i] / PITCH + k * math.pi + phase
            pts.append(p + tw * (math.cos(ph) * N[i] + math.sin(ph) * B[i]))
            rad.append(1.0 if not tail else min(1.0, 0.55 + (total - s[i]) / 1.6))
        sweep(a, pts, STRAND_R, BARK, sides=sides, rfun=lambda u, rad=rad: rad[round(u * (len(rad) - 1))],
              ref=out, phase=k * 0.6)
    return C, T, s


def leaves_along(a, C, T, s, out_fn=lambda p: OUT, start=0.4, end=None, spacing=0.8, L=LEAF_L,
                 side0=1, tip=True, flat_above=None, off=0.2):
    """Leaf clusters every `spacing` along a braid, alternating sides."""
    end = s[-1] - 0.25 if end is None else end
    sd = side0
    pos = start
    while pos <= end:
        i = min(range(len(s)), key=lambda j: abs(s[j] - pos))
        p, t = C[i], T[i]
        out = out_fn(p)
        side = out.cross(t)
        if side.length < 0.35:  # vine running toward/away from the viewer (over the wall top)
            side = Z.cross(t)
            if side.length < 1e-3:
                side = Vector((1, 0, 0))
        side.normalize()
        sj = 1.0 + a.rng.uniform(-0.1, 0.1)
        if flat_above is not None and p.z > flat_above and abs(t.z) < 0.75:
            org = p + side * sd * off * sj + Z * 0.12
            d = side * sd * 0.9 + out * 0.35 + t * 0.2
            n = Z * 0.75 + out * 0.65
        else:
            org = p + side * sd * off * sj + out * 0.12
            d = side * sd * 0.85 + Vector((0, 0, -0.5)) + out * 0.2
            n = out + Z * 0.35
        cluster(a, org, d, n, L * a.rng.uniform(0.92, 1.06))
        sd = -sd
        pos += spacing * a.rng.uniform(0.92, 1.08)
    if tip:
        p, t = C[-1], T[-1]
        out = out_fn(p)
        cluster(a, p + out * 0.1, t + out * 0.2, out + Z * 0.3, L * 0.92, spread=48)


def pad(a, cx, cz, w=1.15, h=1.3, d=0.55, y0=0.0, stub=True, stub_z=0.08, seed_rot=0.0, block=False):
    """Faceted stone attachment plate (centre cx, cz; back face flat at y0 + d/2) with a
    round bark stub in a socket on its front. Returns the stub's front point.
    block=True: a chunkier, squarer stone (chamfered-square outline, small front bevel),
    as the variants draw it."""
    bm = a.bm
    pts = []
    n = 8 if block else 7
    for i in range(n):
        if block:
            ang = 2 * math.pi * i / 8 + math.pi / 8 + seed_rot * 0.15
            k = 1.0 / math.cos(math.pi / 8)
        else:
            ang = 2 * math.pi * i / 7 + 0.35 + seed_rot
            k = 1.0
        rj = a.rng.uniform(0.9, 1.06)
        pts.append((cx + math.cos(ang) * w / 2 * rj * k, cz + math.sin(ang) * h / 2 * rj * k))
    yb, ym, yf = y0 + d / 2, y0 - d * (0.3 if block else 0.12), y0 - d / 2
    fs = 0.82 if block else 0.7
    back = [bm.verts.new((x, yb, z)) for x, z in pts]
    mid = [bm.verts.new((x, ym, z)) for x, z in pts]
    front = [bm.verts.new((cx + (x - cx) * fs, yf, cz + (z - cz) * (fs + 0.02))) for x, z in pts]
    ctr = bm.verts.new((cx + 0.03, yf - 0.05, cz + 0.02))
    m = len(pts)
    bm.faces.new(back)
    for i in range(m):
        j = (i + 1) % m
        bm.faces.new((back[j], back[i], mid[i], mid[j]))
        bm.faces.new((mid[j], mid[i], front[i], front[j]))
        bm.faces.new((front[j], front[i], ctr))
    verts = back + mid + front + [ctr]
    for v in verts:
        v.co += Vector((a.rng.uniform(-0.03, 0.03), a.rng.uniform(-0.02, 0.02), a.rng.uniform(-0.03, 0.03)))
    a._finish(verts, STONE)
    sp = Vector((cx, yf + 0.08, cz + stub_z))
    if stub:
        # socket rim: a shallow stone ring the stub sits in
        rings, _ = sweep(a, [sp + Vector((0, 0.02, 0)), sp - Vector((0, 0.1, 0))], STRAND_R * 1.45, STONE,
                         sides=6, caps=False, ref=Z)
        cut_cap(a, rings[-1], Vector((0, 1, 0)), inset=0.72, depth=0.0, mat=STONE)
        rings, _ = sweep(a, [sp, sp - Vector((0, 0.26, 0))], STRAND_R, BARK, sides=6, caps=False, ref=Z)
        cut_cap(a, rings[-1], Vector((0, 1, 0)))
    return sp - Vector((0, 0.22, 0))


def finish(a):
    bmesh.ops.recalc_face_normals(a.bm, faces=a.bm.faces)
    for v in a.bm.verts:
        if v.co.z < 0.0:
            v.co.z = 0.0
    return a.finish()


# ---------------------------------------------------------------------------
# hero
# ---------------------------------------------------------------------------

WALL_D = 3.0
COURSE_H = 1.45
# (x start, length, height) per block, bottom course first
COURSES = [
    [(-3.1, 2.1, 1.45), (-0.95, 2.2, 1.45), (1.3, 1.8, 1.45)],
    [(-3.0, 1.6, 1.45), (-1.35, 2.3, 1.45), (1.0, 2.1, 1.45)],
    [(-3.1, 2.2, 1.45), (-0.85, 2.3, 1.45), (1.5, 0.9, 1.45)],      # right corner block missing
    [(-3.15, 2.0, 1.45), (-1.1, 2.1, 1.25), (1.05, 2.4, 1.6)],     # broken, stepped top
]


def build_hero(kit):
    a = new_asset(kit, "HangingVine", 6301)
    rng = a.rng
    tops = []
    for ci, course in enumerate(COURSES):
        z0 = ci * COURSE_H
        for x0, ln, hh in course:
            dy = rng.uniform(-0.08, 0.08)
            dd = WALL_D - rng.uniform(0.0, 0.15)
            a.box((ln - 0.06, dd, hh - 0.05), loc=(x0 + ln / 2, dy, z0 + (hh - 0.05) / 2 + 0.02),
                  rot=(0, 0, rng.uniform(-0.025, 0.025)), mat=STONE, bevel=0.16, jitter=0.04)
            if ci == 3:
                tops.append((x0, ln, z0 + hh))
    fy = -WALL_D / 2  # front face

    # moss specks in joints on the front
    for x, z in ((-1.0, 1.45), (0.95, 2.9), (-0.85, 4.35), (1.35, 1.45), (0.3, 4.35), (-2.95, 2.9),
                 (1.05, 5.0), (-1.3, 0.75)):
        a.ico((0.2, 0.07, 0.11), loc=(x + rng.uniform(-0.1, 0.1), fy - 0.05, z), mat=MOSS, subdiv=1,
              jitter=0.25, rot=(0, rng.uniform(-0.4, 0.4), 0))
    # rubble stones and soil at the foot
    for x, y, r in ((-0.6, -2.1, 0.32), (0.4, -2.2, 0.24), (1.7, -2.0, 0.28)):
        a.ico((r * 1.3, r, r * 0.8), loc=(x, y, r * 0.45), mat=STONE, subdiv=1, jitter=0.2,
              rot=(0, 0, rng.uniform(0, 3)))
    for x in (-2.0, 2.75):
        a.ico((0.75, 0.5, 0.16), loc=(x, -2.2, 0.0), mat=SOIL, subdiv=1, jitter=0.15)

    vy = fy - 0.38  # vine centre line, just off the face
    left = [(-1.85, 0.4, 6.05), (-1.95, -0.9, 6.05), (-2.0, fy - 0.1, 5.7), (-1.75, vy, 4.9),
            (-2.15, vy, 3.9), (-1.8, vy, 2.9), (-2.2, vy, 1.9), (-1.85, vy - 0.05, 0.9),
            (-2.05, vy - 0.2, 0.33), (-2.3, vy - 0.45, 0.3)]
    right = [(2.55, 0.5, 6.25), (2.75, -0.8, 6.3), (2.95, fy - 0.1, 5.85), (3.05, vy, 4.95),
             (2.75, fy - 0.15, 3.9), (3.45, -1.1, 2.6), (3.38, fy - 0.12, 1.5), (2.95, vy - 0.05, 0.65),
             (2.7, vy - 0.2, 0.33), (2.45, vy - 0.45, 0.3)]

    def out_right(p):
        if p.x > 3.1 and p.z < 3.6:
            return Vector((1.0, -0.55, 0)).normalized()
        return OUT

    for ctrl, fn, s0, ph in ((left, lambda p: OUT, 1, 0.0), (right, out_right, -1, 1.3)):
        C, T, s = braid(a, ctrl, step=0.36, sides=5, tail=False, phase=ph)
        leaves_along(a, C, T, s, out_fn=fn, start=0.25, spacing=0.85, side0=s0, tip=False,
                     flat_above=5.4, end=s[-1] - 0.6, L=HERO_LEAF, off=0.24)

    # extra leaves on the wall top and a pile at the foot
    for x, y, z, ang in ((-1.0, -0.6, 5.85, 0.3), (-2.6, -0.3, 5.87, 2.2), (2.0, -0.9, 6.0, -0.4),
                         (3.25, -0.2, 6.03, 1.2)):
        d = Vector((math.cos(ang), -0.6 + math.sin(ang) * 0.4, 0.0))
        cluster(a, (x, y, z), d, Z + Vector((0, -0.25, 0)), HERO_LEAF * 0.95)
    for x, y, ang in ((-2.9, -1.95, 3.4), (-1.2, -2.15, -0.2), (-2.3, -2.3, 4.4), (2.0, -2.15, 3.6),
                      (2.95, -1.95, -0.4)):
        d = Vector((math.cos(ang), math.sin(ang) * 0.5 - 0.3, 0.15))
        cluster(a, (x, y, 0.22), d, Z + Vector((0, -0.4, 0)), HERO_LEAF * 0.9)
    return finish(a)


# ---------------------------------------------------------------------------
# parts
# ---------------------------------------------------------------------------


def build_leaf_cluster(kit):
    a = new_asset(kit, "VineLeafCluster", 6311)
    # stalk at the back, three leaves fanned toward the front, tipped back to face the viewer
    top = Vector((0, 0, 0.62))
    sweep(a, [top + Vector((0, 0.18, 0.2)), top + Vector((0, 0.06, 0.08)), top], 0.06, BARK, sides=4, ref=OUT)
    n = Vector((0, -0.5, 0.87))
    d = Vector((0, -0.8, -0.5))
    for ang, sc in ((-58, 0.86), (0, 1.0), (58, 0.86)):
        r = Matrix.Rotation(math.radians(ang), 3, (n - n.dot(d.normalized()) * d.normalized()).normalized())
        dd = (r @ d.normalized()).normalized()
        leaf(a, top + dd * 0.04, dd, n, 0.8 * sc)
    return finish(a)


def build_segment(kit):
    a = new_asset(kit, "VineSegmentStraight", 6312)
    # leans like the reference drawing (bottom-left to top-right) with a gentle bow
    pts = curve([(0, 0.6, 0), (0.5, 0.25, 1.2), (1.1, -0.2, 2.5), (1.6, -0.7, 3.6)], 0.5)
    for p in pts[1:-1]:
        p += Vector((a.rng.uniform(-0.03, 0.03), a.rng.uniform(-0.03, 0.03), 0))
    rings, T = sweep(a, pts, STRAND_R, BARK, sides=7, caps=False, ref=OUT)
    cut_cap(a, rings[0], T[0])
    cut_cap(a, rings[-1], -T[-1])
    return finish(a)


def fork_geometry(a, j, leg, arm_l, arm_r, sides=6, cut=True):
    """Y/T junction at j: a leg and two arms, each a tube of STRAND_R with a cut outer
    end; the inner ends start inside the junction, where nobody sees them."""
    for end, bend in ((leg, Vector((0.05, 0, 0))), (arm_l, Vector((0, 0, 0.06))), (arm_r, Vector((0, 0, 0.12)))):
        end = Vector(end)
        mid = j.lerp(end, 0.5) + bend
        start = j + (end - j).normalized() * -0.1
        rings, T = sweep(a, curve([start, mid, end], 0.45), STRAND_R, BARK, sides=sides, caps=False, ref=OUT)
        if cut:
            cut_cap(a, rings[-1], -T[-1])
        else:
            a.bm.faces.new(rings[-1])


def build_fork(kit):
    a = new_asset(kit, "VineFork", 6313)
    j = Vector((-0.2, 0, 0.72))
    fork_geometry(a, j, (-0.32, 0.05, 0.0), (-0.85, 0.22, 0.82), (0.72, -0.25, 1.38))
    return finish(a)


def build_pad(kit):
    a = new_asset(kit, "VineAttachmentPad", 6314)
    pad(a, 0.0, 0.66, w=1.05, h=1.3, d=0.5, stub_z=0.05)
    return finish(a)


# ---------------------------------------------------------------------------
# variants
# ---------------------------------------------------------------------------


def hang(top, length, sway=0.25, k=0.9, ph=0.0, y=-0.55, dx=0.0, bottom=None):
    """Control points of a vine hanging from `top` straight down `length` with a sway."""
    top = Vector(top)
    n = max(3, int(length / 1.0) + 1)
    pts = [top]
    for i in range(1, n + 1):
        f = i / n
        z = top.z - length * f
        pts.append((top.x + dx * f + sway * math.sin(z * k + ph) * min(1.0, f * 3), y, z))
    return pts




PAD_W, PAD_H, PAD_D = 1.7, 1.55, 0.9  # the variants' pads read as chunky blocks, as drawn


def top_leaves(a, sp):
    """Leaves half covering a pad's top and front, as on the reference."""
    cluster(a, sp + Vector((0.2, -0.1, -0.1)), Vector((0.85, -0.25, -0.45)), Vector((0, -1.0, 0.35)), LEAF_L * 0.95)


def hanging(a, sp, length, ph=0.0, sway=0.22, k=0.85, side0=1, spacing=0.8, dx=0.0, step=0.45):
    """A braided vine leaving the pad stub at sp and hanging `length` below it, with leaves."""
    y = sp.y - 0.12
    ctrl = [sp, sp + Vector((0.04, -0.12, -0.45))] + hang(sp + Vector((0.05, -0.12, -0.85)), length,
                                                          sway=sway, k=k, ph=ph, y=y, dx=dx)[1:]
    C, T, s = braid(a, ctrl, step=step, sides=5, phase=ph)
    leaves_along(a, C, T, s, start=0.75, spacing=spacing, side0=side0)
    return y


def build_straight(kit):
    a = new_asset(kit, "StraightVine", 6321)
    sp = pad(a, 0.0, 8.55, w=PAD_W, h=PAD_H, d=PAD_D, block=True)
    hanging(a, sp, 7.7, sway=0.22, k=0.8, spacing=0.95, step=0.42)
    top_leaves(a, sp)
    return finish(a)


def build_branched(kit):
    a = new_asset(kit, "BranchedVine", 6322)
    spl = pad(a, -2.1, 7.3, w=PAD_W * 0.92, h=PAD_H, d=PAD_D, seed_rot=0.4, block=True)
    spr = pad(a, 2.0, 7.95, w=PAD_W * 0.95, h=PAD_H, d=PAD_D, seed_rot=1.1, block=True)
    y = hanging(a, spl, 6.4, sway=0.2, k=0.9, side0=1, spacing=1.0, step=0.5)
    hanging(a, spr, 7.05, ph=1.0, sway=0.2, k=0.8, side0=-1, spacing=1.0, step=0.5)
    top_leaves(a, spl)
    top_leaves(a, spr)
    # diagonal vine from the right vine down into the left vine: the fork where it joins
    j = Vector((-1.95, y, 3.5))
    dc = [(1.9, y, 6.55), (0.7, y - 0.05, 5.65), (-0.8, y - 0.08, 4.4), j]
    C, T, s = braid(a, dc, step=0.5, sides=5, tail=False, phase=2.0)
    leaves_along(a, C, T, s, start=0.6, end=s[-1] - 0.5, spacing=0.95, side0=1, tip=False)
    return finish(a)


def build_draping(kit):
    a = new_asset(kit, "CurvedDraping", 6323)
    spl = pad(a, -2.8, 6.85, w=PAD_W * 0.95, h=PAD_H * 0.95, d=PAD_D, seed_rot=0.2, block=True)
    spr = pad(a, 2.8, 7.1, w=PAD_W, h=PAD_H, d=PAD_D, seed_rot=0.9, block=True)
    y = spl.y - 0.12
    # U-shaped swag between the pads
    sc = [spl, (-2.45, y, 5.75), (-1.5, y, 4.65), (0.0, y, 4.2), (1.5, y, 4.7), (2.45, y, 5.85), spr]
    C, T, s = braid(a, sc, step=0.5, sides=5, tail=False, head_merge=True)
    leaves_along(a, C, T, s, start=0.6, end=s[-1] - 0.6, spacing=1.0, tip=False)
    # hanging ends below each pad
    hanging(a, spl, 5.3, ph=0.3, sway=0.18, k=0.9, side0=-1, spacing=1.0, dx=-0.15, step=0.5)
    hanging(a, spr, 6.0, ph=1.4, sway=0.18, k=0.9, side0=1, spacing=1.0, dx=0.15, step=0.5)
    top_leaves(a, spl)
    top_leaves(a, spr)
    return finish(a)


# ---------------------------------------------------------------------------


def build(kit):
    out = [kit.tag(build_hero(kit), "hero", collision="box", budget=5000,
                   notes="ruined wall chunk (box collision) overgrown by two braided vines; no VFX")]
    out.append(kit.tag(build_leaf_cluster(kit), "part", collision="none", budget=150,
                       notes="Leaf Cluster (3 leaves): three pointed ivy leaves on one stalk; snaps along any vine"))
    out.append(kit.tag(build_segment(kit), "part", collision="none", budget=150,
                       notes="Vine Segment (straight): 4-stud curved vine stick, r 0.17, cut ends"))
    out.append(kit.tag(build_fork(kit), "part", collision="none", budget=150,
                       notes="Vine Fork (T-joint): Y junction, arms r 0.17 to join segments"))
    out.append(kit.tag(build_pad(kit), "part", collision="box", budget=150,
                       notes="Attachment Pad (wall/rock): stone plate with a vine stub; back face (+Y) sits on the wall"))
    out.append(kit.tag(build_straight(kit), "variant", collision="none", budget=2500,
                       notes="A. Straight Vine: pad + 8-stud braided vine; hang on cliffs, ruins, trees (wall side +Y)"))
    out.append(kit.tag(build_branched(kit), "variant", collision="none", budget=2500,
                       notes="B. Branched Vine: two pads, vines joined by a fork, three hanging ends"))
    out.append(kit.tag(build_draping(kit), "variant", collision="none", budget=2500,
                       notes="C. Curved Draping: U swag between two pads plus a hanging end below each"))
    return out
