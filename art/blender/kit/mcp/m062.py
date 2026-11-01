"""062 Ground Scatter (references/062.png): a knee-low forest-floor litter pile of loose closed solids. Two big green
lobed leaves, two orange maples (one propped on the long twig), a rust maple under the twigs, two yellow maples, three
small green leaves, two square-section twigs crossed in an X (the lifted one is the top of the pile) with a small twig
under them, one upright shingled pinecone, two faceted warm-grey stones and four wood chips. No base plate, no glow,
no VFX.

    import importlib, kit_models, m062; importlib.reload(kit_models); importlib.reload(m062); m062.build()

Build frame: studs, front -Y, +X right, ground z 0 (spec 2). Every object ends with its origin at its bbox bottom
centre; o["m062_offset"] is that origin in the build frame. W07 owns every GroundScatter* name, so the names are
ForestLitter* (decision 2):
- ForestLitter (hero): 10 leaves (6 with petioles), 3 twigs, the pinecone (core + 40 scales), 2 stones, 4 chips, one
  object of separate closed shells, every one resting on the ground or on the piece under it (no booleans).
- ForestLitterLeafLarge / LeafMedium / LeafSmall / LeafVariant / TwigLarge / TwigSmall / Pinecone / StoneLarge /
  StoneSmall: the part list's pieces at hero size.
Colour (stage 4) is painted by role and by position (radial bands from each leaf's petiole hub, along each twig and
each pinecone scale, noise patches on the stones), never by facing. Stages 5-6: none (the sheet shows no effect).
See M062_spec.md.
"""
import json
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
import m047

NUM, TITLE, SHEET = 62, "Ground Scatter", "M062"
OFF = "m062_offset"
PFX = "_m062_"
HERO = "ForestLitter"
LEAF_L_P, LEAF_M_P, LEAF_S_P, LEAF_V_P = ("ForestLitterLeafLarge", "ForestLitterLeafMedium", "ForestLitterLeafSmall",
                                          "ForestLitterLeafVariant")
TWIG_L_P, TWIG_S_P = "ForestLitterTwigLarge", "ForestLitterTwigSmall"
CONE_P = "ForestLitterPinecone"
STONE_L_P, STONE_S_P = "ForestLitterStoneLarge", "ForestLitterStoneSmall"

GREEN, DEEP, LIME, PALE = "m062_leaf_green", "m062_leaf_deep", "m062_leaf_lime", "m062_leaf_pale"
OLIVE, YELLOW, AMBER = "m062_leaf_olive", "m062_leaf_yellow", "m062_leaf_amber"
ORANGE, RUST = "m062_leaf_orange", "m062_leaf_rust"
WOOD, WOOD_L, WOOD_D = "m062_wood", "m062_wood_light", "m062_wood_dark"
CONE_S, CONE_M, CONE_C = "m062_cone_scale", "m062_cone_mid", "m062_cone_core"
STONE, STONE_D = "m062_stone", "m062_stone_deep"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
BURY = 0.05
PEN = 0.006                 # settled pieces press this far into what they rest on, so the contact is a real overlap
PET_SEAT = 0.04             # a petiole starts this far inside its leaf, in front of the base notch (fix round 1)
CHIP_HANG = 0.10            # a chip's underside may hang at most this far over what lies below it (fix round 1)

# key -> (hex, roughness, low specular). Stage 4 writes the calibrated values here (spec "Stage 4").
PALETTE = {
    GREEN: ("#628E31", 0.8, True),
    DEEP: ("#4D792B", 0.85, True),
    LIME: ("#739637", 0.8, True),
    PALE: ("#90A255", 0.8, True),
    OLIVE: ("#6D5B1D", 0.85, True),
    YELLOW: ("#BE9E3E", 0.8, True),
    AMBER: ("#AA7C1E", 0.8, True),
    ORANGE: ("#B1672F", 0.8, True),
    RUST: ("#814A2A", 0.85, True),
    WOOD: ("#734F34", 0.9, True),
    WOOD_L: ("#896E58", 0.9, True),
    WOOD_D: ("#5A3822", 0.9, True),
    CONE_S: ("#9E6C46", 0.75, True),
    CONE_M: ("#6D4529", 0.8, True),
    CONE_C: ("#2A1206", 0.9, True),         # fix round 1: near-black gaps (the sheet's #2A1004); was #40230E
    STONE: ("#9A9493", 0.9, True),          # a red-warm grey, R > G > B (decision 13): the studio's warm light renders
    STONE_D: ("#8C8685", 0.9, True),        # it at the sheet's h 12-20, where a neutral grey renders yellowish (h 31);
                                            # fix round 1: lighter toward the sheet (was #837F7E / #777372)
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions), K.sample kinds
TARGETS = {GREEN: ((0x78, 0xAD, 0x32), "green"), DEEP: ((0x5C, 0x92, 0x2B), "green"),
           LIME: ((0x8E, 0xB8, 0x39), "green"), PALE: ((0xB6, 0xC7, 0x5C), "vivid"),
           OLIVE: ((0x87, 0x6A, 0x1D), "vivid"), YELLOW: ((0xF0, 0xBE, 0x40), "vivid"),
           AMBER: ((0xD5, 0x92, 0x1E), "vivid"), ORANGE: ((0xE0, 0x76, 0x30), "vivid"),
           RUST: ((0xA1, 0x54, 0x2A), "brown"), WOOD: ((0x8E, 0x5A, 0x35), "brown"),
           WOOD_L: ((0xAC, 0x83, 0x5F), "brown"), WOOD_D: ((0x6C, 0x3E, 0x22), "brown"),
           CONE_S: ((0xC8, 0x80, 0x4A), "brown"), CONE_M: ((0x87, 0x4D, 0x29), "brown"),
           CONE_C: ((0x4A, 0x25, 0x0F), "brown"), STONE: ((0xAE, 0xA6, 0xA2), "stone"),
           STONE_D: ((0x9F, 0x94, 0x90), "stone")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m062_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k == "m062_" + tail), None) or \
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


# ---- small helpers -------------------------------------------------------------------------------------------------
_faces = m033._faces


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


def _close(a, vs, fs, key, tint=1.0):
    bmesh.ops.recalc_face_normals(a.bm, faces=fs)
    a._finish(vs, key, tint=tint)


def _u(az):
    r = math.radians(az)
    return Vector((math.cos(r), math.sin(r), 0.0))


def _move(vs, d):
    d = Vector(d)
    for v in vs:
        v.co += d


def _xform(vs, m):
    for v in vs:
        v.co = m @ v.co


def _centre(vs):
    return sum((v.co for v in vs), Vector()) / max(1, len(vs))


def _zmin(vs):
    return min(v.co.z for v in vs)


def _tree(vs):
    fs = _faces(vs)
    idx = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[idx[v] for v in f.verts] for f in fs])


def _overlap(vs1, vs2):
    return bool(_tree(vs1).overlap(_tree(vs2)))


# ---- piece registry (the hero's shells, for settling and the reports) ----------------------------------------------
class Pile:
    """The pieces placed so far: name -> (kind, verts). Kinds: leaf, petiole, twig, core, scale, stone, chip."""

    def __init__(self):
        self.p = {}

    def add(self, name, kind, vs):
        self.p[name] = (kind, vs)
        return vs

    def vs(self, names=None, kinds=None, skip=()):
        out = []
        for n, (k, vs) in self.p.items():
            if n in skip or (names is not None and n not in names) or (kinds is not None and k not in kinds):
                continue
            out += [v for v in vs if v.is_valid]
        return out

    def solids(self, names=None, kinds=None, skip=()):
        s = m047._Solids()
        for n, (k, vs) in self.p.items():
            if n in skip or (names is not None and n not in names) or (kinds is not None and k not in kinds):
                continue
            s.add_vs([v for v in vs if v.is_valid], n)
        return s


def _samples(vs):
    """Verts, face centres and edge midpoints of a piece (settling probes)."""
    pts = [v.co.copy() for v in vs]
    fs = _faces(vs)
    pts += [f.calc_center_median() for f in fs]
    es = {e for f in fs for e in f.edges}
    pts += [(e.verts[0].co + e.verts[1].co) / 2 for e in es]
    return pts


def _clear(vs, sup_vs):
    """How far a piece could fall straight down onto sup_vs (rays both ways), or None if nothing is under it."""
    d_sup = None
    st = _tree(sup_vs)
    down = Vector((0, 0, -1))
    for p in _samples(vs):
        h = st.ray_cast(p, down, 50.0)
        if h[0] is not None:
            d_sup = h[3] if d_sup is None else min(d_sup, h[3])
    lo = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs)))
    hi = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs)))
    pt = _tree(vs)
    up = Vector((0, 0, 1))
    for q in _samples(sup_vs):
        if lo.x <= q.x <= hi.x and lo.y <= q.y <= hi.y:
            h = pt.ray_cast(q, up, 50.0)
            if h[0] is not None:
                d_sup = h[3] if d_sup is None else min(d_sup, h[3])
    return d_sup


def _drop(vs, sup_vs, ground=0.0, pen=PEN, ground_pen=PEN):
    """Lower a piece straight down until it rests on the ground or on the support pieces (rays both ways between the
    two, from verts, face centres and edge midpoints), pressing `pen` into the support. Returns (dz, what)."""
    lift = 4.0 - _zmin(vs)
    _move(vs, (0, 0, lift))
    d_ground = _zmin(vs) - ground + ground_pen
    d_sup = 1e9
    if sup_vs:
        st = _tree(sup_vs)
        down = Vector((0, 0, -1))
        for p in _samples(vs):
            h = st.ray_cast(p, down, 50.0)
            if h[0] is not None:
                d_sup = min(d_sup, h[3])
        lo = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs)))
        hi = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs)))
        pt = _tree(vs)
        up = Vector((0, 0, 1))
        for q in _samples(sup_vs):
            if lo.x <= q.x <= hi.x and lo.y <= q.y <= hi.y:
                h = pt.ray_cast(q, up, 50.0)
                if h[0] is not None:
                    d_sup = min(d_sup, h[3])
        d_sup += pen
    d = min(d_ground, d_sup)
    _move(vs, (0, 0, -d))
    return round(lift - d, 4), ("ground" if d_ground <= d_sup else "support")


def _drape(vs, sup_vs, slope=0.45, pen=PEN, groups=None):
    """A soft leaf lying over the leaves under it: on the ground (lowest point PEN into it), then every vert lifted by
    the support height field dilated with `slope` (h(p) = max over support verts q of z(q) - slope |p - q|), so the
    leaf rises over a neighbour's edge and comes down again beside it, keeping its thickness. Returns (lift, what)."""
    _move(vs, (0, 0, -pen - _zmin(vs)))
    if not sup_vs:
        return 0.0, "ground"
    lo = Vector((min(v.co.x for v in vs) - 0.4, min(v.co.y for v in vs) - 0.4))
    hi = Vector((max(v.co.x for v in vs) + 0.4, max(v.co.y for v in vs) + 0.4))
    qs = [q for q in _samples(sup_vs) if lo.x <= q.x <= hi.x and lo.y <= q.y <= hi.y]
    if not qs:
        return 0.0, "ground"
    zb = _zmin(vs)
    groups = groups or [[v] for v in vs]
    worst = 0.0
    for g in groups:
        lifts = []
        for v in g[:1] if len(g) > 3 else g:
            h = max(q.z - slope * math.hypot(v.co.x - q.x, v.co.y - q.y) for q in qs)
            lifts.append(max(0.0, h - pen - zb))
        lift = max(lifts)
        if lift > 0:
            for v in g:
                v.co.z += lift
            worst = max(worst, lift)
    return round(worst, 4), ("support" if worst > 0 else "ground")


def _support_z(sup_tree, pts):
    """Highest support surface under any of pts (ray down from z 5), or 0 (the ground)."""
    z = 0.0
    if sup_tree is None:
        return z
    for p in pts:
        h = sup_tree.ray_cast(Vector((p.x, p.y, 5.0)), Vector((0, 0, -1)), 10.0)
        if h[0] is not None:
            z = max(z, h[0].z)
    return z


