"""041 Shore Shelf (references/041.png): a modular water tile with an islet. A flat octagonal cyan water plate (32 x 28,
7 x 7 chamfered corners) holds a pale sand shelf (a lobed oval slab, crest 1.6) on which stands one big faceted sea
stack (three tall columns, a spire and two low shoulder blocks) crowned by a flat lime grass cap with ferns, lime leaves,
daisies and buds. Six chunky flat-crowned side rocks stand round the shelf in the water, each in a soft lobed foam
collar; a foam ribbon with bubble holes runs along the shelf's waterline; small rocks and pebbles dot the sand.

    import importlib, kit_models, m041; importlib.reload(kit_models); importlib.reload(m041); m041.build()

Build frame (studs): front -Y, +X right, ground z 0 (one flat underside). The tile contract (M041_spec.md 2.1 and the
main session's decisions, 2026-10-29), recorded for the export notes:
- plate: a regular octagon, X -16 .. 16, Y -14 .. 14, corners chamfered 7 x 7; seams (flat vertical faces) on the
  straight runs X -9 .. +9 (front / back) and Y -7 .. +7 (ends);
- bed 0 -> 0.2 over the whole plate (m041_bed, solid); water 0.25 -> 1.0 (m041_water, see-through 0.3); foam
  1.03 -> 1.07 (m041_water_foam, see-through 0.2); sand shelf crest 1.6, bevelled to 1.15 at its edge; main-rock
  summit 10.12 under the cap, turf top 10.4 (M032's grass top); plant tips about 13.2;
- nothing land within 0.5 of the plate outline; water and foam never touch the land (holes off every rock and the
  shelf); no flow direction (a still shore); 13 water_foam sockets on open water.

The land is one closed shell: a terrace (the bed and the shelf as one multi-level slab, built without booleans) with the
main rock's pieces, the side rocks, the sand rocks and the in-water pebbles united one shell at a time (merge-0 exact
unions at the world origin). The cap, every leaf, petal, bud, stem and sand pebble, the water and the foam are their own
closed shells in the same object (decision 5). Colour (stage 4) is painted by position inside the builders.

Parts (the sheet's Exploded Construction, decision 6), each from its own function: ShoreShelfGrassCap, ShoreShelfMainRock,
ShoreShelfRockLarge (FL), ShoreShelfRockMedium (BR), ShoreShelfRockSmall (FS), ShoreShelfSand (the shelf slab with its
small rocks and pebbles), ShoreShelfWaterPlane (the hero's water shell). See M041_spec.md.
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
import m011
import m012
import m016
import m033
import m034

NUM, TITLE, SHEET = 41, "Shore Shelf", "M041"
OFF = "m041_offset"
PFX = "_m041_"
HERO = "ShoreShelf"
CAP_P, ROCK_P = "ShoreShelfGrassCap", "ShoreShelfMainRock"
RL_P, RM_P, RS_P = "ShoreShelfRockLarge", "ShoreShelfRockMedium", "ShoreShelfRockSmall"
SAND_P, WATER_P = "ShoreShelfSand", "ShoreShelfWaterPlane"

ROCK, ROCK_LIGHT, ROCK_DEEP = "m041_rock", "m041_rock_light", "m041_rock_deep"
SAND, SAND_LIGHT, SAND_DEEP = "m041_sand", "m041_sand_light", "m041_sand_deep"
GRASS, GRASS_LIGHT, SOIL = "m041_grass", "m041_grass_light", "m041_soil"
LEAF, LEAF_LIT, LEAF_LIME = "m041_leaf", "m041_leaf_lit", "m041_leaf_lime"
PETAL, FLOWER, BUD, BUD_PINK = "m041_petal", "m041_flower", "m041_bud", "m041_bud_pink"
PEBBLE = "m041_pebble"
BED, BED_LIGHT = "m041_bed", "m041_bed_light"
WATER, FOAM = "m041_water", "m041_water_foam"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0
CLEAN_MOVE = 0.05          # the sliver pass's largest vertex move (m011 uses 0.18): below the water / foam gaps

# key -> (hex, roughness, low_spec); the comment is the calibration target (spec 5.4: unshadowed rendered regions)
# stage 4: K.calibrate on the kit test dome (m041.calibrate, 2026-10-29); the rock keys are set by hand from the
# calibration's measured studio gain (R 1.68, G 1.56, B 1.40 in linear light) because the calibrated keys came out
# mauve (B > G): every rock key stays R > G > B with R - B >= 14 and renders hue 15-22 deg
PALETTE = {ROCK: ("#A09492", 0.85, False),          # lit faces #C6B4AE (f34 v > .7); renders about #C9B5AA
           ROCK_LIGHT: ("#A99F9D", 0.85, False),    # about +12 levels (lit quartile #D7CAC8); renders about #D6C2B7
           ROCK_DEEP: ("#8F8583", 0.9, False),      # a step below rock; renders about #B5A298
           SAND: ("#EEBA95", 0.95, False),          # #FDE6AD (exploded top #FDE4AB, close-up A #FDE7AE) -> #FFE5AE
           SAND_LIGHT: ("#F4C19D", 0.95, False),    # #FEEFB7 hero open sand -> #FFEEB7
           SAND_DEEP: ("#BEA881", 0.95, False),     # #F2CE95 shade quartiles; the bevel band, the walls -> #F1CE95
           GRASS: ("#93B600", 0.85, True),          # #B7DF02 turf (cap, v > .7) -> #B6DE05
           GRASS_LIGHT: ("#A0C100", 0.85, True),    # #C7ED05 lit turf patches -> #C7EC05
           SOIL: ("#725325", 0.95, False),          # #8F6531 exploded cap sides -> #8E6532
           LEAF: ("#0D5510", 0.85, True),           # #126513 dark ferns -> #116011
           LEAF_LIT: ("#1E8753", 0.85, True),       # #21A157 lit fern tips, teal round leaves -> #22A059
           LEAF_LIME: ("#82A500", 0.85, True),      # #A0C908 lime leaves -> #9FC805
           PETAL: ("#DACAC8", 0.8, False),          # #FBF8EE -> #FFFFF1
           FLOWER: ("#C1A700", 0.8, False),         # #F5CD12 -> #F5CD25
           BUD: ("#A3403D", 0.7, False),            # #CF514B -> #CD524B
           BUD_PINK: ("#A86A90", 0.7, False),       # #BC7CA3 (too pale for the vivid sampler: set by hand)
           PEBBLE: ("#6F4F28", 0.9, False),         # #8B6136 -> #8B6136
           BED: ("#00A0EA", 0.9, False),            # deep water renders #01D7FD
           BED_LIGHT: ("#2CC8EE", 0.9, False),      # light water renders #40E8FD
           WATER: ("#00B4E2", 0.15, False),         # rendered water median #06DFFD
           FOAM: ("#CDE6EE", 0.6, False)}           # rendered foam median #C3F3FC, lit #E8FCFE
TRANSPARENCY = {WATER: 0.3, FOAM: 0.2}
WATER_SPEC = 0.0

TARGETS = {ROCK: ((0xC6, 0xB4, 0xAE), "stone"), ROCK_LIGHT: ((0xD2, 0xC2, 0xBD), "stone"),
           ROCK_DEEP: ((0xB0, 0x9E, 0x98), "stone"),
           SAND: ((0xFD, 0xE6, 0xAD), "all"), SAND_LIGHT: ((0xFE, 0xEF, 0xB7), "all"),
           SAND_DEEP: ((0xF2, 0xCE, 0x95), "all"),
           GRASS: ((0xB7, 0xDF, 0x02), "green"), GRASS_LIGHT: ((0xC7, 0xED, 0x05), "green"),
           SOIL: ((0x8F, 0x65, 0x31), "brown"), LEAF: ((0x12, 0x65, 0x13), "green"),
           LEAF_LIT: ((0x21, 0xA1, 0x57), "green"), LEAF_LIME: ((0xA0, 0xC9, 0x08), "green"),
           PETAL: ((0xFB, 0xF8, 0xEE), "all"), FLOWER: ((0xF5, 0xCD, 0x12), "vivid"),
           BUD: ((0xCF, 0x51, 0x4B), "vivid"), BUD_PINK: ((0xBC, 0x7C, 0xA3), "vivid"),
           PEBBLE: ((0x8B, 0x61, 0x36), "brown")}


def palette():
    f = K.fk()
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        mat = f.material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        if k in TRANSPARENCY:
            f.set_water_transparency(mat, TRANSPARENCY[k])
            _refresh_water_texture(mat, k, hexcol)
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf and "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = WATER_SPEC
    _bed_finish()


def _bed_finish():
    """Preview only (M034): the bed (and its in-between keys) without a specular sheen; seen through the
    0.3-transparent water, the bed's sky glint otherwise lifts every water pixel's red."""
    for mat in bpy.data.materials:
        if mat.name.startswith("FB_" + BED) and mat.node_tree:
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf and "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = 0.0


def _refresh_water_texture(mat, key, hexcol):
    """Repaint the kit's water preview texture when the key's colour changed since the material was made (m034)."""
    f = K.fk()
    nt = mat.node_tree
    tex = nt.nodes.get("FB_WaterTex") if nt else None
    if tex is None or mat.get("m041_tex_hex") == hexcol:
        mat["m041_tex_hex"] = hexcol
        return
    mapping = tex.inputs["Vector"].links[0].from_node if tex.inputs["Vector"].links else None
    coord = mapping.inputs["Vector"].links[0].from_node if mapping and mapping.inputs["Vector"].links else None
    img = tex.image
    for n in (tex, mapping, coord):
        if n is not None:
            nt.nodes.remove(n)
    f._water_texture(mat, key, hexcol)
    if img is not None:
        img.reload()
    mat["m041_tex_hex"] = hexcol


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome; "all" keys are sampled with the
    floor dropped (M.sample). Returns {key: (hex, rendered)} and leaves the keys set. (m034)"""
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


# ---- small helpers -------------------------------------------------------------------------------------------------
_q = m034._q
_mix = m034._mix
_v2 = m034._v2
cdt_region = m034.cdt_region
_offset_poly = m034._offset_poly
_inside = m034._inside
_dist_line = m034._dist_line
_seg_d = m034._seg_d
_hull2 = m034._hull2
_simplify_convex = m034._simplify_convex
_steiner = m034._steiner
_resample_poly = m034._resample_poly
_ray_poly = m034._ray_poly


def _faces(verts):
    return K.faces_of([v for v in verts if v.is_valid])


