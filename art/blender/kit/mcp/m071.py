"""071 Supply Crate (references/071.png) on the shared library (kit_parts / kit_build): a square framed supply crate.
Four L-section corner posts and eight rails (four round the top, four round the bottom) frame the box; each of the four
sides carries an X brace (the continuous board A in front, board B behind it) over a recessed backing of four
horizontal boards with V seams; three planks close the top inside the top rails and three the bottom inside the bottom
rails; an iron corner bracket wraps each of the eight corners with a hexagonal domed bolt on both outer faces, and the four top brackets have a flat round bolt on top.

    import importlib, kit_parts, kit_build, m071
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m071); m071.build()

Build frame (studs): front -Y, +X right, ground z 0, centred on x 0 / y 0. Each side is built in its face frame
(u along the face as seen from outside, v = z, w = depth in from the frame's outer face), see face(). Names:
- BracedSupplyCrate (hero): everything above, one object of closed shells (no booleans). Collision hull.
- BracedSupplyCrateFramePlank (one rail), BracedSupplyCratePanelPlank (one backing board with V-seam edges),
  BracedSupplyCrateSidePanel (one side: two posts, two rails, X brace, backing, four brackets with bolts),
  BracedSupplyCrateTopPanel (three planks on two cleats), BracedSupplyCrateCornerBracket (bracket and two bolts).
Colour is by role and position, never by facing. No lights or VFX (the sheet shows none). See M071_spec.md.
"""
import math

from mathutils import Vector

import kit_build as B
import kit_parts as P

NUM, TITLE = 71, "Supply Crate"
HERO = "BracedSupplyCrate"
FRAME_P, BOARD_P, SIDE_P = "BracedSupplyCrateFramePlank", "BracedSupplyCratePanelPlank", "BracedSupplyCrateSidePanel"
TOP_P, BRACKET_P = "BracedSupplyCrateTopPanel", "BracedSupplyCrateCornerBracket"

WOOD, WOOD_DEEP, SEAM = "m071_wood", "m071_wood_deep", "m071_seam"
IRON, BOLT = "m071_iron", "m071_bolt"

# key -> (hex, roughness, metal, emission, low specular). Stage 4 (spec "Stage 4"): calibrated against the sheet.
PALETTE = {
    WOOD: ("#B0742F", 0.85, 0.0, 0.0, True),
    WOOD_DEEP: ("#784B22", 0.88, 0.0, 0.0, True),
    SEAM: ("#4E2712", 0.9, 0.0, 0.0, True),
    IRON: ("#656068", 0.6, 0.25, 0.0, False),
    BOLT: ("#61636F", 0.5, 0.35, 0.0, False),
}
# calibration targets: the sheet's rendered medians (spec "Stage 4")
TARGETS = {WOOD: ((0xCB, 0x7B, 0x31), "brown"), WOOD_DEEP: ((0x96, 0x55, 0x22), "brown"),
           IRON: ((0x74, 0x6B, 0x6F), "stone"), BOLT: ((0x6A, 0x68, 0x70), "stone")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)

# ---- layout (spec "Brief": height 2.30 at the bracket tops, the footprint from the ortho cells' W : H 1.14) ----------
HW = 1.21                       # frame (posts, rails) outer faces at +-HW
PW = 0.40                       # post width; rails and posts 0.40 deep (top cell)
IN = HW - PW                    # 0.81: post inner faces, rail inner faces
SEAT = 0.02                     # how far a piece sinks into what holds it
FOOT = 0.02                     # wood starts this far up: the brackets are the feet
TOP = 2.30                      # bracket tops (HOUSE_RULES crate height)
WOOD_TOP = 2.26                 # rail tops; post tops 0.01 higher, inside the brackets
RAIL_H = 0.36
RAILS_Z = ((FOOT, FOOT + RAIL_H), (WOOD_TOP - RAIL_H, WOOD_TOP))     # bottom 0.02-0.38, top 1.90-2.26
OPEN_V = (RAILS_Z[0][1], RAILS_Z[1][0])                               # the side opening 0.38-1.90
CORE_W = 0.18                   # backing (core) outer faces this far in from the frame face: +-1.03
CORE_Z = (OPEN_V[0] - 0.01, OPEN_V[1] + 0.01)                         # 0.37-1.91, seated 0.01 into the rails
NOTCH = HW - CORE_W - SEAT      # 1.01: the posts' L notch, so the core seats SEAT into them
SEAMS = (0.76, 1.14, 1.52)      # backing board seams (four boards of 0.38: side cell)
SEAM_E, SEAM_IN = 0.03, 0.035   # V seam half width and depth
BRACE_HW = 0.15                 # brace boards 0.30 wide (front cell)
BRACE_A_W = (0.04, 0.14)        # front board depth range (w)
BRACE_B_W = (0.12, CORE_W + SEAT)     # back board: 0.02 into A, 0.02 into the core
BR_T, BR_IN = 0.04, IN - 0.01   # bracket plate 0.04 proud of the frame, inner edge 0.80
BR_H = 0.41                     # bracket height: z 0-0.41 and 1.89-2.30
BOLT_R, BOLT_SINK, BOLT_PROUD, BOLT_DOME = 0.11, 0.02, 0.04, 0.035
TOP_BOLT_PROUD = 0.03
PLANK_Z = (2.06, 2.22)          # top planks, recessed 0.04 under the rail tops
PLANK_GAP = 0.04
BOTTOM_Z = (CORE_Z[0] - 0.16 + 0.005, CORE_Z[0] + 0.005)    # bottom planks under the core (underside cell)


