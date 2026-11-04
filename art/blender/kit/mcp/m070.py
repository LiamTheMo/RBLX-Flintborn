"""070 Ruined Lean-To (references/070.png, remade 2026-11-04) on the shared library (kit_parts / kit_build): a camp
lean-to built into the corner of a ruined stone wall. An L of big chamfered pale pink-grey blocks (2.3 deep, 1.95
courses, running bond): a long back wall stepping up to a seven-course peak left of centre and a four-to-five-course
side wall at -X whose front end carries a crossbeam; chipped top corners, lime ivy curtains of tent leaves on square
stems over the peak and the wall ends, flat moss patches on the tops. Three square timber posts on stone footings
(front-left 9.4, back 11.3, front-right 12.0) with gold rope turns and X-lashings carry one cream canvas tied at the
two front posts and gathered across the back post's face; the middle of its front edge is pulled down to a low point
over a crate, with a short rope tail and toggle. A red three-point banner with a white diamond hangs from a crossarm
lashed to the front-right post, in front of a dark pole. Inside: a leather bedroll with gold caps and straps, a gold
sleeping mat with teal stripes, two closed X-braced crates, a lidded hooped barrel and a plank bench; loose rubble
blocks at the front.

    import importlib, kit_parts, kit_build, m070
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m070); m070.build()

Build frame (studs): front -Y (open), +X right (open, banner), side wall at -X, back wall at +Y, ground z 0, x 0 midway
between the front posts. Every piece is its own closed shell (no booleans), seated 0.002-0.05 into what holds it.
Names (spec "Brief"): hero RuinedLeanTo; parts RuinedLeanToWallBlock, ...WallSection, ...Rubble, ...Canopy, ...Post,
...Banner, ...Bedroll, ...Table, ...Crate, ...Barrel. Stages 5-6: none (the sheet shows no light or effect in any
assembled view; the exploded view's lantern is left out). See art/blender/renders/models/M070/M070_spec.md.
"""
import math
import random

from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_build as B
import kit_parts as P

NUM, TITLE = 70, "Ruined Lean-To"
HERO = "RuinedLeanTo"
BLOCK_P, SECTION_P, RUBBLE_P = "RuinedLeanToWallBlock", "RuinedLeanToWallSection", "RuinedLeanToRubble"
CANOPY_P, POST_P, BANNER_P = "RuinedLeanToCanopy", "RuinedLeanToPost", "RuinedLeanToBanner"
BEDROLL_P, TABLE_P, CRATE_P, BARREL_P = ("RuinedLeanToBedroll", "RuinedLeanToTable", "RuinedLeanToCrate",
                                         "RuinedLeanToBarrel")

STONE, STONE_LIGHT, STONE_DARK = "m070_stone", "m070_stone_light", "m070_stone_dark"
TIMBER, TIMBER_END, TIMBER_DEEP = "m070_timber", "m070_timber_end", "m070_timber_deep"
PLANK, WOOD_DARK = "m070_plank", "m070_wood_dark"
CANVAS, CANVAS_DEEP = "m070_canvas", "m070_canvas_deep"
ROPE, ROPE_DEEP = "m070_rope", "m070_rope_deep"
BANNER, BANNER_DEEP, WHITE, POLE = "m070_banner", "m070_banner_deep", "m070_cloth_white", "m070_pole"
IVY_L, IVY_G, IVY_D, STEM = "m070_ivy_lime", "m070_ivy", "m070_ivy_dark", "m070_stem"
LEATHER, GOLD, MAT, STRIPE, IRON = "m070_leather", "m070_gold", "m070_mat", "m070_stripe", "m070_iron"

# key -> (hex, roughness, metal, emission, low specular). Stage 4 (spec "Stage 4"): calibrated against the sheet.
PALETTE = {
    STONE: ("#A48F8F", 0.9, 0.0, 0.0, True), STONE_LIGHT: ("#C4B0AE", 0.9, 0.0, 0.0, True),
    STONE_DARK: ("#6E6467", 0.9, 0.0, 0.0, True),
    TIMBER: ("#9A521A", 0.85, 0.0, 0.0, True), TIMBER_END: ("#B47A35", 0.8, 0.0, 0.0, True),
    TIMBER_DEEP: ("#4E2810", 0.9, 0.0, 0.0, True),
    PLANK: ("#784811", 0.85, 0.0, 0.0, True), WOOD_DARK: ("#623820", 0.85, 0.0, 0.0, True),
    CANVAS: ("#D8C6A8", 0.95, 0.0, 0.0, True), CANVAS_DEEP: ("#B9A182", 0.95, 0.0, 0.0, True),
    ROPE: ("#D8A04C", 0.95, 0.0, 0.0, True), ROPE_DEEP: ("#AE7E34", 0.95, 0.0, 0.0, True),
    BANNER: ("#C42727", 0.9, 0.0, 0.0, True), BANNER_DEEP: ("#861818", 0.9, 0.0, 0.0, True),
    WHITE: ("#EAE2DC", 0.9, 0.0, 0.0, True), POLE: ("#3E2B22", 0.85, 0.0, 0.0, True),
    IVY_L: ("#94B00C", 0.8, 0.0, 0.0, True), IVY_G: ("#618000", 0.8, 0.0, 0.0, True),
    IVY_D: ("#3E5A0E", 0.85, 0.0, 0.0, True), STEM: ("#5C4828", 0.9, 0.0, 0.0, True),
    LEATHER: ("#754321", 0.8, 0.0, 0.0, True), GOLD: ("#C08A35", 0.85, 0.0, 0.0, True),
    MAT: ("#A07B3C", 0.9, 0.0, 0.0, True), STRIPE: ("#4F7F8E", 0.9, 0.0, 0.0, True),
    IRON: ("#5A5A62", 0.55, 0.45, 0.0, False),
}
# calibration targets: the sheet's rendered medians (spec "Stage 4") and K.sample kinds
TARGETS = {STONE: ((0xCF, 0xAE, 0xA5), "all"), TIMBER: ((0x9B, 0x4C, 0x15), "brown"),
           PLANK: ((0x97, 0x52, 0x11), "brown"), WOOD_DARK: ((0x77, 0x3D, 0x20), "brown"),
           IVY_G: ((0x6E, 0x8F, 0x01), "green"), IVY_L: ((0xA8, 0xC4, 0x10), "green"),
           BANNER: ((0xCB, 0x22, 0x22), "vivid"), ROPE: ((0xE5, 0x9F, 0x3D), "vivid"),
           LEATHER: ((0x91, 0x4C, 0x21), "brown"), MAT: ((0xC8, 0x91, 0x3E), "vivid")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)


def mix(k1, k2, t):
    return P.mix(k1, k2, t, step=0.05)


