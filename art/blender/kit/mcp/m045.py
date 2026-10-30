"""045 Pine Sapling (references/045.png): a small, chunky three-tier pine (10 tall). Each foliage tier is a ring of
thick constant-thickness paddle slabs (0.20 thick, a midrib fold, a blunt chisel tip, length : width about 1.5) in two
visible rows round a closed core (an upper ring over the seams, tips at mid-slope, on a hem ring); the tiers stack by peg and square recess (the trunk's flat top into the lower tier, each
tier's octagonal peg into the tier above, seats 0.015). The trunk is a smooth tapered 8-sided stump with two knots and
six short blunt root flares (unioned into it), on a thin pale sand patch dressed with four pale grey faceted rocks,
four upright fans of broad round-tipped oval leaves and three lime sprigs.

    import importlib, kit_models, m045; importlib.reload(kit_models); importlib.reload(m045); m045.build()

Build frame: studs, front -Y, +X right, ground z 0 = the sand patch's flat underside, tree axis at (0, 0). Every object
ends with its origin at its bbox bottom centre; o["m045_offset"] is that origin in the build frame.
- PineSaplingTopTier / MiddleTier / LowerTier: tier(kind): one closed core shell (frustum or star cone, flat underside
  ring, square recess, cap and peg) and its plate shells (12 / 14 / 14).
- PineSaplingTrunk: the 8-sided tapered body (knots, flat top, flat bottom) with six root flares exact-unioned in one at a
  time at the world origin: one closed shell.
- PineSaplingGroundFoliage (rosette P1 and its hub), PineSaplingRockMedium (RM), PineSaplingRockSmall (RS2).
- PineSapling (hero): all of it in one object of closed shells (only the roots are unioned, into the trunk).
Colour (stage 4) is painted by position and role inside the builders (never by facing). Stages 5-6: none (the sheet
shows no glow, light or effect). See M045_spec.md. Patterns copied (not imported) from m042 (Young Fir).
"""
import math
import random
import time

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri

import kit_mcp as K
import kit_models as M
import m012
import m033

NUM, TITLE, SHEET = 45, "Pine Sapling", "M045"
OFF = "m045_offset"
PFX = "_m045_"
HERO = "PineSapling"
TOP_P, MID_P, LOW_P = "PineSaplingTopTier", "PineSaplingMiddleTier", "PineSaplingLowerTier"
TRUNK_P, GF_P, RM_P, RS_P = ("PineSaplingTrunk", "PineSaplingGroundFoliage", "PineSaplingRockMedium",
                             "PineSaplingRockSmall")

NEEDLE, NEEDLE_LIGHT, NEEDLE_DEEP = "m045_needle", "m045_needle_light", "m045_needle_deep"
BARK, BARK_LIGHT, BARK_DEEP = "m045_bark", "m045_bark_light", "m045_bark_deep"
ROCK, ROCK_LIGHT, ROCK_DEEP = "m045_rock", "m045_rock_light", "m045_rock_deep"
SAND, SAND_DEEP = "m045_sand", "m045_sand_deep"
PLANT, PLANT_DEEP, PLANT_DARK = "m045_plant", "m045_plant_deep", "m045_plant_dark"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
GAP = 0.015
THICK = 0.20

# key -> (hex, roughness, low specular). Stage 4 writes the calibrated values here (M045_spec.md "Stage 4").
PALETTE = {
    NEEDLE: ("#4B8034", 0.85, True),
    NEEDLE_LIGHT: ("#B4C82C", 0.85, True),
    NEEDLE_DEEP: ("#1E5A3A", 0.9, True),
    BARK: ("#BA6C26", 0.9, False),
    BARK_LIGHT: ("#C47A2C", 0.9, False),
    BARK_DEEP: ("#643A1C", 0.95, False),
    ROCK: ("#A49D99", 0.85, False),
    ROCK_LIGHT: ("#B0A9A4", 0.85, False),
    ROCK_DEEP: ("#8C8A89", 0.9, False),
    SAND: ("#BCAA88", 0.95, False),
    SAND_DEEP: ("#B6A381", 0.95, False),
    PLANT: ("#879C1A", 0.85, True),
    PLANT_DEEP: ("#62AA40", 0.85, True),
    PLANT_DARK: ("#2E7C48", 0.85, True),
}
# calibration targets (spec 5.4: rendered medians of unshadowed regions of the sheet, sRGB)
TARGETS = {NEEDLE: ((0x9E, 0xC5, 0x34), "green"), NEEDLE_LIGHT: ((0xAA, 0xCB, 0x35), "green"),
           NEEDLE_DEEP: ((0x28, 0x72, 0x3F), "green"), BARK: ((0xB0, 0x63, 0x25), "brown"),
           BARK_LIGHT: ((0xEC, 0x8C, 0x36), "brown"), BARK_DEEP: ((0x70, 0x45, 0x28), "brown"),
           ROCK: ((0xCE, 0xC0, 0xB4), "stone"), ROCK_LIGHT: ((0xDC, 0xCB, 0xBD), "stone"),
           ROCK_DEEP: ((0xB1, 0xA9, 0x9F), "stone"), SAND: ((0xEF, 0xD1, 0x9D), "brown"),
           SAND_DEEP: ((0xE5, 0xC7, 0x93), "brown"), PLANT: ((0xAF, 0xC5, 0x18), "green"),
           PLANT_DEEP: ((0x4D, 0x7C, 0x25), "green"), PLANT_DARK: ((0x22, 0x55, 0x29), "green")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    # mixed keys made by an earlier build: re-mix them from the (possibly new) parents
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m045_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k.endswith("_" + tail) and k.startswith(k1)), None) or \
                next((k for k in PALETTE if k.endswith(tail)), None)
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


# ---- small helpers -------------------------------------------------------------------------------------------------
_faces = m033._faces
_mottle = m033._mottle


def _zip(bm, ra, rb):
    """Triangles between two closed rings about +Z, walking both by angle (m033._zip, but both rings start from the
    first vertex at or after the same reference angle: m033's version skips a vertex of rb that lies just before ra's
    first one, which left a triangle over the recess corner)."""
    def ang(v):
        return math.atan2(v.co.y, v.co.x) % (2 * math.pi)
    ref = min(ang(v) for v in ra)
    a0 = min(range(len(ra)), key=lambda i: (ang(ra[i]) - ref) % (2 * math.pi))
    b0 = min(range(len(rb)), key=lambda i: (ang(rb[i]) - ref) % (2 * math.pi))
    A = ra[a0:] + ra[:a0]
    B = rb[b0:] + rb[:b0]
    na, nb = len(A), len(B)

    def u(v, wrap):
        return (ang(v) - ref) % (2 * math.pi) + (2 * math.pi if wrap else 0.0)
    i = j = 0
    out = []
    while i < na or j < nb:
        if j >= nb or (i < na and u(A[(i + 1) % na], i + 1 >= na) <= u(B[(j + 1) % nb], j + 1 >= nb)):
            out.append(bm.faces.new((A[i % na], A[(i + 1) % na], B[j % nb])))
            i += 1
        else:
            out.append(bm.faces.new((A[i % na], B[(j + 1) % nb], B[j % nb])))
            j += 1
    return out


def _q(t, steps=4):
    t = max(0.0, min(1.0, t))
    return round(t * steps) / steps


def _mix(k1, k2, t):
    return K.mix_key(k1, k2, _q(t))


def _needle(v):
    """A plate tone on one axis: v < 0 toward NEEDLE_DEEP, v > 0 toward NEEDLE_LIGHT (25 % steps)."""
    return _mix(NEEDLE, NEEDLE_DEEP, -v) if v < 0 else _mix(NEEDLE, NEEDLE_LIGHT, v)


def _paint(a, faces, key):
    mi = a._mi(key)
    for f in faces:
        if f.is_valid:
            f.material_index = mi


def _tint(a, faces, k):
    for f in faces:
        for l in f.loops:
            t = l[a.tint_layer][0] * k
            l[a.tint_layer] = (t, t, t, 1.0)


def _u(az):
    r = math.radians(az)
    return Vector((math.cos(r), math.sin(r), 0.0))


def _ring(bm, n, r, z, az0=0.0, jit=0.0, rng=None):
    return [bm.verts.new(_u(az0 + 360.0 * k / n) * (r + (rng.uniform(-jit, jit) if rng else 0.0)) + Vector((0, 0, z)))
            for k in range(n)]


# ---- plates (spec 2.3) -----------------------------------------------------------------------------------------------
PX = (0.0, 0.45, 0.78, 1.0)          # stations along the plate (fraction of its length)
PH = (0.08, 0.5, 0.425, 0.09)        # half-width at each station (fraction of its width): paddle + chisel tip
RIDGE = 0.08                         # midrib fold height (fraction of the width; spec 0.07, round 1 had 0.11)


def _rot_xz(p, piv, phi):
    x, z = p.x - piv[0], p.z - piv[1]
    c, s = math.cos(phi), math.sin(phi)
    return Vector((piv[0] + x * c - z * s, p.y, piv[1] + x * s + z * c))


def _plate_local(L, W, droop):
    """Plate stations in its own frame (x along, y across, z up): outline top corners tl / tr at z 0, bottom corners
    bl / br at -THICK straight below them (straight side walls, constant thickness), a midrib point m raised RIDGE * W
    on stations 1-3 (the root end is buried, so it has no ridge). The outer part bends down: station 2 by d1 about
    station 1, the tip by a further d2 about station 2, where (d1, d2) = droop (a pair) or (droop / 2, droop / 2).
    Returns (stations, tip anchor)."""
    st = []
    for i, (fx, fh) in enumerate(zip(PX, PH)):
        x, h = fx * L, fh * W
        p = {"tl": Vector((x, h, 0.0)), "tr": Vector((x, -h, 0.0)),
             "bl": Vector((x, h, -THICK)), "br": Vector((x, -h, -THICK))}
        if i:
            p["m"] = Vector((x, 0.0, RIDGE * W))
        st.append(p)
    d1, d2 = (math.radians(droop[0]), math.radians(droop[1])) if isinstance(droop, (tuple, list)) else \
        (math.radians(droop) / 2,) * 2
    pa = (PX[1] * L, -THICK / 2)
    pb = _rot_xz(Vector((PX[2] * L, 0.0, -THICK / 2)), pa, -d1)
    for i in (2, 3):
        for k in st[i]:
            st[i][k] = _rot_xz(st[i][k], pa, -d1)
    for k in st[3]:
        st[3][k] = _rot_xz(st[3][k], (pb.x, pb.z), -d2)
    tip = _rot_xz(_rot_xz(Vector((L, 0.0, 0.0)), pa, -d1), (pb.x, pb.z), -d2)
    return st, tip


