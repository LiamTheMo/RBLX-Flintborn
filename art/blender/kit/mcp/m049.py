"""049 Classic Pine (references/049.png): the kit's tall standard pine (22 tall). Four canopy rings stack by peg and
hex sleeve on a thick planked trunk: a five-ridge crown cone with 10 blades, Tier 2 (10 outer + 10 inner blades),
Tier 1 upper (12 + 11) and Tier 1 lower (14 + 13). Every blade is a long parallel-sided board with a shallow ridge, a keel (edge
thickness) and a cut-off chisel tip; each ring lays two rows, the inner row on top of the outer one (fix round 1: the
inner row is built first on the core, the outer hem row sinks under it and flares out). The trunk is one
lofted closed shell: seven buttress roots are part of its foot (no union), planks, grooves and a knot slit up the body,
a thick rim round a dished recess and a peg on top. The base is a thin sand patch with five chunky warm grey rocks,
three pebbles, two faceted bush mounds and six upright broad-leaf clusters plus two sprigs.

    import importlib, kit_models, m049; importlib.reload(kit_models); importlib.reload(m049); m049.build()

Build frame: studs, front -Y, +X right, ground z 0 = the sand patch's flat underside, tree axis at (0, 0). Every object
ends with its origin at its bbox bottom centre; o["m049_offset"] is that origin in the build frame.
- TallPineCanopyTier3 / Tier2 / Tier1Upper / Tier1Lower: ring(kind): one closed core shell (crown: the star cone) with
  its sleeve and blind hole (and a top peg on Tiers 1-2), plus its blade shells.
- TallPineTrunk: trunk(): one closed lofted shell (roots, planks, knot, rim, recess, peg).
- TallPineRootFoot: patch, rocks, pebbles, bush lobes, cluster hubs and leaves (closed shells).
- TallPine (hero): all of it in one object of closed shells. No booleans anywhere.
Colour (stage 4) is painted by position and role inside the builders, never by facing. Stages 5-6: none (the sheet shows
no glow, light or effect). See M049_spec.md. Patterns copied (not imported) from m045 (cut tests, contact report).
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

NUM, TITLE, SHEET = 49, "Classic Pine", "M049"
OFF = "m049_offset"
PFX = "_m049_"
HERO = "TallPine"
T3_P, T2_P, T1U_P, T1L_P = ("TallPineCanopyTier3", "TallPineCanopyTier2", "TallPineCanopyTier1Upper",
                            "TallPineCanopyTier1Lower")
TRUNK_P, FOOT_P = "TallPineTrunk", "TallPineRootFoot"

NEEDLE, NEEDLE_LIGHT, NEEDLE_DEEP = "m049_needle", "m049_needle_light", "m049_needle_deep"
BARK, BARK_LIGHT, BARK_DEEP = "m049_bark", "m049_bark_light", "m049_bark_deep"
ROCK, ROCK_LIGHT, ROCK_DEEP = "m049_rock", "m049_rock_light", "m049_rock_deep"
SAND, SAND_DEEP = "m049_sand", "m049_sand_deep"
BUSH, BUSH_DEEP = "m049_bush", "m049_bush_deep"
PLANT, PLANT_DEEP = "m049_plant", "m049_plant_deep"
HOLE = "m049_hole"     # the sleeves' blind holes: near-black brown cavity (close-up 1), fix round 1

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
CUT = 0.05            # spec 6: neighbouring blades may touch but cut no more than 0.05 into each other
BURY = 0.05           # STAGES: no dressing shell more than 0.05 inside rock

# key -> (hex, roughness, low specular). Stage 4 writes the calibrated values here (M049_spec.md "Stage 4").
PALETTE = {
    NEEDLE: ("#416E31", 0.85, True),
    NEEDLE_LIGHT: ("#ACC22A", 0.85, True),
    NEEDLE_DEEP: ("#274D39", 0.9, True),
    BARK: ("#9B5D1D", 0.9, False),
    BARK_LIGHT: ("#B47B3B", 0.9, False),
    BARK_DEEP: ("#6F411E", 0.95, False),
    ROCK: ("#B0A496", 0.85, False),
    ROCK_LIGHT: ("#BEB2A2", 0.85, False),
    ROCK_DEEP: ("#878382", 0.9, False),
    SAND: ("#BCAA88", 0.95, False),
    SAND_DEEP: ("#B29E7B", 0.95, False),
    BUSH: ("#8EA625", 0.85, True),
    BUSH_DEEP: ("#568A2A", 0.85, True),
    PLANT: ("#8CA012", 0.85, True),
    PLANT_DEEP: ("#66A02A", 0.85, True),
    HOLE: ("#2E1C10", 0.95, False),
}
# calibration targets (spec 5.4: rendered medians of unshadowed regions of the sheet, sRGB)
TARGETS = {NEEDLE: ((0x4C, 0x82, 0x32), "green"), NEEDLE_LIGHT: ((0xB0, 0xCD, 0x34), "green"),
           NEEDLE_DEEP: ((0x2B, 0x58, 0x3B), "green"), BARK: ((0xC5, 0x71, 0x2A), "brown"),
           BARK_LIGHT: ((0xE5, 0x95, 0x48), "brown"), BARK_DEEP: ((0x8B, 0x51, 0x2E), "brown"),
           ROCK: ((0xDC, 0xCB, 0xB6), "stone"), ROCK_LIGHT: ((0xE7, 0xD5, 0xC0), "stone"),
           ROCK_DEEP: ((0xAA, 0xA0, 0x97), "stone"), SAND: ((0xEF, 0xD3, 0xA1), "brown"),
           SAND_DEEP: ((0xE3, 0xC4, 0x8F), "brown"), BUSH: ((0xB0, 0xC8, 0x25), "green"),
           BUSH_DEEP: ((0x4E, 0x7A, 0x22), "green"), PLANT: ((0xAB, 0xC0, 0x13), "green"),
           PLANT_DEEP: ((0x55, 0x7C, 0x16), "green")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    # mixed keys made by an earlier build: re-mix them from the (possibly new) parents
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m049_") else None
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
    """Triangles between two closed rings about +Z, walking both by angle from a common reference angle (m045._zip)."""
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


def _band(bm, ra, rb):
    """Quads between two rings of the same vertex count (index k to k)."""
    n = len(ra)
    return [bm.faces.new((ra[k], ra[(k + 1) % n], rb[(k + 1) % n], rb[k])) for k in range(n)]


def _q(t, steps=4):
    t = max(0.0, min(1.0, t))
    return round(t * steps) / steps


def _mix(k1, k2, t):
    return K.mix_key(k1, k2, _q(t))


def _needle(v):
    """A blade tone on one axis: v < 0 toward NEEDLE_DEEP, v > 0 toward NEEDLE_LIGHT (25 % steps)."""
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


def _ring(bm, n, r, z, az0=0.0, shift=(0.0, 0.0)):
    return [bm.verts.new(_u(az0 + 360.0 * k / n) * r + Vector((shift[0], shift[1], z))) for k in range(n)]


def _srt(r):
    return sorted(r, key=lambda v: math.atan2(v.co.y, v.co.x))


# ---- blades (spec 2.3) -----------------------------------------------------------------------------------------------
SA, SB = 0.30, 0.72          # sections A and B along the blade (fraction of its length)
RIDGE, KEEL = 0.08, 0.12     # ridge above / keel below the mid-plane at section A (fraction of the width)
TIPW = 0.24                # truncated tip width (fraction of the width): a chisel point that reads pointed from above
BLADE_TRIS = 18


def _blade_local(L, W, droop, sa=SA, ridge=RIDGE, bend=None):
    """Blade points in its own frame (x along, y across, z up): a root point, section A (left, ridge, right, keel) at
    sa * L (0.30 L; inner rows 0.50 L), section B at SB (0.70) L with the same width (parallel sides; ridge and keel
    0.8x) bent down a further droop / 2 about A, and two tip points TIPW (0.20) W apart at L, bent down droop about B
    (the chisel point). bend = (deg at A, cumulative deg at B) replaces (droop / 2, droop): a negative first angle
    flares the blade up at A (a narrow waist above, the hem still wide; m045's row A), the second droops the tip.
    ridge: the ridge height (fraction of W). Returns (points, tip)."""
    d1, d2 = (math.radians(droop) * 0.5, math.radians(droop)) if bend is None else map(math.radians, bend)
    A = (sa * L, 0.0)
    B = (A[0] + (SB - sa) * L * math.cos(d1), A[1] - (SB - sa) * L * math.sin(d1))
    T = (B[0] + (1 - SB) * L * math.cos(d2), B[1] - (1 - SB) * L * math.sin(d2))
    p = {"R": Vector((0.0, 0.0, 0.0))}
    for tag, P, ang, f in (("A", A, d1 / 2, 1.0), ("B", B, (d1 + d2) / 2, 0.8)):
        n = (math.sin(ang), math.cos(ang))          # normal of a direction pointing down by ang
        p[tag + "l"] = Vector((P[0], W / 2, P[1]))
        p[tag + "r"] = Vector((P[0], -W / 2, P[1]))
        p[tag + "t"] = Vector((P[0] + n[0] * ridge * W * f, 0.0, P[1] + n[1] * ridge * W * f))
        p[tag + "k"] = Vector((P[0] - n[0] * KEEL * W * f, 0.0, P[1] - n[1] * KEEL * W * f))
    p["Tl"] = Vector((T[0], TIPW * W / 2, T[1]))
    p["Tr"] = Vector((T[0], -TIPW * W / 2, T[1]))
    return p, Vector((T[0], 0.0, T[1]))


def blade(a, az, r0, z0, r1, z1, w, droop=12.0, roll=0.0, tones=(0.0, 0.0, 0.0), tint=1.0, sa=SA, ridge=RIDGE,
          bend=None):
    """One closed 18-tri blade (spec 2.3): its root point at (r0, z0) on azimuth az (buried in its core), the tip
    centre at (r1, z1); width w (parallel sides), the outer part bent down `droop` degrees in two steps (or `bend`, see
    _blade_local), rolled `roll` degrees about its own axis (neighbours shingle). tones = (root, middle, tip) band tones
    on the _needle axis (colour by position along the blade). Returns (verts, faces)."""
    bm = a.bm
    dr, dz = r1 - r0, z1 - z0
    C = math.hypot(dr, dz)
    L = C
    for _ in range(4):
        pts, tip = _blade_local(L, w, droop, sa, ridge, bend)
        L *= C / tip.length
    pts, tip = _blade_local(L, w, droop, sa, ridge, bend)
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
    V = {k: bm.verts.new(world(p)) for k, p in pts.items()}
    nf = bm.faces.new
    root = [nf((V["R"], V["Al"], V["At"])), nf((V["R"], V["At"], V["Ar"])), nf((V["R"], V["Ar"], V["Ak"])),
            nf((V["R"], V["Ak"], V["Al"]))]
    mid = [nf((V["Al"], V["Bl"], V["Bt"], V["At"])), nf((V["At"], V["Bt"], V["Br"], V["Ar"])),
           nf((V["Ar"], V["Br"], V["Bk"], V["Ak"])), nf((V["Ak"], V["Bk"], V["Bl"], V["Al"]))]
    tipf = [nf((V["Bl"], V["Tl"], V["Bt"])), nf((V["Bt"], V["Tl"], V["Tr"])), nf((V["Bt"], V["Tr"], V["Br"])),
            nf((V["Br"], V["Tr"], V["Bk"])), nf((V["Bk"], V["Tr"], V["Tl"])), nf((V["Bk"], V["Tl"], V["Bl"]))]
    vs = list(V.values())
    a._finish(vs, _needle(tones[1]), tint=tint)
    _paint(a, root, _needle(tones[0]))
    _paint(a, tipf, _needle(tones[2]))
    res = bmesh.ops.triangulate(bm, faces=mid, quad_method="BEAUTY", ngon_method="BEAUTY")
    fs = root + res["faces"] + tipf
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    return vs, fs


# ---- cut tests (copied from m045: ray-parity inside test, triangle crossing points) ----------------------------------
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


def _hits(vs, coords, polys):
    """Whether a shell (its verts) crosses any triangle of (coords, polys)."""
    fs = _faces(vs)
    idx = {v: i for i, v in enumerate(vs)}
    mine_p = [[idx[v] for v in f.verts] for f in fs]
    mine_c = [v.co.copy() for v in vs]
    mine = BVHTree.FromPolygons(mine_c, mine_p)
    for i, j in mine.overlap(BVHTree.FromPolygons(coords, polys)):
        ta = [mine_c[k] for k in mine_p[i]]
        tb = [coords[k] for k in polys[j]]
        if _cut_pts(ta, tb):
            return True
    return False


def _rec(coords, polys):
    """A closed shell as a record for cut-depth tests: its BVH and sample points (corners, edge midpoints, centres)."""
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
    other's surface), ignoring samples hidden inside `core`. 0 when they don't overlap."""
    if not A["tree"].overlap(B["tree"]):
        return 0.0
    d = 0.0
    for P, Q in ((A, B), (B, A)):
        for p in P["smp"]:
            if _inside(Q["tree"], p) and (core is None or not _inside(core, p)):
                d = max(d, Q["tree"].find_nearest(p)[3])
    return d


# ---- rings (spec 2.2) ------------------------------------------------------------------------------------------------
# Stack (spec 2.1, heights re-derived so every blind hole swallows the peg below with 0.1 head room and every core
# stays solid above its hole): trunk rim 11.0 / peg top 12.2 -> T1L seat 11.015, hole ceiling 12.30, cap 14.50, peg top
# 14.95 -> T1U seat 14.515, ceiling 15.05, cap 15.40, peg 15.85 -> T2 seat 15.415, ceiling 15.95, cap 18.20, peg 18.65
# -> crown seat 18.215, ceiling 18.75, apex 22.0. Pegs are octagons of apothem 0.425; holes octagons of apothem 0.55.
PEG_APO, HOLE_APO = 0.425, 0.55
COS8 = math.cos(math.radians(22.5))
COS6 = math.cos(math.radians(30.0))
TRUNK_RIM, TRUNK_PEG_TOP = 11.0, 12.2
# rows: n blades from az0; root (r0, z0) -> tip (r1, z1); front: the tip z of the blade aimed at -Y (it hangs lowest);
# fix: "roll" (rolled / narrowed until clear of its neighbours), "lift" (rests on the rows before: its tip is raised
# about its buried root), "sink" (tucks under them). tones: (root, middle, tip) on the _needle axis.
# Fix round 1: every tier lays its INNER row first, on its core (roots under the cap, the core cone steepened so the
# blades leave it early), then its OUTER (hem) row as a sink row under it (m045 fix round 1: row B on top, the waists
# narrow). Outer rows flare up at A (bend) so the waist above stays narrow while the hem reaches its width. Long narrow
# boards (outer L : W >= 2.5, inner >= 2.0), more blades instead of wider ones.
RINGS = {
    "t1l": dict(seat=11.015, sleeve=(1.25, 12.05), ceil=12.30, cap=(0.90, 14.50), rim=(1.75, 13.20),
                peg=14.95, seed=49100, below=None,
                rows=[dict(n=13, az0=270.0 + 180.0 / 13, r0=0.60, z0=14.15, r1=3.70, z1=11.20, front=None, w=1.3,
                           droop=6.0, fix="roll", roll=2.0, sa=0.5, tones=(-0.5, -0.25, -0.25)),
                      dict(n=14, az0=270.0, r0=1.50, z0=13.00, r1=8.30, z1=7.70, front=7.20, w=2.8, bend=(-14.0, -4.0),
                           droop=0.0, fix="sink", roll=5.0, tones=(-0.5, -0.25, -0.25))]),
    "t1u": dict(seat=14.515, sleeve=(1.00, 14.60), ceil=15.05, cap=(0.85, 15.40), rim=(2.00, 13.85),
                peg=15.85, seed=49200, below="t1l",
                rows=[dict(n=11, az0=270.0 + 180.0 / 11, r0=0.60, z0=15.25, r1=3.85, z1=12.40, front=None, w=1.5,
                           droop=6.0, fix="roll", roll=4.0, sa=0.5, tones=(-0.5, 0.0, 0.0)),
                      dict(n=12, az0=270.0, r0=1.45, z0=14.40, r1=7.45, z1=9.30, front=9.10, w=2.5, bend=(-14.0, -6.0),
                           droop=0.0, fix="sink", roll=3.0, tones=(-0.5, 0.0, 0.0))]),
    "t2": dict(seat=15.415, sleeve=(0.90, 16.10), ceil=15.95, cap=(0.80, 18.20), rim=(1.70, 16.75),
               peg=18.65, seed=49300, below="t1u",
               rows=[dict(n=10, az0=270.0 + 18.0, r0=0.55, z0=18.00, r1=3.40, z1=15.20, front=None, w=1.35,
                          droop=6.0, fix="roll", roll=4.0, sa=0.5, tones=(-0.25, 0.25, 0.25)),
                     dict(n=10, az0=270.0, r0=1.25, z0=16.85, r1=5.85, z1=13.30, front=13.00, w=2.05,
                          bend=(-16.0, -6.0), droop=0.0, fix="sink", roll=5.0, tones=(-0.25, 0.25, 0.25))]),
    # crown: a deep five-ridge star cone (ridges r 2.3, valleys 1.5, rim z 18.3, base needle) with 5 long narrow lime
    # blades lying just above its ridges from the apex to the hem (the lime five-ridge star seen from above, a raised
    # ridge 0.35 W for the lit / shaded halves), 5 short ones tucked under them in the valleys
    "crown": dict(seat=18.215, sleeve=(0.80, 18.50), ceil=18.75, apex=22.0, rim_z=18.30, ridges=(2.3, 1.5),
                  seed=49400, below="t2",
                  rows=[dict(n=5, az0=270.0, r0=0.05, z0=21.80, r1=3.50, z1=17.30, front=17.15, w=1.3, droop=-4.0,
                             fix="roll", roll=0.0, ridge=0.35, tones=(0.25, 0.5, 0.5)),
                        dict(n=5, az0=270.0 + 36.0, r0=0.55, z0=20.10, r1=2.45, z1=17.70, front=None, w=0.9,
                             droop=-8.0, fix="sink", roll=0.0, tones=(0.0, 0.25, 0.25))]),
}
RING_INFO = {}
RING_RECS = {}           # kind -> cut-test records of its blades (build frame), for the ring above to rest on
CORE_RECS = {}           # kind -> cut-test record of its core


def _top_z(R, r):
    """Height of a ring core's top cone at plan radius r (cap -> rim, straight)."""
    (cr, cz), (rr, rz) = R["cap"], R["rim"]
    return cz + (rz - cz) * (r - cr) / (rr - cr)


def _core(a, kind):
    """The ring's closed core shell (spec 2.3): Tiers 1-2: an octagonal top peg on a flat cap, a cone down to the rim
    (one corner per outer-row azimuth; fix round 1 dropped the in-between pleat corners), an underside in to the hex
    sleeve, the sleeve's flat bottom with a blind octagonal hole (walls and ceiling part of the shell). Crown: the
    five-ridge star cone, its underside, the sleeve and hole. Returns (verts, faces by role)."""
    bm = a.bm
    R = RINGS[kind]
    seat = R["seat"]
    sc, st = R["sleeve"]
    hc = HOLE_APO / COS8
    sl_top = _ring(bm, 6, sc, st, 270.0)
    sl_bot = _ring(bm, 6, sc, seat, 270.0)
    mouth = _ring(bm, 8, hc, seat, 22.5)
    ceil = _ring(bm, 8, hc, R["ceil"], 22.5)
    role = {}
    if kind == "crown":
        apex = bm.verts.new(Vector((0, 0, R["apex"])))
        rim = []
        for k in range(10):
            r = R["ridges"][0] if k % 2 == 0 else R["ridges"][1]
            rim.append(bm.verts.new(_u(270.0 + 36.0 * k) * r + Vector((0, 0, R["rim_z"]))))
        rim = _srt(rim)
        role["top"] = [bm.faces.new((apex, rim[k], rim[(k + 1) % 10])) for k in range(10)]
        vs = [apex] + rim
        role["peg"] = []
    else:
        orow = next(r for r in R["rows"] if r["front"] is not None)      # the outer (hem) row
        n = orow["n"]
        a0 = orow["az0"]
        step = 360.0 / n
        pc = PEG_APO / COS8
        peg_t = _srt(_ring(bm, 8, pc, R["peg"], 22.5))
        peg_b = _srt(_ring(bm, 8, pc, R["cap"][1], 22.5))
        cap = _srt(_ring(bm, n, R["cap"][0], R["cap"][1], a0 + step / 2))
        rr, rz = R["rim"]
        # fix round 1: one rim corner per outer blade (no pleat valleys): the rim is hidden under the blades, and the
        # 2n-corner pleat cost the tris that now buy more blades
        rim = _srt([bm.verts.new(_u(a0 + k * step) * rr + Vector((0, 0, rz))) for k in range(n)])
        role["peg"] = [bm.faces.new(list(peg_t))]
        role["peg"] += [bm.faces.new((peg_b[k], peg_b[(k + 1) % 8], peg_t[(k + 1) % 8], peg_t[k])) for k in range(8)]
        role["top"] = _zip(bm, peg_b, cap) + _zip(bm, cap, rim)
        vs = peg_t + peg_b + cap + rim
    sl_top, sl_bot, mouth, ceil = map(_srt, (sl_top, sl_bot, mouth, ceil))
    role["under"] = _zip(bm, rim, sl_top)
    role["sleeve"] = _band(bm, sl_top, sl_bot)
    role["sleeve_bot"] = _zip(bm, sl_bot, mouth)
    role["hole"] = _band(bm, mouth, ceil) + [bm.faces.new(list(ceil))]
    vs += sl_top + sl_bot + mouth + ceil
    fs = [f for r in role.values() for f in r]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    if kind == "crown":
        # fix round 1: the cone is base needle, so the lime ridge blades on it read as a five-point star from above
        a._finish(vs, NEEDLE, tint=1.0)
        _paint(a, role["under"], _needle(-0.25))
    else:
        a._finish(vs, _mix(NEEDLE, NEEDLE_DEEP, 0.75), tint=1.0)
        _paint(a, role["peg"], BARK)                       # the peg is turned bark (exploded: the trunk's peg)
    _paint(a, role["sleeve"] + role["sleeve_bot"], _mix(BARK, BARK_DEEP, 0.75))
    _paint(a, role["hole"], HOLE)                          # the cavity (close-up 1: dark hole), hard: a socket
    _mottle(a, role["top"] + role["under"], 0.03, 0.5, R["seed"] + 7)
    bmesh.ops.triangulate(bm, faces=[f for f in _faces(vs) if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    return vs


def _below(kind):
    """Blade and core records of the ring under this one, in the build frame (a probe build when not built yet this
    run), so a part built alone and the same ring in the hero come out identical."""
    k = RINGS[kind]["below"]
    if k is None:
        return [], None
    if k not in RING_RECS:
        probe = K.fk().Asset("_probe_" + k, "probe")
        info = RING_INFO.get(k)
        ring(probe, k)
        probe.bm.free()
        if info is not None:
            RING_INFO[k] = info
    return RING_RECS[k], CORE_RECS[k]


def ring(a, kind):
    """A whole ring: its core, then the outer row, then the inner row. A blade that cuts a neighbour or the ring below
    more than CUT is fixed: a lift row's tip is raised about its buried root (then the blade whole), a sink row's
    lowered, a roll row rolled further, and narrowing (x0.96) is the last resort."""
    R = RINGS[kind]
    below, below_core = _below(kind)
    rng = random.Random(R["seed"])
    core_vs = _core(a, kind)
    out = list(core_vs)
    ci = {v: i for i, v in enumerate(core_vs)}
    core_c = [v.co.copy() for v in core_vs]
    core_p = [[ci[v] for v in f.verts] for f in _faces(core_vs)]
    core = BVHTree.FromPolygons(core_c, core_p)
    CORE_RECS[kind] = _rec(core_c, core_p)
    info = {"lifted": 0, "rolled": 0, "narrowed": 0, "blades": 0, "unresolved": 0,
            "core_vs_below": round(max([_depth(CORE_RECS[kind], q) for q in below] + [0.0]), 3)}
    rows_done = []
    for ri, row in enumerate(R["rows"]):
        recA = [r for rr in rows_done for r in rr]
        recB = []
        rows_done.append(recB)
        step = 360.0 / row["n"]
        move = {"lift": 1.0, "sink": -1.0}.get(row["fix"], 0.0)
        for k in range(row["n"]):
            az0 = row["az0"] + k * step
            az = az0 + rng.uniform(-4, 4)
            r1 = row["r1"] * rng.uniform(0.95, 1.05)
            z1 = row["z1"] + rng.uniform(-0.15, 0.15)
            if row["front"] is not None and abs((az0 - 270.0 + 180) % 360 - 180) < 1:
                az = 270.0 + rng.uniform(-1.5, 1.5)
                z1 = row["front"] + rng.uniform(-0.04, 0.04)
            w = row["w"] * rng.uniform(0.92, 1.08)
            roll0 = row["roll"]
            sgn = -1.0 if move > 0 else 1.0
            roll = roll0 + rng.uniform(-4, 4)
            z0 = row["z0"]
            tone = 1.0 + rng.uniform(-0.04, 0.04)
            dz1 = 0.0
            for attempt in range(40):
                vs, fs = blade(a, az, row["r0"], z0, r1, z1 + dz1, w, row["droop"], sgn * roll, row["tones"], tone,
                               row.get("sa", SA), row.get("ridge", RIDGE), row.get("bend"))
                rec = _rec_of(vs)
                dA = max([_depth(rec, q, core) for q in recA] + [0.0])
                dB = max([_depth(rec, q, core) for q in recB] + [0.0])
                dL = max([_depth(rec, q) for q in below] + [0.0])
                dC = _depth(rec, below_core) if below_core else 0.0
                if (dA <= CUT and dB <= CUT and dL <= CUT and dC <= CUT) or attempt == 39:
                    if attempt == 39:
                        info["unresolved"] += 1
                    break
                bmesh.ops.delete(a.bm, geom=vs, context="VERTS")
                # roots stay where they are (buried in the core): only the tip turns about the root
                if (dL > CUT or dC > CUT) and dz1 < 0.9:
                    dz1 += 0.06               # rests on the ring below: tip it up about its buried root
                    info["lifted"] += 1
                elif move and dA > CUT and abs(dz1) < 0.9:
                    dz1 += 0.06 * move        # a lift row rests on the outer row (a sink row tucks under it)
                    info["lifted"] += 1
                elif roll < roll0 + 12:
                    roll += 3.0
                    info["rolled"] += 1
                else:
                    w *= 0.96
                    info["narrowed"] += 1
            info.setdefault("depth", []).append(round(max(dA, dB, dL), 3))
            info.setdefault("final", []).append((ri, round(sgn * roll), round(w / row["w"], 2), round(dz1, 2),
                                                 round(z0 - row["z0"], 2)))
            _mottle(a, fs, 0.03, 0.6, R["seed"] + 17 * k + 101 * ri)
            recB.append(rec)
            out += vs
            info["blades"] += 1
    RING_INFO[kind] = info
    RING_RECS[kind] = [r for rr in rows_done for r in rr]
    return out


def t3_part(a):
    ring(a, "crown")


def t2_part(a):
    ring(a, "t2")


def t1u_part(a):
    ring(a, "t1u")


def t1l_part(a):
    ring(a, "t1l")


# ---- trunk (spec 2.4): one lofted closed shell ------------------------------------------------------------------------
# root-region rings (z, trunk corner radius between the roots); then 16-vertex planked rings (z, corner radius)
ROOT_Z = ((0.05, 3.13), (0.95, 2.74), (1.65, 2.42), (2.50, 2.22), (3.40, 2.10), (4.40, 1.99))
BODY_Z = ((5.40, 1.93), (7.00, 1.85), (8.80, 1.74), (TRUNK_RIM, 1.58))
# roots: name, azimuth, reach (r of the tip), base width at the trunk, rib top z, kink (deg at the tip)
ROOTS = (("RF", 268.0, 4.1, 1.6, 4.0, 4.0), ("RFR", 292.0, 5.2, 1.5, 3.8, -5.0), ("RR", 318.0, 6.5, 1.7, 4.4, 7.0),
         ("RB1", 70.0, 4.6, 1.4, 3.4, -4.0), ("RB2", 128.0, 5.0, 1.4, 3.5, 5.0), ("RL", 176.0, 4.3, 1.5, 3.8, -6.0),
         ("RFL", 238.0, 4.4, 1.4, 3.6, 5.0))
RECESS_C, RECESS_Z = 1.00, 10.65           # recess mouth corner radius, floor z
PEG_LEAN = 0.05                            # the peg top leans toward +X
GROOVES = (0.0, 135.0, 225.0)              # plank splits pushed in (vertical grooves), azimuths
KNOT = (315.0, 1)                          # knot slit: split-face azimuth, body band (5.4 -> 7.0)


def _root_ring(i, z, rt, rng_k):
    """Points of root-region ring i: per gap valley points on the trunk circle, per root flankL / crestL / crestR /
    flankR. Returns [(point, tag)] sorted by angle."""
    pts = []
    roots = sorted(ROOTS, key=lambda r: r[1])
    n = len(roots)
    for j, (name, az, reach, w, rib, kink) in enumerate(roots):
        # crest radius / half-width and flank half-width per ring (ground tip -> blunt end -> buttress -> trunk)
        span = reach - rt
        ribf = max(0.0, min(1.0, (rib - z) / max(rib - 0.95, 0.1)))
        crest_r = [reach, reach - 0.45, rt + 0.50 * span, rt + 0.24 * span * (0.6 + 0.4 * ribf),
                   rt + 0.45 * ribf + 0.12, rt + 0.10][i]
        hc = [0.36, 0.58, 0.64, 0.58, 0.46, 0.32][i] * w / 1.5
        hf = [0.85, 0.88, 0.85, 0.76, 0.64, 0.45][i] * w / 1.5
        k_az = az + kink * [1.0, 0.9, 0.4, 0.1, 0.0, 0.0][i]
        rf = rt
        # flanks never reach past 0.4 of the gap to either neighbour (close roots would overlap and self-intersect)
        g_min = min((az - roots[j - 1][1]) % 360.0, (roots[(j + 1) % n][1] - az) % 360.0)
        fa = min(math.degrees(math.asin(min(0.95, hf / rf))), 0.4 * g_min)
        ca = min(math.degrees(math.asin(min(0.95, hc / crest_r))), 0.7 * fa)
        pts.append((_u(az - fa) * rf, "flank"))
        pts.append((_u(k_az - ca) * crest_r, "crest"))
        pts.append((_u(k_az + ca) * crest_r, "crest"))
        pts.append((_u(az + fa) * rf, "flank"))
        # valleys in the gap to the next root (one per ~30 deg)
        nxt = roots[(j + 1) % n][1] + (360.0 if j == n - 1 else 0.0)
        gap = nxt - az
        nv = max(1, int(round(gap / 30.0)))
        for v in range(nv):
            va = az + gap * (v + 1) / (nv + 1)
            pts.append((_u(va) * rt * 0.98, "valley"))
    return [(p + Vector((0, 0, z)), t) for p, t in pts]


def trunk(a):
    """The trunk, roots, rim, recess and peg as one closed lofted shell (decision 7: the roots are part of the trunk
    mesh). Bark base; the lowest band 25 % deep; grooves and the knot deep; the peg's cut top light with a dark pith."""
    bm = a.bm
    rng = random.Random(49500)
    rings, tags = [], []
    for i, (z, rt) in enumerate(ROOT_Z):
        pts = _root_ring(i, z, rt, rng)
        rings.append([bm.verts.new(p) for p, _ in pts])
        tags.append([t for _, t in pts])
    body = []
    for bi, (z, rc) in enumerate(BODY_Z):
        apo = rc * COS8
        r = []
        for k in range(16):
            ang = 22.5 + 22.5 * k
            if k % 2 == 0:
                rad = rc * (1 + (rng.uniform(-0.02, 0.02) if bi < len(BODY_Z) - 1 else 0.0))
            else:
                groove = any(abs((ang - g + 180) % 360 - 180) < 1 for g in GROOVES)
                rad = apo - 0.10 if groove else apo + (rng.uniform(0.06, 0.10) if bi < len(BODY_Z) - 1 else 0.02)
            r.append(bm.verts.new(_u(ang) * rad + Vector((0, 0, z))))
        body.append(r)
    side = []
    root_bands = []
    for i in range(len(rings) - 1):
        fb = _band(bm, rings[i], rings[i + 1])
        root_bands.append(fb)
        side += fb
    zipf = _zip(bm, rings[-1], body[0])
    side += zipf
    body_bands = []
    for i in range(len(body) - 1):
        fb = _band(bm, body[i], body[i + 1])
        body_bands.append(fb)
        side += fb
    bottom = bm.faces.new(list(reversed(rings[0])))
    # top: rim annulus, recess walls and floor, peg, cut top with the pith
    mo = _srt(_ring(bm, 8, RECESS_C, TRUNK_RIM, 22.5))
    fl = _srt(_ring(bm, 8, RECESS_C, RECESS_Z, 22.5))
    pc = PEG_APO / COS8
    pb = _srt(_ring(bm, 8, pc, RECESS_Z, 22.5))
    pt = _srt(_ring(bm, 8, pc, TRUNK_PEG_TOP, 22.5, (PEG_LEAN, 0.0)))
    pith = _srt(_ring(bm, 8, 0.13, TRUNK_PEG_TOP, 22.5, (PEG_LEAN, 0.0)))
    rim_f = _zip(bm, _srt(body[-1]), mo)
    rec_f = _band(bm, mo, fl) + _band(bm, fl, pb)
    peg_f = _band(bm, pb, pt)
    cut_f = _band(bm, pt, pith)
    pith_f = [bm.faces.new(list(pith))]
    vs = [v for r in rings for v in r] + [v for r in body for v in r] + mo + fl + pb + pt + pith
    allf = side + [bottom] + rim_f + rec_f + peg_f + cut_f + pith_f
    bmesh.ops.recalc_face_normals(bm, faces=allf)
    a._finish(vs, BARK, tint=1.0)
    # position and role only: the ground band and the root ends deeper; the bottom (in the sand) keeps the ground band's
    # colour (not a facing rule); grooves and the recess deep; the peg's cut top light, the pith deep
    _paint(a, root_bands[0] + [bottom], _mix(BARK, BARK_DEEP, 0.25))
    _paint(a, rec_f, _mix(BARK, BARK_DEEP, 0.5))
    _paint(a, cut_f, BARK_LIGHT)
    _paint(a, pith_f, BARK_DEEP)
    for fb in body_bands:
        for k, f in enumerate(fb):
            ang = 22.5 + 22.5 * k + 11.25
            near = [abs((ang - 11.25 - g + 180) % 360 - 180) < 1 or abs((ang + 11.25 - g + 180) % 360 - 180) < 1
                    for g in GROOVES]
            if any(near):
                _paint(a, [f], _mix(BARK, BARK_DEEP, 0.25))
    # plank columns: one tone per column (whole facets), broad mottle on top
    for fb in body_bands:
        for k, f in enumerate(fb):
            _tint(a, [f], 1.0 + 0.04 * math.sin(k * 2.1 + 0.7))
    _mottle(a, side, 0.04, 0.35, 49510)
    # knot slit: the half-facet next to the split at KNOT's azimuth, inset and pressed in
    k = int(round((KNOT[0] - 22.5) / 22.5)) % 16
    f = body_bands[KNOT[1]][k]
    res = bmesh.ops.inset_individual(bm, faces=[f], thickness=0.16, depth=-0.08, use_even_offset=True)
    _paint(a, [f], BARK_DEEP)
    _paint(a, res["faces"], _mix(BARK, BARK_DEEP, 0.5))
    vs += [v for v in f.verts if v not in vs]
    bmesh.ops.triangulate(bm, faces=[f for f in _faces(vs) if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    return vs


def trunk_part(a):
    trunk(a)


def _root_segments():
    """Plan segments (start, end, half-width) of every root, for keeping dressing clear."""
    out = []
    for name, az, reach, w, rib, kink in ROOTS:
        tip = _u(az + kink) * reach
        out.append((_u(az).to_2d() * 2.0, tip.to_2d(), 0.5 * w))
    return out


# ---- ground: patch, rocks, pebbles, bushes, clusters, sprigs (spec 2.4) -----------------------------------------------
PATCH_TOP, PATCH_EDGE, BEVEL = 0.15, 0.0, 0.6
ROCKS = {   # name -> centre, (W, D, H), yaw (deg), top slope, seed
    # fix round 1 (verifier minor 4): R1, R4 and R5 pushed out so rock shows past the skirt from above
    "R1": ((-7.2, -1.0), (3.6, 2.9, 2.4), 20.0, 0.12, 49601),
    "R2": ((-0.9, -6.2), (3.8, 3.1, 2.5), -15.0, 0.12, 49602),
    "R3": ((2.6, 5.2), (2.7, 2.2, 1.8), 35.0, 0.10, 49603),
    "R4": ((9.1, 3.7), (2.4, 2.0, 1.6), 10.0, 0.10, 49604),
    "R5": ((-8.4, 3.9), (1.8, 1.5, 1.1), -30.0, 0.10, 49605),
}
PEBBLES = {"P1": ((-3.4, -6.3), 0.55, 49611), "P2": ((2.4, -6.4), 0.45, 49612), "P3": ((-8.2, 1.2), 0.5, 49613)}
# rock ring stacks (height fraction, radius fraction, points): a broad flat base, widest low, a shoulder, a flat
# sloping 5-corner crown: chunky blocks, never eggs (W : H 1.3-1.6)
ROCK_RINGS = ((0.0, 0.88, 5), (0.28, 1.0, 6), (0.72, 0.9, 5), (1.0, 0.62, 4))
SINK_ROCK, SINK_PEBBLE, SINK_HUB, SINK_LOBE = 0.08, 0.04, 0.03, 0.05
# bushes: centre, lobes [(dx, dy, base z, radius, height)], seed. Faceted gem-like lobes overlapping 0.1-0.3.
BUSHES = {
    "BA": ((5.0, -0.6), [(0.0, 0.0, 1.25, 1.25, 3.10), (-0.90, -0.20, 0.0, 1.10, 2.40), (1.00, -0.70, 0.0, 1.05, 2.25),
                         (0.80, 1.00, 0.0, 1.05, 2.45), (-0.90, 0.90, 0.0, 1.00, 2.05), (0.10, -1.30, 0.0, 0.90, 1.70)],
           49701),
    "BB": ((8.0, 0.1), [(0.0, 0.0, 0.95, 1.10, 2.55), (-0.85, -0.60, 0.0, 1.00, 1.95), (0.85, -0.55, 0.0, 0.95, 1.80),
                        (0.35, 0.95, 0.0, 1.00, 2.00), (-0.65, 0.85, 0.0, 0.85, 1.50)], 49702),
}
LOBE_TRIS = 20
# clusters: centre, diameter, height, (outer, inner) leaves, seed. Sprigs: centre, diameter, height, leaves, seed.
CLUSTERS = {
    "C1": ((-4.2, 1.4), 2.6, 4.0, (5, 2), 49801),
    "C2": ((-8.0, -3.5), 2.0, 2.8, (4, 2), 49802),
    "C3": ((-3.3, -4.4), 1.6, 2.2, (4, 1), 49803),
    "C4": ((3.4, -4.8), 1.6, 1.9, (4, 1), 49804),
    "C5": ((-1.8, 5.7), 2.0, 2.6, (4, 1), 49805),
    "C6": ((5.7, 4.6), 1.8, 2.2, (4, 1), 49806),
}
SPRIGS = {"S1": ((2.0, -6.7), 0.9, 1.2, 3, 49811), "S2": ((-5.4, -4.6), 0.9, 1.2, 3, 49812)}
LEAF_LW, LEAF_FOLD, LEAF_TRIS = 1.75, 18.0, 10


def _items():
    """(centre, footprint radius) of everything on the patch, for the patch outline and the sand's deeper band."""
    out = [(Vector(c), max(s[0], s[1]) / 2) for c, s, *_ in ROCKS.values()]
    out += [(Vector(c), r) for c, r, _ in PEBBLES.values()]
    for c, lobes, _ in BUSHES.values():
        out += [(Vector(c) + Vector((dx, dy)), r) for dx, dy, _, r, _ in lobes]
    out += [(Vector(c), 0.5 * D) for c, D, *_ in CLUSTERS.values()]
    out += [(Vector(c), 0.5 * D) for c, D, *_ in SPRIGS.values()]
    for p0, p1, hw in _root_segments():
        out.append((p1, 0.4))
    return out


def _patch_outline(n=14):
    """Lobed outline (r per azimuth): an ellipse 8.6 x 7.0 with lobes, let out wherever an item needs 0.3 of sand
    beyond its footprint."""
    rng = random.Random(49600)
    ph = [rng.uniform(0, 6.28) for _ in range(3)]
    items = _items()
    out = []
    for k in range(n):
        th = 2 * math.pi * k / n
        r = 1.0 / math.sqrt((math.cos(th) / 8.6) ** 2 + (math.sin(th) / 7.0) ** 2)
        r *= 1.0 + 0.05 * math.sin(3 * th + ph[0]) + 0.035 * math.sin(5 * th + ph[1])
        for c, rad in items:
            dist = c.length
            ang = math.atan2(c.y, c.x)
            dth = abs((th - ang + math.pi) % (2 * math.pi) - math.pi)
            half = math.asin(min(1.0, (rad + 0.3) / max(dist, 1e-3)))
            if dth < half + 2 * math.pi / n:
                r = max(r, dist * math.cos(dth) + math.sqrt(max(0.0, (rad + 0.3) ** 2 - (dist * math.sin(dth)) ** 2)))
        out.append(r)
    return out


_OUTLINE = []


def _patch_z(x, y):
    """Height of the sand patch's top at (x, y): the crest, or the bevel falling to PATCH_EDGE at the outline."""
    if not _OUTLINE:
        _OUTLINE[:] = _patch_outline()
    R = _OUTLINE
    n = len(R)
    th = math.atan2(y, x) % (2 * math.pi)
    k = int(th / (2 * math.pi / n)) % n
    j = (k + 1) % n
    a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
    p0 = Vector((math.cos(a0) * R[k], math.sin(a0) * R[k]))
    p1 = Vector((math.cos(a1) * R[j], math.sin(a1) * R[j]))
    d = Vector((math.cos(th), math.sin(th)))
    e = p1 - p0
    den = d.x * e.y - d.y * e.x
    re = (p0.x * e.y - p0.y * e.x) / den if abs(den) > 1e-9 else R[k]
    r = math.hypot(x, y)
    if r <= re - BEVEL:
        return PATCH_TOP
    return PATCH_EDGE + (PATCH_TOP - PATCH_EDGE) * max(0.0, (re - r) / BEVEL)


def _near_field():
    segs = _root_segments()
    circles = [(Vector((0, 0)), 2.6)] + [(Vector(c), max(s[0], s[1]) / 2) for c, s, *_ in ROCKS.values()]
    circles += [(Vector(c), r) for c, r, _ in PEBBLES.values()]
    circles += [(Vector(c), 0.3) for c, *_ in CLUSTERS.values()] + [(Vector(c), 0.2) for c, *_ in SPRIGS.values()]
    for c, lobes, _ in BUSHES.values():
        circles += [(Vector(c) + Vector((dx, dy)), r * 0.8) for dx, dy, _, r, _ in lobes]

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
    """The thin lobed sand patch: a flat crest at 0.15, a bevel 0.6 wide down to the outline at z 0 (no side wall: a
    0.04 wall gave sliver triangles), a flat underside at z 0. Deeper sand within 0.4 of the trunk, roots, rocks, lobes and hubs and on the bevel."""
    bm = a.bm
    _OUTLINE[:] = _patch_outline()
    R = _OUTLINE
    n = len(R)

    def ring(f_r, z, dr=0.0):
        return [bm.verts.new(_u(360.0 * k / n) * (R[k] * f_r + dr) + Vector((0, 0, z))) for k in range(n)]
    c_top = bm.verts.new(Vector((0, 0, PATCH_TOP)))
    r2 = ring(1.0, PATCH_TOP, -BEVEL)
    r4 = ring(1.0, 0.0)
    c_bot = bm.verts.new(Vector((0, 0, 0)))
    fs = [bm.faces.new((r2[k], r2[(k + 1) % n], c_top)) for k in range(n)]
    for A, B in ((r2, r4),):
        for k in range(n):
            j = (k + 1) % n
            fs.append(bm.faces.new((A[k], B[k], B[j], A[j])))
    fs += [bm.faces.new((r4[(k + 1) % n], r4[k], c_bot)) for k in range(n)]
    bmesh.ops.triangulate(bm, faces=fs, quad_method="BEAUTY")
    vs = [c_top, c_bot] + r2 + r4
    allf = _faces(vs)
    bmesh.ops.recalc_face_normals(bm, faces=allf)
    a._finish(vs, SAND, tint=1.0)
    near = _near_field()
    for f in allf:
        c = f.calc_center_median()
        if c.z < PATCH_TOP - 1e-3:
            f.material_index = a._mi(_mix(SAND, SAND_DEEP, 0.5))
        elif near(c) < 0.4:
            f.material_index = a._mi(_mix(SAND, SAND_DEEP, 0.25))
    _mottle(a, allf, 0.03, 0.15, 49620)
    return vs


def rock(a, name, z0=None):
    """A chunky faceted rock: the hull of jittered ring stacks (a broad flat base sunk 0.08 into the sand, widest low, a
    shoulder, a flat crown sloping down to one side). rock base; rock_light on the top, rock_deep on the lowest 25 %."""
    (cx, cy), (W, D, H), yaw, slope, seed = ROCKS[name]
    if z0 is None:
        z0 = _patch_z(cx, cy) - SINK_ROCK
    rng = random.Random(seed)
    pts = []
    for h, rf, n in ROCK_RINGS:
        off = rng.uniform(0, 2 * math.pi)
        for k in range(n):
            th = off + 2 * math.pi * k / n + rng.uniform(-0.25, 0.25) * (2 * math.pi / n)
            r = rf * (1 + rng.uniform(-0.07, 0.07))
            x, y = math.cos(th) * W / 2 * r, math.sin(th) * D / 2 * r
            z = h * H * (1 + (rng.uniform(-0.06, 0.06) if 0 < h < 1 else 0))
            if h >= 0.7:
                z -= slope * H * (x / (W / 2)) * h
            pts.append(Vector((x, y, max(0.0, z))))
    m = Matrix.Rotation(math.radians(yaw), 3, "Z")
    pts = [m @ p + Vector((cx, cy, z0)) for p in pts]
    vs = m033._hull(a, pts, ROCK)
    fs = _faces(vs)
    for f in fs:
        hgt = (f.calc_center_median().z - z0) / H
        if hgt > 0.78:
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.5))
        elif hgt > 0.62:
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.25))
        elif hgt < 0.25:
            f.material_index = a._mi(_mix(ROCK, ROCK_DEEP, 0.25))
    _mottle(a, fs, 0.04, 0.4, seed)
    return vs


def pebble(a, name):
    (cx, cy), s, seed = PEBBLES[name]
    rng = random.Random(seed)
    z0 = _patch_z(cx, cy) - SINK_PEBBLE
    pts = [Vector((cx + math.cos(t) * s * rng.uniform(0.85, 1.0), cy + math.sin(t) * s * 0.8 * rng.uniform(0.85, 1.0),
                   z0)) for t in (rng.uniform(0, 0.5) + 2 * math.pi * k / 4 for k in range(4))]
    pts += [Vector((cx + rng.uniform(-0.15, 0.15) * s, cy + rng.uniform(-0.15, 0.15) * s, z0 + 0.65 * s))]
    pts += [Vector((cx + rng.uniform(0.2, 0.4) * s, cy + rng.uniform(-0.3, 0.3) * s, z0 + 0.45 * s))]
    vs = m033._hull(a, pts, _mix(ROCK, ROCK_DEEP, 0.25))
    return vs


def lobe(a, c, rad, hgt, seed, key):
    """One faceted bush lobe: the hull of a flat bottom ring (4), a widest ring (5) at 0.38 h and a 3-corner top: a
    gem-like mound with big flat facets (not a smooth ball)."""
    rng = random.Random(seed)
    o = rng.uniform(0, 6.28)
    pts = []
    for h, rf, n in ((0.0, 0.72, 4), (0.42, 1.0, 5), (0.88, 0.62, 3)):
        oo = o + rng.uniform(0, 1.2)
        for k in range(n):
            th = oo + 2 * math.pi * k / n + rng.uniform(-0.2, 0.2)
            r = rf * rad * rng.uniform(0.9, 1.08) if n > 1 else rf * rad
            pts.append(Vector((c.x + math.cos(th) * r, c.y + math.sin(th) * r, c.z + h * hgt * rng.uniform(0.94, 1.0)
                               if 0 < h < 1 else c.z + h * hgt)))
    return m033._hull(a, pts, key)


BUSH_INFO = {}


def bush(a, name):
    """A faceted bush mound: lobes overlapping 0.1-0.3 so every lobe chains to the patch. Colour per lobe by position:
    the top lobe lime (bush), the outer low lobes a mix by height, never per facet by facing."""
    (cx, cy), lobes, seed = BUSHES[name]
    out = []
    zt = max(bz + h for _, _, bz, _, h in lobes)
    for i, (dx, dy, bz, r, h) in enumerate(lobes):
        x, y = cx + dx, cy + dy
        z0 = _patch_z(x, y) - SINK_LOBE + bz
        top = (bz + h) / zt
        key = BUSH if top > 0.9 else _mix(BUSH_DEEP, BUSH, 0.5) if top > 0.65 else _mix(BUSH_DEEP, BUSH, 0.25)
        vs = lobe(a, Vector((x, y, z0)), r, h, seed + 11 * i, key)
        fs = _faces(vs)
        for f in fs:      # the lowest band of each lobe a step deeper (by height in the mound, not facing)
            if f.calc_center_median().z - z0 < 0.25 * h:
                f.material_index = a._mi(_mix(BUSH_DEEP, BUSH, 0.25) if key == BUSH else BUSH_DEEP)
        _tint(a, fs, 1.0 + random.Random(seed + i).uniform(-0.04, 0.04))
        out += vs
    BUSH_INFO[name] = {"lobes": len(lobes), "top": round(zt, 2)}
    return out


def _leaf(a, base, yaw, pitch, L, W, curl, fold, key):
    """One closed 10-tri broad leaf with a blunt oval tip: outline base, widest (W) at 0.45 L, a blunt end 0.34 W wide
    at L; folded on its midrib (a V channel), a top midrib point and a keel under it, arching out by curl * L at the
    tip."""
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
    outline = [(0.0, 0.0), (0.5 * L, W / 2), (L, 0.24 * W), (L, -0.24 * W), (0.5 * L, -W / 2)]
    ov = [bm.verts.new(P(x, y, 0.0)) for x, y in outline]
    m = bm.verts.new(P(0.5 * L, 0.0, 0.03))
    k = bm.verts.new(P(0.5 * L, 0.0, -0.05))
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
    ring = [bm.verts.new(Vector((cx + math.cos(yaw0 + 2 * math.pi * k / 4) * hr,
                                 cy + math.sin(yaw0 + 2 * math.pi * k / 4) * hr, z0))) for k in range(4)]
    apex = bm.verts.new(Vector((cx, cy, z0 + hh)))
    fs = [bm.faces.new((ring[k], ring[(k + 1) % 4], apex)) for k in range(4)]
    fs.append(bm.faces.new(list(reversed(ring))))
    bmesh.ops.triangulate(bm, faces=[fs[-1]])
    vs = ring + [apex]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, _mix(PLANT_DEEP, BARK_DEEP, 0.25), tint=1.0)
    return vs, z0