def flatten(a, faces, tol=1e-4):
    """(m068) Split warped quads (P.block's creased and chipped faces) into their two triangles, so each face is
    planar and the ray-parity normal check probes the real surface."""
    import bmesh
    warped = []
    for f in faces:
        if f.is_valid and len(f.verts) == 4:
            f.normal_update()
            c = f.calc_center_median()
            if max(abs((v.co - c).dot(f.normal)) for v in f.verts) > tol:
                warped.append(f)
    if warped:
        bmesh.ops.triangulate(a.bm, faces=warped, quad_method="BEAUTY", ngon_method="BEAUTY")
    return len(warped)


def blk(a, L, D, H, key, **kw):
    """P.block with its warped faces split (flatten). Returns the Piece (its vs are what the stone tree needs)."""
    p = P.block(a, L, D, H, key, **kw)
    flatten(a, p.fs)
    return p


# ---- masonry (spec "Brief": the front cell's skyline; courses 1.95) ---------------------------------------------------
COURSE, DEPTH, J, SEAT, BCH = 1.95, 2.3, 0.05, 0.015, 0.16
BACK_Y = (4.0, 6.3)              # back wall inner, outer face
SIDE_X = (-9.3, -7.0)            # side wall outer, inner face
BACK_X = (-9.3, 6.6)
SIDE_Y0, SIDE_Y4 = -6.3, -1.4    # side wall front end (courses 0-3), the fifth course's front end
BACK_SPANS = {4: (-9.3, 5.4), 5: (-7.0, 2.4), 6: (-5.0, 1.5)}       # the stepped skyline above course 3
# (wall, course, block index; negative from the end) -> [(corner, size)]: block -y = the wall's inner face
CHIPS = {("B", 6, 0): [("-x-y", 0.40)], ("B", 6, -1): [("+x+y", 0.35)], ("B", 5, 0): [("-x+y", 0.35)],
         ("B", 5, -1): [("+x-y", 0.30)], ("B", 4, -1): [("+x-y", 0.35)], ("B", 3, -1): [("+x+y", 0.30)],
         ("S", 3, 0): [("-x-y", 0.35)], ("S", 4, 0): [("-x+y", 0.30)], ("B", 2, 3): [("-x-y", 0.25)]}
STONE_PIECES = []                # every stone piece of the current object (the tree moss and ivy drape on)


def _layout(x0, x1, fixed, rng, lmin=2.1, lmax=3.4, target=2.9, tries=900):
    """(old m070) Running bond: cut x0..x1 into blocks of about `target` whose joints stand as far as possible from
    the `fixed` joints (the course below, the step ends above), then the most even lengths. Returns the joints."""
    span = x1 - x0
    ns = sorted({n for n in (math.floor(span / target), math.ceil(span / target)) if n >= 1
                 and lmin <= span / n <= lmax} or {max(1, round(span / target))})
    best = None
    for n in ns:
        if n == 1:
            return []
        for _ in range(tries):
            w = [rng.uniform(0.8, 1.2) for _ in range(n)]
            s = sum(w)
            ls = [wi / s * span for wi in w]
            if any(ln < lmin or ln > lmax for ln in ls):
                continue
            cuts, acc = [], x0
            for ln in ls[:-1]:
                acc += ln
                cuts.append(acc)
            score = min([abs(c - f) for c in cuts for f in fixed] or [9.0])
            key = (round(min(score, 0.6), 2), -n, -sum(abs(ln - span / n) for ln in ls))
            if best is None or key > best[0]:
                best = (key, cuts)
    return best[1] if best else []


def courses():
    """(wall, course, run start, run end): the back wall along X, the side wall along Y. The corner pier (x -9.3..-7.0,
    y 4.0..6.3) belongs to the back wall on even courses and to the side wall on odd ones."""
    out = []
    for k in range(7):
        if k <= 3:
            span = BACK_X if k % 2 == 0 else (SIDE_X[1] + J, BACK_X[1])
        else:
            span = BACK_SPANS[k]
        out.append(("B", k) + tuple(span))
    for k in range(5):
        y0 = SIDE_Y0 if k <= 3 else SIDE_Y4
        out.append(("S", k, y0, BACK_Y[0] - J) if k % 2 == 0 else ("S", k, y0, BACK_Y[1]))
    return out


def wall_matrix(wall, s, z0):
    """Block space -> build frame: block x along the wall's run, block -y toward the wall's inner face."""
    if wall == "B":
        return Matrix.Translation((s, sum(BACK_Y) / 2, z0))
    return Matrix.Translation((sum(SIDE_X) / 2, s, z0)) @ Matrix.Rotation(math.pi / 2, 4, "Z")


def course_key(k):
    """By position: the foot courses blend toward stone_dark in steps (grime), the rest plain stone."""
    return {0: mix(STONE, STONE_DARK, 0.30), 1: mix(STONE, STONE_DARK, 0.15)}.get(k, STONE)


def walls(a):
    """The L of ruin masonry: chamfered 2.3-deep blocks in running bond (joints 0.05, seats 0.015), the stepped
    skyline, chips by role (stone_light on the broken facets), a little hand-laid jitter; per-block Tint and mottling."""
    rng = random.Random(7010)
    joints, n_blocks = {}, 0
    for wall, k, s0, s1 in courses():
        fixed = list(joints.get((wall, k - 1), []))
        if wall == "B" and k - 1 >= 0 and (k - 1) % 2 == 1 and k - 1 <= 3:
            fixed.append(SIDE_X[1] + J / 2)
        if wall == "B" and k + 1 in BACK_SPANS:
            fixed += [x for x in BACK_SPANS[k + 1] if s0 + 0.3 < x < s1 - 0.3]
        if wall == "S" and k >= 1 and (k - 1) % 2 == 0:
            fixed.append(BACK_Y[0] - J / 2)
        if wall == "S" and k == 3:
            fixed.append(SIDE_Y4)
        cuts = _layout(s0, s1, fixed, rng)
        joints[(wall, k)] = cuts + ([SIDE_X[1] + J / 2] if wall == "B" and k <= 3 and k % 2 == 1 else [])
        edges = [s0] + cuts + [s1]
        n = len(edges) - 1
        z0 = 0.0 if k == 0 else COURSE * k + SEAT
        H = COURSE * (k + 1) - z0
        for i in range(n):
            a0 = edges[i] + (J / 2 if i else 0.0)
            a1 = edges[i + 1] - (J / 2 if i < n - 1 else 0.0)
            chips = CHIPS.get((wall, k, i)) or CHIPS.get((wall, k, i - n)) or []
            m = wall_matrix(wall, (a0 + a1) / 2 + rng.uniform(-0.01, 0.01), z0) @ \
                Matrix.Translation((0.0, rng.uniform(-0.02, 0.02), 0.0)) @ \
                Matrix.Rotation(math.radians(rng.uniform(-0.5, 0.5)) + (math.pi if rng.random() < 0.5 and not chips
                                                                        else 0.0), 4, "Z")
            STONE_PIECES.append(blk(a, a1 - a0, DEPTH, H, course_key(k), m=m, chips=chips,
                                    chip_key=mix(STONE, STONE_LIGHT, 0.5), name=f"{wall}{k}_{i}", kind="block"))
            n_blocks += 1
    P.GEO["blocks"] = n_blocks


