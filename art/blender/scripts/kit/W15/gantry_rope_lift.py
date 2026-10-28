"""W15 row 4: Gantry and rope lift (timber crane and cargo lift)."""
import math

SUBJECT = "GantryRopeLift"
ROW = 4
PALETTE = {
    "w15_timber": ("#A9662B", 0.85, 0, 0),
    "w15_iron": ("#454B66", 0.5, 0.4, 0),
    "w15_rock": ("#8E8E96", 0.95, 0, 0),
    "w15_sand": ("#D4B98E", 1, 0, 0),
    "w15_foliage": ("#3E9A22", 0.9, 0, 0),
    "w15_banner": ("#C8161F", 0.8, 0, 0),
    "w15_rope": ("#C0903A", 0.95, 0, 0),
}
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 50   # reference SIDE cell shows the frame three-quarter with rope and crate beside the post

T, I, R, S, F, B, P = ("w15_timber", "w15_iron", "w15_rock", "w15_sand",
                       "w15_foliage", "w15_banner", "w15_rope")


# ---------------------------------------------------------------- helpers
def sq(a, p1, p2, w, mat=T, h=None):
    """Square timber of section w x h between two points."""
    dx, dy, dz = (p2[i] - p1[i] for i in range(3))
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    yaw = math.atan2(dy, dx)
    pitch = -math.atan2(dz, math.hypot(dx, dy))
    mid = tuple((p1[i] + p2[i]) / 2 for i in range(3))
    return a.box((L, w, h or w), loc=mid, rot=(0, pitch, yaw), mat=mat, bevel=0.06)


def post(a, x, y, z0, z1, w=1.6):
    a.box((w, w, z1 - z0), loc=(x, y, (z0 + z1) / 2), mat=T, bevel=0.08)
    # iron band near the top
    a.box((w + 0.12, w + 0.12, 0.35), loc=(x, y, z1 - 1.0), mat=I)


def bolts(a, xs, y, z, s=0.22):
    for x in xs:
        a.box((s, s, s), loc=(x, y, z), mat=I)


def plate(a, x, y, z, w=1.0, h=1.4, front=True):
    """Iron plate on the front (-Y) face with 2 bolt heads."""
    a.box((w, 0.12, h), loc=(x, y, z), mat=I)
    bolts(a, [x - w * 0.25, x + w * 0.25], y - 0.1, z + h * 0.22, 0.2)
    bolts(a, [x], y - 0.1, z - h * 0.22, 0.2)


def footing(a, x, y, size=(2.8, 2.8, 2.2)):
    a.rock(size, loc=(x, y, 0), mat=R, subdiv=1, rough=0.1, facets=20, sink=0.1)


def rope(a, pts, t=0.16):
    a.tube_loop(pts, t, mat=P, rseg=5, closed=False)


def ring(a, loc, R_=0.32):
    a.torus(R_, 0.09, loc=loc, rot=(math.pi / 2, 0, 0), mat=I, seg=8, rseg=4)


def crate(a, cx, cy, z0, w=3.6, d=3.6, h=2.4, ring_z=None):
    """Open plank crate frame with iron corner plates; ropes to a ring above."""
    hw, hd = w / 2, d / 2
    a.box((w, d, 0.25), loc=(cx, cy, z0 + 0.125), mat=T)              # floor
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.box((0.35, 0.35, h), loc=(cx + sx * (hw - 0.17), cy + sy * (hd - 0.17), z0 + h / 2), mat=T)
            for zz in (z0 + 0.3, z0 + h - 0.3):                           # iron corner plates
                a.box((0.5, 0.5, 0.45), loc=(cx + sx * (hw - 0.15), cy + sy * (hd - 0.15), zz), mat=I)
    for zz in (z0 + 0.75, z0 + h - 0.45):                                  # side planks with gaps
        for sy in (-1, 1):
            a.box((w - 0.5, 0.16, 0.6), loc=(cx, cy + sy * (hd - 0.1), zz), mat=T)
        for sx in (-1, 1):
            a.box((0.16, d - 0.5, 0.6), loc=(cx + sx * (hw - 0.1), cy, zz), mat=T)
    if ring_z is not None:
        top = z0 + h
        rz = ring_z
        for sx in (-1, 1):
            for sy in (-1, 1):
                rope(a, [(cx + sx * (hw - 0.17), cy + sy * (hd - 0.17), top),
                         (cx + sx * 0.12, cy + sy * 0.12, rz - 0.25)], 0.08)
        ring(a, (cx, cy, rz))


