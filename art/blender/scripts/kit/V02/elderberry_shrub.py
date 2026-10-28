"""V02 row 2: Elderberry shrub (hero, parts, variants, fruitless)."""
import math
import random

from mathutils import Vector

SUBJECT = "ElderberryShrub"
ROW = 2
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 135

PALETTE = {
    "v02_bark": ("#7B4A28", 0.9, 0, 0),
    "v02_elder_leaf": ("#2C6B2E", 0.8, 0, 0),
    "v02_elderberry": ("#242C78", 0.4, 0, 0),
}

BARK, LEAF, BERRY = "v02_bark", "v02_elder_leaf", "v02_elderberry"
UP = Vector((0, 0, 1))


# ---------------------------------------------------------------- helpers

def _basis(n):
    n = Vector(n).normalized()
    ref = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = n.cross(ref).normalized()
    v = n.cross(u).normalized()
    return n, u, v


def seg(a, p1, p2, r1, r2, sides=6, mat=BARK, caps=True):
    """Tapered faceted branch segment between two points."""
    bm = a.bm
    p1, p2 = Vector(p1), Vector(p2)
    d, u, v = _basis(p2 - p1)
    ring1, ring2 = [], []
    rot = random.random() * 6.28
    for i in range(sides):
        t = rot + 2 * math.pi * i / sides
        off = u * math.cos(t) + v * math.sin(t)
        c1 = p1 + off * r1
        c2 = p2 + off * r2
        c1.z = max(c1.z, 0.0)
        ring1.append(bm.verts.new(c1))
        ring2.append(bm.verts.new(c2))
    for i in range(sides):
        j = (i + 1) % sides
        bm.faces.new((ring1[i], ring1[j], ring2[j], ring2[i]))
    if caps:
        bm.faces.new(list(reversed(ring1)))
        bm.faces.new(ring2)
    a._finish(ring1 + ring2, mat)


def leaf(a, base, d, n, length, width, curl=0.25, rib=0.1, mat=LEAF):
    """One broad pointed faceted leaf: 12 tris, closed. base point, direction d
    (along the leaf), n (leaf normal)."""
    bm = a.bm
    base, d, n = Vector(base), Vector(d).normalized(), Vector(n)
    s = d.cross(n).normalized()
    n = s.cross(d).normalized()

    def P(x, y, z=0.0):
        t = y / length
        z = z - curl * length * t * t
        p = base + s * x + d * y + n * z
        p.z = max(p.z, 0.02)
        return bm.verts.new(p)

    B = P(0, 0)
    T = P(0, length)
    L1 = P(-width * 0.5, length * 0.36)
    L2 = P(-width * 0.32, length * 0.72)
    R1 = P(width * 0.5, length * 0.36)
    R2 = P(width * 0.32, length * 0.72)
    M1 = P(0, length * 0.32, rib)
    M2 = P(0, length * 0.66, rib * 0.8)
    f = bm.faces.new
    # top (ridge) - normal +n
    f((B, M1, L1)); f((L1, M1, M2, L2)); f((L2, M2, T))
    f((B, R1, M1)); f((R1, R2, M2, M1)); f((R2, T, M2))
    # flat bottom
    f((B, L1, R1)); f((L1, L2, R2, R1)); f((L2, T, R2))
    a._finish([B, T, L1, L2, R1, R2, M1, M2], mat)


def rosette(a, c, n, leaf_len, rng, count=3, lift=0.28, stem=True):
    """Star of three leaves radiating from c, facing normal n."""
    n, u, v = _basis(n)
    a0 = rng.uniform(0, 6.28)
    for k in range(count):
        t = a0 + 2 * math.pi * k / count + rng.uniform(-0.2, 0.2)
        d = u * math.cos(t) + v * math.sin(t)
        d = (d + n * lift).normalized()
        L = leaf_len * rng.uniform(0.9, 1.1)
        leaf(a, Vector(c) + d * 0.1, d, n, L, L * 0.85, curl=rng.uniform(0.05, 0.14))


def bunch(a, c, out, r=0.42, subdiv=1, stalk_to=None):
    """6 navy spheres (ring of 5 + 1 behind) around a brown centre stub facing out."""
    c = Vector(c)
    out, u, v = _basis(out)
    for k in range(5):
        t = 2 * math.pi * k / 5 + 0.3
        p = c + (u * math.cos(t) + v * math.sin(t)) * (r * 1.25) - out * 0.05
        a.ico(r, loc=tuple(p), mat=BERRY, subdiv=subdiv)
    a.ico(r * 1.05, loc=tuple(c - out * r * 0.8), mat=BERRY, subdiv=subdiv)
    # centre stub
    seg(a, c - out * 0.1, c + out * (r * 0.75), r * 0.28, r * 0.18, sides=5)
    # stalk
    top = Vector(stalk_to) if stalk_to else c + UP * 1.0 - out * 0.4
    seg(a, c - out * 0.2, top, 0.08, 0.06, sides=4)


