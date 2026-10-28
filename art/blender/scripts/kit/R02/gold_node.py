"""R02 row 2: GoldNode resource node (warm-brown boulder with fat gold nuggets)."""
import math
import random

SUBJECT = "GoldNode"
ROW = 2
HERO_AZIMUTH = -22
SIDE_AZIMUTH = -90   # the reference side cell is the left side (front on the right)

PALETTE = {
    "r02_base_rock": ("#8C827D", 0.95, 0, 0),
    "r02_gold_host": ("#7B5640", 0.95, 0, 0),
    "r02_gold": ("#E3A817", 0.35, 0.35, 0),
}

HOST = "r02_gold_host"
GOLD = "r02_gold"
BASE = "r02_base_rock"
CHIPS = ["#F2C230", "#C98E12"]
GLINT = ["#FFF6C8", "#FFD966"]
HOST_TINT = 1.12   # uniform per-part brightness (not by facing); sheet colour renders a touch dark
_rng = random.Random(202)


def _rock(a, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=BASE, subdiv=2, rough=0.1, facets=10,
          sink=0.15, tint=None):
    """rock() with a tint: ellipsoid of full extents `size`, buried underside flattened."""
    r = (size[0] / 2, size[1] / 2, size[2] / 2)
    c = (loc[0], loc[1], loc[2] + r[2] * (1 - sink))
    verts = a.ico(r, c, rot, mat=mat, subdiv=subdiv, jitter=rough, tint=tint, facets=facets,
                  face_tint_var=0.05)
    floor = loc[2]
    for v in verts:
        if v.co.z < floor:
            v.co.z = floor
    return verts


def _host_tint():
    return HOST_TINT * (1 + _rng.uniform(-0.04, 0.04))


def _skew(v, H, lean=0.7, narrow=0.32):
    """Egg profile: the crown narrows in depth, leans a little left and toward the back."""
    t = max(0.0, min(1.0, v[2] / H))
    return (v[0] - 0.4 * lean * t * t, v[1] * (1 - narrow * t) + 0.6 * lean * t * t, v[2])


def _host(a, size, rot=(0.0, 0.0, 0.3)):
    verts = _rock(a, size, (0, 0, 0), rot, HOST, subdiv=3, rough=0.07, facets=13, sink=0.15,
                  tint=_host_tint())
    H = size[2] / 2 * 1.85
    for v in verts:
        x, y, z = _skew(v.co, H)
        v.co.x, v.co.y, v.co.z = x, y, z
    return H


def _surface(size, x, z, front=True, protrude=1.0, rn=1.2):
    """Centre for an embedded nugget so it sticks ~protrude out of the host ellipsoid."""
    ra, rb, rc = size[0] / 2, size[1] / 2, size[2] / 2
    zc = rc * 0.85
    q = 1 - (x / ra) ** 2 - ((z - zc) / rc) ** 2
    y = -rb * math.sqrt(max(q, 0.0)) if front else rb * math.sqrt(max(q, 0.0))
    n = (x / ra ** 2, y / rb ** 2, (z - zc) / rc ** 2)
    ln = math.sqrt(sum(c * c for c in n)) or 1.0
    n = tuple(c / ln for c in n)
    p = (x + n[0] * (protrude - rn), y + n[1] * (protrude - rn), z + n[2] * (protrude - rn))
    return _skew(p, rc * 1.85)