def face(k):
    """Face frame k (0 front -Y, 1 right +X, 2 rear +Y, 3 left -X): (u, v, w) -> build-frame point, u along the face
    as seen from outside, v = z, w = depth in from the frame's outer face at HW."""
    n = [Vector((0, -1, 0)), Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((-1, 0, 0))][k]
    t = Vector((0, 0, 1)).cross(n)
    return lambda u, v, w: n * (HW - w) + t * u + Vector((0, 0, v))


def fbox(a, F, u, v, w, key, name, kind):
    """A box in face frame F: u, v, w = (lo, hi) ranges."""
    pts = [F(uu, v[0], ww) for uu, ww in ((u[0], w[0]), (u[1], w[0]), (u[1], w[1]), (u[0], w[1]))]
    pts += [F(uu, v[1], ww) for uu, ww in ((u[0], w[0]), (u[1], w[0]), (u[1], w[1]), (u[0], w[1]))]
    return P.box_pts(a, pts, key, name=name, kind=kind)


def fquad(a, F, quad, w, key, name, kind, amp=P.TINT):
    """A board of outline quad [(u, v)] x 4 in face frame F, between depths w = (w0, w1)."""
    pts = [F(u, v, w[0]) for u, v in quad] + [F(u, v, w[1]) for u, v in quad]
    return P.box_pts(a, pts, key, name=name, kind=kind, amp=amp)


# ---- timber -----------------------------------------------------------------------------------------------------------
def post(a, sx, sy, name="post"):
    """A corner post, L section: the 0.40 square at corner (sx, sy) less the notch the backing core sits in (its inner
    corner at NOTCH, the core's corner 0.02 into it), from FOOT to 0.01 over the rail tops (inside the bracket)."""
    o, i, n = HW, IN, NOTCH
    poly = [(sx * i, sy * o), (sx * o, sy * o), (sx * o, sy * i), (sx * n, sy * i), (sx * n, sy * n), (sx * i, sy * n)]
    p = P.ext(a, poly, FOOT, WOOD_TOP + 0.01, WOOD, name=name, kind="post")
    P.texture(a, p.vs, 0.03, P.seed(P.TAG[-1] + name), scale=0.6)
    return p


def rail(a, F, z, name="rail", depth=PW):
    """A frame rail along a face between the posts (seated SEAT into them), RAIL_H tall, `depth` deep."""
    p = fbox(a, F, (-IN - SEAT, IN + SEAT), z, (0.0, depth), WOOD, name, "rail")
    P.texture(a, p.vs, 0.03, P.seed(P.TAG[-1] + name), scale=0.6)
    return p


def brace_quads(v0=OPEN_V[0] - SEAT, v1=OPEN_V[1] + SEAT, u0=-IN - 0.01, u1=IN + 0.01, hw=BRACE_HW):
    """The X brace outlines in (u, v): parallelograms with horizontal ends on the rails whose acute tips touch the
    posts at the opening's corners (front cell). A runs bottom-left to top-right, B the other way."""
    du, dv = u1 - u0, v1 - v0
    le = 2 * hw
    for _ in range(20):                         # end length 2 hw / sin(theta), theta from the axis
        ax = du - le
        le = 2 * hw * math.hypot(ax, dv) / dv
    qa = [(u0, v0), (u0 + le, v0), (u1, v1), (u1 - le, v1)]
    qb = [(-u, v) for u, v in qa]
    return qa, qb


