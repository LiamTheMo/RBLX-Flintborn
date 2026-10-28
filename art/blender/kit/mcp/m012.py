"""012 Amber (references/012.png): a chunky faceted amber egg sunk in a nest of weathered split timber.
Low front (a long fused beam across it), tall back (a three-plank tepee behind it), as on the sheet.

    import importlib, kit_models, m011, m012; importlib.reload(kit_models); importlib.reload(m012); m012.build()

Parts (the sheet's exploded view; the R03 kit sheet owns AmberNodule, hence AmberCrystalMain), each built by its own
function in one shared build frame (studs, front -Y, ground z = 0):
- AmberCrystalMain (nodule): the Amber Nodule. A cut-gem egg of about 40 broad facets in rows (crown, upper ring,
  belt of planar trapezoids, lower ring, blunt bottom): a hull of staggered rings, coplanar triangles merged. Built
  upright at its own origin; the hero places it with _nod_matrix() (sunk into the seat, top leaning front-left).
- AmberWoodFront (wood_front): Wood Base (Front). One long beam of two boards fused side by side (V groove along
  the top, staggered oblique ends), its left end raised on a squat stub block, its right end on the ground.
- AmberWoodBack (wood_back): Wood Base (Rear), the chunky block split at one end (two fused halves, V notch,
  staggered tops), standing on end at the front right as the hero views' two right-hand uprights, plus the sheet's
  unlabelled centre seat (two boards side by side whose tops make a shallow V the nodule drops into).
- AmberWoodLeft (wood_left): Side Wood (Left). A hewn upright post with a pyramid-chamfered top, a shorter plank
  standing behind it, a lying split slab at its foot and a lying square block running back towards the tepee.
- AmberWoodRight (wood_right): Side Wood (Right). A tepee behind the nodule (back-centre and -X, where the sheet's
  rear views put it): the tall chisel-topped plank behind the crown, a shorter partner fused alongside, and a broad
  plank leaning out backwards from their feet (the rear views' big slab).
See M012_spec.md, "Stage 1 - Modelling (remake)", for the layout decisions.
Every wood piece is board(): a chamfered rectangle (with grain breaks on its broad faces) lofted through stations
about 1.3 apart, each nudged and twisted a little so the long faces break into long planar facets along the grain;
ends are deliberate planar cuts (oblique, chamfered rim) or hewn pyramid / chisel tops. No hull jitter, no splinters.

The hero is pasted together from the finished part meshes (each put back into the build frame) and unioned into one
closed shell; the base is the parts' flat floor cuts (Detail C). Stage 1 colour is placeholder keys per region only:
amber light / mid / dark by height, wood broad faces, chamfer strips and end cuts (stage 4 colours them).
Stage 2+3: _polish() (all triangles, no corner under POLISH_LIM = 5 degrees, bottom-centre origin, UVs re-made) and
_uv_unfold() (faces an angle-based unwrap folds over are cut free) run on every part and the hero after _finish().
Stage 4 (palette, colour_parts: colour_nodule, colour_wood): calibrated keys blended by position fields on the finished
parts (only material indices and Tint change); the hero inherits them through _paste. Amber: a ranked core field per
facet graded dark -> mid -> light with in-between keys, darker angular inclusions in multi-triangle facets, per-facet
Tint drift. Wood: grain streaks along each board's own axis (board() records its frame in BOARDS), worn chamfers, end
grain, dark V grooves / creases, a warm bleed by the amber, broad Tint mottling.
Stages 5+6 (STUDIO_LIGHT, GLINTS, _vfx): no emissive faces; the hero carries a crystal_glow socket (soft amber
PointLight in front of the nodule) and three ore_glint sockets boxed tight round upper light-facet junctions.
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

NUM, TITLE, SHEET = 12, "Amber", "M012"
A_LIGHT, A_MID, A_DARK = "m012_amber_light", "m012_amber_mid", "m012_amber_dark"
A_GLOW = "m012_amber_glow"
WOOD, WOOD_LIGHT, WOOD_END = "m012_wood", "m012_wood_light", "m012_wood_end"
WOOD_DARK, WOOD_WARM = "m012_wood_dark", "m012_wood_warm"

# stage 3 UVs as on M011: Smart UV islands made seams, re-unwrapped angle-based, exact 0.008 margin
UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008)


def palette():
    # stage 4: base colours calibrated so the kit studio render matches the sheet AS RENDERED (K.calibrate on the
    # test dome, then corrected in linear light against the hero renders; targets and re-measures in M012_spec.md,
    # "Stage 4"). Sheet swatches: amber light #FECD64, mid #FE7719, dark #D25117, wood #8E5E3D.
    # Amber: roughness 0.45 and low specular (no white glints, no cream-washed facets).
    K.set_colour(A_GLOW, "#FDB76E", rough=0.45, low_spec=True)     # seam lines in the core (renders #FFEC81)
    K.set_colour(A_LIGHT, "#FDAE30", rough=0.45, low_spec=True)
    K.set_colour(A_MID, "#F66816", rough=0.45, low_spec=True)
    K.set_colour(A_DARK, "#924A0E", rough=0.45, low_spec=True)     # red-orange (dome renders #CD5214)
    K.set_colour(WOOD, "#6E4A2F", rough=0.9)
    K.set_colour(WOOD_DARK, "#4F2D11", rough=0.9)
    K.set_colour(WOOD_LIGHT, "#A06A44", rough=0.9)
    K.set_colour(WOOD_END, "#98663F", rough=0.9)
    K.set_colour(WOOD_WARM, "#84522B", rough=0.9)


# ---- the nodule ---------------------------------------------------------------------------------------------------
# verifier round 1: narrower, more egg-like (a smaller crown, the widest ring at 0.4 of the height), less amber in the
# top / side / rear views
NOD = dict(w=5.4, d=4.6, h=6.7, seed=12001)
# rings: (height fraction, points, radius as a fraction of the half-width / half-depth, angular phase in steps).
# B and C share count, phase and sector jitter, so the belt between them is planar trapezoids; the others are offset
# half a step, so their facets are kites and pentagons.
NOD_RINGS = ((1.0, 3, 0.27, 0.25), (0.86, 6, 0.6, 0.0), (0.64, 7, 0.92, 0.5), (0.4, 7, 1.0, 0.5),
             (0.18, 6, 0.8, 0.0), (0.0, 4, 0.42, 0.5))
# Seams and inclusions (verifier round 1, for stage 4): every facet gets a coplanar inset border strip SEAM wide (the
# sheet's bright seams along the facet edges) and its inside is fanned from an off-centre point into PATCHES angular
# sub-patches (the darker / lighter inclusions). Facet edges longer than SEAM_SEG are split first, so the strip's
# triangles stay above stage 2's 5 degrees (atan(0.1 / 1.05) = 5.4). Facets whose centre is below SEAM_LOW of the height
# sit in the seat (hidden) and stay plain, to keep the part in budget. Each face is recorded in NOD_FACES (centre in
# the nodule's own frame, "seam" or "patch", facet number, patch number); nod_regions() maps them onto a mesh.
SEAM = 0.1
SEAM_SEG = 1.05
SEAM_LOW = 0.24
PATCHES = 3
NOD_FACES = []
NOD_MERGE = 5.0          # degrees: hull triangles this close to coplanar merge into one broad facet
# placement in the hero: the nodule's bottom centre, then the lean (top towards -X and towards the front)
NOD_POS = (0.9, 0.25, 0.3)
NOD_LEAN = (-8.0, 12.0)  # degrees about Y (top to -X) and about X (top to -Y)


def _sector(th, seed):
    """Broad radius jitter by angle (sectors of the egg, never per vertex): within about +-6 %."""
    r = random.Random(seed)
    a, b = r.uniform(0, 6.3), r.uniform(0, 6.3)
    return 1.0 + 0.05 * math.sin(th + a) + 0.03 * math.sin(2 * th + b)


def nodule(a):
    """Amber Nodule, upright, bottom centre at the origin."""
    w, d, h, seed = NOD["w"], NOD["d"], NOD["h"], NOD["seed"]
    pts = []
    for k, (fz, n, r, ph) in enumerate(NOD_RINGS):
        rng = random.Random(seed + 7 * n)          # B and C (both 7 points) draw the same angular nudges
        for i in range(n):
            th = 2 * math.pi * (i + ph) / n + rng.uniform(-0.09, 0.09)
            j = _sector(th, seed)
            dz = 0.0 if fz in (0.0, 1.0) else 0.03 * h * math.sin(3 * th + n)     # B and C alike
            pts.append(Vector((math.cos(th) * r * j * w / 2, math.sin(th) * r * j * d / 2, fz * h + dz)))
    vs = [a.bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(a.bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    faces = K.faces_of(vs)
    bmesh.ops.dissolve_limit(a.bm, angle_limit=math.radians(NOD_MERGE), verts=vs,
                             edges=list({e for f in faces for e in f.edges}))
    vs = [v for v in vs if v.is_valid]
    NOD["facets"] = len(K.faces_of(vs))
    _seams(a.bm)                        # the nodule is the only geometry in this Asset
    vs = list(a.bm.verts)
    bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
    a._finish(vs, A_MID)
    # placeholder regions: the light core high up, the dark bottom rows
    li, di = a._mi(A_LIGHT), a._mi(A_DARK)
    for f in K.faces_of(vs):
        c = f.calc_center_median()
        if c.z > 0.62 * h and c.x > -0.25 * w:
            f.material_index = li
        elif c.z < 0.24 * h:
            f.material_index = di
    return vs


def _seams(bm):
    """Split the facets (n-gons after the merge) into a seam strip and inclusion patches, all coplanar with the
    facet, triangulate, and record every face in NOD_FACES."""
    NOD_FACES.clear()
    tag = bm.faces.layers.int.new("m012_tag")
    low = NOD["h"] * SEAM_LOW
    seamed = {f for f in bm.faces if f.calc_center_median().z >= low}
    groups = {}
    for e in bm.edges:
        k = int(e.calc_length() / SEAM_SEG)
        if k and any(f in seamed for f in e.link_faces):
            groups.setdefault(k, []).append(e)
    for k, es in groups.items():
        bmesh.ops.bisect_edges(bm, edges=es, cuts=k)      # verts only; the facets stay whole
    rng = random.Random(NOD["seed"] + 5)
    for i, f in enumerate(list(bm.faces)):
        nrm, c = f.normal.copy(), f.calc_center_median()
        if c.z < low:
            # hidden in the seat: plain, fanned from its centre (an edge split for a seamed neighbour leaves a
            # straight run of corners a plain triangulation would make needles of)
            for x in bmesh.ops.poke(bm, faces=[f])["faces"]:
                x[tag] = 100000 + i
            continue
        res = bmesh.ops.inset_individual(bm, faces=[f], thickness=SEAM, depth=0.0, use_even_offset=True)
        for s in res["faces"]:
            s[tag] = -(i + 1)
        # f is the inner face now: fan it from a point part-way to one of its corners
        vs = list(f.verts)
        tgt = vs[rng.randrange(len(vs))].co.copy()
        p = c.lerp(tgt, 0.22)
        fan = bmesh.ops.poke(bm, faces=[f])
        fan["verts"][0].co = p
        e1 = (tgt - c)
        e1 = (e1 - nrm * e1.dot(nrm)).normalized()
        e2 = nrm.cross(e1)
        tris = sorted(fan["faces"], key=lambda x: math.atan2((x.calc_center_median() - p).dot(e2),
                                                              (x.calc_center_median() - p).dot(e1)))
        n_p = PATCHES if len(tris) >= 6 else 2
        start = rng.randrange(len(tris))
        for j, x in enumerate(tris):
            x[tag] = i * 8 + (((j - start) % len(tris)) * n_p // len(tris)) + 1
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    for f in bm.faces:
        t = f[tag]
        tri = tuple(v.co.copy() for v in f.verts)
        NOD_FACES.append((tri, "seam", -t - 1, -1) if t < 0 else
                         (tri, "plain", t - 100000, -1) if t >= 100000 else
                         (tri, "patch", (t - 1) // 8, (t - 1) % 8))
    bm.faces.layers.int.remove(tag)


def nod_regions(o, mat=None):
    """Stage 4 lookup: the nodule's seam strips and inclusion patches on a mesh made from it, as {polygon index:
    ("seam" | "patch", facet, patch)} (patch -1 for seams). mat maps o's mesh coordinates into the nodule's own
    frame (default: the part's own m012_offset, i.e. o is AmberCrystalMain). A face takes the tag of the recorded
    triangle its centre lies on (within 0.06 stud), so stage 2's edge flips, collapses and sub-0.06 nudges keep the
    tags."""
    from mathutils.bvhtree import BVHTree
    if not NOD_FACES:
        M._build_offset(nodule)          # a probe build fills NOD_FACES (after a Blender restart)
    mat = mat if mat is not None else _frame(o)
    vs = [q for r in NOD_FACES for q in r[0]]
    tree = BVHTree.FromPolygons(vs, [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(len(NOD_FACES))])
    out = {}
    for p in o.data.polygons:
        co, _, i, d = tree.find_nearest(mat @ p.center)
        if co is not None and d < 0.06:
            out[p.index] = NOD_FACES[i][1:]
    return out


def _nod_matrix():
    ry, rx = (math.radians(x) for x in NOD_LEAN)
    return Matrix.Translation(NOD_POS) @ Matrix.Rotation(rx, 4, "X") @ Matrix.Rotation(ry, 4, "Y")


# ---- split timber -------------------------------------------------------------------------------------------------
BOARDS = {}             # seed -> the board's frame in the build frame (filled by board(), read by stage 4)
_PART = [None]          # the part whose builder is running (set by build())
# verifier round 1: the boards read soft and lumpy - a narrower chamfer, half the station jitter and twist, one
# grain break per broad face (crisp rectangular sections). Station spacing 1.0 keeps the 0.1 chamfer strips' triangles
# above stage 2's 5 degrees (atan(0.1 / 1.0) = 5.7).
CHAMFER = 0.1           # chamfer on every long edge (studs; at most 22 % of the board's smaller side)
SEG = 1.0               # station spacing along a board
RIM = dict(cap=None)     # default end: a planar cut with a chamfered rim


def _section(W, T, c, rng):
    """A chamfered rectangle in the board's (u, v) plane, counter-clockwise, as (u, v, kind of the edge to the
    next point, grain axis or None). Broad faces get a grain point part-way across (fixed along the board), so they
    break into two long facets; kind 'c' marks the chamfer strips."""
    pts = []

    def face(p, q, axis, length):
        pts.append((p[0], p[1], "f", None))
        k = 1 if length >= 0.8 else 0
        for i in range(k):
            t = (i + 1) / (k + 1) + rng.uniform(-0.12, 0.12)
            pts.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, "f", axis))
    face((W, -T + c), (W, T - c), (1, 0), 2 * T - 2 * c)
    pts.append((W, T - c, "c", None))
    face((W - c, T), (-W + c, T), (0, 1), 2 * W - 2 * c)
    pts.append((-W + c, T, "c", None))
    face((-W, T - c), (-W, -T + c), (-1, 0), 2 * T - 2 * c)
    pts.append((-W, -T + c, "c", None))
    face((-W + c, -T), (W - c, -T), (0, -1), 2 * W - 2 * c)
    pts.append((W - c, -T, "c", None))
    # fix the kinds: each entry's kind describes the edge from it to the next point
    out = []
    for i, (u, v, _, g) in enumerate(pts):
        nu, nv = pts[(i + 1) % len(pts)][:2]
        chamfer = abs(abs(nu - u) - abs(nv - v)) < 1e-6 and abs(nu - u) > 1e-6     # a 45-degree edge
        out.append((u, v, "c" if chamfer else "f", g))
    return out


def board(a, p0, p1, w, t, side=(0, 0, 1), seed=0, end0=None, end1=None, wobble=0.04, grain=0.05, twist=1.5,
          seg=SEG):
    """One split-timber board along p0 -> p1 (centre line), w across `side` (projected square to the axis), t across
    the other way. end0 / end1: dict(cut=(deg towards u, deg towards v)) tilts that end's cut plane; cap=(scale u,
    scale v, push) shapes the end beyond the cut (default a chamfered rim); point=("pyramid", push, off u, off v)
    ends it in a hewn pyramid point (four sloped faces to one apex, offset by fractions of the half width /
    thickness), point=("chisel", push, ridge, off u) in a chisel spire (the narrow sides slope up to a short ridge
    running through the thickness, so the broad faces end in a gable point). Returns its verts."""
    rng = random.Random(seed)
    p0, p1 = Vector(p0), Vector(p1)
    ax = (p1 - p0).normalized()
    L = (p1 - p0).length
    s = Vector(side)
    u = (s - ax * s.dot(ax)).normalized()
    v = ax.cross(u)
    W, T = w / 2, t / 2
    # stage 4: remember the board's frame (build frame), so the colour pass can run grain along its own axis
    BOARDS[seed] = dict(part=_PART[0], p0=p0.copy(), ax=ax.copy(), L=L, u=u.copy(), v=v.copy(), W=W, T=T)
    c = min(CHAMFER, 0.22 * min(w, t))
    sec = _section(W, T, c, rng)
    n = max(2, round(L / seg))
    ends = []
    for k, e, out in ((0, end0 or {}, -ax), (n, end1 or {}, ax)):
        aw, at = e.get("cut", (0.0, 0.0))
        nrm = (out + u * math.tan(math.radians(aw)) + v * math.tan(math.radians(at))).normalized()
        ends.append((k, nrm, e.get("cap"), e.get("point")))
    bm = a.bm
    rings = []
    for k in range(n + 1):
        f = k / n
        centre = p0 + (p1 - p0) * f
        inner = 0 < k < n
        if inner:
            centre += u * rng.uniform(-wobble, wobble) + v * rng.uniform(-wobble, wobble)
        th = math.radians(rng.uniform(-twist, twist)) if inner else 0.0
        su, sv = ((1.0 + rng.uniform(-0.03, 0.03), 1.0 + rng.uniform(-0.03, 0.03)) if inner else (1.0, 1.0))
        cs, sn = math.cos(th), math.sin(th)
        ring = []
        for cu, cv, _, g in sec:
            if g:
                d = rng.uniform(-grain, grain * 0.7)
                cu, cv = cu + g[0] * d, cv + g[1] * d
            cu, cv = cu * su, cv * sv
            ring.append(centre + u * (cu * cs - cv * sn) + v * (cu * sn + cv * cs))
        rings.append(ring)
    # end rings onto their cut planes (along the axis)
    for k, nrm, _, _ in ends:
        P = p0 if k == 0 else p1
        rings[k] = [q + ax * ((P - q).dot(nrm) / ax.dot(nrm)) for q in rings[k]]
    vr = [[bm.verts.new(q) for q in r] for r in rings]
    m = len(sec)
    faces = {"f": [], "c": [], "e": []}
    for k in range(n):
        for i in range(m):
            j = (i + 1) % m
            faces[sec[i][2]].append(bm.faces.new((vr[k][i], vr[k][j], vr[k + 1][j], vr[k + 1][i])))
    allv = [v_ for r in vr for v_ in r]
    for k, nrm, cap, pt in ends:
        P = p0 if k == 0 else p1
        ring = vr[k]
        if pt:
            base = P + nrm * pt[1]
            if pt[0] == "pyramid":
                ou, ov = (pt[2], pt[3]) if len(pt) > 3 else (0.0, 0.0)
                apex = bm.verts.new(base + u * ou * W + v * ov * T)
                allv.append(apex)
                for i in range(m):
                    faces["e"].append(bm.faces.new((ring[i], ring[(i + 1) % m], apex)))
            else:
                ridge, ou = pt[2], (pt[3] if len(pt) > 3 else 0.0)
                tips = [bm.verts.new(base + u * ou * W + v * s * ridge * T) for s in (-1.0, 1.0)]
                allv += tips
                tip = [tips[1] if cv > 0 else tips[0] for _, cv, _, _ in sec]
                for i in range(m):
                    j = (i + 1) % m
                    if tip[i] is tip[j]:
                        faces["e"].append(bm.faces.new((ring[i], ring[j], tip[i])))
                    else:
                        faces["e"].append(bm.faces.new((ring[i], ring[j], tip[j], tip[i])))
            continue
        if cap is None:
            su, sv, push = 1 - 1.3 * c / W, 1 - 1.3 * c / T, 0.75 * c
        else:
            su, sv, push = cap
        top = []
        for cu, cv, _, _ in sec:
            q = P + u * cu * su + v * cv * sv
            q = q + ax * ((P - q).dot(nrm) / ax.dot(nrm)) + nrm * push
            top.append(bm.verts.new(q))
        mid = bm.verts.new(P + nrm * push * (1.0 if cap is None else 1.12))
        allv += top + [mid]
        for i in range(m):
            j = (i + 1) % m
            faces["e"].append(bm.faces.new((ring[i], ring[j], top[j], top[i])))
            faces["e"].append(bm.faces.new((top[i], top[j], mid)))
    allf = faces["f"] + faces["c"] + faces["e"]
    bmesh.ops.recalc_face_normals(bm, faces=allf)
    a._finish(allv, WOOD)
    li, ei = a._mi(WOOD_LIGHT), a._mi(WOOD_END)
    for f_ in faces["c"]:
        f_.material_index = li
    for f_ in faces["e"]:
        f_.material_index = ei
    # long faces into triangles now (whatever runs the union then sees fixed facets): the diagonal that keeps the
    # fold convex, so the grain breaks read as ridges, not dents
    quads = [f_ for f_ in faces["f"] + faces["c"] + faces["e"] if f_.is_valid and len(f_.verts) == 4]
    bmesh.ops.triangulate(bm, faces=quads, quad_method="BEAUTY")
    return allv


def pair(a, p0, p1, w, t, gap_axis, seed, stagger=(0.0, 0.0), ends=(None, None), ends_b=None, t_b=None, **kw):
    """Two boards fused side by side (the sheet's split timber): offset +-(t/2 - 0.05) along gap_axis, so their
    chamfers meet in a V groove; the second board's ends shifted by stagger (studs along the axis, + longer)."""
    p0, p1 = Vector(p0), Vector(p1)
    g = Vector(gap_axis).normalized()
    ax = (p1 - p0).normalized()
    t_b = t_b or t
    off_a, off_b = g * (t / 2 - 0.05), -g * (t_b / 2 - 0.05)
    side = kw.pop("side", (0, 0, 1))
    vs = board(a, p0 + off_a, p1 + off_a, w, t, side=side, seed=seed, end0=ends[0], end1=ends[1], **kw)
    eb = ends_b or ends
    vs += board(a, p0 + off_b - ax * stagger[0], p1 + off_b + ax * stagger[1], w * 0.96, t_b, side=side,
                seed=seed + 1, end0=eb[0], end1=eb[1], **kw)
    return vs


def _up(foot, length, lean_x=0.0, lean_y=0.0):
    """The top of an upright of this length from foot, leaning lean_x degrees towards +X and lean_y towards +Y."""
    d = Vector((math.tan(math.radians(lean_x)), math.tan(math.radians(lean_y)), 1.0)).normalized()
    return Vector(foot) + d * length


# Upright tops (verifier round 1: the sheet's uprights end in sharp points, not domed or flat tops):
PYRAMID = dict(point=("pyramid", 0.85, 0.1, -0.1))   # hewn post end: four sloped faces to one apex, a little off-centre
CHISEL = dict(point=("chisel", 0.8, 0.45, 0.15))     # plank top: the narrow sides slope to a short ridge, gable point


# ---- the wood parts (build frame) ---------------------------------------------------------------------------------
# The beam runs across the front, its left end raised on the stub block, its right end on the ground; turned about
# 11 degrees in plan (left end further back), sloping about 11 degrees. Two boards 1.5 tall x 1.15 thick, fused.
BEAM = ((-3.45, -1.05, 1.5 + 0.75), (3.55, -2.4, -0.12 + 0.75))   # centre line (bottom + half the height)


def wood_front(a):
    """Wood Base (Front): the long fused beam and the stub block under its left end."""
    p0, p1 = (Vector(p) for p in BEAM)
    ax = (p1 - p0).normalized()
    gap = Vector((0, 0, 1)).cross(ax).normalized()            # horizontal, square to the beam (towards the back)
    pair(a, p0, p1, 1.5, 1.15, gap, 12011, stagger=(-0.35, 0.45),
         ends=({"cut": (12.0, -22.0)}, {"cut": (-8.0, 28.0)}),
         ends_b=({"cut": (-6.0, -18.0)}, {"cut": (10.0, 20.0)}))
    # stub block: squat, lying along the beam under its left end, an oblique outer end
    board(a, (-3.8, -1.75, 0.82), (-1.85, -2.1, 0.82), 1.85, 1.9, side=(0, 0, 1), seed=12013,
          end0={"cut": (-24.0, 18.0)}, end1={"cut": (20.0, -10.0)})


def wood_back(a):
    """Wood Base (Rear) and the centre seat.
    - Seat: three boards side by side under the nodule (the outer two rolled in: a shallow cradle), filling the whole
      footprint under its lower half, so from below the base is one flat block of wood (Detail C; verifier round 1:
      the amber showed under the nest).
    - Rear block: the sheet's chunky block split at one end, two halves fused with a V notch and staggered chisel
      tops. In the hero it stands on end at the front right, leaning out past the amber's right flank (the hero
      views' two right-hand uprights, about 0.49 and 0.6 H, and the rear views' short upright at that side); its foot
      rests against the seat's end."""
    board(a, (-1.95, -1.3, 0.8), (3.0, -1.5, 0.8), 1.8, 1.6, side=(0, 0.25, 1), seed=12021,
          end0={"cut": (-14.0, 20.0)}, end1={"cut": (10.0, -16.0)})
    board(a, (-1.75, 0.1, 0.85), (3.15, 0.05, 0.85), 1.9, 1.6, side=(0, 0, 1), seed=12022,
          end0={"cut": (12.0, 8.0)}, end1={"cut": (-8.0, 14.0)})
    board(a, (-1.6, 1.5, 0.82), (2.9, 1.7, 0.82), 1.85, 1.55, side=(0, -0.25, 1), seed=12023,
          end0={"cut": (16.0, -10.0)}, end1={"cut": (-12.0, 22.0)})
    # a short chisel-pointed upright at the back right, its foot in the seat's back board (round 1: the amber showed
    # too much from the side and rear three-quarter; the sheet's rear views show a short upright, about 0.55 H, over
    # lying blocks at that side). From the front it stays behind the nodule's right flank.
    foot = Vector((2.25, 1.85, -0.25))
    board(a, foot, _up(foot, 3.35, 7.0, 4.0), 1.9, 1.1, side=(0, 1, 0), seed=12027,
          end1={"point": ("chisel", 0.6, 0.45, 0.2)})
    foot = Vector((3.05, -1.0, -0.25))
    top = _up(foot, 3.0, 9.0, 2.0)
    ax = (top - foot).normalized()
    pair(a, foot, top, 2.5, 0.95, Vector((0.35, 0.94, 0)).cross(ax), 12025, stagger=(0.0, 0.8),
         side=(0.35, 0.94, 0), ends=(None, {"point": ("chisel", 0.55, 0.45, -0.2)}),
         ends_b=(None, {"point": ("chisel", 0.65, 0.45, 0.25)}))


def wood_left(a):
    """Side Wood (Left): the slim hewn spire standing behind the beam's raised end (pyramid point), the shorter
    chisel-pointed plank behind it, the lying split slab at its foot and the lying square block running back from
    the spire towards the tepee."""
    foot = Vector((-3.05, 0.75, -0.25))
    board(a, foot, _up(foot, 4.85, -6.0, -2.0), 1.05, 1.05, side=(1, 0, 0), seed=12031, end1=PYRAMID)
    foot = Vector((-2.75, 1.85, -0.25))
    board(a, foot, _up(foot, 3.5, -9.0, 6.0), 1.4, 0.75, side=(0.94, -0.34, 0), seed=12033,
          end1={"cut": (-12.0, 0.0), "point": ("chisel", 0.7, 0.45, -0.25)})
    # lying split slab, along the left side under the beam's raised end
    p0, p1 = Vector((-3.55, -1.2, 0.55)), Vector((-2.8, 1.3, 0.55))
    ax = (p1 - p0).normalized()
    pair(a, p0, p1, 1.3, 1.0, Vector((0, 0, 1)).cross(ax), 12035, stagger=(0.3, -0.4),
         ends=({"cut": (16.0, -14.0)}, {"cut": (-12.0, 20.0)}))
    # lying square block from the spire back towards the tepee
    board(a, (-3.0, 0.95, 0.5), (-1.55, 2.3, 0.5), 1.2, 1.2, side=(0, 0, 1), seed=12038,
          end0={"cut": (0.0, 12.0)}, end1={"cut": (-18.0, 0.0)})


def wood_right(a):
    """Side Wood (Right): the tepee behind the nodule. The tall chisel spire behind its crown, a shorter partner
    fused alongside (pyramid point), and the broad shorter plank leaning out backwards from their feet (the rear
    views' big slab), chisel-pointed too."""
    foot = Vector((0.15, 2.45, -0.25))
    board(a, foot, _up(foot, 5.4, -2.0, -6.0), 2.0, 1.15, side=(1, 0, 0), seed=12041, end1=CHISEL)
    foot = Vector((-1.4, 2.55, -0.25))
    board(a, foot, _up(foot, 4.3, -5.0, -3.0), 1.5, 1.1, side=(1, 0, 0), seed=12043,
          end1={"point": ("pyramid", 0.75, -0.15, 0.1)})
    foot = Vector((-0.45, 2.45, -0.25))
    board(a, foot, _up(foot, 4.0, -6.0, 12.0), 2.5, 1.05, side=(1, 0, 0), seed=12045,
          end1={"cut": (14.0, 0.0), "point": ("chisel", 0.75, 0.45, 0.3)})


PARTS = (("AmberCrystalMain", nodule), ("AmberWoodFront", wood_front), ("AmberWoodBack", wood_back),
         ("AmberWoodLeft", wood_left), ("AmberWoodRight", wood_right))
WOOD_PARTS = [n for n, _ in PARTS if n.startswith("AmberWood")]

NOTES = {
    "Amber": "amber resource: a chunky faceted amber egg (broad facets in rows) sunk in a nest of weathered split "
             "timber - a long fused beam low across the front on a stub block, a hewn post and plank at the left, a "
             "split upright pair at the right, a three-plank tepee behind; one closed mesh, flat base. VFX: "
             "crystal_glow (steady soft amber PointLight in front of the nodule, shadows on) and 3 ore_glint "
             "(sparse amber twinkles at the upper +X flank's light facet junctions)",
    "AmberCrystalMain": "Amber Nodule (main crystal): cut-gem egg of broad facets in rows (crown, upper ring, belt, "
                        "lower ring, blunt bottom)",
    "AmberWoodFront": "Wood Base (Front): a long beam of two fused split boards (V groove, staggered oblique ends) "
                      "on a squat stub block",
    "AmberWoodBack": "Wood Base (Rear): a chunky block split at one end (standing at the front right in the hero), "
                     "plus the centre seat (two boards whose tops make a shallow V)",
    "AmberWoodLeft": "Side Wood (Left): hewn upright post with a pyramid top, a broad plank behind it, a lying split "
                     "slab and a lying square block",
    "AmberWoodRight": "Side Wood (Right): tall chisel-topped plank, a shorter fused partner and a broad plank "
                      "leaning out from their feet",
}


# ---- stage 4: colour regions, blends and Tint mottling ------------------------------------------------------------
# Applied to each finished part mesh (after its cleanup, polish and UVs: only material indices and the Tint attribute
# change); the hero inherits it through _paste. Every field is a position (the nodule's own frame, or the shared
# build frame for the wood); no colour is ever chosen by which way a face points.
#
# Amber: a "core" field per facet (coplanar triangles kept together, so each facet is one main tone): up the stone,
# minus the distance from a core point inside it (upper, right of centre, a little forward), plus broad noise. Facets
# are ranked by it and the rank (area fraction, low -> high) is graded dark -> mid over AMBER_LOW and mid -> light over
# AMBER_HIGH with the 25/50/75 % in-between keys, so the sheet's hue shares come out whatever the facet sizes are and
# neighbours step through in-between tones. In facets of two or more triangles the triangle lowest in the field drops
# one or two steps darker: the sheet's angular inclusions, without splitting any face.
AMBER_FIELD = dict(core=(0.25, -0.1, 0.6), up=0.3, near=0.7, noise=0.3, scale=0.35, seed=12061,
                   crown=(0.82, 0.6))   # above 0.82 of the height the field drops (up to 0.4 at the top): the
                                        # sheet's top view shows the crown orange, the yellow sits on the upper flank
AMBER_LOW = (0.0, 0.2)         # rank band of the dark -> mid grade
AMBER_HIGH = (0.34, 1.0)       # rank band of the mid -> light grade
AMBER_INCL_BIG = 1.5           # facets over this area (studs^2) get a two-step inclusion, smaller ones one step
# verifier round 1 (stage 4 fixes): inclusions both ways and glowing seams
AMBER_INCL_LIGHT = dict(level=0.1, min_rank=0.3, seed=12065)   # a facet's other patch goes a step LIGHTER where a
                                                               # broad noise over the patch centres is above level
# seam strips (one side of each facet edge) step up the ladder by facet rank: (rank from, steps); the ladder ends in
# light -> glow 50 % -> glow, so in the core the lines read pale yellow and lower down they fade to a faint edge
SEAM_STEPS = ((0.0, 0), (0.2, 1), (0.5, 2), (0.8, 3))
AMBER_MOTTLE = dict(amp=0.03, scale=0.9, seed=12063)       # per facet, no per-triangle jitter
AMBER_SPEC = 0.0               # Specular IOR Level on every amber key (see colour_nodule)
# Wood: grain streaks along each board's own axis (noise stretched along the board: GRAIN scales along / across),
# graded wood -> wood_dark; chamfer strips wood -> wood_light by a second grain noise (mostly 25-75 %); cut ends
# wood_end; the V grooves and creases where one board meets another (a face within GROOVE of another board's box)
# towards wood_dark; floor cuts of uprights are end grain; a warm bleed on the broad faces within WARM_REACH of the
# nodule. Then broad Tint mottling (each board already has its own +-5 % Tint from mk's tint_var).
GRAIN = dict(along=0.15, across=1.2, level=0.4, width=0.5, seed=12071)
GRAIN_LIGHT = dict(start=0.2, span=0.8)   # the other end of the same grain noise (grain below -start): lighter worn
                                          # streaks, wood -> wood_light over -grain start .. start + span
CHAMFER_WEAR = dict(level=-0.3, seed=12073)   # chamfer strips are full wood_light (the sheet's bright tan edge
                                              # lines), 75 % where the wear noise along the board is below level
GROOVE = (0.05, 0.5)           # reach (studs) and the wood_dark mix the groove / crease faces take
# verifier round 1: angular chips on the broad faces, lighter (worn) and darker (knocks), from a second, isotropic
# noise in each board's frame (patches of a few triangles); graded over CHIP_BAND so a chip's rim is an in-between step
CHIP = dict(scale=1.1, light=0.36, dark=-0.32, band=0.12, light_to=0.75, dark_to=0.75, seed=12077)
WARM_REACH = 0.7
WOOD_MOTTLE = dict(amp=0.07, scale=0.65, jitter=0.012, seed=12075)


def _ladder():
    return ([A_DARK] + [K.mix_key(A_DARK, A_MID, t) for t in (0.25, 0.5, 0.75)] + [A_MID] +
            [K.mix_key(A_MID, A_LIGHT, t) for t in (0.25, 0.5, 0.75)] + [A_LIGHT])


def _seam_ladder():
    """_ladder() plus the seam-only glow steps above light."""
    return _ladder() + [K.mix_key(A_LIGHT, A_GLOW, 0.5), A_GLOW]


def _facets(faces):
    """Coplanar, edge-connected triangles grouped into the nodule's facets."""
    seen, out = set(), []
    for f in faces:
        if f in seen:
            continue
        g, stack = [], [f]
        seen.add(f)
        while stack:
            x = stack.pop()
            g.append(x)
            for e in x.edges:
                for y in e.link_faces:
                    if y not in seen and y.normal.dot(f.normal) > 0.9995:
                        seen.add(y)
                        stack.append(y)
        out.append(g)
    return out


def colour_nodule(o):
    p = m011._Paint(o, off=o["m012_offset"])
    faces = list(p.bm.faces)
    H = max(v.co.z for v in p.bm.verts) + p.off.z
    cf = AMBER_FIELD["core"]
    core = Vector((cf[0] * NOD["w"], cf[1] * NOD["d"], cf[2] * H))
    nf = K.noise_field(scale=AMBER_FIELD["scale"], seed=AMBER_FIELD["seed"])

    z0, drop = AMBER_FIELD["crown"]

    def field(c):
        return (AMBER_FIELD["up"] * c.z / H - AMBER_FIELD["near"] * (c - core).length / H +
                AMBER_FIELD["noise"] * nf(c) - drop * max(0.0, c.z / H - z0) / (1.0 - z0))
    groups = []
    reg = nod_regions(o)            # stage 1 round 2: seam strips and inclusion patches (NOD_FACES)
    # facets by the build's own record (the merged facets are planar only to NOD_MERGE degrees, so grouping by
    # normal split some into per-triangle bands); faces it doesn't know (none expected) fall back to normals
    by_id = {}
    for f in faces:
        if f.index in reg:
            by_id.setdefault(reg[f.index][1], []).append(f)
    known = {f for g in by_id.values() for f in g}
    for g in list(by_id.values()) + _facets([f for f in faces if f not in known]):
        area = sum(f.calc_area() for f in g)
        c = sum((f.calc_center_median() * f.calc_area() for f in g), Vector()) / area + p.off
        groups.append((field(c), area, c, g))
    groups.sort(key=lambda x: x[0])
    total = sum(x[1] for x in groups)
    rank, acc = {}, 0.0
    for fv, area, c, g in groups:
        for f in g:
            rank[f] = (acc + area / 2) / total
        acc += area
    m011._grade(p, [f for f in faces if rank[f] < AMBER_LOW[1]], A_DARK, A_MID, rank.get,
                sum(AMBER_LOW) / 2, AMBER_LOW[1] - AMBER_LOW[0])
    m011._grade(p, [f for f in faces if rank[f] >= AMBER_LOW[1]], A_MID, A_LIGHT, rank.get,
                sum(AMBER_HIGH) / 2, AMBER_HIGH[1] - AMBER_HIGH[0])
    lad = _ladder()
    slad = _seam_ladder()
    incl = [0, 0]
    rng_i = random.Random(AMBER_INCL_LIGHT["seed"])
    ioff = Vector((rng_i.uniform(0, 100), rng_i.uniform(0, 100), rng_i.uniform(0, 100)))
    from mathutils import noise
    for fv, area, c, g in groups:
        i = lad.index(p.key(g[0]))
        pats = {}
        for x in g:
            r = reg.get(x.index)
            if r and r[0] == "patch":
                pats.setdefault((r[1], r[2]), []).append(x)
        if len(g) < 2 or (i < 4 and not pats):
            continue
        pc = {k: sum((x.calc_center_median() for x in fs), Vector()) / len(fs) + p.off for k, fs in pats.items()}
        if pats:            # the facet's patch lowest in the field: an angular darker inclusion
            dk = min(pats, key=lambda k: field(pc[k]))
            pick = pats[dk]
        else:
            dk, pick = None, [min(g, key=lambda x: field(x.calc_center_median() + p.off))]
        step = 3 if area > AMBER_INCL_BIG else 2
        for f in pick:
            f.material_index = p._mi(lad[max(0, i - step)])
        incl[0] += 1
        # ... and, in the lighter facets, another patch a step lighter where a broad noise says so (the sheet's
        # inclusions are both lighter and darker angular shapes)
        rest = [k for k in pats if k != dk]
        if rest and rank[g[0]] >= AMBER_INCL_LIGHT["min_rank"]:
            lk = max(rest, key=lambda k: noise.noise(pc[k] * 0.9 + ioff))
            if noise.noise(pc[lk] * 0.9 + ioff) > AMBER_INCL_LIGHT["level"]:
                for f in pats[lk]:
                    f.material_index = p._mi(slad[min(len(lad) - 1, i + 1)])
                incl[1] += 1
    # glowing seams: along each facet edge the border strip on ONE side (the facet with the higher number) steps up
    # the seam ladder by its facet's rank (SEAM_STEPS), so the line is one strip (0.1 stud) wide, pale yellow in the
    # core and only a faint lighter edge low down: glowing lines, not a cage
    seams = 0
    for f in faces:
        r = reg.get(f.index)
        if not (r and r[0] == "seam"):
            continue
        # the strip's facet neighbours: facets touching its outer verts (its inner triangles share only a vert with
        # the next facet). The facet a strip triangle borders most is the one across its edge.
        cnt = {}
        for v in f.verts:
            for x in v.link_faces:
                if x.index in reg and reg[x.index][1] != r[1]:
                    cnt[reg[x.index][1]] = cnt.get(reg[x.index][1], 0) + 1
        other = {max(cnt, key=cnt.get)} if cnt else set()
        if other and r[1] > min(other):
            st = max(s for r0, s in SEAM_STEPS if rank[f] >= r0)
            f.material_index = p._mi(slad[min(len(slad) - 1, slad.index(p.key(f)) + st)])
            seams += 1
    # Tint: broad per-facet brightness drift (each facet stays one flat tone)
    rng = random.Random(AMBER_MOTTLE["seed"])
    off = Vector((rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(0, 100)))
    from mathutils import noise
    for fv, area, c, g in groups:
        k = 1.0 + AMBER_MOTTLE["amp"] * 1.6 * noise.noise(c * AMBER_MOTTLE["scale"] + off)
        for f in g:
            for l in f.loops:
                t = l[p.tint_layer][0] * k
                l[p.tint_layer] = (t, t, t, 1.0)
    counts = {}
    for f in faces:
        counts[p.key(f)] = counts.get(p.key(f), 0) + 1
    p.done()
    # no specular on any amber key (the in-between keys are made on first use with flintkit's default 0.2, and even
    # the foliage 0.06 leaves the crown, seen at a grazing angle, reflecting the studio sky as a cream-white facet)
    for m in o.data.materials:
        b = m.node_tree.nodes.get("Principled BSDF") if m.node_tree else None
        if b and "Specular IOR Level" in b.inputs:
            b.inputs["Specular IOR Level"].default_value = AMBER_SPEC
    return {"facets": len(groups), "inclusions": incl, "seam_faces": seams, "keys": counts}


def _box_d(b, c):
    """Signed distance from c to a board's box (its centre line +- half width / thickness, 0..L along it): negative
    inside."""
    q = c - b["p0"]
    s, a, w = q.dot(b["ax"]), q.dot(b["u"]), q.dot(b["v"])
    d = (max(-s, s - b["L"]), abs(a) - b["W"], abs(w) - b["T"])
    out = Vector([max(x, 0.0) for x in d]).length
    return out if out > 0 else max(d)


def _nodule_tree():
    """The nodule's surface where the hero puts it, in the build frame."""
    from mathutils.bvhtree import BVHTree
    n = bpy.data.objects["AmberCrystalMain"]
    m = _nod_matrix() @ _frame(n)
    return BVHTree.FromPolygons([m @ v.co for v in n.data.vertices], [list(pl.vertices) for pl in n.data.polygons])


def colour_wood(o, tree):
    from mathutils import noise
    p = m011._Paint(o, off=o["m012_offset"])
    boards = [b for b in BOARDS.values() if b["part"] == o.name]
    faces = list(p.bm.faces)
    cls = {f: {WOOD: "f", WOOD_LIGHT: "c", WOOD_END: "e"}.get(p.key(f), "f") for f in faces}
    own, near2 = {}, {}
    for f in faces:
        c = p.at(f)
        ds = sorted(((_box_d(b, c), k) for k, b in enumerate(boards)), key=lambda x: abs(x[0]))
        own[f] = boards[ds[0][1]]
        near2[f] = abs(ds[1][0]) if len(ds) > 1 else 9.0
        # the floor cut (Detail C): end grain under an upright, a sawn long face under a lying board
        if all(abs(v.co.z + p.off.z) < 1e-3 for v in f.verts):
            cls[f] = "e" if abs(own[f]["ax"].z) > 0.6 else "f"
    offs = {}

    def grain(f, seed):
        b = own[f]
        k = id(b)
        if (k, seed) not in offs:
            r = random.Random(seed + len(offs))
            offs[(k, seed)] = Vector((r.uniform(0, 100), r.uniform(0, 100), r.uniform(0, 100)))
        q = p.at(f) - b["p0"]
        loc = Vector((q.dot(b["ax"]) * GRAIN["along"], q.dot(b["u"]) * GRAIN["across"],
                      q.dot(b["v"]) * GRAIN["across"]))
        return noise.noise(loc + offs[(k, seed)])
    broad = [f for f in faces if cls[f] == "f"]
    cham = [f for f in faces if cls[f] == "c"]
    ends = [f for f in faces if cls[f] == "e"]
    for f in ends:
        f.material_index = p._mi(WOOD_END)
    # grain streaks along the board
    gv = {f: grain(f, GRAIN["seed"]) for f in broad}
    m011._grade(p, broad, WOOD, WOOD_DARK, gv.get, GRAIN["level"], GRAIN["width"])
    # ... and lighter worn streaks at the other end of the same noise (up to 50 % wood_light)
    s0, span = GRAIN_LIGHT["start"], GRAIN_LIGHT["span"]
    lo = [f for f in broad if -gv[f] > s0]
    m011._grade(p, lo, WOOD, WOOD_LIGHT, lambda f: -gv[f], s0 + span / 2, span)
    # angular chips: lighter worn chips and darker knocks, graded at their rims
    cv = {}
    for f in broad:
        b = own[f]
        k = (id(b), CHIP["seed"])
        if k not in offs:
            r = random.Random(CHIP["seed"] + len(offs))
            offs[k] = Vector((r.uniform(0, 100), r.uniform(0, 100), r.uniform(0, 100)))
        q = p.at(f) - b["p0"]
        cv[f] = noise.noise(Vector((q.dot(b["ax"]), q.dot(b["u"]), q.dot(b["v"]))) * CHIP["scale"] + offs[k])
    hb = CHIP["band"] / 2
    chips = [0, 0]
    for f in broad:
        if cv[f] > CHIP["light"] + hb:              # chip core, then a one-step rim
            t = CHIP["light_to"]
        elif cv[f] > CHIP["light"] - hb:
            t = CHIP["light_to"] - 0.25
        else:
            t = None
        if t:
            f.material_index = p._mi(K.mix_key(WOOD, WOOD_LIGHT, t))
            chips[0] += 1
            continue
        if cv[f] < CHIP["dark"] - hb:
            t = CHIP["dark_to"]
        elif cv[f] < CHIP["dark"] + hb:
            t = CHIP["dark_to"] - 0.25
        if t:
            f.material_index = p._mi(K.mix_key(WOOD, WOOD_DARK, t))
            chips[1] += 1
    # chamfer strips: the bright tan edge lines, full wood_light, 75 % where the wear noise along the board dips
    for f in cham:
        worn = grain(f, CHAMFER_WEAR["seed"]) < CHAMFER_WEAR["level"]
        f.material_index = p._mi(K.mix_key(WOOD, WOOD_LIGHT, 0.75) if worn else WOOD_LIGHT)
    # V grooves and creases where boards meet
    groove = [f for f in broad + cham if near2[f] < GROOVE[0]]
    for f in groove:
        f.material_index = p._mi(K.mix_key(WOOD, WOOD_DARK, GROOVE[1]))
    # warm bleed by the amber (broad faces only; chamfers and ends keep their own keys)
    d = {}
    for f in broad:
        hit = tree.find_nearest(p.at(f))
        d[f] = hit[3] if hit[0] is not None else 9.0
    warm = [f for f in broad if d[f] < WARM_REACH and f not in set(groove)]
    m011._grade(p, warm, WOOD, WOOD_WARM, lambda f: -d[f], -WARM_REACH / 2, WARM_REACH)
    m011._mottle(p, faces, **WOOD_MOTTLE)
    counts = {}
    for f in faces:
        counts[p.key(f)] = counts.get(p.key(f), 0) + 1
    p.done()
    return {"boards": len(boards), "groove": len(groove), "warm": len(warm), "chips": chips, "keys": counts}


def colour_parts(objs):
    out = {"AmberCrystalMain": colour_nodule(objs["AmberCrystalMain"])}
    tree = _nodule_tree()
    for name in WOOD_PARTS:
        out[name] = colour_wood(objs[name], tree)
    return out


# ---- assembly -----------------------------------------------------------------------------------------------------
def _bottom_centre(o):
    xs = [v.co.x for v in o.data.vertices]
    ys = [v.co.y for v in o.data.vertices]
    zs = [v.co.z for v in o.data.vertices]
    return Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))


