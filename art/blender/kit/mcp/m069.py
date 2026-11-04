"""069 Palisade Wall (references/069.png, remade 2026-11-03) on the shared library (kit_parts / kit_build): one straight,
tileable 16-stud section of a log palisade with its dressing. See M069_spec.md.

    import importlib, kit_parts, kit_build, m069
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m069); m069.build()

Build frame (studs): front -Y (the banner face), +X right, ground z 0, the log axes on y 0, the module centred on x 0.
- Twelve upright timbers stand edge to edge (0.01 apart) from x -7.995 to +7.995: regular chamfered octagons (broad
  faces on the axes) with flat-cut feet on z 0, a darker foot band to 0.6 and a pale 8-facet pyramid tip about 0.72 of
  the diameter long. Two thick posts (Ø 1.80, tips 10.6 and 12.15), eight logs (Ø 1.25-1.55) and four narrow fillers.
- Each post carries two three-turn rope bands (lower 1.45-2.55; upper from 6.20 / 6.45). The neighbours stand 0.01 off
  the post, so each turn is a front run and a rear run round the post, both ends sunk 0.04 into the neighbour, square to
  its surface; the Post part keeps closed turns.
- Rails (0.90 tall, 0.75 deep, chamfered, pale cut ends) lie against the log faces: the front rail at z 5.30 from P1 to
  behind the banner's left edge, with a stub past P1; a short front beam at z 7.05 from P2's upper band onto L12; two
  rear rails at z 2.75 and 6.00 between the posts, the upper one with stubs past both posts. A rail end stops in the
  post's chamfer (0.02 in) or, where a band is in the way, against the band (stepped in to a sampled sink of 0.015).
- Rope lashings: open C-runs over each rail (top, front, bottom), both ends turned square into the log face behind.
- The banner (front only): a pale knobbed rod on two pegs (L8's chamfer and P2's broad face) at z 8.50, a red hem
  sleeve round the rod, a red swallowtail cloth with two cream edge stripes and a cream double-diamond emblem.
- Grey chock rocks: four along the front foot and three along the rear, each pushed against the wall until it meets it.
StockadeStraight is the tiling module: the wall without banner and rocks. Seam contract: the end logs L1 and L12 are the
same Ø 1.55 octagon, their outer broad faces flat at x -7.995 / +7.995; nothing else reaches past them. Both the hero and
the module tile at the 16-stud pitch (kit_verify seams on all four pairings).
Parts: StockadeLog, StockadePost, StockadeRail, StockadeBanner, StockadeRock. Stages 5-6: nothing (the sheet shows no
glow, light or effect).
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_build as B
import kit_mcp as K
import kit_parts as P

NUM, TITLE = 69, "Palisade Wall"
HERO, PLAIN = "Stockade", "StockadeStraight"
LOG_P, POST_P, RAIL_P, BANNER_P, ROCK_P = "StockadeLog", "StockadePost", "StockadeRail", "StockadeBanner", "StockadeRock"

TIMBER, TIMBER_END, TIMBER_DEEP = "m069_timber", "m069_timber_end", "m069_timber_deep"
ROPE, ROPE_DEEP = "m069_rope", "m069_rope_deep"
BANNER, BANNER_DEEP, CREAM = "m069_banner", "m069_banner_deep", "m069_cream"
ROCK = "m069_rock"

# key -> (hex, roughness, metal, emission, low specular). Stage 4: K.calibrate toward TARGETS (the sheet's rendered
# medians) on the studio dome, then scaled in linear light so the compare renders of the front and f34 cells match
# those medians (vertical faces take less light than the dome; spec "Stage 4").
PALETTE = {
    TIMBER: ("#8B551B", 0.85, 0.0, 0.0, True),
    TIMBER_END: ("#BF883E", 0.8, 0.0, 0.0, True),
    TIMBER_DEEP: ("#613810", 0.9, 0.0, 0.0, True),
    ROPE: ("#E8B470", 0.95, 0.0, 0.0, True),
    ROPE_DEEP: ("#AB874D", 0.95, 0.0, 0.0, True),
    BANNER: ("#F01E1C", 0.9, 0.0, 0.0, True),
    BANNER_DEEP: ("#86100F", 0.9, 0.0, 0.0, True),
    CREAM: ("#E6DCBC", 0.9, 0.0, 0.0, True),
    ROCK: ("#817E8C", 0.9, 0.0, 0.0, True),
}
TARGETS = {TIMBER: ((0x98, 0x55, 0x17), "brown"), TIMBER_END: ((0xF2, 0xA2, 0x41), "brown"),
           TIMBER_DEEP: ((0x6E, 0x3C, 0x10), "brown"), ROPE: ((0xFD, 0xD3, 0x7B), "all"),
           ROPE_DEEP: ((0xD8, 0xA2, 0x50), "all"), BANNER: ((0xFB, 0x21, 0x20), "vivid"),
           BANNER_DEEP: ((0xA8, 0x12, 0x10), "vivid"), CREAM: ((0xF6, 0xE6, 0xBD), "all"),
           ROCK: ((0x91, 0x89, 0x92), "stone")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)

# ---- timbers ------------------------------------------------------------------------------------------------------------
PITCH, SEAM, GAP = 16.0, 7.995, 0.01
T8 = math.tan(math.pi / 8)
CH_K = 1.0 - T8                 # chamfer leg / flat radius: a regular octagon (broad faces on the axes)
TIP_K, TIP_JIT, APEX_JIT = 0.90, 0.05, 0.04
FOOT = (0.6, 0.30)              # foot band top, t toward timber_deep
# name, diameter across flats, tip apex z, kind (front cell, -X -> +X; spec Brief)
TIMBERS = (("L1", 1.55, 8.65, "log"), ("P1", 1.80, 10.60, "post"), ("N1", 1.10, 8.00, "log"),
           ("L4", 1.40, 8.90, "log"), ("L5", 1.40, 9.00, "log"), ("N2", 0.80, 7.65, "log"),
           ("L7", 1.25, 9.65, "log"), ("L8", 1.40, 11.65, "log"), ("N3", 1.15, 9.95, "log"),
           ("P2", 1.80, 12.15, "post"), ("N4", 0.68, 9.30, "log"), ("L12", 1.55, 10.30, "log"))
END_LOGS = ("L1", "L12")


def _layout():
    out, x = {}, -SEAM
    for name, d, tip, kind in TIMBERS:
        h = d / 2
        r = P.rng("tip_" + name)
        jl = 0.0 if name in END_LOGS else r.uniform(-TIP_JIT, TIP_JIT)
        ap = (0.0, 0.0) if name in END_LOGS else (r.uniform(-APEX_JIT, APEX_JIT), r.uniform(-APEX_JIT, APEX_JIT))
        tl = TIP_K * d * (1.0 + jl)
        out[name] = dict(name=name, d=d, h=h, ch=CH_K * h, xc=x + h, y=0.0, tip=tip, sh=tip - tl, tl=tl, apex=ap,
                         kind=kind, x0=x, x1=x + d)
        x += d + GAP
    assert abs(x - GAP - SEAM) < 1e-6, x
    return out


TL = _layout()


def poly2(T, xc=None):
    """A timber's octagon in plan (x, y), counter-clockwise."""
    xc = T["xc"] if xc is None else xc
    return [Vector((xc + u, T["y"] + v)) for u, v in P.sec_rect(T["h"], T["h"], T["ch"])]


