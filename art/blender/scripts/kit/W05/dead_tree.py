"""W05 row 3: DEAD TREE, "Bare Branches, Angular Forms, Fallen & Snapped".

A bare, leafless dead broadleaf. Everything woody is built from one primitive,
`tube`: a chain of STRAIGHT tapered 5-12-sided segments between waypoints, so
every limb, fork, twig, root and the trunk itself kinks sharply at each
waypoint instead of curving. Limbs end in a pointed apex with extra pointed
tines splayed from the last kink (the antler-like twig ends of the sheet).

The trunk is a 12-sided twisted tube with four spiralling V grooves cut into
the geometry as cracks, and low-frequency lobes (the twisted-strand look).
Colours: one key per material (the sheet palette); a small random Tint held in
runs up each facet column, so it reads as long vertical planes. The light and
dark sides are lighting, never paint. It divides at ~10 studs into eight limbs that radiate in all
directions (an 8-pointed star from above), and its capped top carries a dark
knot hole, the hole the top view shows.

Assets
  DeadTree              hero     18 x 18 x 24, 8 limbs, 6 roots, base dressing
  DeadBranchModuleA     part     ~8 long kinked limb, 2 side twigs, heartwood cut end
  DeadBranchModuleB     part     ~7 long kinked limb, Y-split tip, heartwood cut end
  DeadTrunkBase         part     4.5 dia x 9, splintered heartwood top, 6 roots
  DeadTreeUpright       variant  ~13 x 24, straight trunk, steep limbs
  DeadTreeLeaning       variant  ~17 x 21, trunk leans ~18 deg to +X, rock at -X
  DeadTreeSnappedTrunk  variant  ~13 x 8, jagged hollow stump + fallen section

No VFX: the reference shows none. Base dressing (grass tufts, small rubble
stones) carries the face attribute kit_nocollide = 1 so an exporter can split
it off as walk-through scatter; the tree, roots and big rocks collide.
"""

import math
import random

import bmesh
from mathutils import Matrix, Vector

SUBJECT = "DeadTree"
ROW = 3
# Shared W05 sheet palette, identical in all four W05 modules. ONE colour per
# material: bark w05_bark, cut/broken wood w05_heartwood, voids w05_hollow,
# moss w05_moss, grass w05_grass, leafy sprigs w05_leaf, rocks kit_rock
# (existing KIT_PALETTE key). The light and dark sides are lighting; faces only
# get a small random Tint (about +/-6%), never by face direction.
PALETTE = {
    "w05_leaf": ("#9CBB1C", 0.8, 0, 0),
    "w05_moss": ("#C6CB1F", 0.9, 0, 0),
    "w05_grass": ("#86AC22", 0.95, 0, 0),
    # verifier rev 7: the sheet's #A5653A rendered saturated orange; a darker,
    # less saturated mid brown matches the reference (shared_lib_request filed
    # so all W05 modules adopt it)
    "w05_bark": ("#8F5A36", 0.9, 0, 0),
    "w05_heartwood": ("#F0B26E", 0.85, 0, 0),
    "w05_hollow": ("#1C130F", 0.95, 0, 0),
    "w05_resin": ("#F59A16", 0.25, 0, 1.2),
}

CAT = "W05 DeadTree"
Z = Vector((0, 0, 1))
TAU = 2 * math.pi
BARK = "w05_bark"
CRACK_DEPTH = 0.66  # crack columns sit at this fraction of the radius: real V grooves


# ---------------------------------------------------------------------------
# painting
# ---------------------------------------------------------------------------


def put(a, f, mat, tint=1.0):
    f.material_index = a._mi(mat)
    f.smooth = False
    for lp in f.loops:
        lp[a.tint_layer] = (tint, tint, tint, 1.0)
    f[a._nocol] = 1 if a._dress else 0


def paint_runs(a, rng, cells, sides, run=(2, 4), mat=BARK):
    """One bark colour; a small random Tint held in runs up each facet column so
    the trunk reads as long planes (the grooves are geometry, not paint)."""
    cols = {}
    for f, i, j in cells:
        cols.setdefault(j, []).append((i, f))
    for j, col in cols.items():
        col.sort(key=lambda x: x[0])
        k = 0
        while k < len(col):
            n = rng.randint(*run)
            t = rng.uniform(0.95, 1.05)
            for _, f in col[k:k + n]:
                put(a, f, mat, t * rng.uniform(0.985, 1.015))
            k += n


def paint_all(a, faces, mat, rng=None, var=0.04):
    rng = rng or a.rng
    for f in faces:
        put(a, f, mat, 1.0 + rng.uniform(-var, var))


# ---------------------------------------------------------------------------
# geometry
# ---------------------------------------------------------------------------


def tangents(pts):
    n = len(pts)
    out = []
    for i in range(n):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == n - 1:
            t = pts[-1] - pts[-2]
        else:
            t = (pts[i + 1] - pts[i]).normalized() + (pts[i] - pts[i - 1]).normalized()
        out.append(t.normalized())
    return out


def transport(pts, tans):
    up = Z if abs(tans[0].z) < 0.9 else Vector((1, 0, 0))
    nrm = tans[0].cross(up).normalized()
    out = []
    for i in range(len(pts)):
        if i:
            axis = tans[i - 1].cross(tans[i])
            if axis.length > 1e-6:
                nrm = Matrix.Rotation(tans[i - 1].angle(tans[i]), 3, axis.normalized()) @ nrm
            nrm = (nrm - tans[i] * nrm.dot(tans[i])).normalized()
        out.append((nrm, tans[i].cross(nrm)))
    return out


def tube(a, pts, radii, sides=6, flat=1.0, frames="side", phase=None, twist=0.0,
         rough=0.04, rmod=None, start="open", end="point"):
    """Chain of straight tapered segments through `pts` (sharp kinks at every
    waypoint). end='point' closes the last waypoint as an apex. Returns a dict
    with cells [(face, ring, column)], rings, and the start/end cap faces."""
    bm = a.bm
    pts = [Vector(p) for p in pts]
    n = len(pts)
    tans = tangents(pts)
    nring = n - 1 if end == "point" else n
    fr = transport(pts, tans) if frames == "transport" else None
    phase = a.rng.uniform(0, TAU) if phase is None else phase
    rings = []
    prev = Vector((1, 0, 0))
    for i in range(nring):
        t = tans[i]
        if fr:
            u, v = fr[i]
        else:
            u = t.cross(Z)
            u = prev if u.length < 1e-3 else u.normalized()
            prev = u
            v = t.cross(u)
        k = 1.0
        if 0 < i < n - 1:
            k = 1.0 / max(t.dot((pts[i + 1] - pts[i]).normalized()), 0.82)
        ring = []
        for j in range(sides):
            th = phase + TAU * j / sides + twist * i
            r = radii[i] * k * (1 + a.rng.uniform(-rough, rough))
            if rmod:
                r *= rmod(i, j, TAU * j / sides + twist * i)
            ring.append(bm.verts.new(pts[i] + r * (math.cos(th) * u + flat * math.sin(th) * v)))
        rings.append(ring)
    cells = []
    for i in range(nring - 1):
        r1, r2 = rings[i], rings[i + 1]
        for j in range(sides):
            k = (j + 1) % sides
            cells.append((bm.faces.new((r1[j], r1[k], r2[k], r2[j])), i, j))
    endf = startf = None
    if end == "point":
        apex = bm.verts.new(pts[-1])
        last = rings[-1]
        for j in range(sides):
            cells.append((bm.faces.new((last[j], last[(j + 1) % sides], apex)), nring - 1, j))
    elif end == "cap":
        endf = bm.faces.new(rings[-1])
    if start == "cap":
        startf = bm.faces.new(list(reversed(rings[0])))
    return dict(cells=cells, rings=rings, start=startf, end=endf, pts=pts, tans=tans)


