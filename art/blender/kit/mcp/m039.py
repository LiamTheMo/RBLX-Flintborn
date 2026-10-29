"""039 Rock Spire (references/039.png): a tall angular warm grey-pink obelisk (S) at the back centre-right, a
flat-topped pillar (P) leaning on its left flank, a shorter flat-topped side rock (Rr) on its right flank, a big
faceted foot rock (F) in front with a nose vertex, a ring of medium (BL, FL, FR) and small (s1-s3) rocks round the foot,
back dressing (a medium dome, a back-right rock, a back-left small rock), and lime star rosettes (6-7 broad oval
leaves round a round lime bud) in every crevice, on the shoulders and up the spire's right flank.

    import importlib, kit_models, m039; importlib.reload(kit_models); importlib.reload(m039); m039.build()

Build frame: studs, front -Y, +X right, ground z 0; every object ends with its origin at its bbox bottom centre.
W01 owns RockSpire*, so the names are StoneSpire* (spec 8):
- StoneSpireMain (spire_part): the obelisk, bare.
- StoneSpireSideRock (side_rock_part): Rr with one rosette on its top.
- StoneSpireFootRock (foot_rock_part): F with its two top sprigs.
- StoneSpireSmallRock (small_rock_part): s2's mesh, bare.
- StoneSpireFoliage (foliage_part): one 7-leaf rosette with its bud.

The hero (StoneSpire, decision 6) is one object of separate closed shells: each rock, each leaf and each bud. No
booleans: the rocks interlock by overlapping (at most 0.6). Every leaf and bud is seated on the ground, a rock or
another leaf (contact <= 0.03, chained to the ground or a rock; STAGES "No floating dressing"); a settle pass drops
any group that still hangs. Colour (stage 4) is painted by position per flat facet. Stages 5-6: nothing (decision 8).
See M039_spec.md.
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
import m012
import m033

NUM, TITLE, SHEET = 39, "Rock Spire", "M039"
OFF = "m039_offset"
PFX = "_m039_"
HERO = "StoneSpire"
MAIN_P, SIDE_P, FOOT_P = "StoneSpireMain", "StoneSpireSideRock", "StoneSpireFootRock"
SMALL_P, FOL_P = "StoneSpireSmallRock", "StoneSpireFoliage"

ROCK, ROCK_LIGHT, ROCK_DEEP, STAIN = "m039_rock", "m039_rock_light", "m039_rock_deep", "m039_moss_stain"
LEAF, LEAF_LIGHT, LEAF_DEEP, BUD = "m039_leaf", "m039_leaf_light", "m039_leaf_deep", "m039_bud"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low specular). Stage 4 (M039_spec.md "Stage 4") writes the calibrated values here.
PALETTE = {
    ROCK: ("#B6A095", 0.9, False),
    ROCK_LIGHT: ("#CAB4A9", 0.9, False),
    ROCK_DEEP: ("#9F8A7F", 0.9, False),
    STAIN: ("#706D3A", 0.9, False),
    LEAF: ("#718A01", 0.85, True),
    LEAF_LIGHT: ("#ACB306", 0.85, True),
    # fix round 1: greener and more saturated (was #496A01, olive shade halves); #3F6A01 rendered leaf sat 0.922, this 0.943
    LEAF_DEEP: ("#386E03", 0.85, True),
    BUD: ("#96A201", 0.75, True),
}
# calibration targets (spec 5.4: rendered medians of unshadowed regions, the exploded parts and the close-ups)
TARGETS = {ROCK: ((0xC5, 0xA8, 0x96), "all"), ROCK_LIGHT: ((0xD9, 0xBF, 0xAC), "all"),
           ROCK_DEEP: ((0xB3, 0x98, 0x86), "all"), STAIN: ((0x8C, 0x85, 0x48), "all"),
           LEAF: ((0x7E, 0x9C, 0x05), "green"), LEAF_LIGHT: ((0xC8, 0xCF, 0x0A), "vivid"),
           LEAF_DEEP: ((0x4E, 0x74, 0x04), "green"), BUD: ((0xBC, 0xC6, 0x04), "vivid")}
SPEC = {}
ROCK_KEYS = (ROCK, ROCK_LIGHT, ROCK_DEEP)


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    _spec()


def _spec():
    for m in bpy.data.materials:
        if not m.name.startswith("FB_m039_") or not m.node_tree:
            continue
        key = m.name[3:]
        lvl = next((v for p, v in SPEC.items() if key.startswith(p)), None)
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if lvl is not None and bsdf and "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = lvl


def hue_of(hexcol):
    r, g, b = (int(hexcol.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    mx, mn = max(r, g, b), min(r, g, b)
    if mx == mn:
        return 0.0, 0.0
    if mx == r:
        h = (60.0 * (g - b) / (mx - mn)) % 360
    elif mx == g:
        h = 60.0 * (b - r) / (mx - mn) + 120
    else:
        h = 60.0 * (r - g) / (mx - mn) + 240
    return h, (mx - mn) / mx


def warm_ok(hexcol, lo=14.0, hi=26.0):
    """The mauve guard (spec 5.3, 9.1): R > G > B, hue 14-26 deg, R - B >= 30."""
    r, g, b = (int(hexcol.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    if not (r > g > b) or r - b < 30:
        return False
    return lo <= hue_of(hexcol)[0] <= hi


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome. Returns {key: (hex, rendered)}; a
    rock key that fails the mauve guard is flagged REJECTED (and must not be written into PALETTE)."""
    keys = keys or list(TARGETS)
    for k in keys:
        K.fk().material(k)
    try:
        res = K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)
    out = {}
    for k in keys:
        out[k] = list(res[k])
        if k in ROCK_KEYS and not warm_ok(res[k][0]):
            out[k].append("REJECTED: fails the warm-stone guard")
    return out


# ---- small helpers (m033 / m036 / m038) --------------------------------------------------------------------------------
_faces = m033._faces
_place = m033._place


def _q(t, steps=3):
    t = max(0.0, min(1.0, t))
    return round(t * steps) / steps


