"""070 Ruined Lean-To (references/070.png): a camp lean-to built into the corner of a ruined stone wall. An L of big
chamfered pale pink-grey blocks (2.4 deep, 1.65 courses, running bond): a long back wall stepping up to an eight-course
peak left of centre and a five-course side wall at -X ending in a block column at the front, with chipped corners, a
missing top block, a fallen block, lime ivy curtains of five-point leaves on square stems and flat moss patches. Three
square timber posts on pale stone footings (front-left 9.35, back 11.1, front-right 12.0) carry one cream canvas sheet
tied by its corner tabs over square toggles under fat golden X-lashings; its fourth corner hangs free at the front
with a rope tail and a toggle. A crossbeam runs from the front-left post onto the side wall; a red swallowtail banner
with a white emblem (both faces) hangs from a round crossarm in front of the front-right post, held by a dark pole and
an iron sleeve. Inside: a leather bedroll with golden caps, a golden mat with blue-teal stripes, an X-braced crate, an
open-frame side table; an open hooped barrel by the front-right post; loose rubble blocks at the front.

    import importlib, kit_models, m070; importlib.reload(kit_models); importlib.reload(m070); m070.build()

Build frame: studs, front -Y (open, banner at the right), +X right (the second open side), side wall at -X, back wall
at +Y, ground z 0; x 0 midway between the front posts. Every object ends with its origin at its bbox bottom centre;
o["m070_offset"] is that origin in the build frame. Names (spec 8, decision 9):
- RuinedLeanTo (hero): everything above, one object of closed shells (no booleans). Collision precise.
- Parts: RuinedLeanToWallBlock, ...WallSection (the exploded view's chunk with its opening), ...Rubble, ...Canopy,
  ...Post, ...Banner, ...Bedroll, ...Table, ...Crate, ...Barrel.
Colour (stage 4) is painted by role and by position inside the builders, never by facing. Stages 5-6: none (the sheet
shows no light or effect in any assembled view; decision 6). See art/blender/renders/models/M070/M070_spec.md.
Geometry helpers are copied from m048 / m051 / m056 / m064 / m066 (not imported) so this builder stands alone.
"""
import json
import math
import os
import random
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M

NUM, TITLE, SHEET = 70, "Ruined Lean-To", "M070"
OFF = "m070_offset"
PFX = "_m070_"
HERO = "RuinedLeanTo"
BLOCK_P, SECTION_P, RUBBLE_P = "RuinedLeanToWallBlock", "RuinedLeanToWallSection", "RuinedLeanToRubble"
CANOPY_P, POST_P, BANNER_P = "RuinedLeanToCanopy", "RuinedLeanToPost", "RuinedLeanToBanner"
BEDROLL_P, TABLE_P, CRATE_P, BARREL_P = ("RuinedLeanToBedroll", "RuinedLeanToTable", "RuinedLeanToCrate",
                                         "RuinedLeanToBarrel")

TIMBER, TIMBER_END, TIMBER_DEEP = "m070_timber", "m070_timber_end", "m070_timber_deep"
CANVAS, CANVAS_DEEP = "m070_canvas", "m070_canvas_deep"
STONE, STONE_LIGHT, STONE_DARK = "m070_stone", "m070_stone_light", "m070_stone_dark"
IVY_L, IVY_G, IVY_D, STEM = "m070_ivy_lime", "m070_ivy", "m070_ivy_dark", "m070_stem"
ROPE, ROPE_DEEP = "m070_rope", "m070_rope_deep"
BANNER, WHITE, POLE, IRON = "m070_banner", "m070_cloth_white", "m070_pole", "m070_iron"
LEATHER, GOLD, MAT, STRIPE = "m070_leather", "m070_gold", "m070_mat", "m070_stripe"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
BURY = 0.05

# key -> (hex, roughness, metal, emission, low specular). Stage 4 (spec "Stage 4") writes the calibrated values here:
# sampled on the sheet, run through K.calibrate on the studio dome, then re-measured on the hero renders.
PALETTE = {
    TIMBER: ("#864A18", 0.85, 0.0, 0.0, True),
    TIMBER_END: ("#B3741F", 0.8, 0.0, 0.0, True),
    TIMBER_DEEP: ("#4E2812", 0.9, 0.0, 0.0, True),
    CANVAS: ("#CCBDA5", 0.95, 0.0, 0.0, True),       # hue-correct cream under the key light (M064 ruling 1)
    CANVAS_DEEP: ("#BAA58F", 0.95, 0.0, 0.0, True),
    STONE: ("#9A8F8F", 0.9, 0.0, 0.0, True),
    STONE_LIGHT: ("#CBBBBB", 0.9, 0.0, 0.0, True),
    STONE_DARK: ("#66626A", 0.9, 0.0, 0.0, True),
    IVY_L: ("#91AA08", 0.8, 0.0, 0.0, True),
    IVY_G: ("#5E7A12", 0.8, 0.0, 0.0, True),
    IVY_D: ("#3B5616", 0.85, 0.0, 0.0, True),       # a step over its calibration: in shade it went near-black
    STEM: ("#73522E", 0.9, 0.0, 0.0, True),
    ROPE: ("#E4AC54", 0.95, 0.0, 0.0, True),
    ROPE_DEEP: ("#C38B34", 0.95, 0.0, 0.0, True),
    BANNER: ("#C11D23", 0.9, 0.0, 0.0, True),
    WHITE: ("#E2DAD6", 0.9, 0.0, 0.0, True),         # the dome clips white: set below its calibration
    POLE: ("#46322E", 0.85, 0.0, 0.0, True),
    IRON: ("#4A3A36", 0.55, 0.4, 0.0, False),
    LEATHER: ("#6B3C1F", 0.8, 0.0, 0.0, True),
    GOLD: ("#C18419", 0.8, 0.0, 0.0, True),
    MAT: ("#A17737", 0.95, 0.0, 0.0, True),
    STRIPE: ("#3E606D", 0.95, 0.0, 0.0, True),
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions) and K.sample kinds ("all" = paper filtered)
TARGETS = {TIMBER: ((0x96, 0x49, 0x14), "brown"), TIMBER_END: ((0xE2, 0x87, 0x1F), "brown"),
           TIMBER_DEEP: ((0x5E, 0x2B, 0x12), "brown"), CANVAS: ((0xFE, 0xEE, 0xC3), "all"),
           CANVAS_DEEP: ((0xE6, 0xC8, 0xA2), "all"), STONE: ((0xA6, 0x95, 0x8F), "all"),
           STONE_LIGHT: ((0xDE, 0xC4, 0xBB), "all"), STONE_DARK: ((0x6D, 0x64, 0x65), "all"),
           IVY_L: ((0xB4, 0xD0, 0x0A), "vivid"), IVY_G: ((0x71, 0x8A, 0x0F), "vivid"),
           IVY_D: ((0x3A, 0x49, 0x15), "all"), STEM: ((0x8A, 0x5C, 0x2E), "brown"),
           ROPE: ((0xF2, 0xAF, 0x4B), "vivid"), ROPE_DEEP: ((0xCF, 0x8A, 0x2C), "vivid"),
           BANNER: ((0xD6, 0x1B, 0x1F), "vivid"), WHITE: ((0xF8, 0xF0, 0xEC), "all"),
           POLE: ((0x52, 0x36, 0x2F), "all"), IRON: ((0x4E, 0x3C, 0x37), "all"),
           LEATHER: ((0x82, 0x42, 0x1F), "brown"), GOLD: ((0xF0, 0x9D, 0x1A), "vivid"),
           MAT: ((0xCC, 0x8D, 0x38), "vivid"), STRIPE: ((0x47, 0x70, 0x7A), "all")}


def palette():
    for k, (hexcol, rough, metal, emit, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, metal=metal, emit=emit, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, metal=metal, emit=emit, low_spec=low)
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m070_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k == "m070_" + tail), None)
            if k1 in PALETTE and k2 and pct.isdigit():
                K.fk().KIT_PALETTE.pop(key, None)
                K.mix_key(k1, k2, int(pct) / 100)


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS); "all" kinds are sampled with the studio paper dropped. Returns
    {key: (hex, rendered)}."""
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


# ---- small helpers -----------------------------------------------------------------------------------------------------
Z = Vector((0.0, 0.0, 1.0))


def _mix(k1, k2, t, step=0.05):
    t = round(round(max(0.0, min(1.0, t)) / step) * step, 2)
    return K.mix_key(k1, k2, t)


def _paint(a, faces, key):
    mi = a._mi(key)
    for f in faces:
        if f.is_valid:
            f.material_index = mi


def _tint(a, faces, k):
    for f in faces:
        for lp in f.loops:
            t = lp[a.tint_layer][0] * k
            lp[a.tint_layer] = (t, t, t, 1.0)


def _seed(name):
    return sum((i + 1) * ord(c) for i, c in enumerate(name))


def _rt(name, amp):
    return 1.0 + random.Random(_seed(name)).uniform(-amp, amp)


def _texture(a, vs, amp, seed, scale=0.3):
    K.texture(a, vs, amp=amp, scale=scale, jitter=0.0, seed=seed)


def _solid(a, pts, faces, key, tint=1.0):
    """(m048) One closed shell from points and faces all wound one way; flipped as a whole if the signed volume comes
    out negative. Returns (verts, faces)."""
    bm = a.bm
    vs = [bm.verts.new(Vector(p)) for p in pts]
    fs = [bm.faces.new([vs[i] for i in f]) for f in faces]
    for f in fs:
        f.normal_update()
    vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs)
    if vol < 0:
        for f in fs:
            f.normal_flip()
            f.normal_update()
    a._finish(vs, key, tint=tint)
    return vs, fs


def _shell(a, pts, faces, key, tint=1.0):
    """(m051) One closed shell from points and faces of any winding: bmesh makes the winding consistent, then the
    shell is flipped as a whole if its signed volume is negative. Returns (verts, faces)."""
    bm = a.bm
    vs = [bm.verts.new(Vector(p)) for p in pts]
    fs = [bm.faces.new([vs[i] for i in f]) for f in faces]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    for f in fs:
        f.normal_update()
    vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs)
    if vol < 0:
        for f in fs:
            f.normal_flip()
            f.normal_update()
    a._finish(vs, key, tint=tint)
    return vs, fs


HEXA = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (0, 4, 7, 3), (1, 2, 6, 5)]


def _box_pts(lo, hi, m=None):
    pts = [Vector((x, y, z)) for z in (lo[2], hi[2]) for (x, y) in ((lo[0], lo[1]), (hi[0], lo[1]),
                                                                   (hi[0], hi[1]), (lo[0], hi[1]))]
    return [m @ p for p in pts] if m is not None else pts


def _box(a, lo, hi, key, tint=1.0, m=None):
    """Axis box lo..hi (optionally transformed by the 4x4 matrix m). Returns (verts, faces)."""
    return _shell(a, _box_pts(lo, hi, m), HEXA, key, tint)


def _prism(a, rings, key, tint=1.0, caps=(True, True)):
    """A closed prism / loft through rings of n points each. Returns (verts, faces, bands): bands[i] are the faces
    between ring i and i + 1; the caps come last in faces."""
    n = len(rings[0])
    pts = [p for r in rings for p in r]
    faces, bands = [], []
    for i in range(len(rings) - 1):
        bands.append(list(range(len(faces), len(faces) + n)))
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, (i + 1) * n + j1, (i + 1) * n + j])
    if caps[0]:
        faces.append(list(reversed(range(n))))
    if caps[1]:
        faces.append([(len(rings) - 1) * n + j for j in range(n)])
    vs, fs = _shell(a, pts, faces, key, tint)
    return vs, fs, [[fs[k] for k in b] for b in bands]


def _ngon(c, e1, e2, r, n, rot=0.0):
    return [c + (e1 * math.cos(rot + 2 * math.pi * k / n) + e2 * math.sin(rot + 2 * math.pi * k / n)) * r
            for k in range(n)]


def _cyl(a, c, axis, r, h, n, key, tint=1.0, rot=0.0, r_top=None):
    """An n-sided closed prism from c along the unit axis, length h. Returns (verts, faces, bands)."""
    ax = Vector(axis).normalized()
    e1 = ax.orthogonal().normalized()
    e2 = ax.cross(e1)
    c = Vector(c)
    rings = [_ngon(c, e1, e2, r, n, rot), _ngon(c + ax * h, e1, e2, r if r_top is None else r_top, n, rot)]
    return _prism(a, rings, key, tint)


def _tube(a, path, r, sides, closed, key, groove=None, tint=1.0, up=(0, 0, 1), phase=0.0, twist=False):
    """(m048) A low-poly rope tube along `path`: rings of `sides` verts. twist=True: each ring turned half a side and
    joined as an antiprism strip; twist=False: rings aligned. Bends are mitred so the tube keeps its thickness. Open
    tubes get flat end caps. `groove` = {strand: key}: those strands (by their place in the twist) take that key."""
    P = [Vector(p) for p in path]
    N = len(P)
    if closed and twist and N % 2:
        raise ValueError("closed rope path needs an even point count")
    upv = Vector(up)
    rings = []
    for i in range(N):
        prev = P[i - 1] if closed else P[max(i - 1, 0)]
        nxt = P[(i + 1) % N] if closed else P[min(i + 1, N - 1)]
        tin = (P[i] - prev) if (P[i] - prev).length > 1e-9 else (nxt - P[i])
        tout = (nxt - P[i]) if (nxt - P[i]).length > 1e-9 else tin
        tin, tout = tin.normalized(), tout.normalized()
        T = (tin + tout).normalized()
        U = (upv - upv.dot(T) * T).normalized()
        V = T.cross(U)
        B = tout - tin
        bend = B.length > 1e-6
        if bend:
            B.normalize()
        sc = 1.0 / max(0.5, tin.dot(T)) - 1.0
        ring = []
        for k in range(sides):
            ang = phase + 2 * math.pi * (k + (0.5 * i if twist else 0.0)) / sides
            off = (U * math.cos(ang) + V * math.sin(ang)) * r
            if bend:
                off += B * off.dot(B) * sc
            ring.append(P[i] + off)
        rings.append(ring)
    pts = [p for rg in rings for p in rg]
    faces, strand = [], []
    segs = N if closed else N - 1
    for i in range(segs):
        j = (i + 1) % N
        shift = (N // 2) % sides if (twist and closed and j == 0) else 0
        for k in range(sides):
            a0, a1 = i * sides + k, i * sides + (k + 1) % sides
            b0, b1 = j * sides + (k + shift) % sides, j * sides + (k + 1 + shift) % sides
            if twist:
                faces += [[a0, a1, b0], [a1, b1, b0]]
                strand += [k, k]
            else:
                faces += [[a0, a1, b1], [a0, b1, b0]]
                strand += [(k - i) % sides] * 2
    if not closed:
        faces.append(list(reversed(range(sides))))
        faces.append([(N - 1) * sides + k for k in range(sides)])
        strand += [-1, -1]
    vs, fs = _solid(a, pts, faces, key, tint)
    if groove:
        gi = {k: a._mi(v) for k, v in groove.items()}
        for f, s in zip(fs, strand):
            if s in gi:
                f.material_index = gi[s]
    return vs, fs


_PDIRS = (Vector((1.0, 0.0131, 0.0217)).normalized(), Vector((-0.0173, 1.0, 0.0119)).normalized(),
          Vector((0.0151, -0.0191, 1.0)).normalized())


def _parity_in(tree, p):
    """(m047) Ray parity: p is inside the closed shell(s) if at least two of three skewed rays cross an odd number of
    times."""
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


def _newell(pts):
    n = Vector()
    m = len(pts)
    for i in range(m):
        p, q = pts[i], pts[(i + 1) % m]
        n += Vector(((p.y - q.y) * (p.z + q.z), (p.z - q.z) * (p.x + q.x), (p.x - q.x) * (p.y + q.y)))
    return n


def _up_for(path):
    n = _newell(path)
    span = max((p - path[0]).length for p in path)
    if n.length > 1e-3 * max(span, 0.1) ** 2:
        return n.normalized()
    ch = path[-1] - path[0]
    u = ch.cross(Vector((0, 0, 1)))
    if u.length < 1e-4:
        u = ch.cross(Vector((1, 0, 0)))
    return u.normalized()


def _R(c, rot_deg=0.0, z=0.0):
    return Matrix.Translation((c[0], c[1], z)) @ Matrix.Rotation(math.radians(rot_deg), 4, "Z")


# ---- piece register --------------------------------------------------------------------------------------------------
PIECES = []          # (kind, name, centroid in the build frame) per shell, in build order
ROPES = []           # open rope runs: name, end points, radius (both-ends contact check)
GEO = {}             # measured placements (report)
G = {}               # build state: "stone" (BVH of every block in the asset so far), "solids" (posts etc.)
LEAF_INFO = []       # per placed leaf: dict(c, n, size, tone, run, front (face index list into the shell))
DROPPED = []


def _reg(kind, name, vs):
    PIECES.append((kind, name, sum((v.co for v in vs), Vector()) / len(vs)))


def _clear():
    PIECES.clear()
    ROPES.clear()


# ---- ruin blocks (spec 2.2; close-up C) ----------------------------------------------------------------------------
CH = 0.16              # chamfer on the top edges and the vertical edges
J = 0.05               # joint gap between blocks in a course
COURSE = 1.65          # course height
SEAT = 0.015           # an upper block's bottom stands this far above the block under it
DEPTH = 2.4
BACK_Y = (3.0, 5.4)    # back wall inner, outer face
SIDE_X = (-9.6, -7.2)  # side wall outer, inner face
BACK_X = (-9.6, 5.2)
SIDE_Y0 = -4.2
STEP_SPANS = {5: (-7.2, 4.4), 6: (-5.6, 2.6), 7: (-4.0, 1.4)}    # back wall courses above the side wall (spec 2.2)
MISSING = (("S", 4, -0.8),)                                      # (wall, course, run coordinate inside the gap)
# (wall, course, block index) -> [(corner, size)]: corners in block space, -y = the wall's inner face (spec 2.2)
CHIPS = {("B", 7, 0): [("-x-y", 0.40)], ("B", 7, -1): [("+x+y", 0.35)], ("S", 4, 0): [("-x+y", 0.40)],
         ("B", 4, -1): [("+x-y", 0.35)], ("B", 5, 0): [("-x-y", 0.30)], ("B", 6, -1): [("+x-y", 0.30)],
         ("B", 3, 2): [("-x-y", 0.30)]}
CHIP_DIRS = {"+x-y": ((7, 0), 0, (-1, 1)), "-x+y": ((3, 4), 2, (1, -1)), "+x+y": ((1, 2), 1, (-1, -1)),
             "-x-y": ((5, 6), 3, (1, 1))}
BLOCKS = []            # per wall block: wall, course, index, run span, centre, size (report, moss sites)


def block_shell(L, D, H, ch=CH, crease=True, chips=()):
    """(m056 brick_shell) A chamfered block (local: x along L, y along D, base z 0) as points and polygons, 36 tris: an
    octagon section (ch chamfers on the four vertical edges), a top band chamfered to a flat top, square bottom edges.
    crease pushes one bottom corner of each long face in 0.03, so the face folds along its diagonal. chips = [(corner,
    size)] lower those top corners into broken facets. Returns pts, polys, chip vert indices, top polygon index."""
    hl, hd, e = L / 2, D / 2, ch
    oct_ = [(hl, -hd + e), (hl, hd - e), (hl - e, hd), (-hl + e, hd), (-hl, hd - e), (-hl, -hd + e), (-hl + e, -hd),
            (hl - e, -hd)]
    r0 = [Vector((x, y, 0.0)) for x, y in oct_]
    r1 = [Vector((x, y, H - e)) for x, y in oct_]
    top = [Vector((hl - e, -hd + e, H)), Vector((hl - e, hd - e, H)), Vector((-hl + e, hd - e, H)),
           Vector((-hl + e, -hd + e, H))]
    if crease:
        r0[7].y += 0.03
        r0[3].y -= 0.03
    chip_vs = []
    for corner, s in chips:
        ring_i, top_i, inward = CHIP_DIRS[corner]
        for i in ring_i:
            r1[i].z -= s * 0.85
        top[top_i] += Vector((inward[0], inward[1], 0.0)).normalized() * s * 0.55 + Vector((0, 0, -s * 0.45))
        chip_vs += [8 + ring_i[0], 8 + ring_i[1], 16 + top_i]
    pts = r0 + r1 + top
    polys = [list(reversed(range(8)))]
    polys += [[k, (k + 1) % 8, 8 + (k + 1) % 8, 8 + k] for k in range(8)]
    polys += [[8, 9, 17, 16], [9, 10, 17], [10, 11, 18, 17], [11, 12, 18], [12, 13, 19, 18], [13, 14, 19],
              [14, 15, 16, 19], [15, 8, 16], [16, 17, 18, 19]]
    return pts, polys, chip_vs, len(polys) - 1


def _stone_add(pts, polys, name):
    G.setdefault("stone", []).append((list(pts), [list(p) for p in polys], name))
    G.pop("stone_tree", None)


def stone_tree():
    """A BVH of every stone piece placed so far (blocks, rubble, footings), cached."""
    if "stone_tree" not in G:
        cos, polys = [], []
        for pts, pl, _ in G.get("stone", []):
            o = len(cos)
            cos += [Vector(p) for p in pts]
            polys += [[o + i for i in p] for p in pl]
        G["stone_tree"] = BVHTree.FromPolygons(cos, polys) if polys else None
    return G["stone_tree"]


def _stone_piece(a, pts, polys, chip_vs, key, tint, name, kind="block", top_i=None, top_key=None, mottle=0.02,
                 seed=0):
    vs, fs = _shell(a, pts, polys, key, tint)
    if chip_vs:
        cv = {vs[i] for i in chip_vs}
        _paint(a, [f for f in fs if any(v in cv for v in f.verts)], _mix(STONE, STONE_LIGHT, 0.5))
    if top_i is not None and top_key:
        _paint(a, [fs[top_i]], top_key)
    _texture(a, vs, mottle, seed, scale=0.35)
    _stone_add(pts, polys, name)
    _reg(kind, name, vs)
    return vs, fs


def _layout(x0, x1, fixed, rng, lmin=1.8, lmax=2.75, target=2.45, tries=1500):
    """Running bond: cut the span x0..x1 into blocks of about `target` (lmin..lmax) whose joints stand as far as
    possible (up to 0.9) from the `fixed` joints of the course below and the step ends above; then the most even
    lengths. Returns the joint positions (centres of the gaps)."""
    span = x1 - x0
    ns = sorted({n for n in (math.floor(span / target), math.ceil(span / target)) if n >= 1
                 and lmin <= span / n <= lmax} or {max(1, round(span / target))})
    best = None
    for n in ns:
        if n == 1:
            return []
        for _ in range(tries):
            w = [rng.uniform(0.78, 1.22) for _ in range(n)]
            s = sum(w)
            ls = [wi / s * span for wi in w]
            if any(ln < lmin or ln > lmax for ln in ls):
                continue
            cuts, acc = [], x0
            for ln in ls[:-1]:
                acc += ln
                cuts.append(acc)
            score = min([abs(c - f) for c in cuts for f in fixed] or [9.0])
            # offset first (up to 0.7), then fewer blocks, then even lengths
            key = (round(min(score, 0.5), 2), -n, -sum(abs(ln - span / n) for ln in ls))
            if best is None or key > best[0]:
                best = (key, cuts)
    return best[1]


def _courses():
    """(wall, course, run start, run end): the back wall runs along X, the side wall along Y (spec 2.2). The corner
    pier (x -9.6 .. -7.2, y 3.0 .. 5.4) belongs to the back wall on even courses and to the side wall on odd ones."""
    out = []
    for k in range(8):
        if k <= 4:
            span = BACK_X if k % 2 == 0 else (SIDE_X[1] + J, BACK_X[1])
        else:
            span = STEP_SPANS[k]
        out.append(("B", k) + tuple(span))
    for k in range(5):
        out.append(("S", k, SIDE_Y0, BACK_Y[0] - J) if k % 2 == 0 else ("S", k, SIDE_Y0, BACK_Y[1]))
    return out


def _wall_matrix(wall, s, z0):
    """Block space -> build frame: block x along the wall's run, block -y toward the wall's inner face."""
    if wall == "B":
        return Matrix.Translation((s, (BACK_Y[0] + BACK_Y[1]) / 2, z0))
    return Matrix.Translation(((SIDE_X[0] + SIDE_X[1]) / 2, s, z0)) @ Matrix.Rotation(math.pi / 2, 4, "Z")


def course_tone(k):
    """By position (spec 5.3, 5.5): the foot courses blend toward stone_dark in three steps (grime), the rest stone."""
    return {0: _mix(STONE, STONE_DARK, 0.30), 1: _mix(STONE, STONE_DARK, 0.15), 2: _mix(STONE, STONE_DARK, 0.05)}.get(
        k, STONE)


def walls(a):
    """The L of ruin masonry: 59-ish chamfered 2.4-deep blocks in running bond (joints 0.05, seats 0.015), the stepped
    skyline of spec 2.2, chips by role, the side wall's missing top block; a little hand-laid jitter (run 0.01, depth
    0.02, yaw 0.5 deg); per-block Tint 0.05 and broad mottling."""
    rng = random.Random(7010)
    BLOCKS.clear()
    joints = {}
    courses = _courses()
    for wall, k, s0, s1 in courses:
        fixed = list(joints.get((wall, k - 1), []))
        if wall == "B":
            if (k - 1) % 2 == 1 and k - 1 <= 4:
                fixed.append(SIDE_X[1] + J / 2)                    # the corner joint of the course below
            nxt = STEP_SPANS.get(k + 1)
            if nxt:
                fixed += [x for x in nxt if s0 + 0.3 < x < s1 - 0.3]
                if nxt[1] - nxt[0] <= 2 * 2.75:            # two blocks above: their joint is forced near the middle
                    fixed.append((nxt[0] + nxt[1]) / 2)
        else:
            if (k - 1) % 2 == 0 and k >= 1:
                fixed.append(BACK_Y[0] - J / 2)
        cuts = _layout(s0, s1, fixed, rng)
        joints[(wall, k)] = cuts + ([SIDE_X[1] + J / 2] if wall == "B" and k <= 4 and k % 2 == 1 else [])
        edges = [s0] + cuts + [s1]
        n = len(edges) - 1
        z0 = 0.0 if k == 0 else COURSE * k + SEAT
        H = COURSE * (k + 1) - z0
        for i in range(n):
            a0 = edges[i] + (J / 2 if i else 0.0)
            a1 = edges[i + 1] - (J / 2 if i < n - 1 else 0.0)
            if any(w_ == wall and k_ == k and a0 <= s_ <= a1 for w_, k_, s_ in MISSING):
                continue
            L = a1 - a0
            chips = CHIPS.get((wall, k, i)) or CHIPS.get((wall, k, i - n)) or []
            pts, polys, chip_vs, top_i = block_shell(L, DEPTH, H, crease=True, chips=chips)
            if rng.random() < 0.5 and not chips:          # the crease's far half alternates per block
                for p in pts:
                    p.x = -p.x
                for poly in polys:
                    poly.reverse()
            sc = (a0 + a1) / 2 + rng.uniform(-0.01, 0.01)
            m = _wall_matrix(wall, sc, z0) @ Matrix.Translation((0.0, rng.uniform(-0.02, 0.02), 0.0)) @ \
                Matrix.Rotation(math.radians(rng.uniform(-0.5, 0.5)), 4, "Z")
            pts = [m @ p for p in pts]
            name = f"{wall}{k}_{i}"
            _stone_piece(a, pts, polys, chip_vs, course_tone(k), 1.0 + rng.uniform(-0.05, 0.05), name,
                         seed=_seed(name))
            BLOCKS.append({"wall": wall, "k": k, "i": i, "run": [round(a0, 3), round(a1, 3)], "z": [round(z0, 3),
                           round(z0 + H, 3)], "L": round(L, 3), "chips": chips})
    GEO["blocks"] = len(BLOCKS)
    GEO["joint_offsets_min"] = _bond_report(joints)


def _bond_report(joints):
    """The smallest offset between a course's joints and the joints of the course below (running bond: >= 0.5)."""
    worst = 9.0
    for (wall, k), js in joints.items():
        below = joints.get((wall, k - 1), [])
        for j in js:
            for b in below:
                worst = min(worst, abs(j - b))
    return round(worst, 3)


