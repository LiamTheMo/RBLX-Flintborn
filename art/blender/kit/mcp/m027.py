"""027 Reed Patch (references/027.png): a small clump of reeds growing from a low lumpy mud mound. Three fat tan
8-sided faceted cattail heads with dark nubs on straight 6-sided green stalks splay outward above a flattened fan of
nine broad keeled lance leaves; five faceted grey rocks sit half sunk round the mound's rim.

    import importlib, kit_models, m027; importlib.reload(kit_models); importlib.reload(m027); m027.build()

Parts as on the sheet's Exploded Construction, each built by its own function, all in one build frame (studs; front
-Y, +X right, ground z = 0, origin = the mound centre on the ground). R07 owns ReedPatch*, V04 Cattail*, so the names
are ReedClump* (M027_spec.md section 8, decision 11):
- ReedClumpSeedHead (seed_head_part): H2's head, an 8-sided faceted capsule with chamfered ends, a dark nub on top and
  the short bottom peg of the Seed Head Connection close-up.
- ReedClumpStalk (stalk_part): a straight 6-sided prism, flat ends.
- ReedClumpLeafBlade (leaf_part): a broad keeled lance (thick edges, a midrib fold, an oblique knife tip), arched.
- ReedClumpMudBase (mud_base_part): the low oval lumpy mound with a shallow dish, flat bottom.
- ReedClumpRock (rock_part): a faceted boulder with a flat bottom.

The hero (ReedClumpNode) is built from the same builders: mound + 5 rocks + 3 stalks + 3 heads + 9 leaves, united
one shell at a time (guarded exact booleans, merge 0), floor-cut at the ground, the sliver cleanup, bowties split.
Colour (stage 4) is painted by position fields inside the builders before the union: leaves base -> tip along each
leaf, heads bottom -> top along each head, the mound darker in the dish and creases. Never by facing.
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M
import m004
import m011
import m012

NUM, TITLE, SHEET = 27, "Reed Patch", "M027"
HERO = "ReedClumpNode"
PFX = "_m027_"

LEAF, LEAF_BASE, LEAF_TIP = "m027_leaf", "m027_leaf_base", "m027_leaf_tip"
STALK = "m027_stalk"
HEAD, HEAD_LIGHT, NUB = "m027_head", "m027_head_light", "m027_nub"
MUD, MUD_DARK = "m027_mud", "m027_mud_dark"
ROCK, ROCK_DARK = "m027_rock", "m027_rock_dark"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
POLISH_LIM = 5.0

# ---- palette (stage 4) -----------------------------------------------------------------------------------------------
# key -> (hex, roughness, low_spec). The comment is the calibration target (the sheet's rendered median of an
# unshadowed region, spec 5.4). Stage 4 writes the calibrated hexes here.
# Pass 1 (K.calibrate on the dome, 6 iterations, 2026-10-28): every key's dome median within 6 of its target
# (rendered in the comment after the target): leaf #68802D, leaf_base #587129, leaf_tip #899D41, stalk #64782F,
# head #A97F4F, head_light #B28A5B, nub #503C23, mud #685441, mud_dark #544535, rock #6F6B6A, rock_dark #575557.
# Pass 2 (hero f34_sheet against the f34 cell): green median #617325 against #6A8229 (lit #8DA937 / #9FB43D; the
# h .6-.7 bands darkest where the sheet's are lightest: the studio key comes from front-left-above, almost along LA's
# axis, so the outer leaves' upper halves are grazing-lit), heads #C18D56 against #C99057, mud #715841 against
# #846549 (also too much mud_dark mixing, cut back below), rock #7B736C against #83756F. Each family scaled in linear
# light: leaf x(1.2, 1.3, 1.2), leaf_base x(1.15, 1.22, 1.1), leaf_tip x(1.35, 1.42, 1.25), stalk x(1.1, 1.15, 1.1),
# heads x(1.08, 1.06, 1.05) / x(1.1, 1.08, 1.06), mud keys x(1.2, 1.17, 1.13), rocks x(1.08, 1.02, 1.0).
# Pass 2b: f34 / front mud #7A5E43 / #765B41 against #846549 / #86684B: mud keys x(1.16, 1.14, 1.1) more.
# Pass 2c: stalk part #728A2D against #7C9230, hero H3 stalk box #4E601C against #5E7A2A: stalk x(1.15, 1.12, 1.1).
PALETTE = {
    LEAF: ("#719032", 0.8, True),          # #7F9A2E exploded leaf medians; dome (124,151,46)
    LEAF_BASE: ("#5E7C2B", 0.8, True),     # #6A862A leaf base fifths; dome (103,132,41)
    # round 2 (verifier blocker 2a): re-calibrated on the unshadowed parts shot: tip fifth #C2E34D against the
    # sheet's #A5BA3F -> x(0.70, 0.64, 0.67) linear (#9DB849 -> #85963C, back near pass 1's dome value #899D41)
    LEAF_TIP: ("#85963C", 0.8, True),      # #ACC144 leaf tip fifths; dome (168,189,68)
    STALK: ("#708734", 0.8, True),         # #7A9030 exploded stalks / cu1; dome (119,141,48)
    HEAD: ("#AF8251", 0.85, False),        # #D69A5D exploded heads / cu1; dome (214,155,93)
    HEAD_LIGHT: ("#BA8F5E", 0.85, False),  # #E2A86A body upper fifths; dome (225,168,106)
    NUB: ("#503C23", 0.9, False),          # #644A2E nubs; dome (101,76,50)
    # round 2: mud keys x 0.93 linear (#796148 / #63503C before): the sloped side ring catches more key; f34 mud
    # #896848 against #846549 and the parts-shot mud #927151 against #806247
    MUD: ("#755E45", 0.95, False),         # #826347 exploded mud; dome (127,98,72)
    MUD_DARK: ("#604D3A", 0.95, False),    # #66503B shade quartiles / dish; dome (102,80,59)
    ROCK: ("#736C6A", 0.85, False),        # #8C827B exploded rock; dome (139,130,123)
    ROCK_DARK: ("#5A5657", 0.85, False),   # #6E6865 hero RK1; dome (110,104,101)
}
TARGETS = {LEAF: ((0x7F, 0x9A, 0x2E), "green"), LEAF_BASE: ((0x6A, 0x86, 0x2A), "green"),
           LEAF_TIP: ((0xAC, 0xC1, 0x44), "green"), STALK: ((0x7A, 0x90, 0x30), "green"),
           HEAD: ((0xD6, 0x9A, 0x5D), "vivid"), HEAD_LIGHT: ((0xE2, 0xA8, 0x6A), "vivid"),
           NUB: ((0x64, 0x4A, 0x2E), "brown"), MUD: ((0x82, 0x63, 0x47), "brown"),
           MUD_DARK: ((0x66, 0x50, 0x3B), "brown"), ROCK: ((0x8C, 0x82, 0x7B), "stone"),
           ROCK_DARK: ((0x6E, 0x68, 0x65), "stone")}
MUD_SPEC = 0.25        # Specular IOR Level on the mud keys (matte damp soil; flintkit's default is 0.5)


def palette():
    for k, (hx, rough, low) in PALETTE.items():
        K.set_colour(k, hx, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hx, rough=rough, low_spec=low)
    _restyle()


def _restyle():
    """Leaf and stalk keys (mix keys too) at the foliage specular; mud keys at MUD_SPEC."""
    for m in bpy.data.materials:
        if not m.name.startswith("FB_m027_") or not m.node_tree:
            continue
        b = m.node_tree.nodes.get("Principled BSDF")
        if not b or "Specular IOR Level" not in b.inputs:
            continue
        if m.name.startswith(("FB_m027_leaf", "FB_m027_stalk")):
            b.inputs["Specular IOR Level"].default_value = K.FOLIAGE_SPEC
        elif m.name.startswith("FB_m027_mud"):
            b.inputs["Specular IOR Level"].default_value = MUD_SPEC


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome. Returns {key: (hex, rendered)}."""
    keys = keys or list(TARGETS)
    set0 = K.set_colour

    def set_colour(key, hexcol, **kw):
        set0(key, hexcol, **kw)
        _restyle()
    K.set_colour = set_colour
    try:
        for k in keys:
            K.fk().material(k)
        _restyle()
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        K.set_colour = set0
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


# ---- small helpers ---------------------------------------------------------------------------------------------------
STEPS = 4      # 25 / 50 / 75 % in-between keys


def _q(t):
    return round(min(1.0, max(0.0, t)) * STEPS) / STEPS


def _faces(verts):
    return K.faces_of([v for v in verts if v.is_valid])


def _tri(bm, faces):
    bmesh.ops.triangulate(bm, faces=[f for f in faces if f.is_valid and len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")


def _frame(axis):
    d = Vector(axis).normalized()
    u = d.orthogonal().normalized()
    v = d.cross(u).normalized()
    return u, v, d


def _mottle(a, faces, amp, scale, seed, level=1.0, jitter=0.0):
    """Broad Tint patches about 1/scale studs across, times a per-piece level (never per-face confetti)."""
    rng = random.Random(seed)
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    for f in faces:
        k = level * (1.0 + amp * 1.6 * noise.noise(f.calc_center_median() * scale + off) +
                     (rng.uniform(-jitter, jitter) if jitter else 0.0))
        for lo in f.loops:
            lo[a.tint_layer] = (k, k, k, 1.0)


def _loft(a, rings, mat, cap0=True, cap1=True, apex1=None):
    """Quads between consecutive rings (equal counts, same rotational order), flat caps (triangulated) or an apex
    point at the far end. Returns (verts, [faces per band], cap faces)."""
    bm = a.bm
    R = [[bm.verts.new(p) for p in ring] for ring in rings]
    n = len(R[0])
    bands = []
    for r0, r1 in zip(R, R[1:]):
        bands.append([bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k])) for k in range(n)])
    caps = []
    if cap0:
        f = bm.faces.new(list(reversed(R[0])))
        caps += bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="BEAUTY")["faces"]
    vs = [v for r in R for v in r]
    if apex1 is not None:
        t = bm.verts.new(apex1)
        bands.append([bm.faces.new((R[-1][k], R[-1][(k + 1) % n], t)) for k in range(n)])
        vs.append(t)
    elif cap1:
        f = bm.faces.new(R[-1])
        caps += bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="BEAUTY")["faces"]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, mat, tint=1.0)
    return vs, bands, caps


# ---- seed head -------------------------------------------------------------------------------------------------------
# rings (t along the body, radius fraction of d/2): bottom chamfer, straight body with a jittered mid ring, top chamfer
HEAD_PROF = ((0.0, 0.62), (0.13, 1.0), (0.5, 1.03), (0.87, 1.0), (1.0, 0.60))
HEAD_SIDES = 8
HEAD_TWIST = 6.0       # degrees of ring twist (seeded) so the facets break
HEAD_JIT = 0.04        # radial jitter on the inner rings
NUB_TAPER = 0.9
PEG = (0.07, 0.12)     # the part's bottom peg: radius, length


