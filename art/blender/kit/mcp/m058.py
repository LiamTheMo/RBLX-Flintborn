"""058 Low Bush (references/058.png): a low, wide, round-topped flowering shrub. A faceted planked trunk (three root
flares) forks at z 1.15-1.5 into two leaders; seven limbs (LEAD, UP-L, UP-R, BACK-L, BACK-R, LOW-L, LOW-R) and one
bare cut spur carry nine leaf clusters (the low limbs fork into a front and a back cluster, so the side view has a
window). Each cluster's body is a few overlapping faceted lumps in leaf tones; about 45 lobed domes (puffs: broad
lobes round a raised apex, 8n tris) are spread over the crown's outer surface, facing radially out, toned light ->
mid -> dark by height. Dark inner lumps fill the windows behind the trunk; two bridge lumps keep the crown round over
the side windows. Six white five-petal flowers with yellow centres on front rosettes; two foot rosettes and two window
sprigs; at the foot pale warm-grey rocks, a flat stone, pebbles and rounded clover ground pads. The LeafClump parts
are round balls of the same lobed domes.

    import importlib, kit_models, m058; importlib.reload(kit_models); importlib.reload(m058); m058.build()

Build frame: studs, front -Y, +X right, ground z 0, trunk axis at (0, 0). Every object ends with its origin at its bbox
bottom centre; o["m058_offset"] is that origin in the build frame. Names (spec 8): GladeBush (hero) and the parts
GladeBushLeafClumpLarge / Medium / Small, GladeBushBranchStem, GladeBushRock, GladeBushGroundLeaves, GladeBushFlower.
Colour is painted by position and role (never by facing). Stages 5-6: none (the sheet shows no effect).
See art/blender/renders/models/M058/M058_spec.md.
"""
import math
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

NUM, TITLE, SHEET = 58, "Low Bush", "M058"
OFF = "m058_offset"
PFX = "_m058_"
HERO = "GladeBush"
P_L, P_M, P_S = "GladeBushLeafClumpLarge", "GladeBushLeafClumpMedium", "GladeBushLeafClumpSmall"
P_STEM, P_ROCK, P_GL, P_FL = "GladeBushBranchStem", "GladeBushRock", "GladeBushGroundLeaves", "GladeBushFlower"
PARTS = (P_L, P_M, P_S, P_STEM, P_ROCK, P_GL, P_FL)

LEAF_L, LEAF_M, LEAF_D, LEAF_U, LIME = ("m058_leaf_light", "m058_leaf_mid", "m058_leaf_dark", "m058_leaf_under",
                                        "m058_leaf_lime")
BARK, BARK_L, BARK_D = "m058_bark", "m058_bark_light", "m058_bark_deep"
ROCK, ROCK_L, ROCK_D, TAN = "m058_rock", "m058_rock_light", "m058_rock_deep", "m058_pebble_tan"
PETAL, POLLEN, POLLEN_D = "m058_petal", "m058_pollen", "m058_pollen_deep"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
BURY = 0.05
Z = Vector((0.0, 0.0, 1.0))

