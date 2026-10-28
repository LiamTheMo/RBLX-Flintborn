"""W08 row 1: Footbridge - straight plank footbridge on square posts with rope rails.

The reference FRONT cell shows the long side and the SIDE cell the end, so the
bridge runs along X (fronts face -Y)."""
import math
import random

SUBJECT = "Footbridge"
ROW = 1
PALETTE = {
    "w08_wood": ("#A8582A", 0.88, 0, 0),
    "w08_pile_wood": ("#5C3420", 0.92, 0, 0),
    "w08_rope": ("#D4A857", 0.95, 0, 0),
    "w08_stone": ("#9CA2AA", 0.95, 0, 0),
    "w08_nail": ("#C48A3C", 0.5, 0.6, 0),
    "w08_banner": ("#B3202A", 0.85, 0, 0),
}
WOOD, ROPE, NAIL, STONE = "w08_wood", "w08_rope", "w08_nail", "w08_stone"

POST_W = 0.6
PLANK_T = 0.45
DECK_Z = 2.0          # deck top
TOP_EXTRA = 1.6       # post height above the deck
HERO_AZIMUTH = -26
ROPE_R = 0.19         # overall rope radius (two twisted strands)


def timber(a, p1, p2, w, h, mat=WOOD, bevel=0.03):
    """Square timber (w across, h tall) from p1 to p2."""
    dx, dy, dz = (p2[i] - p1[i] for i in range(3))
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    yaw = math.atan2(dy, dx)
    pitch = math.atan2(dz, math.hypot(dx, dy))
    c = tuple((p1[i] + p2[i]) / 2 for i in range(3))
    return a.box((L, w, h), loc=c, rot=(0, -pitch, yaw), mat=mat, bevel=bevel, jitter=0.0)


def nail_y(a, x, y, z, side=-1):
    """Round brass nail head on a face looking along side*Y."""
    a.cyl(0.1, 0.09, 0.06, sides=6, loc=(x, y + side * 0.0, z),
          rot=(-side * math.pi / 2, 0, 0), mat=NAIL)


def nail_x(a, x, y, z, side=-1):
    a.cyl(0.1, 0.09, 0.06, sides=6, loc=(x, y, z), rot=(0, side * math.pi / 2, 0), mat=NAIL)


def collar(a, x, y, z, count=2):
    """Rope collar wraps around a square post (low-poly rings)."""
    for i in range(count):
        a.torus(0.42, 0.14, loc=(x, y, z + i * 0.25), mat=ROPE, seg=8, rseg=4)


def square_post(a, x, y, height, z0=0.0, rot=(0, 0, 0), rings=True, side=-1, nails=(1.7,)):
    a.box((POST_W, POST_W, height), loc=(x, y, z0 + height / 2), rot=rot, mat=WOOD,
          bevel=0.05, jitter=0.0)
    if rot == (0, 0, 0):
        a.cyl(0.11, 0.1, 0.06, sides=6, loc=(x, y, z0 + height), mat=NAIL)
        if rings:
            collar(a, x, y, z0 + height - 0.65)
        for nz in nails:
            nail_y(a, x, y + side * POST_W / 2, nz, side)


def rope_line(a, pts, r=ROPE_R, pitch=1.0, per_turn=4, rseg=3):
    """Twisted two-strand cord along a polyline of centre points."""
    # resample by arc length
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(seg)
    n = max(4, int(total / pitch * per_turn))
    dense = []
    for k in range(n + 1):
        d = total * k / n
        i = 0
        while i < len(seg) - 1 and d > seg[i]:
            d -= seg[i]
            i += 1
        t = d / seg[i] if seg[i] > 1e-6 else 0
        dense.append(tuple(pts[i][j] + (pts[i + 1][j] - pts[i][j]) * t for j in range(3)))
    off, sr = r * 0.42, r * 0.62
    for strand in (0, 1):
        out = []
        for k, c in enumerate(dense):
            p0 = dense[max(0, k - 1)]
            p1 = dense[min(n, k + 1)]
            t = [p1[j] - p0[j] for j in range(3)]
            tl = math.sqrt(sum(v * v for v in t)) or 1
            t = [v / tl for v in t]
            up = (0, 0, 1) if abs(t[2]) < 0.9 else (1, 0, 0)
            n1 = [t[1] * up[2] - t[2] * up[1], t[2] * up[0] - t[0] * up[2], t[0] * up[1] - t[1] * up[0]]
            nl = math.sqrt(sum(v * v for v in n1)) or 1
            n1 = [v / nl for v in n1]
            n2 = [n1[1] * t[2] - n1[2] * t[1], n1[2] * t[0] - n1[0] * t[2], n1[0] * t[1] - n1[1] * t[0]]
            th = 2 * math.pi * (k / per_turn) + strand * math.pi
            out.append(tuple(c[j] + off * (math.cos(th) * n1[j] + math.sin(th) * n2[j])
                             for j in range(3)))
        a.tube_loop(out, sr, mat=ROPE, rseg=rseg, closed=False)


