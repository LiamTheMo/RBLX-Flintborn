"""066 Canvas Shelter (references/066.png, remade 2026-11-04) on the shared library (kit_parts / kit_build): an open
walk-under camp shelter, open on all four sides. Four chunky square timber posts (the right pair 12.0, the left pair
10.4) on tapered stone footings, a square ridge beam lashed level along the inner faces of the two tall posts and
sticking out past the front-right post, one cream canvas sheet tied by its four corners into fat gold X-lashings (the
back-right corner high, up under the beam), a red three-tailed banner with a white diamond emblem on a wooden rod
lashed to the front-left post, and a dark square lantern with Neon glass hung from an iron bracket under the
front-right corner. Under the canopy: a three-plank table with a paper and two bottles, a long bench behind it and a
shorter one in front, a closed X-braced crate by the right side and a lidded hooped barrel on the left side by the
back-left post.

    import importlib, kit_parts, kit_build, m066
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m066); m066.build()

Build frame (studs): front -Y (the hero view looks from the front-left), +X right (the tall side with the ridge beam),
ground z 0, the post rectangle centred on x 0 / y 0 (post centres 14.0 x 10.4). Every piece is its own closed shell
(no booleans), seated 0.002-0.03 into or onto what holds it. Names (spec "Brief"): hero CanvasShelter; parts
CanvasShelterPost, ...Footing, ...RidgePole (the sheet's "Ridge Beam"), ...Canopy, ...Banner, ...Lantern, ...Table,
...Bench, ...Stool, ...Crate, ...Barrel. Stage 5-6: the lantern glass is m066_glow at emission 1.0 (Neon) with one
heat_glow socket. See M066_spec.md.
"""
import math

from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_build as B
import kit_parts as P

NUM, TITLE = 66, "Canvas Shelter"
HERO = "CanvasShelter"
POST_P, FOOT_P, RIDGE_P = "CanvasShelterPost", "CanvasShelterFooting", "CanvasShelterRidgePole"
CANOPY_P, BANNER_P, LANTERN_P = "CanvasShelterCanopy", "CanvasShelterBanner", "CanvasShelterLantern"
TABLE_P, BENCH_P, STOOL_P = "CanvasShelterTable", "CanvasShelterBench", "CanvasShelterStool"
CRATE_P, BARREL_P = "CanvasShelterCrate", "CanvasShelterBarrel"

TIMBER, PLANK, WOOD_DARK, WOOD_DEEP = "m066_timber", "m066_plank", "m066_wood_dark", "m066_wood_deep"
CANVAS, CANVAS_DEEP = "m066_canvas", "m066_canvas_deep"
ROPE, ROPE_DEEP = "m066_rope", "m066_rope_deep"
STONE, STONE_DEEP = "m066_stone", "m066_stone_deep"
BANNER, BANNER_DEEP, BANNER_WHITE = "m066_banner", "m066_banner_deep", "m066_banner_white"
METAL, IRON, GLOW = "m066_metal", "m066_iron", "m066_glow"
BOTTLE, AMBER, PAPER = "m066_bottle", "m066_amber", "m066_paper"

# key -> (hex, roughness, metal, emission, low specular). Stage 4 (spec "Stage 4"): woods and metal from
# MODEL.calibrate(); canvas, rope, stone and banner then corrected against the hero render (the dome pulls the canvas
# salmon, so don't recalibrate it blindly).
PALETTE = {TIMBER: ("#B96825", 0.85, 0.0, 0.0, True), PLANK: ("#9A5621", 0.85, 0.0, 0.0, True),
           WOOD_DARK: ("#8B4C16", 0.85, 0.0, 0.0, True), WOOD_DEEP: ("#522810", 0.9, 0.0, 0.0, True),
           CANVAS: ("#D2B99E", 0.95, 0.0, 0.0, True), CANVAS_DEEP: ("#B09276", 0.95, 0.0, 0.0, True),
           ROPE: ("#C29237", 0.95, 0.0, 0.0, True), ROPE_DEEP: ("#9A6E20", 0.95, 0.0, 0.0, True),
           STONE: ("#AAA4A4", 0.92, 0.0, 0.0, True), STONE_DEEP: ("#878080", 0.92, 0.0, 0.0, True),
           BANNER: ("#BE1F14", 0.9, 0.0, 0.0, True), BANNER_DEEP: ("#821410", 0.9, 0.0, 0.0, True),
           BANNER_WHITE: ("#F2EAE6", 0.9, 0.0, 0.0, True),
           METAL: ("#543F30", 0.55, 0.4, 0.0, False), IRON: ("#6E6A6C", 0.5, 0.5, 0.0, False),
           GLOW: ("#F2B010", 0.5, 0.0, B.NEON, False),
           BOTTLE: ("#7C8A40", 0.4, 0.0, 0.0, False), AMBER: ("#E0A020", 0.4, 0.0, 0.0, False),
           PAPER: ("#F5E2B0", 0.9, 0.0, 0.0, True)}
# calibration targets: the sheet's rendered medians (hero view and swatches; spec "Stage 4") and K.sample kinds
TARGETS = {TIMBER: ((0xB8, 0x5A, 0x18), "brown"), PLANK: ((0xC2, 0x6C, 0x2A), "brown"),
           WOOD_DARK: ((0x9A, 0x4A, 0x16), "brown"), CANVAS: ((0xFC, 0xEB, 0xC6), "all"),
           CANVAS_DEEP: ((0xE6, 0xC2, 0x96), "all"), ROPE: ((0xEA, 0xAF, 0x55), "vivid"),
           STONE: ((0xA8, 0x97, 0x8E), "all"), BANNER: ((0xD8, 0x1A, 0x12), "vivid"),
           METAL: ((0x5A, 0x42, 0x30), "all")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)


