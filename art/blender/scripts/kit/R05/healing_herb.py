"""R05 row 2: HealingHerb - low rosette of broad pointed leaves, two stalks with cream buds."""
import math

import bmesh
from mathutils import Euler, Vector

SUBJECT = "HealingHerb"
ROW = 2
HERO_AZIMUTH = -22

PALETTE = {
    "r05_herb_leaf": ("#4A7846", 0.85, 0, 0),  # HealingHerb broad leaves (cooler blue-green; tuned darker/cooler so the render matches the ref)
    "r05_herb_stem": ("#6FAE2E", 0.85, 0, 0),  # HealingHerb flower stalks (bright yellow-green)
    "r05_bud": ("#F0E2A6", 0.7, 0, 0),  # HealingHerb cream flower buds
    "r05_root": ("#6E5442", 0.95, 0, 0),  # HealingHerb root plug and soil tuft at base
}

LEAF, STEM, BUD, ROOT = "r05_herb_leaf", "r05_herb_stem", "r05_bud", "r05_root"

# leaf/petal-coloured chip burst (no grey stone dust for a plant)
LEAF_CHIPS = {"name": "Leaves", "texture": "rock_chip", "color": ["#4A7846", "#F0E2A6"], "size": [0.45, 0.25],
              "transparency": [0, 0, 1], "lifetime": [0.5, 0.9], "rate": 0, "burst": 8, "speed": [6, 10],
              "spread": 60, "light_emission": 0.0, "acceleration": [0, -30, 0], "rotation": [0, 360],
              "rot_speed": [-360, 360]}

# (t along the blade, half-width factor, ridge factor)
PROFILE = [(0.06, 0.6, 0.6), (0.2, 0.92, 0.9), (0.4, 1.0, 1.0), (0.6, 0.95, 0.95), (0.78, 0.7, 0.75), (0.92, 0.35, 0.4)]
PROFILE_HERO = [(0.1, 0.7, 0.7), (0.3, 1.0, 1.0), (0.55, 1.0, 1.0), (0.76, 0.8, 0.85), (0.9, 0.48, 0.5)]
LANCE = [(0.16, 0.55, 0.7), (0.4, 1.0, 1.0), (0.64, 0.78, 0.85), (0.86, 0.32, 0.45)]
PROFILE_SMALL = [(0.2, 0.7, 0.8), (0.5, 1.0, 1.0), (0.78, 0.55, 0.6)]


