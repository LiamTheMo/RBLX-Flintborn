"""030 Mooncap (references/030.png): a cluster of two bioluminescent cave mushrooms. A big, thick, faceted violet
toadstool (flat-topped crown over its stem, the rim drooping to -X) on a fat cream pear-shaped stem at the back-left,
a small one (drooping to +X) on a short stem at the front-right tucked under the big rim, eleven glowing 8-sided cyan
gems set in the caps, a ring of ten domed brown-grey boulders and three pebbles on a dark dirt slab, and two bright
yellow-green leaf clumps at the back.

    import importlib, kit_models, m030; importlib.reload(kit_models); importlib.reload(m030); m030.build()

Parts as on the sheet's Exploded Construction, each built by its own function, all in one build frame (studs; front
-Y, +X right, ground z = 0, origin = the base ring's centre on the ground). R08 owns Mooncap*, so the names are
(M030_spec.md section 8, decision 12):
- MooncapShell (shell_part): the big cap, undrooped: a lathe of half-step offset rings (underside cone, a vertical rim
  band, two shoulder rings, a flat crown), its five gem pockets carved (8-sided, exact difference).
- MooncapGlowSpot (spot_part): the crown gem S1 whole: 8-sided girdle, two crown rows, a flat table, a pavilion cone.
- MooncapStalkLarge / MooncapStalkSmall (stalk_large_part / stalk_small_part): the fat faceted pear stems.
- MooncapLeafClump (clump_part): L1, five thick kite leaves (convex hulls with a midrib ridge and a keel).
- MooncapRockBase (rock_base_part): the dirt slab, ten peaky dome boulders and three pebbles.

The hero (MooncapNode) is built from the same builders: base, stems, the two drooped caps and the leaves are united one
shell at a time (exact booleans, fine merge); then the seven gems of 0.6 or more get their 8-sided pockets carved one
at a time (cutters in the dark cap key, so the pocket walls and floors come out dark); the eleven gems are united in
(the four small ones on a dark sunk bezel ring instead of a pocket, decision 5); floor cut, cleanup. Colour (stage 4)
is painted by position fields inside the builders before the union. Stages 5-6: the three gem keys are Neon; one
crystal_glow light socket in front of and between the caps. See M030_spec.md.
"""
import json
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
import m011
import m012
import m016

NUM, TITLE, SHEET = 30, "Mooncap", "M030"
OFF = "m030_offset"
PFX = "_m030_"
HERO = "MooncapNode"
SHELL, SPOT, STALK_L, STALK_S, CLUMP, BASE = ("MooncapShell", "MooncapGlowSpot", "MooncapStalkLarge",
                                              "MooncapStalkSmall", "MooncapLeafClump", "MooncapRockBase")

CAP, CAP_LIGHT, CAP_DARK = "m030_cap", "m030_cap_light", "m030_cap_dark"
GEM, GEM_LIGHT, GEM_DEEP = "m030_spot", "m030_spot_light", "m030_spot_deep"
STEM, STEM_BASE = "m030_stem", "m030_stem_base"
LEAF, LEAF_BASE, LEAF_TIP = "m030_leaf", "m030_leaf_base", "m030_leaf_tip"
ROCK, ROCK_LIGHT, ROCK_DARK, DIRT = "m030_rock", "m030_rock_light", "m030_rock_dark", "m030_dirt"
GEM_KEYS = (GEM, GEM_LIGHT, GEM_DEEP)

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0
NEON = 1.0              # the exporter's GLOW_EMISSION threshold: the three gem keys export as Neon pieces
GEM_EMIT = 1.0

# key -> (hex, roughness, emission, low specular). Stage 1 placeholders are the study's 5.4 targets; stage 4 writes the
# calibrated values here (passes in M030_spec.md "Stage 4").
PALETTE = {GEM: ("#74D6EC", 0.4, GEM_EMIT, True), GEM_LIGHT: ("#A9F0F5", 0.4, GEM_EMIT, True),
           GEM_DEEP: ("#4DA2D0", 0.4, GEM_EMIT, True),
           CAP: ("#584DA6", 0.7, 0.0, True), CAP_LIGHT: ("#725FBE", 0.7, 0.0, True),
           CAP_DARK: ("#44396E", 0.75, 0.0, True),
           STEM: ("#CCB18F", 0.85, 0.0, False), STEM_BASE: ("#B0956E", 0.85, 0.0, False),
           LEAF: ("#819630", 0.75, 0.0, True), LEAF_BASE: ("#6A7D28", 0.75, 0.0, True),
           LEAF_TIP: ("#98AA36", 0.75, 0.0, True),
           ROCK: ("#6E5C55", 0.92, 0.0, False), ROCK_LIGHT: ("#8A7973", 0.92, 0.0, False),
           ROCK_DARK: ("#4F433E", 0.92, 0.0, False), DIRT: ("#5E4E4B", 0.95, 0.0, False)}

# calibration targets (spec 5.4: rendered medians of unshadowed regions on the sheet)
TARGETS = {CAP: ((0x6A, 0x58, 0xC2), "vivid"), CAP_LIGHT: ((0x8C, 0x70, 0xDC), "vivid"),
           CAP_DARK: ((0x4F, 0x3F, 0x7C), "vivid"),
           STEM: ((0xE6, 0xC8, 0x9F), "all"), STEM_BASE: ((0xC8, 0xA6, 0x7B), "all"),
           LEAF: ((0x82, 0x95, 0x2E), "green"), LEAF_BASE: ((0x69, 0x79, 0x25), "green"),
           LEAF_TIP: ((0x9D, 0xAC, 0x35), "green"),
           ROCK: ((0x7B, 0x66, 0x5D), "all"), ROCK_LIGHT: ((0x9E, 0x88, 0x80), "all"),
           ROCK_DARK: ((0x5C, 0x4B, 0x43), "all"), DIRT: ((0x6C, 0x58, 0x50), "all")}


def palette():
    for k, (hexcol, rough, emit, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, emit=emit, low_spec=low)
        _restyle(k)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, emit=emit, low_spec=low)
    _glow_mats()


def _restyle(key):
    """Drop an FB_ material whose node set no longer matches its key's emission (flintkit builds emissive keys
    without the Tint node, and set_colour never clears an emission), so flintkit makes it afresh (m015)."""
    mat = bpy.data.materials.get("FB_" + key)
    if mat and mat.node_tree:
        tinted = any(n.type == "MIX" for n in mat.node_tree.nodes)
        if tinted == (K.fk().palette_entry(key)[3] > 0):
            mat.name = mat.name + "_restyle"
            new = K.fk().material(key)
            mat.user_remap(new)
            bpy.data.materials.remove(mat)
            return True
    return False


