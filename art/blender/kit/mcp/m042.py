"""042 Young Fir (references/042.png): a slim stepped green spire of three stacked foliage tiers (a pointed star-cone
crown with a hem of 8 drooping kite flaps, a middle tier of 12 flaps and a lower skirt of 16, each in two staggered
rows), every tier a closed core-and-hub shell that sits by contact on the tier below (flat cap, octagonal hub with a
small recess, gap 0.015), the skirt's hub on the flat top of a chunky orange-brown octagonal planked trunk that flares
into six kinked angular roots (unioned into the trunk), on a thin pale sand patch dressed with five chunky warm-grey
rocks, three pebbles and clumps of upright lanceolate lime and green leaves.

    import importlib, kit_models, m042; importlib.reload(kit_models); importlib.reload(m042); m042.build()

Build frame: studs, front -Y, +X right, ground z 0 = the sand patch's flat underside, tree axis at (0, 0). Every object
ends with its origin at its bbox bottom centre; o["m042_offset"] is that origin in the build frame. W04 owns every
YoungFir* name, so the names are TieredFir* (spec 8):
- TieredFirCrownTier / TieredFirMiddleTier / TieredFirLowerSkirt: tier(kind): one closed core + hub shell and its flap
  shells (8 / 12 / 16), each flap's root buried in the core, row B seated clear of row A.
- TieredFirTrunk: the octagonal planked body (16 facets, slits, flat top with an inner ring) with six roots exact-unioned
  in one at a time at the world origin: one closed shell.
- TieredFirRootBase: the sand patch, rocks, pebbles and plant clumps (separate closed shells, all on the patch).
- TieredFir (hero): all of the above in one object of closed shells (only the roots are unioned, into the trunk).
Colour (stage 4) is painted by position and role inside the builders (never by facing). Stages 5-6: none (the sheet
shows no glow, light or effect). See M042_spec.md.
"""
import math
import random
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri

import kit_mcp as K
import kit_models as M
import m012
import m033

NUM, TITLE, SHEET = 42, "Young Fir", "M042"
OFF = "m042_offset"
PFX = "_m042_"
HERO = "TieredFir"
CROWN_P, MID_P, LOW_P, TRUNK_P, BASE_P = ("TieredFirCrownTier", "TieredFirMiddleTier", "TieredFirLowerSkirt",
                                          "TieredFirTrunk", "TieredFirRootBase")

NEEDLE, NEEDLE_LIGHT, NEEDLE_DEEP = "m042_needle", "m042_needle_light", "m042_needle_deep"
BARK, BARK_LIGHT, BARK_DEEP = "m042_bark", "m042_bark_light", "m042_bark_deep"
ROCK, ROCK_LIGHT, ROCK_DEEP = "m042_rock", "m042_rock_light", "m042_rock_deep"
SAND, SAND_DEEP = "m042_sand", "m042_sand_deep"
PLANT, PLANT_DEEP = "m042_plant", "m042_plant_deep"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
GAP = 0.015

# key -> (hex, roughness, low specular). Stage 4 (M042_spec.md "Stage 4"):
# Pass 1, K.calibrate on the kit test dome against TARGETS (rendered sRGB): needle #7E9D32 (153,189,51), light #85A034
# (163,193,53), deep #295C39 (45,105,59), bark #965B24 (189,111,51), bark light #AB6F39 (216,135,70), bark deep #663F22
# (127,78,48), rock #AAA29A (215,199,180), rock light #B4ADA4, rock deep #8B8786, sand #D0BF9C (230,204,157), sand deep
# #B1A07D, plant #93A134 (182,195,53), plant deep #466E27 (80,128,39).
# Pass 2, against the f34_sheet render (floor hidden, the study's masks): the kit studio lights both halves of the
# canopy almost alike, so a needle base calibrated to the sheet's LIT half made the whole canopy lime (median #9CBE35
# against the sheet's #508733). The base was taken down to a mid green (#437529) and the light key made a yellower
# lime (#B0BC2A) for the flap tips, so the canopy median (#53922C) and the lit (v > .7) median (#9BBE2C, sheet
# #A6C434) both land near the sheet. Deep a cooler teal (#1E5038). Sand x(0.78, 0.74, 0.70) linear (it rendered
# #FFEAB6 against #E7CC9C); rock a little cooler (#9C9894); plant deep darker (#335A20; plants rendered too lime).
PALETTE = {
    NEEDLE: ("#437529", 0.85, True),
    NEEDLE_LIGHT: ("#B0BC2A", 0.85, True),
    NEEDLE_DEEP: ("#1E5038", 0.9, True),
    BARK: ("#965B24", 0.9, False),
    BARK_LIGHT: ("#AB6F39", 0.9, False),
    BARK_DEEP: ("#663F22", 0.95, False),
    ROCK: ("#9C9894", 0.85, False),
    ROCK_LIGHT: ("#A9A49F", 0.85, False),
    ROCK_DEEP: ("#8A8889", 0.9, False),
    SAND: ("#BAA784", 0.95, False),
    SAND_DEEP: ("#9E8B69", 0.95, False),
    PLANT: ("#93A134", 0.85, True),
    PLANT_DEEP: ("#335A20", 0.85, True),
}
# calibration targets (spec 5.4: rendered medians of unshadowed regions of the sheet)
TARGETS = {NEEDLE: ((0x95, 0xBC, 0x32), "green"), NEEDLE_LIGHT: ((0xA6, 0xC4, 0x34), "green"),
           NEEDLE_DEEP: ((0x2E, 0x6A, 0x3C), "green"), BARK: ((0xBE, 0x6F, 0x30), "brown"),
           BARK_LIGHT: ((0xD6, 0x87, 0x45), "brown"), BARK_DEEP: ((0x80, 0x4E, 0x2E), "brown"),
           ROCK: ((0xD9, 0xC8, 0xB5), "all"), ROCK_LIGHT: ((0xE5, 0xD4, 0xC0), "all"),
           ROCK_DEEP: ((0xB0, 0xA5, 0x9D), "all"), SAND: ((0xE7, 0xCC, 0x9C), "brown"),
           SAND_DEEP: ((0xE1, 0xC4, 0x90), "brown"), PLANT: ((0xB8, 0xC5, 0x34), "green"),
           PLANT_DEEP: ((0x50, 0x81, 0x27), "green")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    # mixed keys made by an earlier build: re-mix them from the (possibly new) parents
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m042_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k.endswith("_" + tail) and k.startswith(k1)), None) or \
                next((k for k in PALETTE if k.endswith(tail)), None)
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
_faces = m033._faces
_zip = m033._zip
_mottle = m033._mottle


def _q(t, steps=4):
    t = max(0.0, min(1.0, t))
    return round(t * steps) / steps


def _mix(k1, k2, t):
    return K.mix_key(k1, k2, _q(t))


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


def _shell(a, verts, key):
    """Orient a closed shell's faces outward and give it a key."""
    fs = _faces(verts)
    bmesh.ops.recalc_face_normals(a.bm, faces=fs)
    a._finish(verts, key, tint=1.0)
    return fs


def _u(az):
    r = math.radians(az)
    return Vector((math.cos(r), math.sin(r), 0.0))


# ---- flaps (spec 2.3) ----------------------------------------------------------------------------------------------------
S1, S2 = 0.42, 0.75


