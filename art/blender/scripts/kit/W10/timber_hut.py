"""W10 row 3: TimberHut - log-and-plank hut with a canvas gable roof.

Hut coordinates: front (door gable) faces -Y, ridge along Y, floor top z=1.2.
"""
import math

from mathutils import Vector

SUBJECT = "TimberHut"
ROW = 3
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 90

PALETTE = {
    "w10_wood": ("#8A4A22", 0.85, 0, 0),
    "w10_canvas": ("#E3CFA0", 0.95, 0, 0),
    "w10_rope": ("#C48A38", 0.8, 0, 0),
    "w10_stone": ("#9A9498", 0.9, 0, 0),
    "w10_banner": ("#B8191F", 0.9, 0, 0),
    "w10_iron": ("#575B64", 0.5, 0.4, 0),
    "w10_lantern": ("#FFB022", 0.4, 0, 2),
    "w10_foliage": ("#3F8C24", 0.9, 0, 0),
}
WOOD, CANVAS, ROPE, STONE = "w10_wood", "w10_canvas", "w10_rope", "w10_stone"
BANNER, IRON, GLOW, LEAF = "w10_banner", "w10_iron", "w10_lantern", "w10_foliage"

# Roof geometry: canvas top surface runs from the ridge (0, ZR) to the eave (XE, ZE).
XE, ZE, ZR = 9.0, 8.5, 14.0
RL = math.hypot(XE, ZR - ZE)
C, S = XE / RL, (ZR - ZE) / RL
TH = math.atan2(ZR - ZE, XE)
WX, WY = 7.4, 9.4          # wall centre planes
WALL_TOP = 8.4
FLOOR = 1.2

GLOW_COL = ["#FFB022", "#FF8A1E"]
SMOKE = [{"name": "Smoke", "texture": "smoke_puff", "color": ["#ECE9E4", "#F8F6F3"],
          "size": [0.6, 2.0], "transparency": [0.72, 1.0], "lifetime": [2, 3.5], "rate": 2,
          "speed": [2.5, 3.5], "spread": 5, "light_emission": 0.2,
          "acceleration": [0.3, 0.2, 0], "drag": 0.3, "rotation": [0, 360],
          "rot_speed": [-20, 20]}]


# ---------------------------------------------------------------- helpers
def pt(side, s, y, off):
    return (side * (C * s + S * off), y, ZR - S * s + C * off)


def slope_box(a, side, s0, s1, y0, y1, thick, off, mat, rz=0.0, rx=0.0):
    c = pt(side, (s0 + s1) / 2, (y0 + y1) / 2, off)
    return a.box((s1 - s0, y1 - y0, thick), loc=c, rot=(rx, side * TH, rz), mat=mat)


def sqbeam(a, p1, p2, w, h, mat=WOOD):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    q = d.to_track_quat("Z", "Y")
    m = (p1 + p2) / 2
    return a.box((w, h, d.length), loc=tuple(m), rot=tuple(q.to_euler()), mat=mat)


def stone(a, size, loc, rot=(0, 0, 0), jitter=0.03):
    # sit on the ground: centre z lifted so jitter never dips below z=0
    return a.stone_block(size, loc=loc, rot=rot, mat=STONE, jitter=jitter)


def foundation(a, yf, yb=10.0, xh=8.0):
    rng = a.rng

    def row(u0, u1, fixed, along_x):
        u = u0
        while u < u1 - 0.3:
            l = rng.uniform(2.7, 3.8)
            if u1 - (u + l) < 1.4:
                l = u1 - u
            c = u + l / 2
            h = 1.5 + rng.uniform(-0.1, 0.2)
            d = rng.uniform(1.1, 1.4)
            if along_x and fixed < 0 and abs(c) < 3.2:
                h = 1.2
            o = math.copysign(rng.uniform(0.0, 0.15), fixed)
            if along_x:
                stone(a, (l - 0.16, d, h), (c, fixed + o, h / 2 + 0.08), jitter=0.07)
            else:
                stone(a, (d, l - 0.16, h), (fixed + o, c, h / 2 + 0.08), jitter=0.07)
            u += l

    row(-xh + 1.3, xh - 1.3, yf + 0.5, True)
    row(-xh + 1.3, xh - 1.3, yb - 0.5, True)
    row(yf + 1.3, yb - 1.3, -xh + 0.5, False)
    row(yf + 1.3, yb - 1.3, xh - 0.5, False)


