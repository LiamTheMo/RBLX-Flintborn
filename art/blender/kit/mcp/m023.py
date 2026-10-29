"""023 Clay Deposit (references/023.png): a low, round, thick soil pad carrying a heap of five chunky broad-faceted
orange clay lobes (the main lobe centre-back, a big squat lobe at the front-right, a small low one at the front-left, a
tall small one at the left and one at the back-right), with eleven small warm-grey faceted rocks embedded round the
rim and in the notches.

    import importlib, kit_models, m023; importlib.reload(kit_models); importlib.reload(m023); m023.build()

Parts as on the sheet's Exploded Construction, each built by its own function, all in one build frame (studs; front
-Y, +X right, ground z = 0, origin = the pad centre on the ground). R07 owns ClayDeposit*, so the names are
RedClayDeposit* (M023_spec.md section 8, decision 11):
- RedClayDepositSoilBase (soil_base_part): the pad: a 14-sided thick slab, flat bottom, a short chamfer, a sloped skirt
  of irregular triangles, a gently domed top.
- RedClayDepositMainLobe (main_lobe_part): the main lobe: a broad-faceted dome (the convex hull of jittered point
  rings and crown points; round 2), a flat bottom about as wide as the lobe, big irregular side triangles and a broad
  sloping crown.
- RedClayDepositLobe (lobe_part): the squat satellite lobe at FR's size.
- RedClayDepositRock (rock_part): rock variant A, a squat faceted dome with a flat bottom.

The hero (RedClayDeposit) is built from the same builders: pad + 5 lobes + 11 rocks, one exact union of each shell in
turn (M.union_loose), a floor cut at the ground and the sliver cleanup. Colour (stage 4) is painted by position fields
inside the builders before the union (the union and cleanup keep each face's key and Tint). See M023_spec.md.
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M
import m004
import m011
import m012
import m016

NUM, TITLE, SHEET = 23, "Clay Deposit", "M023"
OFF = "m023_offset"
HERO = "RedClayDeposit"

CLAY, CLAY_LOW, CLAY_LIGHT = "m023_clay", "m023_clay_low", "m023_clay_light"
SOIL, SOIL_DARK = "m023_soil", "m023_soil_dark"
ROCK = "m023_rock"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low_spec). The comment is the calibration target (the sheet's rendered median of an
# unshadowed region, spec 5.4).
# Pass 1 (K.calibrate on the dome, 2026-10-28): clay #A7502D (renders 211,99,61), clay_low #964521 (189,87,52),
# clay_light #AF5630 (221,106,63), soil #785D49 (150,112,85), soil_dark #5E4835 (117,88,64), rock #7C6D6E (150,128,123).
# Pass 2 (hero f34_sheet against the f34 cell): clay median #D36440 against #DA653A, so the three clay keys x (1.076,
# 1.021, 0.825) in linear light; soil (#87644B / #856248) and rock (#98817C / #92827C) already within 6.
# Round 2 (after the lobe reshape, 2026-10-28): pass 1 on the dome again gave the same keys (clay #A7502A, clay_low
# #95451D, clay_light #AF562D, soil #785D49, soil_dark #5E4835, rock #7C6D6E). Pass 2 on the new hero's f34_sheet:
# clay #D76339 against #DA653A, so the clay keys x (1.032, 1.043, 1.034); soil #85634A against #856248, so x (1.0,
# 0.979, 0.946); rock #9A837D against #95837D (f34 rock median), so x (0.93, 1, 1).
PALETTE = {CLAY: ("#AF5329", 0.8, False),          # #D4633B part close-up median
           CLAY_LOW: ("#9D471E", 0.8, False),      # #BC5731 close-up bottom third (swatch Clay (Secondary) #BF5C38)
           CLAY_LIGHT: ("#B8592C", 0.8, False),    # #DE6A3E hero main-lobe mid third
           SOIL: ("#785C47", 0.95, False),         # #987054 exploded base median
           SOIL_DARK: ("#5E4733", 0.95, False),    # #76573F f34 front skirt / junction shade
           ROCK: ("#786D6E", 0.9, False)}          # #917F7C exploded rock medians
CLAY_SPEC = None        # Specular IOR Level on the clay keys (None: flintkit's default)


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    _clay_spec()


def _clay_spec():
    if CLAY_SPEC is None:
        return
    for m in bpy.data.materials:
        if m.name.startswith("FB_m023_clay") and m.node_tree:
            b = m.node_tree.nodes.get("Principled BSDF")
            if b and "Specular IOR Level" in b.inputs:
                b.inputs["Specular IOR Level"].default_value = CLAY_SPEC


TARGETS = {CLAY: ((0xD4, 0x63, 0x3B), "vivid"), CLAY_LOW: ((0xBC, 0x57, 0x31), "vivid"),
           CLAY_LIGHT: ((0xDE, 0x6A, 0x3E), "vivid"),
           SOIL: ((0x98, 0x70, 0x54), "brown"), SOIL_DARK: ((0x76, 0x57, 0x3F), "brown"),
           ROCK: ((0x91, 0x7F, 0x7C), "stone")}


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome. Returns {key: (hex, rendered)} and
    leaves the keys set."""
    keys = keys or list(TARGETS)
    set0 = K.set_colour

    def set_colour(key, hexcol, **kw):
        set0(key, hexcol, **kw)
        _clay_spec()
    K.set_colour = set_colour
    try:
        for k in keys:
            K.fk().material(k)
        _clay_spec()
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        K.set_colour = set0
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


# ---- small helpers ---------------------------------------------------------------------------------------------------
STEPS = 4      # 25 / 50 / 75 % in-between keys


def _q(t):
    return round(min(1.0, max(0.0, t)) * STEPS) / STEPS


def _faces(verts):
    return K.faces_of([v for v in verts if v.is_valid])