def flap(a, az, r0, z0, r1, z1, w, droop=15.0, roll=0.0, keys=(NEEDLE, NEEDLE, NEEDLE)):
    """One closed 16-tri kite flap: root point (r0, z0) on azimuth az (buried in its core), the tip at (r1, z1); widest
    (w) at 0.42 of its length with a raised ridge (0.11 w) and a keel (0.06 w); a second section at 0.75 (0.74 w,
    ridge and keel about halved) bent down a further `droop` degrees; then the tip. keys = (root fan, band, tip fan): the
    colour runs along the flap (position, never facing). Returns (verts, faces by zone)."""
    bm = a.bm
    segs = (S1, S2 - S1, 1.0 - S2)
    b1, b2 = math.radians(droop * 0.15), math.radians(droop)
    loc = (0.0, -b1, -b1 - b2)
    vx = sum(l * math.cos(p) for l, p in zip(segs, loc))
    vz = sum(l * math.sin(p) for l, p in zip(segs, loc))
    cx, cz = r1 - r0, z1 - z0
    th0 = math.atan2(cz, cx) - math.atan2(vz, vx)
    L = math.hypot(cx, cz) / math.hypot(vx, vz)
    u = _u(az)
    side = Vector((-u.y, u.x, 0.0))
    up = Vector((0, 0, 1))

    def dirv(phi):
        return u * math.cos(phi) + up * math.sin(phi)
    phis = [p + th0 for p in loc]
    P0 = u * r0 + up * z0
    P1 = P0 + dirv(phis[0]) * segs[0] * L
    P2 = P1 + dirv(phis[1]) * segs[1] * L
    P3 = P2 + dirv(phis[2]) * segs[2] * L
    rot = math.radians(roll)

    def section(P, pa, pb, half, ridge, keel):
        t = (dirv(pa) + dirv(pb)).normalized()
        n = t.cross(side).normalized()
        R = Matrix.Rotation(rot, 3, t)
        s, nn = R @ side, R @ n
        return [P - s * half, P + nn * ridge, P + s * half, P - nn * keel]
    ring1 = [bm.verts.new(p) for p in section(P1, phis[0], phis[1], w / 2, 0.11 * w, 0.06 * w)]
    ring2 = [bm.verts.new(p) for p in section(P2, phis[1], phis[2], 0.37 * w, 0.06 * w, 0.035 * w)]
    v0, v3 = bm.verts.new(P0), bm.verts.new(P3)
    root = [bm.faces.new((v0, ring1[i], ring1[(i + 1) % 4])) for i in range(4)]
    band = []
    for i in range(4):
        j = (i + 1) % 4
        band.append(bm.faces.new((ring1[i], ring2[i], ring2[j])))
        band.append(bm.faces.new((ring1[i], ring2[j], ring1[j])))
    tip = [bm.faces.new((ring2[i], v3, ring2[(i + 1) % 4])) for i in range(4)]
    vs = [v0, v3] + ring1 + ring2
    bmesh.ops.recalc_face_normals(bm, faces=root + band + tip)
    a._finish(vs, keys[1], tint=1.0)
    _paint(a, root, keys[0])
    _paint(a, tip, keys[2])
    return vs, {"root": root, "band": band, "tip": tip}


# ---- tiers (spec 2.2) -----------------------------------------------------------------------------------------------------
# kind -> hub (bottom r, height, bottom z), core (cap r, cap z, rim r, rim z), rows: (count, first azimuth, root r, root z,
# tip r, tip z, width, droop, front-facing tip z or None), keys per row (root, band, tip) as (key2, t) mixes off NEEDLE
TIERS = {
    # every tier is a cone of flaps lying on it (about 41-48 deg, as the sheet's tier outlines): row A from low on the
    # core out to the hem, row B from the cap over row A to about two thirds of the way out
    "crown": dict(hub=(0.5, 0.15, 12.545), skirt=(0.62, 12.57), seed=42100,
                  rows=[dict(n=4, az0=270.0, r0=1.2, z0=13.35, r1=2.95, z1=11.6, w=2.1, droop=16.0, front=None,
                             fix="roll"),
                        dict(n=4, az0=315.0, r0=1.0, z0=13.45, r1=2.6, z1=11.9, w=1.85, droop=16.0, front=None,
                             fix="roll")],
                  keys=[((NEEDLE_DEEP, 0.25), (NEEDLE_LIGHT, 0.25), (NEEDLE_LIGHT, 0.75)),
                        ((NEEDLE_DEEP, 0.25), (NEEDLE_LIGHT, 0.25), (NEEDLE_LIGHT, 0.75))]),
    "middle": dict(hub=(0.9, 0.15, 9.615), core=(0.6, 12.53, 1.3, 11.3), skirt=(1.04, 9.64), seed=42200,
                   rows=[dict(n=6, az0=270.0, r0=0.75, z0=11.55, r1=4.25, z1=8.75, w=3.0, droop=24.0, front=8.55,
                              fix="roll"),
                         dict(n=6, az0=300.0, r0=0.5, z0=12.35, r1=3.8, z1=9.6, w=2.25, droop=20.0, front=None,
                              fix="lift")],
                   keys=[((NEEDLE_DEEP, 0.5), (NEEDLE, 0.0), (NEEDLE_LIGHT, 0.5)),
                         ((NEEDLE_DEEP, 0.25), (NEEDLE_LIGHT, 0.25), (NEEDLE_LIGHT, 0.75))]),
    "lower": dict(hub=(1.1, 0.3, 6.615), core=(1.2, 9.60, 1.9, 8.3), seed=42300,
                  rows=[dict(n=8, az0=270.0, r0=1.1, z0=8.4, r1=6.0, z1=4.65, w=3.0, droop=24.0, front=4.45,
                             fix="roll"),
                        dict(n=8, az0=292.5, r0=1.0, z0=9.55, r1=5.1, z1=5.85, w=2.7, droop=20.0, front=None,
                             fix="lift")],
                  keys=[((NEEDLE_DEEP, 0.5), (NEEDLE_DEEP, 0.25), (NEEDLE_LIGHT, 0.5)),
                        ((NEEDLE_DEEP, 0.5), (NEEDLE, 0.0), (NEEDLE_LIGHT, 0.5))]),
}
CROWN_APEX, CROWN_RIM_Z = 16.0, 13.3
CROWN_RIDGES = (1.7, 1.25, 0.95)        # main ridge, minor ridge, valley radii of the star cone's rim
TIER_INFO = {}


def _hub(a, r, h, z0, ring_top_r=None):
    """Octagonal hub frustum (corners at 22.5 + 45 k, like the trunk) with a flat bottom and a small recess (Ø 0.3,
    0.08 deep) in its middle. Returns (top ring, all verts, hub faces, recess faces)."""
    bm = a.bm
    rt = ring_top_r or 0.85 * r
    azs = [22.5 + 45 * k for k in range(8)]
    top = [bm.verts.new(_u(t) * rt + Vector((0, 0, z0 + h))) for t in azs]
    bot = [bm.verts.new(_u(t) * r + Vector((0, 0, z0))) for t in azs]
    rec = [bm.verts.new(_u(t) * 0.15 + Vector((0, 0, z0))) for t in azs]
    rec_t = [bm.verts.new(_u(t) * 0.15 + Vector((0, 0, z0 + 0.08))) for t in azs]
    c = bm.verts.new(Vector((0, 0, z0 + 0.08)))
    hub_f, rec_f = [], []
    for k in range(8):
        j = (k + 1) % 8
        hub_f.append(bm.faces.new((top[k], bot[k], bot[j], top[j])))
        hub_f.append(bm.faces.new((bot[k], rec[k], rec[j], bot[j])))
        rec_f.append(bm.faces.new((rec[k], rec_t[k], rec_t[j], rec[j])))
        rec_f.append(bm.faces.new((rec_t[k], c, rec_t[j])))
    return top, top + bot + rec + rec_t + [c], hub_f, rec_f