def braces(a, F, tag=""):
    qa, qb = brace_quads()
    A = fquad(a, F, qa, BRACE_A_W, WOOD, tag + "brace_a", "brace", amp=0.04)
    B_ = fquad(a, F, qb, BRACE_B_W, WOOD, tag + "brace_b", "brace", amp=0.04)
    P.tint(a, B_.fs, 0.94)                      # the back board sits deeper, in the front board's shade on the sheet
    for p in (A, B_):
        P.texture(a, p.vs, 0.03, P.seed(P.TAG[-1] + tag + p.name), scale=0.6)
    return A, B_


def seam_rings(z0, z1, seams=SEAMS, e=SEAM_E):
    """(z, inset) pairs up the backing: board faces flat, each seam a V (out, in, out) SEAM_E either side."""
    out = [(z0, 0.0)]
    for s in seams:
        out += [(s - e, 0.0), (s, SEAM_IN), (s + e, 0.0)]
    return out + [(z1, 0.0)]


def seam_keys(rings):
    return [SEAM if (rings[i][1] or rings[i + 1][1]) else WOOD_DEEP for i in range(len(rings) - 1)]


def core(a, name="core"):
    """The backing: one closed box (outer faces at +-(HW - CORE_W)) round all four sides, its faces cut into four
    horizontal boards by V seams (side cell); the hidden top and bottom close it. 84 tris."""
    c = HW - CORE_W
    rs = seam_rings(*CORE_Z)
    rings = [[(-(c - d), -(c - d), z), ((c - d), -(c - d), z), ((c - d), (c - d), z), (-(c - d), (c - d), z)]
             for z, d in rs]
    p = P.prism(a, rings, WOOD_DEEP, band_keys=seam_keys(rs), cap_keys=(WOOD_DEEP, WOOD_DEEP), name=name, kind="core")
    P.texture(a, p.vs, 0.035, P.seed(name), scale=0.5)
    return p


def top_planks(a, z=PLANK_Z, span=(-IN - SEAT, IN + SEAT), name="plank"):
    """Three planks along X inside the top (or bottom) rails (top cell), seated SEAT into the rails at their ends and
    outer sides, PLANK_GAP between them; a step darker than the frame, as the top cell draws them."""
    lo, hi = -IN - SEAT, IN + SEAT
    w = (hi - lo - 2 * PLANK_GAP) / 3
    key = P.mix(WOOD, WOOD_DEEP, 0.4)
    out = []
    for k in range(3):
        y0 = lo + k * (w + PLANK_GAP)
        p = P.box(a, (span[0], y0, z[0]), (span[1], y0 + w, z[1]), key, name=f"{name}{k}", kind="plank")
        P.texture(a, p.vs, 0.03, P.seed(P.TAG[-1] + f"{name}{k}"), scale=0.6)
        out.append(p)
    return out


# ---- iron -------------------------------------------------------------------------------------------------------------
def bolt(a, c, n, name, proud=BOLT_PROUD, dome=BOLT_DOME, r=BOLT_R, key=BOLT):
    """A round bolt head (hexagonal, 22 tris domed / 20 flat) on a face: centre c on the face, outward normal n, sunk
    BOLT_SINK into it, `proud` out, then a low dome (or a flat top when dome is 0)."""
    n, c = Vector(n).normalized(), Vector(c)
    u = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = (u - n * u.dot(n)).normalized()
    v = n.cross(u)

    def ring(d, k_r=1.0):
        return [c + n * d + (u * math.cos(k * math.pi / 3) + v * math.sin(k * math.pi / 3)) * r * k_r
                for k in range(6)]
    pts = ring(-BOLT_SINK) + ring(proud, 0.92 if dome > 0 else 1.0)
    faces = [[k, (k + 1) % 6, 6 + (k + 1) % 6, 6 + k] for k in range(6)] + [list(reversed(range(6)))]
    if dome > 0:
        pts.append(c + n * (proud + dome))
        faces += [[6 + k, 6 + (k + 1) % 6, 12] for k in range(6)]
    else:
        faces.append(list(range(6, 12)))
    return P.shell(a, pts, faces, key, name=name, kind="bolt", amp=0.02)


def bracket(a, sx, sy, top, name="bracket", top_bolt=True):
    """An iron corner bracket at corner (sx, sy): a box wrapping the post end and the rail ends, BR_T proud of the
    frame faces (and over the rail tops / under nothing at the foot), a domed bolt on both outer faces, and on a top
    bracket a flat bolt on top (close-up and top cells)."""
    o = HW + BR_T
    z0, z1 = (TOP - BR_H, TOP) if top else (0.0, BR_H)
    x0, x1 = sorted((sx * BR_IN, sx * o))
    y0, y1 = sorted((sy * BR_IN, sy * o))
    p = P.box(a, (x0, y0, z0), (x1, y1, z1), IRON, name=name, kind="bracket", amp=0.03)
    m, zc = (BR_IN + o) / 2, (z0 + z1) / 2
    bolt(a, (sx * m, sy * o, zc), (0, sy, 0), name + "_bolt_y")
    bolt(a, (sx * o, sy * m, zc), (sx, 0, 0), name + "_bolt_x")
    if top and top_bolt:
        bolt(a, (sx * m, sy * m, z1), (0, 0, 1), name + "_bolt_z", proud=TOP_BOLT_PROUD, dome=0.0)
    return p


