"""W12 row 3: WallWalk - raised timber wall walk with railings, braces and stairs."""
import math

SUBJECT = "WallWalk"
ROW = 3
HERO_AZIMUTH = -22   # spec: front-left
SIDE_AZIMUTH = -160  # rear view from the rear-left: long back face, stair profile on the right

PALETTE = {
    "w12_wood": ("#8F5A2C", 0.9, 0, 0),
    "w12_tan": ("#C9985A", 0.9, 0, 0),
    "w12_stone": ("#7E7F8C", 0.95, 0, 0),
    "w12_leaf": ("#3F9A2E", 0.9, 0, 0),
    "w12_banner_red": ("#C8202B", 0.8, 0, 0),
    "w12_banner_trim": ("#F2E6D2", 0.8, 0, 0),
    "w12_walk_flower": ("#F2C230", 0.8, 0, 0),  # tiny yellow flowers in the clover at the base
}

W = "w12_wood"
R = "w12_tan"
S = "w12_stone"
L = "w12_leaf"
FL = "w12_walk_flower"
DECK = 7.0          # plank top
RAIL_HI = 9.6       # rail top ~2.8 above the deck
RAIL_MID = 8.45
POST_W = 1.0


# ---------------------------------------------------------------- helpers
def sq_post(a, x, y, top, w=POST_W, z0=0.0, cap=True):
    """Square post from z0 to `top` with a chamfered pyramid cap."""
    h = top - z0
    ch = 0.3 if cap else 0.0
    a.box((w, w, h - ch), loc=(x, y, z0 + (h - ch) / 2), mat=W, bevel=0.06)
    if cap:
        a.cyl(w * 0.7071, w * 0.42, ch, sides=4, loc=(x, y, top - ch),
              rot=(0, 0, math.pi / 4), mat=W)


def band(a, x, y, z, w=POST_W, n=2):
    """Rope wraps around a square post (stacked flat loops)."""
    for k in range(n):
        a.box((w + 0.14, w + 0.14, 0.14), loc=(x, y, z + k * 0.2), mat=R, bevel=0.03)


def bar(a, p1, p2, s=0.35):
    """Square timber beam between two points."""
    a.beam(p1, p2, s * 0.7071, sides=4, mat=W, end_mat=W, jitter=0.0)


def rail_run(a, xs, y, z_list=(RAIL_HI, RAIL_MID), axis="x", s=0.35):
    """Rails between the first and last coordinate of xs along an axis."""
    lo, hi = min(xs), max(xs)
    for z in z_list:
        if axis == "x":
            bar(a, (lo - 0.3, y, z), (hi + 0.3, y, z), s)
        else:
            bar(a, (y, lo - 0.3, z), (y, hi + 0.3, z), s)


def deck(a, x0, x1, y0, y1, z=DECK, t=0.6, along="x"):
    """Planks ~1 wide with small gaps; top surface at z."""
    if along == "x":
        n = max(1, round(y1 - y0))
        w = (y1 - y0) / n
        for i in range(n):
            a.plank((x1 - x0, w - 0.06, t), loc=((x0 + x1) / 2, y0 + w * (i + 0.5), z - t / 2),
                    mat=W, bevel=0.05, jitter=0.01)
    else:
        n = max(1, round(x1 - x0))
        w = (x1 - x0) / n
        for i in range(n):
            a.plank((w - 0.06, y1 - y0, t), loc=(x0 + w * (i + 0.5), (y0 + y1) / 2, z - t / 2),
                    mat=W, bevel=0.05, jitter=0.01)


def rocks(a, spots):
    for (x, y, sx, sy, sz, rz) in spots:
        a.rock((sx, sy, sz), loc=(x, y, 0), rot=(0, 0, rz), mat=S, subdiv=1, facets=20, sink=0.0)