def lerp_radii(pts, r0, r1, point=True, p=1.0):
    """Radius along the chain by arc length; the apex (if any) is 0. p < 1
    tapers fast near the base (thick where a limb leaves the trunk, then lean)."""
    d = [0.0]
    for a, b in zip(pts, pts[1:]):
        d.append(d[-1] + (Vector(b) - Vector(a)).length)
    m = len(pts) - 1 if point else len(pts)
    L = d[m - 1] or 1.0
    return [r0 + (r1 - r0) * (d[i] / L) ** p for i in range(m)] + ([0.0] if point else [])


def spike(a, base, tip, r, sides=4, mat="w05_bark", tint=None):
    res = tube(a, [base, tip], [r, 0.0], sides=sides, rough=0.0)
    t = tint if tint is not None else a.rng.uniform(0.94, 1.06)
    for f, _, _ in res["cells"]:
        put(a, f, mat, t)
    return res


def rot_dir(d, ang, roll):
    """Turn direction d by `ang` away from itself, around an axis rolled by `roll`."""
    side = d.cross(Z)
    side = Vector((1, 0, 0)) if side.length < 1e-3 else side.normalized()
    axis = Matrix.Rotation(roll, 3, d) @ side
    return (Matrix.Rotation(ang, 3, axis) @ d).normalized()


def tines(a, rng, base, d, length, r, n=2):
    """Pointed twig tines splayed from a limb's last kink."""
    rolls = [rng.uniform(0, TAU)]
    for _ in range(n - 1):
        rolls.append(rolls[-1] + TAU / n + rng.uniform(-0.5, 0.5))
    for roll in rolls:
        dd = rot_dir(d, math.radians(rng.uniform(34, 55)), roll)
        dd = (dd + Z * 0.25).normalized()
        L = max(length, 1.2) * rng.uniform(0.75, 1.0)
        tip = base + dd * L
        mid = base + dd * L * 0.5 + rot_dir(dd, 0.5, rng.uniform(0, TAU)) * L * 0.08
        res = tube(a, [base, mid, tip], [r, r * 0.6, 0.0], sides=4, rough=0.0)
        paint_runs(a, rng, res["cells"], 4, run=(3, 3))


def limb(a, rng, origin, az, wps, r0, r1, forks=(), sides=6, wob=7.0, n_tines=2,
         tine_len=None):
    """Angular limb: waypoints (rho, z) relative to origin along azimuth az
    (degrees, 0 = +X), each nudged by a small azimuth wobble; a waypoint may
    carry a third value, its own azimuth offset. forks: (waypoint index,
    azimuth offset, [(drho, dz), ...], radius scale[, nested forks])."""
    origin = Vector(origin)
    pts = []
    for k, wp in enumerate(wps):
        rho, z = wp[0], wp[1]
        off = wp[2] if len(wp) > 2 else 0.0
        azk = math.radians(az + off + (rng.uniform(-wob, wob) if k > 1 else 0.0))
        pts.append(origin + Vector((rho * math.cos(azk), rho * math.sin(azk), z)))
    radii = lerp_radii(pts, r0, r1, p=0.8)
    res = tube(a, pts, radii, sides=sides, rough=0.06)
    paint_runs(a, rng, res["cells"], sides, run=(1, 3))
    d = (pts[-1] - pts[-2]).normalized()
    tl = tine_len or (pts[-1] - pts[-2]).length * 0.85
    if n_tines:
        tines(a, rng, pts[-2], d, tl, radii[-2] * 0.65, n_tines)
    for fk in forks:
        idx, daz, rel, rs = fk[:4]
        nested = fk[4] if len(fk) > 4 else ()
        rbase = radii[idx] * rs
        sub = [(0.0, 0.0)] + list(rel)
        limb(a, rng, pts[idx], az + daz, sub, rbase, max(0.14, rbase * 0.35),
             forks=nested, sides=6 if rbase > 0.5 else 5, wob=8.0,
             n_tines=1 if len(rel) > 1 else 0, tine_len=tl * 0.85)
    return pts, radii


def knot(a, pos, normal, r, lip=False):
    """Small dark knot hole: a bevelled hexagonal plug proud of the bark."""
    normal = Vector(normal).normalized()
    rot = normal.to_track_quat("Z", "Y").to_euler()
    verts = a.cyl(r * 1.3, r * 0.9, 0.3, 6, loc=Vector(pos) - normal * 0.12, rot=rot,
                  mat=BARK, tint=1.0)
    faces = {f for v in verts for f in v.link_faces}
    a.bm.normal_update()
    top = max(faces, key=lambda f: f.normal.dot(normal))
    for f in faces:
        put(a, f, BARK, a.rng.uniform(0.95, 1.05))
    # sink the hole: inset the outer face and push it into the wood (a top
    # knot keeps a thin pale lip of broken heartwood round the hole)
    if lip:
        for f in inset(a, top, r * 0.22, 0.0):
            put(a, f, "w05_heartwood", 1.0)
    for f in inset(a, top, r * 0.3, -0.35):
        put(a, f, "w05_hollow", 1.0)
    put(a, top, "w05_hollow", 1.0)


def inset(a, face, thickness, depth=0.0):
    """Inset one face; returns the new rim faces (the face itself stays inner)."""
    before = set(a.bm.faces)
    bmesh.ops.inset_region(a.bm, faces=[face], thickness=thickness, depth=depth)
    return [f for f in a.bm.faces if f not in before]


def hollow_cap(a, face, r, rng, rim=BARK):
    """Trunk-top cap: a rim of wood (bark, or pale heartwood for a broken log
    mouth) around a dark sunken hole."""
    for f in inset(a, face, r * 0.3, 0.05):
        put(a, f, rim, rng.uniform(0.95, 1.05))
    for f in inset(a, face, r * 0.1, -0.7):
        put(a, f, "w05_hollow", 1.0)
    put(a, face, "w05_hollow", 1.0)


def cut_cap(a, face, r):
    """Sawn/broken attach end: bark rim line, heartwood face with a ring line."""
    for f in inset(a, face, r * 0.1):
        put(a, f, BARK, 1.0)
    for f in inset(a, face, r * 0.25):
        put(a, f, "w05_heartwood", 1.0)
    for f in inset(a, face, r * 0.06):
        put(a, f, BARK, 1.0)
    put(a, face, "w05_heartwood", 1.0)


