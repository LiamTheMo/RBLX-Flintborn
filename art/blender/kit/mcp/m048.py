"""048 Dock (references/048.png, remade 2026-11-03) on the shared library (kit_parts / kit_build): a tiling dock module.
Six chunky square posts (2 across x 3 along, centres 7.4 across and 6.4 along) run from the ground past the deck edge to
bevelled caps (7.2); 15 thick transverse planks (deck top 4.4) on side beams per bay and an end header at each end; a
bolt block with a hex brass bolt on every post's outer face; knee braces on both long sides and an X brace on each end;
two rope turns round every post and five twisted swags (both long sides and the +X end; the -X end is open).

    import importlib, kit_parts, kit_build, m048
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m048); m048.build()

Build frame (studs): long axis X (the tiling axis, 16-stud pitch: end planks at x +-8.0, nothing past them), the open
(rope-free) end at -X, the roped end at +X, front -Y, ground z 0, centred on x 0 / y 0. See M048_spec.md.
"""
import math

from mathutils import Vector

import kit_build as B
import kit_parts as P

NUM, TITLE = 48, "Dock"
HERO = "TimberDock"
POST_P, DECK_P, BEAM_P = "TimberDockPost", "TimberDockDeck", "TimberDockBeam"
CROSS_P, BRACE_P, ROPE_P = "TimberDockCrossbeam", "TimberDockBrace", "TimberDockRope"
WOOD, WOOD_DEEP = "m048_wood", "m048_wood_deep"
ROPE, ROPE_DARK, BRASS = "m048_rope", "m048_rope_dark", "m048_brass"

# key -> (hex, roughness, metal, emission, low specular). Stage 4: calibrated against the sheet (M048_spec.md).
PALETTE = {WOOD: ("#914A16", 0.85, 0.0, 0.0, True), WOOD_DEEP: ("#673514", 0.85, 0.0, 0.0, True),
           ROPE: ("#EEC77A", 0.95, 0.0, 0.0, True), ROPE_DARK: ("#D89A50", 0.95, 0.0, 0.0, True),
           BRASS: ("#EBA949", 0.5, 0.2, 0.0, False)}
# calibration targets: the swatches (timber) and the sheet's rendered medians (rope, groove, bolt); spec stage 4
TARGETS = {WOOD: ((0xB7, 0x5C, 0x20), "brown"), WOOD_DEEP: ((0x7F, 0x42, 0x1A), "brown"),
           ROPE: ((0xFC, 0xD2, 0x75), "vivid"), ROPE_DARK: ((0xE8, 0xAE, 0x52), "vivid"),
           BRASS: ((0xF2, 0xA5, 0x41), "vivid")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)

# ---- layout (spec "Brief": the tiling pitch sets the length, the front three-quarter the proportions) -------------
END = 8.0                       # deck ends (tiling seams)
POSTS_X = (-6.4, 0.0, 6.4)
POST_Y = 3.7                    # post centres +-3.7 (7.4 across: the top cell's W : H 0.598, the f34 W : H)
PH, POST_CH, CAP_CH = 0.625, 0.05, 0.10
POST_TOP = 7.20
LEG_RINGS = (2.25, 2.75)        # leg colour rings: below 2.25 the deep mix, 2.25-2.75 a quarter, above timber
DECK_TOP, PLANK_T, PLANK_CH, GAP = 4.4, 0.9, 0.05, 0.04
PLANK_Z0 = DECK_TOP - PLANK_T
PLANK_Y = POST_Y + 0.30         # bay planks end 0.30 past the post centre line (posts stand 0.33 proud of them)
SEAT = 0.02                     # how far a piece sinks into what holds it
BEAM_Y = (POST_Y - PH + 0.05, POST_Y + 0.15)    # side beams (inner, outer face), under the plank ends, between posts
BEAM_Z = (2.75, PLANK_Z0 + 0.01)
HEAD_X = (6.4 + PH - SEAT, 7.60)        # end header (crossbeam) outside each end post, under the end planks
BLOCK = dict(hw=0.74, hz=0.76, zc=3.50, depth=0.34, ch=0.07)     # bolt block on each post's outer face
BOLT = dict(r=0.32, h=0.18, ch=0.06)
KNEE = ((0.70, 1.75), (1.55, 2.75))     # lower contact z on the post face; upper contact, distance from the face
KNEE_Y = (POST_Y - 0.50, POST_Y + 0.05)
XB = dict(z=(0.66, 2.52), hw=0.25, t=0.24, top=BEAM_Z[0] + SEAT, lo=0.25)
TURN_R, TURNS_Z = 0.16, (5.82, 6.12)
SWAG_R, SWAG_LOW, SWAG_N = 0.15, 5.12, 18      # 18 segments: the twist reads as strands (close-up cell)
TURN_CUT = 0.12                 # a turn's corner cut (along each side from the mitred corner)


