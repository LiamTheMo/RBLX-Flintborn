"""R02 row 4: ObsidianNode resource (fat glassy chamfered crystals in a heap of warm grey rocks)."""
import math
import random

SUBJECT = "ObsidianNode"
ROW = 4
PALETTE = {
    "r02_base_rock": ("#8C827D", 0.95, 0, 0),  # Base rocks everywhere, sulfur host slab, obsidian host/base slabs (warm light grey)
    "r02_obsidian": ("#1E2338", 0.26, 0.6, 0),  # Obsidian crystal, near-black navy glassy (tuned by obsidian_node: lighter navy, glossier, more metallic so edge facets catch blue)
}

OBS = "r02_obsidian"
ROCK = "r02_base_rock"
HIT_COLOR = ["#22263A", "#3A4366"]

# crystal profile: (height fraction, radius fraction, pull of the ring toward the off-centre apex)
# widest ~58% up, a broad shoulder ring, a chamfer ring, then a short off-centre point
GEM = [(0.0, 0.70, 0), (0.30, 0.92, 0), (0.58, 1.0, 0), (0.74, 0.84, 0.2), (0.87, 0.46, 0.6)]
CHUNK = [(0.0, 0.55, 0), (0.15, 0.88, 0), (0.45, 1.0, 0), (0.70, 0.80, 0.25), (0.86, 0.42, 0.6)]


def crystal(a, w, d, h, loc, rot, sides=5, profile=GEM, seed=1, closed=False, jit=0.2, cham=0.13):
    """Irregular faceted 5-6 sided prism with chamfered vertical edges, broad shoulders and an
    asymmetric chamfered tip. Big faces are split into two triangles on random diagonals so the
    facet planes are irregular and the edge strips catch light."""
    rng = random.Random(seed)
    bm = a.bm
    base_ang = rng.uniform(0, 2 * math.pi)
    angs = [base_ang + (i + rng.uniform(-0.25, 0.25)) * 2 * math.pi / sides for i in range(sides)]
    rads = [1.0 + rng.uniform(-jit, jit) for _ in range(sides)]
    ax, ay = rng.uniform(-0.16, 0.16) * w, rng.uniform(-0.12, 0.12) * d   # off-centre apex
    rings = []
    for k, (zf, rf, pull) in enumerate(profile):
        ring = []
        for i in range(sides):
            r = rf * rads[i] * (1.0 + rng.uniform(-0.07, 0.07))
            for s in (-1, 1):
                ang = angs[i] + s * cham * (1.0 + rng.uniform(-0.3, 0.3))
                rr = r * math.cos(cham) * 0.97
                x = math.cos(ang) * rr * w / 2
                y = math.sin(ang) * rr * d / 2
                x += ax * pull
                y += ay * pull
                z = zf * h + (rng.uniform(-0.035, 0.035) * h if k else 0.0)
                ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)
    apex = bm.verts.new((ax, ay, h))
    n = len(rings[0])
    verts = [v for ring in rings for v in ring] + [apex]
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            if i % 2 == 0:      # thin chamfer strip on the crystal's edge
                bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
            elif rng.random() < 0.5:
                bm.faces.new((r0[i], r0[j], r1[j]))
                bm.faces.new((r0[i], r1[j], r1[i]))
            else:
                bm.faces.new((r0[i], r0[j], r1[i]))
                bm.faces.new((r0[j], r1[j], r1[i]))
    top = rings[-1]
    for i in range(n):
        bm.faces.new((top[i], top[(i + 1) % n], apex))
    if closed:
        bm.faces.new(list(reversed(rings[0])))
    a.transform(verts, loc, rot)
    for v in verts:
        if v.co.z < 0:
            v.co.z = 0.0
    return a._finish(verts, OBS)


