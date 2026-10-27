"""W09 row 1: StonePath - sandstone flagstone path tiles with lush grassy edges."""
import math
import random

SUBJECT = "StonePath"
ROW = 1
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 90

PALETTE = {
    "w09_paver": ("#D8B488", 0.9, 0, 0),  # warm sandstone path pavers (row 1)
    "w09_boulder": ("#8C8E98", 0.9, 0, 0),  # cool grey rocks, footings, stray stones (all rows)
    "w09_grass": ("#5FA52A", 0.95, 0, 0),  # grass edge strip tops and turf tufts
    "w09_foliage": ("#3F9A2C", 0.9, 0, 0),  # leafy plant blades and bushes round the bases
    "w09_soil": ("#9A6430", 1, 0, 0),  # exposed earth under strips, path edges and tufts
    "w09_petal": ("#F7F3E6", 0.8, 0, 0),  # small white daisy petals
    "w09_flower_eye": ("#F0BE2A", 0.8, 0, 0),  # daisy centres
}

SOIL_TOP = 0.45   # top of the earth bed (thin skirt under the pavers)
GAP = 0.42        # soil seam between pavers
PAVER_H = 1.1


# ---------------------------------------------------------------- 2D helpers

def _clip(poly, n, c):
    """Keep the part of convex `poly` where dot(p, n) <= c."""
    out = []
    m = len(poly)
    for i in range(m):
        p, q = poly[i], poly[(i + 1) % m]
        dp = p[0] * n[0] + p[1] * n[1] - c
        dq = q[0] * n[0] + q[1] * n[1] - c
        if dp <= 0:
            out.append(p)
        if (dp < 0) != (dq < 0) and dp != dq:
            t = dp / (dp - dq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def _simplify(poly, min_edge=0.55):
    pts = list(poly)
    changed = True
    while changed and len(pts) > 4:
        changed = False
        for i in range(len(pts)):
            p, q = pts[i], pts[(i + 1) % len(pts)]
            if math.hypot(q[0] - p[0], q[1] - p[1]) < min_edge:
                mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
                j = (i + 1) % len(pts)
                pts[i] = mid
                pts.pop(j)
                changed = True
                break
    return pts


def _rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def voronoi(seeds, regions, gap=GAP):
    """Convex cells, one per seed, clipped to that seed's convex region and
    separated from neighbours by `gap`."""
    cells = []
    for i, s in enumerate(seeds):
        poly = list(regions[i])
        for j, t in enumerate(seeds):
            if i == j:
                continue
            dx, dy = t[0] - s[0], t[1] - s[1]
            d = math.hypot(dx, dy)
            if d < 1e-6:
                continue
            n = (dx / d, dy / d)
            mx, my = (s[0] + t[0]) / 2, (s[1] + t[1]) / 2
            poly = _clip(poly, n, mx * n[0] + my * n[1] - gap / 2)
            if len(poly) < 3:
                break
        if len(poly) >= 3:
            cells.append(_round_corners(_simplify(poly)))
    return cells


def _round_corners(poly, max_cut=1.1, sharp_deg=118):
    """Cut sharp corners so the pavers read as rounded 5-7 sided flagstones."""
    n = len(poly)
    out = []
    for i in range(n):
        p0, p, p1 = poly[i - 1], poly[i], poly[(i + 1) % n]
        ax, ay = p0[0] - p[0], p0[1] - p[1]
        bx, by = p1[0] - p[0], p1[1] - p[1]
        la, lb = math.hypot(ax, ay), math.hypot(bx, by)
        cosang = (ax * bx + ay * by) / (la * lb)
        if math.degrees(math.acos(max(-1, min(1, cosang)))) < sharp_deg:
            c = min(max_cut, 0.3 * la, 0.3 * lb)
            out.append((p[0] + ax / la * c, p[1] + ay / la * c))
            out.append((p[0] + bx / lb * c, p[1] + by / lb * c))
        else:
            out.append(p)
    return _simplify(out, 0.45)


def _shrink(poly, d):
    """Pull every point toward the centroid by distance d (convex polys)."""
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    out = []
    for x, y in poly:
        L = math.hypot(x - cx, y - cy)
        k = max(0.2, 1 - d / L) if L > 1e-6 else 1
        out.append((cx + (x - cx) * k, cy + (y - cy) * k))
    return out


# ---------------------------------------------------------------- 3D pieces

def _subdivide(pts, rng, push=(0.02, 0.16)):
    """Insert an outward-pushed midpoint on each edge (rounder, faceted outline)."""
    out = []
    n = len(pts)
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy)
        o = rng.uniform(*push)
        out.append(p)
        out.append(((p[0] + q[0]) / 2 + dy / L * o, (p[1] + q[1]) / 2 - dx / L * o))
    return out


