"""R04 row 3: Starstone resource node (hero, 4 parts, 2 drops, depleted).

Two broad chiselled grey-violet slabs (convex hulls of hand-placed points) lean
together into a cleft; a long cyan hex crystal is wedged inside it, framed by
grey on both sides and behind. Low angular rubble around the base.
"""
import math
import random

import bmesh
from mathutils import Euler, Vector

SUBJECT = "Starstone"
ROW = 3
PALETTE = {
    "r04_star_stone": ("#6F6B72", 0.9, 0, 0),
    "r04_starlight": ("#22C4E6", 0.25, 0, 0.6),
}
STONE, STAR = "r04_star_stone", "r04_starlight"
GLOW = ["#40E0F8", "#A8F4FF"]
LIGHT = {"color": "#40E0F8", "brightness": 1.0, "range": 12, "flicker": False}
HIT_COLOR = ["#22C4E6", "#6F6B72"]
DEPLETE_COLOR = ["#6F6B72", "#8A8690"]

# Hero slab outlines (world studs, front = -Y). Each is a convex hull.
LEFT_SLAB = [
    # base
    (-4.3, -1.6, 0), (-1.8, -2.3, 0), (-0.2, -1.3, 0), (-0.1, 1.0, 0), (-2.2, 1.9, 0), (-4.5, 0.4, 0),
    # chest; proud points on the front give big facet ridges
    (-4.2, -1.3, 2.8), (-2.2, -2.3, 1.8), (-0.2, -1.7, 3.2), (-0.2, 1.2, 3.6), (-3.9, 1.4, 3.2),
    (-2.0, -1.8, 4.8),
    # shoulders narrowing to a sharp peak
    (-3.6, -0.8, 5.4), (-0.5, -1.1, 6.0), (-0.6, 1.1, 6.4), (-3.3, 1.1, 5.6),
    (-2.6, -0.4, 7.3), (-1.2, 0.5, 7.7),
    (-2.0, 0.1, 9.0),   # peak up-left
]
RIGHT_SLAB = [
    (-0.4, 0.9, 0), (2.4, -1.1, 0), (3.9, -1.3, 0), (4.4, 1.4, 0), (2.6, 3.2, 0), (0.2, 2.9, 0),
    (2.6, -1.0, 3.2), (4.2, -0.9, 2.6), (4.3, 1.8, 3.0), (-0.2, 2.6, 4.2), (-0.3, 1.0, 4.0),
    (3.3, -0.5, 1.6), (3.0, 2.8, 2.0),
    # right shoulder falls away to the right
    (2.6, -0.6, 5.0), (3.6, 0.4, 4.4), (3.4, 2.2, 4.6), (0.0, 2.2, 6.4), (0.0, 0.8, 6.2),
    (2.2, 0.6, 6.3), (1.4, 2.0, 6.6),
    (1.0, 1.4, 7.6),    # peak
]
STUMP = [
    (-1.6, -1.0, 0), (0.4, -1.3, 0), (1.6, -0.2, 0), (1.2, 1.1, 0), (-0.6, 1.3, 0), (-1.8, 0.4, 0),
    (-1.3, -0.8, 1.8), (0.6, -1.0, 2.4), (1.2, 0.3, 2.0), (-0.4, 1.0, 2.2),
    (-0.6, -0.3, 3.0), (0.5, 0.2, 2.8),
]


def _xf(verts, loc=(0, 0, 0), rot=(0, 0, 0)):
    m = Euler(rot).to_matrix()
    for v in verts:
        v.co = m @ v.co + Vector(loc)


def hull(a, pts, mat=STONE, loc=(0, 0, 0), rot=(0, 0, 0), lift=False):
    """Flat-faceted convex hull of the given points, outward normals."""
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    res = bmesh.ops.convex_hull(bm, input=vs)
    dead = list({g for g in res["geom_interior"] + res["geom_unused"] if isinstance(g, bmesh.types.BMVert)})
    if dead:
        bmesh.ops.delete(bm, geom=dead, context="VERTS")
    faces = [g for g in res["geom"] if isinstance(g, bmesh.types.BMFace) and g.is_valid]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    verts = list({v for f in faces for v in f.verts})
    _xf(verts, loc, rot)
    if lift:
        mz = min(v.co.z for v in verts)
        for v in verts:
            v.co.z -= mz
    for v in verts:
        if v.co.z < 0:
            v.co.z = 0.0
    a._finish(verts, mat)
    return verts


def fit(pts, size):
    """Recentre a point set on its base centre and scale it to (x, y, z) size."""
    xs, ys, zs = zip(*pts)
    cx, cy, z0 = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)
    kx, ky, kz = size[0] / (max(xs) - min(xs)), size[1] / (max(ys) - min(ys)), size[2] / (max(zs) - z0)
    return [((x - cx) * kx, (y - cy) * ky, (z - z0) * kz) for x, y, z in pts]


