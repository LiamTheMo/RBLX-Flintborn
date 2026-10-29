"""029 Ancient Root (references/029.png): a low, flat, faceted round stone slab ringed by chunky grey-mauve boulders,
a big faceted green egg (the sapstone) standing on the floor just right of centre, and two thick, gnarled, warm-orange
root halves arching over it - root L from a massive buttress foot (column + spur) at the front-left over the crest to
a blunt club end hanging at the upper right, root R from a domed top end standing behind L's crest down the right side
to a blunt foot - with two upright leaf fans (4 thick kite leaves each) growing from behind the two legs.

    import importlib, kit_models, m029; importlib.reload(kit_models); importlib.reload(m029); m029.build()

Parts as on the sheet's Exploded Construction, each built by its own function, all in one shared build frame (studs;
front -Y, +X right, ground z = 0, the base's plan centre at the origin). R08 owns AncientRoot* / GreenSapstone, so the
names are SapstoneRootArch* (M029_spec.md section 8, decision 10):
- SapstoneRootArchBase: Base. A lofted 14-gon slab (flat underside, a low rim, a slightly dished, gently undulating
  floor) with seven low rim lumps fused into its edge.
- SapstoneRootArchRock: Rocks (Side). One chunky hull boulder (the big front-left one).
- SapstoneRootArchSapstone: Green Sapstone. An icosphere (subdivision 1) warped into an egg, flat seat.
- SapstoneRootArchRootLeft: Root Half (Left). A 10-sided gnarled tube (3 creases, 2 knots, an elliptical foot) with
  a flattened spur fused at the foot and a domed club end.
- SapstoneRootArchRootRight: Root Half (Right). A 10-sided S-curved tube (3 creases and one sharp lit ridge, 2
  knots), a domed top end, its foot buried in the base.
- SapstoneRootArchLeafClump: Leaf Clump. Seven thick faceted kite leaves round a small hidden hub.

The hero (SapstoneRootArch) pastes the fused base, nine boulders, both roots, the egg and two leaf fans and unions them
one shell at a time into ONE closed shell (decision 6: the sapstone united, also shipped as its own part), cuts the
floor flat and cleans up. Colour (stage 4) is painted by position fields inside the builders before the union; the
union keeps each face's key and Tint. See M029_spec.md.
"""
import math
import os
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

NUM, TITLE, SHEET = 29, "Ancient Root", "M029"
OFF = "m029_offset"
PFX = "_m029_"
HERO = "SapstoneRootArch"

ROOT, ROOT_DARK, ROOT_LIGHT = "m029_root", "m029_root_dark", "m029_root_light"
BASE, BASE_DARK = "m029_base", "m029_base_dark"
ROCK, ROCK_LIGHT = "m029_rock", "m029_rock_light"
SAP, SAP_LIGHT, SAP_DARK = "m029_sap", "m029_sap_light", "m029_sap_dark"
LEAF, LEAF_TIP, LEAF_BASE = "m029_leaf", "m029_leaf_tip", "m029_leaf_base"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low_spec). Stage 4 (M029_spec.md "Stage 4"): pass 1 K.calibrate on the kit dome against
# TARGETS, pass 2 on the hero's f34_sheet render against the sheet's f34 region medians.
PALETTE = {ROOT: ("#93623E", 0.9, False), ROOT_DARK: ("#664125", 0.92, False), ROOT_LIGHT: ("#A46F49", 0.9, False),
           BASE: ("#69564C", 0.95, False), BASE_DARK: ("#5B4A40", 0.95, False),
           ROCK: ("#695954", 0.9, False), ROCK_LIGHT: ("#877B76", 0.88, False),
           SAP: ("#70A258", 0.55, False), SAP_LIGHT: ("#96CB6B", 0.55, False), SAP_DARK: ("#4E783E", 0.6, False),
           LEAF: ("#637708", 0.8, True), LEAF_TIP: ("#8EA618", 0.8, True), LEAF_BASE: ("#50620A", 0.8, True)}

# calibration targets: the sheet's rendered medians of unshadowed regions (spec section 5.4). key -> (sRGB, kind)
TARGETS = {ROOT: ((0xA0, 0x6A, 0x44), "brown"), ROOT_DARK: ((0x8C, 0x59, 0x35), "brown"),
           ROOT_LIGHT: ((0xB0, 0x74, 0x4B), "brown"),
           BASE: ((0x7B, 0x64, 0x58), "all"), BASE_DARK: ((0x6B, 0x56, 0x4B), "all"),
           ROCK: ((0x7A, 0x67, 0x62), "all"), ROCK_LIGHT: ((0xA2, 0x91, 0x8A), "all"),
           SAP: ((0x70, 0xA6, 0x60), "green"), SAP_LIGHT: ((0x86, 0xBC, 0x68), "green"),
           SAP_DARK: ((0x55, 0x7F, 0x48), "green"),
           LEAF: ((0x6E, 0x82, 0x09), "vivid"), LEAF_TIP: ((0x8C, 0xA5, 0x18), "vivid"),
           LEAF_BASE: ((0x56, 0x68, 0x0A), "vivid")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)


def calibrate(keys=None, iters=6, out_dir=None):
    """Pass 1: K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome. "all" keys are sampled with
    the paper/floor dropped (M.sample). Returns {key: (hex, rendered)}."""
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


# ---- colour helpers ---------------------------------------------------------------------------------------------------
STEPS = 3


def _q(t):
    """Quantise a mix to the 25 / 50 / 75 % steps."""
    return round(min(1.0, max(0.0, t)) * (STEPS + 1)) / (STEPS + 1)


def _mix(k1, k2, t):
    t = _q(t)
    return K.mix_key(k1, k2, t) if t else k1


def _ladder(lo, mid, hi):
    """lo, three lo->mid mixes, mid, three mid->hi mixes, hi (9 keys)."""
    return ([lo] + [K.mix_key(lo, mid, t) for t in (0.25, 0.5, 0.75)] + [mid] +
            [K.mix_key(mid, hi, t) for t in (0.25, 0.5, 0.75)] + [hi])


def _pick(lad, v, low, high):
    if v < (low[1] + high[0]) / 2:
        return lad[round(_q((v - low[0]) / (low[1] - low[0])) * 4)]
    return lad[4 + round(_q((v - high[0]) / (high[1] - high[0])) * 4)]


def _mottle(a, faces, amp, scale, seed, jitter=0.0):
    """Broad Tint patches about 1/scale studs across (never per-triangle confetti)."""
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in faces:
        c = f.calc_center_median()
        k = 1.0 + amp * 1.6 * noise.noise(c * scale + off) + (rng.uniform(-jitter, jitter) if jitter else 0.0)
        for l in f.loops:
            t = l[a.tint_layer][0] * k
            l[a.tint_layer] = (t, t, t, 1.0)


def _patch(n, level, mix, ramp=0.08):
    """A broad light patch: `mix` inside, then 50 % and 25 % rings across its edge (no hard patch edges)."""
    if n > level + ramp:
        return mix
    if n > level:
        return min(mix, 0.5)
    if n > level - ramp:
        return 0.25
    return 0.0


# ---- geometry helpers -------------------------------------------------------------------------------------------------
def _faces(verts):
    return K.faces_of([v for v in verts if v.is_valid])


def _strip(bm, r0, r1):
    n = len(r0)
    return [bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k])) for k in range(n)]


def _fanf(bm, ring, c, flip=False):
    n = len(ring)
    return [bm.faces.new((ring[(k + 1) % n], ring[k], c) if not flip else (ring[k], ring[(k + 1) % n], c))
            for k in range(n)]


