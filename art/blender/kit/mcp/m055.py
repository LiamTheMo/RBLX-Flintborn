"""055 Fallen Log (references/055.png): a big chunky hollow fallen log lying front to back, built like a barrel of
twelve flat-topped planked staves with dark V grooves, a slight twist and a half-stave step seam at 0.3 of its length.
The front (-Y) end is open and broken: twelve chunky chamfered stave-end blocks, staggered in length, round a round
near-black 12-sided bore. The back (+Y) end is closed by a cut cap (a cracked end-grain disc inside a ring of twelve
chamfered rim blocks). One thick Y-forked branch stub rises from the +X shoulder and leans toward the cap end. About
fifty flat lobed moss leaves in rosettes and hanging chains mat the crest and drape both flanks (lime over a green
under-layer); neutral grey faceted rocks and lime grass tufts line both sides of the base. No glow, no VFX.

    import importlib, kit_models, m055; importlib.reload(kit_models); importlib.reload(m055); m055.build()

Build frame: studs, log axis along Y at x 0, z AXZ, the open end at -Y facing the front camera, +X right (the
branch shoulder), ground z 0 (everything on the ground sinks 0.03-0.04 below it). Every object ends with its origin
at its bbox bottom centre; o["m055_offset"] is that origin in the build frame. Names: W05 owns FallenHollowLog and
every LogAndStump* name, 026 owns FallenSoftwoodLog*, so the names are MossyHollowLog* (spec 8):
- MossyHollowLogShell: the staved shell (one closed shell: outer staves, seam, front annulus, 12-sided bore and its
  dark plug, back face, plank splits) plus the twelve seated stave-end blocks of the broken end.
- MossyHollowLogCutEndCap: the cracked disc (with its centre pip) and the twelve chamfered rim blocks.
- MossyHollowLogBranchStub: the planked Y stub (collar, stem, main prong; the side prong a buried closed shell).
- MossyHollowLogMossClump: the big drape M1 (flat lobed leaves) as it lies on the log.
- MossyHollowLogRock: rock module RK1. MossyHollowLogFoliageClump: tuft T3.
- MossyHollowLog (hero): all of the above plus the other moss clumps, rocks, pebbles and tufts, one object of closed
  shells (no booleans).
Colour (stage 4) is painted by position and role inside the builders (never by facing). Stages 5-6: none (the sheet
shows no glow, light or effect). See M055_spec.md.
"""
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

NUM, TITLE, SHEET = 55, "Fallen Log", "M055"
OFF = "m055_offset"
PFX = "_m055_"
HERO = "MossyHollowLog"
SHELL_P = "MossyHollowLogShell"
CAP_P = "MossyHollowLogCutEndCap"
BRANCH_P = "MossyHollowLogBranchStub"
MOSS_P = "MossyHollowLogMossClump"
ROCK_P = "MossyHollowLogRock"
FOL_P = "MossyHollowLogFoliageClump"

WOOD, WOOD_DEEP, WOOD_CUT, WOOD_END, HOLLOW = "m055_wood", "m055_wood_deep", "m055_wood_cut", "m055_wood_end", \
    "m055_hollow"
LIME, GREEN = "m055_leaf_lime", "m055_leaf_green"
ROCK, ROCK_LIGHT, ROCK_DARK = "m055_rock", "m055_rock_light", "m055_rock_dark"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
BURY = 0.05
BURY_PLACE = 0.03
SINK = 0.04

# key -> (hex, roughness, low specular). Stage 4 (M055_spec.md "Stage 4") writes the calibrated values here.
PALETTE = {
    WOOD: ("#B77136", 0.9, False),
    WOOD_DEEP: ("#3E1700", 0.95, False),
    WOOD_CUT: ("#C87F2A", 0.85, False),
    WOOD_END: ("#B76A28", 0.9, False),
    HOLLOW: ("#010000", 1.0, False),
    LIME: ("#B2C106", 0.85, True),
    GREEN: ("#598732", 0.85, True),
    ROCK: ("#8E9094", 0.85, False),
    ROCK_LIGHT: ("#A0A3A8", 0.85, False),
    ROCK_DARK: ("#6B6D71", 0.9, False),     # B <= G + 4 so the dark mix never reads mauve (was #6A6D74)
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions), K.sample kinds
TARGETS = {WOOD: ((0xB8, 0x6C, 0x34), "brown"), WOOD_DEEP: ((0x50, 0x2A, 0x11), "brown"),
           WOOD_CUT: ((0xE4, 0x8C, 0x35), "brown"), WOOD_END: ((0xCA, 0x70, 0x2E), "brown"),
           HOLLOW: ((0x14, 0x0B, 0x04), "all"), LIME: ((0xCE, 0xDB, 0x09), "vivid"),
           GREEN: ((0x6C, 0xA4, 0x33), "vivid"), ROCK: ((0xB4, 0xB1, 0xAE), "stone"),
           ROCK_LIGHT: ((0xCB, 0xC8, 0xC5), "stone"), ROCK_DARK: ((0x86, 0x85, 0x86), "stone")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m055_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k == "m055_" + tail), None) or \
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
_faces = m033._faces
_mottle = m033._mottle
_band = m047._band


def _zip(bm, A, B, c, u, v):
    """Triangles between two closed rings round centre c in the plane basis (u, v), both ordered by increasing angle,
    walking both by angle from A's first vertex (m047._zip, but ring B is started at its first vertex at or after
    that angle, so rings whose first vertices straddle the start never wrap a triangle across the middle)."""
    def ang(p):
        q = p.co - c
        return math.atan2(q.dot(v), q.dot(u))
    base = ang(A[0])
    ra = [(ang(p) - base) % (2 * math.pi) for p in A]
    rb = [(ang(p) - base) % (2 * math.pi) for p in B]
    a0 = min(range(len(A)), key=lambda i: ra[i])
    b0 = min(range(len(B)), key=lambda i: rb[i])
    A = A[a0:] + A[:a0]
    B = B[b0:] + B[:b0]
    ra = ra[a0:] + ra[:a0]
    rb = rb[b0:] + rb[:b0]
    na, nb = len(A), len(B)

    def ua(i):
        return ra[i] if i < na else ra[i - na] + 2 * math.pi

    def ub(j):
        return rb[j] if j < nb else rb[j - nb] + 2 * math.pi
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
_basis = m047._basis
_Solids = m047._Solids
_parity_in = m047._parity_in
X_, Z_ = Vector((1, 0, 0)), Vector((0, 0, 1))


def _mix(k1, k2, t):
    t = round(max(0.0, min(1.0, t)) * 20) / 20
    return K.mix_key(k1, k2, t)


def _paint(a, faces, key):
    mi = a._mi(key)
    for f in faces:
        if f.is_valid:
            f.material_index = mi


def _tint(a, faces, k):
    for f in faces:
        if not f.is_valid:
            continue
        for l in f.loops:
            t = l[a.tint_layer][0] * k
            l[a.tint_layer] = (t, t, t, 1.0)


def _close(a, vs, key):
    vs = [v for v in vs if v.is_valid]
    fs = _faces(vs)
    bmesh.ops.recalc_face_normals(a.bm, faces=fs)
    a._finish(vs, key, tint=1.0)
    return fs


def _vs(faces):
    return list({v for f in faces if f.is_valid for v in f.verts})


def _square(c, u, v, hu, hv):
    return [c + u * (sx * hu) + v * (sy * hv) for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1))]


# ---- the log frame (spec 2.2) --------------------------------------------------------------------------------------------
NST = 12
GROOVE = 0.17            # the groove vertex sits this far inside the stave's nominal radius (a dark V)
EDGE = 10.0              # plank-top half-angle (deg): flat plank top 20 deg wide, 5 deg chamfer into each groove
THICK = (0.04, -0.03, 0.03, -0.02, 0.04, -0.03, 0.04, -0.02, 0.03, -0.03, 0.04, -0.02)   # alternating staves
FRONT = ((-5.6, 2.50, 0.0), (-2.95, 2.48, 3.0))                                     # (Y, R, twist deg), staves at 90+30k
BODY = ((-2.85, 2.54, 3.0), (1.0, 2.52, 5.5), (4.2, 2.50, 7.0), (6.65, 2.48, 8.0))  # staves offset half a stave (15)
YC = FRONT[0][0]
BORE_R = 1.68
BORE = (YC, -3.9, -1.9)                 # bore stations; the dark plug at -1.9 (about 5.0 in from the broken end)
END0 = -6.6
STAGGER = (0.0, -0.35, -0.15, -0.5, -0.2, 0.0, -0.3, -0.1, -0.45, -0.05, -0.25, -0.4)   # clockwise from the top
CHIPS = {3: 2, 7: 1, 10: 2}             # front stave -> plank-edge corner chipped (a broken corner)
SPLITS = ((9, 0, 0.55, 1.4), (8, 1, 0.65, 1.0), (10, 2, 0.45, 1.2), (2, 0, 0.5, 1.4), (1, 2, 0.5, 1.0),
          (3, 1, 0.35, 1.2))            # body stave, band, position along the band, length
