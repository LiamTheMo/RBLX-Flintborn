"""R07 row 1: ClayDeposit resource node (orange clay lobes on a soil pad)."""
import math

SUBJECT = "ClayDeposit"
ROW = 1
HERO_AZIMUTH = -22

PALETTE = {
    "r07_clay": ("#D4572B", 0.85, 0, 0),
    "r07_soil": ("#7A5636", 0.95, 0, 0),
    "r07_stone": ("#77737A", 0.9, 0, 0),
}

CLAY_HEX = "#D4572B"
SOIL_HEX = "#7A5636"


def _floor(verts, z=0.0):
    for v in verts:
        if v.co.z < z:
            v.co.z = z


def _pad(a, rx, ry, h, sides=10, rot=0.3, top=0.7):
    """Low irregular faceted soil slab with a chunky sloped rim, base at z=0."""
    v = a.cyl(rx, rx * top, h, sides=sides, mat="r07_soil", jitter=0.16)
    a.transform(v, rot=(0, 0, rot), scale=(1, ry / rx, 1))
    _floor(v)
    return v


def _pebbles(a, spots):
    for (x, y, z, s, r) in spots:
        a.rock((s, s * 0.85, s * 0.7), loc=(x, y, z), rot=(0.2, 0.1, r), mat="r07_stone",
               subdiv=1, rough=0.12, facets=14, sink=0.2)


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---- hero ------------------------------------------------------------------
    a = fk.Asset("ClayDeposit", "R07 ClayDeposit")
    _pad(a, 4.6, 4.1, 1.1)
    lobes = [
        # size, loc (base), rot
        ((4.2, 3.8, 4.3), (-0.5, 0.7, 0.9), (0.1, -0.05, 0.4)),    # main, back-centre-left
        ((3.7, 3.2, 3.0), (1.3, -1.0, 0.6), (-0.1, 0.1, -0.5)),    # front-right big
        ((2.7, 2.3, 2.3), (-1.8, -1.5, 0.6), (0.1, 0.05, 0.9)),    # front-left medium
        ((1.7, 1.6, 1.7), (-2.9, 0.4, 0.7), (0.2, 0.0, 0.3)),      # small left edge
        ((1.7, 1.7, 1.8), (2.5, 1.6, 0.7), (0.0, 0.2, 1.1)),       # small right-back
    ]
    for size, loc, rot in lobes:
        a.rock(size, loc=loc, rot=rot, mat="r07_clay", subdiv=2, rough=0.16, facets=24,
               sink=0.12)
    _pebbles(a, [
        (-4.1, -1.1, 0.15, 1.4, 0.3), (-3.1, -2.9, 0.1, 1.2, 1.0), (-0.4, -3.7, 0.1, 1.3, 0.5),
        (2.7, -3.3, 0.1, 1.2, 2.0), (4.2, -0.6, 0.15, 1.4, 0.7), (3.9, 1.3, 0.2, 1.2, 1.4),
        (-0.3, -2.4, 0.9, 1.1, 0.2), (-2.6, 2.0, 0.9, 1.1, 2.2),
    ])
    o = a.finish()
    vfx.add(o, "harvest_hit", (2.0, -3.2, 2.4), color=[CLAY_HEX, CLAY_HEX])
    vfx.add(o, "harvest_deplete", (0, 0, 0.5), color=[CLAY_HEX, SOIL_HEX])
    out.append(kit.tag(o, "hero", collision="hull", budget=4000,
                       notes="Clay deposit node. harvest_hit: clay chips on the front-right "
                             "lobe strike face; harvest_deplete: clay/soil burst at the base "
                             "centre when it swaps to ClayDepositDepleted. Matte, no glint."))

    # ---- parts -----------------------------------------------------------------
    a = fk.Asset("ClayDepositMainClayLobe", "R07 ClayDeposit part")
    a.rock((4.5, 4.0, 3.8), rot=(0.1, 0, 0.4), mat="r07_clay", subdiv=2, rough=0.14,
           facets=16, sink=0.1)
    out.append(kit.tag(a.finish(), "part", collision="hull", notes="Large clay lobe."))

    a = fk.Asset("ClayDepositClayLobe", "R07 ClayDeposit part")
    v = a.rock((2.6, 2.2, 2.2), rot=(0.15, 0.1, 0.7), mat="r07_clay", subdiv=1, rough=0.1,
               facets=12, sink=0.1)
    out.append(kit.tag(a.finish(), "part", collision="hull", notes="Small wedge clay lobe."))

    a = fk.Asset("ClayDepositSoilBase", "R07 ClayDeposit part")
    _pad(a, 4.0, 3.25, 1.2, rot=0.1)
    _pebbles(a, [(-3.8, -0.6, 0.15, 1.2, 0.4), (-3.0, 1.6, 0.15, 1.0, 1.2),
                 (1.0, -3.0, 0.1, 1.1, 0.8), (3.6, 1.2, 0.15, 1.0, 2.0)])
    out.append(kit.tag(a.finish(), "part", collision="hull", notes="Soil pad with pebbles."))

    # ---- drop ------------------------------------------------------------------
    a = fk.Asset("ClayLump", "R07 ClayDeposit drop")
    a.rock((1.6, 1.5, 1.5), rot=(0.3, 0.2, 0.5), mat="r07_clay", subdiv=2, rough=0.12,
           facets=24, sink=0.08)
    out.append(kit.tag(a.finish(), "drop", collision="none", budget=300,
                       notes="Clay lump pickup."))

    # ---- depleted --------------------------------------------------------------
    a = fk.Asset("ClayDepositDepleted", "R07 ClayDeposit depleted")
    _pad(a, 4.5, 4.0, 1.0)
    for loc, size in (((-1.0, 0.6, 0.85), (3.6, 3.0, 0.9)), ((1.6, -0.6, 0.85), (2.8, 2.4, 0.75))):
        a.rock(size, loc=loc, rot=(0, 0, 0.5), mat="r07_soil", subdiv=1, rough=0.1,
               facets=12, sink=0.4)
    _pebbles(a, [(-4.2, -0.9, 0.15, 1.3, 0.3), (-3.1, -2.9, 0.1, 1.1, 1.0),
                 (3.1, -2.8, 0.1, 1.1, 2.0), (4.2, 0.7, 0.15, 1.3, 0.7),
                 (-2.7, 2.7, 0.15, 1.0, 2.2)])
    o = a.finish()
    o["kit_caption"] = "Depleted (Base)"
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="Harvested state: bare soil pad with pebbles. No VFX."))
    return out
