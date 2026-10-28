"""017 Berry Bush (references/017.png): a round, slightly wide low-poly shrub. Five faceted brown stems splay out of one
fused root foot and carry fifteen faceted leaf lobes (broad-faceted polyhedra with a pointed five-facet apex) in
five clumps; eight
glossy faceted red berries sit half-sunk in the gaps between the lobes.

    import importlib, kit_models, m017; importlib.reload(kit_models); importlib.reload(m017); m017.build()

Parts as on the sheet's exploded view, each built by its own function (front -Y, ground z = 0):
- BerryBushLeafClump: the exploded three-lobe clump on a flared hex collar with a hex peg (lobe() x 3, collar, peg).
- BerryBushBerry: one round faceted berry (ico-2, squash 0.96) with a small brown peg on top.
- BerryBushTrunkFork: the exploded fork, a 6-sided trunk splitting into three limbs with pale hex cut ends.
The hero (BerryBushNode) is built from the same builders: trunk() with five thin stems parting at the ground (every hero
view shows five stems, not the exploded fork: M017_spec.md 3.1), five clump() calls with their own lobe lists, eight
berry() copies; one exact union, floor-cut at the ground.

Every table below is in SHEET studs (the sheet's own scale: berry 1.0, bush 5.0 tall). Decision 1 (main session):
WorldModeling's forage size wins, so every builder scales its result by S at the end (bush about 4.3 x 3.5 x 3.6).
Colour (stage 4) is painted by position fields inside the builders, before the union (the union and cleanup keep each
face's key and Tint): see "stage 4" below and M017_spec.md.
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

NUM, TITLE, SHEET = 17, "Berry Bush", "M017"
S = 0.70                 # sheet studs -> kit studs (decision 1: the hero 3.6 tall; the sheet's 5.0 x 0.72, less the
                         # 0.1 our lobes stand taller)

LEAF, LEAF_YOUNG, LEAF_OLD = "m017_leaf", "m017_leaf_young", "m017_leaf_old"
BERRY, BERRY_DEEP, BERRY_STEM = "m017_berry", "m017_berry_deep", "m017_berry_stem"
BARK, BARK_DARK, HEART, PEG = "m017_bark", "m017_bark_dark", "m017_heartwood", "m017_peg"
BARK_LIGHT = "m017_bark_light"
LEAF_KEYS = (LEAF, LEAF_YOUNG, LEAF_OLD)

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0
COLOUR = [True]          # stage 1 renders could switch the paint off (placeholder keys only)

# ---- palette --------------------------------------------------------------------------------------------------------
# (hex, roughness, specular IOR level or None for flintkit's default, low_spec)
# stage 4, two passes:
# 1. calibrate() on the test dome against the sheet's rendered medians (TARGETS); the dome rendered each key within
#    3 levels of its target (the dome hexes in the comments).
# 2. On the hero those rendered darker (lobe sides and undersides, the canopy's own shadow; the dome's top faces the
#    sun): each key corrected in linear light by sheet / hero over the lit views (front, front three-quarter, top;
#    the side and rear are lit mostly by the studio's fill and are reported, not fitted, as M013): leaves x1.25,
#    young x1.15, old x1.4, berries x1.25, bark x1.1 (the front's stems sit in the canopy's cast shadow; the side and
#    rear bark already matched).
PALETTE = {
    LEAF: ("#638427", 0.85, None, True),            # dome #698C22 (target #6B8F22)
    LEAF_YOUNG: ("#95AD2F", 0.85, None, True),      # dome #9CBC32 (#A0C032); round 2: yellower / lighter (the lit
                                                    # quartile read #97BC32 against the sheet's #A9C72D)
    LEAF_OLD: ("#4F6D25", 0.85, None, True),        # dome #4D6A1E (#4E6D1E)
    BERRY: ("#D71A1B", 0.32, 0.5, False),           # dome #F32524 (#F42524)
    BERRY_DEEP: ("#A3040B", 0.32, 0.5, False),      # dome #B51B1D (#B5161A)
    BERRY_STEM: ("#6A412C", 0.9, None, False),      # dome #85523A (#865137)
    BARK: ("#73502F", 0.9, None, False),            # dome #8A5E3B (#8A5D38)
    BARK_DARK: ("#4D341B", 0.9, None, False),       # dome #5D422B (#5E4128)
    BARK_LIGHT: ("#986A40", 0.9, None, False),      # round 2: the stem foot (the sheet's lightest bark band, #835A34;
                                                    # the studio's canopy shadow sits on it): bark x1.85 linear
    HEART: ("#8E7B6A", 0.85, None, False),          # dome #C1A488 (#C3A588); round 2: x0.85 linear (part rendered
                                                    # #CCAD90 against the cut end's #BD9F83)
    PEG: ("#453928", 0.9, None, False),             # dome #594A37 (#584833)
}


def palette():
    for k, (hx, rough, spec, low) in PALETTE.items():
        K.set_colour(k, hx, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hx, rough=rough, low_spec=low)
    _restyle()


def _restyle():
    """Berry keys (mix keys too) at their specular; leaf mix keys at the foliage specular (mix_key makes them low-spec
    already, this keeps materials made before a palette change in line)."""
    for m in bpy.data.materials:
        if not m.name.startswith("FB_m017_") or not m.node_tree:
            continue
        b = m.node_tree.nodes.get("Principled BSDF")
        if not b or "Specular IOR Level" not in b.inputs:
            continue
        key = m.name[3:]
        if key.startswith(BERRY) and not key.startswith(BERRY_STEM):
            b.inputs["Specular IOR Level"].default_value = 0.5
            b.inputs["Roughness"].default_value = PALETTE[BERRY][1]
        elif key.startswith("m017_leaf"):
            b.inputs["Specular IOR Level"].default_value = K.FOLIAGE_SPEC


# calibration targets: the sheet's rendered medians (M017_spec.md 5.4), not the swatches. key -> (sRGB, kind)
TARGETS = {LEAF: ((0x6B, 0x8F, 0x22), "green"), LEAF_YOUNG: ((0xA0, 0xC0, 0x32), "green"),
           LEAF_OLD: ((0x4E, 0x6D, 0x1E), "green"), BERRY: ((0xF4, 0x25, 0x24), "vivid"),
           BERRY_DEEP: ((0xB5, 0x16, 0x1A), "vivid"), BERRY_STEM: ((0x86, 0x51, 0x37), "all"),
           BARK: ((0x8A, 0x5D, 0x38), "brown"), BARK_DARK: ((0x5E, 0x41, 0x28), "brown"), BARK_LIGHT: ((0xA6, 0x73, 0x48), "brown"),
           HEART: ((0xC3, 0xA5, 0x88), "all"), PEG: ((0x58, 0x48, 0x33), "all")}


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS): each key on the kit's faceted test dome, rendered in the studio,
    corrected in linear light until its median matches the sheet's rendered median. Returns {key: (hex, rendered)}
    and leaves the keys set (write the hexes into PALETTE)."""
    keys = keys or list(TARGETS)
    for k in keys:
        K.fk().material(k)
    try:
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        gone = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]
        for m in gone:
            bpy.data.meshes.remove(m)


# ---- small geometry helpers -------------------------------------------------------------------------------------------
def _frame_from(d):
    """An orthonormal (u, v, d) basis with d the given axis."""
    d = Vector(d).normalized()
    u = d.orthogonal().normalized()
    v = d.cross(u).normalized()
    return u, v, d


def _cap(bm, ring, flip=False):
    """A flat cap over a closed ring of verts, cut into triangles (no centre point: a hex gives 4 triangles)."""
    vs = list(reversed(ring)) if flip else list(ring)
    f = bm.faces.new(vs)
    res = bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="BEAUTY")
    return res["faces"]


