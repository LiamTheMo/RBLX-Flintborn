"""R04 row 1: Iron Meteor resource node (hero, 3 parts, 2 drops, depleted)."""
import math
import random

from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

SUBJECT = "IronMeteor"
ROW = 1
PALETTE = {
    "r04_meteor_rock": ("#4A4A54", 0.9, 0, 0),
    "r04_impact_rock": ("#7D7570", 0.95, 0, 0),
    "r04_lava_crack": ("#FF7A12", 0.5, 0, 1.0),
}
ROCK, RUBBLE, LAVA = "r04_meteor_rock", "r04_impact_rock", "r04_lava_crack"
HIT_COLOR = ["#4A4A54", "#7D7570"]
GLOW = ["#FF8A1A", "#FFC040"]
LIGHT = {"color": "#FF9A1E", "brightness": 1.2, "range": 10, "flicker": True}


def _surface(bvh, p, axis_z):
    """Project an approximate point onto the shell: cast from outside toward the
    vertical axis point (0, 0, axis_z)."""
    p = Vector(p)
    c = Vector((0.0, 0.0, axis_z))
    d = (p - c).normalized()
    hit = bvh.ray_cast(c + d * 12.0, -d)
    if hit[0] is None:
        return p, d
    n = hit[1]
    if n.dot(d) < 0:
        n = -n
    return hit[0], n


def _crack(a, bvh, pts, width=0.2, depth=0.16, lift=0.02, axis=None):
    """Zig-zag emissive seam: one thin box per segment lying on the shell."""
    surf = []
    for p in pts:
        az = axis if axis is not None else max(0.6, p[2] * 0.7)
        surf.append(_surface(bvh, p, az))
    for (p1, n1), (p2, n2) in zip(surf, surf[1:]):
        x = (p2 - p1)
        length = x.length + 0.18
        x.normalize()
        n = (n1 + n2).normalized()
        z = (n - x * n.dot(x)).normalized()
        y = z.cross(x)
        rot = Matrix((x, y, z)).transposed().to_euler("XYZ")
        mid = (p1 + p2) * 0.5 + z * lift
        a.box((length, width, depth), loc=tuple(mid), rot=tuple(rot), mat=LAVA)


def _rock(a, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=ROCK, subdiv=2, rough=0.12,
          facets=14, sink=0.15):
    """Like Asset.rock() but with a smaller random face Tint (+/-3%), so many-faced
    shells stay inside the runner's 1.25x Tint limit."""
    r = (size[0] / 2, size[1] / 2, size[2] / 2)
    loc = (loc[0], loc[1], loc[2] + r[2] * (1 - sink))
    verts = a.ico(r, loc, rot, mat=mat, subdiv=subdiv, jitter=rough, facets=facets,
                  face_tint_var=0.03)
    floor = loc[2] - r[2] * (1 - sink)
    for v in verts:
        if v.co.z < floor:
            v.co.z = floor
    return verts


def _bvh(a):
    a.bm.normal_update()
    return BVHTree.FromBMesh(a.bm)