def seed_head(a, base, axis, d, body_l, nub_d, nub_l, seed, peg=False):
    """One cattail head from its bottom centre along axis: an 8-sided faceted capsule (HEAD_PROF), a flat top
    annulus round the nub, the nub (8 sides, tapered, flat cap), optionally the peg. Returns (verts, {face: part})
    with part in ("body", t) / "nub"."""
    rng = random.Random(seed)
    u, v, w = _frame(axis)
    B = Vector(base)
    R = d / 2
    ph = rng.uniform(0, 2 * math.pi)
    rings, tags = [], []

    def ring(z, r, twist=0.0, jit=0.0):
        pts = []
        for k in range(HEAD_SIDES):
            th = ph + twist + 2 * math.pi * k / HEAD_SIDES
            rr = r * (1 + rng.uniform(-jit, jit))
            pts.append(B + w * z + (u * math.cos(th) + v * math.sin(th)) * rr)
        return pts
    if peg:
        rings.append(ring(-PEG[1], PEG[0]))
        tags.append("nub")
        rings.append(ring(0.0, PEG[0]))
        tags.append(("body", 0.0))
    for i, (t, rf) in enumerate(HEAD_PROF):
        inner = 0 < i < len(HEAD_PROF) - 1
        tw = math.radians(rng.uniform(-HEAD_TWIST, HEAD_TWIST)) if inner else 0.0
        rings.append(ring(t * body_l, rf * R, tw, HEAD_JIT if inner else 0.01))
        tags.append(("body", t))
    rings.append(ring(body_l, nub_d / 2))
    tags.append("top")
    rings.append(ring(body_l + nub_l, nub_d / 2 * NUB_TAPER))
    tags.append("nub")
    vs, bands, caps = _loft(a, rings, HEAD)
    part = {}
    for i, fs in enumerate(bands):
        t0, t1 = tags[i], tags[i + 1]
        if t1 == "nub":
            p = "nub"
        elif t1 == "top":
            p = ("body", 1.0)
        elif t0 == "nub":
            p = "nub"
        else:
            p = ("body", (t0[1] + t1[1]) / 2)
        for f in fs:
            part[f] = p
    for f in caps:
        part[f] = "nub" if f.calc_center_median().dot(w) > B.dot(w) + body_l * 0.5 or peg else ("body", 0.0)
    return vs, part


# ---- stalk -----------------------------------------------------------------------------------------------------------
STALK_D = 0.25
STALK_SIDES = 6


def stalk(a, p0, p1, seed, d=STALK_D):
    """A straight 6-sided prism from p0 to p1: rings at 0, 0.45 (+-3 % jitter) and 1, flat caps. Returns verts."""
    rng = random.Random(seed)
    p0, p1 = Vector(p0), Vector(p1)
    u, v, w = _frame(p1 - p0)
    L = (p1 - p0).length
    ph = rng.uniform(0, 2 * math.pi)
    rings = []
    for t in (0.0, 0.45, 1.0):
        jit = 0.03 if 0 < t < 1 else 0.0
        rings.append([p0 + w * (t * L) + (u * math.cos(ph + 2 * math.pi * k / STALK_SIDES) +
                                          v * math.sin(ph + 2 * math.pi * k / STALK_SIDES)) *
                      (d / 2 * (1 + rng.uniform(-jit, jit))) for k in range(STALK_SIDES)])
    vs, _, _ = _loft(a, rings, STALK)
    return vs


# ---- leaf ------------------------------------------------------------------------------------------------------------
# width stations (t along the leaf, half width as a fraction of W); the tip is a point at t = 1
LEAF_ST = ((0.0, 0.34), (0.15, 0.40), (0.40, 0.50), (0.62, 0.49), (0.82, 0.36))
EDGE = 0.045           # edge thickness (studs): the sheet's leaves have chunky edges
FOLD = (11.0, 4.0)     # front / back face slope either side of the midrib, degrees (front fold about 158 deg)
TIP_OFF = 0.2          # the knife tip's sideways offset, fraction of W
LEAF_INFO = {}


def leaf_frames(base, tip, arch, n_mid, twist, t):
    """(position, tangent, face normal) at t along a leaf whose chord runs base -> tip: a circular arc turning `arch`
    degrees, bent toward gravity (the tip falls outward, the middle bows up), its broad face n_mid at mid-length
    (the arc's mid tangent is the chord), twisted `twist` degrees from base to tip about its own axis."""
    base, tip = Vector(base), Vector(tip)
    C = tip - base
    chord = C.length
    d = C.normalized()
    g = Vector((0, 0, -1)) + d * d.z
    if g.length < 1e-4:
        g = Vector(n_mid) * -1
    g = (g - d * g.dot(d)).normalized()
    th = math.radians(arch)
    phi = (t - 0.5) * th
    if th < 1e-5:
        pos = base + d * (chord * t)
    else:
        Rr = chord / (2 * math.sin(th / 2))
        phi0 = -th / 2
        pos = base + Rr * ((math.sin(phi) - math.sin(phi0)) * d + (math.cos(phi0) - math.cos(phi)) * g)
    ax = d.cross(g).normalized()
    rot = Matrix.Rotation(phi, 3, ax)
    tan = (rot @ d).normalized()
    n0 = Vector(n_mid)
    n0 = (n0 - d * n0.dot(d)).normalized()
    n = rot @ n0
    n = (Matrix.Rotation(math.radians(twist * (t - 0.5)), 3, tan) @ n).normalized()
    return pos, tan, n


EDGE_SEG = 0.25        # the edge lines are split into segments at most this long (strip corners >= 10 deg, so the
#                        sliver passes never collapse the 0.045 edges to paper)
LEAF_KEEL = {}         # tag -> (min edge thickness, max keel thickness) as built, studs


def leaf(a, base, tip, W, arch, n_mid, twist, seed, tag=None):
    """One broad keeled lance leaf. Stations (LEAF_ST) along the arched, twisted centre line each carry a midrib
    vertex on the front (raised FOLD[0]) and one on the back (FOLD[1]); the two edges are EDGE thick (a top and a
    bottom line) and are split into EDGE_SEG pieces between stations, following the arc; the front and back halves
    are fans from the midrib to those edge points (the midrib fold: two facet planes either side of the keel); a knife
    tip offset sideways (on the upper edge of a leaning leaf); a flat base cap. Returns (verts, {vert: t})."""
    rng = random.Random(seed)
    bm = a.bm
    side = 1 if rng.random() < 0.5 else -1
    pos, tan, n = leaf_frames(base, tip, arch, n_mid, twist, 1.0)
    sz = n.cross(tan).normalized().z
    if abs(sz) > 0.2:          # a leaning leaf: the knife tip on its upper edge (the lower edge runs long to the tip)
        side = 1 if sz > 0 else -1
    e = EDGE / 2
    tf, tb = math.tan(math.radians(FOLD[0])), math.tan(math.radians(FOLD[1]))
    hws = [hf * W * (1 + rng.uniform(-0.04, 0.04)) for _, hf in LEAF_ST]
    ts = [t for t, _ in LEAF_ST] + [1.0]
    y_tip = side * TIP_OFF * W
    tmap = {}

    def vert(t, y, z):
        pos, tan, n = leaf_frames(base, tip, arch, n_mid, twist, t)
        s_ = n.cross(tan).normalized()
        v = bm.verts.new(pos + s_ * y + n * z)
        tmap[v] = t
        return v
    # midrib front / back per station; the tip apex
    MF = [vert(t, 0.0, e + hw * tf) for t, hw in zip(ts, hws)]
    MB = [vert(t, 0.0, -e - hw * tb) for t, hw in zip(ts, hws)]
    apex = vert(1.0, y_tip, 0.0)
    # edge lines: per band a list of (top, bottom) pairs from station i to i + 1 (shared at the stations)
    L = (Vector(tip) - Vector(base)).length * (1 + math.radians(arch) ** 2 / 24)
    edges = {+1: [], -1: []}       # sgn -> list per band of [(top, bottom), ...] incl. both ends
    station = {+1: [], -1: []}
    for sgn in (+1, -1):
        for i, (t, hw) in enumerate(zip(ts[:-1], hws)):
            station[sgn].append((vert(t, sgn * hw, e), vert(t, sgn * hw, -e)))
    for sgn in (+1, -1):
        for i in range(len(hws)):
            t0, t1 = ts[i], ts[i + 1]
            y0 = sgn * hws[i]
            last = i == len(hws) - 1
            y1 = y_tip if last else sgn * hws[i + 1]
            m = max(1, math.ceil((t1 - t0) * L / EDGE_SEG))
            pts = [station[sgn][i]]
            for k in range(1, m):
                u = k / m
                t = t0 + (t1 - t0) * u
                y = y0 + (y1 - y0) * u
                pts.append((vert(t, y, e), vert(t, y, -e)))
            pts.append(None if last else station[sgn][i + 1])
            edges[sgn].append(pts)
    fs = []

    def face(vs):
        fs.append(bm.faces.new(vs))
    for sgn in (+1, -1):
        for i, pts in enumerate(edges[sgn]):
            last = pts[-1] is None
            seq = pts[:-1] if last else pts
            # the edge strip
            for (t0_, b0), (t1_, b1) in zip(seq, seq[1:]):
                face((t0_, t1_, b1, b0))
            if last:
                face((seq[-1][0], apex, seq[-1][1]))
            # front and back halves of this band: midrib i -> edge points -> midrib i + 1 (or the apex)
            top = [p[0] for p in seq] + ([apex] if last else [])
            bot = [p[1] for p in seq] + ([apex] if last else [])
            if last:
                face([MF[i]] + top)
                face([MB[i]] + bot)
            else:
                face([MF[i]] + top + [MF[i + 1]])
                face([MB[i]] + bot + [MB[i + 1]])
    # the midrib fold on the front / back between consecutive stations is shared by the two half fans; at the tip
    # both halves close on the apex. The base cap: the station-0 section
    r0 = station[+1][0]
    l0 = station[-1][0]
    face((r0[0], MF[0], l0[0], l0[1], MB[0], r0[1]))
    # apex faces join MF[-1] / MB[-1] (the last midrib vertex at t = 1 is not used: drop it)
    for v in (MF[-1], MB[-1]):
        if not v.link_faces:
            bm.verts.remove(v)
            tmap.pop(v, None)
    fs = [f for f in fs if f.is_valid]
    tri = bmesh.ops.triangulate(bm, faces=fs, quad_method="BEAUTY", ngon_method="BEAUTY")["faces"]
    vs = [v for v in tmap if v.is_valid]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, LEAF, tint=1.0)
    if tag:
        mid = leaf_frames(base, tip, arch, n_mid, twist, 0.5)[2]
        LEAF_INFO[tag] = dict(n_mid=[round(x, 3) for x in mid],
                              score={c: round(abs(mid.dot(Vector(dv))), 3) for c, dv in CAMS.items()},
                              chord=round((Vector(tip) - Vector(base)).length, 3), W=round(W, 3),
                              keel=round(EDGE + max(hws) * (tf + tb), 3), edge=EDGE)
    return vs, tmap


