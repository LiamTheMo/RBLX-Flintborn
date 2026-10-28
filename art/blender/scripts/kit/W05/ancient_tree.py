"""W05 row 2: Ancient Tree, a massive old broadleaf with buttress roots and a high crown.

Assets
  AncientTree              hero: fluted ~9-dia trunk on 7 wedge buttress roots, 7 angular
                           branches at 16-23 studs carrying a ring of 7 lumpy leaf clumps
                           (open centre: the branches read as a star from above), lime moss
                           strands hanging under the branches, moss on the roots, base
                           dressing (moss ground patch, grey rocks, grass, moss mounds)
                           (~28 x 28 x 34)
  AncientCrownModule       part: one big clump on a short forked branch stub (~9 x 9 x 8)
  AncientBranchModule      part: ~13-stud angular branch, upturned fork and a side stub
  AncientTrunkCore         part: fluted trunk section ~9 dia x 12 with a ragged cut top
  AncientRootModuleA/B/C   part: buttress roots (long swept / short steep / kinked with a
                           split tip), each ending in a flat sloped attach face
  AncientTreeHollowTrunk   variant: walk-in arched cave at the trunk base (-Y), dark cavity
  AncientTreeForkedGiant   variant: trunk splits at ~13 studs into two leaders in a V
  AncientTreeResinBearing  variant: glowing amber resin runs down the front/right into a pool

Shape language: everything is flat-shaded big facets. The trunk is a ring tube with 9
flutes (4 verts per flute: ridge plane, shoulder, a narrow V groove). Every material has ONE
palette key (bark w05_bark, leaves w05_leaf, moss w05_moss, grass w05_grass, cut wood
w05_heartwood, cavities w05_hollow, resin w05_resin, rocks kit_rock) with only a small random
Tint; the light and dark sides come from the facets and the light. Buttress roots are thick
chiselled 8-sided root logs (big and smaller ones alternating) that climb 7-9 studs up the
trunk and fall in a bell to a long low ridge and a tip ~13 out that curls sideways (some
split off a twisting finger root). Leaf clumps are cauliflower clusters of ~28 randomly
tumbled icosphere puffs around a core with a heaped top tier; their inner sides are thinned
so the open crown centre shows the 7-arm branch star. Faces buried inside another puff are
culled. Dressing faces (grass, moss mounds/strands, ground patch, small rocks) carry
the face attribute kit_nocollide = 1 so an exporter can split them off as walk-through.

The Hollow Trunk opening is cut with an exact boolean (cavity cylinder + arch prism) from
a closed trunk, then the cut faces are repainted near-black (w05_hollow) inside and
w05_heartwood on the arch reveal.
"""

import json
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

SUBJECT = "AncientTree"
ROW = 2
# Shared W05 sheet palette (verbatim, identical in every W05 module). kit_rock is an
# existing KIT_PALETTE key and is not redeclared. ONE key per material: the light and
# dark sides in the reference are lighting, so nothing here is picked by face direction.
PALETTE = {
    "w05_leaf": ("#9CBB1C", 0.8, 0, 0),
    "w05_moss": ("#C6CB1F", 0.9, 0, 0),
    "w05_grass": ("#86AC22", 0.95, 0, 0),
    "w05_bark": ("#A5653A", 0.9, 0, 0),
    "w05_heartwood": ("#F0B26E", 0.85, 0, 0),
    "w05_hollow": ("#1C130F", 0.95, 0, 0),
    "w05_resin": ("#F59A16", 0.25, 0, 1.2),
    # The sheet's w05_resin (#F59A16) at emission 1.2 renders lemon yellow; the reference's
    # resin runs are orange-amber. This module's resin uses this one deeper amber key
    # instead (w05_resin is kept verbatim for the other W05 modules, unused here).
    "w05_amber": ("#E0600A", 0.25, 0, 1.2),
}

PI = math.pi
TAU = 2 * PI
Z = Vector((0, 0, 1))
CAT = "Kit W05 AncientTree"
# Parts whose cut end faces up: the pale w05_heartwood cut face vs the w05_bark sides is a
# real material change (sawn/broken wood), not painted lighting; bark itself is one colour.
CUT_OK = "w05_heartwood cut/attach face on top vs w05_bark sides: a real material change, bark is one key"
LEAF, MOSS, GRASS, BARK, HEART, HOLLOW, RESIN, ROCK = (
    "w05_leaf", "w05_moss", "w05_grass", "w05_bark", "w05_heartwood", "w05_hollow", "w05_amber", "kit_rock")


def dirxy(az):
    return Vector((math.cos(az), math.sin(az), 0.0))


def rad(d):
    return math.radians(d)


# ---------------------------------------------------------------------------
# Asset + painting
# ---------------------------------------------------------------------------


def new_asset(kit, name, seed):
    a = kit.flintkit.Asset(name, CAT, seed=seed)
    a.nc = a.bm.faces.layers.int.new("kit_nocollide")
    a.dress = False
    a.blobs = []        # (centre, rx, rz) culling ellipsoids of the leaf blobs
    a.cullable = []     # faces that may be hidden inside a blob
    return a


def put(a, f, mat, tint=1.0):
    f.material_index = a._mi(mat)
    f.smooth = False
    for lp in f.loops:
        lp[a.tint_layer] = (tint, tint, tint, 1.0)
    f[a.nc] = 1 if a.dress else 0


class dressing:
    """with dressing(a): faces made inside are walk-through scatter (kit_nocollide=1)."""

    def __init__(self, a):
        self.a = a

    def __enter__(self):
        self.a.dress = True

    def __exit__(self, *exc):
        self.a.dress = False


# Colour is the MATERIAL only (one key each); a small random Tint per face or per piece
# is the only variation. Flutes and grooves are real geometry, shaded by the light.
def tint(a, var=0.04):
    return a.rng.uniform(1 - var, 1 + var)


def bark(a, f, var=0.04):
    put(a, f, BARK, tint(a, var))


def recalc(a, faces):
    faces = [f for f in faces if f.is_valid]
    if faces:
        bmesh.ops.recalc_face_normals(a.bm, faces=faces)
    return faces


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------


def frames(pts):
    n = len(pts)
    tans = [(pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized() for i in range(n)]
    up = Z if abs(tans[0].z) < 0.9 else Vector((1, 0, 0))
    nrm = tans[0].cross(up).normalized()
    out = []
    for i in range(n):
        if i:
            axis = tans[i - 1].cross(tans[i])
            if axis.length > 1e-6:
                nrm = Matrix.Rotation(tans[i - 1].angle(tans[i]), 3, axis.normalized()) @ nrm
            nrm = (nrm - tans[i] * nrm.dot(tans[i])).normalized()
        out.append((tans[i], nrm, tans[i].cross(nrm)))
    return out


def fluted(a, pts, radii, flutes=9, twist=0.05, phase=0.0, rough=0.06, top="cone", top_h=1.6,
           bottom=False, groove=0.64, shoulder=0.87, ridge_var=0.12, top_jag=0.0, bm=None,
           paint=True):
    """Fluted trunk tube along pts: each flute is a flat chiselled ridge plane, a shoulder
    and a deep V groove (5 verts). Returns (rings, faces, grooves, caps)."""
    bm = bm or a.bm
    pts = [Vector(p) for p in pts]
    fr = frames(pts)
    U = (0.0, 0.24, 0.4, 0.52, 0.64)
    K = (1.0, 1.0, shoulder, groove, shoulder)
    NV = len(U)
    rv = [1 + a.rng.uniform(-ridge_var, ridge_var) for _ in range(flutes)]
    rings = []
    for i, (t, n, b) in enumerate(fr):
        ring = []
        for j in range(flutes):
            for q, (u, k) in enumerate(zip(U, K)):
                th = TAU * (j + u) / flutes + twist * i + phase
                rr = radii[i] * k * (rv[j] if q < 2 else 1 + (rv[j] - 1) * 0.5)
                rr *= 1 + a.rng.uniform(-rough, rough)
                p = pts[i] + rr * (math.cos(th) * n + math.sin(th) * b)
                if top_jag and i == len(fr) - 1:
                    p = p + t * a.rng.uniform(-top_jag, top_jag * 0.6)
                ring.append(bm.verts.new(p))
        rings.append(ring)
    S = NV * flutes
    faces, grooves, caps = [], set(), []
    for i in range(len(rings) - 1):
        for j in range(S):
            k = (j + 1) % S
            f = bm.faces.new((rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]))
            faces.append(f)
            if j % NV in (2, 3):
                grooves.add(f)
    t_end = fr[-1][0]
    if top == "cone":
        apex = bm.verts.new(pts[-1] + t_end * top_h)
        for j in range(S):
            caps.append(bm.faces.new((rings[-1][j], rings[-1][(j + 1) % S], apex)))
    elif top == "flat":
        caps.append(bm.faces.new(rings[-1]))
    if bottom:
        caps.append(bm.faces.new(list(reversed(rings[0]))))
    allf = faces + caps
    if bm is a.bm:
        recalc(a, allf)
    else:
        bmesh.ops.recalc_face_normals(bm, faces=allf)
    if paint and bm is a.bm:
        for f in faces + caps:
            bark(a, f)
    return rings, faces, grooves, caps


