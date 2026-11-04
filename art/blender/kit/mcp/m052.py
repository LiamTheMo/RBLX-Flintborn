"""052 Boardwalk (references/052.png, remade 2026-11-04) on the shared library (kit_parts / kit_build): a level,
raised timber walkway module with one back rail, an open front long side and a three-step stair at the -X end.
See M052_spec.md.

    import importlib, kit_parts, kit_build, m052
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m052); m052.build()

Build frame (studs): long axis X, front (open long side) -Y, back rail +Y, stairs at -X, ground z 0, the deck centred
on x 0 / y 0 (the hero's origin is its bbox bottom centre, so `m052_offset` carries the stairs' shift).
- 12 deck planks laid across the width (y +-3.00), top z 3.00, 0.40 thick, ends of the run at x +-7.998;
- 8 support posts (1.0 square, 4 a side at x +-7.25 / +-2.417, outer faces flush with the plank ends), each with a
  chamfered bolt block and a square bolt on its outer long face; side beams between them under the plank ends, a
  joist across under the deck at every post pair, a header across each end on the end posts' outer faces;
- 12 knee braces in the long-side planes (each post's inner sides) and one diagonal brace under each end;
- 5 back rail posts (0.85 square, x +-7.325 / +-3.663 / 0) standing on the planks to z 5.15, a rail between them
  (z 4.12-4.55) and a stub block on each end post's outer face (to x +-7.99);
- stairs: three chunky stacked slabs (tops 0.75 / 1.50 / 2.25: four rises of 0.75 with the deck) on two sleepers,
  x -10.75 .. -7.99.
TimberBoardwalkStraight is the tiling continuation: no stairs and no -X end posts (it shares the +X end posts of the
module before it; its side beams and rail run to x -7.99), so modules chain at the 16-stud pitch with one post row
at each joint, as the tiling cell draws. Seam contract: plank ends at +-7.998 are the only faces on the seam planes;
nothing passes +-7.99 except them.
Parts (the sheet's reusable modules): TimberBoardwalkRailPost, TimberBoardwalkSupportPost, TimberBoardwalkRailPlank,
TimberBoardwalkFloorPlank, TimberBoardwalkStairs, TimberBoardwalkCrossbeam, TimberBoardwalkBrace.
Stages 5-6: nothing (the sheet shows no glow, light or effect).
"""
import math

from mathutils import Vector
from mathutils.bvhtree import BVHTree

import kit_build as B
import kit_mcp as K
import kit_parts as P

NUM, TITLE = 52, "Boardwalk"
HERO, STRAIGHT = "TimberBoardwalk", "TimberBoardwalkStraight"
RPOST_P, SPOST_P = "TimberBoardwalkRailPost", "TimberBoardwalkSupportPost"
RAIL_P, PLANK_P, STAIRS_P = "TimberBoardwalkRailPlank", "TimberBoardwalkFloorPlank", "TimberBoardwalkStairs"
CROSS_P, BRACE_P = "TimberBoardwalkCrossbeam", "TimberBoardwalkBrace"
WOOD, WOOD_LIGHT, WOOD_DEEP, BOLT = "m052_wood", "m052_wood_light", "m052_wood_deep", "m052_bolt"

# key -> (hex, roughness, metal, emission, low specular). Stage 4: region medians of the sheet's f34 (spec "Stage 4").
PALETTE = {WOOD: ("#BE7531", 0.85, 0.0, 0.0, True), WOOD_LIGHT: ("#E19348", 0.85, 0.0, 0.0, True),
           WOOD_DEEP: ("#965520", 0.85, 0.0, 0.0, True), BOLT: ("#EC8E3A", 0.55, 0.0, 0.0, False)}
TARGETS = {WOOD: ((0xE7, 0x85, 0x30), "brown"), WOOD_LIGHT: ((0xF2, 0x8B, 0x3B), "brown"),
           WOOD_DEEP: ((0xAA, 0x53, 0x14), "brown"), BOLT: ((0xF8, 0x95, 0x32), "vivid")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)