# ---- leaves (spec 1.4, 2.2: closed bevelled slabs, lobes folded along their veins) ---------------------------------
# A lobe is (angle deg from the tip axis, length as a fraction of R, half-span deg, flank profile [(f, rf)]): f is the
# angle offset in half-spans, rf the radius as a fraction of the lobe length. Sinus radii are fractions of R between
# consecutive lobes; base is the sinus behind the petiole hub. Angles strictly increase round the outline, so the
# outline is star-shaped about the hub.
_P3 = [(-0.72, 0.64), (0.0, 1.0), (0.72, 0.64)]
_PL_MAIN = [(-0.78, 0.64), (-0.40, 0.82), (0.0, 1.0), (0.40, 0.82), (0.78, 0.64)]
_PL_SIDE_R = [(-0.70, 0.62), (0.0, 1.0), (0.50, 0.78), (0.74, 0.64)]          # a tooth on the outer (+) edge
_PL_SIDE_L = [(-0.74, 0.64), (-0.50, 0.78), (0.0, 1.0), (0.70, 0.62)]
_PM_MAIN = [(-0.78, 0.60), (-0.52, 0.80), (0.0, 1.0), (0.52, 0.80), (0.78, 0.60)]
_PM_SIDE_R = [(-0.70, 0.62), (0.0, 1.0), (0.46, 0.74), (0.66, 0.78)]
_PM_SIDE_L = [(-0.66, 0.78), (-0.46, 0.74), (0.0, 1.0), (0.70, 0.62)]
_PM_BASAL = [(-0.62, 0.68), (0.0, 1.0), (0.62, 0.68)]
_PS_LOBE = [(-0.66, 0.68), (0.0, 1.0), (0.66, 0.68)]
_PV_MAIN = [(-0.74, 0.56), (-0.50, 0.76), (0.0, 1.0), (0.50, 0.76), (0.74, 0.56)]
_PV_SIDE = [(-0.64, 0.58), (0.0, 1.0), (0.46, 0.70), (0.66, 0.74)]
_PV_SIDE_L = [(-0.66, 0.74), (-0.46, 0.70), (0.0, 1.0), (0.64, 0.58)]
KINDS = {
    # Leaf (large): five broad pointed lobes, a tooth on each side lobe's outer edge (22 outline verts)
    "large": dict(lobes=[(-124, 0.52, 25, _P3), (-64, 0.84, 30, _PL_SIDE_L), (0, 1.0, 32, _PL_MAIN),
                         (64, 0.84, 30, _PL_SIDE_R), (124, 0.52, 25, _P3)],
                  sinus=[0.46, 0.66, 0.66, 0.46], base=0.08, vein=0.50, hub=0.06),
    # Leaf (medium), maple: five toothed lobes (24)
    "maple": dict(lobes=[(-114, 0.60, 24, _PM_BASAL), (-55, 0.92, 28, _PM_SIDE_L), (0, 1.0, 28, _PM_MAIN),
                         (55, 0.92, 28, _PM_SIDE_R), (114, 0.60, 24, _PM_BASAL)],
                  sinus=[0.46, 0.58, 0.58, 0.46], base=0.08, vein=0.48, hub=0.06),
    # Leaf (small): the same maple, rounder, no teeth (16)
    "maple_small": dict(lobes=[(-112, 0.56, 24, [(0.0, 1.0)]), (-55, 0.88, 28, _PS_LOBE), (0, 1.0, 30, _PS_LOBE),
                               (55, 0.88, 28, _PS_LOBE), (112, 0.56, 24, [(0.0, 1.0)])],
                        sinus=[0.48, 0.62, 0.62, 0.48], base=0.10, vein=0.50, hub=0.07),
    # Leaf (variant): jagged maple (22); two lobes curl up
    "variant": dict(lobes=[(-110, 0.60, 22, [(0.0, 1.0)]), (-52, 0.90, 25, _PV_SIDE_L), (0, 1.0, 26, _PV_MAIN),
                           (52, 0.90, 25, _PV_SIDE), (110, 0.60, 22, [(0.0, 1.0)])],
                    sinus=[0.42, 0.55, 0.55, 0.42], base=0.08, vein=0.48, hub=0.06),
    # small green: three-lobed ivy (10)
    "ivy3": dict(lobes=[(-72, 0.82, 36, [(-0.70, 0.64), (0.0, 1.0)]),
                        (0, 1.0, 32, [(-0.66, 0.64), (0.0, 1.0), (0.66, 0.64)]),
                        (72, 0.82, 36, [(0.0, 1.0), (0.70, 0.64)])],
                 sinus=[0.63, 0.63], base=0.18, vein=0.48, hub=0.08),
}


def _outline(kind):
    """[(x, y)] (unit R, base sinus first, counter-clockwise), [(tag, lobe)] per point, lobes."""
    k = KINDS[kind]
    lobes = k["lobes"]
    pts = [(-1.0 * k["base"], 0.0)]
    tags = [("s", -1)]
    for i, (ang, ln, hs, prof) in enumerate(lobes):
        for f, rf in prof:
            th = math.radians(ang + f * hs)
            pts.append((math.cos(th) * ln * rf, math.sin(th) * ln * rf))
            tags.append(("l", i))
        if i < len(lobes) - 1:
            th = math.radians((ang + hs + lobes[i + 1][0] - lobes[i + 1][2]) / 2)
            r = k["sinus"][i]
            pts.append((math.cos(th) * r, math.sin(th) * r))
            tags.append(("s", i))
    return pts, tags, lobes


def _inset(pts, c):
    """Inward 2D offset of a counter-clockwise polygon by c (mitred, the miter clamped to 2.6 c)."""
    n = len(pts)
    out = []
    for i in range(n):
        p, v, q = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        e1, e2 = (v - p).normalized(), (q - v).normalized()
        n1, n2 = Vector((-e1.y, e1.x)), Vector((-e2.y, e2.x))
        b = n1 + n2
        if b.length < 1e-6:
            b = n1
        b.normalize()
        m = min(2.6 * c, c / max(0.25, b.dot(n1)))
        out.append(v + b * m)
    return out


def _area2(a, b, c):
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)


def leaf_shell(a, kind, span, thick, cham, cup, fold, droop, roles, curl=None, seed=0, scale_y=1.0):
    """One leaf as a closed solid in its own frame (petiole hub near the origin, main tip along +X, resting on z 0):
    a flat-bottomed slab whose top is a hub vert plus one raised vein vert per lobe, every lobe folding into facets
    along its midrib, lobe flanks drooping (the fold) and tips rising (the cup); a chamfer ring (cham > 0) from the top
    down to a vertical side band. Colour is painted by radial band from the hub (role(frac, where) -> key), never by
    facing. span: the leaf's width across the lobes. Returns (verts, info)."""
    raw, tags, lobes = _outline(kind)
    k = KINDS[kind]
    ys = [p[1] for p in raw]
    R = span / ((max(ys) - min(ys)) * scale_y)
    P = [Vector((x * R, y * R * scale_y)) for x, y in raw]
    n = len(P)
    lob_ang = [math.radians(l[0]) for l in lobes]
    lob_hs = [math.radians(l[2]) for l in lobes]
    lob_len = [l[1] * R for l in lobes]
    curl = curl or {}

    def lobe_of(p):
        th = math.atan2(p.y / scale_y, p.x)
        best, bi = 9.0, 0
        for i, (ang, hs) in enumerate(zip(lob_ang, lob_hs)):
            d = abs((th - ang + math.pi) % (2 * math.pi) - math.pi) / hs
            if d < best:
                best, bi = d, i
        return bi, best

    def zf(p):
        i, d = lobe_of(p)
        r = p.length / R
        z = cup * r * r - droop * min(1.0, d) * min(1.0, p.length / lob_len[i])
        if i in curl:
            rr = p.length - 0.45 * lob_len[i]
            if rr > 0:
                z += rr * math.tan(math.radians(curl[i]))
        return z

    T2 = _inset(P, cham) if cham > 0 else [p.copy() for p in P]
    hub2 = Vector((k["hub"] * R, 0.0))
    # lobe ranges [a, b] between sinus points (indices into the ring; b may be n = the base sinus again)
    sinus_idx = [i for i, t in enumerate(tags) if t[0] == "s"]
    ranges = []
    for i in range(len(lobes)):
        aa = sinus_idx[i]
        bb = sinus_idx[i + 1] if i + 1 < len(sinus_idx) else n
        ranges.append((aa, bb))
    # one vein vert per lobe at `vein` x its length; pulled toward the hub until its fan has no folded triangle
    vein2, bad = [], 0
    for i, (aa, bb) in enumerate(ranges):
        fr = k["vein"]
        while True:
            v2 = Vector((math.cos(lob_ang[i]), math.sin(lob_ang[i]) * scale_y)) * (fr * lob_len[i])
            nb = sum(1 for j in range(aa, bb) if _area2(v2, T2[j % n], T2[(j + 1) % n]) <= 1e-6)
            nb += _area2(hub2, T2[aa % n], v2) <= 1e-6
            nb += _area2(hub2, v2, T2[bb % n]) <= 1e-6
            if nb == 0 or fr < 0.2:
                break
            fr -= 0.03
        bad += nb
        vein2.append(v2)
    bm = a.bm
    zb = [zf(p) for p in P]
    B = [bm.verts.new((p.x, p.y, z)) for p, z in zip(P, zb)]
    S = [bm.verts.new((p.x, p.y, z + thick - (0.45 * thick if cham > 0 else 0.0))) for p, z in zip(P, zb)]
    T = [bm.verts.new((p.x, p.y, zf(p) + thick)) for p in T2] if cham > 0 else S
    H = bm.verts.new((hub2.x, hub2.y, thick + 0.4 * fold))
    V = [bm.verts.new((v.x, v.y, zf(v) + thick + fold)) for v in vein2]
    side = [bm.faces.new((B[j], B[(j + 1) % n], S[(j + 1) % n], S[j])) for j in range(n)]
    chamf = [bm.faces.new((S[j], S[(j + 1) % n], T[(j + 1) % n], T[j])) for j in range(n)] if cham > 0 else []
    top_seg = {}
    hubf = []
    for i, (aa, bb) in enumerate(ranges):
        for j in range(aa, bb):
            top_seg[j % n] = bm.faces.new((V[i], T[j % n], T[(j + 1) % n]))
        hubf.append(bm.faces.new((H, T[aa % n], V[i])))
        hubf.append(bm.faces.new((H, V[i], T[bb % n])))
    bot = bm.faces.new(list(reversed(B)))
    res = bmesh.ops.triangulate(bm, faces=[bot], quad_method="BEAUTY", ngon_method="BEAUTY")
    botf = res["faces"]
    vs = B + (S if True else []) + (T if cham > 0 else []) + [H] + V
    vs = list(dict.fromkeys(vs))
    allf = side + chamf + list(top_seg.values()) + hubf + botf
    rng = random.Random(seed)
    _close(a, vs, allf, roles(0.5, "seg"), tint=1.0 + rng.uniform(-0.03, 0.03))
    # radial bands: segment j of the outline (its top fan triangle, chamfer quad and side quad) by the mean radius of
    # its two outline points as a fraction of its lobe's length; hub triangles the base band; bottom by centroid
    seg_frac = []
    for j in range(n):
        p, q = P[j], P[(j + 1) % n]
        i, _ = lobe_of((p + q) / 2)
        seg_frac.append(((p.length + q.length) / 2) / lob_len[i])
    band_tint = {}
    for j in range(n):
        key = roles(seg_frac[j], "seg", lobe_of((P[j] + P[(j + 1) % n]) / 2)[0])
        fs = [side[j], top_seg[j]] + ([chamf[j]] if chamf else [])
        _paint(a, fs, key)
        t = band_tint.setdefault(key, 1.0 + rng.uniform(-0.02, 0.02))
        _tint(a, fs, t)
    _paint(a, hubf, roles(0.1, "hub"))
    for f in botf:
        c = f.calc_center_median()
        p2 = Vector((c.x, c.y))
        i, _ = lobe_of(p2)
        key = roles(p2.length / lob_len[i], "bot", i)
        _paint(a, [f], key)
        _tint(a, [f], band_tint.get(key, 1.0))
    # rest on z 0
    _move(vs, (0, 0, -_zmin(vs)))
    cols = [[B[j], S[j]] + ([T[j]] if cham > 0 else []) for j in range(n)] + [[H]] + [[v] for v in V]
    info = {"kind": kind, "R": round(R, 3), "outline": n, "bad_fans": bad, "thick": thick, "cols": cols,
            "span": round(max(p.y for p in P) - min(p.y for p in P), 3),
            "length": round(max(p.x for p in P) - min(p.x for p in P), 3),
            "rear_x": round(min(p.x for p in P), 3), "notch_x": round(-k["base"] * R, 3),
            "tip_x": round(max(p.x for p in P), 3), "tip_lift": round(max(zb) - min(zb), 3)}
    return vs, info