def _tri(bm, faces):
    bmesh.ops.triangulate(bm, faces=[f for f in faces if f.is_valid and len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")


def _mottle(a, faces, amp, scale, seed, tint=1.0):
    """Broad Tint patches about 1/scale studs across (never per-face confetti); tint is a uniform per-piece factor."""
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in faces:
        k = (1.0 + amp * 1.6 * noise.noise(f.calc_center_median() * scale + off)) * tint
        for l in f.loops:
            t = l[a.tint_layer][0] * k
            l[a.tint_layer] = (t, t, t, 1.0)


def _ccw(poly):
    P = [_v2(p) for p in poly]
    ar = sum(P[i].x * P[(i + 1) % len(P)].y - P[(i + 1) % len(P)].x * P[i].y for i in range(len(P)))
    return P if ar > 0 else list(reversed(P))


def _centroid(poly):
    P = [_v2(p) for p in poly]
    return sum(P, Vector((0.0, 0.0))) / len(P)


def _catmull(pts, step, closed=True):
    """A closed Catmull-Rom curve through pts, sampled about every `step`."""
    P = [_v2(p) for p in pts]
    n = len(P)
    out = []
    for i in range(n if closed else n - 1):
        p0, p1, p2, p3 = P[i - 1], P[i], P[(i + 1) % n], P[(i + 2) % n]
        k = max(1, int(math.ceil((p2 - p1).length / step)))
        for j in range(k):
            t = j / k
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    return out


# ---- layout (studs, build frame; spec 2, tuned on the f34_sheet render) --------------------------------------------
PLATE = [(-9.0, -14.0), (9.0, -14.0), (16.0, -7.0), (16.0, 7.0), (9.0, 14.0), (-9.0, 14.0), (-16.0, 7.0),
         (-16.0, -7.0)]
SEAM_INSET = 0.02
BED_TOP = 0.2
WATER_TOP, WATER_BOT = 1.0, 0.25
FOAM_Z = (1.03, 1.07)
SAND_TOP, SAND_EDGE, SAND_BEVEL = 1.6, 1.15, 0.8
SUMMIT, TURF, CAP_BOT, SOIL_TOP = 10.12, 10.4, 9.9, 10.25
FOOT = 0.05               # every rock's hidden plinth reaches down to here (inside the bed / the shelf)

# the shelf's edge at the waterline (CCW; top view, checked against the hero), lobed between the points
SHELF = [(-7.5, -1.5), (-6.5, -4.5), (-4.6, -6.0), (-2.6, -7.4), (0.5, -8.1), (4.0, -8.3), (6.6, -6.6), (8.5, -4.3),
         (10.0, -1.6), (10.0, 1.8), (8.8, 4.4), (6.6, 6.8), (3.6, 8.6), (0.5, 9.4), (-2.6, 9.0), (-5.4, 7.6),
         (-6.9, 4.4), (-7.5, 1.4)]
SHELF_STEP = 1.75
SHELF_LOBE = (0.32, 2.6)   # radial lobing amplitude, lobe length (studs of arclength)
SHELF_POLY = []


def shelf_poly():
    """The shelf's edge polygon (CCW), a lobed Catmull-Rom curve through SHELF."""
    if not SHELF_POLY:
        P = _catmull(SHELF, SHELF_STEP)
        c = _centroid(P)
        out, s = [], 0.0
        for i, p in enumerate(P):
            if i:
                s += (p - P[i - 1]).length
            d = (p - c).normalized()
            out.append(p + d * SHELF_LOBE[0] * math.sin(2 * math.pi * s / SHELF_LOBE[1] + 0.7))
        SHELF_POLY[:] = _ccw(out)
    return SHELF_POLY


def sand_z(p):
    """The shelf top: the 1.6 crest, a bevel band SAND_BEVEL wide down to 1.15 at the edge."""
    P = shelf_poly()
    if not _inside(p, P):
        return SAND_EDGE
    d = _dist_line(p, P, True)
    t = min(1.0, d / SAND_BEVEL)
    return SAND_EDGE + (SAND_TOP - SAND_EDGE) * t


# ---- terrace: the bed and the shelf as one closed multi-level slab (no booleans) ----------------------------------
TOP_STEP = {"shelf": 3.0, "bed": 6.0}
BOTTOM_STEP = 9.0


def _key(p):
    return (round(p[0], 4), round(p[1], 4))


def terrace(a, with_bed=True, seed=41100):
    """Bed (octagon minus shelf, top 0.2) and shelf (top sand_z), vertical walls where they meet and round the plate,
    one flat bottom at z 0. without bed: the shelf alone (the Sand part), its walls down to 0.
    Returns {"bed": faces, "shelf": faces, "wall": faces, "outer": faces, "bottom": faces, "verts": verts}."""
    bm = a.bm
    vmap = {}

    def V(k, z):
        kk = (k[0], k[1], round(z, 4))
        v = vmap.get(kk)
        if v is None:
            v = vmap[kk] = bm.verts.new((k[0], k[1], z))
        return v
    E = shelf_poly()
    inset = _resample_poly(_offset_poly(E, -SAND_BEVEL), 1.6)
    st = _steiner([E], [], TOP_STEP["shelf"], 1.35, seed) + [p for p in inset if _dist_line(p, E, True) > 0.6]
    co, tris = cdt_region([E], [], st, tidy=False)
    ks = [_key(c) for c in co]
    shelf_f = [bm.faces.new((V(ks[i], sand_z(co[i])), V(ks[j], sand_z(co[j])), V(ks[k], sand_z(co[k]))))
               for i, j, k in tris]
    ekeys = [_key(p) for p in E]
    out = {"shelf": shelf_f, "bed": [], "wall": [], "outer": [], "bottom": []}
    n = len(E)
    if with_bed:
        plate = _resample_poly(PLATE, 7.5)
        st = _steiner([plate], [E], TOP_STEP["bed"], 1.6, seed + 1)
        co, tris = cdt_region([plate], [E], st, tidy=False)
        ks = [_key(c) for c in co]
        out["bed"] = [bm.faces.new((V(ks[i], BED_TOP), V(ks[j], BED_TOP), V(ks[k], BED_TOP))) for i, j, k in tris]
        lo = BED_TOP
        outline = [_key(p) for p in plate]
    else:
        lo = 0.0
        outline = ekeys
    # the shelf wall (edge 1.15 down to the bed top, or to 0 for the part)
    for i in range(n):
        p, q = ekeys[i], ekeys[(i + 1) % n]
        f1 = bm.faces.new((V(p, lo), V(q, lo), V(q, SAND_EDGE)))
        f2 = bm.faces.new((V(p, lo), V(q, SAND_EDGE), V(p, SAND_EDGE)))
        out["wall"] += [f1, f2]
    if with_bed:
        m = len(outline)
        for i in range(m):
            p, q = outline[i], outline[(i + 1) % m]
            out["outer"] += [bm.faces.new((V(p, 0.0), V(q, 0.0), V(q, BED_TOP))),
                             bm.faces.new((V(p, 0.0), V(q, BED_TOP), V(p, BED_TOP)))]
    poly = [Vector(k) for k in outline]
    st = _steiner([poly], [], BOTTOM_STEP, BOTTOM_STEP * 0.4, seed + 50)
    co, tris = cdt_region([poly], [], st, tidy=False)
    ks = [_key(c) for c in co]
    out["bottom"] = [bm.faces.new((V(ks[i], 0.0), V(ks[k], 0.0), V(ks[j], 0.0))) for i, j, k in tris]
    allv = list(vmap.values())
    bmesh.ops.recalc_face_normals(bm, faces=_faces(allv))
    a._finish(allv, SAND, tint=1.0)
    out["verts"] = allv
    _paint_terrace(a, out, seed + 7)
    return out


BED_PATCH = dict(scale=0.16, level=0.2, width=0.3)


def _paint_terrace(a, T, seed):
    """Sand: base with broad light patches on the crest, a deeper band on the bevel; the walls deep sand; the bed deep
    blue with broad light patches, light within 1.2 of the shelf and every rock in the water (no dark ring under the
    foam); the bottom sand under the shelf, bed blue elsewhere (close-up B). By position only."""
    nf_s = K.noise_field(scale=0.22, seed=seed)
    nf_b = K.noise_field(scale=BED_PATCH["scale"], seed=seed + 1)
    E = shelf_poly()
    tval = {}
    for f in T["shelf"]:
        c = f.calc_center_median()
        light = min(1.0, max(0.0, (nf_s(c) - 0.02) / 0.25))
        deep = 1.0 if c.z < SAND_EDGE + 0.18 else 0.5 if c.z < SAND_TOP - 0.1 else 0.0
        tval[f] = (light, deep)
    for f in T["bed"]:
        c = f.calc_center_median()
        t = min(1.0, max(0.0, (nf_b(c) - BED_PATCH["level"]) / BED_PATCH["width"]))
        near = min([_dist_line(c, E, True)] + [max(0.0, (_v2(c) - Vector(r[0])).length - 0.5 * max(r[1], r[2]))
                                                for r in IN_WATER_ROCKS()])
        if near < 0.6:
            t = max(t, 0.75)
        tval[f] = (t, 0.0)
    for _ in range(2):          # averaged with neighbours before quantising (no lone triangle shards; M034)
        nxt = {}
        for f, (t, d) in tval.items():
            nb = [tval[g][0] for e in f.edges for g in e.link_faces if g is not f and g in tval]
            nxt[f] = (0.5 * t + 0.5 * (sum(nb) / len(nb)) if nb else t, d)
        tval = nxt
    for f in T["shelf"]:
        light, deep = tval[f]
        if deep >= 1.0:
            key = _mix(SAND, SAND_DEEP, 0.5)
        elif deep > 0:
            key = _mix(SAND, SAND_DEEP, 0.25)
        else:
            key = _mix(SAND, SAND_LIGHT, light * 0.75)
        f.material_index = a._mi(key)
    for f in T["bed"]:
        f.material_index = a._mi(_mix(BED, BED_LIGHT, tval[f][0]))
    for f in T["wall"]:
        f.material_index = a._mi(SAND_DEEP)
    for f in T["outer"]:
        f.material_index = a._mi(BED)
    for f in T["bottom"]:
        c = f.calc_center_median()
        f.material_index = a._mi(SAND_DEEP if _inside(c, E) else BED)
    _mottle(a, T["shelf"], 0.03, 0.15, seed + 2)
    _mottle(a, T["bed"], 0.03, 0.8, seed + 3)


# ---- rocks ---------------------------------------------------------------------------------------------------------
# side rocks: name -> (centre (x, y), footprint w x d, base z, top z, yaw deg, rings, seed); ground "water" rocks
# stand on the bed (base FOOT), "sand" rocks are sunk 0.3 into the shelf (base 1.3)
LARGE_R = [(0.0, 0.95, 7), (0.3, 1.0, 7), (0.55, 0.99, 7), (0.8, 0.92, 6), (1.0, 0.74, 5)]
MED_R = [(0.0, 0.95, 7), (0.33, 1.0, 7), (0.7, 0.95, 6), (1.0, 0.84, 6)]     # + a crown knob (KNOB)
MID_R = [(0.0, 0.95, 7), (0.32, 1.0, 7), (0.72, 0.93, 6), (1.0, 0.72, 5)]
SMALL_R = [(0.0, 0.95, 6), (0.35, 1.0, 6), (0.75, 0.88, 5), (1.0, 0.58, 4)]
PEB_R = [(0.0, 1.0, 4), (0.45, 0.95, 4), (1.0, 0.55, 3)]
WPEB_R = [(0.0, 0.9, 4), (0.62, 1.0, 4), (1.0, 0.6, 3)]
ROCKS = {
    "FL": ((-5.5, -4.9), 6.5, 5.0, FOOT, 5.3, 20.0, LARGE_R, 41201),
    "BR": ((9.4, 8.4), 5.0, 4.5, FOOT, 5.5, -15.0, MED_R, 41202),
    "L": ((-8.9, 1.9), 4.0, 3.5, FOOT, 3.6, 70.0, MID_R, 41213),
    "FR": ((12.0, -5.8), 4.2, 3.8, FOOT, 4.1, -30.0, MID_R, 41204),
    "FLb": ((-5.3, -8.7), 4.0, 2.5, FOOT, 2.9, 5.0, SMALL_R, 41205),
    "FRb": ((13.1, -8.1), 1.8, 1.4, FOOT, 2.3, 40.0, SMALL_R, 41206),
    "FS": ((8.4, -7.3), 2.6, 2.4, FOOT, 2.8, 15.0, SMALL_R, 41207),
    "BL": ((-6.5, 9.4), 2.2, 2.2, FOOT, 2.2, 60.0, SMALL_R, 41208),
    "S1": ((3.8, -5.9), 1.9, 1.6, 1.3, 2.9, 25.0, SMALL_R, 41209),
    "S2": ((8.5, 1.1), 1.0, 1.0, 1.3, 2.1, 70.0, SMALL_R, 41210),
}
KNOB = {"BR": ((0.18, 0.12), 0.5, 0.9)}    # crown knob: offset (fraction of w / 2, d / 2), size fraction, body top
WATER_PEBBLES = [((-9.6, -1.6), 0.8, False, 41301), ((-0.9, -10.6), 0.75, True, 41302),
                 ((11.6, 4.9), 0.9, False, 41303), ((10.8, -10.2), 0.7, True, 41304)]
WPEB_TOP = (1.32, 1.28, 1.36, 1.25)
SAND_PEBBLES = [((1.7, -5.6), 0.55, True, 41311), ((2.2, -6.9), 0.45, False, 41312), ((7.2, -3.5), 0.5, False, 41313)]


def IN_WATER_ROCKS():
    return [r for n, r in ROCKS.items() if r[3] < 1.0] + [(p, s, s) for p, s, _b, _s in WATER_PEBBLES]


def _hull(a, pts, mat):
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    for v in vs:
        if v.is_valid and not v.link_faces:
            bm.verts.remove(v)
    vs = [v for v in vs if v.is_valid]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, mat, tint=1.0)
    return vs


def _tidy_hull(a, vs, angle=4.0):
    """Merge near-coplanar facets of a hull and re-triangulate (big flat facets, not a ring of small ones)."""
    bmesh.ops.dissolve_limit(a.bm, angle_limit=math.radians(angle), verts=vs,
                             edges=list({e for f in _faces(vs) for e in f.edges}))
    vs = [v for v in vs if v.is_valid]
    _tri(a.bm, _faces(vs))
    bmesh.ops.recalc_face_normals(a.bm, faces=_faces(vs))
    return vs


def ring_pts(c, w, d, z0, z1, yaw, rings, seed, jitter=0.07):
    """Jittered rings (height frac, radius frac, count) round c, footprint w x d, base z0 -> top z1, yawed."""
    rng = random.Random(seed)
    rx, ry, h = w / 2, d / 2, z1 - z0
    m = Matrix.Rotation(math.radians(yaw), 2)
    pts = []
    for hf, rf, n in rings:
        if n == 0:
            continue
        off = rng.uniform(0, 2 * math.pi)
        for k in range(n):
            th = off + 2 * math.pi * k / n + rng.uniform(-0.22, 0.22) * (2 * math.pi / n)
            r = rf * (1 + rng.uniform(-jitter, jitter))
            z = z0 + hf * h * (1 + (rng.uniform(-jitter, jitter) * 0.6 if 0 < hf < 1 else 0))
            q = m @ Vector((math.cos(th) * rx * r, math.sin(th) * ry * r))
            pts.append(Vector((c[0] + q.x, c[1] + q.y, z)))
    return pts


def rock(a, name, at_origin=False, base=None):
    """One chunky side rock: the convex hull of jittered rings (a broad base, near-vertical lower sides, a flat
    polygonal crown), facets merged where near-coplanar. BR gets a small stepped knob on its crown (a second hull).
    Returns verts (both hulls)."""
    (cx, cy), w, d, z0, z1, yaw, rings, seed = ROCKS[name]
    if base is not None:
        z1, z0 = z1 - z0 + base, base
    if at_origin:
        cx, cy, z1, z0 = 0.0, 0.0, z1 - z0, 0.0
    zb = z0 + (z1 - z0) * KNOB[name][2] if name in KNOB else z1
    vs = _tidy_hull(a, _hull(a, ring_pts((cx, cy), w, d, z0, zb, yaw, rings, seed), ROCK))
    out = list(vs)
    if name in KNOB:
        (ox, oy), rf, _kf = KNOB[name]
        m = Matrix.Rotation(math.radians(yaw), 2)
        q = m @ Vector((ox * w / 2, oy * d / 2))
        zc = zb
        kp = ring_pts((cx + q.x, cy + q.y), w * rf, d * rf, zc - 0.25, z1, yaw + 30, [(0.0, 1.0, 5), (0.45, 1.0, 5),
                                                                                       (1.0, 0.62, 4)], seed + 5)
        out += _tidy_hull(a, _hull(a, kp, ROCK))
    _paint_rock(a, out, seed, z0, z1)
    return out


def pebble(a, p, s, brown, seed, z0, top=None):
    """A small faceted stone: on the sand (sunk 0.05) a low chunk; in the water (top given) it stands on the bed and
    shows 0.25-0.4 above the water (spec 2.3)."""
    rng = random.Random(seed)
    z1 = top if top is not None else z0 + 0.2 + s * 0.5
    pts = ring_pts(p, s, s * rng.uniform(0.75, 0.9), z0, z1, rng.uniform(0, 360), PEB_R if top is None else WPEB_R,
                   seed, 0.1)
    vs = _hull(a, pts, PEBBLE if brown else ROCK)
    _tri(a.bm, _faces(vs))
    _mottle(a, _faces(vs), 0.03, 0.8, seed, tint=rng.uniform(0.94, 1.06))
    if not brown:
        for f in _faces(vs):
            f.material_index = a._mi(_mix(ROCK, ROCK_DEEP, 0.25) if f.calc_center_median().z < WATER_TOP else ROCK)
    return vs


def _paint_rock(a, vs, seed, z0, z1):
    """Side rock colour by height only: the crown (top 25 % of its height) a step lighter, the foot (within 1.0 above
    the water / sand) a step deeper, faces under the water mixed toward the deep tone; a per-rock Tint."""
    tint = random.Random(seed).uniform(0.96, 1.04)
    ground = WATER_TOP if z0 < 1.0 else SAND_TOP
    for f in _faces(vs):
        z = f.calc_center_median().z
        t = (z - z0) / max(1e-6, z1 - z0)
        if z < WATER_TOP - 0.05 and z0 < 1.0:
            key = _mix(ROCK, ROCK_DEEP, 0.75)
        elif z < ground + 0.6:
            key = _mix(ROCK, ROCK_DEEP, 0.5)
        elif z < ground + 1.2:
            key = _mix(ROCK, ROCK_DEEP, 0.25)
        elif t > 0.8:
            key = _mix(ROCK, ROCK_LIGHT, 0.5)
        elif t > 0.6:
            key = _mix(ROCK, ROCK_LIGHT, 0.25)
        else:
            key = ROCK
        f.material_index = a._mi(key)
    _mottle(a, _faces(vs), 0.04, 0.4, seed, tint=tint)


# ---- the main rock (spec 2.4): explicit prisms, united into the land --------------------------------------------
# the cap's outline (CCW, spec 2.5, with a notch at the front and one at the back); the summit block's top ring is
# this outline offset CAP_LIP outward at SUMMIT, so the turf slab covers the whole flat summit
CAP = [(-2.5, 0.5), (0.5, 0.3), (1.2, 0.85), (2.0, 0.45), (3.5, 0.4), (5.6, 1.2), (5.5, 2.8), (5.15, 3.2),
       (5.4, 4.0), (5.0, 6.4), (3.4, 6.75), (2.9, 6.35), (2.0, 6.7), (-0.3, 6.2), (-2.4, 4.6), (-2.0, 2.6)]
CAP_LIP = 0.03
COL_SEED = 41400
SUMMIT_STEP = 1.55
CREASES_X = (1.3, 3.3)
CREASES_BACK_X = (-0.1, 2.7)


def _summit_rings(foot_z):
    """The summit block (C2 front and C4 back as one mass): rings from the foot up: the foot (a battered footprint),
    a waist, the shoulder, a lip just under the top and the top (the cap outline + CAP_LIP at SUMMIT). Every ring has
    the same count, so the loft follows the cap's notches."""
    top = _resample_poly(_ccw(CAP), SUMMIT_STEP)
    c = Vector((1.6, 3.6))
    rng = random.Random(COL_SEED)
    rings = []

    def batter(n):
        # spec 2.4: the front leans back strongly (3.3 over the height), the left 1.5, the right 1.2; the back 1.8
        # (the side cell draws the stack's back as sloped as its front)
        return Vector((1.2 * n.x if n.x > 0 else 1.5 * n.x, 1.8 * n.y if n.y > 0 else 3.3 * n.y))

    def crease(p, n):
        # vertical creases between the columns: two on C2's front (hero x 290 / 320: X 1.3, 3.3) and two on the
        # back (the r34's back columns), each pulled 0.5 into the mass
        if n.y < -0.35:
            k = max(max(0.0, 1.0 - abs(p.x - cx) / 0.75) for cx in CREASES_X)
            return Vector((0.0, 0.5 * k))
        if n.y > 0.35:
            k = max(max(0.0, 1.0 - abs(p.x - cx) / 0.75) for cx in CREASES_BACK_X)
            return Vector((0.0, -0.5 * k))
        return Vector((0.0, 0.0))

    def ring(z, frac, jit):
        out = []
        for p in top:
            n = (p - c).normalized()
            q = p + batter(n) * frac + crease(p, n) * min(1.0, frac * 2.5) + Vector(
                (rng.uniform(-jit, jit), rng.uniform(-jit, jit)))
            out.append(Vector((q.x, q.y, z)))
        return out
    lip = _offset_poly(top, CAP_LIP)
    rings.append(ring(foot_z, 1.0, 0.1))
    rings.append(ring(4.8, 0.62, 0.16))
    rings.append(ring(8.5, 0.24, 0.12))
    rings.append([Vector((p.x, p.y, SUMMIT - 0.34)) + (p - c).normalized().to_3d() * 0.22 for p in lip])
    rings.append([Vector((p.x, p.y, SUMMIT)) for p in lip])
    return rings


def loft(a, rings, mat):
    """A closed solid through rings of equal count (bottom first, each CCW from above): side quads between rings,
    a flat triangulated cap on the bottom and the top ring. Returns verts."""
    bm = a.bm
    R = [[bm.verts.new(p) for p in r] for r in rings]
    n = len(R[0])
    fs = []
    for r0, r1 in zip(R, R[1:]):
        for i in range(n):
            j = (i + 1) % n
            fs.append(bm.faces.new((r0[i], r0[j], r1[j], r1[i])))
    for r, flip in ((R[0], True), (R[-1], False)):
        co, tris = cdt_region([[v.co.to_2d() for v in r]], [], (), tidy=False)
        km = {_key(v.co): v for v in r}
        for t in tris:
            vv = [km[_key(co[i])] for i in t]
            fs.append(bm.faces.new(vv[::-1] if flip else vv))
    allv = [v for r in R for v in r]
    _tri(bm, fs)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(allv))
    a._finish(allv, mat, tint=1.0)
    return allv