# ---- assemblies -------------------------------------------------------------------------------------------------------
CORNERS = ((-1, -1), (1, -1), (1, 1), (-1, 1))


def hero_all(a):
    core(a)
    for k in range(4):
        F = face(k)
        with P.frame(None, f"f{k}_"):
            for j, z in enumerate(RAILS_Z):
                rail(a, F, z, name=f"rail{j}")
            braces(a, F)
    top_planks(a)
    top_planks(a, z=BOTTOM_Z, name="bottom")
    for i, (sx, sy) in enumerate(CORNERS):
        with P.frame(None, f"c{i}_"):
            post(a, sx, sy)
            bracket(a, sx, sy, False, "bracket_lo")
            bracket(a, sx, sy, True, "bracket_hi")


# ---- parts (the sheet's "Parts overview") -----------------------------------------------------------------------------
def frame_plank(a):
    """Wooden Plank (Frame): one rail, as in the hero."""
    rail(a, face(0), RAILS_Z[0])


def panel_plank(a):
    """Wooden Plank (Panel): one backing board across a side (the hero's backing face between two seams), its two
    outer long edges chamfered into the V seam."""
    c = HW - CORE_W
    sec = P.sec_rect(0.19, 0.06, SEAM_IN, corners=("+u+v", "-u+v"))       # u = z, v = -y: the -Y face's edges
    p = P.beam(a, (-c, 0.0, 0.19), (c, 0.0, 0.19), sec, WOOD_DEEP, up=Vector((0, -1, 0)), name="board", kind="board")
    P.texture(a, p.vs, 0.035, P.seed("board"), scale=0.5)


def slab(a, F, name="backing"):
    """The side panel's backing: a slab of four boards with V seams on its outer face (the hero's core face), between
    the posts (seated SEAT into them) and 0.12 thick."""
    rs = seam_rings(*CORE_Z)
    w0, w1 = CORE_W, CORE_W + 0.12
    prof = [(w0 + d, z) for z, d in rs] + [(w1, CORE_Z[1]), (w1, CORE_Z[0])]
    keys = seam_keys(rs) + [WOOD_DEEP] * 3
    p = P.ext(a, prof, -IN - SEAT, IN + SEAT, WOOD_DEEP, to3=lambda w, v, u: F(u, v, w), cap_key=WOOD_DEEP,
              side_keys=keys, name=name, kind="core")
    P.texture(a, p.vs, 0.035, P.seed(name), scale=0.5)
    return p


def side_panel(a):
    """Side Panel (Frame + X Brace): one side as the exploded view draws it (the hero's front side): its two corner
    posts, top and bottom rails, the X brace, the backing slab, and the four corner brackets with their face bolts
    (no top bolts: the panel stands alone)."""
    F = face(0)
    for j, z in enumerate(RAILS_Z):
        rail(a, F, z, name=f"rail{j}")
    braces(a, F)
    slab(a, F)
    for sx in (-1, 1):
        with P.frame(None, f"c{sx:+d}_"):
            post(a, sx, -1)
            bracket(a, sx, -1, False, "bracket_lo")
            bracket(a, sx, -1, True, "bracket_hi", top_bolt=False)


def top_panel(a):
    """Top / Bottom Panel (Planks): the three top planks on two cleats across their undersides."""
    th = PLANK_Z[1] - PLANK_Z[0]
    cl = 0.16
    for x in (-0.50, 0.50):
        P.box(a, (x - 0.13, -IN + 0.06, 0.0), (x + 0.13, IN - 0.06, cl), WOOD_DEEP, name=f"cleat{x:+.1f}", kind="cleat")
    top_planks(a, z=(cl - 0.01, cl - 0.01 + th))


def corner_bracket(a):
    """Metal Corner Bracket (+ Bolt): a foot bracket and its two face bolts, as on the hero (no post inside)."""
    bracket(a, -1, -1, False, "bracket")


PARTS = ((FRAME_P, frame_plank), (BOARD_P, panel_plank), (SIDE_P, side_panel), (TOP_P, top_panel),
         (BRACKET_P, corner_bracket))
