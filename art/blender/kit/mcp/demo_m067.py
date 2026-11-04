"""067 Table and Seating (references/067.png) rebuilt on the shared library (kit_parts / kit_build): the demonstration
port of m067.py. Same model, same object names: a rugged trestle table set (a four-row top of chamfered planks with
staggered butt joints on two A-frame trestles, a crossbar with tenon stubs, two knee braces), two two-plank benches
and a three-plank stool; 30 dark slate square bolts. See m067.py and M067_spec.md for the design notes.

    import importlib, kit_parts, kit_build, demo_m067
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(demo_m067); demo_m067.build()

Build frame: studs, front -Y (the near bench), +X right, ground z 0, the table centred on x 0, y 0.
"""
import math

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_build as B
import kit_parts as P

NUM, TITLE = 67, "Table and Seating"
HERO = "TrestleTableSet"
TABLE_P, TOP_P, TRESTLE_P = "TrestleTableSetTable", "TrestleTableSetTop", "TrestleTableSetTrestle"
CROSS_P, BENCH_P, STOOL_P = "TrestleTableSetCrossbar", "TrestleTableSetBench", "TrestleTableSetStool"
WOOD, WOOD_LIGHT, WOOD_DEEP, IRON = "m067_wood", "m067_wood_light", "m067_wood_deep", "m067_iron"

PALETTE = {WOOD: ("#A66829", 0.8, 0.0, 0.0, True), WOOD_LIGHT: ("#D48F44", 0.8, 0.0, 0.0, True),
           WOOD_DEEP: ("#844A1A", 0.85, 0.0, 0.0, True), IRON: ("#49525F", 0.7, 0.25, 0.0, False)}
TARGETS = {WOOD: ((0xB8, 0x67, 0x1F), "brown"), WOOD_LIGHT: ((0xE5, 0x92, 0x41), "brown"),
           WOOD_DEEP: ((0x8E, 0x4A, 0x18), "brown"), IRON: ((0x47, 0x4E, 0x56), "all")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)

END_BAND = ((0.15, 0.45), (0.35, 0.25))         # (distance from the chosen plank end, t toward wood_deep)
LIGHT_BAND = ((0.35, 0.35), (0.65, 0.18))       # (distance from the streak centre, t toward wood_light)
LEG_BAND = (0.25, 0.30)                         # (height of the foot band, t toward wood_deep)
CH, PLANK_T = 0.04, 0.44


def mix(k1, k2, t):
    return P.mix(k1, k2, t, step=0.02)


# ---- planks, legs, members ---------------------------------------------------------------------------------------------
def plank(a, x0, x1, yc, zc, hw, name, light=None, end=None):
    """A plank along X (half width hw, 0.44 thick, chamfer 0.04): a darker band at one end (END_BAND) and optionally a
    lighter streak centred at x = light (LIGHT_BAND); rings only where a band edge falls."""
    L = x1 - x0
    cuts = set()
    if end is not None:
        sgn = 1 if end == x0 else -1
        cuts |= {round(end + sgn * d, 4) for d, _ in END_BAND if d < 0.45 * L}
    if light is not None:
        cuts |= {round(light + s * d, 4) for d, _ in LIGHT_BAND for s in (-1, 1)}
    st = [x - x0 for x in sorted(cuts) if x0 + 0.08 < x < x1 - 0.08]

    def colour(l):
        x = x0 + l.s
        if end is not None:
            for lim, t in END_BAND:
                if abs(x - end) < lim - 1e-6:
                    return mix(WOOD, WOOD_DEEP, t)
        if light is not None:
            for lim, t in LIGHT_BAND:
                if abs(x - light) < lim - 1e-6:
                    return mix(WOOD, WOOD_LIGHT, t)
        return WOOD
    return P.plank(a, (x0, yc, zc), (x1, yc, zc), 2 * hw, PLANK_T, WOOD, ch=CH, stations=st, colour=colour, name=name,
                   kind="plank")


