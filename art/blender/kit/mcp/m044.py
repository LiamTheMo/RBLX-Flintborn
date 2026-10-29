"""044 Natural Ramp (references/044.png): a broad walkable sloped path through terrain, from the ground up to the
10.4 plateau of M040 Cliff Wall / M043 Terraced Ledge / M032 / M041. A path of big warm-sand flagstones (2 across,
6 rows up a 29.9 deg slope plus a flat landing) on a stone wedge, between two lime grass borders (raised 0.3 over the
path, overlapping its edge) carrying round two-tone bushes, pale boulders and yellow / white flowers, each border
riding on a mass of pale warm columnar rock whose peaked column tips step up with the slope and show only in a thin
outer strip beside the turf. Lime aprons along both cliff feet.

    import importlib, kit_models, m044; importlib.reload(kit_models); importlib.reload(m044); m044.build()

Build frame (studs): toe at -Y, landing at +Y, +X right, ground z 0. W02 owns NaturalRamp*, so the names are
StoneRamp* (spec 8):
- StoneRampPath ("Top Landing Pad (Path)"): 14 flagstone tiles (2 x 7, each a closed slab 0.6 thick with a 0.07
  top-edge bevel) and 16 pale pebbles.
- StoneRampWedge ("Ramp Wedge (Stone)"): one closed wedge under the path, flat base, faceted long faces.
- StoneRampCliffL / StoneRampCliffR ("Left / Right Cliff Rock Mass"): one closed explicit solid each (six columns
  C1-C6 with stepped peaked tops, creases, two tall facets per outer face; no boolean) plus the pointed toe rock.
- StoneRampBorderL / StoneRampBorderR ("Grass Border (Left / Right)"): the draped turf slab with its round
  dome bushes, boulders and three yellow flowers (sprigs, white flowers and the other yellow flowers are hero-only,
  spec 4.3: the parts stay under 1000 tris).
The hero (StoneRamp) is one object of closed shells: all of the above plus the aprons and their dressing.

SEAM CONTRACT (spec 2.1; record in the export notes). Build frame:
- side planes x = -8 / +8: no rock vertex past them (foliage and aprons overhang <= 0.6, symmetric);
- back plane y = +10.0, flat: the wedge back, both C6 backs, the landing tiles' backs and both turf ends lie on it;
  nothing behind it;
- toe y = -10.0: the path's toe lip (0.35 high), the turf tongues (top 0.65) reach it;
- path top z(y) = 0.35 + SLOPE (y + 10) for y <= +7.5 (29.9 deg), 10.4 for y +7.5 .. +10 (landing);
- border top = path top + 0.3 up to y +8.5, then lowering to 10.45 at the back plane.
Placement: put the back plane on M040's lip front (M040 build frame y -4.2; same x): the landing (10.4) meets M040's
lawn flush. In the hero object the build frame is at the object's origin + hero["m044_offset"].

Stages 5-6: nothing (spec 7: the sheet shows no glow, light or effect). See M044_spec.md.
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
import m012
import m033
import m040
from m040 import _cap, _cdt, _clamp, _faces, _hull_piece, _inside, _mottle, _tree_of, _tri_ngons, _touch

NUM, TITLE, SHEET = 44, "Natural Ramp", "M044"
OFF = "m044_offset"
PFX = "_m044_"
HERO = "StoneRamp"
PATH_P, WEDGE_P = "StoneRampPath", "StoneRampWedge"
CLIFF_L, CLIFF_R = "StoneRampCliffL", "StoneRampCliffR"
BORDER_L, BORDER_R = "StoneRampBorderL", "StoneRampBorderR"
PARTS = (PATH_P, WEDGE_P, CLIFF_L, CLIFF_R, BORDER_L, BORDER_R)

ROCK, ROCK_LIGHT, ROCK_DEEP = "m044_rock", "m044_rock_light", "m044_rock_deep"
PATH, PATH_LIGHT, PATH_DEEP = "m044_path", "m044_path_light", "m044_path_deep"
GRASS, GRASS_LIGHT, GRASS_DEEP = "m044_grass", "m044_grass_light", "m044_grass_deep"
LEAF, LEAF_LIT, LEAF_DEEP, LEAF_LIME = "m044_leaf", "m044_leaf_lit", "m044_leaf_deep", "m044_leaf_lime"
FLOWER, FLOWER_HEART, FLOWER_WHITE = "m044_flower", "m044_flower_heart", "m044_flower_white"
TRUNK = "m044_trunk"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low specular). Stage 4 (M044_spec.md "Stage 4"): K.calibrate (calibrate() below) on the kit
# test dome against TARGETS (spec 5.4: rendered medians of unshadowed regions on the sheet); the dome's rendered sRGB
# in brackets. rock #A7948D (211,181,164) came out at hue 16 deg and rock_deep #97847E (191,161,146) at 14 deg (the
# mauve edge, spec 3.8 / 5.3): both turned to hue 20 / 19 deg at the same value and saturation (#A7968D, #97867E),
# so every rock key is R > G > B at 19-22 deg. rock_light #B7A9A1 (232,208,189). path #C39C71 (246,188,125), light
# #D0A479 (255,198,135), deep #9F7858 (198,141,95). grass #9CA704 (194,202,8), light #B0B804 (221,225,8), deep #899902
# (168,184,7). The leaf, lime, flower and trunk start keys were already within 6 levels of their targets: leaf
# #3A6718 (66,119,24), lit #689634 (124,180,53), deep #175D21 (26,106,33), lime #879A03 (166,185,7), flower #B8B717
# (231,223,24), heart #8B8E17 (171,170,24), trunk #582703 (110,55,30). The cream flower overshot to (255,253,215)
# (clipped): set by hand to #C6BEAE.
PALETTE = {
    ROCK: ("#A7968D", 0.9, False),
    ROCK_LIGHT: ("#B7A9A1", 0.9, False),
    ROCK_DEEP: ("#97867E", 0.9, False),
    PATH: ("#C39C71", 0.9, True),
    PATH_LIGHT: ("#D0A479", 0.9, True),
    PATH_DEEP: ("#9F7858", 0.9, True),
    GRASS: ("#9DA800", 0.85, True),
    GRASS_LIGHT: ("#B1B900", 0.85, True),
    GRASS_DEEP: ("#8A9A00", 0.85, True),
    LEAF: ("#3A6718", 0.85, True),
    LEAF_LIT: ("#7A9C24", 0.85, True),
    LEAF_DEEP: ("#145F28", 0.85, True),
    LEAF_LIME: ("#879A03", 0.85, True),
    FLOWER: ("#B8B717", 0.8, True),
    FLOWER_HEART: ("#8B8E17", 0.8, True),
    FLOWER_WHITE: ("#C6BEAE", 0.8, True),
    TRUNK: ("#582703", 0.95, False),
}
# calibration targets (spec 5.4). "all" keys are sampled with the studio floor dropped (M.sample).
TARGETS = {ROCK: ((0xD3, 0xB6, 0xA4), "all"), ROCK_LIGHT: ((0xE8, 0xD0, 0xBC), "all"),
           ROCK_DEEP: ((0xBF, 0xA1, 0x92), "all"),
           PATH: ((0xF7, 0xBB, 0x7B), "brown"), PATH_LIGHT: ((0xFD, 0xC6, 0x85), "brown"),
           PATH_DEEP: ((0xC6, 0x8B, 0x5C), "brown"),
           GRASS: ((0xC2, 0xCD, 0x07), "vivid"), GRASS_LIGHT: ((0xD8, 0xE1, 0x06), "vivid"),
           GRASS_DEEP: ((0xA9, 0xB7, 0x08), "vivid"),
           LEAF: ((0x43, 0x79, 0x1C), "green"), LEAF_LIT: ((0x7F, 0xB8, 0x34), "green"),
           LEAF_DEEP: ((0x1B, 0x6A, 0x26), "green"), LEAF_LIME: ((0xA6, 0xBC, 0x04), "vivid"),
           FLOWER: ((0xE8, 0xE0, 0x18), "vivid"), FLOWER_HEART: ((0xAB, 0xA9, 0x18), "vivid"),
           FLOWER_WHITE: ((0xF3, 0xEC, 0xDA), "all"), TRUNK: ((0x6E, 0x37, 0x19), "brown")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome; "all" keys sampled with the floor
    dropped. Returns {key: (hex, rendered)} and leaves the keys set (copy the hexes into PALETTE)."""
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


def _mix(k1, k2, t, step=0.1):
    t = round(max(0.0, min(1.0, t)) / step) * step
    return K.mix_key(k1, k2, round(t, 2))