def tufts(a, spots, flowers=True):
    """Chunky clover clumps (4-5 lobes) with a yellow flower or two on top."""
    for j, (x, y, r) in enumerate(spots):
        a.leaf_cluster(r, loc=(x, y, r * 0.4), mat=L, lobes=4 + j % 2, squash=0.65, floor=0.0)
        if flowers and j % 2 == 0:
            for (dx, dy) in ((0.3, -0.35), (-0.35, -0.2))[: 1 + j % 3 // 2]:
                a.cyl(0.22, 0.22, 0.1, sides=5, loc=(x + dx * r * 1.6, y - r * 0.8, r * 0.6),
                      rot=(0.5, 0, 0), mat=FL)


def stringer_profile(f, t, H, deep=1.4):
    """CCW outline (run, z) of a sloped stringer board from foot f to top t."""
    s = 1 if t > f else -1
    pts = [(f, 0.0), (f + s * deep, 0.0), (t, H - deep), (t, H - 0.55), (f, 0.35)]
    return pts if s > 0 else list(reversed(pts))


def stair_x(a, x_top, yc, width, n, rise, run, handrail_y=None, st=0.45):
    """Chunky stair descending toward -X from x_top; tread k top at rise*(k+1)."""
    for k in range(n):
        ztop = rise * (k + 1)
        xc = x_top - (n - k - 0.5) * run
        a.plank((run + 0.15, width, 1.0), loc=(xc, yc, ztop - 0.5), mat=W, bevel=0.08, jitter=0.0)
    x_foot = x_top - n * run
    H = rise * n
    for sy in (yc - width / 2 - st / 2, yc + width / 2 + st / 2):
        a.poly_prism(stringer_profile(x_foot - 0.2, x_top, H), st, loc=(0, sy + st / 2, 0),
                     rot=(math.pi / 2, 0, 0), mat=W)
        sq_post(a, x_foot + 0.2, sy, 1.9, w=0.7)
        band(a, x_foot + 0.2, sy, 1.2, w=0.7)
    if handrail_y is not None:
        sq_post(a, x_foot + 0.2, handrail_y, rise + 2.6, w=0.7)
        band(a, x_foot + 0.2, handrail_y, rise + 1.9, w=0.7)
        bar(a, (x_foot + 0.2, handrail_y, rise + 2.2), (x_top, handrail_y, H + 2.2), s=0.4)


def stair_y(a, y_top, xc, width, n, rise, run, handrail_x=None, st=0.45):
    """Chunky stair descending toward -Y from y_top."""
    for k in range(n):
        ztop = rise * (k + 1)
        yc = y_top - (n - k - 0.5) * run
        a.plank((width, run + 0.15, 1.0), loc=(xc, yc, ztop - 0.5), mat=W, bevel=0.08, jitter=0.0)
    y_foot = y_top - n * run
    H = rise * n
    for sx in (xc - width / 2 - st / 2, xc + width / 2 + st / 2):
        a.poly_prism(stringer_profile(y_foot - 0.2, y_top, H), st, loc=(sx - st / 2, 0, 0),
                     rot=(math.pi / 2, 0, math.pi / 2), mat=W)
        sq_post(a, sx, y_foot + 0.2, 1.9, w=0.7)
        band(a, sx, y_foot + 0.2, 1.2, w=0.7)
    if handrail_x is not None:
        sq_post(a, handrail_x, y_foot + 0.2, rise + 2.6, w=0.7)
        band(a, handrail_x, y_foot + 0.2, rise + 1.9, w=0.7)
        bar(a, (handrail_x, y_foot + 0.2, rise + 2.2), (handrail_x, y_top, H + 2.2), s=0.4)


def banner(a, x, y, z_top, w=1.6, h=4.2):
    """Swallowtail red banner facing -Y on a front face at y, with cream diamond."""
    hw = w / 2
    pts = [(-hw, -h), (0, -h + 0.7), (hw, -h), (hw, 0), (-hw, 0)]
    pts = [(-hw, -h), (0, -h + 0.7), (hw, -h), (hw, 0), (-hw, 0)]
    rot = (math.pi / 2, 0, 0)
    a.poly_prism([(px, py) for px, py in pts], 0.08, loc=(x, y, z_top), rot=rot, mat="w12_banner_red")
    # rod
    bar(a, (x - hw - 0.25, y - 0.1, z_top + 0.05), (x + hw + 0.25, y - 0.1, z_top + 0.05), s=0.2)
    zc = z_top - h * 0.45

    def diamond(rx, rz, dy, mat):
        a.poly_prism([(0, -rz), (rx, 0), (0, rz), (-rx, 0)], 0.03,
                     loc=(x, y - 0.08 - dy, zc), rot=rot, mat=mat)
    diamond(0.55, 0.95, 0.0, "w12_banner_trim")
    diamond(0.38, 0.68, 0.03, "w12_banner_red")
    diamond(0.16, 0.3, 0.06, "w12_banner_trim")
    # cream trim bar across the top
    a.box((w, 0.03, 0.12), loc=(x, y - 0.1, z_top - 0.35), mat="w12_banner_trim")


def frame(a, xs, ys, top, braces="x", lash=True, beam_z=DECK - 0.8):
    """Posts at every (x, y), deck edge beams and braces between neighbouring posts."""
    for y in ys:
        for x in xs:
            sq_post(a, x, y, top)
            band(a, x, y, DECK - 1.0)
        bar(a, (xs[0] - 0.5, y, beam_z), (xs[-1] + 0.5, y, beam_z), s=0.55)
    for x in (xs[0], xs[-1]):
        bar(a, (x, ys[0], beam_z), (x, ys[-1], beam_z), s=0.5)
    for y in ys:
        side = -0.62 if y < 0 else 0.62
        for i in range(len(xs) - 1):
            x0, x1 = xs[i] + 0.5, xs[i + 1] - 0.5
            yb = y + side
            if braces == "x" or i % 2 == 0:
                bar(a, (x0, yb, 0.6), (x1, yb, beam_z - 0.3), s=0.38)
            if braces == "x" or i % 2 == 1:
                bar(a, (x1, yb, 0.6), (x0, yb, beam_z - 0.3), s=0.38)
            if lash and i % 2 == 0:
                a.lashing(((x0 + x1) / 2, yb + side * 0.3, (0.6 + beam_z - 0.3) / 2), size=0.33,
                          thickness=0.08, rot=(math.pi / 2, 0, 0), mat=R) if braces == "x" else None


# ---------------------------------------------------------------- hero
def build_hero(kit):
    fk = kit.flintkit
    a = fk.Asset("WallWalk", "W12 WallWalk")
    xs = [-5.5, -2.75, 0.0, 2.75, 5.5]
    yf, yb = -2.45, 2.45
    top = 10.0
    for y in (yf, yb):
        for x in xs:
            sq_post(a, x, y, top + 0.3, w=1.0)
            band(a, x, y, DECK - 0.9, w=1.0)
            band(a, x, y, RAIL_HI - 0.25, w=1.0, n=1)
            band(a, x, y, RAIL_MID - 0.25, w=1.0, n=1)
        bar(a, (-6.1, y, DECK - 0.85), (6.1, y, DECK - 0.85), s=0.55)
    for x in (-5.5, 5.5):
        bar(a, (x, yf, DECK - 0.85), (x, yb, DECK - 0.85), s=0.5)
    deck(a, -5.9, 5.9, -2.0, 2.0)
    # railings: full front, full back and the right end; the left end is open for the stair
    rail_run(a, xs, yb)
    rail_run(a, xs, yf)
    rail_run(a, (yf, yb), 5.5, axis="y")
    band(a, 5.5, 0.0, RAIL_HI - 0.25, w=0.5, n=1)
    # front plank wall under the deck
    n = 12
    pw = 11.0 / n
    for i in range(n):
        x = -5.5 + pw * (i + 0.5)
        for yy in (yf + 0.2, yb - 0.2):
            a.box((pw - 0.08, 0.3, DECK - 1.1), loc=(x, yy, (DECK - 1.1) / 2), mat=W, bevel=0.04)
    # diagonal braces in front of the wall (alternating 45 deg)
    yb_ = yf - 0.8
    for i in range(4):
        x0, x1 = xs[i] + 0.5, xs[i + 1] - 0.5
        if i == 2:
            continue  # banner bay
        if i % 2 == 0:
            bar(a, (x0, yb_, 0.6), (x1, yb_, 2.4 + (x1 - x0)), s=0.4)
        else:
            bar(a, (x1, yb_, 0.6), (x0, yb_, 2.4 + (x1 - x0)), s=0.4)
        a.lashing((x0 + 0.15 if i % 2 == 0 else x1 - 0.15, yb_ - 0.15, 1.0), size=0.32, thickness=0.08,
                  rot=(math.pi / 2, 0, 0), mat=R)
    # rear braces (visible from the side/rear)
    for i in range(4):
        x0, x1 = xs[i] + 0.6, xs[i + 1] - 0.6
        p, q = ((x0, yb + 0.65, 0.6), (x1, yb + 0.65, 2.4 + (x1 - x0)))
        if i % 2:
            p, q = (x1, p[1], p[2]), (x0, q[1], q[2])
        bar(a, p, q, s=0.4)
    banner(a, 1.375, yf + 0.03, DECK - 1.25)
    # stair: 6 steps off the left end, descending toward -X, handrail on the front (outer) side
    rise = DECK / 6
    syc, sw = -0.35, 3.5
    stair_x(a, -5.9, syc, sw, 6, rise, 1.0, handrail_y=syc - sw / 2 - 0.85)
    # dressing: chunky boulders at the post feet and stair foot, clover masses with flowers
    rocks(a, [(-3.4, -3.7, 2.2, 2.0, 2.1, 0.4), (4.2, -3.6, 2.0, 1.8, 1.9, 1.2),
              (-10.9, -3.2, 2.0, 1.8, 1.8, 0.8), (6.7, 1.0, 1.8, 1.7, 1.6, 0.2)])
    tufts(a, [(-12.3, -1.0, 1.0), (-10.4, -2.9, 0.95), (-8.0, -3.1, 0.9), (-5.6, -3.4, 1.0),
              (-1.9, -3.4, 0.9), (0.2, -3.5, 1.0), (2.7, -3.4, 0.9), (5.8, -3.4, 1.0),
              (7.0, -1.6, 0.9), (6.9, 2.8, 0.85)])
    o = a.finish()
    return kit.tag(o, "hero", collision="precise", budget=8000,
                   notes="Walkable deck (top z=7), 6-step stair descending -X off the open left end. No vfx.")


# ---------------------------------------------------------------- parts
def build_parts(kit):
    fk = kit.flintkit
    out = []

    a = fk.Asset("WalkUprightPost", "W12 WallWalk part")
    sq_post(a, 0, 0, 8.5, w=1.1)
    band(a, 0, 0, 5.6, w=1.1, n=3)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Square post with rope band."))

    a = fk.Asset("WalkRailing", "W12 WallWalk part")
    for x in (-2.6, 2.6):
        sq_post(a, x, 0, 2.5, w=0.5)
        band(a, x, 0, 2.0, w=0.5, n=1)
    bar(a, (-3.0, 0, 2.05), (3.0, 0, 2.05), s=0.35)
    bar(a, (-3.0, 0, 1.0), (3.0, 0, 1.0), s=0.35)
    out.append(kit.tag(a.finish(), "part", collision="precise", budget=1500, notes="Two-rail railing section."))

    a = fk.Asset("WalkFloorPlank", "W12 WallWalk part")
    a.plank((6, 1, 0.6), loc=(0, 0, 0.3), mat=W, bevel=0.08, jitter=0.02)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Single floor plank."))

    a = fk.Asset("WalkSupportBrace", "W12 WallWalk part")
    # 4.3 tall (not 5) so the parts grid ranks it below the 4.4 stair and sets it in front
    sq_post(a, 0, 0, 4.3, w=0.9)
    bar(a, (-2.2, -2.2, 0.3), (-0.4, -0.4, 2.95), s=0.45)   # 45 deg brace toward the front-left
    a.lashing((-0.45, -0.45, 2.8), size=0.42, thickness=0.09, rot=(math.pi / 2, 0, -math.pi / 4), mat=R)
    band(a, 0, 0, 3.1, w=0.9)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500, notes="Post with 45 deg knee brace."))

    out.append(build_steps_part(kit))
    return out