def _frame(o):
    """Part mesh coordinates -> its build frame (the nodule's own upright frame, or the shared one for the wood)."""
    return Matrix.Translation(Vector(o["m012_offset"]))


def hero(a):
    for name in WOOD_PARTS:
        o = bpy.data.objects[name]
        m011._paste(a, o, _frame(o))
    n = bpy.data.objects["AmberCrystalMain"]
    m011._paste(a, n, _nod_matrix() @ _frame(n))


# ---- stage 5: lighting (see M012_spec.md, "Stage 5+6") -------------------------------------------------------------
# No emissive faces. The sheet's amber is lit from within (bright seams, shade facets staying saturated orange) but
# casts no halo on the wood. Emission >= 1.0 exports as Neon in one flat colour per key, erasing the graded
# light / mid / dark facets (and blooming); emission between 0 and 1 doesn't glow in Roblox and only drops the Tint.
# The "lit from within" in game is one soft amber PointLight (crystal_glow socket) in front of the nodule, above the
# front beam, outside the solid: build frame (1.2, -4.6, 4.4), 1.84 studs from the nearest amber facet and 3.0 from
# the nearest wood (BVH on the hero). At 0.9 stud (the study's first suggestion, (0.9, -3.6, 3.4)) the preview showed
# a round hot spot on the lower front facets (+28 levels at the 99th percentile), a "light bulb" the sheet doesn't
# have; from here the lift is spread evenly over the facets (+15) and the wood warms only slightly (+3). Shadows on,
# so the nodule keeps it off the tepee behind; range 8 keeps the pool on the ground in front small.
STUDIO_LIGHT = dict(pos=(1.2, -4.6, 4.4), color="#FFA63A", brightness=0.7, range=8.0, shadows=True)