def limb(a, pts, radii, sides=6, cap_end="cone", cap_start=False, end_mat=None, twist=0.4,
         jitter=0.05, cull=True):
    """Angular faceted branch along a polyline. cap_end: cone | flat | None."""
    bm = a.bm
    pts = [Vector(p) for p in pts]
    fr = frames(pts)
    ph = a.rng.uniform(0, TAU)
    rings = []
    for i, (t, n, b) in enumerate(fr):
        ring = []
        for j in range(sides):
            th = TAU * j / sides + ph + twist * i
            rr = radii[i] * (1 + a.rng.uniform(-jitter, jitter))
            ring.append(bm.verts.new(pts[i] + rr * (math.cos(th) * n + math.sin(th) * b)))
        rings.append(ring)
    body, ends = [], []
    for i in range(len(rings) - 1):
        for j in range(sides):
            k = (j + 1) % sides
            body.append(bm.faces.new((rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j])))
    if cap_end == "cone":
        apex = bm.verts.new(pts[-1] + fr[-1][0] * radii[-1] * 1.2)
        for j in range(sides):
            body.append(bm.faces.new((rings[-1][j], rings[-1][(j + 1) % sides], apex)))
    elif cap_end == "flat":
        ends.append(bm.faces.new(rings[-1]))
    if cap_start:
        ends.append(bm.faces.new(list(reversed(rings[0]))))
    recalc(a, body + ends)
    for f in body:
        bark(a, f)
    for f in ends:
        if end_mat:
            put(a, f, end_mat, tint(a, 0.03))
        else:
            bark(a, f)
    if cull:
        a.cullable += body + ends
    return rings, body, ends


def fin(a, path, heights, widths, bottom=False, start_slope=0.0, start_mat="w05_heartwood",
        start_cap=False, end_cap=True, moss=None, lean=0.15):
    """Buttress root: a lofted wedge fin along a ground path. moss=(i0, i1) paints the top
    faces of those segments moss. start_slope tilts the first section back (attach face)."""
    bm = a.bm
    path = [Vector(p) for p in path]
    n = len(path)
    secs = []
    for i, c in enumerate(path):
        t = (path[min(i + 1, n - 1)] - path[max(i - 1, 0)])
        t.z = 0
        t.normalize()
        sd = t.cross(Z).normalized()
        h, w = heights[i], widths[i]
        # chiselled breaks: the crest line and the shoulders wander a little per section
        cj = sd * (w * a.rng.uniform(-0.16, 0.16))
        pts = [c + sd * w,
               c + sd * w * a.rng.uniform(0.84, 0.96) + Z * h * a.rng.uniform(0.52, 0.64),
               c + sd * w * 0.4 + cj + Z * h,
               c - sd * w * 0.36 + cj + Z * h * a.rng.uniform(0.9, 0.98),
               c - sd * w * a.rng.uniform(0.82, 0.94) + Z * h * a.rng.uniform(0.48, 0.6),
               c - sd * w]
        if i == 0 and start_slope:
            pts = [p - t * (p.z * start_slope) for p in pts]
        secs.append([bm.verts.new(p) for p in pts])
    side, tops, caps, crest = [], [], [], set()
    for i in range(n - 1):
        s1, s2 = secs[i], secs[i + 1]
        for k in range(5):
            f = bm.faces.new((s1[k], s2[k], s2[k + 1], s1[k + 1]))
            (tops if k in (1, 2, 3) else side).append((i, f))
            if k == 2:  # the crest plane: where a moss streak settles on a root
                crest.add(f)
        if bottom:
            side.append((i, bm.faces.new((s1[5], s2[5], s2[0], s1[0]))))
    if end_cap:
        caps.append(("end", bm.faces.new(secs[-1])))
    if start_cap:
        caps.append(("start", bm.faces.new(list(reversed(secs[0])))))
    recalc(a, [f for _, f in side + tops] + [f for _, f in caps])
    for i, f in side + tops:
        if moss and moss[0] <= i <= moss[1] and f in crest:
            put(a, f, MOSS, tint(a, 0.03))  # a moss streak along the root crest
        else:
            bark(a, f)
    for kind, f in caps:
        if kind == "start":
            put(a, f, start_mat, tint(a, 0.03))
        else:
            bark(a, f)
    return secs


def root_path(az, s0, s1, sweep, n=7, wobble=0.0, rng=None):
    out = []
    for i in range(n):
        u = i / (n - 1)
        s = s0 + (s1 - s0) * u
        aa = az + sweep * u * u
        if wobble and rng:
            aa += rng.uniform(-wobble, wobble) * u
        out.append(Vector((s * math.cos(aa), s * math.sin(aa), 0.0)))
    return out


ROOT_H = [1.3, 1.0, 0.72, 0.48, 0.3, 0.17, 0.07]
ROOT_W = [1.0, 0.92, 0.8, 0.66, 0.52, 0.38, 0.22]
ROOT_S = [0.0, 0.17, 0.32, 0.48, 0.64, 0.82, 1.0]


def root_h(s, rb, reach, h0):
    """Crest height of a buttress at distance s (rb = trunk radius where it leaves the trunk):
    a concave bell, steep against the trunk and then long and low over the ground."""
    q = min(1.15, max(0.0, (reach - s) / (reach - rb)))
    # a full shoulder against the trunk (a deep wedge fin, not a thin bell) falling to a long
    # rounded ridge (~1.3 high) that stays readable far out before it tapers into the tip
    return h0 * q ** 1.25 + 2.0 * min(1.0, q * 3.0) * max(0.0, 1 - q * q) + 0.5


def buttress(a, az, rb, reach, h0, w0, sweep=0.15, moss=None, kink=0.0, finger=None):
    """A thick wedge buttress from inside the trunk to `reach`; h0 = its height where it
    leaves the trunk surface (radius rb), dropping in a concave bell to a long low tail,
    ~2*w0 thick at the trunk. kink bends the tail sideways (radians); finger=(side, len)
    splits off a thin twisting finger root near the tip."""
    us = (0.0, 0.1, 0.2, 0.31, 0.43, 0.56, 0.7, 0.85, 1.0)
    s0 = rb * 0.55
    path, hs, ws = [], [], []
    for u in us:
        s = s0 + (reach - s0) * u
        # the tail curls sideways (kink grows toward the tip), so the tips splay and twist
        aa = az + sweep * u * u + kink * max(0.0, u - 0.45) ** 1.5 * 3.3
        path.append(Vector((s * math.cos(aa), s * math.sin(aa), 0)))
        q = max(0.0, (reach - s) / (reach - rb))
        hs.append(root_h(s, rb, reach, h0) * a.rng.uniform(0.94, 1.06))
        ws.append(w0 * (0.5 + 0.5 * min(1.0, q)) * a.rng.uniform(0.93, 1.07))
    secs = root_log(a, path, hs, ws, moss=moss)
    if finger:
        side, L = finger
        i = 6
        p = path[i]
        t = (path[i + 1] - path[i - 1])
        t.z = 0
        t.normalize()
        sd = t.cross(Z) * side
        d1 = (t * 0.55 + sd * 0.85).normalized()
        d2 = (t * 0.9 + sd * 0.3).normalized()
        r0 = ws[i] * 0.5
        p0 = p + Z * (hs[i] * 0.45)
        p1 = p0 + d1 * L * 0.45 + Z * 0.15
        p2 = p1 + d2 * L * 0.55 - Z * (hs[i] * 0.35)
        limb(a, [p0, p1, p2], [r0, r0 * 0.75, r0 * 0.45], sides=5, cap_end="cone", cull=False)
    return secs


def root_log(a, path, hs, ws, moss=None, sides=8):
    """Buttress root as a thick chiselled log: an 8-sided elliptical tube along the ground
    path whose crest follows hs (tall against the trunk, a low rounded ridge far out) and
    half-width ws; it ends in a blunt cone tip. Round flanks give each root its own lit top
    and shadowed sides, with dark valleys between neighbours. The buried underside is
    flattened to z=0 by finish(). moss=(i0, i1): the crest plane of those segments is moss."""
    bm = a.bm
    n = len(path)
    rings = []
    for i, c in enumerate(path):
        t = (path[min(i + 1, n - 1)] - path[max(i - 1, 0)])
        t.z = 0
        t.normalize()
        sd = t.cross(Z).normalized()
        hh = max(0.45, hs[i] * 0.62)       # half-height of the section
        cz = hs[i] - hh                    # centre height (crest at hs[i])
        w = ws[i]
        ring = []
        for j in range(sides):
            th = TAU * (j + 0.5) / sides   # a flat crest plane on top (j = 1)
            k = 1 + a.rng.uniform(-0.07, 0.07)
            ring.append(bm.verts.new(c + sd * (w * math.cos(th) * k) + Z * (cz + hh * math.sin(th) * k)))
        rings.append(ring)
    body, crest = [], set()
    for i in range(n - 1):
        for j in range(sides):
            k = (j + 1) % sides
            f = bm.faces.new((rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]))
            body.append((i, f))
            if j == 1:  # the crest plane: a patchy moss streak settles there
                crest.add(f)
    tip_dir = (path[-1] - path[-2]).normalized()
    apex = bm.verts.new(path[-1] + tip_dir * ws[-1] * 1.3 + Z * 0.15)
    for j in range(sides):
        body.append((n - 1, bm.faces.new((rings[-1][j], rings[-1][(j + 1) % sides], apex))))
    recalc(a, [f for _, f in body])
    for i, f in body:
        if moss and moss[0] <= i <= moss[1] and f in crest:
            put(a, f, MOSS, tint(a, 0.03))  # patchy moss along the root crest
        else:
            bark(a, f)
    return rings


