"""069 Palisade Wall (references/069.png): one straight, tileable 16-stud section of a log palisade with its dressing.
Twelve upright octagonal chamfered timbers stand edge to edge on the log line y 0 (ten logs, two of them narrow filler
poles set back 0.15, and two thick posts inset one log from each end, the tallest pieces), each with a pale 8-facet
pyramid tip and a flat-cut foot on z 0. Two posts carry two three-turn rope bands each. Rails (0.90 x 0.70 chamfered
beams with pale end faces) run on both faces: two full rear rails (z 2.80 / 5.90) and a stepped front pair (5.40 / 7.10),
each span ending in a post's chamfer or against its band, with short stubs beyond the posts; seven rope lashings (open
C-runs over the rail, ends sunk into the log behind). A red swallowtail banner with a white double diamond hangs from a
knobbed rod on two pegs in front of the right half; lavender-grey chock rocks and lime rosettes stand along both faces.

    import importlib, kit_models, m069; importlib.reload(kit_models); importlib.reload(m069); m069.build()

Build frame: studs, front -Y (the outside, the banner face), +X right, ground z 0, the log axes on y 0, the module
centred on x 0. Every object ends with its origin at its bbox bottom centre; o["m069_offset"] is that origin in the
build frame (0, 0, 0 for the hero and the module: the dressing is symmetric, so no PivotOffset is needed).

Tile contract (spec 2.1, decision 8): pitch 16.000, seam planes x = -8.000 and +8.000, nothing crosses them; the end
logs L1 and L11 are the same Ø 1.47 octagon, their outer broad faces flat at x = -7.995 / +7.995 (a 0.01 slot between
modules); rails and stubs stop >= 0.70 inside the seams; rail levels rear 2.80 / 5.90, front 5.40 / 7.10, inner faces
|y| 0.73. Stored on the hero and the module: m069_offset, m069_seams, m069_rails, m069_pitch.

Names (spec 8): Stockade (hero, collision precise), StockadeStraight (the tiling module: the hero without banner, rocks
and rosettes; collision box), parts StockadeLog, StockadePost, StockadeRail, StockadeBanner, StockadeRock,
StockadeRosette. One object each, of closed shells (no booleans). Colour (stage 4) by role and position, never by
facing. Stages 5-6: the sheet shows no glow, light or effect: no emission, no sockets. See M069_spec.md.
"""
import json
import math
import os
import random
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M

NUM, TITLE, SHEET = 69, "Palisade Wall", "M069"
OFF = "m069_offset"
PFX = "_m069_"
HERO, PLAIN = "Stockade", "StockadeStraight"
LOG_P, POST_P, RAIL_P = "StockadeLog", "StockadePost", "StockadeRail"
BANNER_P, ROCK_P, ROSETTE_P = "StockadeBanner", "StockadeRock", "StockadeRosette"

TIMBER, TIMBER_END, TIMBER_DEEP = "m069_timber", "m069_timber_end", "m069_timber_deep"
ROPE, ROPE_DEEP = "m069_rope", "m069_rope_deep"
BANNER, BANNER_DEEP, WHITE = "m069_banner", "m069_banner_deep", "m069_cloth_white"
ROCK, ROCK_LIGHT, ROCK_DARK = "m069_rock", "m069_rock_light", "m069_rock_dark"
LEAF_LIGHT, LEAF, LEAF_DARK = "m069_leaf_light", "m069_leaf", "m069_leaf_dark"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
BURY = 0.05

# key -> (hex, roughness, metal, emission, low specular). Stage 4 (spec "Stage 4"): K.calibrate on the studio dome
# toward the sheet's rendered regions (TARGETS), then checked on the hero renders against the same regions.
PALETTE = {
    TIMBER: ("#8F5B28", 0.85, 0.0, 0.0, True),
    TIMBER_END: ("#CFA266", 0.8, 0.0, 0.0, True),
    TIMBER_DEEP: ("#69461F", 0.9, 0.0, 0.0, True),
    ROPE: ("#C49A5C", 0.95, 0.0, 0.0, True),
    ROPE_DEEP: ("#93652F", 0.95, 0.0, 0.0, True),
    BANNER: ("#FC231F", 0.9, 0.0, 0.0, True),
    BANNER_DEEP: ("#A9140F", 0.9, 0.0, 0.0, True),
    WHITE: ("#F4EEEC", 0.9, 0.0, 0.0, True),
    ROCK: ("#8A8594", 0.9, 0.0, 0.0, True),
    ROCK_LIGHT: ("#ABA6B4", 0.9, 0.0, 0.0, True),
    # rock_dark's dome run diverged (the stone sampler took the floor): its target scaled by rock's own ratio
    ROCK_DARK: ("#4E4C5C", 0.9, 0.0, 0.0, True),
    LEAF_LIGHT: ("#AACF0E", 0.85, 0.0, 0.0, True),
    LEAF: ("#9ACA1C", 0.85, 0.0, 0.0, True),
    LEAF_DARK: ("#2C5C1C", 0.85, 0.0, 0.0, True),
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions) and K.sample kinds
TARGETS = {TIMBER: ((0xAB, 0x64, 0x26), "brown"), TIMBER_END: ((0xF8, 0xB1, 0x5E), "brown"),
           TIMBER_DEEP: ((0x7A, 0x4A, 0x1D), "brown"), ROPE: ((0xD4, 0x99, 0x51), "brown"),
           ROPE_DEEP: ((0xA0, 0x62, 0x28), "brown"), BANNER: ((0xFC, 0x23, 0x1F), "vivid"),
           BANNER_DEEP: ((0xD4, 0x16, 0x10), "vivid"), ROCK: ((0x87, 0x83, 0x8E), "stone"),
           ROCK_LIGHT: ((0xB5, 0xAF, 0xB7), "stone"), ROCK_DARK: ((0x4E, 0x52, 0x61), "stone"),
           LEAF_LIGHT: ((0xB3, 0xD8, 0x0D), "green"), LEAF: ((0x81, 0xAF, 0x12), "green"),
           LEAF_DARK: ((0x2A, 0x5A, 0x18), "green")}

# colour bands (spec 5.3 / 5.5), by position: (top of the band above the foot, t toward timber_deep)
FOOT_BANDS = ((0.50, 0.50), (1.20, 0.25))
PIECE_TINT = 0.05
ROCK_TINT = 0.04
LEAF_TINT = 0.03
CLOTH_TINT = 0.02