# ---- stage 6: VFX sockets on the hero -----------------------------------------------------------------------------
# ore_glint: sparse amber twinkles at the facet junctions of the upper +X flank's light facets (amber_light /
# amber_mid_x_amber_light_75), where the sheet's star glints sit. Each entry: (a build-frame point near the junction,
# snapped to the nearest nodule vertex through _nod_matrix(), rate per second, particle peak size in studs). The box
# hugs the surface: the vertex plus the points GLINT_REACH along each of its hull edges, padded by GLINT_PAD.
GLINTS = (((2.11, -0.92, 6.14), 0.5, 0.6),       # upper-right junction of three light facets (the main glint)
          ((0.93, -2.5, 5.77), 0.35, 0.5),       # upper front-centre junction (light / light_75 / light)
          ((2.77, 0.09, 5.16), 0.25, 0.45))      # +X flank junction of four light / light_75 facets (not the mid
#                                                  junction at (2.62, -1.65, 4.45): the split block's top touches it)
GLINT_REACH = 0.45
GLINT_PAD = 0.05
GLINT = {"name": "Glint", "texture": "spark_diamond", "color": ["#FFF4C8", "#FEC029"], "transparency": [0.1, 1.0],
         "lifetime": [0.5, 0.8], "speed": [0, 0], "spread": 0, "light_emission": 1.0, "rotation": [0, 90]}


