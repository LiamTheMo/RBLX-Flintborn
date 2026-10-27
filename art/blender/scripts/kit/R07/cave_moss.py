"""R07 row 4: Cave Moss resource node (grey dome rock capped with moss clumps)."""
import math

SUBJECT = "CaveMoss"
ROW = 4
HERO_AZIMUTH = -22

PALETTE = {
    "r07_stone": ("#77737A", 0.9, 0, 0),  # grey purple-tinted rock: pebbles around clay and reed bases, mushroom rock base, moss rock base and depleted bases
    "r07_moss": ("#4A9122", 0.9, 0, 0),  # saturated green moss clumps and moss chunk drop
    "r07_sprout": ("#98C82C", 0.8, 0, 0),  # bright lime sprout leaves
}

MOSS_HEX = "#4A9122"


def _sprout(a, base, leaves, length, spread=0.55, start_az=0.0, mat="r07_sprout"):
    """A fan of pointed elongated leaves from one base point."""
    n = len(leaves) if isinstance(leaves, (list, tuple)) else leaves
    for i in range(n):
        az = start_az + 2 * math.pi * i / n
        tilt = spread if i % 2 == 0 else spread * 0.7
        ln = length * (1.0 if i % 2 == 0 else 0.82)
        d = (math.sin(tilt) * math.cos(az), math.sin(tilt) * math.sin(az), math.cos(tilt))
        c = (base[0] + d[0] * ln * 0.5, base[1] + d[1] * ln * 0.5, base[2] + d[2] * ln * 0.5)
        a.ico((0.08 * length, 0.24 * length, 0.5 * ln), c, (0, tilt, az), mat=mat, subdiv=1)
    # one central upright leaf
    c = (base[0], base[1], base[2] + length * 0.55)
    a.ico((0.08 * length, 0.22 * length, 0.55 * length), c, (0.08, 0.05, start_az + 0.8),
          mat=mat, subdiv=1)


def _rock_base(a, flank):
    a.rock((7.6, 6.0, 4.0), (0, 0, 0), (0, 0, 0.15), "r07_stone", subdiv=3, rough=0.08,
           facets=12, sink=0.4)
    for (x, y, s) in flank:
        a.rock((s, s * 0.9, s * 0.8), (x, y, 0), (0, 0, x), "r07_stone", subdiv=1, rough=0.12,
               facets=8, sink=0.15)


HERO_FLANK = [(-3.2, -2.5, 1.5), (1.9, -2.9, 1.7), (3.5, -0.9, 1.3), (3.3, 1.9, 1.2)]


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---- HERO -------------------------------------------------------------
    a = fk.Asset("CaveMoss", "R07 CaveMoss", seed=7104)
    _rock_base(a, HERO_FLANK)
    # moss clumps: left, centre-back (highest), right
    a.rock((3.6, 3.2, 3.4), (-2.25, 0.35, 1.7), (0, 0, 0.3), "r07_moss", subdiv=3, rough=0.09,
           facets=11, sink=0.3)
    a.rock((3.5, 3.0, 3.4), (0.15, 1.35, 2.1), (0, 0, -0.2), "r07_moss", subdiv=3, rough=0.09,
           facets=11, sink=0.3)
    a.rock((3.4, 3.0, 3.3), (2.3, 0.25, 1.65), (0, 0, 0.5), "r07_moss", subdiv=3, rough=0.09,
           facets=11, sink=0.3)
    # sprouts: front centre crevice, right-back on top of the moss
    _sprout(a, (0.15, -2.0, 2.5), 4, 1.9, spread=0.7, start_az=-1.2)
    _sprout(a, (1.5, 1.15, 4.0), 4, 1.7, spread=0.6, start_az=0.4)
    o = a.finish()
    vfx.add(o, "harvest_hit", (0, -2.5, 3), color=[MOSS_HEX, "#98C82C"])
    vfx.add(o, "harvest_deplete", (0, 0, 0.5), color=[MOSS_HEX, "#77737A"])
    out.append(kit.tag(o, "hero", collision="hull", budget=3500,
                       notes="harvest_hit: moss chips on the centre clump front; "
                             "harvest_deplete: moss/rock burst at the base centre. No glow, no glint."))

    # ---- PARTS ------------------------------------------------------------
    a = fk.Asset("CaveMossMossClump", "R07 CaveMoss", seed=7111)
    a.rock((3.5, 3.2, 2.8), (0, 0, 0), (0, 0, 0.3), "r07_moss", subdiv=3, rough=0.08,
           facets=11, sink=0.12)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="large moss clump"))

    a = fk.Asset("CaveMossMossClumpSmall", "R07 CaveMoss", seed=7112)
    a.rock((2.6, 2.3, 1.9), (0, 0, 0), (0, 0, -0.4), "r07_moss", subdiv=3, rough=0.08,
           facets=12, sink=0.12)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="small moss clump"))

    a = fk.Asset("CaveMossSprout", "R07 CaveMoss", seed=7113)
    _sprout(a, (0, 0, 0), 4, 2.3, spread=0.5, start_az=0.3)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="lime sprout, scatter"))

    a = fk.Asset("CaveMossRockBase", "R07 CaveMoss", seed=7114)
    _rock_base(a, [(-3.2, -2.3, 1.4), (3.4, -1.5, 1.3)])
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="domed rock base with two flanking rocks"))

    # ---- DROP -------------------------------------------------------------
    a = fk.Asset("CaveMossChunk", "R07 CaveMoss", seed=7121)
    a.rock((2.0, 1.6, 1.5), (0, 0, 0), (0, 0, 0.4), "r07_moss", subdiv=2, rough=0.10,
           facets=6, sink=0.08)
    out.append(kit.tag(a.finish(), "drop", collision="box", budget=300,
                       notes="Moss Chunk drop"))

    # ---- DEPLETED ---------------------------------------------------------
    a = fk.Asset("CaveMossDepleted", "R07 CaveMoss", seed=7131)
    _rock_base(a, [(-3.2, -2.4, 1.4), (1.9, -2.8, 1.5), (3.5, 0.8, 1.2)])
    out.append(kit.tag(a.finish(), "depleted", collision="hull", budget=2000,
                       notes="Depleted (Base): bare rock, no moss"))
    return out