def palette():
    for k, (hexcol, rough, metal, emit, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, metal=metal, emit=emit, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, metal=metal, emit=emit, low_spec=low)
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m069_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k == "m069_" + tail), None)
            if k1 in PALETTE and k2 and pct.isdigit():
                K.fk().KIT_PALETTE.pop(key, None)
                K.mix_key(k1, k2, int(pct) / 100)


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS). Returns {key: (hex, rendered)}."""
    keys = keys or list(TARGETS)
    try:
        for k in keys:
            K.fk().material(k)
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


# ---- small helpers -----------------------------------------------------------------------------------------------------
def _mix(k1, k2, t, step=0.05):
    t = round(round(max(0.0, min(1.0, t)) / step) * step, 2)
    return K.mix_key(k1, k2, t)


def _seed(name):
    return sum((i + 1) * ord(c) for i, c in enumerate(name))


def _rng(name):
    return random.Random(_seed(name))


def _rt(name, amp):
    return 1.0 + _rng(name).uniform(-amp, amp)


# ---- piece register ------------------------------------------------------------------------------------------------------
PIECES = []          # (kind, name, centroid in the build frame) per shell, in build order
ROPES = []           # open rope runs: name, end points, radius (both-ends contact check)
GEO = {}             # measured placements (report)


def _solid(a, pts, faces, key, tint=1.0):
    """One closed shell from points and faces of any winding: bmesh makes the winding consistent, then the shell is
    flipped as a whole if its signed volume is negative. Returns (verts, faces) in the order given."""
    bm = a.bm
    vs = [bm.verts.new(Vector(p)) for p in pts]
    fs = [bm.faces.new([vs[i] for i in f]) for f in faces]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    for f in fs:
        f.normal_update()
    vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs)
    if vol < 0:
        for f in fs:
            f.normal_flip()
            f.normal_update()
    a._finish(vs, key, tint=tint)
    return vs, fs


def _piece(a, pts, faces, kind, name, colour=None, key=TIMBER, tint=None):
    """Add one shell (build frame), registered; coloured per face by colour(face centre, face index) -> key."""
    if tint is None:
        tint = _rt(name, PIECE_TINT)
    vs, fs = _solid(a, pts, faces, key, tint)
    if colour is not None:
        for i, (f, idx) in enumerate(zip(fs, faces)):
            c = sum((Vector(pts[j]) for j in idx), Vector()) / len(idx)
            f.material_index = a._mi(colour(c, i))
    PIECES.append((kind, name, sum((v.co for v in vs), Vector()) / len(vs)))
    return vs, fs


CAP = {4: [[0, 1, 2, 3]], 8: [[0, 1, 2, 7], [7, 2, 3, 6], [6, 3, 4, 5]]}
HEXA = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (0, 4, 7, 3), (1, 2, 6, 5)]


def _box_pts(lo, hi):
    return [Vector((x, y, z)) for z in (lo[2], hi[2]) for (x, y) in ((lo[0], lo[1]), (hi[0], lo[1]),
                                                                   (hi[0], hi[1]), (lo[0], hi[1]))]


# ---- rope tubes (m048 _tube / m064 rope, copied) ---------------------------------------------------------------------
def _newell(pts):
    n = Vector()
    m = len(pts)
    for i in range(m):
        p, q = pts[i], pts[(i + 1) % m]
        n += Vector(((p.y - q.y) * (p.z + q.z), (p.z - q.z) * (p.x + q.x), (p.x - q.x) * (p.y + q.y)))
    return n


def _up_for(path):
    n = _newell(path)
    span = max((p - path[0]).length for p in path)
    if n.length > 1e-3 * max(span, 0.1) ** 2:
        return n.normalized()
    ch = path[-1] - path[0]
    u = ch.cross(Vector((0, 0, 1)))
    if u.length < 1e-4:
        u = ch.cross(Vector((1, 0, 0)))
    return u.normalized()


def _tube_rings(path, r, sides, closed, up, twist=True):
    """The rings of a low-poly twisted rope tube along path (m048._tube): each ring turned half a side from the last,
    bends mitred so the tube keeps its thickness."""
    P = [Vector(p) for p in path]
    N = len(P)
    upv = Vector(up)
    rings = []
    for i in range(N):
        prev = P[i - 1] if closed else P[max(i - 1, 0)]
        nxt = P[(i + 1) % N] if closed else P[min(i + 1, N - 1)]
        tin = (P[i] - prev) if (P[i] - prev).length > 1e-9 else (nxt - P[i])
        tout = (nxt - P[i]) if (nxt - P[i]).length > 1e-9 else tin
        tin, tout = tin.normalized(), tout.normalized()
        T = (tin + tout).normalized()
        U = (upv - upv.dot(T) * T).normalized()
        V = T.cross(U)
        B = tout - tin
        bend = B.length > 1e-6
        if bend:
            B.normalize()
        sc = 1.0 / max(0.5, tin.dot(T)) - 1.0
        ring = []
        for k in range(sides):
            ang = 2 * math.pi * (k + (0.5 * i if twist else 0.0)) / sides
            off = (U * math.cos(ang) + V * math.sin(ang)) * r
            if bend:
                off += B * off.dot(B) * sc
            ring.append(P[i] + off)
        rings.append(ring)
    return rings


def _tube_faces(N, sides, closed, twist=True):
    faces, strand = [], []
    segs = N if closed else N - 1
    for i in range(segs):
        j = (i + 1) % N
        shift = (N // 2) % sides if (twist and closed and j == 0) else 0
        for k in range(sides):
            a0, a1 = i * sides + k, i * sides + (k + 1) % sides
            b0, b1 = j * sides + (k + shift) % sides, j * sides + (k + 1 + shift) % sides
            faces += [[a0, a1, b0], [a1, b1, b0]]
            strand += [k, k]
    if not closed:
        # the end caps fanned into triangles (a 5-sided cap is an n-gon)
        for c in (list(reversed(range(sides))), [(N - 1) * sides + k for k in range(sides)]):
            for k in range(1, sides - 1):
                faces.append([c[0], c[k], c[k + 1]])
                strand.append(-1)
    return faces, strand


def rope(a, path, r, sides, closed, kind, name, up=None):
    """A twisted rope tube; one strand in four (by its place round the twist, never by facing) rope_deep."""
    path = [Vector(p) for p in path]
    if closed and len(path) % 2:
        raise ValueError(f"{name}: closed twisted rope needs an even point count")
    up = up if up is not None else _up_for(path)
    rings = _tube_rings(path, r, sides, closed, up)
    pts = [p for rg in rings for p in rg]
    faces, strand = _tube_faces(len(path), sides, closed)
    deep = ROPE_DEEP
    vs, fs = _piece(a, pts, faces, kind, name, key=ROPE, tint=_rt(name, 0.03),
                    colour=lambda c, i: deep if strand[i] == 0 else ROPE)
    if not closed:
        ROPES.append({"name": name, "ends": [list(path[0]), list(path[-1])], "rt": r})
    return vs


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


def _mitre(H, d):
    """The mitred offset polygon of a counter-clockwise convex polygon: every edge exactly d outside its hull edge."""
    n = len(H)
    out = []
    for i in range(n):
        p0, p1, p2 = H[i - 1], H[i], H[(i + 1) % n]
        e_a = Vector((p1[0] - p0[0], p1[1] - p0[1])).normalized()
        e_b = Vector((p2[0] - p1[0], p2[1] - p1[1])).normalized()
        n_a = Vector((e_a.y, -e_a.x))
        n_b = Vector((e_b.y, -e_b.x))
        bis = (n_a + n_b).normalized()
        out.append(Vector(p1) + bis * (d / max(bis.dot(n_a), 0.2)))
    return out


def hull_loop(pts3, c, m, ref, offset, n):
    """A rope loop round the convex hull of section points in the plane (c, m) (m064): the hull's mitred offset at
    `offset`, flattest corners dropped or longest edges split until there are n points."""
    m = m.normalized()
    e1 = (ref - m * ref.dot(m)).normalized()
    e2 = m.cross(e1)
    P = [((p - c).dot(e1), (p - c).dot(e2)) for p in pts3]
    H = _hull2(P)
    O = _mitre(H, offset)
    while len(O) > n:
        k = min(range(len(O)), key=lambda i: abs((O[i] - O[i - 1]).to_3d().cross((O[(i + 1) % len(O)] - O[i]).to_3d()).z))
        del O[k]
    while len(O) < n:
        k = max(range(len(O)), key=lambda i: (O[(i + 1) % len(O)] - O[i]).length)
        O.insert(k + 1, (O[k] + O[(k + 1) % len(O)]) / 2)
    return [c + e1 * p.x + e2 * p.y for p in O]


# ---- timbers (spec 2.2): every piece an 8-sided chamfered prism, axis vertical ----------------------------------------
SEAM = 7.995                        # the end logs' outer broad faces (x = -SEAM / +SEAM); the seam planes are x = +-8.000
PITCH = 16.0
GAP = 0.01                          # between neighbouring timbers (no coincident faces)
CH_K = 0.22 / math.sqrt(2.0)        # chamfer leg / diameter: each chamfer face 0.22 of the diameter wide
TIP_K = 0.70                        # tip length (shoulder to apex) / diameter
TIP_JIT = 0.06                      # seeded tip length variation (hand-cut), not on the end logs
APEX_JIT = 0.04                     # seeded apex offset, not on the end logs
# name, diameter (across flats), tip apex z, axis y, kind. L6 is 0.79 (spec 0.80) so the row closes at exactly 15.99
TIMBERS = (("L1", 1.47, 8.3, 0.0, "log"), ("P1", 1.75, 10.3, 0.0, "post"), ("L3", 1.25, 8.0, 0.0, "log"),
           ("L4", 1.35, 8.8, 0.0, "log"), ("L5", 1.25, 8.9, 0.0, "log"), ("L6", 0.79, 7.6, 0.15, "log"),
           ("L7", 1.35, 9.5, 0.0, "log"), ("L8", 1.45, 11.5, 0.0, "log"), ("L9", 1.30, 9.8, 0.0, "log"),
           ("P2", 1.75, 12.2, 0.0, "post"), ("L10", 0.70, 9.4, 0.15, "log"), ("L11", 1.47, 10.4, 0.0, "log"))
END_LOGS = ("L1", "L11")


def _layout():
    out = {}
    x = -SEAM
    for name, d, tip, y, kind in TIMBERS:
        h = d / 2
        rng = _rng("tip_" + name)
        jl, ja = (0.0, (0.0, 0.0)) if name in END_LOGS else (rng.uniform(-TIP_JIT, TIP_JIT),
                                                             (rng.uniform(-APEX_JIT, APEX_JIT),
                                                              rng.uniform(-APEX_JIT, APEX_JIT)))
        tl = TIP_K * d * (1.0 + jl)
        out[name] = {"name": name, "d": d, "h": h, "c": CH_K * d, "xc": x + h, "y": y, "x0": x, "x1": x + d,
                     "tip": tip, "sh": tip - tl, "tl": tl, "apex": ja, "kind": kind}
        x += d + GAP
    assert abs(x - GAP - SEAM) < 1e-6, x
    return out


TL = _layout()


def oct_sec(d):
    """The chamfered octagon (x, y) of diameter d across flats: broad faces to +-X and +-Y."""
    h, c = d / 2, CH_K * d
    return [(h - c, h), (h, h - c), (h, -(h - c)), (h - c, -h), (-(h - c), -h), (-h, -(h - c)), (-h, h - c),
            (-(h - c), h)]


def _foot_key(z):
    for top, t in FOOT_BANDS:
        if z < top - 1e-6:
            return _mix(TIMBER, TIMBER_DEEP, t)
    return TIMBER


def timber(a, T, xc=None, name=None):
    """One log or post (spec 2.2): an 8-sided chamfered prism from a flat-cut foot on z 0 (rings at the foot-band
    heights) up to the shoulder, then an 8-facet pyramid tip (TIP_K x d long, apex seeded off-centre). 62 tris.
    Timber with the foot bands toward timber_deep by height; the tip facets timber_end by role (the cut wood)."""
    xc = T["xc"] if xc is None else xc
    y, sh = T["y"], T["sh"]
    sec = oct_sec(T["d"])
    zs = [0.0] + [top for top, _ in FOOT_BANDS] + [sh]
    pts = [Vector((xc + u, y + v, z)) for z in zs for (u, v) in sec]
    pts.append(Vector((xc + T["apex"][0], y + T["apex"][1], T["tip"])))
    ap = len(pts) - 1
    faces = []
    for i in range(len(zs) - 1):
        for k in range(8):
            k1 = (k + 1) % 8
            faces.append([i * 8 + k, i * 8 + k1, (i + 1) * 8 + k1, (i + 1) * 8 + k])
    top = (len(zs) - 1) * 8
    for k in range(8):
        faces.append([top + k, top + (k + 1) % 8, ap])
    faces += [list(reversed(c)) for c in CAP[8]]

    def colour(c, i):
        return TIMBER_END if c.z > sh + 1e-6 else _foot_key(c.z)
    nm = name or T["name"]
    vs, fs = _piece(a, pts, faces, T["kind"], nm, colour)
    GEO.setdefault("timbers", {})[nm] = {"x": [round(xc - T["h"], 3), round(xc + T["h"], 3)], "d": T["d"],
                                         "tip": T["tip"], "shoulder": round(sh, 3),
                                         "tip_len_d": round(T["tl"] / T["d"], 3)}
    return vs


# ---- post bands (spec 2.4: 3 closed twisted turns round each post) ----------------------------------------------------
RB = 0.18                           # band rope radius (Ø 0.36)
BAND_OFF = 0.16                     # rope centreline off the post faces (sinks RB - BAND_OFF = 0.02)
BAND_STEP = 0.34                    # turn spacing (turns overlap 0.02: each touches the next)
BAND_SIDES, BAND_PTS = 5, 8
BANDS = {"P1": (2.10, 6.40), "P2": (2.10, 6.60)}      # bottom of each band (z)


def _poly2(T):
    """A timber's octagon in plan (x, y), counter-clockwise."""
    return [(T["xc"] + u, T["y"] + v) for u, v in reversed(oct_sec(T["d"]))]


def _near2(poly, p):
    """(nearest boundary point, signed distance: negative inside) of a convex CCW polygon to the 2D point p."""
    best, bq = 1e9, None
    inside = True
    n = len(poly)
    for i in range(n):
        a_, b_ = Vector(poly[i]), Vector(poly[(i + 1) % n])
        e = b_ - a_
        if e.x * (p.y - a_.y) - e.y * (p.x - a_.x) < 0:
            inside = False
        t = max(0.0, min(1.0, (p - a_).dot(e) / e.length_squared))
        q = a_ + e * t
        d = (p - q).length
        if d < best:
            best, bq = d, q
    return bq, (-best if inside else best)


def _collinear(path, closed, tol=math.radians(2.0)):
    """Drop path points where the path runs straight on (tube rings there add nothing)."""
    out = list(path)
    i = 0 if closed else 1
    while len(out) > (4 if closed else 2) and i < len(out) - (0 if closed else 1):
        p0, p1, p2 = out[i - 1], out[i], out[(i + 1) % len(out)]
        a_, b_ = p1 - p0, p2 - p1
        if a_.length > 1e-9 and b_.length > 1e-9 and a_.angle(b_) < tol:
            del out[i]
        else:
            i += 1
    return out


BAND_KEEP = RB - 0.02             # a band point stays where its centreline is this far clear of a neighbouring timber
BAND_END_SINK = 0.04              # a band run's end: this deep into the neighbour it meets


def band_paths(post, xc=None, alone=False):
    """The centreline paths of a post's bands: [(band index, turn index, path, closed)]. Each turn is the mitred
    offset loop round the post's octagon (m064 hull_loop); in the wall the neighbouring timbers stand 0.01 from the
    post, so the loop is cut where it would pass through them: a front run and a rear run, each end carried on to
    sink BAND_END_SINK into the neighbour it meets, square to its surface. `alone` (the Post part): closed loops."""
    T = TL[post]
    xc = T["xc"] if xc is None else xc
    neigh = [] if alone else [_poly2(U) for U in TL.values() if U is not T and abs(U["xc"] - T["xc"]) < 3.0]
    out = []
    for bi, z0 in enumerate(BANDS[post]):
        for ti in range(3):
            z = z0 + RB + ti * BAND_STEP
            c = Vector((xc, T["y"], z))
            sec = [Vector((xc + u, T["y"] + v, z)) for u, v in oct_sec(T["d"])]
            loop = hull_loop(sec, c, Vector((0, 0, 1)), Vector((1, 0, 0)), BAND_OFF, BAND_PTS)
            if not neigh:
                out.append((bi, ti, loop, True))
                continue
            fine = []
            for i in range(len(loop)):
                fine += [loop[i], loop[i].lerp(loop[(i + 1) % len(loop)], 0.5)]
            n = len(fine)

            def clear(p):
                return min(_near2(P, p.to_2d())[1] for P in neigh)
            ok = [clear(p) >= BAND_KEEP for p in fine]
            start = next(i for i in range(n) if ok[i] and not ok[i - 1])
            runs, cur = [], []
            for j in range(n):
                i = (start + j) % n
                if ok[i]:
                    cur.append(fine[i])
                elif cur:
                    runs.append(cur)
                    cur = []
            if cur:
                runs.append(cur)
            for ri, run in enumerate(runs):
                pts = list(run)
                for end in (0, -1):
                    k = pts[end]
                    q, d = min((_near2(P, k.to_2d()) for P in neigh), key=lambda r: r[1])
                    dirv = (q - k.to_2d()).normalized()
                    e = Vector((q.x + dirv.x * BAND_END_SINK, q.y + dirv.y * BAND_END_SINK, z))
                    if end == 0:
                        pts.insert(0, e)
                    else:
                        pts.append(e)
                out.append((bi, ti, _collinear(pts, False), False))
    return out


