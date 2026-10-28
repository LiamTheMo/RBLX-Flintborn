"""W16 row 2: BlockWall - ruin dry-stone sandstone wall, pier, rubble and ivy."""
import math
import random

SUBJECT = "BlockWall"
ROW = 2
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 90

# w16_sandstone retuned at sheet level per verifier (#CDA877 rendered too orange).
PALETTE = {
    "w16_sandstone": ("#D4B98C", 0.9, 0, 0),
    "w16_stone_grey": ("#8F8D86", 0.95, 0, 0),
    "w16_ivy": ("#3F8A1A", 0.8, 0, 0),
    "w16_soil": ("#7A4A2A", 0.95, 0, 0),
}

SAND, GREY, IVY, SOIL = "w16_sandstone", "w16_stone_grey", "w16_ivy", "w16_soil"
SIZES = (4.0, 2.5, 1.8)
GAP = 0.07


def block(a, along, c, z, L, d, h, rng, mat=SAND):
    """One course block: length L along `along` ('x' or 'y'), depth d, height h,
    bottom at z, centred at c=(x, y) in plan."""
    j = rng.uniform(-0.1, 0.1)
    dd = d + rng.uniform(-0.15, 0.08)
    if along == "x":
        size, loc = (L - GAP, dd, h - GAP), (c[0], c[1] + j, z + h / 2)
    else:
        size, loc = (dd, L - GAP, h - GAP), (c[0] + j, c[1], z + h / 2)
    a.stone_block(size, loc, mat=mat)


def course(a, along, s0, s1, other, z, h, d, rng, first=None):
    """Fill one course from s0 to s1 (along the wall axis) with mixed blocks."""
    s = s0
    L0 = first
    while s1 - s > 0.05:
        L = L0 if L0 else rng.choice(SIZES)
        L0 = None
        rem = s1 - s
        if rem - L < 1.4:
            L = rem if rem <= 4.6 else rem / 2
        mid = s + L / 2
        c = (mid, other) if along == "x" else (other, mid)
        block(a, along, c, z, L, d, h, rng)
        s += L


def wall(a, along, s0, s1, other, z0, h, n, d, rng):
    """n staggered courses (running bond: alternating starting block)."""
    starts = (4.0, 1.8, 2.5, 1.8, 4.0)
    for i in range(n):
        course(a, along, s0, s1, other, z0 + i * h, h, d, rng, first=starts[i % len(starts)])


def pier(a, c, w, z0, hs, rng, cap=(5.5, 1.2)):
    """Square pier at plan centre c: each course two half blocks, alternating."""
    z = z0
    for i, h in enumerate(hs):
        if i % 2 == 0:
            for sx in (-1, 1):
                block(a, "y", (c[0] + sx * w / 4, c[1]), z, w, w / 2, h, rng)
        else:
            for sy in (-1, 1):
                block(a, "x", (c[0], c[1] + sy * w / 4), z, w, w / 2, h, rng)
        z += h
    if cap:
        a.stone_block((cap[0], cap[0], cap[1]), (c[0], c[1], z + cap[1] / 2), mat=SAND,
                      bevel=0.25)
        z += cap[1]
    return z


def tumble(a, rng, loc, size, mat=SAND):
    """A fallen block resting on z=loc[2], yawed and slightly tilted."""
    tx = rng.uniform(-0.25, 0.25)
    rz = rng.uniform(-0.7, 0.7)
    h = 0.5 * (size[2] * math.cos(tx) + size[1] * math.sin(abs(tx)))
    a.stone_block(size, (loc[0], loc[1], loc[2] + h - 0.05), (tx, 0, rz), mat=mat)


def leaf(a, rng, r, loc, axis=None, squash=0.55):
    a.leaf_cluster(r, loc, mat=IVY, lobes=5, squash=squash, axis=axis, floor=0.0)


