"""076 Watchtower (references/076.png, remade sheet; no earlier builder) on the shared library (kit_parts / kit_build):
a climbable four-post timber lookout. See art/blender/renders/models/M076/M076_spec.md.

    import importlib, kit_parts, kit_build, m076
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m076); m076.build()

Build frame (studs): front -Y (banner and ladder), +X right, ground z 0, the tower centred on x 0 / y 0, mirror-symmetric
about both axes except the front (ladder, banner, railing gap) and the braces (sides and rear only).
- Four 1.0-square posts on tapered stone footings lean in toward the centre: centre |x| = |y| = c(z), 3.75 at the
  footing top (1.40) to 3.25 at the post top (13.47, inside the corner cap). Each post is three segments joined by two
  block collars (block joinery): the deck collar (6.30-7.55, 1.30 square) and the rail collar (10.20-10.80, 1.20
  square), each with round pegs on its two outer faces; pegs on the posts' outer faces at the lower girt.
- The lower storey: a girt on every face (2.30-2.90), dark vertical plank infill between girt and deck rim beam, an X
  brace of two boards (one over the other, a peg at the crossing) on the sides and rear, a centre leg under the side
  and rear girts.
- The deck: four rim beams between the deck collars (6.45-7.43, 1.19 deep) and six planks between them, plank top at
  7.40 (DECK). Railing on all sides (bottom rail, top rail to 10.70, three balusters); the front railing is split by the
  ladder gap (|x| < 1.55) with a newel post on each side.
- The roof: a straight four-sided canvas pyramid (one closed 0.12 slab, a soft dip along each face's middle) from a
  level eave at 13.62 to a flat apex at 17.27, its corners cut out for four block caps (a small block on each) that
  stand on the post tops at the canvas corners (inner face over the post axis, as the sheet's); a sloped post head
  carries the canvas over each post's inner half. A turned wood finial (octagonal base, neck, ball) on its flat top.
- The banner: a rod with ball knobs under the front rim beam, a red point-tipped cloth with a cream double diamond,
  hanging in front of the infill and behind the ladder.
- The ladder: two rails and seven rungs leaning at 75 deg from the ground (foot 2.0 in front of the deck edge) against
  the front rim beam at the centre, through the railing gap; its rails rise 2.40 over the deck as hand holds. Rung
  tops every 0.929 (the deck edge is the eighth step).
Every piece is its own closed shell (no booleans), seated 0.002-0.05 into what holds it.
Hero TimberWatchtower; parts ...Post, ...Brace, ...Railing, ...DeckFloor, ...CanvasRoof, ...RoofFinial, ...Banner,
...Ladder, ...Footing. Stages 5-6: nothing (the sheet: no lighting or effects).
"""
import math

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import kit_build as B
import kit_parts as P

NUM, TITLE = 76, "Watchtower"
HERO = "TimberWatchtower"
POST_P, BRACE_P, RAIL_P = HERO + "Post", HERO + "Brace", HERO + "Railing"
DECK_P, ROOF_P, FINIAL_P = HERO + "DeckFloor", HERO + "CanvasRoof", HERO + "RoofFinial"
BANNER_P, LADDER_P, FOOT_P = HERO + "Banner", HERO + "Ladder", HERO + "Footing"

TIMBER, TIMBER_END, TIMBER_DEEP, PLANK = "m076_timber", "m076_timber_end", "m076_timber_deep", "m076_plank"
CANVAS, CANVAS_DEEP = "m076_canvas", "m076_canvas_deep"
STONE, STONE_DEEP = "m076_stone", "m076_stone_deep"
BANNER, BANNER_DEEP, CREAM = "m076_banner", "m076_banner_deep", "m076_cream"

# key -> (hex, roughness, metal, emission, low specular). Stage 4 (spec "Stage 4"): sheet medians, calibrated; the
# canvas set by hand (calibration pulls cream toward salmon, m066).
PALETTE = {
    TIMBER: ("#B96825", 0.85, 0.0, 0.0, True),
    TIMBER_END: ("#D08A3E", 0.8, 0.0, 0.0, True),
    TIMBER_DEEP: ("#523018", 0.9, 0.0, 0.0, True),
    PLANK: ("#A65A26", 0.85, 0.0, 0.0, True),
    CANVAS: ("#DEB890", 0.95, 0.0, 0.0, True),
    CANVAS_DEEP: ("#BE9A74", 0.95, 0.0, 0.0, True),
    STONE: ("#A9A9AC", 0.92, 0.0, 0.0, True),
    STONE_DEEP: ("#86878D", 0.92, 0.0, 0.0, True),
    BANNER: ("#F0281C", 0.9, 0.0, 0.0, True),
    BANNER_DEEP: ("#8A1410", 0.9, 0.0, 0.0, True),
    CREAM: ("#F2E8D6", 0.9, 0.0, 0.0, True),
}
# calibration targets: the sheet's rendered medians (spec "Stage 4") and K.sample kinds
TARGETS = {TIMBER: ((0xCA, 0x69, 0x20), "brown"), PLANK: ((0xB7, 0x65, 0x2D), "brown"),
           TIMBER_DEEP: ((0x7C, 0x45, 0x21), "all"), STONE: ((0xAB, 0xAA, 0xA9), "all"),
           BANNER: ((0xE1, 0x24, 0x1B), "vivid")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)


def mix(k1, k2, t):
    return P.mix(k1, k2, t, step=0.05)


