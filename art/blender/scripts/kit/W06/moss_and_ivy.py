"""W06 row 4, MOSS AND IVY: moss cushions and climbing ivy overlays for walls,
ruins and rocks.

MossAndIvy (hero, ~6.5 W x 6 D x 6.5 H): a cube-like ruin block of three
courses of chunky bevelled stone blocks (running bond, small jitter), a heap
of lumpy moss cushions on top spilling over the front edge, a dense ivy
curtain cascading down the front-right corner (right half of the front face
and the front of the right face), a small ivy patch on the lower-left of the
front, thin strips on the left face and the rear of the right face, and moss
cushions, small rocks and loose leaves at the foot.

Parts (collision none): MossCushionLarge, MossCushionSmall, IvyClusterFlat,
IvyTendril, IvyCornerPiece, IvyLeafSingle. Overlay parts stand upright and
face -Y so they can be laid on any wall. Variants: CornerWrap, WallStrip
(box) and RockCap (hull).

Technique: moss is clusters of open-bottomed puffy faceted domes (three
offset rings + apex, ~35 tris each). Ivy is a tendril (thin 4-sided tube)
projected onto the stone by ray casts against the stone-only mesh (a BVH of
the blocks or boulder), with flat pointed 3/5-lobed leaves (a fan round a
slightly raised centre) set alternately along it, tips falling down and
sideways, tilted a little off the stone. One colour per material; Tint is a
small random per-part variation; lighting does the shading.
"""

import math

from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

SUBJECT = "MossAndIvy"
ROW = 4
HERO_AZIMUTH = 22  # the sheet draws the hero and variants from the front-right
PALETTE = {
    "w06_ivy": ("#66A828", 0.8, 0, 0),  # Vine leaves (row 3) and ivy leaves (row 4): pointed 3-lobed ivy leaves. One key for both rows so vines and ivy match on the map.
    "w06_moss": ("#ACC722", 0.9, 0, 0),  # Moss cushions and moss tufts (row 4 mainly, small tufts at the base of rows 1-3): the bright yellow-green of sheet swatch 3.
    "w06_stone": ("#B1ADA9", 0.9, 0, 0),  # Light warm-grey stone: ruin wall blocks (rows 3-4), vine attachment pads, the RockCap boulder and the small base rocks around bushes and ferns (sheet swatch 4). One key; facets do the shading.
    "w06_bark": ("#8D6237", 0.9, 0, 0),  # Brown woody material: bush branch stems and trunks, fern root clusters, vine and ivy stems/tendrils (sheet swatch 5).
}
STONE, MOSS, IVY, BARK = "w06_stone", "w06_moss", "w06_ivy", "w06_bark"

TAU = 2 * math.pi
Z = Vector((0, 0, 1))
STEM_R = 0.055  # ivy tendril radius (shared look with the row 3 vines)

# Leaf outlines in (u, v): stalk at the origin, tip at v = 1, CCW seen from the front.
LEAF5 = [(0, 1.0), (-0.27, 0.72), (-0.6, 0.62), (-0.4, 0.37), (-0.5, 0.16), (-0.18, 0.02), (0, 0.12),
         (0.18, 0.02), (0.5, 0.16), (0.4, 0.37), (0.6, 0.62), (0.27, 0.72)]
LEAF3 = [(0, 1.0), (-0.28, 0.68), (-0.58, 0.52), (-0.32, 0.1), (0, 0.14), (0.32, 0.1),
         (0.58, 0.52), (0.28, 0.68)]


# ---------------------------------------------------------------------------
# Plumbing
# ---------------------------------------------------------------------------


def new(fk, name, seed):
    return fk.Asset(name, "Kit", seed=seed, tint_var=0.05)


def done(a):
    for v in a.bm.verts:
        if v.co.z < 0.0:
            v.co.z = 0.0
    return a.finish()


def frame_to(normal):
    """Rotation taking +Z to `normal`."""
    return Z.rotation_difference(Vector(normal).normalized()).to_matrix()


# ---------------------------------------------------------------------------
# Moss
# ---------------------------------------------------------------------------


