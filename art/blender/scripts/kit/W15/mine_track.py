"""W15 row 2: MineTrack - rails, ties and junctions.

Track runs along +Y (cart wheels sit on rails), front -Y, origin bottom centre.
Gauge: rail centres at x = +/-1.8 (3.0 studs clear between rails), ties 6 wide.
"""
import math
import random

SUBJECT = "MineTrack"
ROW = 2
HERO_AZIMUTH = 202   # rear-left: the +Y end (buffer) is nearest, track runs lower-left to upper-right
SIDE_AZIMUTH = 90
HERO_ELEVATION = 38   # the sheet's iso cells are drawn from higher up

PALETTE = {
    "w15_timber": ("#A9662B", 0.85, 0, 0),
    "w15_iron": ("#65738D", 0.6, 0, 0),   # verifier: sheet value #454B66 rendered near-black navy
    "w15_rock": ("#8E8E96", 0.95, 0, 0),
    "w15_sand": ("#D4B98E", 1, 0, 0),
    "w15_foliage": ("#3E9A22", 0.9, 0, 0),
}

T, I, R, S, F = "w15_timber", "w15_iron", "w15_rock", "w15_sand", "w15_foliage"

HALF_GAUGE = 1.8
RAIL_W, RAIL_H = 0.55, 0.62
TIE_W, TIE_D, TIE_H = 6.0, 1.0, 0.75
TIE_Z0 = 0.1                      # ties sit on the sand pad
RAIL_Z0 = TIE_Z0 + TIE_H          # rails sit on the ties


# ---------------------------------------------------------------- paths
def straight_path(y0, length):
    def f(s):
        return (0.0, y0 + s, 0.0)
    return f, length


def arc_path(x0, y0, radius, angle, sign=1):
    """Start at (x0, y0) heading +Y, turning toward +X (sign=1) or -X."""
    cx = x0 + sign * radius

    def f(s):
        a = s / radius
        x = cx - sign * radius * math.cos(a)
        y = y0 + radius * math.sin(a)
        return (x, y, -sign * a)
    return f, radius * angle


def lateral(p, off):
    x, y, phi = p
    return (x + off * math.cos(phi), y + off * math.sin(phi))


# ---------------------------------------------------------------- pieces
def tie(a, rng, p, width=TIE_W, extra_right=0.0, jitter=True):
    x, y, phi = p
    w = width + (rng.uniform(-0.2, 0.2) if jitter else 0) + extra_right
    shift = extra_right / 2
    cx, cy = x + shift * math.cos(phi), y + shift * math.sin(phi)
    d = TIE_D + (rng.uniform(-0.08, 0.1) if jitter else 0)
    h = TIE_H + (rng.uniform(-0.05, 0.03) if jitter else 0)
    rz = phi + (rng.uniform(-0.05, 0.05) if jitter else 0)
    a.box((w, d, h), (cx, cy, TIE_Z0 + h / 2), (0, 0, rz), T)


def clamp(a, p, off):
    """Small iron bracket plates either side of the rail foot, each with a bolt head."""
    phi = p[2]
    for side in (-1, 1):
        x, y = lateral(p, off + side * (RAIL_W / 2 + 0.17))
        a.box((0.32, 0.6, 0.3), (x, y, RAIL_Z0 + 0.15), (0, 0, phi), I)
        a.cyl(0.1, 0.08, 0.08, sides=6, loc=(x, y, RAIL_Z0 + 0.3), mat=I)


def rail_along(a, path, length, off, steps):
    pts = [path(length * i / steps) for i in range(steps + 1)]
    for p0, p1 in zip(pts, pts[1:]):
        x0, y0 = lateral(p0, off)
        x1, y1 = lateral(p1, off)
        seg = math.hypot(x1 - x0, y1 - y0)
        phi = math.atan2(-(x1 - x0), y1 - y0)
        a.box((RAIL_W, seg + 0.06, RAIL_H), ((x0 + x1) / 2, (y0 + y1) / 2, RAIL_Z0 + RAIL_H / 2),
              (0, 0, phi), I)


