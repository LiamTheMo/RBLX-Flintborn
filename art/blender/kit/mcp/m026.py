"""026 Softwood Log (references/026.png): a fallen softwood log lying on the ground. A long chunky 11-sided bark log
(L : D 2.9) whose bark is a patchwork of raised plates with step ledges and dark carved slits; one pale ringed cut end
at -X (flush, flat, a slight chamfer inside a thin bark rim) and a blunt faceted bark dome at +X with a knot hole; a
large branch stub standing up out of the top past the middle (leaning to +X and a little back) with a pale broken
top and a small knot nub at its -X foot; a small branch stub growing out of the lower front down to the ground with a
pale square-cut end; four bright six-leaf flat star clumps (two on the ground in front, one on the log's top-back near
+X, one on the ground behind).

    import importlib, kit_models, m026; importlib.reload(kit_models); importlib.reload(m026); m026.build()

Parts as on the sheet's Exploded Construction, each built by its own function, all in one build frame (studs; the
log axis along X, cut face at -X, front -Y, ground z = 0). R06 owns SoftwoodLog*, so the names are
FallenSoftwoodLog* (M026_spec.md section 8, decision 11):
- FallenSoftwoodLogTrunk (trunk_part): the log with its plates, slits, knot hole, dome and ringed flush face.
- FallenSoftwoodLogCutEnd (cut_end_part): the 0.38-thick 11-sided disc, the face's ring loops and chamfer.
- FallenSoftwoodLogBranchStubLarge (stub_large_part): the large stub with the knot nub at its foot.
- FallenSoftwoodLogBranchStubSmall (stub_small_part): the small stub with its square pale end.
- FallenSoftwoodLogLeafClump (clump_part): a flat six-leaf star.

The trunk is built first in a temporary object: a lofted 22-vertex-ring log whose raised plates are part of the
same surface (each plate's cells lifted with wall quads round it; no booleans), then the slits and the knot hole
carved one at a time (exact difference). The hero (FallenSoftwoodLog) is that trunk + the two stubs + the knot + four
clumps, one exact union (merge 0), a floor cut at the ground, the guarded sliver cleanup. Colour (stage 4) is painted
by position fields inside the builders (the cutters carry the slit colour); the union and cleanup keep each face's
key and Tint. See M026_spec.md.
"""
import math
import random
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M
import m011
import m012
import m016

NUM, TITLE, SHEET = 26, "Softwood Log", "M026"
OFF = "m026_offset"
PFX = "_m026_"
HERO = "FallenSoftwoodLog"

BARK, BARK_LIGHT, BARK_DARK = "m026_bark", "m026_bark_light", "m026_bark_dark"
CUT, CUT_LIGHT, CUT_RING, CUT_EDGE = "m026_cut", "m026_cut_light", "m026_cut_ring", "m026_cut_edge"
# the large stub's broken top: the sheet's palest wood in every view, the unshadowed exploded cell included
# (#FCDDAE against the insert face's #DFB88A), so a painted region key of its own, calibrated on the hero render
# where the cap is sun-lit as on the sheet (not a facing compensation)
CUT_TOP = "m026_cut_top"
LEAF, LEAF_TIP, LEAF_BASE = "m026_leaf", "m026_leaf_tip", "m026_leaf_base"
# the log's own cut face (and the CutEnd disc): the same wood as the cut keys, calibrated on the views where the
# face is seen (it faces away from the studio sun, so it takes brighter keys than the sun-lit stub tops)
FACE_LIGHT, FACE_RING, FACE_EDGE = "m026_face_light", "m026_face_ring", "m026_face_edge"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low_spec); the comment is the calibration target (spec 5.4)
# Stage 4 pass 1 (K.calibrate on the kit dome, 2026-10-28): rendered medians bark (138,93,66), bark_light
# (148,100,74), bark_dark (94,65,49), cut (222,175,121), cut_light (240,201,151), cut_ring (231,177,120), cut_edge
# (247,214,168), leaf (100,162,29), leaf_tip (112,174,32), leaf_base (76,138,25).
PALETTE = {BARK: ("#674631", 0.9, False),            # #85583E; pass 2 x0.88 (f34 median)
           BARK_LIGHT: ("#986B50", 0.9, False),      # #94654A; pass 2 x1.75 (lit plates)
           BARK_DARK: ("#4A3224", 0.95, False),      # #5E402E
           CUT: ("#AF8F68", 0.85, False),            # #DFAF79
           CUT_LIGHT: ("#BDA482", 0.85, False),      # #F0C997
           CUT_RING: ("#B69167", 0.85, False),       # #E7B278
           CUT_EDGE: ("#C2AE90", 0.85, False),       # #F6D6A8
           CUT_TOP: ("#C6BAA4", 0.85, False),        # round 2: stub tops #FDE7C2 (f34) / #FCDDAE (exploded)
           LEAF: ("#538A16", 0.8, True),             # #63A21E; round 2: sat up (f34 median sat >= 0.78)
           LEAF_TIP: ("#79B416", 0.8, True),         # #70AE21; pass 2 x1.56; round 2 less blue (lit #82BC22)
           LEAF_BASE: ("#356414", 0.8, True),        # #4B8A19; pass 2 x0.85; round 2 -10 % (f34 shade #2F5F14)
           FACE_LIGHT: ("#DCBF99", 0.85, False),     # side_sheet face light bands #F0C998
           FACE_RING: ("#D4AA79", 0.85, False),      # side_sheet pith / ring #E7B278
           FACE_EDGE: ("#E2CBA8", 0.85, False)}      # chamfer (insert lit edge #FBD19A)

TARGETS = {BARK: ((0x85, 0x58, 0x3E), "brown"), BARK_LIGHT: ((0x94, 0x65, 0x4A), "brown"),
           BARK_DARK: ((0x5E, 0x40, 0x2E), "brown"),
           CUT: ((0xDF, 0xAF, 0x79), "all"), CUT_LIGHT: ((0xF0, 0xC9, 0x97), "all"),
           CUT_RING: ((0xE7, 0xB2, 0x78), "all"), CUT_EDGE: ((0xF6, 0xD6, 0xA8), "all"),
           LEAF: ((0x63, 0xA2, 0x1E), "green"), LEAF_TIP: ((0x70, 0xAE, 0x21), "green"),
           LEAF_BASE: ((0x4B, 0x8A, 0x19), "green")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome. "all" keys are sampled with the
    paper / floor dropped (M.sample). Returns {key: (hex, rendered)} and leaves the keys set."""
    keys = keys or list(TARGETS)
    sample0 = K.sample

    def sample(src, box, kind="green"):
        return M.sample(src, box, "all", paper=(242, 238, 230), tol=14) if kind == "all" else sample0(src, box, kind)
    K.sample = sample
    try:
        for k in keys:
            K.fk().material(k)
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        K.sample = sample0
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


# ---- small helpers ---------------------------------------------------------------------------------------------------
STEPS = 4      # 25 / 50 / 75 % in-between keys


def _q(t):
    return round(min(1.0, max(0.0, t)) * STEPS) / STEPS


def _mix(k1, k2, t):
    return K.mix_key(k1, k2, _q(t))


def _mottle(a, faces, amp, scale, seed, jitter=0.0):
    """Broad Tint patches about 1/scale studs across, multiplied into each face's Tint (never per-face confetti)."""
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in faces:
        if not f.is_valid:
            continue
        k = 1.0 + amp * 1.6 * noise.noise(f.calc_center_median() * scale + off) + \
            (rng.uniform(-jitter, jitter) if jitter else 0.0)
        for l in f.loops:
            t = l[a.tint_layer][0] * k
            l[a.tint_layer] = (t, t, t, 1.0)


def _faces(verts):
    return K.faces_of([v for v in verts if v.is_valid])


def _tri(bm, faces):
    bmesh.ops.triangulate(bm, faces=[f for f in faces if f.is_valid and len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")


def _fan(bm, ring, c, flip=False):
    n = len(ring)
    return [bm.faces.new((ring[(k + 1) % n], ring[k], c) if not flip else (ring[k], ring[(k + 1) % n], c))
            for k in range(n)]


def _strip(bm, r0, r1):
    n = len(r0)
    return [bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k])) for k in range(n)]


def _wrap(t):
    return (t + math.pi) % (2 * math.pi) - math.pi


def _zip(bm, A, B, ang):
    """Triangles between two closed loops (both running the same way round by ang(v)): the zipper advances on
    whichever loop's next vertex comes first by angle. len(A) + len(B) triangles (m020's zipper, any plane)."""
    a0 = ang(A[0])
    k = min(range(len(B)), key=lambda j: abs(_wrap(ang(B[j]) - a0)))
    B = B[k:] + B[:k]

    def angles(L):
        out, prev = [], None
        for v in L:
            t = _wrap(ang(v) - a0)
            if prev is not None:
                while t < prev:
                    t += 2 * math.pi
            out.append(t)
            prev = t
        return out + [out[0] + 2 * math.pi]
    ta, tb = angles(A), angles(B)
    nA, nB = len(A), len(B)
    i = j = 0
    fs = []
    while i < nA or j < nB:
        if j >= nB or (i < nA and ta[i + 1] <= tb[j + 1]):
            fs.append(bm.faces.new((A[i], A[(i + 1) % nA], B[j % nB])))
            i += 1
        else:
            fs.append(bm.faces.new((A[i % nA], B[(j + 1) % nB], B[j])))
            j += 1
    return fs


def _perp(t):
    a = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
    return (a - t * a.dot(t)).normalized()


# ---- the log frame (spec 1.1, 1.4) ---------------------------------------------------------------------------------------
NSIDE, NV, NST = 11, 22, 11          # 11 stations, 0.875 apart (spec: 12, about 0.8; one fewer pays for the plates)
X_FACE, X_RIM, X_LAST, X_TIP = -4.65, -4.55, 4.20, 4.65
LOG_L = X_TIP - X_FACE
R0, R9 = 1.6, 1.45                    # radius at the cut end and at t 0.9 (linear taper between)
SINK = 0.06                           # the log's lowest face sinks this far below the ground before the floor cut
FLAT = 0.96                           # the bottom face's distance from the axis, x the radius (a face lies on the ground)
RIM = 0.13                            # bark rim width round the cut face
CHAMFER = (0.92, 0.10)                # the chamfer's inner loop (fraction of the face radius) and depth (studs)
FACE_LOOPS = ((0.62, 11), (0.40, 10), (0.20, 8))     # ring loops inside the chamfer: (fraction, verts)
TRUNK = dict(seed=26001, outline=0.04, rjit=0.03, mid=(-0.005, 0.03), twist=5.0, ajit=0.08, flip=0.3, phase=90.0)
DOME = ((0.17, 0.90, 11), (0.32, 0.70, 8), (0.42, 0.40, 5))    # (x past X_LAST, radius fraction, verts)
DOME_JIT = 0.05


def t_of(x):
    return (x - X_FACE) / LOG_L


def radius(x):
    return R0 + (R9 - R0) * min(1.0, max(0.0, t_of(x) / 0.9))


def axis_z(x):
    """The log axis is level: its lowest face lies on the ground at the cut end; the taper lifts the far end's
    underside a little off the ground (the sheet's bottom profile rises toward the dome)."""
    return R0 * FLAT - SINK


def dirn(th):
    """Radial direction at angle th (radians) round the X axis: 90 deg = up, 180 deg = front (-Y), 0 = back."""
    return Vector((0.0, math.cos(th), math.sin(th)))


def point(x, th, r):
    return Vector((x, 0.0, axis_z(x))) + dirn(th) * r


def theta_of(p):
    return math.atan2(p.z - axis_z(p.x), p.y)


GRID = {}


