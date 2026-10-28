"""W14 row 2: TunnelModule - modular straight cave tunnel (32x32 grid) + parts + variants."""
import math
import random

SUBJECT = "TunnelModule"
ROW = 2
HERO_AZIMUTH = -22
HERO_ELEVATION = 28      # ref hero/variants are drawn from higher; makes L / plus readable
SIDE_AZIMUTH = -135      # rear three-quarter from the left: lit slab wall + back opening

PALETTE = {
    "w14_rock": ("#8C7F7A", 0.95, 0, 0),
    "w14_sand": ("#C79B6C", 1, 0, 0),
    "w14_moss": ("#5C8A2E", 0.9, 0, 0),
}

R, S, M = "w14_rock", "w14_sand", "w14_moss"
ROOF_Z = 11.0      # flat underside of the roof = passage height
HALF = 16.0        # half footprint


# ---------------------------------------------------------------- pieces
def tslab(a, rng, x, y, thick, long, h, rz=0.0, sides=5):
    """Tall tapered angular slab: faceted prism, narrower slanted top."""
    bev = min(thick, long) * 0.16
    v = a.box((thick, long, h), (0, 0, 0), (0, 0, 0), R, bevel=bev, jitter=0.25, base=True)
    tx, ty = rng.uniform(0.62, 0.8), rng.uniform(0.7, 0.88)
    slope = rng.uniform(-0.22, 0.22)
    for p in v:
        f = p.co.z / h                              # taper towards the top
        k = 1.0 - (1.0 - tx) * f, 1.0 - (1.0 - ty) * f
        p.co.x *= k[0]
        p.co.y *= k[1]
        if f > 0.8:                                 # slanted, chipped top
            p.co.z += p.co.y * slope + rng.uniform(-0.6, 0.2)
    a.transform(v, (x, y, 0), (0, 0, rz + rng.uniform(-0.15, 0.15)))
    return v


def wall_row(a, rng, x, y0=-14.5, y1=14.5, count=5, hmin=11.5, hmax=13.5, thick=6.5,
             inner=True, axis="y"):
    """Outer row of tall slabs plus a staggered row of slimmer inner slabs (deep gaps).
    axis='y': row runs along Y at X=x (inner side towards X=0). axis='x': along X at Y=x."""
    side = 1 if x >= 0 else -1
    step = (y1 - y0) / count

    def put(c, t, l, h, off):
        if axis == "y":
            tslab(a, rng, x - side * off, c, t, l, h)
        else:
            tslab(a, rng, c, x - side * off, l, t, h)

    for i in range(count):
        c = y0 + step * (i + 0.5) + rng.uniform(-0.4, 0.4)
        put(c, thick * rng.uniform(0.92, 1.08), step * rng.uniform(0.9, 1.02),
            rng.uniform(hmin, hmax), 0.0)
    if inner:
        for i in range(count - 1):
            c = y0 + step * (i + 1.0) + rng.uniform(-0.3, 0.3)
            put(c, 3.0, step * 0.6, rng.uniform(hmin - 2.5, hmin - 1.0), thick / 2 - 0.4)


def roof_band(a, rng, cells, z=ROOF_Z, thick=(6.0, 7.5), lumpy=True, top_lumps=0,
              span=(-16, 16)):
    """Boulders over a list of cells (cx, cy, sx, sy); flat underside at z."""
    for (cx, cy, sx, sy) in cells:
        sz = rng.uniform(*thick)
        if lumpy:
            a.rock((sx, sy, sz), (cx + rng.uniform(-0.3, 0.3), cy, z),
                   (0, 0, rng.uniform(-0.12, 0.12)), R, subdiv=2, rough=0.13,
                   facets=6, sink=0.12)
        else:                                       # flat, even, rectilinear roof blocks
            a.box((sx - 1.5, sy - 1.5, sz), (cx, cy, z), (0, 0, rng.uniform(-0.05, 0.05)), R,
                  bevel=0.9, jitter=0.45, base=True)
    for _ in range(top_lumps):
        cx, cy, sx, sy = rng.choice(cells)
        a.rock((sx * 0.6, sy * 0.6, 3.5), (cx + rng.uniform(-2, 2), cy + rng.uniform(-1.5, 1.5),
                                           z + thick[0] - 1.8),
               (0, 0, rng.uniform(0, 3)), R, subdiv=1, rough=0.14, facets=8, sink=0.3)