def plank_bands(name, x0, x1, streak, end_band=True):
    """The seeded coin for a plank piece's darker end (or None) and its lighter streak centre (or None)."""
    r = P.rng(name)
    end = x0 if r.random() < 0.5 else x1
    light = None
    if streak and x1 - x0 > 2.0:
        light = max(x0 + 0.8, min(x1 - 0.8, (x0 + x1) / 2 + r.uniform(-0.2, 0.2) * (x1 - x0)))
        if end_band and abs(light - end) < END_BAND[-1][0] + LIGHT_BAND[-1][0] + 0.1:
            light = None
    return (end if end_band else None), light


def leg(a, foot, top, z1, hu, hv, name):
    zb, tb = LEG_BAND
    deep = mix(WOOD, WOOD_DEEP, tb)
    return P.leg(a, foot, top, z1, hu, hv, WOOD, ch=CH, zs=(zb,), colour=lambda c: deep if c.z < zb - 1e-6 else WOOD,
                 name=name, kind="leg")


def between(a, lo, hi, z0, z1, y_of, kind, name, axis="y"):
    """A plain member whose two ends lie on neighbouring slanted faces: section lo..hi by z0..z1, ends at y_of(z, -1)
    and y_of(z, +1) (axis "x": x and y swapped)."""
    sec = [(lo, z0), (hi, z0), (hi, z1), (lo, z1)]
    rings = [[(u, y_of(z, s), z) if axis == "y" else (y_of(z, s), u, z) for u, z in sec] for s in (-1, 1)]
    return P.prism(a, rings, WOOD, name=name, kind=kind)


def bolt(a, c, n, up, name):
    return P.bolt(a, c, n, up, IRON, name=name)


def lerp(foot, top, z1, z):
    t = z / z1
    return foot[0] + (top[0] - foot[0]) * t, foot[1] + (top[1] - foot[1]) * t


# ---- top ---------------------------------------------------------------------------------------------------------------
TOP_Z0, TOP_Z1, TOP_X, ROW_HW = 2.16, 2.60, 3.00, 0.33
ROWS = (1.08, 0.36, -0.36, -1.08)
JOINTS = {0: -1.92, 2: 2.10, 3: -0.84}
JOINT_GAP, END_JIT, END_MIN = 0.04, 0.03, 2.5


def top(a):
    zc = (TOP_Z0 + TOP_Z1) / 2
    for i, yc in enumerate(ROWS):
        r = P.rng(f"row{i}")
        xa, xb = -TOP_X + r.uniform(-END_JIT, END_JIT), TOP_X + r.uniform(-END_JIT, END_JIT)
        spans = P.butt_spans(xa, xb, [JOINTS[i]] if i in JOINTS else [], gap=JOINT_GAP)
        for k, (x0, x1) in enumerate(spans):
            nm = f"R{i + 1}{'ab'[k]}"
            end, light = plank_bands("top" + nm, x0, x1, False, end_band=x1 - x0 > END_MIN)
            plank(a, x0, x1, yc, zc, ROW_HW, "top_" + nm, light=light, end=end)
    for yc in (ROWS[0], ROWS[3]):
        for x in (-TR_X, TR_X):
            bolt(a, (x, yc, TOP_Z1), (0, 0, 1), (1, 0, 0), f"bolt_top_{x:+.1f}_{yc:+.2f}")


# ---- trestles ------------------------------------------------------------------------------------------------------------
TR_X = 2.20
CLEAT_HX, CLEAT_HY, CLEAT_Z0 = 0.225, 1.215, 1.86
CLEAT_ZC = (CLEAT_Z0 + TOP_Z0) / 2
LEG_HX, LEG_HY, LEG_TOP_Y, LEG_FOOT_Y = 0.25, 0.23, 0.86, 1.19
TIE_Z, TIE_HX = (0.40, 0.75), 0.17
TSTUB_HX, TSTUB_D, TSTUB_Z, PEG = 0.15, 0.25, (0.425, 0.725), 0.20
DIAG_HX, DIAG_W, DIAG_TOP_Y = 0.15, 0.34, 0.0


def leg_cy(z):
    return lerp((0.0, LEG_FOOT_Y), (0.0, LEG_TOP_Y), CLEAT_Z0, z)[1]