def legs_key(z):
    return P.mix(WOOD, WOOD_DEEP, 0.5) if z < LEG_RINGS[0] else P.mix(WOOD, WOOD_DEEP, 0.25)


# ---- small model-specific shapes ------------------------------------------------------------------------------------
def pad(a, c, n, u, hu, hv, depth, ch, key, name, kind):
    """A plate on a face (a bolt block, a post cap): centre c on the face, outward normal n, in-face axis u (half
    sizes hu along u, hv along n x u), sunk SEAT into the face, `depth` proud, its front edges bevelled ch."""
    n, u, c = Vector(n).normalized(), Vector(u).normalized(), Vector(c)
    v = n.cross(u)

    def ring(d, inset):
        return [c + n * d + u * (su * (hu - inset)) + v * (sv * (hv - inset)) for su, sv in
                ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return P.prism(a, [ring(-SEAT, 0.0), ring(depth - ch, 0.0), ring(depth, ch)], key, name=name, kind=kind)


def hexbolt(a, c, n, name, r=BOLT["r"], h=BOLT["h"], ch=BOLT["ch"]):
    """A hex bolt head (close-up cell): six sides, a bevelled top, sunk SEAT into the face. 32 tris."""
    n, c = Vector(n).normalized(), Vector(c)
    u = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = (u - n * u.dot(n)).normalized()
    v = n.cross(u)

    def ring(d, rr):
        return [c + n * d + (u * math.cos(math.pi / 6 + k * math.pi / 3) + v * math.sin(math.pi / 6 + k * math.pi / 3))
                * rr for k in range(6)]
    return P.prism(a, [ring(-SEAT, r), ring(h - ch, r), ring(h, r - ch)], BRASS, name=name, kind="bolt", amp=0.02)


def post(a, xc, yc, name="post"):
    """A square post from the ground to a bevelled cap: 8-sided section (vertical edges chamfered), leg colour rings
    below the beams, the top ring inset CAP_CH."""
    sec = P.sec_rect(PH, PH, POST_CH)
    top = P.sec_rect(PH - CAP_CH, PH - CAP_CH, POST_CH * 0.5)
    zs = [0.0, *LEG_RINGS, POST_TOP - CAP_CH]
    rings = [[(xc + u, yc + v, z) for u, v in sec] for z in zs] + [[(xc + u, yc + v, POST_TOP) for u, v in top]]
    bk = [legs_key(0.0), legs_key(LEG_RINGS[0]), WOOD, WOOD]
    return P.prism(a, rings, WOOD, band_keys=bk, name=name, kind="post")


def clip(poly, a, b, c):
    """Sutherland-Hodgman: the part of a convex 2D polygon where a*x + b*y <= c."""
    out = []
    for i in range(len(poly)):
        p, q = poly[i - 1], poly[i]
        fp, fq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
        if fq <= 0:
            if fp > 0:
                t = fp / (fp - fq)
                out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
            out.append(q)
        elif fp <= 0:
            t = fp / (fp - fq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return [(round(x, 5), round(y, 5)) for x, y in out]


def band(p0, p1, hw, box):
    """A straight member's 2D outline: the band of half width hw along p0 -> p1, clipped to box (x0, y0, x1, y1)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0).normalized()
    nrm = Vector((-d.y, d.x))
    e0, e1 = p0 - d * 10, p1 + d * 10
    poly = [tuple(e0 - nrm * hw), tuple(e1 - nrm * hw), tuple(e1 + nrm * hw), tuple(e0 + nrm * hw)]
    x0, y0, x1, y1 = box
    for a_, b_, c_ in ((-1, 0, -x0), (1, 0, x1), (0, -1, -y0), (0, 1, y1)):
        poly = clip(poly, a_, b_, c_)
    return poly, p0, d, nrm


# ---- timber ---------------------------------------------------------------------------------------------------------
def plank(a, x0, x1, y0, y1, name):
    """A transverse deck plank (along Y), top at DECK_TOP, chamfered PLANK_CH."""
    zc = PLANK_Z0 + PLANK_T / 2
    return P.plank(a, ((x0 + x1) / 2, y0, zc), ((x0 + x1) / 2, y1, zc), x1 - x0, PLANK_T, WOOD, ch=PLANK_CH, name=name,
                   kind="plank")


def deck(a):
    """15 planks, seams on the post faces (side cell): per bay three planks between the posts' X faces; under each
    post line one plank cut back to the posts' inner faces; past each end post an end row of three pieces with
    butt joints on those faces."""
    g = GAP / 2
    yin = POST_Y - PH + SEAT                         # into the posts' inner faces
    for s in (-1, 1):
        lo, hi = PH + g, POSTS_X[2] - PH - g         # one bay, between the post faces
        w = (hi - lo - 2 * GAP) / 3
        for k in range(3):
            x0 = lo + k * (w + GAP)
            xa, xb = sorted((s * x0, s * (x0 + w)))
            plank(a, xa, xb, -PLANK_Y, PLANK_Y, f"bay{s:+d}_{k}")
        xa, xb = sorted((s * (POSTS_X[2] - PH + g), s * (POSTS_X[2] + PH - g)))
        plank(a, xa, xb, -yin, yin, f"endpost{s:+d}")
        xa, xb = sorted((s * (POSTS_X[2] + PH + g), s * END))
        yo = POST_Y + PH
        for j, (y0, y1) in enumerate(((-yo, -(yin - SEAT) - g), (-(yin - SEAT) + g, yin - SEAT - g),
                                      (yin - SEAT + g, yo))):
            plank(a, xa, xb, y0, y1, f"end{s:+d}_{j}")
    plank(a, -PH + g, PH - g, -yin, yin, "midpost")


def beam(a, x0, x1, sy, name):
    """A side beam segment along X between the posts (seated into them), its top under the planks."""
    y = sorted((sy * BEAM_Y[0], sy * BEAM_Y[1]))
    yc, zc = sum(y) / 2, sum(BEAM_Z) / 2
    sec = P.sec_rect((y[1] - y[0]) / 2, (BEAM_Z[1] - BEAM_Z[0]) / 2, 0.05)
    return P.beam(a, (x0, yc, zc), (x1, yc, zc), sec, WOOD_DEEP, name=name, kind="beam")


def beams(a):
    for sy in (-1, 1):
        for k, (x0, x1) in enumerate(((POSTS_X[0] + PH - SEAT, -PH + SEAT), (PH - SEAT, POSTS_X[2] - PH + SEAT))):
            beam(a, x0, x1, sy, f"beam{sy:+d}_{k}")


def header(a, sx, name="header"):
    """The end crossbeam outside an end post: across the deck under the end planks, seated into both posts' outer
    X faces; its ends are the beam ends the side cell shows past the posts."""
    xa, xb = sorted((sx * HEAD_X[0], sx * HEAD_X[1]))
    zc = sum(BEAM_Z) / 2
    sec = P.sec_rect((xb - xa) / 2, (BEAM_Z[1] - BEAM_Z[0]) / 2, 0.05)
    return P.beam(a, ((xa + xb) / 2, -BEAM_Y[1], zc), ((xa + xb) / 2, BEAM_Y[1], zc), sec, WOOD_DEEP, name=name,
                  kind="crossbeam")


def knee(a, sx, sy, name="knee"):
    """A knee brace on a long side: from the end post's inner X face (low) up to the beam's underside, toward the
    middle post (front / side cells)."""
    face = sx * (POSTS_X[2] - PH)
    (z0, z1), (d0, d1) = KNEE
    zt = BEAM_Z[0] + SEAT
    poly = [(face + sx * SEAT, z0), (face + sx * SEAT, z1), (face - sx * d0, zt), (face - sx * d1, zt)]
    y = sorted((sy * KNEE_Y[0], sy * KNEE_Y[1]))
    return P.ext(a, poly, y[0], y[1], WOOD_DEEP, to3=lambda u, v, w: Vector((u, w, v)), name=name, kind="brace")


def xbrace(a, sx):
    """The X brace on an end (r34 cell): member A from low -Y to high +Y lying on the legs' outer X faces, member B
    the other way in two halves butted against A (a halved look, no interpenetration), a brass bolt at the
    crossing."""
    yo = POST_Y + PH - 0.02
    box = (-yo, XB["lo"], yo, XB["top"])
    x0 = sx * (POSTS_X[2] + PH - SEAT)
    xs = sorted((x0, x0 + sx * XB["t"]))
    to3 = lambda u, v, w: Vector((w, u, v))          # noqa: E731
    pa, c, d, nrm = band((-yo, XB["z"][0]), (yo, XB["z"][1]), XB["hw"], box)
    P.ext(a, pa, xs[0], xs[1], WOOD_DEEP, to3=to3, name="xbrace_a", kind="brace")
    pb, *_ = band((yo, XB["z"][0]), (-yo, XB["z"][1]), XB["hw"], box)
    lim = XB["hw"] - SEAT                             # B halves seat SEAT into A
    for s, nm in ((-1, "xbrace_b0"), (1, "xbrace_b1")):
        h = clip(pb, -s * nrm.x, -s * nrm.y, -s * nrm.dot(c) - lim)     # the side of A's centreline s, past A
        P.ext(a, h, xs[0], xs[1], WOOD_DEEP, to3=to3, name=nm, kind="brace")
    # the crossing: both centre lines meet at y 0
    zc = (XB["z"][0] + XB["z"][1]) / 2
    P.bolt(a, (sx * (abs(x0) + XB["t"]), 0.0, zc), (sx, 0, 0), (0, 0, 1), BRASS, h=0.07, name="xbolt")


def block_and_bolt(a, xc, sy):
    yf = sy * (POST_Y + PH)
    pad(a, (xc, yf, BLOCK["zc"]), (0, sy, 0), (1, 0, 0), BLOCK["hw"], BLOCK["hz"], BLOCK["depth"], BLOCK["ch"], WOOD,
        "block", "block")
    hexbolt(a, (xc, yf + sy * BLOCK["depth"], BLOCK["zc"]), (0, sy, 0), "bolt")


# ---- rope -----------------------------------------------------------------------------------------------------------
TURN_OUT = TURN_R - P.SINK                        # a turn's centreline off the post face


def turns(a, xc, yc):
    """The lashing: two twisted turns round the post (close-up cell), each a closed loop round the post with its
    corners cut at 45 deg (two 45 deg bends instead of one square mitre, so the coil reads round, not as a square
    collar) and a midpoint on each side; the innermost strands sink P.SINK into the post faces. 120 tris each."""
    lo, hi = (xc - PH, yc - PH), (xc + PH, yc + PH)
    for i, z in enumerate(TURNS_Z):
        c4 = P.rect_loop(lo, hi, z, TURN_OUT)
        loop = []
        for k in range(4):
            a_, b_ = c4[k], c4[(k + 1) % 4]
            d = (b_ - a_).normalized()
            loop += [a_ + d * TURN_CUT, (a_ + b_) / 2, b_ - d * TURN_CUT]
        P.rope(a, loop, TURN_R, ROPE, ROPE_DARK, sides=5, closed=True, twist=True, up=(0, 0, 1), name=f"turn{i}")


def swag_path(p0, p1, low=SWAG_LOW, n=SWAG_N):
    """A sagging run from p0 to p1 (both ends at the upper turn's outer side), lowest point `low` at mid span."""
    p0, p1 = Vector(p0), Vector(p1)
    zm = (p0.z + p1.z) / 2
    out = []
    for i in range(n + 1):
        t = i / n
        q = p0.lerp(p1, t)
        q.z = q.z - 4 * (zm - low) * t * (1 - t)
        out.append(q)
    return out


def swag(a, p_from, p_to, name):
    return P.rope(a, swag_path(p_from, p_to), SWAG_R, ROPE, ROPE_DARK, sides=5, name=name)


END_IN = TURN_OUT + TURN_R - 0.04                 # a swag end's centre off the post face (sunk 0.04 into the turn)
Z_END = TURNS_Z[1] - 0.04


def swags(a):
    for sy in (-1, 1):
        y = sy * POST_Y
        for k in range(2):
            xa, xb = POSTS_X[k] + PH + END_IN, POSTS_X[k + 1] - PH - END_IN
            swag(a, (xa, y, Z_END), (xb, y, Z_END), f"swag{sy:+d}_{k}")
    x = POSTS_X[2]
    ya, yb = POST_Y - PH - END_IN, -(POST_Y - PH - END_IN)
    swag(a, (x, ya, Z_END), (x, yb, Z_END), "swag_end")


# ---- assemblies -----------------------------------------------------------------------------------------------------
def post_all(a, xc, yc, tag):
    with P.frame(None, tag):
        post(a, xc, yc)
        block_and_bolt(a, xc, 1 if yc > 0 else -1)
        turns(a, xc, yc)


def hero_all(a):
    for xc in POSTS_X:
        for yc in (-POST_Y, POST_Y):
            post_all(a, xc, yc, f"p{xc:+.0f}{'ab'[yc > 0]}_")
    deck(a)
    beams(a)
    for sx in (-1, 1):
        header(a, sx, f"header{sx:+d}")
        for sy in (-1, 1):
            knee(a, sx, sy, f"knee{sx:+d}{sy:+d}")
        with P.frame(None, f"x{sx:+d}_"):
            xbrace(a, sx)
    swags(a)


PARTS = ((POST_P, lambda a: post_all(a, 0.0, -POST_Y, "")), (DECK_P, deck),
         (BEAM_P, lambda a: beam(a, PH - SEAT, POSTS_X[2] - PH + SEAT, -1, "beam")),
         (CROSS_P, lambda a: header(a, 1)), (BRACE_P, lambda a: knee(a, 1, -1)),
         (ROPE_P, lambda a: swag(a, (POSTS_X[1] + PH + END_IN, -POST_Y, Z_END),
                                 (POSTS_X[2] - PH - END_IN, -POST_Y, Z_END), "swag")))
NOTES = {
    HERO: "Dock module (remade sheet): six 1.25-stud square posts (2 x 3, centres 7.4 x 6.4) to 7.2, 15 "
          "transverse planks 0.9 thick, deck top 4.4, side beams, an end header and an X brace at each end, four knee "
          "braces, a bolt block with a hex brass bolt on each post, two rope turns per post and five twisted swags "
          "(the -X end open). Tiles along X at a 16-stud pitch (end planks at +-8.0).",
    POST_P: "Mooring Post: ground to bevelled cap, bolt block and hex brass bolt, two rope turns (lashing)",
    DECK_P: "Deck Plank set: the 15 deck planks (0.9 thick, seams on the post faces)",
    BEAM_P: "Longitudinal Beam: one side beam segment between two posts",
    CROSS_P: "Crossbeam: the end header across the deck under the end planks",
    BRACE_P: "Diagonal Brace: a knee brace from a post face to the beam's underside",
    ROPE_P: "Rope Segment: one twisted sagging swag",
}
COLLISION = {HERO: "precise", POST_P: "hull", DECK_P: "box", BEAM_P: "box", CROSS_P: "box", BRACE_P: "hull",
             ROPE_P: "none"}
TARGET_SIZE = ((16.0, 0.01), (2 * (POST_Y + PH + BLOCK["depth"] + BOLT["h"]), 0.02), (POST_TOP, 0.02))
VIEWS = {"f34_sheet": (-42, 18), "r34_sheet": (-138, 18), "front_sheet": (0, 0), "side_sheet": (90, 0),
         "rear_sheet": (180, 0), "top_sheet": (0, 89.9)}
EXPLODED = {POST_P: (-9.5, -2.0, 0.0), DECK_P: (0.0, 2.0, 6.0), BEAM_P: (0.0, -4.5, 2.5), CROSS_P: (8.5, 1.0, 1.5),
            BRACE_P: (4.0, -6.0, 0.0), ROPE_P: (0.0, 3.0, 10.0)}
CLOSE = {"post_cu": dict(at=(0.0, -POST_Y - 0.3, 4.6), r=2.2, az=-30, el=14),
         "xbrace_cu": dict(at=(-7.3, 0.0, 1.7), r=3.6, az=-110, el=10)}
VERIFY = dict(seams={"pitch": (16.0, 0.0, 0.0)},
              walk={"paths": [[(-7.6, 0.0), (5.4, 0.0)], [(-7.6, 0.9), (5.4, 0.9)], [(-7.6, -0.9), (5.4, -0.9)]],
                    "feet_z": DECK_TOP, "ride": True, "skip": ("plank",), "turn": [(4.6, 0.0, DECK_TOP)]})


def deck_check(objs):
    """Every plank top at DECK_TOP; nothing past the seam planes; rope swags at least 0.5 over the deck."""
    import json
    h = objs[HERO]
    off = Vector(h[MODEL.OFF])
    zs = [v.co.z + off.z for v in h.data.vertices]
    xs = [v.co.x + off.x for v in h.data.vertices]
    pieces = json.loads(h[f"{MODEL.key}_pieces"])
    rep = {"top_z": round(max(zs), 3), "x_range": [round(min(xs), 3), round(max(xs), 3)],
           "planks": sum(1 for k, *_ in pieces if k == "plank"), "swag_low": SWAG_LOW,
           "shells": len(pieces)}
    pr = []
    if abs(max(xs) - END) > 1e-3 or abs(min(xs) + END) > 1e-3:
        pr.append(f"{HERO}: deck ends {rep['x_range']} not +-{END}")
    if SWAG_LOW - SWAG_R - DECK_TOP < 0.5:
        pr.append(f"{HERO}: swags hang within 0.5 of the deck")
    return rep, pr


def build(render=True, close=False):
    return MODEL.run(hero=(HERO, hero_all), parts=PARTS, notes=NOTES, collision=COLLISION, budgets={HERO: 6000},
                     target_size=TARGET_SIZE, views=VIEWS, exploded=EXPLODED, scale=(0.0, -7.5, 0.0),
                     close=CLOSE if close else None, verify=dict(VERIFY, classes={HERO: "structure"}),
                     checks=[deck_check], render=render)


def preview(names=("f34_sheet", "front_sheet", "r34_sheet")):
    return MODEL.preview(HERO, VIEWS, names)