def pulley(a, x, y, z, r=1.0, w=0.7, bracket_top=None):
    """Octagonal iron wheel, axis along Y, centred at (x, y, z)."""
    a.cyl(r, r, w, sides=8, loc=(x, y - w / 2, z), rot=(-math.pi / 2, 0, 0), mat=I)
    a.cyl(r * 0.35, r * 0.35, w + 0.3, sides=6, loc=(x, y - w / 2 - 0.15, z), rot=(-math.pi / 2, 0, 0), mat=I)
    if bracket_top is not None:
        for sy in (-1, 1):
            a.box((0.35, 0.14, bracket_top - z), loc=(x, y + sy * (w / 2 + 0.2), (z + bracket_top) / 2), mat=I)
        a.box((0.6, w + 0.7, 0.2), loc=(x, y, bracket_top - 0.1), mat=I)


def fence(a, pts, z0, h=1.3, step=2.0):
    """Post-and-rail fence along a polyline at deck height z0."""
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        L = math.hypot(x2 - x1, y2 - y1)
        n = max(1, round(L / step))
        for i in range(n + 1):
            if i == 0 and (x1, y1) != pts[0]:
                continue
            t = i / n
            a.box((0.28, 0.28, h + 0.1), loc=(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, z0 + (h + 0.1) / 2), mat=T)
        for zz in (z0 + h * 0.5, z0 + h - 0.1):
            sq(a, (x1, y1, zz), (x2, y2, zz), 0.18, h=0.22)


def deck(a, x0, x1, y0, y1, top, fence_pts=None):
    """Plank deck on stub posts; boards run along X."""
    a.box((x1 - x0, y1 - y0, 0.3), loc=((x0 + x1) / 2, (y0 + y1) / 2, top - 0.45), mat=T)
    n = max(3, round((y1 - y0) / 0.9))
    bw = (y1 - y0) / n
    for i in range(n):
        a.box((x1 - x0 + 0.1, bw - 0.08, 0.18), loc=((x0 + x1) / 2, y0 + bw * (i + 0.5), top - 0.09), mat=T)
    for x in (x0 + 0.3, x1 - 0.3):
        for y in (y0 + 0.3, y1 - 0.3):
            a.box((0.45, 0.45, top - 0.3), loc=(x, y, (top - 0.3) / 2), mat=T)
    if fence_pts:
        fence(a, fence_pts, top)


def tufts(a, pts, r=0.9):
    for i, (x, y) in enumerate(pts):
        rr = r * (0.8 + 0.45 * ((i * 37) % 7) / 6)
        a.leaf_cluster(rr, loc=(x, y, rr * 0.55), mat=F, lobes=6, floor=0.0, seed=100 + i)


def sand(a, rx, ry, cx=0.0, cy=0.0):
    v = a.cyl(1.0, 1.0, 0.1, sides=12, loc=(0, 0, 0), mat=S)
    a.transform(v, loc=(cx, cy, 0), scale=(rx, ry, 1))


