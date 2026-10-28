"""019 Resin Node (references/019.png): one fallen, forked branch lying in an X - a thick forked limb (A, lying on the
ground at the front-left, rising steeply from the fork to a pale cut end at the back-right), a second log (B) lying
across it from a low back-left end to a cut end on the ground at the front-right, two short stubs (C to the back,
D to the right) - with two chunky faceted orange resin lumps on it (a large one straddling A at the front-left, a
small one on D at the right), five bright five-leaf clumps tucked into the notches and stub tips, and a thick
faceted cream cut-end insert on every log end.

    import importlib, kit_models, m019; importlib.reload(kit_models); importlib.reload(m019); m019.build()

Parts as on the sheet's Exploded Asset Breakdown, each built by its own function, all in one shared build frame
(studs; front -Y, +X right, ground z = 0, the plan centre of the layout at the origin). R06 owns ResinNode*, so the
names are ResinBranch* (M019_spec.md section 8, main-session decision 10):
- ResinBranchBody (body): Main Branch Body. Six faceted 8-sided log tubes (A_low, A_up, B_back, B_front, stubs C and
  D; `_tube`: jittered, twisted rings along the axis, a flared bark lip and a flat cut face at the end) fused through
  a hull knot at the fork (`_knot`), plus the two hexagonal resin join pads ("Flat Join Surface"). No caps.
- ResinBranchCutEnd (cut_end): Branch Cut End, a thick 10-sided insert with a slightly domed face in two ring bands.
- ResinBranchLumpLarge / ResinBranchLumpSmall: the resin lumps, convex hulls of jittered Fibonacci points with the
  largest faces poked (broad facets split into a few triangles of slightly different tone).
- ResinBranchLeafClump (clump): five broad kite leaves (midrib ridge, keel) radiating from a hidden hub.

The hero (ResinBranchNode) is built from the same builders in the build frame: body + 6 caps + 2 lumps + 5 clumps,
then one guarded exact union of each shell in turn (M.union_loose), a floor cut at the ground, and the sliver
cleanup. Colour (stage 4) is painted by position fields inside the builders, before the union (the union and
cleanup keep each face's key and Tint). See M019_spec.md.
"""
import math
import os
import random

import bmesh
import bpy
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M
import m004
import m012
import m011
import m016

NUM, TITLE, SHEET = 19, "Resin Node", "M019"
OFF = "m019_offset"

BARK, BARK_LIGHT, BARK_DARK = "m019_bark", "m019_bark_light", "m019_bark_dark"
CUT, CUT_RING, JOIN = "m019_cut", "m019_cut_ring", "m019_join"
RESIN, RESIN_LIGHT, RESIN_DARK = "m019_resin", "m019_resin_light", "m019_resin_dark"
LEAF, LEAF_TIP, LEAF_BASE = "m019_leaf", "m019_leaf_tip", "m019_leaf_base"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

BARK_ROUGH, CUT_ROUGH, RESIN_ROUGH, LEAF_ROUGH = 0.9, 0.85, 0.7, 0.8     # resin 0.45 -> 0.7 in round 2 (RESIN_SPEC)
# Specular IOR Level on every resin key. Round 2: 0.2 -> 0.08 and roughness 0.45 -> 0.7: the small lump's upper-left
# facets caught a grazing white reflection that washed them to peach (#FFDE9A, 820 px read as cut wood), where the
# sheet's are yellow-orange (spec 0 renders them #FE8701; 0.08 / 0.7 leaves no washed facet)
RESIN_SPEC = 0.08
# key -> (hex, roughness, low_spec). Stage 4: calibrate() pass 1 on the kit dome against TARGETS (the sheet's
# rendered medians), then pass 2 on the hero renders ("Stage 4" in M019_spec.md).
# Round 2 (verifier findings 4 and 5): bark_light at its dome-calibrated #7A5236 (pass 1 converged at once; the
# lighter bark at the cut ends); cut x 1.14 (B's front end rendered 20 levels dark) and cut_ring at ~40 % of its
# round-1 contrast against cut (the sheet's rings are faint). Bark stays at its round-1 pass-2 value.
PALETTE = {BARK: ("#614129", BARK_ROUGH, False), BARK_LIGHT: ("#7A5236", BARK_ROUGH, False),
           BARK_DARK: ("#462D1D", 0.95, False),
           CUT: ("#E6C192", CUT_ROUGH, False), CUT_RING: ("#D8B384", CUT_ROUGH, False), JOIN: ("#B28A53", 0.8, False),
           RESIN: ("#EC8600", RESIN_ROUGH, False), RESIN_LIGHT: ("#F99A08", RESIN_ROUGH, False),
           RESIN_DARK: ("#E67A02", RESIN_ROUGH, False),
           LEAF: ("#497C14", LEAF_ROUGH, True), LEAF_TIP: ("#6BA51E", LEAF_ROUGH, True),
           LEAF_BASE: ("#447812", LEAF_ROUGH, True)}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    _resin_spec()


def _resin_spec():
    """Specular per family on every m019 material, the mix keys included: the resin keys at RESIN_SPEC, the leaf keys
    at the kit's foliage spec (K.mix_key makes a mix key's material after its colour is set, so a mix of two
    low-spec leaf keys kept flintkit's 0.2 in round 1)."""
    for m in bpy.data.materials:
        spec = RESIN_SPEC if m.name.startswith("FB_m019_resin") else \
            K.FOLIAGE_SPEC if m.name.startswith("FB_m019_leaf") else None
        if spec is not None and m.node_tree:
            b = m.node_tree.nodes.get("Principled BSDF")
            if b and "Specular IOR Level" in b.inputs:
                b.inputs["Specular IOR Level"].default_value = spec
            if b and m.name.startswith("FB_m019_resin"):
                # a resin mix key keeps the roughness it was made with while its colour is unchanged (K.mix_key only
                # resyncs on a colour change): every resin key gets RESIN_ROUGH
                b.inputs["Roughness"].default_value = RESIN_ROUGH
                key = m.name[3:]
                pal = K.fk().KIT_PALETTE
                if key in pal:
                    pal[key] = (pal[key][0], RESIN_ROUGH) + tuple(pal[key][2:])
                if "flintkit_spec" in m:
                    m["flintkit_spec"] = [RESIN_ROUGH] + list(m["flintkit_spec"])[1:]


