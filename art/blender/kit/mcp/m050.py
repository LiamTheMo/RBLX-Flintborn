"""050 Timber Bridge (references/050.png, remade 2026-11-03), on the shared library (kit_parts / kit_build): a short,
level, straight timber footbridge module on eight square posts (four a side, three bays), boards laid across the
width, tan rope wraps and sagging rope rails along both long sides, open at both ends, tiling end to end at a 16-stud
pitch. See M050_spec.md.

    import importlib, kit_parts, kit_build, m050
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m050); m050.build()

Build frame (studs): long axis X, front -Y (the sheet's side view is the -Y elevation), ground z 0, centred on x 0 /
y 0, symmetric about both axes. Seam contract (binding):
- leg feet flat on z 0; deck top (walk surface) z 2.60 on every board (HOUSE_RULES raised floor);
- both ends at x +-7.998 (the end strip, end blocks, stringer ends): nothing past the seams at +-8.000, identical end
  sections, no rope or brace above the deck there; modules butt end to end at the 16-stud pitch;
- post centres y +-2.50, x +-2.35 / +-7.05 (posts 1.0 square, tops 4.90); boards to y +-3.00 (the posts' outer
  faces); stringers on the post lines (|y| 2.05-2.96); side blocks to y +-3.25, pegs to +-3.39.

Every piece is its own closed shell (no booleans), seated 0.005-0.025 into what carries it (blocks 0.003 off):
- 8 posts, each a leg (ground to the stringer underside) and an upper post (stringer top to the bevelled cap) seated
  0.01 into the stringer it stands on (the sheet's exploded view); two twisted rope turns under each cap (corner-cut
  loops, as m048); a pegged block on each post's outer long face, bridging post and stringer;
- 16 boards across the width (0.87 x 0.54, 0.07 gaps, 5 to a bay); the four boards on the post rows run between the
  posts' inner faces; at each end an end strip between the end blocks, and an end block at deck level (top at the
  deck top) on each end post's end face, 0.45 proud of it, out to the seam;
- 2 stringers end to end on the post lines (the beam under the board ends, 0.04 inside them), 4 crossbeams on the
  post rows between them;
- 4 knee braces in the long-side planes, one per long side in each end bay (two per short end), 38 deg from the end
  leg's inner face to the stringer underside;
- 6 rope rails (three per side) sagging between the posts, their ends seated against the turns.
Parts (the sheet's reusable parts): TimberBridgePost, TimberBridgePlank, TimberBridgeStringer, TimberBridgeCrossbeam,
TimberBridgeBrace, TimberBridgeRope. Stages 5-6: nothing (no glow, light or effect on the sheet).
"""
import math

from mathutils import Vector
from mathutils.bvhtree import BVHTree

import kit_build as B
import kit_parts as P

NUM, TITLE = 50, "Timber Bridge"
HERO = "TimberBridge"
POST_P, PLANK_P, STR_P = "TimberBridgePost", "TimberBridgePlank", "TimberBridgeStringer"
CROSS_P, BRACE_P, ROPE_P = "TimberBridgeCrossbeam", "TimberBridgeBrace", "TimberBridgeRope"

WOOD, WOOD_LIGHT, WOOD_DEEP, WOOD_DARK = "m050_wood", "m050_wood_light", "m050_wood_deep", "m050_wood_dark"
ROPE, ROPE_DARK, PEG, BLOCK = "m050_rope", "m050_rope_dark", "m050_peg", "m050_block"

# key -> (hex, roughness, metal, emission, low specular). Stage 4: calibrated against the sheet's f34 (spec "Stage 4";
# rope and block re-measured in "Fixes after round 1").
PALETTE = {WOOD: ("#B47031", 0.85, 0.0, 0.0, True), WOOD_LIGHT: ("#E8873A", 0.85, 0.0, 0.0, True),
           WOOD_DEEP: ("#9C4E1B", 0.85, 0.0, 0.0, True), WOOD_DARK: ("#7A3812", 0.9, 0.0, 0.0, True),
           BLOCK: ("#A4530B", 0.85, 0.0, 0.0, True),
           ROPE: ("#D4A04F", 0.95, 0.0, 0.0, True), ROPE_DARK: ("#BC8A3B", 0.95, 0.0, 0.0, True),
           PEG: ("#EDBF5E", 0.55, 0.0, 0.0, False)}
