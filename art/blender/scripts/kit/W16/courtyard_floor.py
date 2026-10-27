"""W16 row 4: CourtyardFloor -- raised flagstone platform with three front steps,
four corner blocks, stacked side walls, fern/ivy tufts and rubble (32 grid piece)."""
import math
import random

SUBJECT = "CourtyardFloor"
ROW = 4
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 90

PALETTE = {
    "w16_sandstone": ("#CDA877", 0.9, 0, 0),
    "w16_stone_grey": ("#8F8D86", 0.95, 0, 0),
    "w16_ivy": ("#3F8A1A", 0.8, 0, 0),
    "w16_soil": ("#7A4A2A", 0.95, 0, 0),
    # this row's cut stone: the reference row renders a paler, less saturated cream
    # than #CDA877 gives under the kit lights (verifier fix); single base colour
    "w16_paver": ("#CDB590", 0.9, 0, 0),
    # this row's foliage: the sheet ivy renders darker than the reference's bright
    # yellow-green ferns; single base colour for every leaf/frond of this module
    "w16_fern": ("#5AA620", 0.8, 0, 0),
}

S, G, IVY, SOIL = "w16_paver", "w16_stone_grey", "w16_fern", "w16_soil"

RISE = 1.8
DECK = 3 * RISE      # 5.4 deck top
COURSE = DECK / 2    # 2.7 wall course
CORE = DECK - 1.0
HX, HY = 13.5, 16.0  # stone half extents (27 x 32, longer than wide)
WALL = 2.5
STEP_D = 2.8
FRONT_Y = -HY + 3 * STEP_D   # -7.6 front of the deck
STEP_W = 8.0                 # half width of the stairs
IN_X = HX - WALL             # 11 inner face of the side walls
BACK_IN = HY - WALL          # 13.5 inner face of the back wall
CB = 5.2
CX = HX - CB / 2
CORNERS = ((-CX, FRONT_Y + CB / 2), (CX, FRONT_Y + CB / 2), (-CX, HY - CB / 2), (CX, HY - CB / 2))
SOIL_OK = "soil patches are earth, a different material from cut stone"


# ---------------------------------------------------------------- foliage

def fern(a, x, y, z, s=1.0, n=6, rng=None, up=(0.55, 1.05)):
    """Fan of flat pointed fronds radiating up and out from (x, y, z)."""
    rng = rng or a.rng
    yaw0 = rng.uniform(0, 6.28)
    for i in range(n):
        L = s * rng.uniform(2.2, 3.0)
        w = s * rng.uniform(0.5, 0.62)
        pts = [(0, 0), (0.3 * L, -w), (0.68 * L, -0.55 * w), (L, 0), (0.68 * L, 0.55 * w),
               (0.3 * L, w)]
        v = a.poly_prism(pts, 0.08, mat=IVY)
        yaw = yaw0 + i * 6.283 / n + rng.uniform(-0.25, 0.25)
        a.transform(v, (x, y, z + 0.05), (0, -rng.uniform(*up), yaw))


def ivy(a, x, y, z, r=1.0, axis=None, rng=None, lobes=7):
    a.leaf_cluster(r, (x, y, z + 0.4 * r), mat=IVY, lobes=lobes, squash=0.8,
                   floor=max(z, 0.0), axis=axis, seed=(rng or a.rng).randint(0, 99999))


def tuft(a, x, y, z, s=1.0, rng=None, n=6):
    """Big fern fan with an ivy clump at its heart."""
    rng = rng or a.rng
    if s >= 0.8:
        ivy(a, x, y, z, 1.4 * s, rng=rng, lobes=5)
    fern(a, x + rng.uniform(-0.3, 0.3), y + rng.uniform(-0.3, 0.3), z, 1.4 * s, n=n, rng=rng)


def soil_patch(a, x, y, z, r=1.0, rng=None):
    rng = rng or a.rng
    pts = []
    for i in range(7):
        ang = i * 6.283 / 7
        rr = r * rng.uniform(0.6, 1.0)
        pts.append((x + rr * math.cos(ang), y + rr * 0.8 * math.sin(ang)))
    a.poly_prism(pts, 0.06, loc=(0, 0, z), mat=SOIL)


# ---------------------------------------------------------------- stone

def blk(a, sx, sy, sz, x, y, z0, mat=S, rz=0.0, bevel=None, jitter=0.05):
    """Chunky bevelled block sitting on z0."""
    bevel = min(sx, sy, sz) * 0.13 if bevel is None else bevel
    a.box((sx, sy, sz), (x, y, z0 + sz / 2), (0, 0, rz), mat=mat, bevel=bevel, jitter=jitter)


