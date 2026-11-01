"""064 A-Frame Tent (references/064.png): a walk-in A-frame canvas tent with its camp dressing. Two X frames of crossed
square chamfered timber poles (side by side, touching at the crossing, both frames leaning out 9.6 deg), each crossing
tied with a rope lashing (two wraps round both poles and a V sling under them), a cream canvas of closed 0.10 slabs
(two sagging side panels folded over a hidden ridge pole, a closed back, an open front doorway between two flaps with
turned-back edges, a rolled door flap across the top of the doorway), wrap strips folding the canvas out to the outer
poles, corner knots, upper ties, hem ties, four pegs with ropes, a teal mat and bedroll inside, and outside a storage
crate, two banded barrels, a ground lantern and two pale stones. Two lanterns glow (Neon glass + heat_glow sockets).

    import importlib, kit_models, m064; importlib.reload(kit_models); importlib.reload(m064); m064.build()

Build frame: studs, front -Y (the doorway), +X right, ground z 0, the ridge along Y on x 0. Every object ends with its
origin at its bbox bottom centre; o["m064_offset"] is that origin in the build frame. Names (spec 8, decision 14):
- CanvasTent (hero): everything above, one object of closed shells (no booleans). Collision precise.
- CanvasTentFrame (one X with its lashing and foot bands), CanvasTentPanel (one side panel), CanvasTentMat (mat +
  bedroll), CanvasTentCrate, CanvasTentBarrel, CanvasTentStone, CanvasTentPeg (stake, cap, band), CanvasTentLantern.
Colour (stage 4) is painted by role and by position inside the builders, never by facing; the dark interior is light.
Stages 5-6: the lantern glass is m064_glow at emission 1.0 (Neon); one heat_glow socket per lantern. See M064_spec.md.
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
import m048
import m051

NUM, TITLE, SHEET = 64, "A-Frame Tent", "M064"
OFF = "m064_offset"
PFX = "_m064_"
HERO = "CanvasTent"
FRAME_P, PANEL_P, MAT_P = "CanvasTentFrame", "CanvasTentPanel", "CanvasTentMat"
CRATE_P, BARREL_P, STONE_P = "CanvasTentCrate", "CanvasTentBarrel", "CanvasTentStone"
PEG_P, LANTERN_P = "CanvasTentPeg", "CanvasTentLantern"

TIMBER, WOOD_DARK, END_GRAIN = "m064_timber", "m064_wood_dark", "m064_end_grain"
CANVAS, CANVAS_DEEP = "m064_canvas", "m064_canvas_deep"
ROPE, ROPE_DEEP = "m064_rope", "m064_rope_deep"
MAT, METAL, GLOW = "m064_mat", "m064_metal", "m064_glow"
STONE, STONE_DEEP = "m064_stone", "m064_stone_deep"
NEON = 1.0

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
BURY = 0.05

# key -> (hex, roughness, metal, emission, low specular). Stage 4 writes the calibrated values here (spec "Stage 4").
PALETTE = {
    TIMBER: ("#A3501A", 0.85, 0.0, 0.0, True),
    WOOD_DARK: ("#844526", 0.9, 0.0, 0.0, True),
    END_GRAIN: ("#C7A690", 0.9, 0.0, 0.0, True),
    CANVAS: ("#FDE4BC", 0.95, 0.0, 0.0, True),
    CANVAS_DEEP: ("#E6C8A2", 0.95, 0.0, 0.0, True),
    ROPE: ("#C8925A", 0.95, 0.0, 0.0, True),
    ROPE_DEEP: ("#A06C3A", 0.95, 0.0, 0.0, True),
    MAT: ("#4F7674", 0.95, 0.0, 0.0, True),
    METAL: ("#48474B", 0.55, 0.4, 0.0, False),
    GLOW: ("#F8B00A", 0.5, 0.0, NEON, False),
    STONE: ("#B4A199", 0.92, 0.0, 0.0, True),
    STONE_DEEP: ("#978884", 0.92, 0.0, 0.0, True),
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions) and K.sample kinds ("all" = paper filtered)
TARGETS = {TIMBER: ((0xA3, 0x50, 0x1A), "brown"), WOOD_DARK: ((0x84, 0x45, 0x26), "brown"),
           END_GRAIN: ((0xC7, 0xA6, 0x90), "all"), CANVAS: ((0xFD, 0xE4, 0xBC), "all"),
           CANVAS_DEEP: ((0xE6, 0xC8, 0xA2), "all"), ROPE: ((0xC8, 0x92, 0x5A), "brown"),
           ROPE_DEEP: ((0xA0, 0x6C, 0x3A), "brown"), MAT: ((0x4F, 0x76, 0x74), "all"),
           METAL: ((0x48, 0x47, 0x4B), "all"), GLOW: ((0xF9, 0xB7, 0x07), "vivid"),
           STONE: ((0xB4, 0xA1, 0x99), "all"), STONE_DEEP: ((0x97, 0x88, 0x84), "all")}


def _glow_mats():
    """Blender preview of the Neon key as Roblox shows Neon: its own colour, unshaded (m009)."""
    for mat in bpy.data.materials:
        if not (mat.name.startswith("FB_m064_glow") and mat.node_tree):
            continue
        if list(mat.get("flintkit_spec", [0, 0, 0]))[2] < NEON:
            continue
        b = mat.node_tree.nodes.get("Principled BSDF")
        for lk in list(b.inputs["Base Color"].links):
            mat.node_tree.links.remove(lk)
        b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        if "Specular IOR Level" in b.inputs:
            b.inputs["Specular IOR Level"].default_value = 0.0


def palette():
    for k, (hexcol, rough, metal, emit, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, metal=metal, emit=emit, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, metal=metal, emit=emit, low_spec=low)
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m064_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k == "m064_" + tail), None)
            if k1 in PALETTE and k2 and pct.isdigit():
                K.fk().KIT_PALETTE.pop(key, None)
                K.mix_key(k1, k2, int(pct) / 100)
    _glow_mats()


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS); "all" kinds are sampled with the studio paper dropped, the Neon
    preview kept on every round. Returns {key: (hex, rendered)}."""
    keys = keys or list(TARGETS)
    set0, sample0 = K.set_colour, K.sample

    def set_colour(key, hexcol, **kw):
        set0(key, hexcol, **kw)
        _glow_mats()

    def sample(src, box, kind="green"):
        return M.sample(src, box, "all", paper=(242, 238, 230), tol=14) if kind == "all" else sample0(src, box, kind)
    K.set_colour, K.sample = set_colour, sample
    try:
        for k in keys:
            K.fk().material(k)
        _glow_mats()
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        K.set_colour, K.sample = set0, sample0
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


# ---- small helpers -----------------------------------------------------------------------------------------------------
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


def _shell(a, pts, faces, key, tint=1.0):
    """One closed shell (winding made consistent, flipped outward by volume). Returns (verts, faces)."""
    return m051._solid_rc(a, pts, faces, key, tint)


HEXA = m048.HEXA


def _box(a, lo, hi, key, tint=1.0, m=None):
    """Axis box lo..hi (optionally transformed by the 4x4 matrix m). Returns (verts, faces)."""
    pts = [Vector((x, y, z)) for z in (lo[2], hi[2]) for (x, y) in ((lo[0], lo[1]), (hi[0], lo[1]),
                                                                   (hi[0], hi[1]), (lo[0], hi[1]))]
    if m is not None:
        pts = [m @ p for p in pts]
    return _shell(a, pts, HEXA, key, tint)


def _texture(a, vs, amp, seed, scale=0.3):
    K.texture(a, vs, amp=amp, scale=scale, jitter=0.0, seed=seed)


def _newell(pts, closed=True):
    n = Vector()
    m = len(pts)
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p, q = pts[i], pts[(i + 1) % m]
        n += Vector(((p.y - q.y) * (p.z + q.z), (p.z - q.z) * (p.x + q.x), (p.x - q.x) * (p.y + q.y)))
    return n


def _up_for(path, closed):
    n = _newell(path, True)
    span = max((p - path[0]).length for p in path)
    if n.length > 1e-3 * max(span, 0.1) ** 2:
        return n.normalized()
    ch = path[-1] - path[0]
    u = ch.cross(Vector((0, 0, 1)))
    if u.length < 1e-4:
        u = ch.cross(Vector((1, 0, 0)))
    return u.normalized()


# ---- piece register ------------------------------------------------------------------------------------------------------
PIECES = []          # (kind, name, centroid in the build frame) per shell, in build order
ROPES = []           # open rope runs: name, end points, radius (both-ends contact check)
GEO = {}             # measured placements (report)


def _reg(kind, name, vs):
    PIECES.append((kind, name, sum((v.co for v in vs), Vector()) / len(vs)))


# ---- frame geometry (spec 2.2) -----------------------------------------------------------------------------------------
TAN = math.tan(math.radians(9.6))          # the one shared lean for poles and canvas (decision 4)
SEC = math.sqrt(1.0 + TAN * TAN)
CROSS_Z, TIP_Z, FOOT_X, FRAME_Y = 9.40, 11.0, 6.40, 3.40
POLE_H, POLE_CH, TIP_CH = 0.375, 0.10, 0.06
P_N = POLE_H + 0.005                        # each pole's axis plane off the frame plane (normal): 0.01 between poles
CAN_GAP = 0.02                              # canvas end outer face to the inner pole's inner face
END_N = -(P_N + POLE_H + CAN_GAP)           # canvas end outer face (normal offset from the frame plane)
CT = 0.10                                   # canvas thickness
FOOT_RINGS = (0.35, 0.80)                   # horizontal rings near the foot (weathered feet, by height)
OCT = [(POLE_H - POLE_CH, POLE_H), (POLE_H, POLE_H - POLE_CH), (POLE_H, -(POLE_H - POLE_CH)),
       (POLE_H - POLE_CH, -POLE_H), (-(POLE_H - POLE_CH), -POLE_H), (-POLE_H, -(POLE_H - POLE_CH)),
       (-POLE_H, POLE_H - POLE_CH), (-(POLE_H - POLE_CH), POLE_H)]


def plane_y(z, dn):
    """|y| of the plane parallel to the frame plane at normal offset dn (outward +) at height z."""
    return FRAME_Y + TAN * (CROSS_Z - z) + dn * SEC


def n_out(end):
    return Vector((0.0, end, TAN)).normalized()


def on_plane(x, z, dn, end):
    return Vector((x, end * plane_y(z, dn), z))


def pole_axis(end, which):
    sx = 1.0 if which == "outer" else -1.0
    dn = P_N if which == "outer" else -P_N
    F = on_plane(sx * FOOT_X, 0.0, dn, end)
    C = on_plane(0.0, CROSS_Z, dn, end)
    d = (C - F).normalized()
    en = n_out(end)
    ew = d.cross(en).normalized()
    offs = [ew * w + en * n for w, n in OCT]
    return {"F": F, "d": d, "en": en, "ew": ew, "offs": offs, "end": end, "which": which, "sx": sx}


def pole_section(P, c, m):
    """The pole prism's long edges cut by the plane (c, m)."""
    out = []
    for o in P["offs"]:
        q = P["F"] + o
        s = (c - q).dot(m) / P["d"].dot(m)
        out.append(q + P["d"] * s)
    return out


def pole_point(P, z):
    """The pole axis point at height z."""
    s = (z - P["F"].z) / P["d"].z
    return P["F"] + P["d"] * s


def _tip_len(P):
    """Axis length to the square-cut tip so the highest tip corner is at TIP_Z (the sheet's tips, front cell)."""
    k = (POLE_H - TIP_CH) / POLE_H
    top = max(o.z for o in P["offs"]) * k
    return (TIP_Z - top - P["F"].z) / P["d"].z