def surf_y(T, x):
    """|y| of the timber's surface at plan x (None off it)."""
    u = abs(x - T["xc"])
    if u > T["h"]:
        return None
    return min(T["h"], 2 * T["h"] - T["ch"] - u)


def cham_x(T, yi, s, sink=0.02):
    """x of a member end (inner face at |y| = yi) seated `sink` into the timber's chamfer on side s (+1 right)."""
    return T["xc"] + s * (2 * T["h"] - T["ch"] - yi - sink * math.sqrt(2.0))


def timber(a, T, xc=None, name=None):
    """One log or post: an 8-sided regular chamfered prism from a flat-cut foot on z 0 (a ring at the foot band) to the
    shoulder, then an 8-facet pyramid tip (pale cut wood). 46 tris."""
    xc = T["xc"] if xc is None else xc
    return P.post(a, (xc, T["y"]), 0.0, T["sh"], T["h"], TIMBER, ch=T["ch"], zs=(FOOT[0],),
                  band_keys=[P.mix(TIMBER, TIMBER_DEEP, FOOT[1]), None], tip=T["tl"], apex=T["apex"],
                  tip_key=TIMBER_END, name=name or T["name"], kind=T["kind"])


# ---- post bands ---------------------------------------------------------------------------------------------------------
RB, BAND_STEP, BAND_OFF = 0.19, 0.36, 0.17       # rope radius, turn spacing (turns touch), centreline off the faces
BAND_SIDES, BAND_PTS = 6, 8
TWIST = False                   # round turns with a spiral strand (twisted 5-sided rope read as flat slats)
BANDS = {"P1": (1.45, 6.20), "P2": (1.45, 6.45)}   # bottom of each band (z), three turns each
BAND_KEEP = RB - 0.02           # a band point stays where its centreline is this far clear of a neighbouring timber
BAND_END_SINK = 0.04            # a band run's end: this deep into the neighbour it meets