INFO = {}


def _axz():
    """Axis height so the lowest stave crest sinks SINK below the ground."""
    lo = 0.0
    for rows, off in ((FRONT, 0.0), (BODY, 15.0)):
        for y, R, tw in rows:
            for k in range(NST):
                c = 90.0 + off + 30.0 * k + tw
                for ang, r in ((c - EDGE, R + THICK[k]), (c + EDGE, R + THICK[k])):
                    lo = min(lo, r * math.sin(math.radians(ang)))
    return -lo - SINK


AXZ = _axz()


def _p(phi, r, y):
    a = math.radians(phi)
    return Vector((r * math.cos(a), y, AXZ + r * math.sin(a)))


def _stave_ring(bm, y, R, tw, off, gv):
    ring = []
    for k in range(NST):
        c = 90.0 + off + 30.0 * k + tw
        g = bm.verts.new(_p(c - 15.0, R - GROOVE, y))
        gv.add(g)
        r_e = R + THICK[k]
        ring += [g, bm.verts.new(_p(c - EDGE, r_e, y)), bm.verts.new(_p(c + EDGE, r_e, y))]
    return ring


def _split(a, face, along, t, length, width=0.065, depth=0.075):
    """A plank split (spec 2.2): a long narrow V slit in a plank-top facet, `length` along the stave at fraction t,
    no booleans. Returns the slit's inner faces."""
    bm = a.bm
    loop = list(face.verts)
    face.normal_update()
    n = face.normal.copy()
    c0 = face.calc_center_median()
    ys = [v.co.y for v in loop]
    yc = min(ys) + (max(ys) - min(ys)) * t
    c = c0 + Vector(along) * (yc - c0.y)
    u = (Vector(along) - n * Vector(along).dot(n)).normalized()
    v = n.cross(u)
    out = n if n.dot(Vector((c.x, 0.0, c.z - AXZ))) > 0 else -n
    bmesh.ops.delete(bm, geom=[face], context="FACES_ONLY")
    rect = [bm.verts.new(p) for p in _square(c, u, v, length / 2, width / 2)]
    _zip(bm, loop, rect, c, u, v)
    b1 = bm.verts.new(c + u * (length / 2 - 0.12) - out * depth)
    b2 = bm.verts.new(c - u * (length / 2 - 0.12) - out * depth)
    inner = [bm.faces.new((rect[0], rect[1], b2, b1)), bm.faces.new((rect[2], rect[3], b1, b2)),
             bm.faces.new((rect[3], rect[0], b1)), bm.faces.new((rect[1], rect[2], b2))]
    return inner


