"""R03 row 1: Quartz resource node (hero, parts, two drops, depleted base)."""
import math
import random

import bmesh
from mathutils import Euler, Matrix, Vector

SUBJECT = "Quartz"
ROW = 1
HERO_AZIMUTH = -22

PALETTE = {
    "r03_rock": ("#8C7E78", 0.9, 0, 0),
    "r03_quartz": ("#D8CFC8", 0.35, 0, 0),
}

QZ = "r03_quartz"
RK = "r03_rock"
CHIPS = ["#E6DED8", "#C9BFB8"]


def _ring(bm, r, z, ox, oy, spin, rng, slope=0.0, phi=0.0, rj=0.05):
    vs = []
    for i in range(6):
        t = spin + i * math.pi / 3
        rr = r * (1 + rng.uniform(-rj, rj))
        vs.append(bm.verts.new((ox + rr * math.cos(t), oy + rr * math.sin(t),
                                z + slope * math.cos(t - phi) + rng.uniform(-0.03, 0.03) * r)))
    return vs


def _bridge(bm, lo, hi):
    for i in range(6):
        j = (i + 1) % 6
        bm.faces.new((lo[i], lo[j], hi[j]))
        bm.faces.new((lo[i], hi[j], hi[i]))


def _ridge(bm, ring, a, b):
    """Chisel tip: ring verts 0-2 meet apex a, 3-5 meet apex b, ridge a-b."""
    r = ring
    for f in ((r[0], r[1], a), (r[1], r[2], a), (r[2], r[3], b), (r[2], b, a),
              (r[3], r[4], b), (r[4], r[5], b), (r[5], r[0], a), (r[5], a, b)):
        bm.faces.new(f)


