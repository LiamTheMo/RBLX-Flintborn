"""W12 row 1: PalisadeWall (Timberwatch walls). Hero, parts and three variants."""
import math

SUBJECT = "PalisadeWall"
ROW = 1
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 180  # the SIDE/REAR cell is the straight-on back of the wall (beams in view)

PALETTE = {
    "w12_wood": ("#8F5A2C", 0.9, 0, 0),
    "w12_tan": ("#C9985A", 0.9, 0, 0),
    "w12_stone": ("#7E7F8C", 0.95, 0, 0),
    "w12_leaf": ("#3F9A2E", 0.9, 0, 0),
    "w12_banner_red": ("#C8202B", 0.8, 0, 0),
    "w12_banner_trim": ("#F2E6D2", 0.8, 0, 0),
    "w12_flower": ("#F6DC6A", 0.85, 0, 0),  # small pale-yellow flowers in the clover tufts
}

WOOD, TAN, STONE, LEAF = "w12_wood", "w12_tan", "w12_stone", "w12_leaf"
RED, TRIM, FLOWER = "w12_banner_red", "w12_banner_trim", "w12_flower"
TAN_OK = "w12_tan is real pale cut wood (sharpened tips, cut tops) and rope, not lighting"
PI = math.pi
TIP_FRAC = 0.21  # tan cone tip = 1/4 of the log height


def _log_xs(n, half):
    if n == 1:
        return [0.0]
    return [-half + 2 * half * i / (n - 1) for i in range(n)]


def _diamond(a, s, loc, depth, mat):
    a.poly_prism([(0, -s), (s, 0), (0, s), (-s, 0)], depth, loc=loc, rot=(PI / 2, 0, 0), mat=mat)


def banner(a, x, y, zb, w=1.6, h=4.2):
    """Swallowtail banner; back face at y, cloth extruded toward -Y, bottom at zb."""
    hw = w / 2
    a.poly_prism([(-hw, 0), (0, 0.7), (0, h), (-hw, h)], 0.15, loc=(x, y, zb),
                 rot=(PI / 2, 0, 0), mat=RED)
    a.poly_prism([(0, 0.7), (hw, 0), (hw, h), (0, h)], 0.15, loc=(x, y, zb),
                 rot=(PI / 2, 0, 0), mat=RED)
    zc = zb + h * 0.56
    f = y - 0.15
    _diamond(a, 0.58, (x, f, zc), 0.05, TRIM)
    _diamond(a, 0.40, (x, f - 0.05, zc), 0.04, RED)
    _diamond(a, 0.18, (x, f - 0.09, zc), 0.04, TRIM)
    a.box((w, 0.05, 0.16), loc=(x, f - 0.025, zb + h - 0.25), mat=TRIM)
    zt = zb + h + 0.08
    a.beam((x - hw - 0.25, y - 0.08, zt), (x + hw + 0.25, y - 0.08, zt), 0.11, sides=6,
           mat=WOOD, end_mat=WOOD)
    a.tube_loop([(x - hw - 0.1, y - 0.08, zt), (x - 0.15, y + 0.05, zt + 0.75),
                 (x + 0.15, y + 0.05, zt + 0.75), (x + hw + 0.1, y - 0.08, zt)],
                0.05, mat=TAN, rseg=4, closed=False)


def stump(a, r, h, loc, rng):
    """Snapped log: short body with a jagged pale broken top."""
    v = a.cyl(r, r * 0.97, h, 8, mat=WOOD, jitter=r * 0.04)
    v += a.cyl(r * 0.95, r * 0.35, 0.55, 6, loc=(0, 0, h), mat=TAN, jitter=0.12, cap=True)
    v += a.cyl(0.16, 0.02, 0.9, 4, loc=(r * 0.45, 0, h + 0.1), rot=(0.2, 0.25, 0), mat=TAN)
    v += a.cyl(0.13, 0.02, 0.6, 4, loc=(-r * 0.4, r * 0.3, h + 0.1), rot=(-0.3, -0.2, 0), mat=TAN)
    a.transform(v, loc, (rng.uniform(-0.05, 0.05), rng.uniform(-0.05, 0.05), rng.uniform(0, PI)))