CAMS = {"front": (0, -1, 0), "side": (1, 0, 0), "rear": (0, 1, 0)}


# ---- mud mound -------------------------------------------------------------------------------------------------------
MOUND = dict(rx=1.85, ry=1.18, n=16, seed=27201)
# rings from the ground up: (z, radius fraction, lump weight, kind)
# round 1b: taller, steeper sides (rim 0.58 -> 0.66, dish 0.5 -> 0.6): the sheet's mound is a chunky lumpy band, ours
# read as a thin chamfered disc
# round 1c: the side band bulges (ring 0.42 at 1.02) and the dish is shallower (0.62 / 0.6), so the mound reads as
# chunky lumps under a nearly flat top, not a pan with a raised rim
# round 2 (verifier blocker 1): the vertical wall ring (0.42, 1.02) became a sloped (0.38, 0.97), and the rim rises
# and falls with the lumps (RIM_LUMP_Z), so the back views show rounded lumps instead of a plank with a flat top
MOUND_RINGS = ((0.0, 0.94, 0.5), (0.12, 1.0, 1.0), (0.38, 0.97, 1.0), (0.66, 0.90, 0.6), (0.62, 0.58, 0.0))
MOUND_CENTRE = 0.60
LUMPS = dict(n=5, amp=0.14, jit=0.03)   # round 1f: 0.10 -> 0.14 (the rear / side read a smooth slab)
RIM_JIT = 0.06
RIM_LUMP_Z = 0.08      # round 2: rim z +-0.08 with the lumps (high on a lump, low in a crease)
BACK_LUMPS = ((62.0, 0.15), (118.0, 0.13))    # (azimuth deg, rim lift); width BACK_W
BACK_W = 26.0
MOUND_INFO = {}


def _lump(th, phase):
    return 1 + LUMPS["amp"] * math.cos(LUMPS["n"] * th + phase)


def mud_base(a):
    """The mound: 16-sided rings lofted from the flat bottom through a short chamfer, the lumpy side band (4 lumps,
    vertical creases between them) and the rim to a shallow dish and a centre point; quads split on a seeded
    diagonal. Returns (verts, {face: (ring band, crease 0-1)})."""
    rng = random.Random(MOUND["seed"])
    bm = a.bm
    n, rx, ry = MOUND["n"], MOUND["rx"], MOUND["ry"]
    phase = rng.uniform(0, 2 * math.pi)
    angs = [2 * math.pi * k / n + rng.uniform(-0.1, 0.1) * (2 * math.pi / n) for k in range(n)]
    jit = [1 + rng.uniform(-LUMPS["jit"], LUMPS["jit"]) for _ in range(n)]
    rows = []
    for i, (z, rf, lw) in enumerate(MOUND_RINGS):
        row = []
        for k, th in enumerate(angs):
            t = th + (math.pi / n if i == 4 else 0.0)
            lf = 1 + (_lump(t, phase) * jit[k] - 1) * lw
            zz = z
            if i == 3:
                zz += rng.uniform(-RIM_JIT, RIM_JIT) + RIM_LUMP_Z * math.cos(LUMPS["n"] * t + phase)
            if i in (2, 3):
                deg = math.degrees(t) % 360
                for az, lift in BACK_LUMPS:
                    dd = min(abs(deg - az), 360 - abs(deg - az))
                    zz += lift * math.exp(-(dd / BACK_W) ** 2) * (1.0 if i == 3 else 0.45)
            row.append(bm.verts.new((math.cos(t) * rx * rf * lf, math.sin(t) * ry * rf * lf, zz)))
        rows.append(row)
    top = bm.verts.new((rng.uniform(-0.05, 0.05), rng.uniform(-0.05, 0.05), MOUND_CENTRE))
    info = {}
    for bi, (r0, r1) in enumerate(zip(rows, rows[1:])):
        for k in range(n):
            j = (k + 1) % n
            a0, a1, b0, b1 = r0[k], r0[j], r1[k], r1[j]
            th = (angs[k] + angs[j]) / 2
            crease = max(0.0, -math.cos(LUMPS["n"] * th + phase))
            if rng.random() < 0.5:
                fs = [bm.faces.new((a0, a1, b1)), bm.faces.new((a0, b1, b0))]
            else:
                fs = [bm.faces.new((a0, a1, b0)), bm.faces.new((a1, b1, b0))]
            for f in fs:
                info[f] = (bi, crease)
    for k in range(n):
        f = bm.faces.new((rows[-1][k], rows[-1][(k + 1) % n], top))
        info[f] = (5, 0.0)
    bot = bm.faces.new(list(reversed(rows[0])))
    for f in bmesh.ops.triangulate(bm, faces=[bot], quad_method="BEAUTY", ngon_method="BEAUTY")["faces"]:
        info[f] = (-1, 0.0)
    vs = [v for r in rows for v in r] + [top]
    bmesh.ops.recalc_face_normals(bm, faces=_faces(vs))
    a._finish(vs, MUD, tint=1.0)
    MOUND_INFO["phase"] = phase
    MOUND_INFO["rim"] = [v.co.copy() for v in rows[3]]
    return vs, info


# ---- rocks -----------------------------------------------------------------------------------------------------------
ROCK_RINGS = [(0.0, 0.9, 6), (0.42, 1.0, 6), (0.8, 0.66, 5), (1.0, 0.22, 2)]
# (label, centre x, y, size (w, d, h), key, yaw, seed)
# (label, direction x, y (only the azimuth is used since round 2), size (w, d, h), key, yaw, seed)
# round 2 (verifier blocker 1): RK4 back to x 1.0 of spec 2.1 (0.7 x 0.65 x 0.6) and RK5 to x 0.95 (0.6 x 0.55 x
# 0.45); they were 0.9 / 0.85 and sat on the mound's wall like studs
ROCKS = (
    ("RK1", -1.75, 0.47, (0.75, 0.70, 0.62), ROCK_DARK, 20.0, 27111),
    ("RK2", -0.95, -0.85, (0.85, 0.75, 0.66), ROCK, 70.0, 27112),
    ("RK3", 1.10, -0.82, (0.68, 0.60, 0.56), ROCK, 140.0, 27113),
    ("RK4", 1.62, 0.45, (0.70, 0.65, 0.60), ROCK, 210.0, 27114),
    ("RK5", -0.30, 1.10, (0.57, 0.52, 0.43), ROCK, 300.0, 27115),
)
ROCK_SCALE = 1.1       # round 1b: 1.0 read 0.7 of the sheet's rock runs at h .16, 1.3 gave R 16 % against 9, 1.15 R 12.3
ROCK_SINK = 0.35       # round 2: fraction of the height below the mound surface at the rock's centre (0.3 -> 0.35)
ROCK_TILT = 12.0       # degrees outward (the outer bottom edge dips toward the ground)
# round 2: every rock sits ON the rim (sheet: the rocks nest in notches of the rim and stand clear above it): its
# centre at ROCK_RIM_F x the local rim radius, its top inside ROCK_TOP and at least ROCK_CLEAR above the highest mud
# within ROCK_NEAR of its centre
ROCK_RIM_F = 0.96
# per-rock (rim fraction, top z or None for the natural top at ROCK_SINK): RK1 out on the rim edge, at az 180 (its
# ROCKS direction), lower, so it shows left of RK2 in the hero (sheet f .10-.20) and its foot shows in the r34; RK5
# out on the edge for the side view's depth; RK4 / RK5 (nearest the side and rear cameras) a little lower, so the
# rear's rock share stays near the sheet's (rear G 47.6 against 51.9 with every top at 1.04)
ROCK_PLACE = {"RK1": (1.0, 0.92), "RK4": (0.96, 0.98), "RK5": (1.0, 0.95)}
ROCK_TOP = (0.85, 1.05)
ROCK_CLEAR = 0.12
ROCK_NEAR = 0.8
ROCK_TINT = {"RK1": 1.0, "RK2": 1.02, "RK3": 0.97, "RK4": 1.0, "RK5": 1.03}
ROCK_INFO = {}


def rock(a, size, loc, seed, key, yaw=0.0, tilt=(0.0, 0.0)):
    vs = K.hull_rock(a, size, loc=loc, seed=seed, mat=key, rings=ROCK_RINGS, jitter=0.1, rot=math.radians(yaw),
                     tilt=tilt, keep_bottom=True)
    _tri(a.bm, _faces(vs))
    bmesh.ops.recalc_face_normals(a.bm, faces=_faces(vs))
    return vs


def _rim_point(th):
    """Where the mound's rim ring (MOUND_INFO['rim'], a closed polygon round the centre) crosses azimuth th (xy)."""
    rim = MOUND_INFO["rim"]
    d = Vector((math.cos(th), math.sin(th)))
    best = None
    for p, q in zip(rim, rim[1:] + rim[:1]):
        p2, q2 = Vector((p.x, p.y)), Vector((q.x, q.y))
        e = q2 - p2
        den = d.x * e.y - d.y * e.x
        if abs(den) < 1e-9:
            continue
        s = (p2.x * e.y - p2.y * e.x) / den        # distance along d
        u = (p2.x * d.y - p2.y * d.x) / den        # fraction along the edge
        if s > 0 and -1e-6 <= u <= 1 + 1e-6 and (best is None or s < best[0]):
            best = (s, p.z + (q.z - p.z) * u)
    return d * best[0], best[1]