def _tri(bm, faces):
    bmesh.ops.triangulate(bm, faces=[f for f in faces if f.is_valid and len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")


def _perp(t):
    a = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
    return (a - t * a.dot(t)).normalized()


def _catmull(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)


class _Path:
    """A Catmull-Rom curve through control points, sampled densely, queried by arc length."""

    def __init__(self, ctrl, diam, dense=24):
        P = [Vector(p) for p in ctrl]
        ext = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
        pts, ds = [], []
        for i in range(len(P) - 1):
            for j in range(dense):
                t = j / dense
                pts.append(_catmull(ext[i], ext[i + 1], ext[i + 2], ext[i + 3], t))
                ds.append(diam[i] + (diam[i + 1] - diam[i]) * t)
        pts.append(P[-1].copy())
        ds.append(diam[-1])
        acc = [0.0]
        for a_, b_ in zip(pts, pts[1:]):
            acc.append(acc[-1] + (b_ - a_).length)
        self.pts, self.ds, self.acc = pts, ds, acc
        self.L = acc[-1]

    def _idx(self, s):
        s = min(self.L, max(0.0, s))
        lo, hi = 0, len(self.acc) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if self.acc[m] <= s:
                lo = m
            else:
                hi = m
        seg = self.acc[hi] - self.acc[lo]
        return lo, hi, (s - self.acc[lo]) / seg if seg > 1e-9 else 0.0

    def at(self, s):
        lo, hi, u = self._idx(s)
        return self.pts[lo].lerp(self.pts[hi], u)

    def tan(self, s, h=0.08):
        return (self.at(min(self.L, s + h)) - self.at(max(0.0, s - h))).normalized()

    def diam(self, s):
        lo, hi, u = self._idx(s)
        return self.ds[lo] + (self.ds[hi] - self.ds[lo]) * u

    def nearest(self, p):
        """(s, point) of the curve point nearest p."""
        k = min(range(len(self.pts)), key=lambda i: (self.pts[i] - p).length_squared)
        return self.acc[k], self.pts[k]


def _stations(path, s0, s1, step, bend_step):
    n = max(1, round((s1 - s0) / step))
    base = [s0 + (s1 - s0) * i / n for i in range(n + 1)]
    out = [base[0]]
    for a_, b_ in zip(base, base[1:]):
        turn = path.tan(a_).angle(path.tan(b_))
        k = max(1, math.ceil((b_ - a_) / bend_step)) if turn > math.radians(20) else 1
        out += [a_ + (b_ - a_) * j / k for j in range(1, k + 1)]
    return out


def _align(z_axis, yaw=0.0):
    z = Vector(z_axis).normalized()
    return z.to_track_quat("Z", "Y").to_matrix() @ Matrix.Rotation(math.radians(yaw), 3, "Z")


# ---- Base -------------------------------------------------------------------------------------------------------------
SLAB = dict(rx=4.3, ry=3.4, n=14, seed=29001, jit=0.04)
# (z, radius fraction) from the flat underside up to the floor's edge (spec 1.4: bottom 0, bulge 0.25, rim top 0.45 at
# 0.92 R, floor edge 0.38 at 0.80 R); the floor's inner ring and centre after
# round 2: the outer bulge ring 0.25 -> 0.36 (a chunkier front lip, as on the exploded base and the base close-up)
SLAB_RINGS = ((-0.06, 1.0), (0.36, 1.03), (0.47, 0.93), (0.38, 0.80))
FLOOR_IN = (0.36, 0.45, 9)      # inner floor ring: z, radius fraction, verts
FLOOR_C = 0.35
FLOOR_UND = 0.06               # broad floor undulation (+-)
# broad radius sectors (+-6 %)
SLAB_SECT = ((2, 0.035), (3, 0.025), (5, 0.015))
# rim lumps (spec 2.1): azimuth (0 = +X, 90 = back), width, depth, top z, seed. Low fused shoulders on the slab edge.
# round 2: broader (1.5-1.9) and prouder (0.32-0.43 over the rim) fused lumps with broader tops
RIM_LUMPS = ((15.0, 1.8, 1.4, 0.86, 29011), (60.0, 1.7, 1.3, 0.82, 29012), (120.0, 1.9, 1.4, 0.9, 29013),
             (165.0, 1.6, 1.3, 0.84, 29014), (205.0, 1.7, 1.35, 0.8, 29015), (300.0, 1.5, 1.15, 0.78, 29016),
             (340.0, 1.8, 1.35, 0.86, 29017))
RIM_R = 0.97                   # rim lump centres at this fraction of the slab radius
RIM_BASE = -0.08
RIM_RINGS = [(0.0, 1.0, 6), (0.5, 0.97, 6), (1.0, 0.75, 5)]


def _slab_r(th):
    r = random.Random(SLAB["seed"])
    ph = [r.uniform(0, 6.3) for _ in SLAB_SECT]
    return 1.0 + sum(a * math.sin(k * th + p) for (k, a), p in zip(SLAB_SECT, ph))


def _slab_xy(th, rf):
    j = _slab_r(th)
    return math.cos(th) * SLAB["rx"] * rf * j, math.sin(th) * SLAB["ry"] * rf * j


def _floor_z(x, y):
    """The slab's floor height at (x, y) (inside the floor edge)."""
    nf = noise.noise(Vector((x * 0.32 + 11.0, y * 0.32 + 3.0, 0.5)))
    return FLOOR_C + FLOOR_UND * 1.6 * nf


def _ell(x, y):
    """Elliptical radius fraction of (x, y) against the slab outline."""
    th = math.atan2(y / SLAB["ry"], x / SLAB["rx"])
    return math.hypot(x / SLAB["rx"], y / SLAB["ry"]) / _slab_r(th)


def _slab(a):
    m = SLAB
    rng = random.Random(m["seed"])
    bm = a.bm
    rings = []
    for i, (z, rf) in enumerate(SLAB_RINGS):
        ring = []
        for k in range(m["n"]):
            th = 2 * math.pi * k / m["n"] + (math.pi / m["n"]) * (i % 2) * 0.5 + rng.uniform(-0.05, 0.05)
            x, y = _slab_xy(th, rf * (1 + rng.uniform(-m["jit"], m["jit"])))
            zz = z if i == 0 else (z + rng.uniform(-0.04, 0.04) if i < 3 else _floor_z(x, y) + 0.03)
            ring.append(bm.verts.new((x, y, zz)))
        rings.append(ring)
    zi, rfi, ni = FLOOR_IN
    inner = []
    for k in range(ni):
        th = 2 * math.pi * k / ni + rng.uniform(-0.08, 0.08)
        x, y = _slab_xy(th, rfi * (1 + rng.uniform(-0.06, 0.06)))
        inner.append(bm.verts.new((x, y, _floor_z(x, y))))
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        faces += _strip(bm, r0, r1)
    bot = bm.verts.new((0.0, 0.0, SLAB_RINGS[0][0]))
    faces += _fanf(bm, rings[0], bot, flip=True)
    # floor edge ring (14) -> inner ring (9): bridged by a triangle strip in angle order
    faces += _zip(bm, rings[-1], inner)
    c = bm.verts.new((0.1, 0.05, _floor_z(0.1, 0.05)))
    faces += _fanf(bm, inner, c)
    _tri(bm, faces)
    vs = [v for r in rings for v in r] + inner + [bot, c]
    a._finish(vs, BASE)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    return vs


def _zip(bm, A, B):
    """Triangles between two closed rings of different counts (both counter-clockwise, A outside B), by angle."""
    def ang(v):
        return math.atan2(v.co.y, v.co.x) % (2 * math.pi)
    a_ = sorted(A, key=ang)
    b_ = sorted(B, key=ang)
    i = j = 0
    out = []
    na, nb = len(a_), len(b_)
    # start both at their smallest angle
    while i < na or j < nb:
        ai, aj = a_[i % na], a_[(i + 1) % na]
        bi, bj = b_[j % nb], b_[(j + 1) % nb]
        ta = ang(aj) + (2 * math.pi if i + 1 >= na else 0)
        tb = ang(bj) + (2 * math.pi if j + 1 >= nb else 0)
        if j >= nb or (i < na and ta <= tb):
            out.append(bm.faces.new((ai, aj, bi)))
            i += 1
        else:
            out.append(bm.faces.new((ai, bj, bi)))
            j += 1
    return out


def _rim_lump(a, az, w, d, top, seed):
    th = math.radians(az)
    x, y = _slab_xy(th, RIM_R)
    vs = K.hull_rock(a, (w, d, top - RIM_BASE), loc=(x, y, RIM_BASE), seed=seed, mat=BASE, rings=RIM_RINGS,
                     jitter=0.1, rot=th, keep_bottom=True)
    return vs


BASE_FIELD = dict(edge=(0.08, 0.22, 0.5), contact=(0.45, 0.5), lump_top=(0.45, 0.25), patch_scale=0.55,
                  patch_level=0.18, patch_mix=0.25, seed=29021)
BASE_MOTTLE = dict(amp=0.05, scale=0.7, seed=29022, jitter=0.008)


def _contacts():
    """(x, y, radius) of every foot and boulder standing on the slab (for the floor's contact darkening)."""
    out = [(x, y, 0.5 * max(w, d)) for (x, y), (w, d, h), seed, yaw in BOULDERS.values()]
    out += [(-2.65, -1.5, 1.3), (-3.4, -1.55, 0.8), (4.5, -1.05, 0.5)]
    return out


def _paint_base(a, vs, contact=True):
    F = BASE_FIELD
    nf = K.noise_field(scale=F["patch_scale"], seed=F["seed"])
    cts = _contacts() if contact else []
    for f in _faces(vs):
        c = f.calc_center_median()
        z0, z1, mx = F["edge"]
        td = mx * min(1.0, max(0.0, (z1 - c.z) / (z1 - z0)))
        for x, y, r in cts:
            dd = math.hypot(c.x - x, c.y - y) - r
            if dd < F["contact"][0]:
                td = max(td, F["contact"][1] * (1 - max(0.0, dd) / F["contact"][0]))
        if _q(td):
            f.material_index = a._mi(_mix(BASE, BASE_DARK, td))
            continue
        tr = 0.0
        if c.z > F["lump_top"][0]:
            tr = F["lump_top"][1]
        tr = max(tr, _patch(nf(c), F["patch_level"], F["patch_mix"]))
        if _q(tr):
            f.material_index = a._mi(_mix(BASE, ROCK, tr))
    _mottle(a, _faces(vs), BASE_MOTTLE["amp"], BASE_MOTTLE["scale"], BASE_MOTTLE["seed"], BASE_MOTTLE["jitter"])


def base_raw(a, contact=True):
    vs = _slab(a)
    for az, w, d, top, seed in RIM_LUMPS:
        vs += _rim_lump(a, az, w, d, top, seed)
    _paint_base(a, vs, contact)
    return vs


# ---- Boulders ---------------------------------------------------------------------------------------------------------
# name -> ((x, y), (width, depth, height), seed, yaw deg) (spec 2.1)
BOULDERS = {
    "far_left": ((-4.3, 0.2), (1.0, 0.95, 0.9), 29101, 20.0),
    # round 2: the two front boulders x1.25 (the big front-left one was 0.13 W in the f34 against the sheet's 0.19)
    "front_left": ((-2.4, -2.6), (2.25, 1.9, 1.75), 29102, 10.0),
    "front_mid": ((-0.6, -2.7), (1.7, 1.5, 1.4), 29103, 35.0),
    "small": ((-0.35, -1.6), (0.95, 0.85, 0.7), 29104, 60.0),
    "right_mid": ((2.65, -1.0), (1.3, 1.15, 1.15), 29105, 15.0),   # round 2: larger (the sheet's, f34 top h .3)
    "right": ((3.5, -2.35), (1.25, 1.1, 1.0), 29106, 40.0),
    "back_a": ((-1.6, 3.15), (1.4, 1.2, 1.1), 29107, 25.0),
    "back_b": ((0.4, 3.35), (1.3, 1.15, 1.0), 29108, 70.0),
    "back_c": ((2.6, 2.85), (1.1, 1.0, 0.95), 29109, 5.0),
}
# chunky boulders (WorldModeling 12.1): a 5-6-sided footprint, a few big side facets, a broad quiet top
BOULDER_RINGS = [(0.0, 0.86, 6), (0.38, 1.0, 7), (0.8, 0.8, 6), (1.0, 0.55, 4)]
BOULDER_JIT = 0.15
BOULDER_SINK = 0.15
ROCK_FIELD = dict(top=(0.45, 0.9, 0.5), low=(0.12, 0.25), patch_scale=1.1, patch_amp=0.55)
ROCK_MOTTLE = dict(amp=0.06, scale=0.5, seed=29121, jitter=0.012)
BOULDER_INFO = {}


def _boulder_base(x, y):
    """A boulder on the floor sinks BOULDER_SINK into it; one on the rim stands on the ground (floor-cut)."""
    return -0.1 if _ell(x, y) > 0.84 else _floor_z(x, y) - BOULDER_SINK


def _boulder(a, name, at_origin=False):
    (x, y), (w, d, h), seed, yaw = BOULDERS[name]
    z0 = 0.0 if at_origin else _boulder_base(x, y)
    if at_origin:
        x = y = 0.0
    hh = h + (0.0 if at_origin else max(0.0, -z0 if z0 < 0 else 0.0))
    vs = K.hull_rock(a, (w, d, hh), loc=(x, y, z0), seed=seed, mat=ROCK, rings=BOULDER_RINGS, jitter=BOULDER_JIT,
                     rot=math.radians(yaw), keep_bottom=True)
    zs = [v.co.z for v in vs]
    lo, hi = max(0.0, min(zs)), max(zs)
    BOULDER_INFO[name] = {"base": round(z0, 2), "top": round(hi, 2)}
    tz, tf, tm = ROCK_FIELD["top"]
    nf = K.noise_field(scale=ROCK_FIELD["patch_scale"], seed=seed)
    for f in _faces(vs):
        c = f.calc_center_median()
        u = (c.z - lo) / max(1e-3, hi - lo)
        # the greyer weathered top (Rock (Secondary)) by height within the boulder, broken by broad patches that run
        # down the sides and gaps on the top, so the grey follows the stone's weathering, not its facing
        t = tm * min(1.0, max(0.0, (u - tz) / (tf - tz))) + ROCK_FIELD["patch_amp"] * nf(c)
        if _q(t):
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, min(tm, t)))
        elif u < ROCK_FIELD["low"][0]:
            f.material_index = a._mi(_mix(ROCK, BASE_DARK, ROCK_FIELD["low"][1]))
    _mottle(a, _faces(vs), ROCK_MOTTLE["amp"], ROCK_MOTTLE["scale"], ROCK_MOTTLE["seed"] + seed,
            ROCK_MOTTLE["jitter"])
    return vs