def floor(a, y0, y1):
    for i in range(7):
        x = -6.0 + i * 2.0
        a.box((1.94, y1 - y0, 0.4), loc=(x, (y0 + y1) / 2, FLOOR - 0.2), mat=WOOD)


def corner_post(a, x, y, top=8.6, foot=True):
    if foot:
        stone(a, (1.9, 1.9, 1.8), (x, y, 0.93))
    a.box((1.25, 1.25, top - 1.35), loc=(x, y, 1.35 + (top - 1.35) / 2), mat=WOOD, bevel=0.08)


def clap(a, c, out, length, h=1.32, t=0.6):
    """One clapboard: thick lip at the bottom (dark down-facing seam), tapering up
    behind the board above. c = inner bottom-centre, out = outward unit vector."""
    out = Vector(out)
    up = Vector((0, 0, 1))
    al = out.cross(up)
    pts = [(0, 0), (t, 0), (t, 0.32), (0.1, h), (0, h)]
    vs = a.poly_prism(pts, length, mat=WOOD)
    c = Vector(c)
    for v in vs:
        u, w, s = v.co.x, v.co.y, v.co.z
        v.co = c + out * u + up * w + al * (s - length / 2)
    return vs


def boards_x(a, side, y0, y1, win=None):
    """Side wall (plane x = side*WX) of 6 overlapping clapboards; win=(ylo, yhi, i0, i1)."""
    for i in range(6):
        zb = FLOOR + i * 1.2 - 0.04
        segs = [(y0, y1)]
        if win and win[2] <= i <= win[3]:
            segs = [(y0, win[0]), (win[1], y1)]
        for u0, u1 in segs:
            clap(a, (side * (WX - 0.28), (u0 + u1) / 2, zb), (side, 0, 0), u1 - u0)


def boards_y(a, sidey, segs):
    for i in range(6):
        zb = FLOOR + i * 1.2 - 0.04
        for u0, u1 in segs:
            clap(a, ((u0 + u1) / 2, sidey * (WY - 0.28), zb), (0, sidey, 0), u1 - u0)


def gable(a, sidey):
    ly = sidey * WY + 0.25

    def hw(z):
        return max(0.0, min(WX, (ZR - 0.4 - z) * C / S))
    zs = [WALL_TOP, 9.6, 10.8, 12.0, 13.1]
    ztop = ZR - 0.4
    for i, z0 in enumerate(zs):
        z1 = zs[i + 1] + 0.08 if i + 1 < len(zs) else ztop
        h0, h1 = hw(z0), hw(z1)
        if h1 < 0.05:
            pts = [(-h0, z0), (h0, z0), (0, ztop)]
        else:
            pts = [(-h0, z0), (h0, z0), (h1, z1), (-h1, z1)]
        a.poly_prism(pts, 0.5 + 0.06 * (i % 2), loc=(0, ly + 0.03 * (i % 2), 0),
                     rot=(math.pi / 2, 0, 0), mat=WOOD)


def door(a, cx=0.0, yw=-WY, ajar=0.3):
    for sx in (-1, 1):
        a.box((0.8, 1.1, 7.85), loc=(cx + sx * 2.6, yw - 0.2, FLOOR + 3.92), mat=WOOD, bevel=0.08)
    a.box((7.0, 1.2, 0.9), loc=(cx, yw - 0.25, 8.3 + 0.4), mat=WOOD, bevel=0.08)
    a.box((5.6, 1.3, 0.3), loc=(cx, yw - 0.3, FLOOR - 0.1), mat=WOOD)   # threshold
    v = []
    for i in range(4):
        v += a.box((1.02, 0.3, 6.95), loc=(-0.58 - i * 1.06, 0, FLOOR + 0.05 + 3.475), mat=WOOD, bevel=0.1)
    for z in (2.6, 7.0):
        v += a.box((4.0, 0.2, 0.55), loc=(-2.15, -0.22, z), mat=WOOD)
        v += a.box((2.4, 0.12, 0.36), loc=(-1.1, -0.38, z), mat=IRON)
        v += a.box((0.5, 0.14, 0.5), loc=(-0.15, -0.4, z), mat=IRON)
    v += a.box((0.3, 0.12, 0.3), loc=(-3.6, -0.36, 4.75), mat=IRON)
    v += a.torus(0.42, 0.09, loc=(-3.6, -0.42, 4.4), rot=(math.pi / 2, 0, 0), seg=8, rseg=3, mat=IRON)
    a.transform(v, loc=(cx + 2.15, yw + 0.12, 0), rot=(0, 0, -ajar))


