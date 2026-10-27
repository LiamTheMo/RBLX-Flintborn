"""W11 row 3: FireLight - campfire with stone ring, rope-bound tripod and
hanging cauldron; parts; basket brazier, lantern post and wall torch."""
import math

SUBJECT = "FireLight"
ROW = 3
HERO_AZIMUTH = -22

PALETTE = {
    "w11_wood": ("#B5702C", 0.9, 0, 0),
    "w11_iron": ("#40444F", 0.6, 0.3, 0),
    "w11_stone": ("#8D9097", 0.95, 0, 0),
    "w11_rope": ("#C99A55", 1, 0, 0),
    "w11_flame": ("#FF8C1A", 0.5, 0, 1.5),
    "w11_glass": ("#FFC23D", 0.4, 0, 1.2),
}

WOOD, IRON, STONE, ROPE, FLAME, GLASS = ("w11_wood", "w11_iron", "w11_stone",
                                         "w11_rope", "w11_flame", "w11_glass")
TAU = math.tau


def _log(a, p1, p2, r=0.3):
    return a.beam(p1, p2, r, sides=6, mat=WOOD, end_mat=WOOD)


def stone_ring(a, radius=4.6, n=10):
    for i in range(n):
        th = TAU * i / n + 0.15
        front = max(0.0, -math.sin(th))          # 1 at the front (-Y)
        s = (0.95 + 0.2 * front) * a.rng.uniform(0.93, 1.07)
        size = (2.9 * s, 2.6 * s, (2.2 + 0.5 * front) * a.rng.uniform(0.95, 1.08))
        a.rock(size, (radius * math.cos(th), radius * math.sin(th), 0),
               (0, 0, th + math.pi / 2 + a.rng.uniform(-0.2, 0.2)), mat=STONE,
               subdiv=2, rough=0.1, facets=16, sink=0.1)


def log_pile(a, n=6, reach=2.4, r=0.5):
    """Star / teepee of crossed logs with small glowing embers low inside."""
    for i in range(n):
        th = TAU * i / n + (0.2 if i % 2 else 0.0)
        c, s = math.cos(th), math.sin(th)
        lift = 0.35 if i % 2 == 0 else 0.6
        _log(a, (reach * c, reach * s, 0.3), (-0.6 * c, -0.6 * s, lift + 0.75), r)
    for i in range(5):
        th = TAU * i / 5 + 0.6
        rr = 0.55 if i else 0.0
        a.ico((0.32, 0.32, 0.22), (rr * math.cos(th), rr * math.sin(th), 0.22),
              mat=FLAME, subdiv=1, jitter=0.15)
    a.ico((0.55, 0.55, 0.3), (0, 0, 0.3), mat=FLAME, subdiv=1, jitter=0.1)


def pot(a, base=(0, 0, 0), handle=True, sc=1.0, rise=1.3):
    """Black cauldron ~2.6 dia x 2.2 tall (x sc), rim lip, bail handle.
    Returns top-of-handle z."""
    out = []
    out += a.cyl(0.75, 1.25, 0.6, sides=10, loc=(0, 0, 0.15), mat=IRON)
    out += a.cyl(1.25, 1.3, 0.55, sides=10, loc=(0, 0, 0.75), mat=IRON)
    out += a.cyl(1.3, 1.0, 0.6, sides=10, loc=(0, 0, 1.3), mat=IRON)
    out += a.torus(1.05, 0.14, loc=(0, 0, 1.92), mat=IRON, seg=12, rseg=4)
    for i in range(3):
        th = TAU * i / 3 + 0.5
        out += a.cyl(0.14, 0.1, 0.25, sides=5, loc=(0.6 * math.cos(th), 0.6 * math.sin(th), 0),
                     mat=IRON)
    top = 1.95
    if handle:
        pts = [(1.1 * math.cos(math.pi * k / 8), 0, 1.85 + 1.0 * math.sin(math.pi * k / 8))
               for k in range(9)]
        pts = [(1.15 * math.cos(math.pi * k / 8), 0, 1.8 + rise * math.sin(math.pi * k / 8))
               for k in range(9)]
        out += a.tube_loop(pts, 0.16, mat=IRON, rseg=5, closed=False)
        for sx in (-1.2, 1.2):
            out += a.ico(0.2, (sx, 0, 1.8), mat=IRON, subdiv=1)
        top = 1.95 + rise
    a.transform(out, base, (0, 0, 0), (sc, sc, sc))
    return base[2] + top * sc