# ---- layout (spec "Brief": side cell at 17.8 px / stud, the R6 figure 89 px = 5 studs) -----------------------------
FT = 1.40                                # footing top
SEAT = 0.02
# roof first: the eave sets the post top (spec "Fix after R1": a straight pyramid, block caps at its corners)
CANVAS_T = 0.12
Z_EAVE, ZA = 13.62, 17.27                # canvas top at the (level) eave, at the flat apex
HC, RF = 4.05, 0.50                      # canvas half size; flat top inside RF
# the caps stand at the canvas corners as the sheet's (inner face over the post axis, 0.75 over the canvas, the rest
# outside it); the body is tall enough to hide the canvas' cut-out corner (14.40 at its inner corner)
CAP = dict(half=0.65, h=1.10, bev=0.12, top_half=0.35, top_h=0.20)
CAP["c"] = HC - 0.75 + CAP["half"]
CAP_Z = Z_EAVE - CANVAS_T - 0.05         # cap bottom, 0.05 under the eave's underside
CB, CT, E = 3.75, 3.25, CAP_Z + SEAT     # post centre |x| = |y| at the footing top, at the post top; post top
LEAN = (CB - CT) / (E - FT)              # 0.041 per stud (2.4 deg)
PH, PCH = 0.50, 0.06                     # post half width, edge chamfer
DECK = 7.40                              # plank top (the walk surface)
RIM = dict(z=(DECK - 0.95, DECK + 0.03), w=(-0.64, 0.55), ch=0.05)   # rim beams: their top 0.03 proud of the planks
GIRT = dict(z=(2.30, 2.90), w=(-0.25, 0.55), ch=0.05)
COLLARS = {"deck": (DECK - 1.10, DECK + 0.15, 0.65), "rail": (DECK + 2.80, DECK + 3.40, 0.60)}    # z0, z1, half
COLLAR_BEV = 0.08
INFILL_W, INFILL_N, INFILL_GAP = (-0.10, 0.10), 5, 0.025
BRACE_W = 0.60
BRACE_B, BRACE_A = (0.08, 0.28), (0.26, 0.46)                     # back board, front board (w from the post plane)
BRACE_FACES = ("R", "L", "B")
RAILS = {"bottom": (DECK + 0.35, DECK + 0.70, 0.17), "top": (DECK + 2.90, DECK + 3.30, 0.20)}  # z0, z1, half depth
BALUSTERS, BAL_H = (-1.30, 0.0, 1.30), 0.14
GAP_X = 1.55                             # the front railing gap |x| (newels outside it)
NEWEL = dict(x=(1.55, 1.91), hd=0.20, top=DECK + 3.45, bev=0.08)
DECK_PLANKS, PLANK_GAP, PLANK_T = 6, 0.03, 0.35
LEG = dict(hu=0.40, hv=0.30)             # centre legs under the girts (along the face, across)
FOOT = ((0.0, 1.15, 0.12), (1.02, 1.02, 0.11), (FT, 0.85, 0.09))  # (z, half, chamfer)
PEG = dict(r=0.15, h=0.12)

# roof: a straight four-sided canvas pyramid (top surface) with its corners cut out for the caps, caps, finial
# the canvas corners are cut out from here, 0.01 short of the caps' inner faces (seated, the caps' vertical edges
# would cross the thin canvas)
NOTCH = CAP["c"] - CAP["half"] - 0.01
S_FACE = 0.04                            # a soft dip along each face's middle (zero at the hips, apex and eave)
GRID = (0.0, RF, 1.25, 2.0, NOTCH, HC)
FIN = dict(base=0.42, base_h=0.30, neck=0.16, neck_h=0.24, ball=0.38)

# banner (behind the ladder, in front of the infill)
BAN = dict(x=1.40, t=0.08, side=DECK - 3.10, tip=DECK - 4.10)
ROD = dict(r=0.12, x=1.72, knob=0.17)
ROD_Z = RIM["z"][0] - ROD["knob"] + 0.01                  # the knobs' tops 0.01 into the rim beam's underside
SLEEVE_IN, SLEEVE_T = ROD["r"] / math.cos(math.pi / 8) + 0.008, 0.07
EMB = dict(z=DECK - 2.40, rings=((0.75, 1.05, 0.17), (0.32, 0.46, 0.11)))

# ladder (leaning against the front rim beam)
LAD = dict(angle=75.0, inner=1.20, rail_w=0.28, rail_d=0.32, above=2.40, rungs=7, rung=0.24)
RIM_TOP = RIM["z"][1]


def c(z):
    """A post's centre |x| = |y| at height z."""
    return CB - LEAN * (z - FT)


# the banner hangs 0.08 clear of the infill at its tip (the infill leans out going down)
BAN["y"] = -(c(BAN["tip"]) + INFILL_W[1] + BAN["t"] / 2 + 0.08)


def fpt(face, u, z, w):
    """A point on face F / B / L / R: u along the face (+X on F / B, +Y on L / R), z up, w outward from the posts'
    centre plane (which leans with the posts)."""
    d = c(z) + w
    return Vector({"F": (u, -d, z), "B": (u, d, z), "R": (d, u, z), "L": (-d, u, z)}[face])


def corners():
    return [(sx, sy) for sx in (-1, 1) for sy in (-1, 1)]


# ---- small pieces ----------------------------------------------------------------------------------------------------
def peg(a, p, n, name, r=PEG["r"], h=PEG["h"], key=TIMBER_END):
    """A round wooden peg head on a face: six-sided, a bevelled top, sunk 0.03. 32 tris."""
    n, p = Vector(n).normalized(), Vector(p)
    u = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = (u - n * u.dot(n)).normalized()
    v = n.cross(u)

    def ring(d, rr):
        return [p + n * d + (u * math.cos(math.pi / 6 + k * math.pi / 3) + v * math.sin(math.pi / 6 + k * math.pi / 3))
                * rr for k in range(6)]
    return P.prism(a, [ring(-0.03, r), ring(h - 0.04, r), ring(h, r - 0.05)], key, name=name, kind="peg", amp=0.03)