def _glint_fx(n):
    """Stage 6 ore_glint sockets (kind, build-frame loc, overrides) for M.mk's fx, fitted per GLINTS entry."""
    m = _nod_matrix() @ _frame(n)
    bm = bmesh.new()
    bm.from_mesh(n.data)
    out = []
    for at, rate, size in GLINTS:
        v = min(bm.verts, key=lambda x: ((m @ x.co) - Vector(at)).length)
        p0 = m @ v.co
        pts = [p0]
        for e in v.link_edges:
            q = m @ e.other_vert(v).co
            pts.append(p0.lerp(q, min(1.0, GLINT_REACH / (q - p0).length)))
        lo = Vector([min(p[i] for p in pts) - GLINT_PAD for i in range(3)])
        hi = Vector([max(p[i] for p in pts) + GLINT_PAD for i in range(3)])
        d = hi - lo
        em = dict(GLINT, rate=rate, size=[0, size, 0],
                  shape=[round(d.x, 2), round(d.z, 2), round(d.y, 2)])   # Roblox XYZ: x, height, depth
        out.append(("ore_glint", tuple(round(c, 3) for c in (lo + hi) / 2), {"emitters": [em]}))
    bm.free()
    return out


def _vfx(n):
    """Stages 5+6: the hero's sockets (build frame), the amber light first."""
    light = {k: STUDIO_LIGHT[k] for k in ("color", "brightness", "range", "shadows")}
    light["flicker"] = False
    return [("crystal_glow", STUDIO_LIGHT["pos"], {"light": light})] + _glint_fx(n)