def _glow_mats():
    """Blender preview of the Neon keys as Roblox shows Neon: the key's own colour, unshaded (the BSDF's base colour
    black, no specular, so only the emission shows). The exported hex is unchanged (m015)."""
    for mat in bpy.data.materials:
        if not (mat.name.startswith("FB_m030_") and mat.node_tree):
            continue
        if list(mat.get("flintkit_spec", [0, 0, 0]))[2] < NEON:
            continue
        b = mat.node_tree.nodes.get("Principled BSDF")
        for l in list(b.inputs["Base Color"].links):
            mat.node_tree.links.remove(l)
        b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        if "Specular IOR Level" in b.inputs:
            b.inputs["Specular IOR Level"].default_value = 0.0


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's solid keys (TARGETS) on the kit's faceted test dome. Returns {key: (hex, rendered)}
    and leaves the keys set (write them into PALETTE)."""
    keys = keys or list(TARGETS)
    for k in keys:
        K.fk().material(k)
    try:
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


# ---- small helpers ---------------------------------------------------------------------------------------------------
def _faces(verts):
    return K.faces_of([v for v in verts if v.is_valid])


def _tri(bm, faces):
    bmesh.ops.triangulate(bm, faces=[f for f in faces if f.is_valid and len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")


def _mottle(a, faces, amp, scale, seed, tint=1.0):
    """Broad Tint patches about 1/scale studs across, multiplied into each face's Tint (never per-face confetti);
    tint is a uniform per-piece factor."""
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in faces:
        k = (1.0 + amp * 1.6 * noise.noise(f.calc_center_median() * scale + off)) * tint
        for l in f.loops:
            t = l[a.tint_layer][0] * k
            l[a.tint_layer] = (t, t, t, 1.0)


def _ladder(lo, mid, hi):
    """lo, three lo->mid mixes, mid, three mid->hi mixes, hi (9 keys; index 4 = mid; 25 / 50 / 75 % steps)."""
    return ([lo] + [K.mix_key(lo, mid, t) for t in (0.25, 0.5, 0.75)] + [mid] +
            [K.mix_key(mid, hi, t) for t in (0.25, 0.5, 0.75)] + [hi])


def _key(lad, v):
    """v in -1..1 -> the ladder key (quantised to 25 % steps)."""
    v = max(-1.0, min(1.0, v))
    return lad[4 + int(round(v * 4))]


def _band(bm, A, B, shift):
    """Triangles between two closed rings of equal count, B turned half a step from A (B[k + shift] lies between A[k]
    and A[k + 1]): the diamond / kite facets. Returns faces."""
    n = len(A)
    out = []
    for k in range(n):
        a0, a1 = A[k], A[(k + 1) % n]
        b0, b1 = B[(k + shift) % n], B[(k + shift + 1) % n]
        out.append(bm.faces.new((a0, a1, b0)))
        out.append(bm.faces.new((a1, b1, b0)))
    return out


def _fan(bm, ring, centre):
    n = len(ring)
    return [bm.faces.new((ring[k], ring[(k + 1) % n], centre)) for k in range(n)]


def _hull(a, pts):
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    for v in vs:
        if v.is_valid and not v.link_faces:
            bm.verts.remove(v)
    vs = [v for v in vs if v.is_valid]
    _tri(bm, _faces(vs))
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    return vs


# ---- caps ------------------------------------------------------------------------------------------------------------
# lathe rings (name, radius fraction, height fraction of hc), bottom up (spec 1.4). Each ring is turned half a step from
# the one below, so the facets read as triangles and kites. "stem" is the underside's join ring (its radius is given in
# studs per cap, centred on the stem top), "centre" closes the underside; "apex" closes the crown.
BIG_RINGS = (("stem", None, 0.20), ("under", 0.68, 0.07), ("rimb", 1.0, 0.0), ("rimt", 1.0, 0.15),
             ("sh", 0.92, 0.42), ("ush", 0.70, 0.74), ("crown", 0.34, 0.96))
SMALL_RINGS = (("stem", None, 0.20), ("under", 0.68, 0.07), ("rimb", 1.0, 0.0), ("rimt", 1.0, 0.15),
               ("sh", 0.92, 0.48), ("ush", 0.70, 0.80), ("crown", 0.34, 0.96))
UNDER = {"stem", "under", "centre"}
RIM_U = 0.15            # the rim band's height fraction: dome rings above it droop with weight (1 - w)
UNDER_DROOP = 0.5
# spec 2.1 (decisions 3-4): rim centre (x, y), rim-bottom z at the centre, radii, height, sectors, droop e (the crown's
# shift toward the stem) and s (the rim's slope per stud of x), the stem top's centre and the join ring's radius
CAPS = {
    "big": dict(c=(-0.70, 0.50), z0=2.75, rx=3.0, ry=2.4, hc=2.6, n=14, e=0.70, s=0.33, stem=(-0.20, 0.35),
                stem_r=0.88, rings=BIG_RINGS, seed=30001, jit=0.04, zjit=0.03),
    "small": dict(c=(2.18, -1.55), z0=2.0, rx=1.47, ry=1.18, hc=1.42, n=12, e=-0.32, s=-0.35, stem=(1.85, -1.35),
                  stem_r=0.56, rings=SMALL_RINGS, seed=30002, jit=0.04, zjit=0.03),
}
CAP_INFO = {}


def _cap_spec(which, droop=True, at_origin=False):
    s = dict(CAPS[which])
    if at_origin:
        s["c"], s["z0"], s["stem"] = (0.0, 0.0), 0.0, (0.0, 0.0)
    if not droop:
        s["e"] = s["s"] = 0.0
        s["stem"] = s["c"]
    return s


def _cap_geom(s):
    """The cap's lathe as plain data: points, faces (index triples) and per-point (ring name, u). Pure, seeded, so the
    builder and the gem placement probe see the same surface."""
    rng = random.Random(s["seed"])
    n = s["n"]
    cx, cy = s["c"]
    sx, sy = s["stem"]
    pts, info, rings = [], [], []
    for i, (name, rho, u) in enumerate(s["rings"]):
        off = (i % 2) * math.pi / n
        row = []
        for k in range(n):
            th = 2 * math.pi * k / n + off
            j = 1 + rng.uniform(-s["jit"], s["jit"])
            zj = rng.uniform(-s["zjit"], s["zjit"]) * s["hc"] if name not in ("rimb", "rimt") else \
                rng.uniform(-0.01, 0.01) * s["hc"]
            if name == "stem":
                x = sx + math.cos(th) * s["stem_r"] * j
                y = sy + math.sin(th) * s["stem_r"] * j
                z = s["z0"] + u * s["hc"] + zj * 0.3
            else:
                x0 = cx + math.cos(th) * rho * s["rx"] * j
                y = cy + math.sin(th) * rho * s["ry"] * j
                z = s["z0"] + u * s["hc"] + zj
                if u <= RIM_U + 1e-6:
                    x = x0
                    # the underside ring follows the rim half way, so the cone from the rim to the stem never folds
                    z += s["s"] * (x0 - cx) * (UNDER_DROOP if name == "under" else 1.0)
                else:
                    w = (u - RIM_U) / (1 - RIM_U)
                    x = x0 + s["e"] * w
                    z += s["s"] * (x0 - cx) * (1 - w)
            row.append(len(pts))
            pts.append(Vector((x, y, z)))
            info.append((name, u))
        rings.append(row)
    # the underside's centre (inside the stem) and the crown's apex (offset a little toward the stem side)
    c_i = len(pts)
    pts.append(Vector((sx, sy, s["z0"] + 0.22 * s["hc"])))
    info.append(("centre", 0.22))
    a_i = len(pts)
    pts.append(Vector((cx + s["e"] + rng.uniform(-0.04, 0.04), cy + rng.uniform(-0.04, 0.04), s["z0"] + s["hc"])))
    info.append(("apex", 1.0))
    faces = []
    for i in range(len(rings) - 1):
        A, B = rings[i], rings[i + 1]
        shift = 0 if i % 2 == 0 else 1
        for k in range(n):
            a0, a1 = A[k], A[(k + 1) % n]
            b0, b1 = B[(k + shift) % n], B[(k + shift + 1) % n]
            faces += [(a0, a1, b0), (a1, b1, b0)]
    for k in range(n):
        faces.append((rings[0][(k + 1) % n], rings[0][k], c_i))
        faces.append((rings[-1][k], rings[-1][(k + 1) % n], a_i))
    return pts, faces, info


def _cap_tree(s):
    pts, faces, _ = _cap_geom(s)
    return BVHTree.FromPolygons(pts, faces), pts, faces


# cap colour (spec 5.5): the ladder dark -> cap -> light by v. Underside v UNDER_V, rim band RIM_V, dome by its ring u
# (+ broad noise + a random facet scatter): v = (u - lo) / ramp below DOME["lo"], 0 between, (u - hi) / ramp above.
CAP_COL = dict(under=-0.25, rim=-0.5, lo=0.38, lo_ramp=0.22, hi=0.62, hi_ramp=0.14, nz=0.08, chk=0.10, seed=30011)
CAP_MOTTLE = dict(amp=0.03, scale=0.5, seed=30012)


def _paint_cap(a, faces, finfo, s, seed):
    c = CAP_COL
    lad = _ladder(CAP_DARK, CAP, CAP_LIGHT)
    nf = K.noise_field(scale=0.6, seed=c["seed"] + seed)
    rng = random.Random(c["seed"] + seed)
    for f, names_us in zip(faces, finfo):
        names = {nm for nm, _ in names_us}
        u = sum(uu for _, uu in names_us) / len(names_us)
        p = f.calc_center_median()
        if names <= UNDER | {"rimb"}:
            v = c["under"]
        elif names <= {"rimb", "rimt"}:
            v = c["rim"]
        else:
            uu = u + c["nz"] * nf(p) + c["chk"] * (1 if rng.random() < 0.5 else -1)
            if uu < c["lo"]:
                v = max(-1.0, (uu - c["lo"]) / c["lo_ramp"])
            elif uu > c["hi"]:
                v = min(1.0, (uu - c["hi"]) / c["hi_ramp"])
            else:
                v = 0.0
            if "rimt" in names:
                v = min(v, -0.25)
        f.material_index = a._mi(_key(lad, v))
    _mottle(a, faces, CAP_MOTTLE["amp"], CAP_MOTTLE["scale"], CAP_MOTTLE["seed"] + seed)


def _cap(a, which, droop=True, at_origin=False):
    s = _cap_spec(which, droop, at_origin)
    pts, faces, info = _cap_geom(s)
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    fs = [bm.faces.new([vs[i] for i in f]) for f in faces]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    a._finish(vs, CAP)
    _paint_cap(a, fs, [[info[i] for i in f] for f in faces], s, 0 if which == "big" else 7)
    zs = [p.z for p in pts]
    xs = [p.x for p in pts]
    CAP_INFO[which] = dict(x=(round(min(xs), 2), round(max(xs), 2)), z=(round(min(zs), 2), round(max(zs), 2)),
                           tris=len(fs))
    return vs


# ---- gems ------------------------------------------------------------------------------------------------------------
# spec 2.3: (label, cap, diameter, where, a, b). where "front" / "rear": (a, b) = the gem centre's (f, h) in the sheet's
# front / rear cell (fractions of the view's silhouette), placed by a ray from that camera onto the drooped cap; "lathe":
# (rho, phi deg) in the cap's own lathe frame (rho 0 apex, 1 rim; phi from +X ccw), a vertical ray. The undrooped
# Shell part uses each gem's lathe fallback LATHE[label].
GEMS = (("S1", "big", 1.40, "front", 0.60, 0.90), ("S2", "big", 1.10, "front", 0.18, 0.77),
        ("S3", "big", 0.70, "front", 0.25, 0.68), ("S4", "big", 0.45, "front", 0.05, 0.55),
        ("S5", "big", 1.15, "rear", 0.76, 0.84), ("S6", "big", 0.85, "lathe", 0.70, 60.0),
        ("s1", "small", 0.75, "front", 0.71, 0.59), ("s2", "small", 0.62, "front", 0.90, 0.52),
        ("s3", "small", 0.40, "front", 0.77, 0.49), ("s4", "small", 0.30, "lathe", 0.82, 20.0),
        ("s5", "small", 0.50, "rear", 0.16, 0.60))
LATHE = {"S1": (0.42, 10.0), "S2": (0.62, 205.0), "S3": (0.80, 252.0), "S4": (0.88, 180.0), "S5": (0.62, 140.0),
         "S6": (0.70, 60.0), "s1": (0.30, 160.0), "s2": (0.62, 320.0), "s3": (0.70, 240.0), "s4": (0.86, 0.0),
         "s5": (0.65, 80.0)}
# the sheet cameras' view boxes in the build frame (x0, x1 of the silhouette; v0, v1 its screen-height range, v = z cos
# el + y sin el from the front, z cos el - y sin el from the rear), measured on the hero
VIEW_EL = 8.0
VIEW_BOX = {"front": (-3.70, 3.65, -0.33, 5.37), "rear": (-3.70, 3.65, -0.34, 5.23)}
POCKET_MIN = 0.6         # decision 5: gems of this diameter or more sit in carved pockets
# the loose Spot Insert: a rounded nugget (the exploded insert reads W : H 1.08 because its pavilion shows)
SPOT_PART = dict(crown=0.30, pav=0.62)
AXIS_LEAN = {"S2": 0.4, "S3": 0.25, "S4": 0.35}
GEM_SHAPE = dict(n=8, mid_r=0.43, table_r=0.28, mid_h=0.5, pav=0.45, proud=0.12, girdle_up=0.02)
# the pocket: circumradius / d; a shallow recess, its floor rec x d under the mean surface round the rim (spec: "shallow
# recess", a floor about 0.10 d down); the table proud x d above that mean surface
POCKET = dict(r=0.58, rec=0.08, top=0.3)
BEZEL = dict(r=0.64, sink=0.05, lift=0.025)     # small gems: dark collar ring radius / d, its sink, the girdle's lift
GEM_INFO = {}


def _profile_u(rings, rho):
    """The dome's height fraction at plan radius fraction rho (rings above the rim, rim -> apex)."""
    prof = [(1.0, RIM_U)] + [(r, u) for nm, r, u in rings if nm in ("sh", "ush", "crown")] + [(0.0, 1.0)]
    for (r0, u0), (r1, u1) in zip(prof, prof[1:]):
        if r1 <= rho <= r0:
            t = (r0 - rho) / max(r0 - r1, 1e-6)
            return u0 + (u1 - u0) * t
    return 1.0 if rho < 0.5 else RIM_U


