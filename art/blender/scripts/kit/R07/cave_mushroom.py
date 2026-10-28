"""R07 row 3: CaveMushroom resource node (three mushrooms among grey cave rocks)."""
import math

SUBJECT = "CaveMushroom"
ROW = 3
HERO_AZIMUTH = -22

PALETTE = {
    "r07_clay": ("#D4572B", 0.85, 0, 0),
    "r07_soil": ("#7A5636", 0.95, 0, 0),
    "r07_stone": ("#77737A", 0.9, 0, 0),
    "r07_reed_stalk": ("#7B9C2C", 0.8, 0, 0),
    "r07_reed_leaf": ("#3A7A1F", 0.8, 0, 0),
    "r07_cattail": ("#D49A60", 0.85, 0, 0),
    "r07_cap": ("#A84526", 0.8, 0, 0),
    "r07_stalk": ("#E0C298", 0.85, 0, 0),
    "r07_moss": ("#4A9122", 0.9, 0, 0),
    "r07_sprout": ("#98C82C", 0.8, 0, 0),
}

CAP, STALK, STONE = "r07_cap", "r07_stalk", "r07_stone"


def _cap(a, width, height, loc, rot=(0, 0, 0), jitter=0.05, under=True):
    """Faceted dome: an icosahedron with its lower part flattened into a flat
    underside, plus a thin cream underside disc just beneath the rim.
    `loc` is the centre of the flat underside; height is from there to the top."""
    # icosahedron rings sit at +/-0.447; flatten at -0.30 -> height = 1.30 rz
    # subdiv-2 sphere flattened at -0.35: height = 1.35 rz, rim ~ 0.94 rx
    rz = height / 1.35
    rx = width / (2 * 0.95)
    vs = a.ico((rx, rx, rz), loc=(0, 0, 0), mat=CAP, subdiv=2, jitter=jitter)
    flat = -0.35 * rz
    for v in vs:
        if v.co.z < flat:
            v.co.z = flat
    a.transform(vs, (loc[0], loc[1], loc[2] - flat), rot)
    if under:
        r = 0.95 * width / 2
        d = a.cyl(r * 0.9, r, 0.36, sides=10, loc=(0, 0, -0.34), mat=STALK, jitter=0.02)
        a.transform(d, loc, rot)


def _stalk(a, r_base, r_top, h, loc, rot=(0, 0, 0), sides=8):
    a.cyl(r_base, r_top, h, sides=sides, loc=loc, rot=rot, mat=STALK, jitter=0.03)


def _rocks(a, rocks):
    for size, loc, rz in rocks:
        a.rock(size, loc=loc, rot=(0, 0, rz), mat=STONE, subdiv=2, facets=16)


MAIN_ROCK = ((4.8, 3.3, 2.6), (0.2, -1.5, 0), 0.15)
RIM_ROCKS = [
    ((1.9, 1.7, 1.6), (-3.1, -1.5, 0), 0.4),
    ((2.0, 1.8, 2.0), (-3.3, 0.6, 0), 1.1),
    ((2.0, 1.8, 1.9), (-1.6, 1.9, 0), 0.3),
    ((2.2, 1.9, 1.9), (1.9, 2.0, 0), 2.0),
    ((1.9, 1.8, 1.9), (3.2, 0.1, 0), 0.8),
    ((1.2, 1.1, 0.9), (3.4, -2.3, 0), 1.6),
    ((1.2, 1.1, 0.8), (-1.9, -2.9, 0), 0.9),
    ((1.6, 1.5, 1.7), (-1.5, -0.7, 0), 2.4),
    ((1.4, 1.3, 1.3), (2.3, -2.7, 0), 0.5),
]

