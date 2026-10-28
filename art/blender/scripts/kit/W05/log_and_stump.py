"""W05 row 4: LOG AND STUMP (hollow log, cut stump, fallen deadwood).

Hero "FallenHollowLog" (~15 x 8 x 9 studs): a big hollow log lying along X
(yawed 20 degrees, a little past the spec's 12, so its open -X end turns
toward the camera-left/front and the fixed front camera sees into the bore),
built from 11 long bark staves with V grooves between them. The open end
shows the pale plank ends around a deep warm-black bore; the +X end is
snapped into staggered splinters; a Y-forked broken branch rises near the
back; lime moss blankets drape over the top and drip down the front; grey
rocks, spiky grass tufts and a moss ground patch dress the base.

Parts: LogBranchStub, LogMossFoliage, LogShell, LogCutEndCap.
Variants: HollowLog, BrokenLog (snapped end + split top), LowStump.

Technique: `log_tube` lays out the log as one continuous ring mesh along a
local X axis (rings of 5 columns per stave: groove, chamfer, crown, crack,
chamfer), with an inner bore tube and stave-end polygons at each end, so the
same code makes the hero, the variants, the shell, the cut cap (closed by a
concentric ring disc) and the stump (axis turned upright). Open log ends use
`chamfer0`: each staggered plank end gets a broad pale bevel, so the bore sits
in a thick (~1.1-1.2 stud) scalloped heartwood rim. Moss blankets are ragged
pillow grids wrapped around the log axis, studded with rounded moss cushions
(three-ring domes) and leafy sprig clumps, with drip tongues down the front.
Rocks are convex hulls; grass blades are flattened three-sided spikes; fern
clumps are rounded pointed leaves around a low dome.

Colour: ONE palette key per material (w05_bark, w05_heartwood, w05_hollow,
w05_moss, w05_leaf, w05_grass, kit_rock) with a small random per-face Tint
(+/-6%). w05_moss is the moss blanket, cushions and ground patches; w05_leaf
is the sheet's key for the small leafy sprigs on deadwood, here the leafy
clumps and leaf points studding the moss, which give the blankets the
reference's greener lime-leaf read. The light tops and dark grooves of the
reference come from lighting on real V grooves and facets, never from the
paint. All dressing (every moss and leaf face: blankets, cushions, sprigs,
drips, frills, ground patches; grass and ferns) carries kit_nocollide = 1.
"""

import math
import random

import bmesh
from mathutils import Matrix, Vector

SUBJECT = "LogAndStump"
ROW = 4
# Sheet palette (shared by all W05 modules), copied verbatim. kit_rock is an
# existing KIT_PALETTE key and is not redeclared.
PALETTE = {
    "w05_leaf": ("#9CBB1C", 0.8, 0, 0),
    "w05_moss": ("#C6CB1F", 0.9, 0, 0),
    "w05_grass": ("#86AC22", 0.95, 0, 0),
    "w05_bark": ("#A5653A", 0.9, 0, 0),
    "w05_heartwood": ("#F0B26E", 0.85, 0, 0),
    "w05_hollow": ("#1C130F", 0.95, 0, 0),
    "w05_resin": ("#F59A16", 0.25, 0, 1.2),
}

PI = math.pi
YAW = 20  # degrees the variant logs turn their open -X end toward the camera-left/front
HERO_YAW = 20  # the hero (spec ~12): more turn so the fixed front camera sees into the bore
# The sheet's iso cells look a little further round the open end than the
# default -22, so the bore reads as a deep tunnel.
HERO_AZIMUTH = -17  # with the 20 deg yaw: the end seen ~50 deg off its axis, log broadside like the sheet
# The sheet's third cell shows the log broadside from a little left of front,
# branch leaning right and the planked open end visible at the left.
SIDE_AZIMUTH = -10
ZV = Vector((0, 0, 1))
TV = 0.06  # random per-face Tint variation (+/-), never tied to face direction

BARK, HEART, HOLLOW, MOSS, GRASS, ROCK = "w05_bark", "w05_heartwood", "w05_hollow", "w05_moss", "w05_grass", "kit_rock"
LEAF = "w05_leaf"  # the sheet's key for the small leafy sprigs on deadwood (studding the moss blankets)

# concentric end-grain bands (outer fraction of the cut disc, colour), outside
# in: wide pale heartwood bands separated by thin bark-coloured ring lines
RINGS_FULL = [(0.9, HEART), (0.83, BARK), (0.66, HEART), (0.6, BARK), (0.42, HEART), (0.36, BARK),
              (0.18, HEART), (0.13, BARK)]
RINGS_FEW = [(0.86, HEART), (0.78, BARK), (0.5, HEART), (0.43, BARK)]


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------


class dressing:
    """with dressing(a): faces painted inside are walk-through scatter
    (face attribute kit_nocollide = 1)."""

    def __init__(self, a):
        self.a = a

    def __enter__(self):
        self.prev = getattr(self.a, "_w05_dress", False)  # nests safely
        self.a._w05_dress = True

    def __exit__(self, *exc):
        self.a._w05_dress = self.prev


def paint(a, faces, mat, tint=None, var=TV, base=None):
    """One palette key; Tint = small random per-face variation only (the
    `tint` argument is ignored, so no colour follows direction). `base` is a
    random per-piece Tint (e.g. one per stave, so planks read as separate
    boards) that the small per-face variation rides on."""
    mi = a._mi(mat)
    flag = a.bm.faces.layers.int["kit_nocollide"]
    nc = 1 if getattr(a, "_w05_dress", False) else 0
    for f in faces:
        f.material_index = mi
        f.smooth = False
        if base is not None:
            t = round(base * (1.0 + a.rng.uniform(-0.015, 0.015)) * 80) / 80
        else:
            t = round((1.0 + a.rng.uniform(-var, var)) * 40) / 40
        for lp in f.loops:
            lp[a.tint_layer] = (t, t, t, 1.0)
        f[flag] = nc


def hull_bm(points):
    bm = bmesh.new()
    for p in points:
        bm.verts.new(p)
    res = bmesh.ops.convex_hull(bm, input=bm.verts[:])
    kill = [g for g in res["geom_interior"] + res["geom_unused"] if isinstance(g, bmesh.types.BMVert)]
    if kill:
        bmesh.ops.delete(bm, geom=list(set(kill)), context="VERTS")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    return bm


def emit(a, bm, style, M=None):
    """Copy a temp bmesh into the asset; style(face, world normal) -> (key, tint)."""
    bm.normal_update()
    vmap = {}
    for v in bm.verts:
        vmap[v] = a.bm.verts.new(M @ v.co if M is not None else v.co.copy())
    out = []
    for f in bm.faces:
        n = (M.to_3x3() @ f.normal).normalized() if M is not None else f.normal
        mat, t = style(f, n)
        try:
            nf = a.bm.faces.new([vmap[v] for v in f.verts])
        except ValueError:
            continue
        paint(a, [nf], mat, t)
        out.append(nf)
    return out


def ellipse_pts(cx, cy, rx, ry, z, m, rng, jit=0.06, phase=0.0):
    pts = []
    for k in range(m):
        th = phase + 2 * PI * (k + rng.uniform(-0.3, 0.3)) / m
        s = 1 + rng.uniform(-jit, jit)
        pts.append(Vector((cx + math.cos(th) * rx * s, cy + math.sin(th) * ry * s, z)))
    return pts


def new_face(a, verts):
    try:
        f = a.bm.faces.new(verts)
    except ValueError:
        return None
    f.normal_update()
    return f


