"""056 Moss and Ivy (references/056.png): a dressing kit. The hero is a pale warm-stone ruin block, a 7.8 x 4.0 x 4.8
wall chunk of three courses of big chamfered bricks in running bond (26 bricks, a facet crease on every long face, two
broken corners), dressed with low lumpy lime moss cushions on top, four ivy runs of flat five-point leaves on square
stems climbing its faces (front curtain, right-end curtain, back curtain, left-end patch) and lipping over the top
edges, and moss cushions, pale faceted rocks and ivy sprays round its foot. Six overlay parts are the product.

    import importlib, kit_models, m056; importlib.reload(kit_models); importlib.reload(m056); m056.build()

Build frame: studs, long faces front (-Y) and back (+Y), ends left (-X) and right (+X), ground z 0, the stone core
centred at (0, 0): X -3.9..3.9, Y -2.0..2.0, Z 0..4.785. Every object ends with its origin at its bbox bottom centre;
o["m056_offset"] is that origin in the build (or attach) frame, and o["m056_attach"] is the part's attach point in
object coordinates (spec 2.6). W06 owns every MossAndIvy* / MossCushion* / Ivy*Flat name, so the family is Overgrowth*:
- OvergrowthRuinBlock (hero): bricks, cushions, rocks, pebbles, stems, pads, leaves: one object of closed shells.
- OvergrowthMossCushionLarge / Small: one flat-based cushion each, a cauliflower cluster of 7 / 5 overlapping faceted
  sub-domes unioned into one closed shell (attach: base centre, base plane z 0).
- OvergrowthIvyCluster: an upright mat of 22 leaves on three stems from one pad (attach: top centre of the back plane
  y = 0, facing -Y).
- OvergrowthIvyTendril: one square stem with a pad and 8 leaves (attach: the pad centre on the back plane, stem down -Z).
- OvergrowthIvyCorner: an L spray over a horizontal outside edge (attach: the edge line = X axis, top plane z 0 toward
  +Y, face plane y 0 toward -Z).
- OvergrowthIvyLeaf: one leaf with its stalk (attach: the stalk base, blade in the XZ plane facing -Y, hanging).
Colour is painted by height and role (never by facing). Stages 5-6: none (the sheet shows no effect). See
art/blender/renders/models/M056/M056_spec.md.
"""
import math
import random
import time

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M
import m012
import m033
import m047

NUM, TITLE, SHEET = 56, "Moss and Ivy", "M056"
OFF = "m056_offset"
ATT = "m056_attach"
PFX = "_m056_"
HERO = "OvergrowthRuinBlock"
CUSH_L, CUSH_S = "OvergrowthMossCushionLarge", "OvergrowthMossCushionSmall"
CLUSTER, TENDRIL, CORNER, LEAF_P = ("OvergrowthIvyCluster", "OvergrowthIvyTendril", "OvergrowthIvyCorner",
                                    "OvergrowthIvyLeaf")
PART_NAMES = (CUSH_L, CUSH_S, CLUSTER, TENDRIL, CORNER, LEAF_P)

STONE, STONE_D, STONE_L = "m056_stone", "m056_stone_deep", "m056_stone_light"
MOSS, MOSS_D = "m056_moss", "m056_moss_deep"
IVY_L, IVY_G, IVY_D = "m056_ivy_lime", "m056_ivy_green", "m056_ivy_dark"
STEM = "m056_stem"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
BURY = 0.05
CLR = 0.012           # stem and leaf clearance off the stone
HERO_LIMIT = 3850     # decision 14
PART_LIMIT = 1000

