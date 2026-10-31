"""054 Broadleaf Tree (references/054.png): a big round-crowned deciduous tree. A massive orange-brown trunk of six
twisted rope strands (waist 4.7, root flare, twisting about 67 deg CCW foot to top) flares into six split-toed roots
and, at the crotch, carries three bosses and a top cap. Four plug-in branch modules (BM1 the big Y to the low left
clump with a bare forked lower arm; BM2 the short upright to the front-left clump; BM3 the top V leader to the back
crown clump; BM4 the riser to the front-right clump with a side branch to the low right clump and a bare fork) feed
five leaf clumps, each a dark core dome clad in overlapping chunky lobed leaf cards toned light -> mid -> dark by
height in the clump. Round the foot: pale grey rocks, lime moss pads and tall pointed lime grass tufts.

    import importlib, kit_models, m054; importlib.reload(kit_models); importlib.reload(m054); m054.build()

Build frame: studs, front -Y, +X right, ground z 0, trunk axis at (0, 0). Every object ends with its origin at its bbox
bottom centre; o["m054_offset"] is that origin in the build frame. Names (spec 8): ShadeTree (hero), ShadeTreeTrunkCore,
ShadeTreeBranchModule (BM1), ShadeTreeLeafClump (FL), ShadeTreeRootBase. Pegs and socket holes only on the parts
(decision 5). Colour is painted by position and role (never by facing). Stages 5-6: none (the sheet shows no effect).
See art/blender/renders/models/M054/M054_spec.md.
"""
import math
import random
import time

import bmesh
import bpy
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M
import m012
import m033
import m047

NUM, TITLE, SHEET = 54, "Broadleaf Tree", "M054"
OFF = "m054_offset"
PFX = "_m054_"
HERO = "ShadeTree"
TRUNK_P, BRANCH_P, CLUMP_P, BASE_P = ("ShadeTreeTrunkCore", "ShadeTreeBranchModule", "ShadeTreeLeafClump",
                                      "ShadeTreeRootBase")

LEAF_L, LEAF_M, LEAF_D = "m054_leaf_light", "m054_leaf_mid", "m054_leaf_dark"
BARK, BARK_L, BARK_D, HOLLOW = "m054_bark", "m054_bark_light", "m054_bark_deep", "m054_hollow"
ROCK, ROCK_L, ROCK_D = "m054_rock", "m054_rock_light", "m054_rock_deep"
MOSS, GRASS, GRASS_D = "m054_moss", "m054_grass", "m054_grass_deep"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
Z = Vector((0.0, 0.0, 1.0))