def wall(a, rng, heights, half=3.75, r=0.55, post_h=10.5, post_x=5.0, post_r=0.8,
         beam_zs=(3.0, 6.0), band_zs=(3.0, 6.0), stumps=None, by=0.56):
    xs = _log_xs(len(heights), half)
    for i, (x, h) in enumerate(zip(xs, heights)):
        y = 0.05 if i % 2 else -0.05
        if stumps and i in stumps:
            stump(a, r, h, (x, y, 0), rng)
        else:
            a.stake(r, h, tip=h * TIP_FRAC, loc=(x, y, 0), sides=8, mat=WOOD, tip_mat=TAN,
                    lean=(rng.uniform(-0.025, 0.025), rng.uniform(-0.02, 0.02)))
    for sx in (-post_x, post_x):
        a.post(post_r, post_h, loc=(sx, 0, 0), sides=8, mat=WOOD, top_mat=TAN, chamfer=0.3)
        for z in band_zs:
            a.rope_rings(post_r, z - 0.25, count=2, thickness=0.2, loc=(sx, 0), mat=TAN)
    for z in beam_zs:
        a.beam((-post_x, by, z), (post_x, by, z), 0.4, sides=7, mat=WOOD, end_mat=WOOD)
    return xs


def clover(a, rng, x, y, rad, flower=False):
    """A raised clover tuft: one lobed clump plus a smaller offset clump, opt. a flower."""
    a.leaf_cluster(rad, loc=(x, y, rad * 0.72), mat=LEAF, lobes=5, squash=1.0, floor=0.0,
                   depth=1.3)
    ang = rng.uniform(0, 2 * PI)
    r2 = rad * 0.62
    a.leaf_cluster(r2, loc=(x + rad * 0.85 * math.cos(ang), y - abs(rad * 0.6 * math.sin(ang)),
                            r2 * 0.6), mat=LEAF, lobes=4, squash=0.8, floor=0.0)
    if flower:
        fx, fy = x - rad * 0.5 * math.cos(ang), y - rad * 0.95
        v = a.cyl(0.03, 0.03, rad * 1.25, 3, mat=LEAF, cap=False)
        v += a.cyl(0.2, 0.17, 0.1, 5, loc=(0, 0, rad * 1.25), mat=FLOWER)
        a.transform(v, (fx, fy, 0), (0, 0, ang))


def grass(a, rng, x, y, n=3):
    for k in range(n):
        ang = k * 2 * PI / n + rng.uniform(-0.4, 0.4)
        a.cyl(0.07, 0.0, rng.uniform(0.6, 0.9), 3,
              loc=(x + 0.12 * math.cos(ang), y + 0.12 * math.sin(ang), 0),
              rot=(0.35 * math.sin(ang), -0.35 * math.cos(ang), ang), mat=LEAF, cap=False)


def dressing(a, rng, rocks, leaves, rubble=(), grasses=()):
    for (x, y, sx, sy, sz) in rocks:
        a.rock((sx * 1.3, sy * 1.25, sz * 1.6), loc=(x, y - 0.12, 0), rot=(0, 0, rng.uniform(0, PI)), mat=STONE,
               subdiv=1, facets=9, rough=0.16, sink=0.1)
    for (x, y, s) in rubble:
        a.rock((s * 1.4, s * 1.2, s * 1.1), loc=(x, y, 0), rot=(0, 0, rng.uniform(0, PI)),
               mat=STONE, subdiv=1, facets=9, sink=0.08)
    for i, (x, y, rad) in enumerate(leaves):
        clover(a, rng, x, y, rad * 1.5, flower=(i % 2 == 1))
    for (x, y) in grasses:
        grass(a, rng, x, y)


def _tag(kit, o, role, collision, budget, notes):
    o["kit_shading_ok"] = TAN_OK
    return kit.tag(o, role, collision=collision, budget=budget, notes=notes)


