"""024 Thorn Shrub (references/024.png): a dense, round, spiky forage shrub. A thick warm-brown faceted skeleton (a
flared octagonal foot splitting low into eight kinked 7-sided limbs, two of them crossing in front of the foliage)
carries nine flattened fans of faceted pointed leaf gems (30 lobes, each a 6-sided spindle with a real apex pointing
out from the shrub's centre) and five fat pale-cream 5-sided thorns on the diagonals.

    import importlib, kit_models, m024; importlib.reload(kit_models); importlib.reload(m024); m024.build()

Parts as on the sheet's exploded view, each built by its own function (front -Y, +X right, ground z = 0, studs):
- ThornBushBranchCore: the exploded core (8-sided trunk, upper-left and upper-right limbs, a short centre stub with a
  pale cut top, a low left limb; flat 7-sided cut ends).
- ThornBushLeafCluster: the key part's 4-lobe fan (apex_lobes over lobe_mesh, as the hero's clusters).
- ThornBushThorn: one fat 5-sided pyramid with a flat base (thorn_mesh).
The hero (ThornBushNode) uses the same builders: skeleton() (the foot + eight limbs), eleven lobe clusters and five
thorns; united one shell at a time (guarded exact booleans), floor-cut at the ground. M024_spec.md holds the study,
the decisions and each stage's record.

Colour (stage 4) is painted by position fields inside the builders, before the union (the union and cleanup keep each
face's key and Tint): lobes cool base -> key -> light apex along each lobe's own axis, a key per cluster (crown light,
low lobes cool, a third olive by seed); thorns base -> tip; wood with darker crotches and hubs and broad blended
patches. Never by facing.
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise

import kit_mcp as K
import kit_models as M
import m004
import m011
import m012

NUM, TITLE, SHEET = 24, "Thorn Shrub", "M024"

LEAF, LEAF_LIGHT, LEAF_COOL, LEAF_OLIVE = "m024_leaf", "m024_leaf_light", "m024_leaf_cool", "m024_leaf_olive"
THORN, THORN_TIP, THORN_BASE = "m024_thorn", "m024_thorn_tip", "m024_thorn_base"
WOOD, WOOD_DARK, WOOD_CUT = "m024_wood", "m024_wood_dark", "m024_wood_cut"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# ---- palette (stage 4) -------------------------------------------------------------------------------------------------
# (hex, roughness, low_spec). Start = the spec's calibration targets (5.4); stage 4 writes the calibrated hexes.
PALETTE = {
    # pass 2 (the hero renders): with the dome hexes the f34 / front / rear / r34 medians read leaves #546F31
    # (sheet #62772E), thorns #CAAF8E (#E7C09A), wood #6B4D35 (#7A5538): the shrub's lobes shade each other and the
    # wood, so each family is corrected in linear light by the mean sheet / ours ratio over those four views
    # (leaves x(1.60, 1.31, 0.92) then x(0.94, 0.955, 1.0) on the residual, thorns x(1.46, 1.39, 1.29), wood x(1.59, 1.47, 1.30))
    # round 2 (verifier minors 4): the leaf keys were about 7 deg yellower than their targets (the parts read hue 73
    # against the sheet's 86), olive sat within 3 of leaf, the crown was dull and the low lobes light: leaf cooler,
    # light brighter and greener, cool darker, olive darker and duller (distinct from leaf by about 12 levels)
    # Calibration (round 2): pass 1 on the dome gave leaf #546C35, light #647F3D, cool #4A673F, olive #4C5C31;
    # pass 2 on the hero (mean sheet / ours over f34, front, rear, r34 in linear light) asked leaves x(1.65, 1.29,
    # 0.82): applied with the hue push at 0.6 strength (x(1.50, 1.29, 0.98)), because the full push made the parts
    # 16 deg yellower than the sheet's parts; light x(1.68, 1.45, 1.10) and cool x(1.35, 1.16, 0.89) for the sheet's
    # height bands (crown lighter, low lobes darker); then the light and leaf keys nudged 3-4 deg cooler for the parts
    LEAF: ("#647A36", 0.8, True),
    LEAF_LIGHT: ("#7C9C44", 0.8, True),
    LEAF_COOL: ("#4F6433", 0.8, True),
    LEAF_OLIVE: ("#5C6831", 0.8, True),
    # round 2 pass 2: thorns x(1.39, 1.33, 1.30) (between the f34 / front ratio and the four-view mean, which the
    # back-lit rear pulls up), the tip about 6 levels lower; wood x(1.60, 1.52, 1.40) (the hero view governs)
    THORN: ("#D6B798", 0.7, False),         # round 2 dome pass #B9A187
    THORN_TIP: ("#DDC0A7", 0.7, False),     # dome pass #C3AD98
    THORN_BASE: ("#CFAF8E", 0.7, False),    # dome pass #B39A7E
    WOOD: ("#8A6343", 0.9, False),          # dome pass #6F5138
    WOOD_DARK: ("#64482E", 0.9, False),     # dome pass #503A26
    WOOD_CUT: ("#C2AC99", 0.85, False),     # dome pass #9D8E83
}
# calibration targets: the sheet's rendered medians of unshadowed regions (M024_spec.md 5.4). key -> (sRGB, kind)
TARGETS = {LEAF: ((0x64, 0x7F, 0x36), "green"), LEAF_LIGHT: ((0x7A, 0x9A, 0x40), "green"),
           LEAF_COOL: ((0x56, 0x76, 0x40), "green"), LEAF_OLIVE: ((0x5A, 0x6A, 0x32), "green"),
           THORN: ((0xEA, 0xC3, 0x9B), "all"), THORN_TIP: ((0xF3, 0xD4, 0xB0), "all"),
           THORN_BASE: ((0xE2, 0xBA, 0x90), "all"), WOOD: ((0x8C, 0x63, 0x44), "brown"),
           WOOD_DARK: ((0x65, 0x48, 0x32), "brown"), WOOD_CUT: ((0xC9, 0xAF, 0x99), "all")}


def palette():
    for k, (hx, rough, low) in PALETTE.items():
        K.set_colour(k, hx, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hx, rough=rough, low_spec=low)
    _restyle()


THORN_SPEC = 0.25       # round 2: the default 0.5 washed the pale thorns out from above (top median #FFD9A5)


def _restyle():
    """Leaf keys (mix keys too) at the foliage specular; thorn keys at THORN_SPEC."""
    for m in bpy.data.materials:
        if not m.name.startswith(("FB_m024_leaf", "FB_m024_thorn")) or not m.node_tree:
            continue
        b = m.node_tree.nodes.get("Principled BSDF")
        if b and "Specular IOR Level" in b.inputs:
            b.inputs["Specular IOR Level"].default_value = (K.FOLIAGE_SPEC if m.name.startswith("FB_m024_leaf")
                                                            else THORN_SPEC)


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's test dome. Returns {key: (hex, rendered)}."""
    keys = keys or list(TARGETS)
    for k in keys:
        K.fk().material(k)
    try:
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


# ---- small geometry helpers ------------------------------------------------------------------------------------------
def _frame_from(d):
    d = Vector(d).normalized()
    u = d.orthogonal().normalized()
    v = d.cross(u).normalized()
    return u, v, d


def _cap(bm, ring, flip=False):
    vs = list(reversed(ring)) if flip else list(ring)
    f = bm.faces.new(vs)
    return bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="BEAUTY")["faces"]


def _seed(name):
    return 24000 + sum((i + 1) * ord(ch) for i, ch in enumerate(name))


def tube(a, pts, radii, seed, sides=7, jitter=0.06, twist=8.0, knuckle=1.08, mat=WOOD):
    """A faceted limb along the polyline pts (straight segments; each inner point is a kink with a knuckle ring
    swollen by `knuckle`), ring radii +-jitter and +-twist degrees per inner ring, flat end caps square to the first
    and last segments. Returns (verts, rings, bottom cap faces, top cap faces)."""
    rng = random.Random(seed)
    bm = a.bm
    rings = []
    u0, _, _ = _frame_from(pts[1] - pts[0])
    ph = rng.uniform(0, 2 * math.pi)
    for i, p in enumerate(pts):
        if i == 0:
            d = pts[1] - pts[0]
        elif i == len(pts) - 1:
            d = pts[-1] - pts[-2]
        else:
            d = (pts[i + 1] - pts[i]).normalized() + (pts[i] - pts[i - 1]).normalized()
        d = d.normalized()
        u = (u0 - d * u0.dot(d)).normalized()
        v = d.cross(u).normalized()
        u0 = u
        inner = 0 < i < len(pts) - 1
        tw = ph + (math.radians(rng.uniform(-twist, twist)) if inner else 0.0)
        kn = knuckle if inner else 1.0
        ring = []
        for k in range(sides):
            t = tw + 2 * math.pi * k / sides
            r = radii[i] * kn * (1 + rng.uniform(-jitter, jitter) if inner else 1 + rng.uniform(-0.03, 0.03))
            ring.append(bm.verts.new(p + (u * math.cos(t) + v * math.sin(t)) * r))
        rings.append(ring)
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            faces.append(bm.faces.new((r0[k], r0[j], r1[j], r1[k])))
    bot = _cap(bm, rings[0], flip=True)
    top = _cap(bm, rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=faces + bot + top)
    vs = [v for r in rings for v in r]
    a._finish(vs, mat, tint=1.0)
    return vs, rings, bot, top