def _tri(bm, faces):
    bmesh.ops.triangulate(bm, faces=[f for f in faces if f.is_valid and len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")


def _mottle(a, faces, amp, scale, seed, jitter=0.0, tint=1.0):
    """Broad Tint patches about 1/scale studs across, multiplied into each face's Tint (never per-face confetti);
    tint is a uniform per-piece factor."""
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in faces:
        k = (1.0 + amp * 1.6 * noise.noise(f.calc_center_median() * scale + off) +
             (rng.uniform(-jitter, jitter) if jitter else 0.0)) * tint
        for l in f.loops:
            t = l[a.tint_layer][0] * k
            l[a.tint_layer] = (t, t, t, 1.0)


def _ladder(lo, mid, hi):
    """lo, three lo->mid mixes, mid, three mid->hi mixes, hi (9 keys; index 4 = mid)."""
    return ([lo] + [K.mix_key(lo, mid, t) for t in (0.25, 0.5, 0.75)] + [mid] +
            [K.mix_key(mid, hi, t) for t in (0.25, 0.5, 0.75)] + [hi])


# ---- clay lobes ------------------------------------------------------------------------------------------------------
# Round 2 (verifier round 1, item 1): the round-1 lobes were faceted spheroids (the polar dual of 18-28 Fibonacci
# tangent planes, cut flat low down): pinched bases (bottom 0.76 of the max width, widest at half height) and even
# "soccer-ball" pentagons. The sheet's lobes (Part Close-Up, exploded lobes, hero) are broad-based boulders: a flat
# bottom about as wide as the lobe, a short lower band that tucks in to it, sides of big irregular triangles sloping in
# to a shoulder, and a broad sloping crown of 4-5 big faces; their vertices have 5-6 edges (a convex hull of points,
# not a plane dual). So each lobe is now the convex hull of jittered point rings (K.hull_rock's recipe, inline here so
# it keeps the layout's lean, yaw and fitted box):
# rings = (height fraction, radius fraction, points) from the flat bottom up; crown = explicit (x, y, h) points in unit
# radius / unit height (a broad sloping crown for main and squat, a ridge for the tall type); jit = radial and height
# jitter; ang = azimuth jitter (fraction of the ring step); cjit = crown point jitter.
KINDS = {
    # Every kind is a dome over a broad flat bottom: a short lower band that tucks in a little (bottom ring 0.95-0.96,
    # so the flat bottom is at least 0.9 of the max width), the widest ring just above the pad top, steep lower sides,
    # a shoulder band at about 45 deg and a broad crown of 4-6 big faces
    # (round 2: with only one shoulder ring the lobes read as tall cubes with flat lids against the sheet's domes).
    # main: the crown spans about 0.6 of the width (the hero's f34 crown, f .34-.65 over a 0.47 W lobe) and slopes to
    # the front; the back crown points stay high so the kit side view doesn't read a peaked roof.
    # (verifier round 2: upper rings and crown points pulled in, so the main lobe reads as a dome, not an upright block)
    "main": dict(rings=((0.0, 0.96, 8), (0.12, 1.0, 8), (0.38, 0.93, 8), (0.6, 0.82, 8), (0.8, 0.62, 7)),
                 crown=((0.1, 0.05, 1.0), (-0.38, 0.24, 0.95), (0.35, 0.32, 0.96), (0.4, -0.24, 0.91),
                        (-0.32, -0.34, 0.9)), jit=0.07, ang=0.3, cjit=0.05),
    # squat (FR, FL, the Lobe part): a wide low dome with a broad near-flat crown
    "squat": dict(rings=((0.0, 0.96, 8), (0.2, 1.0, 8), (0.42, 0.97, 8), (0.62, 0.86, 7), (0.8, 0.66, 7)),
                  crown=((0.0, 0.05, 1.0), (-0.42, 0.3, 0.97), (0.44, 0.3, 0.98), (0.4, -0.38, 0.95),
                         (-0.44, -0.3, 0.96)), jit=0.07, ang=0.3, cjit=0.05),
    # tall (BL, BR): a rounded wedge, its crown longer along local x
    "tall": dict(rings=((0.0, 0.95, 7), (0.2, 1.0, 7), (0.45, 0.95, 7), (0.66, 0.84, 7), (0.84, 0.64, 6)),
                 crown=((-0.46, 0.1, 0.96), (0.02, -0.04, 1.0), (0.48, 0.08, 0.97), (0.0, 0.4, 0.94),
                        (0.04, -0.4, 0.94)), jit=0.07, ang=0.3, cjit=0.05),
}
LOBE_SINK = 0.3        # the flat bottom this far below the lowest pad top under the footprint (spec 6: 0.25-0.35)
# Layout (spec 2.1, measured on the f34 cell; build frame): name -> (kind, centre x, y, top z, size W x D, yaw deg,
# lean (x, y: crown shift as a fraction of W / D), seed). The base z (so the height) comes from the pad under the
# footprint (LOBE_SINK); the parts are built at PART_H.
LOBES = {
    # round 1b: the main lobe 0.25 forward and the front pair 0.3 towards the rim (the sheet shows almost no pad top in
    # front of them, only the skirt); FL, BL, BR a little fuller (their sheet silhouettes are round domes)
    "Main": ("main", -0.05, 0.85, 4.75, (4.7, 4.4), 15.0, (0.02, -0.03), 23001),
    # round 2: FR 0.25 and FL 0.35 forward, so their broad feet come down to the rim ("Clay overlaps soil base"; the
    # f34 cell's clay bottom line is at h .13-.15 under both, round 2a read .21-.26); FR's top 0.05 up to keep its
    # screen height; FR's yaw -20 -> 0 (with the broad base, the turned right end ran over the rim down the skirt)
    "FR": ("squat", 1.6, -2.25, 3.05, (4.3, 3.9), 0.0, (0.0, -0.03), 23002),
    # round 1c: BL and BR closer in to the main lobe (the top view showed pad between them: "balls on a plate") and
    # further back (the rear cell has both as low near lobes), FL bigger and in against FR and the main lobe
    "FL": ("squat", -1.55, -2.85, 2.2, (2.6, 2.4), 30.0, (0.0, 0.0), 23003),
    # (BL is turned 70 deg, so its local W runs mostly along the build Y: 3.0 deep in Y for the side cell, 2.2 in X)
    # (tried in round 1e: BL 0.6 further back and BR 0.2 back / 0.2 lower, for the rear cell's two low near lobes; the
    # rear hardly changed and the f34 profile got worse (max error 0.07 -> 0.12), so the hero's layout stays)
    "BL": ("tall", -3.0, 0.1, 3.0, (3.0, 2.2), 70.0, (0.06, 0.0), 23004),
    # round 2: BR 0.25 right and 0.2 wider (its broad-based hull hid behind the main lobe: f34 profile at f .80 / .85
    # read .64 / .52 against the sheet's .75 / .66)
    "BR": ("tall", 2.85, 2.3, 2.75, (2.5, 2.3), -60.0, (-0.06, 0.0), 23005),
}
PART_H = {"Main": 3.94, "FR": 2.62}     # the parts' heights (round 1's hero heights)
LOBE_INFO = {}


def _lobe_base(name, pad_tree):
    """(base z, highest pad top under the footprint): the base is LOBE_SINK below the lowest pad top under the lobe's
    footprint (sampled at 0, 0.4 and 0.7 of its half-extents: FR's and BR's outer edges reach over the rim onto the
    skirt, and sampling there would sink them to the skirt)."""
    kind, cx, cy, top, (W, D), yaw, lean, seed = LOBES[name]
    rot = Matrix.Rotation(math.radians(yaw), 3, "Z")
    zs = []
    for i in range(16):
        th = 2 * math.pi * i / 16
        for f in (0.0, 0.4, 0.7):
            p = Vector((cx, cy, 0)) + rot @ Vector((math.cos(th) * W / 2 * f, math.sin(th) * D / 2 * f, 0))
            hit = pad_tree.ray_cast(Vector((p.x, p.y, 20.0)), Vector((0, 0, -1)), 40)
            if hit[0] is not None:
                zs.append(hit[0].z)
    return min(zs) - LOBE_SINK, max(zs)


def _lobe(a, name, at_origin=False, pad_tree=None):
    """One clay lobe: the convex hull of its kind's jittered point rings and crown points, fitted to its W x D x H box
    (base on the flat bottom), leaned, turned and placed. Returns verts."""
    kind, cx, cy, top, (W, D), yaw, lean, seed = LOBES[name]
    if at_origin:
        cx, cy, z0, H, ptop = 0.0, 0.0, 0.0, PART_H[name], None
    else:
        z0, ptop = _lobe_base(name, pad_tree)
        H = top - z0
    k = KINDS[kind]
    rng = random.Random(seed)
    pts = []
    for h, rf, n in k["rings"]:
        off = rng.uniform(0, 2 * math.pi)
        for i in range(n):
            th = off + 2 * math.pi * (i + rng.uniform(-k["ang"], k["ang"])) / n
            r = rf * (1 + rng.uniform(-k["jit"], k["jit"]))
            z = h * (1 + rng.uniform(-k["jit"], k["jit"])) if h > 0 else 0.0
            pts.append(Vector((math.cos(th) * r, math.sin(th) * r, z)))
    cj = k["cjit"]
    for x, y, h in k["crown"]:
        pts.append(Vector((x + rng.uniform(-cj, cj), y + rng.uniform(-cj, cj), h * (1 + rng.uniform(-cj, cj) * 0.4))))
    xs, ys, zs = ([p[i] for p in pts] for i in range(3))
    cxm, cym = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    rot = Matrix.Rotation(math.radians(yaw), 3, "Z")
    bm = a.bm
    vs = []
    for p in pts:
        t = (p.z - min(zs)) / (max(zs) - min(zs))
        q = Vector(((p.x - cxm) / (max(xs) - min(xs)) * W, (p.y - cym) / (max(ys) - min(ys)) * D, t * H))
        # lean in the build frame (after the yaw): the crown shifts by lean x (W, D) at the top
        vs.append(bm.verts.new(Vector((cx + lean[0] * W * t, cy + lean[1] * D * t, z0)) + rot @ q))
    bmesh.ops.convex_hull(bm, input=vs)
    for v in vs:
        if v.is_valid and not v.link_faces:
            bm.verts.remove(v)
    vs = [v for v in vs if v.is_valid]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    sz = min(W, D, H)
    bmesh.ops.remove_doubles(bm, verts=vs, dist=sz * 0.03)
    vs = [v for v in vs if v.is_valid]
    bmesh.ops.dissolve_degenerate(bm, edges=list({e for f in _faces(vs) for e in f.edges}), dist=sz * 0.01)
    vs = [v for v in vs if v.is_valid]
    _tri(bm, _faces(vs))
    a._finish(vs, CLAY)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    LOBE_INFO[name] = dict(z0=round(z0, 3), H=round(H, 3), faces=len(_faces(vs)),
                           sink_centre=None if ptop is None else round(ptop - z0, 2))
    return vs


# ---- rocks -------------------------------------------------------------------------------------------------------------
ROCK_RINGS = [(0.0, 0.92, 6), (0.4, 1.0, 6), (0.8, 0.7, 5), (1.0, 0.25, 3)]
# widths as the spec (tried x 1.1 in round 1c: the rock share rose to 0.09 in f34 against the sheet's 0.063 and 0.15
# in the rear against 0.07)
# round 1d: x 0.92 (the thicker pad lifts the seated rocks: f34 rock share 0.083 against 0.063)
VARIANTS = {"A": (1.24, 23101), "B": (1.1, 23102), "C": (1.01, 23103), "D": (0.87, 23104), "E": (0.7, 23105)}
ROCK_H = 0.8          # height / width
ROCK_D = 0.9          # depth / width


def _rock(a, v, loc=(0, 0, 0), yaw=0.0, tilt=(0.0, 0.0), seed=None):
    w, s = VARIANTS[v]
    vs = K.hull_rock(a, (w, w * ROCK_D, w * ROCK_H), loc=loc, seed=seed or s, mat=ROCK, rings=ROCK_RINGS,
                     jitter=0.12, rot=math.radians(yaw), tilt=tilt, keep_bottom=True)
    _tri(a.bm, _faces(vs))
    bmesh.ops.recalc_face_normals(a.bm, faces=_faces(vs))
    return vs


# rocks (spec 2.3), placed by azimuth (deg, from +X towards +Y) and a fraction of the pad outline radius there:
# (label, az, r fraction, variant, mode, sink (fraction of height), yaw, seed)
# mode "ground": base below the ground (the floor cut flattens it), its inner side cut into the skirt;
# "seat": base sink x height below the soil surface under its centre, its bottom turned half way to the surface normal
# round 2 (verifier item 4): the front and back ground rocks R5, R8, R9 0.95-0.96 -> 0.9-0.92 of the outline radius
# (they read small and far out in the top view); R7 az 26 -> 24 and 0.86 -> 0.88 (with FR now unturned it shows beside
# FR's right flank, as on the sheet). R1, R2 and R6 stay near the old radii: they are the f34 silhouette's ends (at 0.9
# the hero W fell to 9.83, W : H to 1.556 against 1.689 and the profile error at the ends rose to 0.14; R7 at az 15 /
# 0.92 sat at f .95 against the sheet's .85-.92).
ROCKS = (
    ("R1", 167.0, 0.93, "A", "ground", 0.0, 10.0, 23111),
    ("R2", 206.0, 0.97, "D", "ground", 0.0, 40.0, 23112),
    ("R3", 226.0, 0.86, "C", "seat", 0.3, 75.0, 23113),
    ("R4", 207.0, 0.69, "A", "seat", 0.3, 120.0, 23114),
    ("R5", 272.0, 0.92, "B", "ground", 0.0, 160.0, 23115),
    ("R6", 2.0, 0.94, "D", "ground", 0.0, 200.0, 23116),
    ("R7", 24.0, 0.88, "C", "seat", 0.3, 240.0, 23117),
    ("R8", 77.0, 0.9, "C", "ground", 0.0, 280.0, 23118),
    ("R9", 101.0, 0.9, "D", "ground", 0.0, 320.0, 23119),
    ("R10", 129.0, 0.88, "B", "seat", 0.3, 15.0, 23120),
    ("R11", 96.0, 0.72, "A", "seat", 0.3, 55.0, 23121),
)
ROCK_GROUND = -0.15      # a ground rock's base (below the ground; the floor cut makes it flat)
ROCK_TILT = 0.5
ROCK_TINT = {"R1": 1.02, "R2": 0.95, "R3": 1.04, "R4": 0.98, "R5": 1.03, "R6": 0.96, "R7": 1.0, "R8": 0.97,
             "R9": 1.03, "R10": 0.95, "R11": 1.01}
ROCK_INFO = {}
ROCK_YAW_JIT = [0.0]     # extra yaw on every hero rock; the hero guard turns them a little on a retry


def rocks(a, pad_tree):
    out = {}
    for lab, az, rf, v, mode, sink, yaw, seed in ROCKS:
        th = math.radians(az)
        r = _outline_r(th) * rf
        x, y = math.cos(th) * r, math.sin(th) * r
        w = VARIANTS[v][0]
        h = w * ROCK_H
        tilt = (0.0, 0.0)
        if mode == "ground":
            z0 = ROCK_GROUND
        else:
            hit = pad_tree.ray_cast(Vector((x, y, 20.0)), Vector((0, 0, -1)), 40)
            sz = hit[0].z if hit[0] is not None else 0.0
            nrm = Vector((0, 0, 1)).lerp(hit[1], ROCK_TILT).normalized() if hit[0] is not None else Vector((0, 0, 1))
            z0 = sz - sink * h
            tilt = (math.atan2(-nrm.y, nrm.z), math.atan2(nrm.x, math.sqrt(nrm.y ** 2 + nrm.z ** 2)))
        # hull_rock builds about the origin (base at z 0), rotates (yaw, tilt), then moves the base centre to loc
        out[lab] = _rock(a, v, loc=(x, y, z0), yaw=yaw + ROCK_YAW_JIT[0], tilt=tilt, seed=seed)
        ROCK_INFO[lab] = dict(xy=(round(x, 2), round(y, 2)), z0=round(z0, 2), w=w)
    return out


# ---- soil base -------------------------------------------------------------------------------------------------------
PAD = dict(rx=4.9, ry=4.7, n=14, seed=23201)
# rings from the ground up: (z, radius fraction, radial jitter, z jitter)
# round 1d: the rim 0.8 -> 0.95 and the skirt sloped further out (rim 0.925 -> 0.875 R): the f34 cell shows a thick
# sloped skirt band all round, ours read as a thin flat disc
PAD_RINGS = ((-0.05, 0.965, 0.0, 0.0), (0.2, 1.0, 0.012, 0.02), (0.58, 0.95, 0.03, 0.05), (0.95, 0.875, 0.02, 0.05),
             (1.1, 0.64, 0.04, 0.05), (1.2, 0.32, 0.05, 0.04))
PAD_CENTRE = 1.23
# outline radius by azimuth: (az0, az1, factor) sectors (spec 1.3, outline.py): flatter back-left, a bulge front-left
PAD_SECTORS = ((105.0, 135.0, 0.93), (205.0, 230.0, 1.04))


def _outline_r(th):
    """The pad's chamfer-ring radius at azimuth th (radians): the rx / ry ellipse times the sector factors."""
    c, s = math.cos(th), math.sin(th)
    r = 1.0 / math.sqrt((c / PAD["rx"]) ** 2 + (s / PAD["ry"]) ** 2)
    deg = math.degrees(th) % 360
    for a0, a1, f in PAD_SECTORS:
        # a smooth ramp over 12 degrees either side of the sector
        if a0 - 12 <= deg <= a1 + 12:
            w = min(1.0, (deg - (a0 - 12)) / 12, ((a1 + 12) - deg) / 12)
            r *= 1 + (f - 1) * max(0.0, w)
    return r


def _soil_base(a):
    """The pad: 14-sided rings lofted from the flat bottom up through the chamfer, the sloped skirt and the rim to a
    gently domed top and a centre point; quads split on a seeded diagonal (the sheet's irregular skirt triangles).
    Returns verts."""
    rng = random.Random(PAD["seed"])
    bm = a.bm
    n = PAD["n"]
    angs = [2 * math.pi * k / n + rng.uniform(-0.12, 0.12) * (2 * math.pi / n) for k in range(n)]
    sect = [1 + rng.uniform(-0.04, 0.04) for _ in range(n)]
    rows = []
    for i, (z, rf, rj, zj) in enumerate(PAD_RINGS):
        row = []
        for k, th in enumerate(angs):
            # the inner rings turn half a step so the top's triangles are not radial strips
            t = th + (math.pi / n if i >= 4 else 0.0)
            r = _outline_r(t) * rf * (sect[k] if i < 4 else 1.0) * (1 + rng.uniform(-rj, rj))
            row.append(bm.verts.new((math.cos(t) * r, math.sin(t) * r, z + rng.uniform(-zj, zj))))
        rows.append(row)
    top = bm.verts.new((rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), PAD_CENTRE))
    faces = []
    for r0, r1 in zip(rows, rows[1:]):
        for k in range(n):
            j = (k + 1) % n
            a0, a1, b0, b1 = r0[k], r0[j], r1[k], r1[j]
            if rng.random() < 0.5:
                faces += [bm.faces.new((a0, a1, b1)), bm.faces.new((a0, b1, b0))]
            else:
                faces += [bm.faces.new((a0, a1, b0)), bm.faces.new((a1, b1, b0))]
    for k in range(n):
        faces.append(bm.faces.new((rows[-1][k], rows[-1][(k + 1) % n], top)))
    bot = bm.faces.new(list(reversed(rows[0])))
    faces.append(bot)
    _tri(bm, [bot])
    vs = [v for r in rows for v in r] + [top]
    a._finish(vs, SOIL)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    return vs


# ---- colour (stage 4): painted by position, never by facing ------------------------------------------------------------
# Clay ladder: clay_low <- clay -> clay_light. Each lobe: its lowest band towards clay_low (CLAY_LOW_BAND: full
# CLAY_LOW_MIX below t0 of its own height, none above t1), broad noise patches towards clay_light on its upper part
# (CLAY_PATCH), faces close to another lobe (a crease) at least CREASE_MIX towards clay_low. Values add and are
# quantised to 25 % steps, so neighbouring faces never jump more than a step where the fields are smooth.
CLAY_LOW_BAND = (0.22, 0.5)
CLAY_LOW_MIX = 0.4         # round 2: 0.5 -> 0.4 (our bottom third read 7 darker than the sheet's)
CLAY_PATCH = dict(scale=0.45, level=0.05, width=0.35, mix=0.5, t0=0.5, t1=0.7, seed=23301)
CREASE = (0.45, 0.25)       # within this distance of another lobe's surface: at least this far towards clay_low
CLAY_MOTTLE = dict(amp=0.03, scale=0.6, seed=23302)
LOBE_TINT = {"Main": 1.0, "FR": 1.01, "FL": 1.02, "BL": 0.98, "BR": 0.99}
# Soil ladder: soil -> soil_dark. Contact rings round the lobes' feet and the rocks (SOIL_CONTACT: (distance, mix)
# steps), the bottom chamfer band (z < SOIL_CHAMFER[0]) at SOIL_CHAMFER[1], broad noise patches on the skirt.
# round 2: (0.35, 0.5), (0.8, 0.25) -> (0.2, 0.5), (0.45, 0.25): on the dense post-union pad the wide rings covered
# the whole top, so the plain soil key never showed and no contact ring read (verifier item 3)
SOIL_CONTACT = ((0.2, 0.5), (0.45, 0.25))
SOIL_CHAMFER = (0.22, 0.25)
SOIL_PATCH = dict(scale=0.5, level=0.25, level2=0.45, seed=23311)     # round 2: levels 0.12 / 0.4 -> 0.25 / 0.45
SOIL_MOTTLE = dict(amp=0.05, scale=0.5, seed=23312)
ROCK_MOTTLE = dict(amp=0.04, scale=0.8, seed=23321)


def _paint_lobe(a, name, vs, others):
    seed = LOBES[name][-1]
    info = LOBE_INFO[name]
    z0, H = info["z0"], info["H"]
    lad = _ladder(CLAY_LOW, CLAY, CLAY_LIGHT)
    nf = K.noise_field(scale=CLAY_PATCH["scale"], seed=CLAY_PATCH["seed"])
    for f in _faces(vs):
        c = f.calc_center_median()
        t = (c.z - z0) / H
        lo = CLAY_LOW_MIX * min(1.0, max(0.0, (CLAY_LOW_BAND[1] - t) / (CLAY_LOW_BAND[1] - CLAY_LOW_BAND[0])))
        up = min(1.0, max(0.0, (t - CLAY_PATCH["t0"]) / (CLAY_PATCH["t1"] - CLAY_PATCH["t0"])))
        hi = CLAY_PATCH["mix"] * up * min(1.0, max(0.0, (nf(c) - CLAY_PATCH["level"]) / CLAY_PATCH["width"]))
        v = hi - lo
        for tree in others:
            loc = tree.find_nearest(c)
            if loc[0] is not None and loc[3] < CREASE[0]:
                v = min(v, -CREASE[1])
        v = max(-1.0, min(1.0, v))
        f.material_index = a._mi(lad[4 + int(round(v * 4))])
    _mottle(a, _faces(vs), CLAY_MOTTLE["amp"], CLAY_MOTTLE["scale"], CLAY_MOTTLE["seed"] + seed,
            tint=LOBE_TINT.get(name, 1.0))


def _paint_soil(a, vs, contact_trees=()):
    lad = [SOIL] + [K.mix_key(SOIL, SOIL_DARK, t) for t in (0.25, 0.5, 0.75)] + [SOIL_DARK]
    nf = K.noise_field(scale=SOIL_PATCH["scale"], seed=SOIL_PATCH["seed"])
    for f in _faces(vs):
        c = f.calc_center_median()
        t = 0.0
        if c.z < SOIL_CHAMFER[0] and c.z > 0.0:
            t = SOIL_CHAMFER[1]
        n_ = nf(c)
        if n_ > SOIL_PATCH["level2"]:
            t = max(t, 0.5)
        elif n_ > SOIL_PATCH["level"]:
            t = max(t, 0.25)
        for tree in contact_trees:
            loc = tree.find_nearest(c)
            if loc[0] is None:
                continue
            for dist, mix in SOIL_CONTACT:
                if loc[3] < dist:
                    t = max(t, mix)
                    break
        f.material_index = a._mi(lad[int(round(_q(t) * 4))])
    _mottle(a, _faces(vs), SOIL_MOTTLE["amp"], SOIL_MOTTLE["scale"], SOIL_MOTTLE["seed"])


def _paint_rock(a, lab, vs, seed):
    _mottle(a, _faces(vs), ROCK_MOTTLE["amp"], ROCK_MOTTLE["scale"], ROCK_MOTTLE["seed"] + seed,
            tint=ROCK_TINT.get(lab, 1.0))


# ---- parts -----------------------------------------------------------------------------------------------------------
def soil_base_part(a):
    vs = _soil_base(a)
    _paint_soil(a, vs)


def main_lobe_part(a):
    vs = _lobe(a, "Main", at_origin=True)
    _paint_lobe(a, "Main", vs, ())


def lobe_part(a):
    vs = _lobe(a, "FR", at_origin=True)
    _paint_lobe(a, "FR", vs, ())


def rock_part(a):
    vs = _rock(a, "A")
    _paint_rock(a, "R4", vs, 0)


# ---- hero ------------------------------------------------------------------------------------------------------------
def hero(a):
    LOBE_INFO.clear()
    ROCK_INFO.clear()
    pad = _soil_base(a)
    pad_tree = K.bvh_of(pad)
    lobes = {k: _lobe(a, k, pad_tree=pad_tree) for k in LOBES}
    rk = rocks(a, pad_tree)
    trees = {k: K.bvh_of(v) for k, v in lobes.items()}
    for k, vs in lobes.items():
        _paint_lobe(a, k, vs, [t for j, t in trees.items() if j != k])
    rock_trees = [K.bvh_of(v) for v in rk.values()]
    _paint_soil(a, pad, list(trees.values()) + rock_trees)
    for i, (lab, vs) in enumerate(rk.items()):
        _paint_rock(a, lab, vs, i)


NOTES = {
    HERO: "red clay deposit resource node: a heap of five chunky broad-faceted orange clay lobes (a big main lobe "
          "centre-back, a big squat lobe front-right, three small ones round it) on a thick faceted round soil pad, "
          "eleven warm-grey faceted rocks embedded round the rim and in the notches; one closed mesh, flat underside. "
          "No VFX",
    "RedClayDepositSoilBase": "Soil Base (reusable): thick 14-sided faceted soil slab, flat underside, short chamfer, "
                              "sloped skirt of irregular triangles, gently domed top",
    "RedClayDepositMainLobe": "Main Clay Lobe (reusable): chunky broad-faceted orange clay boulder, flat bottom, broad "
                              "sloping crown face",
    "RedClayDepositLobe": "Clay Lobe (reusable): squat broad-faceted orange clay dome, flat bottom",
    "RedClayDepositRock": "Rock (reusable): squat faceted warm-grey dome, flat bottom",
}


# ---- cleanup ---------------------------------------------------------------------------------------------------------
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
    """M020's polish: quads split, the floor cap re-fanned (no needles), slivers forced open, origin back at the
    bottom centre, UVs redone."""
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


def _ground_faces(o):
    """Faces lying on the ground plane (the floor cut's cap, one flat face fanned across the pad and the rim rocks'
    feet): all the plain soil key (the Base Underside's even flat bottom; a darker key on this large down-facing area
    would make the soil family's colour follow facing). Round 1 keyed floor fans by their neighbours and left grey
    rock-keyed spikes across the underside."""
    from m011 import _Paint
    p = _Paint(o, off=o[OFF])
    n = 0
    for f in p.bm.faces:
        if all(abs(v.co.z) < 1e-3 for v in f.verts):
            f.material_index = p._mi(SOIL)
            n += 1
    p.done()
    return n


def _fused_ok(o):
    a = M.audit(o)
    return (a["shells"] == 1 and not a["nonmanifold_edges"] and not a.get("nonmanifold_verts") and
            not a["boundary_edges"] and a["normals"] == "outward"
            and not m016._self_hits(o)[0] and not m012._thin(o, POLISH_LIM)["under"])


# ---- stages 5 + 6 (spec section 7) -------------------------------------------------------------------------------------
# Stage 5: nothing. The sheet shows an ordinary sunlit clay outcrop: no emissive key, no light (decision 8).
# Stage 6: nothing. The sheet shows no glow, sparkle, dust or crumbs: no socket (decision 8).


# ---- build -----------------------------------------------------------------------------------------------------------
PARTS = (("RedClayDepositSoilBase", soil_base_part), ("RedClayDepositMainLobe", main_lobe_part),
         ("RedClayDepositLobe", lobe_part), ("RedClayDepositRock", rock_part))
GROUND_PARTS = {"RedClayDepositSoilBase"}
TARGET_SIZE = ((10.0, 0.4), (9.6, 0.4), (4.75, 0.2))
HERO_TRIES = 6
HERO_YAW_STEP = 17.0


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith("_m023_"):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)