def build_steps_part(kit):
    a = kit.flintkit.Asset("WalkStairSteps", "W12 WallWalk part")
    for k in range(4):
        d = (4 - k) * 1.2
        a.box((4.0, d, 1.1), loc=(0, d / 2 + k * 1.2 - 2.4, 1.1 * k + 0.55), mat=W, bevel=0.08)
    return kit.tag(a.finish(), "part", collision="precise", budget=1500, notes="4-step block stair.")


# ---------------------------------------------------------------- variants
def build_straight(kit):
    a = kit.flintkit.Asset("WalkStraight", "W12 WallWalk variant", tint_var=0.05)
    dz = 5.4
    xs = [-5.4, -1.8, 1.8, 5.4]
    ys = [-2.45, 2.45]
    bz = dz - 0.85
    for y in ys:
        for x in xs:
            sq_post(a, x, y, dz + 3.0, w=1.3)
            band(a, x, y, dz - 0.9, w=1.3)
            band(a, x, y, dz + 2.15, w=1.3, n=1)
        bar(a, (-6.0, y, bz), (6.0, y, bz), s=0.6)
        for z in (dz + 2.4, dz + 1.3):
            bar(a, (-5.8, y, z), (5.8, y, z), s=0.4)
        side = -0.7 if y < 0 else 0.7
        for i in range(3):
            x0, x1 = xs[i] + 0.6, xs[i + 1] - 0.6
            p, q = (x0, y + side, 0.5), (x1, y + side, bz - 0.4)
            bar(a, p, q, s=0.4)
            bar(a, (x1, y + side, 0.5), (x0, y + side, bz - 0.4), s=0.4)
        a.lashing((0.0, y + side * 1.3, (bz + 0.1) / 2), size=0.33, thickness=0.08,
                  rot=(math.pi / 2, 0, 0), mat=R)
    for x in (xs[0], xs[-1]):
        bar(a, (x, ys[0], bz), (x, ys[1], bz), s=0.5)
    deck(a, -6.0, 6.0, -2.0, 2.0, z=dz)
    rocks(a, [(-6.2, -3.5, 2.0, 1.8, 1.8, 0.3), (2.6, -3.6, 1.9, 1.7, 1.7, 1.0), (6.3, 2.6, 1.7, 1.6, 1.5, 0.6)])
    tufts(a, [(-4.4, -3.5, 0.9), (-0.6, -3.5, 0.95), (4.6, -3.4, 0.9), (6.6, -1.2, 0.85), (-6.6, 1.5, 0.85)])
    return kit.tag(a.finish(), "variant", collision="precise", budget=6000,
                   notes="Straight 12x4 wall walk, rails both sides, X braces. No vfx.")