def mix(k1, k2, t):
    return P.mix(k1, k2, t, step=0.05)


# ---- layout (spec "Brief" and "Stage 1") ---------------------------------------------------------------------------
PX, PY = 7.0, 5.2                       # post centres (14.0 x 10.4: the hero view's footprint, 1.35 : 1)
PH, PCH, CAP = 0.65, 0.065, 0.08        # post half width (1.3 square, round 1 fix), vertical edge chamfer, top bevel
FOOT_H = 1.30                           # stone footing: tapered, flat top (2.1 base, 1.64 top, 1.30 high)
FOOT_RINGS = ((0.0, 1.05, 0.12), (1.10, 0.95, 0.11), (FOOT_H, 0.82, 0.09))     # (z, half, chamfer)
POST_Z0 = FOOT_H - 0.02                 # posts seated 0.02 into the footing top
POSTS = {"FL": (-PX, -PY, 10.4), "BL": (-PX, PY, 10.4), "FR": (PX, -PY, 12.0), "BR": (PX, PY, 12.0)}
BEAM_X = (PX - PH - 0.79, PX - PH + 0.01)    # ridge beam on the tall posts' inner faces (sunk 0.01)
BEAM_Z = (10.15, 10.95)
BEAM_Y = (-PY - 1.40, PY + 0.80)        # 0.9 past the front-right post's front face; 0.3 past the back-right's
SEAT = 0.02
# rope (m048 / m050 language): corner-cut twisted turns, 4-sided twisted diagonals
TURN_R, TURN_CUT = 0.16, 0.13
TURN_OUT = TURN_R - P.SINK              # a turn's centreline off the post face
DIAG_R = 0.15
# diagonal ends PH - X_IN off the face centre, pulled PULL * TURN_R out of the turn (1.65 sank 0.12 into the turns on
# the 1.3 post, where the X runs flatter; 2.4 leaves 0.065, under the 0.08 rope-in-rope limit)
X_IN, PULL = 0.10, 2.4
LASH = {                                # turns (z) and the faces carrying an X; "over": the timber the X crosses
    "FL": dict(turns=(8.40, 9.80), faces=[((0, -1), "rod"), ((-1, 0), None)]),
    "BL": dict(turns=(8.40, 9.60), faces=[((-1, 0), None), ((0, 1), None)]),
    "FR": dict(turns=(8.92, 9.64), faces=[((0, -1), None), ((1, 0), None)]),
    "FRb": dict(turns=(9.99, 11.11), faces=[((-1, 0), "beam"), ((0, -1), None)]),
    "BR": dict(turns=(9.62, 11.11), faces=[((-1, 0), "beam"), ((0, 1), None), ((1, 0), None)]),
}
# canvas (top-surface corners at the posts' inner corners, 0.02 toward the post axis; BR up under the beam)
CORNER_Z = {"FL": 9.10, "BL": 9.10, "FR": 9.35, "BR": BEAM_Z[0] - 0.03}
SAG = dict(v0=1.95, u1=1.50, v1=1.60, u0=1.70, c=2.20)      # front, right, back, left edge middles; centre
RIDGE = 0.45                            # share of the sag the corner-to-centre tension lines keep up (the X creases)
CANVAS_NU, CANVAS_NV, CANVAS_T = 7, 7, 0.10
HEADROOM = 6.9
# banner and rod: the rod along X across the front-left post's front face, ending just right of the post centre; the
# cloth facing front, hung by two red bands round the rod, its right part over the post's left half, in front of the
# rod and the lower turn (the front X of that lashing ends on the rod's top, so nothing crosses the cloth)
ROD_R, ROD_Z = 0.18, 8.85
ROD_Y = -PY - PH - ROD_R + SEAT
BAN_W = 2.05
BAN_X = (-PX - 0.10 - BAN_W, -PX - 0.10)                # cloth right edge 0.10 short of the post centre
BAN_Y = ROD_Y - 0.25                                    # cloth plane: 0.03 clear of the rod, 0.07 of the lower turn
BAN_TOP = ROD_Z - 0.10
BANDS = ((BAN_X[0] - 0.02, BAN_X[0] + 0.30), (-PX - PH - 0.65, -PX - PH - 0.33))   # red bands, clear of the lashing
BAND_RO = ROD_R + 0.13
ROD_X = (BAN_X[0] - 0.35, -PX + 0.45)
ROD_XE = 0.25                                           # the front X's ends on the rod top, either side of the centre
BAN_TIP, BAN_NOTCH = 2.75, 3.55
# lantern under the front-right corner, on an iron bracket off the post's inner face
LANT_XY = (PX - 1.6, -PY)
ARM_Z = 8.35
LANT = dict(w=1.0, plate=0.16, gw=0.72, gh=1.15, band=0.18, roof=0.30, fin=0.12, bar=0.13)
# furniture (HOUSE_RULES heights: table top 2.60, seats 1.50, crate 2.30, barrel 2.72)
TABLE_C, TABLE_L, TABLE_D, TOP_Z, TOP_T = (-0.2, -0.9), 7.0, 3.0, 2.60, 0.40
BENCHES = {"back": ((-0.4, 1.55), 6.4), "front": ((0.9, -3.40), 5.8)}
SEAT_Z, SEAT_T, SEAT_D = 1.50, 0.40, 1.30
STOOL_C = (0.0, 0.0)
CRATE_C, CRATE_W, CRATE_H = (5.15, -1.75), 2.30, 2.30     # clear of the table end and the front bench
BRACE_PROUD = 0.10                      # crate braces stand this far off the recessed panels (P.crate: 0.05)
BARREL_C = (-5.70, 2.50)                # just inside the left posts, as the hero, front, rear and r34 cells draw it
GAP = 0.04