def pole(a, end, which, name=None):
    """One chamfered square pole (spec 1.4): an 8-sided prism (four broad, four narrow faces) from a horizontal foot
    cut on the ground, two horizontal rings near the foot (weathered feet blend), a square-cut tip with a 0.06 chamfer
    rim. 76 tris. Timber, the lowest bands blended toward wood_dark by height (spec 5.3)."""
    P = pole_axis(end, which)
    F, d = P["F"], P["d"]

    def ring_z(z):
        return [F + o + d * ((z - F.z - o.z) / d.z) for o in P["offs"]]
    L = _tip_len(P)
    k = (POLE_H - TIP_CH) / POLE_H
    rings = [ring_z(0.0)] + [ring_z(z) for z in FOOT_RINGS] + [[F + d * (L - TIP_CH) + o for o in P["offs"]],
                                                               [F + d * L + o * k for o in P["offs"]]]
    pts = [p for r in rings for p in r]
    n = 8
    faces = []
    bands = []
    for i in range(len(rings) - 1):
        bands.append(len(faces))
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, (i + 1) * n + j1, (i + 1) * n + j])
    faces.append(list(reversed(range(n))))
    faces.append([(len(rings) - 1) * n + j for j in range(n)])
    nm = name or f"pole_{'f' if end < 0 else 'b'}_{which}"
    vs, fs = _shell(a, pts, faces, TIMBER, _rt(nm, 0.04))
    _paint(a, fs[0:8] + [fs[-2]], _mix(TIMBER, WOOD_DARK, 0.5))
    _paint(a, fs[8:16], _mix(TIMBER, WOOD_DARK, 0.25))
    _texture(a, vs, 0.02, _seed(nm), scale=0.5)
    _reg("pole", nm, vs)
    P["name"] = nm
    P["tip_axis"] = F + d * L
    return P


# ---- ridge pole (spec 2.3; see the stage 1 notes for why it runs under the canvas fold) ----------------------------------
RIDGE_R = 0.275
STUB_X, STUB_L = -0.05, 0.50


def _oct_ring(c, e1, e2, r, n=8, rot=math.pi / 2):
    return [c + (e1 * math.cos(rot + 2 * math.pi * k / n) + e2 * math.sin(rot + 2 * math.pi * k / n)) * r
            for k in range(n)]


def _prism_y(a, x, zc, r, y_of, key, name, kind):
    """An 8-sided log along Y, a vertex up; each end vertex on its own end surface y_of(end, z)."""
    pts = []
    for end in (-1, 1):
        ring = _oct_ring(Vector((x, 0, zc)), Vector((1, 0, 0)), Vector((0, 0, 1)), r)
        for p in ring:
            pts.append(Vector((p.x, y_of(end, p.z), p.z)))
    faces = [list(reversed(range(8))), list(range(8, 16))]
    for j in range(8):
        j1 = (j + 1) % 8
        faces.append([j, j1, 8 + j1, 8 + j])
    vs, fs = _shell(a, pts, faces, TIMBER, _rt(name, 0.04))
    _reg(kind, name, vs)
    return vs


def ridge(a):
    """The ridge pole inside the canvas fold: its top vertex 0.01 under the fold's inner apex, its ends 0.01 short of
    the end pieces' inner faces (enclosed by canvas)."""
    zc = IN_APEX - 0.01 - RIDGE_R
    GEO["ridge_z"] = round(zc, 3)
    return _prism_y(a, 0.0, zc, RIDGE_R, lambda e, z: e * plane_y(z, END_N - CT - 0.01), TIMBER, "ridge", "ridge")


def stubs(a):
    """The ridge pole's ends as the side cell shows them: a short log butting the outer pole's outer face at each
    crossing (0.01 off), sticking out 0.5."""
    zc = IN_APEX - 0.01 - RIDGE_R
    out = []
    for end in (-1, 1):
        dn0 = P_N + POLE_H + 0.01

        def y_of(e, z, end=end, dn0=dn0):
            return end * (plane_y(z, dn0) if e == -end else plane_y(z, dn0) + STUB_L)
        out.append(_prism_y(a, STUB_X, zc, RIDGE_R, y_of, TIMBER, f"stub_{'f' if end < 0 else 'b'}", "stub"))
    return out


# ---- canvas (spec 2.4) -------------------------------------------------------------------------------------------------
APEX_Z, HEM_Z, HEM_X = 10.13, 0.40, 5.80
_SL = math.hypot(HEM_X, APEX_Z - HEM_Z)
DX, DZ = HEM_X / _SL, -(APEX_Z - HEM_Z) / _SL       # down-slope unit of the +X panel (x, z)
NX, NZ = -DZ, DX                                    # its outward normal (x, z)
IN_APEX = APEX_Z - CT / DX                          # the fold's inner apex
KSL = HEM_X / (APEX_Z - HEM_Z)                      # x per unit of drop along the outer surface
ROW_Z = (HEM_Z, HEM_Z + 0.30, HEM_Z + 0.60, (APEX_Z + HEM_Z) / 2)    # outer-surface rows: hem bands, mid
COLS = (0.0, 0.25, 0.5, 0.75, 1.0)
SAG_MID = (0.0, 0.14, 0.14, 0.14, 0.0)              # sag creases (geometry, decision 6), along the inward normal
SAG_HEM = (0.0, 0.0, 0.06, 0.0, 0.0)
SIDE_N = END_N + 0.01                               # side panels' end caps: 0.01 proud of the end pieces
TUCK = 0.025                                        # end pieces tuck this far into the side panels
TUCK_APEX = IN_APEX + TUCK / DX
HEM_BANDS = (0.5, 0.25)                             # canvas_deep share of the two hem bands (spec 5.5)
DOOR_APEX, DOOR_HW = 8.40, 2.80
STRIP_TOP, STRIP_T = 8.30, 0.08                     # wrap strips (canvas wrap round the outer pole)
TURN_TOP, TURN_W, TURN_T, TURN_TILT = 5.0, 0.35, 0.06, math.radians(20)


def _sag(ri, c):
    t = (ROW_Z[ri] - ROW_Z[0]) / (ROW_Z[3] - ROW_Z[0])
    return SAG_HEM[c] * (1 - t) + SAG_MID[c] * t


def _x_out(z):
    return KSL * (APEX_Z - z)


def _panel_pt(s, ri, c, inner, cols=COLS, dn=SIDE_N):
    """A side-panel vertex: side s, outer-surface row ri (4 = apex), column c, inner or outer surface."""
    if ri == 4:
        p = Vector((0.0, 0.0, IN_APEX if inner else APEX_Z))
    else:
        z = ROW_Z[ri]
        n = Vector((s * NX, 0.0, NZ))
        p = Vector((s * _x_out(z), 0.0, z)) - n * (_sag(ri, c) + (CT if inner else 0.0))
    ys = plane_y(p.z, dn)
    p.y = -ys + 2.0 * ys * cols[c]
    return p


def _profile(s_list=(-1, 1)):
    """Profile index -> (side, row) across the chevron: L hem .. L mid, apex, R mid .. R hem."""
    prof = [(-1, r) for r in range(4)] + [(0, 4)] + [(1, r) for r in (3, 2, 1, 0)]
    return prof


def _band_key(k_lo, k_hi, prof):
    """Hem-band key of the profile segment k_lo..k_hi (by position: rows 0-1 deepest, 1-2 half)."""
    rows = {prof[k_lo][1], prof[k_hi][1]}
    if rows == {0, 1}:
        return _mix(CANVAS, CANVAS_DEEP, HEM_BANDS[0])
    if rows == {1, 2}:
        return _mix(CANVAS, CANVAS_DEEP, HEM_BANDS[1])
    return CANVAS


def side_shell(a, canvas=None):
    """Both side panels and the ridge fold as one closed slab: a chevron section (9 outer + 9 inner verts) at five
    columns between the end planes, the middle row's three inner columns sunk 0.14 and the hem's middle 0.06 (the
    sheet's diagonal creases), hem bands, rims and end caps. 176 tris."""
    prof = _profile()
    nk = len(prof)
    pts, idx = [], {}
    for c in range(len(COLS)):
        for k, (s, r) in enumerate(prof):
            for inner in (0, 1):
                idx[(c, k, inner)] = len(pts)
                pts.append(_panel_pt(s if s else 1, r, c, inner))
    faces, keys = [], []
    for c in range(len(COLS) - 1):
        for k in range(nk - 1):
            key = _band_key(k, k + 1, prof)
            for inner in (0, 1):
                faces.append([idx[(c, k, inner)], idx[(c, k + 1, inner)], idx[(c + 1, k + 1, inner)],
                              idx[(c + 1, k, inner)]])
                keys.append(key)
        for k in (0, nk - 1):
            faces.append([idx[(c, k, 0)], idx[(c + 1, k, 0)], idx[(c + 1, k, 1)], idx[(c, k, 1)]])
            keys.append(_mix(CANVAS, CANVAS_DEEP, HEM_BANDS[0]))
    for c in (0, len(COLS) - 1):
        for k in range(nk - 1):
            faces.append([idx[(c, k, 0)], idx[(c, k + 1, 0)], idx[(c, k + 1, 1)], idx[(c, k, 1)]])
            keys.append(_band_key(k, k + 1, prof))
    vs, fs = _shell(a, pts, faces, CANVAS, _rt("side", 0.02))
    for f, key in zip(fs, keys):
        if key != CANVAS:
            f.material_index = a._mi(key)
    _texture(a, vs, 0.03, 641, scale=0.22)
    _reg("canvas", "canvas_side", vs)
    if canvas is not None:
        canvas.add(vs)
    return vs


def panel_part_fn(a):
    """CanvasTentPanel: one side panel (+X) as its own closed slab, the fold cut square at the apex (a top rim)."""
    PIECES.clear()
    prof = [(1, 4), (1, 3), (1, 2), (1, 1), (1, 0)]
    pts, idx = [], {}
    for c in range(len(COLS)):
        for k, (s, r) in enumerate(prof):
            for inner in (0, 1):
                idx[(c, k, inner)] = len(pts)
                if r == 4:
                    p = Vector((0.0, 0.0, IN_APEX if inner else APEX_Z))
                    if inner:
                        p = Vector((-CT * NX, 0.0, APEX_Z - CT * NZ))
                    ys = plane_y(p.z, SIDE_N)
                    p.y = -ys + 2 * ys * COLS[c]
                else:
                    p = _panel_pt(1, r, c, inner)
                pts.append(p)
    faces, keys = [], []
    nk = len(prof)
    for c in range(len(COLS) - 1):
        for k in range(nk - 1):
            key = _band_key(k, k + 1, [(1, r) for _, r in prof])
            for inner in (0, 1):
                faces.append([idx[(c, k, inner)], idx[(c, k + 1, inner)], idx[(c + 1, k + 1, inner)],
                              idx[(c + 1, k, inner)]])
                keys.append(key)
        for k in (0, nk - 1):
            faces.append([idx[(c, k, 0)], idx[(c + 1, k, 0)], idx[(c + 1, k, 1)], idx[(c, k, 1)]])
            keys.append(CANVAS if k == 0 else _mix(CANVAS, CANVAS_DEEP, HEM_BANDS[0]))
    for c in (0, len(COLS) - 1):
        for k in range(nk - 1):
            faces.append([idx[(c, k, 0)], idx[(c, k + 1, 0)], idx[(c, k + 1, 1)], idx[(c, k, 1)]])
            keys.append(_band_key(k, k + 1, [(1, r) for _, r in prof]))
    vs, fs = _shell(a, pts, faces, CANVAS, 1.0)
    for f, key in zip(fs, keys):
        if key != CANVAS:
            f.material_index = a._mi(key)
    _texture(a, vs, 0.03, 641, scale=0.22)
    _reg("canvas", "panel", vs)


def _xt(z):
    """The end pieces' outer edge: the panels' inner surface pushed TUCK into the slab."""
    return KSL * (TUCK_APEX - z)


def _xd(z):
    return DOOR_HW * (DOOR_APEX - z) / (DOOR_APEX - HEM_Z)


def _slab2d(a, end, pts2d, tris, boundary, key_of, name, kind="canvas", push=None, canvas=None):
    """A closed canvas slab in an end plane: 2D points (x, z) on the outer face (normal offset END_N), the inner face
    CT further in along the plane normal; tris on both faces, rim quads along the boundary loop. push = {index:
    extra inward offset} (the back's sag vertex). key_of(z centre) -> key."""
    nrm = n_out(end)
    outer = []
    for i, (x, z) in enumerate(pts2d):
        p = on_plane(x, z, END_N, end) - nrm * ((push or {}).get(i, 0.0))
        outer.append(p)
    inner = [p - nrm * CT for p in outer]
    n = len(outer)
    pts = outer + inner
    faces = [list(t) for t in tris] + [[n + t[2], n + t[1], n + t[0]] for t in tris]
    for i in range(len(boundary)):
        u, v = boundary[i], boundary[(i + 1) % len(boundary)]
        faces.append([u, v, n + v, n + u])
    vs, fs = _shell(a, pts, faces, CANVAS, _rt(name, 0.02))
    for f in fs:
        zc = sum(v.co.z for v in f.verts) / len(f.verts)
        k = key_of(zc)
        if k != CANVAS:
            f.material_index = a._mi(k)
    _texture(a, vs, 0.03, _seed(name), scale=0.22)
    _reg(kind, name, vs)
    if canvas is not None:
        canvas.add(vs)
    return vs, fs


