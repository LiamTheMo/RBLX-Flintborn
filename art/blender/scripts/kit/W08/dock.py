"""W08 row 2: Dock. Raised timber pier on dark piles with rope-wrapped mooring posts.

Long axis runs along Y (8 long x 6 wide) so the TOP cell shows a long vertical deck with
planks across it, as the reference draws it. HERO_AZIMUTH looks at the long (-X) side.
"""
import math
import random

SUBJECT = "Dock"
ROW = 2
HERO_AZIMUTH = -112   # camera at -X/+Y: the long side faces the viewer, +Y end on the left
HERO_ELEVATION = 30   # the sheet draws the docks from higher, showing the deck top

PALETTE = {
    "w08_wood": ("#A8582A", 0.88, 0, 0),
    "w08_pile_wood": ("#5C3420", 0.92, 0, 0),
    "w08_rope": ("#D4A857", 0.95, 0, 0),
    "w08_stone": ("#9CA2AA", 0.95, 0, 0),
    "w08_nail": ("#C48A3C", 0.5, 0.6, 0),
    "w08_banner": ("#B3202A", 0.85, 0, 0),
}

W, PW, ROPE, NAIL = "w08_wood", "w08_pile_wood", "w08_rope", "w08_nail"
PILE = 0.8
POST = 0.7
ROPE_T = 0.09
LOW = [False]   # variants drop bevels to stay inside 3000 tris


def _bev(v):
    return 0.0 if LOW[0] else v


# ---------------------------------------------------------------- helpers
def pile(a, x, y, top):
    a.box((PILE, PILE, top), (x, y, top / 2), mat=PW, bevel=_bev(0.04))


def post(a, x, y, z0, z1, rings=3, ring_z=None):
    """Square mooring post from z0 to z1 with an 8-sided round log-end cap and a rope wrap."""
    a.box((POST, POST, z1 - 0.25 - z0), (x, y, (z0 + z1 - 0.25) / 2), mat=W, bevel=_bev(0.04))
    a.cyl(0.43, 0.41, 0.25, sides=8, loc=(x, y, z1 - 0.25), mat=W)
    rz = ring_z if ring_z is not None else z1 - 0.75
    a.rope_rings(0.37, rz, count=rings, thickness=0.1, loc=(x, y), mat=ROPE)


def planks_x(a, rng, x0, x1, y0, y1, z, pitch=0.8, t=0.4, over=0.15):
    """Planks long along X, laid side by side along Y with gaps."""
    n = max(1, round((y1 - y0) / pitch))
    step = (y1 - y0) / n
    L = (x1 - x0) + 2 * over
    for i in range(n):
        cy = y0 + step * (i + 0.5)
        a.box((L + rng.uniform(-0.12, 0.12), step - 0.12, t),
              ((x0 + x1) / 2 + rng.uniform(-0.08, 0.08), cy, z - t / 2 + rng.uniform(-0.03, 0.03)),
              rot=(0, rng.uniform(-0.02, 0.02), rng.uniform(-0.025, 0.025)), mat=W, bevel=_bev(0.05))


def planks_y(a, rng, x0, x1, y0, y1, z, pitch=0.8, t=0.4, over=0.15):
    """Planks long along Y, laid side by side along X with gaps."""
    n = max(1, round((x1 - x0) / pitch))
    step = (x1 - x0) / n
    L = (y1 - y0) + 2 * over
    for i in range(n):
        cx = x0 + step * (i + 0.5)
        a.box((step - 0.12, L + rng.uniform(-0.12, 0.12), t),
              (cx, (y0 + y1) / 2 + rng.uniform(-0.08, 0.08), z - t / 2 + rng.uniform(-0.03, 0.03)),
              rot=(rng.uniform(-0.02, 0.02), 0, rng.uniform(-0.025, 0.025)), mat=W, bevel=_bev(0.05))


def beam_x(a, x0, x1, y, zc, s=0.7):
    a.box((x1 - x0, s, s), ((x0 + x1) / 2, y, zc), mat=W, bevel=_bev(0.04))


def beam_y(a, y0, y1, x, zc, s=0.7):
    a.box((s, y1 - y0, s), (x, (y0 + y1) / 2, zc), mat=W, bevel=_bev(0.04))