def dome(a, c, r, h, n=7, normal=Z, tint=None, mat=MOSS):
    """Puffy faceted open-bottomed dome: base ring, bulging offset mid ring,
    offset upper ring and apex. r may be (rx, ry)."""
    rx, ry = (r, r) if isinstance(r, (int, float)) else r
    rng, bm = a.rng, a.bm
    rot = rng.uniform(0, TAU)
    spec = [(0.0, 0.84), (0.42, 1.0), (0.82, 0.68)]
    rings = []
    for k, (fz, fr) in enumerate(spec):
        ring = []
        for i in range(n):
            ang = rot + TAU * (i + 0.5 * k) / n
            s = fr * rng.uniform(0.9, 1.08)
            z = h * fz * (rng.uniform(0.9, 1.1) if k else 1.0)
            ring.append(bm.verts.new((rx * s * math.cos(ang), ry * s * math.sin(ang), z)))
        rings.append(ring)
    apex = bm.verts.new((rng.uniform(-0.12, 0.12) * rx, rng.uniform(-0.12, 0.12) * ry, h))
    for k in range(len(rings) - 1):
        r0, r1 = rings[k], rings[k + 1]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((r0[i], r0[j], r1[i]))
            bm.faces.new((r1[i], r0[j], r1[j]))
    top = rings[-1]
    for i in range(n):
        bm.faces.new((top[i], top[(i + 1) % n], apex))
    verts = [v for ring in rings for v in ring] + [apex]
    m = frame_to(normal)
    for v in verts:
        v.co = m @ v.co + Vector(c)
    return a._finish(verts, mat, tint)


def heap(a, z, domes, sides=7):
    """A pile of big round moss domes [(x, y, r, h)] with their bases at height z
    (a callable z(x, y) follows a surface)."""
    t = 1.0 + a.rng.uniform(-0.03, 0.03)
    for x, y, r, h in domes:
        zz = z(x, y) if callable(z) else z
        dome(a, (x, y, zz), (r, r * a.rng.uniform(0.85, 1.0)), h, sides, tint=t * (1 + a.rng.uniform(-0.03, 0.03)))


def cushion(a, c, sx, sy, h, n=5, sides=7):
    """Lumpy moss cushion: a tall centre dome ringed by n-1 lower domes, about
    sx x sy across and h tall, base at c."""
    rng = a.rng
    cx, cy, cz = c
    t = 1.0 + rng.uniform(-0.04, 0.04)
    dome(a, (cx + rng.uniform(-0.05, 0.05) * sx, cy, cz), (0.34 * sx, 0.36 * sy), h, sides, tint=t)
    k = n - 1
    a0 = rng.uniform(0, TAU)
    for i in range(k):
        ang = a0 + TAU * i / k + rng.uniform(-0.3, 0.3)
        rr = rng.uniform(0.21, 0.25) * (sx + sy)
        dx = math.cos(ang) * (0.5 * sx - rr * 0.95)
        dy = math.sin(ang) * (0.5 * sy - rr * 0.95)
        dome(a, (cx + dx, cy + dy, cz), (rr, rr * rng.uniform(0.85, 1.0)), h * rng.uniform(0.68, 0.88),
             sides, tint=t * (1 + rng.uniform(-0.03, 0.03)))


# ---------------------------------------------------------------------------
# Ivy
# ---------------------------------------------------------------------------


def leaf(a, base, vdir, nrm, size, lobes=5, tilt=0.3, back=False, tint=None, mat=IVY):
    """Flat pointed ivy leaf: stalk end at `base`, tip along vdir, facing nrm,
    the tip lifted off the surface by `tilt` radians. A fan round a raised
    centre gives it a few big facets; back=True closes it with a flat back."""
    N = Vector(nrm).normalized()
    V = Vector(vdir)
    V = (V - N * V.dot(N))
    if V.length < 1e-4:
        V = Vector((0, 0, -1)) if abs(N.z) < 0.9 else Vector((0, -1, 0))
        V = V - N * V.dot(N)
    V.normalize()
    U = V.cross(N).normalized()
    R = Matrix.Rotation(tilt, 3, U)
    V, N = R @ V, R @ N
    U = V.cross(N).normalized()
    base = Vector(base)
    pts = LEAF5 if lobes == 5 else LEAF3
    rng = a.rng
    bm = a.bm
    ring = []
    for (u, v) in pts:
        u *= rng.uniform(0.92, 1.08)
        v *= rng.uniform(0.95, 1.05)
        ring.append(bm.verts.new(base + size * (U * u + V * v)))
    centre = bm.verts.new(base + size * (V * 0.45 + N * 0.09))
    n = len(ring)
    for i in range(n):
        bm.faces.new((centre, ring[i], ring[(i + 1) % n]))
    if back:
        bm.faces.new(list(reversed(ring)))
    t = tint if tint is not None else 1.0 + rng.uniform(-0.06, 0.06)
    return a._finish(ring + [centre], mat, t)