# columns and blocks (convex hulls): name -> rings [(z, [(x, y), ...])] plus an optional apex (x, y, z); points are
# jittered a little (seeded) and a vertical split vertex pushed out mid-height on the long faces (tall strip facets)
COLS = {
    # C1, the left-back column: a big shaded left face, its bevelled tip 10.8 just outside the cap's left edge
    "C1": dict(foot=[(-5.6, -1.6), (-3.8, -2.4), (-1.4, -1.9), (-0.9, 3.0), (-1.4, 7.3), (-3.9, 7.7), (-5.7, 4.0)],
               shoulder=(8.1, 0.88, (0.45, 0.15)), bevel=(9.75, [(-4.0, 2.15), (-2.6, 1.85), (-2.35, 3.4), (-3.1, 4.0),
                                                                (-4.1, 3.4)]),
               apex=(-3.15, 2.8, 10.85), split=0.16),
    # C3, the right column: tip 10.6 just outside the cap's front-right corner
    "C3": dict(foot=[(3.6, -0.8), (5.6, -1.3), (7.0, 0.6), (7.1, 4.4), (6.4, 7.0), (4.0, 6.6)],
               shoulder=(8.1, 0.8, (-0.35, 0.25)), bevel=(9.7, [(5.3, -0.2), (6.6, 0.0), (6.7, 1.1), (5.6, 1.4)]),
               apex=(6.05, 0.45, 10.6), split=0.15),
    # the spire: a pointed shard leaning 8 deg into C3's front, a stepped front facet
    "SP": dict(foot=[(4.9, -3.3), (6.6, -3.6), (7.9, -2.4), (7.7, -0.7), (5.9, -0.4)],
               shoulder=(4.8, 0.6, (-0.1, 0.45)), bevel=None, apex=(6.35, -1.45, 7.3), split=0.12),
    # LB, the front-left shoulder block (stepped, low) and RB, the right shoulder block between the spire and BR
    "LB": dict(foot=[(-5.7, -4.0), (-3.4, -4.1), (-2.6, -2.2), (-3.6, -1.2), (-5.8, -1.5)],
               shoulder=(3.1, 0.86, (0.1, 0.05)), bevel=(3.5, [(-5.0, -3.3), (-3.6, -3.4), (-3.3, -2.2), (-5.1, -2.1)]),
               apex=None, split=0.1),
    "RB": dict(foot=[(5.6, 1.2), (7.9, 1.4), (8.4, 3.4), (7.8, 5.4), (5.6, 5.3)],
               shoulder=(4.0, 0.84, (-0.1, 0.0)), bevel=(4.55, [(6.0, 2.0), (7.4, 2.1), (7.5, 4.4), (6.1, 4.5)]),
               apex=None, split=0.1),
}
COL_ORDER = ("C1", "C3", "SP", "LB", "RB")