def nail(a, loc, face):
    """Brass bolt head on a face pointing along +-X or +-Y."""
    rot = (0, math.pi / 2, 0) if face in ("x", "-x") else (math.pi / 2, 0, 0)
    d = 1 if face in ("x", "y") else -1
    x, y, z = loc
    if face in ("x", "-x"):
        x -= 0.04 * d
    else:
        y += 0.04 * d
    a.cyl(0.11, 0.09, 0.09, sides=6, loc=(x, y, z), rot=rot, mat=NAIL)


def brace_yz(a, x, y0, z0, y1, z1, s=(0.28, 0.4)):
    dy, dz = y1 - y0, z1 - z0
    a.box((s[0], math.hypot(dy, dz), s[1]), (x, (y0 + y1) / 2, (z0 + z1) / 2),
          rot=(math.atan2(dz, dy), 0, 0), mat=W, bevel=_bev(0.03))


def brace_xz(a, y, x0, z0, x1, z1, s=(0.28, 0.4)):
    dx, dz = x1 - x0, z1 - z0
    a.box((math.hypot(dx, dz), s[0], s[1]), ((x0 + x1) / 2, y, (z0 + z1) / 2),
          rot=(0, -math.atan2(dz, dx), 0), mat=W, bevel=_bev(0.03))


def x_brace_xz(a, y, xa, xb, zlo, zhi):
    """X brace on a plane of constant y between piles at xa and xb."""
    ia, ib = xa + PILE / 2, xb - PILE / 2
    sg = 1 if y > 0 else -1
    brace_xz(a, y, ia, zlo, ib, zhi)
    brace_xz(a, y + 0.06 * sg, ia, zhi, ib, zlo)
    nail(a, ((xa + xb) / 2, y + 0.2 * sg, (zlo + zhi) / 2), "y" if y > 0 else "-y")


def x_brace_yz(a, x, ya, yb, zlo, zhi):
    """X brace on a plane of constant x between piles at ya and yb."""
    ia, ib = ya + PILE / 2, yb - PILE / 2
    sg = 1 if x > 0 else -1
    brace_yz(a, x, ia, zlo, ib, zhi)
    brace_yz(a, x + 0.06 * sg, ia, zhi, ib, zlo)
    nail(a, (x + 0.2 * sg, (ya + yb) / 2, (zlo + zhi) / 2), "x" if x > 0 else "-x")


def swag(a, p1, p2, sag=0.3, th=ROPE_T, n=7):
    pts = []
    for i in range(n):
        t = i / (n - 1)
        pts.append((p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t,
                    p1[2] + (p2[2] - p1[2]) * t - sag * 4 * t * (1 - t)))
    a.tube_loop(pts, th, mat=ROPE, rseg=5, closed=False)


