"""064 A-Frame Tent (references/064.png, remade 2026-11-03), on the shared library (kit_parts / kit_build): a walk-in
A-frame canvas tent with its camp dressing. Two X frames of crossed square timber poles (side by side, touching at the
crossing, both frames leaning out 4 deg), each crossing tied with a ridge lashing (three wraps round both poles and a
turn round each pole below them) and every pole with a two-turn rope band low down; a cream canvas of closed 0.10 slabs (the
two sagging side panels folded over the ridge as one chevron slab, a closed back, two front door flaps with turned-back
edges, the front gable open above a rolled door flap); a lantern hanging inside the doorway from the ridge; hem ties,
flap ties, four pegs; a teal mat, a bedroll and a plank chest inside; outside a braced crate, two banded barrels, a
ground lantern on a stake and two pale stones. See M064_spec.md.

    import importlib, kit_parts, kit_build, m064
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m064); m064.build()

Build frame (studs): front -Y (the doorway), +X right, ground z 0, the ridge along Y on x 0. Each end frame lies in a
plane leaning out L_DEG (top inward); in-plane coordinates (x, h) and the plane-normal offset w (outward +) place the
poles (fp), and y_at(end, z, w) gives a parallel plane's y at height z (canvas ends, roll, lashing gap). Names:
- CanvasTent (hero): everything above, one object of closed shells (no booleans). Collision precise.
- CanvasTentFrame (one X: two poles, ridge lashing, foot bands), CanvasTentPanel (one side panel), CanvasTentMat (mat
  and bedroll), CanvasTentCrate, CanvasTentBarrel, CanvasTentStone, CanvasTentPeg, CanvasTentLantern.
Colour is by role and position, never by facing. Stages 5-6: lantern glass m064_glow at emission 1.0 (Neon) and one
heat_glow socket per lantern.
"""
import math

from mathutils import Vector
from mathutils.bvhtree import BVHTree

import kit_build as B
import kit_parts as P

NUM, TITLE = 64, "A-Frame Tent"
HERO = "CanvasTent"
FRAME_P, PANEL_P, MAT_P = "CanvasTentFrame", "CanvasTentPanel", "CanvasTentMat"
CRATE_P, BARREL_P, STONE_P = "CanvasTentCrate", "CanvasTentBarrel", "CanvasTentStone"
PEG_P, LANTERN_P = "CanvasTentPeg", "CanvasTentLantern"

TIMBER, END_GRAIN, WOOD_DARK, WOOD_DEEP = "m064_timber", "m064_end_grain", "m064_wood_dark", "m064_wood_deep"
CANVAS, CANVAS_DEEP = "m064_canvas", "m064_canvas_deep"
ROPE, ROPE_DEEP = "m064_rope", "m064_rope_deep"
MAT, BEDROLL, METAL, GLOW = "m064_mat", "m064_bedroll", "m064_metal", "m064_glow"
STONE = "m064_stone"

# key -> (hex, roughness, metal, emission, low specular). Stage 4 (spec "Stage 4"): K.calibrate on the studio dome,
# then tuned on the f34 render against the same regions of the sheet's f34 (poles, rope, crate, barrel, mat, stone,
# glass, pegs within ~12 per channel). The canvas keeps the hue-correct cream of the M064 ruling (the dome wants salmon).
PALETTE = {
    TIMBER: ("#B1580A", 0.85, 0.0, 0.0, True),
    END_GRAIN: ("#C47A35", 0.85, 0.0, 0.0, True),
    WOOD_DARK: ("#7B481E", 0.85, 0.0, 0.0, True),
    WOOD_DEEP: ("#55301A", 0.9, 0.0, 0.0, True),
    CANVAS: ("#FDE4BC", 0.95, 0.0, 0.0, True),
    CANVAS_DEEP: ("#E6C8A2", 0.95, 0.0, 0.0, True),
    ROPE: ("#EBB24A", 0.95, 0.0, 0.0, True),
    ROPE_DEEP: ("#C58A34", 0.95, 0.0, 0.0, True),
    MAT: ("#457068", 0.95, 0.0, 0.0, True),
    BEDROLL: ("#9E784A", 0.95, 0.0, 0.0, True),
    METAL: ("#4A4D50", 0.55, 0.4, 0.0, False),
    GLOW: ("#F8B80A", 0.5, 0.0, 1.0, False),
    STONE: ("#908A8C", 0.92, 0.0, 0.0, True),
}
# calibration targets: the sheet's rendered medians (spec "Stage 4") and K.sample kinds ("all" = paper dropped)
TARGETS = {TIMBER: ((0xDA, 0x6A, 0x0E), "brown"), WOOD_DARK: ((0x8C, 0x4A, 0x1E), "brown"),
           CANVAS: ((0xFD, 0xE3, 0xBB), "all"), ROPE: ((0xE4, 0x90, 0x26), "brown"),
           MAT: ((0x4E, 0x7F, 0x6F), "all"), BEDROLL: ((0xC8, 0x8E, 0x4E), "brown"),
           METAL: ((0x50, 0x50, 0x4F), "all"), STONE: ((0xAB, 0xA5, 0xA7), "all")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)


def mix(k1, k2, t):
    return P.mix(k1, k2, t, step=0.05)