def lantern(a, x, yw, z):
    """Iron bracket on the wall face at yw (front, facing -Y); returns glow point."""
    ly = yw - 1.1
    a.box((0.18, 1.25, 0.18), loc=(x, yw - 0.6, z + 1.25), mat=IRON)
    a.box((0.12, 0.12, 0.45), loc=(x, ly, z + 1.0), mat=IRON)
    a.box((0.85, 0.85, 1.1), loc=(x, ly, z + 0.2), mat=GLOW)
    for dx in (-0.45, 0.45):
        a.box((0.1, 0.95, 1.1), loc=(x + dx, ly, z + 0.2), mat=IRON)
    a.cyl(0.7, 0.12, 0.5, sides=4, loc=(x, ly, z + 0.75), rot=(0, 0, math.pi / 4), mat=IRON)
    a.box((1.0, 1.0, 0.14), loc=(x, ly, z - 0.4), mat=IRON)
    return (x, ly, z + 0.35)


def window(a, side, yc, hw, z0, z1):
    x = side * 7.62
    a.box((0.6, 2 * hw + 0.9, 0.42), loc=(x, yc, z1 + 0.2), mat=WOOD)
    a.box((0.7, 2 * hw + 1.0, 0.42), loc=(x + side * 0.05, yc, z0 - 0.2), mat=WOOD)
    for sy in (-1, 1):
        a.box((0.6, 0.42, z1 - z0), loc=(x, yc + sy * (hw + 0.2), (z0 + z1) / 2), mat=WOOD)
    a.box((0.3, 0.2, z1 - z0), loc=(x, yc, (z0 + z1) / 2), mat=WOOD)
    a.box((0.3, 2 * hw, 0.2), loc=(x, yc, (z0 + z1) / 2), mat=WOOD)
    a.box((0.1, 2 * hw, z1 - z0), loc=(side * 7.38, yc, (z0 + z1) / 2), mat=GLOW)
    return (side * 7.9, yc, (z0 + z1) / 2)