def column_pts(name, foot_z, base_z=1.3):
    """A column's points: a hidden plinth at foot_z, the visible foot at base_z, a split ring at mid height, the
    shoulder, the bevel ring and the apex."""
    spec = COLS[name]
    rng = random.Random(COL_SEED + sum(map(ord, name)))
    foot = [Vector(p) for p in spec["foot"]]
    c = _centroid(foot)
    zs, sc, shift = spec["shoulder"]
    shift = Vector(shift)
    pts = []
    if foot_z < base_z - 1e-3:
        pts += [Vector((p.x, p.y, foot_z)) for p in foot]
    pts += [Vector((p.x, p.y, base_z + rng.uniform(0.0, 0.08))) for p in foot]
    sh = [c + (p - c) * sc + shift for p in foot]
    # mid-height split vertices: halfway between foot and shoulder, pushed out (each long face becomes tall strips)
    zm = base_z + (zs - base_z) * rng.uniform(0.42, 0.58)
    t = (zm - base_z) / (zs - base_z)
    for i in range(len(foot)):
        j = (i + 1) % len(foot)
        if (foot[j] - foot[i]).length < 1.6:
            continue
        a_ = foot[i].lerp(foot[j], 0.5)
        b_ = sh[i].lerp(sh[j], 0.5)
        m = a_.lerp(b_, t)
        out = Vector((foot[j].y - foot[i].y, -(foot[j].x - foot[i].x))).normalized()
        q = m + out * spec["split"] * rng.uniform(0.7, 1.3) + (foot[j] - foot[i]) * rng.uniform(-0.12, 0.12)
        pts.append(Vector((q.x, q.y, zm)))
    pts += [Vector((p.x + rng.uniform(-0.06, 0.06), p.y + rng.uniform(-0.06, 0.06), zs + rng.uniform(-0.12, 0.12)))
            for p in sh]
    if spec["bevel"]:
        zb, ring = spec["bevel"]
        pts += [Vector((x, y, zb + rng.uniform(-0.05, 0.05))) for x, y in ring]
    if spec["apex"]:
        pts.append(Vector(spec["apex"]))
    return pts


def main_rock(a, foot_z=FOOT):
    """The stack: the summit block (a loft under the cap) and the columns / blocks round it (hulls). Returns the
    verts of each piece by name."""
    out = {}
    vs = loft(a, _summit_rings(foot_z), ROCK)
    out["SUM"] = vs
    for name in COL_ORDER:
        out[name] = _tidy_hull(a, _hull(a, column_pts(name, foot_z), ROCK), angle=3.0)
    for name, vs in out.items():
        _paint_stack(a, vs, COL_SEED + len(name) * 7 + ord(name[-1]))
    return out


def _paint_stack(a, vs, seed):
    """The stack by height and place: its upper part a step lighter (above 0.7 of the summit), the foot within 1.0 of
    the sand a step deeper, faces in the creases between the columns deeper; a per-piece Tint. Never by facing."""
    tint = random.Random(seed).uniform(0.96, 1.04)
    creases = [((-0.7, -2.2), (-1.3, 7.4)), ((4.0, -0.9), (4.4, 6.8)), ((1.3, -3.4), (1.6, 0.4)),
               ((3.3, -3.2), (3.4, 0.4))]
    for f in _faces(vs):
        c = f.calc_center_median()
        z = c.z
        crease = min(_seg_d(c.to_2d(), Vector(p), Vector(q)) for p, q in creases)
        if z < SAND_TOP - 0.05:
            key = _mix(ROCK, ROCK_DEEP, 0.5)
        elif z < SAND_TOP + 1.0:
            key = _mix(ROCK, ROCK_DEEP, 0.5)
        elif z < SAND_TOP + 2.0:
            key = _mix(ROCK, ROCK_DEEP, 0.25)
        elif z > 0.85 * SUMMIT:
            key = ROCK_LIGHT
        elif z > 0.7 * SUMMIT:
            key = _mix(ROCK, ROCK_LIGHT, 0.5)
        else:
            key = ROCK
        if crease < 0.35 and SAND_TOP + 1.0 < z < 0.85 * SUMMIT:
            key = _mix(ROCK, ROCK_DEEP, 0.5)
        f.material_index = a._mi(key)
    _mottle(a, _faces(vs), 0.04, 0.4, seed, tint=tint)


# ---- the grass cap (spec 2.5) --------------------------------------------------------------------------------------
def cap_slab(a, seed=41500):
    """A flat turf slab over the cap outline: turf top TURF, a turf rim band down to SOIL_TOP, soil sides to CAP_BOT,
    a flat underside. Returns (top faces, all verts)."""
    poly = _ccw(CAP)
    st = _steiner([poly], [], 3.4, 1.3, seed)
    co, tris = cdt_region([poly], [], st, tidy=False)
    tf, wf, bf, allv = m032_slab(a, co, tris, TURF, CAP_BOT, GRASS, bands=(TURF - SOIL_TOP,))
    nf = K.noise_field(scale=0.45, seed=seed)
    for f in tf:
        c = f.calc_center_median()
        f.material_index = a._mi(_mix(GRASS, GRASS_LIGHT, min(1.0, max(0.0, (nf(c) + 0.05) / 0.3)) * 0.75))
    for f in wf:
        f.material_index = a._mi(GRASS if f.calc_center_median().z > SOIL_TOP else SOIL)
    for f in bf:
        f.material_index = a._mi(SOIL)
    _mottle(a, tf, 0.04, 0.4, seed + 1)
    _mottle(a, wf + bf, 0.03, 0.6, seed + 2)
    return tf, allv


def m032_slab(a, co, tris, ztop, zbot, mat, bands=()):
    """m032.slab with constant levels: top, bottom, walls with extra rings `bands` below the top."""
    import m032
    return m032.slab(a, co, tris, lambda p: ztop, lambda p: zbot, mat, bands=bands)


# ---- plants (each leaf, petal, disc, stem and bud its own closed shell; bases sunk into what they stand on) --------
SINK = 0.035


def _leaf(a, base, L, W, key, yaw, pitch, curl=0.2, fold=0.12, shape="lance", thick=0.05):
    vs = K.leaf(a, tuple(base), L, W, key, yaw=yaw, pitch=pitch, fold=fold, curl=curl, thick=thick, shape=shape,
                camber=0.07)
    bmesh.ops.recalc_face_normals(a.bm, faces=_faces(vs))
    return vs


def _bipyramid(a, c, r, h_up, h_dn, n, key, rot=0.0):
    bm = a.bm
    ring = [bm.verts.new(Vector(c) + Vector((math.cos(rot + 2 * math.pi * k / n) * r,
                                              math.sin(rot + 2 * math.pi * k / n) * r, 0.0))) for k in range(n)]
    top = bm.verts.new(Vector(c) + Vector((0, 0, h_up)))
    bot = bm.verts.new(Vector(c) - Vector((0, 0, h_dn)))
    fs = []
    for k in range(n):
        j = (k + 1) % n
        fs.append(bm.faces.new((ring[k], ring[j], top)))
        fs.append(bm.faces.new((ring[j], ring[k], bot)))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    vs = ring + [top, bot]
    a._finish(vs, key, tint=1.0)
    return vs


def _stem(a, p0, p1, r, key):
    """A thin closed triangular prism from p0 to p1 (8 tris)."""
    bm = a.bm
    p0, p1 = Vector(p0), Vector(p1)
    ax = (p1 - p0).normalized()
    u = ax.orthogonal().normalized()
    w = ax.cross(u)
    r0 = [bm.verts.new(p0 + (u * math.cos(t) + w * math.sin(t)) * r) for t in (0.0, 2.094, 4.189)]
    r1 = [bm.verts.new(p1 + (u * math.cos(t) + w * math.sin(t)) * r * 0.8) for t in (0.0, 2.094, 4.189)]
    fs = [bm.faces.new((r0[2], r0[1], r0[0])), bm.faces.new((r1[0], r1[1], r1[2]))]
    for i in range(3):
        j = (i + 1) % 3
        fs.append(bm.faces.new((r0[i], r0[j], r1[j], r1[i])))
    _tri(bm, fs)
    vs = r0 + r1
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, key, tint=1.0)
    return vs


def rosette(a, hub, n, Lr, W, pitch, key_fn, seed, curl=0.2, shape="lance", fold=0.14):
    """n leaves from one hub (each base 0.05 out from the hub along its yaw, sunk SINK into the ground): key_fn(i, t)
    gives each leaf's key (t = 0 for the lowest / outer leaf .. 1 for the innermost)."""
    rng = random.Random(seed)
    y0 = rng.uniform(0, 2 * math.pi)
    out = []
    for i in range(n):
        yaw = y0 + 2 * math.pi * (i + rng.uniform(-0.15, 0.15)) / n
        L = rng.uniform(*Lr)
        p = rng.uniform(*pitch)
        b = Vector(hub) + Vector((math.cos(yaw), math.sin(yaw), 0.0)) * 0.06 - Vector((0, 0, SINK))
        t = (p - pitch[0]) / max(1e-6, pitch[1] - pitch[0])
        vs = _leaf(a, b, L, L * W * rng.uniform(0.85, 1.1), key_fn(i, t), yaw, p, curl=curl, shape=shape, fold=fold)
        out.append(vs)
    return out


def fern(a, hub, R, H, n, seed, lit=True):
    """Dark fern rosette: narrow pointed leaves arching out and up (dark green, the upper ones lit)."""
    pitch = (math.atan2(H, R) * 0.75, math.atan2(H, R) * 1.25)
    key = lambda i, t: _mix(LEAF, LEAF_LIT, 0.5) if (lit and t > 0.55) else LEAF
    core = _core(a, hub, R, H, _mix(LEAF, LEAF_LIT, 0.25), seed)
    return [core] + rosette(a, hub, n, (math.hypot(R, H) * 0.9, math.hypot(R, H) * 1.1), 0.42, pitch, key, seed,
                            curl=0.28)


def _core(a, hub, R, H, key, seed):
    """A clump's leafy heart (12 tris, a low hexagonal bipyramid sunk into the ground at the hub): it fills the
    rosette into a bushy mound, as the sheet's clumps read."""
    return _bipyramid(a, Vector(hub) + Vector((0, 0, 0.22 * H)), 0.42 * R, 0.32 * H, 0.22 * H + SINK, 6, key,
                      random.Random(seed + 3).uniform(0, 1))


def lime_rosette(a, hub, R, H, n, seed):
    """Broad lanceolate lime leaves standing up."""
    pitch = (math.atan2(H, R) * 0.85, math.atan2(H, R) * 1.12)
    key = lambda i, t: _mix(LEAF_LIME, GRASS_LIGHT, 0.25) if t > 0.6 else LEAF_LIME
    core = _core(a, hub, R, H, _mix(LEAF_LIME, LEAF, 0.5), seed)
    return [core] + rosette(a, hub, n, (math.hypot(R, H) * 0.9, math.hypot(R, H) * 1.05), 0.6, pitch, key, seed,
                            curl=0.12, shape="ovate")


def round_leaves(a, hub, R, n, seed):
    key = lambda i, t: LEAF_LIT
    return rosette(a, hub, n, (R * 0.85, R * 1.0), 0.8, (0.25, 0.45), key, seed, curl=0.15, shape="ovate", fold=0.2)