def tripod(a, apex_z=8.3, foot_r=4.8):
    feet = [-168, -12, 90]
    tips = []
    for k, deg in enumerate(feet):
        th = math.radians(deg)
        f = (foot_r * math.cos(th), foot_r * math.sin(th), 0.0)
        # each pole passes a little off-centre so they cross above the bind
        off = (0.18 * math.cos(th + 1.6), 0.18 * math.sin(th + 1.6))
        ap = (off[0], off[1], apex_z)
        d = [ap[i] - f[i] for i in range(3)]
        tip = tuple(f[i] + d[i] * 1.2 for i in range(3))
        _log(a, f, tip, 0.45)
        tips.append(tip)
    a.rope_rings(0.66, apex_z - 0.75, count=4, thickness=0.2, mat=ROPE)
    a.lashing((0, -0.8, apex_z - 0.3), size=0.4, thickness=0.08, mat=ROPE)
    return apex_z - 0.6


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---------------- HERO ----------------
    a = fk.Asset("FireLight", "W11 FireLight", tint_var=0.05)
    stone_ring(a)
    log_pile(a)
    bind_z = tripod(a)
    pot_base = 3.0
    htop = pot(a, (0, 0, pot_base), sc=1.25, rise=1.45)
    a.tube_loop([(0, 0, htop - 0.05), (0, 0, bind_z + 0.1)], 0.08, mat=ROPE, rseg=4,
                closed=False)
    o = a.finish()
    vfx.add(o, "campfire", (0, 0, 0.8), scale=1.1)
    vfx.add(o, "embers", (0, 0, 1.5))
    vfx.add(o, "heat_glow", (0, 0, 0.4), scale=0.3)
    out.append(kit.tag(o, "hero", collision="precise", budget=6000,
                       notes="Campfire: stone ring, log pile with emissive embers, rope-bound "
                             "tripod, hanging cauldron. Sockets: campfire (flame+smoke) in the "
                             "log pile, embers rising, subtle heat_glow at the logs."))

    # ---------------- PARTS ----------------
    a = fk.Asset("FireLightHangingPot", "W11 FireLight part")
    pot(a)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="Cauldron with rim lip and bail handle."))

    a = fk.Asset("FireLightTripodPole", "W11 FireLight part")
    _log(a, (0, 0, 0), (0, 0, 9.0), 0.35)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Single tripod pole 9 x 0.7."))

    a = fk.Asset("FireLightRopeBind", "W11 FireLight part")
    a.rope_rings(0.58, 0.17, count=4, thickness=0.17, gap=0.3, mat=ROPE)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="Rope wrap collar for the tripod apex."))

    a = fk.Asset("FireLightFire", "W11 FireLight part")
    log_pile(a, n=5, reach=1.5, r=0.3)
    o = a.finish()
    vfx.add(o, "campfire", (0, 0, 0.8), scale=1.0)
    vfx.add(o, "embers", (0, 0, 1.3))
    out.append(kit.tag(o, "part", collision="none", budget=1500,
                       notes="Separate fire: crossed logs + emissive embers; campfire socket is "
                             "the flame/smoke, embers socket the sparks."))

    a = fk.Asset("FireLightLogPiece", "W11 FireLight part")
    _log(a, (-1.5, 0, 0.3), (1.5, 0, 0.3), 0.3)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Single firewood log 3 x 0.6."))

    a = fk.Asset("FireLightStoneRing", "W11 FireLight part")
    a.rock((2.2, 2.0, 1.6), (0, 0, 0), (0, 0, 0.3), mat=STONE, subdiv=2, rough=0.1,
           facets=16, sink=0.1)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="One fire-ring stone; place 10 in a circle to make the ring."))

    # ---------------- VARIATIONS ----------------
    # Basket brazier
    a = fk.Asset("FireLightBasketBrazier", "W11 FireLight variant")
    for i in range(3):
        th = TAU * i / 3 - math.pi / 2
        c, s = math.cos(th), math.sin(th)
        _log(a, (1.95 * c, 1.95 * s, 0), (0.95 * c, 0.95 * s, 2.6), 0.26)
    a.cyl(0.75, 0.85, 0.35, sides=12, loc=(0, 0, 1.95), mat=WOOD)
    prof = [(0.8, 2.0), (1.45, 2.55), (1.8, 3.6), (1.9, 5.3)]
    ns = 22
    for i in range(ns):
        th = TAU * i / ns
        c, s = math.cos(th), math.sin(th)
        for (r1, z1), (r2, z2) in zip(prof, prof[1:]):
            a.beam((r1 * c, r1 * s, z1), (r2 * c, r2 * s, z2), 0.2, sides=4,
                   mat=WOOD, end_mat=WOOD, jitter=0.0)
    a.torus(1.72, 0.2, loc=(0, 0, 3.2), mat=IRON, seg=18, rseg=4, squash=1.6)
    a.torus(1.9, 0.2, loc=(0, 0, 4.75), mat=IRON, seg=18, rseg=4, squash=1.6)
    a.cyl(1.6, 1.75, 0.3, sides=12, loc=(0, 0, 4.0), mat=FLAME)
    a.ico((1.3, 1.3, 0.75), (0, 0, 4.25), mat=FLAME, subdiv=1, jitter=0.12)
    for i in range(9):
        th = TAU * i / 9 + 0.3
        rr = 1.15 if i % 2 else 0.8
        a.ico((0.42, 0.42, 0.3), (rr * math.cos(th), rr * math.sin(th), 4.4 + 0.15 * (i % 3)),
              mat=FLAME, subdiv=1, jitter=0.15)
    o = a.finish()
    vfx.add(o, "brazier_fire", (0, 0, 4.9), scale=1.0)
    out.append(kit.tag(o, "variant", collision="box", budget=3000,
                       notes="Slatted wooden brazier on three legs, two iron bands, emissive "
                             "coals; brazier_fire socket is the live flame."))

    # Lantern post
    a = fk.Asset("FireLightLanternPost", "W11 FireLight variant")
    a.box((1.8, 1.8, 0.8), loc=(0, 0, 0), mat=STONE, bevel=0.08, base=True)
    a.box((1.2, 1.2, 0.15), loc=(0, 0, 0.8), mat=IRON, base=True)
    a.box((0.8, 0.8, 8.5), loc=(0, 0, 0.95), mat=WOOD, base=True)
    a.box((3.2, 0.6, 0.6), loc=(1.2, 0, 8.75), mat=WOOD, base=True)
    a.beam((0.4, 0, 6.8), (2.0, 0, 8.8), 0.25, sides=4, mat=WOOD, end_mat=WOOD,
           jitter=0.0)
    lx, ltop = 2.35, 8.75
    a.torus(0.16, 0.05, loc=(lx, 0, ltop - 0.12), rot=(math.pi / 2, 0, 0), mat=IRON,
            seg=8, rseg=3)
    a.cyl(0.08, 0.08, 0.45, sides=5, loc=(lx, 0, ltop - 0.7), mat=IRON)
    lz = ltop - 2.75            # lantern bottom
    a.box((1.2, 1.2, 0.22), loc=(lx, 0, lz), mat=IRON, base=True)
    a.box((0.92, 0.92, 1.25), loc=(lx, 0, lz + 0.22), mat=GLASS, base=True)
    for dx in (-0.5, 0.5):
        for dy in (-0.5, 0.5):
            a.box((0.14, 0.14, 1.25), loc=(lx + dx, 0 + dy, lz + 0.22), mat=IRON,
                  base=True)
    a.box((1.2, 1.2, 0.14), loc=(lx, 0, lz + 1.47), mat=IRON, base=True)
    a.cyl(0.72, 0.12, 0.5, sides=4, loc=(lx, 0, lz + 1.6), rot=(0, 0, math.pi / 4),
          mat=IRON)
    o = a.finish()
    vfx.add(o, "heat_glow", (lx, 0, lz + 0.85), scale=0.8, color=["#FFB347"])
    out.append(kit.tag(o, "variant", collision="box", budget=3000,
                       notes="Wooden lamp post with braced arm and iron lantern (emissive "
                             "glass); heat_glow socket gives the warm lantern light."))

    # Wall torch
    a = fk.Asset("FireLightWallTorch", "W11 FireLight variant")
    a.box((1.0, 0.4, 3.0), loc=(0, 0.45, 0.6), mat=IRON, bevel=0.05, base=True)
    a.cyl(0.3, 0.36, 4.0, sides=7, loc=(0, -0.2, 0), mat=WOOD)
    for bz in (1.5, 2.9):
        a.torus(0.42, 0.1, loc=(0, -0.2, bz), mat=IRON, seg=10, rseg=4)
        a.box((0.22, 0.5, 0.2), loc=(0, 0.2, bz - 0.1), mat=IRON, base=True)
    a.cyl(0.38, 0.72, 0.75, sides=9, loc=(0, -0.2, 3.95), mat=WOOD)
    a.torus(0.68, 0.11, loc=(0, -0.2, 4.68), mat=FLAME, seg=12, rseg=4)
    a.cyl(0.62, 0.62, 0.1, sides=9, loc=(0, -0.2, 4.55), mat=IRON)
    o = a.finish()
    vfx.add(o, "torch_fire", (0, -0.2, 4.8), scale=1.0)
    out.append(kit.tag(o, "variant", collision="none", budget=3000,
                       notes="Wall-mounted torch: flat iron back plate, two iron bands, wooden "
                             "handle, bowl head with glowing rim; torch_fire socket is the flame."))
    return out
