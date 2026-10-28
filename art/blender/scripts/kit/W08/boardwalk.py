"""W08 row 3: Boardwalk -- low raised plank walkway with a double-rail fence,
chunky support legs with bold diagonal braces and a plank staircase at one end.

The sheet's FRONT cell draws the long side and its SIDE cell the end, so the
hero and the Straight variant are built along Y and then turned so the length
runs along X (stairs at -X): FRONT (az 0) then shows the long side."""
import math

SUBJECT = "Boardwalk"
ROW = 3
PALETTE = {
    "w08_wood": ("#A8582A", 0.88, 0, 0),
    "w08_pile_wood": ("#5C3420", 0.92, 0, 0),
    "w08_rope": ("#D4A857", 0.95, 0, 0),
    "w08_stone": ("#9CA2AA", 0.95, 0, 0),
    "w08_nail": ("#C48A3C", 0.5, 0.6, 0),
    "w08_banner": ("#B3202A", 0.85, 0, 0),
}
HERO_AZIMUTH = -22
HERO_ELEVATION = 36   # the sheet looks down on the deck from a little higher than default

W, R, N = "w08_wood", "w08_rope", "w08_nail"
DECK = 1.9          # deck top
PT = 0.4           # plank thickness
UNDER = DECK - PT   # underside of the planks
SH = 0.55           # edge stringer height (thick deck band)
SB = UNDER - SH     # stringer bottom
RAIL_TOP = DECK + 2.4
TOP_RAIL_Z = DECK + 1.85
MID_RAIL_Z = DECK + 0.9
RP = 0.65           # rail post width
SP = 0.75           # support post width
NR = 0.15           # brass nail head radius


def bar(a, p1, p2, w, h, mat=W, bevel=0.05, jitter=0.012):
    """Box running from p1 to p2: w across (horizontal), h deep."""
    dx, dy, dz = (p2[i] - p1[i] for i in range(3))
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    pitch = math.atan2(dz, math.hypot(dx, dy))
    yaw = math.atan2(-dx, dy)
    mid = tuple((p1[i] + p2[i]) / 2 for i in range(3))
    return a.box((w, L, h), mid, (pitch, 0, yaw), mat=mat, bevel=bevel, jitter=jitter)


_NAIL_ROT = {"+x": (0, math.pi / 2, 0), "-x": (0, -math.pi / 2, 0),
             "-y": (math.pi / 2, 0, 0), "+y": (-math.pi / 2, 0, 0), "top": (0, 0, 0)}


def nail(a, loc, face, r=NR):
    a.cyl(r, r * 0.75, 0.09, sides=6, loc=loc, rot=_NAIL_ROT[face], mat=N)


def _plank(a, size, loc):
    a.box(size, (loc[0], loc[1], loc[2] + a.rng.uniform(-0.04, 0.04)),
          (a.rng.uniform(-0.008, 0.008), a.rng.uniform(-0.008, 0.008), a.rng.uniform(-0.012, 0.012)),
          mat=W, bevel=0.08, jitter=0.02)


def planks_y(a, x0, x1, y0, y1, pitch=0.6):
    """Planks spanning x0..x1, laid side by side along Y (wide seams across)."""
    n = max(1, round((y1 - y0) / pitch))
    p = (y1 - y0) / n
    for i in range(n):
        yc = y0 + p * (i + 0.5)
        _plank(a, (x1 - x0 + a.rng.uniform(-0.04, 0.04), p - 0.1, PT),
               ((x0 + x1) / 2 + a.rng.uniform(-0.025, 0.025), yc, DECK - PT / 2))


def planks_x(a, x0, x1, y0, y1, pitch=0.6):
    """Planks spanning y0..y1, laid side by side along X."""
    n = max(1, round((x1 - x0) / pitch))
    p = (x1 - x0) / n
    for i in range(n):
        xc = x0 + p * (i + 0.5)
        _plank(a, (p - 0.1, y1 - y0 + a.rng.uniform(-0.04, 0.04), PT),
               (xc, (y0 + y1) / 2 + a.rng.uniform(-0.025, 0.025), DECK - PT / 2))