def build_corner(kit):
    a = kit.flintkit.Asset("WalkCorner", "W12 WallWalk variant")
    # back arm along X (y 0..4.9), left arm along Y (x -4.9..0); corner at back-left
    dz = 5.8
    top = dz + 3.0
    HI, MID = dz + 2.3, dz + 1.2
    posts = [(-4.45, 4.45), (-4.45, 0.0), (-4.45, -4.45), (-0.45, -4.45), (-0.45, -0.45),
             (4.45, -0.45), (4.45, 4.45), (0.0, 4.45)]
    for (x, y) in posts:
        tall = (x, y) == (-4.45, 4.45)
        sq_post(a, x, y, top + (0.9 if tall else 0.0), w=1.2 if tall else POST_W)
        band(a, x, y, dz - 0.9, w=1.2 if tall else POST_W)
    bz = dz - 0.85
    # edge beams
    bar(a, (-4.45, -5.0, bz), (-4.45, 5.0, bz), s=0.55)
    bar(a, (-5.0, 4.45, bz), (5.0, 4.45, bz), s=0.55)
    bar(a, (-0.45, -5.0, bz), (-0.45, 0.0, bz), s=0.5)
    bar(a, (-0.45, -0.45, bz), (5.0, -0.45, bz), s=0.5)
    bar(a, (-4.45, -4.45, bz), (-0.45, -4.45, bz), s=0.5)
    bar(a, (4.45, -0.45, bz), (4.45, 4.45, bz), s=0.5)
    # decks: left arm planks along Y, back arm planks along X
    deck(a, -4.0, 0.0, -4.9, 0.0, along="y")
    deck(a, -4.0, 4.9, 0.0, 4.0, along="x")
    # outer railings (back y and left x)
    for z in (HI, MID):
        bar(a, (-4.45, 4.45, z), (4.75, 4.45, z), s=0.35)
        bar(a, (-4.45, -4.75, z), (-4.45, 4.45, z), s=0.35)
    for (x, y) in [(-4.45, 0.0), (-4.45, -4.45), (0.0, 4.45), (4.45, 4.45)]:
        band(a, x, y, HI - 0.15, n=1)
    # braces: corner gets extra (both faces), plus X under the inner posts
    c = (-4.45, 4.45)
    bar(a, (c[0] + 0.6, c[1] - 0.6, 0.4), (c[0] + 0.6, c[1] - 3.6, dz - 1.4), s=0.4)
    bar(a, (c[0] + 0.6, c[1] - 0.6, 0.4), (c[0] + 3.6, c[1] - 0.6, dz - 1.4), s=0.4)
    bar(a, (-4.45 + 0.6, -4.45 + 0.6, 0.5), (-0.45 - 0.6, -4.45 + 0.6, dz - 1.4), s=0.4)
    bar(a, (-0.45 - 0.6, -4.45 + 0.6, 0.5), (-4.45 + 0.6, -4.45 + 0.6, dz - 1.4), s=0.4)
    bar(a, (4.45, -0.45 + 0.6, 0.5), (4.45, 4.45 - 0.6, dz - 1.4), s=0.4)
    a.lashing((-2.45, -4.45 + 0.75, 2.3), size=0.35, thickness=0.08, rot=(math.pi / 2, 0, 0), mat=R)
    a.lashing((4.6, 2.0, 2.3), size=0.35, thickness=0.08, rot=(0, 0, 0), mat=R)
    # rope bundle on the deck at the corner (coil)
    for k in range(2):
        a.torus(0.5, 0.1, loc=(-3.2, 3.2, dz + 0.1 + k * 0.18), mat=R, seg=10, rseg=4)
    rocks(a, [(-5.6, -5.4, 1.6, 1.4, 1.4, 0.5), (5.4, -1.5, 1.5, 1.4, 1.3, 0.9)])
    tufts(a, [(-5.8, -3.0, 0.85), (-1.8, -5.6, 0.85), (3.0, -1.7, 0.9)])
    return kit.tag(a.finish(), "variant", collision="precise", budget=6000,
                   notes="L-shaped corner, two 8x4 arms, outer rails only, rope bundle. No vfx.")