def _skirt(bm, rim, skirt, ht):
    """The core's underside: straight from the rim to the hub's top ring, or (skirt = (radius scale, z)) first down a
    short wall to a smaller ring at z, then in to the hub, so the core hangs down round its hub and hides it from the
    side (the sheet's waists show only green there)."""
    if not skirt:
        return _zip(bm, rim, ht), []
    f_r, z = skirt
    sk = [bm.verts.new(Vector((v.co.x * f_r, v.co.y * f_r, z))) for v in rim]
    n = len(rim)
    fs = [bm.faces.new((rim[k], rim[(k + 1) % n], sk[(k + 1) % n], sk[k])) for k in range(n)]
    return fs + _zip(bm, sk, ht), sk


def _core(a, kind):
    """The tier's closed core + hub shell (spec 2.3): a pleated frustum (corners at the row A azimuths pushed out 0.15,
    between them pulled in 0.15) with a flat top cap, an underside sloping up from the rim to the hub, the hub. The
    crown's core is the star cone (4 main ridges, 4 minor, valleys between) with its hub."""
    bm = a.bm
    T = TIERS[kind]
    hr, hh, hz = T["hub"]
    ht, hvs, hub_f, rec_f = _hub(a, hr, hh, hz)
    if kind == "crown":
        apex = bm.verts.new(Vector((0, 0, CROWN_APEX)))
        rim = []
        for k in range(16):
            az = 22.5 * k
            r = CROWN_RIDGES[0] if k % 4 == 0 else CROWN_RIDGES[1] if k % 4 == 2 else CROWN_RIDGES[2]
            rim.append(bm.verts.new(_u(az) * r + Vector((0, 0, CROWN_RIM_Z))))
        top_f = [bm.faces.new((apex, rim[k], rim[(k + 1) % 16])) for k in range(16)]
        under_f, sk = _skirt(bm, rim, T.get("skirt"), ht)
        vs = [apex] + rim + sk + hvs
    else:
        cr, cz, rr, rz = T["core"]
        nA = T["rows"][0]["n"]
        a0 = T["rows"][0]["az0"] % 360
        step = 360.0 / nA
        # rings ordered by increasing azimuth from the first row-A azimuth
        cap = [bm.verts.new(_u(a0 + k * step) * cr + Vector((0, 0, cz))) for k in range(nA)]
        rim = []
        for k in range(2 * nA):
            r = rr + (0.15 if k % 2 == 0 else -0.15)
            rim.append(bm.verts.new(_u(a0 + k * step / 2) * r + Vector((0, 0, rz))))
        cc = bm.verts.new(Vector((0, 0, cz)))
        top_f = [bm.faces.new((cap[k], cap[(k + 1) % nA], cc)) for k in range(nA)]
        for k in range(nA):
            j = (k + 1) % nA
            top_f.append(bm.faces.new((cap[k], rim[2 * k], rim[2 * k + 1])))
            top_f.append(bm.faces.new((cap[k], rim[2 * k + 1], cap[j])))
            top_f.append(bm.faces.new((cap[j], rim[2 * k + 1], rim[(2 * k + 2) % (2 * nA)])))
        under_f, sk = _skirt(bm, rim, T.get("skirt"), ht)
        vs = cap + rim + sk + [cc] + hvs
    fs = top_f + under_f + hub_f + rec_f
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    if kind == "crown":
        a._finish(vs, _mix(NEEDLE, NEEDLE_LIGHT, 0.5), tint=1.0)
    else:
        a._finish(vs, _mix(NEEDLE, NEEDLE_DEEP, 0.75), tint=1.0)
        _paint(a, [f for f in top_f if f.calc_center_median().z > T["core"][1] - 1e-3], _mix(NEEDLE, NEEDLE_DEEP, 0.5))
    _paint(a, under_f, _mix(NEEDLE, NEEDLE_DEEP, 0.75))
    _paint(a, hub_f, _mix(BARK, BARK_DEEP, 0.75))
    _paint(a, rec_f, BARK_DEEP)
    _mottle(a, top_f + under_f, 0.03, 0.5, 42010 + len(kind))
    return vs, fs


DRAPE = True
ROLL = 7.0        # every flap rolled the same way about its spine: neighbours shingle (one's high edge over the
                   # next one's low edge) instead of cutting through each other


def _inside(tree, p):
    """Ray-parity test: is p inside the closed shell in tree?"""
    n, o, d = 0, p.copy(), Vector((0.31, 0.17, 0.93)).normalized()
    for _ in range(24):
        h = tree.ray_cast(o, d)
        if h[0] is None:
            break
        n += 1
        o = h[0] + d * 1e-4
    return n % 2 == 1


def _cut_pts(ta, tb):
    """Points where the edges of triangle ta cross triangle tb and the other way round."""
    out = []
    for t1, t2 in ((ta, tb), (tb, ta)):
        for i in range(3):
            p, q = t1[i], t1[(i + 1) % 3]
            d = q - p
            L = d.length
            if L < 1e-9:
                continue
            h = intersect_ray_tri(t2[0], t2[1], t2[2], d / L, p, True)
            if h is not None and (h - p).length <= L:
                out.append(h)
    return out


def _hits(vs, coords, polys, core=None):
    """Whether a flap (its verts) visibly cuts into any of the triangles (coords, polys) placed before it: any crossing
    point outside the tier's core (a BVH of the core shell; crossings inside it are hidden)."""
    fs = _faces(vs)
    idx = {v: i for i, v in enumerate(vs)}
    mine_p = [[idx[v] for v in f.verts] for f in fs]
    mine_c = [v.co.copy() for v in vs]
    mine = BVHTree.FromPolygons(mine_c, mine_p)
    for i, j in mine.overlap(BVHTree.FromPolygons(coords, polys)):
        ta = [mine_c[k] for k in mine_p[i]]
        tb = [coords[k] for k in polys[j]]
        for p in _cut_pts(ta, tb):
            if core is None or not _inside(core, p):
                return True
    return False


def _drape(vs, tree, clear, extra=0.0):
    """Lay a row B flap over row A: each section of the flap (ring 1, ring 2, then the tip) is lifted just enough that
    no sample of the faces round it (corners, edge midpoints, centres) lies below row A's top surface + clear (ray cast
    down onto row A). `extra` lifts the outer sections a little more when A still pokes through between samples. The
    root stays buried in the core. vs = flap()'s verts: root, tip, ring 1 (4), ring 2 (4). Returns sections lifted."""
    groups = [vs[2:6], vs[6:10], [vs[1]]]
    fneed = {}
    for f in _faces(vs):
        pts = [v.co for v in f.verts] + [f.calc_center_median()]
        pts += [(e.verts[0].co + e.verts[1].co) / 2 for e in f.edges]
        need = 0.0
        for p in pts:
            hit = tree.ray_cast(p + Vector((0, 0, 4.0)), Vector((0, 0, -1)), 8.0)
            if hit[0] is not None and hit[0].z > p.z - 1.0:
                need = max(need, hit[0].z + clear - p.z)
        fneed[f] = need
    lifted = 0
    prev = 0.0
    for gi, g in enumerate(groups):
        need = max([fneed[f] for v in g for f in v.link_faces if f in fneed] + [0.0])
        need = max(need, 0.5 * prev, extra * gi)
        if need > 0:
            for v in g:
                v.co.z += need
            lifted += 1
        prev = need
    return lifted