# ---- frame geometry (spec "Brief" / "Stage 1") ----------------------------------------------------------------------
L_DEG = 4.0                     # shared lean of the end frames and the canvas ends (hero view: a near prism)
SL, CL = math.sin(math.radians(L_DEG)), math.cos(math.radians(L_DEG))
YF0 = 5.64                      # the frame plane's |y| at z 0
ZC = 10.26                      # crossing height (frame plane)
XF = 6.66                       # pole axis feet x (front cell: 33 deg half angle)
KS = XF / ZC                    # pole and canvas slope dx / dz
HC = ZC / CL                    # in-plane crossing height
TIP_Z = 12.0                    # highest tip corner
PH, PCH = 0.45, 0.06            # pole half size, chamfer
PN = PH + 0.005                 # pole axis off the frame plane (0.01 between the two poles)
W_IN = -(PN + PH)               # the inner pole's inner face (-0.905)
GAP = 0.02                      # inner pole face to the canvas end outer face (the canvas end touches the poles)
WE = -W_IN + GAP                # canvas end outer face at w = -WE
CT = 0.10                       # canvas thickness
WCAP = -(WE - 0.005)            # roof slab end caps, 0.005 proud of the end pieces
ZR = 10.50                      # roof outer ridge
Z_HEM = 0.205                   # canvas hem (bottom of the slabs), 0.005 over the floor mat (MAT_T 0.20)
SQ = math.sqrt(1.0 + KS * KS)
XI = CT * SQ                    # inner surface inset (horizontal)
ZRI = ZR - XI / KS              # inner ridge
TUCK = 0.02                     # end pieces tuck into the roof slab (horizontal)
ROWS = (0.0, 0.25, 0.5, 0.75, 1.0)
COLS = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
SAG = 0.30                      # panel sag at the centre (inward)
X = Vector((1.0, 0.0, 0.0))
Z = Vector((0.0, 0.0, 1.0))
POLE_LINES = {}


def basis(end):
    """Frame origin at the ground, in-plane up U and outward normal N of end -1 (front) or +1 (back)."""
    return Vector((0.0, end * YF0, 0.0)), Vector((0.0, -end * SL, CL)), Vector((0.0, end * CL, SL))


def fp(end, x, h, w):
    O, U, N = basis(end)
    return O + X * x + U * h + N * w


def y_at(end, z, w):
    """y of the plane parallel to the frame (normal offset w, outward +) at height z."""
    return end * (YF0 - (z * SL - w) / CL)


def x_out(z):
    return KS * (ZR - z)


def x_in(z):
    return KS * (ZR - z) - XI


def x_t(z):
    return x_in(z) + TUCK


def cut(lines, c, m):
    """Where the lines (p0, d) cross the plane (c, normal m)."""
    return [p0 + d * ((c - p0).dot(m) / d.dot(m)) for p0, d in lines]


# ---- poles, lashing, bands -------------------------------------------------------------------------------------------
def pole_axis(end, which):
    """Pole A (outer, w +PN) runs from the -X foot to the +X tip, B (inner, w -PN) from the +X foot to the -X tip;
    both cross the frame's in-plane point (0, HC). Returns (foot on z 0, direction up, w, x sign of the foot)."""
    w = PN if which == "A" else -PN
    sx = -1 if which == "A" else 1
    foot = fp(end, sx * XF, -w * SL / CL, w)
    d = (fp(end, 0.0, HC, w) - foot).normalized()
    return foot, d, w, sx


def pole(a, end, which, name):
    """A square chamfered pole (8-sided, 0.9): a flat foot on z 0 and a square-cut tip (its highest corner at TIP_Z),
    lighter cut end grain on the tip."""
    foot, d, w, sx = pole_axis(end, which)
    _, U, N = basis(end)
    u = N.cross(d).normalized()
    offs = [u * su + N * sv for su, sv in P.sec_rect(PH, PH, PCH)]
    t_tip = (TIP_Z - max(o.z for o in offs)) / d.z
    ring0 = [foot + o + d * (-o.z / d.z) for o in offs]
    ring1 = [foot + o + d * t_tip for o in offs]
    POLE_LINES[(end, which)] = [(foot + o, d) for o in offs]
    return P.prism(a, [ring0, ring1], TIMBER, cap_keys=(TIMBER, END_GRAIN), name=name, kind="pole")


LASH_R = 0.14
LASH_DH = {"hi": 0.40, "lo1": -0.30, "lo2": -0.30 - (2 * LASH_R - 0.02)}
RING_DH = 0.75                  # the lower lobes' centres below the lowest wrap (in-plane)


def wrap(a, end, loop, r, up, name, kind):
    """A rope turn round the poles from a closed hull loop. The canvas end lies right behind the inner pole, so the
    run behind it is left out: the loop is cut where it crosses w = W_IN + r (each end beside the inner pole's side
    face, its cap flush with the pole's back face, the strands sunk P.SINK). A loop that never passes behind the
    inner pole stays closed."""
    O, _, N = basis(end)
    lim = W_IN + r
    w = [(p - O).dot(N) for p in loop]
    n = len(loop)
    if min(w) >= W_IN - 0.02:
        return P.rope(a, loop, r, ROPE, ROPE_DEEP, sides=5, closed=True, twist=True, up=up, name=name, kind=kind)
    k0 = next(i for i in range(n) if w[i] >= lim and w[(i - 1) % n] < lim)      # first point back in front
    path = []
    for j in range(n + 1):
        i, i1 = (k0 + j) % n, (k0 + j - 1) % n
        if w[i] >= lim and w[i1] < lim:                                     # entering: the crossing point
            t = (lim - w[i1]) / (w[i] - w[i1])
            path.append(loop[i1].lerp(loop[i], t))
        if j < n and w[i] >= lim:
            path.append(loop[i])
        if w[i] < lim and w[i1] >= lim:                                     # leaving: the crossing point
            t = (lim - w[i1]) / (w[i] - w[i1])
            path.append(loop[i1].lerp(loop[i], t))
            break
    path = [p for k, p in enumerate(path) if k == 0 or (p - path[k - 1]).length > 0.03]
    return P.rope(a, path, r, ROPE, ROPE_DEEP, sides=5, twist=True, up=up, name=name, kind=kind)


