"""063 Hanging Vine (references/063.png): one wall-mounted vine. A cracked, faceted warm-beige stone attachment pad
(flat back on the wall, flat underside, a socket groove in its front face) holds a thick woody stub; below the stub two
6-sided woody strands twist round each other (right-handed, a full turn every 2.2 studs) and hang to a pointed end,
carrying three-leaf clusters of chunky broad five-lobed slab leaves that alternate round the vine, one single small leaf,
one fork spur, three green tendril curls and a tip cluster.

    import importlib, kit_models, m063; importlib.reload(kit_models); importlib.reload(m063); m063.build()

Build frame = attach frame: studs, front -Y, +X right, the wall plane y = 0 (the pad's flat back face), nothing behind
it; z = 0 at the lowest leaf tip, the pad top at z 7.5. Every object ends with its origin at its bbox bottom centre;
o["m063_offset"] is that origin in the build frame and o["m063_attach"] the attach point in object coordinates
(spec 2.6). W06 owns HangingVine* / StraightVine / Vine*, so the family is TwistedVine*:
- TwistedVine (hero): pad + stub + strands A / B + spur + 9 clusters + 1 single + 3 tendrils, one object of closed
  shells (attach: the pad's back-face centre, normal +Y into the wall).
- TwistedVinePad: the pad with its socket groove (attach: back-face centre).
- TwistedVineSegment: one 6-sided stick, Ø 0.36 x 1.8, one 15 deg bend, flat cut ends (attach: top end centre, -Z).
- TwistedVineFork: a Y of three cut sticks, Ø 0.36, unioned (attach: the junction, leg down -Z).
- TwistedVineLeafCluster: a stalk with two side leaves and a bigger centre leaf (attach: the stalk's top end).
Colour by role and position (never by facing). Stages 5-6: none (the sheet shows no effect). See
art/blender/renders/models/M063/M063_spec.md.
"""
import math
import os
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
import m056

NUM, TITLE, SHEET = 63, "Hanging Vine", "M063"
OFF, ATT = "m063_offset", "m063_attach"
PFX = "_m063_"
HERO = "TwistedVine"
PAD_P, SEG_P, FORK_P, CLUS_P = "TwistedVinePad", "TwistedVineSegment", "TwistedVineFork", "TwistedVineLeafCluster"
PART_NAMES = (PAD_P, SEG_P, FORK_P, CLUS_P)

LEAF_D, LEAF_M, LEAF_B, LEAF_L = "m063_leaf_dark", "m063_leaf_mid", "m063_leaf_bright", "m063_leaf_light"
STALK = "m063_stalk"
VINE, VINE_D, VINE_L, VINE_C = "m063_vine", "m063_vine_deep", "m063_vine_light", "m063_vine_cut"
STONE, STONE_D, MOSS = "m063_stone", "m063_stone_deep", "m063_moss"
LADDER = (LEAF_D, LEAF_M, LEAF_B, LEAF_L)

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
CLR = 0.006
HERO_LIMIT = 2500
PART_LIMIT = 1000
COS30 = math.cos(math.radians(30))
Z = Vector((0.0, 0.0, 1.0))