def boulders(a):
    vs = []
    for name in BOULDERS:
        vs += _boulder(a, name)
    return vs


# ---- Sapstone ---------------------------------------------------------------------------------------------------------
SAP_C = (1.18, 0.0)       # round 1b 1.0 -> 1.3 (f34 egg centre .543, sheet .597); round 2 1.18 (L hugs it)
SAP_BOTTOM = 0.30
SAP_SIZE = (2.65, 2.45, 3.65)   # round 2: H 3.45 -> 3.65 (the f34 egg top at h .66, sheet .68)
SAP_EQ = 0.45          # widest at this fraction of the height
SAP_TAPER = 0.22       # radius x (1 - taper t) above the equator
SAP_LEAN = 4.0         # degrees toward -X
SAP_SEED = 29201
# the egg's darker foot is mostly the floor's shade (lighting), so the paint keeps only the seat ring dark; the light
# upper body and broad mineral patches by position (a stronger height ramp failed K.check: corr 0.81 with facing)
SAP_FIELD = dict(dark=(0.0, 0.06), light=(0.5, 0.95, 0.25), patch_scale=1.0, patch_amp=0.75)
SAP_MOTTLE = dict(amp=0.03, scale=0.6, seed=29202)


# the sheet's egg: width / max width at h = 0, .1 .. 1 (spec 1.4), slightly fuller at the ends so the coarse
# icosphere's vertex rings don't pinch it into a crystal point
SAP_PROFILE = ((0.0, 0.3), (0.1, 0.68), (0.2, 0.86), (0.3, 0.93), (0.4, 0.98), (0.5, 1.0), (0.6, 0.96), (0.7, 0.89),
               (0.8, 0.78), (0.9, 0.57), (1.0, 0.16))   # round 2: fuller shoulders (the sheet's broad egg top)