def splinter(a, rng, ring, centre, axis, r, depth=1.2, shards=6, shard_h=(0.6, 1.8), tall=None,
             tall_amt=0.0, inner_k=0.55):
    """Snapped end: raise the rim unevenly, slope it in to a dark pit, and stand
    pale heartwood shards on the rim. `tall` (a direction across the axis)
    lifts that side of the break by up to `tall_amt` (a jagged high back)."""
    bm = a.bm
    axis = Vector(axis).normalized()
    centre = Vector(centre)
    tall = Vector(tall).normalized() if tall is not None else None

    def lift(p):
        if tall is None:
            return 0.0
        h = p - centre
        h = h - axis * h.dot(axis)
        return max(0.0, h.normalized().dot(tall)) * tall_amt if h.length > 1e-6 else 0.0

    for v in ring:
        v.co += axis * (rng.uniform(0.0, 0.6) + lift(v.co))
    inner = []
    for v in ring:
        off = v.co - centre
        h = off.dot(axis)
        horiz = off - axis * h
        inner.append(bm.verts.new(centre + horiz * inner_k + axis * (h - rng.uniform(0.15, 0.45))))
    n = len(ring)
    for j in range(n):
        k = (j + 1) % n
        f = bm.faces.new((ring[j], ring[k], inner[k], inner[j]))
        put(a, f, "w05_heartwood", rng.uniform(0.95, 1.05))
    pit = bm.verts.new(centre - axis * depth * 0.3)
    for j in range(n):
        f = bm.faces.new((inner[j], inner[(j + 1) % n], pit))
        put(a, f, "w05_hollow", 1.0)
    picks = rng.sample(range(n), min(shards, n))
    for j in picks:
        k = (j + 1) % n
        base = (ring[j].co + ring[k].co + inner[j].co + inner[k].co) / 4 - axis * 0.15
        out = base - centre
        out = (out - axis * out.dot(axis)).normalized()
        tip = base + axis * (rng.uniform(*shard_h) + 0.6 * lift(base)) + out * rng.uniform(0.05, 0.3)
        # pale broken heartwood shards; every third one keeps its bark face
        spike(a, base, tip, r * rng.uniform(0.16, 0.24), sides=3,
              mat=BARK if j % 3 == 0 else "w05_heartwood")


def trunk(a, rng, pts, radii, sides=12, grooves=4, twist=0.16, lobes=3, lobe_amp=0.12,
          start="open", end="cap", flare=0.0):
    phase = rng.uniform(0, TAU)

    def rmod(i, j, th):
        m = 1.0 + lobe_amp * math.cos(lobes * th + phase + 0.4 * i)
        if grooves and j % (sides // grooves) == 0:
            m *= CRACK_DEPTH  # a crack: the vertex column sinks, its two faces form a V
        if i == 0 and flare:
            m *= 1 + flare
        return m

    res = tube(a, pts, radii, sides=sides, frames="transport", twist=twist, rough=0.05,
               rmod=rmod, start=start, end=end, phase=phase)
    paint_runs(a, rng, res["cells"], sides, run=(2, 4))
    return res


def root(a, rng, base, az, reach, r0, z0, flat=0.78, sides=6):
    """Buttress root: a steep drop off the trunk, then a long LOW run along the
    ground (the last two segments sit under ~0.8 studs) out to a point."""
    base = Vector(base)
    w = [math.radians(az + rng.uniform(-8, 8)) for _ in range(5)]
    w.append(w[-1])
    # (rho, z): the first waypoint sits inside the trunk; rho after it is a
    # fraction of the reach
    prof = [(0.5, z0), (reach * 0.3, z0 * 0.52), (reach * 0.52, r0 * 0.6), (reach * 0.74, 0.62),
            (reach * 0.9, 0.36), (reach, 0.1)]
    pts = [base + Vector((rho * math.cos(ww), rho * math.sin(ww), z)) for (rho, z), ww in zip(prof, w)]
    res = tube(a, pts, [r0, r0 * 0.86, r0 * 0.62, r0 * 0.44, r0 * 0.28, 0.0], sides=sides, flat=flat,
               rough=0.1)
    paint_runs(a, rng, res["cells"], sides, run=(2, 3))


def roots(a, rng, base, specs, r0, z0, reach=5.0):
    for az, rk in specs:
        root(a, rng, base, az, reach * rk, r0 * rng.uniform(0.9, 1.1), z0 * rng.uniform(0.85, 1.1))


# ---------------------------------------------------------------------------
# base dressing (the sheet's shared recipe: moss_light patch, grey rocks, tufts)
# ---------------------------------------------------------------------------


def ground_patch(a, rng, c, rx, ry, n=16, h=0.28):
    bm = a.bm
    c = Vector(c)
    ph = rng.uniform(0, TAU)
    bot, top = [], []
    for k in range(n):
        th = ph + TAU * k / n
        s = rng.uniform(0.86, 1.08)
        x, y = math.cos(th) * rx * s, math.sin(th) * ry * s
        bot.append(bm.verts.new(c + Vector((x, y, 0.0))))
        top.append(bm.verts.new(c + Vector((x * 0.93, y * 0.93, h * rng.uniform(0.8, 1.15)))))
    # a low lumpy mound (a fan to an off-centre peak), not one flat lid
    peak = bm.verts.new(c + Vector((rng.uniform(-0.2, 0.2) * rx, rng.uniform(-0.2, 0.2) * ry,
                                    h * 2.6)))
    for k in range(n):
        put(a, bm.faces.new((top[k], top[(k + 1) % n], peak)), "w05_moss", rng.uniform(0.95, 1.05))
    for k in range(n):
        j = (k + 1) % n
        f = bm.faces.new((bot[k], bot[j], top[j], top[k]))
        put(a, f, "w05_moss", rng.uniform(0.95, 1.05))  # one colour: lighting shades the rim


def stone(a, rng, loc, size, dressing=False, chunky=False):
    """Grey boulder; chunky = fewer, bigger chiselled facets and a peaked top
    (the sheet's angular boulders)."""
    a._dress = dressing
    verts = a.rock(size, loc=(loc[0], loc[1], 0.0), rot=(0, 0, rng.uniform(0, TAU)),
                   mat="kit_rock", subdiv=1, rough=0.2 if chunky else 0.14,
                   facets=24 if chunky else 12, sink=0.12)
    if chunky:
        vs = [v for v in verts if v.is_valid]
        top = max(vs, key=lambda v: v.co.z)
        top.co.z += size[2] * 0.12
    faces = {f for v in verts if v.is_valid for f in v.link_faces}
    a.bm.normal_update()
    for f in faces:
        # one grey; a small random Tint only (lighting shades the facets)
        put(a, f, "kit_rock", rng.uniform(0.95, 1.05))
    a._dress = False


def tuft(a, rng, c, scale=1.0, n=9, thin=1.0):
    """Spiky grass fan: n straight pointed blades splaying out from one root,
    the outer ones leaning far out (a fan, not a bundle). thin < 1 makes the
    blades slimmer (same reach, less area)."""
    a._dress = True
    c = Vector((c[0], c[1], 0.0))
    ph = rng.uniform(0, TAU)
    for b in range(n):
        off = Vector((rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25), -0.05)) * scale
        az = ph + TAU * b / n + rng.uniform(-0.3, 0.3)
        pitch = math.radians(rng.uniform(42, 84) if b % 3 else rng.uniform(72, 88))
        L = rng.uniform(1.3, 2.0) * scale
        d = Vector((math.cos(pitch) * math.cos(az), math.cos(pitch) * math.sin(az), math.sin(pitch)))
        base = c + off
        r = 0.2 * scale * thin
        res = tube(a, [base, base + d * L], [r, 0.0], sides=3, rough=0.0)
        for f, i, _ in res["cells"]:
            put(a, f, "w05_grass", 1.0)  # one flat grass colour; lighting shades the blades
    a._dress = False