# key -> (hex, roughness, low specular). Stage 4 (M054_spec.md "Stage 4") writes the calibrated values here.
PALETTE = {
    LEAF_L: ("#AEB805", 0.8, True),
    LEAF_M: ("#74A623", 0.85, True),
    LEAF_D: ("#3D702D", 0.9, True),
    BARK: ("#A66B32", 0.9, False),
    BARK_L: ("#D1944C", 0.85, False),
    BARK_D: ("#6A3E1D", 0.95, False),
    HOLLOW: ("#241003", 1.0, False),
    ROCK: ("#9E948A", 0.85, False),
    ROCK_L: ("#ADA398", 0.85, False),
    ROCK_D: ("#7A746E", 0.9, False),
    MOSS: ("#D6C411", 0.95, True),
    GRASS: ("#9BA60B", 0.85, True),
    GRASS_D: ("#436813", 0.85, True),
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions or swatches), K.sample kinds
TARGETS = {LEAF_L: ((0xCD, 0xE2, 0x09), "vivid"), LEAF_M: ((0x70, 0xA8, 0x1F), "green"),
           LEAF_D: ((0x47, 0x85, 0x2D), "green"), BARK: ((0xB4, 0x6E, 0x37), "brown"),
           BARK_L: ((0xF1, 0xA4, 0x52), "brown"), BARK_D: ((0x7A, 0x46, 0x26), "brown"),
           HOLLOW: ((0x2E, 0x18, 0x06), "all"), ROCK: ((0xC4, 0xB4, 0xA2), "all"),
           ROCK_L: ((0xD5, 0xC4, 0xB2), "all"), ROCK_D: ((0x99, 0x8D, 0x86), "all"),
           MOSS: ((0xD2, 0xC9, 0x0D), "vivid"), GRASS: ((0xC4, 0xCC, 0x0E), "vivid"),
           GRASS_D: ((0x4E, 0x7A, 0x14), "green")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    for m in list(bpy.data.materials):            # mixed keys from an earlier build: re-mix from the parents
        key = m.name[3:] if m.name.startswith("FB_m054_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = "m054_" + tail
            if k1 in PALETTE and k2 in PALETTE and pct.isdigit():
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


# ---- small helpers ----------------------------------------------------------------------------------------------------
_faces = m033._faces
_mottle = m033._mottle
_u = m047._u
_basis = m047._basis
_ring = m047._ring
_band = m047._band
_zip = m047._zip
_frames = m047._frames


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


def _close(a, vs, fs, key):
    bmesh.ops.recalc_face_normals(a.bm, faces=[f for f in fs if f.is_valid])
    a._finish(vs, key, tint=1.0)


def _dir(rise, az):
    """Unit axis at plan azimuth az (deg), rising `rise` deg above horizontal."""
    r, p = math.radians(rise), math.radians(az)
    return Vector((math.cos(r) * math.cos(p), math.cos(r) * math.sin(p), math.sin(r)))


PIT_SIZE = 0.3          # bark pits are fixed dark squares of this side (spec 2.2: 0.25-0.35), not slots (m8)


def _quad_axes(f):
    q = [v.co for v in f.verts]
    u = (q[1] - q[0]) + (q[2] - q[3])
    u = (u - f.normal * u.dot(f.normal)).normalized()
    return u, f.normal.cross(u).normalized()


def _quad_fits(f, size):
    """A quad facet that holds a size x size square with a 0.06 margin round it."""
    if len(f.verts) != 4:
        return False
    u, v = _quad_axes(f)
    c = f.calc_center_median()
    for e in f.edges:          # distance from the centre to each edge line, in the face plane
        p0, p1 = e.verts[0].co, e.verts[1].co
        d = (p1 - p0).normalized()
        off = (c - p0) - d * (c - p0).dot(d)
        if off.length < size / 2 * math.sqrt(2) + 0.06:
            return False
    return True


def _pit(a, faces, target, size=PIT_SIZE, depth=0.045):
    """A bark pit (fix round 1): on the quad facet nearest `target` that holds it, a fixed size x size square sunk
    `depth` (hollow), joined to the facet's rim by four sloped faces that keep the facet's own colour."""
    cand = [f for f in faces if f.is_valid and _quad_fits(f, size)]
    if not cand:
        return None
    f = min(cand, key=lambda g: (g.calc_center_median() - Vector(target)).length)
    key_i = f.material_index
    c0, n = f.calc_center_median(), f.normal.copy()
    u, v = _quad_axes(f)
    r = bmesh.ops.inset_individual(a.bm, faces=[f], thickness=0.05, depth=-depth, use_even_offset=True)
    corners = [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)]       # CCW about n
    inner = list(f.verts)
    a0 = math.atan2((inner[0].co - c0).dot(v), (inner[0].co - c0).dot(u))
    # the inner loop runs CCW about n like the facet: give its verts the square's corners in the same cyclic order,
    # starting at the corner nearest the first vert
    start = min(range(4), key=lambda k: abs(math.atan2(math.sin(a0 - math.atan2(corners[k][1], corners[k][0])),
                                                       math.cos(a0 - math.atan2(corners[k][1], corners[k][0])))))
    for i, p in enumerate(inner):
        su, sv = corners[(start + i) % 4]
        p.co = c0 - n * depth + (u * su + v * sv) * (size / 2)
    _paint(a, [f], HOLLOW)
    for g in r["faces"]:
        g.material_index = key_i
    return f


# ---- tubes (limbs, arms, tines, twigs, bosses, pegs) ------------------------------------------------------------------
def tube(a, pts, radii, n, u0=None, rot=0.0, start="flat", end="flat", key=BARK, hole=(0.4, 0.3), cap_key=BARK_L):
    """A closed n-sided tube along a polyline (parallel-transported frames, rings mitred on the bisector). Caps:
    "flat" (cut face, cap_key), "socket" (cut rim round a walled hole of radius hole[0] x ring radius, hole[1] deep,
    hollow). Returns (verts, side faces, caps {"cut": [...], "hole": [...]})."""
    bm = a.bm
    pts = [Vector(p) for p in pts]
    fr = _frames(pts, u0 if u0 is not None else _basis(pts[1] - pts[0])[0])
    rings = [[bm.verts.new(q) for q in _ring(p, u, v, r, n, rot)] for p, r, (t, u, v) in zip(pts, radii, fr)]
    side = []
    for i in range(len(rings) - 1):
        side += _band(bm, rings[i], rings[i + 1])
    vs = [v for r in rings for v in r]
    caps = {"cut": [], "hole": []}
    for which, ring, c, d, (t, u, v), r0 in (("s", rings[0], pts[0], -fr[0][0], fr[0], radii[0]),
                                            ("e", rings[-1], pts[-1], fr[-1][0], fr[-1], radii[-1])):
        kind = start if which == "s" else end
        if kind == "socket":
            hn = hole[2] if len(hole) > 2 else n
            inner = [bm.verts.new(q) for q in _ring(c, u, v, hole[0] * r0, hn, rot + 0.3)]
            deep = [bm.verts.new(q - d * hole[1]) for q in _ring(c, u, v, hole[0] * r0, hn, rot + 0.3)]
            caps["cut"] += _zip(bm, ring, inner, c, u, v)
            caps["hole"] += _band(bm, inner, deep) + [bm.faces.new(deep)]
            vs += inner + deep
        else:
            caps["cut"].append(bm.faces.new(ring if which == "e" else list(reversed(ring))))
    _close(a, vs, side + caps["cut"] + caps["hole"], key)
    _paint(a, caps["cut"], cap_key)
    _paint(a, caps["hole"], HOLLOW)
    return vs, side, caps


def _ell_prism(a, A, F, d, ru, rv, n, key, rot=0.0):
    """A closed elliptical n-gon prism from A to F along d (semi-axes ru across, rv up the trunk); flat caps."""
    bm = a.bm
    u = Z.cross(d)
    u = u.normalized() if u.length > 1e-6 else Vector((1, 0, 0))
    v = d.cross(u).normalized()

    def ring(c):
        return [bm.verts.new(c + u * (ru * math.cos(rot + 2 * math.pi * k / n)) + v * (rv * math.sin(rot + 2 * math.pi * k / n)))
                for k in range(n)]
    r0, r1 = ring(A), ring(F)
    fs = _band(bm, r0, r1) + [bm.faces.new(list(reversed(r0))), bm.faces.new(r1)]
    _close(a, r0 + r1, fs, key)
    return r0 + r1, fs


# ---- prisms with a flat bottom (roots, root stubs, toes) --------------------------------------------------------------
ROOT_PROF = ((-0.45, 0.0), (0.45, 0.0), (0.5, 0.44), (0.15, 1.0), (-0.15, 0.97), (-0.5, 0.46))
TOE_PROF = ((-0.5, 0.0), (0.5, 0.0), (0.3, 1.0), (-0.3, 1.0))


def prism(a, path, secs, prof, key=BARK, start="flat", end="flat", hole=(0.42, 0.3), drop=None):
    """A closed prism along a bottom-centre path: at each station the section prof (fractions of (w, h), origin at
    the bottom centre) in the plane across the path (lateral axis horizontal). secs = [(w, h)] per station; drop =
    per-station shift of the whole section along its up axis (to make a station 'wider all round'). Returns
    (verts, rings, side faces, caps)."""
    bm = a.bm
    path = [Vector(p) for p in path]
    n = len(path)
    rings = []
    frames = []
    for i, P in enumerate(path):
        if i == 0:
            t = (path[1] - path[0]).normalized()
        elif i == n - 1:
            t = (path[-1] - path[-2]).normalized()
        else:
            t = ((path[i] - path[i - 1]).normalized() + (path[i + 1] - path[i]).normalized()).normalized()
        s = t.cross(Z)
        s = s.normalized() if s.length > 1e-6 else Vector((1, 0, 0))
        u = s.cross(t).normalized()
        w, h = secs[i]
        dz = (drop[i] if drop else 0.0)
        rings.append([bm.verts.new(P + s * (fx * w) + u * (fy * h - dz)) for fx, fy in prof])
        frames.append((t, s, u))
    side = []
    for i in range(n - 1):
        side += _band(bm, rings[i], rings[i + 1])
    vs = [v for r in rings for v in r]
    caps = {"cut": [], "hole": []}
    for which, ring, (t, s, u) in (("s", rings[0], frames[0]), ("e", rings[-1], frames[-1])):
        kind = start if which == "s" else end
        dirn = t if which == "e" else -t
        if kind == "socket":         # a square hole in the section's face (4 verts zipped to the section)
            c = sum((v.co for v in ring), Vector()) / len(ring)
            rad = hole[0] * min((v.co - c).length for v in ring)
            pts_ = [c + s * (math.cos(0.785 + k * 1.5708) * rad) + u * (math.sin(0.785 + k * 1.5708) * rad)
                    for k in range(4)]
            inner = [bm.verts.new(q) for q in pts_]
            deep = [bm.verts.new(q - dirn * hole[1]) for q in pts_]
            caps["cut"] += _zip(bm, ring, inner, c, s, u)
            caps["hole"] += _band(bm, inner, deep) + [bm.faces.new(deep)]
            vs += inner + deep
        else:
            caps["cut"].append(bm.faces.new(ring if which == "e" else list(reversed(ring))))
    _close(a, vs, side + caps["cut"] + caps["hole"], key)
    _paint(a, caps["hole"], HOLLOW)
    return vs, rings, side, caps


# ---- trunk core (spec 2.2) --------------------------------------------------------------------------------------------
# (z, crest diameter, centre x, twist deg)
RINGS = ((0.0, 6.6, 0.0, 0.0), (3.0, 5.6, 0.0, 16.0),
         (6.0, 4.9, 0.0, 32.0), (7.0, 4.7, 0.0, 37.0), (9.4, 4.7, 0.15, 51.0),
         (10.6, 3.8, 0.35, 58.0), (12.4, 3.0, 0.7, 67.0))
ROOT_AZ = (195.0, 240.0, 295.0, 350.0, 45.0, 125.0)       # RT1..RT6, also the strand azimuths at z 0
GROOVE = 0.42
TOP_Z = RINGS[-1][0]
BOSSES = {   # anchor z on the axis, azimuth, rise, protrusion past the bark, collar radius, socket hole radius
    "B_L": dict(z=8.85, az=175.0, rise=15.0, out=0.32, r=1.1, rh=0.48),
    "B_R": dict(z=8.95, az=355.0, rise=15.0, out=0.32, r=1.1, rh=0.48),
    "B_UL": dict(z=10.1, az=230.0, rise=40.0, out=0.40, r=0.95, rh=0.375),
}
KNOTS = {    # z, azimuth, rim (ru, rv, sides) or None, hole (ru, rv, sides), hole depth below the bark
    "front": dict(z=9.35, az=292.0, rim=(0.7, 0.9, 8), hole=(0.45, 0.65, 8), depth=0.32, proud=0.12),
    "small": dict(z=11.15, az=284.0, rim=None, hole=(0.25, 0.25, 6), depth=0.26, proud=0.0),
    "back": dict(z=9.35, az=92.0, rim=(0.75, 0.75, 6), hole=(0.45, 0.45, 6), depth=0.32, proud=0.12),
}
TRUNK_PITS = ((250.0, 5.0), (276.0, 7.6), (312.0, 6.2), (100.0, 5.6), (70.0, 7.2), (118.0, 8.4),
              (146.0, 4.6), (200.0, 6.6), (332.0, 4.2), (20.0, 5.4), (168.0, 7.8), (226.0, 3.6), (45.0, 8.6))
PIT_COUNT = {}     # pits made, per owner (trunk / module name)
SOCK = {}          # boss / socket name -> dict(F, d, r, rh, A, t)
KNOT_INFO = {}


def _axis_at(z):
    for (z0, _, x0, _), (z1, _, x1, _) in zip(RINGS, RINGS[1:]):
        if z <= z1:
            t = max(0.0, (z - z0) / (z1 - z0))
            return Vector((x0 + (x1 - x0) * t, 0.0, z))
    return Vector((RINGS[-1][2], 0.0, z))


def _strands():
    """Six strands (sorted root azimuths) and the groove azimuths between them: [(groove_start, span, strand idx)]."""
    S = sorted(ROOT_AZ)
    g = [((S[j] + ((S[(j + 1) % 6] - S[j]) % 360) / 2)) % 360 for j in range(6)]
    out = []
    for j in range(6):
        g0 = g[j - 1]
        span = (g[j] - g0) % 360
        out.append((g0, span, j))
    return out


def trunk_body(a, part=False):
    """The twisted six-strand body: 18 verts a ring (per strand a pulled-in groove vertex and two crest verts), eleven
    rings twisting 67 deg CCW, alternate strands 10 % thicker. Flat bottom (the part: an octagonal hollow in a pale
    chamfer rim) and a flat top cap (the part: the top socket). Grooves bark_deep, alternate strand crests a step
    lighter (by strand index), the foot a step deeper."""
    bm = a.bm
    rng = random.Random(54100)
    st = _strands()
    rings, kinds = [], {}
    for i, (z, D, cx, tw) in enumerate(RINGS):
        R = D / 2
        c = Vector((cx, 0.0, z))
        ring = []
        for g0, span, j in st:
            thick = 1.05 if j % 2 == 0 else 0.95
            for k, fr in enumerate((0.0, 1 / 3, 2 / 3)):
                az = g0 + span * fr + tw + rng.uniform(-1.5, 1.5)
                if k == 0:
                    r = R - GROOVE * min(1.0, R / 2.6)
                else:
                    r = R * thick * (1 + rng.uniform(-0.015, 0.015))
                v = bm.verts.new(c + _u(az) * r)
                kinds[v] = ("g", j) if k == 0 else ("c", j)
                ring.append(v)
        rings.append(ring)
    side = []
    for i in range(len(rings) - 1):
        side += _band(bm, rings[i], rings[i + 1])
    vs = [v for r in rings for v in r]
    bot, top, hole = [], [], []
    # bottom
    c0 = Vector((RINGS[0][2], 0, 0))
    if part:
        inner = [bm.verts.new(p) for p in _ring(c0, Vector((1, 0, 0)), Vector((0, 1, 0)), 1.35, 6, math.pi / 6)]
        deep = [bm.verts.new(p.co + Vector((0, 0, 0.4))) for p in inner]
        bot += [f for f in _zip(bm, list(reversed(rings[0])), list(reversed(inner)), c0, Vector((1, 0, 0)),
                                Vector((0, -1, 0)))]
        hole += _band(bm, deep, inner) + [bm.faces.new(deep)]
        vs += inner + deep
    else:
        cb = bm.verts.new(c0)
        bot += [bm.faces.new((rings[0][(k + 1) % 18], rings[0][k], cb)) for k in range(18)]
        vs.append(cb)
    # top
    ct = Vector((RINGS[-1][2], 0, TOP_Z))
    if part:
        inner = [bm.verts.new(p) for p in _ring(ct, Vector((1, 0, 0)), Vector((0, 1, 0)), 0.55, 6, 0.0)]
        deep = [bm.verts.new(p.co - Vector((0, 0, 0.35))) for p in inner]
        top += _zip(bm, rings[-1], inner, ct, Vector((1, 0, 0)), Vector((0, 1, 0)))
        hole += _band(bm, inner, deep) + [bm.faces.new(list(reversed(deep)))]
        vs += inner + deep
    else:
        cc = bm.verts.new(ct)
        top += [bm.faces.new((rings[-1][k], rings[-1][(k + 1) % 18], cc)) for k in range(18)]
        vs.append(cc)
    SOCK["top"] = dict(F=ct.copy(), d=Z.copy(), r=RINGS[-1][1] / 2, rh=0.55)
    _close(a, vs, side + bot + top + hole, BARK)
    # colour by role and position
    for f in side:
        gv = [v for v in f.verts if kinds.get(v, ("", 0))[0] == "g"]
        zc = f.calc_center_median().z
        js = {kinds[v][1] for v in f.verts if v in kinds}
        if len(gv) >= 2:
            f.material_index = a._mi(_mix(BARK, BARK_D, 0.75))       # the groove's two facets
        elif zc < 0.8:
            f.material_index = a._mi(_mix(BARK, BARK_D, 0.25))
        elif min(js) % 2 == 0:
            f.material_index = a._mi(_mix(BARK, BARK_L, 0.5 if not gv else 0.25))   # every other strand lighter
    _paint(a, top, BARK_L)
    _paint(a, bot, BARK_L if part else _mix(BARK, BARK_D, 0.5))
    _paint(a, hole, HOLLOW)
    tones = [1.0 + rng.uniform(-0.04, 0.04) for _ in range(18)]
    for i in range(len(rings) - 1):
        for k in range(18):
            _tint(a, [side[i * 18 + k]], tones[k])
    _mottle(a, side, 0.03, 0.35, 54110)
    crest = [f for f in side if not any(kinds.get(v, ("", 0))[0] == "g" for v in f.verts)]
    return vs, side, crest


def _surface_t(tree, A, d):
    o, last = A.copy(), None
    for _ in range(12):
        h = tree.ray_cast(o, d)
        if h[0] is None:
            break
        last = (h[0] - A).dot(d)
        o = h[0] + d * 1e-4
    return last


def _place_bosses(tree):
    for name, s in BOSSES.items():
        d = _dir(s["rise"], s["az"])
        A = _axis_at(s["z"])
        t = _surface_t(tree, A, d)
        F = A + d * (t + s["out"])
        SOCK[name] = dict(F=F, d=d, r=s["r"], rh=s["rh"], A=A, t=t)


def boss(a, name, part=False):
    """An 8-sided collar from 0.8 inside the bark out to its flat face (the part: a socket hole in it)."""
    s = SOCK[name]
    A0 = s["A"] + s["d"] * (s["t"] - 0.8)
    u = _basis(s["d"])[0]
    vs, side, caps = tube(a, [A0, s["F"]], [s["r"] * 1.06, s["r"]], 8, u, math.pi / 8, start="flat",
                          end="socket" if part else "flat", hole=(s["rh"] / s["r"], 0.3, 5), cap_key=BARK_L)
    _paint(a, side, _mix(BARK, BARK_L, 0.25))
    _mottle(a, side, 0.04, 0.4, 54120 + len(name))
    return vs


# roots: name, azimuth, reach (toe tips), stub width / height, toes, kink (deg), moss on top (r0, r1) or None
ROOTS = (("RT1", 195.0, 7.6, 2.4, 2.4, 2, 6.0, None), ("RT2", 240.0, 7.2, 2.2, 2.2, 2, -8.0, None),
         ("RT3", 295.0, 7.8, 2.6, 2.6, 3, 5.0, (3.4, 4.8)), ("RT4", 350.0, 8.2, 2.4, 2.3, 2, -6.0, (5.6, 6.8)),
         ("RT5", 45.0, 7.4, 2.2, 2.2, 2, 7.0, None), ("RT6", 125.0, 7.6, 2.4, 2.3, 2, -5.0, None))
STUB_R0, STUB_Z0, STUB_R1, STUB_Z1 = 1.3, 2.4, 3.6, 1.0
ROOT_INFO = {}


def _stub_path(spec):
    e = _u(spec[1])
    return [e * STUB_R0 + Vector((0, 0, STUB_Z0)), e * STUB_R1 + Vector((0, 0, STUB_Z1))]


def root_stub(a, spec, part=False):
    """A root stub on the trunk foot: the root's six-sided section from inside the trunk out and down to a flat cut
    face at r 3.6 (the part: a socket hole for the root's peg)."""
    name, az, reach, w, h = spec[:5]
    path = _stub_path(spec)
    vs, rings, side, caps = prism(a, path, [(w * 1.08, h * 1.12), (w, h)], ROOT_PROF, end="socket" if part else "flat",
                                  hole=(0.4, 0.3))
    _paint(a, caps["cut"], BARK_L)
    for f in side:
        if f.calc_center_median().z < 0.8:
            f.material_index = a._mi(_mix(BARK, BARK_D, 0.25))
    _mottle(a, side, 0.04, 0.4, 54130 + int(az))
    return vs


def root(a, spec, peg=False):
    """One root module: from 0.015 off its stub face (0.02 wider all round) on down along the stub's axis to the
    ground, one kink, a low run to the toe base, then 2-3 blunt splayed toes sunk 0.05 (closed shells buried in the
    root end). The part: a round pale peg into the stub's socket."""
    name, az, reach, w, h, ntoe, kink, moss = spec
    p0, p1 = _stub_path(spec)
    t = (p1 - p0).normalized()
    F = p1 + t * 0.015
    Lg = F.z / -t.z
    G = F + t * Lg
    G.z = 0.0
    run = _u(az + kink)
    toe0 = reach - 1.15
    rG = Vector((G.x, G.y, 0)).length
    T0 = G + run * max(0.6, toe0 - rG)
    T0.z = 0.0
    if peg:
        path = [F]
        secs = [(w + 0.04, h + 0.04)]
        drop = [0.02]
    else:
        # hero (decision, budget): the root runs on from inside the trunk foot as one prism - the stub's shape with
        # no union seam; the stub with its socket and the root's peg exist only on the parts
        path = [p0, p1]
        secs = [(w * 1.08, h * 1.12), (w, h)]
        drop = [0.0, 0.0]
    path += [G, T0]
    secs += [(0.78 * w, 0.6 * h), (0.5 * w, 0.36 * h)]
    drop += [0.0, 0.0]
    vs, rings, side, caps = prism(a, path, secs, ROOT_PROF, drop=drop)
    _paint(a, caps["cut"], _mix(BARK, BARK_D, 0.5))
    nb = len(ROOT_PROF)
    for i, f in enumerate(side):
        k = i % nb                     # section edge index: 0 bottom, 1 / 5 lower flanks, 2 / 4 upper flanks, 3 ridge
        c = f.calc_center_median()
        if k == 0 or (k in (1, 5) and c.z < 0.5):
            f.material_index = a._mi(_mix(BARK, BARK_D, 0.25))
        elif k in (2, 3, 4):
            f.material_index = a._mi(_mix(BARK, BARK_L, 0.25))
        if moss and k == 3:
            r = Vector((c.x, c.y, 0)).length
            if moss[0] <= r <= moss[1]:
                f.material_index = a._mi(MOSS)
    _mottle(a, side, 0.04, 0.45, 54140 + int(az))
    out = list(vs)
    # toes
    rng = random.Random(54150 + int(az))
    spl = (-26.0, 0.0, 26.0) if ntoe == 3 else (-15.0, 15.0)
    tips = []
    for k, da in enumerate(spl):
        dv = _u(az + kink + da + rng.uniform(-4, 4))
        s0 = T0 - run * 0.45
        s0.z = 0.0
        L = reach - toe0 + 0.45 + rng.uniform(-0.15, 0.15)
        tip = s0 + dv * L
        tip.z = 0.0
        tw, th = 0.5 * w * 0.62, 0.36 * h * 0.78
        tv, trs, tside, tcaps = prism(a, [s0, tip], [(tw, th), (tw * 0.82, th * 0.8)], TOE_PROF)
        _paint(a, tcaps["cut"][1:], BARK_L if k % 2 == 0 else HOLLOW)
        _paint(a, tcaps["cut"][:1], BARK_D)
        for f in tside:
            if f.calc_center_median().z < 0.15:
                f.material_index = a._mi(_mix(BARK, BARK_D, 0.25))
        _mottle(a, tside, 0.04, 0.5, 54160 + k)
        tips.append(tip)
        out += tv
    if peg:
        cpeg = sum((v.co for v in rings[0]), Vector()) / nb
        u = _basis(t)[0]
        pv, _, pc = tube(a, [cpeg - t * 0.30, cpeg + t * 0.12], [0.5, 0.5], 5, u, 0.0, cap_key=BARK_L)
        _paint(a, _faces(pv), BARK_L)
        out += pv
    ROOT_INFO[name] = dict(F=F, G=G, T0=T0, tips=tips)
    return out


def trunk_part(a, part=False):
    """Body first (shell 0, the union's base), then the bosses, the six root stubs and the knot rims as closed shells
    (unioned in one at a time at the origin); the bark pits are flat insets on the body."""
    vs, side, crest = trunk_body(a, part)
    idx = {v: i for i, v in enumerate(vs)}
    fs = _faces(vs)
    tree = BVHTree.FromPolygons([v.co.copy() for v in vs], [[idx[v] for v in f.verts] for f in fs])
    _place_bosses(tree)
    # knots: on the bark, found by rays from the axis
    KNOT_INFO.clear()
    for name, k in KNOTS.items():
        d = _dir(0.0, k["az"])
        A = _axis_at(k["z"])
        t = _surface_t(tree, A, d)
        KNOT_INFO[name] = dict(S=A + d * t, d=d, **k)
    # pits on strand crests, away from the bosses and knots
    avoid = [(s["F"], s["r"] + 1.2) for s in SOCK.values() if "A" in s] + \
            [(k["S"], 1.4) for k in KNOT_INFO.values()]
    used = set()
    for az, z in (() if part else TRUNK_PITS):
        A = _axis_at(z)
        tgt = A + _u(az + _twist_at(z)) * 2.6

        def ok(f):
            c = f.calc_center_median()
            return f.is_valid and all((c - p).length > r for p, r in avoid) and f not in used and 2.0 < c.z < 11.0
        cand = [f for f in crest if ok(f) and _quad_fits(f, PIT_SIZE)]
        if cand:
            f = min(cand, key=lambda g: (g.calc_center_median() - tgt).length)
            used.add(f)
            if _pit(a, [f], f.calc_center_median(), depth=0.05) is not None:
                PIT_COUNT["trunk"] = PIT_COUNT.get("trunk", 0) + 1
    for name in BOSSES:
        boss(a, name, part)
    if part:
        for spec in ROOTS:
            root_stub(a, spec, part)


def _twist_at(z):
    for (z0, _, _, t0), (z1, _, _, t1) in zip(RINGS, RINGS[1:]):
        if z <= z1:
            return t0 + (t1 - t0) * max(0.0, (z - z0) / (z1 - z0))
    return RINGS[-1][3]


def _knot_rims(o):
    """The knots' pale rims: the bark faces round each carved hole, inside the rim ellipse on the knot's plane (a cut
    face region chosen by position round the hole, not by facing)."""
    keys = _keys(o)
    li = next((i for i, k in enumerate(keys) if k == BARK_L), None)
    if li is None:
        o.data.materials.append(K.fk().material(BARK_L))
        li = len(o.data.materials) - 1
    n = 0
    for p in o.data.polygons:
        if keys[p.material_index] == HOLLOW if p.material_index < len(keys) else False:
            continue
        c = Vector(p.center)
        for k in KNOT_INFO.values():
            if not k["rim"]:
                continue
            ru, rv, _ = k["rim"]
            d = k["d"]
            q = c - k["S"]
            if abs(q.dot(d)) > 0.7:
                continue
            u = Z.cross(d).normalized()
            v = d.cross(u).normalized()
            if (q.dot(u) / ru) ** 2 + (q.dot(v) / rv) ** 2 <= 1.0:
                p.material_index = li
                n += 1
    return n


def _knot_cutter(a):
    for name, k in KNOT_INFO.items():
        ru, rv, n = k["hole"]
        top = k["S"] + k["d"] * (k["proud"] + 0.5)
        bot = k["S"] - k["d"] * k["depth"]
        _ell_prism(a, bot, top, k["d"], ru, rv, n, HOLLOW, rot=math.pi / n)


# ---- branch modules (spec 2.4) ----------------------------------------------------------------------------------------
LIMB_INFO = {}        # visibility polylines: name -> [list of points]
MOD_INFO = {}         # module -> arms tips etc.


def _seat(boss_name, r_out=None):
    """A module's base ring 0.015 off its boss face, 0.02 wider all round, and its axis."""
    s = SOCK[boss_name]
    return s["F"] + s["d"] * 0.015, s["d"], (r_out or s["r"]) + 0.02


def _arm(a, pts, radii, n, key=BARK, end="flat", rot=0.0, back=0.3, cap_key=BARK_L):
    """An arm / tine / twig: a closed tube starting `back` inside its parent along its first segment."""
    p = [Vector(x) for x in pts]
    d0 = (p[1] - p[0]).normalized()
    p[0] = p[0] - d0 * back
    vs, side, caps = tube(a, p, radii, n, None, rot, end=end, key=key, cap_key=cap_key)
    _mottle(a, side, 0.04, 0.45, 54200 + int(abs(p[-1].x) * 10 + abs(p[-1].y) * 7))
    return vs, side, caps


def _main(a, boss_name, way, radii, n, peg=False):
    """A module's main run: base ring on the boss, out along the boss axis, then the waypoints (hard kinks)."""
    F, d, r0 = _seat(boss_name)
    pts = [F, F + d * 0.4] + [Vector(w) for w in way]
    vs, side, caps = tube(a, pts, [r0, r0 * 0.97] + list(radii), n, _basis(d)[0], math.pi / n, cap_key=BARK_L)
    _paint(a, caps["cut"][:1], BARK_D)          # the base face (sits on the boss, unseen)
    _mottle(a, side, 0.04, 0.4, 54210 + n)
    if peg:
        s = SOCK[boss_name]
        rp = s["rh"] - 0.02
        pv, _, _ = tube(a, [F - d * 0.30, F + d * 0.12], [rp, rp], 8, _basis(d)[0], 0.0, cap_key=BARK_L)
        _paint(a, _faces(pv), BARK_L)
        vs += pv
    return vs, side, pts


def _knuckle_light(a, side, pts, k0, k1):
    """The pale worn knob (fix round 1, m9): the knuckle block's outer end, chosen purely by position along the run
    (every ring face past 0.45 of the block, all round it), never by which way a face points."""
    p0, p1 = Vector(pts[k0]), Vector(pts[k1])
    for f in side:
        c = f.calc_center_median()
        tt = (c - p0).dot(p1 - p0) / max(1e-6, (p1 - p0).length_squared)
        if tt > 0.45:
            f.material_index = a._mi(_mix(BARK, BARK_L, 0.5))


# module waypoints (build frame, spec 2.4)
BM = {
    "BM1": dict(boss="B_L", way=[(-4.0, 0.3, 9.6), (-4.4, 0.32, 9.66)], r=(0.84, 0.8), n=8,
                arms=dict(up=([(-4.0, 0.3, 9.6), (-4.6, 0.8, 10.9), (-5.1, 1.1, 12.0)], (0.8, 0.72, 0.62), 5),
                          low=([(-4.0, 0.3, 9.6), (-5.3, -0.4, 8.7), (-6.5, -0.8, 8.8)], (0.72, 0.6, 0.45), 5)),
                tines=[((-6.5, -0.8, 8.8), (-7.5, -1.4, 9.5)), ((-6.5, -0.8, 8.8), (-7.7, -0.5, 8.3))],
                feeds={"up": "L"}, pits=[(-4.0, -0.1, 9.3), (-5.3, -0.7, 8.5), (-6.3, -1.1, 8.7),
                                                 (-4.7, 0.4, 11.0)]),
    "BM2": dict(boss="B_UL", way=[(-2.0, -3.0, 12.3)], r=(0.72,), n=6,
                arms=dict(up=([(-2.0, -3.0, 12.3), (-3.2, -4.7, 13.1)], (0.66, 0.56), 5)),
                spur=((-2.0, -3.0, 12.3), (-1.5, -3.6, 13.3), 0.32),
                tines=[], feeds={"up": "FL"}, pits=[(-1.95, -3.2, 12.0)]),
    # fix round 1 (B1): the V fork 0.5 lower and its arms splayed apart (bl out to the left) so it reads as a V that
    # rises into B's raised underside from the rear as well as the front
    "BM3": dict(boss="top", way=[(0.85, 0.3, 13.6)], r=(1.0,), n=8,
                arms=dict(bl=([(0.85, 0.3, 13.6), (-0.1, 2.3, 14.5), (-0.9, 4.3, 15.6)], (0.8, 0.72, 0.64), 5),
                          br=([(0.85, 0.3, 13.6), (2.5, 1.9, 14.4), (3.8, 4.3, 15.6)], (0.76, 0.68, 0.6), 5)),
                spur=((0.95, -0.2, 13.0), (1.5, -1.3, 14.4), 0.5),
                tines=[], feeds={"bl": "B", "br": "B"}, pits=[(1.1, 0.1, 13.3), (0.6, -0.9, 12.9)]),
    "BM4": dict(boss="B_R", way=[(3.9, -0.7, 10.0), (4.28, -0.78, 10.06)], r=(0.84, 0.78), n=8,
                arms=dict(riser=([(3.9, -0.7, 10.0), (4.0, -2.5, 11.6), (4.3, -4.3, 12.9)], (0.8, 0.7, 0.6), 5),
                          side=([(3.9, -0.7, 10.0), (5.5, -0.4, 9.7), (6.8, 0.1, 10.6)], (0.72, 0.6, 0.5), 5)),
                tines=[((5.1, -0.55, 9.7), (7.4, -1.5, 8.9)), ((5.1, -0.55, 9.7), (7.7, -0.6, 9.2))],
                feeds={"riser": "FR", "side": "R"}, pits=[(4.0, -1.0, 9.7), (5.3, -0.8, 9.5),
                                                                     (3.7, -2.7, 11.6)]),
}
TIP_IN = 0.0          # how far each feeding arm runs on past its joint J into the clump core


def module(a, name, peg=False):
    """One branch module: main run on its boss (8-sided; BM2 6), arms (6-sided) from inside the knuckle, bare tines
    (4-sided, flat ends half pale / half hollow), a spur with a pale cut end, and pits at the kinks and forks. Feeding
    arms run on TIP_IN past their joint into their clump's core."""
    B = BM[name]
    if B["boss"] == "top":
        s = SOCK["top"]
        F = s["F"] + Z * 0.015
        r0 = s["r"] + 0.05
        pts = [F, F + Z * 0.5] + [Vector(w) for w in B["way"]]
        vs, side, caps = tube(a, pts, [r0, r0 * 0.9] + list(B["r"]), B["n"], Vector((1, 0, 0)), 0.0, cap_key=BARK_L)
        _paint(a, caps["cut"][:1], BARK_D)
        _mottle(a, side, 0.04, 0.4, 54230)
        if peg:
            pv, _, _ = tube(a, [F - Z * 0.33, F + Z * 0.12], [0.53, 0.53], 8, Vector((1, 0, 0)), 0.0)
            _paint(a, _faces(pv), BARK_L)
            vs += pv
    else:
        vs, side, pts = _main(a, B["boss"], B["way"], B["r"], B["n"], peg=peg)
    allside = list(side)
    out = list(vs)
    K_ = Vector(B["way"][0])
    if name in ("BM1", "BM4"):
        _knuckle_light(a, side, pts, len(pts) - 2, len(pts) - 1)
    LIMB_INFO[name] = [pts[1:]]
    info = MOD_INFO.setdefault(name, {})
    for arm, (apts, radii, n) in B["arms"].items():
        apts = [Vector(p) for p in apts]
        feed = B["feeds"].get(arm)
        end_pts = list(apts)
        rad = list(radii)
        if feed:
            dlast = (apts[-1] - apts[-2]).normalized()
            if TIP_IN > 0:
                end_pts.append(apts[-1] + dlast * TIP_IN)
                rad.append(radii[-1] * 0.9)
            info[arm] = dict(J=apts[-1].copy(), d=dlast, clump=feed, pts=[p.copy() for p in apts])
        avs, aside, acaps = _arm(a, end_pts, rad, n, back=0.35)
        allside += aside
        out += avs
        LIMB_INFO[name].append(apts)
    for base, tip in B["tines"]:
        tv, tside, tcaps = _arm(a, [base, tip], [0.27, 0.23], 4, back=0.3, rot=0.3)
        _paint(a, tcaps["cut"][1:], BARK_L if tip[1] < -0.5 else HOLLOW)
        allside += tside
        out += tv
        LIMB_INFO[name].append([Vector(base), Vector(tip)])
    if B.get("spur"):
        b, t, r = B["spur"]
        sv, sside, scaps = _arm(a, [b, t], [r, r * 0.92], 5, back=0.3)
        _paint(a, scaps["cut"][1:], BARK_L)
        allside += sside
        out += sv
    # bark deep ring at the knuckle / fork crotch (position along the run)
    for f in allside:
        if f.is_valid and (f.calc_center_median() - K_).length < 0.75:
            f.material_index = a._mi(_mix(BARK, BARK_D, 0.25))
    for p in B["pits"]:
        if _pit(a, allside, p, depth=0.04) is not None:
            PIT_COUNT[name] = PIT_COUNT.get(name, 0) + 1
    return out


# ---- leaf clumps (spec 2.5) -------------------------------------------------------------------------------------------
# centre, core bottom z, top z, W, D, cards (cap / droop), tone shift, droop bottom z (outer side), seed
# Fix round 1: cards are 18-tri five-lobe mounds of radius CARD_R (1.3-1.5), more of them; B has no skirt and its core
# bottom is raised to 15.2 so the BM3 V leader shows from the rear (B1); skirts are small mid-toned cards hung from a
# lower ring (zs x core height) on L / R / FL / FR.
CLUMPS = {
    "B": dict(c=(1.6, 5.6), zc0=15.2, zt=19.85, W=12.1, D=11.7, cards=27, tone=0.3, skirt=(20, 90, 160), zs=0.12, tmax=96.0, seed=54301),
    "FL": dict(c=(-3.2, -5.2), zc0=11.1, zt=18.5, W=8.1, D=9.3, cards=19, tone=0.05, skirt=(), seed=54302),
    "FR": dict(c=(4.0, -5.0), zc0=11.6, zt=18.5, W=8.9, D=9.9, cards=19, tone=0.05, skirt=(), seed=54303),
    "L": dict(c=(-5.2, 1.2), zc0=9.8, zt=15.6, W=11.1, D=11.7, cards=18, tone=-0.1, skirt=(145, 172, 198), zs=0.18, inner_tmax=85.0, seed=54304),
    "R": dict(c=(6.9, 0.2), zc0=9.8, zt=15.4, W=9.5, D=10.7, cards=15, tone=-0.1, skirt=(-25, 8, 40), zs=0.18, inner_tmax=85.0, seed=54305),
}
CLUMP_INFO = {}
CARD_GUARD = []            # the trunk and limb solids while the hero's clumps are built (cards must not cut them)
CLUMP_DROPPED = []
CARD_R = 1.6               # card radius on the top; rim cards taper to ~1.45 (fix round 2: was 1.45)
# fix round 2: card facing (see _card_normal): each card is tipped off the dome by one of CARD_TILTS (deg) toward one of
# CARD_ROLLS directions round its dome normal, the pair chosen to be least edge-on to the views all round the tree
CARD_TILTS = (10.0, 20.0, 30.0, 40.0, 50.0)
CARD_ROLLS = 24
CARD_EDGE = 0.39           # |n.d| under this counts as edge-on (the verifier's line is 0.35)
CARD_SHINGLE = 0.03        # preference for the lower lobe proud (shingled leaves) over other rolls
CARD_TILT_COST = 0.02      # preference for the smaller tilt
CARD_VIEW_ELS = (5.0, 15.0)
CARD_TOP_W = 16.0          # weight of the view from straight above (one view against 24 round each ring)
CAP_TMAX = 128.0
CARD_CUT = 0.0             # a card may not reach into the trunk, a limb or a twig at all (fix round 2: was 0.01)
TOP_PATCH = (-0.03, 0.22)   # top cards: position-noise thresholds for mid->light 50 % / 25 % patches (top view, m3)
TONE_PATCH = 0.9          # broad noise patches mixing tones across the clump (position, never facing)
CORE_RINGS = ((0.12, 0.62), (0.32, 1.0), (0.7, 0.8))   # fix round 2: the bottom tapers to a low point (no plate)
CORE_N = 6
CORE_PAD = 1.15          # core half-width = clump half-width - CORE_PAD x card radius (fix round 2: was 0.9)
CORE_VPAD = 0.6          # core top = clump top - CORE_VPAD x card radius (round 1: 0.4 studs)
TONE_STEPS = ((0.66, LEAF_L), (0.8, (LEAF_M, LEAF_L, 0.5)), (0.88, (LEAF_M, LEAF_L, 0.25)), (0.96, LEAF_M),
              (1.02, (LEAF_M, LEAF_D, 0.5)), (9.9, LEAF_D))


def _away(c):
    v = Vector((c[0], c[1], 0.0))
    return v.normalized() if v.length > 1e-3 else Vector((0, 1, 0))


def clump_core(a, P):
    """The core dome: a 6-sided bottom ring (near-flat underside), a widest ring, a shoulder ring, a top vertex; toned by
    height in the core (dark underside, mid body, light-mid top) so the foliage mass between the cards reads as leaves."""
    bm = a.bm
    cx, cy = P["c"]
    rng = random.Random(P["seed"])
    rc = P["rc"]
    pad = P.get("pad", CORE_PAD)
    ax, ay = P["W"] / 2 - pad * rc, P["D"] / 2 - pad * rc
    zc0 = P["zc0"]
    # fix round 2: the core is shrunk inside the clump's envelope from above as well as round the sides, so it stays
    # round (a tall narrow core is a cylinder: its flanks are edge-on to every camera) and the cards make the outline
    hc = P["zt"] - CORE_VPAD * rc - zc0
    ph = rng.uniform(0, 1)
    rings = []
    for s, rho in CORE_RINGS:
        rings.append([bm.verts.new(Vector((cx + math.cos(ph + 2 * math.pi * k / CORE_N + s) * ax * rho * rng.uniform(0.96, 1.04),
                                           cy + math.sin(ph + 2 * math.pi * k / CORE_N + s) * ay * rho * rng.uniform(0.96, 1.04),
                                           zc0 + s * hc * rng.uniform(0.97, 1.03) if s else zc0)))
                      for k in range(CORE_N)])
    top = bm.verts.new(Vector((cx + rng.uniform(-0.2, 0.2), cy + rng.uniform(-0.2, 0.2), zc0 + hc)))
    if CORE_RINGS[0][0] > 0:     # fix round 2: a low cone under the bottom ring, its point at zc0 (no flat plate)
        bot = bm.verts.new(Vector((cx, cy, zc0)))
        fs = [bm.faces.new((rings[0][(k + 1) % CORE_N], rings[0][k], bot)) for k in range(CORE_N)]
        rings_vs = [bot]
    else:
        fs = [bm.faces.new(list(reversed(rings[0])))]
        rings_vs = []
    for i in range(len(rings) - 1):
        fs += _band(bm, rings[i], rings[i + 1])
    fs += [bm.faces.new((rings[-1][k], rings[-1][(k + 1) % CORE_N], top)) for k in range(CORE_N)]
    vs = [v for r in rings for v in r] + [top] + rings_vs
    _close(a, vs, fs, LEAF_D)
    for f in fs:                 # by height in the core: dark underside and lower band, greener upper dome
        hz = (f.calc_center_median().z - zc0) / hc
        if hz > 0.7:
            f.material_index = a._mi(_mix(LEAF_M, LEAF_L, 0.75))
        elif hz > 0.4:
            f.material_index = a._mi(_mix(LEAF_M, LEAF_L, 0.5))
        elif hz > 0.25:
            f.material_index = a._mi(LEAF_M)
        else:                    # the underside band (fix round 1: darker, the sheet's dark clump bottoms; fix round 2:
            # mid->dark 50 %, since the tapered cone puts more of it face-down and the cards now darken the bottom)
            f.material_index = a._mi(_mix(LEAF_M, LEAF_D, 0.5))
    _mottle(a, fs, 0.03, 0.5, P["seed"] + 3)
    P.update(ax=ax, ay=ay, hc=hc)
    return vs


CARD_LOBES = (1.0, 0.95, 0.97)         # fix round 2: three broad rounded lobes (x rc), a clover-like leaf (16 tris, so
                                       # 98 cards fit where 72 four-lobe ones did: fuller clumps)
CARD_HALF = 22.0                       # fix round 2: each lobe ends in two verts at +-22 deg: a wide, rounded lobe end
CARD_NOTCH = 0.7                       # fix round 2: notches (x rc) between the wide lobes; tips stay >= 110 deg
CARD_DOME = 0.08                       # apex height over the rim plane, x rc (low: the card shades as one leaf)


def card_rim():
    """The card's rim as (angle deg, radius x rc), counter-clockwise from the leading lobe at 0 deg: per lobe two tip
    verts at +-CARD_HALF and a notch at the half-way angle to the next lobe."""
    nl = len(CARD_LOBES)
    step = 360.0 / nl
    pts = []
    for i, r in enumerate(CARD_LOBES):
        c = i * step
        pts += [(c - CARD_HALF, r), (c + CARD_HALF, r), (c + step / 2, CARD_NOTCH)]
    return pts


def card_top_extent():
    """Distance from a card's centre to its rim edge opposite the leading lobe (its 'top' when it hangs), x rc."""
    return max(r * math.cos(math.radians(a_ - 180.0)) for a_, r in card_rim())


def leaf_card(a, P0, n, spin, rc, key):
    """One closed lobed leaf card (fix round 2: 16 tris): a flat 9-vert rim of three broad rounded lobes (each lobe a
    wide two-vert end at CARD_LOBES x rc, +-CARD_HALF deg, with notches at CARD_NOTCH between them, so no tip angle is
    under 110 deg) in the plane across n through P0, and a low apex CARD_DOME x rc above it (a lobed low pyramid:
    closed, outward, no self-intersection). The rim face is triangulated in _post (BEAUTY)."""
    bm = a.bm
    u, v = _basis(n)
    rim = []
    for ang_d, r in card_rim():
        ang = spin + math.radians(ang_d)
        rim.append(bm.verts.new(P0 + (u * math.cos(ang) + v * math.sin(ang)) * (r * rc)))
    top = bm.verts.new(P0 + n * (CARD_DOME * rc))
    N = len(rim)
    fs = [bm.faces.new((rim[k], rim[(k + 1) % N], top)) for k in range(N)]
    fs.append(bm.faces.new(list(reversed(rim))))
    vs = rim + [top]
    _close(a, vs, fs, key)
    return vs, fs


def _ell(P, th, ph):
    """Point and smooth normal on the clump's core ellipsoid at polar angle th (from the top) and azimuth ph."""
    cx, cy = P["c"]
    ax, ay, hc = P["ax"], P["ay"], P["hc"]
    zc = P["zc0"] + 0.3 * hc
    cz = 0.7 * hc if th <= math.pi / 2 else 0.3 * hc
    st, ct = math.sin(th), math.cos(th)
    p = Vector((cx + ax * st * math.cos(ph), cy + ay * st * math.sin(ph), zc + cz * ct))
    nrm = Vector((st * math.cos(ph) / ax, st * math.sin(ph) / ay, ct / cz)).normalized()
    return p, nrm, Vector((cx, cy, zc))


def _inside_count(tree, vs):
    return sum(1 for v in vs if m047._parity_in(tree, v.co))


def _card_in(tree, vs, hi=2):
    """Verts of a card inside its core; a card whose centre is inside counts as too deep (hi + 1 at least)."""
    nin = _inside_count(tree, vs)
    if m047._parity_in(tree, sum((v.co for v in vs), Vector()) / len(vs)):
        nin = max(nin, hi + 1)
    return nin


def _seat_card(a, core_bvh, S, nrm, n2, spin, rc, key, lo=1, hi=2):
    """Place a card on the core: start with its bottom centre 0.03 into the core surface at S and move it along nrm
    until between lo and hi of its 10 verts are inside the core (it touches the core, <= 25 % buried). If the count
    jumps past that window (several verts cross together), the card sits at the outermost push where it still
    touches: the step searched down to 0.005, so its nearest vertex is within 0.005 of the core."""
    seen = {}

    def put(push):
        vs, fs = leaf_card(a, S - nrm * 0.03 + nrm * push, n2, spin, rc, key)
        return vs, _card_in(core_bvh, vs, hi)

    def drop(vs):
        for v in vs:
            a.bm.verts.remove(v)
    for push in sorted([0.04 * i for i in range(-20, 16)], key=abs):
        vs, nin = put(push)
        seen[push] = nin
        if lo <= nin <= hi:
            return vs, nin
        drop(vs)
    inside = [p for p, n in seen.items() if n > hi]
    outside = [p for p, n in seen.items() if n < lo]
    p_in = max(inside) if inside else -0.8
    p_out = min([p for p in outside if p > p_in] or [p_in + 0.04])
    while p_out - p_in > 0.005:
        mid = 0.5 * (p_in + p_out)
        vs, nin = put(mid)
        if lo <= nin <= hi:
            return vs, nin
        drop(vs)
        if nin > hi:
            p_in = mid
        else:
            p_out = mid
    return put(p_out)


def _round_dirs():
    """Directions all round the tree (toward the viewer) with weights: every 15 deg of azimuth at elevation 5 and 25,
    and straight down from above. No azimuth is favoured."""
    out = []
    for el in CARD_VIEW_ELS:
        e = math.radians(el)
        for k in range(24):
            az = math.radians(15.0 * k)
            out.append((Vector((math.sin(az) * math.cos(e), -math.cos(az) * math.cos(e), math.sin(e))), 1.0))
    out.append((Vector((0.0, 0.0, 1.0)), CARD_TOP_W))
    return out


def _card_normal(nrm, e_th, rng=None, vis=None, phase=0.0, score=False):
    """Fix round 2: a card's facing. The card lies on the dome (normal nrm) tipped CARD_TILTS deg toward a direction
    round the normal (the roll); among CARD_ROLLS rolls (random phase) and the tilts, keep the facing that is least
    edge-on to the views all round the tree (|n.d| under CARD_EDGE, for each view that can see that part of the
    dome), preferring the lower lobe proud (shingled leaves) and the smaller tilt. No camera or azimuth is favoured:
    the views are evenly spread, so a card on any silhouette shows a face or its back, not its edge."""
    e_ph = nrm.cross(e_th)
    j = rng.uniform(0.0, 2.0 * math.pi) if rng is not None else phase
    dirs = _round_dirs()
    if vis is None:
        # each view sees this part of the dome fully when it faces the view, fading out just past the silhouette
        vis = [max(0.0, min(1.0, (nrm.dot(d) + 0.35) / 0.7)) for d, w in dirs]
    seen = [(d, w * v) for (d, w), v in zip(dirs, vis) if w * v > 0.0]

    def edge_share(n2):
        # the share of the card's seen (projected) area that is near edge-on, over all the views
        tot = edge = 0.0
        for d, w in seen:
            c = abs(n2.dot(d))
            tot += c * w
            if c < CARD_EDGE:
                edge += c * w
        return edge / max(tot, 1e-6)
    if score:
        return edge_share(score)
    best = None
    for kr in range(CARD_ROLLS):
        roll = j + 2.0 * math.pi * kr / CARD_ROLLS
        e_t = e_th * math.cos(roll) + e_ph * math.sin(roll)
        for td in CARD_TILTS:
            t = math.radians(td)
            n2 = (nrm * math.cos(t) - e_t * math.sin(t)).normalized()
            risk = edge_share(n2) + CARD_SHINGLE * 0.5 * (1.0 - math.cos(roll)) + CARD_TILT_COST * td / 45.0
            if best is None or risk < best[0]:
                best = (risk, n2)
    return best[1]


CORE_SOL = None         # hero build only: every clump's core (a card may not sit > 25 % inside cores, its own or not)


def _in_cores(vs):
    """Verts of a card inside any clump core, and whether its centre is inside one."""
    nin = sum(1 for v in vs if CORE_SOL.point(v.co)[0] > 0.0)
    cen = sum((v.co for v in vs), Vector()) / len(vs)
    return nin, CORE_SOL.point(cen)[0] > 0.0


def _clear_cores(a):
    """Hero only, after every clump is built: a card that a later clump's core swallowed (more than 2 of its verts
    inside the cores, or its centre inside one) is moved out along its dome normal in 0.03 steps until it is not;
    it still touches a core. A card that can't clear without cutting wood is removed. Returns (moved, removed)."""
    moved = removed = 0
    keep = []
    for r in CARD_REC:
        vs = r["vs"]
        nin, cin = _in_cores(vs)
        if nin <= 2 and not cin:
            keep.append(r)
            continue
        ok = False
        for _ in range(40):
            for v in vs:
                v.co += r["nrm"] * 0.03
            nin, cin = _in_cores(vs)
            if nin <= 2 and not cin:
                ok = r["cuts"](vs) <= CARD_CUT
                break
        if ok:
            moved += 1
            keep.append(r)
        else:
            for v in vs:
                a.bm.verts.remove(v)
            removed += 1
    CARD_REC[:] = keep
    return moved, removed


CARD_SEED = 8           # offset on every clump's card-layout seed (fix round 2: the layout picked by an all-round scan)
CARD_REC = None         # hero build only: every cap card placed, for the visibility pass (_refine_cards)
REFINE = [True]         # run the visibility pass in the hero
REFINED = []            # cards re-faced per pass in the last hero build
CLEARED = []            # (moved, removed) cards swallowed by another clump's core, last hero build
REFINE_PASSES = 5
REFINE_GAIN = 0.005     # a card is re-faced only if its edge-on share drops by at least this much


def _card_vis(bvh, own, owner, P0, u, v, rc, extra=()):
    """Per direction of _round_dirs(): the share of 5 points on a card (centre and four points 0.55 rc out) from which
    a ray toward the viewer leaves the tree without hitting anything but the card itself."""
    pts = [P0] + [P0 + (u * math.cos(k * math.pi / 2) + v * math.sin(k * math.pi / 2)) * (0.55 * rc) for k in range(4)]
    out = []
    for d, w in _round_dirs():
        free = 0
        for p in pts:
            q = p.copy()
            blocked = False
            for _ in range(8):
                loc, n, idx, dist = bvh.ray_cast(q, d, 60.0)
                if loc is None:
                    break
                if owner.get(idx) == own:
                    q = loc + d * 1e-4
                    continue
                blocked = True
                break
            if not blocked:
                for t in extra:
                    if t.ray_cast(p + d * 1e-3, d, 60.0)[0] is not None:
                        blocked = True
                        break
            free += 0 if blocked else 1
        out.append(free / len(pts))
    return out


def _refine_cards(a):
    """Fix round 2, hero only: the visibility pass. With every clump built, each cap card's facing is chosen again
    by _card_normal, weighting each view by how much of the card that view really sees (rays past the other cards,
    the cores, the limbs and the trunk) instead of by the dome alone. A card is replaced (same seat, spin, size,
    material and tint) only if that lowers its edge-on share by REFINE_GAIN and the new card keeps out of the wood;
    otherwise it stays. Returns how many cards were re-faced per pass."""
    from mathutils.bvhtree import BVHTree
    bm = a.bm
    extra = [it[3] for it in CARD_GUARD[0].items] if CARD_GUARD else []
    done = []
    for ps in range(REFINE_PASSES):
        bm.faces.ensure_lookup_table()
        bm.faces.index_update()
        bvh = BVHTree.FromBMesh(bm)
        owner = {}
        for ci, r in enumerate(CARD_REC):
            for f in _faces(r["vs"]):
                owner[f.index] = ci
        n_new = 0
        for ci, r in enumerate(CARD_REC):
            vs = r["vs"]
            cen = sum((x.co for x in vs), Vector()) / len(vs)
            n_old = r["n2"]
            u, v = _basis(n_old)
            vis = _card_vis(bvh, ci, owner, cen, u, v, r["rc"], extra)
            s_old = _card_normal(r["nrm"], r["e_th"], vis=vis, score=n_old)
            n_new2 = _card_normal(r["nrm"], r["e_th"], vis=vis, phase=0.37 * ci + ps)
            s_new = _card_normal(r["nrm"], r["e_th"], vis=vis, score=n_new2)
            if s_new > s_old - REFINE_GAIN:
                continue
            if r.get("hang"):
                nvs, nin = _hang_card(a, r["core"], r["S"], r["dv"], n_new2, r["rc"])
            else:
                nvs, nin = _seat_card(a, r["core"], r["S"], r["nrm"], n_new2, r["spin"], r["rc"], LEAF_M)
            if r["cuts"](nvs) > CARD_CUT or nin > 2 or _in_cores(nvs)[0] > 2 or _in_cores(nvs)[1]:
                for x in nvs:
                    bm.verts.remove(x)
                continue
            old_fs = _faces(vs)
            mi = old_fs[0].material_index
            tint = old_fs[0].loops[0][a.tint_layer][0]
            for f in _faces(nvs):
                f.material_index = mi
                for l in f.loops:
                    l[a.tint_layer] = (tint, tint, tint, 1.0)
            for x in vs:
                bm.verts.remove(x)
            r.update(vs=nvs, n2=n_new2)
            n_new += 1
        done.append(n_new)
        if not n_new:
            break
    return done


def _hang_card(a, core_bvh, S, dv, n2, rc):
    """A skirt card hung from the core's lower ring at S (outward dv): its leading lobe hangs down, its top notch is
    tucked into the core (1-2 verts inside) and the card hangs out."""
    w = (Z - n2 * Z.dot(n2)).normalized()          # up, in the card's plane
    spin = math.atan2(w.dot(_basis(n2)[1]), w.dot(_basis(n2)[0])) + math.pi    # leading lobe hanging down
    vs, nin = None, 0
    for k2 in range(8):
        P0 = S - dv * (0.25 + 0.08 * k2) - w * (card_top_extent() * rc)
        vs, fs = leaf_card(a, P0, n2, spin, rc, LEAF_M)
        nin = _card_in(core_bvh, vs)
        if 1 <= nin <= 2 or k2 == 7:
            break
        if nin > 2:             # tucked too deep: back out in small steps until <= 2 verts are inside
            for k3 in range(40):
                for v in vs:
                    a.bm.verts.remove(v)
                P0 = P0 + dv * 0.02
                vs, fs = leaf_card(a, P0, n2, spin, rc, LEAF_M)
                nin = _card_in(core_bvh, vs)
                if nin <= 2:
                    break
            break
        for v in vs:
            a.bm.verts.remove(v)
    return vs, nin


def _tone_key(x):
    for lim, k in TONE_STEPS:
        if x < lim:
            return k if isinstance(k, str) else _mix(*k)
    return LEAF_D


def leaf_clump(a, name, stub=False):
    """A clump: (part only: the branch core's stub from below) twigs from the feeding arm into the core's underside,
    the core dome, then overlapping five-lobe cards on the core - a Fibonacci spread over the cap (top cards larger,
    rim cards steeper, every card tilted so its outer lobes stand proud) and 0-3 small skirt cards hanging on the
    outer side. Every card touches the core (1-2 of its 11 verts inside) and keeps out of the trunk, the limbs and the
    twigs. Cards are toned by height rank within the clump (light top, mid body, dark low) plus position patches."""
    P = dict(CLUMPS[name])
    rng = random.Random(P["seed"] + CARD_SEED)
    n_cap = P["cards"]
    cx, cy = P["c"]
    P["rc"] = CARD_R
    out = []
    # branch core first: twigs from the feeding arm(s) into the core underside; the cards keep clear of them (m7)
    tguard = m047._Solids()
    feeds = [(m, arm, info) for m, ar in MOD_INFO.items() for arm, info in ar.items() if info.get("clump") == name]
    twig_lines = []
    for m, arm, info in feeds:
        J, dl = info["J"], info["d"]
        # fork 0.55 below the core underside on the arm's last segment
        p_a, p_b = info["pts"][-2], info["pts"][-1]
        zf = P["zc0"] - 0.55
        tt = (zf - p_a.z) / (p_b.z - p_a.z) if abs(p_b.z - p_a.z) > 1e-3 else 0.5
        tt = max(0.2, min(0.9, tt))
        fork = p_a + (p_b - p_a) * tt
        side = dl.cross(Z)
        side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
        front = 1 if side.y < 0 else -1
        for sgn in ((front,) if len(feeds) == 1 else (-1,) if arm == "bl" else (1,)):
            tip = Vector((J.x, J.y, 0)) + side * (sgn * 1.3) + dl.to_2d().to_3d() * 0.4
            tip.z = P["zc0"] + 0.32
            tv, tside, tcaps = _arm(a, [fork, tip], [0.3, 0.24], 4, back=0.25, rot=0.4)
            out += tv
            tguard.add_vs(tv, f"twig{len(twig_lines)}")
            twig_lines.append([fork.copy(), tip.copy()])

    def cuts(vs):
        """Depth of a card's deepest vertex inside the trunk, a limb (CARD_GUARD) or one of this clump's twigs; fix
        round 2: 1.0 if any card face crosses one of their faces (a thin twig through a leaf, no vertex inside)."""
        d = tguard.depth(vs)
        sols = [tguard] + (CARD_GUARD[:1] if CARD_GUARD else [])
        if CARD_GUARD:
            d = max(d, CARD_GUARD[0].depth(vs))
        if d <= CARD_CUT:
            fs = _faces(vs)
            idx = {v: i for i, v in enumerate(vs)}
            t = BVHTree.FromPolygons([v.co.copy() for v in vs], [[idx[v] for v in f.verts] for f in fs])
            lo = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
            hi = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
            for sol in sols:
                for nm, a0, a1, tb in sol.items:
                    if a1.x < lo.x or a0.x > hi.x or a1.y < lo.y or a0.y > hi.y or a1.z < lo.z or a0.z > hi.z:
                        continue
                    if t.overlap(tb):
                        return 1.0
        return d

    core_vs = clump_core(a, P)
    # a core vertex that lands inside a limb (the knuckle under L) is drawn in toward the core's axis until clear,
    # so no foliage is buried in wood
    for v in core_vs:
        for _ in range(30):
            d = tguard.point(v.co)[0]
            if CARD_GUARD:
                d = max(d, CARD_GUARD[0].point(v.co)[0])
            if d <= 0.0:
                break
            ax_ = Vector((cx, cy, v.co.z))
            v.co = ax_ + (v.co - ax_) * 0.96
    ctree = m047._Solids()
    ctree.add_vs(core_vs, "core")
    core_bvh = ctree.items[0][3]
    if CORE_SOL is not None:
        CORE_SOL.add_vs(core_vs, f"core_{name}")
    away = _away(P["c"])
    placed = []
    nin_all = []
    # cap cards: Fibonacci over the dome and round under its widest ring (polar 0 .. CAP_TMAX deg)
    ph0 = rng.uniform(0, 2 * math.pi)
    tmax = math.radians(P.get("tmax", CAP_TMAX))
    for i in range(n_cap):
        s = (i + 0.5) / n_cap
        th = math.acos(1 - s * (1 - math.cos(tmax)))
        ph = ph0 + i * math.radians(137.508)
        if "inner_tmax" in P and math.cos(ph) * away.x + math.sin(ph) * away.y < -0.3:
            # the trunk side of a low clump stays up, so the limbs feeding it show (spec 2.5)
            th = min(th, math.radians(P["inner_tmax"]))
        rc = P["rc"] * (1.0 - 0.1 * th / tmax) * rng.uniform(0.96, 1.03)
        p, nrm, C = _ell(P, th, ph)
        hit = core_bvh.ray_cast(C, (p - C).normalized(), 50.0)
        S = hit[0] if hit[0] is not None else p
        e_th = Vector((math.cos(th) * math.cos(ph), math.cos(th) * math.sin(ph), -math.sin(th)))
        e_th = (e_th - nrm * e_th.dot(nrm))
        e_th = e_th.normalized() if e_th.length > 1e-6 else _u(math.degrees(ph))
        n2 = _card_normal(nrm, e_th, rng)
        spin = rng.uniform(0, 2 * math.pi)
        vs, nin = _seat_card(a, core_bvh, S, nrm, n2, spin, rc, LEAF_M)
        if cuts(vs) > CARD_CUT:
            # a card that would cut the trunk, a limb or a twig: shrink it and turn it, keeping it on the core; drop
            # it if it still cuts
            for v in vs:
                a.bm.verts.remove(v)
            vs = None
            for sc, dsp in ((0.9, 0.3), (0.9, 0.9), (0.8, 0.0), (0.8, 0.6), (0.7, 0.3)):
                vs, nin = _seat_card(a, core_bvh, S, nrm, n2, spin + dsp, rc * sc, LEAF_M)
                if cuts(vs) <= CARD_CUT:
                    rc, spin = rc * sc, spin + dsp
                    break
                for v in vs:
                    a.bm.verts.remove(v)
                vs = None
            if vs is None:
                CLUMP_DROPPED.append(name)
                continue
        if CARD_REC is not None:
            CARD_REC.append(dict(vs=vs, S=S, nrm=nrm, e_th=e_th, n2=n2, spin=spin, rc=rc, core=core_bvh, cuts=cuts,
                                 clump=name))
        nin_all.append(nin)
        placed.append((vs, max(v.co.z for v in vs), False))
        out += vs
    # skirt on the outer side: small hanging cards tucked under the core's lower ring (zs x core height), turned to
    # the front / back cameras, mid-toned (m5); none on B, so the V leader shows from the rear (B1)
    for k, az in enumerate(P["skirt"]):
        ph = math.radians(az) + rng.uniform(-0.06, 0.06)
        dv = Vector((math.cos(ph), math.sin(ph), 0.0))
        zr = P["zc0"] + P.get("zs", 0.3) * P["hc"]
        C = Vector((cx, cy, zr))
        hit = core_bvh.ray_cast(C, dv, 50.0)
        S = Vector(hit[0]) if hit[0] is not None else C + Vector((dv.x * P["ax"], dv.y * P["ay"], 0))
        rc = P["rc"] * rng.uniform(0.92, 1.0)
        # fix round 2: the skirt card faces out in plan, tipped up a little, then faced like the cap cards (no turn
        # toward a camera)
        nrm_s = (dv + Z * 0.35).normalized()
        e_s = (-Z - nrm_s * (-Z).dot(nrm_s)).normalized()
        n2 = _card_normal(nrm_s, e_s, rng)
        vs, nin = _hang_card(a, core_bvh, S, dv, n2, rc)
        if cuts(vs) > CARD_CUT:
            for v in vs:
                a.bm.verts.remove(v)
            CLUMP_DROPPED.append(name + "_skirt")
            continue
        if CARD_REC is not None:
            CARD_REC.append(dict(vs=vs, S=S, dv=dv, nrm=nrm_s, e_th=e_s, n2=n2, rc=rc, core=core_bvh, cuts=cuts,
                                 clump=name, hang=True))
        nin_all.append(nin)
        placed.append((vs, max(v.co.z for v in vs), True))
        out += vs
    # tone by height rank within the clump (role and position, never facing)
    order = sorted(range(len(placed)), key=lambda i: -placed[i][1])
    nc = len(placed)
    for rank, i in enumerate(order):
        vs, ztop, droop = placed[i]
        # 0 = top card ... 1 = lowest, shifted by the clump's crown tone and broad position patches (TONE_PATCH)
        cen = sum((v.co for v in vs), Vector()) / len(vs)
        x = rank / max(1, nc - 1) - P["tone"] + TONE_PATCH * noise.noise(cen * 0.32 + Vector((P["seed"] % 97, 3.1, 7.7)))
        if droop:
            x = min(max(x, 0.9), 1.0)          # skirts mid / mid-dark, never dark (m5)
        key = _tone_key(x)
        if x < TONE_STEPS[0][0] and not droop:
            # top cards: broad mid-tone patches by position (a second noise field), so the top view isn't all lime (m3)
            q = noise.noise(cen * 0.45 + Vector((P["seed"] % 53, 11.3, 2.9)))
            if q > TOP_PATCH[1]:
                key = _mix(LEAF_M, LEAF_L, 0.25)
            elif q > TOP_PATCH[0]:
                key = _mix(LEAF_M, LEAF_L, 0.5)
        fs = _faces(vs)
        _paint(a, fs, key)
        _tint(a, fs, 1.0 + rng.uniform(-0.04, 0.04))
    out += core_vs
    if stub:
        # the clump module's stub: below the core, up through J into the core (part only; in the hero the arm is it)
        for m, arm, info in feeds:
            J, dl = info["J"], info["d"]
            base = J - dl * 1.6
            sv, sside, scaps = tube(a, [base, J, J + dl * 0.9], [0.6, 0.56, 0.46], 5, None, 0.0, cap_key=BARK_L)
            _paint(a, scaps["cut"][:1], BARK_L)
            out += sv
    CLUMP_INFO[name] = dict(rc=round(P["rc"], 2), cards=nc, inside=[min(nin_all), max(nin_all)], core=(round(P["ax"] * 2, 2), round(P["ay"] * 2, 2),
                                                                   round(P["hc"], 2)), twigs=twig_lines)
    return out


# ---- base dressing (spec 2.6) -----------------------------------------------------------------------------------------
ROCKS = {   # centre, (W, D, H), yaw, seed, lean (toward the trunk), pointed
    "RK1": ((-5.9, -4.2), (2.8, 2.4, 2.3), 20.0, 54401, 0.12, False),
    "RK2": ((-8.6, -0.7), (1.4, 1.2, 1.3), -15.0, 54402, 0.0, False),
    "RK3": ((-0.6, -7.2), (2.2, 2.0, 2.1), 35.0, 54403, 0.1, False),
    "RK4": ((5.2, -4.1), (2.6, 2.2, 2.8), -25.0, 54404, 0.3, True),
    "RK5": ((6.1, 2.6), (2.6, 2.2, 2.1), 10.0, 54405, 0.1, False),
    "RK6": ((-5.8, 3.8), (2.2, 2.0, 2.0), 40.0, 54406, 0.1, False),
    "RK7": ((-2.3, 6.9), (1.5, 1.3, 1.2), -30.0, 54407, 0.0, False),
}
PEBBLES = (((-2.5, -7.6), 0.75, 54411), ((1.1, -7.8), 0.6, 54412), ((9.0, -2.7), 0.7, 54413), ((1.5, 7.0), 0.6, 54414))
PADS = (   # mid azimuth, radius, length across, depth, seed
    (218.0, 5.3, 4.8, 3.0, 54421), (268.0, 5.2, 4.6, 2.8, 54422), (322.0, 5.3, 4.8, 3.0, 54423),
    (18.0, 5.2, 4.6, 2.9, 54424), (85.0, 5.2, 5.0, 3.2, 54425), (160.0, 5.3, 4.8, 3.0, 54426))
TUFTS = {   # centre, blades, height, spread
    "T1": ((-8.9, -3.5), 4, 3.2, 1.3), "T2": ((-6.0, 0.6), 4, 2.6, 1.0), "T3": ((-0.9, -5.2), 4, 1.6, 0.8),
    "T4": ((1.5, -6.6), 4, 1.3, 0.7), "T5a": ((4.4, -6.2), 4, 2.2, 1.0), "T5b": ((8.6, -3.8), 4, 2.6, 1.2),
    "T6": ((8.6, 3.5), 4, 3.0, 1.1), "T7": ((-7.8, 1.9), 4, 2.6, 1.0), "T8": ((0.4, 7.6), 4, 1.8, 0.8),
}
ROCK_RINGS = ((0.0, 0.92, 5), (0.3, 1.0, 5), (0.7, 0.8, 4), (1.0, 0.36, 3))
ROCK_RINGS_P = ((0.0, 0.92, 5), (0.32, 1.0, 5), (0.72, 0.62, 4), (1.0, 0.12, 1))
PEB_RINGS = ((0.0, 0.92, 4), (0.5, 1.0, 3), (1.0, 0.4, 1))
SINK_ROCK, SINK_PEB, SINK_HUB = 0.0, 0.0, 0.0      # fix round 1 (m6): every ground piece's base at build z 0
PAD_N = 6          # fix round 1 (budget): 6-vert lobed rims (12 tris a pad)
BURY, BURY_PLACE = 0.05, 0.03
BASE_INFO = {}


def _rock(a, c, size, yaw, seed, z0, lean=0.0, rings=ROCK_RINGS):
    """A pale grey angular block: the hull of jittered ring stacks (broad flat base, widest low, a shoulder, a flat
    sloping or pointed top leaning toward the trunk). Tones by height within the rock (light top, deep foot)."""
    rng = random.Random(seed)
    W, D, H = size
    to = -_away(c) * lean
    pts = m033._ring_pts(rng, rings, W / 2, D / 2, H, 0.08)
    tilt = rng.uniform(-0.12, 0.12)
    m = Matrix.Rotation(math.radians(yaw), 3, "Z")
    out = []
    for p in pts:
        q = m @ p
        f = q.z / H
        q += Vector((to.x * W * 0.5 * f, to.y * D * 0.5 * f, tilt * q.x * f))
        out.append(q + Vector((c[0], c[1], z0)))
    vs = m033._hull(a, out, ROCK)
    fs = _faces(vs)
    for f in fs:
        h = (f.calc_center_median().z - z0) / H
        if h > 0.68:
            f.material_index = a._mi(_mix(ROCK, ROCK_L, 0.5))
        elif h > 0.5:
            f.material_index = a._mi(_mix(ROCK, ROCK_L, 0.25))
        elif h < 0.22:
            f.material_index = a._mi(_mix(ROCK, ROCK_D, 0.25))
    _mottle(a, fs, 0.04, 0.4, seed)
    _tint(a, fs, 1.0 + rng.uniform(-0.03, 0.03))
    return vs


def rock(a, name):
    c, size, yaw, seed, lean, pointed = ROCKS[name]
    return _rock(a, c, size, yaw, seed, -SINK_ROCK, lean, ROCK_RINGS_P if pointed else ROCK_RINGS)


def pebble(a, c, s, seed):
    return _rock(a, c, (s, s * 0.85, s * 0.6), random.Random(seed).uniform(0, 180), seed, -SINK_PEB, 0.0, PEB_RINGS)


def _pad_shell(a, c, ux, uy, Lx, Ly, seed, guard):
    rng = random.Random(seed)
    bm = a.bm
    rim_pts = []
    for k in range(PAD_N):
        ang = 2 * math.pi * k / PAD_N + rng.uniform(-0.08, 0.08)
        rr = (1.0 if k % 2 == 0 else 0.8) * rng.uniform(0.92, 1.05)
        p = c + ux * (math.cos(ang) * Lx / 2 * rr) + uy * (math.sin(ang) * Ly / 2 * rr) + Vector((0, 0, 0.03))
        if guard is not None:
            for _ in range(12):
                if guard.point(p)[0] <= 0.0 and guard.point(p + Vector((0, 0, 0.06)))[0] <= 0.0:
                    break
                p = c + (p - c) * 0.88
                p.z = 0.03
        rim_pts.append(p)
    rim = [bm.verts.new(p) for p in rim_pts]
    top = bm.verts.new(c + Vector((0, 0, 0.11)))
    bot = bm.verts.new(Vector((c.x, c.y, 0.0)))
    fs = [bm.faces.new((rim[k], rim[(k + 1) % PAD_N], top)) for k in range(PAD_N)]
    fs += [bm.faces.new((rim[(k + 1) % PAD_N], rim[k], bot)) for k in range(PAD_N)]
    vs = rim + [top, bot]
    _close(a, vs, fs, MOSS)
    return vs, fs, rim, rim_pts, bot


def moss_pad(a, spec, guard=None):
    """A thin lobed lime moss pad (a closed lens: lobed 8-vert rim at z 0.03, top centre 0.11, bottom centre -0.02),
    between two roots; rim verts that would cut a root, the trunk or a rock are pulled in toward the pad centre, and a
    pad that still cuts one moves in toward the trunk, then shrinks; one that cannot clear is dropped."""
    az, r, Lx, Ly, seed = spec
    ux, uy = _u(az + 90), _u(az)
    res = None
    for dr, sc in ((0.0, 1.0), (-0.5, 1.0), (0.5, 1.0), (-0.5, 0.8), (0.0, 0.7), (0.6, 0.6), (-0.8, 0.55)):
        c = _u(az) * (r + dr)
        res = _pad_shell(a, c, ux, uy, Lx * sc, Ly * sc, seed, guard)
        if guard is None or guard.depth(res[0]) <= BURY_PLACE:
            break
        for v in res[0]:
            a.bm.verts.remove(v)
        res = None
    if res is None:
        BASE_INFO.setdefault("pads_dropped", []).append(az)
        return []
    vs, fs, rim, rim_pts, bot = res
    for k in range(PAD_N):            # the pad's outermost lobes fade to grass (position: the outer rim faces)
        if (rim_pts[k] - c).dot(uy) > 0.35 * Ly:
            for f in fs:
                if rim[k] in f.verts and bot not in f.verts:
                    f.material_index = a._mi(_mix(MOSS, GRASS, 0.25))
    _mottle(a, fs, 0.03, 0.2, seed)
    return vs


def blade(a, base, az, pitch, L, W, key, fold=0.28):
    """A closed folded lanceolate grass blade (fix round 1: 4 tris, a thin tetrahedron): broad near the base, pointed
    tip, the two blade edges folded forward so it has a back; seen face-on it is the same B-L-T-R lanceolate outline.
    Its face is turned as close to the front / back cameras as its lean allows (never edge-on)."""
    bm = a.bm
    B = Vector(base)
    d = Vector((math.cos(pitch) * math.cos(az), math.cos(pitch) * math.sin(az), math.sin(pitch)))
    side = d.cross(Vector((0, 1, 0)))
    side = side.normalized() if side.length > 0.2 else d.cross(Vector((1, 0, 0))).normalized()
    nrm = side.cross(d).normalized()
    T = bm.verts.new(B + d * L)
    Lp = bm.verts.new(B + d * (0.3 * L) - side * (W / 2) + nrm * (fold * W / 2))
    Rp = bm.verts.new(B + d * (0.3 * L) + side * (W / 2) + nrm * (fold * W / 2))
    Bv = bm.verts.new(B)
    fs = [bm.faces.new((Bv, Lp, T)), bm.faces.new((Bv, T, Rp)), bm.faces.new((Lp, Rp, T)),
          bm.faces.new((Bv, Rp, Lp))]
    vs = [Bv, Lp, T, Rp]
    _close(a, vs, fs, key)
    return vs


def tuft(a, name, guard=None):
    """A tall pointed lime tuft: a small 5-sided hub sunk 0.03, blades rising 60-85 deg from it, the taller outer
    blades lime, the inner / lower ones deep green. A blade that cuts a root, the trunk or a rock stands up, turns
    aside, then shortens; one that still cuts after its tries is dropped, never kept."""
    (cx, cy), n, H, R = TUFTS[name]
    rng = random.Random(sum(map(ord, name)) * 7 + 54500)
    bm = a.bm
    z0 = -SINK_HUB
    hr, hh = 0.3, 0.32
    yaw0 = rng.uniform(0, 6.28)
    # fix round 1 (budget): a 3-sided hub pyramid (4 tris), circumradius 0.36 so the blade bases stay inside it
    ring = [bm.verts.new(Vector((cx + math.cos(yaw0 + 2 * math.pi * k / 3) * 0.36,
                                 cy + math.sin(yaw0 + 2 * math.pi * k / 3) * 0.36, z0))) for k in range(3)]
    apex = bm.verts.new(Vector((cx, cy, z0 + hh)))
    fs = [bm.faces.new((ring[k], ring[(k + 1) % 3], apex)) for k in range(3)]
    fs.append(bm.faces.new(list(reversed(ring))))
    hub = ring + [apex]
    _close(a, hub, fs, _mix(GRASS_D, BARK_D, 0.25))
    info = BASE_INFO.setdefault(name, {"retried": 0, "dropped": 0})
    if guard is not None:
        info["hub_depth"] = round(guard.depth(hub), 3)
    out = list(hub)
    hs = [H * (rng.uniform(0.86, 1.0) if k % 2 == 0 else rng.uniform(0.55, 0.75)) for k in range(n)]
    for k in range(n):
        yaw = yaw0 + 2 * math.pi * k / n + rng.uniform(-0.25, 0.25)
        tall = hs[k] > 0.8 * H
        pitch = math.radians(rng.uniform(70, 82) if tall else rng.uniform(58, 68))
        L = hs[k] / math.sin(pitch)
        W = L / rng.uniform(3.6, 4.4)
        key = GRASS if tall else _mix(GRASS, GRASS_D, 0.5) if k % 3 else GRASS_D
        up = min(math.radians(86), pitch + math.radians(12))
        tries = [(0.0, pitch, 1.0), (0.0, up, 0.92), (0.4, up, 0.9), (-0.4, up, 0.9), (0.8, up, 0.85),
                 (-0.8, up, 0.85), (0.0, math.radians(86), 0.75)]
        vs = None
        for i, (dy, p_, s_) in enumerate(tries):
            y_ = yaw + dy
            base = (cx + math.cos(y_) * hr * 0.3, cy + math.sin(y_) * hr * 0.3, z0 + hh * 0.35)
            vs = blade(a, base, y_, p_, L * s_, W * s_, key)
            if guard is None or guard.depth(vs) <= BURY_PLACE:
                info["retried"] += i > 0
                break
            for v in vs:
                bm.verts.remove(v)
            vs = None
        if vs is None:
            info["dropped"] += 1
            continue
        _tint(a, _faces(vs), 1.0 + rng.uniform(-0.04, 0.04))
        out += vs
    return out


def _trunk_guard():
    g = m047._Solids()
    t = bpy.data.objects.get(PFX + "trunk_hero") or bpy.data.objects.get(TRUNK_P)
    if t is not None and OFF in t:
        off = Vector(t[OFF])
        me = t.data
        g.add([v.co + off for v in me.vertices], [list(p.vertices) for p in me.polygons], "trunk")
    return g


def root_base(a, part=False):
    """The six root modules (part: with pegs), rocks, pebbles, moss pads (hero only) and tufts, guarded."""
    BASE_INFO.clear()
    guard = _trunk_guard()
    for spec in ROOTS:
        vs = root(a, spec, peg=part)
        guard.add_vs([v for v in vs if v.is_valid], spec[0])
    rk = {}
    for name in ROCKS:
        vs = rock(a, name)
        rk[name] = round(guard.depth(vs), 3)
        guard.add_vs(vs, name)
    BASE_INFO["rocks_in_roots"] = rk
    for i, (c, s, seed) in enumerate(PEBBLES):
        guard.add_vs(pebble(a, c, s, seed), f"PB{i + 1}")
    if not part:
        for spec in PADS:
            moss_pad(a, spec, guard)
    for name in TUFTS:
        tuft(a, name, guard)


# ---- assemblies -------------------------------------------------------------------------------------------------------
def modules(a, peg=False):
    MOD_INFO.clear()
    return {name: module(a, name, peg=peg and name == "BM1") for name in BM}


def _shells_of(vs):
    """The closed shells (edge-connected vertex sets) that the verts vs belong to, pits' inset verts included."""
    seen, shells = set(), []
    for v0 in vs:
        if not v0.is_valid or v0 in seen:
            continue
        comp, st = [], [v0]
        seen.add(v0)
        while st:
            v = st.pop()
            comp.append(v)
            for e in v.link_edges:
                w = e.other_vert(v)
                if w not in seen:
                    seen.add(w)
                    st.append(w)
        shells.append(comp)
    return shells


def hero_rest(a):
    """Everything but the trunk core (unioned on its own and joined in): roots and base, modules, clumps. The cards
    keep out of the trunk and of every limb shell (m7)."""
    root_base(a)
    mods = modules(a)
    guard = _trunk_guard()
    for name, vs in mods.items():
        for i, sh in enumerate(_shells_of(vs)):
            guard.add_vs(sh, f"{name}_{i}")
    CARD_GUARD[:] = [guard]
    CLUMP_DROPPED.clear()
    global CARD_REC, CORE_SOL
    CARD_REC = []
    CORE_SOL = m047._Solids()
    try:
        for name in CLUMPS:
            leaf_clump(a, name)
        CLEARED[:] = _clear_cores(a)
        if REFINE[0]:
            REFINED[:] = _refine_cards(a)
    finally:
        CARD_GUARD.clear()
        CARD_REC = None
        CORE_SOL = None


def branch_part(a):
    MOD_INFO.clear()
    module(a, "BM1", peg=True)


def clump_part(a):
    MOD_INFO.clear()
    for name in BM:          # MOD_INFO for the feeding arm (the module itself is not built into the part)
        _mod_info_only(name)
    leaf_clump(a, "FL", stub=True)


def _mod_info_only(name):
    B = BM[name]
    info = MOD_INFO.setdefault(name, {})
    for arm, (apts, radii, n) in B["arms"].items():
        feed = B["feeds"].get(arm)
        if feed:
            apts = [Vector(p) for p in apts]
            info[arm] = dict(J=apts[-1].copy(), d=(apts[-1] - apts[-2]).normalized(), clump=feed,
                             pts=[p.copy() for p in apts])


def base_part(a):
    root_base(a, part=True)


# ---- objects ----------------------------------------------------------------------------------------------------------
NOTES = {
    HERO: "Broadleaf Tree: a round-crowned deciduous tree, a massive twisted six-strand orange-brown trunk with six "
          "split-toed roots, four plug-in branch modules feeding five clumps of overlapping lobed leaf cards (lime "
          "tops, green bodies, dark undersides) over dark cores, knot holes and bark pits; pale grey rocks, lime moss "
          "pads and tall lime grass tufts at the foot. No VFX",
    TRUNK_P: "Trunk Core: twisted six-strand body with three socket bosses, a top socket, six root stubs with sockets, "
             "a pale-rimmed oval knot, a hex-rimmed back knot, bark pits and an octagonal hollow underside",
    BRANCH_P: "Branch Module: the big Y (BM1) with its 8-sided base, round pale peg, upper arm and bare forked lower arm",
    CLUMP_P: "Leaf Clump (Module): the front-left clump with its branch stub, twigs, dark core and lobed leaf cards",
    BASE_P: "Root Base: six split-toed root modules with pegs, pale grey rocks, pebbles and lime grass tufts",
}
COLLISION = {HERO: "precise", TRUNK_P: "precise", BRANCH_P: "hull", CLUMP_P: "hull", BASE_P: "precise"}


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


def _post(o, uv=True):
    """Stage 2-3 pass for an object of closed shells: triangles, outward normals per shell, flat shading, origin at
    the bbox bottom centre, UVs (angle-based islands, overlaps cut free), bowties split."""
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
    if uv:
        M.smart_uv(o, **UV)
        lg["uv_cut"] = m012._uv_unfold(o)
    K.drop_unused_slots(o)
    return lg


def _carve(o, fn):
    """Exact difference of a cutter (fn's geometry, build frame) from o at the origin; cut faces take the cutter's
    material (hollow)."""
    a = K.fk().Asset(PFX + "cutter", "probe", seed=1, tint_var=0.0)
    fn(a)
    c = a.finish(collection=o.users_collection[0], mark_asset=False, origin=None)
    c.matrix_world = o.matrix_world
    bpy.context.view_layer.update()
    m = o.modifiers.new("Carve", "BOOLEAN")
    m.operation, m.solver, m.object = "DIFFERENCE", "EXACT", c
    m.material_mode = "TRANSFER"
    with M._override(o):
        bpy.ops.object.modifier_apply(modifier=m.name)
    me = c.data
    bpy.data.objects.remove(c, do_unlink=True)
    bpy.data.meshes.remove(me)
    K.drop_unused_slots(o)


MERGE_DEG = 4.0          # near-flat union seam verts merged away (the body's facets keep their verts)


def _make_trunk(part=False):
    t0 = time.time()
    SOCK.clear()
    name = TRUNK_P if part else PFX + "trunk_hero"
    o = _new(name, lambda a: trunk_part(a, part), "part", 1000, temp=not part)
    lg = {}
    m033._sane(o)
    lg["unions"] = m033._union_fine(o)
    _carve(o, _knot_cutter)
    lg["knot_rim_faces"] = _knot_rims(o)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
    # the unions split flat facets into fans of coplanar triangles: merge them back (same material only)
    n0 = len(bm.faces)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(MERGE_DEG), use_dissolve_boundaries=False, verts=bm.verts,
                             edges=bm.edges, delimit={"MATERIAL"})
    lg["coplanar_merged"] = n0 - len(bm.faces)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    lg["slivers_forced"] = m012._force_slivers(o, lim=2.5, max_len=0.2)
    if part:
        lg.update(_post(o))
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