def swag_between(a, q1, q2, z, sag=0.3, n=7):
    """Swag between two post centres, starting at the post faces."""
    dx, dy = q2[0] - q1[0], q2[1] - q1[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    o = POST / 2 + 0.02
    swag(a, (q1[0] + ux * o, q1[1] + uy * o, z), (q2[0] - ux * o, q2[1] - uy * o, z), sag=sag, n=n)


def two_tone(o):
    o["kit_two_tone_ok"] = ("w08_pile_wood is weathered wet pile timber, w08_wood is dry deck/post timber; "
                            "the sheet palette makes them distinct materials")


# ---------------------------------------------------------------- assets
def build_hero(kit):
    fk = kit.flintkit
    a = fk.Asset("Dock", "W08 Dock")
    rng = random.Random(81)
    DZ = 3.2
    PT = DZ - 0.4          # pile top = underside of planks
    BZ = PT - 0.35         # beam centre
    xs, ys = (-2.75, 2.75), (-3.45, 0.0, 3.45)
    for x in xs:
        for y in ys:
            pile(a, x, y, PT)
            post(a, x, y, PT, 5.2)
    # two long beams along Y on the piles
    for x in xs:
        beam_y(a, -4.0, 4.0, x, BZ)
        for y in ys:
            nail(a, (x + 0.4 * (1 if x > 0 else -1), y, BZ), "x" if x > 0 else "-x")
    # transverse crossbeams at both ends and the middle
    for y in ys:
        beam_x(a, -2.4, 2.4, y, BZ, s=0.6)
    for y in (-3.45, 3.45):
        nail(a, (0.0, y + 0.3 * (1 if y > 0 else -1), BZ), "y" if y > 0 else "-y")
    planks_x(a, rng, -3.0, 3.0, -4.0, 4.0, DZ)
    # X braces under both short ends
    for y in (-3.45, 3.45):
        x_brace_xz(a, y + 0.5 * (1 if y > 0 else -1), -2.75, 2.75, 0.25, PT - 0.85)
    # rope swags: along the far (+X) long side and across the +Y end
    zr = 4.6
    swag_between(a, (2.75, -3.45), (2.75, 0.0), zr)
    swag_between(a, (2.75, 0.0), (2.75, 3.45), zr)
    swag_between(a, (-2.75, 3.45), (2.75, 3.45), zr, sag=0.35)
    o = a.finish()
    two_tone(o)
    return kit.tag(o, "hero", collision="precise", budget=6000,
                   notes="Raised pier, 8 long (Y) x 6 wide (X); deck top z=3.2, posts to 6. "
                         "No VFX sockets: the reference draws the dock on plain ground (optional water_foam at pile bases omitted).")


def build_parts(kit):
    fk = kit.flintkit
    out = []

    a = fk.Asset("DockMooringPost", "W08 Dock mooring post")
    post(a, 0, 0, 0.0, 2.6, rings=3, ring_z=1.6)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Short square mooring post, thick rope wrap near the top, round cap."))

    a = fk.Asset("DockRopeTie", "W08 Dock rope tie")
    pts = [(-0.8, 0.05, 0.15), (-0.5, -0.06, 0.16), (-0.2, 0.03, 0.26), (0.2, -0.03, 0.26),
           (0.5, 0.06, 0.16), (0.8, -0.04, 0.15)]
    a.tube_loop(pts, 0.14, mat=ROPE, rseg=6, closed=False)
    for i, x in enumerate((-0.16, 0.0, 0.16)):
        a.torus(0.22, 0.1, loc=(x, 0, 0.3), rot=(0, math.pi / 2, 0.15 * (i - 1)), mat=ROPE, seg=10, rseg=5)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="Short rope with a coiled knot, ends ~1.6 apart."))

    a = fk.Asset("DockPile", "W08 Dock pile")
    a.box((PILE, PILE, 6.0), (0, 0, 3.0), mat=PW, bevel=0.04)
    a.rope_rings(0.44, 5.0, count=3, thickness=0.11, mat=ROPE)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Tall dark pile 0.8 x 0.8 x 6 with rope band near the top."))

    a = fk.Asset("DockDeckPlank", "W08 Dock deck plank")
    a.box((4.0, 0.7, 0.4), (0, 0, 0.2), mat=W, bevel=0.05, jitter=0.02)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="One deck plank 4 x 0.7 x 0.4."))

    a = fk.Asset("DockBeam", "W08 Dock beam")
    a.box((6.0, 0.7, 0.7), (0, 0, 0.35), mat=W, bevel=0.05, jitter=0.02)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Long beam 6 x 0.7 x 0.7."))

    a = fk.Asset("DockBrace", "W08 Dock brace")
    a.box((3.0, 0.4, 0.5), (0, 0, 1.25), rot=(0, -math.pi / 4, 0), mat=W, bevel=0.04)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Slanted brace timber, 3 long at 45 deg."))
    return out


def build_straight(kit):
    fk = kit.flintkit
    a = fk.Asset("DockStraight", "W08 Dock straight")
    rng = random.Random(12)
    DZ = 3.8
    PT, BZ = DZ - 0.4, DZ - 0.75
    xs, ys = (-1.75, 1.75), (-5.4, -1.8, 1.8, 5.4)
    for x in xs:
        for y in ys:
            pile(a, x, y, PT)
            post(a, x, y, PT, DZ + 1.9, rings=2)
    for x in xs:
        beam_y(a, -6.0, 6.0, x, BZ)
        for y in ys:
            nail(a, (x + 0.4 * (1 if x > 0 else -1), y, BZ), "x" if x > 0 else "-x")
    for y in (-5.4, 5.4):
        beam_x(a, -1.4, 1.4, y, BZ, s=0.55)
        x_brace_xz(a, y + 0.5 * (1 if y > 0 else -1), -1.75, 1.75, 0.3, PT - 0.9)
    planks_x(a, rng, -2.0, 2.0, -6.0, 6.0, DZ)
    zr = DZ + 1.3
    for x in xs:
        for y0, y1 in zip(ys[:-1], ys[1:]):
            swag_between(a, (x, y0), (x, y1), zr, n=6)
    o = a.finish()
    two_tone(o)
    return kit.tag(o, "variant", collision="precise", budget=3000,
                   notes="A. Straight: 12 long (Y) x 4 wide narrow pier, 8 posts, tall legs. No sockets.")


