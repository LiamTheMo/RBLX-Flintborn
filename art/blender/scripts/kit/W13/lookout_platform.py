"""W13 row 3: LookoutPlatform. Open roofless raised deck on four square posts with
X bracing, railings, a front staircase and stone footings, plus parts and variants."""
import math
from mathutils import Vector

SUBJECT = "LookoutPlatform"
ROW = 3
HERO_AZIMUTH = -40
SIDE_AZIMUTH = 90

PALETTE = {
    "w13_timber": ("#A9612C", 0.85, 0, 0),
    "w13_stone": ("#8A9199", 0.9, 0, 0),
    "w13_moss": ("#4C9A3C", 0.9, 0, 0),
}

T, S, M = "w13_timber", "w13_stone", "w13_moss"
POST_W = 1.6
CAP = (2.0, 2.0, 1.6)
RAIL_H = 3.5


# ---------------------------------------------------------------- helpers
def bx(a, size, loc, rot=(0, 0, 0), mat=T, bevel=0.0):
    return a.box(size, loc, rot, mat=mat, bevel=bevel)


def strut(a, p1, p2, w, h, mat=T, bevel=0.0):
    """Square-section beam from p1 to p2 (w across, h in the 'up' direction)."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    e = d.to_track_quat('Y', 'Z').to_euler()
    return a.box((w, d.length, h), tuple((p1 + p2) / 2), tuple(e), mat=mat, bevel=bevel)


def footing(a, x, y):
    bx(a, (2.8, 2.8, 1.8), (x, y, 0.9), mat=S, bevel=0.22)


def corner_post(a, x, y, z0, z1, cap=True):
    bx(a, (POST_W, POST_W, z1 - z0), (x, y, (z0 + z1) / 2), bevel=0.1)
    if cap:
        bx(a, CAP, (x, y, z1 + CAP[2] / 2), bevel=0.28)


def bolt(a, loc, normal):
    """Small bolt block proud of a face; normal is 'x', '-x', 'y', '-y'."""
    x, y, z = loc
    s = {"x": (0.3, 0.55, 0.55), "y": (0.55, 0.3, 0.55)}[normal[-1]]
    bx(a, s, (x, y, z), bevel=0.05)


def rail_post(a, x, y, z0, h=RAIL_H):
    bx(a, (0.8, 0.8, h - 0.35), (x, y, z0 + (h - 0.35) / 2))
    bx(a, (1.05, 1.05, 0.4), (x, y, z0 + h - 0.15), bevel=0.08)


def railing(a, p1, p2, z0, h=RAIL_H, end_posts=False, mid_post_over=6.5):
    """Axis-aligned railing from p1 to p2 (x, y) standing on z0."""
    (x1, y1), (x2, y2) = p1, p2
    along_x = abs(x2 - x1) >= abs(y2 - y1)
    L = abs(x2 - x1) if along_x else abs(y2 - y1)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

    def seg(size_along, cross, ht, z):
        size = (size_along, cross, ht) if along_x else (cross, size_along, ht)
        bx(a, size, (cx, cy, z))

    seg(L, 0.6, 0.55, z0 + h - 0.45)     # top rail
    seg(L, 0.4, 0.4, z0 + 1.55)         # mid rail
    n = max(1, int(round(L / 1.7)) - 1)
    for i in range(n):
        t = (i + 1) / (n + 1)
        x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        bx(a, (0.42, 0.42, h - 0.7), (x, y, z0 + (h - 0.7) / 2))
    if end_posts:
        rail_post(a, x1, y1, z0, h)
        rail_post(a, x2, y2, z0, h)
    if L > mid_post_over:
        rail_post(a, cx, cy, z0, h)


def deck(a, x0, x1, y0, y1, ztop, beam_h=0.9, plank_t=0.6, beams=True):
    """Plank deck, planks running left-right (along X), fascia beams beneath."""
    n = max(2, int(round((y1 - y0) / 1.2)))
    w = (y1 - y0) / n
    for i in range(n):
        y = y0 + w * (i + 0.5)
        bx(a, (x1 - x0, w - 0.1, plank_t), (0.5 * (x0 + x1), y, ztop - plank_t / 2), bevel=0.06)
    if beams:
        zb = ztop - plank_t - beam_h / 2
        bx(a, (x1 - x0, 0.7, beam_h), ((x0 + x1) / 2, y0 + 0.35, zb))
        bx(a, (x1 - x0, 0.7, beam_h), ((x0 + x1) / 2, y1 - 0.35, zb))
        bx(a, (0.7, y1 - y0 - 1.4, beam_h), (x0 + 0.35, (y0 + y1) / 2, zb))
        bx(a, (0.7, y1 - y0 - 1.4, beam_h), (x1 - 0.35, (y0 + y1) / 2, zb))


def xbrace(a, face, c, a0, a1, z0, z1, bolt_out=0.0):
    """Two crossing beams in a vertical plane. face 'x': plane x=c spanning y a0..a1;
    face 'y': plane y=c spanning x a0..a1."""
    if face == "x":
        P = lambda s, z, o=0.0: (c + o, s, z)
    else:
        P = lambda s, z, o=0.0: (s, c + o, z)
    strut(a, P(a0, z0, -0.05), P(a1, z1, -0.05), 0.8, 1.0)
    strut(a, P(a0, z1, 0.05), P(a1, z0, 0.05), 0.8, 1.0)
    mid = P((a0 + a1) / 2, (z0 + z1) / 2, bolt_out)
    bx(a, (1.1, 1.1, 1.1), mid, bevel=0.1)


def stairs(a, xc, y_top, z_top, n=10, rise=0.8, run=1.0, width=4.0, rails=True,
           stringers=True, treads=True, rail_sides=(-1, 1)):
    """Straight stairs descending toward -Y from (xc, y_top, z_top)."""
    for k in (range(1, n) if treads else ()):
        zt = z_top - k * rise
        yc = y_top - (k - 0.5) * run
        bx(a, (width, run + 0.05, 0.35), (xc, yc, zt - 0.175), bevel=0.04)
    y_bot = y_top - (n - 1) * run - 0.5
    slope = rise / run
    sx = width / 2 + 0.2
    # stringer centre line z(y) runs from top to bottom
    zc_top, zc_bot = z_top - 0.7, 0.42
    yc_top = y_top - 0.15
    if stringers:
        for s in (-1, 1):
            strut(a, (xc + s * sx, yc_top, zc_top), (xc + s * sx, y_bot, zc_bot), 0.4, 1.0)
    if not rails:
        return
    rz_top, rz_bot = z_top + RAIL_H - 0.45, 3.4
    for s in rail_sides:
        x = xc + s * (sx + 0.05)
        # bottom newel post and cap
        rail_post(a, x, y_bot + 0.2, 0.0, 3.9)
        strut(a, (x, y_top + 0.2, rz_top), (x, y_bot + 0.2, rz_bot), 0.45, 0.45)
        strut(a, (x, y_top + 0.2, rz_top - 1.6), (x, y_bot + 0.2, rz_bot - 1.6), 0.35, 0.35)
        for t in (0.25, 0.5, 0.75):
            y = y_top + (y_bot - y_top) * t
            zr = rz_top + (rz_bot - rz_top) * t
            zs = zc_top + (zc_bot - zc_top) * ((y - yc_top) / (y_bot - yc_top)) + 0.55
            if t == 0.5:
                bx(a, (0.6, 0.6, zr - zs + 0.4), (x, y, (zr + zs) / 2 + 0.2))
            else:
                bx(a, (0.28, 0.28, zr - zs), (x, y, (zr + zs) / 2))


def dressing(a, spots, seed=0):
    """Rubble stones and moss tufts at (x, y, kind) spots."""
    for i, (x, y, kind) in enumerate(spots):
        if kind == "r":
            r = (0.8 + 0.15 * (i % 3), 0.65 + 0.1 * (i % 2), 0.5)
            a.ico(r, (x, y, r[2] * 0.95), (0, 0, i * 0.7), mat=S, subdiv=1, jitter=0.05)
        else:
            a.leaf_cluster(0.75 + 0.1 * (i % 2), (x, y, 0.45), mat=M, lobes=5, squash=0.6,
                           floor=0.0)


def square_frame(a, posts, ztop, cap_top):
    """Footings, posts (with caps) for a list of (x, y, rises_to_rail)."""
    for x, y, tall in posts:
        footing(a, x, y)
        corner_post(a, x, y, 1.8, cap_top - CAP[2] if tall else ztop - 0.6, cap=tall)


# ---------------------------------------------------------------- assets
def build_hero(kit):
    fk = kit.flintkit
    a = fk.Asset("LookoutPlatform", "W13 LookoutPlatform")
    zt, cap_top = 8.0, 12.5
    p = 5.2
    square_frame(a, [(sx * p, sy * p, True) for sx in (-1, 1) for sy in (-1, 1)], zt, cap_top)
    deck(a, -6, 6, -6, 6, zt)
    # bolts at the deck beam joint on the outward faces of each post
    for sx in (-1, 1):
        for sy in (-1, 1):
            bolt(a, (sx * (p + 0.85), sy * p, zt - 1.0), "x")
            bolt(a, (sx * p, sy * (p + 0.85), zt - 1.0), "y")
    # X bracing on left, right and back faces
    xbrace(a, "x", -p, -4.4, 4.4, 2.3, 6.4, bolt_out=-0.45)
    xbrace(a, "x", p, -4.4, 4.4, 2.3, 6.4, bolt_out=0.45)
    xbrace(a, "y", p, -4.4, 4.4, 2.3, 6.4, bolt_out=0.45)
    # front low tie beam under the deck front (keeps the front open for the stairs)
    # railings
    railing(a, (-p, -4.4), (-p, 4.4), zt)
    railing(a, (p, -4.4), (p, 4.4), zt)
    railing(a, (-4.4, p), (4.4, p), zt)
    railing(a, (-4.4, -p), (-2.4, -p), zt)
    railing(a, (2.4, -p), (4.4, -p), zt)
    rail_post(a, -2.4, -p, zt)
    rail_post(a, 2.4, -p, zt)
    stairs(a, 0.0, -6.0, zt)
    dressing(a, [(-6.9, -3.6, "r"), (-6.3, -7.0, "m"), (6.6, -7.0, "r"), (7.0, -3.6, "m"),
                 (-7.0, 6.6, "r"), (3.2, -15.6, "r"), (-3.4, -14.8, "m"), (7.4, 4.0, "m")])
    o = a.finish()
    return kit.tag(o, "hero", collision="precise", budget=8000,
                   notes="Walkable deck at z=8 reached by the front stairs (10 rises of 0.8). No VFX.")


def build_parts(kit):
    fk = kit.flintkit
    out = []

    a = fk.Asset("LookoutRailing", "W13 LookoutRailing")
    railing(a, (-4.5, 0), (4.5, 0), 0.0, end_posts=True, mid_post_over=99)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Railing section 9 long."))

    a = fk.Asset("LookoutFloorPlanks", "W13 LookoutFloorPlanks")
    deck(a, -6, 6, -6, 6, 1.0, beam_h=0.4)
    out.append(kit.tag(a.finish(), "part", collision="precise", budget=1500, notes="Walkable plank floor 12x12."))

    a = fk.Asset("LookoutPost", "W13 LookoutPost")
    corner_post(a, 0, 0, 0.0, 7.4)
    bolt(a, (0, -0.85, 5.0), "y")
    bolt(a, (0.85, 0, 5.0), "x")
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Corner post with cube cap."))

    a = fk.Asset("LookoutXBrace", "W13 LookoutXBrace")
    xbrace(a, "y", 0.0, -3.6, 3.6, 0.45, 7.55, bolt_out=-0.3)
    out.append(kit.tag(a.finish(), "part", collision="precise", budget=1500, notes="Crossed X brace."))

    a = fk.Asset("LookoutCornerPostCap", "W13 LookoutCornerPostCap")
    bx(a, CAP, (0, 0, CAP[2] / 2), bevel=0.3)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Chamfered cube post cap."))

    a = fk.Asset("LookoutRailingPost", "W13 LookoutRailingPost")
    rail_post(a, 0, 0, 0.0)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Single railing post."))

    a = fk.Asset("LookoutStairRail", "W13 LookoutStairRail")
    stairs(a, -2.25, 4.5, 8.0, stringers=False, treads=False, rail_sides=(1,))
    # stringer under the rail so the part reads as a sloped stair side
    strut(a, (0.0, 4.35, 7.3), (0.0, -4.5 + 0.0, 0.42), 0.4, 1.0)
    out.append(kit.tag(a.finish(), "part", collision="precise", budget=1500, notes="Sloped stair rail with posts."))

    a = fk.Asset("LookoutStairs", "W13 LookoutStairs")
    stairs(a, 0.0, 5.0, 8.0, rails=False)
    out.append(kit.tag(a.finish(), "part", collision="precise", budget=1500, notes="10-rise walkable stairs."))

    a = fk.Asset("LookoutBaseStone", "W13 LookoutBaseStone")
    footing(a, 0, 0)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Stone footing block."))
    return out


def build_corner(kit):
    a = kit.flintkit.Asset("LookoutCornerPlatform", "W13 LookoutCornerPlatform")
    zt, cap_top, p = 8.0, 12.5, 4.2
    square_frame(a, [(sx * p, sy * p, True) for sx in (-1, 1) for sy in (-1, 1)], zt, cap_top)
    deck(a, -5, 5, -5, 5, zt)
    for face, c, o in (("x", -p, -0.45), ("x", p, 0.45), ("y", p, 0.45), ("y", -p, -0.45)):
        xbrace(a, face, c, -3.4, 3.4, 2.3, 6.4, bolt_out=o)
    # landing on the left, stairs descending along the left side toward the front
    xl0, xl1 = -9.7, -5.0
    deck(a, xl0, xl1, 1.0, 5.0, zt)
    for y in (1.6, 4.4):
        footing(a, -9.0, y)
        corner_post(a, -9.0, y, 1.8, zt - 0.6, cap=False)
    stairs(a, (xl0 + xl1) / 2 - 0.1, 1.0, zt, width=4.2)
    railing(a, (-p, -3.4), (-p, 0.6), zt)
    railing(a, (xl0 + 0.3, 1.6), (xl0 + 0.3, 5.0), zt, end_posts=True, mid_post_over=99)
    railing(a, (xl0 + 0.3, 4.7), (-5.0, 4.7), zt, mid_post_over=99)
    railing(a, (-3.4, p), (3.4, p), zt)
    railing(a, (p, -3.4), (p, 3.4), zt)
    railing(a, (-3.4, -p), (3.4, -p), zt)
    dressing(a, [(-6.2, -4.8, "r"), (5.9, -5.6, "m"), (6.0, 3.0, "r"), (-10.6, 3.0, "m"),
                 (-5.0, -9.6, "r")])
    return kit.tag(a.finish(), "variant", collision="precise", budget=8000,
                   notes="Corner platform: side landing and stairs on the left. No VFX.")


def build_wide(kit):
    a = kit.flintkit.Asset("LookoutWidePlatform", "W13 LookoutWidePlatform")
    zt, cap_top = 8.0, 12.5
    px, py = 9.2, 4.7
    posts = [(-px, -py, True), (px, -py, True), (-px, py, True), (px, py, True),
             (0.0, -py, False), (0.0, py, True)]
    square_frame(a, posts, zt, cap_top)
    deck(a, -10, 10, -5.5, 5.5, zt)
    for c, o in ((-py, -0.45), (py, 0.45)):
        xbrace(a, "y", c, -8.4, -0.8, 2.3, 6.4, bolt_out=o)
        xbrace(a, "y", c, 0.8, 8.4, 2.3, 6.4, bolt_out=o)
    railing(a, (-px, -3.9), (-px, 3.9), zt)
    railing(a, (px, -3.9), (px, 3.9), zt)
    railing(a, (-8.4, py), (-0.8, py), zt)
    railing(a, (0.8, py), (8.4, py), zt)
    railing(a, (-8.4, -py), (-2.4, -py), zt)
    railing(a, (2.4, -py), (8.4, -py), zt)
    rail_post(a, -2.4, -py, zt)
    rail_post(a, 2.4, -py, zt)
    stairs(a, 0.0, -5.5, zt)
    dressing(a, [(-11.0, -3.2, "r"), (-10.4, -6.4, "m"), (10.8, -6.0, "r"), (11.0, 3.0, "m"),
                 (4.0, -14.8, "r"), (-3.6, -13.5, "m")])
    return kit.tag(a.finish(), "variant", collision="precise", budget=8000,
                   notes="Wide 20x11 deck on six posts, front stairs. No VFX.")


def build_wall(kit):
    a = kit.flintkit.Asset("LookoutWallMounted", "W13 LookoutWallMounted")
    zt = 8.0
    # stone block wall at the back: 16 wide, 2.5 deep, courses of 1.4
    wy0, wy1 = 3.5, 6.0
    bw, ch = 16.0 / 6, 1.4
    for k in range(8):
        xs = [-8.0 + i * bw for i in range(7)] if k % 2 == 0 else \
             [-8.0] + [-8.0 + bw / 2 + i * bw for i in range(6)] + [8.0]
        for xa, xb in zip(xs[:-1], xs[1:]):
            bx(a, (xb - xa - 0.1, wy1 - wy0, ch - 0.1), ((xa + xb) / 2, (wy0 + wy1) / 2,
               k * ch + ch / 2), mat=S, bevel=0.14)
    # stepped irregular top along the right edge
    steps = [(8.0 - bw, 8.0, 8, 10), (8.0 - 1.6 * bw, 8.0 - bw * 0.6, 8, 9), (8.0 - 1.0, 8.0, 10, 10)]
    for xa, xb, k0, k1 in steps:
        for k in range(k0, k1):
            bx(a, (xb - xa - 0.1, wy1 - wy0, ch - 0.1), ((xa + xb) / 2, (wy0 + wy1) / 2,
               k * ch + ch / 2), mat=S, bevel=0.14)
    bx(a, (1.9, wy1 - wy0, 0.6), (7.0, (wy0 + wy1) / 2, 14.0 - 0.3), mat=S, bevel=0.12)
    # deck attached to the wall
    deck(a, -6, 6, -5.5, wy0, zt)
    bx(a, (12.0, 0.6, 1.0), (0, wy0 - 0.3, zt - 1.1))   # ledger against the wall
    for sx in (-1, 1):
        footing(a, sx * 5.2, -4.7)
        corner_post(a, sx * 5.2, -4.7, 1.8, 12.5 - CAP[2])
        bolt(a, (sx * 6.05, -4.7, zt - 1.0), "x")
        bolt(a, (sx * 5.2, -5.55, zt - 1.0), "y")
        # knee brace from the wall to the deck underside
        strut(a, (sx * 4.0, wy0 - 0.3, 3.8), (sx * 4.0, -0.2, zt - 1.3), 0.6, 0.75)
    xbrace(a, "y", -4.7, -4.4, 4.4, 2.3, 6.4, bolt_out=-0.45)
    railing(a, (-4.4, -4.7), (4.4, -4.7), zt)
    railing(a, (-5.2, -3.9), (-5.2, wy0), zt)
    railing(a, (5.2, -3.9), (5.2, wy0), zt)
    dressing(a, [(-7.0, -4.0, "r"), (6.6, -6.0, "m"), (-8.6, 2.6, "m"), (8.7, 2.8, "r"),
                 (-2.0, 2.6, "r")])
    o = a.finish()
    return kit.tag(o, "variant", collision="precise", budget=8000,
                   notes="Wall-mounted deck against a stone wall; no stairs (reached from the wall walk). No VFX.")


def build(kit):
    out = [build_hero(kit)]
    out += build_parts(kit)
    out += [build_corner(kit), build_wide(kit), build_wall(kit)]
    return out