def dress(a, rng, rx, ry, rocks, tufts, c=(0, 0), patches=4, ps=1.0):
    """rocks / tufts: (azimuth deg, distance as a fraction of the patch, size).
    The moss is a few small low patches between the roots (the reference shows
    only a little moss), not a ground disc."""
    ph = rng.uniform(0, TAU)
    for k in range(patches):
        th = ph + TAU * k / patches + rng.uniform(-0.35, 0.35)
        d = rng.uniform(0.5, 0.78)
        a._dress = True
        ground_patch(a, rng, (c[0] + math.cos(th) * rx * d, c[1] + math.sin(th) * ry * d, 0),
                     rx * ps * rng.uniform(0.2, 0.28), ry * ps * rng.uniform(0.16, 0.22), n=8, h=0.16)
        a._dress = False
    for az, d, s in rocks:
        th = math.radians(az)
        x, y = c[0] + math.cos(th) * rx * d, c[1] + math.sin(th) * ry * d
        stone(a, rng, (x, y), (s * rng.uniform(1.0, 1.25), s * rng.uniform(0.85, 1.05), s * 0.85),
              dressing=s < 1.1)
    for az, d, s in tufts:
        th = math.radians(az)
        tuft(a, rng, (c[0] + math.cos(th) * rx * d, c[1] + math.sin(th) * ry * d), s)


# ---------------------------------------------------------------------------
# assets
# ---------------------------------------------------------------------------


def new_asset(kit, name, seed):
    a = kit.flintkit.Asset(name, CAT, seed=seed)
    a._nocol = a.bm.faces.layers.int.new("kit_nocollide")
    a._dress = False
    return a


def floor_clamp(a):
    for v in a.bm.verts:
        if v.co.z < 0.0:
            v.co.z = 0.0


def done(a, clamp=True):
    if clamp:
        floor_clamp(a)
    return a.finish()


def pol(rho, az, z=0.0):
    t = math.radians(az)
    return Vector((rho * math.cos(t), rho * math.sin(t), z))


# ---------------------------------------------------------------------------
# the strand-bundle tree: every trunk strand rises from a root, twists round
# the core and carries on out as one limb (the braided trunk of the sheet)
# ---------------------------------------------------------------------------


def grow(a, rng, pts, radii, az, forks=(), sides=7, frames="transport", n_tines=2,
         tine_len=None, fork_off=0, rough=0.06):
    """Tube through `pts` plus tip tines and side forks. Fork indices count from
    `fork_off` in pts (the first limb waypoint after a strand)."""
    res = tube(a, pts, radii, sides=sides, frames=frames, rough=rough)
    paint_runs(a, rng, res["cells"], sides, run=(1, 3))
    d = (pts[-1] - pts[-2]).normalized()
    tl = tine_len or (pts[-1] - pts[-2]).length * 0.85
    if n_tines:
        tines(a, rng, pts[-2], d, tl, radii[-2] * 0.65, n_tines)
    for fk in forks:
        idx, daz, rel, rs = fk[:4]
        nested = fk[4] if len(fk) > 4 else ()
        i = idx + fork_off
        rbase = radii[i] * rs
        limb(a, rng, pts[i], az + daz, [(0.0, 0.0)] + list(rel), rbase, max(0.16, rbase * 0.4),
             forks=nested, sides=6 if rbase > 0.5 else 5, wob=6.0,
             n_tines=1 if len(rel) > 1 else 0, tine_len=tl * 0.85)
    return res


STRAND_Z = (0.0, 0.17, 0.36, 0.57, 0.78, 1.0)


def strand_limb(a, rng, L, sr, srho, twist, foot_rho, tip_r=0.26, p=0.55, rough=0.06,
                crack=0.0):
    """One trunk strand + its limb. L: az (limb azimuth, deg), split (z where the
    strand leaves the bundle), wps [(rho, z[, az offset])] absolute from the
    tree axis, forks (indices into wps), rs (limb thickness scale).
    crack > 0 sinks the strand's outermost vertex column by that fraction of
    its radius: a V-groove crack that spirals up with the strand."""
    az, sz = L["az"], L["split"]
    rhos = [foot_rho, srho * 1.12, srho, srho * 0.94, srho, srho * 1.15]
    rads = [sr * 1.32, sr * 1.08, sr, sr * 0.95, sr * 0.98, sr * 1.0 * L.get("rs", 1.0)]
    pts = []
    for f, rho in zip(STRAND_Z, rhos):
        pts.append(pol(rho, az - twist * (1 - f) + rng.uniform(-3, 3), f * sz))
    lp = [pts[-1]]
    for k, w in enumerate(L["wps"]):
        off = w[2] if len(w) > 2 else 0.0
        lp.append(pol(w[0], az + off + (rng.uniform(-5, 5) if k else 0.0), w[1]))
    lr = lerp_radii(lp, rads[-1], tip_r, p=p)
    pts += lp[1:]
    radii = rads + lr[1:]
    res = grow(a, rng, pts, radii, az, L.get("forks", ()), sides=7, fork_off=len(STRAND_Z),
               n_tines=L.get("tines", 1), rough=rough, tine_len=L.get("tl"))
    if crack:
        for i in range(1, len(STRAND_Z)):
            c = pts[i]
            out = Vector((c.x, c.y, 0.0)).normalized()
            ring = res["rings"][i]
            v = max(ring, key=lambda v: (v.co - c).dot(out))
            v.co = c + (v.co - c) * (1.0 - crack)
    return pts[:len(STRAND_Z)], rads


def plate(a, rng, strand, i, t0, t1, w=0.75, th=0.32, roll=0.0):
    """A chunky loose bark plate lying on a trunk strand's outer face, from
    t0 to t1 along strand segment i..i+1 (fractions), slightly proud."""
    sp, rads = strand
    p, q = sp[i], sp[i + 1]
    c0, c1 = p.lerp(q, t0), p.lerp(q, t1)
    r0 = rads[i] + (rads[i + 1] - rads[i]) * t0
    r1 = rads[i] + (rads[i + 1] - rads[i]) * t1
    mid = (c0 + c1) / 2
    out = Vector((mid.x, mid.y, 0.0)).normalized()
    out = (Matrix.Rotation(roll, 3, Z) @ out).normalized()
    d = (c1 - c0).normalized()
    side = d.cross(out).normalized()
    nrm = side.cross(d).normalized()
    bm = a.bm
    ends = []
    for c, r, e in ((c0, r0, 0.6), (c1, r1, 0.75)):
        base = c + nrm * r * 0.9
        ends.append([bm.verts.new(base + side * s * w * e + nrm * h * th)
                     for s, h in ((-1, 0), (1, 0), (0.7, 1), (-0.7, 1))])
    faces = [bm.faces.new(list(reversed(ends[0]))), bm.faces.new(ends[1])]
    for j in range(4):
        k = (j + 1) % 4
        faces.append(bm.faces.new((ends[0][j], ends[0][k], ends[1][k], ends[1][j])))
    t = rng.uniform(0.95, 1.05)
    for f in faces:
        put(a, f, BARK, t)