def _tri(bm, faces):
    bmesh.ops.triangulate(bm, faces=[f for f in faces if f.is_valid and len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")


def _face(bm, vs):
    """A face over verts (dropping consecutive duplicates)."""
    out = []
    for v in vs:
        if not out or out[-1] is not v:
            out.append(v)
    if len(out) > 2 and out[0] is out[-1]:
        out.pop()
    return bm.faces.new(out)


def _zip(bm, L, R, key=lambda v: v.co.z):
    """Triangles between two vertex chains (each ordered by key, sharing their first and last rungs as edges of
    neighbouring faces): always advance the chain whose next vertex comes first, so no triangle spans a long chain
    (no needles on tall narrow faces)."""
    fs = []
    i = j = 0
    while i < len(L) - 1 or j < len(R) - 1:
        # advance the side whose new diagonal is shorter (the fatter triangle)
        if i == len(L) - 1 or (j < len(R) - 1 and (R[j + 1].co - L[i].co).length <= (L[i + 1].co - R[j].co).length):
            fs.append(bm.faces.new((L[i], R[j], R[j + 1])))
            j += 1
        else:
            fs.append(bm.faces.new((L[i], R[j], L[i + 1])))
            i += 1
    return fs


def _planar(bm, vs, drop, steiner=()):
    """Delaunay triangles over a planar polygon of existing verts (drop: the axis 0/1/2 the plane is flat in), with
    optional interior points (3D positions in the plane) that become new verts."""
    ax = [i for i in range(3) if i != drop]
    pts = [(v.co[ax[0]], v.co[ax[1]]) for v in vs]
    if m040._area2(pts) < 0:            # the CDT wants the outline counter-clockwise
        vs, pts = vs[::-1], pts[::-1]
    vs = list(vs) + [bm.verts.new(p) for p in steiner]
    co, tris = _cdt(pts, (), [(p[ax[0]], p[ax[1]]) for p in steiner])
    out = [bm.faces.new((vs[i], vs[j], vs[k])) for i, j, k in tris]
    if len(out) != len(pts) - 2 + 2 * len(steiner):
        raise RuntimeError(f"_planar: {len(out)} triangles for a {len(pts)}-gon")
    return out


def _shell_done(a, faces, verts, key=None):
    """Triangulate a freshly built closed shell, orient its normals outward and give it a key and a flat Tint."""
    _tri(a.bm, faces)
    fs = _faces(verts)
    bmesh.ops.recalc_face_normals(a.bm, faces=fs)
    if key:
        a._finish(verts, key, tint=1.0)
    else:
        for f in fs:
            f.smooth = False
            for lp in f.loops:
                lp[a.tint_layer] = (1.0, 1.0, 1.0, 1.0)
    return fs


# ---- layout (spec 2.1) ---------------------------------------------------------------------------------------------------
RISE = 10.4                 # the landing / plateau level (M040's lawn)
TOE_Z = 0.35                # the path's toe lip on the ground
Y0, Y1 = -10.0, 10.0        # toe, back plane
RUN = 17.5                  # the sloped run (y -10 .. +7.5)
LANDING = Y1 - Y0 - RUN     # 2.5
Y_LAND = Y0 + RUN
SLOPE = (RISE - TOE_Z) / RUN           # 0.5743 -> 29.87 deg
HALF_W = 8.0                # side planes x = +-8
PATH_HALF = 4.0             # the path is 8 wide
BORDER_UP = 0.30            # the turf top over the path
BORDER_BACK = 10.45         # the turf top at the back plane


def path_z(y):
    return RISE if y >= Y_LAND else TOE_Z + SLOPE * (y - Y0)


def border_z(y):
    """The turf top line B(y)."""
    if y <= 8.5:
        return path_z(y) + BORDER_UP
    return RISE + BORDER_UP + (BORDER_BACK - RISE - BORDER_UP) * (y - 8.5) / (Y1 - 8.5)


# ---- path tiles (spec 2.2) -----------------------------------------------------------------------------------------------
ROWS = [Y0 + RUN * k / 6.0 for k in range(7)] + [Y1]          # 6 sloped rows + the landing
LIP = 0.10                  # each sloped row's uphill edge sits this far under the next row's downhill edge
TILE_T = 0.60               # tile thickness (vertical)
BEVEL = 0.07                # the tiles' top-edge bevel (decision 4: 0.06-0.08), a 45 deg ring
GAP_ROW, GAP_MID = -0.005, -0.005   # half gaps between rows / at the middle seam: the tiles overlap 0.01, so no
#                                     slit shows the wedge; the seams read by the row lips and per-tile tint
TILE_X = 3.98               # the tiles' outer sides (the cliffs' inner faces are at 4.0)
MID_JOG = [0.30, -0.25, 0.20, -0.30, 0.25, -0.20, 0.10]      # the middle seam per row
TILE_DZ = [(0.0, 0.015), (0.012, -0.004), (-0.006, 0.01), (0.01, -0.012), (-0.01, 0.006), (0.006, -0.01),
           (0.0, 0.0)]      # (left, right) per-row height nudge: the middle seam reads (walk test +-0.02)
TILE_INFO = {}


def tile_rows():
    out = []
    for r in range(7):
        ya, yb = ROWS[r], ROWS[r + 1]
        za = path_z(ya)
        zb = RISE if r == 6 else path_z(yb) - LIP
        out.append((ya, yb, za, zb))
    return out


def tile_top(x, y):
    """The path's walkable surface at (x, y) (the tile under it)."""
    rows = tile_rows()
    r = max(0, min(6, next((i for i, (ya, yb, _a, _b) in enumerate(rows) if y < yb), 6)))
    ya, yb, za, zb = rows[r]
    side = 0 if x < MID_JOG[r] else 1
    return za + (zb - za) * (y - ya) / (yb - ya) + TILE_DZ[r][side]


def tile(a, r, side):
    """One flagstone: a closed slab over a plan rectangle, top tilted LIP flatter than the slope, 0.6 thick, the
    bottom clamped to the ground at the toe (spec 2.2). Returns (verts, top face, side faces, bottom faces)."""
    bm = a.bm
    ya, yb, za, zb = tile_rows()[r]
    dz = TILE_DZ[r][side]
    xm = MID_JOG[r]
    x0, x1 = (-TILE_X, xm - GAP_MID) if side == 0 else (xm + GAP_MID, TILE_X)
    y0 = ya + (GAP_ROW if r else 0.0)
    y1 = yb - (GAP_ROW if r < 6 else 0.0)

    def top(y):
        return za + (zb - za) * (y - ya) / (yb - ya) + dz

    def bot(y):
        return max(0.0, top(y) - TILE_T)
    # the top-edge bevel (decision 4, fix round 1 B3): the top face is inset BEVEL on every side, a 45 deg ring falls
    # BEVEL to the slab's outline (T below), and the sides run down from there. The ring meets the neighbour's ring
    # in a small V groove, so the seams read as dark lines; the tiles still overlap 0.01 (no slit to the wedge).
    b = BEVEL
    U = [bm.verts.new((x0 + b, y0 + b, top(y0 + b))), bm.verts.new((x1 - b, y0 + b, top(y0 + b))),
         bm.verts.new((x1 - b, y1 - b, top(y1 - b))), bm.verts.new((x0 + b, y1 - b, top(y1 - b)))]
    T = [bm.verts.new((x0, y0, top(y0) - b)), bm.verts.new((x1, y0, top(y0) - b)),
         bm.verts.new((x1, y1, top(y1) - b)), bm.verts.new((x0, y1, top(y1) - b))]
    ring = [bm.faces.new((T[i], T[(i + 1) % 4], U[(i + 1) % 4], U[i])) for i in range(4)]
    if r == 0:
        # the toe: the bottom lies on the ground until the slab's underside rises off it (where top - 0.6 = 0)
        yk = ya + (TILE_T - za - dz) / ((zb - za) / (yb - ya))
        xmid = 0.5 * (x0 + x1)
        Bf = [bm.verts.new((x0, y0, 0.0)), bm.verts.new((xmid, y0, 0.0)), bm.verts.new((x1, y0, 0.0))]
        Bk = [bm.verts.new((x1, yk, 0.0)), bm.verts.new((x0, yk, 0.0))]
        Bb = [bm.verts.new((x1, y1, bot(y1))), bm.verts.new((x0, y1, bot(y1)))]
        topf = bm.faces.new(U)
        F = bm.faces.new
        sides = [F((Bf[0], Bf[1], T[0])), F((Bf[1], T[1], T[0])), F((Bf[1], Bf[2], T[1])),     # front (toe lip)
                 F((T[1], Bf[2], Bk[0])), F((T[1], Bk[0], T[2])), F((Bk[0], Bb[0], T[2])),      # +x side
                 F((Bb[0], Bb[1], T[3], T[2])),                                                 # back
                 F((T[0], Bk[1], Bf[0])), F((T[0], T[3], Bk[1])), F((Bk[1], T[3], Bb[1]))]      # -x side
        bots = [F((Bf[0], Bk[1], Bf[1])), F((Bf[1], Bk[1], Bk[0])), F((Bf[1], Bk[0], Bf[2])),
                F((Bk[0], Bk[1], Bb[1], Bb[0]))]
        vs = U + T + Bf + Bk + Bb
    else:
        B = [bm.verts.new((v.co.x, v.co.y, bot(v.co.y))) for v in T]
        topf = bm.faces.new(U)
        sides = [bm.faces.new((B[i], B[(i + 1) % 4], T[(i + 1) % 4], T[i])) for i in range(4)]
        bots = [bm.faces.new(list(reversed(B)))]
        vs = U + T + B
    _tri(bm, [topf] + ring + sides + bots)
    fs = _faces(vs)
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    for f in fs:
        f.smooth = False
        for lp in f.loops:
            lp[a.tint_layer] = (1.0, 1.0, 1.0, 1.0)
    TILE_INFO[(r, side)] = {"x": (round(x0, 3), round(x1, 3)), "y": (round(y0, 3), round(y1, 3)),
                            "z_down": round(top(y0), 3), "z_up": round(top(y1), 3)}
    return vs


def _paint_tile(a, vs, r, side, nf):
    """The tile's top: sand with a per-tile tint, broad lighter patches (noise) and a deeper tone within 0.6 of the
    borders; the faces below the top (the slab's sides: a geometric band, by their place in the tile, never by
    their normal) the darker orange-brown; the hidden bottom plain sand."""
    fs = _faces(vs)
    ya, yb, za, zb = tile_rows()[r]
    tops, sides = [], []

    dz = TILE_DZ[r][side]

    def tz(v):          # this tile's own top plane (the tiles overlap their neighbours by 0.01)
        return za + (zb - za) * (v.co.y - ya) / (yb - ya) + dz

    def lab(v):
        t = tz(v)
        return "T" if abs(v.co.z - t) < 1e-3 else "B" if abs(v.co.z - max(0.0, t - TILE_T)) < 1e-3 else "?"
    for f in fs:
        c = f.calc_center_median()
        labs = {lab(v) for v in f.verts}
        if labs == {"T"}:
            key = PATH
            if abs(c.x) > PATH_HALF - 0.6:
                key = _mix(PATH, PATH_DEEP, 0.15, step=0.05)
            elif nf(c) > 0.12:
                key = _mix(PATH, PATH_LIGHT, 0.2 if nf(c) > 0.28 else 0.1)
            f.material_index = a._mi(key)
            tops.append(f)
        elif "T" in labs:
            f.material_index = a._mi(_mix(PATH, PATH_DEEP, 0.5))     # the bevel ring (spec 5.3: 50 %, by role)
            sides.append(f)
        elif labs != {"B"}:
            f.material_index = a._mi(PATH_DEEP)                      # the slab's sides below the ring
            sides.append(f)
        else:
            f.material_index = a._mi(PATH)          # the hidden underside: plain sand
    rng = random.Random(44100 + r * 2 + side)
    t = rng.uniform(0.96, 1.04)
    _mottle(a, tops, 0.03, 0.4, 44110 + r * 2 + side, tint=t)
    _mottle(a, sides, 0.02, 0.5, 44130 + r * 2 + side, tint=t)


# pebbles on the path (spec 2.2): (x, y, size), more near the edges, clear of the seams
# fix round 1 (m5): 16 bigger, squat, broad-topped blobs (0.36-0.6; were 20 of 0.26-0.5 that read as grey specks)
PEBBLES = [(-3.3, -9.2, 0.5), (2.9, -8.5, 0.4), (-1.2, -7.6, 0.38), (3.4, -6.1, 0.58), (-2.8, -5.3, 0.44),
           (1.1, -4.6, 0.38), (2.4, -2.2, 0.48), (-3.4, -2.6, 0.4), (3.3, 0.4, 0.42), (-2.4, 1.2, 0.55),
           (1.6, 2.6, 0.36), (-3.4, 3.6, 0.46), (2.9, 4.4, 0.4), (-1.4, 5.3, 0.4), (3.4, 6.4, 0.5),
           (-2.6, 8.6, 0.42)]
DARK_PEBBLES = (3, 9)       # two pebbles with a greyer shaded half (by position: their -x half)


def _clear_of_seams(x, y, s):
    """Move a pebble's centre off the tile seams (it must sit on one tile: a lip under it would lift one side)."""
    r = next((i for i in range(7) if y < ROWS[i + 1]), 6)
    m = s * 0.6 + 0.12
    y = min(max(y, ROWS[r] + m), ROWS[r + 1] - m)
    if abs(x - MID_JOG[r]) < m:
        x = MID_JOG[r] + math.copysign(m, x - MID_JOG[r] or 1.0)
    x = max(-3.3, min(3.3, x))
    return x, y


def pebble(a, c, s, seed, ground, key=None, dark=False):
    """A low pale blob of a pebble (a 4-sided tapered prism, 12 tris) whose foot ring follows the surface under it
    (ground(x, y)), sunk 0.04; height 0.32-0.4 of its size (never over 0.2) under a broad crown (0.42 of its size)
    that takes the pale rock_light by place (the crown cap), the sides 60 % light (fix round 1, m5)."""
    rng = random.Random(seed)
    bm = a.bm
    n = 4
    off = rng.uniform(0, 2 * math.pi)
    sq = rng.uniform(0.75, 0.9)
    h = min(0.2, s * rng.uniform(0.32, 0.4))
    angs = [off + 2 * math.pi * k / n + rng.uniform(-0.15, 0.15) for k in range(n)]
    lo, hi = [], []
    for t in angs:
        x, y = c[0] + math.cos(t) * s * 0.55, c[1] + math.sin(t) * s * 0.55 * sq
        lo.append(bm.verts.new((x, y, ground(x, y) - 0.04)))
    for t in angs:
        x, y = c[0] + math.cos(t) * s * 0.42, c[1] + math.sin(t) * s * 0.42 * sq
        hi.append(bm.verts.new((x, y, ground(x, y) + h + rng.uniform(-0.02, 0.0))))
    fs = [bm.faces.new((lo[k], lo[(k + 1) % n], hi[(k + 1) % n], hi[k])) for k in range(n)]
    fs += [bm.faces.new(list(reversed(lo))), bm.faces.new(hi)]
    vs = lo + hi
    _shell_done(a, fs, vs, key or _mix(ROCK, ROCK_LIGHT, 0.6))
    if not key:
        for f in _faces(vs):
            if all(v in hi for v in f.verts):
                f.material_index = a._mi(ROCK_LIGHT)          # the crown cap
    if dark:
        for f in _faces(vs):
            if f.calc_center_median().x < c[0]:
                f.material_index = a._mi(_mix(ROCK, ROCK_DEEP, 0.6))
    _mottle(a, _faces(vs), 0.03, 0.8, seed, tint=rng.uniform(0.96, 1.04))
    return vs


def path_part(a):
    TILE_INFO.clear()
    nf = K.noise_field(scale=0.25, seed=44101)
    for r in range(7):
        for side in (0, 1):
            vs = tile(a, r, side)
            _paint_tile(a, vs, r, side, nf)
    for i, (x, y, s) in enumerate(PEBBLES):
        pebble(a, _clear_of_seams(x, y, s), s, 44201 + i, tile_top, dark=i in DARK_PEBBLES)


# ---- wedge (spec 2.2) ------------------------------------------------------------------------------------------------------
WEDGE_X = 4.1
WEDGE_SINK = 0.58           # wedge top = path top - 0.58 (the tiles sink 0.02 into it at their downhill edges)
WEDGE_Y0 = -8.6             # its toe end: 0.57 tall (row 1's tiles lie on the ground in front of it)
WEDGE_ST = [WEDGE_Y0, -5.6, -2.0, 1.6, 4.8, Y_LAND, Y1]
WEDGE_FACET = {-5.6: 0.10, 1.6: 0.12}   # long-face mid points pushed in (broad facets)
WEDGE_RIM = (0.40, 0.25)    # the underside's outer ring: in 0.4, up 0.25 (close-up 2)


def wedge(a):
    """One closed wedge: a 4-point toe end, then 8-point sections (flat base, a bevelled rim ring, long faces broken
    at a mid line, the sloped top under the tiles) to the back plane."""
    bm = a.bm
    rings = []
    for y in WEDGE_ST:
        zt = path_z(y) - WEDGE_SINK
        if y == WEDGE_Y0:
            pts = [(-WEDGE_X + 0.2, 0.0), (0.0, 0.0), (WEDGE_X - 0.2, 0.0), (WEDGE_X, zt), (0.0, zt), (-WEDGE_X, zt)]
        else:
            hb, rin = WEDGE_RIM[1], WEDGE_RIM[0]
            push = WEDGE_FACET.get(y, 0.08)
            zm = 0.5 * (hb + zt)
            pts = [(-WEDGE_X + rin, 0.0), (WEDGE_X - rin, 0.0), (WEDGE_X, hb), (WEDGE_X - push, zm), (WEDGE_X, zt),
                   (-WEDGE_X, zt), (-WEDGE_X + push * 0.8, zm), (-WEDGE_X, hb)]
        rings.append([bm.verts.new((x, y, z)) for x, z in pts])
    fs = []
    r0, r1 = rings[0], rings[1]
    fs += _zip(bm, [r0[0], r0[1], r0[2]], [r1[0], r1[1]])                       # underside
    fs += _zip(bm, [r0[5], r0[4], r0[3]], [r1[5], r1[4]])                       # top
    fs += _zip(bm, [r0[2], r0[3]], [r1[1], r1[2], r1[3], r1[4]])                # +x long face
    fs += _zip(bm, [r0[0], r0[5]], [r1[0], r1[7], r1[6], r1[5]])                # -x long face
    n = len(rings[1])
    for i in range(1, len(rings) - 1):
        A, B = rings[i], rings[i + 1]
        for k in range(n):
            fs.append(bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k])))
    fs += _planar(bm, rings[0], 1)
    back = _planar(bm, rings[-1], 1, steiner=[(0.0, Y1, 3.0), (0.0, Y1, 7.0)])
    fs += back
    vs = [v for r in rings for v in r]
    # the back fan's two Steiner verts belong to the shell too: without them _faces(vs) misses every back triangle
    # (each touches a Steiner vert), so the normals recalc skipped the fan and it stayed wound inward (fix round 1, B1)
    vs += [v for v in {v for f in back for v in f.verts} if v not in set(vs)]
    _shell_done(a, fs, vs, ROCK)
    nf = K.noise_field(scale=0.2, seed=44301)
    for f in _faces(vs):
        c = f.calc_center_median()
        if c.z < 1.5 and nf(c) > -0.05 and abs(f.normal.z) < 0.9:
            f.material_index = a._mi(_mix(ROCK, ROCK_DEEP, 0.15, step=0.05))
        elif nf(c) > 0.2:
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.2))
    _mottle(a, _faces(vs), 0.04, 0.3, 44302)
    return vs


