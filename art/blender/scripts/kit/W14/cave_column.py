"""W14 row 3: CaveColumn (floor-to-ceiling rock column, parts and variations)."""
import math
import random

SUBJECT = "CaveColumn"
ROW = 3
HERO_AZIMUTH = -22
SIDE_AZIMUTH = -90   # left side: the sunlit side, like the reference side cell
# w14_rock greyed/darkened from the sheet value #8C7F7A per verifier (it rendered too pink);
# the sheet owner is asked to sync the other W14 modules (shared_lib_requests).
PALETTE = {
    "w14_rock": ("#837A77", 0.95, 0, 0),
    "w14_sand": ("#C79B6C", 1, 0, 0),
    "w14_moss": ("#5C8A2E", 0.9, 0, 0),
}
R, S, M = "w14_rock", "w14_sand", "w14_moss"
TOP = 32.0


def _pol(ang_deg, d, cx=0.0, cy=0.0):
    a = math.radians(ang_deg)
    return cx + d * math.cos(a), cy + d * math.sin(a)


def _rot(rng, t=0.25):
    return (rng.uniform(-t, t), rng.uniform(-t, t), rng.uniform(0, 6.28))


def tuft(a, x, y, z=0.0, h=1.8, n=7, rng=None):
    """Spiky fern/grass fan of thin 3-sided blades."""
    rng = rng or random.Random(1)
    for i in range(n):
        ang = i * 2 * math.pi / n + rng.uniform(-0.3, 0.3)
        tilt = rng.uniform(0.5, 0.9)
        hh = h * rng.uniform(0.75, 1.15)
        a.cyl(0.45 * h / 1.8, 0.02, hh, sides=3, loc=(x, y, z), rot=(tilt, 0, ang), mat=M)


def chip(a, x, y, r=0.8, rng=None):
    rng = rng or random.Random(2)
    a.cyl(r, r * 0.85, 0.25, sides=5, loc=(x, y, 0), rot=(0, 0, rng.uniform(0, 6.28)), mat=S)


def lump(a, size, loc, rot, clip=None, subdiv=1, jitter=0.16):
    """Angular faceted lump centred at loc, optionally clipped flat at z=clip."""
    vs = a.ico((size[0] / 2, size[1] / 2, size[2] / 2), loc, rot, mat=R, subdiv=subdiv,
               jitter=jitter, facets=20, face_tint_var=0.05)
    if clip is not None:
        for v in vs:
            if v.co.z > clip:
                v.co.z = clip
    return vs


