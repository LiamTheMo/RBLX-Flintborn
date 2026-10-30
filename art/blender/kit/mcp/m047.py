"""047 Old Pine (references/047.png): a squat, massive old "cloud-pad" pine. A huge leaning orange-brown trunk built of
long vertical bark planks flares into seven angular buttress roots on a pale sand patch and forks at mid-height into a
leader and two fork stubs. Five hexagonal sockets (leader top, an upper-left side socket, the left and right forks, a
low right socket) take five angled, elbowed limbs; each limb ends in two or three short twigs that carry a separate
faceted foliage pad (a core lobe ringed by lower lobes and crowned by top lobes). A hollow cut stub juts from the crown
limb, a second hollow stub from the trunk's back, a knot hole from its front. The base carries chunky warm-grey rocks,
pebbles, a dark broad-leaf bush, lime upright tufts and sprigs.

    import importlib, kit_models, m047; importlib.reload(kit_models); importlib.reload(m047); m047.build()

Build frame: studs, front -Y, +X right, ground z 0 = the sand patch's flat underside, trunk foot axis at (0, 0). Every
object ends with its origin at its bbox bottom centre; o["m047_offset"] is that origin in the build frame. W04 owns
every OldPine* name, so the names are GnarledPine* (spec 8):
- GnarledPineForkedTrunk: the planked body (18 facets, socket top) with four socket stubs, the back stub, the knot and
  seven buttress roots exact-unioned in one at a time at the world origin: one closed shell.
- GnarledPineCrownCanopy / GnarledPineCanopyTier / GnarledPineBranchAngled: branch pieces (limb with a hollow plug end,
  twigs, pad lobes; the crown piece also its cut stub), every piece a closed shell seated by contact.
- GnarledPineRootBase: the sand patch, rocks, pebbles and plants (separate closed shells, all on the patch).
- GnarledPine (hero): all of the above plus the UR and R branch pieces in one object of closed shells.
Colour (stage 4) is painted by position and role inside the builders (never by facing). Stages 5-6: none (the sheet
shows no glow, light or effect). See M047_spec.md.
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
import m040
import m042
import m044

NUM, TITLE, SHEET = 47, "Old Pine", "M047"
OFF = "m047_offset"
PFX = "_m047_"
HERO = "GnarledPine"
TRUNK_P, CROWN_P, TIER_P, ANGLED_P, BASE_P = ("GnarledPineForkedTrunk", "GnarledPineCrownCanopy",
                                              "GnarledPineCanopyTier", "GnarledPineBranchAngled",
                                              "GnarledPineRootBase")

LEAF, LEAF_LIGHT, LEAF_DEEP = "m047_leaf", "m047_leaf_light", "m047_leaf_deep"
BARK, BARK_LIGHT, BARK_DEEP = "m047_bark", "m047_bark_light", "m047_bark_deep"
ROCK, ROCK_LIGHT, ROCK_DEEP = "m047_rock", "m047_rock_light", "m047_rock_deep"
SAND, SAND_DEEP = "m047_sand", "m047_sand_deep"
PLANT, PLANT_MID, PLANT_DEEP = "m047_plant", "m047_plant_mid", "m047_plant_deep"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03

# key -> (hex, roughness, low specular). Stage 4 (M047_spec.md "Stage 4") writes the calibrated values here.
PALETTE = {
    LEAF: ("#5F903A", 0.85, True),
    LEAF_LIGHT: ("#A6C234", 0.85, True),
    LEAF_DEEP: ("#2D5346", 0.9, True),
    BARK: ("#955522", 0.9, False),
    BARK_LIGHT: ("#B06F35", 0.9, False),
    BARK_DEEP: ("#341807", 0.95, False),
    ROCK: ("#A9A29A", 0.85, False),
    ROCK_LIGHT: ("#B4ADA4", 0.85, False),
    ROCK_DEEP: ("#8E8A85", 0.9, False),
    SAND: ("#B2A283", 0.95, False),
    SAND_DEEP: ("#A69175", 0.95, False),
    PLANT: ("#919824", 0.85, True),
    PLANT_MID: ("#558331", 0.85, True),
    PLANT_DEEP: ("#265A3B", 0.85, True),
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions), K.sample kinds
TARGETS = {LEAF: ((0x5A, 0x8C, 0x30), "green"), LEAF_LIGHT: ((0xB0, 0xC4, 0x31), "green"),
           LEAF_DEEP: ((0x2D, 0x56, 0x42), "all"), BARK: ((0xA0, 0x58, 0x29), "brown"),
           BARK_LIGHT: ((0xBE, 0x72, 0x39), "brown"), BARK_DEEP: ((0x42, 0x28, 0x1A), "brown"),
           ROCK: ((0xDB, 0xCC, 0xB6), "all"), ROCK_LIGHT: ((0xE3, 0xD1, 0xBB), "all"),
           ROCK_DEEP: ((0xB1, 0xAD, 0xA8), "all"), SAND: ((0xE2, 0xC6, 0x98), "brown"),
           SAND_DEEP: ((0xD2, 0xB0, 0x86), "brown"), PLANT: ((0x9C, 0xB4, 0x26), "green"),
           PLANT_MID: ((0x4B, 0x75, 0x26), "green"), PLANT_DEEP: ((0x24, 0x55, 0x33), "green")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    # mixed keys made by an earlier build: re-mix them from the (possibly new) parents
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m047_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k == "m047_" + tail), None) or \
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
_faces = m033._faces
_mottle = m033._mottle
_leaf8 = m042._leaf8


def _mix(k1, k2, t):
    t = round(max(0.0, min(1.0, t)) * 4) / 4
    return K.mix_key(k1, k2, t)


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


def _dir(tilt, az):
    """Unit axis tilted `tilt` degrees from vertical toward plan azimuth `az`."""
    t, p = math.radians(tilt), math.radians(az)
    return Vector((math.sin(t) * math.cos(p), math.sin(t) * math.sin(p), math.cos(t)))


def _basis(d, ref=None):
    d = d.normalized()
    if ref is None:
        ref = Vector((1, 0, 0)) if abs(d.z) > 0.9 else Vector((0, 0, 1))
    u = (ref - d * ref.dot(d)).normalized()
    return u, d.cross(u)


def _ring(c, u, v, r, n, rot=0.0):
    return [c + (u * math.cos(rot + 2 * math.pi * k / n) + v * math.sin(rot + 2 * math.pi * k / n)) * r
            for k in range(n)]


def _zip(bm, A, B, c, u, v, cb=None):
    """Triangles between two closed rings (any sizes) round centre c (ring B round cb, if given) in the plane basis
    (u, v), walking both by angle. Returns faces (orientation fixed later by recalc_face_normals)."""
    def ang(p, cc=c):
        q = p.co - cc
        return math.atan2(q.dot(v), q.dot(u))
    cb = c if cb is None else cb
    angb = lambda p: ang(p, cb)
    a0 = min(range(len(A)), key=lambda i: ang(A[i]) % (2 * math.pi))
    b0 = min(range(len(B)), key=lambda i: angb(B[i]) % (2 * math.pi))
    A = A[a0:] + A[:a0]
    B = B[b0:] + B[:b0]
    na, nb = len(A), len(B)
    base = ang(A[0])

    def ua(i):
        return (ang(A[i % na]) - base) % (2 * math.pi) + (2 * math.pi if i >= na else 0.0)

    def ub(j):
        return (angb(B[j % nb]) - base) % (2 * math.pi) + (2 * math.pi if j >= nb else 0.0)
    i = j = 0
    out = []
    while i < na or j < nb:
        if j >= nb or (i < na and ua(i + 1) <= ub(j + 1)):
            out.append(bm.faces.new((A[i % na], A[(i + 1) % na], B[j % nb])))
            i += 1
        else:
            out.append(bm.faces.new((A[i % na], B[(j + 1) % nb], B[j % nb])))
            j += 1
    return out


def _band(bm, A, B):
    n = len(A)
    return [bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k])) for k in range(n)]


def _hollow_cap(bm, ring, c, d, f_in, depth, walls=False):
    """End cap of a tube: a flat rim from `ring` (verts) in to a ring scaled f_in about c, then a hollow down `depth`
    against the axis d (d points out of the tube): a shallow pyramid pit, or (walls) a socket hole with straight walls
    and a flat floor. Returns (rim faces, hollow faces, verts)."""
    inner = [bm.verts.new(c + (v.co - c) * f_in) for v in ring]
    rim = _band(bm, ring, inner)
    n = len(inner)
    if walls:
        deep = [bm.verts.new(v.co - d * depth) for v in inner]
        hollow = _band(bm, inner, deep) + [bm.faces.new(deep)]
        return rim, hollow, inner + deep
    pit = bm.verts.new(c - d * depth)
    hollow = [bm.faces.new((inner[k], inner[(k + 1) % n], pit)) for k in range(n)]
    return rim, hollow, inner + [pit]


def _close(a, vs, fs, key):
    bmesh.ops.recalc_face_normals(a.bm, faces=fs)
    a._finish(vs, key, tint=1.0)


# ---- tubes (limbs, twigs, stubs) ---------------------------------------------------------------------------------------
def _frames(pts, u0):
    """Parallel-transported (tangent, u, v) per point of a polyline, starting from u0."""
    n = len(pts)
    ts = []
    for i in range(n):
        if i == 0:
            t = (pts[1] - pts[0]).normalized()
        elif i == n - 1:
            t = (pts[-1] - pts[-2]).normalized()
        else:
            t = ((pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized()).normalized()
        ts.append(t)
    out = []
    u = u0
    for t in ts:
        u = (u - t * u.dot(t))
        u = u.normalized() if u.length > 1e-6 else _basis(t)[0]
        out.append((t, u, t.cross(u)))
    return out


def tube(a, pts, radii, n, u0, rot=0.0, start="flat", end="flat", key=BARK, hollow=(0.55, 0.12)):
    """A closed n-sided tube along a polyline (parallel-transported frames from u0, rings rotated `rot`). Caps:
    "flat", "point", "hollow" (rim + pit) or "socket" (rim + walled hole); cut-face colours. Returns (verts, side
    faces, cap faces dict)."""
    bm = a.bm
    fr = _frames(pts, u0)
    rings = []
    for p, r, (t, u, v) in zip(pts, radii, fr):
        rings.append([bm.verts.new(q) for q in _ring(p, u, v, r, n, rot)])
    side = []
    for i in range(len(rings) - 1):
        side += _band(bm, rings[i], rings[i + 1])
    vs = [v for r in rings for v in r]
    caps = {"rim": [], "hollow": [], "flat": []}
    for which, ring, c, d in (("s", rings[0], pts[0], -fr[0][0]), ("e", rings[-1], pts[-1], fr[-1][0])):
        kind = start if which == "s" else end
        if kind == "flat":
            caps["flat"].append(bm.faces.new(ring if which == "e" else list(reversed(ring))))
        elif kind == "point":
            tip = bm.verts.new(c + d * 0.25)
            caps["flat"] += [bm.faces.new((ring[k], ring[(k + 1) % n], tip)) for k in range(n)]
            vs.append(tip)
        else:
            rim, hol, extra = _hollow_cap(bm, ring, c, d, *hollow, walls=(kind == "socket"))
            caps["rim"] += rim
            caps["hollow"] += hol
            vs += extra
    fs = side + caps["rim"] + caps["hollow"] + caps["flat"]
    _close(a, vs, fs, key)
    _paint(a, caps["rim"], BARK_LIGHT)
    _paint(a, caps["hollow"], BARK_DEEP)
    return vs, side, caps


# ---- trunk body (spec 2.2) ---------------------------------------------------------------------------------------------
# (z, centre x, centre y, corner radius, x scale, y scale): the rings widen across the fork (X) at z 7.6-8.8
TRUNK = ((0.05, -0.45, 0.0, 4.2, 1.0, 1.0), (1.6, -0.2, 0.0, 3.7, 1.0, 1.0), (4.0, 0.2, 0.1, 3.25, 1.0, 1.0),
         (6.0, 0.55, 0.15, 3.05, 1.0, 1.0), (7.6, 0.8, 0.2, 2.95, 1.05, 0.98), (8.8, 1.0, 0.25, 2.65, 1.1, 0.96),
         (10.2, 1.25, 0.35, 2.15, 1.04, 1.0), (13.5, 1.85, 0.6, 1.7, 1.0, 1.0))
TWIST = 3.0
# per plank (9 sides): the split vertex pushed out (+, a proud plank) or pulled in (-, a groove)
PLANKS = (0.08, -0.16, 0.08, -0.12, -0.19, 0.08, -0.14, 0.08, -0.20)
TOP_HOLE = (1.05, 0.35)
TOP_AXIS = (18.0, 90.0)                  # tilt from vertical, toward plan azimuth                 # leader-top socket hole: hex corner radius, depth
SOCKETS = {   # name -> axis anchor z, tilt, azimuth, protrusion beyond the bark, outer r, hole r, hole depth
    # fix round 1: the right fork and the low right socket moved down (faces at z ~10.3 and ~6.3) and the left fork
    # a little down, so the UR, R and L limbs run 4-5 studs and rise 30-45 deg into their pads (spec 2.3)
    "lf": dict(z=4.4, tilt=56.0, az=194.0, out=1.0, ro=1.35, rh=0.85, depth=0.35),
    "rf": dict(z=8.2, tilt=55.0, az=10.0, out=0.95, ro=1.3, rh=0.85, depth=0.35),
    "lr": dict(z=3.3, tilt=68.0, az=334.0, out=0.85, ro=1.12, rh=0.70, depth=0.30),
    "ul": dict(z=10.9, tilt=55.0, az=150.0, out=0.75, ro=1.05, rh=0.66, depth=0.30),
}
BACK_STUB = dict(z=8.6, tilt=72.0, az=80.0, out=1.2, ro=0.85, rh=0.5, depth=0.32)
KNOT = dict(z=9.6, tilt=90.0, az=272.0, out=0.06, ro=0.36, rh=0.23, depth=0.3, dx=-0.6, n=5)
SOCK = {}              # socket name -> dict(F (face centre), d (axis out), u (hex frame), ro, rh, depth)


def _axis_at(z):
    """Trunk centre (x, y, z) at height z (linear between rings)."""
    for (z0, x0, y0, *_), (z1, x1, y1, *_) in zip(TRUNK, TRUNK[1:]):
        if z <= z1:
            t = max(0.0, (z - z0) / (z1 - z0))
            return Vector((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z))
    return Vector((TRUNK[-1][1], TRUNK[-1][2], z))


def trunk_body(a):
    """The planked body: 9 sides each split once (18 facets; the split pushed out for a proud plank or pulled in for a
    groove, varying a little per ring), rings twisted 3 deg per level, a flat bottom, a flat leader top with the
    hexagonal socket hole. Coloured by role (grooves deeper, foot deeper, cut top lighter, hole deep)."""
    bm = a.bm
    rng = random.Random(47400)
    rings, groove_v = [], set()
    for i, (z, cx, cy, r, sx, sy) in enumerate(TRUNK):
        ring = []
        c = Vector((cx, cy, z))
        tw = TWIST * i
        for k in range(18):
            j = k // 2
            if k % 2 == 0:
                az = 40.0 * j + tw + rng.uniform(-2, 2)
                rr = r * (1 + rng.uniform(-0.025, 0.025))
            else:
                az = 40.0 * j + 20.0 + tw + rng.uniform(-3, 3)
                off = PLANKS[j] * (0.75 + 0.5 * rng.random()) * min(1.0, r / 2.4)
                rr = r * math.cos(math.radians(20)) + off
            if i == len(TRUNK) - 1 and k % 2 == 1:
                continue                     # the small leader top: corners only (the planks converge)
            p = _u(az) * rr
            v = bm.verts.new(c + Vector((p.x * sx, p.y * sy, 0.0)))
            if k % 2 == 1 and PLANKS[j] < 0:
                groove_v.add(v)
            ring.append(v)
        rings.append(ring)
    side = []
    for i in range(len(rings) - 2):
        side += _band(bm, rings[i], rings[i + 1])
    ca, cb = (Vector(TRUNK[-2][1:3] + (TRUNK[-2][0],)), Vector(TRUNK[-1][1:3] + (TRUNK[-1][0],)))
    side += _zip(bm, rings[-2], rings[-1], ca, Vector((1, 0, 0)), Vector((0, 1, 0)), cb=cb)
    bot = [bm.faces.new(list(reversed(rings[0])))]
    zt, cx, cy = TRUNK[-1][:3]
    c = Vector((cx, cy, zt))
    d = _dir(*TOP_AXIS)                     # the leader-top socket leans back toward the crown pad
    u, v = _basis(d)
    rh, depth = TOP_HOLE
    hole = [bm.verts.new(p) for p in _ring(c, u, v, rh, 6, 0.0)]
    top = _zip(bm, rings[-1], hole, c, u, v)
    deep = [bm.verts.new(p) for p in _ring(c - d * depth, u, v, rh, 6, 0.0)]
    walls = _band(bm, hole, deep)
    floor = [bm.faces.new(deep)]
    SOCK["top"] = dict(F=c, d=d, u=u, ro=1.25, rh=rh, depth=depth)
    vs = [x for r in rings for x in r] + hole + deep
    _close(a, vs, side + bot + top + walls + floor, BARK)
    for f in side:
        zc = f.calc_center_median().z
        if sum(1 for x in f.verts if x in groove_v) >= 2:
            f.material_index = a._mi(_mix(BARK, BARK_DEEP, 0.25))
        elif zc < 1.0:
            f.material_index = a._mi(_mix(BARK, BARK_DEEP, 0.25))
    _paint(a, top, BARK_LIGHT)
    _paint(a, walls + floor, BARK_DEEP)
    tones = [1.0 + rng.uniform(-0.04, 0.04) for _ in range(18)]
    for i in range(len(rings) - 2):
        for k in range(18):
            _tint(a, [side[i * 18 + k]], tones[k])
    _mottle(a, side, 0.04, 0.35, 47410)
    vs += knot(a, side)
    return vs, side


def knot(a, side):
    """The front knot hole, cut into the plank facet facing KNOT's direction at its height: the facet inset to a rim
    raised 0.06 (bark_light, a cut face), then inset again and sunk 0.28 (the hole: bark_deep), its inner face squeezed
    to a round-ish hole."""
    bm = a.bm
    d = _dir(KNOT["tilt"], KNOT["az"])
    ax = _axis_at(KNOT["z"])

    def score(f):
        c = f.calc_center_median()
        if abs(c.z - KNOT["z"]) > 0.8:
            return -1e9
        q = c - ax
        q.z = 0.0
        return q.normalized().dot(d) - 0.15 * abs(c.z - KNOT["z"])
    f = max(side, key=score)
    r1 = bmesh.ops.inset_individual(bm, faces=[f], thickness=0.2, depth=0.06, use_even_offset=True)
    c = f.calc_center_median()
    up = Vector((0, 0, 1))
    for v in f.verts:                       # a round-ish inner face: squeeze it toward the centre vertically
        q = v.co - c
        v.co = c + q - up * q.dot(up) * 0.45
    r2 = bmesh.ops.inset_individual(bm, faces=[f], thickness=0.05, depth=-0.28, use_even_offset=True)
    rim = list(r1["faces"])
    hole = list(r2["faces"]) + [f]
    _paint(a, rim, BARK_LIGHT)
    _paint(a, hole, BARK_DEEP)
    SOCK["knot"] = dict(F=c, d=d, t=0.0)
    return list({v for g in rim + hole for v in g.verts})


def _surface_t(tree, A, d):
    """Distance along d from A (inside the body) to where the ray leaves the body."""
    o, t = A.copy(), 0.0
    last = None
    for _ in range(12):
        h = tree.ray_cast(o, d)
        if h[0] is None:
            break
        last = (h[0] - A).dot(d)
        o = h[0] + d * 1e-4
    return last


def _place_socket(tree, name, spec, plug=False):
    d = _dir(spec["tilt"], spec["az"])
    A = _axis_at(spec["z"]) + Vector((spec.get("dx", 0.0), 0.0, 0.0))
    t = _surface_t(tree, A, d)
    F = A + d * (t + spec["out"])
    u, v = _basis(d)
    SOCK[name] = dict(F=F, d=d, u=u, ro=spec["ro"], rh=spec["rh"], depth=spec["depth"], A=A, t=t, plug=plug,
                      n=spec.get("n", 6))
    return SOCK[name]


def stub(a, s, start=None):
    """A hexagonal stub from inside the trunk (from A, flared) out to its flat cut face at F: a rim round a hexagonal
    hole (walls and floor bark_deep, rim bark_light). Unioned into the trunk."""
    F, d, u = s["F"], s["d"], s["u"]
    A = start if start is not None else s["A"]
    L = (F - A).dot(d)
    pts = [F - d * L, F]
    radii = [s["ro"] * 1.18, s["ro"]]
    vs, side, caps = tube(a, pts, radii, s.get("n", 6), u, 0.0, start="flat",
                          end="socket" if s.get("plug") else "hollow",
                          key=BARK, hollow=(s["rh"] / s["ro"], s["depth"]))
    _mottle(a, side, 0.04, 0.35, 47420 + int(L * 10))
    return vs


# roots: name, azimuth, reach, height at the trunk, width, segments, kink (deg)
ROOTS = (("RT1", 330.0, 8.6, 4.6, 3.2, 3, -9.0), ("RT2", 10.0, 7.2, 4.0, 2.8, 2, 8.0),
         ("RT3", 275.0, 6.8, 4.0, 2.8, 2, 10.0), ("RT4", 212.0, 7.4, 4.0, 2.9, 2, -9.0),
         ("RT5", 166.0, 6.4, 3.6, 2.6, 2, 8.0), ("RT6", 118.0, 5.6, 3.3, 2.4, 2, -8.0),
         ("RT7", 62.0, 5.9, 3.5, 2.5, 2, 9.0))
ROOT_ZB = 0.10


def _root_stations(spec):
    name, az, reach, h, w, nseg, kink = spec
    dk = max(0.58 * reach, 4.9)
    # from inside the trunk (the ridge rising up the bark to about h + 0.5) out over the flare to the kink, then on
    # to a blunt tip
    st = [(2.0, h + 0.5, 1.05 * w, ROOT_ZB), (dk, 0.62 * h + 0.15, 0.85 * w, ROOT_ZB)]
    if nseg >= 3:
        st.append((dk + 0.55 * (reach - dk), 0.4 * h + 0.2, 0.62 * w, ROOT_ZB))
    st.append((reach, 0.42, 0.45, ROOT_ZB))
    return st, dk


def _root_at(spec, d):
    name, az, reach, h, w, nseg, kink = spec
    dk = _root_stations(spec)[1]
    if d <= dk:
        return _u(az) * d, _u(az)
    return _u(az) * dk + _u(az + kink) * (d - dk), _u(az + kink)


def root(a, spec, rng):
    """One buttress root: a four-sided prism (flat bottom on the sand, two steep flanks, a narrow top ridge a little
    off centre) from inside the trunk out to a blunt tip sunk into the sand, kinked once in plan."""
    bm = a.bm
    st, dk = _root_stations(spec)
    secs = []
    off = rng.uniform(-0.1, 0.1)
    for d, zt, ww, zb in st:
        c, t = _root_at(spec, d)
        s = Vector((-t.y, t.x, 0.0))
        pts = [c - s * ww / 2 + Vector((0, 0, zb)), c + s * ww / 2 + Vector((0, 0, zb)),
               c + s * (off + 0.16) * ww + Vector((0, 0, zt)), c + s * (off - 0.16) * ww + Vector((0, 0, zt - 0.06))]
        secs.append([bm.verts.new(p) for p in pts])
    c, t = _root_at(spec, spec[2] + 0.25)
    tip = bm.verts.new(c + Vector((0, 0, 0.12)))
    fs = [bm.faces.new(list(reversed(secs[0])))]
    for i in range(len(secs) - 1):
        fs += _band(bm, secs[i], secs[i + 1])
    last = secs[-1]
    fs += [bm.faces.new((last[k], last[(k + 1) % 4], tip)) for k in range(4)]
    vs = [v for s_ in secs for v in s_] + [tip]
    _close(a, vs, fs, BARK)
    ridge_vs = {secs[i][k] for i in range(len(secs)) for k in (2, 3) if st[i][0] >= 0.5 * spec[2]}
    for f in fs:
        if f.calc_center_median().z < 0.6:
            f.material_index = a._mi(_mix(BARK, BARK_DEEP, 0.25))
        elif sum(1 for v in f.verts if v in ridge_vs) >= 3:      # the top ridge strip (position on the root)
            f.material_index = a._mi(_mix(BARK, BARK_LIGHT, 0.25))
    _mottle(a, fs, 0.04, 0.5, 47450 + int(spec[1]))
    return vs


def trunk_part(a):
    """Body first (shell 0, the union's base), then the socket stubs, the back stub, the roots and the knot (each its
    own closed shell, unioned in one at a time)."""
    vs, side = trunk_body(a)
    idx = {v: i for i, v in enumerate(vs)}
    fs = _faces(vs)
    tree = BVHTree.FromPolygons([v.co.copy() for v in vs], [[idx[v] for v in f.verts] for f in fs])
    for name, spec in SOCKETS.items():
        stub(a, _place_socket(tree, name, spec, plug=True))
    stub(a, _place_socket(tree, "back", BACK_STUB))
    rng = random.Random(47500)
    for spec in ROOTS:
        root(a, spec, rng)


# ---- foliage pads (spec 2.3) -------------------------------------------------------------------------------------------
def lobe(a, c, w, h, rot, seed, key, radial=None, sq=0.85, tilt=0.0, stretch=1.0, n=6):
    """One closed faceted lobe (22 tris) standing on its bottom centre c: a near-flat bottom hexagon (0.72 of the
    half-width), a widest ring of 6 at 0.6 h (half a step round), a low top vertex: a chunky dome whose six big top
    facets meet at a point (the sheet's rosette facets). radial: a plan direction to stretch the lobe along (a petal,
    `stretch` long and `sq` across) and to tilt it outward by `tilt` degrees (its top leaning out, as on a dome)."""
    rng = random.Random(seed)
    bm = a.bm
    if radial is None:
        ux, uy, sx, sy = Vector((1, 0, 0)), Vector((0, 1, 0)), 1.0, 1.0
    else:
        ux = Vector((radial.x, radial.y, 0.0)).normalized()
        uy = Vector((-ux.y, ux.x, 0.0))
        sx, sy = stretch, sq
    R = w / 2

    def P(r, ang, z, jit=0.08):
        rr = r * (1 + rng.uniform(-jit, jit))
        return c + ux * (math.cos(ang) * rr * sx) + uy * (math.sin(ang) * rr * sy) + Vector((0, 0, z))
    N = n
    st = 2 * math.pi / N
    bot = [bm.verts.new(P(0.72 * R, rot + st * k, rng.uniform(0.0, 0.05))) for k in range(N)]
    wide = [bm.verts.new(P(R, rot + st * (k + 0.5), 0.6 * h * rng.uniform(0.92, 1.08))) for k in range(N)]
    tip = bm.verts.new(c + ux * rng.uniform(-0.06, 0.06) * w + uy * rng.uniform(-0.06, 0.06) * w + Vector((0, 0, h)))
    fs = [bm.faces.new(list(reversed(bot)))]
    for k in range(N):
        j = (k + 1) % N
        fs.append(bm.faces.new((bot[k], bot[j], wide[k])))
        fs.append(bm.faces.new((bot[j], wide[j], wide[k])))
        fs.append(bm.faces.new((wide[k], wide[j], tip)))
    vs = bot + wide + [tip]
    if tilt and radial is not None:
        piv = c + Vector((0, 0, 0.4 * h))
        bmesh.ops.rotate(bm, verts=vs, cent=piv, matrix=Matrix.Rotation(math.radians(tilt), 3, uy))
    _close(a, vs, fs, key)
    return vs, fs


# pad -> centre (x, y), lowest (drooped outer rim) z, top z, W, D, core bottom z (the flat underside the twigs enter),
# ring lobes, top lobes, tone (light share of the pad's base), seed. Fix round 1: one domed cloud per pad - a broad flat
# core, a ring of flattened lobes overlapping it by about half their width, a broad top rosette; 8-10 lobes a pad
# (decision 3's 9 / 6 / 7 / 8 / 7, main-session ruling: at most 14 / 9 / 11 / 12 / 11).
PADS = {
    "C": dict(c=(1.7, 3.9), zb=15.0, zt=20.0, W=8.6, D=6.0, core=15.6, ring=7, up=4, light=0.75, seed=47601),
    "UL": dict(c=(-3.1, 4.1), zb=14.7, zt=18.6, W=6.0, D=4.8, core=15.2, ring=5, up=2, light=0.25, seed=47602),
    "UR": dict(c=(7.6, 1.6), zb=13.5, zt=17.4, W=6.6, D=5.0, core=14.2, ring=5, up=3, light=0.25, seed=47603),
    "L": dict(c=(-5.6, -3.0), zb=8.5, zt=14.3, W=8.9, D=6.4, core=9.6, ring=6, up=3, light=0.0, seed=47604),
    "R": dict(c=(7.2, -3.2), zb=7.9, zt=12.2, W=6.9, D=5.6, core=8.75, ring=5, up=3, light=0.0, seed=47605),
}
PAD_INFO = {}
LOBE_HW = 0.54               # ring, upper and top lobes: height : width (verifier round 1: 0.55-0.65, not d20 gems)


def _pad_key(t, tone):
    """A lobe's key by its mid height t (0 = the pad's lowest point, 1 = its top): the lowest lobes deepest, the
    middle at the pad's tone, the top light (role and position, never facing). The crown pad (tone 0.75) lightest."""
    if t < 0.28:
        return _mix(LEAF, LEAF_DEEP, 0.5 * (1 - 0.5 * tone))
    if t < 0.42:
        return _mix(LEAF, LEAF_DEEP, 0.25)
    if t < 0.60:
        return _mix(LEAF, LEAF_LIGHT, 0.5 * tone)
    if t < 0.74:
        return _mix(LEAF, LEAF_LIGHT, 0.3 + 0.4 * tone)
    return _mix(LEAF, LEAF_LIGHT, 0.7 + 0.3 * tone)