def tier(a, kind):
    """A whole tier: its core + hub shell, then row A flaps, then row B flaps. Every flap is checked against the flaps
    already placed in the tier: a row A flap that would cut into a neighbour is rolled further (then narrowed), a row B
    flap is lifted (root and tip) until it rests clear on row A. Returns the tier's verts."""
    T = TIERS[kind]
    rng = random.Random(T["seed"])
    core_vs, core_fs = _core(a, kind)
    out = list(core_vs)
    ci = {v: i for i, v in enumerate(core_vs)}
    core = BVHTree.FromPolygons([v.co.copy() for v in core_vs], [[ci[v] for v in f.verts] for f in _faces(core_vs)])
    info = {"lifted": 0, "rolled": 0, "narrowed": 0, "flaps": 0, "unresolved": 0}
    rowA, rowB = ([], []), ([], [])          # (coords, polys) of the flaps placed so far, per row kind
    for ri, row in enumerate(T["rows"]):
        keys = tuple(_mix(NEEDLE, k2, t) for k2, t in T["keys"][ri])
        step = 360.0 / row["n"]
        for k in range(row["n"]):
            az = row["az0"] + k * step + rng.uniform(-5, 5)
            r1 = row["r1"] * rng.uniform(0.96, 1.04)
            z1 = row["z1"] + rng.uniform(-0.1, 0.1)
            if row["front"] is not None and abs(((row["az0"] + k * step) - 270.0 + 180) % 360 - 180) < 1:
                z1 = row["front"] + rng.uniform(-0.05, 0.05)
            w = row["w"] * rng.uniform(0.92, 1.08)
            roll = ROLL + rng.uniform(-3, 3)
            z0 = row["z0"]
            tone = 1.0 + rng.uniform(-0.04, 0.04)
            a_tree = BVHTree.FromPolygons(*rowA) if DRAPE and row["fix"] == "lift" and rowA[1] else None
            for attempt in range(16):
                vs, zones = flap(a, az, row["r0"], z0, r1, z1, w, row["droop"], roll, keys)
                if a_tree is not None:          # row B: drape it over row A first
                    clear = 0.04
                    for it in range(14):
                        if not _hits(vs, *rowA, core=core):
                            break
                        info["lifted"] += _drape(vs, a_tree, clear, extra=0.03 * it)
                        clear += 0.02
                    else:
                        info["unresolved"] += 1
                mine = rowB if row["fix"] == "lift" else rowA
                if not mine[1] or not _hits(vs, *mine, core=core):
                    break
                if attempt == 15:
                    info["unresolved"] += 1
                    break
                bmesh.ops.delete(a.bm, geom=vs, context="VERTS")
                if roll < ROLL + 12:
                    roll += 3.0
                    info["rolled"] += 1
                else:
                    w *= 0.95
                    info["narrowed"] += 1
            if row["fix"] == "lift":
                info.setdefault("tip_lift", []).append(round(vs[1].co.z - z1, 2))
            fs = _faces(vs)
            _tint(a, fs, tone)
            _mottle(a, fs, 0.03, 0.6, T["seed"] + 17 * k + 101 * ri)
            coords, polys = rowB if row["fix"] == "lift" else rowA
            base = len(coords)
            idx = {v: base + i for i, v in enumerate(vs)}
            coords += [v.co.copy() for v in vs]
            polys += [[idx[v] for v in f.verts] for f in fs]
            out += vs
            info["flaps"] += 1
    TIER_INFO[kind] = info
    return out


def crown_part(a):
    tier(a, "crown")


def middle_part(a):
    tier(a, "middle")


def lower_part(a):
    tier(a, "lower")


# ---- trunk and roots (spec 2.4) ----------------------------------------------------------------------------------------
TRUNK_RINGS = ((0.05, 1.9), (0.6, 1.75), (1.5, 1.45), (2.5, 1.17), (3.3, 1.10), (4.2, 1.06), (5.0, 1.04),
               (5.8, 1.02), (6.6, 1.0))
TRUNK_TOP = 6.6
# plank pattern: each octagon side split once; the split vertex pushed out (+) or in (-) of the flat side
PLANKS = (0.12, -0.08, 0.10, -0.12, 0.11, -0.07, 0.12, -0.10)
# slits: (mid column k at azimuth 45 k, ring indices pulled in 0.14): front-left, right, back
SLITS = ((5, (4, 5)), (0, (2, 3)), (3, (5, 6)))
# roots: name, azimuth, reach (r from the axis), width and height at the trunk, segments, kink (deg), ridge start z
ROOTS = (("RF", 285.0, 4.2, 1.4, 1.9, 3, 10.0, 2.8), ("RL", 175.0, 3.4, 1.25, 1.7, 2, -9.0, 2.5),
         ("RFL", 235.0, 3.0, 1.15, 1.55, 2, 8.0, 2.3), ("RR", 345.0, 3.8, 1.25, 1.7, 3, -8.0, 2.6),
         ("RB1", 60.0, 3.0, 1.15, 1.45, 2, 9.0, 2.2), ("RB2", 120.0, 2.8, 1.15, 1.45, 2, -7.0, 2.3))


def trunk_body(a):
    """The octagonal planked body: 16 facets (each side split once, the split pushed in or out), rings from the flared
    foot to the flat top, three slits (split vertices pulled in at two rings), a flat bottom, and a flat top with an
    inner octagon ring inset 0.22 and recessed 0.06. Coloured by height and role."""
    bm = a.bm
    rng = random.Random(42400)
    rings = []
    for i, (z, r) in enumerate(TRUNK_RINGS):
        ring = []
        for k in range(16):
            if k % 2 == 1:      # corner at 22.5 + 45 j
                az = 22.5 + 45 * (k // 2)
                rr = r + rng.uniform(-0.03, 0.03)
            else:               # side split at 45 j
                j = k // 2
                az = 45.0 * j + rng.uniform(-3, 3)
                rr = r * math.cos(math.radians(22.5)) + PLANKS[j] + rng.uniform(-0.02, 0.02)
                for col, rs in SLITS:
                    if col == j and i in rs:
                        rr -= 0.14
            ring.append(bm.verts.new(_u(az) * rr + Vector((0, 0, z))))
        rings.append(ring)
    side_f = []
    for i in range(len(rings) - 1):
        for k in range(16):
            j = (k + 1) % 16
            side_f.append(bm.faces.new((rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k])))
    bc = bm.verts.new(Vector((0, 0, TRUNK_RINGS[0][0])))
    bot_f = [bm.faces.new((rings[0][(k + 1) % 16], rings[0][k], bc)) for k in range(16)]
    top_r = TRUNK_RINGS[-1][1]
    inset = [bm.verts.new(_u(22.5 + 45 * k) * (top_r - 0.22) + Vector((0, 0, TRUNK_TOP))) for k in range(8)]
    floor = [bm.verts.new(_u(22.5 + 45 * k) * (top_r - 0.27) + Vector((0, 0, TRUNK_TOP - 0.06))) for k in range(8)]
    tc = bm.verts.new(Vector((0, 0, TRUNK_TOP - 0.06)))
    top_ring = rings[-1]
    top_f = _zip(bm, top_ring, inset)
    rec_f = []
    for k in range(8):
        j = (k + 1) % 8
        rec_f.append(bm.faces.new((inset[k], floor[k], floor[j], inset[j])))
        rec_f.append(bm.faces.new((floor[k], tc, floor[j])))
    vs = [v for r in rings for v in r] + [bc, tc] + inset + floor
    allf = side_f + bot_f + top_f + rec_f
    bmesh.ops.recalc_face_normals(bm, faces=allf)
    a._finish(vs, BARK, tint=1.0)
    for f in side_f:
        z = f.calc_center_median().z
        if z < 1.0:
            f.material_index = a._mi(_mix(BARK, BARK_DEEP, 0.25))
    slit_vs = set()
    for col, rs in SLITS:
        for i in rs:
            slit_vs.add(rings[i][2 * col])
    for f in side_f:
        if sum(1 for v in f.verts if v in slit_vs) >= 2:
            f.material_index = a._mi(_mix(BARK, BARK_DEEP, 0.25))
    _paint(a, top_f, BARK_LIGHT)
    _paint(a, rec_f, _mix(BARK, BARK_LIGHT, 0.5))
    # whole-plank tint: one tone per column of facets, plus broad mottling
    tones = [1.0 + rng.uniform(-0.04, 0.04) for _ in range(16)]
    for i in range(len(rings) - 1):
        for k in range(16):
            _tint(a, [side_f[i * 16 + k]], tones[k])
    _mottle(a, side_f, 0.04, 0.35, 42410)
    return vs


