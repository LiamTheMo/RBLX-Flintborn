"""W09 row 4: WayfindingPost - timber signpost on a rock footing, its parts and variations."""
import math
import random

SUBJECT = "WayfindingPost"
ROW = 4
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 90

PALETTE = {
    "w09_boulder": ("#8C8E98", 0.9, 0, 0),  # cool grey rocks, footings, stray stones (all rows)
    "w09_foliage": ("#3F9A2C", 0.9, 0, 0),  # leafy plant blades and bushes round the bases
    "w09_petal": ("#F7F3E6", 0.8, 0, 0),  # small white daisy petals
    "w09_flower_eye": ("#F0BE2A", 0.8, 0, 0),  # daisy centres
    "w09_wood": ("#B3622B", 0.85, 0, 0),  # orange-brown timber posts, rails, boards, crosspieces
    "w09_wood_end": ("#7B5A45", 0.9, 0, 0),  # cut end grain, nail notches and cap undersides
    "w09_rope": ("#CFAE6E", 1, 0, 0),  # hemp rope lashings and ties
    "w09_banner_red": ("#DC2F2A", 0.7, 0, 0),  # trail gateway banner cloth
    "w09_banner_emblem": ("#F4E6D2", 0.7, 0, 0),  # banner diamond emblem
}

WOOD, END, ROPE, ROCK, LEAF = "w09_wood", "w09_wood_end", "w09_rope", "w09_boulder", "w09_foliage"
R90 = math.pi / 2


# ---------------------------------------------------------------- helpers
def flatten(a):
    """Nothing below z=0: flatten buried undersides."""
    for v in a.bm.verts:
        if v.co.z < 0:
            v.co.z = 0.0


def coil(a, x0, x1, y0, y1, z, t=0.12, tilt=0.0, tilty=0.0):
    """One rope loop hugging a rectangle (chamfered corners); tilt raises the +X side,
    tilty the +Y side."""
    c = t * 0.7
    xa, xb, ya, yb = x0 - c, x1 + c, y0 - c, y1 + c
    k = t * 1.2
    pts2 = [(xa + k, ya), (xb - k, ya), (xb, ya + k), (xb, yb - k),
            (xb - k, yb), (xa + k, yb), (xa, yb - k), (xa, ya + k)]
    w = max(xb - xa, 1e-3)
    d = max(yb - ya, 1e-3)
    pts = [(x, y, z + tilt * ((x - xa) / w - 0.5) + tilty * ((y - ya) / d - 0.5))
           for x, y in pts2]
    return a.tube_loop(pts, t, mat=ROPE, rseg=4)


def coils(a, half, z0, n, gap=0.24, t=0.12, cx=0.0, cy=0.0):
    for i in range(n):
        coil(a, cx - half, cx + half, cy - half, cy + half, z0 + i * gap, t)


def x_lash(a, half, zc, d=0.55, t=0.16, cx=0.0, cy=0.0, y0=None, y1=None, wraps=True):
    """Crossed diagonal rope loops round a post: tilted along X and Y together, so an X
    reads on the front, back and both sides. Optional straight wraps above and below."""
    ya = cy - half if y0 is None else y0
    yb = cy + half if y1 is None else y1
    x0, x1 = cx - half, cx + half
    coil(a, x0, x1, ya, yb, zc, t, tilt=2 * d, tilty=2 * d)
    coil(a, x0, x1, ya, yb, zc, t, tilt=-2 * d, tilty=-2 * d)
    if wraps:
        coil(a, x0, x1, ya, yb, zc - d * 1.4 - 0.1, t)
        coil(a, x0, x1, ya, yb, zc + d * 1.4 + 0.1, t)