# ---- rubble, fallen block, footings (spec 2.2, 2.3, 2.8) ------------------------------------------------------------
RUBBLE = (  # centre, (L, D, H), yaw, chips, seed
    ((-8.6, -5.6), (1.6, 1.4, 1.2), 15.0, [("+x+y", 0.35)], 7001),
    ((-6.8, -6.2), (1.2, 1.2, 1.0), 30.0, [("-x-y", 0.30)], 7002),
    ((-0.9, -7.0), (1.5, 1.4, 1.3), 8.0, [("+x-y", 0.40), ("-x+y", 0.30)], 7003),
    ((3.2, -6.6), (1.2, 1.1, 0.9), -20.0, [("-x-y", 0.30)], 7004),
    ((8.4, -5.6), (1.0, 1.0, 0.8), 25.0, [("+x+y", 0.25)], 7005),
)
# a broken half block lying along the wall (its long side along Y), tilted 12 deg about its long axis: its outer
# extreme at about x -10.9, the front cell's left extreme (-10.5, spec 1.1) without the fern
FALLEN = {"c": (-10.6, -0.8), "size": (1.6, 1.0, 1.2), "tilt": 12.0, "gap": 0.20,
          "chips": [("+x+y", 0.35), ("-x-y", 0.30)]}
FOOT_H = 0.60
FOOTINGS = {"FL": ((-5.90, -3.90), 1.40, []), "B": ((-1.00, 2.25), 1.20, []), "FR": ((5.90, -4.60), 1.40,
                                                                                   [("+x-y", 0.22)])}


def rubble(a, c, size, yaw, chips, seed, name):
    """A loose chamfered block (spec 2.8): flat bottom, one or two broken corners (stone_light: the freshly broken
    faces, by role). The rest one stone tone: a paler top would follow the face direction (K.check)."""
    L, D, H = size
    pts, polys, chip_vs, top_i = block_shell(L, D, H, ch=0.12, crease=False, chips=chips)
    m = _R(c, yaw)
    pts = [m @ p for p in pts]
    return _stone_piece(a, pts, polys, chip_vs, _mix(STONE, STONE_DARK, 0.10), _rt(name, 0.05), name, "rubble",
                        seed=seed)


def fallen_block(a, name="fallen"):
    """The broken half block lying tilted 12 deg on its edge outside the side wall (spec 2.2): two chipped corners,
    its high side 0.20 off the wall's outer face, its low edge on the ground."""
    L, D, H = FALLEN["size"]
    pts, polys, chip_vs, top_i = block_shell(L, D, H, ch=0.12, crease=False, chips=FALLEN["chips"])
    m = Matrix.Rotation(math.radians(-FALLEN["tilt"]), 4, "Y") @ Matrix.Rotation(math.radians(96.0), 4, "Z")
    pts = [m @ p for p in pts]
    dz = -min(p.z for p in pts) - 0.004
    dx = SIDE_X[0] - FALLEN["gap"] - max(p.x for p in pts)
    dy = FALLEN["c"][1]
    pts = [p + Vector((dx, dy, dz)) for p in pts]
    GEO["fallen_gap"] = round(SIDE_X[0] - max(p.x for p in pts), 3)
    return _stone_piece(a, pts, polys, chip_vs, _mix(STONE, STONE_DARK, 0.10), _rt(name, 0.05), name, "rubble",
                        seed=7009)


def footing(a, tag, at=None):
    """A pale chamfered footing block (1.40 square, 0.60 tall; the back post's 1.20) under a post."""
    (x, y), w, chips = FOOTINGS[tag]
    if at is not None:
        x, y = at
    pts, polys, chip_vs, top_i = block_shell(w, w, FOOT_H, ch=0.10, crease=False, chips=chips)
    pts = [p + Vector((x, y, 0.0)) for p in pts]
    name = f"footing_{tag}"
    return _stone_piece(a, pts, polys, chip_vs, _mix(STONE, STONE_LIGHT, 0.15), _rt(name, 0.04), name, "footing",
                        seed=_seed(name))


# ---- moss patches (spec 2.7) -----------------------------------------------------------------------------------------
MOSS_SITES = (  # (x, y), radius, height, seed: exposed block tops clear of the ivy pads (spec 2.7)
    ((-3.40, 4.70), 0.58, 0.22, 7101), ((0.50, 3.85), 0.55, 0.20, 7102),
    ((-4.80, 4.50), 0.50, 0.18, 7103), ((2.00, 4.60), 0.50, 0.20, 7104),
    ((-6.60, 4.80), 0.45, 0.18, 7105), ((3.10, 3.60), 0.45, 0.18, 7106),
    ((-8.60, 4.40), 0.60, 0.22, 7107), ((-8.40, 1.60), 0.55, 0.20, 7108),
    ((-8.60, -5.60), 0.45, 0.16, 7109),
)
MOSS_N = 7


def moss(a, xy, r, h, seed, name, tree=None):
    """A flat lumpy moss patch (H : W <= 0.2, never a ball) draped on a block top: a lobed base ring (7 points,
    alternately full and 0.82 r) each sunk 0.02 into the stone under it, a shoulder ring turned half a step at 0.6 h
    and 0.72 r, a crown point; the radius shrunk until the whole rim stays on the same top (within 0.15 of the centre
    height, so it never hangs over an edge). Colour by height: lime crown, green shoulder, dark base. 26 tris."""
    tree = tree or stone_tree()
    rng = random.Random(seed)
    down = Vector((0, 0, -1))

    def hz(x, y):
        q = tree.ray_cast(Vector((x, y, 40.0)), down, 80.0)
        return q[0].z if q[0] is not None else None
    z = hz(*xy)
    if z is None:
        return None
    ph = rng.uniform(0, 2 * math.pi)
    n = MOSS_N
    fr = [rng.uniform(0.94, 1.0) if k % 2 == 0 else rng.uniform(0.62, 0.80) for k in range(n)]
    fm = [rng.uniform(0.60, 0.76) for _ in range(n)]
    hm = [rng.uniform(0.50, 0.72) for _ in range(n)]
    sq, rot = rng.uniform(0.55, 0.75), rng.uniform(0, math.pi)       # an irregular, longish patch (never a coin)

    def at(t, rr):
        u, v = math.cos(t) * rr, math.sin(t) * rr * sq
        return (xy[0] + u * math.cos(rot) - v * math.sin(rot), xy[1] + u * math.sin(rot) + v * math.cos(rot))
    for _ in range(14):
        base = [at(ph + 2 * math.pi * k / n, r * fr[k]) for k in range(n)]
        zs = [hz(x, y) for x, y in base]
        if all(q is not None and abs(q - z) <= 0.06 for q in zs):
            break
        r *= 0.9
    h = min(h, 0.4 * r)
    pts = [Vector((x, y, q - 0.015)) for (x, y), q in zip(base, zs)]
    for k in range(n):
        x, y = at(ph + 2 * math.pi * (k + 0.5) / n, r * fm[k])
        pts.append(Vector((x, y, (hz(x, y) or z) + h * hm[k])))
    pts.append(Vector((xy[0] + rng.uniform(-0.1, 0.1) * r, xy[1] + rng.uniform(-0.1, 0.1) * r, z + h)))
    polys = [list(reversed(range(n)))]
    for k in range(n):
        k1 = (k + 1) % n
        polys.append([k, k1, n + k])
        polys.append([k1, n + k1, n + k])
    for k in range(n):
        polys.append([n + k, n + (k + 1) % n, 2 * n])
    vs, fs = _shell(a, pts, polys, IVY_G, _rt(name, 0.03))
    _paint(a, fs[1:1 + 2 * n], IVY_G)
    _paint(a, fs[1 + 2 * n:], _mix(IVY_G, IVY_L, 0.4))
    _paint(a, fs[:1], IVY_D)
    _reg("moss", name, vs)
    GEO.setdefault("moss", []).append({"name": name, "r": round(r, 3), "h": round(h, 3), "z": round(z, 3)})
    return vs


# ---- rope (twisted tubes, spec 2.5) ----------------------------------------------------------------------------------
# corner radii: turns round square timber are 5-sided tubes with spiral strands (4-sided ones read as flat straps);
# diagonals and tails are twisted 4-sided tubes
RT_L, RT_LF, RT_C, RT_B, RT_T = 0.13, 0.15, 0.13, 0.10, 0.06   # lashing turn, FR turn, collar, back band, tail
RD_L, RD_LF = 0.12, 0.14                                       # lashing diagonals
SINK = 0.02                                                    # rope sunk into what it hugs
TURN_SIDES = 5


def _turn_ext(sides=TURN_SIDES):
    """A turn's cross-section extents as fractions of its radius (rope() turns rings by pi / sides, U up, V out of
    the loop): (inward, downward, upward)."""
    th = [math.pi / sides + 2 * math.pi * k / sides for k in range(sides)]
    return max(-math.sin(t) for t in th), max(-math.cos(t) for t in th), max(math.cos(t) for t in th)


TURN_IN, TURN_DN, TURN_UP = _turn_ext()
FLAT4 = TURN_IN          # (the name the turn offsets use)


def _groove(sides):
    return {0: ROPE_DEEP} if sides >= 4 else {0: _mix(ROPE, ROPE_DEEP, 0.5)}


def rope(a, path, rt, sides, closed, name, up=None, kind="rope", twist=True):
    """(m066) A rope piece. twist=True: an antiprism twisted tube (diagonals, tails); twist=False: rings aligned with
    spiral strands (the turns round square timber); one strand in four rope_deep."""
    path = [Vector(p) for p in path]
    up = up if up is not None else _up_for(path)
    groove = _groove(sides) if twist else {0: ROPE_DEEP}
    vs, fs = _tube(a, path, rt, sides, closed, ROPE, groove=groove, tint=_rt(name, 0.03), up=tuple(up),
                   twist=twist, phase=0.0 if twist else math.pi / sides)
    _reg(kind, name, vs)
    if not closed:
        ROPES.append({"name": name, "ends": [list(path[0]), list(path[-1])], "rt": rt})
    return vs


def rect_loop(lo, hi, z, off):
    """Four points round the axis rectangle lo..hi (x, y) at height z, every side `off` outside (a mitred square)."""
    return [Vector((lo[0] - off, lo[1] - off, z)), Vector((hi[0] + off, lo[1] - off, z)),
            Vector((hi[0] + off, hi[1] + off, z)), Vector((lo[0] - off, hi[1] + off, z))]


