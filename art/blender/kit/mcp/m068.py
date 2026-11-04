"""068 Timber Hut (references/068.png, remade 2026-11-03) on the shared library (kit_parts / kit_build): a walk-in
gable-roofed plank cabin with its dressing. See M068_spec.md (brief first, then one section per stage).

    import importlib, kit_parts, kit_build, m068
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m068); m068.build()

Build frame (studs): front -Y (the door gable), +X right, ground z 0, the walls' rectangle centred on x 0 / y 0, ridge
along Y. Every object ends with its origin at its bbox bottom centre; o["m068_offset"] is that origin in the build
frame.
- One course of big chamfered pale stone blocks (four a side) with a lighter, taller block under each corner post;
  a plank floor at 2.60 on it (dark underlay under the seams) with a threshold through the doorway.
- Walls of five rows of 0.40 planks (V seams from chamfered outer edges, staggered butt joints, rows and joints
  overlapping 0.004 at the back so nothing is see-through) between four chamfered corner posts. A barred window with
  a chunky light board frame and a dark inner shutter in each long wall: -X toward the front (the hero view), +X
  centred (the side cell).
- The door in the front gable between two tall door posts on golden caps, a lintel, a collar at eave level; the
  plank leaf stands open inward 95 deg (the DoorFrame part carries it closed, hinge stored).
- Octagonal-ended eave beams (plates) projecting past both gables with iron bracket plates and golden pegs (close-up
  A); rafters, purlins, eave blocking, a ridge beam with golden rope bands; vertical gable boards closed edge to
  edge; crossed bargeboards with a golden saddle and one cleat each.
- A cream canvas roof of two closed slabs, four panels along the ridge and two down each slope with raised seam
  strips (the sheet's panel grid), four golden U ties on each eave.
- A square stone chimney (two blocks with a notched joint, a crenellated cap, a dark flue, a flashing collar) on the
  +X slope in the front half (the hero view).
- Two-tread stairs on blocks (three 0.87 / 0.86 / 0.87 rises), three Neon lanterns (one on an iron bracket off the
  -X eave beam, two on wall brackets flanking the door), a red three-point banner with the white diamond emblem on a
  pole with a block top, a crossarm through it and an X lashing, at the back-left corner; a barrel and a crate along
  -X (the hero view) and a second barrel at the +X back corner (the side and top cells).
Parts: TimberCabinRoofPanel, ...RidgeBeam, ...Chimney, ...Banner, ...Lantern, ...WallPanel, ...WindowWall,
...DoorFrame, ...GableFrame, ...Floor, ...Stairs, ...Foundation.
Stages 5-6: lantern glass m068_glow at emission 1.0 (Neon) with a heat_glow socket per lantern; a thin pale
chimney_smoke socket at the flue.
"""
import math

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_build as B
import kit_parts as P

NUM, TITLE = 68, "Timber Hut"
HERO = "TimberCabin"
ROOF_P, RIDGE_P, CHIMNEY_P = "TimberCabinRoofPanel", "TimberCabinRidgeBeam", "TimberCabinChimney"
BANNER_P, LANTERN_P, WALL_P = "TimberCabinBanner", "TimberCabinLantern", "TimberCabinWallPanel"
WINDOW_P, DOOR_P, GABLE_P = "TimberCabinWindowWall", "TimberCabinDoorFrame", "TimberCabinGableFrame"
FLOOR_P, STAIRS_P, FOUND_P = "TimberCabinFloor", "TimberCabinStairs", "TimberCabinFoundation"

TIMBER, TIMBER_END, TIMBER_DEEP = "m068_timber", "m068_timber_end", "m068_timber_deep"
CANVAS, CANVAS_DEEP = "m068_canvas", "m068_canvas_deep"
STONE, STONE_LIGHT, STONE_DARK, SOOT = "m068_stone", "m068_stone_light", "m068_stone_dark", "m068_soot"
IRON, GLOW, ROPE, ROPE_DEEP = "m068_iron", "m068_glow", "m068_rope", "m068_rope_deep"
BANNER, WHITE = "m068_banner", "m068_cloth_white"

# key -> (hex, roughness, metal, emission, low specular). Stage 4: sheet medians (spec "Stage 4"), K.calibrate'd.
PALETTE = {
    TIMBER: ("#B05A22", 0.85, 0.0, 0.0, True),
    TIMBER_END: ("#D88A3A", 0.8, 0.0, 0.0, True),
    TIMBER_DEEP: ("#7A3A14", 0.9, 0.0, 0.0, True),
    CANVAS: ("#F2E2BC", 0.95, 0.0, 0.0, True),
    CANVAS_DEEP: ("#C9AE86", 0.95, 0.0, 0.0, True),
    STONE: ("#A39698", 0.9, 0.0, 0.0, True),
    STONE_LIGHT: ("#C2B6B6", 0.9, 0.0, 0.0, True),
    STONE_DARK: ("#857B7E", 0.9, 0.0, 0.0, True),
    SOOT: ("#1F1E23", 1.0, 0.0, 0.0, True),
    IRON: ("#55515A", 0.55, 0.4, 0.0, False),
    GLOW: ("#F8B428", 0.5, 0.0, 1.0, False),
    ROPE: ("#ECA01C", 0.9, 0.0, 0.0, True),
    ROPE_DEEP: ("#A8701E", 0.95, 0.0, 0.0, True),
    BANNER: ("#D41C1E", 0.9, 0.0, 0.0, True),
    WHITE: ("#F6F0EA", 0.9, 0.0, 0.0, True),
}
TARGETS = {TIMBER: ((0xC4, 0x68, 0x26), "brown"), TIMBER_END: ((0xF0, 0x9A, 0x44), "brown"),
           TIMBER_DEEP: ((0x8E, 0x46, 0x18), "brown"), CANVAS: ((0xFE, 0xF2, 0xCC), "all"),
           CANVAS_DEEP: ((0xE4, 0xC8, 0x9A), "all"), STONE: ((0xB3, 0xA6, 0xA7), "all"),
           STONE_LIGHT: ((0xCC, 0xBE, 0xBE), "all"), STONE_DARK: ((0x9C, 0x91, 0x92), "all"),
           SOOT: ((0x1F, 0x1E, 0x23), "all"), IRON: ((0x5E, 0x5B, 0x60), "all"),
           ROPE: ((0xEC, 0xA0, 0x1C), "brown"), ROPE_DEEP: ((0xB0, 0x74, 0x1C), "brown"),
           BANNER: ((0xE6, 0x1B, 0x1C), "all"), WHITE: ((0xF6, 0xF0, 0xEA), "all")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)


def mix(k1, k2, t):
    return P.mix(k1, k2, t)


# ---- layout (spec "Brief") ---------------------------------------------------------------------------------------------
PITCH = 32.0
PT = math.tan(math.radians(PITCH))
COS, SIN = math.cos(math.radians(PITCH)), math.sin(math.radians(PITCH))
RIDGE_Z = 16.00                   # canvas top at the apex
CT = 0.12                         # canvas thickness (perpendicular)
CTV = CT / COS
EAVE = 7.45                       # canvas eave edge |x|
CAN_Y = 9.247                     # canvas gable ends |y| (0.003 inside the bargeboards)
FLOOR_Z = 2.60
OVL = 0.002                       # closed joints: neighbours sink this far into each other
PLATE = (6.30, 7.20, 10.40, 11.20, 10.80, 0.12)  # x0, x1, z0, z1, |y| end, chamfer
EAVE_BLK = (6.85, 7.08)
WALL_IN_X, WALL_IN_Y, WALL_T = 6.60, 7.60, 0.40
ROW_PITCH, ROW_Z0, N_ROWS = 1.62, 2.30, 5
POST = (6.10, 7.20, 7.10, 8.20)   # corner post |x| and |y| ranges
CORNER = (6.11, 7.75, 7.11, 8.75, 2.60)          # corner block |x|, |y| ranges, top
COURSE_Z = 2.30                   # run blocks' top (floor and wall sills on them)
DOOR_X, DOOR_TOP = 1.80, 9.60
DPOST = (1.80, 2.90, -9.50, -8.405)              # door post |x| range, y range
BB_Y, BB_D = (9.25, 10.15), 0.92                 # bargeboards |y|, depth
RAFTER_Y = (-3.90, 0.0, 3.90)                    # four bays: the sheet's four canvas panels along the ridge
RAFTER_W, RAFTER_D = 0.50, 0.60
RIDGE_W, RIDGE_END, RIDGE_Z0 = 1.00, 10.75, 14.536
PURLIN_X, PURLIN_W, PURLIN_H = 4.10, 0.50, 0.50
SINK_TOP = 0.015
CHIMNEY = (2.20, -1.95)           # chimney centre: +X slope, front half (hero view), between the rafters at -3.9 / 0
CH_W, CH_JOINT, CH_Z1, CAP_Z, CH_TOP = 2.60, 16.60, 18.40, 19.00, 19.40
HOLE = (CHIMNEY[0] - CH_W / 2 - OVL, CHIMNEY[0] + CH_W / 2 + OVL, CHIMNEY[1] - CH_W / 2 - OVL,
        CHIMNEY[1] + CH_W / 2 + OVL)
COLLAR = (0.12, 0.10)


def zt(x):
    """Canvas top (unsagged) at x."""
    return RIDGE_Z - PT * abs(x)


def zu(x):
    """Canvas underside (unsagged) at x."""
    return zt(x) - CTV


def row_z(i):
    """Wall plank row i: bottom, top (rows overlap 2 * OVL at the back; the bottom row 0.003 over the course, the top
    row OVL into the plate)."""
    z0 = ROW_Z0 + ROW_PITCH * i + (0.003 if i == 0 else -OVL)
    return z0, ROW_Z0 + ROW_PITCH * (i + 1) + OVL


def xz(s=1.0):
    """to3 for a 2D (x, z) profile extruded along Y, x mirrored by s."""
    return lambda u, v, w: Vector((s * u, w, v))


def oct_rect(x0, x1, y0, y1, ch):
    return [(x0 + ch, y0), (x1 - ch, y0), (x1, y0 + ch), (x1, y1 - ch), (x1 - ch, y1), (x0 + ch, y1), (x0, y1 - ch),
            (x0, y0 + ch)]


def bx(a, lo, hi, key, name, kind, m=None, amp=0.04):
    """An axis box lo..hi with its corners sorted (mirrored inputs are fine)."""
    lo2 = tuple(min(p, q) for p, q in zip(lo, hi))
    hi2 = tuple(max(p, q) for p, q in zip(lo, hi))
    return P.box(a, lo2, hi2, key, m=m, name=name, kind=kind, amp=amp)