# ---- layout (spec "Brief") -------------------------------------------------------------------------------------------
PITCH, END, NEAR = 16.0, 7.998, 7.99    # tile pitch; plank ends (on the seam planes); everything else inside NEAR
SEAT = 0.02                             # how far a piece sinks into what carries it
DECK_TOP, PLANK_T, PLANK_CH, N_PLANK, GAP = 3.00, 0.40, 0.05, 12, 0.02
PLANK_Z0 = DECK_TOP - PLANK_T           # 2.60
PLANK_W = (2 * END - (N_PLANK - 1) * GAP) / N_PLANK
DECK_Y = 3.00                           # plank ends across (deck 6.0 wide)
SP_H, SP_Y = 0.50, DECK_Y - 0.50                 # support posts: half width, centre |y| (outer face on the plank ends)
FACE_X = 7.75                           # end posts' outer x faces
SP_TOP = PLANK_Z0 + SEAT
BEAM_Z = (2.00, PLANK_Z0 + SEAT)      # side beams, joists and headers: underside, top (sunk into the planks)
BEAM_Y = (DECK_Y - 0.58, DECK_Y - 0.08)  # side beam |y|: inner, outer face (0.08 behind the post faces)
JOIST_HX = 0.30
BLOCK = dict(hu=0.56, hv=0.42, zc=2.42, depth=0.25, ch=0.06)    # bolt block on a support post's outer face
BOLT_D = dict(h=0.26, depth=0.20, ch=0.10)                      # square bolt head, bevelled (the sheet's rounded knob)
BR_W, BR_RUN, BR_Y = 0.34, 1.10, (DECK_Y - 0.45, DECK_Y - 0.15)                 # knee braces: width, run, |y| (long-side plane)
EB_X = 0.15                                                     # end brace half thickness along x
RP_H, RP_TOP, RP_CAP = 0.425, 5.15, 0.08
RP_Y = DECK_Y - RP_H                    # 2.575: rail posts' outer faces on the plank ends
RAIL_Z, RAIL_HY = (4.12, 4.55), 0.19
STUB = dict(h=0.27, depth=NEAR - FACE_X + SEAT, ch=0.05)
N_TREAD = 3
RISE = DECK_TOP / (N_TREAD + 1)         # 0.75: four rises, ground -> three treads -> deck
STAIR_Y = DECK_Y - 0.05
STAIR_RUN = 0.92
STAIR_X0 = -NEAR - N_TREAD * STAIR_RUN  # the stair foot
SLEEPER = dict(hy=0.18, y=DECK_Y - 0.60, z=0.25 + 0.003)


def tread_box(i):
    """Tread i (0 = bottom): x (front, back), z (bottom, top). Each slab sits 0.003 into the one under it (the bottom
    one on the sleepers); a slab below the beam line runs back into the end posts' outer faces, the top one stops on
    the header."""
    top = (i + 1) * RISE
    x0 = -NEAR - (N_TREAD - i) * STAIR_RUN
    x1 = -FACE_X + SEAT if top < BEAM_Z[0] else -NEAR + 0.002
    return (x0, x1), ((0.25 if i == 0 else i * RISE - 0.003), top)

# per object: support post x, rail post x, ends that carry posts / headers / end braces, stairs
LAYOUT = {HERO: dict(sp=(-7.25, -7.25 / 3, 7.25 / 3, 7.25), rp=(-7.325, -3.6625, 0.0, 3.6625, 7.325), ends=(-1, 1),
                     stairs=True),
          STRAIGHT: dict(sp=(7.25 - 2 * 16 / 3, 7.25 - 16 / 3, 7.25), rp=(-4.675, -0.675, 3.325, 7.325), ends=(1,),
                         stairs=False)}


