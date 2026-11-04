"""075 Wall Walk (references/075.png, remade sheet; no earlier builder) on the shared library (kit_parts / kit_build):
a raised timber wall walk, a deck behind a planked front wall, reached by a stair off its -X end. See
art/blender/renders/models/M075/M075_spec.md.

    import importlib, kit_parts, kit_build, m075
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m075); m075.build()

Build frame (studs): long axis X, front -Y (the banner face), +X right, ground z 0, the deck centred on x 0 / y 0 (the
hero's origin is its bbox bottom centre, so `m075_offset` carries the stair's shift).
- Eight 1.10-square posts at x +-4.85 / +-1.617, y +-1.95: the back row and the front-right post run up past the deck
  to 7.77 (railing posts, bevelled caps); the other three front posts stop 0.95 over the deck (stubs, bevelled caps).
- Rim beams round the deck on the post lines (long rims |y| 1.40-2.225, end rims |x| 4.30-5.125), 1.05 tall, their
  tops the deck's edge; five floor planks along X between them, top z 5.22 (DECK).
- Vertical wall planks under the rims on all four sides (outer faces |y| 2.30, |x| 4.75), diagonal braces on the long
  walls' outer faces (front bays 1 and 3, all three rear bays, as the f34 and r34 cells draw them).
- A railing on the back and the +X end: a rail (0.70 x 0.48) from post to post at z 6.02-6.72, a short baluster
  under the middle of each back bay with a bolt on the rail over it. The front long side is open above the deck (the
  f34 draws stub posts there); the -X end is the stair opening.
- Rope collars (three round turns, r 0.14) round every post at the rim and round the railing posts at the rail;
  each turn is cut where a beam, stringer or tread enters the post, its runs ending 0.04 inside that member.
- The stair: five block treads (rise 0.87 = DECK / 6, run 0.85) between two solid stringers with stepped tops, descending
  -X from the -X end rim between the -X posts; a foot block under the bottom tread.
- A red swallowtail banner (cream stripes and double diamond) on a knobbed rod in a hem sleeve against the front rim
  of the middle bay; six grey footing rocks against the post feet (front and rear).
Every piece is its own closed shell (no booleans), seated 0.002-0.05 into what holds it.
Parts: TimberWallWalkPost, ...RailPost, ...RailBeam, ...RailSegment, ...FloorPlank, ...WallPlank, ...Brace, ...Stairs,
...Banner, ...Rock. Stages 5-6: nothing (the sheet shows no glow, light or effect).
"""
import math

from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_build as B
import kit_parts as P

NUM, TITLE = 75, "Wall Walk"
HERO = "TimberWallWalk"
POST_P, RPOST_P, RAIL_P, SEG_P, FPLANK_P, WPLANK_P, BRACE_P, STAIRS_P, BANNER_P, ROCK_P = (
    HERO + s for s in ("Post", "RailPost", "RailBeam", "RailSegment", "FloorPlank", "WallPlank", "Brace", "Stairs",
                       "Banner", "Rock"))

TIMBER, TIMBER_END, TIMBER_DEEP = "m075_timber", "m075_timber_end", "m075_timber_deep"
ROPE, ROPE_DEEP = "m075_rope", "m075_rope_deep"
BANNER, BANNER_DEEP, CREAM = "m075_banner", "m075_banner_deep", "m075_cream"
STONE, STONE_DARK = "m075_stone", "m075_stone_dark"

# key -> (hex, roughness, metal, emission, low specular). Stage 4 (spec "Stage 4"): sheet medians, calibrated.
PALETTE = {
    TIMBER: ("#A26023", 0.85, 0.0, 0.0, True),
    TIMBER_END: ("#C2843A", 0.8, 0.0, 0.0, True),
    TIMBER_DEEP: ("#693F1A", 0.9, 0.0, 0.0, True),
    ROPE: ("#C29745", 0.95, 0.0, 0.0, True),
    ROPE_DEEP: ("#93702F", 0.95, 0.0, 0.0, True),
    BANNER: ("#E81C1A", 0.9, 0.0, 0.0, True),
    BANNER_DEEP: ("#8E1212", 0.9, 0.0, 0.0, True),
    CREAM: ("#F2E6CF", 0.9, 0.0, 0.0, True),
    STONE: ("#8C8A8A", 0.9, 0.0, 0.0, True),
    STONE_DARK: ("#6E6C6C", 0.9, 0.0, 0.0, True),
}
TARGETS = {TIMBER: ((0xB5, 0x61, 0x1F), "brown"), ROPE: ((0xF6, 0xB7, 0x4B), "all"),
           BANNER: ((0xFC, 0x1E, 0x16), "vivid"), STONE: ((0xAA, 0xA2, 0x9B), "stone"),
           CREAM: ((0xFE, 0xEA, 0xCC), "all")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)


def mix(k1, k2, t):
    return P.mix(k1, k2, t, step=0.05)


Z = Vector((0.0, 0.0, 1.0))