def _tube(a, pts, radii, seed, mat=None, top_mat=None, bot_mat=None, sides=6, jitter=0.08, twist=10.0):
    """A faceted 6-sided limb along the points pts with the given ring radii: each ring turned and scaled a little
    (radius +-jitter, +-twist degrees), flat hex caps at both ends (top_mat on the top cap: the pale cut end).
    Returns (all verts, top cap faces)."""
    rng = random.Random(seed)
    bm = a.bm
    mat = mat or BARK
    rings = []
    u0, v0, _ = _frame_from(pts[1] - pts[0])
    ph = rng.uniform(0, 2 * math.pi)
    for i, p in enumerate(pts):
        if i == 0:
            d = pts[1] - pts[0]
        elif i == len(pts) - 1:
            d = pts[-1] - pts[-2]
        else:
            d = (pts[i + 1] - pts[i - 1])
        d.normalize()
        # parallel transport of the previous ring's u
        u = (u0 - d * u0.dot(d)).normalized()
        v = d.cross(u).normalized()
        u0 = u
        tw = ph + math.radians(rng.uniform(-twist, twist)) if 0 < i < len(pts) - 1 else ph
        ring = []
        for k in range(sides):
            t = tw + 2 * math.pi * k / sides
            r = radii[i] * (1 + (rng.uniform(-jitter, jitter) if 0 < i < len(pts) - 1 else rng.uniform(-0.03, 0.03)))
            ring.append(bm.verts.new(p + (u * math.cos(t) + v * math.sin(t)) * r))
        rings.append(ring)
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            faces.append(bm.faces.new((r0[k], r0[j], r1[j], r1[k])))
    bot = _cap(bm, rings[0], flip=True)
    top = _cap(bm, rings[-1])
    vs = [v for r in rings for v in r]
    bmesh.ops.recalc_face_normals(bm, faces=faces + bot + top)
    a._finish(vs, mat, tint=1.0)
    if top_mat:
        mi = a._mi(top_mat)
        for f in top:
            f.material_index = mi
    if bot_mat:
        mi = a._mi(bot_mat)
        for f in bot:
            f.material_index = mi
    return vs, top


def _ico(bm, subdiv=2):
    """A unit ico sphere added to bm (built in a scratch bmesh and copied in: bmesh.ops.create_icosphere on a bmesh
    that already holds geometry invalidated the earlier pieces' vert references). Pole at +Z. Returns the verts."""
    tmp = bmesh.new()
    bmesh.ops.create_icosphere(tmp, subdivisions=subdiv, radius=1.0)
    vmap = {v: bm.verts.new(v.co) for v in tmp.verts}
    for f in tmp.faces:
        bm.faces.new([vmap[v] for v in f.verts])
    tmp.free()
    return list(vmap.values())


def _ico_flat(bm, push):
    """An ico-1 (20 faces) subdivided once FLAT (80 triangles, 42 verts, the same count as an ico-2), its new mid-edge
    verts pushed only `push` of the way out to the unit sphere, so each ico-1 face reads as one broad, slightly bent
    facet group (round 2: an ico-2 with every vert on the sphere read as a round geodesic ball). Built in a scratch
    bmesh and copied in (see _ico). Pole at +Z. Returns (verts, {mid vert: (parent a, parent b)}) in bm."""
    tmp = bmesh.new()
    bmesh.ops.create_icosphere(tmp, subdivisions=1, radius=1.0)
    old = set(tmp.verts)
    bmesh.ops.subdivide_edges(tmp, edges=list(tmp.edges), cuts=1, use_grid_fill=True)
    par = {}
    for v in tmp.verts:
        if v in old:
            continue
        ps = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in old]
        par[v] = ps
        v.co = v.co.lerp(v.co.normalized(), push)
    vmap = {v: bm.verts.new(v.co) for v in tmp.verts}
    for f in tmp.faces:
        bm.faces.new([vmap[v] for v in f.verts])
    mids = {vmap[v]: tuple(vmap[p] for p in ps) for v, ps in par.items()}
    tmp.free()
    return list(vmap.values()), mids


def _inside(tree, p, d=Vector((0.31, 0.17, 0.93)).normalized()):
    """Ray parity: p inside the closed surface(s) in tree."""
    hits, q = 0, Vector(p)
    while True:
        loc = tree.ray_cast(q, d)[0]
        if loc is None:
            return hits % 2 == 1
        hits += 1
        q = loc + d * 1e-4


def _entry(tree, pts, step=0.03):
    """March back down a stem polyline from its tip: the first point outside the lobes in tree (the stem's entry into
    its clump) and the length of stem inside. (entry = the tip, depth 0 if the tip is outside.)"""
    if not _inside(tree, pts[-1]):
        return pts[-1].copy(), 0.0
    run = 0.0
    for p, q in zip(reversed(pts[1:]), reversed(pts[:-1])):
        seg = (q - p).length
        n = max(1, int(seg / step))
        for k in range(1, n + 1):
            x = p.lerp(q, k / n)
            if not _inside(tree, x):
                return x, run + seg * k / n
        run += seg
    return pts[0].copy(), run


def _seed(name):
    """A stable seed from a name (Python's str hash changes per process)."""
    return 17000 + sum((i + 1) * ord(ch) for i, ch in enumerate(name))


def _dist_poly(c, pts):
    """Distance from c to the polyline pts."""
    best = math.inf
    for p, q in zip(pts, pts[1:]):
        d = q - p
        t = max(0.0, min(1.0, (c - p).dot(d) / max(d.length_squared, 1e-12)))
        best = min(best, (c - (p + d * t)).length)
    return best


def _bezier(p0, p1, p2, n):
    return [p0 * (1 - t) ** 2 + p1 * 2 * (1 - t) * t + p2 * t * t for t in (i / (n - 1) for i in range(n))]


def _frustum(a, base, axis, r0, r1, h, seed, mat, sides=6):
    """A 6-sided frustum (a collar or a peg) from base along axis: radius r0 at the base, r1 at the far end."""
    rng = random.Random(seed)
    u, v, d = _frame_from(axis)
    ph = rng.uniform(0, 2 * math.pi)
    bm = a.bm
    rings = []
    for z, r in ((0.0, r0), (h, r1)):
        rings.append([bm.verts.new(base + d * z + (u * math.cos(ph + 2 * math.pi * k / sides) +
                                                  v * math.sin(ph + 2 * math.pi * k / sides)) * r
                                   * (1 + rng.uniform(-0.04, 0.04))) for k in range(sides)])
    faces = [bm.faces.new((rings[0][k], rings[0][(k + 1) % sides], rings[1][(k + 1) % sides], rings[1][k]))
             for k in range(sides)]
    faces += _cap(bm, rings[0], flip=True) + _cap(bm, rings[1])
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    vs = rings[0] + rings[1]
    a._finish(vs, mat, tint=1.0)
    return vs


# ---- lobe / clump -------------------------------------------------------------------------------------------------------
LOBE_SQUASH = (1.0, 0.9, 0.85)      # W : D : H of a lobe (its size is its width)
LOBE_TAPER = (0.2, 0.3, 1.3)       # below this unit-sphere height the sides draw in, by up to this much (teardrop)
LOBE_APEX = 1.25                   # the pole lifted this much, linearly down its five facets (see lobe_mesh)
LOBE_FACET = 0.4                   # mid-edge verts pushed this much of the way to the sphere (0 flat .. 1 round)
LOBE_PULLS = (3, 0.1, 0.75)         # broad pulls: count, +- radius fraction, angular reach (radians)
TALL = 0.95                        # H : W of the crown and clump-centre lobes (round 2; the exploded top clump)


