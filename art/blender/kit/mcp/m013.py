"""013 Sulfur (references/013.png): three big chamfered blocks of lemon-yellow sulfur and a small nugget on a flat
stack of three horizontal rock strata (stepped ledges, dark undercut grooves), seven small faceted rocks round the foot.

    import importlib, kit_models, m011, m012, m013; importlib.reload(kit_models); importlib.reload(m013); m013.build()

Parts as on the sheet's exploded view, each built by its own function (studs; front -Y, ground z = 0). The R02 kit
sheet owns SulfurChunk / SulfurBaseRock, hence SulfurBlock / SulfurFootRock:
- SulfurBlock (block): the Sulfur Chunk, reusable. A box with every edge broadly chamfered (BEVEL of each side, one
  segment) and each corner cut by a triangle: the hull of 24 corner-chamfer points, corners shifted as groups (broad
  side jitter, the bottom kept flat) plus a gentle bulge point on each side face and a short ridge on top, so each big
  face breaks into a few nearly coplanar planes. Built at its own origin.
- SulfurHostTop (host_top): Host Rock (Top). The thickest stratum (the shelf, 1.8-3.0) with a raised back-left terrace
  (a slab unioned on, its top tilted up towards the back: a 0.5 step at the front rising to 0.7 behind, with its own
  chamfer) and a rock knob at the right end, behind the brick.
- SulfurHostBase (host_base): Host Rock (Base), the sheet's two lower strata fused: the base upper slab and the
  plinth under it, a dark undercut groove between them.
- SulfurFootRock (foot_rock): the Base Rock, reusable. A squat faceted dome with a flat bottom.
Every stratum is slab(): a lofted lozenge of broad straight wall facets (superellipse outline, broad sector jitter),
a top chamfer band, a near-vertical wall and an undercut chamfer at the bottom (the dark groove at every seam), flat
caps fanned from their centres.

The hero is pasted together from the finished part meshes (m011._paste; the blocks and the foot rocks are scaled,
turned copies of their parts) and unioned into one closed shell, floor-cut flat at the ground.
The builders give one placeholder key per region (sulfur, host = top slab, host dark = base strata, base = foot
rocks); stage 4's colour() then grades every finished mesh by position fields (see "stage 4" below).
See M013_spec.md ("Study (2a)" and "Stage 1 - Modelling").
"""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

import kit_mcp as K
import kit_models as M
import m004
import m011
import m012

NUM, TITLE, SHEET = 13, "Sulfur", "M013"
SULFUR, SULFUR_SHADOW = "m013_sulfur", "m013_sulfur_shadow"
HOST, HOST_DARK, BASE = "m013_host", "m013_host_dark", "m013_base"

# stage 3 UVs as on M011 / M012: Smart UV islands made seams, re-unwrapped angle-based, exact 0.008 margin; min_angle
# keeps 45 degree islands on every object (as M009), so smart_uv never drops the angle to more, smaller islands
UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
# Stage 3: the island angle per object, whichever stretched less (uv_stats' worst conformal stretch, 40 against 45):
# the hero 1.035 / 1.234 (at 45 one fold needed a cut and a 6 degree corner change stayed), the base strata
# 1.000 / 1.041; the top slab is better at 45 (1.021 / 1.081), the block and foot rock equal (45 keeps fewer islands).
UV_ANGLE = {"Sulfur": 40.0, "SulfurHostBase": 40.0}


def _uv(o):
    a = UV_ANGLE.get(o.name, UV["angle"])
    return dict(UV, angle=a, min_angle=a)
POLISH_LIM = 5.0       # no corner under this many degrees on any part or the hero


SULFUR_LIGHT, HOST_COOL = "m013_sulfur_light", "m013_host_cool"
SUL_ROUGH, ROCK_ROUGH = 0.58, 0.92
SUL_SPEC = 0.3          # Specular IOR Level on every sulfur key (waxy matte; flintkit's 0.5 glints lemon-white)


def palette():
    # stage 4, two passes (targets, measurements and method in M013_spec.md, "Stage 4"). Sheet swatches: Sulfur
    # #FEE04D, Sulfur Shadow #C4B145, Host Rock #988F8D, Base Rock #6F625C.
    # 1. calibrate() on the test dome against the sheet's rendered medians (TARGETS) gave sulfur #B4A420, light
    #    #BBAE3A, shadow #97871B, host #736B6B, cool #6A676B, dark #595050, base #6E6464 (each rendered on the dome
    #    within 2 levels of its target).
    # 2. On the hero those rendered 1.3-1.4x too dark in linear light (the dome's top faces the sun; the hero's walls
    #    and block sides don't), so each key was corrected in linear light by sheet / hero over the sheet's regions in
    #    the front three-quarter, front, side and top views (the rear is lit by the fill only, so it is reported, not
    #    fitted), three rounds. The shadow key took only part of its gain (the darkest sulfur is the studio's shade on
    #    the down-facing bevels, which paint barely moves) and stays a little darker and more olive than the body.
    # 3. Verifier round 1 (on the reshaped stack): the sulfur shade quartile was 20-40 levels dark and the lit sides
    #    mustard (sat 0.74 against 0.61), the front three-quarter's lower rock band 12 levels light. Re-fitted on the
    #    new shape: a brighter, bluer (paler) body, a shadow key lifted with it (lower contrast across the sulfur
    #    keys), a paler light key, host dark x0.77 in linear and the base upper 50 % towards it (was 25 %).
    K.set_colour(SULFUR, "#D3C03A", rough=SUL_ROUGH)           # was #C8B221
    K.set_colour(SULFUR_LIGHT, "#C9C462", rough=SUL_ROUGH)     # was #C2C155; the crest band
    K.set_colour(SULFUR_SHADOW, "#D0B53A", rough=SUL_ROUGH)    # was #C3A92F
    K.set_colour(HOST, "#857976", rough=ROCK_ROUGH)
    K.set_colour(HOST_COOL, "#7B7576", rough=ROCK_ROUGH)
    K.set_colour(HOST_DARK, "#443D3D", rough=ROCK_ROUGH)       # was #4E4645
    K.set_colour(BASE, "#786D70", rough=ROCK_ROUGH)
    _sulfur_spec()


def _sulfur_spec():
    """SUL_SPEC on every sulfur material, the in-between keys too (flintkit makes new keys at specular 0.5)."""
    for m in bpy.data.materials:
        if m.name.startswith("FB_" + SULFUR) and m.node_tree:
            b = m.node_tree.nodes.get("Principled BSDF")
            if b and "Specular IOR Level" in b.inputs:
                b.inputs["Specular IOR Level"].default_value = SUL_SPEC