def pad(a, name):
    """One pad, a single domed cloud built from few, broad, flattened lobes that overlap by about half their width:
    a broad flat-bottomed core lobe on the twig tips (its underside is close-up 3's "flat cut surface"); a ring of
    lobes round its rim (the scalloped sides: the outer ones, away from the trunk, droop a little; the inner ones are
    lifted so the limb and its twigs show under the pad); an upper ring over the core's shoulder and one broad top
    lobe (together the rosette seen from above). Colour by lobe height in the pad (deepest lowest, light on top)."""
    P = PADS[name]
    rng = random.Random(P["seed"])
    cx, cy = P["c"]
    W, D, zb, zt = P["W"], P["D"], P["zb"], P["zt"]
    H = zt - zb
    zc = P["core"]
    Hp = zt - zc
    ky = D / W
    tone = P["light"]
    away = Vector((cx, cy, 0.0)) - _axis_at(zc)
    away.z = 0.0
    away = away.normalized() if away.length > 1e-3 else Vector((0, 1, 0))
    out = []
    lobes = []

    def put(ctr, w, h, seed, radial=None, tilt=0.0, squeeze=1.0, n=5, sq=0.9):
        vs, fs = lobe(a, ctr, w, h, rng.uniform(0, 1), seed, LEAF, radial=radial, tilt=tilt, sq=sq, n=n)
        if squeeze != 1.0:             # the pad is D deep: squeeze the lobe's spread in y about its own centre
            for v in vs:
                v.co.y = ctr.y + (v.co.y - ctr.y) * squeeze
        zs = [v.co.z for v in vs]
        lobes.append((fs, 0.5 * (min(zs) + max(zs))))
        out.extend(vs)
        return vs
    # core: broad and low, its flat underside at zc
    cw = 0.68 * W
    ch = max(0.5 * cw, min(0.6 * cw, 0.72 * Hp))
    core = put(Vector((cx, cy, zc)), cw, ch, P["seed"] + 1, squeeze=ky, n=6)
    az0 = rng.uniform(0, 360)
    # ring round the core's rim, overlapping it by about half a lobe
    n = P["ring"]
    lw = 0.44 * W
    droop = zc - zb
    for k in range(n):
        az = az0 + 360.0 * k / n + rng.uniform(-8, 8)
        dv = _u(az)
        rr = 0.31 * W * rng.uniform(0.96, 1.04)
        o = dv.dot(away)
        # the rim droops on the pad's outer side in X (the sheet's front and f34 see the pads' undersides across the
        # trunk's sides), the lobes nearer the cameras (-Y) stay up so the limb and twigs show under them
        ox = dv.x * (1.0 if away.x >= 0 else -1.0)
        lift = -droop * max(0.0, ox) ** 2 + 0.5 * max(0.0, -o) + 0.1 * (1 - abs(o))
        ctr = Vector((cx + dv.x * rr, cy + dv.y * rr * ky, zc + lift + rng.uniform(-0.08, 0.08)))
        w = lw * rng.uniform(0.93, 1.07)
        put(ctr, w, LOBE_HW * w, P["seed"] + 10 + k, radial=dv, tilt=7.0)
    # upper ring over the core's shoulder, half a step round from the ring
    n = P["up"]
    uw = 0.38 * W
    for k in range(n):
        az = az0 + 180.0 / P["ring"] + 360.0 * k / n + rng.uniform(-10, 10)
        dv = _u(az)
        rr = 0.2 * W * rng.uniform(0.94, 1.06)
        ctr = Vector((cx + dv.x * rr, cy + dv.y * rr * ky, zc + 0.5 * ch + rng.uniform(-0.08, 0.08)))
        w = uw * rng.uniform(0.94, 1.06)
        put(ctr, w, LOBE_HW * w, P["seed"] + 30 + k, radial=dv, tilt=10.0)
    # one broad top lobe raising the dome to zt (sunk into the core: its bottom at most 0.35 below the core's top)
    tw = 0.46 * W
    th = min(0.65 * tw, max(LOBE_HW * tw, zt - (zc + ch - 0.35)))
    ctr = Vector((cx + rng.uniform(-0.15, 0.15), cy + rng.uniform(-0.15, 0.15), zt - th))
    put(ctr, tw, th, P["seed"] + 50, squeeze=0.5 + 0.5 * ky, n=7)
    for fs, m in lobes:
        _paint(a, fs, _pad_key((m - zb) / H, tone))
        _tint(a, fs, 1.0 + rng.uniform(-0.04, 0.04))
    _mottle(a, _faces(out), 0.03, 0.5, P["seed"] + 77)
    PAD_INFO[name] = dict(core=core, lobes=len(lobes), core_top=round(zc + ch, 2), top_bottom=round(zt - th, 2))
    return out