def shell_rosettes(a, rng, centre, semi, n, leaf_len, zmin_el=-0.05, avoid=(), avoid_r=1.5):
    """Fibonacci-distribute n rosettes over the upper ellipsoid cap."""
    cx, cy, cz = centre
    sx, sy, sz = semi
    golden = math.pi * (3 - math.sqrt(5))
    zlo = math.sin(zmin_el)
    for i in range(n):
        zz = 1 - (i + 0.5) / n * (1 - zlo)
        rr = math.sqrt(max(0.0, 1 - zz * zz))
        th = i * golden + rng.uniform(-0.2, 0.2)
        dx, dy, dz = rr * math.cos(th), rr * math.sin(th), zz
        p = Vector((cx + dx * sx, cy + dy * sy, cz + dz * sz))
        p += Vector((rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), rng.uniform(-0.15, 0.15)))
        if any((p - Vector(b)).length < avoid_r for b in avoid):
            continue
        nrm = Vector((dx / sx, dy / sy, dz / sz)).normalized()
        nrm = (nrm + UP * 0.3 + Vector((rng.uniform(-.3, .3), rng.uniform(-.3, .3), 0))).normalized()
        rosette(a, p, nrm, leaf_len, rng)


def branches(a, rng, arms, base_r=0.6, split_z=0.9, sub=True):
    """Short thick trunk forking low into arms; each arm forks again."""
    seg(a, (0, 0, 0), (0, 0, split_z), base_r, base_r * 0.85, sides=7)
    # root flare
    for ang in (0.4, 2.5, 4.4):
        seg(a, (0, 0, 0.35), (math.cos(ang) * base_r * 1.5, math.sin(ang) * base_r * 1.5, 0.0),
            base_r * 0.45, base_r * 0.25, sides=5)
    tips = []
    for (ang, reach, h) in arms:
        mid = Vector((math.cos(ang) * reach * 0.55, math.sin(ang) * reach * 0.55, split_z + h * 0.5))
        seg(a, (0, 0, split_z * 0.8), mid, base_r * 0.6, base_r * 0.45)
        if sub:
            for da in (-0.45, 0.45):
                a2 = ang + da + rng.uniform(-0.1, 0.1)
                tip = Vector((math.cos(a2) * reach, math.sin(a2) * reach, split_z + h))
                seg(a, mid, tip, base_r * 0.4, base_r * 0.18, sides=5)
                tips.append(tip)
        else:
            tips.append(mid)
    return tips


def on_shell(centre, semi, direction, k=1.3):
    d = Vector(direction).normalized()
    return Vector(centre) + Vector((d.x * semi[0], d.y * semi[1], d.z * semi[2])) * k


def shrub(kit, name, seed, arms, centre, semi, n_ros, leaf_len, bunch_dirs, base_r=0.6,
          extra_low=()):
    fk = kit.flintkit
    a = fk.Asset(name, "V02 " + name, seed=seed)
    rng = random.Random(seed)
    branches(a, rng, arms, base_r=base_r)
    bpos = [on_shell(centre, semi, d) for d in bunch_dirs]
    for p, d in zip(bpos, bunch_dirs):
        out = Vector(d).normalized()
        out = (out - UP * 0.2).normalized()
        bunch(a, p, out)
    shell_rosettes(a, rng, centre, semi, n_ros, leaf_len, avoid=bpos)
    for (p, nrm) in extra_low:
        rosette(a, p, nrm, leaf_len, rng)
    return a.finish(), bpos


HERO_ARMS = [(math.radians(-60), 2.8, 3.4), (math.radians(-135), 2.9, 2.8),
             (math.radians(40), 2.8, 3.2), (math.radians(140), 2.6, 3.6)]
