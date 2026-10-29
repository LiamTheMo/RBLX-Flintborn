"""033 Cave Moss (references/033.png): one broad, low, faceted warm-grey boulder (the Rock Base: a back hump, a lower
front lobe with a notch, a front-left shoulder and a right flank), capped at the back and both sides by three chunky
broad-faceted moss clumps (the centre one highest, on the back hump, with a flat crown polygon; the left and right ones
tilted ovoid lumps draped over the shoulders), two bright lime sprouts (A in the front notch, B taller at the
back-right in the crease between the centre and right clumps) and six small faceted rocks round the foot.

    import importlib, kit_models, m033; importlib.reload(kit_models); importlib.reload(m033); m033.build()

Parts as on the sheet's Exploded Construction, each built by its own function, all in one build frame (studs; front
-Y, +X right, ground z = 0, origin = the bbox bottom centre). R07 owns CaveMoss* and W06 MossCushion*, so the names are
MossBoulder* (M033_spec.md section 8, decision 10):
- MossBoulderClump (clump_centre_part): the centre clump: a squat convex-hull dome of jittered point rings with a flat
  crown polygon.
- MossBoulderClumpSide (clump_side_part): the left clump's shape, untilted (an ovoid lump, pointed-round at both ends).
- MossBoulderSprout (sprout_part): sprout B's fan: four diamond-section blades with a midrib, joined in a small stub.
- MossBoulderBase (base_part): the Rock Base alone: one non-convex ring mesh whose heights follow a lobe field, floor-cut.
- MossBoulderSideRock (side_rock_part): the right side rock alone, a squat bulged dome.

The hero (MossBoulderNode) is built from the same builders: the base, the six small rocks, the three clumps, then the
two sprouts seated by ray casts on the rock / moss, united one shell at a time with merge-0 exact unions at the world
origin, floor-cut flat at the ground. Colour (stage 4) is painted by position inside the builders before the union
(the union and cleanup keep each face's key and Tint). Stages 5-6: nothing (decision 7: no emission, light or VFX).
See M033_spec.md.
"""
import math
import random
import time

import bmesh
import bpy
from mathutils import Matrix, Vector, noise

import kit_mcp as K
import kit_models as M
import m011
import m012
import m016

NUM, TITLE, SHEET = 33, "Cave Moss", "M033"
OFF = "m033_offset"
HERO = "MossBoulderNode"
CLUMP_P, SIDE_CLUMP_P, SPROUT_P = "MossBoulderClump", "MossBoulderClumpSide", "MossBoulderSprout"
BASE_P, SIDE_ROCK_P = "MossBoulderBase", "MossBoulderSideRock"

MOSS, MOSS_DARK = "m033_moss", "m033_moss_dark"
SPROUT, SPROUT_BASE = "m033_sprout", "m033_sprout_base"
ROCK, ROCK_LOW = "m033_rock", "m033_rock_low"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# key -> (hex, roughness, low specular). Stage 4 (M033_spec.md "Stage 4"):
# Pass 1 (K.calibrate on the kit test dome against TARGETS; rendered sRGB in brackets): moss #5B7620 (107,138,32),
# moss_dark #4B631A (87,114,26), sprout #819631 (158,180,50), sprout_base #69801D (126,151,30), rock #7F797D
# (159,147,144; a mauve key, B > G), rock_low #6D676A.
# Pass 2 (front_sheet render, floor hidden, against the sheet's front-cell class medians; linear gains): moss x ~1.3
# then -6 % to balance the hero (#6F8E22) against the parts shot (#6E8E20): moss #648125, moss_dark #516A1D;
# sprout x ~1.75 (the blades sit in the clumps' shade; hero L #778923 against #A5BA38) -> #ABC448 with SPEC 0.25 for
# the sheet's pale lit facets; rock kept a warm key (R > G > B, hue ~5) whose render lands at hue ~20: #857C7B / #736B6A.

PALETTE = {MOSS: ("#648125", 0.9, True), MOSS_DARK: ("#516A1D", 0.9, True),
           SPROUT: ("#ABC448", 0.75, True), SPROUT_BASE: ("#88A226", 0.75, True),
           ROCK: ("#857C7B", 0.92, False), ROCK_LOW: ("#736B6A", 0.92, False)}

# calibration targets (spec 5.4: rendered medians of unshadowed regions on the sheet: the exploded parts)
TARGETS = {MOSS: ((0x6E, 0x8E, 0x20), "green"), MOSS_DARK: ((0x58, 0x74, 0x1A), "green"),
           SPROUT: ((0xA1, 0xB7, 0x32), "green"), SPROUT_BASE: ((0x80, 0x9A, 0x1E), "green"),
           ROCK: ((0xA1, 0x94, 0x92), "stone"), ROCK_LOW: ((0x8A, 0x7E, 0x7B), "stone")}


# Specular IOR Level per key prefix, set after the palette (low_spec keys default to K.FOLIAGE_SPEC 0.06): the
# sheet's blades show soft pale highlights on their lit facets (lit quartile #CEDC57, sat 0.60 against the median's 0.70)
SPEC = {SPROUT: 0.25}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    _spec()