# ---- rubble and footings ---------------------------------------------------------------------------------------------
RUBBLE = (  # centre, (L, D, H), yaw, chips
    ((-9.2, -7.4), (1.5, 1.4, 1.2), 12.0, [("+x+y", 0.35)]),
    ((-6.7, -8.3), (1.9, 1.7, 1.4), -8.0, [("-x-y", 0.35)]),
    ((-4.4, -9.4), (2.0, 1.9, 1.6), 6.0, [("+x-y", 0.40), ("-x+y", 0.30)]),
    ((2.6, -9.0), (1.6, 1.4, 1.0), 20.0, [("-x-y", 0.30)]),
    ((8.3, -7.6), (1.2, 1.1, 0.9), -15.0, [("+x+y", 0.25)]),
)


def rubble(a, c, size, yaw, chips, name):
    L, D, H = size
    p = blk(a, L, D, H, mix(STONE, STONE_DARK, 0.10), m=P.R(c, yaw), ch=0.12, crease=False, chips=chips,
            chip_key=mix(STONE, STONE_LIGHT, 0.5), name=name, kind="rubble")
    STONE_PIECES.append(p)
    return p


def footing(a, tag, x, y):
    w, h, t = FOOTINGS[tag]
    p = blk(a, w, w, h, mix(STONE, STONE_DARK, t), m=Matrix.Translation((x, y, 0.0)), ch=0.10, crease=False, name=f"footing_{tag}",
            kind="footing")
    STONE_PIECES.append(p)
    return p


# ---- posts and rope ----------------------------------------------------------------------------------------------------
PH, PCH = 0.52, 0.06                     # post half width (1.04 square: the front cell's 12.5 px), edge chamfer
POSTS = {"FL": (-5.88, -6.0, 9.4), "B": (-0.99, 3.20, 11.3), "FR": (5.88, -6.0, 12.0)}
FOOTINGS = {"FL": (1.5, 0.5, 0.15), "B": (1.25, 1.3, 0.55), "FR": (2.0, 1.0, 0.10)}   # width, height, t to stone_dark
RT, RD = 0.13, 0.12                      # turn and diagonal radii (P.x_lashing)
# turns (z), X faces [(face, over)]: over = "beam" takes the diagonals round the crossbeam on that face
LASH = {"FL": dict(turns=(7.45, 8.75), faces=[((0, -1), None), ((-1, 0), None)]),
        "B": dict(turns=(9.85, 10.85), faces=[]),
        "FR": dict(turns=(8.85, 10.55), faces=[((0, -1), None)])}
COLLARS = {"FL": (0.75,), "FR": (1.30, 4.70)}     # two stacked turns from each height (gold bands)
BEAM = dict(x=(-9.0, -5.88), z=(7.80, 8.40), hy=0.28)    # the crossbeam on the side wall top, behind the FL post


def post_z0(tag):
    return FOOTINGS[tag][1] - 0.02


def post(a, tag, x, y, top):
    """A square chamfered post from its footing top (sunk 0.02) to `top`, its top edge bevelled."""
    sec, cap = P.sec_rect(PH, PH, PCH), P.sec_rect(PH - 0.07, PH - 0.07, PCH * 0.6)
    rings = [[(x + u, y + v, z) for u, v in sec] for z in (post_z0(tag), top - 0.07)]
    rings.append([(x + u, y + v, top) for u, v in cap])
    return P.prism(a, rings, TIMBER, cap_keys=(None, TIMBER_END), name="post", kind="post")


def diagonals(a, cx, cy, z_lo, z_hi, face, name, over=None):
    """P.x_lashing's two crossing diagonals on one post face (its turns are made once per post, not per face)."""
    flat = P.turn_ext()[0]
    n = Vector((face[0], face[1], 0.0)).normalized()
    ax = Vector((-n.y, n.x, 0.0))
    c = Vector((cx, cy, 0.0))
    dt, d0, xh = PH + RT * flat - P.SINK, PH + 0.8 * RD - P.SINK, PH - 0.10
    out = []
    for k, sg in enumerate((1, -1)):
        S = c + n * dt + ax * (-sg * xh)
        S.z = z_hi
        E = c + n * dt + ax * (sg * xh)
        E.z = z_lo
        lf = 0.20 if k else 0.0
        if over:
            fd, top, bot = over
            o = 0.8 * RD - P.SINK
            B1 = c + n * (fd + o) + ax * (-sg * 0.18)
            B1.z = top + o
            B2 = c + n * (fd + o) + ax * (sg * 0.18)
            B2.z = bot - o
            mid = c + n * (fd + o + lf)
            mid.z = (top + bot) / 2
            inner = [B1, mid, B2] if k else [B1, B2]
        else:
            mid = c + n * (d0 + lf)
            mid.z = (z_lo + z_hi) / 2
            inner = [mid]
        S0 = S + (inner[0] - S).normalized() * (1.4 * RT * flat)
        E0 = E + (inner[-1] - E).normalized() * (1.4 * RT * flat)
        out.append(P.rope(a, [S0] + inner + [E0], RD, ROPE, ROPE_DEEP, sides=4, up=n, name=f"{name}_x{k}",
                          kind="rope_diag"))
    return out


def lashing(a, tag, x, y):
    """The post's rope: two turns and an X on each listed face (close-up "Lashing"), and the gold collar bands."""
    spec = LASH[tag]
    lo, hi = (x - PH, y - PH), (x + PH, y + PH)
    for i, z in enumerate(spec["turns"]):
        P.rope_turn(a, lo, hi, z, RT, ROPE, ROPE_DEEP, name=f"lash_t{i}", kind="rope_turn")
    for i, (face, over) in enumerate(spec["faces"]):
        diagonals(a, x, y, *spec["turns"], face, f"lash{i}", over=over)
    for j, z0 in enumerate(COLLARS.get(tag, ())):
        for t in range(2):
            P.rope_turn(a, lo, hi, z0 + RT + t * (2 * RT - 0.02), RT, ROPE, ROPE_DEEP, name=f"collar{j}_{t}",
                        kind="rope_turn")


def crossbeam(a):
    """The square beam resting on the side wall's front-end top (sunk 0.02 into it), its right end against the FL
    post's back face (sunk 0.01) and stopping at the post's centre line."""
    x, y, _ = POSTS["FL"]
    yc = y + PH + BEAM["hy"] - 0.01
    zc = sum(BEAM["z"]) / 2 - 0.02
    return P.plank(a, (BEAM["x"][0], yc, zc), (BEAM["x"][1], yc, zc), 2 * BEAM["hy"], BEAM["z"][1] - BEAM["z"][0],
                   TIMBER, ch=0.05, cap_keys=(TIMBER_END, TIMBER_END), name="crossbeam", kind="beam")