def blob(a, c, r, flat=0.85, jitter=0.06, subdiv=1, tumble=True):
    """One rounded leaf puff (an icosphere with a little jitter, so it reads round)."""
    rz = r * flat
    # random 3D orientation: no puff shows the icosphere's 5-fold pole cap, so the caps
    # read as rounded bumps rather than a row of identical gems
    rot = (a.rng.uniform(0, TAU), a.rng.uniform(0, TAU), a.rng.uniform(0, TAU)) if tumble and flat > 0.99         else (0, 0, a.rng.uniform(0, TAU))
    verts = a.ico((r, r, rz), c, rot=rot, mat=LEAF, subdiv=subdiv, jitter=jitter)
    faces = list({f for v in verts for f in v.link_faces})
    t = tint(a, 0.04)  # one small random tint per blob
    for f in faces:
        put(a, f, LEAF, t)
    # culling ellipsoid just inside the jittered surface: faces of OTHER pieces fully
    # inside it are hidden, the puff's own faces (verts >= ~0.94 r) never are
    k = 1 - jitter * 1.6
    a.blobs.append((Vector(c), r * k, rz * k))
    a.cullable += faces
    return faces


def clump(a, C, R, n, pr=(1.2, 2.0), flat=0.9, spread=1.0, axis=None, sr=1.0, st=1.0,
          lo=-0.6, inner=None, tier=5):
    """Cauliflower leaf clump of overall radius ~R: n small rounded puffs (radius pr, with
    a few bigger lobes) on a squashed shell, a few pushed out past the outline, around a
    core that fills the gaps, and a second tier of puffs heaped on the top (a taller,
    billowing head). With axis (the branch direction) the shell is scaled sr along it and
    st across it; inner (a dot threshold) drops the puffs on the side facing the tree
    centre, so the crown's open centre shows the branch star from above."""
    # Rev 6: the shared canopy helper (overlapping multi-lobed leaf clusters) gives the
    # reference's dense, lumpy cauliflower head; one random Tint per cluster, one key.
    C = Vector(C)
    k = min(sr, st) if axis is not None else 1.0
    w = 2 * R * 0.98 * spread
    hgt = 2 * R * flat * 1.32
    cnt = max(5, min(9, int(round(n / 4.6))))
    # few BIG overlapping lobed clusters: a dense billowing head, no gaps
    a.canopy((C.x, C.y, C.z + R * 0.15), (w, w, hgt), mat=LEAF, clumps=cnt,
             clump_radius=(R * 0.52, R * 0.7), facets=1, core=False, inner=False,
             seed=a.rng.randrange(1 << 30), bulge=0.4, tilt=0.5, depth=0.85,
             lobes=(6, 7), droop=0.35, flat_bottom=1.0)
    return


def strand(a, top, L, th=0.3, rng=None, face=None):
    """Hanging moss strand: a broad flattened 4-sided ribbon (~2*th wide, half as deep)
    that bends as it hangs and tapers to a blunt tip. face = the direction it faces."""
    rng = rng or a.rng
    bm = a.bm
    top = Vector(top)
    face = Vector(face) if face is not None else dirxy(rng.uniform(0, TAU))
    face.z = 0
    face.normalize()
    side = face.cross(Z)
    sw = face * rng.uniform(0.25, 0.55) + side * rng.uniform(-0.35, 0.35)
    fr = (0.0, 0.3, 0.6, 0.85)
    bend = (0.0, 0.35, 0.8, 1.0)
    pts = [top + Vector((0, 0, -L * f)) + sw * b for f, b in zip(fr, bend)]
    tip = top + Vector((0, 0, -L)) + sw * 1.15
    rings = []
    for i, p in enumerate(pts):
        # a fat tapered square-ish prism (reads from the front AND the side)
        w = th * (1.0 - 0.18 * i)
        d = th * 0.85 * (1.0 - 0.18 * i)
        rings.append([bm.verts.new(p + side * (w * sx) + face * (d * sy))
                      for sx, sy in ((1, 0), (0, 1), (-1, 0), (0, -1))])
    tv = bm.verts.new(tip)
    faces = []
    for i in range(len(rings) - 1):
        for j in range(4):
            k = (j + 1) % 4
            faces.append((i, bm.faces.new((rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]))))
    for j in range(4):
        faces.append((3, bm.faces.new((rings[-1][j], rings[-1][(j + 1) % 4], tv))))
    recalc(a, [f for _, f in faces])
    with dressing(a):
        t = tint(a, 0.04)
        for i, f in faces:
            put(a, f, MOSS, t)
        # a soft moss drape where the strand hangs from the wood, and a drooping blob tip
        for c, rad3 in ((top + Vector((0, 0, th * 0.6)), (th * 2.4, th * 2.4, th * 1.5)),):
            v = a.ico(rad3, c, mat=MOSS, subdiv=0, jitter=0.08)
            for f in {f for vv in v for f in vv.link_faces}:
                put(a, f, MOSS, t)


# ---------------------------------------------------------------------------
# Base dressing
# ---------------------------------------------------------------------------



def stone(a, loc, s, solid=False):
    loc = Vector(loc)
    size = (s * a.rng.uniform(1.0, 1.3), s * a.rng.uniform(0.85, 1.1), s * a.rng.uniform(0.75, 1.0))
    a.dress = not solid
    verts = a.rock(size, (loc.x, loc.y, 0.0), rot=(0, 0, a.rng.uniform(0, TAU)), mat=ROCK,
                   subdiv=1, rough=0.1, facets=10, sink=0.15)
    faces = list({f for v in verts for f in v.link_faces})
    t = tint(a, 0.04)
    for f in faces:
        put(a, f, ROCK, t)
    a.dress = False


def tuft(a, loc, s=1.0, blades=6):
    """Spiky grass tuft: thin 3-sided blades fanning out (w05_grass)."""
    bm = a.bm
    loc = Vector(loc)
    with dressing(a):
        t = tint(a, 0.04)
        for i in range(blades):
            az = TAU * i / blades + a.rng.uniform(-0.4, 0.4)
            base = loc + dirxy(az) * a.rng.uniform(0.05, 0.25) * s
            h = s * a.rng.uniform(0.9, 1.6)
            tip = base + dirxy(az) * h * a.rng.uniform(0.3, 0.55) + Z * h
            r = 0.17 * s
            bv = [bm.verts.new(base + Vector((r * math.cos(az + TAU * k / 3), r * math.sin(az + TAU * k / 3), 0)))
                  for k in range(3)]
            tv = bm.verts.new(tip)
            fs = [bm.faces.new((bv[k], bv[(k + 1) % 3], tv)) for k in range(3)]
            recalc(a, fs)
            for f in fs:
                put(a, f, GRASS, t)


def mound(a, loc, r, h=None):
    h = h or r * 0.55
    with dressing(a):
        v = a.ico((r, r * 0.9, h), (loc[0], loc[1], loc[2] if len(loc) > 2 else 0.1), mat=MOSS,
                  subdiv=0, jitter=0.12, rot=(0, 0, a.rng.uniform(0, TAU)))
        t = tint(a, 0.04)
        for f in {f for vv in v for f in vv.link_faces}:
            put(a, f, MOSS, t)


def moss_pad(a, loc, r, h=0.3, n=7):
    """An irregular low moss tuft on the ground (w05_moss, walk-through)."""
    bm = a.bm
    cx, cy = loc
    ph = a.rng.uniform(0, TAU)
    rim, top = [], []
    for i in range(n):
        th_ = TAU * i / n + ph
        rr = r * a.rng.uniform(0.6, 1.1)
        rim.append(bm.verts.new((cx + rr * math.cos(th_), cy + rr * math.sin(th_), 0.0)))
        top.append(bm.verts.new((cx + rr * 0.62 * math.cos(th_), cy + rr * 0.62 * math.sin(th_),
                                 h * a.rng.uniform(0.75, 1.25))))
    with dressing(a):
        t = tint(a, 0.04)
        fs = [bm.faces.new(top)]
        for i in range(n):
            j = (i + 1) % n
            fs.append(bm.faces.new((rim[i], rim[j], top[j], top[i])))
        recalc(a, fs)
        for f in fs:
            put(a, f, MOSS, t)