def wedge_part(a):
    wedge(a)


# ---- cliff masses (spec 2.3) -----------------------------------------------------------------------------------------------
COL_Y = [-8.3, -4.9, -1.4, 1.8, 4.9, 7.5, 10.0]
COLS = ("C1", "C2", "C3", "C4", "C5", "C6")
X_IN, X_FLAT, X_RIDGE = 4.0, 6.70, 6.95  # inner face; the draped inner top ends; the roof ridge
# (fix round 1, B4: the ridge moved out 0.3 from 6.65 so the tip strip seen from above, from where a tip leaves the
# turf to the outer face's top edge, stays <= 1.1; the roof facets now fall 0.85 over about 0.8, about 47 deg)
ROOF_DROP = 0.85            # the outer roof facets fall this far from the ridge to the outer face's top edge
INNER_DROP = 0.6            # the draped inner top lies this far under the ridge (the ridge band rises 63 deg)
CREASE_D = 0.45             # creases: the outline steps in this far between two columns (fix round 1, m6: 0.35)
BATTER = 0.015              # the outer face leans in this much per stud of height
HIP_L = 0.45                # the hip facet at each column's downhill end (the peaked tip)
RIDGE_OUT = 0.12            # the outer face's vertical ridge stands this far proud at the column's mid station
X_MAX = 7.97
# per side: outer face x of each column, apex variation, mid-point fraction, hip drop, mid-ring push pattern
SIDES = {
    1: dict(xo=[7.62, 7.80, 7.58, 7.82, 7.66, 7.74], dv=[0.0, 0.06, -0.08, 0.05, -0.05, 0.0],
            mf=[0.52, 0.46, 0.55, 0.48, 0.53, 0.5], push=[(-0.12, 0.06, -0.1), (0.05, -0.12, 0.06),
                                                         (-0.1, 0.05, -0.12), (0.06, -0.1, 0.05),
                                                         (-0.12, 0.05, -0.08), (0.05, -0.1, 0.0)], seed=44401),
    -1: dict(xo=[7.70, 7.60, 7.84, 7.64, 7.78, 7.66], dv=[0.05, -0.06, 0.04, -0.08, 0.06, 0.0],
             mf=[0.47, 0.54, 0.49, 0.53, 0.46, 0.5], push=[(0.06, -0.1, 0.05), (-0.12, 0.05, -0.1),
                                                          (0.05, -0.12, 0.06), (-0.1, 0.06, -0.12),
                                                          (0.06, -0.1, 0.05), (-0.08, 0.05, 0.0)], seed=44451),
}
C6_APEX = (10.30, 10.40)
APEX_UP = 0.25              # each column's apex over the turf at its downhill end (before the hip; spec 0-0.3)
HIPS = [0.7, 0.7, 0.7, 0.7, 0.7, 0.0]   # the hip drop at each downhill end (fix round 1: 0.8 with APEX_UP 0.35)
CLIFF_INFO = {}


def col_apex(side, k):
    """(apex at the downhill end, apex at the uphill end) of column k: B + 0.15 down, B - 0.75 up (spec 2.3)."""
    ya, yb = COL_Y[k], COL_Y[k + 1]
    dv = SIDES[side]["dv"][k]
    if k == 5:
        return C6_APEX[0] + dv, C6_APEX[1] + dv
    return border_z(ya) + APEX_UP + dv, border_z(yb) - 0.75 + dv


def col_stations(side, k):
    ya, yb = COL_Y[k], COL_Y[k + 1]
    mf = SIDES[side]["mf"][k]
    s1 = ya + HIP_L
    s2 = yb - 0.5
    return [ya, s1, s1 + mf * (s2 - s1), s2, yb]


def corner_x(side, c):
    """The foot x of the crease corner at COL_Y[c] (front corner, interior creases, back corner)."""
    xo = SIDES[side]["xo"]
    if c == 0:
        return xo[0] - CREASE_D
    if c == 6:
        return xo[5]
    return 0.5 * (xo[c - 1] + xo[c]) - CREASE_D


def outline_foot(side, k):
    """The column's outer foot outline points A, S1, R, S2, B as (x, y) on the +x side (x mirrored later)."""
    xo = SIDES[side]["xo"]
    st = col_stations(side, k)
    return [(corner_x(side, k), st[0]), (xo[k], st[1]), (min(xo[k] + RIDGE_OUT, X_MAX), st[2]), (xo[k], st[3]),
            (corner_x(side, k + 1), st[4])]


def cliff(a, side):
    """One cliff mass: a single closed explicit solid of six columns (no boolean). Each column: a flat bottom on
    z 0, the inner face on x 4.0 (overlapping the wedge's side), an outer face of two tall facets (a vertical ridge at
    the mid point and a staggered mid ring) leaning in (batter), creases into the outline between columns, and a top
    that is a draped plane (under the turf) inside x 6.6, rising 45 deg to a ridge at x 6.9 and falling in roof
    facets (>= 30 deg) to the outer face; a hip facet drops the tip at each column's downhill end. Each column's top
    stands 0.35-0.9 over the previous one's at the crease (the riser). Tall faces are zipped between their vertex
    columns and planar ends are Delaunay-filled, so no needle triangles. Returns the verts."""
    bm = a.bm
    s = side
    P = SIDES[side]
    rng = random.Random(P["seed"])
    V = lambda x, y, z: bm.verts.new((s * x, y, z))
    foot_in = [V(X_IN, y, 0.0) for y in COL_Y]
    prof = []           # per column: 5 stations x [x_in or None, flat, ridge, outer top]
    for k in range(6):
        aa, ab = col_apex(side, k)
        st = col_stations(side, k)
        ol = outline_foot(side, k)
        ya, yb = st[0], st[-1]
        rows = []
        for j, y in enumerate(st):
            apex = aa + (ab - aa) * (y - ya) / (yb - ya)
            ridge = apex - (HIPS[k] if j == 0 else 0.0)
            outer = ridge - (ROOF_DROP - 0.25 if j == 0 and HIPS[k] else ROOF_DROP)   # the hip's foot
            xt = ol[j][0] - BATTER * outer
            # the draped top's outer edge stays >= 0.35 under the ridge, so the ridge band never lies near flat where
            # the hip drops the ridge (fix round 1: at 6.78 such a band face could rise through the turf near s1)
            flat = min(apex - INNER_DROP, ridge - 0.35)
            rows.append([V(X_IN, y, apex - INNER_DROP) if j in (0, 4) else None, V(X_FLAT, y, flat),
                         V(X_RIDGE, y, ridge), V(xt, y, outer)])
        prof.append(rows)
    # crease corners: foot and a mid point on the batter line under the lower top
    corners = []
    for c in range(7):
        y = COL_Y[c]
        fx = corner_x(side, c)
        zlow = prof[c][0][3].co.z if c == 0 else prof[c - 1][4][3].co.z
        zm = 0.5 * zlow
        corners.append((V(fx, y, 0.0), V(fx - BATTER * zm, y, zm)))
    # S1, R, S2 of each column: foot, a staggered mid point, the top
    chains = []
    for k in range(6):
        ol = outline_foot(side, k)
        ch = []
        for j in (1, 2, 3):
            fx, fy = ol[j]
            zt = prof[k][j][3].co.z
            zm = zt * (0.5 + rng.uniform(-0.08, 0.08))
            xm = min(fx - BATTER * zm + P["push"][k][j - 1], X_MAX)
            ch.append([V(fx, fy, 0.0), V(xm, fy + rng.uniform(-0.05, 0.05), zm), prof[k][j][3]])
        chains.append(ch)
    fs = []
    for k in range(6):
        rows = prof[k]
        # top: the draped inner plane, the ridge band, the outer roof band
        fs += _planar(bm, [rows[0][0], rows[0][1], rows[1][1], rows[2][1], rows[3][1], rows[4][1], rows[4][0]], 2)
        for j in range(4):
            fs.append(bm.faces.new((rows[j][1], rows[j + 1][1], rows[j + 1][2], rows[j][2])))
            fs.append(bm.faces.new((rows[j][2], rows[j + 1][2], rows[j + 1][3], rows[j][3])))
        # outer wall: A-S1, S1-R, R-S2, S2-B, each zipped between its two vertex columns
        cf, cm = corners[k]
        A = [cf, cm] + ([prof[k - 1][4][3]] if k > 0 else []) + [rows[0][3]]
        nf_, nm_ = corners[k + 1]
        B = [nf_, nm_, rows[4][3]]
        seq = [A] + chains[k] + [B]
        for j in range(4):
            fs += _zip(bm, seq[j], seq[j + 1])
        # inner wall (x = 4.0)
        L = [foot_in[k]] + ([prof[k - 1][4][0]] if k > 0 else []) + [rows[0][0]]
        fs += _zip(bm, L, [foot_in[k + 1], rows[4][0]])
        # riser at the crease into the next column (planar, on y = the crease)
        if k < 5:
            lo, hi = prof[k][4], prof[k + 1][0]
            fs += _planar(bm, [lo[0], lo[1], lo[2], lo[3], hi[3], hi[2], hi[1], hi[0]], 1)
    # front end (C1) and back end (C6, on the back plane)
    r0 = prof[0][0]
    fs += _planar(bm, [foot_in[0], corners[0][0], corners[0][1], r0[3], r0[2], r0[1], r0[0]], 1)
    r5 = prof[5][4]
    fs += _planar(bm, [foot_in[6], corners[6][0], corners[6][1], r5[3], r5[2], r5[1], r5[0]], 1)
    # bottom (z 0): zipped between the inner feet and the outer feet, along y
    outer = []
    for k in range(6):
        outer.append(corners[k][0])
        outer += [ch[0] for ch in chains[k]]
    outer.append(corners[6][0])
    fs += _zip(bm, foot_in, outer, key=lambda v: v.co.y)
    _tri(bm, [f for f in fs if f.is_valid and len(f.verts) > 3])
    vs = list(foot_in) + [v for c in corners for v in c] + [v for ch in chains for t in ch for v in t[:2]]
    vs += [v for rows in prof for row in rows for v in row if v is not None]
    fs = _faces(vs)
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    for f in fs:
        f.smooth = False
        for lp in f.loops:
            lp[a.tint_layer] = (1.0, 1.0, 1.0, 1.0)
    CLIFF_INFO[side] = {"apex": [[round(x, 2) for x in col_apex(side, k)] for k in range(6)],
                        "outer_x": SIDES[side]["xo"], "tris": sum(len(f.verts) - 2 for f in fs)}
    return vs


def _col_of(y):
    return max(0, min(5, next((k for k in range(6) if y < COL_Y[k + 1]), 5)))


COL_TINT = {1: [1.02, 0.97, 1.03, 0.98, 1.01, 0.99], -1: [0.98, 1.03, 0.97, 1.02, 0.99, 1.01]}
LIGHT_FROM = 0.6            # rock_light rises from 0.6 of a column's apex to 40 % at the top (spec 5.5)
DEEP_Z = 1.5


def _paint_cliff(a, vs, side):
    """Stone colour by position only: lighter in the upper part of each column (rising to 40 %), the roof and hip
    facets of the tips lightest (50 %), broad deeper patches below 1.5; the hidden draped tops, inner face and bottom
    plain stone. Per-column tint."""
    nf = K.noise_field(scale=0.2, seed=44411 + side)
    groups = {k: [] for k in range(6)}
    for f in _faces(vs):
        c = f.calc_center_median()
        k = _col_of(c.y)
        groups[k].append(f)
        ax = abs(c.x)
        apex = max(col_apex(side, k))
        hidden = (ax < X_FLAT + 0.01 and f.normal.z > 0.5) or ax < X_IN + 0.01 or max(v.co.z for v in f.verts) < 1e-4
        if hidden:
            f.material_index = a._mi(ROCK)
            continue
        if ax > X_RIDGE - 0.31 and f.normal.z > 0.3 and c.z > apex - ROOF_DROP - 0.4:
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.5))            # tips: ridge band, roof, hip
            continue
        if c.z < DEEP_Z and nf(c) > -0.05:
            f.material_index = a._mi(_mix(ROCK, ROCK_DEEP, 0.15, step=0.05))
            continue
        t = 0.4 * _clamp((c.z - LIGHT_FROM * apex) / ((1 - LIGHT_FROM) * apex)) + 0.08 * nf(c)
        f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, t) if t >= 0.05 else ROCK)
    for k, fs in groups.items():
        _mottle(a, fs, 0.04, 0.3, 44421 + k + (10 if side < 0 else 0), tint=COL_TINT[side][k])