# ---- limbs and twigs (spec 2.3) ----------------------------------------------------------------------------------------
# limb -> socket, waypoints after the shoulder (absolute build-frame points; the last one is the twig fork), limb
# radius at the socket and at the fork, twig tips as (dx, dy) offsets from the pad centre into the core's underside
# Fix round 1: the planned runs restored (socket face -> twig fork: UR ~5, R ~4.3, L ~4 rising 30-40 deg after an
# elbow), the fork about 1.1-1.3 below the core's flat underside so the 2-3 twigs show (close-up 3).
LIMBS = {
    "C": dict(sock="top", way=["d0.7", (1.85, 1.8, 14.45), (1.8, 2.7, 14.35)], r=(1.4, 0.8),
              twigs=[(-1.0, 0.1), (0.8, -0.2), (0.1, 1.1)], stub=True),
    "UL": dict(sock="ul", way=["d0.9", (-1.9, 2.55, 13.45), (-2.85, 3.3, 13.75)], r=(1.0, 0.6),
               twigs=[(-0.7, -0.5), (0.7, 0.4)]),
    "UR": dict(sock="rf", way=["d0.8", (5.9, 1.1, 11.4), (7.2, 1.5, 12.8)], r=(1.25, 0.65),
               twigs=[(-0.8, -0.5), (0.7, 0.6), (0.3, -1.0)]),
    "L": dict(sock="lf", way=["d0.6", (-4.0, -1.25, 7.0), (-5.25, -2.3, 8.15)], r=(1.3, 0.68),
              twigs=[(-1.0, -0.3), (0.8, 0.3), (-0.1, 1.1)]),
    "R": dict(sock="lr", way=["d0.7", (5.3, -2.05, 6.2), (6.95, -2.6, 7.35)], r=(1.08, 0.62),
              twigs=[(-0.8, -0.5), (0.8, 0.5), (0.2, -1.0)]),
}
# the crown limb's hollow cut stub: from the limb just above the leader top, out toward the front-right and up, its
# hollow end facing the f34 camera (verifier round 1, item 4)
CUT_STUB = dict(r=0.5, length=1.9, az=325.0, tilt=52.0, at=0.6)
LIMB_INFO = {}
STUB_INFO = {}