def _ring(a, rng, specs, mat=RUBBLE, subdiv=2):
    for (x, y, sx, sy, sz, rz) in specs:
        j = rng.uniform(0.92, 1.08)
        _rock(a, (sx * j, sy * j, sz), loc=(x, y, 0), rot=(0, 0, rz), mat=mat, subdiv=subdiv,
               rough=0.14, facets=12, sink=0.12)


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    rng = random.Random(4041)
    out = []

    # ---------------- HERO ----------------
    a = fk.Asset("IronMeteor", "R04 IronMeteor")
    _rock(a, (7.2, 6.6, 6.8), loc=(0, 0.3, 0.2), rot=(0.05, -0.04, 0.35), mat=ROCK,
           subdiv=2, rough=0.05, facets=21, sink=0.05)
    _rock(a, (3.8, 3.4, 4.4), loc=(-2.5, 0.0, 0), rot=(0.1, 0.25, 0.5), mat=ROCK,
           subdiv=1, rough=0.07, facets=8, sink=0.05)
    _rock(a, (3.4, 3.2, 4.0), loc=(2.4, 0.3, 0), rot=(-0.1, -0.2, -0.4), mat=ROCK,
           subdiv=1, rough=0.07, facets=8, sink=0.05)
    _rock(a, (2.6, 2.4, 2.8), loc=(1.3, 1.9, 0), rot=(0.0, 0.15, 0.9), mat=ROCK,
           subdiv=1, rough=0.07, facets=8, sink=0.05)
    bvh = _bvh(a)
    # rubble rim hugging the base: front largest, uneven, low and flat
    _ring(a, rng, [
        (-1.4, -3.3, 2.5, 1.9, 1.3, 0.3),
        (1.6, -3.2, 2.3, 1.8, 1.2, -0.4),
        (-3.4, -2.1, 1.9, 1.6, 1.0, 0.9),
        (3.6, -1.8, 1.8, 1.5, 0.9, -0.7),
        (0.2, -3.7, 1.2, 1.0, 0.6, 1.2),
        (-3.8, 0.6, 1.6, 1.3, 0.8, 0.2),
        (3.8, 0.9, 1.4, 1.2, 0.7, 0.6),
        (-2.6, 3.0, 1.4, 1.2, 0.7, -0.5),
        (2.9, 3.0, 1.3, 1.1, 0.6, 0.8),
        (0.2, 3.7, 1.5, 1.2, 0.7, 0.1),
        (-4.3, -0.9, 0.9, 0.8, 0.5, 0.4),
    ])
    # glowing zig-zag seams on the shell only (asymmetric)
    big = [(-0.6, -2.7, 6.3), (-1.4, -3.0, 5.4), (-1.0, -3.2, 4.6), (-2.0, -3.3, 3.6),
           (-1.7, -3.4, 2.7), (-2.8, -3.2, 1.5)]
    right = [(1.6, -2.9, 5.0), (2.3, -2.8, 4.2), (1.8, -2.9, 3.5), (2.6, -2.7, 2.6)]
    left_side = [(-3.4, 0.4, 3.6), (-3.7, 0.9, 2.9), (-3.4, 1.3, 2.2)]
    right_side = [(3.3, 1.1, 4.4), (3.6, 0.6, 3.6), (3.4, 1.0, 2.8)]
    for pts in (big, right, left_side, right_side):
        _crack(a, bvh, pts)
    o = a.finish()
    o["kit_two_tone_ok"] = ("charcoal meteor shell (r04_meteor_rock) vs warm grey-tan impact "
                            "rubble (r04_impact_rock): two different rocks, as on the reference")
    vfx.add(o, "heat_glow", (-1.6, -3.4, 3.8), scale=0.8, color=GLOW, light=LIGHT)
    vfx.add(o, "heat_glow", (2.1, -3.0, 3.8), scale=0.8, color=GLOW, light=LIGHT)
    vfx.add(o, "heat_glow", (-3.6, 0.9, 2.9), scale=0.8, color=GLOW)
    vfx.add(o, "heat_glow", (3.5, 0.8, 3.6), scale=0.8, color=GLOW)
    vfx.add(o, "embers", (-0.8, -2.8, 6.1), scale=0.6)
    vfx.add(o, "harvest_hit", (0, -4, 3.5), color=HIT_COLOR)
    vfx.add(o, "harvest_deplete", (0, 0, 0.8))
    out.append(kit.tag(o, "hero", collision="hull", budget=3500, notes=(
        "Iron meteor node. heat_glow x4 mark the emissive crack seams (front two carry an "
        "orange PointLight), embers rise from the top of the big left-front crack, "
        "harvest_hit on the front strike face, harvest_deplete at the base centre. "
        "No ore_glint (matte). PARTS labels (Rock Shell, Metal Core, Impact Rim) are real part assets.")))

    # ---------------- PARTS ----------------
    a = fk.Asset("IronMeteorRockShell", "R04 IronMeteorRockShell")
    _rock(a, (5.0, 3.5, 2.5), loc=(0, 0, 0), rot=(0.08, -0.06, 0.25), mat=ROCK,
           subdiv=2, rough=0.04, facets=12, sink=0.08)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=1500,
                       notes="Rock Shell part: elongated angular charcoal shell slab, no glow."))

    a = fk.Asset("IronMeteorMetalCore", "R04 IronMeteorMetalCore")
    _rock(a, (4.0, 4.0, 4.1), loc=(0, 0, 0), rot=(0.1, 0.12, 0.6), mat=ROCK,
           subdiv=2, rough=0.05, facets=17, sink=0.06)
    bvh = _bvh(a)
    _crack(a, bvh, [(-0.6, -1.9, 3.2), (-0.1, -2.0, 2.4), (-0.5, -2.0, 1.5)], axis=2.0)
    o = a.finish()
    vfx.add(o, "heat_glow", (-0.3, -2.0, 2.4), scale=0.8, color=GLOW)
    out.append(kit.tag(o, "part", collision="hull", budget=1500,
                       notes="Metal Core part: chunky faceted core with one short emissive seam (heat_glow)."))

    a = fk.Asset("IronMeteorImpactRim", "R04 IronMeteorImpactRim")
    _ring(a, rng, [
        (-2.6, 0.2, 1.8, 1.6, 0.9, 0.4),
        (-0.9, -0.4, 2.6, 2.0, 1.4, -0.3),
        (1.1, 0.3, 2.2, 1.8, 1.2, 0.8),
        (2.8, -0.3, 1.6, 1.4, 0.8, -0.6),
        (0.1, 1.0, 1.2, 1.0, 0.6, 1.1),
        (-1.8, 1.0, 1.0, 0.9, 0.5, 0.2),
    ])
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=1500,
                       notes="Impact Rim part: merged cluster of flat grey-tan rubble rocks."))

    # ---------------- DROPS ----------------
    a = fk.Asset("MeteorIronChunk", "R04 MeteorIronChunk")
    _rock(a, (1.4, 1.2, 1.0), loc=(0, 0, 0), rot=(0.1, 0.05, 0.4), mat=ROCK,
           subdiv=2, rough=0.1, facets=5, sink=0.08)
    bvh = _bvh(a)
    _crack(a, bvh, [(-0.25, -0.5, 0.85), (0.05, -0.6, 0.55), (-0.1, -0.6, 0.2)],
           width=0.12, depth=0.08, lift=0.01, axis=0.5)
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="none", budget=300,
                       notes="Meteor Iron Chunk drop: charcoal chunk with one emissive front seam."))

    a = fk.Asset("MeteorIronChunkB", "R04 MeteorIronChunkB")
    _rock(a, (1.0, 1.0, 1.4), loc=(0, 0, 0), rot=(0.05, -0.1, 0.7), mat=ROCK,
           subdiv=2, rough=0.1, facets=5, sink=0.06)
    bvh = _bvh(a)
    _crack(a, bvh, [(0.05, -0.4, 1.15), (-0.08, -0.45, 0.75), (0.06, -0.45, 0.3)],
           width=0.12, depth=0.08, lift=0.01, axis=0.7)
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="none", budget=300,
                       notes="Meteor Iron Chunk drop (tall variant) with a vertical emissive seam."))

    # ---------------- DEPLETED ----------------
    a = fk.Asset("IronMeteorDepleted", "R04 IronMeteorDepleted")
    specs = []
    n = 9
    for i in range(n):
        t = 2 * math.pi * i / n + 0.2
        front = max(0.0, -math.sin(t))
        sx = 2.0 + 0.6 * front + rng.uniform(-0.3, 0.3)
        sz = 0.9 + 0.6 * front + rng.uniform(-0.15, 0.15)
        specs.append((3.4 * math.cos(t), 2.8 * math.sin(t), sx, sx * 0.8, min(sz, 1.8),
                      t + rng.uniform(-0.3, 0.3)))
    _ring(a, rng, specs)
    o = a.finish()
    vfx.add(o, "harvest_deplete", (0, 0, 0.3))
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="Depleted (Base): low ring of impact rubble with a hollow centre; harvest_deplete at base centre."))
    return out
