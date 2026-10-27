"""W02 Cliffs, Ledges & Terrain Modules: MCP builders (see kit_mcp.py for the shared tools).

    import importlib, w02; importlib.reload(w02); w02.cliff_row()
"""
import math
import random

from mathutils import Vector

import kit_mcp as K
import w01

SHEET = "W02"
ROCK, ROCK_COOL, ROCK_BASE = "w02_rock", "w02_rock_cool", "w02_rock_base"
GRASS, GRASS_SUN, DIRT = "w02_grass", "w02_grass_sun", "w02_dirt"
BUSH, BUSH_YOUNG = "w02_bush", "w02_bush_young"
CONNECTOR, PATH = "w02_connector", "w02_path"
PETAL, POLLEN, BERRY = "w02_petal", "w02_pollen", "w02_flower_red"


def palette():
    # Calibrated against the master sheet with kit_mcp.calibrate() (see w01.palette()).
    K.set_colour(ROCK, "#8F8381")
    K.set_colour(ROCK_COOL, "#7C7886")
    K.set_colour(ROCK_BASE, "#7A706C")
    K.set_colour(GRASS, "#628219", low_spec=True)
    K.set_colour(GRASS_SUN, "#7C951F", low_spec=True)
    K.set_colour(DIRT, "#5A2E12")
    K.set_colour(BUSH, "#244E06", rough=0.85, low_spec=True)
    K.set_colour(BUSH_YOUNG, "#4B750A", rough=0.85, low_spec=True)
    K.set_colour(CONNECTOR, "#55555E", rough=0.8)
    K.set_colour(PATH, "#D9AE7E")
    K.set_colour(PETAL, "#F6F3EA", rough=0.7)
    K.set_colour(POLLEN, "#F2C230", rough=0.7)
    K.set_colour(BERRY, "#C8402F", rough=0.7)


def stone(a, vs, size, loc, seed, cuts=1):
    """W02 stone colouring: warm/cool drift over whole facets, Tint texture, coplanar split, damp foot."""
    z0 = loc[2]
    K.blend(a, vs, ROCK, ROCK_COOL, K.noise_field(scale=0.14, seed=seed), level=0.1, width=0.5, steps=3)
    K.texture(a, vs, amp=0.07, scale=0.22, jitter=0.02, seed=seed)
    if cuts:
        vs = K.refine(a, vs, cuts)
    if size[2] >= 1.5:
        band = min(1.6, size[2] * 0.1)
        K.blend(a, vs, ROCK, ROCK_BASE, lambda c: -(c.z - z0), level=-band * 0.6, width=band, steps=2, jitter=0.15,
                seed=seed)
    return vs


# Prismatic cliff column: a 5-6 sided shaft, nearly vertical, with a short sloped or pointed top.
COLUMN = [(0.0, 1.0, 6), (0.55, 0.97, 6), (0.86, 0.88, 6), (1.0, 0.52, 3)]
COLUMN_FLAT = [(0.0, 1.0, 6), (0.6, 0.97, 6), (1.0, 0.86, 5)]
BUTTRESS = [(0.0, 1.0, 6), (0.45, 0.86, 6), (0.8, 0.5, 4), (1.0, 0.12, 2)]


def column(a, x, y, w, d, h, seed, rings=COLUMN, rot=0.0, lean=(0.0, 0.0), cuts=0):
    size = (w, d, h)
    vs = K.hull_rock(a, size, loc=(x, y, 0), seed=seed, mat=ROCK, rings=rings, jitter=0.04, rot=rot, lean=lean)
    return stone(a, vs, size, (x, y, 0), seed, cuts=cuts)


def cliff_face(a, p0, p1, h, seed, depth=3.2, wmin=2.6, wmax=4.2, hmin=0.84, hmax=1.08, out=0.0):
    """Columns standing side by side along the segment p0 -> p1 (outside on the right), heights
    varying, as the cliff body's front and sides."""
    rng = random.Random(seed)
    p0, p1 = Vector(p0), Vector(p1)
    dv = p1 - p0
    L = dv.length
    dv.normalize()
    nrm = Vector((dv.y, -dv.x))
    ang = math.atan2(dv.y, dv.x)
    t = 0.0
    while t < L - 0.8:
        w = min(rng.uniform(wmin, wmax), L - t + 0.8)
        c = p0 + dv * (t + w / 2) + nrm * (out - depth * 0.3 + rng.uniform(-0.3, 0.3))
        hh = h * rng.uniform(hmin, hmax)
        column(a, c.x, c.y, w * 1.12, depth, hh, rng.randrange(1 << 20), rot=ang,
               rings=COLUMN if rng.random() < 0.6 else COLUMN_FLAT, lean=(rng.uniform(-0.04, 0.04), 0.0))
        t += w * 0.86