def _hem_key(zc):
    if zc < ROW_Z[1]:
        return _mix(CANVAS, CANVAS_DEEP, HEM_BANDS[0])
    if zc < ROW_Z[2]:
        return _mix(CANVAS, CANVAS_DEEP, HEM_BANDS[1])
    return CANVAS


def back_piece(a, canvas=None):
    """The closed back triangle: hem bands and a centre vert sunk 0.10 (a gentle sag)."""
    z1, z2 = ROW_Z[1], ROW_Z[2]
    P = [(-_xt(HEM_Z), HEM_Z), (_xt(HEM_Z), HEM_Z), (_xt(z1), z1), (_xt(z2), z2), (0.0, TUCK_APEX),
         (-_xt(z2), z2), (-_xt(z1), z1)]
    G = ((P[3][0] + P[4][0] + P[5][0]) / 3, (P[3][1] + P[4][1] + P[5][1]) / 3)
    P.append(G)
    tris = [(0, 1, 2), (0, 2, 6), (6, 2, 3), (6, 3, 5), (5, 3, 7), (3, 4, 7), (4, 5, 7)]
    boundary = [0, 1, 2, 3, 4, 5, 6]
    return _slab2d(a, 1, P, tris, boundary, _hem_key, "canvas_back", push={7: 0.10}, canvas=canvas)


def front_piece(a, canvas=None):
    """The front: the end triangle minus the doorway (apex 8.40, 5.60 wide at the hem): two flaps joined above the
    opening, hem bands on the flaps."""
    z1, z2 = ROW_Z[1], ROW_Z[2]
    P = [(-_xt(HEM_Z), HEM_Z), (-DOOR_HW, HEM_Z), (-_xd(z1), z1), (-_xd(z2), z2), (0.0, DOOR_APEX),
         (_xd(z2), z2), (_xd(z1), z1), (DOOR_HW, HEM_Z), (_xt(HEM_Z), HEM_Z), (_xt(z1), z1), (_xt(z2), z2),
         (0.0, TUCK_APEX), (-_xt(z2), z2), (-_xt(z1), z1)]
    tris = [(0, 1, 2), (0, 2, 13), (13, 2, 3), (13, 3, 12),         # left flap hem bands
            (12, 3, 4), (12, 4, 11),                                 # left flap above
            (7, 8, 9), (7, 9, 6), (6, 9, 10), (6, 10, 5),            # right flap hem bands
            (11, 4, 5), (11, 5, 10)]                                 # right flap above
    boundary = list(range(14))
    return _slab2d(a, -1, P, tris, boundary, _hem_key, "canvas_front", canvas=canvas)


def _hexa(a, pts, key, name, kind, tint=1.0, canvas=None):
    vs, fs = _shell(a, pts, HEXA, key, tint)
    _reg(kind, name, vs)
    if canvas is not None:
        canvas.add(vs)
    return vs, fs


def wrap_strip(a, end, canvas=None):
    """The canvas wrap round the outer pole (sheet "Canvas Wrap around Pole"): a strip lying 0.012 off the +X panel's
    outer surface from the hem to z 8.3, from 0.04 inside the panel's end out to the outer pole's inner face (0.01
    off)."""
    n = Vector((NX, 0.0, NZ))
    corners = []
    for z in (HEM_Z, STRIP_TOP):
        base = Vector((_x_out(z), 0.0, z))
        for dn in (SIDE_N - 0.04 / SEC, P_N - POLE_H - 0.01):
            corners.append((base, dn))
    pts = []
    for off in (0.012, 0.012 + STRIP_T):
        for (base, dn) in (corners[0], corners[1], corners[3], corners[2]):
            p = base + n * off
            pts.append(Vector((p.x, end * plane_y(p.z, dn), p.z)))
    nm = f"wrap_{'f' if end < 0 else 'b'}"
    vs, fs = _hexa(a, pts, CANVAS, nm, "canvas", _rt(nm, 0.02), canvas)
    for f in fs:
        if sum(v.co.z for v in f.verts) / len(f.verts) < ROW_Z[1] + 0.2:
            f.material_index = a._mi(_mix(CANVAS, CANVAS_DEEP, HEM_BANDS[1]))
    return vs


def turned_strip(a, side, canvas=None):
    """A turned-back strip on a door edge (the sheet's lighter folded edge): hinged on the door edge on the flap's
    outer face, 0.35 wide, tilted 20 deg out, from the hem to z 5.0, 0.06 thick."""
    end = -1
    nrm = n_out(end)
    p0 = on_plane(side * DOOR_HW, HEM_Z, END_N + 0.008, end)
    p1 = on_plane(side * _xd(TURN_TOP), TURN_TOP, END_N + 0.008, end)
    along = (p1 - p0).normalized()
    perp = nrm.cross(along).normalized()
    if perp.x * side < 0:
        perp = -perp
    w = perp * math.cos(TURN_TILT) + nrm * math.sin(TURN_TILT)
    t = w.cross(along).normalized()
    if t.dot(nrm) < 0:
        t = -t
    q = [p0, p0 + w * TURN_W, p1 + w * TURN_W, p1]
    pts = q + [p + t * TURN_T for p in q]
    nm = f"turn_{'l' if side < 0 else 'r'}"
    vs, fs = _hexa(a, pts, CANVAS, nm, "canvas", _rt(nm, 0.02), canvas)
    return vs


class _Canvas:
    """The canvas shells as solids: signed distance (+ outside) by nearest surface and ray parity."""

    def __init__(self):
        self.items, self.cos, self.polys = [], [], []
        self.tree = None

    def add(self, vs):
        fs = K.faces_of(vs)
        idx = {v: i for i, v in enumerate(vs)}
        cos = [v.co.copy() for v in vs]
        polys = [[idx[v] for v in f.verts] for f in fs]
        lo = Vector((min(c.x for c in cos), min(c.y for c in cos), min(c.z for c in cos)))
        hi = Vector((max(c.x for c in cos), max(c.y for c in cos), max(c.z for c in cos)))
        self.items.append((BVHTree.FromPolygons(cos, polys), lo, hi))
        base = len(self.cos)
        self.cos += cos
        self.polys += [[base + i for i in p] for p in polys]
        self.tree = None

    def build(self):
        self.tree = BVHTree.FromPolygons(self.cos, self.polys)
        return self

    def sd(self, p):
        loc, nrm, i, d = self.tree.find_nearest(p)
        for t, lo, hi in self.items:
            if all(lo[k] - 1e-4 <= p[k] <= hi[k] + 1e-4 for k in range(3)) and m047._parity_in(t, p):
                return -d
        return d

    def normal(self, p):
        return self.tree.find_nearest(p)[1]


# ---- rope (twisted tubes, spec 2.6) --------------------------------------------------------------------------------------
def _groove(sides):
    """Strand roles by index round the twist (never by facing): one strand in four rope_deep; on 3-ply rope one
    strand half way to rope_deep."""
    return {0: ROPE_DEEP} if sides >= 4 else {0: _mix(ROPE, ROPE_DEEP, 0.5)}


def rope(a, path, rt, sides, closed, name, up=None, kind="rope"):
    path = [Vector(p) for p in path]
    if closed and len(path) % 2:
        raise ValueError(f"{name}: closed twisted rope needs an even point count")
    up = up if up is not None else _up_for(path, closed)
    vs, fs = m048._tube(a, path, rt, sides, closed, ROPE, groove=_groove(sides), tint=_rt(name, 0.03),
                        up=tuple(up), twist=True)
    _reg(kind, name, vs)
    if not closed:
        ROPES.append({"name": name, "ends": [list(path[0]), list(path[-1])], "rt": rt})
    return vs


def _trim(path, closed, rt, canvas, sink=0.02):
    """Rope path runs clear of the canvas: points whose centreline is at least rt - 0.03 outside the canvas are kept;
    each run end is carried on toward the next (dropped) point to sink into the canvas when it meets it steeply."""
    if canvas is None:
        return [(path, closed)]
    keep_d = rt - 0.03
    sd = [canvas.sd(p) for p in path]
    ok = [d >= keep_d for d in sd]
    if all(ok):
        return [(path, closed)]
    if not any(ok):
        return []
    n = len(path)
    if closed:
        start = next(i for i in range(n) if ok[i] and not ok[i - 1])
        order = [(start + j) % n for j in range(n)]
    else:
        order = list(range(n))
    runs, cur = [], []
    for i in order:
        if ok[i]:
            cur.append(i)
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)

    def ext(ik, idr):
        p0, p1 = path[ik], path[idr]
        if canvas.sd(p1) > -sink:
            return None
        lo, hi = 0.0, 1.0
        for _ in range(30):
            t = (lo + hi) / 2
            if canvas.sd(p0.lerp(p1, t)) > -sink:
                lo = t
            else:
                hi = t
        q = p0.lerp(p1, hi)
        dirv = (p1 - p0).normalized()
        if abs(dirv.dot(canvas.normal(q))) < 0.6:
            return None
        return q
    out = []
    for run in runs:
        pts = [path[i] for i in run]
        i0, i1 = run[0], run[-1]
        if closed or i0 > 0:
            q = ext(i0, (i0 - 1) % n)
            if q is not None:
                pts.insert(0, q)
        if closed or i1 < n - 1:
            q = ext(i1, (i1 + 1) % n)
            if q is not None:
                pts.append(q)
        if len(pts) >= 2:
            out.append((pts, False))
    return out


def rope_trim(a, path, rt, sides, closed, name, canvas, up=None):
    up = up if up is not None else _up_for(path, closed)
    runs = _trim(path, closed, rt, canvas)
    out = []
    for i, (pts, cl) in enumerate(runs):
        out.append(rope(a, pts, rt, sides, cl, name if len(runs) == 1 else f"{name}_{i}", up=up))
    GEO.setdefault("trimmed", {})[name] = [len(p) for p, _ in runs]
    return out


def _hull2(pts):
    pts = sorted(set((round(x, 7), round(y, 7)) for x, y in pts))

    def cross(o, p, q):
        return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def _pdist(q, H):
    n = len(H)
    inside = True
    best = 1e9
    for i in range(n):
        a_, b_ = H[i], H[(i + 1) % n]
        ex, ey = b_[0] - a_[0], b_[1] - a_[1]
        if ex * (q[1] - a_[1]) - ey * (q[0] - a_[0]) < 0:
            inside = False
        L2 = ex * ex + ey * ey
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((q[0] - a_[0]) * ex + (q[1] - a_[1]) * ey) / L2))
        best = min(best, math.hypot(q[0] - a_[0] - ex * t, q[1] - a_[1] - ey * t))
    return 0.0 if inside else best


def hull_loop(pts3, c, m, ref, offset, n, phase=0.0):
    """A rope loop hugging the convex hull of section points in the plane (c, m) at `offset` (rounded corners): n
    radial samples round the hull's centroid."""
    m = m.normalized()
    e1 = (ref - m * ref.dot(m)).normalized()
    e2 = m.cross(e1)
    P = [((p - c).dot(e1), (p - c).dot(e2)) for p in pts3]
    H = _hull2(P)
    cx = sum(x for x, _ in H) / len(H)
    cy = sum(y for _, y in H) / len(H)
    out = []
    for k in range(n):
        th = phase + 2 * math.pi * k / n
        ux, uy = math.cos(th), math.sin(th)
        lo, hi = 0.0, 10.0
        for _ in range(40):
            r = (lo + hi) / 2
            if _pdist((cx + ux * r, cy + uy * r), H) < offset:
                lo = r
            else:
                hi = r
        out.append(c + e1 * (cx + ux * hi) + e2 * (cy + uy * hi))
    return out


def _loop_at_x(loop, x0, end):
    """The point of a closed polyline at x = x0 on its outward (|y| larger) side."""
    best = None
    n = len(loop)
    for i in range(n):
        p, q = loop[i], loop[(i + 1) % n]
        if (p.x - x0) * (q.x - x0) <= 0 and abs(q.x - p.x) > 1e-9:
            r = p.lerp(q, (x0 - p.x) / (q.x - p.x))
            if best is None or end * r.y > end * best.y:
                best = r
    return best


# ---- lashing (spec 1.4, 2.6) ---------------------------------------------------------------------------------------------
WRAP_Z, RT_W = (9.02, 9.24), 0.11
RT_V, V_X, V_Z = 0.09, 0.36, 8.74
RING_R, RING_T = 0.17, 0.04