def rail_post(a, x, y, outward, w=RP, top=RAIL_TOP, bottom=SB + 0.05, nails=True):
    a.box((w, w, top - bottom), (x, y, (top + bottom) / 2), mat=W, bevel=0.06, jitter=0.01)
    if nails:
        nail(a, (x, y, top), "top", r=NR * 1.1)
        sx = {"+x": 1, "-x": -1}.get(outward, 0)
        sy = {"+y": 1, "-y": -1}.get(outward, 0)
        for z in (TOP_RAIL_Z, MID_RAIL_Z, UNDER - SH / 2):
            nail(a, (x + sx * w / 2, y + sy * w / 2, z), outward)


def rails(a, p1, p2, top=TOP_RAIL_Z, mid=MID_RAIL_Z, rope_mid=False):
    """Top rail (0.4 x 0.5) and mid rail between two post points (x, y)."""
    bar(a, (p1[0], p1[1], top), (p2[0], p2[1], top), 0.4, 0.5)
    if rope_mid:
        sag(a, (p1[0], p1[1], mid), (p2[0], p2[1], mid), 0.25)
    else:
        bar(a, (p1[0], p1[1], mid), (p2[0], p2[1], mid), 0.34, 0.4)


def sag(a, p1, p2, drop, segs=6, r=0.075):
    pts = []
    for i in range(segs + 1):
        t = i / segs
        pts.append(tuple(p1[k] + (p2[k] - p1[k]) * t for k in range(3)))
        pts[-1] = (pts[-1][0], pts[-1][1], pts[-1][2] - drop * 4 * t * (1 - t))
    a.tube_loop(pts, r, mat=R, rseg=5, closed=False)


def support(a, x, y, outward, top=UNDER):
    a.box((SP, SP, top), (x, y, top / 2), mat=W, bevel=0.06, jitter=0.01)


def braces(a, xb, ys):
    """Bold diagonal brace pairs on the outer face of the legs: from low on each
    leg up to the stringer, flaring both ways (a V between neighbouring legs)."""
    for y, dirs in ys:
        for d in dirs:
            bar(a, (xb, y + d * 0.35, 0.12), (xb, y + d * 1.7, SB + 0.05), 0.32, 0.36)
            nail(a, (xb + (0.18 if xb > 0 else -0.18), y + d * 0.5, 0.3),
                 "+x" if xb > 0 else "-x", r=NR * 0.8)


def end_braces(a, y, xl):
    """A-frame brace pair between a leg pair (seen in the end view)."""
    for s in (-1, 1):
        bar(a, (s * (xl - 0.45), y, 0.2), (s * 0.35, y, UNDER - 0.55), 0.28, 0.32)


def straight(a, y0, y1, sup_ys, post_ys, rail_sides=(-1, 1), deck_ropes=True):
    """A straight 5-wide walkway from y0 to y1."""
    planks_y(a, -2.62, 2.62, y0, y1)
    xl = 2.1
    for s in (-1, 1):
        # thick edge stringer, bolted to the legs
        a.box((0.45, y1 - y0 - 0.1, SH), (s * 2.3, (y0 + y1) / 2, UNDER - SH / 2), mat=W, bevel=0.06)
        for y in sup_ys:
            support(a, s * xl, y, "+x" if s > 0 else "-x")
            for dy in (-0.25, 0.25):
                nail(a, (s * 2.525, y + dy, UNDER - SH / 2), "+x" if s > 0 else "-x")
        bl = []
        for i, y in enumerate(sup_ys):
            dirs = []
            if i > 0:
                dirs.append(-1)
            if i < len(sup_ys) - 1:
                dirs.append(1)
            bl.append((y, dirs))
        braces(a, s * 2.3, bl)
    for y in sup_ys:
        a.box((4.2, 0.6, 0.6), (0, y, UNDER - 0.3), mat=W, bevel=0.05)
    for y in (sup_ys[0], sup_ys[-1]):
        end_braces(a, y, xl)
    for s in rail_sides:
        xo = s * (2.5 + RP / 2)
        for y in post_ys:
            rail_post(a, xo, y, "+x" if s > 0 else "-x")
        rails(a, (xo, post_ys[0]), (xo, post_ys[-1]))
    if deck_ropes:
        for x in (-0.3, 0.3):
            a.tube_loop([(x, y0 + 0.25, DECK + 0.05), (x, (y0 + y1) / 2, DECK + 0.07),
                         (x, y1 - 0.25, DECK + 0.05)], 0.06, mat=R, rseg=4, closed=False)