def bands(a, post, xc=None, tag=None, alone=False):
    for i, (bi, ti, path, closed) in enumerate(band_paths(post, xc, alone)):
        rope(a, path, RB, BAND_SIDES, closed, "band", f"band_{tag or post}_{bi}_{ti}_{i}", up=Vector((0, 0, 1)))


# ---- rails, stubs (spec 2.4): 0.90 H x 0.70 D chamfered beams, inner faces at |y| 0.73 ---------------------------------
RAIL_HZ, RAIL_HY, RAIL_CH = 0.45, 0.35, 0.06
RAIL_IN = 0.73
RAIL_YC = RAIL_IN + RAIL_HY        # 1.08
CHAM_SINK = 0.02                    # a span end in a post's chamfer: its inner edge this deep into the chamfer face
BAND_SINK = 0.03                    # a span end against a band: rail and rope this deep into each other at most
RAILS = {"RR1": (2.80, 1), "RR2": (5.90, 1), "RF1": (5.40, -1), "RF2": (7.10, -1)}
# member, rail, west end, east end; an end is ("cham", post) / ("band", post, band index) / ("x", value) / ("len", L)
SPANS = (("RR1", "RR1", ("band", "P1", 0), ("band", "P2", 0)), ("RR2", "RR2", ("cham", "P1"), ("cham", "P2")),
         ("RF1", "RF1", ("cham", "P1"), ("x", 2.60)), ("RF2", "RF2", ("x", 1.45), ("band", "P2", 1)))
STUBS = (("RR1_w", "RR1", ("len", 0.45), ("band", "P1", 0)), ("RR1_e", "RR1", ("band", "P2", 0), ("x", 6.85)),
         ("RR2_w", "RR2", ("len", 0.60), ("cham", "P1")), ("RR2_e", "RR2", ("cham", "P2"), ("x", 6.85)),
         ("RF1_w", "RF1", ("len", 0.60), ("cham", "P1")), ("RF2_e", "RF2", ("band", "P2", 1), ("x", 7.30)))


def _end_x(spec, rail, away):
    """x of a member's end at a post: `away` = +1 when the member runs off toward +X from that end, -1 toward -X."""
    z, side = RAILS[rail]
    if spec[0] == "x":
        return spec[1]
    T = TL[spec[1]]
    if spec[0] == "cham":
        lx = 2 * T["h"] - T["c"] - RAIL_IN - CHAM_SINK * math.sqrt(2.0)
        return T["xc"] + away * lx
    return _seat_on_band(spec[1], spec[2], z, side, away)


def _beam_geom(x0, x1, z, side):
    sec = _rail_sec(side)
    pts = [Vector((x, u, z + v)) for x in (x0, x1) for (u, v) in sec]
    faces = []
    for k in range(8):
        k1 = (k + 1) % 8
        faces.append([k, k1, 8 + k1, 8 + k])
    faces += [list(reversed(c)) for c in CAP[8]] + [[8 + i for i in c] for c in CAP[8]]
    return pts, faces


def _shell_pts(pts, faces):
    """A shell's verts, face centres and edge midpoints: the points the depth tests probe."""
    out = list(pts) + [sum((pts[i] for i in f), Vector()) / len(f) for f in faces]
    for f in faces:
        for i in range(len(f)):
            out.append((pts[f[i]] + pts[f[(i + 1) % len(f)]]) / 2)
    return out


def _depth(points, tree):
    """Deepest of points inside a closed shell (ray parity), as distance to its surface."""
    d = 0.0
    for p in points:
        h = tree.find_nearest(p)
        if h[0] is not None and h[3] > d and _parity_in(tree, p):
            d = h[3]
    return d


def _seat_on_band(post, bi, z, side, away):
    """x of a rail end that stops against a post's band: bisected so the deeper of (beam into any rope run, any rope
    run into the beam) is BAND_SINK. away = the direction the beam runs off from this end."""
    T = TL[post]
    tubes = []
    for b, ti, path, closed in band_paths(post):
        if b != bi:
            continue
        rings = _tube_rings(path, RB, BAND_SIDES, closed, Vector((0, 0, 1)))
        pts = [p for r in rings for p in r]
        faces, _ = _tube_faces(len(path), BAND_SIDES, closed)
        tubes.append((_shell_pts(pts, faces), BVHTree.FromPolygons(pts, faces)))

    def depth(e):
        far = e + away * 3.0
        pts, faces = _beam_geom(min(e, far), max(e, far), z, side)
        sec = _rail_sec(side)
        grid = [Vector((e, u, z + v)) for u in np.linspace(min(p[0] for p in sec), max(p[0] for p in sec), 8)
                for v in np.linspace(-RAIL_HZ, RAIL_HZ, 8)]
        bpts = _shell_pts(pts, faces) + grid
        btree = BVHTree.FromPolygons(pts, faces)
        return max(max(_depth(bpts, t), _depth(tp, btree)) for tp, t in tubes)
    lo = T["xc"] + away * (T["h"] - 0.05)            # deep in the band
    hi = T["xc"] + away * (T["h"] + 2 * RB + BAND_OFF + 0.3)    # clear of it
    for _ in range(18):
        mid = (lo + hi) / 2
        if depth(mid) > BAND_SINK:
            lo = mid
        else:
            hi = mid
    return hi


def member_x(m):
    """(x0, x1) of a span or stub."""
    _, rail, w, e = m
    if w[0] == "len":
        x1 = _end_x(e, rail, -1)
        return x1 - w[1], x1
    x0 = _end_x(w, rail, 1)
    x1 = x0 + e[1] if e[0] == "len" else _end_x(e, rail, -1)
    return x0, x1


def _rail_sec(side):
    hy, hz, c = RAIL_HY, RAIL_HZ, RAIL_CH
    sec = [(-hy + c, -hz), (hy - c, -hz), (hy, -hz + c), (hy, hz - c), (hy - c, hz), (-hy + c, hz), (-hy, hz - c),
           (-hy, -hz + c)]
    return [(side * RAIL_YC + u, v) for u, v in sec]


def beam(a, x0, x1, z, side, kind, name):
    """A rail span or stub along X from x0 to x1: the chamfered 8-sided section, square ends. 28 tris. Timber, the
    two end faces timber_end by role (the cut ends)."""
    pts, faces = _beam_geom(x0, x1, z, side)
    vs, fs = _piece(a, pts, faces, kind, name, lambda c, i: TIMBER_END if i >= 8 else TIMBER)
    GEO.setdefault("members", {})[name] = [round(x0, 3), round(x1, 3), z, side]
    return vs


# ---- lashings (spec 2.4): open C-runs over the rail's three exposed faces, both ends sunk into the log behind -------
RL = 0.14                           # lashing rope radius (Ø 0.28)
LASH_OFF = 0.12                     # rope centreline off the rail faces (sinks RL - LASH_OFF = 0.02)
LASH_STEP = 0.28
LASH_SINK = 0.04                    # the run ends this deep into the log face behind the rail
LASH_SIDES = 5
# rail, centre x (a log's axis or a value), turns
LASHINGS = (("RF1", "L3", 3), ("RF1", "L5", 3), ("RF2", 7.00, 2), ("RR1", "L3", 2), ("RR1", "L8", 2),
            ("RR2", "L3", 2), ("RR2", "L8", 2))


def _log_at(x):
    return next(T for T in TL.values() if T["x0"] <= x <= T["x1"])


def lashing(a, rail, at, turns, tag, log=None):
    """`turns` vertical open runs over the rail, LASH_STEP apart round x = at; each run's two ends are carried back to
    sink LASH_SINK into the face of the log behind (log: that log's face |y| when built without the log)."""
    z, side = RAILS[rail]
    xc = TL[at]["xc"] if isinstance(at, str) else at
    yo = side * (RAIL_IN + 2 * RAIL_HY + LASH_OFF)
    zt, zb = z + RAIL_HZ + LASH_OFF, z - RAIL_HZ - LASH_OFF
    out = []
    for i in range(turns):
        x = xc + (i - (turns - 1) / 2) * LASH_STEP
        if log is None:
            T = _log_at(x)
            yface = T["y"] + side * T["h"]
        else:
            yface = side * log
        ye = yface - side * LASH_SINK
        path = [Vector((x, ye, zt)), Vector((x, yo, zt)), Vector((x, yo, zb)), Vector((x, ye, zb))]
        out.append(rope(a, path, RL, LASH_SIDES, False, "lash", f"lash_{tag}_{i}", up=Vector((1, 0, 0))))
    return out


def wall(a):
    """The tiling module: twelve timbers, four bands, four rail spans, six stubs, seven lashings."""
    for T in TL.values():
        timber(a, T)
    for p in BANDS:
        bands(a, p)
    for m in SPANS + STUBS:
        x0, x1 = member_x(m)
        z, side = RAILS[m[1]]
        beam(a, x0, x1, z, side, "rail" if m in SPANS else "stub", m[0])
    for rail, at, n in LASHINGS:
        lashing(a, rail, at, n, f"{rail}_{at}")


# ---- banner (spec 2.5; front, hero only, "optional and removable") -----------------------------------------------------
PEG_H, PEG_TOP, PEG_Y1 = 0.15, 8.35, -1.95       # square 0.30 pegs, tops at 8.35, out to the rod's front face
PEGS = (("L8", 1.92), ("P2", 4.66))
PEG_SINK = 0.05
ROD_Y, ROD_R, ROD_X = -1.80, 0.15, (1.62, 4.96)  # rod: across flats 0.30, resting on the pegs (0.005 seat)
ROD_ZC = PEG_TOP + ROD_R - 0.005
KNOB_R, KNOB_IN = 0.21, 0.17                     # knob balls: centre KNOB_IN past each rod end
CLOTH_X = (2.22, 4.42)
CLOTH_T = 0.08
CLOTH_FRONT = ROD_Y - CLOTH_T / 2                # -1.84
SLEEVE_IN, SLEEVE_T = 0.17, 0.07                 # the hem sleeve round the rod: inner circumradius, wall
CLOTH_TOP = ROD_ZC - (SLEEVE_IN + SLEEVE_T) * math.cos(math.pi / 8) + 0.017   # 0.017 up into the sleeve
HEM_Z = 8.00                                     # the hem band row (one blend step toward banner_deep above it)
POINT_Z, NOTCH_Z = 1.95, 3.25
EMB_C = (3.32, 5.50)
EMB_RINGS = ((0.65, 1.45, 0.14), (0.35, 0.775, 0.12))   # half width, half height, line width
DECO_T, DECO_PROUD = 0.02, 0.01                  # emblem / stripes: 0.02 slabs, 0.01 proud of the cloth front
STRIPE_W, STRIPE_IN, STRIPE_TOP = 0.10, 0.12, 8.20


def _oct_x(x, yc, zc, r):
    """An 8-gon in the plane x = const round (yc, zc), circumradius r, flats down / up / front / back."""
    return [Vector((x, yc + r * math.cos(math.pi / 8 + k * math.pi / 4), zc + r * math.sin(math.pi / 8 + k * math.pi / 4)))
            for k in range(8)]


def _prism_x(rings):
    """Faces of a closed 8-sided prism along X through rings of 8 points (CAP quads at both ends)."""
    faces = []
    for i in range(len(rings) - 1):
        for k in range(8):
            k1 = (k + 1) % 8
            faces.append([i * 8 + k, i * 8 + k1, (i + 1) * 8 + k1, (i + 1) * 8 + k])
    last = (len(rings) - 1) * 8
    faces += [list(reversed(c)) for c in CAP[8]] + [[last + i for i in c] for c in CAP[8]]
    return faces


