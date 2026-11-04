"""077 Hunt Workshop (references/077.png, remade sheet; no earlier builder) on the shared library (kit_parts /
kit_build): an open-front timber workshop under a four-sided cream canvas roof. See
art/blender/renders/models/M077/M077_spec.md.

    import importlib, kit_parts, kit_build, m077
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m077); m077.build()

Build frame (studs): front -Y (the open front with the workbench), +X right, ground z 0, the post rectangle centred
on x 0 / y 0 (post centres 13.0 x 11.2).
- Four 1.6-square posts on tapered stone footings; at each post top a wider joint collar (two round pin bolts on each
  outer face) and a narrower cap block standing on it. Four perimeter beams run between the collars (their tops just
  under the canvas rim); four crossed roof beams (rafters) run along the canvas hips from the cap blocks' inner
  corners up to a round hub under the canvas peak.
- The canvas roof: one closed slab, a sagging pyramid whose hips lie on the rafters and whose corners are notched
  round the cap blocks (the rim lies on the collars); a skirt panel hangs from each edge outside the perimeter beam
  (bottom >= 7.8, the walk-under headroom), three tattered flaps hang from the rear skirt; a two-block finial on the
  peak.
- Plank half walls (four rows between two end stiles) on the back and both sides; the front is open.
- A workbench across the front (top 2.60, three boards, breadboard ends, lower shelf, back board) with a tool press,
  a tray with a stone and a bowl, a whetstone and a hammer; the entry is the 2.5-wide gap between its right end and
  the front-right footing. A lantern hangs from an iron bracket off the front-left post over the gap at the bench's
  left end; the red diamond banner hangs from a rod under the rear beam.
- Crates: inside along the back wall (a crate with a green pack, a small chest, a crate); outside the left wall a
  crate with a grey banded box near the front and a crate with a green pack near the back; outside the right wall a
  crate with a green pack.
Every piece is its own closed shell (no booleans), seated 0.002-0.05 into what holds it.
Hero HuntWorkshop; parts HuntWorkshopPost, ...Footing, ...RoofBeam, ...RoofFrame, ...Canvas, ...HalfWall,
...Workbench, ...Crate, ...PackCrate, ...Lantern, ...Banner. Stage 5-6: Neon lantern glass with one heat_glow socket.
"""
import math

from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_build as B
import kit_parts as P

NUM, TITLE = 77, "Hunt Workshop"
HERO = "HuntWorkshop"
POST_P, FOOT_P, BEAM_P, FRAME_P = "HuntWorkshopPost", "HuntWorkshopFooting", "HuntWorkshopRoofBeam", \
    "HuntWorkshopRoofFrame"
CANVAS_P, WALL_P, BENCH_P = "HuntWorkshopCanvas", "HuntWorkshopHalfWall", "HuntWorkshopWorkbench"
CRATE_P, PACK_P, LANTERN_P, BANNER_P = "HuntWorkshopCrate", "HuntWorkshopPackCrate", "HuntWorkshopLantern", \
    "HuntWorkshopBanner"

TIMBER, TIMBER_L, TIMBER_D = "m077_timber", "m077_timber_light", "m077_timber_dark"
PLANK, ACCENT = "m077_plank", "m077_accent"
CANVAS, CANVAS_DEEP = "m077_canvas", "m077_canvas_deep"
STONE, STONE_DEEP = "m077_stone", "m077_stone_deep"
BANNER, BANNER_DEEP, CREAM = "m077_banner", "m077_banner_deep", "m077_cream"
PACK, PACK_DEEP, STRAP = "m077_pack", "m077_pack_deep", "m077_strap"
IRON, METAL, GLOW = "m077_iron", "m077_metal", "m077_glow"

# key -> (hex, roughness, metal, emission, low specular). Stage 4 (spec "Stage 4").
PALETTE = {
    TIMBER: ("#B0601E", 0.85, 0.0, 0.0, True),
    TIMBER_L: ("#C98E48", 0.85, 0.0, 0.0, True),
    TIMBER_D: ("#7A4116", 0.9, 0.0, 0.0, True),
    PLANK: ("#A85A1E", 0.85, 0.0, 0.0, True),
    ACCENT: ("#D8700E", 0.8, 0.0, 0.0, True),
    CANVAS: ("#D9C4A0", 0.95, 0.0, 0.0, True),
    CANVAS_DEEP: ("#A87A48", 0.95, 0.0, 0.0, True),
    STONE: ("#8E8E90", 0.92, 0.0, 0.0, True),
    STONE_DEEP: ("#6E6E72", 0.92, 0.0, 0.0, True),
    BANNER: ("#C42214", 0.9, 0.0, 0.0, True),
    BANNER_DEEP: ("#82140E", 0.9, 0.0, 0.0, True),
    CREAM: ("#E6D2AE", 0.9, 0.0, 0.0, True),
    PACK: ("#64773A", 0.9, 0.0, 0.0, True),
    PACK_DEEP: ("#4A5A2A", 0.9, 0.0, 0.0, True),
    STRAP: ("#6A3A16", 0.9, 0.0, 0.0, True),
    IRON: ("#3A3C45", 0.6, 0.35, 0.0, False),
    METAL: ("#6A6E78", 0.55, 0.4, 0.0, False),
    GLOW: ("#F9C83A", 0.5, 0.0, B.NEON, False),
}
# calibration targets: the sheet's rendered medians (spec "Stage 4") and K.sample kinds
TARGETS = {TIMBER: ((0xD6, 0x79, 0x2B), "brown"), PLANK: ((0xD1, 0x77, 0x2D), "brown"),
           TIMBER_L: ((0xCA, 0x88, 0x3D), "brown"), STONE: ((0xA7, 0xA8, 0xA7), "all"),
           BANNER: ((0xE2, 0x30, 0x18), "vivid"), PACK: ((0x8A, 0x9A, 0x4A), "green"),
           ACCENT: ((0xE8, 0x80, 0x18), "vivid")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)


def mix(k1, k2, t):
    return P.mix(k1, k2, t, step=0.05)