def post_all(a, tag, footing_too=True):
    x, y, top = POSTS[tag]
    with P.frame(None, f"{tag}_"):
        if footing_too:
            footing(a, tag, x, y)
        post(a, tag, x, y, top)
        lashing(a, tag, x, y)


# ---- canvas (spec "Brief": three tied corners and the front edge pulled down over the crate) -------------------------
CANVAS_T, NU, NV = 0.10, 9, 5
CORNERS = {"C1": (POSTS["FL"][0] + PH - 0.02, POSTS["FL"][1] + PH - 0.02, 8.25),       # FL post's inner corner
           "C4": (POSTS["FR"][0] - PH + 0.02, POSTS["FR"][1] + PH - 0.02, 9.30),       # FR post's inner corner
           # across the back post's flat front face, 0.03 off it: the underside's back edge, shifted back along the
           # sloping normals, sinks about 0.03 into the face
           "C2": (POSTS["B"][0] - PH + PCH + 0.05, POSTS["B"][1] - PH - 0.03, 10.35),
           "C3": (POSTS["B"][0] + PH - PCH - 0.05, POSTS["B"][1] - PH - 0.03, 10.35)}
LOW = (1.35, -2.60, 6.55)                # the front edge's low point (top surface), over the right crate
U_LOW = 5 / 8                            # its grid column on the front edge (nu = 9)
SAG = dict(u0=0.55, u1=0.45, v1=0.0, c=0.55)
RIDGE = 0.35
HEADROOM = 6.9


def canvas_top():
    """top(u, v) of the canvas: bilinear over the four corners with edge and centre sag (P.canvas), the X creases
    eased along the diagonals (m066), and the front edge pulled to LOW by a tent in u (straight edges from the tied
    corners down to the low point) that fades toward the back as (1 - v)^1.3 (the crease from the low point up)."""
    C = {k: Vector(v) for k, v in CORNERS.items()}
    s = dict(v0=0.0, **SAG)
    e = s["c"] - 0.5 * (s["v0"] + s["v1"] + s["u0"] + s["u1"])

    def base(u, v):
        p = C["C1"] * (1 - u) * (1 - v) + C["C4"] * u * (1 - v) + C["C2"] * (1 - u) * v + C["C3"] * u * v
        bu, bv = 4 * u * (1 - u), 4 * v * (1 - v)
        drop = (1 - v) * s["v0"] * bu + v * s["v1"] * bu + (1 - u) * s["u0"] * bv + u * s["u1"] * bv + e * bu * bv
        dd = min(abs(u - v), abs(u + v - 1)) * math.sqrt(0.5)
        rc = min(1.0, 1.6 * math.hypot(u - 0.5, v - 0.5) / math.sqrt(0.5))
        p.z -= drop * (1.0 - RIDGE * rc * max(0.0, 1.0 - dd / 0.12))
        return p
    D = Vector(LOW) - base(U_LOW, 0.0)

    def top(u, v):
        f = u / U_LOW if u <= U_LOW else (1 - u) / (1 - U_LOW)
        return base(u, v) + D * (f * (1 - v) ** 1.3)
    return top


def canvas_sheet(a, top, key, deep, nu, nv, hem=0.30, ct=CANVAS_T, name="canvas", kind="canvas"):
    """(m066 canvas_sheet, top surface passed in) One closed ct slab: an nu x nv top grid inset `hem` from the edges,
    each quad split along the diagonal pointing at the centre, a hem strip to the true edge, the underside ct below
    along the vertex normals (straight down at the four corners), rim faces split into triangles (they twist where the
    sheet is steep). Hem colour by distance from the edge toward `deep`."""
    T0 = top(0, 0)
    du = hem / max((top(1, 0) - T0).length, 1e-6)
    dv = hem / max((top(0, 1) - T0).length, 1e-6)
    T = {(i, j): top(du + (1 - 2 * du) * i / (nu - 1), dv + (1 - 2 * dv) * j / (nv - 1)) for i in range(nu)
         for j in range(nv)}
    loop = ([(i, 0) for i in range(nu)] + [(nu - 1, j) for j in range(1, nv)] +
            [(i, nv - 1) for i in range(nu - 2, -1, -1)] + [(0, j) for j in range(nv - 2, 0, -1)])
    Pm = dict(T)
    Pm.update({("o", k): top(k[0] / (nu - 1), k[1] / (nv - 1)) for k in loop})
    ci, cj = (nu - 1) / 2, (nv - 1) / 2
    ring = {(i, j) for i in range(nu) for j in range(nv) if i in (0, nu - 1) or j in (0, nv - 1)}
    tris = []
    for i in range(nu - 1):
        for j in range(nv - 1):
            a_, b_, c_, d_ = (i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)
            pair = [(a_, b_, c_), (a_, c_, d_)] if (i + 0.5 < ci) == (j + 0.5 < cj) else [(a_, b_, d_), (b_, c_, d_)]
            for t in pair:
                tris.append((t, mix(key, deep, 0.15) if sum(1 for k in t if k in ring) == 3 else key))
    hk = mix(key, deep, 0.35)
    for k in range(len(loop)):
        a0, a1 = ("o", loop[k]), ("o", loop[(k + 1) % len(loop)])
        b0, b1 = loop[k], loop[(k + 1) % len(loop)]
        if (Pm[a0] - Pm[b1]).length <= (Pm[a1] - Pm[b0]).length:
            tris += [((a0, a1, b1), hk), ((a0, b1, b0), hk)]
        else:
            tris += [((a0, a1, b0), hk), ((a1, b1, b0), hk)]
    nrm = {k: Vector() for k in Pm}
    for t, _ in tris:
        p0, p1, p2 = (Pm[k] for k in t)
        n = (p1 - p0).cross(p2 - p0)
        if n.z < 0:
            n = -n
        for k in t:
            nrm[k] += n
    keys_ = [k for k in Pm if nrm[k].length > 0]
    idx = {k: i for i, k in enumerate(keys_)}
    flat = {("o", (0, 0)), ("o", (nu - 1, 0)), ("o", (0, nv - 1)), ("o", (nu - 1, nv - 1))}
    under = [Pm[k] - (Vector((0, 0, ct)) if k in flat else nrm[k].normalized() * (ct / max(nrm[k].normalized().z, 0.5)))
             for k in keys_]
    pts = [Pm[k] for k in keys_] + under
    nb = len(keys_)
    faces, fkeys, count = [], [], {}
    for t, k in tris:
        faces.append([idx[q] for q in t])
        fkeys.append(k)
        faces.append([nb + idx[q] for q in reversed(t)])
        fkeys.append(k)
        for x in range(3):
            ed = (t[x], t[(x + 1) % 3])
            count[frozenset(ed)] = count.get(frozenset(ed), []) + [ed]
    rim = mix(key, deep, 0.6)
    for eds in count.values():
        if len(eds) == 1:
            u_, v_ = eds[0]
            faces += [[idx[u_], idx[v_], nb + idx[v_]], [idx[u_], nb + idx[v_], nb + idx[u_]]]
            fkeys += [rim, rim]
    p = P.shell(a, pts, faces, key, keys=[k if k != key else None for k in fkeys], name=name, kind=kind, amp=0.02)
    P.texture(a, p.vs, 0.03, P.seed(name), scale=0.18)
    low = Pm[("o", (round(U_LOW * (nu - 1)), 0))]
    P.GEO.setdefault("canvas", {})[name] = {"low_top": round(min(q.z for q in Pm.values()), 3),
                                            "low_under": round(min(q.z for q in under), 3), "low_point": list(low)}
    return p