TOE_ROCK = {1: dict(base=[(6.35, -9.7), (7.2, -9.98), (7.95, -9.5), (7.92, -8.42), (6.6, -8.37)],
                    apex=(7.3, -8.95, 1.75), seed=44471),
            -1: dict(base=[(6.4, -9.55), (7.1, -9.96), (7.95, -9.3), (7.85, -8.4), (6.5, -8.38)],
                     apex=(7.35, -8.9, 1.6), seed=44472)}


def toe_rock(a, side):
    """The pointed toe rock in front of C1 (spec 2.3, f34 stump): a hull of a 5-point foot, a bulged mid ring and an
    apex. Stands on the ground clear of C1 (y <= -8.36)."""
    t = TOE_ROCK[side]
    rng = random.Random(t["seed"])
    base = [Vector((side * x, y, 0.0)) for x, y in t["base"]]
    apex = Vector((side * t["apex"][0], t["apex"][1], t["apex"][2]))
    cen = sum(base, Vector()) / len(base)
    pts = list(base) + [apex]
    for p in base:
        f_ = rng.uniform(0.4, 0.52)
        q = p.lerp(apex, f_)
        d = q - cen.lerp(apex, f_)
        d.z = 0
        q += d * rng.uniform(0.15, 0.25)
        q.y = min(q.y, -8.37)
        q.x = max(min(q.x, X_MAX), -X_MAX)
        pts.append(q)
    vs = _hull_piece(a, pts, ROCK)
    for f in _faces(vs):
        c = f.calc_center_median()
        f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.4) if c.z > 0.9 else ROCK if c.z > 0.45
                                 else _mix(ROCK, ROCK_DEEP, 0.15, step=0.05))
    _mottle(a, _faces(vs), 0.04, 0.4, t["seed"], tint=rng.uniform(0.97, 1.03))
    return vs


def cliff_part(a, side):
    vs = cliff(a, side)
    _paint_cliff(a, vs, side)
    toe_rock(a, side)


# ---- borders: the draped turf (spec 2.4) -------------------------------------------------------------------------------------
TURF_IN = 3.70              # the inner edge (lobed +-0.15): overlaps the edge tiles by 0.3
TURF_EDGE = (6.82, 6.95)    # the outer edge: at the column tips, and where the rock is low (draped tops end at 6.7)
TURF_CROWN = 0.04


def turf_stations():
    ys = [Y0, -9.35, -8.75]
    for k in range(6):
        ya, yb = COL_Y[k], COL_Y[k + 1]
        L = yb - ya
        ys += [ya + 0.12, ya + 0.55, ya + 0.55 + 0.5 * (L - 0.95)] if k < 5 else [ya + 0.12, ya + 0.9, ya + 1.7]
    ys.append(Y1)
    return ys


def turf_edges(side, y):
    """(inner x, outer x) of the turf at y (positive side; mirrored by the caller)."""
    xi = TURF_IN + 0.15 * math.sin(1.9 * y + (0.7 if side > 0 else 2.3))
    if y < COL_Y[0]:
        xo = 6.85 + 0.08 * math.sin(3.0 * y)
    else:
        k = _col_of(y)
        ya, yb = COL_Y[k], COL_Y[k + 1]
        t = _clamp((y - ya - 0.3) / max(0.5, (yb - ya) - 0.9))
        xo = TURF_EDGE[0] + (TURF_EDGE[1] - TURF_EDGE[0]) * (t * t * (3 - 2 * t))
    return xi, xo


def turf_top(x, y, side=None):
    """The turf's top at (x, y): B(y) at both edges, a 0.04 crown along its middle line."""
    s = 1 if (side or (1 if x >= 0 else -1)) > 0 else -1
    xi, xo = turf_edges(s, y)
    ax = abs(x)
    xm = 0.5 * (xi + xo)
    t = _clamp(1.0 - abs(ax - xm) / max(0.1, 0.5 * (xo - xi)))
    return border_z(y) + TURF_CROWN * t


def turf_bottom(side, y):
    """A line under every support: z 0 on the toe ground, then through the lows at each crease (the lower
    column's draped top - 0.03), so it is under the column tops and the edge tiles everywhere (buried there)."""
    knots = [(Y0, 0.003), (-8.5, 0.003)]
    for k in range(1, 6):
        yc = COL_Y[k]
        inner_prev = col_apex(side, k - 1)[1] - INNER_DROP
        knots.append((yc, min(inner_prev, path_z(yc) - 0.14) - 0.03))
    knots.append((Y1, col_apex(side, 5)[1] - INNER_DROP - 0.03))
    for (y0, z0), (y1, z1) in zip(knots, knots[1:]):
        if y <= y1:
            return z0 + (z1 - z0) * (y - y0) / (y1 - y0)
    return knots[-1][1]


def turf(a, side):
    """One closed sloped slab per side: top (inner edge, crown line, outer edge) at B(y), lime side walls down to a
    bottom line buried in the column tops and the edge tiles; a rounded tongue on the toe ground; a planar end on the
    back plane. Returns (verts, top faces, wall faces)."""
    bm = a.bm
    s = side
    ys = turf_stations()
    rows = []
    for i, y in enumerate(ys):
        xi, xo = turf_edges(side, y)
        xm = 0.5 * (xi + xo) + 0.12 * math.sin(2.7 * y + side)
        zt = border_z(y)
        zb = turf_bottom(side, y)
        ym = y - (0.22 if i == 0 else 0.0)                 # the rounded tongue at the toe
        ye = y + (0.12 if i == 0 else 0.0)
        rows.append([bm.verts.new((s * xi, ye, zt)), bm.verts.new((s * xm, ym, zt + TURF_CROWN)),
                     bm.verts.new((s * xo, ye, zt)), bm.verts.new((s * xo, ye, zb)), bm.verts.new((s * xi, ye, zb))])
    tops, walls, other = [], [], []
    for i in range(len(rows) - 1):
        A, B = rows[i], rows[i + 1]
        tops.append(bm.faces.new((A[0], B[0], B[1], A[1])))
        tops.append(bm.faces.new((A[1], B[1], B[2], A[2])))
        walls.append(bm.faces.new((A[2], B[2], B[3], A[3])))                  # outer wall
        other.append(bm.faces.new((A[3], B[3], B[4], A[4])))                  # bottom
        walls.append(bm.faces.new((A[4], B[4], B[0], A[0])))                  # inner wall
    for r_ in (rows[0], rows[-1]):           # the toe tongue's front, the back plane end: fanned from the bottom
        it, mt, ot, ob, ib = r_
        walls += [bm.faces.new((ib, it, mt)), bm.faces.new((ib, mt, ob)), bm.faces.new((ob, mt, ot))]
    vs = [v for r in rows for v in r]
    fs = tops + walls + other
    _tri(bm, fs)
    fs = _faces(vs)
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    for f in fs:
        f.smooth = False
        for lp in f.loops:
            lp[a.tint_layer] = (1.0, 1.0, 1.0, 1.0)
    return vs


ROOTS = {1: [], -1: []}     # (x, y, r) bush roots and boulders per side: the lawn deepens round them


def _paint_turf(a, vs, side):
    """Lime top and sides: broad lighter patches by a noise field (10-20 %), deeper within 0.8 of bush roots and
    boulders (25 %). Values are averaged over each face's corners, so neighbouring faces step smoothly."""
    nf = K.noise_field(scale=0.25, seed=44501 + side)
    tops = []
    for f in _faces(vs):
        c = f.calc_center_median()
        if f.normal.z < -0.3:
            f.material_index = a._mi(GRASS)                        # hidden bottom
            continue
        if f.normal.z > 0.5:
            near = min([math.hypot(c.x - x, c.y - y) - r for x, y, r in ROOTS[side]] or [9.0])
            n_ = sum(nf(v.co) for v in f.verts) / len(f.verts)
            if near < 0.8:
                key = _mix(GRASS, GRASS_DEEP, 0.25 if near < 0.3 else 0.15, step=0.05)
            elif n_ > 0.1:
                key = _mix(GRASS, GRASS_LIGHT, 0.2 if n_ > 0.25 else 0.1)
            else:
                key = GRASS
            f.material_index = a._mi(key)
            tops.append(f)
        else:
            f.material_index = a._mi(GRASS)                        # the lime sides
    _mottle(a, _faces(vs), 0.04, 0.4, 44511 + side)


# ---- plants ---------------------------------------------------------------------------------------------------------------
def _dleaf(a, mid, xdir, ndir, L, W, key, cup=0.16, curl=0.12, cam=0.12):
    """A broad round-tipped leaf laid on the bush's dome (10 tris, closed; fix round 1, B2): a six-point outline -
    the stem, two shoulders (widest, at 0.38 L) and a three-point rounded tip (0.85 L at +-0.3 W and the tip at L;
    corners 122-140 deg, no point) - its middle at `mid`, its length along xdir, its face turned to ndir (outward).
    The sides cup out, the tip curls in toward the heart, a raised midrib point on top, a flat-ish underside."""
    bm = a.bm
    x = Vector(xdir).normalized()
    z = Vector(ndir) - x * Vector(ndir).dot(x)
    z = z.normalized() if z.length > 1e-6 else x.orthogonal().normalized()
    y = z.cross(x)
    B = Vector(mid) - x * 0.48 * L

    def P(lx, ly, lz):
        t = lx / L
        return bm.verts.new(B + x * lx + y * ly + z * (lz + cup * abs(ly) - curl * L * t * t))
    o = [P(0, 0, 0), P(0.38 * L, -W / 2, 0), P(0.85 * L, -0.3 * W, 0), P(L, 0, 0), P(0.85 * L, 0.3 * W, 0),
         P(0.38 * L, W / 2, 0)]
    up = P(0.5 * L, 0, cam * L)
    fs = [bm.faces.new((o[i], o[(i + 1) % 6], up)) for i in range(6)]
    bot = bm.faces.new(list(reversed(o)))
    _tri(bm, [bot])
    vs = o + [up]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, key, tint=1.0)
    return vs


def _prism(a, centre, z0, z1, r0, r1, key, seed, n=3):
    rng = random.Random(seed)
    bm = a.bm
    off = rng.uniform(0, 2 * math.pi)
    angs = [off + 2 * math.pi * k / n for k in range(n)]
    lo = [bm.verts.new((centre[0] + math.cos(t) * r0, centre[1] + math.sin(t) * r0, z0)) for t in angs]
    hi = [bm.verts.new((centre[0] + math.cos(t) * r1, centre[1] + math.sin(t) * r1, z1)) for t in angs]
    fs = [bm.faces.new((lo[k], lo[(k + 1) % n], hi[(k + 1) % n], hi[k])) for k in range(n)]
    fs += [bm.faces.new(list(reversed(lo))), bm.faces.new(hi)]
    vs = lo + hi
    _shell_done(a, fs, vs, key)
    return vs


PLANT_INFO = {}
# the dark bush's dome tiers, crown first (fix round 1, B2; the m043 dome approach that passed as "rounded leafy
# domes, not palm stars"): (polar angle from the dome's top in deg, count, azimuth phase in turns, length / R,
# width / length, outward flare of the leaf's axis: 0 = straight down the dome's meridian, 1 = half out, role)
DOME_TIERS = ((22, 3, 0.0, 0.95, 0.92, 0.0, "lit"),
              (62, 3, 0.5, 1.0, 0.92, 0.3, "mid"),
              (92, 3, 0.0, 0.98, 0.9, 0.75, "deep"))
SKIRT_MIN_TILT = 25.0       # every skirt leaf's axis lies at least this far out of horizontal (no flat star point)


def _rock_depth(tree, vs):
    """How far a leaf's deepest vert lies inside the rock (0 when it is clear)."""
    worst = 0.0
    for v in vs:
        loc, nrm, _i, d = tree.find_nearest(v.co)
        if loc is not None and nrm is not None and (v.co - loc).dot(nrm) < 0:
            worst = max(worst, d)
    return worst


def _tilt(vs):
    """A leaf's axis (stem -> tip) angle out of horizontal, in degrees."""
    d = vs[3].co - vs[0].co
    return math.degrees(math.asin(_clamp(abs(d.z) / max(1e-6, d.length))))