def stem(a, pts, r=STEM_R):
    if len(pts) >= 2:
        a.tube_loop([tuple(p) for p in pts], r, mat=BARK, rseg=3, closed=False,
                    tint=1.0 + a.rng.uniform(-0.04, 0.04))


def leaves_along(a, path, step=0.4, size=(0.6, 0.85), spread=(25, 70), out=0.06, tilt=(0.15, 0.45),
                 back=False, first=0.1, every_node=1.0, side0=None):
    """Alternate leaves along path = [(point, normal)], tips falling down/sideways."""
    rng = a.rng
    side = side0 if side0 is not None else rng.choice((-1, 1))
    acc = step * first
    for i in range(1, len(path)):
        p0, n0 = path[i - 1]
        p1, n1 = path[i]
        seg = (p1 - p0).length
        while acc <= seg:
            t = acc / max(seg, 1e-6)
            P = p0.lerp(p1, t)
            N = n0.lerp(n1, t).normalized()
            T = (p1 - p0).normalized()
            if T.z > 0:  # leaves always fall away from where the ivy came from
                T = -T
            if rng.random() <= every_node:
                ang = math.radians(rng.uniform(*spread)) * side
                d = Matrix.Rotation(ang, 3, N) @ T
                d = (d + Vector((0, 0, -0.35))).normalized()
                leaf(a, P + N * (out + rng.uniform(0.0, 0.08)), d, N, rng.uniform(*size),
                     lobes=5 if rng.random() < 0.65 else 3, tilt=rng.uniform(*tilt), back=back)
            side = -side
            acc += step * rng.uniform(0.85, 1.15)
        acc -= seg


def ivy_run(a, surf, u0, z0, z1, wig=0.25, step=0.4, size=(0.6, 0.85), lip=None, back=False,
            spread=(25, 70), dz=0.5, top_leaves=2, every_node=1.0):
    """One ivy tendril from height z0 down to z1 on a surface surf(u, z) ->
    (point, normal) or (None, None), with leaves along it. lip = height of the
    top edge: the tendril then starts on the top face and curls over it."""
    rng = a.rng
    n = max(2, int(abs(z0 - z1) / dz))
    ph = rng.uniform(0, TAU)
    fr = rng.uniform(1.5, 2.5)
    path = []
    for i in range(n + 1):
        t = i / n
        z = z0 + (z1 - z0) * t
        u = u0 + wig * math.sin(ph + t * fr * math.pi) + rng.uniform(-0.04, 0.04)
        P, N = surf(u, z)
        if P is None:
            continue
        path.append((P, N))
    if len(path) < 2:
        return
    if lip is not None:
        P, N = path[0]
        h = Vector((N.x, N.y, 0)).normalized()
        e = Vector((P.x, P.y, lip))
        on_top = (e - h * 0.45 + Z * 0.05, Z.copy())
        over = (e + h * 0.04 + Z * 0.02, (Z + h).normalized())
        path = [on_top, over] + path
        for k in range(top_leaves):
            q = e - h * rng.uniform(0.0, 0.4) + Z * 0.04
            side = Matrix.Rotation(rng.uniform(-1.1, 1.1), 3, Z) @ h
            leaf(a, q, side, (Z * 1.0 + h * rng.uniform(0.1, 0.5)), rng.uniform(*size),
                 tilt=rng.uniform(0.0, 0.25), back=back)
    else:  # a crown of two upward leaves hides the stem's cut top
        P, N = path[0]
        for s in (-1, 1):
            d = Matrix.Rotation(math.radians(rng.uniform(35, 65)) * s, 3, N) @ Z
            leaf(a, P + N * 0.08, d, N, rng.uniform(*size) * 0.85, tilt=rng.uniform(0.15, 0.35), back=back)
    stem(a, [P + N * 0.05 for P, N in path])
    leaves_along(a, path, step=step, size=size, back=back, spread=spread, every_node=every_node)


# ---------------------------------------------------------------------------
# Surfaces
# ---------------------------------------------------------------------------