def block(a, cx, cy, z0, z1, half, key, bev, name, kind, top_key=None):
    """An axis block (collar, cap): chamfered vertical edges, its top edge bevelled `bev`. 44 tris."""
    sec, top = P.sec_rect(half, half, PCH), P.sec_rect(half - bev, half - bev, PCH * 0.6)
    rings = [[(cx + u, cy + v, z) for u, v in sec] for z in (z0, z1 - bev)]
    rings.append([(cx + u, cy + v, z1) for u, v in top])
    return P.prism(a, rings, key, band_keys=[None, mix(key, TIMBER_END, 0.4)], cap_keys=(None, top_key), name=name,
                   kind=kind)


def member(a, face, u0, u1, z0, z1, w0, w1, key, name, kind, ch=0.05):
    """A horizontal member along a face from u0 to u1 between heights z0, z1 and w0..w1 off the post plane (taken at
    its mid height)."""
    zm = (z0 + z1) / 2
    p0, p1 = fpt(face, u0, zm, (w0 + w1) / 2), fpt(face, u1, zm, (w0 + w1) / 2)
    return P.beam(a, p0, p1, P.sec_rect((w1 - w0) / 2, (z1 - z0) / 2, ch), key, name=name, kind=kind)


def inner(z, half=PH):
    """|u| of a post's (or collar's) inner face on a face at height z, SEAT into it."""
    return c(z) - half + SEAT


# ---- footing and post ------------------------------------------------------------------------------------------------
def footing(a, x, y, name="footing"):
    """The tapered stone footing: chamfered square rings, flat top; its lower band a shade deeper."""
    rings = [[(x + u, y + v, z) for u, v in P.sec_rect(h, h, ch)] for z, h, ch in FOOT]
    p = P.prism(a, rings, STONE, band_keys=[mix(STONE, STONE_DEEP, 0.35), STONE], name=name, kind="stone")
    P.texture(a, p.vs, 0.04, P.seed(P.TAG[-1] + name), scale=0.6)
    return p


def post(a, sx, sy):
    """One leaning post: three square segments joined by the deck and rail collars (block joinery), pegs on the
    collars' two outer faces and on the post's outer faces at the girt."""
    zs = [FT - SEAT]
    for k in ("deck", "rail"):
        z0, z1, _ = COLLARS[k]
        zs += [z0 + SEAT, z1 - SEAT]
    zs.append(E)
    for i in range(3):
        z0, z1 = zs[2 * i], zs[2 * i + 1]
        P.leg(a, (sx * c(z0), sy * c(z0)), (sx * c(z1), sy * c(z1)), z1, PH, PH, TIMBER, ch=PCH, z0=z0,
              name=f"post{i}", kind="post")
    for k, (z0, z1, h) in COLLARS.items():
        zm = (z0 + z1) / 2
        cx, cy = sx * c(zm), sy * c(zm)
        block(a, cx, cy, z0, z1, h, TIMBER, COLLAR_BEV, f"collar_{k}", "collar")
        zp = (z0 + z1 - COLLAR_BEV) / 2
        peg(a, (sx * (c(zm) + h), cy, zp), (sx, 0, 0), f"peg_{k}_x")
        peg(a, (cx, sy * (c(zm) + h), zp), (0, sy, 0), f"peg_{k}_y")
    zg = sum(GIRT["z"]) / 2
    peg(a, (sx * (c(zg) + PH), sy * c(zg), zg), (sx, 0, 0), "peg_girt_x")
    peg(a, (sx * c(zg), sy * (c(zg) + PH), zg), (0, sy, 0), "peg_girt_y")
    post_head(a, sx, sy)


def post_head(a, sx, sy):
    """The post's top where it runs on under the canvas (the cap covers the rest): an L-shaped block on the post top
    whose top follows the canvas underside (SEAT into it) on both sides of the hip, stopping 0.01 short of the canvas'
    cut-out corner."""
    lo, hi, b = CT - PH, CT + PH, NOTCH - 0.01
    plan = [(lo, lo), (hi, lo), (hi, b), (b, b), (b, hi), (lo, hi)]          # counter-clockwise from above (+, +)
    top = [Vector((sx * u, sy * v, canvas_top(u, v) - CANVAS_T + SEAT)) for u, v in plan]
    bot = [Vector((sx * u, sy * v, E - SEAT)) for u, v in plan]
    faces = [[0, 1, 2, 3], [0, 3, 4, 5], [9, 8, 7, 6], [11, 10, 9, 6]]
    faces += [[(i + 1) % 6, i, 6 + i, 6 + (i + 1) % 6] for i in range(6)]
    if sx * sy < 0:                                                        # mirrored once: keep the winding outward
        faces = [f[::-1] for f in faces]
    return P.shell(a, top + bot, faces, TIMBER, name="post_head", kind="post")


# ---- lower storey ----------------------------------------------------------------------------------------------------
def girt(a, face):
    zm = sum(GIRT["z"]) / 2
    u = inner(zm)
    return member(a, face, -u, u, *GIRT["z"], *GIRT["w"], TIMBER, f"girt_{face}", "beam", ch=GIRT["ch"])


def rim(a, face):
    zm = sum(RIM["z"]) / 2
    u = inner(zm, COLLARS["deck"][2])
    return member(a, face, -u, u, *RIM["z"], *RIM["w"], TIMBER, f"rim_{face}", "beam", ch=RIM["ch"])


def bay(collar=False):
    """The lower bay between girt and rim beam: (z bottom, z top, half width at the bottom, at the top), each SEAT
    into the timber round it; collar=True: the top width to the deck collars' inner faces (the braces' top ends)."""
    zb, zt = GIRT["z"][1] - SEAT, RIM["z"][0] + SEAT
    ht = c(sum(COLLARS["deck"][:2]) / 2) - COLLARS["deck"][2] + SEAT if collar else inner(zt)
    return zb, zt, inner(zb), ht