# key -> (hex, roughness, low specular). Stage 4 (M056_spec.md "Stage 4") writes the calibrated values here.
PALETTE = {
    STONE: ("#B29A84", 0.9, False),
    STONE_D: ("#847D74", 0.95, False),
    STONE_L: ("#B3A190", 0.9, False),
    MOSS: ("#9AAF10", 0.95, True),
    MOSS_D: ("#4F7301", 0.95, True),
    IVY_L: ("#A5BF0D", 0.8, True),
    IVY_G: ("#447619", 0.8, True),
    IVY_D: ("#215A20", 0.85, True),
    STEM: ("#6E4B22", 0.9, False),
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions), K.sample kinds
TARGETS = {STONE: ((0xD1, 0xB2, 0x92), "all"), STONE_D: ((0x9E, 0x90, 0x84), "all"),
           STONE_L: ((0xD9, 0xBE, 0xA2), "all"), MOSS: ((0xC2, 0xD8, 0x10), "vivid"),
           MOSS_D: ((0x5D, 0x88, 0x02), "vivid"), IVY_L: ((0xC8, 0xDE, 0x0E), "vivid"),
           IVY_G: ((0x4F, 0x8C, 0x1A), "vivid"), IVY_D: ((0x1D, 0x52, 0x18), "vivid"),
           STEM: ((0x8A, 0x5C, 0x2E), "brown")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m056_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k == "m056_" + tail), None) or \
                next((k for k in PALETTE if k.startswith(k1) and k.endswith("_" + tail)), None)
            if k1 in PALETTE and k2 and pct.isdigit():
                K.fk().KIT_PALETTE.pop(key, None)
                K.mix_key(k1, k2, int(pct) / 100)


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome. Returns {key: (hex, rendered)}."""
    keys = keys or list(TARGETS)
    for k in keys:
        K.fk().material(k)
    try:
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


# ---- small helpers -----------------------------------------------------------------------------------------------------
Z = Vector((0.0, 0.0, 1.0))
_mottle = m033._mottle


def _mix(k1, k2, t):
    t = round(max(0.0, min(1.0, t)) * 4) / 4
    return K.mix_key(k1, k2, t)


def _set_tint(a, faces, t):
    for f in faces:
        for l in f.loops:
            l[a.tint_layer] = (t, t, t, 1.0)


def _paint(a, faces, key):
    mi = a._mi(key)
    for f in faces:
        f.material_index = mi


def _orient(bm, fs):
    """Consistent winding over the shell, then outward (positive signed volume)."""
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    for f in fs:
        f.normal_update()
    vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs)
    if vol < 0:
        bmesh.ops.reverse_faces(bm, faces=fs)
        for f in fs:
            f.normal_update()


def _shell(a, pts, polys, key, tint=1.0):
    """One closed shell from points and polygons (indices), oriented outward, one key, one tint."""
    bm = a.bm
    vs = [bm.verts.new(Vector(p)) for p in pts]
    fs = [bm.faces.new([vs[i] for i in poly]) for poly in polys]
    _orient(bm, fs)
    _paint(a, fs, key)
    for f in fs:
        f.smooth = False
    _set_tint(a, fs, tint)
    return vs, fs


def _bridge(pts, ia, ib):
    """Faces between two closed rings (index lists, both counter-clockwise round the vertical): quads for equal
    counts, a fan to an apex, else an angular zipper of triangles."""
    n, m = len(ia), len(ib)
    if n == m:
        return [[ia[k], ia[(k + 1) % n], ib[(k + 1) % n], ib[k]] for k in range(n)]
    if m == 1:
        return [[ia[k], ia[(k + 1) % n], ib[0]] for k in range(n)]
    if n == 1:
        return [[ib[(k + 1) % m], ib[k], ia[0]] for k in range(m)]
    ca = sum((pts[i] for i in ia), Vector()) / n
    cb = sum((pts[i] for i in ib), Vector()) / m
    ang = [math.atan2(pts[i].y - ca.y, pts[i].x - ca.x) for i in ia]
    a0 = ang[0]
    ta = [a0]
    for k in range(1, n):
        ta.append(ta[-1] + (ang[k] - ang[k - 1]) % (2 * math.pi))
    angb = [math.atan2(pts[i].y - cb.y, pts[i].x - cb.x) for i in ib]
    j0 = min(range(m), key=lambda j: abs((angb[j] - a0 + math.pi) % (2 * math.pi) - math.pi))
    ib2 = ib[j0:] + ib[:j0]
    angb = angb[j0:] + angb[:j0]
    tb = [a0 + (angb[0] - a0 + math.pi) % (2 * math.pi) - math.pi]
    for k in range(1, m):
        tb.append(tb[-1] + (angb[k] - angb[k - 1]) % (2 * math.pi))
    ta.append(ta[0] + 2 * math.pi)
    tb.append(tb[0] + 2 * math.pi)
    i = j = 0
    out = []
    while i < n or j < m:
        if j >= m or (i < n and ta[i + 1] <= tb[j + 1]):
            out.append([ia[i % n], ia[(i + 1) % n], ib2[j % m]])
            i += 1
        else:
            out.append([ia[i % n], ib2[(j + 1) % m], ib2[j % m]])
            j += 1
    return out


def _stack(rings):
    """A closed ring stack (bottom to top): bottom cap, bridges, top cap. Returns pts, polys, ring index lists."""
    pts, idx = [], []
    for r in rings:
        idx.append(list(range(len(pts), len(pts) + len(r))))
        pts += [Vector(p) for p in r]
    polys = []
    if len(rings[0]) >= 3:
        polys.append(list(reversed(idx[0])))
    for i in range(len(rings) - 1):
        polys += _bridge(pts, idx[i], idx[i + 1])
    if len(rings[-1]) >= 3:
        polys.append(list(idx[-1]))
    return pts, polys, idx


class Wall:
    """A stone face: o on the face plane at s = 0, z = 0; n outward; u along the face (horizontal)."""

    def __init__(self, name, o, n, u):
        self.name, self.o, self.n, self.u = name, Vector(o), Vector(n), Vector(u)

    def p(self, s, z, d=0.0):
        return self.o + self.u * s + Z * z + self.n * d


WALLS = {"F": Wall("F", (0, -2.0, 0), (0, -1, 0), (1, 0, 0)), "B": Wall("B", (0, 2.0, 0), (0, 1, 0), (1, 0, 0)),
         "R": Wall("R", (3.9, 0, 0), (1, 0, 0), (0, 1, 0)), "L": Wall("L", (-3.9, 0, 0), (-1, 0, 0), (0, 1, 0))}

G = {}          # build state: "bricks" (BVH of every brick), "sol" (m047._Solids of bricks and rocks)
LEAF_INFO = []  # per placed leaf: dict(c, n, area, tone, kind, run)
DROPPED = []


# ---- stone core (spec 2.2) ---------------------------------------------------------------------------------------------
CH = 0.16            # chamfer on the vertical and top edges
J = 0.015            # joint gap
TOP = 3 * 1.6 - J    # 4.785
ROWS = {"F": (-2.0, -2.0 / 3 - J / 2), "M": (-2.0 / 3 + J / 2, 2.0 / 3 - J / 2), "B": (2.0 / 3 + J / 2, 2.0)}
BOND = {("F", 0): (2.6, 2.6, 2.6), ("F", 1): (1.3, 2.6, 2.6, 1.3), ("F", 2): (2.6, 2.6, 2.6),
        ("B", 0): (1.3, 2.6, 2.6, 1.3), ("B", 1): (2.6, 2.6, 2.6), ("B", 2): (1.3, 2.6, 2.6, 1.3),
        ("M", 0): (7.8,), ("M", 1): (7.8,), ("M", 2): (2.6, 2.6, 2.6)}
CHIPS = {("F", 2, 2): ("+x-y", 0.35), ("B", 2, 0): ("-x+y", 0.25)}
COURSE_KEY = {0: (STONE, STONE_D, 0.5), 1: (STONE, STONE, 0.0), 2: (STONE, STONE_L, 0.25)}
BRICK_INFO = []


def plain_box(L, D, H):
    """A plain box (12 tris): the hidden middle-row bars of courses 1-2 (only their end faces show)."""
    hl, hd = L / 2, D / 2
    pts = [Vector((x, y, z)) for z in (0.0, H) for x, y in ((hl, -hd), (hl, hd), (-hl, hd), (-hl, -hd))]
    return pts, [[3, 2, 1, 0], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]], []


def top_box(L, D, H):
    """A box with only its top edges chamfered (20 tris): the middle-row top-course bricks, whose sides are hidden
    between the front and back rows but whose tops and top joints show."""
    hl, hd, e = L / 2, D / 2, CH
    pts = [Vector((x, y, z)) for z in (0.0, H - e) for x, y in ((hl, -hd), (hl, hd), (-hl, hd), (-hl, -hd))]
    pts += [Vector((x, y, H)) for x, y in ((hl - e, -hd + e), (hl - e, hd - e), (-hl + e, hd - e), (-hl + e, -hd + e))]
    polys = [[3, 2, 1, 0], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7],
             [4, 5, 9, 8], [5, 6, 10, 9], [6, 7, 11, 10], [7, 4, 8, 11], [8, 9, 10, 11]]
    return pts, polys, []


def brick_shell(L, D, H, crease=(True, True), chip=None):
    """A chamfered brick (local: x along L, y along D, base z 0) as points and polygons, 36 tris: an octagon section
    (0.16 chamfers on the four vertical edges), a top band chamfered to a flat top, square bottom edges. crease pushes
    one bottom corner of each long face in 0.03, so the face folds along its diagonal (the sheet's two-tone face).
    chip = (corner, size) lowers that top corner into a broken facet. Returns pts, polys, chip vert indices."""
    hl, hd, e = L / 2, D / 2, CH
    oct_ = [(hl, -hd + e), (hl, hd - e), (hl - e, hd), (-hl + e, hd), (-hl, hd - e), (-hl, -hd + e), (-hl + e, -hd),
            (hl - e, -hd)]
    r0 = [Vector((x, y, 0.0)) for x, y in oct_]
    r1 = [Vector((x, y, H - e)) for x, y in oct_]
    top = [Vector((hl - e, -hd + e, H)), Vector((hl - e, hd - e, H)), Vector((-hl + e, hd - e, H)),
           Vector((-hl + e, -hd + e, H))]
    if crease[0]:
        r0[7].y += 0.03
    if crease[1]:
        r0[3].y -= 0.03
    chip_vs = []
    if chip:
        corner, s = chip
        ring_i, top_i, inward = {"+x-y": ((7, 0), 0, Vector((-1, 1, 0))), "-x+y": ((3, 4), 2, Vector((1, -1, 0))),
                                 "+x+y": ((1, 2), 1, Vector((-1, -1, 0))), "-x-y": ((5, 6), 3, Vector((1, 1, 0)))}[corner]
        for i in ring_i:
            r1[i].z -= s * 0.85
        top[top_i] += inward.normalized() * s * 0.55 + Vector((0, 0, -s * 0.45))
        chip_vs = [8 + ring_i[0], 8 + ring_i[1], 16 + top_i]
    pts = r0 + r1 + top
    polys = [list(reversed(range(8)))]
    polys += [[k, (k + 1) % 8, 8 + (k + 1) % 8, 8 + k] for k in range(8)]
    polys += [[8, 9, 17, 16], [9, 10, 17], [10, 11, 18, 17], [11, 12, 18], [12, 13, 19, 18], [13, 14, 19],
              [14, 15, 16, 19], [15, 8, 16], [16, 17, 18, 19]]
    return pts, polys, chip_vs


def stone_core(a):
    """26 bricks: three rows (front, middle, back) by three courses in running bond, with 0.015 joints, a little
    hand-laid jitter (x 0.005, y 0.012, yaw 0.5 deg), two chipped corners. Course tone by height (deep at the foot,
    light on top), per-brick Tint 0.04 and broad mottling 0.02."""
    rng = random.Random(5601)
    BRICK_INFO.clear()
    for k in range(3):
        z0 = -0.02 if k == 0 else 1.6 * k
        z1 = 1.6 * (k + 1) - J
        for row, (y0, y1) in ROWS.items():
            lens = BOND[(row, k)]
            x = -3.9
            for i, ln in enumerate(lens):
                xa = x + (J / 2 if i else 0.0)
                xb = x + ln - (J / 2 if i < len(lens) - 1 else 0.0)
                x += ln
                L, D, H = xb - xa, y1 - y0, z1 - z0
                c = Vector(((xa + xb) / 2 + rng.uniform(-0.005, 0.005), (y0 + y1) / 2 + rng.uniform(-0.012, 0.012), z0))
                yaw = math.radians(rng.uniform(-0.5, 0.5))
                chip = CHIPS.get((row, k, i))
                if row == "M" and k < 2:
                    pts, polys, chip_vs = plain_box(L, D, H)
                elif row == "M":
                    pts, polys, chip_vs = top_box(L, D, H)
                else:
                    pts, polys, chip_vs = brick_shell(L, D, H, chip=chip)
                if rng.random() < 0.5 and not chip:     # the crease's far half alternates per brick
                    for p in pts:
                        p.x = -p.x
                    for poly in polys:
                        poly.reverse()
                mat = Matrix.Translation(c) @ Matrix.Rotation(yaw, 4, "Z")
                pts = [mat @ p for p in pts]
                k1, k2, t = COURSE_KEY[k]
                key = _mix(k1, k2, t) if t else k1
                tint = 1.0 + rng.uniform(-0.04, 0.04)
                vs, fs = _shell(a, pts, polys, key, tint)
                if chip_vs:
                    cv = {vs[i] for i in chip_vs}
                    _paint(a, [f for f in fs if any(v in cv for v in f.verts)], _mix(STONE, STONE_L, 0.5))
                _mottle(a, fs, 0.02, 0.35, 5600 + len(BRICK_INFO))
                G["sol"].add(pts, polys, f"brick{len(BRICK_INFO)}")
                G["brick_tris"].append((pts, polys))
                BRICK_INFO.append({"row": row, "course": k, "c": [round(v, 3) for v in c], "L": round(L, 3)})
    allp, allf = [], []
    for pts, polys in G["brick_tris"]:
        o = len(allp)
        allp += pts
        allf += [[o + i for i in poly] for poly in polys]
    G["bricks"] = BVHTree.FromPolygons(allp, allf)


# ---- rocks (spec 2.5) --------------------------------------------------------------------------------------------------
ROCKS = (  # centre, (W, D, H), yaw, seed
    ((-4.55, -2.5), (1.3, 1.1, 0.8), 20.0, 5611),
    ((4.5, -1.5), (1.0, 1.2, 0.85), -15.0, 5612),
    ((3.6, -2.4), (0.7, 0.6, 0.45), 40.0, 5613),
    ((0.05, 2.95), (1.9, 1.5, 1.3), 8.0, 5614),
)
PEBBLES = (((-2.65, -3.45), 0.5, 5621), ((2.6, 2.55), 0.55, 5622), ((-4.75, 1.25), 0.45, 5623))
ROCK_RINGS = ((0.0, 0.92, 5), (0.34, 1.0, 5), (1.0, 0.5, 3))
PEB_RINGS = ((0.0, 0.92, 4), (0.5, 1.0, 4), (1.0, 0.4, 1))
SINK_ROCK, SINK_PEB = 0.03, 0.03


def rock_shell(c, size, yaw, seed, rings=ROCK_RINGS, z0=-SINK_ROCK):
    """A chunky faceted boulder: explicit rings (flat base, widest low, a shoulder, a sloping 3-vert top). Points and
    polygons in the build frame, plus each face's height fraction."""
    rng = random.Random(seed)
    W, D, H = size
    ph = rng.uniform(0, math.pi * 2)
    slope = rng.uniform(0, math.pi * 2)
    rot = Matrix.Rotation(math.radians(yaw), 3, "Z")
    out = []
    for ri, (hf, rf, n) in enumerate(rings):
        ring = []
        for k in range(n):
            th = ph + 2 * math.pi * k / n + ri * 0.45 + rng.uniform(-0.15, 0.15)
            r = rf * rng.uniform(0.9, 1.08)
            z = H * hf
            if ri == len(rings) - 1:
                z = H * (0.9 + 0.1 * math.cos(th - slope))
            elif ri:
                z += H * rng.uniform(-0.05, 0.05)
            ring.append(rot @ Vector((math.cos(th) * W / 2 * r, math.sin(th) * D / 2 * r, z)) +
                        Vector((c[0], c[1], z0)))
        out.append(ring)
    return _stack(out)


def rocks(a):
    rng = random.Random(5610)
    specs = [(c, s, yaw, seed, ROCK_RINGS) for c, s, yaw, seed in ROCKS] + \
            [(c, (s, s * 0.85, s * 0.6), rng.uniform(0, 180), seed, PEB_RINGS) for c, s, seed in PEBBLES]
    for c, size, yaw, seed, rings in specs:
        pts, polys, idx = rock_shell(c, size, yaw, seed, rings)
        vs, fs = _shell(a, pts, polys, STONE, 1.0 + rng.uniform(-0.04, 0.04))
        z0 = -SINK_ROCK
        for f in fs:
            h = (f.calc_center_median().z - z0) / size[2]
            if h < 0.25:
                f.material_index = a._mi(_mix(STONE, STONE_D, 0.5))
        _mottle(a, fs, 0.03, 0.5, seed)
        G["sol"].add(pts, polys, f"rock{seed}")


# ---- moss cushions (spec 2.3) ------------------------------------------------------------------------------------------
TOP_CUSHIONS = (  # centre (x, y), (W, D, H), lumps, yaw, seed
    ((-0.3, 0.15), (3.4, 2.6, 1.35), 7, 10.0, 5631),
    ((-2.55, -0.35), (2.8, 2.3, 1.15), 6, -25.0, 5632),
    ((1.3, 0.85), (2.6, 2.0, 1.1), 6, 35.0, 5633),
    ((-1.2, -1.4), (2.0, 1.5, 0.86), 5, 5.0, 5634),
)
BASE_CUSHIONS = (  # centre, size, lumps, yaw, seed, wall normal it leans on
    ((0.8, -3.0), (3.3, 2.4, 1.4), 6, 0.0, 5641, (0, -1, 0)),
    ((-1.85, -2.95), (2.6, 2.0, 1.1), 5, 20.0, 5642, (0, -1, 0)),
    ((-3.0, -2.8), (2.2, 1.8, 0.95), 5, -15.0, 5643, (0, -1, 0)),
    ((-4.65, -0.4), (1.75, 2.4, 1.03), 5, 0.0, 5644, (-1, 0, 0)),
    ((-2.45, 2.65), (2.3, 1.9, 1.0), 5, 30.0, 5645, (0, 1, 0)),
    ((4.45, 1.05), (1.8, 2.4, 1.03), 5, -10.0, 5646, (1, 0, 0)),
)
CUSHION_INFO = []


def cushion_shell(c, W, D, H, lumps, yaw, seed):
    """A low lumpy cushion (one closed shell), H : W 0.40-0.45, never a ball: a flat base (a vert per lump), a mid
    ring at about 0.4 h alternating lump (full radius, higher) and valley (0.78, lower) so each lump bulges out and
    the outline scallops, an upper ring of one vert per lump (each lump's own shoulder, so radial creases run down
    between the lumps) and a faceted 3-4 vert crown. Widest in the lower half; the base flat and the full width."""
    rng = random.Random(seed)
    ph = rng.uniform(0, 2 * math.pi)
    rot = Matrix.Rotation(math.radians(yaw), 3, "Z")
    c = Vector(c)

    def at(th, r, z):
        return rot @ Vector((math.cos(th) * W / 2 * r, math.sin(th) * D / 2 * r, z)) + c
    base, mid, up = [], [], []
    for k in range(2 * lumps):
        th = ph + math.pi * k / lumps + rng.uniform(-0.06, 0.06)
        if k % 2 == 0:
            rl = rng.uniform(0.95, 1.03)
            base.append(at(th, rl * 0.9, 0.0))
            mid.append(at(th, rl, H * rng.uniform(0.4, 0.47)))
            up.append(at(th + rng.uniform(-0.1, 0.1), rng.uniform(0.6, 0.69), H * rng.uniform(0.74, 0.86)))
        else:
            mid.append(at(th, rng.uniform(0.7, 0.76), H * rng.uniform(0.26, 0.32)))
    nc = 4 if lumps >= 6 else 3
    crown = [at(ph + 2 * math.pi * (k + 0.3) / nc + rng.uniform(-0.2, 0.2), rng.uniform(0.17, 0.26),
                H * rng.uniform(0.95, 1.0)) for k in range(nc)]
    return _stack([base, mid, up, crown])


def _cushion(a, c, size, lumps, yaw, seed, z0):
    W, D, H = size
    pts, polys, idx = cushion_shell((c[0], c[1], z0), W, D, H, lumps, yaw, seed)
    rng = random.Random(seed + 7)
    vs, fs = _shell(a, pts, polys, MOSS, 1.0 + rng.uniform(-0.03, 0.03))
    for f in fs:
        hf = (f.calc_center_median().z - z0) / H
        t = (0.85 - hf) / 0.5
        if t > 0:
            f.material_index = a._mi(_mix(MOSS, MOSS_D, t))
    _mottle(a, fs, 0.025, 1.1, seed)
    return vs, fs, pts


def top_cushions(a):
    for c, size, lumps, yaw, seed in TOP_CUSHIONS:
        _cushion(a, c, size, lumps, yaw, seed, TOP - 0.02)
        CUSHION_INFO.append({"where": "top", "c": c, "size": size, "lumps": lumps})


def base_cushions(a):
    """Ground cushions: base sunk 0.03; the wall-side rim pressed into the wall, then backed off until no point is
    more than 0.03 inside the stone (ray parity against every brick and rock)."""
    for c, size, lumps, yaw, seed, wn in BASE_CUSHIONS:
        wn = Vector(wn)
        c = Vector((c[0], c[1], 0))
        pts, polys, idx = cushion_shell((c.x, c.y, -0.03), *size, lumps, yaw, seed)
        samp = pts + [sum((pts[i] for i in poly), Vector()) / len(poly) for poly in polys]
        samp += [(pts[poly[i]] + pts[poly[(i + 1) % len(poly)]]) / 2 for poly in polys for i in range(len(poly))]
        shift = Vector()
        for _ in range(16):
            d = max(G["sol"].point(p + shift)[0] for p in samp)
            if d <= 0.03:
                break
            shift += wn * (d - 0.02)
        _cushion(a, c + shift, size, lumps, yaw, seed, -0.03)
        CUSHION_INFO.append({"where": "base", "c": [round(v, 3) for v in (c + shift)[:2]], "size": size,
                             "lumps": lumps, "backed_off": round(shift.length, 3)})


# ---- ivy: leaves, stems, pads (spec 2.4) ------------------------------------------------------------------------------
LEAF_OUT = ((0.0, 0.92), (0.22, 0.60), (0.56, 0.50), (0.40, 0.05), (0.0, 0.0), (-0.40, 0.05), (-0.56, 0.50),
            (-0.22, 0.60))
LEAF_CT = (0.0, 0.38)
R_MAIN, R_BR = 0.13, 0.07
PAD_W, PAD_T = 0.55, 0.10
TONE_DEPTH = {IVY_D: (-0.75, -0.45), IVY_G: (-0.2, 0.3), IVY_L: (0.45, 0.75)}   # notch depth / r off the stem axis
TONE_TILT = {IVY_D: (-4.0, 5.0), IVY_G: (2.0, 10.0), IVY_L: (6.0, 16.0)}
SPREAD = {"wall": (25.0, 75.0), "top": (10.0, 45.0), "ground": (45.0, 85.0), "up": (35.0, 70.0), "tendril": (12.0, 35.0)}


def leaf_points(N, d, nL, size, outline=LEAF_OUT, ct=LEAF_CT):
    """The 16-tri five-point leaf: 8 outline points round the notch N (blade toward d, facing nL), a top centre raised
    0.05 (the midrib crease) and a bottom centre 0.02 under. `outline` may be another closed outline (the IvyLeaf
    part's 10-point one); the two centres always come last."""
    x = d.cross(nL).normalized()
    nL = x.cross(d).normalized()
    out = [N + (x * u + d * v) * size for u, v in outline]
    c = N + (x * ct[0] + d * ct[1]) * size
    return out + [c + nL * 0.05 * size, c - nL * 0.02 * size]


def lens_polys(n):
    """Top fan (from centre n) and bottom fan (from centre n + 1) of an n-point leaf outline."""
    return [[n, i, (i + 1) % n] for i in range(n)] + [[n + 1, (i + 1) % n, i] for i in range(n)]


LEAF_POLYS = lens_polys(8)
# Fix round 1 (verifier minor): the IvyLeaf part's outline has deeper notches between the terminal lobe and the side
# lobes, side lobes pointing out, and a small notch above each basal lobe, so the part reads as an ivy leaf, not a
# pentagon (the sheet's SINGLE IVY LEAF cell). Tip, right notch, right side lobe, right basal notch, right basal lobe,
# stalk notch, then the left side mirrored. The hero keeps the 8-point 16-tri leaf.
LEAF_OUT_PART = ((0.0, 1.0), (0.17, 0.55), (0.56, 0.58), (0.41, 0.31), (0.42, 0.07), (0.0, 0.02), (-0.42, 0.07),
                 (-0.41, 0.31), (-0.56, 0.58), (-0.17, 0.55))
LEAF_CT_PART = (0.0, 0.40)


def _leaf_samples(pts):
    o = pts[:8]
    return pts + [(o[i] + o[(i + 1) % 8]) / 2 for i in range(8)] + [(pts[8] + o[i]) / 2 for i in range(8)]


def leaf(a, pts, key, tint):
    return _shell(a, pts, LEAF_POLYS, key, tint)


def _sd_hero(p):
    """Signed clearance to the stone (every brick and rock) and the ground: negative inside."""
    d_in, _ = G["sol"].point(p)
    if d_in > 0:
        return -d_in
    best = p.z
    for name, lo, hi, t in G["sol"].items:
        if lo.x - 0.6 <= p.x <= hi.x + 0.6 and lo.y - 0.6 <= p.y <= hi.y + 0.6 and lo.z - 0.6 <= p.z <= hi.z + 0.6:
            h = t.find_nearest(p)
            if h[0] is not None:
                best = min(best, h[3])
    return best


def place_leaf(st, tone, rng, sd, size=None, tilt=None, max_push=0.3, push=True):
    """Leaf points for a station st (dict: c, t, n, g, r, side, kind): the notch on the stem's side, the blade turned
    from the hanging direction g toward the side, tilted, layered by tone (dark nearest the stone and spread widest,
    lime outermost: lime wall leaves hang over the stem's front face and hide it), then pushed off along its normal
    until every sample is CLR clear of the stone and ground. None if it can't be."""
    C, t, n, g, r, side = st["c"], st["t"], st["n"], st["g"], st["r"], st["side"]
    sdir = n.cross(t)
    if sdir.length < 1e-4:
        sdir = n.cross(g)
    sdir = sdir.normalized() * side
    cover = st["kind"] == "wall" and st.get("cover", True) and (tone == IVY_L or (tone == IVY_G and rng.random() < 0.55))
    if cover:
        spread = (4.0, 40.0)
    elif tone == IVY_D:
        spread = (max(SPREAD[st["kind"]][0], 40.0), max(SPREAD[st["kind"]][1], 88.0))
    else:
        spread = SPREAD[st["kind"]]
    phi = math.radians(rng.uniform(*spread))
    perp = sdir - g * sdir.dot(g)
    if perp.length < 1e-3:
        perp = n.cross(g) * side
    perp.normalize()
    dw = (g * math.cos(phi) + perp * math.sin(phi)).normalized()
    tl = tilt or st.get("tilt") or TONE_TILT[tone]
    tau = math.radians(rng.uniform(*tl))
    d = dw * math.cos(tau) + n * math.sin(tau)
    nL = n * math.cos(tau) - dw * math.sin(tau)
    if cover:      # over the stem: the notch on its front face, a little to either side
        N = C + sdir * (r * rng.uniform(-0.4, 0.7)) + n * (r + 0.01)
    else:
        N = C + sdir * (r - 0.03) + n * (rng.uniform(*TONE_DEPTH[tone]) * r)
    size = size or rng.uniform(0.92, 0.98)
    res = {"pts": leaf_points(N, d, nL, size), "n": nL.normalized(), "push": 0.0, "size": size}
    return push_clear(res, sd, max_push) if push else res


def push_clear(res, sd, max_push=0.3):
    """Push a leaf along its normal until every sample is CLR clear (None if that takes more than max_push)."""
    pts, nL = res["pts"], res["n"]
    push = 0.0
    for _ in range(8):
        m = min(sd(p) for p in _leaf_samples(pts))
        if m >= CLR - 1e-4:
            break
        dv = CLR - m + 0.003
        push += dv
        if push > max_push:
            return None
        pts = [p + nL * dv for p in pts]
    else:
        return None
    return dict(res, pts=pts, push=round(push, 3))


def stem_shell(pts, normals, r):
    """A square-section stem (one closed shell): a ring of 4 at every point, each in the mitre plane of its kink (flat
    junctions, never smooth sweeps), one face toward the surface normal; flat caps at both ends."""
    n = len(pts)
    rings = []
    for i in range(n):
        if i == 0:
            t = (pts[1] - pts[0]).normalized()
            d1 = d2 = t
        elif i == n - 1:
            t = (pts[-1] - pts[-2]).normalized()
            d1 = d2 = t
        else:
            d1 = (pts[i] - pts[i - 1]).normalized()
            d2 = (pts[i + 1] - pts[i]).normalized()
            t = (d1 + d2).normalized()
        nn = Vector(normals[i])
        s = nn.cross(t)
        if s.length < 1e-5:
            s = t.orthogonal()
        s.normalize()
        w = t.cross(s).normalized()
        kd = d2 - d1
        sc = 1.0
        if kd.length > 1e-5:
            kd.normalize()
            half = d1.angle(d2) / 2
            sc = 1.0 / max(math.cos(half), 0.35)
        ring = []
        for a_, b_ in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
            off = (s * a_ + w * b_) * r
            if sc != 1.0:
                off += kd * off.dot(kd) * (sc - 1.0)
            ring.append(pts[i] + off)
        rings.append(ring)
    allp, polys = [], []
    for ring in rings:
        allp += ring
    polys.append([0, 1, 2, 3])
    for i in range(n - 1):
        b0, b1 = 4 * i, 4 * (i + 1)
        polys += [[b0 + k, b0 + (k + 1) % 4, b1 + (k + 1) % 4, b1 + k] for k in range(4)]
    polys.append([4 * (n - 1) + k for k in (3, 2, 1, 0)])
    return allp, polys


def pad_shell(c, n, u, full=False, w=PAD_W, t=PAD_T):
    """The attachment pad: a square plate w x w x t, back on the surface at c (normal n, edge along u): chamfered top
    only (a frustum, 12 tris), or full (chamfered both faces, 20 tris)."""
    n, u = Vector(n).normalized(), Vector(u).normalized()
    v = n.cross(u).normalized()
    c = Vector(c)

    def sq(h, d):
        return [c + n * d + (u * a_ + v * b_) * h for a_, b_ in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
    if full:
        rings = [sq(w / 2 - 0.05, 0.0), sq(w / 2, t * 0.5), sq(w / 2 - 0.05, t)]
    else:
        rings = [sq(w / 2, 0.0), sq(w / 2 - 0.06, t)]
    pts, polys = [], []
    for ring in rings:
        pts += ring
    polys.append([3, 2, 1, 0])
    for i in range(len(rings) - 1):
        b0, b1 = 4 * i, 4 * (i + 1)
        polys += [[b0 + k, b0 + (k + 1) % 4, b1 + (k + 1) % 4, b1 + k] for k in range(4)]
    polys.append([4 * (len(rings) - 1) + k for k in range(4)])
    return pts, polys


def _surf(w, s, z):
    """How far the stone stands proud of the wall's nominal plane at (s, z) (ray from outside); -0.3 if no stone."""
    o = w.p(s, z, 1.0)
    h = G["bricks"].ray_cast(o, -w.n, 1.6)
    if h[0] is None:
        return -0.3
    return 1.0 - h[3]


def wall_points(w, sz, r):
    """Stem centre points on a wall at the right depth: each segment's clearance is taken from the proudest stone
    under it (sampled every 0.08 along it and +-r across), so the stem's back face stays CLR off the stone."""
    n = len(sz)
    seg = []
    for i in range(n - 1):
        (s0, z0), (s1, z1) = sz[i], sz[i + 1]
        m = max(2, int(math.hypot(s1 - s0, z1 - z0) / 0.08) + 1)
        best = -0.3
        for k in range(m + 1):
            f = k / m
            s, z = s0 + (s1 - s0) * f, z0 + (z1 - z0) * f
            for ds, dz in ((0, 0), (r, 0), (-r, 0), (0, r), (0, -r)):
                best = max(best, _surf(w, s + ds, z + dz))
        seg.append(best)
    out = []
    for i, (s, z) in enumerate(sz):
        if n == 1:
            m_ = _surf(w, s, z)
        else:
            m_ = max(seg[max(i - 1, 0)], seg[min(i, n - 2)])
        out.append(w.p(s, z, max(m_, 0.0) + CLR + r))
    return out


def _point_at_z(pts, z):
    """The point on a polyline (descending) at height z."""
    for p, q in zip(pts, pts[1:]):
        if (p.z - z) * (q.z - z) <= 0 and abs(p.z - q.z) > 1e-6:
            f = (z - p.z) / (q.z - p.z)
            return p + (q - p) * f
    return min(pts, key=lambda p: abs(p.z - z))


# Runs: per wall, stems in order. A stem: id, r, wall path sz [(s, z)], lip=(s, pad_xy) for a top pad and a lip over
# the edge, parent=(stem id, z | "end") to branch off, ground=[(x, y)] to continue along the ground, pad_end on the
# wall, leaves: wall count, lip: top count, gl: ground count.
# Fix round 1 (verifier minor 2): 4 lip / top leaves moved off the top (R1 6 -> 5, R2 5 -> 4, R3 3 -> 1) and, with the
# 32 spare tris, 6 leaves added to the middle band of the r34 curtains (R2 main +1, R2 A +2, R3 L +2, R3 Rb +1).
RUNS = {
    "R1": dict(wall="F", stems=[
        dict(id="main", r=R_MAIN, lip=(1.3, (2.5, -0.8)), lipn=4, n=12,
             sz=[(1.2, 3.9), (1.35, 2.4), (1.15, R_MAIN + 0.006)]),
        dict(id="A", r=R_BR, parent=("main", 3.5), n=5, pad_end=True, sz=[(0.4, 3.55), (-0.3, 3.3)]),
        dict(id="A2", r=R_BR, parent=("A", "end"), n=7, sz=[(-0.6, 2.3), (-0.55, 1.2)]),
        dict(id="B", r=R_BR, parent=("main", 2.1), n=6, sz=[(2.5, 1.55), (3.1, R_BR + 0.006)],
             ground=[(3.0, -2.5), (3.25, -2.9)], gn=4),
        dict(id="C", r=R_BR, parent=("main", 4.1), n=6, sz=[(2.4, 3.95), (3.1, 2.45)]),
    ]),
    "R2": dict(wall="R", stems=[
        dict(id="main", r=R_MAIN, lip=(0.45, (2.9, 0.5)), lipn=5, n=11,
             sz=[(0.35, 3.8), (0.5, 2.2), (0.35, R_MAIN + 0.006)]),
        dict(id="A", r=R_BR, parent=("main", 3.5), n=12, sz=[(-0.8, 2.9), (-1.45, 1.1)]),
        dict(id="W", r=R_BR, parent=("main", 3.1), n=7, sz=[(1.1, 2.95), (1.75, 2.7)],
             wrap=("B", [(3.4, 2.45), (2.75, 1.4)])),
    ]),
    "R3": dict(wall="B", stems=[
        dict(id="main", r=R_MAIN, lip=(-1.0, (-1.0, 1.55)), lipn=3, n=13,
             sz=[(-0.95, 3.8), (-1.1, 2.2), (-1.0, R_MAIN + 0.006)],
             ground=[(-1.25, 2.65), (-1.3, 3.3)], gn=4),
        dict(id="L", r=R_BR, parent=("main", 3.2), n=13, sz=[(-2.2, 2.75), (-3.05, 1.15)]),
        dict(id="Rb", r=R_BR, parent=("main", 2.4), n=8, sz=[(0.1, 2.1), (0.8, 1.1)]),
    ]),
    "R4": dict(wall="L", stems=[
        dict(id="main", r=R_BR + 0.02, n=12, sz=[(0.62, R_BR + 0.026), (0.2, 1.35), (-0.5, 2.45)]),
        dict(id="b", r=R_BR, parent=("main", 1.3), n=4, sz=[(-0.6, 1.25), (-1.3, 0.7)]),
    ]),
}
FRONT_PAD = None


def _run_geometry(run):
    """3D stem polylines for one run: per stem dict(pts, normals, seg (per segment: kind, normal), r, pad)."""
    w = WALLS[run["wall"]]
    out = {}
    for st in run["stems"]:
        r = st["r"]
        pts, nrm, seg = [], [], []
        pad = None
        if "lip" in st:
            s, pxy = st["lip"]
            p0 = Vector((pxy[0], pxy[1], TOP + 0.005 + PAD_T + r - 0.06))
            e = w.p(s, 0.0, 0.0) - w.n * 0.22
            p1 = Vector((e.x, e.y, TOP + CLR + r))
            pc = w.p(s, TOP + CLR + r, max(_surf(w, s, TOP - 0.3), 0.0) + CLR + r)
            pts += [p0, p1, pc]
            nrm += [Z, Z, (Z + w.n).normalized()]
            seg += [("top", Z), ("top", Z), ("wall", w.n)]
            pad = ("top", Vector((pxy[0], pxy[1], TOP + 0.005)))
        if "parent" in st:
            pid, at = st["parent"]
            pp = out[pid]["pts"]
            p = pp[-1].copy() if at == "end" else _point_at_z(pp, at)
            pts.append(p)
            nrm.append(w.n)
        wp = wall_points(w, st["sz"], r)
        pts += wp
        nrm += [w.n] * len(wp)
        seg += [("wall", w.n)] * (len(pts) - 1 - len(seg))
        if "wrap" in st:      # round an outside vertical corner onto the next face
            w2 = WALLS[st["wrap"][0]]
            wp2 = wall_points(w2, st["wrap"][1], r)
            cxy = w.o + w2.o
            zc = (pts[-1].z + wp2[0].z) / 2
            pc = Vector((cxy.x, cxy.y, zc)) + (w.n + w2.n) * (CLR + r)
            pts += [pc] + wp2
            nrm += [(w.n + w2.n).normalized()] + [w2.n] * len(wp2)
            seg += [("wall", w.n), ("wall", w2.n)] + [("wall", w2.n)] * (len(wp2) - 1)
        if st.get("pad_end"):
            s, z = st["sz"][-1]
            dep = max(_surf(w, s, z), 0.0) + 0.005
            pad = ("wall", w.p(s, z, dep))
        if "ground" in st:
            # the foot ring is mitred at 45 deg, so it stands a little higher to keep the ring's corner off the ground
            pts[-1].z = max(pts[-1].z, r * 1.45 + 0.01)
            for x, y in st["ground"]:
                pts.append(Vector((x, y, CLR + r)))
                nrm.append(Z)
                seg.append(("ground", Z))
        out[st["id"]] = {"pts": pts, "normals": nrm, "seg": seg, "r": r, "pad": pad, "spec": st}
    return out


def _stations(geo, run_name, rng):
    """Leaf stations along every stem: lip leaves on the top segments, wall leaves on the wall segments (none below
    z 0.75: the base dressing covers the foot), ground-spray leaves on the ground segments; sides alternate."""
    out = []
    for sid, g in geo.items():
        st = g["spec"]
        pts, seg = g["pts"], g["seg"]
        for kind, count in (("top", st.get("lipn", 0)), ("wall", st.get("n", 0)), ("ground", st.get("gn", 0))):
            if not count:
                continue
            segs = [i for i, (k, _) in enumerate(seg) if k == kind]
            if not segs:
                continue
            lens = [(pts[i + 1] - pts[i]).length for i in segs]
            total = sum(lens)
            start = 0.25 if (kind == "wall" and "parent" in st) else 0.45 if kind == "ground" else 0.1
            usable = []
            acc = 0.0
            for i, ln in zip(segs, lens):
                usable.append((acc, i, ln))
                acc += ln
            for j in range(count):
                u = start + (total - start - 0.1) * (j + 0.5) / count
                for a0, i, ln in usable:
                    if a0 <= u <= a0 + ln + 1e-6:
                        f = (u - a0) / max(ln, 1e-6)
                        break
                p = pts[i] + (pts[i + 1] - pts[i]) * f
                if kind == "wall" and p.z < 0.95:
                    p = None
                if p is None:
                    continue
                t = (pts[i + 1] - pts[i]).normalized()
                n = seg[i][1]
                if kind == "wall":
                    gdir = -Z
                elif kind == "top":
                    gdir = Vector((t.x, t.y, 0.0)).normalized()
                else:
                    gdir = t
                side = 1 if (j + len(out)) % 2 == 0 else -1
                h = p.z / TOP if kind == "wall" else (1.2 if kind == "top" else -0.4)
                out.append({"c": p, "t": t, "n": n, "g": gdir, "r": g["r"], "side": side, "kind": kind,
                            "h": h, "run": run_name, "stem": sid,
                            "tilt": (-38.0, -24.0) if kind == "top" else ((4.0, 14.0) if kind == "ground" else None)})
    return out


def ivy(a):
    """Every run: stems (one closed square shell each), pads, then the leaves, toned by role and height rank (40 %
    lime: upper and lip leaves; 35 % green: bodies; 25 % dark: low, foot sprays), each pushed clear of the stone."""
    rng = random.Random(5650)
    LEAF_INFO.clear()
    DROPPED.clear()
    stations = []
    for rn, run in RUNS.items():
        geo = _run_geometry(run)
        for sid, g in geo.items():
            ps, pl = stem_shell(g["pts"], g["normals"], g["r"])
            vs, fs = _shell(a, ps, pl, STEM, 1.0 + rng.uniform(-0.03, 0.03))
            _mottle(a, fs, 0.03, 0.8, len(stations) + 7)
            if g["pad"]:
                where, c = g["pad"]
                w = WALLS[run["wall"]]
                if where == "top":
                    pp, ppl = pad_shell(c, Z, w.u)
                else:
                    pp, ppl = pad_shell(c, w.n, w.u, full=True)
                _shell(a, pp, ppl, STEM, 1.05 + rng.uniform(-0.02, 0.02))
        stations += _stations(geo, rn, rng)
    # tone by role and height rank (never by facing)
    scores = sorted(range(len(stations)), key=lambda i: -(stations[i]["h"] + rng.uniform(-0.3, 0.3)))
    nl = round(0.34 * len(stations))
    ng = round(0.36 * len(stations))
    tone = {}
    for rank, i in enumerate(scores):
        tone[i] = IVY_L if rank < nl else IVY_G if rank < nl + ng else IVY_D
    for i, st in enumerate(stations):
        if st["kind"] == "ground":
            tone[i] = IVY_D if rng.random() < 0.6 else IVY_G
    placed = {}
    for i, st in enumerate(stations):
        # coverage: of 8 tries (side and angle), keep the leaf whose centre is farthest from the run's leaves so far
        mine = placed.setdefault(st["run"], [])
        cands = []
        for k in range(12):
            st2 = dict(st, side=st["side"] if k % 2 == 0 else -st["side"])
            c = place_leaf(st2, tone[i], rng, _sd_hero, push=False)
            ctr = sum(c["pts"][:8], Vector()) / 8
            low = max(0.0, 0.9 - min(p.z for p in c["pts"][:8])) if st["kind"] == "wall" else 0.0
            score = min([(ctr - q).length for q in mine] or [9.0]) - low
            cands.append((score, c))
        res = None
        for score, c in sorted(cands, key=lambda x: -x[0]):
            res = push_clear(c, _sd_hero)
            if res is not None:
                break
        if res is None:
            DROPPED.append((st["run"], st["stem"], [round(v, 2) for v in st["c"]]))
            continue
        leaf(a, res["pts"], tone[i], 1.0 + rng.uniform(-0.04, 0.04))
        mine.append(sum(res["pts"][:8], Vector()) / 8)
        LEAF_INFO.append({"c": sum(res["pts"][:8], Vector()) / 8, "n": res["n"], "tone": tone[i], "kind": st["kind"],
                          "run": st["run"], "push": res["push"], "size": res["size"]})


def hero_rest(a):
    G["sol"] = m047._Solids()
    G["brick_tris"] = []
    CUSHION_INFO.clear()
    stone_core(a)
    rocks(a)
    top_cushions(a)
    base_cushions(a)
    ivy(a)


# ---- the six overlay parts (spec 2.6) ---------------------------------------------------------------------------------
# Fix round 1: the cushion parts are cauliflower clusters of overlapping rounded sub-domes (the sheet's two cushion
# cells: 6-7 lumps on the large, 4-5 on the small), not one faceted mound. Each lump is a faceted dome (an ellipsoid
# with its rings jittered); the lumps are unioned (exact boolean, at the origin) into one closed shell, cut flat at z 0
# and capped. Lump table per part: centre (x, y) in fractions of (W/2, D/2), horizontal radius and height in studs,
# Y squash.
CUSHION_LUMPS = {
    # sides: (crown, the rest); lats: ring latitudes (deg), then an apex; everything below z 0 is cut off.
    # lumps: (fx, fy, r, h, ky, zc): zc is the ellipsoid centre height as a fraction of h (below 0: a flatter cap)
    "large": dict(size=(3.0, 2.5, 1.25), sides=(7, 5), lats=(-40.0, 12.0, 40.0, 66.0), band=(0.58, 0.45), seed=5631,
                  lumps=(
        (-0.05, 0.12, 1.05, 1.25, 0.85, -0.15),   # the broad high crown, a little back
        (-0.52, 0.06, 0.75, 0.86, 1.0, -0.05),    # left
        (-0.30, -0.44, 0.72, 0.76, 0.95, -0.05),  # front-left
        (0.14, -0.46, 0.74, 0.80, 0.92, -0.05),   # front, the big low front lump
        (0.52, -0.40, 0.60, 0.62, 0.95, -0.05),   # front-right, low
        (0.54, 0.14, 0.70, 0.90, 0.95, -0.05),    # right
        (0.10, 0.46, 0.70, 0.95, 0.9, -0.05),     # back
    )),
    "small": dict(size=(1.8, 1.5, 0.8), sides=(6, 5), lats=(-40.0, 12.0, 40.0, 66.0), band=(0.58, 0.45), seed=5661,
                  lumps=(
        (0.0, 0.10, 0.62, 0.80, 0.86, -0.15),     # the crown
        (-0.50, 0.04, 0.45, 0.52, 1.0, -0.05),    # left
        (0.04, -0.50, 0.48, 0.52, 0.9, -0.05),    # front, the big front lump
        (0.50, -0.06, 0.45, 0.54, 1.0, -0.05),    # right
        (0.26, 0.46, 0.42, 0.52, 0.95, -0.05),    # back-right
    )),
}


def _lump_shell(c, r, ry, h, zc_f, sides, lats, rng):
    """One faceted sub-dome: an ellipsoid whose centre sits at zc_f * h (0: a hemisphere whose widest ring is at the
    ground, so the flat cut base is its full width; below 0: a flatter cap), its rings jittered so the facets read
    hand-cut, alternate rings offset half a facet, a bottom pole well below z 0 (cut away later) and an apex at h."""
    zc = zc_f * h
    b = h - zc
    ph = rng.uniform(0, 2 * math.pi)
    rings = [[Vector((c[0] + rng.uniform(-0.03, 0.03), c[1] + rng.uniform(-0.03, 0.03), zc - b * 0.95))]]
    for li, lat in enumerate(lats):
        la = math.radians(lat + rng.uniform(-4, 4))
        ring = []
        for k in range(sides):
            th = ph + 2 * math.pi * (k + 0.5 * (li % 2)) / sides + rng.uniform(-0.12, 0.12)
            j = rng.uniform(0.94, 1.05)
            ring.append(Vector((c[0] + math.cos(th) * r * math.cos(la) * j,
                                c[1] + math.sin(th) * ry * math.cos(la) * j,
                                zc + b * math.sin(la) * rng.uniform(0.96, 1.04))))
        rings.append(ring)
    rings.append([Vector((c[0] + rng.uniform(-0.06, 0.06) * r, c[1] + rng.uniform(-0.06, 0.06) * ry, h))])
    pts, idx = [], []
    for ring in rings:
        idx.append(list(range(len(pts), len(pts) + len(ring))))
        pts += ring
    polys = []
    for i in range(len(rings) - 1):
        polys += _bridge(pts, idx[i], idx[i + 1])
    return pts, polys


def _union_cut(shells):
    """Exact boolean union of closed shells (pts, polys) on temporary objects at the origin, then bisected at z 0
    (everything below removed) and the cut capped flat. Returns (pts, polys) of one closed shell."""
    objs = []
    try:
        for i, (pts, polys) in enumerate(shells):
            bm = bmesh.new()
            vs = [bm.verts.new(p) for p in pts]
            fs = [bm.faces.new([vs[j] for j in poly]) for poly in polys]
            # planar triangles in, so the union's n-gons are planar and triangulate without folds
            fs = bmesh.ops.triangulate(bm, faces=fs, quad_method="BEAUTY", ngon_method="BEAUTY")["faces"]
            _orient(bm, fs)
            me = bpy.data.meshes.new(f"{PFX}lump{i}")
            bm.to_mesh(me)
            bm.free()
            o = bpy.data.objects.new(f"{PFX}lump{i}", me)
            bpy.context.scene.collection.objects.link(o)
            objs.append(o)
        base = objs[0]
        for p in objs[1:]:
            m = base.modifiers.new("U", "BOOLEAN")
            m.operation, m.solver, m.object = "UNION", "EXACT", p
            p.hide_render = True
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        bm = bmesh.new()
        bm.from_object(base, dg)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.003)
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-4,
                               plane_co=(0, 0, 0), plane_no=(0, 0, 1), clear_inner=True)
        bnd = [e for e in bm.edges if e.is_boundary]
        for v in {v for e in bnd for v in e.verts}:
            v.co.z = 0.0
        bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=bnd, normal=Vector((0, 0, -1)))
        # the union leaves 2-valent verts along straight seams (leftovers of the discarded operand edges); inside an
        # n-gon they triangulate into zero-area slivers, duplicated on both sides of the seam
        bmesh.ops.dissolve_verts(bm, verts=[v for v in bm.verts if len(v.link_edges) == 2])
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                              ngon_method="BEAUTY")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bm.verts.index_update()
        pts = [v.co.copy() for v in bm.verts]
        polys = [[v.index for v in f.verts] for f in bm.faces]
        bm.free()
        return pts, polys
    finally:
        for o in objs:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.meshes.remove(me)