def frustum(a, p0, p1, r0, r1, seed, mat, sides=6):
    """A sides-gon frustum from p0 (radius r0) to p1 (radius r1). Returns verts."""
    rng = random.Random(seed)
    p0, p1 = Vector(p0), Vector(p1)
    u, v, d = _frame_from(p1 - p0)
    ph = rng.uniform(0, 2 * math.pi)
    bm = a.bm
    rings = []
    for c, r in ((p0, r0), (p1, r1)):
        rings.append([bm.verts.new(c + (u * math.cos(ph + 2 * math.pi * k / sides) +
                                        v * math.sin(ph + 2 * math.pi * k / sides)) * r * (1 + rng.uniform(-0.04, 0.04)))
                      for k in range(sides)])
    faces = [bm.faces.new((rings[0][k], rings[0][(k + 1) % sides], rings[1][(k + 1) % sides], rings[1][k]))
             for k in range(sides)]
    faces += _cap(bm, rings[0], flip=True) + _cap(bm, rings[1])
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    vs = rings[0] + rings[1]
    a._finish(vs, mat, tint=1.0)
    return vs


# ---- lobe (the unit) ----------------------------------------------------------------------------------------------------
# A 6-sided pointed gem (spec 1.4): bottom apex at t 0, ring A (t, radius / D, ring phase) at 0.28, girdle B rotated 30
# deg at 0.50, crown ring C rotated 30 deg again at 0.74, top apex at t 1 offset sideways. 36 tris.
# round 3: the spec's spacing (A .28 / B .50 / C .74 at .42 / .50 / .36 D) rendered as icosphere balls from every
# side: the crown ring now hugs the girdle (a narrow bevel band) so the apex is a long straight 6-sided pyramid, the
# long point the sheet's lobes show (z_f34_top)
GEM = ((0.22, 0.40, 0.0), (0.45, 0.50, 30.0), (0.57, 0.44, 60.0))
GEM_JIT = dict(r=0.08, twist=10.0, apex=0.06)
INFO = {}


# round 2: the exported Leaf Cluster part read as flat ivy leaves with long sharp tips; the key part's lobes are fat
# faceted gems with short points: a wider bottom ring and the crown ring further up (a short, blunt pyramid)
GEM_FAT = ((0.2, 0.42, 0.0), (0.42, 0.5, 30.0), (0.64, 0.42, 60.0))


def lobe_mesh(a, base, axis, D, L, seed, flat=None, gem=GEM):
    """One leaf lobe: the 6-sided pointed gem from base (its bottom apex) along axis, girdle diameter D, length L.
    flat = (direction, factor): squash the lobe across its axis along direction by factor (a flattened fan).
    Returns (verts, {vert: t})."""
    rng = random.Random(seed)
    bm = a.bm
    d = Vector(axis).normalized()
    u, v, _ = _frame_from(d)
    ph = rng.uniform(0, 2 * math.pi)
    B = Vector(base)
    tm = {}
    bot = bm.verts.new(B)
    tm[bot] = 0.0
    rings = []
    for t, rf, off in gem:
        tw = ph + math.radians(off + rng.uniform(-GEM_JIT["twist"], GEM_JIT["twist"]))
        ring = []
        for k in range(6):
            ang = tw + 2 * math.pi * k / 6
            r = rf * D * (1 + rng.uniform(-GEM_JIT["r"], GEM_JIT["r"]))
            x = bm.verts.new(B + d * (t * L) + (u * math.cos(ang) + v * math.sin(ang)) * r)
            tm[x] = t
            ring.append(x)
        rings.append(ring)
    sa = rng.uniform(0, 2 * math.pi)
    top = bm.verts.new(B + d * L + (u * math.cos(sa) + v * math.sin(sa)) * GEM_JIT["apex"] * D)
    tm[top] = 1.0
    fs = []
    r0, r1, r2 = rings
    for k in range(6):
        j = (k + 1) % 6
        fs.append(bm.faces.new((bot, r0[j], r0[k])))
        fs.append(bm.faces.new((r0[k], r0[j], r1[k])))
        fs.append(bm.faces.new((r1[k], r0[j], r1[j])))
        fs.append(bm.faces.new((r1[k], r1[j], r2[k])))
        fs.append(bm.faces.new((r2[k], r1[j], r2[j])))
        fs.append(bm.faces.new((r2[k], r2[j], top)))
    vs = [bot] + r0 + r1 + r2 + [top]
    if flat:
        fd, fk = flat
        fd = Vector(fd)
        fd = (fd - d * fd.dot(d))
        if fd.length > 1e-4:
            fd.normalize()
            for x in vs:
                rel = x.co - B
                x.co = B + rel - fd * (rel.dot(fd) * (1 - fk))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    a._finish(vs, LEAF, tint=1.0)
    INFO.setdefault("lobe_inverted", []).append(_inverted_piece(vs))
    return vs, tm


# ---- thorn --------------------------------------------------------------------------------------------------------------
THORN_RINGS = (0.25, 0.5, 0.75)     # coplanar colour rings along the straight flanks (the outline stays a pyramid)


def thorn_mesh(a, base, tip, dia, seed, sink=0.15):
    """A straight 5-sided pyramid with a flat pentagonal base: base radius +-6 %, the base sunk `sink` behind
    `base` along the axis. Colour rings at THORN_RINGS sit on the straight flanks. Returns (verts, {vert: t},
    base cap faces)."""
    rng = random.Random(seed)
    bm = a.bm
    B, T = Vector(base), Vector(tip)
    d = (T - B).normalized()
    B = B - d * sink
    L = (T - B).length
    u, v, _ = _frame_from(d)
    ph = rng.uniform(0, 2 * math.pi)
    rad = [dia / 2 * (1 + rng.uniform(-0.06, 0.06)) for _ in range(5)]
    angs = [ph + 2 * math.pi * (k + rng.uniform(-0.06, 0.06)) / 5 for k in range(5)]
    base_pts = [B + (u * math.cos(t) + v * math.sin(t)) * r for t, r in zip(angs, rad)]
    tm = {}
    rings = []
    for t in (0.0,) + THORN_RINGS:
        ring = []
        for p in base_pts:
            x = bm.verts.new(p.lerp(T, t))
            tm[x] = t
            ring.append(x)
        rings.append(ring)
    tipv = bm.verts.new(T)
    tm[tipv] = 1.0
    fs = []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(5):
            j = (k + 1) % 5
            fs.append(bm.faces.new((r0[k], r0[j], r1[j], r1[k])))
    for k in range(5):
        fs.append(bm.faces.new((rings[-1][k], rings[-1][(k + 1) % 5], tipv)))
    quads = [f for f in fs if len(f.verts) == 4]
    bmesh.ops.triangulate(bm, faces=quads, quad_method="SHORT_EDGE")
    cap = _cap(bm, rings[0], flip=True)
    vs = [x for r in rings for x in r] + [tipv]
    bmesh.ops.recalc_face_normals(bm, faces=K.faces_of(vs))
    a._finish(vs, THORN, tint=1.0)
    return vs, tm, cap


# ---- hero skeleton (spec 2.1) -------------------------------------------------------------------------------------------
# Verification round 2 (B1): the skeleton read as a low splayed "nest". The trunk is now a visible column (radius
# about 0.45) up to z 1.0-1.2 and the main limbs leave it there: the front-left limb as a steep rising S, the
# front-right rising and then running level, the two back limbs straight at about 45 deg to TA's and TC's bases (the
# rear Y). The low limbs are short single segments rising 30 deg, tucked behind their lobes. The old level K7 and
# BK spokes are gone; two short back root stubs (BK, BKL) rising about 30 deg carry the low back clusters K12 and K7
# (hub sticks off the trunk showed as green bars from behind) and give the rear its low wood (sheet h .15 .26-.65).
TRUNK = (((0.0, 0.0, -0.12), (0.0, 0.0, 0.12), (0.04, -0.03, 0.55), (0.1, -0.05, 0.95), (0.14, -0.03, 1.22)),
         (0.58, 0.52, 0.49, 0.47, 0.42))