def lashing(a, end, tag):
    """The ridge lashing (sheet joint detail): a wrap round both tips above the crossing and two below it (twisted
    ropes hugging both poles' sections, open behind the inner pole where the canvas end lies), and below them a turn
    square round each pole, the figure-eight's two lobes."""
    _, U, N = basis(end)
    lines = POLE_LINES[(end, "A")] + POLE_LINES[(end, "B")]
    for k, dh in LASH_DH.items():
        c = fp(end, 0.0, HC + dh, 0.0)
        loop = P.hull_loop(cut(lines, c, U), c, U, X, LASH_R - P.SINK, 10)
        wrap(a, end, loop, LASH_R, U, f"{tag}lash_{k}", "rope_lash")
    for which in ("A", "B"):                             # the figure-eight's lower lobes: a turn square round
        foot, d, w, sx = pole_axis(end, which)           # each pole below the wraps (joint detail)
        c = foot + d * ((HC + LASH_DH["lo2"] - RING_DH - (-w * SL / CL)) / (d.dot(U)))
        loop = P.hull_loop(cut(POLE_LINES[(end, which)], c, d), c, d, N, LASH_R - P.SINK, 10)
        wrap(a, end, loop, LASH_R, d, f"{tag}lash_ring{which}", "rope_lash")


BAND_R, BAND_Z = 0.13, 1.70


def bands(a, end, which, tag):
    """Two rope turns square round the pole low down (the sheet's foot lashings), stacked along the pole, touching."""
    foot, d, w, sx = pole_axis(end, which)
    lines = POLE_LINES[(end, which)]
    c0 = foot + d * (BAND_Z / d.z)
    out = []
    for i in range(2):
        c = c0 + d * (i * (2 * BAND_R - 0.02))
        loop = P.hull_loop(cut(lines, c, d), c, d, Z.cross(d).normalized() if abs(d.z) < 0.99 else X,
                           BAND_R - P.SINK, 10)
        out.append(wrap(a, end, loop, BAND_R, d, f"{tag}band_{which}{i}", "rope_band"))
    return out


def frame(a, end, tag):
    for which in ("A", "B"):
        pole(a, end, which, f"{tag}pole_{which}")
    lashing(a, end, tag)
    for which in ("A", "B"):
        bands(a, end, which, tag)


# ---- canvas -----------------------------------------------------------------------------------------------------------
def roof(a, sides=(-1, 1), name="roof"):
    """Both side panels folded over the ridge as one closed 0.10 slab (or one panel with a ridge cap): a rows x columns
    grid from the ridge to the hem, the columns spread between the leaning end caps, sagging inward toward each
    panel's middle; quads split along the diagonal toward the panel centre (the X of creases); the hem row toward
    canvas_deep."""
    R, C = len(ROWS) - 1, len(COLS)
    pts, idx = [], {}

    def pt(s, t, u, inner):
        z = (ZRI - t * (ZRI - Z_HEM)) if inner else (ZR - t * (ZR - Z_HEM))
        x = s * (x_in(z) if inner else x_out(z))
        y0, y1 = y_at(-1, z, WCAP), y_at(1, z, WCAP)
        sg = SAG * math.sin(math.pi * t) * math.sin(math.pi * u)
        return Vector((x, y0 + (y1 - y0) * u, z)) - Vector((s / SQ, 0.0, KS / SQ)) * sg

    def key(s, i, j, inner):
        return ("r", j, inner) if i == 0 else (s, i, j, inner)
    for j, u in enumerate(COLS):
        for inner in (0, 1):
            idx[key(0, 0, j, inner)] = len(pts)
            pts.append(pt(1, 0.0, u, inner))
        for s in sides:
            for i in range(1, R + 1):
                for inner in (0, 1):
                    idx[key(s, i, j, inner)] = len(pts)
                    pts.append(pt(s, ROWS[i], u, inner))
    faces, keys = [], []
    hem_k = mix(CANVAS, CANVAS_DEEP, 0.35)
    ci, cj = R / 2, (C - 1) / 2
    for s in sides:
        for i in range(R):
            for j in range(C - 1):
                q = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
                tri = [(0, 1, 2), (0, 2, 3)] if (i + 0.5 < ci) == (j + 0.5 < cj) else [(0, 1, 3), (1, 2, 3)]
                k = hem_k if i == R - 1 else None
                for t in tri:
                    o = [idx[key(s, *q[n], 0)] for n in t]
                    faces += [o, [idx[key(s, *q[n], 1)] for n in reversed(t)]]
                    keys += [k, k]
        for j in range(C - 1):
            faces.append([idx[key(s, R, j, 0)], idx[key(s, R, j + 1, 0)], idx[key(s, R, j + 1, 1)],
                          idx[key(s, R, j, 1)]])
            keys.append(mix(CANVAS, CANVAS_DEEP, 0.6))
        for j in (0, C - 1):
            for i in range(R):
                faces.append([idx[key(s, i, j, 0)], idx[key(s, i + 1, j, 0)], idx[key(s, i + 1, j, 1)],
                              idx[key(s, i, j, 1)]])
                keys.append(hem_k if i == R - 1 else None)
    if len(sides) == 1:
        for j in range(C - 1):
            faces.append([idx[key(0, 0, j, 0)], idx[key(0, 0, j + 1, 0)], idx[key(0, 0, j + 1, 1)],
                          idx[key(0, 0, j, 1)]])
            keys.append(None)
    p = P.shell(a, pts, faces, CANVAS, keys=keys, name=name, kind="canvas", amp=0.02)
    P.texture(a, p.vs, 0.03, P.seed(name), scale=0.18)
    return p


