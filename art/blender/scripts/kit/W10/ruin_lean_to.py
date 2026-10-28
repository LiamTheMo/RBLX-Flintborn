"""W10 row 4: Ruin Lean-To. A canvas camp built into a broken stone corner."""
import math

import bmesh

SUBJECT = "RuinLeanTo"
ROW = 4
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 135

PALETTE = {
    "w10_wood": ("#8A4A22", 0.85, 0, 0),
    "w10_canvas": ("#E3CFA0", 0.95, 0, 0),
    "w10_rope": ("#C48A38", 0.8, 0, 0),
    "w10_stone": ("#9A9498", 0.9, 0, 0),
    "w10_banner": ("#B8191F", 0.9, 0, 0),
    "w10_iron": ("#575B64", 0.5, 0.4, 0),
    "w10_lantern": ("#FFB022", 0.4, 0, 2),
    "w10_foliage": ("#3F8C24", 0.9, 0, 0),
    "w10_bedroll": ("#2C6A52", 0.95, 0, 0),
    "w10_snow": ("#F0F5FA", 0.95, 0, 0),
}

WOOD, CANVAS, ROPE, STONE = "w10_wood", "w10_canvas", "w10_rope", "w10_stone"
BANNER, IRON, LANTERN, LEAF = "w10_banner", "w10_iron", "w10_lantern", "w10_foliage"
BEDROLL, SNOW = "w10_bedroll", "w10_snow"

CH = 1.85          # course height
DEPTH = 3.2        # wall thickness
BACK_Y = 6.0       # back wall centre line (front face y 4.4, rear face y 7.6)
LEFT_X = -8.0      # left wall centre line (outer face x -9.6, inner face x -6.4)
BACK_FACE = BACK_Y - DEPTH / 2
BACK_H = [6, 6, 5, 5, 6, 5, 5, 6]   # 8 segments, x -9.6..7.0
LEFT_H = [6, 6, 4, 3, 3]            # 5 segments, y 4.4..-5.0
GAP = (3.4, 7.2)                    # left-wall arch along the wall (y 1.0..-2.8), 3 courses tall
POST_X, POST_Y, POST_R = 6.8, -5.8, 0.75
CAN_Y0, CAN_D = 4.3, 10.1


# ---------------------------------------------------------------- helpers
def wall(a, x0, y0, axis, length, heights, depth, ch=CH, skip=None, top_skip=0.18, cuts=()):
    """Running-bond block wall. axis 'x' runs +X from (x0, y0); 'y' runs -Y.
    cuts: (u0, u1, courses) openings clipped out of the lowest courses.
    Returns list of (loc, size, is_top) for each block placed."""
    rng = a.rng
    seg = length / len(heights)
    out = []

    def place(c, u0, u1):
        um = (u0 + u1) / 2
        hh = heights[min(int(um / seg), len(heights) - 1)]
        if hh <= c:
            return
        is_top = c == hh - 1
        if skip and skip(c, um):
            return
        if is_top and c > 1 and rng.random() < top_skip:
            return
        h = ch * rng.uniform(0.88, 0.97)
        d = depth * rng.uniform(0.88, 1.03)
        off = rng.uniform(-0.18, 0.18)
        z = c * ch + h / 2 + 0.02
        ln = u1 - u0 - 0.14
        if axis == "x":
            loc, size = (x0 + um, y0 + off, z), (ln, d, h)
        else:
            loc, size = (x0 + off, y0 - um, z), (d, ln, h)
        rot = (rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04), rng.uniform(-0.06, 0.06))
        a.stone_block(size, loc, rot, mat=STONE, bevel=min(size) * 0.2, jitter=min(size) * 0.07)
        out.append((loc, size, is_top))

    for c in range(max(heights)):
        u = -(c % 2) * 1.2
        while u < length:
            L = rng.uniform(2.1, 2.9)
            pieces = [(max(u, 0.0), min(u + L, length))]
            u += L
            for g0, g1, cmax in cuts:
                if c >= cmax:
                    continue
                nxt = []
                for p0, p1 in pieces:
                    if p1 <= g0 or p0 >= g1:
                        nxt.append((p0, p1))
                        continue
                    if g0 - p0 >= 0.6:
                        nxt.append((p0, g0))
                    if p1 - g1 >= 0.6:
                        nxt.append((g1, p1))
                pieces = nxt
            for p0, p1 in pieces:
                if p1 - p0 >= 0.7:
                    place(c, p0, p1)
    return out