def diag_quad():
    """The diagonal's YZ outline: from the front leg's inner face at the tie top up to the cleat underside, its ends
    planar with the leg's face and level under the cleat."""
    zt = TIE_Z[1]
    k = (LEG_TOP_Y - LEG_FOOT_Y) / CLEAT_Z0

    def leg_in(z):
        return -(leg_cy(z) - LEG_HY)
    c0 = Vector((leg_in(zt), zt))
    y1 = 0.3
    for _ in range(40):
        th = math.atan2(CLEAT_Z0 - zt, y1 - c0.x)
        y1 += DIAG_TOP_Y - (y1 - (DIAG_W / 2) / math.sin(th))
    th = math.atan2(CLEAT_Z0 - zt, y1 - c0.x)
    d = Vector((math.cos(th), math.sin(th)))
    p = c0 + Vector((-d.y, d.x)) * DIAG_W
    s = 0.0
    for _ in range(60):
        q = p + d * s
        s += (leg_in(q.y) - q.x) / (d.x - (-k) * d.y) if abs(d.x + k * d.y) > 1e-9 else 0
    P.GEO["diag_angle"] = round(math.degrees(th), 2)
    return [c0, Vector((y1, CLEAT_Z0)), Vector((y1 - DIAG_W / math.sin(th), CLEAT_Z0)), p + d * s]


def trestle(a, sx):
    """One A-frame trestle at x = sx * TR_X: cleat, two splayed legs, tie, the tie's pegged through-tenon stub on the
    front leg, the diagonal and six bolts on the face away from the table."""
    xc = sx * TR_X
    for s, nm in ((-1, "front"), (1, "back")):
        leg(a, (xc, s * LEG_FOOT_Y), (xc, s * LEG_TOP_Y), CLEAT_Z0, LEG_HX, LEG_HY, f"leg_{nm}")
    sec = P.sec_rect(CLEAT_HX, (TOP_Z0 - CLEAT_Z0) / 2, CH)
    P.prism(a, [[(xc + u, y, CLEAT_ZC + v) for u, v in sec] for y in (-CLEAT_HY, CLEAT_HY)], WOOD, name="cleat",
            kind="cleat")
    between(a, xc - TIE_HX, xc + TIE_HX, *TIE_Z, lambda z, s: s * (leg_cy(z) - LEG_HY), "tie", "tie")
    zm = sum(TSTUB_Z) / 2
    y_out = -(leg_cy(zm) + LEG_HY + TSTUB_D)
    between(a, xc - TSTUB_HX, xc + TSTUB_HX, *TSTUB_Z, lambda z, s: -(leg_cy(z) + LEG_HY) if s > 0 else y_out, "stub",
            "tie_stub")
    yp1 = -(leg_cy(TSTUB_Z[1]) + LEG_HY) - 0.03
    P.box(a, (xc - PEG / 2, yp1 - PEG, TSTUB_Z[1]), (xc + PEG / 2, yp1, TSTUB_Z[1] + PEG), WOOD, name="peg", kind="peg")
    P.prism(a, [[(xc + s * DIAG_HX, p.x, p.y) for p in diag_quad()] for s in (-1, 1)], WOOD, name="diag", kind="diag")
    for s in (-1, 1):
        bolt(a, (xc, s * CLEAT_HY, CLEAT_ZC), (0, s, 0), (1, 0, 0), f"bolt_cleat_end{s:+d}")
        bolt(a, (xc + sx * CLEAT_HX, s * LEG_TOP_Y, CLEAT_ZC), (sx, 0, 0), (0, 0, 1), f"bolt_cleat_face{s:+d}")
        bolt(a, (xc + sx * LEG_HX, s * leg_cy(zm), zm), (sx, 0, 0), (0, 0, 1), f"bolt_leg{s:+d}")


# ---- crossbar and knee braces --------------------------------------------------------------------------------------------
CB_HY, CB_HZ, CB_X = 0.18, 0.15, TR_X - CLEAT_HX
CSTUB_HY, CSTUB_Z, CSTUB_L = 0.13, (1.89, 2.13), 0.30
KNEE_HY, KNEE_BOT, KNEE_TOP_C, KNEE_TOP_HW = 0.14, (2.03, 2.37), 1.00, 0.17