def _near2(poly, p):
    """(nearest boundary point, signed distance: negative inside) of a convex CCW polygon to the 2D point p."""
    best, bq, inside = 1e9, None, True
    n = len(poly)
    for i in range(n):
        a_, b_ = poly[i], poly[(i + 1) % n]
        e = b_ - a_
        if e.x * (p.y - a_.y) - e.y * (p.x - a_.x) < 0:
            inside = False
        t = max(0.0, min(1.0, (p - a_).dot(e) / e.length_squared))
        q = a_ + e * t
        d = (p - q).length
        if d < best:
            best, bq = d, q
    return bq, (-best if inside else best)


def _collinear(path, tol=math.radians(2.0)):
    """Drop interior points of an open path where it runs straight on."""
    out = list(path)
    i = 1
    while len(out) > 2 and i < len(out) - 1:
        a_, b_ = out[i] - out[i - 1], out[i + 1] - out[i]
        if a_.length > 1e-9 and b_.length > 1e-9 and a_.angle(b_) < tol:
            del out[i]
        else:
            i += 1
    return out


def band_paths(post, xc=None, alone=False):
    """[(band, turn, path, closed)]: each turn the mitred offset loop round the post's octagon; in the wall it is cut
    where it would pass through a neighbour (a front and a rear run), each run's ends carried on square to the
    neighbour's surface and BAND_END_SINK into it. alone (the Post part): closed loops."""
    T = TL[post]
    xc = T["xc"] if xc is None else xc
    neigh = [] if alone else [poly2(U) for U in TL.values() if U is not T and abs(U["xc"] - T["xc"]) < 3.0]
    out = []
    for bi, z0 in enumerate(BANDS[post]):
        for ti in range(3):
            z = z0 + RB + ti * BAND_STEP
            sec = [Vector((p.x, p.y, z)) for p in poly2(T, xc)]
            loop = P.hull_loop(sec, (xc, T["y"], z), (0, 0, 1), (1, 0, 0), BAND_OFF, BAND_PTS)
            if not neigh:
                out.append((bi, ti, loop, True))
                continue
            fine = []
            for i in range(len(loop)):
                fine += [loop[i], loop[i].lerp(loop[(i + 1) % len(loop)], 0.5)]
            n = len(fine)
            ok = [min(_near2(Pl, p.to_2d())[1] for Pl in neigh) >= BAND_KEEP for p in fine]
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
            for run in runs:
                pts = list(run)
                for end in (0, -1):
                    k = pts[end]
                    q, _ = min((_near2(Pl, k.to_2d()) for Pl in neigh), key=lambda r: r[1])
                    dv = (q - k.to_2d()).normalized()
                    e = Vector((q.x + dv.x * BAND_END_SINK, q.y + dv.y * BAND_END_SINK, z))
                    if end == 0:
                        pts.insert(0, e)
                    else:
                        pts.append(e)
                out.append((bi, ti, _collinear(pts), False))
    return out


def bands(a, post, xc=None, alone=False):
    out = []
    for i, (bi, ti, path, closed) in enumerate(band_paths(post, xc, alone)):
        out.append(P.rope(a, path, RB, ROPE, ROPE_DEEP, sides=BAND_SIDES, closed=closed, twist=TWIST, up=(0, 0, 1),
                          name=f"band_{post}_{bi}{ti}_{i}", kind="rope_band"))
    return out


# ---- rails, stubs ---------------------------------------------------------------------------------------------------------
RAIL_HZ, RAIL_D, RAIL_CH = 0.45, 0.75, 0.06
RAIL_IN = 0.703                 # inner face |y| of the spans (0.003 off the 1.40 logs)
STUB_IN = 0.778                 # inner face |y| of the stubs and the short beam (0.003 off the end logs)
SEAT_MAX = 0.015                # a member end against a band: the sampled sink (edges between samples go deeper)
# name: (z centre, side (-1 front, +1 rear), inner |y|, left end, right end); an end is ("cham"/"band", post), ("x", x)
# or ("len", length from the other end)
MEMBERS = {
    "RF": (5.30, -1, RAIL_IN, ("band", "P1"), ("x", 1.85)),
    "RF_w": (5.30, -1, STUB_IN, ("len", 0.60), ("band", "P1")),
    "RS": (7.05, -1, STUB_IN, ("band", "P2"), ("x", 7.05)),
    "RR1": (2.75, 1, RAIL_IN, ("band", "P1"), ("band", "P2")),
    "RR2": (6.00, 1, RAIL_IN, ("band", "P1"), ("band", "P2")),
    "RR2_w": (6.00, 1, STUB_IN, ("len", 0.60), ("band", "P1")),
    "RR2_e": (6.00, 1, STUB_IN, ("band", "P2"), ("len", 0.60)),
}


def _band_tree(pieces):
    """BVH and vertex coordinates of the band ropes (build frame)."""
    vs = [v for p in pieces for v in p.vs]
    return (K.bvh_of(vs) if vs else None), [v.co.copy() for v in vs]