def shell_body(a):
    """The staved shell (spec 2.2) as one closed ring-stack shell: front section (staves at 90 + 30k), a half-stave
    seam (a zip of the two offset rings), the body (staves offset 15), a flat back face, the front annulus at YC, the
    12-sided bore with its dark plug, and the plank splits. Painted by role and position."""
    bm = a.bm
    gv = set()
    rings = [_stave_ring(bm, y, R, tw, 0.0, gv) for y, R, tw in FRONT] + \
            [_stave_ring(bm, y, R, tw, 15.0, gv) for y, R, tw in BODY]
    front = [_band(bm, rings[0], rings[1])]
    seam = _zip(bm, rings[1], rings[2], Vector((0, -2.9, AXZ)), X_, Z_)
    body = [_band(bm, rings[i], rings[i + 1]) for i in range(2, len(rings) - 1)]
    back = [bm.faces.new(rings[-1])]
    bore = [[bm.verts.new(_p(75.0 + 30.0 * k, BORE_R, y)) for k in range(NST)] for y in BORE]
    annulus = _zip(bm, rings[0], bore[0], Vector((0, YC, AXZ)), X_, Z_)
    bore_f = [_band(bm, bore[i], bore[i + 1]) for i in range(len(bore) - 1)]
    plug = [bm.faces.new(bore[-1])]
    vs = [v for r in rings + bore for v in r]
    _close(a, vs, WOOD)
    # splits on the body's plank tops (after the normals are set, so each slit knows which way is out)
    split_in = []
    for k, b, t, ln in SPLITS:
        f = body[b][3 * k + 1]
        split_in += _split(a, f, Vector((0, 1, 0)), t, ln)
        body[b][3 * k + 1] = None
    vs = list(set(vs) | set(_vs(split_in)))
    vs = list(set(vs) | set(_vs(_faces(vs))))
    _close(a, vs, WOOD)
    # colour: plank tops wood, the groove chamfers deeper (position: the faces touching a pulled-in groove vertex),
    # the ground band deeper, the seam crease ring, cut-free faces dark, the bore by depth
    rng = random.Random(55100)
    tones = [1.0 + rng.uniform(-0.045, 0.045) for _ in range(NST)]
    for bands in (front, body):
        for band in bands:
            for j, f in enumerate(band):
                if f is None or not f.is_valid:
                    continue
                low = f.calc_center_median().z < 0.45
                if j % 3 == 1:
                    key = _mix(WOOD, WOOD_DEEP, 0.25) if low else WOOD
                else:
                    key = _mix(WOOD, WOOD_DEEP, 0.55) if low else _mix(WOOD, WOOD_DEEP, 0.3)
                _paint(a, [f], key)
                _tint(a, [f], tones[j // 3])
    _paint(a, seam, _mix(WOOD, WOOD_DEEP, 0.5))
    _paint(a, back + annulus, WOOD_DEEP)
    _paint(a, bore_f[0], WOOD_DEEP)
    _paint(a, bore_f[1], _mix(WOOD_DEEP, HOLLOW, 0.65))
    _paint(a, plug, HOLLOW)
    _paint(a, split_in, _mix(WOOD_DEEP, HOLLOW, 0.5))
    # the zip faces round each split keep the plank-top colour of their stave
    tops = [f for band in body for j, f in enumerate(band) if f is not None and j % 3 == 1]
    _mottle(a, [f for bands in (front, body) for band in bands for f in band if f is not None and f.is_valid],
            0.03, 0.35, 55110)
    INFO["groove_v"] = len(gv)
    INFO["tops"] = len(tops)
    return vs


def end_block(a, k):
    """One stave-end block of the broken end (spec 2.2): the stave's section (plank top, chamfers, joint walls, bore
    face) seated 0.015 off the shell's front face, running forward to its staggered end with a 0.12 chamfer round
    the cut end face; a few with a broken corner. Painted: cut face orange, chamfer between, sides as the stave."""
    bm = a.bm
    y0, R, tw = FRONT[0]
    c = 90.0 + 30.0 * k + tw
    gap = 1.3
    sec = [(c - 15.0 + gap, R - GROOVE), (c - EDGE, R + THICK[k]), (c + EDGE, R + THICK[k]),
           (c + 15.0 - gap, R - GROOVE), (c + 15.0 - gap, BORE_R), (c - 15.0 + gap, BORE_R)]
    e = END0 + STAGGER[(-k) % NST]
    ch = 0.12
    r0 = [bm.verts.new(_p(ph, r, y0 - 0.015)) for ph, r in sec]
    r1 = [bm.verts.new(_p(ph, r, e + ch)) for ph, r in sec]
    cen = sum((v.co for v in r1), Vector()) / len(r1)
    r2 = []
    for v in r1:
        d = v.co - cen
        d.y = 0.0
        r2.append(bm.verts.new(Vector((v.co.x, e, v.co.z)) - d.normalized() * ch))
    if k in CHIPS:                       # a broken corner: the outer corner of the end face knocked back
        i = CHIPS[k]
        r2[i].co.y += 0.24
        r2[i].co += (cen - r2[i].co) * 0.12
        r1[i].co.y += 0.1
    backf = [bm.faces.new(list(reversed(r0)))]
    side = _band(bm, r0, r1)
    cham = _band(bm, r1, r2)
    endf = [bm.faces.new(r2)]
    vs = r0 + r1 + r2
    _close(a, vs, WOOD)
    rng = random.Random(55200 + k)
    _paint(a, [side[0], side[2]], _mix(WOOD, WOOD_DEEP, 0.4))
    _paint(a, [side[3], side[4], side[5]] + backf, WOOD_DEEP)
    _paint(a, cham, _mix(WOOD_CUT, WOOD, 0.35))
    _paint(a, endf, WOOD_CUT)
    _tint(a, side + cham + endf, 1.0 + rng.uniform(-0.04, 0.04))
    return vs


def shell_part(a):
    vs = shell_body(a)
    for k in range(NST):
        vs += end_block(a, k)
    return vs


# ---- cut-end cap (spec 2.3) ----------------------------------------------------------------------------------------------
CAP_Y0 = BODY[-1][0] + 0.015
CAP_FACE = 6.95
DISC_R = 1.705
CRACKS = 9


def cap_disc(a):
    """The cut-end disc: a 12-sided plug face seated on the shell's back face, its end-grain face cut by nine narrow
    radial V cracks (r 0.34 - 1.52) round a small raised nine-sided pip; built as planar regions, no booleans."""
    bm = a.bm
    rng = random.Random(55300)
    ph0 = 105.0 + BODY[-1][2]
    back = [bm.verts.new(_p(ph0 + 30.0 * k, DISC_R, CAP_Y0)) for k in range(12)]
    rim = [bm.verts.new(_p(ph0 + 30.0 * k, DISC_R, CAP_FACE)) for k in range(12)]
    side = _band(bm, back, rim)
    backf = [bm.faces.new(list(reversed(back)))]
    al = [(28.0 + 40.0 * i + rng.uniform(-2, 2)) % 360.0 for i in range(CRACKS)]

    def pt(ang, r, dy=0.0, perp=0.0):
        p = _p(ang, r, CAP_FACE + dy)
        t = math.radians(ang)
        return p + Vector((-math.sin(t), 0.0, math.cos(t))) * perp
    A, P, N, Bo, B = [], [], [], [], []
    for ang in al:
        rm = rng.uniform(0.85, 1.05)
        w = rng.uniform(0.045, 0.06)
        A.append(bm.verts.new(pt(ang, 0.34)))
        P.append(bm.verts.new(pt(ang, rm, perp=w)))
        N.append(bm.verts.new(pt(ang, rm, perp=-w)))
        Bo.append(bm.verts.new(pt(ang, rm, dy=-0.07)))
        B.append(bm.verts.new(pt(ang, 1.52 + rng.uniform(-0.06, 0.04))))
    pip_b = [bm.verts.new(pt(al[i] + 20.0, 0.17)) for i in range(CRACKS)]
    pip_t = [bm.verts.new(pt(al[i] + 20.0, 0.12, dy=0.05)) for i in range(CRACKS)]
    crack = []
    for i in range(CRACKS):
        crack += [bm.faces.new((A[i], P[i], Bo[i])), bm.faces.new((P[i], B[i], Bo[i])),
                  bm.faces.new((B[i], N[i], Bo[i])), bm.faces.new((N[i], A[i], Bo[i]))]
    rim_ang = [(ph0 + 30.0 * k) % 360.0 for k in range(12)]
    regions, links = [], []
    for i in range(CRACKS):
        j = (i + 1) % CRACKS
        a0, a1 = al[i], al[j] + (360.0 if al[j] < al[i] else 0.0)
        rs = sorted([(x + (360.0 if x < a0 else 0.0), k) for k, x in enumerate(rim_ang)])
        rs = [rim[k] for x, k in rs if a0 < x < a1]
        loop = [A[i], P[i], B[i]] + rs + [B[j], N[j], A[j], pip_b[i]]
        regions.append(bm.faces.new(loop))
    for i in range(CRACKS):
        h = (i - 1) % CRACKS
        # rim edge crossing crack i, and the pip edge crossing it
        a_ = al[i]
        before = max(((x - a_) % 360.0 - 360.0, k) for k, x in enumerate(rim_ang))[1]
        after = min(((x - a_) % 360.0, k) for k, x in enumerate(rim_ang))[1]
        links.append(bm.faces.new((rim[before], B[i], rim[after])))
        links.append(bm.faces.new((pip_b[h], A[i], pip_b[i])))
    pip_s = _band(bm, pip_b, pip_t)
    pip_top = [bm.faces.new(pip_t)]
    vs = back + rim + A + P + N + Bo + B + pip_b + pip_t
    _close(a, vs, WOOD_END)
    _paint(a, side + backf, WOOD_DEEP)
    _paint(a, crack, _mix(WOOD_DEEP, HOLLOW, 0.55))
    _paint(a, pip_top, _mix(WOOD_END, WOOD_CUT, 0.4))
    _mottle(a, regions + links, 0.035, 0.6, 55310)
    INFO["cap_cracks"] = [round(x, 1) for x in al]
    return vs


def rim_block(a, k):
    """One chamfered rim block of the cap (r 1.73 - 2.62, aligned to a body stave), seated 0.015 off the stave ends;
    its end face cut orange, a 0.10 chamfer, sides bark."""
    bm = a.bm
    rng = random.Random(55400 + k)
    c = 105.0 + BODY[-1][2] + 30.0 * k
    ro = 2.62 + rng.uniform(-0.05, 0.03)
    sec = [(c - 14.0, 1.725), (c - 13.0, ro), (c + 13.0, ro), (c + 14.0, 1.725)]
    ye = 7.07 + rng.uniform(0.0, 0.05)
    ch = 0.10
    # the bottom blocks keep their outer corners above the ground line (-SINK)
    sec = [(ph, min(r, (AXZ - SINK) / -math.sin(math.radians(ph))) if math.sin(math.radians(ph)) < -0.5 else r)
           for ph, r in sec]
    r0 = [bm.verts.new(_p(ph, r, CAP_Y0)) for ph, r in sec]
    r1 = [bm.verts.new(_p(ph, r, ye - ch)) for ph, r in sec]
    cen = sum((v.co for v in r1), Vector()) / 4
    r2 = []
    for v in r1:
        d = v.co - cen
        d.y = 0.0
        r2.append(bm.verts.new(Vector((v.co.x, ye, v.co.z)) - d.normalized() * ch))
    backf = [bm.faces.new(list(reversed(r0)))]
    side = _band(bm, r0, r1)
    cham = _band(bm, r1, r2)
    endf = [bm.faces.new(r2)]
    vs = r0 + r1 + r2
    _close(a, vs, WOOD)
    _paint(a, [side[0], side[2]], _mix(WOOD, WOOD_DEEP, 0.3))
    _paint(a, [side[3]] + backf, _mix(WOOD, WOOD_DEEP, 0.6))
    _paint(a, cham, _mix(WOOD_CUT, WOOD, 0.35))
    _paint(a, endf, WOOD_CUT)
    _tint(a, side + cham + endf, 1.0 + rng.uniform(-0.04, 0.04))
    return vs


def cap_part(a):
    vs = cap_disc(a)
    for k in range(12):
        vs += rim_block(a, k)
    return vs


# ---- branch stub (spec 2.4, option A) ------------------------------------------------------------------------------------
BR_PHI, BR_Y = 47.0, 1.4
FORK = Vector((2.16, 3.14, 6.45))          # 50 deg above horizontal, 15 deg toward +X (decision 3)
MAIN_TIP = Vector((2.12, 3.95, 7.78))
SIDE_TIP = Vector((3.55, 3.25, 7.42))
SEC7 = [(math.cos(2 * math.pi * k / 7 + 0.3) * (0.86 if k in (2, 5) else 1.0),
         math.sin(2 * math.pi * k / 7 + 0.3) * (0.86 if k in (2, 5) else 1.0)) for k in range(7)]


def _chain(a, pts, radii, section, u0):
    """Rings of `section` at each polyline point, in the mitre plane of each kink (m053.chain): (rings, sides)."""
    bm = a.bm
    pts = [Vector(p) for p in pts]
    m = len(pts)
    segs = [(pts[i + 1] - pts[i]).normalized() for i in range(m - 1)]
    u = (u0 - segs[0] * u0.dot(segs[0])).normalized()
    fr = []
    for i, t in enumerate(segs):
        if i:
            u = segs[i - 1].rotation_difference(t) @ u
            u = (u - t * u.dot(t)).normalized()
        fr.append((t, u, t.cross(u)))
    rings = []
    for i, p in enumerate(pts):
        t, uu, vv = fr[i - 1] if i else fr[0]
        nrm = (segs[i - 1] + segs[i]).normalized() if 0 < i < m - 1 else t
        ring = []
        for sx, sy in section:
            q = p + (uu * sx + vv * sy) * radii[i]
            q = q - t * ((q - p).dot(nrm) / t.dot(nrm))
            ring.append(bm.verts.new(q))
        rings.append(ring)
    sides = [_band(bm, rings[i], rings[i + 1]) for i in range(m - 1)]
    return rings, sides


def branch(a):
    """The Y stub: a 7-sided planked prism (two pulled-in creases) from 0.35 inside the bark through a wide collar
    (Ø 2.1) that flares out of the bark, a neck, a hard kink at the fork, the main prong to a flat chamfered cut end;
    the 6-sided side prong a closed shell from the stem's axis to its own flat cut end."""
    n = Vector((math.cos(math.radians(BR_PHI)), 0.0, math.sin(math.radians(BR_PHI))))
    S = _p(BR_PHI, 2.53, BR_Y)
    d0 = (FORK - S).normalized()
    neck = S + d0 * 0.75
    t_m = (MAIN_TIP - FORK).normalized()
    pts = [S - n * 0.35, S + d0 * 0.28, neck, FORK, MAIN_TIP - t_m * 0.09, MAIN_TIP]
    radii = [1.22, 1.25, 1.0, 0.78, 0.58, 0.58 - 0.09]
    rings, sides = _chain(a, pts, radii, SEC7, Vector((0, 1, 0)))
    bm = a.bm
    s_cap = [bm.faces.new(list(reversed(rings[0])))]
    e_cap = [bm.faces.new(rings[-1])]
    vs = [v for r in rings for v in r]
    _close(a, vs, WOOD)
    crease = {r[i] for r in rings for i in (2, 5)}
    for si, sd in enumerate(sides[:-1]):
        for f in sd:
            k = sum(1 for v in f.verts if v in crease)
            _paint(a, [f], _mix(WOOD, WOOD_DEEP, 0.35) if k >= 2 else WOOD)
    _paint(a, sides[-1], _mix(WOOD_CUT, WOOD, 0.35))
    _paint(a, e_cap, WOOD_CUT)
    _mottle(a, [f for sd in sides for f in sd], 0.04, 0.5, 55500)
    # side prong
    p0 = neck.lerp(FORK, 0.78)
    t_s = (SIDE_TIP - p0).normalized()
    sec6 = [(math.cos(2 * math.pi * k / 6), math.sin(2 * math.pi * k / 6)) for k in range(6)]
    r2, s2 = _chain(a, [p0, SIDE_TIP - t_s * 0.09, SIDE_TIP], [0.54, 0.5, 0.41], sec6, Vector((0, 0, 1)))
    c0 = [bm.faces.new(list(reversed(r2[0])))]
    c1 = [bm.faces.new(r2[-1])]
    vs2 = [v for r in r2 for v in r]
    _close(a, vs2, WOOD)
    _paint(a, s2[-1], _mix(WOOD_CUT, WOOD, 0.35))
    _paint(a, c1, WOOD_CUT)
    _tint(a, s2[0], 0.97)
    INFO["branch"] = {"collar_on_bark": [round(x, 2) for x in S], "fork": list(FORK), "tips": [list(MAIN_TIP),
                                                                                                list(SIDE_TIP)]}
    return vs + vs2


# ---- rocks (spec 2.6) ----------------------------------------------------------------------------------------------------
# name -> centre, (W, D, H), yaw, kind, seed
ROCKS = {
    "RK1": ((3.65, 1.6), (2.6, 2.2, 2.3), 20.0, "tall", 55601),
    "RK2": ((3.45, -1.05), (2.6, 2.2, 1.7), -12.0, "low", 55602),
    "RK3": ((3.0, -4.4), (1.8, 1.6, 1.3), 30.0, "low", 55603),
    "RK4": ((2.45, -6.6), (1.5, 1.3, 0.9), -20.0, "low", 55604),
    "RK5": ((-3.45, 3.8), (2.6, 2.2, 2.2), -25.0, "tall", 55605),
    "RK6": ((-3.5, -0.4), (2.2, 1.9, 1.6), 15.0, "low", 55606),
    "RK7": ((-3.3, -4.6), (1.3, 1.1, 0.9), 40.0, "low", 55607),
}
PEBBLES = (((5.0, -0.7), 0.7, 55611), ((4.4, 5.4), 0.6, 55612), ((2.6, 6.9), 0.5, 55613), ((-4.6, -6.5), 0.75, 55614))
TALL_RINGS = ((0.0, 0.94, 5), (0.36, 1.0, 5), (0.74, 0.78, 4), (1.0, 0.36, 3))
LOW_RINGS = ((0.0, 0.94, 5), (0.42, 1.0, 5), (1.0, 0.58, 4))
PEB_RINGS = ((0.0, 0.92, 4), (0.5, 1.0, 4), (1.0, 0.45, 3))
ROCK_BASE = 0.16         # the damp foot band (rock_dark) up to this fraction of a rock's height
BASE_INFO = {}


def _rock(a, c, size, yaw, kind, seed, rings=None):
    """A chunky angular rock: the hull of jittered ring stacks, a flat base sunk SINK, tall ones leaning toward the
    log with a peaked top, low ones with a sloping faceted top. Height bands (position, never facing): rock_light on
    the top 35 %, rock_dark on the lowest 25 %; per-facet Tint."""
    rng = random.Random(seed)
    W, D, H = size
    rings = rings or (TALL_RINGS if kind == "tall" else LOW_RINGS)
    inward = Vector((-1.0 if c[0] > 0 else 1.0, 0.0, 0.0))
    m = Matrix.Rotation(math.radians(yaw), 3, "Z")
    il = m.inverted() @ inward
    lean = (0.25 * il.x, 0.25 * il.y) if kind == "tall" else (0.0, 0.0)
    pts = m033._ring_pts(rng, rings, W / 2, D / 2, H, 0.08, lean=lean)
    if kind == "low":
        tilt = rng.uniform(0.10, 0.18)
        for p in pts:
            p.z += tilt * (p.x * il.x + p.y * il.y) * (p.z / H)
    pts = [m @ p + Vector((c[0], c[1], -SINK)) for p in pts]
    for p in pts:
        p.z = max(-SINK, p.z)
    vs = m033._hull(a, pts, ROCK)
    fs = _faces(vs)
    nf = K.noise_field(0.55, seed)
    for f in fs:
        cc = f.calc_center_median()
        h = (cc.z + SINK) / H
        if h < 0.02:                        # the hidden flat base keeps the plain colour
            continue
        if h < ROCK_BASE:
            f.material_index = a._mi(_mix(ROCK, ROCK_DARK, 0.35))
        else:                               # broad pale and plain patches (position noise), never by height or facing
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.5 if nf(cc) > 0.1 else 0.0))
    _mottle(a, fs, 0.04, 0.45, seed)
    for f in fs:
        _tint(a, [f], 1.0 + random.Random(seed + f.index).uniform(-0.035, 0.035))
    return vs


