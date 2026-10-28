"""W15 row 3: Minecart (wooden ore cart).

Axes: the cart's length runs along Y (track direction, so wheels sit on rails
that run along Y). Front = -Y (coupling block), rear = +Y (U-handle).
"""
import math

SUBJECT = "Minecart"
ROW = 3
HERO_AZIMUTH = -62      # reference draws the cart from the front-right, long side dominant
SIDE_AZIMUTH = 90

PALETTE = {
    "w15_timber": ("#A9662B", 0.85, 0, 0),
    "w15_iron": ("#454B66", 0.5, 0.4, 0),
    "w15_rock": ("#8E8E96", 0.95, 0, 0),
    "w15_sand": ("#D4B98E", 1, 0, 0),
    "w15_ore": ("#33468A", 0.6, 0.1, 0),
}

T = "w15_timber"
I = "w15_iron"

# body dimensions (studs)
ZB = 1.1         # bottom of side planks
ZT = 3.8         # rim
XB, XT = 1.2, 1.6     # inner half-width at bottom / top
YB, YT = 2.45, 2.85   # inner half-length at bottom / top
TH = 0.26        # plank thickness
GAP = 0.28      # plank seam groove
LEAN = 0.16       # clapboard lean: each plank's bottom edge stands proud
PB = 0.1        # plank edge bevel so each seam catches light
PTINT = (1.05, 0.94, 1.01)   # small per-plank variation (within +/-7%)
WX0, WX1 = 1.8, 2.45  # wheel inner/outer x (0.8 thick, outside the body)
WY = 1.85        # wheel y positions (+/-)
WR = 1.1        # wheel radius (centre z = WR)

TILT_X = math.atan((XT - XB) / (ZT - ZB))
TILT_Y = math.atan((YT - YB) / (ZT - ZB))


def _xin(z):
    return XB + (XT - XB) * (z - ZB) / (ZT - ZB)


def _yin(z):
    return YB + (YT - YB) * (z - ZB) / (ZT - ZB)


class Rec:
    """Records verts of every primitive so a whole cart can be moved at once."""

    def __init__(self, a):
        self.a = a
        self.verts = []

    def __getattr__(self, name):
        fn = getattr(self.a, name)

        def call(*args, **kw):
            v = fn(*args, **kw)
            if v:
                self.verts.extend(v)
            return v
        return call


def wheel(r, cx, cy, cz, side, hub=True):
    """Wheel with axis along X; `side` +1/-1 is the outward direction."""
    rot = (0, side * math.pi / 2, 0)
    r.cyl(WR, WR, WX1 - WX0, sides=10, loc=(side * WX0, cy, cz), rot=rot, mat=I)
    if hub:
        r.cyl(0.42, 0.36, 0.14, sides=8, loc=(side * WX1, cy, cz), rot=rot, mat=T)
        r.cyl(0.13, 0.13, 0.07, sides=6, loc=(side * (WX1 + 0.14), cy, cz), rot=rot, mat=I)


def side_panel(r, s, broken=False):
    """3 tapered horizontal planks on the x = s side."""
    h = (ZT - ZB) / 3
    for k in range(3):
        zc = ZB + (k + 0.5) * h
        x = s * (_xin(zc) + TH / 2)
        L = 2 * (_yin(zc) + TH) + 0.02
        if broken and k == 2:
            continue                       # top plank torn off
        if broken and k == 1:
            # cracked middle plank: two short pieces, one sagging
            r.box((TH, L * 0.45, h - GAP), loc=(x, -L * 0.27, zc), rot=(0, s * (TILT_X - LEAN), 0),
                  mat=T, bevel=PB, tint=PTINT[k])
            r.box((TH, L * 0.35, h - GAP), loc=(x, L * 0.32, zc - 0.12),
                  rot=(0.18, s * (TILT_X - LEAN), 0), mat=T, bevel=PB, tint=PTINT[k])
            continue
        r.box((TH, L, h - GAP), loc=(x, 0, zc), rot=(0, s * (TILT_X - LEAN), 0), mat=T,
              bevel=PB, tint=PTINT[k])
    # inner backing board so the seams read as grooves, not see-through slots
    zc = (ZB + ZT) / 2
    if not broken:
        r.box((0.04, 2 * _yin(zc), ZT - ZB - 0.1), loc=(s * (_xin(zc) + 0.02), 0, zc),
              rot=(0, s * TILT_X, 0), mat=T)
        # horizontal iron band across the middle plank, with 2 bolt heads
        zm = ZB + 1.5 * h
        xm = s * (_xin(zm) + TH + 0.04)
        r.box((0.12, 2 * _yin(zm) - 0.9, 0.3), loc=(xm, 0, zm), rot=(0, s * TILT_X, 0), mat=I,
              bevel=0.02)
        for yb in (-0.9, 0.9):
            r.box((0.12, 0.18, 0.18), loc=(xm + s * 0.08, yb, zm), mat=I)