def banner(a, x, y, ztop, w=1.4, h=4.0):
    # outline in XY; rotated +90 about X so Y->Z and the extrusion goes -Y
    pts = [(-w / 2, 0), (w / 2, 0), (w / 2, -h), (0, -h - 0.7), (-w / 2, -h)]
    a.poly_prism(_ccw(pts), 0.1, loc=(x, y + 0.05, ztop), rot=(math.pi / 2, 0, 0), mat=B)
    d = 0.5
    dia = [(0, d), (-d * 0.7, 0), (0, -d), (d * 0.7, 0)]
    a.poly_prism(_ccw(dia), 0.06, loc=(x, y - 0.06, ztop - h * 0.5), rot=(math.pi / 2, 0, 0), mat=S)
    a.box((w + 0.5, 0.18, 0.18), loc=(x, y + 0.1, ztop + 0.05), mat=I)  # hanging rod


def _ccw(pts):
    s = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
            for i in range(len(pts)))
    return pts if s > 0 else pts[::-1]


def counterweight(a, x, y, z0, s=1.1, h=1.5):
    a.box((s, s, h), loc=(x, y, z0 + h / 2), mat=I, bevel=0.08)
    a.box((s * 0.4, 0.2, 0.4), loc=(x, y, z0 + h + 0.2), mat=I)


# ---------------------------------------------------------------- hero
def build_hero(fk):
    a = fk.Asset("GantryRopeLift", "W15 GantryRopeLift")
    sand(a, 7.0, 5.0, 0, 0)
    # rock mass behind the frame and to the right (kept inside ~14 x 10)
    a.rock((5.4, 3.8, 10.0), loc=(4.2, 3.0, 0), mat=R, subdiv=1, facets=22)
    a.rock((3.4, 3.4, 7.2), loc=(5.4, 0.4, 0), mat=R, subdiv=1, facets=22)
    a.rock((4.6, 3.2, 8.6), loc=(0.4, 3.4, 0), mat=R, subdiv=1, facets=22)
    a.rock((4.2, 3.0, 6.8), loc=(-4.0, 3.4, 0), mat=R, subdiv=1, facets=22)
    a.rock((2.8, 2.4, 2.8), loc=(5.4, -3.0, 0), mat=R, subdiv=1, facets=18)
    a.rock((1.6, 1.4, 1.2), loc=(3.0, -4.0, 0), mat=R, subdiv=1, facets=18)
    # footings
    footing(a, -4.5, 0, (2.9, 2.9, 2.2))
    footing(a, 4.5, 0, (3.0, 3.0, 2.6))
    # raised fenced deck on the left front (8 x 6), rails on 3 sides, steps on the right
    top = 2.4
    deck(a, -7.0, 1.0, -4.6, 1.0, top)
    fence(a, [(1.0, -4.6), (-7.0, -4.6), (-7.0, 1.0), (-5.6, 1.0)], top, h=1.1, step=2.0)
    a.box((0.8, 2.0, 1.6), loc=(1.4, -3.8, 0.8), mat=T)
    a.box((0.8, 2.0, 0.8), loc=(2.2, -3.8, 0.4), mat=T)
    # heavy uprights rising slightly above the beam
    pw = 1.8
    post(a, -4.5, 0, 1.6, 19.0, w=pw)
    for x in (-4.5, 4.5):
        a.box((pw + 0.1, pw + 0.1, 0.2), loc=(x, 0, 19.0), mat=I)   # iron post caps (read in top view)
    post(a, 4.5, 0, 2.0, 19.0, w=pw)
    # cross beam overhanging both posts
    bz = 16.9
    a.box((14.2, 1.8, 1.9), loc=(0, 0, bz), mat=T, bevel=0.08)
    for x in (-6.4, 6.4):
        plate(a, x, -0.96, bz, w=1.0, h=1.7)
        a.box((0.12, 1.6, 1.6), loc=(x + (0.75 if x > 0 else -0.75), 0, bz), mat=I)
    for x in (-4.5, 4.5):
        plate(a, x, -0.96, bz, w=1.5, h=1.7)
    # big diagonal braces
    sq(a, (-3.7, 0, 11.6), (-0.9, 0, 15.95), 1.1)
    sq(a, (3.7, 0, 11.6), (0.9, 0, 15.95), 1.1)
    # second lower horizontal rail between the posts (set back)
    a.box((7.4, 1.0, 1.1), loc=(0, 0.35, 10.8), mat=T, bevel=0.05)
    for x in (-3.5, 3.5):
        plate(a, x, -0.2, 10.8, w=0.8, h=1.0)
    # raking struts at the back
    sq(a, (-4.5, 0.7, 7.5), (-4.5, 3.0, 2.4), 0.9)
    # pulley hung on an iron hanger in front of the beam
    px, py, pz, pr = 0.0, -2.6, 14.2, 1.0
    a.box((0.9, 0.12, 1.8), loc=(px, -0.95, bz - 0.1), mat=I)
    a.box((0.7, 2.6, 0.45), loc=(px, -1.75, bz - 0.73), mat=I)        # iron jib arm out over the lift
    sq(a, (px, -0.95, bz + 0.6), (px, -2.75, bz - 0.6), 0.26, mat=I)  # arm strut
    pulley(a, px, py, pz, pr, bracket_top=bz - 0.95)
    # rope: left strand to the crate ring, right strand to the counterweight
    cx, wx = -1.25, 1.95
    rz = 12.4
    rope(a, [(cx, py, rz + 0.3), (-pr, py, pz), (-0.7, py, pz + 0.75), (0, py, pz + pr + 0.08),
             (0.7, py, pz + 0.75), (pr, py, pz), (wx, py, 9.4)], 0.18)
    crate(a, cx, py, 6.6, w=3.1, d=3.2, h=2.4, ring_z=rz)
    counterweight(a, wx, py, 7.0, s=1.5, h=2.0)
    # rope coil hung on the left post
    a.torus(0.55, 0.13, loc=(-4.5, -1.05, 8.5), rot=(math.pi / 2, 0, 0), mat=P, seg=10, rseg=4)
    # banner on the right upright
    banner(a, 4.5, -1.05, 15.7, w=1.5, h=4.4)
    # bright green tufts at rock bases and along the deck sides
    tufts(a, [(-5.8, -4.0), (-3.0, -4.1), (-0.4, -4.1), (2.4, -2.6), (4.0, -4.0), (5.9, -1.6),
              (6.0, -4.0), (3.0, 1.2), (-1.6, 1.8), (-5.8, 2.0), (6.0, 3.4), (2.0, 4.0),
              (-6.0, -1.0), (-4.2, 4.0)], r=1.0)
    return a.finish()


