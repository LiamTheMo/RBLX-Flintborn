"""R08 row 2: Frost Shrub resource node (bare forked sapling, ice nodules,
blue lozenge leaves, rock ring with a snowy ice slab)."""
import math
from mathutils import Vector

SUBJECT = "FrostShrub"
ROW = 2
HERO_AZIMUTH = -22

PALETTE = {
    "r08_rock": ("#6A5A50", 0.95, 0, 0),  # ALL bases, pebbles and ground dirt on every row (single grey-brown rock/soil key)
    "r08_ice": ("#9FC4EE", 0.3, 0, 0),  # Frost Shrub ice nodules, Frost Bud drop, snow drifts on the base
    "r08_frost_leaf": ("#3A66AE", 0.55, 0, 0),  # Frost Shrub blue leaves, Icy Leaf drop
    "r08_twig": ("#684738", 0.9, 0, 0),  # Frost Shrub forked stem and stumps in its depleted base
}

TWIG, ICE, LEAF, ROCK = "r08_twig", "r08_ice", "r08_frost_leaf", "r08_rock"
ICE_CHIPS = ["#CFE6FF", "#9FC4EE"]


def _rot_to(d):
    d = Vector(d).normalized()
    return tuple(Vector((0, 0, 1)).rotation_difference(d).to_euler())


def limb(a, p1, p2, r1, r2, mat=TWIG, sides=6):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    a.cyl(r1, r2, d.length, sides=sides, loc=tuple(p1), rot=_rot_to(d), mat=mat, jitter=0.03)


def knot(a, p, r, mat=TWIG):
    a.ico(r, loc=tuple(p), mat=mat, subdiv=1, jitter=0.05)


def nodule(a, p, size=(2.5, 2.5, 3.3), tilt=(0, 0, 0), mat=ICE):
    """Faceted ice nodule, pointed ends; p is its bottom tip."""
    rx, ry, rz = size[0] / 2, size[1] / 2, size[2] / 2
    c = (p[0], p[1], p[2] + rz * 0.9)
    v = a.ico((rx, ry, rz), loc=(0, 0, 0), mat=mat, subdiv=1, jitter=0.08)
    a.transform(v, loc=c, rot=tilt)


def leaf(a, base, d, length=3.5, width=1.5, thick=0.5, mat=LEAF):
    """Pointed lozenge blade from `base` along direction d, thin across Y."""
    d = Vector(d).normalized()
    c = Vector(base) + d * (length * 0.48)
    v = a.ico((width / 2, thick / 2, length / 2), loc=(0, 0, 0), mat=mat, subdiv=1, jitter=0.04)
    a.transform(v, loc=tuple(c), rot=_rot_to(d))


def stem(a, scale=1.0, tips=True):
    """Trunk plus forked branches. Returns tip points: (kind, point, direction)."""
    s = scale
    V = lambda x, y, z: Vector((x * s, y * s, z * s))
    fork = V(0.1, 0.1, 2.6)
    limb(a, V(0, 0, 0), V(0.05, 0.05, 1.4), 1.15 * s, 0.9 * s, sides=7)
    limb(a, V(0.05, 0.05, 1.4), fork, 0.9 * s, 0.7 * s, sides=7)
    knot(a, fork, 0.72 * s)
    out = []
    # (mid point, [(tip, kind)]) per main limb
    limbs = [
        (V(-1.8, 0.1, 4.0), [(V(-2.7, 0.2, 4.9), "nodule"), (V(-2.6, -0.3, 3.8), "leaf")]),
        (V(1.6, 0.3, 4.2), [(V(2.4, 0.4, 5.2), "nodule"), (V(2.6, 0.0, 4.3), "leaf")]),
        (V(0.9, -0.9, 3.3), [(V(1.6, -1.4, 3.6), "small"), (V(1.0, -1.2, 4.2), "stub")]),
        (V(-0.4, 0.4, 4.6), [(V(-0.7, 0.3, 5.6), "leaf"), (V(0.2, 0.6, 5.5), "stub")]),
        (V(-1.0, -0.8, 3.0), [(V(-1.8, -1.2, 3.1), "leaf")]),
    ]
    for mid, forks in limbs:
        limb(a, fork, mid, 0.6 * s, 0.42 * s)
        knot(a, mid, 0.42 * s)
        for tip, kind in forks:
            limb(a, mid, tip, 0.4 * s, 0.24 * s, sides=5)
            out.append((kind, tip, tip - mid))
    return out


def ring(a, rx=3.4, ry=2.9, n=9, rsize=(2.4, 2.0, 1.3), crystals=True, snow=True, cs=1.0):
    for i in range(n):
        t = 2 * math.pi * i / n + 0.2
        k = 1.0 + 0.12 * math.sin(i * 2.3)
        sz = (rsize[0] * k, rsize[1] * (2 - k), rsize[2] * (0.85 + 0.25 * abs(math.sin(i * 1.7))))
        a.rock(sz, loc=(rx * math.cos(t), ry * math.sin(t), 0), rot=(0, 0, t), mat=ROCK,
               subdiv=1, facets=10)
    if snow:  # snowy ice drift mound filling the centre, just above the rocks
        a.rock((rx * 1.8, ry * 1.8, 1.7), loc=(0, 0, 0), mat=ICE, subdiv=1, facets=8, sink=0.3)
    else:  # dished brown floor
        a.rock((rx * 1.8, ry * 1.8, 0.7), loc=(0, 0, 0), mat=ROCK, subdiv=1, facets=6, sink=0.4)
    if crystals:
        for (x, y, r) in [(-2.4, -1.9, 0.8), (1.9, -2.1, 0.95), (3.0, 0.7, 0.7),
                          (-3.0, 0.9, 0.75), (0.3, -2.7, 0.6)]:
            r *= cs
            a.ico((r, r, r * 1.15), loc=(x, y, 0.5 + r), rot=(0.3, 0.2, x), mat=ICE,
                  subdiv=1, jitter=0.1)