def _paint_cushion(a, fs, z0, H, seed, centres=None, radii=None, band=(0.85, 0.5)):
    """moss over moss_deep by face-centre height within the cushion (spec 5.3: lime above, the lower band darker;
    band = (height fraction where the blend starts, its depth)), never by facing; per-lump Tint +-0.02 (spec 5.6)
    and broad mottling."""
    rng = random.Random(seed + 7)
    base_t = 1.0 + rng.uniform(-0.03, 0.03)
    lump_t = [base_t + rng.uniform(-0.02, 0.02) for _ in (centres or [])]
    for f in fs:
        p = f.calc_center_median()
        t = (band[0] - (p.z - z0) / H) / band[1]
        f.material_index = a._mi(_mix(MOSS, MOSS_D, t) if t > 0 else MOSS)
        if centres:
            k = min(range(len(centres)), key=lambda i: math.hypot((p.x - centres[i][0]) / radii[i][0],
                                                                  (p.y - centres[i][1]) / radii[i][1]))
            _set_tint(a, [f], lump_t[k])
        else:
            _set_tint(a, [f], base_t)
    _mottle(a, fs, 0.025, 1.1, seed)


def lumpy_cushion(a, which):
    """A cushion part: the sub-domes of CUSHION_LUMPS[which] unioned into one closed, flat-based shell."""
    spec = CUSHION_LUMPS[which]
    W, D, H = spec["size"]
    rng = random.Random(spec["seed"])
    shells, centres, radii = [], [], []
    for i, (fx, fy, r, h, ky, zc) in enumerate(spec["lumps"]):
        c = (fx * W / 2, fy * D / 2)
        shells.append(_lump_shell(c, r, r * ky, h, zc, spec["sides"][min(i, 1)], spec["lats"], rng))
        centres.append(c)
        radii.append((r, r * ky))
    pts, polys = _union_cut(shells)
    vs, fs = _shell(a, pts, polys, MOSS)
    _paint_cushion(a, fs, 0.0, H, spec["seed"], centres, radii, spec["band"])
    return vs, fs


