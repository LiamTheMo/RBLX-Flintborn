"""V02 row 1: Raspberry bush (open three-cane bush, 3-leaf clusters, red berries)."""
import math
import random

SUBJECT = "RaspberryBush"
ROW = 1
HERO_AZIMUTH = -22

PALETTE = {
    "v02_bark": ("#7B4A28", 0.9, 0, 0),
    "v02_raspberry_leaf": ("#3A9A22", 0.8, 0, 0),
    "v02_raspberry": ("#D41C28", 0.5, 0, 0),
}

BARK, LEAF, BERRY = "v02_bark", "v02_raspberry_leaf", "v02_raspberry"


# ---------------------------------------------------------------- helpers
def seg(a, p1, p2, r1, r2, sides=7, mat=BARK, ext=0.15):
    """Tapered faceted cylinder from p1 to p2 (slightly overlapped at joints)."""
    dx, dy, dz = (p2[i] - p1[i] for i in range(3))
    ln = math.sqrt(dx * dx + dy * dy + dz * dz)
    pitch = math.acos(max(-1.0, min(1.0, dz / ln)))
    yaw = math.atan2(dy, dx)
    a.cyl(r1, r2, ln + ext, sides=sides, loc=p1, rot=(0, pitch, yaw), mat=mat, jitter=0.02)


def leaf(a, L, pos, yaw, tilt, fold=0.22, roll=0.0, W=0.68, fine=False):
    """Broad pointed leaf, two halves folded along the midrib. Leaf points +X
    before orienting; tilt > 0 raises the tip."""
    w = W * L
    if fine:
        up = [(0, 0), (L, 0), (0.74 * L, 0.30 * w), (0.46 * L, 0.50 * w), (0.17 * L, 0.40 * w)]
    else:
        up = [(0, 0), (L, 0), (0.62 * L, 0.48 * w), (0.22 * L, 0.42 * w)]
    lo = [(0, 0)] + [(x, -y) for x, y in reversed(up[2:])] + [(L, 0)]
    for pts, f in ((up, fold), (lo, -fold)):
        v = a.poly_prism(pts, 0.05, (0, 0, 0), (f, 0, 0), LEAF)
        a.transform(v, pos, (roll, -tilt, yaw))


def leaf_trio(a, pos, yaw, tilt, L=1.8, rng=None, spread=0.95, roll=0.0, fine=False):
    """One 3-leaf cluster: big centre leaf plus two side leaves."""
    j = (lambda s: rng.uniform(-s, s)) if rng else (lambda s: 0.0)
    leaf(a, L, pos, yaw + j(0.15), tilt + j(0.1), roll=roll + j(0.2), fine=fine)
    for s in (-1, 1):
        leaf(a, L * 0.8, pos, yaw + s * (spread + j(0.15)), tilt - 0.15 + j(0.1),
             roll=roll + s * 0.3 + j(0.15), fine=fine)


def berry_clump(a, pos, r=0.28, lobes=5, rng=None, stalk=True):
    x, y, z = pos
    a.ico(r * 0.85, (x, y, z + r * 0.9), (0, 0, 0), BERRY, subdiv=1)
    for i in range(lobes - 1):
        ang = i * 2 * math.pi / (lobes - 1) + (rng.uniform(-0.3, 0.3) if rng else 0)
        a.ico(r, (x + math.cos(ang) * r * 1.05, y + math.sin(ang) * r * 1.05,
                  z + (rng.uniform(-0.08, 0.08) if rng else 0)), (0, 0, 0), BERRY, subdiv=1)
    if stalk:
        seg(a, (x, y, z + r * 1.3), (x * 0.78, y * 0.78, z + r * 1.3 + 0.9), 0.08, 0.06, sides=5)