# key -> (hex, roughness, low specular): K.calibrate results against TARGETS (spec "Stage 4").
PALETTE = {
    LEAF_D: ("#45702F", 0.85, True),     # calibrated #436832 / #5B8822 / #89A30D, then a little greener and brighter:
    LEAF_M: ("#5E9320", 0.8, True),      # the hero render measured G median #66931C against the sheet's #67A416
    LEAF_B: ("#8EAD0C", 0.8, True),      # (stage 4 re-measure)
    LEAF_L: ("#A3B036", 0.8, True),
    STALK: ("#78A11A", 0.8, True),
    VINE: ("#8A5B24", 0.9, False),       # calibrated #765227, then +sat / +value: the hero render measured B median
    VINE_D: ("#67400F", 0.9, False),     # #5B3F21 against the sheet's #70491A (stage 4 re-measure)
    VINE_L: ("#9C6A2E", 0.9, False),
    VINE_C: ("#9D712E", 0.85, False),
    STONE: ("#9A8E89", 0.9, False),
    STONE_D: ("#807773", 0.9, False),
    MOSS: ("#989365", 0.9, False),
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions, or the swatch), K.sample kinds
TARGETS = {LEAF_D: ((0x4E, 0x7B, 0x33), "green"), LEAF_M: ((0x6E, 0xA5, 0x22), "green"),
           LEAF_B: ((0xAD, 0xC9, 0x0F), "vivid"), LEAF_L: ((0xCB, 0xD7, 0x38), "vivid"),
           STALK: ((0x95, 0xC6, 0x1B), "green"), VINE: ((0x95, 0x64, 0x32), "brown"),
           VINE_D: ((0x6E, 0x45, 0x20), "brown"), VINE_L: ((0xA8, 0x74, 0x3C), "brown"),
           VINE_C: ((0xC8, 0x8A, 0x3A), "brown"), STONE: ((0xC4, 0xB0, 0xA0), "all"),
           STONE_D: ((0xA3, 0x92, 0x86), "all"), MOSS: ((0xC2, 0xB6, 0x76), "all")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    for m in list(bpy.data.materials):          # resync mixed keys left in the file to the current parents
        key = m.name[3:] if m.name.startswith("FB_m063_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k == "m063_" + tail), None) or \
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


# ---- small helpers -----------------------------------------------------------------------------------------------------
def _q(t):
    return round(max(0.0, min(1.0, t)) * 4) / 4


def _mix(k1, k2, t):
    return K.mix_key(k1, k2, _q(t))


def _tone(p):
    """Leaf key at ladder position p (0 dark, 1 mid, 2 bright, 3 light), quantised to quarter steps."""
    p = round(max(0.0, min(3.0, p)) * 4) / 4
    i = min(int(p), 2)
    return _mix(LADDER[i], LADDER[i + 1], p - i)


REC = []        # build-frame record of every shell of the object being built: dict(kind, tag, cid, pts, polys)
RECS = {}       # object name -> its records
INFO = {}       # build notes (placement variants, dropped pieces, attach points)


def _add(a, pts, polys, keys, tint=1.0, kind="", tag="", cid=""):
    """One closed shell: verts, faces (oriented outward), a key per face (or one key), a tint per face (or one)."""
    bm = a.bm
    vs = [bm.verts.new(Vector(p)) for p in pts]
    fs = [bm.faces.new([vs[i] for i in poly]) for poly in polys]
    m056._orient(bm, fs)
    keys = [keys] * len(fs) if isinstance(keys, str) else keys
    tints = list(tint) if isinstance(tint, (list, tuple)) else [tint] * len(fs)
    cache = {}
    for f, k, t in zip(fs, keys, tints):
        if k not in cache:
            cache[k] = a._mi(k)
        f.material_index = cache[k]
        f.smooth = False
        for l in f.loops:
            l[a.tint_layer] = (t, t, t, 1.0)
    REC.append(dict(kind=kind, tag=tag, cid=cid, pts=[Vector(p) for p in pts], polys=[list(p) for p in polys]))
    return vs, fs


def _frame(t, ref):
    s = ref - t * ref.dot(t)
    if s.length < 1e-5:
        s = t.orthogonal()
    s.normalize()
    return s, t.cross(s).normalized()


def tube(pts, radii, sides, ref, phase=0.0, start="flat", end="flat", tip=0.1, t_start=None, t_end=None):
    """A faceted tube through straight pieces: a ring of `sides` at every point in the mitre plane of its kink (flat
    junctions, never smooth sweeps). ref (a Vector, or a list with one per point) sets each ring's first-vertex
    direction (turned by phase). start / end: "flat" cap or "point" (an apex `tip` beyond the end). t_start / t_end
    put the end ring in a plane with that normal instead (an oblique seat or cut). Returns pts, polys, rings, caps."""
    pts = [Vector(p) for p in pts]
    n = len(pts)
    out, rings = [], []
    for i in range(n):
        if i == 0:
            d1 = d2 = (pts[1] - pts[0]).normalized()
        elif i == n - 1:
            d1 = d2 = (pts[-1] - pts[-2]).normalized()
        else:
            d1 = (pts[i] - pts[i - 1]).normalized()
            d2 = (pts[i + 1] - pts[i]).normalized()
        t = (d1 + d2).normalized()
        plane_n = None
        if i == 0 and t_start is not None:
            plane_n = Vector(t_start).normalized()
        if i == n - 1 and t_end is not None:
            plane_n = Vector(t_end).normalized()
        if plane_n is not None and abs(d1.dot(plane_n)) < 0.6:
            # a seat plane nearly along the piece would stretch the ring: lean it toward the piece's own normal plane
            plane_n = (plane_n * (1.0 if d1.dot(plane_n) >= 0 else -1.0) + d1).normalized()
        r_ = ref[i] if isinstance(ref, list) else ref
        s, w = _frame(t, Vector(r_))
        sc, kd = 1.0, d2 - d1
        if kd.length > 1e-5:
            kd.normalize()
            sc = 1.0 / max(math.cos(d1.angle(d2) / 2), 0.35)
        ring = []
        for k in range(sides):
            ang = phase + 2 * math.pi * k / sides
            off = (s * math.cos(ang) + w * math.sin(ang)) * radii[i]
            if sc != 1.0:
                off = off + kd * off.dot(kd) * (sc - 1.0)
            p = pts[i] + off
            if plane_n is not None:
                den = d1.dot(plane_n)
                if abs(den) > 1e-4:
                    p = p + d1 * ((pts[i] - p).dot(plane_n) / den)
            ring.append(p)
        rings.append(list(range(len(out), len(out) + sides)))
        out += ring
    polys, caps = [], {"start": [], "end": []}
    for i in range(n - 1):
        a_, b_ = rings[i], rings[i + 1]
        for k in range(sides):     # triangles with a fixed diagonal: twisted pieces are far from planar, and the
            j = (k + 1) % sides    # placement guard must test exactly the faces that ship
            polys += [[a_[k], a_[j], b_[j]], [a_[k], b_[j], b_[k]]]
    for which, ring, c, d in (("start", rings[0], pts[0], (pts[0] - pts[1]).normalized()),
                              ("end", rings[-1], pts[-1], (pts[-1] - pts[-2]).normalized())):
        mode = start if which == "start" else end
        if mode == "flat":
            caps[which].append(len(polys))
            polys.append(list(ring))
        else:
            out.append(c + d * tip)
            ap = len(out) - 1
            for k in range(sides):
                caps[which].append(len(polys))
                polys.append([ring[k], ring[(k + 1) % sides], ap])
    return out, polys, rings, caps


def _centroid(pts, poly):
    return sum((pts[i] for i in poly), Vector()) / len(poly)


# ---- guard: what new pieces must not cut (spec 2.1, 6) ------------------------------------------------------------------
class Guard:
    """Shells placed so far (tag, pts, polys). hits() counts triangle intersections of a candidate with all of them
    except the skipped tags; near() the candidate verts closer than clr to them; inside_pad() ray parity in the pad."""

    def __init__(self):
        self.items = []
        self._cache = {}

    def add(self, tag, pts, polys):
        self.items.append((tag, [Vector(p) for p in pts], [list(p) for p in polys]))
        self._cache.clear()

    def tree(self, skip=()):
        key = frozenset(skip)
        if key not in self._cache:
            cos, polys = [], []
            for tag, p, pl in self.items:
                if tag in key or any(tag.startswith(s + ":") for s in key):
                    continue
                b = len(cos)
                cos += p
                polys += [[b + i for i in q] for q in pl]
            self._cache[key] = BVHTree.FromPolygons(cos, polys) if polys else None
        return self._cache[key]

    def hits(self, pts, polys, skip=()):
        t = self.tree(skip)
        if t is None:
            return 0
        return len(BVHTree.FromPolygons(pts, polys).overlap(t))

    def near(self, pts, skip=(), clr=CLR):
        t = self.tree(skip)
        if t is None:
            return 0
        n = 0
        for p in pts:
            h = t.find_nearest(p, clr)
            if h[0] is not None:
                n += 1
        return n

    def inside_pad(self, p):
        for tag, ps, pl in self.items:
            if tag == "pad":
                return m047._parity_in(BVHTree.FromPolygons(ps, pl), Vector(p))
        return False


# ---- the stone pad (spec 1.4, 2.2) ---------------------------------------------------------------------------------------
STUB_Y, STUB_R = -0.945, 0.195
STUB_CUT = math.radians(35.0)
STUB_TOP = 7.31
PAD_Z0, PAD_Z1 = 5.75, 7.50
GX = STUB_R + 0.012                       # groove half width (0.207): the stub's side vertices sit 0.012 off its walls
GY = STUB_Y + STUB_R * COS30 + 0.010      # groove back wall (-0.766): the stub's back flat 0.010 off it
ROOF = STUB_TOP + 0.020                   # the groove's sloping top, parallel to the stub's cut face, 0.02 above it
# footprint (x, y) round the pad, its top height there (the top facets slope down to the front-left)
FOOT = (((0.95, -0.10), 7.48), ((0.85, 0.0), 7.50), ((-0.37, 0.0), 7.43), ((-0.45, -0.08), 7.38),
        ((-0.45, -0.80), 7.22), ((-0.30, -0.95), 7.35), ((0.85, -0.95), 7.46), ((0.95, -0.85), 7.45))
PAD_CACHE = {}


def stub_plane_z(y):
    """The stub's oblique cut: tilted 35 deg toward -Y, its back edge at STUB_TOP."""
    return STUB_TOP + math.tan(STUB_CUT) * (y - (STUB_Y + STUB_R * COS30))


def _pad_hull(rng):
    cx, cy = 0.25, -0.47
    pts = []
    for (x, y), T in FOOT:
        ox, oy = x - cx, y - cy
        L = math.hypot(ox, oy)
        ox, oy = ox / L, oy / L
        k = 0.03 + rng.uniform(0.0, 0.02)
        pts.append(Vector((x, y, PAD_Z0)))
        if y < -0.05:          # the mid-height fold on the front and side faces only
            pts.append(Vector((x + ox * k, min(y + oy * k, 0.0), 6.55 + rng.uniform(-0.12, 0.12))))
        pts.append(Vector((x, y, T - 0.11)))
        pts.append(Vector((x - ox * 0.12, min(y - oy * 0.12, 0.0), T)))
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in pts]
    res = bmesh.ops.convex_hull(bm, input=vs)
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def _groove_cutter():
    """A prism along X (x -GX..GX): the groove's back wall at y = GY, open at the bottom and through the front, its top
    a slope parallel to the stub's cut face."""
    yf = -1.4
    zr_f = ROOF + math.tan(STUB_CUT) * (yf - GY)
    sec = [(GY, 5.0), (GY, ROOF), (yf, zr_f), (yf, 5.0)]
    bm = bmesh.new()
    a_ = [bm.verts.new((-GX, y, z)) for y, z in sec]
    b_ = [bm.verts.new((GX, y, z)) for y, z in sec]
    bm.faces.new(a_)
    bm.faces.new(list(reversed(b_)))
    for k in range(4):
        bm.faces.new((a_[k], b_[k], b_[(k + 1) % 4], a_[(k + 1) % 4]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def pad_geom():
    """The pad as (pts, polys, keys): a faceted convex block (flat back on y = 0, flat underside), the socket groove
    cut by an exact boolean, a band cut at z 6.1 for the deeper foot, and two V crack creases with lichen strips.
    Cached per build (the hero and the pad part share it)."""
    if PAD_CACHE:
        return PAD_CACHE["pts"], PAD_CACHE["polys"], PAD_CACHE["keys"]
    rng = random.Random(631)
    coll = M.coll(NUM, TITLE)
    objs = []
    try:
        for nm, bm, key in ((PFX + "padtmp", _pad_hull(rng), STONE), (PFX + "groove", _groove_cutter(), STONE_D)):
            me = bpy.data.meshes.new(nm)
            bm.to_mesh(me)
            bm.free()
            me.materials.append(K.fk().material(key))
            o = bpy.data.objects.new(nm, me)
            coll.objects.link(o)
            objs.append(o)
        pad, cut = objs
        m = pad.modifiers.new("Groove", "BOOLEAN")
        m.operation, m.solver, m.object = "DIFFERENCE", "EXACT", cut
        m.material_mode = "TRANSFER"
        with M._override(pad):
            bpy.ops.object.modifier_apply(modifier=m.name)
        keymap = [mt.get("flintkit_key", mt.name[3:]) for mt in pad.data.materials]
        bm = bmesh.new()
        bm.from_mesh(pad.data)
    finally:
        for o in objs:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    groove_mi = {i for i, k in enumerate(keymap) if k == STONE_D}

    def region(pred):
        return [f for f in bm.faces if f.material_index not in groove_mi and pred(f)]

    def bisect(faces, co, no):
        if not faces:
            return []
        geom = list(set(faces) | {e for f in faces for e in f.edges} | {v for f in faces for v in f.verts})
        r = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-4, plane_co=Vector(co), plane_no=Vector(no))
        return [x for x in r["geom_cut"] if isinstance(x, bmesh.types.BMVert)]

    cracks = []
    # crack 1: down the front face right of the groove, from the top at x 0.45 to the bottom near x 0.70
    no1 = Vector((1.65, 0.0, 0.25)).normalized()
    co1 = Vector((0.45, -0.95, 7.40))
    fr = lambda f: f.normal.y < -0.75 and f.calc_center_median().x > 0.25
    for s in (-0.04, 0.04):
        bisect(region(fr), co1 + no1 * s, no1)
    mid1 = bisect(region(fr), co1, no1)
    cracks.append((co1, no1, fr, mid1, Vector((0, 1, 0))))
    # crack 2: across the right face, sloping down to the front at z ~6.6
    no2 = Vector((0.0, -0.3, -1.0)).normalized()
    co2 = Vector((0.95, -0.5, 6.72))
    rt = lambda f: f.normal.x > 0.9 and f.calc_center_median().y < -0.12
    for s in (-0.035, 0.035):
        bisect(region(rt), co2 + no2 * s, no2)
    mid2 = bisect(region(rt), co2, no2)
    cracks.append((co2, no2, rt, mid2, Vector((-1, 0, 0))))
    for co, no, pred, mid, inward in cracks:
        for v in mid:
            # never move the back face off the wall plane or notch the flat underside
            if v.is_valid and v.co.y < -0.15 and v.co.z > PAD_Z0 + 0.01:
                v.co += inward * 0.03
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
    bm.normal_update()
    pts = [v.co.copy() for v in bm.verts]
    bm.verts.index_update()
    polys, keys = [], []
    for f in bm.faces:
        c = f.calc_center_median()
        polys.append([v.index for v in f.verts])
        if f.material_index in groove_mi:
            k = STONE_D
        elif any(abs((c - co).dot(no)) < 0.042 and pred(f) for co, no, pred, mid, inw in cracks):
            k = MOSS
        elif c.z < PAD_Z0 + 0.01:
            k = _mix(STONE, STONE_D, 0.5)                   # the underside
        elif c.z < PAD_Z0 + 0.45:
            k = _mix(STONE, STONE_D, 0.5)                   # the lower facets (under the mid-height fold): the foot
        elif c.z < PAD_Z0 + 0.75:
            k = _mix(STONE, STONE_D, 0.25)
        else:
            k = STONE
        keys.append(k)
    bm.free()
    back = [p for p in pts if abs(p.y) < 1e-4]
    att = Vector(((min(p.x for p in back) + max(p.x for p in back)) / 2, 0.0,
                  (min(p.z for p in back) + max(p.z for p in back)) / 2))
    PAD_CACHE.update(pts=pts, polys=polys, keys=keys, attach=att)
    return pts, polys, keys


def _pad_tints(pts, polys, seed=5):
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    return [1.0 + 0.04 * 1.6 * noise.noise(_centroid(pts, p) * 1.3 + off) for p in polys]


def pad(a, g):
    pts, polys, keys = pad_geom()
    _add(a, pts, polys, keys, _pad_tints(pts, polys), kind="pad", tag="pad")
    g.add("pad", pts, polys)
    return PAD_CACHE["attach"]


# ---- stub (spec 2.2) -----------------------------------------------------------------------------------------------------
def stub_geom():
    """6-sided, one flat facing -Y, a flared knuckle at the bottom (Ø 0.54 -> 0.39) where the strands split off, the top
    cut obliquely (35 deg toward -Y) with a 0.06 band under the cut."""
    rings = []
    for z, r in ((5.55, 0.27), (5.75, STUB_R), (6.60, STUB_R * 1.01)):
        rings.append([Vector((r * math.cos(math.pi / 3 * k), STUB_Y + r * math.sin(math.pi / 3 * k), z))
                      for k in range(6)])
    for dz in (-0.06, 0.0):
        ring = []
        for k in range(6):
            x, y = STUB_R * math.cos(math.pi / 3 * k), STUB_Y + STUB_R * math.sin(math.pi / 3 * k)
            ring.append(Vector((x, y, stub_plane_z(y) + dz)))
        rings.append(ring)
    pts = [p for r in rings for p in r]
    polys = [list(reversed(range(6)))]
    keys = [_mix(VINE, VINE_D, 0.75)]
    for i in range(4):
        b0, b1 = 6 * i, 6 * (i + 1)
        polys += [[b0 + k, b0 + (k + 1) % 6, b1 + (k + 1) % 6, b1 + k] for k in range(6)]
        keys += [_mix(VINE_D, VINE_C, 0.5) if i == 3 else _mix(VINE, VINE_D, 0.5 if i < 2 else 0.75)] * 6
    polys.append(list(range(24, 30)))
    keys.append(VINE_C)
    return pts, polys, keys


def stub(a, g):
    pts, polys, keys = stub_geom()
    _add(a, pts, polys, keys, 0.98, kind="stub", tag="stub")
    g.add("stub", pts, polys)


# ---- the twisted pair (spec 2.3) -----------------------------------------------------------------------------------------
AXIS = ((5.55, 0.00, -0.945), (4.9, 0.15, -0.93), (4.3, 0.05, -1.00), (3.8, -0.15, -1.05), (3.2, 0.05, -0.98),
        (2.6, 0.10, -0.92), (2.0, -0.10, -0.97), (1.4, 0.03, -1.02), (0.8, 0.05, -0.95), (0.30, 0.03, -0.93))
PITCH = 2.2            # a full turn of the pair
STEP = PITCH / 8       # a station every 45 deg of twist (60 deg read as a zigzag at sheet scale)
Z_TOP, Z_LAST = 5.59, 0.36
STRANDS = {}


def axis_at(z):
    """The vine axis (the twist centre): a Catmull-Rom through AXIS, a gentle S-sway."""
    P = AXIS
    if z >= P[0][0]:
        return Vector((P[0][1], P[0][2], z))
    if z <= P[-1][0]:
        return Vector((P[-1][1], P[-1][2], z))
    for i in range(len(P) - 1):
        z0, z1 = P[i][0], P[i + 1][0]
        if z1 <= z <= z0:
            t = (z0 - z) / (z0 - z1)
            p0, p1, p2, p3 = P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, len(P) - 1)]

            def cr(j):
                a_, b_, c_, d_ = p0[j], p1[j], p2[j], p3[j]
                return 0.5 * (2 * b_ + (-a_ + c_) * t + (2 * a_ - 5 * b_ + 4 * c_ - d_) * t * t +
                              (-a_ + 3 * b_ - 3 * c_ + d_) * t ** 3)
            return Vector((cr(1), cr(2), z))


def strand_r(z):
    if z >= 1.5:
        return 0.12
    return 0.06 + 0.06 * max(0.0, (z - Z_LAST)) / (1.5 - Z_LAST)


def strand_centre(s, z):
    pts = STRANDS[s]["pts"]
    if z >= pts[0].z:
        return pts[0].copy()
    for p, q in zip(pts, pts[1:]):
        if q.z <= z <= p.z:
            t = (p.z - z) / max(p.z - q.z, 1e-6)
            return p.lerp(q, t)
    return pts[-1].copy()


def strand_dir(s, z):
    pts = STRANDS[s]["pts"]
    for p, q in zip(pts, pts[1:]):
        if q.z <= z <= p.z:
            return (q - p).normalized()
    return Vector((0, 0, -1))


def strand_geom(s, rng):
    n_pc = max(1, round((Z_TOP - Z_LAST) / STEP))
    dz = (Z_TOP - Z_LAST) / n_pc
    th0 = math.pi if s == "A" else 0.0
    pts, refs, rad = [], [], []
    for i in range(n_pc + 1):
        z = Z_TOP - i * dz
        th = th0 + 2 * math.pi * (Z_TOP - z) / PITCH
        r = strand_r(z)
        off = r * COS30 + 0.003 + (rng.uniform(0.0, 0.008) if 0 < i < n_pc else 0.0)
        rd = Vector((math.cos(th), math.sin(th), 0.0))
        pts.append(axis_at(z) + rd * off)
        refs.append(rd)
        rad.append(r)
    STRANDS[s] = dict(pts=pts, r=rad, refs=refs)
    P, polys, rings, caps = tube(pts, rad, 6, refs, phase=math.radians(30), start="flat", end="point", tip=0.10,
                                 t_start=Vector((0, 0, -1)))
    return P, polys