# ---- foundation ------------------------------------------------------------------------------------------------------------
RUNS = {"R": (-7.08, 7.08), "L": (-7.08, 7.08), "F": (-6.08, 6.08), "B": (-6.08, 6.08)}
RUN_CUTS = {"R": (-3.35, 0.20, 3.65), "L": (-3.70, -0.15, 3.40), "F": (-3.10, 0.0, 3.05), "B": (-2.95, 0.10, 3.10)}
CHIPS = {"R": {1: "+x-y"}, "L": {2: "-x-y"}, "F": {0: "+x-y"}, "B": {3: "-x-y"}}
JOINT = 0.02                      # dark joint between blocks
BLOCK_D, BLOCK_IN = 1.00, 6.40    # run depth, inner face |x| (long sides; ends: |y| 7.40)


def _run_frame(side, t):
    """Matrix placing a run block centred at t along its side (local x along the run, local -y outward)."""
    if side in ("R", "L"):
        s = 1 if side == "R" else -1
        return Matrix.Translation((s * (BLOCK_IN + BLOCK_D / 2), t, 0.0)) @ Matrix.Rotation(math.radians(90 * s), 4, "Z")
    s = -1 if side == "F" else 1
    yc = s * (WALL_IN_Y - 0.20 + BLOCK_D / 2)
    return Matrix.Translation((t, yc, 0.0)) @ Matrix.Rotation(0.0 if s < 0 else math.pi, 4, "Z")


def foundation_run(a, side):
    """One side's single course of big chamfered blocks between the corner blocks (the sheet's four a side), dark
    joints between them, one chipped top corner."""
    t0, t1 = RUNS[side]
    edges = [t0] + list(RUN_CUTS[side]) + [t1]
    for i in range(len(edges) - 1):
        a0 = edges[i] + (JOINT / 2 if i else 0.0)
        a1 = edges[i + 1] - (JOINT / 2 if i < len(edges) - 2 else 0.0)
        L = a1 - a0
        ch = CHIPS[side].get(i)
        P.block(a, L, BLOCK_D, COURSE_Z, STONE, m=_run_frame(side, (a0 + a1) / 2), ch=0.10,
                chips=[(ch, 0.30)] if ch else (), chip_key=STONE_LIGHT, mottle=0.03, name=f"blk_{side}{i}", kind="stone")


def corner_block(a, sx, sy):
    """The lighter, taller block under a corner post (proud of the course), one chipped outer top corner."""
    x0, x1, y0, y1, ztop = CORNER
    c = (sx * (x0 + x1) / 2, sy * (y0 + y1) / 2)
    tag = f"{'L' if sx < 0 else 'R'}{'F' if sy < 0 else 'B'}"
    corner = f"{'+' if sx > 0 else '-'}x{'+' if sy > 0 else '-'}y"
    P.block(a, x1 - x0, y1 - y0, ztop, STONE_LIGHT, m=Matrix.Translation((c[0], c[1], 0.0)), ch=0.10,
            chips=[(corner, 0.34)], chip_key=mix(STONE_LIGHT, STONE, 0.5), mottle=0.03, name=f"corner_{tag}",
            kind="stone")


# ---- floor -------------------------------------------------------------------------------------------------------------------
FLOOR_W, FLOOR_GAP, FLOOR_N = 1.26, 0.06, 10
THRESH = ((-1.78, -0.62), (-0.58, 0.58), (0.62, 1.78))
UNDER = (5.40, WALL_IN_Y - 0.20 + OVL, 2.20)


def floor(a, feet=False):
    """Ten deck planks along Y on the end courses, the outer two notched round the corner posts and blocks; a dark
    underlay board under the seams; three threshold planks out through the doorway on a threshold beam; two hidden
    sleepers (feet: the Floor part's short dark feet instead)."""
    x0 = -(FLOOR_N * FLOOR_W + (FLOOR_N - 1) * FLOOR_GAP) / 2
    ye = WALL_IN_Y + OVL
    cx, cy = CORNER[0] + OVL, CORNER[2] + OVL
    for i in range(FLOOR_N):
        xa = x0 + i * (FLOOR_W + FLOOR_GAP)
        xb = xa + FLOOR_W
        nm = f"deck_{i}"
        if i in (0, FLOOR_N - 1):
            s = -1 if i == 0 else 1
            xi = xb if s < 0 else xa
            xo = s * (WALL_IN_X + OVL)
            poly = [(xi, -ye), (s * cx, -ye), (s * cx, -cy), (xo, -cy), (xo, cy), (s * cx, cy), (s * cx, ye), (xi, ye)]
            if s > 0:
                poly = poly[::-1]
            p = P.ext(a, poly, COURSE_Z - OVL, FLOOR_Z, TIMBER, name=nm, kind="deck", amp=0.05)
        else:
            p = P.box(a, (xa, -ye, COURSE_Z - OVL), (xb, ye, FLOOR_Z), TIMBER, name=nm, kind="deck", amp=0.05)
        P.texture(a, p.vs, 0.03, P.seed(nm), scale=0.35)
    for i, (xa, xb) in enumerate(THRESH):
        P.box(a, (xa, DPOST[2], COURSE_Z + 0.003), (xb, -WALL_IN_Y + OVL, FLOOR_Z), TIMBER, name=f"thresh_{i}",
              kind="thresh", amp=0.05)
    P.box(a, (-DOOR_X + 0.015, -9.48, 1.70 if feet else 1.733), (DOOR_X - 0.015, -8.405, COURSE_Z - 0.003),
          TIMBER_DEEP, name="thresh_beam", kind="beam", tint=0.97)
    ux, uy, uz = UNDER
    P.box(a, (-ux, -uy, uz), (ux, uy, COURSE_Z), mix(TIMBER_DEEP, SOOT, 0.4), name="floor_under", kind="board",
          tint=0.97)
    if feet:
        for i in range(FLOOR_N):
            xc = x0 + i * (FLOOR_W + FLOOR_GAP) + FLOOR_W / 2
            ztop = uz - 0.003 if abs(xc) + 0.30 < ux else COURSE_Z - 0.003
            for k, y in enumerate((-5.0, 5.0)):
                P.box(a, (xc - 0.30, y - 0.30, 1.70), (xc + 0.30, y + 0.30, ztop), TIMBER_DEEP, name=f"floor_foot{i}_{k}",
                      kind="beam")
    else:
        for i, y in enumerate((-3.5, 3.5)):
            P.box(a, (-(BLOCK_IN - 0.005), y - 0.5, 1.70), (BLOCK_IN - 0.005, y + 0.5, uz - 0.003), TIMBER_DEEP,
                  name=f"sleeper_{i}", kind="beam", tint=0.95)


# ---- walls -------------------------------------------------------------------------------------------------------------------
PLANK_CH = 0.10
WIN = (1.50, ROW_Z0 + 2 * ROW_PITCH, ROW_Z0 + 4 * ROW_PITCH, 0.80, 0.20)   # opening half width, bottom, top; frame
WIN_Y = {-1: -3.40, 1: 0.0}       # window centre y: -X toward the front (hero view), +X centred (side cell)
LONG_JOINTS = {-1: {0: [1.20], 1: [4.40], 2: [2.60], 3: [-0.60, 4.80], 4: [0.80]},
               1: {0: [-2.60], 1: [3.40], 2: [-4.20, 3.40], 3: [-3.80, 4.60], 4: [-2.60]}}
END_JOINTS = {1: {0: [-2.00], 1: [2.60], 2: [-2.00], 3: [2.60], 4: [-2.00]}, -1: {}}


def segs(t0, t1, joints=(), cut=None):
    """Plank spans from t0 to t1: butt joints overlap 2 * OVL; an opening `cut` (c0, c1) leaves a gap."""
    edges = [(t0, False)] + [(j, True) for j in sorted(joints)] + [(t1, False)]
    out = []
    for i in range(len(edges) - 1):
        a0 = edges[i][0] - (OVL if edges[i][1] else 0.0)
        a1 = edges[i + 1][0] + (OVL if edges[i + 1][1] else 0.0)
        if cut and a1 > cut[0] and a0 < cut[1]:
            if a0 < cut[0]:
                out.append((a0, cut[0]))
            if a1 > cut[1]:
                out.append((cut[1], a1))
        else:
            out.append((a0, a1))
    return out


def plank(a, wall, s, t0, t1, z0, z1, name, band=True):
    """One wall plank: a 6-sided section 0.37-0.40 thick with its outer top and bottom edges chamfered 0.10 (the dark
    V seams between rows); planks over 2.0 long get a darker end band 30 % from a seeded end (by position)."""
    r = P.rng(name)
    uo = WALL_T - r.uniform(0.0, 0.03)
    H = z1 - z0
    c = PLANK_CH
    sec = [(0.0, 0.0), (uo - c, 0.0), (uo, c), (uo, H - c), (uo - c, H), (0.0, H)]
    if wall == "long":
        mp = lambda u, v, t: Vector((s * (WALL_IN_X + u), t, z0 + v))       # noqa: E731
    else:
        mp = lambda u, v, t: Vector((t, s * (WALL_IN_Y + u), z0 + v))       # noqa: E731
    ts, bk = [t0, t1], None
    if band and t1 - t0 > 2.0:
        f = 0.30 * (t1 - t0)
        if r.random() < 0.5:
            ts, bk = [t0, t0 + f, t1], 0
        else:
            ts, bk = [t0, t1 - f, t1], 1
    p = P.prism(a, [[mp(u, v, t) for u, v in sec] for t in ts], TIMBER, name=name, kind="plank", amp=0.05)
    if bk is not None:
        P.paint(a, p.bands[bk] + p.caps[bk], mix(TIMBER, TIMBER_DEEP, 0.25))
    P.texture(a, p.vs, 0.025, P.seed(name), scale=0.5)
    return p


def wall_long(a, s, window=True):
    """A long wall (s = -1: -X, +1: +X): five rows between the corner posts' inner faces, staggered butt joints,
    rows 2-3 cut by the window opening."""
    tag = "L" if s < 0 else "R"
    yc = WIN_Y[s]
    for i in range(N_ROWS):
        z0, z1 = row_z(i)
        cut = (yc - WIN[0], yc + WIN[0]) if window and i in (2, 3) else None
        joints = [j for j in LONG_JOINTS[s].get(i, []) if not (cut and cut[0] - 0.3 < j < cut[1] + 0.3)]
        for k, (t0, t1) in enumerate(segs(-7.10, 7.10, joints, cut)):
            plank(a, "long", s, t0, t1, z0, z1, f"pl_{tag}{i}_{k}")


def wall_end(a, s, door=False):
    """An end wall (s = -1: front, +1: back): five rows between the posts; at the front the rows stop at the jambs."""
    tag = "F" if s < 0 else "B"
    for i in range(N_ROWS):
        z0, z1 = row_z(i)
        sp = segs(-6.10, 6.10, END_JOINTS[s].get(i, []), (-DOOR_X, DOOR_X) if door else None)
        for k, (t0, t1) in enumerate(sp):
            plank(a, "end", s, t0, t1, z0, z1, f"pl_{tag}{i}_{k}")