def crossbar(a, alone=False):
    """The crossbar between the cleats' inner faces and a bolted tenon stub past each cleat (alone: the stubs run
    through where the cleats would be, so the part is one chained piece)."""
    sec = P.sec_rect(CB_HY, CB_HZ, CH)
    P.prism(a, [[(x, u, CLEAT_ZC + v) for u, v in sec] for x in (-CB_X, CB_X)], WOOD, name="crossbar", kind="cross")
    x_out = TR_X + CLEAT_HX
    for s in (-1, 1):
        lo, hi = sorted((s * (CB_X if alone else x_out), s * (x_out + CSTUB_L)))
        P.box(a, (lo, -CSTUB_HY, CSTUB_Z[0]), (hi, CSTUB_HY, CSTUB_Z[1]), WOOD, name=f"cross_stub{s:+d}", kind="cstub")
        bolt(a, (s * (x_out + CSTUB_L), 0.0, sum(CSTUB_Z) / 2), (s, 0, 0), (0, 0, 1), f"bolt_cstub{s:+d}")


def knee(a, sx):
    zt, (b0, b1) = TIE_Z[1], KNEE_BOT
    q = [(sx * b0, zt), (sx * b1, zt), (sx * (KNEE_TOP_C + KNEE_TOP_HW), CLEAT_Z0),
         (sx * (KNEE_TOP_C - KNEE_TOP_HW), CLEAT_Z0)]
    P.GEO["knee_angle"] = round(math.degrees(math.atan2(CLEAT_Z0 - zt, (b0 + b1) / 2 - KNEE_TOP_C)), 2)
    P.prism(a, [[(x, s * KNEE_HY, z) for x, z in q] for s in (-1, 1)], WOOD, name=f"knee{sx:+d}", kind="knee")


# ---- benches and stool ---------------------------------------------------------------------------------------------------
BENCH_Y, BENCH_HL, SEAT_Z0, SEAT_Z1, SEAT_ROW_HW = 2.40, 2.90, 1.06, 1.50, 0.29
SEAT_ROWS, BENCH_JOINT = (0.31, -0.31), -2.03
BCLEAT_HX, BCLEAT_HY, BCLEAT_Z0 = 0.17, 0.55, 0.80
BLEG_X, BLEG_Y, BLEG_H, BLEG_SPLAY = 2.45, 0.36, 0.21, (5.0, 4.0)
BSTR_HX, BSTR_Z = 0.10, (0.30, 0.54)
STOOL_C, STOOL_HL, STOOL_SEAM = (-4.95, -1.30), 0.70, 0.03
STOOL_ROWS = ((-0.70, -0.26), (-0.24, 0.24), (0.26, 0.70))
SLEG_C, SLEG_H, SLEG_SPLAY = 0.47, 0.19, 7.0
APRON_T, APRON_IN, APRON_Z = 0.14, 0.05, (0.84, 1.06)
SSTR_HX, SSTR_Z = 0.07, (0.30, 0.50)


def bleg_c(sx, sy, z):
    fx = BLEG_X + BCLEAT_Z0 * math.tan(math.radians(BLEG_SPLAY[0]))
    fy = BLEG_Y + BCLEAT_Z0 * math.tan(math.radians(BLEG_SPLAY[1]))
    cx, cy = lerp((fx, fy), (BLEG_X, BLEG_Y), BCLEAT_Z0, z)
    return sx * cx, sy * cy