def part_cushion_large(a):
    lumpy_cushion(a, "large")
    return Vector((0, 0, 0))


def part_cushion_small(a):
    lumpy_cushion(a, "small")
    return Vector((0, 0, 0))


def _sd_wall_y(p):
    """The attach wall of the hanging parts: solid y > 0."""
    return -p.y


def _sd_corner(p):
    """IvyCorner's attach solid: y > 0 and z < 0 (the top plane z 0 toward +Y, the face plane y 0 toward -Z)."""
    if p.y > 0 and p.z < 0:
        return -min(p.y, -p.z)
    return math.hypot(max(0.0, -p.y), max(0.0, p.z))


def _part_ivy(a, stems, stations_fn, sd, seed, tones):
    """stems: list of (pts, normals, r); pads: list of pad shells (already built); stations_fn(geo) -> stations."""
    rng = random.Random(seed)
    for pts, nrm, r in stems:
        ps, pl = stem_shell(pts, nrm, r)
        vs, fs = _shell(a, ps, pl, STEM, 1.0 + rng.uniform(-0.03, 0.03))
        _mottle(a, fs, 0.03, 0.8, seed)
    sts = stations_fn()
    n = 0
    mine = []
    for i, st in enumerate(sts):
        cands = []
        for k in range(10):
            st2 = dict(st, side=st["side"] if k % 2 == 0 else -st["side"])
            c = place_leaf(st2, tones(i, st), rng, sd, tilt=st.get("tilt"), size=st.get("size"), push=False)
            ctr = sum(c["pts"][:8], Vector()) / 8
            cands.append((min([(ctr - q).length for q in mine] or [9.0]), c))
        res = None
        for score, c in sorted(cands, key=lambda x: -x[0]):
            res = push_clear(c, sd)
            if res is not None:
                break
        if res is None:
            DROPPED.append((seed, i))
            continue
        leaf(a, res["pts"], tones(i, st), 1.0 + rng.uniform(-0.04, 0.04))
        mine.append(sum(res["pts"][:8], Vector()) / 8)
        n += 1
    return n