def _overlap(x0, x1, yi, yo, z0, z1, tree, cos):
    """Deepest mutual sink between a member box (x0..x1, y yi..yo, z z0..z1) and the band ropes."""
    deep = 0.0
    lo = Vector((x0, min(yi, yo), z0))
    hi = Vector((x1, max(yi, yo), z1))
    for c in cos:
        if lo.x < c.x < hi.x and lo.y < c.y < hi.y and lo.z < c.z < hi.z:
            deep = max(deep, min(c.x - lo.x, hi.x - c.x, c.y - lo.y, hi.y - c.y, c.z - lo.z, hi.z - c.z))
    if tree is None:
        return deep
    for xe in (x0, x1):
        for i in range(5):
            for j in range(5):
                p = Vector((xe, lo.y + (hi.y - lo.y) * i / 4, z0 + (z1 - z0) * j / 4))
                loc, nrm, fi, d = tree.find_nearest(p)
                if loc is not None and (p - loc).dot(nrm) < 0 and P.parity_in(tree, p):
                    deep = max(deep, d)
    return deep


def member_x(name, tree=None, cos=()):
    """(x0, x1) of a member: a chamfer end, or the band seat (stepped from 0.8 out toward the chamfer until the next
    step would sink more than SEAT_MAX), an x, or a length."""
    zc, side, yi, e0, e1 = MEMBERS[name]
    z0, z1 = zc - RAIL_HZ, zc + RAIL_HZ
    ys = sorted((side * yi, side * (yi + RAIL_D)))

    def solve(spec, s):
        kind = spec[0]
        if kind == "x":
            return spec[1]
        T = TL[spec[1]]
        xc = cham_x(T, yi, s)
        if kind == "cham" or tree is None:
            return xc
        x = xc + s * 0.8
        while (x - xc) * s > 0:
            nx = x - s * 0.004
            lo, hi = sorted((nx, nx + s * 0.6))          # the member's last 0.6 at this end
            if _overlap(lo, hi, ys[0], ys[1], z0, z1, tree, cos) > SEAT_MAX:
                return x
            x = nx
        return xc
    if e0[0] == "len":
        x1 = solve(e1, -1)
        return x1 - e0[1], x1
    x0 = solve(e0, 1)
    if e1[0] == "len":
        return x0, x0 + e1[1]
    return x0, solve(e1, -1)


def member(a, name, x0, x1, tag=""):
    zc, side, yi, *_ = MEMBERS[name]
    yc = side * (yi + RAIL_D / 2)
    P.GEO.setdefault("members", {})[tag + name] = [round(x0, 3), round(x1, 3)]
    return P.plank(a, (x0, yc, zc), (x1, yc, zc), RAIL_D, 2 * RAIL_HZ, TIMBER, ch=RAIL_CH,
                   cap_keys=(TIMBER_END, TIMBER_END), name="rail_" + name, kind="rail")


# ---- lashings ---------------------------------------------------------------------------------------------------------------
RL, LASH_STEP, LASH_SIDES = 0.15, 0.28, 6
LASH_CUT = 0.09                 # the C-run's top outer corner cut at 45 deg (a rounder coil where it shows)
LASH_SINK = 0.04
# (member, centre x, turns)
LASHINGS = (("RF", -4.10, 3), ("RF", -1.24, 3), ("RS", 6.44, 2), ("RR1", -3.00, 2), ("RR1", 2.55, 2),
            ("RR2", -3.00, 2), ("RR2", 2.55, 2))


def lashing(a, mem, xc, turns, tag=""):
    """Open C-runs over a rail at x (top, front, bottom), centreline off = RL - 0.02 outside its faces; each end turned
    square into the nearest timber's surface behind the rail, LASH_SINK deep."""
    zc, side, yi, *_ = MEMBERS[mem]
    yo = yi + RAIL_D
    off = RL - 0.02
    z0, z1 = zc - RAIL_HZ - off, zc + RAIL_HZ + off
    out = []
    for t in range(turns):
        x = xc + (t - (turns - 1) / 2) * LASH_STEP
        k = Vector((x, side * (yi + 0.06)))
        q, _ = min((_near2(poly2(T), k) for T in TL.values() if abs(T["xc"] - x) < 1.5), key=lambda r: r[1])
        dv = (q - k).normalized()
        e = q + dv * LASH_SINK
        f = Vector((x, side * (yo + off)))
        fc = Vector((x, side * (yo + off - LASH_CUT)))
        outer = [Vector((fc.x, fc.y, z1)), Vector((f.x, f.y, z1 - LASH_CUT)), Vector((f.x, f.y, z0))]
        if (k - q).length < 0.08:            # the timber is right behind the rail: one straight run in
            path = [Vector((e.x, e.y, z1))] + outer + [Vector((e.x, e.y, z0))]
        else:
            path = [Vector((e.x, e.y, z1)), Vector((k.x, k.y, z1))] + outer + [Vector((k.x, k.y, z0)),
                                                                               Vector((e.x, e.y, z0))]
        out.append(P.rope(a, path, RL, ROPE, ROPE_DEEP, sides=LASH_SIDES, twist=TWIST, up=(1, 0, 0),
                          name=f"lash_{tag}{mem}_{xc:+.2f}_{t}", kind="rope_lash"))
    return out