def dome_bush(a, name, c, ground, R, H, seed, guard=None, z0=None):
    """A puffy round two-tone bush (decision 11; fix round 1, B2): a hidden faceted heart dome on a short brown
    trunk, clad in nine broad round-tipped leaves laid on the dome - a crown tier of three fresh-green leaves over
    the top, a middle tier of three, and a skirt of three deep-emerald leaves drooping down the dome's sides (tilted
    >= 25 deg, tips curled in toward the heart), so the outline is a dome about 2 R across and H tall, never a star.
    On the sloped turf a skirt leaf that would cut into the ground climbs the dome (smaller polar angle) until it
    clears. Every leaf touches the heart (no floating leaf). Returns all verts."""
    rng = random.Random(seed)
    if z0 is None:
        # sit the dome on the low side of the sloped turf (the lowest ground 0.4 R round the root), so the downhill
        # side reads as foliage down to the lawn, not a canopy on a bare trunk; the uphill leaves climb clear
        z0 = min(ground(c[0] + dx * 0.4 * R, c[1] + dy * 0.4 * R) for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1),
                                                                              (0, -1))) - 0.03
    out = []
    tint = 1.0 + rng.uniform(-0.04, 0.04)
    keys = {"lit": _mix(LEAF, LEAF_LIT, 0.7), "mid": LEAF, "deep": LEAF_DEEP}
    C = Vector((c[0], c[1], z0 + 0.38 * H))
    rx, rz = 0.60 * R, 0.52 * H
    out += _prism(a, c, z0 - 0.08, C.z, 0.13 * R, 0.09 * R, TRUNK, seed + 2)
    hvs = m040._dome_heart(a, C, rx, rz, C.z - 0.25 * H, keys["deep"], seed + 1, n=3)    # 12 tris, hidden
    out += hvs
    heart = _tree_of(hvs)
    off = rng.uniform(0, 2 * math.pi)
    tilts = []
    dropped = 0

    def place(t_deg, phi, lf, wf, flare, key):
        t = math.radians(t_deg)
        u = Vector((math.cos(phi), math.sin(phi), 0.0))
        P = C + u * (rx * 1.02 * math.sin(t)) + Vector((0, 0, rz * math.cos(t) * (1.0 if t < math.pi / 2 else 0.8)))
        nrm = (u * (math.sin(t) / rx) + Vector((0, 0, math.cos(t) / rz))).normalized()
        down = (u * (rx * math.cos(t)) - Vector((0, 0, rz * math.sin(t)))).normalized()
        xdir = (down + u * flare).normalized()
        L = R * lf
        return _dleaf(a, P + xdir * 0.12 * L, xdir, nrm, L, L * wf, key, curl=0.12 if flare < 0.5 else 0.16)

    for ti, (th, cnt, ph, lf, wf, flare, role) in enumerate(DOME_TIERS):
        for k in range(cnt):
            phi = off + 2 * math.pi * (k + ph) / cnt + rng.uniform(-0.18, 0.18)
            t_deg = th + rng.uniform(-5, 5)
            lfk = lf * rng.uniform(0.94, 1.05)
            key = keys["deep" if role == "mid" and k == 0 else role]
            if role == "deep":
                # on the sloped turf a downhill skirt leaf would hang in the air (a parasol on a bare trunk): walk it
                # down the dome (larger polar angle) while its lowest point stays over 0.15 above the turf
                while t_deg < th + 24:
                    vs = place(t_deg, phi, lfk, wf, flare, key)
                    _touch(vs, heart)
                    gap = min(v.co.z - ground(v.co.x, v.co.y) for v in vs)
                    for v in vs:
                        a.bm.verts.remove(v)
                    if gap <= 0.15:
                        break
                    t_deg += 6.0
            while True:
                # one mid leaf in three is emerald too (the sheet's emerald is about 0.44 of the foliage)
                vs = place(t_deg, phi, lfk, wf, flare, key)
                _touch(vs, heart)
                dip = min(v.co.z - ground(v.co.x, v.co.y) for v in vs)
                deep = _rock_depth(guard.tree, vs) if guard and guard.tree else 0.0
                if (dip > -0.04 and deep <= 0.05) or t_deg < th - 30:
                    break
                # it cuts into the sloped turf or the rock (cliff tips, boulders): climb the dome and try again,
                # so the leaf keeps its contact with the heart (a guard push could leave it touching only the
                # rock, which floats in the border part)
                for v in vs:
                    a.bm.verts.remove(v)
                t_deg -= 6.0
            if deep > 0.05:
                # still in the rock after climbing 30 deg: the boulder or tip hides that side of the bush; drop it
                for v in vs:
                    a.bm.verts.remove(v)
                dropped += 1
                continue
            if role == "deep":
                tilts.append(round(_tilt(vs), 1))
            out += vs
    _mottle(a, _faces(out[6:]), 0.04, 0.9, seed, tint=tint)
    xs, ys, zs = ([v.co[i] for v in out] for i in range(3))
    PLANT_INFO[name] = {"centre": [round(c[0], 2), round(c[1], 2)], "z0": round(z0, 2),
                        "size": [round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2), round(max(zs) - z0, 2)],
                        "skirt_tilt": tilts, "leaves": sum(t[1] for t in DOME_TIERS) - dropped}
    return out


def flower(a, c, ground, r, seed, white=False):
    """A yellow five-petal flower lying on the turf (a pentagon disc following the surface, 10 tris, with a darker
    centre knob, 4 tris) or a small cream flower (a square disc, 8 tris)."""
    rng = random.Random(seed)
    bm = a.bm
    n = 4 if white else 5
    off = rng.uniform(0, 2 * math.pi)
    ring = []
    for k in range(n):
        t = off + 2 * math.pi * k / n
        x, y = c[0] + math.cos(t) * r, c[1] + math.sin(t) * r
        ring.append(bm.verts.new((x, y, ground(x, y) + 0.03)))
    g0 = ground(c[0], c[1])
    up = bm.verts.new((c[0], c[1], g0 + 0.07))
    dn = bm.verts.new((c[0], c[1], g0 - 0.03))
    fs = []
    for k in range(n):
        j = (k + 1) % n
        fs.append(bm.faces.new((ring[k], ring[j], up)))
        fs.append(bm.faces.new((ring[j], ring[k], dn)))
    vs = ring + [up, dn]
    _shell_done(a, fs, vs, FLOWER_WHITE if white else FLOWER)
    _mottle(a, _faces(vs), 0.02, 1.0, seed, tint=rng.uniform(0.97, 1.03))
    if white:
        return vs
    hr = r * 0.32
    hv = [bm.verts.new((c[0] + math.cos(off + 2 * math.pi * k / 3) * hr, c[1] + math.sin(off + 2 * math.pi * k / 3) * hr,
                        g0 + 0.05)) for k in range(3)]
    ht = bm.verts.new((c[0], c[1], g0 + 0.14))
    hf = [bm.faces.new((hv[0], hv[1], hv[2]))] + [bm.faces.new((hv[k], hv[(k + 1) % 3], ht)) for k in range(3)]
    _shell_done(a, hf, hv + [ht], FLOWER_HEART)
    return vs + hv + [ht]


def sprig(a, name, c, ground, R, n, seed, guard=None):
    """3-5 lime leaves from one root (m040 sprig on a surface): steep pointed blades fanning out, roots sunk 0.05."""
    rng = random.Random(seed)
    out = []
    y0 = rng.uniform(0, 2 * math.pi)
    z0 = ground(c[0], c[1]) - 0.05
    for k in range(n):
        yaw = y0 + 2 * math.pi * k / n + rng.uniform(-0.25, 0.25)
        L = R * rng.uniform(0.85, 1.1)
        kk = LEAF_LIME if k % 3 else _mix(LEAF_LIME, LEAF, 0.3)
        base = (c[0] + math.cos(yaw) * 0.04, c[1] + math.sin(yaw) * 0.04, z0)
        vs = m040._leaf(a, base, L, L * 0.7, kk, yaw, rng.uniform(0.7, 1.05), curl=0.2, roll=rng.uniform(-0.3, 0.3))
        if guard:
            guard.push(vs)
        out += vs
    _mottle(a, _faces(out), 0.04, 0.9, seed, tint=1.0 + rng.uniform(-0.04, 0.04))
    PLANT_INFO[name] = {"centre": [round(c[0], 2), round(c[1], 2)], "leaves": n}
    return out


BOULDER_INFO = {}


def boulder(a, name, c, w, d, h, yaw, ground, seed, sink=0.1, n=5):
    """A pale rounded-angular boulder (spec 2.4): the hull of a foot ring that follows the surface (sunk `sink`), a
    shoulder ring at 0.7 h and an inset flat-ish crown at h: broad facets, a flat-ish crown >= 25 % of its plan,
    never an egg. Crown lighter by height."""
    rng = random.Random(seed)
    yr = math.radians(yaw)
    ph = rng.uniform(0, 2 * math.pi / n)

    def ring(sc, jit):
        out = []
        for k in range(n):
            ang = ph + 2 * math.pi * k / n + rng.uniform(-0.12, 0.12)
            cx_, cy_ = math.cos(ang), math.sin(ang)
            lx = math.copysign(abs(cx_) ** 0.75, cx_) * w / 2 * sc * (1 + rng.uniform(-jit, jit))
            ly = math.copysign(abs(cy_) ** 0.75, cy_) * d / 2 * sc * (1 + rng.uniform(-jit, jit))
            x = c[0] + lx * math.cos(yr) - ly * math.sin(yr)
            y = min(c[1] + lx * math.sin(yr) + ly * math.cos(yr), Y1 - 0.02)
            out.append((x, y))
        return out
    foot = [Vector((x, y, ground(x, y) - sink)) for x, y in ring(1.0, 0.06)]
    zb = ground(c[0], c[1])
    pts = list(foot)
    for x, y in ring(0.97, 0.05):
        pts.append(Vector((x, y, ground(x, y) + 0.6 * h + rng.uniform(-0.06, 0.06))))
    for x, y in ring(0.7, 0.05):
        pts.append(Vector((x, y, 0.5 * (zb + ground(x, y)) + h + rng.uniform(-0.05, 0.05))))
    vs = _hull_piece(a, pts, ROCK)
    for f in _faces(vs):
        cz = f.calc_center_median().z
        f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.4) if cz > zb + 0.75 * h else
                                 ROCK if cz > zb + 0.25 * h else _mix(ROCK, ROCK_DEEP, 0.15, step=0.05))
    _mottle(a, _faces(vs), 0.04, 0.6, seed, tint=rng.uniform(0.97, 1.04))
    BOULDER_INFO[name] = {"centre": [round(c[0], 2), round(c[1], 2)], "tris": sum(len(f.verts) - 2 for f in _faces(vs))}
    return vs


# dressing per side (x on the +x side; mirrored by side). Bushes: name -> (x, y, R, H, seed)
BUSHES = {1: {"R1": (5.3, -8.45, 1.38, 2.04, 44601), "R2": (5.5, -5.2, 1.41, 2.06, 44602),
              "R3": (5.3, -1.9, 1.39, 2.04, 44603), "R4": (5.5, 1.5, 1.43, 2.08, 44604),
              "R5": (5.3, 4.8, 1.39, 2.04, 44605), "R6": (5.45, 8.05, 1.41, 2.06, 44606)},
          -1: {"L1": (5.4, -7.4, 1.41, 2.06, 44611), "L2": (5.3, -4.6, 1.38, 2.04, 44612),
               "L3": (5.5, -1.3, 1.43, 2.08, 44613), "L4": (5.3, 2.1, 1.39, 2.04, 44614),
               "L5": (5.5, 5.4, 1.41, 2.06, 44615), "L6": (5.3, 8.15, 1.38, 2.04, 44616)}}
# boulders: name -> (x, y, w, d, h, yaw, seed): low rounded-angular lumps on the turf
BOULDERS = {1: {"BR_mid": (5.75, -3.45, 1.7, 1.45, 1.0, 20.0, 44621),
                "BR_top": (5.7, 9.2, 1.8, 1.45, 1.05, -15.0, 44622)},
            -1: {"BL_toe": (5.6, -9.3, 1.9, 1.6, 1.05, 10.0, 44631),
                 "BL_mid": (5.75, 0.45, 1.7, 1.45, 1.0, -25.0, 44632),
                 "BL_top": (5.75, 9.15, 1.8, 1.45, 1.05, 30.0, 44633)}}
# yellow flowers (x, y) in groups at bush feet, white flowers
YELLOW = {1: [(4.5, -7.2), (4.75, -6.75), (6.1, -3.95), (4.45, 0.05), (4.7, 0.5), (6.1, 3.3), (4.5, 6.45),
              (6.25, -6.6), (6.3, 6.55)],
          -1: [(4.55, -8.9), (6.1, -5.95), (6.0, -5.4), (4.45, -2.7), (4.5, 3.6), (4.75, 4.05), (6.1, 6.95),
               (4.5, -6.3), (6.25, 3.75)]}
YELLOW_PART = 3             # the border parts carry the first 3 a side, the rest are hero-only (fix round 1: budget)
WHITE = {1: [(4.35, -3.55), (6.1, -0.95), (4.4, 3.2), (6.1, 6.4), (4.45, 9.35)],
         -1: [(4.4, -6.1), (6.1, -2.2), (4.35, 0.9), (6.1, 3.0), (4.45, 6.75)]}
SPRIGS = {1: [(4.3, -9.5), (6.05, -0.4)], -1: [(4.3, -8.4), (6.05, 1.65)]}
HERO_ONLY = {"sprigs", "white", "yellow3+"}   # the border parts stay under 1000 tris (spec 4.3): sprigs, white
#                                                flowers and all but three yellow flowers a side are hero-only


def _guard_tree(side):
    """A BVH of the rock the side's plants must not cut into (the cliff mass, the toe rock and the side's boulders,
    built into a probe)."""
    pa = K.fk().Asset(PFX + "guard", "probe", seed=1, tint_var=0.0)
    cliff(pa, side)
    toe_rock(pa, side)
    g = _border_ground(side)
    for nm, (x, y, w, d, h, yaw, seed) in BOULDERS[side].items():
        boulder(pa, nm, (side * x, y), w, d, h, side * yaw, g, seed, sink=0.1)
    bm = pa.bm
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    return tree