TAIL = dict(len=0.95, r=0.06, tog=(0.13, 0.13, 0.42))   # rope tail and toggle under the low point


def canopy(a, name="canvas"):
    """The canvas and, under its low point, a short rope tail (sunk 0.03 into the underside) ending in a toggle."""
    p = canvas_sheet(a, canvas_top(), CANVAS, CANVAS_DEEP, NU, NV, name=name)
    low = Vector(P.GEO["canvas"][name]["low_point"])
    z_under = min(v.co.z for v in p.vs)
    c = Vector((low.x, low.y + 0.45, 0.0))
    hit = P.tree_of(p).ray_cast(Vector((c.x, c.y, 0.0)), Vector((0, 0, 1)), 50.0)[0]
    z1 = (hit.z if hit is not None else z_under) + 0.01
    z0 = z1 - TAIL["len"]
    P.rope(a, [(c.x, c.y, z1), (c.x, c.y + 0.03, (z0 + z1) / 2), (c.x, c.y, z0)], TAIL["r"], ROPE, ROPE_DEEP,
           sides=4, name=f"{name}_tail", kind="rope_tail")
    tx, ty, tz = TAIL["tog"]
    P.box(a, (c.x - tz / 2, c.y - ty, z0 - tx + 0.02), (c.x + tz / 2, c.y + ty, z0 + 0.02), TIMBER,
          name=f"{name}_toggle", kind="toggle", amp=0.03)
    return p


# ---- banner (front cell: crossarm off the FR post, dark pole behind the cloth) ------------------------------------------
ARM = dict(z=9.62, r=0.20, x1=9.25)
POLE_XY, POLE_R, POLE_TOP = (7.75, None), 0.20, 10.05
BAN = dict(x=(7.0, 8.95), tip=3.10, notch=3.95)


def banner(a, x_post=POSTS["FR"][0], y_post=POSTS["FR"][1]):
    """The round crossarm (pale cut end, knob) from the FR post's +X face, a dark pole touching its back, the red
    cloth hung from a hem sleeve round the arm, three points, the white diamond on both faces."""
    y, z = y_post, ARM["z"]
    x0 = x_post + PH - 0.02
    P.crossarm(a, (x0, y, z), (ARM["x1"], y, z), ARM["r"], POLE, end_key=TIMBER_END, knob=(0.27, 0.22),
               name="crossarm")
    py = y + ARM["r"] + 0.10 + POLE_R + 0.01          # 0.01 behind the hem sleeve (it stands on the ground)
    P.pole(a, (POLE_XY[0], py), 0.0, POLE_TOP, POLE_R, POLE, top_key=TIMBER_END, name="pole")
    ri, ro = ARM["r"] + 0.008, ARM["r"] + 0.10
    c0, c1 = BAN["x"]
    P.sleeve(a, (c0, y, z), (c1, y, z), ri, ro, mix(BANNER, BANNER_DEEP, 0.3), sides=8, name="banner_hem",
             kind="banner", amp=0.02)
    zt = z - ro + 0.007
    w = c1 - c0
    P.banner(a, c0, c1, y, zt, BAN["tip"], BAN["notch"], BANNER, hem_key=mix(BANNER, BANNER_DEEP, 0.25), t=0.08,
             hem=0.40, points=3, emblem_key=WHITE, emblem_z=zt - 2.9, name="banner", w=w * 0.52, h=w * 0.78,
             dots=(0.12, w * 0.38))


# ---- furniture (HOUSE_RULES sizes: crate 2.30, barrel 2.72, seats 1.50) -----------------------------------------------
CRATES = {"crate_l": (-3.95, -4.25), "crate_r": (LOW[0], LOW[1])}
BARREL_C = (4.00, -3.90)
BOX_C = (6.85, -4.35)                             # the small lidded box behind the FR post (hero view)
BENCH_C, BENCH_L, SEAT_Z, SEAT_T, SEAT_D = (4.15, 2.55), 2.8, 1.50, 0.36, 1.10
BEDROLL = dict(x=(-5.25, -2.05), y=3.05, r=0.70)
MAT_BOX = ((-3.35, -2.45), (-0.05, 2.15), 0.14)
STRIPES = ((-1.65, -1.25), (0.35, 0.75))          # teal stripes across the mat (y ranges)


BRACE_PROUD = 0.10


def crate(a, c, name="crate"):
    """(m066) The closed X-braced crate (P.crate): the frame, lid and braces in the lighter plank wood over darker
    recessed panels, the braces standing BRACE_PROUD off the panels; its hidden bottom in the panel key and the bottom
    and lid at the mean Tint (a random draw there reads as shading by direction)."""
    out = P.crate(a, c, PLANK, WOOD_DARK, W=2.30, H=2.30, frame_t=(0.0, 1.0), open_top=False, name=name)
    body = out[0]
    P.paint(a, [body.fs[0]], WOOD_DARK)
    for f in body.fs[:2]:
        P.tint(a, [f], 1.0 / max(f.loops[0][a.tint_layer][0], 1e-3))
    for br in out[1:]:
        for vb, vf in zip(br.vs[:4], br.vs[4:8]):
            d = vf.co - vb.co
            vf.co = vb.co + d * (BRACE_PROUD / d.length)
        for f in br.fs:
            f.normal_update()
    return out


def barrel(a, c=BARREL_C):
    return P.barrel(a, c, PLANK, WOOD_DARK, IRON, open_top=False, lid_key=mix(PLANK, WOOD_DARK, 0.3), name="barrel")


def bench(a, cx=BENCH_C[0], cy=BENCH_C[1], L=BENCH_L):
    """The exploded view's plank bench: three seat planks along X on end cleats, four chamfered legs, end rails."""
    w = (SEAT_D - 2 * 0.04) / 3
    zc = SEAT_Z - SEAT_T / 2
    for k in range(3):
        yk = cy - SEAT_D / 2 + w / 2 + k * (w + 0.04)
        P.plank(a, (cx - L / 2, yk, zc), (cx + L / 2, yk, zc), w, SEAT_T, PLANK, ch=0.05, name=f"seat{k}", kind="plank",
                amp=0.06)
    z_cl = (SEAT_Z - SEAT_T - 0.22, SEAT_Z - SEAT_T + 0.005)
    lx, ly, lh = L / 2 - 0.40, 0.30, 0.19
    for s in (-1, 1):
        x = cx + s * lx
        P.box(a, (x - 0.22, cy - SEAT_D / 2 + 0.06, z_cl[0]), (x + 0.22, cy + SEAT_D / 2 - 0.06, z_cl[1]), PLANK,
              name=f"cleat{s:+d}", kind="cleat")
        for t in (-1, 1):
            P.post(a, (x, cy + t * ly), 0.0, z_cl[0] + 0.01, lh, PLANK, ch=0.04, name=f"leg{s:+d}{t:+d}", kind="leg")
        P.box(a, (x - 0.08, cy - ly + lh - 0.01, 0.30), (x + 0.08, cy + ly - lh + 0.01, 0.50), PLANK,
              name=f"rail{s:+d}", kind="rail")