LEAF_INFO = {}


def _place_leaf(a, base_xy, z0, yaw, pitch, L, curl, key, obstacles, info):
    for dyaw, f_l in ((0, 1.0), (0.22, 1.0), (-0.22, 1.0), (0.45, 1.0), (-0.45, 1.0), (0, 0.8), (0.3, 0.75),
                      (-0.3, 0.75), (0, 0.6), (0.6, 0.6), (-0.6, 0.6)):
        y2 = yaw + dyaw
        base = (base_xy[0] + math.cos(y2) * 0.06, base_xy[1] + math.sin(y2) * 0.06, z0)
        vs, fs = _leaf(a, base, y2, pitch, L * f_l, L * f_l / LEAF_LW, curl, math.radians(LEAF_FOLD), key)
        if obstacles is None or not _hits(vs, *obstacles):
            if dyaw:
                info["turned"] += 1
            if f_l < 1:
                info["shortened"] += 1
            return vs, fs, base
        bmesh.ops.delete(a.bm, geom=vs, context="VERTS")
    info["dropped"] += 1
    return None


def cluster(a, name, obstacles=None):
    """An upright fan of broad blunt-tipped leaves round a small closed hub sunk 0.03 into the sand: an outer ring
    pitched 60-70 deg arching out at the tips, an inner ring 75-85 deg. Roles: outer leaves lime (plant), inner leaves
    green (plant_deep); each leaf's base faces a step deeper."""
    (cx, cy), D, H, (n_out, n_in), seed = CLUSTERS[name]
    rng = random.Random(seed)
    hvs, z0 = _hub(a, cx, cy, 0.24 if D > 2 else 0.18, 0.28, seed)
    out = list(hvs)
    info = LEAF_INFO.setdefault(name, {"turned": 0, "shortened": 0, "dropped": 0, "leaves": 0})
    yaw0 = rng.uniform(0, 6.28)
    specs = []
    for k in range(n_out):
        yaw = yaw0 + 2 * math.pi * k / n_out + rng.uniform(-0.2, 0.2)
        pitch = math.radians(rng.uniform(60, 70))
        curl = rng.uniform(0.16, 0.24)
        L = (H - 0.2) / (math.sin(pitch) - curl * math.cos(pitch)) * rng.uniform(0.85, 0.95)
        specs.append((yaw, pitch, L, PLANT if k % 3 != 2 else PLANT_DEEP, curl))
    for k in range(n_in):
        yaw = yaw0 + math.pi / n_out + 2 * math.pi * k / n_in + rng.uniform(-0.25, 0.25)
        pitch = math.radians(rng.uniform(75, 85))
        L = (H - 0.25) / math.sin(pitch) * rng.uniform(0.95, 1.02)
        specs.append((yaw, pitch, L, PLANT_DEEP if k % 2 == 0 else PLANT, rng.uniform(0.06, 0.1)))
    for yaw, pitch, L, key, curl in specs:
        got = _place_leaf(a, (cx, cy), z0 + 0.1, yaw, pitch, L, curl, key, obstacles, info)
        if got is None:
            continue
        vs, fs, base = got
        deeper = _mix(PLANT, PLANT_DEEP, 0.5) if key == PLANT else _mix(PLANT_DEEP, BARK_DEEP, 0.25)
        _paint(a, [f for f in fs if any((v.co - Vector(base)).length < 1e-6 for v in f.verts)], deeper)
        _tint(a, fs, 1.0 + rng.uniform(-0.04, 0.04))
        out += vs
        info["leaves"] += 1
    return out


