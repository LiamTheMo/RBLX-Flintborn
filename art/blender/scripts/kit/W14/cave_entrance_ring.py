"""W14 row 1: CaveEntranceRing -- free-standing cave mouth of stacked faceted boulders.

Structure (hero): two tall angular slab pillars per side leaning ~5 deg inward, shoulder
rocks rounding the upper corners, one dominant flat-topped cap rock, smaller crown
boulders on top/back, low back closure (y>=+6, z<9) for a shallow hollow, sand floor
inside and a fan of sand plates out to y=-16, rubble and fern fans at the feet.
"""
import math
import random

SUBJECT = "CaveEntranceRing"
ROW = 1
HERO_AZIMUTH = -22
SIDE_AZIMUTH = -70   # the sheet's side cell is lit; 90 puts the side in full shadow
PALETTE = {
    "w14_rock": ("#8C7F7A", 0.95, 0, 0),
    "w14_sand": ("#C79B6C", 1, 0, 0),
    "w14_moss": ("#5C8A2E", 0.9, 0, 0),
}
R, S, M = "w14_rock", "w14_sand", "w14_moss"
TV = 0.045  # per-part tint variation (small random, not shading)
LEAN = math.radians(5)


def _asset(fk, name, label):
    return fk.Asset(name, label, tint_var=TV)


def _rk(a, rng, size, loc, lean=0.0, sub=2, yaw=0.6, flat=None):
    """Chunky boulder with few big facets; loc z is its base. lean = rot about y.
    flat: clamp the top to this height (flat-topped cap rocks)."""
    rot = (rng.uniform(-0.06, 0.06), lean + rng.uniform(-0.03, 0.03), rng.uniform(-yaw, yaw))
    v = a.rock(size, loc, rot, mat=R, subdiv=sub, rough=0.13, facets=26, sink=0.1)
    if flat is not None:
        for p in v:
            if p.co.z > flat:
                p.co.z = flat
    return v


def _slab(a, rng, size, loc, side, sub=1):
    """Tall angular slab pillar (few big planes), leaning inward."""
    return _rk(a, rng, size, loc, lean=side * LEAN, sub=sub, yaw=0.25)


def _plate(a, rng, r, loc, sides=7, h=1.0):
    return a.cyl(r, r * 0.9, h, sides=sides, loc=loc, rot=(0, 0, rng.uniform(0, 1.0)),
                 mat=S, jitter=0.22)


def _fern(a, rng, loc, r=4.4, n=11):
    """Spiky leaf fan: thin tilted blades radiating from one point."""
    for i in range(n):
        yaw = 2 * math.pi * i / n + rng.uniform(-0.25, 0.25)
        tilt = rng.uniform(0.7, 1.05)
        h = r * rng.uniform(0.85, 1.15)
        a.cyl(1.0, 0.02, h, sides=3, loc=loc, rot=(tilt, 0, yaw), mat=M)
    a.cyl(0.4, 0.02, r * 0.9, sides=3, loc=loc, rot=(0.15, 0, 0), mat=M)


def _pebbles(a, rng, pts):
    for (x, y, rr) in pts:
        a.rock((rr * 1.4, rr * 1.2, rr), (x, y, 0), (0, 0, rng.uniform(0, 3)),
               mat=R, subdiv=1, rough=0.1, facets=20, sink=0.1)


def _walls(a, rng, xi, h, t=6.4):
    """Each side, inner face at |x| = xi: a tall chunky front slab (t x 7 x 0.78h), a
    smaller angular rock stacked on it up to h, and a back slab closing the side.
    All lean ~5 deg inward."""
    for sx in (-1, 1):
        x = sx * (xi + t / 2)
        _slab(a, rng, (t, 7.0, h * 0.78), (x, -1.0, 0), -sx, sub=2)
        _rk(a, rng, (t * 0.9, 6.4, h * 0.36), (x - sx * 0.7, -0.6, h * 0.64),
            lean=-sx * 0.18, sub=2, yaw=0.3)
        _slab(a, rng, (t * 0.95, 6.5, h * 0.86), (x + sx * 0.5, 5.2, 0), -sx, sub=2)


def _back(a, rng, half_w, top=8.0, y=10.4):
    """Low back closure: shallow hollow, keeps the opening reading open."""
    n = 3 if half_w > 8 else 2
    w = (2 * half_w + 2) / n
    for i in range(n):
        x = -half_w - 1 + w * (i + 0.5)
        _rk(a, rng, (w + 1.2, 5.0, top), (x, y, 0), sub=1)