# ---------------------------------------------------------------- whole bush
def bush(a, seed, scale=1.0, n_clusters=19, berries=(), stubs=(), cane_r=0.45, crown=3,
         rot0=0.0, leaf_len=2.2, branches=2):
    rng = random.Random(seed)
    s = scale
    # short shared base
    a.cyl(cane_r * 1.4 * s, cane_r * 1.15 * s, 0.45 * s, sides=8, mat=BARK, jitter=0.03)
    base = (0, 0, 0.3 * s)
    # three canes fanning out in a V
    for ang0 in (-150, -30, 90):
        ang = rot0 + math.radians(ang0) + rng.uniform(-0.2, 0.2)
        lean = rng.uniform(1.4, 1.8)
        mid = (math.cos(ang) * lean * 0.5 * s, math.sin(ang) * lean * 0.5 * s, 2.3 * s)
        top = (math.cos(ang) * lean * s, math.sin(ang) * lean * s, 4.9 * s)
        seg(a, base, mid, cane_r * s, cane_r * 0.8 * s)
        seg(a, mid, top, cane_r * 0.8 * s, cane_r * 0.45 * s)
        for h, off in ((0.45, 0.9), (0.7, -0.85), (0.3, -1.1))[:branches]:
            p = tuple(base[i] + (top[i] - base[i]) * h for i in range(3))
            ba = ang + off + rng.uniform(-0.2, 0.2)
            bl = rng.uniform(1.2, 1.6) * s
            end = (p[0] + math.cos(ba) * bl, p[1] + math.sin(ba) * bl, p[2] + bl * 0.75)
            seg(a, p, end, cane_r * 0.45 * s, cane_r * 0.25 * s, sides=6)
    # leaf clusters on a dome shell, area-uniform, lower third left open
    cz, rxy, rz = 3.3 * s, 1.75 * s, 2.1 * s
    lo, hi = math.sin(math.radians(-30)), 1.0
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(n_clusters):
        t = (i + 0.5) / n_clusters
        phi = math.asin(min(1.0, lo + (hi - lo) * t))
        th = rot0 + i * golden + rng.uniform(-0.25, 0.25)
        cp = math.cos(phi)
        pos = (math.cos(th) * cp * rxy, math.sin(th) * cp * rxy, cz + math.sin(phi) * rz)
        deg = math.degrees(phi)
        if deg > 62:            # crown: flat-ish rosette
            yaw, tilt = rng.uniform(0, 2 * math.pi), rng.uniform(0.1, 0.4)
        elif deg > 15:          # upper flank: leaves rise outward, faces out
            yaw, tilt = th + rng.uniform(-0.35, 0.35), rng.uniform(0.45, 0.85)
        else:                   # lower flank: outward and drooping, faces out
            yaw = th + rng.uniform(-0.35, 0.35)
            tilt = rng.choice((-0.5, 1)) * rng.uniform(0.45, 0.8)
        leaf_trio(a, pos, yaw, tilt, L=leaf_len * s * rng.uniform(0.9, 1.1), rng=rng,
                  roll=rng.uniform(-0.4, 0.4))
    # crown rosette closing the top of the dome
    for k in range(crown):
        th = rot0 + k * 2 * math.pi / max(1, crown) + rng.uniform(-0.3, 0.3)
        pos = (math.cos(th) * 0.45 * s, math.sin(th) * 0.45 * s, cz + rz * 0.97)
        leaf_trio(a, pos, th + rng.uniform(-0.3, 0.3), rng.uniform(0.1, 0.3),
                  L=leaf_len * s * rng.uniform(0.95, 1.1), rng=rng, roll=rng.uniform(-0.3, 0.3))
    # berry clumps hung at the outside edges
    for az, el in berries:
        th, ph = math.radians(az), math.radians(el)
        rr = rxy + 1.5 * s
        pos = (math.cos(th) * math.cos(ph) * rr, math.sin(th) * math.cos(ph) * rr,
               cz + math.sin(ph) * rz * 0.9 - 0.4 * s)
        berry_clump(a, pos, r=0.28 * s, rng=rng)
    for az, el in stubs:
        th, ph = math.radians(az), math.radians(el)
        rr = rxy + 0.6 * s
        p = (math.cos(th) * math.cos(ph) * rr, math.sin(th) * math.cos(ph) * rr,
             cz + math.sin(ph) * rz * 0.9 - 0.1 * s)
        seg(a, p, (p[0] * 0.85, p[1] * 0.85, p[2] + 0.45 * s), 0.1 * s, 0.07 * s, sides=5)