def rocks(a, tree, mvs):
    out = {}
    mud = [v.co.copy() for v in mvs if v.is_valid]
    for lab, x, y, size, key, yaw, seed in ROCKS:
        th = math.atan2(y, x)
        rp, rz = _rim_point(th)
        rim_f, top_z = ROCK_PLACE.get(lab, (ROCK_RIM_F, None))
        c = rp * rim_f
        hit = tree.ray_cast(Vector((c.x, c.y, 5.0)), Vector((0, 0, -1)), 10)
        sz = hit[0].z if hit[0] is not None else rz
        hi = max(p.z for p in mud if (Vector((p.x, p.y)) - c).length <= ROCK_NEAR)
        size = tuple(s * ROCK_SCALE for s in size)
        # outward tilt: about the horizontal axis perpendicular to the radial direction
        r = Vector((c.x / MOUND["rx"], c.y / MOUND["ry"], 0)).normalized()
        tl = math.radians(ROCK_TILT)
        tilt = (-r.y * tl, r.x * tl)          # (about X, about Y): +X radial dips +X side (rotation about +Y)
        z0 = sz - ROCK_SINK * size[2]
        vs = rock(a, size, (c.x, c.y, z0), seed, key, yaw, tilt)
        top = max(v.co.z for v in vs)
        want = min(ROCK_TOP[1] - 0.01, max(top if top_z is None else top_z, ROCK_TOP[0] + 0.01,
                                           hi + ROCK_CLEAR + 0.01))
        dz = want - top
        for v in vs:
            v.co.z += dz
        out[lab] = vs
        ROCK_INFO[lab] = dict(centre=[round(c.x, 3), round(c.y, 3)], rim_f=rim_f, surface=round(sz, 3),
                              top=round(top + dz, 3), mud_near=round(hi, 3), clear=round(top + dz - hi, 3),
                              sink=round((sz - (z0 + dz)) / size[2], 3))
    return out


# ---- layout (spec 2.2, 2.3) ------------------------------------------------------------------------------------------
STALK_SINK = 0.12      # the stalk top this far into the head's bottom chamfer
# head: (stalk foot, head bottom, body d, body length, nub d, nub length, seed)
HEADS = {
    # round 1b: H1 0.1 right (its head reached f .15 in f34 against the sheet's .17)
    "H1": ((-0.20, -0.15, 0.42), (-0.95, -0.35, 2.42), 0.55, 1.18, 0.17, 0.22, 27301),
    "H2": ((0.30, -0.10, 0.42), (-0.20, 0.10, 2.72), 0.65, 1.36, 0.20, 0.25, 27302),
    # round 2: H3 leans 2.7 deg less toward +X (12.9 deg from 15.6) and its head sits 0.04 further back, so its cast
    # shadow falls behind LG: foot (0.15, 0.30) -> (0.20, 0.30), head bottom (0.82, 0.20, 2.85) -> (0.76, 0.24,
    # 2.875). The foot moved right so the head's top stays at the sheet's f .70 peak (x 1.11 against 1.23; leaning
    # less about the old foot put it at x 1.02, f .65, and LI touched the stalk)
    "H3": ((0.20, 0.30, 0.42), (0.76, 0.24, 2.875), 0.62, 1.32, 0.20, 0.24, 27303),
}
LEAF_Z = 0.42          # leaf bases 0.15 under the dish
# leaf: (base x, y, tip (x, y, z), W, arch deg, face normal at mid-length, twist deg, colour shift, seed)
# round 1e: LA, LC, LE, LF and LI bases moved 0.06-0.22 (searched: the smallest base move, tips fixed, that keeps
# every leaf at least 0.04 clear of every stalk and head above z 0.75; four of them passed through a stalk)
# round 1c: RK3 / RK4 (nearest the side camera) 10 % smaller, LD / LE / LF 10 % wider (side: rock 15 % against 10,
# green 49 against 56)
# round 1b: widths x 1.15-1.25 (the sheet's leaves read broader); LA, LB, LG further out in depth (side D : H 0.56
# against 0.633: the side cell's front leaf reaches Y -1.5, its back leaves Y +1.25-1.3); LA arched more (its upper
# edge runs nearly flat at h .57-.60 to the tip); LG's face turned up toward the front (its underside faced the
# camera and read dark; the sheet's LG is lit lime); LC and LI turned toward the back-left / back so the top view's
# tips spread round the circle (spec 3.4)
LEAVES = {
    # round 2 (verifier minor): LA arch 35 -> 40, LH 25 -> 45 (their middles bow up: f34 neck at h .3 0.65 against
    # 0.55-0.63, fan widest at h .4 instead of .5). LA at 44-50 touches H1's stalk (gap < 0.02)
    "LA": ((-0.57, -0.14), (-2.40, -1.65, 2.75), 0.85, 40.0, (0.67, -0.67, 0.31), 20.0, 0.0, 27401),
    # round 2: LB's tip Y 1.35 -> 1.55 (the side view lost depth when LG's tip came forward: D : H 0.57)
    "LB": ((-0.25, 0.20), (-0.85, 1.55, 2.75), 0.62, 10.0, (-0.70, -0.70, 0.17), -18.0, 0.0, 27402),
    "LC": ((-0.48, -0.18), (-0.85, 0.20, 2.05), 0.50, 5.0, (0.71, -0.71, 0.02), 16.0, 0.1, 27403),
    "LD": ((-0.05, -0.45), (-0.15, -0.90, 1.85), 0.50, 5.0, (-0.69, 0.70, 0.17), -16.0, 0.1, 27404),
    "LE": ((0.04, -0.20), (0.12, -0.45, 2.35), 0.55, 0.0, (0.71, 0.70, 0.08), 16.0, 0.1, 27405),
    "LF": ((-0.02, -0.17), (0.25, -0.60, 3.15), 0.68, 5.0, (0.70, 0.71, 0.10), -18.0, 0.0, 27406),
    # round 2 (verifier blocker 2c): LG's tip (2.30, 1.30, 3.05) -> (2.40, 0.92, 2.85), with H3 leaning less, mostly
    # out of H3's cast shadow under the studio key: the shaded share of its upper half (SHADE) 0.65 -> about 0.25.
    # Tried: (2.55, 1.10) 0.50; (2.55, 0.75) 0.10 but the side view lost its back leaf (D : H 0.57) and the f34 tip
    # moved to f .91 (sheet .88)
    "LG": ((0.35, 0.15), (2.40, 0.92, 2.85), 0.85, 20.0, (-0.54, -0.60, 0.59), 20.0, 0.0, 27407),
    "LH": ((0.40, -0.10), (2.85, -0.45, 1.95), 0.82, 45.0, (-0.49, -0.50, 0.72), -20.0, 0.0, 27408),
    "LI": ((0.19, 0.43), (0.50, 1.05, 2.55), 0.60, 10.0, (0.71, -0.71, 0.05), 18.0, 0.0, 27409),
}


def head_geom(name):
    foot, hb, d, bl, nd, nl, seed = HEADS[name]
    foot, hb = Vector(foot), Vector(hb)
    axis = (hb - foot).normalized()
    return foot, hb, axis, d, bl, nd, nl, seed


# ---- colour (stage 4): painted by position, never by facing ----------------------------------------------------------
LEAF_BANDS = ((0.12, 0.42), (0.58, 0.88))     # t: leaf_base -> leaf over the first band, leaf -> tip over the second
# round 2 (verifier blocker 2b): LA and LG, the two big outer leaves whose upper halves are grazing-lit / partly in
# the heads' shade, start the leaf -> tip ladder earlier (a per-leaf position shift along t, like LC/LD/LE's)
# LH (lies low, faces the key squarely; the sheet's LH tip #9BB13A is darker than the other tips) ends its ladder
# later, so its very tip is a 75 % tip mix
LEAF_TIP_BANDS = {"LA": (0.40, 0.70), "LG": (0.40, 0.70), "LH": (0.66, 1.06)}
LEAF_NOISE = 0.06
HEAD_BAND = (0.2, 0.8)                        # head -> head_light across the body t
STALK_FOOT = (0.3, 0.25)                      # the stalk's bottom fraction gets this mix toward leaf_base
MOTTLE = {"leaf": (0.03, 0.5), "head": (0.025, 0.7), "stalk": (0.02, 0.6), "mud": (0.05, 0.4),
          "rock": (0.04, 0.8)}
PIECE_TINT = 0.04
# mud: (dish, rim band, creases, bottom chamfer, patch) mixes toward mud_dark
# (pass 2: rim_near 0.5 -> 0.25, rim and chamfer 0.25 -> 0, patch level 0.18 -> 0.3: the sheet's mound reads plain mud
# #846549 in f34, as its exploded base #806247)
MUD_MIX = dict(dish=0.5, rim_near=0.25, rim=0.0, crease=0.25, chamfer=0.0, patch=0.25, patch_level=0.3,
               patch_scale=0.9, near=0.55)


def _ladder(lo, mid, hi, v, bands):
    (a0, a1), (b0, b1) = bands
    if v < (a1 + b0) / 2:
        return K.mix_key(lo, mid, _q((v - a0) / (a1 - a0)))
    return K.mix_key(mid, hi, _q((v - b0) / (b1 - b0)))


def paint_leaf(a, vs, tm, shift, seed, bands=LEAF_BANDS):
    rng = random.Random(seed)
    nf = K.noise_field(scale=0.9, seed=seed)
    fs = _faces(vs)
    for f in fs:
        c = f.calc_center_median()
        t = sum(tm[v] for v in f.verts) / len(f.verts) - shift + LEAF_NOISE * 1.6 * nf(c)
        f.material_index = a._mi(_ladder(LEAF_BASE, LEAF, LEAF_TIP, t, bands))
    amp, sc = MOTTLE["leaf"]
    _mottle(a, fs, amp, sc, seed + 1, level=1.0 + rng.uniform(-PIECE_TINT, PIECE_TINT))


def paint_head(a, vs, part, seed):
    rng = random.Random(seed)
    fs = _faces(vs)
    for f in fs:
        p = part.get(f, ("body", 0.5))
        if p == "nub":
            f.material_index = a._mi(NUB)
        else:
            t = (p[1] - HEAD_BAND[0]) / (HEAD_BAND[1] - HEAD_BAND[0])
            f.material_index = a._mi(K.mix_key(HEAD, HEAD_LIGHT, _q(t)))
    amp, sc = MOTTLE["head"]
    _mottle(a, fs, amp, sc, seed + 1, level=1.0 + rng.uniform(-PIECE_TINT, PIECE_TINT))


def paint_stalk(a, vs, p0, p1, seed):
    p0, p1 = Vector(p0), Vector(p1)
    w = p1 - p0
    fs = _faces(vs)
    for f in fs:
        t = (f.calc_center_median() - p0).dot(w) / w.length_squared
        f.material_index = a._mi(K.mix_key(STALK, LEAF_BASE, STALK_FOOT[1] if t < STALK_FOOT[0] else 0.0))
    amp, sc = MOTTLE["stalk"]
    _mottle(a, fs, amp, sc, seed + 1)