def _spec():
    """Specular per SPEC prefix on every m033 material, mixes included (m033_sprout_x_base_50 etc.). (m031)"""
    for m in bpy.data.materials:
        if not m.name.startswith("FB_m033_") or not m.node_tree:
            continue
        key = m.name[3:]
        lvl = next((v for p, v in SPEC.items() if key.startswith(p)), None)
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if lvl is not None and bsdf and "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = lvl


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome. Returns {key: (hex, rendered)} and
    leaves the keys set (write them into PALETTE)."""
    keys = keys or list(TARGETS)
    for k in keys:
        K.fk().material(k)
    try:
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


# ---- small helpers (m031) --------------------------------------------------------------------------------------------
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


def _mix(k1, k2, t):
    """k1 -> k2 at t quantised to 25 % steps."""
    t = round(max(0.0, min(1.0, t)) * 4) / 4
    return K.mix_key(k1, k2, t)


def _zip(bm, ra, rb):
    """Triangles between two closed rings ordered by increasing angle about +Z (local frame), walking both by angle
    (half-step offset rings give triangles and kites). Returns faces. (m025 / m031)"""
    def ang(v):
        return math.atan2(v.co.y, v.co.x)
    a0 = min(range(len(ra)), key=lambda i: ang(ra[i]) % (2 * math.pi))
    b0 = min(range(len(rb)), key=lambda i: ang(rb[i]) % (2 * math.pi))
    A = ra[a0:] + ra[:a0]
    B = rb[b0:] + rb[:b0]
    na, nb = len(A), len(B)

    def ua(i):
        return (ang(A[i % na]) - ang(A[0])) % (2 * math.pi) + (2 * math.pi if i >= na else 0.0)

    def ub(j):
        return (ang(B[j % nb]) - ang(A[0])) % (2 * math.pi) + (2 * math.pi if j >= nb else 0.0)
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


def _fan(bm, ring, centre):
    n = len(ring)
    return [bm.faces.new((ring[k], ring[(k + 1) % n], centre)) for k in range(n)]


def _place(bm, vs, m):
    bmesh.ops.transform(bm, matrix=m, verts=[v for v in vs if v.is_valid])


def _hull(a, pts, key):
    """Convex hull of points as one closed triangulated shell (coplanar rings come out as n-gons: triangulated)."""
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    for v in vs:
        if v.is_valid and not v.link_faces:
            bm.verts.remove(v)
    vs = [v for v in vs if v.is_valid]
    _tri(bm, _faces(vs))
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, key)
    return vs


def _ring_pts(rng, rings, rx, ry, T, jitter, lean=(0.0, 0.0), ang_jit=0.28):
    """Jittered point rings (height fraction, radius fraction, points) for a hull (kit_mcp.hull_rock's sampling)."""
    pts = []
    for h, rf, n in rings:
        off = rng.uniform(0, 2 * math.pi)
        for k in range(n):
            th = off + 2 * math.pi * k / n + rng.uniform(-ang_jit, ang_jit) * (2 * math.pi / n)
            r = rf * (1 + rng.uniform(-jitter, jitter))
            z = h * T * (1 + (rng.uniform(-jitter, jitter) if 0 < h < 1 else 0))
            pts.append(Vector((math.cos(th) * rx * r + lean[0] * rx * h, math.sin(th) * ry * r + lean[1] * ry * h,
                               max(0.0, z))))
    return pts


# ---- moss clumps (spec 1.4, 2.2) -------------------------------------------------------------------------------------
# rings (height fraction, radius fraction, points). MC: a broad squat dome, near-flat underside, the last ring all at
# h 1.0 (the flat crown polygon). ML / MR: ovoid lumps, pointed-round at both ends.
MC_RINGS = ((0.0, 0.55, 6), (0.24, 0.92, 7), (0.52, 1.0, 7), (0.80, 0.76, 6), (1.0, 0.36, 4))
SIDE_RINGS = ((0.0, 0.40, 5), (0.20, 0.86, 7), (0.48, 1.0, 7), (0.76, 0.84, 6), (1.0, 0.30, 4))
CLUMP_JIT = 0.10
# name -> centre (x, y, z), size (along the long axis x across x thickness), tilt (deg about Y; negative lifts the +X
# end), yaw (deg), lean (fraction of the radius the upper rings drift, local x), rings, seed
CLUMPS = {
    "MC": dict(loc=(-0.15, 1.14, 2.52), size=(2.72, 2.50, 1.55), tilt=0.0, pitch=-14.0, yaw=10.0, lean=(0.0, 0.0), rings=MC_RINGS,
               seed=33101),
    "ML": dict(loc=(-1.72, -0.30, 1.82), size=(2.42, 2.20, 1.72), tilt=-32.0, yaw=14.0, lean=(0.10, 0.0),
               rings=SIDE_RINGS, seed=33102),
    "MR": dict(loc=(1.74, -0.35, 1.74), size=(2.30, 2.05, 1.72), tilt=32.0, yaw=-14.0, lean=(-0.10, 0.0),
               rings=SIDE_RINGS, seed=33103),
}
CLUMP_MOTTLE = dict(amp=0.035, scale=0.6, seed=33111)
CLUMP_INFO = {}


def _clump_local(a, cp, key=MOSS):
    """One clump's hull in its local frame (bottom at z 0, untilted)."""
    L, D, T = cp["size"]
    rng = random.Random(cp["seed"])
    pts = _ring_pts(rng, cp["rings"], L / 2, D / 2, T, CLUMP_JIT, cp["lean"])
    return _hull(a, pts, key), T


def _paint_clump(a, vs, seed):
    """MOSS, the lowest part of the clump (by its own world height) toward MOSS_DARK at 75 / 50 / 25 % (the exploded
    clumps' bottom fifths are the Moss Dark swatch). Position only, never facing. (A 25 % lime crown was tried: it made
    the clump's colour follow face direction, K.check corr 0.92, and its lit crown read as sprout lime.)"""
    zs = [v.co.z for v in vs]
    z0, z1 = min(zs), max(zs)
    faces = _faces(vs)
    for f in faces:
        c = f.calc_center_median()
        hf = (c.z - z0) / max(1e-6, z1 - z0)
        t = 0.75 if hf < 0.12 else 0.5 if hf < 0.24 else 0.25 if hf < 0.40 else 0.0
        f.material_index = a._mi(_mix(MOSS, MOSS_DARK, t))
    _mottle(a, faces, CLUMP_MOTTLE["amp"], CLUMP_MOTTLE["scale"], CLUMP_MOTTLE["seed"] + seed)


def _clump(a, name):
    cp = CLUMPS[name]
    vs, T = _clump_local(a, cp)
    m = (Matrix.Translation(Vector(cp["loc"])) @ Matrix.Rotation(math.radians(cp["yaw"]), 4, "Z")
         @ Matrix.Rotation(math.radians(cp.get("pitch", 0.0)), 4, "X")
         @ Matrix.Rotation(math.radians(cp["tilt"]), 4, "Y") @ Matrix.Translation((0.0, 0.0, -T / 2)))
    _place(a.bm, vs, m)
    _paint_clump(a, vs, cp["seed"])
    CLUMP_INFO[name] = dict(faces=len(_faces(vs)), verts=len(vs))
    return vs


# ---- sprouts (spec 1.4, 2.3) -----------------------------------------------------------------------------------------
# blade cross-sections (t along the blade, width fraction of w); the tip is a point at t 1
BLADE_T = (0.0, 0.2, 0.55, 0.85)
BLADE_W = (0.40, 0.85, 1.0, 0.62)
BLADE_WF = 0.42           # widest width / length
BLADE_TH = 0.38           # diamond thickness / width
BLADE_FRONT = 0.55        # how far each blade's face turns from its lean toward the front
BLADE_CURL = 0.07         # outward curl of the tip (fraction of the length)
STUB = (0.15, 0.11, 0.17, 0.06, 6)    # (bottom radius, top radius, depth below the base, height above, sides)
# name -> base (x, y, z) (first guess; the hero seats it by a ray cast), blades (length, deg from vertical, toward az),
# seed
SPROUTS = {
    "A": dict(base=(-0.19, -1.35, 1.15), blades=((1.65, 6.0, 270.0), (1.45, 41.0, 195.0), (1.20, 37.0, 345.0),
                                                 (1.10, 25.0, 100.0)), seed=33301, ray=(0.0, 1.0, 0.0), sink=0.12),
    "B": dict(base=(1.313, 0.039, 2.50), blades=((1.64, 14.0, 0.0), (1.30, 30.0, 160.0), (1.10, 62.0, 345.0),
                                               (0.80, 30.0, 95.0), (0.95, 30.0, 240.0)), seed=33302, ray=(0.0, 0.0, -1.0), sink=0.12),
}
SPROUT_INFO = {}


def _blade(a, base, L, tilt, az, seed):
    """One closed blade: 4 diamond cross-sections (left edge, outer midrib, right edge, inner midrib) and a point."""
    rng = random.Random(seed)
    bm = a.bm
    d = Vector((math.cos(math.radians(az)), math.sin(math.radians(az)), 0.0))
    ax = (d * math.sin(math.radians(tilt)) + Vector((0, 0, 1)) * math.cos(math.radians(tilt))).normalized()
    # the blade's face: between its lean direction and the front (-Y): the sheet draws every sprout as a fan in the
    # picture plane, broad faces toward the viewer (a face purely along the lean showed side blades edge-on)
    n = d * (1 - BLADE_FRONT) + Vector((0, -1, 0)) * BLADE_FRONT
    if n.length < 0.25:
        n = d.copy()
    n = (n - ax * n.dot(ax)).normalized()
    tv = n                                    # the thickness axis (the blade's outer face)
    wv = ax.cross(tv).normalized()
    w = BLADE_WF * L * (1 + rng.uniform(-0.06, 0.06))
    secs = []
    for t, wf in zip(BLADE_T, BLADE_W):
        c = Vector(base) + ax * (t * L) + tv * (BLADE_CURL * L * t * t)
        hw = 0.5 * wf * w
        ht = 0.5 * BLADE_TH * wf * w
        secs.append([bm.verts.new(c - wv * hw), bm.verts.new(c + tv * ht), bm.verts.new(c + wv * hw),
                     bm.verts.new(c - tv * ht * 0.6)])
    tip = bm.verts.new(Vector(base) + ax * L + tv * (BLADE_CURL * L))
    faces = []
    for s0, s1 in zip(secs, secs[1:]):
        for k in range(4):
            j = (k + 1) % 4
            faces += [bm.faces.new((s0[k], s0[j], s1[j])), bm.faces.new((s0[k], s1[j], s1[k]))]
    s = secs[-1]
    faces += [bm.faces.new((s[k], s[(k + 1) % 4], tip)) for k in range(4)]
    b = secs[0]
    faces += [bm.faces.new((b[0], b[3], b[2])), bm.faces.new((b[0], b[2], b[1]))]
    vs = [v for sec in secs for v in sec] + [tip]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    a._finish(vs, SPROUT)
    for f in faces:
        tf = (f.calc_center_median() - Vector(base)).dot(ax) / L
        t = 0.75 if tf < 0.2 else 0.5 if tf < 0.4 else 0.25 if tf < 0.6 else 0.0
        f.material_index = a._mi(_mix(SPROUT, SPROUT_BASE, t))
    _mottle(a, faces, 0.02, 0.6, seed + 5)
    return vs


def _stub(a, base, seed):
    rb, rt, dn, up, n = STUB
    bm = a.bm
    az0 = random.Random(seed).uniform(0, 2 * math.pi)
    lo = [bm.verts.new((math.cos(az0 + 2 * math.pi * k / n) * rb, math.sin(az0 + 2 * math.pi * k / n) * rb, -dn))
          for k in range(n)]
    hi = [bm.verts.new((math.cos(az0 + math.pi / n + 2 * math.pi * k / n) * rt,
                        math.sin(az0 + math.pi / n + 2 * math.pi * k / n) * rt, up)) for k in range(n)]
    faces = _zip(bm, lo, hi)
    cb = bm.verts.new((0.0, 0.0, -dn))
    ct = bm.verts.new((0.0, 0.0, up))
    faces += _fan(bm, lo, cb) + _fan(bm, hi, ct)
    vs = lo + hi + [cb, ct]
    _place(bm, vs, Matrix.Translation(Vector(base)))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    a._finish(vs, _mix(SPROUT, SPROUT_BASE, 0.75))
    return vs


def _sprout(a, name, base=None):
    """The stub and the blades (each its own closed shell; the union fuses them). The blades' bases sit inside the
    stub, each nudged a little along its own lean so no two bases coincide."""
    sp = SPROUTS[name]
    base = Vector(base if base is not None else sp["base"])
    vs = _stub(a, base, sp["seed"])
    for i, (L, tilt, az) in enumerate(sp["blades"]):
        d = Vector((math.cos(math.radians(az)), math.sin(math.radians(az)), 0.0))
        b0 = base + d * (0.025 + 0.008 * i) + Vector((0, 0, -0.03 - 0.006 * i))
        vs += _blade(a, b0, L, tilt, az, sp["seed"] + 10 * (i + 1))
    SPROUT_INFO[name] = dict(base=[round(c, 3) for c in base])
    return vs


# ---- rock base (spec 1.4 Rock Base) ----------------------------------------------------------------------------------
BASE = dict(c=(0.05, 0.25), r=(2.45, 2.15), n=14, z0=-0.05, seed=33201)
# (radius fraction, height fraction of the lobe field): the bottom ring (below ground), the bulge, the shoulder, the
# upper ring, the inner ring, a 9-point top ring (even facets on the top: one 14 -> 5 step gave long thin
# streaky triangles); then a 5-point crown
BASE_RINGS = ((0.93, 0.0), (1.0, 0.22), (0.97, 0.52), (0.86, 0.80), (0.64, 0.95), (0.42, 0.99, 9))
BASE_CROWN = (0.18, 1.0, 5)
# lobe field (x, y, height, sigma): back hump, front lobe, front-left shoulder, right flank, left flank
LOBES = ((-0.10, 1.00, 1.90, 0.90), (0.00, -0.45, 2.50, 0.75), (-1.20, -0.70, 2.05, 0.70), (1.30, -0.40, 2.15, 0.75),
         (-1.45, 0.45, 1.60, 0.80), (1.40, 0.40, 1.60, 0.80))
LOBE_FLOOR = 1.10
LOBE_P = 6.0
LOBE_NORM = 0.96       # the soft max overshoots a lone lobe a little
BASE_EVAL = 0.42
NOTCH = dict(x=-0.19, z=1.20, rx=0.55, rz=0.45, depth=0.10)
ROCK_MOTTLE = dict(amp=0.05, scale=0.5, seed=33221)


def _lobe_h(x, y):
    """A soft maximum (p-norm) of the floor and the lobes: swells of one surface with shallow creases between them
    (a hard max folded thin triangles along the crease lines)."""
    acc = LOBE_FLOOR ** LOBE_P
    for lx, ly, lh, sg in LOBES:
        acc += (lh * math.exp(-((x - lx) ** 2 + (y - ly) ** 2) / (2 * sg * sg))) ** LOBE_P
    return acc ** (1.0 / LOBE_P) * LOBE_NORM


def _base_rock(a):
    rng = random.Random(BASE["seed"])
    bm = a.bm
    cx, cy = BASE["c"]
    rx, ry = BASE["r"]
    n = BASE["n"]
    ph = [rng.uniform(0, 2 * math.pi) for _ in range(3)]

    def rmul(th):
        return 1 + 0.05 * math.sin(2 * th + ph[0]) + 0.04 * math.sin(3 * th + ph[1]) + 0.03 * math.sin(5 * th + ph[2])
    rings = []
    for i, (rf, hf, *cn) in enumerate(BASE_RINGS + (BASE_CROWN,)):
        cnt = cn[0] if cn else n
        off = (i % 2) * math.pi / cnt + rng.uniform(-0.1, 0.1)
        ring = []
        for k in range(cnt):
            th = off + 2 * math.pi * k / cnt + rng.uniform(-0.18, 0.18) * (2 * math.pi / cnt)
            r = rf * rmul(th) * (1 + rng.uniform(-0.03, 0.03))
            x, y = math.cos(th) * rx * r, math.sin(th) * ry * r
            if hf <= 0:
                z = BASE["z0"]
            else:
                # the lobe field read at (at most) BASE_EVAL along the same azimuth: each sector is a dome profile
                # whose height follows the lobes (read at the outer rings it fell to a flat plate at the front)
                k = min(1.0, BASE_EVAL / max(rf, 1e-6))
                z = hf * _lobe_h(x * k + cx, y * k + cy) * (1 + rng.uniform(-0.04, 0.04))
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        faces += _zip(bm, r0, r1)
    faces += _fan(bm, rings[0], bm.verts.new((0.0, 0.0, BASE["z0"])))
    top = bm.faces.new(rings[-1])
    faces += list(bmesh.ops.triangulate(bm, faces=[top], quad_method="BEAUTY", ngon_method="BEAUTY")["faces"])
    vs = list({v for f in faces for v in f.verts})
    _place(bm, vs, Matrix.Translation((cx, cy, 0.0)))
    # the notch for sprout A: front-face verts near (x, z) pushed back (+Y)
    for v in vs:
        if v.co.y < cy:
            wx = max(0.0, 1 - abs(v.co.x - NOTCH["x"]) / NOTCH["rx"])
            wz = max(0.0, 1 - abs(v.co.z - NOTCH["z"]) / NOTCH["rz"])
            v.co.y += NOTCH["depth"] * wx * wz
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    a._finish(vs, ROCK)
    return vs


# ---- small rocks (spec 2.1) ------------------------------------------------------------------------------------------
# squat bulged domes (m031 round 2: widest at 0.3 h, a small 3-point crown; never upright slabs)
ROCK_RINGS = ((0.0, 0.92, 7), (0.3, 1.0, 7), (0.62, 0.84, 7), (0.86, 0.5, 6), (1.0, 0.15, 3))
# (label, x, y, w, d, h, bottom z (each its own, so no two bottoms are coplanar), seed)
ROCKS = (
    ("SL", -2.58, 0.15, 1.40, 1.35, 1.45, -0.04, 33401),
    ("SR", 2.52, 0.15, 1.55, 1.45, 1.55, -0.06, 33402),
    ("PL", -1.95, -1.60, 1.00, 0.90, 0.72, -0.07, 33403),
    ("PR", 1.65, -1.64, 1.10, 1.00, 0.85, -0.08, 33404),
    ("BL", -1.50, 2.20, 0.78, 0.72, 0.60, -0.03, 33405),
    ("BR", 1.40, 2.24, 0.72, 0.68, 0.56, -0.09, 33406),
)
ROCK_YAW_JIT = [0.0]
ROCK_INFO = {}


def _small_rock(a, lab, xy=None):
    _, x, y, w, d, h, z0, seed = next(r for r in ROCKS if r[0] == lab)
    if xy is not None:
        x, y = xy
    rng = random.Random(seed)
    yaw = rng.uniform(0, 2 * math.pi) + math.radians(ROCK_YAW_JIT[0])
    pts = _ring_pts(rng, ROCK_RINGS, w / 2, d / 2, h - z0, 0.10)
    vs = _hull(a, pts, ROCK)
    _place(a.bm, vs, Matrix.Translation((x, y, z0)) @ Matrix.Rotation(yaw, 4, "Z"))
    ROCK_INFO[lab] = dict(xy=(round(x, 3), round(y, 3)), size=(w, d, h), faces=len(_faces(vs)))
    return vs


SEAT_ROCKS = {"PL": 0.14, "PR": 0.17, "BL": 0.12, "BR": 0.12}    # label -> overlap with the base (studs)


def _seat_rock(rb, lab):
    """A foot rock's centre pushed out along its azimuth from the base's centre until it overlaps the base's flank
    (ray cast at z 0.25) by SEAT_ROCKS[lab]: every small rock touches the base whatever the base's jitter (a rock
    that missed it by a hair stayed a separate shell). Side rocks keep their layout position (they set the width)."""
    _, x, y, w, d, h, z0, seed = next(r for r in ROCKS if r[0] == lab)
    if lab not in SEAT_ROCKS:
        return (x, y)
    c = Vector((BASE["c"][0], BASE["c"][1], 0.25))
    dv = Vector((x - c.x, y - c.y, 0.0)).normalized()
    hit = None
    p = c + dv * 6.0
    hit = rb.ray_cast(p, -dv)
    if hit[0] is None:
        return (x, y)
    r = (hit[0] - c).length + 0.5 * min(w, d) - SEAT_ROCKS[lab]
    q = c + dv * r
    return (q.x, q.y)


def _paint_rock(a, vs, h, seed, near=None, tint=1.0):
    """ROCK, the ground band toward ROCK_LOW (50 % under 0.12 h, 25 % under 0.26 h); faces within 0.25 of a moss
    clump 25 %. Position only."""
    faces = _faces(vs)
    for f in faces:
        c = f.calc_center_median()
        hf = c.z / h
        t = 0.5 if hf < 0.12 else 0.25 if hf < 0.26 else 0.0
        if not t and near is not None:
            loc = near.find_nearest(c)
            if loc[0] is not None and loc[3] < 0.25:
                t = 0.25
        f.material_index = a._mi(_mix(ROCK, ROCK_LOW, t))
    _mottle(a, faces, ROCK_MOTTLE["amp"], ROCK_MOTTLE["scale"], ROCK_MOTTLE["seed"] + seed, tint=tint)


# ---- parts -----------------------------------------------------------------------------------------------------------
def clump_centre_part(a):
    vs, _ = _clump_local(a, CLUMPS["MC"])
    _paint_clump(a, vs, CLUMPS["MC"]["seed"])


def clump_side_part(a):
    vs, _ = _clump_local(a, CLUMPS["ML"])
    _paint_clump(a, vs, CLUMPS["ML"]["seed"])


def sprout_part(a):
    _sprout(a, "B", base=(0.0, 0.0, STUB[2]))


def base_part(a):
    vs = _base_rock(a)
    _paint_rock(a, vs, 2.5, 0)


def side_rock_part(a):
    vs = _small_rock(a, "SR")
    _paint_rock(a, vs, next(r for r in ROCKS if r[0] == "SR")[5], 2)


# ---- hero ------------------------------------------------------------------------------------------------------------
SPROUT_NUDGE = [Vector()]


def _seat(tree, sp):
    """Where the sprout's ray (from outside, along sp['ray']) first meets the surface; the base sinks sp['sink']."""
    base = Vector(sp["base"]) + SPROUT_NUDGE[0]
    d = Vector(sp["ray"])
    hit = tree.ray_cast(base - d * 6.0, d)
    if hit[0] is None:
        return base
    return hit[0] + d * sp["sink"]


def hero(a):
    ROCK_INFO.clear()
    CLUMP_INFO.clear()
    SPROUT_INFO.clear()
    base = _base_rock(a)
    rb = K.bvh_of(base)
    rocks = {lab: _small_rock(a, lab, _seat_rock(rb, lab)) for lab, *_ in ROCKS}
    clumps = {k: _clump(a, k) for k in ("MC", "ML", "MR")}
    moss_tree = K.bvh_of([v for vs in clumps.values() for v in vs])
    _paint_rock(a, base, 2.5, 0, near=moss_tree)
    for i, (lab, *_r) in enumerate(ROCKS):
        _paint_rock(a, rocks[lab], _r[4], i + 1, near=moss_tree, tint=1.0 + random.Random(i * 7 + 3).uniform(-0.04, 0.04))
    all_tree = K.bvh_of(base + [v for vs in clumps.values() for v in vs])
    for name in ("A", "B"):
        _sprout(a, name, base=_seat(all_tree, SPROUTS[name]))
    trees = {**{k: K.bvh_of(v) for k, v in rocks.items()}, "RB": K.bvh_of(base),
             **{k: K.bvh_of(v) for k, v in clumps.items()}}
    for k in list(ROCK_INFO) + list(CLUMP_INFO):
        info = ROCK_INFO.get(k) or CLUMP_INFO.get(k)
        info["touch"] = [j for j, u in trees.items() if j != k and trees[k].overlap(u)]


NOTES = {
    HERO: "Cave moss boulder (MossBoulderNode): one broad low faceted warm-grey boulder capped at the back and both "
          "sides by three chunky broad-faceted moss clumps (the centre one highest with a flat crown), two bright lime "
          "sprouts (one in a notch on the bare front face, a taller one at the back-right) and six small faceted rocks "
          "round the foot; one closed mesh, flat underside. No VFX",
    CLUMP_P: "Moss Clump (reusable): broad squat faceted moss dome with a flat crown polygon, darker at the bottom",
    SIDE_CLUMP_P: "Moss Clump Side (reusable): faceted ovoid moss lump for draping over a rock's shoulder (tilt it)",
    SPROUT_P: "Sprout (reusable): four chunky diamond-section lime blades with a midrib joined in one small stub",
    BASE_P: "Rock Base (reusable): broad low lobed faceted warm-grey boulder (back hump, front lobe with a notch), "
            "flat underside",
    SIDE_ROCK_P: "Side Rock (reusable): squat faceted warm-grey rock, flat underside",
}


# ---- union, floor cut, cleanup (m031 / m030) -------------------------------------------------------------------------
FINE_MERGE = 0.0          # merge-0 union (m021 round 2): the exact union's output is clean; any weld distance folds hubs
UNION_RETRIES = []


def _union_fine(o, merge=FINE_MERGE):
    """M.union_loose with no post-union weld and a guard against a union that drops most of the mesh (m031). Shells
    are added one at a time in face order (base, rocks, clumps, stubs, blades)."""
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
    bm = bmesh.new()
    bm.from_mesh(o.data)
    if merge > 0:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=merge)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    M.drop_specks(bm, min_area=0.02)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    K.drop_unused_slots(o)
    return len(others)