def _recolor(vfx, kind):
    """Ice-coloured chips (and pale frosty dust) for the harvest bursts."""
    ems = [dict(e) for e in vfx.KINDS[kind]["emitters"]]
    for e in ems:
        e["color"] = list(ICE_CHIPS[::-1]) if e["name"] == "Chips" else ["#E4F0FF", "#CFE6FF"]
    return [e for e in ems if e["name"] == "Chips"]


def _vapour(vfx):
    """Low cold mist creeping over the snow slab (no tall plume over the trunk)."""
    e = dict(vfx.KINDS["vapour"]["emitters"][0])
    e.update(color=["#CFE6FF", "#E8F3FF"], size=[1.5, 3.5], transparency=[0.9, 0.8, 1.0],
             speed=[0.2, 0.5], acceleration=[0.15, 0.1, 0], rate=2, shape=[5.0, 0.3, 4.0])
    return [e]


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    res = []

    # ---- hero ----
    a = fk.Asset("FrostShrub", "R08 FrostShrub")
    ring(a)
    tips = stem(a)
    for kind, tip, d in tips:
        if kind == "nodule":
            nodule(a, tip - Vector((0, 0, 0.3)), size=(2.3, 2.2, 3.1),
                   tilt=(0.0, -0.2 * math.copysign(1, tip.x), 0.4))
        elif kind == "small":
            nodule(a, tip - Vector((0, 0, 0.6)), size=(1.6, 1.6, 2.2), tilt=(0.2, -0.3, 0.9))
        elif kind == "leaf":
            dd = Vector(d).normalized() + Vector((0, 0, 0.45))
            leaf(a, tip - Vector(d).normalized() * 0.2, dd, length=3.4, width=1.9)
    o = a.finish()
    vfx.add(o, "vapour", (0, 0, 1), scale=0.8, emitters=_vapour(vfx))
    vfx.add(o, "harvest_hit", (0, -2, 4), emitters=_recolor(vfx, "harvest_hit"))
    res.append(kit.tag(o, "hero", collision="hull", budget=3000,
                       notes="vapour: cold white mist off the snow slab; harvest_hit: ice chips on the front strike face"))

    # ---- parts ----
    a = fk.Asset("FrostShrubForkedStem", "R08 FrostShrub forked stem")
    limb(a, (0, 0, 0), (0, 0, 2.4), 0.6, 0.45, sides=7)
    knot(a, (0, 0, 2.4), 0.46)
    for mid, tip, stub in [((-1.5, 0, 4.3), (-2.3, 0, 5.8), (-2.4, 0, 4.4)),
                           ((1.4, 0, 4.2), (2.3, 0, 5.6), (2.5, 0, 4.5)),
                           ((0.2, 0, 4.9), (0.1, 0, 6.0), None)]:
        limb(a, (0, 0, 2.4), mid, 0.4, 0.3)
        knot(a, mid, 0.3)
        limb(a, mid, tip, 0.28, 0.2, sides=5)
        if stub:
            limb(a, mid, stub, 0.24, 0.17, sides=5)
    res.append(kit.tag(a.finish(), "part", collision="none", notes="trunk and branches only"))

    a = fk.Asset("FrostShrubIceNodule", "R08 FrostShrub ice nodule")
    nodule(a, (0, 0, 0))
    res.append(kit.tag(a.finish(), "part", collision="none"))

    a = fk.Asset("FrostShrubLeaf", "R08 FrostShrub leaf")
    limb(a, (0, 0, 0), (0.25, 0, 0.7), 0.08, 0.06, mat=LEAF, sides=4)
    leaf(a, (0.15, 0, 0.55), (1.0, 0, 0.45), width=1.6)
    res.append(kit.tag(a.finish(), "part", collision="none"))

    a = fk.Asset("FrostShrubBase", "R08 FrostShrub base")
    ring(a, snow=False, cs=0.65)
    res.append(kit.tag(a.finish(), "part", collision="none"))

    # ---- drops ----
    a = fk.Asset("FrostBud", "R08 Frost Bud drop")
    nodule(a, (0, 0, 0), size=(1.3, 1.3, 1.8))
    res.append(kit.tag(a.finish(), "drop", collision="box", budget=300))

    a = fk.Asset("IcyLeaf", "R08 Icy Leaf drop")
    leaf(a, (0, 0, 0), (1.0, 0, 0.5), length=2.2, width=0.95, thick=0.32)
    res.append(kit.tag(a.finish(), "drop", collision="box", budget=300))

    # ---- depleted ----
    a = fk.Asset("FrostShrubDepleted", "R08 FrostShrub depleted")
    ring(a, snow=False, cs=0.65)
    limb(a, (0, 0, 0), (0, 0, 1.5), 0.75, 0.5, sides=7)
    knot(a, (0, 0, 1.5), 0.5)
    limb(a, (0, 0, 1.5), (-0.8, 0, 2.5), 0.32, 0.2, sides=5)
    limb(a, (0, 0, 1.5), (0.75, 0.1, 2.4), 0.3, 0.2, sides=5)
    o = a.finish()
    vfx.add(o, "harvest_deplete", (0, 0, 0.5), emitters=_recolor(vfx, "harvest_deplete"))
    res.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="harvest_deplete: ice burst at base centre when the shrub is stripped"))
    return res