def _make(name, fn, role, budget):
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget, collision="hull",
             tint_var=0.03)
    off = M._build_offset(fn)
    o[OFF] = list(off)
    lg = {}
    if role == "hero":
        lg["shells_merged"] = M.union_loose(o)
    if name in GROUND_PARTS or role == "hero":
        m004.floor_cut(o, z0=-off.z)
        o[OFF] = [off.x, off.y, 0.0]
    if role == "hero" or name in GROUND_PARTS:
        lg["clean"] = m016._clean_mesh(o, (0.0,))
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    if name in GROUND_PARTS or role == "hero":
        lg["ground_faces"] = _ground_faces(o)
    # bowtie verts (two closed fans meeting at one point; the edge checks miss them): split and part them
    lg["bowties"] = M.fix_bowties(o)
    return o, lg


def build(render=True, parts=True):
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn, "part", 1000)
    # the hero guard: a rock grazing a lobe crease can leave a self-intersecting sliver pair after the union and
    # cleanup; then every rock turns HERO_YAW_STEP degrees about its own axis and the hero is rebuilt
    for attempt in range(HERO_TRIES):
        ROCK_YAW_JIT[0] = attempt * HERO_YAW_STEP
        h, log["hero"] = _make(HERO, hero, "hero", 4000)
        if _fused_ok(h):
            break
    log["hero"]["attempt"] = attempt if _fused_ok(h) else -1
    log["hero"]["rock_yaw_jit"] = ROCK_YAW_JIT[0]
    log["lobes"] = dict(LOBE_INFO)
    log["rocks"] = dict(ROCK_INFO)
    _clay_spec()
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
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges",
                                         "wire_edges", "loose_verts", "zero_area_faces", "normals", "ngons",
                                         "dup_verts")} for au in audits],
           "thin": thin, "self_hits": self_hits, "log": log, "problems": problems,
           "uv": {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped",
                                                                            "min_gap", "border", "density",
                                                                            "stretch_conformal_p95")}
                  for o in order}}
    if render:
        out["views"] = render_views(order)
    return out