def _poly_stations(pts, seg_n, count, r, kind, g_fn, start=0.15, end=0.1, side0=1, tilt=None, seg_ok=None):
    lens = [(q - p).length for p, q in zip(pts, pts[1:])]
    ok = [i for i in range(len(lens)) if seg_ok is None or seg_ok(i)]
    total = sum(lens[i] for i in ok)
    acc, table = 0.0, []
    for i in ok:
        table.append((acc, i))
        acc += lens[i]
    out = []
    for j in range(count):
        u = start + (total - start - end) * (j + 0.5) / count
        a0, i = max((t for t in table if t[0] <= u), key=lambda t: t[0])
        f = min(1.0, (u - a0) / max(lens[i], 1e-6))
        p = pts[i] + (pts[i + 1] - pts[i]) * f
        t = (pts[i + 1] - pts[i]).normalized()
        out.append({"c": p, "t": t, "n": Vector(seg_n[i]), "g": g_fn(p, t, j), "r": r,
                    "side": side0 if j % 2 == 0 else -side0, "kind": kind, "tilt": tilt})
    return out


def part_cluster(a):
    """IvyCluster in its attach frame: back plane y 0 (the wall is y > 0), top centre at the origin, facing -Y. One
    pad at the top, three stems fanning down (hidden under the leaves), 22 leaves: the top ones fan out and up (lime),
    the bottom ones hang to a ragged dark point."""
    n = Vector((0, -1, 0))
    u = Vector((1, 0, 0))
    pc = Vector((0, -0.005, -0.85))
    pp, ppl = pad_shell(pc, n, u, full=True)
    _shell(a, pp, ppl, STEM, 1.05)
    d = CLR + R_BR
    paths = [[(0.0, -0.85), (-0.5, -1.0), (-0.9, -1.35), (-0.95, -1.75)],
             [(0.0, -0.85), (0.08, -1.35), (-0.06, -1.85), (0.02, -2.15)],
             [(0.0, -0.85), (0.5, -1.0), (0.9, -1.35), (0.92, -1.8)]]
    stems = [([Vector((x, -d, z)) for x, z in path], [n] * len(path), R_BR) for path in paths]
    counts = (6, 8, 6)

    def g_fn(p, t, j):
        if p.z > -1.15:      # the top fans out and up
            out = Vector((math.copysign(1.0, p.x) if abs(p.x) > 0.05 else (1 if j % 2 else -1), 0, 0))
            return (out * 0.8 + Z * 0.6).normalized()
        return -Z

    def stations():
        c0 = Vector((0.0, -d, -0.85))
        sts = [{"c": c0, "t": -Z, "n": n, "g": Z, "r": R_BR, "side": 1, "kind": "tendril", "tilt": (2.0, 8.0)},
               {"c": c0, "t": -Z, "n": n, "g": -Z, "r": R_BR, "side": -1, "kind": "tendril", "tilt": (2.0, 8.0)}]
        for (pts, nrm, r), cnt in zip(stems, counts):
            sts += _poly_stations(pts, nrm, cnt, r, "wall", g_fn, start=0.05, end=0.0)
        return sts

    def tones(i, st):
        z = st["c"].z
        return IVY_L if z > -1.2 else IVY_G if z > -1.7 else IVY_D
    _part_ivy(a, stems, stations, _sd_wall_y, 5671, tones)
    return Vector((0, 0, 0))