def cap(a, cx, cy, top, radius, n=8, seed=3, h=7.0):
    """Ceiling cap: flat 7-sided core, ring of angular lumps round the rim, flared underside."""
    rng = random.Random(seed)
    hc = h * 0.72
    a.cyl(radius * 0.5, radius * 0.6, hc, sides=7, loc=(cx, cy, top - hc), rot=(0, 0, 0.2),
          mat=R, jitter=0.12)
    a.cyl(radius * 0.36, radius * 0.6, h - hc, sides=7, loc=(cx, cy, top - h), rot=(0, 0, 0.65),
          mat=R, jitter=0.15)
    br = radius * 0.7
    for i in range(n):
        ang = i * 360.0 / n + rng.uniform(-10, 10) + 12
        x, y = _pol(ang, radius * 0.7, cx, cy)
        s = br * rng.uniform(0.85, 1.1)
        hz = h * rng.uniform(0.95, 1.15)
        lump(a, (s, s * rng.uniform(0.8, 1.0), hz), (x, y, top - hz * 0.4), _rot(rng, 0.3),
             clip=top - rng.uniform(0.4, 0.9), subdiv=2, jitter=0.12)
    k = max(3, n // 2)
    for i in range(k):
        ang = i * 360.0 / k + rng.uniform(-20, 20) + 35
        x, y = _pol(ang, radius * 0.45, cx, cy)
        s = br * 0.95
        lump(a, (s, s * 0.9, s * 0.8), (x, y, top - h * 0.85), _rot(rng, 0.3), clip=top - 1.0,
             subdiv=2, jitter=0.12)


def column(a, cx=0.0, cy=0.0, w=1.0, neck=1.0, seed=7, top=TOP, loose=6, tiny=3, tufts=3,
           chips=4, cap_r=10.5):
    """Full hourglass column: massive boulder base, short faceted neck, ceiling cap."""
    rng = random.Random(seed)
    # base core and big overlapping boulders; biggest at the front (-Y)
    a.rock((15 * w, 15 * w, 14), (cx, cy, 0), (0, 0, 0.4), mat=R, rough=0.14)
    for ang, d, sz in ((-90, 6.8, (11.0, 9.5, 12.5)), (-150, 7.4, (9.5, 9.0, 10.5)),
                       (-28, 7.4, (9.5, 8.5, 10.0)), (150, 7.2, (9.5, 9.0, 11.0)),
                       (35, 7.2, (9.0, 8.5, 10.5)), (95, 7.4, (9.0, 8.0, 9.0))):
        x, y = _pol(ang, d * w, cx, cy)
        a.rock((sz[0] * w, sz[1] * w, sz[2]), (x, y, 0), _rot(rng, 0.2), mat=R, rough=0.14,
               subdiv=2)
    # loose rocks round the foot, kept proud (low sink) so they read as solid objects
    for i in range(loose):
        ang = i * 360.0 / loose + rng.uniform(-14, 14) - 75
        x, y = _pol(ang, rng.uniform(11.5, 12.8) * w, cx, cy)
        s = rng.uniform(3.2, 4.8) * min(1.0, w + 0.1)
        a.rock((s, s * 0.85, s * 0.75), (x, y, 0), _rot(rng, 0.2), mat=R, subdiv=1, sink=0.05,
               rough=0.1)
    for i in range(tiny):
        ang = -110 + i * 55 + rng.uniform(-10, 10)
        x, y = _pol(ang, rng.uniform(14.0, 15.0) * w, cx, cy)
        s = rng.uniform(1.5, 2.1)
        a.rock((s, s * 0.9, s * 0.7), (x, y, 0), _rot(rng, 0.2), mat=R, subdiv=1, sink=0.05)
    # neck: 7-sided core + stacked angular blocks, waist ~9 wide
    nr = 5.0 * neck
    a.cyl(nr * 1.1, nr, 7, sides=7, loc=(cx, cy, 12), rot=(0, 0, 0.2), mat=R, jitter=0.2)
    a.cyl(nr, nr * 1.2, 6, sides=7, loc=(cx, cy, 19), rot=(0, 0, 0.6), mat=R, jitter=0.2)
    for z, s, h, off in ((10.5, 12.5 * neck, 8.0, 0.9), (14.5, 10.5 * neck, 8.0, -1.0),
                         (18.5, 10.5 * neck, 7.0, 0.8), (21.5, 12.5 * neck, 5.0, -0.4)):
        lump(a, (s * w, s * 0.85 * w, h), (cx + off * w, cy + off * 0.6, z + h / 2),
             (rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15), rng.uniform(0, 6.28)),
             subdiv=2, jitter=0.13)
    cap(a, cx, cy, top, cap_r * w, n=8, seed=seed + 1, h=8.0)
    # dressing
    rng2 = random.Random(seed + 5)
    for ang in (-118, -62, 205)[:tufts]:
        x, y = _pol(ang, 10.5 * w, cx, cy)
        tuft(a, x, y, h=3.0, n=9, rng=rng2)
    for ang in (-100, -76, -160, 20)[:chips]:
        x, y = _pol(ang, 13.5 * w, cx, cy)
        chip(a, x, y, rng2.uniform(0.7, 1.0), rng2)