def _root_stations(spec):
    name, az, reach, w, h, nseg, kink, z_top0 = spec
    dk = max(0.55 * reach, 1.95)
    st = [(0.55, z_top0, 1.0 * w, 0.10), (1.55, h, w, 0.09), (dk, 0.64 * h + 0.1, 0.8 * w, 0.08)]
    if nseg >= 3:
        d3 = dk + 0.55 * (reach - dk)
        st.append((d3, 0.42 * h + 0.1, 0.6 * w, 0.08))
    st.append((reach, 0.32, 0.36, 0.08))
    return st, dk


def root(a, spec, rng):
    """One root: a pentagon-section prism (flat bottom on the sand, two shoulders, a top ridge set a little off centre)
    from inside the trunk (the hidden end cap at r 0.55) out to the tip, kinked once in plan (at 0.55 of the reach),
    tapering to a blunt point sunk into the sand. Its ridge rises up the trunk to z_top0. Returns (verts, ridge faces
    on the outer half)."""
    bm = a.bm
    name, az, reach, w, h, nseg, kink, z_top0 = spec
    st, dk = _root_stations(spec)

    def at(d):
        if d <= dk:
            return _u(az) * d, _u(az)
        return _u(az) * dk + _u(az + kink) * (d - dk), _u(az + kink)
    secs = []
    off = rng.uniform(-0.12, 0.12)
    for d, zt, ww, zb in st:
        c, t = at(d)
        s = Vector((-t.y, t.x, 0.0))
        hh = zt - zb
        pts = [c - s * ww / 2 + Vector((0, 0, zb)), c + s * ww / 2 + Vector((0, 0, zb)),
               c + s * ww * 0.42 + Vector((0, 0, zb + 0.55 * hh)), c + s * off * ww + Vector((0, 0, zt)),
               c - s * ww * 0.42 + Vector((0, 0, zb + 0.5 * hh))]
        secs.append([bm.verts.new(p) for p in pts])
    c, t = at(reach + 0.18)
    tip = bm.verts.new(c + Vector((0, 0, 0.09)))
    fs = [bm.faces.new((secs[0][0], secs[0][4], secs[0][3], secs[0][2], secs[0][1]))]
    ridge = []
    for i in range(len(secs) - 1):
        A, B = secs[i], secs[i + 1]
        for k in range(5):
            j = (k + 1) % 5
            f = bm.faces.new((A[k], A[j], B[j], B[k]))
            fs.append(f)
            if k in (2, 3) and st[i][0] >= 0.5 * reach:
                ridge.append(f)
    last = secs[-1]
    fs += [bm.faces.new((last[k], last[(k + 1) % 5], tip)) for k in range(5)]
    bmesh.ops.triangulate(bm, faces=fs, quad_method="BEAUTY", ngon_method="BEAUTY")
    vs = [v for s in secs for v in s] + [tip]
    fs = _faces(vs)
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    a._finish(vs, BARK, tint=1.0)
    for f in fs:
        if f.calc_center_median().z < 0.6:
            f.material_index = a._mi(_mix(BARK, BARK_DEEP, 0.25))
    # the top ridge's outer half (a role: the ridge verts of the stations past half the reach), never by facing
    ridge_vs = {secs[i][3] for i in range(len(secs)) if st[i][0] >= 0.5 * reach}
    ridge = [f for f in fs if any(v in ridge_vs for v in f.verts)]
    _paint(a, ridge, _mix(BARK, BARK_LIGHT, 0.25))
    _mottle(a, fs, 0.04, 0.5, 42450 + int(az))
    return vs


def trunk_part(a):
    """Trunk body first (shell 0, the union's base), then the six roots (each unioned in on its own)."""
    trunk_body(a)
    rng = random.Random(42500)
    for spec in ROOTS:
        root(a, spec, rng)


# ---- root base (spec 2.4) ------------------------------------------------------------------------------------------------
PATCH_TOP, PATCH_EDGE = 0.15, 0.03
ROCKS = {   # name -> centre, (W, D, H), yaw (deg), seed
    "R1": ((-4.6, -0.2), (2.3, 1.9, 1.5), 20.0, 42601),
    "R2": ((-2.75, -3.45), (2.1, 1.8, 1.45), -15.0, 42602),
    "R3": ((4.4, -1.9), (1.6, 1.4, 1.2), 35.0, 42603),
    "R4": ((3.9, 1.5), (1.3, 1.1, 1.0), 10.0, 42604),
    "R5": ((1.6, 4.4), (1.5, 1.3, 1.1), -25.0, 42605),
}
PEBBLES = (((-2.3, -4.35), 0.5, 42611), ((1.75, -4.15), 0.42, 42612), ((-3.6, 2.9), 0.38, 42613))
CLUMPS = {  # name -> centre, leaves, height, spread radius, lime leaves, seed
    "P1": ((-4.3, 1.4), 10, 2.6, 1.5, 2, 42701),
    "P2a": ((2.4, -3.55), 9, 2.8, 1.6, 3, 42702),
    "P2b": ((3.55, -2.55), 7, 2.2, 1.2, 2, 42703),
    "B1": ((3.2, 3.5), 8, 1.6, 1.0, 4, 42704),
    "B2": ((-1.6, 4.2), 8, 2.0, 1.2, 2, 42705),
    "S1": ((-4.0, -2.1), 4, 1.1, 0.55, 2, 42706),
    "S2": ((-1.35, -4.15), 5, 1.15, 0.6, 3, 42707),
    "S3": ((-0.15, -3.95), 4, 1.0, 0.5, 2, 42708),
    "S4": ((-5.5, 3.1), 4, 1.0, 0.5, 2, 42709),     # sprigs at the patch's long ends (the f34's screen left / right)
    "S5": ((5.6, -3.3), 4, 1.1, 0.55, 2, 42710),
}
# rock ring stacks (height fraction, radius fraction, points): a broad base, the widest ring low, a shoulder, a flat
# 5-corner crown (chunky rounded-angular blocks, never eggs)
ROCK_RINGS = ((0.0, 0.9, 6), (0.3, 1.0, 7), (0.72, 0.86, 6), (1.0, 0.45, 5))
SINK_ROCK, SINK_PEB, SINK_HUB = 0.08, 0.04, 0.03


def _patch_outline(n=20):
    """Lobed outline (r per azimuth) of the sand patch: an ellipse 7.2 x 2.8 along 325 / 145 deg (the f34 screen
    axis) with lobes, let out wherever a rock, clump, pebble or root tip needs 0.25 of sand beyond it."""
    rng = random.Random(42600)
    ph = [rng.uniform(0, 6.28) for _ in range(3)]
    items = [(Vector(c), max(s[0], s[1]) / 2) for c, s, _, _ in ROCKS.values()]
    items += [(Vector(c), r) for c, r, _ in PEBBLES]
    items += [(Vector(c), R) for c, _, _, R, _, _ in CLUMPS.values()]
    for spec in ROOTS:
        st, dk = _root_stations(spec)
        d = spec[2] + 0.18
        p = _u(spec[1]) * dk + _u(spec[1] + spec[6]) * (d - dk)
        items.append((p.to_2d(), 0.2))
    out = []
    for k in range(n):
        th = 2 * math.pi * k / n
        rel = th - math.radians(325.0)
        r = 1.0 / math.sqrt((math.cos(rel) / 7.2) ** 2 + (math.sin(rel) / 2.8) ** 2)
        r *= 1.0 + 0.05 * math.sin(5 * th + ph[0]) + 0.035 * math.sin(3 * th + ph[1]) + 0.02 * math.sin(7 * th + ph[2])
        for c, rad in items:
            dist = c.length
            ang = math.atan2(c.y, c.x)
            dth = abs((th - ang + math.pi) % (2 * math.pi) - math.pi)
            half = math.asin(min(1.0, (rad + 0.25) / max(dist, 1e-3)))
            if dth < half + 2 * math.pi / n:
                r = max(r, dist * math.cos(dth) + math.sqrt(max(0.0, (rad + 0.25) ** 2 - (dist * math.sin(dth)) ** 2)) + 0.05)
        out.append(r)
    return out