def infill(a, face):
    """Dark vertical plank infill in the bay (trapezoids: the posts lean), V gaps between the planks."""
    zb, zt, hb, ht = bay()
    to3 = (lambda u, v, w: fpt(face, u, v, w))
    # the outer planks' top corners step in under the deck collars (SEAT into the collar's underside and inner face)
    zc = COLLARS["deck"][0] + SEAT
    hp = inner(zc)
    hc = c(sum(COLLARS["deck"][:2]) / 2) - COLLARS["deck"][2] + SEAT
    out = []
    for i in range(INFILL_N):
        f0, f1 = i / INFILL_N, (i + 1) / INFILL_N
        g0 = INFILL_GAP / 2 if i > 0 else 0.0
        g1 = INFILL_GAP / 2 if i < INFILL_N - 1 else 0.0
        poly = [(-hb + 2 * hb * f0 + g0, zb), (-hb + 2 * hb * f1 - g1, zb), (-ht + 2 * ht * f1 - g1, zt),
                (-ht + 2 * ht * f0 + g0, zt)]
        if i == 0:
            poly = poly[:3] + [(-hc, zt), (-hc, zc), (-hp, zc)]
        elif i == INFILL_N - 1:
            poly = poly[:2] + [(hp, zc), (hc, zc), (hc, zt)] + poly[3:]
        key = mix(TIMBER_DEEP, TIMBER, 0.10 * (i % 2))
        p = P.ext(a, poly, *INFILL_W, key, to3=to3, name=f"infill_{face}{i}", kind="infill", amp=0.04)
        P.texture(a, p.vs, 0.03, P.seed(f"infill_{face}{i}"), scale=0.5)
        out.append(p)
    return out


def brace_len():
    """The horizontal length of a brace board's cut end (its width BRACE_W square to its run)."""
    zb, zt, hb, ht = bay(collar=True)
    L = 0.8
    for _ in range(8):
        ang = math.atan2(zt - zb, hb + ht - L)
        L = BRACE_W / math.sin(ang)
    return L


def xbrace(a, face):
    """The X brace: the back board from bottom-right to top-left on the infill (SEAT into it), the front board from
    bottom-left to top-right over it (SEAT into the back board), both ends cut level into girt and rim beam, a peg at
    the crossing."""
    zb, zt, hb, ht = bay(collar=True)
    L = brace_len()
    to3 = (lambda u, v, w: fpt(face, u, v, w))
    key = mix(TIMBER, TIMBER_END, 0.15)
    back = [(hb - L, zb), (hb, zb), (-ht + L, zt), (-ht, zt)]
    front = [(-hb, zb), (-hb + L, zb), (ht, zt), (ht - L, zt)]
    P.ext(a, back, *BRACE_B, key, to3=to3, name=f"brace_{face}b", kind="brace")
    P.ext(a, front, *BRACE_A, key, to3=to3, name=f"brace_{face}a", kind="brace")
    t = (hb - L / 2) / (hb + ht - L)
    zc = zb + (zt - zb) * t
    n = fpt(face, 0.0, zc, 1.0) - fpt(face, 0.0, zc, 0.0)
    n.z = 0.0
    peg(a, fpt(face, 0.0, zc, BRACE_A[1]), n, f"peg_brace_{face}")
    return zc


def centre_leg(a, face):
    """The short leg under a girt's middle, foot flat on the ground, leaning with the face."""
    z1 = GIRT["z"][0] + SEAT
    p0, p1 = fpt(face, 0.0, 0.0, 0.15), fpt(face, 0.0, z1, 0.15)
    hu, hv = (LEG["hu"], LEG["hv"]) if face in ("F", "B") else (LEG["hv"], LEG["hu"])
    return P.leg(a, (p0.x, p0.y), (p1.x, p1.y), z1, hu, hv, mix(TIMBER, TIMBER_DEEP, 0.15), ch=0.05,
                 name=f"leg_{face}", kind="post")


# ---- deck and railing ------------------------------------------------------------------------------------------------
def deck(a):
    """Six planks along X between the side rim beams (SEAT into them), the outer two SEAT into the front and back rim
    beams; top DECK."""
    zm = sum(RIM["z"]) / 2
    xi = c(zm) + RIM["w"][0] + SEAT          # the side rims' inner faces, SEAT into them
    yi = xi
    w = (2 * yi - (DECK_PLANKS - 1) * PLANK_GAP) / DECK_PLANKS
    out = []
    for i in range(DECK_PLANKS):
        y = -yi + w / 2 + i * (w + PLANK_GAP)
        key = mix(PLANK, TIMBER_DEEP, 0.08 * (i % 2))
        p = P.plank(a, (-xi, y, DECK - PLANK_T / 2), (xi, y, DECK - PLANK_T / 2), w, PLANK_T, key, ch=0.05,
                    name=f"plank{i}", kind="plank", amp=0.05)
        P.texture(a, p.vs, 0.03, P.seed(f"plank{i}"), scale=0.5)
        out.append(p)
    return out


def railing(a, face, spans=None):
    """Bottom rail, top rail and balusters on one face (top rail between the rail collars). spans: [(u0, u1)] of the
    rails' outer ends toward the newels (front), default the full face."""
    out = {}
    for k, (z0, z1, hd) in RAILS.items():
        zm = (z0 + z1) / 2
        u = inner(zm, COLLARS["rail"][2] if k == "top" else PH)
        for j, (u0, u1) in enumerate(spans or [(-u, u)]):
            u0, u1 = max(u0, -u), min(u1, u)
            out[f"{k}{j}"] = member(a, face, u0, u1, z0, z1, -hd, hd, TIMBER, f"rail_{face}_{k}{j}", "rail", ch=0.05)
    if spans is None:
        zb, zt = RAILS["bottom"][1] - SEAT, RAILS["top"][0] + SEAT
        zm = (zb + zt) / 2
        for i, u in enumerate(BALUSTERS):
            q = fpt(face, u, zm, 0.0)
            P.box(a, (q.x - BAL_H, q.y - BAL_H, zb), (q.x + BAL_H, q.y + BAL_H, zt), TIMBER,
                  name=f"baluster_{face}{i}", kind="rail")
    return out