def _grid():
    """The trunk's 12 stations of 22 vertices (11 corners, a vertex in the middle of each face): positions and
    angles, deterministic. Cached in GRID."""
    if GRID:
        return GRID
    rng = random.Random(TRUNK["seed"])
    outl = [rng.uniform(1 - TRUNK["outline"], 1 + TRUNK["outline"]) for _ in range(NSIDE)]
    xs = [X_RIM + i * (X_LAST - X_RIM) / (NST - 1) for i in range(NST)]
    ph = math.radians(TRUNK["phase"])
    rows = []
    for i, x0 in enumerate(xs):
        tw = math.radians(rng.uniform(-TRUNK["twist"], TRUNK["twist"])) if i else 0.0
        corners = []
        for k in range(NSIDE):
            th = ph + 2 * math.pi * k / NSIDE + tw
            r = radius(x0) * outl[k] * (1 + rng.uniform(-TRUNK["rjit"], TRUNK["rjit"]))
            x = x0 + (rng.uniform(-1, 1) * TRUNK["ajit"] if 0 < i < NST - 1 else 0.0)
            corners.append((x, th, r))
        row = []
        for k in range(NSIDE):
            x, th, r = corners[k]
            x2, th2, r2 = corners[(k + 1) % NSIDE]
            if k == NSIDE - 1:
                th2 += 2 * math.pi
            p, q = point(x, th, r), point(x2, th2, r2)
            m = (p + q) / 2
            thm = (th + th2) / 2 + math.radians(rng.uniform(-2.0, 2.0))
            dm = (m - Vector((m.x, 0.0, axis_z(m.x)))).length
            rm = dm * (1 + rng.uniform(*TRUNK["mid"]))
            row.append((p, th, r))
            row.append((point(m.x, thm, rm), thm, rm))
        rows.append(row)
    GRID.update(rows=rows, xs=xs, outl=outl, ph=ph)
    return GRID


# ---- plates and slits (decision 5) -----------------------------------------------------------------------------------------
# slits: (x centre, angle deg, bands, width scale). Each is a V-groove opened along one of the grid's lengthwise
# column lines (the line's vertices split into a low-side, a high-side and a bottom copy; a midpoint on every band),
# pointed at both ends: 0.12 wide at the surface and 0.10 deep at its middle. >= 6 on the front / top half
# (90-235 deg, the hero's side); the long one low on the front at t .4-.65.
SLITS = ((-3.30, 160.0, 2, 1.0), (-2.45, 207.0, 2, 1.0), (-1.45, 122.0, 1, 0.9), (0.55, 222.0, 3, 1.0),
         (1.95, 150.0, 2, 1.0), (2.85, 196.0, 2, 0.9), (3.30, 114.0, 1, 0.9), (-1.20, 40.0, 2, 1.0),
         (2.00, 18.0, 2, 1.0))
SLIT = dict(width=0.12, depth=0.10, wpow=0.8, dpow=0.6)
# round 2: the hole moved 0.85 toward -X (was x 3.85) to leave the crest at x 3.7 for the BR clump's hub
KNOT_HOLE = dict(x=3.0, th=96.0, r=0.175, depth=0.12, above=0.08, seed=26011)

# stubs (spec section 2)
# top_n: the end cut's normal in the build frame (round 2, verifier B1 / B2): the large stub's broken top is aimed
# mostly up and about 25 deg to the front, so the hero camera sees the broad pale cap the sheet draws; the small
# stub's end is slanted up toward the camera and the sun (geometry, not a brighter key)
STUB_L = dict(x=1.05, th=80.0, lean=(35.0, 3.0), length=2.0, r=(0.56, 0.48), bury=0.5, seed=26021,
              top_n=(0.05, -0.40, 0.91), jag=0.04, chip=0.10, lip=0.88, st=(0.38, 0.62))
STUB_S = dict(x=-2.05, th=200.0, yaw=10.0, pitch=12.0, length=2.1, r=(0.5, 0.45), bury=0.45, seed=26022, lip=0.9,
              top_n=(0.25, -0.80, 0.55), st=(0.34, 0.56))
KNOT = dict(x=-0.15, th=100.0, lean=40.0, r=0.42, out=0.68, bury=0.35, seed=26023)
KNOT_TIP = 0.35         # the pale tip's radius, x the knot's radius
STUB_FLARE, STUB_RJIT, STUB_WOBBLE = 1.14, 0.08, 0.05
# round 2 (B1 / B2): the end cuts' keys by region, no facing compensation. The large stub's broken top is the
# sheet's palest wood (#FDE7C2, paler than the cut face): cut_edge with a cut_light pith. The small stub's end is the
# Cut Wood swatch (#E2B37F): cut with a cut_ring pith (spec 5.5)
LARGE_TOP = (CUT_TOP, None)            # pith: half way to cut_ring (the sheet's slightly darker pith)
SMALL_END = ((CUT, CUT_LIGHT, 0.25), CUT_RING)     # a 25 % step of cut toward cut_light, cut_ring pith


def _small_end():
    k1, k2, t = SMALL_END[0]
    return _mix(k1, k2, t), SMALL_END[1]
STUB_FOOT = 0.18       # the flared ring this far out along the stub: a ring lying on the bark left a sliver

PLATE = dict(seed=26031, count=14, tries=1500, levels=(0.07, 0.10), bands=(1, 2, 2, 3), cols=(2, 3, 3, 4),
             bottom=(228.0, 312.0), stub_clear=0.95, knot_clear=0.75, hole_clear=0.45)
PLATE_SHIFT = 0.3       # the most a plate's end slides inward along the log at one column (studs)
# the two short step ledges on the top near the cut end (spec 1.4): (band, first half-column angle deg, width)
LEDGES = ((0, 100.0, 2), (0, 145.0, 2))


def _cell_centre(i, j):
    rows = GRID["rows"]
    ps = [rows[i][j][0], rows[i][(j + 1) % NV][0], rows[i + 1][j][0], rows[i + 1][(j + 1) % NV][0]]
    return sum(ps, Vector()) / 4


def _cell_angle(i, j):
    return math.degrees(theta_of(_cell_centre(i, j))) % 360.0


def _surface_dist(c, x, th_deg):
    """Distance on the surface (about) from point c to the point at (x, th) on the log."""
    p = point(x, math.radians(th_deg), radius(x))
    return (c - p).length


def slit_lines():
    """Each slit as (column line j, first station i0, last station i1, width scale), and the open points: GRID["open"]
    {(kind, i, j): (half width, depth)} (kind "v" a grid vertex, "m" the midpoint of band i on the column line),
    GRID["mids"] the midpoints. The two ends stay closed (width 0)."""
    G = _grid()
    if "slits" in G:
        return G["slits"]
    sp = (X_LAST - X_RIM) / (NST - 1)
    out, opens, mids = [], {}, set()
    for xc, ang, nb, ws in SLITS:
        i0 = int(round((xc - X_RIM) / sp - nb / 2.0))
        i0 = max(1, min(NST - 2 - nb, i0))
        i1 = i0 + nb
        im = (i0 + i1) // 2
        j = min(range(NV), key=lambda j: abs(_wrap(G["rows"][im][j][1] - math.radians(ang))))
        out.append((j, i0, i1, ws))
        pts = []
        for i in range(i0, i1):
            pts += [("v", i, j), ("m", i, j)]
            mids.add(("m", i, j))
        pts.append(("v", i1, j))
        N = len(pts)
        for k, p in enumerate(pts):
            s = math.sin(math.pi * k / (N - 1))
            opens[p] = (SLIT["width"] / 2 * ws * s ** SLIT["wpow"], SLIT["depth"] * s ** SLIT["dpow"]) \
                if 0 < k < N - 1 else (0.0, 0.0)
    G.update(slits=out, open=opens, mids=mids)
    return out


def plates():
    """The raised bark plates: {cell (band, half-column): level}. Two step ledges on the top near the cut end, then
    seeded rectangles 1-3 bands x 2-4 half-columns, never touching another plate (not even at a corner), clear of the
    ground strip, the stub and knot feet, the slits and the knot hole. Cached in GRID."""
    _grid()
    if "plates" in GRID:
        return GRID["plates"]
    rng = random.Random(PLATE["seed"])
    P = PLATE
    cells, info = {}, []
    feet = [(STUB_L["x"], STUB_L["th"], P["stub_clear"]), (KNOT["x"], KNOT["th"], P["knot_clear"]),
            (STUB_S["x"], STUB_S["th"], P["stub_clear"]), (KNOT_HOLE["x"], KNOT_HOLE["th"], P["hole_clear"])]
    blocked = set()          # the cells either side of every slit, and one more cell round them
    for j, i0, i1, ws in slit_lines():
        for i in range(i0, i1):
            for jj in range(j - 2, j + 2):
                blocked.add((i, jj % NV))

    def ok(i0, nb, j0, nc):
        if i0 < 0 or i0 + nb > NST - 1:
            return False
        for i in range(i0, i0 + nb):
            for jj in range(j0, j0 + nc):
                j = jj % NV
                ang = _cell_angle(i, j)
                if P["bottom"][0] <= ang <= P["bottom"][1]:
                    return False
                c = _cell_centre(i, j)
                for x, th, d in feet:
                    if _surface_dist(c, x, th) < d:
                        return False
                if (i, j) in blocked:
                    return False
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        if (i + di, (j + dj) % NV) in cells:
                            return False
        return True

    def jcol(deg, i):
        rows = GRID["rows"]
        return min(range(NV), key=lambda j: abs(_wrap(math.radians(_cell_angle(i, j)) - math.radians(deg))))

    for band, deg, nc in LEDGES:
        j0 = jcol(deg, band)
        if ok(band, 1, j0, nc):
            lv = P["levels"][0]
            for jj in range(j0, j0 + nc):
                cells[(band, jj % NV)] = lv
            info.append((band, 1, j0, nc, lv))
    t = 0
    while len(info) < P["count"] + len(LEDGES) and t < P["tries"]:
        t += 1
        nb = rng.choice(P["bands"])
        nc = rng.choice(P["cols"])
        i0 = rng.randrange(1, NST - 1)
        j0 = rng.randrange(NV)
        if not ok(i0, nb, j0, nc):
            continue
        lv = rng.choice(P["levels"])
        for i in range(i0, i0 + nb):
            for jj in range(j0, j0 + nc):
                cells[(i, jj % NV)] = lv
        info.append((i0, nb, j0, nc, lv))
    GRID["plates"] = cells
    GRID["plate_info"] = info
    # round 2 (verifier minor 6): each seeded plate's two end walls slide inward along the log by a different amount
    # at each column (a diagonal end, 0..PLATE_SHIFT), so plate ends don't line up on the station rings round the log.
    # Only the raised copies move, so the end wall becomes a short ramp; the ledges at the cut end keep their step.
    srng = random.Random(P["seed"] + 7)
    shift = {}
    for (i0, nb, j0, nc, lv) in info[len(LEDGES):]:
        smax = PLATE_SHIFT if nb > 1 else PLATE_SHIFT * 0.7
        for ring, sgn in ((i0, 1.0), (i0 + nb, -1.0)):
            if ring <= 0 or ring >= NST - 1:
                continue
            sa, sb = srng.uniform(0.0, smax), srng.uniform(0.0, smax)
            for c in range(nc + 1):
                shift[(ring, (j0 + c) % NV, lv)] = sgn * (sa + (sb - sa) * c / nc)
    GRID["plate_shift"] = shift
    return cells