def build_stairbay(kit):
    a = kit.flintkit.Asset("WalkStairBay", "W12 WallWalk variant")
    n, rise = 8, 1.1
    dz = n * rise  # 8.8 deck top
    top = 11.4
    xs = [-3.5, 0.0, 3.5]
    ys = [-2.45, 2.45]
    for y in ys:
        for x in xs:
            sq_post(a, x, y, top)
            band(a, x, y, dz - 0.9)
            band(a, x, y, top - 0.75, n=1)
        bar(a, (-4.1, y, dz - 0.85), (4.1, y, dz - 0.85), s=0.55)
    for x in (-3.5, 3.5):
        bar(a, (x, -2.45, dz - 0.85), (x, 2.45, dz - 0.85), s=0.5)
    deck(a, -3.9, 3.9, -2.0, 2.0, z=dz)
    hi, mid = top - 0.6, top - 1.7
    for z in (hi, mid):
        bar(a, (-3.8, 2.45, z), (3.8, 2.45, z), s=0.35)
        bar(a, (3.5, -2.75, z), (3.5, 2.75, z), s=0.35)
        bar(a, (0.0, -2.45, z), (3.8, -2.45, z), s=0.35)
    # X braces on the right end and back
    for (p, q) in [((3.5 + 0.6, -1.95, 0.5), (3.5 + 0.6, 1.95, dz - 1.2)),
                   ((3.5 + 0.6, 1.95, 0.5), (3.5 + 0.6, -1.95, dz - 1.2)),
                   ((0.5, 3.05, 0.5), (3.0, 3.05, dz - 1.2)), ((-3.0, 3.05, 0.5), (-0.5, 3.05, dz - 1.2)),
                   ((0.5, -3.05, 0.5), (3.0, -3.05, dz - 1.2))]:
        bar(a, p, q, s=0.4)
    a.lashing((4.25, 0.0, (dz - 0.7) / 2), size=0.35, thickness=0.08, rot=(0, math.pi / 2, 0), mat=R)
    # long stair at the front-left climbing toward +Y to the deck front edge
    stair_y(a, -2.0, -1.75, 3.2, n, rise, 1.05, handrail_x=-3.55)
    rocks(a, [(0.8, -9.0, 1.6, 1.4, 1.4, 0.4), (4.4, -3.5, 1.6, 1.4, 1.4, 1.1)])
    tufts(a, [(-3.9, -10.4, 0.9), (0.6, -10.4, 0.8), (4.6, 3.4, 0.8), (-4.5, -1.0, 0.85)])
    return kit.tag(a.finish(), "variant", collision="precise", budget=6000,
                   notes="Tall deck (8.8) with 8-step stair at front-left, open front-left end. No vfx.")


def build(kit):
    out = [build_hero(kit)]
    out += build_parts(kit)
    out += [build_straight(kit), build_corner(kit), build_stairbay(kit)]
    return out
