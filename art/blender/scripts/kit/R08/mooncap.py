"""R08 row 3: Mooncap, two glowing purple mushrooms on a rock ring (resource)."""
import math

from mathutils import Vector

SUBJECT = "Mooncap"
ROW = 3
HERO_AZIMUTH = -22

PALETTE = {
    "r08_rock": ("#6A5A50", 0.95, 0, 0),  # ALL bases, pebbles and ground dirt on every row (single grey-brown rock/soil key)
    "r08_cap_purple": ("#6248B2", 0.7, 0, 0),  # Mooncap cap shells
    "r08_spot_cyan": ("#3FD6E4", 0.3, 0, 0.8),  # Mooncap glowing cyan spots (emissive)
    "r08_stem_cream": ("#DCC08E", 0.85, 0, 0),  # Mooncap stems
    "r08_spore": ("#62D3A0", 0.4, 0, 0.3),  # Mooncap Spore Pod drop (mint, faint glow)
    "r08_leaf_green": ("#6E9A18", 0.7, 0, 0),  # Ancient Root leaf clumps; also tiny moss tufts at Mooncap base
}

CYAN = ["#3FD6E4", "#8FF3FA"]


def _glow(scale=1.0):
    return dict(
        emitters=[{"name": "Glimmer", "texture": "glow_soft", "color": CYAN, "size": [1.0, 1.4],
                   "transparency": [0.6, 1.0], "lifetime": [1.5, 2.5], "rate": 1.5, "speed": [0, 0.2],
                   "spread": 0, "light_emission": 1.0}],
        light={"color": "#3FD6E4", "brightness": 0.9 * scale, "range": 10 * scale, "flicker": False, "pulse": True},
    )


SPORES = dict(emitters=[{"name": "Spores", "texture": "dust_mote", "color": ["#8FF3FA", "#62D3A0"],
                         "size": [0.25, 0.1], "transparency": [0.5, 1.0], "lifetime": [3, 5], "rate": 1.2,
                         "speed": [0.1, 0.3], "spread": 180, "light_emission": 0.8, "shape": [6.0, 4.0, 3.0]}],
              light=None)


def _cap(a, ax, ay, cz, under, subdiv=2, jitter=0.05):
    """Faceted flattened dome centred on the origin: equator radii ax/ay, top cz,
    underside squashed to -under. Returns verts (cap-local)."""
    v = a.ico((ax, ay, cz), loc=(0, 0, 0), mat="r08_cap_purple", subdiv=subdiv, jitter=jitter)
    for p in v:
        if p.co.z < 0:
            # flat-ish underside that rises toward the stem: rim overhangs like an umbrella
            r = math.hypot(p.co.x / ax, p.co.y / ay)
            p.co.z = -under * (0.4 + 0.6 * min(1.0, r))
    return v


def _surf(ax, ay, cz, theta, phi):
    """Point and outward normal on the upper ellipsoid (theta from the pole)."""
    p = Vector((ax * math.sin(theta) * math.cos(phi), ay * math.sin(theta) * math.sin(phi), cz * math.cos(theta)))
    n = Vector((p.x / ax ** 2, p.y / ay ** 2, p.z / cz ** 2)).normalized()
    return p, n


def _spots(a, ax, ay, cz, spots):
    """Cyan discs proud of the cap. spots: (theta_deg, phi_deg, radius)."""
    out = []
    for th, ph, r in spots:
        p, n = _surf(ax, ay, cz, math.radians(th), math.radians(ph))
        rot = Vector((0, 0, 1)).rotation_difference(n).to_euler()
        v = a.cyl(r, r * 0.72, 0.32, sides=8 if r > 0.6 else 7, mat="r08_spot_cyan", jitter=0.03)
        a.transform(v, loc=tuple(p - n * 0.1), rot=tuple(rot))
        out += v
    return out