def part_tendril(a):
    """IvyTendril in its attach frame: the pad centre on the back plane y 0 at z 0 (the wall is y > 0), one straight-
    ish square stem down -Z with flat-junction kinks, cut flat at the bottom, 8 leaves alternating, tips down."""
    n = Vector((0, -1, 0))
    u = Vector((1, 0, 0))
    pp, ppl = pad_shell(Vector((0, -0.005, 0.0)), n, u, full=True)
    _shell(a, pp, ppl, STEM, 1.05)
    d = CLR + R_MAIN
    path = [(0.0, 0.05), (0.06, -0.75), (-0.06, -1.55), (0.07, -2.35), (-0.04, -3.1), (0.02, -3.75)]
    stems = [([Vector((x, -d, z)) for x, z in path], [n] * len(path), R_MAIN)]

    def stations():
        sts = _poly_stations(stems[0][0], stems[0][1], 8, R_MAIN, "wall", lambda p, t, j: -Z, start=0.45, end=0.3)
        for s_ in sts:
            s_["kind"], s_["size"] = "tendril", 0.88
        return sts

    def tones(i, st):
        return (IVY_G, IVY_L, IVY_G, IVY_G, IVY_L, IVY_G, IVY_D, IVY_G)[i % 8]
    _part_ivy(a, stems, stations, _sd_wall_y, 5672, tones)
    return Vector((0, 0, 0))


def part_corner(a):
    """IvyCorner in its attach frame: the edge line is the X axis, the top plane z 0 runs toward +Y, the face plane
    y 0 runs down -Z (the solid is y > 0, z < 0). One stem bent 90 deg over the edge from a pad on the top; a top arm
    of 8 lime leaves lying on the top and a hanging arm of 10 darker leaves down the face."""
    r = R_MAIN
    pp, ppl = pad_shell(Vector((0.1, 2.0, 0.005)), Z, Vector((1, 0, 0)))
    _shell(a, pp, ppl, STEM, 1.05)
    nf = Vector((0, -1, 0))
    pts = [Vector((0.1, 2.0, 0.005 + PAD_T + r - 0.06)), Vector((-0.05, 1.2, CLR + r)), Vector((0.05, 0.45, CLR + r)),
           Vector((0.0, -(CLR + r), CLR + r)), Vector((-0.08, -(CLR + r), -0.7)), Vector((0.08, -(CLR + r), -1.4)),
           Vector((-0.02, -(CLR + r), -2.0))]
    nrm = [Z, Z, Z, (Z + nf).normalized(), nf, nf, nf]
    seg_n = [Z, Z, Z, nf, nf, nf]
    stems = [(pts, nrm, r)]

    def stations():
        # fix round 1 (verifier minor): the top arm's leaves point back along the top (+Y) and tilt up 15-30 deg, so
        # they rise and fan toward the viewer as in the CORNER PIECE cell instead of lying flat as a sliver
        top = _poly_stations(pts, seg_n, 8, r, "top", lambda p, t, j: Vector((0, 1, 0)), start=0.25, end=0.05,
                             tilt=(15.0, 30.0), seg_ok=lambda i: i < 3)
        for s in top:
            s["kind"] = "up"
        hang = _poly_stations(pts, seg_n, 10, r, "wall", lambda p, t, j: -Z, start=0.25, end=0.0,
                              seg_ok=lambda i: i >= 3)
        return top + hang

    def tones(i, st):
        if i < 8:
            return IVY_L
        return (IVY_G, IVY_D, IVY_G, IVY_D, IVY_G, IVY_D, IVY_D, IVY_G, IVY_D, IVY_D)[(i - 8) % 10]
    _part_ivy(a, stems, stations, _sd_corner, 5673, tones)
    return Vector((0, 0, 0))


def part_leaf(a):
    """IvyLeaf in its attach frame: the stalk base at the origin, a 3-sided stalk 0.36 long (dia 0.07) down to the
    blade's notch, the blade in the XZ plane facing -Y, hanging (tip down)."""
    N = Vector((0, 0, -0.33))
    pts = leaf_points(N, -Z, Vector((0, -1, 0)), 0.92, LEAF_OUT_PART, LEAF_CT_PART)
    _shell(a, pts, lens_polys(len(LEAF_OUT_PART)), IVY_G, 1.0)
    rr = 0.035
    ring = lambda z: [Vector((math.cos(th) * rr, math.sin(th) * rr - 0.01, z)) for th in (0.3, 2.4, 4.5)]
    sp = ring(0.0) + ring(-0.36)
    spl = [[2, 1, 0], [0, 1, 4, 3], [1, 2, 5, 4], [2, 0, 3, 5], [3, 4, 5]]
    _shell(a, sp, spl, IVY_G, 0.9)
    return Vector((0, 0, 0))


PARTS = ((CUSH_L, part_cushion_large), (CUSH_S, part_cushion_small), (CLUSTER, part_cluster),
         (TENDRIL, part_tendril), (CORNER, part_corner), (LEAF_P, part_leaf))
ATTACH_NOTES = {
    CUSH_L: "attach: base centre, base plane z 0 (sink 0.02-0.05 into an up-facing surface; slopes <= 15 deg)",
    CUSH_S: "attach: base centre, base plane z 0 (sink 0.02-0.05 into an up-facing surface; slopes <= 15 deg)",
    CLUSTER: "attach: top centre of the back plane y 0, facing -Y; back flat on a wall face, top at or under the wall top",
    TENDRIL: "attach: pad centre on the back plane y 0, stem down -Z; the next segment's pad hides this flat-cut end",
    CORNER: "attach: the edge line (X axis), top plane z 0 toward +Y, face plane y 0 toward -Z; any 90 deg outside "
            "top edge",
    LEAF_P: "attach: stalk base, blade in the XZ plane facing -Y, hanging; scatter or hand-place",
}
NOTES = {
    HERO: "056 Moss and Ivy hero: a 7.8 x 4.0 x 4.8 three-course chamfered-brick ruin block (26 bricks, running bond) "
          "with lumpy moss cushions on top, four ivy runs of flat five-point leaves on square stems lipping over the "
          "edges, cushions, rocks and ivy sprays at the foot. Players can stand on the top. No VFX (the sheet shows "
          "none).",
}
NOTES.update({k: f"056 overlay part. {v}. No collision: it dresses other assets." for k, v in ATTACH_NOTES.items()})
COLLISION = {HERO: "hull", **{k: "none" for k in PART_NAMES}}