def wall(a):
    """Timbers, bands, members and lashings. Returns the band pieces."""
    for T in TL.values():
        timber(a, T)
    bp = []
    for post in BANDS:
        bp += bands(a, post)
    tree, cos = _band_tree(bp)
    for name in MEMBERS:
        x0, x1 = member_x(name, tree, cos)
        member(a, name, x0, x1)
    for mem, x, n in LASHINGS:
        lashing(a, mem, x, n)
    return bp


# ---- banner ---------------------------------------------------------------------------------------------------------------
ROD_Z, ROD_Y, ROD_R = 8.50, -1.62, 0.21
ROD_X = (1.25, 4.85)
KNOB_R = 0.30
CLOTH_X, CLOTH_T = (1.75, 4.05), 0.08
SLEEVE_IN, SLEEVE_T = ROD_R + 0.006, 0.07
TIPS_Z, NOTCH_Z = 1.70, 2.70
PEG_W, PEG_SINK = 0.24, 0.04
PEGS = (("L8", 1.57), ("P2", 4.70))
EMB_Z = 5.40
EMB_RINGS = ((0.70, 1.50, 0.15), (0.36, 0.78, 0.12))      # half width, half height, line width (along x)
STRIPE_IN, STRIPE_W, STRIPE_Z0 = 0.12, 0.09, 1.95
EMB_T = 0.015


def knob(a, c, r, name):
    """A low-poly ball on the rod's axis (X): two poles and three rings of six, as a hull."""
    c = Vector(c)
    pts = [c + Vector((r, 0, 0)), c - Vector((r, 0, 0))]
    for k, xf in enumerate((-0.6, 0.0, 0.6)):
        rr = r * math.sqrt(1 - xf * xf)
        for j in range(6):
            th = 2 * math.pi * (j + 0.5 * k) / 6
            pts.append(c + Vector((xf * r, rr * math.cos(th), rr * math.sin(th))))
    return P.hull(a, pts, TIMBER_END, name=name, kind="knob", amp=0.03)


def _diamond_ring(a, cx, cz, hw, hh, line, y0, y1, name):
    """A diamond outline slab (outer half sizes hw x hh, `line` wide measured along x) between y0 and y1."""
    k = line / hw
    outer = [(cx, cz + hh), (cx + hw, cz), (cx, cz - hh), (cx - hw, cz)]
    inner = [(cx, cz + hh * (1 - k)), (cx + hw * (1 - k), cz), (cx, cz - hh * (1 - k)), (cx - hw * (1 - k), cz)]
    pts = [Vector((x, y0, z)) for x, z in outer + inner] + [Vector((x, y1, z)) for x, z in outer + inner]
    faces = []
    for i in range(4):
        i1 = (i + 1) % 4
        faces += [[i, i1, 4 + i1, 4 + i], [12 + i, 12 + i1, 8 + i1, 8 + i], [i1, i, 8 + i, 8 + i1],
                  [4 + i, 4 + i1, 12 + i1, 12 + i]]
    return P.shell(a, pts, faces, CREAM, name=name, kind="emblem", amp=0.02)