def sprig(a, name, obstacles=None):
    """A small sprig: 4 lime leaves (one green) round a small hub."""
    (cx, cy), D, H, n, seed = SPRIGS[name]
    rng = random.Random(seed)
    hvs, z0 = _hub(a, cx, cy, 0.13, 0.18, seed)
    out = list(hvs)
    info = LEAF_INFO.setdefault(name, {"turned": 0, "shortened": 0, "dropped": 0, "leaves": 0})
    yaw0 = rng.uniform(0, 6.28)
    for k in range(n):
        yaw = yaw0 + 2 * math.pi * k / n + rng.uniform(-0.2, 0.2)
        pitch = math.radians(rng.uniform(55, 70))
        L = H / math.sin(pitch) * rng.uniform(0.95, 1.08)
        key = PLANT_DEEP if k == 1 else PLANT
        got = _place_leaf(a, (cx, cy), z0 + 0.07, yaw, pitch, L, 0.08, key, obstacles, info)
        if got is None:
            continue
        vs, fs, base = got
        _tint(a, fs, 1.0 + rng.uniform(-0.04, 0.04))
        out += vs
        info["leaves"] += 1
    return out


def _obstacles(extra=None):
    """(coords, polys) of the rocks and a probe build of the trunk (faces wholly at or below the sand's crest dropped:
    the hubs sit in the sand)."""
    probe = K.fk().Asset("_probe_obs", "probe")
    trunk(probe)
    for name in ROCKS:
        rock(probe, name)
    if extra:
        extra(probe)
    coords, polys = [], []
    bm = probe.bm
    bm.verts.ensure_lookup_table()
    idx = {v: i for i, v in enumerate(bm.verts)}
    coords = [v.co.copy() for v in bm.verts]
    polys = [[idx[v] for v in f.verts] for f in bm.faces]
    probe.bm.free()
    return coords, [p for p in polys if not all(coords[i].z < PATCH_TOP + 1e-4 for i in p)]