def tri_paint(a, f, mat, tint=1.0):
    """Triangulate a (possibly non-planar) n-gon and paint the pieces."""
    if f is None:
        return []
    res = bmesh.ops.triangulate(a.bm, faces=[f], quad_method="BEAUTY", ngon_method="BEAUTY")
    faces = res["faces"]
    paint(a, faces, mat, tint)
    return faces


def disc(a, ring, center, bands, rng, center_mat=HEART, flip=False):
    """Concentric end-grain disc filling `ring` (faces keep the ring's own
    winding, or the reverse with flip). bands: [(fraction, key)] outside in."""
    outer = ring
    c = Vector(center)
    out = []
    for frac, mat in bands:
        inner = [a.bm.verts.new(c + (v.co - c) * frac * (1 + rng.uniform(-0.035, 0.035))) for v in ring]
        faces = []
        k = len(ring)
        for s in range(k):
            s2 = (s + 1) % k
            q = [outer[s], outer[s2], inner[s2], inner[s]]
            if flip:
                q.reverse()
            f = new_face(a, q)
            if f:
                faces.append(f)
        paint(a, faces, mat)
        out += faces
        outer = inner
    poly = list(outer) if not flip else list(reversed(outer))
    f = new_face(a, poly)
    if f:
        paint(a, [f], center_mat, 1.0)
    return out


# ---------------------------------------------------------------------------
# The log: staves around a bore, both ends configurable
# ---------------------------------------------------------------------------


def log_tube(a, M, L, radius, S=9, seed=0, xs=None, kg=0.84, bore=None, start="open", end="open",
             amp0=0.12, amp1=0.12, splinter=0.0, cracks=0, gap=None, plug=None, capk=0.86,
             start_bands=None, end_bands=None, x_jit=0.22, r_jit=0.035, steps=None, crown=1.035,
             chamfer0=None):
    """Log along local +X (0..L), mapped to the world by M. radius(x) is the
    outer radius. Each of the S staves is a broad flat plank: a deep V groove
    (kg), bevelled edges and a flat crown. start/end: "open" (plank ends
    around the bore), "broken" (staggered splintered heartwood ends), "cap"
    (bark rim + ring disc) or "none". gap: [(angle_deg, x_from)] removes the
    stave nearest that angle from x_from on (a split, open slot). plug: x of a
    dark disc inside the bore. steps: [(angle_deg, x_from)] sinks the stave
    nearest that angle from x_from on (a stepped plank joint; put two close
    rings in xs there). chamfer0=(length, k): the open start's plank ends get
    a broad pale bevel (ring 0 shrunk to k of the radius, ring 1 replaced by a
    ring `length` behind each stave's own end, the band between them painted
    w05_heartwood), so the staggered plank ends read as a thick scalloped rim.
    Returns a dict with the stave angles and helpers."""
    rng = random.Random(seed)
    bm = a.bm
    ws = [rng.uniform(0.85, 1.2) for _ in range(S)]
    tot = sum(ws)
    E = [rng.uniform(0, 2 * PI / S)]
    for w in ws:
        E.append(E[-1] + 2 * PI * w / tot)
    xs = xs or [0.0, L / 3, 2 * L / 3, L]
    n = len(xs)
    x0s = [rng.uniform(0, amp0) for _ in range(S)]
    x1s = [L - rng.uniform(0, amp1) for _ in range(S)]
    spl = [rng.uniform(0.35, 1.0) * splinter for _ in range(S)]
    tints = [1.0 + rng.uniform(-0.06, 0.06) for _ in range(S)]  # one random Tint per plank

    def mid(s):
        return (E[s] + E[s + 1]) / 2

    def nearest(deg):
        t = math.radians(deg)
        return min(range(S), key=lambda s: abs(math.atan2(math.sin(mid(s) - t), math.cos(mid(s) - t))))

    gaps = {nearest(d): x for d, x in (gap or [])}
    sunk = {nearest(d): x for d, x in (steps or [])}
    vis = [s for s in range(S) if math.sin(mid(s)) > 0.3 or math.cos(mid(s)) < -0.5]
    vis = [s for s in vis if s not in gaps]
    crack = set(rng.sample(vis, min(cracks, len(vis))))
    cols = []
    for s in range(S):
        w = E[s + 1] - E[s]
        e = 0.12 * w
        cols += [(s, "G", E[s], kg), (s, "C", E[s] + e, 1.0), (s, "D", E[s] + 0.36 * w, crown),
                 (s, "K", E[s] + 0.64 * w, crown), (s, "E", E[s + 1] - e, 1.0)]
    m = len(cols)

    def P(x, phi, r):
        return M @ Vector((x, r * math.cos(phi), r * math.sin(phi)))

    reach = {"D": 1.0, "C": 0.35, "K": 0.7, "E": 0.2}
    V, XG = [], []
    for i in range(n):
        ring, xg = [], []
        jit = x_jit
        if 0 < i < n - 1:
            jit = min(x_jit, 0.3 * min(xs[i] - xs[i - 1], xs[i + 1] - xs[i]))
        for s, kind, phi, k in cols:
            sp = (s - 1) % S
            if i == 0:
                x = max(x0s[s], x0s[sp]) if kind == "G" else x0s[s]
            elif i == 1 and chamfer0:
                x = (max(x0s[s], x0s[sp]) if kind == "G" else x0s[s]) + chamfer0[0]
            elif i == n - 1:
                x = min(x1s[s], x1s[sp]) if kind == "G" else x1s[s] + spl[s] * reach[kind]
            else:
                x = xs[i] + rng.uniform(-jit, jit)
            kk = 0.88 if (kind == "K" and s in crack and 0 < i < n - 1) else k
            if kind != "G" and s in sunk and xs[i] >= sunk[s] - 1e-6:
                kk *= 0.93
            if i == 0 and chamfer0:
                kk = (kk + (1.0 - kk) * 0.5) * chamfer0[1]  # shallower groove on the bevelled end
            r = radius(x) * kk * (1 + rng.uniform(-r_jit, r_jit))
            ring.append(bm.verts.new(P(x, phi, r)))
            if kind == "G":
                xg.append(x)
        V.append(ring)
        XG.append(xg)

    def cut(s, i):
        return s in gaps and xs[i] >= gaps[s] - 1e-6

    for i in range(n - 1):  # all bark faces one key: the grooves read from geometry
        for c in range(m):
            s = cols[c][0]
            if cut(s, i):
                continue
            c2 = (c + 1) % m
            f = new_face(a, (V[i][c], V[i][c2], V[i + 1][c2], V[i + 1][c]))
            if f is not None:
                if i == 0 and chamfer0:
                    paint(a, [f], HEART)  # bevelled plank end: cut wood
                else:
                    paint(a, [f], BARK, base=tints[s])

    I = None
    if bore:
        I = [[bm.verts.new(P(XG[i][s], E[s], radius(XG[i][s]) * bore)) for s in range(S)] for i in range(n)]
        for i in range(n - 1):
            lip = (i == 0 and start in ("open", "broken")) or \
                  (i == n - 2 and end in ("open", "broken") and plug is None)
            for s in range(S):
                if cut(s, i):
                    continue
                s2 = (s + 1) % S
                f = new_face(a, (I[i][s], I[i + 1][s], I[i + 1][s2], I[i][s2]))
                if f:
                    paint(a, [f], HOLLOW)

    def stave_poly(i, s, inner):
        s2 = (s + 1) % S
        return [inner[s]] + V[i][5 * s:5 * s + 5] + [V[i][5 * s2], inner[s2]]

    for i, kind_end, plus, bands in ((0, start, False, start_bands), (n - 1, end, True, end_bands)):
        if kind_end == "none":
            continue
        if kind_end in ("open", "broken"):
            for s in range(S):
                if plus and s in gaps:
                    continue
                poly = stave_poly(i, s, I[i])
                if not plus:
                    poly.reverse()
                tri_paint(a, new_face(a, poly), HEART)
        else:  # cap: bark rim, then concentric end grain
            xe = sum(XG[i]) / S
            cap = [bm.verts.new(P(XG[i][s], E[s], radius(XG[i][s]) * capk)) for s in range(S)]
            for s in range(S):
                poly = stave_poly(i, s, cap)
                if not plus:
                    poly.reverse()
                tri_paint(a, new_face(a, poly), BARK)
            disc(a, cap, M @ Vector((xe, 0, 0)), bands or RINGS_FULL, rng, flip=not plus)

    if plug is not None and bore:
        pr = radius(plug) * bore * 1.03
        pv = [bm.verts.new(P(plug, E[s], pr)) for s in range(S)]
        f = new_face(a, list(reversed(pv)))  # faces -X, into the open end
        if f:
            paint(a, [f], HOLLOW)
        if end != "none":
            pv2 = [bm.verts.new(P(plug + 0.03, E[s], pr)) for s in range(S)]
            f = new_face(a, pv2)
            if f:
                paint(a, [f], HOLLOW)

    for s, xf in gaps.items():  # split slot: side walls and a snapped stave end
        s2 = (s + 1) % S
        i0 = next(i for i in range(n) if xs[i] >= xf - 1e-6)
        for i in range(i0, n - 1):
            walls = []
            if (s - 1) % S not in gaps:
                walls.append((I[i][s], I[i + 1][s], V[i + 1][5 * s], V[i][5 * s]))
            if s2 not in gaps:
                walls.append((I[i][s2], V[i][5 * s2], V[i + 1][5 * s2], I[i + 1][s2]))
            for q in walls:
                f = new_face(a, q)
                if f:
                    paint(a, [f], HEART)  # split-open wood
        tri_paint(a, new_face(a, stave_poly(i0, s, I[i0])), HEART)

    return dict(E=E, P=P, radius=radius, S=S)