def plate(a, az, r0, z0, r1, z1, w, droop=15.0, roll=0.0, tones=(0.0, 0.0, 0.0), length=None):
    """One closed 34-tri paddle slab: its root anchor at (r0, z0) on azimuth az (buried in its core), the tip anchor at
    (r1, z1); width w (widest at 0.45 of the length, 0.85 w at 0.78, a chisel tip 0.18 w wide), 0.20 thick, a midrib
    fold, the outer part drooping `droop` degrees (or a pair: the bend at 0.45 and at 0.78 of the length), rolled
    `roll` degrees about its own axis (neighbours shingle). With `length`, (r1, z1) is an aim point instead: the plate's
    unbent inner part runs from the root toward it, `length` long, and the bends hang below that line (fix round 1:
    the two rows of a tier are laid as parallel layers).
    tones = plate tone per band (root, middle, tip) on the _needle axis: colour by position along the plate.
    Returns (verts, lift groups [station 1, 2, 3])."""
    bm = a.bm
    dr, dz = r1 - r0, z1 - z0
    C = math.hypot(dr, dz)
    if length:
        L = length
        st, tip = _plate_local(L, w, droop)
        al = math.atan2(dz, dr)
    else:
        L = C
        for _ in range(3):
            st, tip = _plate_local(L, w, droop)
            L *= C / math.hypot(tip.x, tip.z)
        st, tip = _plate_local(L, w, droop)
        al = math.atan2(dz, dr) - math.atan2(tip.z, tip.x)
    rr = math.radians(roll)
    u = _u(az)
    s = Vector((-u.y, u.x, 0.0))
    up = Vector((0, 0, 1))
    P0 = u * r0 + up * z0

    def world(p):
        y = p.y * math.cos(rr) - p.z * math.sin(rr)
        z = p.y * math.sin(rr) + p.z * math.cos(rr)
        x2 = p.x * math.cos(al) - z * math.sin(al)
        z2 = p.x * math.sin(al) + z * math.cos(al)
        return P0 + u * x2 + s * y + up * z2
    V = [{k: bm.verts.new(world(p)) for k, p in sti.items()} for sti in st]
    bands = [[], [], []]
    nf = bm.faces.new
    bands[0] += [nf((V[0]["tl"], V[1]["tl"], V[1]["m"])), nf((V[0]["tl"], V[1]["m"], V[0]["tr"])),
                 nf((V[0]["tr"], V[1]["m"], V[1]["tr"]))]
    for i in (1, 2):
        A, B = V[i], V[i + 1]
        bands[i] += [nf((A["m"], A["tl"], B["tl"], B["m"])), nf((A["m"], B["m"], B["tr"], A["tr"]))]
    for i in range(3):
        A, B = V[i], V[i + 1]
        bands[i] += [nf((A["bl"], A["br"], B["br"], B["bl"])), nf((A["tl"], A["bl"], B["bl"], B["tl"])),
                     nf((A["tr"], B["tr"], B["br"], A["br"]))]
    bands[0].append(nf((V[0]["tl"], V[0]["tr"], V[0]["br"], V[0]["bl"])))
    bands[2].append(nf((V[3]["tl"], V[3]["m"], V[3]["tr"], V[3]["br"], V[3]["bl"])))
    vs = [v for d in V for v in d.values()]
    a._finish(vs, _needle(tones[1]), tint=1.0)
    for i in range(3):
        _paint(a, bands[i], _needle(tones[i]))
    bmesh.ops.triangulate(a.bm, faces=[f for b in bands for f in b], quad_method="BEAUTY", ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(a.bm, faces=_faces(vs))
    return vs, [list(V[i].values()) for i in (1, 2, 3)]


# ---- plate seating (copied from m042: ray-parity inside test, triangle crossing points, drape) -----------------------
def _inside(tree, p):
    n, o, d = 0, p.copy(), Vector((0.31, 0.17, 0.93)).normalized()
    for _ in range(24):
        h = tree.ray_cast(o, d)
        if h[0] is None:
            break
        n += 1
        o = h[0] + d * 1e-4
    return n % 2 == 1


def _cut_pts(ta, tb):
    out = []
    for t1, t2 in ((ta, tb), (tb, ta)):
        for i in range(3):
            p, q = t1[i], t1[(i + 1) % 3]
            d = q - p
            L = d.length
            if L < 1e-9:
                continue
            h = intersect_ray_tri(t2[0], t2[1], t2[2], d / L, p, True)
            if h is not None and (h - p).length <= L:
                out.append(h)
    return out


def _hits(vs, coords, polys, core=None):
    """Whether a plate visibly cuts into any triangle placed before it (a crossing point outside the core)."""
    fs = _faces(vs)
    idx = {v: i for i, v in enumerate(vs)}
    mine_p = [[idx[v] for v in f.verts] for f in fs]
    mine_c = [v.co.copy() for v in vs]
    mine = BVHTree.FromPolygons(mine_c, mine_p)
    for i, j in mine.overlap(BVHTree.FromPolygons(coords, polys)):
        ta = [mine_c[k] for k in mine_p[i]]
        tb = [coords[k] for k in polys[j]]
        for p in _cut_pts(ta, tb):
            if core is None or not _inside(core, p):
                return True
    return False


CUT = 0.05        # spec 6: neighbouring plates may touch but cut no more than 0.05 into each other


def _rec(coords, polys):
    """A closed shell as a record for cut-depth tests: its BVH and sample points (corners, edge midpoints, face
    centres)."""
    tree = BVHTree.FromPolygons(coords, polys)
    smp = list(coords)
    seen = set()
    for p in polys:
        smp.append(sum((coords[i] for i in p), Vector()) / len(p))
        for i in range(len(p)):
            e = (min(p[i], p[(i + 1) % len(p)]), max(p[i], p[(i + 1) % len(p)]))
            if e not in seen:
                seen.add(e)
                smp.append((coords[e[0]] + coords[e[1]]) / 2)
    return {"tree": tree, "smp": smp}


def _rec_of(vs):
    fs = _faces(vs)
    idx = {v: i for i, v in enumerate(vs)}
    return _rec([v.co.copy() for v in vs], [[idx[v] for v in f.verts] for f in fs])


def _depth(A, B, core=None):
    """How far two closed shells cut into each other: the deepest sample of either inside the other (distance to the
    other's surface), ignoring samples hidden inside the core. 0 when they don't overlap."""
    if not A["tree"].overlap(B["tree"]):
        return 0.0
    d = 0.0
    for P, Q in ((A, B), (B, A)):
        for p in P["smp"]:
            if _inside(Q["tree"], p) and (core is None or not _inside(core, p)):
                d = max(d, Q["tree"].find_nearest(p)[3])
    return d


def _drape(vs, groups, tree, clear, extra=0.0):
    """Lay a row B plate over row A: each station group (1, 2, tip) is lifted just enough that no sample of the faces
    round it lies below row A's top + clear (ray cast down). The root stays buried in the core."""
    fneed = {}
    for f in _faces(vs):
        pts = [v.co for v in f.verts] + [f.calc_center_median()]
        pts += [(e.verts[0].co + e.verts[1].co) / 2 for e in f.edges]
        need = 0.0
        for p in pts:
            hit = tree.ray_cast(p + Vector((0, 0, 4.0)), Vector((0, 0, -1)), 8.0)
            if hit[0] is not None and hit[0].z > p.z - 1.0:
                need = max(need, hit[0].z + clear - p.z)
        fneed[f] = need
    lifted = 0
    prev = 0.0
    for gi, g in enumerate(groups):
        need = max([fneed[f] for v in g for f in v.link_faces if f in fneed] + [0.0])
        need = max(need, 0.5 * prev, extra * gi)
        if need > 0:
            for v in g:
                v.co.z += need
            lifted += 1
        prev = need
    return lifted


# ---- tiers (spec 2.2) ------------------------------------------------------------------------------------------------
# apothems (half-width across flats) of the pieces that enter each recess: the trunk's top, the lower peg, the middle peg
TRUNK_TOP_APO = 0.55
CLEAR = 0.045             # recess wall clearance round each peg (spec 0.03-0.06)
# The cores are taller than the spec's (lower cap 6.10, middle mouth 6.115 / cap 7.90, crown mouth 7.915) so the plate
# roots stay buried; the stack seats are 0.015.
LIFT_MAX = 0.35           # how far a lift / sink plate may be moved whole
TURN_MAX = 0.40           # how far a tip_first sink plate's tip may be turned down before it is moved whole
# Fix round 1 (verifier round 1, blockers 1-2; round 1 tucked row B under row A, so each tier showed one ring of long
# plates and the middle and lower tiers merged into one skirt). Each of the lower and middle tiers now shows TWO rings,
# laid as parallel layers ("aim" rows: the root, an aim point on the layer's line and a length L; the tip bend hangs
# below the line):
# - Row B (the upper ring, 7 plates over the A seams) is built first, on top. Its roots are buried in the core, which
#   now reaches out to the waist (the pleated widest ring: lower r 1.65 at z 4.6, middle r 1.1 at z 7.0), so the plates
#   leave the core just under the hem above, at their narrow roots: the waist stays narrow. Its tips stop at about 0.55
#   of the tier's slope (lower z 3.9, middle z 6.26).
# - Row A (the hem ring, 7 plates, one aimed at the front) is built second as a "sink" row about 0.32 (normal) under
#   row B's line: rooted in the core's underside, its tips form the hem; a plate that still cuts B is turned down first.
# - Both rows run at about 36-38 deg; with the step at row B's tips the visible outline from waist to hem is about 43
#   deg. Each plate is about half the slope long: L : W 1.4-1.6, the rolls only 0-6 deg (the rings barely overlap).
# The crown keeps its round-1 construction (4 long hem + 4 short + 4 upper plates on the star cone), one tone darker.
TIERS = {
    "lower": dict(cap=(0.85, 6.10), wide=(1.65, 4.60), mouth=(1.00, 3.80), peg=(0.45, 6.50), ceil=4.415,
                  half=TRUNK_TOP_APO + CLEAR, seed=45300,
                  rows=[dict(n=7, az0=270.0 + 360 / 14, r0=1.10, z0=5.26, r1=2.61, z1=3.90, L=2.03, w=1.45,
                             droop=(0.0, 5.0), front=None, fix="roll", roll=3.0, tones=(-0.75, -0.25, 0.25)),
                        dict(n=7, az0=270.0, r0=1.30, z0=4.60, r1=3.00, z1=3.20, L=3.1, w=2.0, droop=(-18.0, 14.0),
                             front=3.00, fix="sink", roll=3.0, tip_first=True, tones=(-0.5, 0.0, 0.5))]),
    "middle": dict(cap=(0.70, 7.90), wide=(0.98, 7.00), mouth=(0.95, 6.115), peg=(0.375, 8.25), ceil=6.515,
                   half=0.45 + CLEAR, seed=45200,
                   rows=[dict(n=7, az0=270.0 + 360 / 14, r0=0.75, z0=7.55, r1=2.00, z1=6.30, L=1.77, w=1.25,
                              droop=(0.0, 5.0), front=None, fix="roll", roll=3.0, tones=(-0.5, 0.0, 0.5)),
                         dict(n=7, az0=270.0, r0=0.95, z0=6.84, r1=3.25, z1=4.62, L=2.4, w=1.65, droop=(-16.0, 14.0),
                              front=4.70, fix="sink", roll=3.0, tip_first=True, tones=(-0.25, 0.0, 0.5))]),
    "crown": dict(apex=10.0, rim_z=8.6, ridges=(1.0, 0.78, 0.62), mouth=(0.68, 7.915), ceil=8.265,
                  half=0.375 + CLEAR, seed=45100,
                  rows=[dict(n=4, az0=270.0, r0=0.50, z0=8.75, r1=1.75, z1=7.25, w=1.38, droop=12.0, front=7.15,
                             fix="roll", tones=(-0.25, 0.0, 0.5)),
                        dict(n=4, az0=315.0, r0=0.45, z0=8.55, r1=1.48, z1=7.38, w=1.1, droop=12.0, front=None,
                             fix="sink", tones=(-0.25, 0.0, 0.25)),
                        dict(n=4, az0=315.0, r0=0.30, z0=9.05, r1=1.22, z1=8.25, w=0.95, droop=12.0, front=None,
                             fix="lift", tones=(-0.25, 0.0, 0.25))]),
}
TIER_INFO = {}
COS8 = math.cos(math.radians(22.5))


def _recess(bm, half, z_mouth, z_ceil):
    """The square recess (corners at 0 / 90 / 180 / 270 deg, a diamond seen from the front): mouth square, ceiling
    square. Returns (mouth ring, walls + ceiling faces, verts)."""
    rc = half * math.sqrt(2)
    mo = [bm.verts.new(_u(90.0 * k) * rc + Vector((0, 0, z_mouth))) for k in range(4)]
    ce = [bm.verts.new(_u(90.0 * k) * rc + Vector((0, 0, z_ceil))) for k in range(4)]
    fs = [bm.faces.new((mo[k], mo[(k + 1) % 4], ce[(k + 1) % 4], ce[k])) for k in range(4)]
    fs.append(bm.faces.new((ce[3], ce[2], ce[1], ce[0])))
    return mo, fs, mo + ce


def _core(a, kind):
    """The tier's closed core shell (spec 2.3): lower / middle: an octagonal peg on a flat cap, a pleated frustum
    (corners at the row A azimuths pushed out 0.1, between them pulled in 0.1), an underside down to a flat ring and the
    square recess through it. Crown: the 4 + 4-ridge star cone, its underside, the flat ring and the recess.
    Returns (verts, faces by role)."""
    bm = a.bm
    T = TIERS[kind]
    mr, mz = T["mouth"]
    sq, rec_f, rec_v = _recess(bm, T["half"], mz, T["ceil"])
    if kind == "crown":
        apex = bm.verts.new(Vector((0, 0, T["apex"])))
        rim = []
        for k in range(16):
            r = T["ridges"][0] if k % 4 == 0 else T["ridges"][1] if k % 4 == 2 else T["ridges"][2]
            rim.append(bm.verts.new(_u(270.0 + 22.5 * k) * r + Vector((0, 0, T["rim_z"]))))
        rim = sorted(rim, key=lambda v: math.atan2(v.co.y, v.co.x))
        top_f = [bm.faces.new((apex, rim[k], rim[(k + 1) % 16])) for k in range(16)]
        mouth = _ring(bm, 8, mr, mz, 22.5)
        under_f = _zip(bm, rim, mouth)
        ring_f = _zip(bm, mouth, sq)
        peg_f = []
        vs = [apex] + rim + mouth + rec_v
    else:
        nA = T["rows"][0]["n"]
        a0 = T["rows"][0]["az0"]
        step = 360.0 / nA
        pr, ptop = T["peg"]
        cr, cz = T["cap"]
        wr, wz = T["wide"]
        pc = pr / COS8
        peg_t = _ring(bm, 8, pc, ptop, 22.5)
        peg_b = _ring(bm, 8, pc, cz, 22.5)
        cap = _ring(bm, nA, cr, cz, a0)
        wide = [bm.verts.new(_u(a0 + k * step / 2) * (wr + (0.1 if k % 2 == 0 else -0.1)) + Vector((0, 0, wz)))
                for k in range(2 * nA)]
        mouth = _ring(bm, nA, mr, mz, a0 + step / 2)
        srt = lambda r: sorted(r, key=lambda v: math.atan2(v.co.y, v.co.x))
        peg_t, peg_b, cap, wide, mouth = map(srt, (peg_t, peg_b, cap, wide, mouth))
        peg_f = [bm.faces.new(list(peg_t))]
        peg_f += [bm.faces.new((peg_b[k], peg_b[(k + 1) % 8], peg_t[(k + 1) % 8], peg_t[k])) for k in range(8)]
        top_f = _zip(bm, peg_b, cap) + _zip(bm, cap, wide)
        under_f = _zip(bm, wide, mouth)
        ring_f = _zip(bm, mouth, sq)
        vs = peg_t + peg_b + cap + wide + mouth + rec_v
    fs = top_f + under_f + ring_f + rec_f + peg_f
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    if kind == "crown":
        a._finish(vs, _mix(NEEDLE, NEEDLE_LIGHT, 0.25), tint=1.0)     # fix round 1: two steps less lime
        _paint(a, under_f, _mix(NEEDLE, NEEDLE_DEEP, 0.5))
    else:
        a._finish(vs, _mix(NEEDLE, NEEDLE_DEEP, 0.75), tint=1.0)
        _paint(a, peg_f, _mix(NEEDLE, NEEDLE_DEEP, 0.5))
    _paint(a, ring_f, _mix(NEEDLE, NEEDLE_DEEP, 0.25))      # the lighter flat joining surface (close-up 1)
    _paint(a, rec_f, BARK_DEEP)                             # the pocket (close-up 1: dark brown), hard: a socket
    _mottle(a, top_f + under_f, 0.03, 0.5, 45010 + len(kind))
    bmesh.ops.triangulate(bm, faces=[f for f in fs if len(f.verts) > 3], quad_method="BEAUTY", ngon_method="BEAUTY")
    return vs


ROLL = 9.0        # every plate rolled the same way about its axis: neighbours shingle instead of cutting each other


def tier(a, kind):
    """A whole tier: its core, then row A plates, then row B plates. A row A plate that would cut into a neighbour is
    rolled further (then narrowed); a row B plate is lifted (stations 1, 2, tip) until it rests clear on row A."""
    T = TIERS[kind]
    below = _below(kind)
    rng = random.Random(T["seed"])
    core_vs = _core(a, kind)
    out = list(core_vs)
    ci = {v: i for i, v in enumerate(core_vs)}
    core = BVHTree.FromPolygons([v.co.copy() for v in core_vs], [[ci[v] for v in f.verts] for f in _faces(core_vs)])
    info = {"lifted": 0, "rolled": 0, "narrowed": 0, "plates": 0, "unresolved": 0, "depth": []}
    rows_done = []
    for ri, row in enumerate(T["rows"]):
        # plates of the rows below this one (a lift row rests on them) and of this row so far (neighbours shingle)
        recA = [r for rr in rows_done for r in rr]
        recB = []
        rows_done.append(recB)
        step = 360.0 / row["n"]
        move = {"lift": 1.0, "sink": -1.0}.get(row["fix"], 0.0)
        lift = bool(move)
        for k in range(row["n"]):
            az0 = row["az0"] + k * step
            az = az0 + rng.uniform(-4, 4)
            f_len = rng.uniform(0.95, 1.05)
            r1 = row["r1"] * (1.0 if row.get("L") else f_len)    # aim rows: jitter the length, not the aim
            length = row["L"] * f_len if row.get("L") else None
            z1 = row["z1"] + rng.uniform(-0.06, 0.06)
            if row["front"] is not None and abs((az0 - 270.0 + 180) % 360 - 180) < 1:
                az = 270.0 + rng.uniform(-1.5, 1.5)
                z1 = row["front"] + rng.uniform(-0.04, 0.04)
            w = row["w"] * rng.uniform(0.94, 1.06)
            # row A plates all roll one way (each one's counter-clockwise edge up, over its neighbour's low edge); row B
            # lies over the seams of row A, where the clockwise A plate's edge is up and the next one's down, so it rolls
            # the other way and follows that step
            sgn = -1.0 if lift else 1.0
            roll0 = row.get("roll", ROLL)
            roll = roll0 + rng.uniform(-3, 3)
            z0 = row["z0"]
            tone = 1.0 + rng.uniform(-0.04, 0.04)
            dz1 = 0.0
            turn = 0.0
            for attempt in range(36):
                vs, groups = plate(a, az, row["r0"], z0, r1, z1 + dz1, w, row["droop"], sgn * roll, row["tones"],
                                   length)
                rec = _rec_of(vs)
                dA = max([_depth(rec, q, core) for q in recA] + [0.0])
                dB = max([_depth(rec, q, core) for q in recB] + [0.0])
                dL = max([_depth(rec, q) for q in below] + [0.0])
                if (dA <= CUT and dB <= CUT and dL <= CUT) or attempt == 35:
                    if attempt == 35:
                        info["unresolved"] += 1
                    break
                bmesh.ops.delete(a.bm, geom=vs, context="VERTS")
                if dL > CUT and dz1 < 0.36:
                    dz1 += 0.06               # rests on the tier below: tip it up about its buried root ...
                    info["lifted"] += 1
                elif dL > CUT and z0 < row["z0"] + 0.25:
                    z0 += 0.05                # ... then raise it whole
                    dz1 += 0.05
                    info["lifted"] += 1
                elif move and row.get("tip_first") and dA > CUT and turn < TURN_MAX - 1e-6:
                    turn += 0.05              # a hem row tucked under the upper ring: first turn its tip down about
                    dz1 += 0.05 * move        # its buried root (keeps the root in the core and the waist narrow) ...
                    info["lifted"] += 1
                elif move and dA > CUT and abs(z0 - row["z0"]) < LIFT_MAX - 1e-6:
                    z0 += 0.05 * move         # a lift row rests on the rows before it, a sink row tucks under them:
                    dz1 += 0.05 * move        # move the whole plate (its slope kept) ...
                    info["lifted"] += 1
                elif move and dA > CUT and abs(dz1) < LIFT_MAX + 0.3:
                    dz1 += 0.06 * move        # ... then turn its tip about its buried root
                    info["lifted"] += 1
                elif roll < roll0 + (24 if row.get("L") else 12):     # aim rows roll further before narrowing
                    roll += 3.0
                    info["rolled"] += 1
                else:
                    w *= 0.96
                    info["narrowed"] += 1
            info["depth"].append(round(max(dA, dB), 3))
            # plate length : width (the whole slab, root to tip; the visible part is shorter)
            p_len = length or math.hypot(r1 - row["r0"], z1 + dz1 - z0)
            info.setdefault("lw", []).append((ri, round(p_len / w, 2)))
            info.setdefault("final", []).append((ri, round(sgn * roll), round(w / row["w"], 2), round(dz1, 2),
                                                 round(dA, 3), round(dB, 3)))
            if lift:
                info.setdefault("tip_lift", []).append(round(dz1, 2))
            fs = _faces(vs)
            _tint(a, fs, tone)
            _mottle(a, fs, 0.03, 0.6, T["seed"] + 17 * k + 101 * ri)
            recB.append(rec)
            out += vs
            info["plates"] += 1
    TIER_INFO[kind] = info
    TIER_RECS[kind] = [r for rr in rows_done for r in rr]
    return out


TIER_RECS = {}            # kind -> cut-test records of its plates (build frame), for the tier above to rest on
BELOW = {"lower": None, "middle": "lower", "crown": "middle"}


def _below(kind):
    """The plates of the tier under this one, in the build frame (a probe build when not built yet this run), so a part
    built alone and the same tier in the hero come out identical."""
    k = BELOW[kind]
    if k is None:
        return []
    if k not in TIER_RECS:
        probe = K.fk().Asset("_probe_" + k, "probe")
        info = TIER_INFO.get(k)
        tier(probe, k)
        probe.bm.free()
        if info is not None:
            TIER_INFO[k] = info
    return TIER_RECS[k]


def top_part(a):
    tier(a, "crown")


def middle_part(a):
    tier(a, "middle")


def lower_part(a):
    tier(a, "lower")


# ---- trunk and roots (spec 2.4) --------------------------------------------------------------------------------------
# (z, width across flats): the front cell's silhouette widths; a straight taper above z 1.5, the flare below
TRUNK_RINGS = ((0.04, 2.30), (1.0, 2.10), (1.5, 1.60), (2.0, 1.37), (2.5, 1.25), (3.1, 1.19), (3.8, 1.14),
               (4.4, 2 * TRUNK_TOP_APO))
TRUNK_TOP = 4.4
KNOTS = ((315.0, 4), (135.0, 3))         # facet normal azimuth, band (ring i to i + 1): front-right z 2.8, left-back 2.25
# roots: name, azimuth, reach (r from the axis), width and height at the trunk, segments, ridge start z on the trunk
ROOTS = (("RFR", 315.0, 2.5, 0.75, 0.80, 2, 1.55), ("RF", 255.0, 1.6, 0.70, 0.70, 1, 1.35),
         ("RL", 200.0, 1.9, 0.70, 0.75, 2, 1.45), ("RBL", 145.0, 1.8, 0.65, 0.70, 1, 1.30),
         ("RB", 85.0, 2.0, 0.70, 0.70, 2, 1.40), ("RR", 355.0, 1.8, 0.65, 0.70, 1, 1.25))
ROOT_ZB = 0.08            # root bottoms: sunk 0.04 into the sand's crest (0.12)


def trunk_body(a):
    """The smooth 8-sided tapered body (a face toward -Y, corners at 22.5 + 45 k), rings jittered a little, two knots
    (a facet inset and pulled in 0.05), a flat bottom and a flat top (the peg into the lower tier's recess)."""
    bm = a.bm
    rng = random.Random(45400)
    rings = []
    for i, (z, wd) in enumerate(TRUNK_RINGS):
        rc = wd / 2 / COS8
        jit = 0.0 if i >= len(TRUNK_RINGS) - 2 else 0.035
        rings.append([bm.verts.new(_u(22.5 + 45 * k) * (rc + rng.uniform(-jit, jit)) + Vector((0, 0, z)))
                      for k in range(8)])
    side_f = {}
    for i in range(len(rings) - 1):
        for k in range(8):
            j = (k + 1) % 8
            side_f[(i, k)] = bm.faces.new((rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]))
    bot = bm.faces.new(list(reversed(rings[0])))
    top = bm.faces.new(list(rings[-1]))
    vs = [v for r in rings for v in r]
    allf = list(side_f.values()) + [bot, top]
    bmesh.ops.recalc_face_normals(bm, faces=allf)
    a._finish(vs, BARK, tint=1.0)
    for (i, k), f in side_f.items():
        if f.calc_center_median().z < 1.0:
            f.material_index = a._mi(_mix(BARK, BARK_DEEP, 0.25))
    # the flat top (hidden in its recess) and bottom (in the sand) keep the body's colour at their height: a light cut
    # top and a dark bottom would put up / down facing into the colours (K.check's baked-shading rule)
    _paint(a, [bot], _mix(BARK, BARK_DEEP, 0.25))
    tones = [1.0 + rng.uniform(-0.04, 0.04) for _ in range(8)]
    for (i, k), f in side_f.items():
        _tint(a, [f], tones[k])
    _mottle(a, list(side_f.values()), 0.04, 0.35, 45410)
    # knots: inset the facet (k: the facet between corners 22.5 + 45 k and + 45, normal at 45 (k + 1)) and pull it in
    for naz, band in KNOTS:
        k = int(round(naz / 45.0)) - 1
        f = side_f[(band, k % 8)]
        res = bmesh.ops.inset_individual(bm, faces=[f], thickness=0.11, depth=-0.05, use_even_offset=True)
        _paint(a, [f], BARK_DEEP)
        _paint(a, res["faces"], _mix(BARK, BARK_DEEP, 0.5))
        vs += [v for v in f.verts if v not in vs]
    bmesh.ops.triangulate(bm, faces=[f for f in _faces(vs) if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    return vs


def _root_stations(spec):
    """(distance from the axis, top z, width) per section: inside the trunk, at the trunk's foot, (mid), the cut end."""
    name, az, reach, w, h, nseg, z_top0 = spec
    st = [(0.35, z_top0, 0.9 * w), (1.05, ROOT_ZB + h, w)]
    if nseg >= 2:
        st.append((1.05 + 0.55 * (reach - 1.05), ROOT_ZB + 0.55 * h + 0.12, 0.72 * w))
    st.append((reach, ROOT_ZB + 0.30, 0.35))
    return st


def root(a, spec, rng):
    """One root flare: a pentagon-section block (flat bottom on the sand, two sides, a top ridge set a little off centre)
    from inside the trunk out along its azimuth, tapering to a blunt flat cut end. Returns its verts."""
    bm = a.bm
    name, az, reach, w, h, nseg, z_top0 = spec
    st = _root_stations(spec)
    t = _u(az + rng.uniform(-3, 3))
    s = Vector((-t.y, t.x, 0.0))
    off = rng.uniform(-0.1, 0.1)
    secs = []
    for d, zt, ww in st:
        c = t * d
        zb = ROOT_ZB
        hh = zt - zb
        pts = [c - s * ww / 2 + Vector((0, 0, zb)), c + s * ww / 2 + Vector((0, 0, zb)),
               c + s * ww * 0.44 + Vector((0, 0, zb + 0.55 * hh)), c + s * off * ww + Vector((0, 0, zt)),
               c - s * ww * 0.44 + Vector((0, 0, zb + 0.5 * hh))]
        secs.append([bm.verts.new(p) for p in pts])
    fs = [bm.faces.new(list(reversed(secs[0]))), bm.faces.new(list(secs[-1]))]
    for i in range(len(secs) - 1):
        A, B = secs[i], secs[i + 1]
        for k in range(5):
            j = (k + 1) % 5
            fs.append(bm.faces.new((A[k], A[j], B[j], B[k])))
    bmesh.ops.triangulate(bm, faces=fs, quad_method="BEAUTY", ngon_method="BEAUTY")
    vs = [v for sc in secs for v in sc]
    fs = _faces(vs)
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    a._finish(vs, BARK, tint=1.0)
    for f in fs:
        if f.calc_center_median().z < 0.5:
            f.material_index = a._mi(_mix(BARK, BARK_DEEP, 0.25))
    _paint(a, [f for f in fs if all(v in secs[-1] for v in f.verts)], _mix(BARK, BARK_DEEP, 0.5))   # the cut end
    _mottle(a, fs, 0.04, 0.5, 45450 + int(az))
    return vs


def trunk_part(a):
    """Trunk body first (shell 0, the union's base), then the six roots (each unioned in on its own)."""
    trunk_body(a)
    rng = random.Random(45500)
    for spec in ROOTS:
        root(a, spec, rng)


# ---- ground: patch, rocks, rosettes, sprigs (spec 2.4) ---------------------------------------------------------------
PATCH_TOP, PATCH_EDGE = 0.12, 0.03
ROCKS = {   # name -> centre, (W, D, H), yaw (deg), top slope, seed
    "RM": ((2.2, 1.5), (1.9, 1.6, 1.15), 25.0, 0.14, 45601),
    "RS1": ((-1.3, -2.0), (1.5, 1.2, 0.95), -20.0, 0.12, 45602),
    "RS2": ((0.8, -2.2), (1.1, 0.95, 0.72), 35.0, 0.12, 45603),
    "RS3": ((-2.7, 0.9), (1.0, 0.9, 0.62), 10.0, 0.10, 45604),
}
# rosettes: centre, diameter, height, leaves (outer ring, inner ring), seed. Sprigs: 5 lime leaves.
ROSETTES = {
    "P1": ((-2.5, -0.5), 2.4, 1.6, (7, 4), 45701),
    "P2": ((2.5, -0.7), 2.4, 1.6, (7, 4), 45702),
    "P3": ((-1.4, 2.7), 1.8, 1.25, (5, 3), 45703),
    "P4": ((3.1, 0.6), 1.6, 1.15, (5, 3), 45704),
}
LEAF_LW, LEAF_FOLD, LEAF_TRIS = 2.0, 22.0, 14     # leaf length : width, midrib fold (deg), tris per leaf
SPRIGS = {"S1": ((0.0, -2.6), 0.8, 0.7, 45711), "S2": ((1.75, -2.5), 0.9, 0.8, 45712),
          "S3": ((-2.05, -2.3), 0.75, 0.6, 45713)}
# rock ring stacks (height fraction, radius fraction, points): a broad flat base, the widest ring low, a shoulder, a
# flat sloping crown of 5 corners: chunky rounded-angular blocks, never eggs
ROCK_RINGS = ((0.0, 0.9, 6), (0.22, 1.0, 7), (0.74, 0.95, 6), (1.0, 0.7, 5))
SINK_ROCK, SINK_HUB = 0.08, 0.03


def _items():
    """(centre, footprint radius) of everything on the patch, for the patch outline and the sand's deeper band."""
    out = [(Vector(c), max(s[0], s[1]) / 2) for c, s, *_ in ROCKS.values()]
    out += [(Vector(c), 0.55 * D / 2) for c, D, *_ in ROSETTES.values()]
    out += [(Vector(c), 0.5 * D / 2) for c, D, *_ in SPRIGS.values()]
    for spec in ROOTS:
        out.append(((_u(spec[1]) * spec[2]).to_2d(), 0.25))
    return out


def _patch_outline(n=12):
    """Lobed outline (r per azimuth): an ellipse 3.9 x 3.4 with lobes, let out wherever an item needs 0.25 of sand
    beyond its footprint."""
    rng = random.Random(45600)
    ph = [rng.uniform(0, 6.28) for _ in range(3)]
    items = _items()
    out = []
    for k in range(n):
        th = 2 * math.pi * k / n
        r = 1.0 / math.sqrt((math.cos(th) / 3.45) ** 2 + (math.sin(th) / 2.95) ** 2)
        r *= 1.0 + 0.05 * math.sin(3 * th + ph[0]) + 0.035 * math.sin(5 * th + ph[1])
        for c, rad in items:
            dist = c.length
            ang = math.atan2(c.y, c.x)
            dth = abs((th - ang + math.pi) % (2 * math.pi) - math.pi)
            half = math.asin(min(1.0, (rad + 0.2) / max(dist, 1e-3)))
            if dth < half + 2 * math.pi / n:
                r = max(r, dist * math.cos(dth) + math.sqrt(max(0.0, (rad + 0.2) ** 2 - (dist * math.sin(dth)) ** 2)))
        out.append(r)
    return out


def _patch_z(x, y):
    """Height of the sand patch's top at (x, y): the crest, or the bevel falling to PATCH_EDGE at the outline (the
    outline taken as straight chords between its points, as built)."""
    R = _patch_outline()
    n = len(R)
    th = math.atan2(y, x) % (2 * math.pi)
    k = int(th / (2 * math.pi / n)) % n
    j = (k + 1) % n
    a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
    p0 = Vector((math.cos(a0) * R[k], math.sin(a0) * R[k]))
    p1 = Vector((math.cos(a1) * R[j], math.sin(a1) * R[j]))
    d = Vector((math.cos(th), math.sin(th)))
    # the ray from the axis along d meets the chord p0-p1 at distance re
    e = p1 - p0
    den = d.x * e.y - d.y * e.x
    re = (p0.x * e.y - p0.y * e.x) / den if abs(den) > 1e-9 else R[k]
    r = math.hypot(x, y)
    if r <= re - 0.35:
        return PATCH_TOP
    return PATCH_EDGE + (PATCH_TOP - PATCH_EDGE) * max(0.0, (re - r) / 0.35)


def _near_field():
    segs = []
    for spec in ROOTS:
        segs.append((_u(spec[1]).to_2d() * 1.0, _u(spec[1]).to_2d() * spec[2], 0.5 * spec[3]))
    circles = [(Vector((0, 0)), 1.15)] + [(Vector(c), max(s[0], s[1]) / 2) for c, s, *_ in ROCKS.values()]
    circles += [(Vector(c), 0.25) for c, *_ in ROSETTES.values()] + [(Vector(c), 0.2) for c, *_ in SPRIGS.values()]

    def f(p):
        q = p.to_2d()
        d = min((q - c).length - r for c, r in circles)
        for a_, b_, r in segs:
            ab = b_ - a_
            t = max(0.0, min(1.0, (q - a_).dot(ab) / ab.length_squared))
            d = min(d, (q - (a_ + ab * t)).length - r)
        return d
    return f


def patch(a):
    """The thin lobed sand patch: a flat crest at 0.12, a bevel 0.35 wide down to 0.03 at the outline, a short side, a
    flat underside at z 0. Deeper sand within 0.35 of the trunk, roots, rocks and hubs and on the bevel."""
    bm = a.bm
    R = _patch_outline()
    n = len(R)

    def ring(f_r, z, dr=0.0):
        return [bm.verts.new(_u(360.0 * k / n) * (R[k] * f_r + dr) + Vector((0, 0, z))) for k in range(n)]
    c_top = bm.verts.new(Vector((0, 0, PATCH_TOP)))
    r1 = ring(0.55, PATCH_TOP)
    r2 = ring(1.0, PATCH_TOP, -0.35)
    r3 = ring(1.0, PATCH_EDGE)
    r4 = ring(1.0, 0.0)
    c_bot = bm.verts.new(Vector((0, 0, 0)))
    fs = [bm.faces.new((r1[k], r1[(k + 1) % n], c_top)) for k in range(n)]
    for A, B in ((r1, r2), (r2, r3), (r3, r4)):
        for k in range(n):
            j = (k + 1) % n
            fs.append(bm.faces.new((A[k], B[k], B[j], A[j])))
    fs += [bm.faces.new((r4[(k + 1) % n], r4[k], c_bot)) for k in range(n)]
    bmesh.ops.triangulate(bm, faces=fs, quad_method="BEAUTY")
    vs = [c_top, c_bot] + r1 + r2 + r3 + r4
    allf = _faces(vs)
    bmesh.ops.recalc_face_normals(bm, faces=allf)
    a._finish(vs, SAND, tint=1.0)
    near = _near_field()
    for f in allf:
        c = f.calc_center_median()
        if c.z < PATCH_TOP - 1e-3:       # the bevelled edge: a soft, deeper rim (position, as on the sheet)
            f.material_index = a._mi(_mix(SAND, SAND_DEEP, 0.5))
        elif near(c) < 0.35:
            f.material_index = a._mi(_mix(SAND, SAND_DEEP, 0.25))
    _mottle(a, allf, 0.03, 0.15, 45620)
    return vs


def rock(a, name, z0=None):
    """A chunky faceted rock: the hull of jittered ring stacks (a broad flat base sunk 0.08 into the sand, widest low, a
    shoulder, a flat crown sloping down to one side). rock base; rock_light on the top 30 %, rock_deep on the lowest
    25 %."""
    (cx, cy), (W, D, H), yaw, slope, seed = ROCKS[name]
    if z0 is None:
        z0 = _patch_z(cx, cy) - SINK_ROCK
    rng = random.Random(seed)
    pts = []
    for h, rf, n in ROCK_RINGS:
        off = rng.uniform(0, 2 * math.pi)
        for k in range(n):
            th = off + 2 * math.pi * k / n + rng.uniform(-0.25, 0.25) * (2 * math.pi / n)
            r = rf * (1 + rng.uniform(-0.06, 0.06))
            x, y = math.cos(th) * W / 2 * r, math.sin(th) * D / 2 * r
            z = h * H * (1 + (rng.uniform(-0.06, 0.06) if 0 < h < 1 else 0))
            if h >= 0.7:
                z -= slope * H * (x / (W / 2)) * h          # the crown slopes down toward +x (before the yaw)
            pts.append(Vector((x, y, max(0.0, z))))
    m = Matrix.Rotation(math.radians(yaw), 3, "Z")
    pts = [m @ p + Vector((cx, cy, z0)) for p in pts]
    vs = m033._hull(a, pts, ROCK)
    fs = _faces(vs)
    for f in fs:
        hgt = (f.calc_center_median().z - z0) / H
        if hgt > 0.75:
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.5))
        elif hgt > 0.6:
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.25))
        elif hgt < 0.25:
            f.material_index = a._mi(_mix(ROCK, ROCK_DEEP, 0.25))
    _mottle(a, fs, 0.04, 0.4, seed)
    return vs