def _near_field():
    """Distance from a ground point to the nearest trunk foot, root, rock or plant hub (for the sand's deeper band)."""
    segs = []
    for spec in ROOTS:
        st, dk = _root_stations(spec)
        p0 = _u(spec[1]) * 1.5
        p1 = _u(spec[1]) * dk
        p2 = _u(spec[1]) * dk + _u(spec[1] + spec[6]) * (spec[2] + 0.18 - dk)
        segs += [(p0.to_2d(), p1.to_2d(), 0.5 * spec[3]), (p1.to_2d(), p2.to_2d(), 0.3 * spec[3])]
    circles = [(Vector((0, 0)), 1.78)] + [(Vector(c), max(s[0], s[1]) / 2) for c, s, _, _ in ROCKS.values()]
    circles += [(Vector(c), 0.3) for c, *_ in CLUMPS.values()]

    def f(p):
        q = p.to_2d()
        d = min((q - c).length - r for c, r in circles)
        for a_, b_, r in segs:
            ab = b_ - a_
            t = max(0.0, min(1.0, (q - a_).dot(ab) / ab.length_squared))
            d = min(d, (q - (a_ + ab * t)).length - r)
        return d
    return f


def patch(a):
    """The thin lobed sand patch: a flat crest at 0.15 out to 0.5 inside the outline, a bevel down to 0.03 at the
    outline, a short side, a flat underside at z 0. Sand-deep within 0.4 of the trunk, roots, rocks and hubs and on the
    bevel."""
    bm = a.bm
    R = _patch_outline()
    n = len(R)
    ring = lambda f_r, z, dr=0.0: [bm.verts.new(_u(360.0 * k / n) * (R[k] * f_r + dr) + Vector((0, 0, z)))
                                   for k in range(n)]
    c_top = bm.verts.new(Vector((0, 0, PATCH_TOP)))
    r1 = ring(0.5, PATCH_TOP)
    r2 = ring(1.0, PATCH_TOP, -0.5)
    r3 = ring(1.0, 0.0)            # the knife edge: the bevel runs from the crest's rim down to the ground
    c_bot = bm.verts.new(Vector((0, 0, 0)))
    fs = []
    top = [bm.faces.new((r1[k], r1[(k + 1) % n], c_top)) for k in range(n)]
    for A, B in ((r1, r2), (r2, r3)):
        for k in range(n):
            j = (k + 1) % n
            fs.append(bm.faces.new((A[k], B[k], B[j], A[j])))
    bot = [bm.faces.new((r3[(k + 1) % n], r3[k], c_bot)) for k in range(n)]
    bmesh.ops.triangulate(bm, faces=fs, quad_method="BEAUTY")
    vs = [c_top, c_bot] + r1 + r2 + r3
    allf = _faces(vs)
    bmesh.ops.recalc_face_normals(bm, faces=allf)
    a._finish(vs, SAND, tint=1.0)
    near = _near_field()
    for f in allf:
        c = f.calc_center_median()
        if c.z < PATCH_TOP - 1e-3:       # the bevelled edge: a soft, deeper rim (position, as on the sheet)
            f.material_index = a._mi(_mix(SAND, SAND_DEEP, 0.5))
        elif near(c) < 0.4:
            f.material_index = a._mi(_mix(SAND, SAND_DEEP, 0.25))
    _mottle(a, allf, 0.03, 0.15, 42620)
    return vs


def rock(a, name):
    """A chunky rounded-angular rock: the hull of jittered ring stacks (broad base sunk 0.08 into the sand, widest low,
    a shoulder, a flat 5-corner crown). rock base; rock_light on the top 30 %, rock_deep on the lowest 25 %."""
    (cx, cy), (W, D, H), yaw, seed = ROCKS[name]
    return _rock(a, (cx, cy), (W, D, H), yaw, seed, PATCH_TOP - SINK_ROCK)


def _rock(a, c, size, yaw, seed, z0, rings=ROCK_RINGS):
    rng = random.Random(seed)
    W, D, H = size
    pts = m033._ring_pts(rng, rings, W / 2, D / 2, H, 0.07, lean=(rng.uniform(-0.1, 0.1), rng.uniform(-0.1, 0.1)))
    m = Matrix.Rotation(math.radians(yaw), 3, "Z")
    pts = [m @ p + Vector((c[0], c[1], z0)) for p in pts]
    vs = m033._hull(a, pts, ROCK)
    fs = _faces(vs)
    for f in fs:
        h = (f.calc_center_median().z - z0) / H
        if h > 0.72:
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.5))
        elif h > 0.55:
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.25))
        elif h < 0.22:
            f.material_index = a._mi(_mix(ROCK, ROCK_DEEP, 0.25))
    _mottle(a, fs, 0.04, 0.4, seed)
    return vs


PEB_RINGS = ((0.0, 0.92, 5), (0.45, 1.0, 5), (1.0, 0.5, 3))


def pebble(a, c, s, seed):
    return _rock(a, c, (s, s * 0.85, s * 0.6), random.Random(seed).uniform(0, 180), seed, PATCH_TOP - SINK_PEB,
                 rings=PEB_RINGS)