def end_sheet(a, end, pts2d, tris, n_out, keys, name, sink=None):
    """A closed canvas slab in the end plane: 2D (x, z) points (the first n_out the outline, in order), outer face
    at w = -WE, inner face CT further in; point i pushed inward sink[i]; rim quads round the outline."""
    sink = sink or {}
    n = len(pts2d)

    def p3(i, w):
        x, z = pts2d[i]
        return Vector((x, y_at(end, z, w) - end * sink.get(i, 0.0), z))
    pts = [p3(i, -WE) for i in range(n)] + [p3(i, -WE - CT) for i in range(n)]
    faces, fk = [], []
    for t, k in zip(tris, keys):
        faces += [list(t), [n + v for v in reversed(t)]]
        fk += [k, k]
    rim = mix(CANVAS, CANVAS_DEEP, 0.5)
    for i in range(n_out):
        i1 = (i + 1) % n_out
        faces.append([i, i1, n + i1, n + i])
        fk.append(rim)
    p = P.shell(a, pts, faces, CANVAS, keys=fk, name=name, kind="canvas", amp=0.02)
    P.texture(a, p.vs, 0.03, P.seed(name), scale=0.18)
    return p


Z_AP = ZR - (XI - TUCK) / KS          # where the end pieces' sloped edges meet


def back_piece(a):
    """The closed back: a triangle tucked into the roof, its centre sunk 0.12 (a gentle sag), the hem band deeper."""
    xh = x_t(Z_HEM)
    zm = (Z_HEM + Z_AP) / 2
    pts = [(-xh, Z_HEM), (0.0, Z_HEM), (xh, Z_HEM), (x_t(zm), zm), (0.0, Z_AP), (-x_t(zm), zm),
           (0.0, Z_HEM + 0.38 * (Z_AP - Z_HEM))]
    tris = [(i, (i + 1) % 6, 6) for i in range(6)]
    hk = mix(CANVAS, CANVAS_DEEP, 0.25)
    keys = [hk, hk, None, None, None, None]
    return end_sheet(a, 1, pts, tris, 6, keys, "back", sink={6: 0.12})


D_TOP, D_BOT = 6.95, 3.30             # the flaps end at z D_TOP; door half width at the hem
STRIP = 0.40                          # the turned-back strip along each door edge (at the hem)


def x_d(z):
    """Door edge (half width): D_BOT at the hem to x_t(D_TOP) at D_TOP."""
    t = (z - Z_HEM) / (D_TOP - Z_HEM)
    return D_BOT + (x_t(D_TOP) - D_BOT) * t


def flap(a, s):
    """A front door flap: from the hem corner up the roof line to D_TOP, down the door edge; the strip along the door
    edge is the turned-back canvas (lighter, by position)."""
    pts = [(s * x_t(Z_HEM), Z_HEM), (s * x_t(D_TOP), D_TOP), (s * D_BOT, Z_HEM), (s * (D_BOT + STRIP), Z_HEM)]
    tris = [(0, 3, 1), (3, 2, 1)]
    keys = [mix(CANVAS, CANVAS_DEEP, 0.2), None]
    return end_sheet(a, -1, pts, tris, 4, keys, f"flap{s:+d}")


ROLL_R, ROLL_Z, ROLL_W = 0.38, 7.40, W_IN - 0.42     # its outer side 0.04 behind the inner pole


def roll(a, roof_piece):
    """The rolled door flap across the top of the doorway: a 10-sided log whose upper end corners stop 0.008 short of
    the roof's (sagging) inner surface, measured by rays along X; a darker rolled core proud of each end; two rope
    bands."""
    zt = ROLL_Z + ROLL_R
    y = y_at(-1, ROLL_Z, ROLL_W)
    tree = P.tree_of(roof_piece)
    reach = []
    for dy in (-ROLL_R, -0.12, 0.0, 0.12, ROLL_R):
        for dz in (0.0, -0.12):
            h = tree.ray_cast(Vector((0.0, y + dy, zt + dz)), X, 9.0)
            if h[0] is not None:
                reach.append(h[0].x)
    LR = min(reach) - 0.008
    P.log(a, (-LR, y, ROLL_Z), (LR, y, ROLL_Z), ROLL_R, CANVAS, sides=10, end_key=mix(CANVAS, CANVAS_DEEP, 0.4),
          name="roll", kind="roll")
    for s in (-1, 1):
        x0 = s * (LR - 0.01)
        P.log(a, (x0, y, ROLL_Z), (x0 + s * 0.03, y, ROLL_Z), 0.20, CANVAS_DEEP, sides=8, name=f"roll_core{s:+d}",
              kind="roll")
        c = Vector((s * 0.62, y, ROLL_Z))
        ring = P.ngon(c, Vector((0, 1, 0)), Z, ROLL_R / math.cos(math.pi / 10) + 0.07 - P.SINK, 8, math.pi / 8)
        P.rope(a, ring, 0.08, ROPE, ROPE_DEEP, sides=4, closed=True, twist=True, up=X, name=f"roll_band{s:+d}",
               kind="rope_band")
    P.GEO["roll"] = {"underside": round(ROLL_Z - ROLL_R, 3), "length": round(2 * LR, 3)}