# calibration targets: the sheet's rendered medians (M013_spec.md §5.2 / §5.5), not the swatches. key -> (sRGB, kind)
TARGETS = {SULFUR: ((0xF0, 0xD2, 0x30), "vivid"), SULFUR_LIGHT: ((0xF8, 0xE0, 0x4A), "vivid"),
           SULFUR_SHADOW: ((0xC8, 0xAC, 0x2A), "vivid"), HOST: ((0x9B, 0x8B, 0x84), "stone"),
           HOST_COOL: ((0x8E, 0x85, 0x84), "stone"), HOST_DARK: ((0x77, 0x68, 0x62), "stone"),
           BASE: ((0x94, 0x81, 0x7B), "stone")}


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS), as m009: stone keys sampled unfiltered (the test box lies wholly
    on the dome; K.sample's sat < 0.18 stone filter drops warm rock), the sulfur keys at SUL_SPEC every round.
    Returns {key: (hex, rendered)}; the orphaned test-dome meshes are purged."""
    keys = keys or list(TARGETS)
    set0, sample0 = K.set_colour, K.sample

    def set_colour(key, hexcol, **kw):
        set0(key, hexcol, **kw)
        _sulfur_spec()

    def sample(src, box, kind="green"):
        return M.sample(src, box, "all", paper=(255, 253, 240), tol=6) if kind == "stone" else \
            sample0(src, box, kind)
    K.set_colour, K.sample = set_colour, sample
    try:
        for k in keys:
            K.fk().material(k)
        _sulfur_spec()
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        K.set_colour, K.sample = set0, sample0
        _drop_calib()


def _drop_calib():
    """K.calibrate removes its test dome object but not its mesh: purge the orphan T_Calib meshes carrying only this
    model's keys."""
    gone = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")
            and all(x is None or x.name.startswith("FB_m013_") for x in m.materials)]
    for m in gone:
        bpy.data.meshes.remove(m)
    return len(gone)


# ---- strata ---------------------------------------------------------------------------------------------------------
# A stratum's section (studs): the undercut (bottom ring drawn in UNDER, the wall reached UNDER_H above the bottom),
# the wall, the top chamfer band (top ring drawn in CHAMFER, the band CHAMFER_H tall: about 40 degrees).
UNDER, UNDER_H = 0.3, 0.25
CHAMFER, CHAMFER_H = 0.36, 0.3
WALL_TILT = 0.08        # the wall rings' heights wander this much per point (each wall facet tilts a few degrees)
WALL_IN_OUT = 0.1       # ... and their plan positions this much in or out

# (centre x, y, plan w, d, bottom z, top z, yaw deg, points per ring, superellipse exponent, seed)
# The three strata are offset from each other (round 1: near-concentric outlines read as one banded tub): the top
# slab is pushed forward and right with a front-right lobe (the sheet's overhang over the set-back plinth at the
# right), the base upper sits further left (its end shows under the top slab at the left), the plinth sticks out at
# the front left.
# Round 2: the stack is 0.35 lower than the spec's first layout (shelf top 2.8, terrace 3.15) and the blocks taller:
# measured against the sheet at the same elevation the sulfur's lowest point sat at 0.49 H (sheet 0.38) and its share
# of the silhouette was 0.37 (sheet 0.46).
# Stage 2: the terrace's bottom went 2.6 -> 2.5. At 2.6 its lower wall ring (2.72-2.81) straddled the shelf top (2.8):
# a ring vert 0.006 above the shelf plane left a 3.6 degree needle on the shelf top that no flip or collapse could
# take. At 2.5 the ring (2.64-2.75) is buried in the shelf; the visible step (2.8 -> 3.15) moves under 0.04.
# Verifier round 1 (stage 1 fixes): the strata thicknesses were inverted - a thin top plate (0.8) with a sharp lip on
# two thick lower strata; on the sheet the front-left seams sit at 0.18 H and 0.35 H with the rock top at 0.55-0.60 H,
# so the top slab is the thickest layer. Now plinth 0-1.0, base upper 0.95-1.9, top slab 1.8-3.0 (a 0.65 near-vertical
# wall band under its chamfer). The terrace rises to 3.6 at its centre and its top tilts up towards the back
# (TERRACE_RISE: about 3.5 at its front edge, 3.7 at the back), so the back rock rises between the blocks in the rear
# view as on the sheet (0.59 H there; ours topped out at 3.15).
# (The terrace's lower wall ring, 2.67-2.83, stays buried under the shelf top 3.0: stage 2's note on the straddling
# ring at 2.6 / 2.8.)
SHELF = (0.4, -0.3, 9.6, 7.3, 1.8, 3.0, -10.0, 16, 2.6, 13001)
TERRACE = (-0.65, 1.0, 7.1, 4.8, 2.5, 3.6, -8.0, 14, 2.6, 13002)   # wider to the right: holds the tall block
TERRACE_RISE = (82.0, 0.05)     # top tilt: direction (deg in plan, towards the back) and rise per stud
BASE_UPPER = (-0.25, 0.25, 9.4, 7.5, 0.95, 1.9, 5.0, 16, 2.6, 13004)
PLINTH = (-0.4, 0.05, 9.1, 7.7, 0.0, 1.0, -3.0, 16, 3.0, 13005)
LOBES = {13001: ((-28.0, 0.07),), 13005: ((215.0, 0.05),)}    # seed -> (local angle deg, push fraction)
# the right-end knob: a faceted rock dome sunk into the shelf behind the brick
# (round 3: 2.4 x 2.5 x 1.0 stood as a big boulder in front of the tall block in the side view; the spec's 2.0 x 2.2;
# verifier round 1: lifted with the thicker top slab, top 3.6)
KNOB = dict(loc=(4.15, 0.75, 2.55), size=(2.0, 2.2, 1.05), seed=13003, rot=0.4,
            rings=[(0.0, 0.9, 7), (0.35, 1.0, 7), (0.7, 0.82, 6), (1.0, 0.4, 4)])


def _outline(cx, cy, w, d, yaw, n, expo, seed):
    """A closed, counter-clockwise plan outline: a superellipse lozenge of n points (broad straight segments), with
    broad sector jitter (a smooth function of the angle, never per point), a little spacing jitter and, where LOBES
    names this seed, a broad lobe pushed out (local angle in degrees, fraction of the radius)."""
    rng = random.Random(seed)
    a1, a2, a3 = (rng.uniform(0, 2 * math.pi) for _ in range(3))
    rot = Matrix.Rotation(math.radians(yaw), 2)
    out = []
    for k in range(n):
        th = 2 * math.pi * (k + rng.uniform(-0.15, 0.15)) / n
        c, s = math.cos(th), math.sin(th)
        x = math.copysign(abs(c) ** (2 / expo), c) * w / 2
        y = math.copysign(abs(s) ** (2 / expo), s) * d / 2
        j = 1.0 + 0.03 * math.sin(th + a1) + 0.015 * math.sin(2 * th + a2) + 0.01 * math.sin(3 * th + a3)
        for ang, amt in LOBES.get(seed, ()):
            j += amt * max(0.0, math.cos(th - math.radians(ang))) ** 3
        out.append(rot @ Vector((x * j, y * j)) + Vector((cx, cy)))
    return out