def rock(a, name, guard=None):
    c, size, yaw, kind, seed = ROCKS[name]
    c = Vector(c)
    dep = 0.0
    for step in range(12):
        vs = _rock(a, c, size, yaw, kind, seed)
        dep = guard.depth(vs) if guard is not None else 0.0
        if dep <= BURY_PLACE or step == 11:
            break
        for x in vs:
            a.bm.verts.remove(x)
        c = c + Vector((0.1 if c.x > 0 else -0.1, 0.0))
    BASE_INFO.setdefault("rocks", {})[name] = (round(dep, 3), [round(c.x, 2), round(c.y, 2)])
    if guard is not None:
        guard.add_vs(vs, name)
    return vs


def pebble(a, i, guard=None):
    c, s, seed = PEBBLES[i]
    c = Vector(c)
    for step in range(10):
        vs = _rock(a, c, (s, s * 0.85, s * 0.6), random.Random(seed).uniform(0, 180), "low", seed, rings=PEB_RINGS)
        if guard is None or guard.depth(vs) <= BURY_PLACE or step == 9:
            break
        for x in vs:
            a.bm.verts.remove(x)
        c = c + Vector((0.15 if c.x > 0 else -0.15, 0.0))
    if guard is not None:
        guard.add_vs(vs, f"PB{i + 1}")
    return vs


def rock_part(a):
    return rock(a, "RK1")