TARGETS = {WOOD: ((0xE7, 0x82, 0x37), "brown"), WOOD_LIGHT: ((0xFB, 0xA1, 0x3E), "brown"),
           WOOD_DEEP: ((0x93, 0x3F, 0x06), "brown"), WOOD_DARK: ((0x70, 0x34, 0x10), "brown"),
           ROPE: ((0xF7, 0xC5, 0x56), "vivid"), PEG: ((0xF8, 0xCB, 0x61), "vivid")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)

# ---- layout (spec "Brief" and "Stage 1") -------------------------------------------------------------------------
PITCH, END = 16.0, 7.998                # tile pitch; the end strip / stringer ends (0.002 inside the seams)
WY = 2.50                               # post centres across (y +-)
PH, POST_CH = 0.50, 0.05                # post half width, vertical edge chamfer
BAY = 4.70
POST_X = (BAY / 2, 1.5 * BAY)           # 2.35, 7.05
POSTS = sorted((sx * x, sy * WY) for x in POST_X for sx in (-1, 1) for sy in (-1, 1))
POST_TOP, CAP = 4.90, 0.08              # cap bevel (the only bevel besides the timber chamfers)
DECK_TOP, BOARD_T, BOARD_W, BP = 2.60, 0.54, 0.87, BAY / 5     # boards 0.87 wide on a 0.94 pitch
BOARD_Y = 3.00                          # board ends = the posts' outer faces
BOARD_CH = 0.04
BOARD_BOT = DECK_TOP - BOARD_T          # 2.06
SEAT = 0.01                             # how far pieces sink into what carries them
STR_Y = (2.05, 2.96)                    # stringer |y|: on the post line, outer face 0.04 inside the board ends
STR_Z = (1.42, BOARD_BOT + SEAT)        # stringer / crossbeam depth (top sunk 0.01 into the boards)
LEG_TOP, POST_BOT = STR_Z[0] + SEAT, STR_Z[1] - SEAT       # 1.43 / 2.06: leg and upper post seated in the stringer
BEAM_CH = 0.04
CB_HX = 0.30                            # crossbeam half width along x
BLOCK_HX, BLOCK_Z, BLOCK_PROUD = 0.55, (1.45, 2.50), 0.25
EBLOCK_Y = (WY - PH + 0.004, WY + PH - 0.004)               # end block |y|: the post's width (just inside its faces)
EBLOCK_Z = (BOARD_BOT, DECK_TOP)        # at deck level, top at the deck top, sunk 0.01 into the stringer top
PEG_H, PEG_PROUD, PEG_DOME = 0.20, 0.10, 0.04
BRACE_W, BRACE_Y = 0.45, (2.25, 2.75)   # knee brace width, |y| range (the long-side plane, under the stringer)
BRACE_ANG, BRACE_REACH = 38.0, 1.55     # deg from horizontal; reach along the stringer underside from the leg face
TURN_R, TURN_SIDES, TURN_CUT = 0.10, 5, 0.10                # twisted turns; corner cut along each side (m048)
TURN_OUT = TURN_R - P.SINK              # a turn's centreline off the post face (inner strands sunk 0.02)
TURN_STEP = 2 * TURN_R - 0.02           # touching turns
WRAP_MID = 4.04                         # the rails' ends, between the two turns
TURN_Z = (WRAP_MID - TURN_STEP / 2, WRAP_MID + TURN_STEP / 2)     # turn centres 3.95 / 4.13
RAIL_R, RAIL_SIDES, RAIL_LOW, RAIL_N = 0.10, 6, 3.32, 13
RAIL_OFF = PH + TURN_OUT + 0.07         # rail end off the post axis: sunk about 0.03 into the turns' outer strands
BOARD_XS = [s * BP * (k + 0.5) for k in range(8) for s in (-1, 1)]        # 16 board centres
ROW_BOARDS = {round(s * x, 4) for x in POST_X for s in (-1, 1)}         # boards on the post rows