def corner_block(a, x, y, z0, size=CB, h=4.6, cap=1.0):
    blk(a, size, size, h, x, y, z0, bevel=0.4)
    blk(a, size * 0.72, size * 0.72, cap, x, y, z0 + h, bevel=0.22)


def rubble_block(a, x, y, size, rng, mat=S, z0=0.0, tilt=0.25):
    sx = size * rng.uniform(0.85, 1.2)
    sy = size * rng.uniform(0.75, 1.05)
    sz = size * rng.uniform(0.65, 0.95)
    tx = rng.uniform(-tilt, tilt)
    ty = rng.uniform(-tilt * 0.7, tilt * 0.7)
    lift = abs(math.sin(tx)) * sy * 0.5 + abs(math.sin(ty)) * sx * 0.5 + 0.05
    a.box((sx, sy, sz), (x, y, z0 + sz / 2 + lift), (tx, ty, rng.uniform(0, 3.14)),
          mat=mat, bevel=min(sx, sy, sz) * 0.2, jitter=size * 0.05)


def paver(a, x0, x1, y0, y1, z0, top, mat=S, cracked=False, rng=None):
    g = 0.15
    x0, x1, y0, y1 = x0 + g, x1 - g, y0 + g, y1 - g
    h = top - z0
    if not cracked:
        a.box((x1 - x0, y1 - y0, h), ((x0 + x1) / 2, (y0 + y1) / 2, z0 + h / 2),
              mat=mat, bevel=0.3, jitter=0.03)
        return
    xm = (x0 + x1) / 2 + (rng.uniform(-0.6, 0.6) if rng else 0.3)
    f = 0.16
    a.poly_prism([(x0, y0), (xm - 0.5 - f, y0), (xm + 0.4 - f, y1), (x0, y1)], h,
                 loc=(0, 0, z0), mat=S)
    a.poly_prism([(xm - 0.5 + f, y0), (x1, y0), (x1, y1), (xm + 0.4 + f, y1)], h - 0.1,
                 loc=(0, 0, z0), mat=S)
    a.poly_prism([(xm - 0.5 - f, y0), (xm - 0.5 + f, y0), (xm + 0.4 + f, y1),
                  (xm + 0.4 - f, y1)], h - 0.35, loc=(0, 0, z0), mat=G)


def wall_run(a, rng, fixed, lo, hi, along_x, z0, h, lens, thick=WALL, skip=0.0):
    t = lo
    while t < hi - 0.3:
        L = min(rng.choice(lens), hi - t)
        if rng.random() >= skip:
            if along_x:
                blk(a, L - 0.18, thick, h, t + L / 2, fixed, z0)
            else:
                blk(a, thick, L - 0.18, h, fixed, t + L / 2, z0)
        t += L


def steps(a, n=3, skip=()):
    for k in range(n):
        y0 = -HY + STEP_D * k
        depth = FRONT_Y - y0
        for sgn in (-1, 1):
            if (k, sgn) in skip:
                continue
            blk(a, STEP_W - 0.18, depth, RISE, sgn * STEP_W / 2, y0 + depth / 2, RISE * k,
                bevel=0.3)


# ---------------------------------------------------------------- platform