def straight_roof(rows=4, length=30.6):
    step = length / rows
    cells = []
    for i in range(rows):
        cy = -length / 2 + step * (i + 0.5)
        sy = step + 0.6 if 0 < i < rows - 1 else step
        cells += [(0.0, cy, 14.5, sy + 1.2), (-10.2, cy, 11.6, sy + 0.8), (10.2, cy, 11.6, sy + 0.8)]
    return cells


def sand_floor(a, rng, x0=-8.0, x1=8.0, y0=-16.0, y1=16.0, rows=5, cols=2, rim=True,
               along="y", rim_sides=(-1, 1)):
    """Irregular sand plates (random seams) + low rock rim stones along the long edges."""
    if along == "x":                       # swap: plates laid along X
        x0, y0, x1, y1 = y0, x0, y1, x1
    width = x1 - x0
    length = y1 - y0
    lens = [rng.uniform(0.7, 1.3) for _ in range(rows)]
    tot = sum(lens)
    yy = y0

    def place(size, cx, cy, **kw):
        if along == "x":
            a.box((size[1], size[0], size[2]), (cy, cx, 0), **kw)
        else:
            a.box(size, (cx, cy, 0), **kw)

    for L in lens:
        rl = L / tot * length
        cut = (x0 + x1) / 2 + rng.uniform(-width * 0.2, width * 0.2)
        spans = [(x0, cut), (cut, x1)] if cols == 2 else [(x0, x1)]
        for (a0, a1) in spans:
            place((a1 - a0 - 0.45, rl - 0.45, rng.uniform(0.5, 0.75)), (a0 + a1) / 2, yy + rl / 2,
                  rot=(0, 0, rng.uniform(-0.04, 0.04)), mat=S, bevel=0.12, jitter=0.06,
                  base=True)
        yy += rl
    if rim:
        n = int(length / 3.2)
        for sd in rim_sides:
            xe = x1 + 0.3 if sd > 0 else x0 - 0.3
            for i in range(n):
                y = y0 + length / n * (i + 0.5) + rng.uniform(-0.3, 0.3)
                p = (y, xe, 0) if along == "x" else (xe, y, 0)
                ln = length / n * rng.uniform(0.7, 0.92)
                sz = (ln, 1.7, rng.uniform(1.0, 1.4)) if along == "x" else (1.7, ln, rng.uniform(1.0, 1.4))
                a.rock(sz, p, (0, 0, rng.uniform(-0.25, 0.25)), R, subdiv=1, rough=0.1,
                       facets=12, sink=0.2)


def rubble(a, rng, pts):
    for (x, y, s) in pts:
        a.rock((s * rng.uniform(0.9, 1.2), s * rng.uniform(0.9, 1.2), s * 0.75),
               (x, y, 0), (0, 0, rng.uniform(0, 3)), R, subdiv=1, rough=0.12,
               facets=12, sink=0.2)


def tufts(a, rng, pts):
    for (x, y) in pts:
        a.leaf_cluster(rng.uniform(1.1, 1.4), (x, y, 0), M, lobes=5, squash=1.1,
                       facets=1, floor=0.0)


def pillar(a, rng, x, y, h=12.0, n=3, r=1.9):
    """Cluster of stacked tapered slabs round a corner point."""
    for k in range(n):
        ang = 2 * math.pi * k / n + rng.uniform(-0.4, 0.4)
        tslab(a, rng, x + r * math.cos(ang), y + r * math.sin(ang),
              rng.uniform(4.6, 5.6), rng.uniform(4.6, 5.6), h * rng.uniform(0.9, 1.04),
              rz=ang, sides=5)