def _interp(tab, x):
    if x <= tab[0][0]:
        return tab[0][1]
    for (x0, y0), (x1, y1) in zip(tab, tab[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return tab[-1][1]


SAP_TURN = (21.0, 13.0, 9.0)   # the icosphere turned first (deg about X, Y, Z): no pole vertex on top, so the egg
#                                reads as a faceted egg, not a five-sided crystal point
SAP_SEAT = 0.05                # verts within this fraction of H of the bottom flattened into the seat


def _sapstone(a, at_origin=False):
    rng = random.Random(SAP_SEED)
    tmp = bmesh.new()
    # bmesh's subdivisions=2 is the "icosphere subdivision 1" of the spec (42 verts, 80 tris); subdivisions=1 is the
    # bare icosahedron (12 verts), which read as a crystal point
    bmesh.ops.create_icosphere(tmp, subdivisions=2, radius=1.0)
    turn = (Matrix.Rotation(math.radians(SAP_TURN[2]), 3, "Z") @ Matrix.Rotation(math.radians(SAP_TURN[1]), 3, "Y")
            @ Matrix.Rotation(math.radians(SAP_TURN[0]), 3, "X"))
    W, D, H = SAP_SIZE
    pts = []
    for v in tmp.verts:
        x, y, z = (turn @ v.co.normalized())
        z = max(-1.0, min(1.0, z))
        # each vertex keeps its direction round the axis; its height comes from its latitude and its radius from the
        # sheet's egg width profile at that height (spec 1.4: widest at h .4-.5, a narrower top, a rounder bottom)
        lat = math.asin(z)
        h = 0.5 + lat / math.pi
        hz = (h / 0.5 * SAP_EQ) if h <= 0.5 else SAP_EQ + (h - 0.5) / 0.5 * (1 - SAP_EQ)
        rxy = math.hypot(x, y)
        k = _interp(SAP_PROFILE, hz) / max(rxy, 1e-6) * (1 + rng.uniform(-0.03, 0.03)) if rxy > 1e-6 else 0.0
        pts.append(Vector((x * k, y * k, hz + rng.uniform(-0.01, 0.01))))
    # normalised to the exact size, then the flat seat
    xs, ys, zs = ([p[i] for p in pts] for i in range(3))
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    sx, sy = W / (max(xs) - min(xs)), D / (max(ys) - min(ys))
    sz_ = H / (1 - SAP_SEAT) / (max(zs) - min(zs))      # the seat takes SAP_SEAT off the bottom
    pts = [Vector(((p.x - cx) * sx, (p.y - cy) * sy, (p.z - min(zs)) * sz_)) for p in pts]
    sz = SAP_SEAT * H
    for p in pts:
        if p.z < sz:
            p.z = sz - 0.005
    lean = Matrix.Rotation(math.radians(-SAP_LEAN), 3, "Y")
    bm = a.bm
    loc = Vector((0, 0, 0)) if at_origin else Vector((SAP_C[0], SAP_C[1], SAP_BOTTOM))
    vmap = {}
    for v, p in zip(tmp.verts, pts):
        q = lean @ (p - Vector((0, 0, sz)))
        vmap[v] = bm.verts.new(q + loc)
    for f in tmp.faces:
        bm.faces.new([vmap[v] for v in f.verts])
    tmp.free()
    vs = list(vmap.values())
    a._finish(vs, SAP)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    zs = [v.co.z for v in vs]
    lo, hi = min(zs), max(zs)
    d0, d1 = SAP_FIELD["dark"]
    l0, l1, lm = SAP_FIELD["light"]
    nf = K.noise_field(scale=SAP_FIELD["patch_scale"], seed=SAP_SEED)
    for f in _faces(vs):
        c = f.calc_center_median()
        u = (c.z - lo) / (hi - lo)
        n = nf(c) * SAP_FIELD["patch_amp"]
        # a darker foot and a lighter upper body by height, broken by broad mineral patches (position noise)
        td = (1.0 - max(0.0, (u - d0) / (d1 - d0))) * 0.75 - n
        tl = lm * min(1.0, max(0.0, (u - l0) / (l1 - l0))) + n
        if _q(td) and u < d1 + 0.15:
            f.material_index = a._mi(_mix(SAP, SAP_DARK, td))
        elif _q(tl):
            f.material_index = a._mi(_mix(SAP, SAP_LIGHT, min(0.75, tl)))
        elif n < -0.18:
            f.material_index = a._mi(_mix(SAP, SAP_DARK, 0.25))
    _mottle(a, _faces(vs), SAP_MOTTLE["amp"], SAP_MOTTLE["scale"], SAP_MOTTLE["seed"])
    return vs


# ---- Roots ------------------------------------------------------------------------------------------------------------
# Centre-line control points (build frame, studs) and diameters (spec section 2.2). Feet run on below the ground and
# into the slab (the floor cut and the union make the contact line).
ROOTS = {
    # round 1b: a flat crest (top z 6.0-6.2 over X -0.3 .. 1.4, f34 h .96-.99 over f .40-.75) and the club end
    # hooking down at X 2.5 onto R's shoulder; the foot a broad buttress (f34 h .3 run 3.1-3.4 studs wide)
    # round 2: the leg moved 0.45 right onto the egg's left flank (f34 inner edge on the sheet's), the crest bend
    # started lower (0.0, -0.75, 4.85) and thicker (1.85); the club end no longer hooks down (a curl-under shelf, and
    # from the r34 a pipe-end pocket): the crest runs on and dives down-back into R's shoulder (its dome buried
    # 0.4 inside R), so L flows into R's descent; the foot ellipse 1.2 : 1 (a deeper leg from the r34)
    "L": dict(ctrl=[(-2.95, -1.6, -0.5), (-2.65, -1.5, 0.55), (-1.6, -1.3, 1.57), (-1.0, -1.1, 2.91),
                    (-0.4, -0.9, 4.2), (0.0, -0.75, 4.85), (0.7, -0.62, 5.2), (1.35, -0.5, 5.1),
                    (1.8, -0.45, 4.5), (2.08, -0.4, 3.8), (2.32, -0.35, 3.2)],
              diam=[3.0, 2.8, 2.45, 2.15, 1.95, 1.9, 1.85, 1.75, 1.6, 1.25, 0.8],
              sides=10, seed=29301, start="buried", end="dome", ellipse=((1, 0, 0), 1.2, 2.4),
              creases=((1, 1.0), (4, 1.0), (7, 1.0)), crease=(0.16, 0.95),
              ridges=((9, 0.05), (5, 0.04)),
              knots=((0.3, 0.15, 0.38), (0.62, 0.13, 0.36))),
    "spur": dict(ctrl=[(-2.4, -1.45, 0.8), (-2.95, -1.5, 0.55), (-3.5, -1.55, 0.42), (-4.25, -1.6, 0.32)],
                 diam=[1.7, 1.55, 1.0, 0.62], sides=8, seed=29302, start="buried", end="dome", flat=0.7,
                 creases=((2, 1.0), (5, 0.9)), crease=(0.09, 0.5), ridges=(), knots=()),
    # round 2: the top end a broad hump (Ø 1.6 at (-0.35, 0.75, 5.45)) standing behind L's crest; its end dives
    # into the back of L's leg (the two roots twist together, no log end showing); the descent pulled in against
    # the egg's right flank
    "R": dict(ctrl=[(-1.1, -0.55, 3.8), (-1.2, 0.15, 4.55), (-1.0, 0.55, 5.0), (-0.45, 0.75, 5.3), (0.25, 0.68, 5.3),
                    (0.95, 0.4, 4.95), (1.62, 0.0, 3.95), (2.28, -0.2, 3.4), (2.95, -0.4, 2.74), (3.32, -0.6, 2.09),
                    (3.68, -0.8, 1.45),
                    (4.3, -0.95, 0.8), (4.5, -1.05, 0.45), (4.62, -1.1, -0.35)],
              diam=[1.3, 1.4, 1.5, 1.6, 1.55, 1.55, 1.5, 1.4, 1.3, 1.3, 1.15, 0.95, 0.85, 0.85],
              sides=10, seed=29303, start="dome", end="buried",
              creases=((2, 1.0), (5, 1.0), (8, 1.0)), crease=(0.14, 0.6), ridges=((0, 0.06),),
              knots=((0.05, 0.1, 0.3), (0.3, 0.13, 0.35), (0.62, 0.12, 0.33))),
}
STEP, STEP_BEND = 0.9, 0.38     # round 1b: 0.55 -> 0.68; round 2 0.9 (long facets, 1-2 studs as drawn)
TWIST = (12.0, 0.45)       # crease wander: +-deg, per stud (spec: +-15 deg round the limb)
VJIT = (0.03, 0.13)       # per-vertex radius jitter (fraction; round 2 0.06 -> 0.03, crisper grooves between long
#                           facets) and slide along the limb (studs): irregular facets
ROOT_INFO = {}
ROOT_PATHS = {}


def _sect(th, s, ph):
    """Broad radius sectors (+-8 %)."""
    return 1.0 + 0.045 * math.sin(2 * th + ph[0] + 0.3 * s) + 0.03 * math.sin(3 * th + ph[1] - 0.22 * s)


def _root_path(name):
    R = ROOTS[name]
    p = _Path(R["ctrl"], R["diam"])
    ROOT_PATHS[name] = p
    return p


ROOT_FIELD = dict(foot=(0.1, 0.36, 1.0), under=(0.62, 0.25), crest=(3.5, 4.6, 0.75), r_crest=0.25, patch_scale=0.7,
                  patch_level=0.22, patch_mix=0.5, seed=29321)
ROOT_MOTTLE = dict(amp=0.05, scale=0.5, seed=29322, jitter=0.008)


def _tube(a, name, paint=True):
    """One gnarled root tube: rings along the path, each 10-sided ring set in the local up frame (column 0 at the
    top), radius from the diameter list x broad sectors x knots, crease columns pulled in (V-grooves), ridge columns
    pushed out; the whole ring twisted slowly (+-TWIST) so the creases wander. Caps: 'dome' (2 rings to a raised
    centre) or 'buried' (a flat fan; inside the base or the foot). Returns verts."""
    R = ROOTS[name]
    path = _root_path(name)
    rng = random.Random(R["seed"])
    ph = [rng.uniform(0, 6.3) for _ in range(4)]
    sides = R["sides"]
    L = path.L
    sts = _stations(path, 0.0, L, STEP, STEP_BEND)
    bm = a.bm
    crease_d, r_ref = R["crease"]
    rings, ring_s, ring_c, ring_r, ring_t = [], [], [], [], []
    vdown = {}
    n_prev = None
    up = Vector((0, 0, 1))
    for i, s in enumerate(sts):
        c = path.at(s)
        t = path.tan(s)
        nu = up - t * up.dot(t)
        if nu.length > 0.25:
            n = nu.normalized()
        else:
            n = (n_prev - t * n_prev.dot(t)).normalized()
        n_prev = n
        b = t.cross(n)
        r = path.diam(s) / 2
        knot = 1.0 + sum(A * math.exp(-((s - f * L) / w) ** 2) for f, A, w in R["knots"])
        tw = math.radians(TWIST[0]) * math.sin(TWIST[1] * s + ph[2]) + math.radians(rng.uniform(-3, 3))
        # creases fade out over the last 0.4 stud at a capped end
        fade = 1.0
        if R["end"] == "dome":
            fade = min(fade, max(0.0, (L - s) / 0.6))
        if R["start"] == "dome":
            fade = min(fade, max(0.0, s / 0.6))
        cd = crease_d * min(1.1, max(0.6, r / r_ref)) * fade
        kappa = path.tan(max(0.0, s - 0.3)).angle(path.tan(min(L, s + 0.3)), 0.0) / 0.6
        slide_k = min(1.0, max(0.0, (1 - r * kappa - 0.3) / 0.4))
        ring = []
        for k in range(sides):
            th = tw + 2 * math.pi * k / sides
            radial = n * math.cos(th) + b * math.sin(th)
            rr = r * knot * _sect(th, s, ph) * (1 + rng.uniform(-VJIT[0], VJIT[0]))
            for cr in R["creases"]:
                col, w = cr[:2]
                if k == col:
                    if len(cr) > 2:
                        # a foot-only groove: full up to s/L = cr[2], gone by cr[3]
                        w *= min(1.0, max(0.0, (cr[3] - s / L) / (cr[3] - cr[2])))
                    rr -= cd * w
            for col, h in R.get("ridges", ()):
                if k == col:
                    rr += h * fade
            off = radial * rr
            if "flat" in R:
                u = off.dot(n)
                off = off - n * u * (1 - R["flat"])
            if "ellipse" in R:
                ax, ratio, flen = R["ellipse"]
                if s < flen:
                    e = 1 + (math.sqrt(ratio) - 1) * (1 - s / flen)
                    axp = Vector(ax) - t * Vector(ax).dot(t)
                    if axp.length > 1e-3:
                        axp.normalize()
                        u = off.dot(axp)
                        off = off + axp * u * (e - 1) - (off - axp * u) * (1 - 1 / e)
            # irregular facets: each vertex slid a little along the limb (not at the ends, less round tight bends,
            # where the rings crowd on the inner side and a slide would fold them through each other)
            sl = rng.uniform(-VJIT[1], VJIT[1]) * slide_k if 0 < i < len(sts) - 1 else 0.0
            v = bm.verts.new(c + off + t * sl)
            vdown[v] = -math.cos(th)
            ring.append(v)
        rings.append(ring)
        ring_s.append(s)
        ring_c.append(c)
        ring_r.append(r)
        ring_t.append(t)
    verts = [v for rg in rings for v in rg]
    faces = []
    for i in range(len(rings) - 1):
        faces += _strip(bm, rings[i], rings[i + 1])

    def cap(ring, c, ax, r, kind, s_val):
        if kind == "dome":
            cen = sum((v.co for v in ring), Vector()) / len(ring)
            dome = [bm.verts.new(cen + (v.co - cen) * 0.74 + ax * r * 0.32) for v in ring]
            cv = bm.verts.new(cen + ax * r * 0.5)
            fs = _strip(bm, ring, dome) + _fanf(bm, dome, cv)
            nv = dome + [cv]
        else:
            cen = sum((v.co for v in ring), Vector()) / len(ring)
            cv = bm.verts.new(cen + ax * 0.08)
            fs = _fanf(bm, ring, cv)
            nv = [cv]
        for v in nv:
            vdown[v] = 0.0
        return fs, nv
    fs, nv = cap(rings[-1], ring_c[-1], ring_t[-1], ring_r[-1], R["end"], ring_s[-1])
    faces += fs
    verts += nv
    end_v = set(nv)
    fs, nv = cap(list(reversed(rings[0])), ring_c[0], -ring_t[0], ring_r[0], R["start"], ring_s[0])
    faces += fs
    verts += nv
    start_v = set(nv)
    a._finish(verts, ROOT)
    _tri(bm, faces)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(verts))
    s_of = {v: ring_s[i] for i, rg in enumerate(rings) for v in rg}
    for v in end_v:
        s_of[v] = L
    for v in start_v:
        s_of[v] = 0.0
    ROOT_INFO[name] = {"L": round(L, 2), "rings": len(rings), "sides": sides,
                       "stations": [(tuple(round(x, 3) for x in c), round(r, 3), round(s, 3))
                                    for c, r, s in zip(ring_c, ring_r, ring_s)]}
    if paint:
        _paint_root(a, name, verts, s_of, vdown)
    return verts


def _paint_root(a, name, verts, s_of, vdown):
    """Root colour by position: darker toward each foot (arc length from the foot) and on the lower part of each
    section (section-frame position), lighter on the crest (world z), broad light patches; never by facing."""
    F = ROOT_FIELD
    R = ROOTS[name]
    L = ROOT_INFO[name]["L"]
    nf = K.noise_field(scale=F["patch_scale"], seed=F["seed"] + R["seed"])
    f0, f1, fm = F["foot"]
    for f in _faces(verts):
        c = f.calc_center_median()
        ss = [s_of[v] for v in f.verts if v in s_of]
        s = sum(ss) / len(ss) if ss else 0.0
        if name == "spur":
            u_foot = 0.0
        elif name == "L":
            u_foot = s / L
        else:
            u_foot = (L - s) / L
        td = fm * min(1.0, max(0.0, (f1 - u_foot) / (f1 - f0)))
        down = sum(vdown.get(v, 0.0) for v in f.verts) / len(f.verts)
        if down > F["under"][0] and c.z < 3.5:     # round 2: not on the crest (its underside is lit-side dark)
            td = max(td, F["under"][1])
        if _q(td):
            f.material_index = a._mi(_mix(ROOT, ROOT_DARK, td))
            continue
        z0, z1, zm = F["crest"]
        if name == "R" and c.y > 0.2 and c.x < 0.5:
            # round 2: R's hump standing behind L's crest keeps the plain mid brown (25 % light at most), so the
            # two roots read apart where they cross, as drawn (by position: the back half of the hump)
            zm = F["r_crest"]
        tl = zm * min(1.0, max(0.0, (c.z - z0) / (z1 - z0)))
        tl = max(tl, _patch(nf(c), F["patch_level"], F["patch_mix"]) * (1.0 if c.z > 1.5 else 0.5))
        if _q(tl):
            f.material_index = a._mi(_mix(ROOT, ROOT_LIGHT, tl))
    _mottle(a, _faces(verts), ROOT_MOTTLE["amp"], ROOT_MOTTLE["scale"], ROOT_MOTTLE["seed"] + R["seed"],
            ROOT_MOTTLE["jitter"])


def root_left_raw(a):
    return _tube(a, "L") + _tube(a, "spur")


def root_right_raw(a):
    return _tube(a, "R")


# ---- Leaves -----------------------------------------------------------------------------------------------------------
KITE = ((0.18, 0.42), (0.42, 0.5), (0.72, 0.42))  # (t, half width / W): shoulder, belly, pre-tip (round 1b: the sheet's
#                                                    long hexagonal kite: near-parallel sides, a short sharp tip)
RIDGE = ((0.42, 0.11), (0.72, 0.07))              # front ridge (t, height / L); round 2 0.075 -> 0.11 (a crisp
KEEL = ((0.42, 0.08), (0.72, 0.05))               # lit half and dark half); back ridge 0.06 -> 0.08
NECK = 0.07                                        # half width of the leaf's neck (no shared hub point)
LEAF_W = 0.48                                      # W : L
LEAF_BANDS = ((0.1, 0.3), (0.62, 0.84))
LEAF_NOISE = 0.06
LEAF_MOTTLE = dict(amp=0.035, scale=0.5, seed=29421)


def _leaf(a, base, D, N, L, seed, roll=0.0, cup=0.0, w=LEAF_W):
    """One thick faceted kite leaf from `base` along unit D, its face turned toward N: a neck, a widest point at 0.42
    L, a sharp tip, a front ridge and a back keel (so it has a lit half and a dark half). Painted base -> mid -> tip
    along its length. Returns verts."""
    rng = random.Random(seed)
    bm = a.bm
    D = Vector(D).normalized()
    S = D.cross(Vector(N)).normalized()
    Nn = S.cross(D).normalized()
    rl = math.radians(roll)
    S, Nn = S * math.cos(rl) + Nn * math.sin(rl), Nn * math.cos(rl) - S * math.sin(rl)
    B = Vector(base)
    W = w * L
    tm = {}

    def vert(t, y, z):
        v = bm.verts.new(B + D * (t * L) + S * y + Nn * z)
        tm[v] = t
        return v
    b0 = vert(0.0, -NECK, 0.0)
    b1 = vert(0.0, NECK, 0.0)
    tip = vert(1.0, 0.0, 0.0)
    right = [vert(t, -h * W * (1 + rng.uniform(-0.06, 0.06)), -cup * h * W) for t, h in KITE]
    left = [vert(t, h * W * (1 + rng.uniform(-0.06, 0.06)), -cup * h * W) for t, h in KITE]
    r1 = vert(RIDGE[0][0], 0.0, RIDGE[0][1] * L)
    r2 = vert(RIDGE[1][0], 0.0, RIDGE[1][1] * L)
    k1 = vert(KEEL[0][0], 0.0, -KEEL[0][1] * L - cup * 0.5 * W)
    k2 = vert(KEEL[1][0], 0.0, -KEEL[1][1] * L - cup * 0.3 * W)
    R1, R2, R3 = right
    L1, L2, L3 = left
    front = [(b0, R1, r1), (R1, R2, r1), (R2, r2, r1), (R2, R3, r2), (R3, tip, r2), (tip, L3, r2), (L3, L2, r2),
             (L2, r1, r2), (L2, L1, r1), (L1, b1, r1), (b1, b0, r1)]
    back = [(R1, b0, k1), (R2, R1, k1), (k2, R2, k1), (R3, R2, k2), (tip, R3, k2), (L3, tip, k2), (L2, L3, k2),
            (k1, L2, k2), (L1, L2, k1), (b1, L1, k1), (b0, b1, k1)]
    fs = [bm.faces.new(t) for t in front + back]
    vs = [b0, b1, tip] + right + left + [r1, r2, k1, k2]
    a._finish(vs, LEAF)
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    lad = _ladder(LEAF_BASE, LEAF, LEAF_TIP)
    for f in fs:
        t = sum(tm[v] for v in f.verts) / len(f.verts) + rng.uniform(-LEAF_NOISE, LEAF_NOISE)
        f.material_index = a._mi(_pick(lad, t, LEAF_BANDS[0], LEAF_BANDS[1]))
    return vs


def _dir(yaw, pitch):
    y, p = math.radians(yaw), math.radians(pitch)
    return Vector((math.cos(p) * math.cos(y), math.cos(p) * math.sin(y), math.sin(p)))


# hero fans (spec 2.3): root it grows from, hub target, fan normal (faces the front, tilted back), leaves
# (yaw deg: 0 = +X, 90 = back; pitch deg; length), seed
FANS = {
    # round 1b: lengths from the leaf origin inside the root, fitted so the tips land on the f34's clump boxes (left
    # X -4.94 .. -1.97, z 1.3 .. 4.95; right X 2.1 .. 4.94, z 1.5 .. 4.6)
    # round 1c: the hubs moved out to the legs' outer back flanks (the left one low on L's buttress, the right one on
    # R's back-left) so each leaf's blade shows beside the leg, as drawn, instead of only its tip over the leg's edge
    # round 2: each fan grows from a fixed origin just inside its root's back-outer flank (`origin`, checked against
    # the root's surface in FAN_INFO): three big kite blades about 45 deg apart as drawn plus a fourth half-hidden
    # behind them, spread like a hand of cards with the lower blades in front. A leaf's optional 4th value moves its
    # base along the root (the right fan's upright blade grows from behind R's shoulder, as drawn). Tips fitted to
    # the sheet's f34 (X, z; left (-4.9, 1.75), (-4.25, 3.7), (-2.8, 4.9); right (4.94, 1.9), (4.3, 3.45),
    # (3.1, 4.5)); the left blades lean 5-25 deg back (yaw < 180) so they also spread across the r34 view
    "left": dict(root="L", origin=(-2.2, -0.55, 2.3), normal=(0.0, -0.9, 0.42), w=0.56,
                 leaves=((175, -12, 2.95), (165, 34, 2.75), (130, 58, 2.3), (155, 82, 2.8)), seed=29401),
    "right": dict(root="R", origin=(3.5, -0.1, 2.5), normal=(0.0, -0.9, 0.42), w=0.56,
                  leaves=((0, -14, 1.5), (20, 42, 1.75), (45, 60, 1.8), (10, 70, 1.95, (-1.0, -0.37, 0.7))),
                  seed=29402),
}
FAN_SINK = 0.3        # the leaves start this far inside the root's surface (toward its centre line)
FAN_STAGGER = 0.25    # neighbouring leaves stacked this far apart along the fan normal (cards in a hand; round 2
#                       0.12 -> 0.25 so the blades separate in depth)
FAN_INFO = {}


def _fan_origin(k):
    F = FANS[k]
    path = ROOT_PATHS.get(F["root"]) or _root_path(F["root"])
    if "origin" in F:
        o = Vector(F["origin"])
        s, c = path.nearest(o)
        r = path.diam(s) / 2
        FAN_INFO[k] = {"origin": [round(x, 2) for x in o], "root_r": round(r, 2),
                       "sunk": round(r - (o - c).length, 2)}
        return o, r - (o - c).length
    H = Vector(F["hub"])
    s, c = path.nearest(H)
    r = path.diam(s) / 2
    d = H - c
    d = d - path.tan(s) * d.dot(path.tan(s))
    o = c + d.normalized() * max(0.0, r - FAN_SINK)
    FAN_INFO[k] = {"origin": [round(x, 2) for x in o], "root_r": round(r, 2), "hub_off": round((H - c).length, 2)}
    return o, r - (o - c).length


def fan(a, k):
    F = FANS[k]
    o, buried = _fan_origin(k)
    rng = random.Random(F["seed"])
    N = Vector(F["normal"]).normalized()
    vs = []
    n = len(F["leaves"])
    for i, lf in enumerate(F["leaves"]):
        yaw, pitch, L = lf[:3]
        D = _dir(yaw + rng.uniform(-3, 3), pitch + rng.uniform(-3, 3))
        # the lower blades in front (toward N), the upright ones behind, as drawn
        base = o + N * ((n - 1) / 2 - i) * FAN_STAGGER + (Vector(lf[3]) if len(lf) > 3 else Vector())
        vs += _leaf(a, base, D, N, L * (1 + rng.uniform(-0.03, 0.03)), F["seed"] * 10 + i,
                    roll=rng.uniform(-6, 6), w=F.get("w", LEAF_W))
    _mottle(a, _faces(vs), LEAF_MOTTLE["amp"], LEAF_MOTTLE["scale"], LEAF_MOTTLE["seed"] + F["seed"])
    return vs


# the part: the exploded drawing's 7-leaf clump (both sides), hero leaf size, on a small hidden hub
# (yaw, pitch, length): round 1b respaced at least 45 deg apart round the hub (two leaves 15 deg apart crossed each
# other into self-intersecting slivers)
# round 2: every pitch 51-85 deg (was 22-82: a low agave rosette, H : span 0.68), so the clump is the exploded
# drawing's upright V fan (H : span >= 0.9)
CLUMP = dict(leaves=((200, 51, 2.2), (250, 63, 2.3), (148, 56, 2.35), (95, 85, 2.5), (35, 58, 2.35),
                     (-20, 51, 2.2), (-82, 61, 2.25)), seed=29645, hub=(0.3, 0.32))


CLUMP_SEED = [0]


def leaf_clump_raw(a):
    rng = random.Random(CLUMP["seed"] + CLUMP_SEED[0])
    bm = a.bm
    hr, hh = CLUMP["hub"]
    ring0 = [bm.verts.new((math.cos(2 * math.pi * k / 6) * hr, math.sin(2 * math.pi * k / 6) * hr, 0.0))
             for k in range(6)]
    ring1 = [bm.verts.new((math.cos(2 * math.pi * k / 6 + 0.5) * hr * 0.75, math.sin(2 * math.pi * k / 6 + 0.5) *
                           hr * 0.75, hh)) for k in range(6)]
    apex = bm.verts.new((0, 0, hh + 0.12))
    bot = bm.verts.new((0, 0, -0.01))
    fs = _strip(bm, ring0, ring1) + _fanf(bm, ring1, apex) + _fanf(bm, ring0, bot, flip=True)
    hub = ring0 + ring1 + [apex, bot]
    a._finish(hub, LEAF_BASE)
    _tri(bm, fs)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(hub))
    vs = list(hub)
    for i, (yaw, pitch, L) in enumerate(CLUMP["leaves"]):
        D = _dir(yaw + rng.uniform(-4, 4), pitch + rng.uniform(-3, 3))
        # the leaf's broad side turned up (its face normal in the vertical plane through the leaf)
        Nf = (Vector((0, 0, 1)) - D * D.z).normalized() if abs(D.z) < 0.95 else Vector((0, -1, 0))
        base = Vector((math.cos(math.radians(yaw)) * hr * 0.6, math.sin(math.radians(yaw)) * hr * 0.6,
                       0.08 + 0.02 * i))
        vs += _leaf(a, base, D, Nf, L * (1 + rng.uniform(-0.05, 0.05)), CLUMP["seed"] * 10 + i,
                    roll=rng.uniform(-6, 6))
    _mottle(a, _faces(vs), LEAF_MOTTLE["amp"], LEAF_MOTTLE["scale"], LEAF_MOTTLE["seed"] + CLUMP["seed"])
    return vs