# ---------------------------------------------------------------------------
# Branches, tubes and splinters
# ---------------------------------------------------------------------------


def tube(a, pts, radii, sides, rng, jitter=0.05):
    """Faceted bark tube along a polyline (open ends). Returns its rings."""
    bm = a.bm
    pts = [Vector(p) for p in pts]
    n = len(pts)
    rings = []
    t0 = (pts[1] - pts[0]).normalized()
    up = ZV if abs(t0.z) < 0.9 else Vector((1, 0, 0))
    ref = t0.cross(up).normalized()
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        nrm = (ref - t * ref.dot(t)).normalized()
        bi = nrm.cross(t).normalized()
        ring = []
        for j in range(sides):
            b = 2 * PI * j / sides
            r = radii[i] * (1 + rng.uniform(-jitter, jitter))
            ring.append(bm.verts.new(p + r * (math.cos(b) * nrm + math.sin(b) * bi)))
        rings.append(ring)
    for i in range(n - 1):
        for j in range(sides):
            k = (j + 1) % sides
            f = new_face(a, (rings[i][j], rings[i + 1][j], rings[i + 1][k], rings[i][k]))
            if f:
                paint(a, [f], BARK)
    return rings


def splinter_tip(a, ring, center, d, r, rng, mat=HEART):
    """Jagged broken tip: the end ring's verts pushed out unevenly along d and
    a pale point in the middle."""
    d = Vector(d).normalized()
    for v in ring:
        v.co += d * rng.uniform(0.0, 0.45) * r
    c = a.bm.verts.new(Vector(center) + d * r * rng.uniform(0.35, 0.7))
    k = len(ring)
    for j in range(k):
        f = new_face(a, (c, ring[(j + 1) % k], ring[j]))
        if f:
            paint(a, [f], mat)


def branch(a, base, d, length, r0, rng, prongs=(), sides=6, base_cut=False, cut_n=None, taper=0.82):
    """Broken branch stub: a main limb from `base` along d, forking into prongs
    [(dir, length, radius)] with splintered tips (no prongs: one splintered end).
    base_cut closes the base with a heartwood ring disc; cut_n slants that saw
    cut so it faces cut_n (e.g. toward the camera)."""
    base = Vector(base)
    d = Vector(d).normalized()
    p1 = base + d * length
    bend = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.3, 0.3))) * 0.06 * length
    rings = tube(a, [base, base + d * length * 0.5 + bend, p1], [r0, r0 * (1 + taper) / 2, r0 * taper], sides, rng)
    if cut_n is not None:
        nn = Vector(cut_n).normalized()
        dn = d.dot(nn)
        for v in rings[0]:
            v.co += d * (-(v.co - base).dot(nn) / dn)
    if base_cut:
        disc(a, rings[0], base, [(0.85, HEART), (0.74, BARK), (0.45, HEART), (0.36, BARK)], rng)
    if not prongs:
        splinter_tip(a, rings[-1], p1, d, r0 * taper, rng)
        return
    f = new_face(a, list(reversed(rings[-1])))
    if f:
        paint(a, [f], BARK)
    for dp, lp, rp in prongs:
        dp = Vector(dp).normalized()
        q0 = p1 - d * r0 * 0.45
        qb = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0)) * 0.05 * lp
        pr = tube(a, [q0, q0 + dp * lp * 0.55 + qb, q0 + dp * lp], [rp, rp * 0.86, rp * 0.72], sides, rng)
        splinter_tip(a, pr[-1], q0 + dp * lp, dp, rp * 0.72, rng)


# ---------------------------------------------------------------------------
# Moss blankets on the log
# ---------------------------------------------------------------------------


def shard(a, base, d, L, w, rng):
    """Tall broken splinter: a leaning 3-sided spike, bark outside and one pale
    split face (a real cut/broken-wood material change)."""
    d = Vector(d).normalized()
    side = d.cross(ZV)
    if side.length < 1e-3:
        side = Vector((1, 0, 0))
    side.normalize()
    up = side.cross(d).normalized()
    b = Vector(base)
    vs = [a.bm.verts.new(b + (side * math.cos(t) + up * math.sin(t)) * w * rng.uniform(0.8, 1.15))
          for t in (0.3, 2.4, 4.3)]
    tip = a.bm.verts.new(b + d * L + side * rng.uniform(-0.15, 0.15) * L)
    fs = [new_face(a, (vs[j], vs[(j + 1) % 3], tip)) for j in range(3)]
    fs = [f for f in fs if f]
    bmesh.ops.recalc_face_normals(a.bm, faces=fs)
    for j, f in enumerate(fs):
        paint(a, [f], HEART if j == 1 else BARK)


def surface_frame(P, radius, x, phi_deg):
    """Point on the log surface at (x, phi) and its out / along / across axes."""
    phi = math.radians(phi_deg)
    rr = radius(x)
    base = P(x, phi, rr)
    out = (P(x, phi, rr + 1.0) - base).normalized()
    ax = (P(x + 1.0, phi, 0.0) - P(x, phi, 0.0)).normalized()
    bi = out.cross(ax).normalized()
    return base, out, ax, bi