def ground(a):
    """Patch, rocks, pebbles, bushes, then the leaf clusters and sprigs (avoiding the rocks, trunk, roots and lobes)."""
    patch(a)
    for name in ROCKS:
        rock(a, name)
    for name in PEBBLES:
        pebble(a, name)
    for name in BUSHES:
        bush(a, name)
    obs = _obstacles()
    for name in CLUSTERS:
        cluster(a, name, obs)
    for name in SPRIGS:
        sprig(a, name, obs)


def foot_part(a):
    ground(a)


def hero_all(a):
    """Everything: ground, trunk, then the four rings bottom up."""
    ground(a)
    trunk(a)
    ring(a, "t1l")
    ring(a, "t1u")
    ring(a, "t2")
    ring(a, "crown")


# ---- objects ---------------------------------------------------------------------------------------------------------
NOTES = {
    HERO: "Classic Pine (TallPine): four canopy rings of long parallel-sided blades with truncated tips (crown star cone "
          "+ 10, Tier 2 10 + 10, Tier 1 upper 12 + 11, Tier 1 lower 14 + 13, inner rows on top) stacked by peg and hex "
          "sleeve on a thick planked trunk with seven buttress roots built into its foot, on a sand patch with 5 rocks, "
          "3 pebbles, 2 faceted bush mounds, 6 broad-leaf clusters and 2 sprigs. No VFX",
    T3_P: "Canopy Tier 3: five-ridge star cone with a hem of 10 blades, hex sleeve with a blind hole underneath",
    T2_P: "Canopy Tier 2: core with a hex sleeve (blind hole) and a top peg, 10 + 10 blades in two rows",
    T1U_P: "Canopy Tier 1 (upper piece): core with a hex sleeve (blind hole) and a top peg, 12 + 11 blades",
    T1L_P: "Canopy Tier 1 (lower piece): the widest ring, core with a hex sleeve and a top peg, 14 + 13 blades",
    TRUNK_P: "Trunk: octagonal planked trunk with grooves and a knot slit, seven buttress roots built into its foot, a "
             "thick rim round a dished recess and an octagonal peg (canopy rings stack and rotate)",
    FOOT_P: "Root Foot: sand patch, 5 chunky warm grey rocks, 3 pebbles, 2 faceted bush mounds, 6 upright broad-leaf "
            "clusters and 2 sprigs",
}
COLLISION = {HERO: "precise", T3_P: "hull", T2_P: "hull", T1U_P: "hull", T1L_P: "hull", TRUNK_P: "hull",
             FOOT_P: "precise"}


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