def ivy_band(a, rng, base, t, n, up, count, sway=0.6, r=(1.1, 1.45), width=0.85):
    """Dense vertical ivy band: base point on the face, t lateral dir, n outward
    normal. Big leaf clumps alternate left/right of a wavy brown stem so the
    band reads as one near-continuous leafy mass ~3 studs wide."""
    pts = []
    k = 8
    for i in range(k + 1):
        f = i / k
        s = math.sin(f * 6.0 + rng.uniform(-0.4, 0.4)) * sway
        pts.append((base[0] + t[0] * s + n[0] * 0.12,
                    base[1] + t[1] * s + n[1] * 0.12,
                    max(0.05, base[2] + f * up)))
    a.tube_loop(pts, 0.11, mat=SOIL, rseg=4, closed=False)
    for i in range(count):
        f = (i + 0.5) / count
        z = base[2] + f * up
        s = math.sin(f * 6.0) * sway
        off = (width if i % 2 == 0 else -width) * rng.uniform(0.6, 1.1)
        loc = (base[0] + t[0] * (s + off) + n[0] * 0.3,
               base[1] + t[1] * (s + off) + n[1] * 0.3, z)
        leaf(a, rng, rng.uniform(*r), loc, axis=n)


def tuft(a, rng, loc, r=1.1):
    a.leaf_cluster(r, loc, mat=IVY, lobes=5, squash=0.85, floor=0.0)


# ---------------------------------------------------------------- hero

def build_hero(fk):
    rng = random.Random(1601)
    a = fk.Asset("BlockWall", "W16 BlockWall")
    H, D = 2.2, 3.5
    # three full courses from the left end to the pier (6.6 tall on the left)
    wall(a, "x", -10.0, 5.5, 0.0, 0.0, H, 3, D, rng)
    # fourth course only on the right part: the wall steps down on the left
    course(a, "x", -3.2, 5.5, 0.0, 3 * H, H, D, rng, first=2.5)
    # small left end cap
    a.stone_block((2.6, 3.9, 0.6), (-8.6, 0.0, 3 * H + 0.3), mat=SAND, bevel=0.18)
    # right corner pier 4.5 x 4.5 x 11 + 1.2 overhanging coping (top 12.2)
    pier(a, (7.75, 0.0), 4.5, 0.0, (H,) * 5, rng)
    # tumbled blocks piled at the front-right base
    tumble(a, rng, (3.0, -3.6, 0), (2.6, 2.5, 2.0))
    tumble(a, rng, (6.2, -4.2, 0), (4.0, 3.0, 2.2))
    tumble(a, rng, (6.0, -4.0, 2.15), (2.6, 2.4, 1.9))
    tumble(a, rng, (9.3, -3.6, 0), (2.0, 2.0, 1.8), GREY)
    tumble(a, rng, (4.6, -6.4, 0), (2.0, 1.8, 1.5))
    tumble(a, rng, (3.4, -3.5, 1.95), (1.9, 1.8, 1.5))
    tumble(a, rng, (8.6, -6.4, 0), (1.5, 1.4, 1.2), GREY)
    tumble(a, rng, (9.2, -3.9, 1.75), (1.8, 1.7, 1.5))
    tumble(a, rng, (1.0, -5.0, 0), (1.3, 1.1, 1.0), GREY)
    # ivy: two dense bands up the front face, one over the pier
    ivy_band(a, rng, (-5.8, -1.75, 0.0), (1, 0, 0), (0, -1, 0), 6.6, 9)
    ivy_band(a, rng, (1.0, -1.75, 0.0), (1, 0, 0), (0, -1, 0), 8.8, 10)
    ivy_band(a, rng, (8.4, -2.25, 0.4), (1, 0, 0), (0, -1, 0), 11.2, 9, r=(1.0, 1.35))
    # small ivy along the top edge and on the pier cap
    for p, r in (((-1.2, -0.9, 8.8), 0.9), ((3.2, -0.8, 8.8), 0.95), ((-8.2, -1.0, 7.2), 0.85),
                 ((6.4, -2.0, 12.2), 0.9), ((9.4, -1.8, 12.1), 0.8)):
        leaf(a, rng, r, p, squash=0.6)
    # grass tufts at the base
    for p in ((-9.4, -2.4, 0), (-7.2, -2.6, 0), (-3.6, -2.5, 0), (-1.2, -2.6, 0), (1.8, -6.6, 0),
              (5.8, -7.2, 0), (7.4, -7.0, 0), (10.4, -2.8, 0), (10.6, -5.6, 0)):
        tuft(a, rng, p, rng.uniform(1.0, 1.3))
    return a.finish()


