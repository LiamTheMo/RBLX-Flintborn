"""W11 row 1: TableSeating - planked trestle picnic table, benches, stool, workbench."""
import math

SUBJECT = "TableSeating"
ROW = 1
HERO_AZIMUTH = -22

PALETTE = {
    # Sheet value is ("#B5702C", 0.9, 0, 0); it renders lighter and more saturated than the
    # reference honey-brown, so this module overrides it (verifier fix). See shared_lib_requests.
    "w11_wood": ("#A2622A", 0.9, 0, 0),  # all planks, posts, logs, staves, poles, handles (one wood colour; planks end grain too)
    "w11_iron": ("#40444F", 0.6, 0.3, 0),  # hoops, straps, nail heads, cauldron, brazier/torch brackets, post base plate, lantern frame
}

W = "w11_wood"
IRON = "w11_iron"
TX = 3.6  # trestle x: reference iso shows the A-frames close to the table ends


def seg(a, p1, p2, t_out, t_in, plane):
    """Square timber between two points lying in the xz or yz plane.
    t_out = thickness out of the plane, t_in = in-plane thickness."""
    (x1, y1, z1), (x2, y2, z2) = p1, p2
    c = ((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2)
    if plane == "xz":
        dx, dz = x2 - x1, z2 - z1
        L = math.hypot(dx, dz)
        return a.plank((L, t_out, t_in), c, (0, -math.atan2(dz, dx), 0), mat=W)
    dy, dz = y2 - y1, z2 - z1
    L = math.hypot(dy, dz)
    return a.plank((t_out, L, t_in), c, (math.atan2(dz, dy), 0, 0), mat=W)


def nail(a, loc, face="top", r=0.11, h=0.07):
    rot = {"top": (0, 0, 0), "-y": (math.pi / 2, 0, 0), "+y": (-math.pi / 2, 0, 0),
           "-x": (0, -math.pi / 2, 0), "+x": (0, math.pi / 2, 0)}[face]
    a.cyl(r, r * 0.9, h, sides=6, loc=loc, rot=rot, mat=IRON, cap=True)


def clamp(a):
    for v in a.bm.verts:
        if v.co.z < 0:
            v.co.z = 0.0


def table_top(a, z0, length=10.0, th=0.9):
    """4 planks along x, top surface at z0 + th."""
    pitch, width = 1.14, 1.04
    offs = [(-0.08, 0.0), (0.06, -0.15), (-0.03, 0.1), (0.1, -0.05)]
    for i, (dx, dl) in enumerate(offs):
        y = (i - 1.5) * pitch
        a.plank((length + dl, width, th), (dx, y, z0 + th / 2), (0, 0, 0.004 * (i - 1.5)),
                mat=W, bevel=0.07)
        for xs in (-TX, TX):
            nail(a, (xs + dx, y, z0 + th), "top")


def trestle(a, c, axis, top_z=2.3, nail_face=None, leg_t=1.0):
    """A-frame trestle centred at c (along x or y); legs span along `axis`.
    Top cleat 4 long, splayed legs, diagonal brace, foot pads."""
    plane = "yz" if axis == "y" else "xz"

    def P(u, z):
        return (c, u, z) if axis == "y" else (u, c, z)

    cleat_z = top_z - 0.25
    if axis == "y":
        a.plank((leg_t, 4.1, 0.5), (c, 0, cleat_z), mat=W, bevel=0.06)
    else:
        a.plank((4.1, leg_t, 0.5), (0, c, cleat_z), mat=W, bevel=0.06)
    for s in (-1, 1):
        seg(a, P(s * 1.55, 0.0), P(s * 0.75, top_z - 0.45), leg_t, 0.8, plane)
        fu = s * 1.55
        if axis == "y":
            a.plank((leg_t + 0.12, 0.9, 0.36), (c, fu, 0.18), mat=W, bevel=0.05)
        else:
            a.plank((0.9, leg_t + 0.12, 0.36), (fu, c, 0.18), mat=W, bevel=0.05)
    # diagonal brace foot-left to top-right, in the leg plane, proud of the legs
    seg(a, P(-1.3, 0.45), P(0.95, top_z - 0.55), leg_t + 0.1, 0.55, plane)
    if nail_face:
        off = leg_t / 2 + 0.05
        sign = -1 if nail_face.startswith("-") else 1
        for u, z in ((-1.1, cleat_z), (1.1, cleat_z), (-1.3, 0.5), (0.95, top_z - 0.6)):
            if axis == "y":
                nail(a, (c + sign * off, u, z), nail_face)
            else:
                nail(a, (u, c + sign * off, z), nail_face)


def bench(a, y, length=10.0, legx=4.0, seat_top=1.7, depth=1.4, th=0.7, splay=0.0, nails=True):
    """Two-plank seat on two chunky end legs."""
    pw = depth / 2 - 0.04
    for i, s in enumerate((-1, 1)):
        a.plank((length - 0.08 * i, pw, th), (0.05 * s, y + s * depth / 4, seat_top - th / 2),
                mat=W, bevel=0.06)
    leg_h = seat_top - th
    for xs in (-legx, legx):
        if splay:
            sx = 1 if xs > 0 else -1
            seg(a, (xs + sx * splay, y, -0.1), (xs, y, leg_h + 0.05), depth - 0.15, 0.8, "xz")
        else:
            a.plank((0.8, depth - 0.15, leg_h + 0.05), (xs, y, leg_h / 2), mat=W, bevel=0.06)
        if nails:
            for s in (-1, 1):
                nail(a, (xs, y + s * depth / 4, seat_top), "top")


def build(kit):
    fk = kit.flintkit
    out = []

    # ---------------- HERO ----------------
    a = fk.Asset("TableSeating", "W11 TableSeating")
    table_top(a, 2.3)
    trestle(a, -TX, "y", nail_face="-x")
    trestle(a, TX, "y", nail_face="+x")
    # chunky crossbar along x at ~1.1, ends poke through the trestles as tenons
    a.plank((2 * TX + 1.4, 0.75, 0.8), (0, 0, 1.1), mat=W, bevel=0.07)
    for s in (-1, 1):
        nail(a, (s * TX, -0.38, 1.1), "-y")
        # front-view diagonal braces from crossbar up to the cleats
        seg(a, (s * 0.9, 0, 1.3), (s * (TX - 0.3), 0, 2.15), 0.5, 0.45, "xz")
    for y in (-3.7, 3.7):  # reference top view shows a clear gap between table and benches
        bench(a, y, seat_top=1.3, th=0.65, legx=4.1)
    clamp(a)
    o = a.finish()
    out.append(kit.tag(o, "hero", collision="precise", budget=4000,
                       notes="Trestle picnic table with two benches; walkable top/benches -> precise. No VFX."))

    # ---------------- PARTS ----------------
    a = fk.Asset("TableSeatingTableTop", "W11 TableSeating part")
    table_top(a, 0.0)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500, notes="4-plank table top"))

    a = fk.Asset("TableSeatingTrestleLeg", "W11 TableSeating part")
    trestle(a, 0.0, "x", top_z=3.2, nail_face="-y")
    clamp(a)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500,
                       notes="A-frame trestle leg with diagonal brace (use two per table)"))

    a = fk.Asset("TableSeatingCrossbar", "W11 TableSeating part")
    a.plank((6.0, 0.8, 0.8), (0, 0, 0.4), mat=W, bevel=0.07)
    for s in (-1, 1):  # end tenons
        a.plank((0.5, 0.5, 0.5), (s * 3.2, 0, 0.4), mat=W, bevel=0.04)
        nail(a, (s * 2.6, -0.4, 0.4), "-y")
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500, notes="Long crossbar beam with end tenons"))

    a = fk.Asset("TableSeatingBenchSeat", "W11 TableSeating part")
    for i, s in enumerate((-1, 1)):
        a.plank((10.0 - 0.08 * i, 0.66, 0.7), (0.05 * s, s * 0.35, 0.35), mat=W, bevel=0.06)
        for xs in (-4.0, 4.0):
            nail(a, (xs, s * 0.35, 0.7), "top")
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500, notes="Two-plank bench seat board"))

    # ---------------- VARIATIONS ----------------
    # Stool
    a = fk.Asset("TableSeatingStool", "W11 TableSeating variant")
    a.plank((1.8, 1.8, 0.45), (0, 0, 2.0 - 0.225), mat=W, bevel=0.06)
    for sx in (-1, 1):
        for sy in (-1, 1):
            seg(a, (sx * 0.82, sy * 0.66, 0.0), (sx * 0.5, sy * 0.66, 1.6), 0.34, 0.34, "xz")
            nail(a, (sx * 0.6, sy * 0.6, 2.0), "top", r=0.05, h=0.05)
    for sy in (-1, 1):
        a.plank((1.4, 0.22, 0.24), (0, sy * 0.66, 0.5), mat=W, bevel=0.03)
    for sx in (-1, 1):
        a.plank((0.22, 1.3, 0.24), (sx * 0.7, 0, 0.7), mat=W, bevel=0.03)
    clamp(a)
    o = a.finish()
    out.append(kit.tag(o, "variant", collision="box", budget=3000, notes="Square stool, splayed legs"))

    # Long bench
    a = fk.Asset("TableSeatingLongBench", "W11 TableSeating variant")
    bench(a, 0.0, length=7.0, legx=2.6, seat_top=2.0, depth=1.6, th=0.8, splay=0.25)
    clamp(a)
    o = a.finish()
    out.append(kit.tag(o, "variant", collision="box", budget=3000, notes="Long bench on splayed chunky end legs"))

    # Workbench
    a = fk.Asset("TableSeatingWorkbench", "W11 TableSeating variant")
    for i in range(3):
        y = (i - 1) * 0.93
        a.plank((6.0 - 0.1 * (i % 2), 0.89, 0.55), (0.04 * (i - 1), y, 2.925), mat=W, bevel=0.06)
        for xs in (-2.55, 2.55):
            nail(a, (xs, y, 3.2), "top")
    px, py = 2.55, 1.1
    for sx in (-1, 1):
        a.plank((0.55, 0.55, 2.65), (sx * px, -py, 1.325), mat=W, bevel=0.05)  # front posts
        a.plank((0.55, 0.55, 4.75), (sx * px, py, 2.375), mat=W, bevel=0.05)  # back posts
        a.plank((0.72, 0.72, 0.25), (sx * px, py, 4.875), mat=W, bevel=0.05)  # post caps
        nail(a, (sx * px, py - 0.28, 4.3), "-y")
        # side X braces (yz plane), thick so they read, set proud of the posts
        xo = sx * (px + 0.2)
        seg(a, (xo, -py + 0.1, 0.35), (xo, py - 0.1, 2.55), 0.3, 0.4, "yz")
        seg(a, (xo + sx * 0.05, -py + 0.1, 2.55), (xo + sx * 0.05, py - 0.1, 0.35), 0.3, 0.4, "yz")
        nail(a, (sx * (px + 0.26), 0, 1.45), "+x" if sx > 0 else "-x")
        a.plank((0.4, 2.2, 0.35), (sx * px, 0, 1.0), mat=W, bevel=0.04)  # shelf rail
    a.plank((5.3, 2.3, 0.25), (0, 0, 1.3), mat=W, bevel=0.04)  # shelf plank
    clamp(a)
    o = a.finish()
    out.append(kit.tag(o, "variant", collision="precise", budget=3000,
                       notes="Workbench with two capped tall back posts, shelf, X braces"))
    return out