# ---- trunk ------------------------------------------------------------------------------------------------------------------
BARK_FIELD = dict(patch_scale=0.55, patch_level=0.05, patch_mix=0.75, plate_light=0.0, plate_frac=0.4, seed=26041)
BARK_MOTTLE = dict(amp=0.045, scale=0.6, seed=26042, jitter=0.006)
RIM_KEY_T = 0.5                     # the bark rim on the cut end: half way to bark_dark (end grain of the bark)
CUT_BANDS = ((0.20, FACE_RING), (0.40, FACE_LIGHT), (0.62, FACE_RING), (CHAMFER[0], FACE_LIGHT))   # (outer edge, key)
CUT_MOTTLE = dict(amp=0.02, scale=0.7, seed=26051)
PATCH_RAMP = 0.08


def _patch(n, F):
    lv = F["patch_level"]
    if n > lv + PATCH_RAMP:
        return F["patch_mix"]
    if n > lv:
        return min(0.5, F["patch_mix"])
    if n > lv - PATCH_RAMP:
        return 0.25
    return 0.0


def _face_loops(bm, centre, angf, to_world, R_face, rng):
    """The cut face's loops from the chamfer inwards: (fraction 0.92 / 0.62 / 0.40 / 0.20) each a closed loop of
    verts made by to_world(angle, radius); the 0.92 and 0.62 loops follow the outline's 11 corners (with the outline
    radius), the inner loops are rounder 10 / 8-gons. Returns (loops, centre vert)."""
    G = _grid()
    corners = [(G["rows"][0][2 * k][1], G["outl"][k]) for k in range(NSIDE)]
    loops = []
    for fr, n in ((CHAMFER[0], NSIDE),) + FACE_LOOPS:
        L = []
        if n == NSIDE:
            for th, o in corners:
                L.append(bm.verts.new(to_world(th, R_face * fr * o * rng.uniform(0.985, 1.015))))
        else:
            ph = rng.uniform(0, 2 * math.pi / n)
            for k in range(n):
                th = G["ph"] + ph + 2 * math.pi * k / n
                o = 1.0 + (sum(c[1] for c in corners) / NSIDE - 1.0)
                L.append(bm.verts.new(to_world(th, R_face * fr * o * rng.uniform(0.96, 1.04))))
        loops.append(L)
    c = bm.verts.new(to_world(0.0, 0.0) + centre)
    return loops, c


def _paint_face(a, bands):
    """bands: [(faces, key)] from the outside in; each band a flat key, the mottle very light (no texture noise)."""
    allf = []
    for fs, key in bands:
        mi = a._mi(key)
        for f in fs:
            f.material_index = mi
        allf += fs
    _mottle(a, allf, CUT_MOTTLE["amp"], CUT_MOTTLE["scale"], CUT_MOTTLE["seed"])


def trunk_raw(a):
    """The log as one closed surface: 12 stations of 22 vertices from the bark rim at the cut end to the start of
    the dome; raised plates lifted out of the same surface (each plate's cells use lifted copies of their corner
    verts, wall quads round the plate's edge); the bark rim annulus, the chamfer and the flat ringed face at -X; the
    blunt faceted dome at +X. Painted by position. Returns verts."""
    G = _grid()
    cells = plates()
    sl = slit_lines()
    opens, mids = G["open"], G["mids"]
    rng = random.Random(TRUNK["seed"] + 1)
    bm = a.bm
    rows = G["rows"]

    def level(i, j):
        if i < 0 or i > NST - 2:
            return 0.0
        return cells.get((i, j % NV), 0.0)
    copies = {}

    def vert(i, j, lv, side=None, kind="v"):
        """The copy of grid point (kind, i, j) for a cell at level lv; on an open slit point, side picks the low-
        angle edge ("lo"), the high-angle edge ("hi") or the groove bottom ("bot")."""
        j %= NV
        o = opens.get((kind, i, j))
        if o is None or o[0] <= 0:
            side = None
        key = (kind, i, j, lv, side)
        if key not in copies:
            if kind == "v":
                p, th, _ = rows[i][j]
            else:
                p = (rows[i][j][0] + rows[i + 1][j][0]) / 2
                th = theta_of(p)
            n = dirn(th)
            q = p + n * lv
            if kind == "v" and lv:
                q = q + Vector((G["plate_shift"].get((i, j, lv), 0.0), 0.0, 0.0))
            tg = Vector((0.0, -math.sin(th), math.cos(th)))
            if side == "lo":
                q = q - tg * o[0]
            elif side == "hi":
                q = q + tg * o[0]
            elif side == "bot":
                q = q - n * o[1]
            copies[key] = bm.verts.new(q)
        return copies[key]
    side, tops, walls, groove = [], [], [], []
    top_cell = {}
    for i in range(NST - 1):
        for j in range(NV):
            lv = level(i, j)
            flip = rng.random() < TRUNK["flip"]
            poly = [vert(i, j, lv, "hi"), vert(i, j + 1, lv, "lo")]
            if ("m", i, (j + 1) % NV) in mids:
                poly.append(vert(i, j + 1, lv, "lo", "m"))
            poly += [vert(i + 1, j + 1, lv, "lo"), vert(i + 1, j, lv, "hi")]
            if ("m", i, j) in mids:
                poly.append(vert(i, j, lv, "hi", "m"))
            if len(poly) == 4:
                a_, b_, c_, d_ = poly
                if flip:
                    fs = [bm.faces.new((a_, b_, d_)), bm.faces.new((b_, c_, d_))]
                else:
                    fs = [bm.faces.new((a_, b_, c_)), bm.faces.new((a_, c_, d_))]
            else:
                f = bm.faces.new(poly)
                fs = [x for x in bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY",
                                                       ngon_method="BEAUTY")["faces"]]
            (tops if lv else side).extend(fs)
            if lv:
                for f in fs:
                    top_cell[f] = (i, j)
    # the slits' grooves: two walls down to the bottom line between consecutive open points (closed ends)
    for j, i0, i1, ws in sl:
        pts = []
        for i in range(i0, i1):
            pts += [("v", i), ("m", i)]
        pts.append(("v", i1))
        lv = level(i0, j)
        cp = lambda p, s: vert(p[1], j, lv, s, p[0])
        for p, q in zip(pts, pts[1:]):
            for quad in ((cp(p, "lo"), cp(q, "lo"), cp(q, "bot"), cp(p, "bot")),
                         (cp(p, "bot"), cp(q, "bot"), cp(q, "hi"), cp(p, "hi"))):
                u = []
                for v in quad:
                    if v not in u:
                        u.append(v)
                if len(u) >= 3:
                    groove.append(bm.faces.new(u))
    gt = bmesh.ops.triangulate(bm, faces=[f for f in groove if len(f.verts) > 3], quad_method="BEAUTY",
                               ngon_method="BEAUTY")["faces"]
    groove = [f for f in groove if f.is_valid] + list(gt)
    # walls: every grid edge whose two cells differ in level
    for i in range(NST):
        for j in range(NV):
            # ring edge (i, j)-(i, j+1) between cells (i-1, j) and (i, j)
            l0, l1 = level(i - 1, j), level(i, j)
            if l0 != l1:
                lo, hi = min(l0, l1), max(l0, l1)
                walls.append(bm.faces.new((vert(i, j, lo), vert(i, j + 1, lo), vert(i, j + 1, hi), vert(i, j, hi))))
            # station edge (i, j)-(i+1, j) between cells (i, j-1) and (i, j)
            if i < NST - 1:
                l0, l1 = level(i, j - 1), level(i, j)
                if l0 != l1:
                    lo, hi = min(l0, l1), max(l0, l1)
                    walls.append(bm.faces.new((vert(i, j, lo), vert(i + 1, j, lo), vert(i + 1, j, hi),
                                               vert(i, j, hi))))
    # cut end: the bark rim annulus (ring 0 -> the face edge, in the X_RIM plane), the chamfer, the ring loops
    ring0 = [vert(0, j, 0.0) for j in range(NV)]
    yz = lambda v: math.atan2(v.co.z - axis_z(v.co.x), v.co.y)
    edge = [bm.verts.new(point(X_RIM, rows[0][2 * k][1], rows[0][2 * k][2] * (R0 - RIM) / R0))
            for k in range(NSIDE)]
    rim = _zip(bm, ring0, edge, yz)
    R_face = R0 - RIM
    frng = random.Random(TRUNK["seed"] + 2)
    loops, centre = _face_loops(bm, Vector((0, 0, 0)), yz,
                                lambda th, r: point(X_FACE, th, r), R_face, frng)
    chamfer = _zip(bm, edge, loops[0], yz)
    bands = []
    for l0, l1 in zip(loops, loops[1:]):
        bands.append(_zip(bm, l0, l1, yz))
    bands.append(_fan(bm, loops[-1], centre))
    # dome
    last = [vert(NST - 1, j, 0.0) for j in range(NV)]
    drng = random.Random(TRUNK["seed"] + 3)
    prev = last
    dome = []
    for dx, fr, n in DOME:
        x = X_LAST + dx
        ring = []
        for k in range(n):
            if n == NSIDE:
                _, th, r = rows[NST - 1][2 * k]
            else:
                th = G["ph"] + 2 * math.pi * k / n + 0.3
                r = radius(X_LAST)
            ring.append(bm.verts.new(point(x + drng.uniform(-0.03, 0.03), th + drng.uniform(-0.05, 0.05),
                                           r * fr * (1 + drng.uniform(-DOME_JIT, DOME_JIT)))))
        dome += _zip(bm, prev, ring, yz)
        prev = ring
    apex = bm.verts.new(point(X_TIP, 0.0, 0.0) + Vector((0, 0.04, 0.05)))
    dome += _fan(bm, prev, apex)
    verts = list({v for f in side + tops + walls + groove + rim + chamfer + dome + [f for b in bands for f in b]
                  for v in f.verts})
    a._finish(verts, BARK)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(verts))
    _paint_trunk(a, side + dome, tops, walls, rim, top_cell)
    mi = a._mi(BARK_DARK)
    for f in groove:
        f.material_index = mi
    _paint_face(a, [(chamfer, FACE_EDGE)] + [(b, CUT_BANDS[len(CUT_BANDS) - 1 - k][1]) for k, b in enumerate(bands)])
    return verts


def _paint_trunk(a, side, tops, walls, rim, top_cell):
    """Bark by position: broad noise patches stepping 25 % -> 50 % toward bark_light (never single faces); about 40 %
    of the plates (whole plates, by seed) a further step lighter; the cut end's bark rim half way to bark_dark."""
    F = BARK_FIELD
    nf = K.noise_field(scale=F["patch_scale"], seed=F["seed"])
    rng = random.Random(F["seed"] + 1)
    plate_of = {}
    for k, (i0, nb, j0, nc, lv) in enumerate(GRID["plate_info"]):
        for i in range(i0, i0 + nb):
            for jj in range(j0, j0 + nc):
                plate_of[(i, jj % NV)] = k
    light = {k for k in range(len(GRID["plate_info"])) if rng.random() < F["plate_frac"]}
    for f in side + tops + walls:
        t = _patch(nf(f.calc_center_median()), F)
        if f in top_cell and plate_of.get(top_cell[f]) in light:
            t = min(1.0, t + F["plate_light"])
        if _q(t):
            f.material_index = a._mi(_mix(BARK, BARK_LIGHT, t))
    for f in rim:
        f.material_index = a._mi(_mix(BARK, BARK_DARK, RIM_KEY_T))
    _mottle(a, side + tops + walls + rim, BARK_MOTTLE["amp"], BARK_MOTTLE["scale"], BARK_MOTTLE["seed"],
            BARK_MOTTLE["jitter"])