def stairs(a, y_top, tops, run=3.0, tread=PT, half=2.0, foot_posts=False, rope_from=None):
    """Stacked plank steps descending toward -Y from y_top; tops = tread top heights."""
    d = run / len(tops)
    for i, top in enumerate(tops):
        yc = y_top - d * (i + 0.5)
        a.box((2 * half + a.rng.uniform(-0.06, 0.06), d - 0.08, tread), (0, yc, top - tread / 2),
              (0, 0, a.rng.uniform(-0.015, 0.015)), mat=W, bevel=0.07, jitter=0.015)
        h = top - tread
        if h > 0.12:   # stacked block under each tread, inset so the plank edge reads
            a.box((2 * half - 0.5, d - 0.3, h), (0, yc + 0.08, h / 2), mat=W, bevel=0.04)
    for s in (-1, 1):
        bar(a, (s * (half - 0.08), y_top - run + 0.25, 0.28),
            (s * (half - 0.08), y_top - 0.05, tops[0] - tread - 0.02), 0.3, 0.5)
        nail(a, (s * (half + 0.08), y_top - run / 2, (tops[0] - tread) / 2 + 0.14), "+x" if s > 0 else "-x")
    if foot_posts:
        yf = y_top - run + 0.35
        for s in (-1, 1):
            xf = s * (half + 0.3)
            a.box((0.5, 0.5, 2.0), (xf, yf, 1.0), mat=W, bevel=0.05)
            nail(a, (xf, yf, 2.0), "top")
            if rope_from:
                sag(a, (s * rope_from[0], rope_from[1], rope_from[2]), (xf, yf, 1.85), 0.25)


def turn(o):
    """Turn the finished mesh so its length runs along X (-Y end -> -X)."""
    from mathutils import Matrix
    o.data.transform(Matrix.Rotation(-math.pi / 2, 4, "Z"))
    o.data.update()
    d = o.dimensions
    o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    return o


def build(kit):
    fk = kit.flintkit
    out = []

    # ---------------- hero ----------------
    a = fk.Asset("Boardwalk", "W08 Boardwalk")
    post_ys = [-5.7, -1.9, 1.9, 5.7]
    straight(a, -6.0, 6.0, [-5.2, 0.0, 5.2], post_ys)
    stairs(a, -6.0, [1.425, 0.95, 0.475], foot_posts=True, rope_from=(2.5 + RP / 2, -5.7, TOP_RAIL_Z))
    o = turn(a.finish())
    out.append(kit.tag(o, "hero", collision="precise", budget=7000,
                       notes="Raised plank boardwalk, length along X, deck at 1.6 studs, 3-step stairs at -X. No VFX."))

    # ---------------- parts ----------------
    # Posts are authored lying along X so the parts cell does not hide the
    # stairs and plank behind two tall posts; stand them up when placing.
    a = fk.Asset("BoardwalkRailPost", "W08 BoardwalkRailPost")
    a.box((3.0, RP, RP), (0, 0, RP / 2), mat=W, bevel=0.06, jitter=0.01)
    nail(a, (1.5, 0, RP / 2), "+x", r=NR * 1.1)
    for x in (0.9, -0.1):
        nail(a, (x, 0, RP), "top")
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Rail post with brass nails (lies along X; top end at +X)."))

    a = fk.Asset("BoardwalkRail", "W08 BoardwalkRail")
    a.box((6.0, 0.4, 0.5), (0, 0, 0.25), mat=W, bevel=0.06, jitter=0.01)
    for x in (-2.7, 2.7):
        nail(a, (x, 0, 0.5), "top")
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Top/mid rail beam."))

    a = fk.Asset("BoardwalkFloorPlank", "W08 BoardwalkFloorPlank")
    a.box((3.0, 0.8, 0.4), (0, 0, 0.2), mat=W, bevel=0.08, jitter=0.02)
    for x in (-1.2, 1.2):
        nail(a, (x, 0, 0.4), "top", r=NR * 0.8)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Single thick floor plank."))

    a = fk.Asset("BoardwalkSupportPost", "W08 BoardwalkSupportPost")
    a.box((3.5, SP, SP), (0, 0, SP / 2), mat=W, bevel=0.07, jitter=0.01)
    for x in (1.2, 0.6):
        nail(a, (x, 0, SP), "top")
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Support leg (lies along X; top end at +X)."))

    a = fk.Asset("BoardwalkStairs", "W08 BoardwalkStairs")
    stairs(a, 1.5, [1.6, 1.07, 0.53], tread=0.5)
    out.append(kit.tag(a.finish(), "part", collision="precise", budget=1500, notes="3-step stacked plank stairs."))

    a = fk.Asset("BoardwalkCrossbeam", "W08 BoardwalkCrossbeam")
    a.box((5.0, 0.6, 0.6), (0, 0, 0.3), mat=W, bevel=0.06, jitter=0.01)
    for x in (-2.2, 2.2):
        nail(a, (x, -0.3, 0.3), "-y")
        nail(a, (x, 0, 0.6), "top")
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Heavy crossbeam."))

    # ---------------- variants ----------------
    a = fk.Asset("BoardwalkStraight", "W08 BoardwalkStraight")
    straight(a, -4.0, 4.0, [-3.4, -1.15, 1.15, 3.4], [-3.7, 0.0, 3.7])
    out.append(kit.tag(turn(a.finish()), "variant", collision="precise", budget=5000,
                       notes="A. Straight 8-stud section along X, rails both sides."))

    a = fk.Asset("BoardwalkCorner", "W08 BoardwalkCorner")
    build_corner(a)
    out.append(kit.tag(turn(a.finish()), "variant", collision="precise", budget=5000,
                       notes="B. Corner (L) 6x6, rails on outer edges, big corner post."))

    a = fk.Asset("BoardwalkRampEnd", "W08 BoardwalkRampEnd")
    build_ramp(a)
    out.append(kit.tag(turn(a.finish()), "variant", collision="precise", budget=5000,
                       notes="C. Ramp End: 25 degree cleated ramp with sloped handrail and rope."))
    return out