def window(a, s):
    """The barred window: a chunky light board frame (head, sill 0.25 past the jambs, two jambs) 0.20 proud on the
    outer face, two iron bars in the opening, a closed dark inner shutter."""
    tag = "L" if s < 0 else "R"
    yc = WIN_Y[s]
    hw, zb, ztp, bw, pr = WIN
    xo = WALL_IN_X + WALL_T + 0.003
    key = mix(TIMBER, TIMBER_END, 0.30)

    def board(y0, y1, z0, z1, out, nm):
        p = bx(a, (s * xo, yc + y0, z0), (s * (xo + out), yc + y1, z1), key, f"win_{tag}_{nm}", "frame")
        P.texture(a, p.vs, 0.03, P.seed(nm + tag), scale=0.5)
    board(-hw - bw, hw + bw, ztp + 0.003, ztp + bw, pr, "head")
    board(-hw - bw - 0.25, hw + bw + 0.25, zb - bw, zb - 0.003, pr + 0.10, "sill")
    for e in (-1, 1):
        y0, y1 = sorted((e * hw, e * (hw + bw)))
        board(y0, y1, zb, ztp, pr, f"jamb{e:+d}")
    xc = s * (WALL_IN_X + 0.20)
    for e in (-1, 1):
        bx(a, (xc - 0.11, yc + e * 0.50 - 0.11, row_z(1)[1] + 0.002), (xc + 0.11, yc + e * 0.50 + 0.11,
                                                                       row_z(4)[0] - 0.002),
           IRON, f"win_{tag}_bar{e:+d}", "bar", amp=0.03)
    shutter(a, s)


SHUT = (0.20, 0.12, 0.14, 0.01)


def shutter(a, s):
    """A closed inner shutter of two dark board leaves against the planks' inner face, 0.20 past the opening all
    round (the window reads dark; square-on views do not see through the hut)."""
    tag = "L" if s < 0 else "R"
    yc = WIN_Y[s]
    hw, zb, ztp = WIN[0], WIN[1], WIN[2]
    m, t_side, t_mid, back = SHUT
    xo = WALL_IN_X - 0.003
    y0, y1 = yc - hw - m, yc + hw + m
    w = (y1 - y0) / 2
    key = mix(TIMBER_DEEP, SOOT, 0.55)
    for i in range(2):
        ya, yb = y0 + i * w - (OVL if i else 0.0), y0 + (i + 1) * w + (OVL if i < 1 else 0.0)
        xa, xb = (xo - back - t_mid, xo - back) if i == 1 else (xo - t_side, xo)
        p = bx(a, (s * xa, ya, zb - m), (s * xb, yb, ztp + m), key, f"shutter_{tag}{i}", "board", amp=0.05)
        P.texture(a, p.vs, 0.03, P.seed(f"shutter_{tag}{i}"), scale=0.5)


def post(a, x0, x1, y0, y1, z0, z1, name, ch=0.06, foot=0.40):
    """A chamfered square post: a weathered foot band (toward timber_deep) and a pale golden top."""
    p = P.post(a, ((x0 + x1) / 2, (y0 + y1) / 2), z0, z1, (x1 - x0) / 2, TIMBER, ch=ch, half_y=(y1 - y0) / 2,
               zs=(z0 + foot,), band_keys=[mix(TIMBER, TIMBER_DEEP, 0.25), TIMBER], top_key=TIMBER_END, name=name,
               kind="post", amp=0.05)
    P.texture(a, p.vs, 0.03, P.seed(name), scale=0.45)
    return p


def corner_post(a, sx, sy):
    x0, x1, y0, y1 = POST
    tag = f"{'L' if sx < 0 else 'R'}{'F' if sy < 0 else 'B'}"
    xs, ys = sorted((sx * x0, sx * x1)), sorted((sy * y0, sy * y1))
    post(a, xs[0], xs[1], ys[0], ys[1], CORNER[4] - OVL, PLATE[2] + OVL, f"post_{tag}")


# ---- roof frame -------------------------------------------------------------------------------------------------------------
def plate(a, s, y_end=None):
    """An eave beam (0.90 x 0.80, chamfered 0.12: octagonal pale end faces, close-up A) along Y over the long wall,
    projecting past both gables."""
    x0, x1, z0, z1, ye, ch = PLATE
    ye = y_end or ye
    tag = "L" if s < 0 else "R"
    p = P.ext(a, oct_rect(x0, x1, z0, z1, ch), -ye, ye, TIMBER, to3=xz(s), cap_key=TIMBER_END, name=f"plate_{tag}",
              kind="beam", amp=0.04)
    P.texture(a, p.vs, 0.03, P.seed(f"plate{tag}"), scale=0.4)


def bracket_plate(a, sx, e):
    """Close-up A: a dark iron plate with two rivets on the eave beam's outer face 0.7 in from its end, a golden peg."""
    tag = f"{'L' if sx < 0 else 'R'}{'F' if e < 0 else 'B'}"
    yc = e * (PLATE[4] - 0.70)
    x0 = PLATE[1] + 0.005
    bx(a, (sx * x0, yc - 0.42, 10.53), (sx * (x0 + 0.08), yc + 0.42, 11.07), IRON, f"bplate_{tag}", "iron", amp=0.03)
    bx(a, (sx * (x0 + 0.085), yc - 0.18, 10.62), (sx * (x0 + 0.44), yc + 0.18, 10.98), TIMBER_END, f"bpeg_{tag}", "peg")
    for k, dy in enumerate((-0.31, 0.31)):
        bx(a, (sx * (x0 + 0.085), yc + dy - 0.06, 10.74), (sx * (x0 + 0.19), yc + dy + 0.06, 10.86), IRON,
           f"rivet_{tag}{k}", "iron", amp=0.03)


def rafter(a, sx, y):
    """A rafter (0.50 x 0.60) from the ridge beam's side onto the eave beam (seat cut), its top 0.015 under the
    canvas; the tail stops at the eave blocking."""
    top = lambda x: zu(x) - SINK_TOP          # noqa: E731
    rv = RAFTER_D / COS
    seat = PLATE[3] + 0.003
    xs = (zu(0.0) - SINK_TOP - rv - seat) / PT
    xe = EAVE_BLK[0] - OVL
    x0 = RIDGE_W / 2 + 0.005
    poly = [(x0, top(x0)), (xe, top(xe)), (xe, seat), (xs, seat), (x0, top(x0) - rv)]
    nm = f"rafter_{'L' if sx < 0 else 'R'}{y:+.2f}"
    p = P.ext(a, poly, y - RAFTER_W / 2, y + RAFTER_W / 2, TIMBER, to3=xz(sx), name=nm, kind="beam", amp=0.05)
    P.texture(a, p.vs, 0.03, P.seed(nm), scale=0.4)


GB_IN, GB_OUT = WALL_IN_Y + 0.01, WALL_IN_Y + WALL_T - 0.01     # gable boards' |y| faces
PURLIN_SEGS = ((-CAN_Y + 0.006, -GB_OUT - 0.012), (-GB_IN + 0.012, -4.152), (-3.648, -0.252), (0.252, 3.648),
               (4.152, GB_IN - 0.012), (GB_OUT + 0.012, CAN_Y - 0.006))


def purlins(a, sx):
    """The mid-slope purlin in segments between the rafters and the gable boards, flush under the canvas."""
    x0, x1 = PURLIN_X - PURLIN_W / 2, PURLIN_X + PURLIN_W / 2
    top = lambda x: zu(x) - SINK_TOP          # noqa: E731
    poly = [(x0, top(x0) - PURLIN_H), (x1, top(x1) - PURLIN_H), (x1, top(x1)), (x0, top(x0))]
    for i, (y0, y1) in enumerate(PURLIN_SEGS):
        P.ext(a, poly, y0, y1, TIMBER, to3=xz(sx), name=f"purlin_{'L' if sx < 0 else 'R'}{i}", kind="beam", amp=0.05)


def eave_block(a, s):
    """Eave blocking on the eave beam's top between the gable planes (OVL into beam and canvas): closes the slit
    between beam and canvas."""
    x0, x1 = EAVE_BLK
    zb = PLATE[3] - OVL
    poly = [(x0, zb), (x1, zb), (x1, zu(x1) + OVL), (x0, zu(x0) + OVL)]
    yy = WALL_IN_Y + WALL_T - 0.015
    P.ext(a, poly, -yy, yy, TIMBER, to3=xz(s), name=f"eaveblk_{'L' if s < 0 else 'R'}", kind="beam", amp=0.04)


def trimmers(a):
    """Two short timbers between the rafters at y -3.9 and 0 under the chimney's long edges (its sloped foot sits on
    them)."""
    cx, cy = CHIMNEY
    h = CH_W / 2
    rv = RAFTER_D / COS
    top = lambda x: zu(x) - SINK_TOP          # noqa: E731
    for i, (x0, x1) in enumerate(((cx - h, cx - h + RAFTER_W), (cx + h - RAFTER_W, cx + h))):
        poly = [(x0, top(x0) - rv), (x1, top(x1) - rv), (x1, top(x1)), (x0, top(x0))]
        P.ext(a, poly, RAFTER_Y[0] + RAFTER_W / 2 + 0.002, RAFTER_Y[1] - RAFTER_W / 2 - 0.002, TIMBER, to3=xz(1),
              name=f"trimmer_{i}", kind="beam", amp=0.05)


# canvas grid (x across each slope, y along the ridge): panel centres sag (the sheet's taut panels with soft X creases)
CXI = (0.001, 2.05, 4.10, 5.775, 6.85, EAVE)
CYS = (-CAN_Y, -7.80, -5.85, -3.90, -1.95, 0.0, 1.95, 3.90, 5.85, 7.80, CAN_Y)
SAG = 0.06
SAG_XI = (2.05, 5.775)
SAG_Y = (-5.85, -1.95, 1.95, 5.85)
HEM = ((6.85, 0.5), (5.775, 0.25))


def ridge_section():
    """The ridge beam's 7-sided section (x, z): chamfered bottom corners, the top following both slopes 0.01 under
    the canvas (and under the first panel column's sag at its edges)."""
    h = RIDGE_W / 2
    ztop = lambda x: zu(x) - 0.01 - SAG * abs(x) / CXI[1] - 0.005 * (abs(x) > 0)     # noqa: E731
    ch = 0.10
    return [(-h + ch, RIDGE_Z0), (h - ch, RIDGE_Z0), (h, RIDGE_Z0 + ch), (h, ztop(h)), (0.0, ztop(0.0)),
            (-h, ztop(h)), (-h, RIDGE_Z0 + ch)]


RT_RB, RIDGE_BANDS = 0.10, (10.36, 10.58)