def roof_side(a, side, y0, y1, slate=False):
    L = RL
    if not slate:
        cuts = [y0 + (y1 - y0) * k / 3 for k in range(4)]
        for i in range(3):
            slope_box(a, side, -0.2, L, cuts[i], cuts[i + 1], 0.3, -0.15, CANVAS)
        # 3 cross battens wrapped in canvas (raised seams) with rope ties at the eave end
        sm = L * 0.55
        for yb in cuts[1:3]:
            slope_box(a, side, 0.2, L - 0.05, yb - 0.2, yb + 0.2, 0.22, 0.05, CANVAS)
            slope_box(a, side, L - 0.75, L - 0.4, yb - 0.3, yb + 0.3, 0.4, 0.08, ROPE)
        slope_box(a, side, sm - 0.2, sm + 0.2, y0 + 0.3, y1 - 0.3, 0.2, 0.04, CANVAS)
        n = 6
        for k in range(n):
            yy = y0 + 0.9 + k * (y1 - y0 - 1.8) / (n - 1)
            slope_box(a, side, L - 0.45, L + 0.05, yy - 0.14, yy + 0.14, 0.55, -0.12, ROPE)
    else:
        rng = a.rng
        slope_box(a, side, -0.2, L, y0, y1, 0.3, -0.15, WOOD)
        ncourse = 5
        for c in range(ncourse):
            s1 = L + 0.1 - c * 2.25
            s0 = max(-0.1, s1 - 2.6)
            y = y0 - 0.1
            while y < y1 - 0.2:
                w = rng.uniform(2.2, 3.0)
                w = min(w, y1 + 0.1 - y)
                if rng.random() > 0.08:
                    sh = rng.uniform(0.0, 0.5) if rng.random() < 0.25 else 0.0
                    sc = pt(side, (s0 + sh + s1) / 2, y + w / 2, 0.32)
                    a.box((s1 - s0 - sh, w - 0.12, 0.42), loc=sc,
                          rot=(rng.uniform(-0.05, 0.05), side * (TH - 0.12), rng.uniform(-0.06, 0.06)),
                          mat=STONE)
                y += w
    for yb in (y0 - 0.25, y1 + 0.25):
        sqbeam(a, pt(side, -1.3, yb, 0.15), pt(side, L + 0.3, yb, 0.15), 0.5, 0.9)
    n = max(2, int(round((y1 - y0) / 5.2)) + 1)
    for k in range(n):
        yr = y0 + 0.6 + k * (y1 - y0 - 1.2) / (n - 1)
        sqbeam(a, pt(side, 0.8, yr, -0.6), pt(side, L + 1.0, yr, -0.6), 0.85, 0.95)


def ridge(a, y0, y1):
    sqbeam(a, (0, y0 - 1.4, ZR + 0.3), (0, y1 + 1.4, ZR + 0.3), 0.9, 0.9)


def chimney(a, x, y, zb=9.6, courses=4, crook=(0.0, 0.0)):
    v = []
    for i in range(courses):
        zc = i * 1.2 + 0.6
        if i % 2:
            for d in (-0.75, 0.75):
                v += a.stone_block((1.45, 3.0, 1.18), loc=(d, 0, zc), mat=STONE)
        else:
            for d in (-0.75, 0.75):
                v += a.stone_block((3.0, 1.45, 1.18), loc=(0, d, zc), mat=STONE)
    top = courses * 1.2
    v += a.stone_block((3.5, 3.5, 0.42), loc=(0, 0, top + 0.21), mat=STONE)
    v += a.box((1.5, 1.5, 0.16), loc=(0, 0, top + 0.43), mat=IRON)
    a.transform(v, loc=(x, y, zb), rot=(crook[0], crook[1], 0))
    h = top + 0.5
    return (x + h * math.sin(crook[1]), y - h * math.sin(crook[0]), zb + h)


def barrel(a, x, y, z=0.0, k=1.25):
    a.cyl(0.85 * k, 1.05 * k, 1.2 * k, sides=10, loc=(x, y, z), mat=WOOD)
    a.cyl(1.05 * k, 0.85 * k, 1.2 * k, sides=10, loc=(x, y, z + 1.2 * k), mat=WOOD)
    for R, zz in ((0.93, 0.28), (1.08, 1.2), (0.93, 2.12)):
        a.torus(R * k, 0.09, loc=(x, y, z + zz * k), seg=10, rseg=3, mat=IRON)


def crate(a, x, y, z=0.0, s=2.0, rz=0.3):
    v = a.box((s, s, s), loc=(0, 0, s / 2), bevel=0.06, mat=WOOD)
    v += a.box((s * 1.25, 0.1, 0.26), loc=(0, -s / 2 - 0.04, s / 2), rot=(0, 0.785, 0), mat=WOOD)
    v += a.box((0.1, s * 1.25, 0.26), loc=(s / 2 + 0.04, 0, s / 2), rot=(0.785, 0, 0), mat=WOOD)
    v += a.box((s + 0.08, s + 0.08, 0.22), loc=(0, 0, s - 0.1), mat=WOOD)
    a.transform(v, loc=(x, y, z), rot=(0, 0, rz))