def end_panel(r, e):
    h = (ZT - ZB) / 3
    for k in range(3):
        zc = ZB + (k + 0.5) * h
        y = e * (_yin(zc) + TH / 2)
        L = 2 * _xin(zc)
        r.box((L, TH, h - GAP), loc=(0, y, zc), rot=(-e * (TILT_Y - LEAN), 0, 0), mat=T,
              bevel=PB, tint=PTINT[k])
    zc = (ZB + ZT) / 2
    r.box((2 * _xin(zc), 0.04, ZT - ZB - 0.1), loc=(0, e * (_yin(zc) + 0.02), zc),
          rot=(-e * TILT_Y, 0, 0), mat=T)


def corner(r, s, e, missing_plate=False):
    """Corner post + iron corner plates with bolts + strap down the post."""
    xb, yb = s * (XB + TH * 0.9), e * (YB + TH * 0.9)
    xt, yt = s * (XT + TH * 0.9), e * (YT + TH * 0.9)
    zb, zt = ZB - 0.05, ZT + 0.06
    rot = (-math.atan2(yt - yb, zt - zb), math.atan2(xt - xb, zt - zb), 0)
    r.box((0.36, 0.36, zt - zb), loc=((xb + xt) / 2, (yb + yt) / 2, (zb + zt) / 2), rot=rot,
          mat=T, bevel=0.04)
    if missing_plate:
        return
    # side-face plate (normal +-X) and end-face plate (normal +-Y)
    zc = ZT - 0.5
    xo = s * (_xin(zc) + TH + 0.1)
    yo = e * (_yin(zc) + TH + 0.1)
    pw = 1.05
    r.box((0.12, pw, 1.1), loc=(xo + s * 0.04, yo - e * (pw / 2 - 0.16), zc),
          rot=(0, s * TILT_X, 0), mat=I, bevel=0.03)
    r.box((pw, 0.12, 1.1), loc=(xo - s * (pw / 2 - 0.16), yo + e * 0.04, zc),
          rot=(-e * TILT_Y, 0, 0), mat=I, bevel=0.03)
    # cap over the corner top
    r.box((0.62, 0.62, 0.14), loc=(xo - s * 0.15, yo - e * 0.15, ZT + 0.1), mat=I, bevel=0.03)
    # straps running down the side face and the end face to the bottom
    zs = (ZB - 0.2 + zc) / 2
    r.box((0.08, 0.36, zc - ZB + 0.2), loc=(s * (_xin(zs) + TH + 0.1), yo - e * 0.3, zs),
          rot=(0, s * TILT_X, 0), mat=I)
    r.box((0.36, 0.08, zc - ZB + 0.2), loc=(xo - s * 0.3, e * (_yin(zs) + TH + 0.1), zs),
          rot=(-e * TILT_Y, 0, 0), mat=I)
    # bolt heads
    for dz in (0.26, -0.26):
        z = zc + dz
        r.box((0.14, 0.2, 0.2), loc=(s * (_xin(z) + TH + 0.22), yo - e * 0.6, z), mat=I)
        r.box((0.2, 0.14, 0.2), loc=(xo - s * 0.6, e * (_yin(z) + TH + 0.22), z), mat=I)