def track(a, rng, path, length, n_ties, rail_steps=1, ties=True, clamps=True, margin=0.6):
    if ties:
        tpos = [path(margin + (length - 2 * margin) * i / (n_ties - 1)) for i in range(n_ties)]
        for p in tpos:
            tie(a, rng, p)
    else:
        tpos = []
    for off in (-HALF_GAUGE, HALF_GAUGE):
        rail_along(a, path, length, off, rail_steps)
        if clamps:
            for p in tpos:
                clamp(a, p, off)
    return tpos


def sand_pad(a, outline, depth=0.1):
    a.poly_prism(outline, depth, (0, 0, 0), (0, 0, 0), S)


def ribbon_outline(path, length, half_w, steps):
    left, right = [], []
    for i in range(steps + 1):
        s = length * i / steps
        p = path(s)
        left.append(lateral(p, -half_w))
        right.append(lateral(p, half_w))
    # extend ends a little along the track
    return right + list(reversed(left))


def ccw(points):
    area = 0.0
    for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
        area += x0 * y1 - x1 * y0
    return points if area > 0 else list(reversed(points))


def tuft(a, loc, r=0.45):
    a.leaf_cluster(r, loc, F, lobes=6, squash=0.75, floor=0.0)


# ---------------------------------------------------------------- assets
def build_hero(kit, fk):
    rng = random.Random(1502)
    a = fk.Asset("MineTrack", "W15 MineTrack")
    L = 10.0
    y0 = -L / 2 - 0.6
    # sandy pad (irregular, long and narrow along the track)
    pad = [(-3.9, -7.0), (-0.8, -7.5), (2.6, -7.2), (4.6, -5.4), (5.0, -1.6), (4.8, 2.6),
           (4.5, 6.2), (2.4, 7.9), (-1.0, 8.2), (-3.8, 7.4), (-4.8, 4.0), (-5.0, 0.0), (-4.7, -4.4)]
    sand_pad(a, ccw(pad), 0.12)
    path, length = straight_path(y0, L)
    track(a, rng, path, length, 7, margin=0.7)
    # big timber end buffer at the camera-near (+Y) end: two posts on footings + crossbeam
    yb = y0 + L + 1.3
    for sx in (-1, 1):
        x = sx * 2.4
        a.box((2.0, 2.0, 0.8), (x, yb, 0.4), (0, 0, rng.uniform(-0.06, 0.06)), T)
        a.box((1.4, 1.4, 2.5), (x, yb, 0.8 + 1.25), (0, 0, rng.uniform(-0.03, 0.03)), T)
        a.box((1.5, 1.5, 0.28), (x, yb, 2.75), (0, 0, 0), I)        # iron strap band
    a.box((6.3, 1.0, 0.95), (0, yb - 0.75, 2.2), (0, 0, 0), T)       # crossbeam across the track end
    a.box((0.35, 1.1, 1.05), (0, yb - 0.75, 2.2), (0, 0, 0), I)      # iron strap on the beam
    for x in (-1.2, 1.2):
        a.cyl(0.13, 0.11, 0.1, sides=6, loc=(x, yb - 1.25, 2.2), rot=(math.pi / 2, 0, 0), mat=I)
    # small stop post at the far end beside the right rail
    a.box((1.5, 1.5, 0.6), (3.3, y0 - 0.2, 0.3), (0, 0, 0.1), T)
    a.box((1.0, 1.0, 1.4), (3.3, y0 - 0.2, 1.3), (0, 0, 0.1), T)
    # grey faceted rocks round the pad (smaller, chunky facets)
    a.rock((2.8, 2.6, 2.4), (-3.9, -4.6, 0), (0, 0, 0.4), R, subdiv=1, rough=0.2, facets=24)
    a.rock((1.6, 1.4, 1.3), (-4.3, -2.3, 0), (0, 0, 1.1), R, subdiv=1, rough=0.2, facets=24)
    a.rock((2.8, 2.6, 2.4), (4.1, 3.4, 0), (0, 0, 0.8), R, subdiv=1, rough=0.2, facets=24)
    a.rock((1.7, 1.5, 1.4), (3.9, -3.2, 0), (0, 0, 2.0), R, subdiv=1, rough=0.2, facets=24)
    a.rock((2.3, 2.0, 1.9), (-1.0, -7.0, 0), (0, 0, 0.6), R, subdiv=1, rough=0.2, facets=24)
    # bright leafy tufts at rock bases and beside the buffer
    for loc, r in (((-2.8, -3.3, 0.25), 0.8), ((-4.4, -0.6, 0.25), 0.7), ((3.4, 1.6, 0.25), 0.85),
                   ((4.3, -1.6, 0.25), 0.7), ((-4.0, 6.4, 0.25), 0.75), ((0.6, -7.1, 0.25), 0.7)):
        tuft(a, loc, r)
    o = a.finish()
    return kit.tag(o, "hero", collision="precise", budget=3000,
                   notes="Straight mine track (10 long, 7 ties) with tall timber end buffer, far stop post, "
                         "sand pad, rocks, tufts. Track runs along Y, gauge 3.0 clear (rails at x=+/-1.8). No VFX.")