def bench(a):
    """One bench (centre 0, inner row toward +y): two seat planks (one butt joint), splayed leg frames with cleats and
    stretchers, four bolts."""
    zc = (SEAT_Z0 + SEAT_Z1) / 2
    for r, yc in enumerate(SEAT_ROWS):
        spans = ([("in_a", -BENCH_HL, BENCH_JOINT - JOINT_GAP / 2), ("in_b", BENCH_JOINT + JOINT_GAP / 2, BENCH_HL)]
                 if r == 0 else [("out", -BENCH_HL, BENCH_HL)])
        for nm, x0, x1 in spans:
            end, light = plank_bands(P.TAG[-1] + nm, x0, x1, nm == "out")
            plank(a, x0, x1, yc, zc, SEAT_ROW_HW, "seat_" + nm, light=light, end=end)
    for sx in (-1, 1):
        x = sx * BLEG_X
        P.box(a, (x - BCLEAT_HX, -BCLEAT_HY, BCLEAT_Z0), (x + BCLEAT_HX, BCLEAT_HY, SEAT_Z0), WOOD, name=f"bcleat{sx:+d}",
              kind="bcleat")
        for sy in (-1, 1):
            leg(a, bleg_c(sx, sy, 0.0), bleg_c(sx, sy, BCLEAT_Z0), BCLEAT_Z0, BLEG_H, BLEG_H, f"bleg{sx:+d}{sy:+d}")
        xm = bleg_c(sx, 1, sum(BSTR_Z) / 2)[0]
        between(a, xm - BSTR_HX, xm + BSTR_HX, *BSTR_Z, lambda z, s, sx=sx: s * (bleg_c(sx, 1, z)[1] - BLEG_H), "stretch",
                f"bstretch{sx:+d}")
        bolt(a, (x, 0.0, SEAT_Z1), (0, 0, 1), (1, 0, 0), f"bolt_seat{sx:+d}")
        bolt(a, (x, SEAT_ROWS[1] - SEAT_ROW_HW, zc), (0, -1, 0), (0, 0, 1), f"bolt_bface{sx:+d}")


def sleg_c(sx, sy, z):
    f = SLEG_C + SEAT_Z0 * math.tan(math.radians(SLEG_SPLAY))
    cx, cy = lerp((f, f), (SLEG_C, SLEG_C), SEAT_Z0, z)
    return sx * cx, sy * cy


def stool(a):
    """The stool turned a quarter (its seat planks run front to back): three planks (the middle one in two halves), four
    7 deg splayed legs, aprons on all sides, stretchers, a bolt on each seat side."""
    with P.frame(Matrix.Rotation(math.pi / 2, 4, "Z")):
        zc = (SEAT_Z0 + SEAT_Z1) / 2
        for r, (y0, y1) in enumerate(STOOL_ROWS):
            spans = P.butt_spans(-STOOL_HL, STOOL_HL, [0.0] if r == 1 else [], gap=STOOL_SEAM)
            for k, (x0, x1) in enumerate(spans):
                nm = f"seat{r}{'ab'[k]}"
                plank(a, x0, x1, (y0 + y1) / 2, zc, (y1 - y0) / 2, nm, end=plank_bands(P.TAG[-1] + nm, x0, x1, False)[0])
        for sx in (-1, 1):
            for sy in (-1, 1):
                leg(a, sleg_c(sx, sy, 0.0), sleg_c(sx, sy, SEAT_Z0), SEAT_Z0, SLEG_H, SLEG_H, f"sleg{sx:+d}{sy:+d}")
        yo = SLEG_C + SLEG_H - APRON_IN
        for s in (-1, 1):
            lo, hi = sorted((s * yo, s * (yo - APRON_T)))
            between(a, lo, hi, *APRON_Z, lambda z, e: e * (sleg_c(1, 1, z)[0] - SLEG_H), "apron", f"apron_y{s:+d}", "x")
            between(a, lo, hi, *APRON_Z, lambda z, e: e * (sleg_c(1, 1, z)[1] - SLEG_H), "apron", f"apron_x{s:+d}")
            xm = sleg_c(s, 1, sum(SSTR_Z) / 2)[0]
            between(a, xm - SSTR_HX, xm + SSTR_HX, *SSTR_Z, lambda z, e: e * (sleg_c(1, 1, z)[1] - SLEG_H), "stretch",
                    f"sstretch{s:+d}")
            bolt(a, (0.0, s * STOOL_HL, zc), (0, s, 0), (0, 0, 1), f"bolt_sy{s:+d}")
            bolt(a, (s * STOOL_HL, 0.0, zc), (s, 0, 0), (0, 0, 1), f"bolt_sx{s:+d}")