def dress_base(a, R, root_az, stones, tufts=10, mounds=5, skip=None, rb=6.5):
    """Moss tufts between the roots, rocks (az deg, dist, size) clustered at the root
    tips, grass tufts and moss mounds nestled against the roots (all walk-through)."""
    for az, d, s in stones:
        th = rad(az)
        stone(a, (d * math.cos(th), d * math.sin(th)), s)
    gaps = sorted(root_az)
    mids = [(gaps[i] + (gaps[(i + 1) % len(gaps)] + (360 if i == len(gaps) - 1 else 0))) / 2
            for i in range(len(gaps))]
    for m in mids:
        if skip and skip(m):
            continue
        for k in range(2):
            d = rb + a.rng.uniform(0.8, 2.2) + k * a.rng.uniform(2.0, 3.2)
            az = rad(m + a.rng.uniform(-9, 9))
            moss_pad(a, (d * math.cos(az), d * math.sin(az)), a.rng.uniform(1.4, 2.1) * (1 - 0.25 * k))
    for i in range(tufts):
        # tufts sit beside a root, against its flank
        g = gaps[i % len(gaps)]
        side = 1 if i % 2 else -1
        d = a.rng.uniform(rb + 1.5, R * 0.95)
        az = g + side * math.degrees(math.atan2(a.rng.uniform(1.3, 2.4), d))
        if skip and skip(az):
            continue
        tuft(a, (d * math.cos(rad(az)), d * math.sin(rad(az)), 0.1), s=a.rng.uniform(1.2, 2.0), blades=7)
    for i in range(mounds):
        g = gaps[(i * 3) % len(gaps)]
        side = -1 if i % 2 else 1
        d = a.rng.uniform(rb + 1.0, rb + 4.0)
        az = g + side * math.degrees(math.atan2(a.rng.uniform(1.6, 2.2), d))
        if skip and skip(az):
            continue
        mound(a, (d * math.cos(rad(az)), d * math.sin(rad(az)), 0.15), a.rng.uniform(1.0, 1.5))


# ---------------------------------------------------------------------------
# Tree assembly
# ---------------------------------------------------------------------------


def trunk_r(prof, z):
    """Outer radius of a trunk profile [(z, r), ...] at height z."""
    for (z0, r0), (z1, r1) in zip(prof, prof[1:]):
        if z0 <= z <= z1:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return prof[-1][1] if z > prof[-1][0] else prof[0][1]


def arm(a, prof, az, zb, ring, zc, R, n, out=None, strands=(), rbr=1.1, spread=0.68, inner=-0.82):
    """A branch from the trunk at zb out along az, turning up into a clump at
    (ring, zc) of radius R; strands = [(frac along the elbow, length)]."""
    d = dirxy(rad(az))
    rt = trunk_r(prof, zb)
    elbow = out if out is not None else ring * 0.6
    p0 = d * 0.4 + Z * max(zb + 0.4, prof[-1][0] + 0.2)  # arms meet over the hub: a 7-arm star from above
    p1 = d * (rt + 0.6) + Z * (zb + 0.1)
    # an angular diagonal: out and up from the trunk, a kink, then up into the clump
    p2 = d * max(elbow, rt + 2.4) + Z * (zb + 0.3 * (zc - zb))
    p3 = d * (ring * 0.9) + Z * (zc - R * 0.35)
    limb(a, [p0, p1, p2, p3], [rbr * 1.15, rbr, rbr * 0.8, rbr * 0.55], sides=6, cap_end="cone")
    C = d * ring + Z * zc
    # a big cauliflower clump of many small puffs with a heaped second tier; its inner side
    # is thinned so the open centre shows the branch star, and it is a little narrower
    # across than its neighbours' spacing so clefts stay between the seven clumps
    clump(a, C, R, n, axis=d, sr=0.8, st=0.8, lo=-0.75, inner=inner)
    side = d.cross(Z)
    for k, (frac, L) in enumerate(strands):
        if frac <= 1:  # under the branch elbow
            strand(a, p1.lerp(p2, frac) - Z * (rbr * 0.75), L, th=0.36, face=d)
        else:  # from the clump's lower rim, toward its outer edge, so it hangs in view
            off = side * (R * 0.35 * (1 if k % 2 else -1))
            strand(a, C + d * (R * 0.45 * (frac - 1)) + off - Z * (R * 0.55), L, th=0.38, face=d)
    return C


def cull(a):
    """Delete faces fully buried inside any leaf blob."""
    blobs = a.blobs
    dead = []
    for f in set(a.cullable):
        if not f.is_valid:
            continue
        vs = [v.co for v in f.verts]
        c = sum(vs, Vector()) / len(vs)
        for (bc, rx, rz) in blobs:
            if (c - bc).length > rx + 0.5:
                continue
            if all(((p.x - bc.x) / rx) ** 2 + ((p.y - bc.y) / rx) ** 2 + ((p.z - bc.z) / rz) ** 2 < 0.98
                   for p in vs):
                dead.append(f)
                break
    if dead:
        bmesh.ops.delete(a.bm, geom=dead, context="FACES")
    a.cullable = []


def floor_clamp(a):
    for v in a.bm.verts:
        if v.co.z < 0.0:
            v.co.z = 0.0


def finish(a):
    cull(a)
    floor_clamp(a)
    bm = a.bm
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, 0.0))
    obj = a.finish()
    return obj, off


# Hero layout ---------------------------------------------------------------

# Massive trunk: ~10.5 dia above the flare, tapering only slightly up to the crown, and
# flaring hard into the roots below ~3 studs so the gaps between the buttresses are filled.
# The trunk ends at the branching point (~21) in a low fluted cone: from above it is the
# hub of the branch star.
HERO_PROF = [(0, 4.7), (2.0, 4.6), (5.0, 4.5), (9.0, 4.4), (12.0, 4.5), (14.5, 4.9), (16.5, 5.1),
             (18.0, 4.4), (19.0, 3.0)]
HERO_ROOTS = [  # az, reach, height where it leaves the trunk, half-width there (big and
    # smaller roots alternate, so each ridge reads on its own with a deep valley between)
    (-116, 15.0, 10.0, 2.45), (-64, 14.4, 8.6, 2.15), (-12, 15.2, 10.2, 2.45), (40, 14.3, 8.4, 2.15),
    (92, 14.8, 9.8, 2.4), (142, 15.0, 10.0, 2.45), (192, 14.4, 8.6, 2.15)]
HERO_ARMS = [  # az, branch height, ring dist, clump z, clump R, puffs, strands, spread
    # A ring of seven BIG overlapping clumps (~13 across) on thick limbs: a billowing dome
    # ~35 wide (1.15x the root flare) around a small open centre (the branch star from
    # above). The front clump is the high top-centre one, the outer side lobes hang lower.
    (-90, 17.6, 10.4, 26.7, 6.6, 23, ((0.55, 5.2), (1.8, 5.6)), 0.62),
    (-38.6, 16.6, 11.2, 23.1, 6.5, 23, ((0.6, 5.6), (1.7, 5.0)), 0.62),
    (12.9, 17.0, 11.4, 25.4, 6.5, 23, ((0.6, 5.4),), 0.62),
    (64.3, 17.4, 10.8, 25.7, 6.6, 23, ((1.8, 5.0),), 0.62),
    (115.7, 17.6, 10.8, 26.1, 6.6, 23, ((1.8, 5.0),), 0.62),
    (167.1, 17.0, 11.4, 25.4, 6.5, 23, ((0.6, 5.4),), 0.62),
    (-141.4, 16.8, 11.2, 23.3, 6.5, 23, ((0.6, 5.6), (1.7, 5.0)), 0.62),
]
# big grey boulders in the gaps between the root tips (az, dist, size), plus a few small ones
HERO_STONES = [(-90, 11.6, 4.2), (-38, 11.8, 3.8), (14, 11.8, 4.4), (66, 11.4, 3.6), (118, 11.6, 4.0),
               (167, 11.8, 4.4), (-140, 11.4, 4.0), (-72, 14.4, 2.2), (32, 14.2, 2.0)]
ROOT_MOSS = (5, 5)  # root segment of the small moss patch on a root crest


def tree_body(a, prof, roots, arms, top_h=1.0, flutes=9, mossy=(0, 2, 4, 6), rbr=2.4):
    zs = [z for z, _ in prof]
    rs = [r for _, r in prof]
    # deep, narrow V flutes (groove at 0.48 of the radius) so they read at thumbnail size
    fluted(a, [(0, 0, z) for z in zs], rs, flutes=flutes, twist=0.06, phase=a.rng.uniform(0, TAU),
           top="cone", top_h=top_h, groove=0.48, shoulder=0.84)
    root_buttresses(a, prof, roots, mossy)
    for spec in arms:
        az, zb, ring, zc, R, n, strands, spread = spec
        arm(a, prof, az, zb, ring, zc, R, n, strands=strands, rbr=rbr * (1.0 if spread > 0.5 else 0.85),
            spread=spread)