def arrow_board(a, length, height, thick, x0, y_front, zc, direction=1, yaw=0.0,
                tip=None, nail=True):
    """Pentagon arrow board in the XZ plane, thickness toward -Y from y_front.
    Starts at x0 (square end) and points along +X (direction=1) or -X (-1)."""
    tip = tip if tip is not None else height * 0.75
    h = height / 2
    ch = min(0.12, h * 0.2)
    pts = [(0, -h + ch), (ch, -h), (length - tip, -h), (length, 0),
           (length - tip, h), (ch, h), (0, h - ch)]
    vs = a.poly_prism(pts, thick, mat=WOOD)
    # local XY -> world XZ, extrusion -> -Y
    a.transform(vs, (0, 0, 0), (R90, 0, 0))
    if direction < 0:
        a.transform(vs, (0, 0, 0), (0, 0, math.pi))
        # after the flip extrusion runs +Y: shift back so it still spans y_front-thick..y_front
        a.transform(vs, (0, -thick, 0), (0, 0, 0))
    a.transform(vs, (0, 0, 0), (0, 0, yaw))
    a.transform(vs, (x0, y_front, zc), (0, 0, 0))
    if nail:
        nx = x0 + direction * 0.45 * math.cos(yaw)
        a.cyl(0.07, 0.07, 0.06, sides=5, loc=(nx, y_front - thick + 0.02, zc),
              rot=(R90, 0, 0), mat=END)
    return vs


def tuft(a, rng, x, y, s=1.0):
    """Leafy clump with a few pointed blades poking out."""
    s *= 1.3
    a.leaf_cluster(0.8 * s, loc=(x, y, 0.0), mat=LEAF, lobes=6, floor=0.0)
    n = 6
    for i in range(n):
        ang = i * 2 * math.pi / n + rng.uniform(-0.35, 0.35)
        lean = rng.uniform(0.4, 0.8)
        hgt = rng.uniform(1.05, 1.5) * s
        vs = a.cyl(0.4 * s, 0.0, hgt, sides=4, mat=LEAF)
        a.transform(vs, (0, 0, 0), (0, 0, 0), (0.3, 1.0, 1.0))  # flat broad pointed leaf
        a.transform(vs, (x + math.cos(ang) * 0.3 * s, y + math.sin(ang) * 0.3 * s, 0.0),
                    (0, lean, ang))


def daisy(a, x, y, z=0.35, r=0.6):
    pts = []
    for i in range(10):
        ang = i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.38
        pts.append((math.cos(ang) * rr, math.sin(ang) * rr))
    a.poly_prism(pts, 0.05, loc=(x, y, z), mat="w09_petal")
    a.cyl(0.11, 0.09, 0.09, sides=5, loc=(x, y, z + 0.04), mat="w09_flower_eye")
    a.cyl(0.03, 0.03, z, sides=3, loc=(x, y, 0.0), mat=LEAF)


def rocks(a, rng, cx=0.0, cy=0.0, s=1.0, out=0):
    """Three-rock footing, the centre one biggest and tallest. Returns top z of centre rock.
    out=+-1 (gateway): side rocks go outward and behind so the walkway stays clear."""
    ccx = cx + out * 0.5 * s
    a.rock((5.4 * s, 4.4 * s, 3.8 * s), loc=(ccx, cy, 0), rot=(0, 0, rng.uniform(-0.3, 0.3)),
           mat=ROCK, facets=14, rough=0.1, sink=0.05)
    if out:
        p1 = (cx + out * 3.2 * s, cy + 0.4 * s)
        p2 = (cx - out * 0.4 * s, cy + 2.0 * s)
    else:
        p1 = (cx - 3.0 * s, cy + 0.5 * s)
        p2 = (cx + 2.9 * s, cy - 0.3 * s)
    a.rock((3.1 * s, 2.8 * s, 2.7 * s), loc=(p1[0], p1[1], 0),
           rot=(0, 0, rng.uniform(0, 3)), mat=ROCK, facets=14, rough=0.1, sink=0.05)
    a.rock((2.8 * s, 2.6 * s, 2.4 * s), loc=(p2[0], p2[1], 0),
           rot=(0, 0, rng.uniform(0, 3)), mat=ROCK, facets=14, rough=0.1, sink=0.05)
    return 3.8 * s * 0.9


def footing(a, rng, cx=0.0, cy=0.0, s=1.0, n_tufts=8, n_daisies=5, out=0):
    """Rocks ringed by leafy tufts and daisies hugging the rock bases."""
    top = rocks(a, rng, cx, cy, s, out)
    cx = cx + out * 0.5 * s
    rx, ry = 4.0 * s, 2.6 * s
    for i in range(n_tufts):
        ang = i * 2 * math.pi / n_tufts + rng.uniform(-0.25, 0.25)
        if out and math.cos(ang) * out < -0.5:
            ang = math.pi - ang  # keep the walkway side clear
        k = rng.uniform(0.95, 1.1)
        tuft(a, rng, cx + math.cos(ang) * rx * k, cy + math.sin(ang) * ry * k,
             s * rng.uniform(0.9, 1.2) if s > 0.8 else 0.8 * rng.uniform(0.9, 1.15))
    for i in range(n_daisies):
        ang = -math.pi / 2 + (i - (n_daisies - 1) / 2) * 0.75 + rng.uniform(-0.15, 0.15)
        k = rng.uniform(1.15, 1.35)
        daisy(a, cx + math.cos(ang) * rx * k, cy + math.sin(ang) * ry * k - 0.4,
              z=rng.uniform(1.2, 1.6), r=0.85 if s > 0.8 else 0.65)
    return top