def lashing(a, end, P, canvas, tag):
    """Two horizontal wraps round both poles under the crossing (hugging their sections, trimmed where they meet the
    canvas end) and a V sling under them on the outer face, its ends sunk 0.04 into the lower wrap (the sheet's
    diamond / lantern hook). Returns the V's bottom point (the hanging lantern hooks it)."""
    loops = []
    for i, z in enumerate(WRAP_Z):
        c = Vector((0.0, end * plane_y(z, 0.0), z))
        m = Vector((0, 0, 1))
        pts = pole_section(P["outer"], c, m) + pole_section(P["inner"], c, m)
        path = hull_loop(pts, c, m, Vector((1, 0, 0)), RT_W - 0.02, 10, phase=math.pi / 10)
        loops.append(path)
        rope_trim(a, path, RT_W, 4, True, f"lash_{tag}_wrap{i}", canvas, up=m)
    S = _loop_at_x(loops[0], -V_X, end)
    E = _loop_at_x(loops[0], V_X, end)
    yB = end * (plane_y(8.55, P_N + POLE_H) + 0.475 + 0.04)
    Bl, Br = Vector((-0.10, yB, V_Z)), Vector((0.10, yB, V_Z))
    S0 = S + (Bl - S).normalized() * (RT_W - 0.04)
    E0 = E + (Br - E).normalized() * (RT_W - 0.04)
    path = [S0, S0.lerp(Bl, 0.5) - Vector((0, 0, 0.03)), Bl, Br, Br.lerp(E0, 0.5) - Vector((0, 0, 0.03)), E0]
    rope(a, path, RT_V, 4, False, f"lash_{tag}_v")
    GEO.setdefault("v_bottom", {})[tag] = [round(x, 3) for x in (Bl + Br) / 2]
    return (Bl + Br) / 2


# ---- corner knots, upper ties (spec 2.6) ---------------------------------------------------------------------------------
KNOT_Z, RT_K = 1.60, 0.11
TAIL_R, RT_T, TAIL_DROP = 0.24, 0.08, 0.45
TIE_Z, RT_U = 7.50, 0.08
KNOTS = {}


def _band(a, P, z, rt, sides, n, name, canvas):
    c = pole_point(P, z)
    pts = [c + o for o in P["offs"]]
    path = hull_loop(pts, c, P["d"], P["ew"], rt - 0.02, n, phase=math.pi / n)
    rope_trim(a, path, rt, sides, True, name, canvas, up=P["d"])
    return c, path


def knot(a, P, canvas, tail=True):
    """Corner knot at z 1.6: a chunky band round the pole (trimmed where it meets the canvas edge) and a tail loop
    lying on the canvas beside the pole (on the end piece by the inner poles, on the wrap strip by the outer ones)."""
    tag = P["name"].replace("pole_", "")
    c, path = _band(a, P, KNOT_Z, RT_K, 4, 8, f"knot_{tag}", canvas)
    KNOTS[tag] = {"c": c, "path": path}
    if not tail:
        return
    end = P["end"]
    if P["which"] == "inner":
        side = P["ew"] if P["ew"].x * (-c.x) > 0 else -P["ew"]
        cen = (c + P["en"] * (-POLE_H - CAN_GAP + RT_T + 0.005) + side * (POLE_H + TAIL_R + RT_T - 0.01)
               - P["d"] * TAIL_DROP)
        e1, e2 = side, P["d"]
        up = P["en"]
    else:
        n = Vector((NX, 0.0, NZ))
        zc = KNOT_Z - 0.55
        base = Vector((_x_out(zc), 0.0, zc)) + n * (0.012 + STRIP_T + RT_T + 0.005)
        face = plane_y(base.z, P_N - POLE_H)
        cen = Vector((base.x, end * (face - (TAIL_R + RT_T + 0.04) * SEC), base.z))
        e1, e2 = Vector((0, 1, 0)), Vector((DX, 0.0, DZ))
        up = n
    ring = [cen + (e1 * math.cos(2 * math.pi * k / 6) + e2 * math.sin(2 * math.pi * k / 6)) * TAIL_R
            for k in range(6)]
    rope(a, ring, RT_T, 3, True, f"tail_{tag}", up=up)
    KNOTS[tag]["tail"] = cen


def upper_tie(a, P, canvas):
    tag = P["name"].replace("pole_", "")
    _band(a, P, TIE_Z, RT_U, 3, 8, f"tie_{tag}", canvas)


# ---- door roll (spec 2.5) ------------------------------------------------------------------------------------------------
ROLL_Z, ROLL_R, ROLL_HL = 6.40, 0.40, 1.40
ROLL_BAND_X = 0.50                          # inside the opening (the bands pass behind the roll)
RT_RB = 0.065


def roll(a, canvas=None):
    """The rolled door flap across the top of the doorway: an 8-sided log touching both flaps (0.005 off), its ends
    two concentric rings (a recessed inner spiral), two rope bands."""
    end = -1
    nrm = n_out(end)
    ang = [math.radians(22.5 + 45 * k) for k in range(8)]
    offs = [Vector((0, math.cos(t), math.sin(t))) * ROLL_R for t in ang]
    on = on_plane(0.0, ROLL_Z, END_N, end)
    dist = max(-o.dot(nrm) for o in offs) + 0.005
    cy = on + nrm * dist
    GEO["roll_axis"] = [round(x, 3) for x in cy]
    pts = []
    for xs in (-ROLL_HL, ROLL_HL):
        pts += [Vector((xs, cy.y + o.y, cy.z + o.z)) for o in offs]
    for xs, sgn in ((-ROLL_HL, -1), (ROLL_HL, 1)):
        pts += [Vector((xs, cy.y + o.y * 0.55, cy.z + o.z * 0.55)) for o in offs]
        pts += [Vector((xs - sgn * 0.05, cy.y + o.y * 0.55, cy.z + o.z * 0.55)) for o in offs]
    faces = []
    for j in range(8):
        j1 = (j + 1) % 8
        faces.append([j, j1, 8 + j1, 8 + j])
    keys = [CANVAS] * 8
    for e, (rim0, in0, deep0) in enumerate(((0, 16, 24), (8, 32, 40))):
        for j in range(8):
            j1 = (j + 1) % 8
            faces.append([rim0 + j, rim0 + j1, in0 + j1, in0 + j])
            keys.append(CANVAS)
            faces.append([in0 + j, in0 + j1, deep0 + j1, deep0 + j])
            keys.append(CANVAS_DEEP)
        faces.append([deep0 + j for j in range(8)])
        keys.append(CANVAS_DEEP)
    vs, fs = _shell(a, pts, faces, CANVAS, 0.97)
    for f, k in zip(fs, keys):
        if k != CANVAS:
            f.material_index = a._mi(k)
    _reg("canvas", "roll", vs)
    if canvas is not None:
        canvas.add(vs)
    for i, xb in enumerate((-ROLL_BAND_X, ROLL_BAND_X)):
        R = ROLL_R + RT_RB - 0.035
        ring = [Vector((xb, cy.y + math.cos(2 * math.pi * k / 8) * R, cy.z + math.sin(2 * math.pi * k / 8) * R))
                for k in range(8)]
        rope(a, ring, RT_RB, 3, True, f"rollband_{i}", up=Vector((1, 0, 0)))
    GEO["roll_under"] = round(cy.z - ROLL_R, 3)


# ---- lanterns (spec 1.4) ------------------------------------------------------------------------------------------------
L_W, L_PLATE, L_GLASS_W, L_GLASS_H, L_BAND, L_ROOF, L_ROOF_TOP = 0.95, 0.12, 0.70, 0.95, 0.18, 0.35, 0.35
L_BAR = 0.09
L_H = L_PLATE + L_GLASS_H + L_BAND + L_ROOF            # 1.60


def lantern(a, base, rot, tag, hook=True):
    """A dark-metal lantern: base plate, Neon glass block, four corner bars, top band, pyramid roof; a ring on top
    (hanging) or a bail handle (standing). Returns (glass centre, ring top)."""
    R = Matrix.Translation(Vector(base)) @ Matrix.Rotation(rot, 4, "Z")
    h = L_W / 2
    z0 = 0.0
    out = []
    vs, _ = _box(a, (-h, -h, z0), (h, h, z0 + L_PLATE), METAL, _rt(tag + "p", 0.03), R)
    _reg("lmetal", f"{tag}_plate", vs)
    g = L_GLASS_W / 2
    vs, _ = _box(a, (-g, -g, L_PLATE - 0.005), (g, g, L_PLATE + L_GLASS_H + 0.005), GLOW, 1.0, R)
    _reg("glass", f"{tag}_glass", vs)
    bh = L_BAR / 2
    bc = h - bh - 0.005
    for i, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        vs, _ = _box(a, (sx * bc - bh, sy * bc - bh, L_PLATE - 0.01), (sx * bc + bh, sy * bc + bh,
                                                                       L_PLATE + L_GLASS_H + 0.01), METAL, 0.95, R)
        _reg("lmetal", f"{tag}_bar{i}", vs)
    zb = L_PLATE + L_GLASS_H
    vs, _ = _box(a, (-h, -h, zb), (h, h, zb + L_BAND), METAL, 1.0, R)
    _reg("lmetal", f"{tag}_band", vs)
    zr = zb + L_BAND - 0.005
    rb, rt_ = 0.50, L_ROOF_TOP / 2
    pts = [R @ Vector(p) for p in ((-rb, -rb, zr), (rb, -rb, zr), (rb, rb, zr), (-rb, rb, zr),
                                   (-rt_, -rt_, zr + L_ROOF), (rt_, -rt_, zr + L_ROOF), (rt_, rt_, zr + L_ROOF),
                                   (-rt_, rt_, zr + L_ROOF))]
    vs, _ = _shell(a, pts, HEXA, METAL, 1.03)
    _reg("lmetal", f"{tag}_roof", vs)
    top = zr + L_ROOF
    gc = R @ Vector((0, 0, L_PLATE + L_GLASS_H / 2))
    if hook:
        cz = top - 0.01 + RING_R + RING_T
        ring = [R @ Vector((0, math.cos(2 * math.pi * k / 8) * RING_R, cz + math.sin(2 * math.pi * k / 8) * RING_R))
                for k in range(8)]
        vs = m048._tube(a, ring, RING_T, 3, True, METAL, tint=0.9, up=tuple((R.to_3x3() @ Vector((1, 0, 0)))),
                        twist=True)[0]
        _reg("lmetal", f"{tag}_ring", vs)
        ring_top = R @ Vector((0, 0, cz + RING_R + RING_T))
    else:
        arc = [R @ Vector((math.cos(t) * 0.42, 0.0, zr + 0.06 + math.sin(t) * 0.55))
               for t in [math.radians(x) for x in (0, 36, 72, 108, 144, 180)]]
        vs = m048._tube(a, arc, 0.035, 3, False, METAL, tint=0.9, up=tuple(R.to_3x3() @ Vector((0, 1, 0))),
                        twist=True)[0]
        _reg("lmetal", f"{tag}_bail", vs)
        ring_top = R @ Vector((0, 0, top + 0.40))
    return gc, ring_top


# ---- pegs, peg ropes, hem ties (spec 2.6) ---------------------------------------------------------------------------------
PEG_S, PEG_H, CAP_S, CAP_H = 0.275, 1.06, 0.375, 0.30
PEG_BAND_Z, RT_PB, RT_PR = 0.85, 0.07, 0.07
# peg positions per corner knot (decision 7: each tied to its knot); the outer-pole pegs stand out beside the foot so
# their ropes clear the cap overhang
PEGS = {"f_inner": (-4.90, -6.20, 4), "f_outer": (5.55, -6.40, -6), "b_inner": (-4.90, 6.20, 8),
        "b_outer": (5.55, 6.40, -3)}
PEG_INFO = {}


