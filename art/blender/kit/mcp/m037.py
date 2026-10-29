"""037 Waterfall Module (references/037.png): a 32 x 32 cliff / waterfall terrain tile. The back half is a tall block
of fat, flat-faced grey rock columns under one lime grass cap; a cyan river channel splits the cap from the back edge,
pinches between rocks, widens into a lip pool and pours over the middle of the cliff face as a broad three-lobed
curtain into a flat cyan pool that fills the front half of the tile edge to edge. At the foot: a white splash disc with
spiky spray, a foam ribbon, foam rings round two big boulders standing in the pool, smaller boulders, two stepped
bush-capped columns either side of the fall and a low grass box with a pine at each front corner. On top: pines, dark
ferns, white / pink / yellow flowers, grey rocks along the channel.

    import importlib, kit_models, m037; importlib.reload(kit_models); importlib.reload(m037); m037.build()

Build frame (studs): front -Y, +X right, ground z 0 (one flat underside). Tile X -16 .. 16, Y -16 .. 16. Levels
(M037_spec.md 2.1, decision 1): pool bed 0.2, pool water 0.26 -> 1.0, foam 1.03 -> 1.08, cap underside 16.9, channel
bed 17.1, channel water 17.16 -> 17.4, grass top 18.0, pine tips about 25.

The cliff block is one closed "cliff solid" built without booleans: the cap's flat tops (left grass, channel bed,
right grass; vertical bank walls between them) over the cap outline A (front Y -1.0), the cap's underside at 16.9
overhanging a narrower core outline B (front Y 0.2, sides X +-14.6) that goes down to the ground, and one flat back
joining face at Y 16. The columns, stepped columns, low boxes, bed slab and rocks are convex closed pieces united one
shell at a time (merge-0 exact unions at the world origin), never with coplanar faces. Pines, leaves and flowers are
separate closed shells set on the finished land; the pool and channel water, the curtain and the foam (disc, ribbon,
rings, patches, splash spikes) are separate closed shells that touch nothing (2D holes cut round every land piece).

Parts (the sheet's Exploded Parts & Assembly, decision 10), each from its own function:
- CliffFallsTopWater (top_water_part): the channel water plate alone.
- CliffFallsTop (top_part): the left grass cap on the upper 3.3 studs of its columns, with its pines, ferns, flowers.
- CliffFallsWall (wall_part): three tall columns in a row, a stepped column in front and a foot boulder.
- CliffFallsCurtain (curtain_part): the three-lobed curtain shell, carrying the curtain sockets.
- CliffFallsFoamRibbon (ribbon_part) / CliffFallsSplashDisc (disc_part, with the splash spikes and the mist socket).
- CliffFallsPool (pool_part): the bed slab with the two big boulders, the water plate and their foam rings.
- CliffFallsRockLarge / RockMedium / RockSmall: reusable rocks (K1, K3, T6 shapes) at the origin.

The hero (CliffFalls, decision 9) is one object: one closed land shell plus closed vegetation, water (m037_water),
curtain (m037_water_fall) and foam (m037_water_foam) shells; the three water keys export as three see-through,
non-colliding water pieces; collision "precise". See M037_spec.md.
"""
import math
import random
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M
import m011
import m012
import m016
import m032
import m034

NUM, TITLE, SHEET = 37, "Waterfall Module", "M037"
OFF = "m037_offset"
PFX = "_m037_"
HERO = "CliffFalls"
TOPW_P, TOP_P, WALL_P = "CliffFallsTopWater", "CliffFallsTop", "CliffFallsWall"
CURT_P, RIB_P, DISC_P, POOL_P = "CliffFallsCurtain", "CliffFallsFoamRibbon", "CliffFallsSplashDisc", "CliffFallsPool"
ROCK_LP, ROCK_MP, ROCK_SP = "CliffFallsRockLarge", "CliffFallsRockMedium", "CliffFallsRockSmall"

GRASS, LIME, LEAF, PINE, BARK = "m037_grass", "m037_leaf_lime", "m037_leaf", "m037_pine", "m037_bark"
PETAL, PINK, POLLEN = "m037_petal", "m037_pink", "m037_pollen"
SOIL, DIRT, ROCK = "m037_soil", "m037_dirt", "m037_rock"
BED, BED_LIGHT = "m037_bed", "m037_bed_light"
WATER, FALL, FOAM = "m037_water", "m037_water_fall", "m037_water_foam"
WATER_KEYS = (WATER, FALL, FOAM)

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low_spec); the comment is the calibration target (spec 5.4: unshadowed rendered regions).
# Stage 4 pass 1 (K.calibrate on the kit dome, 2026-10-29), rendered medians: grass (170,206,5), leaf_lime (124,180,5),
# leaf (17,87,9), pine (9,97,31), bark (113,69,39), petal (254,254,241), pink (234,124,175), pollen (246,216,37),
# soil (143,101,51), dirt (213,169,117), rock (175,160,163).
PALETTE = {GRASS: ("#8AAA00", 0.9, True),          # #ABCE04 exploded cliff-top lawn
           LIME: ("#689600", 0.9, True),           # #7DB401 lime bushes (render median)
           LEAF: ("#0E4E06", 0.9, True),           # #125A04 dark fern crowns
           PINE: ("#04561F", 0.9, True),           # #056324 pines
           BARK: ("#5A3412", 0.9, False),          # #6C4926 trunk lit quartile
           PETAL: ("#C3C9C8", 0.8, False),         # #F4F4EE daisies
           PINK: ("#B96696", 0.8, False),          # #EB7CAF pink flowers
           POLLEN: ("#C2B001", 0.8, False),        # #F6D81A yellow flowers / centres
           SOIL: ("#735326", 0.95, False),         # #906532 low-box soil sides
           DIRT: ("#A88B66", 0.95, False),         # #D6AA76 dirt patches
           ROCK: ("#ADA6A4", 0.85, False),         # G >= B so it never reads mauve (was #ADA5AA); lit faces #CBB6B1
           BED: ("#0B6E8F", 0.9, False),           # tuned so the pool's deep tone renders #02CFFD
           BED_LIGHT: ("#3AC4EA", 0.9, False),     # the light blob tone #43E6FD
           WATER: ("#00C2F2", 0.3, False),         # pool / channel render median #07D3FD
           FALL: ("#10C0F2", 0.3, False),          # curtain render median #11D3FD
           FOAM: ("#E6FCFE", 0.6, False)}          # foam render median #F7FDFE
TRANSPARENCY = {WATER: 0.3, FALL: 0.2, FOAM: 0.1}
WATER_SPEC = 0.0

TARGETS = {GRASS: ((0xAB, 0xCE, 0x04), "green"), LIME: ((0x7D, 0xB4, 0x01), "green"),
           LEAF: ((0x12, 0x5A, 0x04), "green"), PINE: ((0x05, 0x63, 0x24), "green"),
           BARK: ((0x6C, 0x49, 0x26), "brown"), PETAL: ((0xF4, 0xF4, 0xEE), "all"),
           PINK: ((0xEB, 0x7C, 0xAF), "vivid"), POLLEN: ((0xF6, 0xD8, 0x1A), "vivid"),
           SOIL: ((0x90, 0x65, 0x32), "brown"), DIRT: ((0xD6, 0xAA, 0x76), "all"),
           ROCK: ((0xB1, 0xA2, 0xA4), "stone")}


def palette():
    f = K.fk()
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        mat = f.material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        if k in TRANSPARENCY:
            f.set_water_transparency(mat, TRANSPARENCY[k])
            _refresh_water_texture(mat, k, hexcol)
            # preview only (the exporter makes water SmoothPlastic): a low sheen, so the sky glint doesn't wash the
            # flat water white (m034)
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf and "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = WATER_SPEC