def lobe_mesh(bm, centre, size, seed, apex=(0, 0, 1), squash=LOBE_SQUASH, yaw=None):
    """One leaf lobe: an ico-1 subdivided flat (80 triangles, _ico_flat) reshaped into an irregular faceted ovoid with
    big flat facets. Its sides taper into an inverted teardrop below the widest ring, 2-3 broad low pulls break the
    symmetry (never per-vertex noise), and its pole is raised LOBE_APEX into a pointed five-facet apex turned to
    `apex`. The apex lift runs linearly down the five pole facets (each pole-to-ring mid vert gets half of it), so
    those facets stay flat and straight-ridged instead of a small spike. Returns the verts."""
    rng = random.Random(seed)
    vs, mids = _ico_flat(bm, LOBE_FACET)
    pulls = []
    for _ in range(LOBE_PULLS[0]):
        d = Vector((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1) * 0.6)).normalized()
        pulls.append((d, rng.uniform(-LOBE_PULLS[1], LOBE_PULLS[1])))
    t0, amt, ex = LOBE_TAPER
    pole = max(vs, key=lambda v: v.co.z)
    lift = {v: (1.0 if v is pole else 0.5 if pole in mids.get(v, ()) else 0.0) for v in vs}
    for v in vs:
        d = v.co.normalized()
        rad = v.co.length
        r = rad
        for pd, k in pulls:
            r *= 1 + k * math.exp(-(d.angle(pd) / LOBE_PULLS[2]) ** 2)
        xy = 1.0 if d.z > t0 else 1 - amt * ((t0 - d.z) / (1 + t0)) ** ex
        v.co = Vector((d.x * xy * r, d.y * xy * r, d.z * r + (LOBE_APEX - 1.0) * lift[v]))
    w = size / 2
    yaw = rng.uniform(0, 2 * math.pi) if yaw is None else yaw
    sx = squash[0] * rng.uniform(0.95, 1.05)
    sy = squash[1] * rng.uniform(0.95, 1.05)
    sz = squash[2] * rng.uniform(0.95, 1.05)
    rot = Vector((0, 0, 1)).rotation_difference(Vector(apex).normalized()).to_matrix().to_4x4()
    m = (Matrix.Translation(Vector(centre)) @ rot @ Matrix.Rotation(yaw, 4, "Z") @
         Matrix.Diagonal((w * sx, w * sy, w * sz, 1.0)))
    bmesh.ops.transform(bm, matrix=m, verts=vs)
    return vs


CLUMP_PART = dict(
    # exploded "Leaf Clump (x5)": a tall centre lobe, a smaller left lobe set lower and out, a right lobe behind;
    # on one dark collar with a hex peg below. (centre, size, seed, apex, squash z)
    lobes=(((0.0, 0.0, 1.32), 1.9, 17101, (0.12, -0.1, 1.0), TALL),
           ((-0.98, 0.18, 1.08), 1.5, 17102, (-0.6, -0.15, 1.0), 0.85),
           ((0.82, 0.48, 1.18), 1.6, 17103, (0.55, 0.3, 1.0), 0.85)),
    collar=(0.47, 0.25, 0.42, 0.3),     # base z, height, top radius, bottom radius
    peg=(0.0, 0.62, 0.28),              # base z, length, radius
)


PART_MATURITY = (0.5, 0.75, 1.0)    # round 2: was (-0.5, 0, 0.25); the part leaves rendered 22-40 levels lighter than
                                    # the sheet's exploded clumps (#618426)


def clump_part(a):
    """BerryBushLeafClump: the exploded three-lobe clump (lobe x 3, collar, hex peg)."""
    c = CLUMP_PART
    lobes = []
    for k, (ctr, size, seed, apex, sz) in enumerate(c["lobes"]):
        vs = lobe_mesh(a.bm, ctr, size, seed, apex=apex, squash=(1.0, 0.9, sz))
        a._finish(vs, LEAF, tint=1.0)
        lobes.append(dict(verts=vs, centre=Vector(ctr), size=size, maturity=PART_MATURITY[k], name=f"P{k}"))
    z0, h, rt, rb = c["collar"]
    col = _frustum(a, Vector((0, 0, z0)), (0, 0, 1), rb, rt, h, 17104, PEG)
    pz, pl, pr = c["peg"]
    peg = _frustum(a, Vector((0, 0, pz)), (0, 0, 1), pr, pr * 0.96, pl, 17105, PEG)
    if COLOUR[0]:
        for L in lobes:
            paint_lobe(a, L, {"part": True})
        paint_wood(a, col + peg, PEG, mode="peg")
    _scale(a)


# ---- berry ---------------------------------------------------------------------------------------------------------
BERRY_SQUASH = 0.96
BERRY_PEG = (0.17, 0.17)            # peg diameter and length (fractions of the berry's diameter)


def berry_mesh(a, centre, dia, seed, axis=(0, 0, 1), peg=True):
    """One berry: an ico-2 ball (80 triangles, radius jitter under 2 %, squash 0.96 along its axis) and a small
    6-sided brown peg on its axis pole. Returns (ball verts, peg verts)."""
    rng = random.Random(seed)
    bm = a.bm
    vs = _ico(bm, 2)
    for v in vs:
        v.co *= 1 + rng.uniform(-0.018, 0.018)
    rot = Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized()).to_matrix().to_4x4()
    r = dia / 2
    m = (Matrix.Translation(Vector(centre)) @ rot @ Matrix.Rotation(rng.uniform(0, 6.28), 4, "Z") @
         Matrix.Diagonal((r, r, r * BERRY_SQUASH, 1.0)))
    bmesh.ops.transform(bm, matrix=m, verts=vs)
    a._finish(vs, BERRY, tint=1.0)
    pv = []
    if peg:
        d = Vector(axis).normalized()
        base = Vector(centre) + d * (r * BERRY_SQUASH - 0.12 * dia)
        pv = _frustum(a, base, d, BERRY_PEG[0] * dia / 2, BERRY_PEG[0] * dia / 2 * 0.85,
                      BERRY_PEG[1] * dia + 0.12 * dia, seed + 1, BERRY_STEM)
    return vs, pv


def berry_part(a):
    """BerryBushBerry: one 1.0 (sheet) berry with its peg on top."""
    vs, pv = berry_mesh(a, (0, 0, 0.5 * BERRY_SQUASH), 1.0, 17201)
    if COLOUR[0]:
        paint_berry(a, vs, Vector((0, 0, 0.5 * BERRY_SQUASH)), 1.0, Vector((0, 0, 1)), {})
        _tint_mottle(a, pv, 1.0, "wood", 17202)
    _scale(a)


# ---- trunk ---------------------------------------------------------------------------------------------------------
# exploded "Trunk Fork (x1)": a 6-sided trunk (1.4 across at the foot) splitting about 1.3 up into a centre limb
# (about 10 degrees left, to 3.1), a right limb (40 degrees, cut end at 2.8) and a left limb (52 degrees, cut at 2.2);
# limbs 0.8 thick tapering 10 %, flat hex cut ends. (start, tip, radius at start, radius at tip, seed)
FORK = dict(
    trunk=((0.0, 0.0, 0.0), (0.0, 0.0, 1.45), (0.72, 0.66, 0.6), 17301),
    limbs=(((-0.05, 0.02, 1.0), (-0.42, 0.1, 3.1), 0.42, 0.38, 17302),
           ((0.12, -0.02, 1.0), (1.62, 0.25, 2.8), 0.41, 0.37, 17303),
           ((-0.12, -0.05, 1.0), (-1.5, -0.05, 2.25), 0.4, 0.36, 17304)),   # round 2: steeper and not toward the
           # camera (it read 65 deg in the part shot, sheet 50-55)
)


def _limb_pts(p0, p1, step=0.6):
    n = max(2, round((p1 - p0).length / step)) + 1
    return [p0.lerp(p1, i / (n - 1)) for i in range(n)]


def fork_part(a):
    """BerryBushTrunkFork: the exploded fork (trunk + three limbs with pale hex cut ends)."""
    p0, p1, rr, seed = FORK["trunk"]
    p0, p1 = Vector(p0), Vector(p1)
    pts = [p0, p0.lerp(p1, 0.35), p1]
    pieces = []
    vs, _ = _tube(a, pts, list(rr), seed, mat=BARK, bot_mat=BARK)
    pieces.append(vs)
    for q0, q1, r0, r1, sd in FORK["limbs"]:
        q0, q1 = Vector(q0), Vector(q1)
        pts = _limb_pts(q0, q1)
        rad = [r0 + (r1 - r0) * i / (len(pts) - 1) for i in range(len(pts))]
        vs, _ = _tube(a, pts, rad, sd, mat=BARK, top_mat=HEART)
        pieces.append(vs)
    if COLOUR[0]:
        for vs in pieces:
            paint_wood(a, vs, BARK, mode="fork")
    _scale(a)