def swag(a, p1, p2, sag=0.6, n=10, r=ROPE_R):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t,
                    p1[2] + (p2[2] - p1[2]) * t - sag * 4 * t * (1 - t)))
    rope_line(a, pts, r)


def stones(a, spots, rng):
    for (x, y) in spots:
        s = rng.uniform(0.35, 0.6)
        a.rock((s * 1.2, s, s * 0.6), loc=(x, y, 0), rot=(0, 0, rng.uniform(0, 3)), mat=STONE,
               subdiv=1, facets=10, sink=0.1)


def bridge(fk, name, label, length, post_xs, arch=0.0, broken=False, seed=1, dressing=True):
    rng = random.Random(seed)
    a = fk.Asset(name, label)
    half = length / 2
    py = 2.35                     # post centre |y| (posts just outside the deck edge)
    deck_half = 2.05

    def deck_z(x):
        if arch <= 0:
            return DECK_Z
        return DECK_Z + arch * (1 - (x / half) ** 2)

    def slope(x):
        if arch <= 0:
            return 0.0
        return math.atan(-2 * arch * x / (half * half))

    # --- stringers (3) and side fascia beams, in segments when arched ---
    segs = 1 if arch <= 0 else 3
    for sy, w, h, top_off, mat_w in ((-1.45, 0.5, 0.6, PLANK_T, 0), (0.0, 0.5, 0.6, PLANK_T, 0),
                                     (1.45, 0.5, 0.6, PLANK_T, 0),
                                     (-2.18, 0.3, 0.75, -0.05, 1), (2.18, 0.3, 0.75, -0.05, 1)):
        x0, x1 = -half, half
        if broken and sy == 1.45:
            x1 = 0.6          # snapped stringer
        if broken and sy == -2.18:
            x1 = 0.9
        for s in range(segs):
            xa = x0 + (x1 - x0) * s / segs
            xb = x0 + (x1 - x0) * (s + 1) / segs
            za = deck_z(xa) - top_off - h / 2
            zb = deck_z(xb) - top_off - h / 2
            timber(a, (xa, sy, za), (xb, sy, zb), w, h, bevel=0.03 if mat_w else 0.0)
        if broken and x1 < half:
            # splintered stub angled down
            timber(a, (x1, sy, deck_z(x1) - top_off - h / 2),
                   (x1 + 0.9, sy, deck_z(x1) - top_off - h / 2 - 0.5), w * 0.8, h * 0.7)

    # --- deck planks ---
    pitch = 0.68
    n = int(round(length / pitch))
    pitch = length / n
    for i in range(n):
        x = -half + pitch * (i + 0.5)
        z = deck_z(x) - PLANK_T / 2 + rng.uniform(-0.03, 0.03)
        rx = rng.uniform(-0.025, 0.025)
        rz = rng.uniform(-0.035, 0.035)
        ry = slope(x)
        if broken:
            if x > 0.0 and i % 2 == 1:
                continue                    # missing planks
            if x > 1.2 and i % 4 != 0:
                continue
            if x > -0.5:
                rx += rng.uniform(-0.12, 0.12)
                rz += rng.uniform(-0.25, 0.25)
                ry += rng.uniform(-0.15, 0.15)
                z += rng.uniform(-0.05, 0.08)
        a.box((pitch - 0.07, 2 * deck_half + rng.uniform(-0.08, 0.08), PLANK_T), loc=(x, 0, z),
              rot=(rx, ry, rz), mat=WOOD, bevel=0.04, jitter=0.0)
    if broken:
        # dangling planks hanging off the broken end
        a.box((PLANK_T, 2.6, PLANK_T), loc=(1.5, -2.2, 1.45), rot=(1.2, 0, 0.2), mat=WOOD,
              bevel=0.04, jitter=0.0)
        a.box((PLANK_T, 2.2, PLANK_T), loc=(2.6, -0.4, 0.95), rot=(0.25, 0.9, 0.6), mat=WOOD,
              bevel=0.04, jitter=0.0)

    # --- posts, crossbeams, braces ---
    top_extra = TOP_EXTRA
    tops = {-1: [], 1: []}
    for xi, px in enumerate(post_xs):
        dz = deck_z(px)
        ph = dz + top_extra
        # crossbeam under the deck joining the post pair
        cb_z = dz - PLANK_T - 0.3
        timber(a, (px, -py, cb_z), (px, py, cb_z), 0.5, 0.5)
        for side in (-1, 1):
            y = side * py
            lean = broken and side == -1 and xi == len(post_xs) - 1
            if lean:
                ang = 0.2
                a.box((POST_W, POST_W, ph), loc=(px + math.sin(ang) * ph / 2, y,
                      math.cos(ang) * ph / 2 + 0.12), rot=(0, ang, 0), mat=WOOD, bevel=0.05,
                      jitter=0.0)
                tx, tz = px + math.sin(ang) * (ph - 0.65), math.cos(ang) * (ph - 0.65) + 0.12
                tops[side].append(None)
                a.torus(0.42, 0.14, loc=(tx, y, tz), rot=(0, ang, 0),
                        mat=ROPE, seg=8, rseg=4)
                continue
            square_post(a, px, y, ph, side=side, nails=(dz - 0.3, cb_z))
            tops[side].append((px, y, ph - 0.45))
            # nail on the crossbeam end grain is hidden; nail on post face above
            # knee braces in the post plane, towards the neighbouring posts
            for d in (-1, 1):
                nb = px + d * 1.5
                if abs(nb) > half - 0.2:
                    continue
                if broken and nb > 0.5:
                    continue
                timber(a, (px + d * 0.3, y * 0.97, 0.45),
                       (nb, y * 0.97, deck_z(nb) - 0.75), 0.32, 0.32)
        # X-brace at the bridge ends, below the crossbeam
        if xi in (0, len(post_xs) - 1) and not (broken and xi > 0):
            timber(a, (px, -py + 0.35, 0.18), (px, py - 0.35, cb_z), 0.3, 0.34)
            timber(a, (px, -py + 0.35, cb_z), (px, py - 0.35, 0.18), 0.3, 0.34)

    # --- rope swags between post tops ---
    for side in (-1, 1):
        t = tops[side]
        for p1, p2 in zip(t, t[1:]):
            if p1 is None or p2 is None:
                continue
            if arch > 0:
                # rail follows the arch: sample the deck curve
                pts = []
                for k in range(13):
                    u = k / 12
                    x = p1[0] + (p2[0] - p1[0]) * u
                    pts.append((x, p1[1], deck_z(x) + top_extra - 0.45 - 0.3 * math.sin(math.pi * u)))
                rope_line(a, pts)
            else:
                swag(a, p1, p2, sag=0.6 if abs(p2[0] - p1[0]) > 3 else 0.4)
        if broken and side == -1 and len(t) >= 2 and t[-1] is None:
            # rope torn off the leaning post: hangs and frays
            p = t[-2]
            pts = [p, (p[0] + 0.7, p[1] + 0.05, p[2] - 0.9), (p[0] + 1.1, p[1] + 0.1, p[2] - 2.0),
                   (p[0] + 1.2, p[1] + 0.15, p[2] - 2.6)]
            rope_line(a, pts)
            end = pts[-1]
            for k in range(3):
                q = (end[0] + 0.12 * (k - 1), end[1], end[2] - 0.35)
                a.tube_loop([end, q], 0.07, mat=ROPE, rseg=4, closed=False)

    if dressing:
        spots = [(post_xs[0] - 0.7, -py - 0.3), (post_xs[-1] + 0.6, py + 0.4),
                 (post_xs[-1] + 0.5, -py - 0.5)]
        stones(a, spots[:1] if arch > 0 else spots, rng)
    return a.finish()