def moss_lump(a, P, radius, x, phi_deg, r, rng, stretch=1.15, flat=0.8, key=MOSS):
    """Rounded moss mound sitting on the log surface at (x, phi): a dome of
    three stacked rings (7 / 6 / 4 points) plus a crown point, stretched along
    the log, sunk a little into the bark, its buried underside removed. Few
    broad facets, so it reads as a soft cushion, not shards. Dressing
    (kit_nocollide = 1)."""
    base, out, ax, bi = surface_frame(P, radius, x, phi_deg)
    c = base - out * r * 0.12
    pts = []
    for el, m in ((-8, 7), (34, 6), (66, 4)):
        e = math.radians(el)
        ph0 = rng.uniform(0, 2 * PI)
        for k in range(m):
            th = ph0 + 2 * PI * (k + rng.uniform(-0.18, 0.18)) / m
            s = 1 + rng.uniform(-0.08, 0.08)
            pts.append(c + (ax * math.cos(th) * math.cos(e) * stretch + bi * math.sin(th) * math.cos(e)
                            + out * math.sin(e) * flat) * r * s)
    pts.append(c + out * r * flat * rng.uniform(0.95, 1.05))
    bm = hull_bm(pts)
    bm.normal_update()
    under = [f for f in bm.faces if f.normal.dot(out) < -0.6]
    if under:
        bmesh.ops.delete(bm, geom=under, context="FACES_ONLY")
    with dressing(a):
        emit(a, bm, lambda f, nn: (key, 1.0), None)
    bm.free()


def leafy_clump(a, P, radius, x, phi_deg, r, rng, nleaf=5, droop=0.0):
    """Leafy sprig clump on the moss (sheet: w05_leaf is the small leafy
    sprigs on deadwood): a low rounded w05_leaf cushion with pointed leaves
    fanning out over its edge, slightly drooping (more with droop, for the
    clumps hanging down the front). Dressing (kit_nocollide = 1)."""
    moss_lump(a, P, radius, x, phi_deg, r * 0.8, rng, stretch=1.1, flat=0.75, key=LEAF)
    base, out, ax, bi = surface_frame(P, radius, x, phi_deg)
    ph0 = rng.uniform(0, 2 * PI)
    with dressing(a):
        for k in range(nleaf):
            th = ph0 + 2 * PI * (k + rng.uniform(-0.2, 0.2)) / nleaf
            rad = ax * math.cos(th) + bi * math.sin(th)
            b = base + out * r * 0.35 + rad * r * 0.35
            d = rad + out * rng.uniform(0.05, 0.3) - Vector((0, 0, droop))
            frond(a, b, d, r * rng.uniform(1.1, 1.4), r * 0.42, LEAF)


def moss_drip(a, P, radius, x, phi0, n, r0, rng, step=21.0, width=None):
    """A moss tongue dripping down the log's front: a chain of n shrinking
    lumps from phi0 downward, a blanket strip under them (half-width `width`,
    default 0.9 r0) and leafy points along the bottom."""
    width = width or r0 * 0.9
    for j in range(n):
        xj = x + rng.uniform(-0.15, 0.15)
        rj = r0 * (1 - 0.12 * j)
        if j % 2 == 0:
            moss_lump(a, P, radius, xj, phi0 + j * step, rj, rng, stretch=1.0 + rng.uniform(-0.1, 0.1))
        else:
            leafy_clump(a, P, radius, xj, phi0 + j * step, rj, rng, nleaf=4, droop=0.5)
    end = phi0 + (n - 1) * step + 9
    nc = 2 if width < 1.0 else 3
    moss_sleeve(a, P, radius, x - width, x + width, phi0 - 12, end, rng, ncols=nc, nrows=3, thick=0.3)
    pe = math.radians(end)
    offs = (0.0,) if width < 1.0 else (-width * 0.55, 0.0, width * 0.55)
    for k, dx in enumerate(offs):
        pk = pe - (0.12 if k != 1 and len(offs) > 1 else 0.0)
        b = P(x + dx, pk, radius(x) + 0.12)
        d = P(x + dx, pk + 0.25, radius(x) + 0.05) - b
        with dressing(a):
            frond(a, b, d, rng.uniform(0.9, 1.2), 0.4 * r0 / 0.6, LEAF)


def moss_sleeve(a, *args, **kw):
    """Moss blanket; every face is walk-through dressing (kit_nocollide = 1)."""
    with dressing(a):
        return _moss_sleeve(a, *args, **kw)


def _moss_sleeve(a, P, radius, x0, x1, lo, hi, rng, ncols=8, nrows=5, thick=0.2, drips=None, lumps=0,
                 lump_r=(0.35, 0.55), frills=0, frill_l=(0.8, 1.2)):
    """A ragged moss blanket wrapped on the log between x0..x1 and angles
    lo..hi (degrees; 90 = top, 180 = front). Interior verts rise `thick` off
    the bark in a pillow profile, edges hug it, so the blanket reads as a
    thick mass. drips: {column: extra degrees} pulls columns down the front.
    lumps: chunky faceted moss mounds on the upper half; frills: small leafy
    points round the lower (front) edge."""
    drips = drips or {}
    midp = (lo + hi) / 2
    grid = []
    gp = []  # (x, phi degrees) of every grid vertex, for the lumps
    for i in range(ncols + 1):
        u = i / ncols
        taper = math.sin(PI * u) ** 0.5
        l = midp - (midp - lo) * (0.4 + 0.6 * taper) + rng.uniform(-8, 8)
        h = midp + (hi - midp) * (0.4 + 0.6 * taper) + rng.uniform(-10, 10) + drips.get(i, 0)
        x = x0 + (x1 - x0) * u
        if 0 < i < ncols:
            x += rng.uniform(-0.15, 0.15) * (x1 - x0) / ncols
        col = []
        gcol = []
        for k in range(nrows + 1):
            v = k / nrows
            gcol.append((x, l + (h - l) * v))
            phi = math.radians(l + (h - l) * v)
            edge = i in (0, ncols) or k in (0, nrows)
            prof = max(0.45, math.sin(PI * v)) * max(0.5, math.sin(PI * u))
            r = radius(x) * 0.995 + (0.0 if edge else thick * prof * rng.uniform(0.7, 1.25))
            col.append(a.bm.verts.new(P(x, phi, r)))
        grid.append(col)
        gp.append(gcol)
    faces = []
    for i in range(ncols):
        for k in range(nrows):
            f = new_face(a, (grid[i][k], grid[i][k + 1], grid[i + 1][k + 1], grid[i + 1][k]))
            if f is None:
                continue
            paint(a, [f], MOSS)
            faces.append(f)
    # chunky faceted moss mounds spread over the blanket (the reference's lumpy leafy caps)
    for j in range(lumps):
        i = 1 + (j * (ncols - 1)) // max(1, lumps - 1) if lumps > 1 else ncols // 2
        i = min(ncols - 1, max(1, i + rng.choice((-1, 0, 0, 1)) if ncols > 2 else 1))
        k = rng.randint(1, max(1, nrows - 1))
        x, ph = gp[i][k]
        if j % 3 == 0:  # one moss cushion to two leafy sprig clumps
            moss_lump(a, P, radius, x + rng.uniform(-0.3, 0.3), ph, rng.uniform(*lump_r), rng)
        else:
            leafy_clump(a, P, radius, x + rng.uniform(-0.3, 0.3), ph, rng.uniform(*lump_r), rng)
    # leafy points along the lower front edge
    for j in range(frills):
        i = 1 + (j * (ncols - 1)) // max(1, frills - 1) if frills > 1 else ncols // 2
        i = min(ncols, max(0, i))
        b = grid[i][nrows].co.copy()
        c0 = grid[i][nrows - 1].co
        d = (b - c0).normalized()
        frond(a, b - d * 0.15, d, rng.uniform(*frill_l), rng.uniform(0.3, 0.45), LEAF)
    return faces