def _floor_and_dress(a, rng, half, inner_r=6.5, big=6.0):
    """Sand floor inside, fan apron to y=-16, rubble (big one front-left), pebbles, ferns."""
    _plate(a, rng, inner_r, (0, 3.0, 0), sides=7, h=0.8)
    for (r, x, y, sides) in [(4.8, 0.3, -6.4, 8), (4.4, -5.6, -10.6, 6), (4.3, 5.4, -10.8, 7),
                             (3.6, -0.2, -12.6, 6)]:
        _plate(a, rng, r, (x, y, 0), sides=sides, h=1.0)
    # rubble: big boulder clearly in front of the left wall, small stones elsewhere
    _rk(a, rng, (big, big * 0.95, big * 0.85), (-half - 1.2, -9.6, 0), sub=2)
    _rk(a, rng, (2.8, 2.6, 2.3), (-half + 3.4, -13.4, 0), sub=1)
    _rk(a, rng, (2.4, 2.4, 2.0), (-half - 1.4, -3.4, 0), sub=1)
    _rk(a, rng, (3.2, 3.0, 2.6), (half + 0.6, -7.4, 0), sub=1)
    _rk(a, rng, (2.2, 2.2, 1.8), (half - 1.0, -12.0, 0), sub=1)
    _pebbles(a, rng, [(-3.2, -15.2, 0.9), (4.4, -15.4, 0.8), (9.0, -14.6, 0.9),
                      (-8.6, -14.8, 0.8)])
    _fern(a, rng, (-half + 3.2, -4.8, 0))
    _fern(a, rng, (half - 2.4, -4.8, 0), 4.0)
    _fern(a, rng, (8.6, -11.6, 0.8), 3.6)


def build_hero(fk):
    rng = random.Random(1401)
    a = _asset(fk, "CaveEntranceRing", "W14 CaveEntranceRing")
    _walls(a, rng, xi=7.3, h=18.5)
    for sx in (-1, 1):  # shoulder rocks round the upper corners of the opening
        _rk(a, rng, (5.6, 6.5, 5.2), (sx * 6.6, -0.8, 10.0), lean=-sx * 0.35, sub=2)
    # dominant flat-topped cap rock: 16 x 12 x 7, bottom at 12.6
    _rk(a, rng, (16.5, 12.0, 8.2), (0, 0.6, 12.6), yaw=0.08, flat=20.0)
    # smaller crown boulders (<= 7) on top / behind
    _rk(a, rng, (6.5, 6.0, 5.0), (-3.6, 3.4, 18.6))
    _rk(a, rng, (6.0, 5.5, 4.4), (3.8, 4.0, 18.2))
    _rk(a, rng, (8.0, 6.5, 6.5), (0.2, 7.6, 12.6))
    _rk(a, rng, (5.0, 5.0, 4.0), (-8.6, 5.4, 16.0))
    _rk(a, rng, (4.6, 4.6, 3.6), (8.8, 5.6, 15.6))
    _back(a, rng, 8.0)
    _rk(a, rng, (13.0, 5.5, 6.0), (0, 10.8, 7.0))  # upper back, recessed (roofs the hollow)
    _floor_and_dress(a, rng, 13.2, big=7.2)
    return a.finish()


def build_rounded(fk):
    rng = random.Random(1421)
    a = _asset(fk, "CaveEntranceRingRounded", "A. Rounded Entrance")
    xi = 6.0
    for sx in (-1, 1):
        _slab(a, rng, (6.0, 7.0, 10.0), (sx * (xi + 3.0), -1.0, 0), -sx, sub=2)
        _slab(a, rng, (6.0, 6.5, 10.5), (sx * (xi + 3.4), 5.0, 0), -sx, sub=2)
    # semicircular crown: opening radius 6 centred at z=7 -> 13 tall
    rc, zc = xi + 2.8, 7.0
    for layer, (y, angs) in enumerate([(-0.8, (25, 58, 90, 122, 155)), (4.8, (40, 90, 140))]):
        for d in angs:
            th = math.radians(d)
            s = 6.0 if layer == 0 else 6.4
            cx, cz = rc * math.cos(th), zc + rc * math.sin(th)
            _rk(a, rng, (s * 1.1, 6.0, s), (cx, y, max(cz - s * 0.5, 0)),
                lean=(math.pi / 2 - th) * 0.9, sub=2, yaw=0.2)
    _back(a, rng, 6.5)
    _rk(a, rng, (10.0, 5.0, 6.0), (0, 9.8, 7.4), sub=1)
    _floor_and_dress(a, rng, 12.6, inner_r=5.6)
    return a.finish()


def build_wide(fk):
    rng = random.Random(1422)
    a = _asset(fk, "CaveEntranceRingWide", "B. Wide Entrance")
    xi = 10.0
    _walls(a, rng, xi=xi, h=14.0, t=5.6)
    for sx in (-1, 1):
        _rk(a, rng, (4.4, 6.0, 3.8), (sx * 9.0, -0.8, 8.4), lean=-sx * 0.3, sub=2)
    # long low flat cap across the 20-wide opening
    _rk(a, rng, (12.5, 10.0, 6.0), (-5.2, 0.4, 10.2), yaw=0.08, flat=15.8)
    _rk(a, rng, (12.5, 10.0, 6.0), (5.4, 0.8, 10.4), yaw=0.08, flat=16.0)
    _rk(a, rng, (8.0, 7.0, 5.0), (0.4, 3.4, 15.0), sub=1)      # the extra top boulder
    _rk(a, rng, (5.0, 5.0, 3.6), (-8.6, 4.6, 13.6), sub=1)
    _back(a, rng, 10.5, top=7.5, y=11.0)
    _rk(a, rng, (18.0, 5.0, 5.0), (0, 11.2, 6.0), sub=1)
    _floor_and_dress(a, rng, 13.4, inner_r=7.5, big=5.0)
    return a.finish()