def _hole_cutter(a, tree):
    """The knot hole: a shallow inverted 5-sided pyramid near the +X top."""
    bm = a.bm
    H = KNOT_HOLE
    th = math.radians(H["th"])
    n = dirn(th)
    hit = tree.ray_cast(point(H["x"], th, radius(H["x"]) + 1.5), -n, 3.0)
    p = hit[0]
    u = Vector((1, 0, 0))
    w = n.cross(u).normalized()
    rng = random.Random(H["seed"])
    top = H["r"] * (H["depth"] + H["above"]) / H["depth"]
    ring = [bm.verts.new(p + n * H["above"] + (u * math.cos(a_) + w * math.sin(a_)) * top * rng.uniform(0.85, 1.1))
            for a_ in [2 * math.pi * k / 5 + 0.2 for k in range(5)]]
    tip = bm.verts.new(p - n * H["depth"])
    cap = bm.verts.new(p + n * (H["above"] + 0.02))
    fs = _fan(bm, ring, tip) + _fan(bm, ring, cap, flip=True)
    vs = ring + [tip, cap]
    a._finish(vs, BARK_DARK)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    return vs


# ---- stubs and knot ---------------------------------------------------------------------------------------------------------
def _stub_dir_large():
    lx, ly = (math.radians(v) for v in STUB_L["lean"])
    return Vector((math.tan(lx), math.tan(ly), 1.0)).normalized()


def _stub_dir_small():
    yw, pt = math.radians(STUB_S["yaw"]), math.radians(STUB_S["pitch"])
    return Vector((math.sin(yw) * math.cos(pt), -math.cos(yw) * math.cos(pt), -math.sin(pt)))


def _surface(x, th_deg):
    """The point on the plain bark at (x, th) (the grid's ring interpolated; the stubs' feet)."""
    return point(x, math.radians(th_deg), _local_r(x, th_deg))


def _local_r(x, th_deg):
    """The bark's distance from the axis at (x, th): the faceted cross-section (corners and face middles)
    interpolated between stations."""
    G = _grid()
    xs = G["xs"]
    i = max(0, min(NST - 2, int((x - xs[0]) / (xs[1] - xs[0]))))
    f = (x - xs[i]) / (xs[1] - xs[0])
    th = math.radians(th_deg)

    def ring_r(row):
        best = []
        for j in range(NV):
            p, a0, r0 = row[j]
            p2, a1, r1 = row[(j + 1) % NV]
            d0 = _wrap(th - a0)
            span = _wrap(a1 - a0) % (2 * math.pi)
            if 0 <= d0 % (2 * math.pi) <= span:
                s = (d0 % (2 * math.pi)) / span
                # the chord's distance from the axis at this angle
                q0 = Vector((r0 * math.cos(a0), r0 * math.sin(a0)))
                q1 = Vector((r1 * math.cos(a1), r1 * math.sin(a1)))
                dd = Vector((math.cos(th), math.sin(th)))
                # ray from the origin along dd hits the segment q0-q1
                e = q1 - q0
                den = dd.x * e.y - dd.y * e.x
                if abs(den) > 1e-9:
                    t_ = (q0.x * e.y - q0.y * e.x) / den
                    return t_
                return r0 + (r1 - r0) * s
        return radius(x)
    return ring_r(G["rows"][i]) * (1 - f) + ring_r(G["rows"][i + 1]) * f


def _stub(a, base, d, length, r0, r1, bury, seed, sides=8, tilt=(0.0, 0.0, 0.0), jag=0.0, chip=0.0, lip=0.86,
          cut_key=CUT_LIGHT, pith_key=None, top_light=0.25, flare=STUB_FLARE, rjit=STUB_RJIT, wobble=STUB_WOBBLE,
          top_n=None, st=(0.38, 0.7)):
    """A straight 8-sided branch stub from `bury` inside the log (a flat buried cap) out `length` along d: flared
    `flare` x at the bark, tapered r0 -> r1, each vertex jittered +-rjit, each ring twisted and its centre wobbled a
    little, so the long facets come out irregular (not a sawn beam); its end a flat cut plane (normal d + tilt, a
    vector) with a jagged outline (+-jag along the axis, one chip `chip` deep on the +X side), a thin bark lip (the
    outline -> lip x radius), the pale cut annulus and a slightly darker pith (0.3 radius). Returns verts."""
    rng = random.Random(seed)
    bm = a.bm
    d = Vector(d).normalized()
    u = Vector((1, 0, 0)) - d * d.x
    u = u.normalized() if u.length > 1e-3 else _perp(d)
    w = d.cross(u)
    tw0 = rng.uniform(0, 2 * math.pi)
    # the flared ring clear of the bark; the upper stations sit low enough to stay below a slanted end cut
    stations = (-bury, STUB_FOOT, st[0] * length, st[1] * length, length)
    top_i = len(stations) - 1
    rings = []
    for si, s in enumerate(stations):
        rr = r0 + (r1 - r0) * max(0.0, s) / length
        if si == 1:
            rr *= flare
        elif si == 2:
            rr *= 1 + (flare - 1) * 0.3
        tw = tw0 + math.radians(rng.uniform(-11, 11))
        cw = (u * rng.uniform(-1, 1) + w * rng.uniform(-1, 1)) * wobble if 1 < si < top_i else Vector()
        ring = []
        for k in range(sides):
            ph = tw + 2 * math.pi * k / sides
            rad = rr * (1 + rng.uniform(-rjit, rjit))
            ring.append((ph, rad, s + (rng.uniform(-0.04, 0.04) * length if 1 < si < top_i else 0.0), cw))
        rings.append(ring)
    # the end plane
    C = base + d * length
    nt = Vector(top_n).normalized() if top_n else (d + Vector(tilt)).normalized()
    chip_k = max(range(sides), key=lambda k: math.cos(rings[top_i][k][0]))      # the vertex nearest +X (u)
    V = []
    for si, ring in enumerate(rings):
        row = []
        for k, (ph, rad, s, cw) in enumerate(ring):
            off = (u * math.cos(ph) + w * math.sin(ph)) * rad
            q = base + d * s + off + cw
            if si == top_i:
                q = q + d * ((C - q).dot(nt) / d.dot(nt))
                q = q + d * rng.uniform(-jag, jag)
                if chip and k == chip_k:
                    q = q - d * chip
            row.append(bm.verts.new(q))
        V.append(row)
    sides_f = []
    for r0_, r1_ in zip(V, V[1:]):
        sides_f += _strip(bm, r0_, r1_)
    c0 = bm.verts.new(base - d * (bury + 0.02))
    bot = _fan(bm, V[0], c0, flip=True)
    top = V[-1]
    lipv = [bm.verts.new(C + (v.co - C) * lip + nt * 0.012) for v in top]
    lipf = _strip(bm, top, lipv)
    pr = rng.uniform(0, 2 * math.pi)
    pu = (u - nt * u.dot(nt)).normalized()
    pw = nt.cross(pu)
    rr1 = r1 * 0.3
    pith = [bm.verts.new(C + nt * 0.02 + (pu * math.cos(pr + 2 * math.pi * k / 6) +
                                          pw * math.sin(pr + 2 * math.pi * k / 6)) * rr1 * rng.uniform(0.9, 1.1))
            for k in range(6)]
    angf = lambda v: math.atan2((v.co - C).dot(pw), (v.co - C).dot(pu))
    cutf = _zip(bm, lipv, pith, angf)
    cc = bm.verts.new(C + nt * 0.03)
    pithf = _fan(bm, pith, cc)
    vs = [v for r in V for v in r] + [c0] + lipv + pith + [cc]
    _tri(bm, sides_f + lipf)
    a._finish(vs, BARK)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    # colour: bark, its top third a step lighter (the lit lip on the sheet), the lip ring, the pale cut, the pith
    fl = _faces(vs)
    for f in fl:
        c = f.calc_center_median()
        s = (c - base).dot(d)
        if all(v in set(lipv) | set(pith) | {cc} for v in f.verts):
            continue
        if any(v in set(lipv) for v in f.verts):
            f.material_index = a._mi(_mix(BARK, BARK_LIGHT, top_light))
        elif s > length - 0.35:
            f.material_index = a._mi(_mix(BARK, BARK_LIGHT, top_light))
    for f in cutf:
        f.material_index = a._mi(cut_key)
    for f in pithf:
        f.material_index = a._mi(pith_key or K.mix_key(cut_key, CUT_RING, 0.5))
    _mottle(a, [f for f in fl if f not in set(cutf) | set(pithf)], BARK_MOTTLE["amp"], BARK_MOTTLE["scale"],
            BARK_MOTTLE["seed"] + seed)
    _mottle(a, cutf + pithf, CUT_MOTTLE["amp"], CUT_MOTTLE["scale"], CUT_MOTTLE["seed"] + seed)
    return vs


def _nub(a, base, d, r, out, bury, seed, sides=6):
    """The knot: a short 6-sided nub from `bury` inside out `out` along d, a jagged pale tip. Returns verts."""
    rng = random.Random(seed)
    bm = a.bm
    d = Vector(d).normalized()
    u = _perp(d)
    w = d.cross(u)
    ph0 = rng.uniform(0, 2 * math.pi)
    st = ((-bury, 1.0), (0.0, 1.0), (out * 0.62, 0.88), (out * 0.86, 0.72))
    V = []
    for si, (s, sc) in enumerate(st):
        row = []
        for k in range(sides):
            ph = ph0 + 2 * math.pi * k / sides + math.radians(rng.uniform(-6, 6))
            q = base + d * s + (u * math.cos(ph) + w * math.sin(ph)) * r * sc * rng.uniform(0.94, 1.06)
            if si == 3:
                q = q + d * ((0.07 if k % 2 == 0 else -0.04) + rng.uniform(-0.02, 0.02))
            row.append(bm.verts.new(q))
        V.append(row)
    fs = []
    for r0_, r1_ in zip(V, V[1:]):
        fs += _strip(bm, r0_, r1_)
    c0 = bm.verts.new(base - d * (bury + 0.02))
    bot = _fan(bm, V[0], c0, flip=True)
    # round 2 (verifier minor 4): a bark shoulder round a small pale tip about KNOT_TIP of the knot's diameter
    # (the sheet's tip is a small pale fleck, not a cap as large as the stub's top)
    ph1 = ph0 + math.pi / sides
    inner = [bm.verts.new(base + d * (out * 0.94 + rng.uniform(-0.02, 0.02)) +
                          (u * math.cos(ph1 + 2 * math.pi * k / sides) + w * math.sin(ph1 + 2 * math.pi * k / sides))
                          * r * KNOT_TIP * rng.uniform(0.9, 1.1)) for k in range(sides)]
    shoulder = _strip(bm, V[-1], inner)
    fs += shoulder
    tipc = bm.verts.new(base + d * out + u * 0.03)
    tip = _fan(bm, inner, tipc)
    _tri(bm, fs)
    vs = [v for r in V for v in r] + inner + [c0, tipc]
    a._finish(vs, BARK)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    fl = _faces(vs)
    tset = set(tip)
    for f in fl:
        if f in tset:
            f.material_index = a._mi(CUT_EDGE)
        else:
            s = (f.calc_center_median() - base).dot(d)
            f.material_index = a._mi(_mix(BARK, BARK_LIGHT, 0.75 if s > out * 0.6 else 0.5))
    _mottle(a, fl, BARK_MOTTLE["amp"], BARK_MOTTLE["scale"], BARK_MOTTLE["seed"] + seed)
    return vs


def stub_large(a, knot=True):
    S = STUB_L
    base = _surface(S["x"], S["th"])
    d = _stub_dir_large()
    vs = _stub(a, base, d, S["length"], S["r"][0], S["r"][1], S["bury"], S["seed"], top_n=S["top_n"], jag=S["jag"],
               chip=S["chip"], lip=S["lip"], st=S["st"], cut_key=LARGE_TOP[0], pith_key=LARGE_TOP[1])
    return vs