# ---- layout (spec "Brief": front cell 0.076 stud / sheet px vertically, posts widened to 13.0 for the entry) -------
PX, PY = 6.5, 5.6                        # post centres
PH, PCH = 0.80, 0.07                     # post half width, vertical edge chamfer
FOOT_H = 1.55                            # stone footing: tapered (2.30 base, 1.92 top), flat top
FOOT_RINGS = ((0.0, 1.15, 0.12), (1.05, 1.03, 0.11), (FOOT_H, 0.96, 0.09))     # (z, half, chamfer)
POST_Z0 = FOOT_H - 0.02
Z_C = 10.00                              # collar top (the canvas rim lies 0.003 over it)
COL_H, COL_HALF, COL_CH = 1.15, 0.975, 0.08
CAP_HALF, CAP_TOP, CAP_BEV = 0.68, 10.95, 0.08
PIN_R, PIN_OUT, PIN_U = 0.14, 0.12, 0.42  # pin bolts: flat radius, proud of the collar face, offset from the centre
BEAM_HW, BEAM_TOP, BEAM_D = 0.40, Z_C - 0.03, 0.75
CT = 0.10                                # canvas thickness (vertical)
Z_E = Z_C + 0.003 + CT                   # canvas top at the front / back rim
XE, YE = PX + 0.49, PY + 0.49            # canvas rim (the skirts' outer faces 0.007 inside)
XN, YN = PX - CAP_HALF - 0.003, PY - CAP_HALF - 0.003     # corner notch round the cap blocks
YH = YE                                  # hip rectangle: hips through the notch corners
XH = YH * XN / YN
S_STAR = YN / YH                         # the hips meet the notch corners at this s
S_IN = 0.10                              # flat peak (the finial's footprint)
Z_APEX = 13.45
RISE = Z_APEX - Z_E
SAG = 0.40                               # face sag between the hips
S_OUT = {"y": 1.0, "x": XE / XH}         # rim s of the front / back and side patches (the sides 0.11 higher)
RINGS = {"y": (S_IN, 0.35, 0.60, S_STAR, 1.0), "x": (S_IN, 0.35, 0.60, S_STAR, XE / XH)}
LAT = 3                                  # lateral points per half ring
SK_T = 0.08                              # skirt thickness
SK_BOT, SK_MID = 8.05, 7.92              # skirt bottom at the ends / middle (>= 7.8 headroom)
FLAPS = ((3.9, 1.30, 1.75), (0.8, 1.20, 1.85), (-2.9, 1.30, 1.70))   # rear flaps: centre x (build), width, length
FLAP_T = 0.05
FIN = dict(plate=0.60, plate_h=0.30, cube=0.45, cube_h=0.70)
HUB_R = 0.45
RAF_W = 0.50
# half walls
WALL_T, STILE_W, STILE_T = 0.30, 0.55, 0.42
WALL = {"B": (6.00, 5), "L": (4.45, 4), "R": (4.45, 4)}     # plank top, rows (the hero's back wall stands taller)
STILE_UP = 0.17                          # stiles stand this far over the planks
WALL_END = 1.17                          # wall ends this far inside the post centre lines (clear of the footings)
# workbench (HOUSE_RULES table top 2.60)
BENCH = dict(x0=-4.60, x1=2.90, y0=-PY + 0.40, D=2.80, top=2.60, tt=0.36, end=0.50, leg=0.55)
# lantern on a bracket off the front-left post's inner face, over the gap at the bench's left end
LANT_XY = (-4.55, -PY)
ARM_Z = 7.55
LANT = dict(w=1.10, plate=0.16, gw=0.80, gh=1.45, band=0.18, roof=0.30, fin=0.12, bar=0.14)
# banner on a rod under the rear beam, inside
BAN = dict(x0=3.50, x1=5.10, y=PY - 0.42, rod_x=(3.25, 5.20), rod_r=0.12, knob=0.15, tip=3.55, side=4.35, t=0.08)
# crates (HOUSE_RULES crate 2.30)
CRATE_W = 2.30
CRATES = {  # tag: (centre, rot, what's on it)
    "in_l": ((-4.10, 4.00), 0.0, "pack"),
    "in_r": ((3.40, 4.05), 0.0, None),
    "out_lf": ((-PX - 1.55, -PY + 2.65), 0.0, "box"),
    "out_lb": ((-PX - 1.55, PY - 2.55), 0.0, "pack"),
    "out_rb": ((PX + 1.55, PY - 2.55), 0.0, "pack"),
}
CHEST = dict(c=(-0.90, 4.60), L=1.70, D=1.05, H=1.05)
GAP = 0.04


# ---- small helpers ---------------------------------------------------------------------------------------------------
def flatten(a, faces, tol=1e-4):
    """(m068) Split warped quads into their two triangles, so each face is planar."""
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


def bx(a, lo, hi, key, name, kind, m=None, amp=0.04):
    """(m068) An axis box lo..hi with its corners sorted."""
    lo2 = tuple(min(p, q) for p, q in zip(lo, hi))
    hi2 = tuple(max(p, q) for p, q in zip(lo, hi))
    return P.box(a, lo2, hi2, key, m=m, name=name, kind=kind, amp=amp)


def cbox(a, c, hx, hy, z0, z1, key, name, kind, ch=0.05, rot=0.0, amp=0.04, top_key=None):
    """A box with its four vertical edges chamfered (8-sided section), centre c, turned rot deg about Z."""
    m = Matrix.Rotation(math.radians(rot), 3, "Z")
    sec = P.sec_rect(hx, hy, ch)
    rings = [[Vector((c[0], c[1], 0)) + m @ Vector((u, v, z)) for u, v in sec] for z in (z0, z1)]
    return P.prism(a, rings, key, cap_keys=(None, top_key), name=name, kind=kind, amp=amp)


# ---- frame timber ----------------------------------------------------------------------------------------------------
def footing(a, x, y, name="footing"):
    """(m066) The stone footing: a tapered square block, chamfered corners, flat top, its lower band deeper."""
    rings = [[(x + u, y + v, z) for u, v in P.sec_rect(h, h, ch)] for z, h, ch in FOOT_RINGS]
    p = P.prism(a, rings, STONE, band_keys=[mix(STONE, STONE_DEEP, 0.4), STONE], name=name, kind="stone")
    P.texture(a, p.vs, 0.04, P.seed(P.TAG[-1] + name), scale=0.6)
    return p


def post(a, x, y, name="post"):
    """The square post from the footing top up into the collar's underside (0.02)."""
    p = P.post(a, (x, y), POST_Z0, Z_C - COL_H + 0.02, PH, TIMBER, ch=PCH, name=name, kind="post")
    P.texture(a, p.vs, 0.025, P.seed(P.TAG[-1] + name), scale=0.35)
    return p


def collar(a, x, y, sx, sy, name="collar"):
    """The joint collar (sheet close-up "Post & Beam Joint"): a wider block round the post top, its top edge
    bevelled; two round pin bolts on each outer face (the -sx... faces pointing away from the middle)."""
    h, ch = COL_HALF, COL_CH
    z0 = Z_C - COL_H
    rings = [[(x + u, y + v, z) for u, v in P.sec_rect(h, h, ch)] for z in (z0, Z_C - 0.06)]
    rings.append([(x + u, y + v, Z_C) for u, v in P.sec_rect(h - 0.06, h - 0.06, ch * 0.6)])
    key = mix(TIMBER, ACCENT, 0.45)
    P.prism(a, rings, key, name=name, kind="collar")
    zc = z0 + COL_H / 2
    for face, (nx, ny) in (("x", (sx, 0)), ("y", (0, sy))):
        n = Vector((nx, ny, 0))
        t = Vector((-ny, nx, 0))
        f0 = Vector((x, y, zc)) + n * (h - 0.03)
        for k, u in enumerate((-PIN_U, PIN_U)):
            q = f0 + t * u
            P.log(a, q, q + n * (PIN_OUT + 0.03), PIN_R, ACCENT, sides=6, up=(0, 0, 1), end_key=mix(ACCENT, CREAM, 0.3),
                  name=f"{name}_pin{face}{k}", kind="pin", amp=0.03)


def cap(a, x, y, name="cap"):
    """The cap block standing on the collar (seated 0.02): chamfered sides, a bevelled top."""
    h, bv = CAP_HALF, CAP_BEV
    rings = [[(x + u, y + v, z) for u, v in P.sec_rect(h, h, 0.06)] for z in (Z_C - 0.02, CAP_TOP - bv)]
    rings.append([(x + u, y + v, CAP_TOP) for u, v in P.sec_rect(h - bv, h - bv, 0.04)])
    return P.prism(a, rings, mix(TIMBER, ACCENT, 0.6), cap_keys=(None, mix(ACCENT, CREAM, 0.15)), name=name,
                   kind="cap")


def post_set(a, tag, x, y, foot=True):
    sx, sy = (1 if x > 0 else -1), (1 if y > 0 else -1)
    with P.frame(None, f"{tag}_"):
        if foot:
            footing(a, x, y)
        post(a, x, y)
        collar(a, x, y, sx, sy)
        cap(a, x, y)


def perimeter_beam(a, side, name="beam"):
    """A perimeter beam between two collars (ends sunk 0.02 into the collars' faces), its top 0.03 under the collar top.
    side: "F", "B" (along X) or "L", "R" (along Y)."""
    zc = BEAM_TOP - BEAM_D / 2
    if side in ("F", "B"):
        y = -PY if side == "F" else PY
        e = PX - COL_HALF + 0.02
        p0, p1 = (-e, y, zc), (e, y, zc)
    else:
        x = -PX if side == "L" else PX
        e = PY - COL_HALF + 0.02
        p0, p1 = (x, -e, zc), (x, e, zc)
    p = P.plank(a, p0, p1, 2 * BEAM_HW, BEAM_D, TIMBER, ch=0.06, cap_keys=(TIMBER_L, TIMBER_L), name=name,
                kind="beam")
    P.texture(a, p.vs, 0.025, P.seed(P.TAG[-1] + name), scale=0.35)
    return p