# name: (polyline from inside the trunk -> kinks -> flat end, radius start, radius end)
LIMBS = {
    "FL": (((-0.05, -0.25, 0.82), (-0.95, -0.65, 1.25), (-1.1, -0.75, 1.6), (-0.9, -0.7, 2.05)), 0.38, 0.28),
    "FR": (((0.15, -0.2, 0.95), (0.55, -0.85, 1.55), (1.15, -0.9, 1.8), (1.85, -0.6, 2.15)), 0.37, 0.26),
    "C": (((0.1, 0.0, 1.0), (0.05, 0.05, 1.6), (0.0, 0.15, 2.3)), 0.26, 0.21),
    "BR": (((0.2, 0.25, 0.95), (1.15, 0.6, 1.45), (1.55, 0.9, 2.25)), 0.45, 0.33),
    "BL": (((-0.05, 0.2, 1.05), (-0.6, 0.6, 1.6), (-1.05, 0.85, 2.3)), 0.45, 0.33),
    "LL": (((-0.1, 0.0, 0.6), (-0.75, -0.15, 0.95)), 0.27, 0.23),
    "RL": (((0.12, -0.1, 0.6), (0.7, -0.5, 0.95)), 0.27, 0.23),
    # a short back stub rising 30 deg toward +X (the rear cell's low wood at f .26-.35, h .1-.2), carrying K12
    "BK": (((0.08, 0.08, 0.25), (0.95, 0.65, 0.8)), 0.32, 0.26),
    "BKL": (((0.0, 0.08, 0.4), (-0.95, 0.6, 0.95)), 0.32, 0.27),
}


def limb_points(name, table=None):
    pts, r0, r1 = (table or LIMBS)[name]
    pts = [Vector(p) for p in pts]
    acc = [0.0]
    for p, q in zip(pts, pts[1:]):
        acc.append(acc[-1] + (q - p).length)
    rad = [r0 + (r1 - r0) * s / acc[-1] for s in acc]
    return pts, rad


def skeleton(a, limbs=None, table=None, trunk=TRUNK):
    """The foot (an 8-sided flared trunk) and the limbs (7-sided kinked tubes). Returns {name: (verts, caps)} with
    caps the limb's end-cap faces (its flat joining surface)."""
    out = {}
    pts, rad = trunk
    vs, _, bot, top = tube(a, [Vector(p) for p in pts], list(rad), _seed("trunk"), sides=8, jitter=0.05,
                           knuckle=1.0)
    out["trunk"] = (vs, [])
    for name in (limbs or (table or LIMBS)):
        pts, rad = limb_points(name, table)
        vs, _, bot, top = tube(a, pts, rad, _seed(name), sides=7, jitter=0.06, twist=8.0)
        out[name] = (vs, top)
    return out


# ---- hero clusters (spec 2.2) and thorns (2.3) ---------------------------------------------------------------------------
# Stage 1 round 2: the first layout (every lobe's bottom apex on the hub, axes from the spec's az / el table) read as
# nine separate balls with paper between them. Round 3: each lobe is placed by its APEX, read off the sheet's views
# (f34 for the front half, the rear cell for the back half, the top for the ring), and runs from just outside its
# cluster's hub to that apex, so the lobes radiate as a star of points that fills the dome like the sheet's.
# name: (hub, host limb, lobes [(apex (x, y, z), girdle D)], lobe key tier)
# Verification round 2 (B2): the hero was too narrow (f34 W : H 1.23 against 1.356). The right (K5, K6) and left
# (K3, K4) edge lobes now reach X +-2.4 at z 1.0-2.2; the upper-left lobes stay below z 2.7; K10 (in front of the
# trunk foot) is gone; K7 and K12 sit on the short rising back stubs; the back Y arms run clear of the lobes.
CLUSTERS = {
    "K1": ((0.05, 0.15, 2.3), "C", [((0.05, 0.15, 3.5), 0.8), ((-0.8, -0.3, 3.2), 0.95), ((0.7, -0.3, 3.2), 0.9),
                                    ((-0.1, 1.25, 2.85), 1.05), ((-0.65, -1.05, 2.75), 0.9)], "light"),
    "K2": ((-0.15, -0.3, 1.95), "C", [((-0.2, -1.7, 1.85), 1.3), ((0.7, -1.35, 3.0), 1.0),
                                     ((-0.05, -1.25, 1.0), 0.6)], "mid"),
    "K3": ((-1.05, -0.45, 2.15), "FL", [((-1.7, -0.6, 2.5), 0.8), ((-2.4, -0.4, 1.75), 1.05),
                                      ((-1.95, 0.2, 2.4), 0.95),
                                      ((-1.3, -1.0, 2.5), 0.85)], "mid"),
    "K4": ((-1.2, -0.3, 0.95), "LL", [((-2.42, -0.5, 0.8), 1.1), ((-1.5, -1.4, 0.35), 1.0),
                                      ((-2.25, 0.45, 1.25), 1.0), ((-0.75, -1.35, 0.45), 0.8)], "low"),
    "K5": ((1.5, -0.4, 2.1), "FR", [((2.38, -0.25, 1.95), 0.9), ((2.42, -0.15, 1.35), 1.0),
                                     ((1.35, -1.1, 2.45), 0.85)], "mid"),
    "K6": ((1.05, -0.75, 0.95), "RL", [((1.2, -1.85, 0.95), 1.05), ((0.85, -1.45, 0.35), 0.8),
                                       ((2.42, -0.7, 0.85), 0.9)], "low"),
    "K12": ((0.95, 0.65, 0.8), "BK", [((2.15, 1.2, 0.4), 0.9), ((2.3, 0.6, 1.05), 0.85), ((0.6, 1.65, 1.35), 0.65)],
            "low"),
    "K7": ((-0.95, 0.6, 0.95), "BKL", [((-1.95, 1.35, 0.4), 0.9), ((-2.2, 0.75, 0.95), 0.85)], "low"),
    "K8": ((-0.95, 0.7, 2.15), "BL", [((-0.7, 1.3, 2.75), 0.95), ((-2.35, 0.75, 2.05), 1.05),
                                      ((-1.85, 1.45, 1.6), 1.0)], "mid"),
    "K9": ((1.35, 0.7, 2.2), "BR", [((0.55, 1.15, 3.2), 0.95), ((2.3, 0.6, 1.95), 1.0)], "mid"),
    # round 4: the rear cell's big centre lobe sits inside the +X arm (f .25-.45), on its own hub off the C limb
    "K11": ((0.35, 0.5, 1.85), "C", [((0.85, 1.8, 2.15), 0.95)], "mid"),
}
LOBE_OFF = 0.1          # each lobe's bottom apex this far out from its hub toward its apex
LOBE_LD = 1.15          # round 4: girdle at most L / 1.15, so a lobe seen side-on always shows its point
LOBE_GROW = 1.10        # round 3: every girdle wider (1.15; 1.10 from round 4, when the f34 leaf share ran 6 points high)
HUB_R = (0.22, 0.17)
HUB_PAST = 0.22
# name: (base, tip, base diameter). Round 3: the bases moved out onto the limb surfaces so the fat base shows (TB read
# as a sliver with its base buried in K3's lobes)
# Round 2: TA toward NE, TC steeper (rear tip higher), TB less level, TD more forward, T5 smaller on the trunk's back
THORNS = {
    "TA": ((1.5, 0.95, 2.3), (2.15, 1.7, 3.2), 1.15),
    "TB": ((-1.35, -0.85, 1.95), (-2.15, -1.5, 2.75), 1.15),
    "TC": ((-1.0, 0.9, 2.3), (-1.6, 1.75, 3.0), 1.1),
    "TD": ((1.2, -1.0, 0.95), (2.05, -1.95, 0.45), 1.1),
    "T5": ((-0.4, 0.42, 1.2), (-0.95, 0.75, 1.2), 0.4),
}


def _host_pts(host, table=None):
    if host == "trunk":
        return [Vector(p) for p in TRUNK[0]], list(TRUNK[1])
    return limb_points(host, table)


def _nearest_on(pts, p):
    best = None
    for q0, q1 in zip(pts, pts[1:]):
        dd = q1 - q0
        t = max(0.0, min(1.0, (p - q0).dot(dd) / max(dd.length_squared, 1e-12)))
        c = q0 + dd * t
        if best is None or (c - p).length < (best - p).length:
            best = c
    return best