def _ball_x(c, r, segs=6, rings=3):
    """A low-poly ball with its poles on the X axis (the rod's knobs): segs x (rings - 1) verts + 2 poles."""
    c = Vector(c)
    pts = [c - Vector((r, 0, 0))]
    for i in range(1, rings):
        el = -math.pi / 2 + math.pi * i / rings
        for k in range(segs):
            az = 2 * math.pi * k / segs
            pts.append(c + Vector((r * math.sin(el), r * math.cos(el) * math.cos(az), r * math.cos(el) * math.sin(az))))
    pts.append(c + Vector((r, 0, 0)))
    faces = []
    for k in range(segs):
        faces.append([0, 1 + (k + 1) % segs, 1 + k])
    for i in range(rings - 2):
        b0, b1 = 1 + i * segs, 1 + (i + 1) * segs
        for k in range(segs):
            k1 = (k + 1) % segs
            faces.append([b0 + k, b0 + k1, b1 + k1, b1 + k])
    top = len(pts) - 1
    b = 1 + (rings - 2) * segs
    for k in range(segs):
        faces.append([b + k, b + (k + 1) % segs, top])
    return pts, faces


def _diamond_ring(a, cx, cz, hw, hh, line, y0, y1, name):
    """A closed diamond ring slab (y0..y1): outer rhombus hw x hh, the inner one each edge `line` inside it."""
    k = 1.0 - line * math.hypot(hw, hh) / (hw * hh)
    outer = [(cx + hw, cz), (cx, cz + hh), (cx - hw, cz), (cx, cz - hh)]
    inner = [(cx + hw * k, cz), (cx, cz + hh * k), (cx - hw * k, cz), (cx, cz - hh * k)]
    pts = [Vector((x, y, z)) for y in (y0, y1) for (x, z) in outer + inner]
    faces = []
    for s in (0, 8):
        for i in range(4):
            j = (i + 1) % 4
            faces.append([s + i, s + j, s + 4 + j, s + 4 + i])
    for i in range(4):
        j = (i + 1) % 4
        faces.append([i, j, 8 + j, 8 + i])                      # outer wall
        faces.append([4 + i, 4 + j, 12 + j, 12 + i])            # inner wall
    return _piece(a, pts, faces, "emblem", name, key=WHITE, tint=_rt(name, CLOTH_TINT))


def _slab_xz(a, poly, y0, y1, kind, name, key, colour=None, tris=None):
    """A closed slab between y0 and y1 of a simple polygon in (x, z); `tris` triangulates the outline (else fan)."""
    n = len(poly)
    pts = [Vector((x, y, z)) for y in (y0, y1) for (x, z) in poly]
    tris = tris or [(0, i, i + 1) for i in range(1, n - 1)]
    faces = [list(t) for t in tris] + [[n + i for i in t] for t in tris]
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, n + j, n + i])
    return _piece(a, pts, faces, kind, name, colour, key=key, tint=_rt(name, CLOTH_TINT))


def banner(a):
    """Pegs on L8 and P2, the rod resting on them with a knob at each end, the hem sleeve round the rod, the
    swallowtail cloth (a closed 0.08 slab hanging from the sleeve), the white double-diamond emblem and the two edge
    stripes (closed 0.02 slabs, 0.01 proud of the cloth's front)."""
    hang = {}
    for log, x in PEGS:
        T = TL[log]
        yf = T["y"] - T["h"] + PEG_SINK
        _piece(a, _box_pts((x - PEG_H, PEG_Y1, PEG_TOP - 2 * PEG_H), (x + PEG_H, yf, PEG_TOP)), HEXA, "peg",
               f"peg_{log}", lambda c, i: TIMBER_END if abs(c.y - PEG_Y1) < 1e-6 else TIMBER)
        hang[log] = [x, round(T["y"] - T["h"], 4), PEG_TOP - PEG_H]
    GEO["hang"] = hang
    rr = ROD_R / math.cos(math.pi / 8)
    rings = [_oct_x(x, ROD_Y, ROD_ZC, rr) for x in ROD_X]
    _piece(a, [p for r in rings for p in r], _prism_x(rings), "rod", "rod")
    for i, x in enumerate((ROD_X[0] - KNOB_IN, ROD_X[1] + KNOB_IN)):
        pts, faces = _ball_x((x, ROD_Y, ROD_ZC), KNOB_R)
        _piece(a, pts, faces, "knob", f"knob_{i}", key=TIMBER_END, tint=_rt(f"knob_{i}", 0.03))
    # hem sleeve: an 8-sided tube round the rod (outer and inner walls, end rings)
    ro, ri = SLEEVE_IN + SLEEVE_T, SLEEVE_IN
    pts = []
    for x in CLOTH_X:
        pts += _oct_x(x, ROD_Y, ROD_ZC, ro) + _oct_x(x, ROD_Y, ROD_ZC, ri)
    faces = []
    for k in range(8):
        k1 = (k + 1) % 8
        faces.append([k, k1, 16 + k1, 16 + k])                 # outer wall
        faces.append([8 + k, 24 + k, 24 + k1, 8 + k1])         # inner wall
        faces.append([k, 8 + k, 8 + k1, k1])                   # west end ring
        faces.append([16 + k, 16 + k1, 24 + k1, 24 + k])       # east end ring
    hem = _mix(BANNER, BANNER_DEEP, 0.5)
    _piece(a, pts, faces, "sleeve", "sleeve", key=hem, tint=_rt("sleeve", CLOTH_TINT))
    # cloth: A' A B B' (the hem band) over the swallowtail A' B' C D E
    x0, x1 = CLOTH_X
    xm = (x0 + x1) / 2
    poly = [(x0, CLOTH_TOP), (x1, CLOTH_TOP), (x1, HEM_Z), (x1, POINT_Z), (xm, NOTCH_Z), (x0, POINT_Z), (x0, HEM_Z)]
    tris = [(0, 1, 2), (0, 2, 6), (6, 2, 4), (2, 3, 4), (6, 4, 5)]
    band = _mix(BANNER, BANNER_DEEP, 0.25)
    _slab_xz(a, poly, CLOTH_FRONT, CLOTH_FRONT + CLOTH_T, "cloth", "cloth", BANNER,
             colour=lambda c, i: band if c.z > HEM_Z + 1e-6 else BANNER, tris=tris)
    yd0, yd1 = CLOTH_FRONT - DECO_PROUD, CLOTH_FRONT - DECO_PROUD + DECO_T
    for i, (hw, hh, line) in enumerate(EMB_RINGS):
        _diamond_ring(a, EMB_C[0], EMB_C[1], hw, hh, line, yd0, yd1, f"emblem_{i}")
    slope = (NOTCH_Z - POINT_Z) / (xm - x0)
    lift = STRIPE_IN * math.sqrt(1 + slope * slope)
    for i, (sa, sb) in enumerate(((x0 + STRIPE_IN, x0 + STRIPE_IN + STRIPE_W), (x1 - STRIPE_IN - STRIPE_W, x1 - STRIPE_IN))):
        def zb(x):
            return (POINT_Z + (x - x0) * slope if x < xm else POINT_Z + (x1 - x) * slope) + lift
        _slab_xz(a, [(sa, zb(sa)), (sb, zb(sb)), (sb, STRIPE_TOP), (sa, STRIPE_TOP)], yd0, yd1, "stripe",
                 f"stripe_{i}", WHITE)


# ---- rocks (spec 2.6): chunky faceted chock stones, flat bottoms on z 0 -----------------------------------------------
# name, centre (x, y), W x D x H, seed. Each is then pushed in y until it just meets the wall (seat_rock).
ROCKS = (("F1", (-7.00, -1.52), (1.60, 1.50, 1.70), 11), ("F3", (-4.05, -1.25), (1.00, 1.00, 0.85), 13),
         ("F4", (-0.60, -1.35), (1.30, 1.20, 1.20), 17), ("F5", (3.60, -1.25), (1.10, 1.00, 0.80), 19),
         ("F6", (5.90, -1.50), (1.60, 1.50, 1.70), 23), ("B1", (5.70, 1.55), (1.80, 1.60, 1.95), 29),
         ("B2", (-2.90, 1.50), (1.90, 1.50, 1.70), 31), ("B3", (-6.70, 1.50), (1.70, 1.50, 1.80), 37))
ROCK_FOOT = ((0.16, 0.50), (0.32, 0.25))     # soil grime at the foot: (top as a fraction of the height, t to dark)
ROCK_PATCH = (0.85, 0.16, 0.40, -0.22, 0.20)  # broad noise patches: scale, light level, t to light, dark level, t


def rock_geom(size, seed):
    """Points and triangles of a chunky faceted stone (convex hull of jittered rings: a 5-point foot on z 0, a 5-point
    shoulder, a broad 4-point upper ring and a 2-point broken top: a block with sloping top facets, not an egg),
    centred on (0, 0)."""
    rng = random.Random(seed)
    W, D, H = size
    rings = ((0.0, 0.94, 5, 0.0), (0.48, 1.0, 5, 0.5), (0.84, 0.80, 4, 0.25), (1.0, 0.46, 2, 0.1))
    pts = []
    yaw = rng.uniform(0, math.pi)
    for hf, rf, n, ph in rings:
        for k in range(n):
            t = yaw + 2 * math.pi * (k + ph) / n + rng.uniform(-0.18, 0.18)
            r = rf * rng.uniform(0.92, 1.06)
            z = 0.0 if hf == 0 else H * hf * (rng.uniform(0.94, 1.0) if hf == 1.0 else rng.uniform(0.92, 1.08))
            pts.append(Vector((math.cos(t) * W / 2 * r, math.sin(t) * D / 2 * r, z)))
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    for v in list(bm.verts):
        if not v.link_faces:
            bm.verts.remove(v)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.verts.index_update()
    out_pts = [v.co.copy() for v in bm.verts]
    out_faces = [[v.index for v in f.verts] for f in bm.faces]
    bm.free()
    return out_pts, out_faces


def _overlaps(pts, faces, tree):
    t = BVHTree.FromPolygons(pts, faces)
    return bool(t.overlap(tree))


def seat_rock(pts, faces, c, side, tree, step=0.6):
    """Push a rock (local points) toward the wall from c until it would meet it: the y of the last clear placement
    (bisected to 0.002). side -1 front, +1 rear."""
    def placed(y):
        return [p + Vector((c[0], y, 0.0)) for p in pts]
    far = c[1] + side * 1.5
    if _overlaps(placed(far), faces, tree):
        return far
    near = far
    while not _overlaps(placed(near), faces, tree):
        near -= side * step
        if abs(near) < 0.2:
            return near
    for _ in range(14):
        mid = (near + far) / 2
        if _overlaps(placed(mid), faces, tree):
            near = mid
        else:
            far = mid
    return far


def rock(a, name, c, size, seed, tree=None, side=None):
    pts, faces = rock_geom(size, seed)
    y = c[1] if tree is None else seat_rock(pts, faces, c, side, tree)
    wp = [p + Vector((c[0], y, 0.0)) for p in pts]
    H = size[2]

    sc, lv, tl, dv, td = ROCK_PATCH
    field = K.noise_field(scale=sc, seed=seed)

    def colour(cc, i):
        """By position, never by facing: a soil band up the foot (the hidden underside stays plain), then broad
        lighter and darker patches over the rest."""
        hf = cc.z / H
        if hf < 0.01:
            return ROCK
        for top, t in ROCK_FOOT:
            if hf < top:
                return _mix(ROCK, ROCK_DARK, t)
        n = field(cc)
        return _mix(ROCK, ROCK_LIGHT, tl) if n > lv else _mix(ROCK, ROCK_DARK, td) if n < dv else ROCK
    _piece(a, wp, faces, "rock", f"rock_{name}", colour, key=ROCK, tint=_rt(name, ROCK_TINT))
    GEO.setdefault("rocks", {})[name] = [round(c[0], 3), round(y, 3)]
    return wp, faces


# ---- rosettes (spec 2.6): six broad round folded leaves radiating round a dark centre--------------------------------
# name, centre x, side, reach radius (outer leaf tips), seed
# name, centre x, side, reach along X and across (outer leaf tips from the centre: low bushes stretched along the wall's
# foot, as the sheet's clumps are), seed
ROSETTES = (("G1", -5.30, -1, 1.40, 0.95, 41), ("G2", -2.35, -1, 1.45, 0.95, 43), ("G3", 1.00, -1, 1.45, 0.95, 47),
            ("G4", 6.95, -1, 1.00, 0.85, 53), ("G5", 6.90, 1, 1.00, 0.85, 59), ("G6", 3.40, 1, 1.45, 0.95, 61),
            ("G7", -4.65, 1, 1.45, 0.95, 67), ("G8", 4.75, -1, 1.00, 0.85, 71),
            ("G9", 0.40, 1, 1.45, 0.95, 73))