# ---- fusing (temporary objects in the build frame) ---------------------------------------------------------------------
def _tmp(name, fn):
    """fn built into a temporary object whose mesh stays in the build frame (OFF = 0)."""
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
    bpy.context.view_layer.update()      # split_loose copies matrix_world: it must not be stale
    o[OFF] = [0.0, 0.0, 0.0]
    return o


def _union_fine(o, merge=0.0):
    """M.union_loose without its 0.01 post-union merge (which welds converging intersection curves at leaf necks
    into bowties); the exact union's output is clean."""
    act = bpy.context.view_layer.objects.active
    if act and act.mode != "OBJECT":
        with bpy.context.temp_override(active_object=act, object=act):
            bpy.ops.object.mode_set(mode="OBJECT")
    others = M.split_loose(o)
    for p in others:
        m = o.modifiers.new("U", "BOOLEAN")
        m.operation, m.solver, m.object = "UNION", "EXACT", p
        m.material_mode = "TRANSFER"
        with M._override(o):
            bpy.ops.object.modifier_apply(modifier=m.name)
        me = p.data
        bpy.data.objects.remove(p, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    if merge:
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
    """The M020 / M023 polish: quads split, the floor cap re-fanned (no needles), slivers forced open, origin back at
    the bottom centre, UVs redone."""
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
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = m012._force_slivers(o, lim=POLISH_LIM)
    if m012._thin(o, POLISH_LIM)["under"]:
        forced += m012._force_slivers(o, lim=POLISH_LIM, max_len=0.5)
    if m012._thin(o, POLISH_LIM)["under"]:
        forced += m012._force_slivers(o, lim=POLISH_LIM, max_len=0.9)
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


def _fused_ok(o):
    a = M.audit(o)
    return (a["shells"] == 1 and not a["nonmanifold_edges"] and not a.get("nonmanifold_verts", 0)
            and not a["boundary_edges"] and a["normals"] == "outward"
            and not m016._self_hits(o)[0] and not m012._thin(o, POLISH_LIM)["under"])


def _fuse(name, fn, ground=False, clean=True):
    o = _tmp(name, fn)
    log = {"shells_merged": _union_fine(o)}
    if ground:
        m016._floor_cut(o, 0.0)
    if clean:
        log["clean"] = {k: v for k, v in m016._clean_mesh(o, (0.0,) if ground else ()).items()
                        if k in ("pockets", "forced", "ears")}
    log["bowties"] = M.fix_bowties(o)
    a = M.audit(o)
    log["audit"] = {k: a[k] for k in ("tris", "shells", "nonmanifold_edges", "nonmanifold_verts", "boundary_edges")}
    log["self_hits"] = m016._self_hits(o)[0]
    return o, log


FUSE_LOG = {}


def prepare():
    """The fused temporary pieces in the build frame: base (with contact darkening), bare base (the part), root L
    (+ spur), root R, the leaf clump part."""
    palette()
    FUSE_LOG.clear()
    ROOT_INFO.clear()
    BOULDER_INFO.clear()
    t0 = time.time()
    _, FUSE_LOG["base"] = _fuse(PFX + "base", base_raw, ground=True)
    _, FUSE_LOG["base_bare"] = _fuse(PFX + "base_bare", lambda a: base_raw(a, contact=False), ground=True)
    _, FUSE_LOG["rootL"] = _fuse(PFX + "rootL", root_left_raw, ground=True)
    _, FUSE_LOG["rootR"] = _fuse(PFX + "rootR", root_right_raw, ground=True)
    # the clump guard: two leaves grazing near the hub can leave a self-intersecting sliver pair; then the next seed
    for attempt in range(8):
        CLUMP_SEED[0] = 97 * attempt
        _, FUSE_LOG["clump"] = _fuse(PFX + "clump", leaf_clump_raw, ground=True)
        lg = FUSE_LOG["clump"]
        if not (lg["self_hits"] or lg["audit"]["nonmanifold_edges"] or lg["audit"]["nonmanifold_verts"]
                or lg["audit"]["boundary_edges"]):
            break
    FUSE_LOG["clump"]["seed_off"] = CLUMP_SEED[0]
    FUSE_LOG["secs"] = round(time.time() - t0, 1)
    return dict(FUSE_LOG)


# ---- hero and parts ---------------------------------------------------------------------------------------------------
def _paste_obj(a, o, m=None):
    mat = (m if m is not None else Matrix.Identity(4)) @ Matrix.Translation(Vector(o[OFF]))
    return m011._paste(a, o, mat)


def hero(a):
    _paste_obj(a, bpy.data.objects[PFX + "base"])
    boulders(a)
    _paste_obj(a, bpy.data.objects[PFX + "rootL"])
    _paste_obj(a, bpy.data.objects[PFX + "rootR"])
    _sapstone(a)
    fan(a, "left")
    fan(a, "right")


def base_part(a):
    _paste_obj(a, bpy.data.objects[PFX + "base_bare"])


def rock_part(a):
    _boulder(a, "front_left", at_origin=True)


def sapstone_part(a):
    _sapstone(a, at_origin=True)


def root_left_part(a):
    _paste_obj(a, bpy.data.objects[PFX + "rootL"])


def root_right_part(a):
    _paste_obj(a, bpy.data.objects[PFX + "rootR"])


def leaf_clump_part(a):
    _paste_obj(a, bpy.data.objects[PFX + "clump"])


NOTES = {
    HERO: "ancient root resource node: a flat faceted round stone slab ringed by chunky grey-mauve boulders, a big "
          "faceted soft-green sapstone egg on its floor, two thick gnarled warm-orange root halves arching over it "
          "(a buttress foot with a spur, a club end resting on the other root), two upright lime leaf fans; one "
          "closed mesh, flat base. No VFX",
    "SapstoneRootArchBase": "Base (reusable): a low round faceted stone slab, flat floor inside a low lumpy rim, flat "
                            "underside",
    "SapstoneRootArchRock": "Rocks (Side) (reusable): a chunky faceted grey-mauve boulder, lighter greyer top",
    "SapstoneRootArchSapstone": "Green Sapstone (harvestable insert): a faceted soft-green egg, flat seat",
    "SapstoneRootArchRootLeft": "Root Half (Left): a thick gnarled faceted root with a buttress foot and spur and a "
                                "blunt club end",
    "SapstoneRootArchRootRight": "Root Half (Right): a long S-curved gnarled faceted root, domed top end, blunt foot",
    "SapstoneRootArchLeafClump": "Leaf Clump (reusable): seven thick faceted lime kite leaves in an upright clump",
}
PARTS = (("SapstoneRootArchBase", base_part), ("SapstoneRootArchRock", rock_part),
         ("SapstoneRootArchSapstone", sapstone_part), ("SapstoneRootArchRootLeft", root_left_part),
         ("SapstoneRootArchRootRight", root_right_part), ("SapstoneRootArchLeafClump", leaf_clump_part))
GROUND_PARTS = {"SapstoneRootArchBase", "SapstoneRootArchRootLeft", "SapstoneRootArchRootRight"}
TARGET_SIZE = ((9.9, 0.4), (7.6, 0.4), (6.2, 0.25))


def _ground_faces(o):
    """Faces on the ground plane (the floor cut's caps): the plain base key (a darker underside would be colour by
    facing); under a root foot standing on its own (the root parts) the root's dark key, under the clump its hub key."""
    p = m011._Paint(o, off=o[OFF])
    n = 0
    for f in p.bm.faces:
        if all(abs(v.co.z) < 1e-3 for v in f.verts):
            nb = [p.key(g) for e in f.edges for g in e.link_faces if g is not f]
            if nb and all(k.startswith("m029_root") for k in nb):
                key = ROOT_DARK
            elif nb and all(k.startswith("m029_leaf") for k in nb):
                key = LEAF_BASE
            else:
                key = BASE
            f.material_index = p._mi(key)
            n += 1
    p.done()
    return n


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
    t0 = time.time()
    if role == "hero":
        lg["shells_merged"] = _union_fine(o)
        m016._floor_cut(o, -off.z)
        o[OFF] = [off.x, off.y, 0.0]
        lg["clean"] = {k: v for k, v in m016._clean_mesh(o, (0.0,)).items() if k in ("pockets", "forced", "ears")}
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    if role == "hero" or name in GROUND_PARTS:
        lg["ground_faces"] = _ground_faces(o)
    lg["bowties"] = M.fix_bowties(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


def build(render=True, parts=True, keep_tmp=False):
    t_start = time.time()
    M.coll(NUM, TITLE)
    log = {"prepare": prepare()}
    objs = {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn, "part", 1000)
    h, log["hero"] = _make(HERO, hero, "hero", 4000)
    log["fans"] = dict(FAN_INFO)
    log["boulders"] = dict(BOULDER_INFO)
    log["roots"] = {k: {kk: v[kk] for kk in ("L", "rings")} for k, v in ROOT_INFO.items()}
    if not keep_tmp:
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
    log["build_secs"] = round(time.time() - t_start, 1)
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts")} for au in audits],
           "thin": thin, "self_hits": self_hits, "log": log, "problems": problems,
           "uv": {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped",
                                                                            "min_gap", "border", "density",
                                                                            "stretch_conformal_p95")}
                  for o in order}}
    if render:
        t1 = time.time()
        out["views"] = render_views(order)
        log["render_secs"] = round(time.time() - t1, 1)
    log["total_secs"] = round(time.time() - t_start, 1)
    return out