def _refresh_water_texture(mat, key, hexcol):
    """Repaint the kit's water preview texture when the key's colour changed since the material was made (m032)."""
    f = K.fk()
    nt = mat.node_tree
    tex = nt.nodes.get("FB_WaterTex") if nt else None
    if tex is None or mat.get("m037_tex_hex") == hexcol:
        mat["m037_tex_hex"] = hexcol
        return
    mapping = tex.inputs["Vector"].links[0].from_node if tex.inputs["Vector"].links else None
    coord = mapping.inputs["Vector"].links[0].from_node if mapping and mapping.inputs["Vector"].links else None
    img = tex.image
    for n in (tex, mapping, coord):
        if n is not None:
            nt.nodes.remove(n)
    f._water_texture(mat, key, hexcol)
    if img is not None:
        img.reload()
    mat["m037_tex_hex"] = hexcol


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome; "all" keys are sampled with the
    floor dropped (M.sample). Returns {key: (hex, rendered)} and leaves the keys set. (m032 / m034)"""
    keys = keys or list(TARGETS)
    sample0 = K.sample

    def sample(src, box, kind="green"):
        return M.sample(src, box, "all", paper=(242, 238, 230), tol=14) if kind == "all" else sample0(src, box, kind)
    K.sample = sample
    try:
        for k in keys:
            K.fk().material(k)
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        K.sample = sample0
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


# ---- small helpers (m032 / m034) -------------------------------------------------------------------------------------
_faces = m032._faces
_tri = m032._tri
_mottle = m032._mottle
_v2 = m032._v2
_inside = m032._inside
_seg_d = m032._seg_d
_dist_line = m032._dist_line
_hull2 = m032._hull2
_offset_poly = m032._offset_poly
_offset_line = m032._offset_line
_simplify_convex = m032._simplify_convex
_steiner = m032._steiner
cdt_region = m032.cdt_region
_blob = m032._blob
_area2 = m032._area2


def _q(t):
    return round(min(1.0, max(0.0, t)) * 4) / 4


def _mix(k1, k2, t):
    """A blend key t of the way from k1 to k2, t quantised to quarters (0 -> k1, 1 -> k2)."""
    return K.mix_key(k1, k2, _q(t))


def _paint(a, faces, key):
    mi = a._mi(key)
    for f in faces:
        f.material_index = mi


def _key(p):
    return (round(p[0], 3), round(p[1], 3))


def _rs(way, step):
    """A waypoint polyline resampled per segment (the same waypoints reversed give the same points reversed), all
    points including both ends. (m034)"""
    P = [_v2(p) for p in way]
    out = [P[0]]
    for p, q in zip(P, P[1:]):
        n = max(1, int(math.ceil((q - p).length / step - 1e-6)))
        out += [p.lerp(q, k / n) for k in range(1, n + 1)]
    return out


def _poly(*pieces, step=3.4):
    """A closed polygon from waypoint pieces (each resampled on its own, the joint points not repeated). (m034)"""
    out = []
    for w in pieces:
        pts = _rs(w, step)
        if out and (out[-1] - pts[0]).length < 1e-6:
            pts = pts[1:]
        out += pts
    if (out[-1] - out[0]).length < 1e-6:
        out.pop()
    return out


def _flat_slab(a, co, tris, ztop, zbot, mat):
    """A closed flat slab over a 2D triangulation (water, foam, bed): planar quad walls round every boundary edge.
    Returns (top faces, wall faces, bottom faces, verts). (m034)"""
    bm = a.bm
    used = sorted({i for t in tris for i in t})
    top = {i: bm.verts.new((co[i].x, co[i].y, ztop)) for i in used}
    bot = {i: bm.verts.new((co[i].x, co[i].y, zbot)) for i in used}
    directed = set()
    tf, bf, wf = [], [], []
    for i, j, k in tris:
        tf.append(bm.faces.new((top[i], top[j], top[k])))
        bf.append(bm.faces.new((bot[i], bot[k], bot[j])))
        directed |= {(i, j), (j, k), (k, i)}
    for i, j in [(i, j) for i, j in directed if (j, i) not in directed]:
        wf.append(bm.faces.new((bot[i], bot[j], top[j], top[i])))
    allv = list(top.values()) + list(bot.values())
    a._finish(allv, mat, tint=1.0)
    return tf, wf, bf, allv


def _prism(a, poly, z0, z1, mat, step=None):
    """A closed vertical prism over a convex-ish polygon (boxes, the bed slab), quad walls."""
    P = [_v2(p) for p in poly]
    if step:
        P = m032._resample_poly(P, step)
    co, tris = cdt_region([P], [], [], tidy=False)
    return _flat_slab(a, co, tris, z1, z0, mat)


# ---- layout (studs, build frame; spec 2) -----------------------------------------------------------------------------
T = 16.0
FOOT = -0.4                 # every land piece starts here; the floor cut makes z 0 the one flat underside
BED_TOP = 0.2
WATER_TOP, WATER_BOT, WATER_GAP = 1.0, 0.26, 0.09
FOAM_Z = (1.03, 1.08)
CAP_BOT, CH_TOP, CH_WATER, CH_WATER_BOT, GRASS_TOP = 16.9, 17.1, 17.4, 17.16, 18.0
GRASS_BAND = 17.4           # the cap's thin lime edge: grass above, rock below (and the bank walls' waterline)
CAP_FRONT = -1.0            # the cap's front edge: the columns' bevelled shoulders stand 0.3 in front of it
CAP_SIDE = 15.65            # the cap's sides: the side columns' shoulders stand 0.3 outside them (X <= 15.95)
CORE_FRONT, CORE_SIDE = 0.2, 14.6
CAP_STEP = 4.0

# the channel banks, back edge -> lip (spec 2.2: 14 wide at the seam, a 4-stud throat, an 8-wide lip pool, 7.2 lip)
LB = [(-7.0, 16.0), (-7.0, 13.0), (-4.2, 11.4), (-2.2, 5.0), (-2.2, 3.0), (-4.2, 0.5), (-3.6, CAP_FRONT)]
RB = [(7.0, 16.0), (7.0, 13.0), (5.1, 11.4), (1.9, 5.0), (1.9, 3.0), (3.9, 0.5), (3.6, CAP_FRONT)]
DIRT_PATCHES = [((-6.3, 0.9), 1.3), ((-13.2, 14.0), 1.5)]


def cap_regions():
    rev = lambda w: list(reversed(w))
    S = CAP_SIDE
    return {"gl": (_poly([(-S, CAP_FRONT), (-3.6, CAP_FRONT)], rev(LB), [(-7.0, T), (-CORE_SIDE, T), (-S, T)],
                         [(-S, T), (-S, CAP_FRONT)], step=CAP_STEP), GRASS_TOP),
            "ch": (_poly([(-3.6, CAP_FRONT), (3.6, CAP_FRONT)], rev(RB), [(7.0, T), (-7.0, T)], LB, step=CAP_STEP),
                   CH_TOP),
            "gr": (_poly([(3.6, CAP_FRONT), (S, CAP_FRONT)], [(S, CAP_FRONT), (S, T)], [(S, T), (CORE_SIDE, T), (7.0, T)],
                         RB, step=CAP_STEP), GRASS_TOP)}


# columns: name -> (centre, w (x), d (y), yaw deg, top z, sides, mid ring, seed). Spec 2.3, front cell targets. The
# front row's centres put each bevelled shoulder SHOULDER_OUT in front of the cap's edge (the sheet's column tops show
# right under the grass lip); the side columns' shoulders stand the same distance outside the cap's sides.
COL_TOP = 17.85             # tall columns: the flat top sits inside the cap (16.9 .. 18.0), the chamfer crosses its edge
SHOULDER_OUT = 0.3
SUPER = 0.9386              # sin(67.5 deg) ** 0.8: the superellipse octagon's face offset / half-size
TAPER = {"default": (1.04, 0.96), "side": (1.0, 0.98)}


SIDE_TAPER = ("C1", "C6", "LW1", "LW2", "LW3", "RW1", "RW2", "RW3")   # no foot flare: they stand at the tile edge


def _front_y(d, j=0.0, taper="default"):
    return CAP_FRONT - SHOULDER_OUT + j + d / 2 * TAPER[taper][1] * SUPER


def _side_x(w, sign):
    return sign * (CAP_SIDE + SHOULDER_OUT - w / 2 * TAPER["side"][1] * SUPER)


COLS = {
    "C1": ((_side_x(3.4, -1), _front_y(4.3, 0.05, "side")), 3.4, 4.3, 0.0, COL_TOP, 8, True, 37201),
    "C2": ((-10.55, _front_y(4.2, -0.08)), 4.4, 4.2, -5.0, COL_TOP, 8, True, 37202),
    "C3": ((-6.5, _front_y(4.1, 0.06)), 4.2, 4.1, 5.0, COL_TOP, 8, True, 37203),
    "FL": ((-4.15, -0.5), 1.8, 2.0, 0.0, 10.5, 7, False, 37204),
    "C4": ((6.2, _front_y(4.2, -0.05)), 4.2, 4.2, -5.0, COL_TOP, 8, True, 37205),
    "C5": ((10.25, _front_y(4.3, 0.08)), 4.4, 4.3, 6.0, COL_TOP, 8, True, 37206),
    "C6": ((_side_x(3.4, 1), _front_y(4.2, -0.04, "side")), 3.4, 4.2, 0.0, COL_TOP, 8, True, 37207),
    "SL": ((-9.3, -3.0), 5.0, 4.4, 8.0, 12.0, 8, True, 37208),
    "SR": ((8.8, -3.0), 4.2, 4.4, -8.0, 11.5, 8, True, 37209),
    "LW1": ((_side_x(3.4, -1), 5.3), 3.4, 4.4, 3.0, COL_TOP, 6, False, 37210),
    "LW2": ((_side_x(3.4, -1), 9.4), 3.4, 4.4, -2.0, COL_TOP, 6, False, 37211),
    "LW3": ((_side_x(3.4, -1), 13.5), 3.4, 4.4, 3.0, COL_TOP, 6, False, 37212),
    "RW1": ((_side_x(3.4, 1), 5.3), 3.4, 4.4, -3.0, COL_TOP, 6, False, 37213),
    "RW2": ((_side_x(3.4, 1), 9.4), 3.4, 4.4, 2.0, COL_TOP, 6, False, 37214),
    "RW3": ((_side_x(3.4, 1), 13.5), 3.4, 4.4, -3.0, COL_TOP, 6, False, 37215),
}
COL_EXP = 0.8               # superellipse exponent: < 1 pushes the polygon toward the footprint's rectangle (m032)
COL_BEVEL = (0.4, 0.42)     # the top chamfer: inset, drop

# low boxes: name -> (x0, y0, x1, y1, top); soil sides under a grass top band (spec 2.2). 0.6 inside the tile edge,
# so the bed top beside them has no sliver.
BOXES = {"B1": (-15.4, -6.5, -10.5, -1.4, 2.4), "B1b": (-15.4, -3.0, -13.0, -0.25, 4.0),
         "B2": (12.2, -5.0, 15.4, -0.25, 2.6)}
BOX_BAND = 0.42

# rocks: name -> (centre, w, d, base z, height, yaw, kind, wet level). Spec 2.4.
BIG = [(0.0, 0.95, 7), (0.25, 1.0, 7), (0.68, 0.82, 6), (1.0, 0.5, 5)]
MED = [(0.0, 0.95, 6), (0.3, 1.0, 6), (0.72, 0.78, 5), (1.0, 0.48, 4)]
SMALL = [(0.0, 0.95, 5), (0.4, 1.0, 5), (1.0, 0.5, 3)]
PEB = [(0.0, 0.95, 4), (0.5, 1.0, 4), (1.0, 0.45, 3)]
KINDS = {"big": BIG, "med": MED, "small": SMALL, "peb": PEB}
ROCKS = {
    "K1": ((-9.6, -10.6), 5.2, 4.8, -0.1, 5.0, 15.0, "big", WATER_TOP),
    "K2": ((11.0, -10.2), 4.9, 4.6, -0.1, 4.9, -20.0, "big", WATER_TOP),
    "K3": ((-6.0, -4.9), 3.2, 3.0, -0.1, 4.3, 30.0, "med", WATER_TOP),
    "K4": ((5.8, -4.0), 1.9, 1.8, -0.1, 2.9, 10.0, "small", WATER_TOP),
    "K5": ((14.0, -6.9), 3.0, 2.8, -0.1, 3.4, 40.0, "small", WATER_TOP),
    "K6": ((-12.3, -8.7), 2.7, 2.5, -0.1, 3.0, -30.0, "small", WATER_TOP),
    "T1": ((-7.0, 13.2), 4.0, 3.6, 16.85, 3.4, 20.0, "med", CH_WATER),
    "T2": ((7.4, 12.6), 3.4, 3.2, 16.85, 3.2, -15.0, "med", CH_WATER),
    "T4": ((-3.0, 4.4), 2.6, 2.4, 16.85, 2.9, 10.0, "small", CH_WATER),
    "T5": ((2.9, 4.0), 2.9, 2.7, 16.85, 3.0, -25.0, "small", CH_WATER),
    "T6": ((-4.3, 0.2), 1.7, 1.5, 16.85, 2.0, 40.0, "small", CH_WATER),
    "T7": ((4.5, 0.45), 1.8, 1.6, 16.85, 2.1, -30.0, "small", CH_WATER),
    "P3": ((-13.3, 3.6), 0.9, 0.8, 17.85, 0.6, 60.0, "peb", None),
}
ROCK_SEED = {k: 37300 + i * 37 for i, k in enumerate(ROCKS)}
PART_ONLY = ("P3",)          # the lawn pebble dresses the cliff-top part only (hero budget: small rocks cut first)
POOL_ROCKS = ("K1", "K2", "K3", "K4", "K5", "K6")
CHAN_ROCKS = ("T1", "T2", "T4", "T5", "T6", "T7")


# ---- the cliff solid (cap + core, no booleans) ------------------------------------------------------------------------
def core_outline():
    """B, CCW: the core's front (Y 0.2) and sides (X +-14.6), its back on the cap's back edge (the same points)."""
    regs = cap_regions()
    back = sorted({_key(p) for poly, _z in regs.values() for p in poly
                   if abs(p[1] - T) < 1e-6 and abs(p[0]) <= CORE_SIDE + 1e-6}, key=lambda k: -k[0])
    front = _rs([(-CORE_SIDE, T), (-CORE_SIDE, CORE_FRONT), (CORE_SIDE, CORE_FRONT), (CORE_SIDE, T)], CAP_STEP)
    pts = [Vector(k) for k in back] + front[1:-1]
    # CCW: front left -> right, up the right side, back right -> left, down the left side
    if _area2(pts) < 0:
        pts.reverse()
    return pts


def cliff_solid(a, regs, B=None, z_ann=CAP_BOT, z_bot=FOOT, bands=(GRASS_BAND,), step=4.6, seed=37100,
                extra=None, bottom_step=8.0):
    """One closed multi-level solid without booleans. regs = {tag: (poly, level)} are flat tops over the outline A;
    vertical walls stand where regions of different level meet. B (optional, CCW, inside A, sharing A's back points)
    is the core: A's edges that lie on B drop straight to z_bot ("deep" walls: the back joining face); the rest of A
    drops to z_ann, where a flat underside (A minus B) turns in to B, whose own walls go down to z_bot; the bottom is
    over B at z_bot. Without B the bottom is over A at z_ann. Returns a dict of face lists for painting."""
    bm = a.bm
    vmap = {}

    def V(k, z):
        kk = (k[0], k[1], round(z, 4))
        v = vmap.get(kk)
        if v is None:
            v = vmap[kk] = bm.verts.new((k[0], k[1], z))
        return v
    level = {tag: z for tag, (poly, z) in regs.items()}
    tri_keys, bnd = {}, {}
    for i, (tag, (poly, z)) in enumerate(regs.items()):
        st = _steiner([poly], [], step, step * 0.42, seed + i)
        if extra and tag in extra:
            st += [Vector(p) for p in extra[tag] if _inside(p, poly) and _dist_line(p, poly, True) > 0.6]
        co, tris = cdt_region([poly], [], st, tidy=False)
        ks = [_key(c) for c in co]
        tri_keys[tag] = [(ks[i_], ks[j_], ks[k_]) for i_, j_, k_ in tris]
        d = set()
        for t in tri_keys[tag]:
            d |= {(t[0], t[1]), (t[1], t[2]), (t[2], t[0])}
        bnd[tag] = [e for e in d if (e[1], e[0]) not in d]
    owner = {e: tag for tag, es in bnd.items() for e in es}
    outline = [(e, tag) for tag, es in bnd.items() for e in es if (e[1], e[0]) not in owner]
    nxt = {e[0]: e[1] for e, _t in outline}
    start = next(iter(nxt))
    A = [start]
    while nxt[A[-1]] != start:
        A.append(nxt[A[-1]])
    Bk = [_key(p) for p in B] if B else []
    bset = set(Bk)
    bedges = {(Bk[i], Bk[(i + 1) % len(Bk)]) for i in range(len(Bk))}
    deep = {e for e, _t in outline if e[0] in bset and e[1] in bset and e in bedges}
    deep_pts = {p for e in deep for p in e}
    a_pts = set(A)
    lv = {}
    for tag, es in bnd.items():
        for e in es:
            for p in e:
                lv.setdefault(p, set()).add(level[tag])
    for e, _t in outline:
        for p in e:
            ins = [x for x in outline if x[0][1] == p] + [x for x in outline if x[0][0] == p]
            interior_deep = all(x[0] in deep for x in ins)
            if not interior_deep:
                lv[p].add(z_ann)
            if p in deep_pts:
                lv[p].add(z_bot)
    for p in Bk:
        s = lv.setdefault(p, set())
        s.add(z_bot)
        if not (p in a_pts and all(x[0] in deep for x in outline if p in x[0])):
            s.add(z_ann)
    for p, s in lv.items():
        lo, hi = min(s), max(s)
        s |= {b for b in bands if lo + 0.05 < b < hi - 0.05}
    out = {"top": {}, "step": [], "outer": [], "deep": [], "core": [], "under": [], "bottom": []}
    for tag, tris in tri_keys.items():
        z = level[tag]
        out["top"][tag] = [bm.faces.new((V(i, z), V(j, z), V(k, z))) for i, j, k in tris]

    def wall(p, q, lo, hi, bucket, info):
        ci = [V(p, z) for z in sorted(z for z in lv[p] if lo - 1e-6 <= z <= hi + 1e-6)]
        cj = [V(q, z) for z in sorted(z for z in lv[q] if lo - 1e-6 <= z <= hi + 1e-6)]
        ia = ib = 0
        while ia < len(ci) - 1 or ib < len(cj) - 1:
            if ib == len(cj) - 1 or (ia < len(ci) - 1 and ci[ia + 1].co.z <= cj[ib + 1].co.z + 1e-6):
                f = bm.faces.new((ci[ia], cj[ib], ci[ia + 1]))
                ia += 1
            else:
                f = bm.faces.new((ci[ia], cj[ib], cj[ib + 1]))
                ib += 1
            out[bucket].append((f,) + info)
    for tag, es in bnd.items():
        for e in es:
            nb = owner.get((e[1], e[0]))
            if nb is not None:
                if level[nb] < level[tag]:
                    wall(e[0], e[1], level[nb], level[tag], "step", (tag, nb))
            elif e in deep:
                wall(e[0], e[1], z_bot, level[tag], "deep", (tag, None))
            else:
                wall(e[0], e[1], z_ann if B else z_ann, level[tag], "outer", (tag, None))
    if B:
        for p, q in bedges:
            if (p, q) in deep:
                continue
            wall(p, q, z_bot, z_ann, "core", ("core", None))
        # the cap's underside: A minus B (they share the back points, so it is one U-shaped region)
        co, tris = cdt_region([[Vector(k) for k in A]], [[Vector(k) for k in Bk]], [], tidy=False)
        ks = [_key(c) for c in co]
        out["under"] = [bm.faces.new((V(ks[i], z_ann), V(ks[k], z_ann), V(ks[j], z_ann))) for i, j, k in tris]
        poly = [Vector(k) for k in Bk]
        zb = z_bot
    else:
        poly = [Vector(k) for k in A]
        zb = z_ann
    st = _steiner([poly], [], bottom_step, bottom_step * 0.4, seed + 50)
    co, tris = cdt_region([poly], [], st, tidy=False)
    ks = [_key(c) for c in co]
    out["bottom"] = [bm.faces.new((V(ks[i], zb), V(ks[k], zb), V(ks[j], zb))) for i, j, k in tris]
    allv = list(vmap.values())
    bmesh.ops.recalc_face_normals(bm, faces=_faces(allv))
    a._finish(allv, ROCK, tint=1.0)
    out["verts"] = allv
    return out


def _dirt_ring_points():
    pts = []
    for (c, r) in DIRT_PATCHES:
        for rr in (r * 0.55, r + 0.5):
            for k in range(5):
                ang = 2 * math.pi * k / 5 + (0.6 if rr > r else 0.0)
                pts.append((c[0] + math.cos(ang) * rr, c[1] + math.sin(ang) * rr))
    return pts


def _paint_cliff(a, S, seed=37150):
    """The lawn: lime with broad patches toward the lime-bush green, a trampled band toward the dirt along the
    channel banks, two bare dirt patches; the channel bed deep teal with broad light patches; the cap's outer walls a
    thin lime edge over rock; the bank walls grass over the bed colour under the water; the core and underside rock,
    the core wall behind the curtain bed-dark (blended into the rock at its sides). By position only."""
    nf = K.noise_field(scale=0.3, seed=seed)
    nb_ = K.noise_field(scale=0.32, seed=seed + 1)
    for tag, faces in S["top"].items():
        for f in faces:
            c = f.calc_center_median()
            if tag == "ch":
                key = _mix(BED, BED_LIGHT, (nb_(c) - 0.1) / 0.3)
            else:
                dp = min((_v2(c) - Vector(p)).length - r for p, r in DIRT_PATCHES)
                db = min(_dist_line(c, LB), _dist_line(c, RB))
                if dp < 0:
                    key = DIRT
                elif dp < 0.9:
                    key = _mix(GRASS, DIRT, 0.5)
                elif db < 1.0:
                    key = _mix(GRASS, DIRT, 0.25)
                else:
                    t = _q((nf(c) - 0.02) / 0.3) * 0.5
                    key = K.mix_key(GRASS, LIME, t)
            f.material_index = a._mi(key)
    for f, tag, nb in S["step"]:
        z = f.calc_center_median().z
        f.material_index = a._mi(GRASS if z > GRASS_BAND + 0.01 else BED)
    for f, tag, nb in S["outer"] + S["deep"]:
        z = f.calc_center_median().z
        if tag == "ch":                 # the lip and the back seam: bed-coloured channel slab, rock joining face below
            key = BED if z > CAP_BOT - 0.01 else ROCK
        else:
            key = GRASS if z > GRASS_BAND + 0.01 else ROCK
        f.material_index = a._mi(key)
    for f, tag, nb in S["core"]:
        c = f.calc_center_median()
        if abs(c.y - CORE_FRONT) < 0.05 and c.z < CAP_BOT:
            t = (abs(c.x) - 3.6) / 1.6          # bed-dark behind the curtain, blended to rock by |x| 3.6 .. 5.2
            key = _mix(BED, ROCK, t)
        else:
            key = ROCK
        f.material_index = a._mi(key)
    _paint(a, S["under"] + S["bottom"], ROCK)
    grass = [f for t, fs in S["top"].items() if t != "ch" for f in fs]
    _mottle(a, grass, 0.04, 0.5, seed + 2)
    _mottle(a, S["top"].get("ch", []), 0.03, 0.8, seed + 3)
    _mottle(a, [w[0] for k in ("step", "outer", "deep", "core") for w in S[k]] + S["under"], 0.04, 0.5, seed + 4)


def cliff(a):
    S = cliff_solid(a, cap_regions(), core_outline(), extra={"gl": _dirt_ring_points()})
    _paint_cliff(a, S)
    return S["verts"]


# ---- columns -------------------------------------------------------------------------------------------------------
def column_pts(name, z0=FOOT):
    """The points of one column: a foot ring (scale 1.04), an optional mid ring (1.0, twisted a little so the big side
    facets break once), a shoulder ring (0.96) and a flat top ring inset by the bevel. Superellipse rings (m032)."""
    (cx, cy), w, d, yaw, top, sides, mid, seed = COLS[name]
    rng = random.Random(seed)
    yr = math.radians(yaw)
    u = Vector((math.cos(yr), math.sin(yr)))
    n = Vector((-math.sin(yr), math.cos(yr)))
    hw, hd = w / 2, d / 2
    ins, drop = COL_BEVEL
    ins = min(ins, 0.095 * min(w, d))
    ph = rng.uniform(-0.08, 0.08)
    lean = Vector((rng.uniform(-0.1, 0.1), rng.uniform(-0.08, 0.08)))
    sh = top - drop
    H = top - FOOT

    def ring(sx, sy, j, tw):
        out = []
        for k in range(sides):
            ang = 2 * math.pi * (k + 0.5) / sides + ph + rng.uniform(-0.05, 0.05)
            c_, s_ = math.cos(ang), math.sin(ang)
            lu = math.copysign(abs(c_) ** COL_EXP, c_) * sx * (1 + rng.uniform(-j, j))
            lv = math.copysign(abs(s_) ** COL_EXP, s_) * sy * (1 + rng.uniform(-j, j))
            ct, st_ = math.cos(tw), math.sin(tw)
            out.append((lu * ct - lv * st_, lu * st_ + lv * ct))
        return out

    def P(lu, lv, z):
        t = (z - FOOT) / H
        q = Vector((cx, cy)) + u * (lu + lean.x * t) + n * (lv + lean.y * t)
        return Vector((q.x, q.y, z))
    tf, ts = TAPER["side" if name in SIDE_TAPER else "default"]
    levels = [(z0, tf, 0.03, 0.0, 0.0)]
    if mid:
        levels.append((FOOT + (sh - FOOT) * rng.uniform(0.42, 0.58), (tf + ts) / 2 + 0.015, 0.06,
                       rng.uniform(-0.16, 0.16), 1.1))
    levels.append((sh, ts, 0.03, rng.uniform(-0.1, 0.1), 0.06))
    pts = []
    for z, sc, j, tw, zj in levels:
        # the same random draws whatever z0 is (the cliff-top part's short columns match the hero's), but a ring
        # below a raised foot is left out
        scz = sc if z != z0 or z0 == FOOT else tf - (tf - ts) * (z0 - FOOT) / (sh - FOOT)
        ring_pts = [P(lu, lv, z + rng.uniform(-zj, zj)) for lu, lv in ring(hw * scz, hd * scz, j, tw)]
        if z >= z0:
            pts += ring_pts
    for lu, lv in ring(hw * 0.97 - ins, hd * 0.97 - ins, 0.02, levels[-1][3]):
        pts.append(P(lu, lv, top))
    if name in SIDE_TAPER:                  # the outer face stays inside the tile (X <= 15.97)
        for p in pts:
            p.x = math.copysign(min(abs(p.x), T - 0.03), p.x)
    return pts


def column(a, name, z0=FOOT):
    """One fat flat-faced column: the convex hull of its rings (big side facets, one chamfer ring, a flat top)."""
    pts = column_pts(name, z0)
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    for v in vs:
        if v.is_valid and not v.link_faces:
            bm.verts.remove(v)
    vs = [v for v in vs if v.is_valid]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    _tri(bm, _faces(vs))
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, ROCK, tint=1.0)
    _mottle(a, _faces(vs), 0.04, 0.5, COLS[name][7], tint=random.Random(COLS[name][7]).uniform(0.95, 1.05))
    return vs


# ---- boxes, bed, rocks -----------------------------------------------------------------------------------------------
def low_box(a, name):
    """A low blocky box: soil sides under a grass top band (the sheet's tan / brown box sides, lime tops)."""
    x0, y0, x1, y1, top = BOXES[name]
    P = [Vector(p) for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    co, tris = cdt_region([P], [], [], tidy=False)
    bm = a.bm
    used = sorted({i for t in tris for i in t})
    zs = (FOOT, top - BOX_BAND, top)
    ring = {i: [bm.verts.new((co[i].x, co[i].y, z)) for z in zs] for i in used}
    tf, wf, bf = [], [], []
    directed = set()
    for i, j, k in tris:
        tf.append(bm.faces.new((ring[i][2], ring[j][2], ring[k][2])))
        bf.append(bm.faces.new((ring[i][0], ring[k][0], ring[j][0])))
        directed |= {(i, j), (j, k), (k, i)}
    for i, j in [(i, j) for i, j in directed if (j, i) not in directed]:
        for lv_ in range(2):
            wf.append(bm.faces.new((ring[i][lv_], ring[j][lv_], ring[j][lv_ + 1], ring[i][lv_ + 1])))
    vs = [v for r in ring.values() for v in r]
    a._finish(vs, SOIL, tint=1.0)
    for f in wf:
        f.material_index = a._mi(GRASS if f.calc_center_median().z > top - BOX_BAND else SOIL)
    _paint(a, tf, GRASS)
    _mottle(a, tf, 0.04, 0.5, 37401)
    _mottle(a, wf, 0.03, 0.6, 37402)
    return vs


def bed(a):
    """The pool's bed slab under the whole front (its back runs 0.4 into the core); deep teal with broad light
    patches (the water's light / deep blob pattern), 25 % toward the rock round the boulders' feet."""
    # the open edges (front, sides) every 1.8 (the 0.2-tall side face: no needles); the back runs under the core
    P = _rs([(T, 0.45), (T, -T), (-T, -T), (-T, 0.45)], 1.8) + _rs([(-T, 0.45), (T, 0.45)], 8.0)[1:-1]
    P.reverse()
    st = _steiner([P], [], 7.0, 2.6, 37450)
    co, tris = cdt_region([P], [], st, tidy=False)
    tf, wf, bf, vs = _flat_slab(a, co, tris, BED_TOP, FOOT, BED)
    nf = K.noise_field(scale=0.3, seed=37451)
    feet = [(Vector(ROCKS[k][0]), (ROCKS[k][1] + ROCKS[k][2]) / 4) for k in POOL_ROCKS]
    for f in tf:
        c = f.calc_center_median()
        if any((_v2(c) - p).length < r + 0.8 for p, r in feet):
            key = _mix(BED, ROCK, 0.25)
        else:
            key = _mix(BED, BED_LIGHT, (nf(c) - 0.12) / 0.3)
        f.material_index = a._mi(key)
    _mottle(a, tf, 0.03, 0.8, 37452)
    return vs


def rock(a, name, at_origin=False):
    """One faceted rock: the convex hull of jittered rings (flat bottom, widest low, a flat crown), facets merged where
    near-coplanar and re-triangulated (m034). Pool rocks stand on the bed, channel rocks on the channel bed."""
    (cx, cy), w, d, z0, h, yaw, kind, wet = ROCKS[name]
    seed = ROCK_SEED[name]
    if at_origin:
        cx = cy = z0 = 0.0
    vs = K.hull_rock(a, (w, d, h), loc=(cx, cy, z0), seed=seed, mat=ROCK, rings=KINDS[kind], jitter=0.07,
                     rot=math.radians(yaw), keep_bottom=True)
    bmesh.ops.dissolve_limit(a.bm, angle_limit=math.radians(4.0), verts=vs,
                             edges=list({e for f in _faces(vs) for e in f.edges}))
    vs = [v for v in vs if v.is_valid]
    _tri(a.bm, _faces(vs))
    bmesh.ops.recalc_face_normals(a.bm, faces=_faces(vs))
    tint = random.Random(seed).uniform(0.94, 1.06)
    for f in _faces(vs):
        c = f.calc_center_median()
        f.material_index = a._mi(BED if (wet is not None and not at_origin and c.z < wet - 0.02) else ROCK)
    _mottle(a, _faces(vs), 0.04, 0.6, seed, tint=tint)
    return vs


# ---- holes: every land piece's section through the water / foam levels ---------------------------------------------
HOLES = {}


def _section(vs, z0, z1):
    pts = [v.co.copy() for v in vs if z0 <= v.co.z <= z1]
    for e in {e for v in vs for e in v.link_edges}:
        p, q = e.verts[0].co, e.verts[1].co
        for zc in (z0, z1):
            if (p.z - zc) * (q.z - zc) < 0:
                t = (zc - p.z) / (q.z - p.z)
                pts.append(p + (q - p) * t)
    if len(pts) < 3:
        return None
    return _hull2([(p.x, p.y) for p in pts])


def _hole(hull, margin, nmax=6, min_edge=0.9, snap=True):
    """A convex 2D hole round a section: at most nmax corners, no edge under min_edge (or five corners), offset by
    margin plus what the simplification cut in; corners near a tile edge pushed out past it (no water sliver)."""
    simp = _simplify_convex(hull, nmax)
    while len(simp) > 5:
        el = [(simp[(i + 1) % len(simp)] - simp[i]).length for i in range(len(simp))]
        i = min(range(len(simp)), key=lambda k: el[k])
        if el[i] >= min_edge:
            break
        simp.pop((i + 1) % len(simp) if el[i - 1] > el[(i + 1) % len(simp)] else i)
    loss = max(min(_seg_d(q, simp[i], simp[(i + 1) % len(simp)]) for i in range(len(simp)))
               if not any((q - s).length < 1e-6 for s in simp) else 0.0 for q in hull)
    poly = _offset_poly(simp, margin + loss)
    if snap:
        for p in poly:
            if p.x < -T + 0.7:
                p.x = -T - 0.6
            elif p.x > T - 0.7:
                p.x = T + 0.6
    return poly


def holes():
    """name -> {"pool", "foam", "chan"} hole polygons, from a throwaway build of every land piece."""
    if HOLES:
        return HOLES
    a = K.fk().Asset("_m037_probe", "probe")
    pieces = {}
    for nm in COLS:
        pieces[nm] = column(a, nm)
    for nm in BOXES:
        pieces[nm] = low_box(a, nm)
    for nm in ROCKS:
        pieces[nm] = rock(a, nm)
    for nm, vs in pieces.items():
        h = {}
        for band, (z0, z1), margin in (("pool", (BED_TOP, WATER_TOP + 0.1), WATER_GAP),
                                       ("foam", (WATER_TOP - 0.05, FOAM_Z[1] + 0.12), WATER_GAP),
                                       ("chan", (CH_TOP, CH_WATER + 0.08), WATER_GAP)):
            s = _section(vs, z0, z1)
            if s is not None and len(s) >= 3:
                h[band] = _hole(s, margin)
        HOLES[nm] = h
    a.bm.free()
    return HOLES


BANDS = {"pool": ((BED_TOP, WATER_TOP + 0.1), WATER_GAP), "foam": ((WATER_TOP - 0.05, FOAM_Z[1] + 0.12), WATER_GAP),
         "chan": ((CH_TOP, CH_WATER + 0.08), WATER_GAP)}


def refine_holes(o, names=None):
    """Re-measure the holes on the finished land (the union and cleanup move vertices a little): for each piece and
    band, the land's edges crossing the band inside the old hole grown by 0.6 are clipped to the band, and their
    convex hull (simplified and offset as before) becomes the new hole. Returns how many changed."""
    off = Vector(o[OFF])
    me = o.data
    co = [v.co + off for v in me.vertices]
    segs = [(co[e.vertices[0]], co[e.vertices[1]]) for e in me.edges]
    n = 0
    for nm, h in holes().items():
        if names is not None and nm not in names:
            continue
        for band, old in list(h.items()):
            (z0, z1), margin = BANDS[band]
            grown = _offset_poly(old, 0.6)
            pts = []
            for p, q in segs:
                lo, hi = (p, q) if p.z <= q.z else (q, p)
                if hi.z < z0 or lo.z > z1:
                    continue
                for c in (lo, hi):
                    if z0 <= c.z <= z1:
                        pts.append(c)
                for zc in (z0, z1):
                    if lo.z < zc < hi.z:
                        pts.append(lo.lerp(hi, (zc - lo.z) / (hi.z - lo.z)))
            pts = [Vector((c.x, c.y)) for c in pts if _inside((c.x, c.y), grown)]
            if len(pts) >= 3:
                h[band] = _hole(_hull2([(c.x, c.y) for c in pts]), margin)
                n += 1
    return n


def _holes(band, names=None):
    return [h[band] for nm, h in holes().items() if band in h and (names is None or nm in names)]


# ---- water, curtain, foam ----------------------------------------------------------------------------------------------
BANK_GAP = 0.25             # the channel water stands this far off the bank walls (the cleanup slides wall verts a little)
POOL_BACK = -1.62           # the pool plate's back edge: just in front of the column feet (-1.46); the stepped
                            # columns, boxes and boulders cut it


def pool_water(a, names=None):
    """The pool plate: top 1.0, bottom 0.26 (0.06 over the bed), edge faces 0.02 inside the tile, cut round every land
    piece standing in it. Flat: no ripples (spec 6)."""
    rect = [Vector(p) for p in ((-T + 0.02, -T + 0.02), (T - 0.02, -T + 0.02), (T - 0.02, POOL_BACK),
                                (-T + 0.02, POOL_BACK))]
    rect = m032._resample_poly(rect, 8.0)
    co, tris = m034.cdt_region([rect], _holes("pool", names), [], min_island=1.0)
    return _flat_slab(a, co, tris, WATER_TOP, WATER_BOT, WATER)[3]


def channel_poly():
    """The channel water's outline: the banks offset WATER_GAP into the channel, the back face 0.02 inside the seam,
    the front 0.05 past the lip (its overhang rounds into the curtain's top)."""
    left = _offset_line(_rs(LB, 3.5), -BANK_GAP)
    right = _offset_line(_rs(RB, 3.5), BANK_GAP)
    y_back, y_front = T - 0.02, CAP_FRONT - 0.05
    for line in (left, right):
        line[0].y = y_back
        line[-1].y = y_front
    # the back seam edge gets points every 3.5 (one long edge there left a needle triangle)
    back = [right[0].lerp(left[0], k / 4) for k in range(1, 4)]
    return left + list(reversed(right)) + back   # back-left -> lip -> back-right -> along the seam (CCW)


def channel_water(a, names=CHAN_ROCKS):
    poly = channel_poly()
    if _area2(poly) < 0:
        poly.reverse()
    co, tris = m034.cdt_region([poly], _holes("chan", names), [], min_island=0.5)
    return _flat_slab(a, co, tris, CH_WATER, CH_WATER_BOT, WATER)[3]


# the curtain: rings (z, back y, half width, roll) from the lip to the pool (spec 2.4: 7.2 -> 8.4 wide, leaning out
# 1.4, three lobes); the top ring is thin and the second rolls forward over the lip (the rounded caps)
CURTAIN = [(17.45, -1.10, 3.55, "thin"), (17.15, -1.13, 3.6, 0.25), (14.0, -1.35, 3.68, 0.0), (9.0, -1.75, 3.85, 0.0),
           (4.6, -2.12, 4.0, 0.0), (1.12, -2.42, 4.15, 0.0)]
CURT_THICK, CURT_LOBE = 0.47, 0.42
LOBES = (0.0, 0.85, 0.85, 0.0, 0.95, 0.95, 0.0, 0.85, 0.85, 0.0)   # 3 lobes: valleys at the ends and between lobes


def curtain(a):
    """A closed shell: a wavy front surface of three shallow U-lobes (deep valleys between rounded crests) swept down
    six rings with the lean and widening, a flat back with four points per ring, flat side strips, top and bottom
    caps. Its back stays 0.1 in front of the lip wall and the channel water's front edge."""
    bm = a.bm
    n = len(LOBES)
    fronts, backs = [], []
    for z, yb, hw, roll in CURTAIN:
        fr, bk = [], []
        for i in range(n):
            x = -hw + 2 * hw * i / (n - 1)
            if roll == "thin":
                y = yb - 0.3 - 0.5 * CURT_LOBE * LOBES[i]
            else:
                deep = CURT_LOBE * (1.0 + 0.15 * (z < 3))
                y = yb - CURT_THICK - deep * LOBES[i] - roll * (0.4 + 0.6 * LOBES[i])
            fr.append(bm.verts.new((x, y, z)))
        for x in (-hw, -hw / 3, hw / 3, hw):
            bk.append(bm.verts.new((x, yb, z)))
        fronts.append(fr)
        backs.append(bk)
    faces = []
    for r in range(len(CURTAIN) - 1):
        f0, f1, b0, b1 = fronts[r], fronts[r + 1], backs[r], backs[r + 1]
        for i in range(n - 1):
            faces.append(bm.faces.new((f0[i], f1[i], f1[i + 1], f0[i + 1])))
        for i in range(3):
            faces.append(bm.faces.new((b0[i + 1], b1[i + 1], b1[i], b0[i])))
        faces.append(bm.faces.new((b0[0], b1[0], f1[0], f0[0])))
        faces.append(bm.faces.new((f0[-1], f1[-1], b1[-1], b0[-1])))
    # caps: each lobe's front (valley, crest, crest, valley) over its back segment is a convex trapezoid, fanned from
    # the back corner (the back points sit at the same x as the valleys)
    for ring_f, ring_b in ((fronts[0], backs[0]), (fronts[-1], backs[-1])):
        for s in range(3):
            f4 = ring_f[3 * s:3 * s + 4]
            for i in range(3):
                faces.append(bm.faces.new((ring_b[s], f4[i], f4[i + 1])))
            faces.append(bm.faces.new((ring_b[s], f4[3], ring_b[s + 1])))
    vs = [v for r in fronts + backs for v in r]
    _tri(bm, [f for f in faces if f.is_valid])
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, FALL, tint=1.0)
    return vs


def _scallop(c, rx, ry, n, amp, rot=0.0, seed=0):
    """A scalloped ellipse (n lobes, each a rounded bump: two points per lobe)."""
    rng = random.Random(seed)
    out = []
    for k in range(2 * n):
        ang = rot + math.pi * k / n
        r = 1.0 + (amp if k % 2 == 0 else -amp * 0.4) * rng.uniform(0.8, 1.2)
        out.append(Vector((c[0] + math.cos(ang) * rx * r, c[1] + math.sin(ang) * ry * r)))
    return out


DISC = ((0.0, -5.2), 8.0, 4.1, 8)            # the splash disc: centre, radii, scallops (15 x 8, spec 2.4)
RIBBON = ((0.0, -3.4), 4.7, 2.2, 6)          # the foam ribbon round the curtain foot (outer about 10 x 5)
RIBBON_IN = ((0.0, -3.1), 3.3, 1.0)          # its inner hole (the part alone; in the hero the disc fills it)
DISC_HOLES = [((-3.4, -6.9), 0.5), ((3.0, -7.1), 0.5)]
FOAM_RINGS = {"K1": 0.85, "K2": 0.85}
FOAM_BLOBS = [((-13.0, -12.8), 1.3), ((-3.5, -12.6), 1.4), ((4.8, -13.4), 1.3), ((14.0, -13.6), 1.0)]
CH_FOAM = [((0.0, 4.2), 0.55), ((-0.6, -0.3), 0.7)]
FOAM_BACK = [Vector(p) for p in ((-T - 1, POOL_BACK - WATER_GAP), (T + 1, POOL_BACK - WATER_GAP),
                                 (T + 1, T), (-T - 1, T))]


def _clip_tile(poly, m=0.02):
    for p in poly:
        p.x = min(T - m, max(-T + m, p.x))
        p.y = min(T - m, max(-T + m, p.y))
    return poly


def foam_regions(parts=("disc", "ribbon", "rings", "blobs", "holes")):
    pos, neg = [], []
    if "disc" in parts:
        c, rx, ry, nl = DISC
        pos.append(_scallop(c, rx, ry, nl, 0.09, 0.2, 37501))
    if "ribbon" in parts:
        c, rx, ry, nl = RIBBON
        pos.append(_scallop(c, rx, ry, nl, 0.1, 0.0, 37502))
    if "ribbon_in" in parts:
        c, rx, ry = RIBBON_IN
        neg.append(_blob(c, rx, 10, 0.0, ry / rx))
    if "holes" in parts:
        rng = random.Random(37503)
        for c, r in DISC_HOLES:
            neg.append(_blob(c, r, 5, rng.uniform(0, 6.3), 0.8))
    hs = holes()
    if "rings" in parts:
        for nm, w in FOAM_RINGS.items():
            if "pool" in hs[nm]:
                pos.append(_clip_tile(_offset_poly(hs[nm]["pool"], w)))
    if "blobs" in parts:
        rng = random.Random(37504)
        for c, r in FOAM_BLOBS:
            pos.append(_clip_tile(_blob(c, r, 5, rng.uniform(0, 6.3), 0.7)))
    neg += _holes("foam")
    neg.append(FOAM_BACK)
    return pos, neg


def foam(a, parts=("disc", "ribbon", "rings", "blobs", "holes")):
    pos, neg = foam_regions(parts)
    co, tris = m034.cdt_region(pos, neg, [], min_island=0.3)
    return _flat_slab(a, co, tris, FOAM_Z[1], FOAM_Z[0], FOAM)[3]


def channel_foam(a):
    rng = random.Random(37505)
    pos = [_blob(c, r, 5, rng.uniform(0, 6.3), 0.75) for c, r in CH_FOAM]
    neg = _holes("chan", CHAN_ROCKS)
    co, tris = m034.cdt_region(pos, neg, [], min_island=0.2)
    return _flat_slab(a, co, tris, CH_WATER + 0.08, CH_WATER + 0.03, FOAM)[3]


# splash spikes: (x, y, base radius, height) on the disc in front of the curtain foot, the tallest nearest the fall
SPIKES = [(-3.6, -4.6, 0.4, 1.7), (-2.3, -4.85, 0.42, 2.2), (-0.95, -5.0, 0.45, 2.6), (0.45, -5.05, 0.45, 2.7),
          (1.8, -4.9, 0.42, 2.2), (3.2, -4.7, 0.38, 1.6), (-1.7, -6.1, 0.34, 1.3), (1.1, -6.15, 0.34, 1.3)]
# the splash veil: a thin white wall of spray standing on the disc right in front of the curtain's foot, its top a
# row of spiky splash peaks (the sheet's white spray hides the curtain's lowest third); (x, z) outline, y range
VEIL = [(-4.4, 0.0), (-3.6, 3.0), (-2.7, 2.1), (-1.8, 4.7), (-0.9, 2.6), (0.0, 5.7), (0.9, 2.6), (1.8, 4.9),
        (2.7, 2.1), (3.6, 3.2), (4.4, 0.0)]
VEIL_Y = (-3.75, -3.55)
SPIKE_Z = FOAM_Z[1] + 0.01
SPIKE_SCALE = (1.1, 1.45)   # base radius, height multipliers on SPIKES (the sheet's spray reaches a third up the fall)


def _spike_geo(x, y, r, h, k):
    """A 3-sided splash cone leaning away from the curtain foot (0, -2.6): base triangle + apex (4 tris)."""
    rot = 0.7 * k
    out = Vector((x, y + 2.6)).normalized() if (x, y + 2.6) != (0, 0) else Vector((0, -1))
    lean = out * 0.16 * h
    pts = [Vector((x + math.cos(rot + i * 2.094) * r, y + math.sin(rot + i * 2.094) * r, SPIKE_Z)) for i in range(3)]
    pts.append(Vector((x + lean.x, y + lean.y, SPIKE_Z + h)))
    faces = [(0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3)]
    return pts, faces


def veil(a, guard=None):
    """The splash veil: VEIL's outline (x, z above the disc) extruded across VEIL_Y, a closed foam slab."""
    poly = [Vector((x, z)) for x, z in VEIL]
    co, tris = m034.cdt_region([poly], [], [], tidy=False)
    z0 = SPIKE_Z
    bm = a.bm
    used = sorted({i for t in tris for i in t})
    fr = {i: bm.verts.new((co[i].x, VEIL_Y[0], z0 + co[i].y)) for i in used}
    bk = {i: bm.verts.new((co[i].x, VEIL_Y[1], z0 + co[i].y)) for i in used}
    directed = set()
    for i, j, k in tris:
        bm.faces.new((fr[i], fr[j], fr[k]))
        bm.faces.new((bk[i], bk[k], bk[j]))
        directed |= {(i, j), (j, k), (k, i)}
    for i, j in [(i, j) for i, j in directed if (j, i) not in directed]:
        bm.faces.new((fr[i], fr[j], bk[j], bk[i]))
    vs = list(fr.values()) + list(bk.values())
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, FOAM, tint=1.0)
    return vs


def spikes(a, guard=None):
    vs = []
    for k, (x, y, r, h) in enumerate(SPIKES):
        for sc in (1.0, 0.8, 0.62):
            pts, faces = _spike_geo(x, y, r * SPIKE_SCALE[0] * (0.9 + 0.1 * sc), h * SPIKE_SCALE[1] * sc, k)
            if guard is None or guard.ok(pts, faces):
                if guard is not None:
                    guard.add(pts, faces)
                vs += _emit(a, pts, faces, FOAM)
                break
        else:
            if guard is not None:
                guard.dropped += 1
    return vs


# ---- vegetation (m032's pines, fan bushes, daisies) ------------------------------------------------------------------
VEG_GAP = 0.015            # every dressing shell sits this far off its support (STAGES: within 0.03, chained to it)
CONTACT = 0.03


def _leaf_geo(base, yaw, pitch, L, W, curl=0.22, thick=0.05):
    """A broad leaf with a blunt rounded tip (STAGES: rounded clumps, not pointed): a 5-point outline (base, widest at
    0.38 L, two tip corners at 0.88 L), its top a low ridge along the midrib (convex), its back a fan to one point
    (8 tris)."""
    rot = Matrix.Rotation(yaw, 3, "Z") @ Matrix.Rotation(-pitch, 3, "Y")
    B = Vector(base)

    def P(x, y_, z):
        t = x / L
        return B + rot @ Vector((x, y_, z - curl * L * t * t))
    pts = [P(0, 0, 0), P(0.38 * L, -W / 2, -0.05 * W), P(0.88 * L, -0.3 * W, -0.03 * W), P(0.88 * L, 0.3 * W, -0.03 * W),
           P(0.38 * L, W / 2, -0.05 * W)]
    # the back point: under the top's midline at half length (so the closed wedge never turns inside out where the
    # tip curls down)
    mid = pts[0].lerp((pts[2] + pts[3]) / 2, 0.51)
    pts.append(mid - rot @ Vector((0, 0, 1)) * (thick + 0.08 * W))
    faces = [(0, 1, 2), (0, 2, 3), (0, 3, 4)] + [(5, (i + 1) % 5, i) for i in range(5)]
    return pts, faces


def _daisy_geo(c, r, ph, rng, ground):
    """m032's five-petal star lens, VEG_GAP over the ground."""
    pts2 = []
    for k in range(10):
        ang = ph + math.pi * k / 5
        rr = r * (1.0 if k % 2 == 0 else 0.42)
        pts2.append((c[0] + math.cos(ang) * rr, c[1] + math.sin(ang) * rr))
    z = _ground_max(ground, pts2 + [tuple(c)])
    if z is None:
        return None, None, None
    z += VEG_GAP
    pts = [Vector((x, y, z + rng.uniform(0.0, 0.03))) for x, y in pts2] + [Vector((c[0], c[1], z + 0.12)),
                                                                          Vector((c[0], c[1], z))]
    faces = []
    for k in range(10):
        j = (k + 1) % 10
        faces += [(10, k, j), (11, j, k)]
    return pts, faces, z
# pines: name -> (centre, height, scale, seed, tiers)
PINES = {"PL1": ((-11.5, 8.0), 7.2, 1.08, 37601, 3), "PL2": ((-5.9, 9.4), 6.2, 0.95, 37602, 3),
         "PR1": ((8.6, 6.2), 7.0, 1.08, 37603, 3), "PR2": ((12.0, 11.6), 6.0, 0.93, 37604, 3),
         "PF1": ((-13.85, -5.4), 7.0, 0.95, 37605, 3), "PF2": ((13.85, -3.4), 6.6, 0.9, 37606, 3)}
PINE_TIERS = {3: (2.05, 1.6, 1.1), 4: (1.8, 1.46, 1.1, 0.74)}
# fan bushes: (centre, size, leaves, seed, key, side) -- side "l" / "r" for the cliff-top part, None = hero only
BUSHES = [((-13.4, 11.8), 1.6, 5, 37701, LEAF, "l"), ((-8.6, 4.6), 1.6, 5, 37702, LEAF, "l"),
          ((10.4, 3.2), 1.6, 5, 37704, LEAF, "r"),
          ((-9.3, -3.0), 2.5, 7, 37711, LIME, None), ((8.8, -3.0), 2.3, 7, 37712, LIME, None),
          ((-14.2, -2.3), 1.4, 5, 37713, LIME, None),
          ((12.9, -4.2), 1.1, 4, 37715, LIME, None)]
# leaves hanging on the column faces: (point on the face, outward direction, size, leaves, seed)
FACE_BUSHES = [((-8.6, -1.3, 14.4), (0.0, -1.0), 2.1, 5, 37721), ((5.0, -1.3, 14.9), (0.0, -1.0), 1.9, 5, 37722)]
DAISIES = [((-12.6, 1.4), 0.6, PETAL), ((12.6, 1.6), 0.6, PETAL), ((-10.4, 2.9), 0.55, PINK),
           ((11.2, 4.0), 0.55, PINK)]
YELLOWS = [(-11.0, 0.2), (-6.9, 3.6), (9.2, 1.0)]


PINE_INNER = 0.76           # the star's notch radius (m032 0.66): fuller, rounder tiers like the sheet's pines


def _star_tier(a, c, z, r, h, pts, rot, rng, mat, top=None):
    """m032._star_tier with fuller notches: a drooping star outline rising to an apex (or a small flat cap just under
    the next tier's skirt), closed underneath by a fan to a centre raised 0.1 h."""
    bm = a.bm
    ring = []
    for k in range(2 * pts):
        ang = rot + math.pi * k / pts
        rr = r * (1.0 if k % 2 == 0 else PINE_INNER) * rng.uniform(0.94, 1.06)
        dz = -0.3 * r * (1.0 if k % 2 == 0 else 0.3)
        ring.append(bm.verts.new((c[0] + math.cos(ang) * rr, c[1] + math.sin(ang) * rr, z + dz)))
    cen = bm.verts.new((c[0], c[1], z + h * 0.1))
    m = len(ring)
    if top is None:
        apex = bm.verts.new((c[0], c[1], z + h))
        for k in range(m):
            bm.faces.new((ring[k], ring[(k + 1) % m], apex))
        cap = [apex]
    else:
        zt, rt = top
        cap = [bm.verts.new((c[0] + math.cos(rot + 2 * math.pi * k / pts) * rt,
                             c[1] + math.sin(rot + 2 * math.pi * k / pts) * rt, zt)) for k in range(pts)]
        for k in range(pts):
            p0, p1, p2 = ring[2 * k], ring[2 * k + 1], ring[(2 * k + 2) % m]
            bm.faces.new((p0, p1, cap[k]))
            bm.faces.new((p1, cap[(k + 1) % pts], cap[k]))
            bm.faces.new((p1, p2, cap[(k + 1) % pts]))
        bm.faces.new(cap)
    for k in range(m):
        bm.faces.new((ring[(k + 1) % m], ring[k], cen))
    vs = ring + [cen] + cap
    _tri(bm, _faces(vs))
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, mat, tint=rng.uniform(0.95, 1.05))
    return vs