def box_surface(bvh, W, D, rc=0.35):
    """Ray-cast wrap of a W x D block: u = distance round the perimeter from the
    front-left corner (front face, then right, back, left), normals rounded
    over a corner radius rc."""
    faces = [((-W / 2, -D / 2), (1, 0), (0, -1), W), ((W / 2, -D / 2), (0, 1), (1, 0), D),
             ((W / 2, D / 2), (-1, 0), (0, 1), W), ((-W / 2, D / 2), (0, -1), (-1, 0), D)]
    total = 2 * (W + D)

    def surf(u, z):
        u %= total
        i = 0
        while u > faces[i][3] and i < 3:
            u -= faces[i][3]
            i += 1
        (sx, sy), (dx, dy), (nx, ny), ln = faces[i]
        n = Vector((nx, ny, 0))
        if u < rc:
            w = 0.5 + 0.5 * u / rc
            pn = Vector((*faces[i - 1][2], 0))
            n = (n * w + pn * (1 - w)).normalized()
        elif ln - u < rc:
            w = 0.5 + 0.5 * (ln - u) / rc
            nn = Vector((*faces[(i + 1) % 4][2], 0))
            n = (n * w + nn * (1 - w)).normalized()
        p = Vector((sx + dx * u, sy + dy * u, z))
        loc, _nrm, _i, _d = bvh.ray_cast(p + n * 3.0, -n, 6.0)
        if loc is None:
            return p, n
        return loc, n

    return surf


def radial_surface(bvh, centre=(0, 0)):
    """Ray-cast wrap of a lump: u = azimuth in degrees (-90 = front)."""
    cx, cy = centre

    def surf(u, z):
        d = Vector((math.cos(math.radians(u)), math.sin(math.radians(u)), 0))
        o = Vector((cx, cy, z)) + d * 12
        loc, nrm, _i, _d = bvh.ray_cast(o, -d, 24)
        if loc is None:
            return None, None
        return loc, (nrm + d * 0.5).normalized()

    return surf


def flat_surface(u, z):
    return Vector((u, 0, z)), Vector((0, -1, 0))


def corner_surface(rc=0.25):
    """Outside corner at the origin: front plane (y = 0, facing -Y) for u < 0,
    right plane (x = 0, facing +X) for u > 0."""
    def surf(u, z):
        if u < 0:
            p = Vector((u, 0, z))
        else:
            p = Vector((0, u, z))
        w = max(0.0, min(1.0, 0.5 + 0.5 * u / rc))
        n = (Vector((0, -1, 0)) * (1 - w) + Vector((1, 0, 0)) * w).normalized()
        return p, n
    return surf


# ---------------------------------------------------------------------------
# Stone
# ---------------------------------------------------------------------------


def splits(total, target, first, rng):
    out = [target * first * rng.uniform(0.9, 1.1)]
    while total - sum(out) > target * 1.45:
        out.append(target * rng.uniform(0.88, 1.12))
    rest = total - sum(out)
    if rest < target * 0.45:
        out[-1] += rest
    else:
        out.append(rest)
    return out


def stone_core(a, W, D, heights, target=(1.9, 1.8), gap=0.08, bevel=0.17):
    """Courses of bevelled blocks in running bond on every face. Hidden
    interior blocks below the top course are left out."""
    rng = a.rng
    z = 0.0
    for k, h in enumerate(heights):
        xs = splits(W, target[0], 0.55 if k % 2 else 1.0, rng)
        ys = splits(D, target[1], 1.0 if k % 2 else 0.55, rng) if D > target[1] * 1.3 else [D]
        x0 = -W / 2
        for i, wx in enumerate(xs):
            y0 = -D / 2
            for j, wy in enumerate(ys):
                interior = 0 < i < len(xs) - 1 and 0 < j < len(ys) - 1
                if not (interior and k < len(heights) - 1):
                    out = 0.04
                    dx = rng.uniform(-out, out) + (-out if i == 0 else out if i == len(xs) - 1 else 0)
                    dy = rng.uniform(-out, out) + (-out if j == 0 else out if j == len(ys) - 1 else 0)
                    hh = h - gap + rng.uniform(-0.04, 0.04)
                    a.box((wx - gap, wy - gap, hh), loc=(x0 + wx / 2 + dx, y0 + wy / 2 + dy, z + gap / 2 + hh / 2),
                          rot=(0, 0, rng.uniform(-0.025, 0.025)), mat=STONE, bevel=bevel, jitter=0.035)
                y0 += wy
            x0 += wx
        z += h
    return z