HERO_C, HERO_S = (0, 0, 3.7), (3.1, 2.7, 2.3)
HERO_BUNCH = [(-0.1, -1.0, 0.8), (-0.9, -0.75, 0.15), (0.95, -0.6, 0.35), (0.3, 1.0, 0.5)]
HERO_LOW = [((-3.0, -0.4, 2.2), (-1, -0.3, 0.5)), ((3.0, -0.1, 2.3), (1, -0.3, 0.5)),
            ((-2.4, -1.6, 2.4), (-0.7, -0.8, 0.4)), ((2.4, -1.5, 2.5), (0.7, -0.8, 0.4)),
            ((0.5, 2.5, 2.2), (0, 1, 0.5))]


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---- hero
    o, bp = shrub(kit, "ElderberryShrub", 11, HERO_ARMS, HERO_C, HERO_S, 40, 2.1, HERO_BUNCH,
                  extra_low=HERO_LOW)
    vfx.add(o, "harvest_hit", tuple(bp[0] * 0.8), color=["#2C6B2E", "#242C78"])
    out.append(kit.tag(o, "hero", collision="hull", budget=3500,
                       notes="Wide forked elderberry shrub with 4 navy berry bunches. "
                             "harvest_hit socket on the front bunch (leaf/berry colours) for picking."))

    # ---- parts
    a = fk.Asset("ElderberryForkedStem", "V02 ElderberryForkedStem", seed=3)
    seg(a, (0, 0, 0), (0, 0, 2.1), 0.7, 0.45, sides=7)
    seg(a, (0, 0, 1.9), (-1.0, 0.1, 4.0), 0.38, 0.24, sides=6)
    seg(a, (0, 0, 1.9), (1.1, -0.1, 3.8), 0.36, 0.22, sides=6)
    seg(a, (-0.7, 0.05, 3.3), (-1.25, 0.0, 3.6), 0.1, 0.06, sides=4)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="Forked base stem, cut ends."))

    a = fk.Asset("ElderberryLeafClump", "V02 ElderberryLeafClump", seed=4)
    seg(a, (0, 0, 0), (0, 0, 1.3), 0.08, 0.06, sides=5)
    c = Vector((0, 0, 1.3))
    nrm = Vector((0, -1, 0.15))
    for ang, L in ((90, 1.7), (200, 1.45), (-20, 1.45)):
        t = math.radians(ang)
        d = Vector((math.cos(t), 0, math.sin(t)))
        leaf(a, c, d, nrm, L, L * 0.85, curl=0.12)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="Three-leaf clump on a stem."))

    a = fk.Asset("ElderberryBerryBunch", "V02 ElderberryBerryBunch", seed=5)
    bunch(a, (0, 0, 0.8), Vector((0, -1, 0.15)), r=0.34, subdiv=2, stalk_to=(0, 0.2, 1.7))
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="6-sphere berry bunch, stalk and nub."))

    a = fk.Asset("ElderberryLeafUnderside", "V02 ElderberryLeafUnderside", seed=6)
    leaf(a, (-0.8, 0.6, 0.35), Vector((1, -0.7, 0.05)), Vector((0, 0, -1)), 2.2, 1.35, curl=-0.12)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="Single leaf, underside up."))

    # ---- variants
    a = fk.Asset("ElderberryShrubYoung", "V02 ElderberryShrubYoung", seed=7)
    rng = random.Random(7)
    seg(a, (0, 0, 0), (0, 0, 0.6), 0.25, 0.2, sides=6)
    tips = []
    for ang, reach, h in ((-1.2, 1.4, 3.0), (2.2, 1.3, 2.7), (0.6, 1.2, 3.2)):
        mid = Vector((math.cos(ang) * reach * 0.5, math.sin(ang) * reach * 0.5, 0.6 + h * 0.5))
        seg(a, (0, 0, 0.5), mid, 0.15, 0.1, sides=5)
        for da in (-0.5, 0.5):
            tip = Vector((math.cos(ang + da) * reach, math.sin(ang + da) * reach, 0.6 + h * rng.uniform(0.8, 1.0)))
            seg(a, mid, tip, 0.1, 0.05, sides=4)
            tips.append(tip)
    for tp in tips:
        nrm = (Vector((tp.x, tp.y, 0)).normalized() * 0.5 + UP).normalized()
        rosette(a, tp, nrm, 1.8, rng)
    rosette(a, (0.1, -0.1, 3.6), UP, 1.8, rng)
    rosette(a, (0.9, -0.7, 1.6), Vector((0.6, -0.6, 0.6)), 1.4, rng)
    rosette(a, (-1.0, 0.6, 1.8), Vector((-0.6, 0.6, 0.6)), 1.4, rng)
    o = a.finish()
    out.append(kit.tag(o, "variant", collision="hull", budget=3000, notes="Young airy shrub, no berries."))

    m_arms = [(math.radians(-90), 2.9, 3.2), (math.radians(-10), 3.3, 2.6), (math.radians(-170), 3.3, 2.6),
              (math.radians(70), 2.8, 3.4), (math.radians(115), 2.8, 3.0)]
    m_bunch = [(-0.55, -1.0, 0.85), (0.6, -1.0, 0.7), (0.0, -1.0, 0.15), (-0.6, 0.9, 0.6)]
    o, bp = shrub(kit, "ElderberryShrubMature", 21, m_arms, (0, 0, 3.7), (3.2, 2.5, 2.2), 40, 2.0,
                  m_bunch, extra_low=HERO_LOW[:4])
    vfx.add(o, "harvest_hit", tuple(bp[2] * 0.8), color=["#2C6B2E", "#242C78"])
    out.append(kit.tag(o, "variant", collision="hull", budget=3000,
                       notes="Wide mature shrub, 5 arms, 4 bunches across the front top. harvest_hit on the front bunch."))

    o, _ = shrub(kit, "ElderberryShrubFruitless", 11, HERO_ARMS, HERO_C, HERO_S, 40, 2.1, [],
                 extra_low=HERO_LOW)
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="Hero shrub after picking: same branches and leaves, no berries."))
    return out