def _limb_points(name):
    L = LIMBS[name]
    s = SOCK[L["sock"]]
    F, d = s["F"], s["d"]
    rp = s["rh"] - 0.02                      # plug corner radius: 0.02 clearance in the hole
    # the plug, then a thin shoulder 0.05-0.09 over the rim, a touch wider than the stub so it covers the rim
    pts = [F - d * (s["depth"] - 0.015), F + d * 0.05, F + d * 0.09]
    radii = [rp, rp, max(L["r"][0], s["ro"] + 0.03)]
    way = [] if isinstance(L["way"][0], str) else [F + d * 0.35]   # leave the shoulder along the socket axis
    for w in L["way"]:
        if isinstance(w, str):
            way.append(F + d * float(w[1:]))
        else:
            way.append(Vector(w))
    total = sum((q - p).length for p, q in zip([pts[-1]] + way[:-1], way))
    acc = 0.0
    prev = pts[-1]
    for w in way:
        acc += (w - prev).length
        t = acc / total
        radii.append(L["r"][0] + (L["r"][1] - L["r"][0]) * t)
        pts.append(w)
        prev = w
    return pts, radii, s


def limb(a, name):
    """A six-sided limb from its hollow plug end (in the socket, 0.02 clearance, 0.015 off the hole floor) through a
    shoulder over the socket rim and its elbows to the twig fork (flat end)."""
    pts, radii, s = _limb_points(name)
    vs, side, caps = tube(a, pts, radii, 6, s["u"], 0.0, start="hollow", end="flat", key=BARK, hollow=(0.55, 0.12))
    # the last segment a quarter step lighter toward the twigs (position along the limb)
    tail = pts[-2]
    for f in side:
        if (f.calc_center_median() - tail).dot(pts[-1] - tail) > 0.5 * (pts[-1] - tail).length_squared:
            f.material_index = a._mi(_mix(BARK, BARK_LIGHT, 0.25))
    _mottle(a, side, 0.04, 0.4, 47700 + len(name))
    LIMB_INFO[name] = dict(pts=pts, radii=radii, plug=[v.co.copy() for v in vs[:12]])
    return vs


def twigs(a, name):
    """2-3 five-sided twigs from inside the limb's end up into the core lobe's underside (tips buried 0.3)."""
    L = LIMBS[name]
    P = PADS[name]
    pts = LIMB_INFO[name]["pts"]
    E, prev = pts[-1], pts[-2]
    t = (E - prev).normalized()
    u, v = _basis(t)
    out = []
    for i, (dx, dy) in enumerate(L["twigs"]):
        tip = Vector((P["c"][0] + dx, P["c"][1] + dy * P["D"] / P["W"], P["core"] + 0.32))
        lat = (tip - E)
        lat = lat - t * lat.dot(t)
        lat = lat.normalized() * 0.18 if lat.length > 1e-6 else u * 0.18
        base = E - t * 0.28 + lat
        mid = base + (tip - base) * 0.5 + Vector((0, 0, -0.08))
        d0 = (tip - base).normalized()
        u0 = _basis(d0)[0]
        vs, side, caps = tube(a, [base, tip], [0.37, 0.28], 4, u0, 0.3 * i, start="flat", end="flat", key=BARK)
        _mottle(a, side, 0.04, 0.6, 47750 + i)
        LIMB_INFO[name].setdefault("twigs", []).append((base.copy(), tip.copy()))
        out += vs
    return out


def cut_stub(a):
    """The hollow cut stub on the crown limb: a hex prism from the limb's axis out and up, its end cut flat round a
    hollow (spec 2.3)."""
    pts = LIMB_INFO["C"]["pts"]
    p0, p1 = pts[2], pts[3]
    base = p0 + (p1 - p0) * CUT_STUB["at"]
    d = _dir(CUT_STUB["tilt"], CUT_STUB["az"])
    end = base + d * CUT_STUB["length"]
    u = _basis(d)[0]
    vs, side, caps = tube(a, [base, base + d * 0.5, end], [CUT_STUB["r"] * 1.05, CUT_STUB["r"], CUT_STUB["r"]], 6, u,
                          0.0, start="flat", end="hollow", key=BARK, hollow=(0.6, 0.3))
    STUB_INFO.update(end=end.copy(), d=d.copy())
    return vs


def branch_piece(a, name):
    limb(a, name)
    twigs(a, name)
    if LIMBS[name].get("stub"):
        cut_stub(a)
    pad(a, name)


def crown_part(a):
    branch_piece(a, "C")


def tier_part(a):
    branch_piece(a, "UL")


def angled_part(a):
    branch_piece(a, "L")


def ur_part(a):
    branch_piece(a, "UR")


def r_part(a):
    branch_piece(a, "R")


# ---- root base (spec 2.4) ----------------------------------------------------------------------------------------------
PATCH_TOP = 0.15
ROCKS = {   # name -> centre, (W, D, H), yaw, seed
    "RK1": ((-3.4, -5.6), (3.0, 2.6, 2.4), 25.0, 47801),
    "RK2": ((-7.6, -2.0), (2.6, 2.2, 1.8), -20.0, 47802),
    "RK3": ((6.4, -5.7), (2.4, 2.0, 1.7), 30.0, 47803),     # fix round 2: 0.3 off RT1's tip (cut 0.28)
    "RK4": ((4.4, 3.6), (2.0, 1.8, 1.8), 10.0, 47804),
    "RK5": ((1.0, 5.6), (2.6, 2.2, 2.0), -25.0, 47805),
    "RK6": ((-2.6, 5.6), (1.6, 1.4, 1.2), 40.0, 47806),     # fix round 2: 0.4 off RT6's tip (cut 0.26)
}
PEBBLES = (((2.6, -6.0), 0.55, 47811), ((0.2, -6.6), 0.45, 47812), ((-6.0, 0.6), 0.5, 47813),
           ((5.6, 5.0), 0.45, 47814))