# ---- posts, toggles, crossbeam (spec 2.3, 2.4) -----------------------------------------------------------------------
POSTS = {"FL": (-5.90, -3.90, 9.35, 0.43), "B": (-1.00, 2.25, 11.10, 0.40), "FR": (5.90, -4.60, 12.00, 0.55)}
PCH = 0.05
POST_Z0 = FOOT_H + 0.003
# canvas tie height (mid-surface) and the post face the toggle stands on (spec 2.4)
TIES = {"FL": (8.00, (1.0, 0.0)), "B": (9.90, (0.0, -1.0)), "FR": (9.20, (-1.0, 0.0))}
TOG_W, TOG_L = 0.32, 0.55
TAB_G, TAB_T, TAB_S = 0.004, 0.05, 0.30          # tab gap off the toggle, thickness, length along the toggle
CT = 0.10                                        # canvas thickness
CORNER_IN = -(TAB_G + TAB_T)                     # the canvas corner at the tab's outer end (the sheet leaves from it)
TIE_LIFT = TAB_G + TAB_T + 0.008 + CT / 2        # toggle top -> canvas mid-surface at the corner
BEAM = {"x": (-9.10, None), "y": (-4.20, -3.60), "z": (8.255, 8.855)}


def _oct(h, ch):
    return [(h - ch, -h), (h, -h + ch), (h, h - ch), (h - ch, h), (-h + ch, h), (-h, h - ch), (-h, -h + ch),
            (-h + ch, -h)]


def post(a, tag, at=None):
    """A chamfered square post (spec 2.3) standing 0.003 over its footing's flat top: an 8-sided prism with rings at
    0.2 / 0.4 of its height, the lowest bands blended toward timber_deep by height (spec 3.12: 50 %, 25 %, then the
    timber), a square-cut top in timber_end. 60 tris."""
    px, py, top, h = POSTS[tag]
    if at is not None:
        px, py = at
    H = top - POST_Z0
    zs = (POST_Z0, POST_Z0 + 0.20 * H, POST_Z0 + 0.40 * H, top)
    rings = [[Vector((px + x, py + y, z)) for x, y in _oct(h, PCH)] for z in zs]
    nm = f"post_{tag}"
    vs, fs, bands = _prism(a, rings, TIMBER, _rt(nm, 0.04))
    for b, t in zip(bands, (0.50, 0.25)):
        _paint(a, b, _mix(TIMBER, TIMBER_DEEP, t))
    _paint(a, [fs[-1]], TIMBER_END)
    _texture(a, vs, 0.03, _seed(nm), scale=0.45)
    _reg("post", nm, vs)
    return vs


def toggle_frame(tag, at=None):
    """The toggle's frame: post centre c, face normal n (horizontal), across unit u, face distance, top z."""
    px, py, _, h = POSTS[tag]
    if at is not None:
        px, py = at
    tz, f = TIES[tag]
    n = Vector((f[0], f[1], 0.0))
    u = Vector((-n.y, n.x, 0.0))
    return {"c": Vector((px, py, 0.0)), "n": n, "u": u, "s0": h + 0.003, "s1": h + 0.003 + TOG_L,
            "zt": tz - TIE_LIFT, "zb": tz - TIE_LIFT - TOG_W}


def toggle(a, tag, at=None):
    """A 0.32 square wooden toggle 0.55 long standing out of the post's inner face under the lashing (close-up A),
    0.003 off the face; its outer end in timber_end. Returns its frame."""
    T = toggle_frame(tag, at)
    c, n, u = T["c"], T["n"], T["u"]
    pts = []
    for z in (T["zb"], T["zt"]):
        for s, w in ((T["s0"], -TOG_W / 2), (T["s1"], -TOG_W / 2), (T["s1"], TOG_W / 2), (T["s0"], TOG_W / 2)):
            pts.append(c + n * s + u * w + Vector((0, 0, z)))
    nm = f"toggle_{tag}"
    vs, fs = _shell(a, pts, HEXA, TIMBER, _rt(nm, 0.05))
    _paint(a, [fs[5]], TIMBER_END)
    _reg("toggle", nm, vs)
    return T


def corner_tab(a, T, tag):
    """The canvas corner gathered round the toggle's outer end (spec 2.4): a U-shaped 0.05 canvas fold over the
    toggle's top, end and bottom, 0.004 off it, along its last 0.30. 28 tris. Returns the top of its upper leaf."""
    c, n, u = T["c"], T["n"], T["u"]
    s1 = T["s1"] - TAB_S
    se = T["s1"] + TAB_G
    zt, zb = T["zt"] + TAB_G, T["zb"] - TAB_G
    prof = [(s1, zt), (se, zt), (se, zb), (s1, zb), (s1, zb - TAB_T), (se + TAB_T, zb - TAB_T), (se + TAB_T, zt + TAB_T),
            (s1, zt + TAB_T)]
    w = TOG_W / 2 + TAB_G
    pts = [c + n * s + u * (-w) + Vector((0, 0, z)) for s, z in prof] + \
          [c + n * s + u * w + Vector((0, 0, z)) for s, z in prof]
    caps = [(0, 1, 6), (0, 6, 7), (1, 2, 5), (1, 5, 6), (2, 3, 4), (2, 4, 5)]
    faces = [list(t) for t in caps] + [[8 + t[2], 8 + t[1], 8 + t[0]] for t in caps]
    for i in range(8):
        i1 = (i + 1) % 8
        faces.append([i, i1, 8 + i1, 8 + i])
    nm = f"tab_{tag}"
    vs, fs = _shell(a, pts, faces, _mix(CANVAS, CANVAS_DEEP, 0.40), _rt(nm, 0.02))
    _reg("tab", nm, vs)
    return zt + TAB_T


def crossbeam(a):
    """The 0.60 square crossbeam (spec 2.3) from the front-left post's -X face onto the side wall's front-end top
    block, 0.005 off both; pale cut ends."""
    px, py, _, h = POSTS["FL"]
    lo = (BEAM["x"][0], BEAM["y"][0], BEAM["z"][0])
    hi = (px - h - 0.005, BEAM["y"][1], BEAM["z"][1])
    vs, fs = _box(a, lo, hi, TIMBER, _rt("beam", 0.04))
    _paint(a, [fs[4], fs[5]], TIMBER_END)
    _texture(a, vs, 0.03, 7020, scale=0.6)
    _reg("beam", "beam", vs)
    return lo, hi


# ---- lashings, collars (spec 2.5; close-ups A, B) ------------------------------------------------------------------
X_LIFT = 0.20


def lash_heights(tag):
    """(lower turn, upper turn) z: the lower turn's bottom flat 0.01 into the toggle's top; the upper turn above the
    crossbeam (FL), 0.55 up (back post) or high over the crossarm (FR)."""
    T = toggle_frame(tag)
    rt = RT_LF if tag == "FR" else RT_L
    lo = T["zt"] + rt * TURN_DN - 0.01
    if tag == "FL":
        hi = BEAM["z"][1] + rt * TURN_DN + 0.005
    elif tag == "FR":
        hi = 10.35
    else:
        hi = lo + 0.75
    return lo, hi


def post_turn(a, tag, z, name, rt, at=None):
    """A horizontal turn round the post: a 4-sided tube whose inner flat is sunk SINK into the post faces."""
    px, py, _, h = POSTS[tag]
    if at is not None:
        px, py = at
    path = rect_loop((px - h, py - h), (px + h, py + h), z, rt * FLAT4 - SINK)
    rope(a, path, rt, TURN_SIDES, True, name, up=Z, twist=False)
    return path


def lashing(a, tag, xface, over=None, at=None):
    """An X-lashing (close-up A): two turns round the post (the lower one sitting on the toggle) and two diagonals
    crossing on the post's `xface` (unit (x, y)), the second lifted X_LIFT at the crossing. over = (face distance from
    the post centre, top z, bottom z) of a timber lying on that face (the FR crossarm): the diagonals round its top
    and bottom edges. Each diagonal starts and ends just inside its turn. Returns the turn heights."""
    px, py, _, h = POSTS[tag]
    if at is not None:
        px, py = at
    rt = RT_LF if tag == "FR" else RT_L
    rd = RD_LF if tag == "FR" else RD_L
    z_lo, z_hi = lash_heights(tag)
    post_turn(a, tag, z_lo, f"lash_{tag}_lo", rt, at)
    post_turn(a, tag, z_hi, f"lash_{tag}_hi", rt, at)
    n = Vector((xface[0], xface[1], 0.0))
    ax = Vector((-n.y, n.x, 0.0))
    c = Vector((px, py, 0.0))
    dt = h + rt * FLAT4 - SINK            # the turns' centreline off the post centre
    d0 = h + 0.8 * rd - SINK              # the diagonals' centreline on the post face
    xh = h - 0.10
    for k, sg in enumerate((1, -1)):
        S = c + n * dt + ax * (-sg * xh)
        S.z = z_hi
        E = c + n * dt + ax * (sg * xh)
        E.z = z_lo
        lift = X_LIFT if k else 0.0
        if over:
            fd, top, bot = over
            off = 0.8 * rd - SINK
            B1 = c + n * (fd + off) + ax * (-sg * 0.18)
            B1.z = top + off
            B2 = c + n * (fd + off) + ax * (sg * 0.18)
            B2.z = bot - off
            mid = c + n * (fd + off + lift)
            mid.z = (top + bot) / 2
            inner = [B1, mid, B2] if k else [B1, B2]
        else:
            mid = c + n * (d0 + lift)
            mid.z = (z_lo + z_hi) / 2
            inner = [mid]
        S0 = S + (inner[0] - S).normalized() * (1.4 * rt * FLAT4)
        E0 = E + (inner[-1] - E).normalized() * (1.4 * rt * FLAT4)
        rope(a, [S0] + inner + [E0], rd, 4, False, f"lash_{tag}_x{k}", up=n)
    GEO.setdefault("lashings", {})[tag] = [round(z_lo, 3), round(z_hi, 3)]
    return z_lo, z_hi


def beam_wrap(a):
    """A turn round the crossbeam next to the front-left post (the lashing binds both)."""
    x = POSTS["FL"][0] - POSTS["FL"][3] - 0.32
    y0, y1 = BEAM["y"]
    z0, z1 = BEAM["z"]
    o = RT_L * FLAT4 - SINK
    path = [Vector((x, y0 - o, z0 - o)), Vector((x, y1 + o, z0 - o)), Vector((x, y1 + o, z1 + o)),
            Vector((x, y0 - o, z1 + o))]
    rope(a, path, RT_L, TURN_SIDES, True, "beam_wrap", up=Vector((1, 0, 0)), twist=False)


COLLARS = {"FR": (4.60, 4.60 + (TURN_UP + TURN_DN) * RT_C + 0.004, POST_Z0 + TURN_DN * RT_C - 0.01),
           "FL": (POST_Z0 + TURN_DN * RT_C - 0.01,)}
BAND_Z = 3.55


def collars(a, tag, at=None):
    """Golden collar turns (spec 2.5): FR two at mid-height and one at the foot, FL one at the foot; the back post a
    thinner band under the canvas."""
    if tag == "B":
        post_turn(a, tag, BAND_Z, "band_B", RT_B, at)
        return
    for i, z in enumerate(COLLARS[tag]):
        post_turn(a, tag, z, f"collar_{tag}_{i}", RT_C, at)


# ---- canvas (spec 2.4) ------------------------------------------------------------------------------------------------
NU, NV = 5, 5
HEM = 0.35
SAG_FRONT, SAG_BACK, SAG_CENTRE = 0.28, 0.50, 0.75
C4 = Vector((1.40, -5.40, 6.60))


def canvas_corners(at=None):
    """Corner points of the canvas's TOP surface: C1-C3 over their toggles' outer ends (resting on the tabs), C4 the
    free front corner (mid-surface 6.6)."""
    out = {}
    for key, tag in (("C1", "FL"), ("C2", "B"), ("C3", "FR")):
        T = toggle_frame(tag, (at or {}).get(tag))
        p = T["c"] + T["n"] * (T["s1"] - CORNER_IN)
        p.z = T["zt"] + TIE_LIFT + CT / 2
        out[key] = p
    out["C4"] = C4 + Vector((0, 0, CT / 2))
    return out


def canvas_top(u, v, C):
    """u along C1 -> C4 (the front-left edge), v along C1 -> C2 (the back-left edge); sag 0.20 at the front edges'
    middles, 0.45 at the back edges', 0.60 at the centre."""
    p = C["C1"] * (1 - u) * (1 - v) + C["C4"] * u * (1 - v) + C["C2"] * (1 - u) * v + C["C3"] * u * v
    bu, bv = 4 * u * (1 - u), 4 * v * (1 - v)
    e = SAG_CENTRE - 0.5 * (SAG_FRONT + SAG_BACK) * 2
    p.z -= (1 - v) * SAG_FRONT * bu + v * SAG_BACK * bu + (1 - u) * SAG_BACK * bv + u * SAG_FRONT * bv + e * bu * bv
    return p


def _canvas_tris():
    tris = []
    ci, cj = (NU - 1) / 2, (NV - 1) / 2
    for i in range(NU - 1):
        for j in range(NV - 1):
            a_, b_, c_, d_ = (i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)
            if (i + 0.5 < ci) == (j + 0.5 < cj):
                tris += [(a_, b_, c_), (a_, c_, d_)]
            else:
                tris += [(a_, b_, d_), (b_, c_, d_)]
    return tris