def _drop_inner(o):
    """Delete closed pockets left inside the solid by the union (a V groove between two fused boards, roofed over by
    a third piece, seals into a hidden tunnel): every shell but the largest whose centre lies inside the largest
    (ray parity). Returns how many went."""
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    if n < 2:
        bm.free()
        return 0
    area = [0.0] * n
    for f in bm.faces:
        area[ids[f.index]] += f.calc_area()
    main = max(range(n), key=lambda k: area[k])
    mf = [f for f in bm.faces if ids[f.index] == main]
    vs = list({v for f in mf for v in f.verts})
    vi = {v: i for i, v in enumerate(vs)}
    tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in mf])
    kill, gone = [], 0
    for k in range(n):
        if k == main:
            continue
        fs = [f for f in bm.faces if ids[f.index] == k]
        c = sum((f.calc_center_median() for f in fs), Vector()) / len(fs)
        hits, p, d = 0, c.copy(), Vector((0.31, 0.17, 0.93)).normalized()
        while True:
            loc, _, _, _ = tree.ray_cast(p, d)
            if loc is None:
                break
            hits += 1
            p = loc + d * 1e-4
        if hits % 2 or area[k] < 0.02 * area[main]:       # inside, or a crumb by the joins
            kill += fs
            gone += 1
    if kill:
        bmesh.ops.delete(bm, geom=kill, context="FACES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bm.to_mesh(o.data)
    bm.free()
    return gone


def _force_slivers(o, lim=3.0, max_len=0.25):
    """Last resort for the few needles and caps the sliver pass leaves where three boards' unions meet at grazing
    angles: collapse each one's shortest edge (up to max_len studs) onto its better-connected end, if the collapse
    keeps the mesh manifold (link condition) and leaves the ground flat. Returns the number collapsed."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    n = 0
    for _ in range(12):
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY")
        bad = [f for f in bm.faces if m011._fmin(f) < math.radians(lim)]
        if not bad:
            break
        done = False
        for f in bad:
            if not f.is_valid or len(f.verts) != 3:
                continue
            # a point left inside one triangle split three ways: dissolve it (its three neighbours make one face)
            v3 = next((v for v in f.verts if len(v.link_edges) == 3 and abs(v.co.z) > 1e-4
                       and all(len(x.verts) == 3 for x in v.link_faces)), None)
            if v3:
                bmesh.ops.dissolve_verts(bm, verts=[v3])
                n += 1
                done = True
                continue
            es = sorted(f.edges, key=lambda x: x.calc_length())
            e, long_ = es[0], es[-1]
            if e.calc_length() > 0.12 * long_.calc_length() and len(long_.link_faces) == 2:
                # a cap (no short edge): flip its long edge if that leaves both triangles better
                g = next(x for x in long_.link_faces if x is not f)
                if len(g.verts) == 3:
                    A, B = long_.verts
                    c = next(v for v in f.verts if v not in (A, B))
                    d = next(v for v in g.verts if v not in (A, B))
                    old = min(m011._fmin(f), m011._fmin(g))
                    new = min(m011._min_angle([A.co, c.co, d.co]), m011._min_angle([c.co, B.co, d.co]))
                    if new > old and not any(d in {x.other_vert(c) for x in c.link_edges} for _ in (0,)):
                        if bmesh.ops.rotate_edges(bm, edges=[long_], use_ccw=False)["edges"]:
                            n += 1
                            done = True
                            continue
            if e.calc_length() > max_len or len(e.link_faces) != 2:
                continue
            a, b = e.verts
            na = {x.other_vert(a) for x in a.link_edges}
            nb = {x.other_vert(b) for x in b.link_edges}
            if len(na & nb) != 2:
                continue
            on_a, on_b = abs(a.co.z) < 1e-4, abs(b.co.z) < 1e-4
            keep = a if on_a and not on_b else b if on_b and not on_a else max((a, b), key=lambda v: len(v.link_edges))
            bmesh.ops.pointmerge(bm, verts=[a, b], merge_co=keep.co.copy())
            n += 1
            done = True
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-5)
        if not done:
            break
    n += _nudge(bm, lim)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    return n


def _nudge(bm, lim, steps=(0.004, 0.008, 0.015, 0.025, 0.04, 0.06)):
    """Slivers no flip or collapse can take (their fix would make an edge that already exists): move one of their
    corners by a few hundredths of a stud, in the face's plane or out of it, to whichever spot opens every face
    round that corner past lim degrees without turning any of them more than about 25 degrees. Ground verts stay
    on the ground."""
    lim_r = math.radians(lim)
    n = 0
    for f in [f for f in bm.faces if m011._fmin(f) < lim_r]:
        if not f.is_valid or m011._fmin(f) >= lim_r:
            continue
        nf = f.normal.copy()
        best = None
        for v in f.verts:
            ring = list(v.link_faces)
            old = [x.normal.copy() for x in ring]
            e = [(w.co - v.co) for w in f.verts if w is not v]
            dirs = [nf, -nf] + [d.normalized() for d in e if d.length > 1e-9] + \
                   [-d.normalized() for d in e if d.length > 1e-9] + \
                   [nf.cross(d).normalized() for d in e if d.length > 1e-9] + \
                   [-nf.cross(d).normalized() for d in e if d.length > 1e-9]
            home = v.co.copy()
            for s in steps:
                for d in dirs:
                    p = home + d * s
                    if abs(home.z) < 1e-4:
                        p.z = home.z
                    v.co = p
                    ok = True
                    worst = math.pi
                    for x, n0 in zip(ring, old):
                        x.normal_update()
                        if x.normal.length < 1e-9 or x.normal.dot(n0) < 0.9:
                            ok = False
                            break
                        worst = min(worst, m011._fmin(x))
                    if ok and worst > lim_r and (best is None or worst > best[0]):
                        best = (worst, v, p.copy())
                v.co = home
                for x in ring:
                    x.normal_update()
                if best and best[1] is v:
                    break
        if best:
            best[1].co = best[2]
            for x in best[1].link_faces:
                x.normal_update()
            n += 1
    return n


def _finish(o):
    """M.finish, then (finish's merge by distance can turn a near-sliver into a cap) any face left under 3 degrees
    collapsed and finish run again; the part's build-frame offset follows the re-centring."""
    res = M.finish(o, union=False, uv=UV)
    for _ in range(3):
        crumbs = _drop_inner(o)
        if not (crumbs or _thin(o)["under"] or res["nonmanifold_edges"] or res["boundary_edges"]):
            break
        bm = bmesh.new()            # the opening a crumb sat in: close it flat
        bm.from_mesh(o.data)
        bnd = [e for e in bm.edges if e.is_boundary]
        if bnd:
            if not bmesh.ops.holes_fill(bm, edges=bnd)["faces"]:
                bmesh.ops.contextual_create(bm, geom=bnd)      # a twisted little loop holes_fill skips
            bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY")
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(o.data)
        bm.free()
        M.repair_nonmanifold(o)
        _force_slivers(o)
        if "m012_offset" in o:
            o["m012_offset"] = list(Vector(o["m012_offset"]) + _bottom_centre(o))
        res = M.finish(o, union=False, uv=UV)
    return res


POLISH_LIM = 5.0       # stage 2: no corner under this many degrees on any part or the hero


def _tri_quads(bm):
    """Every face over 3 sides into triangles, by the diagonal that keeps the larger smallest corner. A diagonal
    that already exists as an edge elsewhere (a thin wedge left where finish's merge pinched two union creases
    together) can't be cut, since it would double that edge: if both are blocked, the blocking edge is rotated out
    first. Returns the number split."""
    n = 0
    for f in [f for f in bm.faces if len(f.verts) > 3]:
        if not f.is_valid:
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
        bmesh.ops.connect_verts(bm, verts=[p, q])
        n += 1
    return n


def _polish(o):
    """Stage 2 pass after _finish: all faces triangles (_tri_quads), every corner opened past POLISH_LIM by
    _force_slivers' flips, collapses and sub-0.02-stud nudges (ground verts stay on the ground), origin back at the
    bottom centre (the part's build-frame offset follows) and the UVs re-made on the final mesh."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    split = _tri_quads(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    forced = _force_slivers(o, lim=POLISH_LIM)
    bc = _bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        for c in o.children:            # VFX sockets follow the re-centring (as M.finish does)
            c.location -= bc
        if "m012_offset" in o:
            o["m012_offset"] = list(Vector(o["m012_offset"]) + bc)
    o.data.update()
    M.smart_uv(o, **UV)
    return {"split": split, "forced": forced, "uv_cut": _uv_unfold(o)}


def _uv_overlaps(o):
    """Pairs of faces whose UV triangles overlap (as M.uv_stats counts them)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    uv = bm.loops.layers.uv.active
    tris = [[(l[uv].uv.x, l[uv].uv.y) for l in f.loops] for f in bm.faces]
    bm.free()
    boxes = [(min(p[0] for p in t), min(p[1] for p in t), max(p[0] for p in t), max(p[1] for p in t)) for t in tris]
    grid = {}
    for k, b in enumerate(boxes):
        for i in range(int(b[0] // 0.05), int(b[2] // 0.05) + 1):
            for j in range(int(b[1] // 0.05), int(b[3] // 0.05) + 1):
                grid.setdefault((i, j), []).append(k)
    pairs = {(a, b) for lst in grid.values() for i, a in enumerate(lst) for b in lst[i + 1:]}
    return [(a, b) for a, b in pairs if M._tri_overlap(tris[a], tris[b])]


def _uv_unfold(o, rounds=4):
    """Angle-based unwrap folds an island where the union left a shallow S-step (two nearly parallel faces stacked a
    few hundredths apart, dot about 0.99): those faces overlap in UV. Cut the smaller face of each overlapping pair
    out along seams and unwrap again with the same method and margin. Returns the faces cut free."""
    cut = 0
    for _ in range(rounds):
        bad = _uv_overlaps(o)
        if not bad:
            break
        polys = o.data.polygons
        free = {min((a, b), key=lambda i: polys[i].area) for a, b in bad}
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


def _thin(o, lim=3.0):
    """Faces with a corner under lim degrees, and the smallest corner angle on the mesh."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    angs = [m011._fmin(f) for f in bm.faces]
    bm.free()
    return {"under": sum(1 for x in angs if x < math.radians(lim)), "min_deg": round(math.degrees(min(angs)), 2)}


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    objs, audits, cleaned = {}, {}, {}
    BOARDS.clear()
    for name, fn in PARTS:
        _PART[0] = name
        o = M.mk(SHEET, name, fn, subject=TITLE, role="part", notes=NOTES[name], budget=1000, collision="hull")
        off = M._build_offset(fn)
        if fn is nodule:
            o["m012_offset"] = list(off + _bottom_centre(o))
            o["m012_facets"] = NOD.get("facets", 0)
        else:
            M.union_loose(o)
            pockets = _drop_inner(o)
            m004.floor_cut(o, z0=-off.z)            # the ground (build z = 0): a flat base
            cleaned[name] = m011._clean(o, m011._plane_lock((0.0,)), max_move=m011.CLEAN_MOVE)
            pockets += _drop_inner(o)
            cleaned[name]["pockets"] = pockets
            cleaned[name]["forced"] = _force_slivers(o)
            o["m012_offset"] = list(Vector((off.x, off.y, 0.0)) + _bottom_centre(o))
        _finish(o)
        cleaned.setdefault(name, {})["polish"] = _polish(o)
        audits[name] = M.audit(o)
        objs[name] = o
    _PART[0] = None
    coloured = colour_parts(objs)       # stage 4, on the finished parts; the hero inherits it through _paste
    h = M.mk(SHEET, "Amber", hero, subject=TITLE, role="hero", notes=NOTES["Amber"], budget=4000, collision="hull",
             fx=_vfx(objs["AmberCrystalMain"]))
    M.union_loose(h)
    pockets = _drop_inner(h)
    cleaned["Amber"] = m011._clean(h, m011._plane_lock((0.0,)), max_move=m011.CLEAN_MOVE)
    pockets += _drop_inner(h)
    cleaned["Amber"]["pockets"] = pockets
    cleaned["Amber"]["forced"] = _force_slivers(h)
    _finish(h)
    cleaned["Amber"]["polish"] = _polish(h)
    audits["Amber"] = M.audit(h)
    order = [h] + [objs[n] for n, _ in PARTS]
    M.display(NUM, order, TITLE)
    dropped = _drop_unused(order)
    out = {"audit": [{k: M.audit(o)[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges",
                                                     "boundary_edges", "normals", "ngons", "materials")}
                     for o in order],
           "thin": {o.name: _thin(o, POLISH_LIM) for o in order}, "facets": NOD.get("facets"), "cleaned": cleaned,
           "dropped": dropped, "colour": coloured, "problems": K.check(order)}
    if render:
        out["views"] = render_views(order)
    return out


def _drop_unused(objs):
    names = {o.name for o in objs}
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.split(".")[0] in names]
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m012_")]
    out = {"meshes": len(meshes), "materials": sorted(m.name for m in mats)}
    for m in meshes:
        bpy.data.meshes.remove(m)
    for m in mats:
        bpy.data.materials.remove(m)
    for o in objs:
        if o.data.name != o.name and o.name not in bpy.data.meshes:
            o.data.name = o.name
    return out


# exploded shot: each part moved from its place in the hero by (dx, dy, dz), as the sheet lays them out (nodule high
# in the middle, the seat/rear block under it to the right, the front beam low in front, the side groups out wide)
EXPLODE = {"AmberWoodFront": (-0.5, -3.0, 0.0), "AmberWoodBack": (3.0, 1.0, 0.0), "AmberWoodLeft": (-2.5, 0.5, 1.5),
           "AmberWoodRight": (3.5, 1.5, 1.5)}
NOD_EXPLODE_Z = 7.5


def render_views(objs):
    h, nod = objs[0], objs[1]
    parts = objs[1:]
    saved = M.explode(parts, {})
    try:
        x0, y0 = h.location.x + 40, h.location.y
        for o in parts[1:]:
            t = _frame(o).translation
            d = EXPLODE[o.name]
            o.location = (x0 + t.x + d[0], y0 + t.y + d[1], t.z + d[2])
        nod.location = (x0 - 0.4, y0 + 0.2, NOD_EXPLODE_Z)
        bpy.context.view_layer.update()
        extra = {"exploded": (parts, -16, 22)}
        for o in parts:
            extra["part_" + o.name[5:].lower()] = ([o], -25, 18)
        return M.views(NUM, [h], extra=extra)
    finally:
        M.restore(saved)
        M.display(NUM, objs, TITLE)
