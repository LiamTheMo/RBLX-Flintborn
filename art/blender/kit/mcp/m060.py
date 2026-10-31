"""060 Broadleaf Fern (references/060.png): a hip-high undergrowth fern. Six stalks carry eight thick, blunt-lobed
frond blades (two tall dark fronds in a V, two arching lime fronds with a darker fork each, two small lime fronds front
and back), each blade a closed V-folded slab with a raised rachis; a skirt of eight lobed broad leaves droops from the
crown to the ground. An orange-brown faceted root crown (hub, peg, seven splayed roots with cut ends), seven warm-grey
rocks (two taller sage-stained ones behind) and six lime ground sprigs sit at the foot. No glow, no VFX.

    import importlib, kit_models, m060; importlib.reload(kit_models); importlib.reload(m060); m060.build()

Build frame: studs, front -Y, +X right, ground z 0, the root crown's axis on (0, 0). Plan azimuths: 0 = +X,
counter-clockwise, 90 = +Y (back). Every object ends with its origin at its bbox bottom centre; o["m060_offset"] is
that origin in the build frame. Names (spec 8, decision 2): BroadleafFern (hero) and parts BroadleafFernLargeFrond (F1),
...MediumFrond (F3 + F3b on one stalk), ...SmallFrond (F5), ...RootCrown, ...BroadLeaf (skirt leaf N1), ...Rock (R1),
...GroundLeaf (one sprig).

Construction: each frond / skirt leaf = one closed blade shell (a 2D lobed outline triangulated as fans from rachis
stations, mapped onto the arched spine with roll, V-fold and thickness; rim walls all round) + one closed 4-sided tube
shell that is the stalk below the blade and the raised rachis ridge / keel inside it (it pokes 0.03-0.04 above and below
the blade surfaces). Colour is painted by role and position along each frond (lobe bands), rocks by height and
position, the crown by member (never by facing). Stages 5-6: none (the sheet shows no glow, light or effect).
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

NUM, TITLE, SHEET = 60, "Broadleaf Fern", "M060"
OFF = "m060_offset"
PFX = "_m060_"
HERO = "BroadleafFern"
LARGE_P, MEDIUM_P, SMALL_P = "BroadleafFernLargeFrond", "BroadleafFernMediumFrond", "BroadleafFernSmallFrond"
ROOT_P, LEAF_P = "BroadleafFernRootCrown", "BroadleafFernBroadLeaf"
ROCK_P, GROUND_P = "BroadleafFernRock", "BroadleafFernGroundLeaf"

LIGHT, FRESH, MID = "m060_frond_light", "m060_leaf_fresh", "m060_frond_mid"
DARK, DEEP = "m060_frond_dark", "m060_green_deep"
STALK, ROOT, ROOT_LIGHT, ROOT_DEEP = "m060_stalk", "m060_root", "m060_root_light", "m060_root_deep"
ROCK, ROCK_DEEP, SAGE = "m060_rock", "m060_rock_deep", "m060_rock_sage"
LADDER = (DEEP, DARK, MID, FRESH, LIGHT)     # tone value 0..4 along a frond or leaf
GREENS = (LIGHT, FRESH, MID, DARK, DEEP)

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
BURY = 0.05
SINK = 0.02
Z = Vector((0.0, 0.0, 1.0))

# key -> (hex, roughness, low specular). Stage 4 writes the calibrated values here (spec "Stage 4").
PALETTE = {
    LIGHT: ("#9ECA22", 0.8, True),
    FRESH: ("#84BB2B", 0.8, True),
    MID: ("#5E9221", 0.85, True),
    DARK: ("#346D2B", 0.85, True),
    DEEP: ("#244C1C", 0.9, True),
    STALK: ("#735B00", 0.85, False),
    ROOT: ("#7A4D27", 0.9, False),
    ROOT_LIGHT: ("#96693C", 0.85, False),
    ROOT_DEEP: ("#472A10", 0.95, False),
    ROCK: ("#888582", 0.85, False),
    ROCK_DEEP: ("#6E6B68", 0.9, False),
    SAGE: ("#858C74", 0.9, False),
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions), K.sample kinds
TARGETS = {LIGHT: ((0xA8, 0xD7, 0x22), "vivid"), FRESH: ((0x92, 0xCC, 0x28), "vivid"),
           MID: ((0x69, 0xA5, 0x20), "green"), DARK: ((0x33, 0x70, 0x2A), "green"),
           DEEP: ((0x24, 0x4E, 0x1B), "green"), STALK: ((0x90, 0x6F, 0x12), "brown"),
           ROOT: ((0x74, 0x4A, 0x28), "brown"), ROOT_LIGHT: ((0xBF, 0x80, 0x47), "brown"),
           ROOT_DEEP: ((0x5A, 0x38, 0x20), "brown"), ROCK: ((0x92, 0x8E, 0x89), "stone"),
           ROCK_DEEP: ((0x78, 0x74, 0x70), "stone"), SAGE: ((0x96, 0x9E, 0x86), "stone")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m060_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k == "m060_" + tail), None)
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


def _mix(k1, k2, t):
    t = round(max(0.0, min(1.0, t)) * 4) / 4
    return K.mix_key(k1, k2, t)


def _tone(v):
    v = max(0.0, min(4.0, v))
    i = min(3, int(v))
    return _mix(LADDER[i], LADDER[i + 1], v - i)


def _ramp(pts, s):
    if s <= pts[0][0]:
        return pts[0][1]
    for (s0, v0), (s1, v1) in zip(pts, pts[1:]):
        if s <= s1:
            return v0 + (v1 - v0) * (s - s0) / max(1e-9, s1 - s0)
    return pts[-1][1]


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


def _u(az):
    r = math.radians(az)
    return Vector((math.cos(r), math.sin(r), 0.0))


def _close(a, vs, fs, key, tint=1.0):
    bmesh.ops.recalc_face_normals(a.bm, faces=fs)
    a._finish(vs, key, tint=tint)


EXPLODE = {"on": False}


def _shift(vec):
    return Vector(vec) if EXPLODE["on"] else Vector()


# shell registry for the reports: (kind, name, centroid in the build frame)
REG = []
FACE_INFO = {}       # BMFace -> (kind, name, plane normal) for the visibility measure (hero build only)


def _reg(vs, kind, name, faces=None, pn=None):
    c = sum((v.co for v in vs), Vector()) / max(1, len(vs))
    REG.append((kind, name, tuple(c)))
    for f in faces or _faces(vs):
        FACE_INFO[f] = (kind, name, (pn or {}).get(f))


# ---- curves ------------------------------------------------------------------------------------------------------------
def _bez(P, t):
    a, b, c, d = P
    s = 1.0 - t
    return a * (s * s * s) + b * (3 * s * s * t) + c * (3 * s * t * t) + d * (t * t * t)


class _Curve:
    """A polyline sampled densely from cubic Beziers, addressed by arc-length fraction."""

    def __init__(self, ctrls, n=48):
        pts = []
        for P in ctrls:
            seg = [_bez(P, i / n) for i in range(n + 1)]
            pts += seg if not pts else seg[1:]
        self.pts = pts
        self.cum = [0.0]
        for p, q in zip(pts, pts[1:]):
            self.cum.append(self.cum[-1] + (q - p).length)
        self.L = self.cum[-1]

    def at(self, f):
        s = max(0.0, min(1.0, f)) * self.L
        cum = self.cum
        lo, hi = 0, len(cum) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if cum[m] <= s:
                lo = m
            else:
                hi = m
        seg = max(1e-9, cum[hi] - cum[lo])
        t = (s - cum[lo]) / seg
        p = self.pts[lo].lerp(self.pts[hi], t)
        d = (self.pts[hi] - self.pts[lo]).normalized()
        return p, d


def _frame(T, W0, roll):
    W = (W0 - T * T.dot(W0))
    W = W.normalized() if W.length > 1e-6 else T.orthogonal().normalized()
    N = T.cross(W).normalized()
    if roll:
        c, s = math.cos(roll), math.sin(roll)
        W, N = W * c + N * s, N * c - W * s
    return W, N


# ---- the lobed blade (fronds and skirt leaves share it) ---------------------------------------------------------------
def _side_outline(L, Wh, env, n, depth, u0, u1, sweep, ow=None, sh_u=0.35, sh_v=0.84):
    """One side's outline from the base corner to the last lobe's end: (u, v) with v >= 0 in studs, plus the lobe hubs
    (u). Each lobe is a rounded scallop: two shoulder verts (sh_u x the lobe pitch either side of its centre, at sh_v of
    the envelope) and a crown vert on the envelope between them, leaning toward the tip by `sweep`; between lobes one
    notch vert reaches in to depth x the local half-width (a rounded V between the scallops). Fix round 1: replaces the
    two-vert U-slot + two-corner tongue, which read as a square ratchet; the vert count per lobe is unchanged.
    Order: base, then per lobe: (notch for k > 0), shoulder 1, crown, shoulder 2."""
    a = [u0 + k * (u1 - u0) / n for k in range(n + 1)]
    tn = math.tan(math.radians(sweep))
    out = [(0.0, env(0.0) * Wh)]
    hubs = []
    for k in range(n):
        w = a[k + 1] - a[k]
        c = (a[k] + a[k + 1]) / 2
        if k > 0:
            out.append((a[k], depth * env(a[k]) * Wh))
        e = env(c) * Wh
        s = min(tn * (e * (1 - depth)) / L, 0.22 * w)     # the lean, capped so the fan from the hub stays valid
        u1_ = c - sh_u * w + 0.4 * s
        um = c + s
        u2_ = min(0.97, c + sh_u * w + s)
        v1 = max(env(u1_), 0.6 * env(c)) * Wh * sh_v
        vm = max(env(um), 0.7 * env(c)) * Wh
        v2 = max(env(u2_), 0.5 * env(c)) * Wh * sh_v
        if k < n - 1:   # keep shoulder 2 ahead of the next notch as seen from the hub (the fan stays valid)
            nu, nv = a[k + 1], depth * env(a[k + 1]) * Wh
            if _cross2((0.0, 0.0), ((u2_ - c) * L, v2), ((nu - c) * L, nv)) >= 0:
                u2_ = c + (nu - c) * 0.6
        if k > 0:       # the first lobe rises straight from the base vert (keeps the vert count of the old outline)
            out.append((u1_, v1))
        out.append((um, vm))
        out.append((u2_, v2))
        hubs.append(c)
    return out, hubs


def _cross2(p, q, r):
    return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])


def _oi(k):
    """Outline indices of lobe k: (notch, shoulder 1, crown, shoulder 2). The first lobe has no shoulder 1: its notch
    is the base vert (index 0) and shoulder 1 is None."""
    if k == 0:
        return 0, None, 1, 2
    b = 3 + 4 * (k - 1)
    return b, b + 1, b + 2, b + 3


def _is_outer(j):
    """Outline index j is a scallop vert (shoulder or crown), not the base or a notch."""
    return 1 <= j <= 2 or (j >= 3 and (j - 3) % 4 >= 1)


def _lobe_of(j):
    return 0 if j < 3 else (j - 3) // 4 + 1


def _side_tris(Cu, hub_idx, n_out=None):
    """Triangles of one half between the rachis stations C (keys ("C", i)) and that side's outline (keys ("O", j));
    T is the tip. Fans from each lobe's hub over its scallop (notch, shoulder, crown, shoulder, next notch), bridges
    between hubs to the next notch, and a closing tip triangle."""
    tris = []
    last = len(Cu) - 1
    n = len(hub_idx)
    for i in range(0, hub_idx[0]):
        tris.append((("C", i), ("C", i + 1), ("O", 0)))
    for k in range(n):
        h = hub_idx[k]
        nk, o1, om, o2 = _oi(k)
        seq = [("O", j) for j in (nk, o1, om, o2) if j is not None]
        if k < n - 1:
            nxt = _oi(k + 1)[0]
            seq.append(("O", nxt))
        for j in range(len(seq) - 1):
            tris.append((("C", h), seq[j], seq[j + 1]))
        if k < n - 1:
            for i in range(h, hub_idx[k + 1]):
                tris.append((("C", i), ("C", i + 1), ("O", nxt)))
        else:
            for i in range(h, last):
                tris.append((("C", i), ("C", i + 1), ("O", o2)))
            tris.append((("C", last), ("O", o2), ("T",)))
    return tris


def blade(a, name, spec, curve, W0, sh=Vector(), info=None):
    """One closed lobed blade along `curve` (arc fraction = u). spec: W, env, lobes (right, left), depth, u0, u1,
    sweep, ow, t (base, tip), fold (deg per half), roll (base, tip deg), tone ramp. Returns (verts, faces, bands)."""
    L = curve.L
    Wh = spec["W"] / 2
    env = lambda u: _ramp(spec["env"], u)
    nR, nL = spec["lobes"]
    sc = dict(sh_u=spec.get("sh_u", 0.35), sh_v=spec.get("sh_v", 0.84))
    outR, hubsR = _side_outline(L, Wh, env, nR, spec["depth"], spec["u0"], spec["u1"], spec["sweep"], **sc)
    u1L = spec.get("u1L", spec["u1"])
    outL, hubsL = _side_outline(L, Wh * spec.get("inner", 1.0), env, nL, spec["depth"], spec["u0"], u1L, spec["sweep"],
                                **sc)
    hs = sorted(hubsR + hubsL)
    Cu = [0.0]
    for h in hs:
        if h - Cu[-1] > 0.02:
            Cu.append(h)
    near = lambda h: min(range(1, len(Cu)), key=lambda i: abs(Cu[i] - h))
    hR, hL = [near(h) for h in hubsR], [near(h) for h in hubsL]
    t0, t1 = spec["t"]
    tanF = math.tan(math.radians(spec["fold"]))
    ruff = math.radians(spec.get("ruffle", 0.0))
    mode = spec.get("ruffle_mode", "wave")
    r0, r1 = (math.radians(x) for x in spec["roll"])

    def frame(u):
        p, T = curve.at(u)
        W, N = _frame(T, W0, r0 + (r1 - r0) * u)
        return p, T, W, N

    pts2 = {("C", i): (Cu[i], 0.0) for i in range(len(Cu))}
    pts2[("T",)] = (1.0, 0.0)
    for j, (u, v) in enumerate(outR):
        pts2[("O", j, "R")] = (u, v)
    for j, (u, v) in enumerate(outL):
        pts2[("O", j, "L")] = (u, -v)
    bm = a.bm
    top, bot = {}, {}
    fr = {}
    for key, (u, v) in pts2.items():
        if u not in fr:
            fr[u] = frame(u)
        p, T, W, N = fr[u]
        t = t0 + (t1 - t0) * u
        lift = abs(v) * tanF
        if key[0] == "O" and ruff:                 # lobe ruffle: each scallop lifted or dropped
            j = key[1]
            k = _lobe_of(j)
            if _is_outer(j):
                sgn = (-1) ** k if (mode == "wave" or key[2] == "R") else (-1) ** (k + 1)
                lift += sgn * math.tan(ruff) * abs(v) * 0.7
        base = p + W * v + sh
        top[key] = bm.verts.new(base + N * (t / 2 + lift))
        bot[key] = bm.verts.new(base + N * (-t / 2 + lift))
    faces, fu, pn = [], {}, {}
    for side, tri_keys in (("R", _side_tris(Cu, hR, len(outR))), ("L", _side_tris(Cu, hL, len(outL)))):
        for tri in tri_keys:
            ks = [k if k[0] != "O" else ("O", k[1], side) for k in tri]
            p2 = [pts2[k] for k in ks]
            if _cross2(*p2) < 0:
                ks = [ks[0], ks[2], ks[1]]
                p2 = [p2[0], p2[2], p2[1]]
            uc = sum(q[0] for q in p2) / 3
            f1 = bm.faces.new([top[k] for k in ks])
            f2 = bm.faces.new([bot[k] for k in reversed(ks)])
            for f in (f1, f2):
                fu[f] = uc
            faces += [f1, f2]
    loop = [("C", 0)] + [("O", j, "L") for j in range(len(outL))] + [("T",)] + \
           [("O", j, "R") for j in reversed(range(len(outR)))]
    rim = []
    for i in range(len(loop)):
        p_, q_ = loop[i], loop[(i + 1) % len(loop)]
        f = bm.faces.new((top[p_], bot[p_], bot[q_], top[q_]))
        fu[f] = (pts2[p_][0] + pts2[q_][0]) / 2
        rim.append(f)
    faces += rim
    vs = list(top.values()) + list(bot.values())
    rng = random.Random(sum(map(ord, name)) * 13 + 60)
    _close(a, vs, faces, LIGHT, tint=1.0 + rng.uniform(-0.04, 0.04))
    # plane normal per face (station frame at the face's u) for the visibility measure
    for f in faces:
        pn[f] = frame(fu[f])[3]
    # tones per lobe band (band edges at the right side's notches), one key per band across both halves and the rim
    edges = [0.0] + [spec["u0"] + k * (spec["u1"] - spec["u0"]) / nR for k in range(1, nR)] + [1.01]
    bands = {}
    for f in faces:
        b = max(i for i in range(len(edges) - 1) if fu[f] >= edges[i] - 1e-9)
        bands.setdefault(b, []).append(f)
    for b, fs in bands.items():
        um = (edges[b] + min(1.0, edges[b + 1])) / 2
        _paint(a, fs, _tone(_ramp(spec["tone"], um)))
        _tint(a, fs, 1.0 + rng.uniform(-0.02, 0.02))
    if info is not None:
        p0 = frame(0.0)[0]
        notch_depth = [round(1 - v / max(1e-6, env(u) * Wh), 2) for u, v in outR[3::4]]
        lobe_w = [round((outR[_oi(k)[3]][0] - outR[_oi(k)[1]][0]) * L, 3) for k in range(1, nR)]
        info.update({"L": round(L, 3), "W": spec["W"], "LW": round(L / spec["W"], 2), "lobes": [nR, nL],
                     "notch_depth": notch_depth, "scallop_shoulder_w": lobe_w,
                     "tip_deg": round(math.degrees(2 * math.atan2(outR[-1][1], (1 - outR[-1][0]) * L)), 1),
                     "thick_edge": t0, "base": [round(x, 3) for x in p0 + sh],
                     "low_z_past_03L": round(min(top[k].co.z for k, (u, v) in pts2.items() if u > 0.3), 3)})
    return vs, faces, pn


def tube(a, name, curve_st, curve_bl, W0, roll0, spec_bl, radii, hw, ht, hb, key_ramp, sh=Vector(),
         blade_st=(0.2, 0.42, 0.64, 0.84), end=0.93, stalk_st=(0.0, 0.5, 1.0)):
    """The stalk + rachis: a 4-sided (diamond) tube from the foot along the stalk curve, then inside the blade along
    its spine (the ridge pokes out above and keel below the blade), ending in a point. radii (foot, blade base) for the
    stalk; hw / ht / hb (start, end) the half-width / top / bottom offsets inside the blade. key_ramp(i) -> key for
    segment i (stalk segments first). Returns verts."""
    bm = a.bm
    rings = []
    r0, r1 = (math.radians(x) for x in spec_bl["roll"])
    for k, f in enumerate(stalk_st):
        p, T = curve_st.at(f)
        if f >= 1.0:                    # the joint ring bisects the kink between stalk and blade spine
            T = (T + curve_bl.at(0.02)[1]).normalized()
        W, N = _frame(T, W0, r0)
        r = radii[0] + (radii[1] - radii[0]) * f
        rings.append([bm.verts.new(q + sh) for q in (p + N * r, p + W * r, p - N * r, p - W * r)])
    nb = len(blade_st)
    for k, u in enumerate(blade_st):
        p, T = curve_bl.at(u)
        W, N = _frame(T, W0, r0 + (r1 - r0) * u)
        s = k / max(1, nb - 1)
        h_w = hw[0] + (hw[1] - hw[0]) * s
        h_t = ht[0] + (ht[1] - ht[0]) * s
        h_b = hb[0] + (hb[1] - hb[0]) * s
        tbl = spec_bl["t"][0] + (spec_bl["t"][1] - spec_bl["t"][0]) * u
        lift = 0.0
        rings.append([bm.verts.new(q + sh) for q in (p + N * (tbl / 2 + h_t), p + W * h_w,
                                                     p - N * (tbl / 2 + h_b), p - W * h_w)])
    p, T = curve_bl.at(end)
    apex = bm.verts.new(p + sh)
    segs = [m047._band(bm, rings[k], rings[k + 1]) for k in range(len(rings) - 1)]
    tipf = [bm.faces.new((rings[-1][i], rings[-1][(i + 1) % 4], apex)) for i in range(4)]
    cap = bm.faces.new(list(reversed(rings[0])))
    vs = [v for r in rings for v in r] + [apex]
    allf = [f for s in segs for f in s] + tipf + [cap]
    rng = random.Random(sum(map(ord, name)) * 17 + 61)
    _close(a, vs, allf, STALK, tint=1.0 + rng.uniform(-0.03, 0.03))
    for i, fs in enumerate(segs + [tipf]):
        _paint(a, fs + ([cap] if i == 0 else []), key_ramp(i))
    return vs


# ---- fronds (spec 2.3) -------------------------------------------------------------------------------------------------
HUB_TOP, HUB_R = 0.45, (0.35, 0.30, 0.26, 0.22)
FROND_ENV = [(0.0, 0.35), (0.2, 0.88), (0.35, 1.0), (0.6, 0.86), (0.8, 0.58), (0.92, 0.32), (1.0, 0.0)]
LEAF_ENV = [(0.0, 0.45), (0.15, 0.8), (0.4, 1.0), (0.62, 0.82), (0.8, 0.45), (0.9, 0.2), (1.0, 0.0)]
CURTAIN_ENV = [(0.0, 0.45), (0.15, 0.78), (0.45, 1.0), (0.66, 0.92), (0.82, 0.58), (0.92, 0.26), (1.0, 0.0)]
CURTAIN_LOBES = dict(lobes=(3, 3), depth=0.30, u1=0.80)   # big leaves: fewer, bigger scallops whose notches read
FROND_BASE = dict(env=FROND_ENV, depth=0.36, u0=0.04, u1=0.90, sweep=16.0, t=(0.075, 0.045), fold=12.5, ruffle=6.0, ruffle_mode="wave")
LEAF_BASE = dict(env=LEAF_ENV, depth=0.34, u0=0.06, u1=0.80, sweep=14.0, t=(0.07, 0.04), fold=12.5, ruffle=6.0, ruffle_mode="wave",
                 lobes=(4, 4))
LIME = [(0.0, 2.0), (0.25, 2.5), (0.4, 3.5), (1.0, 4.0)]
# name -> foot (az, r) or fork (parent, f), blade base, tip, apex z, droop at the tip (deg), W, lobes (right, left),
# inner (left-side width factor), roll (base, tip deg), stalk radii, tone ramp
FRONDS = {
    "F1": dict(az=222.0, foot_r=0.12, base=(-0.28, -0.26, 1.15), tip=(-1.05, -0.95, 2.90), apex=2.90, droop=35.0,
               W=1.00, lobes=(5, 4), inner=0.80, u1L=0.84, roll=(33.0, 18.0), radii=(0.068, 0.056),
               tone=[(0.0, 0.0), (0.15, 1.0), (0.7, 1.0), (1.0, 1.5)]),
    "F2": dict(az=45.0, foot_r=0.12, base=(0.25, 0.26, 1.10), tip=(1.32, 1.38, 2.84), apex=2.86, droop=35.0,
               W=0.96, lobes=(5, 4), inner=0.80, u1L=0.84, roll=(-25.0, -10.0), radii=(0.066, 0.055),
               tone=[(0.0, 0.0), (0.15, 1.0), (0.4, 1.25), (0.6, 2.0), (0.85, 2.5), (1.0, 2.75)]),
    "F3": dict(az=165.0, foot_r=0.13, base=(-0.42, 0.12, 0.90), tip=(-1.98, 0.45, 1.80), apex=1.98, droop=40.0,
               W=0.70, lobes=(5, 5), roll=(27.0, 27.0), radii=(0.056, 0.047), tone=LIME),
    "F3b": dict(fork="F3", f=0.6, base=(-0.30, 0.30, 0.95), tip=(-1.25, 1.10, 2.10), apex=2.02, droop=25.0,
                W=0.56, lobes=(5, 5), roll=(-50.0, -50.0), radii=(0.045, 0.040),
                tone=[(0.0, 0.0), (0.15, 1.0), (0.7, 1.25), (1.0, 2.0)]),
    "F4": dict(az=345.0, foot_r=0.13, base=(0.42, -0.12, 0.90), tip=(1.99, -0.50, 1.95), apex=2.06, droop=40.0,
               W=0.70, lobes=(5, 5), roll=(-40.0, -40.0), radii=(0.056, 0.047), tone=LIME),
    "F4b": dict(fork="F4", f=0.6, base=(0.32, 0.10, 0.95), tip=(1.45, 0.55, 1.40), apex=1.60, droop=25.0,
                W=0.56, lobes=(5, 5), roll=(-33.0, -33.0), radii=(0.045, 0.040),
                tone=[(0.0, 0.0), (0.15, 1.0), (0.7, 1.25), (1.0, 2.0)]),
    "F5": dict(az=258.0, foot_r=0.12, base=(-0.10, -0.40, 0.80), tip=(-0.45, -1.60, 1.25), apex=1.35, droop=35.0,
               W=0.58, lobes=(5, 5), roll=(-58.0, -58.0), radii=(0.046, 0.040), tone=LIME),
    "F6": dict(az=95.0, foot_r=0.12, base=(-0.03, 0.40, 0.85), tip=(-0.15, 1.72, 1.70), apex=1.70, droop=35.0,
               W=0.58, lobes=(5, 5), roll=(-50.0, -50.0), radii=(0.046, 0.040), tone=LIME),
}
EXPL_FROND = 1.4
FROND_INFO = {}
_CURVES = {}


def _stalk_curve(F, B, t0):
    Q = B - t0 * ((B - F).length * 0.45)
    return _Curve([(F, F + (Q - F) * (2 / 3), B + (Q - B) * (2 / 3), B)])


def _blade_curve(B, T, t0, t1, apex):
    D = (T - B).length
    best = None
    for i in range(25):
        k1 = 0.15 + 1.15 * i / 24
        for j in range(13):
            k2 = 0.15 + 0.6 * j / 12
            P = (B, B + t0 * (k1 * D), T - t1 * (k2 * D), T)
            mz = max(_bez(P, s / 32).z for s in range(33))
            err = (mz - apex) ** 2 + 0.002 * (k1 - 0.6) ** 2 + 0.002 * (k2 - 0.4) ** 2
            if best is None or err < best[0]:
                best = (err, P)
    return _Curve([best[1]])


def _frond_geo(name):
    """Foot, stalk curve, blade curve, W0 (the natural width axis) of a frond."""
    if name in _CURVES:
        return _CURVES[name]
    s = FRONDS[name]
    B, T = Vector(s["base"]), Vector(s["tip"])
    if "fork" in s:
        pF, pst, _, _ = _frond_geo(s["fork"])
        F = pst.at(s["f"])[0]
    else:
        F = _u(s["az"]) * s["foot_r"] + Vector((0, 0, HUB_TOP - 0.06))
    h = Vector((T.x - F.x, T.y - F.y, 0.0)).normalized()
    t0 = ((B - F).normalized() + h * 0.15).normalized()
    dr = math.radians(s["droop"])
    t1 = (h * math.cos(dr) - Z * math.sin(dr)).normalized()
    st = _stalk_curve(F, B, t0)
    bl = _blade_curve(B, T, t0, t1, s["apex"])
    W0 = Vector((-h.y, h.x, 0.0))
    _CURVES[name] = (F, st, bl, W0)
    return _CURVES[name]


def frond(a, name, guard=None, tone=None):
    s = dict(FRONDS[name])
    if tone is not None:            # parts only: the sheet's part cell colour (e.g. the all-mid medium pair)
        s["tone"] = tone
    F, st, bl, W0 = _frond_geo(name)
    spec = dict(FROND_BASE)
    spec.update({k: s[k] for k in ("W", "lobes", "roll", "tone") if k in s})
    for k in ("inner", "u1L"):
        if k in s:
            spec[k] = s[k]
    par = s.get("fork", name)
    sh = _shift((FRONDS[par]["base"] and (Vector(FRONDS[par]["base"]) - _frond_geo(par)[0]).normalized()) * EXPL_FROND)
    info = {"foot": [round(x, 3) for x in F]}
    vs, fs, pn = blade(a, name, spec, bl, W0, sh, info)
    _reg(vs, "blade", name, fs, pn)
    ramp = s["tone"]
    t_base = _ramp(ramp, 0.1)

    def key_ramp(i):
        if i == 0:
            return _mix(ROOT, STALK, 0.5) if "fork" not in s else STALK
        if i == 1:
            return STALK
        if i == 2:
            return _mix(STALK, _tone(t_base), 0.5)
        u = (0.35, 0.72, 0.93)[min(2, i - 2)]
        return _tone(_ramp(ramp, u) - 1.0)
    tv = tube(a, name + "_tube", st, bl, W0, 0.0, spec, s["radii"], hw=(0.045, 0.022),
              ht=(0.036, 0.018), hb=(0.03, 0.012), key_ramp=key_ramp, sh=sh, blade_st=(0.35, 0.72))
    _reg(tv, "tube", name)
    info.update(apex=round(max(v.co.z for v in vs), 3), tip=[round(x, 3) for x in bl.at(1.0)[0] + sh],
                stalk_len=round(st.L, 3), lean_deg=round(math.degrees((Vector(s["tip"]) - F).angle(Z)), 1))
    FROND_INFO[name] = info
    return vs, tv


# ---- skirt leaves (spec 2.4) -------------------------------------------------------------------------------------------
PET_R, PET_Z, PET_LEN, PET_RISE = 0.18, HUB_TOP - 0.07, 0.58, 62.0
LEAVES = {
    "N1": dict(az=288.0, tip=(0.52, -1.52, 0.04), W=1.15, roll=-8.0, lean=30.0, droop=68.0, hk=(0.36, 0.28),
               tone=[(0.0, 2.0), (0.25, 3.0), (0.5, 3.75), (1.0, 4.0)]),
    "N2": dict(az=245.0, tip=(-0.72, -1.42, 0.28), W=1.02, roll=-10.0, tone=[(0.0, 2.0), (0.25, 3.0), (0.5, 3.75), (1.0, 4.0)]),
    "N3": dict(az=332.0, tip=(1.84, -0.80, 0.06), W=1.32, roll=-56.0, lean=15.0, droop=76.0, hk=(0.45, 0.32),
               tone=[(0.0, 2.0), (0.3, 3.0), (0.6, 3.75), (1.0, 4.0)]),
    "N4": dict(az=176.0, tip=(-2.015, 0.141, 0.04), W=1.40, curtain=True, pet=0.72, rise=68.0, roll=10.0, lean=12.0, droop=70.0, hk=(0.48, 0.34),
               tone=[(0.0, 0.0), (0.2, 1.0), (1.0, 1.0)]),
    "N5": dict(az=214.0, tip=(-1.48, -1.04, 0.05), W=1.16, roll=13.0, lean=15.0, droop=76.0, hk=(0.45, 0.32),
               tone=[(0.0, 1.0), (0.3, 2.0), (1.0, 2.25)]),
    "N6": dict(az=128.0, tip=(-1.18, 1.52, 0.04), W=1.40, curtain=True, roll=10.0, pet=0.64, rise=66.0, lean=10.0, droop=70.0, hk=(0.48, 0.34),
               tone=[(0.0, 0.0), (0.2, 1.0), (1.0, 1.25)]),
    "N7": dict(az=95.0, tip=(-0.15, 1.71, 0.05), W=1.40, curtain=True, roll=-25.0, pet=0.62, lean=12.0, droop=70.0, hk=(0.48, 0.34),
               tone=[(0.0, 2.0), (0.3, 3.25), (0.6, 4.0), (1.0, 4.0)]),
    "N8": dict(az=52.0, tip=(1.18, 1.51, 0.04), W=1.40, curtain=True, roll=-7.0, pet=0.70, rise=68.0, lean=4.0, droop=70.0, hk=(0.48, 0.34),
               tone=[(0.0, 1.0), (0.3, 2.5), (1.0, 3.75)]),
    "N9": dict(az=18.0, tip=(1.921, 0.624, 0.04), W=1.40, curtain=True, pet=0.72, rise=68.0, roll=33.0, lean=12.0, droop=70.0, hk=(0.48, 0.34),
               tone=[(0.0, 1.0), (0.3, 2.0), (1.0, 3.25)]),
}
EXPL_LEAF = 0.7
LEAF_INFO = {}


def _leaf_geo(name, lift=0.0):
    s = LEAVES[name]
    F = _u(s["az"]) * PET_R + Vector((0, 0, PET_Z))
    T = Vector(s["tip"]) + Vector((0, 0, lift))
    h = Vector((T.x - F.x, T.y - F.y, 0.0)).normalized()
    rise = math.radians(s.get("rise", PET_RISE))
    d0 = (h * math.cos(rise) + Z * math.sin(rise)).normalized()
    B = F + d0 * s.get("pet", PET_LEN)
    st = _stalk_curve(F, B, d0)
    dr = math.radians(s.get("droop", 62.0))
    t1 = (h * math.cos(dr) - Z * math.sin(dr)).normalized()
    D = (T - B).length
    b0 = math.radians(s.get("lean", 38.0))             # the blade leaves the petiole already heading out and down
    tb = (h * math.cos(b0) - Z * math.sin(b0)).normalized()
    k0, k1 = s.get("hk", (0.33, 0.24))                 # Bezier handles: longer = a fuller arch (fix round 1 mound)
    bl = _Curve([(B, B + tb * (k0 * D), T - t1 * (k1 * D), T)])
    W0 = Vector((-h.y, h.x, 0.0))
    return F, st, bl, W0, d0


def skirt_leaf(a, name, guard=None):
    s = LEAVES[name]
    info = {"lift": 0.0}
    for attempt in range(8):
        lift = 0.06 * attempt
        F, st, bl, W0, d0 = _leaf_geo(name, lift)
        sh = _shift(d0 * EXPL_LEAF)
        spec = dict(LEAF_BASE)
        spec.update(W=s["W"], roll=(s["roll"], s["roll"]), tone=s["tone"])
        if s.get("curtain"):            # fix round 1: back / side leaves stay broad down to the ground (no gaps)
            spec["env"] = CURTAIN_ENV
            spec.update(CURTAIN_LOBES)
        inf = {"foot": [round(x, 3) for x in F]}
        mark = len(REG)
        vs, fs, pn = blade(a, name, spec, bl, W0, sh, inf)
        zmin = min(v.co.z for v in vs)
        d = guard.depth(vs) if guard is not None and not EXPLODE["on"] else 0.0
        if (d <= 0.03 and zmin >= -0.012) or attempt == 7:
            break
        bmesh.ops.delete(a.bm, geom=vs, context="VERTS")
    _reg(vs, "blade", name, fs, pn)
    ramp = s["tone"]

    def key_ramp(i):
        if i == 0:
            return _mix(ROOT, STALK, 0.5)
        if i == 1:
            return _mix(STALK, _tone(_ramp(ramp, 0.0)), 0.5)
        u = (0.45, 0.84)[min(1, i - 2)]
        return _tone(_ramp(ramp, u) - 1.0)
    tv = tube(a, name + "_pet", st, bl, W0, 0.0, spec, (0.045, 0.040), hw=(0.04, 0.02), ht=(0.03, 0.016),
              hb=(0.026, 0.012), key_ramp=key_ramp, sh=sh, blade_st=(0.45,), end=0.84, stalk_st=(0.0, 1.0))
    _reg(tv, "tube", name)
    inf.update(lift=round(lift, 3), rock_depth=round(d, 3), zmin=round(zmin, 3),
               tip=[round(x, 3) for x in bl.at(1.0)[0] + sh])
    LEAF_INFO[name] = inf
    return vs, tv


# ---- root crown (spec 2.2) ---------------------------------------------------------------------------------------------
# root 4 (248 deg) shortened from 0.80: its end ran 0.079 into R1 (verifier round 2, minor 3)
ROOTS = ((0.0, 0.74), (80.0, 1.30), (170.0, 0.85), (208.0, 0.72), (248.0, 0.68), (288.0, 0.76), (326.0, 0.80))
EXPL_ROOT = (0.0, 0.0, 0.0)


def hub(a, sh=Vector(), lift=False):
    bm = a.bm
    rng = random.Random(60101)
    zs = (-SINK, 0.18, HUB_TOP - 0.05, HUB_TOP)
    rad = (HUB_R[0], HUB_R[1], HUB_R[2], HUB_R[3] - 0.03)
    rings = []
    for z, r in zip(zs, rad):
        off = Vector((rng.uniform(-0.02, 0.02), rng.uniform(-0.02, 0.02), 0.0)) if z > 0 else Vector()
        ring = []
        for k in range(8):
            ang = math.pi / 8 + k * math.pi / 4
            rr = r * (1 + rng.uniform(-0.05, 0.05))
            ring.append(bm.verts.new(Vector((math.cos(ang) * rr, math.sin(ang) * rr, z)) + off + sh))
        rings.append(ring)
    bands = [m047._band(bm, rings[k], rings[k + 1]) for k in range(3)]
    bot = bm.faces.new(list(reversed(rings[0])))
    top = bm.faces.new(rings[3])
    vs = [v for r in rings for v in r]
    _close(a, vs, [f for b in bands for f in b] + [bot, top], ROOT)
    _paint(a, bands[0] + [bot], _mix(ROOT, ROOT_DEEP, 0.5) if not lift else _mix(ROOT, ROOT_LIGHT, 0.5))
    if lift:        # hero: the lower bands lighter (they sit in the skirt's shade; by height band, not facing)
        _paint(a, bands[1], ROOT_LIGHT)
    _paint(a, bands[2] + [top], ROOT_LIGHT)
    _tint(a, _faces(vs), 1.0 + rng.uniform(-0.03, 0.03))
    return vs


def peg(a, sh=Vector()):
    bm = a.bm
    r = 0.07
    rings = [[bm.verts.new(Vector((math.cos(k * math.pi / 3) * r, math.sin(k * math.pi / 3) * r, z)) + sh)
              for k in range(6)] for z in (HUB_TOP - 0.06, HUB_TOP + 0.13)]
    side = m047._band(bm, rings[0], rings[1])
    bot = bm.faces.new(list(reversed(rings[0])))
    top = bm.faces.new(rings[1])
    vs = rings[0] + rings[1]
    _close(a, vs, side + [bot, top], ROOT)
    _paint(a, [top], ROOT_LIGHT)
    return vs


def root_arm(a, k, sh=Vector(), lift=False):
    az, R = ROOTS[k]
    rng = random.Random(60200 + k)
    u = _u(az + rng.uniform(-5, 5))
    p0 = u * 0.10 + Vector((0, 0, 0.24 + rng.uniform(-0.03, 0.03)))
    p1 = u * (0.60 * R) + Vector((0, 0, 0.17))
    r_in, r_mid, r_end = 0.10, 0.085, 0.07
    p2 = u * R + Vector((0, 0, r_end * math.cos(math.radians(36)) - SINK + 0.005))
    bm = a.bm
    rings = []
    for p, r, d in ((p0, r_in, (p1 - p0)), (p1, r_mid, (p2 - p0)), (p2, r_end, (p2 - p1))):
        t = d.normalized()
        side = t.cross(Z).normalized()
        up = side.cross(t).normalized()
        rings.append([bm.verts.new(p + (up * math.cos(math.radians(90 + 72 * i)) +
                                        side * math.sin(math.radians(90 + 72 * i))) * r + sh) for i in range(5)])
    # the cut end sits on the ground: drop the end ring so its lowest vertex is at -SINK + 0.005
    lo = min(v.co.z for v in rings[2]) - sh.z
    for v in rings[2]:
        v.co.z -= lo + SINK - 0.005
    segs = [m047._band(bm, rings[i], rings[i + 1]) for i in range(2)]
    inner = bm.faces.new(list(reversed(rings[0])))
    end = bm.faces.new(rings[2])
    vs = [v for r in rings for v in r]
    _close(a, vs, segs[0] + segs[1] + [inner, end], ROOT)
    if lift:        # hero (fix round 1): the arms one step lighter by member, so the shaded front roots read the
        _paint(a, segs[0], ROOT_LIGHT)                          # sheet's #684324 instead of near black
        _paint(a, segs[1], _mix(ROOT, ROOT_LIGHT, 0.75))
    else:
        _paint(a, segs[1], _mix(ROOT, ROOT_DEEP, 0.25))
    _paint(a, [end], ROOT_LIGHT)
    _tint(a, _faces(vs), 1.0 + rng.uniform(-0.03, 0.03))
    return vs


def root_crown(a, guard=None, lift=False):
    out = {}
    vs = hub(a, lift=lift)
    _reg(vs, "root", "hub")
    out["hub"] = vs
    if guard is not None:
        guard.add_vs(vs, "root_hub")
    vs = peg(a)
    _reg(vs, "root", "peg")
    for k in range(len(ROOTS)):
        vs = root_arm(a, k, lift=lift)
        _reg(vs, "root", f"root{k}")
        out[f"root{k}"] = vs
        if guard is not None:
            guard.add_vs(vs, f"root_{k}")
    return out


# ---- rocks (spec 2.5) --------------------------------------------------------------------------------------------------
LOW_RINGS = ((0.0, 0.92, 5), (0.38, 1.0, 5), (0.78, 0.72, 4), (1.0, 0.38, 3))
TALL_RINGS = ((0.0, 0.92, 5), (0.32, 1.0, 6), (0.68, 0.70, 4), (1.0, 0.14, 2))
ROCKS = {
    "R1": dict(c=(-0.52, -0.90), size=(0.74, 0.62, 0.48), yaw=20.0, rings=LOW_RINGS, seed=60501, sage="top_back"),
    "R2": dict(c=(0.30, -1.08), size=(0.54, 0.45, 0.37), yaw=-30.0, rings=LOW_RINGS, seed=60502),
    "R3": dict(c=(1.10, -0.70), size=(0.50, 0.44, 0.42), yaw=55.0, rings=LOW_RINGS, seed=60503),
    "R4": dict(c=(-1.25, -0.48), size=(0.40, 0.36, 0.31), yaw=10.0, rings=LOW_RINGS, seed=60504),
    "R5": dict(c=(-0.58, 0.69), size=(0.70, 0.60, 0.80), yaw=-15.0, rings=TALL_RINGS, seed=60505, sage="upper"),
    "R6": dict(c=(0.58, 0.69), size=(0.80, 0.65, 1.00), yaw=35.0, rings=TALL_RINGS, seed=60506, sage="upper_west"),
    "R7": dict(c=(0.45, 1.46), size=(0.60, 0.50, 0.38), yaw=40.0, rings=LOW_RINGS, seed=60507, sage="top_back"),
}


def rock(a, name, guard=None, at_origin=False):
    s = ROCKS[name]
    rng = random.Random(s["seed"])
    W, D, H = s["size"]
    pts = m033._ring_pts(rng, s["rings"], W / 2, D / 2, H, 0.08, lean=(rng.uniform(-0.1, 0.1), rng.uniform(-0.1, 0.1)))
    for p in pts:
        p.z += 0.08 * p.x * (p.z / H)
    m = Matrix.Rotation(math.radians(s["yaw"]), 3, "Z")
    c = Vector((0, 0, 0)) if at_origin else Vector((s["c"][0], s["c"][1], 0.0))
    pts = [m @ p + c + Vector((0, 0, -SINK)) for p in pts]
    vs = m033._hull(a, pts, ROCK)
    fs = _faces(vs)
    zl, zh = min(v.co.z for v in vs), max(v.co.z for v in vs)
    fld = K.noise_field(scale=2.4, seed=s["seed"])
    for f in fs:
        q = f.calc_center_median()
        hf = (q.z - zl) / max(1e-6, zh - zl)
        v = fld(q)
        # deeper stone in broad noise patches, not by height (a foot band follows the facing on these squat blocks:
        # K.check corr 0.56 with one)
        key = ROCK_DEEP if v < -0.38 else _mix(ROCK, ROCK_DEEP, 0.5) if v < -0.15 else ROCK
        sg = s.get("sage")
        if sg in ("upper", "upper_west"):
            if hf > 0.5 or (sg == "upper_west" and hf > 0.3 and q.x < c.x - 0.05):
                key = SAGE
            elif hf > 0.38:
                key = _mix(ROCK, SAGE, 0.5)
        elif sg == "top_back" and hf > 0.72 and (q - c).dot(Vector((0.3, 1.0, 0)).normalized()) > 0.02:
            key = _mix(ROCK, SAGE, 0.5)
        _paint(a, [f], key)
        k = 1.0 + rng.uniform(-1, 1) * 0.04
        _tint(a, [f], k)
    _reg(vs, "rock", name)
    if guard is not None:
        guard.add_vs(vs, "rock_" + name)
    return vs


# ---- ground sprigs (spec 2.5) ------------------------------------------------------------------------------------------
SPRIGS = {"S1": dict(at=(-0.09, -1.44), n=3, yaw=10.0, key=LIGHT), "S2": dict(at=(0.81, -1.15), n=2, yaw=60.0, key=FRESH),
          "S3": dict(at=(-0.98, -1.15), n=2, yaw=-20.0, key=FRESH), "S4": dict(at=(1.46, -0.21), n=2, yaw=100.0, key=LIGHT),
          "S5": dict(at=(-1.53, 0.26), n=2, yaw=40.0, key=LIGHT), "S6": dict(at=(-0.62, 1.80), n=2, yaw=-60.0, key=FRESH)}
SPRIG_INFO = {}


def _gem(a, b, dirv, L, W, T, key, seed):
    """A small thick leaf: a base point on the ground, a 5-vert ring at 0.45 L, a tip point. 10 tris."""
    side = dirv.cross(Z).normalized()
    up = side.cross(dirv).normalized()
    c = b + dirv * (0.45 * L)
    hw = W / 2
    ring = [c - side * hw, c - side * 0.45 * hw + up * T, c + side * 0.45 * hw + up * T, c + side * hw,
            c - up * 0.4 * T]
    bm = a.bm
    rv = [bm.verts.new(p) for p in ring]
    bv = bm.verts.new(b)
    tv = bm.verts.new(b + dirv * L + up * 0.01)
    fs = [bm.faces.new((bv, rv[(i + 1) % 5], rv[i])) for i in range(5)] + \
         [bm.faces.new((rv[i], rv[(i + 1) % 5], tv)) for i in range(5)]
    vs = rv + [bv, tv]
    rng = random.Random(seed)
    _close(a, vs, fs, key, tint=1.0 + rng.uniform(-0.03, 0.03))
    return vs


def _pad(a, b, dirv, L, W, T, key, seed):
    """Fix round 1: a small rounded leaf (the parts row's "three small rounded leaves"): a domed hexagonal pad, its
    base corner on the ground at b, lying along dirv; a top and a bottom centre vert over a 6-vert oval rim. 12 tris."""
    side = dirv.cross(Z).normalized()
    up = side.cross(dirv).normalized()
    c = b + dirv * (0.5 * L)
    rim = []
    for i in range(6):
        t = math.radians(180 + 60 * i)
        q = c + dirv * (0.5 * L * math.cos(t)) + side * (0.5 * W * math.sin(t))
        if i in (1, 2, 4, 5):          # the side corners curl up a little: a cupped leaf, not a flat chip
            q += up * (0.18 * T)
        rim.append(q)
    bm = a.bm
    rv = [bm.verts.new(q) for q in rim]
    tv = bm.verts.new(c + up * T)
    bv = bm.verts.new(c - up * (0.35 * T))
    fs = [bm.faces.new((rv[i], rv[(i + 1) % 6], tv)) for i in range(6)] +          [bm.faces.new((rv[(i + 1) % 6], rv[i], bv)) for i in range(6)]
    vs = rv + [tv, bv]
    rng = random.Random(seed)
    _close(a, vs, fs, key, tint=1.0 + rng.uniform(-0.03, 0.03))
    return vs


def sprig(a, name, guard=None, at_origin=False):
    s = SPRIGS[name]
    allv = []
    moved = 0.0
    for attempt in range(8):
        x, y = (0.0, 0.0) if at_origin else s["at"]
        out = Vector((x, y, 0)).normalized() if (x or y) else Vector((1, 0, 0))
        c = Vector((x, y, -SINK)) + out * (0.05 * attempt)
        allv = []
        for i in range(s["n"]):
            yaw = math.radians(s["yaw"] + i * 360.0 / s["n"] + (i * 17) % 23)
            tilt = math.radians(16.0 + 5 * (i % 2))
            d = Vector((math.cos(yaw) * math.cos(tilt), math.sin(yaw) * math.cos(tilt), math.sin(tilt)))
            L = 0.19 - 0.02 * (i % 2)
            vs = _pad(a, c + Vector((math.cos(yaw), math.sin(yaw), 0)) * 0.02, d, L, 0.15, 0.05,
                      s["key"] if i % 2 == 0 else (FRESH if s["key"] == LIGHT else LIGHT), 60700 + i)
            allv.append(vs)
        d = max(guard.depth(vs) for vs in allv) if guard is not None and not EXPLODE["on"] else 0.0
        if d <= 0.0 or attempt == 7:
            moved = 0.05 * attempt
            break
        for vs in allv:
            bmesh.ops.delete(a.bm, geom=vs, context="VERTS")
    for vs in allv:
        _reg(vs, "sprig", name)
    SPRIG_INFO[name] = {"moved": round(moved, 3)}
    return allv


# ---- assemblies --------------------------------------------------------------------------------------------------------
def _reset():
    REG.clear()
    FACE_INFO.clear()
    _CURVES.clear()


def hero_all(a):
    _reset()
    FROND_INFO.clear()
    LEAF_INFO.clear()
    SPRIG_INFO.clear()
    g = m047._Solids()
    root_crown(a, g, lift=True)
    for k in ROCKS:
        rock(a, k, g)
    blades = {}
    for k in FRONDS:
        blades[k] = frond(a, k)[0]
    for k in LEAVES:
        blades[k] = skirt_leaf(a, k, g)[0]
    for k in SPRIGS:
        sprig(a, k, g)
    if not EXPLODE["on"]:
        _blade_checks(blades, g)
        VIS.clear()
        VIS.update(vis_bm(a.bm))


def _blade_checks(blades, g):
    """Per blade: deepest point inside a rock or the root crown (ray parity), and the share of its verts inside
    another blade (spec 2.3: <= 25 %)."""
    sol = {}
    for k, vs in blades.items():
        s = m047._Solids()
        s.add_vs(vs, k)
        sol[k] = s
    for k, vs in blades.items():
        info = FROND_INFO.get(k) or LEAF_INFO.get(k)
        info["in_solid"] = round(g.depth(vs), 3)
        worst = 0.0
        for j, sj in sol.items():
            if j == k:
                continue
            inside = sum(1 for v in vs if sj.point(v.co)[0] > 0)
            worst = max(worst, inside / len(vs))
        info["max_inside_other"] = round(worst, 2)


def large_part(a):
    _reset()
    frond(a, "F1")


MEDIUM_PART_TONE = [(0.0, 1.25), (0.15, 2.0), (0.7, 2.25), (1.0, 2.6)]   # sheet cell: mid #6FAF22, 23/63/15


def medium_part(a):
    _reset()
    frond(a, "F3", tone=MEDIUM_PART_TONE)
    frond(a, "F3b", tone=MEDIUM_PART_TONE)


def small_part(a):
    _reset()
    frond(a, "F5")


def root_part(a):
    _reset()
    root_crown(a)


def leaf_part(a):
    _reset()
    skirt_leaf(a, "N1")


def rock_part(a):
    _reset()
    rock(a, "R1", at_origin=True)


def ground_part(a):
    _reset()
    sprig(a, "S1", at_origin=True)


NOTES = {
    HERO: "Broadleaf fern: 8 thick blunt-lobed frond blades on 6 stalks (2 tall dark, 2 arching lime + 2 dark forks, "
          "2 small lime) and a skirt of 8 lobed broad leaves on an orange-brown root crown (hub, peg, 7 roots), 7 warm-grey "
          "rocks (2 sage-stained) and 6 lime sprigs. Hip-high walk-through undergrowth (collision none). Sheet 58/132.",
    LARGE_P: "Fern Frond (large): F1, a dark lobed frond (5 + 4 lobes) on its ochre-brown stalk",
    MEDIUM_P: "Fern Frond (medium): F3 + its fork F3b on one stalk, mid green as the sheet's part cell",
    SMALL_P: "Fern Frond (small): F5, a lime lobed frond on its stalk",
    ROOT_P: "Root Cluster (base): faceted 8-sided hub with a peg and 7 splayed roots with cut ends",
    LEAF_P: "Broad Leaf (single): one lobed skirt leaf (4 lobes a side) on its petiole",
    ROCK_P: "Rock (reusable): warm-grey faceted block, deeper foot, a sage stain at the top back",
    GROUND_P: "Ground Leaf (small): three small rounded, cupped lime leaves in a low clump",
}
COLLISION = {HERO: "none", LARGE_P: "none", MEDIUM_P: "none", SMALL_P: "none", ROOT_P: "hull", LEAF_P: "none",
             ROCK_P: "hull", GROUND_P: "none"}


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
    o["m060_reg"] = json.dumps([[k, n] + list(c) for k, n, c in REG])
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


# ---- checks ------------------------------------------------------------------------------------------------------------
def _shells(o):
    """Shells of o with their kinds, matched to the build registry by centroid."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    groups = [[] for _ in range(n)]
    for f in bm.faces:
        groups[ids[f.index]].append(f)
    off = Vector(o.get(OFF, (0, 0, 0)))
    reg = [(r[0], r[1], Vector(r[2:5])) for r in json.loads(o.get("m060_reg", "[]"))]
    kinds, names = [], []
    for fs in groups:
        vs = {v for f in fs for v in f.verts}
        c = sum((v.co for v in vs), Vector()) / len(vs) + off
        best = min(reg, key=lambda r: (r[2] - c).length) if reg else ("?", "?", c)
        kinds.append(best[0])
        names.append(best[1])
    return bm, ids, n, groups, kinds, names


def shells_report(o):
    bm, ids, n, groups, kinds, names = _shells(o)
    out = []
    for k in range(n):
        fs = groups[k]
        es = {e for f in fs for e in f.edges}
        vs = list({v for f in fs for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        hits = sum(1 for a_, b_ in tree.overlap(tree) if a_ < b_ and not set(fs[a_].verts) & set(fs[b_].verts))
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) / 3.0
        out.append({"kind": kinds[k], "name": names[k], "tris": len(fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary),
                    "winding_errors": sum(1 for e in es if e.is_manifold and not e.is_contiguous),
                    "self_hits": hits, "volume": round(vol, 5), "zmin": round(min(v.co.z for v in vs), 3)})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating pieces: per shell, whether it touches another shell (triangles intersect or a vertex within tol of
    another shell's surface) or the ground, and whether it chains by contact to the ground (blade -> its tube -> hub
    -> ground; root -> hub / ground; rock, sprig -> ground)."""
    bm, ids, n, groups, kinds, names = _shells(o)
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
    ground = {k for k in range(n) if zmin[k] - z0 <= tol and kinds[k] in ("root", "rock", "sprig", "tube")}
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
        seen = set(ground) if ground else {min(range(n), key=lambda k: zmin[k])}
        stack = list(seen)
        while stack:
            k = stack.pop()
            for m_ in adj[k]:
                if m_ not in seen:
                    seen.add(m_)
                    stack.append(m_)
        return [names[k] for k in range(n) if k not in seen]
    floating = [k for k in range(n) if gap[k] > tol]
    un = chained(tol)
    res = {"shells": n, "floating": len(floating), "floating_names": [names[k] for k in floating],
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "unchained": len(un), "unchained_names": un[:8], "unchained_chain_tol": len(chained(chain_tol)),
           "sink": round(z0 + (o[OFF][2] if OFF in o else 0.0), 3),
           "kinds": {k: kinds.count(k) for k in sorted(set(kinds))}}
    bm.free()
    return res


def bury_report(o):
    """Nothing buried: every blade and sprig against every rock and the root crown, every tube against the rocks (tube
    feet sit in the hub by design), every rock against the crown and the other rocks. depth = distance from the deepest
    vert or face centre inside to that shell's surface."""
    bm, ids, n, groups, kinds, names = _shells(o)
    rocks, root = m047._Solids(), m047._Solids()
    for k in range(n):
        if kinds[k] in ("rock", "root"):
            vs = list({v for f in groups[k] for v in f.verts})
            vi = {v: i for i, v in enumerate(vs)}
            (root if kinds[k] == "root" else rocks).add([v.co for v in vs], [[vi[v] for v in f.verts] for f in groups[k]],
                                                        f"{names[k]}#{k}")
    res, rk = [], []
    for k in range(n):
        fs = groups[k]
        if kinds[k] == "root":
            continue
        pts = list({v.co.copy().freeze() for f in fs for v in f.verts}) + [f.calc_center_median() for f in fs]
        if kinds[k] == "rock":
            d, w = max((root.point(Vector(p)) for p in pts), key=lambda r: r[0])
            d2, w2 = max((rocks.point(Vector(p), skip=(f"{names[k]}#{k}",)) for p in pts), key=lambda r: r[0])
            if max(d, d2) > 0:
                rk.append((round(max(d, d2), 3), names[k], w if d >= d2 else w2))
            continue
        d, w = max((rocks.point(Vector(p)) for p in pts), key=lambda r: r[0])
        if kinds[k] != "tube":
            d2, w2 = max((root.point(Vector(p)) for p in pts), key=lambda r: r[0])
            if d2 > d:
                d, w = d2, w2
        if d > 0:
            res.append((round(d, 3), kinds[k], names[k], w))
    bm.free()
    res.sort(key=lambda r: -r[0])
    rk.sort(key=lambda r: -r[0])
    return {"dressing_shells": sum(1 for k in kinds if k in ("blade", "sprig", "tube")),
            "over_0.05": sum(1 for r in res if r[0] > BURY), "max": res[0][0] if res else 0.0, "worst": res[:6],
            "rocks_over_0.05": sum(1 for r in rk if r[0] > BURY), "rocks": rk[:6]}


def tube_seats(o):
    """Each tube's foot depth inside the hub (or its parent tube for forks) and each blade's tube running through it."""
    bm, ids, n, groups, kinds, names = _shells(o)
    hubs = m047._Solids()
    tubes = {}
    hc = Vector()
    for k in range(n):
        vs = list({v for f in groups[k] for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        if names[k] == "hub":
            hubs.add([v.co for v in vs], [[vi[v] for v in f.verts] for f in groups[k]], "hub")
            hc = sum((v.co for v in vs), Vector()) / len(vs)
        if kinds[k] == "tube":
            tubes[names[k]] = (vs, groups[k])
    out = {}
    for nm, (vs, fs) in tubes.items():
        foot = [v.co for v in vs]
        foot.sort(key=lambda c: (c - hc).length)
        c = sum(foot[:4], Vector()) / 4          # the foot ring (the four verts nearest the hub centre)
        d = hubs.point(c)[0]
        out[nm] = round(d, 3)
    bm.free()
    return out


# ---- eight-azimuth visibility (ray grid) -------------------------------------------------------------------------------
VIS = {}
VIS_VIEWS = {f"az{az:03d}": (az, 5) for az in range(0, 360, 45)}
VIS_VIEWS.update({f"az{az:03d}_e20": (az, 20) for az in range(0, 360, 45)})


def _cam(az, el):
    a_, e = math.radians(az), math.radians(el)
    return Vector((math.sin(a_) * math.cos(e), -math.cos(a_) * math.cos(e), math.sin(e)))


def vis_bm(bm, step=0.025):
    """Per view (azimuth, elevation; az 0 = the front camera at -Y): share of visible foliage (blade) hits seen within
    12 / 20 deg of edge-on by facet normal, within 20 deg by the blade's plane normal (rim walls included), and the
    share of tube / root hits among foliage + tube + root (the bare core)."""
    bm.faces.ensure_lookup_table()
    bm.faces.index_update()
    tree = BVHTree.FromBMesh(bm)
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    ctr = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2))
    R = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)) * 0.62
    faces = bm.faces
    out = {}
    for vn, (az, el) in VIS_VIEWS.items():
        d = _cam(az, el)
        u = Z.cross(d).normalized()
        w = d.cross(u).normalized()
        cnt = {}
        e12 = e20 = p20 = 0
        per = {}
        n = int(R / step)
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                org = ctr + u * (i * step) + w * (j * step) + d * 20
                loc, nr, idx, dist = tree.ray_cast(org, -d, 60)
                if loc is None:
                    continue
                fi = FACE_INFO.get(faces[idx])
                kind = fi[0] if fi else "?"
                cnt[kind] = cnt.get(kind, 0) + 1
                if kind == "rock":
                    cnt["#" + fi[1]] = cnt.get("#" + fi[1], 0) + 1
                if kind == "blade":
                    c = abs(nr.dot(d))
                    pnv = fi[2]
                    bad20 = c < 0.342
                    e12 += c < 0.208
                    e20 += bad20
                    pe = pnv is not None and abs(pnv.dot(d)) < 0.342
                    p20 += pe
                    pr = per.setdefault(fi[1], [0, 0])
                    pr[0] += 1
                    pr[1] += bad20
        fol = cnt.get("blade", 0)
        core = cnt.get("tube", 0) + cnt.get("root", 0)
        worst = sorted(((round(100 * b / t, 0), nm, t) for nm, (t, b) in per.items() if t > 150), reverse=True)[:3]
        out[vn] = {"foliage_px": fol, "edge12": round(100 * e12 / max(1, fol), 1),
                   "edge20": round(100 * e20 / max(1, fol), 1), "plane20": round(100 * p20 / max(1, fol), 1),
                   "core": round(100 * core / max(1, fol + core), 1), "worst_blades_edge20": worst,
                   "rock": round(100 * cnt.get("rock", 0) / max(1, sum(v for k, v in cnt.items() if k[0] != "#")), 1),
                   "rock_by": {k[1:]: round(100 * v / max(1, sum(v for k, v in cnt.items() if k[0] != "#")), 1)
                               for k, v in sorted(cnt.items()) if k[0] == "#"}}
    return out