# ---- layout (spec "Brief": 19.15 sheet px / stud from the side cell's 5-stud figure) ---------------------------------
N_STEPS = 5                     # treads between the ground and the deck
RISE = 0.87                     # HOUSE_RULES' largest riser
DECK = RISE * (N_STEPS + 1)     # 5.22: the deck top (sheet 5.3)
RUN = 0.85
TREAD_T = RISE - 0.03          # chunky block treads, 0.03 over the next one down
SEAT = 0.03                     # beams into the post faces
PH, PCH = 0.55, 0.06            # post half width, vertical edge chamfer
PX = (-4.85, -4.85 / 3, 4.85 / 3, 4.85)
YP = 1.95                       # post rows |y|
TOP_TALL, TOP_STUB = DECK + 2.55, DECK + 0.95
CAP_H, CAP_IN = 0.22, 0.17      # bevelled cap: height, inset
FOOT_BAND = 0.32                # the tall corner posts' pale foot band (the r34's plinths)
RIM_Z = (DECK - 1.06, DECK - 0.01)
RIM_Y = (YP - PH, YP + 0.275)   # long rims |y|: inner face on the posts' inner faces
END_X = (PX[3] - PH, PX[3] + 0.275)   # end rims |x|
PLANK_T, PLANK_GAP, N_PLANKS = 0.30, 0.02, 5
WALL_OUT, WALL_T = 2.30, 0.30   # long walls' outer face |y|, plank thickness
END_WALL_OUT = 4.75             # end walls' outer face |x|
WALL_TOP = RIM_Z[0] + 0.02
BRACE_W, BRACE_T = 0.50, 0.28
RAIL_Z, RAIL_HY = (DECK + 0.80, DECK + 1.50), 0.24
BAL_H = 0.20                    # baluster half width
# rope collars (twisted, 4 sides): turn radius, centre offset off the post faces, turn heights
RT = 0.14
ROPE_SIDES = 5                  # round turns with spiral strands (P.rope twist=False; twisted 4-side runs read as plates)
TURN_OFF = RT * P.turn_ext(ROPE_SIDES)[0] - P.SINK
END_SINK = 0.04                 # a cut run's end this deep inside the member it meets
MIN_RUN = 0.25                  # shorter runs (hidden corners) are left out
COLLAR_RIM = (DECK - 0.90, DECK - 0.68, DECK - 0.46)      # under the planks (their underside DECK - 0.30)
COLLAR_RAIL = (DECK + 0.93, DECK + 1.15, DECK + 1.37)
# stair: top tread's back edge sunk 0.02 into the -X end rim; stringers in line with the -X posts
X_TOP = -(END_X[1] - 0.02)
STR_Y = (YP - PH, YP - PH + 0.35)        # |y| 1.55-1.90
TREAD_HY = STR_Y[0] + 0.02
LIP = 0.40                      # the stringers' stepped top over the treads
THROAT = 1.60                   # their sloped underside below the nosing line
STR_TOP = DECK - 0.30           # the top-end block beside the -X posts
# banner (front, middle bay) and rocks
ROD = dict(r=0.11, x=0.72, z=5.03, knob=0.12)     # over the stub posts' collars (tops DECK - 0.32)
SLEEVE_IN = ROD["r"] / math.cos(math.pi / 8) + 0.008
SLEEVE_T = 0.06
ROD_Y = -(RIM_Y[1] + SLEEVE_IN + SLEEVE_T - 0.02)
CLOTH = dict(x=0.70, t=0.08, tips=1.00, notch=1.70)
EMB = dict(z=3.15, rings=((0.50, 0.98, 0.13), (0.24, 0.48, 0.10)))
STRIPE_IN, STRIPE_W, STRIPE_Z0 = 0.09, 0.07, 1.55
ROCK = dict(size=(2.10, 1.60, 1.15), seed=75)
ROCKS = ((-4.85, -1, 1), (-2.05, -1, 2), (4.85, -1, 3), (3.20, 1, 4), (-1.40, 1, 5), (-4.85, 1, 6))


def tall(i, f):
    """Post i (0..3 along X), row f (-1 front, +1 back) is a railing post: the back row and the front-right."""
    return f > 0 or i == 3


# ---- member registry (axis boxes the collars are cut against) -----------------------------------------------------------
MEMBERS = []
KEEP_OUT = []                   # boxes no collar run may enter (the stair opening's walk lane)


def member(name, lo, hi):
    MEMBERS.append((name, Vector(lo), Vector(hi)))


def box_member(a, lo, hi, key, name, kind, **kw):
    member(name, lo, hi)
    return P.box(a, lo, hi, key, name=name, kind=kind, **kw)


# ---- timber ----------------------------------------------------------------------------------------------------------------
def post(a, x, y, top, name, foot=False):
    """A square chamfered post from the ground to `top`: a bevelled cap (cut wood) and, on the tall corner posts, a
    pale foot band."""
    sec = P.sec_rect(PH, PH, PCH)
    zs = ([0.0, FOOT_BAND] if foot else [0.0]) + [top - CAP_H]
    rings = [[(x + u, y + v, z) for u, v in sec] for z in zs]
    rings.append([(x + u, y + v, top) for u, v in P.sec_rect(PH - CAP_IN, PH - CAP_IN, PCH * 0.6)])
    bands = ([mix(TIMBER, TIMBER_END, 0.35)] if foot else []) + [None, mix(TIMBER, TIMBER_END, 0.5)]
    member(name, (x - PH, y - PH, 0.0), (x + PH, y + PH, top))
    return P.prism(a, rings, TIMBER, band_keys=bands, cap_keys=(None, TIMBER_END), name=name, kind="post")


def beam_x(a, x0, x1, y0, y1, z0, z1, key, name, kind, ch=0.05):
    member(name, (x0, y0, z0), (x1, y1, z1))
    return P.plank(a, (x0, (y0 + y1) / 2, (z0 + z1) / 2), (x1, (y0 + y1) / 2, (z0 + z1) / 2), y1 - y0, z1 - z0, key,
                   ch=ch, cap_keys=(TIMBER_END, TIMBER_END), name=name, kind=kind)


