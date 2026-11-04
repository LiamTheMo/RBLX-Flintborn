"""072 Timber Gate (references/072.png, remade sheet; no earlier builder) on the shared library (kit_parts / kit_build):
a walk-through double timber gate. See art/blender/renders/models/M072/M072_spec.md.

    import importlib, kit_parts, kit_build, m072
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m072); m072.build()

Build frame (studs): front -Y (lanterns and banners), +X right, ground z 0, the gate centred on x 0; everything is
mirror-symmetric about x 0 (the right pillar is built with s = +1, the left with s = -1).
- Each pillar: a 1.70-square main post (inner face |x| 4.35) and a 1.60 x 1.05 outer post against it (front face
  recessed 0.35), both up into a deep bolster block (|x| 4.0-8.8, y -1.92..0.85, 7.40-8.24) that carries the lintel and,
  at its front, two hanging lanterns and the banner; a 1.75-square cap block on the lintel over the main post; a rear
  rail on the posts' backs and a diagonal brace on the outer post's back (the rear cell); three open rope collar runs
  at the main post's foot, a C-run lashing over the rail; a grey rock base in front with two leaf clumps.
- The lintel (|x| <= 8.32, 1.30 deep, 8.22-9.66) carries rope wraps round it over the opening (|x| 3.55); wraps round
  the bolster's ends (|x| 8.55); rope bands strapped over lintel and bolster at |x| 7.0 and 5.2 (the front cell).
- Two gate leaves of four vertical planks (0.30 thick, 0.10 off the ground, tops 7.33-7.42), iron straps front and back
  with bolts and end plates, a ring handle near the meeting edge, a latch keeper on the back; each leaf's hinge knuckles
  turn on the pins of two hinge blocks on the main post's inner face. Hinge axis |x| 4.20, y 0.30; the leaves open
  inward (+Y) by 90 deg. A latch bar rests across both keepers on the back (closed state only).
Every piece is its own closed shell (no booleans), seated 0.002-0.05 into what holds it.
Hero TimberGate (closed, as the sheet's hero); parts TimberGatePost, ...Lintel, ...LeafLeft, ...LeafRight, ...LatchBar,
...RopeWrap, ...Hinge, ...Banner, ...Lantern, ...RockBase. The leaf parts keep their origin on their hinge axis (main
session ruling); the hero and the leaf parts store the hinge axes. Stage 5: Neon lantern glass with a heat_glow socket
per lantern (HOUSE_RULES); stage 6: those sockets only.
"""
import math
import random

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_build as B
import kit_parts as P

NUM, TITLE = 72, "Timber Gate"
HERO = "TimberGate"
POST_P, LINTEL_P, LEAF_LP, LEAF_RP = "TimberGatePost", "TimberGateLintel", "TimberGateLeafLeft", "TimberGateLeafRight"
LATCH_P, WRAP_P, HINGE_P = "TimberGateLatchBar", "TimberGateRopeWrap", "TimberGateHinge"
BANNER_P, LANTERN_P, ROCK_P = "TimberGateBanner", "TimberGateLantern", "TimberGateRockBase"

TIMBER, TIMBER_END, TIMBER_DEEP = "m072_timber", "m072_timber_end", "m072_timber_deep"
PLANK = "m072_plank"
IRON, LANT_IRON, GLOW = "m072_iron", "m072_lantern_iron", "m072_glow"
ROPE, ROPE_DEEP = "m072_rope", "m072_rope_deep"
BANNER, BANNER_DEEP, CREAM = "m072_banner", "m072_banner_deep", "m072_cream"
STONE, STONE_DARK = "m072_stone", "m072_stone_dark"
LEAF_L, LEAF_G, LEAF_D = "m072_leaf_lime", "m072_leaf", "m072_leaf_dark"

# key -> (hex, roughness, metal, emission, low specular). Stage 4 (spec "Stage 4"): sheet medians, K.calibrate'd.
PALETTE = {
    TIMBER: ("#9A5E21", 0.85, 0.0, 0.0, True),
    TIMBER_END: ("#C2843A", 0.8, 0.0, 0.0, True),
    TIMBER_DEEP: ("#6E4426", 0.9, 0.0, 0.0, True),
    PLANK: ("#9A5F21", 0.85, 0.0, 0.0, True),
    IRON: ("#545866", 0.55, 0.4, 0.0, False),
    LANT_IRON: ("#3A3C45", 0.6, 0.35, 0.0, False),
    GLOW: ("#F9D83A", 0.5, 0.0, 1.0, False),
    ROPE: ("#C2A058", 0.95, 0.0, 0.0, True),
    ROPE_DEEP: ("#9A7A40", 0.95, 0.0, 0.0, True),
    BANNER: ("#E81C1A", 0.9, 0.0, 0.0, True),
    BANNER_DEEP: ("#8E1212", 0.9, 0.0, 0.0, True),
    CREAM: ("#F2E6CF", 0.9, 0.0, 0.0, True),
    STONE: ("#797C8D", 0.9, 0.0, 0.0, True),
    STONE_DARK: ("#61647A", 0.9, 0.0, 0.0, True),
    LEAF_L: ("#8ABA0B", 0.8, 0.0, 0.0, True),
    LEAF_G: ("#72A307", 0.8, 0.0, 0.0, True),
    LEAF_D: ("#3E6E04", 0.85, 0.0, 0.0, True),
}
# calibration targets: the sheet's rendered medians (spec "Stage 4") and K.sample kinds
TARGETS = {TIMBER: ((0xC2, 0x6C, 0x21), "brown"), PLANK: ((0xC2, 0x6C, 0x21), "brown"),
           ROPE: ((0xF5, 0xC2, 0x5F), "all"), BANNER: ((0xFD, 0x22, 0x1B), "vivid"),
           STONE: ((0x97, 0x95, 0xA4), "all"), LEAF_G: ((0x89, 0xC6, 0x0A), "green"),
           LEAF_L: ((0xAC, 0xE5, 0x0C), "green"), IRON: ((0x59, 0x5D, 0x6A), "all"),
           CREAM: ((0xFE, 0xEA, 0xCC), "all")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)


def mix(k1, k2, t):
    return P.mix(k1, k2, t, step=0.05)


# ---- layout (spec "Brief": front cell at 14 px / stud, the R6 figure 70 px = 5 studs) ------------------------------
XI = 4.35                                # main post inner face |x|
MP = (4.35, 6.05, 0.85)                  # main post |x| range, half depth
OP = (6.03, 7.65, -0.50, 0.55)           # outer post |x| range (sunk 0.02 into the main post), y range
POST_CH = 0.06
LIN = dict(x=8.32, hy=0.65, z=(8.22, 9.66), ch=0.06)
CAP = dict(h=0.875, z0=LIN["z"][1] - 0.02, z1=11.08, bevel=0.10)
# the bolster: a deep block on both posts under the lintel (the lintel sunk 0.02 into its top), from the posts' backs
# out to the front where the lanterns and banner hang
BOL = dict(x=(4.00, 8.80), y=(-1.92, 0.85), z=(7.40, 8.24), ch=0.05)
POST_TOP = BOL["z"][0] + 0.02            # posts sunk 0.02 into the bolster's underside
RAIL = dict(x=(4.30, 7.74), y=(MP[2] - 0.02, 1.45), z=(6.00, 6.80), ch=0.05)
BRACE = dict(lo=(7.70, 2.70), hi=(OP[0], 5.05), w=0.62, y=(OP[3] - 0.02, 1.20))  # back 0.35 proud of the post (verifier R1)
RW = 0.15                                # rope radius (wraps, collars)
COLLAR_Z = (0.95, 1.23, 1.51)            # collar turn centres (z), touching
WRAP_X = {"in": 3.55, "out": 8.55}       # vertical wraps: round the lintel over the opening / the bolster's end