def peg(a, x, y, rot_deg, tag):
    R = Matrix.Translation((x, y, 0)) @ Matrix.Rotation(math.radians(rot_deg), 4, "Z")
    vs, _ = _box(a, (-PEG_S, -PEG_S, 0.0), (PEG_S, PEG_S, PEG_H), WOOD_DARK, _rt(tag + "s", 0.05), R)
    _texture(a, vs, 0.03, _seed(tag), scale=1.0)
    _reg("stake", f"{tag}_stake", vs)
    vs, _ = _box(a, (-CAP_S, -CAP_S, PEG_H - 0.01), (CAP_S, CAP_S, PEG_H - 0.01 + CAP_H), END_GRAIN,
                 _rt(tag + "c", 0.04), R)
    _reg("cap", f"{tag}_cap", vs)
    c = Vector((x, y, PEG_BAND_Z))
    sq = [R @ Vector((sx * PEG_S, sy * PEG_S, PEG_BAND_Z)) for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
    path = hull_loop(sq, c, Vector((0, 0, 1)), Vector((1, 0, 0)), RT_PB - 0.02, 8, phase=math.pi / 8)
    rope(a, path, RT_PB, 3, True, f"{tag}_band", up=Vector((0, 0, 1)))
    PEG_INFO[tag] = {"c": c, "band": path}
    return path


def peg_rope(a, tag):
    """From the knot band's nearest point down to the peg band's nearest point, ends sunk 0.04 / 0.03 into the bands,
    a slight sag."""
    kb = KNOTS[tag]["path"]
    pb = PEG_INFO[tag]["band"]
    pc = PEG_INFO[tag]["c"]
    q1 = min(kb, key=lambda p: (p - pc).length)
    q2 = min(pb, key=lambda p: (p - q1).length)
    s0 = q1 + (q2 - q1).normalized() * (RT_K - 0.04)
    e0 = q2 + (q1 - q2).normalized() * (RT_PB - 0.03)
    sag = Vector((0, 0, -0.06))
    path = [s0, s0.lerp(e0, 1 / 3) + sag, s0.lerp(e0, 2 / 3) + sag, e0]
    rope(a, path, RT_PR, 3, False, f"pegrope_{tag}")


HEM_TIE_Y, RT_H = (-2.6, 0.0, 2.6), 0.065


def _hem_rim(s, y):
    """Centre of the hem rim of side s at y (the hem row interpolated across the columns, sag included)."""
    ys = plane_y(HEM_Z, SIDE_N)
    u = (y + ys) / (2 * ys)
    c = min(range(len(COLS) - 1), key=lambda i: 0 if COLS[i] <= u <= COLS[i + 1] else 9)
    t = (u - COLS[c]) / (COLS[c + 1] - COLS[c])
    po = _panel_pt(s, 0, c, False).lerp(_panel_pt(s, 0, c + 1, False), t)
    pi = _panel_pt(s, 0, c, True).lerp(_panel_pt(s, 0, c + 1, True), t)
    m = (po + pi) / 2
    m.y = y
    return m


def hem_tie(a, s, y, name):
    """A small U loop hanging from the hem rim to the ground: legs sunk 0.04 into the rim, the bottom on the ground."""
    down = Vector((s * DX, 0.0, DZ))
    pts = []
    for dy, leg in ((-0.12, 0), (0.12, 1)):
        rim = _hem_rim(s, y + dy)
        top = rim - down * 0.04
        mid = rim + down * 0.10
        bot = Vector((rim.x + s * 0.10, y + dy * 0.6, RT_H))
        pts.append((top, mid, bot))
    path = [pts[0][0], pts[0][1], pts[0][2], pts[1][2], pts[1][1], pts[1][0]]
    rope(a, path, RT_H, 3, False, name, up=Vector((s * NX, 0.0, NZ)))


# ---- interior (spec 2.7) ---------------------------------------------------------------------------------------------
MAT_X, MAT_Y0, MAT_Y1, MAT_T = 2.50, -3.00, 3.60, 0.22
BED_C, BED_R, BED_HL = (-0.90, 2.30), 0.75, 1.50


def mat(a):
    """The flat teal mat with two tan bands and a tan border strip at the doorway end (proud straps)."""
    vs, _ = _box(a, (-MAT_X, MAT_Y0, 0.0), (MAT_X, MAT_Y1, MAT_T), MAT, 1.0)
    _texture(a, vs, 0.03, 6401, scale=0.4)
    _reg("mat", "mat", vs)
    for i, (y0, y1) in enumerate(((-1.65, -1.15), (1.35, 1.85), (MAT_Y0 - 0.02, MAT_Y0 + 0.33))):
        vs, _ = _box(a, (-MAT_X - 0.02, y0, MAT_T - 0.01), (MAT_X + 0.02, y1, MAT_T + 0.025), ROPE,
                     _rt(f"band{i}", 0.03))
        _reg("matband", f"matband_{i}", vs)


def bedroll(a):
    """The rolled bedroll lying across at the back: 10-sided, resting on the mat, a tan strap, its ends three rings
    (teal / tan / teal from the outside in, recessed: the spiral)."""
    n = 10
    cx, cy = BED_C
    rr = BED_R
    cz = MAT_T + rr * math.cos(math.pi / n) + 0.005
    ang = [math.pi * 1.5 + math.pi / n + 2 * math.pi * k / n for k in range(n)]
    ring = [(math.cos(t), math.sin(t)) for t in ang]

    def rg(x, r, dx=0.0):
        return [Vector((x + dx, cy + c * r, cz + s * r)) for c, s in ring]
    xs = (-BED_HL, -0.15, 0.15, BED_HL)
    rads = (rr, rr + 0.02, rr + 0.02, rr)
    rings = [rg(cx + x, r) for x, r in zip(xs, rads)]
    for sgn, x in ((-1, -BED_HL), (1, BED_HL)):
        rings.append(rg(cx + x, rr * 0.70, -sgn * 0.02))
        rings.append(rg(cx + x, rr * 0.38, -sgn * 0.05))
    pts = [p for r in rings for p in r]
    faces, keys = [], []
    for i in range(3):
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, (i + 1) * n + j1, (i + 1) * n + j])
            keys.append(ROPE if i == 1 else MAT)
    for rim, r1, r2 in ((0, 4, 5), (3, 6, 7)):
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([rim * n + j, rim * n + j1, r1 * n + j1, r1 * n + j])
            keys.append(MAT)
            faces.append([r1 * n + j, r1 * n + j1, r2 * n + j1, r2 * n + j])
            keys.append(ROPE)
        faces.append([r2 * n + j for j in range(n)])
        keys.append(MAT)
    vs, fs = _shell(a, pts, faces, MAT, 0.97)
    for f, k in zip(fs, keys):
        if k != MAT:
            f.material_index = a._mi(k)
    _texture(a, vs, 0.03, 6402, scale=0.6)
    _reg("bedroll", "bedroll", vs)
    GEO["bedroll_z"] = round(cz, 3)


# ---- dressing (spec 2.8) --------------------------------------------------------------------------------------------------
CRATE = {"c": (-7.40, 2.60), "rot": 12.0, "W": 2.30, "H": 2.20}
CR_FW, CR_RD, CR_PT, CR_PL, CR_PH, CR_BW, CR_BT = 0.24, 0.05, 0.04, 0.42, 0.32, 0.20, 0.05


def crate(a, c=None, rot=None):
    """Storage crate: a box whose four sides have a 0.24 frame round a panel recessed 0.05, an X brace of three boards
    on each recessed panel, a plank lid (two seams), dark iron L plates at the eight corners."""
    cx, cy = c or CRATE["c"]
    R = Matrix.Translation((cx, cy, 0)) @ Matrix.Rotation(math.radians(rot if rot is not None else CRATE["rot"]),
                                                            4, "Z")
    W, H = CRATE["W"], CRATE["H"]
    h = W / 2
    # box corners (bottom 0-3, top 4-7, counter-clockwise from (-h, -h))
    cor = [Vector((-h, -h, 0)), Vector((h, -h, 0)), Vector((h, h, 0)), Vector((-h, h, 0)),
           Vector((-h, -h, H)), Vector((h, -h, H)), Vector((h, h, H)), Vector((-h, h, H))]
    pts = list(cor)
    faces, keys = [], []
    frame_key = _mix(WOOD_DARK, TIMBER, 0.35)
    # lid: two seams along y at x = -W/6, +W/6 (extra verts on the front and back top edges)
    s1, s2 = -W / 6, W / 6
    f1 = len(pts)
    pts += [Vector((s1, -h, H)), Vector((s2, -h, H)), Vector((s2, h, H)), Vector((s1, h, H))]
    faces += [[4, f1, f1 + 3, 7], [f1, f1 + 1, f1 + 2, f1 + 3], [f1 + 1, 5, 6, f1 + 2]]
    keys += ["lid0", "lid1", "lid2"]
    faces.append([3, 2, 1, 0])
    keys.append(WOOD_DARK)
    # sides: (outer corners bottom-left, bottom-right, top-right, top-left as seen from outside; top-edge extra verts)
    sides = [((0, 1, 5, 4), [f1 + 1, f1], Vector((0, -1, 0))), ((1, 2, 6, 5), [], Vector((1, 0, 0))),
             ((2, 3, 7, 6), [f1 + 3, f1 + 2], Vector((0, 1, 0))), ((3, 0, 4, 7), [], Vector((-1, 0, 0)))]
    panels = []
    for (b0, b1, t1, t0), extra, nrm in sides:
        P0, P1, P2, P3 = pts[b0], pts[b1], pts[t1], pts[t0]
        U = (P1 - P0).normalized()
        V = Vector((0, 0, 1))
        q = [P0 + U * CR_FW + V * CR_FW, P1 - U * CR_FW + V * CR_FW, P2 - U * CR_FW - V * CR_FW,
             P3 + U * CR_FW - V * CR_FW]
        qi = len(pts)
        pts += q
        ri = len(pts)
        pts += [p - nrm * CR_RD for p in q]
        faces.append([b0, b1, qi + 1, qi])
        faces.append([b1, t1, qi + 2, qi + 1])
        faces.append([t1] + extra + [t0, qi + 3, qi + 2])
        faces.append([t0, b0, qi, qi + 3])
        keys += [frame_key] * 4
        for k in range(4):
            k1 = (k + 1) % 4
            faces.append([qi + k, qi + k1, ri + k1, ri + k])
            keys.append(WOOD_DARK)
        faces.append([ri, ri + 1, ri + 2, ri + 3])
        keys.append(WOOD_DARK)
        panels.append((q, nrm, U))
    pts = [R @ p for p in pts]
    vs, fs = _shell(a, pts, faces, WOOD_DARK, 1.0)
    rng = random.Random(6403)
    for f, k in zip(fs, keys):
        if k.startswith("lid"):
            f.material_index = a._mi(WOOD_DARK)
            _tint(a, [f], 1.0 + (0.06, -0.05, 0.03)[int(k[-1])])
        elif k != WOOD_DARK:
            f.material_index = a._mi(k)
        else:
            _tint(a, [f], 1.0 + rng.uniform(-0.04, 0.04))
    _reg("crate", "crate_body", vs)
    # X braces: plank A corner to corner, plank B in two halves butting plank A's sides
    for si, (q, nrm, U) in enumerate(panels):
        cen = sum(q, Vector()) / 4 - nrm * CR_RD
        A_, B_ = W / 2 - CR_FW, H / 2 - CR_FW
        hw = CR_BW / 2
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
            out = [to3(u, v, -0.005) for u, v in quad] + [to3(u, v, CR_BT - 0.005) for u, v in quad]
            return out
        quadA = [dA * -LA + nA * -hw, dA * LA + nA * -hw, dA * LA + nA * hw, dA * -LA + nA * hw]
        vs, _ = _shell(a, hexa2d([(p.x, p.y) for p in quadA]), HEXA, frame_key, _rt(f"crA{si}", 0.04))
        _reg("plank", f"crate_A{si}", vs)
        for hi, sg in enumerate((1, -1)):
            sgnA = 1 if nA.dot(dB * sg) > 0 else -1
            corners = []
            for e in (-1, 1):
                t_in = (sgnA * hw - e * hw * nA.dot(nB)) / nA.dot(dB)
                corners.append((dB * t_in + nB * (e * hw), dB * (sg * LB) + nB * (e * hw)))
            quad = [corners[0][0], corners[0][1], corners[1][1], corners[1][0]]
            vs, _ = _shell(a, hexa2d([(p.x, p.y) for p in quad]), HEXA, frame_key, _rt(f"crB{si}{hi}", 0.04))
            _reg("plank", f"crate_B{si}_{hi}", vs)
    # corner L plates (top and bottom of each vertical edge), 0.004 off the faces
    g = 0.004
    for ci, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        for zi, (z0, z1) in enumerate(((0.0, CR_PH), (H - CR_PH, H))):
            ox, oy = sx * (h + g), sy * (h + g)
            L2 = [(ox + sx * CR_PT, oy - sy * CR_PL), (ox + sx * CR_PT, oy + sy * CR_PT), (ox - sx * CR_PL, oy + sy * CR_PT),
                  (ox - sx * CR_PL, oy), (ox, oy), (ox, oy - sy * CR_PL)]
            area = sum(L2[i][0] * L2[(i + 1) % 6][1] - L2[(i + 1) % 6][0] * L2[i][1] for i in range(6))
            if area < 0:
                L2 = L2[::-1]
            n6 = 6
            ppts = [R @ Vector((x, y, z0)) for x, y in L2] + [R @ Vector((x, y, z1)) for x, y in L2]
            pf = [list(reversed(range(n6))), list(range(n6, 2 * n6))]
            for i in range(n6):
                i1 = (i + 1) % n6
                pf.append([i, i1, n6 + i1, n6 + i])
            vs, _ = _shell(a, ppts, pf, METAL, _rt(f"pl{ci}{zi}", 0.04))
            _reg("plate", f"crate_plate{ci}{zi}", vs)