def paver(a, pts, z0, h, rng, chamfer=0.4, tilt=0.14, bottom=False, crown=0.14,
          facet=0.08, sub=False, mat="w09_paver"):
    """Chunky flagstone: faceted side band (bulging waist), a chamfer ring and a
    softly faceted top (jittered inner ring + off-centre apex). `pts` CCW."""
    if sub:
        pts = _subdivide(pts, rng)
    bm = a.bm
    n = len(pts)
    cx = sum(p[0] for p in pts) / n
    cy = sum(p[1] for p in pts) / n
    ang = rng.uniform(0, 2 * math.pi)
    sx, sy = math.cos(ang) * tilt / 3.0, math.sin(ang) * tilt / 3.0
    dz = rng.uniform(-0.06, 0.06)

    def zt(x, y, base):
        return base + dz + sx * (x - cx) + sy * (y - cy)

    ch_z = min(chamfer * 0.7, h * 0.35)
    zw = z0 + (h - ch_z) * 0.5
    bot = [bm.verts.new((x, y, z0)) for x, y in pts]
    waist = []
    for x, y in pts:
        L = math.hypot(x - cx, y - cy) or 1.0
        o = rng.uniform(0.04, 0.12)
        waist.append(bm.verts.new((x + (x - cx) / L * o, y + (y - cy) / L * o, zw)))
    mid = [bm.verts.new((x, y, zt(x, y, z0 + h - ch_z) + rng.uniform(-0.03, 0.03)))
           for x, y in pts]
    inner = _shrink(pts, chamfer)
    top = [bm.verts.new((x, y, zt(x, y, z0 + h) + rng.uniform(-facet, facet)))
           for x, y in inner]
    ax, ay = cx + rng.uniform(-0.5, 0.5), cy + rng.uniform(-0.5, 0.5)
    ctr = bm.verts.new((ax, ay, zt(ax, ay, z0 + h) + crown))
    if bottom:
        bm.faces.new(list(reversed(bot)))
    for i in range(n):
        j = (i + 1) % n
        for lo, hi in ((bot, waist), (waist, mid), (mid, top)):
            bm.faces.new((lo[i], lo[j], hi[j]))
            bm.faces.new((lo[i], hi[j], hi[i]))
        bm.faces.new((top[i], top[j], ctr))
    verts = bot + waist + mid + top + [ctr]
    return a._finish(verts, mat, face_tint_var=0.05)


def blade(a, loc, h, lean, yaw, width=0.32, mat="w09_foliage"):
    v = a.cyl(width, 0.0, h, sides=4, mat=mat, cap=False)
    a.transform(v, loc=loc, rot=(lean, 0, yaw), scale=(1.0, 0.42, 1.0))
    return v


def tuft(a, loc, rng, n=8, hmin=1.6, hmax=2.5, out=None, mound=1.0, spread=0.7,
         width=(0.55, 0.8)):
    """Bushy clump of wide pointed leaf blades on a low turf mound. `out` =
    outward direction (radians) the clump fans toward, away from the walkway."""
    x, y, z = loc
    if mound:
        a.leaf_cluster(mound, (x, y, z + mound * 0.25), mat="w09_grass", lobes=6,
                       squash=0.55, floor=z)
    for k in range(n):
        th = 2 * math.pi * k / n + rng.uniform(-0.3, 0.3)
        if out is not None:
            th = out + (th - math.pi) * 0.8
        r = rng.uniform(0.1, spread)
        px, py = x + math.cos(th) * r, y + math.sin(th) * r
        lean = rng.uniform(0.2, 0.6)
        yaw = th - math.pi / 2
        blade(a, (px, py, z), rng.uniform(hmin, hmax), lean, yaw + math.pi,
              width=rng.uniform(*width))