def knot(a):
    Kn = KNOT
    base = _surface(Kn["x"], Kn["th"])
    lean = math.radians(Kn["lean"])
    n = dirn(math.radians(Kn["th"]))
    d = (n * math.cos(lean) + Vector((-1, 0, 0)) * math.sin(lean)).normalized()
    return _nub(a, base, d, Kn["r"], Kn["out"], Kn["bury"], Kn["seed"])


def stub_small(a):
    S = STUB_S
    base = _surface(S["x"], S["th"])
    d = _stub_dir_small()
    ck, pk = _small_end()
    return _stub(a, base, d, S["length"], S["r"][0], S["r"][1], S["bury"], S["seed"], lip=S["lip"],
                 cut_key=ck, pith_key=pk, top_light=0.0, top_n=S["top_n"], st=S["st"])


def stub_end_centre():
    S = STUB_S
    return _surface(S["x"], S["th"]) + _stub_dir_small() * S["length"]


# ---- leaf clumps (the M020 round-2 broad kite recipe, flat stars) -------------------------------------------------------------
KITE = ((0.22, 0.43), (0.52, 0.50), (0.80, 0.33))     # round 2: fuller kites (more leaf area, W : L about 0.6)
RIDGE = ((0.42, 0.075), (0.76, 0.035))
KEEL = (0.50, 0.035)
FOLD = 0.14
HANDLES = (0.48, 0.38)
LEAF_BANDS = ((0.15, 0.40), (0.60, 0.85))
LEAF_NOISE = 0.08
LEAF_HALF = 0.30
LEAF_MOTTLE = dict(amp=0.035, scale=0.5, seed=26071)
LEAF_PITCH = (15.0, 35.0)
LEAF_HANDLE = 2.0
LEAF_SLOPE = (-18.0, -4.0)
LEAF_ROLL = 12.0
LEAF_L, LEAF_W = 1.05, 0.62        # leaf length and width per unit of half-span (leaf L ~0.52 span, W ~0.52 L)
HUB = dict(r=0.16, apex=0.08, sink=0.22)


def _ladder(lo, mid, hi):
    return ([lo] + [K.mix_key(lo, mid, t) for t in (0.25, 0.5, 0.75)] + [mid] +
            [K.mix_key(mid, hi, t) for t in (0.25, 0.5, 0.75)] + [hi])


def _pick(lad, v, low, high):
    if v < (low[1] + high[0]) / 2:
        return lad[round(_q((v - low[0]) / (low[1] - low[0])) * 4)]
    return lad[4 + round(_q((v - high[0]) / (high[1] - high[0])) * 4)]


def _bez(P, t):
    p0, p1, p2, p3 = P
    s = 1 - t
    return p0 * s ** 3 + p1 * 3 * s * s * t + p2 * 3 * s * t * t + p3 * t ** 3


def _bez_d(P, t):
    p0, p1, p2, p3 = P
    s = 1 - t
    return (p1 - p0) * 3 * s * s + (p2 - p1) * 6 * s * t + (p3 - p2) * 3 * t * t


def _leaf_path(base, az, tip, pitch, slope):
    B = Vector(base)
    a1 = math.radians(az)
    T = Vector((math.cos(a1) * tip[0], math.sin(a1) * tip[0], tip[1]))
    chord = (T - B).length

    def dirv(p):
        p = math.radians(p)
        return Vector((math.cos(a1) * math.cos(p), math.sin(a1) * math.cos(p), math.sin(p)))
    return (B, B + dirv(pitch) * HANDLES[0] * chord, T - dirv(slope) * HANDLES[1] * chord, T)


def _leaf(a, path, width, seed, roll=0.0, shift=0.0):
    """One closed broad pointed leaf along path (local clump frame): an 8-point kite outline, two midrib ridge points
    above (lit and shaded halves), a keel below. Painted base -> mid -> tip along its length. Returns verts."""
    rng = random.Random(seed)
    bm = a.bm
    P = [Vector(p) for p in path]
    L = sum((_bez(P, (i + 1) / 20) - _bez(P, i / 20)).length for i in range(20))
    W = width
    side0 = Vector((-(P[3] - P[0]).y, (P[3] - P[0]).x, 0.0)).normalized()
    rl = math.radians(roll)

    def frame(t):
        T = _bez_d(P, t).normalized()
        S = (side0 - T * side0.dot(T)).normalized()
        N = T.cross(S).normalized()
        if N.z < 0:
            N = -N
        S = N.cross(T).normalized()
        S, N = S * math.cos(rl) + N * math.sin(rl), N * math.cos(rl) - S * math.sin(rl)
        return _bez(P, t), S, N
    tm = {}

    def vert(t, y, z):
        c, S, N = frame(t)
        x = bm.verts.new(c + S * y + N * z)
        tm[x] = t
        return x
    base = vert(0.0, 0.0, 0.0)
    tip = vert(1.0, 0.0, 0.0)
    right, left = [], []
    for t, h in KITE:
        y = h * W * (1 + rng.uniform(-0.06, 0.06))
        right.append(vert(t, -y, -FOLD * y * 0.5))
    for t, h in KITE:
        y = h * W * (1 + rng.uniform(-0.06, 0.06))
        left.append(vert(t, y, -FOLD * y * 0.5))
    r1 = vert(RIDGE[0][0], 0.0, RIDGE[0][1] * L)
    r2 = vert(RIDGE[1][0], 0.0, RIDGE[1][1] * L)
    k = vert(KEEL[0], 0.0, -KEEL[1] * L)
    ring = [base] + right + [tip] + list(reversed(left))
    fs = []
    for sd in (right, left):
        s, b, p = sd
        fs += [bm.faces.new((base, s, r1)), bm.faces.new((s, b, r1)), bm.faces.new((b, r2, r1)),
               bm.faces.new((b, p, r2)), bm.faces.new((p, tip, r2))]
    for i in range(len(ring)):
        fs.append(bm.faces.new((k, ring[(i + 1) % len(ring)], ring[i])))
    vs = ring + [r1, r2, k]
    a._finish(vs, LEAF)
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    lad = _ladder(LEAF_BASE, LEAF, LEAF_TIP)
    half = set(fs[:5])
    for f in fs:
        t = sum(tm[v] for v in f.verts) / len(f.verts) + shift + rng.uniform(-LEAF_NOISE, LEAF_NOISE)
        if f in half:
            t -= LEAF_HALF
        f.material_index = a._mi(_pick(lad, t, LEAF_BANDS[0], LEAF_BANDS[1]))
    return vs


def _clump(a, hub, normal, out, span, seed, fan=360.0, shift=0.0, pitch=LEAF_PITCH, sink=None, yaw=0.0):
    """A flat six-leaf star round a hidden 5-sided hub cone (no stem): local frame hub at the origin, +Z along normal,
    local +X toward `out`. Leaves 60 deg apart (+-12) inside `fan` degrees centred on +X, alternately in the lower
    and upper third of `pitch` (so neighbours stack instead of crossing), tips drooping. Returns verts."""
    rng = random.Random(seed)
    bm = a.bm
    s = span / 2.0
    sink = HUB["sink"] * s if sink is None else sink
    out_v = []
    hr = HUB["r"] * s
    ph = rng.uniform(0, 2 * math.pi)
    foot = [bm.verts.new((math.cos(ph + 2 * math.pi * k / 5) * hr * 0.6, math.sin(ph + 2 * math.pi * k / 5) * hr * 0.6,
                          -sink)) for k in range(5)]
    mid = [bm.verts.new((math.cos(ph + 2 * math.pi * k / 5) * hr * 0.8, math.sin(ph + 2 * math.pi * k / 5) * hr * 0.8,
                         0.02)) for k in range(5)]
    apex = bm.verts.new((0, 0, HUB["apex"] * s))
    fb = bm.verts.new((0, 0, -sink - 0.02))
    fs = _strip(bm, foot, mid) + _fan(bm, mid, apex) + _fan(bm, foot, fb, flip=True)
    _tri(bm, fs)
    hub_v = foot + mid + [apex, fb]
    a._finish(hub_v, LEAF_BASE)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(hub_v))
    out_v += hub_v
    n = 6
    step = fan / n if fan < 360.0 else 60.0
    az0 = (-fan / 2 + step / 2 if fan < 360.0 else rng.uniform(0, 360)) + yaw
    for k in range(n):
        az = az0 + step * k + rng.uniform(-12, 12) * (step / 60.0)
        L = LEAF_L * s * (1 + rng.uniform(-0.08, 0.08))
        W = LEAF_W * s * (1 + rng.uniform(-0.06, 0.06))
        b0 = Vector((0.0, 0.0, -0.05 * s))
        lo, hi = pitch
        p = rng.uniform(lo, lo + (hi - lo) / 3) if k % 2 == 0 else rng.uniform(hi - (hi - lo) / 3, hi)
        tipr = L * math.cos(math.radians(p)) * 0.95
        tipz = L * math.sin(math.radians(p)) * 0.95
        path = _leaf_path(b0, az, (tipr, tipz), p + LEAF_HANDLE, rng.uniform(*LEAF_SLOPE))
        out_v += _leaf(a, path, W, seed * 10 + k, roll=rng.uniform(-LEAF_ROLL, LEAF_ROLL), shift=shift)
    N = Vector(normal).normalized()
    X = Vector(out)
    X = (X - N * X.dot(N))
    X = X.normalized() if X.length > 1e-6 else N.orthogonal().normalized()
    Y = N.cross(X)
    R = Matrix((X, Y, N)).transposed().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(hub)) @ R, verts=out_v)
    _mottle(a, _faces(out_v), LEAF_MOTTLE["amp"], LEAF_MOTTLE["scale"], LEAF_MOTTLE["seed"] + seed)
    return out_v


GROUND_HUB = 0.14      # ground hubs this high: the leaf bases stay above the floor cut, only the hub cone is cut
# (verifier round 2 minor 1 asked for -0.05 so the clumps rest on the ground; tried 2026-10-28: the floor cut then split
# the ground clumps off the hero, 3 shells and 11 self-hits, so it stays at 0.14 and the hover is a recorded minor)
# hero clumps (spec section 2): name -> (hub target, normal, outward direction, span, seed, fan, colour shift)
# BR's hub target is (x, angle deg round the log) on the bark; the others are ground hubs slid in to the log
CLUMPS = {"FL": ((-3.35, -2.35, GROUND_HUB), (-0.08, -0.12, 1.0), (-1.0, -0.6, 0.0), 2.3, 26081, 360.0, 0.0),
          "FR": ((2.85, -2.45, GROUND_HUB), (0.08, -0.15, 1.0), (0.6, -1.0, 0.0), 2.8, 26082, 360.0, 0.05),
          "BR": ((3.7, 86.0), None, (0.3, 1.0, 0.0), 2.8, 26083, 360.0, 0.05),
          "BK": ((0.9, 2.3, GROUND_HUB), (0.0, 0.12, 1.0), (0.2, 1.0, 0.0), 2.6, 26084, 360.0, 0.0)}
# round 2 (verifier B3): BR sits on the crest toward the +X end (4 deg behind it; the knot hole moved to x 3.0 to
# clear it), its hub normal only BR_TILT deg off vertical, tipped toward the front so the plane rises toward the back
# and the decided 15-35 deg pitch (its top band here) lifts the back and side leaves above the log's top line, as
# the sheet's fan rises from the top edge. A hub 45-55 deg behind the crest (the verifier's suggestion) was tried:
# the hub's depth pushes it left on screen (f .76-.77) and only the leaf tips clear the crest (hf .05-.11).
# The ground clumps use the upper part of the pitch band (FR a little lower, to keep its centre on the sheet's).
BR_TILT = -12.0
CLUMP_PITCH = {"FL": (20.0, 35.0), "FR": (15.0, 32.0), "BR": (28.0, 35.0), "BK": (20.0, 35.0)}
CLUMP_SINK = 0.10
CLUMP_SINK_GROUND = 0.2
CLUMP_YAW_JIT = [0.0]     # extra yaw on every hero clump (deg); the hero guard turns them a little on a retry
CLUMP_INFO = {}