def _gem_frames(which, droop=True, at_origin=False, labels=None):
    """Each gem on its cap: the surface point p (a vertical ray at the drooped lathe position), the local normal n
    (area-weighted face normals within 0.55 d), a tangent frame turned by a seeded twist, and the rim samples that set
    the pocket floor (POCKET["wall"] d below the lowest surface point on the pocket's rim circle)."""
    s = _cap_spec(which, droop, at_origin)
    tree, pts, faces = _cap_tree(s)
    area = [((pts[f[1]] - pts[f[0]]).cross(pts[f[2]] - pts[f[0]])).length / 2 for f in faces]
    nrm = [((pts[f[1]] - pts[f[0]]).cross(pts[f[2]] - pts[f[0]])).normalized() for f in faces]
    out = []
    el = math.radians(VIEW_EL)
    for lab, cap, d, where, ga, gb in GEMS:
        if cap != which or (labels and lab not in labels):
            continue
        if where in VIEW_BOX and droop and not at_origin:
            x0, x1, v0, v1 = VIEW_BOX[where]
            v = v0 + gb * (v1 - v0)
            if where == "front":
                X, dirv, up = x0 + ga * (x1 - x0), Vector((0, math.cos(el), -math.sin(el))), \
                    Vector((0, math.sin(el), math.cos(el)))
            else:
                X, dirv, up = x1 - ga * (x1 - x0), Vector((0, -math.cos(el), -math.sin(el))), \
                    Vector((0, -math.sin(el), math.cos(el)))
            q = Vector((X, 0, 0)) + up * v
            hit = tree.ray_cast(q - dirv * 30, dirv)
            if hit[0] is None:          # the ray misses this cap (e.g. it grazes the rim): nearest surface point
                loc, nn, idx, _ = tree.find_nearest(q)
                hit = (loc, nn, idx, 0.0)
        else:
            rho, phi = (ga, gb) if where == "lathe" else LATHE[lab]
            u = _profile_u(s["rings"], rho)
            w = (u - RIM_U) / (1 - RIM_U)
            x = s["c"][0] + math.cos(math.radians(phi)) * rho * s["rx"] + s["e"] * w
            y = s["c"][1] + math.sin(math.radians(phi)) * rho * s["ry"]
            hit = tree.ray_cast(Vector((x, y, 50.0)), Vector((0, 0, -1)))
        p = hit[0]
        acc = Vector()
        for loc, _n, idx, dist in tree.find_nearest_range(p, 0.55 * d):
            acc += nrm[idx] * area[idx]
        n = acc.normalized() if acc.length > 1e-9 else hit[1]
        if n.dot(nrm[hit[2]]) < 0:
            n = -n
        rng = random.Random(hash_str(lab) + 30100)
        tw = rng.uniform(0, math.pi / 4)
        t1 = n.cross(Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))).normalized()
        t2 = n.cross(t1).normalized()
        t1, t2 = t1 * math.cos(tw) + t2 * math.sin(tw), -t1 * math.sin(tw) + t2 * math.cos(tw)

        def rim(r, n, t1, t2):
            pts_ = []
            for k in range(16):
                a_ = 2 * math.pi * k / 16
                q = p + (t1 * math.cos(a_) + t2 * math.sin(a_)) * r + n * 1.5
                h = tree.ray_cast(q, -n, 4.0)
                pts_.append(h[0] if h[0] is not None else q - n * 2.0)
            return pts_
        pocket = d >= POCKET_MIN
        r_rim = (POCKET["r"] if pocket else BEZEL["r"]) * d
        # the gem's axis: the normal of the plane fitted to the surface round its rim (two passes), so the recess is
        # even all round instead of deep on the uphill side
        for _ in range(2):
            q = np.array([tuple(v) for v in rim(r_rim, n, t1, t2)])
            ctr = q.mean(0)
            nf = Vector(np.linalg.svd(q - ctr)[2][2])
            nf = nf if nf.dot(n) > 0 else -nf
            n = nf.normalized()
            t1 = (t1 - n * t1.dot(n)).normalized()
            t2 = n.cross(t1).normalized()
        # the big cap's droop turns its whole -X flank toward the side camera; the sheet draws the front-left gems
        # nearly face-on from the front (S2 35 x 31 px), so their axes lean part way toward the front camera
        k = AXIS_LEAN.get(lab, 0.0) if droop and not at_origin else 0.0
        if k:
            n = (n + Vector((0, -math.cos(el), math.sin(el))) * k).normalized()
            t1 = (t1 - n * t1.dot(n)).normalized()
            t2 = n.cross(t1).normalized()
        hs = [(v - p).dot(n) for v in rim(r_rim, n, t1, t2)]
        out.append(dict(label=lab, cap=which, d=d, p=p, n=n, t1=t1, t2=t2, pocket=pocket,
                        low=min(hs), high=max(hs), mean=sum(hs) / len(hs)))
    return out


def hash_str(s):
    return sum((i + 1) * ord(ch) for i, ch in enumerate(s))


def _frame_m(g):
    return Matrix((g["t1"], g["t2"], g["n"])).transposed()


def _gem(a, g, whole=False):
    """One gem in its frame (girdle at local z 0): 8-sided girdle, a mid crown ring turned half a step, a flat table
    (Ø 0.62 of the girdle), a pavilion cone below. Pocket gems: the girdle GEM_SHAPE["girdle_up"] above the pocket
    floor, the table GEM_SHAPE["proud"] d above the surface point. Small gems: a dark bezel collar (cap_dark) from a
    ring sunk under the surface up to the girdle, which sits just above the surface (decision 5's dark ring).
    whole: the loose Spot Insert (girdle at its own z, crown 0.22 d, pavilion 0.45 d)."""
    gs = GEM_SHAPE
    d = g["d"]
    n = gs["n"]
    bm = a.bm
    if whole:
        z_g, crown, collar = 0.0, SPOT_PART["crown"] * d, None
    elif g["pocket"]:
        z_g = g["mean"] - POCKET["rec"] * d + gs["girdle_up"]
        crown = g["mean"] + gs["proud"] * d - z_g
        collar = None
    else:
        z_g = max(g["mean"], 0.0) + BEZEL["lift"]
        crown = max(0.12 * d, g["mean"] + gs["proud"] * d - z_g)
        collar = (BEZEL["r"] * d, g["low"] - BEZEL["sink"] - z_g)
    m = Matrix.Identity(3) if whole else _frame_m(g)
    o = Vector((0, 0, 0)) if whole else g["p"] + g["n"] * z_g

    def P(r, ang, z):
        return o + m @ Vector((math.cos(ang) * r, math.sin(ang) * r, z))
    step = 2 * math.pi / n
    G = [bm.verts.new(P(0.5 * d, k * step, 0.0)) for k in range(n)]
    Mi = [bm.verts.new(P(gs["mid_r"] * d, (k + 0.5) * step, gs["mid_h"] * crown)) for k in range(n)]
    T = [bm.verts.new(P(gs["table_r"] * d, k * step, crown)) for k in range(n)]
    tc = bm.verts.new(P(0.0, 0.0, crown))
    low_row = _band(bm, G, Mi, 0)
    up_row = []
    for k in range(n):        # Mi[k] sits between T[k] and T[k + 1]
        up_row.append(bm.faces.new((T[k], T[(k + 1) % n], Mi[k])))
        up_row.append(bm.faces.new((Mi[k], Mi[(k + 1) % n], T[(k + 1) % n])))
    table = _fan(bm, T, tc)
    vs = G + Mi + T + [tc]
    dark = []
    if collar:
        C = [bm.verts.new(P(collar[0], k * step, collar[1])) for k in range(n)]
        for k in range(n):
            j = (k + 1) % n
            dark += [bm.faces.new((C[k], C[j], G[j])), bm.faces.new((C[k], G[j], G[k]))]
        apex = bm.verts.new(P(0.0, 0.0, collar[1] - gs["pav"] * d * 0.6))
        pav = _fan(bm, C, apex)
        vs += C + [apex]
    else:
        apex = bm.verts.new(P(0.0, 0.0, -(SPOT_PART["pav"] if whole else gs["pav"]) * d))
        pav = _fan(bm, G, apex)
        vs += [apex]
    allf = low_row + up_row + table + pav + dark
    bmesh.ops.recalc_face_normals(bm, faces=allf)
    a._finish(vs, GEM, tint=1.0)
    # the lower crown row alternates: triangles standing on the girdle deep, the ones hanging from the mid ring mid
    # (the sheet's split is about 25 / 48 / 27 deep / mid / light)
    for fs, k in ((low_row[0::2], GEM_DEEP), (low_row[1::2], GEM), (pav, GEM_DEEP), (up_row, GEM), (table, GEM_LIGHT),
                  (dark, CAP_DARK)):
        mi = a._mi(k)
        for f in fs:
            f.material_index = mi
    GEM_INFO[g["label"]] = dict(d=d, pocket=g["pocket"], girdle=round(z_g, 3), crown=round(crown, 3),
                                p=[round(c, 2) for c in g["p"]], n=[round(c, 2) for c in g["n"]],
                                rim_low=round(g["low"], 3), rim_high=round(g["high"], 3),
                                rim_mean=round(g["mean"], 3))
    return vs


