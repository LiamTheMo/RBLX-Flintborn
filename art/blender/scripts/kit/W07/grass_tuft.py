"""W07 row 1 - GrassTuft: chunky faceted broad-leaf grass clump.

Blades are hand-built 6-sided ridged prisms (left edge, two front facets
meeting in a raised mid-rib, right edge, two shallow back facets) over 6-8
rings, so each blade is a fat lanceolate solid with a central crease and a
pointed tip.
"""
import math
import random

import bmesh
from mathutils import Vector

SUBJECT = "GrassTuft"
ROW = 1
HERO_AZIMUTH = -22

PALETTE = {
    "w07_grass": ("#5A9A1E", 0.9, 0, 0),
    "w07_grass_dry": ("#D2A850", 0.9, 0, 0),
    "w07_root": ("#B8672A", 0.9, 0, 0),
    "w07_stone": ("#8E8E94", 0.95, 0, 0),
}

UP = Vector((0, 0, 1))
# cross-section in (width, thickness) units: ridged front, shallow back
SECTION = [(-1.0, 0.0), (-0.5, 0.62), (0.0, 1.0), (0.5, 0.62), (1.0, 0.0), (0.0, -0.55)]
TS6 = (0.0, 0.14, 0.32, 0.52, 0.70, 0.86)
PROF6 = (0.6, 0.88, 1.0, 0.86, 0.58, 0.28)
TS8 = (0.0, 0.1, 0.24, 0.4, 0.56, 0.7, 0.82, 0.91)
PROF8 = (0.62, 0.82, 0.97, 1.0, 0.88, 0.66, 0.44, 0.24)


def _mesh(a, verts, faces, mat):
    bm = a.bm
    vs = [bm.verts.new(Vector(v)) for v in verts]
    fs = [bm.faces.new([vs[i] for i in f]) for f in faces]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    return a._finish(vs, mat)


def blade(a, az, h, w, lean, curl=0.2, twist=0.0, mat="w07_grass", base=0.1,
          thick=0.62, prof=PROF6, ts=TS6, roll=0.0):
    """One solid blade leaning toward azimuth `az` (deg), height `h`, widest
    width `w`. `roll` turns the broad face about the blade axis (radians)."""
    azr = math.radians(az)
    d = Vector((math.cos(azr), math.sin(azr), 0))
    wp = Vector((-math.sin(azr), math.cos(azr), 0))
    tlist = list(ts) + [1.0]

    def ang(t):
        return lean + curl * t * t

    pts, p, prev = [], Vector((0, 0, 0)), 0.0
    for t in tlist:
        dt = t - prev
        th = ang((t + prev) / 2)
        p = p + dt * (math.sin(th) * d + math.cos(th) * UP)
        pts.append(p.copy())
        prev = t
    s = h / max(pts[-1].z, 0.01)
    start = d * base
    pts = [start + q * s for q in pts]
    verts, faces = [], []
    ns = len(SECTION)
    for i, t in enumerate(ts):
        th = ang(t)
        n = math.cos(th) * d - math.sin(th) * UP
        tw = roll + twist * t
        wa = math.cos(tw) * wp + math.sin(tw) * n
        na = wa.cross(math.sin(th) * d + math.cos(th) * UP)
        hw = 0.5 * w * prof[i]
        tk = thick * hw
        c = pts[i]
        for (u, v) in SECTION:
            q = c + wa * (u * hw) + na * (v * tk)
            verts.append((q.x, q.y, max(q.z, 0.0)))
    tip = pts[-1]
    verts.append((tip.x, tip.y, tip.z))
    nr = len(ts)
    for i in range(nr - 1):
        for j in range(ns):
            a0, a1 = i * ns + j, i * ns + (j + 1) % ns
            faces.append((a0, a1, a1 + ns, a0 + ns))
    ti = len(verts) - 1
    for j in range(ns):
        faces.append(((nr - 1) * ns + j, (nr - 1) * ns + (j + 1) % ns, ti))
    faces.append(tuple(range(ns - 1, -1, -1)))
    return _mesh(a, verts, faces, mat)


def root_base(a, scale=1.0, fins=5, stub_h=0.45, rot0=0.0, fin_len=0.58, fin_w=0.13):
    r = 0.15 * scale
    a.cyl(r * 1.2, r, stub_h * scale, sides=7, mat="w07_root")
    for k in range(fins):
        az = rot0 + 2 * math.pi * k / fins + 0.25 * math.sin(k * 2.3)
        d = Vector((math.cos(az), math.sin(az), 0))
        sd = Vector((-d.y, d.x, 0))
        r0, r1 = r * 0.6, fin_len * scale * (0.9 + 0.2 * math.sin(k * 1.7))
        top = d * r0 + UP * (0.42 * scale)
        b1 = d * r0 + sd * fin_w * scale
        b2 = d * r0 - sd * fin_w * scale
        tipv = d * r1 + UP * 0.03 * scale
        ridge = d * (r0 + r1) * 0.5 + UP * 0.28 * scale
        vs = [tuple(top), tuple(b1), tuple(b2), tuple(tipv), tuple(ridge)]
        fs = [(0, 1, 4), (0, 4, 2), (1, 3, 4), (4, 3, 2), (0, 2, 1), (1, 2, 3)]
        _mesh(a, vs, fs, "w07_root")


def pebbles(a, spots):
    for (x, y, sx, sy, sz, rz) in spots:
        a.rock((sx, sy, sz), loc=(x, y, 0), rot=(0, 0, rz), mat="w07_stone",
               subdiv=1, rough=0.1, facets=10, sink=0.0)