# ---------------------------------------------------------------- variants
def build_short_crane(fk):
    a = fk.Asset("GantryRopeLiftShortCrane", "W15 GantryRopeLiftShortCrane")
    sand(a, 5.4, 3.6, -0.5, 0)
    a.rock((2.2, 2.0, 2.0), loc=(4.2, -1.4, 0), mat=R, subdiv=1, facets=20)
    a.rock((2.0, 1.8, 2.4), loc=(-5.4, 1.6, 0), mat=R, subdiv=1, facets=20)
    # post on the right, beam reaching out to the left over a fenced deck
    a.rock((3.0, 2.8, 3.6), loc=(3.0, 0.6, 0), mat=R, subdiv=1, facets=22)
    post(a, 2.8, 0.4, 1.4, 9.0, w=1.3)
    sq(a, (4.0, 0.4, 9.5), (-4.4, 0.4, 9.5), 1.2)
    plate(a, 2.8, -0.25, 9.5, w=1.0, h=1.1)
    plate(a, -3.9, -0.25, 9.5, w=0.7, h=1.1)
    sq(a, (2.3, 0.4, 6.2), (-0.6, 0.4, 9.0), 0.7)
    # pulley block + rope
    pulley(a, -2.8, 0.4, 8.2, 0.55, w=0.5, bracket_top=8.9)
    deck(a, -5.0, 0.6, -2.0, 2.0, 0.9,
         fence_pts=[(0.6, -2.0), (-5.0, -2.0), (-5.0, 2.0)])
    rope(a, [(-2.8 + 0.55, 0.4, 8.2), (-2.25, 0.4, 5.9)], 0.13)
    rope(a, [(-2.8 - 0.55, 0.4, 8.2), (-3.4, 0.4, 3.6)], 0.11)
    crate(a, -2.2, 0.4, 2.6, w=2.4, d=2.4, h=1.7, ring_z=5.6)
    tufts(a, [(4.8, 0.4), (1.6, -2.0), (-5.6, -0.6), (3.4, -2.6), (-5.6, 2.8), (1.4, 1.8)], r=0.85)
    return a.finish()