def root_buttresses(a, prof, roots, mossy=(0, 2, 4, 6), sweep=0.16):
    rb = trunk_r(prof, 1.5)
    for i, (az, reach, h0, w0) in enumerate(roots):
        sw = a.rng.uniform(-sweep, sweep)
        kink = a.rng.choice((-1, 1)) * a.rng.uniform(0.08, 0.16)
        finger = (a.rng.choice((-1, 1)), a.rng.uniform(2.6, 3.6)) if i % 2 == 0 else None
        buttress(a, rad(az), rb, reach, h0, w0, sweep=sw, kink=kink, finger=finger, moss=None)
        if i in mossy:  # moss draped over the root crown, and a cushion lower down
            for fs, rr, hh in ((0.3, 1.2, 0.4),):
                s = rb + (reach - rb) * fs
                aa = rad(az) + sw * fs * fs
                mound(a, (s * math.cos(aa), s * math.sin(aa), root_h(s, rb, reach, h0) - 0.2),
                      rr, hh)


def crown_top(a, prof, z=30.2, R=5.0):
    """A high top-centre clump on a short leader from the trunk top: closes the dip over
    the hub so the crown reads as one billowing dome from the front and the side."""
    zt = prof[-1][0]
    limb(a, [(0, 0, zt - 1.0), (0.2, 0.5, zt + 2.5), (0.3, 0.9, z - R * 0.7)], [2.2, 1.7, 1.2], sides=6,
         cap_end="cone")
    clump(a, (0.3, 0.9, z), R, 23)


def build_hero(kit):
    a = new_asset(kit, "AncientTree", 2051)
    tree_body(a, HERO_PROF, HERO_ROOTS, HERO_ARMS)
    crown_top(a, HERO_PROF)
    dress_base(a, 14.0, [r[0] for r in HERO_ROOTS], HERO_STONES, tufts=20, mounds=3, rb=5.5)
    return finish(a)[0]


# ---------------------------------------------------------------------------
# Variants
# ---------------------------------------------------------------------------