def petiole_shell(a, p0, p1, r0, r1, key, seed=0):
    """A 5-sided tapered prism from p0 (inside the leaf) to p1: 16 tris."""
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0).normalized()
    s = Vector((0, 0, 1)).cross(d)
    if s.length < 1e-4:
        s = Vector((1, 0, 0))
    s.normalize()
    u = d.cross(s).normalized()
    bm = a.bm
    r0v = [bm.verts.new(p0 + (s * math.cos(k * 2 * math.pi / 5 + 0.3) + u * math.sin(k * 2 * math.pi / 5 + 0.3)) * r0)
           for k in range(5)]
    r1v = [bm.verts.new(p1 + (s * math.cos(k * 2 * math.pi / 5 + 0.3) + u * math.sin(k * 2 * math.pi / 5 + 0.3)) * r1)
           for k in range(5)]
    fs = m047._band(bm, r0v, r1v) + [bm.faces.new(list(reversed(r0v))), bm.faces.new(r1v)]
    vs = r0v + r1v
    _close(a, vs, fs, key, tint=1.0 + random.Random(seed).uniform(-0.03, 0.03))
    return vs


# leaf roles (spec 5.3): role(frac, where, lobe) -> key
def _role_big(frac, where, lobe=None):
    if where == "hub" or frac < 0.30:
        return DEEP
    if frac < 0.42:
        return _mix(DEEP, GREEN, 0.5)
    if frac < 0.70:
        return GREEN
    if frac < 0.80:
        return _mix(GREEN, LIME, 0.5)
    return LIME


def _role_orange(inner):
    def r(frac, where, lobe=None):
        if inner:                        # O1: inner 0-0.30 L blended to rust (spec 3.7)
            if where == "hub":
                return _mix(ORANGE, RUST, 0.75)
            if frac < 0.30:
                return _mix(ORANGE, RUST, 0.5)
            if frac < 0.42:
                return _mix(ORANGE, RUST, 0.25)
            return ORANGE
        if where == "hub":
            return _mix(ORANGE, RUST, 0.25)
        return ORANGE
    return r


def _role_rust(curled):
    def r(frac, where, lobe=None):
        if where == "hub":
            return _mix(RUST, WOOD, 0.25)
        if lobe in curled and frac > 0.7:
            return _mix(RUST, WOOD, 0.5)
        return RUST
    return r


def _role_yellow(frac, where, lobe=None):
    # fix round 1: the amber / olive centre covered about half the leaf (a mustard centre); now an amber hub and a
    # thin amber -> yellow band inside 0.30 of each lobe, the rest yellow (the cell's #F0BE40). The hub triangles run
    # from the hub out to the sinuses and the vein verts, a big share of the top, so they take the half step only.
    if where == "hub":
        return _mix(AMBER, YELLOW, 0.5)
    if frac < 0.18:
        return AMBER
    if frac < 0.30:
        return _mix(AMBER, YELLOW, 0.5)
    return YELLOW


def _role_small(body, base, base_t=1.0):
    def r(frac, where, lobe=None):
        if where == "hub" or frac < 0.35:
            return _mix(body, base, base_t)
        if frac < 0.5:
            return _mix(body, base, base_t * 0.5)
        return body
    return r


# name -> part kind, centre (x, y), span across the lobes, tip az, thickness, chamfer, cup, fold, droop, roles, petiole
# (length, rise deg, key) or None, curl {lobe: deg}, seed. Spec 2.2.
LEAVES = {
    # L1 (fix round 1): 0.06 left / forward and turned 12 deg so its right side lobe no longer holds T1's front end
    # up; T1 now comes down onto the ground at that end
    "L1": dict(kind="large", c=(0.88, -0.90), span=2.20, az=308.0, thick=0.08, cham=0.024, cup=0.05, fold=0.05,
               droop=0.06, roles=_role_big, pet=(0.30, 12.0, DEEP), seed=62101),
    "L2": dict(kind="large", c=(-1.25, 0.95), span=1.96, az=140.0, thick=0.08, cham=0.022, cup=0.045, fold=0.05,
               droop=0.055, roles=_role_big, pet=(0.26, 0.0, DEEP), seed=62102),
    "O1": dict(kind="maple", c=(-1.12, -0.94), span=1.68, az=225.0, thick=0.07, cham=0.022, cup=0.045, fold=0.045,
               droop=0.05, roles=_role_orange(True), pet=(0.24, 0.0, (ORANGE, RUST, 0.75)), seed=62103),
    # O2 (fix round 1): its main-lobe tip on the ground behind T1 at c, tip toward the back (az), the base end lifted
    # onto T1 so its top face turns to the front cameras; no petiole (spec 2.2 lists none for O2)
    "O2": dict(kind="maple", c=(0.03, 1.83), span=1.15, az=80.0, thick=0.07, cham=0.02, cup=0.035, fold=0.04,
               droop=0.04, roles=_role_orange(False), pet=None, seed=62104),
    "V1": dict(kind="variant", c=(0.64, 0.44), span=1.36, az=20.0, thick=0.07, cham=0.02, cup=0.04, fold=0.04,
               droop=0.045, roles=_role_rust((0, 4)), pet=None, curl={0: 16.0, 4: 18.0}, seed=62105),
    "Y1": dict(kind="maple_small", c=(-1.92, 0.62), span=0.86, az=160.0, thick=0.06, cham=0.018, cup=0.03, fold=0.032,
               droop=0.035, roles=_role_yellow, pet=(0.15, 0.0, OLIVE), seed=62106),
    "Y2": dict(kind="maple_small", c=(0.48, 1.36), span=0.86, az=70.0, thick=0.06, cham=0.018, cup=0.03, fold=0.032,
               droop=0.035, roles=_role_yellow, pet=(0.15, 0.0, OLIVE), seed=62107),
    "G1": dict(kind="ivy3", c=(-0.20, -1.48), span=0.80, az=265.0, thick=0.06, cham=0.0, cup=0.03, fold=0.03,
               droop=0.03, roles=_role_small(PALE, OLIVE, 0.5), pet=None, seed=62108),
    "G2": dict(kind="ivy3", c=(-1.93, -0.32), span=0.78, az=190.0, thick=0.06, cham=0.0, cup=0.03, fold=0.03,
               droop=0.03, roles=_role_small(LIME, GREEN, 1.0), pet=None, seed=62109),
    "G3": dict(kind="ivy3", c=(1.74, 0.42), span=0.70, az=350.0, thick=0.06, cham=0.0, cup=0.03, fold=0.03,
               droop=0.03, roles=_role_small(GREEN, DEEP, 1.0), pet=None, seed=62110),
}
LEAF_INFO = {}


def leaf_local(a, name):
    """A leaf in its own frame plus its petiole stub (both resting on z 0); returns (leaf verts, petiole verts, info,
    petiole start in the leaf frame)."""
    s = LEAVES[name]
    vs, info = leaf_shell(a, s["kind"], s["span"], s["thick"], s["cham"], s["cup"], s["fold"], s["droop"], s["roles"],
                          curl=s.get("curl"), seed=s["seed"])
    return vs, info


def place_leaf(a, pile, name, sup_names=(), avoid=None, at=None, az=None):
    """Build leaf `name`, turn it to its tip azimuth, centre it on its plan point and settle it on the ground / the
    leaves under it; if it cuts into a stone or the pinecone (avoid: a _Solids) by more than 0.02, shift it away and
    retry. Its petiole (if any) is a stub along -X from the base, built here in the leaf frame."""
    s = LEAVES[name]
    vs, info = leaf_local(a, name)
    pet_vs = []
    pet0 = None
    if s.get("pet"):
        L, rise, key = s["pet"]
        key = _mix(*key) if isinstance(key, tuple) else key
        rear = info["rear_x"]
        th = s["thick"]
        # fix round 1: the stem starts inside the leaf base, PET_SEAT behind the base notch (for `large` / `maple` the
        # outline's rear_x is the basal-lobe tips, so a start at rear_x left the stem loose in the open notch), and
        # runs back between the basal lobes to L past them
        p0 = Vector((info["notch_x"] + PET_SEAT, 0.0, th * 0.55))
        p1 = Vector((rear - L * math.cos(math.radians(rise)), 0.0, th * 0.55 + L * math.sin(math.radians(rise))))
        r0 = 0.05 if s["span"] > 1.2 else 0.04
        pet_vs = petiole_shell(a, p0, p1, r0, r0 * 0.7, key, seed=s["seed"] + 1)
        pet0 = p0
    allv = vs + pet_vs
    groups = info.pop("cols") + ([pet_vs] if pet_vs else [])
    rot = Matrix.Rotation(math.radians(az if az is not None else s["az"]), 4, "Z")
    _xform(allv, rot)
    cx = (min(v.co.x for v in vs) + max(v.co.x for v in vs)) / 2
    cy = (min(v.co.y for v in vs) + max(v.co.y for v in vs)) / 2
    tgt = Vector(at if at is not None else s["c"])
    _move(allv, (tgt.x - cx, tgt.y - cy, 0))
    info["moved"] = 0.0
    if pile is not None:
        sup = pile.vs(names=sup_names)
        z0 = {v: v.co.z for v in allv}
        for attempt in range(16):
            for slope in (0.45, 0.32, 0.22, 0.15):
                for v in allv:                # each try drapes the leaf's own shape afresh
                    v.co.z = z0[v]
                dz, what = _drape(allv, sup, groups=groups, slope=slope)
                if what == "ground":
                    break
                # no support point more than 0.025 inside the draped leaf (its big faces span the columns)
                me = m047._Solids()
                me.add_vs(vs, "me")
                lo = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs)))
                hi = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs)))
                inside = max([me.point(q)[0] for q in _samples(sup) if lo.x <= q.x <= hi.x and lo.y <= q.y <= hi.y]
                             or [0.0])
                if inside <= 0.025:
                    break
            info["drape_slope"] = slope
            depth, who = (0.0, None)
            if avoid is not None:
                for p in _samples(vs):
                    d_, w_ = avoid.point(p)
                    if d_ > depth:
                        depth, who = d_, w_
            info.update(dz=dz, rests_on=what, depth=round(depth, 3), cut=who)
            if depth <= 0.035 or attempt == 15:
                break
            # away from the solid it cuts into
            c = _centre(vs)
            lo, hi = next((it[1], it[2]) for it in avoid.items if it[0] == who)
            far = (lo + hi) / 2
            d = Vector((c.x - far.x, c.y - far.y, 0))
            d = d.normalized() if d.length > 1e-6 else Vector((1, 0, 0))
            _move(allv, d * 0.025)
            info["moved"] = round(info["moved"] + 0.025, 3)
        pile.add(name, "leaf", vs)
        if pet_vs:
            pile.add(name + "_pet", "petiole", pet_vs)
    info["centre"] = [round(x, 3) for x in _centre(vs)]
    info["pet0"] = [round(x, 3) for x in (rot @ pet0)] if pet0 is not None else None
    info.pop("cols", None)
    LEAF_INFO[name] = info
    return vs, pet_vs