def _tri(bm, faces):
    bmesh.ops.triangulate(bm, faces=[f for f in faces if f.is_valid and len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")


def _hull_bm(bm, pts):
    """Convex hull of pts into bm as one closed triangulated shell; returns its verts. (m036)"""
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    for v in vs:
        if v.is_valid and not v.link_faces:
            bm.verts.remove(v)
    vs = [v for v in vs if v.is_valid]
    _tri(bm, _faces(vs))
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    return vs


def _regions(faces, ang=2.0):
    """Flat facets: neighbouring triangles whose normals are within ang degrees, merged. (m036)"""
    fset = set(faces)
    seen = {}
    regs = []
    lim = math.radians(ang)
    for f in faces:
        if f in seen:
            continue
        r = len(regs)
        seen[f] = r
        stack, reg = [f], []
        while stack:
            g = stack.pop()
            reg.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h in fset and h not in seen and h.normal.angle(f.normal, 1.0) <= lim:
                        seen[h] = r
                        stack.append(h)
        regs.append(reg)
    return regs


def _centroid(reg):
    a = sum(f.calc_area() for f in reg)
    return sum((f.calc_center_median() * f.calc_area() for f in reg), Vector()) / max(a, 1e-9)


def _tint_regions(a, regs, amp, scale, seed, tint=1.0):
    """Broad Tint patches read at each flat facet's centroid (one tone per facet, never per-triangle confetti)."""
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for reg in regs:
        k = (1.0 + amp * 1.6 * noise.noise(_centroid(reg) * scale + off)) * tint
        for f in reg:
            for l in f.loops:
                t = l[a.tint_layer][0] * k
                l[a.tint_layer] = (t, t, t, 1.0)


def _mottle(a, faces, amp, scale, seed, tint=1.0):
    m033._mottle(a, faces, amp, scale, seed, tint)


def _planes(pts):
    """Outward face planes (n, d) of the convex hull of pts, and the hull verts. (m036)"""
    bm = bmesh.new()
    vs = _hull_bm(bm, pts)
    out = [(f.normal.copy(), f.normal.dot(f.calc_center_median())) for f in _faces(vs)]
    hv = [v.co.copy() for v in vs]
    bm.free()
    return out, hv


def _pen(pa, pb):
    """Penetration of two convex hulls (max depth of either's verts inside the other). (m036)"""
    best = 0.0
    for (planes, _), (_, verts) in ((pa, pb), (pb, pa)):
        for v in verts:
            d = min(dd - n.dot(v) for n, dd in planes)
            best = max(best, d)
    return best


# ---- the spire (spec 1.4 Rock Spire, decision 4): an explicit 7-sided obelisk ------------------------------------------
# Rings (height fraction, scale of the shared base polygon). Each ring is a scaled, shifted copy of one polygon, so
# every band quad is a planar trapezoid: long flat faces running up the shaft. The top ring is the cap base; a
# 4-face pyramid cap (three cap-base verts are dropped onto the planes of their neighbours) to an apex left of centre.
# One front vertex at the mid ring is pushed in (DIAMOND) to split the front into a diamond facet and slivers.
SPIRE = dict(W=4.4, D=3.8, H=11.0, n=7, seed=39101,
             rings=((0.0, 0.90), (0.12, 1.0), (0.60, 0.76), (0.89, 0.46)),
             lean=(-0.40, -0.20),          # apex offset from the base centre (studs)
             diamond=(2, 0, 0.13),         # (ring, vertex, inward fraction)
             kink=(1, 4, 0.06),            # one back vertex of the foot ring tucked in (breaks the back symmetry)
             cap_major=(0, 2, 4, 6), apex_dx=-0.10)
SPIRE_AT = (1.25, 1.8)


def _spire(a, centre=SPIRE_AT):
    sp = SPIRE
    rng = random.Random(sp["seed"])
    bm = a.bm
    n = sp["n"]
    W, D, H = sp["W"], sp["D"], sp["H"]
    angs, rads = [], []
    for k in range(n):
        angs.append(math.radians(-90.0 + 360.0 * k / n + rng.uniform(-6, 6)))
        rads.append(1.0 + rng.uniform(-0.06, 0.06))
    poly = [Vector((math.cos(t) * r, math.sin(t) * r)) for t, r in zip(angs, rads)]
    xs, ys = [p.x for p in poly], [p.y for p in poly]
    sx, sy = W / (max(xs) - min(xs)), D / (max(ys) - min(ys))
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    poly = [Vector(((p.x - cx) * sx, (p.y - cy) * sy)) for p in poly]
    lx, ly = sp["lean"]
    rings = []
    for ri, (h, s) in enumerate(sp["rings"]):
        ring = []
        for k, p in enumerate(poly):
            q = p * s
            if (ri, k) == sp["diamond"][:2]:
                q = q * (1.0 - sp["diamond"][2])
            if (ri, k) == sp["kink"][:2]:
                q = q * (1.0 - sp["kink"][2])
            ring.append(bm.verts.new((q.x + lx * h, q.y + ly * h, h * H)))
        rings.append(ring)
    apex = bm.verts.new((lx + sp["apex_dx"], ly, H))
    # the cap: the minor cap-base verts are lowered onto the plane through the apex and their major neighbours
    top = rings[-1]
    maj = sp["cap_major"]
    for i, m0 in enumerate(maj):
        m1 = maj[(i + 1) % len(maj)]
        k = (m0 + 1) % n
        while k != m1:
            a0, a1 = top[m0].co, top[m1].co
            nrm = (a0 - apex.co).cross(a1 - apex.co)
            if abs(nrm.z) > 1e-6:
                v = top[k].co
                # z on the plane at v's xy
                v.z = apex.co.z - (nrm.x * (v.x - apex.co.x) + nrm.y * (v.y - apex.co.y)) / nrm.z
            k = (k + 1) % n
    faces = []
    dia_r, dia_k = sp["diamond"][:2]
    for ri in range(len(rings) - 1):
        r0, r1 = rings[ri], rings[ri + 1]
        for k in range(n):
            j = (k + 1) % n
            a0, b0, b1, a1 = r0[k], r0[j], r1[j], r1[k]
            # the split diagonal: through the pushed-in vertex if the quad has it (the diamond), else alternate so
            # neighbouring bands don't line up
            quad = (a0, b0, b1, a1)
            piv = None
            for v, tag in ((a0, (ri, k)), (b0, (ri, j)), (b1, (ri + 1, j)), (a1, (ri + 1, k))):
                if tag == (dia_r, dia_k):
                    piv = v
            if piv is None:
                piv = a0 if (k + ri) % 2 == 0 else b0
            i = quad.index(piv)
            q = quad[i:] + quad[:i]
            faces.append(bm.faces.new((q[0], q[1], q[2])))
            faces.append(bm.faces.new((q[0], q[2], q[3])))
    for k in range(n):
        faces.append(bm.faces.new((top[k], top[(k + 1) % n], apex)))
    floor = bm.faces.new(list(reversed(rings[0])))
    faces.append(floor)
    _tri(bm, [floor])
    vs = [v for r in rings for v in r] + [apex]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    _place(bm, vs, Matrix.Translation((centre[0], centre[1], 0.0)))
    a._finish(vs, ROCK, tint=1.0)
    return vs


# ---- side rocks: the pillar P and Rr (spec 1.4 Side Rock) ---------------------------------------------------------------
# Rings of one shared polygon (planar side faces), a flat top ring, the upper rings leaned. jit: per-vertex in-plane
# jitter of the upper rings (breaks the planarity a little: the Side Rock's medium-sized faces).
SIDE_RINGS = ((0.0, 0.90), (0.12, 1.0), (0.55, 0.82), (0.92, 0.60), (1.0, 0.55))
SIDES = {
    #       size (W, D, H),   lean (dx, dy at the top), top slope (deg, falls to -Y), n, jit, yaw, seed
    "P": dict(size=(3.9, 3.0, 7.7), lean=(0.30, 0.0), slope=7.0, n=6, jit=0.03, yaw=8.0, seed=39111),
    "Rr": dict(size=(2.8, 2.6, 5.1), lean=(-0.90, 0.0), slope=4.0, n=6, jit=0.08, yaw=-12.0, seed=39112),
}


def _side_rock(a, name, centre):
    sp = SIDES[name]
    rng = random.Random(sp["seed"])
    bm = a.bm
    W, D, H = sp["size"]
    n = sp["n"]
    poly = []
    for k in range(n):
        t = math.radians(-90.0 + 360.0 * k / n + rng.uniform(-10, 10))
        r = 1.0 + rng.uniform(-0.07, 0.07)
        poly.append(Vector((math.cos(t) * r, math.sin(t) * r)))
    yaw = Matrix.Rotation(math.radians(sp["yaw"]), 2)
    poly = [yaw @ p for p in poly]
    xs, ys = [p.x for p in poly], [p.y for p in poly]
    sx, sy = W / (max(xs) - min(xs)), D / (max(ys) - min(ys))
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    poly = [Vector(((p.x - cx) * sx, (p.y - cy) * sy)) for p in poly]
    tz = math.tan(math.radians(sp["slope"]))
    rings = []
    for ri, (h, s) in enumerate(SIDE_RINGS):
        ring = []
        for k, p in enumerate(poly):
            q = p * s
            if 0 < ri < len(SIDE_RINGS) - 1:
                q = q + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1))) * sp["jit"] * W
            z = h * H
            if h > 0.5:
                z += q.y * tz * h
            ring.append(bm.verts.new((q.x + sp["lean"][0] * h, q.y + sp["lean"][1] * h, z)))
        rings.append(ring)
    faces = []
    for ri in range(len(rings) - 1):
        r0, r1 = rings[ri], rings[ri + 1]
        for k in range(n):
            j = (k + 1) % n
            if (k + ri) % 2:
                faces += [bm.faces.new((r0[k], r0[j], r1[j])), bm.faces.new((r0[k], r1[j], r1[k]))]
            else:
                faces += [bm.faces.new((r0[k], r0[j], r1[k])), bm.faces.new((r0[j], r1[j], r1[k]))]
    top = bm.faces.new(rings[-1])
    bot = bm.faces.new(list(reversed(rings[0])))
    _tri(bm, [top, bot])
    vs = [v for r in rings for v in r]
    # the base ring sits on the ground
    for v in rings[0]:
        v.co.z = 0.0
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    _place(bm, vs, Matrix.Translation((centre[0], centre[1], 0.0)))
    a._finish(vs, ROCK, tint=1.0)
    return vs


# ---- hull rocks: the foot rock, medium and small rocks (spec 1.4) -------------------------------------------------------
# Point clouds: rings (height fraction, radius fraction, points), jittered; the top ring flat (one top facet, tilted by
# `slope` deg falling toward -Y rotated by `slope_az`); `nose`: the front-most point of a ring pushed forward by this
# fraction of W (F's nose vertex). The cloud is yawed and scaled to the rock's exact world size.
CLOUDS = {
    # fix round 1: the widest ring at 0.55, the 0.80 ring at 0.84 and the top at 0.47 (was .50 / .76 at 0.86 / 0.55):
    # the upper faces slope in (top band 39 deg) to a smaller flat top 0.49 W across (a faceted dome, not a box)
    "F": dict(rings=((0.0, 0.74, 7), (0.55, 1.0, 7), (0.80, 0.84, 6), (1.0, 0.47, 4)), jit=0.08, seed=39121,
              ang_jit=0.45, chips=3,
              slope=7.0, nose=(1, 0.16),
              cuts=(((-1.0, 0.05, 0.1), 0.92, 0.50), ((1.0, 0.15, 0.05), 0.94, 0.50),
                    ((-0.75, -0.66, 0.15), 0.78, 0.40), ((0.72, -0.70, 0.10), 0.80, 0.40),
                    ((0.3, 0.95, 0.3), 0.80, 0.5))),
    # medium rocks: few points, flat cut planes for big facets (no ball): a broad front facet, a side facet
    "MED": dict(rings=((0.0, 0.86, 5), (0.38, 1.0, 6), (0.78, 0.84, 4), (1.0, 0.64, 4)), jit=0.14, seed=39122, ang_jit=0.45, chips=4,
                slope=5.0, cuts=(((0.15, -1.0, 0.15), 0.78, 0.45), ((-1.0, 0.2, 0.1), 0.84, 0.5),
                                 ((0.8, 0.5, 0.35), 0.78, 0.55))),
    "MEDS": dict(rings=((0.0, 0.86, 5), (0.38, 1.0, 6), (0.78, 0.84, 4), (1.0, 0.62, 4)), jit=0.14, seed=39123, ang_jit=0.45, chips=4,
                 slope=16.0, slope_az=-40.0, cuts=(((0.6, -0.8, 0.2), 0.78, 0.45), ((-0.9, -0.3, 0.3), 0.80, 0.5))),
    "DOME": dict(rings=((0.0, 0.86, 6), (0.38, 1.0, 7), (0.75, 0.84, 5), (1.0, 0.50, 4)), jit=0.11, seed=39124, ang_jit=0.45, chips=4,
                 slope=3.0, cuts=(((0.0, -1.0, 0.1), 0.82, 0.45), ((-0.8, 0.5, 0.3), 0.80, 0.5),
                                  ((0.9, 0.3, 0.2), 0.84, 0.5))),
    "SM": dict(rings=((0.0, 0.80, 5), (0.40, 1.0, 5), (0.78, 0.72, 4), (1.0, 0.42, 3)), jit=0.13, seed=39125, ang_jit=0.45, chips=2,
               slope=4.0, cuts=(((0.2, -1.0, 0.2), 0.82, 0.4),)),
}
# name -> cloud, centre (x, y), size (W, D, H), yaw (deg), seed offset  (spec 2.1)
ROCKS = {
    "F": ("F", (0.05, -2.70), (5.0, 3.8, 3.7), 0.0, 0),
    "BL": ("MED", (-4.85, 0.00), (2.4, 2.2, 2.9), 20.0, 1),
    "FL": ("MED", (-3.90, -2.10), (2.8, 2.4, 2.1), -15.0, 2),
    "FR": ("MEDS", (5.95, 0.50), (2.1, 2.0, 2.3), 35.0, 3),
    "s1": ("SM", (-3.05, -3.50), (1.05, 0.9, 0.75), 10.0, 4),
    "s2": ("SM", (2.95, -3.60), (1.4, 1.2, 1.0), -20.0, 5),
    "s3": ("SM", (4.40, -2.60), (1.75, 1.4, 1.2), 30.0, 6),
    "BD": ("DOME", (-0.60, 4.50), (3.3, 2.8, 2.9), 160.0, 7),
    "BR": ("MEDS", (4.30, 3.20), (2.1, 2.0, 2.3), 140.0, 8),
    "BS": ("SM", (-4.40, 2.40), (1.2, 1.0, 0.8), 70.0, 9),
}
ROCK_INFO = {}