# leaves (right leaf; the left is its mirror)
XP, YP = 4.20, 0.30                      # hinge axis |x|, y
LEAF_Z0 = 0.10
PL_T, PL_X0, PL_X1, PL_GAP = 0.30, 0.03, 4.22, 0.02
PL_TOPS = (7.34, 7.48, 7.24, 7.30)       # from the meeting edge out; outer top clears the bolster (verifier R1)
STRAPS = {"hi": (5.25, 5.96, 5.00, 6.22), "lo": (1.45, 2.16, 1.20, 2.40)}    # body z0, z1, plate z0, z1
HINGE_ZC = {k: (v[0] + v[1]) / 2 for k, v in STRAPS.items()}
ST_T, PLATE_T = 0.08, 0.10
F_BODY, F_PLATE = (0.76, 3.40), (3.38, 3.98)
R_BODY, R_PLATE = (0.76, XP), (3.85, 4.06)
BOLT_X = (1.18, 2.10, 3.00)
RING = dict(x=0.72, z=3.16, R=0.50, r=0.10)
KNUCKLE = dict(r=0.11, h=0.36)           # knuckle half height (the strap body's)
LATCH = dict(z=3.83, y=0.37, r=0.14, x=1.25, keep=(0.40, 0.70))
OPEN_DEG = 90.0

# lanterns, banner, rocks, foliage
LANT_Y = -1.45
LANT_X = (5.10, 8.25)
LANT_BOT = 4.50
LANT = dict(w=1.0, plate=0.15, gw=0.74, gh=1.05, band=0.18, roof=0.30, fin=0.12, bar=0.13)
ROD = dict(x=(5.50, 7.72), r=0.13, knob=0.15)
CLOTH = dict(x=(5.80, 7.62), t=0.08, tips=2.30, notch=3.00)
SLEEVE_IN, SLEEVE_T = ROD["r"] / math.cos(math.pi / 8) + 0.008, 0.08
ROD_Z = BOL["z"][0] - (SLEEVE_IN + SLEEVE_T) + 0.02     # the hem sleeve seated 0.02 into the bolster's underside
EMB = dict(z=4.90, rings=((0.60, 1.20, 0.14), (0.30, 0.60, 0.11)))
STRIPE_IN, STRIPE_W, STRIPE_Z0 = 0.10, 0.07, 2.75
ROCK = dict(x=6.65, size=(2.50, 1.90, 1.80), seed=72)
CLUMPS = (("out", (8.45, -1.20), 6, 0.98, 7201), ("in", (4.40, -2.25), 6, 0.95, 7202))


# ---- small helpers -------------------------------------------------------------------------------------------------
def xr(s, x0, x1):
    """An |x| range on side s, ordered."""
    return (min(s * x0, s * x1), max(s * x0, s * x1))


def rope_loop(a, pts3, c, normal, ref, r, n, name, kind="rope_wrap", sides=5, key=ROPE):
    """A closed twisted rope round the convex hull of section points (in the plane through c with this normal), its
    inner strands sunk P.SINK (m050 wraps / P.rope_band): n points (the hull's corners and midpoints of its longest
    sides)."""
    loop = P.hull_loop(pts3, c, normal, ref, r - P.SINK, n)
    return P.rope(a, loop, r, key, ROPE_DEEP, sides=sides, closed=True, twist=True, up=tuple(normal), name=name,
                  kind=kind)


def rect_pts(y0, y1, z0, z1, ch, x):
    """A chamfered rectangle section (y, z) at x as 3D points."""
    yc, zc = (y0 + y1) / 2, (z0 + z1) / 2
    return [Vector((x, yc + u, zc + v)) for u, v in P.sec_rect((y1 - y0) / 2, (z1 - z0) / 2, ch)]


# ---- frame timber ----------------------------------------------------------------------------------------------------
def main_post(a, s):
    x0, x1 = xr(s, MP[0], MP[1])
    return P.post(a, ((x0 + x1) / 2, 0.0), 0.0, POST_TOP, (x1 - x0) / 2, TIMBER, ch=POST_CH, half_y=MP[2],
                  name="post", kind="post")


def outer_post(a, s):
    x0, x1 = xr(s, OP[0], OP[1])
    return P.post(a, ((x0 + x1) / 2, (OP[2] + OP[3]) / 2), 0.0, POST_TOP, (x1 - x0) / 2,
                  mix(TIMBER, TIMBER_DEEP, 0.15), ch=POST_CH, half_y=(OP[3] - OP[2]) / 2, name="outer", kind="post")


def cap(a, s):
    """The cap block standing on the lintel over the main post: chamfered sides, a bevelled top in cut-wood end."""
    xc = s * (MP[0] + MP[1]) / 2
    h, bv = CAP["h"], CAP["bevel"]
    rings = [[(xc + u, v, z) for u, v in P.sec_rect(h, h, POST_CH)] for z in (CAP["z0"], CAP["z1"] - bv)]
    rings.append([(xc + u, v, CAP["z1"]) for u, v in P.sec_rect(h - bv, h - bv, POST_CH * 0.6)])
    return P.prism(a, rings, TIMBER, band_keys=[None, mix(TIMBER, TIMBER_END, 0.5)], cap_keys=(None, TIMBER_END),
                   name="cap", kind="cap")


def lintel(a):
    zc, hv = sum(LIN["z"]) / 2, (LIN["z"][1] - LIN["z"][0]) / 2
    return P.beam(a, (-LIN["x"], 0.0, zc), (LIN["x"], 0.0, zc), P.sec_rect(LIN["hy"], hv, LIN["ch"]), TIMBER,
                  cap_keys=(TIMBER_END, TIMBER_END), name="lintel", kind="beam")


def bolster(a, s):
    x0, x1 = xr(s, *BOL["x"])
    yc, zc = sum(BOL["y"]) / 2, sum(BOL["z"]) / 2
    sec = P.sec_rect((BOL["y"][1] - BOL["y"][0]) / 2, (BOL["z"][1] - BOL["z"][0]) / 2, BOL["ch"])
    return P.beam(a, (x0, yc, zc), (x1, yc, zc), sec, TIMBER, cap_keys=(TIMBER_END, TIMBER_END), name="bolster",
                  kind="beam")


def rear_rail(a, s):
    x0, x1 = xr(s, *RAIL["x"])
    yc, zc = sum(RAIL["y"]) / 2, sum(RAIL["z"]) / 2
    sec = P.sec_rect((RAIL["y"][1] - RAIL["y"][0]) / 2, (RAIL["z"][1] - RAIL["z"][0]) / 2, RAIL["ch"])
    return P.beam(a, (x0, yc, zc), (x1, yc, zc), sec, TIMBER, cap_keys=(TIMBER_END, TIMBER_END), name="rail",
                  kind="beam")