# ---------------------------------------------------------------- parts

def build_parts(fk):
    out = []
    rng = random.Random(1602)
    a = fk.Asset("BlockWallCoping", "W16 BlockWall")
    for sx in (-1, 1):
        a.stone_block((4.0 - GAP, 3.5, 1.2), (sx * 2.0, 0, 0.6), mat=SAND, bevel=0.22)
    out.append(("BlockWallCoping", a.finish()))
    for name, size in (("BlockWallBlockLarge", (4.0, 3.0, 2.0)),
                       ("BlockWallBlockMedium", (2.5, 3.0, 2.0)),
                       ("BlockWallBlockSmall", (1.8, 2.5, 1.8))):
        a = fk.Asset(name, "W16 BlockWall")
        a.stone_block(size, (0, 0, size[2] / 2), mat=SAND)
        out.append((name, a.finish()))
    # corner: wide 5.5 base block, 4 stacked blocks, cap wider than the stack (9 tall)
    a = fk.Asset("BlockWallCorner", "W16 BlockWall")
    a.stone_block((5.5, 5.5, 1.8), (0, 0, 0.9), mat=SAND, bevel=0.25)
    z = 1.8
    for i in range(4):
        a.stone_block((3.8 + rng.uniform(-0.1, 0.1), 3.8 + rng.uniform(-0.1, 0.1), 1.6 - GAP),
                      (rng.uniform(-0.08, 0.08), rng.uniform(-0.08, 0.08), z + 0.8),
                      (0, 0, rng.uniform(-0.04, 0.04)), mat=SAND)
        z += 1.6
    a.stone_block((4.6, 4.6, 0.8), (0, 0, z + 0.4), mat=SAND, bevel=0.2)
    for p in ((-1.2, -2.1, 7.0), (-1.5, -2.1, 5.4), (-1.0, -2.2, 3.8)):
        a.leaf_cluster(1.05, p, mat=IVY, lobes=5, squash=0.5, axis=(0, -1, 0))
    out.append(("BlockWallCorner", a.finish()))
    return out


# ---------------------------------------------------------------- variants

def build_intact(fk):
    rng = random.Random(1603)
    a = fk.Asset("BlockWallIntact", "W16 BlockWall")
    H = 1.95
    wall(a, "x", -8.0, 8.0, 0.0, 0.0, H, 4, 3.5, rng)
    z = 4 * H
    for i in range(4):
        a.stone_block((4.0 - GAP, 3.9, 1.2), (-6.0 + 4.0 * i, 0, z + 0.6), mat=SAND, bevel=0.22)
    ivy_band(a, rng, (-5.0, -1.75, 0.0), (1, 0, 0), (0, -1, 0), 8.4, 9)
    ivy_band(a, rng, (4.6, -1.75, 0.0), (1, 0, 0), (0, -1, 0), 9.0, 9)
    for p in ((-1.0, -1.0, 9.0), (6.8, -1.2, 9.0)):
        leaf(a, rng, 0.9, p, squash=0.6)
    for p in ((-7.4, -2.4, 0), (-2.0, -2.5, 0), (1.5, -2.5, 0), (7.4, -2.4, 0)):
        tuft(a, rng, p, 1.0)
    return a.finish()


def build_broken(fk):
    rng = random.Random(1604)
    a = fk.Asset("BlockWallBroken", "W16 BlockWall")
    H, D = 1.75, 3.5
    wall(a, "x", -7.0, 7.0, 0.0, 0.0, H, 2, D, rng)        # 3.5 tall all along
    course(a, "x", -7.0, 1.2, 0.0, 2 * H, H, D, rng, first=2.5)  # 5.25 step
    course(a, "x", -7.0, -2.8, 0.0, 3 * H, H, D, rng, first=1.8)  # 7.0 top on the left
    # loose blocks on the steps and at its feet
    tumble(a, rng, (-0.6, 0.1, 3 * H), (1.8, 1.8, 1.3))
    tumble(a, rng, (3.8, -0.2, 2 * H), (2.0, 1.9, 1.4))
    tumble(a, rng, (1.5, -3.4, 0), (2.5, 2.2, 1.7))
    tumble(a, rng, (5.2, -3.2, 0), (1.8, 1.6, 1.4), GREY)
    tumble(a, rng, (-4.2, -3.2, 0), (1.6, 1.5, 1.2))
    tumble(a, rng, (3.3, -5.1, 0), (1.2, 1.1, 0.9))
    ivy_band(a, rng, (-5.4, -1.75, 0.0), (1, 0, 0), (0, -1, 0), 7.0, 7, r=(1.0, 1.3))
    ivy_band(a, rng, (-0.8, -1.75, 0.0), (1, 0, 0), (0, -1, 0), 5.2, 5, r=(1.0, 1.3))
    for p in ((-6.8, -2.4, 0), (-2.4, -2.6, 0), (3.0, -2.6, 0), (6.6, -2.3, 0)):
        tuft(a, rng, p, 1.0)
    return a.finish()