def build_corner(a):
    # deck: arm along Y (x -3..1, y -3..-1) + arm along X (x -3..3, y -1..3)
    planks_y(a, -3.0, 1.0, -3.0, -1.0)
    planks_x(a, -3.0, 3.0, -1.0, 3.0)
    outline = [(-3, -3), (1, -3), (1, -1), (3, -1), (3, 3), (-3, 3)]
    for i, p in enumerate(outline):
        q = outline[(i + 1) % len(outline)]
        bar(a, (p[0], p[1], UNDER - SH / 2), (q[0], q[1], UNDER - SH / 2), 0.42, SH)
    sups = [(-2.65, -2.65, "-y"), (0.65, -2.65, "-y"), (2.65, -0.65, "+x"), (2.65, 2.65, "+x"),
            (-2.65, 2.65, "-x"), (0.65, -0.65, "-y"), (-2.65, 0.3, "-x"), (0.0, 2.65, "+y")]
    for x, y, f in sups:
        support(a, x, y, f)
    for y in (-2.65, 0.3, 2.65):
        for dy in (-0.25, 0.25):
            nail(a, (-3.22, y + dy, UNDER - SH / 2), "-x")
    for x in (-2.65, 0.0, 2.65):
        for dx in (-0.25, 0.25):
            nail(a, (x + dx, 3.22, UNDER - SH / 2), "+y")
    for x in (-2.65, 0.65):
        nail(a, (x, -3.22, UNDER - SH / 2), "-y")
    # bold brace pairs on the two outer faces and the front face
    for x, dirs in [(-2.65, (1,)), (0.0, (-1, 1)), (2.65, (-1,))]:
        for d in dirs:
            bar(a, (x + d * 0.35, 2.8, 0.12), (x + d * 1.5, 2.8, SB + 0.05), 0.32, 0.36)
    braces(a, -2.8, [(-2.65, (1,)), (0.3, (-1, 1)), (2.65, (-1,))])
    bar(a, (-2.3, -2.8, 0.12), (-1.0, -2.8, SB + 0.05), 0.32, 0.36)
    bar(a, (0.3, -2.8, 0.12), (-0.7, -2.8, SB + 0.05), 0.32, 0.36)
    for x, y in ((-2.65, -2.65), (0.65, -2.65), (2.65, 2.65), (-2.65, 2.65)):
        for f, dx, dy in (("-x", -SP / 2, 0), ("-y", 0, -SP / 2), ("+x", SP / 2, 0), ("+y", 0, SP / 2)):
            nail(a, (x + dx, y + dy, 0.35), f, r=NR * 0.8)
    a.box((4.0, 0.6, 0.6), (-1.0, -2.65, UNDER - 0.3), mat=W, bevel=0.05)
    a.box((6.0, 0.6, 0.6), (0.0, 0.8, UNDER - 0.3), mat=W, bevel=0.05)
    a.box((0.6, 4.0, 0.6), (2.65, 1.0, UNDER - 0.3), mat=W, bevel=0.05)
    # outer rails: x = -3 side and y = +3 side, big corner post
    xo, yo = -3.0 - RP / 2, 3.0 + RP / 2
    for y in (-2.7, 0.2):
        rail_post(a, xo - 0.2, y, "-x")
    for x in (0.2, 2.7):
        rail_post(a, x, yo + 0.2, "+y")
    xo, yo = xo - 0.2, yo + 0.2
    ct = RAIL_TOP + 0.35
    a.box((0.95, 0.95, ct - SB), (xo, yo, (ct + SB) / 2), mat=W, bevel=0.07)
    nail(a, (xo, yo, ct), "top", r=NR * 1.3)
    nail(a, (xo - 0.475, yo, TOP_RAIL_Z), "-x")
    nail(a, (xo, yo + 0.475, TOP_RAIL_Z), "+y")
    rails(a, (xo, -2.7), (xo, yo))
    rails(a, (xo, yo), (2.7, yo))
    for x in (-1.3, -0.7):
        a.tube_loop([(x, -2.8, DECK + 0.05), (x, 2.8, DECK + 0.05)], 0.06, mat=R, rseg=4, closed=False)