# ---- timber ----------------------------------------------------------------------------------------------------------
def footing(a, x, y, name="footing"):
    """The stone footing (close-up "Post & Footing"): a tapered square block with chamfered corners and a flat top,
    its lower band a little deeper (by height)."""
    rings = [[(x + u, y + v, z) for u, v in P.sec_rect(h, h, ch)] for z, h, ch in FOOT_RINGS]
    p = P.prism(a, rings, STONE, band_keys=[mix(STONE, STONE_DEEP, 0.35), STONE], name=name, kind="stone")
    P.texture(a, p.vs, 0.04, P.seed(P.TAG[-1] + name), scale=0.6)
    return p


def post(a, x, y, top, name="post"):
    """A square post (8-sided: vertical edges chamfered) from the footing top to `top`, its top edge bevelled."""
    sec = P.sec_rect(PH, PH, PCH)
    cap = P.sec_rect(PH - CAP, PH - CAP, PCH * 0.6)
    rings = [[(x + u, y + v, z) for u, v in sec] for z in (POST_Z0, top - CAP)]
    rings.append([(x + u, y + v, top) for u, v in cap])
    return P.prism(a, rings, TIMBER, name=name, kind="post")


def ridge(a, name="ridge"):
    """The ridge beam: 0.8 square (edges chamfered 0.05) along Y on the tall posts' inner faces."""
    xc, zc = sum(BEAM_X) / 2, sum(BEAM_Z) / 2
    return P.plank(a, (xc, BEAM_Y[0], zc), (xc, BEAM_Y[1], zc), BEAM_X[1] - BEAM_X[0], BEAM_Z[1] - BEAM_Z[0], TIMBER,
                   ch=0.05, name=name, kind="beam")


# ---- rope -----------------------------------------------------------------------------------------------------------
def turn(a, cx, cy, z, name):
    """A tight round turn about a post (m048 / m050): a closed twisted loop with its corners cut at 45 deg and a
    midpoint on each side; the innermost strands sink P.SINK into the post faces. 120 tris."""
    c4 = P.rect_loop((cx - PH, cy - PH), (cx + PH, cy + PH), z, TURN_OUT)
    loop = []
    for k in range(4):
        a_, b_ = c4[k], c4[(k + 1) % 4]
        d = (b_ - a_).normalized()
        loop += [a_ + d * TURN_CUT, (a_ + b_) / 2, b_ - d * TURN_CUT]
    return P.rope(a, loop, TURN_R, ROPE, ROPE_DEEP, sides=5, closed=True, twist=True, up=(0, 0, 1), name=name,
                  kind="rope_turn")


def diagonals(a, cx, cy, z_lo, z_hi, face, name, over=None, lift=0.24):
    """Two diagonals crossing on a post face from the upper turn to the lower one (P.x_lashing's diagonals, on the
    corner-cut turns): over = (face distance of a timber lying on that face, its top z, its bottom z) takes them
    round its top and bottom edges; the second diagonal is lifted `lift` where they cross."""
    n = Vector((face[0], face[1], 0.0)).normalized()
    ax = Vector((-n.y, n.x, 0.0))
    c = Vector((cx, cy, 0.0))
    dt = PH + TURN_OUT
    d0 = PH + 0.8 * DIAG_R - P.SINK
    xh = PH - X_IN
    out = []
    for k, sg in enumerate((1, -1)):
        S = c + n * dt + ax * (-sg * xh)
        S.z = z_hi
        E = c + n * dt + ax * (sg * xh)
        E.z = z_lo
        lf = lift if k else 0.0
        if over:
            fd, top, bot = over
            o = 0.8 * DIAG_R - P.SINK
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
        S0 = S + (inner[0] - S).normalized() * (PULL * TURN_R)
        E0 = E + (inner[-1] - E).normalized() * (PULL * TURN_R)
        out.append(P.rope(a, [S0] + inner + [E0], DIAG_R, ROPE, ROPE_DEEP, sides=4, up=n, name=f"{name}_x{k}",
                          kind="rope_diag"))
    return out


def rod_x(a, cx, cy, z_hi, face, name, lift=0.24):
    """The X binding the banner rod (sheet hero): two diagonals from the upper turn down across the post face, each
    ending on the rod's top on the far side of the centre, so nothing runs below the rod where the cloth hangs."""
    n = Vector((face[0], face[1], 0.0)).normalized()
    ax = Vector((-n.y, n.x, 0.0))
    c = Vector((cx, cy, 0.0))
    dt = PH + TURN_OUT
    d0 = PH + 0.8 * DIAG_R - P.SINK
    xh = PH - X_IN
    rc = abs(ROD_Y - cy)                                    # the rod's centre off the post centre
    ze = ROD_Z + ROD_R + 0.8 * DIAG_R - P.SINK
    out = []
    for k, sg in enumerate((1, -1)):
        S = c + n * dt + ax * (-sg * xh)
        S.z = z_hi
        E = c + n * rc + ax * (sg * ROD_XE)
        E.z = ze
        mid = c + n * (d0 + (lift if k else 0.0))
        mid.z = (z_hi + ze) / 2
        S0 = S + (mid - S).normalized() * (PULL * TURN_R)
        out.append(P.rope(a, [S0, mid, E], DIAG_R, ROPE, ROPE_DEEP, sides=4, up=n, name=f"{name}_x{k}",
                          kind="rope_diag"))
    return out