# ---- hero layout (sheet studs, build frame: front -Y, +X right, ground z 0) ----------------------------------------
# five stems: base (x, y) at the ground, tip (x, y, z); radius at the ground flare, above it, at the tip
STEMS = {
    "S1": ((0.1, 0.05), (-0.1, 0.0, 3.5), 17401),        # centre, to the crown clump
    "S2": ((-0.15, -0.4), (-0.85, -1.2, 1.8), 17402),    # front-left
    "S3": ((0.42, -0.25), (1.25, -0.8, 2.6), 17403),     # front-right (round 2: seats in L9 through L10; base
                                                          # moved 0.06: at (0.45, -0.2) the union left a crossing fin)
    "S4": ((0.56, 0.34), (1.7, 0.6, 2.0), 17404),          # back-right
    "S5": ((-0.35, 0.25), (-1.75, 0.6, 2.05), 17405),    # back-left
}
STEM_R = (0.38, 0.32, 0.24)
FOOT_PLUG = ((0.14, -0.04, -0.35), 0.45, 0.36, 0.65)   # base centre, radius at base / top, height (sheet studs)
STEM_Z0 = -0.2          # stems start below the ground; the floor cut makes the foot flat
STEM_BEND = 0.45        # the stems rise steeply from the foot and bend outwards (control point height fraction)

# fifteen lobes in five clumps: name -> (clump, centre (x, y, z), width, maturity -1 young .. +1 old, seed, apex tilt
# (x, y) added to straight up + the outward direction)
# Stage 1 round 2 (against the first renders): every lobe about 8 % bigger (the canopy was porous: berries showed
# through from the opposite side, and stems and collars between the lobes up to mid-height); the two low side lobes
# moved out of the side view's centre (the sheet's side shows no leaf below h 0.35 at mid depth): L6 to the back-left,
# L12 to the back-right, where the rear view's low lobes are; the crown's right lobe lower (front top profile).
# Round 2 (faceted lobes with a raised apex; stems must show): the crown lower (the apex adds height); the low lobes
# that hid the stems raised or moved aside: L5 smaller, left and up and L7 up (f34 centre gap), L4 forward out of the
# side view's mid depth (it now sits where the sheet's side shows leaf to h 0.1), L6 / L12 up (rear and r34 lower
# corners), L11 a little up; L8, L9 lower / inward so clump C3 touches the crown; L10 up a little.
LOBES = {
    "L1": ("C1", (-0.4, -0.15, 3.7), 2.15, -0.5, 17501, (0.35, 0.0)),
    "L2": ("C1", (0.55, 0.55, 3.9), 1.4, -0.5, 17502, None),
    "L3": ("C1", (-1.85, -0.35, 3.0), 1.45, 0.0, 17503, None),
    "L5": ("C2", (-1.4, -1.0, 1.85), 1.9, -0.5, 17505, None),
    "L7": ("C2", (-1.2, -0.85, 1.25), 0.85, 0.5, 17507, None),
    "L8": ("C3", (0.5, -0.95, 3.2), 1.4, -0.5, 17508, None),
    "L9": ("C3", (1.35, -0.8, 3.4), 1.5, 0.0, 17509, None),
    "L10": ("C3", (1.45, -1.2, 1.8), 1.6, -0.5, 17510, None),
    "L11": ("C4", (2.1, 0.3, 2.45), 1.8, 0.5, 17511, None),
    "L12": ("C4", (2.35, 1.4, 2.3), 1.4, 0.5, 17512, None),
    "L13": ("C4", (1.35, 1.1, 3.45), 1.5, 0.0, 17513, None),
    "L14": ("C4", (1.05, 1.8, 2.85), 1.6, 0.0, 17514, None),
    "L4": ("C5", (-2.2, -0.45, 1.95), 1.55, 0.5, 17504, None),
    "L6": ("C5", (-1.8, 1.75, 2.0), 1.35, 0.5, 17506, None),
    "L15": ("C5", (-1.25, 1.3, 2.8), 2.0, 0.0, 17515, None),
}
# the drawn widths are the lobes' silhouettes on the sheet; a lobe's mesh is narrower than its nominal size in depth
# and height (0.9, 0.85) and tapers below, so at the drawn sizes most lobes did not even touch their neighbours (a
# contact graph of the pieces showed eleven separate groups): all lobes grow by this much
LOBE_GROW = 1.18
# round 2: the crown and each clump's centre (upper) lobe stand taller (H about 0.97 W), as the exploded top clump
TALL_LOBES = {"L1", "L2", "L8", "L9", "L13", "L15"}
CLUMP_STEM = {"C1": "S1", "C2": "S2", "C3": "S3", "C4": "S4", "C5": "S5"}
BUSH_CENTRE = Vector((0.0, 0.1, 2.4))
APEX_OUT = 0.5          # lobe apex = up + this x the horizontal outward direction (a little off centre, outwards)

# eight berries, each placed where the sheet's view that shows it best draws it: name -> (view, u, z, diameter, seed).
# The berry is cast straight in from that view at (u, z) - u is x for the front and rear, y for the side (camera at
# +X) - onto the canopy and sunk BERRY_SINK of its diameter into it (stage 1, round 4: centres typed in 3D left the
# berries either buried by the grown lobes or floating; positions from the study's berry components, section 1.3)
# (view, u, z, diameter, seed, sink): sink overrides BERRY_SINK. "at" places a berry at a fixed centre u = (x, y, z)
# and pushes it along z (a direction; None: towards BERRY_CORE) until it is held.
# Round 5 (measured against the sheet's front components): B1, B2, B3, B4 nudged to the sheet's (f, h); B3 sits at a
# fixed point in front of the centre stem (dropped from the front it fell into the stem gap, 0.4 back, and vanished
# from the side view, where the sheet shows it standing out of the front silhouette); B4 deeper (it showed over the
# crown in the side view); B5 / B6 further forward (the front shows both at the right edge, partly hidden).
BERRIES = {
    "B1": ("front", -1.85, 2.55, 0.9, 17601, None),
    "B2": ("front", -1.05, 3.13, 0.95, 17602, None),
    "B3": ("at", (0.15, -2.05, 2.75), None, 0.95, 17603, 0.15),
    "B4": ("at", (1.0, -1.0, 3.95), (0.0, 1.0, -0.2), 0.95, 17604, 0.3),
    # verifier round 2: B5 / B6 came forward (they hid behind the right lobes in the front and f34 and showed as
    # extra berries from the rear); the push directions and sink are unchanged
    "B5": ("at", (2.4, 0.3, 3.3), (-1.0, 0.0, -0.5), 0.95, 17605, 0.25),
    "B6": ("at", (2.7, 0.0, 1.75), (-0.6, 0.3, 0.6), 0.9, 17606, 0.25),
    "Bk1": ("at", (0.0, 1.7, 2.4), (0.0, -0.8, 0.3), 0.95, 17607, 0.2),   # round 2: between L14 and L15
    "Bk2": ("rear", -1.4, 3.45, 0.9, 17608, None),
}
CAST = {"front": Vector((0, 1, 0)), "rear": Vector((0, -1, 0)), "side": Vector((-1, 0, 0))}
COLLAR = (0.42, 0.3, 0.26)      # top radius, bottom radius, height (sheet studs)


def _apex(ctr, tilt):
    h = Vector((ctr[0] - BUSH_CENTRE.x, ctr[1] - BUSH_CENTRE.y, 0.0))
    out = h.normalized() * min(1.0, h.length / 1.2) if h.length > 1e-6 else Vector()
    v = Vector((0, 0, 1)) + out * APEX_OUT
    if tilt:
        v += Vector((tilt[0], tilt[1], 0.0))
    return v.normalized()


BERRY_CORE = Vector((0.0, 0.1, 2.6))
BERRY_SINK = 0.3        # each berry sunk this fraction of its diameter into the canopy (spec 6: 25-35 %)
SINK_REACH = 0.6        # ... moving it at most this far along its axis from its drawn centre


BERRY_HOLD = 0.25


def _surface_dist(tree, p):
    """Signed distance from p to the surfaces in tree (negative inside)."""
    dist = tree.find_nearest(p)[3]
    return -dist if _inside(tree, p) else dist


def _drop(tree, far, d, dia):
    """Move a berry (a ball of diameter dia) from far along d until it first touches the surfaces in tree: rays across
    its disc (centre and two rings) give the first contact. Returns the centre's distance from far, or None."""
    r = dia / 2
    u, v, _ = _frame_from(d)
    best = None
    for k, rho in ((1, 0.0), (8, 0.5), (12, 0.88)):
        for i in range(k):
            t = 2 * math.pi * i / k
            o = (u * math.cos(t) + v * math.sin(t)) * rho * r
            h = tree.ray_cast(far + o, d, 20.0)
            if h[0] is None:
                continue
            c = h[3] - math.sqrt(max(0.0, r * r - (rho * r) ** 2))
            best = c if best is None else min(best, c)
    return best


