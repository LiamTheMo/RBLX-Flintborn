"""V01 row 4: DandelionRosette - toothed leaf rosette, chunky yellow flower,
side bud, seed puff and clipped rosette."""
import math

import bmesh
from mathutils import Vector

SUBJECT = "DandelionRosette"
ROW = 4
HERO_AZIMUTH = -22
PALETTE = {
    "v01_dandelion_leaf": ("#5FAE2A", 0.85, 0, 0),
    "v01_stem": ("#4C9230", 0.85, 0, 0),
    "v01_brown": ("#8A5530", 0.9, 0, 0),
    "v01_dandelion_yellow": ("#FFC400", 0.7, 0, 0),
    "v01_cream": ("#EFE6CF", 0.8, 0, 0),
}
LEAF, STEM, BROWN, YELLOW, CREAM = ("v01_dandelion_leaf", "v01_stem", "v01_brown",
                                    "v01_dandelion_yellow", "v01_cream")


# -- geometry helpers ----------------------------------------------------------

def _close(a, verts, mat):
    faces = list({f for v in verts for f in v.link_faces})
    bmesh.ops.recalc_face_normals(a.bm, faces=faces)
    return a._finish(verts, mat)


def leaf(a, length, width, base, az, lift, curl, teeth=5, fold=0.35, mat=LEAF):
    """Toothed lance leaf: closed thin shell with a creased midrib, bent along
    its length (pitch `lift` at the base, losing `curl` radians by the tip)."""
    bm = a.bm
    # section list: (t, half-width, edge y-offset as fraction of length)
    secs = [(0.0, 0.05, 0.0), (0.08, 0.09, 0.0)]
    t0, t1 = 0.16, 0.86
    for i in range(teeth):
        tn = t0 + (t1 - t0) * i / teeth
        prof = math.sin(math.pi * min(1.0, (tn + 0.04) ** 1.5)) ** 0.8
        secs.append((tn, 0.34 * prof + 0.08, 0.0))             # notch
        secs.append((tn + 0.015, 1.0 * prof + 0.12, -0.06))      # backward tooth apex
    secs.append((0.92, 0.32, 0.0))
    # centerline by integrating the pitch angle
    def theta(t):
        return lift - curl * t ** 1.4

    def centre(t, steps=24):
        x = z = 0.0
        for k in range(steps):
            tm = (k + 0.5) / steps * t
            x += math.cos(theta(tm)) * length * t / steps
            z += math.sin(theta(tm)) * length * t / steps
        return x, z

    ca, sa = math.cos(az), math.sin(az)
    bx, by, bz = base

    def world(t, x, z_off, dy=0.0):
        tt = min(1.0, max(0.0, t + dy))
        h, z = centre(tt)
        th = theta(tt)
        h += -math.sin(th) * z_off
        z += math.cos(th) * z_off
        # local frame: along = (ca, sa), side = (-sa, ca)
        wx = bx + ca * h - sa * x
        wy = by + sa * h + ca * x
        return Vector((wx, wy, max(0.0, bz + z)))

    th_k = 0.035 * width
    rings = []
    for t, hw, dy in secs:
        w = hw * width * 0.5
        L = bm.verts.new(world(t, -w, fold * w, dy))
        Mt = bm.verts.new(world(t, 0.0, th_k))
        R = bm.verts.new(world(t, w, fold * w, dy))
        Mb = bm.verts.new(world(t, 0.0, -th_k))
        rings.append((L, Mt, R, Mb))
    tip = bm.verts.new(world(1.0, 0.0, 0.0))
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(4):
            bm.faces.new((r0[j], r0[(j + 1) % 4], r1[(j + 1) % 4], r1[j]))
    last = rings[-1]
    for j in range(4):
        bm.faces.new((last[j], last[(j + 1) % 4], tip))
    bm.faces.new(rings[0])
    verts = [v for r in rings for v in r] + [tip]
    return _close(a, verts, mat)