def ridge_beam(a):
    """The ridge beam (1.00 wide) under the canvas apex, its pale ends 0.60 past the bargeboards (the sheet's square
    block under the crossing), two golden rope turns round each end."""
    sec = ridge_section()
    p = P.ext(a, sec, -RIDGE_END, RIDGE_END, TIMBER, to3=xz(1), cap_key=TIMBER_END, name="ridge", kind="beam",
              amp=0.04)
    P.texture(a, p.vs, 0.03, 6810, scale=0.4)
    for e in (-1, 1):
        for k, yb in enumerate(RIDGE_BANDS):
            y = e * yb
            pts = [Vector((u, y, v)) for u, v in sec]
            c = Vector((0.0, y, (RIDGE_Z0 + zu(0.0)) / 2))
            path = P.hull_loop(pts, c, Vector((0, 1, 0)), Vector((1, 0, 0)), RT_RB - 0.02, 8)
            P.rope(a, path, RT_RB, ROPE, ROPE_DEEP, sides=4, closed=True, up=Vector((0, 1, 0)),
                   name=f"ridgeband_{'F' if e < 0 else 'B'}{k}")


# ---- gable frames --------------------------------------------------------------------------------------------------------------
BB_FOOT, BB_TIP, BB_HEEL = 8.20, 1.60, (6.40, 7.20)
DV = BB_D / COS
CLEAT = (0.40, 0.30, 1.40, 0.36)      # along the board, thick, across, position (fraction from the foot)


def _bb_bottom(sx, x, lift=0.0):
    return RIDGE_Z - CTV - sx * PT * x + lift


def _isect(sa, la, sb, lb):
    x = (lb - la) / ((sb - sa) * PT) if sa != sb else 0.0
    return x, RIDGE_Z - CTV - sa * PT * x + la


def bargeboards(a, e):
    """The gable's crossed bargeboards (0.90 x 0.92, 0.80 proud of the canvas) in one plane like a half-lap X: board A
    (foot on -X) whole, board B in two pieces butting A's faces; heels on the eave beams; tips 1.60 out; a golden
    saddle in the V between the tips; one cleat across each board."""
    g = 0.003
    tag = "F" if e < 0 else "B"
    y0, y1 = sorted((e * BB_Y[0], e * BB_Y[1]))
    n = lambda sx: Vector((sx * SIN, COS))      # noqa: E731
    pieces = {}
    for sx in (-1, 1):
        bf = Vector((sx * BB_FOOT, _bb_bottom(sx, sx * BB_FOOT)))
        tf = bf + n(sx) * BB_D
        h0, h1 = BB_HEEL
        heel = [(sx * h1, _bb_bottom(sx, sx * h1)), (sx * h1, PLATE[3] + g), (sx * h0, PLATE[3] + g),
                (sx * h0, _bb_bottom(sx, sx * h0))]
        if sx < 0:
            bt = Vector((-sx * BB_TIP, _bb_bottom(sx, -sx * BB_TIP)))
            tt = bt + n(sx) * BB_D
            poly = [tuple(bf)] + heel + [tuple(bt), tuple(tt), tuple(tf)]
            pieces["A"] = (poly, [len(poly) - 1, 5])
        else:
            xi0, zi0 = _isect(1, 0.0, -1, -g)
            xi1, zi1 = _isect(1, DV, -1, -g)
            poly = [tuple(bf)] + heel + [(xi0, zi0), (xi1, zi1), tuple(tf)]
            pieces["B"] = (poly, [len(poly) - 1])
            xt0, zt0 = _isect(1, DV, -1, DV + g)
            xt1, zt1 = _isect(1, 0.0, -1, DV + g)
            bt = Vector((-sx * BB_TIP, _bb_bottom(sx, -sx * BB_TIP)))
            tt = bt + n(sx) * BB_D
            pieces["Bt"] = ([(xt0, zt0), (xt1, zt1), tuple(bt), tuple(tt)], [2])
    for k, (poly, ends) in pieces.items():
        nm = f"bb_{tag}_{k}"
        sk = [TIMBER_END if i in ends else None for i in range(len(poly))]
        p = P.ext(a, poly, y0, y1, TIMBER, to3=xz(1), side_keys=sk, name=nm, kind="board", amp=0.05)
        P.texture(a, p.vs, 0.03, P.seed(nm), scale=0.4)
    ztopA = lambda x: _bb_bottom(-1, x) + DV    # noqa: E731
    sw, stop = 0.35, 17.42
    poly = [(0.0, ztopA(0.0) + g), (sw, ztopA(sw) + g), (sw, stop), (-sw, stop), (-sw, ztopA(sw) + g)]
    P.ext(a, poly, y0 + 0.02, y1 - 0.02, ROPE, to3=xz(1), name=f"saddle_{tag}", kind="board", amp=0.03)
    cleats(a, e)


def cleats(a, e):
    """One cleat across each bargeboard's top face (OVL into it), overhanging both faces by 0.25 (the sheet's block
    near the eave end)."""
    tag = "F" if e < 0 else "B"
    L, T, Wc, f = CLEAT
    yc = e * (BB_Y[0] + BB_Y[1]) / 2
    key = mix(TIMBER, TIMBER_END, 0.25)
    for sx in (-1, 1):
        t = Vector((COS, 0.0, -sx * SIN))
        nv = Vector((sx * SIN, 0.0, COS))
        xc = sx * BB_FOOT * (1.0 - f)
        c = Vector((xc, yc, _bb_bottom(sx, xc) + DV))
        m = Matrix(((t.x, 0.0, nv.x, c.x), (0.0, 1.0, 0.0, c.y), (t.z, 0.0, nv.z, c.z), (0.0, 0.0, 0.0, 1.0)))
        nm = f"cleat_{tag}{'L' if sx < 0 else 'R'}"
        p = P.box(a, (-L / 2, -Wc / 2, -OVL), (L / 2, Wc / 2, T), key, m=m, name=nm, kind="board", amp=0.04)
        P.texture(a, p.vs, 0.03, P.seed(nm), scale=0.4)


def collar(a, e):
    """Front: the collar at eave level in front of the gable over the lintel; back: on the back wall's outer face
    over the two frame posts."""
    if e < 0:
        P.box(a, (-PLATE[0] + 0.003, DPOST[2], PLATE[2]), (PLATE[0] - 0.003, -8.40, PLATE[3] - 0.003), TIMBER,
              name="collar_F", kind="beam", amp=0.04)
    else:
        y0 = WALL_IN_Y + WALL_T + 0.003
        P.box(a, (-PLATE[0] + 0.003, y0, PLATE[2]), (PLATE[0] - 0.003, y0 + 0.80, PLATE[3] - 0.003), TIMBER,
              name="collar_B", kind="beam", amp=0.04)


def back_frame_posts(a):
    """Two frame posts (1.10 x 0.50) on the back wall's outer face (the r34's rear frame)."""
    y0 = WALL_IN_Y + WALL_T + 0.003
    for sx in (-1, 1):
        bx(a, (sx * 1.80, y0, ROW_Z0 + 0.003), (sx * 2.90, y0 + 0.50, PLATE[2] - 0.003), TIMBER,
           f"framepost_{'L' if sx < 0 else 'R'}", "post", amp=0.05)


def gable_infill(a, e):
    """Vertical boards in the end-wall plane above the top plank row, closed edge to edge (every other board 0.01
    thinner on both faces), tops OVL into the canvas underside, a board under the ridge beam and an apex block over
    it; the outer boards wrap the eave beam's inner chamfers and run onto the eave blocking."""
    tag = "F" if e < 0 else "B"
    zb = row_z(4)[1] - 2 * OVL
    h = RIDGE_W / 2
    to3 = xz(1)

    def ys(odd):
        d = 0.01 if odd else 0.0
        return sorted((e * (GB_IN + d), e * (GB_OUT - d)))

    def put(poly, odd, nm, faces=None):
        y0, y1 = ys(odd)
        if faces is None:
            p = P.ext(a, poly, y0, y1, TIMBER, to3=to3, name=nm, kind="plank", amp=0.05)
        else:
            m = len(poly)
            pts = [to3(u, v, y0) for u, v in poly] + [to3(u, v, y1) for u, v in poly]
            fl = [list(f) for f in faces] + [[m + f[2], m + f[1], m + f[0]] for f in faces]
            fl += [[i, (i + 1) % m, m + (i + 1) % m, m + i] for i in range(m)]
            p = P.shell(a, pts, fl, TIMBER, name=nm, kind="plank", amp=0.05)
        P.texture(a, p.vs, 0.03, P.seed(nm), scale=0.5)
    rb, ch = RIDGE_Z0 + OVL, 0.10
    zr = lambda x: RIDGE_Z0 + max(0.0, abs(x) - (h - ch)) + OVL      # noqa: E731
    put([(-h - OVL, zb), (h + OVL, zb), (h + OVL, zr(h) + OVL), (h - ch - 0.001, rb), (-h + ch + 0.001, rb),
         (-h - OVL, zr(h) + OVL)], False, f"gboard_{tag}_mid")
    sec = ridge_section()
    zt_h, zt_0 = sec[3][1], sec[4][1]
    hb = h + OVL
    poly = [(-hb, zt_h - OVL), (0.0, zt_0 - OVL), (hb, zt_h - OVL), (hb, zu(hb) + OVL), (0.0, zu(0.0) + 0.05),
            (-hb, zu(hb) + OVL)]
    put(poly, False, f"gboard_{tag}_apex", faces=[(0, 1, 5), (1, 4, 5), (1, 2, 3), (1, 3, 4)])
    W = (PLATE[0] - h) / 6
    x0p, z0p, z1p, pch = PLATE[0], PLATE[2], PLATE[3], PLATE[5]
    for sx in (-1, 1):
        for k in range(6):
            xa, xb = h + k * W - OVL, h + (k + 1) * W + OVL
            if k < 5:
                poly = [(xa, zb), (xb, zb), (xb, zu(xb) + OVL), (xa, zu(xa) + OVL)]
            else:
                lb = x0p + z0p + pch + 0.003
                lt = z1p - pch - x0p - 0.003
                xf = EAVE_BLK[0] + OVL
                poly = [(xa, zb), (lb - zb, zb), (x0p + OVL, lb - x0p - OVL), (x0p + OVL, lt + x0p + OVL),
                        (z1p - OVL - lt, z1p - OVL), (xf, z1p - OVL), (xf, zu(xf) + OVL), (xa, zu(xa) + OVL)]
            if sx < 0:
                poly = [(-u, v) for u, v in reversed(poly)]
            put(poly, k % 2 == 0, f"gboard_{tag}{'L' if sx < 0 else 'R'}{k}")


def gable_frame(a, e, part=False):
    """GableFrame: the collar, the crossed bargeboards, saddle and cleats; the part carries the two eave-beam ends the
    boards sit on."""
    collar(a, e)
    bargeboards(a, e)
    if part:
        for s in (-1, 1):
            x0, x1, z0, z1, ye, ch = PLATE
            ya, yb = sorted((e * 8.40, e * ye))
            P.ext(a, oct_rect(x0, x1, z0, z1, ch), ya, yb, TIMBER, to3=xz(s), cap_key=TIMBER_END,
                  name=f"plate_end_{s:+d}", kind="beam", tint=0.98)