def _sink(tree, ctr, axis, dia):
    """Slide a berry along its axis (outside -> in, towards its stem tip) until BERRY_SINK of its diameter lies inside
    the canopy along that line: the canopy surface hit from outside, then back out by (0.5 - BERRY_SINK) x dia.
    Returns (centre, how far it moved)."""
    hit = tree.ray_cast(ctr - axis * 4.0, axis, 8.0)[0]
    if hit is None:
        return ctr, 0.0
    new = hit - axis * (0.5 - BERRY_SINK) * dia
    if (new - ctr).length > SINK_REACH:
        new = ctr + (new - ctr).normalized() * SINK_REACH
    return new, (new - ctr).dot(axis)


TIP_DEPTH = 0.35        # each stem runs at least this far into its clump (spec 6)


def _seat(name, tree, lobes):
    """The stem's points with its tip moved (towards the nearest lobe centre of its clump) until the stem runs
    TIP_DEPTH into the clump; the drawn tips are starting values."""
    tip = Vector(STEMS[name][1])
    ctr = min((L["centre"] for L in lobes), key=lambda c: (c - tip).length)
    for k in range(21):
        t = tip.lerp(ctr, k * 0.05)
        pts = stem_points(name, t)
        if _entry(tree, pts)[1] >= TIP_DEPTH:
            break
    INFO.setdefault("tips", {})[name] = [round(x, 2) for x in pts[-1]]
    return pts


def stem_points(name, tip=None):
    (bx, by), tip0, _ = STEMS[name]
    tip = Vector(tip if tip is not None else tip0)
    # each stem starts at its own depth: five nearly coplanar bottom caps overlapping at the foot made one exact union
    # throw most of the hero away (stage 1, round 2)
    p0 = Vector((bx, by, STEM_Z0 - 0.09 * list(STEMS).index(name)))
    p1 = Vector((bx + (tip.x - bx) * 0.2, by + (tip.y - by) * 0.2, tip.z * STEM_BEND))
    n = max(4, round((tip - p0).length / 0.55)) + 1
    return _bezier(p0, p1, tip, n)


def stem_radii(pts):
    out = []
    for i, p in enumerate(pts):
        t = i / (len(pts) - 1)
        r = STEM_R[1] + (STEM_R[2] - STEM_R[1]) * t
        if p.z < 0.35:
            r = STEM_R[0] + (STEM_R[1] - STEM_R[0]) * max(0.0, p.z) / 0.35
        out.append(r)
    return out


INFO = {}


def hero(a):
    """BerryBushNode: trunk (five stems), five clumps (fifteen lobes, a collar where each stem enters), eight berries."""
    lobes = []
    for name, (clump, ctr, size, mat_, seed, tilt) in LOBES.items():
        sq = (LOBE_SQUASH[0], LOBE_SQUASH[1], TALL) if name in TALL_LOBES else LOBE_SQUASH
        vs = lobe_mesh(a.bm, ctr, size * LOBE_GROW, seed, apex=_apex(ctr, tilt), squash=sq)
        a._finish(vs, LEAF, tint=1.0)
        lobes.append(dict(name=name, clump=clump, verts=vs, centre=Vector(ctr), size=size * LOBE_GROW,
                          maturity=mat_))
    stems = {}
    trees = {c: K.bvh_of([v for L in lobes if L["clump"] == c for v in L["verts"]]) for c in CLUMP_STEM}
    for name in STEMS:
        c = next(k for k, v in CLUMP_STEM.items() if v == name)
        pts = _seat(name, trees[c], [L for L in lobes if L["clump"] == c])
        vs, top = _tube(a, pts, stem_radii(pts), STEMS[name][2], mat=BARK)   # tips hidden in the clumps: no cut face
        stems[name] = dict(verts=vs, pts=pts)
    # round 2: a low hex plug fills the inner V-creases between the stems at the ground, so the floor cut slices one
    # solid foot (the thin creases there collapsed into pinholes that _seal's fan fill closed with inverted fins);
    # the creases above it and the outer ones stay as grooves
    plug = _frustum(a, Vector(FOOT_PLUG[0]), (0, 0, 1), FOOT_PLUG[1], FOOT_PLUG[2], FOOT_PLUG[3], 17450, BARK)
    # collars: where each stem's axis leaves its clump's lobes (marched back down the stem from the tip)
    collars = {}
    for c, s in CLUMP_STEM.items():
        tree = K.bvh_of([v for L in lobes if L["clump"] == c for v in L["verts"]])
        pts = stems[s]["pts"]
        entry, depth = _entry(tree, pts)
        d = (pts[-1] - pts[-2]).normalized()
        col = _frustum(a, entry - d * (COLLAR[2] * 0.5), d, COLLAR[1], COLLAR[0], COLLAR[2], _seed(c), PEG)
        collars[c] = dict(verts=col, entry=entry, depth=round(depth, 3))
    berries = []
    canopy = K.bvh_of([v for L in lobes for v in L["verts"]] + [v for st in stems.values() for v in st["verts"]])
    for name, (view, u, z, dia, seed, sink) in BERRIES.items():
        if view == "at":
            ctr = Vector(u)
            axis = (Vector(z) if z is not None else BERRY_CORE - ctr).normalized()
            pushed = 0.0
            hold = BERRY_HOLD if sink is None else sink
            while pushed < 1.0 and dia / 2 - _surface_dist(canopy, ctr) < hold * dia:
                ctr += axis * 0.03
                pushed += 0.03
            INFO.setdefault("berries", {})[name] = ([round(x, 2) for x in ctr], "fixed", round(pushed, 2))
        else:
            d = CAST[view]
            far = (Vector((u, -6.0, z)) if view == "front" else Vector((u, 6.0, z)) if view == "rear"
                   else Vector((6.0, u, z)))
            sink = BERRY_SINK if sink is None else sink
            c = _drop(canopy, far, d, dia)
            ctr = far + d * ((c if c is not None else 6.0) + sink * dia)
            axis = d      # the peg points straight into the canopy, away from the view that shows the berry
            # a berry that met the canopy only at its rim (a lobe's edge) is barely held: push it on in until it is
            # sunk at least BERRY_HOLD of its diameter (the depth of the canopy surface's nearest point inside it)
            pushed = 0.0
            while pushed < 1.0 and dia / 2 - _surface_dist(canopy, ctr) < BERRY_HOLD * dia:
                ctr += d * 0.03
                pushed += 0.03
            INFO.setdefault("berries", {})[name] = ([round(x, 2) for x in ctr], c is not None, round(pushed, 2))
        vs, pv = berry_mesh(a, ctr, dia, seed, axis=axis)
        berries.append(dict(name=name, verts=vs, peg=pv, centre=ctr, dia=dia, axis=axis))
    INFO.update(collars={c: (list(v["entry"]), v["depth"]) for c, v in collars.items()})
    if COLOUR[0]:
        ctx = {"berries": berries, "tips": [st["pts"][-1] for st in stems.values()],
               "entries": [c["entry"] for c in collars.values()]}
        for L in lobes:
            paint_lobe(a, L, ctx)
        for b in berries:
            paint_berry(a, b["verts"], b["centre"], b["dia"], b["axis"], ctx)
            _tint_mottle(a, b["peg"], 1.0, "wood", 17690)
        for name, st in stems.items():
            paint_wood(a, st["verts"], BARK, mode="stem", ctx={"stems": stems, "me": name})
        paint_wood(a, plug, BARK, mode="stem", ctx={"stems": stems, "me": None})
        for c in collars.values():
            paint_wood(a, c["verts"], PEG, mode="peg")
    _scale(a)


def _scale(a):
    bmesh.ops.scale(a.bm, vec=(S, S, S), verts=a.bm.verts)