# ---- twigs (spec 2.3: 8-sided chamfered square beams along a short spine, skewed flat cut caps, a knot) ------------
TWIGS = {
    # stations (fraction of L), lateral offsets (studs, the 6 deg kink), the knot station, end skews (deg)
    "T1": dict(p0=(-0.95, 1.62), p1=(2.05, -0.30), s=0.24, cham=0.045, st=(0.0, 0.07, 0.18, 0.44, 0.70, 0.93, 1.0),
               lat=(0.07, 0.055, 0.0, 0.0, 0.0, 0.0, 0.0), knot=2, skew=(7.0, -5.0), seed=62201),
    "T2": dict(p0=(-0.02, 0.10), p1=(0.90, 1.60), s=0.22, cham=0.042, st=(0.0, 0.08, 0.5, 0.92, 1.0),
               lat=(0.0, 0.0, 0.025, 0.0, 0.0), knot=None, skew=(-6.0, 8.0), seed=62202),
    "Ts": dict(p0=(0.42, 0.30), p1=(1.40, -0.10), s=0.17, cham=0.034, st=(0.0, 0.12, 0.5, 0.88, 1.0),
               lat=(0.0, 0.0, 0.015, 0.0, 0.0), knot=None, skew=(5.0, -7.0), seed=62203),
}
TWIG_INFO = {}


def twig_shell(a, C, s, cham, knot=None, skew=(0.0, 0.0), seed=0, end_keys=True):
    """A chamfered square beam through station centres C (build frame), one flat face down; flat octagon caps skewed
    a few degrees. Colour by position along the beam: wood body, the cap faces and the knot ring wood_light, the end
    bands one step toward it. Returns verts."""
    bm = a.bm
    n = len(C)
    seg = [(C[k + 1] - C[k]).normalized() for k in range(n - 1)]
    Tg = [seg[0]] + [(seg[k - 1] + seg[k]).normalized() for k in range(1, n - 1)] + [seg[-1]]
    h = s / 2
    q = [(h, h - cham), (h - cham, h), (-(h - cham), h), (-h, h - cham), (-h, -(h - cham)), (-(h - cham), -h),
         (h - cham, -h), (h, -(h - cham))]
    rings = []
    for k in range(n):
        t = Tg[k]
        side = Vector((0, 0, 1)).cross(t).normalized()
        up = t.cross(side).normalized()
        sc = 1.13 if k == knot else 1.0
        ring = []
        for x, y in q:
            p = C[k] + (side * x + up * y) * sc
            if k == 0:
                p += t * (y * math.tan(math.radians(skew[0])))
            elif k == n - 1:
                p += t * (y * math.tan(math.radians(skew[1])))
            ring.append(bm.verts.new(p))
        rings.append(ring)
    bands = [m047._band(bm, rings[k], rings[k + 1]) for k in range(n - 1)]
    cap0 = bm.faces.new(list(reversed(rings[0])))
    cap1 = bm.faces.new(rings[-1])
    vs = [v for r in rings for v in r]
    rng = random.Random(seed)
    _close(a, vs, [f for b in bands for f in b] + [cap0, cap1], WOOD, tint=1.0 + rng.uniform(-0.03, 0.03))
    _paint(a, [cap0, cap1], WOOD_L)
    if end_keys and n > 3:
        _paint(a, bands[0] + bands[-1], _mix(WOOD, WOOD_L, 0.25))
    if knot is not None:
        _paint(a, bands[knot - 1] + bands[knot], _mix(WOOD, WOOD_L, 0.25))
    for b in bands:                  # grain: a lengthwise Tint drift band to band
        _tint(a, b, 1.0 + rng.uniform(-0.02, 0.02))
    return vs


def _twig_axis(name):
    s = TWIGS[name]
    p0, p1 = Vector((*s["p0"], 0.0)), Vector((*s["p1"], 0.0))
    u = (p1 - p0).normalized()
    side = Vector((-u.y, u.x, 0.0))
    return p0, p1, u, side, (p1 - p0).length


def place_twig_ground(a, pile, name, sup_names, flat=False):
    """T1 / Ts: a twig lying on the ground and the leaves / twigs under it. Each station's bottom follows the highest
    support under its footprint (the bow and kink follow the litter), then the beam settles straight down."""
    s = TWIGS[name]
    p0, p1, u, side, L = _twig_axis(name)
    sup = pile.vs(names=sup_names) if pile is not None else []
    st = _tree(sup) if sup and not flat else None
    st_ = s["st"]

    def axis_at(f):
        k = max(0, min(len(st_) - 2, next((i for i in range(len(st_) - 1) if f <= st_[i + 1]), len(st_) - 2)))
        t = (f - st_[k]) / (st_[k + 1] - st_[k])
        return p0 + u * (f * L) + side * (s["lat"][k] * (1 - t) + s["lat"][k + 1] * t)
    # the support profile under the beam, every ~0.05 studs across its width
    nprof = max(8, int(L / 0.05))
    prof = []
    for i in range(nprof + 1):
        f = i / nprof
        c = axis_at(f)
        prof.append((f, _support_z(st, [c + side * (dx * s["s"] / 2) for dx in (-1.2, -0.6, 0.0, 0.6, 1.2)])))
    for v in sup:                             # and every support vert inside the beam's strip (thin lobe tips)
        q = v.co - p0
        f = q.dot(u) / L
        if 0.0 <= f <= 1.0 and abs(q.dot(side)) <= 0.62 * s["s"] and st is not None:
            prof.append((f, v.co.z))
    Z = [0.0] * len(st_)
    for f, z in prof:                         # each station at least its own footprint's height
        for k, fk in enumerate(st_):
            if abs(f - fk) < 0.5 / nprof + 1e-9:
                Z[k] = max(Z[k], z)
    for _ in range(40):                       # raise the two stations either side of any profile point above the chord
        moved = False
        for f, z in prof:
            k = max(0, min(len(st_) - 2, next((i for i in range(len(st_) - 1) if f <= st_[i + 1]), len(st_) - 2)))
            t = (f - st_[k]) / (st_[k + 1] - st_[k])
            dz_ = z - (Z[k] * (1 - t) + Z[k + 1] * t)
            if dz_ > 0.002:
                w0, w1 = 1 - t, t
                g = dz_ / (w0 * w0 + w1 * w1)
                Z[k] += g * w0
                Z[k + 1] += g * w1
                moved = True
        if not moved:
            break
    C = [axis_at(f) + Vector((0, 0, z + s["s"] / 2)) for f, z in zip(st_, Z)]
    # a stiff beam: an interior station sags at most 0.02 below the chord of its neighbours, an end bends down at most
    # 4 deg past its neighbour (no drooping cantilevers, no zigzag between the leaves it rests on)
    st_ = s["st"]
    for _ in range(6):
        for kk in range(1, len(C) - 1):
            f0, f1, f2 = st_[kk - 1], st_[kk], st_[kk + 1]
            chord = (C[kk - 1].z * (f2 - f1) + C[kk + 1].z * (f1 - f0)) / (f2 - f0)
            C[kk].z = max(C[kk].z, chord - 0.02)
        C[0].z = max(C[0].z, C[1].z - (st_[1] - st_[0]) * L * math.tan(math.radians(4.0)))
        C[-1].z = max(C[-1].z, C[-2].z - (st_[-1] - st_[-2]) * L * math.tan(math.radians(4.0)))
    vs = twig_shell(a, C, s["s"], s["cham"], knot=s["knot"], skew=s["skew"], seed=s["seed"])
    info = {"L": round(L, 3), "station_z": [round(c.z - s["s"] / 2, 3) for c in C]}
    if pile is not None:
        per = {}
        _move(vs, (0, 0, 1.0))
        for nm in sup_names:
            if nm in pile.p:
                c = _clear(vs, [v for v in pile.p[nm][1] if v.is_valid])
                if c is not None:
                    per[nm] = round(c - 1.0, 3)
        _move(vs, (0, 0, -1.0))
        info["clear_before"] = per
        info["zmin_before"] = round(_zmin(vs), 3)
        dz, what = _drop(vs, sup)
        info.update(dz=dz, rests_on=what)
        pile.add(name, "twig", vs)
    TWIG_INFO[name] = info
    return vs


def place_twig_lifted(a, pile, name, rest_names, foot_names=()):
    """T2: the lower end on the ground (or the leaf under it), the beam pitched up about that end until it comes down
    onto T1 (or T2's other supports): the first pitch that touches, pressed ~0.01 in."""
    s = TWIGS[name]
    p0, p1, u, side, L_plan = _twig_axis(name)
    L = 1.82
    sup_foot = pile.vs(names=foot_names) if foot_names else []
    ft = _tree(sup_foot) if sup_foot else None
    zfoot = _support_z(ft, [p0 + side * dx * s["s"] / 2 + u * dy for dx in (-0.9, 0.9) for dy in (0.0, 0.15)])
    rest = pile.vs(names=rest_names)
    rt = _tree(rest)

    def build(pitch):
        d = (u * math.cos(pitch) + Vector((0, 0, math.sin(pitch)))).normalized()
        upv = d.cross(Vector((0, 0, 1)).cross(d).normalized()).normalized()
        base = p0 + upv * (s["s"] / 2)
        C = [base + d * (f * L) + side * lat for f, lat in zip(s["st"], s["lat"])]
        vs = twig_shell(a, C, s["s"], s["cham"], knot=s["knot"], skew=s["skew"], seed=s["seed"])
        _move(vs, (0, 0, zfoot - PEN - _zmin(vs)))
        return vs

    lo, hi = math.radians(5.0), math.radians(60.0)
    vs = build(hi)
    if rt.overlap(_tree(vs)):
        raise RuntimeError(f"{name} hits its rest even at 60 deg")
    bmesh.ops.delete(a.bm, geom=vs, context="VERTS")
    for _ in range(22):
        mid = (lo + hi) / 2
        vs = build(mid)
        hit = bool(rt.overlap(_tree(vs)))
        bmesh.ops.delete(a.bm, geom=vs, context="VERTS")
        if hit:
            lo = mid
        else:
            hi = mid
    pitch = hi - 0.012                       # press ~0.01 into the twig it rests on (close-up 2: "let in")
    vs = build(pitch)
    TWIG_INFO[name] = {"L": L, "pitch_deg": round(math.degrees(pitch), 2), "foot_z": round(zfoot, 3),
                       "top_z": round(max(v.co.z for v in vs), 3)}
    pile.add(name, "twig", vs)
    return vs


def prop_leaf(a, pile, name, rest_names, sup_names=()):
    """O2: a maple fallen against the back of the twig X: its main-lobe tip rests on the ground behind T1 (az points
    to the back), and the leaf is tipped up about that tip until its base end lies on the twig (the first angle that
    touches). Its top face then looks toward the front cameras (fix round 1: tipped the other way it showed its edge)."""
    s = LEAVES[name]
    rt = _tree(pile.vs(names=rest_names))
    probe = {}

    def build(q):
        vs, info = leaf_local(a, name)
        info.pop("cols", None)
        pet = []
        allv = vs + pet
        tip = max(v.co.x for v in vs)
        _move(allv, (-tip, 0, 0))
        _xform(allv, Matrix.Rotation(q, 4, "Y"))           # lifts the base end (x < 0)
        _xform(allv, Matrix.Rotation(math.radians(s["az"]), 4, "Z"))
        # the tip on the plan point
        piv = Vector((*s["c"], 0.0))
        rp = min(vs, key=lambda v: v.co.z).co
        _move(allv, (piv.x - rp.x, piv.y - rp.y, -_zmin(allv) - 0.004))
        probe["info"] = info
        return vs, pet

    lo, hi = math.radians(4.0), math.radians(75.0)
    for _ in range(20):
        mid = (lo + hi) / 2
        vs, pet = build(mid)
        hit = bool(rt.overlap(_tree(vs)))
        bmesh.ops.delete(a.bm, geom=vs + pet, context="VERTS")
        if hit:
            lo = mid
        else:
            hi = mid
    q = hi - 0.015
    vs, pet = build(q)
    info = probe["info"]
    info.update(prop_deg=round(math.degrees(q), 1), tip_z=round(max(v.co.z for v in vs), 3),
                centre=[round(x, 3) for x in _centre(vs)])
    LEAF_INFO[name] = info
    pile.add(name, "leaf", vs)
    if pet:
        pile.add(name + "_pet", "petiole", pet)
    return vs


