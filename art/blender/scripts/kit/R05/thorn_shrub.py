"""R05 row 4: ThornShrub - gnarled olive bush with a twisting trunk and big cream thorns."""
from mathutils import Vector

SUBJECT = "ThornShrub"
ROW = 4
HERO_AZIMUTH = -22

PALETTE = {
    "r05_bark": ("#7A5030", 0.9, 0, 0),  # trunks, forks, branches, stems and stumps for BerryShrub, FiberShrub, ThornShrub
    "r05_thorn_leaf": ("#6F7F28", 0.85, 0, 0),  # ThornShrub leaves (olive green)
    "r05_thorn": ("#DDBE96", 0.7, 0, 0),  # ThornShrub thorns (pale bone cream)
}

BARK, LEAF, THORN = "r05_bark", "r05_thorn_leaf", "r05_thorn"


def _rot_to(d):
    """Euler that turns +Z onto direction d."""
    return Vector((0, 0, 1)).rotation_difference(Vector(d).normalized()).to_euler()


def _thorn(a, base, d, length=2.7, r=0.75, sides=6, jitter=0.06):
    a.cyl(r, 0.0, length, sides=sides, loc=base, rot=_rot_to(d), mat=THORN, jitter=jitter)


def _limb(a, pts, r0, r1, sides=6, knuckles=True):
    """Angular zig-zag limb: straight tapered faceted segments r0 -> r1, knuckled joints."""
    n = len(pts) - 1
    for i in range(n):
        ra = r0 + (r1 - r0) * i / n
        rb = r0 + (r1 - r0) * (i + 1) / n
        p, q = Vector(pts[i]), Vector(pts[i + 1])
        d = q - p
        a.cyl(ra, rb, d.length, sides=sides, loc=p, rot=_rot_to(d), mat=BARK, jitter=0.04)
        if knuckles and i > 0:
            a.ico(ra * 1.05, loc=pts[i], mat=BARK, subdiv=1, jitter=0.05)


def _trunk(a):
    # heavy trunk rising from the front-centre base
    a.cyl(1.15, 0.95, 0.8, sides=7, loc=(0.0, -1.9, 0.0), mat=BARK, jitter=0.04)
    fork = (-0.1, -2.4, 2.5)
    _limb(a, [(0.0, -1.9, 0.6), (0.35, -2.2, 1.5), fork], 0.95, 0.8, sides=7)
    a.ico(0.85, loc=fork, mat=BARK, subdiv=1, jitter=0.05)
    # left limb: up and out, looping across the front to the upper left
    _limb(a, [fork, (-0.9, -2.75, 2.9), (-1.4, -2.9, 3.7), (-2.2, -2.7, 4.2), (-2.9, -2.0, 4.7)], 0.7, 0.36)
    # right limb: out to the right then up
    _limb(a, [fork, (0.9, -2.8, 2.4), (1.7, -2.9, 3.0), (2.2, -2.9, 3.8), (2.9, -2.0, 4.2)], 0.68, 0.35)
    # middle limb looping up the centre front
    _limb(a, [fork, (0.5, -2.9, 3.3), (-0.2, -2.9, 4.0), (0.3, -2.6, 4.9)], 0.55, 0.3)
    # low side limb from the trunk out to the lower right
    _limb(a, [(0.3, -1.9, 1.2), (1.2, -2.6, 1.0), (2.0, -2.5, 1.5)], 0.5, 0.32)


CLUMPS = [  # (loc, radius) - packed body ~7.5 x 7 x 6
    ((0.0, 0.2, 4.4), (1.85, 1.8, 1.6)),                      # big top-centre
    ((-2.3, -0.4, 3.0), 1.5), ((2.3, -0.4, 3.0), 1.5),
    ((-1.6, 1.7, 3.2), 1.5), ((1.6, 1.7, 3.2), 1.5), ((0.0, 2.2, 2.4), 1.4),
    ((-2.4, -1.4, 1.3), 1.3), ((2.4, -1.4, 1.3), 1.3),
    ((-2.4, 1.1, 1.3), 1.4), ((2.4, 1.1, 1.3), 1.4), ((0.0, 2.0, 1.2), 1.4),
    ((-1.2, -1.7, 3.9), 1.1), ((1.3, -1.7, 3.8), 1.1),
    ((-1.8, -1.6, 0.9), 1.0), ((1.9, -1.5, 0.8), 1.0),
]
POINTED = [  # small pointed lumps sticking up around the top
    ((-1.2, 0.3, 5.3), (0.7, 0.7, 1.1)), ((1.2, -0.1, 5.3), (0.7, 0.7, 1.1)),
    ((-0.2, 1.4, 5.4), (0.65, 0.65, 1.05)), ((2.2, 0.6, 4.4), (0.65, 0.65, 1.0)),
    ((-2.2, 0.6, 4.4), (0.65, 0.65, 1.0)),
]

THORNS = [  # (base, direction, length)
    ((-2.6, -0.9, 4.0), (-0.6, -0.3, 0.75), 2.8),    # upper left
    ((2.6, -0.8, 4.1), (0.6, -0.3, 0.75), 2.8),      # upper right
    ((-2.6, -2.0, 2.4), (-0.75, -0.6, 0.2), 2.6),    # front left
    ((2.5, -2.3, 1.4), (0.65, -0.6, -0.45), 2.6),    # lower front right, down-out
    ((-3.0, 0.5, 2.2), (-0.95, 0.1, 0.3), 2.5),      # left
    ((1.2, 1.4, 4.9), (0.35, 0.4, 0.85), 2.4),       # back right, up
]