def build_hanging_basket(fk):
    a = fk.Asset("GantryRopeLiftHangingBasket", "W15 GantryRopeLiftHangingBasket")
    sand(a, 4.6, 3.4, 0, 0)
    a.rock((3.0, 3.0, 4.0), loc=(-2.4, 0.4, 0), mat=R, subdiv=1, facets=22)
    a.rock((2.2, 2.0, 2.6), loc=(-3.8, -1.2, 0), mat=R, subdiv=1, facets=20)
    a.rock((1.8, 1.8, 1.6), loc=(2.6, 1.6, 0), mat=R, subdiv=1, facets=20)
    a.rock((1.4, 1.3, 1.1), loc=(3.4, -1.4, 0), mat=R, subdiv=1, facets=18)
    post(a, -2.4, 0.3, 2.0, 11.0, w=1.3)
    sq(a, (-3.6, 0.3, 11.5), (3.8, 0.3, 11.5), 1.2)
    plate(a, -2.4, -0.35, 11.5, w=1.0, h=1.1)
    sq(a, (-1.9, 0.3, 7.8), (0.8, 0.3, 11.0), 0.7)
    bx, by = 2.0, 0.3
    pulley(a, bx, by, 10.2, 0.55, w=0.5, bracket_top=10.9)
    a.box((0.9, 0.6, 0.8), loc=(bx, by, 9.3), mat=I, bevel=0.05)  # pulley block
    rope(a, [(bx, by, 8.9), (bx, by, 7.4)], 0.13)
    ring(a, (bx, by, 7.2), 0.28)
    # rope-woven basket: timber rims, rope bars and a rope weave ring
    z0, h, r = 3.6, 2.2, 1.35
    a.cyl(r * 0.9, r * 0.9, 0.2, sides=10, loc=(bx, by, z0), mat=T)
    a.torus(r, 0.13, loc=(bx, by, z0 + h), mat=T, seg=12, rseg=4)
    a.torus(r * 0.92, 0.12, loc=(bx, by, z0 + 0.15), mat=T, seg=12, rseg=4)
    a.torus(r * 0.97, 0.08, loc=(bx, by, z0 + h * 0.5), mat=P, seg=12, rseg=3)
    a.torus(r * 0.98, 0.07, loc=(bx, by, z0 + h * 0.78), mat=P, seg=12, rseg=3)
    a.torus(r * 0.94, 0.07, loc=(bx, by, z0 + h * 0.25), mat=P, seg=12, rseg=3)
    for i in range(10):
        ang = i * 2 * math.pi / 10
        c, s = math.cos(ang), math.sin(ang)
        rope(a, [(bx + c * r * 0.92, by + s * r * 0.92, z0 + 0.1),
                 (bx + c * r, by + s * r, z0 + h)], 0.07)
    for i in range(4):
        ang = math.pi / 4 + i * math.pi / 2
        rope(a, [(bx + math.cos(ang) * r, by + math.sin(ang) * r, z0 + h),
                 (bx, by, 7.0)], 0.07)
    tufts(a, [(-4.4, 0.6), (-0.8, -1.4), (-3.0, -2.6), (3.6, 0.4), (1.4, 2.6), (-1.0, 2.2)], r=0.85)
    return a.finish()