def daisy(a, ground, r, h, seed):
    """A white daisy: a stem from the ground (sunk SINK), a yellow disc on top, 5 petals round it (each base 0.04 out
    along its direction, inside the disc)."""
    rng = random.Random(seed)
    g = Vector(ground)
    top = g + Vector((rng.uniform(-0.05, 0.05), rng.uniform(-0.05, 0.05), h))
    out = [_stem(a, g - Vector((0, 0, SINK)), top + Vector((0, 0, 0.02)), 0.05, LEAF_LIME)]
    out.append(_bipyramid(a, top + Vector((0, 0, 0.03)), r * 0.3, r * 0.2, r * 0.12, 5, FLOWER, rng.uniform(0, 1)))
    y0 = rng.uniform(0, 2 * math.pi)
    for k in range(5):
        yaw = y0 + 2 * math.pi * k / 5
        b = top + Vector((math.cos(yaw), math.sin(yaw), 0.0)) * 0.04 + Vector((0, 0, 0.004 * k))
        out.append(_petal(a, b, r * 0.55, r * 0.42, yaw, 0.12))
    return out


def _petal(a, base, L, W, yaw, pitch, key=PETAL):
    """A rounded petal (8 tris, a closed lens): base, two shoulders, a blunt tip, a raised top and a lowered back."""
    bm = a.bm
    rot = Matrix.Rotation(yaw, 3, "Z") @ Matrix.Rotation(-pitch, 3, "Y")
    B = Vector(base)
    ring = [(0.0, 0.0, 0.0), (0.5 * L, -0.5 * W, 0.02), (L, 0.0, 0.0), (0.5 * L, 0.5 * W, 0.02)]
    o = [bm.verts.new(B + rot @ Vector(p)) for p in ring]
    t = bm.verts.new(B + rot @ Vector((0.5 * L, 0.0, 0.05)))
    b = bm.verts.new(B + rot @ Vector((0.5 * L, 0.0, -0.03)))
    fs = []
    for i in range(4):
        j = (i + 1) % 4
        fs.append(bm.faces.new((o[i], o[j], t)))
        fs.append(bm.faces.new((o[j], o[i], b)))
    vs = o + [t, b]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    a._finish(vs, key, tint=1.0)
    return vs


def bud(a, ground, h, size, key, seed):
    g = Vector(ground)
    top = g + Vector((0, 0, h))
    return [_stem(a, g - Vector((0, 0, SINK)), top + Vector((0, 0, 0.05)), 0.04, LEAF),
            _bipyramid(a, top + Vector((0, 0, size * 0.25)), size * 0.3, size * 0.75, size * 0.3, 5, key,
                       random.Random(seed).uniform(0, 1))]


def drop(a, ground, size, key, seed):
    """A small round bud sitting on the ground (yellow drops in the foot clump)."""
    g = Vector(ground)
    return [_bipyramid(a, g + Vector((0, 0, size * 0.35 - SINK)), size * 0.5, size * 0.6, size * 0.4, 5, key,
                       random.Random(seed).uniform(0, 1))]


CAP_PLANTS = [  # kind, (x, y), params, seed
    ("fern", (-0.7, 4.7), (1.6, 1.9, 7), 41601),
    ("lime", (1.0, 5.5), (1.45, 2.8, 6), 41602),
    ("lime", (3.9, 4.9), (1.4, 2.2, 5), 41603),
    ("fern", (2.2, 1.7), (1.05, 1.0, 5), 41604),
    ("round", (-1.0, 2.0), (0.55, 3), 41605),
    ("daisy", (0.6, 2.4), (1.15, 0.45), 41606),
    ("daisy", (3.0, 3.9), (0.95, 0.4), 41607),
    ("daisy", (4.4, 2.2), (0.85, 0.35), 41608),
    ("bud", (0.2, 5.0), (0.5, 0.8, BUD), 41609),
]
FOOT_PLANTS = [  # on the sand (z = sand_z at the hub)
    # F1, the foot clump between FL's back-right and the stack's front (hero x 197-262): broad lime leaves, dark
    # leaves, a daisy, yellow drops and a pink bud
    ("lime", (-0.9, -4.5), (2.2, 1.6, 5), 41701),
    ("fern", (-1.8, -3.8), (1.6, 1.4, 4), 41702),
    ("daisy", (-1.5, -5.2), (1.2, 0.8), 41703),
    ("bud", (-0.1, -3.9), (0.6, 1.0, BUD_PINK), 41704),
    ("drop", (0.1, -5.1), (0.32, FLOWER), 41705),
    ("drop", (-0.6, -5.7), (0.3, FLOWER), 41706),
    ("sprig", (8.65, 2.6), (0.6, 2.0, 3), 41708),
    ("fern", (5.0, 7.4), (0.9, 1.4, 5), 41709),
    ("fern", (-3.5, 8.0), (0.7, 1.2, 3), 41710),
    ("sprig", (8.2, 4.7), (0.4, 1.0, 2), 41711),
]


def plant(a, kind, xy, prm, seed, z):
    g = (xy[0], xy[1], z)
    if kind == "fern":
        return fern(a, g, *prm, seed)
    if kind == "lime":
        return lime_rosette(a, g, *prm, seed)
    if kind == "round":
        return round_leaves(a, g, *prm, seed)
    if kind == "daisy":
        return daisy(a, g, prm[0], prm[1], seed)
    if kind == "bud":
        return bud(a, g, prm[1], prm[0], prm[2], seed)
    if kind == "drop":
        return drop(a, g, prm[0], prm[1], seed)
    if kind == "sprig":
        R, H, n = prm
        key = lambda i, t: LEAF_LIME if t > 0.4 else _mix(LEAF_LIME, LEAF, 0.5)
        return rosette(a, g, n, (H * 0.9, H * 1.05), 0.2, (1.15, 1.4), key, seed, curl=0.15)
    raise ValueError(kind)


def cap_plants(a):
    for kind, xy, prm, seed in CAP_PLANTS:
        for vs in plant(a, kind, xy, prm, seed, TURF):
            _mottle(a, _faces(vs), 0.04, 0.9, seed, tint=random.Random(seed).uniform(0.96, 1.04))


def foot_plants(a):
    for kind, xy, prm, seed in FOOT_PLANTS:
        for vs in plant(a, kind, xy, prm, seed, sand_z(xy)):
            _mottle(a, _faces(vs), 0.04, 0.9, seed, tint=random.Random(seed).uniform(0.96, 1.04))


def sand_pebbles(a):
    for p, s, brown, seed in SAND_PEBBLES:
        pebble(a, p, s, brown, seed, sand_z(p) - 0.05)


# ---- water and foam (spec 6, 7) ------------------------------------------------------------------------------------
WATER_GAP = 0.08          # the water's holes stand this far off every land piece's section (z 0.25 .. 1.07)
FOAM_GAP = 0.06           # the foam's inner edges stand this far off the land's section at the foam (1.03 .. 1.07)
HOLES = {}                # name -> (water hole, foam hole) 2D polygons
HOLE_MIN_EDGE = 0.75      # no hole edge shorter (the CDT's needle pass collapses edges up to 0.7 to their middle)


def _section_hull(vs, z0, z1):
    """2D convex hull of a convex piece's part between z0 and z1: its verts in the band and its edges' crossings."""
    pts = [v.co.copy() for v in vs if z0 <= v.co.z <= z1]
    for e in {e for v in vs for e in v.link_edges}:
        p, q = e.verts[0].co, e.verts[1].co
        for zc in (z0, z1):
            if (p.z - zc) * (q.z - zc) < 0:
                t = (zc - p.z) / (q.z - p.z)
                pts.append(p + (q - p) * t)
    return _hull2([(p.x, p.y) for p in pts]) if len(pts) >= 3 else []


def _hole(hull, margin, nmax):
    """A convex hull simplified to nmax corners (no edge under 0.3), offset by margin plus what was cut off."""
    simp = _simplify_convex(hull, nmax)
    while len(simp) > 5:
        el = [(simp[(i + 1) % len(simp)] - simp[i]).length for i in range(len(simp))]
        i = min(range(len(simp)), key=lambda k: el[k])
        if el[i] >= HOLE_MIN_EDGE:
            break
        simp.pop((i + 1) % len(simp) if el[i - 1] > el[(i + 1) % len(simp)] else i)
    loss = max([min(_seg_d(q, simp[i], simp[(i + 1) % len(simp)]) for i in range(len(simp)))
                if not any((q - s).length < 1e-6 for s in simp) else 0.0 for q in hull] + [0.0])
    out = _offset_poly(simp, margin + loss)
    if min((out[(i + 1) % len(out)] - out[i]).length for i in range(len(out))) < HOLE_MIN_EDGE:
        # a small hole: a regular polygon round it with every edge at least HOLE_MIN_EDGE long
        c = _centroid(hull)
        R = max((q - c).length for q in hull) + margin
        n = max(4, min(6, int(2 * math.pi * R / HOLE_MIN_EDGE)))
        Rc = max(R / math.cos(math.pi / n), HOLE_MIN_EDGE / (2 * math.sin(math.pi / n)))
        out = [c + Vector((math.cos(2 * math.pi * k / n + 0.3), math.sin(2 * math.pi * k / n + 0.3))) * Rc
               for k in range(n)]
    return out


def holes():
    """Every land piece's water hole (its section from the bed to above the foam) and foam hole (its section at the
    foam), from a throwaway build of the pieces. The shelf's are its edge polygon offset."""
    if HOLES:
        return HOLES
    a = K.fk().Asset(PFX + "probe", "probe")
    pieces = {}
    for name, vs in main_rock(a).items():
        pieces[name] = (vs, 8, 9)
    for name, r in ROCKS.items():
        if r[3] < 1.0:
            n = 7 if r[1] * r[2] > 12 else 5
            pieces[name] = (rock(a, name), n, n)
    for i, (p, s, brown, seed) in enumerate(WATER_PEBBLES):
        pieces[f"peb{i}"] = (pebble(a, p, s, brown, seed, 0.15, WPEB_TOP[i]), 5, 5)
    E = shelf_poly()
    for name, (vs, nw, nf) in pieces.items():
        hw = _section_hull(vs, WATER_BOT - 0.05, FOAM_Z[1] + 0.02)
        hf = _section_hull(vs, FOAM_Z[0] - 0.01, FOAM_Z[1] + 0.01)
        if len(hw) < 3:
            continue
        # a piece wholly inside the shelf's edge makes no hole (the shelf's own hole covers it)
        if all(_inside(q, E) and _dist_line(q, E, True) > 0.2 for q in hw):
            continue
        HOLES[name] = (_hole(hw, WATER_GAP, nw), _hole(hf, FOAM_GAP, nf) if len(hf) >= 3 else None)
    a.bm.free()
    # the water's shelf hole is a simplified edge (fewer wall faces), grown by the simplification tolerance
    import m032
    simp = m032._rdp_closed([Vector(p) for p in E], SHELF_SIMPLIFY)
    HOLES["shelf"] = (_offset_poly(_ccw(simp), WATER_GAP + SHELF_SIMPLIFY), _offset_poly(E, FOAM_GAP))
    return HOLES


SHELF_SIMPLIFY = 0.18


def plate_inset(d):
    return _offset_poly(_ccw(PLATE), -d)


def water(a, with_holes=True):
    """The water slab: top 1.0, bottom 0.25 (0.05 over the bed), its sides 0.02 inside the plate outline, cut round
    the shelf and every rock and pebble in it. A flat top (the sheet's "flat water plane with simple thickness")."""
    poly = _resample_poly(plate_inset(SEAM_INSET), 9.5)
    neg = [h[0] for h in holes().values()] if with_holes else []
    co, tris = cdt_region([poly], neg, (), min_island=1.0)
    return m034.slab(a, co, tris, WATER_TOP, WATER_BOT, WATER)