def crystal(a, r, h, tip, loc=(0, 0, 0), rot=(0, 0, 0), spin=math.radians(30),
            skew=(0.0, 0.0), rng=None, bottom_tip=0.0, kink=(0.0, 0.0), slope=0.22,
            ridge=0.32, drop=0.3, ground=False):
    """Chunky hexagonal quartz prism: kinked shaft (4 rings), sloped shoulder,
    two bevel rings and a chiselled 2-apex ridge tip. Optional pointed bottom.
    Built in a private bmesh and copied into the asset."""
    rng = rng or random.Random(1)
    bm = bmesh.new()
    phi = math.atan2(skew[1], skew[0]) if (skew[0] or skew[1]) else rng.uniform(0, math.tau)
    kx, ky = kink
    rings = []
    if bottom_tip:
        rings.append(_ring(bm, r * 0.62, -bottom_tip * 0.45, 0, 0, spin, rng, -r * slope, phi + 1.0))
    rings.append(_ring(bm, r, 0.0, 0, 0, spin, rng, rj=0.03))
    rings.append(_ring(bm, r * 1.04, h * 0.4, kx * 0.6, ky * 0.6, spin, rng))
    rings.append(_ring(bm, r * 1.0, h * 0.72, kx, ky, spin, rng))
    rings.append(_ring(bm, r * 0.96, h, kx * 0.8, ky * 0.8, spin, rng, r * slope, phi))
    sx, sy = kx * 0.8 + skew[0] * 0.5, ky * 0.8 + skew[1] * 0.5
    rings.append(_ring(bm, r * 0.86, h + tip * 0.16, kx * 0.8 + skew[0] * 0.2,
                       ky * 0.8 + skew[1] * 0.2, spin + 0.06, rng, r * slope, phi))
    rings.append(_ring(bm, r * 0.6, h + tip * 0.45, sx, sy, spin + 0.12, rng, r * slope * 0.8, phi))
    for lo, hi in zip(rings, rings[1:]):
        _bridge(bm, lo, hi)
    top = rings[-1]
    cx, cy = kx * 0.8 + skew[0], ky * 0.8 + skew[1]
    t1 = spin + math.pi / 3
    t4 = spin + 4 * math.pi / 3
    pa = bm.verts.new((cx + ridge * r * math.cos(t1), cy + ridge * r * math.sin(t1), h + tip))
    pb = bm.verts.new((cx + ridge * r * math.cos(t4), cy + ridge * r * math.sin(t4),
                       h + tip * (1 - drop)))
    _ridge(bm, top, pa, pb)
    if bottom_tip:
        bot = rings[0]
        qa = bm.verts.new((ridge * r * 0.8 * math.cos(t1 + 0.5), ridge * r * 0.8 * math.sin(t1 + 0.5),
                           -bottom_tip))
        qb = bm.verts.new((ridge * r * 0.8 * math.cos(t4 + 0.5), ridge * r * 0.8 * math.sin(t4 + 0.5),
                           -bottom_tip * 0.7))
        _ridge(bm, bot, qa, qb)
    else:
        bm.faces.new(list(reversed(rings[0])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    m = Matrix.Translation(Vector(loc)) @ Euler(rot).to_matrix().to_4x4()
    for v in bm.verts:
        v.co = m @ v.co
    if ground:
        mz = min(v.co.z for v in bm.verts)
        for v in bm.verts:
            v.co.z -= mz
    for v in bm.verts:
        if v.co.z < 0:
            v.co.z = 0.0
    vmap = {v: a.bm.verts.new(v.co) for v in bm.verts}
    for f in bm.faces:
        a.bm.faces.new([vmap[v] for v in f.verts])
    bm.free()
    return a._finish(list(vmap.values()), QZ)


# (x, y, w, d, h): ring round the centre; big ones front-centre, small at the ends.
RING = [
    (0.0, -1.9, 3.6, 3.0, 3.4),
    (-2.4, -1.2, 3.1, 2.8, 2.9),
    (2.45, -1.1, 3.1, 2.8, 3.0),
    (-3.3, 0.9, 2.0, 2.2, 2.0),
    (3.35, 1.0, 2.1, 2.2, 2.1),
    (-1.5, 2.3, 3.0, 2.6, 2.7),
    (1.55, 2.4, 3.0, 2.6, 2.8),
]


def rock_ring(a, rng, sx=1.0, sy=1.0, sz=1.0, inward=0.0):
    for x, y, w, d, hgt in RING:
        a.rock((w * sx, d * sy, hgt * sz), (x * sx, y * sy, 0),
               (rng.uniform(-0.1, 0.1) + inward * y / 3, -inward * x / 3, rng.uniform(0, math.tau)),
               mat=RK, subdiv=2, rough=0.15, facets=22, sink=0.36)


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---- hero -------------------------------------------------------------------
    rng = random.Random(31)
    a = fk.Asset("QuartzNode", "R03 Quartz", seed=31, tint_var=0.04)
    rock_ring(a, rng)
    # two wedge fillers between the front boulders and the crystals: raise the band
    # to ~30% and bury the crystal bases
    for x, y, rz in ((-1.05, -0.55, 0.7), (1.1, -0.45, 2.2)):
        a.rock((2.0, 1.8, 2.2), (x, y, 0.9), (0.15, 0, rz), mat=RK, subdiv=2, rough=0.15,
               facets=22, sink=0.2)
    crystal(a, 1.6, 5.4, 3.2, loc=(0, 0.35, 0.3), rot=(0.0, 0, 0), rng=rng,
            skew=(0.15, -0.1), kink=(0.08, -0.06))
    crystal(a, 1.38, 3.4, 2.2, loc=(-1.7, 0.1, 0.6), rot=(0.0, -0.32, 0), rng=rng,
            skew=(-0.2, 0), kink=(-0.08, 0), spin=math.radians(12))
    crystal(a, 1.42, 3.8, 2.3, loc=(1.75, 0.15, 0.6), rot=(0.0, 0.3, 0), rng=rng,
            skew=(0.2, 0), kink=(0.08, 0.04), spin=math.radians(44))
    o = a.finish()
    vfx.add(o, "harvest_hit", (0, -2.2, 3), color=CHIPS)
    vfx.add(o, "harvest_deplete", (0, 0, 0.5))
    out.append(kit.tag(o, "hero", collision="hull", budget=3500,
                       notes="Quartz node: 3 chunky milky crystals centred in a ring of 7 host "
                             "boulders. harvest_hit on the front strike face (quartz chips); "
                             "harvest_deplete at the base centre. Matte quartz: no ore_glint, no light."))

    # ---- parts ------------------------------------------------------------------
    rng = random.Random(7)
    a = fk.Asset("QuartzMainCrystal", "R03 Quartz", seed=7)
    crystal(a, 1.5, 5.4, 3.1, rng=rng, skew=(0.2, 0), kink=(0.1, 0))
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1000,
                       notes="Main crystal of the quartz node, upright, chisel tip."))

    a = fk.Asset("QuartzSideCrystal", "R03 Quartz", seed=8)
    crystal(a, 1.1, 3.6, 1.9, rng=rng, skew=(0.35, 0), kink=(0.08, 0), drop=0.4)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=800,
                       notes="Side crystal with an off-centre angled chisel tip."))

    rng = random.Random(9)
    a = fk.Asset("QuartzBaseRock", "R03 Quartz", seed=9, tint_var=0.04)
    a.rock((3.6, 3.6, 3.4), (-2.2, 0, 0), (0, 0, 0.4), mat=RK, subdiv=2, rough=0.15, facets=22, sink=0.3)
    a.rock((3.3, 3.1, 2.9), (0.7, 0.1, 0), (0, 0, 1.3), mat=RK, subdiv=2, rough=0.15, facets=22, sink=0.3)
    a.rock((1.6, 1.6, 1.6), (3.2, -0.2, 0), (0, 0, 2.1), mat=RK, subdiv=2, rough=0.15, facets=22, sink=0.3)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="Two joined host boulders plus a small third rock."))

    # ---- drops ------------------------------------------------------------------
    rng = random.Random(11)
    a = fk.Asset("QuartzCrystalDrop", "R03 Quartz", seed=11)
    crystal(a, 0.44, 0.5, 0.42, rot=(0.3, math.radians(82), 0.25), spin=0, rng=rng,
            bottom_tip=0.38, skew=(0.08, 0.05), kink=(0.04, 0), ground=True)
    out.append(kit.tag(a.finish(), "drop", collision="none", budget=300,
                       notes="Quartz Crystal drop: chunky shard lying, chisel-pointed both ends."))

    a = fk.Asset("QuartzCrystalDropB", "R03 Quartz", seed=12)
    crystal(a, 0.4, 0.75, 0.6, rot=(0.14, 0.22, 0), spin=math.radians(10), rng=rng,
            skew=(0.12, 0), kink=(0.04, 0.02), drop=0.45, ground=True)
    out.append(kit.tag(a.finish(), "drop", collision="none", budget=300,
                       notes="Second quartz shard drop, standing upright, slanted chisel tip."))

    # ---- depleted ---------------------------------------------------------------
    rng = random.Random(31)
    a = fk.Asset("QuartzDepleted", "R03 Quartz", seed=31, tint_var=0.04)
    rock_ring(a, rng, sx=0.95, sy=0.78, sz=0.72, inward=-0.12)
    o = a.finish()
    vfx.add(o, "harvest_deplete", (0, 0, 0.5), scale=0.35)
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="Depleted (Base): the hero's boulder ring left after the crystals are "
                             "mined, hollow centre; harvest_deplete (small) at the base centre."))
    return out