def build_corner(fk):
    """L-shaped corner seen from inside the L: back arm along x, right arm coming
    forward along y, tall 12-stud corner pier at the back-right, short end pier at
    the left end of the back arm."""
    rng = random.Random(1605)
    a = fk.Asset("BlockWallCornerSection", "W16 BlockWall")
    H, D = 2.2, 3.5
    pc = (4.75, 4.75)
    wall(a, "x", -7.0, 2.5, 5.25, 0.0, H, 4, D, rng)          # back arm (to the pier)
    wall(a, "y", -7.0, 2.5, 5.25, 0.0, H, 4, D, rng)          # right arm (to the pier)
    z = 4 * H
    L = 9.5 / 3
    for i in range(3):
        c = -7.0 + L * (i + 0.5)
        a.stone_block((L - GAP, 3.9, 1.0), (c, 5.25, z + 0.5), mat=SAND, bevel=0.2)
        a.stone_block((3.9, L - GAP, 1.0), (5.25, c, z + 0.5), mat=SAND, bevel=0.2)
    top = pier(a, pc, 4.5, 0.0, (2.4,) * 5, rng, cap=(5.7, 1.2))  # 13.2 tall corner pier
    # ivy up the corner pier (front face, inside the L) and on both arms
    ivy_band(a, rng, (pc[0] - 0.8, pc[1] - 2.25, 0.0), (1, 0, 0), (0, -1, 0), 12.0, 11, width=0.7)
    ivy_band(a, rng, (-4.0, 3.5, 0.0), (1, 0, 0), (0, -1, 0), 8.6, 8)
    ivy_band(a, rng, (3.5, -4.0, 0.0), (0, 1, 0), (-1, 0, 0), 8.6, 7)
    leaf(a, rng, 0.9, (pc[0] - 1.6, pc[1] - 1.8, top), squash=0.6)
    for p in ((-6.4, 2.8, 0), (-1.0, 2.8, 0), (2.8, -1.5, 0), (2.8, -6.4, 0), (2.4, 2.4, 0)):
        tuft(a, rng, p, 1.0)
    return a.finish()


TWO_TONE = "soil-brown ivy stems are a different material from cut sandstone (sheet palette)"


def build(kit):
    fk = kit.flintkit
    _tag = kit.tag

    def tag(o, *args, **kw):
        if any(m and SOIL in m.name for m in o.data.materials):
            o["kit_two_tone_ok"] = TWO_TONE
        return _tag(o, *args, **kw)

    kit = type("K", (), {"tag": staticmethod(tag)})
    out = [kit.tag(build_hero(fk), "hero", collision="precise", budget=6000,
                   notes="Ruin block wall, 20x3.5x8.8, corner pier 12.2 tall, tumbled blocks, ivy")]
    for name, o in build_parts(fk):
        out.append(kit.tag(o, "part", collision="box", budget=1500, notes=name))
    out.append(kit.tag(build_intact(fk), "variant", collision="precise", budget=6000,
                       notes="INTACT WALL: full-height wall with coping"))
    out.append(kit.tag(build_broken(fk), "variant", collision="precise", budget=6000,
                       notes="BROKEN / STEPPED: 7 to 3.5 studs, loose blocks"))
    out.append(kit.tag(build_corner(fk), "variant", collision="precise", budget=6000,
                       notes="CORNER SECTION: L-shaped 14x14 with 12-tall corner pier"))
    return out