def brace(a, s):
    """The rear cell's diagonal brace on the outer post's back face (sunk 0.02), its upper end butting 0.02 into the
    main post's outer side face, both ends cut vertical."""
    (xl, zl), (xh, zh) = BRACE["lo"], BRACE["hi"]
    xh -= 0.02
    ang = math.atan2(zh - zl, abs(xh - xl))
    hv = BRACE["w"] / 2 / math.cos(ang)
    poly = [(s * xl, zl - hv), (s * xl, zl + hv), (s * xh, zh + hv), (s * xh, zh - hv)]
    return P.ext(a, poly, *BRACE["y"], mix(TIMBER, TIMBER_END, 0.25), to3=lambda u, v, w: Vector((u, w, v)),
                 name="brace", kind="brace")


# ---- rope ------------------------------------------------------------------------------------------------------------
COLLAR_IN = 0.30                         # the collar runs' ends turn into the post this far from its inner face
END_SINK = 0.04                          # an open rope's end turned this far into the face it ends in


def post_sections(s, z):
    """The main and outer posts' chamfered sections at height z (3D points)."""
    x0, x1 = xr(s, MP[0], MP[1])
    pts = [Vector(((x0 + x1) / 2 + u, v, z)) for u, v in P.sec_rect((x1 - x0) / 2, MP[2], POST_CH)]
    o0, o1 = xr(s, OP[0], OP[1])
    oy = (OP[2] + OP[3]) / 2
    pts += [Vector(((o0 + o1) / 2 + u, oy + v, z)) for u, v in P.sec_rect((o1 - o0) / 2, (OP[3] - OP[2]) / 2, POST_CH)]
    return pts


def collar(a, s):
    """Three touching twisted runs round the posts' foot (the sheet's tan ground collar): each follows the hull of the
    main and outer posts from the main post's front face round the outer post to its back face, both ends turned
    square into the main post 0.30 from its inner face (the leaf hangs 0.13 off that face: no room for a full turn)."""
    xin = s * (MP[0] + COLLAR_IN)
    out = []
    for i, z in enumerate(COLLAR_Z):
        sec = post_sections(s, z)
        c = sum(sec, Vector()) / len(sec)
        loop = P.hull_loop(sec, c, (0, 0, 1), (1, 0, 0), RW - P.SINK, 16)
        # keep the run outside the inner region, in order from the front face round the outer side to the back face
        keep = [k for k, p in enumerate(loop) if s * p.x > MP[0] + COLLAR_IN + 0.15]
        n = len(loop)
        start = next(k for k in keep if (k - 1) % n not in keep)
        run = []
        k = start
        while k in keep:
            run.append(loop[k])
            k = (k + 1) % n
        if run[0].y > run[-1].y:
            run.reverse()
        yf, yb = -MP[2] + END_SINK, MP[2] - END_SINK
        path = [Vector((xin, yf, z)), Vector((xin, yf - (RW - P.SINK) - END_SINK, z))] + run + \
            [Vector((xin, yb + (RW - P.SINK) + END_SINK, z)), Vector((xin, yb, z))]
        out.append(P.rope(a, path, RW, ROPE, ROPE_DEEP, sides=5, twist=True, up=(0, 0, 1), name=f"collar{i}",
                          kind="rope_turn"))
    return out


def rail_lash(a, s):
    """The rear cell's lashing: an open C-run over the rear rail (top, back, bottom) at the main post's centre, both
    ends turned square into the post's back face."""
    x = s * (MP[0] + MP[1]) / 2
    r, off = 0.12, 0.12 - P.SINK
    (y0, y1), (z0, z1) = RAIL["y"], RAIL["z"]
    yp = MP[2] - END_SINK
    cut = 0.6 * off
    path = [(yp, z1 + off), (y1 - 0.08, z1 + off), (y1 + cut, z1 + cut), (y1 + off, z1 - 0.08), (y1 + off, z0 + 0.08),
            (y1 + cut, z0 - cut), (y1 - 0.08, z0 - off), (yp, z0 - off)]
    return P.rope(a, [Vector((x, y, z)) for y, z in path], r, ROPE, ROPE_DEEP, sides=5, twist=True, up=(1, 0, 0),
                  name="lash", kind="rope_lash")


def wrap_sections(x, bolster):
    if bolster:
        return rect_pts(*BOL["y"], *BOL["z"], BOL["ch"], x)
    return rect_pts(-LIN["hy"], LIN["hy"], *LIN["z"], LIN["ch"], x)


BAND_X = {"mid": 5.20, "outer": 7.00}    # the front cell's rope bands over lintel and bolster
RB = 0.19                                # their rope radius (the sheet's bands are about 0.45 wide)


def band(a, s, which, r=RB):
    """A rope band strapped over the lintel and bolster (open, both ends turned square into the timber, 0.04 deep):
    "outer" runs from the bolster's front face up over the lintel's top and down to the bolster's back face; "mid"
    (under the cap block) starts in the lintel's front face just under the cap and runs down over the bolster's front.
    Corners cut at 45 deg (two bends instead of one square mitre)."""
    x = s * BAND_X[which]
    off, cut, e = r - P.SINK, 0.6 * (r - P.SINK), 0.08
    (yf, yb), (zb, zt) = BOL["y"], BOL["z"]
    hy, (lz0, lz1) = LIN["hy"], LIN["z"]
    front = [(-hy - off, zt + off + 0.02), (yf + e, zt + off), (yf - cut, zt + cut), (yf - off, zt - e),
             (yf - off, zb + 0.15), (yf + END_SINK, zb + 0.15)]
    if which == "mid":
        zs = CAP["z0"] - r + 0.04            # its top 0.04 into the cap's underside
        path = [(-hy + END_SINK, zs), (-hy - off, zs)] + front
    else:
        top = [(-hy - off, lz1 - e), (-hy - cut, lz1 + cut), (-hy + e, lz1 + off), (hy - e, lz1 + off),
               (hy + cut, lz1 + cut), (hy + off, lz1 - e), (hy + off, zt + off + 0.02)]
        back = [(yb + cut, zt + cut), (yb + off, zt - e), (yb + off, zb + 0.15), (yb - END_SINK, zb + 0.15)]
        path = list(reversed(front)) + top + back
    return P.rope(a, [Vector((x, y, z)) for y, z in path], r, ROPE, ROPE_DEEP, sides=4, twist=True, up=(1, 0, 0),
                  name=f"band_{which}", kind="rope_band")


def lintel_wraps(a, sides=(-1, 1), which=("in", "out")):
    out = []
    for s in sides:
        for k in which:
            x = s * WRAP_X[k]
            pts = wrap_sections(x, k == "out")
            c = sum(pts, Vector()) / len(pts)
            out.append(rope_loop(a, pts, c, (1, 0, 0), (0, 1, 0), RW, 12, f"wrap_{k}{'lr'[s > 0]}"))
    return out


# ---- leaves ------------------------------------------------------------------------------------------------------------
def leaf_matrix(s, yaw=0.0):
    """Right-leaf build coordinates -> side s, swung `yaw` deg about its hinge axis."""
    ax = Vector((s * XP, YP, 0.0))
    m = Matrix.Translation(ax) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Translation(-ax)
    if s < 0:
        m = m @ Matrix.Scale(-1.0, 4, (1.0, 0.0, 0.0))
    return m


def plank_spans():
    w = (PL_X1 - PL_X0 - 3 * PL_GAP) / 4
    return [(PL_X0 + k * (w + PL_GAP), PL_X0 + k * (w + PL_GAP) + w) for k in range(4)]