def part_post(fk):
    a = fk.Asset("FootbridgePost", "W08 Footbridge Post")
    h = DECK_Z + TOP_EXTRA
    a.box((POST_W, POST_W, h), loc=(0, 0, h / 2), mat=WOOD, bevel=0.05, jitter=0.0)
    a.cyl(0.11, 0.1, 0.06, sides=6, loc=(0, 0, h), mat=NAIL)
    collar(a, 0, 0, h - 0.75)
    for z in (1.0, 1.7):
        nail_y(a, 0, -POST_W / 2, z, -1)
    return a.finish()


def part_rope(fk):
    a = fk.Asset("FootbridgeRopeSegment", "W08 Footbridge Rope Segment")
    p1, p2 = (-2.0, 0, 0.9), (2.0, 0, 0.9)
    swag(a, p1, p2, sag=0.7, n=12)
    return a.finish()


def part_plank(fk):
    a = fk.Asset("FootbridgePlank", "W08 Footbridge Plank")
    for i, dy in enumerate((-0.5, 0.0, 0.5)):
        a.box((4.2, PLANK_T, PLANK_T), loc=(0, dy, PLANK_T / 2), mat=WOOD,
              bevel=0.04, jitter=0.0)
    return a.finish()


def part_stringer(fk):
    a = fk.Asset("FootbridgeStringer", "W08 Footbridge Stringer")
    a.box((8.0, 0.5, 0.6), loc=(0, 0, 0.3), mat=WOOD, bevel=0.04, jitter=0.0)
    return a.finish()