def bedroll(a, x0=BEDROLL["x"][0], x1=BEDROLL["x"][1], y=BEDROLL["y"]):
    """The leather roll lying along X against the back wall: an 8-sided log on its flat, gold end caps (a step
    smaller) and two gold straps."""
    r = BEDROLL["r"]
    ri = r / math.cos(math.pi / 8) + 0.004   # 6-sided straps round the 8-sided roll, touching its corners
    ro = ri + 0.06
    z = ro - 0.005                       # the straps carry it: their bottom flats 0.005 into the ground
    P.log(a, (x0, y, z), (x1, y, z), r, LEATHER, sides=8, name="bedroll", kind="bedroll")
    for s, xe in ((-1, x0), (1, x1)):
        P.log(a, (xe - s * 0.003, y, z), (xe + s * 0.30, y, z), r * 0.86, GOLD, sides=8,
              end_key=mix(GOLD, LEATHER, 0.35), name=f"bedroll_cap{s:+d}", kind="bedroll", amp=0.03)
    for k, xs in enumerate((x0 + 0.75, x1 - 0.75)):
        P.sleeve(a, (xs - 0.13, y, z), (xs + 0.13, y, z), ri, ro, GOLD, sides=6,
                 name=f"bedroll_strap{k}",
                 kind="bedroll", amp=0.03)


def sleeping_mat(a):
    """The gold mat on the floor in front of the bedroll, two teal stripes across it (stations, colour by place)."""
    (x0, y0), (x1, y1), t = MAT_BOX
    xc = (x0 + x1) / 2
    cuts = [s - y0 for ab in STRIPES for s in ab]
    return P.beam(a, (xc, y0, t / 2), (xc, y1, t / 2), P.sec_rect((x1 - x0) / 2, t / 2), MAT, stations=cuts,
                  colour=lambda l: STRIPE if any(lo - y0 < l.s < hi - y0 for lo, hi in STRIPES) else MAT,
                  name="mat", kind="mat", amp=0.03)


# ---- moss and ivy ----------------------------------------------------------------------------------------------------
MOSS = (((-4.3, 5.5), 0.55, 0.20), ((-6.5, 5.6), 0.50, 0.18), ((5.9, 4.9), 0.45, 0.16), ((-8.1, 2.2), 0.45, 0.16))
MOSS_KEYS = (IVY_D, IVY_G, IVY_L)
WALLS = {"BI": P.Wall("BI", (0, BACK_Y[0], 0), (0, -1, 0), (1, 0, 0)),
         "BO": P.Wall("BO", (0, BACK_Y[1], 0), (0, 1, 0), (1, 0, 0)),
         "SF": P.Wall("SF", (0, SIDE_Y0, 0), (0, -1, 0), (1, 0, 0)),
         "SO": P.Wall("SO", (SIDE_X[0], 0, 0), (-1, 0, 0), (0, 1, 0))}
TOP7, TOP6, TOP5, TOP4 = COURSE * 7, COURSE * 6, COURSE * 5, COURSE * 4
R_MAIN, R_BR = 0.12, 0.08
# per run: the face it climbs, the top it lips over, its stems (P.ivy): lip = (s, pad (x, y)) on the top
IVY_RUNS = {
    "R1": dict(wall="BI", top=TOP7, stems=[
        dict(id="main", r=R_MAIN, lip=(-3.0, (-3.0, 4.85)), lipn=2, n=12, sz=[(-3.0, 13.3), (-2.75, 11.3), (-3.1, 9.2)]),
        dict(id="A", r=R_BR, parent=("main", 12.6), n=6, sz=[(-4.4, 11.6), (-4.8, 9.6)]),
        dict(id="C", r=R_BR, parent=("main", 9.8), n=4, sz=[(-3.6, 8.2), (-3.8, 6.6)])]),
    "R2": dict(wall="BO", top=TOP7, stems=[
        dict(id="main", r=R_MAIN, lip=(0.3, (0.3, 5.45)), lipn=1, n=11, sz=[(0.3, 13.3), (0.55, 10.6), (0.25, 7.2)]),
        dict(id="A", r=R_BR, parent=("main", 11.8), n=4, sz=[(1.2, 10.6), (1.4, 9.0)]),
        dict(id="B", r=R_BR, parent=("main", 9.6), n=4, sz=[(-0.6, 8.2), (-0.8, 6.2)])]),
    "R3": dict(wall="BO", top=TOP5, stems=[
        dict(id="main", r=R_BR + 0.02, lip=(4.25, (4.25, 5.45)), lipn=1, n=4, sz=[(4.25, 9.4), (4.5, 6.6), (4.2, 4.4)])]),
    "R4": dict(wall="SF", top=TOP4, stems=[
        dict(id="main", r=R_BR, lip=(-8.25, (-8.25, -5.9)), lipn=2, n=6, sz=[(-8.25, 7.45), (-8.05, 5.4), (-8.3, 3.6)])]),
    "R5": dict(wall="SO", top=TOP4, stems=[
        dict(id="main", r=R_BR, lip=(-3.0, (-8.6, -3.0)), lipn=1, n=6, sz=[(-3.0, 7.45), (-2.7, 5.2), (-3.0, 3.0)])]),
}
IVY_KEYS = {"lime": IVY_L, "green": IVY_G, "dark": IVY_D, "stem": STEM}
PAD_TOP = 0.035                     # the lip pads' top above the stone (P.ivy's 0.105 sat 0.06-0.08 into the stems)


def lower_pads(a, n0, runs):
    """P.ivy seats each lip stem's underside 0.06 into its pad's top, and the stem's slope down to the edge sinks it
    0.07-0.08 (the old build's suite failure). Lower every pad's top four verts to PAD_TOP over the stone, so the
    stem rests 0.01 over the pad at its start and dips into it 0.03 at most toward the edge."""
    bm = a.bm
    bm.verts.ensure_lookup_table()
    s = P.IVY
    moved = 0
    for run in runs.values():
        for st in run["stems"]:
            if "lip" not in st:
                continue
            px, py = st["lip"][1]
            zt = run["top"] + 0.005 + s["pad_t"]
            for v in bm.verts[n0:]:
                if abs(v.co.z - zt) < 1e-4 and abs(v.co.x - px) < 0.3 and abs(v.co.y - py) < 0.3:
                    v.co.z = run["top"] + PAD_TOP
                    moved += 1
    for f in bm.faces:
        f.normal_update()
    return moved