def leaf_geo(a, knuckles=True, keeper=True):
    """The right leaf in build coordinates: four planks, front and back straps with end plates and bolts, the ring
    handle near the meeting edge, the latch keeper on the back, the hinge knuckles on the axis."""
    out = []
    for k, (x0, x1) in enumerate(plank_spans()):
        xc = (x0 + x1) / 2
        p = P.plank(a, (xc, 0.0, LEAF_Z0), (xc, 0.0, PL_TOPS[k]), x1 - x0, PL_T, mix(PLANK, TIMBER_DEEP, 0.08 * (k % 2)),
                    ch=0.06, up=(0, -1, 0), cap_keys=(None, mix(PLANK, TIMBER_END, 0.35)), name=f"plank{k}",
                    kind="plank")
        P.texture(a, p.vs, 0.03, P.seed(f"plank{k}"), scale=0.5)
        out.append(p)
    yf, yb = -PL_T / 2, PL_T / 2
    for tag, (bz0, bz1, pz0, pz1) in STRAPS.items():
        # front: body and the end plate near the hinge side (plate a little prouder), bolts on both
        out.append(P.box(a, (F_BODY[0], yf - ST_T, bz0), (F_BODY[1], yf + 0.005, bz1), IRON, name=f"fstrap_{tag}",
                         kind="iron", amp=0.03))
        out.append(P.box(a, (F_PLATE[0], yf - PLATE_T, pz0), (F_PLATE[1], yf + 0.005, pz1), IRON,
                         name=f"fplate_{tag}", kind="iron", amp=0.03))
        zc = (bz0 + bz1) / 2
        for i, bx in enumerate(BOLT_X):
            P.bolt(a, (bx, yf - ST_T, zc), (0, -1, 0), (0, 0, 1), IRON, h=0.075, proud=0.05, name=f"fbolt_{tag}{i}")
        for i, bz in enumerate((pz0 + 0.20, pz1 - 0.20)):
            P.bolt(a, ((F_PLATE[0] + F_PLATE[1]) / 2, yf - PLATE_T, bz), (0, -1, 0), (0, 0, 1), IRON, h=0.075,
                   proud=0.05, name=f"fpbolt_{tag}{i}")
        # back: the hinge strap (body to the hinge axis, into the knuckle) and its end plate
        out.append(P.box(a, (R_BODY[0], yb - 0.005, bz0), (R_BODY[1], yb + ST_T, bz1), IRON, name=f"rstrap_{tag}",
                         kind="iron", amp=0.03))
        out.append(P.box(a, (R_PLATE[0], yb - 0.005, pz0), (R_PLATE[1], yb + ST_T, pz1), IRON, name=f"rplate_{tag}",
                         kind="iron", amp=0.03))
        for i, bx in enumerate(BOLT_X):
            P.bolt(a, (bx, yb + ST_T, zc), (0, 1, 0), (0, 0, 1), IRON, h=0.075, proud=0.05, name=f"rbolt_{tag}{i}")
        if knuckles:
            P.pole(a, (XP, YP), zc - KNUCKLE["h"], zc + KNUCKLE["h"], KNUCKLE["r"], IRON, sides=6,
                   name=f"knuckle_{tag}", kind="iron")
    # ring handle: a ring hanging flat on the planks from a round boss
    rx, rz, R_, r_ = RING["x"], RING["z"], RING["R"], RING["r"]
    yr = yf - 0.005 - r_
    ring = [Vector((rx + R_ * math.sin(2 * math.pi * k / 8), yr, rz + R_ * math.cos(2 * math.pi * k / 8)))
            for k in range(8)]
    P.tube(a, ring, r_, 4, True, IRON, up=(0, 1, 0), name="ring", kind="iron", amp=0.03)
    bz = rz + R_ + r_ + 0.12 - 0.015
    P.log(a, (rx, yf + 0.005, bz), (rx, yf - 0.16, bz), 0.12, IRON, sides=6, up=(0, 0, 1), name="ring_boss",
          kind="iron", amp=0.03)
    if keeper:
        # latch keeper on the back: a plate on the planks, a lip the bar rests on, an upright behind the bar
        k0, k1 = LATCH["keep"]
        zl = LATCH["z"] - LATCH["r"] + 0.01
        P.box(a, (k0, yb - 0.005, zl - 0.30), (k1, yb + 0.07, zl + 0.40), IRON, name="keep_plate", kind="iron",
              amp=0.03)
        P.box(a, (k0 + 0.03, yb + 0.065, zl - 0.14), (k1 - 0.03, LATCH["y"] + LATCH["r"] + 0.09, zl), IRON,
              name="keep_lip", kind="iron", amp=0.03)
        yo = LATCH["y"] + LATCH["r"] + 0.012
        P.box(a, (k0 + 0.03, yo, zl - 0.005), (k1 - 0.03, yo + 0.075, zl + 0.30), IRON, name="keep_up", kind="iron",
              amp=0.03)
    return out


def leaf(a, s, yaw=0.0, **kw):
    with P.frame(leaf_matrix(s, yaw), f"door{'lr'[s > 0]}_"):
        return leaf_geo(a, **kw)


def latch_bar(a):
    """The drop bar across both leaves' keepers (closed state), with knobs at both ends."""
    x, y, z, r = LATCH["x"], LATCH["y"], LATCH["z"], LATCH["r"]
    P.log(a, (-x, y, z), (x, y, z), r, TIMBER, sides=8, end_key=TIMBER_END, name="latch", kind="latch")
    for s in (-1, 1):
        q0 = Vector((s * (x + 0.003), y, z))
        P.log(a, q0, q0 + Vector((s * 0.16, 0, 0)), r + 0.06, TIMBER, sides=8, end_key=TIMBER_END,
              name=f"latch_knob{s:+d}", kind="latch")


# ---- hinge blocks ------------------------------------------------------------------------------------------------------
def hinge_block(a, s, zc, tag):
    """The hinge block on the main post's inner face: an iron plate (sunk 0.02) carrying two barrels on the hinge axis,
    above and below the leaf's knuckle (0.004 apart), and the pin's head on the top barrel."""
    h, kh = 0.62, KNUCKLE["h"] + 0.004
    x0, x1 = xr(s, XI - 0.06, XI + 0.02)
    P.box(a, (x0, 0.14, zc - h), (x1, 0.50, zc + h), IRON, name=f"hplate_{tag}", kind="iron", amp=0.03)
    P.pole(a, (s * XP, YP), zc + kh, zc + h, KNUCKLE["r"], IRON, sides=6, name=f"hbarrel_{tag}_t", kind="iron")
    P.pole(a, (s * XP, YP), zc - h, zc - kh, KNUCKLE["r"], IRON, sides=6, name=f"hbarrel_{tag}_b", kind="iron")
    P.pole(a, (s * XP, YP), zc + h - 0.005, zc + h + 0.08, 0.075, IRON, sides=6, name=f"hpin_{tag}", kind="iron")


# ---- lanterns and banner -------------------------------------------------------------------------------------------------
HALO = {"emitters": [{"name": "Halo", "texture": "glow_soft", "color": ["#FFC23A", "#FF9A1E"], "size": [1.2, 1.5],
                      "transparency": [0.65, 1.0], "lifetime": [1.0, 1.5], "rate": 2, "speed": [0, 0.05], "spread": 0,
                      "light_emission": 1.0}],
        "light": {"color": "#FFB347", "brightness": 1.0, "range": 10, "flicker": True}}
GLASS_DZ = LANT["plate"] + LANT["gh"] / 2