# ---- moss: flat lobed leaves on the bark (spec 2.5) ----------------------------------------------------------------------
R_REF = 2.55
LEAF_SCALE = 1.17       # first renders: the 1.1-1.6 leaves read as small stars; the sheet's are big broad leaves
NOTCH = 0.7             # lobe notch depth (fraction of the leaf radius): broad lobes, not a spiky star
# clump -> anchor (Y, phi deg; phi from +X toward +Z: 90 the crest, 0 the +X flank, 180 the -X flank), leaves
# (dY, dphi, size, layer[, stand deg])
CLUMPS = {
    "M1": ((-3.1, 75.0), [(-1.2, 18, 1.3, 0), (0.0, 22, 1.5, 1, 20), (1.2, 16, 1.3, 0), (-0.6, 8, 1.5, 2, 25),
                          (0.7, 6, 1.4, 1), (-1.3, -4, 1.2, 1), (1.3, -6, 1.2, 0), (0.0, -12, 1.6, 2),
                          (-0.3, -30, 1.4, 1), (0.4, -44, 1.3, 2), (-0.2, -58, 1.3, 1), (0.3, -72, 1.2, 2, 15),
                          (-0.1, -86, 1.1, 1, 20)]),
    "M2": ((-0.4, 88.0), [(-0.9, 4, 1.1, 0), (0.0, -4, 1.2, 1, 25), (0.9, 6, 1.0, 0), (-0.3, 14, 1.0, 1),
                          (0.6, -30, 0.95, 1), (1.3, -16, 0.9, 1)]),
    "M3": ((3.6, 70.0), [(-1.0, 15, 1.2, 0), (0.3, 18, 1.3, 1, 25), (1.4, 12, 1.1, 0), (-0.4, 2, 1.3, 2, 20),
                         (0.9, 0, 1.2, 1), (0.2, -14, 1.2, 1), (-0.2, -28, 1.1, 2), (0.3, -42, 1.0, 1, 15),
                         (0.0, -54, 0.9, 1, 20)]),
    "M4": ((5.3, 108.0), [(-0.7, 0, 1.0, 0), (0.5, -4, 1.1, 1, 25), (0.0, 10, 1.2, 2, 45), (0.9, 12, 1.0, 1, 55),
                          (-0.6, 16, 0.9, 1)]),
    "M5": ((-1.1, 100.0), [(-1.1, -4, 1.2, 0), (0.2, -8, 1.3, 1, 25), (1.2, -2, 1.1, 0), (-0.5, 8, 1.4, 2, 20),
                           (0.8, 10, 1.3, 1), (0.0, 24, 1.3, 1), (-0.4, 38, 1.2, 2), (0.3, 52, 1.2, 1),
                           (-0.2, 66, 1.1, 2), (0.2, 80, 1.0, 1, 15), (0.0, 92, 0.9, 1, 20)]),
    "M6": ((5.8, 140.0), [(-0.6, 0, 1.1, 0), (0.4, -6, 1.2, 1, 35), (0.0, 10, 1.2, 2), (0.5, 20, 1.0, 1, 30),
                          (-0.3, 24, 0.9, 1), (0.6, 32, 0.9, 1, 40), (-0.5, 38, 0.85, 1, 35)]),
    "M7": ((2.6, 118.0), [(-0.5, -6, 1.1, 0), (0.4, 2, 1.2, 1, 25), (0.0, 18, 1.2, 1), (0.3, 32, 1.1, 2),
                          (-0.2, 46, 1.0, 1, 15), (0.1, 58, 0.9, 1, 20)]),
    "M8": ((6.0, 50.0), [(-0.2, 0, 1.0, 1, 40), (0.1, 16, 0.9, 1, 45)]),
    # the broken end's top and right shoulder: leaves standing off the bark so they show round the ring (front cell)
    "MF": ((-5.2, 60.0), [(-0.3, 22, 1.0, 1, 35), (0.2, 4, 1.1, 0, 45), (-0.2, -14, 1.0, 1, 50),
                          (0.3, -32, 0.9, 1, 40)]),
}
LEAF_INFO = {}
_SHIFTS = ((0.0, 0.0, 1.0), (0.0, 5.0, 1.0), (0.0, -5.0, 1.0), (0.3, 0.0, 0.9), (-0.3, 0.0, 0.9), (0.0, 9.0, 0.85),
           (0.0, -9.0, 0.85), (0.5, 4.0, 0.8), (-0.5, 4.0, 0.8), (0.0, 13.0, 0.75))


def _hit_r(tree, phi, y):
    """Radius of the bark's outer surface under footprint (phi, y): a ray from outside toward the axis."""
    d = -Vector((math.cos(math.radians(phi)), 0.0, math.sin(math.radians(phi))))
    o = _p(phi, 9.0, y)
    h = tree.ray_cast(o, d, 9.0)
    return None if h[0] is None else 9.0 - h[3]


def leaf(a, tree, Y0, phi0, size, layer, rho, seed, stand=0.0, key=LIME, lobes=5):
    """One flat lobed leaf (spec 2.5): a 2*lobes-point star (pointed lobes, notches at 0.55), a raised centre on top
    and a slightly sunk centre underneath (a closed 20-tri shell), wrapped round the log at the radius of the highest
    bark under its footprint (so it bridges the grooves and never cuts the bark) plus a layer lift; `stand` tips the
    far half up off the bark. Returns (verts, lobe tip build-frame points)."""
    bm = a.bm
    rng = random.Random(seed)
    R = size / 2
    pts = []
    for i in range(2 * lobes):
        t = rho + math.pi * i / lobes
        r = R * (rng.uniform(0.95, 1.05) if i % 2 == 0 else rng.uniform(NOTCH - 0.04, NOTCH + 0.04))
        pts.append((r * math.cos(t), r * math.sin(t)))

    def fp(x, y):
        return phi0 + math.degrees(y / R_REF), Y0 + x
    hits_all = [_hit_r(tree, *fp(x, y)) for x, y in pts + [(0.0, 0.0)]]
    hits = [h for h in hits_all if h is not None]
    if not hits:
        return None, []
    rb = max(hits) + 0.008 + 0.008 * layer
    st = math.tan(math.radians(stand)) if stand else 0.0
    beta = rho + math.pi / lobes * 0.5

    def lift(x, y):
        if not st:
            return 0.0
        return max(0.0, x * math.cos(beta) + y * math.sin(beta) + 0.3 * R) * st
    # contact: if the vertex over the highest bark is one the stand lifted, no vertex lies within CONTACT of the bark;
    # lower the leaf until its closest vertex is 0.016 off (every vertex stays outside the bark under it)
    gaps = [rb + lift(x, y) - h for (x, y), h in zip(pts, hits_all) if h is not None]
    if hits_all[-1] is not None:
        gaps.append(rb - 0.02 + lift(0, 0) - hits_all[-1])
    if min(gaps) > 0.028:
        rb -= min(gaps) - 0.016
    out = []
    for x, y in pts:
        ph, yy = fp(x, y)
        out.append(bm.verts.new(_p(ph, rb + lift(x, y), yy)))
    top = bm.verts.new(_p(phi0, rb + 0.07 + lift(0, 0), Y0))
    bot = bm.verts.new(_p(phi0, rb - 0.02 + lift(0, 0), Y0))
    n = len(out)
    for i in range(n):
        bm.faces.new((top, out[i], out[(i + 1) % n]))
        bm.faces.new((bot, out[(i + 1) % n], out[i]))
    vs = out + [top, bot]
    _close(a, vs, key)
    tips = [out[i].co.copy() for i in range(0, n, 2)]
    return vs, tips


def _leaf_key(layer, z):
    t = {0: 0.45, 1: 0.1, 2: 0.0}[layer]
    if z < 3.0:
        t += 0.15
    return _mix(LIME, GREEN, t)


def moss_clump(a, name, tree, guard=None):
    """A clump of leaves (CLUMPS), each tried at its planned spot, then nudged round it and shrunk, if it cuts the
    branch or a rock more than BURY_PLACE; dropped if every try still cuts (never kept buried)."""
    (Y, phi), leaves = CLUMPS[name]
    info = LEAF_INFO.setdefault(name, {"placed": 0, "moved": 0, "dropped": 0, "tips": []})
    out = []
    for i, lf in enumerate(leaves):
        dY, dphi, size, layer = lf[:4]
        stand = lf[4] if len(lf) > 4 else 0.0
        seed = 55700 + 31 * i + sum(map(ord, name))
        rho = random.Random(seed).uniform(0, 6.28)
        got = None
        for j, (sy, sp, sc) in enumerate(_SHIFTS):
            y0, p0 = Y + dY + sy, phi + dphi + sp
            z = AXZ + 2.5 * math.sin(math.radians(p0))
            vs, tips = leaf(a, tree, y0, p0, size * sc * LEAF_SCALE, layer, rho, seed, stand, key=_leaf_key(layer, z))
            if vs is None:
                continue
            if guard is None or guard.depth(vs) <= BURY_PLACE:
                got = (vs, tips, j)
                break
            for x in vs:
                a.bm.verts.remove(x)
        if got is None:
            info["dropped"] += 1
            continue
        vs, tips, j = got
        info["placed"] += 1
        info["moved"] += j > 0
        info["tips"] += [list(t) for t in tips]
        _tint(a, _faces(vs), 1.0 + random.Random(seed + 1).uniform(-0.04, 0.04))
        out += vs
    return out