def _ground_max(ground, pts):
    zs = [ground(p) for p in pts]
    if any(z is None for z in zs):
        return None
    return max(zs)


def _under(tree, x, y, r, z_from, n=10):
    """The lowest underside of a tier over a circle of radius r round (x, y): rays cast up from z_from."""
    zs = []
    for k in range(n + 1):
        px, py = (x, y) if k == n else (x + math.cos(2 * math.pi * k / n) * r, y + math.sin(2 * math.pi * k / n) * r)
        h = tree.ray_cast(Vector((px, py, z_from)), Vector((0, 0, 1)), 50)
        if h[0] is not None:
            zs.append(h[0].z)
    return min(zs)


def pine(a, name, ground):
    """A pine: a 5-sided trunk and drooping star tiers, each its own closed shell (m032), stacked by contact (STAGES:
    no floating dressing): the tiers are built top down, each frustum's flat cap stops VEG_GAP under the underside of
    the tier above, the trunk's top VEG_GAP under the lowest tier and its foot VEG_GAP over the ground."""
    (x, y), height, s, seed, nt = PINES[name]
    rng = random.Random(seed)
    rt = 0.32 * s
    foot = [(x + math.cos(k * 1.2566) * rt, y + math.sin(k * 1.2566) * rt) for k in range(5)] + [(x, y)]
    z = _ground_max(ground, foot)
    z = (z if z is not None else GRASS_TOP) + VEG_GAP
    rs = PINE_TIERS[nt]
    tier_h = height / (3.2 if nt == 4 else 2.7)
    gap = 0.18 if nt == 4 else 0.235
    zs = [z + 1.1 * s + k * height * gap for k in range(nt)]
    rots = [rng.uniform(0, 6.3) for _ in range(nt)]
    vs = []
    above = None
    for k in reversed(range(nt)):
        h = tier_h if k < nt - 1 else height - (zs[k] - z)
        top = None
        if k < nt - 1:
            rc = 0.22 * s
            top = (_under(above, x, y, rc, zs[k]) - VEG_GAP, rc)
        tv = _star_tier(a, (x, y), zs[k], rs[k] * s, h, 5, rots[k], rng, PINE, top=top)
        if top is not None:                 # every cap corner VEG_GAP under the tier above (contact, no overlap)
            _touch_up(tv[-5:], above, zs[k])
        above = K.bvh_of(tv)
        vs += tv
    r_top = 0.24 * s
    zt = _under(above, x, y, r_top, z) - VEG_GAP
    trunk = a.cyl(rt, r_top, zt - z, sides=4, loc=(x, y, z), mat=BARK)
    _touch_up([v for v in trunk if v.co.z > z + 0.1], above, z)
    _tri(a.bm, _faces(trunk))
    return vs + trunk