HERO_BERRIES = ((-60, 35), (-120, 5), (-170, 25), (-20, 0), (100, 30))
FRUIT_BERRIES = ((-70, 0), (-140, 30), (0, 25), (95, 5), (190, 30))


def build(kit):
    fk = kit.flintkit
    out = []

    a = fk.Asset("RaspberryBush", "V02 RaspberryBush")
    bush(a, seed=11, berries=HERO_BERRIES)
    out.append(kit.tag(a.finish(), "hero", collision="hull", budget=3000,
                       notes="Full & fruiting raspberry bush; leafy, but hull for the canes. No VFX."))

    # ---- parts
    a = fk.Asset("RaspberryCane", "V02 RaspberryCane")
    a.cyl(0.42, 0.34, 1.9, sides=8, mat=BARK, jitter=0.02)
    a.beam((0, 0, 1.8), (-0.95, 0.0, 3.5), 0.27, sides=7, mat=BARK, end_mat="wood_end")
    a.beam((0, 0, 1.8), (0.8, 0.0, 3.3), 0.25, sides=7, mat=BARK, end_mat="wood_end")
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="Y-shaped cane stem with cut ends."))

    a = fk.Asset("RaspberryLeafCluster", "V02 RaspberryLeafCluster")
    seg(a, (0, -0.7, 0.1), (0, 0.0, 0.3), 0.08, 0.06, sides=5)
    leaf_trio(a, (0, 0, 0.3), math.pi / 2, 0.12, L=1.7, spread=1.0, fine=True)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="Three-leaf cluster on a short stalk."))

    a = fk.Asset("RaspberryBerryCluster", "V02 RaspberryBerryCluster")
    a.ico(0.24, (0, 0, 0.46), (0, 0, 0), BERRY, subdiv=1)
    for i in range(4):
        ang = i * math.pi / 2 + math.pi / 4
        a.ico(0.36, (math.cos(ang) * 0.26, math.sin(ang) * 0.26, 0.37), (0, 0, 0), BERRY,
              subdiv=1)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="Berry module: 4 lobes around a centre."))

    a = fk.Asset("RaspberryLeafUnderside", "V02 RaspberryLeafUnderside")
    leaf(a, 2.0, (-1.0, 0, 0.05), 0.0, 0.0, fold=0.35, W=0.55, fine=True)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="Single leaf, slightly curled along the midrib."))

    # ---- variations
    a = fk.Asset("RaspberryBushYoung", "V02 RaspberryBushYoung")
    bush(a, seed=5, scale=0.56, n_clusters=7, crown=1, cane_r=0.34, leaf_len=2.5, branches=1)
    out.append(kit.tag(a.finish(), "variant", collision="hull", budget=3000,
                       notes="Young small bush, sparse, no berries."))

    a = fk.Asset("RaspberryBushFruiting", "V02 RaspberryBushFruiting")
    bush(a, seed=23, berries=FRUIT_BERRIES, rot0=0.6)
    out.append(kit.tag(a.finish(), "variant", collision="hull", budget=3000,
                       notes="Full & fruiting, different clump layout from the hero."))

    a = fk.Asset("RaspberryBushHarvested", "V02 RaspberryBushHarvested")
    bush(a, seed=11, stubs=HERO_BERRIES[:3])
    out.append(kit.tag(a.finish(), "depleted", collision="hull", budget=2000,
                       notes="Harvested (fruitless) state: hero canes and leaves, calyx stubs, no berries. "
                             "Swap target after harvesting the hero."))
    return out