def floor_and_chassis(r, missing=None):
    # base floor: 4 planks along Y
    w = 2 * XB / 4
    for i in range(4):
        x = -XB + w * (i + 0.5)
        r.plank((w - 0.02, 2 * YB + 0.1, 0.38), loc=(x, 0, ZB + 0.19), mat=T)
    # long timber sills under each side, visible below the body in the side view
    for s in (-1, 1):
        r.box((0.42, 2 * YB + 0.4, 0.4), loc=(s * (XB - 0.12), 0, ZB - 0.12), mat=T, bevel=0.05)
    # axle beams (timber) and iron axles
    for e in (-1, 1):
        y = e * WY
        # thick timber axle beam, full width between the wheels, at wheel-centre height
        r.box((2 * WX0 - 0.06, 0.62, 0.55), loc=(0, y, WR - 0.02), mat=T, bevel=0.06)
        for s in (-1, 1):
            if missing == (s, e):
                r.cyl(0.17, 0.17, WX0 - XB + 0.1, sides=6, loc=(s * XB, y, WR),
                      rot=(0, s * math.pi / 2, 0), mat=I)
                continue
            r.cyl(0.17, 0.17, WX1 + 0.05, sides=6, loc=(0, y, WR),
                  rot=(0, s * math.pi / 2, 0), mat=I, cap=True)
            wheel(r, 0, y, WR, s)


def handle(r):
    y = YT + TH + 0.12
    z0 = ZT - 0.7
    pts = [(-1.2, y, z0), (-1.2, y, ZT + 0.35), (-1.0, y, ZT + 0.55), (1.0, y, ZT + 0.55),
           (1.2, y, ZT + 0.35), (1.2, y, z0)]
    r.tube_loop(pts, 0.11, mat=I, rseg=6, closed=False)
    for x in (-1.2, 1.2):
        r.box((0.34, 0.2, 0.3), loc=(x, y - 0.05, z0 + 0.05), mat=I)
        r.box((0.34, 0.2, 0.3), loc=(x, y - 0.03, ZT - 0.05), mat=I)


def coupling(r):
    y = -(YB + TH)
    r.box((0.9, 0.55, 0.6), loc=(0, y - 0.25, ZB + 0.2), mat=T, bevel=0.05)
    r.box((0.7, 0.1, 0.45), loc=(0, y - 0.56, ZB + 0.2), mat=I)
    r.box((0.16, 0.08, 0.16), loc=(0, y - 0.64, ZB + 0.2), mat=I)


def cart(r, broken=False, missing=None):
    floor_and_chassis(r, missing=missing)
    for s in (-1, 1):
        side_panel(r, s, broken=broken and s == -1)
    for e in (-1, 1):
        end_panel(r, e)
    for s in (-1, 1):
        for e in (-1, 1):
            corner(r, s, e, missing_plate=broken and s == -1 and e == -1)
    handle(r)
    coupling(r)


def ore_heap(a):
    chunks = [
        (0.0, 0.0, 4.4, 1.05), (-0.75, -1.2, 4.0, 0.7), (0.8, -1.1, 4.15, 0.88),
        (-0.8, 1.15, 4.1, 0.92), (0.75, 1.25, 4.0, 0.62), (0.1, -1.95, 3.85, 0.5),
        (0.05, 1.95, 3.9, 0.72), (-1.0, 0.05, 3.85, 0.55), (0.95, 0.1, 4.0, 0.78),
    ]
    for i, (x, y, z, rad) in enumerate(chunks):
        a.ico((rad, rad * 0.9, rad * 0.8), loc=(x, y, z), rot=(0.4 * i, 0.7 * i, 1.1 * i),
              mat="w15_ore", subdiv=1, jitter=0.08)
    # fill under the heap so it reads as a full load
    a.box((2 * XT - 0.1, 2 * YT - 0.1, 0.5), loc=(0, 0, ZT - 0.4), mat="w15_ore", jitter=0.05)