def prune_leaves(a, n0, lim=0.045):
    """P.ivy keeps each leaf off the stone and its own stem, but not off its neighbours: on dense curtains a leaf can
    sink 0.05-0.08 into the next leaf or a branch stem (kit_verify samples verts, face centres and edge midpoints).
    Drop the later of every such pair (and its register entries). Returns the names dropped."""
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
    names = [l["name"] for l in P.LEAVES]
    if len(leaves) != len(names):
        return []
    shells = comps

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
    I = [info(c) for c in shells]
    leaf_ix = {id(c): k for k, c in enumerate(leaves)}

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
    for s, c in enumerate(shells):
        if id(c) not in leaf_ix:
            continue
        for t, c2 in enumerate(shells):
            if t == s or t in drop or s in drop:
                continue
            if depth_in(s, t) > lim or depth_in(t, s) > lim:
                if id(c2) in leaf_ix and leaf_ix[id(c2)] > leaf_ix[id(c)]:
                    drop.add(t)
                else:
                    drop.add(s)
    gone = [names[leaf_ix[id(shells[s])]] for s in sorted(drop) if id(shells[s]) in leaf_ix]
    bmesh.ops.delete(bm, geom=[v for s in drop for v in shells[s]], context="VERTS")
    P.PIECES[:] = [p for p in P.PIECES if p[1] not in gone]
    P.LEAVES[:] = [l for l in P.LEAVES if l["name"] not in gone]
    return gone


def dressing(a, keep_pieces, runs=IVY_RUNS, moss=MOSS, walls=WALLS):
    """Moss on the exposed tops and the ivy runs, both draped on the stone tree; leaves kept off the timber, rope
    and canvas (keep_pieces)."""
    tree = P.tree_of(*STONE_PIECES)
    for i, (xy, r, h) in enumerate(moss):
        P.moss(a, xy, r, h, tree, MOSS_KEYS, seed_=7100 + i, name=f"moss{i}")
    keep = P.tree_of(*keep_pieces) if keep_pieces else None
    n0 = len(a.bm.verts)
    res = P.ivy(a, runs, walls, tree, IVY_KEYS, keep=keep, seed_=7070)
    P.GEO["pads_lowered"] = lower_pads(a, n0, runs)
    P.GEO["ivy_dropped"] = res["dropped"]
    P.GEO["leaves_pruned"] = prune_leaves(a, n0)
    return res


# ---- assemblies ------------------------------------------------------------------------------------------------------
def hero_all(a):
    STONE_PIECES.clear()
    walls(a)
    for i, (c, size, yaw, chips) in enumerate(RUBBLE):
        rubble(a, c, size, yaw, chips, f"rubble{i}")
    keep = []
    n_before = len(P.PIECES)
    v_before = len(a.bm.verts)
    for tag in POSTS:
        post_all(a, tag)
    keep.append(crossbeam(a))
    cv = canopy(a)
    keep.append(cv)
    P.GEO["timber_pieces"] = len(P.PIECES) - n_before
    banner(a)
    for nm, c in CRATES.items():
        with P.frame(None, nm + "_"):
            crate(a, c, name="crate")
    barrel(a)
    with P.frame(None, "box_"):
        P.crate(a, BOX_C, PLANK, WOOD_DARK, W=1.20, H=1.20, frame_t=(0.0, 0.9), open_top=False, braces=False,
                name="box")
    bedroll(a)
    sleeping_mat(a)
    # the keep-out tree for the ivy: every piece built since the stone (posts, rope, canvas, banner, props), minus the
    # footings (stone the ivy may touch)
    a.bm.verts.ensure_lookup_table()
    foot = {v for p in STONE_PIECES if p.name and "footing" in p.name for v in p.vs}
    keep_vs = [v for v in a.bm.verts[v_before:] if v not in foot]
    dressing(a, [keep_vs] + keep)


def section(a):
    """The exploded view's ruin chunk: two block columns with an opening between them, a three-block course over
    it, a broken top course stepping up on the left, an ivy run down the front face and a moss patch."""
    STONE_PIECES.clear()
    rng = random.Random(7020)
    rows = [  # (course, [(x0, x1)])
        (0, [(-3.75, -1.25), (1.25, 3.75)]), (1, [(-3.75, -1.35), (1.35, 3.75)]),
        (2, [(-3.75, -1.25), (-1.20, 1.20), (1.25, 3.75)]), (3, [(-3.75, -1.15), (-1.10, 1.50)]),
        (4, [(-3.0, -0.6)])]
    for k, spans in rows:
        z0 = 0.0 if k == 0 else COURSE * k + SEAT
        H = COURSE * (k + 1) - z0
        for i, (x0, x1) in enumerate(spans):
            chips = [("+x-y", 0.35)] if (k, i) in ((3, 1), (4, 0)) else []
            m = Matrix.Translation(((x0 + x1) / 2, 0.0, z0)) @ Matrix.Rotation(math.radians(rng.uniform(-0.5, 0.5)),
                                                                               4, "Z")
            STONE_PIECES.append(blk(a, x1 - x0, DEPTH, H, course_key(k), m=m, chips=chips,
                                    chip_key=mix(STONE, STONE_LIGHT, 0.5), name=f"S{k}_{i}", kind="block"))
    walls = {"F": P.Wall("F", (0, -DEPTH / 2, 0), (0, -1, 0), (1, 0, 0))}
    runs = {"S1": dict(wall="F", top=COURSE * 5, stems=[
        dict(id="main", r=R_BR + 0.02, lip=(-1.5, (-1.5, -0.4)), lipn=1, n=5, sz=[(-1.5, 9.4), (-1.3, 7.0),
                                                                                  (-1.55, 4.9)])])}
    dressing(a, [], runs=runs, moss=(((-2.2, 0.3), 0.45, 0.16),), walls=walls)


def rubble_part(a):
    STONE_PIECES.clear()
    loose = (((-0.9, 0.0), (1.9, 1.7, 1.4), -8.0, [("-x-y", 0.35)]),
             ((1.15, 0.2), (1.5, 1.4, 1.2), 12.0, [("+x+y", 0.35)]),
             ((0.2, -1.55), (1.1, 1.0, 0.8), 30.0, [("-x+y", 0.25)]))
    for i, (c, size, yaw, chips) in enumerate(loose):
        rubble(a, c, size, yaw, chips, f"rubble{i}")


def post_part(a):
    """The reusable tall post (12.0 on a 1.0 footing) with its lashing and collars, without the footing."""
    x, y, top = 0.0, 0.0, POSTS["FR"][2]
    post(a, "FR", x, y, top)
    lashing(a, "FR", x, y)