# ---- stage 4: colour by position fields (never facing) ------------------------------------------------------------
STEPS = 4                       # 0.25 steps on each side of the leaf ladder
CANOPY = dict(hi=(4.0, 0.3), lo=(1.3, 0.4), band=0.5, noise=0.15, scale=0.6, seed=17701)
UNDER = (0.3, 0.25)             # the lowest 30 % of a lobe's height -> +0.25 towards old
CONTACT = dict(berry=(0.25, 0.5), stem=(0.3, 0.5))
MOTTLE = {"leaf": dict(amp=0.035, scale=0.5, jitter=0.006), "bark": dict(amp=0.05, scale=0.35, jitter=0.006),
          "berry": dict(amp=0.02, scale=0.9, jitter=0.004), "wood": dict(amp=0.04, scale=0.6, jitter=0.006)}
PIECE_TINT = 0.04


def _q(t, steps=STEPS):
    return round(max(-1.0, min(1.0, t)) * steps) / steps


def leaf_key(v):
    """The leaf ladder: -1 young .. 0 leaf .. +1 old, in quarter steps."""
    v = _q(v)
    if v < 0:
        return K.mix_key(LEAF, LEAF_YOUNG, -v)
    return K.mix_key(LEAF, LEAF_OLD, v)


def _tint_mottle(a, verts, level, kind, seed):
    m = MOTTLE[kind]
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in K.faces_of(verts):
        c = f.calc_center_median()
        k = level * (1.0 + m["amp"] * 1.6 * noise.noise(c * m["scale"] + off) + rng.uniform(-m["jitter"], m["jitter"]))
        for l in f.loops:
            l[a.tint_layer] = (k, k, k, 1.0)


def paint_lobe(a, L, ctx):
    """One lobe on the leaf ladder: its maturity, the canopy height field (crown younger, low lobes older; broad noise
    on z so it is no band), the lobe's own lowest 30 % a little older, older where it touches a berry or where a stem
    enters. Tint: the lobe's level x broad mottling."""
    vs = L["verts"]
    zs = [v.co.z for v in vs]
    z0, z1 = min(zs), max(zs)
    nf = K.noise_field(scale=CANOPY["scale"], seed=CANOPY["seed"])
    rng = random.Random(_seed(L["name"]))
    for f in K.faces_of(vs):
        c = f.calc_center_median()
        v = L["maturity"]
        if not ctx.get("part"):
            z = c.z + CANOPY["noise"] * 2 * nf(c)
            hz, hv = CANOPY["hi"]
            lz, lv = CANOPY["lo"]
            v -= hv * min(1.0, max(0.0, (z - (hz - CANOPY["band"] / 2)) / CANOPY["band"]))
            v += lv * min(1.0, max(0.0, ((lz + CANOPY["band"] / 2) - z) / CANOPY["band"]))
        rel = (c.z - z0) / max(z1 - z0, 1e-6)
        if rel < UNDER[0]:
            v += UNDER[1] * (1 - rel / UNDER[0])
        for b in ctx.get("berries", ()):
            d = (c - b["centre"]).length - b["dia"] / 2
            if d < CONTACT["berry"][0]:
                v = max(v, CONTACT["berry"][1])
        for p in ctx.get("entries", ()):
            if (c - p).length < CONTACT["stem"][0] + COLLAR[0]:
                v = max(v, CONTACT["stem"][1])
        f.material_index = a._mi(leaf_key(v))
    _tint_mottle(a, vs, 1.0 + rng.uniform(-PIECE_TINT, PIECE_TINT), "leaf", 17710 + rng.randint(0, 99))


def paint_berry(a, vs, centre, dia, axis, ctx):
    """Berry body; the third of its faces nearest the peg (the side in the canopy) grades to berry_deep."""
    rng = random.Random(int(centre.x * 100 + centre.y * 10 + centre.z))
    for f in K.faces_of(vs):
        c = f.calc_center_median()
        u = (c - centre).dot(axis) / (dia / 2)      # -1 far side .. +1 at the peg
        t = min(1.0, max(0.0, (u - 0.05) / 0.8))
        t = round(t * 3) / 3
        f.material_index = a._mi(K.mix_key(BERRY, BERRY_DEEP, t))
    _tint_mottle(a, vs, 1.0 + rng.uniform(-PIECE_TINT * 0.5, PIECE_TINT * 0.5), "berry", 17720)


BARK_FIELD = dict(z=((1.6, 0.5), (2.2, 0.75)), crease=(0.12, 0.5), foot=(0.5, 1.1), noise=0.6, level=0.3,
                  seed=17730)


def paint_wood(a, vs, base, mode="stem", ctx=None):
    """Bark: darker up under the canopy (z), in the V-creases between stems and at the ground, broad noise patches
    along each stem; heartwood cut faces stay. Pegs and collars: one dull key with mottling."""
    nf = K.noise_field(scale=BARK_FIELD["noise"], seed=BARK_FIELD["seed"])
    heart = a._mi(HEART)
    for f in K.faces_of(vs):
        if f.material_index == heart:
            continue
        c = f.calc_center_median()
        if mode == "peg":
            f.material_index = a._mi(PEG)
            continue
        t = 0.0
        if mode == "stem" and c.z < BARK_FIELD["foot"][1]:
            # round 2: the foot is the lightest bark on the sheet in every view (#835A34 at h 0-0.1, darker up under
            # the canopy): bark_light at the foot grading to bark by thirds, no ground darkening, creases or patches
            z0, z1 = BARK_FIELD["foot"]
            k = round(min(1.0, max(0.0, (c.z - z0) / (z1 - z0))) * 3) / 3
            f.material_index = a._mi(K.mix_key(BARK_LIGHT, BARK, k))
            continue
        if mode == "stem":
            for z, k in BARK_FIELD["z"]:
                if c.z > z:
                    t = max(t, k)
            me = ctx["me"]
            for n, st in ctx["stems"].items():
                if n == me or c.z > 1.0:
                    continue
                d = _dist_poly(c, st["pts"]) - STEM_R[1]
                if d < BARK_FIELD["crease"][0]:
                    t = max(t, BARK_FIELD["crease"][1])
        nv = nf(c)
        if nv > BARK_FIELD["level"]:
            t = max(t, 0.25 if nv < BARK_FIELD["level"] + 0.15 else 0.5)
        t = round(t * 4) / 4
        f.material_index = a._mi(K.mix_key(BARK, BARK_DARK, t))
    _tint_mottle(a, vs, 1.0, "bark" if mode != "peg" else "wood", 17740)