def _wood(p):
    """Wood key on a ladder: -1 young light, 0 vine, +1 old deep (quarter steps)."""
    return _mix(VINE, VINE_L, -p) if p < 0 else _mix(VINE, VINE_D, p)


def _dist_to_line(c, pts):
    best = 9.0
    for p, q in zip(pts, pts[1:]):
        d = q - p
        t = max(0.0, min(1.0, (c - p).dot(d) / max(d.length_squared, 1e-9)))
        best = min(best, (c - (p + d * t)).length)
    return best


def strand_keys(P, polys, seed, other):
    """By height (older deep wood near the pad, the young light taper at the bottom) and, one step deeper, the faces
    within 0.19 of the other strand's centreline (where the two strands lie against each other: a position rule)."""
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    keys, tints = [], []
    for p in polys:
        c = _centroid(P, p)
        z = c.z
        w = 0.5 if z > 4.85 else 0.25 if z > 4.3 else -0.75 if z < 0.9 else -0.5 if z < 1.5 else 0.0
        if _dist_to_line(c, other) < 0.19 * strand_r(z) / 0.12:
            w += 0.25
        keys.append(_wood(w))
        tints.append(1.0 + 0.02 * 1.6 * noise.noise(Vector((0.0, 0.0, z * 1.4)) + off))
    return keys, tints


def strands(a, g, rng):
    geo = {s: strand_geom(s, rng) for s in "AB"}
    for s, tint in (("A", 1.03), ("B", 0.97)):
        P, polys = geo[s]
        keys, tints = strand_keys(P, polys, 70 + ord(s), STRANDS["B" if s == "A" else "A"]["pts"])
        _add(a, P, polys, keys, [t * tint for t in tints], kind="strand", tag="strand" + s)
        g.add("strand" + s, P, polys)


# ---- fork spur (spec 2.5) ------------------------------------------------------------------------------------------------
SPUR = {"z": 3.60, "az": 230.0, "up": 45.0, "len": 0.40}


def spur(a, g):
    z, az = SPUR["z"], math.radians(SPUR["az"])
    oh = Vector((math.cos(az), math.sin(az), 0.0))
    s = max("AB", key=lambda k: (strand_centre(k, z) - axis_at(z)).normalized().dot(oh))
    c = strand_centre(s, z)
    root = c + oh * (strand_r(z) * COS30 - 0.045)
    d = (oh * math.sin(math.radians(SPUR["up"])) + Z * math.cos(math.radians(SPUR["up"]))).normalized()
    pts = [root, root + d * 0.22, root + d * SPUR["len"]]
    P, polys, rings, caps = tube(pts, [0.09, 0.085, 0.075], 6, Z, phase=0.0, t_start=oh)
    keys = [VINE] * len(polys)
    for i in caps["end"]:
        keys[i] = VINE_C
    for k in range(12):
        keys[12 + k] = _mix(VINE, VINE_C, 0.5)       # the band under the cut end (the second piece)
    keys = [_mix(VINE, VINE_D, 0.25) if k == VINE else k for k in keys]
    _add(a, P, polys, keys, 1.0, kind="spur", tag="spur")
    g.add("spur", P, polys)
    SPUR.update(end=pts[-1], dir=d, host="strand" + s)


# ---- leaves (spec 1.4) ---------------------------------------------------------------------------------------------------
# A broad fig / grape leaf as on the sheet's close-ups and cluster cell (never a star). Fix round 3: five broad lobes
# with ONE point each - the main tip (about 83 deg), two broad side lobes (about 67 deg), two small rounded basal
# lobes flanking the stalk - between shallow notches and a shallow heart notch at the stalk: 10 outline points. The
# top is a fan from one hub vertex on the midrib, so each lobe is exactly two planar facets meeting on its vein (one
# lit, one shaded): the main lobe's two facets meet on the midrib. Round 2's pleat (12 points, raised mid-vein verts,
# deep notches) read as crumpled stars. (u across, v along the leaf toward the tip; x L, the stalk notch at 0, 0)
LEAF_RIGHT = ((0.44, 0.50), (0.80, 0.30), (0.47, 0.04), (0.34, -0.16))   # notch, side lobe, notch, basal lobe
LEAF_HEART = -0.02
LEAF_NOTCH = (1, 3, 7, 9)       # outline indices of the notches between lobes (the heart notch, 5, stays level)
NO = 10                # outline points
HUB_V = 0.15           # the fan's hub on the midrib (x L along from the stalk notch)


def _leaf_uv():
    right = list(LEAF_RIGHT)
    return [(0.0, 1.0)] + right + [(0.0, LEAF_HEART)] + [(-u, v) for u, v in reversed(right)]


LEAF_UV = _leaf_uv()
C_, CB_ = 2 * NO, 2 * NO + 1        # top and bottom hub
# lobe of each outline edge i -> i+1: 2 the main lobe, 1 a side lobe, 0 a basal lobe (tone by position on the leaf)
EDGE_LOBE = (2, 1, 1, 0, 0, 0, 0, 1, 1, 2)


def _leaf_top():
    """0-9 top outline (tip, then the right side down to the heart notch and up the left), 10-19 bottom, 20 / 21 the
    hubs: one facet per outline edge, fanned from the hub."""
    return [[i, (i + 1) % NO, C_] for i in range(NO)]


# the underside: the same fan from its own hub, so the slab keeps one thickness (top and bottom parallel)
LEAF_BOTTOM = [[NO + (i + 1) % NO, NO + i, CB_] for i in range(NO)]
LEAF_POLYS = (_leaf_top() + LEAF_BOTTOM +
              [q for i in range(NO) for q in ([i, (i + 1) % NO, NO + (i + 1) % NO], [i, NO + (i + 1) % NO, NO + i])])
# the lobe of every face (top, bottom, rim) for its tone
LEAF_LOBE = list(EDGE_LOBE) + list(EDGE_LOBE) + [l for l in EDGE_LOBE for _ in range(2)]
SPAN = 2 * max(u for u, v in LEAF_UV)   # the leaf's span (its width across the side lobes) in units of L (1.60)


# Fix round 3: the folds follow the veins only. The lobes droop away from the face by DOME deg (a shallow dome: every
# outline point sits tan(DOME) x its distance from the hub behind the hub), and the four lobe notches sit a further
# DROP x L back, so each vein (hub -> lobe point) is a ridge and each notch spoke a valley: per lobe one lit and one
# shaded planar facet, the midrib a fold between the main lobe's two. No other creases.
DOME = 12.0
DROP = 0.03


def leaf_pts(N, d, n, L, thick=0.055, dome=None, drop=None, aspect=1.0):
    """A closed broad five-lobed slab: the stalk notch at N, the main tip along d (length L), facing n. aspect < 1
    narrows it across (the parts cell's longer centre leaf)."""
    x = d.cross(n).normalized()
    n = x.cross(d).normalized()
    t = math.tan(math.radians(DOME if dome is None else dome))
    dr = DROP if drop is None else drop

    def P(u, v, h):
        return N + (x * (u * aspect) + d * v) * L + n * h

    hs = [-(t * math.hypot(u * aspect, v - HUB_V) + (dr if i in LEAF_NOTCH else 0.0)) * L
          for i, (u, v) in enumerate(LEAF_UV)]
    top = [P(u, v, thick / 2 + h) for (u, v), h in zip(LEAF_UV, hs)]
    bot = [P(u, v, -thick / 2 + h) for (u, v), h in zip(LEAF_UV, hs)]
    return top + bot + [P(0, HUB_V, thick / 2), P(0, HUB_V, -thick / 2)]


# ladder positions (base, body, lobe ends) per role; one step brighter than spec 5.3's first plan after the hero
# render measured D 47 / M 37 / Br 15 / L 0 against the sheet's 37 / 41 / 20 / 3 (stage 4 re-measure)
# Round-3 verification measured the planar-lobe leaf at D 54 / M 35 / Br 7 / L 4 (front median #5D8A18 vs #67A416):
# every role moves up half a band (main session, 2026-11-02).
ROLE = {"under": (0.75, 1.25, 1.75), "outer": (1.0, 1.75, 2.5), "young": (1.75, 2.5, 3.25)}


def leaf_keys(role, shift=0.0):
    """A key per leaf face by its lobe, base to tip (spec 5.3; fix round 3: whole planar lobe facets, so one tone per
    lobe, half a band apart so a leaf reads as one green with its lit and shaded facets): the basal lobes at the stalk
    between base and body, the side lobes the body, the main lobe between body and tip; the role sets the band."""
    b, m, t = (x + shift for x in ROLE[role])
    pos = ((b + m) / 2, m, (m + t) / 2)
    return [_tone(pos[k]) for k in LEAF_LOBE]


def leaf_tints(base, rng):
    band = {}
    out = []
    for k in LEAF_LOBE:
        if k not in band:
            band[k] = rng.uniform(-0.02, 0.02)
        out.append(base + band[k])
    return out


def leaf_frame(n0, phi, tilt, roll):
    """Tip direction and normal of a leaf in a cluster facing n0: phi turns the tip round n0 from straight down (in the
    leaf plane), tilt brings the tip forward (+n0), roll turns the leaf about its own axis."""
    dn = -Z - n0 * (-Z).dot(n0)
    if dn.length < 1e-4:
        dn = Vector((0, -1, 0)) - n0 * Vector((0, -1, 0)).dot(n0)
    dn.normalize()
    s = n0.cross(dn).normalized()
    d = dn * math.cos(phi) + s * math.sin(phi)
    d2 = (d * math.cos(tilt) + n0 * math.sin(tilt)).normalized()
    n2 = (n0 * math.cos(tilt) - d * math.sin(tilt)).normalized()
    x = d2.cross(n2)
    n3 = (n2 * math.cos(roll) + x * math.sin(roll)).normalized()
    return d2, n3


# ---- clusters (spec 2.4) -------------------------------------------------------------------------------------------------
# name: host, hub z (stalk root height), stalk azimuth, cluster facing azimuth (naz) and pitch, fan (the side leaves'
# swing, deg), croll (the centre leaf's roll, deg), stalk length, spans (centre first), role.
# The back-right clusters hang behind the rope (stalks toward the wall) with their leaves turned out to the front-right,
# so they peek out on both sides of the rope as on the front cell, never facing the wall.
# Fix round 1: each cluster is a fan (fan_frames), so its leaves face naz - fan, naz + croll and naz + fan: three planes
# >= 36 deg apart. naz / fan / croll come from a small search that spreads the 28 leaf planes evenly over the front
# half (normals 185 ... 355, every one off the wall), so each 5 deg step of the sweep sees only the unavoidable ~1/6 of
# the leaf planes near edge-on, from different clusters, never two of one cluster (edge_sweep checks the build). swing:
# the side-leaf swing tried first (the one the search assumed; placement may take the other).
# Fix round 3: the smooth leaves (facets within ~14 deg of their plane) no longer hide edge-on behind a crumple, so
# naz / fan / croll / pitch were searched again on the built leaves (whole-leaf sweep, every leaf off the wall, a
# ray-free stand-in for vis_report's edge-on share): pitch now varies -10 ... 16 per cluster (leaf normals -10 ... 25
# deg) as well as yaw (normals 187 ... 358).
CLUSTERS = (
    dict(cid="J2", host="stub", z=6.60, az=318, naz=285, fan=48, croll=-5, pitch=14, L=0.28, spans=(1.19, 1.08, 1.03),
         role="outer", swing="fwd"),
    dict(cid="J1", host="stub", z=6.10, az=222, naz=220, fan=33, croll=10, pitch=-10, L=0.30, spans=(1.24, 1.13, 1.08),
         role="under"),
    dict(cid="C1", host="strand", z=4.95, az=35, naz=318, fan=36, croll=-3, pitch=8, L=0.36, spans=(1.19, 1.13, 1.07),
         role="under"),
    dict(cid="C2", host="strand", z=4.50, az=318, naz=325, fan=33, croll=-4, pitch=2, L=0.16, spans=(0.65, 0.59),
         role="young"),
    dict(cid="C3", host="spur", z=None, az=232, naz=262, fan=41, croll=-14, pitch=2, L=0.20, spans=(1.19, 1.08, 1.03),
         role="outer"),
    dict(cid="C4", host="strand", z=2.65, az=58, naz=293, fan=44, croll=-8, pitch=14, L=0.34, spans=(1.10, 1.04, 0.98),
         role="under", swing="fwd"),
    dict(cid="C5", host="strand", z=2.00, az=212, naz=231, fan=33, croll=0, pitch=2, L=0.25, spans=(1.13, 1.07, 1.01),
         role="outer"),
    dict(cid="C6", host="strand", z=1.10, az=35, naz=325, fan=30, croll=-1, pitch=5, L=0.34, spans=(1.09, 1.01, 0.95),
         role="under", swing="fwd"),
    dict(cid="C7", host="strand", z=0.70, az=275, naz=228, fan=45, croll=8, pitch=16, L=0.18, spans=(0.89, 0.78, 0.71),
         role="young"),
)
# one single small leaf (the lean alternative of spec 4.3 drops the singles; fix round 1: the fanned clusters fill the
# space round the rope, and S3 found no place clear of the strands at z 2.45-3.3, so only S1 is kept: 27 leaves)
SINGLES = (dict(cid="S1", z=5.32, az=340, naz=339, span=0.50),)
TENDRILS = (dict(cid="T1", z=3.25, az=185, L=0.95, curl=0.15), dict(cid="T2", z=1.62, az=355, L=0.85, curl=0.13),
            dict(cid="T3", z=2.62, az=268, L=1.25, curl=0.16))