def tube(a, pts, radii, sides=6, mat=STEM):
    bm = a.bm
    pts = [Vector(p) for p in pts]
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        u = t.cross(ref).normalized()
        v = t.cross(u)
        ring = []
        for k in range(sides):
            ang = 2 * math.pi * k / sides
            q = p + radii[i] * (math.cos(ang) * u + math.sin(ang) * v)
            q.z = max(0.0, q.z)
            ring.append(bm.verts.new(q))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            bm.faces.new((r0[k], r0[(k + 1) % sides], r1[(k + 1) % sides], r1[k]))
    bm.faces.new(rings[0])
    bm.faces.new(rings[-1])
    return _close(a, [v for r in rings for v in r], mat)


def petal_ring(a, n, r0, r1, half0, half1, z, tilt, depth, az0, mat):
    out = []
    outline = [(r0, -half0), (r1 * 0.9, -half1), (r1, 0.0), (r1 * 0.9, half1), (r0, half0)]
    for i in range(n):
        az = az0 + 2 * math.pi * i / n
        out += a.poly_prism(outline, depth, loc=(0, 0, z), rot=(0, tilt, az), mat=mat)
    return out


def flower_head(a, loc, rot=(0, 0, 0), scale=1.0):
    """Yellow head ~1 stud wide: green bract collar + reflexed bracts, then two
    rings of faceted petal wedges and a flat yellow centre."""
    v = []
    v += a.cyl(0.14, 0.34, 0.24, sides=8, loc=(0, 0, -0.04), mat=LEAF)
    v += petal_ring(a, 8, 0.12, 0.40, 0.05, 0.08, 0.02, 0.75, 0.04, 0.2, LEAF)
    v += petal_ring(a, 16, 0.12, 0.54, 0.05, 0.12, 0.16, -0.18, 0.16, 0.0, YELLOW)
    v += petal_ring(a, 13, 0.06, 0.44, 0.04, 0.11, 0.28, -0.38, 0.15, 0.12, YELLOW)
    v += petal_ring(a, 9, 0.02, 0.28, 0.04, 0.10, 0.40, -0.55, 0.12, 0.3, YELLOW)
    v += a.cyl(0.24, 0.16, 0.3, sides=8, loc=(0, 0, 0.22), mat=YELLOW)
    a.transform(v, loc, rot, (scale, scale, scale))
    return v


def bud(a, loc, rot=(0, 0, 0)):
    v = []
    v += a.ico((0.17, 0.17, 0.27), loc=(0, 0, 0.22), mat=LEAF)
    v += petal_ring(a, 5, 0.0, 0.22, 0.05, 0.08, 0.04, 1.0, 0.05, 0.3, LEAF)
    v += a.cyl(0.12, 0.03, 0.18, sides=5, loc=(0, 0, 0.42), mat=YELLOW)
    a.transform(v, loc, rot)
    return v


def roots(a, loc=(0, 0, 0), height=0.32, reach=0.5, n=5, r=0.045):
    x0, y0, z0 = loc
    a.cyl(0.17, 0.09, height, sides=6, loc=(x0, y0, z0), mat=BROWN)
    for i in range(n):
        ang = 2 * math.pi * i / n + 0.4
        c, s = math.cos(ang), math.sin(ang)
        tube(a, [(x0 + 0.05 * c, y0 + 0.05 * s, z0 + height * 0.55),
                 (x0 + 0.5 * reach * c, y0 + 0.5 * reach * s, z0 + 0.07),
                 (x0 + reach * c, y0 + reach * s, z0 + 0.02)],
             [r * 1.3, r, r * 0.45], sides=4, mat=BROWN)


def rosette(a, size=1.0, n=11, upright=0.0, seed=0, teeth=5):
    """n leaves radiating from the hub; even leaves low and curling, odd ones raised."""
    rng = a.rng
    for i in range(n):
        az = 2 * math.pi * i / n + 0.35 + rng.uniform(-0.12, 0.12)
        low = i % 2 == 0
        length = size * (2.25 if low else 2.05) * rng.uniform(0.92, 1.05)
        width = size * (1.3 if low else 1.15)
        lift = (0.42 if low else 0.98) + upright
        curl = (0.4 if low else 0.38) + upright * 0.3
        leaf(a, length, width, (0.08 * math.cos(az), 0.08 * math.sin(az), 0.06),
             az, lift, curl, teeth=teeth)