def build_tall_hoist(fk):
    a = fk.Asset("GantryRopeLiftTallHoist", "W15 GantryRopeLiftTallHoist")
    sand(a, 6.4, 4.4, 0, 0)
    # taller rock mass behind and left (6 rocks)
    a.rock((4.4, 3.6, 11.0), loc=(-4.4, 2.2, 0), mat=R, subdiv=1, facets=22)
    a.rock((3.2, 3.0, 7.6), loc=(-6.0, 0.0, 0), mat=R, subdiv=1, facets=22)
    a.rock((3.4, 2.6, 6.2), loc=(-1.6, 3.0, 0), mat=R, subdiv=1, facets=22)
    a.rock((2.4, 2.2, 2.6), loc=(-5.6, -2.4, 0), mat=R, subdiv=1, facets=20)
    a.rock((2.8, 2.6, 3.6), loc=(3.0, 3.0, 0), mat=R, subdiv=1, facets=22)
    a.rock((1.6, 1.5, 1.2), loc=(5.6, -2.6, 0), mat=R, subdiv=1, facets=18)
    footing(a, -3.5, 0, (2.6, 2.6, 2.2))
    footing(a, 3.5, 0, (2.6, 2.6, 2.2))
    post(a, -3.5, 0, 1.6, 23.0, w=1.5)
    post(a, 3.5, 0, 1.6, 23.0, w=1.5)
    a.box((10.6, 1.6, 1.6), loc=(0, 0, 23.7), mat=T, bevel=0.08)
    for x in (-3.5, 3.5):
        plate(a, x, -0.85, 23.7, w=1.2, h=1.4)
    sq(a, (-2.9, 0, 19.8), (-1.0, 0, 22.95), 0.85)
    sq(a, (2.9, 0, 19.8), (1.0, 0, 22.95), 0.85)
    # larger fenced middle platform on the right, between post and two outriggers
    top = 11.5
    for y in (-2.3, 2.3):
        a.box((0.9, 0.9, top), loc=(6.8, y, top / 2), mat=T)
    a.box((4.6, 5.0, 0.35), loc=(5.0, 0, top - 0.45), mat=T)
    for i in range(5):
        a.box((4.7, 0.92, 0.18), loc=(5.0, -2.0 + i * 1.0, top - 0.09), mat=T)
    fence(a, [(2.7, -2.5), (7.3, -2.5), (7.3, 2.5), (2.7, 2.5)], top, h=1.3, step=1.6)
    sq(a, (6.6, 0, 6.0), (4.2, 0, 10.9), 0.6)
    # second lower tie
    sq(a, (-3.5, 0.0, 6.0), (3.5, 0.0, 6.0), 0.85)
    # pulley + rope + hanging cargo between posts
    px = -0.6
    pulley(a, px, 0, 21.4, 0.85, w=0.6, bracket_top=22.9)
    rope(a, [(px - 0.85, 0, 21.4), (px - 0.85, 0, 13.0)], 0.14)
    rope(a, [(px + 0.85, 0, 21.4), (px + 0.85, 0, 16.2)], 0.14)
    counterweight(a, px + 0.85, 0, 14.6, s=0.9, h=1.3)
    crate(a, px - 0.85, 0, 8.6, w=2.8, d=2.6, h=2.0, ring_z=12.8)
    banner(a, -3.5, -0.8, 22.6, w=1.3, h=4.0)
    tufts(a, [(-6.2, -1.2), (-2.2, -2.0), (1.6, -2.0), (5.0, -3.0), (-4.0, -3.0), (4.8, 3.6),
              (-0.2, 2.4), (-6.4, 2.6)], r=0.95)
    return a.finish()