# ---- renders ---------------------------------------------------------------------------------------------------------
def _part_matrix(o):
    return Matrix.Translation(Vector(o[OFF]))


# the sheet's comparison cameras (decision 9): the f34 cell is an aligned elevated front view, the front cell the same
# drawing lower, the r34 cell the f34 mirrored, the side from -X
SHEET_VIEWS = {"f34_sheet": (0, 14), "front_sheet": (0, 9), "rear_sheet": (180, 9), "side_sheet": (-90, 10),
               "top_sheet": (0, 89)}
SHEET_LENS = 3.0        # the sheet's cells are near-orthographic: the *_sheet shots use a 3x longer lens (M018/M020)
JUNC_CU = (-35, 12, (-3.0, -1.6, 1.2), 1.7)      # the Junction Detail: R4 between BL and FL
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


EXPL = dict(main=(0.0, 0.8, 7.6), lobe_l=(-3.4, -0.6, 4.6), lobe_r=(3.4, -0.6, 4.6),
            rocks=(("A", -3.9, -1.8, 2.0), ("B", -1.3, -0.8, 2.7), ("C", 1.1, -0.6, 2.3), ("D", 2.5, -1.2, 2.6),
                   ("E", 4.1, -2.0, 1.9)))


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded Construction: the soil base at the bottom, five rocks
    above it, the two clay lobes and the main lobe on top."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []

    def put(tag, part, m):
        c = bpy.data.objects.new(f"_m023_expl_{tag}", by[part].data)
        coll.objects.link(c)
        c.matrix_world = m @ _part_matrix(by[part])
        shown.append(c)
    x0 = objs[0].location.x + 40
    base = Matrix.Translation((x0, objs[0].location.y, 0))
    put("base", "RedClayDepositSoilBase", base)
    put("main", "RedClayDepositMainLobe", base @ Matrix.Translation(EXPL["main"]))
    s = 0.7
    put("lobe_l", "RedClayDepositLobe", base @ Matrix.Translation(EXPL["lobe_l"]) @ Matrix.Diagonal((s, s, s, 1)))
    put("lobe_r", "RedClayDepositLobe", base @ Matrix.Translation(EXPL["lobe_r"]) @
        Matrix.Rotation(math.radians(140), 4, "Z") @ Matrix.Diagonal((s * 0.85, s * 0.85, s * 1.1, 1)))
    for v, x, y, z in EXPL["rocks"]:
        sc = VARIANTS[v][0] / VARIANTS["A"][0]
        put("rock_" + v, "RedClayDepositRock", base @ Matrix.Translation((x, y, z)) @
            Matrix.Rotation(math.radians(70 * ord(v)), 4, "Z") @ Matrix.Diagonal((sc, sc, sc, 1)))
    bpy.context.view_layer.update()
    return shown