# ---- pinecone (spec 1.4: dark egg core + shingled lozenge scales, every scale rooted in the core) ------------------
# fix round 1: a rounded egg tip (the old core ended in a near-flat cone under a lifted crown ring + flat cap that read
# as a lid); 6 sides, since only the gaps between the scales show it
CORE_PROF = ((-0.02, 0.15), (0.15, 0.32), (0.38, 0.40), (0.60, 0.395), (0.75, 0.32), (0.85, 0.18))
CORE_TOP = 0.915
CORE_SIDES = 6
# scale rings, every one pointing down the egg like shingles, shrinking toward the apex: root position as an arc
# length from the apex down the profile (each ring's roots tuck under the tips of the ring above), count, tip lift
# off the surface, arc length L, W, thickness at the tip. Each plate is the chord from its root to its lifted tip, so
# it follows the egg's curve.
CONE_RINGS = ((0.115, 5, 0.025, 0.22, 0.27, 0.065), (0.275, 7, 0.03, 0.27, 0.32, 0.075),
              (0.455, 8, 0.035, 0.30, 0.36, 0.08), (0.645, 8, 0.035, 0.31, 0.37, 0.085),
              (0.84, 8, 0.035, 0.29, 0.35, 0.08), (1.03, 6, 0.025, 0.20, 0.29, 0.07))
# cap: small scales whose roots meet (and cross) at the apex, lying on the rounded tip and pointing down its slope
# (count, tip lift, arc L, W, thickness)
CONE_CAP = (4, 0.01, 0.18, 0.23, 0.045)
CONE_INFO = {}


def _core_r(z):
    pr = CORE_PROF
    if z <= pr[0][0]:
        return pr[0][1]
    for (z0, r0), (z1, r1) in zip(pr, pr[1:]):
        if z <= z1:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    z0, r0 = pr[-1]
    return max(0.02, r0 * (CORE_TOP - z) / (CORE_TOP - z0))


def cone_core(a):
    bm = a.bm
    rings = []
    n = CORE_SIDES
    for z, r in CORE_PROF:
        rings.append([bm.verts.new((math.cos((k + 0.5) * 2 * math.pi / n) * r, math.sin((k + 0.5) * 2 * math.pi / n) * r,
                                    z)) for k in range(n)])
    apex = bm.verts.new((0.0, 0.0, CORE_TOP))
    fs = [f for k in range(len(rings) - 1) for f in m047._band(bm, rings[k], rings[k + 1])]
    fs += [bm.faces.new((rings[-1][k], rings[-1][(k + 1) % n], apex)) for k in range(n)]
    fs.append(bm.faces.new(list(reversed(rings[0]))))
    vs = [v for r in rings for v in r] + [apex]
    _close(a, vs, fs, CONE_C, tint=1.0)
    return vs


def scale_shell(a, root, d, w, L, W, T, out=None, seed=0):
    """One closed scale (fix round 1: a flat shingle plate, not a pyramid): a lozenge outline (a narrow root, widest
    at 0.45 L, a blunt tip) whose flat top plane rises from the root to the tip, lifted T there along the scale's
    outward normal: a wedge, thin at its root and thick at its exposed end (7 verts, 10 tris). Colour by part of the
    plate: the flat top the scale colour, the rim and the inner face mid brown; the near-black gaps are the core
    (cone_core) showing between the plates."""
    m = d.cross(w).normalized()
    if m.dot(out if out is not None else Vector((root.x, root.y, 0.0))) < 0:
        m = -m
    bm = a.bm
    base = [root, root + d * (0.45 * L) - w * (W / 2), root + d * L, root + d * (0.45 * L) + w * (W / 2)]
    B = [bm.verts.new(p) for p in base]
    Tv = [bm.verts.new(base[1] + m * (0.45 * T)), bm.verts.new(base[2] + m * T - d * (0.25 * T)),
          bm.verts.new(base[3] + m * (0.45 * T))]
    top = [bm.faces.new((B[0], Tv[0], Tv[1])), bm.faces.new((B[0], Tv[1], Tv[2]))]
    rim = [bm.faces.new((B[1], B[2], Tv[1], Tv[0])), bm.faces.new((B[2], B[3], Tv[2], Tv[1])),
           bm.faces.new((B[0], B[1], Tv[0])), bm.faces.new((B[3], B[0], Tv[2]))]
    fb = bm.faces.new(list(reversed(B)))
    vs = B + Tv
    rng = random.Random(seed)
    _close(a, vs, top + rim + [fb], CONE_S, tint=1.0 + rng.uniform(-0.05, 0.05))
    _paint(a, rim + [fb], CONE_M)
    return vs


def _cone_pt(th, z, inset=0.0):
    """A point on the hexagonal core's surface at azimuth th and height z (the flats sit at cos 30 of the corner
    radius), pushed `inset` inward along the profile normal; and that normal."""
    n = CORE_SIDES
    dl = ((th + math.pi / n) % (2 * math.pi / n)) - math.pi / n          # angle from the nearest flat's normal
    k = math.cos(math.pi / n) / math.cos(dl)

    def rr(zz):
        return _core_r(zz) * k
    er = Vector((math.cos(th), math.sin(th), 0.0))
    dr = (rr(z + 0.01) - rr(z - 0.01)) / 0.02
    nrm = (er - Vector((0, 0, dr))).normalized()
    return er * rr(z) + Vector((0, 0, z)) - nrm * inset, nrm


def _z_at_arc(th, s):
    """The height on the core at azimuth th that lies an arc s down the profile from the apex."""
    zz, prev, arc = CORE_TOP, _cone_pt(th, CORE_TOP)[0], 0.0
    while arc < s and zz > -0.02:
        zz -= 0.003
        p = _cone_pt(th, zz)[0]
        arc += (p - prev).length
        prev = p
    return zz


def _scale_on_egg(th, z, L, lift, inset=0.02):
    """Root on the core at (th, z), 0.02 inside it; tip on the surface an arc L further down the profile (or, for
    the cap, from the apex), lifted `lift` off it: the plate is the chord, so it follows the egg's curve instead of
    sticking out of the rounded tip. Returns root, unit direction, chord length, outward normal at the tip."""
    root, _ = _cone_pt(th, z, inset)
    zz, prev, arc = z, _cone_pt(th, z)[0], 0.0
    while arc < L and zz > -0.02:
        zz -= 0.004
        p = _cone_pt(th, zz)[0]
        arc += (p - prev).length
        prev = p
    tip, nrm = _cone_pt(th, zz)
    tip = tip + nrm * lift
    d = tip - root
    return root, d.normalized(), d.length, nrm


def pinecone(a, pile=None, at=(-0.25, -0.45), lean=5.0, lean_az=45.0):
    """The core egg and its 40 scales (6 / 8 / 8 / 8 / 6 + a 4-scale cap), rings staggered by half a scale; every scale
    root 0.025 inside the core. Upright with a slight lean, foot sunk 0.02."""
    core = cone_core(a)
    scales = []
    for j, (s_root, n, lift, L, W, T) in enumerate(CONE_RINGS):
        ph = (j % 2) * math.pi / n + 0.21 + 0.37 * j
        for k in range(n):
            th = ph + 2 * math.pi * k / n
            z = _z_at_arc(th, s_root)
            ew = Vector((-math.sin(th), math.cos(th), 0.0))
            root, d, Lc, nrm = _scale_on_egg(th, z, L, lift)
            w = (ew - d * ew.dot(d)).normalized()
            vs = scale_shell(a, root, d, w, Lc, W, T, out=nrm, seed=6230 + j * 10 + k)
            scales.append(vs)
    # the cap: roots meeting at the apex (so no hole), each plate lying on the rounded tip and pointing down its slope
    n, lift, L, W, T = CONE_CAP
    for k in range(n):
        th = 2 * math.pi * k / n + 0.55
        er = Vector((math.cos(th), math.sin(th), 0.0))
        ew = Vector((-math.sin(th), math.cos(th), 0.0))
        root0, d0, L0, nrm = _scale_on_egg(th, CORE_TOP - 0.002, L, lift)
        tip = root0 + d0 * L0
        # just over the apex (a zero-thickness root seated in the core let the apex poke through as a hex hole), each
        # root 0.012 out on its own side; each plate spans ~110 deg at its root, so the four overlap over the apex
        root = Vector((0, 0, CORE_TOP + 0.002)) + er * 0.012
        d = tip - root
        w = (ew - d.normalized() * ew.dot(d.normalized())).normalized()
        vs = scale_shell(a, root, d.normalized(), w, d.length, W, T, out=nrm + Vector((0, 0, 0.5)), seed=6290 + k)
        scales.append(vs)
    allv = core + [v for s in scales for v in s]
    # bottom-ring tips must stay above the ground: lift so the lowest point is at -0.02 (the sunk foot)
    _move(allv, (0, 0, -0.02 - _zmin(allv)))
    ax = _u(lean_az + 90.0)
    _xform(allv, Matrix.Rotation(math.radians(lean), 4, ax))
    _move(allv, (at[0], at[1], -0.02 - _zmin(allv)))
    if pile is not None:
        pile.add("P_core", "core", core)
        for i, s in enumerate(scales):
            pile.add(f"P_s{i:02d}", "scale", s)
    xs = [v.co.x for v in allv]
    ys = [v.co.y for v in allv]
    CONE_INFO.update(width=round(max(max(xs) - min(xs), max(ys) - min(ys)), 3), top=round(max(v.co.z for v in allv), 3),
                     scales=len(scales))
    return core, scales


# ---- stones and chips (spec 2.4) -------------------------------------------------------------------------------------
ROCK_RINGS = ((0.0, 0.90, 6), (0.30, 1.0, 7), (0.70, 0.80, 6), (1.0, 0.42, 4))
SMALL_RINGS = ((0.0, 0.90, 5), (0.35, 1.0, 6), (0.75, 0.74, 5), (1.0, 0.38, 3))
STONES = {
    "S1": dict(c=(1.27, 0.92), size=(1.05, 0.89, 0.64), yaw=15.0, rings=ROCK_RINGS, seed=62501, slope=0.12),
    "S2": dict(c=(-1.64, -0.18), size=(0.80, 0.66, 0.54), yaw=-20.0, rings=SMALL_RINGS, seed=62502, slope=0.06),
}


def stone(a, pile, name, at=None):
    """A squat faceted warm-grey boulder: the hull of jittered rings (flat base sunk 0.02, broad sloping top higher
    toward the back-right). Colour by broad noise patches across facets (stone / stone_deep / a lighter mix), never
    by height or facing."""
    s = STONES[name]
    rng = random.Random(s["seed"])
    W, D, H = s["size"]
    pts = m033._ring_pts(rng, s["rings"], W / 2, D / 2, H, 0.08, lean=(rng.uniform(-0.08, 0.08), rng.uniform(-0.06, 0.06)))
    for p in pts:
        p.z += s["slope"] * (0.7 * p.x / (W / 2) + 0.7 * p.y / (D / 2)) * (p.z / H) * H
    m = Matrix.Rotation(math.radians(s["yaw"]), 3, "Z")
    c = at if at is not None else s["c"]
    pts = [m @ p + Vector((c[0], c[1], -0.02)) for p in pts]
    vs = m033._hull(a, pts, STONE)
    fs = _faces(vs)
    fld = K.noise_field(scale=2.4, seed=s["seed"])
    for f in fs:
        v = fld(f.calc_center_median())
        key = (_mix(STONE, STONE_D, 1.0) if v < -0.28 else _mix(STONE, STONE_D, 0.5) if v < -0.08 else
               _mix(STONE, WOOD_L, 0.0) if v < 0.25 else STONE)
        _paint(a, [f], key)
        _tint(a, [f], 1.0 + rng.uniform(-0.04, 0.04))
    if pile is not None:
        pile.add(name, "stone", vs)
    return vs