def _hub(a, name, hub, host, table=None):
    """A hidden 6-sided hub joining the host limb (its nearest axis point, or 0.2 inside its end) to the lobes'
    meeting point."""
    pts, rad = _host_pts(host, table)
    H = Vector(hub)
    p0 = _nearest_on(pts, H)
    if (p0 - pts[-1]).length < 1e-4:
        p0 = pts[-1] - (pts[-1] - pts[-2]).normalized() * 0.2
    dl = (pts[-1] - pts[-2]).normalized()
    if (H - pts[-1]).length < 0.08:
        # a hub on the limb end would put its cap in the end cap's plane: coplanar faces the exact union leaves
        # unjoined (round 4: K7 and K12 came out as loose shells)
        H = pts[-1] + dl * 0.15
    if (H - p0).length < 0.15:
        H = p0 + dl * 0.25
    # round 5: run the hub on past the lobes' meeting point, so every lobe's bottom apex (LOBE_OFF out from it)
    # sits inside the hub (a single-lobe cluster, K10, otherwise only touched it and fell off in the union)
    H = H + (H - p0).normalized() * HUB_PAST
    return frustum(a, p0, H, min(HUB_R[0], rad[-1] * 0.95), HUB_R[1], _seed("hub" + name), LEAF_COOL)


def apex_lobes(a, hub, lobes, seed, off=LOBE_OFF, gem=GEM, ld=None, grow=None):
    """A cluster's lobes placed by their apexes: each runs from `off` out of the hub to its apex (L = that
    distance). Returns [(verts, tm, axis)]."""
    ld = ld or LOBE_LD
    grow = grow or LOBE_GROW
    out = []
    H = Vector(hub)
    for i, (apex, D) in enumerate(lobes):
        P = Vector(apex)
        d = (P - H).normalized()
        B = H + d * off
        L = (P - B).length
        vs, tm = lobe_mesh(a, B, d, min(D * grow, L / ld), L, seed + 7 * i, gem=gem)
        out.append((vs, tm, d))
    return out


def hero(a):
    """ThornBushNode: skeleton (foot + nine limbs and stubs), eleven lobe clusters (33 lobes), five thorns (spec 2)."""
    INFO.clear()
    sk = skeleton(a)
    lobes, hubs = [], []
    for name, (hub, host, ls, tier) in CLUSTERS.items():
        hubs.append(_hub(a, name, hub, host))
        for i, (vs, tm, d) in enumerate(apex_lobes(a, hub, ls, _seed(name))):
            lobes.append((name, i, vs, tm, d, tier))
    thorns = {}
    for name, (b, t, dia) in THORNS.items():
        thorns[name] = thorn_mesh(a, b, t, dia, _seed(name))
    paint_hero(a, sk, lobes, hubs, thorns)


# ---- parts --------------------------------------------------------------------------------------------------------------
# the exploded core (spec 1.4): about 1.85 W x 0.9 D x 1.65 H; trunk Ø 0.85 splitting at 0.45 H; limbs Ø 0.40-0.45
CORE_TRUNK = (((0.0, 0.0, -0.05), (0.0, 0.0, 0.12), (0.0, 0.0, 0.55), (0.03, 0.0, 0.85)), (0.50, 0.44, 0.42, 0.36))
CORE = {
    "UL": (((-0.05, 0.0, 0.6), (-0.4, 0.0, 1.0), (-0.78, 0.0, 1.5)), 0.23, 0.2),
    "UR": (((0.05, 0.0, 0.62), (0.4, 0.0, 1.05), (0.62, 0.0, 1.5)), 0.23, 0.21),
    "CS": (((0.02, 0.0, 0.7), (0.02, 0.0, 1.0), (0.05, 0.0, 1.3)), 0.2, 0.19),
    "LO": (((-0.1, 0.0, 0.45), (-0.6, 0.0, 0.55), (-1.05, 0.0, 0.62)), 0.22, 0.2),
}


def core_part(a):
    """ThornBushBranchCore: the exploded 4-limb core with flat cut ends."""
    sk = skeleton(a, table=CORE, trunk=CORE_TRUNK)
    paint_core(a, sk)


# the key part's fan (spec 1.4): two big front lobes up-left and up-right, a taller one behind pointing up, a smaller
# one behind at the left; H/W 0.85, depth 0.55 W
# round 5: the key part's fan by its apexes, built exactly like the hero's clusters (apex_lobes): two big front lobes
# up-left and up-right, a taller one behind pointing up, a small one behind at the left. (The first two tries, lobes
# from az / el with their bottoms on the hub, rendered a squat 1.4-stud blob, then a box with flat sides: the lobes
# overlapped almost whole.)
PART_HUB = (0.0, 0.0, 0.12)
PART_CLUSTER = [((-0.9, -0.25, 1.2), 0.95), ((0.95, -0.2, 1.15), 0.95), ((0.1, 0.3, 1.6), 0.9),
                ((-0.55, 0.45, 1.35), 0.7)]


def cluster_part(a):
    """ThornBushLeafCluster: the key part's 4-lobe fan on its hub (fan plane facing -Y)."""
    res = apex_lobes(a, PART_HUB, PART_CLUSTER, _seed("part_cluster"), gem=GEM_FAT, ld=0.95, grow=1.2)
    hv = frustum(a, (0, 0, 0.0), (0, 0, PART_HUB[2] + 0.12), 0.2, 0.17, _seed("part_hub"), LEAF_COOL)
    for i, (vs, tm, d) in enumerate(res):
        # round 2: the part's unshaded lobes rendered #799238 (hue 77) against the key part's #688A3B (hue 86); the
        # hero's leaf key can't move that far (its f34 median must stay hue 74-82), so the part's lobes start from
        # a 50 % leaf / cool mix
        base = K.mix_key(LEAF, LEAF_COOL, 0.5) if i != 3 else LEAF_OLIVE
        paint_lobe(a, vs, tm, base, _seed("part_cluster") + 3 * i, soft=True)
    _paint_flat(a, hv, LEAF_COOL, "leaf", _seed("part_hub"))


def thorn_part(a):
    """ThornBushThorn: L 1.7, base Ø 0.95, 5 sides, flat base, pointing up."""
    vs, tm, cap = thorn_mesh(a, (0, 0, 0.15), (0.0, 0.0, 1.9), 1.1, _seed("part_thorn"))   # the hero thorns' size
    paint_thorn(a, vs, tm, cap, _seed("part_thorn") + 1)


# ---- stage 4: colour by position fields (never facing) ---------------------------------------------------------------
LOBE_BANDS = ((0.30, 0.5), (0.42, 0.25), (0.70, 0.0), (0.78, 0.25))   # (t below, cool mix) ... then light mixes
LOBE_NOISE = 0.08
MOTTLE = {"leaf": dict(amp=0.035, scale=0.5, jitter=0.004), "thorn": dict(amp=0.02, scale=0.6, jitter=0.003),
          "wood": dict(amp=0.05, scale=0.35, jitter=0.005)}
PIECE_TINT = 0.04
OLIVE_EVERY = 3
# round 2: about 73 % of the wood faces were dark mixes; dark now only at the split crotch and right under hubs, with
# sparse broad patches (a higher noise level)
WOOD_FIELD = dict(crotch=(0.12, -0.03, 1.12), crotch_r=(0.35, 0.55), hub_r=(0.22, 0.38), mix=0.5, patch_scale=0.6,
                  patch_level=0.42, patch_mix=0.25, ramp=0.06)


def _mottle(a, faces, level, kind, seed):
    m = MOTTLE[kind]
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in faces:
        c = f.calc_center_median()
        k = level * (1.0 + m["amp"] * 1.6 * noise.noise(c * m["scale"] + off) + rng.uniform(-m["jitter"], m["jitter"]))
        for lo in f.loops:
            lo[a.tint_layer] = (k, k, k, 1.0)


def _paint_flat(a, vs, key, kind, seed):
    fs = K.faces_of(vs)
    for f in fs:
        f.material_index = a._mi(key)
    _mottle(a, fs, 1.0, kind, seed)


def lobe_key(base, t):
    """A lobe face's key from its position t along the lobe (0 hub end .. 1 apex): toward cool by 50 / 25 % over the
    base, the lobe's own key across the middle, toward light by 25 / 50 % over the apex."""
    if t < 0.30:
        return K.mix_key(base, LEAF_COOL, 0.5) if base != LEAF_COOL else LEAF_COOL
    if t < 0.42:
        return K.mix_key(base, LEAF_COOL, 0.25) if base != LEAF_COOL else LEAF_COOL
    if t < 0.70:
        return base
    if t < 0.78:
        return K.mix_key(base, LEAF_LIGHT, 0.25) if base != LEAF_LIGHT else LEAF_LIGHT
    return K.mix_key(base, LEAF_LIGHT, 0.5) if base != LEAF_LIGHT else LEAF_LIGHT