def stalactite(a, cx, cy, ztip, length=11.0, r=2.5, attach=True):
    """Hanging 6-sided spike: tip at ztip, widest bulge ~2/3 up, flat narrower top."""
    zb = ztip + length * 0.66
    a.cyl(0.05, r, length * 0.66, sides=6, loc=(cx, cy, ztip), rot=(0, 0, 0.3), mat=R, jitter=0.06)
    a.cyl(r, r * 0.7, length * 0.34, sides=6, loc=(cx, cy, zb), rot=(0, 0, 0.3), mat=R, jitter=0.08)
    if attach:
        a.cyl(r * 0.7, r * 0.75, 0.4, sides=6, loc=(cx, cy, ztip + length - 0.4), rot=(0, 0, 0.3),
              mat=R)


def stalagmite(a, cx, cy, h=10.0, r=2.4, base=6.0, rng=None):
    rng = rng or random.Random(9)
    a.rock((base * 0.7, base * 0.65, 2.6), (cx, cy, 0), (0, 0, 0.5), mat=R)
    for ang in (30, 160, 260):
        x, y = _pol(ang, base * 0.38, cx, cy)
        a.rock((2.0, 1.8, 1.6), (x, y, 0), (0, 0, ang), mat=R, subdiv=1, sink=0.05)
    a.cyl(r, r * 0.55, h * 0.45, sides=6, loc=(cx, cy, 1.0), rot=(0, 0, 0.2), mat=R, jitter=0.1)
    a.cyl(r * 0.55, 0.05, h * 0.55 - 1.0, sides=6, loc=(cx, cy, 1.0 + h * 0.45), mat=R, jitter=0.05)