def mix(k1, k2, t):
    return P.mix(k1, k2, t, step=0.05)


# ---- timber ---------------------------------------------------------------------------------------------------------
def leg(a, x, y, name):
    """The post's leg: 1.0 square, vertical edges chamfered 0.05, from the ground up into the stringer underside
    (sunk 0.01); the post's colour (sheet: the legs are the post colour on the lit face)."""
    sec = P.sec_rect(PH, PH, POST_CH)
    rings = [[(x + u, y + v, z) for u, v in sec] for z in (0.0, LEG_TOP)]
    return P.prism(a, rings, WOOD_DEEP, name=name, kind="leg")


def post(a, x, y, name):
    """The upper post: 1.0 square (vertical edges chamfered 0.05), standing on the stringer (sunk 0.01) up to 4.90
    with a bevelled cap; the bevel and top toward wood_light (by position)."""
    sec = P.sec_rect(PH, PH, POST_CH)
    top = P.sec_rect(PH - CAP, PH - CAP, POST_CH * 0.6)
    zs = (POST_BOT, POST_TOP - CAP)
    rings = [[(x + u, y + v, z) for u, v in sec] for z in zs] + [[(x + u, y + v, POST_TOP) for u, v in top]]
    light = mix(WOOD_DEEP, WOOD_LIGHT, 0.6)
    return P.prism(a, rings, WOOD_DEEP, band_keys=[WOOD_DEEP, light], cap_keys=(WOOD_DEEP, WOOD_LIGHT), name=name,
                   kind="post")


def wraps(a, x, y, name):
    """Two tight round rope turns stacked under the cap (m048 turns): each a closed twisted loop round the post with
    its corners cut at 45 deg (two 45 deg bends instead of one square mitre, so the coil reads round, not as a square
    collar) and a midpoint on each side; the innermost strands sink P.SINK into the post faces, the turns touch.
    120 tris each."""
    lo, hi = (x - PH, y - PH), (x + PH, y + PH)
    out = []
    for t, z in enumerate(TURN_Z):
        c4 = P.rect_loop(lo, hi, z, TURN_OUT)
        loop = []
        for k in range(4):
            a_, b_ = c4[k], c4[(k + 1) % 4]
            d = (b_ - a_).normalized()
            loop += [a_ + d * TURN_CUT, (a_ + b_) / 2, b_ - d * TURN_CUT]
        out.append(P.rope(a, loop, TURN_R, ROPE, ROPE_DARK, sides=TURN_SIDES, closed=True, twist=True, up=(0, 0, 1),
                          name=f"{name}_{t}", kind="rope_wrap"))
    return out


def side_block(a, x, y, name):
    """The pegged block on a post's outer long face (y = +-3.0), bridging post and stringer, with its square peg."""
    s = 1 if y > 0 else -1
    y0, y1 = sorted((s * (BOARD_Y + 0.003), s * (BOARD_Y + BLOCK_PROUD)))      # 0.003 off the post face
    P.box(a, (x - BLOCK_HX, y0, BLOCK_Z[0]), (x + BLOCK_HX, y1, BLOCK_Z[1]), BLOCK, name=name, kind="block")
    P.bolt(a, (x, s * (BOARD_Y + BLOCK_PROUD), sum(BLOCK_Z) / 2), (0, s, 0), (0, 0, 1), PEG, h=PEG_H, proud=PEG_PROUD,
           dome=PEG_DOME, name=name + "_peg", kind="peg")


def end_block(a, x, y, name):
    """The end block on an end post's end face at deck level (side cell: top at the deck top, 0.45 proud of the post,
    out to the seam), sitting on the stringer end (sunk 0.01) with the end strip running between the two. No peg: one
    on the end face would cross the seam."""
    s = 1 if x > 0 else -1
    sy = 1 if y > 0 else -1
    x0, x1 = sorted((s * (abs(x) + PH - SEAT), s * END))
    yc = sy * sum(EBLOCK_Y) / 2
    zc = sum(EBLOCK_Z) / 2
    return P.plank(a, (x0, yc, zc), (x1, yc, zc), EBLOCK_Y[1] - EBLOCK_Y[0], EBLOCK_Z[1] - EBLOCK_Z[0], BLOCK,
                   ch=BOARD_CH, name=name, kind="block")