def build_thead(kit):
    fk = kit.flintkit
    a = fk.Asset("DockTHead", "W08 Dock T-head")
    rng = random.Random(23)
    DZ = 3.2
    PT, BZ = DZ - 0.4, DZ - 0.75
    # walkway along X toward the camera: x -7..3, y -1.5..1.5; T bar at the back: x 3..7, y -5..5
    wpiles = [(x, y) for x in (-6.6, -3.3, -0.2) for y in (-1.15, 1.15)]
    tpiles = [(x, y) for y in (-4.6, -1.15, 1.15, 4.6) for x in (3.4, 6.6)]
    posts = [(-6.6, -1.15), (-6.6, 1.15), (3.4, -4.6), (3.4, 4.6),
             (6.6, -4.6), (6.6, 4.6), (6.6, -1.15), (6.6, 1.15)]
    for (x, y) in wpiles + tpiles:
        pile(a, x, y, PT)
    for (x, y) in posts:
        post(a, x, y, PT, DZ + 1.9, rings=2)
    for y in (-1.15, 1.15):
        beam_x(a, -7.0, 3.4, y, BZ, s=0.6)
        x_brace_xz(a, y + 0.5 * (1 if y > 0 else -1), -6.6, -3.3, 0.3, PT - 0.85)
    for x in (3.4, 6.6):
        beam_y(a, -5.0, 5.0, x, BZ, s=0.6)
    beam_y(a, -0.8, 0.8, -6.6, BZ, s=0.55)
    # walkway planks across its width, T planks across the T depth (continuous at x=3)
    planks_y(a, rng, -7.0, 3.0, -1.5, 1.5, DZ)
    planks_x(a, rng, 3.0, 7.0, -5.0, 5.0, DZ)
    zr = DZ + 1.3
    for s in (-1, 1):
        swag_between(a, (3.4, s * 4.6), (6.6, s * 4.6), zr, n=6)
        swag_between(a, (6.6, s * 4.6), (6.6, s * 1.15), zr, n=6)
    swag_between(a, (-6.6, -1.15), (-6.6, 1.15), zr, n=6)
    o = a.finish()
    two_tone(o)
    return kit.tag(o, "variant", collision="precise", budget=3000,
                   notes="B. T-Head: 3-wide walkway ending in a 10 x 4 cross platform, 8 posts. No sockets.")


def build_lhead(kit):
    fk = kit.flintkit
    a = fk.Asset("DockLHead", "W08 Dock L-head")
    rng = random.Random(34)
    DZ = 3.2
    PT, BZ = DZ - 0.4, DZ - 0.75
    # main pier x -2..2, y -4..4; L extension toward the camera: x -6..-2, y 0..4
    posts = [(-1.6, -3.6), (1.6, -3.6), (1.6, 0.0), (1.6, 3.6), (-5.6, 3.6), (-5.6, 0.4)]
    piles = posts + [(-1.6, 0.4)]
    for (x, y) in piles:
        pile(a, x, y, PT)
    for (x, y) in posts:
        post(a, x, y, PT, DZ + 1.9, rings=3)
    for x in (-1.6, 1.6):
        beam_y(a, -4.0, 4.0, x, BZ, s=0.6)
    for y in (0.4, 3.6):
        beam_x(a, -6.0, -1.6, y, BZ, s=0.6)
    beam_x(a, -1.2, 1.2, -3.6, BZ, s=0.55)
    planks_x(a, rng, -2.0, 2.0, -4.0, 4.0, DZ)
    planks_y(a, rng, -6.0, -2.0, 0.0, 4.0, DZ)
    x_brace_xz(a, -4.1, -1.6, 1.6, 0.3, PT - 0.85)
    zr = DZ + 1.3
    swag_between(a, (-1.6, -3.6), (1.6, -3.6), zr, n=6)
    swag_between(a, (1.6, -3.6), (1.6, 0.0), zr, n=6)
    swag_between(a, (1.6, 0.0), (1.6, 3.6), zr, n=6)
    swag_between(a, (-5.6, 0.4), (-5.6, 3.6), zr, n=6)
    o = a.finish()
    two_tone(o)
    return kit.tag(o, "variant", collision="precise", budget=3000,
                   notes="C. L-Head: 8 x 4 pier with a 4 x 4 perpendicular extension, 6 posts with rope ties. No sockets.")


def build(kit):
    LOW[0] = False
    out = [build_hero(kit)]
    out += build_parts(kit)
    LOW[0] = True
    out += [build_straight(kit), build_thead(kit), build_lhead(kit)]
    LOW[0] = False
    return out