# ---------------------------------------------------------------- parts
def build_parts(fk):
    out = []
    a = fk.Asset("GantryRopeLiftCrossBeam", "W15 GantryRopeLiftCrossBeam")
    a.box((12.0, 1.6, 1.6), loc=(0, 0, 0.8), mat=T, bevel=0.08)
    for x in (-5.3, 5.3):
        plate(a, x, -0.86, 0.8, w=1.0, h=1.4)
        a.box((0.12, 1.4, 1.4), loc=(x + (0.64 if x > 0 else -0.64), 0, 0.8), mat=I)
    out.append(a.finish())

    a = fk.Asset("GantryRopeLiftUprightPost", "W15 GantryRopeLiftUprightPost")
    a.box((2.8, 2.8, 2.0), loc=(0, 0, 1.0), mat=R, bevel=0.25)
    post(a, 0, 0, 1.9, 14.0, w=1.6)
    out.append(a.finish())

    a = fk.Asset("GantryRopeLiftDiagonalBrace", "W15 GantryRopeLiftDiagonalBrace")
    # angled beam with horizontal notched ends (parallelogram profile in XZ)
    w, L = 1.0, 5.0
    cx, cy = L * math.cos(math.radians(32)), L * math.sin(math.radians(32))
    W, D = cx + 1.2, cy + 1.0
    prof = [(0, 0), (1.2, 0), (W, cy), (W, D), (cx, D), (0, 1.0)]
    # laid flat (profile in XY, extruded up) at a shallow angle so the parts grid shows it
    # in front of the beam row, clear of the crate
    a.poly_prism(_ccw([(x - W / 2, y - D / 2) for x, y in prof]), w, loc=(0, 0, 0), mat=T)
    for bx, by in ((-W / 2 + 0.6, -D / 2 + 0.5), (W / 2 - 0.6, D / 2 - 0.5)):
        a.box((0.26, 0.26, 0.14), loc=(bx, by, w + 0.05), mat=I)   # bolt heads at the notched ends
    out.append(a.finish())

    a = fk.Asset("GantryRopeLiftPulleyWheel", "W15 GantryRopeLiftPulleyWheel")
    pulley(a, 0, 0, 1.05, 1.0, w=0.8, bracket_top=2.6)
    out.append(a.finish())

    a = fk.Asset("GantryRopeLiftThickRope", "W15 GantryRopeLiftThickRope")
    pts = []
    turns, n = 3, 12
    for i in range(turns * n + 1):
        t = i / n * 2 * math.pi
        pts.append((0.65 * math.sin(t), -0.25 + 0.18 * i / n, 1.25 + 0.95 * math.cos(t)))
    pts.append((0.0, 0.3, 0.2))
    a.tube_loop(pts, 0.17, mat=P, rseg=5, closed=False)
    a.box((0.5, 0.7, 0.35), loc=(0, 0.05, 2.25), mat=P)  # binding wrap at the top
    out.append(a.finish())

    a = fk.Asset("GantryRopeLiftCargoPlatform", "W15 GantryRopeLiftCargoPlatform")
    crate(a, 0, 0, 0, w=4.0, d=4.0, h=2.5, ring_z=5.0)
    out.append(a.finish())
    return out


def build(kit):
    fk = kit.flintkit
    res = []
    hero = build_hero(fk)
    res.append(kit.tag(hero, "hero", collision="precise", budget=8000,
                       notes="Timber gantry crane with pulley, rope lift crate, counterweight, fenced deck, "
                             "banner, rock mass. Precise: deck and rocks walkable. No VFX."))
    for p in build_parts(fk):
        res.append(kit.tag(p, "part", collision="box", budget=1500, notes="GantryRopeLift part"))
    for fn, note in ((build_short_crane, "Short single-upright crane over a fenced deck"),
                     (build_hanging_basket, "Single upright with rope-woven basket on a pulley block"),
                     (build_tall_hoist, "Two-storey scaffold hoist with fenced mid deck, banner, cargo")):
        res.append(kit.tag(fn(fk), "variant", collision="precise", budget=6000, notes=note))
    return res