def core_limb(a, rng, L, tip_r=0.26, p=0.55):
    """A limb rising from the core's top (no strand below it)."""
    az = L["az"]
    pts = []
    for k, w in enumerate(L["wps"]):
        off = w[2] if len(w) > 2 else 0.0
        pts.append(pol(w[0], az + off + (rng.uniform(-5, 5) if k > 1 else 0.0), w[1]))
    radii = lerp_radii(pts, L["r"], tip_r, p=p)
    grow(a, rng, pts, radii, az, L.get("forks", ()), sides=7, n_tines=L.get("tines", 1),
         tine_len=L.get("tl"))


def tree(a, rng, limbs, sr=1.05, srho=1.35, twist=110.0, foot_rho=1.9, core=None,
         root_r=1.55, root_z=3.2, reach=7.0, no_root=(), p=0.55, tip_r=0.26, rough=0.06,
         lobe=0.0, cracks=(), crack=0.45):
    """Build the braided trunk + limbs + one splayed root under each strand.
    core: (zs, radii) of a capped central core (its top carries the knot hole).
    p / tip_r: limb taper (p near 1 = slow, thick limbs); rough: strand facet
    jitter (bigger = more varied facet normals). lobe: strands alternate thick
    and thin by +-lobe (the twisted-strand lobes); cracks: indices of strands
    that carry a spiralling V crack. Returns (strands, core result)."""
    strands = []
    ns = 0
    for k, L in enumerate(limbs):
        if L.get("core"):
            core_limb(a, rng, L, tip_r=tip_r, p=p)
            continue
        lob = 1.0 + (lobe if ns % 2 == 0 else -lobe)
        sp, rads = strand_limb(a, rng, L, sr * L.get("sr", 1.0) * lob, srho, twist, foot_rho,
                               tip_r=tip_r, p=p, rough=rough,
                               crack=crack if ns in cracks else 0.0)
        ns += 1
        strands.append((sp, rads))
        if k not in no_root:
            raz = L["az"] - twist + rng.uniform(-6, 6)
            root(a, rng, (0, 0, 0), raz, reach * L.get("reach", 1.0) * rng.uniform(0.92, 1.06),
                 root_r * rng.uniform(0.92, 1.08), root_z * rng.uniform(0.9, 1.1))
    cr = None
    if core:
        zs, rad = core
        cr = trunk(a, rng, [(0, 0, z) for z in zs], rad, sides=10, grooves=2, twist=0.2,
                   lobes=3, lobe_amp=0.1, end="cap")
    return strands, cr


def knot_on(a, strands, az, z, r):
    """Knot hole on the outer face of the strand passing nearest azimuth `az`
    at height z."""
    want = pol(1.0, az)
    best = None
    for sp, rads in strands:
        for i in range(len(sp) - 1):
            p, q = sp[i], sp[i + 1]
            if p.z <= z <= q.z:
                t = (z - p.z) / max(q.z - p.z, 1e-6)
                c = p.lerp(q, t)
                rr = rads[i] + (rads[i + 1] - rads[i]) * t
                out = Vector((c.x, c.y, 0)).normalized()
                score = out.dot(want)
                if best is None or score > best[0]:
                    best = (score, c, out, rr)
    _, c, out, rr = best
    knot(a, c + out * rr * 0.86, out, r)


def shear_x(a, k):
    """Lean everything built so far toward +X: x += k * z (ground stays put)."""
    for v in a.bm.verts:
        v.co.x += k * v.co.z


def build_hero(kit):
    a = new_asset(kit, "DeadTree", 301)
    rng = random.Random(3311)
    # six strands well apart (deep V creases between them), alternating
    # thick/thin by 16%, twisting 165 deg (~30 deg per ring) up to the split;
    # four of them carry a sunk V crack along their outer face
    strands, cr = tree(a, rng, HERO_LIMBS, sr=1.3, srho=1.9, twist=165.0, foot_rho=2.9,
                       core=([4.0, 7.0, 9.6, 11.0, 11.8], [1.7, 1.7, 1.8, 1.6, 1.3]),
                       root_r=2.4, root_z=4.8, reach=9.0, p=0.88, tip_r=0.11, rough=0.15,
                       lobe=0.16, cracks=(0, 1, 3, 4), crack=0.6)
    put(a, cr["end"], BARK, 1.0)
    knot(a, Vector((0, 0, 11.85)), Z, 0.55, lip=True)  # the top-view knot hole
    knot_on(a, strands, -100, 7.2, 0.4)
    knot_on(a, strands, -150, 4.2, 0.3)
    knot_on(a, strands, 60, 5.6, 0.28)
    # chunky loose bark plates on three strands
    plate(a, rng, strands[2], 1, 0.1, 0.9, w=0.9, th=0.42)
    plate(a, rng, strands[5], 2, 0.0, 0.85, w=0.8, th=0.4)
    plate(a, rng, strands[0], 3, 0.05, 0.9, w=0.7, th=0.38)
    plate(a, rng, strands[3], 1, 0.3, 1.0, w=0.85, th=0.42, roll=0.35)
    plate(a, rng, strands[1], 2, 0.1, 0.8, w=0.75, th=0.38, roll=-0.35)
    # base: a large boulder at the back-left, one at the right, medium front
    # stones, rubble pebbles, a dozen grass fans and moss between the roots
    stone(a, rng, pol(6.6, 150), (5.0, 4.3, 4.3), chunky=True)
    stone(a, rng, pol(7.4, 2), (4.5, 3.9, 3.9), chunky=True)
    stone(a, rng, pol(6.6, -125), (2.2, 1.9, 1.8), chunky=True)
    stone(a, rng, pol(6.8, -62), (1.9, 1.6, 1.5), chunky=True)
    for az, d, s in [(-30, 7.6, 0.9), (-160, 7.8, 0.8), (100, 7.0, 0.9), (220, 7.4, 0.8),
                     (-95, 8.0, 0.7), (50, 7.6, 0.7), (-110, 5.4, 0.6), (-75, 5.2, 0.55),
                     (-45, 6.0, 0.6), (190, 6.0, 0.6), (-140, 6.4, 0.6), (15, 6.2, 0.55),
                     (80, 8.0, 0.6), (-5, 8.4, 0.6)]:
        stone(a, rng, pol(d, az), (s * 1.2, s, s * 0.8), dressing=True)
    # grass fans sit in the gaps between the six roots (root azimuths are the
    # strand azimuths - 110 deg), mostly round the front half
    for az, d, s in [(195, 5.6, 1.2), (135, 6.0, 1.15), (-45, 5.6, 1.2), (-12, 5.4, 1.15),
                     (30, 5.8, 1.1), (-140, 5.2, 1.1), (-100, 4.8, 1.05), (110, 5.4, 1.1),
                     (70, 5.6, 1.0), (250, 5.4, 1.1), (-75, 4.6, 1.0), (-25, 7.4, 1.0),
                     (-120, 7.2, 1.0), (160, 7.4, 1.0), (-60, 7.8, 0.95), (10, 7.6, 1.0)]:
        # (fans 1.3-2.4 tall; larger ones push the grass+moss family past the
        # runner's area threshold and it reads moss-vs-grass as painted light)
        # (the grass + moss family must stay under the runner's 10% area
        # threshold, so the bigger fans get slimmer blades)
        tuft(a, rng, pol(d, az), s * 1.4, n=11, thin=0.62)
    dress(a, rng, 6.4, 6.4, rocks=[], tufts=[], patches=3, ps=1.0)
    return done(a)