def lobe_key_soft(base, t):
    """The part's fat upright lobes: only 25 % mixes at the hub end and the tip (the full ramp followed the face
    direction on the upright fan, K.check corr 0.59)."""
    if t < 0.22:
        return K.mix_key(base, LEAF_COOL, 0.25) if base != LEAF_COOL else LEAF_COOL
    if t > 0.82:
        return K.mix_key(base, LEAF_LIGHT, 0.25) if base != LEAF_LIGHT else LEAF_LIGHT
    return base


def paint_lobe(a, vs, tm, base, seed, soft=False):
    rng = random.Random(seed)
    nf = K.noise_field(scale=0.9, seed=seed)
    fs = K.faces_of(vs)
    for f in fs:
        c = f.calc_center_median()
        t = sum(tm[v] for v in f.verts) / len(f.verts) + LOBE_NOISE * 1.6 * nf(c)
        f.material_index = a._mi((lobe_key_soft if soft else lobe_key)(base, t))
    _mottle(a, fs, 1.0 + rng.uniform(-PIECE_TINT, PIECE_TINT), "leaf", seed + 1)


def _lobe_base(name, i, d, tier, k):
    # round 2: the crown read dull and the base light (f34 bands bottom +17, top -9 against the sheet): every
    # upward crown lobe takes the light key, every lobe of a low cluster the cool key
    if tier == "light":
        return LEAF_LIGHT if i == 0 or d.z > 0.5 else LEAF
    if tier == "low":
        return LEAF_COOL
    return LEAF_OLIVE if k % OLIVE_EVERY == 1 else LEAF


def thorn_key(t):
    if t < 0.25:
        return THORN_BASE
    if t < 0.5:
        return K.mix_key(THORN_BASE, THORN, 0.5)
    if t < 0.75:
        return THORN
    return K.mix_key(THORN, THORN_TIP, 0.75)


def paint_thorn(a, vs, tm, cap, seed, shift=0.0):
    rng = random.Random(seed)
    fs = K.faces_of(vs)
    for f in fs:
        t = sum(tm[v] for v in f.verts) / len(f.verts) - shift
        f.material_index = a._mi(thorn_key(t))
    for f in cap:
        f.material_index = a._mi(THORN_BASE)
    _mottle(a, fs, 1.0 + rng.uniform(-PIECE_TINT * 0.5, PIECE_TINT * 0.5), "thorn", seed + 1)


def _ramp(n, F):
    """The patch mix for noise n: patch_mix inside, then 50 % / 25 % of it across the edge (m020's _patch)."""
    lv = F["patch_level"]
    if n > lv + F["ramp"]:
        return F["patch_mix"]
    if n > lv:
        return F["patch_mix"] * 0.5
    if n > lv - F["ramp"]:
        return F["patch_mix"] * 0.25
    return 0.0


def _near(d, r):
    """1 inside r[0], 0.5 to r[1], else 0 (the dark crotch fade, in two steps)."""
    return 1.0 if d < r[0] else 0.5 if d < r[1] else 0.0


def _q4(t):
    return round(max(0.0, min(1.0, t)) * 4) / 4


def paint_wood(a, vs, caps, seed, hubs=(), crotch=True, crotch_at=None, crotch_r=None, base_mix=0.0):
    W = WOOD_FIELD
    pf = K.noise_field(scale=W["patch_scale"], seed=24090)
    cr = Vector(crotch_at or W["crotch"])
    capset = set(caps)
    fs = K.faces_of(vs)
    for f in fs:
        if f in capset:
            f.material_index = a._mi(WOOD_CUT)
            continue
        c = f.calc_center_median()
        t = base_mix
        if crotch:
            t = max(t, W["mix"] * _near((c - cr).length, crotch_r or W["crotch_r"]))
        for h in hubs:
            t = max(t, W["mix"] * _near((c - h).length, W["hub_r"]))
        t = max(t, _ramp(pf(c), W))
        f.material_index = a._mi(K.mix_key(WOOD, WOOD_DARK, _q4(t)))
    _mottle(a, [f for f in fs if f not in capset], 1.0, "wood", seed)


def paint_hero(a, sk, lobes, hubs, thorns):
    hub_pts = [Vector(h[0]) for h in CLUSTERS.values()]
    for name, (vs, caps) in sk.items():
        paint_wood(a, vs, caps, _seed(name) + 9, hubs=hub_pts)
    for k, (name, i, vs, tm, ae, tier) in enumerate(lobes):
        paint_lobe(a, vs, tm, _lobe_base(name, i, ae, tier, k), _seed(name) + 5 + 11 * i)
    for hv in hubs:
        _paint_flat(a, hv, LEAF_COOL, "leaf", 24500 + len(hv))
    for name, (vs, tm, cap) in thorns.items():
        paint_thorn(a, vs, tm, cap, _seed(name) + 1, shift=0.1 if name == "T5" else 0.0)


def paint_core(a, sk):
    for name, (vs, caps) in sk.items():
        # round 2: the core part is rendered unshaded, and with the hero's wood keys it read 20+ levels light against
        # the key and exploded cores (#A06E48 / #8B6143): a 25 % dark mix as its base, 50 % in the crotch
        paint_wood(a, vs, caps, _seed("core" + name), crotch_at=(0.0, 0.0, 0.72), crotch_r=(0.2, 0.32),
                   base_mix=0.25)


# ---- checks on pieces ----------------------------------------------------------------------------------------------------
def _inverted_piece(vs):
    """Faces of one closed piece whose normal points into the piece (ray parity). Must be 0."""
    from mathutils.bvhtree import BVHTree
    fs = K.faces_of(vs)
    idx = {v: i for i, v in enumerate(vs)}
    for f in fs:
        f.normal_update()
    t = BVHTree.FromPolygons([v.co.copy() for v in vs], [[idx[v] for v in f.verts] for f in fs])
    bad = 0
    for f in fs:
        n = f.normal.normalized()
        o = f.calc_center_median() + n * 1e-4
        hits = 0
        while hits < 50:
            loc = t.ray_cast(o, n)[0]
            if loc is None:
                break
            hits += 1
            o = loc + n * 1e-5
        bad += hits % 2
    return bad


# ---- cleanup (M018 / M022's guarded procedure, copied: the other builders change in parallel) ------------------------
def _volume(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    v = bm.calc_volume(signed=True)
    bm.free()
    return v


UNION_MERGE = 0.0005


def _union(o, tries=5):
    """Guarded union: each shell is unioned on with an exact boolean, one at a time, the result checked against the
    volumes going in; a bad result is undone and the shell retried nudged a few thousandths of a stud; a shell that
    still fails is reported and left out. Returns {"shells", "retried", "failed"}."""
    act = bpy.context.view_layer.objects.active
    if act and act.mode != "OBJECT":
        with bpy.context.temp_override(active_object=act, object=act):
            bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()
    others = M.split_loose(o)
    retried, failed = [], []
    rng = random.Random(24900)
    queue = [(i, p, False) for i, p in enumerate(others)]
    deferred = []
    while queue:
        i, p, late = queue.pop(0)
        for ob in (o, p):
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            loose = [v for v in bm.verts if not v.link_faces]
            if loose:
                bmesh.ops.delete(bm, geom=loose, context="VERTS")
                bm.to_mesh(ob.data)
            bm.free()
        v0, vp = _volume(o.data), _volume(p.data)
        home = p.matrix_world.copy()
        ok = False
        for t in range(tries):
            keep = o.data.copy()
            if t:
                p.matrix_world = Matrix.Translation(Vector([rng.uniform(-1, 1) * 0.006 * t for _ in range(3)])) @ home
            bpy.context.view_layer.update()
            m = o.modifiers.new("U", "BOOLEAN")
            m.operation, m.solver, m.object = "UNION", "EXACT", p
            m.material_mode = "TRANSFER"
            with M._override(o):
                bpy.ops.object.modifier_apply(modifier=m.name)
            v1 = _volume(o.data)
            # round 5: a union that leaves the piece unjoined (touching, not overlapping) also passes the volume
            # test, so the result must still be one shell
            if v1 >= max(v0, vp) * 0.995 and v1 <= (v0 + vp) * 1.005 and _nshells(o) == 1:
                ok = True
                bpy.data.meshes.remove(keep)
                if t or late:
                    retried.append((i, t, late))
                break
            old = o.data
            o.data = keep
            bpy.data.meshes.remove(old)
        if not ok and not late:
            # a shell that fails against the part-built solid is tried again once everything else is on (its
            # neighbours then cut it differently), from home
            p.matrix_world = home
            queue.append((i, p, True))
            continue
        if not ok:
            ctr = sum((p.matrix_world @ v.co for v in p.data.vertices), Vector()) / max(1, len(p.data.vertices))
            failed.append((i, [round(c, 2) for c in ctr], round(v0, 3), round(vp, 3)))
        bpy.data.objects.remove(p, do_unlink=True)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=UNION_MERGE)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=UNION_MERGE)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    M.drop_specks(bm, min_area=0.02)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    K.drop_unused_slots(o)
    return {"shells": len(others) + 1, "retried": retried, "failed": failed}