def frond(a, b, d, L, W, key):
    """Small leafy point (4 tris): a flat, slightly domed spike from b along d."""
    d = Vector(d).normalized()
    side = d.cross(ZV)
    if side.length < 1e-3:
        side = Vector((1, 0, 0))
    side.normalize()
    up = side.cross(d).normalized()
    if up.z < 0:
        up = -up
    bm = a.bm
    v1 = bm.verts.new(b + side * W)
    v2 = bm.verts.new(b - side * W)
    c = bm.verts.new(b + d * L * 0.35 + up * W * 0.45)
    t = bm.verts.new(b + d * L - up * W * 0.25)
    fs = [f for f in (new_face(a, (v1, c, t)), new_face(a, (c, v2, t)), new_face(a, (v1, v2, c)),
                      new_face(a, (v2, v1, t))) if f]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    paint(a, fs, key)


# ---------------------------------------------------------------------------
# Base dressing: rocks, grass tufts, fern clumps, moss ground patches
# ---------------------------------------------------------------------------


def rock_style(rng):
    """One grey stone colour; the facets shade it."""
    return lambda f, n: (ROCK, 1.0)


def rock(a, c, size, rng, yaw=0.0, n=15, key=ROCK):
    """Chunky faceted grey rock (convex hull, flat buried base removed). With
    key=MOSS (inside `dressing`) the same hull makes a ground moss mound."""
    sx, sy, sz = size
    zc = sz * 0.35
    rz = sz - zc
    pts = []
    ga = PI * (3 - math.sqrt(5))
    for i in range(n):
        zz = 1 - 1.5 * (i + 0.5) / n
        rr = math.sqrt(max(0.0, 1 - zz * zz))
        th = ga * i + rng.uniform(-0.35, 0.35)
        s = 1 + rng.uniform(-0.13, 0.13)
        pts.append(Vector((rr * math.cos(th) * sx / 2 * s, rr * math.sin(th) * sy / 2 * s,
                           max(0.0, zc + zz * rz * s))))
    pts.append(Vector((rng.uniform(-0.15, 0.15) * sx, rng.uniform(-0.15, 0.15) * sy, sz)))
    pts += ellipse_pts(0, 0, sx * 0.42, sy * 0.42, 0.0, 6, rng, 0.1, rng.random())
    bm = hull_bm(pts)
    bottom = [f for f in bm.faces if all(v.co.z < 0.02 for v in f.verts)]
    bmesh.ops.delete(bm, geom=bottom, context="FACES_ONLY")
    M = Matrix.Translation((c[0], c[1], c[2] if len(c) > 2 else 0.0)) @ Matrix.Rotation(yaw, 4, "Z")
    emit(a, bm, rock_style(random.Random(rng.random())) if key == ROCK else (lambda f, nn: (key, 1.0)), M)
    bm.free()


def orient_out(faces, axis_pt):
    for f in faces:
        f.normal_update()
        c = f.calc_center_median()
        if f.normal.dot(c - axis_pt(c)) < 0:
            f.normal_flip()
            f.normal_update()


def blade(a, b, d, h, w, rng, low=GRASS, tip=GRASS):
    """One spiky grass blade: flattened 3-sided spike (9 tris), one grass colour."""
    d = Vector(d).normalized()
    side = d.cross(ZV)
    if side.length < 1e-4:
        side = Vector((1, 0, 0))
    side.normalize()
    thick = side.cross(d).normalized()
    out = Vector((d.x, d.y, 0))
    out = out.normalized() if out.length > 1e-4 else Vector((0, 0, 0))
    b = Vector(b)
    m = b + d * h * 0.5 + out * h * 0.06
    t = b + d * h + out * h * 0.2
    base = [b + side * w, b - side * w, b + thick * w * 0.4]
    midr = [m + side * w * 0.62, m - side * w * 0.62, m + thick * w * 0.25]
    bv = [a.bm.verts.new(p) for p in base]
    mv = [a.bm.verts.new(p) for p in midr]
    tv = a.bm.verts.new(t)
    lowf, tipf = [], []
    for j in range(3):
        k = (j + 1) % 3
        f = new_face(a, (bv[j], bv[k], mv[k], mv[j]))
        if f:
            lowf.append(f)
        f = new_face(a, (mv[j], mv[k], tv))
        if f:
            tipf.append(f)

    def axis(p):
        s = max(0.0, min(h, (p - b).dot(d)))
        return b + d * s

    orient_out(lowf + tipf, axis)
    paint(a, lowf, low)
    paint(a, tipf, tip)


def tuft(a, c, h, rng, n=7, spread=0.35, lean=0.5):
    """Spiky grass tuft: n w05_grass blades fanning out of one root."""
    c = Vector(c)
    for k in range(n):
        az = 2 * PI * k / n + rng.uniform(-0.4, 0.4)
        off = spread * rng.uniform(0.1, 0.6)
        b = c + Vector((math.cos(az) * off, math.sin(az) * off, 0))
        tilt = lean * rng.uniform(0.3, 1.1) * (0.4 if k == 0 else 1.0)
        d = Vector((math.sin(tilt) * math.cos(az), math.sin(tilt) * math.sin(az), math.cos(tilt)))
        hb = h * rng.uniform(0.6, 1.0) * (1.15 if k == 0 else 1.0)
        with dressing(a):
            blade(a, b, d, hb, 0.13 + 0.06 * h, rng)


def leaf(a, base, d, L, W, key, curl=0.45, fold=0.18, th=0.06):
    """Pointed leaf (16 tris): ridged top over a flat underside, bending down."""
    d = Vector(d).normalized()
    side = d.cross(ZV)
    if side.length < 1e-4:
        side = Vector((1, 0, 0))
    side.normalize()
    prof = ((0.0, 0.1), (0.3, 0.4), (0.62, 0.38), (0.88, 0.18), (1.0, 0.0))
    c = Vector(base)
    dk = d.copy()
    prev = 0.0
    pts = []
    for t, w in prof:
        c = c + dk * L * (t - prev)
        prev = t
        u = side.cross(dk).normalized()
        if u.z < 0:
            u = -u
        pts.append((c.copy(), u, w * W))
        dk = (Matrix.Rotation(-curl * 0.3, 3, side) @ dk).normalized()
        if dk.z > d.z + 0.01 and abs(curl) > 0:
            dk = (Matrix.Rotation(curl * 0.6, 3, side) @ dk).normalized()
    bm = a.bm
    B = bm.verts.new(pts[0][0])
    T = bm.verts.new(pts[-1][0])
    Ls, Rs, Ms = [], [], []
    for cc, u, w in pts[1:-1]:
        Ls.append(bm.verts.new(cc + side * w - u * fold * w))
        Rs.append(bm.verts.new(cc - side * w - u * fold * w))
        Ms.append(bm.verts.new(cc + u * th))
    for v in [B, T] + Ls + Rs + Ms:
        v.co.z = max(v.co.z, 0.0)
    L1, L2, L3 = Ls
    R1, R2, R3 = Rs
    M1, M2, M3 = Ms
    left = [bm.faces.new(f) for f in ((B, L1, M1), (M1, L1, L2), (M1, L2, M2), (M2, L2, L3),
                                      (M2, L3, M3), (M3, L3, T))]
    right = [bm.faces.new(f) for f in ((B, M1, R1), (M1, R2, R1), (M1, M2, R2), (M2, R3, R2),
                                       (M2, M3, R3), (M3, T, R3))]
    under = [bm.faces.new((B, R1, R2, R3, T, L3, L2, L1))]
    faces = left + right + under
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    paint(a, faces, key)