def build(kit):
    fk = kit.flintkit
    out = []

    # ---- hero -----------------------------------------------------------
    a = fk.Asset("Minecart", "W15 Minecart")
    cart(Rec(a))
    o = a.finish()
    out.append(kit.tag(o, "hero", collision="box", budget=3500,
                       notes="Wooden ore cart; length along Y (rails along Y), front -Y coupling, rear +Y handle."))

    # ---- parts ----------------------------------------------------------
    h = (ZT - ZB) / 3
    a = fk.Asset("MinecartSidePanel", "W15 Minecart")
    a.box((4.9, 0.04, 3 * h - 0.1), loc=(0, TH / 2 - 0.02, 1.5 * h), mat=T)   # backing
    for k in range(3):
        a.box((5.0, TH, h - GAP), loc=(0, 0, (k + 0.5) * h), rot=(LEAN, 0, 0), mat=T, bevel=PB,
              tint=PTINT[k])
    for x in (-2.3, 2.3):
        a.box((0.4, 0.08, 3 * h), loc=(x, -TH / 2 - 0.04, 1.5 * h), mat=I, bevel=0.02)
        for z in (0.5, 1.5, 2.4):
            a.box((0.15, 0.1, 0.15), loc=(x, -TH / 2 - 0.12, z * h), mat=I)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="3-plank side panel with iron end straps"))

    a = fk.Asset("MinecartEndPanel", "W15 Minecart")
    a.box((3.4, 0.04, 3 * h - 0.1), loc=(0, TH / 2 - 0.02, 1.5 * h), mat=T)
    for k in range(3):
        a.box((3.5, TH, h - GAP), loc=(0, 0, (k + 0.5) * h), rot=(LEAN, 0, 0), mat=T, bevel=PB,
              tint=PTINT[k])
    for x in (-1.3, 1.3):
        a.plank((0.35, 0.25, 3 * h - 0.1), loc=(x, TH / 2 + 0.12, 1.5 * h), mat=T)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="3-plank end panel with back battens"))

    a = fk.Asset("MinecartHandle", "W15 Minecart")
    pts = [(-1.2, 0, 0.15), (-1.2, 0, 1.25), (-1.0, 0, 1.47), (1.0, 0, 1.47), (1.2, 0, 1.25), (1.2, 0, 0.15)]
    a.tube_loop(pts, 0.11, mat=I, rseg=6, closed=False)
    for x in (-1.2, 1.2):
        a.box((0.34, 0.24, 0.3), loc=(x, 0.0, 0.15), mat=I)
        a.box((0.34, 0.24, 0.3), loc=(x, 0.0, 0.75), mat=I)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="U-shaped iron end handle"))

    a = fk.Asset("MinecartBasePlank", "W15 Minecart")
    for x in (-1.75, 1.75):
        pass
    for y in (-1.6, 1.6):
        a.box((3.6, 0.5, 0.3), loc=(0, y, 0.15), mat=T, bevel=0.04)
    w = 3.5 / 4
    for i in range(4):
        a.plank((w - 0.03, 5.0, 0.38), loc=(-1.75 + w * (i + 0.5), 0, 0.3 + 0.19), mat=T)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="4-plank floor with 2 cross runners"))

    a = fk.Asset("MinecartWheel", "W15 Minecart")
    rot = (-math.pi / 2, 0, 0)     # axis along -Y, face toward the front camera
    a.cyl(WR, WR, 0.56, sides=10, loc=(0, -0.28, WR), rot=rot, mat=I)
    a.cyl(0.44, 0.38, 0.1, sides=8, loc=(0, -0.38, WR), rot=rot, mat=T)
    a.cyl(0.13, 0.13, 0.05, sides=6, loc=(0, -0.43, WR), rot=rot, mat=I)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="10-sided iron wheel with timber hub"))

    a = fk.Asset("MinecartAxle", "W15 Minecart")
    rx = (0, math.pi / 2, 0)
    a.cyl(0.17, 0.17, 4.8, sides=8, loc=(-2.4, 0, 0.3), rot=rx, mat=I)
    for x in (-2.4, 2.0):
        a.cyl(0.3, 0.3, 0.4, sides=8, loc=(x, 0, 0.3), rot=rx, mat=I)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="iron axle rod with end collars"))

    a = fk.Asset("MinecartMetalBand", "W15 Minecart")
    a.box((1.0, 0.2, 2.8), loc=(0, 0, 1.4), mat=I, bevel=0.03)
    a.box((1.0, 0.5, 0.12), loc=(0, 0.15, 2.74), mat=I)     # bent top lip
    for z in (0.4, 1.4, 2.3):
        for x in (-0.3, 0.3):
            a.box((0.16, 0.1, 0.16), loc=(x, -0.13, z), mat=I)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="bolted iron corner band"))

    # ---- variants -------------------------------------------------------
    a = fk.Asset("MinecartEmpty", "W15 Minecart")
    cart(Rec(a))
    r = a
    r.box((2.6, 0.22, 0.3), loc=(0, -(YB + TH) - 0.62, ZB + 0.2), mat=I)   # front bumper bar
    out.append(kit.tag(a.finish(), "variant", collision="box", budget=4000, notes="Empty Cart: hero cart with front bumper bar"))

    a = fk.Asset("MinecartLoaded", "W15 Minecart")
    cart(Rec(a))
    ore_heap(a)
    out.append(kit.tag(a.finish(), "variant", collision="box", budget=4000, notes="Loaded Cart: ore heaped above the rim"))

    a = fk.Asset("MinecartBroken", "W15 Minecart")
    sand = 0.06
    rads = (4.6, 4.1, 4.9, 4.3, 4.7, 3.9, 4.8, 4.4, 4.2, 4.9, 4.0, 4.6, 4.5, 4.1)
    pts = [(rr * math.cos(2 * math.pi * i / len(rads)), rr * math.sin(2 * math.pi * i / len(rads)))
           for i, rr in enumerate(rads)]
    a.poly_prism(pts, sand, loc=(0, 0.3, 0), mat="w15_sand")   # ~9-stud irregular sand pool
    r = Rec(a)
    cart(r, broken=True, missing=(-1, -1))   # camera-facing (-X) side is the wrecked one
    r.verts = [v for v in dict.fromkeys(r.verts) if v.is_valid]
    a.transform(r.verts, rot=(0.14, -0.3, 0))
    zmin = min(v.co.z for v in r.verts)
    a.transform(r.verts, loc=(0.5, 0.4, sand - zmin))
    # detached wheel lying flat at front-right
    a.cyl(WR, WR, 0.45, sides=10, loc=(-2.6, -2.6, sand), mat=I)
    a.cyl(0.42, 0.36, 0.14, sides=8, loc=(-2.6, -2.6, sand + 0.45), mat=T)
    # fallen planks
    a.plank((2.6, 0.9, 0.24), loc=(0.4, -3.4, sand + 0.12), rot=(0, 0, -0.35), mat=T)
    a.plank((2.2, 0.9, 0.24), loc=(-3.2, 0.8, sand + 0.12), rot=(0, 0, -1.2), mat=T)
    # two grey rocks
    a.rock((1.3, 1.1, 0.9), loc=(2.4, -2.6, sand), rot=(0, 0, 0.4), mat="w15_rock", subdiv=1)
    a.rock((1.1, 1.0, 0.8), loc=(-2.6, 2.8, sand), rot=(0, 0, 1.1), mat="w15_rock", subdiv=1)
    out.append(kit.tag(a.finish(), "variant", collision="hull", budget=4000,
                       notes="Broken Cart: tilted, front-left wheel lying detached, cracked side, fallen planks, sand patch"))
    return out