def banner(a, pegs=True):
    """Rod with knobs (pegs into L8 / P2), red hem sleeve round the rod, swallowtail cloth, cream stripes and the
    double-diamond emblem on the front face."""
    if pegs:
        for tname, x in PEGS:
            T = TL[tname]
            yb = []
            for xx in (x - PEG_W / 2, x + PEG_W / 2):
                yb.append(-(surf_y(T, xx) - PEG_SINK))
            ztop = ROD_Z - ROD_R + 0.02
            zb = ztop - PEG_W
            rings = [[(x - PEG_W / 2, yb[0], zb), (x + PEG_W / 2, yb[1], zb), (x + PEG_W / 2, yb[1], ztop),
                      (x - PEG_W / 2, yb[0], ztop)],
                     [(x - PEG_W / 2, ROD_Y, zb), (x + PEG_W / 2, ROD_Y, zb), (x + PEG_W / 2, ROD_Y, ztop),
                      (x - PEG_W / 2, ROD_Y, ztop)]]
            P.prism(a, rings, TIMBER, cap_keys=(None, TIMBER_END), name=f"peg_{tname}", kind="peg")
    P.log(a, (ROD_X[0], ROD_Y, ROD_Z), (ROD_X[1], ROD_Y, ROD_Z), ROD_R, TIMBER_END, sides=8, end_key=TIMBER_END,
          name="rod", kind="rod")
    for s, xe in ((-1, ROD_X[0]), (1, ROD_X[1])):
        knob(a, (xe + s * (KNOB_R - 0.035), ROD_Y, ROD_Z), KNOB_R, f"knob{s:+d}")
    P.sleeve(a, (CLOTH_X[0] - 0.04, ROD_Y, ROD_Z), (CLOTH_X[1] + 0.04, ROD_Y, ROD_Z), SLEEVE_IN, SLEEVE_IN + SLEEVE_T, BANNER_DEEP,
             sides=8, name="hem", kind="hem", amp=0.02)
    top = ROD_Z - SLEEVE_IN - 0.015
    x0, x1 = CLOTH_X
    xm = (x0 + x1) / 2
    outline = [(x0, top), (x1, top), (x1, TIPS_Z), (xm, NOTCH_Z), (x0, TIPS_Z)]
    yf, yb = ROD_Y - CLOTH_T / 2, ROD_Y + CLOTH_T / 2
    cloth = P.ext(a, outline, yf, yb, BANNER, to3=lambda u, v, w: Vector((u, w, v)), name="cloth", kind="banner",
                  amp=0.02)
    P.texture(a, cloth.vs, 0.02, P.seed("cloth"), scale=0.4)
    e0, e1 = yf + 0.005, yf - EMB_T
    for i, (hw, hh, line) in enumerate(EMB_RINGS):
        _diamond_ring(a, xm, EMB_Z, hw, hh, line, e0, e1, f"emblem{i}")
    zt = ROD_Z - SLEEVE_IN - SLEEVE_T - 0.06
    for s, xe in ((1, x0), (-1, x1)):
        xa, xb = sorted((xe + s * STRIPE_IN, xe + s * (STRIPE_IN + STRIPE_W)))
        P.ext(a, [(xa, STRIPE_Z0), (xb, STRIPE_Z0), (xb, zt), (xa, zt)], e1, e0, CREAM,
              to3=lambda u, v, w: Vector((u, w, v)), name=f"stripe{s:+d}", kind="emblem", amp=0.02)


# ---- rocks ------------------------------------------------------------------------------------------------------------------
# name, centre x, side, (width, depth, height), seed (front cell / rear cell, spec Brief)
ROCKS = (("F1", -6.75, -1, (1.95, 1.55, 1.50), 11), ("F2", -3.75, -1, (1.55, 1.25, 0.97), 13),
         ("F3", -0.10, -1, (1.55, 1.30, 1.30), 17), ("F4", 6.55, -1, (2.15, 1.65, 1.62), 19),
         ("B1", 6.45, 1, (1.75, 1.40, 1.55), 23), ("B2", -2.05, 1, (1.55, 1.25, 1.15), 29),
         ("B3", -6.70, 1, (2.10, 1.60, 1.55), 31))
ROCK_SCALE = 1.08               # the hull sits inside its jittered rings: this brings it to the measured size


def rock_points(size, seed_):
    """A squat faceted boulder: a 6-point foot ring on z 0, a 6-point waist, a 5-point shoulder and a 4-point broken
    top (a flat-ish top facet), all jittered; flattened, not an egg."""
    r = P.rng(f"rock{seed_}")
    w, d, h = size[0] * ROCK_SCALE, size[1] * ROCK_SCALE, size[2] * 1.03
    pts = []
    for zf, rf, n, rot in ((0.0, 0.94, 6, 0.0), (0.45, 1.0, 6, 0.5), (0.80, 0.80, 5, 0.2), (1.0, 0.52, 4, 0.9)):
        off = rot + r.uniform(-0.15, 0.15)
        for k in range(n):
            th = off + 2 * math.pi * k / n + r.uniform(-0.16, 0.16)
            rr = rf * r.uniform(0.90, 1.0)
            z = 0.0 if zf == 0.0 else h * zf * r.uniform(0.96, 1.0)
            pts.append(Vector((w / 2 * rr * math.cos(th), d / 2 * rr * math.sin(th), z)))
    return pts


def _hull_tris(pts):
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    cos = [v.co.copy() for v in bm.verts]
    idx = {v: i for i, v in enumerate(bm.verts)}
    tris = [[idx[v] for v in f.verts] for f in bm.faces]
    bm.free()
    return cos, tris


def rock_place(pts, cx, side, tree):
    """Slide the rock from 2.5 out toward the wall until it meets it (bisection to 0.002); returns its y."""
    cos, tris = _hull_tris(pts)

    def hits(y):
        t = BVHTree.FromPolygons([c + Vector((cx, y, 0)) for c in cos], tris)
        return bool(t.overlap(tree))
    far = side * 3.5
    near = 0.0
    for _ in range(30):
        mid = (far + near) / 2
        if hits(mid):
            near = mid
        else:
            far = mid
    return far + side * 0.002