def daisy(a, loc, rng, size=0.9):
    x, y, z = loc
    r = size / 2
    rot0 = rng.uniform(0, 2 * math.pi)
    for k in range(5):
        th = rot0 + 2 * math.pi * k / 5
        a.ico((r * 0.55, r * 0.26, 0.06), (x + math.cos(th) * r * 0.5, y + math.sin(th) * r * 0.5, z),
              (0, 0, th), mat="w09_petal", subdiv=1)
    a.ico((r * 0.28, r * 0.28, 0.1), (x, y, z + 0.04), mat="w09_flower_eye", subdiv=1)


def turf(a, loc, size, rng):
    """Low grass hummock on the soil rim."""
    v = a.ico((size[0] / 2, size[1] / 2, size[2]), (loc[0], loc[1], loc[2]), mat="w09_grass",
              subdiv=1, jitter=0.08)
    for p in v:
        if p.co.z < loc[2] - 0.05:
            p.co.z = loc[2] - 0.05


def soil_bed(a, outline, z=SOIL_TOP):
    """Earth bed: prism of the outline (no hidden bottom face)."""
    bm = a.bm
    bot = [bm.verts.new((x, y, 0.0)) for x, y in outline]
    top = [bm.verts.new((x, y, z)) for x, y in outline]
    bm.faces.new(top)
    n = len(outline)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    return a._finish(bot + top, "w09_soil")


def wobble_rect(x0, y0, x1, y1, rng, step=4.0, amp=0.25):
    """Rectangle outline with gently irregular edges (CCW)."""
    pts = []
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for i in range(4):
        p, q = corners[i], corners[(i + 1) % 4]
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        k = max(1, int(round(L / step)))
        for s in range(k):
            t = s / k
            x = p[0] + (q[0] - p[0]) * t
            y = p[1] + (q[1] - p[1]) * t
            if s:
                nx, ny = (q[1] - p[1]) / L, -(q[0] - p[0]) / L
                o = rng.uniform(-amp, amp)
                x, y = x + nx * o, y + ny * o
            pts.append((x, y))
    return pts


def lay_pavers(a, cells, rng, z0=SOIL_TOP, h=PAVER_H):
    for c in cells:
        paver(a, c, z0, h + rng.uniform(-0.06, 0.08), rng)


def _jit(seeds, rng, d=0.4):
    return [(x + rng.uniform(-d, d), y + rng.uniform(-d, d)) for x, y in seeds]


def _dress(a, rng, tufts, daisies, rocks, turfs=()):
    for x, y, out, n, big in tufts:
        if out == "c":
            out = math.atan2(y, x)
        tuft(a, (x, y, SOIL_TOP), rng, n=n + 3, hmin=2.1 if big else 1.7,
             hmax=3.0 if big else 2.5, out=out, mound=1.8 if big else 1.3,
             spread=1.25 if big else 0.95, width=(0.7, 1.0))
    for x, y in daisies:
        daisy(a, (x, y, SOIL_TOP + 1.45), rng, size=1.2)
    for (x, y), s in rocks:
        s *= 1.25
        a.rock((s * 1.1, s, s * 0.85), (x, y, SOIL_TOP - 0.15), (0, 0, rng.uniform(0, 3)),
               mat="w09_boulder", subdiv=1, facets=12)
    for x, y, sx, sy in turfs:
        turf(a, (x, y, SOIL_TOP), (sx * 1.3, sy, 0.8), rng)


# ---------------------------------------------------------------- assets