def _leaf12(a, base, yaw, pitch, L, W, curl, fold, key):
    """One closed 14-tri broad oval leaf with a ROUND (blunt) tip (fix round 1: round 1's pointed tips read as 042's
    lanceolate / agave clumps): outline base, widest (W) at 0.4 L, 0.8 W at 0.78 L, a short blunt end 0.26 W wide at
    the tip; folded on its midrib (the halves rise `fold` radians: a V channel), a top midrib point and a keel 0.04
    under it, arching out and down by `curl` (fraction of L) toward the tip."""
    bm = a.bm
    cy, sy, cp, sp = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch)
    d = Vector((cy * cp, sy * cp, sp))
    s = Vector((-sy, cy, 0.0))
    n = d.cross(s).normalized()
    B = Vector(base)
    tf = math.tan(fold)

    def P(x, y, z):
        t = x / L
        return B + d * x + s * y + n * (z + abs(y) * tf - curl * L * t * t)
    outline = [(0.0, 0.0), (0.42 * L, W / 2), (0.8 * L, 0.42 * W), (L, 0.17 * W), (L, -0.17 * W),
               (0.8 * L, -0.42 * W), (0.42 * L, -W / 2)]
    ov = [bm.verts.new(P(x, y, 0.0)) for x, y in outline]
    m = bm.verts.new(P(0.45 * L, 0.0, 0.02))
    k = bm.verts.new(P(0.45 * L, 0.0, -0.04))
    fs = []
    no = len(outline)
    for i in range(no):
        j = (i + 1) % no
        fs.append(bm.faces.new((m, ov[i], ov[j])))
        fs.append(bm.faces.new((k, ov[j], ov[i])))
    vs = ov + [m, k]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    a._finish(vs, key, tint=1.0)
    return vs, fs