def board(a, x, name, y=BOARD_Y, width=BOARD_W, ch=BOARD_CH):
    zc = DECK_TOP - BOARD_T / 2
    return P.plank(a, (x, -y, zc), (x, y, zc), width, BOARD_T, WOOD, ch=ch, name=name, kind="plank", amp=0.06)


def deck(a):
    """16 boards across the width (the post-row boards between the posts' inner faces) and an end strip at each end
    between the end blocks (sunk 0.01 into them)."""
    for i, x in enumerate(sorted(BOARD_XS)):
        on_row = round(x, 4) in ROW_BOARDS
        board(a, x, f"board{i:02d}", y=(WY - PH + SEAT) if on_row else BOARD_Y)
    x0 = POST_X[1] + PH + 0.003
    for s in (-1, 1):
        board(a, s * (x0 + END) / 2, f"end_strip{s:+d}", y=EBLOCK_Y[0] + SEAT, width=END - x0,
              ch=0.0)                                                               # square: one flat end face


def stringer(a, sy, name, x0=-END, x1=END):
    lo, hi = STR_Y
    yc, zc = sy * (lo + hi) / 2, sum(STR_Z) / 2
    return P.plank(a, (x0, yc, zc), (x1, yc, zc), hi - lo, STR_Z[1] - STR_Z[0], WOOD_DARK, ch=BEAM_CH, name=name,
                   kind="stringer")


def crossbeam(a, x, name):
    """A crossbeam on a post row, between the stringers' inner faces (sunk 0.01 into them)."""
    lo = STR_Y[0] + SEAT
    zc = sum(STR_Z) / 2
    return P.plank(a, (x, -lo, zc), (x, lo, zc), 2 * CB_HX, STR_Z[1] - STR_Z[0], WOOD_DARK, ch=BEAM_CH, name=name,
                   kind="crossbeam")


def brace_quad(sx):
    """The knee brace's XZ outline at the end post on side sx: BRACE_ANG from horizontal, BRACE_W wide, its low end
    cut on the leg's inner face (sunk 0.01), its top cut level on the stringer underside (sunk 0.01), reaching
    BRACE_REACH along it from the leg face (side cell: about 38 deg, 1.5-1.6)."""
    th = math.radians(BRACE_ANG)
    xf = sx * (POST_X[1] - PH + SEAT)           # 0.01 inside the leg's inner face
    zt = STR_Z[0] + SEAT                        # 0.01 inside the stringer
    hx = BRACE_W / 2 / math.sin(th)             # half the top cut (horizontal)
    hv = BRACE_W / 2 / math.cos(th)             # half the low cut (vertical)
    run = BRACE_REACH - hx                      # leg face to where the centreline meets the stringer underside
    zc = zt - run * math.tan(th)                # the centreline's height at the leg face
    xt = xf - sx * run
    P.GEO["brace"] = {"reach": round(BRACE_REACH, 3), "low_cut": [round(zc - hv, 3), round(zc + hv, 3)],
                      "deg": BRACE_ANG}
    return [(xf, zc - hv), (xf, zc + hv), (xt + sx * hx, zt), (xt - sx * hx, zt)]


def brace(a, sx, sy, name):
    lo, hi = sorted((sy * BRACE_Y[0], sy * BRACE_Y[1]))
    q = brace_quad(sx)
    return P.prism(a, [[(x, y, z) for x, z in q] for y in (lo, hi)], WOOD_DARK, name=name, kind="brace")