# the shore ribbon: segments along the shelf edge (fractions of its perimeter), widths lobed between FOAM_RIB_W
FOAM_RIB_W = (0.42, 1.0)
FOAM_SEGS = [(0.02, 0.17), (0.2, 0.36), (0.395, 0.55), (0.58, 0.74), (0.77, 0.985)]
FOAM_CAP = 0.9            # the rounded end of each ribbon segment (studs)
FOAM_BUBBLES = [0.07, 0.27, 0.47, 0.66, 0.86]     # bubble holes (perimeter fractions), a row along the shore
# collars round the rocks in the water: name -> width (lobed +-30 %)
FOAM_RING = {"FL+FLb": 1.05, "L": 0.9, "BL": 0.75, "BR": 1.0, "FR+FRb": 0.95, "FS": 0.8}
FOAM_STEP = 1.9
FOAM_RING_SCALE = 0.55
FOAM_BLOBS = [((-11.4, -3.8), 0.45), ((2.6, -11.6), 0.42), ((12.2, 1.4), 0.42), ((-2.0, 11.2), 0.42),
              ((-9.8, 6.2), 0.36)]


def _perim(P):
    cum = [0.0]
    for i in range(len(P)):
        cum.append(cum[-1] + (P[(i + 1) % len(P)] - P[i]).length)
    return cum


def _at_s(P, cum, s):
    L = cum[-1]
    s %= L
    for i in range(len(P)):
        if s <= cum[i + 1] + 1e-9:
            t = (s - cum[i]) / max(1e-9, cum[i + 1] - cum[i])
            return P[i].lerp(P[(i + 1) % len(P)], t)
    return P[0]


def _normal_s(P, cum, s):
    q0, q1 = _at_s(P, cum, s - 0.6), _at_s(P, cum, s + 0.6)
    t = (q1 - q0).normalized()
    return Vector((t.y, -t.x))          # outward for a CCW polygon


def foam_regions():
    """(pos, neg) 2D polygons of the foam: the shore ribbon in segments (lobed widths, rounded ends), a lobed collar
    round every rock and pebble in the water (its inner edge the rock's foam hole: no blue ring), loose blobs; neg:
    the holes, the shelf (grown FOAM_GAP), bubble holes in the ribbon, and a 0.3 band inside the plate outline."""
    rng = random.Random(41801)
    E = shelf_poly()
    P = _resample_poly(_offset_poly(E, FOAM_GAP), 0.9)
    cum = _perim(P)
    L = cum[-1]
    pos, neg = [], []
    for f0, f1 in FOAM_SEGS:
        s0, s1 = f0 * L, f1 * L
        n = max(2, int(math.ceil((s1 - s0) / FOAM_STEP)))
        ss = sorted(set([s0 + (s1 - s0) * k / n for k in range(n + 1)] + [s0 + 0.3, s1 - 0.3]))
        inner, outer = [], []
        for s in ss:
            p = _at_s(P, cum, s)
            nrm = _normal_s(P, cum, s)
            w0, w1 = FOAM_RIB_W
            w = w0 + (w1 - w0) * (0.5 + 0.5 * math.sin(s * 0.9 + 1.3)) * rng.uniform(0.85, 1.15)
            dd = min(s - s0, s1 - s)
            if dd < FOAM_CAP:
                w *= max(0.25, math.sqrt(max(0.0, 1.0 - (1.0 - dd / FOAM_CAP) ** 2)))
            inner.append(p - nrm * 0.25)          # under the shelf's neg (so the inner edge is exactly the hole)
            outer.append(p + nrm * w)
        pos.append(_ccw(inner + list(reversed(outer))))
    for fb in FOAM_BUBBLES:
        s = fb * L
        p = _at_s(P, cum, s) + _normal_s(P, cum, s) * 0.55
        neg.append([p + Vector((math.cos(t), math.sin(t) * 0.8)) * rng.uniform(0.2, 0.26)
                    for t in [rng.uniform(0, 1) + 2 * math.pi * k / 4 for k in range(4)]])
    hs = holes()
    for names, w in FOAM_RING.items():
        names = names.split("+")
        if any(nm not in hs or hs[nm][1] is None for nm in names):
            continue
        # a lodged pair (FL + FLb, FR + FRb) shares one collar round both
        hole = _hull2([p for nm in names for p in hs[nm][1]]) if len(names) > 1 else hs[names[0]][1]
        c = _centroid(hole)
        n = 7 if w >= 0.9 else 6
        th0 = rng.uniform(0, 2 * math.pi)
        ring = []
        for k in range(n):
            th = th0 + 2 * math.pi * (k + rng.uniform(-0.15, 0.15)) / n
            d = Vector((math.cos(th), math.sin(th)))
            ring.append(c + d * (_ray_poly(c, d, hole) + w * FOAM_RING_SCALE * rng.uniform(0.7, 1.3)))
        pos.append(ring)
    for c, r in FOAM_BLOBS:
        a0 = rng.uniform(0, 6.3)
        pos.append([Vector(c) + Vector((math.cos(t), math.sin(t) * 0.8)) * r * rng.uniform(0.85, 1.15)
                    for t in [a0 + 2 * math.pi * k / 4 for k in range(4)]])
    neg += [h[1] for h in hs.values() if h[1] is not None]
    # a 0.3 band inside the plate outline: one outward quad per plate edge
    pin = plate_inset(0.3)
    for i in range(len(pin)):
        p, q = pin[i], pin[(i + 1) % len(pin)]
        t = (q - p).normalized()
        nrm = Vector((t.y, -t.x))
        neg.append([p - t * 3, q + t * 3, q + t * 3 + nrm * 5, p - t * 3 + nrm * 5])
    return pos, neg


def foam(a):
    pos, neg = foam_regions()
    co, tris = cdt_region(pos, neg, min_island=0.08)
    return m034.slab(a, co, tris, FOAM_Z[1], FOAM_Z[0], FOAM)


# ---- parts and the hero ------------------------------------------------------------------------------------------
SIDE_ORDER = sorted([n for n in ROCKS], key=lambda n: -ROCKS[n][1] * ROCKS[n][2])


def hero_land(a):
    """The terrace first, then the stack's pieces, the side and sand rocks largest first, then the pebbles in the
    water: closed shells the union fuses one at a time."""
    terrace(a, with_bed=True)
    main_rock(a)
    for name in SIDE_ORDER:
        rock(a, name)
    for i, (p, s, brown, seed) in enumerate(WATER_PEBBLES):
        pebble(a, p, s, brown, seed, 0.15, WPEB_TOP[i])


def hero_rest(a):
    """Everything outside the land union: the water, the foam, the cap and its plants, the foot plants, the sand
    pebbles (each its own closed shell)."""
    water(a)
    foam(a)
    cap_slab(a)
    cap_plants(a)
    foot_plants(a)
    sand_pebbles(a)


def grass_cap_part(a):
    cap_slab(a)
    cap_plants(a)


def main_rock_part(a):
    main_rock(a, foot_z=1.3)


def rock_large_part(a):
    rock(a, "FL", at_origin=True)


def rock_medium_part(a):
    rock(a, "BR", at_origin=True)


def rock_small_part(a):
    rock(a, "FS", at_origin=True)


def sand_part(a):
    terrace(a, with_bed=False)
    for name in ("S1", "S2"):
        rock(a, name)


def water_plane_part(a):
    water(a)


NOTES = {
    HERO: "shore shelf water tile (32 x 28 octagon, 7 x 7 chamfers; seams X -9..9 / Y -7..7; ground 0, bed 0.2, water "
          "0.25 -> 1.0, foam 1.03 -> 1.07, sand crest 1.6, turf 10.4): a flat cyan water plate with a pale sand shelf, "
          "one faceted sea stack (three columns, a spire, two shoulder blocks) under a lime grass cap with ferns, lime "
          "leaves, daisies and buds; six chunky flat-crowned side rocks in soft lobed foam, a foam ribbon round the "
          "shelf. One closed land shell; the cap, plants and sand pebbles their own shells; closed water and foam "
          "shells (two water pieces). Still water (no flow). 13 water_foam sockets",
    CAP_P: "Grass Cap (reusable): a flat turf slab (lime top, brown soil sides) with ferns, lime rosettes, daisies, buds",
    ROCK_P: "Main Rock (reusable): the sea stack: a summit block, two columns with bevelled tips, a spire, two shoulder "
            "blocks; flat summit under the cap",
    RL_P: "Side Rock Large (reusable): a broad chunky flat-crowned boulder (FL)",
    RM_P: "Side Rock Medium (reusable): a taller chunky boulder with a small stepped knob on its crown (BR)",
    RS_P: "Side Rock Small (reusable): a small flat-topped rock (FS)",
    SAND_P: "Sand Shelf (reusable): the lobed sand slab (crest 1.6, bevelled edge) with two small rocks and pebbles",
    WATER_P: "Water Plane (reusable): the see-through water slab (top 1.0) with the shelf and rock holes",
}

# ---- stages 5 + 6 (spec 7) ------------------------------------------------------------------------------------------
# Stage 5: nothing glows (decision 10): no emissive key, no light. Stage 6 (decision 7): 13 water_foam sockets at
# z 1.05 on open water, each >= 0.5 off every rock footprint: 7 along the shore (scale 0.7), 6 on the rocks' seaward
# sides
FOAM_FX = [((0.5, -10.6), 0.7), ((4.2, -10.8), 0.7), ((11.5, -1.7), 0.7), ((11.2, 2.8), 0.7), ((4.2, 10.2), 0.7),
           ((-2.4, 10.6), 0.7), ((-8.6, -3.0), 0.7),
           ((-6.0, -11.4), 1.0), ((-11.6, 1.9), 0.7), ((-6.7, 11.8), 0.5), ((9.4, 11.4), 0.9), ((12.4, -9.6), 0.8),
           ((8.3, -9.6), 0.5)]


def socket_clearance():
    """Per foam socket: the distance to the nearest water hole (negative: inside one)."""
    hs = holes()
    out = []
    for (x, y), _s in FOAM_FX:
        p = Vector((x, y))
        best = 1e9
        for name, (hw, _hf) in hs.items():
            d = -1.0 if _inside(p, hw) else _dist_line(p, hw, True)
            best = min(best, d)
        out.append(round(best, 2))
    return out


def _sockets(o):
    off = Vector(o[OFF])
    for (x, y), sc in FOAM_FX:
        K.socket(o, "water_foam", Vector((x, y, 1.05)) - off, scale=sc)


# ---- union, cleanup (m034 / m033) -----------------------------------------------------------------------------------
UNION_RETRIES = []


def _union_fine(o):
    """Exact unions one shell at a time in face order, no post-union weld, with a guard against a union that drops
    most of the mesh (m034)."""
    bpy.context.view_layer.update()
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
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    M.drop_specks(bm, min_area=0.02)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    K.drop_unused_slots(o)
    return len(others)


def _clean_mesh(o, planes):
    """m016._clean_mesh with a smaller largest vertex move (CLEAN_MOVE), so the land never moves into the water's or
    the foam's gap."""
    m016._weld(o)
    ears = m016._dissolve_ears(o)
    pockets = m012._drop_inner(o)
    log = m011._clean(o, m011._plane_lock(planes), max_move=CLEAN_MOVE)
    pockets += m012._drop_inner(o)
    log["ears"] = ears
    log["pockets"] = pockets
    log["forced"] = m012._force_slivers(o)
    return log


def _finish(o):
    o[OFF] = list(Vector(o[OFF]) + m012._bottom_centre(o))
    res = M.finish(o, union=False, uv=False)
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
        res = M.finish(o, union=False, uv=False)
    return res