def tuft(a, x, y, r=1.0, n=6):
    rng = a.rng
    for k in range(n):
        ang = k * 2 * math.pi / n + rng.uniform(-0.3, 0.3)
        tilt = rng.uniform(0.25, 0.6)
        dx, dy = math.cos(ang) * 0.25 * r, math.sin(ang) * 0.25 * r
        a.cyl(0.24 * r, 0.0, rng.uniform(0.9, 1.5) * r, sides=3,
              loc=(x + dx, y + dy, 0.1 * r),
              rot=(-math.sin(ang) * tilt, math.cos(ang) * tilt, rng.uniform(0, 3)), mat=LEAF)


def rubble(a, x, y, s=0.7):
    rng = a.rng
    h = s * rng.uniform(0.55, 0.8)
    stone(a, (s * rng.uniform(0.9, 1.3), s, h), (x, y, h / 2 + 0.03), rot=(0, 0, rng.uniform(0, 3)))


def banner(a, x, y):
    a.box((0.6, 0.6, 8.0), loc=(x, y, 4.0), mat=WOOD, bevel=0.05)
    a.cyl(0.38, 0.18, 0.5, sides=6, loc=(x, y, 8.0), mat=WOOD)
    bx = x - 0.4
    a.box((3.2, 0.42, 0.42), loc=(bx, y, 7.55), mat=WOOD)
    for ex in (bx - 1.6, bx + 1.6):
        a.box((0.5, 0.5, 0.5), loc=(ex, y, 7.55), mat=WOOD, bevel=0.08)
    for hx in (bx - 0.75, bx + 0.75):
        a.box((0.12, 0.12, 0.4), loc=(hx, y - 0.3, 7.25), mat=IRON)
    cloth = [(-0.9, -4.5), (0.0, -3.8), (0.9, -4.5), (0.9, 0.0), (-0.9, 0.0)]
    a.poly_prism(cloth, 0.15, loc=(bx, y - 0.25, 7.3), rot=(math.pi / 2, 0, 0), mat=BANNER)
    dia = [(0, -0.9), (-0.55, -1.9), (0, -2.9), (0.55, -1.9)]
    a.poly_prism(dia, 0.05, loc=(bx, y - 0.4, 7.3), rot=(math.pi / 2, 0, 0), mat=CANVAS)
    dia2 = [(0, -1.35), (-0.28, -1.9), (0, -2.45), (0.28, -1.9)]
    a.poly_prism(dia2, 0.04, loc=(bx, y - 0.45, 7.3), rot=(math.pi / 2, 0, 0), mat=BANNER)


def platform(a, x, y):
    for sx in (-1.4, 1.4):
        a.box((0.45, 2.6, 0.45), loc=(x + sx, y, 0.25), mat=WOOD)
    for i in range(3):
        a.box((3.6, 0.8, 0.24), loc=(x, y + (i - 1) * 0.86, 0.6), mat=WOOD, bevel=0.04)


def steps(a, yf):
    for sx in (-1, 1):
        stone(a, (2.6, 1.05, 0.8), (sx * 1.3, yf - 0.55, 0.43))
        stone(a, (2.9, 1.0, 0.42), (sx * 1.45, yf - 1.55, 0.24))


def moss(a, side, s, y, r=1.4):
    p = pt(side, s, y, 0.45)
    a.leaf_cluster(r, loc=p, mat=LEAF, lobes=6, squash=0.35, facets=1,
                   axis=(side * S, 0.0, C))