def build_split(fk):
    rng = random.Random(1423)
    a = _asset(fk, "CaveEntranceRingSplit", "C. Split Entrance (portal with pillar)")
    xi = 9.0
    _walls(a, rng, xi=xi, h=15.5, t=6.0)
    # central pillar 4x4x12, set forward of the lintel face so both doors read
    a.cyl(2.3, 1.9, 12.8, sides=6, loc=(0, -3.4, 0), rot=(0, 0, 0.3), mat=R, jitter=0.3)
    _rk(a, rng, (4.4, 4.2, 3.0), (0.2, -3.6, 0), sub=2)          # pillar foot
    # lintel across the top
    _rk(a, rng, (25.0, 9.0, 6.0), (0, -1.4, 11.8), yaw=0.04, flat=17.0)
    _rk(a, rng, (6.0, 6.0, 4.6), (-4.6, 0.6, 15.4))
    _rk(a, rng, (6.0, 6.0, 4.4), (4.8, 1.0, 15.2))
    _back(a, rng, 9.5, top=6.5, y=11.0)   # low, far back
    _floor_and_dress(a, rng, 13.4, inner_r=7.0, big=5.0)
    return a.finish()


def build(kit):
    fk = kit.flintkit
    out = []
    out.append(kit.tag(build_hero(fk), "hero", collision="precise", budget=6000,
                       notes="Walk-through arch (14x12 opening, faces -Y) with shallow hollow "
                             "~10 deep. No VFX: optional cave-haze vapour socket omitted "
                             "(dry cave; it rendered as an opaque puff)."))

    # ---- parts ----
    rng = random.Random(1410)
    a = _asset(fk, "CaveEntranceRingCeilingRock", "W14 CaveEntranceRing ceiling rock")
    _rk(a, rng, (16.5, 12.0, 8.4), (0, 0, 0), yaw=0.08, flat=7.0)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="Big flat-topped cap boulder of the arch (16x12x7)."))

    a = _asset(fk, "CaveEntranceRingLeftWall", "W14 CaveEntranceRing left wall")
    _slab(a, rng, (5.0, 5.6, 18.0), (0.4, 0, 0), 1)
    _slab(a, rng, (3.2, 4.0, 10.0), (-1.8, 1.2, 0), 1)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="Tall angular slab pillar cluster, leans to +X (inward)."))

    a = _asset(fk, "CaveEntranceRingRightWall", "W14 CaveEntranceRing right wall")
    _slab(a, rng, (5.2, 5.8, 17.0), (-0.4, 0, 0), -1)
    _slab(a, rng, (3.0, 3.6, 8.0), (1.8, -1.4, 0), -1)
    _rk(a, rng, (2.6, 2.6, 2.4), (2.4, 2.0, 0), sub=1)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="Mirror-different slab pillar, leans to -X (inward)."))

    a = _asset(fk, "CaveEntranceRingFloorSill", "W14 CaveEntranceRing floor sill")
    for (r, x, y, sides) in [(5.2, -6.0, 1.2, 8), (4.6, 1.8, 2.0, 6), (4.4, 7.4, -1.0, 8),
                             (3.6, -1.0, -4.0, 6)]:
        _plate(a, rng, r, (x, y, 0), sides=sides, h=1.2)
    _pebbles(a, rng, [(-10.6, -4.6, 0.8), (11.0, 3.4, 0.7), (4.6, -5.6, 0.7)])
    out.append(kit.tag(a.finish(), "part", collision="precise", budget=1500,
                       notes="Walkable fan of irregular sand plates with gaps, plus pebbles."))

    a = _asset(fk, "CaveEntranceRingRubble", "W14 CaveEntranceRing rubble")
    for (s, x, y) in [((4, 3.6, 3.4), -3.2, 0), ((3, 2.8, 2.4), 1.6, 1.2),
                      ((2.4, 2.2, 2), 4.2, -1.0), ((2.2, 2.4, 1.8), 0.4, -2.6)]:
        _rk(a, rng, s, (x, y, 0), sub=1)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=800,
                       notes="Loose stones drawn in the exploded view."))

    # ---- variations ----
    out.append(kit.tag(build_rounded(fk), "variant", collision="precise", budget=5000,
                       notes="A. Rounded Entrance: 12x13 opening, semicircular crown."))
    out.append(kit.tag(build_wide(fk), "variant", collision="precise", budget=5000,
                       notes="B. Wide Entrance: 20x10 opening, pillars at outer edges, "
                             "extra boulder on top."))
    out.append(kit.tag(build_split(fk), "variant", collision="precise", budget=5000,
                       notes="C. Split Entrance: central 4x4x12 pillar, two ~7-wide doors, lintel."))
    return out