# ---- stages 5 + 6 (spec section 7) -------------------------------------------------------------------------------------
# Stage 5: nothing. The sheet shows an ordinary sunlit root arch over a matte green stone: no emissive key, no light
# (decision 8). Stage 6: nothing. No glow, sparkle, dust or particles on the sheet: no socket (decision 8).


# ---- renders ----------------------------------------------------------------------------------------------------------
SHEET_VIEWS = {"f34_sheet": (0, 13), "r34_sheet": (-40, 15), "side_sheet": (90, 10), "rear_sheet": (180, 10),
               "top_sheet": (0, 50)}
SHEET_LENS = 3.0        # the sheet's cells are near-orthographic: the *_sheet shots use a 3x longer lens
JUNC_CU = (30, 18, (2.4, -0.6, 4.0), 1.1)       # Close-Up: Root Junction (L's club end on R, the right fan)
BASE_CU = (-15, 12, (0.4, -2.6, 0.45), 1.5)      # Close-Up: Base & Joining
PARTS_SHOT = (-20, 15)


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


# exploded layout (build frame offsets from each part's place in the hero)
EXPL = {"SapstoneRootArchBase": (0, 0, 0), "SapstoneRootArchSapstone": (0.0, 0.0, 3.2),
        "SapstoneRootArchRootLeft": (-2.2, 0.0, 5.2), "SapstoneRootArchRootRight": (2.6, 0.6, 5.6)}