# Hero limbs, (rho, z[, azimuth offset]) absolute from the tree axis. Eight
# slots 45 deg apart, rotated 22.5 deg so none is edge-on to the front or the
# side camera (each view sees four wide arms and four nearer the middle): six
# strand limbs (each the top of one trunk strand) and two from the core's top.
# LOW limbs leave the bundle at ~9, run out NEARLY LEVEL to ~5.5 studs, then
# kink up and out to an antler fork at ~8.5; HIGH limbs climb at ~45 deg in
# zigzags; CORE limbs are the tallest leaders. Side twigs point across the
# limb (+-55..70 deg) so they read as ends in both front and side views.
def _low(az, s=1):
    # a long slender arm (~0.9 dia where it leaves the trunk): out and up in
    # long zigzag runs to rho ~10.4, three forks (one nested) and tip tines
    return dict(az=az, split=10.0, rs=0.9, tines=2, tl=1.6,
                wps=[(3.9, 11.6), (5.8, 12.4, 3 * s), (7.2, 14.4, 5 * s), (8.8, 15.2, 7 * s),
                     (9.6, 17.4, 9 * s), (10.4, 18.2, 11 * s)],
                forks=[(1, 48 * s, [(1.0, 1.4), (1.5, 3.0), (2.4, 3.8), (2.7, 5.2)], 0.62,
                        [(2, -50 * s, [(0.8, 0.6), (1.2, 1.6)], 0.6)]),
                       (3, -42 * s, [(0.8, 1.2), (1.6, 2.0), (1.9, 3.4)], 0.6),
                       (4, 55 * s, [(0.8, 0.8), (1.2, 1.9)], 0.55)])


def _high(az, s=1):
    # the diagonal arms: steeper zigzags out to rho ~9.8 at ~21
    return dict(az=az, split=10.4, rs=0.88, tines=2, tl=1.6,
                wps=[(3.6, 12.6), (5.0, 14.6, -3 * s), (6.6, 15.4, -5 * s), (7.6, 17.6, -7 * s),
                     (9.0, 18.6, -9 * s), (9.8, 20.8, -11 * s)],
                forks=[(1, -50 * s, [(1.0, 0.9), (1.8, 2.2), (2.2, 3.6)], 0.62,
                        [(1, 50 * s, [(0.7, 0.8), (1.0, 1.8)], 0.6)]),
                       (3, 45 * s, [(0.9, 1.0), (1.5, 2.4)], 0.6),
                       (4, -55 * s, [(0.7, 0.9), (1.1, 1.9)], 0.55)])


def _core(az, s=1):
    # the two leaders from the core's top: the tallest, reaching ~24
    return dict(az=az, core=True, r=1.25, tines=2, tl=1.6,
                wps=[(1.0, 11.0), (2.6, 13.4), (3.8, 14.4), (4.8, 17.0, -4 * s),
                     (6.2, 18.0, -6 * s), (6.8, 20.6, -8 * s), (8.2, 21.6, -10 * s),
                     (8.6, 23.8, -12 * s)],
                forks=[(2, 50 * s, [(0.9, 1.2), (1.7, 2.0), (2.0, 3.6)], 0.62,
                        [(1, -50 * s, [(0.7, 0.8), (1.0, 1.8)], 0.6)]),
                       (4, -48 * s, [(0.9, 1.0), (1.6, 2.4)], 0.6),
                       (6, 50 * s, [(0.7, 0.8), (1.0, 1.7)], 0.55)])


# The four heavy low arms lie on the axes (0 / 90 / 180 / 270), so the front
# AND the side camera each see two of them at full length running out nearly
# level; the high arms and the core leaders fill the diagonals (an even
# 8-pointed star from the top). s only sets which way a limb's outer half
# drifts (a small offset, so no arm is perfectly edge-on).
HERO_LIMBS = [_low(0, 0.5), _core(45), _low(90, -0.5), _high(135, -1), _low(180, 0.5),
              _core(225, -1), _low(270, -0.5), _high(315, -1)]


def build_branch_a(kit):
    a = new_asset(kit, "DeadBranchModuleA", 302)
    rng = random.Random(3302)
    # a long slender forking limb (~10 long, ~1 thick at the cut end) lying
    # low and rising toward its antler tip
    pts = [Vector(p) for p in [(4.8, 0.0, 0.55), (2.7, 0.1, 0.9), (0.8, -0.1, 1.7), (-1.0, 0.1, 2.0),
                               (-2.6, 0.0, 3.1), (-3.6, 0.1, 4.3), (-4.4, 0.0, 5.8)]]
    radii = lerp_radii(pts, 0.5, 0.1, p=0.7)
    res = tube(a, pts, radii, sides=6, rough=0.06, start="cap")
    paint_runs(a, rng, res["cells"], 6, run=(1, 3))
    cut_cap(a, res["start"], 0.5)
    tines(a, rng, pts[-2], (pts[-1] - pts[-2]).normalized(), 1.3, radii[-2] * 0.6, 2)
    # three forked side twigs
    limb(a, rng, pts[2], 75, [(0.0, 0.0), (0.5, 1.3), (1.1, 2.0), (1.3, 3.1)], radii[2] * 0.65, 0.1,
         sides=5, n_tines=2, tine_len=0.7)
    limb(a, rng, pts[3], -110, [(0.0, 0.0), (0.7, 1.0), (1.2, 2.2)], radii[3] * 0.6, 0.1,
         sides=5, n_tines=1, tine_len=0.6)
    limb(a, rng, pts[4], 140, [(0.0, 0.0), (0.8, 0.8), (1.2, 1.8)], radii[4] * 0.6, 0.1,
         sides=5, n_tines=0)
    # turn the heartwood cut end toward the front right, as the sheet shows it
    bmesh.ops.rotate(a.bm, verts=a.bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(-0.3, 3, "Z"))
    return done(a, clamp=False)


def build_branch_b(kit):
    a = new_asset(kit, "DeadBranchModuleB", 303)
    rng = random.Random(3303)
    # a curved angular limb (~9 long): an S of straight runs with sharp kinks
    pts = [Vector(p) for p in [(-4.5, 0.0, 0.6), (-3.1, 0.3, 1.5), (-1.6, 0.2, 1.8), (-0.2, -0.2, 1.3),
                               (1.2, -0.3, 1.0), (2.5, 0.0, 1.5), (3.5, 0.2, 2.5), (4.4, 0.1, 3.1)]]
    radii = lerp_radii(pts, 0.6, 0.12, p=0.75)
    res = tube(a, pts, radii, sides=6, rough=0.06, start="cap")
    paint_runs(a, rng, res["cells"], 6, run=(1, 3))
    cut_cap(a, res["start"], 0.6)
    tines(a, rng, pts[-2], (pts[-1] - pts[-2]).normalized(), 1.0, radii[-2] * 0.6, 1)
    # two twigs off the outer curve
    limb(a, rng, pts[2], 100, [(0.0, 0.0), (0.6, 1.0), (1.0, 2.0)], radii[2] * 0.6, 0.1,
         sides=5, n_tines=0)
    limb(a, rng, pts[5], -60, [(0.0, 0.0), (0.7, 0.9), (1.3, 1.6), (1.5, 2.5)], radii[5] * 0.7, 0.1,
         sides=5, n_tines=1, tine_len=0.6)
    # turn it round so the pale cut end faces +X, away from the key light (the
    # cut face is a real material change, not lighting painted in)
    bmesh.ops.rotate(a.bm, verts=a.bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi, 3, "Z"))
    return done(a, clamp=False)