def _push(pts, ds):
    """Each outline point moved ds[i] outwards along its normal (from its neighbours)."""
    n = len(pts)
    out = []
    for i, p in enumerate(pts):
        t = (pts[(i + 1) % n] - pts[i - 1]).normalized()
        out.append(p + Vector((t.y, -t.x)) * ds[i])
    return out


def _inset(pts, d):
    """Each outline point moved d inwards along its outward normal (from its neighbours)."""
    n = len(pts)
    out = []
    for i, p in enumerate(pts):
        t = (pts[(i + 1) % n] - pts[i - 1]).normalized()
        out.append(p - Vector((t.y, -t.x)) * d)
    return out


def _loft(a, rings, mat, cap_lift=(0.0, 0.0)):
    """Quads between rings of equal length (bottom ring first), each cap fanned from its centre (lifted by
    cap_lift = (bottom, top) along -z / +z). Quads are split along the diagonal that keeps the larger corner.
    Returns the verts."""
    bm = a.bm
    vr = [[bm.verts.new(p) for p in r] for r in rings]
    n = len(rings[0])
    faces = []
    for k in range(len(vr) - 1):
        for i in range(n):
            j = (i + 1) % n
            q = (vr[k][i], vr[k][j], vr[k + 1][j], vr[k + 1][i])
            ac = min(m011._min_angle([q[0].co, q[1].co, q[2].co]), m011._min_angle([q[0].co, q[2].co, q[3].co]))
            bd = min(m011._min_angle([q[0].co, q[1].co, q[3].co]), m011._min_angle([q[1].co, q[2].co, q[3].co]))
            if ac >= bd:
                faces += [bm.faces.new((q[0], q[1], q[2])), bm.faces.new((q[0], q[2], q[3]))]
            else:
                faces += [bm.faces.new((q[0], q[1], q[3])), bm.faces.new((q[1], q[2], q[3]))]
    extra = []
    for ring, lift in ((vr[0], -cap_lift[0]), (vr[-1], cap_lift[1])):
        c = sum((v.co for v in ring), Vector()) / n
        cv = bm.verts.new(c + Vector((0, 0, lift)))
        extra.append(cv)
        for i in range(n):
            faces.append(bm.faces.new((ring[i], ring[(i + 1) % n], cv)))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    vs = [v for r in vr for v in r] + extra
    a._finish(vs, mat)
    return vs


def slab(a, spec, mat, under=UNDER, chamfer=CHAMFER, cap_lift=(0.0, 0.0), rise=None):
    """One stratum (see the section constants): a lofted lozenge, flat bottom, flat top. rise = (plan direction in
    degrees, rise per stud) tilts the top plane (and the wall's upper ring with it) about the slab's centre; the top
    stays one plane, z1 at the centre."""
    cx, cy, w, d, z0, z1, yaw, n, expo, seed = spec
    rng = random.Random(seed + 77)
    out = _outline(cx, cy, w, d, yaw, n, expo, seed)
    h = z1 - z0
    uh, ch = min(UNDER_H, 0.3 * h), min(CHAMFER_H, 0.35 * h)

    def dz(p):
        if not rise:
            return 0.0
        t = math.radians(rise[0])
        return rise[1] * ((p.x - cx) * math.cos(t) + (p.y - cy) * math.sin(t))
    # the wall's two rings wander in and out independently (WALL_IN_OUT), so each wall facet leans its own way
    lo_xy = _push(out, [rng.uniform(-WALL_IN_OUT, WALL_IN_OUT) for _ in out])
    hi_xy = _push(out, [rng.uniform(-WALL_IN_OUT, WALL_IN_OUT) for _ in out])
    lo = [p.to_3d() + Vector((0, 0, z0 + uh + rng.uniform(-WALL_TILT, WALL_TILT) * min(1.0, h)))
          for p in lo_xy]
    hi = [p.to_3d() + Vector((0, 0, z1 - ch + dz(p) + rng.uniform(-WALL_TILT, WALL_TILT) * min(1.0, h)))
          for p in hi_xy]
    rings = [[p.to_3d() + Vector((0, 0, z0)) for p in _inset(out, under)], lo, hi,
             [p.to_3d() + Vector((0, 0, z1 + dz(p))) for p in _inset(out, chamfer)]]
    return _loft(a, rings, mat, cap_lift)


def terrace_z(x, y):
    """The terrace's top height at (x, y) (build frame)."""
    t = math.radians(TERRACE_RISE[0])
    return TERRACE[5] + TERRACE_RISE[1] * ((x - TERRACE[0]) * math.cos(t) + (y - TERRACE[1]) * math.sin(t))


def host_top(a):
    """Host Rock (Top): the shelf, the raised back-left terrace and the right-end knob (three closed slabs; build()
    unions them)."""
    slab(a, SHELF, HOST)
    slab(a, TERRACE, HOST, rise=TERRACE_RISE)
    K.hull_rock(a, KNOB["size"], loc=KNOB["loc"], seed=KNOB["seed"], mat=HOST, rings=KNOB["rings"], jitter=0.06,
                rot=KNOB["rot"], keep_bottom=True)


def host_base(a):
    """Host Rock (Base): the base upper slab on the plinth (two closed slabs; build() unions them)."""
    slab(a, BASE_UPPER, HOST_DARK)
    slab(a, PLINTH, HOST_DARK, under=0.35)


# ---- sulfur block ---------------------------------------------------------------------------------------------------
# verifier round 1: the blocks read as faceted gems - the bevel 0.22 -> 0.15 of each side and the bulges 7 -> 4
# (sides) / 3 (top ridge) degrees, so the big faces read flat like the sheet's brick
BLOCK = dict(w=3.8, d=3.0, h=3.2, bevel=0.15, jitter=0.04, bulge=4.0, bulge_top=3.0, seed=13011)