# ---- canvas ----------------------------------------------------------------------------------------------------------
def canvas_z(x, y):
    """The canvas top surface: a pyramid over the hip rectangle (XH, YH), flat inside S_IN, each face sagging between
    its hips (none on the hips, the rim or the peak)."""
    ax, ay = abs(x) / XH, abs(y) / YH
    s = max(ax, ay)
    if s <= S_IN + 1e-9:
        return Z_APEX
    base = Z_APEX - RISE * (s - S_IN) / (1.0 - S_IN)
    if ay >= ax:
        w, so = x / (s * XH), S_OUT["y"]
    else:
        w, so = y / (s * YH), S_OUT["x"]
    sh = min(1.0, max(0.0, (s - S_IN) / (so - S_IN)))
    return base - SAG * max(0.0, 1.0 - w * w) * 4.0 * sh * (1.0 - sh)


def roof_grid():
    """The roof's top points and triangles: four patches (front, back, left, right) of rings s (outward) x lateral
    points, their lateral extent the hip (s x hip rectangle) or the corner notch, whichever is smaller; the peak a flat
    rectangle. Returns (points {key: Vector}, tris [(k0, k1, k2)])."""
    pts = {}

    def key(x, y):
        k = (round(x, 4), round(y, 4))
        if k not in pts:
            pts[k] = Vector((x, y, canvas_z(x, y)))
        return k
    tris = []
    patches = (("y", -1), ("y", 1), ("x", -1), ("x", 1))
    for ax, sg in patches:
        rings = RINGS[ax]
        rows = []
        for i, s in enumerate(rings):
            n = 1 if i == 0 else LAT
            js = (-1, 1) if i == 0 else range(-n, n + 1)
            if ax == "y":
                ext = min(s * XH, XN)
                row = [key(ext * j / n, sg * s * YH) for j in js]
            else:
                ext = min(s * YH, YN)
                row = [key(sg * s * XH, ext * j / n) for j in js]
            rows.append(row)
        # fan from the peak corners to the first full ring
        c0, c1 = rows[0]
        r1 = rows[1]
        m = len(r1) // 2
        for j in range(m):
            tris.append((c0, r1[j], r1[j + 1]))
        tris.append((c0, r1[m], c1))
        for j in range(m, len(r1) - 1):
            tris.append((c1, r1[j], r1[j + 1]))
        for i in range(1, len(rows) - 1):
            r0, r1 = rows[i], rows[i + 1]
            for j in range(len(r0) - 1):
                a_, b_, c_, d_ = r0[j], r0[j + 1], r1[j + 1], r1[j]
                if (pts[a_] - pts[c_]).length <= (pts[b_] - pts[d_]).length:
                    tris += [(a_, b_, c_), (a_, c_, d_)]
                else:
                    tris += [(a_, b_, d_), (b_, c_, d_)]
    # the flat peak
    i0 = RINGS["y"][0]
    corners = [key(-i0 * XH, -i0 * YH), key(i0 * XH, -i0 * YH), key(i0 * XH, i0 * YH), key(-i0 * XH, i0 * YH)]
    tris += [(corners[0], corners[1], corners[2]), (corners[0], corners[2], corners[3])]
    return pts, tris


def slab(a, top, tris, t, key, name, kind, rim_key=None):
    """A closed sheet from top points and triangles: the underside t straight below, rim quads on the open edges
    (canvas_sheet's recipe, m066). Returns the Piece."""
    keys_ = list(top)
    idx = {k: i for i, k in enumerate(keys_)}
    nb = len(keys_)
    pts = [top[k] for k in keys_] + [top[k] - Vector((0, 0, t)) for k in keys_]
    faces, fkeys, count = [], [], {}
    for tr in tris:
        p0, p1, p2 = (top[k] for k in tr)
        if (p1 - p0).cross(p2 - p0).z < 0:
            tr = (tr[0], tr[2], tr[1])
        faces.append([idx[q] for q in tr])
        fkeys.append(None)
        faces.append([nb + idx[q] for q in reversed(tr)])
        fkeys.append(None)
        for x in range(3):
            ed = (tr[x], tr[(x + 1) % 3])
            count.setdefault(frozenset(ed), []).append(ed)
    for eds in count.values():
        if len(eds) == 1:
            u_, v_ = eds[0]
            faces.append([idx[v_], idx[u_], nb + idx[u_], nb + idx[v_]])
            fkeys.append(rim_key)
    return P.shell(a, pts, faces, key, keys=fkeys, name=name, kind=kind, amp=0.02)


def roof(a, name="canvas"):
    top, tris = roof_grid()
    p = slab(a, top, tris, CT, CANVAS, name, "canvas", rim_key=mix(CANVAS, CANVAS_DEEP, 0.15))
    P.texture(a, p.vs, 0.03, P.seed(name), scale=0.18)
    P.GEO["canvas_low_under"] = round(min(v.z for v in top.values()) - CT, 3)
    return p


def skirt_bottom(u, half_b):
    f = 1.0 - (u / half_b) ** 2
    return SK_BOT - (SK_BOT - SK_MID) * f


def panel(a, cols, w0, w1, to3, key, name, hem_key=None):
    """A closed thin panel from columns [(u, z_top, z_bot)] (u increasing) between depths w0 and w1: front and back
    quads column to column (planar trapezoids), top, bottom and end rims; the bottom rim in hem_key. Clean quads
    where an ear-clipped outline would leave slivers."""
    n = len(cols)
    pts = [to3(u, zt, w) for w in (w0, w1) for u, zt, zb in cols] + [to3(u, zb, w) for w in (w0, w1)
                                                                      for u, zt, zb in cols]
    T0, T1, B0, B1 = 0, n, 2 * n, 3 * n
    faces, keys = [], []
    for k in range(n - 1):
        lowk = hem_key if hem_key else None
        faces += [[T0 + k, T0 + k + 1, B0 + k + 1, B0 + k], [T1 + k + 1, T1 + k, B1 + k, B1 + k + 1],
                  [T0 + k + 1, T0 + k, T1 + k, T1 + k + 1], [B0 + k, B0 + k + 1, B1 + k + 1, B1 + k]]
        keys += [None, None, None, lowk]
    faces += [[T0, B0, B1, T1], [T0 + n - 1, T1 + n - 1, B1 + n - 1, B0 + n - 1]]
    keys += [None, None]
    return P.shell(a, pts, faces, key, keys=keys, name=name, kind="canvas", amp=0.02)


def skirts(a, sides=("F", "B", "L", "R")):
    """The four skirt panels hanging outside the perimeter beams (0.003 off them), their tops 0.03 into the canvas
    rim (just inside it), ends 0.003 off the collars; under the collars a narrow end strip (inset 0.005 in the
    skirt's thickness, 0.02 into the panel) reaches to 0.003 off the post."""
    out = []
    zc = Z_C - COL_H - 0.02
    for side in sides:
        if side in ("F", "B"):
            sg = -1 if side == "F" else 1
            ha, hb = PX - COL_HALF - 0.003, PX - PH - 0.003
            zt = canvas_z(0.0, sg * YE) - 0.03
            wo = sg * (YE - 0.007)

            def to3(u, z, w):
                return Vector((u, w, z))
        else:
            sg = -1 if side == "L" else 1
            ha, hb = PY - COL_HALF - 0.003, PY - PH - 0.003
            zt = canvas_z(sg * XE, 0.0) - 0.03
            wo = sg * (XE - 0.007)

            def to3(u, z, w):
                return Vector((w, u, z))
        w0, w1 = sorted((wo, wo - sg * SK_T))
        cols = [(u, zt, skirt_bottom(u, hb)) for u in (-ha + 2 * ha * k / 6 for k in range(7))]
        p = panel(a, cols, w0, w1, to3, CANVAS, f"skirt{side}", hem_key=mix(CANVAS, CANVAS_DEEP, 0.12))
        P.texture(a, p.vs, 0.03, P.seed(f"skirt{side}"), scale=0.25)
        out.append(p)
        for e, (u0, u1) in (("a", (-hb, -ha + 0.02)), ("b", (ha - 0.02, hb))):
            cols = [(u0, zc, skirt_bottom(u0, hb)), (u1, zc, skirt_bottom(u1, hb))]
            out.append(panel(a, cols, w0 + 0.005, w1 - 0.005, to3, CANVAS, f"skirt{side}_end{e}"))
    return out