def newels(a):
    """The two newel posts either side of the ladder gap, standing on the front rim beam."""
    for s in (-1, 1):
        x0, x1 = sorted((s * NEWEL["x"][0], s * NEWEL["x"][1]))
        yc = -c((RIM_TOP + NEWEL["top"]) / 2)
        hx = (x1 - x0) / 2
        sec, top = P.sec_rect(hx, NEWEL["hd"], 0.04), P.sec_rect(hx - NEWEL["bev"], NEWEL["hd"] - NEWEL["bev"], 0.03)
        cx = (x0 + x1) / 2
        rings = [[(cx + u, yc + v, z) for u, v in sec] for z in (RIM_TOP - SEAT, NEWEL["top"] - NEWEL["bev"])]
        rings.append([(cx + u, yc + v, NEWEL["top"]) for u, v in top])
        P.prism(a, rings, TIMBER, band_keys=[None, mix(TIMBER, TIMBER_END, 0.4)], name=f"newel{s:+d}", kind="rail")


def front_railing(a):
    return railing(a, "F", spans=[(-9.0, -NEWEL["x"][0] + SEAT), (NEWEL["x"][0] - SEAT, 9.0)])


# ---- roof --------------------------------------------------------------------------------------------------------------
def canvas_top(x, y):
    """The canvas top surface height: a flat apex inside RF, straight hip faces down to the level eave (Z_EAVE) at HC;
    each face dips softly toward its middle line (S_FACE, zero on the hips, at the apex and at the eave)."""
    r, m = max(abs(x), abs(y)), min(abs(x), abs(y))
    if r <= RF + 1e-6:
        return ZA
    t = (r - RF) / (HC - RF)
    q = m / r
    return ZA - (ZA - Z_EAVE) * t - S_FACE * 4.0 * t * (1.0 - t) * (1.0 - q * q)


def canvas(a, name="canvas"):
    """The canvas roof: one closed slab over a square grid (GRID, mirrored) without its four corner cells (the caps
    stand there), each cell split along the diagonal toward the centre (so the hips run along grid edges), the
    underside CANVAS_T straight below, vertical rim faces a shade deeper round the outline."""
    cs = sorted({-g for g in GRID} | set(GRID))
    n = len(cs)
    idx, pts = {}, []
    for i in range(n):
        for j in range(n):
            idx[(i, j)] = len(pts)
            pts.append(Vector((cs[i], cs[j], canvas_top(cs[i], cs[j]))))
    nb = len(pts)
    pts += [p - Vector((0, 0, CANVAS_T)) for p in pts[:nb]]
    ci = (n - 1) / 2
    faces, keys, tops = [], [], []
    for i in range(n - 1):
        for j in range(n - 1):
            xm, ym = (cs[i] + cs[i + 1]) / 2, (cs[j] + cs[j + 1]) / 2
            if min(abs(xm), abs(ym)) > NOTCH:
                continue                    # a corner cell: the cap stands there
            a_, b_, c_, d_ = idx[(i, j)], idx[(i + 1, j)], idx[(i + 1, j + 1)], idx[(i, j + 1)]
            tris = [(a_, b_, c_), (a_, c_, d_)] if (i + 0.5 < ci) == (j + 0.5 < ci) else [(a_, b_, d_), (b_, c_, d_)]
            for t in tris:
                tops.append(t)
                faces.append(list(t))
                keys.append(None)
                faces.append([nb + q for q in reversed(t)])
                keys.append(None)
    # rim: a vertical quad under every outline edge (an edge used by one top triangle), wound outward
    used = {}
    for t in tops:
        for k in range(3):
            e = (t[k], t[(k + 1) % 3])
            used.setdefault(frozenset(e), []).append(e)
    rim_k = mix(CANVAS, CANVAS_DEEP, 0.45)
    for es in used.values():
        if len(es) == 1:
            p0, p1 = es[0]
            faces.append([p1, p0, nb + p0, nb + p1])
            keys.append(rim_k)
    keep = sorted({q for f in faces for q in f})            # drop the cut-out corners' grid points
    remap = {q: k for k, q in enumerate(keep)}
    pts, faces = [pts[q] for q in keep], [[remap[q] for q in f] for f in faces]
    p = P.shell(a, pts, faces, CANVAS, keys=keys, name=name, kind="canvas", amp=0.02)
    P.texture(a, p.vs, 0.03, P.seed(name), scale=0.18)
    under = [q.z for q in pts[nb:]]
    P.GEO.setdefault("canvas", {})[name] = {"apex_top": round(ZA, 3), "eave_top": Z_EAVE,
                                            "low_under": round(min(under), 3)}
    return p


def corner_caps(a):
    """Compact block caps on the post tops at the canvas corners (the canvas SEAT into their inner faces), a small
    block on each."""
    tk = mix(TIMBER, TIMBER_END, 0.15)
    z1 = CAP_Z + CAP["h"]
    for sx, sy in corners():
        cx, cy = sx * CAP["c"], sy * CAP["c"]
        block(a, cx, cy, CAP_Z, z1, CAP["half"], TIMBER, CAP["bev"], f"cap{sx:+d}{sy:+d}", "cap", top_key=tk)
        block(a, cx, cy, z1 - SEAT, z1 - SEAT + CAP["top_h"], CAP["top_half"], TIMBER, 0.06,
              f"cap_top{sx:+d}{sy:+d}", "cap", top_key=tk)