def _cutter(a, g):
    """The 8-sided pocket prism (cap_dark): floor POCKET["wall"] d below the lowest rim point, top above the highest."""
    d = g["d"]
    m = _frame_m(g)
    n = GEM_SHAPE["n"]
    r = POCKET["r"] * d
    z0 = g["mean"] - POCKET["rec"] * d
    z1 = max(g["high"], 0.0) + POCKET["top"]
    bm = a.bm
    rows = []
    for z in (z0, z1):
        rows.append([bm.verts.new(g["p"] + m @ Vector((math.cos(k * 2 * math.pi / n) * r,
                                                      math.sin(k * 2 * math.pi / n) * r, z))) for k in range(n)])
    c0 = bm.verts.new(g["p"] + m @ Vector((0, 0, z0)))
    c1 = bm.verts.new(g["p"] + m @ Vector((0, 0, z1)))
    fs = []
    for k in range(n):
        j = (k + 1) % n
        fs += [bm.faces.new((rows[0][k], rows[0][j], rows[1][j])), bm.faces.new((rows[0][k], rows[1][j], rows[1][k])),
               bm.faces.new((rows[0][j], rows[0][k], c0)), bm.faces.new((rows[1][k], rows[1][j], c1))]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    a._finish(rows[0] + rows[1] + [c0, c1], CAP_DARK, tint=1.0)


# ---- stems -----------------------------------------------------------------------------------------------------------
# spec 1.4 hero profiles: (z, diameter) from the foot up; the last ring is set 0.15 above the cap's join ring
STEMS = {
    "big": dict(xy=(-0.20, 0.35), n=10, seed=30201, cap="big",
                prof=((-0.1, 1.83), (0.5, 2.20), (1.1, 2.38), (1.6, 2.42), (2.2, 2.25), (2.7, 1.90), (3.1, 1.60))),
    "small": dict(xy=(1.85, -1.35), n=8, seed=30202, cap="small",
                  prof=((-0.1, 1.18), (0.45, 1.45), (0.9, 1.47), (1.4, 1.30), (1.8, 1.08), (2.15, 0.95))),
}
STEM_TOP_D = {"big": 1.48, "small": 0.92}
STEM_IN = 0.15
STEM_COL = dict(base=0.25, width=0.15, nz=0.05, seed=30211)
STEM_MOTTLE = dict(amp=0.03, scale=0.5, seed=30212)


def _stem(a, which, at_origin=False):
    st = STEMS[which]
    cs = CAPS[st["cap"]]
    top = cs["z0"] + 0.20 * cs["hc"] + STEM_IN
    prof = list(st["prof"]) + [(top, STEM_TOP_D[which])]
    if at_origin:
        prof = [(max(0.0, z), d) for z, d in prof]
    rng = random.Random(st["seed"])
    n = st["n"]
    x0, y0 = (0.0, 0.0) if at_origin else st["xy"]
    bm = a.bm
    rows = []
    for i, (z, dia) in enumerate(prof):
        off = (i % 2) * math.pi / n
        jz = rng.uniform(-0.04, 0.04) if 0 < i < len(prof) - 1 else 0.0
        rows.append([bm.verts.new((x0 + math.cos(2 * math.pi * k / n + off) * dia / 2 * (1 + rng.uniform(-0.04, 0.04)),
                                   y0 + math.sin(2 * math.pi * k / n + off) * dia / 2 * (1 + rng.uniform(-0.04, 0.04)),
                                   z + jz)) for k in range(n)])
    fs = []
    for i in range(len(rows) - 1):
        fs += _band(bm, rows[i], rows[i + 1], 0 if i % 2 == 0 else 1)
    cb = bm.verts.new((x0, y0, prof[0][0]))
    ct = bm.verts.new((x0, y0, prof[-1][0]))
    ends = _fan(bm, rows[0], cb) + _fan(bm, rows[-1], ct)
    vs = [v for r in rows for v in r] + [cb, ct]
    bmesh.ops.recalc_face_normals(bm, faces=fs + ends)
    a._finish(vs, STEM)       # the end fans (foot on the ground, top inside the cap) keep the plain stem key
    # colour: the lowest STEM_COL["base"] of the stem's visible height -> stem_base, blending into stem
    c = STEM_COL
    H = prof[-1][0] - max(0.0, prof[0][0])
    lad = [STEM_BASE] + [K.mix_key(STEM_BASE, STEM, t) for t in (0.25, 0.5, 0.75)] + [STEM]
    nf = K.noise_field(scale=0.8, seed=c["seed"] + n)
    for f in fs:
        p = f.calc_center_median()
        t = ((p.z - max(0.0, prof[0][0])) / H - c["base"] + c["nz"] * nf(p)) / c["width"] + 0.5
        f.material_index = a._mi(lad[int(round(max(0.0, min(1.0, t)) * 4))])
    _mottle(a, fs + ends, STEM_MOTTLE["amp"], STEM_MOTTLE["scale"], STEM_MOTTLE["seed"] + n)
    return vs


# ---- leaves ----------------------------------------------------------------------------------------------------------
# a thick kite leaf (spec 1.4): base, two outline points per side at 0.30 / 0.58 L (half-widths 0.30 / 0.50 W), tip;
# a midrib ridge raised 0.6 T at 0.45 L (and a lower one at 0.75 L), a keel 0.4 T under it. W = WL x L, T = 0.10 L.
WL, TL = 0.44, 0.10
# clumps (spec 2.2): root (x, y, z) and leaves (L, azimuth deg, elevation deg, roll deg, seed)
CLUMPS = {
    # (round 1: broader, shorter, more splayed fans sitting on the back rocks, as the rear cell draws them; the first
    # upright spikes hid the back boulders: rear R 19.7 against 24.8)
    "L1": dict(root=(1.55, 1.2, 0.8), leaves=((1.7, 95.0, 70.0, 0.0, 30301), (1.5, 55.0, 48.0, 15.0, 30302),
                                               (1.55, 135.0, 50.0, -15.0, 30303), (1.3, 15.0, 35.0, 20.0, 30304),
                                               (1.35, 170.0, 38.0, -20.0, 30305))),
    "L2": dict(root=(-2.0, 1.1, 0.65), leaves=((1.35, 120.0, 68.0, 0.0, 30311), (1.15, 168.0, 45.0, -15.0, 30312),
                                               (1.2, 72.0, 48.0, 15.0, 30313), (1.0, 205.0, 36.0, -20.0, 30314))),
}
HUB_Z = 0.1            # every hero leaf's hidden root point sinks into the slab here,
HUB_R = 0.16           # HUB_R out toward the leaf's own azimuth (closer hubs left needles where the hulls met)
LEAF_COL = dict(base=0.3, tip=0.7, nz=0.08, seed=30321)
LEAF_MOTTLE = dict(amp=0.03, scale=0.5, seed=30322)
LEAF_INFO = {}


