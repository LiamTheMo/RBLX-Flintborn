"""W15 row 1: MineSupport - heavy timber portal in a rock cliff (mine tunnel mouth)."""
import math

SUBJECT = "MineSupport"
ROW = 1
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 90

PALETTE = {
    "w15_timber": ("#A9662B", 0.85, 0, 0),
    "w15_iron": ("#454B66", 0.5, 0.4, 0),
    "w15_rock": ("#8E8E96", 0.95, 0, 0),
    "w15_sand": ("#D4B98E", 1, 0, 0),
    "w15_foliage": ("#3E9A22", 0.9, 0, 0),
    "w15_banner": ("#C8161F", 0.8, 0, 0),
    "w15_lantern_glow": ("#FFB347", 0.4, 0, 1.5),
}

T, IRON, ROCK, SAND, LEAF, BAN, GLOW = ("w15_timber", "w15_iron", "w15_rock", "w15_sand",
                                        "w15_foliage", "w15_banner", "w15_lantern_glow")

GLOW_EMIT = [{"name": "Heat", "texture": "glow_soft", "color": ["#FFB347", "#FF9A30"],
              "size": [0.8, 1.1], "transparency": [0.55, 1.0], "lifetime": [0.8, 1.2],
              "rate": 2, "speed": [0.0, 0.2], "spread": 5, "light_emission": 1.0}]
GLOW_LIGHT = {"color": "#FFA040", "brightness": 0.8, "range": 9, "flicker": True}


# ---------------------------------------------------------------- helpers
def xz_beam(a, p1, p2, w, y=0.0, d=None, mat=T):
    """Square beam between two (x, z) points in the plane y."""
    dx, dz = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dx, dz)
    c = ((p1[0] + p2[0]) / 2, y, (p1[1] + p2[1]) / 2)
    a.box((L, d or w, w), loc=c, rot=(0, -math.atan2(dz, dx), 0), mat=mat, bevel=0.06)