# ---- assemblies ------------------------------------------------------------------------------------------------------------
BENCHES = (("bench_f_", Matrix.Translation((0.0, -BENCH_Y, 0.0))),
           ("bench_b_", Matrix.Translation((0.0, BENCH_Y, 0.0)) @ Matrix.Rotation(math.pi, 4, "Z")))


def table_all(a):
    top(a)
    for sx, tg in ((-1, "trestle_l_"), (1, "trestle_r_")):
        with P.frame(None, tg):
            trestle(a, sx)
    crossbar(a)
    knee(a, -1)
    knee(a, 1)


def hero_all(a, with_stool=True):
    table_all(a)
    for tg, m in BENCHES:
        with P.frame(m, tg):
            bench(a)
    if with_stool:
        with P.frame(Matrix.Translation((STOOL_C[0], STOOL_C[1], 0.0)), "stool_"):
            stool(a)


PARTS = ((TABLE_P, table_all), (TOP_P, top), (TRESTLE_P, lambda a: trestle(a, 1)),
         (CROSS_P, lambda a: crossbar(a, alone=True)), (BENCH_P, bench), (STOOL_P, stool))
SEATS = {"m067_seat_f1": ((-1.20, -BENCH_Y, SEAT_Z1), (0, 1, 0)), "m067_seat_f2": ((1.20, -BENCH_Y, SEAT_Z1), (0, 1, 0)),
         "m067_seat_b1": ((-1.20, BENCH_Y, SEAT_Z1), (0, -1, 0)), "m067_seat_b2": ((1.20, BENCH_Y, SEAT_Z1), (0, -1, 0)),
         "m067_seat_stool": ((STOOL_C[0], STOOL_C[1], SEAT_Z1), (1, 0, 0))}
POINTS = {HERO: SEATS, TABLE_P: {k: v for k, v in SEATS.items() if "stool" not in k},
          BENCH_P: {"m067_seat_1": ((-1.20, 0.0, SEAT_Z1), (0, 1, 0)), "m067_seat_2": ((1.20, 0.0, SEAT_Z1), (0, 1, 0))},
          STOOL_P: {"m067_seat": ((0.0, 0.0, SEAT_Z1), (1, 0, 0))}}
NOTES = {
    HERO: "Trestle table set: a thick four-plank top (seven pieces, three butt joints) on two A-frame trestles (10 deg "
          "splay, cleat, low tie with a pegged through-tenon stub, diagonal), a crossbar under the top with tenon stubs "
          "past both trestles, two 42 deg knee braces, two two-plank benches on splayed leg frames, a three-plank stool "
          "at the front-left; 30 dark slate square bolts. Table top 2.60, seats 1.50; five seat points stored "
          "(m067_seat_*, with facings) for Studio Seat parts (Requires Manual Validation). Sheet header 69/132.",
    TABLE_P: "The table alone: top, two trestles, crossbar with stubs, two knee braces and their bolts (bench seat points "
             "stored relative to it)",
    TOP_P: "Table Top (Planks): four rows of 0.44 chamfered planks, seven pieces, four bolts",
    TRESTLE_P: "Leg / Trestle: cleat, two 10 deg splayed legs, low tie with a pegged through-tenon stub, diagonal, six "
               "bolts (the left trestle is the same mesh, translated)",
    CROSS_P: "Crossbar: chamfered beam with a tenon stub and bolt at each end",
    BENCH_P: "Bench Seat (Planks): two-plank seat (one butt joint) on two splayed leg frames with cleats and stretchers; "
             "two seat points stored",
    STOOL_P: "Stool: three-plank seat with a cross seam, four 7 deg splayed legs, aprons and stretchers; one seat point",
}
COLLISION = {HERO: "precise", TABLE_P: "box", TOP_P: "box", TRESTLE_P: "hull", CROSS_P: "box", BENCH_P: "box",
             STOOL_P: "box"}
TARGET_SIZE = ((8.75, 0.15), (6.10, 0.12), (2.67, 0.02))
VIEWS = {"front_sheet": (0, 0, "nostool"), "side_sheet": (90, 0), "rear_sheet": (180, 0, "nostool"),
         "f34_sheet": (-30, 20), "r34_sheet": (145, 20), "top_sheet": (0, 89.9)}