def _cloud(cloud, seed_off=0):
    cp = CLOUDS[cloud]
    rng = random.Random(cp["seed"] + 97 * seed_off)
    pts = m033._ring_pts(rng, cp["rings"], 1.0, 1.0, 1.0, cp["jit"], (0.0, 0.0), ang_jit=cp.get("ang_jit", 0.30))
    # chips: a few extra points just inside the hull next to an upper point, so small chip facets sit beside the
    # broad faces (irregular triangle sizes, spec 2.2: area CV >= 0.6)
    for _ in range(cp.get("chips", 0)):
        q = rng.choice([p for p in pts if 0.3 < p.z < 0.95])
        t = Vector((-q.y, q.x, 0.0)).normalized() * rng.choice((-1, 1))
        pts.append(q * 0.97 + t * rng.uniform(0.12, 0.2) + Vector((0, 0, rng.uniform(-0.08, 0.08))))
    for nrm, dd, zc in cp.get("cuts", ()):
        # every point beyond the plane (unit normal, distance from (0, 0, zc)) moves onto it: one big flat facet;
        # floor points slide horizontally so the floor stays flat (m038)
        nv = Vector(nrm).normalized()
        c0 = Vector((0.0, 0.0, zc))
        for p in pts:
            s = (p - c0).dot(nv) - dd
            if s <= 0:
                continue
            if p.z < 1e-6:
                nh = Vector((nv.x, nv.y, 0.0))
                if nh.length > 1e-6:
                    p -= nh.normalized() * (s / nh.length)
            else:
                p -= nv * s
                p.z = max(0.0, p.z)
    if cp.get("nose"):
        # after the cuts: the nose stands out of the flat front faces, so five big faces meet at it
        ri, f = cp["nose"]
        h = cp["rings"][ri][0]
        ring = [p for p in pts if abs(p.z - h) < 0.2 and 0 < p.z < 1]
        if ring:
            p = min(ring, key=lambda q: q.y)
            p.y -= f * 2.0
            p.x *= 0.5
    tz = math.tan(math.radians(cp.get("slope", 0.0)))
    az = math.radians(cp.get("slope_az", 0.0))
    dirn = Vector((math.sin(az), -math.cos(az)))       # the direction the top falls toward
    for p in pts:
        if p.z > 0.999:
            p.z = 1.0 - tz * (Vector((p.x, p.y)).dot(dirn) + 1.0) * 0.5
    return pts