# ---- cleanup ------------------------------------------------------------------------------------------------------
def _volume(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    v = bm.calc_volume(signed=True)
    bm.free()
    return v


NUDGES = ((0, 0, 0), (0.02, 0.014, -0.006), (0.04, 0.028, -0.012), (-0.04, 0.03, 0.02), (0.03, -0.04, 0.03),
          (0.06, 0.04, -0.02))


def _union(o, tries=len(NUDGES)):
    """M.union_loose, guarded: each shell is unioned on with an exact boolean, and the result is checked against the
    volumes going in (an exact union that loses track of inside/outside throws most of the mesh away: one collar
    did that in stage 1, round 2, and stem S4 later: it failed at nudges up to 0.02 and passed at 0.04). A bad
    result is undone and the shell retried nudged by NUDGES (a few hundredths of a stud, far below what reads); a shell that still fails is reported (build() lists it under "union") and left
    out. Then union_loose's merge / repair pass. Returns
    {"shells": n, "retried": [...], "failed": [...]}."""
    act = bpy.context.view_layer.objects.active
    if act and act.mode != "OBJECT":
        with bpy.context.temp_override(active_object=act, object=act):
            bpy.ops.object.mode_set(mode="OBJECT")
    others = M.split_loose(o)
    retried, failed = [], []
    rng = random.Random(17900)
    for i, p in enumerate(others):
        v0, vp = _volume(o.data), _volume(p.data)
        home = p.matrix_world.copy()
        ok = False
        for t in range(tries):
            keep = o.data.copy()
            if t:
                p.matrix_world = Matrix.Translation(Vector(NUDGES[min(t, len(NUDGES) - 1)])) @ home
            m = o.modifiers.new("U", "BOOLEAN")
            m.operation, m.solver, m.object = "UNION", "EXACT", p
            m.material_mode = "TRANSFER"
            with M._override(o):
                bpy.ops.object.modifier_apply(modifier=m.name)
            v1 = _volume(o.data)
            if v1 >= max(v0, vp) * 0.995 and v1 <= (v0 + vp) * 1.005:
                ok = True
                bpy.data.meshes.remove(keep)
                if t:
                    retried.append((i, t))
                break
            old = o.data
            o.data = keep
            bpy.data.meshes.remove(old)
        if not ok:
            failed.append(i)
        bpy.data.objects.remove(p, do_unlink=True)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=0.01)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    M.drop_specks(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    K.drop_unused_slots(o)
    return {"shells": len(others) + 1, "retried": retried, "failed": failed}


def _bottom_centre(o):
    return m011._bottom_centre(o)


def _fix_floor(o):
    """Faces the floor cut made (flat, facing down at z 0): plain bark (round 2: no darkening at the foot), Tint 1."""
    p = m011._Paint(o, off=(0, 0, 0))
    lay = p.tint_layer
    for f in p.bm.faces:
        if f.normal.z < -0.99 and abs(f.calc_center_median().z) < 1e-3:
            f.material_index = p._mi(BARK)
            for l in f.loops:
                l[lay] = (0.95, 0.95, 0.95, 1.0)
    p.done()


def _finish(o):
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
        res = M.finish(o, union=False, uv=UV)
    return res


def _loops(edges):
    """Boundary edges -> closed vertex loops (in order)."""
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
    """Fill each boundary loop with a triangle fan from a corner none of whose diagonals already exist as an edge
    (holes_fill gives up on a pinhole whose other diagonal is already an edge of the surface). Returns faces made."""
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
    """Close any small hole the sliver collapses opened (a 4-edge pinhole by B3 in stage 1): fill boundary loops,
    split them into triangles, repair edges on more than two faces, and open any new sliver. Returns holes filled."""
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
    split = m012._tri_quads(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = m012._force_slivers(o, lim=POLISH_LIM)
    sealed = _seal(o)
    inverted = []
    for _ in range(4):
        # round 2: _seal's fan fill once left a thin inside-out fin in a stem crease (3 faces) and a one-face
        # micro-pocket; delete every face whose front side is solid, then re-seal
        bad = _inverted(o)
        if not bad:
            break
        inverted.append(len(bad))
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.faces[i] for i in bad], context="FACES")
        bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bm.to_mesh(o.data)
        bm.free()
        sealed += _seal(o)
        m012._force_slivers(o, lim=POLISH_LIM)
    bc = _bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
    o.data.update()
    M.smart_uv(o, **UV)
    return {"split": split, "forced": forced, "sealed": sealed, "inverted": inverted, "uv_cut": m012._uv_unfold(o)}


PARITY_DIRS = tuple(Vector(d).normalized() for d in ((0.31, 0.17, 0.93), (-0.77, 0.41, 0.29), (0.13, -0.88, -0.35),
                                                      (0.62, 0.55, -0.48), (-0.29, -0.36, 0.87)))


def _inverted(o, eps=2e-3):
    """Faces whose front side is solid (inside-out or interior faces): a point eps in front of the face's centre is
    inside the mesh by a majority of five ray-parity tests. Returns face indices."""
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.normal_update()
    tree = BVHTree.FromBMesh(bm)
    out = []
    for f in bm.faces:
        if f.calc_area() < 1e-10:
            continue
        p = f.calc_center_median() + f.normal * eps
        if sum(_inside(tree, p, d) for d in PARITY_DIRS) >= 3:
            out.append(f.index)
    bm.free()
    return out


def _clean_mesh(o, planes=(0.0,)):
    pockets = m012._drop_inner(o)
    log = m011._clean(o, m011._plane_lock(planes), max_move=m011.CLEAN_MOVE)
    pockets += m012._drop_inner(o)
    log["pockets"] = pockets
    log["forced"] = m012._force_slivers(o)
    return log


def _shell_report(o):
    """Each closed shell of o: triangles and centre (studs), largest first."""
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


PARTS = (("BerryBushTrunkFork", fork_part), ("BerryBushLeafClump", clump_part), ("BerryBushBerry", berry_part))
HERO = "BerryBushNode"
NOTES = {
    HERO: "berry bush forage node: five faceted brown stems splaying from one fused foot, fifteen faceted leaf lobes in "
          "five clumps, eight glossy red berries half-sunk between the lobes; one closed mesh, flat base",
    "BerryBushTrunkFork": "Trunk Fork (reusable): a 6-sided trunk splitting into three limbs with pale hex cut ends",
    "BerryBushLeafClump": "Leaf Clump (reusable): three faceted leaf lobes on a dark hex collar with a hex peg",
    "BerryBushBerry": "Berry (reusable): a round faceted glossy red berry with a small brown peg",
}


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    objs, cleaned = {}, {}
    for name, fn in PARTS:
        o = M.mk(SHEET, name, fn, subject=TITLE, role="part", notes=NOTES[name], budget=1000, collision="hull",
                 tint_var=0.0)
        un = _union(o)
        cleaned[name] = _clean_mesh(o)
        cleaned[name]["union"] = un
        _finish(o)
        cleaned[name]["polish"] = _polish(o)
        objs[name] = o
    h = M.mk(SHEET, HERO, hero, subject=TITLE, role="hero", notes=NOTES[HERO], budget=4000, collision="hull",
             tint_var=0.0)
    hoff = M._build_offset(hero)
    un = _union(h)
    m004.floor_cut(h, z0=-hoff.z)
    _fix_floor(h)
    cleaned[HERO] = _clean_mesh(h)
    cleaned[HERO]["union"] = un
    _finish(h)
    cleaned[HERO]["polish"] = _polish(h)
    order = [h] + [objs[n] for n, _ in PARTS]
    _restyle()
    M.display(NUM, order, TITLE)
    dropped = _drop_unused(order)
    out = {"audit": [{k: M.audit(o)[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges",
                                                     "boundary_edges", "normals", "ngons", "dup_verts")}
                     for o in order],
           "thin": {o.name: m012._thin(o, POLISH_LIM) for o in order}, "cleaned": cleaned, "dropped": dropped,
           "problems": K.check(order), "shading": {o.name: o.get("kit_baked_shading") for o in order},
           "collars": INFO.get("collars"), "tips": INFO.get("tips"), "berries": INFO.get("berries"),
           "shells": {o.name: _shell_report(o) for o in order}, "union": {k: v.get("union") for k, v in cleaned.items()}}
    out["self_hits"] = {o.name: _self_hits(o) for o in order}
    out["inverted"] = {o.name: len(_inverted(o)) for o in order}
    out["problems"] += [f"{a_['name']}: {a_['shells']} shells" for a_ in out["audit"] if a_["shells"] != 1]
    out["problems"] += [f"{n}: {c} faces with solid in front" for n, c in out["inverted"].items() if c]
    out["problems"] += [f"{n}: {c} crossing face pairs {w}" for n, (c, w) in out["self_hits"].items() if c]
    out["problems"] += [f"{n}: union left out shells {v['union']['failed']}" for n, v in cleaned.items()
                        if v.get("union", {}).get("failed")]
    if render:
        out["views"] = render_views(order)
    return out


def _drop_unused(objs):
    names = {o.name for o in objs}
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.split(".")[0] in names]
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m017_")]
    out = {"meshes": len(meshes), "materials": len(mats)}
    for m in meshes:
        bpy.data.meshes.remove(m)
    for m in mats:
        bpy.data.materials.remove(m)
    for o in objs:
        if o.data.name != o.name and o.name not in bpy.data.meshes:
            o.data.name = o.name
    return out


# ---- renders ------------------------------------------------------------------------------------------------------
SHEET_VIEWS = {"front_sheet": (0, 8), "side_sheet": (90, 8), "rear_sheet": (180, 8), "f34_sheet": (-20, 14),
               "r34_sheet": (160, 14), "top_tilt": (0, 70)}


# exploded shot, as the sheet lays it out (sheet studs from the fork's foot, x right, z up, measured on the sheet at
# 58 px per stud): five clump copies round and above the fork, their pegs aimed at the fork, four berry copies
EXPL_CLUMPS = ((0.5, 0.0, 5.7), (-3.2, 0.3, 3.9), (-0.9, -0.2, 4.0), (1.9, -0.3, 3.7), (4.3, 0.2, 2.5))
EXPL_BERRIES = ((-2.5, -0.3, 5.7), (-2.2, -0.5, 2.6), (3.2, 0.0, 5.4), (4.3, -0.4, 4.2))
EXPL_AIM = Vector((0.0, 0.0, 2.4))