DRESS_X = 7.95                      # nothing of the dressing past |x| 7.95 (the seam planes are +-8.000)
DRESS_Y = 2.50                      # outermost leaf tips at |y| 2.50 on both faces (symmetric bbox)
LEAF_N, LEAF_WL = 6, 1.0
LEAF_FOLD = math.tan(math.radians(28))
LEAF_BASE_R = 0.10
LEAF_OUTLINE = [(0.14, 0.42), (0.48, 0.5), (0.84, 0.36)]   # disc (kit_mcp.LEAF_OUTLINES): round blunt, 16 tris
LEAF_TIERS = ((40, 46, 1.0), (60, 68, 0.95))       # alternate leaves: low and long / high and shorter (pitch deg, L)


def leaf_geom(base, L, W, yaw, pitch, fold=LEAF_FOLD, curl=0.06, thick=0.05, camber=0.0):
    """kit_mcp.leaf's ovate leaf as points and faces: the outline fanned to a front point on the midrib and a back
    ridge (a closed shallow wedge), folded along the midrib (edges lifted fold x |y|, the front point not raised, so
    each half is one plane turned the full fold angle: no facet turns edge-on with the leaf), the tip curled down."""
    rot = Matrix.Rotation(yaw, 3, "Z") @ Matrix.Rotation(-pitch, 3, "Y")
    B = Vector(base)
    ring = [(0.0, 0.0)] + [(f * L, -h * W) for f, h in LEAF_OUTLINE] + [(L, 0.0)] + \
           [(f * L, h * W) for f, h in reversed(LEAF_OUTLINE)]

    def place(x, y, z):
        t = x / L
        return B + rot @ Vector((x, y, z - curl * L * t * t))
    pts = [place(x, y, fold * abs(y)) for x, y in ring]
    pts.append(place(0.52 * L, 0.0, camber * L))
    pts.append(place(0.52 * L, 0.0, -thick))
    n = len(ring)
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append([n, i, j])
        faces.append([n + 1, j, i])
    along = [0.0] + [f for f, _ in LEAF_OUTLINE] + [1.0] + [f for f, _ in reversed(LEAF_OUTLINE)]
    fpos = []
    for i in range(n):
        j = (i + 1) % n
        fpos += [(0.52 + along[i] + along[j]) / 3] * 2
    return pts, faces, fpos


# (along-leaf limit, partner, t) per tier: the low outer leaves dark at the heart, mid, lime at the tip; the high inner
# leaves (shaded under the clump on the sheet) one step deeper: dark at the heart, mid green above
LEAF_BANDS = (((0.40, LEAF_DARK, 0.45), (0.62, None, 0.0), (9.0, LEAF_LIGHT, 1.0)),
              ((0.40, LEAF_DARK, 0.55), (0.62, LEAF_DARK, 0.2), (9.0, None, 0.0)))
LEAF_W_MAX = 1.15
LEAF_SHRINK = 0.86                 # a leaf that meets the wall or a rock is shortened by this, up to 6 times


def rosette_leaves(rx, ry, seed, yaw0):
    """Per leaf (yaw, pitch, length): six leaves round the centre, alternately low / long and high / shorter, each long
    enough for its tip to reach the ellipse (rx, ry) round the centre."""
    rng = random.Random(seed)
    out = []
    for k in range(LEAF_N):
        yaw = yaw0 + 2 * math.pi * k / LEAF_N + rng.uniform(-0.17, 0.17)
        p0, p1, lk = LEAF_TIERS[k % 2]
        pitch = math.radians(rng.uniform(p0, p1))
        reach = 1.0 / math.sqrt((math.cos(yaw) / rx) ** 2 + (math.sin(yaw) / ry) ** 2)
        L = (reach - LEAF_BASE_R) / math.cos(math.radians(LEAF_TIERS[0][1])) * lk * rng.uniform(0.95, 1.03)
        out.append((yaw, pitch, L))
    return out


def rosette_leaf(cx, cy, yaw, pitch, L):
    base = (cx + math.cos(yaw) * LEAF_BASE_R, cy + math.sin(yaw) * LEAF_BASE_R, 0.0)
    pts, faces, fpos = leaf_geom(base, L, min(L * LEAF_WL, LEAF_W_MAX), yaw, pitch)
    zmin = min(p.z for p in pts)
    return [p - Vector((0, 0, zmin)) for p in pts], faces, fpos


def _leaf_bad(pts, faces, tree):
    """A leaf that meets what is already built, or crosses |x| DRESS_X."""
    return max(abs(p.x) for p in pts) > DRESS_X or (tree is not None and _overlaps(pts, faces, tree))


def rosette(a, name, cx, side, rx, ry, seed, tree=None, tag=None):
    """Six leaves (alternately low and high) turned radially outward round (cx, cy), cy set so the outermost tip
    reaches |y| DRESS_Y; the whole rosette turned (yaw0) to the setting where the fewest leaves meet what is already
    built (tree), then each leaf that still does is shortened until it clears."""
    best = None
    for s_ in range(12):
        yaw0 = _rng(name).uniform(0, 2 * math.pi) + s_ * (2 * math.pi / LEAF_N) / 12
        params = rosette_leaves(rx, ry, seed, yaw0)
        probe = [rosette_leaf(cx, 0.0, *p) for p in params]
        ext = max(side * q.y for pts, _, _ in probe for q in pts)
        cy = side * (DRESS_Y - ext)
        leaves = [rosette_leaf(cx, cy, *p) for p in params]
        hits = sum(_leaf_bad(pts, faces, tree) for pts, faces, _ in leaves)
        if best is None or hits < best[0]:
            best = (hits, cy, params, leaves)
        if hits == 0:
            break
    hits, cy, params, leaves = best
    shrunk = 0
    if hits:
        for k, (yaw, pitch, L) in enumerate(params):
            for _ in range(8):
                if not _leaf_bad(leaves[k][0], leaves[k][1], tree):
                    break
                L *= LEAF_SHRINK
                leaves[k] = rosette_leaf(cx, cy, yaw, pitch, L)
                shrunk += 1
    for k, (pts, faces, fpos) in enumerate(leaves):
        def colour(c, i, fpos=fpos, bands=LEAF_BANDS[k % 2]):
            for lim, k2, t in bands:
                if fpos[i] < lim:
                    return LEAF if k2 is None else _mix(LEAF, k2, t)
            return LEAF_LIGHT
        _piece(a, pts, faces, "leaf", f"leaf_{tag or name}_{k}", colour, key=LEAF, tint=_rt(f"{name}{k}", LEAF_TINT))
    GEO.setdefault("rosettes", {})[name] = {"c": [cx, round(cy, 3)], "hits": hits, "shrunk": shrunk}
    return leaves


def dressing(a):
    """Rocks seated against the wall, then rosettes clear of the wall and the rocks."""
    tree = K.bvh(a)
    for name, c, size, seed in ROCKS:
        rock(a, name, c, size, seed, tree, -1 if c[1] < 0 else 1)
    tree = K.bvh(a)
    for name, cx, side, rx, ry, seed in ROSETTES:
        rosette(a, name, cx, side, rx, ry, seed, tree)
        tree = K.bvh(a)


def hero_all(a):
    wall(a)
    banner(a)
    dressing(a)


def hero_nobanner(a):
    wall(a)
    dressing(a)


# ---- parts (spec 8) ------------------------------------------------------------------------------------------------------
def log_part(a):
    """'Palisade Log (uneven height)': L4 (Ø 1.35, tip 8.8) on its own."""
    timber(a, TL["L4"], xc=0.0)


def post_part(a):
    """The tall post P2 (12.2) with its two three-turn bands."""
    timber(a, TL["P2"], xc=0.0)
    bands(a, "P2", xc=0.0, alone=True)


RAIL_PART_LEN = 9.0


def rail_part(a):
    """'Horizontal Beam': one rear rail (RR length) with a three-turn lashing at its middle (the ends sunk 0.04 behind
    the rail's inner face, where a log would be)."""
    z, side = RAILS["RR2"]
    beam(a, -RAIL_PART_LEN / 2, RAIL_PART_LEN / 2, z, side, "rail", "rail")
    lashing(a, "RR2", 0.0, 3, "rail", log=RAIL_IN - 0.005)


def banner_part(a):
    banner(a)


def rock_part(a):
    """'Ground Rock (Stone)': F1."""
    name, c, size, seed = ROCKS[0]
    rock(a, name, (0.0, 0.0), size, seed)


def rosette_part(a):
    """'Foliage (Decorative)': G2."""
    name, cx, side, rx, ry, seed = ROSETTES[1]
    rosette(a, name, 0.0, side, rx, ry, seed)


SEAMS = (-PITCH / 2, PITCH / 2)
RAIL_LEVELS = {k: v[0] for k, v in RAILS.items()}
NOTES = {
    HERO: "Palisade wall module (16-stud pitch, seams x -8 / +8, nothing crosses them; end logs L1 / L11 identical Ø "
          "1.47 octagons with outer faces at -7.995 / +7.995): ten sharpened octagonal logs (two narrow fillers set "
          "back) and two banded posts (10.3, 12.2), rear rails at 2.80 / 5.90 and a stepped front pair at 5.40 / 7.10 "
          "(inner faces |y| 0.73) with stubs and seven rope lashings, a red swallowtail banner with a white double "
          "diamond on a knobbed rod, lavender-grey chock rocks and lime rosettes. Origin on the log line at mid-module "
          "(no PivotOffset). Studio: check a character can't climb the rocks and front rails over the tips "
          "(Requires Manual Validation). Sheet header 73/132.",
    PLAIN: "The tiling module: the hero without banner, rocks and rosettes. Place every 16 studs along X with one "
           "rotation; module N's L11 meets module N+1's L1 across a 0.01 slot. Collision box.",
    LOG_P: "Palisade Log (uneven height): one octagonal chamfered log, Ø 1.35, pale 8-facet pyramid tip at 8.8, "
           "flat-cut foot",
    POST_P: "Post: the tall Ø 1.75 post (tip 12.2) with its two three-turn rope bands",
    RAIL_P: "Horizontal Beam: one 9-stud chamfered rail (0.90 x 0.70) with a three-turn rope lashing",
    BANNER_P: "Banner (optional and removable): two pegs, a knobbed rod, hem sleeve, red swallowtail cloth with two "
              "white edge stripes and a white double diamond; m069_hang holds the pegs' wall-face points",
    ROCK_P: "Ground Rock (Stone): a chunky faceted lavender-grey chock stone, flat bottom",
    ROSETTE_P: "Foliage (Decorative): six broad round folded lime leaves in two tiers round a dark centre",
}
COLLISION = {HERO: "precise", PLAIN: "box", LOG_P: "box", POST_P: "box", RAIL_P: "box", BANNER_P: "none",
             ROCK_P: "hull", ROSETTE_P: "none"}
ROLES = {HERO: "hero", PLAIN: "variant"}
# the kit check reads a pale tip on a lone log as painted light (its tip facets face up); the tip is the sheet's Wood
# (Secondary) swatch, the cut wood, coloured by role on every timber
SHADING_OK = {LOG_P: "pale cut tip: the sheet's Wood (Secondary) swatch on the pyramid facets by role (the cut end "
                     "grain), a real material change, not light"}


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
    o["m069_pieces"] = json.dumps([[k, n_, [round(x, 5) for x in c]] for k, n_, c in PIECES])
    o["m069_ropes"] = json.dumps(ROPES)
    bpy.context.view_layer.update()
    return o


def _bottom_centre(o):
    xs = [v.co.x for v in o.data.vertices]
    ys = [v.co.y for v in o.data.vertices]
    zs = [v.co.z for v in o.data.vertices]
    return Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))


def _recentre(o):
    bc = _bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