def build_parts(kit, fk):
    rng = random.Random(77)
    out = []
    # rail segment (lies along X for display)
    a = fk.Asset("MineTrackRailSegment", "W15 MineTrack part")
    # rail lies along Y so the parts grid sets it beside the buffer, apart from tie and bracket
    a.box((RAIL_W, 8.0, RAIL_H), (0, 0, RAIL_H / 2), (0, 0, 0), I)
    for y in (-3.4, 0.0, 3.4):
        a.box((0.7, 0.5, 0.2), (0, y, RAIL_H + 0.1), (0, 0, 0), I)
        a.cyl(0.12, 0.1, 0.08, sides=6, loc=(0, y, RAIL_H + 0.2), mat=I)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Single iron rail, 8 studs, 3 bolt plates."))
    # wooden tie
    a = fk.Asset("MineTrackWoodenTie", "W15 MineTrack part")
    a.box((1.0, 6.0, 0.7), (0, 0, 0.35), (0, 0, 0), T)
    for y in (-1.8, 1.8):
        a.cyl(0.16, 0.14, 0.1, sides=6, loc=(0, y, 0.7), mat=I)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Single timber tie 6x1x0.7 with 2 bolt dots."))
    # join bracket: bolts on the front (-Y) face
    a = fk.Asset("MineTrackJoinBracket", "W15 MineTrack part")
    a.box((3.0, 0.8, 0.6), (0, 0, 0.3), (0, 0, 0), I)
    for x in (-1.05, -0.35, 0.35, 1.05):
        a.cyl(0.17, 0.14, 0.16, sides=8, loc=(x, -0.4, 0.3), rot=(math.pi / 2, 0, 0), mat=I)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Iron fish-plate joining two rails, 4 bolt heads."))
    # end buffer
    a = fk.Asset("MineTrackEndBuffer", "W15 MineTrack part")
    for x, h in ((-1.4, 1.7), (1.4, 2.3)):
        a.box((1.5, 1.5, 0.7), (x, 0, 0.35), (0, 0, rng.uniform(-0.08, 0.08)), T)
        a.box((1.1, 1.1, h), (x, 0, 0.7 + h / 2), (0, 0, 0), T)
    a.box((1.2, 1.2, 0.25), (1.4, 0, 2.6), (0, 0, 0), I)
    a.box((3.9, 0.85, 0.85), (0, -0.05, 1.7), (0, 0, 0), T)
    a.box((0.3, 0.95, 0.95), (0.0, -0.05, 1.7), (0, 0, 0), I)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Timber stop buffer: two posts on footings, crossbar, iron strap."))
    return out