# ---------------------------------------------------------------- hut assembly
def hut(a, opt):
    rng = a.rng
    ws = opt.get("workshop", False)
    slate = opt.get("slate", False)
    yf = -14.0 if ws else -10.0
    ry0 = -14.4 if ws else -11.0
    ry1 = 11.0
    out = {"glow": [], "smoke": None}

    foundation(a, yf)
    floor(a, yf + 0.8, 9.2)
    if not ws:
        steps(a, yf)
    posts = [(sx * WX, sy * WY) for sx in (-1, 1) for sy in (-1, 1)]
    if ws:
        posts += [(-WX, -13.4), (WX, -13.4)]
    for x, y in posts:
        corner_post(a, x, y)

    win = opt.get("window", "big")
    wtuple = None
    if win == "big":
        wtuple = (-1.2, 1.2, 3, 4)
    elif win == "small":
        wtuple = (-0.8, 0.8, 3, 3)
    boards_x(a, -1, -WY + 0.5, WY - 0.5)
    boards_x(a, 1, -WY + 0.5, WY - 0.5, wtuple)
    if wtuple:
        z0 = FLOOR + wtuple[2] * 1.2 + 0.05
        z1 = FLOOR + (wtuple[3] + 1) * 1.2 + 0.05
        out["glow"].append(window(a, 1, 0.0, wtuple[1], z0, z1))
    boards_y(a, 1, [(-WX + 0.5, WX - 0.5)])
    if not ws:
        boards_y(a, -1, [(-WX + 0.5, -2.9), (2.9, WX - 0.5)])
        door(a)
    gable(a, -1)
    gable(a, 1)

    for sx in (-1, 1):
        sqbeam(a, (sx * 7.6, ry0 - 1.0, 8.85), (sx * 7.6, ry1 + 1.0, 8.85), 0.9, 0.9)
    tie_front = -13.4 if ws else -WY - 0.6
    # king post at the front gable, tie beam up to the ridge
    a.box((0.6, 0.5, ZR - 9.2), loc=(0, -WY - 0.45, 9.2 + (ZR - 9.2) / 2), mat=WOOD)
    for ty in (tie_front, WY + 0.6):
        sqbeam(a, (-9.7, ty, 8.85), (9.7, ty, 8.85), 0.8, 0.8)
    for side in (-1, 1):
        roof_side(a, side, ry0, ry1, slate=slate)
    ridge(a, ry0, ry1)

    if opt.get("chimney", True):
        crook = (0.1, -0.12) if opt.get("crooked") else (0.0, 0.0)
        out["smoke"] = chimney(a, 4.6, 6.0, crook=crook)

    for lx in opt.get("lanterns", ()):
        out["glow"].append(lantern(a, lx, -WY - 0.25, 5.85))
    if opt.get("banner"):
        banner(a, -11.2, -11.4)
    if opt.get("platform"):
        platform(a, 5.6, -11.5)
    if opt.get("barrel"):
        barrel(a, -9.9, -8.0)
    if opt.get("crate"):
        crate(a, -8.2, -11.9)
    for (x, y, r) in opt.get("tufts", ()):
        tuft(a, x, y, r * 1.4)
    for (x, y, s) in opt.get("rubble", ()):
        rubble(a, x, y, s)

    if ws:
        # workbench with lamp and forge-lit goods, barrel and crate in the open bay
        bx, by = 0.0, -6.8
        a.box((5.6, 2.0, 0.35), loc=(bx, by, 4.0), mat=WOOD, bevel=0.05)
        for sx in (-1, 1):
            for sy in (-1, 1):
                a.box((0.35, 0.35, 2.65), loc=(bx + sx * 2.4, by + sy * 0.7, FLOOR + 1.33), mat=WOOD)
        a.box((5.0, 0.3, 0.3), loc=(bx, by, 2.2), mat=WOOD)
        lp = (bx + 1.7, by, 4.55)
        a.box((0.55, 0.55, 0.7), loc=lp, mat=GLOW)
        a.cyl(0.48, 0.1, 0.38, sides=4, loc=(lp[0], lp[1], 4.9), rot=(0, 0, math.pi / 4), mat=IRON)
        a.box((0.9, 0.5, 0.3), loc=(bx - 0.9, by - 0.2, 4.32), mat=GLOW)
        a.box((0.6, 0.6, 0.45), loc=(bx - 0.1, by + 0.3, 4.4), mat=IRON)
        out["glow"].append(lp)
        barrel(a, -5.2, -4.6, z=FLOOR)
        crate(a, 5.0, -4.0, z=FLOOR, s=1.4, rz=0.2)

    if opt.get("mossy"):
        for side, s, y, r in ((-1, 3.0, -6.0, 2.0), (-1, 7.5, 2.0, 1.8), (1, 5.0, -8.0, 1.6),
                              (1, 8.5, 4.0, 1.9), (-1, 9.6, -9.5, 1.6)):
            moss(a, side, s, y, r)
        # vines draping down the front-left corner and left wall
        for (x0, y0) in ((-6.0, -9.9), (-4.4, -9.9), (-7.9, -7.0), (-7.9, -2.0)):
            pts = [(x0, y0, 8.6)]
            for k in range(1, 5):
                pts.append((x0 + rng.uniform(-0.3, 0.3), y0, 8.6 - k * 1.3))
            a.tube_loop(pts, 0.14, mat=LEAF, rseg=4, closed=False)
            ax = (0.0, -1.0, 0.0) if y0 < -9 else (-1.0, 0.0, 0.0)
            for p in pts[2:3]:
                q = (p[0] + 0.5 * ax[0], p[1] + 0.5 * ax[1], p[2])
                a.leaf_cluster(0.75, loc=q, mat=LEAF, lobes=5, squash=0.45, facets=1, axis=ax)
        a.leaf_cluster(1.4, loc=(-8.5, -5.0, 1.3), mat=LEAF, lobes=6, squash=0.6, facets=1,
                       axis=(-1.0, 0.0, 0.0))
    return out