def buttresses(a, p0, p1, h, seed, n=3, out=1.4):
    """Shorter pointed columns leaning on the foot of a face."""
    rng = random.Random(seed)
    p0, p1 = Vector(p0), Vector(p1)
    dv = (p1 - p0)
    L = dv.length
    dv.normalize()
    nrm = Vector((dv.y, -dv.x))
    for k in range(n):
        f = (k + 0.5) / n + rng.uniform(-0.12, 0.12)
        c = p0 + dv * (L * f) + nrm * out
        hh = h * rng.uniform(0.28, 0.5)
        column(a, c.x, c.y, rng.uniform(2.6, 3.6), rng.uniform(2.4, 3.0), hh, rng.randrange(1 << 20), rings=BUTTRESS,
               rot=math.atan2(dv.y, dv.x) + rng.uniform(-0.3, 0.3), lean=(0.0, -0.12))


def body_core(a, W, D, H):
    """The flat-backed core block the columns stand against (hidden, keeps the back clean)."""
    vs = a.box((W - 1.2, D - 1.0, H * 0.96), loc=(0, 0.3, 0), mat=ROCK, base=True)
    return vs


def jag_outline(pts, lip, seed, step=1.5, jit=0.4):
    """Subdivide a CCW outline and push it out by lip with jitter (a ragged overhanging grass edge)."""
    rng = random.Random(seed)
    out = []
    n = len(pts)
    for i in range(n):
        p0, p1 = Vector(pts[i]), Vector(pts[(i + 1) % n])
        dv = p1 - p0
        L = dv.length
        dv.normalize()
        nrm = Vector((dv.y, -dv.x))
        k = max(1, int(L / step))
        for j in range(k):
            q = p0 + dv * (L * j / k) + nrm * (lip + (rng.uniform(-jit, jit) if j else 0))
            out.append((q.x, q.y))
    return out


def bush(a, x, y, z, size, seed, berries=False):
    """A round leafy bush (as on the cliff tops): a lobed dome of foliage ringed and topped with broad
    rounded leaves, the outer ones older and darker, the top ones young and lighter."""
    rng = random.Random(seed)
    v = a.leaf_cluster(size * 0.62, loc=(x, y, z + size * 0.3), mat=BUSH, lobes=7, squash=1.0, facets=1,
                       floor=z)
    K.texture(a, v, amp=0.06, scale=1.2, seed=seed)
    n = 9
    for k in range(n):
        t = 2 * math.pi * k / n + rng.uniform(-0.25, 0.25)
        up = k % 3 == 0
        r = size * (0.35 if up else 0.55)
        base = (x + math.cos(t) * r * 0.5, y + math.sin(t) * r * 0.5, z + size * (0.62 if up else 0.32))
        K.leaf(a, base, size * 0.55, size * 0.45, BUSH_YOUNG if up else K.mix_key(BUSH, BUSH_YOUNG, 0.5), yaw=t,
               pitch=rng.uniform(-0.05, 0.25) if up else rng.uniform(-0.15, 0.2), fold=0.2, curl=0.35,
               thick=0.05 * size, shape="round")
    if berries:
        for k in range(3):
            t = rng.uniform(0, 6.28)
            a.ico(size * 0.11, loc=(x + math.cos(t) * size * 0.5, y + math.sin(t) * size * 0.5, z + size * 0.6),
                  mat=BERRY)