EXPL_EXTRA = (("SapstoneRootArchLeafClump", (-3.6, -1.0, 2.2), 0.8),
              ("SapstoneRootArchLeafClump", (3.4, -0.6, 2.4), 0.75),
              ("SapstoneRootArchRock", (-4.3, -1.8, 1.0), 0.6), ("SapstoneRootArchRock", (-2.9, -2.4, 1.8), 0.5),
              ("SapstoneRootArchRock", (3.6, -2.2, 1.2), 0.55), ("SapstoneRootArchRock", (4.4, -1.4, 1.5), 0.45))


def _exploded(objs):
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []
    x0 = objs[0].location.x + 40
    base = Matrix.Translation((x0, objs[0].location.y, 0))
    for name, dv in EXPL.items():
        if name not in by:
            continue
        c = bpy.data.objects.new(f"{PFX}expl_{name}", by[name].data)
        coll.objects.link(c)
        c.matrix_world = base @ Matrix.Translation(Vector(dv)) @ Matrix.Translation(Vector(by[name][OFF]))
        shown.append(c)
    for i, (name, loc, sc) in enumerate(EXPL_EXTRA):
        if name not in by:
            continue
        c = bpy.data.objects.new(f"{PFX}expl_x{i}", by[name].data)
        coll.objects.link(c)
        c.matrix_world = (base @ Matrix.Translation(Vector(loc)) @ Matrix.Rotation(math.radians(57 * i), 4, "Z") @
                          Matrix.Diagonal((sc, sc, sc, 1)))
        shown.append(c)
    bpy.context.view_layer.update()
    return shown