def _polish(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = m012._tri_quads(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = m012._force_slivers(o, lim=POLISH_LIM)
    if m012._thin(o, POLISH_LIM)["under"]:
        forced += m012._force_slivers(o, lim=POLISH_LIM, max_len=0.5)
    _recentre(o)
    return {"split": split, "forced": forced}


def _recentre(o):
    bc = m012._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


def _uv(o):
    for p in o.data.polygons:
        p.use_smooth = False
    M.smart_uv(o, **UV)
    return m012._uv_unfold(o)


def _join_built(o, fn, name):
    """Build fn into a temporary object in the same build frame as o and join it into o (no union, no weld)."""
    a = K.fk().Asset(PFX + name, "probe", seed=7, tint_var=0.0)
    fn(a)
    c = a.finish(collection=o.users_collection[0], mark_asset=False, origin=None)
    c.matrix_world = o.matrix_world @ Matrix.Translation(-Vector(o[OFF]))
    bpy.context.view_layer.update()
    with M._override(o):
        c.select_set(True)
        with bpy.context.temp_override(selected_objects=[o, c], selected_editable_objects=[o, c]):
            bpy.ops.object.join()
    return o


def _tri_all(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    _tri(bm, list(bm.faces))
    bm.to_mesh(o.data)
    bm.free()


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m041_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", "ShoreShelf"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


PLANES = (0.0, BED_TOP, SAND_EDGE, SAND_TOP, SUMMIT)
# K.check's baked-shading test reads the Sand part's deep-sand side walls (the wet sand below the waterline, close-up
# B's #BB9666 underside, painted by position) against its pale top as light painted by facing; in the hero they are
# under the water
SHADING_OK = ("the shelf's side walls are the wet sand below the waterline (close-up B: the underside reads #BB9666), "
              "a real colour region painted by position (the bevel and walls deep sand, the crest pale)")
SHADING_OK_OBJS = (SAND_P,)
# name, builder, mode ("union": one closed shell; "shells": several closed shells, no union; "sand": the slab and its
# rocks united, then the pebbles added as their own shells; "water": one shell, no union), collision
PARTS = ((CAP_P, grass_cap_part, "shells", "hull"), (ROCK_P, main_rock_part, "union", "hull"),
         (RL_P, rock_large_part, "union", "hull"), (RM_P, rock_medium_part, "union", "hull"),
         (RS_P, rock_small_part, "union", "hull"), (SAND_P, sand_part, "sand", "precise"),
         (WATER_P, water_plane_part, "water", "none"))
TARGET_SIZE = ((32.0, 0.1), (28.0, 0.1), (13.2, 0.6))


def _make(name, fn, mode, collision):
    t0 = time.time()
    o = M.mk(SHEET, name, fn, subject=TITLE, role="part", notes=NOTES[name], budget=1000, collision=collision,
             tint_var=0.0)
    off = M._build_offset(fn)
    o[OFF] = list(off)
    o.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    lg = {}
    if mode in ("water", "shells"):
        _recentre(o)
        m016._weld(o, 1e-5)
        _tri_all(o)
        lg["bowties"] = M.fix_bowties(o)
        K.drop_unused_slots(o)
        lg["uv_cut"] = _uv(o)
        return o, lg
    lg["shells_merged"] = _union_fine(o)
    lg["clean"] = {k: v for k, v in _clean_mesh(o, tuple(z - off.z for z in PLANES)).items()
                   if not isinstance(v, (list, dict))}
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    lg["bowties"] = M.fix_bowties(o)
    if mode == "sand":
        _join_built(o, sand_pebbles, "sandpeb")
        _tri_all(o)
        _recentre(o)
    K.drop_unused_slots(o)
    lg["uv_cut"] = _uv(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


def _make_hero():
    t0 = time.time()
    o = M.mk(SHEET, HERO, hero_land, subject=TITLE, role="hero", notes=NOTES[HERO], budget=4000, collision="precise",
             tint_var=0.0)
    off = M._build_offset(hero_land)
    o[OFF] = list(off)
    o.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    lg = {"t_build": round(time.time() - t0, 1)}
    lg["shells_merged"] = _union_fine(o)
    lg["t_union"] = round(time.time() - t0, 1)
    lg["clean"] = {k: v for k, v in _clean_mesh(o, PLANES).items() if not isinstance(v, (list, dict))}
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    lg["bowties_land"] = M.fix_bowties(o)
    lg["land"] = {k: v for k, v in M.audit(o).items() if k in ("tris", "shells", "nonmanifold_edges",
                                                                  "nonmanifold_verts", "boundary_edges")}
    lg["land_self_hits"] = m016._self_hits(o)[0]
    _join_built(o, hero_rest, "rest")
    _tri_all(o)
    lg["bowties_rest"] = M.fix_bowties(o)
    _recentre(o)
    K.drop_unused_slots(o)
    lg["uv_cut"] = _uv(o)
    _sockets(o)
    lg["t_total"] = round(time.time() - t0, 1)
    return o, lg


# ---- reports ---------------------------------------------------------------------------------------------------------
LAND_KEYS = ("m041_rock", "m041_sand", "m041_bed", "m041_pebble")
PLANT_KEYS = ("m041_leaf", "m041_petal", "m041_flower", "m041_bud", "m041_grass_light")


def _keys(o):
    return [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]


def _shell_kind(ks, nf):
    if ks == {FOAM}:
        return "foam"
    if ks == {WATER}:
        return "water"
    if any(k.startswith(("m041_grass", "m041_soil")) for k in ks) and nf > 40:
        return "cap"
    if all(k.startswith(LAND_KEYS) for k in ks):
        return "land" if nf > 200 else "pebble"
    return "plant"


def shells_report(o):
    """Per shell: kind (land / water / foam / cap / plant / pebble), tris, non-manifold edges and verts, boundary
    edges, self-intersecting face pairs inside the shell, outward volume."""
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
        out.append({"kind": _shell_kind(ks, len(fs)), "tris": sum(len(f.verts) - 2 for f in fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary), "self_hits": hits,
                    "volume": round(vol, 3)})
    bm.free()
    return out


def contact_report(o, tol=0.03, chain_tol=0.1):
    """Floating dressing (STAGES): over every shell but the water and the foam, whether it touches another shell
    (triangles overlap, or a vert within tol of another shell's surface) or the ground; the shells touching nothing,
    the worst such gap, and the shells with no chain of contact down to the land shell (the largest)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    keys = _keys(o)
    wet = [f for f in bm.faces if keys[f.material_index] in (WATER, FOAM)]
    bmesh.ops.delete(bm, geom=wet, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    bm.faces.index_update()
    bm.verts.index_update()
    ids, n = M._shell_ids(bm)
    fsh = [ids[f.index] for f in bm.faces]
    vsh = {}
    for f in bm.faces:
        for v in f.verts:
            vsh[v.index] = fsh[f.index]
    tree = BVHTree.FromBMesh(bm)
    zmin = [1e9] * n
    for v in bm.verts:
        zmin[vsh[v.index]] = min(zmin[vsh[v.index]], v.co.z)
    area = [0.0] * n
    for f in bm.faces:
        area[fsh[f.index]] += f.calc_area()
    land = max(range(n), key=lambda k: area[k])
    near = {}
    for i, j in tree.overlap(tree):
        a_, b_ = fsh[i], fsh[j]
        if a_ != b_:
            near[(min(a_, b_), max(a_, b_))] = 0.0
    for v in bm.verts:
        s = vsh[v.index]
        for _loc, _n, fi, d in tree.find_nearest_range(v.co, chain_tol):
            t = fsh[fi]
            if t != s:
                kk = (min(s, t), max(s, t))
                near[kk] = min(near.get(kk, 1e9), d)
    gap = [1e9] * n
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    for k in range(n):
        gap[k] = min(gap[k], max(0.0, zmin[k]))

    def chained(t):
        adj = {k: set() for k in range(n)}
        for (a_, b_), d in near.items():
            if d <= t:
                adj[a_].add(b_)
                adj[b_].add(a_)
        seen = {land}
        stack = [land]
        while stack:
            k = stack.pop()
            for m_ in adj[k]:
                if m_ not in seen:
                    seen.add(m_)
                    stack.append(m_)
        return n - len(seen)
    kind = {}
    for f in bm.faces:
        kind.setdefault(fsh[f.index], keys[f.material_index])
    floating = [k for k in range(n) if gap[k] > tol and k != land]
    res = {"shells": n, "floating": len(floating),
           "floating_kinds": sorted({kind[k].replace("m041_", "") for k in floating}),
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "max_gap_all": round(max([gap[k] for k in range(n) if k != land], default=0.0), 3),
           "unchained": chained(tol), "unchained_chain_tol": chained(chain_tol)}
    bm.free()
    return res


def wet_report(o):
    """Water and foam against the land shell: overlapping triangle pairs, the smallest distance from any water / foam
    vert to the land, and the foam's inner-edge plan gap (median and max over the foam verts within 0.5 of the land);
    the bed under the water and the foam over the water."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    keys = _keys(o)
    ids, n = M._shell_ids(bm)
    area = {}
    for f in bm.faces:
        area[ids[f.index]] = area.get(ids[f.index], 0.0) + f.calc_area()
    land_id = max((k for k in area), key=lambda k: area[k] if keys[next(
        f for f in bm.faces if ids[f.index] == k).material_index] not in (WATER, FOAM) else -1)

    def tree_of(fs):
        vs = list({v for f in fs for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        return BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs]), vs
    land_fs = [f for f in bm.faces if ids[f.index] == land_id]
    lt, _ = tree_of(land_fs)
    out = {}
    for key, nm in ((WATER, "water"), (FOAM, "foam")):
        fs = [f for f in bm.faces if keys[f.material_index] == key]
        if not fs:
            continue
        t, vs = tree_of(fs)
        dmin = min(lt.find_nearest(v.co)[3] for v in vs)
        res = {"overlaps": len(t.overlap(lt)), "min_dist": round(dmin, 3),
               "z": [round(min(v.co.z for v in vs), 3), round(max(v.co.z for v in vs), 3)]}
        if key == FOAM:
            top = [v for v in vs if v.co.z > FOAM_Z[1] - 1e-3]
            gaps = []
            for v in top:
                d = lt.find_nearest(Vector((v.co.x, v.co.y, (FOAM_Z[0] + FOAM_Z[1]) / 2)))[3]
                if d < 0.25:
                    gaps.append(d)
            res["inner_gap"] = [round(float(np.median(gaps)), 3), round(max(gaps), 3), len(gaps)] if gaps else None
        out[nm] = res
    bm.free()
    return out


def capping(o):
    """Spec 2.7 capping: rock faces with n.z > 0.85 above z 9.0 outside the cap outline (visible from above), in
    studs^2; and the cap's coverage of the summit (flat land faces above 10.0 outside the cap outline)."""
    capp = _ccw(CAP)
    keys = _keys(o)
    off = Vector(o.get(OFF, (0.0, 0.0, 0.0)))
    exposed = 0.0
    for p in o.data.polygons:
        k = keys[p.material_index]
        if not k.startswith("m041_rock"):
            continue
        c = Vector(p.center) + off
        if p.normal.z > 0.85 and c.z > 9.0 and not _inside(c, capp):
            exposed += p.area
    return round(exposed, 3)


def rock_metrics(o):
    """Spec 2.7 side-rock targets on a rock part (at the origin): tris, triangle-area CV, crown (faces n.z > 0.9 above
    0.7 h) share of the plan, widths per height against the widest, the widest height, the share of the side area
    within 25 deg of vertical, H : W, and facets seen from the front (coplanar neighbours merged)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    fs = list(bm.faces)
    H = max(v.co.z for v in bm.verts)
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]

    def width(z):
        pts = []
        for e in bm.edges:
            a_, b_ = e.verts
            if (a_.co.z - z) * (b_.co.z - z) < 0:
                t = (z - a_.co.z) / (b_.co.z - a_.co.z)
                pts.append(a_.co.lerp(b_.co, t))
        if len(pts) < 3:
            return 0.0
        h = _hull2([(p.x, p.y) for p in pts])
        return max((p - q).length for p in h for q in h)
    zs = [H * f for f in (0.05, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)]
    ws = [width(z) for z in zs]
    wmax = max(ws)
    sides = [f for f in fs if abs(f.normal.z) < 0.99]
    side_a = sum(f.calc_area() for f in sides)
    vert = sum(f.calc_area() for f in sides if abs(f.normal.z) < math.sin(math.radians(25)))
    plan = _hull2([(x, y) for x, y in zip(xs, ys)])
    plan_a = abs(sum(plan[i].x * plan[(i + 1) % len(plan)].y - plan[(i + 1) % len(plan)].x * plan[i].y
                     for i in range(len(plan)))) / 2
    crown = sum(f.calc_area() * f.normal.z for f in fs if f.normal.z > 0.9 and f.calc_center_median().z > 0.7 * H)
    areas = np.array([f.calc_area() for f in fs if f.calc_center_median().z > 0.01])
    view = Vector((0.0, -1.0, 0.3)).normalized()
    regs, seen = [], set()
    for f in fs:
        if f in seen or f.normal.dot(view) <= 0.05:
            continue
        stack, reg = [f], []
        seen.add(f)
        while stack:
            g = stack.pop()
            reg.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h not in seen and h.normal.angle(f.normal, 1.0) < math.radians(4.0):
                        seen.add(h)
                        stack.append(h)
        regs.append(sum(g.calc_area() * g.normal.dot(view) for g in reg))
    tot = sum(regs)
    res = {"tris": sum(len(f.verts) - 2 for f in fs), "H": round(H, 2),
           "W": round(max(xs) - min(xs), 2), "D": round(max(ys) - min(ys), 2),
           "H_W": round(H / (max(xs) - min(xs)), 2), "area_cv": round(float(areas.std() / areas.mean()), 2),
           "crown_share": round(crown / plan_a, 2), "w07": round(width(0.7 * H) / wmax, 2),
           "w09": round(width(0.9 * H) / wmax, 2), "widest_h": round(zs[ws.index(wmax)] / H, 2),
           "base": round(width(0.02 * H) / wmax, 2), "vertical_share": round(vert / side_a, 2),
           "facets_front": sum(1 for r in regs if r / tot >= 0.01)}
    bm.free()
    return res


def report(order):
    h = order[0]
    audits = [M.audit(o) for o in order]
    problems = list(K.check(order))
    shells = shells_report(h)
    kinds = [s["kind"] for s in shells]
    if kinds.count("land") != 1 or kinds.count("water") != 1 or "foam" not in kinds or kinds.count("cap") != 1:
        problems.append(f"{HERO}: shells {dict((k, kinds.count(k)) for k in set(kinds))}, expected one land, one "
                        f"water, one cap, foam")
    bad_sh = {}
    for s in shells:
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "self_hits"):
            if s[k]:
                bad_sh.setdefault(f"{s['kind']}_{k}", 0)
                bad_sh[f"{s['kind']}_{k}"] += s[k]
        if s["volume"] <= 0:
            bad_sh.setdefault(f"{s['kind']}_inward", 0)
            bad_sh[f"{s['kind']}_inward"] += 1
    for k, v in bad_sh.items():
        problems.append(f"{HERO} shells: {k} {v}")
    for o, au in zip(order, audits):
        lim = 4000 if o is h else 1000
        if au["tris"] > lim:
            problems.append(f"{o.name}: {au['tris']} tris over {lim}")
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "wire_edges", "loose_verts",
                  "zero_area_faces", "ngons"):
            if au[k]:
                problems.append(f"{o.name}: {k} {au[k]}")
        if o.name in (ROCK_P, RL_P, RM_P, RS_P, WATER_P) and au["shells"] != 1:
            problems.append(f"{o.name}: {au['shells']} shells")
        if au["normals"] != "outward":
            problems.append(f"{o.name}: normals {au['normals']}")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    socks = [c.get("vfx_kind") for c in h.children if c.get("vfx_kind")]
    if socks.count("water_foam") != 13 or len(socks) != 13:
        problems.append(f"{HERO}: sockets {socks}, expected 13 water_foam")
    sc = socket_clearance()
    if min(sc) < 0.5:
        problems.append(f"{HERO}: foam sockets closer than 0.5 to a rock: {sc}")
    contact = {o.name: contact_report(o) for o in order if o.name in (HERO, CAP_P, SAND_P)}
    for nm, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{nm}: {c['floating']} floating shells, {c['unchained']} unchained")
    wet = wet_report(h)
    for nm, w in wet.items():
        if w["overlaps"] or w["min_dist"] < 0.03:
            problems.append(f"{HERO} {nm}: overlaps {w['overlaps']}, min distance to land {w['min_dist']}")
    cap = capping(h)
    if cap > 1.5:
        problems.append(f"{HERO}: exposed flat rock above 9.0 outside the cap {cap} studs^2 (limit 1.5)")
    rocks = {o.name: rock_metrics(o) for o in order if o.name in (RL_P, RM_P, RS_P)}
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    thin = {o.name: m012._thin(o, POLISH_LIM) for o in order}
    return {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                          "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                          "ngons", "dup_verts")} for au in audits],
            "shells": {k: {"n": kinds.count(k), "tris": sum(s["tris"] for s in shells if s["kind"] == k)}
                       for k in sorted(set(kinds))},
            "contact": contact, "wet": wet, "capping": cap, "rocks": rocks, "thin": thin,
            "problems": problems, "uv": uv,
            "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
            "sockets": {k: socks.count(k) for k in set(socks)}, "socket_clearance": sc}


def build(render=True, parts=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    UNION_RETRIES.clear()
    SHELF_POLY.clear()
    palette()
    HOLES.clear()
    holes()
    objs, log = {}, {}
    if parts:
        for name, fn, mode, coll in PARTS:
            objs[name], log[name] = _make(name, fn, mode, coll)
    h, log["hero"] = _make_hero()
    log["union_retries"] = list(UNION_RETRIES)
    _cleanup_tmp()
    _bed_finish()
    order = [h] + [objs[n] for n, *_ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
        if o.name in SHADING_OK_OBJS:
            o["kit_shading_ok"] = SHADING_OK
        elif "kit_shading_ok" in o:
            del o["kit_shading_ok"]
    out = report(order)
    out["log"] = log
    out["build_s"] = round(time.time() - t0, 1)
    if render:
        out["views"] = render_views(order)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders -----------------------------------------------------------------------------------------------------------
# the sheet's comparison cameras (decision 11): the hero cell is an elevated front view (0, 28); the *_sheet shots use
# a 3x longer lens and hide the studio floor (m033._long_lens; the sheet draws no ground shadow)
SHEET_VIEWS = {"f34_sheet": (0, 28), "r34_sheet": (180, 26), "front_sheet": (0, 10), "side_sheet": (90, 5),
               "rear_sheet": (180, 10), "top_sheet": (0, 89)}
PARTS_SHOT = (-30, 25)
CLOSE = {"cap_cu": (-20, 35, (1.6, 3.6, 10.6), 4.2), "junc_cu": (-25, 22, (-3.4, -3.6, 2.4), 3.6),
         "water_cu": (-20, 40, (10.0, -7.6, 1.6), 3.6)}


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded Construction: the water plane at the bottom, the sand
    shelf above it, the main rock over the shelf, the cap over the rock, the side rocks round about."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []

    def put(tag, part, m):
        if part not in by:
            return
        c = bpy.data.objects.new(f"{PFX}expl_{tag}", by[part].data)
        coll.objects.link(c)
        c.matrix_world = m
        shown.append(c)
    x0 = objs[0].location.x + 80
    o0 = Matrix.Translation((x0, objs[0].location.y, 0))
    tr = lambda part, d: o0 @ Matrix.Translation(d) @ Matrix.Translation(Vector(by[part][OFF]))
    put("water", WATER_P, tr(WATER_P, (0, 0, -4.0)))
    put("sand", SAND_P, tr(SAND_P, (0, 0, 0.0)))
    put("rock", ROCK_P, tr(ROCK_P, (0, 0, 4.5)))
    put("cap", CAP_P, tr(CAP_P, (0, 0, 8.5)))
    S = Matrix.Diagonal
    for tag, part, (x, y, z), s in (("rl", RL_P, (13.0, 0.0, 9.0), 1.0), ("rm", RM_P, (-14.0, 3.0, 8.0), 1.0),
                                    ("rs1", RS_P, (-14.0, -7.0, 3.0), 1.0), ("rs2", RS_P, (-10.0, -11.0, 2.0), 0.9),
                                    ("rs3", RS_P, (13.0, -9.0, 4.0), 0.8), ("rs4", RS_P, (15.0, -3.0, 6.0), 0.75)):
        put(tag, part, o0 @ Matrix.Translation((x, y, z)) @ S((s, s, s, 1)))
    bpy.context.view_layer.update()
    return shown


def _scale_marker(h):
    """A 5.5-stud character stand-in (a plain grey column) on the shelf, for the scale shot."""
    a = K.fk().Asset(PFX + "char", "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=BUD, tint=0.8)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=BUD, tint=0.8)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=BUD, tint=0.8)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    off = Vector(h[OFF])
    c.location = h.location + Vector((5.6, -6.0, sand_z((5.6, -6.0)))) - off
    bpy.context.view_layer.update()
    return c


def render_views(objs, close=True):
    h = objs[0]
    _bed_finish()
    shown = _exploded(objs) if len(objs) > 1 else []
    marker = _scale_marker(h)
    try:
        # the *_sheet comparison shots are rendered without the VFX particle previews (the sheet draws the foam as
        # a mesh, not as particles: the water_foam sprites would read as extra foam); every other shot with them,
        # including f34_vfx (the hero camera with the sockets realised)
        sheet_extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        extra = {"f34_vfx": ([h], *SHEET_VIEWS["f34_sheet"])}
        if shown:
            extra["exploded"] = (shown, -30, 25)
        for o in objs[1:]:
            extra["part_" + o.name.replace("ShoreShelf", "").lower()] = ([o], *PARTS_SHOT)
        extra["scale"] = ([h, marker], -20, 12)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = m033._long_lens(kit)
        try:
            M.views(NUM, [h], names=(), extra=sheet_extra, vfx=False)
            M.views(NUM, [h], extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
        names = list(M.VIEWS) + list(sheet_extra) + list(extra)
        paths = [f"{d}/{n}.png" for n in names]
        rows = [kit["hstack"](paths[i:i + 4]) for i in range(0, len(paths), 4)]
        w = max(r.shape[1] for r in rows)
        rows = [np.concatenate([r, np.ones((r.shape[0], w - r.shape[1], 4), np.float32)], axis=1)
                if r.shape[1] < w else r for r in rows]
        sheet = f"{d}/{M.code(NUM)}_views.png"
        kit["save_px"](kit["vstack"](rows), sheet)
        out = {"sheet": sheet, "order": names}
        if close:
            d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
            off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
            for name, (az, el, c, r) in CLOSE.items():
                out[name] = m033.render_close([h], f"{d}/{name}.png", az, el, off @ Vector(c), r)
            out["under_cu"] = m033.render_close([h], f"{d}/under_cu.png", 20, -30, off @ Vector((0.0, 0.0, 0.5)), 14.0)
        return out
    finally:
        for o in shown + [marker]:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if o is marker and me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def preview(names=("f34_sheet", "top_sheet"), vfx=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    _bed_finish()
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig


def hero_only():
    """Rebuild just the hero (tuning loop): returns its report."""
    M.coll(NUM, TITLE)
    SHELF_POLY.clear()
    palette()
    HOLES.clear()
    holes()
    h, lg = _make_hero()
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, *_ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    sh = shells_report(h)
    kinds = [s["kind"] for s in sh]
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals")}, "log": lg,
            "shells": {k: {"n": kinds.count(k), "tris": sum(s["tris"] for s in sh if s["kind"] == k),
                           "bad": sum(s["nonmanifold_edges"] + s["nonmanifold_verts"] + s["boundary_edges"]
                                      for s in sh if s["kind"] == k)} for k in sorted(set(kinds))},
            "contact": contact_report(h), "wet": wet_report(h), "capping": capping(h),
            "sockets": socket_clearance()}