def render_views(objs):
    h, fork, clump, berry = objs
    saved = M.explode(objs[1:], {})
    shown = []
    try:
        x0, y0 = h.location.x + 40, h.location.y
        base = Vector((x0, y0, 0.0))
        fork.location = base
        clump.location = base + Vector((0, 30, 0))     # the parts' own shots below show them alone
        berry.location = base + Vector((8, 30, 0))
        for k, p in enumerate(EXPL_CLUMPS):
            c = bpy.data.objects.new(f"_m017_expl_clump{k}", clump.data)
            clump.users_collection[0].objects.link(c)
            p = Vector(p) * S
            d = (EXPL_AIM * S - p).normalized()
            rot = Vector((0, 0, -1)).rotation_difference(d).to_matrix().to_4x4() if d.z < 0.98 else Matrix()
            c.matrix_world = Matrix.Translation(base + p) @ rot
            shown.append(c)
        for k, p in enumerate(EXPL_BERRIES):
            c = bpy.data.objects.new(f"_m017_expl_berry{k}", berry.data)
            berry.users_collection[0].objects.link(c)
            c.matrix_world = Matrix.Translation(base + Vector(p) * S)
            shown.append(c)
        bpy.context.view_layer.update()
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        extra["exploded"] = ([fork] + shown, -16, 18)
        for o in objs[1:]:
            extra["part_" + o.name[9:].lower()] = ([o], -25, 18)
        return M.views(NUM, [h], extra=extra)
    finally:
        for c in shown:
            bpy.data.objects.remove(c, do_unlink=True)
        M.restore(saved)
        M.display(NUM, objs, TITLE)


# ---- measuring (same masks as the study's m.py, numpy) -------------------------------------------------------------
REF_VIEWS = {"f34": (25, 130, 525, 478), "r34": (530, 130, 1000, 478), "front": (22, 535, 285, 752),
             "side": (290, 535, 510, 752), "rear": (515, 535, 765, 752), "top": (772, 535, 1010, 752)}
OUR_VIEWS = {"front": "front_sheet", "side": "side_sheet", "rear": "rear_sheet", "f34": "f34_sheet",
             "r34": "r34_sheet", "top": "top_tilt"}


def _classes(px):
    """px: (h, w, 3) sRGB 0-255, top row first -> uint8 class map 0 none, 1 L, 2 B, 3 T, 4 O."""
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    mx, mn = px.max(-1), px.min(-1)
    v = mx / 255.0
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    d = np.maximum(mx - mn, 1e-6)
    hh = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    paper = (np.abs(px - np.array([242, 237, 230])).max(-1) <= 14)
    out = np.full(r.shape, 4, np.uint8)
    out[v >= 0.88] = 0
    T = (s >= 0.18) & (hh > 12) & (hh < 55) & (v < 0.85)
    L = (s >= 0.25) & (hh >= 55) & (hh <= 110) & (g > 60)
    B = (s >= 0.35) & ((hh >= 340) | (hh <= 12)) & (r > 90)
    out[T] = 3
    out[L] = 1
    out[B] = 2
    out[paper] = 0
    return out


def _load(path, box=None):
    px = K.NS["KIT"]["load_px"](path)[::-1, :, :3] * 255.0      # top row first
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1]
    return np.clip(px, 0, 255)


def _comps(mask, minn):
    """Connected components (4-neighbour) of a bool mask with at least minn pixels: list of (cx, cy, w, h, n)."""
    seen = np.zeros(mask.shape, bool)
    out = []
    H, W = mask.shape
    ys, xs = np.nonzero(mask)
    for y, x in zip(ys, xs):
        if seen[y, x]:
            continue
        st = [(y, x)]
        seen[y, x] = True
        pts = []
        while st:
            q = st.pop()
            pts.append(q)
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = q[0] + dy, q[1] + dx
                if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    st.append((yy, xx))
        if len(pts) >= minn:
            a = np.array(pts)
            out.append(((a[:, 1].min() + a[:, 1].max()) / 2, (a[:, 0].min() + a[:, 0].max()) / 2,
                        a[:, 1].max() - a[:, 1].min(), a[:, 0].max() - a[:, 0].min(), len(pts)))
    return out


def stats(px):
    """Silhouette bbox, W:H, L/B/T shares, top / leaf-bottom profiles (21 columns), width per height (11 rows),
    berry components (centre f, h; width / H)."""
    c = _classes(px)
    obj = (c == 1) | (c == 2) | (c == 3)
    cols = np.nonzero(obj.sum(0) >= 3)[0]
    rows = np.nonzero(obj.sum(1) >= 3)[0]
    bx0, bx1, by0, by1 = cols.min(), cols.max(), rows.min(), rows.max()
    W, H = bx1 - bx0, by1 - by0
    sub = c[by0:by1 + 1, bx0:bx1 + 1]
    n = max(1, ((sub == 1) | (sub == 2) | (sub == 3)).sum())
    out = {"wh": round(W / H, 3), "L": round((sub == 1).sum() / n, 3), "B": round((sub == 2).sum() / n, 3),
           "T": round((sub == 3).sum() / n, 3)}
    top, lb = [], []
    for i in range(21):
        x = bx0 + int(i * W / 20)
        colm = obj[:, max(0, x - 1):x + 2].any(1)
        ys = np.nonzero(colm)[0]
        top.append(round((by1 - ys.min()) / H, 2) if len(ys) else None)
        lm = (c[:, max(0, x - 1):x + 2] == 1).any(1)
        ys = np.nonzero(lm)[0]
        lb.append(round((by1 - ys.max()) / H, 2) if len(ys) else None)
    wid = []
    for i in range(11):
        y = by1 - int(i * H / 10)
        xs = np.nonzero(obj[y])[0]
        wid.append((round((xs.max() - xs.min()) / W, 2), round((xs.min() - bx0) / W, 2)) if len(xs) else None)
    out.update(top=top, leafbot=lb, width=wid)
    pxs = px[by0:by1 + 1, bx0:bx1 + 1]
    hexs = lambda c: "#" + "".join(f"{int(round(x)):02X}" for x in c)
    for k, lab in ((1, "Lmed"), (2, "Bmed"), (3, "Tmed")):
        sel = pxs[sub == k]
        out[lab] = hexs(np.median(sel, axis=0)) if len(sel) else None
    # leaf median per height band (fifths, from the ground) and the bark foot band (h 0-0.1) and 0.2-0.3
    bands = []
    for i in range(5):
        r0, r1 = by1 - int((i + 1) * H / 5), by1 - int(i * H / 5)
        sel = px[r0:r1 + 1, bx0:bx1 + 1][c[r0:r1 + 1, bx0:bx1 + 1] == 1]
        bands.append(hexs(np.median(sel, axis=0)) if len(sel) > 20 else None)
    out["Lbands"] = bands
    tb = []
    for lo_, hi_ in ((0.0, 0.1), (0.2, 0.3)):
        r0, r1 = by1 - int(hi_ * H), by1 - int(lo_ * H)
        sel = px[r0:r1 + 1, bx0:bx1 + 1][c[r0:r1 + 1, bx0:bx1 + 1] == 3]
        tb.append(hexs(np.median(sel, axis=0)) if len(sel) > 20 else None)
    out["Tbands"] = tb
    bs = _comps(c == 2, max(20, int(0.002 * W * H)))
    out["berries"] = sorted([(round((cx - bx0) / W, 3), round((by1 - cy) / H, 3), round(w / H, 3))
                             for cx, cy, w, h_, n_ in bs])
    return out


def measure(views=("front", "side", "rear", "f34", "r34", "top")):
    """Sheet against our renders, per view (the study's masks on both)."""
    ref = M.ref(NUM)
    out = {}
    for v in views:
        a = stats(_load(ref, REF_VIEWS[v]))
        b = stats(_load(f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[v]}.png"))
        out[v] = {"sheet": a, "ours": b}
    return out