def _make_shells(name, fn, role="part", budget=1000, temp=False, uv=True):
    o = _new(name, fn, role, budget, temp=temp)
    return o, _post(o, uv=uv)


def _make_hero(trunk):
    t0 = time.time()
    o = _new(HERO, hero_rest, "hero", 4000)
    c = bpy.data.objects.new(PFX + "trunkjoin", trunk.data.copy())
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


# ---- checks -----------------------------------------------------------------------------------------------------------
def _keys(o):
    return [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]


def _kind(ks, nf, zmin):
    if any("leaf" in k for k in ks):
        return "card" if nf <= 28 else "core"     # cards 16 tris, cores 36
    if any("grass" in k for k in ks) and not any("moss" in k for k in ks):
        return "hub" if any("bark" in k for k in ks) else "blade"
    if any("rock" in k for k in ks):
        return "rock"
    if any("bark" in k or "hollow" in k for k in ks):
        return "wood"
    if any("moss" in k for k in ks):
        return "pad"
    return "other"


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
        ks = {keys[f.material_index] for f in fs}
        zmin = min(v.co.z for f in fs for v in f.verts)
        kinds.append(_kind(ks, len(fs), zmin))
    wood = [k for k in range(n) if kinds[k] == "wood"]
    if wood:
        big = max(wood, key=lambda k: len(groups[k]))
        z0 = min(v.co.z for v in bm.verts)
        for k in wood:
            nf = len(groups[k])
            zmin = min(v.co.z for f in groups[k] for v in f.verts)
            if k == big and nf > 250:
                kinds[k] = "trunk"
            elif zmin - z0 < 0.1:
                kinds[k] = "root" if nf > 24 else "toe"
            else:
                kinds[k] = "limb" if nf > 24 else "twig"
    return bm, ids, n, groups, kinds