def _border_ground(side):
    """The surface plants of a side stand on: the turf top over the turf, the tiles inside it."""
    def ground(x, y):
        xi, xo = turf_edges(side, y)
        if xi - 0.02 <= abs(x) <= xo + 0.02:
            return turf_top(x, y, side)
        if abs(x) < xi:
            return tile_top(x, y)
        return turf_top(math.copysign(xo, x), y, side)       # plants stay on the turf
    return ground


def border(a, side, hero=False, guard=None):
    """Turf, bushes, boulders, flowers (and on the hero, sprigs) of one side."""
    s = side
    vs = turf(a, side)
    ROOTS[side] = ([(s * x, y, R * 0.6) for x, y, R, H, sd in BUSHES[side].values()] +
                   [(s * b[0], b[1], 0.75) for b in BOULDERS[side].values()])
    _paint_turf(a, vs, side)

    ground = _border_ground(side)
    for nm, (x, y, w, d, h, yaw, seed) in BOULDERS[side].items():
        boulder(a, nm, (s * x, y), w, d, h, s * yaw, ground, seed, sink=0.1)
    for nm, (x, y, R, H, seed) in BUSHES[side].items():
        dome_bush(a, nm, (s * x, y), ground, R, H, seed, guard=guard)
    for i, (x, y) in enumerate(YELLOW[side]):
        if i >= YELLOW_PART and not hero:
            continue
        flower(a, (s * x, y), ground, 0.32 + 0.03 * (i % 3), 44700 + i + (20 if s < 0 else 0))
    for i, (x, y) in enumerate(WHITE[side]):
        if not hero:
            continue                      # white flowers are hero-only (fix round 1: border part budget)
        flower(a, (s * x, y), ground, 0.17, 44740 + i + (20 if s < 0 else 0), white=True)
    if hero:
        for i, (x, y) in enumerate(SPRIGS[side]):
            sprig(a, f"S{'R' if s > 0 else 'L'}{i}", (s * x, y), ground, 0.45, 3, 44780 + i + (10 if s < 0 else 0),
                  guard=guard)
    return vs


def border_part(a, side):
    PLANT_INFO.clear()
    border(a, side, hero=False, guard=m040._Guard(_guard_tree(side)))


# ---- aprons (hero only) --------------------------------------------------------------------------------------------------------
APRON_IN = 7.32             # inner edge, tucked under the cliff foot
APRON_Y = (-9.2, 9.75)
APRON_TOP = 0.26            # the apron's inner edge height (inside the rock); its outer edge is a lime lip at 0.02


def apron(a, side, seed):
    """A thin lime strip along the cliff foot (spec 2.4): a wedge section (0.26 at the rock, 0.02 at the jagged
    outer edge, 0.6 past the side plane at most), one closed shell, flat bottom 0.005 over the ground."""
    rng = random.Random(seed)
    bm = a.bm
    s = side
    n = 11                  # stations (fix round 1: 13, trimmed for the budget)
    ys = [APRON_Y[0] + (APRON_Y[1] - APRON_Y[0]) * i / (n - 1) for i in range(n)]
    rows = []
    for i, y in enumerate(ys):
        xo = 8.12 + (0.38 if i % 2 else 0.12) + rng.uniform(-0.06, 0.06)
        if i in (0, n - 1):
            xo = 7.9
        rows.append([bm.verts.new((s * APRON_IN, y, APRON_TOP)),
                     bm.verts.new((s * xo, y + (rng.uniform(-0.2, 0.2) if 0 < i < n - 1 else 0.0), 0.03)),
                     bm.verts.new((s * APRON_IN, y, 0.005))])
    fs = []
    for i in range(n - 1):
        A, B = rows[i], rows[i + 1]
        fs.append(bm.faces.new((A[0], B[0], B[1], A[1])))           # top
        fs.append(bm.faces.new((A[1], B[1], B[2], A[2])))           # bottom (outer edge to the inner foot)
        fs.append(bm.faces.new((A[2], B[2], B[0], A[0])))           # inner wall (inside the rock)
    fs.append(bm.faces.new(rows[0]))
    fs.append(bm.faces.new(list(reversed(rows[-1]))))
    vs = [v for r in rows for v in r]
    _shell_done(a, fs, vs, GRASS)
    for f in _faces(vs):
        c = f.calc_center_median()
        if f.normal.z > 0.3 and abs(c.x) < 7.75:
            f.material_index = a._mi(_mix(GRASS, GRASS_DEEP, 0.3))
    _mottle(a, _faces(vs), 0.04, 0.5, seed)
    return vs


APRON_YELLOW = {1: [(8.05, -6.6), (8.0, -2.4), (8.0, 0.9), (8.1, 6.1)],
                -1: [(8.05, -4.4), (8.0, -0.6), (8.0, 2.6), (8.1, 7.6)]}
APRON_SPRIGS = {1: [(8.1, -7.9), (8.15, 4.6)],          # fix round 1: 2 a side (budget for the domes and flowers)
                -1: [(8.05, -6.5), (8.0, 6.2)]}


def apron_ground(x, y):
    t = _clamp((abs(x) - APRON_IN) / (8.4 - APRON_IN))
    return APRON_TOP + (0.03 - APRON_TOP) * t


# ---- hero ----------------------------------------------------------------------------------------------------------------------
def hero(a):
    PLANT_INFO.clear()
    BOULDER_INFO.clear()
    wedge(a)
    path_part(a)
    for side in (1, -1):
        vs = cliff(a, side)
        _paint_cliff(a, vs, side)
        toe_rock(a, side)
    for side in (1, -1):
        tree = _guard_tree(side)
        g = m040._Guard(tree)
        border(a, side, hero=True, guard=g)
        apron(a, side, 44801 + (1 if side > 0 else 2))
        for i, (x, y) in enumerate(APRON_YELLOW[side]):
            flower(a, (side * x, y), apron_ground, 0.33, 44820 + i + (10 if side < 0 else 0))
        for i, (x, y) in enumerate(APRON_SPRIGS[side]):
            sprig(a, f"SA{'R' if side > 0 else 'L'}{i}", (side * x, y), apron_ground, 0.42, 3,
                  44840 + i + (10 if side < 0 else 0), guard=g)


# ---- make / finish -------------------------------------------------------------------------------------------------------------
NOTES = {
    HERO: "Natural ramp (16 x 20, path from z 0.35 at the toe to 10.4 at 29.9 deg, then a 2.5-stud landing): warm "
          "sand flagstone path (2 x 7 tiles) on a stone wedge between two raised lime grass borders with round "
          "two-tone bushes, pale boulders and yellow / white flowers, each border on a mass of pale warm columnar "
          "rock with peaked tips stepping up the slope; lime aprons along the cliff feet. Walkable (no step over "
          "0.35). Seam contract: sides x = +-8, flat back plane y = +10 (meets M040's lip front), landing 10.4. "
          "Every piece its own closed shell. No VFX",
    PATH_P: "Top Landing Pad (Path) (reusable): 14 warm sand flagstone slabs (2 across, 6 sloped rows and a flat "
            "landing row) with darker tile sides and pale pebbles",
    WEDGE_P: "Ramp Wedge (Stone) (reusable): long pale stone wedge, flat base, broad faceted long faces, sloped top "
             "under the path",
    CLIFF_L: "Left Cliff Rock Mass (reusable): six tall flat-faced pale warm rock columns stepping up the slope with "
             "peaked tips and dark creases, and a pointed toe rock",
    CLIFF_R: "Right Cliff Rock Mass (reusable): six tall flat-faced pale warm rock columns stepping up the slope "
             "with peaked tips and dark creases, and a pointed toe rock",
    BORDER_L: "Grass Border (Left) (reusable): sloped lime turf strip with lime sides, six round two-tone bushes, "
              "pale boulders, yellow and white flowers",
    BORDER_R: "Grass Border (Right) (reusable): sloped lime turf strip with lime sides, six round two-tone bushes, "
              "pale boulders, yellow and white flowers",
}
COLLISION = {HERO: "precise", PATH_P: "precise", WEDGE_P: "hull", CLIFF_L: "hull", CLIFF_R: "hull",
             BORDER_L: "none", BORDER_R: "none"}
FNS = {PATH_P: path_part, WEDGE_P: wedge_part, CLIFF_L: lambda a: cliff_part(a, -1),
       CLIFF_R: lambda a: cliff_part(a, 1), BORDER_L: lambda a: border_part(a, -1),
       BORDER_R: lambda a: border_part(a, 1)}


def _recentre(o):
    bc = m012._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


def _thin(o):
    """m012._thin, leaving out the tiles' bevel ring: each ring side is a planar 0.1-wide strip up to 4 long, so its two
    coplanar triangles have corners near 1.5 deg by shape (a strip, not a sliver; flat shading renders it as one
    face). Returns the m012 counts plus how many ring faces were left out."""
    ring = o.data.materials.find(f"FB_{PATH}_x_deep_50") if f"FB_{PATH}_x_deep_50" in o.data.materials else -1
    bm = bmesh.new()
    bm.from_mesh(o.data)
    angs, skipped = [], 0
    import m011
    for f in bm.faces:
        if f.material_index == ring and ring >= 0:
            skipped += 1
            continue
        angs.append(m011._fmin(f))
    bm.free()
    return {"under": sum(1 for x in angs if x < math.radians(POLISH_LIM)),
            "min_deg": round(math.degrees(min(angs)), 2) if angs else None, "bevel_ring_faces_skipped": skipped}


def _make(name, fn, role="part", budget=1000):
    """An object of separate clean closed shells (no union): n-gons triangulated, origin at the bottom centre, flat
    shading, UVs, bowties split."""
    t0 = time.time()
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget,
             collision=COLLISION[name], tint_var=0.0)
    o[OFF] = list(M._build_offset(fn))
    o.location = (0.0, 0.0, 0.0)
    _tri_ngons(o)
    _recentre(o)
    for p in o.data.polygons:
        p.use_smooth = False
    M.smart_uv(o, **UV)
    lg = {"uv_cut": m012._uv_unfold(o), "bowties": M.fix_bowties(o), "secs": round(time.time() - t0, 1)}
    K.drop_unused_slots(o)
    return o, lg


# ---- checks --------------------------------------------------------------------------------------------------------------------
def _keys(o):
    return [m.get("flintkit_key", m.name) if m else "" for m in o.data.materials]


def _kind(ks):
    if all(k.startswith("m044_leaf") for k in ks):
        return "leaf"
    if ks == {TRUNK}:
        return "trunk"
    if all(k.startswith("m044_flower") for k in ks):
        return "flower"
    if all(k.startswith("m044_path") for k in ks):
        return "tile"
    if all(k.startswith("m044_grass") for k in ks):
        return "turf"
    return "rock"


def shells_report(o):
    """Per shell: kind, tris, non-manifold edges and verts, boundary edges, self-intersecting face pairs inside the
    shell, volume. (m040)"""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = _keys(o)
    groups = {}
    for f in bm.faces:
        groups.setdefault(ids[f.index], []).append(f)
    out = []
    for k in range(n):
        fs = groups[k]
        es = {e for f in fs for e in f.edges}
        vs = list({v for f in fs for v in f.verts})
        ks = {keys[f.material_index] for f in fs}
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        hits = sum(1 for a_, b_ in tree.overlap(tree) if a_ < b_ and not set(fs[a_].verts) & set(fs[b_].verts))
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) / 3.0
        # winding: a manifold edge whose two faces run it the same way (one face flipped against its neighbour);
        # the total volume can stay positive with a flipped patch (fix round 1, B1), so check edges directly
        wind = sum(1 for e in es if len(e.link_loops) == 2 and e.link_loops[0].vert == e.link_loops[1].vert)
        out.append({"kind": _kind(ks), "tris": sum(len(f.verts) - 2 for f in fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary), "self_hits": hits,
                    "winding_errors": wind, "volume": round(vol, 4)})
    bm.free()
    return out


CONTACT = 0.03


def contact_report(o):
    return m040.contact_report(o, tol=CONTACT)