def _hub(a, cx, cy, hr, hh, seed):
    bm = a.bm
    z0 = _patch_z(cx, cy) - SINK_HUB
    yaw0 = random.Random(seed).uniform(0, 6.28)
    ring = [bm.verts.new(Vector((cx + math.cos(yaw0 + 2 * math.pi * k / 5) * hr,
                                 cy + math.sin(yaw0 + 2 * math.pi * k / 5) * hr, z0))) for k in range(5)]
    apex = bm.verts.new(Vector((cx, cy, z0 + hh)))
    fs = [bm.faces.new((ring[k], ring[(k + 1) % 5], apex)) for k in range(5)]
    fs.append(bm.faces.new(list(reversed(ring))))
    bmesh.ops.triangulate(bm, faces=[fs[-1]])
    vs = ring + [apex]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, _mix(PLANT_DARK, BARK_DEEP, 0.25), tint=1.0)
    return vs, z0


LEAF_INFO = {}


def _leaf_ok(vs, obstacles):
    """True when the leaf cuts into no obstacle (rocks, the trunk and its roots) deeper than touching: no crossing."""
    if obstacles is None:
        return True
    coords, polys = obstacles
    return not _hits(vs, coords, polys)


def rosette(a, name, obstacles=None):
    """A rosette of broad round-tipped oval leaves round a small closed 5-sided hub sunk 0.03 into the sand: an outer
    ring of longer leaves (pitch 60-72 deg, arching out at the tips) and an inner ring of upright ones (75-85 deg), so
    the fan stands taller than the rocks. Each leaf's base sits
    inside the hub. Roles: outer leaves mostly lime (PLANT) with a few green, inner leaves green and dark; the leaf's
    base third a step deeper. A leaf that would cut into a rock or root is turned a little or shortened."""
    (cx, cy), D, H, (n_out, n_in), seed = ROSETTES[name]
    rng = random.Random(seed)
    hvs, z0 = _hub(a, cx, cy, 0.22 if D > 2 else 0.18, 0.26, seed)
    out = list(hvs)
    info = LEAF_INFO.setdefault(name, {"turned": 0, "shortened": 0, "dropped": 0})
    yaw0 = rng.uniform(0, 6.28)
    # fix round 1: upright fans show the inner leaves, so fewer lime outer leaves and more dark inner ones keep the
    # sheet's lime / green / dark split (38 / 39 / 23)
    out_roles = [PLANT, PLANT_DEEP, PLANT_DEEP, PLANT, PLANT_DEEP, PLANT_DEEP, PLANT_DEEP][:n_out]
    in_roles = [PLANT_DARK, PLANT_DEEP, PLANT_DARK, PLANT_DEEP][:n_in]
    specs = []
    # fix round 1: upright fans (outer ring 60-72 deg, inner 75-85 deg) of broad round-tipped ovals, L : W 2.1, the
    # outer leaves arching out at the tips; the fan stands taller than the rocks
    for k in range(n_out):
        yaw = yaw0 + 2 * math.pi * k / n_out + rng.uniform(-0.2, 0.2)
        pitch = math.radians(rng.uniform(60, 72))
        curl = rng.uniform(0.26, 0.34)       # the tip arches out by curl * L (and drops by curl * L * cos pitch)
        L = (H - 0.2) / (math.sin(pitch) - curl * math.cos(pitch)) * rng.uniform(0.92, 1.0)
        specs.append((yaw, pitch, L, out_roles[k], curl))
    for k in range(n_in):
        yaw = yaw0 + math.pi / n_out + 2 * math.pi * k / n_in + rng.uniform(-0.25, 0.25)
        pitch = math.radians(rng.uniform(75, 85))
        L = (H - 0.3) / math.sin(pitch) * rng.uniform(0.95, 1.05)
        specs.append((yaw, pitch, L, in_roles[k], rng.uniform(0.10, 0.14)))
    for yaw, pitch, L, key, curl in specs:
        placed = None
        for dyaw, f_l in ((0, 1.0), (0.22, 1.0), (-0.22, 1.0), (0.45, 1.0), (-0.45, 1.0), (0, 0.8), (0.3, 0.75),
                          (-0.3, 0.75), (0, 0.6)):
            y2 = yaw + dyaw
            base = (cx + math.cos(y2) * 0.06, cy + math.sin(y2) * 0.06, z0 + 0.1)
            vs, fs = _leaf12(a, base, y2, pitch, L * f_l, L * f_l / LEAF_LW, curl, math.radians(LEAF_FOLD), key)
            if _leaf_ok(vs, obstacles):
                placed = (vs, fs, base, L * f_l)
                if dyaw:
                    info["turned"] += 1
                if f_l < 1:
                    info["shortened"] += 1
                break
            bmesh.ops.delete(a.bm, geom=vs, context="VERTS")
        if placed is None:
            info["dropped"] += 1
            continue
        vs, fs, base, Lp = placed
        # the leaf's base half a step deeper (position along the leaf)
        deeper = {PLANT: _mix(PLANT, PLANT_DEEP, 0.5), PLANT_DEEP: _mix(PLANT_DEEP, PLANT_DARK, 0.5),
                  PLANT_DARK: PLANT_DARK}[key]
        _paint(a, [f for f in fs if any((v.co - Vector(base)).length < 1e-6 for v in f.verts)], deeper)
        _tint(a, fs, 1.0 + rng.uniform(-0.04, 0.04))
        out += vs
    return out