def canvas_sheet(a, C=None, name="canvas"):
    """(m066) The canvas: one closed 0.10 slab. A 6 x 6 top grid inset HEM from the edges, each quad split along the
    diagonal pointing at the grid centre (the X of creases), a hem strip to the true edge, the underside CT below
    along the vertex normals, rim faces round the edge. Hem colour by distance from the edge, three steps toward
    canvas_deep (rim 75 %, hem strip 50 %, the inner grid's border facets 20 %). Returns (verts, top grid)."""
    C = C or canvas_corners()
    du = HEM / (C["C4"] - C["C1"]).length
    dv = HEM / (C["C2"] - C["C1"]).length
    T = {(i, j): canvas_top(du + (1 - 2 * du) * i / (NU - 1), dv + (1 - 2 * dv) * j / (NV - 1), C)
         for i in range(NU) for j in range(NV)}
    loop = ([(i, 0) for i in range(NU)] + [(NU - 1, j) for j in range(1, NV)] +
            [(i, NV - 1) for i in range(NU - 2, -1, -1)] + [(0, j) for j in range(NV - 2, 0, -1)])
    O = {("o", k): canvas_top(k[0] / (NU - 1), k[1] / (NV - 1), C) for k in loop}
    P = dict(T)
    P.update(O)
    tris = [(t, CANVAS) for t in _canvas_tris()]
    ring = {(i, j) for i in range(NU) for j in range(NV) if i in (0, NU - 1) or j in (0, NV - 1)}
    tris = [(t, _mix(CANVAS, CANVAS_DEEP, 0.20) if sum(1 for k in t if k in ring) == 3 else key) for t, key in tris]
    hem = _mix(CANVAS, CANVAS_DEEP, 0.50)
    for k in range(len(loop)):
        a0, a1 = ("o", loop[k]), ("o", loop[(k + 1) % len(loop)])
        b0, b1 = loop[k], loop[(k + 1) % len(loop)]
        if (P[a0] - P[b1]).length <= (P[a1] - P[b0]).length:
            tris += [((a0, a1, b1), hem), ((a0, b1, b0), hem)]
        else:
            tris += [((a0, a1, b0), hem), ((a1, b1, b0), hem)]
    nrm = {k: Vector() for k in P}
    for t, _ in tris:
        p0, p1, p2 = (P[k] for k in t)
        n = (p1 - p0).cross(p2 - p0)
        if n.z < 0:
            n = -n
        for k in t:
            nrm[k] += n
    keys = list(P)
    idx = {k: i for i, k in enumerate(keys)}
    # the underside straight down at the tied corners (they rest flat on their tabs), along the normal elsewhere
    corner_keys = {("o", (0, 0)), ("o", (NU - 1, 0)), ("o", (0, NV - 1)), ("o", (NU - 1, NV - 1))}
    under = []
    for k in keys:
        nn = nrm[k].normalized()
        under.append(P[k] - (Vector((0, 0, CT)) if k in corner_keys else nn * (CT / max(nn.z, 0.5))))
    pts = [P[k] for k in keys] + under
    nb = len(keys)
    faces, fkeys = [], []
    for t, key in tris:
        faces.append([idx[k] for k in t])
        fkeys.append(key)
        faces.append([nb + idx[k] for k in reversed(t)])
        fkeys.append(key)
    for k in range(len(loop)):
        u_, v_ = ("o", loop[k]), ("o", loop[(k + 1) % len(loop)])
        faces.append([idx[u_], idx[v_], nb + idx[v_], nb + idx[u_]])
        fkeys.append(_mix(CANVAS, CANVAS_DEEP, 0.75))
    vs, fs = _shell(a, pts, faces, CANVAS, _rt(name, 0.02))
    for f, k in zip(fs, fkeys):
        if k != CANVAS:
            f.material_index = a._mi(k)
    _texture(a, vs, 0.03, 7030, scale=0.18)
    _reg("canvas", name, vs)
    GEO["canvas_low_top"] = round(min(p.z for p in P.values()), 3)
    GEO["canvas_low_under"] = round(min(p.z for p in under), 3)
    GEO["canvas_centre_top"] = round(T[((NU - 1) // 2, (NV - 1) // 2)].z, 3)
    GEO["canvas_corners_mid"] = {k: [round(x, 3) for x in (p - Vector((0, 0, CT / 2)))] for k, p in C.items()}
    return vs, T


def c4_tail(a, C=None):
    """The free corner's short rope tail (0.45, twisted, its top sunk 0.03 into the corner) and the small square
    toggle dangling from it (spec 2.4)."""
    C = C or canvas_corners()
    q = canvas_top(0.96, 0.04, C)                  # just inside the corner, so the rope's top ring is under the sheet
    b = q - Vector((0, 0, CT * 1.08))
    p0 = b + Vector((0, 0, 0.02))
    p1 = b + Vector((0.03, -0.02, -0.22))
    p2 = b + Vector((0.05, -0.04, -0.45))
    rope(a, [p0, p1, p2], RT_T, 4, False, "c4_tail", up=Vector((0, -1, 0)))
    zt = p2.z + 0.03
    lo = (p2.x - 0.10, p2.y - 0.10, zt - 0.34)
    hi = (p2.x + 0.10, p2.y + 0.10, zt)
    vs, fs = _box(a, lo, hi, TIMBER, _rt("c4_toggle", 0.04))
    _reg("toggle", "toggle_C4", vs)
    GEO["c4_tail_bottom"] = round(lo[2], 3)


# ---- banner, crossarm, dark pole (spec 2.6) ----------------------------------------------------------------------------
ARM_R = 0.225                                   # crossarm flat radius (8-sided, flats on the axes)
ARM_Z = 9.60
ARM_X = (5.25, 9.30)
ARM_Y = POSTS["FR"][1] - POSTS["FR"][3] - ARM_R - 0.005      # resting 0.005 off the FR post's front face
KNOB_R, KNOB_L = 0.30, 0.25
POLE_R, POLE_X, POLE_TOP = 0.25, 6.94, 9.75
SLEEVE_X = (6.72, 7.15)
SLEEVE_R = 0.36
POLE_Y = ARM_Y + SLEEVE_R / math.cos(math.pi / 6) + POLE_R - 0.03   # its front flat 0.03 into the sleeve's back ridge
BAN_X = (7.20, 9.25)
BAN_T, BAN_TIP, BAN_NOTCH, BAN_HEM = 0.08, 3.00, 3.80, 0.45
HEM_RI, HEM_RO = 0.25, 0.32                     # the banner's top hem: 6-sided sleeve round the arm (flat radii)
C8 = math.cos(math.pi / 8)
C6 = math.cos(math.pi / 6)


def _flat_rot(n):
    """The ring turn that puts a flat at the bottom (and on the axes for n = 8)."""
    return math.pi / n if n % 4 == 0 else 0.0


def _oct_rings_x(x0, x1, y, z, r_flat, n=8):
    """n-gon rings across X (flats on the Y and Z axes) of flat radius r_flat."""
    rv = r_flat / math.cos(math.pi / n)
    e1, e2 = Vector((0, 1, 0)), Vector((0, 0, 1))
    return [_ngon(Vector((x, y, z)), e1, e2, rv, n, _flat_rot(n)) for x in (x0, x1)]


def crossarm(a, x0=ARM_X[0], x1=ARM_X[1], y=ARM_Y, z=ARM_Z):
    """The round (8-sided) crossarm in front of the FR post, through its lashing, with an end knob (pale cut faces)."""
    vs, fs, _ = _prism(a, _oct_rings_x(x0, x1, y, z, ARM_R), TIMBER, _rt("arm", 0.04))
    _paint(a, fs[-2:], TIMBER_END)
    _texture(a, vs, 0.03, 7040, scale=0.6)
    _reg("arm", "crossarm", vs)
    vs, fs, _ = _prism(a, _oct_rings_x(x1 + 0.003, x1 + 0.003 + KNOB_L, y, z, KNOB_R), TIMBER, _rt("knob", 0.04))
    _paint(a, fs[-1:], TIMBER_END)
    _reg("arm", "knob", vs)


def _annulus_x(x0, x1, y, z, ri, ro, n):
    """A closed annular sleeve across X (n-gon rings, flats on the axes): outer, inner and the two end rings."""
    ra, rb = ri / math.cos(math.pi / n), ro / math.cos(math.pi / n)
    e1, e2 = Vector((0, 1, 0)), Vector((0, 0, 1))
    rot = _flat_rot(n)
    o0 = _ngon(Vector((x0, y, z)), e1, e2, rb, n, rot)
    o1 = _ngon(Vector((x1, y, z)), e1, e2, rb, n, rot)
    i0 = _ngon(Vector((x0, y, z)), e1, e2, ra, n, rot)
    i1 = _ngon(Vector((x1, y, z)), e1, e2, ra, n, rot)
    pts = o0 + o1 + i0 + i1
    faces = []
    for j in range(n):
        j1 = (j + 1) % n
        faces.append([j, j1, n + j1, n + j])
        faces.append([2 * n + j1, 2 * n + j, 3 * n + j, 3 * n + j1])
        faces.append([j1, j, 2 * n + j, 2 * n + j1])
        faces.append([n + j, n + j1, 3 * n + j1, 3 * n + j])
    return pts, faces


def pole(a, x=POLE_X, y=POLE_Y):
    """The dark pole (8-sided, 0.50) from the ground to inside the iron sleeve, and the sleeve round the crossarm."""
    rv = POLE_R / C8
    rings = [_ngon(Vector((x, y, z)), Vector((1, 0, 0)), Vector((0, 1, 0)), rv, 8, math.pi / 8) for z in (0.0, POLE_TOP)]
    vs, fs, _ = _prism(a, rings, POLE, _rt("pole", 0.03))
    _texture(a, vs, 0.02, 7041, scale=0.5)
    _reg("pole", "pole", vs)
    # 6-sided: its inner flats (0.252) clear the 8-sided arm's corners (0.2435)
    pts, faces = _annulus_x(SLEEVE_X[0], SLEEVE_X[1], ARM_Y, ARM_Z, ARM_R / C8 + 0.008, SLEEVE_R, 6)
    vs, fs = _shell(a, pts, faces, IRON, _rt("sleeve", 0.02))
    _reg("iron", "sleeve", vs)


EMB_W, EMB_H, EMB_S = 1.10, 1.60, 0.15
EMB_IW, EMB_IH, DOT_R, DOT_X = 0.36, 0.52, 0.12, 0.80
EMB_T = 0.015


def _slab_y(a, outline, tris, y0, y1, key, name, kind, tint=1.0):
    """A closed slab from a 2D outline (x, z) between the planes y0 and y1, explicit cap triangles."""
    n = len(outline)
    pts = [Vector((x, y0, z)) for x, z in outline] + [Vector((x, y1, z)) for x, z in outline]
    faces = [list(t) for t in tris] + [[n + t[2], n + t[1], n + t[0]] for t in tris]
    for i in range(n):
        i1 = (i + 1) % n
        faces.append([i, i1, n + i1, n + i])
    vs, fs = _shell(a, pts, faces, key, tint)
    _reg(kind, name, vs)
    return vs, fs


def emblem(a, cx, cz, yf, side):
    """(m066) The white emblem on one banner face: a diamond outline, an inner diamond, two side points; each 0.005
    into the face and 0.015 proud."""
    y0, y1 = yf - side * 0.005, yf + side * EMB_T
    hw, hh = EMB_W / 2, EMB_H / 2
    k = EMB_S * math.hypot(hw, hh) / hw
    kx = EMB_S * math.hypot(hw, hh) / hh
    outer = [(cx, cz + hh), (cx + hw, cz), (cx, cz - hh), (cx - hw, cz)]
    inner = [(cx, cz + hh - k), (cx + hw - kx, cz), (cx, cz - hh + k), (cx - hw + kx, cz)]
    pts = [Vector((x, y0, z)) for x, z in outer + inner] + [Vector((x, y1, z)) for x, z in outer + inner]
    faces = []
    for i in range(4):
        i1 = (i + 1) % 4
        faces.append([i, i1, 4 + i1, 4 + i])
        faces.append([8 + 4 + i, 8 + 4 + i1, 8 + i1, 8 + i])
        faces.append([i1, i, 8 + i, 8 + i1])
        faces.append([4 + i, 4 + i1, 12 + i1, 12 + i])
    tag = "f" if side < 0 else "b"
    vs, _ = _shell(a, pts, faces, WHITE, _rt("emb" + tag, 0.02))
    _reg("emblem", f"emblem_{tag}", vs)
    for nm, (ex, ez, w2, h2) in (("in", (cx, cz, EMB_IW / 2, EMB_IH / 2)), ("dl", (cx - DOT_X, cz, DOT_R, DOT_R * 1.3)),
                                 ("dr", (cx + DOT_X, cz, DOT_R, DOT_R * 1.3))):
        d = [(ex, ez + h2), (ex + w2, ez), (ex, ez - h2), (ex - w2, ez)]
        _slab_y(a, d, [(0, 1, 2), (0, 2, 3)], y0, y1, WHITE, f"emblem_{tag}_{nm}", "emblem", _rt(nm + tag, 0.02))


def banner(a, y=ARM_Y):
    """The red two-point swallowtail banner (2.10 wide): a 6-sided cloth hem sleeve round the crossarm, a 0.08 slab
    hanging from it (its top 0.007 into the hem), tips at z 3.0, the notch up to 3.8, the hem band one step deeper;
    the white emblem on both faces. Returns the emblem centre."""
    x0, x1 = BAN_X
    pts, faces = _annulus_x(x0, x1, y, ARM_Z, HEM_RI, HEM_RO, 6)
    vs, fs = _shell(a, pts, faces, _mix(BANNER, IRON, 0.15), _rt("hem", 0.02))
    _reg("banner", "banner_hem", vs)
    zt = ARM_Z - HEM_RO + 0.007
    zb = zt - BAN_HEM
    xm = (x0 + x1) / 2
    outline = [(x0, zt), (x1, zt), (x1, zb), (x1, BAN_TIP), (xm, BAN_NOTCH), (x0, BAN_TIP), (x0, zb)]
    tris = [(0, 1, 2), (0, 2, 6), (6, 2, 3), (6, 3, 4), (6, 4, 5)]
    vs, fs = _slab_y(a, outline, tris, y - BAN_T / 2, y + BAN_T / 2, BANNER, "banner", "banner", _rt("banner", 0.02))
    for f in fs:
        if f.calc_center_median().z > zb + 0.01:
            f.material_index = a._mi(_mix(BANNER, IRON, 0.10))
    _texture(a, vs, 0.02, 7042, scale=0.4)
    cx, cz = xm, 6.30
    for side in (-1, 1):
        emblem(a, cx, cz, y + side * BAN_T / 2, side)
    GEO["banner"] = {"w": round(x1 - x0, 3), "top": round(zt, 3), "tips": BAN_TIP, "notch": BAN_NOTCH,
                     "arm_end": ARM_X[1], "knob_end": round(ARM_X[1] + 0.003 + KNOB_L, 3)}
    return Vector((cx, y, cz))


# ---- interior dressing and props (spec 2.8; kit sizes) -------------------------------------------------------------
BED = {"c": (-4.20, 2.15), "x": (-6.40, -2.00), "d": 1.20, "strap": -2.80}
MATP = {"x": (-3.82, -1.65), "y": (-3.30, 1.74), "t": 0.16}   # its head corner clear of the back footing
CRATE = {"c": (-5.60, -1.20), "rot": 5.0, "W": 2.30, "H": 2.20}
TABLE = {"c": (1.20, 2.00), "L": 2.80, "W": 1.60, "top": 2.60}
BARREL = {"c": (3.90, -3.00), "rot": 15.0}


def bedroll(a, c=None, x=None):
    """The leather bedroll lying along the back (spec 2.8): an 8-sided roll (flat underneath, 1.20 across) with golden
    end caps 0.20 wide and flat golden ends, a tan strap band. 92 tris."""
    cx, cy = c or BED["c"]
    x0, x1 = x or BED["x"]
    dx = cx - BED["c"][0]
    n = 8
    rv = BED["d"] / 2 / C8
    cz = BED["d"] / 2 + 0.002
    ang = [-math.pi / 2 + math.pi / n + 2 * math.pi * k / n for k in range(n)]

    def ring(xx):
        return [Vector((xx, cy + math.cos(t) * rv, cz + math.sin(t) * rv)) for t in ang]
    xs = (x0, x0 + 0.20, BED["strap"] + dx - 0.125, BED["strap"] + dx + 0.125, x1 - 0.20, x1)
    vs, fs, bands = _prism(a, [ring(xx) for xx in xs], LEATHER, _rt("bedroll", 0.03))
    for b, k in zip(bands, (GOLD, LEATHER, ROPE_DEEP, LEATHER, GOLD)):
        _paint(a, b, k)
    _paint(a, fs[-2:], GOLD)
    _texture(a, vs, 0.03, 7050, scale=0.6)
    _reg("bedroll", "bedroll", vs)
    GEO["bedroll"] = {"x": [x0, x1], "centre_z": round(cz, 3)}


def mat(a, dx=0.0, dy=0.0):
    """The golden sleeping mat (2.20 x 5.00 x 0.16) with two blue-teal stripes 0.25 wide at 0.6 from each end (thin
    boxes on its top, 0.015 into it: stripe | mat is a hard edge between two materials)."""
    (x0, x1), (y0, y1), t = MATP["x"], MATP["y"], MATP["t"]
    vs, _ = _box(a, (x0 + dx, y0 + dy, 0.0), (x1 + dx, y1 + dy, t), MAT, 1.0)
    _texture(a, vs, 0.03, 7051, scale=0.4)
    _reg("mat", "mat", vs)
    for i, (s0, s1) in enumerate(((y0 + 0.60, y0 + 0.85), (y1 - 0.85, y1 - 0.60))):
        vs, _ = _box(a, (x0 + dx - 0.02, s0 + dy, t - 0.015), (x1 + dx + 0.02, s1 + dy, t + 0.010), STRIPE,
                     _rt(f"stripe{i}", 0.03))
        _reg("stripe", f"stripe_{i}", vs)


def crate(a, c=None, rot=None, tag="crate"):
    """(m066) The X-braced open crate (2.30 x 2.30 x 2.20): four framed sides with recessed panels and an X brace of
    three boards on each, an open top whose rim is the frame width, a dark inner floor 0.60 below the rim. One step
    deeper than the posts overall (by role)."""
    R = _R(c or CRATE["c"], CRATE["rot"] if rot is None else rot)
    W, H = CRATE["W"], CRATE["H"]
    FW, RD, BW, BT, IN = 0.26, 0.05, 0.20, 0.05, 0.60
    h = W / 2
    hi_ = h - FW
    zf = H - IN
    pts = [Vector((-h, -h, 0)), Vector((h, -h, 0)), Vector((h, h, 0)), Vector((-h, h, 0)),
           Vector((-h, -h, H)), Vector((h, -h, H)), Vector((h, h, H)), Vector((-h, h, H)),
           Vector((-hi_, -hi_, H)), Vector((hi_, -hi_, H)), Vector((hi_, hi_, H)), Vector((-hi_, hi_, H)),
           Vector((-hi_, -hi_, zf)), Vector((hi_, -hi_, zf)), Vector((hi_, hi_, zf)), Vector((-hi_, hi_, zf))]
    faces, keys = [], []
    frame_key = _mix(TIMBER, TIMBER_DEEP, 0.25)
    panel_key = _mix(TIMBER, TIMBER_DEEP, 0.45)
    faces.append([3, 2, 1, 0])
    keys.append(TIMBER_DEEP)
    for k in range(4):
        k1 = (k + 1) % 4
        faces.append([4 + k, 4 + k1, 8 + k1, 8 + k])
        keys.append(frame_key)
        faces.append([8 + k, 8 + k1, 12 + k1, 12 + k])
        keys.append(TIMBER_DEEP)
    faces.append([12, 13, 14, 15])
    keys.append(_mix(TIMBER_DEEP, IRON, 0.5))
    sides = [((0, 1, 5, 4), Vector((0, -1, 0))), ((1, 2, 6, 5), Vector((1, 0, 0))),
             ((2, 3, 7, 6), Vector((0, 1, 0))), ((3, 0, 4, 7), Vector((-1, 0, 0)))]
    panels = []
    for (b0, b1, t1, t0), nrm in sides:
        P0, P1, P2, P3 = pts[b0], pts[b1], pts[t1], pts[t0]
        U = (P1 - P0).normalized()
        V = Vector((0, 0, 1))
        q = [P0 + U * FW + V * FW, P1 - U * FW + V * FW, P2 - U * FW - V * FW, P3 + U * FW - V * FW]
        qi = len(pts)
        pts += q
        ri = len(pts)
        pts += [p - nrm * RD for p in q]
        faces += [[b0, b1, qi + 1, qi], [b1, t1, qi + 2, qi + 1], [t1, t0, qi + 3, qi + 2], [t0, b0, qi, qi + 3]]
        keys += [frame_key] * 4
        for k in range(4):
            k1 = (k + 1) % 4
            faces.append([qi + k, qi + k1, ri + k1, ri + k])
            keys.append(panel_key)
        faces.append([ri, ri + 1, ri + 2, ri + 3])
        keys.append(panel_key)
        panels.append((q, nrm, U))
    pts = [R @ p for p in pts]
    vs, fs = _shell(a, pts, faces, panel_key, 1.0)
    rng = random.Random(_seed(tag))
    for f, k in zip(fs, keys):
        f.material_index = a._mi(k)
        _tint(a, [f], 1.0 + rng.uniform(-0.04, 0.04))
    _reg("crate", tag, vs)
    for si, (q, nrm, U) in enumerate(panels):
        cen = sum(q, Vector()) / 4 - nrm * RD
        A_, B_ = W / 2 - FW, H / 2 - FW
        hw = BW / 2
        V = Vector((0, 0, 1))

        def fit(dv, nv):
            return min((A_ - hw * abs(nv[0])) / max(abs(dv[0]), 1e-6), (B_ - hw * abs(nv[1])) / max(abs(dv[1]), 1e-6))
        dA = Vector((A_, B_)).normalized()
        nA = Vector((-dA.y, dA.x))
        LA = fit(dA, nA)
        dB = Vector((-A_, B_)).normalized()
        nB = Vector((-dB.y, dB.x))
        LB = fit(dB, nB)

        def to3(u, v, w):
            return R @ (cen + U * u + V * v + nrm * w)

        def hexa2d(quad):
            return [to3(u, v, -0.005) for u, v in quad] + [to3(u, v, BT - 0.005) for u, v in quad]
        quadA = [dA * -LA + nA * -hw, dA * LA + nA * -hw, dA * LA + nA * hw, dA * -LA + nA * hw]
        vs, _ = _shell(a, hexa2d([(p.x, p.y) for p in quadA]), HEXA, frame_key, _rt(f"{tag}A{si}", 0.04))
        _reg("brace", f"{tag}_A{si}", vs)
        for hi, sg in enumerate((1, -1)):
            sgnA = 1 if nA.dot(dB * sg) > 0 else -1
            corners = []
            for e in (-1, 1):
                t_in = (sgnA * hw - e * hw * nA.dot(nB)) / nA.dot(dB)
                corners.append((dB * t_in + nB * (e * hw), dB * (sg * LB) + nB * (e * hw)))
            quad = [corners[0][0], corners[0][1], corners[1][1], corners[1][0]]
            vs, _ = _shell(a, hexa2d([(p.x, p.y) for p in quad]), HEXA, frame_key, _rt(f"{tag}B{si}{hi}", 0.04))
            _reg("brace", f"{tag}_B{si}_{hi}", vs)


def table(a, c=None, rot=0.0):
    """The open-frame side table (2.80 x 1.60, top 2.60, kit height): a two-plank top, four square legs, two long rails
    under the top and a lower shelf between the legs, each 0.003 off what it meets. One step deeper (by role). 108
    tris."""
    R = _R(c or TABLE["c"], rot)
    L, W, top = TABLE["L"], TABLE["W"], TABLE["top"]
    key = _mix(TIMBER, TIMBER_DEEP, 0.30)
    leg_key = _mix(TIMBER, TIMBER_DEEP, 0.45)
    pw = W / 2 - 0.01
    for i, y0 in enumerate((-W / 2, 0.01)):
        vs, _ = _box(a, (-L / 2, y0, top - 0.20), (L / 2, y0 + pw, top), key, _rt(f"tp{i}", 0.05), R)
        _texture(a, vs, 0.03, 7060 + i, scale=0.6)
        _reg("plank", f"table_plank{i}", vs)
    lx, ly, lh = L / 2 - 0.25, W / 2 - 0.22, 0.13
    zt = top - 0.203
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        x, y = sx * lx, sy * ly
        vs, _ = _box(a, (x - lh, y - lh, 0.0), (x + lh, y + lh, zt), leg_key, _rt(f"tl{i}", 0.04), R)
        _reg("plank", f"table_leg{i}", vs)
    for i, sy in enumerate((-1, 1)):
        y = sy * ly
        vs, _ = _box(a, (-lx + lh + 0.003, y - 0.06, zt - 0.26), (lx - lh - 0.003, y + 0.06, zt), leg_key,
                     _rt(f"tr{i}", 0.04), R)
        _reg("plank", f"table_rail{i}", vs)
    vs, _ = _box(a, (-lx + lh + 0.003, -W / 2 + 0.10, 0.55), (lx - lh - 0.003, W / 2 - 0.10, 0.67), key,
                 _rt("tshelf", 0.04), R)
    _reg("plank", "table_shelf", vs)
    GEO["table"] = {"L": L, "W": W, "top": top}


BARREL_R0, BARREL_R1, BARREL_H, HOOP = 1.00, 1.10, 2.72, 0.05
BARREL_N = 8


def barrel(a, c=None, rot=None, tag="barrel"):
    """(m066) The open hooped barrel (kit size: 2.20 across, 2.72 tall): 8 staves (per-stave tint) bulging from 2.0 to
    2.2, two dark iron hoops 0.21 tall proud 0.05, an open top with a dark inner rim and floor 0.15 below it."""
    c = c or BARREL["c"]
    n = BARREL_N
    R = _R(c, (BARREL["rot"] if rot is None else rot) + 180 / n)
    s = BARREL_H / 2.80

    def r_at(z):
        return BARREL_R0 + (BARREL_R1 - BARREL_R0) * (1 - ((z - BARREL_H / 2) / (BARREL_H / 2)) ** 2)
    prof = [(0.0, 0), (0.24 * s, 0), (0.24 * s, 1), (0.46 * s, 1), (0.46 * s, 0), (BARREL_H / 2, 0), (2.34 * s, 0),
            (2.34 * s, 1), (2.56 * s, 1), (2.56 * s, 0), (BARREL_H, 0)]
    ang = [2 * math.pi * k / n for k in range(n)]
    rings = []
    for z, hoop in prof:
        r = r_at(z) + (HOOP if hoop else 0.0)
        rings.append([Vector((math.cos(t) * r, math.sin(t) * r, z)) for t in ang])
    rin = 0.86 * BARREL_R0
    rings.append([Vector((math.cos(t) * rin, math.sin(t) * rin, BARREL_H)) for t in ang])
    rings.append([Vector((math.cos(t) * rin, math.sin(t) * rin, BARREL_H - 0.15)) for t in ang])
    pts = [R @ p for r in rings for p in r]
    faces, keys, stave = [], [], []
    nr = len(prof)
    for i in range(nr - 1):
        hoop = prof[i][1] or prof[i + 1][1]
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, (i + 1) * n + j1, (i + 1) * n + j])
            keys.append(IRON if hoop else TIMBER)
            stave.append(j)
    for i in (nr - 1, nr):
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, (i + 1) * n + j1, (i + 1) * n + j])
            keys.append(_mix(TIMBER, TIMBER_DEEP, 0.5) if i == nr - 1 else TIMBER_DEEP)
            stave.append(j)
    faces.append([(nr + 1) * n + j for j in range(n)])
    keys.append(_mix(TIMBER_DEEP, IRON, 0.5))
    stave.append(-1)
    faces.append(list(reversed(range(n))))
    keys.append(TIMBER_DEEP)
    stave.append(-1)
    vs, fs = _shell(a, pts, faces, TIMBER, 1.0)
    rng = random.Random(_seed(tag))
    st = [1.0 + rng.uniform(-0.06, 0.06) for _ in range(n)]
    for f, k, sv in zip(fs, keys, stave):
        if k != TIMBER:
            f.material_index = a._mi(k)
        if sv >= 0 and k == TIMBER:
            _tint(a, [f], st[sv])
    _reg("barrel", tag, vs)