def platform(a, rng, mode):
    """mode: hero | clean | overgrown"""
    a.box((2 * IN_X, BACK_IN - FRONT_Y, CORE), (0, (BACK_IN + FRONT_Y) / 2, CORE / 2 + 0.001),
          mat=S)
    # paver grid: 3 columns x 4 rows of large pavers (~7.3 x 5.3)
    nx, ny = 3, 4
    xs = [-IN_X + i * 2 * IN_X / nx for i in range(nx + 1)]
    ys = [FRONT_Y + j * (BACK_IN - FRONT_Y) / ny for j in range(ny + 1)]
    grey = {(2, 2)} if mode != "clean" else set()
    cracked = {(0, 1), (2, 1)} if mode != "clean" else {(2, 1)}
    for i in range(nx):
        for j in range(ny):
            paver(a, xs[i], xs[i + 1], ys[j], ys[j + 1], CORE, DECK + rng.uniform(-0.1, 0.1),
                  mat=G if (i, j) in grey else S, cracked=(i, j) in cracked, rng=rng)
    # side walls: two stacked courses to the deck, then a raised course on the back half
    for sgn in (-1, 1):
        xc = sgn * (HX - WALL / 2)
        wall_run(a, rng, xc, FRONT_Y, HY, False, 0.0, COURSE, (6.5, 7.5))
        wall_run(a, rng, xc, FRONT_Y + 3.0, HY, False, COURSE, COURSE, (5.0, 6.0))
        blk(a, WALL, 3.0, COURSE, xc, FRONT_Y + 1.5, COURSE)
        wall_run(a, rng, xc, 3.0, HY, False, DECK, 2.4, (4.5, 5.6))
    # back wall raised course: the back corner blocks stand on it (descending profile)
    wall_run(a, rng, HY - WALL / 2, -IN_X, IN_X, True, DECK, 2.4, (5.5, 6.5))
    # back wall
    yc = HY - WALL / 2
    wall_run(a, rng, yc, -IN_X, IN_X, True, 0.0, COURSE, (7.0, 8.0))
    wall_run(a, rng, yc, -IN_X, IN_X, True, COURSE, COURSE, (5.5, 6.5))
    # front wall beside the stairs
    for sgn in (-1, 1):
        for z0 in (0.0, COURSE):
            blk(a, IN_X - STEP_W - 0.15, WALL, COURSE, sgn * (STEP_W + IN_X) / 2,
                FRONT_Y + WALL / 2, z0)
    steps(a)
    for k, (x, y) in enumerate(CORNERS):
        corner_block(a, x, y, DECK + (2.4 if k >= 2 else 0.0))


def foliage(a, rng, mode):
    if mode == "clean":
        for x, y, z, s in ((-9.0, -15.0, 0, 1.0), (13.8, -7.0, 0, 1.1),
                           (-8.0, 12.0, DECK, 0.8), (-14.0, 6.0, 0, 0.9)):
            tuft(a, x, y, z, s, rng)
        return
    big = [(-14.0, -7.5, 0, 1.4), (14.0, -7.0, 0, 1.4),        # front corner feet
           (-8.6, -15.0, 0, 1.2), (8.6, -15.2, 0, 1.2),         # step ends
           (-8.4, -10.5, RISE * 2, 0.9), (8.4, -12.5, RISE, 0.9),
           (-14.0, 15.0, 0, 1.3), (14.0, 15.2, 0, 1.3),         # back corner feet
           (-8.0, -2.5, DECK, 1.0), (8.0, 11.0, DECK, 1.0),     # deck edges by corners
           (-8.2, 11.6, DECK, 1.0), (14.2, 4.0, 0, 1.1),
           (-14.2, -0.5, 0, 1.1), (-12.2, 7.0, DECK + 2.4, 0.8), (-14.0, -12.0, 0, 1.0), (14.2, -11.5, 0, 1.0),
           (10.0, 1.0, DECK, 0.8), (-CX, FRONT_Y + CB / 2, DECK + 5.6, 0.7),
           (CX, HY - CB / 2, DECK + 8.0, 0.6)]
    if mode == "overgrown":
        big += [(-14.2, 9.5, 0, 1.2), (14.2, 10.0, 0, 1.1), (12.2, 8.5, DECK + 2.4, 0.8), (-CX, HY - CB / 2, DECK + 8.0, 0.6),
                ]
    for x, y, z, s in big:
        tuft(a, x, y, z, s, rng)
    gaps = [(-3.7, 0.0), (3.7, 5.3)]
    if mode == "overgrown":
        gaps += [(-3.7, 8.2), (0.0, 13.3)]
    for x, y in gaps:
        fern(a, x, y, DECK, 0.7, n=4, rng=rng)
    soil = [(-3.7, 0.0, DECK + 0.12, 1.1), (3.7, 5.3, DECK + 0.12, 1.0),
            (-11.5, -11.0, 0.01, 2.2), (11.5, -12.0, 0.01, 2.0),
            (-14.5, 3.0, 0.01, 2.0), (14.5, 12.0, 0.01, 1.8)]
    if mode == "overgrown":
        soil += [(3.7, -2.3, DECK + 0.12, 1.1), (-3.7, 8.2, DECK + 0.12, 1.0),
                 (0.0, 13.3, DECK + 0.12, 1.0)]
    for x, y, z, r in soil:
        soil_patch(a, x, y, z, r, rng)


def rubble_foot(a, rng, n):
    spots = [(-11.5, -12.5, 2.8), (-13.0, -15.0, 1.9), (11.8, -13.2, 2.6),
             (13.6, -10.5, 1.8), (-15.0, 9.0, 2.0), (15.0, -2.0, 2.2)]
    for k, (x, y, s) in enumerate(spots[:n]):
        rubble_block(a, x, y, s, rng, mat=G if k == 3 else S)