def build_hero(kit, fk):
    rng = random.Random(901)
    a = fk.Asset("StonePath", "W09 StonePath")
    soil_bed(a, wobble_rect(-8, -12, 8, 12, rng, amp=0.15))
    seeds = [(-4.6, -9.2), (1.2, -9.8), (5.9, -7.4), (-3.6, -3.6), (2.9, -2.6),
             (-5.3, 2.0), (0.3, 2.6), (5.6, 3.6), (-3.1, 7.8), (3.6, 8.9), (-6.0, 11.0)]
    seeds = _jit(seeds, rng, 0.3)
    region = _rect(-7.5, -11.5, 7.5, 11.5)
    lay_pavers(a, voronoi(seeds, [region] * len(seeds)), rng)
    P = math.pi
    tufts = [(-7.2, -11.0, "c", 10, True), (7.2, -11.0, "c", 10, True),
             (-7.2, 11.0, "c", 10, True), (7.3, 11.0, "c", 10, True),
             (-7.7, -5.6, P, 8, False), (-7.7, 0.2, P, 8, False), (-7.7, 5.8, P, 8, False),
             (7.7, -2.6, 0, 8, False), (7.7, 4.4, 0, 7, False)]
    daisies = [(-7.9, -10.0), (6.4, -11.6), (-8.1, 4.0), (8.1, -2.4), (7.9, 10.0), (-6.4, 11.7)]
    rocks = [((-4.6, 11.9), 1.3), ((7.9, 8.2), 1.2), ((7.9, -8.6), 1.4)]
    turfs = [(-7.8, 0.2, 1.4, 4.0), (-7.8, -7.8, 1.4, 3.2), (-7.8, 8.2, 1.4, 3.0),
             (7.8, 2.0, 1.4, 3.6), (7.8, -5.0, 1.4, 3.0)]
    _dress(a, rng, tufts, daisies, rocks, turfs)
    o = a.finish()
    return kit.tag(o, "hero", collision="precise", budget=6000,
                   notes="16 x 24 x 1.6 stud flagstone path slab (snaps to the 8-stud grid; "
                         "walk surface ~1.6 high). 11 sandstone pavers in an irregular "
                         "jigsaw on a thin earth bed (0.45) with soil seams; leaf tufts, "
                         "turf, daisies and rocks on the edges only.")


def build_part_paver(kit, fk, name, pts, seed):
    rng = random.Random(seed)
    a = fk.Asset(name, "W09 StonePath part")
    paver(a, pts, 0.0, 1.1, rng, chamfer=0.45, tilt=0.06, bottom=True, crown=0.16,
          facet=0.1, sub=True)
    o = a.finish()
    return kit.tag(o, "part", collision="hull", budget=1500,
                   notes="Loose sandstone paver for hand-laid paths.")


def build_grass_strip(kit, fk):
    rng = random.Random(907)
    a = fk.Asset("StonePathGrassEdgeStrip", "W09 StonePath part")
    R = (math.pi / 2, 0, 0)
    # soil profile in XZ with stepped-down ends, extruded along Y (2.5 deep)
    prof = [(-6.0, 0.0), (6.0, 0.0), (6.0, 0.35), (4.3, 0.35), (4.3, 1.1),
            (-4.3, 1.1), (-4.3, 0.35), (-6.0, 0.35)]
    a.poly_prism(prof, 2.5, loc=(0, 1.25, 0), rot=R, mat="w09_soil")

    def wavy_cap(x0, x1, zb, zt, depth, k):
        bot = []
        for i in range(k + 1):
            x = x0 + (x1 - x0) * i / k
            z = zb - (0.22 if i % 2 else 0.0) + rng.uniform(-0.04, 0.04)
            if i in (0, k):
                z = zb
            bot.append((x, z))
        top = [(x1 - (x1 - x0) * i / k, zt + rng.uniform(-0.05, 0.1)) for i in range(k + 1)]
        a.poly_prism(bot + top, depth, loc=(0, depth / 2, 0), rot=R, mat="w09_grass")

    wavy_cap(-4.55, 4.55, 1.05, 1.6, 2.9, 12)       # main cap, overhangs 0.2 all round
    wavy_cap(-6.15, -4.2, 0.32, 0.75, 2.8, 3)       # left step cap
    wavy_cap(4.2, 6.15, 0.32, 0.75, 2.8, 3)         # right step cap
    for x, n, hm in [(-3.7, 10, 3.0), (-0.6, 8, 2.4), (2.6, 10, 2.9)]:
        tuft(a, (x, 0.1, 1.55), rng, n=n, hmin=1.9, hmax=hm, mound=0, spread=0.8,
             width=(0.6, 0.85))
    daisy(a, (-1.9, -0.9, 1.95), rng, size=1.2)
    daisy(a, (3.8, -0.95, 1.95), rng, size=1.2)
    a.rock((2.3, 2.1, 2.2), (5.0, 0.2, 0.6), (0, 0, 0.4), mat="w09_boulder", subdiv=1,
           facets=12)
    o = a.finish()
    return kit.tag(o, "part", collision="box", budget=1500,
                   notes="12-stud grassy soil edge strip to border paths; wavy overhanging "
                         "grass cap, stepped ends tile.")