# ---- ivy: stems, pads, leaves (spec 2.7; M056 recipe) ----------------------------------------------------------------
CLR = 0.012           # stem and leaf clearance off the stone
KEEP = 0.10           # leaves keep this far from posts, lashings, toggles, canvas
R_MAIN, R_BR = 0.12, 0.08
PAD_W, PAD_T = 0.55, 0.10
# the five-point ivy outline (m056): (lateral, along the blade) from the stalk notch, tip first
LEAF_OUT = ((0.0, 0.92), (0.22, 0.60), (0.56, 0.50), (0.40, 0.05), (0.0, 0.0), (-0.40, 0.05), (-0.56, 0.50),
            (-0.22, 0.60))
LEAF_CT = 0.38
RISE = 0.22           # the top centre raised RISE x size: eight facets tilted about 25 deg round it (a low tent)
FOLD = 0.0            # the halves lift toward the face side by FOLD x |lateral|
CURL = 0.10           # the tip bends back by CURL x along^2
LEAF_POLYS = [[8, i, (i + 1) % 8] for i in range(8)] + [[9, (i + 1) % 8, i] for i in range(8)]
TONE_DEPTH = {IVY_D: (-0.7, -0.35), IVY_G: (-0.2, 0.3), IVY_L: (0.35, 0.7)}    # notch depth / r off the stem axis
TONE_TILT = {IVY_D: (16.0, 26.0), IVY_G: (20.0, 32.0), IVY_L: (26.0, 40.0)}
ROLL = (16.0, 34.0)


class Wall:
    """A stone face: o on the face plane at s = 0, z = 0; n outward; u along the face (horizontal)."""

    def __init__(self, name, o, n, u):
        self.name, self.o, self.n, self.u = name, Vector(o), Vector(n), Vector(u)

    def p(self, s, z, d=0.0):
        return self.o + self.u * s + Z * z + self.n * d


WALLS = {"BI": Wall("BI", (0, BACK_Y[0], 0), (0, -1, 0), (1, 0, 0)),
         "BO": Wall("BO", (0, BACK_Y[1], 0), (0, 1, 0), (1, 0, 0)),
         "SO": Wall("SO", (SIDE_X[0], 0, 0), (-1, 0, 0), (0, 1, 0))}

# Runs (spec 2.7, decision 2: the extra budget goes to the ivy): per run its face, the top it lips over and its stems.
# A stem: id, r, lip=(s, pad (x, y)) to start from a pad on the top, parent=(stem id, z) to branch off, sz = wall path
# [(s, z)], n = wall leaves, lipn = leaves on the lip.
RUNS = {
    "R1": dict(wall="BI", top=13.2, stems=[
        dict(id="main", r=R_MAIN, lip=(-2.85, (-2.85, 3.75)), lipn=2, n=12,
             sz=[(-2.85, 12.75), (-2.6, 10.6), (-2.8, 7.05)]),
        dict(id="A", r=R_BR, parent=("main", 12.1), n=5, sz=[(-3.6, 11.3), (-3.75, 9.4)]),
        dict(id="B", r=R_BR, parent=("main", 10.3), n=3, sz=[(-2.1, 8.2)]),
    ]),
    "R2": dict(wall="BO", top=13.2, stems=[
        dict(id="main", r=R_MAIN, lip=(-1.55, (-1.55, 4.85)), lipn=1, n=10,
             sz=[(-1.55, 12.75), (-1.35, 9.8), (-1.6, 4.3)]),
        dict(id="A", r=R_BR, parent=("main", 11.2), n=4, sz=[(-2.7, 8.2)]),
    ]),
    "R3": dict(wall="BO", top=9.9, stems=[
        dict(id="main", r=R_BR + 0.02, lip=(3.85, (3.85, 4.85)), lipn=1, n=5,
             sz=[(3.85, 9.45), (4.1, 6.4), (3.95, 3.15)]),
    ]),
    "R4": dict(wall="SO", top=8.25, stems=[
        dict(id="a", r=R_BR, lip=(-3.25, (-9.15, -3.25)), lipn=1, n=4, sz=[(-3.25, 7.85), (-3.45, 4.3)]),
        dict(id="b", r=R_BR, lip=(-2.7, (-8.55, -2.7)), lipn=0, n=2, sz=[(-2.7, 7.85), (-2.1, 5.2)]),
    ]),
    "R5": dict(wall="BI", top=9.9, stems=[
        dict(id="main", r=R_BR, lip=(-6.45, (-6.45, 3.75)), lipn=1, n=4, sz=[(-6.45, 9.5), (-6.4, 6.3)]),
    ]),
}


def _surf(w, s, z, tree):
    """How far the stone stands proud of the wall's nominal plane at (s, z) (ray from outside); -0.3 if no stone."""
    o = w.p(s, z, 1.0)
    h = tree.ray_cast(o, -w.n, 1.6)
    if h[0] is None:
        return -0.3
    return 1.0 - h[3]


def wall_points(w, sz, r, tree):
    """(m056) Stem centre points on a wall at the right depth: each segment's clearance is taken from the proudest
    stone under it (sampled every 0.08 along it and +-r across), so the stem's back face stays CLR off the stone."""
    n = len(sz)
    seg = []
    for i in range(n - 1):
        (s0, z0), (s1, z1) = sz[i], sz[i + 1]
        m = max(2, int(math.hypot(s1 - s0, z1 - z0) / 0.08) + 1)
        best = -0.3
        for k in range(m + 1):
            f = k / m
            s, z = s0 + (s1 - s0) * f, z0 + (z1 - z0) * f
            for ds, dz in ((0, 0), (r, 0), (-r, 0), (0, r), (0, -r)):
                best = max(best, _surf(w, s + ds, z + dz, tree))
        seg.append(best)
    out = []
    for i, (s, z) in enumerate(sz):
        m_ = _surf(w, s, z, tree) if n == 1 else max(seg[max(i - 1, 0)], seg[min(i, n - 2)])
        out.append(w.p(s, z, max(m_, 0.0) + CLR + r))
    return out


def _point_at_z(pts, z):
    for p, q in zip(pts, pts[1:]):
        if (p.z - z) * (q.z - z) <= 0 and abs(p.z - q.z) > 1e-6:
            f = (z - p.z) / (q.z - p.z)
            return p + (q - p) * f
    return min(pts, key=lambda p: abs(p.z - z))


def stem_shell(pts, normals, r):
    """(m056) A square-section stem (one closed shell): a ring of 4 at every point, each in the mitre plane of its kink
    (flat junctions), one face toward the surface normal; flat caps at both ends."""
    n = len(pts)
    rings = []
    for i in range(n):
        if i == 0:
            t = (pts[1] - pts[0]).normalized()
            d1 = d2 = t
        elif i == n - 1:
            t = (pts[-1] - pts[-2]).normalized()
            d1 = d2 = t
        else:
            d1 = (pts[i] - pts[i - 1]).normalized()
            d2 = (pts[i + 1] - pts[i]).normalized()
            t = (d1 + d2).normalized()
        nn = Vector(normals[i])
        s = nn.cross(t)
        if s.length < 1e-5:
            s = t.orthogonal()
        s.normalize()
        w = t.cross(s).normalized()
        kd = d2 - d1
        sc = 1.0
        if kd.length > 1e-5:
            kd.normalize()
            half = d1.angle(d2) / 2
            sc = 1.0 / max(math.cos(half), 0.35)
        ring = []
        for a_, b_ in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
            off = (s * a_ + w * b_) * r
            if sc != 1.0:
                off += kd * off.dot(kd) * (sc - 1.0)
            ring.append(pts[i] + off)
        rings.append(ring)
    allp, polys = [], []
    for ring in rings:
        allp += ring
    polys.append([0, 1, 2, 3])
    for i in range(n - 1):
        b0, b1 = 4 * i, 4 * (i + 1)
        polys += [[b0 + k, b0 + (k + 1) % 4, b1 + (k + 1) % 4, b1 + k] for k in range(4)]
    polys.append([4 * (n - 1) + k for k in (3, 2, 1, 0)])
    return allp, polys


def pad_shell(c, n, u, w=PAD_W, t=PAD_T):
    """(m056) The attachment pad on a block top: a square plate w x w x t, chamfered top (a frustum, 12 tris)."""
    n, u = Vector(n).normalized(), Vector(u).normalized()
    v = n.cross(u).normalized()
    c = Vector(c)

    def sq(h, d):
        return [c + n * d + (u * a_ + v * b_) * h for a_, b_ in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
    rings = [sq(w / 2, 0.0), sq(w / 2 - 0.06, t)]
    pts = rings[0] + rings[1]
    polys = [[3, 2, 1, 0]] + [[k, (k + 1) % 4, 4 + (k + 1) % 4, 4 + k] for k in range(4)] + [[4, 5, 6, 7]]
    return pts, polys


def leaf_points(N, d, nL, size):
    """The 16-tri five-point leaf (m056 outline) as a low tent: its top centre raised RISE x size (the midrib and vein
    crease), so its eight facets tilt about 25 deg each round it and never all turn edge-on together from any side
    (STAGES' sweep); the tip curled back CURL x along^2; a bottom centre 0.03 under."""
    x = d.cross(nL).normalized()
    nL = x.cross(d).normalized()
    out = [N + (x * u + d * v) * size + nL * ((FOLD * abs(u) - CURL * v * v) * size) for u, v in LEAF_OUT]
    c = N + d * LEAF_CT * size + nL * (-CURL * LEAF_CT ** 2 * size)
    return out + [c + nL * RISE * size, c - nL * 0.03 * size]


def _leaf_samples(pts):
    o = pts[:8]
    return pts + [(o[i] + o[(i + 1) % 8]) / 2 for i in range(8)] + [(pts[8] + o[i]) / 2 for i in range(8)] + \
        [(c + o[i] + o[(i + 1) % 8]) / 3 for c in pts[8:10] for i in range(8)]


def _sd_stone(p, tree):
    """Signed clearance to the stone (every block in the tree) and the ground: negative inside."""
    h = tree.find_nearest(p)
    d = h[3] if h[0] is not None else 9.0
    if d < 0.6 and _parity_in(tree, p):
        return -d
    return min(d, p.z)


def _clear_of(pts, tree, lim):
    """Every sample at least lim from the keep-out pieces (posts, lashings, canvas ...)."""
    if tree is None:
        return True
    for p in _leaf_samples(pts):
        h = tree.find_nearest(p, lim)
        if h[0] is not None:
            return False
    return True


def push_clear(pts, nL, tree, max_push=0.3):
    """(m056) Push a leaf along its normal until every sample is CLR clear of the stone (None if that takes more than
    max_push). Returns (points, push)."""
    push = 0.0
    for _ in range(8):
        m = min(_sd_stone(p, tree) for p in _leaf_samples(pts))
        if m >= CLR - 1e-4:
            return pts, round(push, 3)
        dv = CLR - m + 0.003
        push += dv
        if push > max_push:
            return None
        pts = [p + nL * dv for p in pts]
    return None


def leaf_frame(st, tone, rng):
    """Blade and face for a station st (dict: c, n, u, g, r, side, kind): the blade turned from the hanging direction
    toward the side (phi), tilted out of the wall (tau, lime outermost and steepest) and rolled about itself (rho,
    alternating), so the leaves face out along many azimuths, never all edge-on from one side (STAGES)."""
    n, u, g, side = st["n"], st["u"], st["g"], st["side"]
    if st["kind"] == "lip":
        phi = math.radians(rng.uniform(5.0, 35.0))
        tau = math.radians(rng.uniform(5.0, 18.0))
    else:
        phi = math.radians(rng.uniform(15.0, 62.0))
        tau = math.radians(rng.uniform(*TONE_TILT[tone]))
    perp = (u - g * u.dot(g)).normalized() * side
    dw = (g * math.cos(phi) + perp * math.sin(phi)).normalized()
    d = dw * math.cos(tau) + n * math.sin(tau)
    nL = n * math.cos(tau) - dw * math.sin(tau)
    rho = math.radians(rng.uniform(*ROLL)) * (side if rng.random() < 0.75 else -side)
    nL = (nL * math.cos(rho) + d.cross(nL) * math.sin(rho)).normalized()
    return d.normalized(), nL


def _stem_depth(pts, stems):
    """The deepest leaf sample inside any stem (ray parity on the stems' BVH)."""
    if stems is None:
        return 0.0
    worst = 0.0
    for p in _leaf_samples(pts):
        h = stems.find_nearest(p, 0.3)
        if h[0] is not None and _parity_in(stems, p):
            worst = max(worst, h[3])
    return worst


def _swallow(pts, spts):
    """The deepest stem sample point inside the leaf's lens (the tented leaf is thick at its centre)."""
    if not spts:
        return 0.0
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))) - Vector((0.01, 0.01, 0.01))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))) + Vector((0.01, 0.01, 0.01))
    cand = [q for q in spts if lo.x <= q.x <= hi.x and lo.y <= q.y <= hi.y and lo.z <= q.z <= hi.z]
    if not cand:
        return 0.0
    t = BVHTree.FromPolygons(pts, LEAF_POLYS)
    worst = 0.0
    for q in cand:
        if _parity_in(t, q):
            worst = max(worst, t.find_nearest(q)[3])
    return worst


def place_leaf(st, tone, rng, tree, keep, stems=None, spts=None):
    """Leaf points for a station: the notch on the stem's side face (0.03 into it), depth by tone (dark nearest the
    stone, lime in front), then pushed off along its normal until clear of the stone and slid out sideways until no
    part of it is more than 0.035 inside a stem; None if it can't be or if it comes within KEEP of the keep-out
    pieces."""
    d, nL = leaf_frame(st, tone, rng)
    C, r, n, side = st["c"], st["r"], st["n"], st["side"]
    sdir = (st["u"] * side)
    N = C + sdir * (r - 0.03) + n * (rng.uniform(*TONE_DEPTH[tone]) * r)
    size = rng.uniform(0.86, 0.95)
    pts = leaf_points(N, d, nL, size)
    res = push_clear(pts, nL, tree)
    if res is None:
        return None
    pts, push = res
    for _ in range(5):
        dep = _stem_depth(pts, stems)
        if dep <= 0.03:
            break
        pts = [p + sdir * (dep - 0.015) for p in pts]
        res = push_clear(pts, nL, tree)
        if res is None:
            return None
        pts, p2 = res
        push += p2
    else:
        return None
    for _ in range(4):
        sw = _swallow(pts, spts)
        if sw <= 0.03:
            break
        pts = [p + nL * (sw - 0.015) for p in pts]
        push += sw - 0.015
    else:
        return None
    if _stem_depth(pts, stems) > 0.03 or not _clear_of(pts, keep, KEEP):
        return None
    return {"pts": pts, "n": nL, "d": d, "size": size, "push": round(push, 3)}


def run_geometry(run, walls_, tree):
    """3D stem polylines for one run: per stem dict(pts, normals, seg (per segment: kind, normal), r, pad)."""
    w = walls_[run["wall"]]
    top = run["top"]
    out = {}
    for st in run["stems"]:
        r = st["r"]
        pts, nrm, seg = [], [], []
        pad = None
        if "lip" in st:
            s, pxy = st["lip"]
            p0 = Vector((pxy[0], pxy[1], top + 0.005 + PAD_T + r - 0.06))
            e = w.p(s, 0.0, 0.0) - w.n * 0.22
            p1 = Vector((e.x, e.y, top + CLR + r))
            pc = w.p(s, top + CLR + r, max(_surf(w, s, top - 0.3, tree), 0.0) + CLR + r)
            pts += [p0, p1, pc]
            nrm += [Z, Z, (Z + w.n).normalized()]
            seg += [("lip", Z), ("lip", Z), ("wall", w.n)]
            pad = Vector((pxy[0], pxy[1], top + 0.005))
        wp = wall_points(w, st["sz"], r, tree)
        if "parent" in st:      # the branch leaves its parent's side face, 0.03 inside it (never from its axis)
            pid, at = st["parent"]
            pp = out[pid]["pts"]
            p = _point_at_z(pp, at)
            tp = min(zip(pp, pp[1:]), key=lambda s: abs((s[0].z + s[1].z) / 2 - at))
            t = (tp[1] - tp[0]).normalized()
            dv = wp[0] - p
            perp = (dv - t * dv.dot(t) - w.n * dv.dot(w.n)).normalized()     # sideways, along the wall
            pts.append(p + perp * (out[pid]["r"] + r - 0.03))
            nrm += [w.n, w.n]
            pts.append(p + perp * (out[pid]["r"] + r + 0.12) + (dv - perp * dv.dot(perp)) * 0.15)
            nrm.append(w.n)
        pts += wp
        nrm += [w.n] * len(wp)
        seg += [("wall", w.n)] * (len(pts) - 1 - len(seg))
        out[st["id"]] = {"pts": pts, "normals": nrm, "seg": seg, "r": r, "pad": pad, "spec": st}
    return out