def sprig(a, name, obstacles=None):
    """A small sprig: 5 lime leaves (one green) round a small hub."""
    (cx, cy), D, H, seed = SPRIGS[name]
    rng = random.Random(seed)
    hvs, z0 = _hub(a, cx, cy, 0.13, 0.18, seed)
    out = list(hvs)
    info = LEAF_INFO.setdefault(name, {"turned": 0, "shortened": 0, "dropped": 0})
    yaw0 = rng.uniform(0, 6.28)
    for k in range(5):
        yaw = yaw0 + 2 * math.pi * k / 5 + rng.uniform(-0.2, 0.2)
        pitch = math.radians(rng.uniform(50, 70))
        L = H / math.sin(pitch) * rng.uniform(0.95, 1.08)
        key = PLANT_DEEP if k in (1, 3) else PLANT
        for dyaw, f_l in ((0, 1.0), (0.3, 1.0), (-0.3, 1.0), (0, 0.75), (0.5, 0.7), (-0.5, 0.7)):
            base = (cx + math.cos(yaw + dyaw) * 0.04, cy + math.sin(yaw + dyaw) * 0.04, z0 + 0.07)
            vs, fs = _leaf12(a, base, yaw + dyaw, pitch, L * f_l, L * f_l / LEAF_LW, 0.08, math.radians(LEAF_FOLD),
                             key)
            if _leaf_ok(vs, obstacles):
                break
            bmesh.ops.delete(a.bm, geom=vs, context="VERTS")
            vs = None
        if vs is None:
            info["dropped"] += 1
            continue
        _tint(a, fs, 1.0 + rng.uniform(-0.04, 0.04))
        out += vs
    return out