def lashing(a, tag, cx, cy, spec=None):
    """A post's X-lashing (close-up "Lashing Detail"): two turns and an X on each listed face."""
    spec = spec or LASH[tag]
    z_lo, z_hi = spec["turns"]
    turn(a, cx, cy, z_lo, f"lash{tag}_lo")
    turn(a, cx, cy, z_hi, f"lash{tag}_hi")
    for i, (face, what) in enumerate(spec["faces"]):
        if what == "rod":
            rod_x(a, cx, cy, z_hi, face, f"lash{tag}_{i}")
            continue
        over = (cx - BEAM_X[0], BEAM_Z[1], BEAM_Z[0]) if what == "beam" else None
        diagonals(a, cx, cy, z_lo, z_hi, face, f"lash{tag}_{i}", over=over)


# ---- canvas ----------------------------------------------------------------------------------------------------------
def corner_xy(tag):
    x, y, _ = POSTS[tag]
    sx, sy = (1 if x < 0 else -1), (1 if y < 0 else -1)          # toward the shelter's middle
    return x + sx * (PH - SEAT), y + sy * (PH - SEAT)


def canvas_sheet(a, corners, key, deep, nu, nv, sag, ridge, hem=0.35, ct=0.10, name="canvas", kind="canvas"):
    """P.canvas (m070) with tension lines: the sag is eased by `ridge` along the two diagonals (u = v, u = 1 - v), so
    the X of creases from the tied corners to the centre reads as folds (sheet: top view, f34). With nu = nv the
    diagonals run along grid edges. Otherwise as P.canvas: one closed ct slab, an nu x nv top grid inset `hem`, each
    quad split along the diagonal pointing at the centre, a hem strip, the underside ct below along the vertex
    normals (straight down at the tied corners), rim faces (split into triangles: they twist where the sag is steep),
    hem colour by distance from the edge toward `deep` (deep=None: one plain colour to the edge)."""
    def mix(k1, k2, t):
        return k1 if deep is None else P.mix(k1, k2, t, step=0.05)
    C = {k: Vector(v) for k, v in corners.items()}
    s = dict(sag)
    e = s["c"] - 0.5 * (s["v0"] + s["v1"] + s["u0"] + s["u1"])

    def top(u, v):
        p = C["C1"] * (1 - u) * (1 - v) + C["C4"] * u * (1 - v) + C["C2"] * (1 - u) * v + C["C3"] * u * v
        bu, bv = 4 * u * (1 - u), 4 * v * (1 - v)
        drop = (1 - v) * s["v0"] * bu + v * s["v1"] * bu + (1 - u) * s["u0"] * bv + u * s["u1"] * bv + e * bu * bv
        dd = min(abs(u - v), abs(u + v - 1)) * math.sqrt(0.5)
        rc = min(1.0, 1.6 * math.hypot(u - 0.5, v - 0.5) / math.sqrt(0.5))     # none at the centre (the belly)
        p.z -= drop * (1.0 - ridge * rc * max(0.0, 1.0 - dd / 0.12))
        return p
    du = hem / max((C["C4"] - C["C1"]).length, 1e-6)
    dv = hem / max((C["C2"] - C["C1"]).length, 1e-6)
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
                tris.append((t, mix(key, deep, 0.20) if sum(1 for k in t if k in ring) == 3 else key))
    hk = mix(key, deep, 0.50)
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
    rim = mix(key, deep, 0.75)
    for eds in count.values():
        if len(eds) == 1:                                   # an open (outer hem) edge: two rim triangles
            u_, v_ = eds[0]
            faces += [[idx[u_], idx[v_], nb + idx[v_]], [idx[u_], nb + idx[v_], nb + idx[u_]]]
            fkeys += [rim, rim]
    p = P.shell(a, pts, faces, key, keys=[k if k != key else None for k in fkeys], name=name, kind=kind, amp=0.02)
    P.texture(a, p.vs, 0.03, P.seed(name), scale=0.18)
    P.GEO.setdefault("canvas", {})[name] = {"low_top": round(min(q.z for q in Pm.values()), 3),
                                            "low_under": round(min(q.z for q in under), 3)}
    return p


def canopy(a, name="canvas"):
    """The canvas: C1 front-left, C4 front-right, C2 back-left, C3 back-right; the back-right corner high under the
    beam; X creases along the diagonals; plain cream to the edge (the sheet has no darker hem)."""
    cn = {"C1": "FL", "C4": "FR", "C2": "BL", "C3": "BR"}
    corners = {k: (*corner_xy(t), CORNER_Z[t]) for k, t in cn.items()}
    return canvas_sheet(a, corners, CANVAS, None, CANVAS_NU, CANVAS_NV, SAG, RIDGE, hem=0.35, ct=CANVAS_T, name=name)


# ---- banner and rod --------------------------------------------------------------------------------------------------
def arrow_bar(a, cx, cz, y_face, side, half, key, bh=0.045, head=(0.16, 0.13), t=0.012, name="emblem_bar"):
    """The emblem's horizontal arrow bar (sheet hero): a bar through the diamond, `half` each side of the centre, with
    an outward arrowhead (length, half height) at each end; 0.005 into the cloth face and t proud (under the
    diamond's 0.015, so it never shares a face with it)."""
    y0, y1 = y_face - side * 0.005, y_face + side * t
    w0, w1 = min(y0, y1), max(y0, y1)

    def to3(u, v, w_):
        return Vector((u, w_, v))
    tag = "f" if side < 0 else "b"
    hl, hh = head
    xb = half - hl + 0.02
    out = [P.ext(a, [(cx - xb, cz + bh), (cx + xb, cz + bh), (cx + xb, cz - bh), (cx - xb, cz - bh)], w0, w1, key,
                 to3=to3, name=f"{name}_{tag}", kind="emblem", amp=0.02)]
    for s, nm in ((1, "r"), (-1, "l")):
        xb0 = cx + s * (half - hl)
        tri = [(xb0, cz + hh), (cx + s * half, cz), (xb0, cz - hh)]
        out.append(P.ext(a, tri if s > 0 else [tri[1], tri[0], tri[2]], w0, w1, key, to3=to3,
                         name=f"{name}_{tag}_{nm}", kind="emblem", amp=0.02))
    return out