def part_crossbeam(fk):
    a = fk.Asset("FootbridgeCrossbeam", "W08 Footbridge Crossbeam")
    a.box((1.4, 0.6, 0.6), loc=(0, 0, 0.3), mat=WOOD, bevel=0.05, jitter=0.0)
    nail_y(a, 0, -0.3, 0.3, -1)
    return a.finish()


def part_brace(fk):
    a = fk.Asset("FootbridgeBrace", "W08 Footbridge Brace")
    a.box((0.5, 0.5, 2.4), loc=(0, 0, 1.2), mat=WOOD, bevel=0.04, jitter=0.0)
    timber(a, (0.2, 0, 0.2), (1.6, 0, 1.6), 0.4, 0.4)
    nail_y(a, 0, -0.25, 0.4, -1)
    return a.finish()


def build(kit):
    fk = kit.flintkit
    out = []
    hero = bridge(fk, "Footbridge", "W08 Footbridge", 10.0, (-4.7, 0.0, 4.7), seed=8)
    out.append(kit.tag(hero, "hero", collision="precise", budget=5000,
                       notes="Walkable plank footbridge along X, deck top z~2.0, 4.1 wide walkable, 10 long. No VFX."))
    for fn in (part_post, part_rope, part_plank, part_stringer, part_crossbeam, part_brace):
        out.append(kit.tag(fn(fk), "part", collision="box", budget=1500, notes="Footbridge part"))
    v = bridge(fk, "FootbridgeShortSpan", "W08 Footbridge A. Short Span", 4.4, (-1.9, 1.9),
               seed=3)
    out.append(kit.tag(v, "variant", collision="precise", budget=3000, notes="A. Short Span"))
    v = bridge(fk, "FootbridgeArched", "W08 Footbridge B. Arched", 7.5, (-3.45, 3.45),
               arch=1.2, seed=5)
    out.append(kit.tag(v, "variant", collision="precise", budget=3000, notes="B. Arched"))
    v = bridge(fk, "FootbridgeBroken", "W08 Footbridge C. Broken", 7.0, (-3.2, 0.0, 3.2),
               broken=True, seed=7)
    out.append(kit.tag(v, "variant", collision="precise", budget=3000,
                       notes="C. Broken: snapped stringer, missing planks, leaning post, frayed rope"))
    return out