CHIPS = {
    "C1": dict(c=(-1.85, -0.70), size=(0.34, 0.17, 0.12), yaw=20.0, key=WOOD_D, seed=62601),
    "C2": dict(c=(-0.45, -1.05), size=(0.28, 0.16, 0.12), yaw=-30.0, key=WOOD_L, seed=62602),
    "C3": dict(c=(0.25, -0.95), size=(0.28, 0.15, 0.11), yaw=70.0, key=WOOD_D, seed=62603),
    "C4": dict(c=(-0.78, -0.35), size=(0.36, 0.14, 0.06), yaw=35.0, key=AMBER, seed=62604, frag=True),
}


def chip(a, pile, name, sup_names=(), avoid=None):
    """A small faceted wood block with one or two chamfered corners (C4: a flat broken leaf fragment), settled on the
    ground / the leaf under it."""
    s = CHIPS[name]
    rng = random.Random(s["seed"])
    L, W, H = s["size"]
    if s.get("frag"):
        out = [(-0.5, -0.3), (-0.2, -0.5), (0.35, -0.42), (0.5, 0.05), (0.15, 0.5), (-0.4, 0.35)]
        pts = [Vector((x * L, y * W * 2 * 0.5, z)) for x, y in out for z in (0.0, H)]
    else:
        pts = []
        for x in (-0.5, 0.5):
            for y in (-0.5, 0.5):
                for z in (0.0, 1.0):
                    pts.append(Vector((x * L * (1 + rng.uniform(-0.08, 0.08)), y * W * (1 + rng.uniform(-0.08, 0.08)),
                                       z * H * (1 + rng.uniform(-0.1, 0.1)))))
        # chamfer one top corner: replace it with three points pulled in
        k = rng.randrange(4) * 2 + 1
        p = pts.pop(k)
        cut = 0.32
        pts += [p + Vector((-math.copysign(cut * L, p.x), 0, 0)), p + Vector((0, -math.copysign(cut * W, p.y), 0)),
                p + Vector((0, 0, -cut * H * 1.4))]
    m = Matrix.Rotation(math.radians(s["yaw"]), 3, "Z")
    pts = [m @ p + Vector((s["c"][0], s["c"][1], 0.0)) for p in pts]
    vs = m033._hull(a, pts, s["key"])
    _tint(a, _faces(vs), 1.0 + rng.uniform(-0.03, 0.03))
    info = {}
    if pile is not None:
        sup = pile.vs(names=sup_names)
        # fix round 1: a rigid chip dropped onto a leaf balanced on a lobe edge with most of its underside hanging
        # (C1-C3 hung 0.10-0.16). Each chip now lies flat on bare ground: the nearest spot to its plan point (rings
        # of 0.04, 16 directions) with no leaf under its footprint and no cut into a stone or the pinecone.
        c0 = _centre(vs)
        best = None
        for ring in range(0, 13):
            r = 0.04 * ring
            for k in range(1 if ring == 0 else 16):
                d = Vector((math.cos(k * math.pi / 8), math.sin(k * math.pi / 8), 0.0)) * r
                _move(vs, d)
                _move(vs, (0, 0, -_zmin(vs) - PEN))
                under = _clear(vs, sup) if sup else None
                depth = avoid.depth(vs) if avoid is not None else 0.0
                _move(vs, -d)
                if under is None and depth <= 0.005:
                    best = d
                    break
            if best is not None:
                break
        if best is None:
            best = Vector()
        _move(vs, best)
        dz, what = _drop(vs, sup)
        depth = avoid.depth(vs) if avoid is not None else 0.0
        info = {"rests_on": what, "depth": round(depth, 3), "moved": round(best.length, 3),
                "centre": [round(x, 3) for x in _centre(vs)]}
        pile.add(name, "chip", vs)
    CHIP_INFO[name] = info
    return vs


CHIP_INFO = {}


# ---- assemblies ------------------------------------------------------------------------------------------------------
EXPLODE = {"on": False}
LEAF_NAMES = tuple(LEAVES)
GROUND_LEAVES = ("Y1", "Y2", "L1", "L2", "O1", "V1", "G1", "G2", "G3")
EXPL = {  # exploded shot offsets (spec 4.1 step 8)
    "twigs": (0.0, 0.0, 0.8), "S1": (0.45, 0.4, 0.0), "S2": (-0.55, -0.1, 0.0)}


def hero_all(a):
    LEAF_INFO.clear()
    TWIG_INFO.clear()
    CHIP_INFO.clear()
    CONE_INFO.clear()
    pile = Pile()
    pinecone(a, pile)
    for k in STONES:
        stone(a, pile, k)
    avoid = pile.solids(kinds=("core", "scale", "stone"))
    placed = []
    for k in GROUND_LEAVES:
        place_leaf(a, pile, k, sup_names=tuple(placed), avoid=avoid)
        placed.append(k)
    for k in CHIPS:
        chip(a, pile, k, sup_names=tuple(placed), avoid=avoid)
    place_twig_ground(a, pile, "Ts", sup_names=("V1", "L1", "Y2", "L2"))
    place_twig_ground(a, pile, "T1", sup_names=("L2", "V1", "Y2", "L1", "O1"))
    place_twig_lifted(a, pile, "T2", rest_names=("T1",), foot_names=("V1", "Ts", "L2", "Y2"))
    prop_leaf(a, pile, "O2", rest_names=("T1", "T2"))
    _aim_petiole(a, pile, "L1")
    if EXPLODE["on"]:
        _explode(pile)
    PILE["last"] = pile
    return pile


PILE = {}


def _aim_petiole(a, pile, name):
    """L1's petiole: from its leaf base up to the pinecone's right foot, ending 0.01 inside the first surface it meets
    (spec 2.2: rises 10-15 deg onto P's foot)."""
    if name + "_pet" not in pile.p:
        return
    old = pile.p[name + "_pet"][1]
    p0 = (old[0].co + old[1].co + old[2].co + old[3].co + old[4].co) / 5
    bmesh.ops.delete(a.bm, geom=[v for v in old if v.is_valid], context="VERTS")
    del pile.p[name + "_pet"]
    cone = pile.vs(kinds=("core", "scale"))
    ct = _tree(cone)
    core_c = _centre(pile.vs(names=("P_core",)))
    tgt = Vector((core_c.x, core_c.y, 0.12))
    d = (tgt - p0).normalized()
    h = ct.ray_cast(p0, d, 5.0)
    p1 = h[0] + d * 0.012 if h[0] is not None else tgt
    if (p1 - p0).length > 0.95:              # fix round 1: p0 is now inside the leaf base, so the stem is longer
        p1 = p0 + d * 0.95
    vs = petiole_shell(a, p0, p1, 0.05, 0.036, DEEP, seed=62199)
    pile.add(name + "_pet", "petiole", vs)
    LEAF_INFO[name]["petiole_len"] = round((p1 - p0).length, 3)
    LEAF_INFO[name]["petiole_rise_deg"] = round(math.degrees(math.asin(max(-1, min(1, d.z)))), 1)


def _explode(pile):
    for n, (k, vs) in pile.p.items():
        if k == "twig" or n == "O2" or n == "O2_pet":
            _move(vs, EXPL["twigs"])
        elif n in EXPL:
            _move(vs, EXPL[n])
        elif k in ("leaf", "petiole", "chip"):
            base = n.split("_")[0]
            c = _centre(pile.p[base][1]) if base in pile.p else _centre(vs)
            d = Vector((c.x + 0.07, c.y + 0.05, 0))
            if d.length > 1e-3:
                _move(vs, d.normalized() * 0.45)


# parts: the hero's pieces alone (positions do not matter: the object is recentred)
def part_leaf(name, az=10.0):
    def fn(a):
        place_leaf(a, None, name, at=(0.0, 0.0), az=az)
    return fn


def part_twig(name, L=None):
    def fn(a):
        s = TWIGS[name]
        p0, p1, u, side, Lp = _twig_axis(name)
        L_ = L or Lp
        d = _u(20.0)
        sd = Vector((-d.y, d.x, 0))
        C = [d * (f * L_) + sd * lat + Vector((0, 0, s["s"] / 2)) for f, lat in zip(s["st"], s["lat"])]
        twig_shell(a, C, s["s"], s["cham"], knot=s["knot"], skew=s["skew"], seed=s["seed"])
    return fn


def part_cone(a):
    pinecone(a, None, at=(0.0, 0.0), lean=0.0)


def part_stone(name):
    def fn(a):
        stone(a, None, name, at=(0.0, 0.0))
    return fn


NOTES = {
    HERO: "Forest litter pile: two big green lobed leaves, orange maples (one propped on the long twig), a rust maple, "
          "two yellow maples, three small green leaves, two square twigs crossed in an X with a small twig under them, "
          "one shingled pinecone, two warm-grey stones, four chips. Walk-through floor dressing (collision none). "
          "Sheet page 64/132.",
    LEAF_L_P: "Leaf (large): five-lobed bright green slab with lobe folds, deep base, lime tips, petiole",
    LEAF_M_P: "Leaf (medium): orange five-lobed toothed maple slab with a rust inner band and petiole",
    LEAF_S_P: "Leaf (small): yellow maple slab, amber / olive base, short petiole",
    LEAF_V_P: "Leaf (variant): rust-brown jagged maple slab, two lobes curled up",
    TWIG_L_P: "Twig (large): chamfered square-section beam, knot, skewed flat cut ends",
    TWIG_S_P: "Twig (small): chamfered square-section beam",
    CONE_P: "Pinecone: upright egg of 40 shingled lozenge scales on a dark core",
    STONE_L_P: "Ground Stone (large): squat faceted warm-grey boulder",
    STONE_S_P: "Ground Stone (small): faceted warm-grey stone",
}
COLLISION = {HERO: "none", LEAF_L_P: "none", LEAF_M_P: "none", LEAF_S_P: "none", LEAF_V_P: "none", TWIG_L_P: "none",
             TWIG_S_P: "none", CONE_P: "none", STONE_L_P: "hull", STONE_S_P: "none"}


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
    ret = fn(a)
    pieces = None
    if isinstance(ret, Pile):
        pieces = [[n, k, *[round(x, 4) for x in _centre([v for v in vs if v.is_valid])]] for n, (k, vs) in ret.p.items()]
    o = a.finish(collection=M.coll(NUM, TITLE), mark_asset=not temp, origin=None)
    K.drop_unused_slots(o)
    if not temp:
        K.tag(o, SHEET, TITLE, role, COLLISION[name], budget, NOTES[name])
    o[OFF] = [0.0, 0.0, 0.0]
    if pieces:
        o["m062_pieces"] = json.dumps(pieces)
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


