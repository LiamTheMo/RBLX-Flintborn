"""R03 row 2: Azurite resource node (hero, parts, drops, depleted)."""
import math
import random

SUBJECT = "Azurite"
ROW = 2
HERO_AZIMUTH = -22

PALETTE = {
    "r03_rock": ("#8C7E78", 0.9, 0, 0),  # Single host-rock colour shared by quartz, azurite and amethyst base rocks, geode shells and all depleted rubble. Warm grey-taupe; the lighter/darker faces are lighting only.
    "r03_azurite": ("#1C8EDB", 0.25, 0, 0.35),  # Azurite crystals and drops. Saturated cyan-leaning cobalt blue, glossy, faint inner glow.
}

ROCK = "r03_rock"
GEM = "r03_azurite"
GEM_FX = ["#8FD8FF", "#1C8EDB"]

# Crystal profile, bottom to top: (height fraction, radius fraction, twist in half-steps)
PROFILE = ((0.0, 0.95, 0), (0.6, 1.0, 0), (0.8, 0.72, 1), (1.0, 0.24, 0))


def crystal(a, r, h, loc, rot, sides=7, sx=1.0, sy=1.0, seed=1, floor=0.0,
            profile=PROFILE, bottom_cap=True):
    """Fat faceted crystal: prism body, two-step blunt faceted point. Built
    straight up from local z=0, then scaled, rotated and placed."""
    import bmesh
    rnd = random.Random(seed)
    bm = a.bm
    jit = [1.0 + rnd.uniform(-0.09, 0.09) for _ in range(sides)]
    rings = []
    for (fz, fr, tw) in profile:
        ring = []
        for j in range(sides):
            ang = 2 * math.pi * (j + 0.5 * tw) / sides
            k = jit[j] if tw == 0 else jit[(j + 1) % sides] * 0.5 + jit[j] * 0.5
            rr = r * fr * k
            ring.append(bm.verts.new((math.cos(ang) * rr * sx, math.sin(ang) * rr * sy, fz * h)))
        rings.append(ring)
    faces = []
    for lo, hi in zip(rings, rings[1:]):
        for j in range(sides):
            n = (j + 1) % sides
            faces.append(bm.faces.new((lo[j], lo[n], hi[n], hi[j])))
    faces.append(bm.faces.new(rings[-1]))
    if bottom_cap:
        faces.append(bm.faces.new(list(reversed(rings[0]))))
    verts = [v for ring in rings for v in ring]
    a.transform(verts, loc, rot)
    for v in verts:
        if v.co.z < floor:
            v.co.z = floor
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return a._finish(verts, GEM, None, 0.0)


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---------------- hero -----------------------------------------------
    a = fk.Asset("AzuriteNode", "R03 Azurite")
    a.tint_var = 0.05  # keep random Tint spread within the 1.25x limit
    # three fat crystals, lower ends buried behind the mound
    crystal(a, 1.8, 7.5, (0.1, 1.15, 0.2), (-0.1, 0.03, 0.15), sides=8, sx=1.08, sy=0.9, seed=3)   # main
    crystal(a, 1.55, 6.0, (-1.1, 0.95, 0.2), (0.02, -0.31, 0.12), sides=8, sx=1.05, sy=0.9, seed=5)   # left
    crystal(a, 1.4, 4.8, (1.2, 0.85, 0.2), (0.3, 0.34, 0.1), sides=8, sx=1.05, sy=0.9, seed=7)      # right lean
    # big low faceted boulder mound fronting the crystals
    a.rock((6.2, 3.6, 4.0), (0.0, -1.5, 0.0), (0, 0, 0.12), ROCK, subdiv=1, rough=0.14, facets=20, sink=0.12)
    # smaller rocks ringing the base (kept inside +/-4 studs)
    a.rock((1.8, 1.8, 1.5), (-3.05, -1.0, 0.0), (0, 0, 0.5), ROCK, subdiv=1, rough=0.14)
    a.rock((1.1, 1.2, 1.0), (-3.45, 0.5, 0.0), (0, 0, 0.9), ROCK, subdiv=1, rough=0.14)
    a.rock((1.6, 1.6, 1.4), (3.1, -1.1, 0.0), (0, 0, -0.4), ROCK, subdiv=1, rough=0.14)
    a.rock((0.75, 0.75, 0.65), (3.6, 0.3, 0.0), (0, 0, 0.3), ROCK, subdiv=1, rough=0.1)
    a.rock((1.6, 1.5, 1.4), (3.05, 1.75, 0.0), (0, 0, 0.8), ROCK, subdiv=1, rough=0.14)
    a.rock((2.6, 1.7, 1.7), (0.1, 2.95, 0.0), (0, 0, 0.2), ROCK, subdiv=1, rough=0.14)
    a.rock((1.5, 1.4, 1.2), (-2.3, 2.5, 0.0), (0, 0, 0.4), ROCK, subdiv=1, rough=0.14)
    a.rock((1.3, 1.2, 1.1), (-3.2, 1.7, 0.0), (0, 0, 1.2), ROCK, subdiv=1, rough=0.14)
    a.rock((1.2, 1.1, 0.9), (2.35, -2.5, 0.0), (0, 0, 0.7), ROCK, subdiv=1, rough=0.14)
    a.rock((1.1, 1.0, 0.8), (-2.2, -2.55, 0.0), (0, 0, 0.2), ROCK, subdiv=1, rough=0.14)
    o = a.finish()
    vfx.add(o, "harvest_hit", (0, -2.5, 3), color=GEM_FX)
    vfx.add(o, "ore_glint", (0, -1.5, 5), scale=0.8, color=["#F2FBFF", "#9ADCFF"])
    vfx.add(o, "dust", (0, 0, 4.5), scale=0.6, color=["#9ADCFF", "#4FB0F0"],
            light={"color": "#4FB4FF", "brightness": 0.7, "range": 10, "flicker": False, "pulse": True})
    out.append(kit.tag(o, "hero", collision="hull", budget=3500,
                       notes="harvest_hit: blue chips on the front boulder/crystal face; "
                             "ore_glint: twinkle on the main gem; dust: blue motes + soft blue "
                             "PointLight for the faint crystal glow."))

    # ---------------- parts ----------------------------------------------
    a = fk.Asset("AzuriteMainCrystal", "R03 Azurite")
    crystal(a, 1.9, 7.0, (0, 0, 0), (0.0, 0.08, 0.35), sides=8, sx=1.08, sy=0.9, seed=3)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1000, notes="main azurite crystal"))

    a = fk.Asset("AzuriteSideCrystal", "R03 Azurite")
    crystal(a, 1.3, 4.6, (0, 0, 0), (0.0, 0.16, 0.5), sides=8, sx=1.05, sy=0.92, seed=7)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=800, notes="side azurite crystal"))

    a = fk.Asset("AzuriteBaseRock", "R03 Azurite")
    a.rock((5.4, 3.8, 3.1), (-0.8, 0, 0), (0, 0, 0.12), ROCK, subdiv=1, rough=0.14, facets=20)
    a.rock((1.6, 1.4, 1.3), (2.9, -0.3, 0), (0, 0, 0.6), ROCK, subdiv=1, rough=0.14)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=1500,
                       notes="large boulder mound plus a small separate satellite rock"))

    # ---------------- drops ----------------------------------------------
    a = fk.Asset("AzuriteCrystalDrop", "R03 Azurite")
    crystal(a, 0.52, 1.75, (-0.7, 0, 0.45), (0.0, math.radians(78), math.radians(-25)),
            sides=6, sx=1.0, sy=0.85, seed=11)
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="box", budget=300, notes="azurite shard lying diagonally"))

    a = fk.Asset("AzuriteCrystalDropB", "R03 Azurite")
    crystal(a, 0.56, 1.4, (-0.25, 0, 0.0), (0.15, math.radians(28), 0.4),
            sides=6, sx=1.0, sy=0.9, seed=13)
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="box", budget=300, notes="azurite shard, tilted upright pose"))

    # ---------------- depleted -------------------------------------------
    a = fk.Asset("AzuriteDepleted", "R03 Azurite")
    a.tint_var = 0.05
    a.rock((4.4, 3.6, 2.6), (0, 0, 0), (0, 0, 0.1), ROCK, subdiv=1, rough=0.14, facets=20)
    a.rock((1.7, 1.5, 1.3), (-2.6, -0.3, 0), (0, 0, 0.5), ROCK, subdiv=1, rough=0.14)
    a.rock((1.5, 1.4, 1.1), (2.65, -0.1, 0), (0, 0, -0.3), ROCK, subdiv=1, rough=0.14)
    o = a.finish()
    vfx.add(o, "harvest_deplete", (0, 0, 0.5), color=["#8C7E78", "#1C8EDB"])
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="Depleted (Base); harvest_deplete burst at the base centre"))
    return out