def fern(a, *args, **kw):
    """Walk-through leafy clump (kit_nocollide dressing faces)."""
    with dressing(a):
        _fern(a, *args, **kw)


def _fern(a, c, s, rng, n=9, away=(0.0, -1.0), key=GRASS, dome=None):
    """Spiky leafy clump: a low dome with pointed leaves sprouting up and out,
    the whole clump one colour (key; dome defaults to the same key)."""
    c = Vector(c)
    z0 = c.z
    base_az = math.atan2(away[1], away[0])
    rx, rz = 0.4 * s, 0.62 * s
    core = [Vector((c.x + math.cos(k * 2.1 + 0.3) * rx * 0.25, c.y + math.sin(k * 2.1 + 0.3) * rx * 0.25, z0 + rz))
            for k in range(3)]
    core += ellipse_pts(c.x, c.y, rx * 0.8, rx * 0.8, z0 + rz * 0.65, 5, rng, 0.15)
    core += ellipse_pts(c.x, c.y, rx, rx, z0, 6, rng, 0.12)
    bm = hull_bm(core)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.z < -0.9], context="FACES_ONLY")
    emit(a, bm, lambda f, nn: (dome or key, 1.0), None)
    bm.free()
    ga = PI * (3 - math.sqrt(5))
    for i in range(n):
        f = (i + 0.5) / n
        el = math.asin(1 - f)
        az = base_az + ((ga * i) % (2 * PI) - PI) * (0.75 + 0.25 * (1 - f)) + rng.uniform(-0.2, 0.2)
        nrm = Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el)))
        b = Vector((c.x + nrm.x * rx * 0.7, c.y + nrm.y * rx * 0.7, z0 + nrm.z * rz * 0.7 + 0.04))
        pitch = min(1.4, el * 0.8 + rng.uniform(0.6, 0.9))
        d = Vector((math.cos(az) * math.cos(pitch), math.sin(az) * math.cos(pitch), math.sin(pitch)))
        L = s * rng.uniform(0.55, 0.7)
        leaf(a, b, d, L, L * rng.uniform(0.6, 0.75), key, curl=rng.uniform(0.25, 0.45))


def ground_patch(a, c, rx, ry, rng, yaw=0.0, h=0.22):
    """Low w05_moss ground patch (~0.2-0.3 thick) under the dressing."""
    pts = ellipse_pts(0, 0, rx, ry, 0.0, 10, rng, 0.18, rng.random())
    pts += ellipse_pts(0, 0, rx * 0.72, ry * 0.72, h, 7, rng, 0.12, rng.random())
    bm = hull_bm(pts)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(v.co.z < 0.01 for v in f.verts)], context="FACES_ONLY")
    M = Matrix.Translation((c[0], c[1], 0)) @ Matrix.Rotation(yaw, 4, "Z")
    with dressing(a):
        emit(a, bm, lambda f, nn: (MOSS, 1.0), M)
    bm.free()


# ---------------------------------------------------------------------------
# Asset plumbing
# ---------------------------------------------------------------------------


def new_asset(kit, name, seed):
    a = kit.flintkit.Asset(name, f"Kit {kit.sheet} {kit.subject}", seed=seed)
    a.bm.faces.layers.int.new("kit_nocollide")  # before any face exists (adding later frees face refs)
    return a


def done(kit, a, role, collision, budget=None, notes=""):
    """Flatten anything below the ground, drop faces lying on it (never seen),
    clean degenerate slivers, then finish and tag."""
    bm = a.bm
    for v in bm.verts:
        if v.co.z < 0:
            v.co.z = 0.0
    flat = [f for f in bm.faces if all(v.co.z < 0.002 for v in f.verts)]
    if flat:
        bmesh.ops.delete(bm, geom=flat, context="FACES_ONLY")
    bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges[:])
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
    obj = a.finish()
    if role != "part":
        # moss (lime, on the log top) and grass (darker green, upright blades)
        # are two sheet materials; the runner groups them as one hue family, so
        # where they sit (moss up, grass sideways) looks like baked lighting.
        obj["kit_shading_ok"] = ("w05_moss blankets / w05_leaf sprigs on the log top vs w05_grass blades at the "
                                 "foot, and pale w05_heartwood plank-end bevels: real material changes")
    return kit.tag(obj, role, collision=collision, budget=budget, notes=notes)


def log_frame(L, yaw_deg, axis_z):
    """G maps log-ground coords (lx along the log from its open end, ly to the
    log's left/back) to the asset; M adds the axis height."""
    G = Matrix.Rotation(math.radians(yaw_deg), 4, "Z") @ Matrix.Translation((-L / 2, 0, 0))
    M = G @ Matrix.Translation((0, 0, axis_z))
    return G, M


def radius_fn(R, L, bulge=0.03, taper=0.05):
    return lambda x: R * (1 + bulge * math.sin(PI * max(0.0, min(L, x)) / L)) * (1 - taper * x / L)


def dress(a, G, rng, rocks=(), tufts=(), patches=(), ferns=(), rs=1.35, ts=1.75):
    """Base dressing placed in log-ground coords (lx, ly)."""
    yaw = G.to_euler().z
    for lx, ly, rx, ry in patches:
        p = G @ Vector((lx, ly, 0))
        ground_patch(a, p, rx, ry, rng, yaw=yaw)
    for lx, ly, size in rocks:
        p = G @ Vector((lx, ly, 0))
        rock(a, p, tuple(v * rs for v in size), rng, yaw=rng.uniform(0, 2 * PI))
    for lx, ly, s in ferns:
        p = G @ Vector((lx, ly, 0))
        fern(a, p, s, rng, away=(0.0, -1.0))
    for lx, ly, h in tufts:
        p = G @ Vector((lx, ly, 0))
        tuft(a, p, h * ts, rng, n=rng.choice((6, 7, 8)))


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------