def finial(a):
    """The turned finial on the canvas' flat top: an octagonal base with a bevelled top, a round neck, a ball."""
    base, bh = FIN["base"], FIN["base_h"]
    rings = [[(u, v, z) for u, v in P.sec_ngon(base, 8)] for z in (ZA - SEAT, ZA + bh - 0.08)]
    rings.append([(u, v, ZA + bh) for u, v in P.sec_ngon(base - 0.09, 8)])
    P.prism(a, rings, TIMBER, band_keys=[None, mix(TIMBER, TIMBER_END, 0.4)], name="finial_base", kind="finial")
    z0 = ZA + bh - SEAT
    P.log(a, (0, 0, z0), (0, 0, z0 + FIN["neck_h"]), FIN["neck"], TIMBER, sides=8, up=(1, 0, 0), name="finial_neck",
          kind="finial")
    R_ = FIN["ball"]
    zc = z0 + FIN["neck_h"] + R_ - 0.05
    pts = [Vector((0, 0, zc - R_))]
    for k, el in enumerate((-50.0, -15.0, 20.0, 52.0)):
        e = math.radians(el)
        for j in range(8):
            th = 2 * math.pi * (j + 0.5 * (k % 2)) / 8
            pts.append(Vector((R_ * math.cos(e) * math.cos(th), R_ * math.cos(e) * math.sin(th), zc + R_ * math.sin(e))))
    for j in range(4):
        th = 2 * math.pi * j / 4 + math.pi / 4
        pts.append(Vector((0.12 * math.cos(th), 0.12 * math.sin(th), zc + R_ * 0.97)))
    P.hull(a, pts, mix(TIMBER, TIMBER_END, 0.25), name="finial_ball", kind="finial", amp=0.03)
    P.GEO["finial_top"] = round(zc + R_ * 0.97, 3)


# ---- banner ------------------------------------------------------------------------------------------------------------
def knob(a, c_, r, name):
    """(m069 / m072) A low-poly ball on the rod's axis (X): two poles and three rings of six, as a hull."""
    c_ = Vector(c_)
    pts = [c_ + Vector((r, 0, 0)), c_ - Vector((r, 0, 0))]
    for k, xf in enumerate((-0.6, 0.0, 0.6)):
        rr = r * math.sqrt(1 - xf * xf)
        for j in range(6):
            th = 2 * math.pi * (j + 0.5 * k) / 6
            pts.append(c_ + Vector((xf * r, rr * math.cos(th), rr * math.sin(th))))
    return P.hull(a, pts, TIMBER_END, name=name, kind="knob", amp=0.03)


def _diamond_ring(a, cx, cz, hw, hh, line, y0, y1, name):
    """(m069 / m072) A diamond outline slab (outer half sizes hw x hh, `line` wide along x) between y0 and y1."""
    k = line / hw
    outer = [(cx, cz + hh), (cx + hw, cz), (cx, cz - hh), (cx - hw, cz)]
    inner_ = [(cx, cz + hh * (1 - k)), (cx + hw * (1 - k), cz), (cx, cz - hh * (1 - k)), (cx - hw * (1 - k), cz)]
    pts = [Vector((x, y0, z)) for x, z in outer + inner_] + [Vector((x, y1, z)) for x, z in outer + inner_]
    faces = []
    for i in range(4):
        i1 = (i + 1) % 4
        faces += [[i, i1, 4 + i1, 4 + i], [12 + i, 12 + i1, 8 + i1, 8 + i], [i1, i, 8 + i, 8 + i1],
                  [4 + i, 4 + i1, 12 + i1, 12 + i]]
    return P.shell(a, pts, faces, CREAM, name=name, kind="emblem", amp=0.02)


def banner(a, y=BAN["y"]):
    """(m072 recipe) The rod under the front rim beam (ball knobs SEAT-ish into the beam), a dark hem sleeve round it,
    the red point-tipped cloth and the cream double diamond on its front face."""
    x = ROD["x"]
    P.log(a, (-x, y, ROD_Z), (x, y, ROD_Z), ROD["r"], TIMBER_END, sides=8, end_key=TIMBER_END, name="rod", kind="rod")
    for sg in (-1, 1):
        knob(a, (sg * (x + ROD["knob"] - 0.035), y, ROD_Z), ROD["knob"], f"knob{sg:+d}")
    c0, c1 = -BAN["x"], BAN["x"]
    P.sleeve(a, (c0 - 0.04, y, ROD_Z), (c1 + 0.04, y, ROD_Z), SLEEVE_IN, SLEEVE_IN + SLEEVE_T, BANNER_DEEP, sides=8,
             name="hem", kind="hem", amp=0.02)
    top = ROD_Z - SLEEVE_IN - 0.015
    outline = [(c0, top), (c1, top), (c1, BAN["side"]), (0.0, BAN["tip"]), (c0, BAN["side"])]
    yf, yb = y - BAN["t"] / 2, y + BAN["t"] / 2
    cloth = P.ext(a, outline, yf, yb, BANNER, to3=lambda u, v, w: Vector((u, w, v)), name="cloth", kind="banner",
                  amp=0.02)
    P.texture(a, cloth.vs, 0.02, P.seed("cloth"), scale=0.4)
    e0, e1 = yf + 0.005, yf - 0.015
    for i, (hw, hh, line) in enumerate(EMB["rings"]):
        _diamond_ring(a, 0.0, EMB["z"], hw, hh, line, e0, e1, f"emblem{i}")
    P.GEO["banner"] = {"top": round(top, 3), "tip": BAN["tip"], "y": y}


# ---- ladder ------------------------------------------------------------------------------------------------------------
TAN = math.tan(math.radians(LAD["angle"]))
Y_TOUCH = -(c(sum(RIM["z"]) / 2) + RIM["w"][1]) + SEAT        # the rails' back face crosses the rim's top front edge
RAIL_DY = LAD["rail_d"] / math.sin(math.radians(LAD["angle"]))  # the rail's horizontal depth
LAD_TOP = DECK + LAD["above"]
RUNG_PITCH = RIM_TOP / (LAD["rungs"] + 1)


def y_back(z):
    """The ladder's back face (toward the tower) at height z."""
    return Y_TOUCH + (z - RIM_TOP) / TAN