def banner(a):
    """The rod (a round log with pale cut ends) lashed across the front-left post's front face, ending just right of
    the post centre and sticking out to the left; the three-tailed cloth hung facing front by two red bands round the
    rod, its right part over the post's left half; the white diamond emblem with its arrow bar on both faces."""
    P.log(a, (ROD_X[0], ROD_Y, ROD_Z), (ROD_X[1], ROD_Y, ROD_Z), ROD_R, TIMBER, sides=8,
          end_key=mix(TIMBER, PAPER, 0.35), name="rod", kind="rod")
    ri = ROD_R / math.cos(math.pi / 8) + 0.008
    for k, (x0, x1) in enumerate(BANDS):
        P.sleeve(a, (x0, ROD_Y, ROD_Z), (x1, ROD_Y, ROD_Z), ri, BAND_RO, BANNER, sides=8, name=f"banner_band{k}",
                 kind="banner", amp=0.02)
    w = BAN_X[1] - BAN_X[0]
    t = 0.08
    ez = (BAN_TOP + BAN_NOTCH) / 2 + 0.25
    P.banner(a, BAN_X[0], BAN_X[1], BAN_Y, BAN_TOP, BAN_TIP, BAN_NOTCH, BANNER, hem_key=mix(BANNER, BANNER_DEEP, 0.4),
             t=t, hem=0.40, points=3, emblem_key=BANNER_WHITE, emblem_z=ez, name="banner", w=w * 0.50, h=w * 0.80,
             dots=None)
    xm = (BAN_X[0] + BAN_X[1]) / 2
    for side in (-1, 1):
        arrow_bar(a, xm, ez, BAN_Y + side * t / 2, side, w * 0.44, BANNER_WHITE, name="banner_emblem_bar")


# ---- lantern ---------------------------------------------------------------------------------------------------------
def lantern_height():
    L = LANT
    top = L["plate"] + L["gh"] + L["band"] + 0.003 + L["roof"] + 0.003 + L["fin"] - 0.006
    return top - 0.01 + 0.20 + 0.06 + 0.20 + 0.06                 # P.lantern's ring top above its base


def lantern(a, with_bracket=True):
    """The square dark lantern (P.lantern, Neon glass) hung by its ring from an iron bracket arm off the front-right
    post's inner face, under the canvas corner. Returns the glass centre."""
    rt = ARM_Z - 0.30
    base = (LANT_XY[0], LANT_XY[1], rt - lantern_height())
    r = P.lantern(a, base, METAL, GLOW, ring_axis=(1, 0, 0), name="lantern", **LANT)
    if with_bracket:
        P.bracket(a, LANT_XY, (PX - PH, LANT_XY[1], 0.0), (-1, 0), ARM_Z, r["ring_top"].z, METAL, strap=0.45,
                  name="lantern_bracket")
    return r["glass"]


# ---- furniture -------------------------------------------------------------------------------------------------------
def leg(a, x, y, z1, h, name, key=PLANK):
    return P.post(a, (x, y), 0.0, z1, h, key, ch=0.04, name=name, kind="leg")


def table(a, cx=TABLE_C[0], cy=TABLE_C[1], items=True):
    """Three top planks along X on two end cleats, four chamfered legs, low end rails and a middle stretcher; a
    paper, a green bottle and an amber bottle on the top."""
    L, D = TABLE_L, TABLE_D
    w = (D - 2 * GAP) / 3
    zc = TOP_Z - TOP_T / 2
    rows = [cy - D / 2 + w / 2 + k * (w + GAP) for k in range(3)]
    for k, yk in enumerate(rows):
        P.plank(a, (cx - L / 2, yk, zc), (cx + L / 2, yk, zc), w, TOP_T, PLANK, ch=0.05, name=f"top{k}", kind="plank",
                amp=0.06)
    z_cl = (TOP_Z - TOP_T - 0.26, TOP_Z - TOP_T + 0.005)
    lx, ly, lh = L / 2 - 0.55, D / 2 - 0.45, 0.27
    for s in (-1, 1):
        x = cx + s * lx
        P.box(a, (x - 0.30, cy - D / 2 + 0.15, z_cl[0]), (x + 0.30, cy + D / 2 - 0.15, z_cl[1]), PLANK,
              name=f"cleat{s:+d}", kind="cleat")
        for t in (-1, 1):
            leg(a, x, cy + t * ly, z_cl[0] + 0.01, lh, f"leg{s:+d}{t:+d}")
        P.box(a, (x - 0.12, cy - ly + lh - 0.01, 0.45), (x + 0.12, cy + ly - lh + 0.01, 0.75), PLANK,
              name=f"rail{s:+d}", kind="rail")
    P.box(a, (cx - lx + 0.11, cy - 0.15, 0.50), (cx + lx - 0.11, cy + 0.15, 0.70), PLANK, name="stretcher",
          kind="rail")
    if items:
        table_items(a, cx, rows)