def beam_y(a, x0, x1, y0, y1, z0, z1, key, name, kind, ch=0.05):
    member(name, (x0, y0, z0), (x1, y1, z1))
    return P.plank(a, ((x0 + x1) / 2, y0, (z0 + z1) / 2), ((x0 + x1) / 2, y1, (z0 + z1) / 2), x1 - x0, z1 - z0, key,
                   ch=ch, cap_keys=(TIMBER_END, TIMBER_END), name=name, kind=kind)


def rims(a):
    """The deck's rim beams: three spans per long side between the posts (ends SEAT into the post faces), one across
    each end between the corner posts' inner faces; tops 0.01 under the planks (the -X end rim, the stair's landing,
    level with them)."""
    for f in (-1, 1):
        y0, y1 = sorted((f * RIM_Y[0], f * RIM_Y[1]))
        for i in range(3):
            beam_x(a, PX[i] + PH - SEAT, PX[i + 1] - PH + SEAT, y0, y1, *RIM_Z, TIMBER, f"rim{'fb'[f > 0]}{i}", "rim")
    for s in (-1, 1):
        x0, x1 = sorted((s * END_X[0], s * END_X[1]))
        top = DECK if s < 0 else RIM_Z[1]
        beam_y(a, x0, x1, -(YP - PH + SEAT), YP - PH + SEAT, RIM_Z[0], top, TIMBER, f"rim{'lr'[s > 0]}", "rim")


def deck(a):
    """Five planks along X between the rims (sunk 0.02 into the long rims; 0.003 off the end rims), one butt joint
    each, staggered; tops at DECK."""
    w = (2 * (RIM_Y[0] + 0.02) - (N_PLANKS - 1) * PLANK_GAP) / N_PLANKS
    xe = END_X[0] - 0.003
    joints = (-1.6, 2.1, -0.4, 1.3, -2.4)
    for k in range(N_PLANKS):
        y0 = -(RIM_Y[0] + 0.02) + k * (w + PLANK_GAP)
        yc = y0 + w / 2
        for j, (x0, x1) in enumerate(P.butt_spans(-xe, xe, [joints[k]], gap=0.03)):
            nm = f"plank{k}_{j}"
            p = P.plank(a, (x0, yc, DECK - PLANK_T / 2), (x1, yc, DECK - PLANK_T / 2), w, PLANK_T,
                        mix(TIMBER, TIMBER_DEEP, 0.10 * ((k + j) % 2)), ch=0.05, cap_keys=(TIMBER_END, TIMBER_END),
                        name=nm, kind="plank", amp=0.05)
            P.texture(a, p.vs, 0.03, P.seed(nm), scale=0.5)
            member(nm, (x0, y0, DECK - PLANK_T), (x1, y0 + w, DECK))


def wall_plank(a, c, along, out, w, z0, z1, key, name):
    """A vertical wall plank: centre (x, y) on its outer face line, `along` the wall, `out` its outward normal; the two
    outer edges chamfered (the V seams between planks)."""
    along, out = Vector(along), Vector(out)
    cc = Vector((c[0], c[1], 0.0)) - out * (WALL_T / 2)
    sec = P.sec_rect(w / 2, WALL_T / 2, 0.08, corners=("+u+v", "-u+v"))
    p = P.beam(a, cc + Vector((0, 0, z0)), cc + Vector((0, 0, z1)), sec, key, up=out, name=name, kind="wallplank")
    P.texture(a, p.vs, 0.03, P.seed(name), scale=0.5)
    return p


def wall_run(a, t0, t1, n, fixed, axis, out, tag):
    """n planks filling t0..t1 along `axis` ("x": a long wall at y = fixed, "y": an end wall at x = fixed)."""
    gap = 0.02
    w = (t1 - t0 - (n - 1) * gap) / n
    for k in range(n):
        t = t0 + w / 2 + k * (w + gap)
        c = (t, fixed) if axis == "x" else (fixed, t)
        along = (1, 0, 0) if axis == "x" else (0, 1, 0)
        wall_plank(a, c, along, out, w, 0.0, WALL_TOP, mix(TIMBER, TIMBER_DEEP, 0.12 + 0.08 * (k % 2)), f"{tag}{k}")
    return w


def walls(a):
    for f in (-1, 1):
        for i in range(3):
            wall_run(a, PX[i] + PH - 0.02, PX[i + 1] - PH + 0.02, 3, f * WALL_OUT, "x", (0, f, 0),
                     f"wall{'fb'[f > 0]}{i}_")
    for s in (-1, 1):
        wall_run(a, -(YP - PH + 0.02), YP - PH + 0.02, 4, s * END_WALL_OUT, "y", (s, 0, 0), f"wall{'lr'[s > 0]}_")


def _clip(poly, inside, cut):
    """Sutherland-Hodgman: keep the part of a 2D polygon where inside(p) holds (cut(p, q) = the crossing point)."""
    out = []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        if inside(p):
            out.append(p)
            if not inside(q):
                out.append(cut(p, q))
        elif inside(q):
            out.append(cut(p, q))
    return out


