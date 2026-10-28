"""R05 row 1: BerryShrub - waist-high berry bush, harvestable."""
import math

SUBJECT = "BerryShrub"
ROW = 1
HERO_AZIMUTH = -22
PALETTE = {
    "r05_shrub_leaf": ("#5A9E22", 0.85, 0, 0),  # BerryShrub leaves (yellow-green faceted clumps)
    "r05_bark": ("#7A5030", 0.9, 0, 0),  # trunks, forks, branches, stems and stumps
    "r05_berry": ("#D81E1E", 0.5, 0, 0),  # berries (glossy saturated red)
}

LEAF, BARK, BERRY = "r05_shrub_leaf", "r05_bark", "r05_berry"


def _clump(a, r, loc, squash=0.92, jit=0.03, rot=(0, 0, 0)):
    """One chunky icosahedron clump: 20 big flat facets."""
    a.ico((r, r * 0.95, r * squash), loc=loc, rot=rot, mat=LEAF, subdiv=1, jitter=jit)


def _berry(a, loc, r=0.55):
    a.ico(r, loc=loc, mat=BERRY, subdiv=2, jitter=0.02)


def _trunks(a, h=2.5, spread=0.62, r1=0.42, r2=0.27, azs=(-100, -10, 85, 170)):
    """3-4 thick tapering trunks fanning out from a small base (one points to the front)."""
    a.cyl(0.62, 0.5, 0.35, sides=7, mat=BARK, jitter=0.02)
    for i, az in enumerate(azs):
        ang = math.radians(az)
        dx, dy = math.cos(ang), math.sin(ang)
        sp = spread * (1.0 + 0.12 * ((i % 2) * 2 - 1))
        a.cyl(r1, r2, h, sides=6, loc=(dx * 0.32, dy * 0.32, 0.0),
              rot=(-dy * sp, dx * sp, 0), mat=BARK, jitter=0.02)


def _exit(clumps, c, d):
    """Farthest point where the ray c + t*d leaves the union of clump spheres."""
    n = math.sqrt(sum(v * v for v in d))
    d = [v / n for v in d]
    best = 0.0
    for r, cc in clumps:
        oc = [c[i] - cc[i] for i in range(3)]
        b = sum(oc[i] * d[i] for i in range(3))
        q = sum(v * v for v in oc) - (r * 0.86) ** 2
        disc = b * b - q
        if disc >= 0:
            best = max(best, -b + math.sqrt(disc))
    return tuple(c[i] + d[i] * best for i in range(3)), d


def _place_berries(a, clumps, centre, dirs, sink=-0.08):
    for d in dirs:
        p, u = _exit(clumps, centre, d)
        _berry(a, tuple(p[i] - u[i] * sink for i in range(3)))