# ---- build -------------------------------------------------------------------------------------------------------------
PARTS = ((LARGE_P, large_part), (MEDIUM_P, medium_part), (SMALL_P, small_part), (ROOT_P, root_part),
         (LEAF_P, leaf_part), (ROCK_P, rock_part), (GROUND_P, ground_part))
TARGET_SIZE = ((3.85, 0.2), (3.45, 0.25), (3.0, 0.1))      # hero W (X), D (Y), H (Z) +- tolerance (decision 1)
HERO_BUDGET = 3800


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m060_")]
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
            objs[name], log[name] = _make(name, fn)
    h, log["hero"] = _make(HERO, hero_all, "hero", HERO_BUDGET)
    fronds = {k: dict(v) for k, v in FROND_INFO.items()}
    leaves = {k: dict(v) for k, v in LEAF_INFO.items()}
    vis = {k: dict(v) for k, v in VIS.items()}
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
                    problems.append(f"{o.name} shell {i} ({s['kind']} {s['name']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['kind']} {s['name']}): not closed outward ({s['volume']})")
    contact = {o.name: contact_report(o) for o in order}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} shells float ({c['floating_names']}), {c['unchained']} unchained "
                            f"({c['unchained_names']})")
        if c["sink"] < -0.031:
            problems.append(f"{n_}: sinks {c['sink']} below the ground (decision 10: at most 0.03)")
    bury = bury_report(h)
    if bury["over_0.05"]:
        problems.append(f"{HERO}: {bury['over_0.05']} shells more than {BURY} inside a rock / the crown ({bury['worst'][:3]})")
    if bury["rocks_over_0.05"]:
        problems.append(f"{HERO}: {bury['rocks_over_0.05']} rocks more than {BURY} into the crown or a rock")
    seats = tube_seats(h)
    for k, d in seats.items():
        if not (0.02 <= d <= 0.12) and k not in ("F3b", "F4b"):
            problems.append(f"{HERO}: tube {k} foot depth {d} in the hub (0.04-0.08 wanted)")
    for k, b in list(fronds.items()) + list(leaves.items()):
        if b.get("max_inside_other", 0) > 0.25:
            problems.append(f"{HERO}: blade {k} {b['max_inside_other']} of its verts inside another blade")
        if b.get("in_solid", 0) > BURY:
            problems.append(f"{HERO}: blade {k} {b['in_solid']} inside a rock / the crown")
    for k, lf in leaves.items():
        if lf.get("zmin", 0) < -0.012:
            problems.append(f"{HERO}: leaf {k} dips to z {lf['zmin']}")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 11: none)")
    for n_, t in thin.items():
        if t["under"]:
            problems.append(f"{n_}: {t['under']} faces with a corner under 2 deg (min {t['min_deg']})")
    for vn, v in vis.items():
        if not vn.endswith("_e20") and v["edge20"] > 10.0:
            problems.append(f"{HERO}: view {vn} edge-on (20 deg) {v['edge20']} % of foliage (target <= 10)")
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
           "hero_shells": kinds, "contact": contact, "bury": bury, "tube_seats": seats, "winding": winding,
           "fronds": fronds, "leaves": leaves, "sprigs": dict(SPRIG_INFO), "vis": vis, "thin": thin, "log": log,
           "problems": problems, "uv": uv, "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders -----------------------------------------------------------------------------------------------------------