def _make(name, fn, role="part", budget=1000):
    t0 = time.time()
    o = _new(name, fn, role, budget)
    lg = _post(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


# ---- checks ----------------------------------------------------------------------------------------------------------
def _keys(o):
    return [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]


def _kind(ks, nf):
    if any("bush" in k for k in ks):
        return "lobe"
    if any("plant" in k for k in ks):
        return "leaf" if nf == LEAF_TRIS else "hub"
    if any("bark" in k for k in ks) and any("needle" in k for k in ks):
        return "core"
    if any("bark" in k for k in ks):
        return "trunk"
    if any("needle" in k for k in ks):
        return "blade"
    if any("sand" in k for k in ks):
        return "patch"
    if any("rock" in k for k in ks):
        return "pebble" if nf <= 10 else "rock"
    return "other"


def _winding(es):
    """Manifold edges whose two faces walk them the same way (faces wound against their neighbours)."""
    bad = 0
    for e in es:
        if len(e.link_faces) == 2:
            dirs = []
            for f in e.link_faces:
                vv = list(f.verts)
                i = vv.index(e.verts[0])
                dirs.append(vv[(i + 1) % len(vv)] == e.verts[1])
            bad += dirs[0] == dirs[1]
    return bad


def shells_report(o):
    """Per shell: kind, tris, non-manifold edges and verts, boundary edges, self-intersecting face pairs inside the
    shell, winding errors, signed volume (closed and outward when > 0)."""
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
        xs = [v.co.x for v in vs]
        ys = [v.co.y for v in vs]
        out.append({"kind": _kind(ks, len(fs)), "tris": len(fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary), "self_hits": hits, "winding": _winding(es),
                    "volume": round(vol, 4), "zmin": round(min(v.co.z for v in vs), 3),
                    "zmax": round(max(v.co.z for v in vs), 3),
                    "size": [round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2)]})
    bm.free()
    return out