BIG = dict(xy=(0.2, 0.9))
MED = dict(xy=(-2.8, -0.2))
SMALL = dict(xy=(2.9, -1.5))


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---- hero --------------------------------------------------------------
    a = fk.Asset("CaveMushroom", "R07 CaveMushroom", tint_var=0.05)
    _rocks(a, [MAIN_ROCK] + RIM_ROCKS)
    bx, by = BIG["xy"]
    _stalk(a, 1.15, 0.85, 3.8, (bx, by, 0.3))
    _cap(a, 5.2, 2.3, (bx, by, 4.15))
    mx, my = MED["xy"]
    _stalk(a, 0.7, 0.55, 2.1, (mx, my, 0.3), rot=(0, -0.12, 0))
    _cap(a, 3.0, 1.5, (mx - 0.25, my, 2.35), rot=(0, -0.25, 0))
    sx, sy = SMALL["xy"]
    _stalk(a, 0.52, 0.43, 1.5, (sx, sy, 0.35), rot=(0.1, 0.12, 0))
    _cap(a, 2.0, 1.1, (sx + 0.15, sy - 0.1, 1.8), rot=(0.15, 0.3, 0))
    o = a.finish()
    vfx.add(o, "harvest_hit", (1, -2.5, 4.5), color=["#A84526", "#E0C298"])
    vfx.add(o, "harvest_deplete", (0, 0, 0.5))
    out.append(kit.tag(o, "hero", collision="hull", budget=3500,
                       notes="Cave mushroom node. harvest_hit: chips of rust cap at the big cap edge; "
                             "harvest_deplete: burst at the base centre. No dust: spores read as smoke in the render."))

    # ---- parts -------------------------------------------------------------
    a = fk.Asset("CaveMushroomMushroomCap", "R07 Mushroom Cap")
    _cap(a, 5.0, 2.4, (0, 0, 0.22))
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="Big rust dome cap with its cream flat underside."))

    a = fk.Asset("CaveMushroomCapUnderside", "R07 Cap Underside")
    a.cyl(2.1, 2.3, 0.25, sides=10, loc=(0, 0, 0), mat=STALK, jitter=0.03)
    a.cyl(2.3, 1.95, 0.25, sides=10, loc=(0, 0, 0.25), mat=STALK, jitter=0.03)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Thin cream gill disc under the cap."))

    a = fk.Asset("CaveMushroomMushroomStalk", "R07 Mushroom Stalk")
    _stalk(a, 0.95, 0.75, 3.0, (0, 0, 0))
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="Cream faceted tapered stalk."))

    a = fk.Asset("CaveMushroomRockBase", "R07 Rock Base", tint_var=0.05)
    _rocks(a, [((5.6, 4.2, 2.0), (0, 0, 0), 0.15),
               ((1.2, 1.1, 0.9), (-3.6, -0.6, 0), 0.5),
               ((1.0, 0.9, 0.75), (3.5, -0.4, 0), 1.2)])
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="Main grey rock with two small flanking rocks."))

    # ---- drops -------------------------------------------------------------
    a = fk.Asset("CaveMushroomWhole", "R07 Whole Mushroom")
    _stalk(a, 0.42, 0.34, 1.2, (0, 0, 0), sides=7)
    _cap(a, 1.6, 0.85, (0, 0, 1.15), jitter=0.04)
    out.append(kit.tag(a.finish(), "drop", collision="box", budget=300,
                       notes="Whole Mushroom drop: small cap + stalk."))

    a = fk.Asset("CaveMushroomCapDrop", "R07 Mushroom Cap")
    _cap(a, 2.0, 1.0, (0, 0, 0), jitter=0.06, under=False)
    out.append(kit.tag(a.finish(), "drop", collision="box", budget=300,
                       notes="Mushroom Cap drop: loose rust dome."))

    # ---- depleted ----------------------------------------------------------
    a = fk.Asset("CaveMushroomDepleted", "R07 Depleted (Base)", tint_var=0.05)
    _rocks(a, [((5.2, 3.4, 1.6), (0.3, -1.5, 0), 0.15)] +
           [(s, l, r) for s, l, r in RIM_ROCKS])
    _stalk(a, 0.47, 0.44, 1.4, (-0.9, 0.6, 0.6))
    _stalk(a, 0.45, 0.42, 1.0, (1.2, 0.3, 0.9))
    out.append(kit.tag(a.finish(), "depleted", collision="hull", budget=2000,
                       notes="Depleted node: rocks with two cut cream stalk stubs; regrows to CaveMushroom."))
    return out