def flaps(a):
    """Three tattered tan flaps hanging from the rear skirt's hem (tops 0.05 up inside the skirt, centred in its
    thickness)."""
    yc = YE - 0.007 - SK_T / 2
    hb = PX - PH - 0.003
    out = []
    for i, (xc, w, L) in enumerate(FLAPS):
        x0, x1 = xc - w / 2, xc + w / 2
        zt = min(skirt_bottom(x0, hb), skirt_bottom(x1, hb), skirt_bottom(xc, hb)) + 0.05
        zb = zt - L
        outline = [(x0, zt), (x1, zt), (x1, zb + 0.30), (x1 - 0.22 * w, zb + 0.05), (xc + 0.08 * w, zb + 0.42),
                   (xc - 0.12 * w, zb), (x0 + 0.20 * w, zb + 0.38), (x0, zb + 0.12)]
        if i == 1:
            outline = [(x0, zt), (x1, zt), (x1, zb + 0.10), (x1 - 0.30 * w, zb + 0.45), (xc, zb + 0.05),
                       (x0 + 0.28 * w, zb + 0.40), (x0, zb + 0.18)]
        p = P.ext(a, outline, yc - FLAP_T / 2, yc + FLAP_T / 2, mix(CANVAS, CANVAS_DEEP, 0.55),
                  to3=lambda u, v, w_: Vector((u, w_, v)), name=f"flap{i}", kind="canvas", amp=0.03)
        P.texture(a, p.vs, 0.04, P.seed(f"flap{i}"), scale=0.4)
        out.append(p)
    return out


def finial(a):
    """The finial on the peak: a plate seated 0.02 into the canvas top and a cube on it."""
    z0 = Z_APEX - 0.02
    pl, ph, cu, chh = FIN["plate"], FIN["plate_h"], FIN["cube"], FIN["cube_h"]
    cbox(a, (0, 0), pl, pl, z0, z0 + ph, mix(TIMBER, ACCENT, 0.6), "fin_plate", "finial", ch=0.06)
    cbox(a, (0, 0), cu, cu, z0 + ph - 0.02, z0 + ph - 0.02 + chh, mix(TIMBER, ACCENT, 0.6), "fin_cube", "finial",
         ch=0.06, top_key=mix(ACCENT, CREAM, 0.15))


def canvas_all(a):
    roof(a)
    skirts(a)
    flaps(a)
    finial(a)


# ---- roof frame: crossed beams and hub --------------------------------------------------------------------------------
HUB_TOP = Z_APEX - CT + 0.02


def rafter_geo():
    """The rafter line (shared by all four): unit plan direction d (+x +y quadrant), its end at the cap block's inner
    corner chamfer (0.07 past the corner along d), its start 0.03 inside the hub; the top straight under the canvas
    hip, lowered until its top edges clear the canvas underside by 0.01; depth to sit 0.02 into the collar top."""
    d = Vector((XH, YH, 0)).normalized()
    lat = Vector((-d.y, d.x, 0))
    corner = Vector((PX - CAP_HALF, PY - CAP_HALF, 0))
    end = corner + d * 0.07
    L_end = end.length
    L_hub = HUB_R / math.cos(math.radians(5.0)) - 0.03
    hipL = math.hypot(XH, YH)

    def hip_top(L):
        s = L / hipL
        return Z_APEX if s <= S_IN else Z_APEX - RISE * (s - S_IN) / (1 - S_IN)
    off = 0.0
    for k in range(41):
        L = L_hub + (L_end - L_hub) * k / 40
        for u in (-RAF_W / 2, 0.0, RAF_W / 2):
            q = d * L + lat * u
            if max(abs(q.x) / XH, abs(q.y) / YH) > S_STAR:
                continue                         # past the notch: no canvas over it
            under = canvas_z(q.x, q.y) - CT
            off = max(off, (hip_top(L) - CT) - under + 0.012)
    top0, top1 = hip_top(L_hub) - CT - off, hip_top(L_end) - CT - off
    depth = top1 - (Z_C - 0.02)
    return dict(d=d, lat=lat, L0=L_hub, L1=L_end, top0=top0, top1=top1, depth=depth, off=off)


def rafters(a):
    g = rafter_geo()
    out = []
    for qx, qy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        d = Vector((g["d"].x * qx, g["d"].y * qy, 0))
        lat = Vector((-d.y, d.x, 0))
        rings = []
        for L, zt in ((g["L0"], g["top0"]), (g["L1"], g["top1"])):
            c = d * L
            rings.append([c + lat * u + Vector((0, 0, zt + v)) for u, v in
                          ((-RAF_W / 2, -g["depth"]), (RAF_W / 2, -g["depth"]), (RAF_W / 2, 0.0), (-RAF_W / 2, 0.0))])
        p = P.prism(a, rings, TIMBER, cap_keys=(TIMBER_L, TIMBER_L), name=f"rafter{'pn'[qx < 0]}{'pn'[qy < 0]}",
                    kind="rafter")
        P.texture(a, p.vs, 0.025, P.seed(f"rafter{qx}{qy}"), scale=0.35)
        out.append(p)
    P.GEO["rafter"] = {"depth": round(g["depth"], 3), "top_hub": round(g["top0"], 3), "top_end": round(g["top1"], 3),
                       "clear_off": round(g["off"], 3)}
    return out


def hub(a):
    """The round hub under the peak (sheet close-up "Roof Hub"): an 8-sided drum seated 0.02 into the canvas
    underside, deep enough to take the rafter ends, with a pale disc and bolt under it."""
    g = rafter_geo()
    bot = min(HUB_TOP - 0.6, g["top0"] - g["depth"] - 0.10)
    P.pole(a, (0.0, 0.0), bot, HUB_TOP, HUB_R, mix(TIMBER, ACCENT, 0.5), sides=8, name="hub", kind="hub")
    P.pole(a, (0.0, 0.0), bot - 0.10, bot + 0.02, 0.26, mix(ACCENT, CREAM, 0.2), sides=8, name="hub_disc",
           kind="hub")
    P.pole(a, (0.0, 0.0), bot - 0.16, bot - 0.08, 0.11, IRON, sides=6, name="hub_bolt", kind="hub")
    P.GEO["hub_bottom"] = round(bot - 0.16, 3)


def roof_frame(a):
    """The crossed roof beams and the hub under the peak."""
    hub(a)
    rafters(a)