# ---- grass tufts (spec 2.6), from m053 -----------------------------------------------------------------------------------
TUFTS = {   # centre, blade count, height, lime share, seed
    "T1": ((-4.1, -6.0), 7, 1.8, 0.6, 55801),
    "T2": ((5.2, -4.8), 7, 2.3, 0.6, 55802),
    "T3": ((3.75, -2.65), 8, 2.6, 0.6, 55803),
    "T4a": ((3.95, 4.6), 8, 2.5, 0.6, 55804),
    "T4b": ((5.1, 6.25), 6, 2.0, 0.6, 55805),
    "T5": ((4.7, 0.45), 5, 0.8, 0.6, 55806),
    "T6": ((-3.95, 5.95), 8, 2.5, 0.6, 55807),
    "T7": ((-4.3, 1.7), 6, 1.2, 0.6, 55808),
    "T8": ((-3.9, -2.5), 7, 2.3, 0.6, 55809),
}
CAM_F34 = Vector((0.82, -0.57, 0.3)).normalized()
CAM_R34 = Vector((-0.74, -0.67, 0.3)).normalized()
_SEARCH = [Vector((0, 0, 0))] + [Vector((math.cos(2 * math.pi * k / n + 0.3 * i) * r, math.sin(2 * math.pi * k / n +
                                                                                                0.3 * i) * r, 0.0))
                                 for i, (r, n) in enumerate(((0.3, 8), (0.6, 8), (0.9, 12), (1.2, 12), (1.5, 16)))
                                 for k in range(n)]
_HUBS = []


def blade(a, base, yaw, pitch, L, W, key, curl=0.12, face=None, base_key=None):
    """A pointed lanceolate grass blade (m053): a closed folded bipyramid (8 tris), widest at 0.35 L, the tip arching
    out by `curl`; its broad face turned toward `face` (a camera) so it is never edge-on."""
    bm = a.bm
    u = Vector((math.cos(yaw), math.sin(yaw), 0.0))
    cp, sp = math.cos(pitch), math.sin(pitch)
    x = u * cp + Vector((0, 0, sp))
    z = -u * sp + Vector((0, 0, cp))
    if face is not None:
        f = Vector(face) - x * Vector(face).dot(x)
        if f.length > 1e-6:
            f.normalize()
            if f.dot(z) < 0:
                f = -f
            z = (z + f * 1.2).normalized()
            z = (z - x * z.dot(x)).normalized()
    y = z.cross(x)
    B = Vector(base)

    def P(lx, ly, lz):
        t = lx / L
        return bm.verts.new(B + x * lx + y * ly + z * (lz - curl * L * t * t))
    o = [P(0, 0, 0), P(0.35 * L, -W / 2, 0), P(L, 0, 0), P(0.35 * L, W / 2, 0)]
    fr = P(0.4 * L, 0, 0.09 * W + 0.03)
    bk = P(0.4 * L, 0, -0.05)
    fs = [bm.faces.new((o[i], o[(i + 1) % 4], fr)) for i in range(4)] + \
         [bm.faces.new((o[(i + 1) % 4], o[i], bk)) for i in range(4)]
    vs = o + [fr, bk]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    a._finish(vs, key, tint=1.0)
    if base_key:                    # two-tone by role: the faces at the base deeper green, the tip half lime
        _paint(a, [f for f in fs if o[0] in f.verts], base_key)
    return vs


def tuft(a, name, guard=None):
    """A tuft of pointed lime blades round a small closed 5-sided hub sunk 0.03 (hub 0.3 clear of the log and the
    rocks, else moved); the tallest blades lime, the inner and lower ones deeper green (role). A blade that cuts the
    log or a rock more than BURY_PLACE stands up, turns aside, shortens; dropped if every try still cuts."""
    (cx, cy), n, H, lime, seed = TUFTS[name]
    rng = random.Random(seed)
    bm = a.bm
    info = BASE_INFO.setdefault(name, {"retried": 0, "dropped": 0, "moved": 0})
    hr, hh = 0.24, 0.3
    yaw0 = rng.uniform(0, 6.28)
    c = Vector((cx, cy, 0.0))
    if guard is not None:
        for off in _SEARCH:
            q = c + off
            probe = [q + Vector((math.cos(2 * math.pi * k / 8) * (hr + 0.3), math.sin(2 * math.pi * k / 8) * (hr + 0.3),
                                 z)) for k in range(8) for z in (0.05, 0.3)] + [q + Vector((0, 0, 0.15))]
            # the hub's own ring and just outside it (a pebble can sit between the outer probes: fix, T5)
            probe += [q + Vector((math.cos(2 * math.pi * k / 8 + 0.4) * rr, math.sin(2 * math.pi * k / 8 + 0.4) * rr,
                                  0.08)) for k in range(8) for rr in (hr, hr + 0.15)]
            if max(guard.point(p)[0] for p in probe) <= 0.0 and all((q - h).length > 0.9 for h in _HUBS):
                info["moved"] = round(off.length, 2)
                c = q
                break
    _HUBS.append(c.copy())
    ring = [bm.verts.new(c + Vector((math.cos(yaw0 + 2 * math.pi * k / 5) * hr,
                                     math.sin(yaw0 + 2 * math.pi * k / 5) * hr, -0.03))) for k in range(5)]
    apex = bm.verts.new(c + Vector((0, 0, hh)))
    fs = [bm.faces.new((ring[k], ring[(k + 1) % 5], apex)) for k in range(5)] + [bm.faces.new(list(reversed(ring)))]
    hub = ring + [apex]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    a._finish(hub, _mix(GREEN, WOOD_DEEP, 0.3), tint=1.0)
    info["hub"] = [round(c.x, 2), round(c.y, 2)]
    out = list(hub)
    face = CAM_F34 if c.x > 0 else CAM_R34
    hs = [H * (rng.uniform(0.85, 1.0) if k % 2 == 0 else rng.uniform(0.55, 0.75)) for k in range(n)]
    order = sorted(range(n), key=lambda k: -hs[k])
    n_lime = max(1, round(lime * n))
    for k in range(n):
        yaw = yaw0 + 0.3 + 2 * math.pi * k / n + rng.uniform(-0.25, 0.25)
        tall = order.index(k) < n_lime
        pitch = math.radians(rng.uniform(66, 80) if hs[k] > 0.8 * H else rng.uniform(52, 64))
        Lb = hs[k] / math.sin(pitch) * 1.08
        Wb = Lb / 2.7 * rng.uniform(0.95, 1.1)
        key = _mix(LIME, GREEN, 0.1) if tall else _mix(LIME, GREEN, 0.5)
        tries = [(0.0, pitch, 1.0), (0.0, min(math.radians(82), pitch + 0.25), 0.9), (0.4, pitch, 0.9),
                 (-0.4, pitch, 0.9), (0.8, pitch + 0.15, 0.8), (-0.8, pitch + 0.15, 0.8), (0.0, math.radians(84), 0.7)]
        vs = None
        for i, (dy, p_, s_) in enumerate(tries):
            y_ = yaw + dy
            base = c + Vector((math.cos(y_) * hr * 0.3, math.sin(y_) * hr * 0.3, hh * 0.35))
            vs = blade(a, base, y_, p_, Lb * s_, Wb * s_, key, curl=rng.uniform(0.08, 0.15), face=face,
                       base_key=_mix(LIME, GREEN, 0.75 if tall else 0.9))
            if guard is None or guard.depth(vs) <= BURY_PLACE:
                info["retried"] += i > 0
                break
            for x in vs:
                bm.verts.remove(x)
            vs = None
        if vs is None:
            info["dropped"] += 1
            continue
        _tint(a, _faces(vs), 1.0 + rng.uniform(-0.04, 0.04))
        out += vs
    return out


def foliage_part(a):
    _HUBS.clear()
    return tuft(a, "T3")


# ---- assemblies --------------------------------------------------------------------------------------------------------
def _solid(guard, vs, name):
    guard.add_vs([v for v in vs if v.is_valid], name)


def _wood(a):
    """Shell, end blocks, cap and branch into a; returns (placement BVH of shell + cap, guard of every wood shell,
    shell verts, cap verts, branch verts)."""
    sv = shell_body(a)
    blocks = [end_block(a, k) for k in range(NST)]
    cv = cap_disc(a)
    rims = [rim_block(a, k) for k in range(12)]
    bv = branch(a)
    guard = _Solids()
    _solid(guard, sv, "shell")
    for k, b in enumerate(blocks):
        _solid(guard, b, f"block{k}")
    _solid(guard, cv, "disc")
    for k, r in enumerate(rims):
        _solid(guard, r, f"rim{k}")
    bvs = [v for v in bv if v.is_valid]
    _solid(guard, bvs[:len(bvs) - 18], "branch")
    _solid(guard, bvs[len(bvs) - 18:], "prong")
    wood = sv + [v for b in blocks for v in b] + cv + [v for r in rims for v in r]
    fs = _faces(wood)
    idx = {v: i for i, v in enumerate(wood)}
    tree = BVHTree.FromPolygons([v.co.copy() for v in wood], [[idx[v] for v in f.verts] for f in fs])
    return tree, guard, wood, bv