# key -> (hex, roughness, low specular). Stage 4 (M058_spec.md "Stage 4") writes the calibrated values here.
PALETTE = {
    LEAF_L: ("#A8CC0D", 0.8, True),
    LEAF_M: ("#60932B", 0.85, True),
    LEAF_D: ("#407337", 0.9, True),
    LEAF_U: ("#1B3313", 0.95, True),     # fix round 1: the inner (window) body, toward the sheet's near-black; 105 deg
    LIME: ("#93B207", 0.85, True),
    BARK: ("#93561F", 0.9, False),
    BARK_L: ("#AE7329", 0.85, False),
    BARK_D: ("#55300C", 0.95, False),
    ROCK: ("#A19996", 0.85, False),
    ROCK_L: ("#B0A9A4", 0.85, False),
    ROCK_D: ("#847F7D", 0.9, False),
    TAN: ("#907B59", 0.9, False),
    PETAL: ("#CFCCC8", 0.7, False),
    POLLEN: ("#DDAD00", 0.6, False),
    POLLEN_D: ("#C19000", 0.6, False),
}
# calibration targets (spec 5.4: the sheet's rendered regions or swatches, as a lit faceted dome shows them)
TARGETS = {LEAF_L: ((0xC0, 0xE2, 0x0B), "vivid"), LEAF_M: ((0x66, 0x9E, 0x25), "green"),
           LEAF_D: ((0x41, 0x7A, 0x32), "green"), LEAF_U: ((0x2E, 0x56, 0x22), "green"),
           LIME: ((0xBA, 0xD5, 0x09), "vivid"),
           BARK: ((0x8A, 0x50, 0x20), "brown"), BARK_L: ((0xDD, 0x8C, 0x37), "brown"),
           BARK_D: ((0x5A, 0x34, 0x16), "brown"),
           ROCK: ((0xCE, 0xBD, 0xB0), "all"), ROCK_L: ((0xE0, 0xD0, 0xC0), "all"), ROCK_D: ((0xA8, 0x9C, 0x92), "all"),
           TAN: ((0xB7, 0x97, 0x67), "all"), PETAL: ((0xF6, 0xF4, 0xEE), "all"),
           POLLEN: ((0xFA, 0xD3, 0x06), "vivid"), POLLEN_D: ((0xF3, 0xAE, 0x07), "vivid")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    for m in list(bpy.data.materials):            # mixed keys from an earlier build: re-mix from the parents
        key = m.name[3:] if m.name.startswith("FB_m058_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = "m058_" + tail
            if k1 in PALETTE and k2 in PALETTE and pct.isdigit():
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


# ---- small helpers ----------------------------------------------------------------------------------------------------
_faces = m033._faces
_mottle = m033._mottle
_u = m047._u
_basis = m047._basis
_ring = m047._ring
_band = m047._band
_zip = m047._zip
_frames = m047._frames
_parity_in = m047._parity_in
_Solids = m047._Solids


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


def _close(a, vs, fs, key):
    bmesh.ops.recalc_face_normals(a.bm, faces=[f for f in fs if f.is_valid])
    a._finish(vs, key, tint=1.0)


def _leaf_key(s):
    """Leaf tone on a 0..2 scale (0 light, 1 mid, 2 dark), quantised to quarter steps between the three keys."""
    s = max(0.0, min(2.0, s))
    return _mix(LEAF_L, LEAF_M, s) if s <= 1.0 else _mix(LEAF_M, LEAF_D, s - 1.0)


def _rot_to(d):
    """Rotation taking +Z onto d."""
    return Z.rotation_difference(Vector(d).normalized()).to_matrix()


# ---- tubes (limbs, spur, twigs) ---------------------------------------------------------------------------------------
def tube(a, pts, radii, n, u0=None, rot=0.0, key=BARK, cap_key=BARK_L, start_key=None, grooves=()):
    """A closed n-sided tube along a polyline (parallel-transported frames, each ring on the bisector of its kink, so
    every waypoint is a hard mitred kink); flat end caps: the end is a cut face (cap_key), the start is buried in its
    parent (start_key, default the bark). grooves = ring vert indices pulled in 25 %. Returns (verts, rings, strips,
    caps), strips[k] = the side faces between ring verts k and k + 1."""
    bm = a.bm
    pts = [Vector(p) for p in pts]
    fr = _frames(pts, u0 if u0 is not None else _basis(pts[1] - pts[0])[0])
    rings = []
    for p, r, (t, u, v) in zip(pts, radii, fr):
        q = _ring(p, u, v, r, n, rot)
        for k in grooves:
            q[k] = p + (q[k] - p) * 0.75
        rings.append([bm.verts.new(x) for x in q])
    strips = [[] for _ in range(n)]
    side = []
    for i in range(len(rings) - 1):
        fs = _band(bm, rings[i], rings[i + 1])
        side += fs
        for k, f in enumerate(fs):
            strips[k].append(f)
    caps = [bm.faces.new(list(reversed(rings[0]))), bm.faces.new(rings[-1])]
    vs = [v for r in rings for v in r]
    _close(a, vs, side + caps, key)
    _paint(a, caps[1:], cap_key)
    _paint(a, caps[:1], start_key or key)
    return vs, rings, strips, caps


def _strip_paint(a, strips, light=(), deep=(), lt=0.5, dt=0.5):
    for k in light:
        _paint(a, strips[k % len(strips)], _mix(BARK, BARK_L, lt))
    for k in deep:
        _paint(a, strips[k % len(strips)], _mix(BARK, BARK_D, dt))


# ---- branch stem (spec 2.2, 2.3) --------------------------------------------------------------------------------------
# trunk rings: z, half-width in x, half-width in y (8 sides, verts at 0, 45 .. 315 deg; v2 = back, v6 = front)
TRUNK = ((0.0, 0.36, 0.35), (0.4, 0.30, 0.29), (0.8, 0.28, 0.275), (1.15, 0.34, 0.28))
TRUNK_GROOVES = (1, 5)
CROTCH = (0.02, 0.0, 1.30)
# leaders continue the trunk shell from its fork ring: centres and radii after the fork ring
LEADERS = {
    "LEAD": dict(half="R", pts=((0.24, 0.02, 1.52), (0.19, 0.18, 2.08), (0.2, 0.35, 2.58)), radii=(0.18, 0.15, 0.13)),
    "UP-L": dict(half="L", pts=((-0.3, -0.12, 1.5), (-0.6, -0.52, 1.86), (-0.95, -1.02, 2.22)), radii=(0.17, 0.14, 0.11)),
}
# buried limbs: start inside the parent (>= 0.12), waypoints, radii, sides
LIMBS = {
    "UP-R": dict(pts=((0.08, -0.02, 1.2), (0.85, -0.36, 1.7), (1.4, -0.72, 2.15)), radii=(0.15, 0.125, 0.10), n=5),
    "BACK-L": dict(pts=((-0.1, 0.04, 1.26), (-0.5, 0.88, 1.95), (-0.9, 1.48, 2.3)), radii=(0.14, 0.11, 0.10), n=5),
    "BACK-R": dict(pts=((0.12, 0.1, 1.38), (0.6, 0.92, 1.95), (1.0, 1.52, 2.25)), radii=(0.14, 0.11, 0.10), n=5),
    # fix round 1: the low limbs end at a fork under the gap between their front and back low clusters (two twigs
    # each), so the side view shows the limb and the trunk through a window
    "LOW-L": dict(pts=((-0.04, 0.0, 0.5), (-1.0, -0.15, 0.9), (-1.8, 0.05, 1.22)), radii=(0.13, 0.11, 0.095), n=5),
    "LOW-R": dict(pts=((0.04, 0.05, 0.55), (1.1, 0.15, 0.95), (1.9, 0.2, 1.25)), radii=(0.13, 0.11, 0.095), n=5),
    "SPUR": dict(pts=((0.22, 0.06, 1.7), (0.12, -0.5, 2.05)), radii=(0.075, 0.065), n=4),
}
FLARES = (200.0, 320.0, 80.0)
LIMB_INFO = {}           # name -> centreline polyline (build frame), for the visibility report
TIPS = {}                # limb name -> (tip point, unit direction)


def _trunk_ring(z, rx, ry, k):
    a_ = math.radians(45.0 * k)
    g = 0.86 if k in TRUNK_GROOVES else 1.0
    return Vector((math.cos(a_) * rx * g, math.sin(a_) * ry * g, z))


def trunk_shell(a):
    """Trunk + both leaders as ONE closed ring-stack shell (decision 5): the 8-sided planked trunk forks at its top ring
    into two 6-vert rings (each half of the trunk ring plus a shared crotch vertex), which run on as LEAD (right) and
    UP-L (left) to flat cut tips. Returns (verts, faces)."""
    bm = a.bm
    rings = [[bm.verts.new(_trunk_ring(z, rx, ry, k)) for k in range(8)] for z, rx, ry in TRUNK]
    fs = [bm.faces.new(list(reversed(rings[0])))]
    trunk_strips = [[] for _ in range(8)]
    for i in range(len(rings) - 1):
        for k, f in enumerate(_band(bm, rings[i], rings[i + 1])):
            fs.append(f)
            trunk_strips[k].append(f)
    top = rings[-1]
    mid = bm.verts.new(Vector(CROTCH))
    vs = [v for r in rings for v in r] + [mid]
    halves = {"R": [top[6], top[7], top[0], top[1], top[2], mid], "L": [top[2], top[3], top[4], top[5], top[6], mid]}
    start_ang = {"R": 270.0, "L": 90.0}
    tips_caps = []
    lead_strips = {}
    for name, L in LEADERS.items():
        r0 = halves[L["half"]]
        c0 = sum((v.co for v in r0), Vector()) / 6
        cs = [c0] + [Vector(p) for p in L["pts"]]
        prev = r0
        strips = [[] for _ in range(6)]
        for j, (c, r) in enumerate(zip(cs[1:], L["radii"])):
            j1 = j + 1
            if j1 < len(cs) - 1:
                t = ((cs[j1] - cs[j1 - 1]).normalized() + (cs[j1 + 1] - cs[j1]).normalized()).normalized()
            else:
                t = (cs[j1] - cs[j1 - 1]).normalized()
            R = _rot_to(t)
            ring = []
            for k in range(6):
                ang = math.radians(start_ang[L["half"]] + 60.0 * k)
                ring.append(bm.verts.new(c + R @ Vector((math.cos(ang) * r, math.sin(ang) * r, 0.0))))
            for k, f in enumerate(_band(bm, prev, ring)):
                fs.append(f)
                strips[k].append(f)
            vs += ring
            prev = ring
        cap = bm.faces.new(prev)
        fs.append(cap)
        tips_caps.append(cap)
        lead_strips[name] = strips
        LIMB_INFO[name] = [c.copy() for c in cs]
        TIPS[name] = (cs[-1].copy(), (cs[-1] - cs[-2]).normalized())
    _close(a, vs, fs, BARK)
    # colour by role and position (spec 5.5): lit plank crests by strip index, grooves deep, a deep foot band, the
    # crotch ring deep, pale cut faces
    for k in (2, 6):
        _paint(a, trunk_strips[k], _mix(BARK, BARK_L, 0.5))
    for k in (0, 4):
        _paint(a, trunk_strips[k], _mix(BARK, BARK_L, 0.25))
    for k in (1, 5):
        _paint(a, trunk_strips[k], _mix(BARK, BARK_D, 0.5))
    for k in range(8):
        _paint(a, [trunk_strips[k][0]], _mix(BARK, BARK_D, 0.75 if k in (1, 5) else 0.25))
    for name, strips in lead_strips.items():
        _paint(a, strips[1] + strips[4], _mix(BARK, BARK_L, 0.25))
        _paint(a, [s[0] for s in strips], _mix(BARK, BARK_D, 0.25))     # the crotch ring
    _paint(a, fs[:1], BARK_D)
    _paint(a, tips_caps, BARK_L)
    _mottle(a, fs, 0.03, 0.8, 58101)
    return vs, fs


def flare(a, az):
    """A short root flare: a closed 6-vert wedge from inside the trunk foot (z 0.35) out to r 0.52 at z 0, flat
    underneath (spec 2.2)."""
    bm = a.bm
    d = _u(az)
    s = _u(az + 90.0)
    pts = [d * 0.05 + s * 0.13, d * 0.05 - s * 0.13, d * 0.52 - s * 0.07, d * 0.52 + s * 0.07,
           d * 0.06 + Z * 0.38, d * 0.46 + Z * 0.07]
    v = [bm.verts.new(p) for p in pts]
    fs = [bm.faces.new((v[0], v[3], v[2], v[1])),           # bottom
          bm.faces.new((v[0], v[1], v[4])),                  # inner end
          bm.faces.new((v[1], v[2], v[5], v[4])),            # side
          bm.faces.new((v[3], v[0], v[4], v[5])),            # side
          bm.faces.new((v[2], v[3], v[5]))]                  # outer end
    _close(a, v, fs, _mix(BARK, BARK_D, 0.5))
    return v


def limb(a, name):
    L = LIMBS[name]
    pts = [Vector(p) for p in L["pts"]]
    vs, rings, strips, caps = tube(a, pts, L["radii"], L["n"], rot=0.3, key=BARK, cap_key=BARK_L)
    _strip_paint(a, strips, light=(1,), deep=(3,), lt=0.25, dt=0.25)
    if len(rings) > 2:
        _paint(a, [s[0] for s in strips], BARK)
    _paint(a, caps[1:], BARK_L)
    _mottle(a, _faces(vs), 0.03, 0.8, 58110 + len(name))
    LIMB_INFO[name] = [p.copy() for p in pts]
    TIPS[name] = (pts[-1].copy(), (pts[-1] - pts[-2]).normalized())
    return vs


def branch_stem(a):
    """The whole branch stem: trunk + leaders shell, three root flares, five buried limbs and the bare spur."""
    LIMB_INFO.clear()
    TIPS.clear()
    out = {}
    out["trunk"] = trunk_shell(a)[0]
    for i, az in enumerate(FLARES):
        out[f"flare{i}"] = flare(a, az)
    for name in LIMBS:
        out[name] = limb(a, name)
    return out


# ---- rosettes (spec 2.4, 4.1) -----------------------------------------------------------------------------------------
# size class -> mound (R, lobes, height), upper tier (R, lobes, height, seat as a fraction of the lower height) or
# None; part heights (hp, hpu)
# part_up: the parts' extra tiers (R, lobes, height, seat as a fraction of the tier below's height), each a mound
# seated in the one below and turned half a lobe, so a part is the sheet's stacked clump of drooping lobes
ROS = {"L": dict(R=0.7, n=5, h=0.6, lv=4, up=None, Rp=0.75, np=6, hp=0.5,
                 part_up=((0.55, 5, 0.42, 0.45), (0.33, 4, 0.3, 0.5))),
       "M": dict(R=0.58, n=5, h=0.5, lv=4, up=None, Rp=0.6, np=6, hp=0.42, part_up=((0.42, 5, 0.36, 0.45),)),
       "S": dict(R=0.48, n=4, h=0.41, lv=4, up=None, Rp=0.45, np=5, hp=0.5, part_up=None)}
SHOULDER = (0.92, 0.30)      # lobe shoulders: radius x R, angle off the lobe axis x lobe step
NOTCH = 0.66                 # notch radius x R (the creases between lobes)
LOBE_Z = (0.14, 0.30, 0.34)  # mound: tip / shoulder / notch heights x h (the lobes droop over a skirt)
RIM = 0.64                   # mound underside rim radius x R
FLAT_Z = (0.06, 0.08, 0.0)   # flat star (upper tier, pads): tip / shoulder / notch heights x h
LV3 = (0.97, 0.22)           # 3-vert lobes: the two end corners (radius x R, angle off the lobe axis x lobe step)


def rosette(a, B, axis, R, h, n, spin, seed, key_top, key_base, mound=True, key_low=None, lv=4, dome=False):
    """One closed faceted lobed rosette (spec 2.4): a raised centre (apex) over a star outline of n broad blunt
    pentagonal lobes - per lobe two shoulders at 0.92 R and a tip at R (tip corner about 130 deg), deep notches at
    0.58 R - so each lobe is a ridge (apex -> tip) with a broad facet each side and a crease (apex -> notch) to the
    next lobe. mound: the outline sits at a third of the height and the lobes droop over a skirt down to a bottom
    point (a chunky clump, 8n tris; the skirt sinks into its cluster); otherwise the outline is the flat underside (a
    low star, 8n - 2 tris). dome (the parts): a ring of ridge / crease points at half the radius rounds the top
    into a lobed dome (12n tris). Base centre B, axis along `axis`. Returns (verts, top faces, low faces, base
    faces)."""
    bm = a.bm
    rng = random.Random(seed)
    step = 2 * math.pi / n
    tz, sz, nz = LOBE_Z if mound else FLAT_Z
    loc = []
    lobe_ang = []
    for k in range(n):
        ph = spin + k * step + rng.uniform(-0.06, 0.06) * step
        lobe_ang.append(ph)
        r = R * rng.uniform(0.94, 1.05)
        hz = rng.uniform(0.9, 1.1)
        if lv == 4:     # shoulder, tip, shoulder, notch: a ridged lobe with a blunt tip
            pts = ((SHOULDER[0] * r, -SHOULDER[1] * step, sz * h * hz), (r, 0.0, tz * h * hz),
                   (SHOULDER[0] * r, SHOULDER[1] * step, sz * h * hz), (NOTCH * R, 0.5 * step, nz * h))
        else:           # two corners of a broad squared lobe end, notch
            pts = ((LV3[0] * r, -LV3[1] * step, tz * h * hz), (LV3[0] * r, LV3[1] * step, tz * h * hz),
                   (NOTCH * R, 0.5 * step, nz * h))
        for rr, dang, z in pts:
            loc.append(Vector((math.cos(ph + dang) * rr, math.sin(ph + dang) * rr, z)))
    Rm = _rot_to(axis)
    B = Vector(B)
    ax_off = Vector((rng.uniform(-0.06, 0.06) * R, rng.uniform(-0.06, 0.06) * R, h))
    out = [bm.verts.new(B + Rm @ p) for p in loc]
    apex = bm.verts.new(B + Rm @ ax_off)
    N = len(out)
    vs = out + [apex]
    if dome:
        ring_l = []
        for ph in lobe_ang:
            ring_l += [Vector((math.cos(ph) * 0.52 * R, math.sin(ph) * 0.52 * R, 0.8 * h)),
                       Vector((math.cos(ph + step / 2) * 0.4 * R, math.sin(ph + step / 2) * 0.4 * R, 0.66 * h))]
        ring = [bm.verts.new(B + Rm @ p) for p in ring_l]
        M_ = len(ring)
        top = [bm.faces.new((ring[k], ring[(k + 1) % M_], apex)) for k in range(M_)]
        loc_of = {v: p for v, p in zip(ring, ring_l)}
        loc_of.update({v: p for v, p in zip(out, loc)})
        top += _zip_local(bm, ring, out, loc_of)
        vs += ring
    else:
        top = [bm.faces.new((out[k], out[(k + 1) % N], apex)) for k in range(N)]
    low = []
    if mound:
        # the lobes droop over a skirt that closes at a bottom point on the axis (sunk in the cluster, never seen)
        bot = bm.verts.new(B + Rm @ Vector((0.0, 0.0, 0.0)))
        low = [bm.faces.new((out[(k + 1) % N], out[k], bot)) for k in range(N)]
        base = []
        vs.append(bot)
    else:
        base = [bm.faces.new(list(reversed(out)))]
    _close(a, vs, top + low + base, key_top)
    _paint(a, low, key_low or key_top)
    _paint(a, base, key_base)
    return vs, top, low, base


# fix round 1: the hero's rosettes are lobed DOMES (puffs), not thin lobed discs, so a rosette seen side-on reads as
# a chunky lump (the sheet's clumps), never as an edge-on flap. Same 8n tris as the old disc.
PUFF = {"L": dict(R=0.66, H=0.6, n=6), "M": dict(R=0.56, H=0.52, n=5), "S": dict(R=0.47, H=0.44, n=5)}
PUFF_Z = dict(tip=(1.0, 0.24), notch=(0.82, 0.36), crown=(0.56, 0.86), crease=(0.4, 0.62))   # (radius x R, z x H)


def puff(a, B, axis, R, H, n, spin, seed, key_top, key_low):
    """One closed lobed dome (fix round 1): n broad lobes round a raised apex. Outline ring: a lobe tip (R, low) and a
    shallow notch (0.84 R, a little higher) per lobe; upper ring: a lobe crown over each tip and a crease over each
    notch; the apex on the axis; a shallow skirt under the outline closes at a bottom point on the axis (sunk in the
    core). Each lobe is a rounded faceted bump with a crease to the next. 8n tris. Returns (verts, top, low)."""
    bm = a.bm
    rng = random.Random(seed)
    step = 2 * math.pi / n
    Rm = _rot_to(axis)
    B = Vector(B)
    outline, upper = [], []
    for k in range(n):
        ph = spin + k * step + rng.uniform(-0.06, 0.06) * step
        rr = rng.uniform(0.94, 1.06)
        hz = rng.uniform(0.9, 1.1)
        for (fr, fz), ang, lst, j in ((PUFF_Z["tip"], ph, outline, rr), (PUFF_Z["notch"], ph + step / 2, outline, 1.0),
                                       (PUFF_Z["crown"], ph, upper, rr), (PUFF_Z["crease"], ph + step / 2, upper, 1.0)):
            r_ = fr * R * j
            z_ = fz * H * (hz if lst is upper or fr == 1.0 else 1.0)
            lst.append(bm.verts.new(B + Rm @ Vector((math.cos(ang) * r_, math.sin(ang) * r_, z_))))
    apex = bm.verts.new(B + Rm @ Vector((rng.uniform(-0.05, 0.05) * R, rng.uniform(-0.05, 0.05) * R, H)))
    bot = bm.verts.new(B.copy())
    m = len(outline)
    top = [bm.faces.new((upper[k], upper[(k + 1) % m], apex)) for k in range(m)]
    for k in range(m):
        k1 = (k + 1) % m
        top += [bm.faces.new((outline[k], outline[k1], upper[k1])), bm.faces.new((outline[k], upper[k1], upper[k]))]
    low = [bm.faces.new((outline[(k + 1) % m], outline[k], bot)) for k in range(m)]
    vs = outline + upper + [apex, bot]
    _close(a, vs, top + low, key_top)
    _paint(a, low, key_low)
    return vs, top, low


def rosette_unit(a, B, axis, cls, spin, seed, s, scale=1.0, part=False):
    """A rosette of class L / M / S at base centre B on `axis`: the lobed mound and, for L, a smaller flat star
    seated on its top (rotated half a lobe; its own closed shell), so the two tiers shingle. Tone s (0 light .. 2
    dark): the upper tier a quarter step lighter, the drooping lobe skirts a quarter darker, the underside half.
    Returns (verts, shells [verts], groups)."""
    C = ROS[cls]
    h = (C["hp"] if part else C["h"]) * scale
    ax = Vector(axis).normalized()
    if not part:
        Pf = PUFF[cls]
        vs, top, low = puff(a, B, ax, Pf["R"] * scale, Pf["H"] * scale, Pf["n"], spin, seed, _leaf_key(s),
                            _leaf_key(s + 0.5))
        return vs, [vs], {"top": top, "low": low, "base": [], "up": []}
    up = C["part_up"] if part else C["up"]
    R, n, lv = (C["Rp"], C["np"], 4) if part else (C["R"], C["n"], C["lv"])
    v1, t1, l1, b1 = rosette(a, B, ax, R * scale, h, n, spin, seed, _leaf_key(s), _leaf_key(s + 0.75),
                             key_low=_leaf_key(s + 0.5), lv=lv, dome=part)
    shells = [v1]
    groups = {"top": t1, "low": l1, "base": b1, "up": []}
    if up and not isinstance(up[0], tuple):
        up = (up,)
    base, hb, sp = Vector(B), h, spin
    for i, (Ru, nu, hu, seat) in enumerate(up or ()):
        hu = hu * scale
        base = base + ax * (seat * hb)
        sp = sp + math.pi / nu
        v2, t2, l2, b2 = rosette(a, base, ax, Ru * scale, hu, nu, sp, seed + 7 * (i + 1), _leaf_key(s - 0.25),
                                 _leaf_key(s + 0.25), mound=part, lv=4, dome=part)
        shells.append(v2)
        groups["up"] += t2 + l2
        groups["base"] = groups["base"] + b2
        hb = hu
    return [v for sh in shells for v in sh], shells, groups


def _repaint_unit(a, groups, s):
    _paint(a, groups["top"], _leaf_key(s))
    _paint(a, groups["low"], _leaf_key(s + 0.5))
    _paint(a, groups["up"], _leaf_key(s - 0.25))
    _paint(a, groups["base"], _leaf_key(s + 0.75))


def _zip_local(bm, A, B, loc_of):
    """m047._zip in the rosette's local frame (angles about local +Z)."""
    def ang(v):
        p = loc_of[v]
        return math.atan2(p.y, p.x)
    a0 = min(range(len(A)), key=lambda i: ang(A[i]) % (2 * math.pi))
    b0 = min(range(len(B)), key=lambda i: ang(B[i]) % (2 * math.pi))
    A = A[a0:] + A[:a0]
    B = B[b0:] + B[:b0]
    na, nb = len(A), len(B)
    base = ang(A[0])

    def ua(i):
        return (ang(A[i % na]) - base) % (2 * math.pi) + (2 * math.pi if i >= na else 0.0)

    def ub(j):
        return (ang(B[j % nb]) - base) % (2 * math.pi) + (2 * math.pi if j >= nb else 0.0)
    i = j = 0
    out = []
    while i < na or j < nb:
        if j >= nb or (i < na and ua(i + 1) <= ub(j + 1)):
            out.append(bm.faces.new((A[i % na], A[(i + 1) % na], B[j % nb])))
            i += 1
        else:
            out.append(bm.faces.new((A[i % na], B[(j + 1) % nb], B[j % nb])))
            j += 1
    return out


# ---- leaf clusters (spec 2.4) -----------------------------------------------------------------------------------------
# c: centre (x, y); zb: core bottom; ax / ay / hc: core semi-axes and height; ros: rosette classes (largest first);
# tmax: polar limit (deg) of the rosette spread; inner: polar limit on the trunk side (window); tone: shift (<0 lighter)
CLUSTERS = {
    "CT": dict(feed="LEAD", c=(0.1, -0.15), zb=2.45, ax=1.6, ay=1.35, hc=1.74, tone=-0.3, seed=58201),
    "CFL": dict(feed="UP-L", c=(-1.35, -1.22), zb=1.3, ax=1.15, ay=0.88, hc=2.1, tone=0.0, seed=58202),
    "CR": dict(feed="UP-R", c=(1.55, -1.15), zb=1.3, ax=1.15, ay=0.88, hc=2.1, tone=0.0, seed=58203),
    "CBL": dict(feed="BACK-L", c=(-1.3, 1.38), zb=1.35, ax=1.1, ay=0.88, hc=1.95, tone=0.05, seed=58204),
    "CBR": dict(feed="BACK-R", c=(1.3, 1.42), zb=1.35, ax=1.1, ay=0.88, hc=1.9, tone=0.05, seed=58205),
    # fix round 1: each low cluster is split into a front and a back cluster on its limb's fork, so the side view has
    # a window (the sheet's side: the trunk and limbs under the crown, T 8 %)
    "CLLF": dict(feed="LOW-L", c=(-2.3, -0.85), zb=0.85, ax=0.62, ay=0.6, hc=1.75, tone=0.25, seed=58206),
    "CLLB": dict(feed="LOW-L", c=(-2.2, 1.1), zb=0.9, ax=0.62, ay=0.6, hc=1.7, tone=0.25, seed=58208),
    "CLRF": dict(feed="LOW-R", c=(2.35, -0.75), zb=0.85, ax=0.62, ay=0.6, hc=1.75, tone=0.25, seed=58207),
    "CLRB": dict(feed="LOW-R", c=(2.25, 1.2), zb=0.9, ax=0.62, ay=0.6, hc=1.7, tone=0.25, seed=58209),
}
SIDE_GAP = (0.15, 0.5, 2.0, 0.7)   # side-view window: no rosette seat with |y - y0| < half, z < zmax, |x| > xmin
FOOT = {"FC": dict(c=(-0.55, -2.05), cls="M", scale=1.1, s=0.3, seed=58251),
        "FB": dict(c=(0.5, 2.2), cls="S", scale=1.05, s=0.6, seed=58252),
}
# the window sprig (spec 2.5 F5): a small rosette on a twig off LOW-R's kink, inside the window above RK1
# window sprigs (spec 1.3 / 2.5): small rosettes on 4-sided twigs off the low limbs' kinks, hanging in the lower window
# (F5 sits on SR; the front view's dark low rosettes left of the trunk; the rear window's leaves)
SPRIGS = {
    "SR": dict(base=(1.05, 0.12, 0.92), end=(1.42, -0.62, 1.04), axis=(0.1, -0.75, 0.65), cls="S", scale=0.9, s=0.6,
               seed=58260),
    "SL": dict(base=(-0.95, -0.14, 0.88), end=(-1.25, -0.8, 0.98), axis=(-0.15, -0.8, 0.55), cls="M", scale=0.85,
               s=1.15, seed=58261),
    # SB (the rear window's sprig) is dropped in fix round 1: the dark inner lumps fill the rear window
}
CORE_N = 5
CORE_RINGS = ((0.0, 0.8), (0.42, 1.0))
SEAT_MAX = 0.25         # at most this fraction of a rosette's verts inside its core
CLUSTER_INFO = {}
DROPPED = []
ROS_LOG = []            # per rosette: (cluster, class, centre z, inside frac, tone)


# fix round 1 (main-session option from 057): each cluster's body is a cluster of overlapping faceted LUMPS in leaf
# tones (by height, a step darker than the rosettes: the inner body), not one smooth dark core, so whatever shows
# between the rosettes reads as foliage, never as bare dark planes. Each lump is a flat-bottomed 5-sided dome
# (base ring, a half-turned shoulder ring, an apex; 18 tris); the flat bottoms are the dark undersides (close-up 2).
LUMP_N = 5
LUMPS = {"CT": 2, "CFL": 2, "CR": 2, "CBL": 2, "CBR": 2, "CLLF": 1, "CLLB": 1, "CLRF": 1, "CLRB": 1}   # extra lumps


def _lump(a, c, rx, ry, zb, h, ph, rng):
    bm = a.bm
    rings = []
    for li, (fz, rho) in enumerate(((0.0, 0.84), (0.55, 1.0))):
        ring = []
        for k in range(LUMP_N):
            th = ph + 2 * math.pi * (k + 0.5 * li) / LUMP_N + rng.uniform(-0.1, 0.1)
            j = rng.uniform(0.93, 1.06)
            ring.append(bm.verts.new(Vector((c[0] + math.cos(th) * rx * rho * j, c[1] + math.sin(th) * ry * rho * j,
                                             zb + fz * h * (rng.uniform(0.92, 1.08) if li else 1.0)))))
        rings.append(ring)
    top = bm.verts.new(Vector((c[0] + rng.uniform(-0.08, 0.08) * rx, c[1] + rng.uniform(-0.08, 0.08) * ry, zb + h)))
    base = bm.faces.new(list(reversed(rings[0])))
    side = []
    r0, r1 = rings
    for k in range(LUMP_N):
        k1 = (k + 1) % LUMP_N
        side += [bm.faces.new((r0[k], r0[k1], r1[k])), bm.faces.new((r0[k1], r1[k1], r1[k]))]
    cap = [bm.faces.new((r1[k], r1[(k + 1) % LUMP_N], top)) for k in range(LUMP_N)]
    vs = r0 + r1 + [top]
    return vs, base, side, cap


def core(a, P, paint=True):
    """A cluster body (fix round 1): a main flat-bottomed lump on the old core's footprint plus LUMPS[name] smaller
    lumps on its outer side (away from the crown axis), overlapping. Toned by height in the crown, a step darker
    than the rosettes (the inner body); the flat bottoms dark (the underside role, close-up 2)."""
    cx, cy = P["c"]
    rng = random.Random(P["seed"])
    name = next(n for n, Q in CLUSTERS.items() if Q is P)
    out_dir = Vector((cx - CROWN_AX[0], cy - CROWN_AX[1], 0.0))
    oa = math.atan2(out_dir.y, out_dir.x) if out_dir.length > 0.2 else rng.uniform(0, 6.28)
    specs = [((cx, cy), P["ax"], P["ay"], P["zb"], P["hc"] * 0.86)]
    m = LUMPS.get(name, 0)
    for i in range(m):
        ang = oa + (i - (m - 1) / 2) * math.radians(80 if name == "CT" else 70) + rng.uniform(-0.2, 0.2)
        d = 0.5
        specs.append(((cx + math.cos(ang) * P["ax"] * d, cy + math.sin(ang) * P["ay"] * d), P["ax"] * 0.62,
                      P["ay"] * 0.62, P["zb"] + 0.12 * P["hc"], P["hc"] * 0.55))
    vs_all = []
    for c, rx, ry, zb, h in specs:
        vs, base, side, cap = _lump(a, c, rx, ry, zb, h, rng.uniform(0, 6.28), rng)
        _close(a, vs, [base] + side + cap, LEAF_D)
        if paint:
            _paint_body(a, base, side + cap, P["tone"], P["seed"] + len(vs_all))
        vs_all += vs
    return vs_all


def _paint_body(a, base, faces, tone, seed):
    """A body lump's colour by height in the crown (a step darker than the rosettes there: the inner body) and broad
    position noise; the flat bottom is the dark underside role."""
    for f in faces:
        z = f.calc_center_median().z
        u = max(0.0, min(1.0, (z - 0.6) / 3.6))
        st = 1.85 - 0.95 * u + 0.4 * tone + 0.35 * noise.noise(f.calc_center_median() * 0.9)
        f.material_index = a._mi(_leaf_key(st))
    _paint(a, [base], LEAF_D)       # the flat dark underside (never leaf_under: it is foliage body)
    _mottle(a, faces, 0.03, 0.7, seed)


# fix round 1: body lumps bridging the front and back clusters over each side window, so the crown stays round in
# the top view (the split low clusters left a notch) and the side window has a leafy ceiling at about z 2 (the sheet's
# side: the window up to h .45). (centre x, y), radius x / y, base z, height, seed
BRIDGES = (((1.95, 0.15), 0.62, 0.55, 2.15, 0.75, 58281), ((-1.95, 0.12), 0.62, 0.55, 2.15, 0.75, 58282))


def bridge_lumps(a):
    out = []
    for c, rx, ry, zb, h, seed in BRIDGES:
        rng = random.Random(seed)
        vs, base, side, cap = _lump(a, c, rx, ry, zb, h, rng.uniform(0, 6.28), rng)
        _close(a, vs, [base] + side + cap, LEAF_D)
        _paint_body(a, base, side + cap, 0.0, seed)
        out += vs
    return out


def _ell(P, th, ph):
    """Point and normal on the cluster core's ellipsoid (polar th from the top, azimuth ph); centre at 0.35 hc."""
    cx, cy = P["c"]
    ax, ay, hc = P["ax"], P["ay"], P["hc"]
    zc = P["zb"] + 0.35 * hc
    cz = 0.65 * hc if th <= math.pi / 2 else 0.35 * hc
    st, ct = math.sin(th), math.cos(th)
    p = Vector((cx + ax * st * math.cos(ph), cy + ay * st * math.sin(ph), zc + cz * ct))
    nrm = Vector((st * math.cos(ph) / ax, st * math.sin(ph) / ay, ct / cz)).normalized()
    return p, nrm, Vector((cx, cy, zc))


def _inside_frac(sol, vs):
    return sum(1 for v in vs if sol.point(v.co)[0] > 0.0) / len(vs)


def _remove(a, vs):
    for v in vs:
        if v.is_valid:
            a.bm.verts.remove(v)


def _lift(vs, zmin):
    low = min(v.co.z for v in vs)
    if low < zmin:
        for v in vs:
            v.co.z += zmin - low


def seat_rosette(a, csol, S, nrm, axis, cls, spin, seed, guard=None, scale=1.0, zmin=0.0):
    """Place a rosette unit on its core: base centre on the core surface at S, sunk along the core normal as far as
    allowed (<= SEAT_MAX of its verts inside the core, its centroid outside), so the core stays hidden. A rosette that
    would go under the ground (zmin) is lifted. csol holds every core of the crown, so a rosette is never buried in a
    neighbouring cluster's core either. Returns (verts, shells, groups, inside fraction, cut depth, ok)."""
    for push in (-0.16, -0.12, -0.08, -0.05, -0.02, 0.0, 0.03, 0.07, 0.12, 0.18):
        vs, shells, groups = rosette_unit(a, S + nrm * push, axis, cls, spin, seed, 1.0, scale)
        _lift(vs, zmin)
        frac = _inside_frac(csol, vs)
        cen = sum((v.co for v in vs), Vector()) / len(vs)
        if frac <= SEAT_MAX and csol.point(cen)[0] == 0.0:
            return vs, shells, groups, frac, (guard.depth(vs) if guard is not None else 0.0), True
        _remove(a, vs)
    vs, shells, groups = rosette_unit(a, S + nrm * 0.06, axis, cls, spin, seed, 1.0, scale)
    _lift(vs, zmin)
    return vs, shells, groups, _inside_frac(csol, vs), (guard.depth(vs) if guard is not None else 0.0), False


def _tone_of(P, z, rank, nros):
    """Rosette base tone (0 light .. 2 dark): by height in the crown, by rank within its cluster (top 35 % lighter),
    the cluster's shift and a little position noise (never facing)."""
    u = max(0.0, min(1.0, (z - 0.4) / (4.1 - 0.4)))
    s = 1.32 - 1.1 * u                  # fix round 1: a quarter step darker (f34 dark share 17 against 32)
    if rank < max(1, round(0.35 * nros)):
        s -= 0.12
    amp = 1.35 + 0.5 * (1.0 - u)
    s += 0.4 * P["tone"] + amp * noise.noise(Vector((z * 1.7 + rank * 0.77, P["seed"] % 31 * 0.37, rank * 1.3)))
    return s


def _core_tree(core_vs):
    idx = {v: i for i, v in enumerate(core_vs)}
    return BVHTree.FromPolygons([v.co for v in core_vs], [[idx[v] for v in f.verts] for f in _faces(core_vs)])


def _axis_up(nrm, rng):
    """The core normal tilted 15-25 deg toward up (never past vertical)."""
    ang = nrm.angle(Z)
    if ang < 1e-4:
        return Z.copy()
    tilt = min(ang, math.radians(rng.uniform(15, 25)))
    axis = nrm.cross(Z).normalized()
    return (Matrix.Rotation(tilt, 3, axis) @ nrm).normalized()


CROWN_C = Vector((0.1, 0.15, 1.7))    # rays are cast at the crown's cores from outside toward this point
CROWN_RAYS = 900
CROWN_POLAR = 128.0                  # deg from the top: down to the low clusters' lower flanks
SPACING = 0.70                       # rosette centres at least this far apart over the crown's outer surface
N_ROS = 48
PLAN = []                            # (cluster, S, normal, class, spin, seed)


def _ell_normal(P, p):
    cx, cy = P["c"]
    zc = P["zb"] + 0.35 * P["hc"]
    cz = 0.65 * P["hc"] if p.z >= zc else 0.35 * P["hc"]
    return Vector(((p.x - cx) / P["ax"] ** 2, (p.y - cy) / P["ay"] ** 2, (p.z - zc) / cz ** 2)).normalized()


def plan_rosettes():
    """Where the crown's rosettes go (spec 2.4): rays from outside onto the seven cores pick the crown's OUTER
    surface (faces turned to the ray only; no undersides), then farthest-point sampling spreads N_ROS rosette seats
    evenly over it, at least SPACING apart, so the dome is shingled all over instead of each core carrying a cap.
    Each seat belongs to the core it is on (its cluster). Classes by height: large on top, medium round the
    shoulders, small low. Pure geometry: no mesh is kept."""
    a = K.fk().Asset(PFX + "plan", "probe", seed=1, tint_var=0.0)
    owner = []
    for name, P in CLUSTERS.items():
        vs = core(a, P)
        owner += [name] * len(_faces(vs))
    bm = a.bm
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    bm.faces.index_update()
    fo = {}
    for f in bm.faces:
        fo[f.index] = None
    # owner per face: faces were made cluster by cluster in order
    for i, f in enumerate(bm.faces):
        fo[f.index] = owner[i]
    tree = BVHTree.FromBMesh(bm)
    cands = []
    n = CROWN_RAYS
    cmax = math.cos(math.radians(CROWN_POLAR))
    for i in range(n):
        zf = 1 - (i + 0.5) / n * (1 - cmax)
        th = math.acos(zf)
        ph = i * math.radians(137.508)
        d = Vector((math.sin(th) * math.cos(ph) * 1.15, math.sin(th) * math.sin(ph), math.cos(th))).normalized()
        hit = tree.ray_cast(CROWN_C + d * 15.0, -d, 30.0)
        if hit[0] is None:
            continue
        p, nrm, fi = Vector(hit[0]), Vector(hit[1]), hit[2]
        if nrm.dot(d) < 0.15 or nrm.z < -0.62:
            continue
        y0, half, zmax, xmin = SIDE_GAP
        if abs(p.y - y0) < half and p.z < zmax and abs(p.x) > xmin:
            continue                 # keep the side-view window open (fix round 1)
        cands.append((p, fo[fi]))
    a.bm.free()
    # farthest-point sampling from the top
    picked = [max(range(len(cands)), key=lambda k: cands[k][0].z)]
    dmin = [(c[0] - cands[picked[0]][0]).length for c in cands]
    while len(picked) < N_ROS:
        k = max(range(len(cands)), key=lambda j: dmin[j])
        if dmin[k] < SPACING:
            break
        picked.append(k)
        for j, c in enumerate(cands):
            dmin[j] = min(dmin[j], (c[0] - cands[k][0]).length)
    rng = random.Random(58290)
    PLAN.clear()
    zs = sorted(cands[k][0].z for k in picked)
    z_hi, z_lo = zs[int(0.8 * (len(zs) - 1))], zs[int(0.38 * (len(zs) - 1))]
    for i, k in enumerate(picked):
        p, name = cands[k]
        P = CLUSTERS[name]
        cls = "L" if p.z >= z_hi else "M" if p.z >= z_lo else "S"
        PLAN.append((name, p, _ell_normal(P, p), cls, rng.uniform(0, 2 * math.pi), 58700 + i))
    return len(cands), len(PLAN)


def cluster_core(a, name, twig=True):
    """A cluster's wood and core (spec 2.4, close-up 1): a short twig from its limb's last segment up into the core's
    underside, and the dark flat-bottomed core round the limb tip (the joint is hidden)."""
    P = CLUSTERS[name]
    rng = random.Random(P["seed"])
    cx, cy = P["c"]
    out = []
    tip, d = TIPS.get(P["feed"], (Vector((cx, cy, P["zb"] + 0.3)), Z))
    if twig:
        away = Vector((cx - tip.x, cy - tip.y, 0.0))
        away = away.normalized() if away.length > 1e-3 else _u(rng.uniform(0, 360))
        side = d.cross(Z)
        side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
        base = tip - d * 0.45
        end = Vector((cx, cy, P["zb"] + 0.22)) + side * (0.35 if rng.random() < 0.5 else -0.35) + away * 0.2
        if (end - base).length > 1.5:      # the split low clusters' long twigs: a kinked middle ring (no sliver tris)
            mid = (base + end) / 2 + Z * 0.08
            tv, _, _, tcaps = tube(a, [base, mid, end], [0.065, 0.055, 0.045], 4, rot=0.4, key=BARK, cap_key=BARK_L)
        else:
            tv, _, _, tcaps = tube(a, [base, end], [0.06, 0.045], 4, rot=0.4, key=BARK, cap_key=BARK_L)
        out += tv
    return out, core(a, P)


CROWN_AX = (0.1, 0.1)      # the crown's vertical axis (plan centre)
EL_RANGE = (25.0, 52.0)    # rosette axis elevation from the lowest seats to the crown top (deg)
AXIS_KEEP = 0.2            # share of the core-normal axis kept in the turned axis (variety)


def _turn(axis, S, P):
    """Fix round 1 (STAGES "Foliage reads from every azimuth"): every rosette faces RADIALLY out from the crown's axis,
    never toward the front / rear cameras only, so each of the eight views sees the rosettes on its side of the dome
    face-on. The elevation rises with the seat's height (25 deg low -> 52 deg at the top), so the top rosettes tilt
    toward their own azimuth instead of lying flat (seen edge-on from every side) or standing up as fins."""
    r = Vector((S.x - CROWN_AX[0], S.y - CROWN_AX[1], 0.0))
    if r.length < 0.3:
        r = Vector((axis.x, axis.y, 0.0))
        if r.length < 1e-3:
            r = Vector((0.0, -1.0, 0.0))
    r.normalize()
    u = max(0.0, min(1.0, (S.z - 1.0) / 3.0))
    el = math.radians(EL_RANGE[0] + (EL_RANGE[1] - EL_RANGE[0]) * u)
    tgt = r * math.cos(el) + Z * math.sin(el)
    return (tgt * (1.0 - AXIS_KEEP) + axis * AXIS_KEEP).normalized()


def leaf_clusters(a, names=None, guard=None):
    """The crown (spec 2.4): each named cluster's twig and core, then the planned rosettes on those cores - each
    seated on its own core (<= 25 % of its verts inside, centroid outside), its axis the core normal tilted 15-25 deg
    up, then toned by height in the crown and rank within its cluster. A rosette that would cut the stem is turned,
    shrunk or slid, or dropped."""
    full = names is None
    names = list(names or CLUSTERS)
    if not PLAN:
        plan_rosettes()
    out = []
    sols = {}
    allc = _Solids()
    for name in names:
        tw, cv = cluster_core(a, name)
        out += tw + cv
        BODY_VS.extend(cv)
        nl = 2 * LUMP_N + 1           # each body lump is its own solid (overlapping shells break one-BVH parity)
        for i in range(0, len(cv), nl):
            allc.add_vs(cv[i:i + nl], f"{name}{i // nl}")
        sols[name] = True
    if full:                       # the side-window bridges, built before the rosettes are seated against them
        bv = bridge_lumps(a)
        out += bv
        BODY_VS.extend(bv)
        nl = 2 * LUMP_N + 1
        for i in range(0, len(bv), nl):
            allc.add_vs(bv[i:i + nl], f"BR{i // nl}")
    rng = random.Random(58291)
    placed = {name: [] for name in names}
    for name, S, nrm, cls, spin, seed in PLAN:
        if name not in sols:
            continue
        got = None
        for sp, sc, slide in ((0.0, 1.0, 0.0), (0.4, 0.92, 0.0), (0.9, 0.86, 0.18), (0.2, 0.8, -0.18),
                              (0.6, 0.72, 0.3)):
            S2 = S + (nrm.cross(Z).normalized() * slide if slide and abs(nrm.z) < 0.98 else Vector())
            vs, shells, groups, frac, cut, ok = seat_rosette(a, allc, S2, nrm,
                                                             _turn(_axis_up(nrm, rng), S2, CLUSTERS[name]), cls,
                                                             spin + sp, seed, guard, sc)
            if ok and cut <= 0.03:
                got = (vs, groups, frac)
                break
            _remove(a, vs)
        if got is None:
            DROPPED.append(f"{name}:{cls}@{S.z:.2f}")
            continue
        vs, groups, frac = got
        cen = sum((v.co for v in vs), Vector()) / len(vs)
        placed[name].append((vs, groups, frac, cen, cls))
    for name, lst in placed.items():
        P = CLUSTERS[name]
        order = sorted(range(len(lst)), key=lambda k: -max(v.co.z for v in lst[k][0]))
        for rank, k in enumerate(order):
            vs, groups, frac, cen, cls = lst[k]
            s = _tone_of(P, cen.z, rank, len(lst))
            _repaint_unit(a, groups, s)
            fs_all = [f for fs in groups.values() for f in fs]
            _tint(a, fs_all, 1.0 + rng.uniform(-0.04, 0.04))
            _mottle(a, fs_all, 0.02, 0.6, P["seed"] + k)
            out += vs
            PUFF_VS.extend(vs)
            PUFF_SHELLS.append(vs)
            ROS_LOG.append((name, cls, round(cen.z, 2), round(frac, 2), round(s, 2)))
        CLUSTER_INFO[name] = dict(rosettes=len(lst), classes="".join(sorted(p[4] for p in lst)),
                                  inside=[round(min((p[2] for p in lst), default=0), 2),
                                          round(max((p[2] for p in lst), default=0), 2)])
    return out


# fix round 1: dark inner lumps behind the trunk's flanks (on BACK-L / BACK-R), so the front window shows the trunk and
# limbs against the near-black interior the sheet has, while the trunk itself stays clear from the front, rear and
# sides. (centre x, y), radius, base z, height
INNER = (((-0.62, 0.62), 0.5, 0.88, 1.3, 58271), ((0.62, 0.66), 0.5, 0.92, 1.25, 58272),
         ((-0.78, -0.62), 0.4, 0.62, 1.05, 58273), ((0.82, -0.6), 0.38, 0.7, 0.95, 58274))
PUFF_VS = []           # the crown's rosette verts (flowers sit on these, never on the body lumps)
PUFF_SHELLS = []       # the crown's rosettes, one vert list each
BODY_VS = []           # the crown's body lumps (the cores) and inner lumps


def inner_lumps(a):
    out = []
    for c, r, zb, h, seed in INNER:
        rng = random.Random(seed)
        vs, base, side, cap = _lump(a, c, r, r * 0.85, zb, h, rng.uniform(0, 6.28), rng)
        _close(a, vs, [base] + side + cap, LEAF_U)       # the innermost, shaded body: the dark core role by position
        _mottle(a, side + cap, 0.03, 0.7, seed)
        out += vs
    return out


def leaf_cluster(a, name, guard=None):
    return leaf_clusters(a, [name], guard)


def foot_rosette(a, name, guard=None):
    F = FOOT[name]
    rng = random.Random(F["seed"])
    c = Vector((F["c"][0], F["c"][1], 0.0))
    for k in range(8):
        vs, shells, groups = rosette_unit(a, c, Z, F["cls"], rng.uniform(0, 6.28), F["seed"], F["s"], F["scale"])
        if guard is None or guard.depth(vs) <= 0.0:
            break
        _remove(a, vs)
        c = c + Vector((c.x, c.y, 0.0)).normalized() * 0.1
    _tint(a, _faces(vs), 1.0 + rng.uniform(-0.04, 0.04))
    return vs


def sprig(a, name, guard=None):
    """A window sprig: a 4-sided twig off a low limb's kink and one rosette on its end."""
    S = SPRIGS[name]
    b, e = Vector(S["base"]), Vector(S["end"])
    tv, _, _, _ = tube(a, [b, e], [0.055, 0.045], 4, rot=0.4)
    ax = Vector(S["axis"]).normalized()
    vs, shells, groups = rosette_unit(a, e - ax * 0.02, ax, S["cls"], 0.7, S["seed"], S["s"], S["scale"])
    _tint(a, _faces(vs), 0.97)
    return tv, vs


# ---- base dressing (spec 2.6) -----------------------------------------------------------------------------------------
ROCKS = {   # centre, (W, D, H), yaw, seed, lean
    "RK1": ((1.45, -1.25), (1.5, 1.15, 0.74), 15.0, 58301, 0.12),
    "RK2": ((-1.85, -1.3), (1.4, 1.05, 0.58), -20.0, 58302, 0.08),
    "RK3": ((0.3, -2.0), (1.3, 0.9, 0.25), 8.0, 58303, 0.0),
    "RK4": ((1.95, 1.4), (1.75, 1.25, 0.7), -10.0, 58304, 0.1),
    "RK5": ((-0.8, 1.65), (1.6, 1.15, 0.62), 25.0, 58305, 0.1),
}
PEBBLES = (((-2.95, -1.25), 0.38, 58311, ROCK_D), ((0.95, -2.4), 0.36, 58312, TAN), ((-2.75, 1.5), 0.32, 58313, ROCK_D))
PADS = {   # centre, R, lobes, height, seed (fix round 1: rounded clovers of 3-4 lobes)
    "GL1": ((-2.7, -1.8), 0.58, 4, 0.24, 58321), "GL2": ((-0.15, -2.18), 0.52, 4, 0.24, 58322),
    "GL3": ((2.6, -1.75), 0.52, 4, 0.22, 58323), "GL4": ((2.8, -0.5), 0.42, 3, 0.2, 58324),
    "GL5": ((2.55, 1.85), 0.52, 4, 0.22, 58325), "GL6": ((-0.1, 2.35), 0.46, 3, 0.2, 58326),
    "GL7": ((-2.3, 1.9), 0.46, 3, 0.2, 58327), "GL8": ((-2.85, 0.4), 0.42, 3, 0.2, 58328),
}
ROCK_RINGS = ((0.0, 0.92, 5), (0.3, 1.0, 5), (0.68, 0.8, 4), (1.0, 0.36, 3))
FLAT_RINGS = ((0.0, 0.94, 5), (0.5, 1.0, 5), (1.0, 0.6, 3))
PEB_RINGS = ((0.0, 0.92, 4), (0.5, 1.0, 3), (1.0, 0.4, 1))
BASE_INFO = {}


def _rock(a, c, size, yaw, seed, lean=0.0, rings=ROCK_RINGS, key=ROCK):
    """A pale warm-grey angular block: the hull of jittered ring stacks (flat base at z 0, widest low, a shoulder, a
    rounded faceted crown leaning a little toward the trunk). Tones by height within the rock (light top, deep foot)."""
    rng = random.Random(seed)
    W, D, H = size
    to = -Vector((c[0], c[1], 0.0)).normalized() * lean
    pts = m033._ring_pts(rng, rings, W / 2, D / 2, H, 0.08)
    m = Matrix.Rotation(math.radians(yaw), 3, "Z")
    out = []
    for p in pts:
        q = m @ p
        f = q.z / H
        q += Vector((to.x * W * 0.5 * f, to.y * D * 0.5 * f, 0.0))
        out.append(q + Vector((c[0], c[1], 0.0)))
    vs = m033._hull(a, out, key)
    fs = _faces(vs)
    if key == ROCK:
        for f in fs:
            h = f.calc_center_median().z / H
            if h > 0.7:
                f.material_index = a._mi(_mix(ROCK, ROCK_L, 0.5))
            elif h > 0.5:
                f.material_index = a._mi(_mix(ROCK, ROCK_L, 0.25))
            elif h < 0.25:
                f.material_index = a._mi(_mix(ROCK, ROCK_D, 0.25))
    _mottle(a, fs, 0.04, 0.5, seed)
    _tint(a, fs, 1.0 + rng.uniform(-0.03, 0.03))
    return vs


def rock(a, name):
    c, size, yaw, seed, lean = ROCKS[name]
    return _rock(a, c, size, yaw, seed, lean, FLAT_RINGS if size[2] < 0.4 else ROCK_RINGS)


def pebble(a, spec):
    c, s, seed, key = spec
    return _rock(a, c, (s, s * 0.82, s * 0.55), random.Random(seed).uniform(0, 180), seed, 0.0, PEB_RINGS, key)


CLOVER = dict(shoulder=(0.95, 0.3), notch=0.52, bump=(0.56, 1.0), centre=0.72)   # (radius x R, angle x step / z x h)


def clover(a, c, R, n, h, spin, seed, key):
    """A rounded clover-like ground pad (fix round 1, close-up 3 / the parts row): n rounded lobes, each a low dome
    (a bump at half the radius) with a squared-round end (two shoulders) and a deep notch to the next, a slight dip in
    the middle, flat underneath on the ground. 5n top tris + (3n - 2) bottom. Returns (verts, top faces, base)."""
    bm = a.bm
    rng = random.Random(seed)
    step = 2 * math.pi / n
    outline, bumps = [], []
    for k in range(n):
        ph = spin + k * step + rng.uniform(-0.08, 0.08) * step
        r = R * rng.uniform(0.9, 1.08)
        hz = h * rng.uniform(0.85, 1.12)
        for fr, dang in ((CLOVER["shoulder"][0] * r, -CLOVER["shoulder"][1] * step),
                         (CLOVER["shoulder"][0] * r, CLOVER["shoulder"][1] * step),
                         (CLOVER["notch"] * R, 0.5 * step)):
            outline.append(bm.verts.new(Vector((c.x + math.cos(ph + dang) * fr, c.y + math.sin(ph + dang) * fr, 0.0))))
        bumps.append(bm.verts.new(Vector((c.x + math.cos(ph) * CLOVER["bump"][0] * r,
                                          c.y + math.sin(ph) * CLOVER["bump"][0] * r, hz))))
    mid = bm.verts.new(Vector((c.x, c.y, CLOVER["centre"] * h)))
    top = [bm.faces.new((bumps[k], bumps[(k + 1) % n], mid)) for k in range(n)]
    m = len(outline)
    for k in range(n):
        s1, s2, nk = outline[3 * k], outline[3 * k + 1], outline[3 * k + 2]
        nprev = outline[(3 * k - 1) % m]
        B, B1 = bumps[k], bumps[(k + 1) % n]
        top += [bm.faces.new((nprev, s1, B)), bm.faces.new((s1, s2, B)), bm.faces.new((s2, nk, B)),
                bm.faces.new((nk, B1, B))]
    base = bm.faces.new(list(reversed(outline)))
    vs = outline + bumps + [mid]
    _close(a, vs, top + [base], key)
    return vs, top, base


def pad(a, name, guard=None, spec=None):
    """A ground-leaf pad (fix round 1): a rounded clover of 3-4 lobes, flat underneath, at the sheet's darker ground
    green (lime -> mid by distance from the trunk: the inner pads sit in the crown's shade; a position role, never
    facing). One that would cut a rock or the stem is pulled in, moved out, then shrunk."""
    c, R, n, h, seed = spec or PADS[name]
    rng = random.Random(seed)
    c = Vector((c[0], c[1], 0.0))
    vs = None
    for dr, sc in ((0.0, 1.0), (0.25, 1.0), (0.0, 0.85), (0.45, 0.85), (0.25, 0.7), (0.6, 0.6)):
        cc = c + (Vector((c.x, c.y, 0)).normalized() * dr if c.length > 1e-3 else Vector())
        vs, top, base = clover(a, cc, R * sc, n, h * sc, rng.uniform(0, 6.28), seed, _mix(LIME, LEAF_D, 0.75))
        if guard is None or guard.depth(vs) <= 0.03:
            break
        _remove(a, vs)
        vs = None
    if vs is None:
        BASE_INFO.setdefault("pads_dropped", []).append(name)
        return []
    dist = Vector((c.x, c.y, 0.0)).length
    if spec is None:
        _paint(a, top, _mix(LIME, LEAF_D, 0.5 if dist > 2.6 else 0.75))   # ground median about #729804
    _paint(a, [base], _mix(LIME, LEAF_D, 0.75))
    _mottle(a, top, 0.03, 0.8, seed)
    _tint(a, _faces(vs), 0.78 + rng.uniform(-0.03, 0.03))     # the pads lie in the crown's shade (sheet ground band)
    return vs


# ---- flowers (spec 2.5) -----------------------------------------------------------------------------------------------
FLOWERS = {   # front-view (x, z), facing (az deg, rise deg), diameter
    "F1": ((-2.15, 1.95), (240.0, 25.0), 0.6), "F2": ((-0.6, 2.35), (270.0, 20.0), 0.6),
    "F3": ((0.8, 3.45), (270.0, 45.0), 0.6), "F4": ((1.45, 2.65), (270.0, 20.0), 0.55),
    "F5": ((1.5, 1.2), (275.0, 5.0), 0.45), "F6": ((2.5, 2.4), (300.0, 20.0), 0.55),
}
FLOWER_INFO = {}


def _lens(a, root, d_out, nrm, L, W, rise, key, thick=0.025):
    """A closed spoon-shaped petal / leaf lens: 5 rim verts (root, two flanks, a broad blunt tip of two corners), a
    top and a bottom vertex (10 tris). root at `root`, running along d_out in the plane across nrm, cupped up by
    `rise` (radians)."""
    bm = a.bm
    d = (d_out - nrm * d_out.dot(nrm)).normalized()
    s = nrm.cross(d).normalized()
    up = nrm
    pts2 = [(0.0, 0.0), (0.42, -0.44), (0.95, -0.30), (0.95, 0.30), (0.42, 0.44)]

    def P(x, y, z=0.0):
        return Vector(root) + d * (x * L) + s * (y * W) + up * (math.tan(rise) * x * L + z)
    rim = [bm.verts.new(P(x, y)) for x, y in pts2]
    t = bm.verts.new(P(0.5, 0.0, thick))
    b = bm.verts.new(P(0.5, 0.0, -thick))
    n = len(rim)
    fs = [bm.faces.new((rim[k], rim[(k + 1) % n], t)) for k in range(n)]
    fs += [bm.faces.new((rim[(k + 1) % n], rim[k], b)) for k in range(n)]
    vs = rim + [t, b]
    _close(a, vs, fs, key)
    return vs


def flower(a, O, f, Dm, seed, depth=0.08, leaf=True):
    """One flower in the plane across axis f at O: a 6-sided centre column from `depth` below O (into the rosette it
    sits on) up to a domed yellow centre, five broad rounded white petals cupped up 12 deg with their roots under the
    centre, and one broad green under-leaf. Returns the verts."""
    bm = a.bm
    rng = random.Random(seed)
    f = Vector(f).normalized()
    u, v = _basis(f)
    out = []
    rc = 0.16 * Dm
    # centre column: a 5-sided bottom ring (deep, narrow), a ring just over the petals, a domed top vertex (18 tris)
    spin = rng.uniform(0, 6.28)
    r0 = [bm.verts.new(q) for q in _ring(O - f * depth, u, v, 0.55 * rc, 5, spin)]
    r1 = [bm.verts.new(q) for q in _ring(O + f * 0.06, u, v, rc, 5, spin)]
    top = bm.verts.new(O + f * 0.105)
    fs = [bm.faces.new(list(reversed(r0)))] + _band(bm, r0, r1)
    fs += [bm.faces.new((r1[k], r1[(k + 1) % 5], top)) for k in range(5)]
    cvs = r0 + r1 + [top]
    _close(a, cvs, fs, POLLEN)
    _paint(a, _band_faces(r0, r1), _mix(POLLEN, POLLEN_D, 0.5))
    out += cvs
    L = 0.5 * Dm - 0.03
    a0 = rng.uniform(0, 6.28)
    for k in range(5):
        ang = a0 + 2 * math.pi * k / 5 + rng.uniform(-0.08, 0.08)
        dd = u * math.cos(ang) + v * math.sin(ang)
        pv = _lens(a, O + dd * 0.03 + f * 0.025, dd, f, L, 0.75 * L, math.radians(12), PETAL, thick=0.022)
        _tint(a, _faces(pv), 1.0 + rng.uniform(-0.02, 0.02))
        out += pv
    if not leaf:            # the hero's flowers sit on their rosettes: the under-leaf would be hidden (fix round 1)
        return out
    # under-leaf: between two petals, below them, pointing out and a little down
    ang = a0 + math.pi / 5
    dd = u * math.cos(ang) + v * math.sin(ang)
    lv = _lens(a, O - f * 0.02, dd, f, 0.42 * Dm, 0.5 * 0.42 * Dm, math.radians(-8), LEAF_M, thick=0.025)
    out += lv
    return out


def _band_faces(r0, r1):
    s0, s1 = set(r0), set(r1)
    fs = {f for v in r0 for f in v.link_faces}
    return [f for f in fs if any(x in s0 for x in f.verts) and any(x in s1 for x in f.verts)]


FLOWER_SEARCH = [(0.0, 0.0)] + [(r * math.cos(t), r * math.sin(t)) for r in (0.12, 0.24, 0.36, 0.5)
                                  for t in [k * math.pi / 4 for k in range(8)]]


def place_flowers(a, ros_vs, guard=None):
    """Six flowers on the front half (decision 6), each on a FRONT rosette that the front camera sees at that spot
    (fix round 1: F4 sat inside the crown and F5 half under a rosette). For each flower the front-view spot (x, z) and
    nearby spots (a spiral out to 0.5) are tried until the first foliage hit (rosettes AND body lumps) lands on a
    front-half rosette facing the camera; the flower is then lifted along its axis until no petal is more than 0.03
    inside a rosette."""
    FLOWER_INFO.clear()
    tree = K.bvh_of(ros_vs)
    body = [v for v in BODY_VS if v.is_valid]
    tree_all = K.bvh_of([v for v in ros_vs if v.is_valid] + body)
    front = [sh for sh in PUFF_SHELLS if all(v.is_valid for v in sh)
             and (sum((v.co for v in sh), Vector()) / len(sh)).y < -0.25]
    tree_front = K.bvh_of([v for sh in front for v in sh])
    out = []
    used = []
    for name, ((x, z), (az, rise), Dm) in FLOWERS.items():
        H = N = None
        for dx, dz in FLOWER_SEARCH:
            o = Vector((x + dx, -12.0, z + dz))
            h1 = tree_all.ray_cast(o, Vector((0, 1, 0)), 40.0)
            h2 = tree_front.ray_cast(o, Vector((0, 1, 0)), 40.0)
            if h1[0] is None or h2[0] is None or (Vector(h1[0]) - Vector(h2[0])).length > 1e-3:
                continue
            if Vector(h2[1]).y > -0.3 or any((Vector(h2[0]) - u).length < 0.45 for u in used):
                continue
            H, N = Vector(h2[0]), Vector(h2[1])
            break
        if H is None:
            FLOWER_INFO[name] = "miss"
            continue
        used.append(H)
        face_dir = Vector((math.cos(math.radians(rise)) * math.cos(math.radians(az)),
                           math.cos(math.radians(rise)) * math.sin(math.radians(az)), math.sin(math.radians(rise))))
        f = (face_dir * 0.7 + N * 0.3).normalized()
        best = None
        for lift in (0.03, 0.06, 0.09, 0.12, 0.16, 0.2):
            O = H + f * lift
            vs = flower(a, O, f, Dm, 58400 + int(x * 10) + int(z * 100), depth=lift + 0.04, leaf=False)
            d = _ros_depth(tree, vs, skip_centre=True)
            if d <= 0.03:
                best = (vs, lift, d)
                break
            _remove(a, vs)
        if best is None:
            O = H + f * 0.24
            vs = flower(a, O, f, Dm, 58400 + int(x * 10) + int(z * 100), depth=0.28, leaf=False)
            best = (vs, 0.24, _ros_depth(tree, vs, skip_centre=True))
        out += best[0]
        FLOWER_INFO[name] = dict(at=[round(c, 2) for c in H], lift=best[1], petal_depth=round(best[2], 3))
    return out


def _ros_depth(tree, vs, skip_centre=False):
    """Deepest petal / leaf vert of a flower inside the foliage (ray parity against the rosettes' BVH)."""
    pts = [v.co for v in vs if v.is_valid]
    if skip_centre:
        pts = pts[11:]               # the centre column (11 verts) is meant to reach into the rosette
    worst = 0.0
    for p in pts:
        if _parity_in(tree, Vector(p)):
            worst = max(worst, tree.find_nearest(p)[3])
    return worst


# ---- assemblies -------------------------------------------------------------------------------------------------------
def _wood_guard(stem):
    g = _Solids()
    for name, vs in stem.items():
        g.add_vs([v for v in vs if v.is_valid], name)
    return g


def hero_geo(a):
    """GladeBush: stem, rocks and pebbles, seven clusters, two foot rosettes, ground pads, six flowers."""
    CLUSTER_INFO.clear()
    DROPPED.clear()
    ROS_LOG.clear()
    BASE_INFO.clear()
    stem = branch_stem(a)
    wood = _wood_guard(stem)
    ground = _wood_guard(stem)
    rk = {}
    for name in ROCKS:
        vs = rock(a, name)
        rk[name] = round(wood.depth(vs), 3)
        ground.add_vs(vs, name)
    BASE_INFO["rocks_in_wood"] = rk
    for i, spec in enumerate(PEBBLES):
        ground.add_vs(pebble(a, spec), f"PB{i + 1}")
    plan_rosettes()
    PUFF_VS.clear()
    PUFF_SHELLS.clear()
    BODY_VS.clear()
    leaf_clusters(a, guard=ground)      # fix round 1: rocks too (the low back clusters hang over RK4)
    BODY_VS.extend(inner_lumps(a))
    ros_vs = [v for v in PUFF_VS if v.is_valid]
    for name in FOOT:
        vs = foot_rosette(a, name, guard=ground)
        ros_vs += vs
    for name in SPRIGS:
        tv, sv = sprig(a, name, guard=ground)
        ros_vs += sv
    for name in PADS:
        pad(a, name, guard=ground)
    def leafy(v):
        k = a.mats[next(iter(v.link_faces)).material_index]
        return "leaf" in k and k != LEAF_U
    place_flowers(a, [v for v in ros_vs if v.is_valid and v.link_faces and leafy(v)])


def stem_part(a):
    branch_stem(a)


# fix round 1: the three LeafClump parts are ROUND LOBED CLUMPS matching their parts-row cells (W : H 0.97 / 1.06 / 1.06),
# not tiered tents: the hero's lobed domes (puffs) shingled over a small ball - one on top facing up, an upper ring
# facing out and up, a lower ring facing out and down - round a 5-sided body lump that fills the gaps, so the part
# reads as one chunky ball of broad lobes from every side, as the cells show. Overlapping closed shells, no booleans.
CLUMP = {   # ball radius, puff R / H / lobes, (polar deg, count) rings after the top puff, seed
    "L": dict(rc=0.36, R=0.4, H=0.36, n=6, rings=((58.0, 5), (108.0, 6)), wh=0.97, seed=58511),
    "M": dict(rc=0.3, R=0.34, H=0.3, n=5, rings=((60.0, 4), (110.0, 5)), wh=1.06, seed=58521),
    "S": dict(rc=0.21, R=0.26, H=0.23, n=5, rings=((60.0, 4), (112.0, 4)), wh=1.06, seed=58531),
}


def lobed_clump(a, cls, key):
    C = CLUMP[cls]
    rng = random.Random(C["seed"])
    rc = C["rc"]
    vs_all, fs_all = [], []
    lv, base, side, cap = _lump(a, (0.0, 0.0), rc * 1.05, rc * 1.05, -rc * 0.9, rc * 1.9, rng.uniform(0, 6.28), rng)
    _close(a, lv, [base] + side + cap, key)
    vs_all += lv
    fs_all += [base] + side + cap
    dirs = [(0.0, 0.0)]
    ph0 = rng.uniform(0, 2 * math.pi)
    for i, (pol, n) in enumerate(C["rings"]):
        ph0 += math.pi / n
        dirs += [(math.radians(pol + rng.uniform(-5, 5)), ph0 + 2 * math.pi * k / n + rng.uniform(-0.1, 0.1))
                 for k in range(n)]
    for i, (th, ph) in enumerate(dirs):
        d = Vector((math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)))
        j = rng.uniform(0.94, 1.06)
        vs, top, low = puff(a, d * rc * 0.82, d, C["R"] * j, C["H"] * j, C["n"], rng.uniform(0, 6.28),
                            C["seed"] + i, key, key)
        vs_all += vs
        fs_all += top + low
    zmin = min(v.co.z for v in vs_all)
    xs = [v.co.x for v in vs_all]
    H = max(v.co.z for v in vs_all) - zmin
    k = (max(xs) - min(xs)) / C["wh"] / H          # match the cell's W : H (a gentle vertical stretch)
    for v in vs_all:
        v.co.z = (v.co.z - zmin) * k
    return vs_all, fs_all


def rosette_part(cls):
    def fn(a):
        # a part is one module: one tone (the lighting shades it), never darker undersides by facing
        vs, fs = lobed_clump(a, cls, _leaf_key(0.5))
        _mottle(a, fs, 0.03, 0.7, CLUMP[cls]["seed"])
    return fn


def rock_part(a):
    c, size, yaw, seed, lean = ROCKS["RK1"]
    _rock(a, (0.0, 0.0), size, yaw, seed, 0.0)


def pads_part(a):
    pad(a, "a", spec=((-0.55, 0.0), 0.6, 5, 0.3, 58331))
    pad(a, "b", spec=((0.62, 0.35), 0.42, 4, 0.24, 58332))
    pad(a, "c", spec=((0.5, -0.6), 0.42, 4, 0.24, 58333))


def flower_part(a):
    flower(a, Vector((0, 0, 0.04)), Vector((0, 0.0, 1.0)), 0.6, 58600, depth=0.04)


# ---- objects ----------------------------------------------------------------------------------------------------------
NOTES = {
    HERO: "Low Bush (GladeBush): a low, wide, round-topped flowering shrub of the forest floor, paths and ruins. A "
          "faceted planked trunk with three root flares forks into two leaders; seven limbs and a bare cut spur carry "
          "seven clusters of faceted lobed leaf domes over lumpy leafy bodies (lime tops, green bodies, dark undersides); "
          "the stem shows through an arched lower window. Six white five-petal flowers with yellow centres on the "
          "front half; two foot rosettes; pale warm-grey rocks, a flat stone, pebbles and lime ground-leaf pads. No "
          "VFX. Walk-through foliage would need CanCollide = false set in Studio",
    P_L: "Leaf Clump (large): a round chunky clump of twelve faceted lobed domes over a small body; reusable",
    P_M: "Leaf Clump (medium): a round chunky clump of ten faceted lobed domes over a small body; reusable",
    P_S: "Leaf Clump (small): a round chunky clump of nine faceted lobed domes over a small body; reusable",
    P_STEM: "Branch Stem (base): the planked trunk with three root flares, two leaders, five limbs and a spur, all "
            "tips flat-cut and bare",
    P_ROCK: "Rock (base): a pale warm-grey faceted block with a flat base",
    P_GL: "Ground Leaves (optional): three low rounded clover pads, flat underneath",
    P_FL: "Flower (optional): five broad rounded white petals round a domed yellow centre, a green under-leaf",
}
COLLISION = {HERO: "hull", P_L: "hull", P_M: "hull", P_S: "hull", P_STEM: "hull", P_ROCK: "hull", P_GL: "box",
             P_FL: "box"}


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
    fn(a)
    o = a.finish(collection=M.coll(NUM, TITLE), mark_asset=not temp, origin=None)
    K.drop_unused_slots(o)
    if "kit_part" in o.data.attributes:
        o.data.attributes.remove(o.data.attributes["kit_part"])
    if not temp:
        K.tag(o, SHEET, TITLE, role, COLLISION[name], budget, NOTES[name])
    o[OFF] = [0.0, 0.0, 0.0]
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


def _post(o, uv=True):
    """Stage 2-3 pass for an object of closed shells: triangles, outward normals per shell, flat shading, no custom
    normals, origin at the bbox bottom centre, UVs (angle-based islands, overlaps cut free), bowties split."""
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
    if uv:
        M.smart_uv(o, **UV)
        lg["uv_cut"] = m012._uv_unfold(o)
    K.drop_unused_slots(o)
    return lg


def _make(name, fn, role="part", budget=1000, temp=False, uv=True):
    o = _new(name, fn, role, budget, temp=temp)
    return o, _post(o, uv=uv)


# ---- checks -----------------------------------------------------------------------------------------------------------
def _keys(o):
    return [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]


def _kind(ks, nf):
    if any("petal" in k for k in ks):
        return "petal"
    if any("pollen" in k for k in ks):
        return "centre"
    if any("lime" in k for k in ks):
        return "pad"
    if any("leaf_under" in k for k in ks):
        return "core"
    if any("leaf" in k for k in ks):
        # flower under-leaves 10 tris; cluster body lumps 18 (fix round 1: they replace the dark cores, so the checks
        # keep calling them "core"); rosettes (puffs) 8n >= 32
        return "rosette" if nf > 24 else "core" if nf > 16 else "fleaf"
    if any("rock" in k or "tan" in k for k in ks):
        return "rock" if nf > 16 else "pebble"
    if any("bark" in k for k in ks):
        return "wood"
    return "other"


def _shells(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = _keys(o)
    groups = [[] for _ in range(n)]
    for f in bm.faces:
        groups[ids[f.index]].append(f)
    kinds = [_kind({keys[f.material_index] for f in fs}, len(fs)) for fs in groups]
    wood = [k for k in range(n) if kinds[k] == "wood"]
    if wood:
        big = max(wood, key=lambda k: len(groups[k]))
        for k in wood:
            nf = len(groups[k])
            if k == big and nf > 60:
                kinds[k] = "trunk"
            elif nf <= 8:
                kinds[k] = "flare"
            elif nf <= 16:
                kinds[k] = "twig"
            else:
                kinds[k] = "limb"
    return bm, ids, n, groups, kinds


def shells_report(o):
    """Per shell: kind, tris, non-manifold edges / verts, boundary edges, winding errors (manifold edges whose two
    faces don't run the same way round), self-intersections, signed volume."""
    bm, ids, n, groups, kinds = _shells(o)
    out = []
    for k in range(n):
        fs = groups[k]
        es = {e for f in fs for e in f.edges}
        vs = list({v for f in fs for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        hits = sum(1 for a_, b_ in tree.overlap(tree) if a_ < b_ and not set(fs[a_].verts) & set(fs[b_].verts))
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) / 3.0
        out.append({"kind": kinds[k], "tris": len(fs), "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary),
                    "winding_errors": sum(1 for e in es if e.is_manifold and not e.is_contiguous),
                    "self_hits": hits, "volume": round(vol, 4)})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating dressing: per shell, whether it touches another shell (triangles intersect, or a vertex within
    tol of another shell's surface) or the ground (its lowest point within tol of the object's lowest point), and
    whether it chains by contact to the ground."""
    bm, ids, n, groups, kinds = _shells(o)
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
    gap = [1e9] * n
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    ground = {k for k in range(n) if zmin[k] - z0 <= tol}
    for k in ground:
        gap[k] = 0.0

    def chained(t):
        adj = {k: set() for k in range(n)}
        for (a_, b_), d in near.items():
            if d <= t:
                adj[a_].add(b_)
                adj[b_].add(a_)
        seen = set(ground)
        stack = list(seen)
        while stack:
            k = stack.pop()
            for m_ in adj[k]:
                if m_ not in seen:
                    seen.add(m_)
                    stack.append(m_)
        return [k for k in range(n) if k not in seen]
    floating = [k for k in range(n) if gap[k] > tol]
    un = chained(tol)
    res = {"shells": n, "floating": len(floating), "floating_kinds": sorted({kinds[k] for k in floating}),
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "unchained": len(un), "unchained_kinds": sorted({kinds[k] for k in un}),
           "ground_shells": len(ground), "kinds": {k: kinds.count(k) for k in sorted(set(kinds))}}
    bm.free()
    return res


def _solid_of(groups, k):
    vs = list({v for f in groups[k] for v in f.verts})
    vi = {v: i for i, v in enumerate(vs)}
    return [v.co.copy() for v in vs], [[vi[v] for v in f.verts] for f in groups[k]]


def bury_report(o):
    """No buried dressing (STAGES, spec 6): every rosette, core, pad, pebble, flower piece tested by ray parity against
    the stem (trunk, limbs, twigs, flares) and every rock (depth = distance from the deepest vert or face centre
    inside to that shell's surface); rocks against the stem; rosettes against the cores (centroid outside, <= 25 %
    verts inside) and against each other (<= 50 % inside a neighbour); petals and under-leaves against the rosettes."""
    bm, ids, n, groups, kinds = _shells(o)
    hard = _Solids()
    rocks = []
    for k in range(n):
        if kinds[k] in ("trunk", "limb", "twig", "flare", "rock", "pebble"):
            hard.add(*_solid_of(groups, k), f"{kinds[k]}{k}")
            if kinds[k] in ("rock", "pebble"):
                rocks.append(k)
    off = Vector(o[OFF]) if OFF in o else Vector()
    res = []
    tested = 0
    for k in range(n):
        if kinds[k] not in ("rosette", "pad", "core", "petal", "fleaf", "centre", "pebble"):
            continue
        tested += 1
        fs = groups[k]
        pts = list({v.co.copy().freeze() for f in fs for v in f.verts}) + [f.calc_center_median() for f in fs]
        skip = [f"{kinds[k]}{k}"]
        if kinds[k] == "core":         # a core is built round its limb tip and twig (close-up 1: the joint is hidden)
            skip += [nm for nm, *_ in hard.items if nm.startswith(("limb", "twig", "trunk"))]
        d, who = max((hard.point(Vector(p), skip=skip) for p in pts), key=lambda r: r[0])
        if d > 0.0:
            c = sum((f.calc_center_median() for f in fs), Vector()) / len(fs) + off
            res.append((round(d, 3), kinds[k], who, [round(x, 2) for x in c]))
    rk = []
    for k in rocks:
        fs = groups[k]
        pts = list({v.co.copy().freeze() for f in fs for v in f.verts}) + [f.calc_center_median() for f in fs]
        d = max(hard.point(Vector(p), skip=[f"rock{j}" for j in rocks] + [f"pebble{j}" for j in rocks])[0] for p in pts)
        if d > 0.0:
            rk.append((round(d, 3), [round(x, 2) for x in sum((f.calc_center_median() for f in fs), Vector()) / len(fs) + off]))
    cores = [k for k in range(n) if kinds[k] == "core"]
    csol = _Solids()
    for k in cores:
        csol.add(*_solid_of(groups, k), f"core{k}")
    ros = [k for k in range(n) if kinds[k] == "rosette"]
    rsol = _Solids()
    for k in ros:
        rsol.add(*_solid_of(groups, k), f"ros{k}")
    bad_core, bad_nb, fr_core, fr_nb = [], [], [], []
    for k in ros:
        vs = list({v for f in groups[k] for v in f.verts})
        cen = sum((v.co for v in vs), Vector()) / len(vs)
        fin = sum(1 for v in vs if csol.point(v.co)[0] > 0.0) / len(vs)
        fr_core.append(fin)
        if fin > 0.25 + 1e-6 or csol.point(cen)[0] > 0.0:
            bad_core.append((round(fin, 2), [round(x, 2) for x in cen + off]))
        worst = 0.0
        for j in ros:
            if j == k:
                continue
            nm, lo, hi, t = rsol.items[ros.index(j)]
            cnt = sum(1 for v in vs if (lo.x <= v.co.x <= hi.x and lo.y <= v.co.y <= hi.y and lo.z <= v.co.z <= hi.z)
                      and _parity_in(t, v.co))
            worst = max(worst, cnt / len(vs))
        fr_nb.append(worst)
        if worst > 0.5:
            bad_nb.append((round(worst, 2), [round(x, 2) for x in cen + off]))
    fl_bad = []
    for k in range(n):
        if kinds[k] not in ("petal", "fleaf"):
            continue
        pts = list({v.co.copy().freeze() for f in groups[k] for v in f.verts})
        d = max(rsol.point(Vector(p))[0] for p in pts)
        if d > BURY:
            fl_bad.append((round(d, 3), kinds[k]))
    bm.free()
    res.sort(key=lambda r: -r[0])
    rk.sort(key=lambda r: -r[0])
    return {"tested": tested, "over_0.05": sum(1 for r in res if r[0] > BURY), "max": res[0][0] if res else 0.0,
            "worst": res[:6], "rocks_over_0.05": sum(1 for r in rk if r[0] > BURY), "rocks": rk[:4],
            "rosettes": len(ros), "rosettes_in_core_bad": len(bad_core), "core_bad": bad_core[:4],
            "rosette_core_frac_max": round(max(fr_core), 2) if fr_core else None,
            "rosettes_in_neighbour_bad": len(bad_nb), "neighbour_frac_max": round(max(fr_nb), 2) if fr_nb else None,
            "flower_pieces_in_rosette_over_0.05": len(fl_bad), "flower_worst": sorted(fl_bad)[-3:]}


def winding_total(shells):
    return sum(s["winding_errors"] for s in shells)


LIMB_VIEWS = {"front": (0, 5), "rear": (180, 5), "f34": (0, 10), "r34": (180, 10)}


def _cam(az, el):
    a_, e_ = math.radians(az), math.radians(el)
    return Vector((math.sin(a_) * math.cos(e_), -math.cos(a_) * math.cos(e_), math.sin(e_)))


def limb_visibility(h, views=LIMB_VIEWS, step=0.1):
    """Per limb and view: the bare length seen (centreline samples whose ray to the camera clears every non-wood
    shell), in studs along the limb (trunk: z 0 -> the fork). Polylines from LIMB_INFO (build frame)."""
    bm, ids, n, groups, kinds = _shells(h)
    off = Vector(h[OFF])
    keep = [f for k in range(n) if kinds[k] not in ("trunk", "limb", "twig", "flare") for f in groups[k]]
    vs = list({v for f in keep for v in f.verts})
    vi = {v: i for i, v in enumerate(vs)}
    tree = BVHTree.FromPolygons([v.co + off for v in vs], [[vi[v] for v in f.verts] for f in keep])
    bm.free()
    lines = dict(LIMB_INFO)
    lines["TRUNK"] = [Vector((0, 0, 0.05)), Vector((0, 0, 1.2))]
    out = {}
    for name, pts in lines.items():
        row = {}
        for vn, (az, el) in views.items():
            d = _cam(az, el)
            vis = 0.0
            for p, q in zip(pts, pts[1:]):
                seg = Vector(q) - Vector(p)
                m = max(1, int(seg.length / step))
                for i in range(m):
                    c = Vector(p) + seg * ((i + 0.5) / m)
                    # sample the limb's surface facing the camera, not its axis
                    if tree.ray_cast(c + d * 0.1, d, 200.0)[0] is None:
                        vis += seg.length / m
            row[vn] = round(vis, 2)
        out[name] = row
    return out


# ---- build ------------------------------------------------------------------------------------------------------------
TARGET_SIZE = ((6.4, 0.3), (5.6, 0.4), (4.5, 0.15))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m058_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", "GladeBush"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build_hero():
    M.coll(NUM, TITLE)
    palette()
    t0 = time.time()
    h, lg = _make(HERO, hero_geo, "hero", 4000)
    lg["secs"] = round(time.time() - t0, 1)
    lg["dropped"] = list(DROPPED)
    return h, lg


def build(render=True, parts=True, close=True):
    t0 = time.time()
    h, lh = build_hero()
    hero_limbs = {k: [p.copy() for p in v] for k, v in LIMB_INFO.items()}
    log = {"hero": lh}
    objs = {}
    if parts:
        objs[P_L], log[P_L] = _make(P_L, rosette_part("L"))
        objs[P_M], log[P_M] = _make(P_M, rosette_part("M"))
        objs[P_S], log[P_S] = _make(P_S, rosette_part("S"))
        objs[P_STEM], log[P_STEM] = _make(P_STEM, stem_part)
        objs[P_ROCK], log[P_ROCK] = _make(P_ROCK, rock_part)
        objs[P_GL], log[P_GL] = _make(P_GL, pads_part)
        objs[P_FL], log[P_FL] = _make(P_FL, flower_part)
    LIMB_INFO.clear()
    LIMB_INFO.update(hero_limbs)
    _cleanup_tmp()
    order = [h] + [objs[n] for n in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped_data"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    audits = [M.audit(o) for o in order]
    thin = {o.name: m012._thin(o, 2.0) for o in order}
    shells = {o.name: shells_report(o) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = 3800 if o is h else 1000
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
                    problems.append(f"{o.name} shell {i} ({s['kind']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['kind']}): not closed outward (volume {s['volume']})")
    contact = {o.name: contact_report(o) for o in order}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} floating shells ({c['floating_kinds']}), {c['unchained']} "
                            f"unchained ({c['unchained_kinds']})")
    bury = {o.name: bury_report(o) for o in order if o.name in (HERO, P_GL, P_FL)}
    for n_, b in bury.items():
        if b["over_0.05"]:
            problems.append(f"{n_}: {b['over_0.05']} dressing shells more than {BURY} inside wood / rock "
                            f"(worst {b['worst'][:3]})")
        if b["rocks_over_0.05"]:
            problems.append(f"{n_}: {b['rocks_over_0.05']} rocks more than {BURY} into the stem")
        if b["rosettes_in_core_bad"]:
            problems.append(f"{n_}: {b['rosettes_in_core_bad']} rosettes buried in a core ({b['core_bad'][:3]})")
        if b["rosettes_in_neighbour_bad"]:
            problems.append(f"{n_}: {b['rosettes_in_neighbour_bad']} rosettes > 50 % inside a neighbour")
        if b["flower_pieces_in_rosette_over_0.05"]:
            problems.append(f"{n_}: {b['flower_pieces_in_rosette_over_0.05']} petals / under-leaves > {BURY} "
                            f"inside a rosette")
    trunks = sum(1 for s in shells[HERO] if s["kind"] == "trunk")
    if trunks != 1:
        problems.append(f"{HERO}: trunk shells {trunks}, expected 1")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if abs(h[OFF][2]) > 1e-4:
        problems.append(f"{HERO}: origin offset z {h[OFF][2]:.3f} (decision 10: 0)")
    for o in order:
        if [c for c in o.children if c.get("vfx_kind")]:
            problems.append(f"{o.name}: has VFX sockets (decision 11: none)")
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    vis = limb_visibility(h)
    kinds = {}
    for s in shells[HERO]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts", "origin_offset", "transforms_applied")} for au in audits],
           "hero_shells": kinds, "winding": {o: winding_total(s) for o, s in shells.items()},
           "contact": contact, "bury": bury, "base_info": dict(BASE_INFO), "clusters": dict(CLUSTER_INFO),
           "flowers": dict(FLOWER_INFO), "limb_visibility": vis, "thin": thin, "log": log, "problems": problems,
           "uv": uv, "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders ----------------------------------------------------------------------------------------------------------
SHEET_VIEWS = {"f34_sheet": (0, 10), "r34_sheet": (180, 10), "front_sheet": (0, 5), "side_sheet": (90, 5),
               "rear_sheet": (180, 5), "top_sheet": (0, 89)}
VIEW_NAMES = ("front34", "rear34", "front", "side", "rear", "top", "underside")
PARTS_SHOT = (0, 25)
SCALE_AT = (5.2, 0.0, 0.0)


def _scale_marker(h, at=SCALE_AT, tall=5.5):
    """A 5.5-stud character-sized marker (legs, torso, head) beside the bush."""
    a = K.fk().Asset(PFX + "char", "probe", seed=1, tint_var=0.0)
    a.cyl(0.55, 0.55, 2.6, sides=8, loc=(0, 0, 0), mat=ROCK_D, tint=0.7)
    a.cyl(0.8, 0.7, 1.9, sides=8, loc=(0, 0, 2.6), mat=ROCK_D, tint=0.7)
    a.cyl(0.5, 0.45, tall - 4.5, sides=8, loc=(0, 0, 4.5), mat=ROCK_D, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
    c.location = off @ Vector(at)
    bpy.context.view_layer.update()
    return c


def _temp(name, fn):
    return _new(PFX + name, fn, "part", 1000, temp=True)


def _exploded(objs):
    """The parts laid out like the sheet's Exploded Construction: the stem and rocks / pads / pebbles at the bottom,
    every cluster lifted 1.5 off its tip (twig and core included), two flowers beside their tips."""
    h = objs[0]
    x0, y0 = h.location.x + 40, h.location.y
    shown = []
    base = _temp("expl_base", lambda a: (branch_stem(a), [rock(a, n) for n in ROCKS], [pebble(a, s) for s in PEBBLES],
                                         [pad(a, n) for n in PADS]))
    base.matrix_world = Matrix.Translation((x0, y0, 0))
    shown.append(base)
    for nm, P in CLUSTERS.items():
        o = _temp("expl_" + nm, lambda a, nm=nm: (branch_stem_info(), leaf_cluster(a, nm)))
        tip, d = TIPS[P["feed"]]
        lift = (Vector((P["c"][0], P["c"][1], 0)) * 0.35 + Z * 1.6)
        o.matrix_world = Matrix.Translation((x0, y0, 0)) @ Matrix.Translation(lift)
        shown.append(o)
    for i, (dx, tipname) in enumerate(((-1.4, "LOW-L"), (1.4, "LOW-R"))):
        tip, d = TIPS[tipname]
        o = _temp(f"expl_fl{i}", lambda a: flower(a, Vector(), Vector((0, -0.6, 0.8)), 0.6, 58610, depth=0.1))
        o.matrix_world = Matrix.Translation((x0, y0, 0)) @ Matrix.Translation(tip + Vector((dx * 0.6, -0.4, 0.6)))
        shown.append(o)
    bpy.context.view_layer.update()
    return shown


def branch_stem_info():
    """TIPS / LIMB_INFO without keeping any geometry."""
    a = K.fk().Asset(PFX + "info", "probe", seed=1, tint_var=0.0)
    branch_stem(a)
    a.bm.free()


def render_views(objs, close=True):
    h = objs[0]
    hero_limbs = {k: [p.copy() for p in v] for k, v in LIMB_INFO.items()}
    shown = _exploded(objs) if len(objs) > 1 else []
    marker = _scale_marker(h)
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        for o in objs[1:]:
            extra["part_" + o.name.replace("GladeBush", "").lower()] = ([o], *PARTS_SHOT)
        if shown:
            extra["exploded"] = (shown, 0, 14)
        extra["scale"] = ([h, marker], 0, 6)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = m033._long_lens(kit)
        try:
            sheet = M.views(NUM, [h], names=VIEW_NAMES, extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet}
        if close:
            out.update(render_close_ups(objs))
        return out
    finally:
        for o in shown + [marker]:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me.users == 0:
                bpy.data.meshes.remove(me)
        LIMB_INFO.clear()
        LIMB_INFO.update(hero_limbs)
        M.display(NUM, objs, TITLE)


def render_close_ups(objs):
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    by = {o.name: o for o in objs}
    h = objs[0]
    out = {}
    rc = m033.render_close

    def at(o, p):
        return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)
    out["window_cu"] = rc([h], f"{d}/window_cu.png", 0, 6, at(h, (0.2, -1.0, 1.2)), 1.6)
    out["rock_cu"] = rc([h], f"{d}/rock_cu.png", -30, 10, at(h, (-2.2, -1.6, 0.4)), 1.3)
    out["rosette_cu"] = rc([h], f"{d}/rosette_cu.png", 0, 35, at(h, (0.3, -0.6, 4.0)), 1.3)
    out["underside_hero"] = rc([h], f"{d}/underside_hero.png", 0, -80, at(h, (0.0, 0.0, 1.8)), 3.4)
    if P_L in by:
        o = by[P_L]
        out["underside_part"] = rc([o], f"{d}/underside_part.png", 0, -80, at(o, (0, 0, 0.4)), 0.9)
    # branch-to-leaf attachment: the stem part's fork with the CFL cluster lifted off its tip
    if P_STEM in by:
        t = by[P_STEM]
        branch_stem_info()
        cl = _temp("attach_CFL", lambda a: leaf_cluster(a, "CFL"))
        cl.matrix_world = t.matrix_world @ Matrix.Translation(-Vector(t[OFF])) @ Matrix.Translation((-0.35, -0.35, 1.0))
        bpy.context.view_layer.update()
        try:
            out["attach_cu"] = rc([t, cl], f"{d}/attach_cu.png", -20, 25, at(t, (-0.6, -0.6, 2.2)), 1.7)
        finally:
            me = cl.data
            bpy.data.objects.remove(cl, do_unlink=True)
            bpy.data.meshes.remove(me)
    return out


def preview(names=("f34_sheet", "front_sheet", "rear_sheet", "side_sheet", "top_sheet", "r34_sheet"), vfx=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig


def hero_only():
    h, lg = build_hero()
    _cleanup_tmp()
    others = [bpy.data.objects[n] for n in PARTS if n in bpy.data.objects]
    M.display(NUM, [h] + others, TITLE)
    au = M.audit(h)
    sh = shells_report(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals", "origin_offset")}, "log": lg,
            "offset": list(h[OFF]), "winding": winding_total(sh),
            "kinds": {k: [sum(1 for s in sh if s["kind"] == k), sum(s["tris"] for s in sh if s["kind"] == k)]
                      for k in sorted({s["kind"] for s in sh})},
            "clusters": dict(CLUSTER_INFO), "flowers": dict(FLOWER_INFO), "base": dict(BASE_INFO)}
