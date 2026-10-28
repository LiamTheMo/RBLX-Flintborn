"""R06 row 3: ResinNode resource (leaning broken limb with amber resin lumps)."""
import math
from mathutils import Vector

SUBJECT = "ResinNode"
ROW = 3
HERO_AZIMUTH = -22

PALETTE = {
    "r06_cutwood": ("#E0B27C", 0.85, 0, 0),
    "r06_softbark": ("#8A5B3E", 0.9, 0, 0),
    "r06_dirt": ("#6A5047", 0.95, 0, 0),
    "r06_leaf": ("#3F9A2C", 0.7, 0, 0),
    "r06_resin": ("#F29A1A", 0.25, 0, 0.15),
}

BARK, CUT, DIRT, LEAF, RESIN = "r06_softbark", "r06_cutwood", "r06_dirt", "r06_leaf", "r06_resin"
RESIN_CHIPS = ["#F29A1A", "#C8701A"]
WOOD_CHIPS = ["#8A5B3E", "#E0B27C"]
GLINT = ["#FFF0C0", "#FFB648"]
GLOW = {"color": "#FF9A1A", "brightness": 0.6, "range": 8, "flicker": False, "pulse": True}
GLOW_SMALL = {"color": "#FF9A1A", "brightness": 0.4, "range": 6, "flicker": False, "pulse": True}


def _rot_to(d):
    return Vector(d).to_track_quat("Z", "Y").to_euler()