def canvas_all(a):
    rp = roof(a)
    back_piece(a)
    for s in (-1, 1):
        flap(a, s)
    roll(a, rp)
    return rp


# ---- rope ties ----------------------------------------------------------------------------------------------------------
HEM_TIES = (-2.0, 1.6)


def hem_tie(a, s, y, name, tree):
    """A rope loop standing out of the hem's outer face (the sheet's hem ties): both ends on the (sagging) canvas,
    found by rays in along the panel normal."""
    r = 0.09
    n = Vector((s / SQ, 0.0, KS / SQ))
    pts = []
    for z, out in ((Z_HEM + 0.78, 0.0), (Z_HEM + 0.70, 0.20), (Z_HEM + 0.46, 0.30), (Z_HEM + 0.22, 0.20),
                   (Z_HEM + 0.14, 0.0)):
        p0 = Vector((s * x_out(z), y, z)) + n * 1.0
        h = tree.ray_cast(p0, -n, 3.0)[0]
        pts.append((h if h is not None else p0 - n) + n * (r - P.SINK + out))
    return P.rope(a, pts, r, ROPE, ROPE_DEEP, sides=4, name=name, kind="rope_tie")


def flap_tie(a, s):
    """A short tie from the flap's door corner down to the ground (the sheet's toggles)."""
    r = 0.07
    x = s * (D_BOT + 0.15)
    y0 = y_at(-1, Z_HEM + 0.15, -WE)
    return P.rope(a, [Vector((x, y0 - (r - P.SINK), Z_HEM + 0.15)), Vector((x, y0 - 0.25, r))], r, ROPE, ROPE_DEEP,
                  sides=4, name=f"flap_tie{s:+d}", kind="rope_tie")


def ties(a, roof_piece):
    tree = P.tree_of(roof_piece)
    for s in (-1, 1):
        for y in HEM_TIES:
            hem_tie(a, s, y, f"hem_tie{s:+d}{y:+.1f}", tree)
        flap_tie(a, s)


# ---- lanterns -----------------------------------------------------------------------------------------------------------
LANT = dict(w=1.05, plate=0.12, gw=0.78, gh=0.95, band=0.12, roof=0.30, fin=0.12, bar=0.12)
LANT_H = LANT["plate"] + LANT["gh"] + LANT["band"] + LANT["roof"] + LANT["fin"] + 0.51     # to the ring top
RING_TOP, LANT_Y = 9.78, -1.95          # the hanging lantern's ring top and axis: inside the gable, just behind the
                                        # roll, under the ridge (its bottom 7.66, over the 6.9 headroom)


def hang_point():
    """Where the hanger meets the canvas: the inner ridge over the lantern, sunk 0.07 into the fold."""
    return Vector((0.0, LANT_Y, ZRI - 0.07))


def lantern_base():
    return Vector((0.0, LANT_Y, RING_TOP - LANT_H))



def hanging_lantern(a, base, hanger=True):
    out = P.lantern(a, base, METAL, GLOW, ring_axis=(1, 0, 0), name="lantern", **LANT)
    if hanger:                          # a short rope from the ring up to the ridge (the sheet's hook)
        top = out["ring_top"]
        P.rope(a, [top - Vector((0, 0, 0.01)), hang_point()], 0.05, ROPE, ROPE_DEEP, sides=4, name="hanger",
               kind="rope")
    return out


GLAMP = ((-7.30, -4.40), 20.0)


def ground_lantern(a):
    """The lantern on a stake beside barrel A, with a bail handle."""
    (x, y), rot = GLAMP
    P.post(a, (x, y), 0.0, 1.0, 0.17, WOOD_DARK, ch=0.03, top_key=WOOD_DEEP, rot=rot, name="glamp_stake", kind="stake")
    return P.lantern(a, (x, y, 1.003), METAL, GLOW, rot=rot, ring_axis=(1, 0, 0), name="glamp", **LANT)


# ---- interior ---------------------------------------------------------------------------------------------------------------
MAT_T = 0.20
MAT_X = x_out(Z_HEM) + 0.08             # the floor mat runs under the hems (sheet floor plan: the whole floor)
MAT_Y = y_at(1, MAT_T, -WE) + 0.01          # and 0.01 past the end pieces' outer faces (short of the poles)
BED_X, BED_Y, BED_R = -0.90, (-2.60, 0.90), 0.55
CHEST = dict(x=2.0, y=(2.75, 3.90), z=1.55)