# ---- door frame and leaf --------------------------------------------------------------------------------------------------
LEAF = (3.56, 2.62, 9.58)
HINGE = (-DOOR_X, -WALL_IN_Y + 0.01)
OPEN_DEG = 95.0


def door_leaf(a, theta_deg):
    """The plank door: four vertical planks, two inner battens, two iron strap hinges, an iron ring handle; hinged on
    the left jamb's inner line; theta 0 closed, 95 open inward. One step toward timber_deep (the sheet's darker leaf)."""
    R = Matrix.Translation((HINGE[0], HINGE[1], 0.0)) @ Matrix.Rotation(math.radians(theta_deg), 4, "Z")
    W, z0, z1 = LEAF
    deep = mix(TIMBER, TIMBER_DEEP, 0.35)
    pw = (W - 3 * 0.04) / 4
    for i in range(4):
        u0 = i * (pw + 0.04) + 0.003
        p = P.box(a, (u0, 0.003, z0), (u0 + pw, 0.203, z1), deep, m=R, name=f"leaf_plank{i}", kind="door", amp=0.05)
        P.texture(a, p.vs, 0.03, P.seed(f"leaf{i}"), scale=0.5)
    for i, zc in enumerate((3.90, 8.10)):
        P.box(a, (0.18, 0.206, zc - 0.30), (W - 0.18, 0.306, zc + 0.30), deep, m=R, name=f"leaf_batten{i}", kind="door")
        P.box(a, (0.05, -0.057, zc - 0.15), (1.85, 0.0, zc + 0.15), IRON, m=R, name=f"leaf_hinge{i}", kind="iron",
              amp=0.03)
    uc, zc = W - 0.50, 6.00
    P.box(a, (uc - 0.14, -0.043, zc - 0.14), (uc + 0.14, 0.0, zc + 0.14), IRON, m=R, name="leaf_ringplate", kind="iron",
          tint=0.95)
    ring = [R @ Vector((uc + math.cos(2 * math.pi * k / 6) * 0.26, -0.043 - 0.05,
                        zc - 0.20 + math.sin(2 * math.pi * k / 6) * 0.26)) for k in range(6)]
    P.tube(a, ring, 0.05, 3, True, IRON, up=tuple(R.to_3x3() @ Vector((0, 1, 0))), twist=True, name="leaf_ring",
           kind="iron", tint=0.92)
    P.GEO["hinge"] = {"axis_bottom": [HINGE[0], HINGE[1], z0], "closed_yaw": 0.0, "open_yaw": OPEN_DEG}


def doorframe(a, theta_deg=OPEN_DEG):
    """DoorFrame: two door posts on golden foot caps, the lintel (pale ends 0.40 past the posts), the header plank
    over the opening and the leaf."""
    x0, x1, y0, y1 = DPOST
    for sx in (-1, 1):
        tag = "L" if sx < 0 else "R"
        xa, xb = sorted((sx * x0, sx * x1))
        bx(a, (xa - 0.03, y0 - 0.03, 0.0), (xb + 0.03, y1 - 0.005, 0.40), ROPE, f"dcap_{tag}", "peg", amp=0.03)
        post(a, xa, xb, y0, y1, 0.403, DOOR_TOP - 0.003, f"dpost_{tag}")
    p = P.box(a, (-3.30, y0, DOOR_TOP), (3.30, -WALL_IN_Y - WALL_T - 0.005, PLATE[2] - 0.003), TIMBER, name="lintel",
              kind="beam", amp=0.04)
    P.paint(a, [p.fs[1], p.fs[3]], TIMBER_END)
    plank(a, "end", -1, -DOOR_X - OVL, DOOR_X + OVL, DOOR_TOP + 0.003, row_z(4)[1], "header", band=False)
    door_leaf(a, theta_deg)


# ---- canvas, seams, ties ----------------------------------------------------------------------------------------------------
def roof_panel(a, s, hole=False):
    """One closed canvas slab (0.12 thick) over one slope: 4 panels along Y (rafter lines) x 2 down the slope (the
    purlin line), each sagging at its centre; from the apex (0.001 off the ridge line) to the eave 0.25 past the
    eave beam. hole: cut round the chimney (OVL clear; a flashing collar covers it). Hem bands toward canvas_deep along
    the eave and round the cut (by position)."""
    tag = "L" if s < 0 else "R"
    nx, ny = len(CXI), len(CYS)

    def sag(i, j):
        return SAG if (CXI[i] in SAG_XI and CYS[j] in SAG_Y) else 0.0
    top = {(i, j): Vector((s * CXI[i], CYS[j], zt(CXI[i]) - sag(i, j))) for i in range(nx) for j in range(ny)}
    j0 = CYS.index(-3.90)
    hole_q = {(i, j) for i in (0, 1) for j in (j0, j0 + 1)} if hole else set()
    keys_t = list(top.keys())
    pts = [top[k] for k in keys_t]
    idx = {k: n for n, k in enumerate(keys_t)}
    inner = []
    if hole:
        x0, x1, y0, y1 = HOLE
        for xx, yy in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            inner.append(len(pts))
            pts.append(Vector((s * xx, yy, zt(xx))))
    nt = len(pts)
    pts += [p - Vector((0, 0, CTV)) for p in pts]
    tris, tkeys = [], []

    def hem_key(xc):
        for lim, t in HEM:
            if xc > lim:
                return mix(CANVAS, CANVAS_DEEP, t)
        return CANVAS
    for i in range(nx - 1):
        for j in range(ny - 1):
            if (i, j) in hole_q:
                continue
            q = [idx[(i, j)], idx[(i + 1, j)], idx[(i + 1, j + 1)], idx[(i, j + 1)]]
            sg = [sag(*k) for k in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))]
            k0 = next((k for k in range(4) if sg[k] > 0), 0)
            q = q[k0:] + q[:k0]
            key = hem_key((CXI[i] + CXI[i + 1]) / 2)
            tris += [(q[0], q[1], q[2]), (q[0], q[2], q[3])]
            tkeys += [key, key]
    if hole:
        O = [idx[(0, j0)], idx[(1, j0)], idx[(2, j0)], idx[(2, j0 + 1)], idx[(2, j0 + 2)], idx[(1, j0 + 2)],
             idx[(0, j0 + 2)], idx[(0, j0 + 1)]]
        I_ = inner
        ring = [(O[0], O[1], I_[0]), (O[1], I_[1], I_[0]), (O[1], O[2], I_[1]), (O[2], O[3], I_[1]), (O[3], I_[2], I_[1]),
                (O[3], O[4], I_[2]), (O[4], O[5], I_[2]), (O[5], I_[3], I_[2]), (O[5], O[6], I_[3]), (O[6], O[7], I_[3]),
                (O[7], I_[0], I_[3]), (O[7], O[0], I_[0])]
        tris += ring
        tkeys += [mix(CANVAS, CANVAS_DEEP, 0.5)] * len(ring)
    faces = [list(t) for t in tris] + [[nt + t[2], nt + t[1], nt + t[0]] for t in tris]
    keys = tkeys + tkeys
    if hole:
        used = {i for t in tris for i in t}
        loop_pts = ({idx[(i, 0)] for i in range(nx)} | {idx[(nx - 1, j)] for j in range(ny)} |
                    {idx[(i, ny - 1)] for i in range(nx)} | {idx[(0, j)] for j in range(ny)})
        drop = sorted(set(range(nt)) - used - loop_pts)
        if drop:
            keep = [i for i in range(nt) if i not in drop]
            remap = {old: new for new, old in enumerate(keep)}
            remap.update({nt + old: len(keep) + new for new, old in enumerate(keep)})
            pts = [pts[i] for i in keep] + [pts[nt + i] for i in keep]
            faces = [[remap[i] for i in f] for f in faces]
            idx = {k: remap[v] for k, v in idx.items() if v in remap}
            inner = [remap[i] for i in inner]
            nt = len(keep)
    loop = ([idx[(i, 0)] for i in range(nx)] + [idx[(nx - 1, j)] for j in range(1, ny)] +
            [idx[(i, ny - 1)] for i in range(nx - 2, -1, -1)] + [idx[(0, j)] for j in range(ny - 2, 0, -1)])
    rims = [(loop[k], loop[(k + 1) % len(loop)]) for k in range(len(loop))]
    if hole:
        rims += [(inner[k], inner[(k + 1) % 4]) for k in range(4)]
    for u, v in rims:
        faces.append([u, v, nt + v, nt + u])
        xc = abs((pts[u].x + pts[v].x) / 2)
        keys.append(mix(CANVAS, CANVAS_DEEP, 0.75) if (xc > EAVE - 0.01 or (hole and u in inner)) else hem_key(xc))
    p = P.shell(a, pts, faces, CANVAS, keys=[k if k != CANVAS else None for k in keys], name=f"canvas_{tag}",
                kind="canvas", amp=0.02)
    P.texture(a, p.vs, 0.03, P.seed(f"canvas{tag}"), scale=0.22)
    return p


SEAM = (0.12, 0.010, 0.025)          # seam strip width, depth into the canvas top, height above it
SEAM_Y = RAFTER_Y                     # along-slope seams over the rafter lines; the cross seam over the purlin


def seams(a, s):
    """The sheet's panel grid: raised seam strips on the canvas top, three down the slope (ridge to eave) over the
    rafter lines and one across over the purlin line in four pieces butting them. Each sits SEAM[1] into the
    canvas top (inside the 0.12 slab), a darker canvas tone (by role)."""
    tag = "L" if s < 0 else "R"
    w, dn, upz = SEAM
    key = mix(CANVAS, CANVAS_DEEP, 0.70)
    x0, x1 = 0.004, EAVE - 0.04
    poly = [(x0, zt(x0) - dn), (x1, zt(x1) - dn), (x1, zt(x1) + upz), (x0, zt(x0) + upz)]
    for k, y in enumerate(SEAM_Y):
        P.ext(a, poly, y - w / 2, y + w / 2, key, to3=xz(s), name=f"seam_{tag}{k}", kind="seam", amp=0.02)
    xa, xb = PURLIN_X - w / 2, PURLIN_X + w / 2
    poly = [(xa, zt(xa) - dn), (xb, zt(xb) - dn), (xb, zt(xb) + upz), (xa, zt(xa) + upz)]
    edges = [-CAN_Y + 0.10] + [v for y in SEAM_Y for v in (y - w / 2 - 0.003, y + w / 2 + 0.003)] + [CAN_Y - 0.10]
    for k in range(0, len(edges), 2):
        P.ext(a, poly, edges[k], edges[k + 1], key, to3=xz(s), name=f"seamx_{tag}{k // 2}", kind="seam", amp=0.02)


TIE_W, TIE_T, TIE_G = 0.24, 0.08, 0.005
TIE_Y = (-5.85, -1.95, 1.95, 5.85)    # four ties per eave, at the panel centres (side, top and f34 cells)