def brace_poly(x_lo, x_hi, top_left, z_top=RIM_Z[0] - 0.02, w=BRACE_W):
    """The brace outline in (x, z): a band w wide along the bay's diagonal (top at the left or the right post), cut
    to the bay x_lo..x_hi (post faces, sunk 0.02) and to 0..z_top."""
    a0 = Vector((x_lo, z_top)) if top_left else Vector((x_lo, 0.0))
    a1 = Vector((x_hi, 0.0)) if top_left else Vector((x_hi, z_top))
    d = (a1 - a0).normalized()
    n = Vector((-d.y, d.x)) * (w / 2)
    e = d * 3.0
    poly = [a0 - e - n, a1 + e - n, a1 + e + n, a0 - e + n]
    for k, lim, sgn in ((0, x_lo, 1), (0, x_hi, -1), (1, 0.0, 1), (1, z_top, -1)):
        poly = _clip(poly, lambda p, k=k, lim=lim, sgn=sgn: sgn * (p[k] - lim) >= -1e-9,
                     lambda p, q, k=k, lim=lim: p + (q - p) * ((lim - p[k]) / (q[k] - p[k])))
    return [(p.x, p.y) for p in poly]


def brace(a, i, f, top_left, name):
    """A diagonal brace on a long wall's outer face in bay i (sunk 0.02 into the planks)."""
    x_lo, x_hi = PX[i] + PH - 0.02, PX[i + 1] - PH + 0.02
    poly = brace_poly(x_lo, x_hi, top_left)
    y0, y1 = sorted((f * (WALL_OUT - 0.02), f * (WALL_OUT - 0.02 + BRACE_T)))
    return P.ext(a, poly, y0, y1, mix(TIMBER, TIMBER_END, 0.15), to3=lambda u, v, w_: Vector((u, w_, v)), name=name,
                 kind="brace")


# front: bay 0 top at -X, bay 2 top at +X ("\" both, the f34); rear (the r34): bay 2 top at -X, bay 1 top at +X,
# bay 0 top at -X
BRACES = ((0, -1, True), (2, -1, True), (0, 1, True), (1, 1, False), (2, 1, True))


def braces(a):
    for i, f, tl in BRACES:
        brace(a, i, f, tl, f"brace{'fb'[f > 0]}{i}")


def railing(a, balusters=True):
    """Back rail spans and the +X end rail (ends SEAT into the post faces); balusters under the back bays' middles
    (into the rim top and the rail underside) with a bolt on the rail's outer face over each."""
    for i in range(3):
        beam_x(a, PX[i] + PH - SEAT, PX[i + 1] - PH + SEAT, YP - RAIL_HY, YP + RAIL_HY, *RAIL_Z, TIMBER, f"rail{i}",
               "rail")
    beam_y(a, PX[3] - RAIL_HY, PX[3] + RAIL_HY, -(YP - PH + SEAT), YP - PH + SEAT, *RAIL_Z, TIMBER, "rail_end", "rail")
    if balusters:
        for i in range(3):
            baluster(a, (PX[i] + PX[i + 1]) / 2, f"bal{i}")


def baluster(a, x, name, z0=None, z1=None):
    z0 = RIM_Z[1] - 0.02 if z0 is None else z0
    z1 = RAIL_Z[0] + 0.02 if z1 is None else z1
    P.post(a, (x, YP), z0, z1, BAL_H, mix(TIMBER, TIMBER_DEEP, 0.1), ch=0.04, name=name, kind="baluster")
    P.bolt(a, (x, YP + RAIL_HY, (RAIL_Z[0] + RAIL_Z[1]) / 2), (0, 1, 0), (0, 0, 1), TIMBER_DEEP, h=0.10, proud=0.05,
           name=name + "_bolt")


# ---- stair -------------------------------------------------------------------------------------------------------------------
def stair_frame():
    """Local frame of P.stairs (steps down toward local -Y) -> descending -X from X_TOP."""
    return Matrix.Translation((X_TOP, 0.0, 0.0)) @ Matrix.Rotation(math.radians(-90.0), 4, "Z")


def stringer_profile():
    """(t, z) outline of a stringer, t = X_TOP - x: the top end against the -X post face, the stepped top LIP over
    each tread (a block to STR_TOP beside the post), the sloped underside THROAT under the nosing line, the foot on
    the ground."""
    t_top = X_TOP - (PX[0] - PH) - 0.02          # the post's -X face, sunk 0.02
    tops = [DECK - RISE * (i + 1) for i in range(N_STEPS)]
    t_end = RUN * N_STEPS
    slope = RISE / RUN

    def under(t):
        return DECK - slope * t - THROAT
    t_g = (DECK - THROAT) / slope                   # the underside meets the ground
    prof = [(t_top, under(t_top)), (t_g, 0.0), (t_end, 0.0), (t_end, tops[-1] + LIP)]
    for i in range(N_STEPS - 1, 0, -1):
        prof += [(RUN * i, tops[i] + LIP), (RUN * i, tops[i - 1] + LIP if i > 1 else STR_TOP)]
    prof.append((t_top, STR_TOP))
    return prof


def stairs(a):
    """Five treads (P.stairs, one board each) between two solid stringers, a foot block under the bottom tread."""
    with P.frame(stair_frame(), ""):
        P.stairs(a, -TREAD_HY, TREAD_HY, 0.0, DECK - RISE, N_STEPS, RISE, RUN, TIMBER, tread_t=TREAD_T, boards=1, gap=0.0,
                 support="none", name="stair")
    for i in range(N_STEPS):
        zt = DECK - RISE * (i + 1)
        member(f"tread{i}", (X_TOP - RUN * (i + 1), -TREAD_HY, zt - TREAD_T), (X_TOP - RUN * i, TREAD_HY, zt))
    prof = stringer_profile()
    for s in (-1, 1):
        y0, y1 = sorted((s * STR_Y[0], s * STR_Y[1]))
        nm = f"stringer{'lr'[s > 0]}"
        P.ext(a, prof, y0, y1, TIMBER, to3=lambda u, v, w_: Vector((X_TOP - u, w_, v)), name=nm, kind="stringer")
        member(nm, (X_TOP - RUN * N_STEPS, y0, 0.0), (PX[0] - PH, y1, STR_TOP))
    zb = DECK - RISE * N_STEPS - TREAD_T - 0.003
    if zb > 0.1:                                     # thin treads: a foot block under the bottom one
        x0, x1 = X_TOP - RUN * N_STEPS, X_TOP - RUN * (N_STEPS - 1)
        P.box(a, (x0 + 0.12, -(TREAD_HY - 0.35), 0.0), (x1 - 0.12, TREAD_HY - 0.35, zb),
              mix(TIMBER, TIMBER_DEEP, 0.3), name="stair_foot", kind="foot")
    KEEP_OUT.append((Vector((-30.0, -(YP - PH), 0.0)), Vector((PX[0] + PH, YP - PH, DECK - 0.1))))