PARTS = ((BLOCK_P, lambda a: blk(a, 2.5, DEPTH, COURSE, STONE, chips=[("+x-y", 0.35)],
                                 chip_key=mix(STONE, STONE_LIGHT, 0.5), name="block", kind="block")),
         (SECTION_P, section), (RUBBLE_P, rubble_part), (CANOPY_P, canopy), (POST_P, post_part),
         (BANNER_P, banner), (BEDROLL_P, lambda a: bedroll(a, -1.6, 1.6, 0.0)),
         (TABLE_P, lambda a: bench(a, 0.0, 0.0)), (CRATE_P, lambda a: crate(a, (0.0, 0.0))),
         (BARREL_P, lambda a: barrel(a, (0.0, 0.0))))

NOTES = {
    HERO: "Ruined lean-to (sheet 070, remade): an L of chamfered pale stone blocks (2.3 deep, 1.95 courses; back wall "
          "stepping to a seven-course 13.65 peak left of centre, side wall four to five courses) with chipped tops, ivy "
          "curtains and moss; three square posts on stone footings (FL 9.4, back 11.3, FR 12.0) with gold turns and "
          "X-lashings, a crossbeam on the side wall top; one cream canvas tied at the front posts and gathered across "
          "the back post, its front edge pulled down over the right crate (rope tail and toggle), underside >= 6.9 "
          "over the walk lane; a red three-point banner with a white diamond on a crossarm off the FR post, a dark pole "
          "behind it; bedroll, gold mat with teal stripes, two closed crates, a lidded barrel, a plank bench; rubble.",
    BLOCK_P: "Ruin Wall Block: one chamfered stone block 2.5 x 2.3 x 1.95 with a chipped corner",
    SECTION_P: "Ruin Wall Section: a chunk of five courses with an opening, ivy run and moss",
    RUBBLE_P: "Stone Rubble: three loose chipped blocks",
    CANOPY_P: "Canvas Canopy: the canvas with its pulled-down front corner, rope tail and toggle",
    POST_P: "Upright Post: 1.04 square timber post, 12.0 on a 1.0 footing (the part has no footing), gold X-lashing "
            "and two collar bands",
    BANNER_P: "Banner: crossarm with knob, dark pole, hem sleeve and the three-point red cloth with the white diamond",
    BEDROLL_P: "Bedroll: leather roll with gold end caps and two straps",
    TABLE_P: "Table / Bench: three-plank bench, seat 1.50, on cleats and four legs",
    CRATE_P: "Crate: closed X-braced crate, 2.30 cube",
    BARREL_P: "Barrel: lidded hooped barrel, 2.72 tall",
}
COLLISION = {HERO: "precise", BLOCK_P: "box", SECTION_P: "hull", RUBBLE_P: "hull", CANOPY_P: "none", POST_P: "hull",
             BANNER_P: "none", BEDROLL_P: "hull", TABLE_P: "box", CRATE_P: "box", BARREL_P: "hull"}
BUDGETS = {HERO: 6000}
TARGET_SIZE = None
VIEWS = {"f34_sheet": (0, 24), "front_sheet": (0, 0), "side_sheet": (90, 0), "rear_sheet": (180, 0),
         "top_sheet": (0, 89.9)}
EXPLODED = None
WALK = {"paths": [[(-1.55, -12.0), (-1.55, 0.6)]], "ride": True, "skip": ("mat",), "turn": [(-1.55, -0.4, MAT_BOX[2])]}
VERIFY = dict(cls="structure", walk=WALK, foliage={"keys": ("leaf",)})
COMPARE = {"f34": {"box": (16, 122, 506, 484), "view": (0, 24), "lens": 1.5},
           "r34": {"box": (518, 122, 1008, 484), "view": (145, 22), "mirror": True},
           "front": {"box": (18, 570, 268, 772), "view": (0, 0)},
           "side": {"box": (279, 570, 506, 772), "view": (90, 0)},
           "rear": {"box": (519, 570, 758, 772), "view": (180, 0)},
           "top": {"box": (771, 563, 1008, 775), "view": (0, 89.9)}}


def lean_check(objs):
    """Spec "Brief": the canvas underside at least HEADROOM over the walk lane (rays up from the floor along the walk
    path and 1.0 either side); crate tops 2.30 and the barrel lid (rays down)."""
    h = objs[HERO]
    me = h.data
    tree = BVHTree.FromPolygons([h.matrix_world @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])
    up, down = Vector((0, 0, 1)), Vector((0, 0, -1))

    def ray(x, y, z, d):
        hit = tree.ray_cast(MODEL.at(h, (x, y, z)), d)[0]
        return round(hit.z - h.matrix_world.translation.z + h[MODEL.OFF][2], 3) if hit else None
    x_lane = WALK["paths"][0][0][0]
    under = []
    for dx in (-1.0, 0.0, 1.0):
        y = -7.0
        while y <= 0.6:
            z = ray(x_lane + dx, y, 6.0, up)
            if z is not None:
                under.append((z, (round(x_lane + dx, 2), round(y, 2))))
            y += 0.25
    low = min(under) if under else (None, None)
    rep = {"lane_canvas_under": low[0], "at": low[1], "canvas": P.GEO.get("canvas", {}),
           "crate_tops": {k: ray(c[0] + 0.05, c[1] + 0.05, 2.9, down) for k, c in CRATES.items()},
           "barrel_top": ray(BARREL_C[0] + 0.1, BARREL_C[1] + 0.1, 4.0, down)}
    pr = []
    if low[0] is not None and low[0] < HEADROOM:
        pr.append(f"{HERO}: canvas underside {low[0]} at {low[1]} over the walk lane, under {HEADROOM}")
    pr += [f"{HERO}: crate {k} top {z} not 2.30" for k, z in rep["crate_tops"].items() if z is None or abs(z - 2.30) > 0.02]
    return rep, pr


def build(render=True, close=False, spin=False):
    def after(objs):
        h = objs[HERO]
        h["m070_centre"] = [round(x, 4) for x in -Vector(h[MODEL.OFF])]
    return MODEL.run(hero=(HERO, hero_all), parts=PARTS, notes=NOTES, collision=COLLISION, budgets=BUDGETS,
                     target_size=TARGET_SIZE, views=VIEWS, exploded=EXPLODED, close=CLOSE if close else None,
                     verify=VERIFY, checks=[lean_check], after=after, render=render, spin=spin)


CLOSE = {"lash_cu": dict(at=(POSTS["FR"][0], POSTS["FR"][1], 9.7), r=1.8, az=-30, el=10),
         "low_cu": dict(at=(LOW[0], LOW[1], 5.6), r=2.2, az=15, el=10),
         "ivy_cu": dict(at=(-3.2, BACK_Y[0], 11.0), r=3.0, az=10, el=10),
         "pad_cu": dict(at=(-3.0, 4.85, TOP7), r=1.0, az=20, el=35)}


def preview(names=("f34_sheet", "front_sheet", "side_sheet")):
    return MODEL.preview(HERO, VIEWS, names)


def compare(cells=None, out_dir=None):
    import importlib
    import compare as C
    importlib.reload(C)
    return C.compare(NUM, {k: COMPARE[k] for k in (cells or COMPARE)}, out_dir=out_dir)