def _make(name, fn, role="part", budget=1000, temp=False):
    t0 = time.time()
    o = _new(name, fn, role, budget, temp=temp)
    lg = _post(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


# ---- checks ----------------------------------------------------------------------------------------------------------
def _shells(o):
    """bm, groups of faces per shell, piece name and kind per shell (matched by vertex centroid to the pieces the
    builder recorded; a part without a record is one piece of its own)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    groups = [[] for _ in range(n)]
    for f in bm.faces:
        groups[ids[f.index]].append(f)
    off = Vector(o.get(OFF, (0, 0, 0)))
    pieces = json.loads(o["m062_pieces"]) if "m062_pieces" in o else []
    names, kinds = [], []
    for fs in groups:
        vs = list({v for f in fs for v in f.verts})
        c = sum((v.co for v in vs), Vector()) / len(vs) + off
        if pieces:
            best = min(pieces, key=lambda p: (Vector(p[2:5]) - c).length)
            names.append(best[0])
            kinds.append(best[1])
        else:
            names.append(o.name)
            kinds.append("part")
    return bm, groups, names, kinds


def shells_report(o):
    """Per shell: piece, kind, tris, non-manifold edges and verts, boundary edges, winding errors (manifold edges whose
    two faces don't run the same way round), self-intersecting face pairs, signed volume."""
    bm, groups, names, kinds = _shells(o)
    out = []
    for k, fs in enumerate(groups):
        es = {e for f in fs for e in f.edges}
        vs = list({v for f in fs for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        hits = sum(1 for a_, b_ in tree.overlap(tree) if a_ < b_ and not set(fs[a_].verts) & set(fs[b_].verts))
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) / 3.0
        out.append({"piece": names[k], "kind": kinds[k], "tris": len(fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary),
                    "winding_errors": sum(1 for e in es if e.is_manifold and not e.is_contiguous),
                    "self_hits": hits, "volume": round(vol, 5), "zmin": round(min(v.co.z for v in vs), 3)})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating pieces (STAGES): per shell, whether it touches another shell (triangles intersect, or a vertex
    within `tol` of another shell's surface) or the ground (its lowest point within `tol` of z 0 in the build frame),
    and whether it chains by contact to the ground. Also the named rests the spec requires (T2 on T1, O2 on a twig,
    every pinecone scale on the core or another scale)."""
    bm, groups, names, kinds = _shells(o)
    n = len(groups)
    fsh = {}
    for k, fs in enumerate(groups):
        for f in fs:
            fsh[f.index] = k
    vsh = {}
    for k, fs in enumerate(groups):
        for f in fs:
            for v in f.verts:
                vsh[v.index] = k
    tree = BVHTree.FromBMesh(bm)
    off_z = o.get(OFF, (0, 0, 0))[2]
    zmin = [min(v.co.z for f in fs for v in f.verts) + off_z for fs in groups]
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
    gap = [1e9] * n
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    ground = {k for k in range(n) if zmin[k] <= tol}
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
        return [names[k] for k in range(n) if k not in seen]

    def touch(a_name, b_names):
        ia = [k for k in range(n) if names[k] == a_name]
        ib = [k for k in range(n) if names[k] in b_names]
        best = min((near.get((min(i, j), max(i, j)), 1e9) for i in ia for j in ib), default=None)
        return None if best is None else round(best, 4)
    floating = [k for k in range(n) if gap[k] > tol]
    rests = {}
    if "T2" in names:
        rests["T2_on_T1"] = touch("T2", ("T1",))
    if "O2" in names:
        rests["O2_on_twig"] = touch("O2", ("T1", "T2"))
    if "L1_pet" in names:
        rests["L1_petiole_on_cone"] = touch("L1_pet", tuple(nm for nm in names if nm.startswith("P_")))
    if "Ts" in names:
        rests["Ts_on"] = sorted({names[j] for (i, j), d in near.items() if d <= tol and names[i] == "Ts"} |
                                {names[i] for (i, j), d in near.items() if d <= tol and names[j] == "Ts"})
    scl = [k for k in range(n) if kinds[k] == "scale"]
    cone_idx = [k for k in range(n) if kinds[k] in ("core", "scale")]
    loose_scales = [names[k] for k in scl
                    if min(near.get((min(k, j), max(k, j)), 1e9) for j in cone_idx if j != k) > tol]
    out_unch = chained(tol)
    res = {"shells": n, "floating": len(floating), "floating_pieces": sorted(names[k] for k in floating),
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "unchained": len(out_unch), "unchained_pieces": out_unch[:10],
           "unchained_chain_tol": len(chained(chain_tol)), "on_ground": len(ground),
           "sink": round(min(zmin), 3), "kinds": {k: kinds.count(k) for k in sorted(set(kinds))},
           "rests": rests, "scales_not_touching_cone": loose_scales}
    bm.free()
    return res


def _shell_tree(fs):
    vs = list({v for f in fs for v in f.verts})
    vi = {v: i for i, v in enumerate(vs)}
    return BVHTree.FromPolygons([v.co.copy() for v in vs], [[vi[v] for v in f.verts] for f in fs]), vs


def _gap(fa, fb):
    """0 if two shells' triangles intersect, else the smallest vertex-to-surface distance either way."""
    ta, va = _shell_tree(fa)
    tb, vb = _shell_tree(fb)
    if ta.overlap(tb):
        return 0.0
    d = 9.0
    for t, vs in ((tb, va), (ta, vb)):
        for v in vs:
            h = t.find_nearest(v.co, 1.0)
            if h[0] is not None:
                d = min(d, h[3])
    return round(d, 4)


def petiole_report(objs):
    """Fix round 1: every petiole must touch its own leaf (triangles intersecting: gap 0). In the hero by piece name
    (X_pet against X); in a part with a leaf and a stem (two shells), the stem against the leaf."""
    out = {}
    for o in objs:
        bm, groups, names, kinds = _shells(o)
        if "m062_pieces" in o:
            for k, nm in enumerate(names):
                if nm.endswith("_pet"):
                    leaf = [j for j, n2 in enumerate(names) if n2 == nm[:-4]]
                    out[f"{o.name}:{nm}"] = min((_gap(groups[k], groups[j]) for j in leaf), default=9.0)
        elif len(groups) == 2 and o.name.startswith("ForestLitterLeaf"):
            small, big = sorted(range(2), key=lambda k: len(groups[k]))
            out[f"{o.name}:stem"] = _gap(groups[small], groups[big])
        bm.free()
    return out


def chip_report(o):
    """Fix round 1: how far each chip's underside hangs over what lies below it (rays straight down from the verts
    and centres of its downward faces to the next other shell or the ground): max, median and the share over
    CHIP_HANG."""
    bm, groups, names, kinds = _shells(o)
    off = Vector(o.get(OFF, (0, 0, 0)))
    fsh = {}
    for k, fs in enumerate(groups):
        for f in fs:
            fsh[f.index] = k
    tree = BVHTree.FromBMesh(bm)
    out = {}
    for k, fs in enumerate(groups):
        if kinds[k] != "chip":
            continue
        gaps = []
        for f in fs:
            if f.normal.z >= -0.3:
                continue
            for p in [f.calc_center_median()] + [v.co.copy() for v in f.verts]:
                q = p + Vector((0, 0, -1e-4))
                h = tree.ray_cast(q, Vector((0, 0, -1)), 5.0)
                while h[0] is not None and fsh[h[2]] == k:
                    q = h[0] + Vector((0, 0, -1e-4))
                    h = tree.ray_cast(q, Vector((0, 0, -1)), 5.0)
                zg = p.z + off.z
                gaps.append(max(0.0, min(zg, p.z - h[0].z) if h[0] is not None else zg))
        gaps.sort()
        if gaps:
            out[names[k]] = {"max": round(gaps[-1], 3), "median": round(gaps[len(gaps) // 2], 3),
                             "over": round(sum(1 for g in gaps if g > CHIP_HANG) / len(gaps), 2)}
    bm.free()
    return out


def bury_report(o, skip_pairs=None):
    """STAGES "nothing buried": every shell tested by ray parity against every other closed shell (verts and face
    centres); depth = distance from its deepest point inside to that shell's surface. Allowed by design: a petiole
    inside its own leaf (it starts there). Reported: shells more than BURY inside anything, the deepest per kind,
    the T2 seat in T1 and the scale roots in the core."""
    bm, groups, names, kinds = _shells(o)
    n = len(groups)
    sol = m047._Solids()
    for k, fs in enumerate(groups):
        vs = list({v for f in fs for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        sol.add([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs], str(k))
    worst = []
    per_kind = {}
    for k, fs in enumerate(groups):
        pts = list({v.co.copy().freeze() for f in fs for v in f.verts}) + [f.calc_center_median() for f in fs]
        skip = [str(k)]
        if names[k].endswith("_pet"):
            base = names[k][:-4]
            skip += [str(j) for j in range(n) if names[j] == base]
        if names[k] in LEAVES:
            skip += [str(j) for j in range(n) if names[j] == names[k] + "_pet"]
        d, w = max((sol.point(Vector(p), skip=tuple(skip)) for p in pts), key=lambda r: r[0])
        who = names[int(w)] if w is not None else None
        if d > 0:
            worst.append((round(d, 3), names[k], who))
            kk = kinds[k]
            if d > per_kind.get(kk, (0,))[0]:
                per_kind[kk] = (round(d, 3), names[k], who)
    bm.free()
    worst.sort(key=lambda r: -r[0])
    return {"over_0.05": [w for w in worst if w[0] > BURY], "max": worst[0][0] if worst else 0.0,
            "worst": worst[:8], "per_kind": per_kind}


def leaf_ground(o):
    """Spec 2.1 / decision 10: the leaves lying on the ground have their bottom within 0.000-0.02 of z 0 (none deeper
    than 0.02), measured per leaf shell's lowest vertex in the build frame."""
    bm, groups, names, kinds = _shells(o)
    off_z = o.get(OFF, (0, 0, 0))[2]
    out = {}
    for k, fs in enumerate(groups):
        if kinds[k] == "leaf":
            out[names[k]] = round(min(v.co.z for f in fs for v in f.verts) + off_z, 3)
    bm.free()
    return out


def vis_report(o, el=25.0, step=0.025):
    """Eight-azimuth ray-grid visibility (STAGES "Foliage reads from every azimuth"): per azimuth at elevation `el`,
    the share of hits per kind, the share of leaf hits on edge-on faces (|n . view| < 0.35), how many leaves show
    (>= 25 hits) and the share of hits that land on leaf top/bottom faces (the slab face, not its rim)."""
    bm, groups, names, kinds = _shells(o)
    fk_ = {}
    for k, fs in enumerate(groups):
        for f in fs:
            fk_[f.index] = k
    mw = o.matrix_world
    bm.transform(mw)
    tree = BVHTree.FromBMesh(bm)
    lo = Vector((min(v.co.x for v in bm.verts), min(v.co.y for v in bm.verts), min(v.co.z for v in bm.verts)))
    hi = Vector((max(v.co.x for v in bm.verts), max(v.co.y for v in bm.verts), max(v.co.z for v in bm.verts)))
    c = (lo + hi) / 2
    rad = (hi - lo).length / 2 + 0.2
    out = {}
    bm.faces.ensure_lookup_table()
    for az in range(0, 360, 45):
        a_, e_ = math.radians(az), math.radians(el)
        d = Vector((math.sin(a_) * math.cos(e_), -math.cos(a_) * math.cos(e_), math.sin(e_)))
        u = Vector((0, 0, 1)).cross(d).normalized()
        w = d.cross(u).normalized()
        cnt, edge, leafhits, leafface, per_leaf = {}, 0, 0, 0, {}
        m = int(rad / step)
        for i in range(-m, m + 1):
            for j in range(-m, m + 1):
                p = c + u * (i * step) + w * (j * step) + d * 20.0
                h = tree.ray_cast(p, -d, 60.0)
                if h[0] is None:
                    continue
                k = fk_[h[2]]
                kd = kinds[k]
                cnt[kd] = cnt.get(kd, 0) + 1
                if kd == "leaf":
                    leafhits += 1
                    per_leaf[names[k]] = per_leaf.get(names[k], 0) + 1
                    nd = abs(h[1].dot(d))
                    if nd < 0.35:
                        edge += 1
                    if abs(bm.faces[h[2]].normal.z) > 0.6:
                        leafface += 1
        tot = max(1, sum(cnt.values()))
        out[f"az{az:03d}"] = {"shares": {k: round(100 * v / tot, 1) for k, v in sorted(cnt.items())},
                              "leaf_edge_on": round(100 * edge / max(1, leafhits), 1),
                              "leaf_slab_face": round(100 * leafface / max(1, leafhits), 1),
                              "leaves_seen": sum(1 for v in per_leaf.values() if v >= 25)}
    bm.free()
    return out


def screen_report(o, views=None):
    """Projected piece centroids (x from the left, h from the bottom, fractions of the projected hero bbox) for the
    sheet's front, f34 and top cameras (near-orthographic), to compare with the spec's piece-centroid table."""
    views = views or {"front_sheet": SHEET_VIEWS["front_sheet"], "f34_sheet": SHEET_VIEWS["f34_sheet"],
                      "top_sheet": SHEET_VIEWS["top_sheet"]}
    pieces = json.loads(o["m062_pieces"])
    off = Vector(o[OFF])
    mw = o.matrix_world
    allp = [mw @ v.co for v in o.data.vertices]
    out = {}
    for vn, (az, el) in views.items():
        a_, e_ = math.radians(az), math.radians(el)
        d = Vector((math.sin(a_) * math.cos(e_), -math.cos(a_) * math.cos(e_), math.sin(e_)))
        u = Vector((0, 0, 1)).cross(d).normalized()
        w = d.cross(u).normalized()
        xs = [p.dot(u) for p in allp]
        ys = [p.dot(w) for p in allp]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        row = {"WH": round((x1 - x0) / (y1 - y0), 3)}
        for nm, kd, *cc in pieces:
            if nm in ("L1", "L2", "O1", "O2", "S1", "S2", "G1", "G2", "G3", "Y1", "P_core"):
                p = mw @ (Vector(cc) - off)
                row[nm] = (round((p.dot(u) - x0) / (x1 - x0), 2), round((p.dot(w) - y0) / (y1 - y0), 2))
        out[vn] = row
    return out


# ---- build -----------------------------------------------------------------------------------------------------------
PARTS = ((LEAF_L_P, part_leaf("L1", 10.0)), (LEAF_M_P, part_leaf("O1", 10.0)), (LEAF_S_P, part_leaf("Y1", 10.0)),
         (LEAF_V_P, part_leaf("V1", 10.0)), (TWIG_L_P, part_twig("T1")), (TWIG_S_P, part_twig("Ts")),
         (CONE_P, part_cone), (STONE_L_P, part_stone("S1")), (STONE_S_P, part_stone("S2")))
TARGET_SIZE = ((4.4, 0.25), (3.6, 0.25), (1.1, 0.10))      # hero W (X), D (Y), H (Z) +- tolerance (decision 1)
HERO_BUDGET = 2200
PART_BUDGET = {CONE_P: 600}


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m062_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", HERO))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build(render=True, parts=True, close=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    EXPLODE["on"] = False
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn, budget=PART_BUDGET.get(name, 999))
    h, log["hero"] = _make(HERO, hero_all, "hero", HERO_BUDGET)
    leaves = {k: dict(v) for k, v in LEAF_INFO.items()}
    twigs = {k: dict(v) for k, v in TWIG_INFO.items()}
    chips = {k: dict(v) for k, v in CHIP_INFO.items()}
    cone = dict(CONE_INFO)
    _cleanup_tmp()
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.2f} x {d.y:.2f} x {d.z:.2f}"
    audits = [M.audit(o) for o in order]
    thin = {o.name: m012._thin(o, 3.0) for o in order}
    shells = {o.name: shells_report(o) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = HERO_BUDGET if o is h else PART_BUDGET.get(o.name, 999)
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
                    problems.append(f"{o.name} shell {i} ({s['piece']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['piece']}): not closed outward (volume {s['volume']})")
    contact = contact_report(h)
    if contact["floating"] or contact["unchained"]:
        problems.append(f"{HERO}: {contact['floating']} shells touch nothing within {CONTACT} "
                        f"({contact['floating_pieces'][:6]}), {contact['unchained']} have no chain to the ground")
    if contact["sink"] < -0.031:
        problems.append(f"{HERO}: sinks {contact['sink']} below the ground")
    for k, v in contact["rests"].items():
        if v is None or (isinstance(v, float) and v > CONTACT) or (isinstance(v, list) and not v):
            problems.append(f"{HERO}: {k} not in contact ({v})")
    if contact["scales_not_touching_cone"]:
        problems.append(f"{HERO}: scales touching neither the core nor another scale: {contact['scales_not_touching_cone']}")
    pets = petiole_report(order)
    for k, g in pets.items():
        if g > 0.0:
            problems.append(f"{k}: petiole {g} from its leaf (must touch it)")
    if len([k for k in pets if k.startswith(HERO + ":")]) != sum(1 for s in LEAVES.values() if s.get("pet")):
        problems.append(f"{HERO}: petiole count {len(pets)} does not match LEAVES")
    chips_hang = chip_report(h)
    for k, c in chips_hang.items():
        if c["max"] > CHIP_HANG:
            problems.append(f"{HERO}: chip {k} hangs {c['max']} over what is below it (at most {CHIP_HANG})")
    bury = bury_report(h)
    if bury["over_0.05"]:
        problems.append(f"{HERO}: {len(bury['over_0.05'])} shells more than {BURY} inside another ({bury['over_0.05'][:4]})")
    lg = leaf_ground(h)
    for k, z in lg.items():
        if k in GROUND_LEAVES and z < -0.02:
            problems.append(f"{HERO}: leaf {k} {z} into the ground (decision 10: at most 0.02)")
    for k, lf in leaves.items():
        if lf.get("bad_fans"):
            problems.append(f"{HERO}: leaf {k} has {lf['bad_fans']} folded top-fan triangles")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 11: none)")
    for n_, t in thin.items():
        if t["under"]:
            problems.append(f"{n_}: {t['under']} faces with a corner under 3 deg (min {t['min_deg']})")
    winding = {o.name: sum(s["winding_errors"] for s in shells[o.name]) for o in order}
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
           "hero_shells": kinds, "contact": contact, "bury": bury, "leaf_ground": lg, "winding": winding,
           "petioles": pets, "chip_hang": chips_hang,
           "leaves": leaves, "twigs": twigs, "chips": chips, "cone": cone, "thin": thin, "log": log,
           "problems": problems, "uv": uv,
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "vis": vis_report(h), "screen": screen_report(h),
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders ---------------------------------------------------------------------------------------------------------
# decision 9: front_sheet (0, 30) governs positions, f34_sheet the read, top_sheet the plan (probed: spec 3.2); floor
# hidden and a 3x lens in every *_sheet shot
SHEET_VIEWS = {"f34_sheet": (-5, 38), "r34_sheet": (155, 35), "front_sheet": (0, 30), "side_sheet": (90, 30),
               "rear_sheet": (180, 30), "top_sheet": (0, 68)}
PARTS_SHOT = (-20, 35)
SPIN_EL = 25


def _exploded(objs):
    EXPLODE["on"] = True
    try:
        o = _new(PFX + "exploded", hero_all, "part", 3000, temp=True)
    finally:
        EXPLODE["on"] = False
    o.location = (objs[0].location.x + 30, objs[0].location.y, 0)
    bpy.context.view_layer.update()
    return [o]


def _scale_marker(h, at, name="char"):
    """A 5.5-stud character stand-in at build-frame point `at`."""
    a = K.fk().Asset(PFX + name, "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=STONE_D, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=STONE_D, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=STONE_D, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
    c.location = off @ Vector(at)
    bpy.context.view_layer.update()
    return c


def _at(o, p):
    return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    markers = [_scale_marker(h, (3.2, 0.3, 0.0)), _scale_marker(h, (-3.3, 0.3, 0.0), "char2")]
    kit = K.NS["KIT"]
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        for o in objs[1:]:
            extra["part_" + o.name.replace(HERO, "").lower()] = ([o], *PARTS_SHOT)
        if shown:
            extra["exploded"] = (shown, -5, 38)
        extra["scale"] = ([h] + markers, -20, 6)
        orig, kit["render_group"] = m033._long_lens(kit)
        try:
            sheet = M.views(NUM, [h], names=(), extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet, "spin": render_spin(h)}
        if close:
            out.update(render_close_ups(objs))
        return out
    finally:
        for o in shown + markers:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def render_spin(h, el=SPIN_EL):
    """Eight azimuths at elevation 25 (every 45 deg from the front), one contact sheet M062_spin.png."""
    kit = K.NS["KIT"]
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    old = kit["CELL"]
    kit["CELL"] = (480, 320)
    paths = []
    try:
        for az in range(0, 360, 45):
            paths.append(kit["render_group"]([h], f"{d}/spin_{az:03d}.png", az, el))
    finally:
        kit["CELL"] = old
        g = bpy.data.objects.get("FB_Ground")
        if g:
            g.location.z = 0.0
            g.hide_set(True)
    rows = [kit["hstack"](paths[i:i + 4]) for i in range(0, 8, 4)]
    sheet = f"{d}/{M.code(NUM)}_spin.png"
    kit["save_px"](kit["vstack"](rows), sheet)
    return sheet


def render_close_ups(objs):
    """cone_cu (the pinecone, against z_cone_f34), junction_cu (the twig crossing from above, close-up 2), twig_x (the
    whole X), leaf_edge (L1's main lobe tip edge-on, close-up 3), leaf_edge_part (the large leaf part edge-on),
    underside_cu (low at the front, close-up 1)."""
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    by = {o.name: o for o in objs}
    h = objs[0]
    pieces = {p[0]: p for p in json.loads(h["m062_pieces"])}
    out = {}
    rc = m033.render_close
    pc = Vector(pieces["P_core"][2:5])
    out["cone_cu"] = rc([h], f"{d}/cone_cu.png", 0, 20, _at(h, pc + Vector((0, 0, 0.12))), 0.62)
    cross = Vector((0.39, 0.76, 0.3))
    out["junction_cu"] = rc([h], f"{d}/junction_cu.png", -30, 50, _at(h, cross), 0.42)
    out["twig_x"] = rc([h], f"{d}/twig_x.png", -15, 40, _at(h, Vector((0.55, 0.75, 0.4))), 1.4)
    # L1's main lobe tip: tip az 320 -> camera looks across the tip (perpendicular to the lobe axis), low
    tipd = _u(LEAVES["L1"]["az"])
    tip = Vector(pieces["L1"][2:5]) + tipd * 0.62
    out["leaf_edge"] = rc([h], f"{d}/leaf_edge.png", LEAVES["L1"]["az"] - 270 + 90, 6, _at(h, Vector((tip.x, tip.y, 0.06))), 0.28)
    if LEAF_L_P in by:
        lp = by[LEAF_L_P]
        out["leaf_edge_part"] = rc([lp], f"{d}/leaf_edge_part.png", 0, 4, lp.matrix_world @ Vector((0.55, 0, 0.06)), 0.4)
    out["underside_cu"] = rc([h], f"{d}/underside_cu.png", 0, 5, _at(h, Vector((0.0, 0.0, 0.4))), 2.2)
    out["thumb"] = rc([h], f"{d}/thumb.png", 0, 30, _at(h, Vector((-0.07, -0.05, 0.5))), 2.4)
    return out


def preview(names=("front_sheet", "f34_sheet", "top_sheet", "rear_sheet", "side_sheet", "r34_sheet"), vfx=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig


def hero_only():
    """Rebuild just the hero (tuning loop)."""
    M.coll(NUM, TITLE)
    palette()
    EXPLODE["on"] = False
    h, lg = _make(HERO, hero_all, "hero", HERO_BUDGET)
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, _ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"hero": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                        "boundary_edges", "normals")}, "log": lg,
            "leaves": {k: dict(v) for k, v in LEAF_INFO.items()}, "twigs": dict(TWIG_INFO), "cone": dict(CONE_INFO),
            "chips": dict(CHIP_INFO), "offset": [round(x, 3) for x in h[OFF]]}