def _hero(kit):
    fk, vfx = kit.flintkit, kit.vfx
    a = fk.Asset("ThornShrub", "R05 ThornShrub")
    for loc, r in CLUMPS:
        a.ico(tuple(v * 1.08 for v in r) if isinstance(r, tuple) else r * 1.08, loc=loc, mat=LEAF, subdiv=1, jitter=0.12)
    for loc, r in POINTED:
        a.ico(r, loc=loc, mat=LEAF, subdiv=1, jitter=0.1)
    _trunk(a)
    for base, d, ln in THORNS:
        _thorn(a, base, d, ln)
    o = a.finish()
    vfx.add(o, "harvest_hit", (0, -3, 2.5), scale=0.6, color=["#6F7F28", "#DDBE96"])
    vfx.add(o, "harvest_deplete", (0, 0, 0.5), color=["#6F7F28", "#7A5030"])
    return kit.tag(o, "hero", collision="hull", budget=4000,
                   notes="harvest_hit on the front face (olive leaf + thorn chips); "
                         "harvest_deplete at the base when stripped to ThornShrubDepleted")


def _leaf_cluster(kit):
    a = kit.flintkit.Asset("ThornShrubLeafCluster", "R05 ThornShrub Leaf Cluster")
    a.ico((1.05, 1.0, 0.8), loc=(-0.75, -0.1, 0.8), mat=LEAF, subdiv=1, jitter=0.1)
    a.ico((0.95, 0.9, 1.1), loc=(0.75, 0.1, 1.1), mat=LEAF, subdiv=1, jitter=0.1)
    a.ico((0.75, 0.75, 0.65), loc=(0.05, -0.7, 0.65), mat=LEAF, subdiv=1, jitter=0.1)
    return kit.tag(a.finish(), "part", collision="none", budget=1500, notes="leaf clump piece")


def _thorn_part(kit):
    a = kit.flintkit.Asset("ThornShrubThorn", "R05 ThornShrub Thorn")
    a.cyl(0.6, 0.0, 2.4, sides=6, loc=(0, 0, 0), mat=THORN, jitter=0.1)
    return kit.tag(a.finish(), "part", collision="none", budget=1500, notes="single thorn")


def _branch(kit):
    a = kit.flintkit.Asset("ThornShrubBranch", "R05 ThornShrub Branch")
    a.cyl(0.85, 0.75, 0.8, sides=7, loc=(0, 0, 0), mat=BARK, jitter=0.03)
    _limb(a, [(0, 0, 0.6), (0.3, 0, 2.0), (0.5, 0, 3.3)], 0.75, 0.62, sides=7)
    _limb(a, [(0.1, 0, 1.5), (-0.9, 0, 2.2), (-1.8, 0, 2.9)], 0.5, 0.42, sides=6)
    return kit.tag(a.finish(), "part", collision="box", budget=1500,
                   notes="Y branch: stout trunk with one 45-degree side limb, flat cut ends")


def _drop(kit):
    a = kit.flintkit.Asset("ThornShrubThorns", "R05 ThornShrub Thorns x2")
    a.cyl(0.55, 0.0, 1.8, sides=6, loc=(-0.9, 0, 0), mat=THORN, jitter=0.03)
    a.cyl(0.55, 0.0, 1.8, sides=6, loc=(0.6, 0, 0.5), rot=(0, 1.05, 0), mat=THORN, jitter=0.03)
    return kit.tag(a.finish(), "drop", collision="none", budget=300, notes="two thorns pickup")


def _depleted(kit):
    a = kit.flintkit.Asset("ThornShrubDepleted", "R05 ThornShrub Depleted")
    a.cyl(0.95, 0.8, 0.9, sides=7, loc=(0, 0, 0), mat=BARK, jitter=0.04)
    hub = (0.0, 0.0, 0.9)
    a.ico(0.8, loc=hub, mat=BARK, subdiv=1, jitter=0.05)
    _limb(a, [hub, (-1.2, -0.2, 0.95), (-2.0, 0.15, 1.35), (-2.7, -0.1, 1.5)], 0.5, 0.26)
    _limb(a, [hub, (-0.55, 0.25, 1.8), (-1.15, 0.0, 2.3), (-1.2, 0.2, 3.1)], 0.46, 0.25)
    _limb(a, [hub, (0.35, -0.15, 2.1), (0.0, 0.1, 2.9), (0.45, 0.0, 4.0)], 0.6, 0.34)
    _limb(a, [hub, (0.75, 0.25, 1.6), (1.25, 0.0, 2.1), (1.5, 0.2, 2.8)], 0.42, 0.24)
    _limb(a, [hub, (1.1, -0.25, 1.0), (1.9, 0.1, 1.05), (2.7, -0.1, 1.6)], 0.48, 0.26)
    return kit.tag(a.finish(), "depleted", collision="hull", budget=2000,
                   notes="bare trunk after harvest")


def build(kit):
    return [_hero(kit), _leaf_cluster(kit), _thorn_part(kit), _branch(kit),
            _drop(kit), _depleted(kit)]