BARREL_R0, BARREL_R1, BARREL_H, HOOP = 1.00, 1.10, 2.70, 0.05
BARRELS = {"A": ((-7.30, -0.90), 0.0), "B": ((7.00, -3.40), 15.0)}


def barrel(a, c, rot_deg, tag):
    """A banded barrel: 8 staves (per-stave tint) bulging from Ø 2.0 to 2.2, two iron hoops proud 0.05 (rings of the
    body), a lid inset 0.06 with a bung."""
    n = 8
    R = Matrix.Translation((c[0], c[1], 0)) @ Matrix.Rotation(math.radians(rot_deg + 22.5), 4, "Z")

    def r_at(z):
        return BARREL_R0 + (BARREL_R1 - BARREL_R0) * (1 - ((z - BARREL_H / 2) / (BARREL_H / 2)) ** 2)
    prof = [(0.0, 0), (0.19, 0), (0.19, 1), (0.41, 1), (0.41, 0), (BARREL_H / 2, 0), (2.29, 0), (2.29, 1),
            (2.51, 1), (2.51, 0), (BARREL_H, 0)]
    ang = [2 * math.pi * k / n for k in range(n)]
    rings = []
    for z, hoop in prof:
        r = r_at(z) + (HOOP if hoop else 0.0)
        rings.append([Vector((math.cos(t) * r, math.sin(t) * r, z)) for t in ang])
    rin = 0.88 * BARREL_R0 / math.cos(math.pi / n) * math.cos(math.pi / n)
    rings.append([Vector((math.cos(t) * rin, math.sin(t) * rin, BARREL_H)) for t in ang])
    rings.append([Vector((math.cos(t) * rin, math.sin(t) * rin, BARREL_H - 0.06)) for t in ang])
    pts = [R @ p for r in rings for p in r]
    faces, keys, stave = [], [], []
    nr = len(prof)
    for i in range(nr - 1):
        hoop = prof[i][1] or prof[i + 1][1]
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, (i + 1) * n + j1, (i + 1) * n + j])
            keys.append(METAL if hoop else WOOD_DARK)
            stave.append(j)
    for i in (nr - 1, nr):
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, (i + 1) * n + j1, (i + 1) * n + j])
            keys.append(WOOD_DARK)
            stave.append(j)
    faces.append([(nr + 1) * n + j for j in range(n)])
    keys.append("lid")
    stave.append(-1)
    faces.append(list(reversed(range(n))))
    keys.append(WOOD_DARK)
    stave.append(-1)
    vs, fs = _shell(a, pts, faces, WOOD_DARK, 1.0)
    rng = random.Random(_seed(tag))
    st = [1.0 + rng.uniform(-0.05, 0.05) for _ in range(n)]
    lid_key = _mix(WOOD_DARK, TIMBER, 0.35)
    for f, k, s in zip(fs, keys, stave):
        if k == "lid":
            f.material_index = a._mi(lid_key)
        elif k != WOOD_DARK:
            f.material_index = a._mi(k)
        if s >= 0 and k == WOOD_DARK:
            _tint(a, [f], st[s])
    _reg("barrel", f"barrel_{tag}", vs)
    bc = R @ Vector((0.35, -0.25, BARREL_H - 0.06))
    br = 0.175
    bp = [Vector((bc.x + math.cos(2 * math.pi * k / 6) * br, bc.y + math.sin(2 * math.pi * k / 6) * br, bc.z + z))
          for z in (-0.005, 0.08) for k in range(6)]
    bfa = [list(reversed(range(6))), list(range(6, 12))] + [[k, (k + 1) % 6, 6 + (k + 1) % 6, 6 + k] for k in range(6)]
    vs, _ = _shell(a, bp, bfa, METAL, 0.95)
    _reg("bung", f"barrel_{tag}_bung", vs)


STONES = {"S1": ((-6.62, 0.75), (1.10, 1.00, 0.80), 25.0, 641), "S2": ((-7.60, -3.30), (0.90, 0.80, 0.65), 40.0, 642)}