def _LEAF_CHIPS(burst, size, speed, spread):
    """Leaf-coloured chip burst (no grey dust) for harvest sockets."""
    return {"name": "Leaves", "texture": "rock_chip", "color": ["#7BC23A", "#5A9E22"],
            "size": [size, size * 0.55], "transparency": [0, 0, 1], "lifetime": [0.5, 1.0],
            "rate": 0, "burst": burst, "speed": list(speed), "spread": spread,
            "light_emission": 0.0, "acceleration": [0, -35, 0], "rotation": [0, 360],
            "rot_speed": [-360, 360]}


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---- HERO ----
    a = fk.Asset("BerryShrub", "R05 Berry Shrub")
    _trunks(a)
    # rosette: big centre clump, ring of 6 upper clumps, 4 smaller low clumps tucked at the sides
    clumps = [(1.9, (0.0, -0.15, 3.7))]
    for k, az in enumerate((-90, -30, 30, 90, 150, 210)):
        rr = 1.75 if az == -90 else 1.55
        ang = math.radians(az)
        clumps.append((rr, (math.cos(ang) * 2.15 * 0.95, math.sin(ang) * 2.15 * 0.8,
                            3.1 + 0.15 * (k % 2))))
    for az in (-140, -40, 0, 180):
        ang = math.radians(az)
        clumps.append((1.3, (math.cos(ang) * 2.6, math.sin(ang) * 2.6 * 0.72, 2.5)))
    for k, (r, loc) in enumerate(clumps):
        _clump(a, r, loc, rot=(0.3 * k, 0.5 * k, 0.7 * k))
    # 7 berries nestled into the gaps between clumps: 2 front, both sides, top, upper right, back
    _place_berries(a, clumps, (0, 0, 2.9), [
        (-0.5, -1.0, 0.3), (0.1, -1.0, -0.15), (0.55, -0.9, 0.6),   # front: left, low centre, upper right
        (-1.0, -0.05, 0.55), (1.0, -0.3, 0.35),                   # left and right sides
        (-0.4, 0.35, 1.0), (0.6, 0.5, 0.9)])                      # top, upper right-back                      # back-left
    o = a.finish()
    vfx.add(o, "harvest_hit", (0, -2.5, 2.5), emitters=[_LEAF_CHIPS(8, 0.4, (7, 12), 55)])
    vfx.add(o, "harvest_deplete", (0, 0, 0.3), scale=1.0,
            emitters=[dict(_LEAF_CHIPS(18, 0.55, (8, 14), 80), shape=[3.0, 1.0, 3.0])])
    out.append(kit.tag(o, "hero", collision="hull", budget=3000,
                       notes="Harvestable berry bush. harvest_hit: leaf burst on the front face when picked; "
                             "harvest_deplete: burst at the base when the berries run out (swap to BerryShrubDepleted)."))

    # ---- PARTS ----
    a = fk.Asset("BerryShrubLeafClump", "R05 Leaf Clump")
    a.ico((0.95, 0.85, 1.05), loc=(-1.0, -0.1, 0.85), rot=(0.2, -0.45, 0.3), mat=LEAF, subdiv=1, jitter=0.03)
    a.ico((1.1, 0.95, 1.25), loc=(0.05, 0.2, 1.05), rot=(0.1, 0.25, 0.9), mat=LEAF, subdiv=1, jitter=0.03)
    a.ico((0.9, 0.8, 1.0), loc=(1.0, -0.2, 0.8), rot=(-0.25, 0.45, 1.6), mat=LEAF, subdiv=1, jitter=0.03)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="Leaf Clump: three overlapping faceted lobes."))

    a = fk.Asset("BerryShrubBerry", "R05 Berry")
    _berry(a, (0, 0, 0.53))
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes="Berry: single faceted berry."))

    a = fk.Asset("BerryShrubTrunkFork", "R05 Trunk Fork")
    a.cyl(0.55, 0.38, 1.6, sides=7, mat=BARK, jitter=0.03)
    a.cyl(0.36, 0.22, 1.8, sides=6, loc=(0.05, 0, 1.35), rot=(0, 0.7, 0), mat=BARK, jitter=0.03)
    a.cyl(0.34, 0.2, 1.6, sides=6, loc=(-0.05, 0, 1.35), rot=(0.15, -0.6, 0), mat=BARK, jitter=0.03)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Trunk Fork: Y-shaped brown stem."))

    # ---- DROP ----
    a = fk.Asset("BerryShrubBerries", "R05 Berries (x2)")
    _berry(a, (-0.6, 0, 0.53))
    _berry(a, (0.6, 0.05, 0.53))
    out.append(kit.tag(a.finish(), "drop", collision="none", budget=300,
                       notes="Berries (x2): pickup dropped when harvesting."))

    # ---- DEPLETED ----
    a = fk.Asset("BerryShrubDepleted", "R05 Depleted (No Fruit)")
    _trunks(a, h=2.6, spread=0.62)
    for k, (r, loc) in enumerate([(1.25, (0.1, 0.25, 3.05)), (1.1, (-1.75, -0.2, 2.35)),
                                  (1.1, (1.8, 0.0, 2.45)), (0.95, (-0.6, 1.25, 2.6)),
                                  (1.0, (0.75, -1.05, 2.5))]):
        _clump(a, r, loc, squash=0.82, rot=(0.4 * k, 0.6 * k, 0.9 * k))
    out.append(kit.tag(a.finish(), "depleted", collision="hull", budget=2000,
                       notes="Depleted (No Fruit): sparse leaves, no berries; regrows into BerryShrub."))
    return out