# ---- half walls ---------------------------------------------------------------------------------------------------------
def half_wall(a, side, name="wall"):
    """A plank half wall (sheet rear cell): WALL_ROWS horizontal boards (8-sided, chamfered: V seams on both faces,
    rows overlapping 0.02) between two end stiles (proud on both faces, a bevelled top) with two bolts on each
    stile's outer face. side "B", "L" or "R"; it stands on the post line between the footings."""
    if side == "B":
        along, out_n, c = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, PY, 0))
        half = PX - WALL_END
    else:
        sg = -1 if side == "L" else 1
        along, out_n, c = Vector((0, 1, 0)), Vector((sg, 0, 0)), Vector((sg * PX, 0, 0))
        half = PY - WALL_END
    top, nrows = WALL[side]
    stile_top = top + STILE_UP
    rh = top / nrows
    s0, s1 = -half + STILE_W - 0.03, half - STILE_W + 0.03
    out = []
    for i in range(nrows):
        z0, z1 = i * rh - (0.01 if i else 0.0), (i + 1) * rh + (0.01 if i < nrows - 1 else 0.0)
        zc, hz = (z0 + z1) / 2, (z1 - z0) / 2
        nm = f"{name}_row{i}"
        p = P.beam(a, c + along * s0 + Vector((0, 0, zc)), c + along * s1 + Vector((0, 0, zc)),
                   P.sec_rect(WALL_T / 2, hz, 0.07), mix(PLANK, TIMBER_D, 0.10 * (i % 2)), up=(0, 0, 1),
                   cap_keys=(TIMBER_L, TIMBER_L), name=nm, kind="plank")
        P.texture(a, p.vs, 0.025, P.seed(P.TAG[-1] + nm), scale=0.5)
        out.append(p)
    for k, s in enumerate((-half + STILE_W / 2, half - STILE_W / 2)):
        q = c + along * s
        hx, hy = (STILE_W / 2, STILE_T / 2) if side == "B" else (STILE_T / 2, STILE_W / 2)
        st = cbox(a, (q.x, q.y), hx, hy, 0.0, stile_top, TIMBER, f"{name}_stile{k}", "stile", ch=0.05,
                  top_key=TIMBER_L)
        P.texture(a, st.vs, 0.025, P.seed(P.TAG[-1] + f"stile{k}"), scale=0.5)
        for j, z in enumerate((0.75, stile_top - 0.70)):
            P.bolt(a, q + out_n * (STILE_T / 2) + Vector((0, 0, z)), out_n, (0, 0, 1), IRON, h=0.09, proud=0.05,
                   name=f"{name}_bolt{k}{j}", kind="iron")
    return out


# ---- workbench ----------------------------------------------------------------------------------------------------------
def workbench(a, cx=None, cy=None, items=True):
    """The workbench (sheet hero, exploded): three top boards between breadboard ends (top 2.60), four square legs,
    front and back aprons, a low stretcher frame carrying a shelf board with a block, a back board along the rear
    edge; bolts on the breadboard ends."""
    b = BENCH
    L = b["x1"] - b["x0"]
    if cx is None:
        cx, cy = (b["x0"] + b["x1"]) / 2, b["y0"] + b["D"] / 2
    D, top, tt, e, lg = b["D"], b["top"], b["tt"], b["end"], b["leg"]
    x0, x1, y0, y1 = cx - L / 2, cx + L / 2, cy - D / 2, cy + D / 2
    w = (D - 2 * GAP) / 3
    zc = top - tt / 2
    for k in range(3):
        yk = y0 + w / 2 + k * (w + GAP)
        p = P.plank(a, (x0 + e - 0.02, yk, zc), (x1 - e + 0.02, yk, zc), w, tt, mix(TIMBER_L, TIMBER, 0.15 * k),
                    ch=0.05, name=f"top{k}", kind="plank", amp=0.05)
        P.texture(a, p.vs, 0.025, P.seed(f"top{k}"), scale=0.5)
    for s, xe in ((-1, x0 + e / 2), (1, x1 - e / 2)):
        cbox(a, (xe, cy), e / 2, D / 2 + 0.04, top - tt - 0.04, top + 0.02, TIMBER, f"bread{s:+d}", "plank", ch=0.05,
             top_key=TIMBER_L)
        P.bolt(a, (xe, y0 - 0.04, top - tt / 2 + 0.01), (0, -1, 0), (0, 0, 1), IRON, h=0.08, proud=0.04,
               name=f"bread_bolt{s:+d}", kind="iron")
    zl = top - tt - 0.04 + 0.02
    lx, ly = L / 2 - 0.30 - lg / 2, D / 2 - 0.16 - lg / 2
    for s in (-1, 1):
        for t in (-1, 1):
            p = P.post(a, (cx + s * lx, cy + t * ly), 0.0, zl, lg / 2, TIMBER, ch=0.05, name=f"leg{s:+d}{t:+d}",
                       kind="leg")
            P.texture(a, p.vs, 0.025, P.seed(f"leg{s}{t}"), scale=0.5)
    # aprons under the top, between the legs (front and back faces flush 0.06 inside the legs' faces)
    for t in (-1, 1):
        ya = cy + t * (ly + lg / 2 - 0.06 - 0.07)
        bx(a, (cx - lx + lg / 2 - 0.02, ya - 0.07, zl - 0.42), (cx + lx - lg / 2 + 0.02, ya + 0.07, zl + 0.01),
           TIMBER, f"apron{t:+d}", "rail")
    # low frame: side rails (along y) and long rails (along x), a shelf board on the long rails, a block on it
    zr0, zr1 = 0.50, 0.78
    for s in (-1, 1):
        bx(a, (cx + s * lx - 0.14, cy - ly + lg / 2 - 0.02, zr0), (cx + s * lx + 0.14, cy + ly - lg / 2 + 0.02, zr1),
           TIMBER, f"srail{s:+d}", "rail")
    for t in (-1, 1):
        bx(a, (cx - lx + lg / 2 - 0.02, cy + t * ly - 0.13, zr0), (cx + lx - lg / 2 + 0.02, cy + t * ly + 0.13, zr1),
           TIMBER, f"lrail{t:+d}", "rail")
    p = P.plank(a, (cx - lx + lg / 2 + 0.02, cy, zr1 + 0.09), (cx + lx - lg / 2 - 0.02, cy, zr1 + 0.09),
                2 * ly - 0.10, 0.20, mix(TIMBER_L, TIMBER, 0.4), ch=0.04, name="shelf", kind="plank", amp=0.05)
    cbox(a, (cx + 0.6, cy + 0.1), 0.65, 0.42, zr1 + 0.17, zr1 + 0.17 + 0.55, TIMBER_L, "shelf_block", "item",
         ch=0.04, rot=6.0)
    # back board along the rear edge of the top
    bx(a, (x0 + e - 0.01, y1 - 0.20, top - 0.02), (x1 - e + 0.01, y1 - 0.02, top + 0.40), TIMBER, "backboard",
       "plank")
    if items:
        bench_items(a, cx, cy, x0, x1, y0, y1, top)