def _nshells(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = M._shell_ids(bm)[1]
    bm.free()
    return n


def _shell_report(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    out = []
    for k in range(n):
        fs = [f for f in bm.faces if ids[f.index] == k]
        c = sum((f.calc_center_median() for f in fs), Vector()) / len(fs)
        out.append((sum(len(f.verts) - 2 for f in fs), [round(x, 2) for x in c]))
    bm.free()
    return sorted(out, reverse=True)


def _self_hits(o):
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    pairs = [(x, y) for x, y in tree.overlap(tree) if x < y and not set(bm.faces[x].verts) & set(bm.faces[y].verts)]
    where = [[round(c, 2) for c in bm.faces[x].calc_center_median()] for x, _ in pairs[:5]]
    bm.free()
    return len(pairs), where


def inverted(o):
    return len(_inverted_ids(o))


def _inverted_ids(o):
    """Face indices whose front side is solid (ray parity along the normal is odd)."""
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.normal_update()
    t = BVHTree.FromBMesh(bm)
    out = []
    for f in bm.faces:
        if f.calc_area() < 1e-12:
            continue
        n = f.normal.normalized()
        p = f.calc_center_median() + n * 1e-4
        hits = 0
        while hits < 60:
            loc = t.ray_cast(p, n)[0]
            if loc is None:
                break
            hits += 1
            p = loc + n * 1e-5
        if hits % 2:
            out.append(f.index)
    bm.free()
    return out


def _guarded(o, fn):
    """Run a cleanup step on o; undo it if it leaves more crossing faces or more shells than before."""
    before = (_self_hits(o)[0], len(_shell_report(o)))
    keep = o.data.copy()
    out = fn()
    after = (_self_hits(o)[0], len(_shell_report(o)))
    if after[0] > before[0] or after[1] > before[1]:
        old = o.data
        o.data = keep
        bpy.data.meshes.remove(old)
        return None
    bpy.data.meshes.remove(keep)
    return out


def _finish(o):
    res = M.finish(o, union=False, uv=UV)
    for _ in range(3):
        crumbs = m012._drop_inner(o)
        if not (crumbs or res["nonmanifold_edges"] or res["boundary_edges"]):
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
        _guarded(o, lambda: m012._force_slivers(o))
        res = M.finish(o, union=False, uv=UV)
    return res


def _tri_quads(bm):
    n = 0
    for f in [f for f in bm.faces if len(f.verts) > 3]:
        if not f.is_valid or len(f.verts) < 4:
            continue
        if len(f.verts) > 4:
            bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="BEAUTY")
            n += 1
            continue
        a, b, c, d = f.verts
        opts = sorted(((min(m011._min_angle([p.co, q.co, r.co]), m011._min_angle([p.co, q.co, s.co])), p, q)
                       for p, q, r, s in ((a, c, b, d), (b, d, c, a))), key=lambda x: -x[0])
        for _, p, q in opts:
            e = bm.edges.get((p, q))
            if e is None or bmesh.ops.rotate_edges(bm, edges=[e], use_ccw=False)["edges"]:
                break
        else:
            continue
        if f.is_valid and len(f.verts) == 4:
            bmesh.ops.connect_verts(bm, verts=[p, q])
            n += 1
    leftover = [f for f in bm.faces if len(f.verts) > 3]
    if leftover:
        bmesh.ops.triangulate(bm, faces=leftover, quad_method="BEAUTY", ngon_method="BEAUTY")
    return n


def _collapse_needles(o, max_len=0.05, lim=POLISH_LIM):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = 0
    for _ in range(30):
        bad = None
        for f in bm.faces:
            if math.degrees(m011._min_angle([v.co for v in f.verts])) < lim:
                e = min(f.edges, key=lambda e: e.calc_length())
                if e.calc_length() < max_len and all(v.co.z > 1e-4 for v in e.verts):
                    bad = e
                    break
        if bad is None:
            break
        bmesh.ops.collapse(bm, edges=[bad], uvs=True)
        n += 1
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    return n


def _flip_thin(o, lim=POLISH_LIM, max_bend=20.0):
    """Needles with no short edge: rotate the needle's longest edge when both new triangles are fatter and the two
    faces are nearly coplanar (at most max_bend degrees apart, so the silhouette doesn't change). Returns flips."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = 0
    for _ in range(20):
        done = False
        for f in list(bm.faces):
            if not f.is_valid or len(f.verts) != 3:
                continue
            if math.degrees(m011._min_angle([v.co for v in f.verts])) >= lim:
                continue
            e = max(f.edges, key=lambda e: e.calc_length())
            if len(e.link_faces) != 2:
                continue
            g = e.link_faces[0] if e.link_faces[1] is f else e.link_faces[1]
            if math.degrees(f.normal.angle(g.normal, 0.0)) > max_bend:
                continue
            a, b = e.verts
            c = next(v for v in f.verts if v not in (a, b))
            d = next(v for v in g.verts if v not in (a, b))
            if bm.edges.get((c, d)):
                continue
            new = min(m011._min_angle([a.co, c.co, d.co]), m011._min_angle([b.co, c.co, d.co]))
            old = min(m011._min_angle([v.co for v in f.verts]), m011._min_angle([v.co for v in g.verts]))
            if new <= old:
                continue
            if bmesh.ops.rotate_edges(bm, edges=[e], use_ccw=False)["edges"]:
                n += 1
                done = True
                break
        if not done:
            break
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    return n


def _loops(edges):
    nbr = {}
    for e in edges:
        a, b = e.verts
        nbr.setdefault(a, []).append(b)
        nbr.setdefault(b, []).append(a)
    seen, out = set(), []
    for v0 in nbr:
        if v0 in seen or len(nbr[v0]) != 2:
            continue
        loop, prev, v = [v0], None, v0
        seen.add(v0)
        while True:
            nxt = next((w for w in nbr[v] if w is not prev), None)
            if nxt is None or nxt is v0 or nxt in seen or len(nbr[nxt]) != 2:
                break
            loop.append(nxt)
            seen.add(nxt)
            prev, v = v, nxt
        if len(loop) >= 3:
            out.append(loop)
    return out


def _fan_fill(bm, bnd):
    made = 0
    for loop in _loops(bnd):
        k = len(loop)
        for s0 in range(k):
            vs = loop[s0:] + loop[:s0]
            if any(bm.edges.get((vs[0], vs[i])) for i in range(2, k - 1)):
                continue
            for i in range(1, k - 1):
                try:
                    bm.faces.new((vs[0], vs[i], vs[i + 1]))
                    made += 1
                except ValueError:
                    pass
            break
    return made


def _seal(o, rounds=3):
    """Close the holes left by deleted slivers (fan fill), triangulate, repair edges on more than two faces."""
    n = 0
    for _ in range(rounds):
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bnd = [e for e in bm.edges if e.is_boundary]
        if not bnd:
            bm.free()
            break
        n += _fan_fill(bm, bnd)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY")
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(o.data)
        bm.free()
        M.repair_nonmanifold(o)
    return n


def _polish(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = _tri_quads(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = _guarded(o, lambda: m012._force_slivers(o, lim=POLISH_LIM))
    if forced is None:
        forced = _guarded(o, lambda: m012._force_slivers(o, lim=3.0, max_len=0.08))
    needles = _guarded(o, lambda: _collapse_needles(o))
    removed = []
    for _ in range(4):
        bad = _inverted_ids(o)
        if not bad:
            break
        removed.append(len(bad))
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.faces[i] for i in bad], context="FACES")
        bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bm.to_mesh(o.data)
        bm.free()
        _seal(o)
        _guarded(o, lambda: m012._force_slivers(o, lim=POLISH_LIM))
    late = []
    for ml in (0.15, 0.3, 0.5):
        if not m012._thin(o, POLISH_LIM)["under"]:
            break
        late.append(_guarded(o, lambda: m012._force_slivers(o, lim=POLISH_LIM, max_len=ml)))
    if m012._thin(o, POLISH_LIM)["under"]:
        late.append(_guarded(o, lambda: _flip_thin(o)))
    bc = m011._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
    o.data.update()
    M.smart_uv(o, **UV)
    return {"split": split, "forced": forced, "needles": needles, "late": late, "inverted_removed": removed,
            "uv_cut": m012._uv_unfold(o)}


CLEAN_MOVE = 0.05


def _clean_mesh(o, planes=(0.0,)):
    """The shared sliver pass, guarded (thin lobe flanks and thorn tips must not fold through each other)."""
    pockets = m012._drop_inner(o)
    log = None
    for mv in (CLEAN_MOVE, CLEAN_MOVE / 2, CLEAN_MOVE / 4):
        log = _guarded(o, lambda: m011._clean(o, m011._plane_lock(planes), max_move=mv))
        if log is not None:
            log["max_move"] = mv
            break
    log = log or {"undone": True}
    pockets += m012._drop_inner(o)
    log["pockets"] = pockets
    log["forced"] = _guarded(o, lambda: m012._force_slivers(o))
    return log


def _fix_floor(o):
    """Faces the floor cut made (flat, facing down at z 0): plain wood, Tint 0.95."""
    p = m011._Paint(o, off=(0, 0, 0))
    lay = p.tint_layer
    for f in p.bm.faces:
        if f.normal.z < -0.99 and abs(f.calc_center_median().z) < 1e-3:
            f.material_index = p._mi(WOOD)
            for lo in f.loops:
                lo[lay] = (0.95, 0.95, 0.95, 1.0)
    p.done()


# ---- stages 5 + 6 ---------------------------------------------------------------------------------------------------------
# Stage 5: nothing. The sheet shows an ordinary sunlit shrub: no emissive key, no light (decision 7).
# Stage 6: nothing. No glow, sparkle, falling leaves or dust on the sheet: no socket (decision 7).

# ---- build ---------------------------------------------------------------------------------------------------------------
PARTS = (("ThornBushBranchCore", core_part), ("ThornBushLeafCluster", cluster_part), ("ThornBushThorn", thorn_part))
HERO = "ThornBushNode"
UNION_PARTS = {"ThornBushBranchCore", "ThornBushLeafCluster"}
NOTES = {
    HERO: "thorn shrub (forage shrub): a thick faceted brown skeleton (flared foot, eight kinked limbs, two crossing "
          "in front), nine fans of pointed faceted leaf gems and five fat pale-cream thorns on the diagonals; one "
          "closed mesh, flat base",
    "ThornBushBranchCore": "Branch Core (reusable): an 8-sided trunk splitting into upper-left and upper-right limbs, "
                           "a short centre stub and a low left limb, flat pale cut ends",
    "ThornBushLeafCluster": "Leaf Cluster (reusable): a flattened fan of four pointed 6-sided leaf gems on a hub",
    "ThornBushThorn": "Thorn (reusable): a fat straight 5-sided pyramid (L 1.9, base 1.1) with a flat base, cream to the tip",
}


def _make(name, fn, role, budget):
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget, collision="hull",
             tint_var=0.0)
    lg = {}
    if role == "hero" or name in UNION_PARTS:
        lg["union"] = _union(o)
    if role == "hero":
        hoff = M._build_offset(fn)
        m004.floor_cut(o, z0=-hoff.z)
        _fix_floor(o)
        lg["clean"] = _clean_mesh(o, (0.0,))
    elif name in UNION_PARTS:
        lg["clean"] = _clean_mesh(o, ())
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    # bowtie verts (two closed fans meeting at one point, which edge checks miss; lobe hubs make them): split
    lg["bowties"] = M.fix_bowties(o)
    return o, lg


def build(render=True, parts=True):
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn, "part", 1000)
    info_parts = {k: list(v) if isinstance(v, list) else v for k, v in INFO.items()}
    h, log["hero"] = _make(HERO, hero, "hero", 4000)
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    _restyle()
    M.display(NUM, order, TITLE)
    dropped = _drop_unused(order)
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    out = {"audit": [{k: M.audit(o)[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges",
                                                     "boundary_edges", "nonmanifold_verts", "wire_edges", "loose_verts",
                                                     "zero_area_faces",
                                                     "normals", "ngons", "dup_verts")}
                     for o in order],
           "thin": {o.name: m012._thin(o, POLISH_LIM) for o in order}, "log": log, "dropped": dropped,
           "problems": K.check(order),
           "inverted": {o.name: inverted(o) for o in order},
           "self_hits": {o.name: _self_hits(o) for o in order},
           "uv": {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped",
                                                                            "min_gap", "density",
                                                                            "stretch_conformal_p95")}
                  for o in order}}
    out["problems"] = list(out["problems"])
    out["problems"] += [f"{a_['name']}: {a_['shells']} shells" for a_ in out["audit"] if a_["shells"] != 1]
    out["problems"] += [f"{a_['name']}: {a_['nonmanifold_edges']} non-manifold / {a_['boundary_edges']} boundary"
                        for a_ in out["audit"] if a_["nonmanifold_edges"] or a_["boundary_edges"]]
    out["problems"] += [f"{a_['name']}: {a_['nonmanifold_verts']} non-manifold (bowtie) verts" for a_ in out["audit"]
                        if a_["nonmanifold_verts"]]
    out["problems"] += [f"{n}: {c} inverted faces" for n, c in out["inverted"].items() if c]
    out["problems"] += [f"{n}: {c} crossing face pairs {w}" for n, (c, w) in out["self_hits"].items() if c]
    out["problems"] += [f"{n}: union left out shells {v['union']['failed']}" for n, v in log.items()
                        if isinstance(v, dict) and v.get("union", {}).get("failed")]
    lob = list(info_parts.get("lobe_inverted", [])) + list(INFO.get("lobe_inverted", []))
    out["problems"] += [f"lobe pieces with inverted faces: {sum(1 for x in lob if x)}" for _ in [0] if any(lob)]
    for o in order:
        if o.get("kit_role") == "part" and M.audit(o)["tris"] > 1000:
            out["problems"].append(f"{o.name}: over the part budget")
    if M.audit(h)["tris"] > 4000:
        out["problems"].append(f"{h.name}: over the hero budget")
    if render:
        out["views"] = render_views(order)
    return out


def _drop_unused(objs):
    names = {o.name for o in objs}
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.split(".")[0] in names]
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m024_")]
    out = {"meshes": len(meshes), "materials": len(mats)}
    for m in meshes:
        bpy.data.meshes.remove(m)
    for m in mats:
        bpy.data.materials.remove(m)
    for o in objs:
        if o.data.name != o.name and o.name not in bpy.data.meshes:
            o.data.name = o.name
    return out


# ---- renders -------------------------------------------------------------------------------------------------------------
# the sheet's comparison cameras (decision 9)
SHEET_VIEWS = {"f34_sheet": (0, 13), "front_sheet": (0, 10), "rear_sheet": (180, 10), "side_sheet": (90, 10),
               "r34_sheet": (180, 15), "top_tilt_sheet": (0, 70)}
SHEET_LENS = 3.0        # the sheet's cells are drawn almost orthographic: the *_sheet shots use a 3x longer lens


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


# the exploded shot as the sheet lays it out (studs from the core's foot; x right, z up): the core at the centre, three
# clusters above (left, top centre, right), two low clusters left and right with thorns plugged into their outer
# sides, two loose thorns far left and right. (part, location, rotation XYZ (deg))
EXPL = (("ThornBushBranchCore", (0.0, 0.0, 0.0), (0, 0, 0)),
        ("ThornBushLeafCluster", (0.2, 0.0, 1.85), (0, 0, 0)),
        ("ThornBushLeafCluster", (-1.75, 0.0, 1.3), (0, -15, 0)),
        ("ThornBushLeafCluster", (1.8, 0.0, 1.15), (0, 15, 0)),
        ("ThornBushLeafCluster", (-1.85, 0.0, -0.1), (0, -35, 0)),
        ("ThornBushLeafCluster", (1.9, 0.0, -0.15), (0, 35, 0)),
        ("ThornBushThorn", (-2.7, 0.0, 0.3), (0, -100, 0)),
        ("ThornBushThorn", (2.75, 0.0, 0.25), (0, 100, 0)),
        ("ThornBushThorn", (-3.4, 0.0, 2.0), (0, 135, 0)),
        ("ThornBushThorn", (3.3, 0.0, 2.5), (0, -150, 0)))


def render_views(objs):
    h = objs[0]
    by = {o.name: o for o in objs}
    shown = []
    saved = M.explode(objs[1:], {})
    try:
        if len(objs) > 1:
            base = Vector((h.location.x + 40, h.location.y, 0.0))
            for k, (part, loc, rot) in enumerate(EXPL):
                c = bpy.data.objects.new(f"_m024_expl_{k}", by[part].data)
                by[part].users_collection[0].objects.link(c)
                r = (Matrix.Rotation(math.radians(rot[1]), 4, "Y") @ Matrix.Rotation(math.radians(rot[0]), 4, "X")
                     @ Matrix.Rotation(math.radians(rot[2]), 4, "Z"))
                c.matrix_world = Matrix.Translation(base + Vector(loc)) @ r
                shown.append(c)
            bpy.context.view_layer.update()
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        if shown:
            extra["exploded"] = (shown, -12, 12)
        for o in objs[1:]:
            extra["part_" + o.name.replace("ThornBush", "").lower()] = ([o], -20, 15)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            return M.views(NUM, [h], extra=extra)
        finally:
            kit["render_group"] = orig
    finally:
        for c in shown:
            bpy.data.objects.remove(c, do_unlink=True)
        M.restore(saved)
        M.display(NUM, objs, TITLE)


# ---- measuring (the study's masks, numpy) ----------------------------------------------------------------------------------
REF_VIEWS = {"f34": (15, 62, 510, 404), "r34": (515, 62, 1010, 404), "front": (20, 454, 272, 656),
             "side": (278, 454, 500, 656), "rear": (506, 454, 758, 656), "top": (764, 454, 1006, 656)}
OUR_VIEWS = {"f34": "f34_sheet", "r34": "r34_sheet", "front": "front_sheet", "side": "side_sheet",
             "rear": "rear_sheet", "top": "top_tilt_sheet"}


def _classes(px, paper):
    """px (h, w, 3) sRGB 0-255 -> 0 paper, 1 L leaves, 2 T thorns, 3 W wood, 4 O other (the study's cls())."""
    a = px / 255.0
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-9), 0)
    v = mx
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    dd = np.maximum(d, 1e-9)
    hh = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60
    hh = np.where(d == 0, 0, hh)
    bg = np.abs(px - np.array(paper)).max(-1) <= 18
    L = (~bg) & (s >= 0.25) & (hh >= 60) & (hh <= 170) & (px[..., 1] > 40)
    T = (~bg) & (hh >= 22) & (hh <= 55) & (s >= 0.12) & (s < 0.43) & (v >= 0.66) & ~L
    W = (~bg) & (s >= 0.30) & ((hh < 45) | (hh >= 340)) & (v < 0.88) & ~L & ~T
    out = np.full(r.shape, 4, np.uint8)
    out[bg] = 0
    out[W] = 3
    out[T] = 2
    out[L] = 1
    return out