def shells_report(o):
    """Per shell: kind, tris, non-manifold edges / verts, boundary edges, winding errors (manifold edges whose two
    faces don't run the same way round), self-intersections, signed volume."""
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
        out.append({"kind": kinds[k], "tris": len(fs), "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary),
                    "winding_errors": sum(1 for e in es if e.is_manifold and not e.is_contiguous),
                    "self_hits": hits, "volume": round(vol, 4)})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating dressing: per shell, whether it touches another shell (triangles intersect, or a vertex within
    tol of another shell's surface) or the ground, and whether it chains by contact to an anchor (ground shells in
    the hero / root base; the trunk, the main limb run or the clump core in the parts)."""
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
    near = {}
    for i, j in tree.overlap(tree):
        a_, b_ = fsh[i], fsh[j]
        if a_ != b_:
            near[(min(a_, b_), max(a_, b_))] = 0.0
    for v in bm.verts:
        s = vsh.get(v.index)
        if s is None:
            continue
        for loc, _, fi, d in tree.find_nearest_range(v.co, chain_tol):
            t = fsh[fi]
            if t != s:
                kk = (min(s, t), max(s, t))
                near[kk] = min(near.get(kk, 1e9), d)
    gap = [1e9] * n
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    if any(kinds[k] in ("rock", "hub") for k in range(n)):
        ground = {k for k in range(n) if zmin[k] - z0 <= 0.12 and kinds[k] in ("trunk", "root", "toe", "rock", "pad",
                                                                                  "hub")}
    else:
        ground = {max(range(n), key=lambda k: len(groups[k]))}
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
    res = {"shells": n, "floating": len(floating), "floating_kinds": sorted({kinds[k] for k in floating}),
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "unchained": chained(tol), "kinds": {k: kinds.count(k) for k in sorted(set(kinds))}}
    bm.free()
    return res


def bury_report(o):
    """No buried dressing (STAGES): every tuft blade / hub, moss pad, leaf card and clump core tested by ray parity
    against the trunk, every root and toe and every rock shell (depth = distance from the deepest vert or face centre
    inside to that shell's surface); each rock against the trunk and roots. RootBase is tested against the trunk part
    brought into its frame. Cards are also checked against their core: card centre outside, <= 25 % verts inside."""
    bm, ids, n, groups, kinds = _shells(o)
    sol = m047._Solids()
    rocks = []
    for k in range(n):
        if kinds[k] in ("trunk", "root", "toe", "rock"):
            vs = list({v for f in groups[k] for v in f.verts})
            vi = {v: i for i, v in enumerate(vs)}
            sol.add([v.co for v in vs], [[vi[v] for v in f.verts] for f in groups[k]], f"{kinds[k]}{k}")
            if kinds[k] == "rock":
                rocks.append(k)
    t = bpy.data.objects.get(TRUNK_P)
    if "trunk" not in kinds and t is not None and o is not t and OFF in t and OFF in o and \
            any(kinds[k] in ("hub", "rock") for k in range(n)):
        sh = Vector(t[OFF]) - Vector(o[OFF])
        sol.add([v.co + sh for v in t.data.vertices], [list(p.vertices) for p in t.data.polygons], "trunk_part")
    off = Vector(o[OFF]) if OFF in o else Vector()
    res = []
    tested = 0
    for k in range(n):
        if kinds[k] not in ("blade", "hub", "pad", "card", "core"):
            continue
        tested += 1
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
    # cards against their own core
    cores = [k for k in range(n) if kinds[k] == "core"]
    csol = m047._Solids()
    for k in cores:
        vs = list({v for f in groups[k] for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        csol.add([v.co for v in vs], [[vi[v] for v in f.verts] for f in groups[k]], f"core{k}")
    card_bad, card_frac = [], []
    for k in range(n):
        if kinds[k] != "card":
            continue
        vs = list({v for f in groups[k] for v in f.verts})
        inn = sum(1 for v in vs if csol.point(v.co)[0] > 0.0)
        cen = sum((v.co for v in vs), Vector()) / len(vs)
        card_frac.append(inn / len(vs))
        if inn / len(vs) > 0.25 or csol.point(cen)[0] > 0.0:
            card_bad.append((round(inn / len(vs), 2), [round(x, 2) for x in cen + off]))
    bm.free()
    res.sort(key=lambda r: -r[0])
    rk.sort(key=lambda r: -r[0])
    return {"tested": tested, "solids": len(sol.items), "over_0.05": sum(1 for r in res if r[0] > BURY),
            "max": res[0][0] if res else 0.0, "worst": res[:6],
            "rocks_over_0.05": sum(1 for r in rk if r[0] > BURY), "rocks": rk[:6],
            "cards": len(card_frac), "cards_buried": len(card_bad), "cards_bad": card_bad[:6],
            "card_inside_frac_max": round(max(card_frac), 2) if card_frac else None}


def winding_total(shells):
    return sum(s["winding_errors"] for s in shells)


LIMB_VIEWS = {"front": (0, 5), "rear": (180, 5), "f34": (0, 13), "r34": (180, 13)}


def _cam(az, el):
    a_, e_ = math.radians(az), math.radians(el)
    return Vector((math.sin(a_) * math.cos(e_), -math.cos(a_) * math.cos(e_), math.sin(e_)))


def limb_visibility(h, views=LIMB_VIEWS, step=0.1):
    """Per module and view: the bare limb length seen (centreline samples whose ray to the camera clears every
    non-wood shell and the trunk), in studs along the limb; per bare fork: tine lengths seen. Polylines from
    LIMB_INFO (build frame)."""
    bm, ids, n, groups, kinds = _shells(h)
    off = Vector(h[OFF])
    keep = [f for k in range(n) if kinds[k] not in ("limb", "twig") for f in groups[k]]
    vs = list({v for f in keep for v in f.verts})
    vi = {v: i for i, v in enumerate(vs)}
    tree = BVHTree.FromPolygons([v.co + off for v in vs], [[vi[v] for v in f.verts] for f in keep])
    bm.free()
    out = {}
    for name, lines in LIMB_INFO.items():
        row = {}
        for vn, (az, el) in views.items():
            d = _cam(az, el)
            per = []
            for pts in lines:
                vis = 0.0
                for p, q in zip(pts, pts[1:]):
                    seg = Vector(q) - Vector(p)
                    m = max(1, int(seg.length / step))
                    for i in range(m):
                        c = Vector(p) + seg * ((i + 0.5) / m)
                        if tree.ray_cast(c, d, 200.0)[0] is None:
                            vis += seg.length / m
                per.append(round(vis, 2))
            row[vn] = per
        out[name] = row
    return out


# ---- build ------------------------------------------------------------------------------------------------------------
TARGET_SIZE = ((20.2, 1.0), (19.5, 1.6), (20.0, 0.4))
HERO_CEILING = 3950      # main session ruling after verification round 2 (was 3800), under the 4000 limit


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m054_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", "ShadeTree"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build_hero():
    """Trunk (unioned) + hero (tuning loop). Returns (hero, log)."""
    M.coll(NUM, TITLE)
    palette()
    LIMB_INFO.clear()
    CLUMP_INFO.clear()
    CLUMP_DROPPED.clear()
    PIT_COUNT.clear()
    m033.UNION_RETRIES.clear()
    trunk, lt = _make_trunk(part=False)
    trunk[OFF] = [0.0, 0.0, 0.0]
    h, lg = _make_hero(trunk)
    lg["trunk"] = lt
    lg["pits"] = dict(PIT_COUNT, total=sum(PIT_COUNT.values()))
    lg["cards_dropped"] = list(CLUMP_DROPPED)
    lg["cards_refaced"] = list(REFINED)
    lg["cards_cleared"] = list(CLEARED)
    return h, lg


def build(render=True, parts=True, close=True):
    t0 = time.time()
    h, lh = build_hero()
    log = {"hero": lh}
    objs = {}
    if parts:
        objs[TRUNK_P], log[TRUNK_P] = _make_trunk(part=True)
        objs[BRANCH_P], log[BRANCH_P] = _make_shells(BRANCH_P, branch_part)
        objs[CLUMP_P], log[CLUMP_P] = _make_shells(CLUMP_P, clump_part)
        objs[BASE_P], log[BASE_P] = _make_shells(BASE_P, base_part)
        # the hero's MOD_INFO / LIMB_INFO were overwritten by the parts: rebuild them (no geometry kept)
        a = K.fk().Asset(PFX + "info", "probe", seed=1, tint_var=0.0)
        LIMB_INFO.clear()
        modules(a)
        a.bm.free()
    _cleanup_tmp()
    order = [h] + [objs[n] for n in (TRUNK_P, BRANCH_P, CLUMP_P, BASE_P) if n in objs]
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
        lim = HERO_CEILING if o is h else 1000
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
            problems.append(f"{n_}: {c['floating']} floating shells ({c['floating_kinds']}), {c['unchained']} unchained")
    bury = {o.name: bury_report(o) for o in order if o.name in (HERO, BASE_P, CLUMP_P)}
    for n_, b in bury.items():
        if b["over_0.05"]:
            problems.append(f"{n_}: {b['over_0.05']} dressing shells more than {BURY} inside wood / rock "
                            f"(worst {b['worst'][:3]})")
        if b["rocks_over_0.05"]:
            problems.append(f"{n_}: {b['rocks_over_0.05']} rocks more than {BURY} into the trunk / roots")
        if b["cards_buried"]:
            problems.append(f"{n_}: {b['cards_buried']} cards buried in their core ({b['cards_bad'][:3]})")
    if parts and len(shells[TRUNK_P]) != 1:
        problems.append(f"{TRUNK_P}: {len(shells[TRUNK_P])} shells, expected 1")
    if sum(1 for s in shells[HERO] if s["kind"] == "trunk") != 1:
        problems.append(f"{HERO}: trunk shells != 1")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 14: none)")
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    vis = limb_visibility(h)
    kinds = {}
    for s in shells[HERO]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts", "origin_offset", "transforms_applied")} for au in audits],
           "hero_shells": kinds, "winding": {o: winding_total(s) for o, s in shells.items()},
           "contact": contact, "bury": bury, "base_info": dict(BASE_INFO), "clumps": dict(CLUMP_INFO),
           "limb_visibility": vis, "thin": thin, "log": log, "problems": problems, "uv": uv,
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders ----------------------------------------------------------------------------------------------------------
SHEET_VIEWS = {"f34_sheet": (0, 13), "r34_sheet": (180, 13), "front_sheet": (0, 5), "side_sheet": (90, 5),
               "rear_sheet": (180, 5), "top_sheet": (0, 89)}
VIEW_NAMES = ("front", "side", "rear", "top", "underside")
PARTS_SHOT = (20, 15)
SCALE_AT = (8.6, 1.2, 0.0)


def _scale_marker(h, at=SCALE_AT):
    a = K.fk().Asset(PFX + "char", "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=ROCK_D, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=ROCK_D, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=ROCK_D, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
    c.location = off @ Vector(at)
    bpy.context.view_layer.update()
    return c


def _temp(name, fn):
    o = _new(PFX + name, fn, "part", 1000, temp=True)
    return o


def _exploded(objs):
    """The parts laid out like the sheet's Exploded Construction: the root base, the trunk core lifted, the four branch
    modules drawn out along their boss axes and the five clumps lifted above them (built as temporary pieces)."""
    h = objs[0]
    x0, y0 = h.location.x + 70, h.location.y
    shown = []
    by = {o.name: o for o in objs}
    lift = Vector((0, 0, 4.0))
    for nm, dv in ((BASE_P, Vector((0, 0, 0))), (TRUNK_P, lift)):
        o = by.get(nm)
        if o is None:
            continue
        c = bpy.data.objects.new(f"{PFX}expl_{nm}", o.data)
        h.users_collection[0].objects.link(c)
        c.matrix_world = Matrix.Translation((x0, y0, 0)) @ Matrix.Translation(dv + Vector(o[OFF]))
        shown.append(c)
    a_axis = {"BM1": SOCK["B_L"]["d"], "BM2": SOCK["B_UL"]["d"], "BM3": Z, "BM4": SOCK["B_R"]["d"]}
    for nm in BM:
        o = _temp("mod_" + nm, lambda a, nm=nm: module(a, nm))
        o.matrix_world = Matrix.Translation((x0, y0, 0)) @ Matrix.Translation(lift + a_axis[nm] * 3.5)
        shown.append(o)
    cl_off = {"B": Vector((0, 2, 4.0)), "FL": Vector((-1.5, -2, 3.5)), "FR": Vector((1.5, -2, 3.5)),
              "L": Vector((-3.5, 0, 3.0)), "R": Vector((3.5, 0, 3.0))}
    for nm in CLUMPS:
        o = _temp("clump_" + nm, lambda a, nm=nm: leaf_clump(a, nm, stub=True))
        o.matrix_world = Matrix.Translation((x0, y0, 0)) @ Matrix.Translation(lift + cl_off[nm] + _clump_axis(nm) * 3.5)
        shown.append(o)
    bpy.context.view_layer.update()
    return shown


def _clump_axis(nm):
    for m, ar in MOD_INFO.items():
        for arm, info in ar.items():
            if info.get("clump") == nm:
                return info["d"]
    return Z


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    marker = _scale_marker(h)
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        extra["front34"] = ([h], -28, 12)
        extra["rear34"] = ([h], 152, 12)
        for o in objs[1:]:
            extra["part_" + o.name.replace("ShadeTree", "").lower()] = ([o], *PARTS_SHOT)
        if shown:
            extra["exploded"] = (shown, 0, 14)
        extra["scale"] = ([h, marker], 0, 6)
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
            if me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def _cut_clump(a):
    """The FL clump cut open (close-up 3): its stub, twigs and core with the cards in front of its centre left out."""
    leaf_clump(a, "FL", stub=True)
    cx, cy = CLUMPS["FL"]["c"]
    bm = a.bm
    bm.faces.ensure_lookup_table()
    # shells: delete card shells whose centre lies in front (-y) of the clump centre
    bm.faces.index_update()
    sid, ns = M._shell_ids(bm)
    groups = {}
    for f in bm.faces:
        groups.setdefault(sid[f.index], []).append(f)
    kill = []
    for k, fs in groups.items():
        if any(len(f.verts) >= 8 for f in fs) and len(fs) <= 16:      # a leaf card (apex fan + its rim face)
            c = sum((f.calc_center_median() for f in fs), Vector()) / len(fs)
            if c.y < cy - 0.4:
                kill += fs
    vs = list({v for f in kill for v in f.verts})
    bmesh.ops.delete(bm, geom=vs, context="VERTS")


def render_close_ups(objs):
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    by = {o.name: o for o in objs}
    h = objs[0]
    out = {}
    rc = m033.render_close

    def at(o, p):
        return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)
    kf = KNOT_INFO["front"]["S"]
    out["knot_cu"] = rc([h], f"{d}/knot_cu.png", -10, 5, at(h, kf), 1.9)
    out["trunk_cu"] = rc([h], f"{d}/trunk_cu.png", 0, 8, at(h, (0.3, -1.0, 6.2)), 5.2)
    rt = ROOT_INFO["RT3"]
    mid = (rt["F"] + rt["T0"]) / 2
    out["root_cu"] = rc([h], f"{d}/root_cu.png", -35, 16, at(h, mid), 3.3)
    out["limbs_cu"] = rc([h], f"{d}/limbs_cu.png", 0, 8, at(h, (0.5, -1.0, 11.0)), 6.0)
    if TRUNK_P in by:
        t = by[TRUNK_P]
        out["underside_part"] = rc([t], f"{d}/underside_part.png", 0, -80, at(t, (0, 0, 0.5)), 5.5)
        if BRANCH_P in by:
            b = by[BRANCH_P]
            s = SOCK["B_L"]
            c = bpy.data.objects.new(PFX + "join_bm1", b.data)
            t.users_collection[0].objects.link(c)
            c.matrix_world = t.matrix_world @ Matrix.Translation(-Vector(t[OFF])) @ \
                Matrix.Translation(s["d"] * 2.6 + Vector(b[OFF]))
            bpy.context.view_layer.update()
            try:
                out["join_cu"] = rc([t, c], f"{d}/join_cu.png", -25, 20, at(t, s["F"] + s["d"] * 1.4), 2.6)
            finally:
                bpy.data.objects.remove(c, do_unlink=True)
    cut = _temp("clumpcut", _cut_clump)
    try:
        P = CLUMPS["FL"]
        cut.location = h.location + Vector((0, -40, 0))
        bpy.context.view_layer.update()
        out["clump_cu"] = rc([cut], f"{d}/clump_cu.png", 15, -14,
                             cut.matrix_world @ Vector((P["c"][0], P["c"][1], P["zc0"] + 0.6)), 4.4)
    finally:
        me = cut.data
        bpy.data.objects.remove(cut, do_unlink=True)
        bpy.data.meshes.remove(me)
    return out


def preview(names=("f34_sheet", "front_sheet", "rear_sheet", "side_sheet", "top_sheet", "r34_sheet"), vfx=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig


def hero_only():
    h, lg = build_hero()
    _cleanup_tmp()
    others = [bpy.data.objects[n] for n in (TRUNK_P, BRANCH_P, CLUMP_P, BASE_P) if n in bpy.data.objects]
    M.display(NUM, [h] + others, TITLE)
    au = M.audit(h)
    sh = shells_report(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals")}, "log": lg,
            "winding": winding_total(sh), "kinds": {k: [sum(1 for s in sh if s["kind"] == k),
                                                         sum(s["tris"] for s in sh if s["kind"] == k)]
                                                     for k in sorted({s["kind"] for s in sh})},
            "clumps": dict(CLUMP_INFO)}