def _offset_dirs(prof):
    """Mitred offset directions (to the left) of an open 2D polyline."""
    out = []
    n = len(prof)
    for i in range(n):
        dirs = []
        if i > 0:
            dirs.append(Vector((prof[i][0] - prof[i - 1][0], prof[i][1] - prof[i - 1][1])).normalized())
        if i < n - 1:
            dirs.append(Vector((prof[i + 1][0] - prof[i][0], prof[i + 1][1] - prof[i][1])).normalized())
        nrm = [Vector((-t.y, t.x)) for t in dirs]
        if len(nrm) == 1:
            out.append(nrm[0])
        else:
            bis = (nrm[0] + nrm[1]).normalized()
            out.append(bis / max(bis.dot(nrm[0]), 0.3))
    return out


def tie(a, s, y, name, short=False):
    """A golden U tie: a flat strap over the canvas top near the eave, round the canvas edge, across to the eave beam
    and down its outer face to the wall (both ends touch). short (the RoofPanel part): a clip round the canvas edge."""
    x0, x1, z0, z1, _, ch = PLATE
    if short:
        prof = [(6.85, zt(6.85)), (EAVE, zt(EAVE)), (EAVE, zt(EAVE) - CTV), (6.85, zt(6.85) - CTV)]
    else:
        prof = [(6.85, zt(6.85)), (EAVE, zt(EAVE)), (EAVE, zt(EAVE) - CTV), (x1, z1 - ch), (x1, z0 + ch),
                (x1 - ch, z0), (WALL_IN_X + WALL_T + 0.03, z0)]
    mv = _offset_dirs(prof)
    rings, cl = [], []
    for (u, v), m in zip(prof, mv):
        p = Vector((u, v))
        q0, q1 = p + m * TIE_G, p + m * (TIE_G + TIE_T)
        cl.append(p + m * (TIE_G + TIE_T / 2))
        rings.append([Vector((s * q0.x, y - TIE_W / 2, q0.y)), Vector((s * q0.x, y + TIE_W / 2, q0.y)),
                      Vector((s * q1.x, y + TIE_W / 2, q1.y)), Vector((s * q1.x, y - TIE_W / 2, q1.y))])
    p = P.prism(a, rings, ROPE, name=name, kind="rope", amp=0.04)
    for b in p.bands:
        P.paint(a, [b[1]], mix(ROPE, ROPE_DEEP, 0.5))
    P.ROPES.append({"name": p.name, "ends": [[s * cl[0].x, y, cl[0].y], [s * cl[-1].x, y, cl[-1].y]],
                    "rt": TIE_G + TIE_T / 2})


def ties(a, s, short=False):
    for i, y in enumerate(TIE_Y):
        tie(a, s, y, f"tie_{'L' if s < 0 else 'R'}{i}", short=short)


# ---- chimney ------------------------------------------------------------------------------------------------------------------
MERLON = 0.85                         # cap merlons (the sheet's crenellated cap): corner squares


def chimney(a):
    """A square stone stack: a lower block whose foot follows the roof pitch on the trimmers, a flashing collar on the
    canvas, an upper block set in 0.10 (the notched joint), a wider pale cap with a dark flue recess and four corner
    merlons (the crenellated top)."""
    cx, cy = CHIMNEY
    h = CH_W / 2
    foot = lambda x: zu(x) - SINK_TOP + 0.003     # noqa: E731
    pts = [Vector((x, y, foot(x))) for x, y in ((cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h))]
    pts += [Vector((p.x, p.y, CH_JOINT)) for p in pts]
    p = P.box_pts(a, pts, mix(STONE_DARK, STONE, 0.25), name="chim_lo", kind="chimney", amp=0.03)
    P.texture(a, p.vs, 0.04, 6820, scale=0.8)
    P.GEO["chimney_foot"] = [round(foot(cx - h), 3), round(foot(cx + h), 3)]
    fw, fh = COLLAR
    ri, ro = h - OVL, h + fw
    sq = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    ring = lambda r, dz: [Vector((cx + x * r, cy + y * r, zt(cx + x * r) + dz)) for x, y in sq]     # noqa: E731
    pts = ring(ro, -OVL) + ring(ri, -OVL) + ring(ro, fh) + ring(ri, fh)
    faces = []
    for k in range(4):
        k1 = (k + 1) % 4
        faces += [[8 + k, 8 + k1, 12 + k1, 12 + k], [k1, k, 4 + k, 4 + k1], [k, k1, 8 + k1, 8 + k],
                  [4 + k1, 4 + k, 12 + k, 12 + k1]]
    P.shell(a, pts, faces, mix(STONE_DARK, SOOT, 0.25), name="chim_collar", kind="chimney", amp=0.03)
    h2 = h - 0.10
    p = P.box(a, (cx - h2, cy - h2, CH_JOINT + 0.003), (cx + h2, cy + h2, CH_Z1), STONE_DARK, name="chim_up",
              kind="chimney", amp=0.03)
    P.texture(a, p.vs, 0.04, 6821, scale=0.8)
    cap = mix(STONE_LIGHT, STONE, 0.4)
    hc, hf, zc0, zf = 1.50, 0.70, CH_Z1 + 0.003, CAP_Z - 0.60
    o0 = [Vector((cx + x * hc, cy + y * hc, zc0)) for x, y in sq]
    o1 = [q + Vector((0, 0, CAP_Z - zc0)) for q in o0]
    i1 = [Vector((cx + x * hf, cy + y * hf, CAP_Z)) for x, y in sq]
    i0 = [q - Vector((0, 0, CAP_Z - zf)) for q in i1]
    faces, keys = [[3, 2, 1, 0]], [None]
    for k in range(4):
        k1 = (k + 1) % 4
        faces += [[k, k1, 4 + k1, 4 + k], [4 + k, 4 + k1, 8 + k1, 8 + k], [8 + k, 8 + k1, 12 + k1, 12 + k]]
        keys += [None, None, SOOT]
    faces.append([12, 13, 14, 15])
    keys.append(SOOT)
    P.shell(a, o0 + o1 + i1 + i0, faces, cap, keys=keys, name="chim_cap", kind="chimney", amp=0.03)
    for k, (sx, sy) in enumerate(sq):
        xa, xb = sorted((cx + sx * hc, cx + sx * (hc - MERLON)))
        ya, yb = sorted((cy + sy * hc, cy + sy * (hc - MERLON)))
        P.box(a, (xa, ya, CAP_Z - OVL), (xb, yb, CH_TOP), cap, name=f"chim_merlon{k}", kind="chimney", amp=0.04)
    P.GEO["flue"] = [cx, cy, zf + 0.05]


FLUE = (CHIMNEY[0], CHIMNEY[1], CAP_Z - 0.55)
SMOKE = {"emitters": [{"name": "Smoke", "texture": "smoke_puff", "color": ["#BDB8B4", "#E4E0DC"], "size": [1.0, 3.5],
                       "transparency": [0.6, 1.0], "lifetime": [3, 5], "rate": 2, "speed": [1.5, 2.5], "spread": 6,
                       "light_emission": 0.0, "acceleration": [0.4, 0.3, 0], "drag": 0.3, "rotation": [0, 360],
                       "rot_speed": [-15, 15]}], "light": None}


# ---- stairs ------------------------------------------------------------------------------------------------------------------
STAIR_X = 2.40
TREADS = ((-11.10, -9.503, 1.73), (-12.70, -11.10, 0.87))       # y0, y1, top


def stairs(a):
    """Two treads of two planks (0.30 thick, 0.04 gap) on two blocks each (the exploded's steps); rises 0.87 / 0.86
    / 0.87 to the threshold."""
    for ti, (y0, y1, ztop) in enumerate(TREADS):
        w = (y1 - y0 - 0.04) / 2
        for k in range(2):
            ya = y0 + k * (w + 0.04)
            nm = f"tread{ti}_{k}"
            p = P.plank(a, (-STAIR_X, ya + w / 2, ztop - 0.15), (STAIR_X, ya + w / 2, ztop - 0.15), w, 0.30,
                        mix(TIMBER, TIMBER_END, 0.30), ch=0.04, name=nm, kind="tread", amp=0.05)
            P.texture(a, p.vs, 0.03, P.seed(nm), scale=0.5)
        for k, sx in enumerate((-1, 1)):
            bx(a, (sx * 1.50, y0 + 0.10, 0.0), (sx * 2.10, y1 - 0.10, ztop - 0.303), mix(TIMBER, TIMBER_DEEP, 0.4),
               f"tblock{ti}_{k}", "tblock", amp=0.05)
    P.GEO["risers"] = [TREADS[1][2], round(TREADS[0][2] - TREADS[1][2], 3), round(FLOOR_Z - TREADS[0][2], 3)]


# ---- lanterns ----------------------------------------------------------------------------------------------------------------
L1 = (-8.30, -6.60, 7.00)                                   # eave lantern base (on a bracket off the -X eave beam)
L23 = ((-4.70, -9.10, 6.20), (4.70, -9.10, 6.20))           # door lanterns
GLASS_DZ = 0.20 + 1.60 / 2                                  # glass centre above the lantern base
HALO = {"emitters": [{"name": "Halo", "texture": "glow_soft", "color": ["#FFC23A", "#FF9A1E"], "size": [1.4, 1.7],
                      "transparency": [0.65, 1.0], "lifetime": [1.0, 1.5], "rate": 2, "speed": [0, 0.05], "spread": 0,
                      "light_emission": 1.0}],
        "light": {"color": "#FFB347", "brightness": 1.0, "range": 12, "flicker": True}}


def lantern_set(a, kind, base, tag):
    """A lantern on its iron bracket. kind "eave": hung from an L bracket on the -X eave beam's outer face (the
    sheet's hanging lantern); "door": on a wall bracket on the front wall."""
    lt = P.lantern(a, base, IRON, GLOW, ring_axis=(0, 1, 0) if kind == "eave" else (1, 0, 0), name=tag)
    rtop = lt["ring_top"].z
    if kind == "eave":
        P.bracket(a, (base[0], base[1]), (-(PLATE[1] + 0.003), base[1]), (-1, 0), 10.75, rtop, IRON, strap=0.30,
                  name=f"{tag}_br")
    else:
        z_arm = 9.75
        P.bracket(a, (base[0], base[1]), (base[0], -(WALL_IN_Y + WALL_T + 0.003)), (0, -1), z_arm, rtop, IRON,
                  strap=PLATE[2] - 0.003 - (z_arm - 0.10), name=f"{tag}_br")
    P.GEO.setdefault("lanterns", {})[tag] = {"bottom": round(base[2], 3), "glass": [round(x, 3) for x in lt["glass"]],
                                              "ring_top": round(rtop, 3)}
    return lt