def bench_items(a, cx, cy, x0, x1, y0, y1, top):
    """On the top: the tool press at the back right (base, two uprights, crossbar, a grey jaw block), a tray with a
    grey stone and a wooden bowl, a cream whetstone near the front left, a hammer lying near the front."""
    z0 = top - 0.01
    # tool press
    px_, py_ = x1 - 1.55, y1 - 0.62
    bx(a, (px_ - 0.95, py_ - 0.38, z0), (px_ + 0.95, py_ + 0.38, z0 + 0.18), TIMBER_D, "press_base", "item")
    for k, sx in enumerate((-1, 1)):
        cbox(a, (px_ + sx * 0.72, py_ + 0.05), 0.17, 0.17, z0 + 0.16, z0 + 1.55, TIMBER, f"press_up{k}", "item",
             ch=0.03)
    bx(a, (px_ - 0.95, py_ - 0.17, z0 + 1.50), (px_ + 0.95, py_ + 0.27, z0 + 1.82), TIMBER_D, "press_bar", "item")
    bx(a, (px_ - 0.56, py_ - 0.20, z0 + 0.16), (px_ + 0.56, py_ + 0.26, z0 + 0.75), METAL, "press_jaw", "item")
    bx(a, (px_ - 0.30, py_ - 0.12, z0 + 0.73), (px_ + 0.30, py_ + 0.18, z0 + 1.10), mix(TIMBER_L, CREAM, 0.4),
       "press_block", "item")
    # tray with a stone and a bowl
    m = Matrix.Translation((cx - 0.80, cy + 0.25, 0.0)) @ Matrix.Rotation(math.radians(-8), 4, "Z")
    tw, td = 0.80, 0.52
    P.box(a, (-tw, -td, z0), (tw, td, z0 + 0.12), CREAM, m=m, name="tray", kind="item", amp=0.02)
    for k, (lo, hi) in enumerate((((-tw, -td), (tw, -td + 0.12)), ((-tw, td - 0.12), (tw, td)),
                                  ((-tw, -td + 0.10), (-tw + 0.12, td - 0.10)), ((tw - 0.12, -td + 0.10), (tw, td - 0.10)))):
        P.box(a, (lo[0], lo[1], z0 + 0.10), (hi[0], hi[1], z0 + 0.26), mix(CREAM, TIMBER_L, 0.3), m=m,
              name=f"tray_rim{k}", kind="item", amp=0.02)
    stone = [m @ Vector(p) for p in ((-0.55, -0.28, z0 + 0.10), (0.05, -0.32, z0 + 0.10), (0.10, 0.25, z0 + 0.10),
                                     (-0.55, 0.28, z0 + 0.10), (-0.45, -0.18, z0 + 0.40), (-0.02, -0.15, z0 + 0.42),
                                     (0.0, 0.15, z0 + 0.38), (-0.48, 0.18, z0 + 0.36))]
    P.hull(a, stone, METAL, name="tray_stone", kind="item", amp=0.04)
    bc = m @ Vector((0.38, 0.02, 0.0))
    rings = [[(bc.x + r * math.cos(2 * math.pi * k / 8 + math.pi / 8), bc.y + r * math.sin(2 * math.pi * k / 8 + math.pi / 8),
               z) for k in range(8)] for z, r in ((z0 + 0.10, 0.17), (z0 + 0.36, 0.25))]
    P.prism(a, rings, TIMBER_L, cap_keys=(None, TIMBER_D), name="bowl", kind="item", amp=0.03)
    # whetstone and hammer
    m2 = Matrix.Translation((x0 + 0.95, y0 + 0.55, 0.0)) @ Matrix.Rotation(math.radians(12), 4, "Z")
    P.box(a, (-0.50, -0.20, z0), (0.50, 0.20, z0 + 0.24), CREAM, m=m2, name="whetstone", kind="item", amp=0.02)
    hx, hy = cx - 0.75, y0 + 0.45
    P.log(a, (hx - 0.70, hy, z0 + 0.09), (hx + 0.35, hy, z0 + 0.09), 0.08, TIMBER_L, sides=6, end_key=TIMBER_D,
          name="hammer_handle", kind="item")
    bx(a, (hx + 0.33, hy - 0.30, z0), (hx + 0.62, hy + 0.30, z0 + 0.26), METAL, "hammer_head", "item")


# ---- crates, packs and boxes ----------------------------------------------------------------------------------------------
def crate(a, c, rot=0.0, name="crate"):
    """A closed framed crate (P.crate without braces): a lighter frame and lid over darker recessed panels."""
    out = P.crate(a, c, TIMBER, TIMBER_D, rot=rot, W=CRATE_W, H=CRATE_W, frame_t=(0.0, 0.35), open_top=False,
                  braces=False, name=name)
    P.paint(a, [out[0].fs[0]], TIMBER)                     # the hidden bottom like the lid (no dark-down shading)
    return out


def pack(a, c, z0, rot=0.0, name="pack"):
    """A green pack (bedroll bundle) lying along X on top of something at z0 (seated 0.02): a rounded 8-sided
    bundle and two leather straps round it."""
    Lh, hy, hz = 0.80, 0.55, 0.42
    m = Matrix.Translation((c[0], c[1], 0)) @ Matrix.Rotation(math.radians(rot), 4, "Z")
    sec = P.sec_rect(hy, hz, 0.20)
    zc = z0 + 0.034 + hz                 # the straps' lower runs sit 0.01 into what it lies on
    rings = [[m @ Vector((x, u, zc + v)) for u, v in sec] for x in (-Lh, Lh)]
    body = P.prism(a, rings, PACK, cap_keys=(PACK_DEEP, PACK_DEEP), name=name, kind="pack", amp=0.04)
    P.texture(a, body.vs, 0.04, P.seed(name), scale=0.5)
    out = [body]
    for k, x in enumerate((-0.42, 0.42)):
        secp = [m @ Vector((x, u, zc + v)) for u, v in sec]
        cen = m @ Vector((x, 0, zc))
        nrm = m.to_3x3() @ Vector((1, 0, 0))
        out.append(P.strap(a, secp, cen, nrm, 0.16, 0.04, STRAP, gap=0.004, pts=8, name=f"{name}_strap{k}"))
    return out


def grey_box(a, c, z0, name="gbox"):
    """The grey banded box on the front-left crate (sheet hero): a metal box with cream corner posts and a knob."""
    hx, hy, H, pp = 0.42, 0.37, 0.80, 0.12
    zb = z0 - 0.02
    bx(a, (c[0] - hx, c[1] - hy, zb), (c[0] + hx, c[1] + hy, zb + H), METAL, name, "item")
    for k, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        q = (c[0] + sx * (hx + pp - 0.03), c[1] + sy * (hy + pp - 0.03))       # each corner post 0.03 into the box
        bx(a, (q[0] - pp, q[1] - pp, zb), (q[0] + pp, q[1] + pp, zb + H + 0.04), CREAM, f"{name}_post{k}",
           "item", amp=0.02)
    bx(a, (c[0] - 0.20, c[1] - 0.20, zb + H - 0.02), (c[0] + 0.20, c[1] + 0.20, zb + H + 0.22), METAL,
       f"{name}_knob", "item")


def chest(a):
    """A small wooden chest against the back wall, two iron bands over its lid."""
    (x, y), L, D, H = CHEST["c"], CHEST["L"], CHEST["D"], CHEST["H"]
    cbox(a, (x, y), L / 2, D / 2, 0.0, H, TIMBER, "chest", "item", ch=0.05)
    for k, dx in enumerate((-0.45, 0.45)):
        x0, x1 = x + dx - 0.08, x + dx + 0.08
        bx(a, (x0, y - D / 2 - 0.04, H - 0.02), (x1, y + D / 2 + 0.04, H + 0.04), IRON, f"chest_band{k}", "iron",
           amp=0.02)
        for sg in (-1, 1):
            yf = y + sg * D / 2
            bx(a, (x0 + 0.005, yf - sg * 0.02, H - 0.45), (x1 - 0.005, yf + sg * 0.035, H), IRON,
               f"chest_band{k}{'fb'[sg > 0]}", "iron", amp=0.02)


def crates(a):
    for tag, ((x, y), rot, what) in CRATES.items():
        with P.frame(None, f"{tag}_"):
            crate(a, (x, y), rot)
            if what == "pack":
                pack(a, (x - 0.05, y + 0.05), CRATE_W, rot=rot + 4.0)
            elif what == "box":
                grey_box(a, (x + 0.15, y + 0.10), CRATE_W)
    chest(a)


# ---- lantern and banner -------------------------------------------------------------------------------------------------
HALO = {"emitters": [{"name": "Halo", "texture": "glow_soft", "color": ["#FFC23A", "#FF9A1E"], "size": [1.3, 1.6],
                      "transparency": [0.65, 1.0], "lifetime": [1.0, 1.5], "rate": 2, "speed": [0, 0.05], "spread": 0,
                      "light_emission": 1.0}],
        "light": {"color": "#FFB347", "brightness": 1.0, "range": 12, "flicker": True}}