def lantern(a, x, y=LANT_Y, z=LANT_BOT, hook_top=BOL["z"][0], tag="lantern"):
    """P.lantern (dark iron, Neon glass) hung from an iron hook sunk 0.02 into the bolster's underside."""
    lt = P.lantern(a, (x, y, z), LANT_IRON, GLOW, ring_axis=(1, 0, 0), name=tag, **LANT)
    top = lt["ring_top"]
    P.tube(a, [Vector((x, y, hook_top + 0.02)), Vector((x, y, (hook_top + top.z) / 2)), top - Vector((0, 0, 0.035))],
           0.05, 4, False, LANT_IRON, up=(1, 0, 0), name=f"{tag}_hook", kind="lmetal", amp=0.03)
    P.GEO.setdefault("lanterns", {})[tag] = {"glass": [round(v, 3) for v in lt["glass"]], "ring_top": round(top.z, 3)}
    return lt


def knob(a, c, r, name):
    """(m069) A low-poly ball on the rod's axis (X): two poles and three rings of six, as a hull."""
    c = Vector(c)
    pts = [c + Vector((r, 0, 0)), c - Vector((r, 0, 0))]
    for k, xf in enumerate((-0.6, 0.0, 0.6)):
        rr = r * math.sqrt(1 - xf * xf)
        for j in range(6):
            th = 2 * math.pi * (j + 0.5 * k) / 6
            pts.append(c + Vector((xf * r, rr * math.cos(th), rr * math.sin(th))))
    return P.hull(a, pts, TIMBER_END, name=name, kind="knob", amp=0.03)


def _diamond_ring(a, cx, cz, hw, hh, line, y0, y1, name):
    """(m069) A diamond outline slab (outer half sizes hw x hh, `line` wide along x) between y0 and y1."""
    k = line / hw
    outer = [(cx, cz + hh), (cx + hw, cz), (cx, cz - hh), (cx - hw, cz)]
    inner = [(cx, cz + hh * (1 - k)), (cx + hw * (1 - k), cz), (cx, cz - hh * (1 - k)), (cx - hw * (1 - k), cz)]
    pts = [Vector((x, y0, z)) for x, z in outer + inner] + [Vector((x, y1, z)) for x, z in outer + inner]
    faces = []
    for i in range(4):
        i1 = (i + 1) % 4
        faces += [[i, i1, 4 + i1, 4 + i], [12 + i, 12 + i1, 8 + i1, 8 + i], [i1, i, 8 + i, 8 + i1],
                  [4 + i, 4 + i1, 12 + i1, 12 + i]]
    return P.shell(a, pts, faces, CREAM, name=name, kind="emblem", amp=0.02)


def banner(a, s, y=LANT_Y):
    """(m069 recipe) The rod (knobbed ends) under the bolster, a dark-red hem sleeve round it, the red swallowtail
    cloth with two cream edge stripes and the cream double diamond on its front face."""
    x0, x1 = xr(s, *ROD["x"])
    P.log(a, (x0, y, ROD_Z), (x1, y, ROD_Z), ROD["r"], TIMBER_END, sides=8, end_key=TIMBER_END, name="rod",
          kind="rod")
    for sg, xe in ((-1, x0), (1, x1)):
        knob(a, (xe + sg * (ROD["knob"] - 0.035), y, ROD_Z), ROD["knob"], f"knob{sg:+d}")
    c0, c1 = xr(s, *CLOTH["x"])
    P.sleeve(a, (c0 - 0.04, y, ROD_Z), (c1 + 0.04, y, ROD_Z), SLEEVE_IN, SLEEVE_IN + SLEEVE_T, BANNER_DEEP, sides=8,
             name="hem", kind="hem", amp=0.02)
    top = ROD_Z - SLEEVE_IN - 0.015
    xm = (c0 + c1) / 2
    outline = [(c0, top), (c1, top), (c1, CLOTH["tips"]), (xm, CLOTH["notch"]), (c0, CLOTH["tips"])]
    yf, yb = y - CLOTH["t"] / 2, y + CLOTH["t"] / 2
    cloth = P.ext(a, outline, yf, yb, BANNER, to3=lambda u, v, w: Vector((u, w, v)), name="cloth", kind="banner",
                  amp=0.02)
    P.texture(a, cloth.vs, 0.02, P.seed("cloth"), scale=0.4)
    e0, e1 = yf + 0.005, yf - 0.015
    for i, (hw, hh, line) in enumerate(EMB["rings"]):
        _diamond_ring(a, xm, EMB["z"], hw, hh, line, e0, e1, f"emblem{i}")
    zt = ROD_Z - SLEEVE_IN - SLEEVE_T - 0.06
    for sg, xe in ((1, c0), (-1, c1)):
        xa, xb = sorted((xe + sg * STRIPE_IN, xe + sg * (STRIPE_IN + STRIPE_W)))
        P.ext(a, [(xa, STRIPE_Z0), (xb, STRIPE_Z0), (xb, zt), (xa, zt)], e1, e0, CREAM,
              to3=lambda u, v, w: Vector((u, w, v)), name=f"stripe{sg:+d}", kind="emblem", amp=0.02)


# ---- rock and foliage -------------------------------------------------------------------------------------------------------
def rock_points(size, seed_):
    """(m069) A squat faceted boulder: foot ring on z 0, waist, shoulder and a broken top, jittered."""
    r = P.rng(f"rock{seed_}")
    w, d, h = size[0] * 1.08, size[1] * 1.08, size[2] * 1.03
    pts = []
    for zf, rf, n, rot in ((0.0, 0.94, 6, 0.0), (0.45, 1.0, 6, 0.5), (0.80, 0.80, 5, 0.2), (1.0, 0.52, 4, 0.9)):
        off = rot + r.uniform(-0.15, 0.15)
        for k in range(n):
            th = off + 2 * math.pi * k / n + r.uniform(-0.16, 0.16)
            rr = rf * r.uniform(0.90, 1.0)
            z = 0.0 if zf == 0.0 else h * zf * r.uniform(0.96, 1.0)
            pts.append(Vector((w / 2 * rr * math.cos(th), d / 2 * rr * math.sin(th), z)))
    return pts


def _hull_tris(pts):
    import bmesh
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    cos = [v.co.copy() for v in bm.verts]
    idx = {v: i for i, v in enumerate(bm.verts)}
    tris = [[idx[v] for v in f.verts] for f in bm.faces]
    bm.free()
    return cos, tris


def rock_place(pts, cx, tree):
    """(m069) Slide the rock from the front toward the gate until it meets it (bisection to 0.002); returns its y."""
    cos, tris = _hull_tris(pts)

    def hits(y):
        t = BVHTree.FromPolygons([c + Vector((cx, y, 0)) for c in cos], tris)
        return bool(t.overlap(tree))
    far, near = -4.0, 0.0
    for _ in range(30):
        mid = (far + near) / 2
        if hits(mid):
            near = mid
        else:
            far = mid
    return far - 0.002