def _o(az):
    a_ = math.radians(az)
    return Vector((math.cos(a_), math.sin(a_), 0.0))


def _n0(naz, pitch):
    p = math.radians(pitch)
    return (_o(naz) * math.cos(p) + Z * math.sin(p)).normalized()


def host_point(host, z, o):
    """Where a stalk / tendril leaves the wood: (point inside the surface, seat plane normal, host tag)."""
    if host == "stub":
        return Vector((0.0, STUB_Y, z)) + o * (STUB_R * COS30 - 0.012), o, "stub"
    if host == "spur":
        return SPUR["end"] - SPUR["dir"] * 0.03, SPUR["dir"], "spur"
    s = max("AB", key=lambda k: (strand_centre(k, z) - axis_at(z)).normalized().dot(o))
    c = strand_centre(s, z)
    rd = (o - strand_dir(s, z) * o.dot(strand_dir(s, z))).normalized()
    return c + rd * (strand_r(z) * COS30 - 0.02), rd, "strand" + s


def _yaw(v, deg):
    return Matrix.Rotation(math.radians(deg), 3, "Z") @ v


# fix round 1: the fanned clusters spread wider than the stacked ones and hid the rope (front B 12 vs the sheet's
# 19): every hero cluster leaf is scaled by FAN_K
FAN_K = 0.94


def fan_frames(n0, n, fan, croll, lr, swing="back", calm=False):
    """Tip directions and normals of the leaves of one cluster facing n0 (fix round 1: a fan, never a stack of parallel
    leaves). Order: [side, side, centre] (three leaves) or [side, centre] (two). The side leaves leave the hub at
    +-(100..110) deg from straight down in the cluster plane and swing their tips `fan` deg back toward the vine
    (swing "back") or forward ("fwd"); the centre leaf hangs below the hub, its tip 6-10 deg forward, rolled `croll` deg
    about its own axis. So the normals sit near naz - fan, naz + croll and naz + fan: no two leaves of a cluster share a
    plane, whichever way they swing."""
    dn = -Z - n0 * (-Z).dot(n0)
    dn.normalize()
    s = n0.cross(dn).normalized()
    b = math.radians(fan) * (-1.0 if swing == "back" else 1.0)
    out = []
    sg = 1 if lr.random() < 0.5 else -1
    phis = [sg * lr.uniform(100, 110), -sg * lr.uniform(100, 110)][:max(0, n - 1)]
    for phi in phis:
        f = math.radians(phi)
        din = dn * math.cos(f) + s * math.sin(f)
        d = din * math.cos(b) + n0 * math.sin(b)
        nl = n0 * math.cos(b) - din * math.sin(b)
        r = math.radians(lr.uniform(3, 8) * lr.choice((-1, 1)) * (0.5 if calm else 1.0))
        x = d.cross(nl)
        out.append((d, (nl * math.cos(r) + x * math.sin(r)).normalized(), phi))
    f = math.radians(lr.uniform(-6, 6))
    din = dn * math.cos(f) + s * math.sin(f)
    t = math.radians(lr.uniform(6, 10))
    d = din * math.cos(t) + n0 * math.sin(t)
    nl = n0 * math.cos(t) - din * math.sin(t)
    r = math.radians(croll + lr.uniform(-3, 3))
    x = d.cross(nl)
    out.append((d, (nl * math.cos(r) + x * math.sin(r)).normalized(), 0.0))
    return out


def cluster_geom(spec, rng, az_off=0.0, len_k=1.0, size_k=1.0, sep=0.12, calm=False, dz=0.0, swing="back",
                 lat=0.18, cfront=True, stag=0.08):
    """Stalk + leaves of one cluster (lists of shells), not yet added (fix round 1: a fan, as the sheet's cluster cell
    and close-up 2 draw it). The stalk runs out and down from the wood to the hub, then on as a short cross-piece from
    one side leaf's notch to the other's (`lat` either side of the hub, the second `stag` in front of the first, so
    their overlapping bases stack); the side leaves spread out to their sides from those notches; the centre leaf
    hangs below the hub, its notch on the cross-piece, `sep` in front of the side leaves (cfront) or behind them. Each
    leaf faces its own way (fan_frames)."""
    o = _o(spec["az"] + az_off)
    n0 = _n0(spec["naz"], spec["pitch"])          # a placement turn moves the stalk, never the leaves' facing
    z = (spec["z"] + dz) if spec["z"] is not None else SPUR["end"].z
    root, seat, host = host_point(spec["host"], z, o)
    p = math.radians(25.0 if spec["host"] != "spur" else 40.0)
    L = spec["L"] * len_k
    H = root + (o * math.cos(p) - Z * math.sin(p)) * L
    spans = list(spec["spans"])
    n = len(spans)
    lr = random.Random(rng.random())
    fr = fan_frames(n0, n, spec.get("fan", 36.0), spec.get("croll", 0.0), lr, swing, calm)
    shift_i = lr.randrange(n)
    shift = lr.choice((-0.5, 0.5))
    tints = [1.0 + lr.uniform(-0.03, 0.03) for _ in range(n)]
    # spans: centre first in the spec; the frames list the side leaves first
    order = list(range(1, n)) + [0]
    shells, ends = [], []
    cdep = (sep + stag) if cfront else -sep
    for k, (d, nl, phi) in enumerate(fr):
        span = spans[order[k]]
        if k < n - 1:
            sd = (d - n0 * d.dot(n0)).normalized()
            hz = (sd - Z * sd.dot(Z))
            hz = hz.normalized() if hz.length > 1e-4 else sd
            Q = H + hz * lat + n0 * (stag * k)
            ends.append(Q)
            N = Q - d * 0.04
        else:
            Q = H + n0 * cdep
            N = Q - d * 0.05
        Lf = span * size_k * FAN_K / SPAN
        pts = leaf_pts(N, d, nl, Lf)
        keys = leaf_keys(spec["role"], shift if k == shift_i else 0.0)
        shells.append(dict(kind="leaf", pts=pts, polys=LEAF_POLYS, keys=keys,
                           tints=leaf_tints(tints[k], lr), info=dict(c=Q, n=nl, span=span * size_k * FAN_K,
                                                                     role=spec["role"], N=N, d=d, L=Lf)))
    Hc = H + n0 * cdep                  # the centre leaf's notch point: the stalk passes 0.05 inside the leaf there
    # the stalk: out and down from its seat to the hub, then on to the centre leaf's notch; the side leaves sit on the
    # ends of a short cross-stalk through the hub (a second shell crossing the first, as the parts cell draws it)
    SP, spolys, rings, caps = tube([root, H, Hc], [0.04, 0.036, 0.033], 3, Z if abs(o.z) < 0.9 else Vector((1, 0, 0)),
                                   phase=math.radians(90), t_start=seat)
    stalks = [dict(kind="stalk", pts=SP, polys=spolys, keys=[STALK] * len(spolys), tints=[1.0] * len(spolys),
                   info={})]
    if ends:
        a_, b_ = (ends[0], ends[1]) if len(ends) == 2 else (ends[0], H)
        ax_ = (b_ - a_).normalized()
        XP, xpolys, rings, caps = tube([a_ - ax_ * 0.02, b_ + ax_ * 0.02], [0.03, 0.03], 3, n0, phase=math.radians(90))
        stalks.append(dict(kind="stalk", pts=XP, polys=xpolys, keys=[STALK] * len(xpolys),
                           tints=[1.0] * len(xpolys), info={}))
    return stalks + shells, host


def _leaf_clash(shells):
    leaves = [s for s in shells if s["kind"] == "leaf"]
    for i in range(len(leaves)):
        ti = BVHTree.FromPolygons(leaves[i]["pts"], leaves[i]["polys"])
        for j in range(i + 1, len(leaves)):
            if ti.overlap(BVHTree.FromPolygons(leaves[j]["pts"], leaves[j]["polys"])):
                return True
    return False


def _fits(g, shells, host):
    """Badness of a candidate group against what is placed: triangle hits, near verts, the wall, inside the pad."""
    bad = 0
    for s in shells:
        skip = (host,) if s["kind"] in ("stalk", "tendril") else ()
        bad += 10 * g.hits(s["pts"], s["polys"], skip)
        if s["kind"] == "leaf":
            bad += g.near(s["pts"])
            if g.inside_pad(sum(s["pts"], Vector()) / len(s["pts"])):
                bad += 50
        bad += 10 * sum(1 for p in s["pts"] if p.y > -0.01)
    return bad


# placement variants, cheapest change first: (azimuth offset, stalk length factor, leaf size factor, height shift)
VARIANTS = [(da, lk, sk, dz) for dz in (0.0, 0.12, -0.12, 0.25, -0.25) for sk in (1.0, 0.93, 0.86)
            for lk in (1.0, 1.2, 0.85) for da in (0, 12, -12, 24, -24)]
SEPS = (0.08, 0.10, 0.12, 0.14, 0.17, 0.20)     # (the parts cell's cluster search)
# fix round 1, the fanned hero clusters: (calm, side stagger, centre-leaf depth, side-notch offset, swing, centre in
# front), tightest first
CLUSTER_TRIES = [(calm, stag, sep, lat, sw, cf) for calm in (False, True) for cf in (True, False)
                 for lat in (0.28, 0.22, 0.34) for sep in (0.20, 0.16, 0.24, 0.12) for stag in (0.06, 0.10, 0.14)
                 for sw in ("first", "second")]


def _commit(a, g, shells, cid, host):
    for i, s in enumerate(shells):
        tag = f"{cid}:{s['kind']}{i}"
        _add(a, s["pts"], s["polys"], s["keys"], s["tints"], kind=s["kind"], tag=tag, cid=cid)
        g.add(tag, s["pts"], s["polys"])
        if s["kind"] == "leaf":
            INFO.setdefault("leaves", []).append(dict(cid=cid, **{k: v for k, v in s["info"].items()}))


def _place(a, g, cid, make):
    """Try the variants in order; commit the first that cuts nothing (or record the piece as dropped: a missing leaf
    is better than one through the wood). make(variant) -> (shells, host, note) or None."""
    best = None
    for v in VARIANTS:
        got = make(v)
        if got is None:
            continue
        shells, host, note = got
        bad = _fits(g, shells, host)
        if best is None or bad < best[0]:
            best = (bad, shells, host, dict(note, az_off=v[0], len_k=v[1], size_k=v[2], dz=v[3]))
        if bad == 0:
            break
    if best is None or best[0] > 0:
        why = []
        if best:
            for s in best[1]:
                skip = (best[2],) if s["kind"] in ("stalk", "tendril") else ()
                t = BVHTree.FromPolygons(s["pts"], s["polys"])
                why += [f"{s['kind']}x{tag}" for tag, P, PL in g.items if tag not in skip and
                        t.overlap(BVHTree.FromPolygons(P, PL))]
                if any(p.y > -0.01 for p in s["pts"]):
                    why.append(f"{s['kind']}xwall")
        INFO.setdefault("dropped", []).append((cid, best[0] if best else None, best[3] if best else None, why[:6]))
        return False
    INFO.setdefault("variants", {})[cid] = best[3]
    _commit(a, g, best[1], cid, best[2])
    return True