def _overlaps(tree, hub, normal, out, span, seed, fan, yaw=0.0, pitch=LEAF_PITCH):
    t = K.fk().Asset(PFX + "probe", "probe")
    _clump(t, hub, normal, out, span, seed, fan=fan, yaw=yaw, pitch=pitch)
    t.bm.verts.ensure_lookup_table()
    t.bm.faces.ensure_lookup_table()
    hit = bool(BVHTree.FromBMesh(t.bm).overlap(tree))
    t.bm.free()
    return hit


def clumps(a):
    """The four clumps: BR dropped onto the log's top-back (hub sunk CLUMP_SINK, its normal half way between the
    bark's and up); FL, FR, BK slid in from their ground hubs toward the log just until their leaves cut into it (so
    the hero stays one shell)."""
    a.bm.verts.ensure_lookup_table()
    a.bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(a.bm)
    out = []
    CLUMP_INFO.clear()
    for k, (hub, nrm, outd, span, seed, fan, shift) in CLUMPS.items():
        if nrm is None:
            x, th = hub
            n = dirn(math.radians(th))
            hit = tree.ray_cast(point(x, math.radians(th), radius(x) + 1.5), -n, 3.0)
            back = Vector((0.0, n.y, 0.0)).normalized()
            N = Vector((0, 0, 1)) * math.cos(math.radians(BR_TILT)) + back * math.sin(math.radians(BR_TILT))
            P = hit[0] - N * CLUMP_SINK
        else:
            H, N = Vector(hub), Vector(nrm).normalized()
            P = H
            d = Vector((0.0, -1.0 if H.y > 0 else 1.0, 0.0))
            for step in range(45):
                q = H + d * (0.05 * step)
                if _overlaps(tree, q, N, outd, span, seed, fan, CLUMP_YAW_JIT[0], CLUMP_PITCH[k]):
                    P = q + d * CLUMP_SINK_GROUND
                    break
        CLUMP_INFO[k] = {"hub": [round(c, 2) for c in P]}
        out += _clump(a, P, N, outd, span, seed, fan=fan, shift=shift, yaw=CLUMP_YAW_JIT[0], pitch=CLUMP_PITCH[k])
    return out


# ---- the fused trunk (temporary objects in the build frame) ----------------------------------------------------------------
def _tmp(name, fn):
    old = bpy.data.objects.get(name)
    if old:
        me = old.data
        bpy.data.objects.remove(old, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    coll = M.coll(NUM, TITLE)
    a = K.fk().Asset(name, "wip", seed=7, tint_var=0.04)
    fn(a)
    o = a.finish(collection=coll, mark_asset=False, origin=None)
    o.location = (0, 0, 0)
    bpy.context.view_layer.update()
    o[OFF] = [0.0, 0.0, 0.0]
    return o


def _carve(o, fn):
    """Exact difference of one cutter (fn, in the build frame) from o (a temporary object in the build frame)."""
    c = _tmp(PFX + "cutter", fn)
    m = o.modifiers.new("Carve", "BOOLEAN")
    m.operation, m.solver, m.object = "DIFFERENCE", "EXACT", c
    m.material_mode = "TRANSFER"
    with M._override(o):
        bpy.ops.object.modifier_apply(modifier=m.name)
    me = c.data
    bpy.data.objects.remove(c, do_unlink=True)
    bpy.data.meshes.remove(me)
    K.drop_unused_slots(o)


def _tree_of(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.transform(o.matrix_world)
    t = BVHTree.FromBMesh(bm)
    bm.free()
    return t


TRUNK_LOG = {}


def fuse_trunk():
    """The trunk with its plates and slits (one surface), then the knot hole carved (the one boolean)."""
    GRID.clear()
    _grid()
    slit_lines()
    plates()
    o = _tmp(PFX + "trunk", trunk_raw)
    raw = M.audit(o)["tris"]
    tree = _tree_of(o)
    _carve(o, lambda a: _hole_cutter(a, tree))
    m016._weld(o)
    au = M.audit(o)
    TRUNK_LOG.update(slits=len(GRID["slits"]), plates=len(GRID["plate_info"]), tris_raw=raw, tris=au["tris"],
                     nonmanifold=au["nonmanifold_edges"], bowties=au["nonmanifold_verts"],
                     boundary=au["boundary_edges"], shells=au["shells"])
    return o


# ---- parts -----------------------------------------------------------------------------------------------------------------
def _paste_obj(a, o, m=None):
    mat = (m if m is not None else Matrix.Identity(4)) @ Matrix.Translation(Vector(o[OFF]))
    return m011._paste(a, o, mat)


def trunk_part(a):
    _paste_obj(a, bpy.data.objects[PFX + "trunk"])


DISC_T = 0.38


def cut_end_part(a):
    """FallenSoftwoodLogCutEnd: the 11-sided disc standing on its edge facing -X, as on the log end and the sheet's
    exploded cell: the face's loops (same outline, orientation and rings as the trunk's face), the chamfer to the
    edge, a straight side band, a flat back. Built face up, then turned."""
    bm = a.bm
    G = _grid()
    R_face = R0 - RIM
    rng = random.Random(TRUNK["seed"] + 2)
    to_w = lambda th, r: Vector((r * math.sin(th), r * math.cos(th), DISC_T))    # turned: y = r cos, z = r sin
    loops, centre = _face_loops(bm, Vector((0, 0, 0)), None, to_w, R_face, rng)
    angf = lambda v: math.atan2(v.co.x, v.co.y)
    edge = [bm.verts.new(to_w(G["rows"][0][2 * k][1], G["rows"][0][2 * k][2] * R_face / R0) -
                         Vector((0, 0, CHAMFER[1]))) for k in range(NSIDE)]
    low = [bm.verts.new(Vector((v.co.x, v.co.y, 0.0))) for v in edge]
    chamfer = _zip(bm, edge, loops[0], angf)
    bands = [_zip(bm, l0, l1, angf) for l0, l1 in zip(loops, loops[1:])]
    bands.append(_fan(bm, loops[-1], centre))
    side = _strip(bm, low, edge)
    bc = bm.verts.new((0, 0, 0))
    bot = _fan(bm, low, bc, flip=True)
    _tri(bm, side)
    vs = [v for l in loops for v in l] + [centre] + edge + low + [bc]
    a._finish(vs, CUT)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    _paint_face(a, [(chamfer, FACE_EDGE)] + [(b, CUT_BANDS[len(CUT_BANDS) - 1 - k][1]) for k, b in enumerate(bands)])
    sf = [f for f in _faces(vs) if f.calc_center_median().z < DISC_T - CHAMFER[1] + 1e-4]
    for f in sf:          # the disc's side and bottom: the face's outer light band (one wood, no facing shade)
        f.material_index = a._mi(FACE_LIGHT)
    _mottle(a, sf, CUT_MOTTLE["amp"], CUT_MOTTLE["scale"], CUT_MOTTLE["seed"] + 5)
    bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0), matrix=Matrix.Rotation(-math.pi / 2, 3, "Y"))     # +Z -> -X


def stub_large_part(a):
    """FallenSoftwoodLogBranchStubLarge: the stub as in the hero (leaning), with its buried base, and the knot nub
    at its foot on the -X side (the exploded cell's nub)."""
    S = STUB_L
    base = Vector((0.0, 0.0, S["bury"]))
    d = _stub_dir_large()
    _stub(a, base, d, S["length"], S["r"][0], S["r"][1], S["bury"], S["seed"], top_n=S["top_n"], jag=S["jag"],
          chip=S["chip"], lip=S["lip"], st=S["st"], cut_key=LARGE_TOP[0], pith_key=LARGE_TOP[1])
    nd = Vector((-0.85, 0.0, -0.25)).normalized()
    _nub(a, base + d * 0.15 - Vector((0.25, 0, 0)), nd, KNOT["r"] * 0.85, 0.75, 0.25, KNOT["seed"])


def stub_small_part(a):
    S = STUB_S
    d = _stub_dir_small()
    ck, pk = _small_end()
    _stub(a, Vector((0.0, 0.0, 0.0)), d, S["length"], S["r"][0], S["r"][1], S["bury"], S["seed"], lip=S["lip"],
          cut_key=ck, pith_key=pk, top_light=0.0, top_n=S["top_n"], st=S["st"])


CLUMP_PART = dict(span=1.9, seed=26091, pitch=(15.0, 30.0), sink=0.06)


def clump_part(a):
    C = CLUMP_PART
    _clump(a, (0, 0, C["sink"] + 0.02), (0, 0, 1), (1, 0, 0), C["span"], C["seed"], shift=0.05, pitch=C["pitch"],
           sink=C["sink"])


def hero(a):
    _paste_obj(a, bpy.data.objects[PFX + "trunk"])
    stub_large(a)
    knot(a)
    stub_small(a)
    clumps(a)


NOTES = {
    HERO: "fallen softwood log: a long chunky 11-sided bark log with raised bark plates, step ledges and dark slits, "
          "a pale ringed flush cut end in a thin bark rim at one end and a blunt faceted bark dome at the other, a "
          "large leaning branch stub with a pale broken top and a knot nub, a small stub down to the ground with a "
          "pale end, four bright six-leaf flat star clumps; one closed mesh, flat contact strip. No VFX",
    "FallenSoftwoodLogTrunk": "Main Log (reusable): 11-sided bark log with raised plates, slits, a knot hole, a pale "
                              "ringed flush cut face with a chamfer and a blunt bark dome at the far end",
    "FallenSoftwoodLogCutEnd": "Cut-End Insert (reusable): 0.38-thick 11-sided pale disc, painted rings, chamfered "
                               "edge",
    "FallenSoftwoodLogBranchStubLarge": "Branch Stub (Large, reusable): 8-sided leaning branch stub with a pale "
                                        "jagged broken top and a knot nub at its foot, buried base",
    "FallenSoftwoodLogBranchStubSmall": "Branch Stub (Small, reusable): 8-sided straight branch stub with a pale "
                                        "square-cut end, flat attach end",
    "FallenSoftwoodLogLeafClump": "Leaf Clump (reusable): six broad pointed kite leaves in a flat star round a hidden "
                                  "hub, dark bases to lime tips",
}


# ---- cleanup (m020's guarded procedure, this model's planes) ----------------------------------------------------------------
def _crosses(bm, v, co):
    bm.faces.ensure_lookup_table()
    tris = []
    for f in v.link_faces:
        ps = [co if w is v else w.co for w in f.verts]
        if len(ps) == 3 and ((ps[1] - ps[0]).cross(ps[2] - ps[0])).length > 1e-12:
            tris.append(ps)
    if not tris:
        return False
    moved = _shrunk_tree(tris)
    full = BVHTree.FromBMesh(bm)
    return any(v not in bm.faces[j].verts for _, j in moved.overlap(full))


def _shrunk_tree(tris, k=0.995):
    pts = []
    for t in tris:
        c = (t[0] + t[1] + t[2]) / 3
        pts += [c + (p - c) * k for p in t]
    return BVHTree.FromPolygons(pts, [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(len(tris))], epsilon=0.0)