def square_post(a, w, z0, z1, cap=True, slot=True, cx=0.0, cy=0.0):
    a.box((w, w, z1 - z0), loc=(cx, cy, (z0 + z1) / 2), mat=WOOD, bevel=0.07)
    if cap:
        cw = w * 1.25
        a.box((cw, cw, 0.6), loc=(cx, cy, z1 + 0.3), mat=WOOD, bevel=0.09)
    if slot:
        h = min(1.6, (z1 - z0) * 0.2)
        zs = z0 + (z1 - z0) * 0.32
        a.box((0.22, 0.04, h), loc=(cx, cy - w / 2 - 0.005, zs), mat=END)
        a.box((0.16, 0.04, 0.16), loc=(cx + 0.1, cy - w / 2 - 0.005, zs + h * 0.85), mat=END)


def cross_beam(a, length, width, height, zc, cx=0.0):
    """Crosspiece along Y through the post: square front end, angled back end."""
    h = height / 2
    tip = height * 0.7
    pts = [(0, -h), (length - tip, -h), (length, 0), (length - tip, h), (0, h)]
    vs = a.poly_prism(pts, width, mat=WOOD)
    a.transform(vs, (0, 0, 0), (R90, 0, 0))          # XZ plane, thickness toward -Y
    a.transform(vs, (-length / 2, width / 2, zc), (0, 0, 0))
    a.transform(vs, (0, 0, 0), (0, 0, R90))          # now runs along Y
    a.transform(vs, (cx, 0, 0), (0, 0, 0))
    return vs


def rope_tails(a, x, y, z):
    a.cyl(0.09, 0.03, 0.6, sides=4, loc=(x, y, z), rot=(0, 0.45, 0), mat=ROPE)
    a.cyl(0.09, 0.03, 0.55, sides=4, loc=(x, y, z), rot=(0, -0.5, 0.3), mat=ROPE)


# ---------------------------------------------------------------- assets
def build_hero(kit):
    fk = kit.flintkit
    rng = random.Random(901)
    a = fk.Asset("WayfindingPost", "W09 WayfindingPost")
    footing(a, rng, n_tufts=10, n_daisies=5)
    w = 1.2
    square_post(a, w, 3.0, 11.4)
    # crosspiece 8 x 0.7 x 1.0 running front-back through the post, one pointed end:
    # the front-back arm of the top-view cross and the profile board of the side view
    cross_beam(a, 8.0, 0.7, 1.0, 8.9)
    # upper bold board -> right (+X), in front of the post, crossing it
    arrow_board(a, 6.0, 1.55, 0.5, -1.6, -w / 2, 10.15, 1, tip=1.1)
    # lower board -> left (-X), behind the post, turned 10 degrees
    arrow_board(a, 5.6, 1.5, 0.5, 1.3, w / 2 + 0.5, 7.6, -1, yaw=math.radians(10), tip=1.1)
    # bold rope: X lashings binding each board and the crosspiece to the post
    x_lash(a, w / 2, 10.15, d=0.42, y0=-w / 2 - 0.5, y1=w / 2, wraps=False)
    x_lash(a, w / 2, 8.9, d=0.45, wraps=False)
    x_lash(a, w / 2, 7.6, d=0.42, y0=-w / 2, y1=w / 2 + 0.5, wraps=False)
    coils(a, w / 2, 11.0, 2, gap=0.3, t=0.15)
    rope_tails(a, 0.2, -w / 2 - 0.65, 9.6)
    flatten(a)
    o = a.finish()
    return kit.tag(o, "hero", collision="hull", budget=5000,
                   notes="Signpost on rock footing; no VFX sockets.")