def rock(a, s, tree=None, name="rock", cx=None):
    pts = rock_points(ROCK["size"], ROCK["seed"] + (s > 0))
    if s < 0:
        pts = [Vector((-p.x, p.y, p.z)) for p in pts]
    cx = s * ROCK["x"] if cx is None else cx
    y = rock_place(pts, cx, tree) if tree is not None else 0.0
    p = P.hull(a, [q + Vector((cx, y, 0)) for q in pts], STONE, name=name, kind="rock", amp=0.04)
    P.paint(a, [f for f in p.fs if f.is_valid and f.calc_center_median().z < 0.35], mix(STONE, STONE_DARK, 0.5))
    P.texture(a, p.vs, 0.05, ROCK["seed"], scale=0.9)
    P.GEO.setdefault("rocks", {})[name] = [round(cx, 3), round(y, 3)]
    return p, y


def solid_tree(a):
    """A BVH of everything built so far (build frame)."""
    a.bm.verts.ensure_lookup_table()
    return BVHTree.FromBMesh(a.bm)


LEAF_S = dict(P.IVY, leaf_ct=0.45)       # the ivy's tent (rise 0.22: a lower tent turns edge-on in the 5 deg sweep)
# the sheet's broad rounded leaf (the ivy's five-point outline reads as spiky stars), same eight points, tip first
LEAF_OVAL = ((0.0, 1.0), (0.30, 0.86), (0.46, 0.55), (0.36, 0.18), (0.0, 0.0), (-0.36, 0.18), (-0.46, 0.55),
             (-0.30, 0.86))


def leaf_points(N, d, nL, size, s=LEAF_S):
    """P.leaf_points with the broad outline: a low tent, its top centre raised rise x size, the tip curled back."""
    x = Vector(d).cross(Vector(nL)).normalized()
    nL = x.cross(Vector(d)).normalized()
    d = Vector(d)
    out = [N + (x * u + d * v) * size + nL * ((s["fold"] * abs(u) - s["curl"] * v * v) * size) for u, v in LEAF_OVAL]
    c = N + d * s["leaf_ct"] * size + nL * (-s["curl"] * s["leaf_ct"] ** 2 * size)
    return out + [c + nL * s["rise"] * size, c - nL * 0.03 * size]


def clump(a, c, n, size, seed_, name, tree=None):
    """A ground rosette of tent leaves (P.leaf_points): n leaves whose blades rise 30-50 deg radially out from a small
    ring round c, each rolled about its midrib (so the clump reads from every azimuth, STAGES' 5 deg sweep), lifted
    so its lowest point sits 0.005 over the ground; a leaf that would sink more than 0.04 into the solid tree (rock,
    posts) is pushed out radially, or left out."""
    rg = random.Random(seed_)
    ph = rg.uniform(0.0, 2 * math.pi)
    tones = [LEAF_L, LEAF_G, LEAF_D]
    made, done = [], []
    for k in range(n):
        phi = ph + 2 * math.pi * k / n + rg.uniform(-0.15, 0.15)
        # alternate steep and low blades, so neighbours part vertically instead of sinking into each other
        tau = math.radians(rg.uniform(58.0, 70.0) if k % 2 == 0 else rg.uniform(38.0, 48.0))
        radial = Vector((math.cos(phi), math.sin(phi), 0.0))
        d = Vector((radial.x * math.cos(tau), radial.y * math.cos(tau), math.sin(tau)))
        lat = Vector((-math.sin(phi), math.cos(phi), 0.0))
        nL = d.cross(lat).normalized()
        rho = math.radians(rg.uniform(14.0, 30.0)) * (1 if rg.random() < 0.5 else -1)
        nL = (nL * math.cos(rho) + d.cross(nL) * math.sin(rho)).normalized()
        sz = size * rg.uniform(0.85, 1.1)
        key = tones[0] if k % 2 == 0 else tones[2] if k == n - 1 else tones[1]
        placed = None
        for push in (0.0, 0.06, 0.12, 0.18, 0.24, 0.30, 0.36):
            N = Vector((c[0], c[1], 0.0)) + radial * (0.18 * sz + push)
            pts = leaf_points(N, d, nL, sz)
            dz = 0.005 - min(p.z for p in pts)
            pts = [p + Vector((0, 0, dz)) for p in pts]
            if tree is not None and _leaf_depth(pts, tree) > 0.04:
                continue
            if any(_leaf_depth(pts, _leaf_tree(q)) > 0.04 or _leaf_depth(q, _leaf_tree(pts)) > 0.04 for q in done):
                continue
            placed = pts
            break
        if placed is None:
            continue
        done.append(placed)
        nm = f"{name}_{k}"
        p = P.shell(a, placed, P.LEAF_POLYS, key, name=nm, kind="leaf", amp=0.04)
        P.LEAVES.append({"name": p.name, "n": [round(x, 5) for x in nL], "kind": "leaf", "size": sz})
        made.append(p)
    return made


def _leaf_tree(pts):
    """A BVH of one leaf's shell, wound outward (signed volume positive)."""
    vol = sum(pts[f[0]].dot(pts[f[1]].cross(pts[f[2]])) for f in P.LEAF_POLYS)
    polys = P.LEAF_POLYS if vol > 0 else [list(reversed(f)) for f in P.LEAF_POLYS]
    return BVHTree.FromPolygons(pts, polys)


def _leaf_depth(pts, tree):
    """How deep the leaf's points (verts, face centres, edge midpoints) sink into the closed solids of tree."""
    samp = list(pts)
    for f in P.LEAF_POLYS:
        samp.append(sum((pts[i] for i in f), Vector()) / len(f))
        for j in range(len(f)):
            samp.append((pts[f[j]] + pts[f[(j + 1) % len(f)]]) / 2)
    d = 0.0
    for q in samp:
        loc, nrm, fi, dist = tree.find_nearest(q)
        if loc is not None and (q - loc).dot(nrm) < 0 and P.parity_in(tree, q):
            d = max(d, dist)
    return d


def prune_leaves(a, n0, l0, lim=0.045):
    """(m070) Drop the later of every pair of leaves (built since vertex n0 / leaf register entry l0) that sink more
    than lim into each other. Returns the names dropped."""
    import bmesh
    bm = a.bm
    bm.verts.ensure_lookup_table()
    new = list(bm.verts[n0:])
    seen, comps = set(), []
    for v in new:
        if v in seen:
            continue
        st, comp = [v], []
        seen.add(v)
        while st:
            x = st.pop()
            comp.append(x)
            for e in x.link_edges:
                w = e.other_vert(x)
                if w not in seen:
                    seen.add(w)
                    st.append(w)
        comps.append(comp)
    leaves = [c for c in comps if len(c) == 10]
    lnames = [l["name"] for l in P.LEAVES[l0:]]
    if len(leaves) != len(comps) or len(leaves) != len(lnames):
        raise RuntimeError(f"prune_leaves: {len(comps)} shells, {len(leaves)} leaf shells, {len(lnames)} names")

    def info(c):
        fs = list({f for v in c for f in v.link_faces})
        cos = [v.co.copy() for v in c]
        lo = Vector((min(p.x for p in cos), min(p.y for p in cos), min(p.z for p in cos)))
        hi = Vector((max(p.x for p in cos), max(p.y for p in cos), max(p.z for p in cos)))
        idx = {v: i for i, v in enumerate(c)}
        tree = BVHTree.FromPolygons(cos, [[idx[v] for v in f.verts] for f in fs])
        pts = cos + [f.calc_center_median() for f in fs] + \
            [(e.verts[0].co + e.verts[1].co) / 2 for e in {e for f in fs for e in f.edges}]
        return dict(lo=lo, hi=hi, tree=tree, pts=pts)
    I = [info(c) for c in leaves]

    def depth_in(s, t):
        A, Bt = I[s], I[t]
        if any(A["hi"][i] < Bt["lo"][i] or A["lo"][i] > Bt["hi"][i] for i in range(3)):
            return 0.0
        d = 0.0
        for p in A["pts"]:
            loc, nrm, fi, dist = Bt["tree"].find_nearest(p)
            if loc is not None and dist > lim and (p - loc).dot(nrm) < 0 and P.parity_in(Bt["tree"], p):
                d = max(d, dist)
        return d
    drop = set()
    for s in range(len(leaves)):
        for t in range(s + 1, len(leaves)):
            if s in drop or t in drop:
                continue
            if depth_in(s, t) > lim or depth_in(t, s) > lim:
                drop.add(t)
    gone = [lnames[s] for s in sorted(drop)]
    bmesh.ops.delete(bm, geom=[v for s in drop for v in leaves[s]], context="VERTS")
    P.PIECES[:] = [p for p in P.PIECES if p[1] not in gone]
    P.LEAVES[:] = [l for l in P.LEAVES if l["name"] not in gone]
    return gone