def mat(a):
    """The teal floor mat (the whole floor, under the hems and end pieces: the sheet's "Walkable Floor") and the
    bedroll lying along Y on the -X half: tan with a teal band, a darker rolled core proud of its front end."""
    zc = MAT_T / 2
    m = P.plank(a, (0.0, -MAT_Y, zc), (0.0, MAT_Y, zc), 2 * MAT_X, MAT_T, MAT, ch=0.0, name="mat", kind="mat",
                amp=0.02)
    P.texture(a, m.vs, 0.03, 64, scale=0.25)
    zb = MAT_T + BED_R - 0.01
    L = BED_Y[1] - BED_Y[0]
    st = (0.30 * L, 0.62 * L)
    teal = mix(MAT, BEDROLL, 0.15)
    P.log(a, (BED_X, BED_Y[0], zb), (BED_X, BED_Y[1], zb), BED_R, BEDROLL, sides=10, stations=st,
          end_key=mix(BEDROLL, WOOD_DARK, 0.25), band_keys=[None, teal, None], name="bedroll", kind="bedroll")
    P.log(a, (BED_X, BED_Y[0] + 0.01, zb), (BED_X, BED_Y[0] - 0.03, zb), 0.30, mix(BEDROLL, WOOD_DARK, 0.45), sides=8,
          name="bedroll_core", kind="bedroll")


def chest(a):
    """The plank chest at the back inside (front cell, exploded): a body on the mat, a lid 0.06 proud all round and
    two battens on its front."""
    x, (y0, y1), zt = CHEST["x"], CHEST["y"], CHEST["z"]
    P.box(a, (-x, y0, MAT_T - 0.01), (x, y1, zt), WOOD_DARK, name="chest", kind="chest")
    P.box(a, (-x - 0.06, y0 - 0.06, zt - 0.01), (x + 0.06, y1 + 0.06, zt + 0.14), mix(WOOD_DARK, TIMBER, 0.3),
          name="chest_lid", kind="chest")
    for k, zc in enumerate((0.62, 1.10)):
        P.box(a, (-x + 0.08, y0 - 0.05, zc - 0.1), (x - 0.08, y0 + 0.01, zc + 0.1), mix(WOOD_DARK, WOOD_DEEP, 0.3),
              name=f"chest_batten{k}", kind="chest")


# ---- dressing ---------------------------------------------------------------------------------------------------------------
CRATE = ((-9.60, 3.60), 12.0)
BARRELS = {"A": ((-8.40, -1.60), 0.0), "B": ((8.40, -4.40), 15.0)}
STONES = {"S1": ((-8.30, 1.20), (1.15, 1.05, 0.95), 20.0), "S2": ((-8.30, -6.00), (1.05, 1.0, 0.90), 38.0)}
PEGS = {"fl": ((-5.0, -7.1), 8.0), "fr": ((5.0, -7.1), -6.0), "bl": ((-5.0, 7.1), 4.0), "br": ((5.0, 7.1), -10.0)}


def crate(a, c=(0.0, 0.0), rot=0.0):
    """The braced storage crate (closed lid) with iron bolts at the frame corners of every side."""
    out = P.crate(a, c, WOOD_DARK, WOOD_DEEP, rot=rot, W=2.30, H=2.20, open_top=False, frame_t=(0.1, 0.25),
                  name="crate")
    P.paint(a, [out[0].fs[0]], mix(WOOD_DARK, WOOD_DEEP, 0.3))          # the base like the frame, not a dark shade
    for f in out[0].fs:                                 # one Tint on the body (per-face random tints read as facing)
        for lp in f.loops:
            lp[a.tint_layer] = (1.0, 1.0, 1.0, 1.0)
    Rm = P.R(c, rot)
    R3 = Rm.to_3x3()
    h, fw = 2.30 / 2, 0.13
    for k, (nrm, u) in enumerate((((0, -1, 0), (1, 0, 0)), ((1, 0, 0), (0, 1, 0)), ((0, 1, 0), (-1, 0, 0)),
                                  ((-1, 0, 0), (0, -1, 0)))):
        n, uu = Vector(nrm), Vector(u)
        for su in (-1, 1):
            for z in (fw, 2.20 - fw):
                p = n * h + uu * (su * (h - fw)) + Z * z
                P.bolt(a, Rm @ p, R3 @ n, Z, METAL, h=0.07, proud=0.04, name=f"crate_bolt{k}{su:+d}{z:.1f}")
    return out


def barrel(a, c=(0.0, 0.0), rot=0.0, name="barrel"):
    """A lidded barrel, ten staves and two iron hoops; one wood colour all over (the per-stave Tint varies), so no
    shade follows the face direction."""
    return P.barrel(a, c, WOOD_DARK, WOOD_DARK, METAL, rot=rot, n=10, open_top=False, lid_key=WOOD_DARK, name=name)


def stone(a, c, size, rot, name, seed_=641):
    return P.stone(a, c, size, STONE, rot=rot, seed_=seed_, name=name)


def peg(a, c=(0.0, 0.0), rot=0.0, name="peg"):
    """A square stake (0.6) with a lighter cut top and a rope-tan collar band near the top (sheet "Peg (x4)")."""
    P.post(a, c, 0.0, 1.30, 0.30, TIMBER, ch=0.05, top_key=END_GRAIN, rot=rot, name=name, kind="peg")
    zc = 0.95
    m = P.R(c, rot).to_3x3()
    sec = [Vector((c[0], c[1], zc)) + m @ Vector((u, v, 0.0)) for u, v in P.sec_rect(0.30, 0.30, 0.05)]
    return P.strap(a, sec, (c[0], c[1], zc), Z, 0.22, 0.07, ROPE, name=name + "_collar", kind="rope_band")