# ---- rope rails -----------------------------------------------------------------------------------------------------
def rail_path(x0, x1, y, n=RAIL_N):
    """A sagging rail from x0 to x1 at y: ends at WRAP_MID, low point RAIL_LOW at mid-span (a catenary)."""
    L = x1 - x0
    sag = WRAP_MID - RAIL_LOW
    c = L / 2
    lo, hi = 0.05, 100.0
    for _ in range(80):                          # the catenary parameter k with k (cosh(c / k) - 1) = sag
        k = (lo + hi) / 2
        lo, hi = (k, hi) if k * (math.cosh(c / k) - 1) > sag else (lo, k)
    pts = []
    for i in range(n):
        t = i / (n - 1)
        x = x0 + L * t
        z = RAIL_LOW + k * (math.cosh((x - x0 - c) / k) - 1)
        pts.append(Vector((x, y, z)))
    return pts


def rail(a, xa, xb, y, name):
    path = rail_path(xa + RAIL_OFF, xb - RAIL_OFF, y)
    return P.rope(a, path, RAIL_R, ROPE, ROPE_DARK, sides=RAIL_SIDES, twist=False, up=(0, 0, 1), name=name,
                  kind="rope_rail")


# ---- assemblies ------------------------------------------------------------------------------------------------------
def post_set(a, x, y, tag, end=False):
    """The upper post with its turns, side block and (end posts) end block: the TimberBridgePost part."""
    post(a, x, y, tag + "post")
    wraps(a, x, y, tag + "wrap")
    side_block(a, x, y, tag + "block")
    if end:
        end_block(a, x, y, tag + "eblock")


def hero_fn(a):
    for x, y in POSTS:
        leg(a, x, y, f"p{x:+.2f}{y:+.1f}_leg")
        post_set(a, x, y, f"p{x:+.2f}{y:+.1f}_", end=abs(x) > POST_X[0] + 1)
    deck(a)
    for sy in (-1, 1):
        stringer(a, sy, f"stringer{sy:+d}")
    for x in sorted({p[0] for p in POSTS}):
        crossbeam(a, x, f"crossbeam{x:+.2f}")
    for sx in (-1, 1):
        for sy in (-1, 1):
            brace(a, sx, sy, f"brace{sx:+d}{sy:+d}")
    xs = sorted({p[0] for p in POSTS})
    for sy in (-1, 1):
        for j in range(3):
            rail(a, xs[j], xs[j + 1], sy * WY, f"rail{sy:+d}_{j}")


def post_part(a):
    """The -X / -Y corner upper post (the leg stays in the hero) with its turns, side block and end block."""
    post_set(a, -POST_X[1], -WY, "", end=True)


def plank_part(a):
    board(a, 0.0, "board")


def stringer_part(a):
    stringer(a, 1, "stringer")


def cross_part(a):
    crossbeam(a, 0.0, "crossbeam")


def brace_part(a):
    brace(a, 1, 1, "brace")


def rope_part(a):
    rail(a, -BAY / 2, BAY / 2, 0.0, "rail")


PARTS = ((POST_P, post_part), (PLANK_P, plank_part), (STR_P, stringer_part), (CROSS_P, cross_part),
         (BRACE_P, brace_part), (ROPE_P, rope_part))
NOTES = {
    HERO: "Timber footbridge module (sheet 050, remade): 8 square posts (1.0, tops 4.90), each a leg and an upper "
          "post standing on the stringers, with two twisted rope turns and a pegged block; 16 boards across the "
          "width plus end strips and end blocks, deck top 2.60 (level), 2 stringers on the long sides under the "
          "board ends, 4 crossbeams, 4 long-side knee braces in the end bays, 6 sagging rope rails; open ends at x "
          "+-8.000, tiles end to end at a 16-stud pitch.",
    POST_P: "Post: the 1.0 square chamfered upper post (stringer top to 4.90) with a bevelled cap, two twisted rope "
            "turns, a pegged block on its outer face and the deck-level end block on its end face (the corner post)",
    PLANK_P: "Deck Plank: one 0.87 x 0.54 board, 6.0 long (across the deck)",
    STR_P: "Stringer: the full-length 0.91 x 0.65 beam on a long side, under the board ends and the posts (16.0)",
    CROSS_P: "Crossbeam: 0.6 x 0.65 beam between the stringers on a post row",
    BRACE_P: "Brace: 38 deg knee brace in the long-side plane, end leg to stringer underside",
    ROPE_P: "Rope Segment: one sagging rope rail between two posts (bay 4.70)",
}
COLLISION = {HERO: "precise", POST_P: "hull", PLANK_P: "box", STR_P: "box", CROSS_P: "box", BRACE_P: "hull",
             ROPE_P: "none"}