def bottle(a, x, y, z0, sides, r, h, neck_r, neck_h, key, name, rot=0.0):
    """A small bottle on the table: a body, a shoulder and a neck as one loft."""
    sec = [(math.cos(rot + 2 * math.pi * k / sides) * r, math.sin(rot + 2 * math.pi * k / sides) * r)
           for k in range(sides)]
    nk = [(u * neck_r / r, v * neck_r / r) for u, v in sec]
    zs = ((z0, sec), (z0 + h, sec), (z0 + h + 0.10, nk), (z0 + h + 0.10 + neck_h, nk))
    return P.prism(a, [[(x + u, y + v, z) for u, v in s] for z, s in zs], key, name=name, kind="item", amp=0.02)


def table_items(a, cx, rows):
    z0 = TOP_Z - 0.01
    m = Matrix.Translation((cx - 0.9, rows[0] + 0.02, 0.0)) @ Matrix.Rotation(math.radians(-12), 4, "Z")
    P.box(a, (-0.45, -0.31, z0), (0.45, 0.31, TOP_Z + 0.03), PAPER, m=m, name="paper", kind="item", amp=0.02)
    bottle(a, cx + 0.2, rows[1], z0, 8, 0.36, 0.85, 0.16, 0.30, BOTTLE, "bottle_green", rot=math.pi / 8)
    bottle(a, cx + 1.45, rows[1] + 0.05, z0, 4, 0.44, 0.72, 0.16, 0.24, AMBER, "bottle_amber", rot=math.pi / 4)


def bench(a, cx, cy, L, name_seats=True):
    """Two seat planks along X on end cleats, two chamfered legs at each end, low end rails and a stretcher."""
    w = (SEAT_D - GAP) / 2
    zc = SEAT_Z - SEAT_T / 2
    for k, yk in enumerate((cy - (w + GAP) / 2, cy + (w + GAP) / 2)):
        P.plank(a, (cx - L / 2, yk, zc), (cx + L / 2, yk, zc), w, SEAT_T, PLANK, ch=0.05, name=f"seat{k}",
                kind="plank", amp=0.06)
    z_cl = (SEAT_Z - SEAT_T - 0.24, SEAT_Z - SEAT_T + 0.005)
    lx, ly, lh = L / 2 - 0.45, 0.34, 0.22
    for s in (-1, 1):
        x = cx + s * lx
        P.box(a, (x - 0.25, cy - SEAT_D / 2 + 0.08, z_cl[0]), (x + 0.25, cy + SEAT_D / 2 - 0.08, z_cl[1]), PLANK,
              name=f"bcleat{s:+d}", kind="cleat")
        for t in (-1, 1):
            leg(a, x, cy + t * ly, z_cl[0] + 0.01, lh, f"bleg{s:+d}{t:+d}")
        P.box(a, (x - 0.09, cy - ly + lh - 0.01, 0.30), (x + 0.09, cy + ly - lh + 0.01, 0.52), PLANK,
              name=f"brail{s:+d}", kind="rail")
    P.box(a, (cx - lx + 0.08, cy - 0.11, 0.33), (cx + lx - 0.08, cy + 0.11, 0.49), PLANK, name="bstretch", kind="rail")


def stool(a, cx=STOOL_C[0], cy=STOOL_C[1]):
    """The exploded view's stool: a two-plank seat (1.4 x 1.2) on two cleats, four chamfered legs, two rails."""
    L = 1.4
    w = (SEAT_D - GAP) / 2
    zc = SEAT_Z - SEAT_T / 2
    for k, yk in enumerate((cy - (w + GAP) / 2, cy + (w + GAP) / 2)):
        P.plank(a, (cx - L / 2, yk, zc), (cx + L / 2, yk, zc), w, SEAT_T, PLANK, ch=0.05, name=f"sseat{k}",
                kind="plank", amp=0.06)
    z_cl = (SEAT_Z - SEAT_T - 0.22, SEAT_Z - SEAT_T + 0.005)
    lx, ly, lh = L / 2 - 0.24, 0.34, 0.18
    for s in (-1, 1):
        x = cx + s * lx
        P.box(a, (x - 0.18, cy - SEAT_D / 2 + 0.08, z_cl[0]), (x + 0.18, cy + SEAT_D / 2 - 0.08, z_cl[1]), PLANK,
              name=f"scleat{s:+d}", kind="cleat")
        for t in (-1, 1):
            leg(a, x, cy + t * ly, z_cl[0] + 0.01, lh, f"sleg{s:+d}{t:+d}")
        P.box(a, (x - 0.08, cy - ly + lh - 0.01, 0.32), (x + 0.08, cy + ly - lh + 0.01, 0.50), PLANK,
              name=f"srail{s:+d}", kind="rail")


def crate(a, c=CRATE_C):
    """The closed X-braced crate (P.crate, sheet hero): the frame, lid and braces in the lighter plank wood over darker
    recessed panels, the braces thickened to stand BRACE_PROUD off the panels (0.045 past the frame face); its hidden
    bottom in the panel key (a deep bottom would darken only the down-facing face)."""
    out = P.crate(a, c, PLANK, WOOD_DARK, W=CRATE_W, H=CRATE_H, frame_t=(0.0, 1.0), open_top=False, name="crate")
    body = out[0]
    P.paint(a, [body.fs[0]], WOOD_DARK)
    for f in body.fs[:2]:                                   # bottom and lid: the mean Tint, not a random draw
        P.tint(a, [f], 1.0 / max(f.loops[0][a.tint_layer][0], 1e-3))
    for br in out[1:]:                                      # box_pts: back quad (on the panel) then front quad
        for vb, vf in zip(br.vs[:4], br.vs[4:8]):
            d = vf.co - vb.co
            vf.co = vb.co + d * (BRACE_PROUD / d.length)
        for f in br.fs:
            f.normal_update()
    return out