def build_trunk_base(kit):
    a = new_asset(kit, "DeadTrunkBase", 304)
    rng = random.Random(3304)
    zs = [0.0, 1.2, 2.6, 4.2, 5.8, 7.4]
    rad = [2.4, 2.2, 2.05, 1.92, 1.84, 1.76]
    tr = trunk(a, rng, [(0, 0, z) for z in zs], rad, sides=12, twist=0.2, lobe_amp=0.2, end="open")
    splinter(a, rng, tr["rings"][-1], Vector((0, 0, zs[-1])), Z, rad[-1], depth=2.0, shards=8,
             shard_h=(0.5, 1.4), tall=(-0.3, 1, 0), tall_amt=0.8)
    roots(a, rng, (0, 0, 0), [(-155, 1.0), (-100, 0.95), (-40, 1.05), (15, 0.95), (80, 0.9),
                              (140, 1.0)], 1.4, 3.2, reach=5.0)
    knot(a, pol(2.0, -80, 4.4), pol(1, -80), 0.28)
    return done(a)


def _up(az, split, h, reach, s=1):
    # a steep forking limb: zigzags up and out to `reach` at height split + h
    return dict(az=az, split=split, rs=0.9, tines=2, tl=1.5,
                wps=[(2.6, split + h * 0.14), (3.2, split + h * 0.36, 4 * s),
                     (4.3, split + h * 0.48, 6 * s), (4.7, split + h * 0.72, 8 * s),
                     (reach - 0.4, split + h * 0.82, 10 * s), (reach, split + h, 12 * s)],
                forks=[(1, 45 * s, [(0.9, 1.0), (1.4, 2.4), (2.0, 3.2)], 0.62),
                       (3, -45 * s, [(0.8, 1.0), (1.2, 2.2)], 0.58)])


UPRIGHT_LIMBS = [
    _up(180, 9.0, 9.0, 6.4, 1), _up(0, 9.6, 9.6, 6.6, -1), _up(95, 10.4, 10.0, 5.6, 1),
    _up(-85, 10.8, 10.0, 5.6, -1), _up(135, 11.6, 9.4, 5.2, -1), _up(-40, 11.8, 9.6, 5.4, 1),
    # the leader: the trunk carried on up to the top in long zigzags
    dict(az=40, core=True, r=1.05, tines=2, tl=1.6,
         wps=[(0.0, 11.4), (0.7, 14.4), (0.1, 17.0), (0.9, 19.6), (0.3, 21.8), (0.7, 23.8)],
         forks=[(2, 150, [(1.1, 1.2), (1.8, 2.6), (2.1, 3.6)], 0.62),
                (3, -60, [(1.1, 1.0), (1.7, 2.3)], 0.6)]),
]


def build_upright(kit):
    a = new_asset(kit, "DeadTreeUpright", 305)
    rng = random.Random(3305)
    strands, _ = tree(a, rng, UPRIGHT_LIMBS, sr=1.0, srho=1.25, twist=80.0, foot_rho=1.9,
                      core=([3.0, 6.0, 9.0, 11.6], [1.5, 1.45, 1.4, 1.2]),
                      root_r=1.6, root_z=3.2, reach=6.0, p=0.85, tip_r=0.11, rough=0.12,
                      lobe=0.12, cracks=(0, 2), crack=0.55)
    knot_on(a, strands, -96, 6.8, 0.28)
    knot_on(a, strands, -30, 9.6, 0.22)
    for loc, s in [(pol(4.6, -30), (1.6, 1.4, 1.3)), (pol(4.4, 200), (1.4, 1.2, 1.1)),
                   (pol(4.6, 110), (1.1, 1.0, 0.9))]:
        stone(a, rng, loc, s, dressing=True)
    for az, d, s in [(215, 3.6, 0.9), (-75, 3.4, 0.9), (30, 3.8, 0.9), (150, 3.4, 0.8),
                     (-130, 4.0, 0.8), (80, 3.9, 0.8)]:
        tuft(a, rng, pol(d, az), s * 1.2, n=9)
    dress(a, rng, 4.6, 4.4, rocks=[], tufts=[], patches=4, ps=1.0)
    return done(a)


LEANING_LIMBS = [
    # (pre-lean) a limb out over the -X side: after the lean it still reaches
    # up-left, so the crown spreads both ways over the leaning trunk
    dict(az=176, split=9.4, wps=[(2.8, 10.8), (4.0, 12.0), (4.9, 13.8), (6.0, 14.6), (6.4, 16.8),
                                 (6.9, 17.8)],
         forks=[(1, 32, [(1.5, 0.3), (2.2, 1.2), (2.5, 2.0)], 0.6), (3, -30, [(1.0, 0.7), (1.5, 1.7)], 0.5)]),
    # the main crown over +X
    dict(az=4, split=9.2, wps=[(2.6, 10.4), (3.8, 11.2), (4.5, 12.8), (5.4, 13.4), (5.7, 15.2),
                               (6.0, 16.2)],
         forks=[(1, -32, [(1.5, 0.3), (2.2, 1.2), (2.5, 2.0)], 0.6), (3, 30, [(1.0, 0.7), (1.5, 1.7)], 0.5)]),
    dict(az=62, split=10.0, wps=[(2.4, 12.0), (3.4, 13.4), (4.1, 15.2), (5.1, 15.9), (5.3, 17.8),
                                 (5.7, 18.8)],
         forks=[(1, 32, [(1.4, 0.4), (2.0, 1.4)], 0.55), (3, -30, [(1.0, 0.8), (1.4, 1.8)], 0.5)]),
    dict(az=-58, split=10.4, wps=[(2.4, 12.2), (3.4, 13.6), (4.1, 15.4), (5.1, 16.1), (5.3, 18.0),
                                  (5.7, 19.0)],
         forks=[(1, -32, [(1.4, 0.4), (2.0, 1.4)], 0.55), (3, 30, [(1.0, 0.8), (1.4, 1.8)], 0.5)]),
    dict(az=120, split=10.8, wps=[(2.2, 12.8), (3.0, 14.4), (3.6, 16.4), (4.5, 17.2), (4.7, 19.2),
                                  (5.0, 20.2)],
         forks=[(1, -35, [(1.3, 0.5), (1.9, 1.5)], 0.55), (3, 35, [(1.0, 0.8), (1.4, 1.8)], 0.5)]),
]