def cluster(a, g, spec, rng):
    seed = rng.random()

    swings = (spec.get("swing", "back"), "fwd" if spec.get("swing", "back") == "back" else "back")

    def make(v):
        da, lk, sk, dz = v
        best = None
        for calm, stag, sep, lat, sw, cf in CLUSTER_TRIES:
            if sw == "first":
                sw = swings[0]
            elif sw == "second":
                sw = swings[1]
            cand, host = cluster_geom(spec, random.Random(seed), da, lk, sk, sep, calm, dz, sw, lat, cf, stag)
            if _leaf_clash(cand):
                continue
            bad = _fits(g, cand, host)
            if best is None or bad < best[0]:
                best = (bad, cand, host, dict(sep=sep, calm=calm, swing=sw, lat=lat, cfront=cf, stag=stag))
            if bad == 0:
                return best[1:]
        return best[1:] if best else None
    return _place(a, g, spec["cid"], make)


def single_geom(spec, rng, az_off=0.0, len_k=1.0, size_k=1.0, dz=0.0):
    o = _o(spec["az"] + az_off)
    root, seat, host = host_point("strand", spec["z"] + dz, o)
    P1 = root + (o * math.cos(math.radians(20)) - Z * math.sin(math.radians(20))) * 0.15 * len_k
    n0 = _n0(spec["naz"], 6)
    d, nl = leaf_frame(n0, math.radians(rng.uniform(-25, 25)), math.radians(rng.uniform(6, 12)), 0.0)
    Lf = spec["span"] * size_k / SPAN
    pts = leaf_pts(P1 - d * 0.04, d, nl, Lf, thick=0.045)
    SP, spolys, rings, caps = tube([root, P1], [0.032, 0.028], 3, Z, phase=math.radians(90), t_start=seat)
    return [dict(kind="stalk", pts=SP, polys=spolys, keys=[STALK] * len(spolys), tints=[1.0] * len(spolys), info={}),
            dict(kind="leaf", pts=pts, polys=LEAF_POLYS, keys=leaf_keys("young"),
                 tints=leaf_tints(1.0 + rng.uniform(-0.03, 0.03), rng),
                 info=dict(c=P1, n=nl, span=spec["span"] * size_k, role="young", N=P1 - d * 0.04, d=d, L=Lf,
                           thick=0.045))], host


def single(a, g, spec, rng):
    seed = rng.random()

    def make(v):
        shells, host = single_geom(spec, random.Random(seed), *v)
        return shells, host, {}
    return _place(a, g, spec["cid"], make)


def tendril_geom(spec, az_off=0.0, len_k=1.0, dz=0.0):
    """A 3-sided green tube: out and down from a strand in a few straight pieces, then one loose curl (a shrinking
    spiral in the plane of its run)."""
    o = _o(spec["az"] + az_off)
    root, seat, host = host_point("strand", spec["z"] + dz, o)
    L = spec["L"] * len_k
    rc = spec["curl"]
    side = o.cross(Z).normalized()
    p1 = root + o * 0.16 - Z * 0.08
    p2 = p1 + o * 0.10 - Z * (0.30 * L)
    p3 = p2 + o * 0.03 - Z * (0.30 * L)
    pts = [root, p1, p2, p3]
    c = p3 + o * rc
    for k, ang in enumerate((235, 310, 385, 460)):
        r = rc * (1.0 - 0.15 * (k + 1))
        a_ = math.radians(ang)
        pts.append(c + (o * math.cos(a_) + Z * math.sin(a_)) * r + side * 0.012 * (k + 1))
    n = len(pts)
    rad = [0.045 - 0.018 * i / (n - 1) for i in range(n)]
    P, polys, rings, caps = tube(pts, rad, 3, side, phase=math.radians(90), t_start=seat)
    keys = []
    for p in polys:
        ci = max((i for i in range(n) if any(q in rings[i] for q in p)), default=0)
        keys.append(_mix(STALK, LEAF_B, 0.5) if ci >= n - 2 else STALK)
    return [dict(kind="tendril", pts=P, polys=polys, keys=keys, tints=[1.0] * len(polys), info={})], host


def tendril(a, g, spec, rng):
    def make(v):
        da, lk, sk, dz = v
        shells, host = tendril_geom(spec, da * 2.0, lk * (0.85 if sk < 1 else 1.0), dz)
        if g.near(shells[0]["pts"][3 * 3:], skip=(host,)):        # the free curl touches nothing
            return None
        return shells, host, {}
    return _place(a, g, spec["cid"], make)


# ---- the hero -------------------------------------------------------------------------------------------------------------
def hero_fn(a):
    REC.clear()
    INFO.clear()
    STRANDS.clear()
    rng = random.Random(63)
    g = Guard()
    att = pad(a, g)
    stub(a, g)
    strands(a, g, rng)
    spur(a, g)
    for spec in CLUSTERS:
        cluster(a, g, spec, rng)
    for spec in SINGLES:
        single(a, g, spec, rng)
    for spec in TENDRILS:
        tendril(a, g, spec, rng)
    INFO["socket"] = [0.0, GY, ROOF]
    return att


# ---- parts (spec 3.5, 3.9) ------------------------------------------------------------------------------------------------
def part_pad(a):
    REC.clear()
    pts, polys, keys = pad_geom()
    _add(a, pts, polys, keys, _pad_tints(pts, polys), kind="pad", tag="pad")
    return PAD_CACHE["attach"]


def _stick(pts, r0, r1, seed, tint=1.0):
    """A 6-sided stick through pts with flat cut ends (vine_cut caps, a one-step band ring 0.06 inside each end)."""
    P = [Vector(p) for p in pts]
    d0 = (P[1] - P[0]).normalized()
    d1 = (P[-1] - P[-2]).normalized()
    full = [P[0], P[0] + d0 * 0.06] + P[1:-1] + [P[-1] - d1 * 0.06, P[-1]]
    L = sum((q - p).length for p, q in zip(full, full[1:]))
    rad, acc = [], 0.0
    for i, p in enumerate(full):
        if i:
            acc += (p - full[i - 1]).length
        rad.append(r0 + (r1 - r0) * acc / L)
    V, polys, rings, caps = tube(full, rad, 6, Vector((0, -1, 0)) if abs(d0.y) < 0.9 else Z, phase=math.radians(90))
    nring = len(full)
    keys = []
    for p in polys:
        ris = {i for i in range(nring) for q in p if q in rings[i]}
        if len(ris) == 1:
            keys.append(VINE_C)
        elif min(ris) == 0 or max(ris) == nring - 1:
            keys.append(_mix(VINE, VINE_C, 0.5))
        else:
            keys.append(VINE)
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    tints = [tint * (1.0 + 0.02 * 1.6 * noise.noise(_centroid(V, p) * 1.4 + off)) for p in polys]
    return V, polys, keys, tints


def part_segment(a):
    REC.clear()
    top = Vector((0.0, 0.0, 1.8))
    bend = top - Z * 0.99
    bot = bend + Vector((-math.sin(math.radians(15)), 0.0, -math.cos(math.radians(15)))) * 0.81
    mid1 = top.lerp(bend, 0.5) + Vector((0.01, 0.0, 0.0))
    mid2 = bend.lerp(bot, 0.5)
    V, polys, keys, tints = _stick([top, mid1, bend, mid2, bot], 0.18, 0.165, 11)
    _add(a, V, polys, keys, tints, kind="stick", tag="seg")
    return top


FORK_J = Vector((0.0, 0.0, 1.0))


def part_fork(a):
    """The Y: a leg down (one slight bend) and two arms, up-left at 58 deg and up-right at 45 deg from vertical, each a
    stick that runs 0.14 into the junction; unioned into one shell after the build (union_loose)."""
    REC.clear()
    J = FORK_J
    leg_d = Vector((0.04, 0.0, -1.0)).normalized()
    arms = [(Vector((-math.sin(math.radians(58)), 0.0, math.cos(math.radians(58)))), 0.75, 21),
            (Vector((math.sin(math.radians(45)), 0.0, math.cos(math.radians(45)))), 0.85, 22)]
    V, polys, keys, tints = _stick([J - leg_d * 0.10, J + leg_d * 0.5, J + leg_d * 0.5 + Vector((0.03, 0, -0.5))],
                                   0.18, 0.17, 20)
    _add(a, V, polys, keys, tints, kind="stick", tag="leg")
    for d, L, sd in arms:
        V, polys, keys, tints = _stick([J - d * 0.14, J + d * (L * 0.5), J + d * L], 0.175, 0.16, sd)
        _add(a, V, polys, keys, tints, kind="stick", tag=f"arm{sd}")
    return J


CLUS_SPEC = dict(cid="P", spans=(1.0, 0.80, 0.78), role="outer")
CLUS_DROP = 0.14         # the part's centre-leaf notch under the hub
CLUS_JOIN = 0.10         # fix round 3: the side leaves' notches this far under the hub, behind the centre leaf's top
CLUS_TOP = 0.65          # the stalk's top (the pivot) above the hub


def part_cluster(a):
    """The parts cell's cluster: the stalk rising from the hub to the pivot on top; at its foot a short V-stalk
    whose ends hold the two side leaves, spreading out; one bigger, longer centre leaf hanging below
    the hub on the stalk's own end, in front, overlapping only the side leaves' inner lobes. Leaves face about -Y (the
    part's front), each its own way."""
    REC.clear()
    rng = random.Random(77)
    hub = Vector((0.0, 0.0, 0.0))
    top = hub + Vector((0.0, 0.03, CLUS_TOP))
    n0 = _n0(270, 8)
    xs = Vector((1.0, 0.0, 0.0))
    # fix round 1: laid out like the cell - the side leaves spread out from the ends of the V-stalk,
    # clear of the centre leaf, which hangs below the hub (its notch DROP under it) and overlaps their inner lobes
    # only; each leaf faces its own way (fan_frames: sides +-22 deg, centre rolled 8 deg), never one plane.
    # Fix round 3: the side leaves hang from a short V-stalk (hub -> each notch, CLUS_JOIN under the hub) that the
    # centre leaf's top hides, instead of round 2's straight cross-stalk, which showed as a T-bar above it.
    best = None
    for sw, spread, sep in [(sw, sp, se) for sw in ("fwd", "back") for sp in (0.30, 0.34, 0.38)
                            for se in (0.16, 0.20, 0.24, 0.28)]:
        fr = fan_frames(n0, 3, 22.0, 8.0, random.Random(77), sw)
        shells, ends = [], []
        for k in range(2):
            d, nl, phi = fr[k]
            sg = 1.0 if d.x > 0 else -1.0
            E = hub + xs * (sg * spread) - Z * CLUS_JOIN + n0 * (k * 0.05)
            shells.append(dict(kind="leaf", pts=leaf_pts(E - d * 0.04, d, nl, CLUS_SPEC["spans"][1 + k] / SPAN),
                               polys=LEAF_POLYS, keys=leaf_keys("outer" if k else "under"),
                               tints=leaf_tints(1.0 + rng.uniform(-0.03, 0.03), rng)))
            ends.append(E)
        d, nl, phi = fr[2]
        Qc = hub + n0 * sep - Z * CLUS_DROP
        shells.append(dict(kind="leaf", pts=leaf_pts(Qc - d * 0.05, d, nl, CLUS_SPEC["spans"][0] / SPAN * 1.25,
                                                     aspect=0.70),
                           polys=LEAF_POLYS,
                           keys=leaf_keys("outer"), tints=leaf_tints(1.0 + rng.uniform(-0.03, 0.03), rng)))
        if not _leaf_clash(shells):
            best = (shells, ends, Qc)
            break
    shells, ends, Qc = best
    SP, spolys, rings, caps = tube([top, hub, Qc], [0.04, 0.034, 0.03], 4, Vector((1, 0, 0)), phase=math.radians(45))
    _add(a, SP, spolys, STALK, 1.0, kind="stalk", tag="stalk")
    BP, bpolys, rings, caps = tube([ends[1] + (ends[1] - hub).normalized() * 0.03, hub,
                                    ends[0] + (ends[0] - hub).normalized() * 0.03], [0.03, 0.03, 0.03], 4, Z,
                                   phase=math.radians(45))
    _add(a, BP, bpolys, STALK, 1.0, kind="stalk", tag="crossstalk")
    for i, s in enumerate(shells):
        _add(a, s["pts"], s["polys"], s["keys"], s["tints"], kind="leaf", tag=f"leaf{i}")
    return top