def render_close(objs, path, az, el, centre, radius):
    kit = K.NS["KIT"]
    fb = kit["frame_box"]
    c = Vector(centre)
    box = [c + Vector((dx, dy, dz)) * radius for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
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
            extra["exploded"] = (shown, -12, 16)
        for o in objs[1:]:
            extra["part_" + o.name.replace(HERO, "").lower()] = ([o], *PARTS_SHOT)
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
            az, el, c, r = JUNC_CU
            out["junc_cu"] = render_close([h], f"{d}/junc_cu.png", az, el, off @ Vector(c), r)
            az, el, c, r = BASE_CU
            out["base_cu"] = render_close([h], f"{d}/base_cu.png", az, el, off @ Vector(c), r)
        return out
    finally:
        for o in shown:
            bpy.data.objects.remove(o, do_unlink=True)
        M.display(NUM, objs, TITLE)


# ---- measuring --------------------------------------------------------------------------------------------------------
# bark relief (spec 4 step 5.6): stations on L's leg at z 1.5 / 2.5 / 3.5 and R's at z 2.0 / 3.0
BARK_STATIONS = (("L", 1.5), ("L", 2.5), ("L", 3.5), ("R", 2.0), ("R", 3.0))


def bark_relief(o=None, step=2.0):
    """The bark radius round the centre line by azimuth (2 deg steps) at the spec's stations, measured on the hero
    (or `o`) by rays cast from the centre line in the plane square to it. Per station: creases (local minima at least
    0.06 below both neighbouring maxima within 60 deg), min / median radius, spread (max - min) / 2, groove depths."""
    o = o or bpy.data.objects[HERO]
    bm = bmesh.new()
    bm.from_mesh(o.data)
    off = Vector(o[OFF])
    bmesh.ops.translate(bm, verts=bm.verts, vec=off)
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    out = {}
    for name, z in BARK_STATIONS:
        path = ROOT_PATHS.get(name) or _root_path(name)
        # the leg's station at height z (L: its rising leg; R: its descending leg)
        cand = [s for s in [i * 0.02 for i in range(int(path.L / 0.02))] if abs(path.at(s).z - z) < 0.03]
        if not cand:
            continue
        s = min(cand) if name == "L" else max(cand)
        c, t = path.at(s), path.tan(s)
        n = Vector((0, 0, 1)) - t * t.z
        n = n.normalized() if n.length > 1e-3 else _perp(t)
        b = t.cross(n)
        rs = []
        for k in range(int(360 / step)):
            th = math.radians(k * step)
            d = n * math.cos(th) + b * math.sin(th)
            # from outside inward: the outer surface of this root here
            hit = tree.ray_cast(c + d * 3.0, -d, 3.0)
            rr = 3.0 - hit[3] if hit[0] is not None else None
            # only this root's own surface: rays that first meet a leaf, the spur or the other root are dropped
            rnom = path.diam(s) / 2
            rs.append(rr if rr is not None and 0.55 * rnom < rr < 1.45 * rnom else None)
        vals = [r for r in rs if r is not None]
        med = sorted(vals)[len(vals) // 2]
        m = len(rs)
        win = int(60 / step)
        creases = []
        for k in range(m):
            r = rs[k]
            if r is None:
                continue
            nb = [rs[(k + j) % m] for j in range(-win, win + 1) if j and rs[(k + j) % m] is not None]
            if r <= min(nb):
                left = max([rs[(k - j) % m] for j in range(1, win + 1) if rs[(k - j) % m] is not None] or [r])
                right = max([rs[(k + j) % m] for j in range(1, win + 1) if rs[(k + j) % m] is not None] or [r])
                depth = min(left, right) - r
                if depth >= 0.06:
                    creases.append((k * step, round(depth, 3)))
        out[f"{name}@z{z}"] = {"creases": len(creases), "depths": [d for _, d in creases],
                               "angles": [a_ for a_, _ in creases],
                               "min_over_median": round(min(vals) / med, 3), "spread": round((max(vals) - min(vals)) / 2, 3),
                               "median_r": round(med, 3), "s": round(s, 2)}
    # knots: the mean radius along each limb (every 0.25 stud), local maxima at least 12 % over the minima beside them
    for name in ("L", "R"):
        path = ROOT_PATHS.get(name) or _root_path(name)
        prof = []
        ss = [i * 0.25 for i in range(int(path.L / 0.25) + 1)]
        for s in ss:
            c, t = path.at(s), path.tan(s)
            n = _perp(t)
            b = t.cross(n)
            r_ = []
            for k in range(12):
                th = 2 * math.pi * k / 12
                d = n * math.cos(th) + b * math.sin(th)
                hit = tree.ray_cast(c + d * 3.0, -d, 3.0)
                if hit[0] is not None:
                    r_.append(3.0 - hit[3])
            prof.append(sum(r_) / len(r_) / (path.diam(s) / 2) if r_ else None)
        knots = []
        for i in range(2, len(prof) - 2):
            p = prof[i]
            if p is None or c is None:
                continue
            lo = [x for x in prof[max(0, i - 6):i] if x is not None]
            hi = [x for x in prof[i + 1:i + 7] if x is not None]
            if lo and hi and p >= max(prof[i - 1] or 0, prof[i + 1] or 0) and p >= 1.12 * min(lo) and p >= 1.12 * min(hi):
                knots.append((round(ss[i] / path.L, 2), round(p / max(min(lo), min(hi)), 2)))
        out[f"{name}_knots"] = knots
    return out


# the study's masks (m_cls.py), on the sheet and on our renders
REF_VIEWS = {"f34": (15, 120, 551, 490), "r34": (554, 120, 1008, 490), "front": (15, 525, 287, 741),
             "side": (291, 525, 516, 741), "rear": (519, 525, 761, 741), "top": (764, 525, 1008, 741)}
OUR_VIEWS = {"f34": "f34_sheet", "front": "f34_sheet", "r34": "r34_sheet", "side": "side_sheet",
             "rear": "rear_sheet", "top": "top_sheet"}
SHEET_PAPER = (243, 237, 229)


def _hsv(a):
    r, g, b = a[..., 0] / 255, a[..., 1] / 255, a[..., 2] / 255
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rr = m & (mx == r)
    gg = m & (mx == g) & ~rr
    bb = m & ~rr & ~gg
    h[rr] = ((g - b)[rr] / d[rr]) % 6
    h[gg] = (b - r)[gg] / d[gg] + 2
    h[bb] = (r - g)[bb] / d[bb] + 4
    return h * 60, np.where(mx > 0, d / np.maximum(mx, 1e-6), 0), mx


def _classes(a, paper):
    """0 background (paper + the soft grey ground shadow), 1 leaf, 2 sapstone, 3 root, 4 stone, 6 other."""
    h, s, v = _hsv(a)
    bgd = np.abs(a - np.array(paper, float)).max(-1)
    out = np.full(h.shape, 6, np.uint8)
    bg = (bgd < 16) | ((s < 0.10) & (v >= 0.78))
    # round 2: the studio's warm-grey ground shadow (hue 30-70, sat < 0.11, value > 0.62) is background too, as the
    # sheet's soft shadow already is; before, it counted as stone and stretched our bbox to the right of the f34
    bg |= (s < 0.11) & (v > 0.62) & (h >= 30) & (h <= 70)
    out[bg] = 0
    fg = ~bg
    green = fg & (h >= 48) & (h <= 160) & (s >= 0.22) & (a[..., 1] > 45)
    leaf = green & ((h < 80) | (s >= 0.70))
    sap = green & ~leaf
    root = fg & ~green & (h >= 12) & (h <= 36) & (s >= 0.40) & (v >= 0.25)
    stone = fg & ~green & ~root & (((h <= 45) | (h >= 300)) | (s < 0.12)) & (v >= 0.14) & (v < 0.80)
    out[leaf] = 1
    out[sap] = 2
    out[root] = 3
    out[stone] = 4
    return out


def _load(path, box=None):
    px = K.NS["KIT"]["load_px"](path)[::-1, :, :3] * 255.0
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1]
    return np.clip(px, 0, 255)


def _hex(q):
    return "#" + "".join(f"{int(round(x)):02X}" for x in q)


def stats(px, paper=SHEET_PAPER):
    c = _classes(px, paper)
    obj = (c >= 1) & (c != 0)
    cols = np.nonzero(obj.sum(0) >= 2)[0]
    rows = np.nonzero(obj.sum(1) >= 2)[0]
    bx0, bx1, by0, by1 = cols.min(), cols.max(), rows.min(), rows.max()
    W, H = bx1 - bx0, by1 - by0
    sub = c[by0:by1 + 1, bx0:bx1 + 1]
    pxs = px[by0:by1 + 1, bx0:bx1 + 1]
    n = max(1, ((sub >= 1) & (sub <= 4)).sum())
    out = {"wh": round(W / H, 3)}
    for k, lab in ((1, "L"), (2, "S"), (3, "R"), (4, "K")):
        out[lab] = round((sub == k).sum() / n, 3)
        sel = pxs[sub == k]
        if len(sel) >= 8:
            srt = sel[np.argsort(sel.sum(1))]
            q = max(1, len(srt) // 4)
            out[lab + "med"] = _hex(np.median(sel, axis=0))
            out[lab + "lit"] = _hex(np.median(srt[-q:], axis=0))
            out[lab + "shade"] = _hex(np.median(srt[:q], axis=0))
    objm = obj[by0:by1 + 1, bx0:bx1 + 1]
    top, rtop = [], []
    for i in range(21):
        x = min(W, int(i * W / 20))
        col = objm[:, max(0, x - 1):x + 2].any(1)
        ys = np.nonzero(col)[0]
        top.append(round((H - ys.min()) / H, 2) if len(ys) else None)
        rc = (sub[:, max(0, x - 1):x + 2] == 3).any(1)
        ys = np.nonzero(rc)[0]
        rtop.append(round((H - ys.min()) / H, 2) if len(ys) else 0.0)
    out["top"] = top
    out["root_top"] = rtop
    # sapstone centre (fraction of the bbox)
    ys, xs = np.nonzero(sub == 2)
    if len(xs):
        out["sap_c"] = (round(xs.mean() / W, 3), round(1 - ys.mean() / H, 3))
    # root height bands (bottom -> top fifths of the bbox)
    ys, xs = np.nonzero(sub == 3)
    bands = []
    for i in range(5):
        y0, y1 = H * (1 - (i + 1) / 5), H * (1 - i / 5)
        m = (ys >= y0) & (ys < y1)
        bands.append(_hex(np.median(pxs[ys[m], xs[m]], axis=0)) if m.sum() > 8 else None)
    out["root_bands"] = bands
    return out


def _runs(row, gap=2, min_len=3):
    """(start, end) column runs of True in a boolean row, gaps up to `gap` px bridged."""
    xs = np.nonzero(row)[0]
    out = []
    for x in xs:
        if out and x - out[-1][1] <= gap + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return [(a_, b_) for a_, b_ in out if b_ - a_ + 1 >= min_len]


def arch_stats(px, paper=SHEET_PAPER):
    """The round-1 verifier's arch reads (M029_spec.md "Stage 7"): root runs per height (f = fraction of the bbox
    width, h = fraction of its height from the bottom), the background share inside the arch box (f .35-.80,
    h .20-.85), the right leaf fan's extent (leaf pixels right of f .6) and the widest root run at h .5."""
    c = _classes(px, paper)
    obj = c >= 1
    cols = np.nonzero(obj.sum(0) >= 2)[0]
    rows = np.nonzero(obj.sum(1) >= 2)[0]
    bx0, bx1, by0, by1 = cols.min(), cols.max(), rows.min(), rows.max()
    W, H = bx1 - bx0, by1 - by0
    sub = c[by0:by1 + 1, bx0:bx1 + 1]
    out = {"runs": {}}
    for h in (0.3, 0.4, 0.5, 0.6, 0.7):
        y = int(round(H * (1 - h)))
        band = (sub[max(0, y - 1):y + 2] == 3).any(0)
        out["runs"][h] = [(round(a_ / W, 2), round(b_ / W, 2)) for a_, b_ in _runs(band)]
    ya, yb = int(H * (1 - 0.85)), int(H * (1 - 0.20))
    xa, xb = int(W * 0.35), int(W * 0.80)
    box = sub[ya:yb, xa:xb]
    out["arch_bg"] = round(float((box == 0).mean()) * 100, 1)
    # the right fan: the widest contiguous run of columns right of f .6 holding at least 3 leaf pixels
    lc = (sub == 1).sum(0) >= 3
    lc[:int(0.6 * W)] = False
    fr = _runs(lc, gap=3, min_len=2)
    if fr:
        a_, b_ = max(fr, key=lambda r: r[1] - r[0])
        out["rfan"] = (round(a_ / W, 2), round(b_ / W, 2), int(b_ - a_))
    y = int(round(H * 0.5))
    rr = _runs((sub[y - 1:y + 2] == 3).any(0))
    out["widest_root_h5"] = round(max((b_ - a_ for a_, b_ in rr), default=0) / W, 3)
    out["W_px"] = int(W)
    return out


def arch_measure(views=("f34", "r34", "rear")):
    """arch_stats on the sheet and on our *_sheet renders."""
    ref = M.ref(NUM)
    out = {}
    for vname in views:
        a = arch_stats(_load(ref, REF_VIEWS[vname]))
        ours = _load(f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[vname]}.png")
        corner = tuple(int(x) for x in np.median(ours[:6, :6].reshape(-1, 3), axis=0))
        out[vname] = {"sheet": a, "ours": arch_stats(ours, paper=corner)}
    return out


def measure(views=("f34", "r34", "side", "rear", "top")):
    """Sheet against our renders, per view (the study's masks on both; our studio floor colour counts as paper)."""
    ref = M.ref(NUM)
    out = {}
    for vname in views:
        a = stats(_load(ref, REF_VIEWS[vname]))
        ours = _load(f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[vname]}.png")
        corner = tuple(int(x) for x in np.median(ours[:6, :6].reshape(-1, 3), axis=0))
        b = stats(ours, paper=corner)
        err = [abs(x - y) for x, y in zip(a["top"], b["top"]) if x is not None and y is not None]
        out[vname] = {"sheet": a, "ours": b, "top_err_mean_max": (round(sum(err) / len(err), 3), round(max(err), 2))}
    return out