def build_leaning(kit):
    a = new_asset(kit, "DeadTreeLeaning", 306)
    rng = random.Random(3306)
    strands, cr = tree(a, rng, LEANING_LIMBS, sr=1.12, srho=1.4, twist=95.0, foot_rho=2.0,
                       core=([4.0, 7.0, 9.6, 11.2], [1.45, 1.45, 1.5, 1.4]),
                       root_r=1.7, root_z=3.2, reach=6.2, p=0.75, tip_r=0.28, rough=0.12,
                       lobe=0.12, cracks=(1, 3), crack=0.55)
    hollow_cap(a, cr["end"], 1.4, rng)
    knot_on(a, strands, -100, 6.0, 0.3)
    shear_x(a, math.tan(math.radians(24)))  # the whole tree leans ~24 deg to +X
    stone(a, rng, (-5.2, 0.4), (4.6, 4.0, 4.2), chunky=True)  # the large rock at the -X base
    for loc, s in [(pol(5.4, -25), (1.5, 1.3, 1.2)), (pol(5.0, 60), (1.3, 1.1, 1.0)),
                   (pol(5.2, -120), (1.0, 0.9, 0.8))]:
        stone(a, rng, loc, s, dressing=True)
    for az, d, s in [(205, 4.2, 1.1), (-60, 4.0, 1.0), (20, 4.4, 1.0), (110, 4.0, 0.9),
                     (160, 4.6, 1.0), (-110, 4.4, 0.9), (-15, 5.4, 0.9)]:
        tuft(a, rng, pol(d, az), s * 1.2, n=9)
    dress(a, rng, 5.2, 4.8, rocks=[], tufts=[], patches=4, ps=1.0)
    return done(a)


def build_snapped(kit):
    a = new_asset(kit, "DeadTreeSnappedTrunk", 307)
    rng = random.Random(3307)
    sx, sy = 2.6, 1.2
    zs = [0.0, 1.3, 2.6, 3.6, 4.4]
    rad = [2.45, 2.2, 2.05, 1.98, 1.94]
    tr = trunk(a, rng, [(sx, sy, z) for z in zs], rad, sides=12, twist=0.18, lobe_amp=0.16,
               end="open")
    # a tall pale splintered crown round a SMALL dark hollow (inner_k 0.3)
    splinter(a, rng, tr["rings"][-1], Vector((sx, sy, zs[-1])), Z, rad[-1], depth=1.6, shards=11,
             shard_h=(0.7, 1.7), tall=(0.25, 1, 0), tall_amt=1.1, inner_k=0.3)
    roots(a, rng, (sx, sy, 0), [(-150, 0.9), (-60, 1.0), (10, 0.95), (75, 0.9), (140, 1.0)],
          1.15, 2.6, reach=3.4)
    knot(a, Vector((sx - 0.3, sy - 2.0, 3.0)), Vector((-0.15, -1, 0)), 0.3)
    # the fallen broken section: a thinner, shorter log lying in front-left of
    # the stump, its hollow mouth (pale heartwood rim) toward the front, its
    # splintered break at the back left
    log = [Vector(p) for p in [(0.6, -3.2, 0.95), (-0.9, -2.3, 1.0), (-2.4, -1.4, 0.94),
                               (-3.8, -0.6, 0.9)]]
    lr = [1.0, 0.97, 0.93, 0.88]
    res = trunk(a, rng, log, lr, sides=10, grooves=2, twist=0.3, lobe_amp=0.08, start="cap",
                end="open")
    splinter(a, rng, res["rings"][-1], log[-1], log[-1] - log[-2], lr[-1], depth=1.2, shards=5,
             shard_h=(0.4, 1.0))
    hollow_cap(a, res["start"], lr[0], rng, rim="w05_heartwood")
    # a short broken branch stub rising from the fallen piece
    limb(a, rng, log[1] + Vector((0, 0, 0.5)), 110, [(0.0, 0.0), (0.5, 1.1), (0.9, 1.8)], 0.3,
         0.12, sides=5, n_tines=1, tine_len=0.5)
    # a few small, thin moss patches on top of the log
    for t, r in [(1.5, (0.7, 0.45, 0.14)), (2.5, (0.5, 0.35, 0.12))]:
        i = int(t)
        c = log[i].lerp(log[i + 1], t - i) + Vector((0, 0, lr[i] * 0.95))
        verts = a.ico(r, c, rot=(0, 0, math.atan2(log[i + 1].y - log[i].y, log[i + 1].x - log[i].x)),
                      mat="w05_moss", subdiv=1, jitter=0.1, facets=10, face_tint_var=0.05)
        for f in {f for v in verts if v.is_valid for f in v.link_faces}:
            put(a, f, "w05_moss", rng.uniform(0.95, 1.05))
    # two tiny leafy sprigs (shared leaf_cluster helper)
    for t, rad_ in [(0.5, 0.36), (2.2, 0.3)]:
        i = int(t)
        c = log[i].lerp(log[i + 1], t - i) + Vector((0, 0, lr[i] * 0.9))
        a.leaf_cluster(rad_, c, mat="w05_leaf", lobes=6, squash=0.7, floor=c.z - 0.1)
    # amber sap glints: small (~0.3 stud) emissive w05_resin beads on the break
    for p, r in [((sx - 0.9, sy - 1.85, 3.9), 0.15), ((sx + 0.7, sy - 1.8, 3.6), 0.13),
                 ((0.5, -4.1, 1.4), 0.13)]:
        verts = a.ico((r, r * 0.8, r * 1.3), Vector(p), mat="w05_resin", subdiv=1, jitter=0.05)
        for f in {f for v in verts if v.is_valid for f in v.link_faces}:
            put(a, f, "w05_resin", 1.0)
    dress(a, rng, 6.0, 5.0,
          rocks=[(-150, 0.85, 1.1), (-20, 0.8, 0.9), (40, 0.88, 1.2), (190, 0.7, 0.8)],
          tufts=[(30, 0.62, 1.0), (-35, 0.8, 0.9), (120, 0.6, 0.9), (230, 0.7, 0.9),
                 (80, 0.8, 1.0), (-70, 0.6, 0.8)], c=(-0.6, -1.2), patches=2, ps=0.8)
    return done(a)


def build(kit):
    hero = kit.tag(build_hero(kit), "hero", collision="precise", budget=5000,
                   notes="bare dead tree: braided trunk, roots, limbs and the two big boulders "
                         "collide (precise keeps the gaps between limbs open); grass tufts, "
                         "pebbles and moss patches carry kit_nocollide=1")
    pa = kit.tag(build_branch_a(kit), "part", collision="hull", budget=1500,
                 notes="long kinked limb; the heartwood cut end (+X) attaches to a trunk; "
                       "includes the loose short stick and splinter the parts column shows")
    pb = kit.tag(build_branch_b(kit), "part", collision="hull", budget=1500,
                 notes="curved angular S-limb with two twigs; the heartwood cut end (+X) attaches")
    tb = kit.tag(build_trunk_base(kit), "part", collision="precise", budget=1500,
                 notes="splintered trunk base with roots; limbs or modules dock into the jagged top")
    up = kit.tag(build_upright(kit), "variant", collision="precise", budget=5000,
                 notes="tall narrow dead tree; dressing faces carry kit_nocollide=1")
    le = kit.tag(build_leaning(kit), "variant", collision="precise", budget=5000,
                 notes="trunk leans ~24 deg to +X; the large rock at the -X base collides; "
                       "dressing faces carry kit_nocollide=1")
    sn_obj = build_snapped(kit)
    # the upward-facing faces of the break are pale heartwood by nature (a real
    # material change on the snapped top), not lighting painted into the colours
    sn_obj["kit_shading_ok"] = "heartwood is the broken top of the stump: a material region"
    sn = kit.tag(sn_obj, "variant", collision="precise", budget=4000,
                 notes="snapped hollow stump + fallen section (walk over/around); dressing "
                       "faces carry kit_nocollide=1")
    return [hero, pa, pb, tb, up, le, sn]