def leaf(a, length, width, thick, base, yaw, pitch, tip_z=None, droop=0.0, arch=0.0,
         roll=0.0, profile=PROFILE, mat=LEAF):
    """Closed faceted lance blade along local +X with a raised midrib ridge.
    `tip_z`: wanted world height of the tip above the base's ground (sets droop)."""
    bm = a.bm
    if tip_z is not None:
        sp, cp = math.sin(pitch), math.cos(pitch)
        droop = max(0.0, (length * sp - (tip_z - base[2])) / (cp * length))
    hw = width / 2

    def zc(t):
        return -droop * length * t ** 3 + arch * math.sin(math.pi * t)

    root = bm.verts.new((0, 0, 0))
    tip = bm.verts.new((length, 0, zc(1.0)))
    rings = []
    for t, wf, rf in profile:
        x, z = t * length, zc(t)
        w = hw * wf
        rings.append([
            bm.verts.new((x, w, z)),
            bm.verts.new((x, 0, z + thick * rf)),
            bm.verts.new((x, -w, z)),
            bm.verts.new((x, 0, z - thick * 0.35 * rf)),
        ])
    faces = []
    r0 = rings[0]
    for k in range(4):
        faces.append(bm.faces.new((root, r0[(k + 1) % 4], r0[k])))
    for ra, rb in zip(rings, rings[1:]):
        for k in range(4):
            faces.append(bm.faces.new((ra[k], ra[(k + 1) % 4], rb[(k + 1) % 4], rb[k])))
    rl = rings[-1]
    for k in range(4):
        faces.append(bm.faces.new((tip, rl[k], rl[(k + 1) % 4])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    verts = [root, tip] + [v for r in rings for v in r]
    a.transform(verts, base, (roll, -pitch, yaw))
    return a._finish(verts, mat)


def bud(a, loc, rx=0.5, rz=0.56, subdiv=2, cap=True):
    """Cream faceted teardrop bud; `loc` is its bottom point."""
    v = a.ico((rx, rx, rz), (0, 0, 0), mat=BUD, subdiv=subdiv, jitter=0.04)
    for p in v:
        if p.co.z > 0:
            p.co.z *= 1.15
        else:
            s = 1.0 + 0.3 * p.co.z / rz
            p.co.x *= s
            p.co.y *= s
    a.transform(v, (loc[0], loc[1], loc[2] + rz * 0.92))
    if cap:
        a.cyl(rx * 0.25, rx * 0.6, rz * 0.4, sides=6, loc=loc, mat=STEM)
    return v


def stalk(a, base, h, lean, r=0.15, sides=6):
    """Slim stalk; returns its top point."""
    a.cyl(r, r * 0.8, h, sides=sides, loc=base, rot=lean, mat=STEM)
    top = Vector(base) + Euler(lean, "XYZ").to_matrix() @ Vector((0, 0, h))
    return tuple(top)


def clamp_floor(a):
    for v in a.bm.verts:
        if v.co.z < 0:
            v.co.z = 0.0


def rosette(a, n, length, width, thick, pitch, tip_z, z0, r0, yaw0=0.0, jitter=0.12, seed_scale=1.0,
            arch=0.0, profile=PROFILE):
    rng = a.rng
    for i in range(n):
        yaw = yaw0 + i * 2 * math.pi / n + rng.uniform(-jitter, jitter)
        L = length * rng.uniform(0.9, 1.08) * seed_scale
        base = (r0 * math.cos(yaw), r0 * math.sin(yaw), z0)
        leaf(a, L, width * rng.uniform(0.92, 1.08), thick, base, yaw,
             pitch + rng.uniform(-0.08, 0.08), tip_z=tip_z + rng.uniform(0, 0.12),
             roll=rng.uniform(-0.15, 0.15), arch=arch, profile=profile)


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # --- hero ---------------------------------------------------------------
    a = fk.Asset("HealingHerb", "R05 HealingHerb")
    a.rock((1.4, 1.3, 0.6), (0, 0, 0), mat=ROOT, subdiv=1, rough=0.1, facets=10)
    # outer ring: broad blades that rise steeply, arch, then droop to a point
    rosette(a, 7, 2.4, 2.15, 0.65, math.radians(52), 1.0, 0.35, 0.3, yaw0=math.radians(-64),
            arch=0.55, profile=PROFILE_HERO)
    # inner ring: upright blades; the front one is a tall near-upright diamond
    for yaw, L, tz in ((-90, 2.2, 2.1), (15, 2.4, 2.0), (165, 2.4, 2.0), (95, 2.3, 2.1)):
        leaf(a, L, 1.75, 0.55, (0.15 * math.cos(math.radians(yaw)), 0.15 * math.sin(math.radians(yaw)), 0.4),
             math.radians(yaw), math.radians(62), tip_z=tz, arch=0.12, profile=PROFILE_HERO)
    t1 = stalk(a, (-0.2, 0.15, 0.3), 2.15, (0.06, -0.12, 0))
    bud(a, t1)
    t2 = stalk(a, (0.25, -0.15, 0.3), 1.65, (-0.1, 0.2, 0))
    bud(a, t2, rx=0.47, rz=0.52)
    clamp_floor(a)
    o = a.finish()
    vfx.add(o, "harvest_hit", (0, -1.5, 2.5), scale=0.8, emitters=[dict(LEAF_CHIPS, burst=8)])
    vfx.add(o, "harvest_deplete", (0, 0, 0.3), emitters=[dict(LEAF_CHIPS, burst=16, size=[0.6, 0.3], shape=[3.0, 1.0, 3.0])])
    out.append(kit.tag(o, "hero", collision="none", budget=3000,
                       notes="Healing herb rosette. harvest_hit: leaf/bud-coloured burst on the "
                             "front of the buds; harvest_deplete: burst at the base when clipped."))

    # --- parts --------------------------------------------------------------
    a = fk.Asset("HealingHerbBud", "R05 HealingHerb")
    t = stalk(a, (0, 0, 0), 1.0, (0, 0, 0), r=0.13)
    bud(a, t, rx=0.52, rz=0.58)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="Flower Bud"))

    a = fk.Asset("HealingHerbLeaf", "R05 HealingHerb")
    # crisp lance: sharp base and tip points, raised midrib keel, tip curling up
    leaf(a, 3.0, 1.6, 0.75, (-1.5, 0, 0.12), 0.0, math.radians(4), droop=-0.06, arch=0.04,
         roll=0.45, profile=LANCE)
    clamp_floor(a)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="Leaf"))

    a = fk.Asset("HealingHerbRootPlug", "R05 HealingHerb")
    a.rock((1.6, 1.4, 1.0), (0, 0, 0), mat=ROOT, subdiv=2, rough=0.12, facets=14)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500, notes="Root Plug"))

    # --- drop ---------------------------------------------------------------
    a = fk.Asset("HealingHerbSprig", "R05 HealingHerb")
    for sx, lean in ((-0.55, (0.0, -0.18, 0)), (0.55, (0.0, 0.2, 0))):
        top = stalk(a, (sx, 0, 0), 0.95, lean, r=0.07, sides=5)
        bud(a, top, rx=0.2, rz=0.26, subdiv=1, cap=False)
        for yaw in (math.radians(20), math.radians(200)):
            leaf(a, 0.85, 0.42, 0.1, (sx, 0, 0.08), yaw + (0.3 if sx > 0 else 0),
                 math.radians(55), tip_z=0.75, profile=PROFILE_SMALL)
    clamp_floor(a)
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="none", budget=300, notes="Herb Sprig (x2)"))

    # --- depleted -----------------------------------------------------------
    a = fk.Asset("HealingHerbDepleted", "R05 HealingHerb")
    a.rock((1.2, 1.1, 0.45), (0, 0, 0), mat=ROOT, subdiv=1, rough=0.1, facets=10)
    a.cyl(0.32, 0.36, 0.7, sides=7, loc=(0, 0, 0), mat=ROOT)
    rosette(a, 7, 2.1, 1.8, 0.4, math.radians(46), 0.7, 0.3, 0.3, yaw0=math.radians(-70),
            arch=0.4, profile=PROFILE_HERO)
    clamp_floor(a)
    o = a.finish()
    out.append(kit.tag(o, "depleted", collision="none", budget=2000,
                       notes="Depleted (Clipped): leaf skirt around a cut stump, no buds."))
    return out