def top_at(blocks, x, y):
    best = 0.0
    for loc, size, _ in blocks:
        if abs(loc[0] - x) <= size[0] / 2 + 0.1 and abs(loc[1] - y) <= size[1] / 2 + 0.1:
            best = max(best, loc[2] + size[2] / 2)
    return best or CH


def snow_caps(a, blocks):
    for loc, size, is_top in blocks:
        if is_top:
            a.box((size[0] + 0.25, size[1] + 0.25, 0.4), (loc[0], loc[1], loc[2] + size[2] / 2 + 0.12),
                  mat=SNOW, bevel=0.12, jitter=0.04)


def sheet(a, fn, nx, ny, thick, mat, mask=None):
    """Thin cloth slab over a grid; fn(u, v, i, j) -> (x, y, z) top point."""
    bm = a.bm
    present = lambda i, j: 0 <= i < nx and 0 <= j < ny and (mask is None or mask(i, j))
    tv, bv = {}, {}

    def vt(i, j):
        if (i, j) not in tv:
            x, y, z = fn(i / nx, j / ny, i, j)
            tv[(i, j)] = bm.verts.new((x, y, z))
            bv[(i, j)] = bm.verts.new((x, y, z - thick))
        return tv[(i, j)], bv[(i, j)]

    faces = []
    for i in range(nx):
        for j in range(ny):
            if not present(i, j):
                continue
            c = [(i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j)]
            t = [vt(*k)[0] for k in c]
            b = [vt(*k)[1] for k in c]
            faces.append(bm.faces.new(t))
            faces.append(bm.faces.new(list(reversed(b))))
            for (p, q), nb in (((0, 1), (i - 1, j)), ((1, 2), (i, j + 1)), ((2, 3), (i + 1, j)), ((3, 0), (i, j - 1))):
                if not present(*nb):
                    faces.append(bm.faces.new((t[q], t[p], b[p], b[q])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    verts = list(tv.values()) + list(bv.values())
    return a._finish(verts, mat)


def ivy(a, blocks, face, normal, length, strands=2, cap=True):
    """Small moss cap on the wall lip plus vine strands with leaves draping down a face.
    face: (x, y) point on the wall face; normal: outward face normal."""
    rng = a.rng
    fx, fy = face
    nx, ny = normal
    top = top_at(blocks, fx - nx * 0.8, fy - ny * 0.8)
    if cap:
        a.leaf_cluster(0.8, (fx - nx * 0.35, fy - ny * 0.35, top + 0.05), mat=LEAF, lobes=6, squash=0.5)
    side = (-ny, nx)
    for s in range(strands):
        so = (s - (strands - 1) / 2) * 1.25
        slen = min(length * (1.0 if s % 2 == 0 else 0.72), top - 0.3)
        bx, by = fx + nx * 0.1 + side[0] * so, fy + ny * 0.1 + side[1] * so
        steps = max(3, int(slen / 0.9))
        pts = []
        for k in range(steps + 1):
            w = math.sin(k * 1.3 + s * 2.1) * 0.3
            pts.append((bx + side[0] * w, by + side[1] * w, top + 0.05 - slen * k / steps))
        a.tube_loop(pts, 0.08, mat=LEAF, rseg=3, closed=False)
        for k, p in enumerate(pts[1:]):
            sg = 1 if k % 2 else -1
            lx = p[0] + side[0] * 0.32 * sg + nx * 0.1
            ly = p[1] + side[1] * 0.32 * sg + ny * 0.1
            sz = rng.uniform(0.8, 1.1) * (1.0 - 0.25 * k / steps)
            size = (0.1, sz, sz * 0.8) if abs(nx) > 0.5 else (sz, 0.1, sz * 0.8)
            ax = (0, rng.uniform(-0.6, 0.6), 0) if abs(ny) > 0.5 else (rng.uniform(-0.6, 0.6), 0, 0)
            a.box(size, (lx, ly, p[2]), ax, mat=LEAF)


def tuft(a, loc, n=6, h=1.0):
    rng = a.rng
    for k in range(n):
        ang = k / n * math.tau + rng.uniform(-0.3, 0.3)
        lean = rng.uniform(0.25, 0.55)
        a.cyl(0.13, 0.01, h * rng.uniform(0.7, 1.15), sides=3,
              loc=(loc[0] + math.cos(ang) * 0.14, loc[1] + math.sin(ang) * 0.14, 0),
              rot=(-math.sin(ang) * lean, math.cos(ang) * lean, 0), mat=LEAF, cap=False)


def flower(a, loc):
    x, y = loc
    a.cyl(0.05, 0.04, 0.6, sides=3, loc=(x, y, 0), mat=LEAF, cap=False)
    a.cyl(0.3, 0.22, 0.12, sides=5, loc=(x, y, 0.58), mat=CANVAS)


def rubble(a, loc, s=1.0):
    rng = a.rng
    a.stone_block((s * rng.uniform(0.9, 1.3), s * rng.uniform(0.8, 1.1), s * rng.uniform(0.6, 0.9)),
                  (loc[0], loc[1], s * 0.3), (0, rng.uniform(-0.15, 0.15), rng.uniform(0, 1.2)), mat=STONE)


def crate(a, loc, s=2.3, rz=0.0, snow=False):
    x, y, z = loc
    a.box((s, s, s), (x, y, z + s / 2), (0, 0, rz), mat=WOOD, bevel=0.05)
    for zz in (0.2, s - 0.2):
        a.box((s + 0.1, s + 0.1, 0.26), (x, y, z + zz), (0, 0, rz), mat=WOOD)
    for k in (-1, 1):
        cx, cy = math.cos(rz) * k * (s / 2 - 0.15), math.sin(rz) * k * (s / 2 - 0.15)
        a.box((0.26, s + 0.1, s), (x + cx, y + cy, z + s / 2), (0, 0, rz), mat=WOOD)
    if snow:
        a.box((s + 0.15, s + 0.15, 0.3), (x, y, z + s + 0.12), (0, 0, rz), mat=SNOW, bevel=0.1, jitter=0.03)


def barrel(a, loc, r=0.9, h=2.1, snow=False):
    x, y, z = loc
    a.cyl(r * 0.85, r, h / 2, sides=10, loc=(x, y, z), mat=WOOD)
    a.cyl(r, r * 0.85, h / 2, sides=10, loc=(x, y, z + h / 2), mat=WOOD)
    for zz in (h * 0.2, h * 0.8):
        a.torus(r * 0.96, 0.07, loc=(x, y, z + zz), mat=IRON, seg=10, rseg=3)
    if snow:
        a.cyl(r * 0.9, r * 0.6, 0.3, sides=8, loc=(x, y, z + h - 0.02), mat=SNOW)


def upright(a, x, y, h=9.0, collar=True, r=POST_R):
    a.cyl(r, r * 0.95, h - 1.6, sides=8, loc=(x, y, 0), mat=WOOD, jitter=0.02)
    a.cyl(r * 0.72, r * 0.72, 0.35, sides=8, loc=(x, y, h - 1.6), mat=WOOD)          # notch
    a.cyl(r * 0.95, r * 0.92, 1.48, sides=8, loc=(x, y, h - 1.6), mat=WOOD)
    a.cyl(r * 0.92, r * 0.72, 0.12, sides=8, loc=(x, y, h - 0.12), mat=ROPE)          # cut end
    if collar:
        a.rope_rings(r * 0.95, h - 2.05, count=3, thickness=0.17, loc=(x, y), mat=ROPE)


def bench(a, loc, length=3.4, rz=0.0):
    x, y, z = loc
    dx, dy = math.cos(rz) * length / 2, math.sin(rz) * length / 2
    a.beam((x - dx, y - dy, 0.8), (x + dx, y + dy, 0.8), 0.45, sides=7, mat=WOOD, end_mat=ROPE)
    for k in (-0.7, 0.7):
        a.box((0.55, 0.95, 0.55), (x + dx * k, y + dy * k, 0.28), (0, 0, rz), mat=WOOD)


def bedmat(a, loc, size=(3.8, 5.2, 0.3), roll=True, rz=0.0):
    x, y, z = loc
    a.box(size, (x, y, size[2] / 2), (0, 0, rz), mat=ROPE, bevel=0.05)
    for k in range(4):   # woven cream weft bands
        yy = y - size[1] * 0.38 + k * size[1] * 0.22
        a.box((size[0] * 0.96, size[1] * 0.08, 0.06), (x, yy, size[2] + 0.02), (0, 0, rz), mat=CANVAS)
    if roll:
        rr = 0.7
        a.cyl(rr, rr, size[0] * 0.9, sides=8, loc=(x - size[0] * 0.45, y + size[1] / 2 - 0.75, size[2] + rr),
              rot=(0, math.pi / 2, 0), mat=BEDROLL)
        for k in (-0.25, 0.25):
            a.torus(rr + 0.02, 0.07, loc=(x + size[0] * k, y + size[1] / 2 - 0.75, size[2] + rr),
                    rot=(0, math.pi / 2, 0), mat=ROPE, seg=8, rseg=3)


def banner(a, x, y, top=7.6):
    a.beam((x - 0.6, y, top + 0.05), (x + 2.7, y, top + 0.05), 0.1, sides=5, mat=WOOD, end_mat=ROPE)
    cx = x + 1.75
    pts = [(-0.8, 0), (-0.8, -4.0), (0, -3.4), (0.8, -4.0), (0.8, 0)]
    a.poly_prism(pts, 0.1, loc=(cx, y + 0.05, top), rot=(math.pi / 2, 0, 0), mat=BANNER)
    dia = [(0, 0.55), (-0.38, 0), (0, -0.55), (0.38, 0)]
    a.poly_prism(dia, 0.05, loc=(cx, y - 0.04, top - 1.6), rot=(math.pi / 2, 0, 0), mat=CANVAS)


def canopy_fn(back_z=7.9, front_z=7.3, x0=-6.0, w=12.0, y0=CAN_Y0, d=CAN_D, sag=0.6, belly=1.35, torn=False):
    """Sheet tied at the wall (v=0) and to the posts (v=1); sags into a V across and down the middle."""
    def fn(u, v, i, j):
        su = math.sin(math.pi * u)
        z = back_z + (front_z - back_z) * v - sag * su * (0.3 + 0.7 * v) - belly * su * math.sin(math.pi * v)
        y = y0 - d * v
        if torn and j >= 6:
            y += 0.35 * (i % 2)
            z -= 0.25 * ((i + 1) % 2)
        return (x0 + w * u, y, z)
    return fn


def canopy(a, snow=False):
    fn = canopy_fn()
    sheet(a, fn, 9, 7, 0.12, CANVAS)
    if snow:
        f2 = lambda u, v, i, j: (lambda p: (p[0], p[1], p[2] + 0.2))(fn(0.1 + 0.8 * u, 0.03 + 0.4 * v, i, j))
        sheet(a, f2, 6, 3, 0.12, SNOW, mask=lambda i, j: not (j == 2 and i in (0, 3, 5)))
    # ties: front corners to the posts, back corners to wall pegs
    for sx in (-1, 1):
        fx, fy, fz = fn(0 if sx < 0 else 1, 1, 0, 7)
        a.tube_loop([(fx, fy, fz), (sx * (POST_X - POST_R), POST_Y, fz + 0.1)], 0.08, mat=ROPE, rseg=4, closed=False)
        bx, by, bz = fn(0 if sx < 0 else 1, 0, 0, 0)
        a.beam((bx, BACK_FACE + 0.6, bz + 0.25), (bx, BACK_FACE - 0.5, bz + 0.25), 0.14, sides=5, mat=WOOD, end_mat=ROPE)
        a.torus(0.24, 0.07, loc=(bx, BACK_FACE - 0.25, bz + 0.1), rot=(math.pi / 2, 0, 0), mat=ROPE, seg=8, rseg=3)
    return fn


def wall_anchor(a, x, y, z, h=2.6, r=0.3):
    a.cyl(r, r * 0.9, h, sides=7, loc=(x, y, z), mat=WOOD)
    a.cyl(r * 0.9, r * 0.65, 0.1, sides=7, loc=(x, y, z + h), mat=ROPE)
    a.rope_rings(r, z + h * 0.62, count=2, thickness=0.11, loc=(x, y), mat=ROPE)
    a.torus(0.5, 0.08, loc=(x, y - r - 0.42, z + h * 0.45), rot=(math.pi / 2, 0, 0), mat=IRON, seg=10, rseg=3)
    a.torus(0.32, 0.07, loc=(x, y - r - 0.05, z + h * 0.62), rot=(math.pi / 2, 0, math.pi / 2), mat=ROPE, seg=8, rseg=3)


def ruin_walls(a, back_h=BACK_H, left_h=LEFT_H, top_skip=0.18):
    def lskip(c, um):
        return c == 3 and GAP[0] + 0.2 < um < GAP[1] + 0.6

    b = wall(a, LEFT_X - DEPTH / 2, BACK_Y, "x", 16.6, back_h, DEPTH, top_skip=top_skip)
    l = wall(a, LEFT_X, BACK_FACE, "y", 9.4, left_h, DEPTH, skip=lskip, top_skip=top_skip,
             cuts=[(GAP[0], GAP[1], 3)])
    # broken lintel: spans the back half of the gap, the front half is open to the sky
    lz = 3 * CH + CH * 0.47 + 0.02
    ly = BACK_FACE - 4.0
    size = (DEPTH * 0.95, 2.0, CH * 0.94)
    a.stone_block(size, (LEFT_X, ly, lz), (0, 0, 0.03), mat=STONE, bevel=0.35, jitter=0.12)
    l.append(((LEFT_X, ly, lz), size, True))
    return b + l


def finish_with(a, kit, sockets=()):
    """Clamp buried verts, compute the origin offset, finish and add sockets."""
    for v in a.bm.verts:
        if v.co.z < 0:
            v.co.z = 0.0
    xs = [v.co.x for v in a.bm.verts]
    ys = [v.co.y for v in a.bm.verts]
    off = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, 0.0)
    o = a.finish()
    for kind, loc, kw in sockets:
        kit.vfx.add(o, kind, (loc[0] - off[0], loc[1] - off[1], loc[2]), **kw)
    return o


RF = BACK_Y + DEPTH / 2          # back wall rear face
LO = LEFT_X - DEPTH / 2          # left wall outer face
HERO_IVY = [   # (face point, normal, drape length)
    ((-5.3, BACK_FACE), (0, -1), 6.0),
    ((4.6, BACK_FACE), (0, -1), 5.0),
    ((-9.0, -5.0), (0, -1), 4.0),         # left wall front end
    ((LO, 3.3), (-1, 0), 7.0),
    ((-3.2, RF), (0, 1), 7.0),
    ((7.0, 6.0), (1, 0), 6.0),            # back wall right end
    ((LO, -4.2), (-1, 0), 4.0),
    ((2.4, RF), (0, 1), 6.0),
]


def base_dressing(a, rubbles, tufts, flowers=(), mossy=()):
    for p, s in rubbles:
        rubble(a, p, s)
    for p in mossy:
        a.leaf_cluster(0.7, (p[0], p[1], 0.75), mat=LEAF, lobes=6, squash=0.5)
    for p, h in tufts:
        tuft(a, p, n=5, h=h)
    for p in flowers:
        flower(a, p)


# ---------------------------------------------------------------- assets
def build_hero(kit):
    a = kit.flintkit.Asset("RuinLeanTo", "W10 RuinLeanTo")
    blocks = ruin_walls(a)
    for face, n, ln in HERO_IVY:
        ivy(a, blocks, face, n, ln)
    upright(a, -POST_X, POST_Y)
    upright(a, POST_X, POST_Y)
    fn = canopy(a)
    tz = top_at(blocks, 0.0, BACK_Y)
    wall_anchor(a, 0.0, BACK_FACE - 0.3, tz - 1.2)
    cx, cy, cz = fn(0.5, 0, 5, 0)
    a.tube_loop([(0.0, BACK_FACE - 0.6, tz - 0.3), (cx, cy, cz)], 0.07, mat=ROPE, rseg=4, closed=False)
    banner(a, POST_X, POST_Y)
    bedmat(a, (-3.9, 0.8, 0), rz=0.05)
    crate(a, (2.2, 2.9, 0), rz=0.05)
    crate(a, (4.7, 3.0, 0), rz=-0.08)
    crate(a, (3.4, 2.9, 2.3), s=2.1, rz=0.3)
    barrel(a, (0.0, 3.1, 0))
    barrel(a, (5.0, -2.6, 0))
    bench(a, (1.0, -1.4, 0), rz=0.1)
    base_dressing(a,
                  [((-6.8, -7.0), 1.3), ((-4.0, -7.4), 0.9), ((1.5, -7.2), 1.0), ((8.0, -6.6), 1.2),
                   ((-10.2, -6.2), 1.1), ((4.5, -7.6), 0.8)],
                  [((-5.4, -6.8), 1.5), ((-1.0, -7.0), 1.3), ((3.2, -6.7), 1.4), ((8.8, -5.2), 1.5), ((-10.3, 1.0), 1.4)],
                  flowers=((-2.4, -7.3), (2.4, -7.6), (-8.6, -6.6)),
                  mossy=((-6.8, -7.0), (8.0, -6.6)))
    rubble(a, (-10.6, -0.4), 1.1)
    rubble(a, (-10.9, -2.2), 0.9)
    for p in ((6.8, -6.4),):
        a.leaf_cluster(0.8, (p[0], p[1], 0.45), mat=LEAF, lobes=6, squash=0.6)
    o = finish_with(a, kit)
    return kit.tag(o, "hero", collision="precise", budget=8000,
                   notes="Ruin lean-to camp: thick L stone wall with a lintelled gap, canopy on two uprights, "
                         "banner, bed, crates, barrels. Precise collision so players can walk under the canopy "
                         "and through the wall gap. No VFX.")


def build_snow(kit):
    a = kit.flintkit.Asset("RuinLeanToSnowShelter", "W10 RuinLeanTo")
    blocks = ruin_walls(a, top_skip=0.0)
    snow_caps(a, blocks)
    for face, n, ln in (HERO_IVY[0], HERO_IVY[3], HERO_IVY[4]):
        ivy(a, blocks, face, n, ln * 0.6, strands=1, cap=False)
    upright(a, -POST_X, POST_Y)
    upright(a, POST_X, POST_Y)
    for sx in (-1, 1):
        a.cyl(POST_R + 0.08, 0.3, 0.35, sides=8, loc=(sx * POST_X, POST_Y, 9.0), mat=SNOW)
    canopy(a, snow=True)
    bench(a, (-1.0, -0.8, 0), rz=-0.08)
    barrel(a, (2.6, 2.6, 0), snow=True)
    crate(a, (-4.2, 2.8, 0), s=2.1, rz=0.1, snow=True)
    crate(a, (4.6, 3.0, 0), s=2.1, rz=-0.1, snow=True)
    for p, s in (((-6.8, -7.0), 1.3), ((1.5, -7.2), 1.0), ((8.0, -6.6), 1.2)):
        rubble(a, p, s)
        a.cyl(s * 0.5, s * 0.3, 0.25, sides=7, loc=(p[0], p[1], s * 0.55), mat=SNOW)
    for p, r in (((-5.0, -6.6), 2.0), ((3.5, -6.6), 1.8), ((8.6, 1.0), 1.6), ((-10.6, -2.0), 1.5), ((0.0, 1.2), 2.4)):
        a.cyl(r, r * 0.75, 0.18, sides=8, loc=(p[0], p[1], 0), mat=SNOW)
    o = finish_with(a, kit)
    o["kit_shading_ok"] = "snow caps are a separate material (w10_snow) lying on tops, not painted lighting"
    return kit.tag(o, "variant", collision="precise", budget=6000,
                   notes="Snow Shelter: snow caps on wall tops, canopy, crates and barrel; bench and barrel under; no banner. No VFX.")


def build_trader(kit):
    a = kit.flintkit.Asset("RuinLeanToTraderStall", "W10 RuinLeanTo")
    blocks = ruin_walls(a)
    for face, n, ln in (HERO_IVY[0], HERO_IVY[3], HERO_IVY[4], HERO_IVY[5]):
        ivy(a, blocks, face, n, ln * 0.8, strands=1)
    upright(a, -POST_X, POST_Y)
    upright(a, POST_X, POST_Y)
    canopy(a)
    banner(a, POST_X, POST_Y)
    # table with goods
    tx, ty, th = 0.0, -1.6, 1.7
    a.plank((5.0, 1.8, 0.2), (tx, ty, th), mat=WOOD)
    for lx in (-2.2, 2.2):
        for ly in (-0.7, 0.7):
            a.box((0.24, 0.24, th - 0.1), (tx + lx, ty + ly, (th - 0.1) / 2), mat=WOOD)
    goods = [(-2.0, CANVAS, 0.5), (-1.3, BANNER, 0.7), (-0.6, ROPE, 0.45), (0.2, CANVAS, 0.8),
             (0.9, BANNER, 0.5), (1.6, ROPE, 0.65), (2.2, CANVAS, 0.45)]
    for k, (gx, m, gh) in enumerate(goods):
        gy = ty + (0.35 if k % 2 else -0.3)
        a.cyl(0.26, 0.21, gh, sides=7, loc=(tx + gx, gy, th + 0.1), mat=m)
        if gh > 0.6:
            a.cyl(0.08, 0.08, 0.3, sides=5, loc=(tx + gx, gy, th + 0.1 + gh), mat=m)
    a.box((0.9, 0.6, 0.45), (tx - 0.4, ty + 0.1, th + 0.32), (0, 0, 0.2), mat=WOOD)   # small goods box
    crate(a, (-4.0, 2.8, 0), s=2.1, rz=0.1)
    crate(a, (-4.2, 2.8, 2.1), s=1.7, rz=-0.2)
    crate(a, (4.4, 3.0, 0), s=2.1, rz=-0.1)
    barrel(a, (2.0, 3.1, 0))
    barrel(a, (-4.6, -2.6, 0))
    # lantern hung from the left upright
    lx, ly, lz = -POST_X + 1.6, POST_Y, 5.4
    a.beam((-POST_X, POST_Y, 6.3), (lx + 0.1, ly, 6.3), 0.09, sides=5, mat=IRON, end_mat=IRON)
    a.cyl(0.03, 0.03, 0.3, sides=4, loc=(lx, ly, 6.0), mat=IRON)
    a.cyl(0.32, 0.32, 0.1, sides=6, loc=(lx, ly, lz - 0.35), mat=IRON)
    a.cyl(0.24, 0.24, 0.6, sides=6, loc=(lx, ly, lz - 0.25), mat=LANTERN)
    a.cyl(0.34, 0.06, 0.3, sides=6, loc=(lx, ly, lz + 0.35), mat=IRON)
    for p, s in (((-6.8, -7.0), 1.2), ((2.5, -7.2), 1.0), ((8.0, -6.6), 1.1)):
        rubble(a, p, s)
    for p in ((-5.2, -6.6), (5.8, -6.8)):
        tuft(a, p, n=6, h=1.2)
    o = finish_with(a, kit, [("heat_glow", (lx, ly, lz + 0.05), dict(scale=0.5, color=["#FFB022", "#FF8A1E"]))])
    return kit.tag(o, "variant", collision="precise", budget=6000,
                   notes="Trader Stall: banner, goods table, crates, barrels. heat_glow socket at the lantern "
                         "hanging from the left upright (warm lantern light).")


def build_abandoned(kit):
    a = kit.flintkit.Asset("RuinLeanToAbandoned", "W10 RuinLeanTo")
    blocks = ruin_walls(a)
    for face, n, ln in HERO_IVY[:7]:
        ivy(a, blocks, face, n, ln * 1.15)
    upright(a, POST_X, POST_Y)
    a.cyl(POST_R, POST_R * 0.8, 1.2, sides=8, loc=(-POST_X, POST_Y, 0), mat=WOOD)       # broken stump

    rng = a.rng
    lens = [rng.randint(3, 6) for _ in range(8)]
    lens[7] = 6
    lens[6] = 6

    def fn(u, v, i, j):
        z = 7.9 + (7.3 - 7.9) * v - 0.8 * math.sin(math.pi * u) * v
        drop = (1 - u) ** 1.4 * max(0.0, v - 0.25) * 8.5
        y = CAN_Y0 - CAN_D * v + drop * 0.45
        if j >= 4 and i % 2:
            y += 0.4
        return (-6.0 + 12.0 * u, y, z - drop)

    mask = lambda i, j: j < lens[i] and not (j >= 2 and i in (1, 3, 5)) and not (j == 1 and i == 3)
    sheet(a, fn, 8, 6, 0.1, CANVAS, mask=mask)
    fx, fy, fz = fn(1, 1, 8, 6)
    a.tube_loop([(fx, fy, fz), (POST_X - POST_R, POST_Y, fz + 0.1)], 0.08, mat=ROPE, rseg=4, closed=False)
    base_dressing(a,
                  [((-6.8, -7.0), 1.3), ((-4.0, -7.4), 0.9), ((1.5, -7.2), 1.0), ((8.0, -6.6), 1.2),
                   ((-2.0, 0.8), 1.1), ((-10.2, -6.2), 1.1), ((-4.5, 2.8), 1.4)],
                  [((-5.4, -6.8), 1.6), ((-1.0, -7.0), 1.5), ((3.2, -6.7), 1.6), ((8.8, -5.2), 1.5),
                   ((0.5, 2.3), 1.4), ((-2.8, -2.2), 1.5), ((3.5, 0.8), 1.4)],
                  mossy=((-6.8, -7.0), (-4.5, 2.8)))
    o = finish_with(a, kit)
    return kit.tag(o, "variant", collision="precise", budget=6000,
                   notes="Abandoned: torn canvas strips, one standing upright plus a broken stump, heavy ivy, overgrowth, no goods. No VFX.")


def build_parts(kit):
    fk = kit.flintkit
    out = []

    a = fk.Asset("RuinLeanToWallBlocks", "W10 RuinLeanTo")
    blocks = wall(a, -4.0, 0.0, "x", 8.0, [4, 4, 3, 2], 3.0, ch=2.0, top_skip=0.0)
    ivy(a, blocks, (-2.6, -1.5), (0, -1), 4.0, strands=2)
    ivy(a, blocks, (1.2, -1.5), (0, -1), 2.6, strands=1, cap=False)
    out.append(kit.tag(finish_with(a, kit), "part", collision="box", budget=1500,
                       notes="Stepped chunk of broken wall blocks with ivy."))

    a = fk.Asset("RuinLeanToCanopy", "W10 RuinLeanTo")
    fn = canopy_fn(back_z=1.85, front_z=0.75, y0=4.5, d=9.0, sag=0.45, belly=0.5, torn=True)
    sheet(a, fn, 8, 7, 0.12, CANVAS, mask=lambda i, j: not (j == 6 and i in (1, 4, 6)))
    for u, v in ((0, 0), (1, 0), (0, 1), (1, 1)):
        x, y, z = fn(u, v * 6 / 7, 0, 0)
        a.torus(0.24, 0.07, loc=(x, y, z), mat=ROPE, seg=8, rseg=3)
        a.tube_loop([(x, y, z), (x * 1.06, y + (0.6 if v == 0 else -0.6), max(z - 0.6, 0.05))], 0.07, mat=ROPE,
                    rseg=4, closed=False)
    out.append(kit.tag(finish_with(a, kit), "part", collision="box", budget=1500,
                       notes="Sloped canvas canopy with rope tie corners and a torn lower edge."))

    a = fk.Asset("RuinLeanToUprightPost", "W10 RuinLeanTo")
    upright(a, 0, 0)
    out.append(kit.tag(finish_with(a, kit), "part", collision="box", budget=1500,
                       notes="9-stud upright with notch and rope collar; used twice."))

    a = fk.Asset("RuinLeanToWallAnchor", "W10 RuinLeanTo")
    wall_anchor(a, 0, 0, 0, h=4.0, r=0.55)
    out.append(kit.tag(finish_with(a, kit), "part", collision="box", budget=1500,
                       notes="Short anchor post with rope loop and iron ring that holds the canopy to the wall."))

    a = fk.Asset("RuinLeanToCrate", "W10 RuinLeanTo")
    crate(a, (0, 0, 0), s=2.0)
    out.append(kit.tag(finish_with(a, kit), "part", collision="box", budget=1500, notes="2x2x2 plank crate."))

    a = fk.Asset("RuinLeanToBedMat", "W10 RuinLeanTo")
    bedmat(a, (0, 0, 0), size=(5.0, 7.0, 0.4))
    out.append(kit.tag(finish_with(a, kit), "part", collision="none", budget=1500,
                       notes="Woven tan bed mat with a rolled green bedroll."))

    a = fk.Asset("RuinLeanToPeg", "W10 RuinLeanTo")
    a.cyl(0.02, 0.2, 0.3, sides=6, mat=WOOD, cap=False)
    a.cyl(0.2, 0.18, 0.75, sides=6, loc=(0, 0, 0.3), mat=WOOD)
    a.cyl(0.24, 0.2, 0.15, sides=6, loc=(0, 0, 1.05), mat=ROPE)
    a.torus(0.27, 0.07, loc=(0, 0, 0.85), mat=ROPE, seg=8, rseg=3)
    a.torus(0.3, 0.07, loc=(0.38, 0, 0.75), rot=(math.pi / 2, 0, 0), mat=ROPE, seg=8, rseg=3)
    out.append(kit.tag(finish_with(a, kit), "part", collision="none", budget=1500,
                       notes="Small wood peg with rope loop."))
    return out


def build(kit):
    out = [build_hero(kit)]
    out += build_parts(kit)
    out += [build_snow(kit), build_trader(kit), build_abandoned(kit)]
    return out