def build_floor(fk, name, label, mode, seed):
    a = fk.Asset(name, label, seed=seed)
    rng = random.Random(seed)
    platform(a, rng, mode)
    foliage(a, rng, mode)
    rubble_foot(a, rng, 2 if mode == "clean" else 5)
    o = a.finish()
    o["kit_two_tone_ok"] = SOIL_OK
    return o


def build_rubble_heap(fk, seed=416):
    a = fk.Asset("CourtyardFloorRubbleHeap", "W16 CourtyardFloor broken rubble", seed=seed)
    rng = random.Random(seed)
    # surviving raised floor at the back-left: 2 pavers + 1 cracked on a low core
    a.box((10.0, 7.5, CORE), (-6.0, 9.75, CORE / 2 + 0.001), mat=S)
    for (x0, x1, y0, y1, cr) in ((-11.0, -6.0, 6.0, 9.75, False), (-6.0, -1.0, 6.0, 9.75, True),
                                 (-11.0, -6.0, 9.75, 13.5, False)):
        paver(a, x0, x1, y0, y1, CORE, DECK + rng.uniform(-0.1, 0.1), cracked=cr, rng=rng)
    paver(a, -6.0, -1.5, 9.75, 13.2, CORE, CORE + 0.6)          # sunken half paver
    xc = -(HX - WALL / 2)
    wall_run(a, rng, xc, 2.0, HY, False, 0.0, COURSE, (5.5, 6.5))
    wall_run(a, rng, xc, 5.0, HY, False, COURSE, COURSE, (5.5,))
    wall_run(a, rng, HY - WALL / 2, -IN_X, 1.0, True, 0.0, COURSE, (6.0, 7.0))
    wall_run(a, rng, HY - WALL / 2, -IN_X, -4.0, True, COURSE, COURSE, (5.5,))
    corner_block(a, -CX, HY - CB / 2, DECK)
    corner_block(a, 10.0, 12.0, 0.0, size=4.6, h=4.0, cap=0.9)    # toppled to the ground
    # partial stair: left half of the two lower steps
    blk(a, STEP_W, 2 * STEP_D, RISE, -STEP_W / 2, -HY + STEP_D, 0.0, bevel=0.3)
    blk(a, STEP_W - 1.5, STEP_D, RISE, -STEP_W / 2 - 0.5, -HY + STEP_D * 1.5, RISE, bevel=0.3)
    # tumbled heap: 17 big blocks in three layers, peak ~8 high, centred on the floor
    heap = [  # x, y, size, z0
        (-2.5, -2.0, 4.4, 0), (2.5, -4.0, 4.2, 0), (5.0, 1.0, 4.4, 0), (0.5, 3.0, 4.0, 0),
        (8.5, -3.5, 3.8, 0), (9.0, 5.0, 3.6, 0), (-7.0, 1.5, 3.4, 0), (4.0, -9.5, 3.2, 0),
        (11.5, -9.0, 3.0, 0), (-8.0, -7.0, 3.0, 0), (13.0, 1.0, 2.8, 0),
        (0.0, -2.0, 4.0, 3.4), (4.0, -1.5, 3.8, 3.4), (5.5, 3.0, 3.4, 3.2), (-3.5, 1.5, 3.4, 3.0),
        (2.0, -0.5, 3.6, 6.4), (6.5, -4.0, 2.8, 3.2),
        (-1.5, -4.5, 3.2, 3.0), (3.5, 3.0, 3.0, 6.2), (8.5, 0.5, 3.2, 3.2),
    ]
    for k, (x, y, s, z0) in enumerate(heap):
        rubble_block(a, x, y, s, rng, mat=G if k in (7, 16) else S, z0=z0, tilt=0.3)
    for x, y, s in ((-2.0, -11.0, 1.4), (14.5, -4.5, 1.3), (-11.0, -3.0, 1.3), (8.0, -12.5, 1.2)):
        rubble_block(a, x, y, s, rng, mat=G)
    for x, y, z, s in ((-14.0, -6.5, 0, 1.2), (-14.0, 15.0, 0, 1.0), (-8.0, 11.5, DECK, 0.8),
                       (-5.0, -5.5, 0, 1.0), (12.5, 9.0, 0, 1.1), (13.5, -3.5, 0, 0.9),
                       (-10.0, -10.5, 0, 0.9), (7.5, -8.0, 0, 1.0), (-5.0, 5.0, 0, 0.9),
                       (14.0, 15.0, 0, 0.9), (8.0, 1.5, 3.4, 0.8), (-1.5, 2.5, 6.4, 0.7),
                       (1.0, -7.0, 0, 0.9)):
        tuft(a, x, y, z, s, rng)
    for x, y, r in ((0.0, -3.0, 2.4), (7.0, 6.0, 2.2), (-6.0, -2.0, 2.0), (6.0, -11.0, 2.0)):
        soil_patch(a, x, y, 0.01, r, rng)
    o = a.finish()
    o["kit_two_tone_ok"] = SOIL_OK
    return o


