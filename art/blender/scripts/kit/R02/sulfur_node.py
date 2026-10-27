"""R02 row 3: SulfurNode resource (tiered grey slab plateau with lemon-yellow blocky sulfur)."""
import math
import json
import random

import mathutils

SUBJECT = "SulfurNode"
ROW = 3
PALETTE = {
    "r02_base_rock": ("#8C827D", 0.95, 0, 0),
    "r02_sulfur": ("#E6DB2E", 0.7, 0, 0),
}

ROCK = "r02_base_rock"
SULF = "r02_sulfur"
CAT = "R02 SulfurNode"


def _outline(rx, ry, n, seed, wob=0.13):
    """Irregular, lumpy rounded polygon (not a regular octagon)."""
    rng = random.Random(seed)
    pts = []
    for i in range(n):
        t = 2 * math.pi * (i + rng.uniform(-0.25, 0.25)) / n
        k = 1.0 + rng.uniform(-wob, wob)
        c, s = math.cos(t), math.sin(t)
        c = math.copysign(abs(c) ** 0.85, c)
        s = math.copysign(abs(s) ** 0.85, s)
        pts.append((rx * c * k, ry * s * k))
    return pts


def slab(a, size, loc, seed, n=13, jitter=0.07, mat=ROCK):
    """Flat sedimentary slab: tucked-in base, overhanging rounded lip, flat top."""
    sx, sy, h = size
    x0, y0, z0 = loc
    pts = _outline(sx / 2, sy / 2, n, seed)
    rings = [(0.0, 0.84), (0.45, 0.97), (0.78, 1.0), (1.0, 0.9)]
    bm = a.bm
    layers = []
    rng = random.Random(seed + 1)
    for li, (zf, sc) in enumerate(rings):
        row = []
        for px, py in pts:
            jx = rng.uniform(-jitter, jitter) if li else 0.0
            jz = rng.uniform(-jitter, jitter) if 0 < li < len(rings) - 1 else 0.0
            row.append(bm.verts.new((x0 + px * sc + jx, y0 + py * sc + jx * 0.5, z0 + h * zf + jz)))
        layers.append(row)
    for lo, hi in zip(layers, layers[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bm.faces.new(layers[-1])
    if z0 > 0.01:
        bm.faces.new(list(reversed(layers[0])))
    verts = [v for l in layers for v in l]
    return a._finish(verts, mat, None, 0.0)


def chunk(a, size, loc, rot=(0, 0, 0), seed=1, jitter=0.12, skew=0.0, mat=SULF):
    """Chamfered sulfur block: 10-sided chamfered outline lofted through 5 rings,
    jittered so it breaks into a few big facets like the reference blocks.
    Base sits at loc z.  skew lowers the +x end of the top (wedge-ish)."""
    rng = random.Random(seed)
    sx, sy, sz = size
    hx, hy = sx / 2, sy / 2
    c = min(hx, hy) * rng.uniform(0.3, 0.42)
    pts = [(hx - c, -hy), (0.05 * sx, -hy), (-hx + c, -hy), (-hx, -hy + c), (-hx, hy - c),
           (-hx + c, hy), (-0.05 * sx, hy), (hx - c, hy), (hx, hy - c), (hx, -hy + c)]
    rings = [(0.0, 0.8), (0.14, 0.96), (0.55, 1.0), (0.86, 0.94), (1.0, 0.72)]
    bm = a.bm
    R = mathutils.Euler(rot).to_matrix()
    L = mathutils.Vector(loc)
    layers = []
    for li, (zf, sc) in enumerate(rings):
        row = []
        for px, py in pts:
            x = px * sc + rng.uniform(-jitter, jitter)
            y = py * sc + rng.uniform(-jitter, jitter)
            z = sz * zf
            if li:
                z += rng.uniform(-jitter, jitter) * 0.8
            if li >= len(rings) - 2:
                z -= skew * sz * (px / sx + 0.5) * zf
            row.append(bm.verts.new(L + R @ mathutils.Vector((x, y, z))))
        layers.append(row)
    n = len(pts)
    for lo, hi in zip(layers, layers[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bm.faces.new(layers[-1])
    bm.faces.new(list(reversed(layers[0])))
    verts = [v for l in layers for v in l]
    return a._finish(verts, mat, None, 0.0)


def _emitters(vfx, kind, color, faint=0.0, size_k=1.0):
    """Copy a kind's emitters with a new colour (optionally fainter / smaller)."""
    ems = json.loads(json.dumps(vfx.KINDS[kind]["emitters"]))
    for em in ems:
        em["color"] = list(color)
        if faint and "transparency" in em:
            em["transparency"] = [min(1.0, t + faint) for t in em["transparency"]]
        if size_k != 1.0 and "size" in em:
            em["size"] = [s * size_k for s in em["size"]]
    return ems


HERO_TIERS = [  # (size, loc, seed)  bottom wide, middle back, top right
    ((11.0, 8.8, 1.5), (0.0, -0.1, 0.0), 11),
    ((9.0, 7.0, 1.3), (-0.4, 0.9, 1.4), 23),
    ((7.4, 5.6, 1.0), (1.0, 0.6, 2.6), 37),
]


def slab_stack(a, tiers):
    for size, loc, seed in tiers:
        slab(a, size, loc, seed)


def base_rocks(a, sets):
    for size, loc, rz in sets:
        a.rock(size, loc=loc, rot=(0, 0, rz), mat=ROCK, subdiv=2, rough=0.12, facets=14)


HERO_ROCKS = [
    ((2.4, 2.1, 1.6), (-4.0, -3.7, 0), 0.3),
    ((1.6, 1.4, 1.1), (-2.0, -4.3, 0), 1.1),
    ((2.2, 1.9, 1.5), (3.6, -3.8, 0), -0.4),
    ((1.5, 1.3, 1.0), (1.4, -4.4, 0), 0.7),
    ((1.7, 1.5, 1.2), (4.7, -1.8, 0), 0.2),
]


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []
    top = 3.4   # chunks seat slightly into the top slab (top surface ~3.6)

    # ---- hero
    a = fk.Asset("SulfurNode", CAT, seed=302)
    slab_stack(a, HERO_TIERS)
    chunk(a, (3.4, 3.0, 2.8), (-0.2, 1.3, top), (-0.15, -0.06, 0.3), seed=1, jitter=0.24)  # tall back-centre
    chunk(a, (2.7, 2.6, 2.2), (-2.4, 0.0, top - 0.1), (-0.1, 0.14, -0.35), seed=2, jitter=0.24)  # medium left
    chunk(a, (4.5, 3.0, 2.4), (1.7, -0.7, top - 0.05), (0.14, 0.1, 0.2), seed=3, jitter=0.24)  # big right-front
    chunk(a, (1.0, 0.9, 0.8), (4.3, -1.4, top - 0.1), (0, 0, 0.5), seed=4, jitter=0.05)  # crumb
    base_rocks(a, HERO_ROCKS)
    o = a.finish()
    chips = ["#E6DB2E", "#C9BE22"]
    vap = ["#F2EE9A", "#FFFFFF"]
    vfx.add(o, "harvest_hit", (1, -3.5, 5), color=chips, emitters=_emitters(vfx, "harvest_hit", chips))
    vfx.add(o, "vapour", (0, 0.5, 7), scale=0.5, color=vap,
            emitters=_emitters(vfx, "vapour", vap, faint=0.3, size_k=0.6))
    vfx.add(o, "vapour", (-2, 0.5, 6.3), scale=0.3, color=vap,
            emitters=_emitters(vfx, "vapour", vap, faint=0.35, size_k=0.5))
    out.append(kit.tag(o, "hero", collision="hull", budget=5000,
                       notes="harvest_hit: strike face of the front chunks (sulfur yellow chips); "
                             "vapour x2: faint, small yellowish sulfur wisp above/behind the chunk pile. "
                             "Matte ore: no ore_glint."))

    # ---- parts
    a = fk.Asset("SulfurHostRock", CAT, seed=303)
    slab_stack(a, [((10.0, 8.0, 1.8), (0.0, 0.0, 0.0), 11),
                   ((8.4, 6.4, 1.6), (-0.4, 0.7, 1.7), 23),
                   ((6.6, 5.0, 1.5), (0.8, 0.4, 3.2), 37)])
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=2500, notes="layered slab stack without chunks"))

    a = fk.Asset("SulfurChunk", CAT, seed=304)
    chunk(a, (4.0, 2.8, 2.4), (0, 0, 0), seed=5, jitter=0.1)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=500, notes="one blocky chamfered sulfur chunk"))

    a = fk.Asset("SulfurBaseRock", CAT, seed=305)
    a.rock((2.0, 1.7, 1.4), loc=(0, 0, 0), mat=ROCK, subdiv=2, rough=0.12, facets=14)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=400, notes="small base rock"))

    # ---- drops
    a = fk.Asset("SulfurChunkDrop", CAT, seed=306)
    chunk(a, (1.5, 1.1, 1.0), (0, 0, 0), (0, 0, 0.2), seed=6, jitter=0.05)
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="box", budget=300, notes="sulfur chunk pickup"))

    a = fk.Asset("SulfurChunkDrop2", CAT, seed=307)
    chunk(a, (1.4, 1.2, 0.9), (0, 0, 0), (0, 0, -0.3), seed=7, jitter=0.05, skew=0.45)
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="box", budget=300, notes="squat faceted wedge-topped sulfur pickup"))

    # ---- depleted
    a = fk.Asset("SulfurNodeDepleted", CAT, seed=308)
    slab_stack(a, [((10.0, 8.0, 1.7), (0.0, 0.0, 0.0), 11),
                   ((7.8, 5.8, 1.5), (0.4, 0.5, 1.6), 41)])
    base_rocks(a, [((1.8, 1.6, 1.4), (-4.2, -2.8, 0), 0.4),
                   ((1.4, 1.2, 1.0), (-3.0, -3.7, 0), 1.0),
                   ((1.7, 1.5, 1.3), (4.2, -2.9, 0), -0.3)])
    o = a.finish()
    vfx.add(o, "harvest_deplete", (0, 0, 0.2), emitters=_emitters(vfx, "harvest_deplete", ["#B5ADA8", "#8C827D"]))
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="caption 'Depleted (Base)': slab tiers minus chunks; harvest_deplete at base centre"))
    return out