DRESSING = ("leaf", "hub", "lobe", "pebble")


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating dressing (STAGES): per shell, whether it touches another shell (triangles intersect, or a vertex
    within `tol` of another shell's surface) or the ground (z <= tol). Anchors: shells on the ground; for a ring alone,
    its core. Returns the floating count, the worst gap, shells with no chain of contact to an anchor, core seat gaps,
    blade pairs that cut into each other (crossing points outside every core) more than CUT, leaves that cross a rock
    or the trunk, and dressing buried in rock / trunk deeper than BURY (ray parity against the full shells)."""
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
    if any(kinds[k] in ("patch", "trunk") for k in range(n)) or all(kinds[k] in DRESSING + ("rock",) for k in range(n)):
        ground = {k for k in range(n) if zmin[k] - z0 <= tol}
        if not any(kinds[k] == "patch" for k in range(n)):
            ground |= {k for k in range(n) if kinds[k] == "trunk"}
    else:
        ground = {k for k in range(n) if kinds[k] == "core"}
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
    cut_pairs, depths = set(), {}
    for kp in pairs:
        if kinds[kp[0]] == "blade" and kinds[kp[1]] == "blade":
            depths[kp] = _depth(rec(kp[0]), rec(kp[1]), core_tree)
            if depths[kp] > CUT:
                cut_pairs.add(kp)
    leaf_cuts = set()
    for i, j in overl:
        a_, b_ = fsh[i], fsh[j]
        if a_ == b_:
            continue
        kp = (min(a_, b_), max(a_, b_))
        ka = {kinds[a_], kinds[b_]}
        if "leaf" in ka and ka & {"rock", "trunk", "lobe"} and kp not in leaf_cuts:
            if _cut_pts([v.co for v in bm.faces[i].verts], [v.co for v in bm.faces[j].verts]):
                leaf_cuts.add(kp)
    # dressing buried in rock / trunk (ray parity against the whole solid shells)
    solid = [k for k in range(n) if kinds[k] in ("rock", "trunk")]
    bury = 0.0
    buried = []
    for kp in pairs:
        a_, b_ = kp
        for d_, s_ in ((a_, b_), (b_, a_)):
            if kinds[d_] in DRESSING and s_ in solid:
                R_ = rec(s_)
                dd = max((R_["tree"].find_nearest(p)[3] for p in rec(d_)["smp"] if _inside(R_["tree"], p)),
                         default=0.0)
                bury = max(bury, dd)
                if dd > BURY:
                    buried.append((kinds[d_], kinds[s_], round(dd, 3)))
    rock_trunk = max([_depth(rec(a_), rec(b_)) for a_, b_ in pairs if {kinds[a_], kinds[b_]} == {"rock", "trunk"}]
                     + [0.0])
    res = {"shells": n, "floating": len(floating), "rock_trunk_cut": round(rock_trunk, 3), "floating_kinds": sorted({kinds[k] for k in floating}),
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "max_gap_all": round(max(gap[k] for k in range(n)), 3),
           "unchained": chained(tol), "unchained_kinds": list(loose_k), "unchained_chain_tol": chained(chain_tol),
           "blade_blade_cuts": len(cut_pairs), "blade_cut_max": round(max(depths.values(), default=0.0), 3),
           "blade_pairs_touching": len(depths), "leaf_cuts": len(leaf_cuts), "core_seats": seats[:6],
           "core_seat_cuts": seat_cuts, "buried_max": round(bury, 3), "buried": buried[:8],
           "kinds": {k: kinds.count(k) for k in sorted(set(kinds))}}
    bm.free()
    return res


# ---- build -----------------------------------------------------------------------------------------------------------
PARTS = ((T3_P, t3_part), (T2_P, t2_part), (T1U_P, t1u_part), (T1L_P, t1l_part), (TRUNK_P, trunk_part),
         (FOOT_P, foot_part))
ORDER = (T3_P, T2_P, T1U_P, T1L_P, TRUNK_P, FOOT_P)
TARGET_H = (22.0, 0.4)
BUDGET = {HERO: 3600, FOOT_P: 960}


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m049_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", "TallPine"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def _reset():
    RING_INFO.clear()
    RING_RECS.clear()
    CORE_RECS.clear()
    LEAF_INFO.clear()
    BUSH_INFO.clear()
    _OUTLINE.clear()


def build(render=True, parts=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    _reset()
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn)
    LEAF_INFO.clear()
    h, log["hero"] = _make(HERO, hero_all, "hero", 4000)
    log["rings"] = {k: {kk: vv for kk, vv in v.items() if kk not in ("depth", "final")} for k, v in RING_INFO.items()}
    log["leaves"] = {k: dict(v) for k, v in LEAF_INFO.items()}
    log["bushes"] = {k: dict(v) for k, v in BUSH_INFO.items()}
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
    audits = [M.audit(o) for o in order]
    thin = {o.name: m012._thin(o, 2.0) for o in order}
    shells = {o.name: shells_report(o) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = BUDGET.get(o.name, 4000 if o is h else 1000)
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
    contact = {o.name: contact_report(o) for o in order if len(shells[o.name]) > 1}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} shells touch nothing within {CONTACT}, {c['unchained']} have no "
                            f"chain of contact to the ground ({c['unchained_kinds']})")
        if c["blade_blade_cuts"]:
            problems.append(f"{n_}: {c['blade_blade_cuts']} blade pairs cut into each other (max {c['blade_cut_max']})")
        if c["leaf_cuts"]:
            problems.append(f"{n_}: {c['leaf_cuts']} leaves cut into a rock, a lobe or the trunk")
        if c["buried"]:
            problems.append(f"{n_}: dressing buried more than {BURY}: {c['buried']}")
        if c.get("rock_trunk_cut", 0) > BURY:
            problems.append(f"{n_}: a rock cuts {c['rock_trunk_cut']} into the trunk / roots")
        if c["core_seat_cuts"]:
            problems.append(f"{n_}: {c['core_seat_cuts']} core / trunk pairs intersect (pegs must clear the holes)")
    if TRUNK_P in shells and len(shells[TRUNK_P]) != 1:
        problems.append(f"{TRUNK_P}: {len(shells[TRUNK_P])} shells, expected 1")
    if sum(1 for s in shells[h.name] if s["kind"] == "trunk") != 1:
        problems.append(f"{HERO}: {sum(1 for s in shells[h.name] if s['kind'] == 'trunk')} trunk shells, expected 1")
    if abs(h.dimensions.z - TARGET_H[0]) > TARGET_H[1]:
        problems.append(f"{HERO}: height {h.dimensions.z:.2f} outside {TARGET_H[0]} +- {TARGET_H[1]}")
    for k, v in RING_INFO.items():
        if v.get("unresolved"):
            problems.append(f"ring {k}: {v['unresolved']} blades unresolved")
        if v.get("core_vs_below", 0) > CUT:
            problems.append(f"ring {k}: core cuts the ring below {v['core_vs_below']}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 12: none)")
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
            "winding": {o.name: sum(s["winding"] for s in shells[o.name]) for o in order},
            "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
            "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
            "baked_shading": {o.name: o.get("kit_baked_shading") for o in order}}


# ---- renders ---------------------------------------------------------------------------------------------------------
# decision 10: f34_sheet (-15, 12) governs; r34_sheet (165, 12), front / side / rear_sheet at e 7, top; floor hidden and
# a 3x lens on the *_sheet shots (m033._long_lens)
SHEET_VIEWS = {"f34_sheet": (-15, 12), "r34_sheet": (165, 12), "front_sheet": (0, 7), "side_sheet": (90, 7),
               "rear_sheet": (180, 7), "top_sheet": (0, 89)}
PARTS_SHOT = (-20, 20)
LIFT = {TRUNK_P: 1.8, T1L_P: 3.6, T1U_P: 5.6, T2_P: 7.6, T3_P: 9.6}      # exploded gaps (studs)


def _copy(o, tag, m, coll):
    c = bpy.data.objects.new(f"{PFX}{tag}", o.data)
    coll.objects.link(c)
    c.matrix_world = m
    return c


def _exploded(objs):
    """Copies laid out like the sheet's exploded view: crown over Tier 2 over Tier 1 upper over Tier 1 lower over the
    trunk over the root foot, each lifted along the axis."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    base = Matrix.Translation((objs[0].location.x + 80, objs[0].location.y, 0))
    shown = []
    if FOOT_P in by:
        shown.append(_copy(by[FOOT_P], "expl_foot", base @ Matrix.Translation(Vector(by[FOOT_P][OFF])), coll))
    for name, dz in LIFT.items():
        if name in by:
            shown.append(_copy(by[name], "expl_" + name, base @ Matrix.Translation((0, 0, dz))
                               @ Matrix.Translation(Vector(by[name][OFF])), coll))
    bpy.context.view_layer.update()
    return shown


def _scale_marker(h, at=(-3.6, -6.6)):
    """A 5.5-stud character stand-in under the skirt's edge, for the scale shot (its head must clear the tips)."""
    a = K.fk().Asset(PFX + "char", "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=ROCK_DEEP, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=ROCK_DEEP, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=ROCK_DEEP, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
    c.location = off @ Vector((at[0], at[1], 0.0))
    bpy.context.view_layer.update()
    return c


def render_views(objs, close=True):
    h = objs[0]
    by = {o.name: o for o in objs}
    shown = _exploded(objs) if len(objs) > 1 else []
    marker = _scale_marker(h)
    temps = shown + [marker]
    coll = h.users_collection[0]
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        for o in objs[1:]:
            extra["part_" + o.name.replace("TallPine", "").lower()] = ([o], *PARTS_SHOT)
        if shown:
            extra["exploded"] = (shown, -15, 18)
        extra["scale"] = ([h, marker], -20, 6)
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
            out["root_cu"] = m033.render_close([h], f"{d}/root_cu.png", -20, 14, off @ Vector((0.5, -2.5, 1.4)), 4.6)
            out["skirt_cu"] = m033.render_close([h], f"{d}/skirt_cu.png", -15, 12, off @ Vector((0.0, -2.0, 10.5)), 5.5)
            if T1L_P in by:
                o = by[T1L_P]
                oo = o.matrix_world @ Matrix.Translation(-Vector(o[OFF]))
                out["ring_under"] = m033.render_close([o], f"{d}/ring_under.png", -10, -40,
                                                      oo @ Vector((0.0, 0.0, 11.0)), 4.6)
                out["blade_cu"] = m033.render_close([o], f"{d}/blade_cu.png", -80, 6,
                                                    oo @ Vector((0.0, -5.2, 9.6)), 3.6)
            if TRUNK_P in by:
                o = by[TRUNK_P]
                oo = o.matrix_world @ Matrix.Translation(-Vector(o[OFF]))
                out["trunk_cu"] = m033.render_close([o], f"{d}/trunk_cu.png", -30, 30,
                                                    oo @ Vector((0.0, 0.0, 10.9)), 2.1)
        return out
    finally:
        own = {marker.name}
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
    """Rebuild just the hero (tuning loop)."""
    M.coll(NUM, TITLE)
    palette()
    _reset()
    h, lg = _make(HERO, hero_all, "hero", 4000)
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n in ORDER if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals")}, "log": lg,
            "rings": {k: {kk: vv for kk, vv in v.items() if kk not in ("depth", "final")} for k, v in RING_INFO.items()},
            "leaves": {k: dict(v) for k, v in LEAF_INFO.items()}}


def compare_conifers(path=None):
    """042 / 045 / 047 / 049 heroes side by side at true scale (copies in a row, the f34 camera)."""
    names = ("TieredFir", "PineSapling", "GnarledPine", HERO)
    objs = [bpy.data.objects[n] for n in names if n in bpy.data.objects]
    coll = bpy.data.objects[HERO].users_collection[0]
    x = 0.0
    cps = []
    try:
        for o in objs:
            w = o.dimensions.x
            x += w / 2
            cps.append(_copy(o, "cmp_" + o.name, Matrix.Translation((600 + x, -400, 0)), coll))
            x += w / 2 + 4.0
        bpy.context.view_layer.update()
        kit = K.NS["KIT"]
        path = path or f"{M.MODEL_RENDERS}/{M.code(NUM)}/cmp_conifers.png"
        old = kit["CELL"]
        kit["CELL"] = (1200, 520)
        ground = bpy.data.objects.get("FB_Ground")
        try:
            return kit["render_group"](cps, path, -15, 12)
        finally:
            kit["CELL"] = old
            if ground:
                ground.location.z = 0.0
                ground.hide_set(True)
    finally:
        for c in cps:
            bpy.data.objects.remove(c, do_unlink=True)