def _rock_pts(name, centre=None):
    cloud, c, size, yaw, so = ROCKS[name]
    c = centre if centre is not None else c
    pts = [Matrix.Rotation(math.radians(yaw), 3, "Z") @ p for p in _cloud(cloud, so)]
    xs, ys, zs = [p.x for p in pts], [p.y for p in pts], [p.z for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    sx, sy, sz = size[0] / (max(xs) - min(xs)), size[1] / (max(ys) - min(ys)), size[2] / max(zs)
    return [Vector(((p.x - cx) * sx + c[0], (p.y - cy) * sy + c[1], p.z * sz)) for p in pts]


def _hull_rock(a, name, centre=None):
    vs = _hull_bm(a.bm, _rock_pts(name, centre))
    a._finish(vs, ROCK, tint=1.0)
    return vs


def _rock(a, name, centre=None):
    """Any rock by its layout name; returns its verts."""
    if name == "S":
        return _spire(a, centre if centre is not None else SPIRE_AT)
    if name in SIDES:
        return _side_rock(a, name, centre if centre is not None else SIDE_AT[name])
    return _hull_rock(a, name, centre)


# fix round 1: P 0.12 to -X (S-P full-SAT overlap 0.625 -> 0.58; 0.04 gave only 0.61)
SIDE_AT = {"P": (-1.94, 0.35), "Rr": (3.65, 0.30)}
ROCK_ORDER = ("S", "P", "Rr", "F", "BL", "FL", "FR", "s1", "s2", "s3", "BD", "BR", "BS")
ROCK_H = {"S": SPIRE["H"], "P": SIDES["P"]["size"][2], "Rr": SIDES["Rr"]["size"][2],
          **{k: v[2][2] for k, v in ROCKS.items()}}


# ---- rock colour (spec 5.3, 5.5): per flat facet, by position only --------------------------------------------------------
# Broad noise patches on the upper part -> rock_light (25-30 %, the spire's upper third 35 %); patches low down ->
# rock_deep (15-20 %); faint olive stains on whole facets near rosette roots (<= 20 %); Tint per facet.
LIGHT = dict(scale=0.30, level=0.00, width=0.30, mix=0.30, h0=0.55, seed=39131)
DEEP = dict(scale=0.32, level=0.05, width=0.30, mix=0.20, z1=1.5, seed=39132)
SPIRE_LIGHT = dict(h0=0.62, mix=0.35)
STAIN_R, STAIN_Z, STAIN_MIX = 1.6, 2.5, 0.20
ROCK_MOTTLE = dict(amp=0.04, scale=0.30, seed=39141)
ROOTS = []          # rosette roots placed so far (for the stains)


def _paint_rock(a, vs, seed, H, spire=False):
    fs = _faces(vs)
    floor = [f for f in fs if f.normal.z < -0.99 and f.calc_center_median().z < 1e-3]
    fl = set(floor)
    side = [f for f in fs if f not in fl]
    regs = _regions(side)
    nl = K.noise_field(LIGHT["scale"], LIGHT["seed"] + seed)
    nd = K.noise_field(DEEP["scale"], DEEP["seed"] + seed)
    h0 = SPIRE_LIGHT["h0"] if spire else LIGHT["h0"]
    lmix = SPIRE_LIGHT["mix"] if spire else LIGHT["mix"]
    stained = 0
    for reg in regs:
        c = _centroid(reg)
        hf = c.z / H
        tl = _q((nl(c) - LIGHT["level"]) / LIGHT["width"]) if hf > h0 else 0.0
        if spire and hf > 0.85:
            tl = max(tl, 0.67)
        td = _q((nd(c) - DEEP["level"]) / DEEP["width"]) if c.z < DEEP["z1"] else 0.0
        ts = 0.0
        if c.z < STAIN_Z and ROOTS:
            d = min((c - r).length for r in ROOTS)
            ts = _q(1.0 - d / STAIN_R, 2)
        if ts > 0:
            key = K.mix_key(ROCK, STAIN, round(ts * STAIN_MIX, 2))
            stained += 1
        elif td > 0 and td >= tl:
            key = K.mix_key(ROCK, ROCK_DEEP, round(td * DEEP["mix"] / 0.2 * 0.2, 2))
        elif tl > 0:
            key = K.mix_key(ROCK, ROCK_LIGHT, round(min(1.0, tl * lmix), 2))
        else:
            key = ROCK
        mi = a._mi(key)
        for f in reg:
            f.material_index = mi
    mi = a._mi(ROCK)
    for f in floor:
        f.material_index = mi
    _tint_regions(a, regs, ROCK_MOTTLE["amp"], ROCK_MOTTLE["scale"], ROCK_MOTTLE["seed"] + seed,
                  tint=1.0 + random.Random(seed).uniform(-0.04, 0.04))
    return stained


def _paint_all(a, names):
    out = {}
    for nm in names:
        vs = K.part(a, nm)
        if vs:
            out[nm] = _paint_rock(a, vs, sum(map(ord, nm)) + 39000, ROCK_H[nm], spire=(nm == "S"))
    return out


# ---- rock-shape metrics (spec 2.2) --------------------------------------------------------------------------------------
def rock_metrics(fs, view=(0.0, 20.0)):
    ground = [f for f in fs if f.normal.z < -0.99 and f.calc_center_median().z < 1e-3]
    gs = set(ground)
    side = [f for f in fs if f not in gs]
    areas = np.array([f.calc_area() for f in side])
    edges = list({e for f in side for e in f.edges})
    el = np.array([e.calc_length() for e in edges])
    vs = [v for v in {v for f in side for v in f.verts} if v.co.z > 1e-3]
    val = np.array([len(v.link_edges) for v in vs])
    allv = list({v for f in fs for v in f.verts})
    xs, ys, zs = [v.co.x for v in allv], [v.co.y for v in allv], [v.co.z for v in allv]
    W, D, H = max(xs) - min(xs), max(ys) - min(ys), max(zs)

    def width(z):
        pts = []
        for e in edges:
            a_, b_ = e.verts
            if (a_.co.z - z) * (b_.co.z - z) < 0:
                t = (z - a_.co.z) / (b_.co.z - a_.co.z)
                pts.append(a_.co.lerp(b_.co, t).x)
        return (max(pts) - min(pts)) if pts else 0.0
    hs = np.linspace(0.05, 0.95, 10)
    widths = [width(h * H) for h in hs]
    wmax = max(widths) or 1.0
    small = 0
    for f in side:
        p = [v.co for v in f.verts]
        angs = [(p[(i + 1) % 3] - p[i]).angle(p[(i + 2) % 3] - p[i], 0.0) for i in range(3)]
        small += min(angs) < math.radians(25)
    az, elv = math.radians(view[0]), math.radians(view[1])
    vv = Vector((math.sin(az) * math.cos(elv), -math.cos(az) * math.cos(elv), math.sin(elv)))
    out = {}
    for thr in (5.0, 7.0):
        regs = _regions(side, ang=thr)
        proj = [sum(g.calc_area() * max(0.0, g.normal.dot(vv)) for g in reg) for reg in regs]
        tot = sum(proj) or 1.0
        seen = sorted([p / tot for p in proj if p / tot >= 0.004], reverse=True)
        out[f"facets{int(thr)}"] = [len(seen), round(seen[0], 3) if seen else 0]
    tall = sum(1 for f in side if (max(v.co.z for v in f.verts) - min(v.co.z for v in f.verts)) > 0.35 * H)
    big = sum(1 for f in side if f.calc_area() >= 2.5)
    regs2 = _regions(side, ang=2.0)
    big_reg = sum(1 for r in regs2 if sum(f.calc_area() for f in r) >= 2.5)
    wall = sum(f.calc_area() for f in side if abs(f.normal.z) < math.sin(math.radians(20)))
    top = [f for f in side if f.normal.z > 0.95]
    # the upper faces' slope (deg from horizontal, area-weighted) above 0.55 H, the top facet excluded (fix round 1:
    # the foot rock's upper faces should slope 35-45 deg, not stand as walls under a big flat top)
    def _slope(lo):
        up = [f for f in side if f.normal.z <= 0.95 and f.calc_center_median().z > lo * H]
        ua = sum(f.calc_area() for f in up)
        return sum(math.degrees(math.acos(max(-1.0, min(1.0, f.normal.z)))) * f.calc_area() for f in up) / ua \
            if ua else 0.0
    upper_slope = _slope(0.55)
    band_slope = _slope(0.78)      # the band between the 0.80 H ring and the top facet
    tx = [v.co.x for f in top for v in f.verts]
    gx = [v.co.x for f in ground for v in f.verts]
    gy = [v.co.y for f in ground for v in f.verts]
    out.update({
        "tris": len(side) + len(ground), "size": [round(W, 2), round(D, 2), round(H, 2)], "h_w": round(H / W, 2),
        "area_cv": round(float(areas.std() / areas.mean()), 2), "edge_cv": round(float(el.std() / el.mean()), 2),
        "valence": [int(val.min()), int(val.max()), round(float(val.mean()), 2),
                    round(float(np.bincount(val).max() / len(val)), 2)],
        "small_angle_share": round(small / max(1, len(side)), 2),
        "widths": [round(w / wmax, 2) for w in widths], "widest_h": round(float(hs[int(np.argmax(widths))]), 2),
        "tall_faces": tall, "faces_ge_2.5": big, "regions_ge_2.5": big_reg,
        "min_face_area": round(float(areas.min()), 3),
        "wall_share": round(wall / max(1e-9, float(areas.sum())), 2),
        "top_faces": len(top), "top_span": round((max(tx) - min(tx)) / W, 2) if tx else 0,
        "upper_slope": round(upper_slope, 1), "top_band_slope": round(band_slope, 1),
        "floor_span": [round((max(gx) - min(gx)) / W, 2) if gx else 0, round((max(gy) - min(gy)) / D, 2) if gy else 0]})
    return out


# ---- leaves, buds, rosettes (spec 1.4 Foliage Cluster, 2.3) --------------------------------------------------------------
# Leaves (fix round 1): broad ovals. An 8-point outline: the stem point, a wide base pair at 0.20 L, the widest pair at
# 0.58 L, a blunt shoulder pair at 0.92 L and a rounded tip point at 0.98 L (tip corner ~150 deg, shoulders ~125 deg).
# The midrib (stem -> tip) is a low crease-ridge, camber <= 0.07 L above the rim, falling linearly to the rim, so each
# half is one near-flat plane: a lit half and a shaded half, like the sheet's folded leaves. The underside is a strip
# across the midrib (12 tris, a closed solid with its thickness under the midrib). Round 1's kite outline with a
# 0.16 L two-point midrib read as green shards.
LEAF_OUT = ((0.20, 0.70), (0.58, 1.00), (0.92, 0.45))
LEAF_TIP = 0.98
LEAF_W = 0.74
ROS_SCALE = 1.4               # every table rosette width x this (the sheet's clumps are lush; f34 green 22.7 %)
LEAF_CAMBER, LEAF_CURL = 0.06, 0.08
LEAF_L = 0.48                 # leaf length / rosette width
LEAF_MOTTLE = dict(amp=0.04, scale=0.9, seed=39411)
CL_TINT = 0.04
CONTACT = 0.03                # every leaf / bud ends within this of the ground, a rock or another leaf (STAGES)
DROP_DEPTH = 0.15             # a leaf this far inside a rock is left out (less is pushed out to touch it)
MAX_CUT = 0.05                # after the push, a leaf or bud still deeper than this in a rock is left out (spec 2.3)
# re-tries for a leaf that cuts into a rock: (yaw deg, extra pitch deg, length factor), in order
VARIANTS = ((0, 0, 1.0), (0, 15, 1.0), (25, 10, 1.0), (-25, 10, 1.0), (0, 30, 0.9), (45, 20, 0.9), (-45, 20, 0.9),
            (0, 45, 0.8))
BUD_R = 0.11                  # bud radius / rosette width
# the bud: a squat round dome, equator at 0.05 r (in the hub), top ring 0.62 r wide, flat top at 0.85 r (round 1: a
# double cone with its apex at 1.45 r)
BUD_RING, BUD_SH, BUD_TOP = 0.05, 0.62, 0.85
# leaf roles by count: (azimuth offset from the face direction in deg, pitch in deg, length factor, role)
# role 2: the upright back leaf (light), 1: side leaves, 0: low front leaves (deep)
# fix round 1: the back leaf is upright but broad (pitch 48-50, length 1.0), no tall pointed shard
# and the low front leaves lie flatter (12-14 deg) so the sheet cameras (e 18-25) see them as ovals, not edge-on slivers
ROLES = {
    7: ((180, 50, 1.0, 2), (115, 34, 1.0, 1), (-115, 34, 1.0, 1), (62, 16, 0.95, 0), (-62, 16, 0.95, 0),
        (18, 12, 0.92, 0), (-24, 12, 0.92, 0)),
    6: ((180, 50, 1.0, 2), (112, 34, 1.0, 1), (-112, 34, 1.0, 1), (52, 15, 0.95, 0), (-52, 15, 0.95, 0),
        (0, 12, 0.92, 0)),
    5: ((180, 50, 1.0, 2), (100, 34, 1.0, 1), (-100, 34, 1.0, 1), (35, 13, 0.92, 0), (-35, 13, 0.92, 0)),
    4: ((180, 50, 1.0, 2), (95, 34, 1.0, 1), (-95, 34, 1.0, 1), (0, 13, 0.92, 0)),
    3: ((160, 48, 1.0, 2), (40, 26, 1.0, 1), (-80, 14, 1.0, 0)),
}
CLUSTER_INFO = {}


def _leaf(a, base, L, key, yaw, pitch, width=LEAF_W, outline=LEAF_OUT, camber=LEAF_CAMBER, curl=LEAF_CURL,
          roll=0.0, frame=None):
    """One broad oval leaf (a closed solid, 12 tris). base = the stem end; yaw about Z; pitch = its rise (rad).
    outline: (x / L, half-width fraction) pairs from the base to the shoulder pair; the tip point at LEAF_TIP L.
    frame: an extra rotation (the rosette's tilt) applied about the base."""
    bm = a.bm
    W = width * L / 2
    rot = Matrix.Rotation(yaw, 3, "Z") @ Matrix.Rotation(-pitch, 3, "Y") @ Matrix.Rotation(roll, 3, "X")
    if frame is not None:
        rot = frame @ rot
    B = Vector(base)

    def put(x, y):
        t = x / L
        # the midrib ridge: camber at y 0 falling linearly to the rim (each half one plane), the tip curling down
        return bm.verts.new(B + rot @ Vector((x, y, camber * L * (1.0 - abs(y) / W) - curl * L * t * t)))
    stem = put(0.0, 0.0)
    right = [put(f * L, -h * W) for f, h in outline]
    tip = put(LEAF_TIP * L, 0.0)
    left = [put(f * L, h * W) for f, h in outline]
    faces = []
    # top: each half a fan from the stem (stem -> tip is the crease)
    rr = right + [tip]
    ll = left + [tip]
    for i in range(len(rr) - 1):
        faces.append(bm.faces.new((stem, rr[i], rr[i + 1])))
        faces.append(bm.faces.new((stem, ll[i + 1], ll[i])))
    # underside: a strip across the midrib
    faces.append(bm.faces.new((stem, left[0], right[0])))
    for i in range(len(outline) - 1):
        faces.append(bm.faces.new((right[i], left[i], left[i + 1])))
        faces.append(bm.faces.new((right[i], left[i + 1], right[i + 1])))
    faces.append(bm.faces.new((right[-1], left[-1], tip)))
    vs = [stem] + right + [tip] + left
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    a._finish(vs, key, tint=1.0)
    return vs


def _bud(a, root, w, frame=None):
    """The round lime bud: a squat two-ring dome (14 tris): a 6-vert equator at BUD_RING r (in the hub, among the leaf
    stems), a 3-vert top ring (radius BUD_SH r, a flat top) at BUD_TOP r, and a flat floor."""
    bm = a.bm
    r = BUD_R * w
    rot = frame if frame is not None else Matrix.Identity(3)
    R = Vector(root)

    def at(ang, rad, z):
        return bm.verts.new(R + rot @ Vector((math.cos(ang) * rad, math.sin(ang) * rad, z)))
    ring = [at(k * math.pi / 3 + 0.3, r, BUD_RING * r) for k in range(6)]
    top = [at((2 * i + 1) * math.pi / 3 + 0.3, BUD_SH * r, BUD_TOP * r) for i in range(3)]
    fs = []
    for i in range(3):
        e0, e1, e2 = ring[2 * i], ring[2 * i + 1], ring[(2 * i + 2) % 6]
        fs += [bm.faces.new((e0, e1, top[i])), bm.faces.new((e1, e2, top[i])),
               bm.faces.new((e2, top[(i + 1) % 3], top[i]))]
    fs.append(bm.faces.new(top))
    for k in range(1, 5):
        fs.append(bm.faces.new((ring[0], ring[k + 1], ring[k])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    vs = ring + top
    a._finish(vs, BUD, tint=1.0)
    return vs


class _Guard:
    """Keeps a leaf out of the rocks: more than `allow` inside, it is moved out along the surface normal at its deepest
    vert (horizontal part, never down). (m036)"""

    def __init__(self, tree):
        # one tree, or (fix round 1) a list of per-rock trees: with one tree over overlapping rocks the nearest surface
        # can belong to the neighbour, so a vertex inside one rock read as outside (a C2 bud sat 0.23 inside FL)
        self.trees = [] if tree is None else (list(tree) if isinstance(tree, (list, tuple)) else [tree])
        self.tree = self.trees[0] if self.trees else None
        self.moved = 0

    RAYS = (Vector((0.0, 0.0, 1.0)), Vector((0.31, 0.17, 0.93)).normalized())

    @staticmethod
    def _inside(t, p):
        """Ray parity on one closed rock (both rays odd). The nearest face's normal sign misreads points beside an
        edge (a floor edge gives "inside" to a leaf just outside a rock's foot)."""
        for dv in _Guard.RAYS:
            c, x = 0, p.copy()
            for _ in range(24):
                h = t.ray_cast(x, dv)
                if h[0] is None:
                    break
                c += 1
                x = h[0] + dv * 1e-5
            if c % 2 == 0:
                return False
        return True

    def depth(self, vs):
        worst, nrm = 0.0, None
        for t in self.trees:
            for v in vs:
                loc, n, _, d = t.find_nearest(v.co)
                if loc is None or n is None or d <= worst or d < 1e-5:
                    continue
                if self._inside(t, v.co):
                    worst, nrm = d, n
        return worst, nrm

    def push(self, vs, allow, clearance=0.02):
        if self.tree is None:
            return
        for _ in range(5):
            worst, nrm = self.depth(vs)
            if worst <= allow or nrm is None:
                return
            m = Vector((nrm.x, nrm.y, max(0.0, nrm.z)))
            if m.length < 1e-6:
                m = Vector((nrm.x, nrm.y, 0.0))
            m.normalize()
            for v in vs:
                v.co += m * (worst - allow + clearance)
            self.moved += 1


def _lift(vs, floor=0.004):
    z = min(v.co.z for v in vs)
    if z < floor:
        for v in vs:
            v.co.z += floor - z


def _kill(a, vs):
    bmesh.ops.delete(a.bm, geom=[v for v in vs if v.is_valid], context="VERTS")


def _leaf_key(role, shift=0):
    """role 0 low front (leaf_deep 40 %), 1 side (leaf), 2 upright back (leaf_light 67 %); shift: one step lighter
    (the high rosettes C4, C10)."""
    t = role + shift
    if t <= 0:
        return K.mix_key(LEAF, LEAF_DEEP, 0.4)
    if t == 1:
        return LEAF
    if t == 2:
        return K.mix_key(LEAF, LEAF_LIGHT, 0.67)
    return LEAF_LIGHT


def _rosette(a, root, w, n, seed, face, up=None, shift=0, guard=None, tint=1.0, info=None):
    """A star rosette: n broad oval leaves round a round bud, all rooted at `root`; face = the azimuth the low leaves
    point to (the upright leaf points the other way); up = the rosette's axis (tilted off a flank). Returns verts."""
    rng = random.Random(seed)
    R = Vector(root)
    frame = None
    if up is not None and Vector(up).normalized().z < 0.999:
        frame = Vector((0, 0, 1)).rotation_difference(Vector(up).normalized()).to_matrix()
    L0 = LEAF_L * w
    allv = []
    for k, (off, pitch, lf, role) in enumerate(ROLES[n]):
        yaw = face + math.radians(off + rng.uniform(-12, 12))
        L = L0 * lf * rng.uniform(0.92, 1.06)
        p = math.radians(pitch + rng.uniform(-5, 5))
        d = Vector((math.cos(yaw), math.sin(yaw), 0.0))
        loc = d * 0.04 * w + Vector((0, 0, 0.012 * w))
        base = R + (frame @ loc if frame is not None else loc)
        roll = rng.uniform(-0.25, 0.25)
        vs = None
        # fix round 1: a leaf that cuts into a rock is re-tried turned and raised (VARIANTS) before it is left out; a
        # kept leaf is pushed out to <= 0.03 and never ends deeper than MAX_CUT
        for dy, dp, dl in (VARIANTS if guard is not None else ((0, 0, 1.0),)):
            vs = _leaf(a, tuple(base), L * dl, _leaf_key(role, shift), yaw + math.radians(dy),
                       min(p + math.radians(dp), math.radians(75)), roll=roll, frame=frame)
            if guard is None:
                break
            if guard.depth(vs)[0] <= DROP_DEPTH:
                guard.push(vs, 0.03)
                if guard.depth(vs)[0] <= MAX_CUT:
                    if info is not None and (dy or dp or dl != 1.0):
                        info["retried"] = info.get("retried", 0) + 1
                    break
            _kill(a, vs)
            vs = None
        if vs is None:
            if info is not None:
                info["dropped"] = info.get("dropped", 0) + 1
            continue
        _lift(vs)
        _mottle(a, _faces(vs), LEAF_MOTTLE["amp"], LEAF_MOTTLE["scale"], LEAF_MOTTLE["seed"] + seed, tint=tint)
        allv += vs
        if info is not None:
            info["leaves"] = info.get("leaves", 0) + 1
    bv = _bud(a, R, w, frame)
    if guard is not None:
        guard.push(bv, 0.03)
        # in a crevice the push can't clear both rocks: raise the bud along the rosette's axis instead
        ax = frame @ Vector((0, 0, 1)) if frame is not None else Vector((0, 0, 1))
        for _ in range(4):
            dep = guard.depth(bv)[0]
            if dep <= 0.03:
                break
            for v in bv:
                v.co += ax * (dep + 0.01)
    _lift(bv)
    allv += bv
    if info is not None:
        info["buds"] = info.get("buds", 0) + 1
    return allv


def _ray_down(tree, xy, z_from=20.0):
    if tree is None:
        return None
    h = tree.ray_cast(Vector((xy[0], xy[1], z_from)), Vector((0, 0, -1)), 200)
    return h if h[0] is not None else None


def _ray_side(tree, xy, z, az):
    """From (xy, z) horizontally toward azimuth az (deg): the first rock hit (loc, normal) or None."""
    d = Vector((math.cos(math.radians(az)), math.sin(math.radians(az)), 0.0))
    h = tree.ray_cast(Vector((xy[0], xy[1], z)), d, 20.0)
    return h if h[0] is not None else None


# Clusters (spec 2.3): name -> rosettes [(x, y, seat, w, leaves, face az deg)], tier shift, seed.
# seat: "g" on the ground; ("t", z_from): on the rock top under (x, y) (ray down from z_from); ("f", z, az): on a rock
# flank at height z, reached by a horizontal ray from (x, y) toward azimuth az: the rosette leans out (its axis tilted
# FLANK_TILT toward the flank's outward normal) with its root on the flank.
FLANK_TILT = 0.45
CLUSTERS = (
    ("C1", ((-6.30, -0.90, "g", 1.8, 7, -120), (-5.60, -1.95, "g", 1.6, 7, -100), (-6.00, -1.35, "l", 1.6, 6, -110)),
     0, 39401),
    ("C2", ((-3.40, -1.15, "g", 2.0, 7, -95), (-3.40, -1.15, "l", 1.5, 6, -95), (-2.80, -1.45, "g", 1.7, 6, -90), (-3.30, -1.75, ("t", 5.0), 1.7, 7, -100),
            (-3.30, -1.40, ("f", 3.0, 40.0), 1.7, 7, -110), (-4.00, -0.70, ("f", 3.6, 15.0), 1.5, 6, -110)), 0, 39402),
    ("C3", ((-1.30, -1.40, ("t", 6.0), 1.5, 6, -90), (-0.50, -1.25, ("t", 6.0), 1.4, 6, -80)), 0, 39403),
    ("C4", ((-0.90, 0.90, ("t", 9.5), 1.7, 7, -70), (-0.70, 1.20, "l", 1.2, 5, -60)), 1, 39404),
    ("C5", ((0.90, -1.20, ("t", 6.0), 2.0, 7, -90), (1.60, -1.00, ("t", 6.0), 1.6, 6, -60), (1.20, -1.10, "l", 1.4, 6, -80)), 0, 39405),
    ("C6", ((2.55, -0.95, "g", 1.9, 7, -80), (1.60, -0.60, ("f", 1.7, 0.0), 1.7, 7, -100),
            (2.40, -0.80, "l", 1.5, 6, -90), (2.70, -1.90, "g", 1.7, 7, -80), (1.70, -0.90, ("f", 3.0, 0.0), 1.6, 7, -100),
            (2.00, -1.90, ("t", 6.0), 1.6, 6, -70)), 0, 39406),
    ("C7", ((3.50, -1.70, "g", 1.7, 7, -80), (4.40, -1.40, "g", 1.8, 7, -60), (3.90, -1.50, "l", 1.6, 6, -70), (4.40, -1.30, "l", 1.5, 6, -60), (3.30, -2.45, "g", 1.6, 6, -90)), 0,
     39407),
    ("C8", ((1.90, -4.00, "g", 1.1, 5, -90),), 0, 39408),
    ("C9", ((5.30, -1.40, "g", 1.9, 7, -50), (5.30, -1.30, "l", 1.5, 6, -40), (5.80, -0.60, "g", 1.6, 6, -30)), 0, 39409),
    ("C10", ((2.90, 0.40, ("t", 7.0), 1.7, 7, -60), (2.90, 0.60, "l", 1.4, 6, -50),
             (3.80, 1.00, ("f", 6.5, 180.0), 1.6, 7, -20)), 1, 39410),
    ("C11", ((-2.40, -3.90, "g", 0.9, 4, -90),), 0, 39411),
    ("B1", ((-3.00, 2.80, "g", 2.0, 7, 130), (-2.40, 2.10, "g", 1.8, 7, 160), (-3.50, 3.50, "g", 1.7, 6, 110)), 0,
     39412),
    ("B2", ((1.80, 4.60, "g", 1.6, 6, 60),), 0, 39413),
    ("B3", ((5.30, 2.30, "g", 1.6, 6, 20),), 0, 39414),
)


def _seat(a, tree, x, y, seat, w, guard=None):
    """Root point and axis for a rosette seat."""
    if seat == "g":
        p = Vector((x, y, 0.0))
        # fix round 1: a ground root inside a rock's foot (C2's first root was inside FL's back edge) slides out
        # horizontally by the shortest way (16 horizontal rays) to just outside it, so its bud doesn't sit in the rock
        for t in (guard.trees if guard is not None else ()):
            for _ in range(3):
                q = p + Vector((0, 0, 0.12))
                if not _Guard._inside(t, q):
                    break
                best = None
                for k in range(16):
                    dv = Vector((math.cos(k * math.pi / 8), math.sin(k * math.pi / 8), 0.0))
                    h = t.ray_cast(q, dv, 20.0)
                    if h[0] is not None and (best is None or h[3] < best[0]):
                        best = (h[3], dv)
                if best is None:
                    break
                p += best[1] * (best[0] + 0.10)
        return p, None
    if seat == "l":
        # the highest surface (leaves or rock) over a small disk round the root: the rosette's hub rests on the
        # rosettes below it (no hidden stems)
        a.bm.verts.ensure_lookup_table()
        a.bm.faces.ensure_lookup_table()
        t = BVHTree.FromBMesh(a.bm)
        zs = []
        for k in range(7):
            dx = 0.10 * w * math.cos(k * 1.0472) * (k > 0)
            dy = 0.10 * w * math.sin(k * 1.0472) * (k > 0)
            h = _ray_down(t, (x + dx, y + dy), 20.0)
            zs.append(h[0].z if h is not None else 0.0)
        zs.sort()
        return Vector((x, y, max(0.0, zs[len(zs) // 2 + 1] - 0.06))), None
    if seat[0] == "t":
        h = _ray_down(tree, (x, y), seat[1])
        if h is None:
            return Vector((x, y, 0.0)), None
        return h[0] - Vector((0, 0, 0.03)), None
    _, z, az = seat
    h = _ray_side(tree, (x, y), z, az)
    if h is None:
        return Vector((x, y, z)), None
    n = Vector((h[1].x, h[1].y, 0.0)).normalized()
    up = Vector((0, 0, 1)).lerp(n, FLANK_TILT).normalized()
    return h[0] - n * 0.03, up


def _cluster(a, name, rosettes, shift, seed, guard, rock_tree):
    info = {"leaves": 0, "dropped": 0, "buds": 0, "roots": []}
    rng = random.Random(seed)
    tint = 1.0 + rng.uniform(-CL_TINT, CL_TINT)
    allv = []
    for i, (x, y, seat, w, n, face) in enumerate(rosettes):
        w *= ROS_SCALE
        root, up = _seat(a, rock_tree, x, y, seat, w, guard)
        if up is not None:
            # a flank rosette faces out of the flank, turned a little toward the table's direction
            fv = Vector((up.x, up.y)).normalized() + 0.6 * Vector((math.cos(math.radians(face)),
                                                                     math.sin(math.radians(face))))
            face = math.degrees(math.atan2(fv.y, fv.x))
        ROOTS.append(root.copy())
        info["roots"].append([round(c, 2) for c in root])
        allv += _rosette(a, root, w, n, seed + 13 * i, math.radians(face), up=up, shift=shift, guard=guard,
                         tint=tint, info=info)
    xs, ys, zs = ([v.co[i] for v in allv if v.is_valid] for i in range(3))
    if xs:
        info.update(size=[round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2)], top=round(max(zs), 2))
    CLUSTER_INFO[name] = info
    return [v for v in allv if v.is_valid]


def dressing(a, rock_tree, clusters=CLUSTERS, rock_trees=None):
    guard = _Guard(rock_trees or rock_tree)
    for name, ros, shift, seed in clusters:
        _cluster(a, name, ros, shift, seed, guard, rock_tree)
    return guard.moved


# ---- settle and contact: no floating dressing (STAGES; m038) -----------------------------------------------------------
def _shell_groups(bm):
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    bm.faces.index_update()
    bm.verts.index_update()
    ids, n = M._shell_ids(bm)
    fs = {}
    for f in bm.faces:
        fs.setdefault(ids[f.index], []).append(f)
    return ids, n, fs


def contacts(bm, base, tol=CONTACT):
    """Contact graph of a bmesh's shells. base: the shell ids that count as support (rocks). Returns (n, zmin, gap to
    the nearest other shell or the ground per shell, the set chained to the ground or a support at tol, faces, adj)."""
    ids, n, fs = _shell_groups(bm)
    tree = BVHTree.FromBMesh(bm)
    fsh = [ids[f.index] for f in bm.faces]
    vsh = {}
    for f in bm.faces:
        for v in f.verts:
            vsh[v.index] = fsh[f.index]
    zmin = [1e9] * n
    for v in bm.verts:
        s = vsh.get(v.index)
        if s is not None:
            zmin[s] = min(zmin[s], v.co.z)
    near = {}
    for i, j in tree.overlap(tree):
        a_, b_ = fsh[i], fsh[j]
        if a_ != b_:
            near[(min(a_, b_), max(a_, b_))] = 0.0
    for v in bm.verts:
        s = vsh.get(v.index)
        if s is None:
            continue
        for loc, _, fi, d in tree.find_nearest_range(v.co, tol * 3):
            t = fsh[fi]
            if t != s:
                k = (min(s, t), max(s, t))
                near[k] = min(near.get(k, 1e9), d)
    gap = [max(0.0, z) for z in zmin]
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    adj = {k: set() for k in range(n)}
    for (a_, b_), d in near.items():
        if d <= tol:
            adj[a_].add(b_)
            adj[b_].add(a_)
    seen = {k for k in range(n) if zmin[k] <= tol} | set(base)
    stack = list(seen)
    while stack:
        k = stack.pop()
        for m_ in adj[k]:
            if m_ not in seen:
                seen.add(m_)
                stack.append(m_)
    return n, zmin, gap, seen, fs, adj


def settle(a, support_parts, rounds=4):
    """Drop every group of dressing shells not chained to the ground or a rock at CONTACT straight down until its
    lowest-clearance vertex is 0.01 above whatever is under it. Returns the groups moved per round. (m038)"""
    bm = a.bm
    lay = bm.faces.layers.int.get("kit_part")
    pid = {v for k, v in a.__dict__.get("_parts", {}).items() if k in support_parts}
    moved = []
    for _ in range(rounds):
        ids, n, fs = _shell_groups(bm)
        base = {ids[f.index] for f in bm.faces if lay is not None and f[lay] in pid}
        n, zmin, gap, seen, fs, adj = contacts(bm, base)
        loose = [k for k in range(n) if k not in seen]
        if not loose:
            moved.append(0)
            break
        grp, gid = [], {}
        for k in loose:
            if k in gid:
                continue
            g, st = [], [k]
            gid[k] = len(grp)
            while st:
                x = st.pop()
                g.append(x)
                for y in adj[x]:
                    if y not in seen and y not in gid:
                        gid[y] = len(grp)
                        st.append(y)
            grp.append(g)
        cnt = 0
        for g in grp:
            gs = set(g)
            others = [f for f in bm.faces if ids[f.index] not in gs]
            ov = list({v for f in others for v in f.verts})
            vi = {v: i for i, v in enumerate(ov)}
            t = BVHTree.FromPolygons([v.co for v in ov], [[vi[v] for v in f.verts] for f in others])
            gv = list({v for k in g for f in fs[k] for v in f.verts})
            best = min(v.co.z for v in gv)
            for v in gv:
                h = t.ray_cast(v.co + Vector((0, 0, 1e-4)), Vector((0, 0, -1)), 50)
                if h[0] is not None:
                    best = min(best, v.co.z - h[0].z)
            if best > 0.01:
                for v in gv:
                    v.co.z -= best - 0.01
                cnt += 1
        moved.append(cnt)
        if not cnt:
            break
    return moved


def _kind(ks):
    if any(x.startswith("m039_rock") or x.startswith("m039_moss") for x in ks):
        return "rock"
    if ks == {BUD}:
        return "bud"
    if all(x.startswith("m039_leaf") for x in ks):
        return "leaf"
    return "other"


def contact_report(o, tol=CONTACT):
    """Floating dressing on a built object: shells whose nearest other shell (or the ground) is farther than tol, the
    worst such gap, and the shells with no chain of contact to the ground or a rock at tol and at 0.05."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    keys = [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]
    ids, n, fs = _shell_groups(bm)
    kind = {k: _kind({keys[f.material_index] for f in fs[k]}) for k in range(n)}
    base = {k for k in range(n) if kind[k] == "rock"}
    n, zmin, gap, seen, _, adj = contacts(bm, base, tol)
    floating = [k for k in range(n) if gap[k] > tol and k not in base]
    _, _, _, seen5, _, _ = contacts(bm, base, 0.05)
    bm.free()
    kinds = {}
    for k in range(n):
        kinds[kind[k]] = kinds.get(kind[k], 0) + 1
    return {"shells": n, "kinds": kinds, "floating": len(floating),
            "floating_kinds": sorted({kind[k] for k in floating}),
            "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
            "max_gap_dressing": round(max([gap[k] for k in range(n) if k not in base], default=0.0), 3),
            "unchained": n - len(seen), "unchained_005": n - len(seen5)}


def shells_report(o):
    """Per shell: kind, tris, non-manifold edges and verts, boundary edges, self-intersecting face pairs inside the
    shell, inverted faces (ray parity inside the shell), signed volume. (m035 / m036)"""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]
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
        inv = 0
        for f in fs:
            odd = 0
            for dv in (f.normal, (f.normal + f.normal.orthogonal().normalized() * 0.21).normalized(),
                       (f.normal - f.normal.orthogonal().normalized() * 0.17).normalized()):
                p = f.calc_center_median() + dv * 1e-4
                cnt, x, last = 0, p.copy(), None
                for _ in range(40):
                    h = tree.ray_cast(x, dv)
                    if h[0] is None:
                        break
                    if last is None or (h[0] - last).length > 1e-4:
                        cnt += 1
                    last = h[0]
                    x = h[0] + dv * 1e-5
                odd += cnt % 2
            inv += odd == 3
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) / 3.0
        out.append({"kind": _kind(ks), "tris": sum(len(f.verts) - 2 for f in fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary), "self_hits": hits, "inverted": inv,
                    "volume": round(vol, 4)})
    bm.free()
    return out


# ---- parts ----------------------------------------------------------------------------------------------------------------
def _new_parts(a):
    if a.bm.faces.layers.int.get("kit_part") is None:
        a.bm.faces.layers.int.new("kit_part")


PART_LOG = {}
PART_ROCKS = {}


def spire_part(a):
    _new_parts(a)
    ROOTS.clear()
    K.tag_part(a, _rock(a, "S", (0.0, 0.0)), "S")
    _paint_all(a, ("S",))
    PART_ROCKS[MAIN_P] = {"S": rock_metrics(_faces(K.part(a, "S")))}


def side_rock_part(a):
    """Rr with one rosette on its top (the exploded drops one there)."""
    _new_parts(a)
    ROOTS.clear()
    K.tag_part(a, _rock(a, "Rr", (0.0, 0.0)), "Rr")
    tree = K.bvh_of(K.part(a, "Rr"))
    _cluster(a, "part_side", ((-0.35, 0.05, ("t", 9.0), 1.3, 7, -90),), 0, 39431, _Guard(tree), tree)
    _paint_all(a, ("Rr",))
    PART_LOG[SIDE_P] = {"settle": settle(a, ("Rr",))}
    PART_ROCKS[SIDE_P] = {"Rr": rock_metrics(_faces(K.part(a, "Rr")))}


def foot_rock_part(a):
    """F with its two top sprigs (exploded)."""
    _new_parts(a)
    ROOTS.clear()
    K.tag_part(a, _rock(a, "F", (0.0, 0.0)), "F")
    tree = K.bvh_of(K.part(a, "F"))
    _cluster(a, "part_foot", ((-0.6, 0.5, ("t", 6.0), 1.0, 5, -90), (0.9, 0.8, ("t", 6.0), 0.9, 4, -60)), 0, 39432,
             _Guard(tree), tree)
    _paint_all(a, ("F",))
    PART_LOG[FOOT_P] = {"settle": settle(a, ("F",))}
    PART_ROCKS[FOOT_P] = {"F": rock_metrics(_faces(K.part(a, "F")))}


def small_rock_part(a):
    _new_parts(a)
    ROOTS.clear()
    K.tag_part(a, _rock(a, "s2", (0.0, 0.0)), "s2")
    _paint_all(a, ("s2",))
    PART_ROCKS[SMALL_P] = {"s2": rock_metrics(_faces(K.part(a, "s2")))}


def foliage_part(a):
    _new_parts(a)
    _cluster(a, "part_rosette", ((0.0, 0.0, "g", 1.6, 7, -90),), 0, 39441, None, None)
    PART_LOG[FOL_P] = {"settle": settle(a, ())}


# ---- hero -----------------------------------------------------------------------------------------------------------------
LAYOUT = {}
CONTACT_PAIRS = (("P", "S"), ("Rr", "S"), ("F", "P"), ("FL", "F"), ("FR", "Rr"), ("BD", "S"), ("BL", "FL"),
                 ("BL", "P"), ("F", "S"), ("F", "Rr"), ("s3", "Rr"), ("BS", "BL"), ("BR", "S"), ("BR", "Rr"))


def hero(a):
    _new_parts(a)
    ROOTS.clear()
    for nm in ROCK_ORDER:
        K.tag_part(a, _rock(a, nm), nm)
    rocks = {k: K.part(a, k) for k in ROCK_ORDER}
    LAYOUT["pen"] = _pens(rocks)
    LAYOUT["rocks"] = {k: rock_metrics(_faces(vs)) for k, vs in rocks.items()}
    tree = K.bvh_of([v for vs in rocks.values() for v in vs])
    LAYOUT["guard_moves"] = dressing(a, tree, rock_trees=[K.bvh_of(vs) for vs in rocks.values()])
    LAYOUT["settle"] = settle(a, ROCK_ORDER)
    LAYOUT["stained"] = _paint_all(a, ROCK_ORDER)


def _pens(rocks):
    """Penetration depth for every overlapping rock pair (convex-hull planes), and the gap for the contact pairs."""
    hulls = {k: _planes([v.co.copy() for v in vs if v.is_valid]) for k, vs in rocks.items()}
    trees = {k: K.bvh_of(vs) for k, vs in rocks.items()}
    out = {}
    names = list(hulls)
    for i, a_ in enumerate(names):
        for b_ in names[i + 1:]:
            pen = _pen(hulls[a_], hulls[b_])
            pair = (a_, b_) in CONTACT_PAIRS or (b_, a_) in CONTACT_PAIRS
            if pen > 1e-4:
                out[f"{a_}-{b_}"] = round(-pen, 2)
            elif pair:
                d = min(min(trees[b_].find_nearest(v.co)[3] for v in rocks[a_] if v.is_valid),
                        min(trees[a_].find_nearest(v.co)[3] for v in rocks[b_] if v.is_valid))
                out[f"{a_}-{b_}"] = round(d, 2)
    return out


NOTES = {
    HERO: "Rock spire: a tall angular warm grey-pink 7-sided obelisk with a flat-topped pillar leaning on its left, a "
          "shorter flat-topped side rock on its right, a big faceted foot rock in front, a ring of medium and small "
          "faceted rocks and lime star rosettes (broad oval leaves round a lime bud) in the crevices and up the "
          "spire's right flank; every rock, leaf and bud its own closed shell. Landmark. No VFX",
    MAIN_P: "Rock Spire (main mesh): tall 7-sided warm grey-pink obelisk, long flat faces, a 4-face pyramid cap, flat "
            "underside",
    SIDE_P: "Side Rock (reusable): tapered flat-topped faceted warm grey-pink block leaning a little, one lime star "
            "rosette on its top",
    FOOT_P: "Foot Rock (base, front): chunky wide faceted warm grey-pink dome with a broad flat top, a front nose "
            "vertex and a flat underside; two lime sprigs on its top",
    SMALL_P: "Small Rock (reusable): squat faceted warm grey-pink pebble, one flat top facet, flat underside",
    FOL_P: "Foliage Cluster (reusable): lime star rosette of seven broad oval leaves (an upright back leaf) round a "
           "round lime bud; every leaf and the bud its own closed piece",
}
COLLISION = {HERO: "none", MAIN_P: "hull", SIDE_P: "hull", FOOT_P: "hull", SMALL_P: "hull", FOL_P: "none"}


# ---- make / finish (no unions: closed shells) ----------------------------------------------------------------------------
OFFS = {}


def _recentre(o):
    bc = m012._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


def _tri_all(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = m012._tri_quads(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    return n


def _make(name, fn, role, budget):
    t0 = time.time()

    def wrapped(a):
        fn(a)
        xs, ys, zs = ([v.co[i] for v in a.bm.verts] for i in range(3))
        OFFS[name] = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    o = M.mk(SHEET, name, wrapped, subject=TITLE, role=role, notes=NOTES[name], budget=budget,
             collision=COLLISION[name], tint_var=0.0)
    o[OFF] = list(OFFS[name])
    o.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    lg = {"split": _tri_all(o)}
    if o.data.has_custom_normals:
        with M._override(o):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
    lg["forced"] = m012._force_slivers(o, lim=POLISH_LIM) if m012._thin(o, POLISH_LIM)["under"] else 0
    _recentre(o)
    for p in o.data.polygons:
        p.use_smooth = False
    M.smart_uv(o, **UV)
    lg["uv_cut"] = m012._uv_unfold(o)
    lg["bowties"] = M.fix_bowties(o)
    K.drop_unused_slots(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


# ---- render measurement (the study's masks, spec "Pixel boxes and masks") ---------------------------------------------
def classify(px, sheet=True, min_sat=0.03):
    """px: (h, w, 3) sRGB 0-1. Returns (class map: 1 rock, 2 green, 4 text/crevice; background mask). The study's
    cls(): R hue <= 45 or >= 190, sat .03-.42, v >= .30; G hue 45-150, sat >= .28, v >= .12; B (sheet only) neutral
    sat < .05, v .55-.955, or blue-grey B > R + 4 and G >= R; T v < .32, sat < .25."""
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    mx, mn = px.max(-1), px.min(-1)
    v = mx
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    d = mx - mn
    hue = np.zeros_like(mx)
    m = d > 1e-6
    rr = m & (mx == r)
    gg = m & (mx == g) & ~rr
    bb = m & ~rr & ~gg
    hue[rr] = (60 * ((g - b)[rr] / d[rr])) % 360
    hue[gg] = 60 * ((b - r)[gg] / d[gg]) + 120
    hue[bb] = 60 * ((r - g)[bb] / d[bb]) + 240
    G = (hue >= 45) & (hue <= 150) & (s >= 0.28) & (v >= 0.12)
    if sheet:
        B = ((s < 0.05) & (v >= 0.55) & (v <= 0.955)) | ((b > r + 4 / 255) & (g >= r) & (v >= 0.45) & (s < 0.25))
    else:
        B = np.zeros(mx.shape, bool)
    T = (v < 0.32) & (s < 0.25)
    R = ((hue <= 45) | (hue >= 190)) & (s >= min_sat) & (s <= 0.42) & (v >= 0.30) & ~G & ~B & ~T
    out = np.zeros(mx.shape, np.int8)
    out[R] = 1
    out[G] = 2
    out[T & ~G] = 4
    return out, B


def _hexmed(sel):
    return "#" + "".join(f"{int(x):02X}" for x in np.median(sel, axis=0)) if len(sel) else None


def measure(path, box=None, blank=(), bg=None, tol=12 / 255, min_sat=0.03):
    """Silhouette bbox, W:H, shares (rock / green of R + G), green by height fifths, 21-column top profile, width per
    height (h .05 .. .95), and class medians of a render (or a box of the sheet, ground shadow excluded)."""
    kit = K.NS["KIT"]
    px = np.clip(kit["load_px"](path)[::-1, :, :3], 0, 1)
    sheet = box is not None
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1].copy()
        for bx0, by0, bx1, by1 in blank:
            px[by0 - y0:by1 - y0, bx0 - x0:bx1 - x0] = np.array([251, 247, 239]) / 255
    if bg is None:
        bg = np.array([251, 247, 239]) / 255 if sheet else \
            np.median(np.concatenate([px[:4, :4].reshape(-1, 3), px[:4, -4:].reshape(-1, 3)]), axis=0)
    sil = np.abs(px - bg).max(-1) > tol
    cls, B = classify(px, sheet, min_sat)
    sil &= ~B
    ys, xs = np.nonzero(sil)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    H, W = y1 - y0 + 1, x1 - x0 + 1
    c = cls * sil
    rock, green = int((c == 1).sum()), int((c == 2).sum())
    tot = max(1, rock + green)
    prof = []
    for f in np.linspace(0, 1, 21):
        col = int(round(x0 + f * (W - 1)))
        on = np.nonzero(sil[:, col])[0]
        prof.append(round(float((y1 - on.min()) / (H - 1)), 2) if len(on) else 0.0)
    wph = []
    for h in np.linspace(0.05, 0.95, 10):
        row = int(round(y1 - h * (H - 1)))
        on = np.nonzero(sil[row])[0]
        wph.append(round(float((on.max() - on.min() + 1) / W), 2) if len(on) else 0.0)
    gy = np.nonzero(c == 2)[0]
    fifths = []
    for k in range(5):
        lo, hi = y1 - (k + 1) * H / 5, y1 - k * H / 5
        fifths.append(round(float(((gy > lo) & (gy <= hi)).sum() / max(1, len(gy))), 3))
    rgb = px * 255
    lum = rgb.mean(-1)
    rk = c == 1
    rl = rgb[rk]
    ll = lum[rk]
    out = {"wh": round(W / H, 3), "rock": round(rock / tot, 3), "green": round(green / tot, 3),
           "green_fifths": fifths, "profile": prof, "wph": wph,
           "rock_med": _hexmed(rl), "green_med": _hexmed(rgb[c == 2])}
    if len(ll):
        out["rock_lit"] = _hexmed(rl[ll >= np.percentile(ll, 75)])
        out["rock_shade"] = _hexmed(rl[ll <= np.percentile(ll, 25)])
    return out


SHEET_CELLS = {"f34_sheet": (100, 30, 565, 438), "r34_sheet": (565, 75, 955, 438),
               "front_sheet": (12, 515, 272, 720), "side_sheet": (276, 515, 511, 720),
               "rear_sheet": (516, 515, 762, 720), "top_sheet": (766, 515, 1012, 720)}
SHEET_BLANK = {"f34_sheet": ((100, 30, 300, 92), (300, 69, 330, 77), (420, 69, 565, 77))}
# per-part targets (spec 5.2 / 5.7)
PART_TARGETS = {"part_main": {"rock_med": "#C5A997"}, "part_siderock": {"rock_med": "#C7A997"},
                "part_footrock": {"rock_med": "#C7A997"}, "part_smallrock": {"rock_med": "#C4A999"},
                "part_foliage": {"green_med": "#769705"}, "parts": {"rock_med": "#C5A896", "green_med": "#769705"}}


def compare(names=None):
    """Our *_sheet renders against the sheet's cells: shares, W:H, profiles, width per height, green fifths, medians."""
    out = {}
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    keys = ("wh", "rock", "green", "green_fifths", "rock_med", "rock_lit", "rock_shade", "green_med")
    for k, box in SHEET_CELLS.items():
        if names and k not in names:
            continue
        try:
            s = measure(M.ref(NUM), box, SHEET_BLANK.get(k, ()))
            r = measure(f"{d}/{k}.png")
        except Exception as e:      # a render not made yet
            out[k] = str(e)
            continue
        pd = [abs(x - y) for x, y in zip(s["profile"], r["profile"])]
        wd = [abs(x - y) for x, y in zip(s["wph"], r["wph"])]
        out[k] = {"sheet": {x: s.get(x) for x in keys}, "ours": {x: r.get(x) for x in keys},
                  "profile_mean": round(sum(pd) / len(pd), 3), "profile_max": round(max(pd), 2),
                  "wph_mean": round(sum(wd) / len(wd), 3), "wph_max": round(max(wd), 2),
                  "profile_ours": r["profile"], "profile_sheet": s["profile"], "wph_ours": r["wph"],
                  "wph_sheet": s["wph"]}
    for k, tgt in PART_TARGETS.items():
        if names and k not in names:
            continue
        try:
            # the part shots stand on the studio floor: its grey shadow (sat < 0.1) is not rock
            r = measure(f"{d}/{k}.png", min_sat=0.10)
        except Exception as e:
            out[k] = str(e)
            continue
        out[k] = {"ours": {x: r.get(x) for x in ("rock", "green", "rock_med", "rock_lit", "green_med")},
                  "target": tgt}
    return out


# ---- build ------------------------------------------------------------------------------------------------------------------
PARTS = ((MAIN_P, spire_part), (SIDE_P, side_rock_part), (FOOT_P, foot_rock_part), (SMALL_P, small_rock_part),
         (FOL_P, foliage_part))
TARGET_SIZE = ((14.0, 0.6), (10.5, 0.8), (11.0, 0.3))
MAX_PEN = 0.6


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m039_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib",
                                                                                 "StoneSpire"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build(render=True, parts=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    LAYOUT.clear()
    PART_LOG.clear()
    PART_ROCKS.clear()
    CLUSTER_INFO.clear()
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn, "part", 1000)
        log["part_settle"] = dict(PART_LOG)
    CLUSTER_INFO.clear()
    h, log["hero"] = _make(HERO, hero, "hero", 4000)
    log["layout"] = {k: v for k, v in LAYOUT.items() if k != "rocks"}
    log["clusters"] = {k: dict(v) for k, v in CLUSTER_INFO.items()}
    _cleanup_tmp()
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    _spec()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    audits = [M.audit(o) for o in order]
    thin = {o.name: m012._thin(o, POLISH_LIM) for o in order}
    shells = {o.name: shells_report(o) for o in order}
    contact = {o.name: contact_report(o) for o in order}
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
        if thin[o.name]["under"]:
            problems.append(f"{o.name}: {thin[o.name]['under']} faces with a corner under {POLISH_LIM} deg")
        for i, s in enumerate(shells[o.name]):
            for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "self_hits", "inverted"):
                if s[k]:
                    problems.append(f"{o.name} shell {i} ({s['kind']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['kind']}): not closed outward (volume {s['volume']})")
        cr = contact[o.name]
        if cr["floating"] or cr["unchained"]:
            problems.append(f"{o.name}: {cr['floating']} floating shells, {cr['unchained']} unchained "
                            f"(worst gap {cr['worst_gap']})")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    for pair, g in LAYOUT.get("pen", {}).items():
        if g < -MAX_PEN:
            problems.append(f"rocks {pair} overlap by {-g} (> {MAX_PEN})")
    for key, (hexcol, _, _) in PALETTE.items():
        if key in ROCK_KEYS and not warm_ok(hexcol, 10.0, 30.0):
            problems.append(f"{key} {hexcol} fails the warm-stone guard")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 8: none)")
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95",
                                                                    "texels_per_stud_1024")}
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
                                         "ngons", "dup_verts", "transforms_applied", "custom_normals")}
                     for au in audits],
           "shells": kinds, "contact": contact, "thin": thin, "log": log, "problems": problems, "uv": uv,
           "rocks": LAYOUT.get("rocks"), "part_rocks": dict(PART_ROCKS),
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order)
        out["compare"] = compare()
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders -----------------------------------------------------------------------------------------------------------
# decision 9 / spec 3: f34_sheet (0, 20) and front_sheet (0, 18) govern; r34_sheet (-30, 20) is the sheet's "rear
# three-quarter" (a front-left view); side_sheet (90, 10), rear_sheet (180, 15) and top_sheet (0, 89) loosely.
# Floor hidden and a 3x lens on *_sheet shots (m033._long_lens).
SHEET_VIEWS = {"f34_sheet": (0, 20), "front_sheet": (0, 18), "r34_sheet": (-30, 20), "side_sheet": (90, 10),
               "rear_sheet": (180, 15), "top_sheet": (0, 89)}