def barrel(a, c=BARREL_C):
    return P.barrel(a, c, WOOD_DARK, WOOD_DEEP, IRON, open_top=False, lid_key=mix(WOOD_DARK, WOOD_DEEP, 0.3),
                    name="barrel")


# ---- assemblies ------------------------------------------------------------------------------------------------------
def post_all(a, tag):
    x, y, top = POSTS[tag]
    with P.frame(None, f"{tag}_"):
        footing(a, x, y)
        post(a, x, y, top)
        lashing(a, tag, x, y)
        if tag == "FR":
            lashing(a, "FRb", x, y)


def hero_all(a):
    for tag in POSTS:
        post_all(a, tag)
    ridge(a)
    canopy(a)
    banner(a)
    P.GEO["glass"] = list(lantern(a))
    table(a)
    for tag, ((bx, by), L) in BENCHES.items():
        with P.frame(None, f"bench_{tag}_"):
            bench(a, bx, by, L)
    crate(a)
    barrel(a)


def post_part(a):
    """The reusable tall post (12.0) with its canvas lashing, without the footing (CanvasShelterFooting)."""
    post(a, 0.0, 0.0, 12.0)
    lashing(a, "post", 0.0, 0.0, LASH["FR"])


PARTS = ((POST_P, post_part), (FOOT_P, lambda a: footing(a, 0.0, 0.0)), (RIDGE_P, ridge), (CANOPY_P, canopy),
         (BANNER_P, banner), (LANTERN_P, lambda a: lantern(a, with_bracket=False)),
         (TABLE_P, lambda a: table(a, 0.0, 0.0)), (BENCH_P, lambda a: bench(a, 0.0, 0.0, BENCHES["back"][1])),
         (STOOL_P, stool), (CRATE_P, lambda a: crate(a, (0.0, 0.0))), (BARREL_P, lambda a: barrel(a, (0.0, 0.0))))


def seat_points():
    out = {}
    for tag, ((bx, by), L) in BENCHES.items():
        face = (0, -1, 0) if by > 0 else (0, 1, 0)
        for i, dx in enumerate((-L / 4, L / 4)):
            out[f"m066_seat_{tag}{i + 1}"] = ((bx + dx, by, SEAT_Z), face)
    return out


def glass_point():
    rt = ARM_Z - 0.30
    return (LANT_XY[0], LANT_XY[1], rt - lantern_height() + LANT["plate"] + LANT["gh"] / 2)


POINTS = {HERO: dict(seat_points(), m066_lantern=(glass_point(), (0, -1, 0))),
          BENCH_P: {"m066_seat_1": ((-1.6, 0.0, SEAT_Z), (0, 1, 0)), "m066_seat_2": ((1.6, 0.0, SEAT_Z), (0, 1, 0))},
          STOOL_P: {"m066_seat": ((0.0, 0.0, SEAT_Z), (0, 1, 0))},
          RIDGE_P: {"m066_end_front": (((BEAM_X[0] + BEAM_X[1]) / 2, BEAM_Y[0], BEAM_Z[0]), (0, -1, 0))}}
FX = {HERO: [("heat_glow", glass_point(), {})],
      LANTERN_P: [("heat_glow", (LANT_XY[0], LANT_XY[1], ARM_Z - 0.30 - lantern_height() + LANT["plate"] +
                                 LANT["gh"] / 2), {})]}
NOTES = {
    HERO: "Canvas shelter (sheet 066, remade): four 1.3 square timber posts on tapered stone footings (2.1 base, 1.30 "
          "high; post tops 12.0 for the right pair, 10.4 for the left; centres 14.0 x 10.4), a 0.8 ridge beam lashed "
          "level along the tall posts' inner faces, one cream canvas (closed 0.10 slab) tied into gold X-lashings at "
          "the four corners, the back-right corner up under the beam, lowest underside >= 6.9 (walk under); a red "
          "three-tailed banner with a white diamond and arrow bar, hung by red bands from a rod lashed to the "
          "front-left post; a square lantern with Neon glass on an iron bracket under the front-right corner "
          "(heat_glow); a plank table (top 2.60) with a paper and two bottles, two benches (seats 1.50), a closed "
          "X-braced crate and a lidded barrel. Seat and lantern points stored.",
    POST_P: "Post: the 1.3 square chamfered timber post, 10.72 long (its top at 12.0 on the 1.30 footing), with its "
            "gold X-lashing; the short posts are 1.6 shorter (cut in Studio or rebuild)",
    FOOT_P: "Footing: the tapered stone footing (2.1 base, 1.64 top, 1.30 high) a post stands on",
    RIDGE_P: "Ridge Beam: the 0.8 square timber beam, 12.6 long",
    CANOPY_P: "Canvas Canopy: the sagging canvas sheet with its corners tied (one corner high)",
    BANNER_P: "Banner & Rod: the rod, two red bands and the three-tailed red banner with the white diamond and arrow "
              "bar on both faces",
    LANTERN_P: "Lantern: square dark frame, Neon glass, ring top; heat_glow socket",
    TABLE_P: "Table: three-plank top (7.0 x 3.0, top 2.60) on cleats and four legs, with a paper and two bottles",
    BENCH_P: "Bench: two-plank seat (6.4 x 1.3, seat 1.50) on cleats and four legs; two seat points",
    STOOL_P: "Stool: two-plank seat (1.4 x 1.3, seat 1.50) on four legs; one seat point",
    CRATE_P: "Crate: closed X-braced crate, 2.30 cube, a light frame and proud braces over darker panels",
    BARREL_P: "Barrel: lidded hooped barrel, 2.72 tall",
}
COLLISION = {HERO: "precise", POST_P: "hull", FOOT_P: "box", RIDGE_P: "box", CANOPY_P: "none", BANNER_P: "none",
             LANTERN_P: "none", TABLE_P: "box", BENCH_P: "box", STOOL_P: "box", CRATE_P: "box", BARREL_P: "hull"}