PARTS = ((PAD_P, part_pad), (SEG_P, part_segment), (FORK_P, part_fork), (CLUS_P, part_cluster))
ATTACH_NOTES = {
    HERO: "attach: the pad's back-face centre, normal +Y into the wall, up +Z; put it on a wall, cliff, ruin or trunk "
          "face with the object's -Y facing out; nothing lies behind the wall plane",
    PAD_P: "attach: the back-face centre, normal +Y into the wall; the socket groove takes a Segment end",
    SEG_P: "attach: the top end centre, the stick hanging along -Z; chain under a Pad socket or another stick's end",
    FORK_P: "attach: the junction, the leg hanging along -Z, arms up-left and up-right",
    CLUS_P: "attach: the stalk's top end (the pivot); seat it 0.02 into a stick, leaves hanging below",
}
NOTES = {
    HERO: "063 Hanging Vine hero: a 2.3 x 2.0 x 7.5 wall-mounted vine: a cracked faceted stone pad with a socket groove, "
          "a woody stub, two twisted 6-sided strands with a fork spur, nine fanned five-point-leaf clusters, one "
          "single leaf and three tendril curls. Dressing: no collision. No VFX (the sheet shows none). " + ATTACH_NOTES[HERO],
}
NOTES.update({k: f"063 Hanging Vine part. {v}. No collision: dressing." for k, v in ATTACH_NOTES.items() if k != HERO})
COLLISION = {HERO: "none", **{k: "none" for k in PART_NAMES}}


# ---- objects ----------------------------------------------------------------------------------------------------------------
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
    att = fn(a)
    RECS[name] = list(REC)
    o = a.finish(collection=M.coll(NUM, TITLE), mark_asset=not temp, origin=None)
    K.drop_unused_slots(o)
    if not temp:
        K.tag(o, SHEET, TITLE, role, COLLISION[name], budget, NOTES[name])
    o["kit_shading_ok"] = ("leaves coloured by role and by position along each leaf, wood by height, stone by height "
                           "in the pad (spec 5.3): material regions, not light")
    o[OFF] = [0.0, 0.0, 0.0]
    o["m063_attach_build"] = list(att) if att is not None else [0.0, 0.0, 0.0]
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
    o[ATT] = [round(x, 4) for x in Vector(o["m063_attach_build"]) - Vector(o[OFF])]
    if o.name == HERO:
        o["m063_socket"] = [round(x, 4) for x in Vector(INFO.get("socket", (0, 0, 0))) - Vector(o[OFF])]


def _post(o, union=False):
    """Stage 2-3 pass on an object of closed shells: (optional exact union), triangles only, each shell's volume checked
    and reversed if inward, flat shading, origin at the bbox bottom centre, bowties split, angle-based UVs with
    overlaps cut free."""
    lg = {}
    if union:
        lg["unioned"] = M.union_loose(o, merge=0.002)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    groups = [[] for _ in range(n)]
    for f in bm.faces:
        groups[ids[f.index]].append(f)
    flipped = 0
    for fs in groups:
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs)
        if vol < 0:
            bmesh.ops.reverse_faces(bm, faces=fs)
            flipped += 1
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = False
    if o.data.has_custom_normals:
        with M._override(o):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
    _recentre(o)
    lg.update(flipped_shells=flipped, bowties=M.fix_bowties(o))
    M.smart_uv(o, **UV)
    lg["uv_cut"] = m012._uv_unfold(o)
    K.drop_unused_slots(o)
    return lg


def _make(name, fn, role="part", budget=PART_LIMIT, temp=False):
    t0 = time.time()
    o = _new(name, fn, role, budget, temp=temp)
    lg = _post(o, union=(name == FORK_P))
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


# ---- checks -------------------------------------------------------------------------------------------------------------------
WOOD = ("strand", "stub", "spur", "stick")
FOLIAGE = ("leaf", "stalk", "tendril")


def _shell_table(o):
    """The object's shells, each matched to its build record (kind, tag, cluster) by centroid."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    groups = [[] for _ in range(n)]
    for f in bm.faces:
        groups[ids[f.index]].append(f)
    off = Vector(o[OFF])
    recs = RECS.get(o.name, [])
    rc = [sum(r["pts"], Vector()) / len(r["pts"]) for r in recs]
    info = []
    for fs in groups:
        vs = list({v for f in fs for v in f.verts})
        c = sum((v.co for v in vs), Vector()) / len(vs) + off
        if recs:
            j = min(range(len(recs)), key=lambda k: (rc[k] - c).length)
            r = recs[j]
            info.append(dict(kind=r["kind"], tag=r["tag"], cid=r["cid"], match=round((rc[j] - c).length, 4)))
        else:
            info.append(dict(kind="?", tag="?", cid="", match=None))
    return bm, ids, n, groups, info


def shells_report(o):
    bm, ids, n, groups, info = _shell_table(o)
    out = []
    for k in range(n):
        fs = groups[k]
        es = {e for f in fs for e in f.edges}
        vs = list({v for f in fs for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        hits = sum(1 for a_, b_ in tree.overlap(tree) if a_ < b_ and not set(fs[a_].verts) & set(fs[b_].verts))
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) / 3.0
        out.append({"kind": info[k]["kind"], "tag": info[k]["tag"], "tris": len(fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary),
                    "winding_errors": sum(1 for e in es if e.is_manifold and not e.is_contiguous),
                    "self_hits": hits, "volume": round(vol, 5), "match": info[k]["match"]})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating dressing: per shell, the nearest other shell (triangles intersect, or a vert within chain_tol), and
    whether it chains by contact <= tol to the anchor (the pad, which sits on the wall; for a part its biggest shell)."""
    bm, ids, n, groups, info = _shell_table(o)
    fsh = [ids[f.index] for f in bm.faces]
    vsh = {}
    for f in bm.faces:
        for v in f.verts:
            vsh[v.index] = fsh[f.index]
    tree = BVHTree.FromBMesh(bm)
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
    anchor = {k for k in range(n) if info[k]["kind"] == "pad"} or {max(range(n), key=lambda k: len(groups[k]))}
    gap = [1e9] * n
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    for k in anchor:
        gap[k] = 0.0
    adj = {k: set() for k in range(n)}
    for (a_, b_), d in near.items():
        if d <= tol:
            adj[a_].add(b_)
            adj[b_].add(a_)
    seen, stack = set(anchor), list(anchor)
    while stack:
        k = stack.pop()
        for m_ in adj[k]:
            if m_ not in seen:
                seen.add(m_)
                stack.append(m_)
    floating = [k for k in range(n) if gap[k] > tol]
    unch = [k for k in range(n) if k not in seen]
    kinds = [i["kind"] for i in info]
    res = {"shells": n, "floating": len(floating), "floating_at": [info[k]["tag"] for k in floating[:8]],
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3), "unchained": len(unch),
           "unchained_at": [info[k]["tag"] for k in unch[:8]], "kinds": {k: kinds.count(k) for k in sorted(set(kinds))}}
    bm.free()
    return res


ALLOWED = {("leaf", "stalk"), ("stalk", "stalk"), ("stalk", "strand"), ("stalk", "stub"), ("spur", "stalk"), ("strand", "tendril"),
           ("strand", "strand"), ("strand", "stub"), ("spur", "strand"), ("stick", "stick")}


def clash_report(o):
    """Shell pairs whose triangles intersect. Allowed by design: a leaf on its own stalk, a stalk / tendril / spur root in
    its wood, the two strands along the twist, the strand tops in the stub. Anything else is reported."""
    bm, ids, n, groups, info = _shell_table(o)
    tree = BVHTree.FromBMesh(bm)
    fsh = [ids[f.index] for f in bm.faces]
    pairs = {}
    for i, j in tree.overlap(tree):
        a_, b_ = fsh[i], fsh[j]
        if a_ != b_:
            pairs[(min(a_, b_), max(a_, b_))] = pairs.get((min(a_, b_), max(a_, b_)), 0) + 1
    bad = []
    for (a_, b_), cnt in pairs.items():
        ka, kb = info[a_]["kind"], info[b_]["kind"]
        kk = tuple(sorted((ka, kb)))
        ok = kk in ALLOWED
        if kk == ("leaf", "stalk") and info[a_]["cid"] != info[b_]["cid"]:
            ok = False
        if ok:
            continue
        bad.append((info[a_]["tag"], info[b_]["tag"], cnt))
    bm.free()
    return {"pairs": len(pairs), "bad": len(bad), "bad_at": bad[:10]}


def bury_report(o):
    """Ray parity of every shell's verts and face centres against each solid (pad, stub, strands, spur): the deepest
    point inside another solid, per shell; limits by kind (spec 6)."""
    bm, ids, n, groups, info = _shell_table(o)
    sol = m047._Solids()
    for k in range(n):
        if info[k]["kind"] in ("pad", "stub", "strand", "spur"):
            vs = list({v for f in groups[k] for v in f.verts})
            vi = {v: i for i, v in enumerate(vs)}
            sol.add([v.co for v in vs], [[vi[v] for v in f.verts] for f in groups[k]], info[k]["tag"])
    lim = {"leaf": 0.03, "stalk": 0.035, "tendril": 0.035, "spur": 0.05, "strand": 0.05, "stub": 0.03, "pad": 0.0}
    worst = {}
    over = []
    for k in range(n):
        fs = groups[k]
        pts = list({v.co.copy().freeze() for f in fs for v in f.verts}) + [f.calc_center_median() for f in fs]
        d, who = max((sol.point(Vector(p), skip=(info[k]["tag"],)) for p in pts), key=lambda r: r[0])
        kd = info[k]["kind"]
        if d > worst.get(kd, (0.0, None))[0]:
            worst[kd] = (round(d, 3), who, info[k]["tag"])
        if d > lim.get(kd, 0.03) + 1e-4:
            over.append((info[k]["tag"], round(d, 3), who))
    bm.free()
    return {"worst": worst, "over": len(over), "over_at": over[:8]}


def wall_report(o):
    """Nothing behind the wall plane: max build-frame y per kind; the pad's back face on y = 0."""
    bm, ids, n, groups, info = _shell_table(o)
    off = Vector(o[OFF])
    my = {}
    for k in range(n):
        y = max(v.co.y for f in groups[k] for v in f.verts) + off.y
        kd = info[k]["kind"]
        my[kd] = max(my.get(kd, -9.0), y)
    back = [v.co.y + off.y for v in bm.verts if abs(v.co.y + off.y) < 0.01]
    bm.free()
    cross = sum(1 for kd, y in my.items() if (kd != "pad" and y > -0.005) or y > 0.0005)
    return {"max_y": {k: round(v, 4) for k, v in my.items()}, "crossing": cross,
            "pad_back_verts": len(back), "pad_back_dev": round(max((abs(y) for y in back), default=0.0), 5)}


def _cam(az, el):
    a_, e_ = math.radians(az), math.radians(el)
    return Vector((math.sin(a_) * math.cos(e_), -math.cos(a_) * math.cos(e_), math.sin(e_)))


SPIN_AZ = (0, 45, 90, 135, 180, 225, 270, 315)
FRONT_HALF = (0, 45, 90, 270, 315)