PARTS_SHOT = (0, 25)


def _copy(tag, src, m, coll):
    c = bpy.data.objects.new(f"{PFX}{tag}", src.data)
    coll.objects.link(c)
    c.matrix_world = m
    return c


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded Construction: the spire raised in the middle, the side
    rock raised at the right, a pillar (the side rock scaled up) at the left, the foot rock low in front, small rocks
    round it, rosettes floating over the rock tops."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    o0 = Matrix.Translation((objs[0].location.x + 70, objs[0].location.y, 0))
    S = Matrix.Diagonal
    shown = [_copy("expl_spire", by[MAIN_P], o0 @ Matrix.Translation((0.0, 2.5, 4.5)), coll),
             _copy("expl_side", by[SIDE_P], o0 @ Matrix.Translation((5.2, 1.0, 3.6)) @ Matrix.Rotation(-0.25, 4, "Y"),
                   coll),
             _copy("expl_pillar", by[SIDE_P], o0 @ Matrix.Translation((-4.8, 1.2, 1.6)) @ S((1.3, 1.2, 1.15, 1)),
                   coll),
             _copy("expl_foot", by[FOOT_P], o0 @ Matrix.Translation((0.0, -3.5, 0.0)), coll),
             _copy("expl_small1", by[SMALL_P], o0 @ Matrix.Translation((-6.8, -2.0, 0.0)) @ S((1.4, 1.4, 1.4, 1)), coll),
             _copy("expl_small2", by[SMALL_P], o0 @ Matrix.Translation((6.6, -2.4, 0.0)) @ Matrix.Rotation(1.3, 4, "Z") @ S((1.4, 1.4, 1.4, 1)),
                   coll),
             _copy("expl_small3", by[SMALL_P], o0 @ Matrix.Translation((3.6, -6.6, 0.0)) @ Matrix.Rotation(2.2, 4, "Z")
                   @ S((1.2, 1.2, 1.2, 1)), coll)]
    for i, (x, y, z) in enumerate(((-5.0, 1.2, 12.0), (0.0, 2.0, 17.6), (5.6, 1.0, 11.0), (-6.8, -2.0, 3.4),
                                   (6.6, -2.4, 3.6), (2.6, -0.6, 6.6))):
        shown.append(_copy(f"expl_fol{i}", by[FOL_P], o0 @ Matrix.Translation((x, y, z)) @ Matrix.Rotation(i * 1.1, 4, "Z")
                           @ S((2.2, 2.2, 2.2, 1)), coll))
    bpy.context.view_layer.update()
    return shown