# name -> centre, leaves, height, spread, lime / mid / deep leaf counts (in that order: tallest first), leaf L:W, seed
CLUMPS = {
    "B1": ((-1.0, -5.9), 10, 3.2, 3.0, (0, 4, 6), 1.2, 47901),     # fix round 2: out of RT3 / RT4 / RK1
    "T1": ((-7.2, 0.4), 5, 3.0, 1.2, (3, 1, 1), 2.0, 47902),
    "T2a": ((6.9, -1.6), 5, 3.0, 1.3, (3, 1, 1), 2.0, 47903),
    "T2b": ((7.2, -3.0), 4, 2.8, 1.0, (2, 1, 1), 2.0, 47904),     # fix round 2: off RT1 (hub was in it)
    "T3": ((3.6, -5.4), 4, 2.6, 0.9, (2, 2, 0), 2.0, 47905),
    "T4": ((6.4, 3.0), 4, 2.9, 1.2, (2, 1, 1), 2.0, 47906),
    "T5": ((-4.8, 4.0), 4, 2.9, 1.3, (2, 1, 1), 2.0, 47907),
    "S1": ((-0.4, -6.9), 3, 1.0, 0.5, (3, 0, 0), 2.0, 47908),
    "S2": ((1.6, -6.7), 3, 1.1, 0.5, (3, 0, 0), 2.0, 47909),
    "S3": ((-6.0, -4.4), 3, 1.0, 0.5, (3, 0, 0), 2.0, 47910),
    "S4": ((2.4, 5.9), 3, 1.0, 0.5, (3, 0, 0), 2.0, 47911),
}
ROCK_RINGS = ((0.0, 0.92, 6), (0.28, 1.0, 6), (0.66, 0.84, 6), (1.0, 0.42, 4))
PEB_RINGS = ((0.0, 0.92, 5), (0.45, 1.0, 4), (1.0, 0.5, 3))
SINK_ROCK, SINK_PEB, SINK_HUB = 0.10, 0.04, 0.03


def _patch_outline(n=16):
    """Lobed outline (r per azimuth) of the sand patch: an ellipse 8.6 x 6.4 along 330 / 150 deg with lobes, let out
    wherever a rock, clump, pebble or root tip needs 0.35 of sand beyond it."""
    rng = random.Random(47600)
    ph = [rng.uniform(0, 6.28) for _ in range(3)]
    items = [(Vector(c), max(s[0], s[1]) / 2) for c, s, _, _ in ROCKS.values()]
    items += [(Vector(c), r) for c, r, _ in PEBBLES]
    items += [(Vector(c), 0.45 * R + 0.3) for c, _, _, R, _, _, _ in CLUMPS.values()]
    for spec in ROOTS:
        p, _ = _root_at(spec, spec[2] + 0.25)
        items.append((p.to_2d(), 0.25))
    out = []
    for k in range(n):
        th = 2 * math.pi * k / n
        rel = th - math.radians(330.0)
        r = 1.0 / math.sqrt((math.cos(rel) / 8.6) ** 2 + (math.sin(rel) / 7.6) ** 2)
        r *= 1.0 + 0.05 * math.sin(5 * th + ph[0]) + 0.035 * math.sin(3 * th + ph[1]) + 0.02 * math.sin(7 * th + ph[2])
        for c, rad in items:
            dist = c.length
            ang = math.atan2(c.y, c.x)
            dth = abs((th - ang + math.pi) % (2 * math.pi) - math.pi)
            half = math.asin(min(1.0, (rad + 0.35) / max(dist, 1e-3)))
            if dth < half + 2 * math.pi / n:
                # the crest (0.6 inside the outline) must reach past the item: its projection plus its radius + 0.7
                r = max(r, dist * math.cos(dth) + (rad + 0.7) * max(0.0, 1.0 - dth / (half + 2 * math.pi / n)) + 0.3)
        out.append(r)
    return out


def _near_field():
    segs = []
    for spec in ROOTS:
        p0 = _u(spec[1]) * 4.0
        p1, _ = _root_at(spec, _root_stations(spec)[1])
        p2, _ = _root_at(spec, spec[2] + 0.25)
        segs += [(p0.to_2d(), p1.to_2d(), 0.5 * spec[4]), (p1.to_2d(), p2.to_2d(), 0.3 * spec[4])]
    circles = [(Vector((0, 0)), 4.6)] + [(Vector(c), max(s[0], s[1]) / 2) for c, s, _, _ in ROCKS.values()]

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
    """The thin lobed sand patch: a flat crest at 0.15 out to 0.6 inside the outline, a bevel down to the outline at
    the ground, a flat underside at z 0. Sand-deep within 0.5 of the trunk, roots and rocks and on the bevel."""
    bm = a.bm
    R = _patch_outline()
    n = len(R)

    def ring(f_r, z, dr=0.0):
        return [bm.verts.new(_u(360.0 * k / n) * (R[k] * f_r + dr) + Vector((0, 0, z))) for k in range(n)]
    c_top = bm.verts.new(Vector((0, 0, PATCH_TOP)))
    r1 = ring(0.5, PATCH_TOP)
    r2 = ring(1.0, PATCH_TOP, -0.6)
    r3 = ring(1.0, 0.0)
    c_bot = bm.verts.new(Vector((0, 0, 0)))
    fs = [bm.faces.new((r1[k], r1[(k + 1) % n], c_top)) for k in range(n)]
    fs += _band(bm, r1, r2) + _band(bm, r2, r3)
    fs += [bm.faces.new((r3[(k + 1) % n], r3[k], c_bot)) for k in range(n)]
    bmesh.ops.triangulate(bm, faces=fs, quad_method="BEAUTY")
    vs = [c_top, c_bot] + r1 + r2 + r3
    allf = _faces(vs)
    _close(a, vs, allf, SAND)
    near = _near_field()
    for f in allf:
        c = f.calc_center_median()
        if c.z < PATCH_TOP - 1e-3 and c.z > 1e-3:
            f.material_index = a._mi(_mix(SAND, SAND_DEEP, 0.5))
        elif c.z > 1e-3 and near(c) < 0.5:
            f.material_index = a._mi(_mix(SAND, SAND_DEEP, 0.25))
    _mottle(a, allf, 0.03, 0.15, 47620)
    return vs


def _rock(a, c, size, yaw, seed, z0, rings=ROCK_RINGS):
    """A chunky angular rock: the hull of jittered ring stacks (broad flat base sunk into the sand, widest low, a
    shoulder, a flat sloping crown). rock base; rock_light on the top 30 %, rock_deep on the lowest 25 % (height)."""
    rng = random.Random(seed)
    W, D, H = size
    pts = m033._ring_pts(rng, rings, W / 2, D / 2, H, 0.08, lean=(rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15)))
    tilt = rng.uniform(-0.12, 0.12)
    for p in pts:                   # a sloping crown: the top rings tilt one way
        p.z += tilt * p.x * (p.z / H)
    m = Matrix.Rotation(math.radians(yaw), 3, "Z")
    pts = [m @ p + Vector((c[0], c[1], z0)) for p in pts]
    vs = m033._hull(a, pts, ROCK)
    fs = _faces(vs)
    for f in fs:
        h = (f.calc_center_median().z - z0) / H
        if h > 0.70:
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.5))
        elif h > 0.52:
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.25))
        elif h < 0.25:
            f.material_index = a._mi(_mix(ROCK, ROCK_DEEP, 0.25))
    _mottle(a, fs, 0.04, 0.4, seed)
    return vs


def rock(a, name):
    (cx, cy), size, yaw, seed = ROCKS[name]
    return _rock(a, (cx, cy), size, yaw, seed, PATCH_TOP - SINK_ROCK)


def pebble(a, c, s, seed):
    return _rock(a, c, (s, s * 0.85, s * 0.6), random.Random(seed).uniform(0, 180), seed, PATCH_TOP - SINK_PEB,
                 rings=PEB_RINGS)


def _rleaf(a, base, yaw, pitch, L, W, curl, key):
    """One broad round-tipped leaf (m044._dleaf: 10 tris, closed; a six-point outline - stem, two shoulders at 0.38 L,
    a three-point rounded tip - with a raised midrib point and a flat-ish underside) rising from `base` toward plan
    azimuth `yaw` at `pitch`, its face turned up and in, the tip arching out and down by `curl` (fix round 1: broad
    round-tipped leaves, not spiky agave stars)."""
    u = Vector((math.cos(yaw), math.sin(yaw), 0.0))
    cp, sp = math.cos(pitch), math.sin(pitch)
    d = u * cp + Vector((0, 0, sp))
    nrm = -u * sp + Vector((0, 0, cp))
    mid = Vector(base) + d * 0.48 * L
    return m044._dleaf(a, mid, d, nrm, L, W, key, cup=0.12, curl=curl, cam=0.1)


BURY = 0.05          # STAGES "no floating dressing": no dressing shell more than this inside the trunk, roots or rocks
BURY_PLACE = 0.03    # the placement guard keeps a margin under BURY, so a second measuring method agrees
BASE_INFO = {}       # fix round 2: what the base guard moved, shrank or dropped (filled by root_base_part)
_PDIRS = (Vector((1.0, 0.0131, 0.0217)).normalized(), Vector((-0.0173, 1.0, 0.0119)).normalized(),
          Vector((0.0109, -0.0207, 1.0)).normalized())


def _parity_in(tree, p):
    """Ray parity (m046): p is inside the closed shell if at least two of three skewed rays cross it an odd number of
    times. Unlike the nearest face's normal sign it is not fooled beside a concave root flank."""
    votes = 0
    for d in _PDIRS:
        n, q = 0, p.copy()
        for _ in range(64):
            h = tree.ray_cast(q, d, 1000.0)
            if h[0] is None:
                break
            n += 1
            q = h[0] + d * 1e-4
        votes += n % 2
    return votes >= 2


class _Solids:
    """Fix round 2: what the base dressing must not cut - the built trunk part (body and roots) and every rock and
    pebble - as closed shells, each a BVH with its bbox. depth() is the deepest vert or face centre of a piece inside
    any of them by ray parity, as the distance to that shell's surface (0 when clear)."""

    def __init__(self):
        self.items = []

    def add(self, cos, polys, name):
        cos = [Vector(c) for c in cos]
        lo = Vector((min(c.x for c in cos), min(c.y for c in cos), min(c.z for c in cos)))
        hi = Vector((max(c.x for c in cos), max(c.y for c in cos), max(c.z for c in cos)))
        self.items.append((name, lo, hi, BVHTree.FromPolygons(cos, polys)))

    def add_vs(self, vs, name):
        fs = _faces(vs)
        idx = {v: i for i, v in enumerate(vs)}
        self.add([v.co.copy() for v in vs], [[idx[v] for v in f.verts] for f in fs], name)

    def point(self, p, skip=()):
        worst, who = 0.0, None
        for name, lo, hi, t in self.items:
            if name in skip or not (lo.x - 1e-4 <= p.x <= hi.x + 1e-4 and lo.y - 1e-4 <= p.y <= hi.y + 1e-4 and
                                    lo.z - 1e-4 <= p.z <= hi.z + 1e-4):
                continue
            if _parity_in(t, p):
                d = t.find_nearest(p)[3]
                if d > worst:
                    worst, who = d, name
        return worst, who

    def depth(self, vs, skip=()):
        pts = [v.co.copy() for v in vs if v.is_valid] + [f.calc_center_median() for f in _faces(vs)]
        return max([self.point(p, skip)[0] for p in pts] or [0.0])