NOTES = {
    HERO: "Braced supply crate (sheet 071): 2.65 x 2.65 x 2.33 (bracket tops 2.30). Four L-section corner posts and "
          "eight 0.36 x 0.40 rails frame it; an X brace (front board continuous, the other behind it) on every side over "
          "a recessed backing of four horizontal boards with V seams; three planks inside the top rails and three under "
          "the backing inside the bottom rails; an iron "
          "bracket on each of the eight corners with a domed bolt on both faces, the top four with a flat bolt on top.",
    FRAME_P: "Wooden Plank (Frame): one 1.66 x 0.40 x 0.36 rail",
    BOARD_P: "Wooden Plank (Panel): one 2.06 x 0.38 x 0.12 backing board, V-seam edges",
    SIDE_P: "Side Panel (Frame + X Brace): two posts, two rails, X brace, backing slab, four brackets with bolts",
    TOP_P: "Top / Bottom Panel (Planks): three planks on two cleats",
    BRACKET_P: "Metal Corner Bracket (+ Bolt): iron corner bracket with two hexagonal domed bolts",
}
COLLISION = {HERO: "hull", FRAME_P: "box", BOARD_P: "box", SIDE_P: "box", TOP_P: "box", BRACKET_P: "box"}
BUDGETS = {HERO: 1000}
SIZE_W = 2 * (HW + BR_T + BOLT_PROUD + BOLT_DOME)
TARGET_SIZE = ((SIZE_W, 0.01), (SIZE_W, 0.01), (TOP + TOP_BOLT_PROUD, 0.01))
VIEWS = {"f34_sheet": (-40, 22), "r34_sheet": (140, 22), "front_sheet": (0, 0), "side_sheet": (90, 0),
         "rear_sheet": (180, 0), "top_sheet": (0, 89.9)}
EXPLODED = {SIDE_P: (-1.0, 0.0, 0.0), TOP_P: (2.2, 0.0, 0.0), FRAME_P: (5.0, 0.0, 0.0), BOARD_P: (5.0, 0.0, 1.0),
            BRACKET_P: (7.0, 0.0, 0.0)}
CLOSE = {"under_cu": dict(at=(0.0, 0.0, 0.3), r=1.6, az=-35, el=-30)}
VERIFY = dict(cls="prop")
COMPARE = {"f34": {"box": (160, 105, 525, 462), "view": (-40, 22)},
           "r34": {"box": (595, 105, 958, 465), "view": (140, 22)},
           "front": {"box": (40, 545, 246, 724), "view": (0, 0)},
           "side": {"box": (287, 545, 493, 724), "view": (90, 0)},
           "rear": {"box": (536, 545, 742, 724), "view": (180, 0)},
           "top": {"box": (788, 538, 983, 724), "view": (0, 89.9)}}


def crate_check(objs):
    """Spec "Brief": bracket tops at TOP, the top planks 0.04 under the rail tops, wood clear of the ground by FOOT
    (the brackets are the feet), and the crate square in plan."""
    import json
    h = objs[HERO]
    off = Vector(h[MODEL.OFF])
    vs = [v.co + off for v in h.data.vertices]
    xs, ys = [v.x for v in vs], [v.y for v in vs]
    rep = {"x": [round(min(xs), 3), round(max(xs), 3)], "y": [round(min(ys), 3), round(max(ys), 3)],
           "top_bracket": TOP, "plank_top": PLANK_Z[1], "rail_top": WOOD_TOP,
           "shells": len(json.loads(h.get(f"{MODEL.key}_pieces", "[]")))}
    pr = []
    if abs((max(xs) - min(xs)) - (max(ys) - min(ys))) > 1e-3:
        pr.append(f"{HERO}: not square in plan {rep['x']} {rep['y']}")
    return rep, pr


def build(render=True, close=False, spin=False):
    return MODEL.run(hero=(HERO, hero_all), parts=PARTS, notes=NOTES, collision=COLLISION, budgets=BUDGETS,
                     target_size=TARGET_SIZE, views=VIEWS, exploded=EXPLODED, close=CLOSE if close else None,
                     verify=VERIFY, checks=[crate_check], render=render, spin=spin)


def preview(names=("f34_sheet", "front_sheet", "side_sheet")):
    return MODEL.preview(HERO, VIEWS, names)


def compare(cells=None, out_dir=None):
    import importlib
    import compare as C
    importlib.reload(C)
    return C.compare(NUM, {k: COMPARE[k] for k in (cells or COMPARE)}, out_dir=out_dir)