def foot_rock(a, x, y, s):
    a.rock((s, s * 0.8, s * 0.55), loc=(x, y, 0), rot=(0, 0, a.rng.uniform(0, TAU)), mat=STONE, subdiv=1,
           rough=0.15, facets=8, sink=0.1)


def ground_leaf(a, x, y, size=0.55):
    d = Matrix.Rotation(a.rng.uniform(0, TAU), 3, Z) @ Vector((1, 0, 0))
    leaf(a, (x, y, 0.04), d, Z, size, tilt=0.1, back=True)


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------


def build_hero(kit):
    a = new(kit.flintkit, "MossAndIvy", 4061)
    W, D = 5.6, 5.0
    H = stone_core(a, W, D, [1.8, 1.75, 1.75], target=(1.6, 1.7))
    bvh = BVHTree.FromBMesh(a.bm)
    surf = box_surface(bvh, W, D)
    Ht = H - 0.04
    # top moss heap, biased back/left, spilling over the front-left edge
    heap(a, Ht, [(-1.5, 1.0, 1.0, 1.15), (0.3, 1.3, 0.95, 1.1), (-0.4, -0.2, 0.9, 1.0), (1.5, 0.6, 0.75, 0.8),
                 (-1.9, -1.2, 0.8, 0.85), (-0.9, -1.7, 0.6, 0.6), (-2.2, 2.0, 0.55, 0.55), (1.0, 2.0, 0.55, 0.6)])
    for x in (-2.2, -1.2):  # drips over the front top edge
        dome(a, (x, -D / 2 - 0.02, H - 0.35 - a.rng.uniform(0, 0.2)), (0.42, 0.3), 0.28, 6,
             normal=(0, -1, 0.25))
    # ivy: dense curtain on the front-right corner
    for u, z1 in ((W - 0.15, 0.1), (W - 0.7, 0.3), (W - 1.25, 0.0), (W - 1.85, 0.5), (W - 2.5, 1.4),
                  (W + 0.5, 0.2), (W + 1.1, 0.6), (W + 1.7, 1.8)):
        ivy_run(a, surf, u, H - 0.15, z1, lip=H)
    # small patch climbing the lower-left of the front
    ivy_run(a, surf, 1.0, 2.6, 0.1, wig=0.2, top_leaves=0)
    # thin strips: rear of the right face, front of the left face
    ivy_run(a, surf, W + D - 0.7, H - 0.15, 1.4, wig=0.15, lip=H, top_leaves=1, every_node=0.8)
    ivy_run(a, surf, 2 * W + 2 * D - 1.0, H - 0.15, 2.4, wig=0.15, lip=H, top_leaves=1, every_node=0.8)
    # ivy leaves lying on the top near the corner
    for (x, y) in ((2.0, -1.6), (2.3, -0.7), (1.4, -1.9)):
        d = Matrix.Rotation(a.rng.uniform(-1, 1), 3, Z) @ Vector((0.3, -1, 0))
        leaf(a, (x, y, H + 0.03), d, Z, a.rng.uniform(0.6, 0.8), tilt=0.1)
    # foot: moss cushions, rocks, loose leaves
    heap(a, 0.0, [(-1.9, -D / 2 - 0.45, 0.8, 1.0), (-2.6, -D / 2 - 0.1, 0.5, 0.55), (-0.3, -D / 2 - 0.4, 0.6, 0.7),
                  (1.2, -D / 2 - 0.5, 0.8, 0.95), (2.0, -D / 2 - 0.35, 0.5, 0.5), (-W / 2 - 0.15, -1.5, 0.5, 0.6)])
    foot_rock(a, -2.9, -2.9, 0.8)
    foot_rock(a, 2.6, -3.0, 0.9)
    foot_rock(a, 0.55, -3.1, 0.55)
    ground_leaf(a, -1.0, -3.3)
    ground_leaf(a, 2.1, -3.2)
    obj = done(a)
    kit.tag(obj, "hero", collision="box", budget=5000,
            notes="Assembled moss and ivy ruin block: 3 courses of bevelled stone, moss heap on top, "
                  "ivy curtain down the front-right corner, moss and rocks at the foot. No VFX.")
    return obj