def build_main(kit):
    a = kit.flintkit.Asset("WayfindingPostMain", "W09 WayfindingPost part")
    w = 1.2
    a.box((w, w, 9.6), loc=(0, 0, 4.8), mat=WOOD, bevel=0.07)
    # bevelled (pyramid-chamfered) top
    a.cyl(w * 0.707, w * 0.5, 0.4, sides=4, loc=(0, 0, 9.6), rot=(0, 0, math.pi / 4), mat=WOOD)
    a.box((w - 0.02, w - 0.02, 0.04), loc=(0, 0, 0.02), mat=END)  # end grain bottom
    a.box((0.24, 0.04, 2.2), loc=(0, -w / 2 - 0.005, 6.6), mat=END)  # slot
    a.box((0.24, 0.04, 1.0), loc=(0, -w / 2 - 0.005, 3.2), mat=END)
    for z in (8.6, 4.6, 1.6):
        a.cyl(0.08, 0.08, 0.04, sides=5, loc=(0.2, -w / 2 - 0.0, z), rot=(R90, 0, 0), mat=END)
    o = a.finish()
    return kit.tag(o, "part", collision="box", budget=1500, notes="Main 10-stud post.")


def build_crosspiece(kit):
    a = kit.flintkit.Asset("WayfindingPostCrosspiece", "W09 WayfindingPost part")
    pts = [(0, 0), (7.0, 0), (6.4, 1.0), (0, 1.0)]
    vs = a.poly_prism(pts, 0.8, mat=WOOD)
    a.transform(vs, (-3.5, 0.4, 0), (R90, 0, 0))
    a.box((0.04, 0.78, 0.98), loc=(-3.52, 0, 0.5), mat=END)
    a.box((0.6, 0.04, 0.5), loc=(-2.4, -0.42, 0.5), mat=END)  # notch
    o = a.finish()
    return kit.tag(o, "part", collision="box", budget=1500, notes="Crosspiece beam.")


def build_arrow(kit):
    a = kit.flintkit.Asset("WayfindingPostArrowBoard", "W09 WayfindingPost part")
    vs = arrow_board(a, 6.0, 1.6, 0.5, -3.0, 0.25, 0.8, 1, tip=1.2, nail=False)
    a.cyl(0.08, 0.08, 0.06, sides=5, loc=(-2.5, -0.23, 0.8), rot=(R90, 0, 0), mat=END)
    # laid at a shallow angle like the sheet; bbox stays close to 6 x 0.5 x 1.6
    a.transform(list(a.bm.verts), (0, 0, 0), (0, 0, math.radians(8)))
    o = a.finish()
    return kit.tag(o, "part", collision="box", budget=1500, notes="Arrow board.")


def build_rope_tie(kit):
    a = kit.flintkit.Asset("WayfindingPostRopeTie", "W09 WayfindingPost part")
    a.box((1.4, 1.4, 1.8), loc=(0, 0, 0.9), mat=WOOD, bevel=0.07)
    a.box((1.36, 1.36, 0.04), loc=(0, 0, 1.8), mat=END)
    coils(a, 0.7, 0.45, 5, gap=0.23, t=0.13)
    o = a.finish()
    return kit.tag(o, "part", collision="box", budget=1500, notes="Rope-wrapped post block.")


def build_footing(kit):
    a = kit.flintkit.Asset("WayfindingPostStoneFooting", "W09 WayfindingPost part")
    rocks(a, random.Random(77))
    flatten(a)
    o = a.finish()
    return kit.tag(o, "part", collision="hull", budget=1500, notes="Three-rock footing.")


def build_forked(kit):
    rng = random.Random(902)
    a = kit.flintkit.Asset("WayfindingForkedSignpost", "W09 WayfindingPost variant")
    footing(a, rng, n_tufts=7, n_daisies=4)
    w = 1.2
    square_post(a, w, 3.0, 11.4)
    arrow_board(a, 5.6, 1.4, 0.5, -1.4, -w / 2, 10.45, 1, tip=1.0)
    arrow_board(a, 5.2, 1.3, 0.5, 1.3, w / 2 + 0.5, 9.5, -1, yaw=math.radians(8), tip=1.0)
    arrow_board(a, 4.8, 1.3, 0.5, -1.2, -w / 2, 8.6, 1, yaw=math.radians(-8), tip=1.0)
    x_lash(a, w / 2, 10.45, d=0.42, y0=-w / 2 - 0.5, y1=w / 2 + 0.5, wraps=False)
    x_lash(a, w / 2, 8.6, d=0.42, y0=-w / 2 - 0.5, y1=w / 2 + 0.5, wraps=False)
    coils(a, w / 2, 11.0, 2, gap=0.3, t=0.15)
    rope_tails(a, 0.2, -w / 2 - 0.65, 9.9)
    flatten(a)
    o = a.finish()
    return kit.tag(o, "variant", collision="hull", budget=4000, notes="Three-board fork.")