def _world_bm(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    off = Vector(o[OFF])
    for v in bm.verts:
        v.co += off                 # build frame
    bm.faces.ensure_lookup_table()
    return bm


def capping_report(h):
    """Spec 6 on the hero, build frame. (1) Flat cliff faces (n.z > 0.85) seen from above or from the sheet cameras:
    area of such faces whose sample points have a clear line toward the camera direction (0 required). (2) What a
    downward ray hits first on a 0.1 grid inside x +-8, y -10..10: rock (cliff / other), wedge, lawn, path, plants."""
    bm = _world_bm(h)
    ids, n = M._shell_ids(bm)
    keys = _keys(h)
    tree = BVHTree.FromBMesh(bm)
    sk = {}
    area = {}
    cx = {}
    for f in bm.faces:
        k_ = ids[f.index]
        sk.setdefault(k_, set()).add(keys[f.material_index])
        a_ = f.calc_area()
        area[k_] = area.get(k_, 0.0) + a_
        cx[k_] = cx.get(k_, 0.0) + f.calc_center_median().x * a_
    skind = {k: _kind(v) for k, v in sk.items()}
    # the cliff masses: big rock shells off the middle; the wedge: the big rock shell in the middle
    big = [k for k in range(n) if skind[k] == "rock" and area[k] > 100.0]
    cliffs = {k for k in big if abs(cx[k] / area[k]) > 3.0}
    wedge_ = next((k for k in big if abs(cx[k] / area[k]) < 1.0), None)
    dirs = {"up": (0, 0)}
    for nm, (az, el) in SHEET_VIEWS.items():
        dirs[nm] = (az, el)
    exposed = {k: 0.0 for k in dirs}
    where = []
    flat_area = 0.0
    for f in bm.faces:
        if ids[f.index] not in cliffs or f.normal.z <= 0.85:
            continue
        flat_area += f.calc_area()
        c = f.calc_center_median()
        pts = [c] + [c.lerp(v.co, 0.75) for v in f.verts]
        for nm, (az, el) in dirs.items():
            if nm == "up":
                d = Vector((0, 0, 1))
            else:
                a_, e_ = math.radians(az), math.radians(el)
                d = Vector((math.sin(a_) * math.cos(e_), -math.cos(a_) * math.cos(e_), math.sin(e_)))
            if d.dot(f.normal) <= 0:
                continue
            seen = 0
            for p in pts:
                hh = tree.ray_cast(p + d * 0.002, d, 200)
                if hh[0] is None:
                    seen += 1
            exposed[nm] += f.calc_area() * seen / len(pts)
            if seen:
                where.append((nm, [round(x, 2) for x in c], round(f.normal.z, 3), round(f.calc_area(), 3)))
    top = {}
    step = 0.1
    for xi in range(int(16 / step)):
        x = -8.0 + (xi + 0.5) * step
        for yi in range(int(20 / step)):
            y = Y0 + (yi + 0.5) * step
            hh = tree.ray_cast(Vector((x, y, 60.0)), Vector((0, 0, -1)), 200)
            if hh[0] is None:
                continue
            s_ = ids[hh[2]]
            k = skind[s_]
            if s_ in cliffs:
                k = "cliff_flat" if bm.faces[hh[2]].normal.z > 0.85 else "cliff_tips"
            elif s_ == wedge_:
                k = "wedge"
            elif k == "rock":
                k = "rocks"
            top[k] = top.get(k, 0.0) + step * step
    bm.free()
    rock_total = sum(v for k, v in top.items() if k in ("cliff_flat", "cliff_tips", "rocks", "wedge"))
    return {"flat_cliff_area": round(flat_area, 2), "exposed_flat": {k: round(v, 3) for k, v in exposed.items()},
            "exposed_where": where[:12],
            "from_above": {k: round(v, 2) for k, v in sorted(top.items())}, "rock_from_above": round(rock_total, 2)}


def tip_strip_report(h, step=0.05, dx=0.02, limit=1.1):
    """Decision 6: the exposed column-tip strip seen from straight above. Per side and per y (step), downward rays at
    x = 5.0 .. 8.3 (dx); the strip is the outermost contiguous run of cliff-mass hits. Returns per side max / mean
    width, the share of stations over `limit`, the worst stations (y, x from, x to) and whether a turf hit lies
    outboard of a run (a run cut in two by the turf counts as two runs; the outer one is reported)."""
    bm = _world_bm(h)
    ids, n = M._shell_ids(bm)
    keys = _keys(h)
    tree = BVHTree.FromBMesh(bm)
    area, cx, sk = {}, {}, {}
    for f in bm.faces:
        k_ = ids[f.index]
        a_ = f.calc_area()
        area[k_] = area.get(k_, 0.0) + a_
        cx[k_] = cx.get(k_, 0.0) + f.calc_center_median().x * a_
        sk.setdefault(k_, set()).add(keys[f.material_index])
    cliffs = {k for k in range(n) if _kind(sk[k]) == "rock" and area[k] > 100.0 and abs(cx[k] / area[k]) > 3.0}
    out = {}
    nx = int(round((8.3 - 5.0) / dx)) + 1
    for side in (1, -1):
        widths, worst = [], []
        y = Y0 + 0.3
        while y < Y1 - 0.05:
            run, best = None, None
            for i in range(nx):
                x = 5.0 + i * dx
                hh = tree.ray_cast(Vector((side * x, y, 60.0)), Vector((0, 0, -1)), 200)
                is_c = hh[0] is not None and ids[hh[2]] in cliffs
                if is_c:
                    run = (run[0], x) if run else (x, x)
                elif run:
                    best, run = run, None
            if run:
                best = run
            w = (best[1] - best[0] + dx) if best else 0.0
            widths.append(w)
            worst.append((round(w, 2), round(y, 2), round(best[0], 2) if best else None,
                          round(best[1], 2) if best else None))
            y += step
        worst.sort(reverse=True)
        out["R" if side > 0 else "L"] = {"max": round(max(widths), 3), "mean": round(sum(widths) / len(widths), 3),
                                         "over": round(sum(1 for w in widths if w > limit + 1e-6) / len(widths), 3),
                                         "worst": worst[:6]}
    bm.free()
    return out


def seam_report(h):
    """The seam contract on the hero mesh (build frame): rock verts past x +-8; anything behind y +10; the verts on the
    back plane; the landing at 10.4; the turf ends at the back plane."""
    bm = _world_bm(h)
    ids, n = M._shell_ids(bm)
    keys = _keys(h)
    sk = {}
    for f in bm.faces:
        sk.setdefault(ids[f.index], set()).add(keys[f.material_index])
    vk = {}
    for f in bm.faces:
        vk[f.verts[0].index] = None
        for v in f.verts:
            vk[v.index] = _kind(sk[ids[f.index]])
    past_side = sum(1 for v in bm.verts if vk.get(v.index) == "rock" and abs(v.co.x) > HALF_W + 5e-4)
    behind = sum(1 for v in bm.verts if v.co.y > Y1 + 5e-4)
    on_back = {}
    for v in bm.verts:
        if abs(v.co.y - Y1) < 1e-3:
            k = vk.get(v.index)
            on_back[k] = on_back.get(k, 0) + 1
    land = [v.co.z for v in bm.verts if vk.get(v.index) == "tile" and v.co.y > Y_LAND + 0.05 and v.co.z > RISE - 0.5 * BEVEL]
    turf_back = [v.co.z for v in bm.verts if vk.get(v.index) == "turf" and abs(v.co.y - Y1) < 1e-3]
    over = max([abs(v.co.x) - HALF_W for v in bm.verts] + [0.0])
    bm.free()
    return {"rock_verts_past_sides": past_side, "verts_behind_back_plane": behind,
            "verts_on_back_plane": on_back, "landing_top": [round(min(land), 3), round(max(land), 3)] if land else None,
            "turf_at_back_plane": [round(min(turf_back), 3), round(max(turf_back), 3)] if turf_back else None,
            "overhang_past_sides": round(over, 3),
            "back_plane_y_object": round(Y1 - h[OFF][1], 3), "sides_x_object": [round(-HALF_W - h[OFF][0], 3),
                                                                                 round(HALF_W - h[OFF][0], 3)]}


def walk_report():
    """The path's walk test (spec 4.2): each row's downhill edge height, the steps between rows (the lips), the toe
    step, the slope, the landing; pebble heights."""
    rows = tile_rows()
    edges = []
    for r, (ya, yb, za, zb) in enumerate(rows):
        for side in (0, 1):
            edges.append((r, side, round(za + TILE_DZ[r][side], 3)))
    lips = []
    for r in range(6):
        for side in (0, 1):
            up_prev = rows[r][3] + TILE_DZ[r][side]
            down_next = rows[r + 1][2] + TILE_DZ[r + 1][side]
            lips.append(round(down_next - up_prev, 3))
    mid = [round(abs(TILE_DZ[r][0] - TILE_DZ[r][1]), 3) for r in range(7)]
    return {"row_down_edges": edges, "row_lips": lips, "max_lip": max(lips), "mid_seam_steps": mid,
            "toe_step": TOE_Z, "slope_deg": round(math.degrees(math.atan(SLOPE)), 2),
            "tile_slope_deg": round(math.degrees(math.atan((rows[0][3] - rows[0][2]) / (rows[0][1] - rows[0][0]))), 2),
            "landing": RISE}


def pebble_heights(o):
    """Heights of the pebbles above the tile surface under each of their verts (hero or path part, build frame)."""
    bm = _world_bm(o)
    ids, n = M._shell_ids(bm)
    keys = _keys(o)
    out = []
    groups = {}
    for f in bm.faces:
        groups.setdefault(ids[f.index], []).append(f)
    for k, fs in groups.items():
        ks = {keys[f.material_index] for f in fs}
        vs = {v for f in fs for v in f.verts}
        if not all(x.startswith("m044_rock") for x in ks) or len(fs) > 14:
            continue
        cx = sum(v.co.x for v in vs) / len(vs)
        cy = sum(v.co.y for v in vs) / len(vs)
        if abs(cx) > 3.8 or cy < Y0 or cy > Y1:
            continue
        out.append(round(max(v.co.z - tile_top(v.co.x, v.co.y) for v in vs), 3))
    bm.free()
    return {"n": len(out), "max": max(out) if out else None}


# ---- render measurement (the study's masks, spec "Pixel boxes and masks") ------------------------------------------------
SHEET_REF = {
    "f34": {"wh": 1.456, "R": 36.4, "P": 30.6, "L": 20.6, "F": 11.8, "G": 32.4, "D": 0.7,
            "fifths_G": [14.3, 22.9, 24.0, 25.0, 13.8], "fifths_P": [8.7, 31.9, 25.2, 21.4, 12.7],
            "fifths_R": [13.6, 36.4, 31.5, 16.3, 2.3],
            "top": [.25, .32, .43, .50, .55, .56, .66, .73, .80, .80, .82, .91, .91, .93, .99, .97, .94, .91, .89, .84,
                    .31],
            "rock_warm": "#D6B7A3", "path": "#F8BB7B", "lawn": "#C3CF06", "bush": "#43791C", "yellow": "#E5DD0D"},
    "r34": {"wh": 1.500, "R": 36.9, "P": 29.5, "G": 32.8},
    "front": {"wh": 1.294, "R": 21.1, "P": 46.0, "L": 19.8, "F": 12.5, "G": 32.3,
              "top": [.08, .32, .56, .86, .91, .98, .96, .91, .90, .89, .89, .89, .89, .91, .96, .99, .96, .91, .65,
                      .39, .09], "rock_warm": "#D2B6A5", "path": "#FCC180", "lawn": "#BFCA06"},
    "side": {"wh": 1.612, "R": 76.2, "P": 0.3, "L": 11.4, "F": 11.9, "G": 23.3,
             "top": [.06, .25, .33, .32, .36, .39, .48, .56, .58, .57, .69, .69, .75, .75, .86, .95, .95, .99, .95,
                     .94, .84]},
    "rear": {"wh": 1.337, "R": 21.6, "P": 46.1, "G": 31.9},
    "top": {"wh": 0.739, "R": 17.4, "P": 48.2, "L": 22.5, "F": 11.5, "G": 34.0},
}


def _hsv(px):
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0)
    return h, s, mx


def classify(px):
    """The study's cls() on an sRGB 0-1 image: 1 rock R, 2 path P, 3 lawn L, 4 foliage F, 5 dirt / trunk D."""
    h, s, v = _hsv(px)
    G = (h >= 45) & (h <= 170) & (s >= 0.28) & (v >= 0.12)
    Lw = G & (h < 80) & (v >= 0.62)
    F = G & ~Lw
    T = (v < 0.25) & (s < 0.35)
    Pa = ~G & (h >= 15) & (h <= 42) & (s >= 0.33) & (v >= 0.62)
    D = ~G & ~Pa & (h <= 40) & (s >= 0.40) & (v >= 0.15) & (v < 0.62)
    Rk = ~G & ~T & ~D & ~Pa & (((h <= 50) | (h >= 190)) & (s < 0.40) & (v >= 0.25))
    out = np.zeros(v.shape, np.int8)
    out[Rk] = 1
    out[Pa] = 2
    out[Lw] = 3
    out[F] = 4
    out[D] = 5
    return out, h, s, v


def measure(path, bg_tol=0.04):
    kit = K.NS["KIT"]
    px = np.clip(kit["load_px"](path)[::-1, :, :3], 0, 1)
    bg = np.median(np.concatenate([px[:4, :4].reshape(-1, 3), px[:4, -4:].reshape(-1, 3)]), axis=0)
    sil = np.abs(px - bg).max(-1) > bg_tol
    cls, h, s, v = classify(px)
    ys, xs = np.nonzero(sil)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    H, W = y1 - y0 + 1, x1 - x0 + 1
    c = np.where(sil, cls, 0)
    cnt = {k: int((c == i).sum()) for k, i in (("R", 1), ("P", 2), ("L", 3), ("F", 4), ("D", 5))}
    tot = max(1, sum(cnt.values()))
    sh = {k: round(100 * v_ / tot, 1) for k, v_ in cnt.items()}
    sh["G"] = round(sh["L"] + sh["F"], 1)

    def fif(ids_):
        gy = np.nonzero(np.isin(c, ids_))[0]
        f = [0] * 5
        for y in gy:
            f[min(4, int((y1 - y) / H * 5))] += 1
        t = max(1, sum(f))
        return [round(100 * x / t, 1) for x in f]
    prof = []
    for f in np.linspace(0, 1, 21):
        col = int(round(x0 + f * (W - 1)))
        on = np.nonzero(sil[:, max(x0, col - 1):col + 2].any(1))[0]
        prof.append(round(float((y1 - on.min()) / H), 2) if len(on) else 0.0)
    rgb = px * 255

    def med(mask):
        sel = rgb[mask]
        return "#" + "".join(f"{int(x):02X}" for x in np.median(sel, axis=0)) if len(sel) else None
    yel = (h >= 46) & (h <= 60) & (s >= 0.6) & (v >= 0.85) & sil
    return {"wh": round(W / H, 3), **sh, "fifths_G": fif([3, 4]), "fifths_P": fif([2]), "fifths_R": fif([1]),
            "top": prof, "rock_all": med(c == 1), "rock_warm": med((c == 1) & (h <= 60)),
            "path": med(c == 2), "lawn": med(c == 3), "bush": med(c == 4),
            "emerald": med((c == 4) & (h >= 95)), "fresh": med((c == 4) & (h < 95)), "yellow": med(yel),
            "yellow_pct": round(100 * yel.sum() / max(1, sil.sum()), 2),
            # the bushes' two tones: emerald (h >= 95) share of all foliage F; and the verifier's leaf-hue area
            # (green of hue >= 85 at any value, % of the classed pixels)
            "emerald_share": round(float(((c == 4) & (h >= 95)).sum()) / max(1, int((c == 4).sum())), 3),
            "leaf_hue_pct": round(100 * float((np.isin(c, [3, 4]) & (h >= 85)).sum()) / tot, 1)}