# ---- rope collars --------------------------------------------------------------------------------------------------------------
def _covered(p, z):
    for _, lo, hi in MEMBERS:
        if lo.z <= z <= hi.z and lo.x <= p.x <= hi.x and lo.y <= p.y <= hi.y:
            return True
    return False


def _seg_box(p, q, lo, hi):
    """Parameter interval (t0, t1) of segment p..q inside the xy rectangle lo..hi, or None."""
    t0, t1 = 0.0, 1.0
    for k in (0, 1):
        d = q[k] - p[k]
        if abs(d) < 1e-12:
            if p[k] < lo[k] or p[k] > hi[k]:
                return None
            continue
        a_, b_ = (lo[k] - p[k]) / d, (hi[k] - p[k]) / d
        t0, t1 = max(t0, min(a_, b_)), min(t1, max(a_, b_))
    return (t0, t1) if t0 < t1 else None


def collar_runs(xc, yc, z, closed_only=False):
    """One collar turn round the post at (xc, yc), height z: the offset loop round its section, cut where a member
    enters the post (each run ends END_SINK inside the member). Returns [(path, closed)]."""
    sec = [Vector((xc + u, yc + v, z)) for u, v in P.sec_rect(PH, PH, PCH)]
    loop = P.hull_loop(sec, (xc, yc, z), Z, Vector((1, 0, 0)), TURN_OFF, 8)
    if closed_only:
        return [(loop, True)]
    n = len(loop)
    pts = []
    for i in range(n):
        p, q = loop[i], loop[(i + 1) % n]
        L = (q - p).length
        ts = set()
        for _, lo, hi in MEMBERS:
            if not lo.z <= z <= hi.z:
                continue
            iv = _seg_box(p, q, lo, hi)
            if iv is None:
                continue
            for t in (iv[0] + END_SINK / L, iv[1] - END_SINK / L):
                if 1e-4 < t < 1 - 1e-4:
                    ts.add(round(t, 6))
        pts.append(p)
        pts += [p + (q - p) * t for t in sorted(ts)]
    m = len(pts)
    cov = [_covered((pts[i] + pts[(i + 1) % m]) / 2, z) for i in range(m)]
    if not any(cov):
        return [(loop, True)]
    if all(cov):
        return []
    runs = []
    start = next(i for i in range(m) if cov[i - 1] and not cov[i])
    i, run = start, [pts[start]]
    for _ in range(m):
        if cov[i]:
            if len(run) > 1:
                runs.append(run)
            run = [pts[(i + 1) % m]]
        else:
            run.append(pts[(i + 1) % m])
        i = (i + 1) % m
    if len(run) > 1:
        runs.append(run)
    out = []
    for r in runs:
        if sum((r[k + 1] - r[k]).length for k in range(len(r) - 1)) < MIN_RUN:
            continue
        if any(all(lo[k] <= p[k] <= hi[k] for k in range(3)) for p in r for lo, hi in KEEP_OUT):
            continue
        out.append((r, False))
    return out


def collar(a, xc, yc, zs, tag, closed_only=False):
    out = []
    for ti, z in enumerate(zs):
        for ri, (path, closed) in enumerate(collar_runs(xc, yc, z, closed_only)):
            out.append(P.rope(a, path, RT, ROPE, ROPE_DEEP, sides=ROPE_SIDES, closed=closed, twist=False,
                              up=(0, 0, 1),
                              name=f"{tag}t{ti}_{ri}", kind="rope_turn"))
    return out


def collars(a):
    for f in (-1, 1):
        for i, x in enumerate(PX):
            tag = f"c{'fb'[f > 0]}{i}_"
            collar(a, x, f * YP, COLLAR_RIM, tag + "rim_")
            if tall(i, f):
                collar(a, x, f * YP, COLLAR_RAIL, tag + "rail_")


# ---- banner --------------------------------------------------------------------------------------------------------------------
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