def _floor_cut(o, z0=0.0):
    """m004.floor_cut with a triangle fill of the cut loops (no n-gon cap). (m031)"""
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


def _polish(o):
    """Quads split, slivers forced open, origin back at the bottom centre, UVs redone (m025 / m031)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = m012._tri_quads(bm)
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
    """Faces on the ground plane (the floor cut's cap): one even ROCK_LOW-free ROCK (close-up 3's flat grey bottom;
    its darker look there is shade, so not painted dark: that would make colour follow facing)."""
    p = m011._Paint(o, off=o[OFF])
    n = 0
    for f in p.bm.faces:
        if all(abs(v.co.z) < 1e-3 for v in f.verts):
            f.material_index = p._mi(ROCK)
            n += 1
    p.done()
    return n


def _sane(o, limit=30.0):
    co = [v.co for v in o.data.vertices]
    ext = max(max(abs(c[i]) for c in co) for i in range(3))
    if ext > limit:
        raise RuntimeError(f"{o.name}: a vertex {ext:.1f} studs from its origin; not unioning it")


def _make(name, fn, role, budget, union=False, ground=False):
    t0 = time.time()
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget, collision="hull",
             tint_var=0.03)
    off = M._build_offset(fn)
    o[OFF] = list(off)
    # booleans at the world origin (m030): a rebuilt object keeps its display slot, where float32 matrix error made
    # the exact unions self-intersect. M.display puts it back.
    o.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    lg = {}
    if union:
        _sane(o)
        lg["shells_merged"] = _union_fine(o)
    if ground:
        lg["cap"] = _floor_cut(o, z0=-off.z)
        o[OFF] = [off.x, off.y, 0.0]
        lg["clean"] = {k: v for k, v in m016._clean_mesh(o, (0.0,)).items() if not isinstance(v, (list, dict))}
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    if ground:
        lg["ground_faces"] = _ground_faces(o)
    lg["bowties"] = M.fix_bowties(o)
    K.drop_unused_slots(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


def _fused_ok(o):
    a = M.audit(o)
    return (a["shells"] == 1 and not a["nonmanifold_edges"] and not a.get("nonmanifold_verts") and
            not a["boundary_edges"] and a["normals"] == "outward"
            and not m016._self_hits(o)[0] and not m012._thin(o, POLISH_LIM)["under"])


def _inverted(o):
    """Faces whose normal points into the solid (a ray from just outside the face, along its normal, that hits the
    mesh an odd number of times). 0 on a clean closed mesh. (m031)"""
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    bad = 0
    for f in bm.faces:
        p = f.calc_center_median() + f.normal * 1e-4
        n, x = 0, p.copy()
        for _ in range(50):
            hit = tree.ray_cast(x, f.normal)
            if hit[0] is None:
                break
            n += 1
            x = hit[0] + f.normal * 1e-5
        bad += n % 2
    bm.free()
    return bad


# ---- stages 5 + 6 (spec section 7) -----------------------------------------------------------------------------------
# Stage 5: nothing. The sheet shows sunlit moss on grey rock: no emissive key, no light (decision 7; WorldModeling 9:
# cave moss gets its visibility from shape and placed lighting, not emission).
# Stage 6: nothing. The sheet shows no glow, spores, dust or sparkle (decision 7).


# ---- build -----------------------------------------------------------------------------------------------------------
PARTS = ((CLUMP_P, clump_centre_part, False, False), (SIDE_CLUMP_P, clump_side_part, False, False),
         (SPROUT_P, sprout_part, True, False), (BASE_P, base_part, False, True),
         (SIDE_ROCK_P, side_rock_part, False, True))
TARGET_SIZE = ((6.4, 0.3), (4.75, 0.35), (3.9, 0.2))
HERO_TRIES = 4
HERO_YAW_STEP = 13.0


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith("_m033_"):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m033_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith(("_m033", "_probe", "T_Calib",
                                                                                 "MossBoulder"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def _try_setup(attempt):
    ROCK_YAW_JIT[0] = attempt * HERO_YAW_STEP
    SPROUT_NUDGE[0] = Vector((0.013, -0.011, 0.007)) * attempt


def build(render=True, parts=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    UNION_RETRIES.clear()
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn, union, ground in PARTS:
            for attempt in range(HERO_TRIES if union else 1):
                _try_setup(attempt)
                objs[name], log[name] = _make(name, fn, "part", 1000, union=union, ground=ground)
                if not union or _fused_ok(objs[name]):
                    break
            log[name]["attempt"] = attempt
    # the hero guard: a rock grazing another piece can leave a sliver pair after the union; then every small rock
    # turns HERO_YAW_STEP degrees about its own axis, the sprouts shift a hair, and the hero is rebuilt
    for attempt in range(HERO_TRIES):
        _try_setup(attempt)
        h, log["hero"] = _make(HERO, hero, "hero", 4000, union=True, ground=True)
        if _fused_ok(h):
            break
    log["hero"]["attempt"] = attempt if _fused_ok(h) else -1
    _try_setup(0)
    log["clumps"] = {k: dict(v) for k, v in CLUMP_INFO.items()}
    log["rocks"] = {k: dict(v) for k, v in ROCK_INFO.items()}
    log["sprouts"] = {k: dict(v) for k, v in SPROUT_INFO.items()}
    log["union_retries"] = list(UNION_RETRIES)
    _cleanup_tmp()
    order = [h] + [objs[n] for n, *_ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    _spec()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    audits = [M.audit(o) for o in order]
    self_hits = {o.name: m016._self_hits(o)[0] for o in order}
    thin = {o.name: m012._thin(o, POLISH_LIM) for o in order}
    inverted = {o.name: _inverted(o) for o in order}
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
        if inverted[o.name]:
            problems.append(f"{o.name}: {inverted[o.name]} inverted faces")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 7: none)")
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts")} for au in audits],
           "thin": thin, "self_hits": self_hits, "inverted": inverted, "log": log, "problems": problems,
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "uv": {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped",
                                                                            "min_gap", "border", "density",
                                                                            "stretch_conformal_p95")}
                  for o in order}}
    out["build_s"] = round(time.time() - t0, 1)
    if render:
        out["views"] = render_views(order)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders ---------------------------------------------------------------------------------------------------------
# the sheet's comparison cameras (decision 9): front (0, 12) for the front and f34 cells (and flipped for the r34);
# side (90, 12), rear (180, 12) and top (0, 75) judged by shares
SHEET_VIEWS = {"front_sheet": (0, 12), "side_sheet": (90, 12), "rear_sheet": (180, 12), "top_sheet": (0, 75)}
SHEET_LENS = 3.0        # the sheet's cells are near-orthographic: the *_sheet shots use a 3x longer lens (M018/M020)
PARTS_SHOT = (-20, 20)


def _long_lens(kit):
    """render_group with a long lens and the studio floor hidden for the *_sheet shots. (m031)"""
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


def _part_matrix(o):
    return Matrix.Translation(Vector(o[OFF]))


def _exploded(objs):
    """Copies of the parts laid out like the sheet's Exploded Construction: the base and side rocks at the bottom,
    the three clumps above (the side clump tilted at the left and, mirrored, at the right), three sprouts on top."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []

    def put(tag, part, m):
        c = bpy.data.objects.new(f"_m033_expl_{tag}", by[part].data)
        coll.objects.link(c)
        c.matrix_world = m
        shown.append(c)
    x0 = objs[0].location.x + 40
    o0 = Matrix.Translation((x0, objs[0].location.y, 0))
    put("base", BASE_P, o0)
    put("rock_r", SIDE_ROCK_P, o0 @ Matrix.Translation((4.3, -0.4, 0)) @ Matrix.Diagonal((0.8, 0.8, 0.8, 1)))
    put("rock_l", SIDE_ROCK_P, o0 @ Matrix.Translation((-4.2, -0.3, 0)) @ Matrix.Rotation(1.3, 4, "Z")
        @ Matrix.Diagonal((0.85, 0.85, 0.75, 1)))
    put("clump_c", CLUMP_P, o0 @ Matrix.Translation((0.0, 0.3, 3.6)))
    put("clump_l", SIDE_CLUMP_P, o0 @ Matrix.Translation((-3.3, 0.0, 3.0)) @ Matrix.Rotation(math.radians(-22), 4, "Y"))
    put("clump_r", SIDE_CLUMP_P, o0 @ Matrix.Translation((3.3, 0.0, 3.0)) @ Matrix.Rotation(math.radians(22), 4, "Y")
        @ Matrix.Diagonal((-0.92, 0.92, 0.92, 1)))
    for i, x in enumerate((-2.0, 0.0, 2.0)):
        put(f"sprout{i}", SPROUT_P, o0 @ Matrix.Translation((x, 0.2, 6.0 - abs(x) * 0.25))
            @ Matrix.Rotation(i * 1.7, 4, "Z") @ Matrix.Diagonal((0.85, 0.85, 0.85, 1)))
    bpy.context.view_layer.update()
    return shown