def slab(a, pts, h, loc, rot=(0, 0, 0), inset=0.80, seed=1):
    """Flat stone plate: irregular outline, bevelled sides, uneven flat top."""
    rng = random.Random(seed)
    bm = a.bm
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    bot, mid, top = [], [], []
    for (x, y) in pts:
        bot.append(bm.verts.new((cx + (x - cx) * 0.94, cy + (y - cy) * 0.94, 0.0)))
        mid.append(bm.verts.new((x, y, h * rng.uniform(0.5, 0.65))))
        top.append(bm.verts.new((cx + (x - cx) * inset, cy + (y - cy) * inset, h * rng.uniform(0.9, 1.06))))
    n = len(pts)
    for r0, r1 in ((bot, mid), (mid, top)):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    verts = bot + mid + top
    a.transform(verts, loc, rot)
    for v in verts:
        if v.co.z < 0:
            v.co.z = 0.0
    return a._finish(verts, ROCK)


def cracked_slabs(a, small=True, hs=1.0):
    """Two big plates meeting at a crack plus smaller plates (host rock / depleted base)."""
    slab(a, [(-3.5, -2.0), (-2.0, -2.5), (-0.1, -2.3), (0.15, 0.2), (-1.8, 0.45), (-3.8, 0.0)], 1.6 * hs,
         (0, 0, 0), (0.03, 0.05, 0), seed=3)
    slab(a, [(-3.6, 0.35), (-1.8, 0.7), (-0.05, 0.5), (-0.3, 2.4), (-2.0, 2.5), (-3.2, 1.9)], 1.4 * hs,
         (0, 0, 0), (-0.04, 0.04, 0), seed=8)
    slab(a, [(0.35, -2.4), (2.0, -2.5), (3.4, -1.8), (3.8, -0.2), (0.45, 0.0)], 2.0 * hs,
         (0, 0, 0), (0.02, -0.05, 0), seed=4)
    slab(a, [(0.5, 0.2), (3.8, 0.05), (3.4, 1.7), (2.4, 2.5), (0.15, 2.3)], 1.8 * hs,
         (0, 0, 0), (0.04, -0.03, 0), seed=7)
    if small:
        slab(a, [(-1.0, -0.6), (0.2, -0.8), (0.9, -0.5), (1.0, 0.6), (-0.9, 0.7)], 1.0 * hs,
             (-2.3, -2.9, 0), (0, 0, 0.3), seed=5)
        slab(a, [(-0.8, -0.6), (0.8, -0.5), (0.7, 0.6), (-0.1, 0.7), (-0.7, 0.5)], 0.9 * hs,
             (2.6, -2.8, 0), (0, 0, -0.2), seed=6)


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---- hero -------------------------------------------------------------
    a = fk.Asset("ObsidianNode", "R02 ObsidianNode", tint_var=0.05)
    crystal(a, 6.8, 5.4, 10.3, (-0.4, 1.0, 0.3), (-0.06, -0.10, 0.2), sides=6, seed=11)   # tall centre-back
    crystal(a, 5.4, 4.4, 8.2, (2.6, 0.0, 0.3), (0.06, 0.24, -0.3), sides=5, seed=12)     # right, out right
    crystal(a, 5.0, 4.2, 6.5, (-2.8, -0.9, 0.3), (-0.04, -0.20, 0.4), sides=5, seed=13)  # left-front
    crystal(a, 2.4, 2.2, 3.8, (4.1, -2.0, 0.2), (-0.10, 0.45, 0.3), sides=5, seed=14)    # small right-low
    rocks = [
        ((4.3, 3.6, 3.4), (0.0, -2.6, 0), (0, 0, 0.3), 2),     # big centre-front
        ((3.3, 2.9, 3.0), (-3.5, -2.3, 0), (0, 0, 0.8), 2),
        ((2.2, 2.0, 1.8), (2.3, -3.4, 0), (0, 0, -0.5), 1),
        ((3.0, 2.8, 2.4), (-4.9, 0.5, 0), (0, 0, 0.2), 2),
        ((3.4, 3.2, 3.0), (4.6, 1.2, 0), (0, 0, 1.1), 2),      # big right rock (front in side view)
        ((3.2, 2.4, 2.3), (1.4, 2.9, 0), (0, 0, 0.4), 1),
        ((2.8, 2.4, 2.2), (-2.2, 2.8, 0), (0, 0, -0.6), 1),
        ((1.2, 1.1, 0.9), (-1.8, -4.3, 0), (0, 0, 0.5), 1),
        ((1.1, 1.0, 0.8), (1.6, -4.4, 0), (0, 0, 1.0), 1),
        ((1.3, 1.2, 1.0), (-5.3, -2.3, 0), (0, 0, 0.3), 1),
        ((1.2, 1.1, 0.9), (5.6, -2.6, 0), (0, 0, 0.7), 1),
        ((1.4, 1.3, 1.1), (-0.4, 4.0, 0), (0, 0, 0.2), 1),
    ]
    for size, loc, rot, sub in rocks:
        a.rock(size, loc, rot, ROCK, subdiv=sub, rough=0.12, facets=14)
    o = a.finish()
    vfx.add(o, "harvest_hit", (0, -3, 4), color=HIT_COLOR)
    vfx.add(o, "harvest_deplete", (0, 0, 0.3))
    vfx.add(o, "ore_glint", (0, -1.8, 6), scale=1.0)
    vfx.add(o, "ore_glint", (3, -1.5, 4.5), scale=0.8)
    out.append(kit.tag(o, "hero", collision="hull", budget=5000,
                       notes="harvest_hit: obsidian chips on the front strike face; harvest_deplete: base burst; "
                             "ore_glint x2: glints on the glossy tall and right crystals. No light (not glowing)."))

    # ---- parts ------------------------------------------------------------
    a = fk.Asset("ObsidianChunk", "R02 Obsidian Chunk", tint_var=0.05)
    crystal(a, 3.8, 3.2, 7.6, (-2.7, 0, 0.9), (0.0, 1.08, 0.15), sides=6, profile=CHUNK, seed=21, closed=True)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=700, notes="big leaning obsidian crystal chunk"))

    a = fk.Asset("ObsidianChunkB", "R02 Obsidian Chunk B", tint_var=0.05)
    crystal(a, 3.1, 2.7, 4.6, (0, 0, 0), (0.12, 0.28, 0.9), sides=5, profile=CHUNK, seed=24, closed=True)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=600, notes="short pointed obsidian crystal"))

    a = fk.Asset("ObsidianHostRock", "R02 Host Rock", tint_var=0.05)
    cracked_slabs(a)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1200, notes="cracked flat host slabs"))

    a = fk.Asset("ObsidianBaseRock", "R02 Base Rock", tint_var=0.05)
    a.rock((1.4, 1.2, 1.0), (0, 0, 0), (0, 0, 0.4), ROCK, subdiv=2, rough=0.12, facets=14)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=300, notes="small base rock scatter"))

    # ---- drops ------------------------------------------------------------
    a = fk.Asset("ObsidianChunkDrop", "R02 Obsidian Chunk", tint_var=0.05)
    crystal(a, 1.1, 1.0, 1.9, (-0.75, 0, 0.25), (0.0, 1.15, 0.0), sides=5, profile=CHUNK, seed=31, closed=True)
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="box", budget=300, notes="obsidian shard pickup"))

    a = fk.Asset("ObsidianChunkDrop2", "R02 Obsidian Chunk 2", tint_var=0.05)
    crystal(a, 1.2, 1.0, 1.6, (0, 0, 0), (0.12, 0.2, 0.2), sides=5, profile=CHUNK, seed=32, closed=True)
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="box", budget=300, notes="short obsidian shard pickup"))

    # ---- depleted ---------------------------------------------------------
    a = fk.Asset("ObsidianNodeDepleted", "R02 Depleted (Base)", tint_var=0.05)
    cracked_slabs(a, small=True, hs=1.2)
    for size, loc, rot in [((1.4, 1.2, 1.0), (-3.7, -2.6, 0), (0, 0, 0.4)),
                           ((1.2, 1.0, 0.8), (3.9, -2.2, 0), (0, 0, 1.0)),
                           ((1.1, 1.0, 0.8), (4.0, 1.9, 0), (0, 0, 0.2))]:
        a.rock(size, loc, rot, ROCK, subdiv=1, rough=0.12, facets=14)
    o = a.finish()
    vfx.add(o, "harvest_deplete", (0, 0, 0.3))
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="harvest_deplete: dust burst at the base when the node is mined out"))
    return out