def paint_mud(a, vs, info, feet=()):
    """mud -> mud_dark by position: the dish, the rim band near a leaf/stalk foot, the creases between lumps, the
    bottom chamfer, broad noise patches; quarter steps."""
    mm = MUD_MIX
    pf = K.noise_field(scale=mm["patch_scale"], seed=27501)
    fs = _faces(vs)
    for f in fs:
        band, crease = info.get(f, (2, 0.0))
        c = f.calc_center_median()
        t = 0.0
        if band == 5:
            t = mm["dish"]
        elif band == 3:
            near = min((Vector((c.x - x, c.y - y)).length for x, y in feet), default=9.0)
            t = mm["rim_near"] if near < mm["near"] else mm["rim"]
        elif band == 0:
            t = mm["chamfer"]
        if band in (1, 2) and crease > 0.7:
            t = max(t, mm["crease"])
        if band != -1 and pf(c) > mm["patch_level"]:
            t = max(t, mm["patch"])
        f.material_index = a._mi(K.mix_key(MUD, MUD_DARK, _q(t)))
    amp, sc = MOTTLE["mud"]
    _mottle(a, fs, amp, sc, 27502)


def paint_rock(a, lab, vs, seed):
    amp, sc = MOTTLE["rock"]
    _mottle(a, _faces(vs), amp, sc, seed, level=ROCK_TINT.get(lab, 1.0))


# ---- parts -----------------------------------------------------------------------------------------------------------
# the part leans right with its face toward the studio key (front-left-above): leaning left, its face could turn at
# most 0.63 to the key and the parts shot read 25-30 darker than the sheet's lit exploded leaf
PART_LEAF = dict(base=(0.0, 0.0, 0.0), tip=(1.06, 0.0, 2.26), W=0.6, arch=25.0, n=(-0.72, -0.66, 0.34), twist=20.0)


def seed_head_part(a):
    foot, hb, axis, d, bl, nd, nl, seed = head_geom("H2")
    vs, part = seed_head(a, (0, 0, PEG[1]), (0, 0, 1), d, bl, nd, nl, seed, peg=True)
    paint_head(a, vs, part, seed)


def stalk_part(a):
    vs = stalk(a, (0, 0, 0), (0, 0, 2.45), 27311)
    for f in _faces(vs):
        f.material_index = a._mi(STALK)
    amp, sc = MOTTLE["stalk"]
    _mottle(a, _faces(vs), amp, sc, 27312)


def leaf_part(a):
    p = PART_LEAF
    vs, tm = leaf(a, p["base"], p["tip"], p["W"], p["arch"], p["n"], p["twist"], 27411, tag="part")
    paint_leaf(a, vs, tm, 0.0, 27411)


def mud_base_part(a):
    vs, info = mud_base(a)
    paint_mud(a, vs, info, feet=[(0.0, 0.0)])


def rock_part(a):
    vs = rock(a, (0.9, 0.8, 0.65), (0, 0, 0), 27120, ROCK)
    paint_rock(a, "RK2", vs, 27120)


# ---- hero ------------------------------------------------------------------------------------------------------------
PIECES = {}
CLEAR = {}             # leaf -> (smallest gap to any stalk / head above z 0.75, which); -1 = they intersect
HERO_TRIES = 6
LEAF_W_SCALE = 1.12    # round 1d: every hero leaf 8 % wider (rear / side green 45-50 % against the sheet's 52-56)
#                        round 2: 1.08 -> 1.12 (the rocks now stand above the rim: side / rear G 51.9 / 47.5 against
#                        56.1 / 51.9)
LEAF_JIT = [0]         # hero guard: on a retry every leaf base moves a few hundredths of a stud (seeded per leaf)


def hero(a):
    LEAF_INFO.clear()
    ROCK_INFO.clear()
    PIECES.clear()
    mvs, minfo = mud_base(a)
    tree = K.bvh_of(mvs)
    rk = rocks(a, tree, mvs)
    feet = [(v[0][0], v[0][1]) for v in HEADS.values()] + [v[0] for v in LEAVES.values()]
    paint_mud(a, mvs, minfo, feet)
    for i, (lab, vs) in enumerate(rk.items()):
        paint_rock(a, lab, vs, 27130 + i)
    PIECES["mound"] = mvs
    PIECES.update(rk)
    for k in HEADS:
        foot, hb, axis, d, bl, nd, nl, seed = head_geom(k)
        top = hb + axis * STALK_SINK
        vs = stalk(a, foot, top, seed + 10)
        paint_stalk(a, vs, foot, top, seed + 10)
        PIECES["S" + k[1]] = vs
    for k in HEADS:
        foot, hb, axis, d, bl, nd, nl, seed = head_geom(k)
        vs, part = seed_head(a, hb, axis, d, bl, nd, nl, seed)
        paint_head(a, vs, part, seed)
        PIECES[k] = vs
    for k, (bxy, tip, W, arch, n, tw, shift, seed) in LEAVES.items():
        jr = random.Random(seed * 31 + LEAF_JIT[0])
        j = 0.02 * LEAF_JIT[0]
        b = (bxy[0] + jr.uniform(-j, j), bxy[1] + jr.uniform(-j, j), LEAF_Z)
        vs, tm = leaf(a, b, tip, W * LEAF_W_SCALE, arch, n, tw, seed, tag=k)
        bands = (LEAF_BANDS[0], LEAF_TIP_BANDS[k]) if k in LEAF_TIP_BANDS else LEAF_BANDS
        paint_leaf(a, vs, tm, shift, seed, bands)
        PIECES[k] = vs
        LEAF_T[k] = tm
    CLEAR.clear()
    CLEAR.update(clearances())
    SHADE.clear()
    SHADE.update(shade())


KEY_DIR = Vector((0.49, 0.59, -0.64)).normalized()   # the studio key light's travel direction (verifier round 1)
LEAF_T = {}
SHADE = {}             # leaf -> fraction of its upper half (t > 0.5, by area) in another piece's cast shadow


def shade(leaves=("LA", "LG", "LH")):
    """Cast-shadow share of each leaf's upper half under the studio key, from the hero's live pieces (pre-union)."""
    out = {}
    for lk in leaves:
        others = [v for k, vs in PIECES.items() if k != lk for v in vs if v.is_valid]
        fs = _faces(others)
        idx, pts = {}, []
        for f in fs:
            for v in f.verts:
                if v not in idx:
                    idx[v] = len(pts)
                    pts.append(v.co.copy())
        tree = BVHTree.FromPolygons(pts, [[idx[v] for v in f.verts] for f in fs])
        tm = LEAF_T[lk]
        tot = hid = 0.0
        for f in _faces(PIECES[lk]):
            t = sum(tm.get(v, 0) for v in f.verts) / len(f.verts)
            if t < 0.5:
                continue
            ar = f.calc_area()
            tot += ar
            if tree.ray_cast(f.calc_center_median() - KEY_DIR * 0.02, -KEY_DIR, 20)[0] is not None:
                hid += ar
        out[lk] = round(hid / max(tot, 1e-9), 3)
    return out


def clearances(zmin=0.75):
    """Smallest gap between each leaf and any stalk / head above zmin (below that they meet inside the clump base),
    from the hero's pieces while its bmesh is live (hero() calls this before the union); -1 = they intersect."""
    def tree(vs):
        fs = [f for f in _faces(vs) if f.calc_center_median().z > zmin]
        idx, pts = {}, []
        for f in fs:
            for v in f.verts:
                if v not in idx:
                    idx[v] = len(pts)
                    pts.append(v.co.copy())
        return BVHTree.FromPolygons(pts, [[idx[v] for v in f.verts] for f in fs]), pts
    obs = {k: tree(PIECES[k]) for k in ("S1", "S2", "S3", "H1", "H2", "H3")}
    out = {}
    for lk in LEAVES:
        tl, lp = tree(PIECES[lk])
        best = (9.0, None)
        for sk, (ts, sp) in obs.items():
            if tl.overlap(ts):
                best = (-1.0, sk)
                break
            d = min(min((ts.find_nearest(p)[3] for p in lp), default=9.0),
                    min((tl.find_nearest(p)[3] for p in sp), default=9.0))
            if d < best[0]:
                best = (round(d, 3), sk)
        out[lk] = best
    return out


NOTES = {
    HERO: "reed patch resource node: three tan faceted cattail heads with dark nubs on straight green stalks above a "
          "fan of nine broad keeled leaves, on a low lumpy brown mud mound ringed with five grey rocks; one closed "
          "mesh, flat underside. No VFX",
    "ReedClumpSeedHead": "Seed Head (reusable): 8-sided faceted tan capsule, chamfered ends, dark nub on top, short "
                         "bottom peg",
    "ReedClumpStalk": "Reed Stalk (reusable): straight 6-sided green prism, flat ends",
    "ReedClumpLeafBlade": "Leaf Blade (reusable): broad keeled lance with a midrib fold, thick edges, knife tip",
    "ReedClumpMudBase": "Mud Base (reusable): low oval lumpy mud mound with a shallow dish, flat underside",
    "ReedClumpRock": "Rock (reusable): faceted grey boulder, flat bottom",
}


# ---- cleanup (M022's guarded procedure, copied: other builders are edited in parallel) --------------------------------
def _volume(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    v = bm.calc_volume(signed=True)
    bm.free()
    return v


UNION_MERGE = 0.0


def _union(o, tries=5):
    """Guarded union: each shell is unioned on with an exact boolean, one at a time, the result checked against the
    volumes going in; a bad result is undone and the shell retried nudged a few thousandths of a stud; a shell that
    still fails is reported and left out. Returns {"shells", "retried", "failed"}."""
    act = bpy.context.view_layer.objects.active
    if act and act.mode != "OBJECT":
        with bpy.context.temp_override(active_object=act, object=act):
            bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()
    others = M.split_loose(o)
    bpy.context.view_layer.update()
    retried, failed = [], []
    rng = random.Random(27900)
    for i, p in enumerate(others):
        for ob in (o, p):
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            loose = [v for v in bm.verts if not v.link_faces]
            if loose:
                bmesh.ops.delete(bm, geom=loose, context="VERTS")
                bm.to_mesh(ob.data)
            bm.free()
        v0, vp = _volume(o.data), _volume(p.data)
        home = p.matrix_world.copy()
        ok = False
        for t in range(tries):
            keep = o.data.copy()
            if t:
                p.matrix_world = Matrix.Translation(Vector([rng.uniform(-1, 1) * 0.006 * t for _ in range(3)])) @ home
            bpy.context.view_layer.update()
            m = o.modifiers.new("U", "BOOLEAN")
            m.operation, m.solver, m.object = "UNION", "EXACT", p
            m.material_mode = "TRANSFER"
            with M._override(o):
                bpy.ops.object.modifier_apply(modifier=m.name)
            v1 = _volume(o.data)
            if v1 >= max(v0, vp) * 0.995 and v1 <= (v0 + vp) * 1.005:
                ok = True
                bpy.data.meshes.remove(keep)
                if t:
                    retried.append((i, t))
                break
            old = o.data
            o.data = keep
            bpy.data.meshes.remove(old)
        if not ok:
            failed.append(i)
        bpy.data.objects.remove(p, do_unlink=True)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    if UNION_MERGE:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=UNION_MERGE)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=UNION_MERGE)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    M.drop_specks(bm, min_area=0.02)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    K.drop_unused_slots(o)
    return {"shells": len(others) + 1, "retried": retried, "failed": failed}