def vis_report(o, el=5.0, step=0.03):
    """Eight-azimuth ray-grid visibility (vis.py for a wall-mounted vine): per camera azimuth, the share of the visible
    vine that is bare wood (strands, stub, spur) against foliage, the share of visible leaf pixels seen within 20 deg
    of edge-on, and the rope continuity (z bins 0.25 tall from 0.6 to 5.5 where wood shows). Binding in the five
    front-half views (spec 3.12)."""
    bm, ids, n, groups, info = _shell_table(o)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    fk = [info[ids[f.index]]["kind"] for f in bm.faces]
    # leaf rims (the slab's thickness band) are edge-on by construction: counted apart, not as edge-on leaves
    rim = set()
    for k in range(n):
        if info[k]["kind"] == "leaf":
            big = max(groups[k], key=lambda f: f.calc_area())
            rim |= {f.index for f in groups[k] if abs(f.normal.dot(big.normal)) < 0.6}
    off = Vector(o[OFF])
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    c = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2))
    R = max(max(xs) - min(xs), max(ys) - min(ys)) * 0.75 + 0.2
    H = (max(zs) - min(zs)) / 2 + 0.2
    out = {}
    for az in SPIN_AZ:
        d = _cam(az, el)
        u = Z.cross(d).normalized()
        w = d.cross(u).normalized()
        cnt = {}
        edge = leafpx = rimpx = 0
        by = {}
        bins = set()
        ni, nj = int(R / step), int(H / step)
        for i in range(-ni, ni + 1):
            for j in range(-nj, nj + 1):
                p = c + u * (i * step) + w * (j * step) + d * 20.0
                loc, nrm, fi, dist = tree.ray_cast(p, -d, 60.0)
                if loc is None:
                    continue
                kd = fk[fi]
                cnt[kd] = cnt.get(kd, 0) + 1
                if kd == "leaf":
                    if fi in rim:
                        rimpx += 1
                    else:
                        leafpx += 1
                        if abs(nrm.dot(d)) < 0.35:
                            edge += 1
                            tg = info[ids[fi]]["tag"]
                            by[tg] = by.get(tg, 0) + 1
                if kd in WOOD:
                    zb = loc.z + off.z
                    if 0.6 <= zb <= 5.5:
                        bins.add(int((zb - 0.6) / 0.25))
        wood = sum(cnt.get(k, 0) for k in WOOD)
        fol = sum(cnt.get(k, 0) for k in FOLIAGE)
        out[az] = {"wood_share": round(100 * wood / max(1, wood + fol), 1),
                   "edge_on_leaf": round(100 * edge / max(1, leafpx), 1),
                   "rim_share": round(100 * rimpx / max(1, leafpx + rimpx), 1),
                   "rope_bins": f"{len(bins)}/{int(4.9 / 0.25) + 1}",
                   "edge_by": sorted(by.items(), key=lambda kv: -kv[1])[:4],
                   "pad_share": round(100 * cnt.get("pad", 0) / max(1, sum(cnt.values())), 1)}
    bm.free()
    return out


NT_TOP = len(_leaf_top())
EDGE15 = math.sin(math.radians(15.0))
SWEEP_AZ = tuple(range(-175, 181, 5))    # all 72 camera azimuths (0 = the front, -Y); |az| <= 90 is the front half


def _leaf_solids(recs):
    """Per leaf record: its outward area vectors, the mean normal of its top faces and its face-on projected area."""
    out = []
    for r in recs:
        if r["kind"] != "leaf":
            continue
        P = r["pts"]
        fs = []
        for j, p in enumerate(r["polys"]):
            for i in range(1, len(p) - 1):
                a_, b_, c_ = P[p[0]], P[p[i]], P[p[i + 1]]
                fs.append(((b_ - a_).cross(c_ - a_) * 0.5, j < NT_TOP))
        top = [f for f, t in fs if t]
        ref = max(top, key=lambda f: f.length)
        n = sum((f if f.dot(ref) >= 0 else -f for f in top), Vector()).normalized()
        fs = [f for f, t in fs]
        # a closed shell's projected area is half the sum of |area vector . view| (every ray crosses it twice)
        face_on = 0.5 * sum(abs(f.dot(n)) for f in fs)
        # fix round 3: how far the top (lobe) facets tilt off the leaf plane, area-weighted mean and max (deg)
        tilts = [(math.degrees(math.acos(min(1.0, abs(f.normalized().dot(n))))), f.length) for f in top]
        out.append(dict(cid=r["cid"], tag=r["tag"], n=n, fs=fs, top=top, top_area=sum(f.length for f in top),
                        face_on=face_on, tilt=sum(t * a_ for t, a_ in tilts) / sum(a_ for t, a_ in tilts),
                        tilt_max=max(t for t, a_ in tilts)))
    return out


WHOLE = 0.75       # a leaf is wholly edge-on when this share of its top-face area is within 15 deg of edge-on


def edge_sweep(recs=None, el=5.0):
    """Edge-on leaves between the eight test views (STAGES "Check between the eight views too"): all 72 camera azimuths
    in 5 deg steps at e 5 (binding in the front half, |az| <= 90; the wall hides the rest). Per step:
    - plane: leaves whose mean (top-face) plane is within 15 deg of edge-on (|n.d| < sin 15): the verifier's leafn.py
      measure. Every plane contains a horizontal direction, so every leaf is in this band for >= 30 of every 180 deg
      of azimuth, whatever its facing: averaged over the sweep the band holds >= 1/6 (16.7 %) of the leaf area for any
      leaf set, so this measure has a floor and is reported, not limited. What it must not show is a comb (two leaves
      of one cluster at once) or a pile-up well above the floor; the facings are spread so it stays near it;
    - whole: whole leaves edge-on: >= 75 % of the leaf's top-face area (its lobe facets) within 15 deg of edge-on;
    - sliver: the leaf's projected area under sin 15 (0.26) of its face-on area (exactly "within 15 deg of edge-on"
      for a flat card; a creased slab keeps its lobe facets and thickness in view).
    Limits (front half; SWEEP_LIMITS, ruling for round 3): whole at most 10 % of the leaf area, sliver at most 15 %,
    at every step; never two leaves of one cluster whole-edge-on or slivers together (comb_edge). The plane-band comb
    is reported only.
    Also the closest pair of leaf planes in each cluster (no two leaves of a cluster on one plane: >= 20 deg)."""
    recs = recs if recs is not None else RECS.get(HERO, [])
    lv = _leaf_solids(recs)
    if not lv:
        return {}
    tot = sum(l["face_on"] for l in lv)
    steps = {}
    keys = ("plane_n", "plane_area", "whole_n", "whole_area", "sliver_n", "sliver_area", "comb", "comb_edge")
    worst = {k: 0 for k in keys}
    worst_rear = {k: 0 for k in keys}
    worst_at = {}
    for az in SWEEP_AZ:
        d = _cam(az, el)
        pl = [l for l in lv if abs(l["n"].dot(d)) < EDGE15]
        wh = [l for l in lv if sum(f.length for f in l["top"] if abs(f.normalized().dot(d)) < EDGE15)
              >= WHOLE * l["top_area"]]
        sl = [l for l in lv if 0.5 * sum(abs(f.dot(d)) for f in l["fs"]) < EDGE15 * l["face_on"]]
        per, pe = {}, {}
        for l in pl:
            per[l["cid"]] = per.get(l["cid"], 0) + 1
        for l in {id(l): l for l in sl + wh}.values():
            pe[l["cid"]] = pe.get(l["cid"], 0) + 1
        s = {"plane_n": len(pl), "plane_area": round(100 * sum(l["face_on"] for l in pl) / tot, 1),
             "whole_n": len(wh), "whole_area": round(100 * sum(l["face_on"] for l in wh) / tot, 1),
             "sliver_n": len(sl), "sliver_area": round(100 * sum(l["face_on"] for l in sl) / tot, 1),
             "comb": max(per.values(), default=0), "comb_edge": max(pe.values(), default=0),
             "slivers": [l["tag"] for l in sl + wh]}
        steps[az] = s
        w = worst if abs(az) <= 90 else worst_rear
        for k in keys:
            if s[k] > w[k]:
                w[k] = s[k]
                if w is worst:
                    worst_at[k] = az
    planes = {}
    for cid in sorted({l["cid"] for l in lv}):
        ns = [l["n"] for l in lv if l["cid"] == cid]
        if len(ns) > 1:
            planes[cid] = round(min(math.degrees(math.acos(min(1.0, abs(ns[i].dot(ns[j])))))
                                    for i in range(len(ns)) for j in range(i + 1, len(ns))), 1)
    naz = sorted(round(math.degrees(math.atan2(l["n"].y, l["n"].x)) % 180) + 180 for l in lv)   # as lines, front half
    fr = [s["plane_area"] for az, s in steps.items() if abs(az) <= 90]
    tl = [l["tilt"] for l in lv]
    return {"worst": worst, "worst_at": worst_at, "worst_rear": worst_rear, "plane_mean": round(sum(fr) / len(fr), 1),
            "steps": steps, "min_plane_angle": planes, "normal_az": naz, "leaves": len(lv),
            "facet_tilt": {"mean": round(sum(tl) / len(tl), 1), "leaf_min": round(min(tl), 1),
                           "leaf_max": round(max(tl), 1), "max": round(max(l["tilt_max"] for l in lv), 1)},
            "outline_points": NO}


# front-half limits per 5 deg step (ruling, targeted round 3): whole leaves edge-on at most about 10 % of the leaf
# area (3 leaves); sliver leaves at most 15 %; never two leaves of one cluster whole-edge-on or slivers together
SWEEP_LIMITS = {"whole": (3, 10.0), "sliver": (99, 15.0)}


def sweep_problems(sw):
    out = []
    w = sw.get("worst", {})
    front = {az: s for az, s in sw.get("steps", {}).items() if abs(az) <= 90}
    for k, (ln, la) in SWEEP_LIMITS.items():
        if w.get(k + "_n", 0) > ln or w.get(k + "_area", 0) > la:
            bad = {az: (s[k + "_n"], s[k + "_area"]) for az, s in front.items()
                   if s[k + "_n"] > ln or s[k + "_area"] > la}
            out.append(f"{HERO}: {k} edge-on leaves over {ln} / {la} % at az {bad}")
    if w.get("comb_edge", 0) > 1:
        out.append(f"{HERO}: two leaves of one cluster edge-on (whole or sliver) together at az "
                   f"{[az for az, s in front.items() if s['comb_edge'] > 1]}")
    flat = {c: a for c, a in sw.get("min_plane_angle", {}).items() if a < 20}
    if flat:
        out.append(f"{HERO}: leaves of one cluster on (nearly) one plane {flat}")
    return out