def grass_top(a, outline, z, seed, lip=0.45, grass=0.3, dirt=0.32, bushes=(), stones=(), flowers=()):
    """The Grass Top Lip: a thin grass slab with a ragged overhanging edge over a thin dirt band,
    sunlit and shaded grass patches blended across it, round bushes, small stones and flowers."""
    o = jag_outline(outline, lip, seed)
    dv = a.poly_prism(o, dirt, loc=(0, 0, z - dirt), mat=DIRT)
    gv = a.poly_prism(o, grass, loc=(0, 0, z), mat=GRASS)
    K.tag_part(a, gv, f"grass_{seed}")
    gv = K.refine(a, K.part(a, f"grass_{seed}"), 2)
    K.blend(a, gv, GRASS, GRASS_SUN, K.noise_field(scale=0.18, seed=seed), level=0.05, width=0.5, steps=3)
    K.texture(a, gv, amp=0.05, scale=0.4, seed=seed)
    top = z + grass
    for i, (x, y, s, b) in enumerate(bushes):
        bush(a, x, y, top - 0.1, s, seed + 10 + i, berries=b)
    for i, (x, y, s) in enumerate(stones):
        v = K.pebble(a, (s, s * 0.85, s * 0.6), (x, y, top - 0.05), seed + 40 + i, ROCK)
        K.texture(a, v, amp=0.08, scale=0.5, seed=seed + i)
    for i, (x, y) in enumerate(flowers):
        K.daisy(a, (x, y, top + 0.35), 0.32, seed + 60 + i, PETAL, POLLEN, petals=6)
    return o


def back_connector(a, W, H, y=0.0, x=0.0):
    """Flat Back Connector: a dark slab with notched tabs so modules butt together cleanly."""
    a.box((W, 0.6, H), loc=(x, y, 0), mat=CONNECTOR, base=True)
    for k in range(3):
        zc = H * (0.2 + 0.3 * k)
        for side in (-1, 1):
            a.box((0.5, 0.6, 1.1), loc=(x + side * (W / 2 + 0.25), y, zc), mat=CONNECTOR, base=True)


# ---------------------------------------------------------------- Row 1: Cliff Wall
def footprint(W, D, shape="straight"):
    """CCW plan outline; the back edge (y = +D/2) is the flat connector side."""
    hw, hd = W / 2, D / 2
    if shape == "inner":     # front steps back on the right: a concave (inner) corner
        return [(-hw, -hd), (-W * 0.02, -hd), (-W * 0.02, -hd + D * 0.38), (hw, -hd + D * 0.38), (hw, hd), (-hw, hd)]
    if shape == "outer":     # front-right corner cut: a convex (outer) corner facing out
        return [(-hw, -hd), (hw - D * 0.45, -hd), (hw, -hd + D * 0.45), (hw, hd), (-hw, hd)]
    return [(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)]


def cliff_body(a, W=18.0, D=12.0, H=13.0, seed=1101, shape="straight", buttress=True):
    """The Cliff Wall Body: a flat-backed core with tall prismatic columns along its front and sides
    and shorter pointed buttresses leaning on the foot of the front."""
    pts = footprint(W, D, shape)
    inset = [(x * 0.93, y * 0.93 + 0.2) for x, y in pts]
    core = a.poly_prism(inset, H * 0.95, loc=(0, 0, 0), mat=ROCK)
    stone(a, core, (W, D, H), (0, 0, 0), seed, cuts=0)
    n = len(pts)
    for i in range(n):
        p0, p1 = pts[i], pts[(i + 1) % n]
        if abs(p0[1] - D / 2) < 1e-3 and abs(p1[1] - D / 2) < 1e-3:
            continue                                   # the back stays flat for the connector
        cliff_face(a, p0, p1, H, seed + 17 * i)
        if buttress and p0[1] < -D / 2 + D * 0.4 and p1[1] < -D / 2 + D * 0.4:
            buttresses(a, p0, p1, H, seed + 31 * i, n=2 if (Vector(p1) - Vector(p0)).length < 10 else 3)
    return pts