def build(kit):
    fk = kit.flintkit
    out = []

    # HERO
    a = fk.Asset("CaveColumn", "W14 CaveColumn", tint_var=0.05)
    column(a)
    out.append(kit.tag(a.finish(), "hero", collision="hull", budget=5000,
                       notes="Floor-to-ceiling hourglass rock column; flat top meets the cave ceiling."))

    # PARTS
    a = fk.Asset("CaveColumnUpperSection", "W14 CaveColumn upper section", tint_var=0.05)
    a.cyl(4.0, 4.6, 2.5, sides=7, loc=(0, 0, 0), mat=R, jitter=0.15)
    cap(a, 0, 0, 9.0, 7.2, n=7, seed=11, h=6.5)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="Ceiling cap block of the column; flat top."))

    a = fk.Asset("CaveColumnMiddleSection", "W14 CaveColumn middle section", tint_var=0.05)
    a.cyl(3.2, 3.0, 9.6, sides=7, loc=(0, 0, 0), rot=(0, 0, 0.2), mat=R, jitter=0.2)
    rng = random.Random(13)
    for zc, sz, off in ((2.2, (9.6, 8.6, 5.0), (0.5, -0.3)), (5.0, (8.6, 9.2, 5.0), (-0.6, 0.4)),
                        (7.6, (9.2, 8.4, 4.4), (0.3, 0.5))):
        lump(a, sz, (off[0], off[1], zc), (rng.uniform(-.15, .15), rng.uniform(-.15, .15),
             rng.uniform(0, 6.28)), clip=10.0, subdiv=2, jitter=0.12)

    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1200,
                       notes="Neck block: stacked faceted rock chunks."))

    a = fk.Asset("CaveColumnBaseSection", "W14 CaveColumn base section", tint_var=0.05)
    a.cyl(6.6, 5.6, 9, sides=7, loc=(0, 0, 0), rot=(0, 0, 0.2), mat=R, jitter=0.2)
    rng = random.Random(12)
    for i in range(7):
        x, y = _pol(i * 360 / 7 - 90, 6.6)
        s = rng.uniform(4.8, 6.0)
        a.rock((s, s * 0.9, rng.uniform(3.6, 5.6)), (x, y, 0), _rot(rng, 0.15), mat=R, subdiv=1,
               sink=0.05)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="Wide base block ringed by boulders; flat top takes the neck."))

    a = fk.Asset("CaveColumnStalactite", "W14 CaveColumn stalactite", tint_var=0.05)
    stalactite(a, 0, 0, 0.0, 11.0, 2.5)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=600,
                       notes="Hanging spike; tip at z=0, flat top attaches to the ceiling."))

    a = fk.Asset("CaveColumnStalagmite", "W14 CaveColumn stalagmite", tint_var=0.05)
    stalagmite(a, 0, 0)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=600,
                       notes="Floor spike on a small rock base."))

    # VARIATIONS
    a = fk.Asset("CaveColumnFull", "A. Full Column (floor to ceiling)", tint_var=0.05)
    column(a, neck=0.88, seed=21, w=0.95, loose=5, tiny=2, tufts=2, chips=2)
    out.append(kit.tag(a.finish(), "variant", collision="hull", budget=5000,
                       notes="Slimmer-necked full column."))

    a = fk.Asset("CaveColumnBroken", "B. Broken Column (ruined)", tint_var=0.05)
    rng = random.Random(31)
    a.rock((13, 12, 6.5), (0, 0, 0), (0, 0, 0.3), mat=R)
    ring = ((6.8, (7.5, 6.5, 5.5)), (7.0, (6.5, 6.0, 4.5)), (7.2, (6.0, 5.5, 4.0)),
            (7.0, (6.5, 6.0, 5.0)), (7.0, (6.0, 5.5, 4.2)), (7.2, (5.5, 5.0, 3.8)),
            (7.0, (6.0, 5.5, 4.4)), (7.2, (5.5, 5.0, 3.6)))
    for i, (d, sz) in enumerate(ring):
        x, y = _pol(-90 + i * 45 + rng.uniform(-8, 8), d)
        a.rock(sz, (x, y, 0), _rot(rng, 0.2), mat=R, subdiv=1, sink=0.08)
    for i in range(4):
        x, y = _pol(-120 + i * 70 + rng.uniform(-10, 10), rng.uniform(10.0, 11.0))
        s = rng.uniform(1.8, 2.8)
        a.rock((s, s * 0.9, s * 0.7), (x, y, 0), _rot(rng, 0.2), mat=R, subdiv=1, sink=0.05)
    # stump: 3 stacked angular blocks with a slanted jagged break on top (~12 high)
    lump(a, (8.5, 8.0, 4.5), (0.2, 0, 6.6), (0, 0, 0.4), jitter=0.1)
    lump(a, (7.0, 6.6, 4.0), (-0.3, 0.2, 8.6), (0, 0, 1.3), jitter=0.1)
    lump(a, (3.2, 3.0, 4.0), (1.6, -0.8, 10.0), (0.3, 0.2, 0.7), jitter=0.2)
    vs = lump(a, (5.2, 4.8, 5.0), (-0.4, 0.3, 10.0), (0.1, 0, 2.2), jitter=0.18)
    for v in vs:
        cut = 11.0 + 0.32 * v.co.x + rng.uniform(-0.35, 0.35)
        if v.co.z > cut:
            v.co.z = cut
    tuft(a, *_pol(-120, 9.5), h=1.4, rng=rng)
    tuft(a, *_pol(-55, 9.5), h=1.2, rng=rng)
    chip(a, *_pol(-80, 11.5), r=0.8, rng=rng)
    out.append(kit.tag(a.finish(), "variant", collision="hull", budget=3000,
                       notes="Ruined column: rubble heap and jagged broken stump."))

    a = fk.Asset("CaveColumnPaired", "C. Paired Formation (column + stalactite)", tint_var=0.05)
    column(a, cx=-7.5, w=0.72, neck=1.2, seed=41, loose=4, tiny=1, tufts=2, chips=2, cap_r=11.0)
    cap(a, 9.5, 0, TOP, 6.5, n=6, seed=43, h=4.0)
    stalactite(a, 9.5, 0, 15.0, 14.0, 3.0, attach=False)
    stalagmite(a, 10.0, 0, h=9.0, r=2.2, base=6.0)
    rng = random.Random(44)
    tuft(a, 7.0, -3.0, h=1.4, rng=rng)
    out.append(kit.tag(a.finish(), "variant", collision="hull", budget=5000,
                       notes="Column plus a hanging stalactite under its own cap and a floor stalagmite."))
    return out