def foliage(a, tree):
    """Both sides' clumps, then one prune (BMesh reuses deleted vertex slots, so a prune must come after the last
    leaf is built)."""
    n0, l0 = len(a.bm.verts), len(P.LEAVES)
    for s in (-1, 1):
        for tag, (x, y), n, size, sd in CLUMPS:
            with P.frame(None, f"{'lr'[s > 0]}{tag}_"):
                clump(a, (s * x, y), n, size, sd + (s > 0) * 10, "leaf", tree=tree)
    return prune_leaves(a, n0, l0)


# ---- assemblies ------------------------------------------------------------------------------------------------------------
def pillar(a, s, bands=True):
    with P.frame(None, f"{'LR'[s > 0]}_"):
        main_post(a, s)
        outer_post(a, s)
        bolster(a, s)
        rear_rail(a, s)
        brace(a, s)
        collar(a, s)
        rail_lash(a, s)
        if bands:
            for which in BAND_X:
                band(a, s, which)


def gate_all(a, open_deg=0.0, dressing=True):
    lintel(a)
    for s in (-1, 1):
        pillar(a, s)
        with P.frame(None, f"{'LR'[s > 0]}_"):
            cap(a, s)
            for tag, zc in HINGE_ZC.items():
                hinge_block(a, s, zc, tag)
    lintel_wraps(a)
    for s in (-1, 1):
        leaf(a, s, yaw=-s * open_deg)
    if not open_deg:
        latch_bar(a)
    for s in (-1, 1):
        with P.frame(None, f"{'LR'[s > 0]}_"):
            banner(a, s)
            for i, x in enumerate(LANT_X):
                lantern(a, s * x, tag=f"lantern{i}")
    if dressing:
        tree = solid_tree(a)
        for s in (-1, 1):
            with P.frame(None, f"{'LR'[s > 0]}_"):
                rock(a, s, tree)
        P.GEO["leaves_pruned"] = foliage(a, solid_tree(a))


def hero_all(a):
    gate_all(a)


def open_all(a):
    gate_all(a, open_deg=OPEN_DEG)


def post_part(a):
    """One pillar (the left one): main and outer post, bolster, rear rail, brace, collar and lashing (the bands over
    the lintel stay with the hero)."""
    pillar(a, -1, bands=False)


def lintel_part(a):
    lintel(a)
    for s in (-1, 1):
        with P.frame(None, f"{'LR'[s > 0]}_"):
            cap(a, s)
    lintel_wraps(a, which=("in",))


def leaf_part(s):
    def fn(a):
        return leaf(a, s)
    return fn


def wrap_part(a):
    """The exploded view's rope coil: three touching twisted turns round a 1.70-square post section."""
    for i, z in enumerate(COLLAR_Z):
        sec = [Vector((u, v, z - COLLAR_Z[0] + RW)) for u, v in P.sec_rect(0.85, 0.85, POST_CH)]
        rope_loop(a, sec, (0.0, 0.0, z - COLLAR_Z[0] + RW), (0, 0, 1), (1, 0, 0), RW, 12, f"coil{i}",
                  kind="rope_turn")


def hinge_part(a):
    hinge_block(a, 1, 0.62, "hi")


def banner_part(a):
    banner(a, 1)


def lantern_part(a):
    lantern(a, 0.0, 0.0, 0.0, hook_top=BOL["z"][0] - LANT_BOT)


def rock_part(a):
    rock(a, 1, None, cx=0.0)
    tree = solid_tree(a)
    n0, l0 = len(a.bm.verts), len(P.LEAVES)
    for tag, (x, y), n, size, sd in (("out", (2.1, 0.3), 6, 1.10, 7211), ("in", (-2.05, -0.4), 6, 0.95, 7212)):
        with P.frame(None, f"{tag}_"):
            clump(a, (x, y), n, size, sd, "leaf", tree=tree)
    P.GEO["leaves_pruned"] = prune_leaves(a, n0, l0)


PARTS = ((POST_P, post_part), (LINTEL_P, lintel_part), (LEAF_LP, leaf_part(-1)), (LEAF_RP, leaf_part(1)),
         (LATCH_P, latch_bar), (WRAP_P, wrap_part), (HINGE_P, hinge_part), (BANNER_P, banner_part),
         (LANTERN_P, lantern_part), (ROCK_P, rock_part))

NOTES = {
    HERO: "Timber gate (sheet 072), closed: two pillars (1.70-square main post, outer post, cap block, front bolster, "
          "rear rail and diagonal brace, rope collar and lashing), a 16.5 lintel with rope wraps, two plank leaves with "
          "iron straps, bolts, ring handles and hinge knuckles on hinge blocks (axes |x| 4.20, y 0.30; open 90 deg "
          "inward), a latch bar on the back, four Neon lanterns (heat_glow), two red banners with the cream diamond, "
          "rock bases with leaf clumps. Opening 8.70 between the posts, 8.22 under the lintel (7.40 under the bolster "
          "ends); open, 7.2 clear between the leaves. Hinges stored as m072_hinges.",
    POST_P: "Upright Post: main post 1.70 sq to 8.24, outer post, front bolster, rear rail, diagonal brace, three-turn "
            "rope collar and the rail lashing",
    LINTEL_P: "Top Beam (Lintel): 16.5 x 1.30 x 1.44 beam, the two cap blocks and the inner rope wraps",
    LEAF_LP: "Left Gate Leaf: four planks, iron straps with bolts both faces, ring handle, latch keeper, hinge knuckles; "
             "origin on the hinge axis (swing about local Z, opens +90 deg)",
    LEAF_RP: "Right Gate Leaf: four planks, iron straps with bolts both faces, ring handle, latch keeper, hinge knuckles; "
             "origin on the hinge axis (swing about local Z, opens -90 deg)",
    LATCH_P: "Latch Bar: round drop bar with knobbed ends, rests in the leaves' keepers",
    WRAP_P: "Rope Wrap: three-turn twisted rope coil for a 1.70-square post",
    HINGE_P: "Hinge Block & Pin: iron plate, two barrels on the pin axis, pin head",
    BANNER_P: "Banner: knobbed rod, hem sleeve, red swallowtail with cream stripes and double diamond",
    LANTERN_P: "Lantern: dark iron lantern, Neon amber glass, hanging ring and hook (heat_glow halo)",
    ROCK_P: "Rock Base: grey faceted rock with two leaf clumps",
}
COLLISION = {HERO: "precise", POST_P: "hull", LINTEL_P: "box", LEAF_LP: "box", LEAF_RP: "box", LATCH_P: "hull",
             WRAP_P: "none", HINGE_P: "none", BANNER_P: "none", LANTERN_P: "none", ROCK_P: "hull"}