def build_moss_large(kit):
    a = new(kit.flintkit, "MossCushionLarge", 4101)
    heap(a, 0.0, [(-0.1, 0.05, 0.62, 1.2), (-0.8, -0.3, 0.5, 0.85), (0.7, -0.35, 0.52, 0.9), (-0.75, 0.42, 0.48, 0.8),
                  (0.75, 0.4, 0.5, 0.75), (0.05, -0.55, 0.42, 0.7)], sides=6)
    obj = done(a)
    kit.tag(obj, "part", collision="none", budget=300, notes="Moss Cushion (large): lumpy moss mound")
    return obj


def build_moss_small(kit):
    a = new(kit.flintkit, "MossCushionSmall", 4102)
    heap(a, 0.0, [(0.0, 0.1, 0.42, 0.8), (-0.38, -0.2, 0.32, 0.55), (0.38, -0.18, 0.32, 0.6),
                  (0.05, -0.35, 0.28, 0.45)], sides=6)
    obj = done(a)
    kit.tag(obj, "part", collision="none", budget=200, notes="Moss Cushion (small)")
    return obj


def build_ivy_flat(kit):
    a = new(kit.flintkit, "IvyClusterFlat", 4103)
    for u, z0, z1 in ((-0.6, 1.5, 0.95), (0.0, 1.6, 0.15), (0.6, 1.5, 0.9)):
        ivy_run(a, flat_surface, u, z0, z1, wig=0.12, step=0.42, size=(0.55, 0.75), back=True, dz=0.45)
    obj = done(a)
    kit.tag(obj, "part", collision="none", budget=600,
            notes="Ivy Cluster (flat): upright ivy mat facing -Y, lay it on any wall")
    return obj


def build_ivy_tendril(kit):
    a = new(kit.flintkit, "IvyTendril", 4104)
    pts = []
    for i in range(13):
        t = i / 12
        x = -1.0 + 2.0 * t
        z = 0.15 + 1.35 * t + 0.25 * math.sin(t * TAU * 1.1)
        pts.append(Vector((x, 0, z)))
    curl = [pts[-1] + Vector((0.15 * math.cos(a_), 0, 0.15 * math.sin(a_) + 0.15))
            for a_ in (-0.5, 0.6, 1.6, 2.6)]
    stem(a, pts + curl, r=0.06)
    path = [(p, Vector((0, -1, 0))) for p in pts]
    leaves_along(a, path, step=0.55, size=(0.38, 0.5), back=True, first=0.6, spread=(40, 80))
    obj = done(a)
    kit.tag(obj, "part", collision="none", budget=300,
            notes="Ivy Tendril (segment): curly stem with small leaves, faces -Y")
    return obj


def build_ivy_corner(kit):
    a = new(kit.flintkit, "IvyCornerPiece", 4105)
    surf = corner_surface()
    for u, z0, z1 in ((-0.95, 1.95, 0.9), (-0.3, 2.0, 0.5), (0.15, 2.0, 0.0), (0.8, 1.95, 0.9)):
        ivy_run(a, surf, u, z0, z1, wig=0.12, step=0.45, size=(0.55, 0.75), back=True, dz=0.5)
    obj = done(a)
    kit.tag(obj, "part", collision="none", budget=600,
            notes="Corner Piece (angled): ivy bent 90 degrees round an outside corner (front -Y, side +X)")
    return obj


def build_leaf_single(kit):
    a = new(kit.flintkit, "IvyLeafSingle", 4106)
    base = Vector((0, 0, 0.72))
    leaf(a, base, (0.15, 0, -1), (0, -1, 0), 0.72, lobes=5, tilt=0.12, back=True)
    a.tube_loop([base + Vector((0, 0.0, -0.1)), base + Vector((0.08, 0.02, 0.12)), base + Vector((0.12, 0.02, 0.24))],
                0.045, mat=BARK, rseg=4, closed=False)
    obj = done(a)
    kit.tag(obj, "part", collision="none", budget=60, notes="Single Ivy Leaf: one leaf with its stalk, faces -Y")
    return obj