def _trunk_guard():
    """The base guard (fix round 2: a _Solids, not just the trunk's BVH): the built trunk part in the build frame, so
    the dressing keeps out of the trunk foot and roots; root_base_part adds each rock and pebble as it is built."""
    g = _Solids()
    t = bpy.data.objects.get(TRUNK_P)
    if t is not None and OFF in t:
        off = Vector(t[OFF])
        me = t.data
        g.add([v.co + off for v in me.vertices], [list(p.vertices) for p in me.polygons], "trunk")
    return g


def clump(a, name, guard=None):
    """A tuft of broad round-tipped upright leaves round a small closed 5-sided hub pyramid sunk 0.03 into the sand;
    each leaf's stem sits inside the hub. The tallest leaves lime, then mid green (tufts lime outside, sprigs all
    lime). The bush B1 is a dome instead (bush())."""
    if name == "B1":
        return bush(a, name, guard)
    (cx, cy), n, H, R, (n_lime, n_mid, n_deep), lw, seed = CLUMPS[name]
    rng = random.Random(seed)
    bm = a.bm
    z0 = PATCH_TOP - SINK_HUB
    hr, hh = (0.32, 0.36) if H > 1.5 else (0.18, 0.24)
    yaw0 = rng.uniform(0, 6.28)
    ring = [bm.verts.new(Vector((cx + math.cos(yaw0 + 2 * math.pi * k / 5) * hr,
                                 cy + math.sin(yaw0 + 2 * math.pi * k / 5) * hr, z0))) for k in range(5)]
    apex = bm.verts.new(Vector((cx, cy, z0 + hh)))
    fs = [bm.faces.new((ring[k], ring[(k + 1) % 5], apex)) for k in range(5)]
    fs.append(bm.faces.new(list(reversed(ring))))
    hub_vs = ring + [apex]
    _close(a, hub_vs, fs, _mix(PLANT_DEEP, BARK_DEEP, 0.25))
    info = BASE_INFO.setdefault(name, {"retried": 0, "dropped": 0})
    if guard is not None:
        info["hub_depth"] = round(guard.depth(hub_vs), 3)     # CLUMPS must seat every hub clear (bury_report checks)
    out = list(hub_vs)
    hs = []
    for k in range(n):
        tall = (k % 2 == 0)
        hs.append(H * (rng.uniform(0.85, 1.0) if tall else rng.uniform(0.55, 0.78)))
    order = sorted(range(n), key=lambda k: -hs[k])
    role = {}
    for i, k in enumerate(order):
        role[k] = PLANT if i < n_lime else PLANT_MID if i < n_lime + n_mid else PLANT_DEEP
    for k in range(n):
        yaw = yaw0 + 0.3 + 2 * math.pi * k / n + rng.uniform(-0.2, 0.2)
        tall = hs[k] > 0.8 * H
        pitch = math.radians(rng.uniform(58, 70) if tall else rng.uniform(42, 54))
        L = hs[k] / math.sin(pitch) * 1.12
        W = L / lw * rng.uniform(0.95, 1.08)
        curl = rng.uniform(0.08, 0.14)
        tint = 1.0 + rng.uniform(-0.04, 0.04)
        # fix round 2: a leaf that cuts the trunk, a root or a rock more than BURY stands up, then turns aside, then
        # shortens; if every try still cuts it is dropped, never kept (no rng is drawn here, so the clear leaves
        # stay as they were)
        up = min(math.radians(78), pitch + math.radians(16))
        tries = [(0.0, pitch, 1.0), (0.0, up, 0.9), (0.35, up, 0.9), (-0.35, up, 0.9), (0.7, up, 0.85),
                 (-0.7, up, 0.85), (0.0, math.radians(80), 0.75)]
        vs = None
        for i, (dy, p_, s_) in enumerate(tries):
            y_ = yaw + dy
            base = (cx + math.cos(y_) * hr * 0.35, cy + math.sin(y_) * hr * 0.35, z0 + hh * 0.3)
            vs = _rleaf(a, base, y_, p_, L * s_, W * s_, curl, role[k])
            if guard is None or guard.depth(vs) <= BURY_PLACE:
                info["retried"] += i > 0
                break
            for v in vs:
                bm.verts.remove(v)
            vs = None
        if vs is None:
            info["dropped"] += 1
            continue
        _tint(a, _faces(vs), tint)
        out += vs
    return out


# the dark bush's dome tiers, crown first (m044's dome bush, fix round 1): (polar angle from the dome's top in deg,
# count, azimuth phase in turns, length / R, width / length, outward flare of the leaf's axis, key)
BUSH_TIERS = ((24, 3, 0.0, 0.92, 0.88, 0.0, PLANT_MID),
              (60, 3, 0.5, 0.98, 0.88, 0.3, PLANT_DEEP),
              (90, 4, 0.25, 0.92, 0.85, 0.7, PLANT_DEEP))


def bush(a, name, guard=None):
    """The dark broad-leaf bush B1 as a rounded dome (m044.dome_bush on the flat patch): a hidden faceted heart dome
    clad in ten broad round-tipped leaves laid on it - a crown tier of three mid-green leaves, a middle tier of three
    and a skirt of four deep leaves drooping down its sides (tips curled in) - so the outline is a dome about 2 R
    across and H tall, never a star. A skirt leaf that would cut into the sand or a root climbs the dome until it
    clears; every leaf touches the heart (no floating leaf)."""
    (cx, cy), n, H, R, _roles, _lw, seed = CLUMPS[name]
    rng = random.Random(seed)
    z0 = PATCH_TOP - SINK_HUB
    C = Vector((cx, cy, z0 + 0.38 * H))
    rx, rz = 0.60 * R, 0.52 * H
    info = BASE_INFO.setdefault(name, {"retried": 0, "dropped": 0})
    for i in range(8):          # fix round 2: the heart must clear the trunk, roots and rocks too; else it narrows
        hvs = m040._dome_heart(a, C, rx, rz, z0 - 0.02, PLANT_DEEP, seed + 1, n=4)
        if guard is None or i == 7 or guard.depth(hvs) <= BURY_PLACE:
            break
        for v in hvs:
            a.bm.verts.remove(v)
        rx *= 0.93
    info["heart_rx"] = round(rx, 3)
    if guard is not None:
        info["heart_depth"] = round(guard.depth(hvs), 3)
    out = list(hvs)
    heart = m040._tree_of(hvs)
    off = rng.uniform(0, 2 * math.pi)

    def place(t_deg, phi, lf, wf, flare, key):
        t = math.radians(t_deg)
        u = Vector((math.cos(phi), math.sin(phi), 0.0))
        P = C + u * (rx * 1.02 * math.sin(t)) + Vector((0, 0, rz * math.cos(t) * (1.0 if t < math.pi / 2 else 0.8)))
        nrm = (u * (math.sin(t) / rx) + Vector((0, 0, math.cos(t) / rz))).normalized()
        down = (u * (rx * math.cos(t)) - Vector((0, 0, rz * math.sin(t)))).normalized()
        xdir = (down + u * flare).normalized()
        L = R * lf
        vs = m044._dleaf(a, P + xdir * 0.12 * L, xdir, nrm, L, L * wf, key, curl=0.12 if flare < 0.5 else 0.16)
        m040._touch(vs, heart)
        return vs

    for th, cnt, ph, lf, wf, flare, key in BUSH_TIERS:
        for k in range(cnt):
            phi = off + 2 * math.pi * (k + ph) / cnt + rng.uniform(-0.18, 0.18)
            t_deg = th + rng.uniform(-5, 5)
            lfk = lf * rng.uniform(0.94, 1.05)
            tint = 1.0 + rng.uniform(-0.04, 0.04)
            # fix round 2: shorten, then climb the dome 6 deg at a time (to 36 deg), then turn aside; a leaf that
            # still cuts the sand, the trunk, a root or a rock after every try is dropped, never kept (shortening
            # first keeps the skirt low over the heart's lower cone)
            tries = [(t_deg - 6.0 * i, phi, lfk * s) for i in range(7) for s in (1.0, 0.85, 0.72)]
            tries += [(t_deg - 6.0 * i, phi + s * 0.3, lfk * 0.85) for i in (0, 2, 4) for s in (1, -1)]
            tries += [(t_deg - 6.0 * i, phi + s * 0.6, lfk * 0.75) for i in (0, 2, 4) for s in (1, -1)]
            tries += [(t_deg - 6.0 * i, phi, lfk * 0.65) for i in (0, 2, 4)]
            # last, move it round the dome into open sand (a skirt leaf boxed in by a root and a rock re-grows on the
            # bush's free front, so the bush keeps its leaf count and its dark share)
            tries += [(t_deg - 6.0 * i, phi + s * a_, lfk * 0.85) for a_ in (0.9, 1.2) for i in (0, 2) for s in (1, -1)]
            vs = None
            for i, (t_, p_, l_) in enumerate(tries):
                vs = place(t_, p_, l_, wf, flare, key)
                dip = min(v.co.z for v in vs) - PATCH_TOP
                if dip > -0.04 and (guard is None or guard.depth(vs) <= BURY_PLACE):
                    info["retried"] += i > 0
                    break
                for v in vs:
                    a.bm.verts.remove(v)
                vs = None
            info.setdefault("leaves", []).append((th, round(math.degrees(phi) % 360), i if vs is not None else -1))
            if vs is None:
                info["dropped"] += 1
                continue
            _tint(a, _faces(vs), tint)
            out += vs
    return out


def root_base_part(a):
    BASE_INFO.clear()
    guard = _trunk_guard()
    patch(a)
    rk = {}
    for name in ROCKS:
        vs = rock(a, name)
        if guard.items and guard.items[0][0] == "trunk":
            rk[name] = round(guard.depth(vs), 3)        # rock into the roots (fix round 2: <= BURY)
        guard.add_vs(vs, name)
    BASE_INFO["rocks_in_trunk"] = rk
    for i, (c, s, seed) in enumerate(PEBBLES):
        guard.add_vs(pebble(a, c, s, seed), f"PB{i + 1}")
    for name in CLUMPS:
        clump(a, name, guard)


def hero_rest(a):
    """Everything but the trunk (which is unioned on its own and joined in): root base, then the five branch pieces."""
    root_base_part(a)
    for name in ("L", "R", "UR", "UL", "C"):
        branch_piece(a, name)