def rock(a, name, cx, side, size, seed_, tree=None):
    pts = rock_points(size, seed_)
    y = rock_place(pts, cx, side, tree) if tree is not None else 0.0
    p = P.hull(a, [q + Vector((cx, y, 0)) for q in pts], ROCK, name=name, kind="rock", amp=0.04)
    P.texture(a, p.vs, 0.05, seed_, scale=0.9)
    P.GEO.setdefault("rocks", {})[name] = [round(cx, 3), round(y, 3)]
    return p


def wall_tree(a):
    """A BVH of everything built so far (the wall) in the build frame."""
    a.bm.verts.ensure_lookup_table()
    return BVHTree.FromBMesh(a.bm)


# ---- assemblies ---------------------------------------------------------------------------------------------------------------
def hero_all(a, with_banner=True):
    wall(a)
    if with_banner:
        banner(a)
    tree = wall_tree(a)
    for name, cx, side, size, sd in ROCKS:
        rock(a, f"rock_{name}", cx, side, size, sd, tree)


def plain(a):
    wall(a)


def log_part(a):
    """One palisade log (L4's Ø 1.40, tip 9.0) with a three-turn band (the exploded view's first log)."""
    T = dict(TL["L4"], name="log", tip=9.0, apex=(0.0, 0.0), xc=0.0)
    T["sh"] = T["tip"] - T["tl"]
    timber(a, T, 0.0, "log")
    for ti in range(3):
        z = 1.80 + RB + ti * BAND_STEP
        sec = [Vector((p.x, p.y, z)) for p in poly2(T, 0.0)]
        loop = P.hull_loop(sec, (0, 0, z), (0, 0, 1), (1, 0, 0), BAND_OFF, BAND_PTS)
        P.rope(a, loop, RB, ROPE, ROPE_DEEP, sides=BAND_SIDES, closed=True, twist=TWIST, up=(0, 0, 1),
               name=f"band_{ti}", kind="rope_band")


def post_part(a):
    timber(a, TL["P2"], 0.0, "post")
    bands(a, "P2", 0.0, alone=True)


RAIL_PART_L = 8.0


def rail_part(a):
    """'Horizontal Beam': one rail 8.0 long with a three-turn closed lashing near each end (no log behind)."""
    zc, hz, d = RAIL_HZ + 0.0, RAIL_HZ, RAIL_D
    P.plank(a, (-RAIL_PART_L / 2, 0, zc), (RAIL_PART_L / 2, 0, zc), d, 2 * hz, TIMBER, ch=RAIL_CH,
            cap_keys=(TIMBER_END, TIMBER_END), name="rail", kind="rail")
    off = RL - 0.02
    for s in (-1, 1):
        for t in range(3):
            x = s * (RAIL_PART_L / 2 - 0.75 - t * LASH_STEP)
            c4 = [Vector((x, -d / 2 - off, zc - hz - off)), Vector((x, d / 2 + off, zc - hz - off)),
                  Vector((x, d / 2 + off, zc + hz + off)), Vector((x, -d / 2 - off, zc + hz + off))]
            loop = []
            for k in range(4):
                p0, p1 = c4[k], c4[(k + 1) % 4]
                dv = (p1 - p0).normalized()
                loop += [p0 + dv * 0.10, p1 - dv * 0.10]
            P.rope(a, loop, RL, ROPE, ROPE_DEEP, sides=LASH_SIDES, closed=True, twist=TWIST, up=(1, 0, 0),
                   name=f"lash{s:+d}_{t}", kind="rope_lash")


def banner_part(a):
    banner(a, pegs=False)


def rock_part(a):
    name, cx, side, size, sd = ROCKS[3]
    rock(a, "rock", 0.0, side, size, sd)


PARTS = ((PLAIN, plain), (LOG_P, log_part), (POST_P, post_part), (RAIL_P, rail_part), (BANNER_P, banner_part),
         (ROCK_P, rock_part))