def _leaf(a, root, L, az, el, roll, seed, tag, hub):
    rng = random.Random(seed)
    W, T = WL * L * (1 + rng.uniform(-0.05, 0.05)), TL * L
    j = lambda s_: 1 + rng.uniform(-s_, s_)
    loc = [Vector((0.0, 0.0, 0.0)), Vector((L, rng.uniform(-0.02, 0.02) * L, 0.0))]
    for side in (-1, 1):
        loc.append(Vector((0.30 * L * j(0.05), side * 0.30 * W * j(0.06), 0.0)))
        loc.append(Vector((0.58 * L * j(0.04), side * 0.50 * W * j(0.06), 0.0)))
    loc += [Vector((0.45 * L, 0.0, 0.6 * T * j(0.05))), Vector((0.75 * L, 0.0, 0.35 * T * j(0.05))),
            Vector((0.45 * L, 0.0, -0.4 * T * j(0.05))), Vector((0.15 * L, 0.0, 0.25 * T))]
    a_, e_ = math.radians(az), math.radians(el)
    d = Vector((math.cos(e_) * math.cos(a_), math.cos(e_) * math.sin(a_), math.sin(e_)))
    t = Vector((-math.sin(a_), math.cos(a_), 0.0))
    nn = d.cross(t).normalized()
    if nn.z < 0:
        t, nn = -t, -nn
    r = Matrix.Rotation(math.radians(roll), 3, d)
    t, nn = r @ t, r @ nn
    m = Matrix((d, t, nn)).transposed()
    base = Vector(root)
    # the buried root: a point near the clump's centre, below the base, own to each leaf (a vertex shared by two
    # leaves' hulls made m025's exact union drop the base), so every leaf of a clump overlaps the others
    hub = Vector((hub[0], hub[1], min(HUB_Z, hub[2] - 0.18))) + Vector((math.cos(a_), math.sin(a_), 0.0)) * HUB_R
    vs = _hull(a, [base + m @ p for p in loc] + [hub])
    a._finish(vs, LEAF)
    lad = [LEAF_BASE, K.mix_key(LEAF_BASE, LEAF, 0.5), LEAF, K.mix_key(LEAF, LEAF_TIP, 0.5), LEAF_TIP]
    nf = K.noise_field(scale=0.9, seed=LEAF_COL["seed"] + seed)
    for f in _faces(vs):
        c = f.calc_center_median()
        tt = (c - base).dot(d) / L + LEAF_COL["nz"] * nf(c)
        k = 0 if tt < LEAF_COL["base"] - 0.08 else 1 if tt < LEAF_COL["base"] + 0.06 else \
            2 if tt < LEAF_COL["tip"] - 0.06 else 3 if tt < LEAF_COL["tip"] + 0.08 else 4
        f.material_index = a._mi(lad[k])
    _mottle(a, _faces(vs), LEAF_MOTTLE["amp"], LEAF_MOTTLE["scale"], LEAF_MOTTLE["seed"] + seed,
            tint=1.0 + random.Random(seed).uniform(-0.04, 0.04))
    tip = base + d * L
    LEAF_INFO[tag] = dict(L=L, tip=[round(c, 2) for c in tip], faces=len(_faces(vs)))
    return vs


def _clump(a, name, at_origin=False):
    cl = CLUMPS[name]
    root = (0.0, 0.0, 0.0) if at_origin else cl["root"]
    out = []
    for i, (L, az, el, roll, seed) in enumerate(cl["leaves"]):
        r = Vector(root) + Vector((math.cos(math.radians(az)), math.sin(math.radians(az)), 0)) * 0.08
        out.append(_leaf(a, r, L, az, el, roll, seed, f"{name}.{i}", root))
    return out


# ---- base: slab, boulders, pebbles -----------------------------------------------------------------------------------
SLAB = dict(c=(0.15, 0.0), rx=2.5, ry=1.9, n=14, seed=30401)
SLAB_RINGS = ((-0.05, 1.0, 0.0, 0.0), (0.24, 0.97, 0.03, 0.02), (0.30, 0.62, 0.04, 0.02))
SLAB_TOP = 0.34


def _slab(a, at_origin=False):
    rng = random.Random(SLAB["seed"])
    bm = a.bm
    n = SLAB["n"]
    cx, cy = (0.0, 0.0) if at_origin else SLAB["c"]
    rows = []
    for i, (z, rf, rj, zj) in enumerate(SLAB_RINGS):
        off = (i % 2) * math.pi / n
        rows.append([bm.verts.new((cx + math.cos(2 * math.pi * k / n + off) * SLAB["rx"] * rf * (1 + rng.uniform(-rj, rj)),
                                   cy + math.sin(2 * math.pi * k / n + off) * SLAB["ry"] * rf * (1 + rng.uniform(-rj, rj)),
                                   z + rng.uniform(-zj, zj))) for k in range(n)])
    fs = []
    for i in range(len(rows) - 1):
        fs += _band(bm, rows[i], rows[i + 1], 0 if i % 2 == 0 else 1)
    top = bm.verts.new((cx + rng.uniform(-0.1, 0.1), cy + rng.uniform(-0.1, 0.1), SLAB_TOP))
    bot = bm.verts.new((cx, cy, -0.05))
    fs += _fan(bm, rows[-1], top) + _fan(bm, rows[0], bot)
    vs = [v for r in rows for v in r] + [top, bot]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    a._finish(vs, DIRT)
    return vs


ROCK_RINGS = ((0.0, 0.93, 7), (0.38, 1.0, 7), (0.74, 0.74, 5), (1.0, 0.22, 2))
ROCK_Z0 = -0.1
# boulders (spec 2.2): (label, x, y, d, h, seed)
BOULDERS = (("B1", -2.05, -1.00, 1.6, 1.15, 30501), ("B2", -0.95, -1.65, 1.35, 1.00, 30502),
            ("B3", 0.35, -1.75, 1.6, 1.15, 30503), ("B4", 1.55, -1.85, 1.25, 0.90, 30504),
            ("B5", 2.50, -1.35, 1.3, 0.95, 30505), ("B6", 2.45, 0.25, 1.5, 1.1, 30506),
            ("B7", 2.35, 1.15, 1.5, 1.1, 30507), ("B8", 0.20, 1.50, 2.0, 1.4, 30508),
            ("B9", -1.40, 1.50, 1.55, 1.15, 30509), ("B10", -2.25, 0.50, 1.6, 1.2, 30510),
            # (round 1: two back boulders behind the leaf clumps, so from behind the leaves stand on a continuous rock
            # band as the rear cell draws it; without them the clumps' feet filled the gaps, rear R 19.4 against 24.8)
            ("B11", 1.35, 1.95, 1.15, 0.85, 30511), ("B12", -2.5, 1.45, 1.1, 0.8, 30512))
PEBBLES = (("Pa", -1.0, -2.25, 0.6, 0.4, 30521), ("Pb", 0.95, -2.3, 0.5, 0.35, 30522),
           ("Pc", 2.72, -0.55, 0.6, 0.42, 30523))
ROCK_INFO = {}


def _boulders(a, at_origin=False):
    out = {}
    dx = -SLAB["c"][0] if at_origin else 0.0
    for lab, x, y, d, h, seed in BOULDERS:
        rot = random.Random(seed).uniform(0, 2 * math.pi)
        # each boulder's flat bottom at its own depth under the ground: coplanar overlapping bottoms (B1 / B2) made the
        # exact unions leave self-intersecting slivers
        z0 = ROCK_Z0 - 0.013 * len(out)
        vs = K.hull_rock(a, (d, d * 0.88, h - z0), loc=(x + dx, y, z0), seed=seed, mat=ROCK, rings=ROCK_RINGS,
                         jitter=0.12, rot=rot, keep_bottom=True)
        _tri(a.bm, _faces(vs))
        bmesh.ops.recalc_face_normals(a.bm, faces=_faces(vs))
        out[lab] = (vs, z0, h - z0)
        ROCK_INFO[lab] = dict(xy=(x, y), d=d, h=h, tris=len(_faces(vs)))
    for lab, x, y, d, h, seed in PEBBLES:
        z0 = ROCK_Z0 - 0.013 * len(out)
        vs = K.hull_rock(a, (d, d * 0.85, h - z0), loc=(x + dx, y, z0), seed=seed, mat=ROCK_DARK,
                         rings=((0.0, 0.92, 5), (0.45, 1.0, 5), (1.0, 0.35, 3)), jitter=0.12,
                         rot=random.Random(seed).uniform(0, 6.28), keep_bottom=True)
        _tri(a.bm, _faces(vs))
        bmesh.ops.recalc_face_normals(a.bm, faces=_faces(vs))
        out[lab] = (vs, z0, h - z0)
    return out


ROCK_PATCH = dict(scale=0.55, level=-0.05, width=0.3, mix=0.75, seed=30531)
ROCK_GROUND = (0.15, 0.35)
ROCK_CONTACT = (0.2, 0.25)
ROCK_MOTTLE = dict(amp=0.06, scale=0.45, seed=30532)
DIRT_PATCH = dict(scale=0.6, level=0.15, seed=30541)
DIRT_MOTTLE = dict(amp=0.06, scale=0.45, seed=30542)


def _paint_rocks(a, rocks, stem_trees=()):
    lad = _ladder(ROCK_DARK, ROCK, ROCK_LIGHT)
    nf = K.noise_field(scale=ROCK_PATCH["scale"], seed=ROCK_PATCH["seed"])
    trees = {k: K.bvh_of(v[0]) for k, v in rocks.items()}
    others = list(stem_trees)
    for i, (lab, (vs, z0, H)) in enumerate(rocks.items()):
        peb = lab.startswith("P")
        for f in _faces(vs):
            c = f.calc_center_median()
            hf = (c.z - max(z0, 0.0)) / H
            if peb:
                v = -0.75 if nf(c) < 0.2 else -0.5
            else:
                hi = ROCK_PATCH["mix"] * min(1.0, max(0.0, (nf(c) - ROCK_PATCH["level"]) / ROCK_PATCH["width"]))
                if hf < 0.4:
                    hi *= 0.0
                lo = ROCK_GROUND[1] * min(1.0, max(0.0, (2 * ROCK_GROUND[0] - hf) / ROCK_GROUND[0]))
                v = hi - lo
                if hf < 0.7:
                    for j, t in list(trees.items()) + [(None, t) for t in others]:
                        if j == lab:
                            continue
                        loc = t.find_nearest(c)
                        if loc[0] is not None and loc[3] < ROCK_CONTACT[0]:
                            v = min(v, -ROCK_CONTACT[1])
                            break
            f.material_index = a._mi(_key(lad, v))
        _mottle(a, _faces(vs), ROCK_MOTTLE["amp"], ROCK_MOTTLE["scale"], ROCK_MOTTLE["seed"] + i,
                tint=1.0 + random.Random(i * 7 + 3).uniform(-0.04, 0.04))