def _parts_row(objs):
    """The five parts in a row at one scale (the parts shot): rosette, spire, side rock, foot rock, small rock."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    x = objs[0].location.x + 140
    shown = []
    for n_ in (FOL_P, MAIN_P, SIDE_P, FOOT_P, SMALL_P):
        o = by[n_]
        w = o.dimensions.x
        shown.append(_copy("row_" + n_[10:], o, Matrix.Translation((x + w / 2, objs[0].location.y, 0)), coll))
        x += w + 1.6
    bpy.context.view_layer.update()
    return shown


def _scale_marker(h):
    """A 5.5-stud character stand-in (a plain column) beside the hero, for the scale shot."""
    a = K.fk().Asset(PFX + "char", "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=ROCK_DEEP, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=ROCK_DEEP, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=ROCK_DEEP, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    c.location = h.location + Vector((h.dimensions.x / 2 + 1.5, -2.0, 0))
    bpy.context.view_layer.update()
    return c


def render_views(objs, close=True):
    h = objs[0]
    by = {o.name: o for o in objs}
    shown = _exploded(objs) if FOL_P in by else []
    row = _parts_row(objs) if SMALL_P in by else []
    marker = _scale_marker(h)
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        for o in objs[1:]:
            extra["part_" + o.name.replace("StoneSpire", "").lower()] = ([o], *PARTS_SHOT)
        if row:
            extra["parts"] = (row, *PARTS_SHOT)
        if FOOT_P in by:
            extra["foot_under"] = ([by[FOOT_P]], 10, -35)
        if FOL_P in by:
            # fix round 1: the sheet draws its Foliage Clusters from well above (the bud ringed by leaves); compare
            # the rosette's star read here as well as in the e 25 parts shot
            extra["part_foliage_top"] = ([by[FOL_P]], 0, 55)
        if shown:
            extra["exploded"] = (shown, -8, 18)
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
            # Part close-up: Rock Spire: the cap and upper shaft from the front, low
            sx, sy = SPIRE_AT
            ground = bpy.data.objects.get("FB_Ground")
            gh = ground.hide_render if ground else None
            if ground:
                ground.hide_render = True        # the close-up floats in the air: no studio floor through it
            try:
                kit = K.NS["KIT"]
                rc = kit["render_group"]

                def no_floor(group, path, azimuth=-22, elevation=20):
                    if ground:
                        ground.hide_render = True
                    return rc(group, path, azimuth, elevation)
                kit["render_group"] = no_floor
                out["spire_cu"] = m033.render_close([h], f"{d}/spire_cu.png", 0, 10,
                                                    off @ Vector((sx + SPIRE["lean"][0], sy - 0.3, 9.9)), 1.4)
            finally:
                kit["render_group"] = rc
                if ground:
                    ground.hide_render = gh
            # Junction detail: C6 between F, S and Rr
            out["junc_cu"] = m033.render_close([h], f"{d}/junc_cu.png", 0, 12, off @ Vector((2.4, -0.9, 1.6)), 1.6)
        return out
    finally:
        for o in shown + row + [marker]:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if o is marker and me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def preview(names=("f34_sheet", "front_sheet"), vfx=False, extra=None, views=None, cell=(480, 400)):
    """Just the sheet comparison shots of the hero (fast tuning loop), then compare(). views overrides cameras."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    cams = dict(SHEET_VIEWS)
    cams.update(views or {})
    ex = {k: ([h], *cams[k]) for k in names}
    ex.update(extra or {})
    try:
        M.views(NUM, [h], names=(), extra=ex, vfx=vfx, cell=cell)
    finally:
        kit["render_group"] = orig
    return compare([n for n in names if n in SHEET_CELLS])


def hero_only():
    """Rebuild just the hero (tuning loop)."""
    M.coll(NUM, TITLE)
    palette()
    LAYOUT.clear()
    CLUSTER_INFO.clear()
    h, lg = _make(HERO, hero, "hero", 4000)
    _cleanup_tmp()
    _spec()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, _ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals")}, "log": lg,
            "layout": {k: v for k, v in LAYOUT.items() if k != "rocks"},
            "thin": m012._thin(h, POLISH_LIM), "contact": contact_report(h),
            "clusters": {k: {x: y for x, y in v.items() if x != "roots"} for k, v in CLUSTER_INFO.items()}}