def _touch_up(verts, tree, z_from):
    """Move each vertex up (or down) to VEG_GAP under the surface found by a ray cast up from z_from."""
    for v in verts:
        h = tree.ray_cast(Vector((v.co.x, v.co.y, z_from)), Vector((0, 0, 1)), 50)
        if h[0] is not None:
            v.co.z = h[0].z - VEG_GAP


class _Guard:
    """Keeps every vegetation / spray shell clear of the land and of what is already placed (m032)."""

    def __init__(self, o=None):
        self.land = None
        if o is not None:
            off = Vector(o[OFF])
            me = o.data
            self.land = BVHTree.FromPolygons([v.co + off for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
        self.pts, self.faces, self.tree = [], [], None
        self.dropped = 0

    def ok(self, pts, faces):
        t = BVHTree.FromPolygons(pts, faces)
        if self.land is not None and t.overlap(self.land):
            return False
        return not (self.tree is not None and t.overlap(self.tree))

    def add(self, pts, faces):
        n = len(self.pts)
        self.pts += [Vector(p) for p in pts]
        self.faces += [tuple(i + n for i in f) for f in faces]
        self.tree = BVHTree.FromPolygons(self.pts, self.faces)


def _emit(a, pts, faces, mat):
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    for f in faces:
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, mat)
    return vs


def _place(a, guard, tries, mat):
    for pts, faces in tries:
        if guard is None or guard.ok(pts, faces):
            if guard is not None:
                guard.add(pts, faces)
            return _emit(a, pts, faces, mat)
    if guard is not None:
        guard.dropped += 1
    return []


CAP_PITCH = (0.38, 0.72)    # the lime caps on the stepped columns spread low over the flat tops (the sheet's big caps)


def bush(a, c, size, n, seed, ground, mat, guard=None, pitch_range=(0.75, 1.15)):
    """A fan bush: n broad pointed leaves round a hub, each its own closed shell just above the ground (m032)."""
    rng = random.Random(seed)
    vs = []
    y0 = rng.uniform(0, 6.3)
    for k in range(n):
        yaw = y0 + 2 * math.pi * k / n + rng.uniform(-0.08, 0.08)
        L0 = size * rng.uniform(0.85, 1.1)
        pitch0 = rng.uniform(*pitch_range)
        tries = []
        for L, pitch in ((L0, pitch0), (L0 * 0.8, pitch0 + 0.2), (L0 * 0.62, pitch0 + 0.35)):
            W = L * 0.58
            off = 0.3 * size
            bx, by = c[0] + math.cos(yaw) * off, c[1] + math.sin(yaw) * off
            cy, sy = math.cos(yaw), math.sin(yaw)
            foot = [(bx + cy * L * f - sy * w, by + sy * L * f + cy * w) for f in (0.2, 0.42) for w in (-W / 2, W / 2)]
            z = ground((bx, by))
            zf = _ground_max(ground, foot)
            # the leaf sits on the ground under its own base (contact); a foot point on higher ground (a column
            # top over the bush) would lift it off, so that try is skipped
            if z is not None and zf is not None and zf <= z + 0.05:
                tries.append(_leaf_geo((bx, by, z + VEG_GAP), yaw, pitch, L, W))
        vs += _place(a, guard, tries, mat)
    return vs


def face_bush(a, p, out, size, n, seed, guard=None):
    """Leaves hanging off a column face: fanned round the outward direction, drooping, each a closed shell clear of the
    rock (the sheet's lime bushes on the cliff face)."""
    rng = random.Random(seed)
    base_yaw = math.atan2(out[1], out[0])
    d = Vector((out[0], out[1], 0.0)).normalized()
    vs = []
    for k in range(n):
        yaw = base_yaw + (k / max(1, n - 1) - 0.5) * 2.2 + rng.uniform(-0.1, 0.1)
        pitch0 = rng.uniform(-0.55, 0.35)
        L0 = size * rng.uniform(0.85, 1.1)
        q = Vector(p) + Vector((-d.y, d.x, 0.0)) * rng.uniform(-0.3, 0.3) + Vector((0, 0, rng.uniform(-0.25, 0.25)))
        hit = guard.land.ray_cast(q + d * 3.0, -d, 10.0) if guard is not None and guard.land is not None else (None,)
        if hit[0] is None:
            continue
        base = hit[0] + hit[1] * VEG_GAP
        tries = [_leaf_geo(tuple(base), yaw, pitch, L, L * 0.58)
                 for L, pitch in ((L0, pitch0), (L0 * 0.75, pitch0 - 0.2), (L0 * 0.55, pitch0 - 0.35))]
        vs += _place(a, guard, tries, LIME)
    return vs


def daisy(a, c, r, seed, ground, mat, guard=None):
    """A flat five-petal flower (a star lens) with a small yellow pyramid centre (m032)."""
    rng = random.Random(seed)
    ph = rng.uniform(0, 6.3)
    for rr in (r, r * 0.75):
        pts, faces, z = _daisy_geo(c, rr, ph, rng, ground)
        if pts is None:
            continue
        cpts, cfaces = m032._pyramid_geo((c[0], c[1], z + 0.13), rr * 0.3, 0.12, ph)
        if guard is None or (guard.ok(pts, faces) and guard.ok(cpts, cfaces)):
            if guard is not None:
                guard.add(pts, faces)
                guard.add(cpts, cfaces)
            return _emit(a, pts, faces, mat) + _emit(a, cpts, cfaces, POLLEN)
    if guard is not None:
        guard.dropped += 1
    return []


def yellow_flower(a, c, seed, ground, guard=None):
    rng = random.Random(seed)
    rot = rng.uniform(0, 1.5)
    foot = [(c[0] + math.cos(rot + k * 1.571) * 0.22, c[1] + math.sin(rot + k * 1.571) * 0.22) for k in range(4)]
    z = _ground_max(ground, foot + [tuple(c)])
    if z is None:
        return []
    return _place(a, guard, [m032._pyramid_geo((c[0], c[1], z + VEG_GAP), 0.24, 0.32, rot)], POLLEN)


def vegetation(a, ground, guard, side=None):
    """Every leaf and flower as its own closed shell set just above the finished land; side "l" keeps the cliff-top
    part's half only."""
    in_side = (lambda x: x < -2.0) if side == "l" else (lambda x: True)
    for c, size, n, seed, mat, s in BUSHES:
        if side is None or s == side:
            bush(a, c, size, n, seed, ground, mat, guard,
                 pitch_range=CAP_PITCH if seed in (37711, 37712) else (0.75, 1.15))
    if side is None:
        for p, out, size, n, seed in FACE_BUSHES:
            face_bush(a, p, out, size, n, seed, guard)
    for i, (c, r, mat) in enumerate(DAISIES):
        if in_side(c[0]) and (side is None or c[1] > -0.8):
            daisy(a, c, r, 37801 + i, ground, mat, guard)
    for i, c in enumerate(YELLOWS):
        if in_side(c[0]) and (side is None or c[1] > -0.8):
            yellow_flower(a, c, 37851 + i, ground, guard)


def ground_of(o):
    off = Vector(o[OFF])
    me = o.data
    tree = BVHTree.FromPolygons([v.co + off for v in me.vertices], [tuple(p.vertices) for p in me.polygons])

    def ground(p):
        h = tree.ray_cast(Vector((p[0], p[1], 80.0)), Vector((0, 0, -1)), 200)
        return h[0].z if h[0] is not None else None
    return ground


# ---- parts ------------------------------------------------------------------------------------------------------------
TOP_CUT = 14.6              # the cliff-top part shows the upper 3.3 studs of its columns


def top_water_part(a):
    channel_water(a)


def top_part(a):
    """The left grass cap (its own closed slab, 16.9 -> 18.0) on the tops of C1-C3 and the left side columns, with a
    lawn pebble; the pines, ferns and flowers are set on it after the cleanup."""
    S = cliff_solid(a, {"gl": cap_regions()["gl"]}, None, extra={"gl": _dirt_ring_points()})
    _paint_cliff(a, S)
    for nm in ("C1", "C2", "C3", "LW1", "LW2", "LW3"):
        column(a, nm, z0=TOP_CUT - 0.3)
    rock(a, "P3")


def wall_part(a):
    for nm in ("C2", "C1", "C3", "SL"):
        column(a, nm)
    rock(a, "K3")


def curtain_part(a):
    curtain(a)


def ribbon_part(a):
    foam(a, ("ribbon", "ribbon_in"))


def disc_part(a):
    foam(a, ("disc", "holes"))
    veil(a)
    spikes(a, _Guard())


def pool_part(a):
    """The pool slab (bed + water plate) with the two big boulders standing in their foam rings."""
    bed(a)
    for nm in ("K1", "K2"):
        rock(a, nm)


def pool_part_water(a):
    pool_water(a, names=("K1", "K2"))
    pos = [_clip_tile(_offset_poly(holes()[nm]["pool"], FOAM_RINGS[nm])) for nm in ("K1", "K2")]
    neg = [holes()[nm]["foam"] for nm in ("K1", "K2")]
    co, tris = m034.cdt_region(pos, neg, [], min_island=0.3)
    _flat_slab(a, co, tris, FOAM_Z[1], FOAM_Z[0], FOAM)


def rock_large_part(a):
    rock(a, "K1", at_origin=True)


def rock_medium_part(a):
    rock(a, "K3", at_origin=True)


def rock_small_part(a):
    rock(a, "T6", at_origin=True)


# ---- hero ---------------------------------------------------------------------------------------------------------------
def hero_land(a):
    """Every solid land piece as its own closed shell, in union order: the bed slab, the cliff solid, the columns
    (largest first), the low boxes, the rocks."""
    bed(a)
    cliff(a)
    for nm in ("C2", "C5", "C3", "C4", "SL", "C1", "C6", "SR", "LW1", "LW2", "LW3", "RW1", "RW2", "RW3", "FL"):
        column(a, nm)
    for nm in BOXES:
        low_box(a, nm)
    for nm in ROCKS:
        if nm not in PART_ONLY:
            rock(a, nm)


def hero_water(a):
    pool_water(a)
    channel_water(a)
    curtain(a)
    # the ribbon lies wholly inside the splash disc on the hero (its own part shows it): left out of the union, where
    # its outline would only add constraint edges
    foam(a, ("disc", "rings", "blobs", "holes"))
    channel_foam(a)


NOTES = {
    HERO: "cliff / waterfall terrain tile (32 x 32; pool water 1.0 over bed 0.2, channel water 17.4 over bed 17.1, "
          "grass top 18.0): a block of big flat-faced rock columns under one lime grass cap split by a river channel "
          "that pours over a notch as a three-lobed curtain into a full-width pool; a splash disc with spray spikes, a "
          "foam ribbon, foam rings round two boulders; stepped bush-capped columns, low pine boxes, pines, ferns, "
          "flowers. One closed land shell plus vegetation, water, curtain and foam shells (three see-through water "
          "pieces). Back seam = M034's seam raised 16.4. 16 sockets",
    TOPW_P: "Top Water Plane (reusable): the channel's see-through water plate (17.16 -> 17.4), 14 wide at the back seam",
    TOP_P: "Cliff Top (reusable): the left lime grass cap on the flat tops of its rock columns, with pines, dark ferns "
           "and flowers",
    WALL_P: "Cliff Wall Pieces (reusable): three tall flat-faced bevelled rock columns in a row, a stepped column in "
            "front and a foot boulder",
    CURT_P: "Waterfall Mesh (reusable): the three-lobed curtain shell with a rolled lip, 7.1 -> 8.3 wide, 16.3 tall",
    RIB_P: "Foam Ribbon (reusable): the flat scalloped foam ring round the curtain's foot",
    DISC_P: "Splash Disc (reusable): the flat scalloped splash disc with its crown of spray spikes",
    POOL_P: "Water Plane + Foam (reusable): the pool's bed slab and see-through water plate with two boulders in foam "
            "rings",
    ROCK_LP: "Rock Piece, large (reusable): a big faceted boulder with a flat crown",
    ROCK_MP: "Rock Piece, medium (reusable)",
    ROCK_SP: "Rock Piece, small (reusable)",
}

# ---- stages 5 + 6 (spec section 7) --------------------------------------------------------------------------------------
# Stage 5: nothing glows (decision 8). Stage 6 (decision 6): 16 sockets; the pool's water_flow first (the exporter
# gives every water piece of the asset the first water_flow socket's flow).
FLOW = [((0.0, -6.0, 1.03), (0.0, -15.5, 1.03), 12.0), ((0.5, 15.5, 17.43), (0.0, 1.0, 17.43), 5.0)]
CURTAIN_FX = [((-1.8, -1.15, 17.3), (-2.0, -2.7, 1.2), 4.0), ((1.8, -1.15, 17.3), (2.0, -2.7, 1.2), 4.0)]
MIST_FX = ((0.0, -3.6, 1.4), 1.2)
FOAM_FX = [((-3.0, -3.2, 1.05), 1.0), ((3.0, -3.2, 1.05), 1.0), ((-9.6, -10.6, 1.05), 1.0), ((11.0, -10.2, 1.05), 1.0),
           ((-6.0, -4.9, 1.05), 0.6), ((14.0, -6.9, 1.05), 0.6), ((-12.3, -8.7, 1.05), 0.6),
           ((-3.0, -14.0, 1.05), 0.7), ((5.0, -14.0, 1.05), 0.7), ((0.0, 4.2, 17.45), 0.6), ((0.0, 0.0, 17.45), 0.7)]


def _sockets(o, which=("flow", "curtain", "mist", "foam"), flows=(0, 1)):
    off = Vector(o[OFF])
    if "flow" in which:
        for i in flows:
            p, e, w = FLOW[i]
            K.socket(o, "water_flow", Vector(p) - off, end=tuple(Vector(e) - off), width=w)
    if "curtain" in which:
        for p, e, w in CURTAIN_FX:
            K.socket(o, "waterfall_curtain", Vector(p) - off, end=tuple(Vector(e) - off), width=w)
    if "mist" in which:
        p, sc = MIST_FX
        K.socket(o, "waterfall_mist", Vector(p) - off, scale=sc)
    if "foam" in which:
        for p, sc in FOAM_FX:
            K.socket(o, "water_foam", Vector(p) - off, scale=sc)


# ---- union, cleanup (m034) ---------------------------------------------------------------------------------------------
UNION_RETRIES = []


def _union_fine(o):
    """Exact unions one shell at a time at the world origin, merge 0 (m021 / m034), guarded against a union that
    drops most of the mesh."""
    bpy.context.view_layer.update()
    others = M.split_loose(o)
    bpy.context.view_layer.update()
    for p in others:
        for attempt in range(4):
            keep = o.data.copy()
            n0 = len(o.data.polygons) + len(p.data.polygons)
            m = o.modifiers.new("U", "BOOLEAN")
            m.operation, m.solver, m.object = "UNION", "EXACT", p
            m.material_mode = "TRANSFER"
            with M._override(o):
                bpy.ops.object.modifier_apply(modifier=m.name)
            if len(o.data.polygons) >= 0.6 * n0 or attempt == 3:
                bpy.data.meshes.remove(keep)
                break
            bad = o.data
            o.data = keep
            bpy.data.meshes.remove(bad)
            UNION_RETRIES.append((p.name, attempt))
            p.location += Vector((0.004, 0.003, 0.002)) * (attempt + 1)
            bpy.context.view_layer.update()
        me = p.data
        bpy.data.objects.remove(p, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    M.drop_specks(bm, min_area=0.02)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    K.drop_unused_slots(o)
    return len(others)


PLANES = (0.0, BED_TOP, CAP_BOT, CH_TOP, GRASS_TOP, 2.4, 4.0, 2.6, 12.0, 11.5, 10.5)


def _finish(o):
    o[OFF] = list(Vector(o[OFF]) + m012._bottom_centre(o))
    res = M.finish(o, union=False, uv=False)
    for _ in range(3):
        crumbs = m012._drop_inner(o)
        if not (crumbs or m012._thin(o)["under"] or res["nonmanifold_edges"] or res["boundary_edges"]):
            break
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bnd = [e for e in bm.edges if e.is_boundary]
        if bnd:
            if not bmesh.ops.holes_fill(bm, edges=bnd)["faces"]:
                bmesh.ops.contextual_create(bm, geom=bnd)
            bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY")
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(o.data)
        bm.free()
        M.repair_nonmanifold(o)
        m012._force_slivers(o)
        o[OFF] = list(Vector(o[OFF]) + m012._bottom_centre(o))
        res = M.finish(o, union=False, uv=False)
    return res


def _polish(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = m012._tri_quads(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = m012._force_slivers(o, lim=POLISH_LIM)
    if m012._thin(o, POLISH_LIM)["under"]:
        forced += m012._force_slivers(o, lim=POLISH_LIM, max_len=0.5)
    guarded = 0
    if m012._thin(o, POLISH_LIM)["under"]:
        # union seams where two column faces cross at a shallow angle: m032's fold-guarded needle collapse, then
        # longer collapses (still refused where they would fold the surface)
        guarded = m032._polish(o)["forced"]
        for ml in (1.5, 2.5):
            if m012._thin(o, POLISH_LIM)["under"]:
                guarded += m032._safe_force(o, lim=POLISH_LIM, max_len=ml)
    _recentre(o)
    return {"split": split, "forced": forced, "guarded": guarded}


def _recentre(o):
    bc = m012._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


def _uv(o):
    for p in o.data.polygons:
        p.use_smooth = False
    M.smart_uv(o, **UV)
    return m012._uv_unfold(o)


def _join_built(o, fn, name):
    """Build fn into a temporary object in o's build frame and join it into o (no union)."""
    a = K.fk().Asset(PFX + name, "probe", seed=7, tint_var=0.0)
    fn(a)
    if not a.bm.verts:
        a.bm.free()
        return o
    c = a.finish(collection=o.users_collection[0], mark_asset=False, origin=None)
    c.matrix_world = o.matrix_world @ Matrix.Translation(-Vector(o[OFF]))
    bpy.context.view_layer.update()
    bm = bmesh.new()
    bm.from_mesh(c.data)
    ng = [f for f in bm.faces if len(f.verts) > 4]
    if ng:
        bmesh.ops.triangulate(bm, faces=ng, quad_method="BEAUTY", ngon_method="BEAUTY")
        bm.to_mesh(c.data)
    bm.free()
    with M._override(o):
        c.select_set(True)
        with bpy.context.temp_override(selected_objects=[o, c], selected_editable_objects=[o, c]):
            bpy.ops.object.join()
    return o


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m037_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith(("_m037", "_probe", "T_Calib",
                                                                                 "CliffFalls"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def _clean_land(o, cut_z, planes):
    """Union, floor cut, cleanup, finish, polish, bowties (m034 / m032). o[OFF] tracks the build point at the origin."""
    lg = {"shells_merged": _union_fine(o)}
    off = Vector(o[OFF])
    if cut_z is not None:
        m016._floor_cut(o, cut_z - off.z)
        o[OFF] = [off.x, off.y, cut_z]
    zoff = o[OFF][2]
    lg["self_hits_union"] = m016._self_hits(o)[0]
    lg["clean"] = {k: v for k, v in m016._clean_mesh(o, tuple(z - zoff for z in planes)).items()
                   if not isinstance(v, (list, dict))}
    lg["self_hits_clean"] = m016._self_hits(o)[0]
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    lg["bowties"] = M.fix_bowties(o)
    lg["floor_faces"] = _floor_faces(o)
    return lg


def _floor_faces(o):
    """The faces on the flat underside: rock (the floor cut's cap takes whatever key the boolean gives it)."""
    from m011 import _Paint
    p = _Paint(o, off=o[OFF])
    n = 0
    zmin = min(v.co.z for v in p.bm.verts)
    for f in p.bm.faces:
        if all(abs(v.co.z - zmin) < 1e-3 for v in f.verts):
            f.material_index = p._mi(ROCK)
            n += 1
    p.done()
    return n


def _add_vegetation(o, pines, side=None):
    ground = ground_of(o)
    g0 = _Guard(o)
    dropped = []
    for name in pines:
        a = K.fk().Asset("_chk", "probe")
        pine(a, name, ground)
        a.bm.verts.ensure_lookup_table()
        a.bm.faces.ensure_lookup_table()
        pts = [v.co.copy() for v in a.bm.verts]
        idx = {v: i for i, v in enumerate(a.bm.verts)}
        faces = [tuple(idx[v] for v in f.verts) for f in a.bm.faces]
        a.bm.free()
        if not g0.ok(pts, faces):
            dropped.append(name)
        _join_built(o, lambda a_, n=name: pine(a_, n, ground), "pine_" + name)
    guard = _Guard(o)
    _join_built(o, lambda a_: vegetation(a_, ground, guard, side), "veg")
    return {"pines_touching_land": dropped, "leaves_dropped": guard.dropped}


# name, builder, collision, kind ("land" unions + cleans, "water" only joins), floor cut z, planes
PARTS = ((TOPW_P, top_water_part, "none", "water", None, ()),
         (TOP_P, top_part, "hull", "land", TOP_CUT, (TOP_CUT, CAP_BOT, GRASS_TOP)),
         (WALL_P, wall_part, "hull", "land", 0.0, (0.0, 12.0)),
         (CURT_P, curtain_part, "none", "water", None, ()),
         (RIB_P, ribbon_part, "none", "water", None, ()),
         (DISC_P, disc_part, "none", "water", None, ()),
         (POOL_P, pool_part, "precise", "land", 0.0, (0.0, BED_TOP)),
         (ROCK_LP, rock_large_part, "hull", "land", None, ()),
         (ROCK_MP, rock_medium_part, "hull", "land", None, ()),
         (ROCK_SP, rock_small_part, "hull", "land", None, ()))
TARGET_SIZE = ((32.0, 0.3), (32.0, 0.3), (25.0, 1.0))


def _make(name, fn, collision, kind, cut_z, planes):
    t0 = time.time()
    o = M.mk(SHEET, name, fn, subject=TITLE, role="part", notes=NOTES[name], budget=1000, collision=collision,
             tint_var=0.0)
    off = M._build_offset(fn)
    o[OFF] = list(off)
    o.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    lg = {}
    if kind == "water":
        _recentre(o)
        m016._weld(o, 1e-4)
    else:
        lg.update(_clean_land(o, cut_z, planes or (0.0,)))
    if name == TOP_P:
        lg["veg"] = _add_vegetation(o, ("PL1", "PL2"), side="l")
    if name == POOL_P:
        saved = {nm: dict(h) for nm, h in holes().items()}
        refine_holes(o, ("K1", "K2"))
        _join_built(o, pool_part_water, "poolwater")
        HOLES.update(saved)
    _recentre(o)
    K.drop_unused_slots(o)
    lg["uv_cut"] = _uv(o)
    if name == TOPW_P:
        _sockets(o, ("flow",), flows=(1,))
    elif name == CURT_P:
        _sockets(o, ("curtain",))
    elif name == DISC_P:
        _sockets(o, ("mist",))
    elif name == POOL_P:
        _sockets(o, ("flow",), flows=(0,))
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


def _make_hero():
    t0 = time.time()
    o = M.mk(SHEET, HERO, hero_land, subject=TITLE, role="hero", notes=NOTES[HERO], budget=4000, collision="precise",
             tint_var=0.0)
    off = M._build_offset(hero_land)
    o[OFF] = list(off)
    o.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    lg = {"t_build": round(time.time() - t0, 1)}
    lg.update(_clean_land(o, 0.0, PLANES))
    lg["t_land"] = round(time.time() - t0, 1)
    lg["land"] = {k: v for k, v in M.audit(o).items() if k in ("tris", "shells", "nonmanifold_edges",
                                                                  "nonmanifold_verts", "boundary_edges")}
    lg["land_self_hits"] = m016._self_hits(o)[0]
    lg["holes_refined"] = refine_holes(o)
    _join_built(o, hero_water, "water")
    _join_built(o, veil, "veil")
    g = _Guard(o)
    _join_built(o, lambda a: spikes(a, g), "spikes")
    lg["spikes_dropped"] = g.dropped
    lg["veg"] = _add_vegetation(o, tuple(PINES))
    lg["bowties_all"] = M.fix_bowties(o)
    _recentre(o)
    K.drop_unused_slots(o)
    lg["uv_cut"] = _uv(o)
    _sockets(o)
    lg["t_total"] = round(time.time() - t0, 1)
    return o, lg


LAND_KEYS_VEG = {LEAF, LIME, PINE, BARK, PETAL, PINK, POLLEN}


def shells_report(o):
    """Per shell: its kind (land / veg / water / curtain / foam), tris, non-manifold edges and verts, boundary edges."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = [m.get("flintkit_key", m.name) if m else None for m in o.data.materials]
    out = []
    for k in range(n):
        fs = [f for f in bm.faces if ids[f.index] == k]
        es = {e for f in fs for e in f.edges}
        vs = {v for f in fs for v in f.verts}
        ks = sorted({keys[f.material_index] for f in fs})
        kind = ("foam" if ks == [FOAM] else "water" if ks == [WATER] else "curtain" if ks == [FALL] else
                "veg" if set(ks) <= LAND_KEYS_VEG else "land")
        out.append({"kind": kind, "tris": sum(len(f.verts) - 2 for f in fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary)})
    bm.free()
    return out


def floating(o, contact=CONTACT):
    """STAGES "no floating dressing": every vegetation shell (leaf, needle tier, trunk, petal, flower centre) must lie
    within `contact` of another shell and chain by such contacts to the land shell. Contacts are found from each
    shell's vertices to the faces of every other shell. Returns {"loose": shells with no contact at all, "unchained":
    shells whose chain never reaches the land, "where": a few of their centres (build frame)}."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = [m.get("flintkit_key", m.name) if m else None for m in o.data.materials]
    kind = {}
    for f in bm.faces:
        k = keys[f.material_index]
        kind[ids[f.index]] = ("veg" if k in LAND_KEYS_VEG else "water" if k in WATER_KEYS else
                              kind.get(ids[f.index], "land"))
    tree = BVHTree.FromBMesh(bm)
    nbr = {i: set() for i in range(n)}
    vshell = {}
    for f in bm.faces:
        for v in f.verts:
            vshell[v.index] = ids[f.index]
    for v in bm.verts:
        i = vshell.get(v.index)
        if i is None or kind[i] != "veg":
            continue
        for _co, _no, fi, _d in tree.find_nearest_range(v.co, contact):
            j = ids[fi]
            if j != i and kind[j] != "water":
                nbr[i].add(j)
                nbr[j].add(i)
    land = {i for i in range(n) if kind[i] == "land"}
    seen, stack = set(land), list(land)
    while stack:
        i = stack.pop()
        for j in nbr[i]:
            if j not in seen and kind[j] != "water":
                seen.add(j)
                stack.append(j)
    veg = [i for i in range(n) if kind[i] == "veg"]
    loose = [i for i in veg if not nbr[i]]
    unchained = [i for i in veg if i not in seen]
    off = Vector(o.get(OFF, (0.0, 0.0, 0.0)))
    cen = {}
    for f in bm.faces:
        if ids[f.index] in unchained and ids[f.index] not in cen:
            cen[ids[f.index]] = [round(c, 2) for c in f.calc_center_median() + off] + [keys[f.material_index][5:]]
    bm.free()
    return {"veg_shells": len(veg), "loose": len(loose), "unchained": len(unchained), "where": list(cen.values())[:12]}


def _inverted(o):
    """Faces whose normal points into their own shell's solid (odd ray parity, per shell). (m033 / m034)"""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n_sh = M._shell_ids(bm)
    bad = 0
    for k in range(n_sh):
        fs = [f for f in bm.faces if ids[f.index] == k]
        vs = list({v for f in fs for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        for f in fs:
            d = (f.normal + Vector((0.031, 0.017, 0.023))).normalized()
            p = f.calc_center_median() + d * 1e-4
            n, x, last = 0, p.copy(), None
            for _ in range(50):
                hit = tree.ray_cast(x, d)
                if hit[0] is None:
                    break
                if last is None or (hit[0] - last).length > 1e-4:
                    n += 1
                last = hit[0].copy()
                x = hit[0] + d * 1e-4
            bad += n % 2
    bm.free()
    return bad


SHADING_OK = ("the sheet's own material regions: lime grass tops and the cap's lime edge over grey rock walls, "
              "soil-sided low boxes under grass tops, the dark bed colour under the water and on the wall behind the "
              "curtain; painted by position (height bands, plan regions), never by facing")


def build(render=True, parts=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    UNION_RETRIES.clear()
    palette()
    HOLES.clear()
    holes()
    objs, log = {}, {}
    if parts:
        for name, fn, coll, kind, cut_z, planes in PARTS:
            objs[name], log[name] = _make(name, fn, coll, kind, cut_z, planes)
            _cleanup_tmp()
    h, log["hero"] = _make_hero()
    log["union_retries"] = list(UNION_RETRIES)
    _cleanup_tmp()
    order = [h] + [objs[n] for n, *_ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
        o["kit_shading_ok"] = SHADING_OK
    out = report(order)
    out["log"] = log
    out["build_s"] = round(time.time() - t0, 1)
    if render:
        out["views"] = render_views(order)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


def report(order):
    h = order[0]
    audits = [M.audit(o) for o in order]
    self_hits = {o.name: m016._self_hits(o)[0] for o in order}
    thin = {o.name: m012._thin(o, POLISH_LIM) for o in order}
    inverted = {o.name: _inverted(o) for o in order}
    floats = {o.name: floating(o) for o in order if o.name in (HERO, TOP_P)}
    problems = list(K.check(order))
    for nm, fl in floats.items():
        if fl["loose"] or fl["unchained"]:
            problems.append(f"{nm}: floating dressing {fl['loose']} loose / {fl['unchained']} unchained shells")
    shells = shells_report(h)
    kinds = [s["kind"] for s in shells]
    if kinds.count("land") != 1 or not {"water", "curtain", "foam", "veg"} <= set(kinds):
        problems.append(f"{HERO}: shells {kinds.count('land')} land / {sorted(set(kinds))}, expected one land shell "
                        f"plus veg, water, curtain and foam shells")
    for s in shells:
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges"):
            if s[k]:
                problems.append(f"{HERO} {s['kind']} shell: {k} {s[k]}")
    for o, au in zip(order, audits):
        lim = 4000 if o is h else 1000
        if au["tris"] > lim:
            problems.append(f"{o.name}: {au['tris']} tris over {lim}")
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "wire_edges", "loose_verts",
                  "zero_area_faces", "ngons"):
            if au[k]:
                problems.append(f"{o.name}: {k} {au[k]}")
        if o.name in (WALL_P, ROCK_LP, ROCK_MP, ROCK_SP, TOPW_P, CURT_P, RIB_P) and au["shells"] != 1:
            problems.append(f"{o.name}: {au['shells']} shells")
        if au["normals"] != "outward":
            problems.append(f"{o.name}: normals {au['normals']}")
        if self_hits[o.name]:
            problems.append(f"{o.name}: {self_hits[o.name]} self-intersecting face pairs")
        if thin[o.name]["under"]:
            problems.append(f"{o.name}: {thin[o.name]['under']} faces with a corner under {POLISH_LIM} deg")
        if inverted[o.name]:
            problems.append(f"{o.name}: {inverted[o.name]} inverted faces")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    socks = [c.get("vfx_kind") for c in h.children if c.get("vfx_kind")]
    want = {"water_flow": 2, "waterfall_curtain": 2, "waterfall_mist": 1, "water_foam": 11}
    if {k: socks.count(k) for k in want} != want:
        problems.append(f"{HERO}: sockets {dict((k, socks.count(k)) for k in want)}, expected {want}")
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    return {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                          "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                          "ngons", "dup_verts")} for au in audits],
            "shells": {k: {"n": sum(1 for x in shells if x["kind"] == k),
                           "tris": sum(x["tris"] for x in shells if x["kind"] == k),
                           "bad": sum(x["nonmanifold_edges"] + x["nonmanifold_verts"] + x["boundary_edges"]
                                      for x in shells if x["kind"] == k)}
                       for k in ("land", "veg", "water", "curtain", "foam")},
            "thin": thin, "self_hits": self_hits, "inverted": inverted, "floating": floats, "problems": problems,
            "uv": uv,
            "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
            "sockets": {k: socks.count(k) for k in set(socks)}}


# ---- renders -------------------------------------------------------------------------------------------------------------
# the sheet's comparison cameras (decision 3): the hero (30, 26) from the front-right; the "rear three-quarter" cell is
# a front-left view (-25, 24); the "rear" cell is a second front view (front_sheet); the "side (right)" cell is from -X
# (270, 12); the "top" cell is a high front view (0, 50). *_sheet shots use a 3x longer lens and hide the studio floor
# (the sheet draws no ground shadow).
SHEET_VIEWS = {"f34_sheet": (30, 26), "r34_sheet": (-25, 24), "front_sheet": (0, 10), "side_sheet": (270, 12),
               "top_sheet": (0, 50)}
SHEET_LENS = 3.0
JUNC_CU = (-20, 20, (-8.6, -1.0, 17.0), 3.6)      # close-up 1: the grass cap on C2 / C3's tops
LIP_CU = (15, -20, (0.0, -1.4, 15.2), 4.6)        # close-up 2: the lip from below (top water underside, curtain top)
POOL_CU = (-35, 25, (-11.0, -14.6, 1.0), 4.4)     # close-up 3: the pool's front-left edge (the water's thickness)
PARTS_SHOT = (35, 28)


def _long_lens(kit):
    orig = kit["render_group"]

    def rg(group, path, azimuth=-22, elevation=20):
        cam = bpy.data.objects["FB_Cam"].data
        lens = cam.lens
        ground = bpy.data.objects.get("FB_Ground")
        gh = ground.hide_render if ground else None
        name = path.rsplit("/", 1)[-1]
        if "_sheet" in name:
            cam.lens = lens * SHEET_LENS
            if ground:
                ground.hide_render = True
        try:
            return orig(group, path, azimuth, elevation)
        finally:
            cam.lens = lens
            if ground:
                ground.hide_render = gh
    return orig, rg


# exploded layout (build-frame offsets, like the sheet: top water over the cliff top over the walls; the curtain, the
# ribbon and the disc stacked over the pool; the rock pieces in front-left)
EXPL = {POOL_P: (2.0, -2.0, 0.0), DISC_P: (2.0, -2.0, 1.8), RIB_P: (2.0, -2.0, 3.4), CURT_P: (4.0, -2.0, 4.5),
        WALL_P: (-3.0, 3.0, 0.8), TOP_P: (-3.0, 3.0, 4.5), TOPW_P: (2.0, 5.0, 8.0)}
EXPL_ROCKS = (("rl", ROCK_LP, (-12.0, -11.0, 0.0)), ("rm", ROCK_MP, (-17.0, -5.0, 0.0)),
              ("rs", ROCK_SP, (-16.0, -13.0, 0.0)))


def _exploded(objs):
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []
    x0 = objs[0].location.x + 80
    o0 = Matrix.Translation((x0, objs[0].location.y, 0))

    def put(tag, part, m):
        if part not in by:
            return
        c = bpy.data.objects.new(f"{PFX}expl_{tag}", by[part].data)
        coll.objects.link(c)
        c.matrix_world = m
        shown.append(c)
    for part, d in EXPL.items():
        if part in by:
            put(part[10:], part, o0 @ Matrix.Translation(d) @ Matrix.Translation(Vector(by[part][OFF])))
    for tag, part, d in EXPL_ROCKS:
        put(tag, part, o0 @ Matrix.Translation(d))
    bpy.context.view_layer.update()
    return shown


def render_close(objs, path, az, el, centre, radius):
    """A close-up from (az, el), framed on a sphere (centre, radius) (m023 / m031)."""
    kit = K.NS["KIT"]
    fb = kit["frame_box"]
    c = Vector(centre)
    box = [c + Vector((dx, dy, dz)) * radius for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    kit["frame_box"] = lambda corners, a_, e_: fb(box, a_, e_)
    ground = bpy.data.objects.get("FB_Ground")
    if ground:
        ground.hide_render = el < 0
    cell = kit["CELL"]
    kit["CELL"] = (480, 400)
    try:
        return kit["render_group"](objs, path, az, el)
    finally:
        kit["CELL"] = cell
        kit["frame_box"] = fb
        if ground:
            ground.hide_render = False


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        if shown:
            extra["exploded"] = (shown, 35, 26)
        for o in objs[1:]:
            extra["part_" + o.name.replace("CliffFalls", "").lower()] = ([o], *PARTS_SHOT)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            sheet = M.views(NUM, [h], extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet}
        if close:
            d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
            off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
            for tag, (az, el, c, r) in (("junc_cu", JUNC_CU), ("lip_cu", LIP_CU), ("pool_cu", POOL_CU)):
                out[tag] = render_close([h], f"{d}/{tag}.png", az, el, off @ Vector(c), r)
            out["under_cu"] = render_close([h], f"{d}/under_cu.png", 20, -40, off @ Vector((0.0, 0.0, 0.5)), 16.0)
        return out
    finally:
        for o in shown:
            bpy.data.objects.remove(o, do_unlink=True)
        M.display(NUM, objs, TITLE)


def preview(names=("f34_sheet", "front_sheet", "side_sheet", "top_sheet", "r34_sheet"), vfx=True):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = _long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig


def hero_only(render=False):
    """Rebuild just the hero (tuning loop): returns its report."""
    M.coll(NUM, TITLE)
    palette()
    HOLES.clear()
    holes()
    h, lg = _make_hero()
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, *_ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    out = {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                        "boundary_edges", "normals")}, "log": lg,
           "self_hits": m016._self_hits(h)[0], "thin": m012._thin(h, POLISH_LIM)["under"], "floating": floating(h),
           "shells": {k: [sum(1 for s in shells_report(h) if s["kind"] == k),
                          sum(s["tris"] for s in shells_report(h) if s["kind"] == k)]
                      for k in ("land", "veg", "water", "curtain", "foam")}}
    if render:
        out["preview"] = preview()
    return out