def _leaf8(a, base, yaw, pitch, L, W, curl, key):
    """One closed 8-tri lanceolate leaf folded on its midrib (V channel: the edges raised, a keel beneath): base,
    widest at 0.38 L, a pointed tip that arches out and down by `curl`."""
    bm = a.bm
    cy, sy, cp, sp = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch)
    d = Vector((cy * cp, sy * cp, sp))
    s = Vector((-sy, cy, 0.0))
    n = d.cross(s).normalized()
    B = Vector(base)
    c1 = B + d * (0.38 * L)
    left = c1 - s * W / 2 + n * 0.16 * W
    right = c1 + s * W / 2 + n * 0.16 * W
    mid = c1 + n * 0.02 * W
    keel = c1 - n * 0.12 * W
    T = B + d * L + Vector((cy, sy, 0)) * curl * L * 0.5 - Vector((0, 0, curl * L))
    v = [bm.verts.new(p) for p in (B, left, T, right, mid, keel)]
    eq = [v[0], v[1], v[2], v[3]]
    fs = []
    for i in range(4):
        j = (i + 1) % 4
        fs.append(bm.faces.new((eq[i], eq[j], v[4])))
        fs.append(bm.faces.new((eq[j], eq[i], v[5])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    a._finish(v, key, tint=1.0)
    return v


def clump(a, name):
    """A clump of upright lanceolate leaves (50-78 deg) round a small closed 5-sided hub pyramid sunk 0.03 into the
    sand; each leaf's base sits inside the hub. Taller leaves lime (PLANT), lower ones green (PLANT_DEEP); the lime
    count per clump follows the sheet (P1 and B2 mostly green, sprigs all lime)."""
    (cx, cy), n, H, R, lime, seed = CLUMPS[name]
    rng = random.Random(seed)
    bm = a.bm
    z0 = PATCH_TOP - SINK_HUB
    hr, hh = (0.28, 0.32) if H > 1.2 else (0.18, 0.24)
    yaw0 = rng.uniform(0, 6.28)
    ring = [bm.verts.new(Vector((cx + math.cos(yaw0 + 2 * math.pi * k / 5) * hr,
                                 cy + math.sin(yaw0 + 2 * math.pi * k / 5) * hr, z0))) for k in range(5)]
    apex = bm.verts.new(Vector((cx, cy, z0 + hh)))
    fs = [bm.faces.new((ring[k], ring[(k + 1) % 5], apex)) for k in range(5)]
    fs.append(bm.faces.new(list(reversed(ring))))
    bmesh.ops.triangulate(bm, faces=[fs[-1]])
    hub_vs = ring + [apex]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(hub_vs))
    a._finish(hub_vs, _mix(PLANT_DEEP, BARK_DEEP, 0.25), tint=1.0)
    out = list(hub_vs)
    # leaf heights: alternate tall / short; the `lime` tallest are lime
    hs = []
    for k in range(n):
        tall = (k % 2 == 0)
        hs.append(H * (rng.uniform(0.85, 1.0) if tall else rng.uniform(0.55, 0.75)))
    order = sorted(range(n), key=lambda k: -hs[k])
    lime_set = set(order[:lime])
    for k in range(n):
        yaw = yaw0 + 0.3 + 2 * math.pi * k / n + rng.uniform(-0.25, 0.25)
        tall = hs[k] > 0.8 * H
        pitch = math.radians(rng.uniform(64, 76) if tall else rng.uniform(42, 56))
        L = hs[k] / math.sin(pitch) * 1.25
        W = L * rng.uniform(0.40, 0.46)
        curl = rng.uniform(0.06, 0.12)
        base = (cx + math.cos(yaw) * hr * 0.35, cy + math.sin(yaw) * hr * 0.35, z0 + hh * 0.3)
        key = PLANT if k in lime_set else PLANT_DEEP
        vs = _leaf8(a, base, yaw, pitch, L, W, curl, key)
        lf = _faces(vs)
        # the leaf's base half a step toward the clump's deeper green (position along the leaf)
        _paint(a, [f for f in lf if (f.calc_center_median() - Vector(base)).length < 0.3 * L],
               _mix(key, PLANT_DEEP, 0.25) if key == PLANT else _mix(PLANT_DEEP, BARK_DEEP, 0.0))
        _tint(a, lf, 1.0 + rng.uniform(-0.04, 0.04))
        out += vs
    return out


def root_base_part(a):
    patch(a)
    for name in ROCKS:
        rock(a, name)
    for c, s, seed in PEBBLES:
        pebble(a, c, s, seed)
    for name in CLUMPS:
        clump(a, name)


def hero_rest(a):
    """Everything but the trunk (which is unioned on its own and joined in): root base, then the three tiers."""
    root_base_part(a)
    tier(a, "lower")
    tier(a, "middle")
    tier(a, "crown")


# ---- objects -------------------------------------------------------------------------------------------------------------
NOTES = {
    HERO: "Young Fir: three stacked foliage tiers (crown star cone + 8 hem flaps, middle 12, lower skirt 16 drooping "
          "kite flaps in two rows) seated by contact on flat caps and hubs, an octagonal planked orange-brown trunk "
          "with six kinked roots, on a sand patch with rocks, pebbles and lime / green plant clumps. No VFX",
    CROWN_P: "Crown Tier: star cone (4 + 4 ridges) with a hem of 8 drooping kite flaps, octagonal hub underneath",
    MID_P: "Middle Tier: pleated core with a flat cap and an octagonal hub, 12 kite flaps in two staggered rows",
    LOW_P: "Lower Skirt: pleated core with a flat cap and an octagonal hub, 16 kite flaps in two staggered rows",
    TRUNK_P: "Trunk: octagonal planked trunk with slits and a flat top (inner ring), six kinked angular roots unioned in",
    BASE_P: "Root Base: thin lobed sand patch, 5 chunky warm-grey rocks, 3 pebbles, 8 clumps of upright lanceolate leaves",
}
COLLISION = {HERO: "precise", CROWN_P: "hull", MID_P: "hull", LOW_P: "hull", TRUNK_P: "hull", BASE_P: "precise"}


def _new(name, fn, role, budget):
    """Build fn into a fresh tagged kit object in the model's collection, keeping the build frame (origin at the build
    frame's origin until _post re-centres it)."""
    old = bpy.data.objects.get(name)
    if old:
        if old.get("kit_sheet") not in (None, SHEET):
            raise RuntimeError(f"{name} belongs to {old.get('kit_sheet')}")
        for c in list(old.children_recursive):
            bpy.data.objects.remove(c, do_unlink=True)
        me = old.data
        bpy.data.objects.remove(old, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    a = K.fk().Asset(name, f"{SHEET} {TITLE}", seed=7, tint_var=0.0)
    fn(a)
    o = a.finish(collection=M.coll(NUM, TITLE), mark_asset=True, origin=None)
    K.drop_unused_slots(o)
    if "kit_part" in o.data.attributes:
        o.data.attributes.remove(o.data.attributes["kit_part"])
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


def _make_trunk():
    t0 = time.time()
    o = _new(TRUNK_P, trunk_part, "part", 1000)
    lg = {}
    m033._sane(o)
    lg["unions"] = m033._union_fine(o)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    lg["slivers_forced"] = m012._force_slivers(o, lim=2.0, max_len=0.12)
    lg.update(_post(o))
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


def _make_shells(name, fn, role="part", budget=1000):
    o = _new(name, fn, role, budget)
    return o, _post(o)


def _make_hero(trunk):
    t0 = time.time()
    o = _new(HERO, hero_rest, "hero", 4000)
    c = bpy.data.objects.new(PFX + "trunk", trunk.data.copy())
    o.users_collection[0].objects.link(c)
    c.matrix_world = Matrix.Translation(Vector(trunk[OFF]))
    bpy.context.view_layer.update()
    with M._override(o):
        c.select_set(True)
        with bpy.context.temp_override(selected_objects=[o, c], selected_editable_objects=[o, c]):
            bpy.ops.object.join()
    lg = _post(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


# ---- checks ----------------------------------------------------------------------------------------------------------------
def _keys(o):
    return [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]


def _kind(ks, nf):
    if any("plant" in k for k in ks):
        return "leaf" if nf == 8 else "hub"
    if any("bark" in k for k in ks) and any("needle" in k for k in ks):
        return "core"
    if any("bark" in k for k in ks):
        return "trunk"
    if any("needle" in k for k in ks):
        return "flap"
    if any("sand" in k for k in ks):
        return "patch"
    if any("rock" in k for k in ks):
        return "rock"
    if any("plant" in k for k in ks):
        return "leaf" if nf == 8 else "hub"
    return "other"


def shells_report(o):
    """Per shell: kind, tris, non-manifold edges and verts, boundary edges, self-intersecting face pairs inside the
    shell, signed volume (closed and outward when > 0)."""
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
        out.append({"kind": _kind(ks, len(fs)), "tris": len(fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary), "self_hits": hits,
                    "volume": round(vol, 4), "zmin": round(min(v.co.z for v in vs), 3)})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating dressing (STAGES): per shell, whether it touches another shell (triangles intersect, or a vertex
    within `tol` of another shell's surface) or the ground (z <= tol). Anchors: shells on the ground, and for a tier
    part its core (the shell with the bark hub). Returns the floating count, the worst gap, shells with no chain of
    contact to an anchor, the hub-to-seat gaps and the deepest cut between flaps (two flap shells intersecting)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = _keys(o)
    fsh = [ids[f.index] for f in bm.faces]
    vsh = {}
    for f in bm.faces:
        for v in f.verts:
            vsh[v.index] = fsh[f.index]
    shell_keys = [set() for _ in range(n)]
    nfaces = [0] * n
    for f in bm.faces:
        shell_keys[fsh[f.index]].add(keys[f.material_index])
        nfaces[fsh[f.index]] += 1
    kinds = [_kind(shell_keys[k], nfaces[k]) for k in range(n)]
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
    gap = [1e9] * n
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    if any(kinds[k] == "patch" for k in range(n)):          # the hero / root base: the ground anchors
        ground = {k for k in range(n) if zmin[k] - z0 <= tol}
    else:                                                    # a tier or the trunk alone: its core / trunk anchors
        ground = {k for k in range(n) if kinds[k] in ("core", "trunk")}
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
        return n - len(seen)
    floating = [k for k in range(n) if gap[k] > tol]
    # flap-flap cuts that show: crossing points of two flap shells' triangles outside every core shell
    core_f = [f for f in bm.faces if kinds[fsh[f.index]] == "core"]
    cvi = {}
    for f in core_f:
        for v in f.verts:
            cvi.setdefault(v, len(cvi))
    core_tree = BVHTree.FromPolygons([v.co for v in cvi], [[cvi[v] for v in f.verts] for f in core_f]) if core_f else None
    cut_pairs = set()
    for i, j in tree.overlap(tree):
        a_, b_ = fsh[i], fsh[j]
        if a_ == b_ or kinds[a_] != "flap" or kinds[b_] != "flap" or (min(a_, b_), max(a_, b_)) in cut_pairs:
            continue
        ta = [v.co for v in bm.faces[i].verts]
        tb = [v.co for v in bm.faces[j].verts]
        if any(core_tree is None or not _inside(core_tree, p) for p in _cut_pts(ta, tb)):
            cut_pairs.add((min(a_, b_), max(a_, b_)))
    flap_cuts = len(cut_pairs)
    # hub seats: the gap from each core to whatever is below it (trunk top or the cap below)
    seats = sorted(round(d, 4) for (a_, b_), d in near.items()
                   if {kinds[a_], kinds[b_]} in ({"core"}, {"core", "trunk"}))
    res = {"shells": n, "floating": len(floating),
           "floating_kinds": sorted({kinds[k] for k in floating}),
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "max_gap_all": round(max(gap[k] for k in range(n)), 3),
           "unchained": chained(tol), "unchained_chain_tol": chained(chain_tol),
           "flap_flap_cuts": flap_cuts, "hub_seats": seats,
           "kinds": {k: kinds.count(k) for k in sorted(set(kinds))}}
    bm.free()
    return res


# ---- build -------------------------------------------------------------------------------------------------------------------
PARTS = ((CROWN_P, crown_part), (MID_P, middle_part), (LOW_P, lower_part), (BASE_P, root_base_part))
TARGET_SIZE = ((12.8, 0.8), (12.4, 0.8), (16.0, 0.3))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m042_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", "TieredFir"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build(render=True, parts=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    m033.UNION_RETRIES.clear()
    palette()
    TIER_INFO.clear()
    objs, log = {}, {}
    trunk, log[TRUNK_P] = _make_trunk()
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make_shells(name, fn)
    objs[TRUNK_P] = trunk
    h, log["hero"] = _make_hero(trunk)
    log["tiers"] = {k: dict(v) for k, v in TIER_INFO.items()}
    log["union_retries"] = list(m033.UNION_RETRIES)
    _cleanup_tmp()
    order = [h] + [objs[n] for n in (CROWN_P, MID_P, LOW_P, TRUNK_P, BASE_P) if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    audits = [M.audit(o) for o in order]
    thin = {o.name: m012._thin(o, 2.0) for o in order}
    shells = {o.name: shells_report(o) for o in order}
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
        for i, s in enumerate(shells[o.name]):
            for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "self_hits"):
                if s[k]:
                    problems.append(f"{o.name} shell {i} ({s['kind']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['kind']}): not closed outward (volume {s['volume']})")
    contact = {o.name: contact_report(o) for o in order if o is not trunk}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} shells touch nothing within {CONTACT}, {c['unchained']} have no "
                            f"chain of contact to the ground")
        if c["flap_flap_cuts"]:
            problems.append(f"{n_}: {c['flap_flap_cuts']} flap pairs cut into each other")
    if len(shells[TRUNK_P]) != 1:
        problems.append(f"{TRUNK_P}: {len(shells[TRUNK_P])} shells, expected 1")
    if sum(1 for s in shells[HERO] if s["kind"] == "trunk") != 1:
        problems.append(f"{HERO}: {sum(1 for s in shells[HERO] if s['kind'] == 'trunk')} trunk shells, expected 1")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 12: none)")
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
           "hero_shells": kinds, "contact": contact, "thin": thin, "log": log, "problems": problems, "uv": uv,
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders -----------------------------------------------------------------------------------------------------------------
# decision 10: f34_sheet (-35, 16) governs; r34_sheet (145, 16), front / side / rear_sheet at e 8, kit top and underside;
# floor hidden and a 3x lens on the *_sheet shots (m033._long_lens)
SHEET_VIEWS = {"f34_sheet": (-35, 16), "r34_sheet": (145, 16), "front_sheet": (0, 8), "side_sheet": (90, 8),
               "rear_sheet": (180, 8), "top_sheet": (0, 89)}
PARTS_SHOT = (-30, 20)
EXPLODE_LIFT = {BASE_P: 0.0, TRUNK_P: 2.5, LOW_P: 7.5, MID_P: 10.0, CROWN_P: 12.5}


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded Parts & Assembly: each part at its own place in the tree,
    lifted by cumulative gaps of 2 (root base, trunk, lower skirt, middle tier, crown)."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []
    x0 = objs[0].location.x + 70
    for name, lift in EXPLODE_LIFT.items():
        if name not in by:
            continue
        o = by[name]
        c = bpy.data.objects.new(f"{PFX}expl_{name}", o.data)
        coll.objects.link(c)
        c.matrix_world = Matrix.Translation((x0, objs[0].location.y, lift)) @ Matrix.Translation(Vector(o[OFF]))
        shown.append(c)
    bpy.context.view_layer.update()
    return shown


def _scale_marker(h):
    """A 5.5-stud character stand-in beside the hero, for the scale shot."""
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
    shown = _exploded(objs) if len(objs) > 1 else []
    marker = _scale_marker(h)
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        by = {o.name: o for o in objs}
        for o in objs[1:]:
            extra["part_" + o.name.replace("TieredFir", "").lower()] = ([o], *PARTS_SHOT)
        if MID_P in by:
            extra["tier_under"] = ([by[MID_P]], 0, -35)
        if TRUNK_P in by:
            extra["trunk_cu"] = ([by[TRUNK_P]], -30, 30)
        if shown:
            extra["exploded"] = (shown, 0, 25)
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
            out["root_cu"] = m033.render_close([h], f"{d}/root_cu.png", -25, 15, off @ Vector((0.0, -1.2, 1.3)), 3.4)
        return out
    finally:
        for o in shown + [marker]:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if o is marker and me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def preview(names=("f34_sheet", "front_sheet", "r34_sheet", "top_sheet"), vfx=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig


def hero_only():
    """Rebuild just the trunk and the hero (tuning loop)."""
    M.coll(NUM, TITLE)
    palette()
    TIER_INFO.clear()
    trunk, lt = _make_trunk()
    h, lg = _make_hero(trunk)
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n in (CROWN_P, MID_P, LOW_P, TRUNK_P, BASE_P)
                          if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals")}, "log": lg, "trunk": lt,
            "tiers": {k: dict(v) for k, v in TIER_INFO.items()}}