def banner(a, xm=0.0, y=ROD_Y, rod_z=ROD["z"]):
    """(m072 recipe) The rod with knobbed ends in a dark-red hem sleeve (the sleeve against the front rim, sunk 0.02),
    the red swallowtail cloth with two cream edge stripes and the cream double diamond on its front face."""
    x0, x1 = xm - ROD["x"], xm + ROD["x"]
    P.log(a, (x0, y, rod_z), (x1, y, rod_z), ROD["r"], TIMBER_END, sides=8, end_key=TIMBER_END, name="rod",
          kind="rod")
    for sg, xe in ((-1, x0), (1, x1)):
        knob(a, (xe + sg * (ROD["knob"] - 0.03), y, rod_z), ROD["knob"], f"knob{sg:+d}")
    c0, c1 = xm - CLOTH["x"], xm + CLOTH["x"]
    P.sleeve(a, (c0 - 0.04, y, rod_z), (c1 + 0.04, y, rod_z), SLEEVE_IN, SLEEVE_IN + SLEEVE_T, BANNER_DEEP, sides=8,
             name="hem", kind="hem", amp=0.02)
    top = rod_z - SLEEVE_IN - 0.015
    outline = [(c0, top), (c1, top), (c1, CLOTH["tips"]), (xm, CLOTH["notch"]), (c0, CLOTH["tips"])]
    yf, yb = y - CLOTH["t"] / 2, y + CLOTH["t"] / 2
    cloth = P.ext(a, outline, yf, yb, BANNER, to3=lambda u, v, w: Vector((u, w, v)), name="cloth", kind="banner",
                  amp=0.02)
    P.texture(a, cloth.vs, 0.02, P.seed("cloth"), scale=0.4)
    e0, e1 = yf + 0.005, yf - 0.015
    for i, (hw, hh, line) in enumerate(EMB["rings"]):
        _diamond_ring(a, xm, EMB["z"], hw, hh, line, e0, e1, f"emblem{i}")
    zt = rod_z - SLEEVE_IN - SLEEVE_T - 0.06
    for sg, xe in ((1, c0), (-1, c1)):
        xa, xb = sorted((xe + sg * STRIPE_IN, xe + sg * (STRIPE_IN + STRIPE_W)))
        P.ext(a, [(xa, STRIPE_Z0), (xb, STRIPE_Z0), (xb, zt), (xa, zt)], e1, e0, CREAM,
              to3=lambda u, v, w: Vector((u, w, v)), name=f"stripe{sg:+d}", kind="emblem", amp=0.02)


# ---- rocks -----------------------------------------------------------------------------------------------------------------------
def rock_points(size, seed_):
    """(m073 footing stone) The sheet's chunky flat-topped rock: a chamfered base ring on z 0, a low waist, then the
    sides slope in to a smaller flat chamfered top; jittered (shrinking only), the top a little off centre."""
    r = P.rng(f"rock{seed_}")
    hx, hy, h = size[0] / 2, size[1] / 2, size[2]
    pts = []
    for (u, v) in P.sec_rect(hx, hy, 0.30):
        k = r.uniform(0.90, 1.0)
        pts.append(Vector((u * k, v * k, 0.0)))
    for (u, v) in P.sec_rect(hx, hy, 0.30):
        k = r.uniform(0.93, 0.99)
        pts.append(Vector((u * k, v * k, h * r.uniform(0.20, 0.28))))
    ox, oy = r.uniform(-0.08, 0.08), r.uniform(-0.05, 0.05)
    for (u, v) in P.sec_rect(hx * 0.58, hy * 0.58, 0.16):
        pts.append(Vector((u + ox, v + oy, h * r.uniform(0.95, 1.0))))
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


def rock_place(pts, cx, f, tree):
    """(m072) Slide the rock from outside (side f) toward the wall until it meets it (bisection); returns its y."""
    cos, tris = _hull_tris(pts)

    def hits(y):
        t = BVHTree.FromPolygons([c + Vector((cx, y, 0)) for c in cos], tris)
        return bool(t.overlap(tree))
    far, near = f * 6.0, 0.0
    for _ in range(30):
        mid = (far + near) / 2
        if hits(mid):
            near = mid
        else:
            far = mid
    return far + f * 0.002


def rock(a, cx, f, sd, tree=None, name="rock"):
    pts = rock_points(ROCK["size"], ROCK["seed"] * 10 + sd)
    y = rock_place(pts, cx, f, tree) if tree is not None else 0.0
    p = P.hull(a, [q + Vector((cx, y, 0)) for q in pts], STONE, name=name, kind="rock", amp=0.04)
    P.paint(a, [fc for fc in p.fs if fc.is_valid and fc.calc_center_median().z < 0.30], mix(STONE, STONE_DARK, 0.5))
    P.texture(a, p.vs, 0.05, ROCK["seed"] + sd, scale=0.9)
    P.GEO.setdefault("rocks", {})[name] = [round(cx, 3), round(y, 3)]
    return p


def solid_tree(a):
    a.bm.verts.ensure_lookup_table()
    return BVHTree.FromBMesh(a.bm)


# ---- assemblies -----------------------------------------------------------------------------------------------------------------
def frame_all(a):
    """Posts, rims, deck, walls, braces, railing, stair (members registered), then the collars."""
    MEMBERS.clear()
    KEEP_OUT.clear()
    for f in (-1, 1):
        for i, x in enumerate(PX):
            post(a, x, f * YP, TOP_TALL if tall(i, f) else TOP_STUB, f"post{'fb'[f > 0]}{i}",
                 foot=tall(i, f) and i in (0, 3))
    rims(a)
    deck(a)
    walls(a)
    braces(a)
    railing(a)
    stairs(a)
    # runs under the deck, inside the planked box, are never seen: left out (their ends would sit in the rims' inner
    # corners)
    KEEP_OUT.append((Vector((-END_X[0], -RIM_Y[0], 0.0)), Vector((END_X[0], RIM_Y[0], DECK - 0.1))))
    collars(a)


def hero_all(a):
    frame_all(a)
    banner(a)
    tree = solid_tree(a)
    for x, f, sd in ROCKS:
        rock(a, x, f, sd, tree, f"rock{sd}")


