"""R07 row 2: ReedPatch resource node (cattails in a mud mound)."""
import math

from mathutils import Vector, Matrix

SUBJECT = "ReedPatch"
ROW = 2
HERO_AZIMUTH = -22

PALETTE = {
    "r07_soil": ("#7A5636", 0.95, 0, 0),
    "r07_stone": ("#77737A", 0.9, 0, 0),
    "r07_reed_stalk": ("#7B9C2C", 0.8, 0, 0),
    "r07_reed_leaf": ("#3A7A1F", 0.8, 0, 0),
    "r07_cattail": ("#D49A60", 0.85, 0, 0),
}

CHIPS = ["#7B9C2C", "#3A7A1F"]
SOIL_DUST = ["#7A5636", "#5E4229"]


# --------------------------------------------------------------------- helpers

def lathe(a, profile, sides, mat, rot0=0.0):
    """Closed faceted solid of revolution. profile = [(z, r), ...] bottom to top."""
    bm = a.bm
    rings = []
    for z, r in profile:
        ring = []
        for i in range(sides):
            t = rot0 + 2 * math.pi * i / sides
            ring.append(bm.verts.new((r * math.cos(t), r * math.sin(t), z)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(sides):
            j = (i + 1) % sides
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    verts = [v for ring in rings for v in ring]
    return a._finish(verts, mat)


def blade(a, base, az, length, width, lean, curve, mat="r07_reed_leaf", segs=4,
          thick=0.09, twist=0.0, cut=None, roll=0.0):
    """Flat, pointed, diamond-section leaf blade bending outward along azimuth `az`.
    `cut` (0-1) truncates the blade with a flat top (clipped stub)."""
    bm = a.bm
    d = Vector((math.cos(az), math.sin(az), 0))
    w0 = Vector((-math.sin(az), math.cos(az), 0))
    end = 1.0 if cut is None else cut
    n = segs
    pts, tans = [], []
    p = Vector(base)
    ds = length * end / n
    for k in range(n + 1):
        s = end * k / n
        th = lean + curve * s * s
        tan = (d * math.sin(th) + Vector((0, 0, 1)) * math.cos(th)).normalized()
        pts.append(p.copy())
        tans.append(tan)
        p = p + tan * ds
    rings = []
    tip = None
    for k, (c, tan) in enumerate(zip(pts, tans)):
        s = end * k / n
        if cut is None and k == n:
            tip = bm.verts.new(c)
            break
        if s < 0.3:
            hw = width / 2 * (0.6 + 1.33 * s)
        elif s < 0.55:
            hw = width / 2
        else:
            hw = width / 2 * max(0.0, (1 - s) / 0.45)
        hw = max(hw, 0.03)
        nrm = tan.cross(w0).normalized()
        wv = tan.cross(nrm).normalized() * -1
        ang = roll + twist * s
        wr = wv * math.cos(ang) + nrm * math.sin(ang)
        nr = nrm * math.cos(ang) - wv * math.sin(ang)
        th = thick * (1 - 0.5 * s)
        rings.append([bm.verts.new(c - wr * hw), bm.verts.new(c - nr * th * 0.6),
                      bm.verts.new(c + wr * hw), bm.verts.new(c + nr * th)])
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    bm.faces.new(list(reversed(rings[0])))
    if tip is not None:
        r = rings[-1]
        for i in range(4):
            bm.faces.new((r[i], r[(i + 1) % 4], tip))
    else:
        bm.faces.new(rings[-1])
    verts = [v for ring in rings for v in ring] + ([tip] if tip else [])
    return a._finish(verts, mat)


def lean_rot(az, ang):
    """Euler rotation tilting +Z by `ang` toward azimuth `az`."""
    m = Matrix.Rotation(ang, 3, Vector((-math.sin(az), math.cos(az), 0)))
    return m.to_euler()


def head(a, length=2.4, radius=0.55, sides=7, rot0=0.0):
    prof = [(0.0, radius * 0.35), (0.22 * length / 2.4, radius * 0.85),
            (0.55 * length / 2.4, radius), (length * 0.8, radius * 0.97),
            (length * 0.93, radius * 0.72), (length, radius * 0.3)]
    return lathe(a, prof, sides, "r07_cattail", rot0)


def cattail(a, base, top_h, az, tilt, head_len=2.2):
    """Stalk + seed head + tip nub, built upright then tilted and moved to base."""
    stalk_h = top_h - base[2] - head_len - 0.35
    vs = a.cyl(0.17, 0.15, stalk_h + 0.2, sides=7, mat="r07_reed_stalk")
    hv = head(a, head_len, 0.5, 6, rot0=az)
    a.transform(hv, (0, 0, stalk_h))
    nub = a.cyl(0.13, 0.07, 0.45, sides=5, loc=(0, 0, stalk_h + head_len - 0.05), mat="r07_cattail")
    allv = vs + hv + nub
    a.transform(allv, (0, 0, 0), tuple(lean_rot(az, tilt)))
    a.transform(allv, base)
    return allv


def mound(a, size, pebbles, seed_off=0.0):
    """Faceted mud mound sitting on z=0 plus rim pebbles [(x, y, s)]."""
    a.rock((size[0], size[1], size[2] * 1.3), (0, 0, 0), (0, 0, 0.3 + seed_off),
           mat="r07_soil", subdiv=2, rough=0.10, facets=12, sink=0.42)
    for i, (x, y, s) in enumerate(pebbles):
        a.rock((s, s * 0.85, s * 0.7), (x, y, 0), (0, 0, i * 1.3),
               mat="r07_stone", subdiv=1, rough=0.12, facets=8, sink=0.2)


HERO_PEBBLES = [(-2.85, -0.9, 1.35), (-2.5, 1.0, 1.1), (-1.5, -2.3, 1.05),
                (1.6, -2.2, 1.3), (2.85, -0.6, 1.2), (2.4, 1.4, 0.95), (-0.2, -2.55, 0.85)]


# ----------------------------------------------------------------------- build

def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---- HERO --------------------------------------------------------------
    a = fk.Asset("ReedPatch", "R07 ReedPatch")
    mound(a, (6.5, 5.5, 1.2), HERO_PEBBLES)
    top = 0.95
    cattail(a, (-1.0, -0.45, top), 5.8, math.radians(200), math.radians(11))
    cattail(a, (0.0, 0.55, top), 6.5, math.radians(100), math.radians(6))
    cattail(a, (0.95, -0.05, top), 7.2, math.radians(15), math.radians(9))
    # long leaf blades: (azimuth deg, length, lean deg, curve deg, base offset)
    leaves = [(185, 4.5, 40, 32), (215, 5.0, 22, 28), (150, 4.6, 30, 30),
              (355, 4.6, 42, 34), (320, 5.2, 20, 26), (30, 4.6, 30, 30),
              (95, 5.4, 8, 22), (125, 4.6, 24, 30), (65, 5.5, 6, 18), (250, 4.4, 16, 28)]
    for i, (az, L, ln, cv) in enumerate(leaves):
        r = math.radians(az)
        b = (0.45 * math.cos(r), 0.4 * math.sin(r), top - 0.15)
        blade(a, b, r, L, 1.3, math.radians(ln), math.radians(cv), twist=0.3 * ((i % 3) - 1),
              thick=0.11, roll=0.75 if i % 2 else -0.75)
    # short front blades
    for az, L in [(255, 3.2), (290, 2.8), (235, 2.6)]:
        r = math.radians(az)
        blade(a, (0.5 * math.cos(r), 0.5 * math.sin(r), top - 0.15), r, L, 0.85,
              math.radians(20), math.radians(35), roll=0.6)
    # extra thin headless stalks
    for x, y, h, az, t in [(-0.3, -0.6, 3.6, 260, 6), (0.5, -0.5, 4.2, 300, 5),
                           (-0.4, 0.7, 4.0, 140, 7), (1.1, 0.6, 3.4, 40, 8)]:
        v = a.cyl(0.12, 0.08, h, sides=6, mat="r07_reed_stalk")
        a.transform(v, (0, 0, 0), tuple(lean_rot(math.radians(az), math.radians(t))))
        a.transform(v, (x, y, top - 0.2))
    o = a.finish()
    vfx.add(o, "harvest_hit", (0, -1.5, 3.5), color=CHIPS)
    vfx.add(o, "harvest_deplete", (0, 0, 0.5), color=SOIL_DUST)
    out.append(kit.tag(o, "hero", collision="hull", budget=3500,
                       notes="harvest_hit: reed chips on the front face at mid height; "
                             "harvest_deplete: soil burst at the base centre when cleared"))

    # ---- PARTS -------------------------------------------------------------
    a = fk.Asset("ReedPatchReedStalk", "R07 ReedPatch part")
    a.cyl(0.21, 0.2, 1.1, sides=8, mat="r07_reed_stalk")
    a.cyl(0.23, 0.23, 0.14, sides=8, loc=(0, 0, 1.05), mat="r07_reed_stalk")
    a.cyl(0.18, 0.16, 3.95, sides=8, loc=(0.03, 0, 1.15), mat="r07_reed_stalk")
    a.cyl(0.2, 0.2, 0.12, sides=8, loc=(0.03, 0, 3.2), mat="r07_reed_stalk")
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="single straight reed stalk with node joints"))

    a = fk.Asset("ReedPatchSeedHead", "R07 ReedPatch part")
    a.cyl(0.16, 0.15, 0.45, sides=7, mat="r07_reed_stalk")
    hv = head(a, 2.4, 0.55, 7)
    a.transform(hv, (0, 0, 0.4))
    a.cyl(0.13, 0.07, 0.3, sides=5, loc=(0, 0, 2.75), mat="r07_cattail")
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="cattail seed head with stalk stub and tip nub"))

    a = fk.Asset("ReedPatchLeafBlade", "R07 ReedPatch part")
    blade(a, (0, 0, 0), math.radians(90), 5.5, 1.0, math.radians(2), math.radians(8),
          segs=5, thick=0.12)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="single flat pointed leaf blade"))

    a = fk.Asset("ReedPatchMudBase", "R07 ReedPatch part")
    mound(a, (6.5, 5.5, 1.2), [(2.6, 1.2, 1.1), (-2.7, -0.9, 0.9)], -0.3)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="mud mound base with two pebbles"))

    # ---- DROP: ReedStems ---------------------------------------------------
    a = fk.Asset("ReedStems", "R07 ReedPatch drop")
    rot = (0, math.radians(90), 0)
    stems = [(-0.42, 0.2, -0.1), (0.0, 0.2, 0.15), (0.42, 0.2, -0.05),
             (-0.21, 0.55, 0.05), (0.21, 0.55, -0.15)]
    for i, (y, z, dx) in enumerate(stems):
        yaw = y * 0.6
        v = a.cyl(0.14, 0.14, 2.2, sides=5, loc=(0, 0, -1.1 + dx), mat="r07_reed_stalk")
        hv = lathe(a, [(0, 0.15), (0.1, 0.26), (0.55, 0.25), (0.72, 0.09)], 5, "r07_cattail")
        a.transform(hv, (0, 0, 1.08 + dx))
        allv = v + hv
        a.transform(allv, (0, 0, 0), (0, math.radians(90), yaw))
        a.transform(allv, (-0.3, y * 0.6, z))
    band = a.cyl(0.5, 0.5, 0.3, sides=6, mat="r07_cattail")
    a.transform(band, (0, 0, 0), rot)
    a.transform(band, (-0.3, 0, 0.38))
    out.append(kit.tag(a.finish(), "drop", collision="none", budget=300,
                       notes="Reed Stems: tied bundle of cut stems with cattail heads"))

    # ---- VARIANT: Clipped Patch -------------------------------------------
    a = fk.Asset("ReedPatchClippedPatch", "R07 ReedPatch variant")
    mound(a, (6.0, 5.0, 1.0), [(-2.6, -0.8, 1.05), (-1.2, -2.1, 0.85), (1.6, -2.0, 1.0),
                               (2.6, 0.6, 0.9), (-2.2, 1.2, 0.8)], 1.4)
    top = 0.8
    for i, (az, L, ln, cv) in enumerate([(200, 3.0, 25, 35), (340, 2.8, 28, 30), (120, 2.6, 12, 20),
                                         (60, 2.6, 10, 18), (270, 2.4, 18, 25), (20, 2.5, 15, 22)]):
        r = math.radians(az)
        blade(a, (0.45 * math.cos(r), 0.4 * math.sin(r), top - 0.1), r, L, 0.9,
              math.radians(ln), math.radians(cv), segs=2, cut=0.65, roll=0.7 if i % 2 else -0.7)
    for x, y in [(-0.2, -0.1), (0.35, 0.3)]:
        a.cyl(0.17, 0.16, 1.5, sides=7, loc=(x, y, top - 0.1), mat="r07_reed_stalk")
    o = a.finish()
    vfx.add(o, "harvest_deplete", (0, 0, 0.5), color=SOIL_DUST)
    out.append(kit.tag(o, "variant", collision="hull", budget=2000,
                       notes="Clipped Patch: partly harvested, cut stubs; harvest_deplete at the base"))

    # ---- DEPLETED -----------------------------------------------------------
    a = fk.Asset("ReedPatchDepleted", "R07 ReedPatch depleted")
    mound(a, (6.3, 5.3, 1.0), HERO_PEBBLES[:6], -0.2)
    out.append(kit.tag(a.finish(), "depleted", collision="hull", budget=2000,
                       notes="Depleted (Base): bare mud mound with pebbles"))
    return out