def _paint_dirt(a, vs, rock_trees=()):
    lad = [DIRT, K.mix_key(DIRT, ROCK_DARK, 0.25)]
    nf = K.noise_field(scale=DIRT_PATCH["scale"], seed=DIRT_PATCH["seed"])
    for f in _faces(vs):
        c = f.calc_center_median()
        k = 0
        if nf(c) > DIRT_PATCH["level"]:
            for t in rock_trees:
                loc = t.find_nearest(c)
                if loc[0] is not None and loc[3] < 0.5:
                    k = 1
                    break
        f.material_index = a._mi(lad[k])
    _mottle(a, _faces(vs), DIRT_MOTTLE["amp"], DIRT_MOTTLE["scale"], DIRT_MOTTLE["seed"])


def _stem_probe():
    """BVHs of the two hero stems (for the rocks' contact darkening), on a throwaway Asset."""
    p = K.fk().Asset("_m030_probe", "probe")
    trees = [K.bvh_of(_stem(p, w)) for w in ("big", "small")]
    p.bm.free()
    return trees


def _base(a, at_origin=False, stem_trees=()):
    slab = _slab(a, at_origin)
    rocks = _boulders(a, at_origin)
    _paint_rocks(a, rocks, stem_trees)
    _paint_dirt(a, slab, [K.bvh_of(v[0]) for v in rocks.values()])
    return slab, rocks


# ---- parts -----------------------------------------------------------------------------------------------------------
def shell_part(a):
    _cap(a, "big", droop=False, at_origin=True)


def spot_part(a):
    g = dict(label="S1", d=1.40, pocket=False, p=Vector(), n=Vector((0, 0, 1)), low=0, high=0, mean=0)
    _gem(a, g, whole=True)


def stalk_large_part(a):
    _stem(a, "big", at_origin=True)


def stalk_small_part(a):
    _stem(a, "small", at_origin=True)


def clump_part(a):
    _clump(a, "L1", at_origin=True)


def rock_base_part(a):
    _base(a, at_origin=True)


# ---- hero ------------------------------------------------------------------------------------------------------------
def hero_body(a):
    """Everything but the gems, in union order: slab, boulders, pebbles, stems, caps, leaves."""
    LEAF_INFO.clear()
    ROCK_INFO.clear()
    _base(a, stem_trees=_stem_probe())
    _stem(a, "big")
    _stem(a, "small")
    _cap(a, "big")
    _cap(a, "small")
    _clump(a, "L1")
    _clump(a, "L2")


def hero_gems(a):
    GEM_INFO.clear()
    for which in ("big", "small"):
        for g in _gem_frames(which):
            _gem(a, g)


def hero_cutters(which, droop=True, at_origin=False, labels=None):
    """One cutter builder per pocket gem: [(label, fn)]."""
    return [(g["label"], (lambda gg: (lambda a: _cutter(a, gg)))(g))
            for g in _gem_frames(which, droop, at_origin, labels) if g["pocket"]]


NOTES = {
    HERO: "Mooncap event node: two chunky faceted violet toadstools (a big flat-crowned cap drooping to -X over a fat "
          "cream pear stem, a small cap drooping to +X on a short stem in front-right), eleven glowing 8-sided cyan "
          "gems set in dark pockets / bezels on the caps (Neon: deep, mid and light facets), a ring of ten domed "
          "brown-grey boulders and three pebbles on a dirt slab, two yellow-green leaf clumps at the back; one closed "
          "mesh. VFX: crystal_glow (a soft cyan light in front of and between the caps)",
    SHELL: "Cap Shell (reusable): the big cap undrooped, a thick faceted flat-crowned dome with a vertical rim band and a "
           "faceted underside cone; five 8-sided gem pockets carved",
    SPOT: "Spot Insert (reusable): an 8-sided faceted cyan gem, flat table, two crown rows, pavilion cone; Neon deep / "
          "mid / light facets",
    STALK_L: "Stem (Large) (reusable): a fat faceted 10-sided pear stem, darker foot band",
    STALK_S: "Stem (Small) (reusable): a faceted 8-sided pear stem, darker foot band",
    CLUMP: "Leaf Clump (reusable): five thick yellow-green kite leaves with a midrib ridge, dark base to bright tip",
    BASE: "Base (reusable): a faceted dirt slab ringed by ten peaky domed brown-grey boulders and three pebbles",
}


# ---- union, carve, floor cut, cleanup ----------------------------------------------------------------------------------
FINE_MERGE = 0.002
UNION_RETRIES = []


def _union_fine(o, merge=FINE_MERGE):
    """M.union_loose with a finer post-union merge (m021) and a guard against a union that drops most of the mesh."""
    bpy.context.view_layer.update()
    act = bpy.context.view_layer.objects.active
    if act and act.mode != "OBJECT":
        with bpy.context.temp_override(active_object=act, object=act):
            bpy.ops.object.mode_set(mode="OBJECT")
    others = M.split_loose(o)
    bpy.context.view_layer.update()
    for p in others:
        for attempt in range(4):
            keep = o.data.copy()
            n0 = len(o.data.polygons) + len(p.data.polygons)
            m = o.modifiers.new("U", "BOOLEAN")
            m.operation, m.solver, m.object = "UNION", "EXACT", p
            m.material_mode = "TRANSFER"
            with M._override(o):
                bpy.ops.object.modifier_apply(modifier=m.name)
            if len(o.data.polygons) >= 0.6 * n0 or attempt == 3:
                bpy.data.meshes.remove(keep)
                break
            bad = o.data
            o.data = keep
            bpy.data.meshes.remove(bad)
            UNION_RETRIES.append((p.name, attempt))
            p.location += Vector((0.004, 0.003, 0.002)) * (attempt + 1)
            bpy.context.view_layer.update()
        me = p.data
        bpy.data.objects.remove(p, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    _weld_clean(o, merge)
    return len(others)


def _weld_clean(o, merge):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=merge)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    M.drop_specks(bm, min_area=0.02)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    K.drop_unused_slots(o)


def _temp_obj(o, fn, name):
    """fn's geometry (build frame) as a temporary object lined up with o (whose mesh is shifted by o[OFF])."""
    a = K.fk().Asset(PFX + name, "probe", seed=7, tint_var=0.0)
    fn(a)
    c = a.finish(collection=o.users_collection[0], mark_asset=False, origin=None)
    c.matrix_world = o.matrix_world @ Matrix.Translation(-Vector(o[OFF]))
    bpy.context.view_layer.update()
    return c


CARVE_LOG = []


def _carve(o, cutters):
    """Exact differences, one cutter at a time (decision 7); the new faces take the cutter's cap_dark key."""
    for lab, fn in cutters:
        c = _temp_obj(o, fn, "cut_" + lab)
        keep = o.data.copy()
        n0 = len(o.data.polygons)
        m = o.modifiers.new("Carve", "BOOLEAN")
        m.operation, m.solver, m.object = "DIFFERENCE", "EXACT", c
        m.material_mode = "TRANSFER"
        with M._override(o):
            bpy.ops.object.modifier_apply(modifier=m.name)
        n1 = len(o.data.polygons)
        ok = n1 >= 0.8 * n0
        if not ok:
            bad = o.data
            o.data = keep
            bpy.data.meshes.remove(bad)
        else:
            bpy.data.meshes.remove(keep)
        CARVE_LOG.append((o.name, lab, n0, n1, ok))
        me = c.data
        bpy.data.objects.remove(c, do_unlink=True)
        bpy.data.meshes.remove(me)
        _weld_clean(o, FINE_MERGE)


def _append(o, fn, name):
    """Join fn's geometry (build frame) into o's mesh (bmesh, no operator context): materials by palette key, Tint
    copied."""
    c = _temp_obj(o, fn, name)
    src = bmesh.new()
    src.from_mesh(c.data)
    dst = bmesh.new()
    dst.from_mesh(o.data)
    sl = src.loops.layers.float_color.get("Tint")
    dl = dst.loops.layers.float_color.get("Tint")
    keys = [m.get("flintkit_key") or m.name[3:] for m in o.data.materials]
    mis = []
    for m in c.data.materials:
        k = m.get("flintkit_key") or m.name[3:]
        if k not in keys:
            o.data.materials.append(K.fk().material(k))
            keys.append(k)
        mis.append(keys.index(k))
    mat = o.matrix_world.inverted() @ c.matrix_world          # build frame -> o's mesh (shifted by o[OFF])
    vmap = {v: dst.verts.new(mat @ v.co) for v in src.verts}
    for f in src.faces:
        nf = dst.faces.new([vmap[v] for v in f.verts])
        nf.material_index = mis[f.material_index]
        nf.smooth = False
        for l, nl in zip(f.loops, nf.loops):
            t = l[sl][0] if sl else 1.0
            nl[dl] = (t, t, t, 1.0)
    dst.to_mesh(o.data)
    dst.free()
    src.free()
    me = c.data
    bpy.data.objects.remove(c, do_unlink=True)
    bpy.data.meshes.remove(me)