def _mushroom(a, loc, stem_r, stem_h, cap, tilt, spots):
    """Stem (two bulging faceted sections) + tilted cap with spots."""
    x, y = loc
    r0, rm, r1 = stem_r
    h1 = stem_h * 0.4
    a.cyl(r0, rm, h1, sides=8, loc=(x, y, 0), mat="r08_stem_cream", jitter=0.04, cap=False)
    a.cyl(rm, r1, stem_h - h1, sides=8, loc=(x, y, h1 - 0.02), mat="r08_stem_cream", jitter=0.04,
          cap=False, twist=0.2)
    ax, ay, cz, under, zc = cap
    v = _cap(a, ax, ay, cz, under)
    v += _spots(a, ax, ay, cz, spots)
    a.transform(v, loc=(x, y, zc), rot=tilt)


def _ring(a, rx, ry, n, sizes, seed_off=0.0, dirt=True):
    if dirt:
        a.cyl(rx * 0.95, rx * 0.85, 0.35, sides=10, mat="r08_rock", jitter=0.05)
        a.transform(a.bm.verts[-20:], scale=(1, ry / rx, 1)) if False else None
    for i in range(n):
        ang = 2 * math.pi * i / n + seed_off
        s = sizes[i % len(sizes)]
        a.rock((s * 1.1, s, s * 0.75), loc=(rx * math.cos(ang), ry * math.sin(ang), 0),
               rot=(0, 0, ang * 1.7), mat="r08_rock", subdiv=1, facets=12)


BIG_SPOTS = [(8, 200, 1.0), (35, 120, 0.85), (40, 330, 0.75), (55, 250, 0.6), (62, 285, 0.45), (30, 30, 0.55)]
SMALL_SPOTS = [(10, 160, 0.7), (40, 240, 0.5), (45, 320, 0.4), (35, 60, 0.45), (58, 280, 0.35)]