NOTES = {
    HERO: "Palisade wall (remade sheet): one straight 16-stud tile. Twelve chamfered octagonal timbers (two posts Ø 1.80 "
          "to 10.6 / 12.15 with two three-turn rope bands each, eight logs, four narrow fillers) with pale pointed tips "
          "and flat-cut feet; a front rail with a stub, a short front beam at the right post's upper band, two rear "
          "rails (the upper with stubs past both posts), rope lashings; a red swallowtail banner with a cream double "
          "diamond on a knobbed rod; seven grey chock rocks. Tiles at 16 studs along X (seams at x +-8; the end logs "
          "meet face to face).",
    PLAIN: "Tiling module: the wall without banner and rocks. Place at 16-stud steps along X, before or after the hero "
           "or another module; the end logs meet face to face at the seams (x +-8).",
    LOG_P: "Palisade Log: one Ø 1.40 chamfered log, tip 9.0, flat-cut foot, a three-turn rope band",
    POST_P: "Post: the Ø 1.80 post (tip 12.15) with its two three-turn rope bands",
    RAIL_P: "Horizontal Beam: an 8.0 rail (0.90 x 0.75, chamfered, pale ends) with a three-turn lashing near each end",
    BANNER_P: "Banner: knobbed rod, hem sleeve, red swallowtail cloth with cream stripes and a cream double diamond",
    ROCK_P: "Stone: one squat faceted chock rock (2.15 x 1.65 x 1.62)",
}
COLLISION = {HERO: "precise", PLAIN: "box", LOG_P: "box", POST_P: "box", RAIL_P: "box", BANNER_P: "none",
             ROCK_P: "hull"}
BUDGETS = {HERO: 4000, PLAIN: 4000}
TARGET_SIZE = ((2 * SEAM, 0.01), (5.0, 1.0), (12.15, 0.01))
VIEWS = {"f34_sheet": (-20, 12), "r34_sheet": (-20, 12, "nobanner"), "front_sheet": (0, 0), "side_sheet": (90, 0),
         "rear_sheet": (180, 0), "top_sheet": (0, 89.9)}
VARIANTS = {"nobanner": lambda a: hero_all(a, False)}
EXPLODED = {LOG_P: (-9.0, 2.0, 0.0), POST_P: (8.0, 2.0, 0.0), RAIL_P: (-1.0, 2.0, 5.0), BANNER_P: (12.5, 0.0, 2.0),
            ROCK_P: (-4.0, -2.5, 0.0)}
CLOSE = {"lash_cu": dict(at=(-4.1, -1.3, 5.6), r=1.6, az=-35, el=14),
         "band_cu": dict(at=(4.85, -1.0, 7.0), r=2.0, az=25, el=12),
         "banner_cu": dict(at=(2.9, -1.6, 7.6), r=2.2, az=-20, el=10)}
VERIFY = dict(cls="asset", classes={HERO: "asset", PLAIN: "asset"},
              seams={"pitch": (PITCH, 0.0, 0.0), "obj": PLAIN, "with": HERO})
# compare cells: sheet pixel boxes (spec Brief) and cameras
COMPARE = {"f34": {"box": (12, 146, 512, 512), "view": VIEWS["f34_sheet"][:2]},
           "front": {"box": (12, 585, 312, 800), "view": (0, 0)},
           "rear": {"box": (508, 585, 766, 800), "view": (180, 0)},
           "side": {"box": (330, 585, 420, 800), "view": (90, 0)},
           "top": {"box": (770, 585, 1012, 800), "view": (0, 89.9)}}


def after(objs):
    """The tiling module is built with the parts but is a variant; both carry the tile contract."""
    o = objs[PLAIN]
    K.tag(o, MODEL.sheet, TITLE, "variant", COLLISION[PLAIN], BUDGETS[PLAIN], NOTES[PLAIN])
    for nm in (HERO, PLAIN):
        objs[nm]["m069_pitch"] = PITCH
        objs[nm]["m069_seams"] = [-PITCH / 2, PITCH / 2]


def build(render=True, close=False, spin=False):
    return MODEL.run(hero=(HERO, hero_all), parts=PARTS, notes=NOTES, collision=COLLISION, budgets=BUDGETS,
                     target_size=TARGET_SIZE, views=VIEWS, variants=VARIANTS, exploded=EXPLODED,
                     scale=(-9.8, -2.0, 0.0), close=CLOSE if close else None, verify=VERIFY, render=render,
                     after=after, spin=spin)


def preview(names=("f34_sheet", "front_sheet", "rear_sheet")):
    return MODEL.preview(HERO, VIEWS, names, variants=VARIANTS)


def compare(cells=None, out_dir=None, height=360):
    import importlib
    import compare as C
    importlib.reload(C)
    return C.compare(NUM, {k: COMPARE[k] for k in (cells or COMPARE)}, out_dir=out_dir, height=height)


TILE_CELL = {"box": (705, 1080, 1010, 1260), "view": (0, 0)}


def tile_compare(out_dir=None, height=300):
    """The tiling cell: the hero and a linked copy at +PITCH, against the sheet's cell."""
    h = bpy.data.objects[HERO]
    c = B.linked(h, MODEL.PFX + "tile", h.matrix_world @ Matrix.Translation((PITCH, 0, 0)))
    try:
        import importlib
        import compare as C
        importlib.reload(C)
        return C.compare(NUM, {"tile": TILE_CELL}, objs=[h, c], out_dir=out_dir, height=height)
    finally:
        B.remove([c])