def build(kit):
    fk = kit.flintkit
    out = []
    rng = random.Random(7)

    # ---- hero: 5 broad main blades + 2 low side blades -------------------
    a = fk.Asset("GrassTuft", "W07 GrassTuft")
    root_base(a, 1.0, fins=5)
    for (az, h, w, lean, curl, tw, rl) in [
        (90, 3.0, 1.3, 0.3, 0.2, 0.15, 0),      # centre-back tall
        (165, 2.5, 1.25, 0.24, 0.26, -0.25, 1.1),   # left
        (15, 2.6, 1.25, 0.22, 0.26, 0.25, -1.1),     # right
        (-112, 2.15, 1.2, 0.56, 0.34, 0.2, 0),    # front-left
        (-66, 2.3, 1.2, 0.54, 0.34, -0.2, 0),     # front-right
        (215, 0.95, 0.85, 0.95, 0.25, 0.0, 0),    # low side blade left
        (-20, 0.9, 0.82, 0.98, 0.25, 0.0, 0),     # low side blade right
    ]:
        blade(a, az, h, w, lean, curl, tw, base=0.25 if h > 1.5 else 0.4, roll=rl)
    pebbles(a, [(-0.95, -0.8, 0.72, 0.58, 0.44, 0.4),
                (0.95, -0.75, 0.64, 0.52, 0.4, 1.2),
                (0.2, -1.25, 0.48, 0.4, 0.3, 2.0)])
    o = a.finish()
    out.append(kit.tag(o, "hero", collision="none", budget=800,
                       notes="Grass tuft scatter: 5 broad main blades + 2 low side blades, root base, 3 pebbles. No VFX."))

    # ---- parts -----------------------------------------------------------
    a = fk.Asset("SingleBlade", "W07 GrassTuft part")
    blade(a, 60, 2.6, 0.78, 0.16, 0.12, 0.25, base=0.0, ts=TS8, prof=PROF8)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=150, notes="One ridged tapered blade."))

    a = fk.Asset("ThreeBladeClump", "W07 GrassTuft part")
    blade(a, 100, 2.6, 0.85, 0.05, 0.1, 0.15, base=0.0, ts=TS8, prof=PROF8)
    blade(a, 180, 2.0, 0.85, 0.24, 0.2, -0.15, base=0.08, roll=math.pi / 2, ts=TS8, prof=PROF8)
    blade(a, 0, 2.0, 0.85, 0.24, 0.2, 0.15, base=0.08, roll=math.pi / 2, ts=TS8, prof=PROF8)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=500, notes="Three broad blades joined at the base."))

    a = fk.Asset("RootBase", "W07 GrassTuft part")
    root_base(a, 0.95, fins=5, stub_h=0.74, rot0=-0.5, fin_len=0.44, fin_w=0.17)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=200, notes="Cut stem stub with flared root fins."))

    # ---- variants --------------------------------------------------------
    a = fk.Asset("ShortWide", "W07 GrassTuft variant")
    root_base(a, 0.8, fins=4)
    blade(a, 90, 1.45, 0.9, 0.3, 0.2, 0.2)
    for k in range(6):
        az = -100 + k * 60 + rng.uniform(-12, 12)
        blade(a, az, rng.uniform(1.15, 1.4), 0.9, 0.85, 0.3, base=0.2,
              twist=rng.uniform(-0.3, 0.3))
    o = a.finish()
    out.append(kit.tag(o, "variant", collision="none", budget=800,
                       notes="Short & Wide: low spreading rosette of 7 broad blades."))

    a = fk.Asset("TallPointed", "W07 GrassTuft variant")
    root_base(a, 0.8, fins=4)
    tst = (0.0, 0.12, 0.28, 0.45, 0.62, 0.77, 0.89)
    prt = (0.6, 0.88, 1.0, 0.9, 0.68, 0.42, 0.2)
    for (az, h, lean, rl) in [(95, 4.2, 0.03, 0), (165, 3.7, 0.2, 1.2), (15, 3.8, 0.18, -1.2),
                          (-125, 3.2, 0.28, 0.4), (-55, 3.4, 0.26, -0.4), (250, 2.8, 0.26, 1.2)]:
        blade(a, az, h, 1.1, lean, 0.1, base=0.18, roll=rl, twist=rng.uniform(-0.3, 0.3),
              ts=tst, prof=prt)
    o = a.finish()
    out.append(kit.tag(o, "variant", collision="none", budget=800,
                       notes="Tall & Pointed: broad upright blades with sharp points."))

    a = fk.Asset("DryGrass", "W07 GrassTuft variant")
    root_base(a, 0.8, fins=4)
    for (az, h, w, lean, curl) in [(95, 2.8, 1.0, 0.12, 0.5), (165, 2.4, 0.95, 0.32, 0.65),
                                   (25, 2.5, 0.95, 0.3, 0.65), (-125, 2.1, 0.92, 0.38, 0.7),
                                   (-45, 2.2, 0.92, 0.36, 0.65), (230, 1.5, 0.85, 0.55, 0.6)]:
        blade(a, az, h, w, lean, curl + 0.3, rng.uniform(-0.3, 0.3), mat="w07_grass_dry", base=0.24)
    o = a.finish()
    out.append(kit.tag(o, "variant", collision="none", budget=800,
                       notes="Dry Grass: hero form, drooping tips, sandy gold."))
    return out