def done(a):
    xs = [v.co.x for v in a.bm.verts]
    ys = [v.co.y for v in a.bm.verts]
    zs = [v.co.z for v in a.bm.verts]
    off = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs))
    return a.finish(), off


def sock(vfx, o, off, kind, p, **kw):
    vfx.add(o, kind, (p[0] - off[0], p[1] - off[1], p[2] - off[2]), **kw)


HERO_TUFTS = [(-8.6, -10.5, 1.1), (-8.7, -3.5, 0.9), (-3.4, -10.7, 0.9), (3.4, -10.7, 0.8),
              (8.6, -9.0, 1.0), (8.7, 3.5, 0.9), (-8.6, 6.5, 0.9), (-11.4, -11.0, 1.0),
              (-10.6, -8.0, 0.8), (2.5, 10.5, 0.8)]
HERO_RUBBLE = [(-10.6, -9.6, 0.7), (8.9, -11.2, 0.6), (-3.8, -11.9, 0.55), (9.1, 7.0, 0.7)]


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    res = []

    # ---------------- hero
    a = fk.Asset("TimberHut", "W10 TimberHut", seed=310)
    out = hut(a, dict(window="big", lanterns=(-4.1, 4.1), banner=True, platform=True,
                      barrel=True, crate=True, tufts=HERO_TUFTS, rubble=HERO_RUBBLE))
    o, off = done(a)
    sock(vfx, o, off, "chimney_smoke", out["smoke"], scale=1.0, emitters=SMOKE)
    for g in out["glow"][1:]:
        sock(vfx, o, off, "heat_glow", g, scale=0.5, color=GLOW_COL)
    sock(vfx, o, off, "heat_glow", out["glow"][0], scale=0.4, color=GLOW_COL)
    res.append(kit.tag(o, "hero", collision="precise", budget=8000,
                       notes="Walkable one-room hut, floor z=1.2, door opening 4.4x7.1 with the plank leaf ~17 deg ajar "
                             "(swap in TimberHutDoorframe as a hinged part to open it). VFX: chimney_smoke at "
                             "chimney top (thin pale smoke); heat_glow at each door lantern (2) and at the "
                             "side window glow."))

    # ---------------- parts
    a = fk.Asset("TimberHutRoofPanel", "W10 TimberHut", seed=311)
    roof_side(a, -1, -9.0, 9.0)
    res.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="One canvas roof side on rafters with battens, rope ties and edge boards; use 2x mirrored."))

    a = fk.Asset("TimberHutRidgeBeam", "W10 TimberHut", seed=312)
    a.box((0.9, 17.6, 0.9), loc=(0, 0, 0.45), mat=WOOD, bevel=0.06)
    for sy in (-1, 1):
        a.box((0.9, 1.2, 0.5), loc=(0, sy * 9.4, 0.25), mat=WOOD, bevel=0.04)
        a.torus(0.55, 0.08, loc=(0, sy * 7.6, 0.45), rot=(math.pi / 2, 0, 0), seg=8, rseg=3, mat=ROPE)
    res.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Ridge beam 20 long with half-lap notched ends and rope wraps."))

    a = fk.Asset("TimberHutWallPanel", "W10 TimberHut", seed=313)
    for i in range(6):
        clap(a, (0, 0.15, 0.3 + i * 1.25), (0, -1, 0), 7.2, h=1.38, t=0.65)
    for sx in (-1, 1):
        a.box((0.9, 1.0, 8.0), loc=(sx * 3.55, 0.0, 4.0), mat=WOOD, bevel=0.08)
    a.box((7.2, 0.8, 0.35), loc=(0, 0.1, 0.18), mat=WOOD)
    res.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Plank wall panel ~8x8x1 of stacked overlapping boards; used 4x."))

    a = fk.Asset("TimberHutFloor", "W10 TimberHut", seed=314)
    for sx in (-1, 0, 1):
        a.box((0.9, 20.0, 0.8), loc=(sx * 6.5, 0, 0.4), mat=WOOD)
    for i in range(8):
        a.box((1.94, 20.0, 0.4), loc=(-7.0 + i * 2.0, 0, 1.0), mat=WOOD, bevel=0.05)
    a.box((5.0, 1.2, 0.8), loc=(0, -10.6, 0.4), mat=WOOD, bevel=0.05)
    a.box((5.0, 1.2, 0.4), loc=(0, -11.8, 0.2), mat=WOOD, bevel=0.05)
    res.append(kit.tag(a.finish(), "part", collision="precise", budget=1500,
                       notes="Plank floor 16x20x1.2 on joists with a 2-step entry."))

    a = fk.Asset("TimberHutDoorframe", "W10 TimberHut", seed=315)
    door(a, yw=0.0, ajar=0.12)
    res.append(kit.tag(a.finish(), "part", collision="precise", budget=1500,
                       notes="Heavy doorframe with plank door leaf, iron hinges and ring handle, 5 wide x 8 tall."))

    a = fk.Asset("TimberHutCornerPost", "W10 TimberHut", seed=316)
    corner_post(a, 0, 0, top=9.0)
    res.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Square timber post 9 tall on a grey stone footing; used 4x."))

    # ---------------- variations
    a = fk.Asset("TimberHutStandardOneRoom", "W10 TimberHut", seed=320)
    out = hut(a, dict(window="small", lanterns=(-4.1,), barrel=True,
                      tufts=HERO_TUFTS[:6], rubble=HERO_RUBBLE[:2]))
    o, off = done(a)
    sock(vfx, o, off, "chimney_smoke", out["smoke"], scale=1.0, emitters=SMOKE)
    sock(vfx, o, off, "heat_glow", out["glow"][1], scale=0.5, color=GLOW_COL)
    res.append(kit.tag(o, "variant", collision="precise", budget=6000,
                       notes="1. Standard One-Room. VFX: chimney_smoke at chimney top; heat_glow at the lantern."))

    a = fk.Asset("TimberHutOpenWorkshop", "W10 TimberHut", seed=321)
    out = hut(a, dict(workshop=True, window=None, tufts=HERO_TUFTS[3:8], rubble=HERO_RUBBLE[1:3]))
    o, off = done(a)
    sock(vfx, o, off, "heat_glow", out["glow"][-1], scale=0.6, color=GLOW_COL)
    res.append(kit.tag(o, "variant", collision="precise", budget=6000,
                       notes="2. Open Workshop: open front bay with workbench. VFX: heat_glow on the workbench "
                             "lamp."))

    a = fk.Asset("TimberHutWeathered", "W10 TimberHut", seed=322)
    out = hut(a, dict(slate=True, window="small", lanterns=(4.1,), crooked=True, mossy=True,
                      tufts=HERO_TUFTS[:7], rubble=HERO_RUBBLE))
    o, off = done(a)
    sock(vfx, o, off, "chimney_smoke", out["smoke"], scale=1.0, emitters=SMOKE)
    res.append(kit.tag(o, "variant", collision="precise", budget=6000,
                       notes="3. Weathered: stone-slate roof, moss and vines, crooked chimney. VFX: chimney_smoke "
                             "at chimney top."))
    return res