# parts ------------------------------------------------------------------------------------------------------------------------------
def post_part(a):
    """Upright Post (Main): a railing post from the ground to 7.77 with its foot band, a rope collar at the rim and
    one at the rail (closed turns)."""
    MEMBERS.clear()
    KEEP_OUT.clear()
    post(a, 0.0, 0.0, TOP_TALL, "post", foot=True)
    collar(a, 0.0, 0.0, COLLAR_RIM, "rim_", closed_only=True)
    collar(a, 0.0, 0.0, COLLAR_RAIL, "rail_", closed_only=True)


def rpost_part(a):
    """Railing Post (Top): the stub post's top length (deck to cap, 2.15) with its cap and a bolt."""
    post(a, 0.0, 0.0, 2.15, "rpost")
    P.bolt(a, (0.0, -PH, 1.2), (0, -1, 0), (0, 0, 1), TIMBER_DEEP, h=0.10, proud=0.05, name="rpost_bolt")


def rail_part(a):
    beam_x(a, -1.5, 1.5, -RAIL_HY, RAIL_HY, 0.0, RAIL_Z[1] - RAIL_Z[0], TIMBER, "rail", "rail")


def seg_part(a):
    """Railing Segment: one back bay's rail span with its baluster and bolt."""
    L = PX[1] - PX[0] - 2 * PH + 2 * SEAT
    h = RAIL_Z[0] - RIM_Z[1]
    beam_x(a, -L / 2, L / 2, YP - RAIL_HY, YP + RAIL_HY, h, h + RAIL_Z[1] - RAIL_Z[0], TIMBER, "rail", "rail")
    P.post(a, (0.0, YP), 0.0, h + 0.02, BAL_H, mix(TIMBER, TIMBER_DEEP, 0.1), ch=0.04, name="bal", kind="baluster")
    P.bolt(a, (0.0, YP + RAIL_HY, h + (RAIL_Z[1] - RAIL_Z[0]) / 2), (0, 1, 0), (0, 0, 1), TIMBER_DEEP, h=0.10,
           proud=0.05, name="bal_bolt")


def fplank_part(a):
    w = (2 * (RIM_Y[0] + 0.02) - (N_PLANKS - 1) * PLANK_GAP) / N_PLANKS
    P.plank(a, (-4.0, 0.0, PLANK_T / 2), (4.0, 0.0, PLANK_T / 2), w, PLANK_T, TIMBER, ch=0.05,
            cap_keys=(TIMBER_END, TIMBER_END), name="plank", kind="plank")


def wplank_part(a):
    """Wall Plank (vertical): one bay's three planks."""
    wall_run(a, -0.985, 0.985, 3, 0.0, "x", (0, -1, 0), "wplank")


def brace_part(a):
    poly = brace_poly(-0.985, 0.985, True)
    P.ext(a, poly, 0.0, BRACE_T, mix(TIMBER, TIMBER_END, 0.15), to3=lambda u, v, w_: Vector((u, w_, v)), name="brace",
          kind="brace")


def stairs_part(a):
    MEMBERS.clear()
    KEEP_OUT.clear()
    stairs(a)


def banner_part(a):
    banner(a, 0.0, 0.0)


def rock_part(a):
    rock(a, 0.0, -1, 1, None, "rock")


PARTS = ((POST_P, post_part), (RPOST_P, rpost_part), (RAIL_P, rail_part), (SEG_P, seg_part), (FPLANK_P, fplank_part),
         (WPLANK_P, wplank_part), (BRACE_P, brace_part), (STAIRS_P, stairs_part), (BANNER_P, banner_part),
         (ROCK_P, rock_part))

NOTES = {
    HERO: "Timber wall walk (sheet 075): a 9.7 x 2.8 deck (top 5.22) on rim beams and eight 1.10-square posts, a "
          "planked wall with diagonal braces under it on all sides, a railing (rail 6.02-6.72) on the back and the +X "
          "end with balusters, rope collars at the rim and the rail, a five-step stair (rises 0.87, run 0.85) with "
          "solid stringers off the -X end, a red banner on the front, six footing rocks. Walkable: collision precise.",
    POST_P: "Upright Post (Main): 1.10 square, 7.77 tall with a bevelled cap and foot band, two three-turn rope collars",
    RPOST_P: "Railing Post (Top): the stub post's top length with its bevelled cap and a bolt",
    RAIL_P: "Railing Beam: a 3.0 x 0.48 x 0.70 rail",
    SEG_P: "Railing Segment: one bay's rail span with its baluster and bolt",
    FPLANK_P: "Floor Plank: one 8.0 x 0.55 x 0.30 deck plank",
    WPLANK_P: "Wall Plank (vertical): one bay's three vertical planks, 4.18 tall",
    BRACE_P: "Support Brace (diagonal): one bay's diagonal brace, 0.50 x 0.28",
    STAIRS_P: "Stair Steps: five block treads between solid stepped stringers, rises 0.87, run 0.85",
    BANNER_P: "Banner: knobbed rod, hem sleeve, red swallowtail with cream stripes and double diamond",
    ROCK_P: "Footing Rock: grey faceted rock",
}
COLLISION = {HERO: "precise", POST_P: "box", RPOST_P: "box", RAIL_P: "box", SEG_P: "box", FPLANK_P: "box",
             WPLANK_P: "box", BRACE_P: "hull", STAIRS_P: "precise", BANNER_P: "none", ROCK_P: "hull"}
BUDGETS = {HERO: 6000}
TARGET_SIZE = None
VIEWS = {"f34_sheet": (-28, 26), "r34_sheet": (-156, 22), "front_sheet": (0, 0), "side_sheet": (-90, 0),
         "rear_sheet": (180, 0), "top_sheet": (0, 89.9)}