def stone(a, c, size, rot_deg, seed, tag):
    """A chunky pale faceted block: a box with two top corners broken off and a little jitter, a flat bottom."""
    rng = random.Random(seed)
    sx, sy, sz = size[0] / 2, size[1] / 2, size[2]
    R = Matrix.Translation((c[0], c[1], 0)) @ Matrix.Rotation(math.radians(rot_deg), 4, "Z")
    pts = [Vector((x * sx * rng.uniform(0.92, 1.0), y * sy * rng.uniform(0.92, 1.0), 0.0))
           for x, y in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
    broken = (0, 2)
    for k, (x, y) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        top = Vector((x * sx * rng.uniform(0.85, 0.95), y * sy * rng.uniform(0.85, 0.95), sz * rng.uniform(0.92, 1.0)))
        if k in broken:
            cut = rng.uniform(0.28, 0.38)
            pts += [top - Vector((x * sx * cut, 0, 0)), top - Vector((0, y * sy * cut, 0)),
                    top - Vector((0, 0, sz * cut * 1.1))]
        else:
            pts.append(top)
    pts = [R @ p for p in pts]
    vs, fs, _ = m051._hull(a, pts, STONE, _rt(tag, 0.03))
    for f in fs:
        if f.is_valid and f.calc_center_median().z < 0.30 * sz:
            f.material_index = a._mi(_mix(STONE, STONE_DEEP, 0.5))
    _texture(a, vs, 0.05, seed, scale=1.2)
    _reg("stone", f"stone_{tag}", vs)


# ---- assemblies -----------------------------------------------------------------------------------------------------------
GROUND_LANTERN = ((-6.50, -2.60), 20.0)
FX = []                       # (kind, build-frame point, overrides) for the hero's sockets


def _fx_spec(rng):
    return {"emitters": [{"name": "Halo", "texture": "glow_soft", "color": ["#FFC23A", "#FF9A1E"], "size": [1.3, 1.5],
                          "transparency": [0.65, 1.0], "lifetime": [1.0, 1.5], "rate": 2, "speed": [0, 0.05],
                          "spread": 0, "light_emission": 1.0}],
            "light": {"color": "#FFB347", "brightness": 1.0, "range": rng, "flicker": True}}


def hero_all(a):
    PIECES.clear()
    ROPES.clear()
    GEO.clear()
    KNOTS.clear()
    PEG_INFO.clear()
    FX.clear()
    P = {}
    for end in (-1, 1):
        for w in ("outer", "inner"):
            P[(end, w)] = pole(a, end, w)
    ridge(a)
    stubs(a)
    cv = _Canvas()
    side_shell(a, cv)
    back_piece(a, cv)
    front_piece(a, cv)
    for end in (-1, 1):
        wrap_strip(a, end, cv)
    for s in (-1, 1):
        turned_strip(a, s, cv)
    roll(a, cv)
    cv.build()
    B = None
    for end in (-1, 1):
        b = lashing(a, end, {"outer": P[(end, "outer")], "inner": P[(end, "inner")]}, cv, "f" if end < 0 else "b")
        if end < 0:
            B = b
    for (end, w), Pp in P.items():
        knot(a, Pp, cv)
        if end < 0:
            upper_tie(a, Pp, cv)
    # hanging lantern on the front V (ring hooked over its bottom), ground lantern by barrel A
    base_z = B.z + RT_V - (RING_R - RING_T) + 0.01 - RING_R - RING_T + 0.01 - L_H
    gc, top = lantern(a, (B.x, B.y, base_z), 0.0, "lantern_hang", hook=True)
    FX.append(("heat_glow", gc, _fx_spec(12)))
    GEO["lantern_hang"] = {"base_z": round(base_z, 3), "top": round(base_z + L_H, 3), "glass": [round(x, 3) for x in gc]}
    (gx, gy), grot = GROUND_LANTERN
    gc2, _ = lantern(a, (gx, gy, 0.0), math.radians(grot), "lantern_ground", hook=False)
    FX.append(("heat_glow", gc2, _fx_spec(8)))
    for tag, (x, y, r) in PEGS.items():
        peg(a, x, y, r, f"peg_{tag}")
        PEG_INFO[tag] = PEG_INFO.pop(f"peg_{tag}")
        peg_rope(a, tag)
    for s in (-1, 1):
        for i, y in enumerate(HEM_TIE_Y):
            hem_tie(a, s, y, f"hemtie_{'l' if s < 0 else 'r'}{i}")
    mat(a)
    bedroll(a)
    crate(a)
    for tag, (c, r) in BARRELS.items():
        barrel(a, c, r, tag)
    for tag, (c, size, r, seed) in STONES.items():
        stone(a, c, size, r, seed, tag)


def frame_part(a):
    """CanvasTentFrame: the front X with its lashing (closed wraps, the V) and two foot bands (no canvas tails)."""
    PIECES.clear()
    ROPES.clear()
    KNOTS.clear()
    P = {w: pole(a, -1, w) for w in ("outer", "inner")}
    lashing(a, -1, P, None, "f")
    for w in P:
        knot(a, P[w], None, tail=False)


def mat_part(a):
    PIECES.clear()
    ROPES.clear()
    mat(a)
    bedroll(a)


def crate_part(a):
    PIECES.clear()
    crate(a, (0.0, 0.0), 0.0)


def barrel_part(a):
    PIECES.clear()
    barrel(a, (0.0, 0.0), 0.0, "A")


def stone_part(a):
    PIECES.clear()
    c, size, r, seed = STONES["S1"]
    stone(a, (0.0, 0.0), size, 0.0, seed, "S1")


def peg_part(a):
    PIECES.clear()
    ROPES.clear()
    peg(a, 0.0, 0.0, 0.0, "peg")


LANTERN_INFO = {}


def lantern_part(a):
    PIECES.clear()
    gc, top = lantern(a, (0.0, 0.0, 0.0), 0.0, "lantern", hook=True)
    LANTERN_INFO["glass"] = gc
    LANTERN_INFO["hang"] = top


NOTES = {
    HERO: "A-frame canvas tent: two X frames of chamfered square poles (side by side, leaning out 9.6 deg) with rope "
          "lashings, a cream canvas of closed slabs (sagging side panels over a hidden ridge, closed back, open "
          "doorway with turned-back flaps and a door roll), corner knots, pegs, a teal mat and bedroll inside; a "
          "crate, two barrels, a ground lantern and two stones outside. Two Neon lanterns with heat_glow halos. "
          "Walk-in doorway (Requires Manual Validation in Studio). Sheet header 66/132.",
    FRAME_P: "A-Frame Pole: one X of two side-by-side chamfered poles with the crossing lashing and foot bands",
    PANEL_P: "Canvas Panel (Left / Right): one sloped side panel with its sag creases (the other side is the same mesh "
             "turned 180 deg)",
    MAT_P: "Tent Mat (Rolled + Flat): teal mat with tan bands and a rolled bedroll",
    CRATE_P: "Storage Crate: framed box with X braces, iron corner plates and a plank lid",
    BARREL_P: "Barrel: eight-stave banded barrel with two iron hoops and a bunged lid",
    STONE_P: "Stone (x2): pale faceted block with broken corners (the smaller is this scaled in Studio)",
    PEG_P: "Peg (x4): square stake with a pale cap block and a rope band",
    LANTERN_P: "Lantern: dark-metal lantern with Neon amber glass and a hanging ring (heat_glow halo)",
}
COLLISION = {HERO: "precise", FRAME_P: "precise", PANEL_P: "hull", MAT_P: "none", CRATE_P: "box",
             BARREL_P: "hull", STONE_P: "hull", PEG_P: "none", LANTERN_P: "none"}


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
    PIECES.clear()
    ROPES.clear()
    fn(a)
    o = a.finish(collection=M.coll(NUM, TITLE), mark_asset=not temp, origin=None)
    K.drop_unused_slots(o)
    if not temp:
        K.tag(o, SHEET, TITLE, role, COLLISION[name], budget, NOTES[name])
    o[OFF] = [0.0, 0.0, 0.0]
    o.location = (0, 0, 0)
    o["m064_pieces"] = json.dumps([[k, n_, [round(x, 5) for x in c]] for k, n_, c in PIECES])
    o["m064_ropes"] = json.dumps(ROPES)
    bpy.context.view_layer.update()
    return o


def _recentre(o):
    bc = m012._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


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
    lg["uv_cut"] = m012._uv_unfold(o)
    K.drop_unused_slots(o)
    return lg


def _make(name, fn, role="part", budget=1000, temp=False):
    t0 = time.time()
    o = _new(name, fn, role, budget, temp=temp)
    lg = _post(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


# ---- checks ---------------------------------------------------------------------------------------------------------------
CAT = {"pole": "wood", "ridge": "wood", "stub": "wood", "stake": "wood", "cap": "wood", "crate": "wood",
       "plank": "wood", "barrel": "wood", "plate": "metal", "bung": "metal", "lmetal": "metal", "glass": "glass",
       "canvas": "canvas", "rope": "rope", "mat": "mat", "matband": "mat", "bedroll": "mat", "stone": "stone"}
SINK_LIMIT = {("rope", "rope"): 0.08}       # rope ends sunk into the bands / wraps they leave (joins)


def _shells(o):
    """bmesh, shell id per face, shell count, faces per shell, and (kind, name) per shell matched to the register."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    groups = [[] for _ in range(n)]
    for f in bm.faces:
        groups[ids[f.index]].append(f)
    off = Vector(o[OFF]) if OFF in o else Vector()
    reg = [(k, nm, Vector(c)) for k, nm, c in json.loads(o.get("m064_pieces", "[]"))]
    labels, used = [], set()
    for fs in groups:
        vs = list({v for f in fs for v in f.verts})
        c = sum((v.co for v in vs), Vector()) / len(vs) + off
        best = min(((i, (rc - c).length) for i, (_, _, rc) in enumerate(reg) if i not in used),
                   key=lambda x: x[1], default=(None, 0))
        if best[0] is not None and best[1] < 0.06:
            used.add(best[0])
            labels.append(reg[best[0]][:2])
        else:
            labels.append(("?", "?"))
    return bm, ids, n, groups, labels


def shells_report(o):
    """Per shell: kind, name, tris, non-manifold edges and verts, boundary edges, winding errors (manifold edges whose
    two faces run the same way round), self-intersecting face pairs, signed volume."""
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
    """No floating pieces (STAGES): per shell its nearest gap to another shell (0 where triangles intersect) or the
    ground, and whether it chains by contact to the ground. seats = [(name, name)] pair gaps to report."""
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
    """Nothing buried (STAGES): per shell pair, the deepest vert / face centre of one inside the other (ray parity,
    depth to its surface), judged against BURY (SINK_LIMIT for rope joins); and shells wholly inside others."""
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
            dmax = 0.0
            for j, p in enumerate(A["pts"]):
                if not all(B["lo"][k] - 1e-4 <= p[k] <= B["hi"][k] + 1e-4 for k in range(3)):
                    continue
                if m047._parity_in(B["tree"], p):
                    inside_any[j] = True
                    dmax = max(dmax, B["tree"].find_nearest(p)[3])
            if dmax <= 0:
                continue
            pair = (A["cat"], B["cat"])
            worst[pair] = max(worst.get(pair, 0.0), dmax)
            lim = SINK_LIMIT.get(pair, BURY)
            if dmax > lim + 1e-3:
                over.append({"shell": A["name"], "in": B["name"], "depth": round(dmax, 3)})
        if all(inside_any):
            hidden.append(A["name"])
    bm.free()
    return {"worst_depth": {f"{a_}>{b_}": round(d, 3) for (a_, b_), d in sorted(worst.items())},
            "over_limit": over, "fully_hidden": hidden, "buried": len(over) + len(hidden)}


def rope_ends_report(o):
    """Decision 7: every open rope touches what it ties at both ends: each end point's gap to the nearest other shell
    (surface distance minus the rope radius, 0 when the end is inside another shell)."""
    bm, ids, n, groups, labels = _shells(o)
    off = Vector(o[OFF])
    fsh = [ids[f.index] for f in bm.faces]
    tree = BVHTree.FromBMesh(bm)
    byname = {labels[k][1]: k for k in range(n)}
    out, bad = {}, []
    for r in json.loads(o.get("m064_ropes", "[]")):
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


def _hero_tree(o, skip_kinds=()):
    bm, ids, n, groups, labels = _shells(o)
    off = Vector(o[OFF])
    cos, polys, owner = [], [], []
    keep = [k for k in range(n) if labels[k][0] not in skip_kinds]
    items = []
    for k in keep:
        vs = list({v for f in groups[k] for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        co = [v.co + off for v in vs]
        pl = [[vi[v] for v in f.verts] for f in groups[k]]
        lo = Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co)))
        hi = Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co)))
        items.append((labels[k][1], BVHTree.FromPolygons(co, pl), lo, hi))
        base = len(cos)
        cos += co
        polys += [[base + i for i in p] for p in pl]
        owner += [labels[k][1]] * len(pl)
    bm.free()
    return BVHTree.FromPolygons(cos, polys), owner, items


PROXY = ((1.0, 0.5, 0.25, 4.4), (0.55, 0.5, 4.4, 5.5))     # (half x, half y, z0, z1): body, head (spec 2.9)


def walk_report(o):
    """Spec 2.9: a 2 x 1 x 5.5 proxy (head 1.1 wide above 4.4) walks from y -8 in through the doorway to the mat at
    x 0: the nearest hero surface to its sampled surface along the way (mat and bedroll excepted: the mat is the step);
    the door's clear width at z 4.4 and 5.5, the canvas clear width inside at z 5.5, the roll underside and the hanging
    lantern's bottom."""
    tree, owner, items = _hero_tree(o, skip_kinds=("mat", "matband", "bedroll"))
    samples = []
    for hx, hy, z0, z1 in PROXY:
        for i in range(9):
            for j in range(9):
                u, w = -1 + 2 * i / 8, -1 + 2 * j / 8
                z = z0 + (z1 - z0) * j / 8
                samples += [Vector((hx * u, -hy, z)), Vector((hx * u, hy, z)), Vector((-hx, hy * u, z)),
                            Vector((hx, hy * u, z)), Vector((hx * u, hy * w, z1))]
    worst, at, who = 9.0, None, None
    y = -8.0
    while y <= 0.51:
        for s in samples:
            p = s + Vector((0, y, 0))
            loc, nrm, fi, d = tree.find_nearest(p)
            if d < worst:
                worst, at, who = d, round(y, 2), owner[fi]
        y += 0.1
    yd = -plane_y(4.4, END_N - CT / 2)

    def clear(z, ypos):
        w = 0.0
        for sgn in (-1, 1):
            h = tree.ray_cast(Vector((0, ypos, z)), Vector((sgn, 0, 0)), 20)
            w += h[3] if h[0] is not None else 20
        return round(w, 3)
    res = {"min_clearance": round(worst, 3), "at_y": at, "nearest": who,
           "door_width_4.4": clear(4.4, -plane_y(4.4, END_N - CT / 2)),
           "door_width_5.5": clear(5.5, -plane_y(5.5, END_N - CT / 2)),
           "inside_width_5.5": clear(5.5, 0.0), "roll_under": GEO.get("roll_under"),
           "lantern_bottom": (GEO.get("lantern_hang") or {}).get("base_z"), "door_y": round(yd, 3)}
    return res


def placement_report(o):
    """Measured targets (spec 4.4): pole tips, crossing, tip spacing, door apex and hem width, ridge and hem canvas
    lengths, the dressing clearances to the hem line and to each other."""
    off = Vector(o[OFF])
    me = o.data
    out = {}
    P = {(e, w): pole_axis(e, w) for e in (-1, 1) for w in ("outer", "inner")}
    tips = {}
    for (e, w), Pp in P.items():
        tips[f"{e}{w}"] = round(Pp["F"].z + Pp["d"].z * _tip_len(Pp), 3)
    out["tip_axis_z"] = tips
    fo, fi = P[(-1, "outer")], P[(-1, "inner")]
    to = fo["F"] + fo["d"] * _tip_len(fo)
    ti = fi["F"] + fi["d"] * _tip_len(fi)
    out["tip_spacing_x"] = round(abs(to.x - ti.x), 3)
    out["crossing_z"] = CROSS_Z
    out["door_apex"] = DOOR_APEX
    out["door_hem_width"] = 2 * DOOR_HW
    out["ridge_len_outer"] = round(2 * plane_y(APEX_Z, SIDE_N), 3)
    out["hem_len"] = round(2 * plane_y(HEM_Z, SIDE_N), 3)
    zs = [v.co.z for v in me.vertices]
    out["height"] = round(max(zs) - min(zs), 3)
    out["size"] = [round(d, 3) for d in o.dimensions]
    return out


# ---- build ---------------------------------------------------------------------------------------------------------------
PARTS = ((FRAME_P, frame_part), (PANEL_P, panel_part_fn), (MAT_P, mat_part), (CRATE_P, crate_part),
         (BARREL_P, barrel_part), (STONE_P, stone_part), (PEG_P, peg_part), (LANTERN_P, lantern_part))
TARGET_SIZE = ((16.9, 0.5), (13.2, 0.7), (11.0, 0.3))    # hero W (X), D (Y), H (Z) +- tolerance (decision 1)
HERO_BUDGET = 4000
SEATS = [("canvas_side", "pole_f_inner"), ("canvas_side", "pole_b_inner"), ("canvas_front", "pole_f_inner"),
         ("canvas_back", "pole_b_inner"), ("wrap_f", "pole_f_outer"), ("wrap_b", "pole_b_outer"),
         ("wrap_f", "canvas_side"), ("wrap_b", "canvas_side"), ("ridge", "canvas_side"), ("stub_f", "pole_f_outer"),
         ("stub_b", "pole_b_outer"), ("pole_f_outer", "pole_f_inner"), ("pole_b_outer", "pole_b_inner"),
         ("roll", "canvas_front"), ("lantern_hang_ring", "lash_f_v"), ("turn_l", "canvas_front"),
         ("turn_r", "canvas_front"), ("bedroll", "mat")]


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m064_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", HERO))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def _sockets(h):
    """Stages 5-6: one heat_glow socket per lantern at its glass centre, overridden to a steady warm halo (decision
    13)."""
    for c in [c for c in h.children if c.get("vfx_kind")]:
        bpy.data.objects.remove(c, do_unlink=True)
    off = Vector(h[OFF])
    made = []
    for kind, p, kw in FX:
        made.append(K.socket(h, kind, Vector(p) - off, **kw))
    return made


def export_stats(objs):
    """What the exporter's STATS line would report for these objects: VFX sockets and glow (Neon) keys."""
    out = {}
    for o in objs:
        socks = [c for c in o.children_recursive if c.get("vfx_kind")]
        glow = sorted({m.name[3:] for m in o.data.materials
                       if list(m.get("flintkit_spec", [0, 0, 0]))[2] >= NEON})
        out[o.name] = {"vfx_sockets": len(socks), "kinds": [c["vfx_kind"] for c in socks], "glow_keys": glow}
    return out


def build(render=True, parts=True, close=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn)
        lp = objs[LANTERN_P]
        off = Vector(lp[OFF])
        lp["m064_hang"] = [round(x, 3) for x in LANTERN_INFO["hang"] - off]
        for c in [c for c in lp.children if c.get("vfx_kind")]:
            bpy.data.objects.remove(c, do_unlink=True)
        K.socket(lp, "heat_glow", LANTERN_INFO["glass"] - off, **_fx_spec(12))
    h, log["hero"] = _make(HERO, hero_all, "hero", HERO_BUDGET)
    geo = json.loads(json.dumps(GEO, default=lambda v: [round(x, 3) for x in v]))
    _sockets(h)
    off = Vector(h[OFF])
    h["m064_door"] = [round(x, 3) for x in Vector((0.0, -plane_y(HEM_Z, END_N), 0.0)) - off]
    h["m064_inside"] = [round(x, 3) for x in Vector((0.0, 0.0, 0.0)) - off]
    _cleanup_tmp()
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.2f} x {d.y:.2f} x {d.z:.2f}"
    audits = [M.audit(o) for o in order]
    thin = {o.name: m012._thin(o, 2.0) for o in order}
    shells = {o.name: shells_report(o) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = HERO_BUDGET if o is h else 999
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
                    problems.append(f"{o.name} shell {i} ({s['name']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['name']}): not closed outward (volume {s['volume']})")
            if s["kind"] == "?":
                problems.append(f"{o.name} shell {i}: not matched to a built piece")
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
            problems.append(f"{n_}: buried {b['over_limit']} hidden {b['fully_hidden']}")
    ropes = {o.name: rope_ends_report(o) for o in order if json.loads(o.get("m064_ropes", "[]"))}
    for n_, r in ropes.items():
        if r["loose"]:
            problems.append(f"{n_}: rope ends not touching {r['loose']}")
    walk = walk_report(h)
    if walk["min_clearance"] < 0.05:
        problems.append(f"{HERO}: walk proxy clearance {walk['min_clearance']} at y {walk['at_y']} ({walk['nearest']})")
    for k, lim in (("door_width_4.4", 2.6), ("door_width_5.5", 1.8), ("inside_width_5.5", 5.0)):
        if walk[k] < lim:
            problems.append(f"{HERO}: {k} {walk[k]} under {lim}")
    place = placement_report(h)
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    for n_, t in thin.items():
        if t["under"]:
            problems.append(f"{n_}: {t['under']} faces with a corner under 2 deg (min {t['min_deg']})")
    winding = {o.name: sum(s["winding_errors"] for s in shells[o.name]) for o in order}
    bowties = {o.name: au["nonmanifold_verts"] for o, au in zip(order, audits)}
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    stats = export_stats(order)
    if stats[HERO]["vfx_sockets"] != 2:
        problems.append(f"{HERO}: {stats[HERO]['vfx_sockets']} sockets (2 wanted)")
    if LANTERN_P in stats and stats[LANTERN_P]["vfx_sockets"] != 1:
        problems.append(f"{LANTERN_P}: {stats[LANTERN_P]['vfx_sockets']} sockets (1 wanted)")
    kinds = {}
    for s in shells[HERO]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts", "origin_offset", "transforms_applied")} for au in audits],
           "hero_shells": kinds, "contact": contact, "bury": bury, "rope_ends": ropes, "walk": walk,
           "placement": place, "winding": winding, "bowties": bowties, "thin": thin, "log": log, "geo": geo,
           "problems": problems, "uv": uv, "export_stats": stats,
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "stored": {"m064_door": h.get("m064_door"), "m064_inside": h.get("m064_inside"),
                      "m064_hang": objs[LANTERN_P].get("m064_hang") if LANTERN_P in objs else None},
           "sockets": {o.name: [{"kind": c["vfx_kind"], "local": [round(x, 3) for x in c.location]}
                                for c in o.children if c.get("vfx_kind")] for o in order},
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders -------------------------------------------------------------------------------------------------------------
# decision 12: front_sheet (0, 3) and side_sheet (90, 0) govern the tent, f34_sheet (-45, 20) the read and dressing;
# floor hidden, long lens (m033._long_lens) in every *_sheet shot
SHEET_VIEWS = {"front_sheet": (0, 3), "side_sheet": (90, 0), "f34_sheet": (-45, 20), "r34_sheet": (225, 20),
               "rear_sheet": (180, 3), "top_sheet": (0, 89.9)}
VIEW_NAMES = ("front34", "rear34", "front", "side", "rear", "top")
PARTS_SHOT = (-20, 15)
SPIN = tuple(range(0, 360, 45))
SPIN_EL = 10


def _at(o, p):
    return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)


def _exploded(objs):
    """Linked copies of the parts laid out like the sheet's Exploded Construction: a frame at each side, the two
    panels lifted over the centre, the lantern in the middle, the mat, crate, barrel, stones and pegs below."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown = []
    x0 = objs[0].location.x + 45
    o0 = Matrix.Translation((x0, objs[0].location.y, 0))

    def put(tag, part, m):
        if part not in by:
            return
        c = bpy.data.objects.new(f"{PFX}expl_{tag}", by[part].data)
        coll.objects.link(c)
        c.matrix_world = o0 @ m
        shown.append(c)
    put("frame_l", FRAME_P, Matrix.Translation((-11.0, 0.0, 1.5)))
    put("frame_r", FRAME_P, Matrix.Translation((11.0, 0.0, 1.5)) @ Matrix.Rotation(math.pi, 4, "Z"))
    put("panel_l", PANEL_P, Matrix.Translation((-3.6, 0.0, 4.0)) @ Matrix.Rotation(math.pi, 4, "Z"))
    put("panel_r", PANEL_P, Matrix.Translation((3.6, 0.0, 4.0)))
    put("lantern", LANTERN_P, Matrix.Translation((0.0, -1.0, 9.5)))
    put("mat", MAT_P, Matrix.Translation((0.0, -4.0, 0.0)))
    put("crate", CRATE_P, Matrix.Translation((-6.0, -7.5, 0.0)))
    put("barrel", BARREL_P, Matrix.Translation((5.5, -7.0, 0.0)))
    put("stone1", STONE_P, Matrix.Translation((-0.8, -10.0, 0.0)))
    put("stone2", STONE_P, Matrix.Translation((1.4, -10.2, 0.0)) @ Matrix.Diagonal((0.8, 0.8, 0.8, 1)))
    put("peg_l", PEG_P, Matrix.Translation((-9.5, -7.5, 0.0)))
    put("peg_r", PEG_P, Matrix.Translation((9.5, -7.5, 0.0)))
    bpy.context.view_layer.update()
    return shown


def _marker(h, at, name, proxy=False):
    """A 5.5-stud character stand-in (proxy: the spec 2.9 walk box, body 2 x 1 to 4.4, head 1.1 wide to 5.5)."""
    a = K.fk().Asset(PFX + name, "probe", seed=1, tint_var=0.0)
    if proxy:
        for hx, hy, z0, z1 in PROXY:
            _box(a, (-hx, -hy, z0), (hx, hy, z1), METAL, 0.8)
        _box(a, (-0.5, -0.4, 0.0), (0.5, 0.4, 0.25), METAL, 0.8)
    else:
        a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=METAL, tint=0.7)
        a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=METAL, tint=0.7)
        a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=METAL, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    c.location = _at(h, at)
    bpy.context.view_layer.update()
    return c


def _remove(objs):
    for o in objs:
        me = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(me, bpy.types.Mesh) and me.users == 0:
            bpy.data.meshes.remove(me)


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    markers = [_marker(h, (2.6, -7.0, 0.0), "char"), _marker(h, (0.6, 0.5, MAT_T), "char2")]
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        for o in objs[1:]:
            extra["part_" + o.name.replace(HERO, "").lower()] = ([o], *PARTS_SHOT)
        if shown:
            extra["exploded"] = (shown, -10, 15)
        extra["scale"] = ([h] + markers, -25, 8)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = m033._long_lens(kit)
        try:
            sheet = M.views(NUM, [h], names=VIEW_NAMES, extra=extra, vfx=True)
            spin = render_spin(h)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet, "spin": spin}
        if close:
            out.update(render_close_ups(objs))
        return out
    finally:
        _remove(shown + markers)
        M.display(NUM, objs, TITLE)


def render_spin(h):
    """The eight-azimuth contact sheet: az 0, 45 ... 315 at e 10, long lens, floor hidden -> M064_spin.png."""
    kit = K.NS["KIT"]
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    old = kit["CELL"]
    kit["CELL"] = (420, 360)
    sc = bpy.context.scene
    try:
        kit["vfx"].clear(sc)
        kit["vfx"].realize(sc, [h])
        paths = [kit["render_group"]([h], f"{d}/spin{az:03d}_sheet.png", az, SPIN_EL) for az in SPIN]
    finally:
        kit["CELL"] = old
        kit["vfx"].clear(sc)
    rows = [kit["hstack"](paths[i:i + 4]) for i in (0, 4)]
    out = f"{d}/M064_spin.png"
    kit["save_px"](kit["vstack"](rows), out)
    return out


def render_cam(objs, path, loc, look, lens=18.0, cell=(560, 420), vfx=True):
    """A render from a fixed camera (loc looking at look), e.g. from inside the doorway."""
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
    sc = bpy.context.scene
    try:
        if vfx:
            kit["vfx"].clear(sc)
            kit["vfx"].realize(sc, objs)
        return kit["render_group"](objs, path, 0, 10)
    finally:
        kit["frame_box"] = fb
        kit["CELL"] = old
        cam.data.lens = lens0
        if vfx:
            kit["vfx"].clear(sc)


def render_close_ups(objs):
    """junction_cu (close-up A: the front crossing, lashing wraps and V), canvas_cu (close-up B: the crossing from
    above, the canvas fold and lantern), crease_cu (the -X panel's sag creases), inside_cu (close-up C: from the
    doorway looking in and up), knot_cu (a corner knot, its tail and peg rope), door_walk (the 5.5 proxy in the
    doorway and on the mat, front and side), thumb (the f34 at about 125 px)."""
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    by = {o.name: o for o in objs}
    h = objs[0]
    out = {}
    rc = m033.render_close
    kit = K.NS["KIT"]
    sc = bpy.context.scene
    kit["vfx"].clear(sc)
    kit["vfx"].realize(sc, [h])
    try:
        out["junction_cu"] = rc([h], f"{d}/junction_cu.png", -30, 8, _at(h, (0.0, -4.0, 9.3)), 1.5)
        out["canvas_cu"] = rc([h], f"{d}/canvas_cu.png", -20, 28, _at(h, (0.0, -3.7, 9.0)), 1.9)
        out["crease_cu"] = rc([h], f"{d}/crease_cu.png", -75, 15, _at(h, (-3.2, 0.0, 4.6)), 5.0)
        out["knot_cu"] = rc([h], f"{d}/knot_cu.png", -40, 18, _at(h, (-5.1, -5.0, 1.2)), 1.5)
        out["knot_outer_cu"] = rc([h], f"{d}/knot_outer_cu.png", 40, 18, _at(h, (5.4, -5.6, 1.2)), 1.5)
    finally:
        kit["vfx"].clear(sc)
    out["inside_cu"] = render_cam([h], f"{d}/inside_cu.png", _at(h, (0.0, -6.2, 1.8)), _at(h, (0.0, 2.0, 5.6)),
                                  lens=16.0)
    # door_walk: the proxy in the doorway (front, side) and on the mat (side)
    px = _marker(h, (0.0, -plane_y(HEM_Z, END_N), 0.0), "proxy", proxy=True)
    px2 = _marker(h, (0.0, 0.5, MAT_T), "proxy2", proxy=True)
    try:
        old = kit["CELL"]
        kit["CELL"] = (420, 360)
        try:
            p1 = kit["render_group"]([h, px], f"{d}/door_walk_front.png", 0, 4)
            p2 = rc([h, px, px2], f"{d}/door_walk_side.png", 90, 4, _at(h, (0.0, -1.5, 4.0)), 6.0)
            p3 = rc([h, px], f"{d}/door_walk_f34.png", -35, 10, _at(h, (0.0, -4.0, 3.8)), 4.5)
        finally:
            kit["CELL"] = old
        path = f"{d}/door_walk.png"
        kit["save_px"](kit["hstack"]([p1, p2, p3]), path)
        out["door_walk"] = path
    finally:
        _remove([px, px2])
    old = kit["CELL"]
    kit["CELL"] = (150, 125)
    try:
        orig, kit["render_group"] = m033._long_lens(kit)
        try:
            out["thumb"] = kit["render_group"]([h], f"{d}/thumb_sheet.png", -45, 20)
        finally:
            kit["render_group"] = orig
    finally:
        kit["CELL"] = old
    return out


def preview(names=("front_sheet", "side_sheet", "f34_sheet", "r34_sheet"), vfx=False, spin=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        r = M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
        if spin:
            r = [r, render_spin(h)]
        return r
    finally:
        kit["render_group"] = orig


def hero_only():
    """Rebuild just the hero (tuning loop)."""
    M.coll(NUM, TITLE)
    palette()
    h, lg = _make(HERO, hero_all, "hero", HERO_BUDGET)
    _sockets(h)
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, _ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"hero": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                        "boundary_edges", "normals")}, "log": lg,
            "geo": json.loads(json.dumps(GEO, default=lambda v: [round(x, 3) for x in v])),
            "offset": [round(x, 3) for x in h[OFF]]}