def lantern_height():
    L = LANT
    top = L["plate"] + L["gh"] + L["band"] + 0.003 + L["roof"] + 0.003 + L["fin"] - 0.006
    return top - 0.01 + 0.20 + 0.06 + 0.20 + 0.06


def lantern_base():
    return (LANT_XY[0], LANT_XY[1], ARM_Z - 0.30 - lantern_height())


def glass_point():
    b = lantern_base()
    return (b[0], b[1], b[2] + LANT["plate"] + LANT["gh"] / 2)


def lantern(a, with_bracket=True):
    """(m066) The square dark lantern (P.lantern, Neon glass) hung by its ring from an iron bracket arm off the
    front-left post's inner (+X) face."""
    r = P.lantern(a, lantern_base(), IRON, GLOW, ring_axis=(0, 1, 0), name="lantern", **LANT)
    if with_bracket:
        P.bracket(a, LANT_XY, (-PX + PH, LANT_XY[1], 0.0), (1, 0), ARM_Z, r["ring_top"].z, IRON, strap=0.70,
                  name="lantern_bracket")
    P.GEO["lantern"] = {"bottom": round(lantern_base()[2], 3), "glass": [round(v, 3) for v in r["glass"]]}
    return r


def knob(a, c, r, name):
    """(m072) A low-poly ball on the rod's axis (X)."""
    c = Vector(c)
    pts = [c + Vector((r, 0, 0)), c - Vector((r, 0, 0))]
    for k, xf in enumerate((-0.6, 0.0, 0.6)):
        rr = r * math.sqrt(1 - xf * xf)
        for j in range(6):
            th = 2 * math.pi * (j + 0.5 * k) / 6
            pts.append(c + Vector((xf * r, rr * math.cos(th), rr * math.sin(th))))
    return P.hull(a, pts, mix(TIMBER, ACCENT, 0.5), name=name, kind="knob", amp=0.03)


def _diamond_ring(a, cx, cz, hw, hh, line, y0, y1, name):
    """(m072) A diamond outline slab (outer half sizes hw x hh, `line` wide along x) between y0 and y1."""
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


def rod_z():
    """The rod's height: the hem sleeve round it (flat radius rod + 0.088 + 0.08) seated 0.02 into the beam's
    underside."""
    return BEAM_TOP - BEAM_D - (BAN["rod_r"] / math.cos(math.pi / 8) + 0.008 + 0.08) + 0.02


def banner(a, y=None, rz=None):
    """(m072 recipe) The rod (knobbed ends) under the rear beam, its top seated 0.02 into the beam's underside; a
    dark-red hem sleeve round it, the red cloth with a pointed foot and the cream diamond (ring and centre) on its
    front (-Y) face."""
    y = BAN["y"] if y is None else y
    rz = rod_z() if rz is None else rz
    r = BAN["rod_r"]
    x0, x1 = BAN["rod_x"]
    P.log(a, (x0, y, rz), (x1, y, rz), r, mix(TIMBER, ACCENT, 0.3), sides=8, end_key=TIMBER_L, name="rod", kind="rod")
    for sg, xe in ((-1, x0), (1, x1)):
        knob(a, (xe + sg * (BAN["knob"] - 0.035), y, rz), BAN["knob"], f"knob{sg:+d}")
    s_in = r / math.cos(math.pi / 8) + 0.008
    s_t = 0.08
    c0, c1 = BAN["x0"], BAN["x1"]
    P.sleeve(a, (c0 - 0.04, y, rz), (c1 + 0.04, y, rz), s_in, s_in + s_t, BANNER_DEEP, sides=8, name="hem",
             kind="hem", amp=0.02)
    top = rz - s_in - 0.015
    xm = (c0 + c1) / 2
    outline = [(c0, top), (c1, top), (c1, BAN["side"]), (xm, BAN["tip"]), (c0, BAN["side"])]
    t = BAN["t"]
    yf, yb = y - t / 2, y + t / 2
    cloth = P.ext(a, outline, yf, yb, BANNER, to3=lambda u, v, w: Vector((u, w, v)), name="cloth", kind="banner",
                  amp=0.02)
    P.texture(a, cloth.vs, 0.02, P.seed("cloth"), scale=0.4)
    ez = (top + BAN["side"]) / 2 - 0.25
    e0, e1 = yf + 0.005, yf - 0.015
    _diamond_ring(a, xm, ez, 0.55, 0.85, 0.16, e0, e1, "emblem_ring")
    d = [(xm, ez + 0.24), (xm + 0.15, ez), (xm, ez - 0.24), (xm - 0.15, ez)]
    P.ext(a, d, e1, e0, CREAM, to3=lambda u, v, w: Vector((u, w, v)), name="emblem_dot", kind="emblem", amp=0.02)
    P.GEO["banner"] = {"top": round(top, 3), "tip": BAN["tip"]}


# ---- assemblies ------------------------------------------------------------------------------------------------------------
POSTS = {"FL": (-PX, -PY), "FR": (PX, -PY), "BL": (-PX, PY), "BR": (PX, PY)}


def hero_all(a):
    for tag, (x, y) in POSTS.items():
        post_set(a, tag, x, y)
    for side in ("F", "B", "L", "R"):
        with P.frame(None, f"{side}_"):
            perimeter_beam(a, side)
    roof_frame(a)
    canvas_all(a)
    for side in ("B", "L", "R"):
        with P.frame(None, f"{side}_"):
            half_wall(a, side)
    with P.frame(None, "bench_"):
        workbench(a)
    crates(a)
    with P.frame(None, "lantern_"):
        lantern(a)
    with P.frame(None, "banner_"):
        banner(a)


def post_part(a):
    """One post with its collar, pins and cap block (no footing: HuntWorkshopFooting), the front-left one."""
    post_set(a, "FL", -PX, -PY, foot=False)


def beam_part(a):
    with P.frame(None, "F_"):
        perimeter_beam(a, "F")


def wall_part(a):
    with P.frame(None, "B_"):
        half_wall(a, "B")


def crate_part(a):
    crate(a, (0.0, 0.0))


def pack_part(a):
    crate(a, (0.0, 0.0))
    pack(a, (-0.05, 0.05), CRATE_W, rot=4.0)


def lantern_part(a):
    lantern(a)


def banner_part(a):
    banner(a)


PARTS = ((POST_P, post_part), (FOOT_P, lambda a: footing(a, 0.0, 0.0)), (BEAM_P, beam_part), (FRAME_P, roof_frame),
         (CANVAS_P, canvas_all), (WALL_P, wall_part), (BENCH_P, lambda a: workbench(a)), (CRATE_P, crate_part),
         (PACK_P, pack_part), (LANTERN_P, lantern_part), (BANNER_P, banner_part))


def bench_point():
    b = BENCH
    return ((b["x0"] + b["x1"]) / 2, b["y0"] + b["D"] + 0.9, 0.0)


POINTS = {HERO: {"m077_bench": (bench_point(), (0, -1, 0)), "m077_lantern": (glass_point(), (0, -1, 0)),
                 "m077_entry": ((4.08, -PY - 1.5, 0.0), (0, 1, 0))},
          BENCH_P: {"m077_bench": (bench_point(), (0, -1, 0))}}