def log(a, p1, p2, r1, r2, sides=7, cut_end=True, cut_start=False, jitter=0.05, ce_k=0.22):
    """Tapered bark log from p1 to p2 with pale cut faces."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    L = d.length
    ce = min(r2 * ce_k, 0.4)
    rot = _rot_to(d)
    z0 = ce if cut_start else 0.0
    z1 = L - ce if cut_end else L
    rs = r1 + (r2 - r1) * (z0 / L)
    re = r1 + (r2 - r1) * (z1 / L)
    v = a.cyl(rs, re, z1 - z0, sides, loc=(0, 0, z0), mat=BARK, jitter=r1 * jitter)
    a.transform(v, p1, rot)
    if cut_end:
        c = a.cyl(re, r2 * 0.92, ce, sides, loc=(0, 0, z1), mat=CUT)
        a.transform(c, p1, rot)
    if cut_start:
        c = a.cyl(r1 * 0.92, rs, ce, sides, mat=CUT)
        a.transform(c, p1, rot)


def cut_disc(a, centre, normal, r, sides=7, h=0.35):
    """Pale slanted break face: a short cut-wood slab facing `normal`."""
    v = a.cyl(r, r * 0.9, h, sides, loc=(0, 0, -h * 0.5), mat=CUT)
    a.transform(v, centre, _rot_to(normal))


def leaf(a, base, length, width, pitch, yaw):
    """One broad pointed leaf with a centre ridge, base at `base`, tilted out by pitch."""
    v = a.cyl(width * 0.15, width, length * 0.38, 4, mat=LEAF, cap=False)
    v += a.cyl(width, 0.0, length * 0.62, 4, loc=(0, 0, length * 0.38), mat=LEAF, cap=False)
    a.transform(v, base, (pitch, 0, yaw), (1.0, 0.3, 1.0))


def leaf_rosette(a, base, size=1.0, n=6, yaw0=0.0, stem=0.0):
    bx, by, bz = base
    if stem > 0:
        a.cyl(0.1 * size, 0.08 * size, stem, 5, loc=(bx, by, bz), mat=LEAF)
        bz += stem
    for i in range(n):
        yaw = yaw0 + 2 * math.pi * i / n + (0.2 if i % 2 else -0.1)
        pitch = (0.95 if i % 2 else 1.2)
        ln = size * (1.45 if i % 2 else 1.25)
        leaf(a, (bx, by, bz), ln, 0.72 * size, pitch, yaw)
    leaf(a, (bx, by, bz), size * 1.3, 0.62 * size, 0.4, yaw0 + 0.8)


def gem(a, radius, loc, seed_rot=(0.4, 0.7, 0.2), squash=(1.0, 0.92, 0.95)):
    r = (radius * squash[0], radius * squash[1], radius * squash[2])
    return a.ico(r, loc, seed_rot, mat=RESIN, subdiv=1, jitter=0.2, facets=8)


def _offset(a):
    xs = [v.co.x for v in a.bm.verts]
    ys = [v.co.y for v in a.bm.verts]
    zs = [v.co.z for v in a.bm.verts]
    return Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---- hero ---------------------------------------------------------------
    a = fk.Asset("ResinNode", "R06 ResinNode")
    # broad chunky dirt mound with lobes so its rim shows all round
    a.rock((10.0, 8.0, 3.3), loc=(0.3, -0.2, 0), mat=DIRT, subdiv=1, rough=0.2, facets=10, sink=0.1)
    a.rock((5.4, 4.4, 2.7), loc=(-3.2, -2.4, 0), mat=DIRT, subdiv=1, rough=0.2, facets=10, sink=0.1)
    a.rock((4.8, 4.0, 2.4), loc=(3.0, -2.2, 0), mat=DIRT, subdiv=1, rough=0.2, facets=10, sink=0.1)
    a.rock((4.6, 3.8, 2.4), loc=(2.0, 2.2, 0), mat=DIRT, subdiv=1, rough=0.2, facets=10, sink=0.1)
    # flared chunky trunk base
    a.cyl(2.3, 1.85, 1.5, 7, loc=(-0.9, 0.6, 1.5), mat=BARK, jitter=0.35)
    # main leaning trunk: up, right and back (+X, +Y)
    tip = Vector((2.3, 2.6, 8.1))
    log(a, (-0.9, 0.6, 2.0), tip, 1.85, 1.15, sides=7, cut_end=False, jitter=0.2)
    cut_disc(a, tip + Vector((0, 0, -0.05)), (-0.3, -0.6, 1.0), 1.25)
    # ground limb forward-right
    log(a, (-0.4, 0.2, 2.6), (5.6, -3.4, 1.35), 1.35, 1.0, sides=7, jitter=0.16, ce_k=0.36)
    big = (-2.7, -0.8, 3.9)
    small = (3.1, 0.9, 5.9)
    gem(a, 2.4, big, (0.3, 0.5, 0.9))
    gem(a, 1.45, small, (0.8, 0.2, 0.4))
    leaf_rosette(a, (4.0, 3.9, 6.3), 1.9, yaw0=0.3)      # behind trunk tip
    leaf_rosette(a, (0.6, -3.7, 2.0), 1.7, yaw0=1.0)     # base front-centre
    leaf_rosette(a, (4.2, 0.2, 3.6), 1.7, yaw0=2.0)      # right mid
    off = _offset(a)
    o = a.finish()
    o["kit_shading_ok"] = "cut wood ends, resin and leaves are real material changes on the bark"
    vfx.add(o, "harvest_hit", tuple(Vector((-2.4, -2.9, 2.9)) - off), color=RESIN_CHIPS)
    vfx.add(o, "harvest_deplete", (0.0, 0.0, 0.3), color=WOOD_CHIPS)
    vfx.add(o, "ore_glint", tuple(Vector(big) - off), scale=1.0, color=GLINT, light=GLOW)
    vfx.add(o, "ore_glint", tuple(Vector(small) - off), scale=0.7, color=GLINT, light=GLOW_SMALL)
    vfx.add(o, "dust", tuple(Vector((-0.5, -1.5, 3.5)) - off), scale=0.5,
            color=["#FFD07A", "#F29A1A"])
    out.append(kit.tag(o, "hero", collision="hull", budget=4500,
                       notes="Resin node. harvest_hit: resin chips off the big lump's front face; "
                             "harvest_deplete: wood chips at base centre; ore_glint x2: twinkles on the "
                             "glossy resin lumps, each with an orange PointLight; dust: orange "
                             "resin motes round the lumps."))

    # ---- parts --------------------------------------------------------------
    a = fk.Asset("ResinNodeWoodyBase", "R06 ResinNode part")
    a.cyl(2.3, 1.45, 2.0, 7, mat=BARK, jitter=0.35)
    a.cyl(1.45, 1.1, 4.7, 7, loc=(0, 0, 1.9), mat=BARK, jitter=0.18)
    cut_disc(a, (0, 0, 6.6), (-0.15, -0.35, 1.0), 1.12)
    a.cyl(0.55, 0.3, 0.45, 5, loc=(0.45, 0.4, 6.7), mat=BARK, jitter=0.05)  # broken splinter
    o = a.finish()
    o["kit_shading_ok"] = "pale cut top is cut wood, a real material change"
    out.append(kit.tag(o, "part", collision="hull", budget=1500, notes="Tapered broken trunk with cut top."))

    a = fk.Asset("ResinNodeResinLump", "R06 ResinNode part")
    gem(a, 1.5, (0, 0, 1.4), (0.5, 0.3, 0.8))
    o = a.finish()
    vfx.add(o, "ore_glint", (0, 0, 1.4), scale=0.8, color=GLINT, light=GLOW)
    out.append(kit.tag(o, "part", collision="none", budget=1500,
                       notes="Faceted resin lump; ore_glint twinkle with soft orange light."))

    a = fk.Asset("ResinNodeLeafClump", "R06 ResinNode part")
    leaf_rosette(a, (0, 0, 0), 1.4, yaw0=0.2, stem=0.6)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="Pointed leaf rosette on a stem."))

    # ---- drops --------------------------------------------------------------
    a = fk.Asset("ResinNodeRawResin", "R06 ResinNode drop")
    gem(a, 0.75, (0, 0, 0.7), (0.2, 0.9, 0.4), (1.0, 0.85, 0.85))
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="none", budget=300, notes="Raw resin nugget."))

    a = fk.Asset("ResinNodeRawResinSmall", "R06 ResinNode drop")
    gem(a, 0.5, (0, 0, 0.5), (1.1, 0.1, 0.7), (1.0, 0.95, 0.88))
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="none", budget=300, notes="Small raw resin nugget."))

    # ---- depleted -----------------------------------------------------------
    a = fk.Asset("ResinNodeBareBranch", "R06 ResinNode depleted")
    # thick end raised at the left, gentle curve in three segments, forked twig
    log(a, (-3.5, -0.6, 2.3), (-1.2, 0.1, 1.0), 0.95, 0.8, cut_end=False, cut_start=True,
        jitter=0.12, ce_k=0.32)
    log(a, (-1.35, 0.05, 1.0), (1.2, 0.2, 0.72), 0.8, 0.66, cut_end=False, jitter=0.1)
    log(a, (1.0, 0.2, 0.74), (3.6, -0.4, 0.62), 0.66, 0.54, jitter=0.1, ce_k=0.4)
    log(a, (0.2, 0.3, 1.0), (2.9, 1.3, 2.3), 0.45, 0.34, jitter=0.08, ce_k=0.4)
    o = a.finish()
    o["kit_shading_ok"] = "pale cut ends are cut wood, a real material change"
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="Depleted resin node: bare lying branch with a forked twig."))
    return out