def _obstacles(a):
    """(coords, polys) of the rocks already in the asset plus a probe build of the trunk and its roots (not unioned:
    the union changes nothing a leaf could touch)."""
    probe = K.fk().Asset("_probe", "probe")
    trunk_part(probe)
    coords, polys = [], []
    for bm in (probe.bm, a.bm):
        bm.verts.ensure_lookup_table()
        base = len(coords)
        idx = {v: base + i for i, v in enumerate(bm.verts)}
        coords += [v.co.copy() for v in bm.verts]
        polys += [[idx[v] for v in f.verts] for f in bm.faces]
    probe.bm.free()
    return coords, polys


def _ground_obstacles():
    """What the plants must not cut into: the rocks, the trunk and its roots (faces wholly at or below the sand's
    crest dropped: the hubs sit in the sand)."""
    probe = K.fk().Asset("_probe2", "probe")
    for name in ROCKS:
        rock(probe, name)
    coords, polys = _obstacles(probe)
    probe.bm.free()
    return coords, [p for p in polys if not all(coords[i].z < PATCH_TOP + 1e-4 for i in p)]


def ground(a):
    """Patch, rocks, then the plants (avoiding the rocks, trunk and roots)."""
    patch(a)
    for name in ROCKS:
        rock(a, name)
    obs = _ground_obstacles()
    for name in ROSETTES:
        rosette(a, name, obs)
    for name in SPRIGS:
        sprig(a, name, obs)


def ground_foliage_part(a):
    """Ground Foliage: rosette P1 with its hub (no sand), the same leaves as in the hero."""
    rosette(a, "P1", _ground_obstacles())


def rock_medium_part(a):
    rock(a, "RM", z0=0.0)


def rock_small_part(a):
    rock(a, "RS2", z0=0.0)


def hero_rest(a):
    """Everything but the trunk (which is unioned on its own and joined in): ground, then the three tiers."""
    ground(a)
    tier(a, "lower")
    tier(a, "middle")
    tier(a, "crown")