def render_close(objs, path, az, el, centre, radius):
    """A close-up: the kit studio and camera aimed from (az, el), framed on a sphere (centre, radius)."""
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
            extra["exploded"] = (shown, -12, 14)
        for o in objs[1:]:
            extra["part_" + o.name.replace("RedClayDeposit", "").lower()] = ([o], *PARTS_SHOT)
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
            out["under_cu"] = render_close([h], f"{d}/under_cu.png", 20, -40, off @ Vector((0, 0, 0.5)), 5.0)
        return out
    finally:
        for o in shown:
            bpy.data.objects.remove(o, do_unlink=True)
        M.display(NUM, objs, TITLE)


# ---- measuring (the study's masks, numpy) ------------------------------------------------------------------------------
REF_VIEWS = {"f34": (15, 115, 540, 435), "r34": (545, 115, 1010, 435), "front": (12, 480, 295, 700),
             "side": (296, 480, 523, 700), "rear": (524, 480, 790, 700), "top": (796, 478, 1012, 700)}
OUR_VIEWS = {"f34": "f34_sheet", "front": "front_sheet", "rear": "rear_sheet", "side": "side_sheet",
             "r34": "f34_sheet", "top": "top_sheet"}
SHEET_PAPER = (241, 236, 230)


def _classes(px, paper=SHEET_PAPER):
    """px (h, w, 3) sRGB 0-255 -> 0 none, 1 K clay, 2 S soil, 3 R rock, 4 O other (the study's m.py cls())."""
    r, g, b = px[..., 0] / 255, px[..., 1] / 255, px[..., 2] / 255
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0)
    v = mx
    near = np.abs(px - np.array(paper, float)).max(-1) <= 14
    warm = (h <= 40) | (h >= 345)
    Kc = (warm & (s >= 0.56) & (v >= 0.35) & (h <= 30)) | ((h >= 345) & (s >= 0.56))
    Sc = ~Kc & warm & (s >= 0.24) & (s < 0.70) & (v < 0.80) & (v >= 0.18)
    # rock: the study's mask, plus warm or purple hue only (the studio floor's shadow is a cream grey, hue 35-45 at sat 0.07,
    # which would otherwise count as rock in our renders; the sheet's rocks are hue 7-21 or about 350)
    Rc = ~Kc & ~Sc & (s < 0.24) & (v >= 0.33) & (v < 0.80) & ((h <= 30) | (h >= 300)) & (s >= 0.06)
    out = np.zeros(px.shape[:2], np.uint8)
    out[~near & (v < 0.86)] = 4
    out[Kc] = 1
    out[Sc] = 2
    out[Rc] = 3
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