# ---- small model-specific shapes ---------------------------------------------------------------------------------------
def pad(a, c, n, u, hu, hv, depth, ch, key, name, kind):
    """A plate on a face (bolt block, rail stub, bolt head; m048): centre c on the face, outward normal n, in-face axis
    u (half sizes hu along u, hv along n x u), sunk SEAT into the face, `depth` proud, its front edges bevelled ch."""
    n, u, c = Vector(n).normalized(), Vector(u).normalized(), Vector(c)
    v = n.cross(u)

    def ring(d, inset):
        return [c + n * d + u * (su * (hu - inset)) + v * (sv * (hv - inset)) for su, sv in
                ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return P.prism(a, [ring(-SEAT, 0.0), ring(depth - ch, 0.0), ring(depth, ch)], key, name=name, kind=kind)


def beam_x(a, x0, x1, yc, hy, z, key, name, kind, ch=0.04):
    """A member along X (half width hy across, z = (bottom, top)), chamfered long edges."""
    zc = sum(z) / 2
    return P.plank(a, (x0, yc, zc), (x1, yc, zc), 2 * hy, z[1] - z[0], key, ch=ch, name=name, kind=kind)


def beam_y(a, xc, hx, y0, y1, z, key, name, kind, ch=0.04):
    """A member along Y (half width hx along x)."""
    zc = sum(z) / 2
    return P.plank(a, (xc, y0, zc), (xc, y1, zc), 2 * hx, z[1] - z[0], key, ch=ch, name=name, kind=kind)


# ---- timber --------------------------------------------------------------------------------------------------------------
def plank(a, i, name=None):
    x0 = -END + i * (PLANK_W + GAP)
    zc = PLANK_Z0 + PLANK_T / 2
    xc = x0 + PLANK_W / 2
    return P.plank(a, (xc, -DECK_Y, zc), (xc, DECK_Y, zc), PLANK_W, PLANK_T, WOOD, ch=PLANK_CH,
                   name=name or f"plank{i:02d}", kind="plank", amp=0.06)


def deck(a):
    for i in range(N_PLANK):
        plank(a, i)


def support_post(a, x, sy, name="spost"):
    """A 1.0 square post from the ground to the plank underside (sunk SEAT), vertical edges chamfered 0.05; its bolt
    block (on the outer long face, over the beam line and the plank ends) and square bolt."""
    y = sy * SP_Y
    P.post(a, (x, y), 0.0, SP_TOP, SP_H, WOOD, ch=0.05, name=name, kind="post")
    yf = sy * (SP_Y + SP_H)
    pad(a, (x, yf, BLOCK["zc"]), (0, sy, 0), (1, 0, 0), BLOCK["hu"], BLOCK["hv"], BLOCK["depth"], BLOCK["ch"], WOOD,
        name + "_block", "block")
    pad(a, (x, yf + sy * BLOCK["depth"], BLOCK["zc"]), (0, sy, 0), (1, 0, 0), BOLT_D["h"], BOLT_D["h"],
        BOLT_D["depth"], BOLT_D["ch"], BOLT, name + "_bolt", "bolt")


def rail_post(a, x, name="rpost", stub=0):
    """A 0.85 square rail post standing on the planks (sunk SEAT) to 4.60, a bevelled cap toward wood_light; stub = +-1
    puts the rail's end block on its outer x face."""
    sec = P.sec_rect(RP_H, RP_H, 0.05)
    top = P.sec_rect(RP_H - RP_CAP, RP_H - RP_CAP, 0.03)
    zs = (DECK_TOP - SEAT, RP_TOP - RP_CAP)
    rings = [[(x + u, RP_Y + v, z) for u, v in sec] for z in zs] + [[(x + u, RP_Y + v, RP_TOP) for u, v in top]]
    P.prism(a, rings, WOOD, band_keys=[WOOD, P.mix(WOOD, WOOD_LIGHT, 0.5)], cap_keys=(WOOD, WOOD_LIGHT), name=name,
            kind="post")
    if stub:
        pad(a, (stub * FACE_X, RP_Y, sum(RAIL_Z) / 2), (stub, 0, 0), (0, 1, 0), STUB["h"], STUB["h"],
            STUB["depth"] - SEAT, STUB["ch"], WOOD, name + "_stub", "rail")


def rail(a, x0, x1, name="rail"):
    return beam_x(a, x0, x1, RP_Y, RAIL_HY, RAIL_Z, WOOD, name, "rail")


def side_beam(a, x0, x1, sy, name="beam"):
    return beam_x(a, x0, x1, sy * sum(BEAM_Y) / 2, (BEAM_Y[1] - BEAM_Y[0]) / 2, BEAM_Z, WOOD_DEEP, name, "beam")


def joist(a, x, name="joist"):
    lo = SP_Y - SP_H - SEAT
    return beam_y(a, x, JOIST_HX, -lo, lo, BEAM_Z, WOOD_DEEP, name, "joist")


def header(a, sx, name="header"):
    """The end beam across the deck end, on the end posts' outer x faces (sunk SEAT), out to NEAR."""
    xa, xb = sorted((sx * (FACE_X - SEAT), sx * NEAR))
    return beam_y(a, (xa + xb) / 2, (xb - xa) / 2, -BEAM_Y[1], BEAM_Y[1], BEAM_Z, WOOD_DEEP, name, "header")


def brace_quad(f, s):
    """A 45 deg knee brace's outline in (along, z): low end cut on the post face at `f` (sunk SEAT), toward s (+-1),
    its top cut level on the beam underside (sunk SEAT)."""
    zt = BEAM_Z[0] + SEAT
    zc = zt - BR_RUN
    h = BR_W / 2 * math.sqrt(2)
    ft = f + s * BR_RUN
    return [(f - s * SEAT, zc - h), (f - s * SEAT, zc + h), (ft - s * h, zt), (ft + s * h, zt)]


def knee(a, f, s, sy, name="brace"):
    """A knee brace in a long-side plane (|y| BR_Y) from a post's x face at f toward s up to the side beam."""
    y = sorted((sy * BR_Y[0], sy * BR_Y[1]))
    return P.ext(a, brace_quad(f, s), y[0], y[1], WOOD_DEEP, to3=lambda u, v, w: Vector((u, w, v)), name=name,
                 kind="brace")


def end_brace(a, x, name="ebrace"):
    """The diagonal under an end: from the front end post's inner face (y -1.5) up to the joist's underside."""
    f = -(SP_Y - SP_H)
    return P.ext(a, brace_quad(f, 1), x - EB_X, x + EB_X, WOOD_DEEP, to3=lambda u, v, w: Vector((w, u, v)),
                 name=name, kind="brace")


def stairs(a):
    """Three chunky stacked slabs across the deck's -X end (four rises of 0.75 with the deck), the bottom one on two
    sleepers (the f34's dark feet)."""
    for i in range(N_TREAD):
        (x0, x1), (z0, z1) = tread_box(i)
        P.plank(a, (x0, 0.0, (z0 + z1) / 2), (x1, 0.0, (z0 + z1) / 2), 2 * STAIR_Y, z1 - z0, WOOD, ch=0.04,
                name=f"tread{i}", kind="tread", amp=0.06)
    (x0, x1), _ = tread_box(0)
    for sy in (-1, 1):
        y = sy * SLEEPER["y"]
        P.box(a, (x0 + 0.12, y - SLEEPER["hy"], 0.0), (x1 - 0.30, y + SLEEPER["hy"], SLEEPER["z"]),
              WOOD_DEEP, name=f"sleeper{sy:+d}", kind="sleeper")


# ---- assemblies ------------------------------------------------------------------------------------------------------------
def frame(a, L):
    """Posts, blocks, bolts, beams, joists, headers and braces of one layout."""
    sp = list(L["sp"])
    for sy in (-1, 1):
        tag = "ab"[sy > 0]
        for x in sp:
            support_post(a, x, sy, f"sp{x:+.2f}{tag}")
        # beams: between posts, and from an open end (no end post) to the first post
        spans = [(sp[i] + SP_H - SEAT, sp[i + 1] - SP_H + SEAT) for i in range(len(sp) - 1)]
        if -1 not in L["ends"]:
            spans.insert(0, (-NEAR, sp[0] - SP_H + SEAT))
        for k, (x0, x1) in enumerate(spans):
            side_beam(a, x0, x1, sy, f"beam{tag}{k}")
        for x in sp:
            for s in (-1, 1):
                f = x + s * SP_H
                if any(x0 - 0.1 <= f <= x1 + 0.1 for x0, x1 in spans):
                    knee(a, f, s, sy, f"knee{x:+.2f}{tag}{s:+d}")
    for x in sp:
        joist(a, x, f"joist{x:+.2f}")
    for sx in L["ends"]:
        header(a, sx, f"header{sx:+d}")
        end_brace(a, sx * 7.25, f"ebrace{sx:+d}")


def railing(a, L):
    rp = list(L["rp"])
    for x in rp:
        stub = (1 if x > 0 else -1) if (abs(abs(x) - 7.325) < 1e-6 and (1 if x > 0 else -1) in L["ends"]) else 0
        rail_post(a, x, f"rpost{x:+.2f}", stub=stub)
    spans = [(rp[i] + RP_H - SEAT, rp[i + 1] - RP_H + SEAT) for i in range(len(rp) - 1)]
    if -1 not in L["ends"]:
        spans.insert(0, (-NEAR, rp[0] - RP_H + SEAT))
    for k, (x0, x1) in enumerate(spans):
        rail(a, x0, x1, f"rail{k}")


def module(L):
    def fn(a):
        deck(a)
        frame(a, L)
        railing(a, L)
        if L["stairs"]:
            stairs(a)
    return fn


def support_post_part(a):
    support_post(a, 0.0, -1, "spost")


def rail_post_part(a):
    rail_post(a, -7.325, "rpost", stub=-1)


def rail_part(a):
    rail(a, -3.6625 + RP_H - SEAT, -RP_H + SEAT)


def plank_part(a):
    plank(a, 0, "plank")


def crossbeam_part(a):
    side_beam(a, -7.25 / 3 + SP_H - SEAT, 7.25 / 3 - SP_H + SEAT, -1, "beam")


def brace_part(a):
    knee(a, -7.25 / 3 + SP_H, 1, -1)


PARTS = ((RPOST_P, rail_post_part), (SPOST_P, support_post_part), (RAIL_P, rail_part), (PLANK_P, plank_part),
         (STAIRS_P, stairs), (CROSS_P, crossbeam_part), (BRACE_P, brace_part), (STRAIGHT, module(LAYOUT[STRAIGHT])))
NOTES = {
    HERO: "Boardwalk (remade sheet): a 16-stud raised deck module 6.0 wide, 12 planks across the width (deck top "
          "3.00), 8 support posts with bolt blocks and square bolts, side beams, joists and end headers, 14 braces; 5 "
          "back rail posts (to 5.15) with a rail and end stubs; open front long side; a three-step stair (three slabs, "
          "rises 0.75) at the -X end.",
    STRAIGHT: "Tiling continuation: the hero without stairs and without its -X end posts. Place at +16 studs along X "
              "after the hero (or another Straight); it shares the previous module's end posts (one post row per "
              "joint).",
    RPOST_P: "Back Rail Post: 0.85 square, deck to 5.15, bevelled cap, the rail's end stub block",
    SPOST_P: "Support Post: 1.0 square, ground to the plank underside, bolt block and square bolt",
    RAIL_P: "Rail: one 0.38 x 0.43 rail segment between two rail posts (bay 3.66)",
    PLANK_P: "Deck Plank: one 1.31 x 0.40 plank, 6.0 long (across the deck)",
    STAIRS_P: "Stairs: three chunky stacked slabs on two sleepers, four rises of 0.75 to the deck",
    CROSS_P: "Crossbeam: one side beam segment between two support posts, under the plank ends",
    BRACE_P: "Brace: a 45 deg knee brace from a post face up to the beam",
}
COLLISION = {HERO: "precise", STRAIGHT: "precise", RPOST_P: "box", SPOST_P: "hull", RAIL_P: "box", PLANK_P: "box",
             STAIRS_P: "hull", CROSS_P: "box", BRACE_P: "hull"}
BUDGETS = {HERO: 6000, STRAIGHT: 6000}
Y_OUT = SP_Y + SP_H + BLOCK["depth"] + BOLT_D["depth"]
TARGET_SIZE = ((NEAR - STAIR_X0, 0.01), (2 * Y_OUT, 0.01), (RP_TOP, 0.01))
VIEWS = {"f34_sheet": (-24, 19), "r34_sheet": (-30, 24), "front_sheet": (0, 0), "side_sheet": (90, 0),
         "rear_sheet": (180, 0), "top_sheet": (0, 89.9)}
EXPLODED = {RPOST_P: (-9.0, 3.0, 0.0), SPOST_P: (-6.5, 3.0, 0.0), RAIL_P: (-2.5, 3.0, 2.0), PLANK_P: (2.0, 3.0, 0.0),
            STAIRS_P: (-8.0, -3.5, 0.0), CROSS_P: (1.5, -3.5, 0.0), BRACE_P: (6.0, -3.5, 0.0)}
CLOSE = {"stair_cu": dict(at=(-8.8, -2.0, 1.6), r=2.6, az=-35, el=20),
         "under_cu": dict(at=(2.4, -2.7, 2.0), r=2.2, az=-20, el=-4)}
WALK = {"paths": [[(-11.6, y), (7.4, y)] for y in (-1.4, 0.0, 1.0)], "feet_z": 0.0, "ride": True,
        "skip": ("plank", "tread", "sleeper", "header"),
        "turn": [(0.0, -0.4, DECK_TOP), (-5.4, -0.4, DECK_TOP), (5.4, -0.4, DECK_TOP)]}
VERIFY = dict(cls="structure", classes={HERO: "structure", STRAIGHT: "structure"}, walk=WALK,
              seams={"pitch": (PITCH, 0.0, 0.0), "obj": STRAIGHT})
COMPARE = {"f34": {"box": (25, 145, 505, 370), "view": VIEWS["f34_sheet"][:2]},
           "r34": {"box": (520, 145, 1005, 370), "view": VIEWS["r34_sheet"][:2]},
           "front": {"box": (18, 462, 300, 555), "view": (0, 0)},
           "side": {"box": (318, 462, 422, 555), "view": (90, 0), "mirror": True},
           "rear": {"box": (500, 462, 735, 555), "view": (180, 0)},
           "top": {"box": (750, 455, 1008, 555), "view": (0, 89.9)}}


def after(objs):
    """The Straight module is built with the parts; it is a variant (its own structure budget)."""
    o = objs[STRAIGHT]
    K.tag(o, MODEL.sheet, TITLE, "variant", COLLISION[STRAIGHT], BUDGETS[STRAIGHT], NOTES[STRAIGHT])


def deck_check(objs):
    """The walk surface: every plank top at 2.60 (rays down across each plank), the stair tops at 0.867 / 1.733, and
    nothing of either module past +-7.998 along X except the hero's stairs."""
    out, pr = {}, []
    for nm in (HERO, STRAIGHT):
        h = objs[nm]
        me = h.data
        tree = BVHTree.FromPolygons([h.matrix_world @ v.co for v in me.vertices],
                                    [list(p.vertices) for p in me.polygons])
        tops = []
        for i in range(N_PLANK):
            x = -END + i * (PLANK_W + GAP) + PLANK_W / 2
            for y in (-2.8, -1.0, 0.0, 1.0, 2.0):
                hit = tree.ray_cast(MODEL.at(h, (x, y, 9.0)), Vector((0, 0, -1)))[0]
                tops.append(round(hit.z - h.matrix_world.translation.z, 3) if hit else None)
        bad = [t for t in tops if t is None or abs(t - DECK_TOP) > 0.005]
        out[nm] = {"plank_tops": [min(t for t in tops if t), max(t for t in tops if t)], "samples": len(tops),
                   "off": len(bad)}
        if bad:
            pr.append(f"{nm}: {len(bad)} deck samples off {DECK_TOP}")
    h = objs[HERO]
    me = h.data
    tree = BVHTree.FromPolygons([h.matrix_world @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])
    st = []
    for i in range(N_TREAD):
        hit = tree.ray_cast(MODEL.at(h, (tread_box(i)[0][0] + STAIR_RUN / 2, 0.0, 9.0)), Vector((0, 0, -1)))[0]
        st.append(round(hit.z - h.matrix_world.translation.z, 3) if hit else None)
    out["stair_tops"] = st
    if st != [round((i + 1) * RISE, 3) for i in range(N_TREAD)]:
        pr.append(f"{HERO}: stair tops {st}")
    return out, pr


def _frame_tree(o, shift=0.0):
    """A BVH of o's triangles in the build frame, moved `shift` along X; and its vertices."""
    off = Vector(o[MODEL.OFF]) + Vector((shift, 0.0, 0.0))
    me = o.data
    cos = [v.co + off for v in me.vertices]
    return BVHTree.FromPolygons(cos, [list(p.vertices) for p in me.polygons]), cos


def junction_check(objs):
    """The hero followed by a Straight at +PITCH (kit_verify's seams cannot take the hero: its stairs pass -8): no
    crossing triangles, the closest approach, and the Straight's -X plank face meeting the hero's +X one."""
    th, ch = _frame_tree(objs[HERO])
    ts, cs = _frame_tree(objs[STRAIGHT], PITCH)
    crossing = len(th.overlap(ts))
    near = [c for c in ch if c.x > PITCH / 2 - 1.0]
    close = min(ts.find_nearest(c)[3] for c in near)
    rep = {"crossing_tri_pairs": crossing, "closest": round(close, 4),
           "hero_max_x": round(max(c.x for c in ch), 4), "straight_min_x": round(min(c.x for c in cs), 4)}
    return rep, ([f"{HERO} + {STRAIGHT}: {crossing} triangle pairs cross at the joint"] if crossing else [])


TILE_CELL = {"box": (35, 1362, 640, 1472), "view": (-8, 12)}


def tile_compare(out_dir=None, height=300):
    """Cell C (two modules tiled): the hero and the Straight placed at +PITCH, against the sheet's cell."""
    import bpy
    h, s = bpy.data.objects[HERO], bpy.data.objects[STRAIGHT]
    old = s.location.copy()
    try:
        s.location = h.location + Vector((PITCH, 0.0, 0.0)) + Vector(s[MODEL.OFF]) - Vector(h[MODEL.OFF])
        bpy.context.view_layer.update()
        import importlib
        import compare as C
        importlib.reload(C)
        return C.compare(NUM, {"tile": TILE_CELL}, objs=[h, s], out_dir=out_dir, height=height)
    finally:
        s.location = old
        bpy.context.view_layer.update()


def build(render=True, close=False):
    return MODEL.run(hero=(HERO, module(LAYOUT[HERO])), parts=PARTS, notes=NOTES, collision=COLLISION,
                     budgets=BUDGETS, target_size=TARGET_SIZE, views=VIEWS, exploded=EXPLODED,
                     scale=(-12.0, -3.0, 0.0), close=CLOSE if close else None, verify=VERIFY, checks=[deck_check, junction_check],
                     render=render, after=after)


def preview(names=("f34_sheet", "front_sheet", "top_sheet")):
    return MODEL.preview(HERO, VIEWS, names)


def compare(cells=None, out_dir=None, height=360):
    import importlib
    import compare as C
    importlib.reload(C)
    return C.compare(NUM, {k: COMPARE[k] for k in (cells or COMPARE)}, out_dir=out_dir, height=height)