def build_variants(kit, fk):
    out = []
    # straight, 16 studs
    rng = random.Random(5)
    a = fk.Asset("MineTrackStraight", "W15 MineTrack variant")
    path, length = straight_path(-8.0, 16.0)
    sand_pad(a, ccw(ribbon_outline(path, length, 3.8, 1)))
    track(a, rng, path, length, 8, margin=0.8)
    out.append(kit.tag(a.finish(), "variant", collision="precise", budget=3500,
                       notes="Straight Track: 16-stud straight, 8 ties, snaps on the 32 grid."))
    # curved: 90 deg, radius 16
    rng = random.Random(6)
    a = fk.Asset("MineTrackCurved", "W15 MineTrack variant")
    path, length = arc_path(8.0, -8.0, 16.0, math.pi / 2, sign=-1)   # chord runs into the view
    sand_pad(a, ccw(ribbon_outline(path, length, 3.8, 12)))
    track(a, rng, path, length, 12, rail_steps=16, margin=0.8)
    out.append(kit.tag(a.finish(), "variant", collision="precise", budget=3500,
                       notes="Curved Track: 90 deg arc radius 16, ties fan radially."))
    # fork / switch
    rng = random.Random(7)
    a = fk.Asset("MineTrackFork", "W15 MineTrack variant")
    y0, L = -6.0, 12.0
    mpath, mlen = straight_path(y0, L)
    bang = math.radians(58)
    bpath, blen = arc_path(0.0, y0, 12.0, bang)
    # sand outline: main left edge + branch outer edge
    bend = bpath(blen)
    outer = [lateral(bpath(blen * i / 8), 3.8) for i in range(9)]
    inner_end = lateral(bend, -3.8)
    # where the branch end cap meets the main track's right sand edge
    ox, oy = outer[-1]
    ix, iy = inner_end
    t = (ox - 3.8) / (ox - ix) if ox != ix else 0
    pad = [(-3.8, y0 - 0.4), (3.8, y0 - 0.4)] + outer[1:] + \
          [(3.8, oy + t * (iy - oy)), (3.8, y0 + L + 0.4), (-3.8, y0 + L + 0.4)]
    sand_pad(a, ccw(pad))
    # ties: main ties, widened to the right where the branch still overlaps
    n = 8
    for i in range(n):
        s = 0.6 + (L - 1.2) * i / (n - 1)
        p = mpath(s)
        # branch centre offset at this y
        sb = min(blen, s)
        bx = bpath(sb)[0]
        extra = 0.0
        extra = (bx + 0.3 if bx > 0.2 else 0.0) if bx < 3.0 else 0.0
        tie(a, rng, p, extra_right=extra)
    # branch's own ties once it has diverged, fanning along the curve
    bties = [s for s in (blen * f for f in (0.6, 0.73, 0.86, 0.97))]
    for s in bties:
        tie(a, rng, bpath(s))
        for off in (-HALF_GAUGE, HALF_GAUGE):
            clamp(a, bpath(s), off)
    for off in (-HALF_GAUGE, HALF_GAUGE):
        rail_along(a, mpath, mlen, off, 1)
        rail_along(a, bpath, blen, off, 10)
    # clamps on the main ties
    for i in range(n):
        s = 0.6 + (L - 1.2) * i / (n - 1)
        for off in (-HALF_GAUGE, HALF_GAUGE):
            clamp(a, mpath(s), off)
    out.append(kit.tag(a.finish(), "variant", collision="precise", budget=3500,
                       notes="Fork / Switch: main straight with a 58 deg branch curving right, "
                             "shared long ties at the switch."))
    return out


def build(kit):
    fk = kit.flintkit
    out = [build_hero(kit, fk)]
    out += build_parts(kit, fk)
    out += build_variants(kit, fk)
    return out