# ---- objects ---------------------------------------------------------------------------------------------------------
NOTES = {
    HERO: "Pine Sapling: three foliage tiers of thick paddle slab plates (crown star cone + 12, middle 14, lower 14, "
          "two rows each) stacked by peg and square recess on a smooth tapered orange trunk with two knots and six "
          "blunt root flares, on a thin sand patch with 4 pale grey rocks, 4 broad-leaf rosettes and 3 sprigs. No VFX",
    TOP_P: "Top Foliage Tier: 4 + 4-ridge star cone with 8 hem plates and 4 upper plates, square recess underneath",
    MID_P: "Middle Tier: the lower tier's construction at 0.8 (core with recess, flat cap and peg, 14 plates in two rows)",
    LOW_P: "Lower Foliage Tier: pleated core with a square recess, a flat cap and an octagonal peg, 14 plates in two rows",
    TRUNK_P: "Trunk: smooth 8-sided tapered stump with two knots, a flat top (the peg) and six blunt root flares",
    GF_P: "Ground Foliage: an upright fan of 11 broad round-tipped oval leaves (lime and green outside, dark and green "
          "inside) on a hub",
    RM_P: "Rock (Medium): chunky faceted pale grey block with a flat sloping crown",
    RS_P: "Rock (Small): chunky faceted pale grey block with a flat sloping crown",
}
COLLISION = {HERO: "precise", TOP_P: "hull", MID_P: "hull", LOW_P: "hull", TRUNK_P: "hull", GF_P: "box",
             RM_P: "hull", RS_P: "hull"}


def _new(name, fn, role, budget):
    """Build fn into a fresh tagged kit object in the model's collection, keeping the build frame."""
    old = bpy.data.objects.get(name)
    if old:
        if old.get("kit_sheet") not in (None, SHEET):
            raise RuntimeError(f"{name} belongs to {old.get('kit_sheet')}")
        for c in list(old.children_recursive):
            bpy.data.objects.remove(c, do_unlink=True)
        me = old.data
        bpy.data.objects.remove(old, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    a = K.fk().Asset(name, f"{SHEET} {TITLE}", seed=7, tint_var=0.0)
    fn(a)
    o = a.finish(collection=M.coll(NUM, TITLE), mark_asset=True, origin=None)
    K.drop_unused_slots(o)
    if "kit_part" in o.data.attributes:
        o.data.attributes.remove(o.data.attributes["kit_part"])
    K.tag(o, SHEET, TITLE, role, COLLISION[name], budget, NOTES[name])
    o[OFF] = [0.0, 0.0, 0.0]
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


def _post(o):
    """Stage 2-3 pass for an object of closed shells: every face a triangle, normals outward per shell, flat shading,
    origin at the bbox bottom centre, UVs (angle-based islands, overlaps cut free), bowties split."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = False
    if o.data.has_custom_normals:
        with M._override(o):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
    _recentre(o)
    lg = {"bowties": M.fix_bowties(o)}
    M.smart_uv(o, **UV)
    lg["uv_cut"] = m012._uv_unfold(o)
    K.drop_unused_slots(o)
    return lg


def _make_trunk():
    t0 = time.time()
    o = _new(TRUNK_P, trunk_part, "part", 1000)
    lg = {}
    m033._sane(o)
    lg["unions"] = m033._union_fine(o)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    lg["slivers_forced"] = m012._force_slivers(o, lim=2.0, max_len=0.12)
    lg.update(_post(o))
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


def _make_shells(name, fn, role="part", budget=1000):
    o = _new(name, fn, role, budget)
    return o, _post(o)


def _make_hero(trunk):
    t0 = time.time()
    o = _new(HERO, hero_rest, "hero", 4000)
    c = bpy.data.objects.new(PFX + "trunk", trunk.data.copy())
    o.users_collection[0].objects.link(c)
    c.matrix_world = Matrix.Translation(Vector(trunk[OFF]))
    bpy.context.view_layer.update()
    with M._override(o):
        c.select_set(True)
        with bpy.context.temp_override(selected_objects=[o, c], selected_editable_objects=[o, c]):
            bpy.ops.object.join()
    lg = _post(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


# ---- checks ----------------------------------------------------------------------------------------------------------
def _keys(o):
    return [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]


def _kind(ks, nf):
    if any("plant" in k for k in ks):
        return "leaf" if nf == LEAF_TRIS else "hub"
    if any("bark" in k for k in ks) and any("needle" in k for k in ks):
        return "core"
    if any("bark" in k for k in ks):
        return "trunk"
    if any("needle" in k for k in ks):
        return "plate"
    if any("sand" in k for k in ks):
        return "patch"
    if any("rock" in k for k in ks):
        return "rock"
    return "other"


def shells_report(o):
    """Per shell: kind, tris, non-manifold edges and verts, boundary edges, self-intersecting face pairs inside the
    shell, signed volume (closed and outward when > 0)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = _keys(o)
    groups = {}
    for f in bm.faces:
        groups.setdefault(ids[f.index], []).append(f)
    out = []
    for k in range(n):
        fs = groups[k]
        es = {e for f in fs for e in f.edges}
        vs = list({v for f in fs for v in f.verts})
        ks = {keys[f.material_index] for f in fs}
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        hits = sum(1 for a_, b_ in tree.overlap(tree) if a_ < b_ and not set(fs[a_].verts) & set(fs[b_].verts))
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) / 3.0
        # winding (STAGES "Consistent winding"): a manifold edge whose two faces walk it the same way
        wind = 0
        for e in es:
            if len(e.link_faces) == 2:
                dirs = []
                for f in e.link_faces:
                    vv = list(f.verts)
                    i = vv.index(e.verts[0])
                    dirs.append(vv[(i + 1) % len(vv)] == e.verts[1])
                wind += dirs[0] == dirs[1]
        xs = [v.co.x for v in vs]
        ys = [v.co.y for v in vs]
        out.append({"kind": _kind(ks, len(fs)), "tris": len(fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary), "self_hits": hits, "winding": wind,
                    "volume": round(vol, 4), "zmin": round(min(v.co.z for v in vs), 3),
                    "zmax": round(max(v.co.z for v in vs), 3),
                    "size": [round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2)]})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating dressing (STAGES): per shell, whether it touches another shell (triangles intersect, or a vertex
    within `tol` of another shell's surface) or the ground (z <= tol). Anchors: shells on the ground; for a tier or
    the trunk alone, its core / trunk. Returns the floating count, the worst gap, shells with no chain of contact to an
    anchor, the core seat gaps, plate pairs that visibly cut into each other (crossing points outside every core) and
    leaves that cut into a rock or the trunk."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = _keys(o)
    fsh = [ids[f.index] for f in bm.faces]
    vsh = {}
    for f in bm.faces:
        for v in f.verts:
            vsh[v.index] = fsh[f.index]
    shell_keys = [set() for _ in range(n)]
    nfaces = [0] * n
    for f in bm.faces:
        shell_keys[fsh[f.index]].add(keys[f.material_index])
        nfaces[fsh[f.index]] += 1
    kinds = [_kind(shell_keys[k], nfaces[k]) for k in range(n)]
    tree = BVHTree.FromBMesh(bm)
    zmin = [1e9] * n
    for v in bm.verts:
        if v.index in vsh:
            zmin[vsh[v.index]] = min(zmin[vsh[v.index]], v.co.z)
    z0 = min(zmin)
    pairs = set()
    overl = list(tree.overlap(tree))
    for i, j in overl:
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
    seats = sorted(round(d, 4) for (a_, b_), d in near.items()
                   if {kinds[a_], kinds[b_]} in ({"core"}, {"core", "trunk"}) and (a_, b_) not in pairs)
    seat_cuts = sum(1 for (a_, b_) in pairs if {kinds[a_], kinds[b_]} in ({"core"}, {"core", "trunk"}))
    for kk in pairs:
        near[kk] = 0.0
    gap = [1e9] * n
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    if any(kinds[k] == "patch" for k in range(n)) or all(kinds[k] in ("leaf", "hub", "rock") for k in range(n)):
        ground = {k for k in range(n) if zmin[k] - z0 <= tol}
    else:
        ground = {k for k in range(n) if kinds[k] in ("core", "trunk")}
    for k in ground:
        gap[k] = 0.0

    loose_k = []

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
        loose_k[:] = [(kinds[k], round(zmin[k], 2)) for k in range(n) if k not in seen][:12]
        return n - len(seen)
    floating = [k for k in range(n) if gap[k] > tol]
    core_f = [f for f in bm.faces if kinds[fsh[f.index]] == "core"]
    cvi = {}
    for f in core_f:
        for v in f.verts:
            cvi.setdefault(v, len(cvi))
    core_tree = BVHTree.FromPolygons([v.co for v in cvi], [[cvi[v] for v in f.verts] for f in core_f]) if core_f else None
    cut_pairs, leaf_cuts = set(), set()
    recs = {}

    def rec(k):
        if k not in recs:
            fs = [f for f in bm.faces if fsh[f.index] == k]
            vi = {}
            for f in fs:
                for v in f.verts:
                    vi.setdefault(v, len(vi))
            recs[k] = _rec([v.co.copy() for v in vi], [[vi[v] for v in f.verts] for f in fs])
        return recs[k]
    depths = {}
    for kp in pairs:
        if kinds[kp[0]] == "plate" and kinds[kp[1]] == "plate":
            depths[kp] = _depth(rec(kp[0]), rec(kp[1]), core_tree)
            if depths[kp] > CUT:
                cut_pairs.add(kp)
    for i, j in overl:
        a_, b_ = fsh[i], fsh[j]
        if a_ == b_:
            continue
        kp = (min(a_, b_), max(a_, b_))
        ka = {kinds[a_], kinds[b_]}
        if "leaf" in ka and ka & {"rock", "trunk"} and kp not in leaf_cuts:
            ta = [v.co for v in bm.faces[i].verts]
            tb = [v.co for v in bm.faces[j].verts]
            if _cut_pts(ta, tb):
                leaf_cuts.add(kp)
    res = {"shells": n, "floating": len(floating),
           "floating_kinds": sorted({kinds[k] for k in floating}),
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "max_gap_all": round(max(gap[k] for k in range(n)), 3),
           "unchained": chained(tol), "unchained_kinds": list(loose_k), "unchained_chain_tol": chained(chain_tol),
           "plate_plate_cuts": len(cut_pairs), "plate_cut_max": round(max(depths.values(), default=0.0), 3),
           "plate_pairs_touching": len(depths), "leaf_cuts": len(leaf_cuts), "core_seats": seats,
           "core_seat_cuts": seat_cuts, "kinds": {k: kinds.count(k) for k in sorted(set(kinds))}}
    bm.free()
    return res


# ---- build -----------------------------------------------------------------------------------------------------------
PARTS = ((TOP_P, top_part), (MID_P, middle_part), (LOW_P, lower_part), (GF_P, ground_foliage_part),
         (RM_P, rock_medium_part), (RS_P, rock_small_part))
TARGET_SIZE = ((7.6, 0.4), (7.3, 0.4), (10.0, 0.2))   # fix round 1: hem tips r 3.6-3.8 set the depth (patch 6.4)


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m045_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib",
                                                                                 "PineSapling"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


ORDER = (TOP_P, MID_P, LOW_P, TRUNK_P, GF_P, RM_P, RS_P)


def build(render=True, parts=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    m033.UNION_RETRIES.clear()
    palette()
    TIER_INFO.clear()
    TIER_RECS.clear()
    LEAF_INFO.clear()
    objs, log = {}, {}
    trunk, log[TRUNK_P] = _make_trunk()
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make_shells(name, fn)
    objs[TRUNK_P] = trunk
    h, log["hero"] = _make_hero(trunk)
    log["tiers"] = {k: dict(v) for k, v in TIER_INFO.items()}
    log["leaves"] = {k: dict(v) for k, v in LEAF_INFO.items()}
    log["union_retries"] = list(m033.UNION_RETRIES)
    _cleanup_tmp()
    order = [h] + [objs[n] for n in ORDER if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    out = check(order)
    out["log"] = log
    out["build_s"] = round(time.time() - t0, 1)
    if render:
        out["views"] = render_views(order)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


def check(order):
    h = order[0]
    trunk = next((o for o in order if o.name == TRUNK_P), None)
    audits = [M.audit(o) for o in order]
    thin = {o.name: m012._thin(o, 2.0) for o in order}
    shells = {o.name: shells_report(o) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = 4000 if o is h else 1000
        if au["tris"] > lim:
            problems.append(f"{o.name}: {au['tris']} tris over {lim}")
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "wire_edges", "loose_verts",
                  "zero_area_faces", "ngons"):
            if au[k]:
                problems.append(f"{o.name}: {k} {au[k]}")
        if au["normals"] != "outward":
            problems.append(f"{o.name}: normals {au['normals']}")
        for i, s in enumerate(shells[o.name]):
            for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "self_hits", "winding"):
                if s[k]:
                    problems.append(f"{o.name} shell {i} ({s['kind']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['kind']}): not closed outward (volume {s['volume']})")
    contact = {o.name: contact_report(o) for o in order if o is not trunk and len(shells[o.name]) > 1}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} shells touch nothing within {CONTACT}, {c['unchained']} have no "
                            f"chain of contact to the ground")
        if c["plate_plate_cuts"]:
            problems.append(f"{n_}: {c['plate_plate_cuts']} plate pairs cut into each other")
        if c["leaf_cuts"]:
            problems.append(f"{n_}: {c['leaf_cuts']} leaves cut into a rock or the trunk")
        if c["core_seat_cuts"]:
            problems.append(f"{n_}: {c['core_seat_cuts']} core / trunk pairs intersect (pegs must clear the recesses)")
        if any(s > CONTACT for s in c["core_seats"][:3]):
            problems.append(f"{n_}: core seats {c['core_seats'][:4]}")
    if trunk is not None and len(shells[TRUNK_P]) != 1:
        problems.append(f"{TRUNK_P}: {len(shells[TRUNK_P])} shells, expected 1")
    if sum(1 for s in shells[h.name] if s["kind"] == "trunk") != 1:
        problems.append(f"{HERO}: {sum(1 for s in shells[h.name] if s['kind'] == 'trunk')} trunk shells, expected 1")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 13: none)")
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    kinds = {}
    for s in shells[h.name]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    return {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                          "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                          "ngons", "dup_verts", "origin_offset", "transforms_applied")}
                      for au in audits],
            "hero_shells": kinds, "contact": contact, "thin": thin, "problems": problems, "uv": uv,
            "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
            "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
            "baked_shading": {o.name: o.get("kit_baked_shading") for o in order}}