def dressing(a):
    crate(a, *CRATE)
    for tag, (c, rot) in BARRELS.items():
        barrel(a, c, rot, f"barrel{tag}")
    for k, (tag, (c, size, rot)) in enumerate(STONES.items()):
        stone(a, c, size, rot, f"stone{tag}", 641 + k)
    for tag, (c, rot) in PEGS.items():
        peg(a, c, rot, f"peg_{tag}")
    ground_lantern(a)


# ---- assemblies ------------------------------------------------------------------------------------------------------
def hero_all(a):
    for end, tg in ((-1, "front_"), (1, "back_")):
        frame(a, end, tg)
    ties(a, canvas_all(a))
    hanging_lantern(a, lantern_base())
    mat(a)
    chest(a)
    dressing(a)


def frame_part(a):
    frame(a, -1, "")


PARTS = ((FRAME_P, frame_part), (PANEL_P, lambda a: roof(a, sides=(1,), name="panel")), (MAT_P, mat),
         (CRATE_P, lambda a: crate(a)), (BARREL_P, lambda a: barrel(a)),
         (STONE_P, lambda a: stone(a, (0.0, 0.0), STONES["S1"][1], 0.0, "stone")), (PEG_P, lambda a: peg(a)),
         (LANTERN_P, lambda a: hanging_lantern(a, (0.0, 0.0, 0.0), hanger=False)))


def lantern_glass(base):
    return Vector(base) + Vector((0.0, 0.0, LANT["plate"] + LANT["gh"] / 2))


def fx_spec(rng):
    """heat_glow overridden to a steady warm lantern halo (M064 decision 13, as M068)."""
    return {"emitters": [{"name": "Halo", "texture": "glow_soft", "color": ["#FFC23A", "#FF9A1E"], "size": [1.4, 1.7],
                          "transparency": [0.65, 1.0], "lifetime": [1.0, 1.5], "rate": 2, "speed": [0, 0.05],
                          "spread": 0, "light_emission": 1.0}],
            "light": {"color": "#FFB347", "brightness": 1.0, "range": rng, "flicker": True}}


FX = {HERO: [("heat_glow", lantern_glass(lantern_base()), fx_spec(12)),
             ("heat_glow", lantern_glass((GLAMP[0][0], GLAMP[0][1], 1.003)), fx_spec(8))],
      LANTERN_P: [("heat_glow", lantern_glass((0.0, 0.0, 0.0)), fx_spec(12))]}
POINTS = {HERO: {"m064_door": (0.0, y_at(-1, 0.0, -WE), 0.0), "m064_inside": (0.0, 0.0, MAT_T)}}
NOTES = {
    HERO: "Walk-in A-frame canvas tent (remade sheet): two X frames of 0.9 square poles (tips 12.0, crossing 10.26, "
          "leaning out 4 deg) with ridge lashings and foot bands; a cream canvas of closed 0.10 slabs (sagging side "
          "panels folded over the ridge, closed back, two front door flaps with turned-back edges, open gable above a "
          "rolled door flap); a Neon lantern hanging inside the doorway from the ridge; hem and flap ties; teal mat, "
          "bedroll and a plank chest inside; a braced crate, two barrels, a ground lantern on a stake, two stones and "
          "four pegs outside. Doorway 3.6 clear to 7.0 (roll underside 7.02, lantern 7.76); collision precise, "
          "walk-in Requires Manual Validation.",
    FRAME_P: "A-Frame Pole: one X of two 0.9 square poles side by side, ridge lashing (three wraps, two diagonals), a "
             "two-turn rope band low on each pole",
    PANEL_P: "Canvas Panel: one sagging side panel slab (0.10), ridge cut square",
    MAT_P: "Tent Mat (Rolled + Flat): the flat teal mat and the tan bedroll with its teal band",
    CRATE_P: "Storage Crate: braced crate with a closed lid and iron bolts",
    BARREL_P: "Barrel: ten staves, two iron hoops, lidded",
    STONE_P: "Stone: a pale chamfered block",
    PEG_P: "Peg: square stake with a rope collar",
    LANTERN_P: "Lantern: dark-metal lantern, Neon amber glass, hanging ring (heat_glow halo)",
}
COLLISION = {HERO: "precise", FRAME_P: "hull", PANEL_P: "hull", MAT_P: "none", CRATE_P: "box", BARREL_P: "hull",
             STONE_P: "hull", PEG_P: "none", LANTERN_P: "none"}
BUDGETS = {HERO: 6000}
TARGET_SIZE = ((20.5, 0.3), (15.0, 0.3), (12.0, 0.02))
VIEWS = {"f34_sheet": (-42, 25), "r34_sheet": (-138, 25), "front_sheet": (0, 0), "side_sheet": (-22, 6),
         "rear_sheet": (90, 0), "top_sheet": (0, 89.9)}