def block(a):
    """Sulfur Chunk: a broadly chamfered block, bottom centre at the origin."""
    w, d, h, b = BLOCK["w"], BLOCK["d"], BLOCK["h"], BLOCK["bevel"]
    rng = random.Random(BLOCK["seed"])
    bx, by, bz = b * w, b * d, b * h
    jt = BLOCK["jitter"]
    pts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (0, 1):
                X, Y, Z = sx * w / 2, sy * d / 2, sz * h
                iz = 1 if sz == 0 else -1
                # broad side jitter: the corner's three points move together (the bottom stays flat)
                j = Vector((rng.uniform(-jt, jt) * w, rng.uniform(-jt, jt) * d, rng.uniform(-jt, jt) * h * sz))
                for p in ((X, Y - sy * by, Z + iz * bz), (X - sx * bx, Y, Z + iz * bz), (X - sx * bx, Y - sy * by, Z)):
                    pts.append(Vector(p) + j)
    # gentle bulges: one point on each side face (off centre), a short ridge along the top's long axis
    t = math.tan(math.radians(BLOCK["bulge"]))
    fy, fx, fz = d / 2 - by, w / 2 - bx, h / 2 - bz        # half-sizes of the flat faces
    # (round 2: one bulge per side face left the faces reading as single flat planes; two, at different heights
    # and pushes, break each into 3-4 planes as on the sheet)
    for sx in (-1, 1):
        for s in (-1, 1):
            u, v = (s * 0.4 + rng.uniform(-0.1, 0.1)) * fy, rng.uniform(-0.35, 0.35) * fz
            pts.append(Vector((sx * (w / 2 + t * rng.uniform(0.6, 1.0) * min(0.6 * fy, fz)), u, h / 2 + v)))
    for sy in (-1, 1):
        for s in (-1, 1):
            u, v = (s * 0.4 + rng.uniform(-0.1, 0.1)) * fx, rng.uniform(-0.35, 0.35) * fz
            pts.append(Vector((u, sy * (d / 2 + t * rng.uniform(0.6, 1.0) * min(0.6 * fx, fz)), h / 2 + v)))
    off = rng.uniform(-0.15, 0.15) * fy
    tt = math.tan(math.radians(BLOCK["bulge_top"]))
    for s in (-1, 1):
        x = s * 0.45 * fx
        pts.append(Vector((x + rng.uniform(-0.1, 0.1) * fx, off, h + tt * min(fy, fx - abs(x)))))
    vs = [a.bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(a.bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    faces = K.faces_of(vs)
    bmesh.ops.dissolve_limit(a.bm, angle_limit=math.radians(3.0), verts=vs,
                             edges=list({e for f in faces for e in f.edges}))
    vs = [v for v in vs if v.is_valid]
    BLOCK["planes"] = len(K.faces_of(vs))
    faces = K.faces_of(vs)
    bmesh.ops.triangulate(a.bm, faces=[f for f in faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
    # one placeholder key; stage 4 grades the olive shadow by position fields (a height band placed here tripped
    # K.check's facing test: the bottom row faces down)
    a._finish(vs, SULFUR)
    return vs


# ---- foot rock ------------------------------------------------------------------------------------------------------
FOOT = dict(size=(2.2, 1.9, 1.5), seed=13031)
# round 1: the draft's rings (top ring 0.25, 3 points) peaked the rocks into pointed pebbles; the sheet's are squat
# domes with a small flat-ish pentagon top
FOOT_RINGS = [(0.0, 0.92, 6), (0.38, 1.0, 6), (0.74, 0.78, 6), (1.0, 0.42, 5)]


def foot_rock(a):
    """Base Rock: a squat faceted dome, flat bottom, bottom centre at the origin."""
    return K.hull_rock(a, FOOT["size"], seed=FOOT["seed"], mat=BASE, rings=FOOT_RINGS, jitter=0.07,
                       keep_bottom=True)


# ---- hero layout (build frame) --------------------------------------------------------------------------------------
# blocks: name -> (centre x, y, bottom z, size w, d, h, yaw deg, tilt about x, y deg, turn the part 90 deg, mirror x)
# Each block's bottom sits 0.1 into its slab top (terrace 3.15, shelf 2.8), so its lower bevel row shows. Round 2:
# taller blocks on the lower stack (the top stays at 6.95), the brick and left chunk 0.25 further left (the front
# view's sulfur span was 0.16-0.93 of W; sheet 0.13-0.90).
# Verifier round 1 (stage 1 fixes), on the thicker top slab (shelf top 3.0, terrace 3.5-3.7):
# - the tall block read cube- or ball-like (4.0 x 3.1 x 3.9; the sheet's chunks are W : H 1.19-1.43): now 4.2 wide,
#   3.43 tall, on the terrace (its top stays 6.95);
# - the brick sat 1.1-1.5 back from the shelf's front edge; on the sheet its bottom sits on the slab's front chamfer:
#   centre y -1.2 -> -1.85, bottom 2.85 (0.15 into the shelf top), a little lower and longer (W : H 1.66);
# - the nugget against the brick's front-right foot at (3.7, -3.2), on the front chamfer;
# - the left chunk a little lower (its top 0.8 of the tall block's, as the sheet's front view).
# (measured: at y -1.85 / yaw -12 the brick's left end still stood 0.6 back from the shelf's top edge while its right
# end reached it; at y -2.1 / yaw -6 its front runs along the edge, the right end over the chamfer, and it is 3.2 deep
# so its back still overlaps the tall block's lower front. The nugget then sits off its front-right corner.)
# (then: the shelf's front edge bows forward in the middle, so a turned brick overhung it at one end in the top view;
# nearly square-on (yaw -3) its ends sit on the edge and a narrow strip of shelf shows mid-front. The tall block and
# the brick 0.3 shallower and the tall block 0.25 forward: the top view's sulfur cover was 0.63 (sheet 0.45) and the
# tall block's back showed past the slab from below.)
BLOCKS = {
    "Tall": (0.15, 0.95, 3.52, 4.2, 2.9, 3.43, 15.0, 0.0, 0.0, False, False),
    "Brick": (1.6, -1.95, 2.85, 4.3, 2.9, 2.65, -3.0, 0.0, 0.0, False, True),
    "Left": (-2.25, 0.7, 3.4, 2.7, 2.5, 2.3, 30.0, 0.0, -6.0, True, False),
    "Nugget": (3.85, -3.3, 2.75, 1.05, 0.95, 0.6, 40.0, 0.0, 0.0, True, True),
}
# foot rocks: (centre x, y, size w, d, h, yaw deg); none at the back centre or the front centre (rear / front views).
# Round 1: the spec's spread made the hero 11.1 wide (target 10.4 +- 0.4); the end rocks sit further in.
ROCKS = (
    (-0.9, -3.6, 2.5, 2.1, 1.6, 20.0),      # front centre-left (largest)
    (-3.95, -2.75, 2.2, 1.9, 1.5, -35.0),   # front left
    (3.5, -3.3, 1.9, 1.7, 1.3, 70.0),       # front right
    # right. Stage 2 (verifier round 2): yaw 110 -> 125. At 110 one upper facet grazed the base-upper undercut at
    # about z 1.3, leaving a 3 degree needle in the narrow crevice; _polish's nudge (m012._force_slivers) opened it
    # by pushing a corner through the groove's facing wall: 3 crossing face pairs, 0.2-0.3 deep, at (4.1, 1.6, 1.0)
    # and (4.2, 0.9, 1.1). Turned 15 degrees the rock meets the groove cleanly (no needle there, nothing to nudge);
    # same place, size and hero bounds.
    (4.5, 1.1, 1.7, 1.6, 1.2, 125.0),
    (3.8, 3.1, 1.6, 1.4, 1.0, 160.0),       # back right
    (-2.6, 3.45, 2.0, 1.7, 1.3, 200.0),     # back left
    (-4.35, 2.6, 1.2, 1.0, 0.8, 250.0),     # back-left small
)
ROCK_SINK = 0.1        # the rocks go this far below the ground; the hero's floor cut makes the base one flat plane


def _frame(o):
    """Part mesh coordinates -> the part's build frame (the shared one for the strata, its own for block / rock)."""
    return Matrix.Translation(Vector(o["m013_offset"]))


def _part_dims(o):
    m = _frame(o)
    ps = [m @ v.co for v in o.data.vertices]
    return Vector([max(p[i] for p in ps) - min(p[i] for p in ps) for i in range(3)])


def _block_matrix(name, part):
    x, y, z, w, d, h, yaw, tx, ty, turn, mirror = BLOCKS[name]
    pd = _part_dims(part)
    pre = Matrix.Identity(4)
    if mirror:
        pre = Matrix.Diagonal((-1.0, 1.0, 1.0, 1.0))
    if turn:
        pre = Matrix.Rotation(math.pi / 2, 4, "Z") @ pre
        pd = Vector((pd.y, pd.x, pd.z))
    s = Matrix.Diagonal((w / pd.x, d / pd.y, h / pd.z, 1.0))
    r = (Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Rotation(math.radians(ty), 4, "Y") @
         Matrix.Rotation(math.radians(tx), 4, "X"))
    return Matrix.Translation((x, y, z)) @ r @ s @ pre @ _frame(part)


def _rock_matrix(k, part):
    x, y, w, d, h, yaw = ROCKS[k]
    pd = _part_dims(part)
    return (Matrix.Translation((x, y, -ROCK_SINK)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @
            Matrix.Diagonal((w / pd.x, d / pd.y, (h + ROCK_SINK) / pd.z, 1.0)) @ _frame(part))


def hero(a):
    base = bpy.data.objects["SulfurHostBase"]
    top = bpy.data.objects["SulfurHostTop"]
    blk = bpy.data.objects["SulfurBlock"]
    rock = bpy.data.objects["SulfurFootRock"]
    m011._paste(a, base, _frame(base))
    m011._paste(a, top, _frame(top))
    for name in BLOCKS:
        m011._paste(a, blk, _block_matrix(name, blk))
    for k in range(len(ROCKS)):
        m011._paste(a, rock, _rock_matrix(k, rock))


PARTS = (("SulfurBlock", block), ("SulfurHostTop", host_top), ("SulfurHostBase", host_base),
         ("SulfurFootRock", foot_rock))

NOTES = {
    "Sulfur": "sulfur resource: three big chamfered lemon-yellow sulfur blocks and a small nugget on a flat stack of "
              "three horizontal rock strata (a raised back-left terrace, a lower front-right shelf, a rock knob at "
              "the right end; stepped ledges and dark undercut grooves), seven small faceted rocks round the foot; "
              "one closed mesh, flat base",
    "SulfurBlock": "Sulfur Chunk (reusable): a block with every edge broadly chamfered, faces gently broken, flat "
                   "bottom",
    "SulfurHostTop": "Host Rock (Top): a thick flat lozenge slab, top chamfer band, faceted wall, undercut; a raised "
                     "back-left terrace and a rock knob at the right end",
    "SulfurHostBase": "Host Rock (Base): two fused flat strata (base upper slab on a plinth) with a dark groove "
                      "between",
    "SulfurFootRock": "Base Rock (reusable): small squat faceted rock, flat bottom",
}


# ---- cleanup (as M012's stage 2 passes, with this model's offset key) -----------------------------------------------
def _bottom_centre(o):
    return m012._bottom_centre(o)


def _finish(o):
    """M.finish, then any crumbs, holes or faces under 3 degrees fixed and finish run again; the part's
    build-frame offset follows the re-centring."""
    if "m013_offset" in o:
        o["m013_offset"] = list(Vector(o["m013_offset"]) + _bottom_centre(o))
    res = M.finish(o, union=False, uv=_uv(o))
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
        if "m013_offset" in o:
            o["m013_offset"] = list(Vector(o["m013_offset"]) + _bottom_centre(o))
        res = M.finish(o, union=False, uv=_uv(o))
    return res


def _polish(o):
    """All faces triangles, every corner opened past POLISH_LIM, origin at the bottom centre (offset follows), UVs
    re-made on the final mesh."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = m012._tri_quads(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = m012._force_slivers(o, lim=POLISH_LIM)
    bc = _bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        if "m013_offset" in o:
            o["m013_offset"] = list(Vector(o["m013_offset"]) + bc)
    o.data.update()
    M.smart_uv(o, **_uv(o))
    return {"split": split, "forced": forced, "uv_cut": m012._uv_unfold(o)}


def _dissolve_ears(o):
    """Stage 2: the union can leave an 'ear' where a foot rock's wall grazes the plinth / base-upper groove: a vert
    on only two edges whose two faces are a speck triangle and the n-gon wrapped round it (the hero had one, 0.013
    studs across, at (-1.80, -3.05, 1.15)). m011._clean's two-edge dissolve skips it (one face is a triangle), and
    triangulating the n-gon then clips that same ear a second time: an edge on four faces, which finish's repair
    turned into a pinhole (stage 1 sealed it afterwards with _seal). Dissolving the vert first merges the speck into
    the n-gon (the surface moves under 0.015 studs). Returns the verts dissolved."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    ears = [v for v in bm.verts if len(v.link_edges) == 2 and len(v.link_faces) == 2
            and any(len(f.verts) == 3 for f in v.link_faces)]
    if ears:
        bmesh.ops.dissolve_verts(bm, verts=ears)
        bm.to_mesh(o.data)
    bm.free()
    return len(ears)


def _self_hits(o):
    """Pairs of faces that cross each other without sharing a vertex (as m009._self_hits): interpenetration the
    unions or the cleanup's collapses and nudges can leave. Returns (count, up to 5 pairs with their centres in the
    build frame)."""
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    off = Vector(o.get("m013_offset", (0.0, 0.0, 0.0)))
    pairs = [(a, b) for a, b in tree.overlap(tree)
             if a < b and not set(bm.faces[a].verts) & set(bm.faces[b].verts)]
    where = [(a, b, [round(c, 2) for c in bm.faces[a].calc_center_median() + off]) for a, b in pairs[:5]]
    bm.free()
    return len(pairs), where


def _clean_mesh(o, planes):
    """Union leftovers: union ears, closed pockets, slivers and caps (planes stay flat), last-resort sliver
    collapse."""
    ears = _dissolve_ears(o)
    pockets = m012._drop_inner(o)
    log = m011._clean(o, m011._plane_lock(planes), max_move=m011.CLEAN_MOVE)
    pockets += m012._drop_inner(o)
    log["ears"] = ears
    log["pockets"] = pockets
    log["forced"] = m012._force_slivers(o)
    return log


# flat planes to keep flat in each part's cleanup (build-frame z; the part's bottom is always one)
# (the terrace's top is tilted since verifier round 1, so it is no longer a level plane to lock)
PLANES = {"SulfurHostTop": (SHELF[4], SHELF[5]), "SulfurHostBase": (0.0,)}


def _seats(top):
    """Stage 1 check: how far each block's flat bottom (corners) lies outside the slab top it rests on (studs, 0 if
    inside): its inset bottom footprint in the build frame against the terrace / shelf top outline."""
    def inside(p, poly):
        c = False
        for i in range(len(poly)):
            a, b = poly[i - 1], poly[i]
            if (a.y > p.y) != (b.y > p.y) and p.x < (b.x - a.x) * (p.y - a.y) / (b.y - a.y) + a.x:
                c = not c
        return c

    def dist(p, poly):
        best = 9.0
        for i in range(len(poly)):
            a, b = poly[i - 1], poly[i]
            ab = b - a
            t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
            best = min(best, (p - (a + ab * t)).length)
        return best
    tops = {"terrace": _inset(_outline(*TERRACE[:4], TERRACE[6], *TERRACE[7:]), CHAMFER),
            "shelf": _inset(_outline(*SHELF[:4], SHELF[6], *SHELF[7:]), CHAMFER)}
    blk = bpy.data.objects["SulfurBlock"]
    out = {}
    for name in BLOCKS:
        m = _block_matrix(name, blk)
        z = BLOCKS[name][2]
        poly = tops["terrace"] if z > SHELF[5] + 0.05 else tops["shelf"]
        bot = [m @ v.co for v in blk.data.vertices if (_frame(blk) @ v.co).z < 1e-3]
        worst = max((0.0 if inside(p.to_2d(), poly) else dist(p.to_2d(), poly)) for p in bot) if bot else None
        # how deep the bottom corners sit in the top they rest on (the terrace's top is tilted)
        sink = [(terrace_z(p.x, p.y) if poly is tops["terrace"] else SHELF[5]) - p.z for p in bot]
        # a corner past a terrace's edge hangs over the shelf: how high above the shelf top
        gap = [p.z - SHELF[5] for p in bot if poly is tops["terrace"] and not inside(p.to_2d(), poly)]
        out[name] = {"outside": round(worst, 2) if worst is not None else None,
                     "sink": [round(min(sink), 2), round(max(sink), 2)] if sink else None,
                     "gap_over_shelf": round(max(gap), 2) if gap else 0.0}
    return out


# ---- stage 4: colour regions, graded blends and Tint mottling -------------------------------------------------------
# Run on each finished mesh (after its cleanup and UVs, so no geometry or UV changes), the hero and the parts alike,
# straight after build() made them: a face's region comes from the builder's placeholder key (sulfur / host = top
# slab / host dark = base strata / base = foot rocks). Every field is a position: the shared build frame for the rock,
# each block's own part frame for the sulfur (the hero's blocks are mapped back through _block_matrix, so the part
# and its three copies carry the same grading). No colour is ever chosen by which way a face points.
STEPS = 3               # K.blend's mode="blend": 25 / 50 / 75 % in-between keys
# sulfur, per block: u = height fraction in the block + SUL_NOISE x broad noise + SUL_LATERAL x position along the
# block's long axis (the band edges wander and don't follow face rows). Shadow -> sulfur over SUL_SHADOW_BAND, sulfur
# -> light over SUL_LIGHT_BAND (the crest; the pale lemon itself is the sun's).
SUL_NOISE, SUL_SCALE, SUL_LATERAL, SUL_SEED = 0.12, 0.5, 0.1, 13061
SUL_SHADOW_BAND = (0.0, 0.22)
SUL_LIGHT_BAND = (0.82, 0.97)
# occlusion: distance (studs) from a face to the rock or to another block -> shadow mix: full within the first, 50 %
# at the second, none past the third (the olive crevices between the blocks and the contact row; the part's own
# contact is its flat bottom plane)
SUL_OCC = (0.05, 0.2, 0.45)
# rock: the strata darken downwards (host -> host dark): top slab 0, base upper 50 % (25 % before verifier round 1:
# the front three-quarter's lower band rendered 12 levels light; at 50 % it no longer takes the cool weathering), the
# plinth ramps (z, mix) with
# ROCK_NOISE x broad noise on z; the seams (each stratum's undercut ring, where it sits on the one below) are dark
# grooves: SEAM_DARK within SEAM[0] of the ring, fading out by SEAM[1]
ROCK_NOISE, ROCK_SCALE, ROCK_SEED = 0.12, 0.6, 13062
STRATA_DARK = {"top": 0.0, "upper": 0.5}
# (verifier round 1: the plinth is 1.0 tall now, was 1.15; ramp and split scaled with it)
PLINTH_DARK = ((0.8, 0.5), (0.45, 0.75))
UPPER_Z = 0.97          # host-dark faces above this are the base upper stratum (bottom 0.95), below it the plinth
SEAM, SEAM_DARK = (0.2, 0.5), 1.0
# broad warm <-> cool weathering on the two upper strata (where they are at most 25 % dark): mild, the sheet's rock is
# "clean, solid"
WEATHER = dict(scale=0.2, level=0.45, width=0.5, seed=13063)
# foot rocks: crown (above FOOT_CROWN of the rock's height) 25 % towards host so they blend with the slab walls; the
# ground-contact row (below FOOT_CONTACT) 25 % towards host dark
FOOT_CROWN, FOOT_CONTACT, FOOT_MIX = 0.7, 0.22, 0.25
# Tint: a per-piece level (neighbouring blocks, strata and foot rocks differ slightly) times broad mottling
PIECE_TINT = {"Tall": 1.0, "Brick": 1.02, "Left": 0.97, "Nugget": 1.01, "top": 1.0, "upper": 0.98, "plinth": 0.99,
              "rocks": (1.02, 0.97, 1.0, 1.03, 0.98, 1.01, 0.96)}
MOTTLE = {"rock": dict(amp=0.055, scale=0.45, jitter=0.015, seed=13065),
          "sulfur": dict(amp=0.03, scale=0.9, jitter=0.01, seed=13066)}
# K.check's baked-shading test correlates a face's brightness with its facing. The sulfur passes (hero 0.29, block
# under the gate); the rock strata trip it, waived with the reason (as M011's crystal zoning):
SHADING_OK = {
    "Sulfur": "rock strata colour by stratum and height (top slab host, base upper 25 %, plinth 50-75 % towards the "
              "darker browner Base Rock tone, dark seam grooves): the sheet's exploded base, with no slab over it, "
              "still renders darker than the top slab (#756B68 against #8A7E7C). The upward-facing top slab is the "
              "upper stratum, so the correlation follows the stack, not the light. Rendered strata match the sheet's",
    "SulfurHostBase": "the plinth darkens towards the Base Rock tone by height and the seam groove is dark (see "
                      "Sulfur); it follows the stratum, not the light",
}


def _q(t):
    return round(min(1.0, max(0.0, t)) * (STEPS + 1)) / (STEPS + 1)


def _lerp_ramp(x, pts):
    """Piecewise-linear through (x, y) points sorted by x descending (held flat past the ends)."""
    if x >= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x >= x1:
            return y0 + (y1 - y0) * (x0 - x) / (x0 - x1)
    return pts[-1][1]


class _Inst:
    """One placed copy of a reusable part: build frame -> the part's own frame (bottom centre at the origin), with
    the part's bounds there."""

    def __init__(self, label, inv, part, seed):
        self.label, self.inv = label, inv
        ps = [_frame(part) @ v.co for v in part.data.vertices]
        self.lo = Vector([min(p[i] for p in ps) for i in range(3)])
        self.hi = Vector([max(p[i] for p in ps) for i in range(3)])
        r = random.Random(seed)
        self.noise_off = Vector((r.uniform(0, 50), r.uniform(0, 50), r.uniform(0, 50)))

    def local(self, c):
        return self.inv @ c

    def norm(self, c):
        """Box norm of c in the part's bounds: 1 on the box, < 1 inside."""
        q = self.local(c)
        mid, half = (self.lo + self.hi) / 2, (self.hi - self.lo) / 2
        return max(abs(q[i] - mid[i]) / max(half[i], 1e-6) for i in range(3))

    def u(self, c):
        q = self.local(c)
        return (q.z - self.lo.z) / (self.hi.z - self.lo.z)

    def lateral(self, c):
        q = self.local(c)
        mid, half = (self.lo + self.hi) / 2, (self.hi - self.lo) / 2
        return (q.x - mid.x) / half.x


def _instances(o):
    """The block and foot-rock copies o is made of, as _Inst lists (the parts are one copy of themselves)."""
    blk = bpy.data.objects["SulfurBlock"]
    rock = bpy.data.objects["SulfurFootRock"]
    if o.name == "SulfurBlock":
        return [_Inst("Tall", Matrix.Identity(4), blk, 0)], []
    if o.name == "SulfurFootRock":
        return [], [_Inst(0, Matrix.Identity(4), rock, 0)]
    if o.name != "Sulfur":
        return [], []
    blocks = [_Inst(n, _frame(blk) @ _block_matrix(n, blk).inverted(), blk, i + 1) for i, n in enumerate(BLOCKS)]
    rocks = [_Inst(k, _frame(rock) @ _rock_matrix(k, rock).inverted(), rock, 20 + k) for k in range(len(ROCKS))]
    return blocks, rocks


def _block_bvhs():
    """The hero's four blocks as BVH trees in the build frame (for the block-to-block occlusion)."""
    from mathutils.bvhtree import BVHTree
    blk = bpy.data.objects["SulfurBlock"]
    out = {}
    for n in BLOCKS:
        m = _block_matrix(n, blk)
        out[n] = BVHTree.FromPolygons([m @ v.co for v in blk.data.vertices],
                                      [list(p.vertices) for p in blk.data.polygons])
    return out


def _seam_tree():
    """Points along each stratum's undercut ring where it sits on the one below (the top slab's shelf on the base
    upper, the base upper on the plinth), every 0.05 stud, in the build frame."""
    from mathutils.kdtree import KDTree
    pts = []
    for spec, under in ((SHELF, UNDER), (BASE_UPPER, UNDER)):
        cx, cy, w, d, z0, z1, yaw, n, expo, seed = spec
        ring = _inset(_outline(cx, cy, w, d, yaw, n, expo, seed), under)
        for i in range(len(ring)):
            a, b = ring[i - 1], ring[i]
            k = max(1, int((b - a).length / 0.05))
            pts += [(a + (b - a) * (j / k)).to_3d() + Vector((0, 0, z0)) for j in range(k)]
    kd = KDTree(len(pts))
    for i, p in enumerate(pts):
        kd.insert(p, i)
    kd.balance()
    return kd


def _tint(p, f, level, mottle, c):
    """Tint = the piece's level x broad mottling (K.texture's patches, about 1/scale studs, at position c) x a
    little per-face jitter."""
    from mathutils import noise
    m = MOTTLE[mottle]
    r = random.Random(m["seed"])
    off = Vector((r.uniform(0, 100), r.uniform(0, 100), r.uniform(0, 100)))
    k = level * (1.0 + m["amp"] * 1.6 * noise.noise(c * m["scale"] + off)
                 + random.Random(hash((round(c.x, 3), round(c.y, 3), round(c.z, 3)))).uniform(-m["jitter"],
                                                                                             m["jitter"]))
    for l in f.loops:
        l[p.tint_layer] = (k, k, k, 1.0)


def colour(o):
    """Stage 4 on a freshly built M013 object (hero or part). Returns the face count per key."""
    from mathutils.bvhtree import BVHTree
    p = m011._Paint(o, off=o["m013_offset"])
    blocks, rocks = _instances(o)
    faces = list(p.bm.faces)
    region = {f: p.key(f) for f in faces}
    sul = [f for f in faces if region[f] == SULFUR]
    rock = [f for f in faces if region[f] != SULFUR]
    # occlusion sources: the hero's rock surface and its other blocks; a lone block's contact is its bottom plane
    rock_bvh = None
    if o.name == "Sulfur" and rock:
        vs = [v.co + p.off for v in p.bm.verts]
        idx = {v: i for i, v in enumerate(p.bm.verts)}
        rock_bvh = BVHTree.FromPolygons(vs, [[idx[v] for v in f.verts] for f in rock])
    blk_bvh = _block_bvhs() if o.name == "Sulfur" else {}
    nf_s = K.noise_field(scale=SUL_SCALE, seed=SUL_SEED)
    for f in sul:
        c = p.at(f)
        b = min(blocks, key=lambda i: i.norm(c))
        q = b.local(c)
        v = b.u(c) + SUL_NOISE * nf_s(q + b.noise_off) + SUL_LATERAL * b.lateral(c)
        shade = 1.0 - min(1.0, max(0.0, (v - SUL_SHADOW_BAND[0]) / (SUL_SHADOW_BAND[1] - SUL_SHADOW_BAND[0])))
        if o.name == "Sulfur":
            d = min([rock_bvh.find_nearest(c)[3]] + [t.find_nearest(c)[3] for n, t in blk_bvh.items()
                                                    if n != b.label])
        else:
            d = q.z - b.lo.z
        shade = max(shade, _lerp_ramp(d, [(SUL_OCC[2], 0.0), (SUL_OCC[1], 0.5), (SUL_OCC[0], 1.0)]))
        if _q(shade) > 0:
            key = K.mix_key(SULFUR, SULFUR_SHADOW, _q(shade))
        else:
            key = K.mix_key(SULFUR, SULFUR_LIGHT, _q((v - SUL_LIGHT_BAND[0]) / (SUL_LIGHT_BAND[1] -
                                                                                SUL_LIGHT_BAND[0])))
        f.material_index = p._mi(key)
        _tint(p, f, PIECE_TINT[b.label], "sulfur", q + b.noise_off)
    nf_r = K.noise_field(scale=ROCK_SCALE, seed=ROCK_SEED)
    nf_w = K.noise_field(scale=WEATHER["scale"], seed=WEATHER["seed"])
    seams = _seam_tree() if any(region[f] != BASE for f in rock) else None
    for f in rock:
        c = p.at(f)
        if region[f] == BASE:
            r = min(rocks, key=lambda i: i.norm(c))
            u = r.u(c)
            key = (K.mix_key(BASE, HOST, FOOT_MIX) if u > FOOT_CROWN else
                   K.mix_key(BASE, HOST_DARK, FOOT_MIX) if u < FOOT_CONTACT else BASE)
            f.material_index = p._mi(key)
            _tint(p, f, PIECE_TINT["rocks"][r.label], "rock", c)
            continue
        cls = "top" if region[f] == HOST else "upper" if c.z >= UPPER_Z else "plinth"
        if cls == "plinth":
            td = _lerp_ramp(c.z + ROCK_NOISE * nf_r(c), PLINTH_DARK)
        else:
            td = STRATA_DARK[cls]
        ds = seams.find(c)[2]
        td = max(td, SEAM_DARK * min(1.0, max(0.0, (SEAM[1] - ds) / (SEAM[1] - SEAM[0]))))
        td = _q(td)
        if td <= 0.25 and cls != "plinth":
            tc = _q((nf_w(c) - (WEATHER["level"] - WEATHER["width"] / 2)) / WEATHER["width"])
            key = K.mix_key(HOST, HOST_COOL, tc)
            if td > 0:
                key = K.mix_key(key, HOST_DARK, td)
        else:
            key = K.mix_key(HOST, HOST_DARK, td)
        f.material_index = p._mi(key)
        _tint(p, f, PIECE_TINT[cls], "rock", c)
    counts = {}
    for f in faces:
        counts[p.key(f)] = counts.get(p.key(f), 0) + 1
    p.done()
    _sulfur_spec()
    return counts


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    objs, audits, cleaned = {}, {}, {}
    for name, fn in PARTS:
        o = M.mk(SHEET, name, fn, subject=TITLE, role="part", notes=NOTES[name], budget=1000, collision="hull")
        off = M._build_offset(fn)
        o["m013_offset"] = list(off)
        if name in PLANES:
            M.union_loose(o)
            if name == "SulfurHostBase":
                m004.floor_cut(o, z0=-off.z)
            cleaned[name] = _clean_mesh(o, tuple(z - off.z for z in PLANES[name]))
        _finish(o)
        cleaned.setdefault(name, {})["polish"] = _polish(o)
        objs[name] = o
    h = M.mk(SHEET, "Sulfur", hero, subject=TITLE, role="hero", notes=NOTES["Sulfur"], budget=4000,
             collision="hull")
    hoff = M._build_offset(hero)
    h["m013_offset"] = list(hoff)
    M.union_loose(h)
    m004.floor_cut(h, z0=-hoff.z)
    h["m013_offset"] = list(Vector((hoff.x, hoff.y, 0.0)))
    cleaned["Sulfur"] = _clean_mesh(h, (0.0,))
    _finish(h)
    cleaned["Sulfur"]["polish"] = _polish(h)
    order = [h] + [objs[n] for n, _ in PARTS]
    # stage 4: the hero first (it was pasted from the parts' placeholder keys), then each part, by the same fields
    coloured = {o.name: colour(o) for o in order}
    for o in order:
        if o.name in SHADING_OK:
            o["kit_shading_ok"] = SHADING_OK[o.name]
        elif "kit_shading_ok" in o:
            del o["kit_shading_ok"]
    M.display(NUM, order, TITLE)
    dropped = _drop_unused(order)
    out = {"audit": [{k: M.audit(o)[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges",
                                                     "boundary_edges", "normals", "ngons", "materials")}
                     for o in order],
           "thin": {o.name: m012._thin(o, 3.0) for o in order}, "block_planes": BLOCK.get("planes"),
           "seats": _seats(objs["SulfurHostTop"]), "cleaned": cleaned, "dropped": dropped, "colour": coloured,
           "problems": K.check(order), "shading": {o.name: o.get("kit_baked_shading") for o in order}}
    # stage 2: no face may cross another on any object
    out["self_hits"] = {o.name: _self_hits(o) for o in order}
    out["problems"] += [f"{n}: {c} crossing face pairs {w}" for n, (c, w) in out["self_hits"].items() if c]
    if render:
        out["views"] = render_views(order)
    return out


def _drop_unused(objs):
    names = {o.name for o in objs}
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.split(".")[0] in names]
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m013_")]
    out = {"meshes": len(meshes), "materials": sorted(m.name for m in mats)}
    for m in meshes:
        bpy.data.meshes.remove(m)
    for m in mats:
        bpy.data.materials.remove(m)
    for o in objs:
        if o.data.name != o.name and o.name not in bpy.data.meshes:
            o.data.name = o.name
    return out


# exploded shot, as the sheet lays it out: the plinth stack at the bottom, the top slab lifted over it, three block
# variants (temporary linked copies of the one part, at the hero's tall / left / brick sizes) floating above, a foot
# rock in front. (name, x from the shot's centre, y, z of the bottom)
EXPL_TOP_LIFT = 2.6
EXPL_BLOCKS = (("Tall", 0.3, 0.6, 8.6), ("Left", -3.2, 0.4, 7.5), ("Brick", 3.0, -1.0, 7.1))
EXPL_ROCK = (1.0, -5.6)


def render_views(objs):
    h, blk, top, base, rock = objs
    saved = M.explode(objs[1:], {})
    shown = []
    try:
        x0, y0 = h.location.x + 40, h.location.y
        for o in (top, base):
            t = _frame(o).translation
            o.location = (x0 + t.x, y0 + t.y, t.z + (EXPL_TOP_LIFT if o is top else 0.0))
        rock.location = (x0 + EXPL_ROCK[0], y0 + EXPL_ROCK[1], 0.0)
        blk.location = (x0 + 40, y0, 0.0)        # the part itself is shown on its own below
        for name, dx, dy, z in EXPL_BLOCKS:
            c = bpy.data.objects.new(f"_m013_expl_{name}", blk.data)
            blk.users_collection[0].objects.link(c)
            # the hero's placement of that block, moved to its spot in the shot
            c.matrix_world = (Matrix.Translation(Vector((x0 + dx, y0 + dy, z)) - Vector(BLOCKS[name][:3])) @
                              _block_matrix(name, blk))
            shown.append(c)
        bpy.context.view_layer.update()
        extra = {"front_el11": ([h], 0, 11), "side_el11": ([h], 90, 11), "side_left_el11": ([h], -90, 11),
                 "rear_el11": ([h], 180, 11), "r34_sheet": ([h], 28, 12),
                 "exploded": ([top, base, rock] + shown, -16, 18)}
        for o in objs[1:]:
            extra["part_" + o.name[6:].lower()] = ([o], -25, 18)
        return M.views(NUM, [h], extra=extra)
    finally:
        for c in shown:
            bpy.data.objects.remove(c, do_unlink=True)
        M.restore(saved)
        M.display(NUM, objs, TITLE)