def cliff_assembly(a, W=18.0, D=12.0, H=13.0, seed=1101, shape="straight", connector=True):
    pts = cliff_body(a, W, D, H, seed, shape)
    rng = random.Random(seed)
    hw, hd = W / 2, D / 2
    grass_top(a, [(x * 0.97, y * 0.97) for x, y in pts], H - 0.15, seed + 5,
              bushes=[(-hw * 0.72, -hd * 0.35, 2.1, False), (-hw * 0.35, hd * 0.6, 1.7, False),
                      (hw * 0.55, hd * 0.5, 2.0, True), (hw * 0.78, -hd * 0.6, 1.5, False), (hw * 0.05, hd * 0.75, 1.4, False)],
              stones=[(-hw * 0.1, hd * 0.2, 1.2), (hw * 0.2, -hd * 0.45, 0.8), (-hw * 0.6, hd * 0.1, 0.7)],
              flowers=[(rng.uniform(-hw, hw) * 0.6, rng.uniform(-hd, hd) * 0.6) for _ in range(3)])
    if connector:
        back_connector(a, W * 0.9, H * 0.92, y=hd + 0.05)
    # grass patches and dressing at the foot of the front
    for k, (cx, w) in enumerate(((-hw * 0.7, 5.0), (hw * 0.1, 4.0), (hw * 0.75, 4.5))):
        cy = -hd - 1.6
        patch = [(cx - w / 2, cy - 1.8), (cx + w / 2, cy - 1.8), (cx + w / 2, cy + 2.2), (cx - w / 2, cy + 2.2)]
        sv = a.poly_prism(jag_outline(patch, 0.0, seed + 7 + k, step=1.2, jit=0.5), 0.12, loc=(0, 0, 0), mat=GRASS)
        K.texture(a, sv, amp=0.05, scale=0.5, seed=seed + k)
    for k in range(4):
        x = -hw + W * (k + 0.5) / 4 + rng.uniform(-1.5, 1.5)
        bush(a, x, -hd - 2.2 + rng.uniform(-0.6, 0.6), 0.1, rng.uniform(0.9, 1.3), seed + 70 + k)
    for k in range(4):
        x = rng.uniform(-hw - 1, hw + 1)
        v = K.pebble(a, (1.0, 0.9, 0.6), (x, -hd - rng.uniform(1.8, 3.2), 0.05), seed + 90 + k, ROCK)


CLIFF_NOTES = {
    "CliffWall": "repeatable tall cliff chunk: prismatic rock columns of varying height along the front and sides, "
                 "pointed buttresses at the foot, a thin grass top lip over a dirt band with bushes, stones and "
                 "flowers, a grass skirt at the foot, a flat back connector for tiling",
    "CliffWallBody": "cliff wall body alone: flat-backed core with prismatic columns and buttresses",
    "CliffWallGrassTop": "grass top lip alone: thin ragged grass slab over a dirt band, bushes, stones, flowers",
    "CliffWallBackConnector": "flat back connector: dark slab with notched tabs",
    "CliffWallStraight": "A. Straight: straight front",
    "CliffWallInnerCorner": "B. Inner Corner: the front steps back into a concave corner",
    "CliffWallOuterCorner": "C. Outer Corner: the front-right corner is cut into a convex corner",
}


def cliff_row(render=True):
    palette()
    W, D, H = 18.0, 12.0, 13.0
    hw, hd = W / 2, D / 2
    specs = [("CliffWall", "hero", lambda a: cliff_assembly(a, W, D, H, 1101), 6000, "precise"),
             ("CliffWallBody", "part", lambda a: cliff_body(a, W, D, H, 1101), 3500, "hull"),
             ("CliffWallGrassTop", "part", lambda a: grass_top(a, [(x * 0.97, y * 0.97) for x, y in footprint(W, D)], 0.5,
                                                              1106, bushes=[(-hw * 0.7, -hd * 0.3, 1.5, False),
                                                                            (hw * 0.55, hd * 0.5, 1.4, True)],
                                                              stones=[(-hw * 0.1, hd * 0.2, 1.2)],
                                                              flowers=[(2.0, -1.0), (-3.0, 2.0)]), 2000, "box"),
             ("CliffWallBackConnector", "part", lambda a: back_connector(a, W * 0.9, H * 0.92), 300, "box"),
             ("CliffWallStraight", "variant", lambda a: cliff_assembly(a, 15.0, 11.0, 12.5, 1201), 6000, "precise"),
             ("CliffWallInnerCorner", "variant", lambda a: cliff_assembly(a, W, D, H, 1301, "inner"), 6000, "precise"),
             ("CliffWallOuterCorner", "variant", lambda a: cliff_assembly(a, W, D, H, 1401, "outer"), 6000, "precise")]
    objs = [K.mk(SHEET, n, fn, subject="CliffWall", role=r, notes=CLIFF_NOTES[n], budget=b, collision=c)
            for n, r, fn, b, c in specs]
    out = {"stats": K.stats(objs), "problems": K.check(objs)}
    if render:
        out["compare"] = K.render_row(SHEET, "cliff_wall", 1, "CliffWall", objs, vfx=True, SIDE_AZIMUTH=115,
                                      HERO_ELEVATION=26)
    return out
