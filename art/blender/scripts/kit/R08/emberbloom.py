"""R08 row 1: Emberbloom, a fire flower resource node on a rock ring."""
import math

import bmesh

SUBJECT = "Emberbloom"
ROW = 1
HERO_AZIMUTH = -22

PALETTE = {
    "r08_ember": ("#F2800F", 0.5, 0, 0.6),  # Emberbloom glowing seedpod, Ember Seed drop (emissive)
    "r08_petal_red": ("#B0121C", 0.6, 0, 0),  # Emberbloom leaves/petals, Red Petal drop
    "r08_rock": ("#6A5A50", 0.95, 0, 0),  # ALL bases, pebbles and ground dirt on every row (single grey-brown rock/soil key)
}


def _poly(a, pts, faces, mat):
    """Closed custom polyhedron from points and face index lists."""
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    fs = [bm.faces.new([vs[i] for i in f]) for f in faces]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    a._finish(vs, mat)
    return vs


def petal(a, length, width, thick, lift, mat="r08_petal_red"):
    """Pointed lozenge petal along +X from the origin, ridge on top, tip curving up."""
    L, W, T = length, width, thick
    pts = [
        (0, 0, 0),                                  # 0 base point
        (L, 0, lift),                               # 1 tip
        (0.45 * L, W / 2, 0.1 * lift),              # 2 left widest
        (0.45 * L, -W / 2, 0.1 * lift),             # 3 right widest
        (0.45 * L, 0, T * 0.55 + 0.1 * lift),       # 4 ridge (top)
        (0.75 * L, 0, T * 0.3 + lift * 0.5),        # 5 ridge near tip
        (0.45 * L, 0, -T * 0.4),                    # 6 keel (bottom)
        (0.75 * L, W * 0.36, lift * 0.45),          # 7 left near tip
        (0.75 * L, -W * 0.36, lift * 0.45),         # 8 right near tip
        (0.15 * L, W * 0.32, 0),                    # 9 left near base
        (0.15 * L, -W * 0.32, 0),                   # 10 right near base
        (0.15 * L, 0, T * 0.35),                    # 11 ridge near base
    ]
    faces = [
        (0, 10, 11), (0, 11, 9), (10, 3, 4, 11), (11, 4, 2, 9),
        (3, 8, 5, 4), (4, 5, 7, 2), (8, 1, 5), (5, 1, 7),
        (0, 9, 6), (0, 6, 10), (9, 2, 6), (10, 6, 3),
        (2, 7, 6), (6, 8, 3), (6, 1, 8), (6, 7, 1),
    ]
    return _poly(a, pts, faces, mat)


def teardrop(a, w, h, z0=0.0, sides=6, mat="r08_ember"):
    """Faceted teardrop: blunt bottom, widest ~40% up, long pointed top."""
    R = w / 2
    rings = [(0.07, 0.35), (0.22, 0.78), (0.44, 1.0), (0.66, 0.74), (0.84, 0.40)]
    pts = [(0, 0, z0)]
    for k, (fz, fr) in enumerate(rings):
        off = (k % 2) * math.pi / sides
        for i in range(sides):
            ang = off + 2 * math.pi * i / sides
            pts.append((R * fr * math.cos(ang), R * fr * math.sin(ang), z0 + h * fz))
    pts.append((0, 0, z0 + h))
    top = len(pts) - 1
    faces = []
    for i in range(sides):
        faces.append((0, 1 + (i + 1) % sides, 1 + i))
    for k in range(len(rings) - 1):
        b, c = 1 + k * sides, 1 + (k + 1) * sides
        for i in range(sides):
            j = (i + 1) % sides
            if k % 2 == 0:   # upper ring is offset forward by half a step
                faces.append((b + i, b + j, c + i))
                faces.append((b + j, c + j, c + i))
            else:            # lower ring offset forward
                faces.append((b + i, b + j, c + j))
                faces.append((b + i, c + j, c + i))
    last = 1 + (len(rings) - 1) * sides
    for i in range(sides):
        faces.append((last + i, last + (i + 1) % sides, top))
    return _poly(a, pts, faces, mat)


def dirt_dish(a, r_out, r_rim, r_in, h_rim, h_in, sides=10, mat="r08_rock"):
    """Flat dirt disc with a raised rim and a dished centre."""
    pts = []
    for (r, z) in ((r_out, 0.0), (r_rim, h_rim), (r_in, h_in)):
        for i in range(sides):
            ang = 2 * math.pi * (i + 0.5) / sides
            pts.append((r * math.cos(ang), r * math.sin(ang), z))
    faces = [tuple(range(sides - 1, -1, -1))]          # bottom
    for k in range(2):
        b, c = k * sides, (k + 1) * sides
        for i in range(sides):
            j = (i + 1) % sides
            faces.append((b + i, b + j, c + j, c + i))
    faces.append(tuple(range(2 * sides, 3 * sides)))   # dished floor
    return _poly(a, pts, faces, mat)