# -- assets --------------------------------------------------------------------

def build(kit):
    fk = kit.flintkit
    out = []
    note = "no sockets; plain mesh flowers, players walk through it"

    # HERO
    a = fk.Asset("DandelionRosette", "V01 DandelionRosette")
    rosette(a, 1.0, 10)
    roots(a, height=0.3, reach=0.45)
    tube(a, [(0, 0, 0.1), (0.02, 0.0, 1.4), (0.0, 0.0, 2.62)], [0.15, 0.14, 0.13])
    flower_head(a, (0, 0, 2.62), scale=1.1)
    tube(a, [(0.05, 0, 0.2), (0.4, -0.08, 0.85), (0.58, -0.12, 1.2)], [0.09, 0.08, 0.075])
    bud(a, (0.58, -0.12, 1.17), (0.0, 0.3, 0.0))
    out.append(kit.tag(a.finish(), "hero", collision="none", budget=3500, notes=note))

    # PARTS
    for name, ln, wd, th in (("DandelionLeafLarge", 2.4, 1.2, 5),
                             ("DandelionLeafMedium", 1.8, 1.0, 4),
                             ("DandelionLeafSmall", 1.2, 0.75, 3)):
        a = fk.Asset(name, "V01 " + name)
        leaf(a, ln, wd, (0, 0, 0), math.pi / 2, 1.5, 0.12, teeth=th)
        out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes=note))

    a = fk.Asset("DandelionFlowerHeadSide", "V01 DandelionFlowerHeadSide")
    tube(a, [(0, 0, 0), (0, 0, 0.4)], [0.09, 0.08])
    flower_head(a, (0, 0, 0.4))
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes=note))

    a = fk.Asset("DandelionFlowerHeadBottom", "V01 DandelionFlowerHeadBottom")
    tube(a, [(0, -0.25, 0.0), (0, -0.05, 0.45)], [0.09, 0.08])
    flower_head(a, (0, 0.05, 0.62), (-1.15, 0, 0))
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes=note))

    a = fk.Asset("DandelionStalk", "V01 DandelionStalk")
    tube(a, [(0, 0, 0), (0.03, 0, 0.6), (0.06, 0, 1.15), (0.2, 0, 1.75), (0.38, 0, 2.35)],
         [0.11, 0.1, 0.1, 0.09, 0.085])
    a.cyl(0.135, 0.135, 0.12, sides=6, loc=(0.06, 0, 1.09), mat=STEM)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes=note))

    a = fk.Asset("DandelionRootBase", "V01 DandelionRootBase")
    roots(a, height=0.6, reach=0.6, n=6, r=0.08)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes=note))

    # VARIATIONS
    a = fk.Asset("DandelionYellowBloom", "V01 DandelionYellowBloom")
    rosette(a, 0.85, 10)
    roots(a, height=0.25, reach=0.4)
    tube(a, [(0, 0, 0.1), (0.02, 0, 1.3), (0, 0, 2.45)], [0.14, 0.13, 0.12])
    flower_head(a, (0, 0, 2.45), scale=1.05)
    out.append(kit.tag(a.finish(), "variant", collision="none", budget=3000,
                       notes="A. Yellow Bloom; " + note))

    a = fk.Asset("DandelionSeedPuff", "V01 DandelionSeedPuff")
    rosette(a, 0.85, 10)
    roots(a, height=0.25, reach=0.4)
    tube(a, [(0, 0, 0.1), (0.02, 0, 1.3), (0, 0, 2.5)], [0.14, 0.13, 0.12])
    a.ico(0.65, loc=(0, 0, 2.55), mat=CREAM, subdiv=2, jitter=0.07, facets=14)
    out.append(kit.tag(a.finish(), "variant", collision="none", budget=3000,
                       notes="B. Seed Puff; " + note))

    a = fk.Asset("DandelionClippedRosette", "V01 DandelionClippedRosette")
    rosette(a, 0.72, 10, upright=0.35)
    roots(a, height=0.22, reach=0.35)
    out.append(kit.tag(a.finish(), "depleted", collision="none", budget=2000,
                       notes="C. Clipped Rosette (harvested state); " + note))
    return out