def fallen_hollow_log(kit):
    a = new_asset(kit, "FallenHollowLog", 5401)
    rng = random.Random(5401)
    L, R = 13.2, 2.75  # chunky: length ~2.4 x the diameter, like the sheet's barrel
    G, M = log_frame(L, HERO_YAW, R * 0.97)
    radius = radius_fn(R, L)
    # open -X end: bore 60% of the diameter inside a ~1.1-1.2 stud pale rim of
    # bevelled, staggered plank ends (chamfer0); few rings so the tris go to
    # rounder staves with deeper grooves
    info = log_tube(a, M, L, radius, S=11, seed=5402, xs=[0.0, 0.0, 3.2, 6.6, 9.9, L], kg=0.8, crown=1.045,
                    bore=0.6, r_jit=0.03, start="open", end="broken", amp0=0.6, amp1=1.0, splinter=1.0, cracks=1,
                    plug=L - 2.6, chamfer0=(0.45, 0.88))
    P = info["P"]
    R3 = M.to_3x3()
    xe = L - 0.5
    # snapped +X end: tall splinters standing off the top/front so the break
    # shows in the hero silhouette (bark outside, one pale split face)
    for phi, ln, lean in ((70, 1.9, 0.9), (100, 2.4, 0.7), (128, 1.7, 0.95), (150, 1.3, 1.0)):
        t = math.radians(phi)
        shard(a, P(xe - 0.9, t, radius(xe) * 0.82), R3 @ Vector((lean, math.cos(t) * 0.3, 0.75)), ln, 0.42, rng)
    # thick broken limb off the back top at ~60% of the length, leaning toward
    # +X and back, splitting into a clear Y of two thick splintered prongs
    branch(a, M @ Vector((7.6, 0.9, radius(7.6) * 0.7)), R3 @ Vector((0.75, 0.3, 0.8)), 3.4, 1.25, rng, sides=7,
           taper=0.75, prongs=[(R3 @ Vector((0.95, 0.1, 0.35)), 2.3, 0.62), (R3 @ Vector((0.05, 0.15, 1.0)), 2.2, 0.56)])
    # moss: rounded cushion and leafy-sprig mounds running the length of the
    # top (left part up to the branch, right part beyond it), a big curtain
    # dripping down the front beside the open end and two smaller drips
    moss_sleeve(a, P, radius, 0.9, 7.0, 58, 128, rng, ncols=6, nrows=4, thick=0.45, lumps=10, lump_r=(0.7, 0.95),
                frills=3)
    moss_sleeve(a, P, radius, 8.8, 12.2, 62, 118, rng, ncols=4, nrows=3, thick=0.35, lumps=4, lump_r=(0.6, 0.8),
                frills=1)
    moss_drip(a, P, radius, 2.6, 124, 3, 0.8, rng, width=1.0)
    moss_drip(a, P, radius, 5.6, 124, 2, 0.6, rng)
    # leafy fern sprigs on top of the moss (left end and right end, like the sheet)
    fern(a, P(1.2, math.radians(98), radius(1.2) + 0.45), 1.1, rng, n=5, away=(0.0, 1.0), key=LEAF)
    fern(a, P(11.8, math.radians(92), radius(11.8) + 0.35), 0.9, rng, n=4, away=(0.0, 1.0), key=LEAF)
    dress(a, G, rng, rs=1.0, ts=1.9,
          patches=[(5.0, -3.1, 2.8, 0.9), (-0.6, -1.6, 1.1, 0.9)],
          rocks=[(-0.9, 3.4, (2.0, 1.8, 1.9)), (3.5, -3.3, (1.7, 1.5, 1.3)), (6.4, -3.5, (2.9, 2.5, 2.4)),
                 (9.3, -3.2, (2.6, 2.3, 2.2)), (11.9, -2.8, (1.7, 1.5, 1.4))],
          tufts=[(-0.4, -1.7, 1.0), (1.9, -3.2, 0.9), (4.9, -3.3, 1.5), (7.9, -3.7, 1.1), (10.8, -3.4, 1.3),
                 (12.8, -1.9, 1.0)])
    return done(kit, a, "hero", "precise", budget=3000,
                notes="big fallen hollow log: open dark bore at -X (front-left), forked branch stub, moss drape, "
                      "rocks + grass; precise collision keeps the bore open")


def hollow_log(kit):
    a = new_asset(kit, "HollowLog", 5411)
    rng = random.Random(5411)
    L, R = 10.3, 2.4
    G, M = log_frame(L, YAW, R * 0.97)
    radius = radius_fn(R, L)
    info = log_tube(a, M, L, radius, S=10, seed=5412, xs=[0.0, 0.0, 3.0, 4.1, 4.35, 6.6, 8.6, L], bore=0.6,
                    r_jit=0.04, start="open", end="broken", amp0=0.5, amp1=0.6, splinter=0.4, cracks=1,
                    kg=0.81, chamfer0=(0.4, 0.88),
                    plug=L - 2.0, steps=[(165, 4.35), (115, 4.35)])
    P = info["P"]
    R3 = M.to_3x3()
    branch(a, M @ Vector((6.0, 0.4, radius(6.0) * 0.8)), R3 @ Vector((0.5, 0.15, 0.85)), 2.4, 0.78, rng, sides=7,
           taper=0.8, prongs=[(R3 @ Vector((0.85, 0.05, 0.6)), 1.25, 0.5), (R3 @ Vector((-0.3, 0.2, 1.0)), 1.05, 0.44)])
    moss_sleeve(a, P, radius, 1.0, 5.0, 55, 126, rng, ncols=5, nrows=4, thick=0.4, lumps=5, lump_r=(0.5, 0.7),
                frills=2)
    moss_sleeve(a, P, radius, 7.0, 9.6, 62, 118, rng, ncols=3, nrows=3, thick=0.3, lumps=2, lump_r=(0.4, 0.55))
    for x, n, r0 in ((2.0, 2, 0.65), (8.1, 2, 0.45)):
        moss_drip(a, P, radius, x, 128, n, r0, rng)
    dress(a, G, rng, rs=1.0,
          patches=[(4.6, -3.2, 2.2, 0.8), (-0.7, -1.5, 1.0, 0.9)],
          rocks=[(1.2, -3.4, (1.2, 1.1, 1.0)), (5.0, -3.3, (2.3, 2.0, 2.0)), (7.6, -3.1, (1.9, 1.7, 1.7)),
                 (-1.1, -0.4, (1.4, 1.2, 1.3))],
          tufts=[(-1.6, -1.6, 1.0), (3.4, -3.5, 1.4), (9.4, -2.8, 1.2), (11.1, -1.1, 1.0)])
    return done(kit, a, "variant", "precise", budget=3000,
                notes="shorter hollow log with open end, forked stub and moss")


def broken_log(kit):
    a = new_asset(kit, "BrokenLog", 5421)
    rng = random.Random(5421)
    L, R = 10.0, 2.45
    G, M = log_frame(L, YAW, R * 0.97)
    radius = radius_fn(R, L, taper=0.02)
    xe = L - 1.6
    info = log_tube(a, M, L, radius, S=10, seed=5422, xs=[0.0, 0.0, 3.0, 5.0, 6.2, xe], bore=0.6, r_jit=0.04,
                    start="open", end="broken", amp0=0.45, amp1=1.0, splinter=1.2, cracks=1,
                    kg=0.81, chamfer0=(0.4, 0.88),
                    gap=[(95, 5.0)], plug=2.4, steps=[(200, 3.0)])
    P = info["P"]
    R3 = M.to_3x3()
    # tall jagged splinters standing up off the snapped +X end (bark outside, pale split face)
    for phi, ln, lean in ((62, 2.0, 0.55), (88, 2.6, 0.45), (118, 2.2, 0.5), (145, 1.6, 0.7), (35, 1.5, 0.8)):
        t = math.radians(phi)
        base = P(xe - 1.4, t, radius(xe) * 0.82)
        d = R3 @ Vector((lean, math.cos(t) * 0.35, 0.9 + math.sin(t) * 0.2))
        shard(a, base, d, ln, 0.42, rng)
    # short thick snapped stub on the top toward the broken end
    branch(a, M @ Vector((4.4, 0.7, radius(4.4) * 0.8)), R3 @ Vector((0.45, 0.35, 0.82)), 1.9, 0.72, rng, sides=7)
    moss_sleeve(a, P, radius, 0.8, 3.2, 42, 128, rng, ncols=3, nrows=3, thick=0.4, lumps=3, lump_r=(0.45, 0.62),
                frills=2)
    moss_drip(a, P, radius, 1.9, 126, 2, 0.6, rng)
    dress(a, G, rng, rs=1.0,
          patches=[(4.5, -3.1, 2.0, 0.8), (-0.6, -1.4, 1.0, 0.9)],
          rocks=[(4.6, -3.3, (2.5, 2.2, 2.2)), (7.6, -3.0, (1.9, 1.7, 1.7)), (1.0, -3.3, (1.3, 1.1, 1.0))],
          tufts=[(-1.4, -1.4, 1.0), (2.9, -3.3, 1.3), (9.4, -2.5, 1.1)])
    return done(kit, a, "variant", "precise", budget=3000,
                notes="snapped log: open end, splintered heartwood shards, split top, broken stub")