def rock_ring(a, n=10, radius=3.5, seed_off=0.0, k=1.0):
    dirt_dish(a, 3.9 * k, 3.6 * k, 2.6 * k, 0.55, 0.38)
    sizes = [2.3, 1.7, 2.1, 1.6, 2.4, 1.8, 2.0, 1.6, 2.2, 1.9]
    for i in range(n):
        ang = seed_off + 2 * math.pi * i / n + 0.15 * math.sin(i * 2.3)
        s = sizes[i % len(sizes)] * (0.5 + 0.5 * k)
        r = (radius + 0.25 * math.cos(i * 1.7)) * k
        a.rock((s, s * 0.9, s * 0.68), loc=(r * math.cos(ang), r * math.sin(ang), 0),
               rot=(0, 0, ang + 0.4 * i), mat="r08_rock", subdiv=1, facets=12)


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---- hero ---------------------------------------------------------------
    a = fk.Asset("Emberbloom", "R08 Emberbloom")
    rock_ring(a, k=0.8)   # ring tucked under the rosette so the petals overhang it
    # outer tier: 5 low petals, ~32 deg up, reaching past the boulders
    for i in range(5):
        yaw = -math.pi / 2 + 2 * math.pi * i / 5 + math.pi / 5   # one petal points to the back
        vs = petal(a, 4.6, 2.6, 1.2, 0.55)
        a.transform(vs, loc=(0.6 * math.cos(yaw), 0.6 * math.sin(yaw), 1.25),
                    rot=(0, -math.radians(28), yaw))
    # inner tier: 4 steeper petals between the outer ones
    for i in range(4):
        yaw = -math.pi / 2 + 2 * math.pi * i / 4 + math.pi / 4
        vs = petal(a, 3.6, 2.3, 1.1, 0.35)
        a.transform(vs, loc=(0.45 * math.cos(yaw), 0.45 * math.sin(yaw), 1.6),
                    rot=(0, -math.radians(50), yaw))
    teardrop(a, 3.0, 4.6, z0=1.9)
    o = a.finish()
    vfx.add(o, "heat_glow", (0, 0, 4.5))
    vfx.add(o, "embers", (0, 0, 6.0), scale=0.6)
    vfx.add(o, "harvest_hit", (0, -2, 3), color=["#B0121C", "#F2800F"])
    out.append(kit.tag(o, "hero", collision="hull", budget=3000,
                       notes="heat_glow: seedpod glow + orange PointLight; embers: sparks rising off the pod tip; "
                             "harvest_hit: petal/ember chips on the front face; the deplete burst lives on "
                             "EmberbloomDepleted (swapped in when harvested)"))

    # ---- parts --------------------------------------------------------------
    a = fk.Asset("EmberbloomSeedpod", "R08 Emberbloom seedpod")
    teardrop(a, 3.0, 4.5)
    o = a.finish()
    vfx.add(o, "heat_glow", (0, 0, 2.2))
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="heat_glow: seedpod glow + light"))

    a = fk.Asset("EmberbloomLeaf", "R08 Emberbloom leaf")
    vs = petal(a, 4.0, 1.8, 1.0, 0.45)
    a.transform(vs, loc=(-2.0, 0, 0.35))
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="one rosette petal"))

    a = fk.Asset("EmberbloomBase", "R08 Emberbloom base")
    rock_ring(a)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="rock ring with dished dirt centre"))

    # ---- drops --------------------------------------------------------------
    a = fk.Asset("EmberSeed", "R08 Ember Seed drop")
    teardrop(a, 1.2, 1.8)
    o = a.finish()
    vfx.add(o, "embers", (0, 0, 1.2), scale=0.3)
    out.append(kit.tag(o, "drop", collision="box", budget=300, notes="embers: small sparks off the seed"))

    a = fk.Asset("RedPetal", "R08 Red Petal drop")
    vs = petal(a, 1.8, 0.9, 0.6, 0.3)
    a.transform(vs, loc=(-0.9, 0, 0.25), rot=(0, -math.radians(14), 0))
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="box", budget=300, notes="loose petal pickup"))

    # ---- depleted -----------------------------------------------------------
    a = fk.Asset("EmberbloomDepleted", "R08 Emberbloom depleted")
    rock_ring(a)
    o = a.finish()
    vfx.add(o, "harvest_deplete", (0, 0, 0.5))
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="empty rock ring; harvest_deplete: burst at base centre"))
    return out