EXPLODED = {POST_P: (-14.0, 0.0, 0.0), STAIRS_P: (-9.5, 0.0, 0.0), RPOST_P: (-12.0, 0.0, 9.0), RAIL_P: (-7.0, 0.0, 9.6),
            SEG_P: (-1.5, 0.0, 8.6), FPLANK_P: (-3.5, 0.0, 6.6), BRACE_P: (-4.6, 0.0, 0.0), WPLANK_P: (-1.4, 0.0, 0.0),
            BANNER_P: (2.6, 0.0, 1.2), ROCK_P: (5.2, 0.0, 0.0)}
WALK = {"paths": [[(-11.0, y), (3.6, y)] for y in (-0.03, 0.0, 0.03)], "feet_z": 0.0, "ride": True,
        "skip": ("plank", "rim", "foot"), "turn": [(-3.0, 0.0, DECK), (0.0, 0.0, DECK), (3.0, 0.0, DECK)]}
VERIFY = dict(cls="structure", walk=WALK)
COMPARE = {"f34": {"box": (20, 180, 508, 512), "view": VIEWS["f34_sheet"][:2]},
           "r34": {"box": (520, 180, 1010, 512), "view": VIEWS["r34_sheet"][:2]},
           "front": {"box": (18, 595, 300, 765), "view": (0, 0)},
           "side": {"box": (316, 595, 450, 765), "view": (-90, 0)},
           "rear": {"box": (518, 595, 760, 765), "view": (180, 0)},
           "top": {"box": (768, 595, 1012, 765), "view": (0, 89.9)}}


def _tree(o):
    me = o.data
    return BVHTree.FromPolygons([o.matrix_world @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])


def deck_check(objs):
    """The walk surface: deck samples at DECK (rays down over the planks), tread tops (even risers to the deck), the
    rail's height over the deck, the stair opening between the -X posts (collars included) and the deck's clear width
    between the back rail and the front edge."""
    h = objs[HERO]
    tree = _tree(h)
    base = h.matrix_world.translation.z

    def down(x, y):
        hit = tree.ray_cast(MODEL.at(h, (x, y, 20.0)), Vector((0, 0, -1)))[0]
        return round(hit.z - base, 3) if hit else None

    def side(p, d):
        q = tree.ray_cast(MODEL.at(h, p), Vector(d))
        return round(q[3], 3) if q[0] is not None else None
    deck = [down(x, y) for x in (-3.9, -2.0, 0.0, 2.0, 3.9) for y in (-1.0, -0.5, 0.0, 0.5, 1.0)]
    treads = [down(X_TOP - RUN * (i + 0.5), 0.0) for i in range(N_STEPS)]
    landing = down(X_TOP + 0.4, 0.0)
    levels = [0.0] + list(reversed(treads)) + [landing]
    risers = [round(levels[i + 1] - levels[i], 3) for i in range(len(levels) - 1)]
    rail_top = down(0.0, YP) - DECK if down(0.0, YP) else None
    opening = []
    for z in (DECK - RISE + 0.2, DECK - 0.4, DECK + 0.5):
        l_, r_ = side((PX[0] - 0.3, 0.0, z), (0, -1, 0)), side((PX[0] - 0.3, 0.0, z), (0, 1, 0))
        opening.append((round(z, 2), round((l_ or 0) + (r_ or 0), 3)))
    rep = {"deck_samples": [min(d for d in deck if d), max(d for d in deck if d)], "deck_off": sum(
        1 for d in deck if d is None or abs(d - DECK) > 0.005), "tread_tops": treads, "landing": landing,
        "risers": risers, "rail_top_over_deck": round(rail_top, 3) if rail_top else None, "stair_opening": opening}
    pr = []
    if rep["deck_off"]:
        pr.append(f"{HERO}: {rep['deck_off']} deck samples off {DECK}")
    if any(abs(r - RISE) > 0.005 for r in risers):
        pr.append(f"{HERO}: uneven risers {risers}")
    if min(w for _, w in opening) < 2.2:
        pr.append(f"{HERO}: stair opening {opening}")
    return rep, pr


def after(objs):
    """Parts whose one up-facing region is a real material change (m073 ruling): the stub's cut-wood cap, the rock's
    darker foot (ground grime by height)."""
    objs[RPOST_P]["kit_shading_ok"] = "the bevelled cap is cut end grain (timber_end), as on every post"
    objs[ROCK_P]["kit_shading_ok"] = "the lowest 0.30 is darker stone by height (ground grime), as on m072's rocks"


def build(render=True, close=False, spin=False):
    return MODEL.run(hero=(HERO, hero_all), parts=PARTS, notes=NOTES, collision=COLLISION, budgets=BUDGETS,
                     target_size=TARGET_SIZE, views=VIEWS, exploded=EXPLODED, scale=(6.8, -3.0, 0.0),
                     close=CLOSE if close else None, verify=VERIFY, checks=[deck_check], render=render, spin=spin,
                     after=after)


CLOSE = {"lash_cu": dict(at=(PX[1], YP, DECK + 1.15), r=1.6, az=-150, el=15),
         "stair_cu": dict(at=(-6.5, -1.6, 2.6), r=3.2, az=-40, el=18),
         "banner_cu": dict(at=(0.0, -2.5, 3.6), r=2.6, az=-20, el=8)}


def preview(names=("f34_sheet", "front_sheet", "r34_sheet")):
    return MODEL.preview(HERO, VIEWS, names)


def compare(cells=None, out_dir=None, height=360):
    import importlib
    import compare as C
    importlib.reload(C)
    return C.compare(NUM, {k: COMPARE[k] for k in (cells or COMPARE)}, out_dir=out_dir, height=height)