EXPLODED = {TOP_P: (0.0, 0.6, 4.4), TRESTLE_P: [(-3.6, 0.0, 0.6), (3.6, 0.0, 0.6)], CROSS_P: (0.0, -0.3, 2.3),
            BENCH_P: (1.8, -4.6, 0.0), STOOL_P: (-6.6, -2.6, 0.0)}
CLOSE = {"join_cu": dict(at=(2.45, -0.6, 1.9), r=0.95, az=35, el=12),
         "plank_cu": dict(at=(2.65, -1.15, 2.25), r=0.8, az=30, el=24),
         "stool_cu": dict(at=(STOOL_C[0], STOOL_C[1], 0.85), r=1.1, az=-35, el=20),
         "tie_cu": dict(cam=(-3.9, -1.75, 1.05), look=(-2.2, -1.40, 0.6), lens=30.0),
         "under_cu": dict(cam=(0.0, -1.1, 0.35), look=(0.0, 0.3, 2.2), lens=13.0)}


def seat_check(objs):
    """Spec 2.8: every seat point lies on a level plank top at 1.50 and the table top at 2.60; the knee room in front of
    each bench seat (a 1.2 x 1.2 box from the seat's inner edge toward the table, z 0-1.75) stays 0.10 clear of the
    table."""
    h = objs[HERO]
    me = h.data
    down = Vector((0, 0, -1))

    def z_at(o, tree, x, y):          # the top surface's height (build frame) under (x, y), off joints and seams
        hit = tree.ray_cast(MODEL.at(o, (x + 0.3, y + 0.2, 9.0)), down)[0]
        return round(hit.z - o.matrix_world.translation.z + o[MODEL.OFF][2], 3) if hit else None
    tree = BVHTree.FromPolygons([h.matrix_world @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])
    rep = {"seat_z": {k: z_at(h, tree, p[0], p[1]) for k, (p, _) in SEATS.items()}, "table_z": z_at(h, tree, 0.0, 0.16)}
    table = objs[TABLE_P]
    tt = BVHTree.FromPolygons([table.matrix_world @ v.co for v in table.data.vertices],
                              [list(p.vertices) for p in table.data.polygons])
    knee_ = {}
    for k, (p, f) in SEATS.items():
        if "stool" in k:
            continue
        edge = p[1] + f[1] * (SEAT_ROWS[0] + SEAT_ROW_HW)
        y0, y1 = sorted((edge, edge + f[1] * 1.2))
        pts = [Vector((p[0] + dx, y, z)) for dx in (-0.6, 0.0, 0.6) for y in (y0, (y0 + y1) / 2, y1)
               for z in (0.0, 0.6, 1.2, 1.75)]
        knee_[k] = round(min(tt.find_nearest(MODEL.at(table, q))[3] for q in pts), 3)
    rep["knee"] = knee_
    pr = [f"{HERO}: seat {k} top {z} not 1.50" for k, z in rep["seat_z"].items() if z is None or abs(z - SEAT_Z1) > 0.01]
    if rep["table_z"] is None or abs(rep["table_z"] - TOP_Z1) > 0.01:
        pr.append(f"{HERO}: table top {rep['table_z']} not 2.60")
    pr += [f"{HERO}: knee clearance {k} {d} under 0.10" for k, d in knee_.items() if d < 0.10]
    return rep, pr


def build(render=True, close=False):
    def after(objs):
        h = objs[HERO]
        h["m067_centre"] = [round(x, 4) for x in -Vector(h[MODEL.OFF])]
    return MODEL.run(hero=(HERO, hero_all), parts=PARTS, notes=NOTES, collision=COLLISION,
                     budgets={HERO: 4000}, target_size=TARGET_SIZE, points=POINTS, views=VIEWS, exploded=EXPLODED,
                     scale=(0.0, -4.6, 0.0), variants={"nostool": lambda a: hero_all(a, False)},
                     close=CLOSE if close else None, checks=[seat_check], after=after, render=render)


def preview(names=("front_sheet", "side_sheet", "f34_sheet")):
    return MODEL.preview(HERO, VIEWS, names, variants={"nostool": lambda a: hero_all(a, False)})