def yz_beam(a, p1, p2, w, x=0.0, mat=T):
    """Square beam between two (y, z) points in the plane x."""
    dy, dz = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dy, dz)
    c = (x, (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    a.box((w, L, w), loc=c, rot=(math.atan2(dz, dy), 0, 0), mat=mat, bevel=0.06)


def bolts(a, pts, y):
    for (x, z) in pts:
        a.box((0.36, 0.2, 0.36), loc=(x, y, z), mat=IRON)


def plate(a, x, z, w, h, y, nb=2):
    """Iron plate on a front face (y = face) with bolt heads."""
    a.box((w, 0.12, h), loc=(x, y - 0.06, z), mat=IRON)
    if nb == 2:
        off = (max(w, h) / 2 - 0.32)
        pts = [(x - off, z), (x + off, z)] if w >= h else [(x, z - off), (x, z + off)]
    else:
        pts = [(x, z)]
    bolts(a, pts, y - 0.18)


def lantern(a, x, y, z, arm=0.7, s=1.0, side=0):
    """Hanging lantern; (x, y, z) = glass centre; arm reaches back +Y (or along X by
    `side` * arm) to the mount. arm=0: hangs from a beam just above."""
    if arm > 0 and side:
        a.box((arm, 0.14 * s, 0.14 * s), loc=(x + side * arm / 2, y, z + 0.95 * s), mat=IRON)
    elif arm > 0:
        a.box((0.14 * s, arm, 0.14 * s), loc=(x, y + arm / 2, z + 0.95 * s), mat=IRON)
    else:
        a.box((0.08, 0.08, 0.8 * s), loc=(x, y, z + 1.3 * s), mat=IRON)
    a.box((0.08, 0.08, 0.3 * s), loc=(x, y, z + 0.78 * s), mat=IRON)                   # hook
    a.cyl(0.5 * s, 0.12 * s, 0.32 * s, sides=4, loc=(x, y, z + 0.42 * s),
          rot=(0, 0, math.pi / 4), mat=IRON)                                         # roof
    a.box((0.62 * s, 0.62 * s, 0.75 * s), loc=(x, y, z), mat=GLOW)                     # glass
    a.box((0.8 * s, 0.8 * s, 0.14 * s), loc=(x, y, z - 0.44 * s), mat=IRON)            # base
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.box((0.09, 0.09, 0.78 * s), loc=(x + sx * 0.33 * s, y + sy * 0.33 * s, z), mat=IRON)
    return (x, y, z)


def banner(a, x, ztop, w, h, y, torn=False):
    """Red banner hung from an iron rod, pointed bottom, pale diamond emblem."""
    a.cyl(0.07, 0.07, w + 0.5, sides=5, loc=(x - (w + 0.5) / 2, y + 0.05, ztop),
          rot=(0, math.pi / 2, 0), mat=IRON)
    b = ztop - h
    if torn:
        pts = [(x - w / 2, b + 1.2), (x - w * 0.15, b + 0.5), (x + w * 0.05, b + 1.0),
               (x + w / 2, b + 0.3), (x + w / 2, ztop), (x - w / 2, ztop)]
    else:
        pts = [(x - w / 2, b + 0.7), (x, b), (x + w / 2, b + 0.7), (x + w / 2, ztop), (x - w / 2, ztop)]
    a.poly_prism(pts, 0.1, loc=(0, y, 0), rot=(math.pi / 2, 0, 0), mat=BAN)
    zc = ztop - h * 0.45
    dw, dh = w * 0.28, w * 0.42
    a.poly_prism([(x, zc - dh), (x + dw, zc), (x, zc + dh), (x - dw, zc)], 0.05,
                 loc=(0, y - 0.1, 0), rot=(math.pi / 2, 0, 0), mat=SAND)


def sand_patch(a, rx, y0, y1, cx=0.0):
    pts = []
    n = 12
    cy, ry = (y0 + y1) / 2, (y1 - y0) / 2
    for i in range(n):
        t = 2 * math.pi * i / n
        k = 1.0 + 0.08 * math.sin(3 * t + 1.0)
        pts.append((cx + rx * k * math.cos(t), cy + ry * k * math.sin(t)))
    a.poly_prism(pts, 0.12, loc=(0, 0, 0), mat=SAND)


def rails(a, y0, y1, gauge=2.4, tie_step=1.5):
    y = y0 + 0.4
    while y < y1:
        a.box((gauge + 1.4, 0.6, 0.22), loc=(0, y, 0.23), mat=T)
        y += tie_step
    for sx in (-1, 1):
        a.box((0.24, y1 - y0, 0.3), loc=(sx * gauge / 2, (y0 + y1) / 2, 0.49), mat=IRON)


def R(a, size, x, y, zbase, rz=0.0, small=False):
    """Faceted grey boulder sitting on zbase (rock() takes the base height)."""
    a.rock(size, loc=(x, y, zbase), rot=(0, 0, rz), mat=ROCK,
           subdiv=1 if small else 2, facets=10 if small else 16)


def tuft(a, r, loc, floor=0.0):
    a.leaf_cluster(r * 1.25, loc=loc, mat=LEAF, lobes=7, squash=0.7, floor=floor)


def portal(a, hw, post_w, lintel_z, lintel_len, y=0.0, depth=5.0, braces=True,
           double=False, collar=True, brackets=True, rear=True, drop=3.6, reach=None, bw=1.2):
    """Post-lintel-collar-brace timber portal. hw = post centre x. Each side gets a long
    front brace (post -> lintel) and a second brace on the inner frame set at y+depth."""
    foot = 1.2
    reach = reach or drop
    for sx in (-1, 1):
        x = sx * hw
        a.box((post_w + 0.9, post_w + 0.9, foot), loc=(x, y, foot / 2), mat=ROCK, bevel=0.15)
        a.box((post_w, post_w, lintel_z - foot), loc=(x, y, (lintel_z + foot) / 2), mat=T, bevel=0.06)
        if collar:
            a.box((post_w + 0.5, post_w + 0.5, 1.3), loc=(x, y, lintel_z - 0.65), mat=T, bevel=0.08)
            # iron strap round the collar
            a.box((post_w + 0.6, post_w + 0.6, 0.24), loc=(x, y, lintel_z - 0.9), mat=IRON)
        inner = hw - post_w / 2
        if braces:
            sets = [(y - post_w / 2 + bw / 2, bw)] + ([(y + depth, bw * 0.85)] if rear else [])
            for (by, bd) in sets:
                xz_beam(a, (sx * (inner + 0.3), lintel_z - drop), (sx * (inner - reach), lintel_z + 0.3),
                        bd, y=by, d=bd)
            if brackets:
                fy = y - post_w / 2
                plate(a, sx * (inner - reach + 0.5), lintel_z + 0.55, 1.4, 0.9, fy - 0.02)
                plate(a, sx * (inner - 0.1), lintel_z - drop + 0.3, 0.9, 1.4, fy - 0.02)
        if rear:
            # inner frame set: rear post + side tie and side brace
            a.box((post_w * 0.9, post_w * 0.9, lintel_z - foot), loc=(x, y + depth, (lintel_z + foot) / 2), mat=T)
            a.box((post_w + 0.6, post_w + 0.6, foot), loc=(x, y + depth, foot / 2), mat=ROCK, bevel=0.15)
            yz_beam(a, (y, lintel_z + 0.6), (y + depth, lintel_z + 0.6), 1.2, x=x)
            yz_beam(a, (y + 0.6, lintel_z - 4.5), (y + depth - 0.6, lintel_z - 0.3), 1.0, x=x)
            yz_beam(a, (y + 0.6, lintel_z - 0.3), (y + depth - 0.6, lintel_z - 4.5), 0.9, x=x + sx * 0.12)
            if brackets:
                for yy in (y + 0.9, y + depth - 0.9):
                    a.box((0.12, 1.2, 1.2), loc=(x + sx * (post_w / 2 + 0.06), yy, lintel_z + 0.6), mat=IRON)
    lh = max(1.6, post_w * 0.9)
    a.box((lintel_len, post_w + 0.1, lh), loc=(0, y, lintel_z + lh / 2), mat=T, bevel=0.07)
    # end caps standing on the lintel above the posts
    for sx in ((-1, 1) if not double else ()):
        a.box((post_w + 0.3, post_w + 0.3, 0.9), loc=(sx * hw, y, lintel_z + lh + 0.45), mat=T, bevel=0.07)
    top = lintel_z + lh
    if double:
        a.box((lintel_len - 1.5, post_w, 1.2), loc=(0, y, top + 0.6), mat=T, bevel=0.07)
        top += 1.2
    if rear:
        a.box((lintel_len - 1.0, 1.0, 1.1), loc=(0, y + depth, lintel_z + 0.55), mat=T)
    if brackets:
        fy = y - (post_w + 0.1) / 2
        for sx in (-1, 1):
            # L bracket: lintel face + post face
            plate(a, sx * hw, lintel_z + lh / 2, 1.9, 1.0, fy)
            plate(a, sx * hw, lintel_z - 2.3, 1.0, 1.4, y - post_w / 2)
            plate(a, sx * (lintel_len / 2 - 0.6), lintel_z + lh / 2, 0.9, 1.3, fy)
    return top


def finish(kit, a, role, budget, collision, notes, glows):
    o = a.finish()
    for g in glows:
        kit.vfx.add(o, "heat_glow", g, scale=0.6, emitters=GLOW_EMIT, light=GLOW_LIGHT)
    return kit.tag(o, role, collision=collision, budget=budget, notes=notes)


# ---------------------------------------------------------------- assets
def hero(kit):
    a = kit.flintkit.Asset("MineSupport", "W15 MineSupport", tint_var=0.05, seed=1501)
    sand_patch(a, 9.5, -7.5, 8.0)
    rails(a, -7.5, 10.5)
    # rock massif (6 big rocks): two flanks, two roof rocks, crown, back wall
    R(a, (6.4, 9.0, 11.5), -8.8, 7.2, 0.0, 0.15)
    R(a, (6.4, 9.0, 10.5), 8.8, 7.2, 0.0, -0.2)
    R(a, (13.0, 11.0, 3.0), 0.0, 7.5, 13.4, 0.0)
    R(a, (8.5, 7.0, 6.5), -4.6, 6.0, 14.4, 0.3)
    R(a, (8.0, 7.0, 6.0), 4.8, 6.0, 14.6, -0.3)
    R(a, (7.0, 6.0, 5.0), 0.0, 9.0, 16.2, 0.6)
    R(a, (14.0, 7.5, 15.0), 0.0, 13.5, 0.0, 0.0)
    for (x, y, s) in ((-7.8, -2.6, 1.3), (8.0, -3.0, 1.1), (-4.4, -6.2, 0.7), (4.6, -6.6, 0.6)):
        R(a, (s * 1.3, s, s * 0.8), x, y, 0.0, x, small=True)
    portal(a, hw=6.0, post_w=2.0, lintel_z=13.5, lintel_len=16.0, depth=3.8, drop=5.0, reach=4.0, bw=1.35)
    glows = [lantern(a, -6.0, -2.6, 7.2, arm=1.6, s=2.5), lantern(a, 6.0, -2.6, 7.2, arm=1.6, s=2.5),
             lantern(a, -2.0, 3.8, 11.2, arm=0.0, s=1.5)]
    banner(a, 8.0, 13.4, 1.8, 5.0, -1.25)
    for (r, loc) in ((1.7, (-6.6, -2.6, 0.5)), (1.5, (-10.2, 0.6, 0.4)), (1.6, (6.8, -2.4, 0.5)),
                     (1.4, (10.4, 1.0, 0.4)), (1.0, (-3.6, -3.0, 0.4)), (1.0, (4.2, -3.4, 0.4)),
                     (1.4, (6.4, 3.0, 19.8)), (1.1, (8.8, 3.0, 17.0)), (1.0, (-9.4, 2.8, 9.6))):
        tuft(a, r, loc, floor=0.0 if loc[2] < 1 else None)
    return finish(kit, a, "hero", 8000, "precise",
                  "Mine tunnel portal. Doorway clear >= 10 x 9.5 studs (under braces) for players and carts; rails along Y "
                  "(-Y front). heat_glow x3: two post lanterns and the inner tunnel lantern (warm amber, "
                  "small). No smoke.", glows)


def narrow(kit):
    a = kit.flintkit.Asset("MineSupportNarrow", "W15 MineSupportNarrow", tint_var=0.05, seed=1502)
    sand_patch(a, 7.5, -6.5, 7.0)
    rails(a, -6.5, 8.5, gauge=2.0)
    R(a, (5.5, 8.0, 11.0), -7.0, 4.6, 0.0, 0.2)
    R(a, (5.5, 8.0, 10.0), 7.0, 4.6, 0.0, -0.2)
    R(a, (4.0, 6.0, 8.0), -5.0, 7.0, 0.0, 0.3)
    R(a, (4.0, 6.0, 8.0), 5.0, 7.0, 0.0, -0.3)
    R(a, (7.0, 7.0, 5.5), -2.0, 5.0, 10.6, 0.4)
    R(a, (6.0, 7.0, 5.0), 3.0, 5.0, 10.6, -0.3)
    R(a, (11.0, 4.0, 12.0), 0.0, 10.0, 0.0)
    R(a, (2.8, 2.6, 2.2), -6.6, -2.6, 0.0, small=True)
    portal(a, hw=3.7, post_w=1.6, lintel_z=10.8, lintel_len=10.4, depth=4.0, drop=2.2, reach=2.2, bw=1.0)
    glows = [lantern(a, -3.7, -2.0, 6.6, arm=1.1, s=1.6), lantern(a, 3.7, -2.0, 4.8, arm=1.1, s=1.6)]
    banner(a, 3.7, 10.7, 1.4, 3.6, -1.15)
    for (r, loc) in ((1.4, (-5.2, -2.0, 0.4)), (1.2, (5.4, -2.0, 0.4)), (1.1, (-9.0, 1.0, 0.4)),
                     (1.1, (9.0, 0.5, 0.4)), (1.0, (4.6, 2.4, 14.4)), (0.9, (-5.6, 0.0, 9.0))):
        tuft(a, r, loc, floor=0.0 if loc[2] < 1 else None)
    return finish(kit, a, "variant", 5000, "precise",
                  "Narrow Support. Opening 5.7 x 8.6 studs. heat_glow x2 on the post lanterns; banner on the right post (as the reference image).",
                  glows)


def wide(kit):
    a = kit.flintkit.Asset("MineSupportWide", "W15 MineSupportWide", tint_var=0.05, seed=1503)
    sand_patch(a, 14.5, -8.0, 9.0)
    rails(a, -8.0, 11.0)
    R(a, (7.0, 9.0, 12.5), -13.2, 5.2, 0.0, 0.15)
    R(a, (7.0, 9.0, 11.5), 13.2, 5.2, 0.0, -0.15)
    R(a, (5.0, 7.0, 9.0), -10.6, 8.0, 0.0, 0.3)
    R(a, (5.0, 7.0, 9.0), 10.6, 8.0, 0.0, -0.3)
    R(a, (9.0, 7.0, 8.0), -6.5, 6.0, 12.4, 0.3)
    R(a, (9.0, 7.0, 8.5), 2.0, 6.0, 12.4, -0.2)
    R(a, (7.5, 7.0, 7.0), 9.8, 6.0, 12.0, 0.5)
    R(a, (24.0, 5.0, 18.0), 0.0, 12.0, 0.0)
    R(a, (3.8, 3.4, 3.0), -12.6, -3.0, 0.0, 0.4)
    portal(a, hw=9.0, post_w=2.4, lintel_z=11.0, lintel_len=22.0, depth=5.0, double=True, drop=4.5, reach=4.5, bw=1.3)
    glows = [lantern(a, -9.0, -2.7, 7.0, arm=1.5, s=1.9), lantern(a, 9.0, -2.7, 7.0, arm=1.5, s=1.9),
             lantern(a, 0.0, -0.2, 8.9, arm=0.0, s=1.3)]
    for (r, loc) in ((1.6, (-10.8, -2.0, 0.4)), (1.6, (10.8, -2.0, 0.4)), (1.3, (-16.0, 1.0, 0.4)),
                     (1.3, (16.0, 0.5, 0.4)), (1.0, (-4.0, -2.0, 0.4)), (1.3, (9.8, 2.4, 16.2)),
                     (1.1, (-7.0, 2.0, 17.6))):
        tuft(a, r, loc, floor=0.0 if loc[2] < 1 else None)
    return finish(kit, a, "variant", 6000, "precise",
                  "Wide Support, double lintel, no banner. heat_glow x3: post lanterns and centre lintel lantern.",
                  glows)


def damaged(kit):
    a = kit.flintkit.Asset("MineSupportDamaged", "W15 MineSupportDamaged", tint_var=0.05, seed=1504)
    sand_patch(a, 10.0, -8.0, 8.0)
    R(a, (6.5, 8.5, 12.0), -9.0, 5.0, 0.0, 0.2)
    R(a, (6.5, 8.5, 10.5), 9.0, 5.0, 0.0, -0.2)
    R(a, (4.5, 6.0, 8.0), -6.6, 7.0, 0.0, 0.3)
    R(a, (4.5, 6.0, 7.0), 6.6, 7.0, 0.0, -0.3)
    R(a, (8.5, 7.5, 6.0), -2.5, 5.5, 10.6, 0.4)
    R(a, (6.0, 6.5, 4.5), 4.2, 5.5, 9.5, -0.3)
    R(a, (13.0, 4.0, 12.0), 0.0, 10.5, 0.0)
    # standing left post on footing
    a.box((2.2, 2.2, 1.2), loc=(-5.0, 0, 0.6), mat=ROCK, bevel=0.15)
    a.box((1.4, 1.4, 10.8), loc=(-5.0, 0, 6.6), mat=T, bevel=0.06)
    a.box((1.9, 1.9, 1.3), loc=(-5.0, 0, 11.35), mat=T, bevel=0.08)
    plate(a, -5.0, 10.0, 0.7, 1.0, -0.95, nb=1)
    # leaning, broken right post
    a.box((2.2, 2.2, 1.2), loc=(5.0, 0, 0.6), mat=ROCK, bevel=0.15)
    tilt = 0.32
    h = 7.6
    a.box((1.4, 1.4, h), loc=(5.0 - math.sin(tilt) * h / 2, 0, 1.2 + math.cos(tilt) * h / 2),
          rot=(0, -tilt, 0), mat=T, bevel=0.06)
    a.box((0.8, 1.2, 1.0), loc=(5.0 - math.sin(tilt) * h + 0.1, 0, 1.2 + math.cos(tilt) * h + 0.2),
          rot=(0, -tilt - 0.4, 0), mat=T)  # splintered stub
    # cracked lintel: two pieces slanting from the left post down to the leaning post
    top_r = (5.0 - math.sin(tilt) * h, 1.2 + math.cos(tilt) * h + 0.7)
    xz_beam(a, (-6.0, 12.6), (-0.4, 11.0), 1.3, y=0.0)
    xz_beam(a, (0.0, 10.7), (top_r[0] + 1.5, top_r[1] - 0.4), 1.3, y=0.15)
    plate(a, -5.0, 12.4, 1.2, 0.7, -0.75)
    # one brace still hanging on the left
    xz_beam(a, (-4.3, 8.4), (-2.0, 11.6), 0.8, y=0.0, d=0.8)
    # two braces fallen on the ground, and a fallen tie
    a.box((5.5, 1.1, 1.1), loc=(-1.5, -3.6, 0.55), rot=(0, 0, 0.5), mat=T)
    a.box((5.5, 1.1, 1.1), loc=(3.0, -2.6, 1.05), rot=(0, -0.2, -0.35), mat=T)
    a.box((3.4, 0.6, 0.25), loc=(-3.0, -6.0, 0.25), rot=(0, 0, 0.3), mat=T)
    # rubble in the opening
    for (x, y, s) in ((-1.2, 2.2, 3.6), (1.8, 1.8, 3.2), (0.2, -0.4, 2.2), (3.4, -0.6, 1.8),
                      (-2.6, 0.8, 1.2), (5.8, -3.0, 1.1), (-6.8, -3.0, 1.0), (1.0, -4.5, 0.7)):
        R(a, (s * 1.3, s * 1.1, s * 0.9), x, y, 0.0, x * 0.7, small=s < 1.5)
    banner(a, -3.4, 11.0, 1.2, 3.2, -0.8, torn=True)
    glows = [lantern(a, -6.2, -1.6, 7.8, arm=0.9)]
    # fallen lantern on the ground (unlit, no socket)
    a.box((0.8, 0.8, 0.6), loc=(3.8, -4.6, 0.4), rot=(0.4, 0.9, 0.3), mat=IRON)
    for (r, loc) in ((1.6, (-7.2, -1.8, 0.4)), (1.4, (7.0, -1.8, 0.4)), (1.4, (-11.0, 0.5, 0.4)),
                     (1.0, (10.5, 0.0, 0.4)), (0.8, (-1.0, 0.8, 1.6)), (0.8, (2.2, 0.6, 1.4)),
                     (0.9, (-8.0, 1.0, 9.5)), (0.9, (7.5, 1.0, 8.5)), (0.8, (-2.0, 2.0, 15.0)),
                     (0.8, (0.5, -5.0, 0.3))):
        tuft(a, r, loc, floor=0.0 if loc[2] < 1 else None)
    return finish(kit, a, "variant", 6000, "precise",
                  "Damaged Support: leaning broken post, cracked slanted lintel, fallen braces and rubble partly "
                  "block the opening. heat_glow x1 on the surviving left lantern; fallen lantern has no socket.",
                  glows)


# ---------------------------------------------------------------- parts
def part_lintel(kit):
    a = kit.flintkit.Asset("MineSupportLintelBeam", "W15 MineSupportLintelBeam", tint_var=0.05, seed=1511)
    a.box((12.0, 1.2, 1.2), loc=(0, 0, 0.6), mat=T, bevel=0.07)
    for sx in (-1, 1):
        plate(a, sx * 5.3, 0.6, 1.3, 1.1, -0.6, nb=2)
        a.box((0.2, 1.3, 1.3), loc=(sx * 4.4, 0, 0.6), mat=IRON)
    o = a.finish()
    return kit.tag(o, "part", collision="box", budget=1500, notes="Lintel beam with iron end plates and bolts.")


def part_post(kit):
    a = kit.flintkit.Asset("MineSupportUprightPost", "W15 MineSupportUprightPost", tint_var=0.05, seed=1512)
    a.box((2.2, 2.2, 1.4), loc=(0, 0, 0.7), mat=ROCK, bevel=0.18)
    a.box((1.4, 1.4, 10.0), loc=(0, 0, 6.4), mat=T, bevel=0.06)
    a.box((1.5, 1.5, 0.2), loc=(0, 0, 9.6), mat=IRON)
    plate(a, 0, 2.6, 0.7, 1.0, -0.7, nb=1)
    o = a.finish()
    return kit.tag(o, "part", collision="box", budget=1500, notes="Upright post on a stone footing block.")


def part_collar(kit):
    a = kit.flintkit.Asset("MineSupportCollar", "W15 MineSupportCollar", tint_var=0.05, seed=1513)
    a.box((1.6, 1.6, 1.6), loc=(0, 0, 0.8), mat=T, bevel=0.1)
    a.box((1.7, 1.7, 0.22), loc=(0, 0, 0.55), mat=IRON)
    bolts(a, [(0, 0.55)], -0.9)
    o = a.finish()
    return kit.tag(o, "part", collision="box", budget=1500, notes="Collar block with iron strap.")


def part_brace(kit):
    a = kit.flintkit.Asset("MineSupportDiagonalBrace", "W15 MineSupportDiagonalBrace", tint_var=0.05, seed=1514)
    ang = math.radians(40)
    L = 5.5
    hx, hz = math.cos(ang) * L / 2, math.sin(ang) * L / 2
    zc = hz + 0.7
    xz_beam(a, (-hx, zc - hz), (hx, zc + hz), 1.2, y=0.0)
    # chunky notched end blocks: a block plus a stepped tenon (the notch)
    for sx, z in ((-1, zc - hz), (1, zc + hz)):
        a.box((1.3, 1.4, 1.2), loc=(sx * hx, 0, z), mat=T, bevel=0.07)
        a.box((0.6, 1.0, 0.6), loc=(sx * (hx + 0.85), 0, z - 0.3), mat=T, bevel=0.04)
        plate(a, sx * hx, z, 1.0, 1.0, -0.7, nb=1)
    plate(a, 0, zc, 1.2, 0.5, -0.6)
    o = a.finish()
    return kit.tag(o, "part", collision="box", budget=1500, notes="Diagonal brace with end blocks and iron plate.")


def build(kit):
    return [hero(kit), part_lintel(kit), part_post(kit), part_collar(kit), part_brace(kit),
            narrow(kit), wide(kit), damaged(kit)]