def rock_pts(sx, sy, sz, seed, lean=(0.0, 0.0)):
    """Low angular rock: 6 base, 4 mid, 2 top points; top sheared by lean (tilt)."""
    rng = random.Random(seed)
    pts = []
    a0 = rng.uniform(0, 6.28)
    for i in range(6):
        ang = a0 + i * 2 * math.pi / 6 + rng.uniform(-0.3, 0.3)
        r = 0.5 * rng.uniform(0.8, 1.0)
        pts.append((math.cos(ang) * sx * r, math.sin(ang) * sy * r, 0.0))
    for i in range(4):
        ang = a0 + 0.5 + i * 2 * math.pi / 4 + rng.uniform(-0.35, 0.35)
        r = 0.46 * rng.uniform(0.75, 1.0)
        z = sz * rng.uniform(0.35, 0.6)
        pts.append((math.cos(ang) * sx * r + lean[0] * z, math.sin(ang) * sy * r + lean[1] * z, z))
    for i in range(2):
        ang = a0 + rng.uniform(0, 6.28)
        r = rng.uniform(0.12, 0.24)
        z = sz * rng.uniform(0.85, 1.0)
        pts.append((math.cos(ang) * sx * r + lean[0] * z, math.sin(ang) * sy * r + lean[1] * z, z))
    return pts


def rocks(a, specs, seed=0):
    for i, (x, y, sx, sy, sz, rz) in enumerate(specs):
        lean = (0.25 * math.sin(i * 2.1 + seed), 0.25 * math.cos(i * 1.7 + seed))
        hull(a, rock_pts(sx, sy, sz, seed * 31 + i, lean), loc=(x, y, 0), rot=(0, 0, rz))