BUDGETS = {HERO: 6000}
TARGET_SIZE = None
VIEWS = {"f34_sheet": (-24, 18), "r34_sheet": (-150, 16), "front_sheet": (0, 0), "side_sheet": (90, 0),
         "rear_sheet": (180, 0), "top_sheet": (0, 89.9), "open_sheet": (-20, 12, "open")}
VARIANTS = {"open": open_all}
# exploded view, laid out like the sheet's panel: post at the left, lintel up top, the leaves in the middle, the small
# parts to their right, the rock base last (offsets of each part's origin)
EXPLODED = {POST_P: (0.0, 0.0, 0.0), BANNER_P: (5.0, -1.0, 2.0), LANTERN_P: (7.6, -1.0, 4.0),
            LINTEL_P: (15.0, 2.0, 9.5), LEAF_LP: (9.0, 0.0, 0.0), LEAF_RP: (19.5, 0.0, 0.0),
            LATCH_P: (23.0, 0.0, 7.0), WRAP_P: (23.0, 0.0, 4.2), HINGE_P: (23.0, 0.0, 1.0), ROCK_P: (28.5, 0.0, 0.0)}
FX = {HERO: [("heat_glow", (s * x, LANT_Y, LANT_BOT + GLASS_DZ), HALO) for s in (-1, 1) for x in LANT_X],
      LANTERN_P: [("heat_glow", (0.0, 0.0, GLASS_DZ), HALO)]}
WALK = {"paths": [[(0.0, -7.0), (0.0, 7.0)]], "ride": False}
VERIFY = dict(cls="structure", foliage={"keys": ("leaf",), "objs": [HERO, ROCK_P]},
              sockets={HERO: ["heat_glow"] * 4, LANTERN_P: ["heat_glow"]},
              stored={HERO: ["m072_hinges"], LEAF_LP: ["m072_hinge"], LEAF_RP: ["m072_hinge"]})
COMPARE = {"f34": {"box": (35, 125, 515, 455), "view": VIEWS["f34_sheet"][:2]},
           "r34": {"box": (565, 115, 1000, 455), "view": VIEWS["r34_sheet"][:2]},
           "front": {"box": (15, 540, 278, 712), "view": (0, 0)},
           "side": {"box": (350, 540, 428, 712), "view": (90, 0)},
           "rear": {"box": (500, 540, 745, 712), "view": (180, 0)},
           "top": {"box": (800, 575, 1000, 675), "view": (0, 89.9)}}
WAIVED = ("origin not at the bottom centre", "origin is not centred on the footprint")


def hinge_axes():
    """{side: (axis bottom (build frame), open yaw)}: the leaves open inward (+Y)."""
    return {s: (Vector((s * XP, YP, LEAF_Z0)), -s * OPEN_DEG) for s in (-1, 1)}


def after(objs):
    """Leaf parts: origin moved from the bbox bottom centre onto the hinge axis (main session ruling), the mesh kept
    in place; hinge records on the hero and the leaves."""
    ax = hinge_axes()
    h = objs[HERO]
    h["m072_hinges"] = {("left" if s < 0 else "right"): {"axis_bottom": [round(c, 4) for c in MODEL.local(h, p)],
                                                         "closed_yaw": 0.0, "open_yaw": yaw}
                        for s, (p, yaw) in ax.items()}
    for name, s in ((LEAF_LP, -1), (LEAF_RP, 1)):
        o = objs[name]
        p, yaw = ax[s]
        shift = p - Vector(o[MODEL.OFF])
        for v in o.data.vertices:
            v.co -= shift
        o.data.update()
        o.location = o.location + shift
        o[MODEL.OFF] = list(p)
        o["m072_hinge"] = {"axis_bottom": [0.0, 0.0, 0.0], "closed_yaw": 0.0, "open_yaw": yaw}
    bpy.context.view_layer.update()


def gate_check(objs):
    """The walk through the opening with the leaves open 90 deg (an open variant, built and checked, then removed),
    the clear width between the open leaves and the heights over the walk lane."""
    import importlib
    import kit_verify as V
    importlib.reload(V)
    h = objs[HERO]
    o = MODEL.variant(h, "opencheck", open_all)
    try:
        res = V.run([o], cls="structure", walk=dict(WALK, obj=o.name), kit_check=False)
        walk = res.get("walk")
        pr = [p for p in res["problems"] if ": walk" in p]
        me = o.data
        tree = BVHTree.FromPolygons([o.matrix_world @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])

        def ray(p, d):
            q = tree.ray_cast(MODEL.at(o, p), Vector(d))
            return round(q[3], 3) if q[0] is not None else None
        clear = []
        for z in (0.5, 2.0, 3.83, 5.6, 7.0):
            l_, r_ = ray((0.0, 1.5, z), (-1, 0, 0)), ray((0.0, 1.5, z), (1, 0, 0))
            if l_ is not None and r_ is not None:
                clear.append((z, round(l_ + r_, 3)))
        up = {x: ray((x, 0.0, 0.5), (0, 0, 1)) for x in (0.0, 2.0, 3.6, 4.1)}
        rep = {"walk": walk, "open_clear_width": clear, "headroom": {k: (round(v + 0.5, 3) if v else None)
                                                                     for k, v in up.items()}}
        if clear and min(c for _, c in clear) < 3.6:
            pr.append(f"{HERO}: open clear width {min(c for _, c in clear)} under 3.6")
        return rep, pr
    finally:
        B.remove([o])


def build(render=True, close=False, spin=False):
    out = MODEL.run(hero=(HERO, hero_all), parts=PARTS, notes=NOTES, collision=COLLISION, budgets=BUDGETS,
                    target_size=TARGET_SIZE, fx=FX, views=VIEWS, variants=VARIANTS, exploded=EXPLODED,
                    close=CLOSE if close else None, verify=VERIFY, checks=[gate_check], after=after, render=render,
                    spin=spin)
    # ruled exception (main session): the leaf parts' origins sit on their hinge axes, not the bottom centre
    keep, waived = [], []
    for p in out.get("problems", []):
        (waived if p.startswith((LEAF_LP + ":", LEAF_RP + ":")) and any(w in p for w in WAIVED) else keep).append(p)
    out["problems"], out["waived"] = keep, waived
    return out


CLOSE = {"hinge_cu": dict(at=(XP, YP, HINGE_ZC["hi"]), r=1.1, az=-143, el=10),
         "pillar_cu": dict(at=(-6.6, -1.0, 7.2), r=2.8, az=-30, el=12),
         "joint_cu": dict(at=(-5.2, 0.0, 9.3), r=2.0, az=-35, el=20),
         "foliage_cu": dict(at=(-6.6, -2.0, 1.0), r=2.2, az=-25, el=15)}


def preview(names=("f34_sheet", "front_sheet", "rear_sheet")):
    return MODEL.preview(HERO, VIEWS, names, variants=VARIANTS)


def compare(cells=None, out_dir=None, height=360):
    import importlib
    import compare as C
    importlib.reload(C)
    return C.compare(NUM, {k: COMPARE[k] for k in (cells or COMPARE)}, out_dir=out_dir, height=height)