FX = {HERO: [("heat_glow", glass_point(), HALO)], LANTERN_P: [("heat_glow", glass_point(), HALO)]}
NOTES = {
    HERO: "Hunt workshop (sheet 077): an open-front timber workshop, posts 13.0 x 11.2 apart on tapered stone "
          "footings, collar blocks with pin bolts and cap blocks at the post tops, four perimeter beams, crossed roof "
          "beams under a four-sided sagging cream canvas (peak 13.45, finial to 14.45) with skirts on all sides "
          "(lowest 7.92, the walk-under headroom) and three tattered flaps on the rear skirt; plank half walls (4.62) "
          "on the back and both sides; a workbench across the front (top 2.60) with a tool press, a tray, a whetstone "
          "and a hammer; the entry is the gap right of the bench; a Neon lantern on an iron bracket off the front-left "
          "post (heat_glow); the red diamond banner on a rod under the rear beam; crates (one with a grey box, three "
          "with green packs) and a chest. Bench, lantern and entry points stored.",
    POST_P: "Post: 1.6 square timber post (to 9.98) with its joint collar (1.95 square, four pin bolts) and cap block "
            "(1.36 square, top 10.95); stands on HuntWorkshopFooting",
    FOOT_P: "Stone Footing: tapered stone block (2.30 base, 1.92 top, 1.55 high)",
    BEAM_P: "Roof Beam: a 0.8 x 0.75 perimeter beam between two collars (11.09 long; the side beams are 1.8 shorter)",
    FRAME_P: "Roof Frame: the crossed roof beams (four rafters along the canvas hips) and the round hub under the peak",
    CANVAS_P: "Canvas Roof: the four-sided sagging canvas notched round the cap blocks, its four skirts, three rear "
              "flaps and the finial",
    WALL_P: "Half Wall: four-row plank panel between two bolted end stiles (10.66 long, 4.62 high; the side walls "
            "are 1.8 shorter)",
    BENCH_P: "Workbench: 6.4 x 2.5 plank bench (top 2.60) with breadboard ends, shelf and back board, a tool press, "
             "tray with stone and bowl, whetstone and hammer",
    CRATE_P: "Crate: closed framed crate, 2.30 cube, lighter lid",
    PACK_P: "Supply Crate: the crate with a strapped green pack on it",
    LANTERN_P: "Lantern: square dark iron lantern, Neon glass, on its iron wall bracket; heat_glow socket",
    BANNER_P: "Banner: knobbed rod, hem sleeve, red pointed cloth with the cream diamond",
}
COLLISION = {HERO: "precise", POST_P: "hull", FOOT_P: "box", BEAM_P: "box", FRAME_P: "none", CANVAS_P: "none",
             WALL_P: "box", BENCH_P: "box", CRATE_P: "box", PACK_P: "box", LANTERN_P: "none", BANNER_P: "none"}
BUDGETS = {HERO: 8000}
TARGET_SIZE = None
VIEWS = {"f34_sheet": (-35, 25), "r34_sheet": (-140, 25), "front_sheet": (0, 0), "side_sheet": (90, 0),
         "rear_sheet": (180, 0), "top_sheet": (0, 89.9)}
EXPLODED = {CANVAS_P: (0.0, 0.0, 6.0), FRAME_P: (0.0, 0.0, 3.0), BEAM_P: (0.0, -9.0, 3.0),
            POST_P: [(-12.0, -6.0, 1.8), (12.0, -6.0, 1.8)], FOOT_P: [(-12.0, -6.0, 0.0), (12.0, -6.0, 0.0)],
            WALL_P: (0.0, 9.0, 0.0), BENCH_P: (0.0, -2.0, 0.0), CRATE_P: (-7.0, -12.0, 0.0),
            PACK_P: (7.0, -12.0, 0.0), LANTERN_P: (0.0, -10.0, 2.0), BANNER_P: (-1.0, -14.0, 0.0)}
WALK = {"paths": [[(4.12, -10.5), (4.12, -1.0), (0.0, 1.0)]], "ride": False, "turn": [(0.0, 1.0, 0.0)]}
VERIFY = dict(cls="building", walk=WALK, sockets={HERO: ["heat_glow"], LANTERN_P: ["heat_glow"]},
              stored={HERO: ["m077_bench", "m077_lantern", "m077_entry"], BENCH_P: ["m077_bench"]})
COMPARE = {"f34": {"box": (20, 100, 508, 472), "view": VIEWS["f34_sheet"][:2]},
           "r34": {"box": (520, 100, 1008, 472), "view": VIEWS["r34_sheet"][:2]},
           "front": {"box": (18, 512, 280, 712), "view": (0, 0)},
           "side": {"box": (288, 512, 510, 712), "view": (90, 0)},
           "rear": {"box": (516, 512, 757, 712), "view": (180, 0)},
           "top": {"box": (763, 512, 1008, 712), "view": (0, 89.9)}}


def workshop_check(objs):
    """Spec "Brief": headroom under the skirts, beams and canvas over the entry and the floor; the bench top at
    2.60; the free floor area under the canvas (a 1.0-square footprint clear of everything up to 5.5)."""
    h = objs[HERO]
    me = h.data
    tree = BVHTree.FromPolygons([h.matrix_world @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])
    up, down = Vector((0, 0, 1)), Vector((0, 0, -1))
    oz = h.matrix_world.translation.z - h[MODEL.OFF][2]

    def z_up(x, y, z0=0.05):
        hit = tree.ray_cast(MODEL.at(h, (x, y, z0)), up)[0]
        return round(hit.z - oz, 3) if hit else None

    def z_down(x, y, top=3.4):
        hit = tree.ray_cast(MODEL.at(h, (x, y, top)), down)[0]
        return round(hit.z - oz, 3) if hit else None
    head = {"entry_skirt": z_up(4.08, -YE + 0.04), "front_beam": z_up(4.08, -PY),
            "inside": z_up(0.0, 0.6), "under_rafter": z_up(3.0, 2.55), "side_beam": z_up(PX - 0.6, 0.0, 5.0)}
    bench_z = z_down((BENCH["x0"] + BENCH["x1"]) / 2 - 1.6, BENCH["y0"] + 0.5)
    # free floor: grid cells (0.5) inside the post rectangle whose 1.0-square footprint is clear up to 5.5
    cell, free = 0.5, 0
    xs = [-PX + 0.25 + cell * i for i in range(int(2 * PX / cell))]
    ys = [-PY + 0.25 + cell * j for j in range(int(2 * PY / cell))]
    for x in xs:
        for y in ys:
            ok = True
            for dx in (-0.5, 0.0, 0.5):
                for dy in (-0.5, 0.0, 0.5):
                    zz = z_up(x + dx, y + dy, 0.02)
                    if zz is not None and zz < 5.5:
                        ok = False
                        break
                if not ok:
                    break
            free += ok
    rep = {"headroom": head, "bench_top": bench_z, "free_floor_area": round(free * cell * cell, 2),
           "canvas_low_under": P.GEO.get("canvas_low_under"), "rafter": P.GEO.get("rafter")}
    pr = []
    for k in ("entry_skirt", "front_beam", "inside"):
        if head[k] is None or head[k] < 7.8:
            pr.append(f"{HERO}: headroom {k} {head[k]} under 7.8")
    if bench_z is None or abs(bench_z - BENCH["top"]) > 0.01:
        pr.append(f"{HERO}: bench top {bench_z} not {BENCH['top']}")
    return rep, pr


def build(render=True, close=False, spin=False):
    return MODEL.run(hero=(HERO, hero_all), parts=PARTS, notes=NOTES, collision=COLLISION, budgets=BUDGETS,
                     target_size=TARGET_SIZE, points=POINTS, fx=FX, views=VIEWS, exploded=EXPLODED,
                     close=CLOSE if close else None, verify=VERIFY, checks=[workshop_check], render=render, spin=spin)


CLOSE = {"joint_cu": dict(at=(-PX, -PY, 9.9), r=2.2, az=-35, el=15),
         "hub_cu": dict(cam=(1.5, -2.5, 4.0), look=(0.0, 0.0, 12.6), lens=18.0),
         "bench_cu": dict(at=(-0.4, -3.9, 3.0), r=4.0, az=-30, el=25)}


def preview(names=("f34_sheet", "front_sheet", "rear_sheet")):
    return MODEL.preview(HERO, VIEWS, names)


def compare(cells=None, out_dir=None, height=360):
    import importlib
    import compare as C
    importlib.reload(C)
    return C.compare(NUM, {k: COMPARE[k] for k in (cells or COMPARE)}, out_dir=out_dir, height=height)