def _shell_count(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    _, n = M._shell_ids(bm)
    bm.free()
    return n


def _self_hits(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    pairs = [(x, y) for x, y in tree.overlap(tree) if x < y and not set(bm.faces[x].verts) & set(bm.faces[y].verts)]
    where = [[round(c, 2) for c in bm.faces[x].calc_center_median()] for x, _ in pairs[:5]]
    bm.free()
    return len(pairs), where


def _inverted_ids(o):
    """Face indices whose front side is solid (ray parity along the normal is odd)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.normal_update()
    t = BVHTree.FromBMesh(bm)
    out = []
    for f in bm.faces:
        if f.calc_area() < 1e-12:
            continue
        n = f.normal.normalized()
        p = f.calc_center_median() + n * 1e-4
        hits = 0
        while hits < 60:
            loc = t.ray_cast(p, n)[0]
            if loc is None:
                break
            hits += 1
            p = loc + n * 1e-5
        if hits % 2:
            out.append(f.index)
    bm.free()
    return out


def inverted(o):
    return len(_inverted_ids(o))


def _guarded(o, fn):
    """Run a cleanup step on o; undo it if it leaves more crossing faces or more shells than before."""
    before = (_self_hits(o)[0], _shell_count(o))
    keep = o.data.copy()
    out = fn()
    after = (_self_hits(o)[0], _shell_count(o))
    if after[0] > before[0] or after[1] > before[1]:
        old = o.data
        o.data = keep
        bpy.data.meshes.remove(old)
        return None
    bpy.data.meshes.remove(keep)
    return out


def _finish(o):
    res = M.finish(o, union=False, uv=UV)
    for _ in range(3):
        crumbs = m012._drop_inner(o)
        if not (crumbs or res["nonmanifold_edges"] or res["boundary_edges"]):
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
        _guarded(o, lambda: m012._force_slivers(o))
        res = M.finish(o, union=False, uv=UV)
    return res


def _tri_quads(bm):
    n = 0
    for f in [f for f in bm.faces if len(f.verts) > 3]:
        if not f.is_valid or len(f.verts) < 4:
            continue
        if len(f.verts) > 4:
            bmesh.ops.triangulate(bm, faces=[f], quad_method="BEAUTY", ngon_method="BEAUTY")
            n += 1
            continue
        a, b, c, d = f.verts
        opts = sorted(((min(m011._min_angle([p.co, q.co, r.co]), m011._min_angle([p.co, q.co, s.co])), p, q)
                       for p, q, r, s in ((a, c, b, d), (b, d, c, a))), key=lambda x: -x[0])
        for _, p, q in opts:
            e = bm.edges.get((p, q))
            if e is None or bmesh.ops.rotate_edges(bm, edges=[e], use_ccw=False)["edges"]:
                break
        else:
            continue
        if f.is_valid and len(f.verts) == 4:
            bmesh.ops.connect_verts(bm, verts=[p, q])
            n += 1
    leftover = [f for f in bm.faces if len(f.verts) > 3]
    if leftover:
        bmesh.ops.triangulate(bm, faces=leftover, quad_method="BEAUTY", ngon_method="BEAUTY")
    return n


def _collapse_needles(o, max_len=0.05, lim=POLISH_LIM):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = 0
    for _ in range(30):
        bad = None
        for f in bm.faces:
            if math.degrees(m011._min_angle([v.co for v in f.verts])) < lim:
                e = min(f.edges, key=lambda e: e.calc_length())
                if e.calc_length() < max_len and all(v.co.z > 1e-4 for v in e.verts):
                    bad = e
                    break
        if bad is None:
            break
        bmesh.ops.collapse(bm, edges=[bad], uvs=True)
        n += 1
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    return n


def _flip_thin(o, lim=POLISH_LIM, max_bend=20.0):
    """Needles with no short edge: rotate the needle's longest edge when both new triangles are fatter and the two
    faces are nearly coplanar (at most max_bend degrees apart). Returns the flips made."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = 0
    for _ in range(20):
        done = False
        for f in list(bm.faces):
            if not f.is_valid or len(f.verts) != 3:
                continue
            if math.degrees(m011._min_angle([v.co for v in f.verts])) >= lim:
                continue
            e = max(f.edges, key=lambda e: e.calc_length())
            if len(e.link_faces) != 2:
                continue
            g = e.link_faces[0] if e.link_faces[1] is f else e.link_faces[1]
            if math.degrees(f.normal.angle(g.normal, 0.0)) > max_bend:
                continue
            a, b = e.verts
            c = next(v for v in f.verts if v not in (a, b))
            d = next(v for v in g.verts if v not in (a, b))
            if bm.edges.get((c, d)):
                continue
            new = min(m011._min_angle([a.co, c.co, d.co]), m011._min_angle([b.co, c.co, d.co]))
            old = min(m011._min_angle([v.co for v in f.verts]), m011._min_angle([v.co for v in g.verts]))
            if new <= old:
                continue
            if bmesh.ops.rotate_edges(bm, edges=[e], use_ccw=False)["edges"]:
                n += 1
                done = True
                break
        if not done:
            break
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    return n


def _loops(edges):
    nbr = {}
    for e in edges:
        a, b = e.verts
        nbr.setdefault(a, []).append(b)
        nbr.setdefault(b, []).append(a)
    seen, out = set(), []
    for v0 in nbr:
        if v0 in seen or len(nbr[v0]) != 2:
            continue
        loop, prev, v = [v0], None, v0
        seen.add(v0)
        while True:
            nxt = next((w for w in nbr[v] if w is not prev), None)
            if nxt is None or nxt is v0 or nxt in seen or len(nbr[nxt]) != 2:
                break
            loop.append(nxt)
            seen.add(nxt)
            prev, v = v, nxt
        if len(loop) >= 3:
            out.append(loop)
    return out


def _fan_fill(bm, bnd):
    made = 0
    for loop in _loops(bnd):
        k = len(loop)
        for s0 in range(k):
            vs = loop[s0:] + loop[:s0]
            if any(bm.edges.get((vs[0], vs[i])) for i in range(2, k - 1)):
                continue
            for i in range(1, k - 1):
                try:
                    bm.faces.new((vs[0], vs[i], vs[i + 1]))
                    made += 1
                except ValueError:
                    pass
            break
    return made


def _seal(o, rounds=3):
    n = 0
    for _ in range(rounds):
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bnd = [e for e in bm.edges if e.is_boundary]
        if not bnd:
            bm.free()
            break
        n += _fan_fill(bm, bnd)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY")
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(o.data)
        bm.free()
        M.repair_nonmanifold(o)
    return n


def _polish(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = _tri_quads(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = _guarded(o, lambda: m012._force_slivers(o, lim=POLISH_LIM))
    if forced is None:
        forced = _guarded(o, lambda: m012._force_slivers(o, lim=3.0, max_len=0.08))
    needles = _guarded(o, lambda: _collapse_needles(o))
    removed = []
    for _ in range(4):
        bad = _inverted_ids(o)
        if not bad:
            break
        removed.append(len(bad))
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.faces[i] for i in bad], context="FACES")
        bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bm.to_mesh(o.data)
        bm.free()
        _seal(o)
        _guarded(o, lambda: m012._force_slivers(o, lim=POLISH_LIM))
    late = []
    for ml in (0.15, 0.3, 0.5):
        if not m012._thin(o, POLISH_LIM)["under"]:
            break
        late.append(_guarded(o, lambda: m012._force_slivers(o, lim=POLISH_LIM, max_len=ml)))
    if m012._thin(o, POLISH_LIM)["under"]:
        late.append(_guarded(o, lambda: _flip_thin(o)))
    bc = m011._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:
            c.location -= bc
    o.data.update()
    M.smart_uv(o, **UV)
    return {"split": split, "forced": forced, "needles": needles, "late": late, "inverted_removed": removed,
            "uv_cut": m012._uv_unfold(o)}


CLEAN_MOVE = 0.05


def _clean_mesh(o, planes=(0.0,)):
    """The shared sliver pass, guarded (thin leaf edges must not fold through each other)."""
    pockets = m012._drop_inner(o)
    log = None
    for mv in (CLEAN_MOVE, CLEAN_MOVE / 2, CLEAN_MOVE / 4):
        log = _guarded(o, lambda: m011._clean(o, m011._plane_lock(planes), max_move=mv))
        if log is not None:
            log["max_move"] = mv
            break
    log = log or {"undone": True}
    pockets += m012._drop_inner(o)
    log["pockets"] = pockets
    log["forced"] = _guarded(o, lambda: m012._force_slivers(o))
    return log


def _fix_floor(o):
    """Faces the floor cut made (flat, facing down at z 0): plain mud, Tint 0.95 (never a darker key on the
    down-facing underside, which would colour by facing)."""
    p = m011._Paint(o, off=(0, 0, 0))
    lay = p.tint_layer
    for f in p.bm.faces:
        if f.normal.z < -0.99 and abs(f.calc_center_median().z) < 1e-3:
            f.material_index = p._mi(MUD)
            for lo in f.loops:
                lo[lay] = (0.95, 0.95, 0.95, 1.0)
    p.done()


def _fused_ok(o):
    au = M.audit(o)
    return (au["shells"] == 1 and not au["nonmanifold_edges"] and not au["nonmanifold_verts"] and
            not au["boundary_edges"] and au["normals"] == "outward" and not _self_hits(o)[0] and not inverted(o))


# ---- stages 5 + 6 (spec section 7) -----------------------------------------------------------------------------------
# Stage 5: nothing. The sheet shows an ordinary sunlit plant clump on dry mud: no emissive key, no light (decision 7).
# Stage 6: nothing. No glow, floating seeds, fluff, water or dust on the sheet: no socket (decision 7).

# ---- build -----------------------------------------------------------------------------------------------------------
PARTS = (("ReedClumpSeedHead", seed_head_part), ("ReedClumpStalk", stalk_part),
         ("ReedClumpLeafBlade", leaf_part), ("ReedClumpMudBase", mud_base_part), ("ReedClumpRock", rock_part))
GROUND_PARTS = {"ReedClumpMudBase"}
TARGET_SIZE = ((5.3, 0.3), (2.8, 0.35), (4.4, 0.2))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)


def _make(name, fn, role, budget):
    o = M.mk(SHEET, name, fn, subject=TITLE, role=role, notes=NOTES[name], budget=budget, collision="hull",
             tint_var=0.0)
    lg = {}
    if role == "hero":
        lg["union"] = _union(o)
        hoff = M._build_offset(fn)
        m004.floor_cut(o, z0=-hoff.z)
        _fix_floor(o)
        lg["clean"] = _clean_mesh(o, (0.0,))
    lg["finish"] = {k: v for k, v in _finish(o).items() if k in ("tris", "nonmanifold_edges", "boundary_edges")}
    lg["polish"] = _polish(o)
    # bowtie vertices (two closed fans meeting at one point) left by the unions: split per fan (shared helper)
    lg["bowties"] = M.fix_bowties(o)
    return o, lg


def _drop_unused(objs):
    names = {o.name for o in objs}
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.split(".")[0] in names]
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m027_")]
    out = {"meshes": len(meshes), "materials": len(mats)}
    for m in meshes:
        bpy.data.meshes.remove(m)
    for m in mats:
        bpy.data.materials.remove(m)
    for o in objs:
        if o.data.name != o.name and o.name not in bpy.data.meshes:
            o.data.name = o.name
    return out