# ---------------------------------------------------------------- assets
def build(kit):
    fk = kit.flintkit
    out = []

    # ---- hero
    rng = random.Random(1402)
    a = fk.Asset("TunnelModule", "W14 TunnelModule", seed=1402, tint_var=0.04)
    wall_row(a, rng, -12.3, count=5, hmin=11.6, hmax=13.6)
    wall_row(a, rng, 12.3, count=5, hmin=11.4, hmax=13.2)
    roof_band(a, rng, straight_roof(), thick=(6.0, 7.6), top_lumps=6)
    sand_floor(a, rng)
    rubble(a, rng, [(-13.4, -14.2, 3.4), (13.6, -14.0, 3.0), (-5.6, -12.5, 0.9),
                    (5.0, -9.0, 0.8), (-3.5, 6.0, 0.7), (11.0, -14.8, 1.3)])
    tufts(a, rng, [(-10.4, -14.6), (-15.3, -10.5), (9.8, -14.8), (15.3, -6.0),
                   (-15.4, 3.0), (15.4, 9.0)])
    o = a.finish()
    out.append(kit.tag(o, "hero", collision="precise", budget=7000,
                       notes="Straight 32x32 tunnel segment, axis Y, open -Y/+Y, passage 16x11, tiles end to end."))

    # ---- parts
    rng = random.Random(2402)
    a = fk.Asset("TunnelModuleCeiling", "W14 TunnelModule part", seed=2402, tint_var=0.04)
    roof_band(a, rng, straight_roof(length=30.0), z=0.0, thick=(6.0, 7.6), top_lumps=5)
    out.append(kit.tag(a.finish(), "part", collision="precise", budget=1500,
                       notes="Ceiling boulder run, flat underside."))

    rng = random.Random(2403)
    a = fk.Asset("TunnelModuleLeftWall", "W14 TunnelModule part", seed=2403, tint_var=0.04)
    wall_row(a, rng, -3.5, y0=-15, y1=15, count=5, hmin=12.0, hmax=14.2, thick=6.8)
    rubble(a, rng, [(-2.0, -16.0, 1.6), (0.5, 15.5, 1.2)])
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="Left wall: row of 5 tapered angular slabs + inner slabs."))

    rng = random.Random(2404)
    a = fk.Asset("TunnelModuleRightWall", "W14 TunnelModule part", seed=2404, tint_var=0.04)
    wall_row(a, rng, 3.5, y0=-15, y1=15, count=4, hmin=11.0, hmax=13.2, thick=7.2)
    rubble(a, rng, [(2.0, 16.0, 1.4)])
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="Right wall: 4 broader tapered slabs, different arrangement."))

    rng = random.Random(2405)
    a = fk.Asset("TunnelModuleFloor", "W14 TunnelModule part", seed=2405, tint_var=0.04)
    sand_floor(a, rng, rows=4)
    out.append(kit.tag(a.finish(), "part", collision="precise", budget=1500,
                       notes="Sand plate floor with rock rim stones; walkable."))

    rng = random.Random(2406)
    a = fk.Asset("TunnelModuleRubble", "W14 TunnelModule part", seed=2406, tint_var=0.04)
    rubble(a, rng, [(0, 0, 3.0), (4.0, 1.0, 2.2), (-3.2, 1.6, 1.2), (1.4, -2.8, 1.0),
                    (-1.8, -2.4, 0.8), (2.6, 3.2, 0.9), (-4.4, -0.6, 0.7), (5.6, -1.8, 0.8),
                    (0.2, 3.6, 0.6), (-2.6, 4.0, 0.7)])
    out.append(kit.tag(a.finish(), "part", collision="none", budget=600,
                       notes="Loose pebble/rock set: 2 small boulders + 8 pebbles."))

    # ---- A. straight: rectilinear, lower, flat even roof
    rng = random.Random(3401)
    a = fk.Asset("TunnelModuleStraight", "W14 TunnelModule variant", seed=3401, tint_var=0.04)
    zr = 9.5
    wall_row(a, rng, -12.3, y0=-15.5, y1=15.5, count=5, hmin=10.0, hmax=10.4)
    wall_row(a, rng, 12.3, y0=-15.5, y1=15.5, count=5, hmin=10.0, hmax=10.4)
    roof_band(a, rng, straight_roof(rows=5), z=zr, thick=(4.0, 4.5), lumpy=False)
    sand_floor(a, rng)
    tufts(a, rng, [(-15.4, -12.0), (15.4, 4.0)])
    out.append(kit.tag(a.finish(), "variant", collision="precise", budget=6000,
                       notes="A. Straight Tunnel: same cross-section, lower, flat even roof."))

    # ---- B. bend (enter -Y, exit +X): rectilinear L
    rng = random.Random(3402)
    a = fk.Asset("TunnelModuleBend", "W14 TunnelModule variant", seed=3402, tint_var=0.04)
    wall_row(a, rng, -12.3, y0=-15.5, y1=8.0, count=4, hmin=11.0, hmax=12.4)   # -X outer wall
    wall_row(a, rng, 12.3, y0=-8.0, y1=15.5, count=4, hmin=11.0, hmax=12.4, axis="x")  # +Y outer wall
    tslab(a, rng, -12.0, 12.0, 7.5, 7.5, 12.2, rz=0.78, sides=6)              # rounded outer corner
    pillar(a, rng, 12.4, -12.4, h=11.6, n=3, r=1.6)                            # inner corner pillar
    cells = []
    for cx in (-12, -4, 4, 12):
        for cy in (-12, -4, 4, 12):
            if cx > 8 and cy < -8:
                continue                                                         # notch over pillar
            arm_x = cy > -8 and cx > 0                                           # exit arm: long along X
            sx, sy = (9.0, 8.4) if arm_x else (8.4, 9.0)
            sx = min(sx, 2 * (16 - abs(cx)))
            sy = min(sy, 2 * (16 - abs(cy)))
            cells.append((cx, cy, sx, sy))
    roof_band(a, rng, cells, z=ROOF_Z, thick=(6.0, 6.6), lumpy=False)
    sand_floor(a, rng, -8, 8, -16, 8, rows=3, rim_sides=(-1,))                  # entry arm
    sand_floor(a, rng, 8, 16, -8, 8, rows=1, cols=2, rim=False, along="x")      # exit arm
    tufts(a, rng, [(-15.4, -13.5), (13.5, 15.3), (15.0, -15.0)])
    out.append(kit.tag(a.finish(), "variant", collision="precise", budget=6000,
                       notes="B. Bend Module (90 deg): enters -Y, exits +X; L of slab walls, inner corner pillar, flat roof."))

    # ---- C. 4-way junction: plus roof, corner pillar clusters
    rng = random.Random(3403)
    a = fk.Asset("TunnelModuleJunction", "W14 TunnelModule variant", seed=3403, tint_var=0.04)
    for sx in (-1, 1):
        for sy in (-1, 1):
            pillar(a, rng, sx * 12.2, sy * 12.2, h=11.4, n=4, r=1.7)
    cells = []
    for cx in (-12, -4, 4, 12):
        for cy in (-12, -4, 4, 12):
            if abs(cx) > 8 and abs(cy) > 8:
                continue
            cells.append((cx, cy, min(8.8, 2 * (16 - abs(cx))), min(8.8, 2 * (16 - abs(cy)))))
    roof_band(a, rng, cells, z=ROOF_Z, thick=(6.2, 6.8), lumpy=False)
    sand_floor(a, rng, -8, 8, -16, 16, rows=4, rim=False)
    sand_floor(a, rng, -16, -8, -8, 8, rows=1, rim=False, along="x")
    sand_floor(a, rng, 8, 16, -8, 8, rows=1, rim=False, along="x")
    tufts(a, rng, [(-15.3, -8.8), (8.8, -15.3), (15.3, 9.0)])
    out.append(kit.tag(a.finish(), "variant", collision="precise", budget=6000,
                       notes="C. Junction (4-way): openings -Y,+Y,-X,+X, corner slab pillar clusters, plus-shaped flat roof."))
    return out