def _load(path, box=None):
    px = K.NS["KIT"]["load_px"](path)[::-1, :, :3] * 255.0
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1]
    return np.clip(px, 0, 255)


def _paper(px):
    c = np.concatenate([px[:4].reshape(-1, 3), px[-4:].reshape(-1, 3)])
    return tuple(np.median(c, 0))


def _runs(row, W, minw=3):
    seg, start = [], None
    for x in range(len(row) + 1):
        on = x < len(row) and row[x]
        if on and start is None:
            start = x
        if not on and start is not None:
            if x - start >= minw:
                seg.append((round(start / W, 2), round(x / W, 2)))
            start = None
    return seg


def stats(px, paper=None):
    paper = paper or _paper(px)
    c = _classes(px, paper)
    # round 2: leaves, thorns and wood only; class O (other) holds the grey ground shadow, which inflated the
    # silhouette box (the verifier's f34 W : H 1.23 with the floor hidden against 1.30 here)
    obj = (c >= 1) & (c <= 3)
    cols = np.nonzero(obj.sum(0) >= 3)[0]
    rows = np.nonzero(obj.sum(1) >= 3)[0]
    bx0, bx1, by0, by1 = cols.min(), cols.max(), rows.min(), rows.max()
    W, H = bx1 - bx0, by1 - by0
    sub = c[by0:by1 + 1, bx0:bx1 + 1]
    n = max(1, ((sub >= 1) & (sub <= 3)).sum())
    out = {"wh": round(W / H, 3), "L": round((sub == 1).sum() / n, 3), "T": round((sub == 2).sum() / n, 3),
           "W": round((sub == 3).sum() / n, 3)}
    top = []
    for i in range(21):
        x = bx0 + int(i * W / 20)
        ys = np.nonzero(obj[:, max(0, x - 1):x + 2].any(1))[0]
        top.append(round((by1 - ys.min()) / H, 2) if len(ys) else None)
    out["top"] = top
    out["peaks"] = sum(1 for i in range(3, 20) if top[i] is not None and top[i - 1] is not None and
                       top[i + 1] is not None and top[i] > top[i - 1] and top[i] >= top[i + 1])
    wid = []
    for i in range(11):
        y = by1 - int(i * H / 10)
        xs = np.nonzero(obj[min(y, obj.shape[0] - 1)])[0]
        wid.append((round((xs.max() - xs.min()) / W, 2), round((xs.min() - bx0) / W, 2)) if len(xs) else None)
    out["width"] = wid
    pxs = px[by0:by1 + 1, bx0:bx1 + 1]
    hexs = lambda q: "#" + "".join(f"{int(round(x)):02X}" for x in q)
    for k, lab in ((1, "L"), (2, "T"), (3, "W")):
        sel = pxs[sub == k]
        if len(sel) >= 8:
            srt = sel[np.argsort(sel.sum(1))]
            q = len(srt) // 4
            out[lab + "med"] = hexs(np.median(sel, axis=0))
            out[lab + "lit"] = hexs(np.median(srt[-q:], axis=0))
            out[lab + "shade"] = hexs(np.median(srt[:q], axis=0))
    runs = []
    for hh_ in (0.06, 0.15, 0.25, 0.35, 0.45, 0.5, 0.6):
        r = by1 - by0 - int(hh_ * H)
        row = (sub[max(0, r - 1):r + 2] == 3).sum(0) >= 2
        runs.append((hh_, _runs(row, W)))
    out["wood_runs"] = runs
    bands = []
    for i in range(5):
        r0, r1 = by1 - int((i + 1) * H / 5), by1 - int(i * H / 5)
        sel = px[r0:r1 + 1, bx0:bx1 + 1][c[r0:r1 + 1, bx0:bx1 + 1] == 1]
        bands.append(hexs(np.median(sel, axis=0)) if len(sel) > 20 else None)
    out["Lbands"] = bands
    return out