def _branch_guard(a, bv):
    g = _Solids()
    bvs = [v for v in bv if v.is_valid]
    _solid(g, bvs[:len(bvs) - 18], "branch")
    _solid(g, bvs[len(bvs) - 18:], "prong")
    return g


def hero_all(a):
    """Everything in one object of closed shells: shell + end blocks, cap, branch; rocks and pebbles (guarded off the
    log); the moss clumps (guarded off the branch and the rocks); the tufts (guarded off the log and the rocks)."""
    BASE_INFO.clear()
    LEAF_INFO.clear()
    _HUBS.clear()
    tree, guard, wood, bv = _wood(a)
    rguard = _Solids()
    for name in ROCKS:
        vs = rock(a, name, guard)
        _solid(rguard, vs, name)
    for i in range(len(PEBBLES)):
        vs = pebble(a, i, guard)
        _solid(rguard, vs, f"PB{i + 1}")
    mguard = _branch_guard(a, bv)
    mguard.items += rguard.items
    for name in CLUMPS:
        moss_clump(a, name, tree, mguard)
    for name in TUFTS:
        tuft(a, name, guard)


def moss_part(a):
    """Clump M1 as it lies on the log (the log is built for the placement, then removed)."""
    LEAF_INFO.clear()
    tree, guard, wood, bv = _wood(a)
    rguard = _Solids()
    for name in ROCKS:
        vs = rock(a, name, guard)
        _solid(rguard, vs, name)
    mguard = _branch_guard(a, bv)
    mguard.items += rguard.items
    keep = set(moss_clump(a, "M1", tree, mguard))
    bmesh.ops.delete(a.bm, geom=[v for v in a.bm.verts if v not in keep], context="VERTS")


def branch_part(a):
    return branch(a)


# ---- objects -------------------------------------------------------------------------------------------------------
NOTES = {
    HERO: "Fallen Log: a big chunky hollow log of twelve planked staves with V grooves and a half-stave step seam; "
          "the open broken end a ring of staggered chamfered orange stave blocks round a near-black bore, the far end "
          "a cracked cut cap in a ring of rim blocks; one forked branch stub; flat lobed lime moss leaves over the "
          "crest and down both flanks; neutral grey rocks and lime grass tufts along the base. No VFX",
    SHELL_P: "Log Shell: the single hollow staved shell with its 12-sided bore, dark plug and plank splits, plus the "
             "twelve staggered chamfered stave-end blocks of the broken end",
    CAP_P: "Cut End (Cap): an end-grain disc with nine radial cracks and a pip inside a ring of twelve chamfered rim "
           "blocks",
    BRANCH_P: "Branch Stub: a planked Y stub with a flared collar and two flat cut prong ends",
    MOSS_P: "Moss / Foliage: a drape of flat lobed moss leaves (clump M1) shaped to the log's crest and flank",
    ROCK_P: "Rock Module: a chunky faceted neutral grey boulder",
    FOL_P: "Foliage Clump: a tuft of pointed lime grass blades round a small hub",
}
COLLISION = {HERO: "precise", SHELL_P: "precise", CAP_P: "hull", BRANCH_P: "hull", MOSS_P: "hull", ROCK_P: "hull",
             FOL_P: "hull"}


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
def _keys(o):
    return [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]


def _kind(ks, nf):
    if any(k.startswith("m055_rock") for k in ks):
        return "rock"
    if any("wood_deep" in k for k in ks) and any(k.startswith("m055_leaf_green") for k in ks):
        return "plant"                                   # the tuft hub
    if all(k.startswith("m055_leaf") for k in ks):
        return "plant" if nf <= 10 else "moss"
    return "wood"


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
        if len(groups[big]) > 300:
            kinds[big] = "log"
    return bm, ids, n, groups, kinds


def shells_report(o):
    """Per shell: kind, tris, non-manifold edges and verts, boundary edges, winding errors (manifold edges whose two
    faces don't run the same way round), self-intersecting face pairs, signed volume."""
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
        out.append({"kind": kinds[k], "tris": len(fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary),
                    "winding_errors": sum(1 for e in es if e.is_manifold and not e.is_contiguous),
                    "self_hits": hits, "volume": round(vol, 4), "zmin": round(min(v.co.z for v in vs), 3)})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating dressing (STAGES): per shell, whether it touches another shell (triangles intersect, or a vertex
    within `tol` of another shell's surface) or the ground, and whether it chains by contact to an anchor (shells on
    the ground; for a part with nothing on the ground, its biggest shell)."""
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
    ground = {k for k in range(n) if zmin[k] - z0 <= tol}
    if o.name in (MOSS_P, BRANCH_P, CAP_P) or len(ground) == n and n > 1:
        ground = {max(range(n), key=lambda k: len(groups[k]))}
    for k in ground:
        gap[k] = 0.0 if n > 1 else gap[k]
    if n == 1:
        gap = [0.0]

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
    res = {"shells": n, "floating": len(floating), "floating_kinds": sorted({kinds[k] for k in floating}),
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "unchained": chained(tol), "unchained_chain_tol": chained(chain_tol),
           "kinds": {k: kinds.count(k) for k in sorted(set(kinds))}}
    bm.free()
    return res


def bury_report(o):
    """STAGES "nothing buried": every moss and plant shell tested by ray parity against every wood shell (log, end
    blocks, cap pieces, branch) and every rock; every rock against the wood. depth = the distance from its deepest
    vert or face centre inside to that shell's surface."""
    bm, ids, n, groups, kinds = _shells(o)
    wood = _Solids()
    rocks = _Solids()
    for k in range(n):
        if kinds[k] in ("wood", "log", "rock"):
            vs = list({v for f in groups[k] for v in f.verts})
            vi = {v: i for i, v in enumerate(vs)}
            (rocks if kinds[k] == "rock" else wood).add([v.co for v in vs], [[vi[v] for v in f.verts] for f in groups[k]],
                                                        f"{kinds[k]}{k}")
    res, rk = [], []
    for k in range(n):
        if kinds[k] not in ("plant", "moss", "rock"):
            continue
        fs = groups[k]
        pts = list({v.co.copy().freeze() for f in fs for v in f.verts}) + [f.calc_center_median() for f in fs]
        d1, w1 = max((wood.point(Vector(p)) for p in pts), key=lambda r: r[0])
        if kinds[k] == "rock":
            if d1 > 0:
                rk.append((round(d1, 3), w1))
            continue
        d2, w2 = max((rocks.point(Vector(p)) for p in pts), key=lambda r: r[0])
        d, who = (d1, w1) if d1 >= d2 else (d2, w2)
        if d > 0:
            c = sum((f.calc_center_median() for f in fs), Vector()) / len(fs)
            res.append((round(d, 3), kinds[k], who, [round(x, 2) for x in c]))
    bm.free()
    res.sort(key=lambda r: -r[0])
    rk.sort(key=lambda r: -r[0])
    return {"dressing_shells": sum(1 for k in kinds if k in ("plant", "moss")), "over_0.05": sum(1 for r in res if r[0] > BURY),
            "max": res[0][0] if res else 0.0, "worst": res[:6],
            "rocks_in_wood_over_0.05": sum(1 for r in rk if r[0] > BURY), "rocks_in_wood": rk[:6]}