BUDGETS = {HERO: 6000}
TARGET_SIZE = ((15.996, 0.01), (6.780, 0.01), (4.90, 0.01))
VIEWS = {"f34_sheet": (-37, 23), "r34_sheet": (143, 23), "side_sheet": (0, 0), "front_sheet": (-90, 0),
         "rear_sheet": (90, 0), "top_sheet": (0, 89.9)}
EXPLODED = {POST_P: (-7.0, 3.5, 0.0), PLANK_P: (-3.5, 3.5, 0.0), CROSS_P: (-0.5, 3.5, 0.0), BRACE_P: (2.0, 3.5, 0.0),
            ROPE_P: (6.0, 3.5, 0.0), STR_P: (0.0, -2.0, 0.0)}
CLOSE = {"joint_cu": dict(at=(-2.35, -3.0, 2.9), r=1.6, az=-40, el=18),
         "under_cu": dict(at=(-6.0, -2.0, 1.2), r=2.6, az=-30, el=8)}
WALK = {"paths": [[(-7.95, 0.0), (7.95, 0.0)], [(-7.95, -0.6), (7.95, -0.6)], [(-7.95, 0.6), (7.95, 0.6)]],
        "feet_z": DECK_TOP, "skip": ("plank",), "turn": [(0.0, 0.0, DECK_TOP), (-4.7, 0.0, DECK_TOP)]}
VERIFY = dict(cls="structure", walk=WALK, seams={"pitch": (PITCH, 0.0, 0.0)})
COMPARE = {"f34": {"box": (40, 100, 500, 385), "view": (-37, 23)},
           "r34": {"box": (520, 100, 1010, 385), "view": (143, 23)},
           "front": {"box": (25, 455, 190, 585), "view": (-90, 0)},
           "side": {"box": (200, 455, 540, 585), "view": (0, 0)},
           "rear": {"box": (665, 455, 830, 585), "view": (90, 0)},
           "top": {"box": (850, 405, 1000, 595), "view": (0, 89.9), "rot90": 1}}


def deck_check(objs):
    """The walk surface: every board top at 2.60 (rays down at each board centre and near both ends), and every
    full-width board resting on both stringers."""
    h = objs[HERO]
    me = h.data
    tree = BVHTree.FromPolygons([h.matrix_world @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])
    down = Vector((0, 0, -1))
    tops = []
    for x in sorted(BOARD_XS) + [s * (POST_X[1] + PH + END) / 2 for s in (-1, 1)]:
        for y in (-1.5, 0.0, 1.5):
            hit = tree.ray_cast(MODEL.at(h, (x + 0.05, y, 9.0)), down)[0]
            tops.append(round(hit.z - h.matrix_world.translation.z + h[MODEL.OFF][2], 3) if hit else None)
    bad = [t for t in tops if t is None or abs(t - DECK_TOP) > 0.02]
    rep = {"board_tops": [min(t for t in tops if t), max(t for t in tops if t)], "samples": len(tops), "off": len(bad)}
    return rep, ([f"{HERO}: {len(bad)} deck samples off 2.60"] if bad else [])


def build(render=True, close=False):
    return MODEL.run(hero=(HERO, hero_fn), parts=PARTS, notes=NOTES, collision=COLLISION, budgets=BUDGETS,
                     target_size=TARGET_SIZE, views=VIEWS, close=CLOSE if close else None, verify=VERIFY,
                     checks=[deck_check], render=render, exploded=EXPLODED, scale=(-9.5, -4.0, 0.0))


def preview(names=("f34_sheet", "side_sheet", "front_sheet")):
    return MODEL.preview(HERO, VIEWS, names)


def compare(cells=None, out_dir=None):
    import importlib
    import compare as C
    importlib.reload(C)
    return C.compare(NUM, {k: COMPARE[k] for k in (cells or COMPARE)}, out_dir=out_dir)