def _floor_cut(o, z0=0.0):
    """Cut everything below the ground plane and cap the cut with one triangle fill (m025)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), plane_co=(0, 0, z0),
                           plane_no=(0, 0, -1), clear_outer=True)
    below = [v for v in bm.verts if v.co.z < z0 - 1e-4]
    if below:
        bmesh.ops.delete(bm, geom=below, context="VERTS")
    for v in bm.verts:
        if v.co.z < z0 + 0.02:
            v.co.z = z0
        v.co.z -= z0
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    bnd = [e for e in bm.edges if e.is_boundary]
    made = 0
    if bnd:
        res = bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=bnd, normal=(0, 0, -1))
        made = len(res["geom"])
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=0.004)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    return made


def _finish(o):
    o[OFF] = list(Vector(o[OFF]) + m012._bottom_centre(o))
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
        o[OFF] = list(Vector(o[OFF]) + m012._bottom_centre(o))
        res = M.finish(o, union=False, uv=UV)
    return res


def _refan_floor(bm):
    """m023's floor re-fan: the floor cap's big needle triangles poked, its inner edges beautified, and any floor
    sliver left split by a point on its long inner edge (no needles on the ground)."""
    zmin = min(v.co.z for v in bm.verts)
    floor = [f for f in bm.faces if f.normal.z < -0.999 and all(abs(v.co.z - zmin) < 1e-4 for v in f.verts)]
    if not floor:
        return
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


def _polish(o):
    """Quads split, slivers forced open, origin back at the bottom centre, UVs redone (m025)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = m012._tri_quads(bm)
    _refan_floor(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = m012._force_slivers(o, lim=POLISH_LIM)
    if m012._thin(o, POLISH_LIM)["under"]:
        forced += m012._force_slivers(o, lim=POLISH_LIM, max_len=0.5)
    bc = m012._bottom_centre(o)
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
    """Faces lying on the ground plane (the floor cut's cap): the plain rock key, one even colour (m025)."""
    p = m011._Paint(o, off=o[OFF])
    n = 0
    for f in p.bm.faces:
        if all(abs(v.co.z) < 1e-3 for v in f.verts):
            f.material_index = p._mi(ROCK)
            n += 1
    p.done()
    return n


def _gem_tint(o):
    """Neon keys must stay one flat colour: Tint 1 on every gem-key face (the union can average loop colours)."""
    tint = o.data.color_attributes.get("Tint")
    if tint is None:
        return 0
    idx = {i for i, m in enumerate(o.data.materials) if m and m.get("flintkit_key") in GEM_KEYS}
    n = 0
    for p in o.data.polygons:
        if p.material_index in idx:
            for li in p.loop_indices:
                if abs(tint.data[li].color[0] - 1.0) > 1e-4:
                    n += 1
                tint.data[li].color = (1.0, 1.0, 1.0, 1.0)
    return n


def _sane(o, limit=30.0):
    co = [v.co for v in o.data.vertices]
    ext = max(max(abs(c[i]) for c in co) for i in range(3))
    if ext > limit:
        raise RuntimeError(f"{o.name}: a vertex {ext:.1f} studs from its origin; not unioning it")


def _make(name, fn, role, budget, union=False, ground=False, cutters=(), gems=None):
    t0 = time.time()
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget, collision="hull",
             tint_var=0.04)
    off = M._build_offset(fn)
    o[OFF] = list(off)
    # booleans at the world origin: a rebuilt object keeps its display slot (x about 1700), where the operands'
    # float32 matrices are off by about 1e-4 and the exact unions came out self-intersecting. M.display puts it back.
    o.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    lg = {}
    if union:
        _sane(o)
        lg["shells_merged"] = _union_fine(o)
    if cutters:
        _carve(o, cutters)
        lg["carved"] = len(cutters)
    if gems:
        _append(o, gems, "gems")
        lg["gem_shells"] = _union_fine(o)
    if ground:
        lg["cap"] = _floor_cut(o, z0=-off.z)
        o[OFF] = [off.x, off.y, 0.0]
        lg["clean"] = {k: v for k, v in m016._clean_mesh(o, (0.0,)).items() if not isinstance(v, (list, dict))}
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    if ground:
        lg["ground_faces"] = _ground_faces(o)
    lg["bowties"] = M.fix_bowties(o)
    lg["gem_tint_reset"] = _gem_tint(o)
    K.drop_unused_slots(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


# ---- stages 5 + 6 (spec section 7, decision 8) -------------------------------------------------------------------------
# Stage 5: the three gem keys are Neon (emission GEM_EMIT, previewed unlit by _glow_mats); one soft cyan PointLight in
# the open in front of and between the caps (crystal_glow, light only). Stage 6: nothing else (the sheet draws no halo,
# spores or sparkle).
GLOW_LIGHT = dict(pos=(0.6, -2.7, 3.6), color="#7FE9F8", brightness=0.5, range=8.0, flicker=False, shadows=True)


def _vfx(h):
    for c in [c for c in h.children if c.get("vfx_kind")]:
        bpy.data.objects.remove(c, do_unlink=True)
    off = Vector(h[OFF])
    light = {k: GLOW_LIGHT[k] for k in ("color", "brightness", "range", "flicker", "shadows")}
    return [K.socket(h, "crystal_glow", Vector(GLOW_LIGHT["pos"]) - off, light=light)]


def _inside_fn(tree):
    dirs = [Vector(d).normalized() for d in ((0.31, 0.17, 0.93), (-0.62, 0.71, 0.33), (0.45, -0.83, -0.32))]

    def inside(q):
        k = 0
        for d in dirs:
            n, x = 0, q.copy()
            for _ in range(200):
                hit = tree.ray_cast(x, d)
                if hit[0] is None:
                    break
                n += 1
                x = hit[0] + d * 1e-5
            k += n % 2
        return k >= 2
    return inside


def fx_check(h=None):
    """Each socket: the nearest hero surface, whether the socket point is inside the hero (ray parity), and how many
    of its spawn box's 5^3 grid points lie inside (m015)."""
    h = h or bpy.data.objects[HERO]
    bm = bmesh.new()
    bm.from_mesh(h.data)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    inside = _inside_fn(tree)
    out = []
    for s in [c for c in h.children if c.get("vfx_kind")]:
        spec = json.loads(s["roblox"])
        loc = Vector(s.location)
        sh = (spec.get("emitters") or [{}])[0].get("shape")
        bad = 0
        if sh:
            for i in range(5):
                for j in range(5):
                    for k in range(5):
                        q = loc + Vector(((i / 4 - 0.5) * sh[0], (k / 4 - 0.5) * sh[2], (j / 4 - 0.5) * sh[1]))
                        bad += inside(q)
        out.append({"name": s.name, "kind": s["vfx_kind"], "at_build": [round(c, 2) for c in loc + Vector(h[OFF])],
                    "clear": round(tree.find_nearest(loc)[3], 2), "inside": inside(loc), "box_inside": bad,
                    "light": spec.get("light"), "roblox_xyz": [round(loc.x, 2), round(loc.z, 2), round(-loc.y, 2)]})
    bm.free()
    return out


# ---- build -----------------------------------------------------------------------------------------------------------
PARTS = ((SHELL, shell_part, False, False), (SPOT, spot_part, False, False), (STALK_L, stalk_large_part, False, False),
         (STALK_S, stalk_small_part, False, False), (CLUMP, clump_part, True, False),
         (BASE, rock_base_part, True, True))
TARGET_SIZE = ((7.1, 0.35), (5.5, 0.4), (5.5, 0.25))
SHELL_POCKETS = ("S1", "S2", "S3", "S5", "S6")


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m030_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and (m.name.startswith((PFX, "_probe", "T_Calib", "Mooncap")))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def _fused_ok(o):
    a = M.audit(o)
    return (a["shells"] == 1 and not a["nonmanifold_edges"] and not a.get("nonmanifold_verts") and
            not a["boundary_edges"] and a["normals"] == "outward"
            and not m016._self_hits(o)[0] and not m012._thin(o, POLISH_LIM)["under"])


def build(render=True, parts=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    UNION_RETRIES.clear()
    CARVE_LOG.clear()
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn, union, ground in PARTS:
            kw = {}
            if name == SHELL:
                kw["cutters"] = hero_cutters("big", droop=False, at_origin=True, labels=SHELL_POCKETS)
            objs[name], log[name] = _make(name, fn, "part", 1000, union=union, ground=ground, **kw)
    cutters = hero_cutters("big") + hero_cutters("small")
    h, log["hero"] = _make(HERO, hero_body, "hero", 4000, union=True, ground=True, cutters=cutters, gems=hero_gems)
    log["leaves"] = dict(LEAF_INFO)
    log["rocks"] = dict(ROCK_INFO)
    log["caps"] = dict(CAP_INFO)
    log["gems"] = dict(GEM_INFO)
    log["carve"] = list(CARVE_LOG)
    log["union_retries"] = list(UNION_RETRIES)
    socks = _vfx(h)
    _glow_mats()
    _cleanup_tmp()
    order = [h] + [objs[n] for n, *_ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
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
    for lab, *_rest, ok in CARVE_LOG:
        if not ok:
            problems.append(f"carve {lab} on {_rest[0]}: undone (the difference lost the mesh)")
    # gems: each on its cap's top side and no two pockets / bezels overlapping
    gi = list(GEM_INFO.items())
    for i, (la, ga) in enumerate(gi):
        if ga["n"][2] < 0.1:
            problems.append(f"gem {la}: on the cap's underside (normal z {ga['n'][2]})")
        for lb, gb in gi[i + 1:]:
            ra = (POCKET["r"] if ga["pocket"] else BEZEL["r"]) * ga["d"]
            rb = (POCKET["r"] if gb["pocket"] else BEZEL["r"]) * gb["d"]
            if (Vector(ga["p"]) - Vector(gb["p"])).length < ra + rb + 0.05:
                problems.append(f"gems {la} and {lb} overlap")
    fx = fx_check(h)
    for s in fx:
        if s["inside"] or s["box_inside"] or s["clear"] < 0.6:
            problems.append(f"{s['name']}: socket placement (inside {s['inside']}, clear {s['clear']})")
    neon = [m.name for m in h.data.materials if m and list(m.get("flintkit_spec", [0, 0, 0]))[2] >= NEON]
    if len(neon) != 3:
        problems.append(f"{HERO}: {len(neon)} Neon keys, expected 3")
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts")} for au in audits],
           "thin": thin, "self_hits": self_hits, "log": log, "problems": problems, "fx": fx, "neon": neon,
           "sockets": [(s.name, s["vfx_kind"]) for s in socks],
           "uv": {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped",
                                                                            "min_gap", "border", "density",
                                                                            "stretch_conformal_p95")}
                  for o in order}}
    out["build_secs"] = round(time.time() - t0, 1)
    if render:
        out["views"] = render_views(order)
        out["render_secs"] = round(time.time() - t0 - out["build_secs"], 1)
    return out