# ---- objects ----------------------------------------------------------------------------------------------------------
def _new(name, fn, role, budget, temp=False):
    old = bpy.data.objects.get(name)
    if old:
        if old.get("kit_sheet") not in (None, SHEET) and not temp:
            raise RuntimeError(f"{name} belongs to {old.get('kit_sheet')}")
        for c in list(old.children_recursive):
            bpy.data.objects.remove(c, do_unlink=True)
        me = old.data
        bpy.data.objects.remove(old, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    a = K.fk().Asset(name, f"{SHEET} {TITLE}", seed=7, tint_var=0.0)
    att = fn(a)
    o = a.finish(collection=M.coll(NUM, TITLE), mark_asset=not temp, origin=None)
    K.drop_unused_slots(o)
    if not temp:
        K.tag(o, SHEET, TITLE, role, COLLISION[name], budget, NOTES[name])
    if name in (HERO, CUSH_L, CUSH_S):
        o["kit_shading_ok"] = ("moss is lime over a darker yellow-green lower band, coloured by height within each "
                               "cushion (spec 5.3, decision 12), a material region, not light")
    o[OFF] = [0.0, 0.0, 0.0]
    o["m056_attach_build"] = list(att) if att is not None else [0.0, 0.0, 0.0]
    o.location = (0, 0, 0)
    bpy.context.view_layer.update()
    return o


def _recentre(o):
    bc = m012._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()
    o[ATT] = [round(x, 4) for x in Vector(o["m056_attach_build"]) - Vector(o[OFF])]


def _post(o):
    """Stage 2-3 pass on an object of closed shells: triangles only (built outward, so no recalc that could flip a
    thin leaf), each shell's volume checked and reversed if inward, flat shading, origin at the bbox bottom centre,
    bowties split, angle-based UVs with overlaps cut free."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    groups = [[] for _ in range(n)]
    for f in bm.faces:
        groups[ids[f.index]].append(f)
    flipped = 0
    for fs in groups:
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs)
        if vol < 0:
            bmesh.ops.reverse_faces(bm, faces=fs)
            flipped += 1
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = False
    if o.data.has_custom_normals:
        with M._override(o):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
    _recentre(o)
    lg = {"flipped_shells": flipped, "bowties": M.fix_bowties(o)}
    M.smart_uv(o, **UV)
    lg["uv_cut"] = m012._uv_unfold(o)
    K.drop_unused_slots(o)
    return lg


def _make(name, fn, role="part", budget=PART_LIMIT, temp=False):
    t0 = time.time()
    o = _new(name, fn, role, budget, temp=temp)
    lg = _post(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


# ---- checks -----------------------------------------------------------------------------------------------------------
def _keys(o):
    return [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]


def _kind_of(keys, dz):
    if any(k.startswith("m056_stone") for k in keys):
        return "brick" if dz > 1.4 else "rock"
    if any(k.startswith("m056_moss") for k in keys):
        return "moss"
    if any(k.startswith("m056_ivy") for k in keys):
        return "leaf"
    return "stem"


def _shells(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = _keys(o)
    groups = [[] for _ in range(n)]
    for f in bm.faces:
        groups[ids[f.index]].append(f)
    kinds = []
    for fs in groups:
        zs = [v.co.z for f in fs for v in f.verts]
        kinds.append(_kind_of({keys[f.material_index] for f in fs}, max(zs) - min(zs)))
    return bm, ids, n, groups, kinds


def shells_report(o):
    """Per shell: kind, tris, non-manifold edges and verts, boundary edges, winding errors (manifold edges whose two
    faces don't run the same way round), self-intersecting face pairs, signed volume."""
    bm, ids, n, groups, kinds = _shells(o)
    out = []
    for k in range(n):
        fs = groups[k]
        es = {e for f in fs for e in f.edges}
        vs = list({v for f in fs for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        hits = sum(1 for a_, b_ in tree.overlap(tree) if a_ < b_ and not set(fs[a_].verts) & set(fs[b_].verts))
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) / 3.0
        out.append({"kind": kinds[k], "tris": len(fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary),
                    "winding_errors": sum(1 for e in es if e.is_manifold and not e.is_contiguous),
                    "self_hits": hits, "volume": round(vol, 5)})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating dressing (STAGES): per shell, whether it touches another shell (triangles intersect, or a vertex
    within `tol` of another shell's surface) or the ground (build z 0), and whether it chains by contact to an anchor
    (the hero: shells on the ground; a part: its base on z 0 for the cushions, its biggest stem for the ivy)."""
    bm, ids, n, groups, kinds = _shells(o)
    off = Vector(o[OFF])
    fsh = [ids[f.index] for f in bm.faces]
    vsh = {}
    for f in bm.faces:
        for v in f.verts:
            vsh[v.index] = fsh[f.index]
    tree = BVHTree.FromBMesh(bm)
    zmin = [1e9] * n
    for v in bm.verts:
        if v.index in vsh:
            zmin[vsh[v.index]] = min(zmin[vsh[v.index]], v.co.z + off.z)
    pairs = set()
    for i, j in tree.overlap(tree):
        a_, b_ = fsh[i], fsh[j]
        if a_ != b_:
            pairs.add((min(a_, b_), max(a_, b_)))
    near = {}
    for v in bm.verts:
        s = vsh.get(v.index)
        if s is None:
            continue
        for loc, _, fi, d in tree.find_nearest_range(v.co, chain_tol):
            t = fsh[fi]
            if t != s:
                kk = (min(s, t), max(s, t))
                near[kk] = min(near.get(kk, 1e9), d)
    for kk in pairs:
        near[kk] = 0.0
    gap = [1e9] * n
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    if o.name in (CLUSTER, TENDRIL, CORNER, LEAF_P):
        big = max(range(n), key=lambda k: (kinds[k] == "stem", len(groups[k])))
        ground = {big}
    else:
        ground = {k for k in range(n) if zmin[k] <= tol}
    for k in range(n):
        if zmin[k] <= tol and o.name not in (CLUSTER, TENDRIL, CORNER, LEAF_P):
            gap[k] = 0.0
    for k in ground:
        gap[k] = 0.0

    def chained(t):
        adj = {k: set() for k in range(n)}
        for (a_, b_), d in near.items():
            if d <= t:
                adj[a_].add(b_)
                adj[b_].add(a_)
        seen = set(ground)
        stack = list(seen)
        while stack:
            k = stack.pop()
            for m_ in adj[k]:
                if m_ not in seen:
                    seen.add(m_)
                    stack.append(m_)
        return [k for k in range(n) if k not in seen]
    floating = [k for k in range(n) if gap[k] > tol]
    unch = chained(tol)

    def where(k):
        vs = {v for f in groups[k] for v in f.verts}
        c = sum((v.co for v in vs), Vector()) / len(vs) + off
        return [round(x, 2) for x in c]
    res = {"shells": n, "floating": len(floating), "floating_at": [(kinds[k], where(k)) for k in floating[:6]],
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "unchained": len(unch), "unchained_at": [(kinds[k], where(k)) for k in unch[:6]],
           "kinds": {k: kinds.count(k) for k in sorted(set(kinds))}}
    bm.free()
    return res


def bury_report(o):
    """STAGES "nothing buried": every dressing shell (leaf, stem, pad, moss) tested by ray parity against every stone
    shell (each brick and rock), every rock against the bricks; depth = the distance from its deepest vert or face
    centre inside to that stone's surface."""
    bm, ids, n, groups, kinds = _shells(o)
    bricks, rocks_ = m047._Solids(), m047._Solids()
    for k in range(n):
        if kinds[k] in ("brick", "rock"):
            vs = list({v for f in groups[k] for v in f.verts})
            vi = {v: i for i, v in enumerate(vs)}
            (bricks if kinds[k] == "brick" else rocks_).add([v.co for v in vs],
                                                             [[vi[v] for v in f.verts] for f in groups[k]], f"{kinds[k]}{k}")
    res, rk = [], []
    off = Vector(o[OFF])
    for k in range(n):
        if kinds[k] == "brick":
            continue
        fs = groups[k]
        pts = list({v.co.copy().freeze() for f in fs for v in f.verts}) + [f.calc_center_median() for f in fs]
        d1, w1 = max((bricks.point(Vector(p)) for p in pts), key=lambda r: r[0])
        if kinds[k] == "rock":
            if d1 > 0:
                rk.append((round(d1, 3), w1))
            continue
        d2, w2 = max((rocks_.point(Vector(p)) for p in pts), key=lambda r: r[0])
        d, who = (d1, w1) if d1 >= d2 else (d2, w2)
        if d > 0:
            c = sum((f.calc_center_median() for f in fs), Vector()) / len(fs) + off
            res.append((round(d, 3), kinds[k], who, [round(x, 2) for x in c]))
    bm.free()
    res.sort(key=lambda r: -r[0])
    rk.sort(key=lambda r: -r[0])
    return {"dressing_shells": sum(1 for k in kinds if k in ("leaf", "stem", "moss")),
            "over_0.05": sum(1 for r in res if r[0] > BURY), "max": res[0][0] if res else 0.0, "worst": res[:6],
            "rocks_in_bricks_over_0.05": sum(1 for r in rk if r[0] > BURY), "rocks_in_bricks": rk[:4]}


def _cam(az, el):
    a_, e_ = math.radians(az), math.radians(el)
    return Vector((math.sin(a_) * math.cos(e_), -math.cos(a_) * math.cos(e_), math.sin(e_)))


def leaf_report():
    """Hero leaves: count, tone and kind shares, size, the edge-on share at f34 (-47, 12) (leaves within 12 deg of
    edge-on, area weighted), leaves whose normal is more than 75 deg from both 3/4 cameras, undersides facing both."""
    if not LEAF_INFO:
        return {}
    f34, r34 = _cam(-47, 12), _cam(133, 12)
    n = len(LEAF_INFO)
    tones = {k: sum(1 for l in LEAF_INFO if l["tone"] == k) for k in (IVY_L, IVY_G, IVY_D)}
    edge = sum(l["size"] ** 2 for l in LEAF_INFO if abs(l["n"].dot(f34)) < math.sin(math.radians(12))
               and l["kind"] != "ground" and l["run"] in ("R1", "R4"))
    tot = sum(l["size"] ** 2 for l in LEAF_INFO if l["kind"] != "ground" and l["run"] in ("R1", "R4"))
    far = sum(1 for l in LEAF_INFO if l["kind"] == "wall" and
              max(l["n"].dot(f34), l["n"].dot(r34)) < math.cos(math.radians(75)))
    far_all = [(l["kind"], [round(x, 2) for x in l["c"]]) for l in LEAF_INFO
               if max(l["n"].dot(f34), l["n"].dot(r34)) < math.cos(math.radians(75))]
    under = sum(1 for l in LEAF_INFO if l["n"].dot(f34) < 0 and l["n"].dot(r34) < 0)
    return {"leaves": n, "tones": {k[5:]: round(v / n, 2) for k, v in tones.items()},
            "kinds": {k: sum(1 for l in LEAF_INFO if l["kind"] == k) for k in ("wall", "top", "ground")},
            "runs": {r: sum(1 for l in LEAF_INFO if l["run"] == r) for r in RUNS},
            "size_median": round(sorted(l["size"] for l in LEAF_INFO)[n // 2] * 1.12, 3),
            "edge_on_f34_share_R1_R4": round(edge / max(tot, 1e-6), 3), "wall_over_75_from_both": far, "any_over_75_from_both": far_all,
            "undersides_both": under, "pushed": sum(1 for l in LEAF_INFO if l["push"] > 0),
            "push_max": max(l["push"] for l in LEAF_INFO), "dropped": len(DROPPED), "dropped_at": DROPPED[:6]}


TARGET_SIZE = ((11.0, 0.5), (7.9, 0.5), (6.05, 0.3))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m056_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", "Overgrowth"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build_hero():
    M.coll(NUM, TITLE)
    palette()
    h, lg = _make(HERO, hero_rest, "hero", 4000)
    return h, lg


def build(render=True, parts=True, close=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    h, log[HERO] = _make(HERO, hero_rest, "hero", 4000)
    li = leaf_report()
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn)
    _cleanup_tmp()
    order = [h] + [objs[n] for n in PART_NAMES if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    audits = [M.audit(o) for o in order]
    shells = {o.name: shells_report(o) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = HERO_LIMIT if o is h else PART_LIMIT
        if au["tris"] > lim:
            problems.append(f"{o.name}: {au['tris']} tris over {lim}")
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "wire_edges", "loose_verts",
                  "zero_area_faces", "ngons"):
            if au[k]:
                problems.append(f"{o.name}: {k} {au[k]}")
        if au["normals"] != "outward":
            problems.append(f"{o.name}: normals {au['normals']}")
        for i, s in enumerate(shells[o.name]):
            for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "winding_errors", "self_hits"):
                if s[k]:
                    problems.append(f"{o.name} shell {i} ({s['kind']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['kind']}): not closed outward (volume {s['volume']})")
    contact = {o.name: contact_report(o) for o in order}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} shells touch nothing within {CONTACT} {c['floating_at']}, "
                            f"{c['unchained']} have no chain of contact to an anchor {c['unchained_at']}")
    bury = {h.name: bury_report(h)}
    for n_, b in bury.items():
        if b["over_0.05"]:
            problems.append(f"{n_}: {b['over_0.05']} dressing shells more than {BURY} inside stone (worst {b['worst'][:3]})")
        if b["rocks_in_bricks_over_0.05"]:
            problems.append(f"{n_}: {b['rocks_in_bricks_over_0.05']} rocks more than {BURY} into the bricks")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    for o in order:
        if [c for c in o.children if c.get("vfx_kind")]:
            problems.append(f"{o.name}: has VFX sockets (decision 13: none)")
    if li.get("dropped"):
        problems.append(f"{HERO}: {li['dropped']} leaves dropped by the placement guard {li['dropped_at']}")
    winding = {o.name: sum(s["winding_errors"] for s in shells[o.name]) for o in order}
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    kinds = {}
    for s in shells[HERO]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts", "origin_offset", "transforms_applied")} for au in audits],
           "hero_shells": kinds, "contact": contact, "bury": bury, "winding": winding, "leaves": li,
           "cushions": CUSHION_INFO, "log": log, "problems": problems, "uv": uv,
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "attach": {o.name: list(o.get(ATT, [])) for o in order},
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders ----------------------------------------------------------------------------------------------------------
# decisions 2 and 3: f34 at (-47, 12), r34 at (133, 12), the front / rear redraws at (-44, 8) / (128, 8); side and top
# judged on content. *_sheet shots use the long lens with the floor hidden (m033._long_lens).
SHEET_VIEWS = {"f34_sheet": (-47, 12), "r34_sheet": (133, 12), "front_sheet": (-44, 8), "rear_sheet": (128, 8),
               "side_sheet": (111, 8), "top_sheet": (0, 89)}
VIEW_NAMES = ("front", "side", "rear", "top", "underside")
PARTS_SHOT = (-25, 20)
SCALE_AT = ((-2.0, -3.4, 0.0), (2.4, 0.0, TOP))


def _marker(h, at, name):
    a = K.fk().Asset(PFX + name, "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=STONE_D, tint=0.6)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=STONE_D, tint=0.6)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=STONE_D, tint=0.6)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    c.location = _at(h, at)
    bpy.context.view_layer.update()
    return c


def _at(o, p):
    """Build-frame point p in world space for object o."""
    return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)


def _temp_obj(name, fn):
    a = K.fk().Asset(PFX + name, "probe", seed=1, tint_var=0.0)
    fn(a)
    o = a.finish(collection=M.coll(NUM, TITLE), mark_asset=False, origin=None)
    bpy.context.view_layer.update()
    return o


def _copy(o, name, m):
    """A linked copy of part o placed so its attach frame sits at world matrix m."""
    c = bpy.data.objects.new(PFX + name, o.data)
    M.coll(NUM, TITLE).objects.link(c)
    c.matrix_world = m @ Matrix.Translation(-Vector(o["m056_attach_build"])) @ Matrix.Translation(Vector(o[OFF]))
    return c


def _exploded(objs, base):
    """The sheet's exploded: four double bricks pulled apart (two per course), two cushions above with gaps, an ivy
    tendril and the cluster (a draping curtain) to the right."""
    by = {o.name: o for o in objs}

    def body(a):
        rng = random.Random(3)
        for i, (x, z) in enumerate(((-1.6, 2.4), (1.6, 2.4), (-1.3, 0.0), (1.9, 0.0))):
            pts, polys, _ = brick_shell(2.585, 1.33, 1.585, chip=("+x-y", 0.25) if i == 1 else None)
            pts = [p + Vector((x, 0, z)) for p in pts]
            _shell(a, pts, polys, STONE, 1.0 + rng.uniform(-0.04, 0.04))
    shown = [_temp_obj("expl_bricks", body)]
    shown[0].matrix_world = base
    if CUSH_L in by:
        shown.append(_copy(by[CUSH_L], "expl_cl", base @ Matrix.Translation((-1.2, 0.2, 5.6))))
    if CUSH_S in by:
        shown.append(_copy(by[CUSH_S], "expl_cs", base @ Matrix.Translation((1.8, 0.3, 5.4))))
    if CLUSTER in by:
        shown.append(_copy(by[CLUSTER], "expl_ic", base @ Matrix.Translation((4.6, -0.9, 4.4))))
    if TENDRIL in by:
        shown.append(_copy(by[TENDRIL], "expl_it", base @ Matrix.Translation((6.9, -0.9, 5.2))))
    bpy.context.view_layer.update()
    return shown


def _attach_shot(objs, base):
    """Each overlay part on a plain box in its attach frame: the cushions on a box top, the cluster and the tendril
    back-flat on a wall face under its top, the corner over the wall's top edge, the leaf on the ground."""
    by = {o.name: o for o in objs}

    def boxes(a):
        for x0, w, h in ((-7.0, 3.4, 1.6), (-3.0, 7.6, 5.0), (5.2, 3.0, 4.0)):
            pts, polys, _ = brick_shell(w, 2.4, h, crease=(False, False))
            _shell(a, [p + Vector((x0 + w / 2, 1.2, 0)) for p in pts], polys, STONE_L, 1.0)
    shown = [_temp_obj("att_boxes", boxes)]
    shown[0].matrix_world = base
    put = []
    if CUSH_L in by:
        put.append((CUSH_L, Matrix.Translation((-5.3, 1.2, 1.6 - 0.03))))
    if CUSH_S in by:
        put.append((CUSH_S, Matrix.Translation((6.7, 1.3, 4.0 - 0.03))))
    if CLUSTER in by:
        put.append((CLUSTER, Matrix.Translation((-1.6, 0.0, 5.0 - CH))))
    if TENDRIL in by:
        put.append((TENDRIL, Matrix.Translation((2.4, 0.0, 4.6))))
    if CORNER in by:
        put.append((CORNER, Matrix.Translation((6.7, 0.0, 4.0))))
    if LEAF_P in by:
        put.append((LEAF_P, Matrix.Translation((0.6, -1.6, 0.02)) @ Matrix.Rotation(math.radians(-80), 4, "X")))
    for name, m in put:
        shown.append(_copy(by[name], "att_" + name, base @ m))
    bpy.context.view_layer.update()
    return shown


def render_views(objs, close=True):
    h = objs[0]
    base = Matrix.Translation((h.location.x + 40, h.location.y, 0))
    shown = _exploded(objs, base) if len(objs) > 1 else []
    att = _attach_shot(objs, Matrix.Translation((h.location.x + 70, h.location.y, 0))) if len(objs) > 1 else []
    markers = [_marker(h, SCALE_AT[0], "char1"), _marker(h, SCALE_AT[1], "char2")]
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        extra["front34"] = ([h], -47, 12)
        extra["rear34"] = ([h], 133, 12)
        for o in objs[1:]:
            extra["part_" + o.name.replace("Overgrowth", "").lower()] = ([o], *PARTS_SHOT)
        if shown:
            extra["exploded"] = (shown, -40, 16)
        if att:
            extra["attach"] = (att, -30, 16)
        extra["scale"] = ([h] + markers, -47, 6)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = m033._long_lens(kit)
        try:
            sheet = M.views(NUM, [h], names=VIEW_NAMES, extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet}
        if close:
            out.update(render_close_ups(objs))
        return out
    finally:
        for o in shown + att + markers:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me.users == 0 and me.name.startswith(PFX):
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def render_close_ups(objs):
    """moss_cu (top cushions and the front-left top edge, close-up 1), curtain_cu (the front curtain R1), pad_cu (the
    front-face pad from below, close-up 2), junction_cu (leaves layered round the back-right corner, close-up 3),
    corner_cu (the IvyCorner part), leaf_cu (the IvyLeaf part), cushion_cu (the two cushion parts)."""
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    by = {o.name: o for o in objs}
    h = objs[0]
    rc = m033.render_close
    out = {"moss_cu": rc([h], f"{d}/moss_cu.png", -30, 20, _at(h, (-1.6, -1.2, 5.0)), 1.9),
           "curtain_cu": rc([h], f"{d}/curtain_cu.png", -30, 8, _at(h, (1.5, -2.3, 2.5)), 2.9),
           "pad_cu": rc([h], f"{d}/pad_cu.png", -10, -35, _at(h, (-0.3, -2.1, 3.3)), 0.9),
           "junction_cu": rc([h], f"{d}/junction_cu.png", 125, 10, _at(h, (3.9, 1.6, 2.6)), 2.2),
           "lip_cu": rc([h], f"{d}/lip_cu.png", -20, 30, _at(h, (2.6, -1.5, 4.7)), 1.6)}
    if CORNER in by:
        out["corner_cu"] = rc([by[CORNER]], f"{d}/corner_cu.png", -35, 22, _at(by[CORNER], (0.0, 0.5, -0.7)), 1.6)
    if LEAF_P in by:
        out["leaf_cu"] = rc([by[LEAF_P]], f"{d}/leaf_cu.png", -15, 10, _at(by[LEAF_P], (0.0, 0.0, -0.75)), 0.7)
    if CUSH_L in by:
        out["cushion_cu"] = rc([by[CUSH_L]], f"{d}/cushion_cu.png", -20, 20, _at(by[CUSH_L], (0.0, 0.0, 0.55)), 1.45)
    return out


def preview(names=("f34_sheet", "r34_sheet", "front_sheet", "rear_sheet", "side_sheet", "top_sheet"), vfx=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig


def hero_only():
    """Rebuild just the hero (tuning loop)."""
    h, lg = build_hero()
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n in PART_NAMES if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"hero": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                        "boundary_edges", "normals")}, "log": lg, "leaves": leaf_report(),
            "cushions": CUSHION_INFO, "offset": [round(x, 3) for x in h[OFF]]}