def ladder(a):
    """Two rails (level-cut feet on the ground, level-cut tops LAD["above"] over the deck) and LAD["rungs"] square
    rungs SEAT into the rails' inner faces; rung tops every RUNG_PITCH."""
    hw = LAD["rail_w"] / 2
    xr = LAD["inner"] + hw
    yc = (lambda z: y_back(z) - RAIL_DY / 2)
    for s in (-1, 1):
        P.leg(a, (s * xr, yc(0.0)), (s * xr, yc(LAD_TOP)), LAD_TOP, hw, RAIL_DY / 2, TIMBER, ch=0.05, z0=0.0,
              name=f"ladder_rail{s:+d}", kind="ladder_rail")
    rh = LAD["rung"] / 2
    tops = []
    for k in range(1, LAD["rungs"] + 1):
        zt = k * RUNG_PITCH
        y = yc(zt - rh)
        P.plank(a, (-LAD["inner"] - SEAT, y, zt - rh), (LAD["inner"] + SEAT, y, zt - rh), LAD["rung"], LAD["rung"],
                mix(TIMBER, TIMBER_END, 0.2), ch=0.04, name=f"rung{k}", kind="ladder_rung")
        tops.append(round(zt, 3))
    P.GEO["ladder"] = {"rung_tops": tops, "foot_y": round(y_back(0.0), 3), "inner": round(2 * LAD["inner"], 3),
                       "angle": LAD["angle"], "top": LAD_TOP}


# ---- assemblies --------------------------------------------------------------------------------------------------------
def tower(a, roof=True, dressing=True):
    for sx, sy in corners():
        with P.frame(None, f"{'lr'[sx > 0]}{'fb'[sy > 0]}_"):
            footing(a, sx * CB, sy * CB)
            post(a, sx, sy)
    for face in ("F", "B", "L", "R"):
        girt(a, face)
        rim(a, face)
        infill(a, face)
    for face in BRACE_FACES:
        xbrace(a, face)
        centre_leg(a, face)
    deck(a)
    for face in ("B", "L", "R"):
        railing(a, face)
    front_railing(a)
    newels(a)
    if roof:
        canvas(a)
        corner_caps(a)
        finial(a)
    if dressing:
        banner(a)
        ladder(a)


def hero_all(a):
    tower(a)


def post_part(a):
    post(a, -1, -1)


def brace_part(a):
    xbrace(a, "F")


def railing_part(a):
    railing(a, "B")


def deck_part(a):
    for face in ("F", "B", "L", "R"):
        rim(a, face)
    deck(a)


def roof_part(a):
    canvas(a)
    corner_caps(a)


def finial_part(a):
    finial(a)


def footing_part(a):
    footing(a, 0.0, 0.0)


PARTS = ((POST_P, post_part), (BRACE_P, brace_part), (RAIL_P, railing_part), (DECK_P, deck_part),
         (ROOF_P, roof_part), (FINIAL_P, finial_part), (BANNER_P, banner), (LADDER_P, ladder),
         (FOOT_P, footing_part))

NOTES = {
    HERO: "Watchtower (sheet 076): four leaning 1.0-square posts on tapered stone footings, block collars with pegs, a "
          "dark plank lower storey with X braces on the sides and rear, a plank deck at 7.40 with rim beams, railings "
          "on all sides (top rail 10.70; ladder gap 3.1 at the front between newels), a straight canvas pyramid roof "
          "(level eave 13.62, apex 17.27) with block caps on the post tops at its corners and a turned finial, a red "
          "banner under the front deck beam, and a 75 deg ladder at the front centre (7 rungs, pitch 0.93; inner width "
          "2.4). Headroom over the deck 6.9+.",
    POST_P: "Post: one leaning post (2.4 deg) in three segments with the deck and rail block collars and their pegs",
    BRACE_P: "Brace: an X brace of two boards for one lower bay (3.55 tall), a peg at the crossing",
    RAIL_P: "Railing: bottom and top rail with three balusters for one side (between the rail collars)",
    DECK_P: "Deck Floor: four rim beams and six planks, deck top 7.40 (rims 0.03 proud)",
    ROOF_P: "Canvas Roof: the straight four-sided canvas pyramid (8.1 square, rise 3.65) with its four block corner caps",
    FINIAL_P: "Roof Finial: octagonal base, neck and ball (turned wood)",
    BANNER_P: "Banner: rod with ball knobs, hem sleeve, red point-tipped cloth with the cream double diamond",
    LADDER_P: "Ladder: two rails and seven rungs, leaning 75 deg, 9.80 tall (2.4 over the deck), rung pitch 0.93",
    FOOT_P: "Footing: tapered stone block, 2.3 square base, 1.7 top, 1.4 tall",
}
COLLISION = {HERO: "precise", POST_P: "hull", BRACE_P: "hull", RAIL_P: "hull", DECK_P: "box", ROOF_P: "hull",
             FINIAL_P: "none", BANNER_P: "none", LADDER_P: "precise", FOOT_P: "box"}
BUDGETS = {HERO: 6000}
TARGET_SIZE = None
VIEWS = {"f34_sheet": (-35, 20), "r34_sheet": (-145, 20), "front_sheet": (0, 0), "side_sheet": (90, 0),
         "rear_sheet": (180, 0), "top_sheet": (0, 89.9)}
# exploded view, laid out like the sheet's panel (offsets of each part's origin)
EXPLODED = {ROOF_P: (0.0, 2.0, 15.0), FINIAL_P: (0.0, 2.0, 19.5), RAIL_P: [(-7.5, 0.0, 11.0), (7.5, 0.0, 11.0)],
            DECK_P: (0.0, 2.0, 9.5), POST_P: [(-10.5, 8.0, 1.6), (-3.5, 8.0, 1.6), (3.5, 8.0, 1.6), (10.5, 8.0, 1.6)],
            BRACE_P: [(-7.0, 0.0, 2.5), (0.0, 0.0, 2.5), (7.0, 0.0, 2.5)],
            FOOT_P: [(-10.5, 8.0, 0.0), (-3.5, 8.0, 0.0), (3.5, 8.0, 0.0), (10.5, 8.0, 0.0)],
            BANNER_P: (15.0, 0.0, 8.0), LADDER_P: (15.5, 0.0, 0.0)}