# ---- renders ---------------------------------------------------------------------------------------------------------
# the sheet's comparison cameras (decision 11; spec 3): the three-quarter cells are elevated front / rear views; the
# side cell is drawn from -X (azimuth 270); the top is mirrored (flip ours before comparing). Floor hidden, long lens.
SHEET_VIEWS = {"front_sheet": (0, 8), "f34_sheet": (0, 14), "rear_sheet": (180, 8), "r34_sheet": (180, 14),
               "side_sheet": (270, 8), "top_sheet": (0, 89), "top_tilt_sheet": (0, 70)}
SHEET_LENS = 3.0
PARTS_SHOT = (-20, 20)


def _long_lens(kit):
    orig = kit["render_group"]

    def rg(group, path, azimuth=-22, elevation=20):
        cam = bpy.data.objects["FB_Cam"].data
        lens = cam.lens
        ground = bpy.data.objects.get("FB_Ground")
        hid = ground.hide_render if ground else None
        if "_sheet" in path:
            cam.lens = lens * SHEET_LENS
            if ground:
                ground.hide_render = True
        try:
            return orig(group, path, azimuth, elevation)
        finally:
            cam.lens = lens
            if ground:
                ground.hide_render = hid
    return orig, rg


# the sheet's Exploded Construction (build frame from the base's centre): the cap shell high, the gem right of it, the
# two stems under it, the leaf clump left, the base at the bottom
EXPL = ((SHELL, (-0.4, 0.0, 6.2), 0.0), (SPOT, (3.7, 0.0, 7.0), 0.0), (STALK_L, (-0.3, 0.0, 2.3), 0.0),
        (STALK_S, (2.4, 0.0, 2.1), 0.0), (CLUMP, (-3.6, -1.2, 0.4), 0.0), (BASE, (0.0, 0.0, 0.0), 0.0))


def _exploded(objs):
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []
    x0 = objs[0].location.x + 40
    base = Matrix.Translation((x0, objs[0].location.y, 0))
    for name, loc, yaw in EXPL:
        if name not in by:
            continue
        c = bpy.data.objects.new(f"{PFX}expl_{name}", by[name].data)
        coll.objects.link(c)
        c.matrix_world = base @ Matrix.Translation(loc) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
        shown.append(c)
    bpy.context.view_layer.update()
    return shown


def render_views(objs):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        if shown:
            extra["exploded"] = (shown, -12, 14)
        for o in objs[1:]:
            extra["part_" + o.name.replace("Mooncap", "").lower()] = ([o], *PARTS_SHOT)
        extra["part_underside"] = ([bpy.data.objects[SHELL]] if SHELL in bpy.data.objects else [h], -20, -30)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            sheet = M.views(NUM, [h], extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        return {"sheet": sheet}
    finally:
        for o in shown:
            bpy.data.objects.remove(o, do_unlink=True)
        M.display(NUM, objs, TITLE)


def preview(names=("front_sheet", "f34_sheet", "side_sheet", "rear_sheet", "r34_sheet", "top_sheet",
                   "top_tilt_sheet"), vfx=True, tag=""):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = _long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k + tag: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig
        M.display(NUM, [h] + [bpy.data.objects[n] for n, *_ in PARTS if n in bpy.data.objects], TITLE)


# ---- measuring (the study's m.py masks, numpy) -------------------------------------------------------------------------
REF_VIEWS = {"f34": (16, 114, 510, 450), "r34": (516, 114, 1010, 450), "front": (16, 486, 266, 710),
             "side": (271, 486, 510, 710), "rear": (515, 486, 760, 710), "top": (765, 486, 1010, 710)}
OUR_VIEWS = {"f34": "f34_sheet", "front": "front_sheet", "rear": "rear_sheet", "side": "side_sheet",
             "r34": "r34_sheet", "top": "top_sheet", "top_tilt": "top_tilt_sheet"}
CLS = ("P", "C", "T", "G", "R")


def _hsv(px):
    a = px / 255.0
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-9), 0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    dd = np.maximum(d, 1e-9)
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60
    return np.where(d == 0, 0, h), s, mx


def _classes(px, paper):
    """The study's cls(): P cap, C spot, T stem, G leaf, R rock; the rest (shadow, fringe) O; background within 18."""
    h, s, v = _hsv(px)
    bg = np.abs(px - np.array(paper, float)).max(-1) <= 18
    P = ~bg & (h >= 225) & (h <= 300) & (s >= 0.20)
    C = ~bg & (h >= 165) & (h < 225) & (s >= 0.20) & (v >= 0.45)
    G = ~bg & (h >= 55) & (h < 130) & (s >= 0.35)
    T = ~bg & (h >= 27) & (h < 55) & (s >= 0.12) & (s < 0.50) & (v >= 0.45) & ~G
    R = ~bg & ~P & ~C & ~G & ~T & (v < 0.72)
    return {"P": P, "C": C, "T": T, "G": G, "R": R}, h, s, v


def _load(path, box=None):
    px = K.NS["KIT"]["load_px"](path)[::-1, :, :3] * 255.0
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1]
    return np.clip(px, 0, 255)


def _hex(q):
    return "#" + "".join(f"{int(round(x)):02X}" for x in q)


def stats(px, paper):
    m, hue, sat, val = _classes(px, paper)
    sil = m["P"] | m["C"] | m["T"] | m["G"] | m["R"]
    rows = np.nonzero(sil.sum(1) >= 3)[0]
    cols = np.nonzero(sil.sum(0) >= 3)[0]
    y0, y1, x0, x1 = rows[0], rows[-1], cols[0], cols[-1]
    W, H = x1 - x0 + 1, y1 - y0 + 1
    tot = max(1, sil.sum())
    out = {"wh": round(W / H, 3), "px": [int(W), int(H)]}
    for k in CLS:
        out[k] = round(100 * m[k].sum() / tot, 1)
    out["C/(P+C)"] = round(100 * m["C"].sum() / max(1, m["C"].sum() + m["P"].sum()), 1)
    cv = val[m["C"]]
    if len(cv):
        out["C_bright"] = round(float((cv >= 0.85).mean()), 3)
        ch, cs = hue[m["C"]], sat[m["C"]]
        deep = (ch >= 192) | (cv < 0.88)
        light = ~deep & (cs < 0.38)
        out["C_deep_mid_light"] = [round(float(deep.mean()), 2), round(float((~deep & ~light).mean()), 2),
                                   round(float(light.mean()), 2)]
    top = []
    for i in range(21):
        c = x0 + min(W - 1, int(round(i * 0.05 * (W - 1))))
        col = sil[y0:y1 + 1, max(x0, c - 1):c + 2].any(1)
        idx = np.nonzero(col)[0]
        top.append(round(1 - idx[0] / (H - 1), 2) if len(idx) else 0.0)
    out["top"] = top
    wid = []
    for i in range(11):
        r = y1 - min(H - 1, int(round(i * 0.1 * (H - 1))))
        row = sil[max(y0, r - 1):min(y1, r + 1) + 1, x0:x1 + 1].any(0)
        idx = np.nonzero(row)[0]
        wid.append(round((idx[-1] - idx[0] + 1) / W, 2) if len(idx) else 0.0)
    out["width"] = wid
    for k in CLS:
        sel = px[m[k]]
        if len(sel) >= 8:
            lum = sel @ np.array([.299, .587, .114])
            o = np.argsort(lum)
            n = len(o)
            out[k + "med"] = _hex(np.median(sel, 0))
            out[k + "lit"] = _hex(np.median(sel[o[int(.75 * n):]], 0))
            out[k + "shade"] = _hex(np.median(sel[o[:int(.25 * n)]], 0))
    # bands per 0.1 h of P / C / T / G / R
    bands = []
    for i in range(10):
        ra = y1 - int(round((i + 1) * 0.1 * (H - 1)))
        rb = y1 - int(round(i * 0.1 * (H - 1)))
        sub = {k: int(m[k][ra:rb + 1, x0:x1 + 1].sum()) for k in CLS}
        t = max(1, sum(sub.values()))
        bands.append("/".join(f"{k}{round(100 * sub[k] / t)}" for k in CLS if sub[k] / t >= 0.02))
    out["bands"] = bands
    return out


def measure(views=("front", "f34", "side", "rear", "r34", "top", "top_tilt"), tag=""):
    """Sheet against our renders, per view (the study's masks on both; our top flipped left-right). Returns
    {view: {sheet, ours, top_err (mean, max), width_err_max, share_err}}."""
    ref = _load(M.ref(NUM))
    out = {}
    for vname in views:
        x0, y0, x1, y1 = REF_VIEWS["top" if vname == "top_tilt" else vname]
        rp = ref[y0:y1, x0:x1]
        paper = np.median(np.concatenate([rp[:4].reshape(-1, 3), rp[-4:].reshape(-1, 3)]), axis=0)
        a = stats(rp, paper)
        ours = _load(f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[vname]}{tag}.png")
        if vname.startswith("top"):
            ours = ours[:, ::-1]
        corner = np.median(np.concatenate([ours[:4].reshape(-1, 3), ours[-4:].reshape(-1, 3)]), axis=0)
        b = stats(ours, corner)
        err = [abs(x - y) for x, y in zip(a["top"], b["top"])]
        werr = [abs(x - y) for x, y in zip(a["width"], b["width"])]
        out[vname] = {"sheet": a, "ours": b, "top_err": (round(sum(err) / len(err), 3), round(max(err), 2)),
                      "width_err_max": round(max(werr), 2),
                      "share_err": {k: round(b[k] - a[k], 1) for k in CLS}}
    return out