def render_close(objs, path, az, el, centre, radius):
    """A close-up from (az, el), framed on a sphere (centre, radius) (m023 / m031)."""
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
            extra["exploded"] = (shown, -8, 14)
        for o in objs[1:]:
            extra["part_" + o.name.replace("MossBoulder", "").lower()] = ([o], *PARTS_SHOT)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            sheet = M.views(NUM, [h], extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet}
        if close:
            d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
            off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
            sb = Vector(SPROUT_INFO.get("B", {}).get("base", SPROUTS["B"]["base"]))
            # close-up 1 (Sprout Junction): sprout B's blades meeting the moss
            out["sprout_cu"] = render_close([h], f"{d}/sprout_cu.png", -15, 15, off @ (sb + Vector((0, 0, 0.5))), 1.0)
            # close-up 2 (Rock to Moss Interface): the right clump on the base with the side rock and pebble
            out["rockmoss_cu"] = render_close([h], f"{d}/rockmoss_cu.png", 20, 10, off @ Vector((2.1, -0.6, 1.2)), 1.4)
            # close-up 3 (Underside View): the flat floor-cut base from below
            out["under_cu"] = render_close([h], f"{d}/under_cu.png", -20, -35, off @ Vector((0.0, 0.2, 0.8)), 3.0)
        return out
    finally:
        for o in shown:
            bpy.data.objects.remove(o, do_unlink=True)
        M.display(NUM, objs, TITLE)


def preview(names=("front_sheet", "side_sheet", "rear_sheet", "top_sheet"), vfx=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = _long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig


def hero_only():
    """Rebuild just the hero (tuning loop): returns its audit."""
    M.coll(NUM, TITLE)
    palette()
    for attempt in range(HERO_TRIES):
        _try_setup(attempt)
        h, lg = _make(HERO, hero, "hero", 4000, union=True, ground=True)
        if _fused_ok(h):
            break
    _try_setup(0)
    lg["attempt"] = attempt
    _spec()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, *_ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals")}, "log": lg,
            "self_hits": m016._self_hits(h)[0], "thin": m012._thin(h, POLISH_LIM)["under"],
            "clumps": dict(CLUMP_INFO), "sprouts": dict(SPROUT_INFO), "rocks": dict(ROCK_INFO)}