def build_corner_wrap(kit):
    a = new(kit.flintkit, "CornerWrap", 4201)
    W, D = 4.4, 4.2
    H = stone_core(a, W, D, [1.45, 1.4, 1.35], target=(1.5, 1.45), bevel=0.14)
    bvh = BVHTree.FromBMesh(a.bm)
    surf = box_surface(bvh, W, D)
    Ht = H - 0.04
    heap(a, Ht, [(-0.9, 0.7, 0.85, 0.95), (0.6, 0.9, 0.8, 0.9), (-0.2, -0.4, 0.7, 0.75), (-1.4, -0.9, 0.55, 0.55),
                 (1.2, -0.2, 0.5, 0.5)])
    for u, z1 in ((W - 0.15, 0.0), (W - 0.7, 0.2), (W - 1.3, 0.9), (W + 0.5, 0.1), (W + 1.1, 1.0)):
        ivy_run(a, surf, u, H - 0.15, z1, lip=H)
    ivy_run(a, surf, 0.6, 1.4, 0.1, wig=0.15, top_leaves=0)
    cushion(a, (-1.2, -D / 2 - 0.45, 0), 1.2, 1.0, 0.65, n=3)
    cushion(a, (W / 2 + 0.25, 0.6, 0), 0.9, 1.1, 0.5, n=3)
    foot_rock(a, -2.2, -2.5, 0.7)
    foot_rock(a, 2.0, -2.6, 0.75)
    obj = done(a)
    kit.tag(obj, "variant", collision="box", budget=4000,
            notes="A. Corner Wrap: stone corner with moss on top and ivy wrapping the front-right corner")
    return obj


def build_wall_strip(kit):
    a = new(kit.flintkit, "WallStrip", 4202)
    W, D = 7.0, 1.9
    H = stone_core(a, W, D, [1.45, 1.45, 1.4], target=(1.75, 2.0), bevel=0.15)
    bvh = BVHTree.FromBMesh(a.bm)
    surf = box_surface(bvh, W, D)
    for u, z1 in ((1.2, 0.0), (1.75, 0.5), (4.3, 0.1), (4.85, 0.6)):
        ivy_run(a, surf, u, H - 0.15, z1, wig=0.18, lip=H)
    for x in (-1.9, 1.0):  # moss along the top edge where the ivy comes over
        cushion(a, (x, 0.1, H - 0.04), 1.2, 1.1, 0.5, n=3)
    for x, s in ((-2.6, 0.8), (-0.2, 1.3), (1.5, 0.9), (3.0, 0.7)):
        cushion(a, (x, -D / 2 - 0.3, 0), s, s * 0.8, s * 0.5, n=3, sides=6)
    foot_rock(a, -1.1, -D / 2 - 0.4, 0.55)
    obj = done(a)
    kit.tag(obj, "variant", collision="box", budget=4000,
            notes="B. Wall Strip: low stone wall section with two ivy strips hanging down the front")
    return obj


def build_rock_cap(kit):
    a = new(kit.flintkit, "RockCap", 4203)
    a.rock((6.3, 4.8, 3.4), loc=(0.15, 0.1, 0), mat=STONE, subdiv=2, rough=0.16, facets=9, sink=0.1)
    bvh = BVHTree.FromBMesh(a.bm)
    surf = radial_surface(bvh)

    def top(x, y):
        loc, _n, _i, _d = bvh.ray_cast(Vector((x, y, 20)), Vector((0, 0, -1)), 40)
        return loc.z - 0.15

    heap(a, top, [(-1.3, 0.3, 0.95, 0.95), (0.3, 0.6, 0.9, 0.9), (1.7, 0.4, 0.7, 0.7), (-0.6, -0.9, 0.75, 0.7),
                  (-2.2, -0.6, 0.6, 0.55), (0.9, -0.7, 0.5, 0.45)])
    for u, z1 in ((-105, 0.2), (-125, 0.1), (-145, 0.5), (-165, 1.2)):
        ivy_run(a, surf, u, 3.0, z1, wig=6, dz=0.35, top_leaves=1)
    cushion(a, (-2.6, -2.2, 0), 1.0, 0.9, 0.55, n=3, sides=6)
    cushion(a, (2.9, -1.0, 0), 0.8, 0.8, 0.45, n=3, sides=6)
    foot_rock(a, 1.0, -2.6, 0.9)
    obj = done(a)
    kit.tag(obj, "variant", collision="hull", budget=4000,
            notes="C. Rock Cap: faceted boulder capped with moss, ivy draping its front-left face")
    return obj


def build(kit):
    return [build_hero(kit), build_moss_large(kit), build_moss_small(kit), build_ivy_flat(kit),
            build_ivy_tendril(kit), build_ivy_corner(kit), build_leaf_single(kit),
            build_corner_wrap(kit), build_wall_strip(kit), build_rock_cap(kit)]