def _tri_safe(bm):
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    flist = list(bm.faces)
    for f in [f for f in bm.faces if len(f.verts) > 3]:
        if not f.is_valid:
            continue
        vs = list(f.verts)
        n = len(vs)
        fn = f.normal.copy()
        best = None
        for k in range(n):
            tris = [(vs[k].co, vs[(k + i) % n].co, vs[(k + i + 1) % n].co) for i in range(1, n - 1)]
            nrm = [(b - a).cross(c - a) for a, b, c in tris]
            if min(x.length for x in nrm) < 1e-12 or any(x.dot(fn) <= 0 for x in nrm):
                continue
            cand = _shrunk_tree([[p.copy() for p in t] for t in tris])
            cross = sum(1 for _, j in cand.overlap(tree) if flist[j].is_valid and flist[j] is not f)
            ang = min(m011._min_angle(list(t)) for t in tris)
            score = (cross, -ang)
            if best is None or score < best[0]:
                best = (score, k)
        if best is None:
            bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="BEAUTY")
            continue
        k = best[1]
        for i in range(2, n - 1):
            bmesh.ops.connect_verts(bm, verts=[vs[k], vs[(k + i) % n]])
    left = [f for f in bm.faces if len(f.verts) > 3]
    if left:
        bmesh.ops.triangulate(bm, faces=left, quad_method="BEAUTY", ngon_method="BEAUTY")


def _lock(zs=(), xs=()):
    """movable(v, co): verts on one of the z planes (the ground) or x planes (the flat cut face) only slide within
    them."""
    def movable(v, co):
        if not all(abs(v.co.z - z) > 1e-4 or abs(co.z - z) < 1e-6 for z in zs):
            return False
        return all(abs(v.co.x - x) > 1e-4 or abs(co.x - x) < 1e-6 for x in xs)
    return movable


CLEAN_MOVE = 0.08        # smaller than m011's 0.18: the slits are 0.12 wide


def _clean_guarded(o, movable, max_move):
    from mathutils.geometry import intersect_point_line
    bm = bmesh.new()
    bm.from_mesh(o.data)
    v2 = []
    for v in bm.verts:
        if len(v.link_edges) == 2 and all(len(f.verts) > 3 for f in v.link_faces) and movable(v, v.co):
            a_, c_ = (e.other_vert(v) for e in v.link_edges)
            p, _ = intersect_point_line(v.co, a_.co, c_.co)
            if (p - v.co).length < max_move and movable(v, p):
                v2.append(v)
    bmesh.ops.dissolve_verts(bm, verts=v2)
    _tri_safe(bm)

    def guarded(v, co):
        if not movable(v, co):
            return False
        return (co - v.co).length < 1e-9 or not _crosses(bm, v, co)
    log = m011._desliver(bm, guarded, min_angle=5.0, max_move=max_move)
    log["dissolved_v2"] = len(v2)
    bm.to_mesh(o.data)
    bm.free()
    return log


def _clean_mesh(o, zs=(), xs=()):
    m016._weld(o)
    ears = m016._dissolve_ears(o)
    pockets = m012._drop_inner(o)
    log = _clean_guarded(o, _lock(zs, xs), max_move=CLEAN_MOVE)
    pockets += m012._drop_inner(o)
    log["ears"] = ears
    log["pockets"] = pockets
    log["forced"] = m012._force_slivers(o)
    return log


def _bottom_centre(o):
    return m012._bottom_centre(o)


def _finish(o):
    o[OFF] = list(Vector(o[OFF]) + _bottom_centre(o))
    res = M.finish(o, union=False, uv=UV)
    for _ in range(3):
        crumbs = m012._drop_inner(o)
        if not (crumbs or m012._thin(o)["under"] or res["nonmanifold_edges"] or res["boundary_edges"]):
            break
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bnd = [e for e in bm.edges if e.is_boundary]
        if bnd:
            if not bmesh.ops.holes_fill(bm, edges=bnd)["faces"]:
                bmesh.ops.contextual_create(bm, geom=bnd)
            bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY")
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(o.data)
        bm.free()
        M.repair_nonmanifold(o)
        m012._force_slivers(o)
        o[OFF] = list(Vector(o[OFF]) + _bottom_centre(o))
        res = M.finish(o, union=False, uv=UV)
    return res


def _polish(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = m012._tri_quads(bm)
    zmin = min(v.co.z for v in bm.verts)
    floor = [f for f in bm.faces if f.normal.z < -0.999 and all(abs(v.co.z - zmin) < 1e-4 for v in f.verts)]
    big = [f for f in floor if f.calc_area() > 0.8 and m011._fmin(f) < math.radians(12)]
    if big:
        made = bmesh.ops.poke(bm, faces=big)["faces"]
        floor = [f for f in floor if f.is_valid] + list(made)
    fset = set(floor)
    inner = [e for e in {e for f in floor for e in f.edges} if all(g in fset for g in e.link_faces)]
    if inner:
        bmesh.ops.beautify_fill(bm, faces=floor, edges=inner)
    for _ in range(4):
        bad = [f for f in bm.faces if f.is_valid and f.normal.z < -0.999 and m011._fmin(f) < math.radians(POLISH_LIM)
               and all(abs(v.co.z - zmin) < 1e-4 for v in f.verts)]
        if not bad:
            break
        longs = list({max((e for e in f.edges if len(e.link_faces) == 2 and all(
            g.normal.z < -0.999 for g in e.link_faces)), key=lambda x: x.calc_length(), default=None) for f in bad}
                     - {None})
        if not longs:
            break
        res = bmesh.ops.subdivide_edges(bm, edges=longs, cuts=1)
        touched = {f for v in res["geom_inner"] if isinstance(v, bmesh.types.BMVert) for f in v.link_faces}
        bmesh.ops.triangulate(bm, faces=[f for f in touched if len(f.verts) > 3], quad_method="BEAUTY",
                              ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = m012._force_slivers(o, lim=POLISH_LIM)
    if m012._thin(o, POLISH_LIM)["under"]:
        forced += m012._force_slivers(o, lim=POLISH_LIM, max_len=0.5)
    bc = _bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()
    M.smart_uv(o, **UV)
    return {"split": split, "forced": forced, "uv_cut": m012._uv_unfold(o)}


def _ground_faces(o):
    """Faces on the ground plane (the floor cut's caps): leaf base under a leaf, cut wood under the small stub's pale
    end, plain bark elsewhere (a darker key on this large down-facing area would follow facing)."""
    from m011 import _Paint
    p = _Paint(o, off=o[OFF])
    end = stub_end_centre()
    n = {"cut": 0, "leaf": 0, "bark": 0}
    for f in p.bm.faces:
        if not all(abs(v.co.z) < 1e-3 for v in f.verts):
            continue
        c = p.at(f)
        nb = {p.key(g) for e in f.edges for g in e.link_faces if g is not f}
        if Vector((c.x - end.x, c.y - end.y)).length < 0.3 and any(k.startswith("m026_cut") for k in nb):
            key = CUT
        elif any(k.startswith("m026_leaf") for k in nb) and f.calc_area() < 0.06:
            key = LEAF_BASE
        else:
            key = BARK
        f.material_index = p._mi(key)
        n["cut" if key == CUT else "leaf" if key == LEAF_BASE else "bark"] += 1
    p.done()
    return n


# ---- stages 5 + 6 (spec section 7) -----------------------------------------------------------------------------------------
# Stage 5: nothing. The sheet shows an ordinary sunlit log: no emissive key, no light (decision 8).
# Stage 6: nothing. The sheet shows no glow, sparkle, dust or chips: no socket (decision 8).


# ---- build -------------------------------------------------------------------------------------------------------------------
PARTS = (("FallenSoftwoodLogTrunk", trunk_part), ("FallenSoftwoodLogCutEnd", cut_end_part),
         ("FallenSoftwoodLogBranchStubLarge", stub_large_part), ("FallenSoftwoodLogBranchStubSmall", stub_small_part),
         ("FallenSoftwoodLogLeafClump", clump_part))
UNION_PARTS = {"FallenSoftwoodLogBranchStubLarge", "FallenSoftwoodLogLeafClump"}
GROUND_PARTS = {"FallenSoftwoodLogTrunk"}
TARGET_SIZE = ((9.4, 0.35), (6.7, 0.5), (5.05, 0.25))
HERO_TRIES = 6
HERO_YAW_STEP = 17.0


def _union_fine(o, merge=0.0):
    """M.union_loose with no post-union merge (m021): the merge welds the leaves' converging intersection curves at
    a hub into bowties."""
    act = bpy.context.view_layer.objects.active
    if act and act.mode != "OBJECT":
        with bpy.context.temp_override(active_object=act, object=act):
            bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()
    others = M.split_loose(o)
    for p in others:
        m = o.modifiers.new("U", "BOOLEAN")
        m.operation, m.solver, m.object = "UNION", "EXACT", p
        m.material_mode = "TRANSFER"
        with M._override(o):
            bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.data.objects.remove(p, do_unlink=True)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=max(merge, 1e-5))
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    M.drop_specks(bm, min_area=0.05)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    K.drop_unused_slots(o)
    return len(others)


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)


def _make(name, fn, role, budget):
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget, collision="hull",
             tint_var=0.04)
    off = M._build_offset(fn)
    o[OFF] = list(off)
    lg = {}
    if name in UNION_PARTS or role == "hero":
        lg["shells_merged"] = _union_fine(o)
    ground = name in GROUND_PARTS or role == "hero"
    if ground:
        m016._floor_cut(o, -off.z)
        o[OFF] = [off.x, off.y, 0.0]
    xs = (X_FACE - off.x,) if (ground or name == "FallenSoftwoodLogTrunk") else ()
    lg["clean"] = _clean_mesh(o, (0.0,) if ground else (), xs)
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    lg["bowties"] = M.fix_bowties(o)
    if ground:
        lg["ground_faces"] = _ground_faces(o)
    return o, lg


def _fused_ok(o):
    a = M.audit(o)
    return (a["shells"] == 1 and not a["nonmanifold_edges"] and not a.get("nonmanifold_verts") and
            not a["boundary_edges"] and a["normals"] == "outward"
            and not m016._self_hits(o)[0] and not m012._thin(o, POLISH_LIM)["under"])


def build(render=True, parts=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    log = {}
    fuse_trunk()
    log["trunk"] = dict(TRUNK_LOG)
    objs = {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn, "part", 1000)
    # the hero guard: a leaf grazing the bark can leave a fold (a self-intersection) after the union and cleanup;
    # then every clump turns HERO_YAW_STEP degrees about its own axis and the hero is rebuilt (m019 / m023's guard)
    for attempt in range(HERO_TRIES):
        CLUMP_YAW_JIT[0] = attempt * HERO_YAW_STEP
        h, log["hero"] = _make(HERO, hero, "hero", 4000)
        if _fused_ok(h):
            break
    log["hero"]["attempt"] = attempt if _fused_ok(h) else -1
    log["hero"]["clump_yaw_jit"] = CLUMP_YAW_JIT[0]
    log["clumps"] = dict(CLUMP_INFO)
    _cleanup_tmp()
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    audits = [M.audit(o) for o in order]
    self_hits = {o.name: m016._self_hits(o)[0] for o in order}
    thin = {o.name: m012._thin(o, POLISH_LIM) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = 4000 if o is h else 1000
        if au["tris"] > lim:
            problems.append(f"{o.name}: {au['tris']} tris over {lim}")
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "wire_edges", "loose_verts",
                  "zero_area_faces", "ngons"):
            if au[k]:
                problems.append(f"{o.name}: {k} {au[k]}")
        if au["shells"] != 1:
            problems.append(f"{o.name}: {au['shells']} shells")
        if au["normals"] != "outward":
            problems.append(f"{o.name}: normals {au['normals']}")
        if self_hits[o.name]:
            problems.append(f"{o.name}: {self_hits[o.name]} self-intersecting face pairs")
        if thin[o.name]["under"]:
            problems.append(f"{o.name}: {thin[o.name]['under']} faces with a corner under {POLISH_LIM} deg")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if log["trunk"]["slits"] != len(SLITS):
        problems.append(f"only {log['trunk']['slits']} of {len(SLITS)} slits carved")
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts")} for au in audits],
           "thin": thin, "self_hits": self_hits, "log": log, "problems": problems, "uv": uv,
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order)
        out["total_s"] = round(time.time() - t0, 1)
    return out