def build_short(kit):
    rng = random.Random(903)
    a = kit.flintkit.Asset("WayfindingShortBoundaryPost", "W09 WayfindingPost variant")
    footing(a, rng, s=0.62, n_tufts=6, n_daisies=3)
    w = 1.4
    square_post(a, w, 1.6, 5.4)
    coils(a, w / 2, 3.7, 3, gap=0.3, t=0.15)
    x_lash(a, w / 2, 4.85, d=0.3, t=0.15, wraps=False)
    flatten(a)
    o = a.finish()
    return kit.tag(o, "variant", collision="hull", budget=3500, notes="Squat boundary post.")


def build_gateway(kit):
    rng = random.Random(904)
    a = kit.flintkit.Asset("WayfindingTrailGateway", "W09 WayfindingPost variant")
    w = 1.4
    w = 1.6
    px = 9.2
    bzc = 11.4  # beam centre; beam runs through both posts
    for sx in (-1, 1):
        footing(a, rng, cx=sx * px, cy=0.0, s=0.9, n_tufts=7, n_daisies=3, out=sx)
        square_post(a, w, 2.4, 12.5, cap=False, cx=sx * px)
        a.box((w * 1.15, w * 1.15, 0.5), loc=(sx * px, 0, 12.75), mat=WOOD, bevel=0.08)
        # bold rope X over the beam/post join, plus coils above and below
        x_lash(a, w / 2, bzc, d=0.6, t=0.2, cx=sx * px, wraps=False)
        coils(a, w / 2, bzc + 1.0, 2, gap=0.36, t=0.19, cx=sx * px)
        coils(a, w / 2, bzc - 1.35, 2, gap=0.36, t=0.19, cx=sx * px)
    # top beam through the post tops, ends poking clearly beyond (1 stud each side)
    a.box((22.0, 1.1, 1.3), loc=(0, 0, bzc), mat=WOOD, bevel=0.08)
    # banner: swallow-tail cloth hanging from the beam centre
    by = -0.6
    bw, bh, bz0 = 3.5, 6.0, bzc - 0.6 - 0.4 - 6.0
    pts = [(-bw / 2, 0.0), (0.0, 1.0), (bw / 2, 0.0), (bw / 2, bh), (-bw / 2, bh)]
    vs = a.poly_prism(pts, 0.2, mat="w09_banner_red")
    a.transform(vs, (0, by + 0.1, bz0), (R90, 0, 0))
    ez = bz0 + 3.8
    dia = [(0, -1.25), (0.85, 0), (0, 1.25), (-0.85, 0)]
    vs = a.poly_prism(dia, 0.06, mat="w09_banner_emblem")
    a.transform(vs, (0, by - 0.1, ez), (R90, 0, 0))
    dia2 = [(0, -0.6), (0.4, 0), (0, 0.6), (-0.4, 0)]
    vs = a.poly_prism(dia2, 0.06, mat="w09_banner_red")
    a.transform(vs, (0, by - 0.16, ez), (R90, 0, 0))
    for sx in (-1, 1):
        x = sx * 1.1
        loop = [(x, by - 0.1, bz0 + bh - 0.1), (x, -0.62, bzc + 0.75), (x, 0.62, bzc + 0.75),
                (x, 0.62, bzc - 0.6), (x, by, bz0 + bh + 0.1)]
        a.tube_loop(loop, 0.12, mat=ROPE, rseg=4)
    flatten(a)
    o = a.finish()
    return kit.tag(o, "variant", collision="precise", budget=5000,
                   notes="Timber gate; static banner; walkway ~14 wide x 10.8 tall under the beam.")


def build(kit):
    return [build_hero(kit), build_main(kit), build_crosspiece(kit), build_arrow(kit),
            build_rope_tie(kit), build_footing(kit), build_forked(kit), build_short(kit),
            build_gateway(kit)]