# ---- objects -------------------------------------------------------------------------------------------------------------
NOTES = {
    HERO: "Old Pine: a squat cloud-pad pine on a massive leaning planked orange-brown trunk forking into five elbowed "
          "limbs plugged into hexagonal sockets, each limb's twigs carrying a separate faceted lobe pad (sky between "
          "them); a hollow cut stub, a back stub and a knot; seven buttress roots on a sand patch with warm-grey "
          "rocks, a dark broad-leaf bush, lime tufts and sprigs. No VFX",
    TRUNK_P: "Forked Trunk: planked leaning body with a socket top, two fork stubs, two side sockets, a back hollow "
             "stub, a knot and seven buttress roots unioned in",
    CROWN_P: "Crown Canopy: the crown limb (hollow plug end, cut stub) with three twigs carrying the crown pad",
    TIER_P: "Canopy Tier: the upper-left limb (hollow plug end) with two twigs carrying its pad",
    ANGLED_P: "Branch (angled): the long elbowed lower-left limb (hollow plug end) with three twigs carrying its pad",
    BASE_P: "Rocks / Base: thin lobed sand patch, 6 angular warm-grey rocks, 4 pebbles, a dark broad-leaf bush, "
            "6 lime / green tufts and 4 sprigs",
}
COLLISION = {HERO: "precise", TRUNK_P: "hull", CROWN_P: "hull", TIER_P: "hull", ANGLED_P: "hull", BASE_P: "precise"}


def _new(name, fn, role, budget, temp=False):
    """Build fn into a fresh tagged kit object in the model's collection, keeping the build frame."""
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
    fn(a)
    o = a.finish(collection=M.coll(NUM, TITLE), mark_asset=not temp, origin=None)
    K.drop_unused_slots(o)
    if "kit_part" in o.data.attributes:
        o.data.attributes.remove(o.data.attributes["kit_part"])
    if not temp:
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
    SOCK.clear()
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


def _make_shells(name, fn, role="part", budget=1000, temp=False):
    o = _new(name, fn, role, budget, temp=temp)
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


# ---- checks ----------------------------------------------------------------------------------------------------------------
def _keys(o):
    return [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]


def _kind(ks, nf):
    if any("plant" in k for k in ks):
        return "hub" if nf in (8, 16) else "leaf"
    if any("leaf" in k for k in ks):
        return "lobe"
    if any("sand" in k for k in ks):
        return "patch"
    if any("rock" in k for k in ks):
        return "rock"
    if any("bark" in k for k in ks):
        return "bark"
    return "other"


def _shells(o):
    """bmesh of o plus per-shell face lists, keys and kinds (bark shells split into trunk / limb / twig / stub)."""
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
        ks = {keys[f.material_index] for f in fs}
        kinds.append(_kind(ks, len(fs)))
    bark = [k for k in range(n) if kinds[k] == "bark"]
    if bark:
        big = max(bark, key=lambda k: len(groups[k]))
        for k in bark:
            nf = len(groups[k])
            has_hollow = any(keys[f.material_index] == BARK_DEEP for f in groups[k])
            kinds[k] = ("trunk" if k == big and nf > 150 else "limb" if nf > 40 and has_hollow and nf > 50
                        else "stub" if has_hollow else "twig")
    return bm, ids, n, groups, kinds