def stats(px, paper=SHEET_PAPER):
    c = _classes(px, paper)
    obj = (c >= 1) & (c <= 3)
    cols = np.nonzero(obj.sum(0) >= 3)[0]
    rows = np.nonzero(obj.sum(1) >= 3)[0]
    bx0, bx1, by0, by1 = cols.min(), cols.max(), rows.min(), rows.max()
    W, H = bx1 - bx0, by1 - by0
    sub = c[by0:by1 + 1, bx0:bx1 + 1]
    n = max(1, ((sub >= 1) & (sub <= 3)).sum())
    out = {"wh": round(W / H, 3), "K": round((sub == 1).sum() / n, 3), "S": round((sub == 2).sum() / n, 3),
           "R": round((sub == 3).sum() / n, 3)}
    top = []
    for i in range(21):
        x = bx0 + int(i * W / 20)
        ys = np.nonzero(obj[:, max(0, x - 1):x + 2].any(1))[0]
        top.append(round((by1 - ys.min()) / H, 2) if len(ys) else None)
    out["top"] = top
    pxs = px[by0:by1 + 1, bx0:bx1 + 1]
    for k, lab in ((1, "K"), (2, "S"), (3, "R")):
        sel = pxs[sub == k]
        if len(sel) >= 8:
            srt = sel[np.argsort(sel.sum(1))]
            q = len(srt) // 4
            out[lab + "med"] = _hex(np.median(sel, axis=0))
            out[lab + "lit"] = _hex(np.median(srt[-q:], axis=0))
            out[lab + "shade"] = _hex(np.median(srt[:q], axis=0))
    # clay by height thirds of the clay's own extent (the painted low band)
    ys, xs = np.nonzero(sub == 1)
    if len(ys):
        y0, y1 = ys.min(), ys.max()
        thirds = []
        for i in range(3):
            a_, b_ = y0 + (y1 - y0) * i / 3, y0 + (y1 - y0) * (i + 1) / 3
            m = (ys >= a_) & (ys <= b_)
            thirds.append(_hex(np.median(pxs[ys[m], xs[m]], axis=0)))
        out["Kthirds_top_mid_bot"] = thirds
    return out


def measure(views=("f34", "front", "rear", "side", "r34", "top")):
    """Sheet against our renders, per view (the study's masks on both; the studio floor counts as paper). The r34 cell
    is compared with the f34_sheet render flipped left-right (spec 3.2)."""
    ref = M.ref(NUM)
    out = {}
    for vname in views:
        a = stats(_load(ref, REF_VIEWS[vname]))
        ours = _load(f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[vname]}.png")
        if vname == "r34":
            ours = ours[:, ::-1]
        corner = tuple(int(x) for x in np.median(ours[:8, :8].reshape(-1, 3), axis=0))
        b = stats(ours, paper=corner)
        err = [abs(x - y) for x, y in zip(a["top"], b["top"]) if x is not None and y is not None]
        out[vname] = {"sheet": a, "ours": b, "prof_err_mean_max": (round(sum(err) / len(err), 3), round(max(err), 2))}
    return out