def _stations(geo, run_name, wall, top):
    """Leaf stations along every stem: lip leaves on the top segments, wall leaves spread along the wall segments
    (branches start a little below their fork); sides alternate."""
    out = []
    for sid, g in geo.items():
        st = g["spec"]
        pts, seg = g["pts"], g["seg"]
        for kind, count in (("lip", st.get("lipn", 0)), ("wall", st.get("n", 0))):
            if not count:
                continue
            segs = [i for i, (k, _) in enumerate(seg) if k == kind]
            if not segs:
                continue
            lens = [(pts[i + 1] - pts[i]).length for i in segs]
            total = sum(lens)
            start = 0.25 if (kind == "wall" and "parent" in st) else 0.12
            usable, acc = [], 0.0
            for i, ln in zip(segs, lens):
                usable.append((acc, i, ln))
                acc += ln
            for j in range(count):
                uu = start + (total - start - 0.1) * (j + 0.5) / count
                i, f = usable[-1][1], 1.0
                for a0, ii, ln in usable:
                    if a0 <= uu <= a0 + ln + 1e-6:
                        i, f = ii, (uu - a0) / max(ln, 1e-6)
                        break
                p = pts[i] + (pts[i + 1] - pts[i]) * f
                if kind == "lip":       # over the top edge: blade out and down, face out and up
                    nn, gdir = (Z * 0.5 + wall.n * 0.866).normalized(), (wall.n * 0.5 - Z * 0.866).normalized()
                else:
                    nn, gdir = wall.n, -Z
                side = 1 if (j + len(out)) % 2 == 0 else -1
                h = 1.2 if kind == "lip" else p.z / top
                out.append({"c": p, "n": nn, "u": wall.u, "g": gdir, "r": g["r"], "side": side, "kind": kind,
                            "h": h, "run": run_name, "stem": sid})
    return out


def ivy(a, runs=None, walls_=None, tree=None, keep=None, seed=7080):
    """Every run: stems (one closed square shell each), pads, then the leaves, toned by role and height rank (about
    40 % lime: lip and upper leaves; 35 % green; 25 % dark: low), each pushed clear of the stone and kept off the
    posts and canvas; of 12 tries per station the leaf farthest from the run's leaves so far is kept."""
    runs = runs or RUNS
    walls_ = walls_ or WALLS
    tree = tree or stone_tree()
    rng = random.Random(seed)
    LEAF_INFO.clear()
    DROPPED.clear()
    stations = []
    scos, spolys = [], []
    for rn, run in runs.items():
        geo = run_geometry(run, walls_, tree)
        w = walls_[run["wall"]]
        for sid, g in geo.items():
            ps, pl = stem_shell(g["pts"], g["normals"], g["r"])
            o_ = len(scos)
            scos += [Vector(p) for p in ps]
            spolys += [[o_ + i for i in p] for p in pl]
            vs, fs = _shell(a, ps, pl, STEM, 1.0 + rng.uniform(-0.03, 0.03))
            _texture(a, vs, 0.03, len(stations) + 7, scale=0.8)
            _reg("stem", f"stem_{rn}_{sid}", vs)
            if g["pad"] is not None:
                pp, ppl = pad_shell(g["pad"], Z, w.u)
                vs, _ = _shell(a, pp, ppl, _mix(STEM, IVY_D, 0.3), 1.0 + rng.uniform(-0.02, 0.02))
                _reg("pad", f"pad_{rn}_{sid}", vs)
        stations += _stations(geo, rn, w, run["top"])
    stems = BVHTree.FromPolygons(scos, spolys) if spolys else None
    spts = scos + [sum((scos[i] for i in p), Vector()) / len(p) for p in spolys] + \
        [(scos[p[i]] + scos[p[(i + 1) % len(p)]]) / 2 for p in spolys for i in range(len(p))]
    scores = sorted(range(len(stations)), key=lambda i: -(stations[i]["h"] + rng.uniform(-0.25, 0.25)))
    nl, ng = round(0.32 * len(stations)), round(0.40 * len(stations))
    tone = {}
    for rank, i in enumerate(scores):
        tone[i] = IVY_L if rank < nl else IVY_G if rank < nl + ng else IVY_D
    placed = {}
    for i, st in enumerate(stations):
        mine = placed.setdefault(st["run"], [])
        cands = []
        for k in range(12):
            st2 = dict(st, side=st["side"] if k % 2 == 0 else -st["side"])
            res = place_leaf(st2, tone[i], rng, tree, keep, stems, spts)
            if res is None:
                continue
            ctr = sum(res["pts"][:8], Vector()) / 8
            cands.append((min([(ctr - q).length for q in mine] or [9.0]), res))
        if not cands:
            DROPPED.append((st["run"], st["stem"], [round(v, 2) for v in st["c"]]))
            continue
        res = max(cands, key=lambda x: x[0])[1]
        nm = f"leaf_{st['run']}_{len(LEAF_INFO)}"
        vs, fs = _shell(a, res["pts"], LEAF_POLYS, tone[i], 1.0 + rng.uniform(-0.04, 0.04))
        _reg("leaf", nm, vs)
        mine.append(sum(res["pts"][:8], Vector()) / 8)
        LEAF_INFO.append({"name": nm, "c": sum(res["pts"][:8], Vector()) / 8, "n": res["n"], "tone": tone[i],
                          "kind": st["kind"], "run": st["run"], "push": res["push"], "size": res["size"]})


def keepout_tree(a):
    """A BVH of the non-stone pieces built so far (posts, toggles, tabs, lashings, beam, canvas, arm ...)."""
    bm = a.bm
    bm.faces.ensure_lookup_table()
    stone = {tuple(round(c, 4) for c in p) for pts, _, _ in G.get("stone", []) for p in pts}
    cos, polys = [], []
    idx = {}
    for f in bm.faces:
        if all(tuple(round(c, 4) for c in v.co) in stone for v in f.verts):
            continue
        poly = []
        for v in f.verts:
            if v not in idx:
                idx[v] = len(cos)
                cos.append(v.co.copy())
            poly.append(idx[v])
        polys.append(poly)
    return BVHTree.FromPolygons(cos, polys) if polys else None


# ---- assemblies -----------------------------------------------------------------------------------------------------------
FR_OVER = (POSTS["FR"][3] + 0.005 + 2 * ARM_R, ARM_Z + ARM_R, ARM_Z - ARM_R)
XFACE = {"FL": (0.0, -1.0), "B": (-1.0, 0.0), "FR": (0.0, -1.0)}


def _reset():
    _clear()
    GEO.clear()
    G.clear()
    LEAF_INFO.clear()
    DROPPED.clear()


def hero_all(a):
    _reset()
    walls(a)
    fallen_block(a)
    for i, (c, size, yaw, chips, seed) in enumerate(RUBBLE):
        rubble(a, c, size, yaw, chips, seed, f"rubble_{i + 1}")
    for tag in POSTS:
        footing(a, tag)
        post(a, tag)
        collars(a, tag)
    crossbeam(a)
    beam_wrap(a)
    for tag in POSTS:
        corner_tab(a, toggle(a, tag), tag)
    for tag in POSTS:
        lashing(a, tag, XFACE[tag], over=FR_OVER if tag == "FR" else None)
    crossarm(a)
    pole(a)
    GEO["emblem_centre"] = [round(x, 3) for x in banner(a)]
    canvas_sheet(a)
    c4_tail(a)
    bedroll(a)
    mat(a)
    crate(a)
    table(a)
    barrel(a)
    keep = keepout_tree(a)
    ivy(a, keep=keep)
    for i, (xy, r, h, seed) in enumerate(MOSS_SITES):
        moss(a, xy, r, h, seed, f"moss_{i}")
    GEO["leaves"] = len(LEAF_INFO)
    GEO["leaves_dropped"] = len(DROPPED)


PART_INFO = {}


def block_part(a):
    """RuinedLeanToWallBlock: one chamfered block (2.0 x 2.4 x 1.635) with one broken corner."""
    _reset()
    pts, polys, chip_vs, top_i = block_shell(2.0, DEPTH, COURSE - SEAT, chips=[("+x-y", 0.35)])
    _stone_piece(a, pts, polys, chip_vs, STONE, 1.0, "block", seed=7090)


# the exploded view's wall chunk (spec 3.14): two piers, an opening one block wide and two courses tall under a long
# bridging block, a stepped top; (course, x0, x1) in its own frame (wall along X, depth 2.4 centred on y 0)
SECTION = ((0, -3.0, -1.0), (0, 1.0, 3.0), (1, -3.0, -1.0), (1, 1.0, 3.0), (2, -3.0, -2.05), (2, -2.0, 2.0),
           (2, 2.05, 3.0), (3, -3.0, -1.0), (3, -0.95, 1.05), (3, 1.1, 3.0), (4, -3.0, -0.95), (4, -0.9, 1.0))
SECTION_CHIPS = {(4, 0): [("-x-y", 0.40)], (3, 2): [("+x-y", 0.35)], (2, 1): [("+x+y", 0.30)]}
SECTION_WALLS = {"F": Wall("F", (0, -DEPTH / 2, 0), (0, -1, 0), (1, 0, 0))}
SECTION_RUN = {"S1": dict(wall="F", top=5 * COURSE, stems=[
    dict(id="main", r=R_BR + 0.02, lip=(0.05, (0.05, -0.35)), lipn=1, n=7,
         sz=[(0.05, 7.8), (0.35, 6.2), (-0.15, 4.6)])])}


def section_part(a):
    """RuinedLeanToWallSection: the modular chunk with its opening, an ivy run down its middle, two moss patches."""
    _reset()
    rng = random.Random(7091)
    for i, (k, x0, x1) in enumerate(SECTION):
        z0 = 0.0 if k == 0 else COURSE * k + SEAT
        H = COURSE * (k + 1) - z0
        chips = SECTION_CHIPS.get((k, sum(1 for kk, _, _ in SECTION[:i] if kk == k)), [])
        pts, polys, chip_vs, _ = block_shell(x1 - x0, DEPTH, H, chips=chips)
        m = Matrix.Translation(((x0 + x1) / 2, rng.uniform(-0.02, 0.02), z0)) @ \
            Matrix.Rotation(math.radians(rng.uniform(-0.5, 0.5)), 4, "Z")
        pts = [m @ p for p in pts]
        _stone_piece(a, pts, polys, chip_vs, course_tone(k), 1.0 + rng.uniform(-0.05, 0.05), f"S{k}_{i}",
                     seed=7092 + i)
    ivy(a, runs=SECTION_RUN, walls_=SECTION_WALLS, tree=stone_tree(), keep=None, seed=7093)
    moss(a, (2.0, 0.3), 0.55, 0.20, 7094, "moss_s1")
    moss(a, (-2.0, 0.4), 0.55, 0.20, 7095, "moss_s2")
    PART_INFO["section_opening"] = [-0.95, 0.95, 0.0, COURSE * 2]


def rubble_part(a):
    """RuinedLeanToRubble: a loose broken block with a moss patch."""
    _reset()
    rubble(a, (0.0, 0.0), (1.6, 1.4, 1.2), 0.0, [("+x+y", 0.35)], 7001, "rubble")
    moss(a, (-0.15, -0.1), 0.45, 0.16, 7110, "moss_r")


def canopy_part(a):
    """RuinedLeanToCanopy: the canvas with its four toggles, corner tabs and the free corner's tail (the toggles where
    the posts hold them in the hero)."""
    _reset()
    for tag in POSTS:
        corner_tab(a, toggle(a, tag), tag)
    canvas_sheet(a)
    c4_tail(a)
    PART_INFO["ties"] = {k: p - Vector((0, 0, CT / 2)) for k, p in canvas_corners().items()}


def post_part(a):
    """RuinedLeanToPost: the front-right post on its footing with its X-lashing, toggle and collars."""
    _reset()
    at = (0.0, 0.0)
    footing(a, "FR", at=at)
    post(a, "FR", at=at)
    collars(a, "FR", at=at)
    toggle(a, "FR", at=at)
    lashing(a, "FR", XFACE["FR"], at=at)
    PART_INFO["post_top"] = Vector((0.0, 0.0, POSTS["FR"][2]))


def banner_part(a):
    """RuinedLeanToBanner: crossarm, knob, dark pole, iron sleeve, banner with its hem and emblems."""
    _reset()
    crossarm(a)
    pole(a)
    banner(a)


def bedroll_part(a):
    """RuinedLeanToBedroll: the bedroll on its mat."""
    _reset()
    bedroll(a)
    mat(a)


def table_part(a):
    _reset()
    table(a, (0.0, 0.0))


def crate_part(a):
    _reset()
    crate(a, (0.0, 0.0), 0.0)


def barrel_part(a):
    _reset()
    barrel(a, (0.0, 0.0), 0.0)


NOTES = {
    HERO: "Camp lean-to in the corner of a ruined stone wall: an L of chamfered pale pink-grey blocks (2.4 deep, 1.65 "
          "courses) stepping up to an eight-course peak, chipped corners, a missing top block, a fallen block, lime "
          "ivy curtains and moss patches; three square timber posts on stone footings with golden X-lashings over "
          "toggles; one cream canvas tied at three corners, the fourth hanging free with a rope tail; a crossbeam "
          "onto the side wall; a red swallowtail banner with a white emblem on a crossarm and dark pole; a leather "
          "bedroll, a striped mat, an X-braced crate, a side table, an open barrel, rubble. Walk-in under the canvas "
          "(Requires Manual Validation in Studio). No light or effect (the sheet shows none). Sheet header 68/132.",
    BLOCK_P: "Ruin Wall Block (modular): one chamfered 2.0 x 2.4 x 1.635 block with a broken corner (course 1.65)",
    SECTION_P: "Ruin Wall Section: a stepped five-course chunk with a one-block, two-course opening under a bridging "
               "block, an ivy run and moss",
    RUBBLE_P: "Stone Rubble: a loose chamfered block with a broken corner and a moss patch",
    CANOPY_P: "Canvas Canopy: the 0.10 canvas sheet with its four corner toggles, gathered tabs and the free corner's "
              "rope tail",
    POST_P: "Upright Post: a 12.0 square timber post on its stone footing with a golden X-lashing, toggle and collars",
    BANNER_P: "Banner: red two-point swallowtail banner with a white emblem on both faces, round crossarm and knob, "
              "dark pole and iron sleeve",
    BEDROLL_P: "Bedroll: a leather bedroll with golden caps and a strap on a golden mat with blue-teal stripes",
    TABLE_P: "Table: an open-frame side table (two-plank top 2.60, rails, lower shelf)",
    CRATE_P: "Crate: an open X-braced crate with a dark interior",
    BARREL_P: "Barrel: an open eight-stave barrel with two iron hoops",
}
COLLISION = {HERO: "precise", BLOCK_P: "box", SECTION_P: "precise", RUBBLE_P: "hull", CANOPY_P: "none",
             POST_P: "hull", BANNER_P: "none", BEDROLL_P: "none", TABLE_P: "box", CRATE_P: "box", BARREL_P: "hull"}


def _bottom_centre(o):
    xs = [v.co.x for v in o.data.vertices]
    ys = [v.co.y for v in o.data.vertices]
    zs = [v.co.z for v in o.data.vertices]
    return Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))


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
    _clear()
    fn(a)
    o = a.finish(collection=M.coll(NUM, TITLE), mark_asset=not temp, origin=None)
    K.drop_unused_slots(o)
    if not temp:
        K.tag(o, SHEET, TITLE, role, COLLISION[name], budget, NOTES[name])
    o[OFF] = [0.0, 0.0, 0.0]
    o.location = (0, 0, 0)
    o["m070_pieces"] = json.dumps([[k, n_, [round(x, 5) for x in c]] for k, n_, c in PIECES])
    o["m070_ropes"] = json.dumps(ROPES)
    o["m070_leaves"] = json.dumps([[l["name"], [round(x, 5) for x in l["n"]], l["kind"]] for l in LEAF_INFO])
    bpy.context.view_layer.update()
    return o


def _recentre(o):
    bc = _bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


def _min_angle(pts):
    out = math.pi
    for k, p in enumerate(pts):
        u, v = pts[k - 1] - p, pts[(k + 1) % len(pts)] - p
        out = min(out, u.angle(v) if u.length > 1e-9 and v.length > 1e-9 else 0.0)
    return out


def _thin(o, lim=3.0):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    angs = [_min_angle([v.co for v in f.verts]) for f in bm.faces]
    bm.free()
    return {"under": sum(1 for x in angs if x < math.radians(lim)), "min_deg": round(math.degrees(min(angs)), 2)}