def shells_report(o):
    """Per shell: kind, tris, non-manifold edges and verts, boundary edges, winding errors (manifold edges whose two
    faces don't run the same way round), self-intersecting face pairs inside the shell, signed volume."""
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
                    "self_hits": hits, "volume": round(vol, 4), "zmin": round(min(v.co.z for v in vs), 3)})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating dressing (STAGES): per shell, whether it touches another shell (triangles intersect, or a vertex
    within `tol` of another shell's surface) or the ground. Anchors: shells on the ground (the hero, the root base),
    else the trunk (trunk part) or the limb (a branch piece). Returns the floating count, the worst gap, shells with
    no chain of contact to an anchor, and the plug clearances (limb to trunk)."""
    bm, ids, n, groups, kinds = _shells(o)
    fsh = [ids[f.index] for f in bm.faces]
    vsh = {}
    for f in bm.faces:
        for v in f.verts:
            vsh[v.index] = fsh[f.index]
    tree = BVHTree.FromBMesh(bm)
    zmin = [1e9] * n
    for v in bm.verts:
        if v.index in vsh:
            zmin[vsh[v.index]] = min(zmin[vsh[v.index]], v.co.z)
    z0 = min(zmin)
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
    for kk in pairs:            # BVHTree.overlap pairs are triangles that really intersect
        near[kk] = 0.0
    gap = [1e9] * n
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    if "patch" in kinds:
        ground = {k for k in range(n) if zmin[k] - z0 <= tol}
    elif "trunk" in kinds:
        ground = {k for k in range(n) if kinds[k] == "trunk"}
    else:
        ground = {k for k in range(n) if kinds[k] == "limb"}
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
        return n - len(seen)
    floating = [k for k in range(n) if gap[k] > tol]
    plugs = sorted(round(d, 4) for (a_, b_), d in near.items() if {kinds[a_], kinds[b_]} == {"limb", "trunk"})
    res = {"shells": n, "floating": len(floating), "floating_kinds": sorted({kinds[k] for k in floating}),
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "max_gap_all": round(max(gap[k] for k in range(n)), 3),
           "unchained": chained(tol), "unchained_chain_tol": chained(chain_tol), "plug_gaps": plugs,
           "kinds": {k: kinds.count(k) for k in sorted(set(kinds))}}
    bm.free()
    return res


def bury_report(o):
    """Fix round 2 (STAGES "no floating dressing", m046.bury_report): on a finished object, every plant shell (leaf,
    hub, bush heart) tested by ray parity against the trunk shell (body and roots) and each rock and pebble shell;
    depth = the distance from its deepest vert or face centre inside to that shell's surface. An object without a
    trunk shell (the root base) is tested against the built trunk part brought into its frame. Also each rock against
    the trunk (nestled rocks: <= BURY)."""
    bm, ids, n, groups, kinds = _shells(o)
    sol = _Solids()
    rocks = []
    for k in range(n):
        if kinds[k] in ("trunk", "rock"):
            vs = list({v for f in groups[k] for v in f.verts})
            vi = {v: i for i, v in enumerate(vs)}
            sol.add([v.co for v in vs], [[vi[v] for v in f.verts] for f in groups[k]], f"{kinds[k]}{k}")
            if kinds[k] == "rock":
                rocks.append(k)
    t = bpy.data.objects.get(TRUNK_P)
    if "trunk" not in kinds and t is not None and o is not t and OFF in t and OFF in o:
        sh = Vector(t[OFF]) - Vector(o[OFF])
        sol.add([v.co + sh for v in t.data.vertices], [list(p.vertices) for p in t.data.polygons], "trunk_part")
    off = Vector(o[OFF]) if OFF in o else Vector()
    res = []
    plants = 0
    for k in range(n):
        if kinds[k] not in ("leaf", "hub"):
            continue
        plants += 1
        fs = groups[k]
        pts = list({v.co.copy().freeze() for f in fs for v in f.verts}) + [f.calc_center_median() for f in fs]
        d, who = max((sol.point(Vector(p)) for p in pts), key=lambda r: r[0])
        if d > 0.0:
            c = sum((f.calc_center_median() for f in fs), Vector()) / len(fs) + off
            res.append((round(d, 3), kinds[k], who, [round(x, 2) for x in c]))
    rk = []
    for k in rocks:
        fs = groups[k]
        pts = list({v.co.copy().freeze() for f in fs for v in f.verts}) + [f.calc_center_median() for f in fs]
        d = max(sol.point(Vector(p), skip=[f"rock{j}" for j in rocks])[0] for p in pts)
        if d > 0.0:
            c = sum((f.calc_center_median() for f in fs), Vector()) / len(fs) + off
            rk.append((round(d, 3), [round(x, 2) for x in c]))
    bm.free()
    res.sort(key=lambda r: -r[0])
    rk.sort(key=lambda r: -r[0])
    return {"plant_shells": plants, "solids": len(sol.items), "over_0.05": sum(1 for r in res if r[0] > BURY),
            "max": res[0][0] if res else 0.0, "worst": res[:6],
            "rocks_in_trunk_over_0.05": sum(1 for r in rk if r[0] > BURY), "rocks_in_trunk": rk[:6]}


def plug_report(h):
    """Each limb's plug (its first two hex rings, inside the socket hole) against the trunk shell of h: the nearest
    distance from its corners to the bark (the 0.02 clearance; 0.005-0.03 expected) and whether any corner lies inside
    the trunk's solid (it must not: the plug sits in the hole's cavity)."""
    bm, ids, n, groups, kinds = _shells(h)
    k = kinds.index("trunk")
    fs = groups[k]
    vs = list({v for f in fs for v in f.verts})
    vi = {v: i for i, v in enumerate(vs)}
    off = Vector(h[OFF])
    tree = BVHTree.FromPolygons([v.co + off for v in vs], [[vi[v] for v in f.verts] for f in fs])
    bm.free()
    out = {}
    for name, info in LIMB_INFO.items():
        ds = [tree.find_nearest(p)[3] for p in info["plug"]]
        inside = sum(1 for p in info["plug"] if m042._inside(tree, p))
        out[name] = {"min": round(min(ds), 4), "max": round(max(ds), 4), "inside_solid": inside}
    return out


LIMB_VIEWS = {"front": (0, 6), "rear": (180, 6), "f34": (25, 10), "r34": (205, 11)}


def limb_visibility(h, views=LIMB_VIEWS, step=0.1):
    """Fix round 1 check: per limb and view, how much of the limb (shoulder -> twig fork) and of its twigs is seen,
    i.e. not hidden behind the pads, the trunk or the base (a ray from each centreline sample toward the camera,
    against every shell but the limbs, twigs and stub). Returns {limb: {view: (visible 3D length, visible length on
    screen, total length)}, ..., "twigs": {limb: {view: twigs at least half seen}}}."""
    bm, ids, n, groups, kinds = _shells(h)
    off = Vector(h[OFF])
    keep = [f for k in range(n) if kinds[k] not in ("limb", "twig", "stub") for f in groups[k]]
    vs = list({v for f in keep for v in f.verts})
    vi = {v: i for i, v in enumerate(vs)}
    tree = BVHTree.FromPolygons([v.co + off for v in vs], [[vi[v] for v in f.verts] for f in keep])
    bm.free()

    def cam(az, el):
        a_, e_ = math.radians(az), math.radians(el)
        return Vector((math.sin(a_) * math.cos(e_), -math.cos(a_) * math.cos(e_), math.sin(e_)))

    def seen(p, d):
        hit = tree.ray_cast(p, d, 200.0)
        return hit[0] is None
    out = {"twigs": {}}
    for name, info in LIMB_INFO.items():
        pts = info["pts"][2:]
        row = {}
        tw = {}
        for vn, (az, el) in views.items():
            d = cam(az, el)
            vis = scr = tot = 0.0
            for p, q in zip(pts, pts[1:]):
                seg = q - p
                m = max(1, int(seg.length / step))
                for i in range(m):
                    c = p + seg * ((i + 0.5) / m)
                    ln = seg.length / m
                    tot += ln
                    if seen(c, d):
                        vis += ln
                        scr += (seg - d * seg.dot(d)).length / m
            row[vn] = (round(vis, 2), round(scr, 2), round(tot, 2))
            nt = 0
            for base, tip in info.get("twigs", []):
                ss = [seen(base + (tip - base) * ((i + 0.5) / 8), d) for i in range(8)]
                nt += sum(ss) >= 4
            tw[vn] = nt
        out[name] = row
        out["twigs"][name] = tw
    return out


def lobe_report(o):
    """Per pad-lobe shell: height : width (z extent over the larger plan extent, as the round-1 verifier measured)."""
    bm, ids, n, groups, kinds = _shells(o)
    hw = []
    for k in range(n):
        if kinds[k] != "lobe":
            continue
        vs = list({v for f in groups[k] for v in f.verts})
        xs, ys, zs = ([v.co[i] for v in vs] for i in range(3))
        hw.append((max(zs) - min(zs)) / max(max(xs) - min(xs), max(ys) - min(ys)))
    bm.free()
    hw.sort()
    return {"lobes": len(hw), "hw_median": round(hw[len(hw) // 2], 3) if hw else None,
            "hw_min": round(hw[0], 3) if hw else None, "hw_max": round(hw[-1], 3) if hw else None,
            "per_pad": {k: v["lobes"] for k, v in PAD_INFO.items()}}


def socket_report():
    """Each socket rim's clearance above the bark (all six rim corners outside the body) and each plug's seat."""
    out = {}
    for k, s in SOCK.items():
        out[k] = {"F": [round(x, 2) for x in s["F"]], "bark_t": round(s.get("t") or 0.0, 2)}
    return out


# ---- build -------------------------------------------------------------------------------------------------------------------
PARTS = ((CROWN_P, crown_part), (TIER_P, tier_part), (ANGLED_P, angled_part), (BASE_P, root_base_part))
TARGET_SIZE = ((20.3, 1.0), (15.0, 2.0), (20.0, 0.4))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m047_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", "GnarledPine"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build(render=True, parts=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    m033.UNION_RETRIES.clear()
    palette()
    PAD_INFO.clear()
    LIMB_INFO.clear()
    objs, log = {}, {}
    trunk, log[TRUNK_P] = _make_trunk()
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make_shells(name, fn)
    objs[TRUNK_P] = trunk
    h, log["hero"] = _make_hero(trunk)
    log["union_retries"] = list(m033.UNION_RETRIES)
    log["sockets"] = socket_report()
    _cleanup_tmp()
    order = [h] + [objs[n] for n in (TRUNK_P, CROWN_P, TIER_P, ANGLED_P, BASE_P) if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    audits = [M.audit(o) for o in order]
    thin = {o.name: m012._thin(o, 2.0) for o in order}
    shells = {o.name: shells_report(o) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = 3800 if o is h else 1000
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
            problems.append(f"{n_}: {c['floating']} shells touch nothing within {CONTACT}, {c['unchained']} have no "
                            f"chain of contact to an anchor")
    bury = {o.name: bury_report(o) for o in order if o.name in (HERO, BASE_P)}
    for n_, b in bury.items():
        if b["over_0.05"]:
            problems.append(f"{n_}: {b['over_0.05']} plant shells more than {BURY} inside the trunk, roots or rocks "
                            f"(worst {b['worst'][:3]})")
        if b["rocks_in_trunk_over_0.05"]:
            problems.append(f"{n_}: {b['rocks_in_trunk_over_0.05']} rocks more than {BURY} into the roots "
                            f"({b['rocks_in_trunk'][:3]})")
    if len(shells[TRUNK_P]) != 1:
        problems.append(f"{TRUNK_P}: {len(shells[TRUNK_P])} shells, expected 1")
    if sum(1 for s in shells[HERO] if s["kind"] == "trunk") != 1:
        problems.append(f"{HERO}: {sum(1 for s in shells[HERO] if s['kind'] == 'trunk')} trunk shells, expected 1")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 12: none)")
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
           "hero_shells": kinds, "contact": contact, "bury": bury, "base_info": dict(BASE_INFO), "thin": thin, "log": log, "problems": problems, "uv": uv,
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders -----------------------------------------------------------------------------------------------------------------
# decision 10: f34_sheet (+25, 10) governs; r34_sheet (205, 11); front / side / rear_sheet at e 6; kit top and underside;
# floor hidden and a 3x lens on the *_sheet shots (m033._long_lens)
SHEET_VIEWS = {"f34_sheet": (25, 10), "r34_sheet": (205, 11), "front_sheet": (0, 6), "side_sheet": (90, 6),
               "rear_sheet": (180, 6), "top_sheet": (0, 89)}
VIEW_NAMES = ("front", "side", "rear", "top", "underside")
PARTS_SHOT = (20, 15)
PARTS_SHOT_BRANCH = (33, 6)    # fix round 1: the branch pieces side-on and low, so each limb, its elbow and its twigs show
# exploded: each piece moved along its socket axis (branch pieces) or lifted (the trunk), like the sheet's exploded
EXPLODE = {BASE_P: (0, 0, 0), TRUNK_P: (0, 0, 2.5)}
EXPLODE_BRANCH = {"C": 4.5, "UL": 4.0, "UR": 4.0, "L": 4.0, "R": 4.0}


def _branch_temp(name):
    fn = {"UR": ur_part, "R": r_part}[name]
    o, _ = _make_shells(PFX + "piece_" + name, fn, temp=True)
    return o


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded Construction: the base, the trunk lifted, each of the
    five branch pieces drawn out of its socket along the socket axis (the UR and R pieces are built on the fly)."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []
    x0 = objs[0].location.x + 80
    y0 = objs[0].location.y
    trunk_lift = Vector(EXPLODE[TRUNK_P])
    pieces = {"C": by.get(CROWN_P), "UL": by.get(TIER_P), "L": by.get(ANGLED_P)}
    temps = []
    for nm in ("UR", "R"):
        t = _branch_temp(nm)
        temps.append(t)
        pieces[nm] = t
    for name, o in ((BASE_P, by.get(BASE_P)), (TRUNK_P, by.get(TRUNK_P))):
        if o is None:
            continue
        c = bpy.data.objects.new(f"{PFX}expl_{name}", o.data)
        coll.objects.link(c)
        c.matrix_world = Matrix.Translation((x0, y0, 0)) @ Matrix.Translation(Vector(EXPLODE[name])) \
            @ Matrix.Translation(Vector(o[OFF]))
        shown.append(c)
    for nm, o in pieces.items():
        if o is None:
            continue
        s = SOCK[LIMBS[nm]["sock"]]
        dv = s["d"] * EXPLODE_BRANCH[nm] + trunk_lift
        c = bpy.data.objects.new(f"{PFX}expl_{nm}", o.data)
        coll.objects.link(c)
        c.matrix_world = Matrix.Translation((x0, y0, 0)) @ Matrix.Translation(dv) @ Matrix.Translation(Vector(o[OFF]))
        shown.append(c)
    bpy.context.view_layer.update()
    return shown, temps


def _scale_marker(h, at):
    """A 5.5-stud character stand-in at build-frame point `at` (under the R pad)."""
    a = K.fk().Asset(PFX + "char", "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=ROCK_DEEP, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=ROCK_DEEP, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=ROCK_DEEP, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
    c.location = off @ Vector(at)
    bpy.context.view_layer.update()
    return c


def render_views(objs, close=True):
    h = objs[0]
    shown, temps = _exploded(objs) if len(objs) > 1 else ([], [])
    marker = _scale_marker(h, (8.4, -4.6, PATCH_TOP))
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        extra["front34"] = ([h], 25, 12)
        extra["rear34"] = ([h], 205, 12)
        for o in objs[1:]:
            shot = PARTS_SHOT_BRANCH if o.name in (CROWN_P, TIER_P, ANGLED_P) else PARTS_SHOT
            extra["part_" + o.name.replace("GnarledPine", "").lower()] = ([o], *shot)
        if shown:
            extra["exploded"] = (shown, 0, 20)
        extra["scale"] = ([h, marker], 20, 6)
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
        for o in shown + [marker]:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if o is marker and me.users == 0:
                bpy.data.meshes.remove(me)
        for t in temps:
            me = t.data
            bpy.data.objects.remove(t, do_unlink=True)
            if me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def render_close_ups(objs):
    """join_cu (the trunk part's right fork and leader-top sockets from above, against close-up 1), plug_cu (the angled branch's plug end),
    base_cu (the hero's trunk foot, close-up 2), foliage_cu (the angled branch piece's twigs into its pad, close-up 3),
    stub_cu (the crown limb's cut stub, the knot), back_cu (the back stub)."""
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    by = {o.name: o for o in objs}
    h = objs[0]
    out = {}

    def at(o, p):
        return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)
    if TRUNK_P in by:
        t = by[TRUNK_P]
        out["join_cu"] = m033.render_close([t], f"{d}/join_cu.png", 80, 45, at(t, SOCK["rf"]["F"]), 1.8)
    if ANGLED_P in by:
        b = by[ANGLED_P]
        p0 = LIMB_INFO["L"]["pts"][0]
        out["plug_cu"] = m033.render_close([b], f"{d}/plug_cu.png", 160, 10, at(b, p0), 1.6)
        pts = LIMB_INFO["L"]["pts"]
        # side-on to the L limb (plan direction ~213 deg) from a little below: the limb rising into its twigs and
        # the pad's flat underside, like close-up 3
        out["foliage_cu"] = m033.render_close([b], f"{d}/foliage_cu.png", 33, -6, at(b, pts[-1] + Vector((0.6, 0, 0.9))),
                                              3.4)
    out["base_cu"] = m033.render_close([h], f"{d}/base_cu.png", 15, 18, at(h, (0.5, -2.0, 2.0)), 6.5)
    out["stub_cu"] = m033.render_close([h], f"{d}/stub_cu.png", 25, 8, at(h, (1.8, 0.0, 12.5)), 3.6)
    out["back_cu"] = m033.render_close([h], f"{d}/back_cu.png", 200, 10, at(h, SOCK["back"]["F"]), 2.4)
    return out


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
    PAD_INFO.clear()
    LIMB_INFO.clear()
    trunk, lt = _make_trunk()
    h, lg = _make_hero(trunk)
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n in (TRUNK_P, CROWN_P, TIER_P, ANGLED_P, BASE_P)
                          if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals")}, "log": lg, "trunk": lt,
            "sockets": socket_report()}