# ---- renders ---------------------------------------------------------------------------------------------------------
# decision 10: f34_sheet (-15, 16) governs; r34_sheet (165, 16), front / side / rear_sheet at e 5, kit top and underside;
# floor hidden and a 3x lens on the *_sheet shots (m033._long_lens)
SHEET_VIEWS = {"f34_sheet": (-15, 16), "r34_sheet": (165, 16), "front_sheet": (0, 5), "side_sheet": (90, 5),
               "rear_sheet": (180, 5), "top_sheet": (0, 89)}
PARTS_SHOT = (-15, 20)


def _copy(o, tag, m, coll):
    c = bpy.data.objects.new(f"{PFX}{tag}", o.data)
    coll.objects.link(c)
    c.matrix_world = m
    return c


def _exploded(objs):
    """Copies laid out like the sheet's Exploded Construction: top tier over lower tier over trunk (the middle tier
    between them, which the sheet does not draw), the ground pieces in a row in front and below."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    x0 = objs[0].location.x + 70
    y0 = objs[0].location.y
    base = Matrix.Translation((x0, y0, 0))
    shown = []
    lift = {TRUNK_P: 1.5, LOW_P: 4.5, MID_P: 7.0, TOP_P: 9.5}
    for name, dz in lift.items():
        if name in by:
            shown.append(_copy(by[name], "expl_" + name, base @ Matrix.Translation((0, 0, dz))
                               @ Matrix.Translation(Vector(by[name][OFF])), coll))
    row = [(GF_P, (-3.2, -4.0, 0)), (RM_P, (0.0, -4.5, 0)), (RS_P, (3.0, -4.2, 0))]
    for name, p in row:
        if name in by:
            shown.append(_copy(by[name], "expl_" + name, base @ Matrix.Translation(p), coll))
    bpy.context.view_layer.update()
    return shown


def _scale_marker(h):
    """A 5.5-stud character stand-in beside the hero, for the scale shot."""
    a = K.fk().Asset(PFX + "char", "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=ROCK_DEEP, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=ROCK_DEEP, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=ROCK_DEEP, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    c.location = h.location + Vector((h.dimensions.x / 2 + 1.0, -2.0, 0))
    bpy.context.view_layer.update()
    return c


def _no_patch(h):
    """A temporary copy of the hero without its sand patch (close-up 3 draws none)."""
    me = h.data.copy()
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = _keys(h)
    sand = {ids[f.index] for f in bm.faces if "sand" in keys[f.material_index]}
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if ids[f.index] in sand], context="FACES")
    bm.to_mesh(me)
    bm.free()
    c = bpy.data.objects.new(PFX + "nopatch", me)
    h.users_collection[0].objects.link(c)
    c.matrix_world = h.matrix_world.copy()
    bpy.context.view_layer.update()
    return c


def render_views(objs, close=True):
    h = objs[0]
    by = {o.name: o for o in objs}
    shown = _exploded(objs) if len(objs) > 1 else []
    marker = _scale_marker(h)
    nop = _no_patch(h)
    temps = shown + [marker, nop]
    coll = h.users_collection[0]
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        for o in objs[1:]:
            extra["part_" + o.name.replace("PineSapling", "").lower()] = ([o], *PARTS_SHOT)
        if shown:
            extra["exploded"] = (shown, -15, 20)
        extra["scale"] = ([h, marker], -20, 8)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = m033._long_lens(kit)
        try:
            sheet = M.views(NUM, [h], extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet}
        if close:
            d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
            off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
            out["root_cu"] = m033.render_close([h], f"{d}/root_cu.png", -20, 15, off @ Vector((0.0, -0.6, 0.8)), 2.6)
            out["underside_cu"] = m033.render_close([nop], f"{d}/underside_cu.png", 0, -80,
                                                    off @ Vector((0.0, 0.0, 1.0)), 3.2)
            if LOW_P in by and TRUNK_P in by:
                # close-up 1: the lower tier lifted off its trunk, seen from the front and below
                x0 = h.location.x + 70
                b = Matrix.Translation((x0, h.location.y + 30, 0))
                lo = _copy(by[LOW_P], "join_low", b @ Matrix.Translation((0, 0, 1.4))
                           @ Matrix.Translation(Vector(by[LOW_P][OFF])), coll)
                tr = _copy(by[TRUNK_P], "join_trunk", b @ Matrix.Translation(Vector(by[TRUNK_P][OFF])), coll)
                temps += [lo, tr]
                bpy.context.view_layer.update()
                out["join_cu"] = m033.render_close([lo, tr], f"{d}/join_cu.png", 0, -30,
                                                   b @ Vector((0.0, 0.0, 4.6)), 2.0)
                # close-up 2: lower tier plates from the side
                out["plate_cu"] = m033.render_close([lo], f"{d}/plate_cu.png", -60, 15,
                                                    b @ Vector((0.6, -2.4, 4.7)), 1.6)
        return out
    finally:
        own = {marker.name, nop.name}
        for o in temps:
            me, nm = o.data, o.name
            bpy.data.objects.remove(o, do_unlink=True)
            if nm in own and me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def preview(names=("f34_sheet", "front_sheet", "r34_sheet", "top_sheet"), vfx=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig


def hero_only():
    """Rebuild just the trunk and the hero (tuning loop)."""
    M.coll(NUM, TITLE)
    palette()
    TIER_INFO.clear()
    TIER_RECS.clear()
    LEAF_INFO.clear()
    trunk, lt = _make_trunk()
    h, lg = _make_hero(trunk)
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n in ORDER if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals")}, "log": lg, "trunk": lt,
            "tiers": {k: dict(v) for k, v in TIER_INFO.items()}, "leaves": {k: dict(v) for k, v in LEAF_INFO.items()}}