def _dirt(a, rx, ry):
    v = a.cyl(rx, rx * 0.9, 0.3, sides=10, mat="r08_rock", jitter=0.04)
    a.transform(v, scale=(1, ry / rx, 1))


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---- hero
    a = fk.Asset("Mooncap", "R08 Mooncap")
    _dirt(a, 4.0, 3.2)
    _mushroom(a, (-1.2, -0.2), (1.45, 1.4, 1.1), 4.0, (3.75, 3.0, 2.8, 0.75, 4.3),
              (0.08, 0.17, 0.1), BIG_SPOTS)
    _mushroom(a, (2.7, 1.3), (0.8, 0.78, 0.65), 2.6, (2.25, 1.9, 1.6, 0.5, 2.6),
              (0.05, 0.22, -0.3), SMALL_SPOTS)
    for p in [(-3.0, -1.2, 0.35), (-2.6, -1.9, 0.25)]:
        a.leaf_cluster(0.6, loc=p, mat="r08_leaf_green", lobes=6, squash=0.6, floor=0.0)
    ring = [(-4.0, -0.6, 1.9), (-3.0, -2.6, 1.7), (-1.0, -3.3, 2.1), (1.2, -3.0, 1.6), (3.2, -1.8, 1.9),
            (4.3, 0.6, 1.5), (3.4, 2.8, 1.4), (0.8, 3.1, 1.8), (-1.8, 2.9, 1.5), (-3.8, 1.8, 1.7)]
    for i, (x, y, s) in enumerate(ring):
        a.rock((s * 1.15, s, s * 0.8), loc=(x, y, 0), rot=(0, 0, i * 1.3), mat="r08_rock", subdiv=1, facets=12)
    o = a.finish()
    vfx.add(o, "glyph_glow", (-1.2, -0.4, 6.6), **_glow())
    vfx.add(o, "glyph_glow", (2.7, 1.0, 4.0), **_glow(0.6))
    vfx.add(o, "dust", (0, 0, 6.5), scale=0.5, **SPORES)
    vfx.add(o, "harvest_hit", (0, -3, 5), color=["#6248B2", "#3FD6E4"])
    out.append(kit.tag(o, "hero", collision="hull", budget=3000,
                       notes="glyph_glow x2: cyan cap-spot glow + light (big/small cap); dust: faint glowing spores; "
                             "harvest_hit: strike face of the big cap, purple/cyan chips"))

    # ---- parts
    a = fk.Asset("MooncapCapShell", "R08 Mooncap")
    _cap(a, 3.75, 3.0, 2.8, 0.75)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="cap shell without spots"))

    a = fk.Asset("MooncapSpotInsert", "R08 Mooncap")
    v = a.ico((0.8, 0.8, 0.45), loc=(0, 0, 0), mat="r08_spot_cyan", subdiv=1, jitter=0.05)
    for p in v:
        if p.co.z < -0.15:
            p.co.z = -0.15
    o = a.finish()
    vfx.add(o, "glyph_glow", (0, 0, 0.4), **_glow(0.4))
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="glyph_glow: spot glow + light"))

    a = fk.Asset("MooncapStem", "R08 Mooncap")
    a.cyl(1.4, 1.4, 1.4, sides=8, mat="r08_stem_cream", jitter=0.04, cap=False)
    a.cyl(1.4, 1.1, 2.12, sides=8, loc=(0, 0, 1.38), mat="r08_stem_cream", jitter=0.04, twist=0.2)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="cream stem alone"))

    a = fk.Asset("MooncapBase", "R08 Mooncap")
    _dirt(a, 4.0, 3.0)
    a.rock((3.6, 3.0, 2.2), loc=(0.3, 0.2, 0), mat="r08_rock", subdiv=2, facets=14)
    for i, (x, y, s) in enumerate(ring[::2]):
        a.rock((s * 1.1, s, s * 0.7), loc=(x * 0.95, y * 0.9, 0), rot=(0, 0, i), mat="r08_rock", subdiv=1, facets=12)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="rock pile with dirt"))

    # ---- drops
    a = fk.Asset("MooncapDrop", "R08 Mooncap")
    a.cyl(0.5, 0.42, 1.0, sides=7, mat="r08_stem_cream", jitter=0.03, cap=False)
    v = _cap(a, 1.1, 1.0, 0.85, 0.25, subdiv=1, jitter=0.04)
    v += _spots(a, 1.1, 1.0, 0.85, [(20, 230, 0.32), (50, 320, 0.26)])
    a.transform(v, loc=(0, 0, 1.25), rot=(0.1, 0.15, 0))
    o = a.finish()
    vfx.add(o, "glyph_glow", (0, -0.4, 2.0), **_glow(0.3))
    out.append(kit.tag(o, "drop", collision="box", budget=300, notes="glyph_glow: faint spot glow on the pickup"))

    a = fk.Asset("SporePod", "R08 Mooncap")
    v = a.ico((0.7, 0.7, 1.1), loc=(0, 0, 0), mat="r08_spore", subdiv=1, jitter=0.05)
    for p in v:
        if p.co.z > 0:
            k = 1 - 0.55 * p.co.z / 1.1
            p.co.x *= k
            p.co.y *= k
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="box", budget=300, notes="mint spore pod pickup (faint emissive)"))

    # ---- depleted
    a = fk.Asset("MooncapDepleted", "R08 Mooncap")
    _dirt(a, 4.0, 3.2)
    a.cyl(1.45, 1.3, 1.6, sides=8, loc=(-1.2, -0.2, 0), mat="r08_stem_cream", jitter=0.05)
    a.cyl(0.8, 0.72, 1.1, sides=8, loc=(2.2, 1.0, 0), mat="r08_stem_cream", jitter=0.05)
    for i, (x, y, s) in enumerate(ring):
        a.rock((s * 1.1, s, s * 0.7), loc=(x, y, 0), rot=(0, 0, i * 1.3), mat="r08_rock", subdiv=1, facets=12)
    o = a.finish()
    vfx.add(o, "harvest_deplete", (0, 0, 0.5))
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="harvest_deplete: burst at the base centre when the node is used up"))
    return out