def build(kit):
    fk = kit.flintkit
    out = []

    # ---------------- HERO ----------------
    a = fk.Asset("PalisadeWall", "W12 PalisadeWall")
    rng = a.rng
    heights = [7.8, 8.9, 7.4, 8.5, 9.1, 7.6, 8.8, 8.1, 9.0, 7.5, 8.4]
    xs = wall(a, rng, heights, post_h=10.0)
    for z in (3.0, 6.0):
        a.rope_band(xs[:2], 0.55, z - 0.15, count=2, thickness=0.14)
        a.rope_band(xs[-2:], 0.55, z - 0.15, count=2, thickness=0.14)
    banner(a, 2.0, -0.6, 3.5)
    dressing(a, rng,
             rocks=[(-5.25, -0.6, 2.1, 1.6, 1.7), (5.3, -0.55, 1.9, 1.6, 1.5),
                    (0.4, -0.75, 1.6, 1.25, 1.2), (-2.9, -0.8, 1.3, 1.05, 0.95)],
             rubble=[(-4.1, -1.1, 0.6), (3.6, -1.05, 0.55), (1.7, -1.1, 0.45)],
             leaves=[(-5.4, -1.0, 0.7), (-4.0, -0.85, 0.55), (-1.7, -0.85, 0.6),
                     (1.6, -0.85, 0.55), (3.0, -0.85, 0.6), (4.4, -0.9, 0.6),
                     (5.6, -1.05, 0.55)],
             grasses=[(-0.7, -1.0), (2.4, -1.15), (-3.4, -1.15)])
    o = a.finish()
    out.append(_tag(kit, o, "hero", "box", 4500,
                    "no vfx. Standard palisade section: 11 sharpened logs, 2 lashed end posts, "
                    "2 rear beams, red banner mesh, boulder + clover/flower foot dressing."))

    # ---------------- PARTS ----------------
    a = fk.Asset("PalisadeLog", "W12 PalisadeLog")
    a.stake(0.6, 8.0, tip=8.0 * TIP_FRAC, sides=8, mat=WOOD, tip_mat=TAN)
    out.append(_tag(kit, a.finish(), "part", "box", 1500, "no vfx. One sharpened log, tan tip."))

    a = fk.Asset("PalisadeBeam", "W12 PalisadeBeam")
    a.beam((-4, 0, 0.4), (4, 0, 0.4), 0.4, sides=7, mat=WOOD, end_mat=WOOD)
    out.append(_tag(kit, a.finish(), "part", "box", 1500, "no vfx. Rear horizontal beam, 8 long."))

    a = fk.Asset("PalisadePost", "W12 PalisadePost")
    a.post(0.8, 10.5, sides=8, mat=WOOD, top_mat=TAN, chamfer=0.3)
    for z in (3.0, 7.5):
        a.rope_rings(0.8, z - 0.25, count=2, thickness=0.2, mat=TAN)
    out.append(_tag(kit, a.finish(), "part", "box", 1500,
                    "no vfx. Thick end post, flat chamfered top, 2 rope bands."))

    a = fk.Asset("PalisadeLashing", "W12 PalisadeLashing")
    pts = []
    for i in range(29):
        t = i / 28.0
        ang = t * 4 * PI
        pts.append((0.9 * math.cos(ang), 0.9 * math.sin(ang), 0.2 + t * 0.45))
    a.tube_loop(pts, 0.3, mat=TAN, rseg=6, closed=False)
    out.append(_tag(kit, a.finish(), "part", "none", 1500, "no vfx. Two-turn rope coil."))

    a = fk.Asset("PalisadeGroundCollar", "W12 PalisadeGroundCollar")
    for k, (sz, ang) in enumerate([(1.15, 0.2), (1.0, 1.8), (1.1, 3.4), (0.95, 4.9)]):
        a.rock((sz * 1.35, sz * 1.25, sz * 1.4), loc=(0.72 * math.cos(ang), 0.72 * math.sin(ang), 0),
               rot=(0, 0, ang), mat=STONE, subdiv=1, facets=9, sink=0.08)
    out.append(_tag(kit, a.finish(), "part", "none", 1500,
                    "no vfx. Ring of 4 chunky stones around a post hole, ~2.4 wide."))

    a = fk.Asset("PalisadeBanner", "W12 PalisadeBanner")
    banner(a, 0, 0.075, 0.0)
    out.append(_tag(kit, a.finish(), "part", "none", 1500,
                    "no vfx. Red swallowtail banner, cream diamond, crossbar + rope loop."))

    # ---------------- VARIANTS ----------------
    a = fk.Asset("PalisadeWallIntact", "W12 PalisadeWallIntact")
    rng = a.rng
    xs = wall(a, rng, [7.6, 8.8, 7.2, 8.4, 9.0, 7.5, 8.6, 7.9, 8.9, 7.4], r=0.58)
    for z in (3.0, 6.0):
        a.rope_band(xs[:2], 0.58, z - 0.15, count=2, thickness=0.14)
        a.rope_band(xs[-2:], 0.58, z - 0.15, count=2, thickness=0.14)
    dressing(a, rng,
             rocks=[(-5.25, -0.6, 2.0, 1.6, 1.6), (5.3, -0.55, 1.9, 1.5, 1.5),
                    (0.3, -0.75, 1.6, 1.25, 1.15), (3.0, -0.8, 1.3, 1.0, 0.9)],
             rubble=[(-3.0, -1.1, 0.55), (1.8, -1.1, 0.45)],
             leaves=[(-5.4, -1.0, 0.65), (-3.9, -0.85, 0.55), (-1.5, -0.85, 0.55),
                     (1.5, -0.85, 0.5), (4.3, -0.9, 0.6), (5.6, -1.05, 0.5)],
             grasses=[(-0.6, -1.0), (2.4, -1.1)])
    out.append(_tag(kit, a.finish(), "variant", "box", 4500,
                    "no vfx. A intact standard wall, no banner."))

    a = fk.Asset("PalisadeWallBroken", "W12 PalisadeWallBroken")
    rng = a.rng
    hs = [8.4, 7.6, 3.4, 2.4, 3.8, 2.0, 2.9, 3.6, 7.2, 8.6, 7.9]
    xs = wall(a, rng, hs, post_h=9.0, beam_zs=(2.2,), band_zs=(2.6, 6.0),
              stumps={2, 3, 4, 5, 6, 7})
    a.beam((-3.0, -0.75, 3.3), (2.4, -1.15, 0.4), 0.38, sides=7, mat=WOOD, end_mat=WOOD)
    a.beam((-2.2, -1.5, 0.4), (0.4, -1.25, 0.4), 0.4, sides=7, mat=WOOD, end_mat=TAN)
    a.stake(0.42, 3.0, tip=0.9, loc=(2.0, -1.5, 0.42), sides=8, mat=WOOD, tip_mat=TAN,
            lean=(0, PI / 2))
    a.tube_loop([(-1.8, -0.55, 3.6), (-1.0, -0.75, 2.4), (-0.2, -0.65, 3.0),
                 (0.5, -0.9, 1.4), (0.9, -1.2, 0.15)], 0.09, mat=TAN, rseg=4, closed=False)
    a.rope_band(xs[:2], 0.55, 2.4, count=2, thickness=0.13)
    a.rope_band(xs[-2:], 0.55, 2.4, count=2, thickness=0.13)
    dressing(a, rng,
             rocks=[(-5.25, -0.6, 2.0, 1.6, 1.6), (5.3, -0.55, 1.9, 1.5, 1.5),
                    (-3.4, -0.9, 1.4, 1.1, 1.0), (3.4, -0.9, 1.5, 1.2, 1.1)],
             rubble=[(-1.2, -1.3, 0.55), (1.2, -1.6, 0.5), (0.0, 0.9, 0.6), (-2.4, 0.9, 0.5)],
             leaves=[(-5.5, -1.05, 0.6), (-4.3, -1.2, 0.5), (-2.4, -1.3, 0.5),
                     (-0.3, -1.4, 0.45), (2.6, -1.4, 0.5), (4.4, -1.1, 0.55),
                     (5.6, -1.1, 0.5), (1.0, 0.9, 0.45)],
             grasses=[(0.6, -1.5), (-3.0, -1.4)])
    out.append(_tag(kit, a.finish(), "variant", "box", 4500,
                    "no vfx. B low/broken wall: snapped stumps, fallen beam, debris."))

    a = fk.Asset("PalisadeWallTall", "W12 PalisadeWallTall")
    rng = a.rng
    hs = [11.2, 10.4, 11.8, 10.7, 11.5, 10.2, 12.0, 10.9, 11.4, 10.5, 11.9, 10.8, 11.3]
    xs = wall(a, rng, hs, half=3.85, r=0.5, post_h=13.0, beam_zs=(3.0, 6.5, 10.0),
              band_zs=(3.0, 9.5))
    a.rope_band(xs[:2], 0.5, 6.35, count=2, thickness=0.12)
    a.rope_band(xs[-2:], 0.5, 6.35, count=2, thickness=0.12)
    dressing(a, rng,
             rocks=[(-5.25, -0.6, 1.9, 1.5, 1.5), (5.3, -0.55, 1.8, 1.5, 1.4),
                    (1.0, -0.75, 1.4, 1.1, 1.0)],
             leaves=[(-5.5, -1.0, 0.55), (-1.0, -0.85, 0.5), (5.6, -1.0, 0.5)])
    out.append(_tag(kit, a.finish(), "variant", "box", 4500,
                    "no vfx. C tall defensive wall, 13 logs, 3 beam levels."))
    return out