# ---- banner ------------------------------------------------------------------------------------------------------------------
POLE = (-8.60, 8.40, 115.0)           # pole x, y and the turn of its crossarm (local +X; 115 deg: toward +Y and -X)
POLE_R, POLE_TOP = 0.42, 12.90
ARM_Z, ARM_R = 12.40, 0.18
ARM_PROF = ((-0.85, 0.26), (-0.60, 0.26), (-0.60, ARM_R), (0.55, ARM_R), (0.55, 0.23), (0.75, 0.23), (0.75, ARM_R),
            (2.95, ARM_R), (2.95, 0.23), (3.15, 0.23), (3.15, ARM_R), (3.30, ARM_R), (3.30, 0.26), (3.55, 0.26))
SLEEVE = (0.78, 2.92, 0.30, ARM_R + 0.003)      # x0, x1, outer and inner flat radius
BAN_T, BAN_DROP, RT_X = 0.08, 6.40, 0.10


def banner_set(a):
    """Banner Pole + Banner, built in the pole's frame (pole at the origin, crossarm along local +X): an 8-sided pole
    with a golden foot band and a block top; a 6-sided crossarm through it (two pieces butting the pole's faces,
    knob ends, two iron bands at the cloth's ends); a golden X lashing; a hem sleeve round the arm and the red
    three-point banner with the white diamond emblem on both faces."""
    px, py, rot = POLE
    with P.frame(Matrix.Translation((px, py, 0.0)) @ Matrix.Rotation(math.radians(rot), 4, "Z"), "ban_"):
        ex, ey, ez = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
        prof = ((0.0, POLE_R), (0.40, POLE_R), (0.40, POLE_R + 0.05), (0.70, POLE_R + 0.05), (0.70, POLE_R),
                (POLE_TOP, POLE_R))
        rings = [P.ngon(Vector((0, 0, z)), ex, ey, r, 8, math.pi / 8) for z, r in prof]
        p = P.prism(a, rings, TIMBER, name="pole", kind="pole", amp=0.04)
        P.paint(a, p.bands[1] + p.bands[2] + p.bands[3], ROPE)
        P.texture(a, p.vs, 0.03, 6830, scale=0.4)
        P.box(a, (-0.50, -0.50, POLE_TOP + 0.003), (0.50, 0.50, POLE_TOP + 0.60), TIMBER, name="pole_top", kind="pole")
        pf = POLE_R * math.cos(math.pi / 8) + 0.003
        stub = [q for q in ARM_PROF if q[0] < 0] + [(-pf, ARM_R)]
        arm = [(pf, ARM_R)] + [q for q in ARM_PROF if q[0] > 0]
        rings = [P.ngon(Vector((x, 0, ARM_Z)), ey, ez, r, 6, math.pi / 6) for x, r in stub]
        P.prism(a, rings, TIMBER, cap_keys=(TIMBER_END, None), name="armstub", kind="pole", amp=0.04)
        rings = [P.ngon(Vector((x, 0, ARM_Z)), ey, ez, r, 6, math.pi / 6) for x, r in arm]
        p = P.prism(a, rings, TIMBER, cap_keys=(None, TIMBER_END), name="arm", kind="pole", amp=0.04)
        for k in range(1, len(arm) - 2):        # the two iron bands: the raised rings between the knob ends
            if arm[k][1] > ARM_R + 1e-6 and arm[k + 1][1] > ARM_R + 1e-6 and arm[k][0] < 3.2:
                P.paint(a, p.bands[k - 1] + p.bands[k] + p.bands[k + 1], IRON)
        c = Vector((0, 0, ARM_Z))
        pole_lines = P.ngon(Vector((0, 0, 0)), ex, ey, POLE_R, 8, math.pi / 8)
        arm_lines = P.ngon(Vector((0, 0, ARM_Z)), ey, ez, ARM_R, 6, math.pi / 6)
        for k, (sg, off) in enumerate(((1, RT_X - 0.02), (-1, RT_X - 0.02 + 2 * RT_X - 0.04))):
            m = Vector((sg, 0, 1)).normalized()
            pts = [Vector((q.x, q.y, ARM_Z - sg * q.x)) for q in pole_lines]
            pts += [Vector((-sg * (q.z - ARM_Z), q.y, q.z)) for q in arm_lines]
            path = P.hull_loop(pts, c, m, ey, off, 8)
            P.rope(a, path, RT_X, ROPE, ROPE_DEEP, sides=4, closed=True, up=m, name=f"xlash_{k}")
        x0, x1, ro, ri = SLEEVE
        P.sleeve(a, (x0, 0, ARM_Z), (x1, 0, ARM_Z), ri, ro, mix(BANNER, IRON, 0.15), sides=6, name="sleeve",
                 kind="banner", amp=0.02)
        zt_ = ARM_Z - ro + 0.007
        out = P.banner(a, x0 + 0.02, x1 - 0.02, 0.0, zt_, zt_ - BAN_DROP, zt_ - BAN_DROP + 0.75, BANNER,
                       hem_key=mix(BANNER, IRON, 0.10), t=BAN_T, points=3, name="cloth")
        xc, cz = (x0 + x1) / 2, zt_ - BAN_DROP * 0.42
        for side in (-1, 1):
            P.emblem(a, xc, cz, side * BAN_T / 2, side, WHITE, w=1.20, h=1.90, dots=(0.12, 0.80), name="emblem")
        P.GEO["banner_top"] = list(P.here((0, 0, POLE_TOP + 0.60)))
    return out


# ---- dressing ----------------------------------------------------------------------------------------------------------------
BARRELS = {"A": ((-9.25, 4.20), 10.0), "B": ((9.20, 6.30), 25.0)}
CRATE = ((-9.00, 1.05), 8.0)
CR_PT, CR_PL, CR_PH = 0.04, 0.42, 0.32


def crate(a, c, rot):
    """An X-braced crate with a closed lid and dark iron L plates at its eight corners (the sheet's crate)."""
    P.crate(a, c, TIMBER, TIMBER_DEEP, rot=rot, W=2.30, H=2.20, open_top=False, name="crate")
    Rm = P.R(c, rot)
    h, H, g = 2.30 / 2, 2.20, 0.004
    for ci, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        for zi, (z0, z1) in enumerate(((0.0, CR_PH), (H - CR_PH, H))):
            ox, oy = sx * (h + g), sy * (h + g)
            L2 = [(ox + sx * CR_PT, oy - sy * CR_PL), (ox + sx * CR_PT, oy + sy * CR_PT), (ox - sx * CR_PL, oy + sy * CR_PT),
                  (ox - sx * CR_PL, oy), (ox, oy), (ox, oy - sy * CR_PL)]
            area = sum(L2[i][0] * L2[(i + 1) % 6][1] - L2[(i + 1) % 6][0] * L2[i][1] for i in range(6))
            if area < 0:
                L2 = L2[::-1]
            P.ext(a, L2, z0, z1, IRON, to3=lambda u, v, w: Rm @ Vector((u, v, w)), name=f"crate_plate{ci}{zi}",
                  kind="iron", amp=0.04)


def dressing(a):
    for tag, (c, rot) in BARRELS.items():
        P.barrel(a, c, TIMBER, TIMBER_DEEP, IRON, rot=rot, h=2.72, open_top=False, lid_key=mix(IRON, WHITE, 0.55),
                 name=f"barrel_{tag}")
    crate(a, *CRATE)


# ---- hero ----------------------------------------------------------------------------------------------------------------------
def hero_all(a):
    """TimberCabin: every part function placed by the layout (leaf open inward), one object of closed shells."""
    for side in RUNS:
        foundation_run(a, side)
    for sx in (-1, 1):
        for sy in (-1, 1):
            corner_block(a, sx, sy)
            corner_post(a, sx, sy)
    floor(a)
    for s in (-1, 1):
        wall_long(a, s)
        window(a, s)
        plate(a, s)
        for e in (-1, 1):
            bracket_plate(a, s, e)
        for y in RAFTER_Y:
            rafter(a, s, y)
        purlins(a, s)
        eave_block(a, s)
    wall_end(a, -1, door=True)
    wall_end(a, 1)
    back_frame_posts(a)
    for e in (-1, 1):
        gable_frame(a, e)
        gable_infill(a, e)
    doorframe(a, OPEN_DEG)
    trimmers(a)
    ridge_beam(a)
    roof_panel(a, -1)
    roof_panel(a, 1, hole=True)
    for s in (-1, 1):
        seams(a, s)
        ties(a, s)
    chimney(a)
    stairs(a)
    lantern_set(a, "eave", L1, "L1")
    for tag, base in zip(("L2", "L3"), L23):
        lantern_set(a, "door", base, tag)
    banner_set(a)
    dressing(a)


def roof_part(a):
    """TimberCabinRoofPanel: the +X canvas slab (uncut) with its seams and four U clips (mirror for the other slope)."""
    roof_panel(a, 1)
    seams(a, 1)
    ties(a, 1, short=True)


def chimney_part(a):
    chimney(a)


def lantern_part(a):
    """TimberCabinLantern: one door lantern with its wall bracket (the strap's back face is the wall face)."""
    lantern_set(a, "door", (0.0, -9.10, 6.20), "L")


def wall_part(a):
    """TimberCabinWallPanel: the back wall's five plank rows between its two corner posts."""
    wall_end(a, 1)
    for sx in (-1, 1):
        corner_post(a, sx, 1)


def window_part(a):
    """TimberCabinWindowWall: the +X long wall with its centred window between its two corner posts."""
    wall_long(a, 1)
    window(a, 1)
    for sy in (-1, 1):
        corner_post(a, 1, sy)


def foundation_part(a):
    """TimberCabinFoundation: the +X side's run with its back corner block."""
    foundation_run(a, "R")
    corner_block(a, 1, 1)


PARTS = ((ROOF_P, roof_part), (RIDGE_P, ridge_beam), (CHIMNEY_P, chimney_part), (BANNER_P, banner_set),
         (LANTERN_P, lantern_part), (WALL_P, wall_part), (WINDOW_P, window_part), (DOOR_P, lambda a: doorframe(a, 0.0)),
         (GABLE_P, lambda a: gable_frame(a, -1, part=True)), (FLOOR_P, lambda a: floor(a, feet=True)),
         (STAIRS_P, stairs), (FOUND_P, foundation_part))