def _fit(px, h):
    """Nearest-neighbour resize of a bottom-up RGBA block to height h."""
    ys = (np.arange(h) * px.shape[0] / h).astype(int)
    w = max(1, int(round(px.shape[1] * h / px.shape[0])))
    xs = (np.arange(w) * px.shape[1] / w).astype(int)
    return px[ys][:, xs]


def _crop_obj(px, pad=0.06):
    """Crop a bottom-up RGBA render / sheet cell to its object silhouette (+pad)."""
    top = np.clip(px[::-1, :, :3] * 255.0, 0, 255)
    c = _classes(top, _paper(top))
    obj = (c >= 1) & (c <= 3)
    ys, xs = np.nonzero(obj)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    p = int(pad * max(y1 - y0, x1 - x0))
    H, W = obj.shape
    y0, y1, x0, x1 = max(0, y0 - p), min(H, y1 + p), max(0, x0 - p), min(W, x1 + p)
    return px[H - y1:H - y0, x0:x1]


def compare(views=("f34", "front", "side", "rear", "r34", "top"), h=360):
    """Sheet cell (left) beside our long-lens render (right), each cropped to the silhouette and scaled to the same
    height; one row per view -> M024_sheet_compare.png."""
    kit = K.NS["KIT"]
    ref = kit["load_px"](M.ref(NUM))
    H = ref.shape[0]
    rows = []
    for v in views:
        x0, y0, x1, y1 = REF_VIEWS[v]
        a = _fit(_crop_obj(ref[H - y1:H - y0, x0:x1]), h)
        b = _fit(_crop_obj(kit["load_px"](f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[v]}.png")), h)
        gap = np.ones((h, 20, 4), np.float32)
        rows.append(np.concatenate([a, gap, b], axis=1))
    w = max(r.shape[1] for r in rows)
    rows = [np.concatenate([r, np.ones((h, w - r.shape[1], 4), np.float32)], axis=1) if r.shape[1] < w else r
            for r in rows]
    out = f"{M.MODEL_RENDERS}/{M.code(NUM)}/{M.code(NUM)}_sheet_compare.png"
    kit["save_px"](kit["vstack"](rows), out)
    return out


def measure(views=("f34", "front", "side", "rear", "r34", "top")):
    """Sheet against our renders, per view (the study's masks on both; paper from each image's top/bottom rows)."""
    ref = M.ref(NUM)
    out = {}
    for vname in views:
        a = stats(_load(ref, REF_VIEWS[vname]))
        b = stats(_load(f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[vname]}.png"))
        out[vname] = {"sheet": a, "ours": b}
    return out