def _gem(a, radius, loc, rot=(0, 0, 0), jitter=0.1, facets=9, subdiv=1):
    """Crisp low-poly gem: a jittered icosahedron (20 big planar facets, a few merged)."""
    return a.ico(radius, loc, rot, GOLD, subdiv=subdiv, jitter=jitter, facets=facets, face_tint_var=0.04)


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---------------- hero ----------------
    a = fk.Asset("GoldNode", "R02 GoldNode")
    hs = (9.0, 7.6, 8.1)
    _host(a, hs)
    # big nugget (~3.8 across), centre-right low, facing front
    _gem(a, (2.1, 1.3, 1.95), _surface(hs, 1.3, 2.9, protrude=1.35, rn=1.45), (0.25, 0.15, 0.3), jitter=0.12, facets=14, subdiv=1)
    # medium nugget (~3), front-left, facing front-left so it reads on the left edge from the top
    _gem(a, (1.65, 1.1, 1.75), _surface(hs, -3.3, 4.4, protrude=1.2, rn=1.25), (0.1, -0.35, -0.5), jitter=0.12, facets=14, subdiv=1)
    # small-medium nugget (~2.4) on the upper right shoulder, compact, tilted right
    _gem(a, (1.35, 1.0, 1.4), _surface(hs, 3.4, 5.2, protrude=1.1, rn=1.05), (0.2, 0.5, 0.6), jitter=0.12, facets=14, subdiv=1)
    # small nugget (~1.8) on the crown, toward the back-right
    top = _surface(hs, 1.2, 6.7, front=False, rn=0.55)
    _gem(a, (1.05, 0.85, 0.6), top, (0.1, 0.2, 0.5))
    # light grey base rocks at the toes, outside the host footprint
    _rock(a, (2.9, 2.4, 2.1), (-3.9, -2.9, 0), (0.1, 0, 0.5), BASE, rough=0.1, facets=9)
    _rock(a, (2.3, 2.0, 1.7), (3.8, -3.1, 0), (0, 0.1, -0.4), BASE, rough=0.1, facets=9)
    _rock(a, (1.4, 1.2, 1.0), (-1.3, -3.9, 0), (0, 0, 0.8), BASE, rough=0.1, facets=9)
    o = a.finish()
    vfx.add(o, "harvest_hit", (1, -3.8, 3), color=CHIPS)
    vfx.add(o, "ore_glint", (1.5, -4, 3), scale=0.8, color=GLINT)
    vfx.add(o, "ore_glint", (-3, -3.5, 3.5), scale=0.6, color=GLINT)
    out.append(kit.tag(o, "hero", collision="hull", budget=4500,
                       notes="Gold ore node. harvest_hit: strike face on the big front nugget (gold chips); "
                             "ore_glint x2: twinkles on the big and left nuggets. Swap to GoldNodeDepleted when empty."))

    # ---------------- parts ----------------
    a = fk.Asset("GoldHostRock", "R02 GoldNode part")
    _host(a, (9.0, 7.0, 7.6))
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500, notes="Bare gold host boulder."))

    a = fk.Asset("GoldNugget", "R02 GoldNode part")
    _gem(a, (0.8, 0.7, 2.0), (0, 0, 1.75), (0.05, 0.08, 0.3), jitter=0.07)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=500, notes="Upright elongated gold nugget insert."))

    a = fk.Asset("GoldNuggetB", "R02 GoldNode part")
    _gem(a, (1.25, 1.0, 1.3), (0, 0, 1.1), (0.1, 0.0, 0.6))
    out.append(kit.tag(a.finish(), "part", collision="none", budget=500, notes="Squat gold nugget insert (optional)."))

    a = fk.Asset("GoldBaseRock", "R02 GoldNode part")
    _rock(a, (2.0, 1.7, 1.5), (0, 0, 0), (0, 0, 0.4), BASE, rough=0.1, facets=9)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=400, notes="Small grey base rock for the toes."))

    # ---------------- drops ----------------
    a = fk.Asset("GoldNuggetDrop", "R02 GoldNode drop")
    _gem(a, (0.82, 0.58, 0.62), (0, 0, 0.7), (0.0, 0.3, 0.25), jitter=0.12, facets=6)
    out.append(kit.tag(a.finish(), "drop", collision="box", budget=300, notes="Gold nugget pickup (tilted bar shape)."))

    a = fk.Asset("GoldNuggetDrop2", "R02 GoldNode drop")
    _gem(a, (0.7, 0.6, 0.62), (0, 0, 0.65), (0.7, 0.4, 1.3), jitter=0.18, facets=10)
    out.append(kit.tag(a.finish(), "drop", collision="box", budget=300, notes="Rounder faceted gold nugget pickup."))

    # ---------------- depleted ----------------
    a = fk.Asset("GoldNodeDepleted", "R02 GoldNode depleted")
    # low faceted mound: equator near the ground so the sides taper up, top flattened into a rough plateau
    mv = _rock(a, (8.2, 6.2, 4.0), (0, 0, 0), (0, 0, 0.2), HOST, subdiv=3, rough=0.09, facets=8,
               sink=0.5, tint=_host_tint())
    top = 2.6
    pits = [(-1.6, -1.0), (1.3, -1.3), (0.4, 1.0)]   # where the nuggets were torn out
    for v in mv:
        if v.co.z > top:
            v.co.z = top + (v.co.z - top) * 0.35
        for px, py in pits:
            d = math.hypot(v.co.x - px, v.co.y - py)
            if d < 1.3 and v.co.z > 1.8:
                v.co.z -= 0.85 * (1 - d / 1.3)
    _rock(a, (2.3, 2.0, 1.7), (-4.0, -1.2, 0), (0, 0, 0.5), BASE, rough=0.1, facets=9)
    _rock(a, (2.0, 1.8, 1.4), (3.9, -1.0, 0), (0, 0, -0.3), BASE, rough=0.1, facets=9)
    o = a.finish()
    vfx.add(o, "harvest_deplete", (0, 0, 0.3), color=CHIPS)
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="Depleted (Base): stripped faceted mound with pits. harvest_deplete: final burst at the base centre."))
    return out