def measure_views(out_dir=None):
    d = out_dir or f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    res = {}
    for k, f in (("f34", "f34_sheet"), ("f34_lit", "f34_lit_sheet"), ("front", "front_sheet"), ("side", "side_sheet"),
                 ("rear", "rear_sheet"), ("r34", "r34_sheet"), ("top", "top_sheet")):
        try:
            m = measure(f"{d}/{f}.png")
        except Exception as e:      # a view not rendered yet
            res[k] = str(e)
            continue
        ref = SHEET_REF["f34" if k == "f34_lit" else k]
        if "top" in ref:
            m["top_err_mean"] = round(float(np.mean(np.abs(np.array(m["top"]) - np.array(ref["top"])))), 3)
            m["top_err_max"] = round(float(np.max(np.abs(np.array(m["top"]) - np.array(ref["top"])))), 3)
        m["sheet"] = {kk: vv for kk, vv in ref.items() if kk != "top"}
        res[k] = m
    return res


# ---- build ---------------------------------------------------------------------------------------------------------------------
TARGET_SIZE = ((17.2, 0.4), (20.4, 0.4), (12.5, 0.5))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me is not None and isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m044_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib",
                                                                                 "StoneRamp"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build(render=True, parts=True, close=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    if parts:
        for nm in PARTS:
            objs[nm], log[nm] = _make(nm, FNS[nm])
        log["border_plants"] = {k: dict(v) for k, v in PLANT_INFO.items()}
    h, log["hero"] = _make(HERO, hero, role="hero", budget=4000)
    log["plants"] = {k: dict(v) for k, v in PLANT_INFO.items()}
    log["boulders"] = {k: dict(v) for k, v in BOULDER_INFO.items()}
    log["cliffs"] = {str(k): dict(v) for k, v in CLIFF_INFO.items()}
    _cleanup_tmp()
    order = [h] + [objs[n] for n in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    audits = [M.audit(o) for o in order]
    thin = {o.name: _thin(o) for o in order}
    shells = {o.name: shells_report(o) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = 4000 if o is h else 1000
        if au["tris"] > lim:
            problems.append(f"{o.name}: {au['tris']} tris over {lim}")
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "wire_edges", "loose_verts",
                  "zero_area_faces", "ngons"):
            if au[k]:
                problems.append(f"{o.name}: {k} {au[k]}")
        if au["normals"] != "outward":
            problems.append(f"{o.name}: normals {au['normals']}")
        if thin[o.name]["under"]:
            problems.append(f"{o.name}: {thin[o.name]['under']} faces with a corner under {POLISH_LIM} deg")
        for i, s in enumerate(shells[o.name]):
            for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "self_hits", "winding_errors"):
                if s[k]:
                    problems.append(f"{o.name} shell {i} ({s['kind']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['kind']}): not closed outward (volume {s['volume']})")
    for nm in (WEDGE_P,):
        if nm in shells and len(shells[nm]) != 1:
            problems.append(f"{nm}: {len(shells[nm])} shells, expected 1")
    for nm in (CLIFF_L, CLIFF_R):
        if nm in shells and len(shells[nm]) != 2:
            problems.append(f"{nm}: {len(shells[nm])} shells, expected 2 (mass + toe rock)")
    contact = {o.name: contact_report(o) for o in order if o is h or o.name in (BORDER_L, BORDER_R, PATH_P)}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} shells touch nothing within {CONTACT}, {c['unchained']} have no "
                            f"chain of contact to the ground")
    cap = capping_report(h)
    tips = tip_strip_report(h)
    for sd, t_ in tips.items():
        if t_["max"] > 1.1 + 1e-6:
            problems.append(f"{HERO}: tip strip {sd} up to {t_['max']} (decision 6: <= 1.1)")
    flat_skirt = {k: v["skirt_tilt"] for k, v in PLANT_INFO.items() if min(v.get("skirt_tilt") or [90]) < SKIRT_MIN_TILT}
    if flat_skirt:
        problems.append(f"{HERO}: skirt leaves flatter than {SKIRT_MIN_TILT} deg {flat_skirt}")
    if max(cap["exposed_flat"].values()) > 0.0:
        problems.append(f"{HERO}: exposed flat column-top area {cap['exposed_flat']}")
    if cap["from_above"].get("wedge", 0) > 0:
        problems.append(f"{HERO}: wedge visible from above {cap['from_above']['wedge']}")
    seam = seam_report(h)
    if seam["rock_verts_past_sides"] or seam["verts_behind_back_plane"]:
        problems.append(f"{HERO}: seam contract broken {seam}")
    walk = walk_report()
    peb = pebble_heights(h)
    if walk["max_lip"] > 0.12 + 1e-6 or (peb["max"] or 0) > 0.25 + 1e-3:
        problems.append(f"{HERO}: walk test {walk['max_lip']} / pebbles {peb['max']}")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WLH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (spec 7: none)")
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    kinds = {}
    for s in shells[HERO]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts", "transforms_applied")} for au in audits],
           "shells": kinds, "contact": contact, "capping": cap, "tip_strip": tips, "seams": seam, "walk": walk,
           "pebbles": peb, "winding": {o.name: sum(s["winding_errors"] for s in shells[o.name]) for o in order},
           "thin": thin, "log": log, "problems": problems, "uv": uv,
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order, close=close)
        out["measure"] = measure_views()
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders ---------------------------------------------------------------------------------------------------------------------
# spec 2.5 / decision 9: f34_sheet governs; the *_sheet shots hide the floor and use the 3x lens (m033._long_lens)
# f34_sheet (44, 12): the spec 2.5 probe (az 38-68 x e 12-30, M044_spec.md "Stage 1") scored on W:H, R / P / G and the
# top profile; the sheet's path corners give an orthographic-equivalent camera of about (47, 23) whose W:H the sheet's
# strong perspective widens. f34_lit: the same view mirrored (rendered from (-44, 12), flipped left-right), so the
# studio's front-left key lights the near cliff as the sheet's front-right light does (colour comparison only).
SHEET_VIEWS = {"f34_sheet": (44, 12), "front_sheet": (0, 6), "side_sheet": (90, 4), "rear_sheet": (180, 6),
               "r34_sheet": (-120, 15), "top_sheet": (0, 89)}
LIT_VIEW = (-44, 12)
PARTS_SHOT = (-35, 25)
M040_GAP = 14.2             # M040's build origin sits this far behind ours (its lip front y -4.2 on our back plane)


def _copy(tag, src, m, coll):
    c = bpy.data.objects.new(f"{PFX}{tag}", src.data)
    coll.objects.link(c)
    c.matrix_world = m
    return c


def _frame_of(o):
    """An object's build frame in world space."""
    return o.matrix_world @ Matrix.Translation(-Vector(o[OFF]))


def _exploded(objs):
    """Copies of the six parts laid out like the sheet's exploded view: the left border above the left cliff, the
    path above the wedge, the right border above the right cliff."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []
    o0 = Matrix.Translation((objs[0].location.x + 120, objs[0].location.y, 0))
    place = {CLIFF_L: (-7.0, 0, 0), BORDER_L: (-7.0, 0, 5.0), WEDGE_P: (0, 0, 0), PATH_P: (0, 0, 4.0),
             CLIFF_R: (7.0, 0, 0), BORDER_R: (7.0, 0, 5.0)}
    for nm, d in place.items():
        if nm in by:
            shown.append(_copy("expl_" + nm, by[nm], o0 @ Matrix.Translation(Vector(d)) @
                               Matrix.Translation(Vector(by[nm][OFF])), coll))
    bpy.context.view_layer.update()
    return shown


def _m040_copy(h):
    """A copy of M040's hero with its lip front on our back plane (same x): the plateau shot (spec 4.2.6)."""
    src = bpy.data.objects.get("StoneCliff")
    if not src or "m040_offset" not in src:
        return None
    m = _frame_of(h) @ Matrix.Translation((0.0, M040_GAP, 0.0)) @ Matrix.Translation(Vector(src["m040_offset"]))
    return _copy("m040", src, m, h.users_collection[0])


def _scale_markers(h):
    """Three 5.5-stud character stand-ins: on the ground at the toe, on the path at y 0, on the landing."""
    out = []
    fr = _frame_of(h)
    for i, (x, y) in enumerate(((-1.5, -11.5), (1.0, 0.0), (-1.0, 8.8))):
        a = K.fk().Asset(PFX + f"char{i}", "probe", seed=1, tint_var=0.0)
        z = 0.0 if y < Y0 else tile_top(x, y)
        a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat="m040_connector", tint=0.7)
        a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat="m040_connector", tint=0.7)
        a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat="m040_connector", tint=0.7)
        c = a.finish(collection=h.users_collection[0], mark_asset=False)
        c.matrix_world = fr @ Matrix.Translation((x, y, z))
        out.append(c)
    bpy.context.view_layer.update()
    return out


def _close(objs, path, az, el, centre, radius):
    """m033.render_close with the studio floor hidden."""
    kit = K.NS["KIT"]
    ground = bpy.data.objects.get("FB_Ground")
    orig = kit["render_group"]

    def rg(group, path_, azimuth=-22, elevation=20):
        if ground:
            ground.hide_render = True
        return orig(group, path_, azimuth, elevation)
    kit["render_group"] = rg
    try:
        return m033.render_close(objs, path, az, el, centre, radius)
    finally:
        kit["render_group"] = orig
        if ground:
            ground.hide_render = False


def _flip_lit():
    """f34_lit_sheet.png: the (-44, 12) render mirrored left-right (the sheet's composition under the sheet's light)."""
    kit = K.NS["KIT"]
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    src = f"{d}/f34_litraw_sheet.png"
    try:
        px = kit["load_px"](src)
    except Exception:
        return None
    dst = f"{d}/f34_lit_sheet.png"
    kit["save_px"](np.ascontiguousarray(px[:, ::-1]), dst)
    import os
    os.remove(src)
    return dst


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    m40 = _m040_copy(h)
    marks = _scale_markers(h)
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        by = {o.name: o for o in objs}
        for o in objs[1:]:
            extra["part_" + o.name.replace("StoneRamp", "").lower()] = ([o], *PARTS_SHOT)
        if WEDGE_P in by:
            extra["wedge_underside"] = ([by[WEDGE_P]], -35, -35)
        if shown:
            extra["exploded"] = (shown, -35, 25)
        if m40:
            extra["plateau_f34"] = ([h, m40], 45, 20)
            extra["plateau_front"] = ([h, m40], 0, 8)
        extra["scale"] = ([h] + marks, 60, 12)
        extra["f34_litraw_sheet"] = ([h], *LIT_VIEW)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = m033._long_lens(kit)
        try:
            sheet = M.views(NUM, [h], extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet, "f34_lit": _flip_lit()}
        if close:
            d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
            fr = _frame_of(h)
            # 1. Path to Border Junction: the +x border at y -3 (turf over the tiles, lime side, column tips)
            out["junc_cu"] = _close([h], f"{d}/junc_cu.png", 40, 30, fr @ Vector((5.6, -3.0, path_z(-3.0))), 2.8)
            # 3. Thickness / cross-section: the path on the wedge and the border on the cliff, at the toe end
            out["sect_cu"] = _close([h], f"{d}/sect_cu.png", 20, 8, fr @ Vector((4.6, -9.6, 1.0)), 2.8)
            # a bush close-up (round two-tone domes, not stars)
            out["bush_cu"] = _close([h], f"{d}/bush_cu.png", 60, 15, fr @ Vector((5.8, -5.2, path_z(-5.2) + 1.2)),
                                    1.8)
        return out
    finally:
        for o in shown + marks + ([m40] if m40 else []):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if o in marks and me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def preview(names=("f34_sheet", "front_sheet", "side_sheet", "top_sheet"), vfx=False, measure_too=True, views=None):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    views = views or {k: SHEET_VIEWS[k] for k in names}
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        sheet = M.views(NUM, [h], names=(), extra={k: ([h], *v) for k, v in views.items()}, vfx=vfx)
    finally:
        kit["render_group"] = orig
    return {"sheet": sheet, "measure": measure_views() if measure_too else None}


def hero_only():
    """Rebuild just the hero (tuning loop)."""
    M.coll(NUM, TITLE)
    palette()
    h, lg = _make(HERO, hero, role="hero", budget=4000)
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals", "zero_area_faces")}, "log": lg,
            "thin": m012._thin(h, POLISH_LIM)}