def leaf_report():
    lv = INFO.get("leaves", [])
    if not lv:
        return {}
    spans = sorted(l["span"] for l in lv)
    return {"leaves": len(lv), "roles": {r: sum(1 for l in lv if l["role"] == r) for r in ROLE},
            "span_min_med_max": [round(spans[0], 2), round(spans[len(spans) // 2], 2), round(spans[-1], 2)],
            "variants": INFO.get("variants", {}), "dropped": INFO.get("dropped", [])}


TARGET_SIZE = ((2.3, 0.2), (2.0, 0.2), (7.5, 0.3))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m063_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", "TwistedVine"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build_hero():
    M.coll(NUM, TITLE)
    palette()
    PAD_CACHE.clear()
    return _make(HERO, hero_fn, "hero", HERO_LIMIT)


def build(render=True, parts=True, close=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    PAD_CACHE.clear()
    objs, log = {}, {}
    h, log[HERO] = _make(HERO, hero_fn, "hero", HERO_LIMIT)
    li = leaf_report()
    hero_info = dict(INFO)
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn)
    _cleanup_tmp()
    order = [h] + [objs[n] for n in PART_NAMES if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.2f} x {d.y:.2f} x {d.z:.2f}"
    audits = [M.audit(o) for o in order]
    shells = {o.name: shells_report(o) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = HERO_LIMIT if o is h else PART_LIMIT
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
                    problems.append(f"{o.name} shell {i} ({s['tag']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['tag']}): not closed outward (volume {s['volume']})")
    contact = {o.name: contact_report(o) for o in order}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} floating {c['floating_at']}, {c['unchained']} unchained "
                            f"{c['unchained_at']}")
    clash = {o.name: clash_report(o) for o in order}
    for n_, c in clash.items():
        if c["bad"]:
            problems.append(f"{n_}: {c['bad']} shell pairs pass through each other {c['bad_at'][:4]}")
    bury = {o.name: bury_report(o) for o in (h,) + tuple(objs[n] for n in (PAD_P,) if n in objs)}
    for n_, b in bury.items():
        if b["over"]:
            problems.append(f"{n_}: {b['over']} shells buried past their limit {b['over_at'][:4]}")
    wall = wall_report(h)
    if wall["crossing"]:
        problems.append(f"{HERO}: something behind the wall plane {wall['max_y']}")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    for o in order:
        if [c for c in o.children if c.get("vfx_kind")]:
            problems.append(f"{o.name}: has VFX sockets (decision 11: none)")
    if li.get("dropped"):
        problems.append(f"{HERO}: clusters dropped {li['dropped']}")
    sweep = edge_sweep(RECS.get(HERO, []))
    problems += sweep_problems(sweep)
    vis = vis_report(h)
    for az in FRONT_HALF:
        v = vis[az]
        if v["wood_share"] > 30 or v["edge_on_leaf"] > 10:
            problems.append(f"{HERO}: az {az} wood {v['wood_share']} % / edge-on {v['edge_on_leaf']} % (limits 30 / 10)")
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
           "hero_shells": kinds, "contact": contact, "clash": clash, "bury": bury, "wall": wall, "winding": winding,
           "vis": vis, "sweep": {k: v for k, v in sweep.items() if k != "steps"}, "leaves": li, "log": log,
           "problems": problems, "uv": uv,
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "attach": {o.name: list(o.get(ATT, [])) for o in order}, "socket": list(h.get("m063_socket", [])),
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders --------------------------------------------------------------------------------------------------------------------
# decision 9: front_sheet (0, 6) governs, side_sheet (90, 6) positions in depth, rear / top content; *_sheet shots use
# the long lens with the floor hidden (m033._long_lens).
SHEET_VIEWS = {"front_sheet": (0, 6), "side_sheet": (90, 6), "rear_sheet": (180, 6), "top_sheet": (0, 89)}
VIEW_NAMES = ("front34", "rear34", "front", "side", "rear", "top", "underside")
PARTS_SHOT = (-15, 15)
SPIN_EL = 10


def _at(o, p):
    """Build-frame point p in world space for object o."""
    return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)


def _temp_obj(name, fn):
    a = K.fk().Asset(PFX + name, "probe", seed=1, tint_var=0.0)
    fn(a)
    o = a.finish(collection=M.coll(NUM, TITLE), mark_asset=False, origin=None)
    bpy.context.view_layer.update()
    return o


def _box(a, x0, x1, y0, y1, z0, z1, key=STONE, tint=1.1):
    pts = [Vector((x, y, z)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    polys = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    fs = [bm.faces.new([vs[i] for i in p]) for p in polys]
    m056._orient(bm, fs)
    mi = a._mi(key)
    for f in fs:
        f.material_index = mi
        for l in f.loops:
            l[a.tint_layer] = (tint, tint, tint, 1.0)


def _copy(o, name, m):
    """A linked copy of o placed so its attach frame (the attach point, +Y into the wall) sits at world matrix m."""
    c = bpy.data.objects.new(PFX + name, o.data)
    M.coll(NUM, TITLE).objects.link(c)
    c.matrix_world = m @ Matrix.Translation(-Vector(o["m063_attach_build"])) @ Matrix.Translation(Vector(o[OFF]))
    return c


def _marker(at, name):
    """A 5.5-stud stand-in character (body 3.3, chest 0.9, head 1.2)."""
    a = K.fk().Asset(PFX + name, "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=STONE_D, tint=0.6)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.3), mat=STONE_D, tint=0.6)
    a.cyl(0.55, 0.3, 1.3, sides=8, loc=(0, 0, 4.2), mat=STONE_D, tint=0.6)
    c = a.finish(collection=M.coll(NUM, TITLE), mark_asset=False)
    c.location = at
    bpy.context.view_layer.update()
    return c


def _exploded(objs, base):
    """The sheet's exploded view from the parts: the pad with a segment in its socket and a cluster at the joint; below
    it with gaps a segment, the fork (arm up-left), a segment, a segment with two clusters, the tip cluster."""
    by = {o.name: o for o in objs}
    shown = []
    if PAD_P not in by:
        return shown
    rot = Matrix.Rotation(math.radians(180), 4, "Z")     # the parts face -Y; the pad's back stays behind
    put = [(PAD_P, Matrix.Translation((0.0, 0.0, 10.4))),
           (SEG_P, Matrix.Translation((0.0, -0.75, 10.7))),
           (CLUS_P, Matrix.Translation((-0.35, -1.0, 9.9))),
           (SEG_P, Matrix.Translation((0.05, -0.75, 8.6))),
           (FORK_P, Matrix.Translation((0.0, -0.75, 5.85))),
           (CLUS_P, Matrix.Translation((-1.25, -1.3, 7.6))),
           (CLUS_P, Matrix.Translation((1.2, -1.3, 8.6))),
           (SEG_P, Matrix.Translation((0.05, -0.75, 4.5))),
           (CLUS_P, Matrix.Translation((-1.2, -1.3, 4.9))),
           (CLUS_P, Matrix.Translation((1.15, -1.3, 5.9))),
           (SEG_P, Matrix.Translation((0.05, -0.75, 2.3))),
           (CLUS_P, Matrix.Translation((-0.5, -1.3, 1.3))),
           (CLUS_P, Matrix.Translation((0.55, -1.3, 1.0))),
           (CLUS_P, Matrix.Translation((0.0, -1.2, 0.15)))]
    for i, (nm, m) in enumerate(put):
        shown.append(_copy(by[nm], f"expl{i}", base @ m))
    del rot
    bpy.context.view_layer.update()
    return shown


def _context(h, base):
    """Context only (not exported): a plain 6 x 3 x 7 stone block like the assembled cells, two hero copies on its front
    face and one on its right face, pad tops 0.1 under the block top."""
    box = _temp_obj("ctx_block", lambda a: _box(a, -3.0, 3.0, 0.0, 3.0, 0.6, 7.6, STONE, 1.12))
    box.matrix_world = base
    za = 7.6 - 0.1 - (PAD_Z1 - h["m063_attach_build"][2])
    shown = [box, _copy(h, "ctx1", base @ Matrix.Translation((-1.5, 0.0, za))),
             _copy(h, "ctx2", base @ Matrix.Translation((1.4, 0.0, za - 0.3))),
             _copy(h, "ctx3", base @ Matrix.Translation((3.0, 1.6, za - 0.15)) @ Matrix.Rotation(math.radians(90), 4, "Z"))]
    bpy.context.view_layer.update()
    return shown


def _scale_shot(h, base):
    wall = _temp_obj("scale_wall", lambda a: _box(a, -1.9, 1.9, 0.0, 1.0, 0.0, 7.7, STONE, 1.12))
    wall.matrix_world = base
    shown = [wall, _copy(h, "scale_vine", base @ Matrix.Translation((0.0, 0.0, h["m063_attach_build"][2]))),
             _marker((base.translation + Vector((-1.4, -1.6, 0.0))), "char1"),
             _marker((base.translation + Vector((1.6, -2.2, 0.0))), "char2")]
    bpy.context.view_layer.update()
    return shown


def _wall_plane(h):
    """A thin plane on the wall plane y = 0 (behind it, 0.02 thick) for the wall check render."""
    pl = _temp_obj("wallplane", lambda a: _box(a, -1.6, 1.8, 0.0, 0.02, -0.2, 7.8, STONE_D, 0.8))
    pl.matrix_world = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
    bpy.context.view_layer.update()
    return [pl]


def render_views(objs, close=True):
    h = objs[0]
    base = Matrix.Translation((h.location.x + 30, h.location.y, 0))
    shown = _exploded(objs, base) if len(objs) > 1 else []
    ctx = _context(h, Matrix.Translation((h.location.x + 50, h.location.y, 0)))
    sc = _scale_shot(h, Matrix.Translation((h.location.x + 70, h.location.y, 0)))
    wp = _wall_plane(h)
    temps = shown + ctx + sc + wp
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        for o in objs[1:]:
            extra["part_" + o.name.replace("TwistedVine", "").lower()] = ([o], *PARTS_SHOT)
        if shown:
            extra["exploded"] = (shown, -8, 10)
        extra["context"] = (ctx, -35, 15)
        extra["scale"] = (sc, -30, 6)
        extra["wall"] = ([h] + wp, 90, 0)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = m033._long_lens(kit)
        try:
            sheet = M.views(NUM, [h], names=VIEW_NAMES, extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet, "spin": render_spin(h)}
        if close:
            out.update(render_close_ups(objs))
        return out
    finally:
        for o in temps:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me.users == 0 and me.name.startswith(PFX):
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def render_spin(h, el=SPIN_EL):
    """Eight azimuths at e 10 (long lens, floor hidden) into spinNNN_sheet.png and the contact sheet M063_spin.png."""
    kit = K.NS["KIT"]
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    orig, kit["render_group"] = m033._long_lens(kit)
    old = kit["CELL"]
    kit["CELL"] = (300, 480)
    paths = []
    try:
        for az in SPIN_AZ:
            paths.append(kit["render_group"]([h], f"{d}/spin{az:03d}_sheet.png", az, el))
    finally:
        kit["render_group"] = orig
        kit["CELL"] = old
    sheet = f"{d}/{M.code(NUM)}_spin.png"
    kit["save_px"](kit["vstack"]([kit["hstack"](paths[:4]), kit["hstack"](paths[4:])]), sheet)
    return sheet


def _thumb(h, path):
    kit = K.NS["KIT"]
    old = kit["CELL"]
    kit["CELL"] = (90, 140)
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        return kit["render_group"]([h], path, 0, 6)
    finally:
        kit["render_group"] = orig
        kit["CELL"] = old


def _leaf_centre(cid, k=-1):
    lv = [l for l in INFO.get("leaves", []) if l["cid"] == cid]
    return Vector(lv[k]["c"]) if lv else Vector((0, -1.2, 6.0))


def _close(objs, path, az, el, centre, radius):
    """m033.render_close with the studio floor always hidden (a close-up frame box puts the floor through the subject)."""
    kit = K.NS["KIT"]
    fb = kit["frame_box"]
    c = Vector(centre)
    box = [c + Vector((dx, dy, dz)) * radius for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    kit["frame_box"] = lambda corners, a_, e_: fb(box, a_, e_)
    ground = bpy.data.objects.get("FB_Ground")
    if ground:
        ground.hide_render = True
    cell = kit["CELL"]
    kit["CELL"] = (480, 400)
    try:
        return kit["render_group"](objs, path, az, el)
    finally:
        kit["CELL"] = cell
        kit["frame_box"] = fb
        if ground:
            ground.hide_render = False


def render_close_ups(objs):
    """junction_cu (the stub in its socket under the junction leaves, close-up 1), pivot_cu (C3's stalk on the spur,
    close-up 2), underside_cu (the flat underside and the socket notch, close-up 3), twist_cu (the strand pair at z 2-4),
    socket_cu (the pad socket and the stub with the leaves hidden), stub_cu (the stub's cut end from above), cluster_cu
    (one cluster), leaf_edge (a junction leaf edge-on: thickness and folds), thumb (the front at ~120 px)."""
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    h = objs[0]
    by = {o.name: o for o in objs}
    rc = _close
    hinfo = RECS.get(HERO, [])
    out = {"junction_cu": rc([h], f"{d}/junction_cu.png", -35, 10, _at(h, (0.1, -1.1, 6.2)), 1.0),
           "underside_cu": rc([h], f"{d}/underside_cu.png", 10, -50, _at(h, (0.2, -0.7, 5.8)), 1.05),
           "twist_cu": rc([h], f"{d}/twist_cu.png", 0, 5, _at(h, (0.0, -1.0, 3.0)), 1.0),
           "stub_cu": rc([h], f"{d}/stub_cu.png", -20, 40, _at(h, (0.0, -1.0, 7.15)), 0.45),
           "thumb": _thumb(h, f"{d}/thumb.png")}
    try:
        spur_end = SPUR.get("end", Vector((-0.3, -1.3, 4.1)))
        out["pivot_cu"] = rc([h], f"{d}/pivot_cu.png", -95, 5, _at(h, spur_end), 0.55)
        out["cluster_cu"] = rc([h], f"{d}/cluster_cu.png", -30, 10, _at(h, _leaf_centre("C5") - Z * 0.3), 0.75)
        out["leaf_edge"] = rc([h], f"{d}/leaf_edge.png", 90, 5, _at(h, _leaf_centre("J2") - Z * 0.25), 0.45)
    except Exception as e:             # noqa: BLE001 - the main views matter more than one close-up
        out["close_err"] = str(e)
    # the socket with the foliage hidden: pad, stub and strand tops only
    if PAD_P in by:
        out["socket_cu"] = rc([by[PAD_P]], f"{d}/socket_cu.png", 20, -40,
                              _at(by[PAD_P], (0.2, -0.7, 5.9)), 1.0)
    if CLUS_P in by:
        out["leafpart_cu"] = rc([by[CLUS_P]], f"{d}/leafpart_cu.png", -15, 15, _at(by[CLUS_P], (0.0, -0.1, -0.4)), 0.85)
    del hinfo
    return out


def preview(names=("front_sheet", "side_sheet", "rear_sheet", "top_sheet"), vfx=False):
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
    h, lg = build_hero()
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n in PART_NAMES if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"hero": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                        "boundary_edges", "normals")}, "log": lg, "leaves": leaf_report(),
            "offset": [round(x, 3) for x in h[OFF]], "attach": list(h[ATT])}