def build(render=True, parts=True):
    import time
    t0 = time.time()
    M.coll(NUM, TITLE)
    palette()
    objs, log = {}, {}
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make(name, fn, "part", 1000)
    part_leaf = dict(LEAF_INFO.get("part", {}))
    # the hero guard: two leaves crossing at a grazing angle near their bases can leave a self-intersecting sliver
    # pair after the union and cleanup; then every leaf base moves a little (LEAF_JIT) and the hero is rebuilt
    for attempt in range(HERO_TRIES):
        LEAF_JIT[0] = attempt
        h, log["hero"] = _make(HERO, hero, "hero", 4000)
        if _fused_ok(h):
            break
    log["hero"]["attempt"] = attempt
    clear = dict(CLEAR)
    order = [h] + [objs[n] for n, _ in PARTS if n in objs]
    _restyle()
    _cleanup_tmp()
    M.display(NUM, order, TITLE)
    dropped = _drop_unused(order)
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    audits = [M.audit(o) for o in order]
    inv = {o.name: inverted(o) for o in order}
    hits = {o.name: _self_hits(o) for o in order}
    thin = {o.name: m012._thin(o, POLISH_LIM) for o in order}
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
        if inv[o.name]:
            problems.append(f"{o.name}: {inv[o.name]} inverted faces")
        if hits[o.name][0]:
            problems.append(f"{o.name}: {hits[o.name][0]} self-intersecting face pairs {hits[o.name][1]}")
        if thin[o.name]["under"]:
            problems.append(f"{o.name}: {thin[o.name]['under']} faces with a corner under {POLISH_LIM} deg")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if log["hero"]["union"]["failed"]:
        problems.append(f"{HERO}: union left out shells {log['hero']['union']['failed']}")
    for k, v in LEAF_INFO.items():
        lo = min(v["score"].values())
        floor = 0.30 if k == "LH" else 0.35
        if lo < floor:
            problems.append(f"leaf {k}: face score {lo} under {floor}")
    for k, (g, sk) in clear.items():
        if g < 0.02:
            problems.append(f"leaf {k} {'intersects' if g < 0 else 'touches'} {sk} (gap {g})")
    for k, v in ROCK_INFO.items():      # round 2: every rock stands on the rim, clear above the mud round it
        if not ROCK_TOP[0] <= v["top"] <= ROCK_TOP[1] or v["clear"] < ROCK_CLEAR:
            problems.append(f"rock {k}: top {v['top']} / {v['clear']} above the mud near it")
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts")} for au in audits],
           "inverted": inv, "self_hits": {k: v[0] for k, v in hits.items()}, "thin": thin, "log": log,
           "dropped": dropped, "leaves": dict(LEAF_INFO), "part_leaf": part_leaf, "rocks": dict(ROCK_INFO),
           "clearance": clear, "shade": dict(SHADE), "problems": problems,
           "uv": {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped",
                                                                            "min_gap", "density",
                                                                            "stretch_conformal_p95")}
                  for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order)
        out["expl_face"] = dict(EXPL_FACE)
        out["total_s"] = round(time.time() - t0, 1)
    return out


# ---- renders ---------------------------------------------------------------------------------------------------------
# the sheet's comparison cameras (decision 9); every *_sheet shot hides the studio floor (the grey rocks can't be told
# from the floor's shadow) and uses a 3x longer lens (the sheet's cells are drawn almost orthographic)
SHEET_VIEWS = {"f34_sheet": (0, 14), "front_sheet": (0, 10), "side_sheet": (90, 10), "rear_sheet": (180, 10),
               "r34_sheet": (152, 12), "top_tilt_sheet": (0, 75)}
SHEET_LENS = 3.0
PARTS_SHOT = (-20, 15)


def _long_lens(kit):
    orig = kit["render_group"]

    def rg(group, path, azimuth=-22, elevation=20):
        cam = bpy.data.objects["FB_Cam"].data
        lens = cam.lens
        ground = bpy.data.objects.get("FB_Ground")
        hid = ground.hide_render if ground else None
        if "_sheet" in path:
            cam.lens = lens * SHEET_LENS
            if ground:
                ground.hide_render = True
        try:
            return orig(group, path, azimuth, elevation)
        finally:
            cam.lens = lens
            if ground:
                ground.hide_render = hid
    return orig, rg


# the exploded shot as the sheet lays it out (studs from the mound centre; x right, z up): the mound at the bottom,
# five rocks round it, eight leaves fanned above, three stalks, three heads on top. (part, location, rot Y deg,
# mirror, scale)
EXPL = (("ReedClumpMudBase", (0.0, 0.0, 0.0), 0, False, 1.0),
        ("ReedClumpRock", (-2.5, -0.3, 0.5), 0, False, 0.95), ("ReedClumpRock", (-2.3, -1.3, -0.1), 0, False, 1.2),
        ("ReedClumpRock", (1.3, -1.1, 0.35), 0, False, 0.6), ("ReedClumpRock", (2.4, -0.7, 0.5), 0, False, 0.8),
        ("ReedClumpRock", (2.0, -1.6, -0.1), 0, False, 1.15),
        ("ReedClumpLeafBlade", (-2.9, 0.0, 1.5), -20, True, 1.1),
        ("ReedClumpLeafBlade", (-1.9, 0.0, 2.5), -8, True, 1.05),
        ("ReedClumpLeafBlade", (-0.6, 0.0, 1.2), -15, False, 0.9),
        ("ReedClumpLeafBlade", (-0.1, 0.0, 1.3), 25, True, 1.0),
        ("ReedClumpLeafBlade", (0.2, -0.2, 1.1), 20, True, 0.75),
        ("ReedClumpLeafBlade", (0.6, 0.0, 1.25), 10, False, 0.9),
        ("ReedClumpLeafBlade", (1.7, 0.0, 2.3), -5, False, 1.0),
        ("ReedClumpLeafBlade", (2.6, 0.0, 1.4), -25, False, 1.05),
        ("ReedClumpStalk", (-1.0, 0.0, 3.7), -12, False, 0.55), ("ReedClumpStalk", (0.0, 0.0, 3.8), 0, False, 0.55),
        ("ReedClumpStalk", (1.0, 0.0, 3.6), 14, False, 0.55),
        ("ReedClumpSeedHead", (-1.3, 0.0, 5.3), -12, False, 1.0),
        ("ReedClumpSeedHead", (0.0, 0.0, 5.5), 0, False, 1.0),
        ("ReedClumpSeedHead", (1.3, 0.0, 5.2), 14, False, 1.0))


EXPL_VIEW = (-12, 14)
EXPL_FACE = {}         # exploded leaf copy -> (yaw added, face score before, after)


def _face_score(me, m3, d):
    """Area-weighted |n . d| over a mesh's faces under the 3x3 matrix m3 (how broad it reads from direction d)."""
    nm = m3.inverted().transposed()
    tot = s = 0.0
    for p in me.polygons:
        n = (nm @ p.normal).normalized()
        tot += p.area
        s += p.area * abs(n.dot(d))
    return s / max(tot, 1e-9)


def _expl_matrix(loc, ry, mirror, sc, yaw=0.0):
    return (Matrix.Translation(Vector(loc)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @
            Matrix.Rotation(math.radians(ry), 4, "Y") @ Matrix.Diagonal((-sc if mirror else sc, sc, sc, 1.0)))


def render_views(objs):
    h = objs[0]
    by = {o.name: o for o in objs}
    shown = []
    az, el = (math.radians(x) for x in EXPL_VIEW)
    cam = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    try:
        if len(objs) > 1:
            base = Vector((h.location.x + 40, h.location.y, 0.0))
            EXPL_FACE.clear()
            for k, (part, loc, ry, mirror, sc) in enumerate(EXPL):
                c = bpy.data.objects.new(f"{PFX}expl_{k}", by[part].data)
                by[part].users_collection[0].objects.link(c)
                yaw = 0.0
                if part == "ReedClumpLeafBlade":
                    # round 2 (verifier minor): turn each leaf copy about Z (at most 40 deg) so its broad face
                    # points at the exploded camera, as the sheet draws them (several read edge-on before)
                    me = by[part].data
                    sc0 = _face_score(me, _expl_matrix(loc, ry, mirror, sc).to_3x3(), cam)
                    yaw = max(range(-40, 41, 5),
                              key=lambda y: _face_score(me, _expl_matrix(loc, ry, mirror, sc, y).to_3x3(), cam))
                    EXPL_FACE[k] = (yaw, round(sc0, 3), round(_face_score(
                        me, _expl_matrix(loc, ry, mirror, sc, yaw).to_3x3(), cam), 3))
                c.matrix_world = Matrix.Translation(base) @ _expl_matrix(loc, ry, mirror, sc, yaw)
                shown.append(c)
            bpy.context.view_layer.update()
        extra = {k: ([h], az_, el_) for k, (az_, el_) in SHEET_VIEWS.items()}
        if shown:
            extra["exploded"] = (shown, *EXPL_VIEW)
        for o in objs[1:]:
            extra["part_" + o.name.replace("ReedClump", "").lower()] = ([o], *PARTS_SHOT)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = _long_lens(kit)
        try:
            return M.views(NUM, [h], extra=extra)
        finally:
            kit["render_group"] = orig
    finally:
        for c in shown:
            bpy.data.objects.remove(c, do_unlink=True)
        M.display(NUM, objs, TITLE)


# ---- measuring (the study's m.py masks, numpy) -----------------------------------------------------------------------
REF_VIEWS = {"f34": (30, 120, 498, 492), "r34": (500, 120, 808, 492), "front": (22, 536, 288, 772),
             "side": (293, 536, 490, 772), "rear": (495, 536, 746, 772), "top": (752, 536, 1005, 772)}
OUR_VIEWS = {"f34": "f34_sheet", "front": "front_sheet", "side": "side_sheet", "rear": "rear_sheet",
             "r34": "r34_sheet", "top": "top_tilt_sheet"}


def _hsv(a):
    a = a / 255.0
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-9), 0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    dd = np.maximum(d, 1e-9)
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60
    return np.where(d == 0, 0, h), s, mx