SHEET_VIEWS = {"f34_sheet": (0, 20), "r34_sheet": (180, 20), "front_sheet": (0, 5), "side_sheet": (90, 5),
               "rear_sheet": (180, 5), "top_sheet": (0, 60)}
VIEW_NAMES = ("front", "side", "rear", "top", "underside")
PARTS_SHOT = (0, 15)
PART_SHOTS = {ROOT_P: (-25, 30), LEAF_P: (-30, 35), GROUND_P: (-20, 30)}


def _exploded(objs):
    EXPLODE["on"] = True
    try:
        o = _new(PFX + "exploded", hero_all, "part", 9999, temp=True)
    finally:
        EXPLODE["on"] = False
    o.location = (objs[0].location.x + 30, objs[0].location.y, 0)
    bpy.context.view_layer.update()
    return [o]


def _scale_marker(h, at, name="char"):
    a = K.fk().Asset(PFX + name, "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=ROCK_DEEP, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=ROCK_DEEP, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=ROCK_DEEP, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
    c.location = off @ Vector(at)
    bpy.context.view_layer.update()
    return c


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    markers = [_scale_marker(h, (3.2, 0.0, 0.0))]
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        extra["front34"] = ([h], -25, 15)
        extra["rear34"] = ([h], 155, 15)
        for o in objs[1:]:
            extra["part_" + o.name.replace(HERO, "").lower()] = ([o], *PART_SHOTS.get(o.name, PARTS_SHOT))
        if shown:
            extra["exploded"] = (shown, 0, 15)
        extra["scale"] = ([h] + markers, -20, 6)
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
        for o in shown + markers:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def render_spin(h, el=8):
    """Eight azimuths (45 deg apart, floor hidden, long lens) into spin_NNN.png and M060_spin.png (4 per row)."""
    kit = K.NS["KIT"]
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    orig, kit["render_group"] = m033._long_lens(kit)
    old = kit["CELL"]
    kit["CELL"] = (360, 300)
    paths = []
    try:
        for az in range(0, 360, 45):
            paths.append(kit["render_group"]([h], f"{d}/spin{az:03d}_sheet.png", az, el))
    finally:
        kit["render_group"] = orig
        kit["CELL"] = old
    rows = [kit["hstack"](paths[i:i + 4]) for i in range(0, 8, 4)]
    out = f"{d}/{M.code(NUM)}_spin.png"
    kit["save_px"](kit["vstack"](rows), out)
    return out


def render_close_ups(objs):
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    by = {o.name: o for o in objs}
    h = objs[0]
    out = {}

    def at(o, p):
        return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)
    rc = m033.render_close
    _CURVES.clear()
    F, st, bl, W0 = _frond_geo("F1")
    out["junction_cu"] = rc([h], f"{d}/junction_cu.png", -20, 10, at(h, (0.0, -0.2, 0.35)), 0.75)
    if ROOT_P in by:
        r = by[ROOT_P]
        out["underside"] = rc([r], f"{d}/underside_crown.png", 0, -60, at(r, (0, 0, 0.15)), 0.75)
    out["underside_hero"] = rc([h], f"{d}/underside_hero.png", 0, -50, at(h, (0, 0, 0.4)), 1.6)
    if LARGE_P in by:
        b = by[LARGE_P]
        p, T = bl.at(0.75)
        Wv, Nv = _frame(T, W0, 0.0)
        az = math.degrees(math.atan2(Wv.x, -Wv.y)) + 12
        out["thickness_cu"] = rc([b], f"{d}/thickness_cu.png", az, 10, at(b, p), 0.6)
        out["frond_face"] = rc([b], f"{d}/frond_face.png", math.degrees(math.atan2(-Nv.x, Nv.y)), 15,
                               at(b, bl.at(0.5)[0]), 1.2)
    out["edge_side"] = rc([h], f"{d}/edge_side.png", 90, 0, at(h, (0.0, 0.0, 1.4)), 1.9)
    out["root_cu"] = rc([h], f"{d}/root_cu.png", -15, 15, at(h, (0.0, -0.5, 0.3)), 0.9)
    kit = K.NS["KIT"]
    old = kit["CELL"]
    kit["CELL"] = (150, 130)
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        out["thumb"] = kit["render_group"]([h], f"{d}/thumb_sheet.png", 0, 5)
    finally:
        kit["render_group"] = orig
        kit["CELL"] = old
    return out


def preview(names=("front_sheet", "f34_sheet", "rear_sheet", "side_sheet", "top_sheet"), vfx=False):
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig


def hero_only():
    M.coll(NUM, TITLE)
    palette()
    EXPLODE["on"] = False
    h, lg = _make(HERO, hero_all, "hero", HERO_BUDGET)
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n, _ in PARTS if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    return {"hero": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                        "boundary_edges", "normals")}, "log": lg,
            "fronds": {k: dict(v) for k, v in FROND_INFO.items()}, "leaves": {k: dict(v) for k, v in LEAF_INFO.items()},
            "vis": {k: v for k, v in VIS.items() if not k.endswith("_e20")}, "offset": [round(x, 3) for x in h[OFF]]}