# ---- renders -----------------------------------------------------------------------------------------------------------------
def _part_matrix(o):
    return Matrix.Translation(Vector(o[OFF]))


# the sheet's comparison cameras (decision 9): the hero cell is kit front34 (-28, 12); the alternative-drawing cells
SHEET_VIEWS = {"f34_sheet": (-34, 12), "r34_sheet": (-130, 12), "rear_sheet": (-145, 6), "side_sheet": (-80, 6),
               "top_sheet": (-30, 45)}
SHEET_LENS = 3.0        # the sheet's cells are drawn nearly orthographic: the *_sheet shots use a 3x longer lens


def _long_lens(kit):
    orig = kit["render_group"]

    def rg(group, path, azimuth=-22, elevation=20):
        cam = bpy.data.objects["FB_Cam"].data
        lens = cam.lens
        if "_sheet" in path:
            cam.lens = lens * SHEET_LENS
        try:
            return orig(group, path, azimuth, elevation)
        finally:
            cam.lens = lens
    return orig, rg


EXPL = {"FallenSoftwoodLogCutEnd": (-6.2, 0.0, 0.2), "FallenSoftwoodLogBranchStubLarge": (0.9, 0.3, 4.2),
        "FallenSoftwoodLogBranchStubSmall": (6.6, -1.6, 0.9), "FallenSoftwoodLogLeafClump": ((-1.6, -4.4, 0.0),
                                                                                              (2.4, -4.6, 0.0))}


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded Construction: the trunk, the cut-end disc stood up
    facing -X off its left end, the large stub lifted above its foot, the small stub off the right end, two clumps
    below the front."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []

    def put(tag, part, m):
        c = bpy.data.objects.new(f"{PFX}expl_{tag}", by[part].data)
        coll.objects.link(c)
        c.matrix_world = m
        shown.append(c)
    x0 = objs[0].location.x + 60
    base = Matrix.Translation((x0, objs[0].location.y, 0))
    tr = by["FallenSoftwoodLogTrunk"]
    put("trunk", tr.name, base @ _part_matrix(tr))
    ce = by["FallenSoftwoodLogCutEnd"]
    put("cut", ce.name, base @ Matrix.Translation(EXPL[ce.name]))
    for nm in ("FallenSoftwoodLogBranchStubLarge", "FallenSoftwoodLogBranchStubSmall"):
        put(nm[-5:], nm, base @ Matrix.Translation(EXPL[nm]))
    lc = "FallenSoftwoodLogLeafClump"
    for i, p in enumerate(EXPL[lc]):
        put(f"leaf{i}", lc, base @ Matrix.Translation(p) @ Matrix.Rotation(math.radians(40 * i), 4, "Z"))
    bpy.context.view_layer.update()
    return shown


# close-ups (az, el, centre in the build frame, framing radius)
CUT_CU = (-75, 8, (-4.6, -0.2, 1.5), 1.9)
JUNC_CU = (-20, 20, (1.2, 0.2, 3.6), 1.5)


def render_close(objs, path, az, el, centre, radius_):
    kit = K.NS["KIT"]
    fb = kit["frame_box"]
    c = Vector(centre)
    box = [c + Vector((dx, dy, dz)) * radius_ for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    kit["frame_box"] = lambda corners, a_, e_: fb(box, a_, e_)
    ground = bpy.data.objects.get("FB_Ground")
    if ground:
        ground.hide_render = el < 0
    cell = kit["CELL"]
    kit["CELL"] = (480, 400)
    try:
        return kit["render_group"](objs, path, az, el)
    finally:
        kit["CELL"] = cell
        kit["frame_box"] = fb
        if ground:
            ground.hide_render = False


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        if shown:
            extra["exploded"] = (shown, -20, 18)
        for o in objs[1:]:
            az, el = (-62, 10) if o.name.endswith("CutEnd") else (-25, 15)
            extra["part_" + o.name.replace("FallenSoftwoodLog", "").lower()] = ([o], az, el)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            sheet = M.views(NUM, [h], extra=extra)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet}
        if close:
            d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
            off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
            cl = lambda tag, az, el, c, r: render_close([h], f"{d}/{tag}.png", az, el, off @ Vector(c), r)
            out["cut_cu"] = cl("cut_cu", *CUT_CU)
            out["junc_cu"] = cl("junc_cu", *JUNC_CU)
        return out
    finally:
        for o in shown:
            bpy.data.objects.remove(o, do_unlink=True)
        M.display(NUM, objs, TITLE)


# ---- measuring (the study's masks, numpy) -------------------------------------------------------------------------------------
REF_VIEWS = {"f34": (15, 176, 540, 470), "r34": (545, 176, 1010, 470), "front": (12, 540, 290, 730),
             "side": (290, 540, 508, 730), "rear": (508, 540, 768, 730), "top": (768, 540, 1012, 730)}
OUR_VIEWS = {"f34": "f34_sheet", "front": "front34", "r34": "r34_sheet", "side": "side_sheet", "rear": "rear_sheet",
             "top": "top_sheet"}
SHEET_PAPER = (241, 237, 229)


def _hsv(px):
    r, g, b = px[..., 0] / 255, px[..., 1] / 255, px[..., 2] / 255
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0)
    return h, s, mx


def _classes(px, paper=SHEET_PAPER):
    """px (h, w, 3) sRGB 0-255 -> 0 none, 1 L leaves, 2 W cut wood, 3 B bark, 4 O other (the study's m.py cls())."""
    h, s, v = _hsv(px)
    near = np.abs(px - np.array(paper, float)).max(-1) <= 14
    L = (s >= 0.30) & (h >= 62) & (h <= 160) & (px[..., 1] > 50)
    W = (h >= 24) & (h <= 52) & (s >= 0.12) & (s <= 0.58) & (v >= 0.78)
    B = (s >= 0.18) & ((h <= 45) | (h >= 340)) & (v < 0.78)
    out = np.zeros(px.shape[:2], np.uint8)
    out[~near & (v < 0.86)] = 4
    out[B] = 3
    out[W] = 2
    out[L] = 1
    out[near] = 0
    return out


def _load(path, box=None):
    px = K.NS["KIT"]["load_px"](path)[::-1, :, :3] * 255.0
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1]
    return np.clip(px, 0, 255)


def _hex(q):
    return "#" + "".join(f"{int(round(x)):02X}" for x in q)


def _components(mask):
    """4-connected components of a boolean mask: list of (ys, xs) arrays."""
    H, W = mask.shape
    seen = np.zeros_like(mask, bool)
    out = []
    ys, xs = np.nonzero(mask)
    for y0, x0 in zip(ys, xs):
        if seen[y0, x0]:
            continue
        stack = [(y0, x0)]
        seen[y0, x0] = True
        cy, cx = [], []
        while stack:
            y, x = stack.pop()
            cy.append(y)
            cx.append(x)
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    stack.append((yy, xx))
        out.append((np.array(cy), np.array(cx)))
    return out


def slits(px, c, bbox, dpx, bottom=0.12):
    """The dark slits on the bark (the study's cracks.py): dark pixels (v < 0.36, brownish or grey) inside the object,
    above its lowest `bottom` of height, in thin components at least 0.07 D long. Returns [(length px, width px)]."""
    bx0, bx1, by0, by1 = bbox
    h, s, v = _hsv(px)
    dark = (v < 0.36) & ((h <= 45) | (h >= 340) | (s < 0.25)) & (c != 0) & (c != 1)
    m = np.zeros_like(dark)
    ylim = by1 - int((by1 - by0) * bottom)
    m[by0:ylim, bx0:bx1 + 1] = dark[by0:ylim, bx0:bx1 + 1]
    out = []
    for ys, xs in _components(m):
        if len(ys) < 6:
            continue
        L = math.hypot(xs.max() - xs.min(), ys.max() - ys.min())
        wd = len(ys) / max(L, 1)
        if L >= 0.07 * dpx and wd <= 7:
            out.append((round(L), round(wd, 1)))
    return out


def stats(px, paper=SHEET_PAPER):
    c = _classes(px, paper)
    obj = (c >= 1) & (c <= 3)
    cols = np.nonzero(obj.sum(0) >= 3)[0]
    rows = np.nonzero(obj.sum(1) >= 3)[0]
    bx0, bx1, by0, by1 = cols.min(), cols.max(), rows.min(), rows.max()
    W, H = bx1 - bx0, by1 - by0
    sub = c[by0:by1 + 1, bx0:bx1 + 1]
    n = max(1, ((sub >= 1) & (sub <= 3)).sum())
    out = {"wh": round(W / H, 3), "L": round((sub == 1).sum() / n, 3), "W": round((sub == 2).sum() / n, 3),
           "B": round((sub == 3).sum() / n, 3)}
    top = []
    for i in range(21):
        x = bx0 + int(i * W / 20)
        ys = np.nonzero(obj[:, max(0, x - 1):x + 2].any(1))[0]
        top.append(round((by1 - ys.min()) / H, 2) if len(ys) else None)
    out["top"] = top
    pxs = px[by0:by1 + 1, bx0:bx1 + 1]
    for k, lab in ((1, "L"), (2, "W"), (3, "B")):
        sel = pxs[sub == k]
        if len(sel) >= 8:
            srt = sel[np.argsort(sel.sum(1))]
            q = len(srt) // 4
            out[lab + "med"] = _hex(np.median(sel, axis=0))
            out[lab + "lit"] = _hex(np.median(srt[-q:], axis=0))
            out[lab + "shade"] = _hex(np.median(srt[:q], axis=0))
    ys, xs = np.nonzero(sub == 2)
    if len(xs):
        # the cut face: the largest W component
        comps = _components(sub == 2)
        cy, cx = max(comps, key=lambda t: len(t[0]))
        out["cut_face"] = {"f": (round(cx.min() / W, 2), round(cx.max() / W, 2)),
                           "h": (round((H - cy.max()) / H, 2), round((H - cy.min()) / H, 2)),
                           "w_px": int(cx.max() - cx.min()), "h_px": int(cy.max() - cy.min())}
        dpx = (cy.max() - cy.min()) / 0.92
    else:
        dpx = H * 0.6
    sl = slits(px, c, (bx0, bx1, by0, by1), dpx)
    out["slits"] = len(sl)
    out["slit_list"] = sl[:14]
    return out


def measure(views=("f34", "front", "r34", "side", "rear", "top"), our=None):
    """Sheet against our renders, per view (the study's masks on both; the studio floor counts as paper)."""
    ref = M.ref(NUM)
    out = {}
    for vname in views:
        a = stats(_load(ref, REF_VIEWS[vname]))
        name = (our or OUR_VIEWS)[vname]
        ours = _load(f"{M.MODEL_RENDERS}/{M.code(NUM)}/{name}.png")
        corner = tuple(int(x) for x in np.median(ours[:8, :8].reshape(-1, 3), axis=0))
        b = stats(ours, paper=corner)
        err = [abs(x - y) for x, y in zip(a["top"], b["top"]) if x is not None and y is not None]
        out[vname] = {"sheet": a, "ours": b, "prof_err_mean_max": (round(sum(err) / len(err), 3), round(max(err), 2))}
    return out