def _uv_overlaps(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    uv = bm.loops.layers.uv.active
    tris = [[(l[uv].uv.x, l[uv].uv.y) for l in f.loops] for f in bm.faces]
    bm.free()
    boxes = [(min(p[0] for p in t), min(p[1] for p in t), max(p[0] for p in t), max(p[1] for p in t)) for t in tris]
    grid = {}
    for k, b in enumerate(boxes):
        for i in range(int(b[0] // 0.05), int(b[2] // 0.05) + 1):
            for j in range(int(b[1] // 0.05), int(b[3] // 0.05) + 1):
                grid.setdefault((i, j), []).append(k)
    pairs = {(a_, b_) for lst in grid.values() for i, a_ in enumerate(lst) for b_ in lst[i + 1:]}
    return [(a_, b_) for a_, b_ in pairs if M._tri_overlap(tris[a_], tris[b_])]


def _uv_unfold(o, rounds=4):
    """(m012) Cut the smaller face of each UV-overlapping pair free along seams and unwrap again."""
    cut = 0
    for _ in range(rounds):
        bad = _uv_overlaps(o)
        if not bad:
            break
        polys = o.data.polygons
        free = {min((a_, b_), key=lambda i: polys[i].area) for a_, b_ in bad}
        keys = {tuple(sorted(e)) for i in free for e in polys[i].edge_keys}
        for e in o.data.edges:
            if tuple(sorted(e.vertices)) in keys:
                e.use_seam = True
        cut += len(free)
        with M._override(o):
            bpy.ops.object.mode_set(mode="EDIT")
            try:
                bpy.ops.mesh.select_all(action="SELECT")
                bpy.ops.uv.unwrap(method=UV["method"], fill_holes=False, correct_aspect=True,
                                  margin_method="FRACTION", margin=UV["margin"])
            finally:
                bpy.ops.object.mode_set(mode="OBJECT")
    return cut


def _post(o):
    """Stage 2-3 pass: every face a triangle, normals outward per shell, flat shading, origin at the bbox bottom centre,
    UVs (angle-based islands, overlaps cut free), bowties split."""
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
    lg["uv_cut"] = _uv_unfold(o)
    K.drop_unused_slots(o)
    return lg


def _make(name, fn, role="part", budget=1000, temp=False, uv=True):
    t0 = time.time()
    o = _new(name, fn, role, budget, temp=temp)
    if uv:
        lg = _post(o)
    else:
        lg = {}
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


# ---- checks ---------------------------------------------------------------------------------------------------------------
CAT = {"block": "stone", "rubble": "stone", "footing": "stone", "post": "wood", "beam": "wood", "toggle": "wood",
       "arm": "wood", "pole": "wood", "crate": "wood", "brace": "wood", "plank": "wood", "barrel": "wood",
       "bedroll": "cloth", "mat": "cloth", "stripe": "cloth", "tab": "canvas", "canvas": "canvas", "rope": "rope",
       "banner": "banner", "emblem": "banner", "iron": "metal", "leaf": "leaf", "stem": "stem", "pad": "stem",
       "moss": "moss"}
SINK_LIMIT = {("rope", "rope"): 0.08}
THIN_KINDS = ("canvas", "tab", "banner")
DENSE = 5
SKIP_BURY = {("leaf", "leaf")}


def _shells(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    groups = [[] for _ in range(n)]
    for f in bm.faces:
        groups[ids[f.index]].append(f)
    off = Vector(o[OFF]) if OFF in o else Vector()
    reg = [(k, nm, Vector(c)) for k, nm, c in json.loads(o.get("m070_pieces", "[]"))]
    # nearest registered centroid, matched greedily from the closest pairs
    cents = []
    for fs in groups:
        vs = list({v for f in fs for v in f.verts})
        cents.append(sum((v.co for v in vs), Vector()) / len(vs) + off)
    cand = sorted(((rc - c).length, si, ri) for si, c in enumerate(cents) for ri, (_, _, rc) in enumerate(reg)
                  if (rc - c).length < 0.06)
    labels = [("?", "?")] * n
    used_s, used_r = set(), set()
    for d, si, ri in cand:
        if si in used_s or ri in used_r:
            continue
        used_s.add(si)
        used_r.add(ri)
        labels[si] = reg[ri][:2]
    return bm, ids, n, groups, labels


def shells_report(o):
    """(m064) Per shell: kind, name, tris, non-manifold edges and verts, boundary edges, winding errors (manifold edges
    whose two faces run the same way round), self-intersecting face pairs, signed volume."""
    bm, ids, n, groups, labels = _shells(o)
    out = []
    for k in range(n):
        fs = groups[k]
        es = {e for f in fs for e in f.edges}
        vs = list({v for f in fs for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        hits = sum(1 for a_, b_ in tree.overlap(tree) if a_ < b_ and not set(fs[a_].verts) & set(fs[b_].verts))
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) / 3.0
        out.append({"kind": labels[k][0], "name": labels[k][1], "tris": len(fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary),
                    "winding_errors": sum(1 for e in es if e.is_manifold and not e.is_contiguous),
                    "self_hits": hits, "volume": round(vol, 5)})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1, seats=()):
    """(m064) No floating pieces (STAGES): per shell its nearest gap to another shell (0 where triangles intersect) or
    the ground, and whether it chains by contact to the ground. seats = [(name, name)] pair gaps to report."""
    bm, ids, n, groups, labels = _shells(o)
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
    for kk in pairs:
        near[kk] = 0.0
    # long faces (the crossarm against the post, the sleeves round the arm) touch other shells far from their verts:
    # sample every larger triangle on a grid as well
    for f in bm.faces:
        if f.calc_area() < 0.01 or len(f.verts) != 3:
            continue
        s = fsh[f.index]
        c0, c1, c2 = (v.co for v in f.verts)
        for i in range(DENSE + 1):
            for j in range(DENSE + 1 - i):
                p = c0 + (c1 - c0) * (i / DENSE) + (c2 - c0) * (j / DENSE)
                for loc, _, fi, d in tree.find_nearest_range(p, tol):
                    t = fsh[fi]
                    if t != s:
                        kk = (min(s, t), max(s, t))
                        near[kk] = min(near.get(kk, 1e9), d)
    gap = [1e9] * n
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    ground = {k for k in range(n) if zmin[k] - z0 <= tol}
    if n == 1:
        gap = [0.0]
    for k in ground:
        gap[k] = 0.0

    def chained(t):
        adj = {k: set() for k in range(n)}
        for (a_, b_), d in near.items():
            if d <= t:
                adj[a_].add(b_)
                adj[b_].add(a_)
        seen = set(ground) if n > 1 else {0}
        stack = list(seen)
        while stack:
            k = stack.pop()
            for m_ in adj[k]:
                if m_ not in seen:
                    seen.add(m_)
                    stack.append(m_)
        return [labels[k][1] for k in range(n) if k not in seen]
    floating = [k for k in range(n) if gap[k] > tol]
    idx = {labels[k][1]: k for k in range(n)}

    def pair_gap(x, y):
        if x not in idx or y not in idx:
            return None
        a_, b_ = idx[x], idx[y]
        return round(near.get((min(a_, b_), max(a_, b_)), 9.0), 3)
    unch = chained(tol)
    res = {"shells": n, "floating": len(floating), "floating_names": [labels[k][1] for k in floating],
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "unchained": len(unch), "unchained_names": unch, "unchained_chain_tol": len(chained(chain_tol)),
           "on_ground": sorted({labels[k][0] for k in ground}),
           "sink": round(z0 + (o[OFF][2] if OFF in o else 0.0), 3),
           "kinds": {k: [lb[0] for lb in labels].count(k) for k in sorted({lb[0] for lb in labels})},
           "seats": {f"{x}|{y}": pair_gap(x, y) for x, y in seats}}
    bm.free()
    return res


def bury_report(o):
    """(m064) Nothing buried (STAGES): per shell pair, the deepest vert / face centre of one inside the other (ray
    parity, depth to its surface), judged against BURY (SINK_LIMIT for rope joins); and shells wholly inside others."""
    bm, ids, n, groups, labels = _shells(o)
    info = []
    for s in range(n):
        fs = groups[s]
        vs = list({v for f in fs for v in f.verts})
        idx = {v: i for i, v in enumerate(vs)}
        co = [v.co.copy() for v in vs]
        lo = Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co)))
        hi = Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co)))
        tree = BVHTree.FromPolygons(co, [[idx[v] for v in f.verts] for f in fs])
        info.append({"cat": CAT.get(labels[s][0], "?"), "name": labels[s][1], "lo": lo, "hi": hi, "tree": tree,
                     "pts": co + [f.calc_center_median() for f in fs]})
    worst, over, hidden = {}, [], []
    for s, A in enumerate(info):
        inside_any = [False] * len(A["pts"])
        for t, B in enumerate(info):
            if s == t or any(A["hi"][k] < B["lo"][k] - 1e-4 or A["lo"][k] > B["hi"][k] + 1e-4 for k in range(3)):
                continue
            pair = (A["cat"], B["cat"])
            dmax = 0.0
            for j, p in enumerate(A["pts"]):
                if not all(B["lo"][k] - 1e-4 <= p[k] <= B["hi"][k] + 1e-4 for k in range(3)):
                    continue
                if _parity_in(B["tree"], p):
                    inside_any[j] = True
                    dmax = max(dmax, B["tree"].find_nearest(p)[3])
            if dmax <= 0 or pair in SKIP_BURY:
                if dmax > 0:
                    worst[pair] = max(worst.get(pair, 0.0), dmax)
                continue
            worst[pair] = max(worst.get(pair, 0.0), dmax)
            lim = SINK_LIMIT.get(pair, BURY)
            if dmax > lim + 1e-3:
                over.append({"shell": A["name"], "in": B["name"], "depth": round(dmax, 3)})
        if all(inside_any):
            hidden.append(A["name"])
    bm.free()
    return {"worst_depth": {f"{a_}>{b_}": round(d, 3) for (a_, b_), d in sorted(worst.items())},
            "over_limit": over, "fully_hidden": hidden, "buried": len(over) + len(hidden)}


def pierce_report(o):
    """(m064) Thin slabs hide pass-throughs from the bury report: count the edges of every other shell that cross a
    thin surface (canvas, tabs, banner) twice."""
    bm, ids, n, groups, labels = _shells(o)
    cos, polys = [], []
    for k in range(n):
        if labels[k][0] not in THIN_KINDS:
            continue
        vs = list({v for f in groups[k] for v in f.verts})
        vi = {v: i + len(cos) for i, v in enumerate(vs)}
        cos += [v.co.copy() for v in vs]
        polys += [[vi[v] for v in f.verts] for f in groups[k]]
    out = {}
    if polys:
        tree = BVHTree.FromPolygons(cos, polys)
        for k in range(n):
            if labels[k][0] in THIN_KINDS:
                continue
            bad = 0
            for e in {e for f in groups[k] for e in f.edges}:
                p, q = e.verts[0].co, e.verts[1].co
                d = q - p
                L = d.length
                if L < 1e-6:
                    continue
                d = d / L
                hits, t0 = 0, 0.0
                while t0 < L and hits < 2:
                    h = tree.ray_cast(p + d * (t0 + 1e-4), d, L - t0 - 1e-4)
                    if h[0] is None:
                        break
                    hits += 1
                    t0 = (h[0] - p).length + 1e-4
                bad += hits >= 2
            if bad:
                out[labels[k][1]] = bad
    bm.free()
    return out


def rope_ends_report(o):
    """(m064) Every open rope touches what it ties at both ends: each end point's gap to the nearest other shell."""
    bm, ids, n, groups, labels = _shells(o)
    off = Vector(o[OFF])
    fsh = [ids[f.index] for f in bm.faces]
    tree = BVHTree.FromBMesh(bm)
    byname = {labels[k][1]: k for k in range(n)}
    out, bad = {}, []
    for r in json.loads(o.get("m070_ropes", "[]")):
        k = byname.get(r["name"])
        if k is None:
            continue
        gaps = []
        for p in r["ends"]:
            q = Vector(p) - off
            best = 9.0
            for loc, nrm, fi, d in tree.find_nearest_range(q, r["rt"] + 0.3):
                if fsh[fi] != k:
                    best = min(best, d)
            gaps.append(round(max(0.0, best - r["rt"]), 3) if best < 9 else None)
        out[r["name"]] = gaps
        if any(g is None or g > CONTACT for g in gaps):
            bad.append(r["name"])
    bm.free()
    return {"ends": out, "loose": bad}


def _hero_tree(o, kinds=None, skip=()):
    """A BVH of the hero's shells in the build frame (only `kinds` if given, never `skip`), with each face's owner."""
    bm, ids, n, groups, labels = _shells(o)
    off = Vector(o[OFF])
    cos, polys, owner = [], [], []
    for k in range(n):
        if (kinds and labels[k][0] not in kinds) or labels[k][0] in skip:
            continue
        vs = list({v for f in groups[k] for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        base = len(cos)
        cos += [v.co + off for v in vs]
        polys += [[base + vi[v] for v in f.verts] for f in groups[k]]
        owner += [labels[k][1]] * len(groups[k])
    bm.free()
    return (BVHTree.FromPolygons(cos, polys) if polys else None), owner


# body (half x across the walk, half along it, z0, z1) and head (spec 2.10)
PROXY = ((1.0, 0.5, 0.30, 4.4), (0.55, 0.5, 4.4, 5.5))
LANES = {"front": ((-3.2, -9.0), (-3.2, 0.0)), "side": ((9.0, -0.5), (0.0, -0.5))}
UNDER = {"front": ((-4.4, -2.0), (-9.0, 0.0), 6.9), "side": ((0.0, 9.0), (-1.5, 0.5), 8.0)}


def walk_report(o):
    """Spec 2.10: a 5.5 proxy (body 2 x 1 to 4.4, feet 0.25 up over the mat, a 1.1 head to 5.5) walks each lane; the
    nearest hero surface to its sampled surface along the way; the canvas underside's lowest point over each lane
    (rays straight up, canvas faces only); the C4 tail's distance to the lanes."""
    tree, owner = _hero_tree(o)
    res = {}
    for lane, (p0, p1) in LANES.items():
        p0, p1 = Vector((*p0, 0)), Vector((*p1, 0))
        fwd = (p1 - p0).normalized()
        side = Vector((-fwd.y, fwd.x, 0))
        samples = []
        for hx, hy, z0, z1 in PROXY:
            for i in range(9):
                for j in range(9):
                    u, w = -1 + 2 * i / 8, -1 + 2 * j / 8
                    z = z0 + (z1 - z0) * j / 8
                    samples += [side * (hx * u) - fwd * hy + Vector((0, 0, z)), side * (hx * u) + fwd * hy +
                                Vector((0, 0, z)), -side * hx + fwd * (hy * u) + Vector((0, 0, z)),
                                side * hx + fwd * (hy * u) + Vector((0, 0, z)),
                                side * (hx * u) + fwd * (hy * w) + Vector((0, 0, z1))]
        worst, at, who = 9.0, None, None
        L = (p1 - p0).length
        steps = int(L / 0.1) + 1
        for s in range(steps + 1):
            c = p0 + (p1 - p0) * (s / steps)
            for q in samples:
                loc, nrm, fi, d = tree.find_nearest(c + q)
                if d < worst:
                    worst, at, who = d, [round(c.x, 2), round(c.y, 2)], owner[fi]
        res[lane] = {"min_clearance": round(worst, 3), "at": at, "nearest": who}
    ctree, _ = _hero_tree(o, kinds=("canvas", "tab"))
    for lane, ((x0, x1), (y0, y1), need) in UNDER.items():
        low, at = 99.0, None
        x = x0
        while x <= x1 + 1e-6:
            y = y0
            while y <= y1 + 1e-6:
                h = ctree.ray_cast(Vector((x, y, 0.3)), Vector((0, 0, 1)), 30.0)
                if h[0] is not None and h[0].z < low:
                    low, at = h[0].z, [round(x, 2), round(y, 2)]
                y += 0.2
            x += 0.2
        res[lane]["canvas_under_min"] = round(low, 3) if low < 99 else None
        res[lane]["canvas_under_at"] = at
        res[lane]["need"] = need
    res["c4_tail_bottom"] = GEO.get("c4_tail_bottom")
    return res


SKYLINE = ((-9.6, -7.2, 8.25), (-7.2, -5.6, 9.90), (-5.6, -4.0, 11.55), (-4.0, 1.4, 13.20), (1.4, 2.6, 11.55),
           (2.6, 4.4, 9.90), (4.4, 5.2, 8.25))


def skyline_report(o):
    """The back wall's top per span of spec 2.2 (rays down along the wall's mid-depth, every 0.1, the highest stone in
    the middle 60 % of each span) against the table; the side wall's top."""
    tree, _ = _hero_tree(o, kinds=("block",))
    out = []
    for x0, x1, want in SKYLINE:
        zs = []
        x = x0 + 0.2 * (x1 - x0)
        while x <= x1 - 0.2 * (x1 - x0) + 1e-6:
            h = tree.ray_cast(Vector((x, 4.2, 40.0)), Vector((0, 0, -1)), 80.0)
            if h[0] is not None:
                zs.append(h[0].z)
            x += 0.1
        out.append({"span": [x0, x1], "want": want, "top": round(max(zs), 3) if zs else None})
    side = []
    for y in (-3.6, -2.6, 1.0, 2.0):
        h = tree.ray_cast(Vector((-8.4, y, 40.0)), Vector((0, 0, -1)), 80.0)
        side.append([y, round(h[0].z, 3) if h[0] is not None else None])
    return {"back": out, "side": side}


def placement_report(o):
    """Measured targets (spec 4.4): post tops, canvas corner heights, C4 and its tail, banner, crossarm, beam, extents."""
    return {"post_tops": {t: v[2] for t, v in POSTS.items()}, "post_sections": {t: 2 * v[3] for t, v in POSTS.items()},
            "canvas_corners_mid": GEO.get("canvas_corners_mid"), "canvas_low_top": GEO.get("canvas_low_top"),
            "canvas_low_under": GEO.get("canvas_low_under"), "canvas_centre_top": GEO.get("canvas_centre_top"),
            "c4_tail_bottom": GEO.get("c4_tail_bottom"), "lashings": GEO.get("lashings"),
            "banner": GEO.get("banner"), "beam": BEAM, "table": GEO.get("table"), "bedroll": GEO.get("bedroll"),
            "blocks": GEO.get("blocks"), "bond_min_offset": GEO.get("joint_offsets_min"),
            "fallen_gap": GEO.get("fallen_gap"), "size": [round(d, 3) for d in o.dimensions]}


def _cam(az, el):
    a_, e_ = math.radians(az), math.radians(el)
    return Vector((math.sin(a_) * math.cos(e_), -math.cos(a_) * math.cos(e_), math.sin(e_)))


SWEEP_ELS = (0, 5, 10, 20)
EDGE15 = math.sin(math.radians(15))


def leaf_records(o):
    """Per leaf shell of an object: its face normal (stored at placement), its front lobe facets (area vectors) and
    face-on area."""
    bm, ids, n, groups, labels = _shells(o)
    nrm = {nm: Vector(v) for nm, v, _ in json.loads(o.get("m070_leaves", "[]"))}
    kind = {nm: k for nm, _, k in json.loads(o.get("m070_leaves", "[]"))}
    out = []
    for k in range(n):
        nm = labels[k][1]
        if labels[k][0] != "leaf" or nm not in nrm:
            continue
        nL = nrm[nm]
        A = [f.normal * f.calc_area() for f in groups[k]]
        top = [v for v in A if v.length > 1e-9 and v.normalized().dot(nL) > 0.3]
        out.append({"name": nm, "n": nL, "top": top, "top_area": sum(v.length for v in top),
                    "face_on": sum(v.dot(nL) for v in top), "kind": kind[nm]})
    bm.free()
    return out


def leaf_sweep(o, els=SWEEP_ELS, step=5):
    """STAGES' foliage check: the azimuth swept in 5 deg steps at each elevation. A whole leaf is edge-on when at least
    75 % of its front lobe facets are within 15 deg of edge-on, or its projected front area falls under 0.26 of its
    face-on area (a sliver); the share of leaf area edge-on at the worst step must be <= 10 %. The share of leaves
    whose mean plane is within 15 deg of edge-on is reported only."""
    lv = leaf_records(o)
    if not lv:
        return {}
    tot = sum(l["face_on"] for l in lv)
    res = {"leaves": len(lv)}
    for el in els:
        worst, worst_az, plane = 0.0, None, 0.0
        for az in range(0, 360, step):
            v = _cam(az, el)
            edge = pl = 0.0
            for l in lv:
                near = sum(t.length for t in l["top"] if abs(t.normalized().dot(v)) < EDGE15)
                proj = sum(abs(t.dot(v)) for t in l["top"])
                if near >= 0.75 * l["top_area"] or proj < 0.26 * l["face_on"]:
                    edge += l["face_on"]
                if abs(l["n"].dot(v)) < EDGE15:
                    pl += l["face_on"]
            if edge / tot > worst:
                worst, worst_az = edge / tot, az
            plane = max(plane, pl / tot)
        res[f"e{el}"] = {"worst_whole_edge_on_pct": round(100 * worst, 1), "at_az": worst_az,
                         "mean_plane_edge_on_max_pct": round(100 * plane, 1)}
    return res


def leaf_report():
    """Hero leaves: count, tones, kinds, runs, sizes, pushes, dropped stations."""
    if not LEAF_INFO:
        return {}
    n = len(LEAF_INFO)
    return {"leaves": n, "tones": {k[5:]: round(sum(1 for l in LEAF_INFO if l["tone"] == k) / n, 2)
                                   for k in (IVY_L, IVY_G, IVY_D)},
            "kinds": {k: sum(1 for l in LEAF_INFO if l["kind"] == k) for k in ("wall", "lip")},
            "runs": {r: sum(1 for l in LEAF_INFO if l["run"] == r) for r in RUNS},
            "size_across": round(1.12 * sorted(l["size"] for l in LEAF_INFO)[n // 2], 3),
            "pushed": sum(1 for l in LEAF_INFO if l["push"] > 0), "push_max": max(l["push"] for l in LEAF_INFO),
            "dropped": len(DROPPED), "dropped_at": DROPPED[:6]}


# ---- build ---------------------------------------------------------------------------------------------------------------
PARTS = ((BLOCK_P, block_part), (SECTION_P, section_part), (RUBBLE_P, rubble_part), (CANOPY_P, canopy_part),
         (POST_P, post_part), (BANNER_P, banner_part), (BEDROLL_P, bedroll_part), (TABLE_P, table_part),
         (CRATE_P, crate_part), (BARREL_P, barrel_part))
# hero W (X), D (Y), H (Z) +- tolerance: spec 2.11's 21.0 x 13.1 x 13.2 plus the ivy standing proud of the outer
# faces (Y) and lipping over the peak (Z, the front cell's 13.2-13.6)
TARGET_SIZE = ((20.6, 0.4), (13.9, 0.4), (13.45, 0.25))
HERO_BUDGET = 6000                                        # decision 2 (plan about 4800-5400)
HERO_PLAN = 5400
THIN_FLOOR = 0.3
SWEEP_LIMIT = 10.0
SEATS = [("post_FL", "footing_FL"), ("post_B", "footing_B"), ("post_FR", "footing_FR"), ("beam", "post_FL"),
         ("beam", "S4_0"), ("toggle_FL", "post_FL"), ("toggle_B", "post_B"), ("toggle_FR", "post_FR"),
         ("tab_FL", "toggle_FL"), ("tab_B", "toggle_B"), ("tab_FR", "toggle_FR"), ("canvas", "tab_FL"),
         ("canvas", "tab_B"), ("canvas", "tab_FR"), ("c4_tail", "canvas"), ("toggle_C4", "c4_tail"),
         ("crossarm", "post_FR"), ("sleeve", "crossarm"), ("pole", "sleeve"), ("banner_hem", "crossarm"),
         ("banner", "banner_hem"), ("bedroll", "mat"), ("lash_FR_lo", "toggle_FR"), ("lash_FL_lo", "toggle_FL"),
         ("lash_B_lo", "toggle_B")]


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m070_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", HERO))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def export_stats(objs):
    out = {}
    for o in objs:
        socks = [c for c in o.children_recursive if c.get("vfx_kind")]
        glow = sorted({m.name[3:] for m in o.data.materials if list(m.get("flintkit_spec", [0, 0, 0]))[2] > 0})
        out[o.name] = {"vfx_sockets": len(socks), "glow_keys": glow}
    return out


def _store(h, objs):
    off = Vector(h[OFF])
    h["m070_centre"] = [round(x, 3) for x in Vector((-1.0, -1.0, 0.0)) - off]
    h["m070_sleep"] = [round(x, 3) for x in Vector((-2.60, -0.80, MATP["t"])) - off]
    h["m070_corner"] = [round(x, 3) for x in Vector((SIDE_X[1], BACK_Y[0], 0.0)) - off]
    if BLOCK_P in objs:
        objs[BLOCK_P]["m070_course"] = COURSE
    if CANOPY_P in objs and "ties" in PART_INFO:
        cp = objs[CANOPY_P]
        cp["m070_ties"] = json.dumps({k: [round(x, 3) for x in p - Vector(cp[OFF])] for k, p in PART_INFO["ties"].items()})
    if POST_P in objs and "post_top" in PART_INFO:
        pp = objs[POST_P]
        pp["m070_top"] = [round(x, 3) for x in PART_INFO["post_top"] - Vector(pp[OFF])]
    if SECTION_P in objs and "section_opening" in PART_INFO:
        objs[SECTION_P]["m070_opening"] = PART_INFO["section_opening"]


def _object_checks(o, au, shells, problems, lim):
    if au["tris"] > lim:
        problems.append(f"{o.name}: {au['tris']} tris over {lim}")
    for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "wire_edges", "loose_verts",
              "zero_area_faces", "ngons", "dup_verts"):
        if au[k]:
            problems.append(f"{o.name}: {k} {au[k]}")
    if au["normals"] != "outward":
        problems.append(f"{o.name}: normals {au['normals']}")
    for i, s in enumerate(shells):
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "winding_errors", "self_hits"):
            if s[k]:
                problems.append(f"{o.name} shell {i} ({s['name']}): {k} {s[k]}")
        if s["volume"] <= 0:
            problems.append(f"{o.name} shell {i} ({s['name']}): not closed outward (volume {s['volume']})")
        if s["kind"] == "?":
            problems.append(f"{o.name} shell {i}: not matched to a built piece")


def build(render=True, parts=True, close=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    part_geo = {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn)
            if name in (RUBBLE_P, BLOCK_P):
                objs[name]["kit_shading_ok"] = ("the paler facets are the broken corner's freshly exposed stone "
                                                "(spec 5.3, a role); the rest of the block is one stone tone")
            if name == BARREL_P:
                objs[name]["kit_shading_ok"] = ("the dark inner wall and floor are the open barrel's inside and the "
                                                "hoops iron (spec 2.8: open top with a dark rim), materials by role")
            if name == SECTION_P:
                part_geo["section_leaves"] = len(LEAF_INFO)
                part_geo["section_dropped"] = len(DROPPED)
                objs[name]["m070_leaves"] = json.dumps([[l["name"], [round(x, 5) for x in l["n"]], l["kind"]]
                                                        for l in LEAF_INFO])
    h, log["hero"] = _make(HERO, hero_all, "hero", HERO_BUDGET)
    geo = json.loads(json.dumps(GEO, default=lambda v: [round(x, 3) for x in v]))
    leaves = leaf_report()
    _store(h, objs)
    _cleanup_tmp()
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.2f} x {d.y:.2f} x {d.z:.2f}"
    audits = [M.audit(o) for o in order]
    thin = {o.name: _thin(o, 3.0) for o in order}
    shells = {o.name: shells_report(o) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        _object_checks(o, au, shells[o.name], problems, HERO_BUDGET if o is h else 999)
    contact = {o.name: contact_report(o, seats=SEATS if o is h else ()) for o in order}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: floating {c['floating_names']}, unchained {c['unchained_names']}")
        if n_ == HERO and c["sink"] < -0.051:
            problems.append(f"{n_}: sinks {c['sink']} below the ground")
    for k, g in contact[HERO]["seats"].items():
        if g is None or g > CONTACT:
            problems.append(f"{HERO}: seat {k} gap {g}")
    bury = {o.name: bury_report(o) for o in order}
    for n_, b in bury.items():
        if b["buried"]:
            problems.append(f"{n_}: buried {b['over_limit'][:6]} hidden {b['fully_hidden'][:6]}")
    pierce = {o.name: pierce_report(o) for o in (h, objs.get(CANOPY_P), objs.get(BANNER_P)) if o}
    for n_, p in pierce.items():
        if p:
            problems.append(f"{n_}: edges passing through thin canvas / banner {p}")
    ropes = {o.name: rope_ends_report(o) for o in order if json.loads(o.get("m070_ropes", "[]"))}
    for n_, r in ropes.items():
        if r["loose"]:
            problems.append(f"{n_}: rope ends not touching {r['loose']}")
    walk = walk_report(h)
    for lane in LANES:
        w = walk[lane]
        if w["min_clearance"] < 0.10:
            problems.append(f"{HERO}: walk lane {lane} clearance {w['min_clearance']} ({w['nearest']} at {w['at']})")
        if w["canvas_under_min"] is not None and w["canvas_under_min"] < w["need"]:
            problems.append(f"{HERO}: canvas underside {w['canvas_under_min']} over the {lane} lane (need {w['need']})")
    place = placement_report(h)
    sky = skyline_report(h)
    for s in sky["back"]:
        if s["top"] is None or abs(s["top"] - s["want"]) > 0.1:
            problems.append(f"{HERO}: skyline {s['span']} top {s['top']} (want {s['want']})")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    for n_, t in thin.items():
        if t["min_deg"] < THIN_FLOOR:
            problems.append(f"{n_}: a face corner of {t['min_deg']} deg (floor {THIN_FLOOR})")
    sweep = {o.name: leaf_sweep(o) for o in (h, objs.get(SECTION_P)) if o}
    for n_, sw in sweep.items():
        for el in SWEEP_ELS:
            w = sw.get(f"e{el}")
            if w and w["worst_whole_edge_on_pct"] > SWEEP_LIMIT:
                problems.append(f"{n_}: whole edge-on leaves {w['worst_whole_edge_on_pct']} % of the leaf area at e "
                                f"{el} az {w['at_az']} (limit {SWEEP_LIMIT})")
    winding = {o.name: sum(s["winding_errors"] for s in shells[o.name]) for o in order}
    bowties = {o.name: au["nonmanifold_verts"] for o, au in zip(order, audits)}
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
        if u.get("min_gap") is not None and u["min_gap"] < 0.0159:
            problems.append(f"{n_}: UV island gap {u['min_gap']} (margin 0.008)")
    stats = export_stats(order)
    for n_, s in stats.items():
        if s["vfx_sockets"] or s["glow_keys"]:
            problems.append(f"{n_}: {s['vfx_sockets']} sockets, glow {s['glow_keys']} (none wanted)")
    kinds = {}
    for s in shells[HERO]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts", "origin_offset", "transforms_applied")} for au in audits],
           "hero_plan": {"tris": audits[0]["tris"], "plan": HERO_PLAN, "over_plan": audits[0]["tris"] > HERO_PLAN},
           "hero_shells": kinds, "contact": contact, "bury": bury, "rope_ends": ropes, "walk": walk,
           "placement": place, "skyline": sky, "winding": winding, "bowties": bowties, "thin": thin, "log": log,
           "geo": geo, "leaves": leaves, "sweep": sweep, "part_geo": part_geo, "problems": problems, "uv": uv,
           "export_stats": stats, "pierce": pierce,
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "stored": {k: h.get(k) for k in ("m070_centre", "m070_sleep", "m070_corner")},
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


def hero_only(uv=False):
    """Rebuild just the hero (tuning loop): counts, sizes, placements; no UVs unless asked."""
    M.coll(NUM, TITLE)
    palette()
    h, lg = _make(HERO, hero_all, "hero", HERO_BUDGET, uv=uv)
    if not uv:
        bm = bmesh.new()
        bm.from_mesh(h.data)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(h.data)
        bm.free()
        _recentre(h)
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, _ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"hero": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                        "boundary_edges", "normals", "dup_verts")}, "log": lg,
            "geo": json.loads(json.dumps(GEO, default=lambda v: [round(x, 3) for x in v])), "leaves": leaf_report(),
            "offset": [round(x, 3) for x in h[OFF]]}