def gem(a, length, rx, ry, sides=6, tip_top=1.5, tip_bot=1.0, loc=(0, 0, 0), rot=(0, 0, 0),
        mat=STAR, seed=0, skew=0.0):
    """Long faceted crystal prism, pointed both ends; base tip at local z=0."""
    rng = random.Random(seed)
    z0, z1 = tip_bot, length - tip_top
    pts = [(0.0, 0.0, 0.0), (skew * 1.3, 0.0, length)]
    for i in range(sides):
        ang = 2 * math.pi * i / sides + 0.3
        k = rng.uniform(0.92, 1.06)
        x, y = math.cos(ang) * rx * k, math.sin(ang) * ry * k
        pts.append((x * 0.95, y * 0.95, z0 + rng.uniform(-0.08, 0.08)))
        pts.append((x + skew, y, z1 + rng.uniform(-0.12, 0.12)))
    return hull(a, pts, mat=mat, loc=loc, rot=rot)


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---------------- HERO ----------------
    a = fk.Asset("Starstone", "R04 Starstone")
    hull(a, LEFT_SLAB)
    hull(a, RIGHT_SLAB)
    # crystal wedged in the cleft, tilted ~10 deg toward the viewer
    gem(a, 5.9, 1.6, 1.2, sides=6, tip_top=1.8, tip_bot=1.3, loc=(0.9, -0.15, 0.7),
        rot=(0.17, 0.08, 0.5), seed=11)
    rocks(a, [
        (-0.6, -2.7, 3.5, 2.4, 1.8, 0.4),   # largest, front
        (2.3, -2.5, 3.0, 2.2, 1.6, -0.5),
        (-3.1, -2.2, 2.6, 2.0, 1.4, 0.9),
        (3.8, -1.2, 1.9, 1.6, 1.2, 0.2),
        (-3.9, -0.3, 1.6, 1.4, 1.0, 1.3),
        (0.9, -1.6, 1.3, 1.1, 0.8, 0.7),
        (-3.0, 2.4, 1.4, 1.2, 0.9, 0.1),
        (3.3, 2.8, 1.5, 1.2, 1.0, 0.6),
        (4.2, 0.4, 1.2, 1.0, 0.7, 1.1),     # small rock on the right
    ], seed=1)
    o = a.finish()
    vfx.add(o, "heat_glow", (0.6, -0.4, 3.4), scale=1.2, color=GLOW, light=LIGHT)
    vfx.add(o, "dust", (0.6, -0.6, 3.6), scale=0.8, color=GLOW)
    vfx.add(o, "ore_glint", (0.5, -1.3, 3.6), scale=1.0)
    vfx.add(o, "harvest_hit", (0, -3.5, 3), color=HIT_COLOR)
    vfx.add(o, "harvest_deplete", (0, 0, 0.8), color=DEPLETE_COLOR)
    out.append(kit.tag(o, "hero", collision="hull", budget=4000, notes=(
        "Starstone node: two broad leaning grey-violet slabs with an emissive cyan hex crystal wedged in the "
        "cleft. heat_glow (cyan PointLight) + dust motes = soft starlight halo at the crystal; ore_glint on the "
        "glossy crystal front; harvest_hit on the front strike face (cyan/grey chips); harvest_deplete at "
        "base centre.")))

    # ---------------- PARTS ----------------
    a = fk.Asset("StarstoneStoneShell", "R04 StarstoneStoneShell")
    hull(a, fit(LEFT_SLAB, (3.6, 2.8, 5.8)), rot=(0.1, 0.44, 0.25), lift=True)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=1500,
                       notes="Stone Shell: the hero's left slab, tilted ~25 deg."))

    a = fk.Asset("StarstoneStoneShellB", "R04 StarstoneStoneShellB")
    hull(a, fit(RIGHT_SLAB, (3.0, 2.5, 4.5)), rot=(0.05, -0.2, 0.5), lift=True)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=1500,
                       notes="Stone Shell B: the hero's right-hand slab."))

    a = fk.Asset("StarstoneStarlightCore", "R04 StarstoneStarlightCore")
    gem(a, 5.5, 1.25, 1.1, sides=6, tip_top=1.7, tip_bot=1.3, rot=(0.0, 0.12, 0.3), seed=31)
    o = a.finish()
    vfx.add(o, "heat_glow", (0, 0, 2.8), scale=0.8, color=GLOW)
    vfx.add(o, "ore_glint", (0, -1.1, 3.0), scale=0.8)
    out.append(kit.tag(o, "part", collision="hull", budget=1500,
                       notes="Starlight Core: emissive long hex crystal; heat_glow halo and ore_glint."))

    a = fk.Asset("StarstoneBaseRock", "R04 StarstoneBaseRock")
    rocks(a, [
        (-1.9, -0.2, 2.4, 2.0, 1.6, 0.4),
        (0.4, 0.4, 2.2, 1.8, 1.8, -0.6),
        (2.3, -0.3, 1.5, 1.4, 1.0, 0.9),
        (-0.6, -0.9, 1.3, 1.1, 0.8, 1.2),
        (1.4, 1.0, 1.1, 1.0, 0.7, 0.3),
    ], seed=2)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=1500,
                       notes="Base Rock: low cluster of angular grey rocks merged into one mesh."))

    # ---------------- DROPS ----------------
    a = fk.Asset("StarlightShard", "R04 StarlightShard")
    gem(a, 1.8, 0.5, 0.4, sides=6, tip_top=0.6, tip_bot=0.35, rot=(0.0, 0.25, 0.4), seed=41)
    o = a.finish()
    vfx.add(o, "ore_glint", (0, -0.4, 1.0), scale=0.5)
    out.append(kit.tag(o, "drop", collision="none", budget=300,
                       notes="Starlight Shard drop: pointed emissive cyan crystal; small ore_glint."))

    a = fk.Asset("StarlightShardB", "R04 StarlightShardB")
    gem(a, 1.5, 0.66, 0.5, sides=5, tip_top=0.5, tip_bot=0.3, rot=(0.2, -0.55, 0.9), seed=45,
        skew=0.15)
    o = a.finish()
    vfx.add(o, "ore_glint", (0, -0.5, 0.7), scale=0.5)
    out.append(kit.tag(o, "drop", collision="none", budget=300,
                       notes="Starlight Shard drop (chunky angled variant); small ore_glint."))

    # ---------------- DEPLETED ----------------
    a = fk.Asset("StarstoneDepleted", "R04 StarstoneDepleted")
    hull(a, STUMP, loc=(-0.4, 1.6, 0), rot=(0, 0, 0.4))
    rocks(a, [
        (-2.6, -1.0, 2.6, 2.1, 1.6, 0.4),
        (0.2, -1.6, 2.6, 2.0, 1.4, -0.5),
        (2.7, -0.8, 2.3, 2.0, 1.5, 0.8),
        (1.8, 1.4, 1.8, 1.6, 1.2, 0.2),
        (-2.6, 1.5, 1.6, 1.4, 1.0, 1.2),
        (3.4, 1.6, 1.2, 1.1, 0.8, 0.6),
        (-3.6, 0.2, 1.2, 1.1, 0.7, 0.3),
        (-1.0, 0.2, 1.4, 1.2, 0.9, 0.9),
    ], seed=3)
    o = a.finish()
    vfx.add(o, "harvest_deplete", (0, 0, 0.8), color=DEPLETE_COLOR)
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="Depleted (Base): low angular grey rubble pile with a stubby broken slab stump at "
                             "the back, no crystal; harvest_deplete at base centre."))
    return out