def _cls(a, elev=True, split=0.42, paper=None):
    """G green (leaves + stalks), S seed heads incl. nubs, M mud, R rock (the study's cls(); the ground shadow is
    background)."""
    if paper is None:
        paper = np.median(np.concatenate([a[:4].reshape(-1, 3), a[-4:].reshape(-1, 3)]), 0)
    h, s, v = _hsv(a)
    bg = np.abs(a - paper).max(-1) <= 18
    G = (~bg) & (s >= 0.25) & (h >= 55) & (h <= 165) & (a[..., 1] > 35)
    B = (~bg) & (((h >= 5) & (h <= 45)) | (h >= 340)) & (s >= 0.28) & ~G
    Rk = (~bg) & (s < 0.28) & (v < 0.80) & ~G & ~B
    if elev:
        fg = G | B | Rk
        yi = np.nonzero(fg.sum(1) >= 2)[0]
        y0, y1 = yi[0], yi[-1]
        cut = int(y1 - split * (y1 - y0 + 1))
        rows = np.arange(a.shape[0])[:, None]
        S, Mm, R = B & (rows < cut), B & (rows >= cut), Rk & (rows >= cut)
    else:
        S = B & (s >= 0.48) & (v >= 0.60)
        Mm, R = B & ~S, Rk
    return G, S, Mm, R


def _hexs(c):
    return "#" + "".join(f"{int(round(x)):02X}" for x in c)


def _runs(row, W, minw=2):
    seg, start = [], None
    for x in range(len(row) + 1):
        on = x < len(row) and row[x]
        if on and start is None:
            start = x
        if not on and start is not None:
            if x - start >= minw:
                seg.append((round(start / W, 2), round(x / W, 2)))
            start = None
    return seg


def view_stats(a, elev=True):
    G, S, Mm, R = _cls(a, elev)
    fg = G | S | Mm | R
    xi = np.nonzero(fg.sum(0) >= 2)[0]
    yi = np.nonzero(fg.sum(1) >= 2)[0]
    x0, x1, y0, y1 = xi[0], xi[-1], yi[0], yi[-1]
    W, H = x1 - x0 + 1, y1 - y0 + 1
    n = max(1, fg[y0:y1 + 1, x0:x1 + 1].sum())
    out = {"wh": round(W / H, 3)}
    for k, m in (("G", G), ("S", S), ("M", Mm), ("R", R)):
        out[k] = round(m[y0:y1 + 1, x0:x1 + 1].sum() / n * 100, 1)
    tp = []
    for i in range(21):
        c = int(x0 + min(i / 20, 0.999) * W)
        col = fg[y0:y1 + 1, max(c - 1, x0):c + 2].any(1)
        idx = np.nonzero(col)[0]
        tp.append(round(1 - idx[0] / H, 2) if len(idx) else 0)
    out["top"] = tp
    ws = []
    for i in range(11):
        r = int(y1 - min(i / 10, 0.999) * (H - 1))
        row = fg[r - 1:r + 2, x0:x1 + 1].any(0)
        idx = np.nonzero(row)[0]
        ws.append(f"{(idx[-1] - idx[0] + 1) / W:.2f}@{idx[0] / W:.2f}" if len(idx) else "-")
    out["wph"] = " ".join(ws)
    for hh in (0.55, 0.50, 0.40):
        r = int(y1 - hh * (H - 1))
        out[f"green_{hh}"] = _runs(G[r, x0:x1 + 1], W)
    r = int(y1 - 0.16 * (H - 1))
    out["rocks_0.16"] = _runs(R[r, x0:x1 + 1], W, 3)
    sub = a[y0:y1 + 1, x0:x1 + 1]
    for k, m in (("G", G), ("S", S), ("M", Mm), ("R", R)):
        p = sub[m[y0:y1 + 1, x0:x1 + 1]]
        if len(p) > 20:
            lum = p @ np.array([.299, .587, .114])
            o = np.argsort(lum)
            out[k + "hex"] = [_hexs(np.median(p, 0)), _hexs(np.median(p[o[int(.75 * len(o)):]], 0)),
                              _hexs(np.median(p[o[:int(.25 * len(o))]], 0))]
    bands = []
    for i in range(10):
        r0, r1 = int(y1 + 1 - (i + 1) / 10 * H), int(y1 + 1 - i / 10 * H)
        p = a[r0:r1, x0:x1 + 1][G[r0:r1, x0:x1 + 1]]
        bands.append(_hexs(np.median(p, 0)) if len(p) > 20 else "-")
    out["Gbands"] = bands
    return out


def _img(path, box=None):
    px = K.NS["KIT"]["load_px"](path)[::-1, :, :3] * 255.0
    px = np.clip(px, 0, 255).astype(np.int32)
    if box:
        x0, y0, x1, y1 = box
        px = px[y0:y1, x0:x1]
    return px


def measure(views=("f34", "front", "side", "rear", "r34", "top")):
    """Sheet against our renders per view (the study's masks on both; our renders hide the floor)."""
    out = {}
    for v in views:
        a = view_stats(_img(M.ref(NUM), REF_VIEWS[v]), elev=(v != "top"))
        b = view_stats(_img(f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[v]}.png"), elev=(v != "top"))
        err = [abs(x - y) for x, y in zip(a["top"], b["top"])]
        out[v] = {"sheet": a, "ours": b, "prof_err_mean_max": (round(sum(err) / len(err), 3), round(max(err), 2))}
    return out


def leaf_tips(a, r=0.06):
    """Median colour of the green pixels within r x W of three leaf tips in an f34-type view: LA (the leftmost green
    pixel), LH (the rightmost below h .55) and LG (the green pixel with the largest f + h above h .55)."""
    G, S, Mm, R = _cls(a)
    fg = G | S | Mm | R
    xi, yi = np.nonzero(fg.sum(0) >= 2)[0], np.nonzero(fg.sum(1) >= 2)[0]
    x0, x1, y0, y1 = xi[0], xi[-1], yi[0], yi[-1]
    W, H = x1 - x0 + 1, y1 - y0 + 1
    ys, xs = np.nonzero(G)
    f, h = (xs - x0) / W, (y1 - ys) / H
    pick = {"LA": np.argmin(f), "LH": np.argmax(np.where(h < 0.55, f, -9)), "LG": np.argmax(np.where(h > 0.55, f + h, -9))}
    out = {}
    for k, i in pick.items():
        m = (xs - xs[i]) ** 2 + (ys - ys[i]) ** 2 <= (r * W) ** 2
        out[k] = dict(at=(round(float(f[i]), 2), round(float(h[i]), 2)), hex=_hexs(np.median(a[ys[m], xs[m]], 0)))
    return out


def leaf_fifths(a):
    """Base -> tip medians in five equal steps along a single leaf's long axis (PCA of its green pixels); the tip is
    the end higher in the image."""
    G = _cls(a, elev=False)[0]
    ys, xs = np.nonzero(G)
    P = np.stack([xs, ys], 1).astype(float)
    c = P.mean(0)
    w, V = np.linalg.eigh(np.cov((P - c).T))
    ax = V[:, -1]
    s = (P - c) @ ax
    if ys[np.argmax(s)] > ys[np.argmin(s)]:      # the tip is the upper end
        s = -s
    lo, hi = s.min(), s.max()
    out = []
    for k in range(5):
        m = (s >= lo + (hi - lo) * k / 5) & (s <= lo + (hi - lo) * (k + 1) / 5)
        out.append(_hexs(np.median(a[ys[m], xs[m]], 0)))
    return out


EXPL_LEAF_BOX = (77, 1095, 209, 1262)          # the sheet's far-left exploded leaf (unshadowed)


def tips():
    """Leaf-tip colours (f34) and the parts-shot leaf's base -> tip fifths, ours against the sheet."""
    ref = _img(M.ref(NUM))
    rd = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    return {"f34": {"sheet": leaf_tips(_img(M.ref(NUM), REF_VIEWS["f34"])), "ours": leaf_tips(_img(f"{rd}/f34_sheet.png"))},
            "part": {"sheet": leaf_fifths(ref[EXPL_LEAF_BOX[1]:EXPL_LEAF_BOX[3], EXPL_LEAF_BOX[0]:EXPL_LEAF_BOX[2]]),
                     "ours": leaf_fifths(_img(f"{rd}/part_leafblade.png"))}}


def _fit(px, h):
    ys = (np.arange(h) * px.shape[0] / h).astype(int)
    w = max(1, int(round(px.shape[1] * h / px.shape[0])))
    xs = (np.arange(w) * px.shape[1] / w).astype(int)
    return px[ys][:, xs]


def _crop_obj(px, pad=0.06):
    """Crop a bottom-up RGBA image to its object silhouette (+pad)."""
    top = np.clip(px[::-1, :, :3] * 255.0, 0, 255)
    G, S, Mm, R = _cls(top, elev=False)
    obj = G | S | Mm | R
    ys, xs = np.nonzero(obj)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    p = int(pad * max(y1 - y0, x1 - x0))
    H, W = obj.shape
    y0, y1, x0, x1 = max(0, y0 - p), min(H, y1 + p), max(0, x0 - p), min(W, x1 + p)
    return px[H - y1:H - y0, x0:x1]


def compare(views=("f34", "front", "side", "rear", "r34", "top"), h=360):
    """Sheet cell (left) beside our render (right), each cropped to the silhouette and scaled to the same height; one
    row per view -> M027_sheet_compare.png."""
    kit = K.NS["KIT"]
    ref = kit["load_px"](M.ref(NUM))
    H = ref.shape[0]
    rows = []
    for v in views:
        x0, y0, x1, y1 = REF_VIEWS[v]
        a = _fit(_crop_obj(ref[H - y1:H - y0, x0:x1]), h)
        b = _fit(_crop_obj(kit["load_px"](f"{M.MODEL_RENDERS}/{M.code(NUM)}/{OUR_VIEWS[v]}.png")), h)
        gap = np.ones((h, 20, 4), np.float32)
        rows.append(np.concatenate([a, gap, b], axis=1))
    w = max(r.shape[1] for r in rows)
    rows = [np.concatenate([r, np.ones((r.shape[0], w - r.shape[1], 4), np.float32)], axis=1) if r.shape[1] < w
            else r for r in rows]
    out = f"{M.MODEL_RENDERS}/{M.code(NUM)}/{M.code(NUM)}_sheet_compare.png"
    kit["save_px"](kit["vstack"](rows), out)
    return out