# ---- renders -------------------------------------------------------------------------------------------------------------
SHEET_LENS = 3.0
SHEET_VIEWS = {"front_sheet": (0, 3), "side_sheet": (90, 3), "rear_sheet": (180, 3), "f34_sheet": (-15, 12),
               "r34_sheet": (140, 15), "r34_high_sheet": (125, 28), "top_sheet": (0, 89.9)}
VIEW_NAMES = ("front34", "rear34", "front", "side", "rear", "top")
PARTS_SHOT = (-25, 15)
PART_SHOTS = {CANOPY_P: (-20, 35), BANNER_P: (-15, 8), BEDROLL_P: (-30, 30), SECTION_P: (-20, 12)}
SPIN = tuple(range(0, 360, 45))
SPIN_EL = 10


def _long_lens(kit):
    """(m033) render_group with a long lens and the studio floor hidden for the *_sheet shots."""
    orig = kit["render_group"]

    def rg(group, path, azimuth=-22, elevation=20):
        cam = bpy.data.objects["FB_Cam"].data
        lens = cam.lens
        ground = bpy.data.objects.get("FB_Ground")
        gh = ground.hide_render if ground else None
        name = path.rsplit("/", 1)[-1]
        if "_sheet" in name:
            cam.lens = lens * SHEET_LENS
            if ground:
                ground.hide_render = True
        try:
            return orig(group, path, azimuth, elevation)
        finally:
            cam.lens = lens
            if ground:
                ground.hide_render = gh
    return orig, rg


def render_close(objs, path, az, el, centre, radius, cell=(480, 400)):
    """(m033) A close-up from (az, el), framed on a sphere (centre, radius)."""
    kit = K.NS["KIT"]
    fb = kit["frame_box"]
    c = Vector(centre)
    box = [c + Vector((dx, dy, dz)) * radius for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    kit["frame_box"] = lambda corners, a_, e_: fb(box, a_, e_)
    ground = bpy.data.objects.get("FB_Ground")
    if ground:
        ground.hide_render = el < 0
    old = kit["CELL"]
    kit["CELL"] = cell
    try:
        return kit["render_group"](objs, path, az, el)
    finally:
        kit["CELL"] = old
        kit["frame_box"] = fb
        if ground:
            ground.hide_render = False


def render_cam(objs, path, loc, look, lens=18.0, cell=(560, 420)):
    """(m064) A render from a fixed camera (loc looking at look)."""
    kit = K.NS["KIT"]
    fb = kit["frame_box"]
    cam = bpy.data.objects["FB_Cam"]
    lens0 = cam.data.lens
    ground = bpy.data.objects.get("FB_Ground")
    loc, look = Vector(loc), Vector(look)
    z0 = objs[0].matrix_world.translation.z

    def fixed(corners, az, el):
        cam.data.shift_x = cam.data.shift_y = 0.0
        cam.location = loc
        cam.rotation_euler = (look - loc).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lens
        if ground:
            ground.location = (loc.x, loc.y, z0)
    kit["frame_box"] = fixed
    old = kit["CELL"]
    kit["CELL"] = cell
    try:
        return kit["render_group"](objs, path, 0, 10)
    finally:
        kit["frame_box"] = fb
        kit["CELL"] = old
        cam.data.lens = lens0


def _at(o, p):
    return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)


def _exploded(objs):
    """Linked copies of the parts laid out like the sheet's exploded assembly: the wall section and rubble at the
    left, the canopy lifted over a post, the banner and barrel at the right, the bedroll, table and crate in front."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []
    o0 = Matrix.Translation((objs[0].location.x + 60, objs[0].location.y, 0))

    def put(tag, part, m):
        if part not in by:
            return
        c = bpy.data.objects.new(f"{PFX}expl_{tag}", by[part].data)
        coll.objects.link(c)
        c.matrix_world = o0 @ m
        shown.append(c)
    put("section", SECTION_P, Matrix.Translation((-9.0, 2.0, 0.0)) @ Matrix.Rotation(math.radians(25), 4, "Z"))
    put("block", BLOCK_P, Matrix.Translation((-12.5, -3.5, 0.0)))
    put("rubble", RUBBLE_P, Matrix.Translation((-8.5, -5.0, 0.0)))
    put("canopy", CANOPY_P, Matrix.Translation((0.5, 1.0, 5.0)))
    put("post", POST_P, Matrix.Translation((5.0, 1.0, 0.0)))
    put("banner", BANNER_P, Matrix.Translation((9.0, -1.0, 0.0)))
    put("bedroll", BEDROLL_P, Matrix.Translation((-1.0, -5.0, 0.0)))
    put("table", TABLE_P, Matrix.Translation((-3.5, -0.5, 0.0)))
    put("crate", CRATE_P, Matrix.Translation((2.5, -6.0, 0.0)))
    put("barrel", BARREL_P, Matrix.Translation((7.0, -6.5, 0.0)))
    bpy.context.view_layer.update()
    return shown


def _marker(h, at, name, proxy=False, rot=0.0):
    """A 5.5-stud character stand-in (proxy: the spec 2.10 walk box)."""
    a = K.fk().Asset(PFX + name, "probe", seed=1, tint_var=0.0)
    if proxy:
        for hx, hy, z0, z1 in PROXY:
            _box(a, (-hx, -hy, z0), (hx, hy, z1), IRON, 0.8)
    else:
        a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=IRON, tint=0.7)
        a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=IRON, tint=0.7)
        a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=IRON, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    c.location = _at(h, at)
    c.rotation_euler = (0, 0, math.radians(rot))
    bpy.context.view_layer.update()
    return c


def _remove(objs):
    for o in objs:
        me = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(me, bpy.types.Mesh) and me.users == 0:
            bpy.data.meshes.remove(me)


def _mirror_png(src, dst):
    kit = K.NS["KIT"]
    px = kit["load_px"](src)
    kit["save_px"](np.ascontiguousarray(px[:, ::-1]), dst)
    return dst


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    markers = [_marker(h, (-3.2, -7.5, 0.0), "char"), _marker(h, (-2.6, -0.8, 0.0), "char2", proxy=True)]
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        for o in objs[1:]:
            extra["part_" + o.name.replace(HERO, "").lower()] = ([o], *PART_SHOTS.get(o.name, PARTS_SHOT))
        if shown:
            extra["exploded"] = (shown, -20, 22)
        extra["scale"] = ([h] + markers, -25, 8)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            sheet = M.views(NUM, [h], names=VIEW_NAMES, extra=extra, vfx=False)
            spin = render_spin(h)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet, "spin": spin, "top_mirror": _mirror_png(f"{d}/top_sheet.png",
                                                                        f"{d}/top_mirror_sheet.png")}
        if close:
            out.update(render_close_ups(objs))
        return out
    finally:
        _remove(shown + markers)
        M.display(NUM, objs, TITLE)


def render_spin(h):
    """The eight-azimuth contact sheet: az 0, 45 ... 315 at e 10, long lens, floor hidden -> M070_spin.png."""
    kit = K.NS["KIT"]
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    old = kit["CELL"]
    kit["CELL"] = (420, 360)
    try:
        paths = [kit["render_group"]([h], f"{d}/spin{az:03d}_sheet.png", az, SPIN_EL) for az in SPIN]
    finally:
        kit["CELL"] = old
    rows = [kit["hstack"](paths[i:i + 4]) for i in (0, 4)]
    out = f"{d}/M070_spin.png"
    kit["save_px"](kit["vstack"](rows), out)
    return out


def render_close_ups(objs):
    """junction_cu (close-up A: the FR post top, toggle, tab, lashing, crossarm), underside_cu (close-up B: under the
    FL corner looking up), block_cu (close-up C: the peak's inner face with R1), ruin_cu (the side wall's front end, the
    fallen block), inside_cu (from the front lane), walk (the 5.5 proxy on both lanes), thumb (the f34 small)."""
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    h = objs[0]
    out = {}
    rc = render_close
    kit = K.NS["KIT"]
    out["junction_cu"] = rc([h], f"{d}/junction_cu.png", -35, 12, _at(h, (5.6, -4.9, 9.6)), 1.5)
    out["junction_fl_cu"] = rc([h], f"{d}/junction_fl_cu.png", -30, 15, _at(h, (-5.8, -4.0, 8.4)), 1.4)
    out["block_cu"] = rc([h], f"{d}/block_cu.png", -12, 12, _at(h, (-3.0, 2.8, 11.0)), 2.2)
    out["ruin_cu"] = rc([h], f"{d}/ruin_cu.png", -55, 15, _at(h, (-9.8, -2.0, 4.0)), 4.6)
    out["rear_ivy_cu"] = rc([h], f"{d}/rear_ivy_cu.png", 165, 10, _at(h, (-1.8, 5.6, 9.0)), 3.2)
    out["underside_cu"] = render_cam([h], f"{d}/underside_cu.png", _at(h, (-3.6, -2.4, 2.6)),
                                     _at(h, (-5.3, -3.9, 8.0)), lens=16.0)
    out["inside_cu"] = render_cam([h], f"{d}/inside_cu.png", _at(h, (-3.2, -7.0, 4.6)), _at(h, (-3.4, 1.5, 1.2)),
                                  lens=16.0)
    lanes = [_marker(h, (-3.2, -6.0, 0.0), "proxy0", proxy=True), _marker(h, (-3.2, -0.5, 0.0), "proxy1", proxy=True),
             _marker(h, (6.5, -0.5, 0.0), "proxy2", proxy=True, rot=90.0)]
    try:
        old = kit["CELL"]
        kit["CELL"] = (420, 360)
        try:
            p1 = kit["render_group"]([h] + lanes, f"{d}/walk_front.png", 0, 4)
            p2 = kit["render_group"]([h] + lanes, f"{d}/walk_side.png", 90, 4)
            p3 = rc([h] + lanes, f"{d}/walk_f34.png", -35, 10, _at(h, (-0.5, -2.0, 4.0)), 7.0, cell=(420, 360))
        finally:
            kit["CELL"] = old
        path = f"{d}/walk.png"
        kit["save_px"](kit["hstack"]([p1, p2, p3]), path)
        out["walk"] = path
    finally:
        _remove(lanes)
    old = kit["CELL"]
    kit["CELL"] = (180, 150)
    try:
        orig, kit["render_group"] = _long_lens(kit)
        try:
            out["thumb"] = kit["render_group"]([h], f"{d}/thumb_sheet.png", *SHEET_VIEWS["f34_sheet"])
        finally:
            kit["render_group"] = orig
    finally:
        kit["CELL"] = old
    return out


def preview(names=("front_sheet", "side_sheet", "f34_sheet", "rear_sheet"), spin=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = _long_lens(kit)
    try:
        r = M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=False)
        if spin:
            r = [r, render_spin(h)]
        return r
    finally:
        kit["render_group"] = orig