# calibration targets: the sheet's rendered medians of unshadowed regions (M019_spec.md section 5.4).
# key -> (sRGB, kind)
TARGETS = {BARK: ((0x85, 0x57, 0x3A), "brown"), BARK_LIGHT: ((0x9E, 0x67, 0x43), "brown"),
           BARK_DARK: ((0x5F, 0x3E, 0x2A), "brown"),
           CUT: ((0xF1, 0xC6, 0x8C), "all"), CUT_RING: ((0xE2, 0xB0, 0x74), "all"), JOIN: ((0xE2, 0xA8, 0x62), "all"),
           RESIN: ((0xFC, 0x94, 0x07), "vivid"), RESIN_LIGHT: ((0xFD, 0xAA, 0x14), "vivid"),
           RESIN_DARK: ((0xE2, 0x76, 0x02), "vivid"),
           LEAF: ((0x5C, 0x9E, 0x16), "green"), LEAF_TIP: ((0x72, 0xB4, 0x1C), "green"),
           LEAF_BASE: ((0x4F, 0x91, 0x13), "green")}


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome, the resin keys at RESIN_SPEC every
    round. "all" keys are sampled with the paper/floor dropped (M.sample). Returns {key: (hex, rendered)}."""
    keys = keys or list(TARGETS)
    set0, sample0 = K.set_colour, K.sample

    def set_colour(key, hexcol, **kw):
        set0(key, hexcol, **kw)
        _resin_spec()

    def sample(src, box, kind="green"):
        return M.sample(src, box, "all", paper=(242, 238, 230), tol=14) if kind == "all" else sample0(src, box, kind)
    K.set_colour, K.sample = set_colour, sample
    try:
        for k in keys:
            K.fk().material(k)
        _resin_spec()
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        K.set_colour, K.sample = set0, sample0
        gone = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]
        for m in gone:
            bpy.data.meshes.remove(m)


# ---- colour ladders (stage 4: painted by position inside the builders) ------------------------------------------
STEPS = 3


def _q(t):
    return round(min(1.0, max(0.0, t)) * (STEPS + 1)) / (STEPS + 1)


def _ladder(lo, mid, hi):
    """lo, three lo->mid mixes, mid, three mid->hi mixes, hi (9 keys)."""
    return ([lo] + [K.mix_key(lo, mid, t) for t in (0.25, 0.5, 0.75)] + [mid] +
            [K.mix_key(mid, hi, t) for t in (0.25, 0.5, 0.75)] + [hi])


def _pick(lad, v, low, high):
    """The ladder key for value v: lo below low[0], blended across low to mid, mid, blended across high to hi."""
    if v < (low[1] + high[0]) / 2:
        return lad[round(_q((v - low[0]) / (low[1] - low[0])) * 4)]
    return lad[4 + round(_q((v - high[0]) / (high[1] - high[0])) * 4)]


def _mottle(a, faces, amp, scale, seed, jitter=0.0):
    """K.texture over a face list: broad Tint patches about 1/scale studs across (never per-triangle confetti)."""
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in faces:
        k = 1.0 + amp * 1.6 * noise.noise(f.calc_center_median() * scale + off) + \
            (rng.uniform(-jitter, jitter) if jitter else 0.0)
        for l in f.loops:
            t = l[a.tint_layer][0] * k
            l[a.tint_layer] = (t, t, t, 1.0)


# ---- geometry helpers -----------------------------------------------------------------------------------------------
def _perp(t):
    a = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
    return (a - t * a.dot(t)).normalized()


def _strip(bm, r0, r1):
    n = len(r0)
    return [bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k])) for k in range(n)]


def _fan(bm, ring, c, flip=False):
    n = len(ring)
    return [bm.faces.new((ring[(k + 1) % n], ring[k], c) if not flip else (ring[k], ring[(k + 1) % n], c))
            for k in range(n)]


def _tri(bm, faces):
    bmesh.ops.triangulate(bm, faces=[f for f in faces if f.is_valid and len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")


def _faces(verts):
    return K.faces_of([v for v in verts if v.is_valid])


def _align(z_axis, yaw=0.0):
    """3x3 rotation taking local +Z to z_axis, turned yaw degrees about it."""
    z = Vector(z_axis).normalized()
    return z.to_track_quat("Z", "Y").to_matrix() @ Matrix.Rotation(math.radians(yaw), 3, "Z")


# ---- logs -----------------------------------------------------------------------------------------------------------
SIDES = 8
FLARE = 1.06        # the last ring (the bark lip) is this much wider than the log there
LIP = 0.82          # the end face's inner ring (cut wood inside, bark lip outside), as a fraction of the lip ring


def _stations(path, rings):
    """Ring stations along a polyline: `rings` points at even arc-length fractions, the one nearest each interior
    path vertex (an elbow) snapped onto it. Returns [(point, tangent, fraction)]."""
    P = [Vector(p) for p in path]
    segs = [(P[i + 1] - P[i]).length for i in range(len(P) - 1)]
    tot = sum(segs)
    acc = [0.0]
    for x in segs:
        acc.append(acc[-1] + x)
    fr = [i / (rings - 1) for i in range(rings)]
    elbows = {}
    for j in range(1, len(P) - 1):
        k = min(range(1, rings - 1), key=lambda i: abs(fr[i] - acc[j] / tot))
        fr[k] = acc[j] / tot
        elbows[k] = j
    out = []
    for i, f in enumerate(fr):
        if i in elbows:
            j = elbows[i]
            t = ((P[j] - P[j - 1]).normalized() + (P[j + 1] - P[j]).normalized()).normalized()
            out.append((P[j].copy(), t, f))
            continue
        d = f * tot
        j = next((q for q in range(len(segs)) if d <= acc[q + 1] + 1e-9), len(segs) - 1)
        u = (d - acc[j]) / segs[j]
        out.append((P[j].lerp(P[j + 1], u), (P[j + 1] - P[j]).normalized(), f))
    return out


def _tube(a, path, r0, r1, rings, seed, end_n=None, sides=SIDES, twist=10.0, rjit=0.07, vjit=0.06, ajit=0.1,
          wobble=0.05, start_back=0.15, info=None, name=None, end_clear=None):
    """One closed faceted log along a polyline path: `rings` 8-sided rings (parallel-transported frames) from the
    path's start (buried end: a fan pushed back along the axis) to its end (the cut end: flared bark lip, flat end
    face perpendicular to the last segment, or to end_n for an oblique cut). Each ring is turned (+-twist deg) and
    scaled (+-rjit), each vertex jittered (vjit radial, ajit along the axis), the inner rings wobble off the axis a
    little, so the bark facets come out as long irregular triangles. The end face is an inner fan (cut wood) inside
    an annulus (bark lip). Returns verts."""
    rng = random.Random(seed)
    bm = a.bm
    st = _stations(path, rings)
    P0, P1 = st[0][0], st[-1][0]
    t0, t1 = st[0][1], st[-1][1]
    en = Vector(end_n).normalized() if end_n else t1
    if end_clear and len(path) == 2:
        # a steep oblique cut reaches back along the axis by r tan(angle) on its low side: pull the inner rings back
        # (evenly, on the straight path) so the ring before the end clears the cut's low side by end_clear x that
        cosa = max(0.2, abs(en.dot(t1)))
        pull = r1 * FLARE * 1.08 * math.sqrt(1 - cosa * cosa) / cosa
        tot0 = (P1 - P0).length
        fmax = 1 - pull * end_clear / tot0
        f_last = st[-2][2]
        if f_last > fmax:
            k_ = fmax / f_last
            st = [st[0]] + [(P0.lerp(P1, f * k_), t, f * k_) for (_, t, f) in st[1:-1]] + [st[-1]]
    phase = rng.uniform(0, 2 * math.pi)
    tot = sum((Vector(path[i + 1]) - Vector(path[i])).length for i in range(len(path) - 1))
    seg = tot / (rings - 1)
    rr = []
    n = _perp(t0)
    prev_t = t0
    for i, (c, t, f) in enumerate(st):
        n = prev_t.rotation_difference(t) @ n
        n = (n - t * n.dot(t)).normalized()
        prev_t = t
        b = t.cross(n)
        inner = 0 < i < rings - 1
        if inner:
            c = c + (n * rng.uniform(-1, 1) + b * rng.uniform(-1, 1)) * wobble
        r = r0 + (r1 - r0) * f
        sc = 1.0 + rng.uniform(-rjit, rjit) if inner else (FLARE if i == rings - 1 else 1.0)
        tw = phase + math.radians(rng.uniform(-twist, twist))
        ring = []
        for k in range(sides):
            th = tw + 2 * math.pi * k / sides
            q = c + (n * math.cos(th) + b * math.sin(th)) * r * sc * (1 + rng.uniform(-vjit, vjit))
            if inner:
                q = q + t * rng.uniform(-ajit, ajit) * seg
            if i == rings - 1:
                q = q + t * ((P1 - q).dot(en) / t.dot(en))      # onto the end plane
            ring.append(bm.verts.new(q))
        rr.append(ring)
    n_end = n
    faces = []
    for r0_, r1_ in zip(rr, rr[1:]):
        faces += _strip(bm, r0_, r1_)
    c0 = bm.verts.new(P0 - t0 * start_back)
    faces += _fan(bm, rr[0], c0, flip=True)
    inner_ring = [bm.verts.new(P1 + (v.co - P1) * LIP) for v in rr[-1]]
    faces += _strip(bm, rr[-1], inner_ring)
    ce = bm.verts.new(P1)
    faces += _fan(bm, inner_ring, ce)
    _tri(bm, faces)
    verts = [v for r in rr for v in r] + [c0, ce] + inner_ring
    a._finish(verts, BARK)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(verts))
    ci = a._mi(CUT)
    cs = set(inner_ring) | {ce}
    for f in _faces(verts):
        if all(v in cs for v in f.verts):
            f.material_index = ci
    if info is not None:
        info.setdefault("ends", {})[name] = {"centre": tuple(P1), "normal": tuple(en), "radius": r1, "axis": tuple(t1),
                                             "u": tuple(n_end), "phase": phase}
    return verts


# Layout (M019_spec.md section 2.1; build frame, studs). Each piece: (path from the buried start to the cut end,
# diameter from, diameter to, rings, seed). A and B are built as four arms out of the fork J, fused through the knot;
# C rises from J's back, D from B. A_up is straight (see A_UP).
# LAYOUT_SX: every layout point's x is scaled by this (log paths, the fork, the lumps' and clumps' centres; not the
# radii), which narrows the X to the sheet's proportions in both the front34 (W : H) and the top (W : D) without
# squashing any round part
LAYOUT_SX = 0.91


def _sx(p):
    return (p[0] * LAYOUT_SX, p[1], p[2])


J = _sx((-0.42, 0.06, 0.74))
CAM34 = Vector((-0.459, -0.864, 0.208))     # toward the front34 camera (azimuth -28, elevation 12)
# A_up (round 2, verifier finding 1): a STRAIGHT log from J to A_UP["aim"] (the cut end's centre, before LAYOUT_SX).
# Round 1's elbow read as a hooked horn with no cut end from the side, rear and rear34. The cut face's normal is
# tilted A_UP["tilt"] = (deg off straight up, toward camera azimuth deg; 0 = the front, -28 = the front34 camera):
# 20 deg toward the front shows a big disc to the front34 camera (the sheet's face-on top end), a thin face to the
# side camera, and keeps the top flat from every side. The ~57 deg slice on a 47 deg log reaches back along the axis,
# so the ring before it is pulled back (END_CLEAR). The insert on this end is thicker with a deeper rim chamfer
# (CAP_PROUD_END / CAP_BEVEL_END), so a cream rim shows from the rear and rear34 too, where the face turns away.
# Tested and rejected (renders in M019_spec.md, round 2): up + 30 % toward the axis (a 300 px sliver of a disc in
# front34), 12-15 deg toward the front34 camera (passes, but a sharper blade from the side), 54 deg off the axis
# straight at the camera (the face hides from the rear entirely).
A_UP = dict(aim=(3.1, 1.75, 4.1), tilt=(20.0, 0.0))


def _a_up_path():
    Jv, E0 = Vector(J), Vector(_sx(A_UP["aim"]))
    th, az = (math.radians(x) for x in A_UP["tilt"])
    nt = Vector((math.sin(az) * math.sin(th), -math.cos(az) * math.sin(th), math.cos(th)))
    return [Jv, E0], nt


LOGS = {
    "A_low": ([J, (-2.70, -0.45, 0.62)], 1.55, 1.42, 4, 19001),
    "A_up": (_a_up_path()[0], 1.50, 1.38, 6, 19002),     # round 2: thicker end (the sheet's top disc is 0.146 W)
    # round 2 (verifier finding 6): B_back 0.3 shorter and D 0.25 further back, so the front34 shows fewer stick ends
    "B_back": ([J, (-2.60, 2.48, 1.02)], 1.34, 1.26, 4, 19003),
    "B_front": ([J, (2.21, -2.52, 0.62)], 1.40, 1.30, 5, 19004),
    "C": ([(-0.72, 0.42, 0.90), (-0.85, 2.3, 2.35)], 0.96, 0.84, 3, 19005),
    "D": ([(0.74, -0.85, 0.72), (2.85, 0.25, 3.25)], 0.86, 0.76, 4, 19006),
}
for _k, _v in LOGS.items():
    if _k != "A_up":        # A_up's path is built from the scaled J and aim
        LOGS[_k] = ([_sx(q) if q is not J else q for q in _v[0]],) + tuple(_v[1:])
END_CLEAR = {"A_up": 1.3}     # the ring before A_up's steep oblique cut sits behind the cut's low side (x this)
B_BACK_TILT = 30.0      # B's back end: the cut face's normal tilted this far up from the axis (spec section 3.2)


def _ends(name):
    p = LOGS[name][0]
    return Vector(p[0]), Vector(p[-1])


def _dir0(name):
    p = LOGS[name][0]
    return (Vector(p[1]) - Vector(p[0])).normalized()


def _end_normal(name):
    p0, p1 = _ends(name)
    d = (p1 - p0).normalized()
    if name == "B_back":
        up = (Vector((0, 0, 1)) - d * d.z).normalized()
        a = math.radians(B_BACK_TILT)
        return tuple(d * math.cos(a) + up * math.sin(a))
    if name == "A_up":
        return tuple(_a_up_path()[1])
    if name in END_TURN:
        yaw, pitch = END_TURN[name]
        h = Matrix.Rotation(math.radians(yaw), 3, "Z") @ d
        side = Vector((0, 0, 1)).cross(h).normalized()
        return tuple((Matrix.Rotation(math.radians(pitch), 3, side) @ h).normalized())
    return None


# oblique cuts that turn an end face (yaw about Z, then pitch, degrees) toward or away from the front34 camera: the
# sheet hides A_low's end under the large lump and shows B's front end nearly face-on
# round 2: B_front -38 -> -30 (its disc was 0.157 x 0.247 of the front34 against the sheet's 0.132 x 0.204)
# verifier round 2: A_low -45 -> -15, its acute end lip read as a bark spike under the large lump in front34
END_TURN = {"A_low": (-15.0, 0.0), "B_front": (-30.0, 0.0)}


KNOT = dict(dist=0.38, scale=0.97, merge=4.0, seed=19011, low=0.02)


def _knot(a):
    """The fork's crotch filler: the convex hull of each arm's ring KNOT['dist'] out of J (7 points at the arm's
    radius), plus two points under J at the ground, so the bark runs from arm to arm over broad facets with no
    cylinder-through-cylinder seam (spec section 1.3, Branch Junction close-up)."""
    rng = random.Random(KNOT["seed"])
    bm = a.bm
    Jv = Vector(J)
    pts = []
    for name in ("A_low", "A_up", "B_back", "B_front", "C"):
        d0 = LOGS[name][1]
        p0 = _ends(name)[0]
        t = _dir0(name)
        c = p0 + t * KNOT["dist"] if name != "C" else p0 + t * 0.2
        n = _perp(t)
        b = t.cross(n)
        ph = rng.uniform(0, 6.3)
        for k in range(7):
            th = ph + 2 * math.pi * k / 7
            pts.append(c + (n * math.cos(th) + b * math.sin(th)) * d0 / 2 * KNOT["scale"] * rng.uniform(0.95, 1.03))
    for dx, dy in ((0.35, -0.3), (-0.35, 0.3)):
        pts.append(Vector((Jv.x + dx, Jv.y + dy, KNOT["low"])))
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    for v in vs:
        if v.is_valid and not v.link_faces:
            bm.verts.remove(v)
    vs = [v for v in vs if v.is_valid]
    fs = _faces(vs)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(KNOT["merge"]), verts=vs,
                             edges=list({e for f in fs for e in f.edges}))
    vs = [v for v in vs if v.is_valid]
    _tri(bm, _faces(vs))
    a._finish(vs, BARK)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    return vs


# resin join pads ("Flat Join Surface"): (log, along-axis fraction, direction from the axis (build frame), radius,
# proud of the bark, seed)
# (log, its lump, how far the pad's axis leans from "straight at the lump" toward PAD_LEAN, radius, proud, seed).
# The pad sits where its lump meets the log (the nearest axis point to the lump's centre); leaning it front-down a
# little lets its rim show under the lump's front-bottom and from below, as the underside close-up.
# Round 2 (verifier finding 2): the large pad leans only 15 % (45 % stuck a tan corner out past the lump's silhouette
# in front34); the small pad stands 0.05 prouder. Both lumps straddle their logs (the large lump's centre is 0.80
# from A_low's axis, the small one's 0.27 from D's), so a pad aimed at the lump ends wholly inside it: neither shows
# in the hero now (no tan shard in front34, no block from below). Tested: a 0.7-radius block leaning 85 % to the
# front-left showed a big tan hexagon under the large lump in front34, where the sheet shows none; leans of 0.3-0.4
# stay hidden and 0.45 pokes a corner out. The Body part keeps both pads (the sheet's "Flat Join Surface").
PADS = {"large": ("A_low", "large", 0.15, 0.62, 0.2, 19021),
        "small": ("D", "small", 0.5, 0.45, 0.23, 19022)}
PAD_LEAN = (0.0, -0.35, -1.0)


def _pad_frame(name):
    log, lump, lean, r, proud, seed = PADS[name]
    (p0, p1), d0, d1 = _ends(log), LOGS[log][1], LOGS[log][2]
    t = (p1 - p0).normalized()
    lc = Vector(LUMPS[lump][0])
    s = max(0.15, min(0.95, (lc - p0).dot(t) / (p1 - p0).length))
    c = p0.lerp(p1, s)
    n = (lc - c)
    n = (n - t * n.dot(t)).normalized()
    n = n.lerp(Vector(PAD_LEAN).normalized(), lean)
    n = (n - t * n.dot(t)).normalized()
    rl = (d0 + (d1 - d0) * s) / 2
    return c, n, rl


def _pad(a, name):
    """A 6-sided prism standing `proud` off the bark along its direction, its foot 0.15 inside the log."""
    log, lump, lean, r, proud, seed = PADS[name]
    rng = random.Random(seed)
    c, n, rl = _pad_frame(name)
    R = _align(n, rng.uniform(0, 60))
    bm = a.bm
    rings = []
    for z, sc in ((rl - 0.3, 1.0), (rl + proud, 0.96)):
        rings.append([bm.verts.new(c + R @ Vector((math.cos(math.radians(60 * k)) * r * sc * rng.uniform(0.96, 1.04),
                                                      math.sin(math.radians(60 * k)) * r * sc * rng.uniform(0.96, 1.04),
                                                      z))) for k in range(6)])
    cb = bm.verts.new(c + n * (rl - 0.3))
    ct = bm.verts.new(c + n * (rl + proud + 0.01))
    fs = _strip(bm, rings[0], rings[1]) + _fan(bm, rings[0], cb, flip=True) + _fan(bm, rings[1], ct)
    _tri(bm, fs)
    vs = rings[0] + rings[1] + [cb, ct]
    a._finish(vs, JOIN)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    return vs


def pad_top(name):
    log, lump, lean, r, proud, seed = PADS[name]
    c, n, rl = _pad_frame(name)
    return c + n * (rl + proud), n


# bark colour fields (spec section 5.5)
# Round 2 (verifier finding 5): `near` is now measured along the log axis back from the end plane (round 1 measured
# the straight distance to the end's centre, which no bark face is within 0.55 of on a 1.3-stud log, so there was no
# lift at all); full bark_light at the lip, fading out over `near`.
BARK_FIELD = dict(near=1.0, near_mix=0.75, ground=0.15, ground_mix=0.3, pad=0.25, pad_mix=0.25,
                  patch_scale=0.6, patch_level=0.3, patch_mix=0.35, seed=19031)
BARK_MOTTLE = dict(amp=0.05, scale=0.4, seed=19032, jitter=0.01)


def _paint_bark(a, verts, info):
    """Bark keys by position: lighter within BARK_FIELD['near'] of each cut end (the Wood (Inner) lip leading into
    the cream disc), broad lighter noise patches, darker at the ground contact and round the pads' feet. Then broad
    Tint mottling."""
    nf = K.noise_field(scale=BARK_FIELD["patch_scale"], seed=BARK_FIELD["seed"])
    ends = [(Vector(e["centre"]), Vector(e["normal"]).normalized(), Vector(e["axis"]).normalized(), e["radius"])
            for e in info["ends"].values()]
    pads = [pad_top(k)[0] for k in PADS]
    bark = [f for f in _faces(verts) if a.bm and f.material_index == a._mi(BARK)]

    def end_dist(c):
        # distance back along each log's axis from its (possibly oblique) end plane, for faces on that log's skin
        best = 99.0
        for P, n, t, r in ends:
            d = (P - c).dot(n) / max(0.2, t.dot(n))
            side = ((c - P) + t * d).length
            if -0.1 < d and side < r * 2.0:
                best = min(best, max(0.0, d))
        return best
    for f in bark:
        c = f.calc_center_median()
        dn = end_dist(c)
        dp = min((c - p).length for p in pads)
        td = 0.0
        if c.z < BARK_FIELD["ground"]:
            td = BARK_FIELD["ground_mix"]
        if dp < BARK_FIELD["pad"]:
            td = max(td, BARK_FIELD["pad_mix"])
        if td:
            f.material_index = a._mi(K.mix_key(BARK, BARK_DARK, _q(td)))
            continue
        tl = BARK_FIELD["near_mix"] * max(0.0, 1 - dn / BARK_FIELD["near"]) * 1.5
        if nf(c) > BARK_FIELD["patch_level"]:
            tl = max(tl, BARK_FIELD["patch_mix"])
        tl = min(tl, BARK_FIELD["near_mix"])
        if _q(tl):
            f.material_index = a._mi(K.mix_key(BARK, BARK_LIGHT, _q(tl)))
    _mottle(a, _faces(verts), BARK_MOTTLE["amp"], BARK_MOTTLE["scale"], BARK_MOTTLE["seed"], BARK_MOTTLE["jitter"])


BODY_INFO = {}


def body(a):
    """Main Branch Body: the six logs, the knot and the two join pads (no caps; the end faces are cut wood)."""
    BODY_INFO.clear()
    vs = []
    for name, (path, d0, d1, rings, seed) in LOGS.items():
        vs += _tube(a, path, d0 / 2, d1 / 2, rings, seed, end_n=_end_normal(name), info=BODY_INFO, name=name,
                    end_clear=END_CLEAR.get(name))
    vs += _knot(a)
    for k in PADS:
        vs += _pad(a, k)
    _paint_bark(a, vs, BODY_INFO)
    return vs


def body_info():
    if not BODY_INFO:
        probe = K.fk().Asset("_m019_probe", "probe")
        body(probe)
        probe.bm.free()
    return BODY_INFO


# ---- cut-end insert ---------------------------------------------------------------------------------------------------
CAP_SIDES = 10
CAP_RINGS = (0.22, 0.38, 0.62, 0.78, 1.0)      # face loops (fractions of R): centre fan + 4 bands = 2 ring bands
CAP_BANDS = (CUT, CUT_RING, CUT, CUT_RING, CUT)   # the centre fan, then each band out to the rim
CAP_PROUD, CAP_SINK, CAP_DOME, CAP_BEVEL = 0.08, 0.12, 0.03, 0.025    # fractions of the disc's diameter
CAP_R = 0.86         # the insert's radius, as a fraction of the log's radius at its end (inside the flared lip)
CAP_MOTTLE = dict(amp=0.03, scale=0.9, seed=19041)


CAP_PROUD_END = {"A_up": 0.18}   # per log end: a thicker insert (fraction of D); the sheet shows A's rim from all sides
CAP_BEVEL_END = {"A_up": 0.10}   # per log end: a deeper chamfer to the rim (fraction of D), so the rim faces sideways


def _cap(a, centre, normal, R, seed, axis=None, u=None, phase=None, proud=None, bevel=None):
    """Branch Cut End: a thick 10-sided insert on a log end. Its outline is the log's cross-section (radius R
    perpendicular to the log axis) projected along the axis onto the end plane (normal), so on an oblique cut it is
    the same ellipse as the end face. Its face stands CAP_PROUD x D off the end plane with a low dome in loops at
    CAP_RINGS (real ring edges) and a slight bevel to the rim; its side band runs back along the log axis
    CAP_SINK x D into the log. Painted cut / ring bands by loop (spec section 5.5). Returns verts."""
    rng = random.Random(seed)
    bm = a.bm
    D = 2 * R
    C = Vector(centre)
    n = Vector(normal).normalized()
    t = Vector(axis).normalized() if axis else n
    uu = Vector(u) if u else _perp(t)
    uu = (uu - t * uu.dot(t)).normalized()
    w = t.cross(uu)
    ph = rng.uniform(0, 2 * math.pi) if phase is None else phase + math.pi / CAP_SIDES
    rj = [rng.uniform(0.97, 1.03) for _ in range(CAP_SIDES)]
    zf = (CAP_PROUD if proud is None else proud) * D
    bv = CAP_BEVEL if bevel is None else bevel

    def on_face(fr, k, jit):
        th = ph + 2 * math.pi * k / CAP_SIDES
        q = C + (uu * math.cos(th) + w * math.sin(th)) * R * fr * rj[k] * jit
        return q + t * ((C - q).dot(n) / t.dot(n))
    loops = []
    for fr in CAP_RINGS:
        z = zf + CAP_DOME * D * (1 - fr * fr) if fr < 1 else zf - bv * D
        loops.append([bm.verts.new(on_face(fr, k, 1 + (rng.uniform(-0.02, 0.02) if fr < 1 else 0.0)) + n * z)
                      for k in range(CAP_SIDES)])
    back = [bm.verts.new(on_face(1.0, k, 1.0) - t * CAP_SINK * D) for k in range(CAP_SIDES)]
    top = bm.verts.new(C + n * (zf + CAP_DOME * D))
    bc = bm.verts.new(C - t * CAP_SINK * D)
    bands = [_fan(bm, loops[0], top)]
    for l0, l1 in zip(loops, loops[1:]):
        bands.append(_strip(bm, l1, l0))
    side = _strip(bm, back, loops[-1])
    bot = _fan(bm, back, bc, flip=True)
    side_key = K.mix_key(CUT, CUT_RING, 0.25)
    groups = [(g, CAP_BANDS[i]) for i, g in enumerate(bands)] + [(side, side_key), (bot, CUT)]
    vs = [v for l in loops for v in l] + back + [top, bc]
    a._finish(vs, CUT)
    for g, key in groups:
        mi = a._mi(key)
        for f in g:
            f.material_index = mi
    _tri(bm, [f for g, _ in groups for f in g])
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    _mottle(a, _faces(vs), CAP_MOTTLE["amp"], CAP_MOTTLE["scale"], CAP_MOTTLE["seed"] + seed)
    return vs


def caps(a):
    """The six cut-end inserts on the log ends (hero only)."""
    out = []
    for i, (name, e) in enumerate(body_info()["ends"].items()):
        out += _cap(a, e["centre"], e["normal"], e["radius"] * CAP_R, 19050 + i, axis=e["axis"], u=e["u"],
                    phase=e["phase"], proud=CAP_PROUD_END.get(name), bevel=CAP_BEVEL_END.get(name))
    return out


PART_CAP_R = 0.53       # the part: the B front end's insert (log diameter 1.06)


def cut_end(a):
    """ResinBranchCutEnd: one insert standing on its back, face up."""
    _cap(a, (0, 0, CAP_SINK * 2 * PART_CAP_R), (0, 0, 1), PART_CAP_R, 19059)


# ---- resin lumps --------------------------------------------------------------------------------------------------------
# (centre, radius, squash (x, y, z), points, pokes, seed, yaw)
LUMPS = {"large": ((-2.2, -0.35, 1.45), 1.32, (1.0, 0.95, 0.93), 16, 10, 19061, 0.0),
         "small": ((2.10, -0.45, 2.15), 1.0, (0.92, 0.97, 0.97), 13, 8, 19062, 25.0)}   # round 2: x 1.0 -> 0.92
LUMPS = {k: (_sx(v[0]),) + tuple(v[1:]) for k, v in LUMPS.items()}
LUMP_FIT = 0.85         # plane distance / radius: the dual solid's corners stand out past its planes
LUMP_JIT = dict(radius=0.06, angle=0.16, poke=0.025)
RESIN_BANDS = ((0.18, 0.42), (0.58, 0.82))      # dark -> mid across the first, mid -> light across the second
RESIN_NOISE = dict(amp=0.06, scale=0.8, seed=19063)
RESIN_MOTTLE = dict(amp=0.025, scale=0.7, seed=19064)


def _dual_hull(planes):
    """Intersection of half-spaces n . x <= h (h > 0, origin inside), as (verts, polygons): the polar dual of the
    convex hull of the points n / h. Each hull triangle is one corner of the solid; each hull vertex one face, its
    corners in order round it. Redundant planes (points inside the hull) drop out."""
    tmp = bmesh.new()
    qs = [tmp.verts.new(Vector(nv) / h) for nv, h in planes]
    bmesh.ops.convex_hull(tmp, input=qs)
    bmesh.ops.recalc_face_normals(tmp, faces=tmp.faces)
    corner = {}
    for f in tmp.faces:
        # the plane through the triangle's three dual points q: q . x = 1 for x = the corner
        a_, b_, c_ = (v.co for v in f.verts)
        nrm = (b_ - a_).cross(c_ - a_)
        corner[f] = nrm / nrm.dot(a_)
    polys = []
    for v in tmp.verts:
        if not v.link_faces:
            continue
        d = v.co.normalized()
        e1 = _perp(d)
        e2 = d.cross(e1)
        cs = sorted(v.link_faces, key=lambda f: math.atan2(corner[f].dot(e2), corner[f].dot(e1)))
        polys.append(cs)
    faces = list(tmp.faces)
    idx = {f: i for i, f in enumerate(faces)}
    out = ([corner[f].copy() for f in faces], [[idx[f] for f in p] for p in polys])
    tmp.free()
    return out


def _lump(a, centre, radius, squash, n, pokes, seed, yaw=0.0, top_cap=8, tint=1.0):
    """A chunky resin nodule: the solid bounded by n planes tangent to a jittered Fibonacci sphere (radius +-6 %),
    squashed - so its faces are broad irregular pentagons and hexagons, as the sheet's (not a hull of points, which
    reads as a jewel of similar triangles) - then the `pokes` largest faces poked with a slightly raised centre (the
    sheet's subtle splits of each broad facet into triangles of slightly different tone). Painted dark -> mid ->
    light by height within the lump (paint, not light: the sheet's bottom third stays red-orange even where lit).
    Returns verts."""
    rng = random.Random(seed)
    bm = a.bm
    C = Vector(centre)
    rot = Matrix.Rotation(math.radians(yaw), 3, "Z")
    planes = []
    ga = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n
        rr = math.sqrt(max(0.0, 1 - z * z))
        th = ga * i + rng.uniform(-LUMP_JIT["angle"], LUMP_JIT["angle"]) * 2
        d = Vector((math.cos(th) * rr, math.sin(th) * rr, z + rng.uniform(-1, 1) * LUMP_JIT["angle"] * 0.5))
        planes.append((d.normalized(), radius * LUMP_FIT * (1 + rng.uniform(-LUMP_JIT["radius"], LUMP_JIT["radius"]))))
    co, polys = _dual_hull(planes)
    sq = Matrix.Diagonal(Vector(squash))
    vs = [bm.verts.new(C + rot @ (sq @ p)) for p in co]
    fs = [bm.faces.new([vs[i] for i in p]) for p in polys]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    bmesh.ops.remove_doubles(bm, verts=vs, dist=radius * 0.04)
    vs = [v for v in vs if v.is_valid]
    bmesh.ops.dissolve_degenerate(bm, edges=list({e for f in _faces(vs) for e in f.edges}), dist=radius * 0.01)
    vs = [v for v in vs if v.is_valid]
    big = sorted(_faces(vs), key=lambda f: -f.calc_area())[:pokes]
    res = bmesh.ops.poke(bm, faces=big, offset=radius * LUMP_JIT["poke"])
    vs = vs + list(res["verts"])
    _tri(bm, _faces(vs))
    a._finish(vs, RESIN)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    lad = _ladder(RESIN_DARK, RESIN, RESIN_LIGHT)
    nf = K.noise_field(scale=RESIN_NOISE["scale"], seed=RESIN_NOISE["seed"] + seed)
    zs = [v.co.z for v in vs]
    z0, z1 = min(zs), max(zs)
    for f in _faces(vs):
        c = f.calc_center_median()
        h = (c.z - z0) / (z1 - z0) + RESIN_NOISE["amp"] * nf(c) / 0.6
        k_ = _pick(lad, h, RESIN_BANDS[0], RESIN_BANDS[1])
        f.material_index = a._mi(lad[min(lad.index(k_), top_cap)])
    _mottle(a, _faces(vs), RESIN_MOTTLE["amp"], RESIN_MOTTLE["scale"], RESIN_MOTTLE["seed"] + seed)
    if tint != 1.0:
        for f in _faces(vs):
            for l in f.loops:
                t = l[a.tint_layer][0] * tint
                l[a.tint_layer] = (t, t, t, 1.0)
    return vs


# Round 2 (verifier finding 3): the small lump sits high in the key light and its light top washed to pale cream; its
# top band stops at the mid -> light 50 % mix (ladder index 6; the sheet's top third is #FD9F07)
LUMP_TOP = {"large": 8, "small": 6}
# and the whole small lump renders brighter than the large one (it sits high, open to the key light; the sheet draws
# both lumps at the same tones): a uniform Tint factor on the small lump (the same on its part)
LUMP_TINT = {"large": 1.0, "small": 0.78}


def lumps(a):
    out = []
    for k, (c, r, sq, n, pk, seed, yaw) in LUMPS.items():
        out += _lump(a, c, r, sq, n, pk, seed, yaw, top_cap=LUMP_TOP[k], tint=LUMP_TINT[k])
    return out


def lump_large(a):
    c, r, sq, n, pk, seed, yaw = LUMPS["large"]
    _lump(a, (0, 0, r * sq[2]), r, sq, n, pk, seed, yaw, top_cap=LUMP_TOP["large"], tint=LUMP_TINT["large"])


def lump_small(a):
    c, r, sq, n, pk, seed, yaw = LUMPS["small"]
    _lump(a, (0, 0, r * sq[2]), r, sq, n, pk, seed, yaw, top_cap=LUMP_TOP["small"], tint=LUMP_TINT["small"])


# ---- leaf clumps ------------------------------------------------------------------------------------------------------
KITE = ((0.25, 0.40), (0.55, 0.50), (0.82, 0.28))     # (t, half width / W): shoulder, belly, pre-tip (M018 recipe)
RIDGE = ((0.42, 0.08), (0.76, 0.04))                  # (t, camber / L): the midrib ridge
KEEL = (0.50, 0.04)
FOLD = 0.45
HANDLES = (0.48, 0.38)
LEAF_BANDS = ((0.18, 0.42), (0.58, 0.82))
LEAF_NOISE = 0.08
LEAF_MOTTLE = dict(amp=0.035, scale=0.5, seed=19071)


def _bez(P, t):
    p0, p1, p2, p3 = P
    s = 1 - t
    return p0 * s ** 3 + p1 * 3 * s * s * t + p2 * 3 * s * t * t + p3 * t ** 3


def _bez_d(P, t):
    p0, p1, p2, p3 = P
    s = 1 - t
    return (p1 - p0) * 3 * s * s + (p2 - p1) * 6 * s * t + (p3 - p2) * 3 * t * t


def _leaf_path(base, az, tip, pitch, slope):
    """Cubic Bezier midline in the clump's local frame: leaves base at `pitch` toward azimuth az, reaches the tip
    (r, z) at `slope` degrees (negative = drooping)."""
    B = Vector(base)
    a1 = math.radians(az)
    T = Vector((math.cos(a1) * tip[0], math.sin(a1) * tip[0], tip[1]))
    chord = (T - B).length

    def dirn(p):
        p = math.radians(p)
        return Vector((math.cos(a1) * math.cos(p), math.sin(a1) * math.cos(p), math.sin(p)))
    return (B, B + dirn(pitch) * HANDLES[0] * chord, T - dirn(slope) * HANDLES[1] * chord, T)


def _leaf(a, path, width, seed, roll=0.0, shift=0.0):
    """One closed broad pointed leaf along path (local clump frame): an 8-point kite outline, two midrib ridge
    points above (the lit and shaded halves), a keel below. Painted base -> mid -> tip along its own length.
    Returns verts."""
    rng = random.Random(seed)
    bm = a.bm
    P = [Vector(p) for p in path]
    L = sum((_bez(P, (i + 1) / 20) - _bez(P, i / 20)).length for i in range(20))
    W = width
    side0 = Vector((-(P[3] - P[0]).y, (P[3] - P[0]).x, 0.0)).normalized()
    rl = math.radians(roll)

    def frame(t):
        T = _bez_d(P, t).normalized()
        S = (side0 - T * side0.dot(T)).normalized()
        N = T.cross(S).normalized()
        if N.z < 0:
            N = -N
        S = N.cross(T).normalized()
        S, N = S * math.cos(rl) + N * math.sin(rl), N * math.cos(rl) - S * math.sin(rl)
        return _bez(P, t), S, N
    tm = {}

    def vert(t, y, z):
        c, S, N = frame(t)
        x = bm.verts.new(c + S * y + N * z)
        tm[x] = t
        return x
    base = vert(0.0, 0.0, 0.0)
    tip = vert(1.0, 0.0, 0.0)
    right, left = [], []
    for t, h in KITE:
        y = h * W * (1 + rng.uniform(-0.06, 0.06))
        right.append(vert(t, -y, -FOLD * y * 0.5))
    for t, h in KITE:
        y = h * W * (1 + rng.uniform(-0.06, 0.06))
        left.append(vert(t, y, -FOLD * y * 0.5))
    r1 = vert(RIDGE[0][0], 0.0, RIDGE[0][1] * L)
    r2 = vert(RIDGE[1][0], 0.0, RIDGE[1][1] * L)
    # the keel below the lowest (drooped) outline point, so the bottom fan never folds up through the top: a leaf
    # whose drooped edges hung below its keel was inside-out there, and the exact boolean then dropped or broke it
    k = vert(KEEL[0], 0.0, -(FOLD * 0.5 * max(KITE[1][1], KITE[0][1]) * W * 1.07 + KEEL[1] * L))
    tm[k] = KEEL[0] - 0.25 * 2       # keel faces read toward the base
    ring = [base] + right + [tip] + list(reversed(left))
    fs = []
    for sd in (right, left):
        s, b, p = sd
        fs += [bm.faces.new((base, s, r1)), bm.faces.new((s, b, r1)), bm.faces.new((b, r2, r1)),
               bm.faces.new((b, p, r2)), bm.faces.new((p, tip, r2))]
    for i in range(len(ring)):
        fs.append(bm.faces.new((k, ring[(i + 1) % len(ring)], ring[i])))
    vs = ring + [r1, r2, k]
    a._finish(vs, LEAF)
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    lad = _ladder(LEAF_BASE, LEAF, LEAF_TIP)
    for f in fs:
        t = sum(tm[v] for v in f.verts) / len(f.verts) + shift + rng.uniform(-LEAF_NOISE, LEAF_NOISE)
        f.material_index = a._mi(_pick(lad, t, LEAF_BANDS[0], LEAF_BANDS[1]))
    return vs


LEAF_LW = (1.0, 0.55)         # leaf length and width (x span / 1.5)
LEAF_RISE = (3, 9)            # default chord rise of a leaf above the hub plane, degrees
LEAF_PITCH = (20, 34)         # the base leaves this much steeper than the chord, degrees
LEAF_BURY = -0.16             # leaf base depth below the hub point (x span / 1.5)
HUB_R, HUB_H = 0.2, 0.16      # hub cone radius and apex height (x span / 1.5)


def _clump(a, hub, normal, span, seed, yaw=0.0, shift=0.0, sink=0.35, rise=LEAF_RISE):
    """A five-leaf star round a hidden 5-sided hub cone: local frame hub at the origin, +Z along normal. Leaves at
    72 deg (+-12), each leaf's chord rising `rise` (a range, degrees) off the hub's plane, the base steeper and the
    tip drooping below the chord; per leaf +-8 % L, +-6 % W, +-5 deg roll.
    span = the clump's tip-to-tip width. The hub cone's foot is `sink` below the hub (inside the support)."""
    rng = random.Random(seed)
    bm = a.bm
    s = span / 1.5
    out = []
    # hub cone (hidden under the leaf bases): 5 sides, foot sunk into the support
    hr = HUB_R * s
    ph = rng.uniform(0, 2 * math.pi)
    foot = [bm.verts.new((math.cos(ph + 2 * math.pi * k / 5) * hr, math.sin(ph + 2 * math.pi * k / 5) * hr, -sink))
            for k in range(5)]
    mid = [bm.verts.new((math.cos(ph + 2 * math.pi * k / 5) * hr * 0.85,
                         math.sin(ph + 2 * math.pi * k / 5) * hr * 0.85, 0.04 * s)) for k in range(5)]
    apex = bm.verts.new((0, 0, HUB_H * s))
    fb = bm.verts.new((0, 0, -sink - 0.02))
    fs = _strip(bm, foot, mid) + _fan(bm, mid, apex) + _fan(bm, foot, fb, flip=True)
    _tri(bm, fs)
    hub_v = foot + mid + [apex, fb]
    a._finish(hub_v, LEAF_BASE)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(hub_v))
    out += hub_v
    az0 = rng.uniform(0, 360)
    for k in range(5):
        az = az0 + 72 * k + rng.uniform(-12, 12)
        L = LEAF_LW[0] * s * (1 + rng.uniform(-0.08, 0.08))
        W = LEAF_LW[1] * s * (1 + rng.uniform(-0.06, 0.06))
        # the leaf's base point deep inside the hub, so each leaf crosses the hub's surface where it already has real
        # width and thickness (a leaf entering at its zero-thickness point stayed a separate shell after the union);
        # the base offsets differ per leaf so no two leaves share a point
        b0 = Vector((math.cos(math.radians(az)) * 0.02 * s, math.sin(math.radians(az)) * 0.02 * s,
                     (LEAF_BURY + 0.012 * k) * s))
        ch = math.radians(rng.uniform(*rise))
        path = _leaf_path(b0, az, (L * 0.92 * math.cos(ch), L * 0.92 * math.sin(ch)),
                          math.degrees(ch) + rng.uniform(*LEAF_PITCH), math.degrees(ch) + rng.uniform(-28, -12))
        out += _leaf(a, path, W, seed * 10 + k, roll=rng.uniform(-5, 5), shift=shift)
    m = Matrix.Translation(Vector(hub)) @ _align(normal, yaw).to_4x4()
    bmesh.ops.transform(bm, matrix=m, verts=out)
    _mottle(a, _faces(out), LEAF_MOTTLE["amp"], LEAF_MOTTLE["scale"], LEAF_MOTTLE["seed"] + seed)
    return out


# hero clumps: (hub target (build frame), normal, span, seed, yaw, colour shift toward the tips)
CLUMPS = {"TL": ((-0.7, 2.3, 2.6), (-0.2, -0.8, 0.55), 1.85, 19081, 10.0, 0.1),
          "TR": ((3.2, 0.15, 3.5), (0.3, -0.7, 0.65), 2.4, 19082, 40.0, 0.1),
          "R_low": ((2.2, -0.75, 1.3), (0.8, -0.35, 0.5), 1.7, 19083, 0.0, 0.0),
          "F": ((-0.45, -1.45, 0.42), (0.0, -0.85, 0.5), 1.65, 19084, 56.0, 0.0),
          "L": ((-2.7, 1.25, 1.3), (-0.45, 0.3, 0.84), 1.5, 19085, 0.0, 0.0)}
CLUMP_LIFT = -0.03      # the hub point this far out of the surface it lands on (negative: just inside it)
HUB_SINK = 0.14         # the hub cone's foot this far below the hub point (a deeper foot, with the leaf bases inside the
#                         hub, left the leaves as separate shells after the union)
CLUMP_INFO = {}


# the high clumps stand up as fans (the sheet shows them nearly face-on from the front34 camera)
CLUMPS = {k: (_sx(v[0]),) + tuple(v[1:]) for k, v in CLUMPS.items()}
CLUMP_RISE = {"TL": (26, 40), "TR": (34, 50)}
CLUMP_SNAP = 0.6       # a hub within this of the bark / pad / lump moves onto it; further out it keeps its place and
#                        a hidden stalk joins it to the nearest surface (the front clump lies on the ground)


def _stalk(a, p0, p1, r, seed):
    """A hidden 5-sided tapered prism from p0 (inside the hub) to p1 (inside the support)."""
    rng = random.Random(seed)
    bm = a.bm
    P0, P1 = Vector(p0), Vector(p1)
    t = (P1 - P0).normalized()
    n = _perp(t)
    b = t.cross(n)
    ph = rng.uniform(0, 6.3)
    rings = [[bm.verts.new(c + (n * math.cos(ph + 2 * math.pi * k / 5) + b * math.sin(ph + 2 * math.pi * k / 5)) * rr)
              for k in range(5)] for c, rr in ((P0, r * 0.8), (P1, r))]
    c0, c1 = bm.verts.new(P0 - t * 0.02), bm.verts.new(P1 + t * 0.02)
    fs = _strip(bm, rings[0], rings[1]) + _fan(bm, rings[0], c0, flip=True) + _fan(bm, rings[1], c1)
    _tri(bm, fs)
    vs = rings[0] + rings[1] + [c0, c1]
    a._finish(vs, LEAF_BASE)
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    return vs


def clumps(a):
    """The five leaf clumps. A hub near the bark / pads / lumps built so far moves onto the nearest surface; one
    further out keeps its place and gets a hidden stalk to it, so none floats (spec section 6)."""
    a.bm.verts.ensure_lookup_table()
    a.bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(a.bm)
    out = []
    pre_info = CLUMP_INFO.get("_pre")
    CLUMP_INFO.clear()
    if pre_info:
        CLUMP_INFO["_pre"] = pre_info
    for k, (hub, nrm, span, seed, yaw, shift) in CLUMPS.items():
        rise = CLUMP_RISE.get(k, LEAF_RISE)
        H, N = Vector(hub), Vector(nrm).normalized()
        loc, sn, _, dist = tree.find_nearest(H)
        if dist <= CLUMP_SNAP:
            P = loc + sn * CLUMP_LIFT
        else:
            P = H
            out += _stalk(a, H - N * 0.1, loc - sn * 0.15, 0.13 * span / 1.5, seed + 7)
        CLUMP_INFO[k] = {"moved": round((P - H).length, 2), "gap": round(dist, 2), "hub": [round(c, 2) for c in P],
                         "n_dot_surface": round(N.dot(sn), 2)}
        pre = bpy.data.objects.get(f"_m019_clump_{k}")
        if pre is not None:
            # the clump pre-fused into one shell (_clump_objs): one clean boolean against the bark in the hero
            m = Matrix.Translation(P) @ _align(N, yaw + CLUMP_YAW_JIT[0]).to_4x4() @ Matrix.Translation(Vector(pre[OFF]))
            out += m011._paste(a, pre, m)
        else:
            out += _clump(a, P, N, span, seed, yaw + CLUMP_YAW_JIT[0], shift, rise=rise)
    return out


def _clump_fn(k, attempt=0):
    hub, nrm, span, seed, yaw, shift = CLUMPS[k]
    return lambda a: _clump(a, (0, 0, 0), (0, 0, 1), span, seed + 1000 * attempt, 0.0, shift, sink=HUB_SINK,
                            rise=CLUMP_RISE.get(k, LEAF_RISE))


CLUMP_TRIES = 8
HERO_TRIES = 6
HERO_YAW_STEP = 9.0
CLUMP_YAW_JIT = [0.0]      # extra yaw on every hero clump; the hero guard turns the clumps a little on a retry


def _fused_ok(o):
    a = M.audit(o)
    return (a["shells"] == 1 and not a["nonmanifold_edges"] and not a["boundary_edges"] and a["normals"] == "outward"
            and not m016._self_hits(o)[0] and not m012._thin(o, POLISH_LIM)["under"])


def _fuse_clump(name, fn_of, tries=CLUMP_TRIES):
    """Build fn_of(attempt) into a temporary object, fuse its leaves and hub into one closed shell and clean it (as
    a part). A union of five thin leaves can fold a sliver into a neighbour (a self-intersection, which then makes
    the hero's exact boolean fail): the guard checks the result (one shell, manifold, outward, no self-hits, no
    corner under POLISH_LIM) and rebuilds with the next leaf seed until it is clean. Returns (object, attempt)."""
    o = None
    for attempt in range(tries):
        fn = fn_of(attempt)
        o = K.test_asset(name, fn, tint_var=0.04)
        o.location = (0, 0, 0)
        bpy.context.view_layer.update()      # split_loose copies matrix_world: it must not be stale
        o[OFF] = list(M._build_offset(fn))
        M.union_loose(o)
        m016._clean_mesh(o, ())
        _finish(o)
        _polish(o)
        if _fused_ok(o):
            return o, attempt
    return o, -1


def _clump_objs():
    """Each hero clump built in its own frame (hub at the origin, +Z its normal) and fused into one closed shell
    first (_fuse_clump), so the hero's union meets one clean shell per clump. Temporary objects, removed by
    _cleanup_tmp."""
    out = {}
    for k in CLUMPS:
        o, attempt = _fuse_clump(f"_m019_clump_{k}", lambda i, k=k: _clump_fn(k, i))
        CLUMP_INFO.setdefault("_pre", {})[k] = {"attempt": attempt, "tris": len(o.data.polygons)}
        out[k] = o
    return out


def clump_part(a):
    """ResinBranchLeafClump: one clump, hub up."""
    _clump(a, (0, 0, PART_SINK), (0, 0, 1), 1.5, 19089, 0.0, 0.0, sink=PART_SINK)


PART_SINK = 0.12


# ---- hero ----------------------------------------------------------------------------------------------------------
def hero(a):
    body(a)
    caps(a)
    lumps(a)
    clumps(a)


NOTES = {
    "ResinBranchNode": "resin node: one fallen forked branch lying in an X (a thick straight limb rising to a flat cut end, a "
                       "second log across it, two short stubs), every log end a thick faceted cream cut-end insert, "
                       "two chunky faceted orange resin lumps straddling the logs (large at the front-left, small "
                       "on the right stub), five bright five-leaf clumps in the notches; one closed mesh, flat "
                       "ground contact. VFX: 2 ore_glint (pale gold sparkle stars round each lump); no glow",
    "ResinBranchBody": "Main Branch Body (reusable): two crossing faceted logs and two stubs fused through a knot at "
                       "the fork, the two resin join pads; flat cut faces with a bark lip at each end, no inserts",
    "ResinBranchCutEnd": "Branch Cut End (reusable): thick 10-sided cream insert, low faceted dome face in two ring "
                         "bands",
    "ResinBranchLumpLarge": "Resin Lump (Large, reusable): chunky broad-faceted orange nodule, yellow top to "
                            "red-orange bottom",
    "ResinBranchLumpSmall": "Resin Lump (Small, reusable): the large lump's family at two thirds the size",
    "ResinBranchLeafClump": "Leaf Clump (reusable): five broad pointed leaves in a star round a hidden hub, dark "
                            "bases to lime tips",
}


# ---- cleanup (m016's procedure, this model's offset key) -------------------------------------------------------------
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
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = m012._tri_quads(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = m012._force_slivers(o, lim=POLISH_LIM)
    if m012._thin(o, POLISH_LIM)["under"]:
        forced += m012._force_slivers(o, lim=POLISH_LIM, max_len=0.5)
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
    """Faces lying on the ground plane (the floor cut's caps): the ground-contact tone (bark_dark, or the leaf base
    under a leaf), chosen by position, not light."""
    from m011 import _Paint
    p = _Paint(o, off=o[OFF])
    n = 0
    for f in p.bm.faces:
        if all(abs(v.co.z) < 1e-3 for v in f.verts):
            nb = {p.key(g) for e in f.edges for g in e.link_faces if g is not f}
            f.material_index = p._mi(LEAF_BASE if any(k.startswith("m019_leaf") for k in nb) else BARK_DARK)
            n += 1
    p.done()
    return n


# ---- stages 5 + 6 (spec section 7) ---------------------------------------------------------------------------------
# Stage 5: nothing. The sheet says "No glow baked into model": no emissive key, no light.
# Stage 6: two ore_glint sockets, one per lump, the sheet's pale-gold four-point stars round each lump.
GLINT = {"name": "Glint", "texture": "spark_diamond", "color": ["#F9E4C4", "#FBD28E"], "transparency": [0.1, 1.0],
         "lifetime": [0.6, 0.9], "speed": [0, 0], "spread": 0, "light_emission": 1.0, "rotation": [0, 90]}
# Round 2 (verifier finding 7): round 1 put each socket at its lump's centre, so 33 % (large; 14 % under the ground)
# and 21 % (small) of the spawn box was inside the mesh. Each socket now sits `shift` from its lump centre (up, and a
# little toward the upper-front-left, where the sheet's stars are), and `height` (Roblox Y) caps the box above the
# ground.
# Monte Carlo (3000 points, 3-ray parity): large 13.2 % hidden, small 13.1 %, none below the ground.
GLINTS = {"large": dict(size=[0, 0.9, 0], rate=2.5, pad=0.8, shift=(-0.35, -0.55, 0.85), height=3.0),
          "small": dict(size=[0, 0.65, 0], rate=1.5, pad=0.7, shift=(-0.4, -0.7, 0.9), height=2.6)}


def _vfx(h):
    off = Vector(h[OFF])
    made = []
    for k, g in GLINTS.items():
        c, r, sq = LUMPS[k][:3]
        d = [2 * r * s + 2 * g["pad"] for s in sq]
        if g.get("height"):
            d[2] = g["height"]
        em = dict(GLINT, size=g["size"], rate=g["rate"], shape=[round(d[0], 2), round(d[2], 2), round(d[1], 2)])
        p = Vector(c) + Vector(g.get("shift", (0, 0, 0))) - off
        made.append(K.socket(h, "ore_glint", [round(x, 3) for x in p], emitters=[em]))
    return made


# ---- build --------------------------------------------------------------------------------------------------------
PARTS = (("ResinBranchBody", body), ("ResinBranchCutEnd", cut_end), ("ResinBranchLumpLarge", lump_large),
         ("ResinBranchLumpSmall", lump_small), ("ResinBranchLeafClump", clump_part))
UNION_PARTS = {"ResinBranchBody", "ResinBranchLeafClump"}
GROUND_PARTS = {"ResinBranchBody"}


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith("_m019_"):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)


def _make(name, fn, role, budget):
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget, collision="hull",
             tint_var=0.04)
    off = M._build_offset(fn)
    o[OFF] = list(off)
    lg = {}
    if name in UNION_PARTS or role == "hero":
        lg["shells_merged"] = M.union_loose(o)
    if name in GROUND_PARTS or role == "hero":
        m004.floor_cut(o, z0=-off.z)
        o[OFF] = [off.x, off.y, 0.0]
    if name in UNION_PARTS or role == "hero":
        lg["clean"] = m016._clean_mesh(o, (0.0,) if (name in GROUND_PARTS or role == "hero") else ())
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    if name in GROUND_PARTS or role == "hero":
        lg["ground_faces"] = _ground_faces(o)
    return o, lg


def build(render=True, parts=True):
    M.coll(NUM, TITLE)
    palette()
    BODY_INFO.clear()
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn, "part", 1000)
    _clump_objs()
    # the hero guard: a leaf grazing a cap or a crease can leave a hole or a fold after the union and cleanup; then
    # every clump turns HERO_YAW_STEP degrees about its own axis and the hero is rebuilt
    for attempt in range(HERO_TRIES):
        CLUMP_YAW_JIT[0] = attempt * HERO_YAW_STEP
        h, log["hero"] = _make("ResinBranchNode", hero, "hero", 4000)
        if _fused_ok(h):
            break
    log["hero"]["attempt"] = attempt if _fused_ok(h) else -1
    log["hero"]["clump_yaw_jit"] = CLUMP_YAW_JIT[0]
    log["clumps"] = dict(CLUMP_INFO)
    sockets = _vfx(h)
    _resin_spec()
    _cleanup_tmp()
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    out = {"audit": [{k: M.audit(o)[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges",
                                                     "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces",
                                                     "normals", "ngons")}
                     for o in order],
           "thin": {o.name: m012._thin(o, POLISH_LIM) for o in order}, "log": log,
           "self_hits": {o.name: m016._self_hits(o)[0] for o in order}, "problems": K.check(order),
           "sockets": [(s.name, s["vfx_kind"], [round(c, 3) for c in s.location]) for s in sockets],
           "uv": {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped",
                                                                            "min_gap", "density",
                                                                            "stretch_conformal_p95")}
                  for o in order}}
    if render:
        out["views"] = render_views(order)
    return out


# ---- renders ---------------------------------------------------------------------------------------------------------
def _part_matrix(o):
    """Part mesh coords -> its own build frame."""
    return Matrix.Translation(Vector(o[OFF]))


# exploded shot: (part, matrix in the hero build frame) with the sheet's offsets
EXPL_CLUMPS = {"TL": (-1.2, 0.6, 1.6), "TR": (1.4, 0.2, 1.4), "R_low": (1.8, -0.6, 0.0), "F": (0.0, -1.8, -0.3),
               "L": (-1.8, -0.4, 0.4)}


def _exploded(objs):
    """Copies of the parts laid out like the sheet's exploded view (lumps and clumps pulled out from the body, two
    loose cut ends in front); returns the temporary objects."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []

    def put(name, part, m):
        c = bpy.data.objects.new(f"_m019_expl_{name}", by[part].data)
        coll.objects.link(c)
        c.matrix_world = m @ _part_matrix(by[part])
        shown.append(c)
    x0 = objs[0].location.x + 40
    base = Matrix.Translation((x0, objs[0].location.y, 0))
    put("body", "ResinBranchBody", base)
    for k, dv in (("large", (-1.6, -0.6, 0.5)), ("small", (1.4, -0.6, 0.5))):
        c, r, sq = LUMPS[k][:3]
        name = "ResinBranchLumpLarge" if k == "large" else "ResinBranchLumpSmall"
        put(k, name, base @ Matrix.Translation(Vector(c) + Vector(dv) - Vector((0, 0, r * sq[2]))))
    for k, (hub, nrm, span, seed, yaw, shift) in CLUMPS.items():
        P = Vector(CLUMP_INFO.get(k, {}).get("hub", hub))
        m = Matrix.Translation(P + Vector(EXPL_CLUMPS[k])) @ _align(nrm, yaw).to_4x4() @ \
            Matrix.Diagonal((span / 1.5, span / 1.5, span / 1.5, 1.0)) @ Matrix.Translation((0, 0, -PART_SINK))
        put("clump_" + k, "ResinBranchLeafClump", base @ m)
    ends = body_info()["ends"]
    for k, dv in (("A_low", (-0.6, -1.3, -0.1)), ("B_front", (1.0, -1.2, 0.0))):
        e = ends[k]
        sc = e["radius"] * CAP_R / PART_CAP_R
        m = Matrix.Translation(Vector(e["centre"]) + Vector(dv)) @ _align(e["normal"]).to_4x4() @ \
            Matrix.Diagonal((sc, sc, sc, 1.0)) @ Matrix.Translation((0, 0, -CAP_SINK * 2 * PART_CAP_R))
        put("cap_" + k, "ResinBranchCutEnd", base @ m)
    bpy.context.view_layer.update()
    return shown


def render_close(objs, path, az, el, centre, radius):
    """A close-up: the kit studio and camera aimed from (az, el), framed on a sphere (centre, radius) in world
    coordinates instead of the whole group."""
    kit = K.NS["KIT"]
    fb = kit["frame_box"]
    c = Vector(centre)
    box = [c + Vector((dx, dy, dz)) * radius for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    kit["frame_box"] = lambda corners, a_, e_: fb(box, a_, e_)
    ground = bpy.data.objects.get("FB_Ground")
    if ground:
        ground.hide_render = el < 0
    old = kit["CELL"]
    kit["CELL"] = (480, 400)
    try:
        return kit["render_group"](objs, path, az, el)
    finally:
        kit["frame_box"] = fb
        kit["CELL"] = old
        if ground:
            ground.hide_render = False


def render_views(objs):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    for o in shown:
        o.hide_render = False
    try:
        extra = {"front_sheet": ([h], -28, 6), "side_sheet": ([h], 90, 4), "top_tilt": ([h], -20, 60)}
        if shown:
            extra["exploded"] = (shown, -25, 15)
        for o in objs[1:]:
            extra["part_" + o.name.replace("ResinBranch", "").lower()] = ([o], -25, 15)
        sheet = M.views(NUM, [h], extra=extra)
        d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
        off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
        jc = off @ Vector(J)
        close = {"junction": render_close([h], f"{d}/junction.png", -10, 20, jc + Vector((0.6, 0, 0.4)), 1.6)}
        c, r = LUMPS["large"][:2]
        close["underside_pad"] = render_close([h], f"{d}/underside_pad.png", -40, -30, off @ Vector(c), 1.7)
        e = body_info()["ends"]["B_front"]
        close["cut_end"] = render_close([h], f"{d}/cut_end.png", 15, 10, off @ Vector(e["centre"]), 1.1)
        return {"sheet": sheet, **close}
    finally:
        for o in shown:
            bpy.data.objects.remove(o, do_unlink=True)
        M.display(NUM, objs, TITLE)