def build_straight(kit, fk):
    rng = random.Random(911)
    a = fk.Asset("StonePathStraight", "W09 StonePath variant")
    soil_bed(a, wobble_rect(-4, -12, 4, 12, rng, amp=0.15))
    seeds = _jit([(-1.6, -9.8), (1.9, -8.4), (-0.4, -4.6), (2.2, -1.0), (-1.9, 0.6),
                  (0.6, 4.8), (-1.8, 8.8), (2.0, 9.9)], rng, 0.25)
    region = _rect(-3.5, -11.5, 3.5, 11.5)
    lay_pavers(a, voronoi(seeds, [region] * len(seeds)), rng)
    P = math.pi
    tufts = [(-3.5, -11.0, "c", 9, True), (3.6, 11.0, "c", 9, True),
             (3.8, -6.0, 0, 7, False), (-3.8, -2.0, P, 7, False),
             (3.8, 3.6, 0, 7, False), (-3.8, 7.2, P, 7, False)]
    daisies = [(-4.2, -10.0), (4.2, 2.8), (-4.2, 7.9), (4.1, -6.8)]
    turfs = [(-3.9, -6.5, 1.1, 3.2), (3.9, -0.8, 1.1, 3.2), (-3.9, 3.0, 1.1, 3.0),
             (3.9, 7.5, 1.1, 3.0)]
    _dress(a, rng, tufts, daisies, [((3.7, -11.0), 1.0)], turfs)
    o = a.finish()
    return kit.tag(o, "variant", collision="precise", budget=3000,
                   notes="8 x 24 narrow straight path run, tiles end to end on the 8-stud grid.")


def _offset_polyline(pts, d):
    """Mitred offset of an open polyline to its left by d."""
    out = []
    for i, p in enumerate(pts):
        dirs = []
        if i > 0:
            dirs.append((p[0] - pts[i - 1][0], p[1] - pts[i - 1][1]))
        if i < len(pts) - 1:
            dirs.append((pts[i + 1][0] - p[0], pts[i + 1][1] - p[1]))
        ns = []
        for dx, dy in dirs:
            L = math.hypot(dx, dy)
            ns.append((-dy / L, dx / L))
        nx = sum(n[0] for n in ns)
        ny = sum(n[1] for n in ns)
        L = math.hypot(nx, ny)
        nx, ny = nx / L, ny / L
        cosh = nx * ns[0][0] + ny * ns[0][1]
        out.append((p[0] + nx * d / cosh, p[1] + ny * d / cosh))
    return out


CURVE_L, CURVE_A = 16.0, 4.4


def _cx(y):
    return CURVE_A * math.sin(math.pi * y / CURVE_L)


def _cframe(y):
    """Point, unit tangent and left normal of the S centreline at y."""
    dx = CURVE_A * math.pi / CURVE_L * math.cos(math.pi * y / CURVE_L)
    L = math.hypot(dx, 1.0)
    ux, uy = dx / L, 1.0 / L
    return (_cx(y), y), (ux, uy), (-uy, ux)