NOTES = {
    HERO: "Walk-in gable-roofed timber cabin (remade sheet; door 3.60 x 7.00 clear on a 2.60 floor, rises 0.87 / "
          "0.86 / 0.87): one course of big pale stone blocks with lighter corner blocks, plank floor, five rows of "
          "planks between chamfered corner posts, a barred window with a dark inner shutter in each long wall, the "
          "door between tall posts on golden caps under a lintel and collar (leaf open inward 95 deg), octagonal-ended "
          "eave beams with iron brackets, rafters, purlins and a ridge beam under two closed cream canvas slabs with "
          "a seam grid and golden U ties, crossed bargeboards with golden saddles and cleats, a stone chimney with a "
          "crenellated cap (thin pale chimney_smoke), two-tread stairs, three Neon lanterns (heat_glow), a red banner "
          "on an X-lashed pole, two barrels and a crate. Collision precise: Requires Manual Validation in Studio (walk "
          "in, turn round, walk out).",
    ROOF_P: "Roof Panel (Left / Right): one closed 0.12 canvas slab, 4 x 2 panels with raised seams, four golden U "
            "clips (mirror for the other slope)",
    RIDGE_P: "Ridge Beam: 1.00 beam with a pitched top, pale ends and two golden rope turns at each end",
    CHIMNEY_P: "Chimney: square stone stack in two blocks with a notched joint, a flashing collar and a crenellated "
               "flued cap (chimney_smoke socket); its foot is cut to the 32 deg roof pitch",
    BANNER_P: "Banner Pole + Banner: 8-sided pole with a golden foot band and block top, crossarm through it with an "
              "X lashing and iron bands, red three-point banner with the white diamond emblem on both faces",
    LANTERN_P: "Lantern: square dark-iron lantern with Neon amber glass (heat_glow halo) on its iron wall bracket",
    WALL_P: "Wall Panel (Left / Rear): five rows of 0.40 V-seamed planks with staggered joints between two corner "
            "posts",
    WINDOW_P: "Wall Panel (Right): a long plank wall with the centred barred window, its chunky frame and dark inner "
              "shutter, and its corner posts",
    DOOR_P: "Doorframe: two chamfered door posts on golden caps, lintel, header plank and the plank door (closed; "
            "hinge stored as m068_hinge for a scripted door)",
    GABLE_P: "Front Gable Frame: collar, crossed bargeboards (half-lap X) with a golden saddle and cleats, on the two "
             "eave-beam ends",
    FLOOR_P: "Floor: ten deck planks, the dark underlay and the threshold on short dark feet (top 2.60)",
    STAIRS_P: "Steps: two two-plank treads on blocks (rises 0.87 / 0.86 / 0.87 to a 2.60 floor)",
    FOUND_P: "Stone Foundation (x4): one side's run of four big chamfered blocks with its lighter corner block",
}
COLLISION = {HERO: "precise", ROOF_P: "box", RIDGE_P: "box", CHIMNEY_P: "box", BANNER_P: "none", LANTERN_P: "none",
             WALL_P: "box", WINDOW_P: "precise", DOOR_P: "precise", GABLE_P: "hull", FLOOR_P: "box",
             STAIRS_P: "precise", FOUND_P: "box"}
BUDGETS = {HERO: 8000}
TARGET_SIZE = ((20.6, 0.3), (24.4, 0.3), (CH_TOP, 0.05))

# points (build frame) and sockets; the parts' frames are the hero's build frame (each recentred by its own offset)
POINTS = {HERO: {"m068_centre": (0.0, 0.0, FLOOR_Z), "m068_threshold": ((0.0, -(WALL_IN_Y + WALL_T), FLOOR_Z),
                                                                         (0.0, -1.0, 0.0)),
                 "m068_chimney": FLUE},
          LANTERN_P: {"m068_hang": (0.0, -9.10, 9.40), "m068_mount": (0.0, -(WALL_IN_Y + WALL_T + 0.003), 10.0)},
          CHIMNEY_P: {"m068_flue": FLUE},
          BANNER_P: {"m068_top": (POLE[0], POLE[1], POLE_TOP + 0.60)}}
FX = {HERO: [("heat_glow", (L1[0], L1[1], L1[2] + GLASS_DZ), HALO)] +
      [("heat_glow", (b[0], b[1], b[2] + GLASS_DZ), HALO) for b in L23] + [("chimney_smoke", FLUE, SMOKE)],
      LANTERN_P: [("heat_glow", (0.0, -9.10, 6.20 + GLASS_DZ), HALO)],
      CHIMNEY_P: [("chimney_smoke", FLUE, SMOKE)]}

VIEWS = {"f34_sheet": (-36, 18), "r34_sheet": (35, 18, "mirror"), "front_sheet": (-30, 10), "side_sheet": (90, 3),
         "rear_sheet": (-90, 3, "mirror"), "top_sheet": (0, 89.9)}
EXPLODED = {ROOF_P: (6.0, 0.0, 14.0), RIDGE_P: (0.0, 0.0, 20.0), CHIMNEY_P: (-6.0, 0.0, 16.0),
            BANNER_P: (-20.0, 0.0, 0.0), LANTERN_P: (-26.0, 0.0, 0.0), WALL_P: (-12.0, 0.0, 0.0),
            WINDOW_P: (0.0, 0.0, 0.0), DOOR_P: (12.0, 0.0, 0.0), GABLE_P: (24.0, 0.0, 0.0), FLOOR_P: (36.0, 0.0, 0.0),
            STAIRS_P: (50.0, 0.0, 0.0), FOUND_P: (58.0, 0.0, 0.0)}
CLOSE = {"junction_cu": dict(at=(-7.0, -10.0, 11.0), r=1.6, az=-40, el=12),
         "apex_cu": dict(at=(0.0, -9.7, 16.6), r=2.2, az=-25, el=10),
         "chimney_cu": dict(at=(2.2, -1.95, 17.0), r=3.0, az=-35, el=20),
         "door_cu": dict(at=(0.0, -9.0, 5.5), r=5.0, az=-20, el=12),
         "inside_cu": dict(cam=(4.5, 6.5, 8.0), look=(-2.0, -5.0, 5.0), lens=14.0),
         "underside_cu": dict(cam=(0.0, 4.0, 4.5), look=(1.5, -2.0, 14.0), lens=14.0),
         "base_cu": dict(at=(-7.0, -8.0, 1.6), r=2.2, az=-40, el=15)}

ESCAPE = {"box": ((-6.55, -7.55, 2.65), (6.55, 7.55, 15.6)),
          "allow": {"door": ((-DOOR_X, -7.65, FLOOR_Z), (DOOR_X, -7.45, DOOR_TOP))}}
WALK = {"paths": [[(0.0, -14.5), (0.0, -9.0), (0.0, -3.0), (0.0, 4.0)], [(0.0, -2.0), (-3.5, 3.0)],
                  [(0.0, -2.0), (3.5, 3.0)]],
        "feet_z": 0.0, "ride": True, "skip": ("tread", "deck", "thresh", "floor_under", "tblock"),
        "turn": [(0.0, 0.0, FLOOR_Z), (-2.5, 3.5, FLOOR_Z), (2.5, 3.5, FLOOR_Z)]}
VERIFY = dict(cls="building", escape=ESCAPE, walk=WALK,
              sockets={HERO: ["chimney_smoke", "heat_glow", "heat_glow", "heat_glow"], LANTERN_P: ["heat_glow"],
                       CHIMNEY_P: ["chimney_smoke"]})
COMPARE = {"f34": {"box": (16, 104, 508, 466), "view": VIEWS["f34_sheet"][:2]},
           "r34": {"box": (516, 104, 1010, 466), "view": (35, 18), "mirror": True},
           "front": {"box": (16, 532, 272, 738), "view": (-30, 10)},
           "side": {"box": (276, 532, 478, 738), "view": (90, 3)},
           "rear": {"box": (516, 532, 762, 738), "view": (-90, 3), "mirror": True},
           "top": {"box": (765, 532, 1010, 738), "view": (0, 89.9)}}


def after(objs):
    """The hinge records (dicts) for the hero and the DoorFrame part."""
    for nm in (HERO, DOOR_P):
        o = objs[nm]
        hb = MODEL.local(o, (HINGE[0], HINGE[1], LEAF[1]))
        o["m068_hinge"] = {"axis_bottom": [round(x, 4) for x in hb], "closed_yaw": 0.0,
                           "open_yaw": OPEN_DEG if nm == HERO else 0.0}


def house_check(objs):
    """The walk-in numbers: floor top 2.60 across the room, the door's clear opening (3.60 x 7.00 above the floor),
    the stair tops, headroom 7.8 inside under every member."""
    h = objs[HERO]
    me = h.data
    tree = BVHTree.FromPolygons([h.matrix_world @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])
    oz = h.matrix_world.translation.z

    def down(x, y, z=9.0):
        hit = tree.ray_cast(MODEL.at(h, (x, y, z)), Vector((0, 0, -1)))[0]
        return round(hit.z - oz, 3) if hit else None

    def up(x, y, z):
        hit = tree.ray_cast(MODEL.at(h, (x, y, z)), Vector((0, 0, 1)))[0]
        return round(hit.z - oz, 3) if hit else None
    floor_z = [down(x, y) for x in (-4.0, -1.3, 1.3, 4.0) for y in (-5.0, 0.0, 5.0)]
    head = [up(x, y, FLOOR_Z + 0.1) for x in (-5.0, -2.5, 0.0, 2.5, 5.0) for y in (-6.5, -3.0, 0.0, 3.0, 6.5)]
    head_min = round(min(z for z in head if z is not None) - FLOOR_Z, 3)
    door_top = up(0.0, -7.8, FLOOR_Z + 0.1)
    xs = []
    for sx in (-1, 1):
        hit = tree.ray_cast(MODEL.at(h, (0.0, -7.8, 5.0)), Vector((sx, 0, 0)))[0]
        xs.append(round(hit.x - h.matrix_world.translation.x + h[MODEL.OFF][0], 3) if hit else None)
    stairs_z = [down(0.0, -10.3, 5.0), down(0.0, -11.9, 5.0)]
    rep = {"floor_z": sorted(set(floor_z)), "headroom_min": head_min, "door_top": door_top, "door_x": xs,
           "stair_tops": stairs_z}
    pr = []
    if any(z is None or abs(z - FLOOR_Z) > 0.005 for z in floor_z):
        pr.append(f"{HERO}: floor tops {rep['floor_z']}")
    if head_min < 7.8:
        pr.append(f"{HERO}: headroom {head_min} under 7.8")
    if door_top is None or door_top - FLOOR_Z < 6.99 or None in xs or xs[1] - xs[0] < 3.59:
        pr.append(f"{HERO}: door clear {xs} to {door_top}")
    return rep, pr


def build(render=True, close=False):
    return MODEL.run(hero=(HERO, hero_all), parts=PARTS, notes=NOTES, collision=COLLISION, budgets=BUDGETS,
                     target_size=TARGET_SIZE, points=POINTS, fx=FX, views=VIEWS, exploded=EXPLODED,
                     scale=(-12.5, -9.0, 0.0), close=CLOSE if close else None, verify=VERIFY,
                     variants={"mirror": mirrored}, checks=[house_check], render=render, after=after)


def mirrored(a):
    """The hero mirrored front to back (the r34 and rear cells draw it so); used only for those renders."""
    with P.frame(Matrix.Scale(-1.0, 4, (0, 1, 0))):
        hero_all(a)


def preview(names=("f34_sheet", "side_sheet")):
    return MODEL.preview(HERO, VIEWS, names, variants={"mirror": mirrored})


def compare(cells=None, out_dir=None, height=360):
    import importlib
    import compare as C
    importlib.reload(C)
    return C.compare(NUM, {k: COMPARE[k] for k in (cells or COMPARE)}, out_dir=out_dir, height=height)