def lobe_tip_report(h):
    """Spec 6: every moss lobe tip ray-checked against the bark: for each tip, a ray from outside toward the log axis
    through the tip finds the first wood surface (log, blocks, cap, branch) - the tip is inside the wood if that
    surface lies further out than the tip (by more than 0.05: buried); the gap otherwise (how far the tip floats)."""
    bm, ids, n, groups, kinds = _shells(h)
    off = Vector(h[OFF])
    wood = _Solids()
    keep = []
    for k in range(n):
        if kinds[k] in ("wood", "log", "rock"):
            vs = list({v for f in groups[k] for v in f.verts})
            vi = {v: i for i, v in enumerate(vs)}
            wood.add([v.co + off for v in vs], [[vi[v] for v in f.verts] for f in groups[k]], f"{kinds[k]}{k}")
            if kinds[k] != "rock":
                keep += groups[k]
    vs = list({v for f in keep for v in f.verts})
    vi = {v: i for i, v in enumerate(vs)}
    tree = BVHTree.FromPolygons([v.co + off for v in vs], [[vi[v] for v in f.verts] for f in keep])
    bm.free()
    inside, gaps = [], []
    for name, info in LEAF_INFO.items():
        for t in info["tips"]:
            t = Vector(t)
            dep, who = wood.point(t)
            if dep > 0:
                inside.append((round(dep, 3), name, who))
            # the radial gap: from the tip straight in toward the log axis to the first wood surface
            rd = Vector((t.x, 0.0, t.z - AXZ))
            hit = tree.ray_cast(t, -rd.normalized(), rd.length)
            gaps.append(hit[3] if hit[0] is not None else None)
    g = sorted(x for x in gaps if x is not None)
    inside.sort(key=lambda r: -r[0])
    return {"tips": len(gaps), "inside_over_0.05": sum(1 for r in inside if r[0] > BURY), "inside_any": len(inside),
            "worst_inside": inside[:4], "over_open_air": sum(1 for x in gaps if x is None),
            "radial_gap_min": round(g[0], 3) if g else None, "radial_gap_median": round(g[len(g) // 2], 3) if g else None,
            "radial_gap_max": round(g[-1], 3) if g else None, "radial_gap_over_0.2": sum(1 for x in g if x > 0.2)}


# ---- build -------------------------------------------------------------------------------------------------------------
PARTS = ((SHELL_P, shell_part), (CAP_P, cap_part), (BRANCH_P, branch_part), (MOSS_P, moss_part), (ROCK_P, rock_part),
         (FOL_P, foliage_part))
TARGET_SIZE = ((11.5, 1.2), (14.6, 0.6), (8.1, 0.3))      # hero W (X), D (Y), H (Z) +- tolerance


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m055_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", "MossyHollowLog"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build(render=True, parts=True, close=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn)
    h, log["hero"] = _make(HERO, hero_all, "hero", 4000)
    _cleanup_tmp()
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
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
        lim = 3600 if o is h else 1000
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
            problems.append(f"{n_}: {c['floating']} shells touch nothing within {CONTACT}, {c['unchained']} have no "
                            f"chain of contact to an anchor")
    bury = {h.name: bury_report(h)}
    if MOSS_P in objs:
        bury[MOSS_P] = "n/a (no wood in the part; placed on the log as in the hero)"
    for n_, b in bury.items():
        if isinstance(b, str):
            continue
        if b["over_0.05"]:
            problems.append(f"{n_}: {b['over_0.05']} dressing shells more than {BURY} inside wood or rock "
                            f"(worst {b['worst'][:3]})")
        if b["rocks_in_wood_over_0.05"]:
            problems.append(f"{n_}: {b['rocks_in_wood_over_0.05']} rocks more than {BURY} into the log "
                            f"({b['rocks_in_wood'][:3]})")
    tips = lobe_tip_report(h)
    if tips.get("inside_over_0.05"):
        problems.append(f"{HERO}: {tips['inside_over_0.05']} moss lobe tips more than {BURY} inside the wood")
    if SHELL_P in objs and sum(1 for s in shells[SHELL_P] if s["kind"] == "log") != 1:
        problems.append(f"{SHELL_P}: expected one main shell")
    if sum(1 for s in shells[HERO] if s["kind"] == "log") != 1:
        problems.append(f"{HERO}: {sum(1 for s in shells[HERO] if s['kind'] == 'log')} main log shells, expected 1")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 14: none)")
    for n_, t in thin.items():
        if t["under"]:
            problems.append(f"{n_}: {t['under']} faces with a corner under 2 deg (min {t['min_deg']})")
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
           "hero_shells": kinds, "contact": contact, "bury": bury, "lobe_tips": tips, "winding": winding,
           "base_info": dict(BASE_INFO), "leaves": {k: {kk: v for kk, v in i.items() if kk != "tips"}
                                                   for k, i in LEAF_INFO.items()},
           "thin": thin, "log": log, "problems": problems, "uv": uv, "axz": round(AXZ, 3), "info": dict(INFO),
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders -------------------------------------------------------------------------------------------------------
# decision 10: f34_sheet (55, 18) and front_sheet (0, 3) govern; floor hidden and a 3x lens in every *_sheet shot
SHEET_VIEWS = {"f34_sheet": (55, 22), "r34_sheet": (-46, 10), "front_sheet": (0, 3), "side_sheet": (90, 3),
               "rear_sheet": (180, 3), "top_sheet": (0, 89)}
VIEW_NAMES = ("front", "side", "rear", "top", "underside")
PARTS_SHOT = (55, 22)
PART_SHOTS = {CAP_P: (150, 15)}    # the cap's cracked face looks out of the +Y end


def _exploded(objs):
    """Copies laid out like the sheet's exploded view: the shell in the middle, the cap drawn off its +Y end, the
    branch lifted off its socket, the moss clump lifted off the crest, the rock and the foliage clump in front."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []
    base = Matrix.Translation((objs[0].location.x + 80, objs[0].location.y, 0))

    def put(tag, o, dv):
        c = bpy.data.objects.new(f"{PFX}expl_{tag}", o.data)
        coll.objects.link(c)
        c.matrix_world = base @ Matrix.Translation(Vector(dv)) @ Matrix.Translation(Vector(o[OFF]))
        shown.append(c)
    for name, dv in ((SHELL_P, (0, 0, 0)), (CAP_P, (0, 4.5, 0)), (BRANCH_P, (1.2, 0.0, 4.2)), (MOSS_P, (1.6, 0, 3.6)),
                     (ROCK_P, (6.0, -0.5, 0)), (FOL_P, (5.6, -6.0, 0))):
        if name in by:
            put(name, by[name], dv)
    bpy.context.view_layer.update()
    return shown


def _scale_marker(h, at, name="char"):
    """A 5.5-stud character stand-in at build-frame point `at`."""
    a = K.fk().Asset(PFX + name, "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=ROCK_DARK, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=ROCK_DARK, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=ROCK_DARK, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
    c.location = off @ Vector(at)
    bpy.context.view_layer.update()
    return c


def _top_z(h, x, y):
    off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
    o = off @ Vector((x, y, 30.0))
    dg = bpy.context.evaluated_depsgraph_get()
    hit = bpy.context.scene.ray_cast(dg, o, Vector((0, 0, -1)))
    return (off.inverted() @ hit[1]).z if hit[0] else 5.0


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    markers = [_scale_marker(h, (-5.9, -1.0, -SINK), "char")]
    markers.append(_scale_marker(h, (-0.5, -4.0, _top_z(h, -0.5, -4.0) - 0.02), "char_top"))
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        extra["front34"] = ([h], 55, 22)
        extra["rear34"] = ([h], -46, 10)
        for o in objs[1:]:
            extra["part_" + o.name.replace("MossyHollowLog", "").lower()] = ([o], *PART_SHOTS.get(o.name, PARTS_SHOT))
        if shown:
            extra["exploded"] = (shown, 55, 22)
        extra["scale"] = ([h] + markers, -62, 6)
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
        for o in shown + markers:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if o in markers and me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def render_close_ups(objs):
    """bore_cu (close-up A), branch_cu (close-up B), section_cu (the shell part end-on: close-up C), cap_cu (the cut
    cap), moss_cu (the big drape M1), base_cu (rocks and tufts on the +X flank)."""
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    by = {o.name: o for o in objs}
    h = objs[0]
    out = {}

    def at(o, p):
        return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)
    rc = m033.render_close
    out["bore_cu"] = rc([h], f"{d}/bore_cu.png", 20, 8, at(h, (0.3, -6.6, AXZ)), 3.0)
    out["branch_cu"] = rc([h], f"{d}/branch_cu.png", 55, 25, at(h, (1.9, 1.7, 4.9)), 1.9)
    out["cap_cu"] = rc([h], f"{d}/cap_cu.png", 180, 5, at(h, (0.0, 7.0, AXZ)), 2.9)
    out["moss_cu"] = rc([h], f"{d}/moss_cu.png", 55, 25, at(h, (1.6, -3.1, 3.9)), 2.6)
    out["base_cu"] = rc([h], f"{d}/base_cu.png", 70, 12, at(h, (3.6, 0.0, 1.2)), 4.0)
    if SHELL_P in by:
        s = by[SHELL_P]
        out["section_cu"] = rc([s], f"{d}/section_cu.png", 8, 6, at(s, (0.0, -6.8, AXZ)), 2.9)
    return out


def preview(names=("f34_sheet", "front_sheet", "r34_sheet", "side_sheet", "rear_sheet", "top_sheet"), vfx=False):
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
    h, lg = _make(HERO, hero_all, "hero", 4000)
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, _ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"hero": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                        "boundary_edges", "normals")}, "log": lg, "axz": round(AXZ, 3),
            "base": dict(BASE_INFO), "leaves": {k: {kk: v for kk, v in i.items() if kk != "tips"}
                                                for k, i in LEAF_INFO.items()}}