def _uv_overlaps(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    uv = bm.loops.layers.uv.active
    tris = []
    for f in bm.faces:
        ls = [(l[uv].uv.x, l[uv].uv.y) for l in f.loops]
        for i in range(1, len(ls) - 1):
            tris.append((f.index, [ls[0], ls[i], ls[i + 1]]))
    bm.free()
    boxes = [(min(p[0] for p in t), min(p[1] for p in t), max(p[0] for p in t), max(p[1] for p in t)) for _, t in tris]
    grid = {}
    for k, b in enumerate(boxes):
        for i in range(int(b[0] // 0.05), int(b[2] // 0.05) + 1):
            for j in range(int(b[1] // 0.05), int(b[3] // 0.05) + 1):
                grid.setdefault((i, j), []).append(k)
    pairs = {(a_, b_) for lst in grid.values() for i, a_ in enumerate(lst) for b_ in lst[i + 1:]
             if tris[a_][0] != tris[b_][0]}
    return [(tris[a_][0], tris[b_][0]) for a_, b_ in pairs if M._tri_overlap(tris[a_][1], tris[b_][1])]


def _uv_unfold(o, rounds=4):
    """Cut the smaller face of each UV-overlapping pair free along seams and unwrap again (m012). Returns faces cut."""
    cut = 0
    for _ in range(rounds):
        bad = _uv_overlaps(o)
        if not bad:
            break
        polys = o.data.polygons
        free = {min((a_, b_), key=lambda i: polys[i].area) for a_, b_ in bad}
        keys = {tuple(sorted(e)) for i in free for e in polys[i].edge_keys}
        for e in o.data.edges:
            if tuple(sorted(e.vertices)) in keys:
                e.use_seam = True
        cut += len(free)
        with M._override(o):
            bpy.ops.object.mode_set(mode="EDIT")
            try:
                bpy.ops.mesh.select_all(action="SELECT")
                bpy.ops.uv.unwrap(method=UV["method"], fill_holes=False, correct_aspect=True,
                                  margin_method="FRACTION", margin=UV["margin"])
            finally:
                bpy.ops.object.mode_set(mode="OBJECT")
    return cut


def _post(o, uv=True):
    """Stage 2-3 pass: normals outward per shell, flat shading, no custom normals, origin at the bbox bottom centre,
    bowties split, UVs (angle-based islands, overlaps cut free). Every face is built as a planar quad or a triangle
    (the 8-sided caps are split into quads): no n-gons."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    ng = [f for f in bm.faces if len(f.verts) > 4]
    if ng:
        bmesh.ops.triangulate(bm, faces=ng, quad_method="BEAUTY", ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = False
    if o.data.has_custom_normals:
        with M._override(o):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
    _recentre(o)
    lg = {"bowties": M.fix_bowties(o), "ngons_split": len(ng)}
    if uv:
        M.smart_uv(o, **UV)
        lg["uv_cut"] = _uv_unfold(o)
    K.drop_unused_slots(o)
    return lg


def _make(name, fn, role="part", budget=1000, temp=False):
    t0 = time.time()
    o = _new(name, fn, role, budget, temp=temp)
    lg = _post(o, uv=not temp)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


def _store_points(o):
    o["m069_seams"] = list(SEAMS)
    o["m069_rails"] = json.dumps({"levels": RAIL_LEVELS, "inner_y": RAIL_IN})
    o["m069_pitch"] = PITCH


# ---- checks ---------------------------------------------------------------------------------------------------------------
_PDIRS = (Vector((1.0, 0.0131, 0.0217)).normalized(), Vector((-0.0173, 1.0, 0.0119)).normalized(),
          Vector((0.0109, -0.0207, 1.0)).normalized())


def _parity_in(tree, p):
    """Ray parity (m046 / m047): inside a closed shell if at least two of three skewed rays cross it an odd number of
    times."""
    votes = 0
    for d in _PDIRS:
        n, q = 0, p.copy()
        for _ in range(64):
            h = tree.ray_cast(q, d, 1000.0)
            if h[0] is None:
                break
            n += 1
            q = h[0] + d * 1e-4
        votes += n % 2
    return votes >= 2


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
    reg = [(k, nm, Vector(c)) for k, nm, c in json.loads(o.get("m069_pieces", "[]"))]
    labels, used = [], set()
    for fs in groups:
        vs = list({v for f in fs for v in f.verts})
        c = sum((v.co for v in vs), Vector()) / len(vs) + off
        best = min(((i, (rc - c).length) for i, (_, _, rc) in enumerate(reg) if i not in used),
                   key=lambda x: x[1], default=(None, 0))
        if best[0] is not None and best[1] < 0.02:
            used.add(best[0])
            labels.append(reg[best[0]][:2])
        else:
            labels.append(("?", "?"))
    return bm, ids, n, groups, labels


def _fmin(f):
    """Smallest corner angle of a face (radians)."""
    vs = [v.co for v in f.verts]
    m = len(vs)
    out = math.pi
    for i in range(m):
        e1, e2 = vs[i - 1] - vs[i], vs[(i + 1) % m] - vs[i]
        if e1.length > 1e-9 and e2.length > 1e-9:
            out = min(out, e1.angle(e2))
    return out


def thin_report(o, lim=3.0):
    """Faces with a corner under lim degrees, the smallest corner on the mesh, non-planar quads."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    angs = [_fmin(f) for f in bm.faces]
    nonplanar = sum(1 for f in bm.faces if len(f.verts) == 4 and
                    abs((f.verts[3].co - f.verts[0].co).dot((f.verts[1].co - f.verts[0].co).cross(
                        f.verts[2].co - f.verts[0].co).normalized())) > 1e-4)
    bm.free()
    return {"under": sum(1 for x in angs if x < math.radians(lim)), "min_deg": round(math.degrees(min(angs)), 2),
            "nonplanar_quads": nonplanar}


def _parity_check(fs):
    """Winding by parity (044's wedge): from each face centre step 0.002 along its normal; the point must be outside
    the shell by ray parity. Returns the number of faces whose normal points inward."""
    vs = list({v for f in fs for v in f.verts})
    vi = {v: i for i, v in enumerate(vs)}
    tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
    bad = 0
    for f in fs:
        if f.calc_area() < 1e-8:
            continue
        p = f.calc_center_median() + f.normal * 0.002
        if _parity_in(tree, p):
            bad += 1
    return bad


def shells_report(o):
    """Per shell: kind, name, tris, non-manifold edges and verts, boundary edges, winding errors (manifold edges whose
    two faces run the same way round), self-intersecting face pairs, signed volume, parity winding."""
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
        out.append({"kind": labels[k][0], "name": labels[k][1], "tris": sum(len(f.verts) - 2 for f in fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary),
                    "winding_errors": sum(1 for e in es if e.is_manifold and not e.is_contiguous),
                    "self_hits": hits, "volume": round(vol, 5), "parity_out": _parity_check(fs)})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating pieces (STAGES): per shell its nearest gap to another shell (0 where triangles intersect or touch)
    or the ground, and whether it chains by contact to the ground."""
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
    ground = {k for k in range(n) if zmin[k] - z0 <= 0.005}
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
    unch = chained(tol)
    res = {"shells": n, "floating": len(floating), "floating_names": [labels[k][1] for k in floating],
           "worst_gap": round(max([gap[k] for k in range(n)], default=0.0), 4),
           "unchained": len(unch), "unchained_names": unch,
           "on_ground": sorted({labels[k][0] for k in ground}),
           "feet_z": round(z0 + (o[OFF][2] if OFF in o else 0.0), 4),
           "kinds": {k: [lb[0] for lb in labels].count(k) for k in sorted({lb[0] for lb in labels})}}
    bm.free()
    return res


def bury_report(o):
    """Nothing buried (STAGES): per shell pair, the deepest vert / face centre of one inside the other (ray parity,
    depth to its surface), judged against BURY; shells wholly inside others; the worst sink per kind pair."""
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
        info.append({"kind": labels[s][0], "name": labels[s][1], "lo": lo, "hi": hi, "tree": tree,
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
                d = B["tree"].find_nearest(p)[3]
                if d < 1e-4:
                    continue
                if _parity_in(B["tree"], p):
                    inside_any[j] = True
                    dmax = max(dmax, d)
            if dmax <= 0:
                continue
            pair = (A["kind"], B["kind"])
            worst[pair] = max(worst.get(pair, 0.0), dmax)
            if dmax > BURY + 1e-3:
                over.append({"shell": A["name"], "in": B["name"], "depth": round(dmax, 3)})
        if all(inside_any):
            hidden.append(A["name"])
    bm.free()
    return {"worst_depth": {f"{a_}>{b_}": round(d, 3) for (a_, b_), d in sorted(worst.items())},
            "over_limit": over, "fully_hidden": hidden, "buried": len(over) + len(hidden)}


def pierce_report(o, thin=("cloth", "emblem", "stripe", "sleeve")):
    """Thin slabs hide pass-throughs from the bury report: count the edges of every other shell that cross a thin
    slab's surface twice (in one side and out the other)."""
    bm, ids, n, groups, labels = _shells(o)
    cos, polys = [], []
    for k in range(n):
        if labels[k][0] not in thin:
            continue
        vs = list({v for f in groups[k] for v in f.verts})
        vi = {v: i + len(cos) for i, v in enumerate(vs)}
        cos += [v.co.copy() for v in vs]
        polys += [[vi[v] for v in f.verts] for f in groups[k]]
    out = {}
    if polys:
        tree = BVHTree.FromPolygons(cos, polys)
        for k in range(n):
            if labels[k][0] in thin:
                continue
            bad = 0
            for e in {e for f in groups[k] for e in f.edges}:
                p, q = e.verts[0].co, e.verts[1].co
                d = q - p
                L = d.length
                if L < 1e-6:
                    continue
                d = d / L
                hits, t0 = 0, 0.0
                while t0 < L and hits < 2:
                    h = tree.ray_cast(p + d * (t0 + 1e-4), d, L - t0 - 1e-4)
                    if h[0] is None:
                        break
                    hits += 1
                    t0 = (h[0] - p).length + 1e-4
                bad += hits >= 2
            if bad:
                out[labels[k][1]] = bad
    bm.free()
    return out


def rope_ends_report(o):
    """Every open rope run touches what it ties at both ends: each end point's gap to the nearest other shell (surface
    distance minus the rope radius, 0 when the end is inside another shell)."""
    bm, ids, n, groups, labels = _shells(o)
    off = Vector(o[OFF])
    fsh = [ids[f.index] for f in bm.faces]
    tree = BVHTree.FromBMesh(bm)
    byname = {labels[k][1]: k for k in range(n)}
    out, bad = {}, []
    for r in json.loads(o.get("m069_ropes", "[]")):
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
    return {"worst": max([g for v in out.values() for g in v if g is not None], default=0.0), "loose": bad}


def seam_report(o):
    """Tile contract (spec 2.1): extents against the seam planes, the end logs' outer faces (flat at +-7.995 over their
    broad face, identical sections), every vertex inside |x| 7.995 (+0.001), rails and stubs >= 0.70 inside."""
    off = Vector(o[OFF])
    xs = [v.co.x + off.x for v in o.data.vertices]
    out = {"x_min": round(min(xs), 4), "x_max": round(max(xs), 4),
           "past_seam": sum(1 for x in xs if abs(x) > SEAM + 0.001)}
    faces = {}
    for s in (-1, 1):
        flat = [v.co + off for v in o.data.vertices if abs((v.co.x + off.x) - s * SEAM) < 1e-4]
        if flat:
            faces[s] = {"n": len(flat), "y": [round(min(p.y for p in flat), 4), round(max(p.y for p in flat), 4)],
                        "z": [round(min(p.z for p in flat), 4), round(max(p.z for p in flat), 4)]}
    out["end_faces"] = faces
    L1, L11 = TL["L1"], TL["L11"]
    out["end_logs_same_section"] = L1["d"] == L11["d"] and abs(L1["xc"] + L11["xc"]) < 1e-9 and L1["y"] == L11["y"]
    mem = GEO.get("members", {})
    out["member_ends"] = {k: v[:2] for k, v in mem.items()}
    out["member_min_inset"] = round(min((SEAMS[1] - max(abs(v[0]), abs(v[1])) for v in mem.values()), default=9.0), 3)
    out["pitch"] = PITCH
    return out


def levels_report():
    """Spec 4.4 shape targets from the build: the ordered skyline, tip lengths, rail levels and sections, rope sizes."""
    sky = [round(T["tip"], 2) for T in TL.values()]
    return {"skyline": sky, "shoulders": [round(T["sh"], 2) for T in TL.values()],
            "tip_len_d": [round(T["tl"] / T["d"], 3) for T in TL.values()],
            "diameters": [T["d"] for T in TL.values()], "rails": RAIL_LEVELS,
            "rail_section": [2 * RAIL_HZ, 2 * RAIL_HY], "rail_inner_y": RAIL_IN,
            "band_rope_d": 2 * RB, "lash_rope_d": 2 * RL,
            "bands": {p: [[round(z0, 2), round(z0 + 2 * RB + 2 * BAND_STEP, 2)] for z0 in zs] for p, zs in BANDS.items()},
            "banner": {"w": round(CLOTH_X[1] - CLOTH_X[0], 3), "top": round(ROD_ZC, 3), "points": POINT_Z,
                       "notch": NOTCH_Z, "emblem": [2 * EMB_RINGS[0][0], 2 * EMB_RINGS[0][1]], "cloth_t": CLOTH_T}}


def leaf_sweep_report(o, step=5, elevations=(0, 10)):
    """STAGES' foliage check: sweep the azimuth in `step` degree steps; per step, the share of leaf area belonging to
    whole leaves that are edge-on (at least 75 % of their upper facets within 15 deg of edge-on, or projected area under
    0.26 of their face-on area). Returns the worst step per elevation and the mean-plane-edge-on share (reported only)."""
    bm, ids, n, groups, labels = _shells(o)
    leaves = []
    for k in range(n):
        if labels[k][0] != "leaf":
            continue
        fs = groups[k]
        rows = [(f.normal.copy(), f.calc_area()) for f in fs]
        nsum = sum((nn * a_ for nn, a_ in rows if nn.z > 0), Vector())
        face_on = nsum.length
        up = [(nn, a_) for nn, a_ in rows if nn.dot(nsum) > 0]
        leaves.append((up, face_on, nsum.normalized() if face_on > 0 else Vector((0, 0, 1))))
    bm.free()
    if not leaves:
        return {}
    total = sum(fo for _, fo, _ in leaves)
    lim = math.sin(math.radians(15))
    out = {}
    for el in elevations:
        worst, worst_az, plane = 0.0, None, 0.0
        for az in range(0, 360, step):
            a_, e_ = math.radians(az), math.radians(el)
            v = Vector((math.sin(a_) * math.cos(e_), -math.cos(a_) * math.cos(e_), math.sin(e_)))
            edge, pl = 0.0, 0.0
            for up, fo, mn in leaves:
                area = sum(x for _, x in up)
                near = sum(x for nn, x in up if abs(nn.dot(v)) < lim)
                proj = sum(abs(nn.dot(v)) * x for nn, x in up)
                if near >= 0.75 * area or proj < 0.26 * fo:
                    edge += fo
                if abs(mn.dot(v)) < lim:
                    pl += fo
            if edge / total > worst:
                worst, worst_az = edge / total, az
            plane = max(plane, pl / total)
        out[f"e{el}"] = {"worst_edge_on_share": round(worst, 3), "at_az": worst_az,
                         "mean_plane_edge_on_max": round(plane, 3)}
    out["leaves"] = len(leaves)
    return out


# ---- build ---------------------------------------------------------------------------------------------------------------
PARTS = ((LOG_P, log_part), (POST_P, post_part), (RAIL_P, rail_part), (BANNER_P, banner_part), (ROCK_P, rock_part),
         (ROSETTE_P, rosette_part))
# hero W (X), D (Y), H (Z) +- tolerance (spec 2.7 / 4.4)
TARGET_SIZE = ((15.99, 0.01), (5.00, 0.10), (12.20, 0.2))
PLAIN_SIZE = ((15.99, 0.01), (3.38, 0.10), (12.20, 0.2))
HERO_BUDGET = 4000
PLAIN_BUDGET = 3000
THIN_FLOOR = 0.3                                          # deg: smallest face corner allowed (M064 ruling 2)


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m069_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", HERO))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def export_stats(objs):
    """What the exporter's STATS line would report: VFX sockets and glow (Neon) keys (none on this sheet)."""
    out = {}
    for o in objs:
        socks = [c for c in o.children_recursive if c.get("vfx_kind")]
        glow = sorted({m.name[3:] for m in o.data.materials if list(m.get("flintkit_spec", [0, 0, 0]))[2] > 0})
        out[o.name] = {"vfx_sockets": len(socks), "glow_keys": glow}
    return out


def build(render=True, parts=True, close=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn)
            if name in SHADING_OK:
                objs[name]["kit_shading_ok"] = SHADING_OK[name]
    GEO.clear()
    pl, log["plain"] = _make(PLAIN, wall, "variant", PLAIN_BUDGET)
    h, log["hero"] = _make(HERO, hero_all, "hero", HERO_BUDGET)
    geo = json.loads(json.dumps(GEO, default=lambda v: [round(x, 3) for x in v]))
    for o in (h, pl):
        _store_points(o)
    if BANNER_P in objs:
        b = objs[BANNER_P]
        off = Vector(b[OFF])
        b["m069_hang"] = json.dumps({k: [round(x - o_, 4) for x, o_ in zip(v, off)] for k, v in GEO["hang"].items()})
    _cleanup_tmp()
    order = [h, pl] + [objs[n] for n, _ in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.2f} x {d.y:.2f} x {d.z:.2f}"
    audits = [M.audit(o) for o in order]
    thin = {o.name: thin_report(o) for o in order}
    shells = {o.name: shells_report(o) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = HERO_BUDGET if o is h else PLAIN_BUDGET if o is pl else 999
        if au["tris"] > lim:
            problems.append(f"{o.name}: {au['tris']} tris over {lim}")
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "wire_edges", "loose_verts",
                  "zero_area_faces", "ngons", "dup_verts"):
            if au[k]:
                problems.append(f"{o.name}: {k} {au[k]}")
        if au["normals"] != "outward":
            problems.append(f"{o.name}: normals {au['normals']}")
        for i, s in enumerate(shells[o.name]):
            for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "winding_errors", "self_hits",
                      "parity_out"):
                if s[k]:
                    problems.append(f"{o.name} shell {i} ({s['name']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['name']}): not closed outward (volume {s['volume']})")
            if s["kind"] == "?":
                problems.append(f"{o.name} shell {i}: not matched to a built piece")
        if thin[o.name]["nonplanar_quads"]:
            problems.append(f"{o.name}: {thin[o.name]['nonplanar_quads']} non-planar quads")
        if thin[o.name]["min_deg"] < THIN_FLOOR:
            problems.append(f"{o.name}: a face corner of {thin[o.name]['min_deg']} deg (floor {THIN_FLOOR})")
    contact = {o.name: contact_report(o) for o in order}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: floating {c['floating_names']}, unchained {c['unchained_names']}")
        if abs(c["feet_z"]) > 0.005 and n_ in (HERO, PLAIN):
            problems.append(f"{n_}: feet at z {c['feet_z']}")
    bury = {o.name: bury_report(o) for o in order}
    for n_, b_ in bury.items():
        if b_["buried"]:
            problems.append(f"{n_}: buried {b_['over_limit']} hidden {b_['fully_hidden']}")
    pierce = {o.name: pierce_report(o) for o in (h, objs.get(BANNER_P)) if o}
    for n_, p_ in pierce.items():
        if p_:
            problems.append(f"{n_}: thin slabs pierced {p_}")
    ropes = {o.name: rope_ends_report(o) for o in order}
    for n_, r_ in ropes.items():
        if r_["loose"]:
            problems.append(f"{n_}: rope ends loose {r_['loose']}")
    seams = {o.name: seam_report(o) for o in (h, pl)}
    for n_, s_ in seams.items():
        if s_["past_seam"] or not s_["end_logs_same_section"] or s_["member_min_inset"] < 0.70 - 1e-6:
            problems.append(f"{n_}: seam contract {s_['past_seam']} past, inset {s_['member_min_inset']}")
    pivot = {o.name: [round(x, 4) for x in o[OFF]] for o in (h, pl)}
    for n_, p_ in pivot.items():
        if abs(p_[0]) > 0.02 or abs(p_[1]) > 0.05 or abs(p_[2]) > 0.005:
            problems.append(f"{n_}: origin off the build origin by {p_}")
    for o, sizes in ((h, TARGET_SIZE), (pl, PLAIN_SIZE)):
        for (tgt, tol), got, ax in zip(sizes, o.dimensions, "WDH"):
            if abs(got - tgt) > tol + 1e-6:
                problems.append(f"{o.name}: {ax} {got:.3f} outside {tgt} +- {tol}")
    sweep = {o.name: leaf_sweep_report(o) for o in (h, objs.get(ROSETTE_P)) if o}
    for n_, sw in sweep.items():
        for el, r_ in sw.items():
            if isinstance(r_, dict) and r_["worst_edge_on_share"] > 0.10:
                problems.append(f"{n_}: edge-on leaves {r_['worst_edge_on_share']} at az {r_['at_az']} ({el})")
    winding = {o.name: sum(s["winding_errors"] + s["parity_out"] for s in shells[o.name]) for o in order}
    bowties = {o.name: au["nonmanifold_verts"] for o, au in zip(order, audits)}
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
        if u.get("min_gap") is not None and u["min_gap"] < 0.008:
            problems.append(f"{n_}: UV island gap {u['min_gap']} under 0.008")
    stats = export_stats(order)
    for n_, s in stats.items():
        if s["vfx_sockets"] or s["glow_keys"]:
            problems.append(f"{n_}: sockets / glow on a sheet with none {s}")
    kinds = {}
    for s in shells[HERO]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts", "origin_offset", "transforms_applied")} for au in audits],
           "hero_shells": kinds, "contact": contact, "bury": bury, "pierce": pierce, "ropes": ropes, "seams": seams,
           "pivot": pivot, "levels": levels_report(), "sweep": sweep, "winding": winding, "bowties": bowties,
           "thin": thin, "log": log, "geo": geo, "problems": problems, "uv": uv, "export_stats": stats,
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders -------------------------------------------------------------------------------------------------------------
# spec 2.8: front_sheet (0, 0) the X layout and skyline, rear_sheet (180, 0) the rear rails, side_sheet (90, 0) the
# depth, f34_sheet the read (probed: see the spec's stage 1 notes), r34_sheet = the f34 with the banner hidden (spec
# 3.2), top_sheet (0, 89.9); floor hidden and a 3x lens in every *_sheet shot
F34 = (-22, 12)
SHEET_VIEWS = {"front_sheet": (0, 0), "side_sheet": (90, 0), "rear_sheet": (180, 0), "f34_sheet": F34,
               "r34_sheet": F34, "top_sheet": (0, 89.9)}
NOBANNER = ("r34_sheet",)
VIEW_NAMES = ("front34", "rear34", "front", "side", "rear", "top")
SHEET_LENS = 3.0
PARTS_SHOT = (-25, 15)
PART_SHOTS = {RAIL_P: (-20, 20), BANNER_P: (-20, 10)}
SPIN = tuple(range(0, 360, 45))
SPIN_EL = 10


def _long_lens(kit):
    """render_group with a long lens and the studio floor hidden for the *_sheet shots (m033 / m031)."""
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


def _at(o, p):
    return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)


def _linked(o, tag, m):
    c = bpy.data.objects.new(f"{PFX}{tag}", o.data)
    o.users_collection[0].objects.link(c)
    c.matrix_world = m
    return c


def _remove(objs):
    for o in objs:
        me = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(me, bpy.types.Mesh) and me.users == 0:
            bpy.data.meshes.remove(me)


def _tiles(o, n=(-1, 1)):
    """Linked copies of a module at k x PITCH along X (the tiling shots)."""
    out = [_linked(o, f"tile_{o.name}_{k}", o.matrix_world @ Matrix.Translation((k * PITCH, 0, 0))) for k in n]
    bpy.context.view_layer.update()
    return out


def _exploded(objs):
    """Linked copies of the parts laid out like the sheet's Exploded Construction: logs and the post standing in a row,
    two rails floating between them, the banner on the right, rocks and rosettes in front."""
    by = {o.name: o for o in objs}
    h = objs[0]
    o0 = Matrix.Translation((h.location.x + 40, h.location.y, 0))
    shown = []

    def put(tag, part, loc, rz=0.0):
        if part in by:
            shown.append(_linked(by[part], "expl_" + tag, o0 @ Matrix.Translation(loc) @ Matrix.Rotation(rz, 4, "Z")))
    put("log1", LOG_P, (-7.0, 0.0, 1.2))
    put("log2", LOG_P, (-4.8, 0.0, 0.6))
    put("rail1", RAIL_P, (0.0, 0.0, 6.0))
    put("rail2", RAIL_P, (0.0, 0.0, 3.2))
    put("post", POST_P, (5.6, 0.0, 0.8))
    put("banner", BANNER_P, (8.4, -1.0, 2.0))
    put("rock", ROCK_P, (-6.0, -3.2, 0.0))
    put("rosette1", ROSETTE_P, (-1.5, -3.4, 0.0))
    put("rosette2", ROSETTE_P, (2.5, -3.0, 0.0), 0.7)
    bpy.context.view_layer.update()
    return shown


def _marker(h, at, name):
    """A 5.5-stud character stand-in."""
    a = K.fk().Asset(PFX + name, "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=ROCK_DARK, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=ROCK_DARK, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=ROCK_DARK, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    c.location = _at(h, at)
    bpy.context.view_layer.update()
    return c


def _nobanner(h):
    """The hero without the banner (the sheet's r34 draws none), lined up with the hero."""
    o, _ = _make(PFX + "nobanner", hero_nobanner, temp=True)
    o.location = h.location + Vector(o[OFF]) - Vector(h[OFF])
    bpy.context.view_layer.update()
    return o


def render_views(objs, close=True):
    h = objs[0]
    pl = next((o for o in objs if o.name == PLAIN), None)
    shown = _exploded(objs) if len(objs) > 2 else []
    nb = _nobanner(h)
    tiles = _tiles(h)
    ptiles = _tiles(pl) if pl else []
    markers = [_marker(h, (TL["L3"]["xc"], -3.2, 0.0), "char")]
    try:
        extra = {k: ([nb] if k in NOBANNER else [h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        for o in objs[1:]:
            extra["part_" + (o.name.replace(HERO, "").lower() or "hero")] = ([o], *PART_SHOTS.get(o.name, PARTS_SHOT))
        if shown:
            extra["exploded"] = (shown, -25, 15)
        extra["scale"] = ([h] + markers, -25, 8)
        extra["tiling_front_sheet"] = ([h] + tiles, 0, 0)
        extra["tiling_f34"] = ([h] + tiles, -30, 18)
        extra["tiling_top_sheet"] = ([h] + tiles, 0, 89.9)
        if pl:
            extra["tiling_plain_f34"] = ([pl] + ptiles, -30, 18)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            sheet = M.views(NUM, [h], names=VIEW_NAMES, extra=extra, vfx=False)
            spin = render_spin(h)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet, "spin": spin}
        if close:
            out.update(render_close_ups(objs, tiles))
        return out
    finally:
        _remove(shown + markers + tiles + ptiles + [nb])
        M.display(NUM, objs, TITLE)


def render_spin(h):
    """The eight-azimuth contact sheet: az 0, 45 ... 315 at e 10, long lens, floor hidden -> M069_spin.png."""
    kit = K.NS["KIT"]
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    old = kit["CELL"]
    kit["CELL"] = (420, 360)
    try:
        paths = [kit["render_group"]([h], f"{d}/spin{az:03d}_sheet.png", az, SPIN_EL) for az in SPIN]
    finally:
        kit["CELL"] = old
    rows = [kit["hstack"](paths[i:i + 4]) for i in (0, 4)]
    out = f"{d}/M069_spin.png"
    kit["save_px"](kit["vstack"](rows), out)
    return out


def render_close(objs, path, az, el, centre, radius, cell=(480, 400), floor=True):
    """A close-up from (az, el), framed on a sphere (centre, radius) (m023 / m031 / m033)."""
    kit = K.NS["KIT"]
    fb = kit["frame_box"]
    c = Vector(centre)
    box = [c + Vector((dx, dy, dz)) * radius for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    kit["frame_box"] = lambda corners, a_, e_: fb(box, a_, e_)
    ground = bpy.data.objects.get("FB_Ground")
    if ground:
        ground.hide_render = el < 0 or not floor
    old = kit["CELL"]
    kit["CELL"] = cell
    try:
        return kit["render_group"](objs, path, az, el)
    finally:
        kit["CELL"] = old
        kit["frame_box"] = fb
        if ground:
            ground.hide_render = False


def render_cam(objs, path, loc, look, lens=18.0, cell=(560, 420)):
    """A render from a fixed camera (loc looking at look)."""
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
    try:
        return kit["render_group"](objs, path, 0, 10)
    finally:
        kit["frame_box"] = fb
        kit["CELL"] = old
        cam.data.lens = lens0


def render_close_ups(objs, tiles=()):
    """lash_cu (close-up A: P2's upper band and RF2's outer piece running in against it, from the front-right), tip_cu (close-up B: P2's tip),
    base_cu (close-up C: low under RR1 at L3, from the rear), banner_cu, seam_cu (a joint between two modules, from
    above the rear), thumb (the f34 at about 140 px)."""
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    h = objs[0]
    P2, L3 = TL["P2"], TL["L3"]
    out = {}
    out["lash_cu"] = render_close([h], f"{d}/lash_cu.png", 40, 12, _at(h, (P2["xc"] + 0.7, -0.9, 7.1)), 1.3)
    out["tip_cu"] = render_close([h], f"{d}/tip_cu.png", -30, 12, _at(h, (P2["xc"], 0.0, P2["sh"] + 0.2)), 1.1,
                                 floor=False)
    out["base_cu"] = render_cam([h], f"{d}/base_cu.png", _at(h, (L3["xc"] - 1.6, 3.4, 0.45)),
                                _at(h, (L3["xc"] + 0.2, 0.9, 2.2)), lens=16.0)
    out["banner_cu"] = render_close([h], f"{d}/banner_cu.png", -20, 10, _at(h, (3.32, -1.8, 5.2)), 3.4)
    joint = _at(h, (PITCH / 2, 0.0, 4.5))
    out["seam_cu"] = render_close([h] + list(tiles), f"{d}/seam_cu.png", 160, 35, joint, 2.6)
    out["seam_top_cu"] = render_close([h] + list(tiles), f"{d}/seam_top_cu.png", 0, 89.9,
                                      _at(h, (PITCH / 2, 0.0, 6.0)), 2.0, floor=False)
    kit = K.NS["KIT"]
    old = kit["CELL"]
    kit["CELL"] = (180, 150)
    try:
        orig, kit["render_group"] = _long_lens(kit)
        try:
            out["thumb"] = kit["render_group"]([h], f"{d}/thumb_sheet.png", *F34)
        finally:
            kit["render_group"] = orig
    finally:
        kit["CELL"] = old
    return out


def preview(names=("front_sheet", "side_sheet", "rear_sheet", "f34_sheet", "r34_sheet", "top_sheet")):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    nb = _nobanner(h) if any(n in NOBANNER for n in names) else None
    kit = K.NS["KIT"]
    orig, kit["render_group"] = _long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([nb] if k in NOBANNER else [h], *SHEET_VIEWS[k]) for k in names},
                       vfx=False)
    finally:
        kit["render_group"] = orig
        if nb:
            _remove([nb])


# ---- measuring renders against the sheet (spec 1.2 masks) ---------------------------------------------------------------
REF_CELLS = {"f34": (12, 146, 532, 512), "r34": (537, 146, 1014, 512), "front": (12, 585, 334, 800),
             "side": (338, 585, 496, 800), "rear": (500, 585, 764, 800), "top": (769, 585, 1013, 800)}


def _hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(axis=-1), rgb.min(axis=-1)
    d = mx - mn
    h = np.zeros_like(mx)
    nz = d > 1e-6
    rm = nz & (mx == r)
    gm = nz & (mx == g) & ~rm
    bm_ = nz & ~rm & ~gm
    h[rm] = (60 * ((g[rm] - b[rm]) / d[rm])) % 360
    h[gm] = 60 * ((b[gm] - r[gm]) / d[gm]) + 120
    h[bm_] = 60 * ((r[bm_] - g[bm_]) / d[bm_]) + 240
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def classes(rgb):
    """The spec 1.2 masks (W timber, R pale timber + rope, B banner red, S cool stone, G foliage, K dark)."""
    h, s, v = _hsv(rgb)
    r, b = rgb[..., 0] * 255, rgb[..., 2] * 255
    B = ((h < 14) | (h > 340)) & (s >= 0.55) & (v >= 0.35)
    G = (h >= 62) & (h <= 170) & (s >= 0.28) & (v >= 0.12)
    R = (h >= 30) & (h <= 50) & (s >= 0.25) & (s < 0.62) & (v >= 0.66)
    W = (((h >= 8) & (h <= 48)) | (h >= 345)) & (s >= 0.40) & (v >= 0.12) & ~B & ~R
    W |= ((h >= 8) & (h <= 48)) & (s >= 0.25) & (s < 0.40) & (v < 0.66)
    St = (s < 0.26) & (v >= 0.22) & (v <= 0.90) & (b >= r - 4) & ~G & ((s >= 0.06) | (v < 0.80))
    Kd = (v < 0.22) & ~W & ~B & ~G
    return {"W": W, "R": R, "B": B, "S": St, "G": G, "K": Kd, "obj": W | R | B | St | G | Kd}, v


def measure(path, box=None):
    """The spec's masks on an image (sheet cell or our render): object and timber + rope bboxes and W : H, class shares,
    wood lit / mid / shade shares, median / lit / shade hex per class."""
    px = K.NS["KIT"]["load_px"](path)[::-1, :, :3]          # top-down rows
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1]
    rgb = np.clip(px, 0, 1)
    cl, v = classes(rgb)
    hexs = lambda c: "#" + "".join(f"{int(round(x)):02X}" for x in c)
    obj = cl["obj"]
    ys, xs = np.nonzero(obj)
    wr = cl["W"] | cl["R"]
    ys2, xs2 = np.nonzero(wr)
    n = max(1, int(obj.sum()))
    out = {"bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
           "wh_obj": round((xs.max() - xs.min() + 1) / (ys.max() - ys.min() + 1), 3),
           "wh_timber": round((xs2.max() - xs2.min() + 1) / (ys2.max() - ys2.min() + 1), 3),
           "shares": {k: round(100 * float(cl[k].sum()) / n, 1) for k in "WRBSGK"}}
    vw = v[cl["W"]]
    out["wood_lms"] = [round(100 * float((vw >= 0.80).mean())), round(100 * float(((vw >= 0.5) & (vw < 0.8)).mean())),
                       round(100 * float((vw < 0.5).mean()))]
    for k in "WRBSG":
        c = rgb[cl[k]] * 255
        if len(c) < 20:
            continue
        lum = c.max(axis=1)
        lo, hi = np.percentile(lum, 25), np.percentile(lum, 75)
        out[k] = [hexs(np.median(c, axis=0)), hexs(np.median(c[lum >= hi], axis=0)), hexs(np.median(c[lum <= lo], axis=0))]
    g = cl["G"]
    if g.sum() > 20:
        hh, _, _ = _hsv(rgb)
        out["lime_of_G"] = round(100 * float((hh[g] < 80).mean()), 1)
    return out


def compare(names=("front", "rear", "side", "f34", "r34", "top")):
    """measure() on the sheet cells and on our *_sheet renders side by side."""
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    out = {}
    for k in names:
        p = f"{d}/{k}_sheet.png"
        if os.path.exists(p):
            out[k] = {"sheet": measure(M.ref(NUM), REF_CELLS[k]), "ours": measure(p)}
    return out