# the climb: from the ground in front up the ladder, through the railing gap, round the deck
CLIMB = [(0.0, -9.0), (0.0, 1.2), (-1.5, 1.2), (-1.5, -1.0), (1.5, -1.0), (1.5, 1.2)]
PROXY = ((1.0, 0.40, 0.0, 1.0), (1.0, 0.5, 1.0, 4.4), (0.55, 0.5, 4.4, 5.5))      # feet box 0.10 slimmer (ride)
WALK = {"paths": [CLIMB], "ride": True, "max_rise": 1.0, "lift": 0.12, "skip": ("ladder",), "proxy": PROXY,
        "turn": [(0.0, 0.2, DECK), (0.0, -1.2, DECK)]}
VERIFY = dict(cls="structure", walk=WALK, stored={HERO: ["m076_deck", "m076_ladder_foot"]})
COMPARE = {"f34": {"box": (240, 75, 540, 460), "view": VIEWS["f34_sheet"][:2]},
           "r34": {"box": (630, 75, 940, 460), "view": VIEWS["r34_sheet"][:2]},
           "front": {"box": (20, 548, 265, 812), "view": (0, 0)},
           "side": {"box": (275, 548, 458, 812), "view": (90, 0)},
           "rear": {"box": (550, 548, 760, 812), "view": (180, 0)},
           "top": {"box": (765, 590, 1000, 795), "view": (0, 89.9)}}
POINTS = {HERO: {"m076_deck": ((0.0, 0.0, DECK), (0, 1, 0)), "m076_ladder_foot": ((0.0, y_back(0.0) - 1.2, 0.0),
                                                                                 (0, 1, 0))}}


def tower_check(objs):
    """Spec "Brief": the deck top (rays down over the planks), the headroom from the deck to the lowest thing over it
    inside the railing (rays up on a grid), the clear width between the railings, the ladder's rung tops and the gap
    between the newels."""
    h = objs[HERO]
    me = h.data
    tree = BVHTree.FromPolygons([h.matrix_world @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])
    z0 = h.matrix_world.translation.z - h[MODEL.OFF][2]

    def ray(p, d):
        q = tree.ray_cast(MODEL.at(h, p), Vector(d))
        return q[0].z - z0 if q[0] is not None else None
    yi = c(sum(RIM["z"]) / 2) + RIM["w"][0] + SEAT                 # as deck(): rays down the planks' middles
    pw = (2 * yi - (DECK_PLANKS - 1) * PLANK_GAP) / DECK_PLANKS
    ys = [-yi + pw / 2 + i * (pw + PLANK_GAP) for i in (0, 2, 3, 5)]
    deck_z = [ray((x, y, DECK + 1.15), (0, 0, -1)) for x in (-1.8, -0.6, 0.6, 1.8) for y in ys]
    rail_in = c(RAILS["top"][1]) - RAILS["top"][2]
    lim = rail_in - 0.02
    heads = []
    post_in = c(DECK) - COLLARS["deck"][2]          # the corners behind the posts and collars are not stood on
    for i in range(9):
        for j in range(9):
            x, y = -lim + 2 * lim * i / 8, -lim + 2 * lim * j / 8
            if min(abs(x), abs(y)) > post_in:
                continue
            up = ray((x, y, DECK + 0.05), (0, 0, 1))
            if up is not None:
                heads.append(up - DECK)
    xs = [ray((0.0, -3.0, z), (1, 0, 0)) for z in (DECK + 1.0, DECK + 2.0)]
    rep = {"deck_top": [round(min(d for d in deck_z if d), 3), round(max(d for d in deck_z if d), 3)],
           "headroom_min": round(min(heads), 3), "rail_inner_clear": round(2 * (c(DECK + 1.5) - RAILS["bottom"][2]), 3),
           "ladder": P.GEO.get("ladder"), "gap_between_newels": round(2 * NEWEL["x"][0], 3),
           "canvas": P.GEO.get("canvas"), "finial_top": P.GEO.get("finial_top"), "rail_top": RAILS["top"][1],
           "deck_x_at_front_gap": xs}
    pr = []
    if any(d is None or abs(d - DECK) > 0.005 for d in deck_z):
        pr.append(f"{HERO}: deck samples off {DECK}: {deck_z}")
    if rep["headroom_min"] < 6.9:
        pr.append(f"{HERO}: headroom over the deck {rep['headroom_min']} under 6.9")
    return rep, pr


def build(render=True, close=False, spin=False):
    return MODEL.run(hero=(HERO, hero_all), parts=PARTS, notes=NOTES, collision=COLLISION, budgets=BUDGETS,
                     target_size=TARGET_SIZE, points=POINTS, views=VIEWS, exploded=EXPLODED,
                     close=CLOSE if close else None, verify=VERIFY, checks=[tower_check], render=render, spin=spin)


CLOSE = {"joint_cu": dict(at=(-c(DECK - 0.35), -c(DECK - 0.35), DECK + 0.25), r=1.8, az=-35, el=15),
         "roof_cu": dict(at=(0.0, 0.0, ZA - 0.5), r=2.4, az=-30, el=25),
         "ladder_cu": dict(at=(0.0, -4.4, DECK + 0.25), r=2.4, az=-25, el=25)}


def preview(names=("f34_sheet", "front_sheet", "side_sheet")):
    return MODEL.preview(HERO, VIEWS, names)


def compare(cells=None, out_dir=None, height=360):
    import importlib
    import compare as C
    importlib.reload(C)
    return C.compare(NUM, {k: COMPARE[k] for k in (cells or COMPARE)}, out_dir=out_dir, height=height)