EXPLODED = {FRAME_P: [(-12.0, 0.0, 0.0), (12.0, 0.0, 0.0)], PANEL_P: [(-4.0, 0.0, 1.0)], MAT_P: (2.0, -7.0, 0.0),
            CRATE_P: (-7.0, -9.0, 0.0), BARREL_P: (8.0, -8.0, 0.0), STONE_P: [(-1.5, -11.0, 0.0), (1.0, -11.5, 0.0)],
            PEG_P: [(-11.0, -9.0, 0.0), (11.0, -10.0, 0.0)], LANTERN_P: (0.0, -2.0, 9.0)}
COMPARE = {"f34": {"box": (16, 104, 510, 452), "view": (-42, 25)},
           "r34": {"box": (516, 104, 1008, 452), "view": (-138, 25)},
           "front": {"box": (16, 526, 262, 718), "view": (0, 0)},
           "side": {"box": (268, 526, 545, 718), "view": (-22, 6)},
           "rear": {"box": (548, 526, 780, 718), "view": (90, 0)},
           "top": {"box": (786, 526, 1008, 718), "view": (0, 89.9)}}
CLOSE = {"lash_cu": dict(at=(0.0, -3.9, 10.2), r=1.3, az=-25, el=10),
         "door_cu": dict(cam=(1.5, -12.0, 4.5), look=(0.0, -2.0, 4.5), lens=24.0),
         "inside_cu": dict(cam=(0.8, -2.5, 4.0), look=(-0.5, 3.5, 3.0), lens=14.0)}

ESC_Y = 2.30                                        # inside both end pieces up to the box top, and clear of the
                                                    # space under the pole tips (outside the canvas, roofed by poles)
ESC_BOX = ((-6.0, -ESC_Y, 0.3), (6.0, ESC_Y, 10.2))  # the inside over the mat (points outside the canvas are not
ESCAPE = {"box": ESC_BOX, "floor": False,           # enclosed, so they are skipped; x +-6.0 keeps the space under
          "allow": {"door": ((-6.05, -ESC_Y - 0.05, 0.25), (6.05, -ESC_Y + 0.05, 10.25)),   # the hem ties out); the
                    "gable": ((-6.05, -ESC_Y - 0.05, 10.15), (6.05, -1.0, 10.25)),          # mat is the floor. Allowed:
                    "door_floor": ((-6.05, -ESC_Y - 0.05, 0.25), (6.05, -1.5, 0.35))}}      # door, gable, sill rays
WALK = {"paths": [[(1.0, -9.5), (1.0, -4.0), (1.0, 1.8)], [(1.0, -9.5), (1.0, -3.0), (1.3, 1.0)]], "skip": ("mat",),
        "turn": [(1.4, -0.2, MAT_T)]}
VERIFY = dict(cls="structure", walk=WALK, escape=ESCAPE, stored=["m064_door", "m064_inside"],
              sockets={HERO: ["heat_glow", "heat_glow"], LANTERN_P: ["heat_glow"]})


DOOR_FULL = 6.5


def door_check(objs):
    """House rules: headroom >= 6.9 over the walk-in lane (rays up from the floor, x 0.45-1.55: the head over the walk path, door to mat centre);
    the doorway (rays along +Y from y -9 to the front canvas plane: nothing hit) clear 3.6 wide to DOOR_FULL (the
    poles converge above it, spec departure) and 2.0 wide (+-1.0) to 7.0."""
    h = objs[HERO]
    me = h.data
    tree = BVHTree.FromPolygons([h.matrix_world @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])
    z0 = h.matrix_world.translation.z - h[MODEL.OFF][2]
    head = 99.0
    for x in (0.45, 1.0, 1.55):
        y = -9.0
        while y <= 1.0:
            hit = tree.ray_cast(MODEL.at(h, (x, y, MAT_T + 0.02)), Z, 50.0)[0]
            if hit is not None:
                head = min(head, hit.z - z0)
            y += 0.25
    blocked = []
    probes = [(x, z) for x in (-1.8, -0.9, 0.0, 0.9, 1.8) for z in (0.5, 2.0, 4.0, 5.5, DOOR_FULL)]
    probes += [(x, 7.0) for x in (-1.0, 0.0, 1.0)]
    for x, zz in probes:
        dist = 9.0 - abs(y_at(-1, zz, -WE - CT))
        if tree.ray_cast(MODEL.at(h, (x, -9.0, zz)), Vector((0, 1, 0)), dist)[0] is not None:
            blocked.append((x, zz))
    rep = {"headroom_min": round(head, 3), "door_blocked": blocked}
    pr = []
    if head < 6.9:
        pr.append(f"{HERO}: headroom {head:.2f} over the walk-in line under 6.9")
    if blocked:
        pr.append(f"{HERO}: doorway blocked at {blocked[:6]}")
    return rep, pr


def build(render=True, close=False, spin=False):
    return MODEL.run(hero=(HERO, hero_all), parts=PARTS, notes=NOTES, collision=COLLISION, budgets=BUDGETS,
                     target_size=TARGET_SIZE, points=POINTS, fx=FX, views=VIEWS, exploded=EXPLODED,
                     scale=(3.5, -9.5, 0.0), close=CLOSE if close else None, verify=VERIFY, checks=[door_check],
                     render=render, spin=spin)


def preview(names=("f34_sheet", "front_sheet", "rear_sheet")):
    return MODEL.preview(HERO, VIEWS, names)


def compare(cells=None, out_dir=None):
    import importlib
    import compare as C
    importlib.reload(C)
    return C.compare(NUM, {k: COMPARE[k] for k in (cells or COMPARE)}, out_dir=out_dir)