def build_curved(kit, fk):
    rng = random.Random(913)
    a = fk.Asset("StonePathCurved", "W09 StonePath variant")
    ys = [-CURVE_L + i * 2 * CURVE_L / 16 for i in range(17)]
    line = [(_cx(y), y) for y in ys]
    left = _offset_polyline(line, 4.4)
    right = _offset_polyline(line, -4.4)
    soil_bed(a, right + list(reversed(left)))
    seeds, regions = [], []
    k = 10
    for s in range(k):
        y = -CURVE_L + (s + 0.5) * 2 * CURVE_L / k
        (px, py), (ux, uy), (nx, ny) = _cframe(y)
        side = 1 if s % 2 else -1
        seeds.append((px + nx * 1.85 * side + ux * rng.uniform(-0.3, 0.3),
                      py + ny * 1.85 * side + uy * rng.uniform(-0.3, 0.3)))
        h, e = 3.55, 3.6
        reg = [(px - ux * e - nx * h, py - uy * e - ny * h), (px + ux * e - nx * h, py + uy * e - ny * h),
               (px + ux * e + nx * h, py + uy * e + ny * h), (px - ux * e + nx * h, py - uy * e + ny * h)]
        reg = _clip(reg, (0, 1), CURVE_L - 0.45)
        reg = _clip(reg, (0, -1), CURVE_L - 0.45)
        regions.append(reg)
    lay_pavers(a, voronoi(seeds, regions), rng)
    tufts, daisies = [], []
    P = math.pi
    for i, (y, side, n, big) in enumerate([(-15.2, 1, 9, True), (-15.0, -1, 7, False),
                                           (-8.0, 1, 8, False), (-3.0, -1, 7, False),
                                           (3.0, 1, 7, False), (8.0, -1, 8, False),
                                           (15.0, 1, 7, False), (15.2, -1, 9, True)]):
        (px, py), _, (nx, ny) = _cframe(y)
        x0, y0 = px + nx * 4.0 * side, py + ny * 4.0 * side
        out = math.atan2(ny * side, nx * side)
        tufts.append((x0, y0, out, n, big))
        if i % 2 == 0:
            daisies.append((x0 + nx * side * 0.5, y0 - 0.9))
    _dress(a, rng, tufts, daisies[:4], [((-3.8, -13.0), 1.0), ((4.0, 12.6), 0.9)])
    o = a.finish()
    return kit.tag(o, "variant", collision="precise", budget=3000,
                   notes="S-curved path, width 8, 32 studs long; both ends centred on x=0 "
                         "so it joins the straight run on the 8-stud grid.")


def build_junction(kit, fk):
    rng = random.Random(917)
    a = fk.Asset("StonePathJunction", "W09 StonePath variant")
    soil_bed(a, wobble_rect(-12, -12, 12, 12, rng, step=6.0, amp=0.15))
    seeds = [(0.0, 0.0)]
    for i in range(6):
        t = math.radians(15 + 60 * i)
        seeds.append((math.cos(t) * 6.2, math.sin(t) * 6.2))
    seeds += [(9.0, 9.0), (-9.0, 9.0), (-9.0, -9.0), (9.0, -9.0)]
    seeds = [seeds[0]] + _jit(seeds[1:], rng, 0.5)
    region = _rect(-11.5, -11.5, 11.5, 11.5)
    lay_pavers(a, voronoi(seeds, [region] * len(seeds)), rng)
    tufts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            tufts.append((sx * 10.7, sy * 10.7, "c", 10, True))
            tufts.append((sx * 6.0, sy * 11.6, math.atan2(sy, 0), 6, False))
    daisies = [(-11.2, -9.6), (9.6, -11.4), (11.3, 9.4), (-9.4, 11.4)]
    turfs = [(11.6, 0.0, 1.0, 4.0), (-11.6, 0.0, 1.0, 4.0), (0.0, 11.6, 4.0, 1.0),
             (0.0, -11.6, 4.0, 1.0)]
    _dress(a, rng, tufts, daisies, [((11.6, -8.6), 1.2), ((-8.6, 11.6), 1.0)], turfs)
    o = a.finish()
    return kit.tag(o, "variant", collision="precise", budget=3000,
                   notes="24 x 24 four-way path junction; 11 pavers radiating from a centre "
                         "stone; arms 8 wide meet the straight run.")


def build(kit):
    fk = kit.flintkit
    out = [build_hero(kit, fk)]
    # parts (CCW outlines)
    hexa = [(2.4, 0.0), (1.3, 2.15), (-1.2, 2.15), (-2.4, 0.1), (-1.2, -2.15), (1.2, -2.15)]
    hepta = [(2.4, -0.6), (2.2, 1.1), (0.9, 2.1), (-1.2, 2.05), (-2.4, 0.4), (-2.1, -1.3),
             (-0.6, -2.1), (0.9, -2.1), (1.2, -1.2)]  # notch at the +x,-y corner
    penta = [(2.65, -0.5), (1.8, 1.9), (-1.8, 1.9), (-2.65, -0.3), (0.2, -1.9)]
    out.append(build_part_paver(kit, fk, "StonePaverA", hexa, 921))
    out.append(build_part_paver(kit, fk, "StonePaverB", hepta, 922))
    out.append(build_part_paver(kit, fk, "StonePaverC", penta, 923))
    out.append(build_grass_strip(kit, fk))
    out.append(build_straight(kit, fk))
    out.append(build_curved(kit, fk))
    out.append(build_junction(kit, fk))
    return out