# ---------------------------------------------------------------- parts

def build_parts(fk):
    out = []
    a = fk.Asset("CourtyardFloorPaver", "W16 CourtyardFloor paver")
    a.box((4, 4, 1), (0, 0, 0.5), mat=S, bevel=0.22, jitter=0.03)
    out.append((a.finish(), "box", "single 4x4x1 floor paver"))

    a = fk.Asset("CourtyardFloorCrackedPaver", "W16 CourtyardFloor cracked paver")
    paver(a, -2.15, 2.15, -2.15, 2.15, 0.0, 1.0, cracked=True, rng=random.Random(7))
    out.append((a.finish(), "box", "4x4x1 paver split by a fissure with grey fill"))

    a = fk.Asset("CourtyardFloorStepBlock", "W16 CourtyardFloor step block")
    a.box((8, 2.5, 1), (0, 0, 0.5), mat=S, bevel=0.22, jitter=0.03)
    out.append((a.finish(), "box", "long edge step block 8x2.5x1"))

    a = fk.Asset("CourtyardFloorCornerBlock", "W16 CourtyardFloor corner block")
    corner_block(a, 0, 0, 0.0, size=3.5, h=3.3, cap=0.7)
    out.append((a.finish(), "box", "3.5x3.5x4 corner block with inset top"))

    a = fk.Asset("CourtyardFloorRubble", "W16 CourtyardFloor rubble")
    for (sx, sy, sz, x, y, rz) in ((3.5, 3.0, 3.3, 1.8, 0.3, 0.4), (2.5, 2.3, 2.0, -1.9, 1.1, -0.3),
                                   (1.8, 1.7, 1.6, -1.1, -1.9, 0.8)):
        a.box((sx, sy, sz), (x, y, sz / 2), (0, 0, rz), mat=S, bevel=min(sx, sy, sz) * 0.24,
              jitter=0.14 * sz)
    out.append((a.finish(), "hull", "3 chunky chipped rubble blocks 1.8 / 2.5 / 3.5"))

    a = fk.Asset("CourtyardFloorIvy", "W16 CourtyardFloor ivy tuft")
    rng = random.Random(13)
    for x, y, s in ((-1.6, 0.2, 1.2), (1.6, 0.9, 1.0), (0.3, -1.3, 0.95)):
        fern(a, x, y, 0.0, s, n=7, rng=rng, up=(0.75, 1.15))
    ivy(a, -0.6, 0.6, 0.0, 1.3, rng=rng, lobes=7)
    ivy(a, 1.7, -0.6, 0.0, 1.1, rng=rng, lobes=7)
    out.append((a.finish(), "none", "ivy/fern overlay tuft (3 fern fans, 2 ivy clusters)"))
    return out


def build(kit):
    fk = kit.flintkit
    res = []
    hero = build_floor(fk, "CourtyardFloor", "W16 CourtyardFloor", "hero", 401)
    res.append(kit.tag(hero, "hero", collision="precise", budget=8000,
                       notes="32-grid terrain piece: paver deck 5.4 high, 3 front steps "
                             "(1.8 rise), corner blocks, stacked side walls; no VFX"))
    for o, col, note in build_parts(fk):
        res.append(kit.tag(o, "part", collision=col, budget=1500, notes=note))
    for name, mode, seed, cap in (("CourtyardFloorClean", "clean", 402, "CLEAN FLOOR"),
                                  ("CourtyardFloorOvergrown", "overgrown", 403, "OVERGROWN")):
        o = build_floor(fk, name, "W16 " + name, mode, seed)
        res.append(kit.tag(o, "variant", collision="precise", budget=8000, notes=cap))
    o = build_rubble_heap(fk)
    res.append(kit.tag(o, "variant", collision="precise", budget=8000, notes="BROKEN RUBBLE"))
    return res