BUDGETS = {HERO: 6000}
TARGET_SIZE = ((17.60, 0.05), (12.90, 0.05), (12.0, 0.01))
VIEWS = {"f34_sheet": (-30, 20), "r34_sheet": (-22, 24), "front_sheet": (0, 0), "side_sheet": (90, 0),
         "rear_sheet": (180, 0), "top_sheet": (0, 89.9)}
EXPLODED = {POST_P: [(-8.5, -6.5, 1.6), (-8.5, 6.5, 1.6), (8.5, -6.5, 1.6), (8.5, 6.5, 1.6)],
            FOOT_P: [(-8.5, -6.5, 0.0), (-8.5, 6.5, 0.0), (8.5, -6.5, 0.0), (8.5, 6.5, 0.0)],
            RIDGE_P: (5.5, 0.0, 15.5), CANOPY_P: (0.0, 0.0, 12.0), BANNER_P: (-12.5, -7.5, 2.0),
            LANTERN_P: (12.0, -7.5, 5.0), TABLE_P: (0.0, 0.0, 0.0), BENCH_P: (1.0, -4.0, 0.0),
            STOOL_P: (4.5, -7.0, 0.0), CRATE_P: (12.0, 0.0, 0.0), BARREL_P: (-12.0, 2.0, 0.0)}
CLOSE = {"lash_cu": dict(at=(-PX, -PY, 8.7), r=1.6, az=-35, el=12),
         "foot_cu": dict(at=(-PX, -PY, 0.8), r=1.6, az=-35, el=15),
         "fr_cu": dict(at=(PX - 0.6, -PY, 8.6), r=2.4, az=-30, el=10),
         "under_cu": dict(cam=(-4.3, -3.5, 1.5), look=(1.0, 1.0, 8.5), lens=14.0)}
WALK = {"paths": [[(-4.83, -10.0), (-4.83, -0.5)], [(-11.0, -0.8), (-4.5, -0.8)], [(4.45, 11.0), (4.45, 1.5)],
                  [(11.0, 2.4), (3.9, 2.4)]],
        "ride": False, "turn": [(-5.2, -0.8, 0.0)]}
VERIFY = dict(cls="structure", walk=WALK, sockets={HERO: ["heat_glow"], LANTERN_P: ["heat_glow"]},
              stored={HERO: ["m066_centre", "m066_lantern", "m066_seat_back1", "m066_seat_front1"],
                      BENCH_P: ["m066_seat_1", "m066_seat_2"], STOOL_P: ["m066_seat"]})
COMPARE = {"f34": {"box": (95, 125, 525, 482), "view": (-30, 20)},
           "r34": {"box": (565, 62, 1010, 470), "view": (-22, 24)},
           "front": {"box": (16, 530, 268, 705), "view": (0, 0)},
           "side": {"box": (274, 530, 455, 705), "view": (90, 0)},
           "rear": {"box": (524, 530, 772, 705), "view": (180, 0)},
           "top": {"box": (776, 530, 1010, 705), "view": (0, 89.9)}}


def shelter_check(objs):
    """Spec "Brief": the canvas underside at least HEADROOM over the floor; the table top at 2.60 and every bench
    seat at 1.50 (rays down)."""
    h = objs[HERO]
    me = h.data
    tree = BVHTree.FromPolygons([h.matrix_world @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])
    down = Vector((0, 0, -1))

    def z_at(x, y, top=9.0):
        hit = tree.ray_cast(MODEL.at(h, (x, y, top)), down)[0]
        return round(hit.z - h.matrix_world.translation.z + h[MODEL.OFF][2], 3) if hit else None
    can = P.GEO.get("canvas", {}).get("canvas", {})
    rep = {"canvas": can, "table_z": z_at(TABLE_C[0] - 2.0, TABLE_C[1] + 0.9, 2.9),
           "seats": {k: z_at(p[0] + 0.3, p[1] + 0.3, 2.0) for k, (p, _) in seat_points().items()}}
    pr = []
    if can and can.get("low_under", 0) < HEADROOM:
        pr.append(f"{HERO}: canvas underside {can['low_under']} under the {HEADROOM} headroom")
    if rep["table_z"] is None or abs(rep["table_z"] - TOP_Z) > 0.01:
        pr.append(f"{HERO}: table top {rep['table_z']} not {TOP_Z}")
    pr += [f"{HERO}: seat {k} at {z} not {SEAT_Z}" for k, z in rep["seats"].items()
           if z is None or abs(z - SEAT_Z) > 0.01]
    return rep, pr


def build(render=True, close=False, spin=False):
    def after(objs):
        h = objs[HERO]
        h["m066_centre"] = [round(x, 4) for x in -Vector(h[MODEL.OFF])]
    return MODEL.run(hero=(HERO, hero_all), parts=PARTS, notes=NOTES, collision=COLLISION, budgets=BUDGETS,
                     target_size=TARGET_SIZE, points=POINTS, fx=FX, views=VIEWS, exploded=EXPLODED,
                     scale=(-10.0, -6.5, 0.0), close=CLOSE if close else None, verify=VERIFY, checks=[shelter_check],
                     after=after, render=render, spin=spin)


def preview(names=("f34_sheet", "front_sheet", "side_sheet")):
    return MODEL.preview(HERO, VIEWS, names)


def compare(cells=None, out_dir=None):
    import importlib
    import compare as C
    importlib.reload(C)
    return C.compare(NUM, {k: COMPARE[k] for k in (cells or COMPARE)}, out_dir=out_dir)