def build_ramp(a):
    RUN = 3.3
    slope = (DECK - 0.3) / RUN         # ~25 degrees
    straight(a, 0.0, 5.0, [0.45, 2.5, 4.6], [], rail_sides=(), deck_ropes=False)
    a.box((4.6, 0.5, 0.3), (0, -RUN - 0.05, 0.15), mat=W, bevel=0.04)   # toe board at the ramp foot
    # ramp planks along the slope, from (y=0, z=1.6) down to (y=-2.8, z=0.3)
    L = math.hypot(RUN, DECK - 0.3)
    dy, dz = -RUN / L, -(DECK - 0.3) / L
    ny, nz = dz, -dy              # unit normal of the ramp surface
    if nz < 0:
        ny, nz = -ny, -nz
    n = 7
    for i in range(n):
        t0, t1 = L * i / n + 0.05, L * (i + 1) / n - 0.05
        p1 = (0, dy * t0 - ny * PT / 2, DECK + dz * t0 - nz * PT / 2)
        p2 = (0, dy * t1 - ny * PT / 2, DECK + dz * t1 - nz * PT / 2)
        bar(a, p1, p2, 4.6 + a.rng.uniform(-0.06, 0.06), PT, bevel=0.06)
        tc = (t0 + t1) / 2
        c = (dy * tc + ny * 0.05, DECK + dz * tc + nz * 0.05)
        bar(a, (-2.1, c[0], c[1]), (2.1, c[0], c[1]), 0.16, 0.14, bevel=0.02)
        for x in (-1.6, 1.6):
            nail(a, (x, c[0] + ny * 0.07, c[1] + nz * 0.07), "top", r=NR * 0.7)
    for s in (-1, 1):
        bar(a, (s * 2.05, -RUN + 0.1, 0.2), (s * 2.05, 0.0, UNDER - 0.15), 0.34, 0.5)
    # handrail along -X: flat posts then posts following the slope
    xo = -2.5 - RP / 2

    def surf(y):
        return DECK if y >= 0 else DECK + y * slope

    flat = [4.7, 2.2, -0.2]
    for y in flat:
        rail_post(a, xo, y, "-x")
    ramp_ys = [-1.6, -RUN + 0.25]
    for y in ramp_ys:
        top = surf(y) + RAIL_TOP - DECK
        a.box((RP, RP, top), (xo, y, top / 2), mat=W, bevel=0.06)
        nail(a, (xo, y, top), "top", r=NR * 1.1)
        nail(a, (xo - RP / 2, y, surf(y) + TOP_RAIL_Z - DECK), "-x")
    rails(a, (xo, 4.7), (xo, -0.2))
    bar(a, (xo, -0.2, TOP_RAIL_Z), (xo, -RUN + 0.25, surf(-RUN + 0.25) + TOP_RAIL_Z - DECK), 0.4, 0.5)
    sag(a, (xo, -0.2, MID_RAIL_Z), (xo, -RUN + 0.25, surf(-RUN + 0.25) + MID_RAIL_Z - DECK), 0.2)
    # end rail across the +Y end
    xr = 2.5 + RP / 2
    rail_post(a, xr, 4.7, "+x")
    rails(a, (xo, 4.7), (xr, 4.7))