def bool_diff(bm, cutters):
    """bm minus each closed cutter bmesh (exact boolean). Returns a new bmesh."""
    scene = bpy.context.scene
    me = bpy.data.meshes.new("w05_tmp")
    bm.to_mesh(me)
    ob = bpy.data.objects.new("w05_tmp", me)
    scene.collection.objects.link(ob)
    cobs = []
    for i, cb in enumerate(cutters):
        cm = bpy.data.meshes.new(f"w05_cut{i}")
        cb.to_mesh(cm)
        co = bpy.data.objects.new(f"w05_cut{i}", cm)
        scene.collection.objects.link(co)
        cobs.append(co)
        mod = ob.modifiers.new(f"cut{i}", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        try:
            mod.solver = "EXACT"
        except TypeError:
            pass
        mod.object = co
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    out = bmesh.new()
    out.from_mesh(ev.to_mesh())
    ev.to_mesh_clear()
    for o in cobs + [ob]:
        m = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.meshes.remove(m)
    return out


HOLLOW_PROF = [(0, 6.7), (1.5, 6.25), (4.0, 5.85), (8.0, 5.5), (12.0, 5.15), (15.5, 4.8), (18.0, 4.25),
               (19.8, 3.5), (21.0, 2.6)]


def variant_arms(scale=0.94, dz=0.0, strands=True):
    """The hero crown, a touch narrower (the variant cells draw slimmer crowns)."""
    out = []
    for az, zb, ring, zc, R, n, st, spread in HERO_ARMS:
        out.append((az, zb + dz, ring * scale, zc + dz, R * scale, n, st if strands else (), spread))
    return out
DOOR_HW, DOOR_RECT, CAV_R, CAV_TOP = 2.65, 5.3, 3.3, 8.8


def hollow_trunk(a, prof):
    """Closed fluted trunk, minus a cavity and an arched doorway facing -Y."""
    tmp = bmesh.new()
    zs = [z for z, _ in prof]
    zs[0] = -0.4
    rings, faces, grooves, caps = fluted(a, [(0, 0, z) for z in zs], [r for _, r in prof], flutes=9,
                                         twist=0.04, phase=rad(-90) + TAU / 18, top="cone", top_h=2.0,
                                         bottom=True, bm=tmp, paint=False)
    # cavity: one closed 14-sided cylinder with a low cone roof
    cav = bmesh.new()
    nc = 14
    lo = [cav.verts.new((CAV_R * math.cos(TAU * i / nc), 0.2 + CAV_R * math.sin(TAU * i / nc), -1.0))
          for i in range(nc)]
    hi = [cav.verts.new((CAV_R * 0.93 * math.cos(TAU * i / nc), 0.2 + CAV_R * 0.93 * math.sin(TAU * i / nc),
                         CAV_TOP)) for i in range(nc)]
    apex = cav.verts.new((0, 0.2, CAV_TOP + 1.4))
    cav.faces.new(list(reversed(lo)))
    for i in range(nc):
        j = (i + 1) % nc
        cav.faces.new((lo[i], lo[j], hi[j], hi[i]))
        cav.faces.new((hi[i], hi[j], apex))
    # arch prism, extruded along Y from the front to the cavity centre
    arch = bmesh.new()
    outline = [(-DOOR_HW, -1.0), (DOOR_HW, -1.0), (DOOR_HW, DOOR_RECT)]
    for i in range(1, 6):
        ang = PI * i / 6
        outline.append((DOOR_HW * math.cos(ang), DOOR_RECT + DOOR_HW * 1.05 * math.sin(ang)))
    outline.append((-DOOR_HW, DOOR_RECT))
    front = [arch.verts.new((x, -9.0, z)) for x, z in outline]
    back = [arch.verts.new((x, 0.2, z)) for x, z in outline]
    arch.faces.new(front)
    arch.faces.new(list(reversed(back)))
    m = len(outline)
    for i in range(m):
        j = (i + 1) % m
        arch.faces.new((front[i], front[j], back[j], back[i]))
    bmesh.ops.recalc_face_normals(arch, faces=arch.faces[:])
    bmesh.ops.recalc_face_normals(cav, faces=cav.faces[:])
    out = bool_diff(tmp, [cav, arch])
    tmp.free()
    cav.free()
    arch.free()
    # copy into the asset, painting by where each face sits
    bm = a.bm
    vmap = {v: bm.verts.new(v.co) for v in out.verts}
    new = []
    for f in out.faces:
        c = f.calc_center_median()
        if c.z < 0.01 and all(v.co.z < 0.01 for v in f.verts):
            continue  # buried bottom cap
        try:
            new.append((bm.faces.new([vmap[v] for v in f.verts]), c))
        except ValueError:
            pass
    out.free()
    recalc(a, [f for f, _ in new])
    for f, c in new:
        rho = math.hypot(c.x, c.y - 0.2)
        R = trunk_r(prof, max(0.0, c.z))
        if c.z < CAV_TOP + 2.0 and rho < CAV_R + 0.12:
            put(a, f, HOLLOW, tint(a, 0.04))
        elif c.y < 0 and c.z < DOOR_RECT + DOOR_HW * 1.1 + 0.2 and abs(c.x) < DOOR_HW + 0.15 and \
                math.hypot(c.x, c.y) < R * 0.95:
            put(a, f, HEART, tint(a, 0.03))  # the arch reveal: pale broken wood
        else:
            bark(a, f)
    # dark floor inside the cavity, just above the ground patch
    ring = [bm.verts.new((CAV_R * 1.02 * math.cos(TAU * i / 14), 0.2 + CAV_R * 1.02 * math.sin(TAU * i / 14), 0.3))
            for i in range(14)]
    fl = bm.faces.new(ring)
    fl.normal_update()
    if fl.normal.z < 0:
        fl.normal_flip()
    put(a, fl, HOLLOW, 1.0)
    # threshold strip between the doorway and the cavity floor
    ys = -math.sqrt(max(0.0, (prof[0][1]) ** 2 - DOOR_HW ** 2)) - 0.6
    th = [bm.verts.new(p) for p in ((-DOOR_HW, ys, 0.3), (DOOR_HW, ys, 0.3), (DOOR_HW, 0.0, 0.3),
                                     (-DOOR_HW, 0.0, 0.3))]
    tf = bm.faces.new(th)
    tf.normal_update()
    if tf.normal.z < 0:
        tf.normal_flip()
    put(a, tf, HOLLOW, 1.0)


def build_hollow(kit):
    a = new_asset(kit, "AncientTreeHollowTrunk", 2052)
    prof = HOLLOW_PROF
    hollow_trunk(a, prof)
    # a chunky pale broken-wood rim framing the arch (w05_heartwood), proud of the bark
    hw = DOOR_HW + 0.35
    rim_xz = [(-hw - 0.3, 0.2), (-hw - 0.1, 2.2), (-hw, DOOR_RECT)]
    for i in range(1, 6):
        ang = PI - PI * i / 6
        rim_xz.append((hw * math.cos(ang), DOOR_RECT + hw * 1.05 * math.sin(ang)))
    rim_xz += [(hw, DOOR_RECT), (hw + 0.1, 2.2), (hw + 0.3, 0.2)]
    rim_pts = [Vector((x, -math.sqrt(max(0.0, (trunk_r(prof, z) * 0.97) ** 2 - x * x)), z))
               for x, z in rim_xz]
    _, body, _ = limb(a, rim_pts, [0.6] * len(rim_pts), sides=5, cap_end=None, twist=0.0,
                      jitter=0.12, cull=False)
    for f in body:
        put(a, f, HEART, tint(a, 0.04))
    roots = [(-146, 14.4, 8.4, 2.46), (-34, 14.2, 8.1, 2.46), (14, 14.6, 8.6, 2.46), (62, 14.0, 7.8, 2.39),
             (110, 14.4, 8.4, 2.46), (158, 14.6, 8.6, 2.46), (206, 14.2, 8.1, 2.39)]
    root_buttresses(a, prof, roots, mossy=(2, 3, 5), sweep=0.12)
    for az, zb, ring, zc, R, n, strands, spread in variant_arms():
        arm(a, prof, az, zb, ring, zc, R, n, strands=strands, rbr=2.1,
            spread=spread)
    crown_top(a, prof, z=29.6, R=4.8)
    # moss on the arch rim
    for k in range(7):
        ang = PI * (k + 0.5) / 7
        x = DOOR_HW * 1.15 * math.cos(ang)
        z = DOOR_RECT + DOOR_HW * 1.15 * math.sin(ang) + 0.3
        y = -math.sqrt(max(0.0, trunk_r(prof, z) ** 2 - x * x)) + 0.15
        mound(a, (x, y, z - 0.25), 0.55 if k % 2 else 0.7, 0.4)
    for z in (1.0, 2.8):
        for sgn in (-1, 1):
            x = sgn * (DOOR_HW + 0.5)
            y = -math.sqrt(max(0.0, trunk_r(prof, z) ** 2 - x * x)) + 0.1
            mound(a, (x, y, z), 0.5, 0.45)
    stones = [(-62, 11.6, 2.4), (-120, 11.4, 2.8), (-150, 12.6, 1.6), (-20, 12.6, 2.0), (36, 12.0, 2.4),
              (86, 12.2, 2.0), (134, 12.0, 2.6), (182, 12.2, 3.0)]
    dress_base(a, 12.4, [r[0] for r in roots], stones, tufts=10, mounds=5, rb=6.4,
               skip=lambda az: -110 < ((az + 180) % 360 - 180) < -70)
    obj, off = finish(a)
    # sparse slow warm motes drifting in the cave: ~2.5 up, just inside the doorway
    kit.vfx.add(obj, "dust", (0.0 - off.x, -1.3 - off.y, 2.5), 1.0, name="VFX_dust_HollowCavity",
                emitters=[dict(kit.vfx.KINDS["dust"]["emitters"][0], rate=0.6, speed=[0.05, 0.15],
                               color=["#E8C79A", "#E8C79A"], shape=[3.0, 3.0, 4.0])])
    return obj


FORK_BASE = [(0, 6.0), (1.5, 5.6), (4.0, 5.2), (8.0, 5.0), (12.0, 5.1), (15.0, 5.4)]


def build_forked(kit):
    a = new_asset(kit, "AncientTreeForkedGiant", 2053)
    prof = FORK_BASE
    fluted(a, [(0, 0, z) for z, _ in prof], [r for _, r in prof], flutes=9, twist=0.04,
           phase=a.rng.uniform(0, TAU), top="cone", top_h=1.5)
    # two leaders in a V
    legs = {
        -1: [(-1.8, 0.2, 13.0), (-2.9, 0.25, 16.5), (-4.4, 0.3, 20.5), (-5.6, 0.4, 24.5), (-6.0, 0.4, 26.5)],
        1: [(1.8, -0.1, 13.0), (3.0, -0.15, 17.0), (4.5, -0.2, 21.0), (5.6, -0.2, 25.5), (5.9, -0.2, 28.0)],
    }
    lrad = {-1: [4.1, 3.6, 3.0, 2.4, 1.8], 1: [4.2, 3.7, 3.1, 2.5, 1.85]}
    for s, pts in legs.items():
        fluted(a, pts, lrad[s], flutes=7, twist=0.05, phase=a.rng.uniform(0, TAU), top="cone",
               top_h=1.2, groove=0.74)
    roots = [(-120, 14.6, 8.6, 2.54), (-64, 14.2, 8.1, 2.46), (-10, 14.6, 8.6, 2.54), (42, 14.0, 7.8, 2.46),
             (94, 14.2, 8.1, 2.46), (144, 14.6, 8.4, 2.54), (194, 14.2, 8.1, 2.46)]
    root_buttresses(a, prof, roots, mossy=(1, 3, 5))

    def leader_arm(base, az, out, rise, R, n, strands=()):
        base = Vector(base)
        d = dirxy(rad(az))
        p1 = base + d * 1.6 + Z * 0.5
        p2 = base + d * out * 0.6 + Z * (rise * 0.3)
        p3 = base + d * out + Z * (rise - R * 0.35)
        limb(a, [base, p1, p2, p3], [1.7, 1.4, 1.1, 0.7], sides=6)
        C = base + d * out + Z * rise
        clump(a, C, R, n, lo=-0.75, tier=4)
        for frac, L in strands:
            if frac <= 1:
                strand(a, p1.lerp(p2, frac) - Z * 0.9, L, th=0.5, face=d)
            else:
                strand(a, C + d * (R * 0.5) - Z * (R * 0.55), L, th=0.52, face=d)

    # left leader crown
    # two big crowns (R ~6.4) that nearly touch over the V, each with lower side clumps
    clump(a, Vector((-6.6, 0.4, 29.0)), 7.0, 26)
    leader_arm((-4.6, 0.3, 21.0), 180, 4.6, 1.4, 5.4, 18, ((0.7, 5.0), (1.5, 4.6)))
    leader_arm((-5.4, 0.4, 23.0), 120, 4.2, 2.2, 5.0, 16)
    leader_arm((-5.0, 0.3, 22.5), -125, 4.2, 1.8, 5.0, 16, ((1.5, 4.8),))
    # right leader crown
    clump(a, Vector((6.6, -0.2, 29.6)), 7.0, 26)
    leader_arm((4.6, -0.2, 21.5), 0, 4.6, 1.4, 5.4, 18, ((0.7, 5.0), (1.5, 4.6)))
    leader_arm((5.4, -0.2, 24.0), 60, 4.2, 2.2, 5.0, 16)
    leader_arm((5.0, -0.2, 23.0), -55, 4.2, 1.8, 5.0, 16, ((1.5, 4.6),))
    # bark crotch: a bulge of bark where the leaders split
    v = a.ico((2.4, 2.4, 1.2), (0, 0, 15.2), mat=BARK, subdiv=1, jitter=0.05)
    for f in {f for vv in v for f in vv.link_faces}:
        f.normal_update()
        put(a, f, BARK, tint(a, 0.04))
    stones = [(-92, 12.2, 3.0), (-150, 12.4, 2.4), (-38, 12.4, 2.6), (18, 12.4, 1.6), (68, 12.2, 2.6),
              (120, 12.2, 2.0), (170, 12.2, 3.2), (-110, 13.0, 1.4)]
    dress_base(a, 12.6, [r[0] for r in roots], stones, tufts=10, mounds=5)
    return finish(a)[0]


RESIN_PROF = [(0, 6.2), (1.5, 5.9), (4.0, 5.6), (8.0, 5.35), (12.0, 5.05), (15.5, 4.7), (18.0, 4.2),
              (19.8, 3.4), (21.0, 2.5)]


def resin_run(a, prof, az, z_top, w, th=1.0, drift=6.0, beads=3, z_end=0.35):
    """A thick glowing resin run hugging the trunk: a curved 5-vertex sheet from a bark
    wound at z_top down to z_end, widening as it flows, with drip beads (all w05_resin).
    Returns the centre-line points (top to bottom)."""
    bm = a.bm
    zs = []
    z = z_top
    while z > z_end + 0.25:
        zs.append(z)
        z -= 1.2
    zs.append(z_end)
    n = len(zs)
    ph = a.rng.uniform(0, TAU)
    ph2 = a.rng.uniform(0, TAU)
    secs, centre = [], []
    for i, z in enumerate(zs):
        u = i / (n - 1)
        aa = rad(az + drift * math.sin(ph + u * 2.6))
        R = trunk_r(prof, z) * 1.04
        if i == n - 1 and z_end < 1:
            R += 0.9  # spills out over the root flare onto the ground
        # bulging lobes along the run: thick drips that swell and pinch as they flow
        lobe = 1 + 0.38 * math.sin(ph2 + u * 8.5)
        ww = w * (0.45 + 0.55 * min(1.0, u * 1.6)) * lobe * a.rng.uniform(0.9, 1.1)
        da = (ww / 2) / R
        ring = []
        for fa, fr in ((-1, -0.12), (-0.5, 0.8), (0, 1.0), (0.5, 0.8), (1, -0.12)):
            ang = aa + fa * da
            rr = R + th * fr
            ring.append(bm.verts.new((rr * math.cos(ang), rr * math.sin(ang), z)))
        secs.append(ring)
        centre.append(Vector(((R + th) * math.cos(aa), (R + th) * math.sin(aa), z)))
    faces = []
    for i in range(n - 1):
        for k in range(4):
            faces.append(bm.faces.new((secs[i][k], secs[i][k + 1], secs[i + 1][k + 1], secs[i + 1][k])))
    faces.append(bm.faces.new(secs[0]))
    recalc(a, faces)
    for f in faces:
        put(a, f, RESIN, 1.0)
    # hanging tear-drops off alternate edges of the run (organic drips)
    for k in range(beads):
        u = (k + 0.8) / (beads + 0.6)
        p = centre[min(n - 1, int(u * (n - 1)))]
        o = Vector((p.x, p.y, 0)).normalized()
        sd = o.cross(Z) * (1 if k % 2 else -1)
        r = w * a.rng.uniform(0.2, 0.27)
        a.ico((r, r, r * 2.2), p + sd * (w * 0.42) - Z * (r * 1.4), mat=RESIN, subdiv=1, jitter=0.04,
              tint=1.0)
    return centre


def wound(a, p, size=0.8):
    """Torn bark where the resin leaks out: pale broken wood."""
    p = Vector(p)
    o = Vector((p.x, p.y, 0)).normalized()
    phi = math.atan2(-o.x, o.y)
    v = a.ico((size, 0.3, size * 1.4), p, rot=(0, 0, phi), mat=HEART, subdiv=1, jitter=0.05)
    for f in {f for vv in v for f in vv.link_faces}:
        f.normal_update()
        put(a, f, HEART, 1.0)


def build_resin(kit):
    a = new_asset(kit, "AncientTreeResinBearing", 2054)
    prof = RESIN_PROF
    fluted(a, [(0, 0, z) for z, _ in prof], [r for _, r in prof], flutes=9, twist=0.0, phase=rad(-90),
           top="cone", top_h=2.0)
    roots = [(-122, 14.6, 8.6, 2.54), (-60, 14.2, 8.1, 2.46), (-2, 14.6, 8.6, 2.54), (52, 14.0, 7.8, 2.46),
             (103, 14.2, 8.1, 2.46), (154, 14.6, 8.4, 2.54), (206, 14.2, 8.1, 2.46)]
    root_buttresses(a, prof, roots, mossy=(3, 5), sweep=0.1)
    for az, zb, ring, zc, R, n, strands, spread in variant_arms():
        arm(a, prof, az, zb, ring, zc, R, n, strands=strands, rbr=2.1,
            spread=spread)
    crown_top(a, prof, z=29.6, R=4.8)
    # thick resin runs oozing down the front and the right side from bark wounds, in the
    # gaps between the roots; two shorter drips above the root tops
    runs = []
    # three separate drips (a long main run, two shorter ones) of orange-amber resin
    for az, z_top, w, z_end, beads in ((-88, 16.0, 2.2, 0.35, 4), (-36, 13.5, 1.6, 0.35, 3),
                                       (-122, 12.0, 1.4, 6.5, 2)):
        runs.append(resin_run(a, prof, az, z_top, w, z_end=z_end, beads=beads))
        p = runs[-1][0]
        wound(a, p + Z * 0.6, size=w * 0.42)
    # the glowing resin mass bulging from the main wound (the glyph_glow socket sits on it)
    top = runs[0][0]
    o = Vector((top.x, top.y, 0)).normalized()
    mass = top + o * 0.3 - Z * 0.4
    a.ico((1.0, 0.8, 1.3), mass, mat=RESIN, subdiv=1, jitter=0.08, tint=1.0)
    # two rounded resin pools at the foot, among the front / front-right roots
    bm = a.bm
    for cx, cy, Rp in ((0.6, -8.4, 3.0),):
        n = 11
        ph = a.rng.uniform(0, TAU)
        rim, bot = [], []
        for i in range(n):
            th_ = ph + TAU * i / n
            k = Rp * (1 + 0.16 * math.sin(3 * th_ + ph)) * a.rng.uniform(0.92, 1.06)
            x, y = cx + k * math.cos(th_), cy + 0.8 * k * math.sin(th_)
            rim.append(bm.verts.new((x, y, 0.42)))
            bot.append(bm.verts.new((cx + (x - cx) * 1.08, cy + (y - cy) * 1.08, 0.12)))
        apex = bm.verts.new((cx, cy, 0.62))  # a slightly domed, rounded pool surface
        fs = [bm.faces.new((rim[i], rim[(i + 1) % n], apex)) for i in range(n)]
        fs += [bm.faces.new((rim[i], bot[i], bot[(i + 1) % n], rim[(i + 1) % n])) for i in range(n)]
        recalc(a, fs)
        for f in fs:
            put(a, f, RESIN, 1.0)
    stones = [(-150, 12.4, 2.6), (-128, 12.8, 1.6), (78, 12.2, 2.6), (128, 12.2, 2.0), (178, 12.2, 3.0),
              (-112, 12.0, 2.2)]
    dress_base(a, 12.4, [r[0] for r in roots], stones, tufts=10, mounds=5,
               skip=lambda az: -100 < ((az + 180) % 360 - 180) < 35)
    obj, off = finish(a)
    p = mass + o * 1.0
    # live glow of the resin mass: slow warm amber pulse + sparse amber motes (#F59A16)
    kit.vfx.add(obj, "glyph_glow", (p.x - off.x, p.y - off.y, p.z), 1.0, name="VFX_glyph_glow_Resin",
                light={"color": "#FF8A1A", "brightness": 1.5, "range": 10, "flicker": False, "pulse": True},
                emitters=[{"name": "Glimmer", "texture": "glow_soft", "color": ["#FF8A1A", "#FF8A1A"],
                           "size": [0.6, 0.9], "transparency": [0.6, 1.0], "lifetime": [2.0, 3.0],
                           "rate": 0.8, "speed": [0, 0.2], "spread": 0, "light_emission": 1.0}])
    allp = [q for r in runs for q in r]
    cxr = sum((q.x for q in allp)) / len(allp)
    cyr = sum((q.y for q in allp)) / len(allp)
    czr = sum((q.z for q in allp)) / len(allp)
    glint = dict(kit.vfx.KINDS["ore_glint"]["emitters"][0])
    glint.update(color=["#FFD27A", "#FFD27A"], shape=[6.0, 8.0, 3.0])
    kit.vfx.add(obj, "ore_glint", (cxr - off.x, cyr - off.y, czr), 1.0, name="VFX_ore_glint_Resin",
                emitters=[glint])
    return obj


# ---------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------


def build_crown_module(kit):
    a = new_asset(kit, "AncientCrownModule", 2061)
    # a short angled stub (flat heartwood attach face at its foot) that forks under the clump;
    # the clump sits off to one side so the forked stub reads below it
    limb(a, [(2.0, 0, 0), (1.5, 0, 1.2), (0.6, 0.05, 2.5)], [1.0, 0.88, 0.74], sides=6, cap_end=None,
         cap_start=True, end_mat="w05_heartwood", cull=False)
    limb(a, [(0.6, 0.05, 2.3), (-0.8, -0.2, 3.4), (-1.8, -0.3, 4.4)], [0.62, 0.52, 0.4], sides=6)
    limb(a, [(0.6, 0.05, 2.3), (2.2, 0.2, 2.9), (3.7, 0.3, 3.5)], [0.55, 0.45, 0.34], sides=6,
         cap_end="flat", end_mat="w05_heartwood", cull=False)
    # the same cauliflower clump as the hero crown (many small puffs + a heaped tier)
    clump(a, (-0.7, 0, 4.4), 4.6, 24, pr=(1.0, 1.7), flat=0.72, lo=-0.7, tier=3)
    return finish(a)[0]


def build_branch_module(kit):
    a = new_asset(kit, "AncientBranchModule", 2062)
    # thick main limb; the flat heartwood attach face at -X faces sideways (a vertical cut)
    main = [(-6.6, 0, 1.75), (-4.4, -0.2, 1.9), (-1.6, 0.0, 1.8), (1.4, 0.3, 2.1), (4.2, 0.2, 2.9),
            (6.4, 0.1, 3.9)]
    limb(a, main, [1.7, 1.6, 1.45, 1.2, 0.95, 0.7], sides=7, cap_end="cone", cap_start=True,
         end_mat="w05_heartwood", cull=False)
    # upturned fork: a thick riser that splits into a Y of two sub-stubs
    # (the fork leans back toward +Y and the side stub reaches out toward -Y, so the part
    # has real depth and the parts-cell grid gives it its own space)
    limb(a, [(-1.6, 0.0, 2.4), (-1.4, 0.5, 3.9), (-1.1, 0.9, 5.0)],
         [1.15, 1.0, 0.88], sides=6, cap_end=None, cull=False)
    limb(a, [(-1.1, 0.9, 4.8), (-2.2, 1.3, 6.4), (-3.2, 1.6, 8.0)], [0.82, 0.66, 0.48], sides=6,
         cap_end="cone", cull=False)
    limb(a, [(-1.1, 0.9, 4.8), (0.2, 1.2, 6.2), (0.9, 1.5, 7.8)], [0.8, 0.64, 0.46], sides=6,
         cap_end="cone", cull=False)
    limb(a, [(0.0, 1.2, 5.4), (1.2, 1.3, 5.9), (1.8, 1.4, 6.5)], [0.32, 0.27, 0.2], sides=5,
         cull=False)
    # side stub reaching out sideways
    limb(a, [(2.6, 0.3, 2.4), (3.4, -1.8, 3.0), (4.0, -3.6, 3.4)], [0.75, 0.6, 0.45], sides=6,
         cap_end="cone", cull=False)
    return finish(a)[0]


def build_trunk_core(kit):
    a = new_asset(kit, "AncientTrunkCore", 2063)
    # a straight fluted barrel (~9.4 dia), barely tapering, with a ragged broken top
    # with a short flared foot where the roots attach
    prof = [(0, 6.0), (0.5, 5.6), (1.4, 5.0), (2.8, 4.55), (5.5, 4.35), (8.6, 4.3), (11.4, 4.25)]
    rings, faces, grooves, caps = fluted(a, [(0, 0, z) for z, _ in prof], [r for _, r in prof], flutes=9,
                                         twist=0.04, phase=a.rng.uniform(0, TAU), top=None, top_jag=0.9,
                                         bottom=True)
    bm = a.bm
    # the core is a sawn section: its underside is a cut face too (heartwood, both ends)
    put(a, caps[-1], HEART, 1.0)
    top = rings[-1]
    zc = sum(v.co.z for v in top) / len(top)
    # ragged cut top: a bark rim, then pale heartwood with two w05_bark growth-ring lines
    # (scale of the outline, height squash, material) from the outside in
    bands = [(0.86, 0.3, BARK), (0.64, 0.12, HEART), (0.57, 0.1, BARK), (0.34, 0.06, HEART),
             (0.28, 0.05, BARK)]
    prev = top
    out = []
    for s, sq, mat in bands:
        ring = [bm.verts.new(Vector((v.co.x * s, v.co.y * s, zc - 0.05 + (v.co.z - zc) * sq))) for v in top]
        S = len(top)
        for j in range(S):
            k = (j + 1) % S
            out.append((bm.faces.new((prev[j], prev[k], ring[k], ring[j])), mat))
        prev = ring
    centre = bm.verts.new((0, 0, zc + 0.05))
    S = len(prev)
    for j in range(S):
        out.append((bm.faces.new((prev[j], prev[(j + 1) % S], centre)), HEART))
    recalc(a, [f for f, _ in out])
    for f, mat in out:
        put(a, f, mat, tint(a, 0.03))
    obj = finish(a)[0]
    obj["kit_shading_ok"] = CUT_OK
    return obj


def root_part(kit, name, seed, path, radii, split=None, flutes=6):
    """A chunky root log lying on the ground: a tapered fluted tube (6 chiselled flutes)
    whose thick -X end is raised and cut square to the path, so the flat w05_heartwood
    attach face slopes; it runs down to a low +X tip. split=(deg, length) forks the tip
    into two short angular fingers. The buried underside is flattened at z=0."""
    a = new_asset(kit, name, seed)
    path = [Vector(p) for p in path]
    rings, faces, grooves, caps = fluted(a, path, radii, flutes=flutes, twist=0.06,
                                         phase=a.rng.uniform(0, TAU), rough=0.07, top="cone",
                                         top_h=radii[-1] * (0.6 if split else 1.6), bottom=True,
                                         groove=0.7, shoulder=0.9)
    put(a, caps[-1], HEART, 1.0)  # the start cap: the attach face
    if split:
        end = path[-1]
        t = (path[-1] - path[-2])
        t.z = 0
        t.normalize()
        r = radii[-1]
        for sgn, k in ((-1, 1.0), (1, 0.8)):
            d = Matrix.Rotation(sgn * rad(split[0]), 3, "Z") @ t
            L = split[1] * k
            limb(a, [end - t * 0.4, end + d * L * 0.55 + Z * (-r * 0.25), end + d * L + Z * (-r * 0.45)],
                 [r * 0.8, r * 0.62, r * 0.42], sides=6, cap_end="cone", cull=False)
    obj = finish(a)[0]
    obj["kit_shading_ok"] = CUT_OK
    return obj


def build_root_a(kit):
    # long swept: curves in plan, the raised thick end ramping down, ~11 long x ~3.8 thick
    path = [(-5.0, 0.0, 2.5), (-3.8, -0.4, 2.6), (-1.8, -0.75, 1.9), (0.2, -0.8, 1.4), (2.2, -0.4, 1.1),
            (3.9, 0.2, 0.85), (5.0, 0.6, 0.7)]
    return root_part(kit, "AncientRootModuleA", 2071, path, [1.9, 1.8, 1.6, 1.4, 1.2, 1.0, 0.85],
                     split=(26, 2.0))


def build_root_b(kit):
    # short steep: a high attach end dropping fast to the ground, ~6 long x ~5 tall
    path = [(-2.8, 0.0, 3.0), (-1.7, 0.05, 3.5), (-0.6, 0.1, 2.6), (0.6, 0.05, 1.7), (1.9, -0.1, 1.15),
            (3.1, -0.2, 0.8)]
    return root_part(kit, "AncientRootModuleB", 2072, path, [1.8, 1.75, 1.6, 1.35, 1.05, 0.8])


def build_root_c(kit):
    # kinked: runs out, bends sideways at a knuckle, then forks into a split tip
    path = [(-4.4, 0.0, 2.2), (-3.2, 0.1, 2.65), (-1.4, 0.3, 1.8), (-0.2, 1.3, 1.5), (1.3, 1.5, 1.15),
            (2.8, 1.0, 0.9)]
    return root_part(kit, "AncientRootModuleC", 2073, path, [1.85, 1.75, 1.6, 1.6, 1.3, 1.05],
                     split=(30, 2.2))


# ---------------------------------------------------------------------------


def build(kit):
    hero = kit.tag(build_hero(kit), "hero", collision="precise", budget=8000,
                   notes="buttress grooves and the crown ring need precise collision; dressing faces "
                         "(grass, moss mounds/strands, ground patch, small rocks) carry kit_nocollide=1")
    parts = [
        kit.tag(build_crown_module(kit), "part", collision="hull", budget=1500,
                notes="clump on a forked stub; the stub's flat heartwood base attaches to a branch end"),
        kit.tag(build_branch_module(kit), "part", collision="hull", budget=1500,
                notes="the -X end is the flat heartwood attach face for the trunk"),
        kit.tag(build_trunk_core(kit), "part", collision="hull", budget=1500,
                notes="ragged cut top with heartwood rings; roots and branches kit-bash onto it"),
        kit.tag(build_root_a(kit), "part", collision="hull", budget=1500,
                notes="sloped heartwood attach face at -X sits against AncientTrunkCore"),
        kit.tag(build_root_b(kit), "part", collision="hull", budget=1500,
                notes="sloped heartwood attach face at -X sits against AncientTrunkCore"),
        kit.tag(build_root_c(kit), "part", collision="hull", budget=1500,
                notes="sloped heartwood attach face at -X; knuckle mid-way, split tip at +X"),
    ]
    hollow = kit.tag(build_hollow(kit), "variant", collision="precise", budget=8000,
                     notes="walk-in arch at -Y (precise keeps it open); dust socket = sparse motes in "
                           "the cavity; dressing faces carry kit_nocollide=1")
    forked = kit.tag(build_forked(kit), "variant", collision="precise", budget=8000,
                     notes="dressing faces carry kit_nocollide=1")
    resin = kit.tag(build_resin(kit), "variant", collision="precise", budget=8000,
                    notes="w05_resin faces (emissive) export as Neon; glyph_glow socket = slow amber pulse "
                          "light + sparse amber motes on the main front run; ore_glint socket = glossy "
                          "twinkles over the runs; dressing faces carry kit_nocollide=1")
    return [hero] + parts + [hollow, forked, resin]