def low_stump(kit):
    a = new_asset(kit, "LowStump", 5431)
    rng = random.Random(5431)
    h, R = 4.0, 2.3
    Mz = Matrix(((0, 1, 0, 0), (0, 0, 1, 0), (1, 0, 0, 0), (0, 0, 0, 1)))  # local X -> world Z

    def radius(x):
        return R * (1 + 0.3 * max(0.0, 1 - x / 1.4) ** 2) * (1 - 0.05 * x / h)

    log_tube(a, Mz, h, radius, S=12, seed=5432, xs=[0.0, 0.45, 1.1, 2.2, h], kg=0.83, bore=None, crown=1.05,
             start="none", end="cap", amp0=0.0, amp1=0.0, cracks=4, x_jit=0.12, r_jit=0.07, end_bands=RINGS_FULL,
             capk=0.86)
    # long, thick flared roots
    for ang in (200, 255, 318, 25, 125):
        t = math.radians(ang + rng.uniform(-8, 8))
        dvec = Vector((math.cos(t), math.sin(t), 0))
        p0 = dvec * R * 0.55 + Vector((0, 0, 1.5))
        p1 = dvec * R * 1.15 + Vector((0, 0, 0.62))
        p2 = dvec * R * 1.68 + Vector((0, 0, 0.18))
        rings = tube(a, [p0, p1, p2], [1.15, 0.85, 0.48], 6, rng)
        splinter_tip(a, rings[-1], p2, (p2 - p1), 0.25, rng, mat=BARK)
    for x, y, rx, ry in ((-1.2, -3.3, 1.4, 0.8), (-2.9, 2.1, 1.0, 0.7)):
        ground_patch(a, (x, y), rx, ry, rng, yaw=math.atan2(y, x) + PI / 2, h=0.2)
    # lumpy moss mound over the front roots
    with dressing(a):  # walk-through moss mounds (kit_nocollide = 1)
        for x, y, z, r in ((-0.9, -3.0, 0.35, 0.8), (-1.9, -2.5, 0.5, 0.6)):
            rock(a, (x, y, 0.0), (r * 2.4, r * 2.0, r * 0.8 + z), rng, yaw=rng.uniform(0, PI), n=12, key=LEAF)
    for x, y, size in ((2.9, -2.8, (2.1, 1.8, 1.9)), (-3.5, -1.5, (1.7, 1.5, 1.5)), (3.5, 1.5, (1.0, 0.9, 0.9)),
                       (1.0, -3.9, (0.8, 0.7, 0.6))):
        rock(a, (x, y), size, rng, yaw=rng.uniform(0, 2 * PI))
    for x, y, s in ((-1.3, -3.6, 1.25), (-3.4, 0.9, 1.0)):
        fern(a, (x, y, 0.0), s, rng, n=7, key=LEAF)
    for x, y, hh in ((-4.0, -0.2, 1.5), (4.1, -1.0, 1.4), (1.4, 3.3, 1.2), (-1.6, 3.2, 1.0)):
        tuft(a, (x, y, 0.0), hh, rng, n=7)
    return done(kit, a, "variant", "hull", budget=3000,
                notes="low cut stump: flat ring top, ridged bark, flared roots, moss + grass foot")


def log_shell(kit):
    a = new_asset(kit, "LogShell", 5441)
    L, R = 12.0, 2.6
    # open -X end turned a little to the front-left like the sheet's shell; a
    # small turn keeps the +X end clear of the cap in the parts grid
    G, M = log_frame(L, 10, R * 0.97)
    log_tube(a, M, L, radius_fn(R, L), S=9, seed=5442, xs=[0.0, 0.0, 3.0, 5.0, 5.25, 7.4, 9.6, 11.2, L], bore=0.62,
             r_jit=0.04, start="open", end="open", amp0=0.45, amp1=0.35, cracks=1, kg=0.81, chamfer0=(0.4, 0.88),
             steps=[(170, 5.25), (115, 5.25), (230, 5.25)],
             # two broken-away staves at the +X end (stepped), as on the sheet's
             # shell: the dark bore shows there from the camera side too
             gap=[(95, 9.6), (135, 7.4)])
    return done(kit, a, "part", "precise", budget=1500,
                notes="bare hollow log tube, both ends open; precise collision keeps the bore walkable")


def log_cut_end_cap(kit):
    a = new_asset(kit, "LogCutEndCap", 5451)
    L, R = 1.6, 2.3
    Mc = Matrix.Translation((0, L / 2, R * 0.98)) @ Matrix(((0, 1, 0, 0), (-1, 0, 0, 0), (0, 0, 1, 0),
                                                            (0, 0, 0, 1)))  # local X -> world -Y
    log_tube(a, Mc, L, lambda x: R, S=10, seed=5452, xs=[0.0, L], kg=0.86, bore=None, start="cap", end="cap",
             amp0=0.0, amp1=0.0, cracks=0, x_jit=0.0, start_bands=RINGS_FEW, end_bands=RINGS_FULL)
    return done(kit, a, "part", "hull", budget=1500,
                notes="cut log disc standing on edge, ring face toward -Y; plugs a log end")


def log_branch_stub(kit):
    a = new_asset(kit, "LogBranchStub", 5461)
    rng = random.Random(5461)
    # thick limb rising to the right; its slanted saw cut faces the front-left
    # camera so the heartwood rings show
    branch(a, Vector((0, 0, 0.9)), Vector((0.8, 0.1, 0.58)), 2.5, 0.72, rng, sides=7, taper=0.8,
           prongs=[(Vector((0.95, 0.05, 0.3)), 1.9, 0.48), (Vector((-0.15, -0.05, 1.0)), 2.1, 0.44)],
           base_cut=True, cut_n=(-0.55, -0.8, 0.25))
    return done(kit, a, "part", "hull", budget=1500, notes="Y-forked broken branch with heartwood cut base")


def log_moss_foliage(kit):
    a = new_asset(kit, "LogMossFoliage", 5471)
    rng = random.Random(5471)
    for (x, y, s), key, n in zip(((-0.9, 0.0, 1.45), (0.5, 0.35, 0.8), (1.0, -0.3, 1.05)), (MOSS, GRASS, MOSS),
                                 (12, 7, 10)):
        fern(a, (x, y, 0.0), s, rng, n=n, key=key)
    return done(kit, a, "part", "none", budget=1500,
                notes="two leafy w05_moss clumps and a small w05_grass fern sprig to scatter on logs; walk-through")


def build(kit):
    return [
        fallen_hollow_log(kit),
        log_branch_stub(kit),
        log_moss_foliage(kit),
        log_shell(kit),
        log_cut_end_cap(kit),
        hollow_log(kit),
        broken_log(kit),
        low_stump(kit),
    ]
