"""W04 row 4: OLD PINE, an ancient gnarled umbrella pine (bonsai-like).

Assets
  OldPine              hero (~22 x 20 x 24): a massive, deeply grooved trunk with a
                       strong spiral twist and a buttress-root flare, forking at ~12
                       studs into two leaders; angled side branches each carry a flat
                       cloud pad (clusters of star-shaped needle clumps) with a flat
                       underside; two broken stubs with a pale cut rim around a
                       recessed hollow; pale rocks, grass and leafy fern tufts on a
                       wide sandy soil patch.
  OldPineCanopyTier    part: one canopy pad (~6 x 6 x 2.5)
  OldPineBranchAngled  part: a bent log branch with an elbow and hollow cut ends
  OldPineForkedTrunk   part: the trunk from the roots to the fork, both leaders cut flat
                       and hollow
  OldPineRootsBase     part: the root spread cut at ~2.5 studs with rocks, grass, soil
  OldPineSplitTrunk    variant: trunk splits low into a V of two leaders
  OldPineBent          variant: S-curved trunk with a long near-horizontal branch
  OldPineBrokenCrown   variant: tall bare trunk snapped at the top (jagged splinters)

Technique: trunks, leaders, roots and branches are swept faceted tubes (parallel
transport frames, as build_05 trunk()). The trunk is a fat cone with 6 broad
lobes split by narrow deep V grooves, twisted 0.14 rad/stud so the grooves
spiral, flaring into buttress roots that continue the lobes. Leaders rise out
of the trunk top and splay apart (a Y); limbs have sharp elbows (polyline()).

Pads are layered FLAT star rosettes (star(): n broad pointed leaves folded
along a midrib round a low peak, h/R ~0.35, drooping tips and a flat
down-facing underside): a big base star, a ring of outward-tilted satellite
stars at its rim, a smaller upper star turned half a leaf and a raised centre
star. From above each pad reads as one star cluster; from the side as a flat
layered pad with a dark underside band (shading, not paint).

ONE colour per material (w04_bark, w04_needle, w04_wood_end, w04_grass,
kit_rock, w04_ground), every Tint 1.0 +/- a few percent: the reference's dark
grooves, dark pad undersides and black hollows are lighting made by geometry
(V grooves, flat pad floors, narrow deep undercut hollows). The leafy bushes at
the base are the same foliage as the pads (w04_needle); the lime grass tufts
are w04_grass. Buried geometry is clamped to z=0. Walk-through dressing (grass,
bushes) carries the face attribute kit_nocollide = 1. No VFX: the reference
shows none (no fire, water or harvest).
"""

import math
import random

import bmesh
from mathutils import Matrix, Vector

SUBJECT = "OldPine"
ROW = 4
PALETTE = {
    "w04_needle": ("#5E8E1A", 0.8, 0, 0),
    "w04_bark": ("#9A6038", 0.9, 0, 0),
    "w04_wood_end": ("#E4A458", 0.85, 0, 0),
    "w04_ground": ("#DCC9A0", 0.95, 0, 0),
    "w04_grass": ("#8DB83A", 0.9, 0, 0),
    # "kit_rock": ("#A89C9C", 0.9, 0, 0),  # Existing KIT_PALETTE key (used as-is; the runner only accepts w04_-prefixed keys here): the pale grey faceted rocks/pebbles at every tree base.
}

TAU = 2 * math.pi
Z = Vector((0, 0, 1))
F_BARK, F_NEEDLE, F_ROCK, F_GRASS = 1, 3, 4, 5

# ONE colour per material, every Tint 1.0 with a small random variation (the
# Roblox export pins each colour's Tint levels near 1.0; a per-material Tint
# level lands off them). The reference's lit tops, dark grooves, dark pad
# undersides and black hollows are LIGHTING made by geometry.


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------


def new_asset(kit, name, seed):
    a = kit.flintkit.Asset(name, f"Kit {kit.sheet} {kit.subject}", seed=seed, tint_var=0.05)
    a.bm.faces.layers.int.new("fam")
    a.bm.faces.layers.int.new("kit_nocollide")
    return a


def paint(a, faces, mat, tint=1.0, var=0.04, fam=0, nocollide=False):
    mi = a._mi(mat)
    lay = a.bm.faces.layers.int["fam"]
    nc = a.bm.faces.layers.int["kit_nocollide"]
    for f in faces:
        f.material_index = mi
        f.smooth = False
        t = tint * (1.0 + a.rng.uniform(-var, var))
        for lp in f.loops:
            lp[a.tint_layer] = (t, t, t, 1.0)
        f[lay] = fam
        if nocollide:
            f[nc] = 1
    return faces


def mk_face(a, verts, out_dir=None, out_from=None):
    """New face; flipped so its normal points along out_dir (or away from out_from)."""
    clean = []
    for v in verts:
        if not clean or clean[-1] is not v:
            clean.append(v)
    if len(clean) > 1 and clean[0] is clean[-1]:
        clean.pop()
    if len(clean) < 3:
        return None
    try:
        f = a.bm.faces.new(clean)
    except ValueError:
        return None
    f.normal_update()
    if out_dir is None and out_from is not None:
        out_dir = f.calc_center_median() - Vector(out_from)
    if out_dir is not None and f.normal.dot(Vector(out_dir)) < 0:
        f.normal_flip()
    return f


def polar(r, az, z):
    return Vector((r * math.cos(az), r * math.sin(az), z))


def bezier(p0, p1, p2, n):
    p0, p1, p2 = Vector(p0), Vector(p1), Vector(p2)
    return [(1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2 for t in (i / (n - 1) for i in range(n))]


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


# ---------------------------------------------------------------------------
# Wood: tubes, cut ends, broken tops
# ---------------------------------------------------------------------------


def tube(a, pts, radii, sides=8, lobes=0, depth=0.0, twist=0.0, flare=(), squash=1.0,
         rough=0.04, caps=("flat", "flat"), fam=F_BARK, mat="w04_bark", hollow=None, shoulder=0.45, rim=0.82):
    """Swept faceted tube in one material. With `lobes`, sides = lobes * k and every
    k-th vertex is a groove pulled in by `depth` (its neighbours a little), so the
    faces either side of it form a V notch that the light shades dark. `twist`
    turns the rings so the grooves spiral. `flare` bulges the lobes of the first
    rings (buttresses). `squash` < 1 narrows the horizontal width of the cross-
    section (root fins). caps: 'flat', 'cut' (pale rim, recessed hollow) or None."""
    pts = [Vector(p) for p in pts]
    fr = frames(pts)
    per = sides // lobes if lobes else 0
    phase = a.rng.uniform(0, TAU)
    # twist is radians per stud of length, so the grooves spiral at an even
    # lean all the way up (not fast at the closely spaced base rings only)
    arc = [0.0]
    for i in range(1, len(pts)):
        arc.append(arc[-1] + (pts[i] - pts[i - 1]).length)
    rings = []
    for i, (t, n, b) in enumerate(fr):
        h = t.cross(Z)
        hn = h.normalized() if h.length > 0.25 else None
        fl = flare[i] if i < len(flare) else 0.0
        ring = []
        for j in range(sides):
            loc = TAU * j / sides
            th = loc + twist * arc[i] + phase
            r = radii[i]
            if lobes:
                bulge = (1 - math.cos(lobes * loc)) / 2  # 0 at grooves, 1 mid-lobe
                if fl:
                    r *= 1 + fl * (0.2 + 0.8 * bulge ** 2)
                if j % per == 0:
                    r *= 1 - depth
                elif per > 3 and j % per in (1, per - 1):
                    r *= 1 - depth * shoulder
            r *= 1 + a.rng.uniform(-rough, rough)
            o = r * (math.cos(th) * n + math.sin(th) * b)
            if hn is not None and squash != 1.0:
                o -= hn * o.dot(hn) * (1 - squash)
            ring.append(a.bm.verts.new(pts[i] + o))
        rings.append(ring)
    body = []
    for i in range(len(rings) - 1):
        r1, r2 = rings[i], rings[i + 1]
        ax = (pts[i] + pts[i + 1]) / 2
        for j in range(sides):
            k = (j + 1) % sides
            f = mk_face(a, (r1[j], r1[k], r2[k], r2[j]), out_from=ax)
            if f is not None:
                body.append(f)
    t = 1.0 + a.rng.uniform(-a.tint_var, a.tint_var)
    paint(a, body, mat, t, 0.04, fam=fam)
    for end, kind in ((0, caps[0]), (1, caps[1])):
        if not kind:
            continue
        ring = rings[0] if end == 0 else rings[-1]
        c = pts[0] if end == 0 else pts[-1]
        d = -fr[0][0] if end == 0 else fr[-1][0]
        if kind == "cut":
            cut_end(a, ring, c, d, radii[0] if end == 0 else radii[-1], deep=hollow, rim=rim)
        else:
            f = mk_face(a, ring, out_dir=d)
            if f:
                paint(a, [f], mat, t, 0.0, fam=fam)
    return rings


def cut_end(a, ring, c, d, r, rim=0.82, deep=None, wall_mat="w04_bark"):
    """Sawn/broken end: pale w04_wood_end rim around a deep recessed hollow, lined
    with the same heartwood key (the hollow reads dark through shadow alone).
    `deep` is the hollow depth in studs (default ~3 r); the mouth is narrow (rim 0.56). The well is slightly
    undercut (it widens below the opening), so its walls face a little away
    from the sky and the rim shades them and the floor: the dark comes from
    depth, not from a dark colour."""
    c, d = Vector(c), Vector(d).normalized()
    deep = 3.0 * r if deep is None else deep
    bm = a.bm
    inner = [bm.verts.new(c + (v.co - c) * rim + d * 0.03 * r) for v in ring]
    hole = [bm.verts.new(c + (v.co - c) * rim * 1.15 - d * deep) for v in ring]
    n = len(ring)
    rimf, wall = [], []
    for j in range(n):
        k = (j + 1) % n
        f = mk_face(a, (ring[j], ring[k], inner[k], inner[j]), out_dir=d)
        f and rimf.append(f)
        f = mk_face(a, (inner[j], inner[k], hole[k], hole[j]), out_dir=None)
        if f:
            # walls face the axis (and the opening)
            ctr = f.calc_center_median()
            axis_pt = c + d * (ctr - c).dot(d)
            if f.normal.dot(axis_pt - ctr) < 0:
                f.normal_flip()
            wall.append(f)
    f = mk_face(a, hole, out_dir=d)
    f and wall.append(f)
    # thin pale heartwood rim; the well is lined with the darker decayed bark key
    # so the deep, undercut hollow reads as a dark hole, not a pale ring
    paint(a, rimf, "w04_wood_end", 1.0, 0.05)
    paint(a, wall, wall_mat, 1.0, 0.03, fam=F_BARK)


def broken_top(a, ring, c, r, rng, spikes=((0, 3.2), (5, 2.2), (9, 1.6))):
    """Snapped trunk top: jagged splinters (bark outside, pale heartwood inside)
    around a deep recessed hollow lined with heartwood. spikes = (ring index,
    height) of the tall splinters."""
    bm = a.bm
    c = Vector(c)
    n = len(ring)
    hs = [rng.uniform(0.3, 0.9) for _ in range(n)]
    for j0, hgt in spikes:
        hs[j0 % n] = hgt
        hs[(j0 + 1) % n] = max(hs[(j0 + 1) % n], hgt * 0.55)
        hs[(j0 - 1) % n] = max(hs[(j0 - 1) % n], hgt * 0.3)
    top, band, inner, mid, hole = [], [], [], [], []
    for j, v in enumerate(ring):
        o = v.co - c
        o.z = 0
        taper = 0.95 - 0.12 * min(hs[j] / 5.0, 1.0)
        top.append(bm.verts.new(c + o * taper + Z * hs[j]))
        band.append(bm.verts.new(c + o * 0.97 + Z * min(hs[j], 0.7)))
        # thin shell: a wide hollow, deep enough that its floor sits in shadow
        inner.append(bm.verts.new(c + o * 0.84 + Z * (hs[j] * 0.8 - 0.15)))
        mid.append(bm.verts.new(c + o * 0.8 - Z * 1.0))
        hole.append(bm.verts.new(c + o * 0.62 - Z * 3.2))
    bark, rim, shard, char = [], [], [], []
    for j in range(n):
        k = (j + 1) % n
        oc = c + Z * 0.25 * (hs[j] + hs[k])
        f = mk_face(a, (ring[j], ring[k], band[k], band[j]), out_from=oc)
        f and bark.append(f)
        # tall splinters lose their bark: pale heartwood shards above the band
        f = mk_face(a, (band[j], band[k], top[k], top[j]), out_from=oc)
        if f:
            (shard if hs[j] + hs[k] > 2.4 else bark).append(f)
        f = mk_face(a, (top[j], top[k], inner[k], inner[j]), out_dir=Z)
        f and rim.append(f)
        f = mk_face(a, (inner[j], inner[k], mid[k], mid[j]), out_from=None)
        if f:
            ctr = f.calc_center_median()
            if f.normal.dot(Vector((c.x, c.y, ctr.z)) - ctr) < 0:
                f.normal_flip()
            shard.append(f)
        f = mk_face(a, (mid[j], mid[k], hole[k], hole[j]))
        if f:
            ctr = f.calc_center_median()
            if f.normal.dot(Vector((c.x, c.y, ctr.z)) - ctr) < 0:
                f.normal_flip()
            char.append(f)
    f = mk_face(a, hole, out_dir=Z)
    f and char.append(f)
    paint(a, bark, "w04_bark", 1.0, 0.04, fam=F_BARK)
    paint(a, rim + shard + char, "w04_wood_end", 1.0, 0.05)


PER = 6  # trunk vertices per lobe: groove, shoulder, 3 lobe tops, shoulder
# spiral twist in radians per stud: the grooves lean ~25-30 deg on a 3.5-4
# stud radius, a strong spiral that still reads as one solid fluted cone.
TWIST = 0.14


def trunk(a, pts, radii, flare=(0.5, 0.32, 0.18, 0.08, 0.02), lobes=6, per=PER, depth=0.42, twist=TWIST,
          caps=(None, "flat")):
    """Fluted trunk: 6 broad round lobes split by narrow, deep V grooves (only
    the groove vertex is pulled in far; its shoulders a little), so the
    grooves read as crisp dark lines on one solid cone instead of splitting the
    trunk into separate stems; twist in radians per stud."""
    return tube(a, pts, radii, sides=lobes * per, lobes=lobes, depth=depth, twist=twist,
                flare=flare, rough=0.03, caps=caps, shoulder=0.22)


def leader(a, pts, r0, r1, cap="flat", sides=16, lobes=4, twist=0.05, hollow=None):
    n = len(pts)
    rad = [r0 + (r1 - r0) * i / (n - 1) for i in range(n)]
    return tube(a, pts, rad, sides=sides, lobes=lobes, depth=0.28, twist=twist, rough=0.035,
                caps=(None, cap), hollow=hollow)


def polyline(pts, per_seg=(2, 2)):
    """Points along straight segments p0-p1-p2... (each split into per_seg[i]
    pieces): a limb with sharp elbows instead of a smooth curve."""
    pts = [Vector(p) for p in pts]
    out = [pts[0]]
    for i in range(len(pts) - 1):
        k = per_seg[i] if i < len(per_seg) else 2
        for s in range(1, k + 1):
            out.append(pts[i].lerp(pts[i + 1], s / k))
    return out


def column(z0, z1, step=1.1, sway=(0.0, 0.0), lean=(0.0, 0.0)):
    """Trunk axis points evenly spaced (~step studs) from z0 to z1, with a gentle
    sway (amplitude x, y) and lean (offset per stud x, y)."""
    n = max(2, round((z1 - z0) / step) + 1)
    out = []
    for i in range(n):
        z = z0 + (z1 - z0) * i / (n - 1)
        out.append((sway[0] * math.sin(z * 0.24) + lean[0] * z, sway[1] * math.sin(z * 0.3) + lean[1] * z, z))
    return out


def cone(r0, r1, n, power=1.4):
    """Radii tapering from r0 to r1 over n rings, faster near the base (a cone
    that swells into the root flare)."""
    return [r1 + (r0 - r1) * (1 - i / (n - 1)) ** power for i in range(n)]


def branch(a, p0, p1, p2, r0=0.85, r1=0.45, cap="flat", sides=7):
    """Bonsai limb with a sharp elbow at p1: out from the trunk, then up into
    its pad."""
    pts = polyline((p0, p1, p2), (2, 2))
    n = len(pts)
    rad = [r0 + (r1 - r0) * i / (n - 1) for i in range(n)]
    return tube(a, pts, rad, sides=sides, rough=0.05, caps=(None, cap))


def twigs(a, base, x, y, zb, R, H, r, rng, n=3):
    """2-3 short twigs forking from a limb up into the underside of its pad."""
    base = Vector(base)
    az0 = rng.uniform(0, TAU)
    for k in range(n):
        az = az0 + TAU * k / n + rng.uniform(-0.3, 0.3)
        tip = Vector((x + math.cos(az) * R * 0.5, y + math.sin(az) * R * 0.5, zb + H * 0.12))
        mid = base.lerp(tip, 0.5) + Vector((0, 0, -0.25))
        tube(a, bezier(base, mid, tip, 3), [r * 0.7, r * 0.55, r * 0.42], sides=5, rough=0.05,
             caps=(None, "flat"))


def stub(a, base, d, length, r, rim=0.82, deep=3.0):
    """Broken branch stub with a hollow cut end (pale rim, deep recessed well).
    `base` sits inside the trunk; the stub flares where it leaves the bark."""
    base, d = Vector(base), Vector(d).normalized()
    pts = [base, base + d * length * 0.45, base + d * length * 0.75, base + d * length]
    return tube(a, pts, [r * 1.45, r * 1.2, r * 1.05, r], sides=10, rough=0.04, caps=(None, "cut"),
                hollow=r * deep, rim=rim)


def lobe_azimuths(ring, centre, per=PER):
    """Azimuths of the mid-lobe vertices of a fluted trunk's base ring."""
    c = Vector(centre)
    return [math.atan2(v.co.y - c.y, v.co.x - c.x) for v in ring[per // 2::per]]


def roots(a, base, R, n, reach, rng, h0=3.4, r0=1.35, phase=0.0, sides=8, azs=None, twist=0.0):
    """Buttress roots: fins arcing from the lower trunk into the soil. With `azs`
    (the trunk's lobe azimuths) each root continues one twisted lobe, so the
    spiral ribs run on down into the roots instead of crossing them."""
    base = Vector(base)
    if azs:
        n = len(azs)
    for k in range(n):
        if azs:
            az = azs[k] + rng.uniform(-0.08, 0.08)
        else:
            az = phase + TAU * k / n + rng.uniform(-0.22, 0.22)
        rk = reach * rng.uniform(0.82, 1.08)
        hk = h0 * rng.uniform(0.9, 1.05)
        # the fin hugs the trunk surface high up, then swells out low and runs
        # into the soil: a buttress that flows out of the trunk, not a strut
        top = base + polar(R * 0.62, az + twist * hk, hk)
        mid = base + polar(R * 1.0, az + twist * hk * 0.18, h0 * 0.18)
        end = base + polar(rk, az, -0.5)
        pts = bezier(top, mid, end, 6)
        rr = r0 * rng.uniform(0.9, 1.1)
        rad = [rr * 0.85, rr, rr * 0.88, rr * 0.66, rr * 0.44, rr * 0.22]
        tube(a, pts, rad, sides=sides, squash=0.62, rough=0.05, caps=(None, "flat"))


# ---------------------------------------------------------------------------
# Needles: flat star rosettes and cloud pads
# ---------------------------------------------------------------------------


def star(a, c, R, h, n=7, notch=0.7, droop=0.3, az=0.0, tilt=0.0, spin=None, fam=F_NEEDLE, mat="w04_needle",
         nocollide=False):
    """Flat star rosette: n broad pointed leaves round a low peak (h/R ~0.35).
    Each leaf is a kite folded along its midrib (tip, two notches, a midrib
    point at 0.5 R and the peak), so its two halves catch the sun differently;
    the tips droop below the base so the flat, down-facing underside fan shows
    as a dark band from the side. The lit/shadow star pattern is geometry,
    never paint. 6n tris. `tilt` leans the star outward along azimuth `az`."""
    rng = a.rng
    spin = rng.uniform(0, TAU) if spin is None else spin
    M = (Matrix.Translation(Vector(c)) @ Matrix.Rotation(az, 4, "Z") @ Matrix.Rotation(tilt, 4, "Y")
         @ Matrix.Rotation(spin, 4, "Z"))
    up = M.to_3x3() @ Vector((0, 0, 1))
    bm = a.bm

    def P(r, th, z):
        return bm.verts.new(M @ Vector((r * math.cos(th), r * math.sin(th), z)))

    T, N, Mid = [], [], []
    for k in range(n):
        th = TAU * k / n + rng.uniform(-0.06, 0.06)
        T.append(P(R * rng.uniform(0.93, 1.06), th, -droop * h * rng.uniform(0.7, 1.25)))
        # midrib high, notches low: each leaf is a steep V fold, so its two
        # halves face the sun and the shade differently (lime / dark halves)
        Mid.append(P(R * rng.uniform(0.47, 0.53), th, h * rng.uniform(0.8, 0.9)))
        N.append(P(R * rng.uniform(notch - 0.04, notch + 0.04), th + TAU / (2 * n), -0.15 * h))
    peak = P(R * rng.uniform(0.0, 0.06), rng.uniform(0, TAU), h)
    bot = P(0.0, 0.0, -0.05 * h)
    pc = M @ Vector((0, 0, -0.6 * h))
    faces = []
    for k in range(n):
        nb, na, t, m = N[k - 1], N[k], T[k], Mid[k]
        for tri in ((nb, t, m), (t, na, m), (nb, m, peak), (m, na, peak)):
            f = mk_face(a, tri, out_from=pc)
            f and faces.append(f)
        for tri in ((bot, nb, t), (bot, t, na)):
            f = mk_face(a, tri, out_dir=-up)
            f and faces.append(f)
    paint(a, faces, mat, 1.0, 0.04, fam=fam, nocollide=nocollide)
    return faces


def pad_height(R):
    return 0.9 * R


def pad(a, x, y, zb, R, ring=7, n=None, facets=1):
    """Flat cloud pad ~2R wide and ~0.9 R tall with its flat underside at zb:
    the shared Asset.canopy crown helper filled with `ring` lumpy star-shaped
    leaf clusters (the reference's chunky cauliflower star clumps), one
    w04_needle key; the dark underside is shading from the flat floor."""
    # crisp star rosette pad: one big flat 7-lobed star clump (flat floor at zb)
    # topped by a smaller turned star and two rim satellites, so it reads as a
    # big faceted star cloud, not a cauliflower of many small lumps
    rng = a.rng
    az0 = rng.uniform(0, TAU)
    parts = [(R, 0.0, 0.0, 0.42 * R, 7, 0.78, 2)]
    parts.append((0.62 * R, 0.1 * R * math.cos(az0), 0.1 * R * math.sin(az0), 0.92 * R, 6, 0.8, 1))
    for k in range(3):
        az = az0 + 1.0 + k * TAU / 3
        parts.append((0.5 * R, 0.5 * R * math.cos(az), 0.5 * R * math.sin(az), 0.5 * R, 6, 0.75, 1))
    for r, ox, oy, z, lobes, sq, fc in parts:
        a.leaf_cluster(r, (x + ox, y + oy, zb + z), mat="w04_needle", lobes=lobes, squash=sq,
                       facets=fc, floor=zb, depth=1.15, seed=rng.randint(0, 99999))


def bush(a, x, y, s, rng):
    """Leafy fern/bush clump at the tree base (~1.6 s tall): two stacked shared
    leaf_cluster clumps in the needle green. Walk-through: kit_nocollide."""
    for (ox, oy, z, r) in ((0, 0, 0.55 * s, 1.0 * s), (rng.uniform(-0.3, 0.3) * s, rng.uniform(-0.3, 0.3) * s, 1.1 * s, 0.7 * s)):
        v = a.leaf_cluster(r, (x + ox, y + oy, z), mat="w04_needle", lobes=6, squash=0.85, floor=0.0,
                           seed=rng.randint(0, 99999))
        paint(a, a_faces(v), "w04_needle", 1.0, 0.03, fam=F_NEEDLE, nocollide=True)


def a_faces(verts):
    fs = set()
    for v in verts:
        fs.update(v.link_faces)
    return list(fs)


# ---------------------------------------------------------------------------
# Base dressing: soil patch, rocks, grass, leafy bushes
# ---------------------------------------------------------------------------


def soil(a, R, rng, cx=0.0, cy=0.0, n=20, th=0.12, sy=1.0):
    bm = a.bm
    ph = rng.uniform(0, TAU)
    pts = []
    for k in range(n):
        az = ph + TAU * k / n
        rr = R * rng.uniform(0.82, 1.06) * (1 + 0.08 * math.sin(3 * az + ph))
        pts.append((cx + rr * math.cos(az), cy + rr * math.sin(az) * sy))
    top = [bm.verts.new((x, y, th)) for x, y in pts]
    bot = [bm.verts.new((cx + (x - cx) * 1.02, cy + (y - cy) * 1.02, 0.0)) for x, y in pts]
    faces = [mk_face(a, top, out_dir=Z)]
    for k in range(n):
        j = (k + 1) % n
        faces.append(mk_face(a, (bot[k], bot[j], top[j], top[k]), out_from=(cx, cy, 0)))
    paint(a, [f for f in faces if f], "w04_ground", 1.0, 0.0)


def rock(a, x, y, size, rng):
    s = (size * rng.uniform(1.1, 1.3), size * rng.uniform(0.85, 1.0), size * rng.uniform(0.7, 0.85))
    verts = a.rock(s, (x, y, 0), rot=(0, 0, rng.uniform(0, TAU)), mat="kit_rock", subdiv=1,
                   rough=0.1, facets=6, sink=0.08)
    # pale grey stones: one rock key, small random tint per rock
    paint(a, a_faces(verts), "kit_rock", rng.uniform(0.97, 1.03), 0.04, fam=F_ROCK)


def grass(a, x, y, s, rng):
    """Spiky grass tuft: 9-12 three-sided blades fanning out (3 tris each), all
    w04_grass (the olive tips in the reference are lit grass)."""
    n = rng.randint(9, 12)
    az0 = rng.uniform(0, TAU)
    for i in range(n):
        az = az0 + TAU * i / n + rng.uniform(-0.3, 0.3)
        lean = rng.uniform(0.2, 0.65)
        L = s * rng.uniform(0.6, 1.15)
        d = Vector((math.cos(az) * math.sin(lean), math.sin(az) * math.sin(lean), math.cos(lean)))
        base = (x + math.cos(az) * 0.15 * s, y + math.sin(az) * 0.15 * s, 0.0)
        verts = a.cyl(s * 0.16, 0.0, L, 3, loc=base, rot=d.to_track_quat("Z", "Y").to_euler(),
                      mat="w04_grass", cap=False)
        paint(a, a_faces(verts), "w04_grass", rng.uniform(0.97, 1.03), 0.04, fam=F_GRASS, nocollide=True)


# ---------------------------------------------------------------------------
# Finishing
# ---------------------------------------------------------------------------


def finish(kit, a, role, collision, budget, notes):
    used = sorted({f.material_index for f in a.bm.faces})
    remap = {old: new for new, old in enumerate(used)}
    for f in a.bm.faces:
        f.material_index = remap[f.material_index]
    a.mats = [a.mats[i] for i in used]
    a.bm.faces.layers.int.remove(a.bm.faces.layers.int["fam"])
    for v in a.bm.verts:
        if v.co.z < 0.0:
            v.co.z = 0.0
    obj = a.finish()
    return kit.tag(obj, role, collision=collision, budget=budget, notes=notes)


# ---------------------------------------------------------------------------
# Tree assembly from a spec
# ---------------------------------------------------------------------------


def base_dressing(a, rng, spec, centre=(0.0, 0.0)):
    """Soil patch plus rocks, grass and leafy bushes round the roots: each entry
    is (azimuth in degrees, distance from the trunk, size). Front (-Y) is -90,
    left (-X) 180, right (+X) 0."""
    sc = spec.get("soil_c", centre)
    soil(a, spec.get("soil", 9.0), rng, cx=sc[0], cy=sc[1], sy=spec.get("soil_sy", 0.92))

    def at(deg, r):
        az = math.radians(deg)
        return centre[0] + r * math.cos(az), centre[1] + r * math.sin(az)

    for u, r, s in spec.get("rocks", ()):
        rock(a, *at(u, r), s, rng)
    for u, r, s in spec.get("grass", ()):
        grass(a, *at(u, r), s, rng)
    for u, r, s in spec.get("bushes", ()):
        bush(a, *at(u, r), s, rng)


def tree(kit, name, seed, spec, broken=False):
    """Trunk (flat or snapped top), roots, leaders, branches, stubs, pads, dressing.
    Pads are (x, y, floor z, R): flat star pads ~2R wide, ~0.78 R tall."""
    a = new_asset(kit, name, seed)
    rng = random.Random(seed)
    tp = [Vector(p) for p in spec["trunk"]]
    rings = trunk(a, tp, spec["radii"], flare=spec.get("flare", (0.6, 0.4, 0.24, 0.12, 0.05)),
                  twist=spec.get("twist", TWIST), caps=(None, None if broken else "flat"))
    if broken:
        broken_top(a, rings[-1], tp[-1], spec["radii"][-1], rng, spikes=spec["spikes"])
    roots(a, tp[0], spec["radii"][0], 6, spec.get("reach", 8.0), rng, h0=spec.get("root_h", 4.6),
          r0=spec.get("root_r", 2.6), azs=lobe_azimuths(rings[0], tp[0]), twist=spec.get("twist", TWIST))
    ends = []
    for p0, p1, p2, r0, r1, cap in spec.get("leaders", ()):
        leader(a, bezier(p0, p1, p2, 7), r0, r1, cap=cap)
        ends.append((Vector(p1), Vector(p2), r1))
    for p0, p1, p2, r0, r1 in spec.get("branches", ()):
        branch(a, p0, p1, p2, r0, r1)
        ends.append((Vector(p1), Vector(p2), r1))
    for st in spec.get("stubs", ()):
        stub(a, *st)
    k = spec.get("pad_k", 1.0)
    pads = [(x, y, zb, R * k, pad_height(R * k)) for x, y, zb, R in spec.get("pads", ())]
    for x, y, zb, R, H in pads:
        pad(a, x, y, zb, R, ring=spec.get("pad_n", 7))
    for p1, p2, r1 in ends:  # bonsai twigs fanning out under the pad each limb carries
        if not pads:
            break
        x, y, zb, R, H = min(pads, key=lambda p: (Vector(p[:2]) - p2.xy).length + abs(p[2] - p2.z))
        if (Vector((x, y)) - p2.xy).length > R:
            continue
        twigs(a, p2 - (p2 - p1).normalized() * 1.4, x, y, zb, R, H, r1, rng, n=2)
    base_dressing(a, rng, spec, centre=(tp[0].x, tp[0].y))
    return a


# ---------------------------------------------------------------------------
# Specs (studs; front = -Y). Dressing entries are (azimuth deg, distance,
# size): front -90, left 180, right 0.
# ---------------------------------------------------------------------------


def resample(pts, step=1.1):
    """Re-space a trunk polyline into rings ~step studs apart (even twist)."""
    pts = [Vector(p) for p in pts]
    seg = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    total = sum(seg)
    n = max(2, round(total / step) + 1)
    out, i, acc = [], 0, 0.0
    for k in range(n):
        s = total * k / (n - 1)
        while i < len(seg) - 1 and acc + seg[i] < s:
            acc += seg[i]
            i += 1
        t = min(1.0, (s - acc) / seg[i]) if seg[i] else 0.0
        out.append(pts[i].lerp(pts[i + 1], t))
    return out


def hero_spec():
    # slender sinuous trunk (~1/4-1/3 of the crown width at mid height) rising
    # to a high fork at ~14, flaring into buttress roots
    pts = column(0, 14.0, 1.1, sway=(1.0, 0.3))
    s = dict(trunk=pts, radii=cone(4.4, 2.1, len(pts), power=1.6), flare=(0.65, 0.42, 0.24, 0.1, 0.03),
             reach=8.8, root_h=4.4, root_r=2.4, pad_k=1.0)
    # big star pads (each ~6.5-8 wide) sprawled 7-9 studs out on long elbowed
    # limbs: a large crown pad on top, upper-left and upper-right pads, low
    # left and low right pads, and one at the back.
    ring = {"UL": (150, 8.5, 17.4, 3.6), "L": (-150, 8.6, 11.6, 3.7), "UR": (20, 8.5, 16.8, 3.6),
            "R": (-55, 8.6, 10.0, 3.6), "B": (100, 8.5, 14.4, 3.3)}
    P = {k: (r * math.cos(math.radians(d)), r * math.sin(math.radians(d)), z, R) for k, (d, r, z, R) in ring.items()}
    P["T"] = (0.5, 0.5, 20.6, 4.3)

    def end(k, dz=0.3):
        x, y, z, _ = P[k]
        return (x, y, z + dz)

    s["leaders"] = [
        ((-0.2, 0.2, 13.2), (1.0, 0.4, 18.0), end("T"), 1.7, 0.9, "flat"),     # central leader to the crown
        ((-1.0, 0.3, 13.2), (-3.4, 2.0, 15.0), end("UL"), 1.4, 0.7, "flat"),   # fork: left leader
    ]
    s["branches"] = [
        ((-2.0, -0.5, 8.8), (-5.0, -2.6, 9.4), end("L"), 1.1, 0.55),       # left, low, elbowed
        ((2.0, -0.6, 7.4), (3.6, -3.6, 8.2), end("R"), 1.1, 0.55),         # right, low, elbowed
        ((0.8, 0.4, 16.0), (4.6, 1.6, 16.2), end("UR"), 0.95, 0.5),        # off the central leader
        ((0.2, 1.6, 11.6), (-0.4, 4.8, 12.4), end("B"), 0.9, 0.5),          # back
    ]
    s["pads"] = [P[k] for k in ("T", "UL", "UR", "L", "R", "B")]
    # one small knot hole on the front: thin pale rim, deep dark bark-lined well
    s["stubs"] = [((-0.9, -1.6, 6.2), (-0.3, -1.0, -0.3), 1.9, 0.8, 0.9, 5.0)]
    s.update(soil=9.0, soil_sy=0.95,
             rocks=[(-112, 8.0, 3.4), (-62, 8.6, 2.4), (-160, 8.2, 2.2), (-22, 8.4, 2.2), (150, 7.6, 1.8),
                    (40, 8.0, 1.6)],
             grass=[(-90, 8.8, 1.7), (-138, 8.6, 1.6), (-40, 8.8, 1.6), (0, 8.2, 1.6), (120, 8.0, 1.5),
                    (70, 8.2, 1.5), (-178, 8.0, 1.5), (175, 8.6, 1.4), (-75, 7.2, 1.4), (30, 7.6, 1.4)],
             bushes=[(-132, 6.8, 2.0), (-92, 7.2, 1.6), (-28, 7.2, 1.6), (165, 7.0, 1.7)])
    return s


def split_spec():
    pts = column(0, 7.0, 1.1)
    s = dict(trunk=pts, radii=cone(4.8, 3.3, len(pts), power=1.5), flare=(0.62, 0.4, 0.2, 0.07),
             reach=8.8, root_h=4.6, root_r=2.5, pad_k=1.1)
    s["leaders"] = [
        ((-1.3, 0, 6.4), (-2.2, -0.2, 11.0), (-4.0, 0.2, 17.0), 2.1, 1.2, "flat"),
        ((1.3, 0, 6.4), (2.1, 0.0, 11.0), (2.5, -0.2, 16.4), 2.2, 1.5, "cut"),   # broken top, hollow
    ]
    s["branches"] = [
        ((-2.0, 0, 9.0), (-5.0, -0.3, 9.8), (-7.0, -0.5, 11.8), 1.1, 0.6),
        ((-2.4, 0.2, 12.4), (-2.8, 3.2, 12.8), (-2.6, 5.0, 14.2), 0.85, 0.5),
        ((2.3, 0, 13.6), (4.8, 0.2, 14.6), (5.6, 0.5, 17.2), 0.95, 0.5),
        ((2.1, 0.2, 10.0), (3.8, 3.0, 10.6), (4.6, 5.0, 12.6), 0.9, 0.5),
    ]
    s["pads"] = [(-4.0, 0.2, 16.8, 3.6), (-7.0, -0.5, 11.6, 3.3), (-2.6, 5.0, 14.0, 3.0),
                 (5.6, 0.5, 17.0, 3.4), (4.6, 5.0, 12.4, 3.0)]
    s["stubs"] = [((-1.9, -2.3, 3.4), (-0.5, -0.75, 0.45), 2.6, 0.95)]
    s.update(soil=8.8,
             rocks=[(-105, 7.0, 2.8), (-45, 7.0, 1.9), (-160, 6.8, 1.7), (40, 7.0, 1.5)],
             grass=[(-80, 8.0, 1.5), (-60, 8.2, 1.4), (-150, 7.8, 1.4), (150, 7.2, 1.3), (60, 7.4, 1.3),
                    (-125, 8.2, 1.3), (10, 7.8, 1.3)],
             bushes=[(-20, 6.2, 1.5), (-135, 6.4, 1.3), (100, 6.0, 1.2)])
    return s


def bent_spec():
    zs = [0, 0.6, 1.6, 3.2, 5.2, 7.4, 9.4, 11.2, 12.8, 14.0]
    xs = [2.8, 2.8, 2.6, 1.8, 0.3, -1.0, -1.4, -0.7, 0.5, 1.4]
    pts = resample([(x, 0.0, z) for x, z in zip(xs, zs)], 1.1)
    s = dict(trunk=pts, radii=cone(4.2, 2.2, len(pts), power=1.4), flare=(0.62, 0.38, 0.18, 0.06),
             reach=8.4, root_h=4.4, root_r=2.4, pad_k=1.0)
    # three clearly separate pads with gaps between them, each on a visible
    # elbowed limb (plus a small back pad)
    s["branches"] = [
        ((-1.4, 0, 9.4), (-5.4, -0.3, 9.6), (-9.4, -0.4, 11.4), 1.15, 0.6),   # long near-horizontal, left
        ((0.6, 0, 11.6), (5.0, 0.2, 11.4), (9.6, 0.4, 13.0), 1.0, 0.55),      # right, elbowed
        ((-1.0, 0.3, 10.6), (-1.6, 2.8, 11.2), (-2.0, 5.0, 12.6), 0.8, 0.45),  # back
    ]
    s["pads"] = [(1.4, 0.0, 14.2, 3.5), (-9.4, -0.4, 11.2, 3.2), (9.6, 0.4, 12.8, 3.1), (-2.0, 5.0, 12.4, 2.6)]
    s["stubs"] = [((1.0, -2.3, 6.0), (-0.4, -0.9, 0.4), 2.6, 0.9)]
    s.update(soil=8.8, soil_c=(1.2, 0.0),
             rocks=[(-100, 6.6, 2.6), (-50, 6.8, 1.8), (-150, 6.4, 1.6)],
             grass=[(-80, 7.4, 1.5), (-60, 7.6, 1.4), (-130, 7.2, 1.4), (30, 6.8, 1.3), (100, 6.6, 1.3),
                    (-170, 7.0, 1.3)],
             bushes=[(-20, 5.8, 1.4), (160, 5.6, 1.2)])
    return s


def broken_spec():
    pts = column(0, 18.6, 1.1, sway=(0.25, 0.15))
    s = dict(trunk=pts, radii=cone(4.8, 3.3, len(pts), power=1.5), flare=(0.62, 0.4, 0.2, 0.07),
             reach=8.8, root_h=4.8, root_r=2.4, pad_k=1.1,
             spikes=((0, 5.2), (6, 3.0), (11, 4.4), (17, 2.2), (23, 3.4), (29, 2.6)))
    s["branches"] = [
        ((1.8, 0, 14.4), (4.4, 0.0, 15.2), (6.4, 0.3, 17.6), 1.0, 0.55),     # upper right
        ((2.2, 0, 9.4), (4.6, -0.2, 10.0), (6.2, -0.4, 12.0), 1.0, 0.55),    # mid right
        ((-2.2, 0, 7.6), (-4.6, -0.2, 8.2), (-6.4, -0.2, 10.0), 1.0, 0.55),  # left low
    ]
    s["pads"] = [(6.4, 0.3, 17.4, 3.1), (6.2, -0.4, 11.8, 3.0), (-6.4, -0.2, 9.8, 3.0)]
    s["stubs"] = [((-2.8, -1.4, 14.6), (-0.9, -0.5, 0.4), 2.4, 0.85)]
    s.update(soil=8.4,
             rocks=[(-110, 6.8, 2.6), (-50, 6.4, 1.7), (160, 6.4, 1.6)],
             grass=[(-80, 7.4, 1.4), (-60, 7.8, 1.4), (-160, 7.4, 1.4), (100, 7.0, 1.3), (60, 7.2, 1.3),
                    (-130, 7.8, 1.3)],
             bushes=[(-20, 6.0, 1.4), (-140, 6.2, 1.2), (30, 5.8, 1.2)])
    return s


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------


HULL_NOTE = (" Hull collision (convex, trunk + crown); the exporter has no per-face hull filter, so the pads are "
             "inside the hull. Grass and leafy-bush faces carry kit_nocollide = 1. No VFX (no fire, water or "
             "harvest). One colour per material, every Tint 1.0 +/- a few percent.")


def build_hero(kit):
    a = tree(kit, "OldPine", 4401, hero_spec())
    return finish(kit, a, "hero", "hull", 8000,
                  "Ancient umbrella pine: slender sinuous 6-lobed fluted trunk with spiral V grooves and buttress roots, "
                  "forking at ~14 studs, long elbowed limbs to six big star cloud pads 7-9 studs out "
                  "(flat undersides), a small dark knot hole, boulders, grass, leafy "
                  "bushes on an ~18-stud sandy patch." + HULL_NOTE)


def build_canopy_tier(kit):
    a = new_asset(kit, "OldPineCanopyTier", 4410)
    pad(a, 0, 0, 0, 3.6)
    return finish(kit, a, "part", "hull", 1500,
                  "One flat star cloud pad (~6 x 6 x 2.4): a big flat 7-leaf star with a flat down-facing underside, "
                  "a ring of five outward-tilted star clumps, an upper star and a raised centre star; one needle "
                  "colour (the dark underside is shading).")


def build_branch(kit):
    a = new_asset(kit, "OldPineBranchAngled", 4420)
    # turned so the low hollow end faces the front-left (toward the viewer, as drawn)
    yaw = Matrix.Rotation(math.radians(32), 3, "Z")
    pts = [yaw @ p for p in polyline(((-4.6, 0, 1.3), (0.5, 0.0, 1.45), (3.6, 0.1, 4.6)), (3, 2))]
    n = len(pts)
    rad = [1.3 - 0.28 * i / (n - 1) for i in range(n)]
    tube(a, pts, rad, sides=10, rough=0.04, caps=("cut", "cut"), hollow=2.2)
    tw = [yaw @ Vector(p) for p in ((-0.8, 0.05, 1.6), (-0.7, -0.7, 2.3), (-0.6, -1.0, 2.7))]
    tube(a, tw, [0.4, 0.33, 0.28], sides=6, caps=(None, "flat"))
    return finish(kit, a, "part", "hull", 600,
                  "Bent branch log (~7.5 long, ~2 dia) with a sharp elbow (~45 deg), a knob and hollow cut ends "
                  "(pale heartwood rim round a narrow, 1.8 deep recessed hollow); lies at an angle.")


def build_forked_trunk(kit):
    a = new_asset(kit, "OldPineForkedTrunk", 4430)
    rng = random.Random(4430)
    pts = column(0, 7.4, 1.1, sway=(0.25, 0.1))
    rings = trunk(a, pts, cone(3.5, 2.9, len(pts), power=1.5), flare=(0.38, 0.24, 0.12, 0.05))
    roots(a, pts[0], 3.5, 6, 4.4, rng, h0=3.4, r0=1.8, azs=lobe_azimuths(rings[0], pts[0]), twist=TWIST)
    # a V: the left leader bends out left then up, the right one rises straight;
    # they start apart (x = -/+1.3 at the fork, a visible crotch between them)
    # and never cross
    leader(a, bezier((-1.3, 0, 6.6), (-3.4, -0.1, 9.0), (-3.6, 0.0, 12.0), 7), 1.75, 1.4, cap="cut", hollow=3.6)
    leader(a, bezier((1.3, 0, 6.6), (1.7, 0.1, 9.6), (1.9, 0.1, 13.0), 7), 1.9, 1.55, cap="cut", hollow=4.0)
    return finish(kit, a, "part", "hull", 3000,
                  "Stocky twisted fluted trunk from the roots to the fork; a V of two leaders, both cut flat with "
                  "pale heartwood rims around narrow, deep recessed hollows. Hull collision.")


def build_roots_base(kit):
    a = new_asset(kit, "OldPineRootsBase", 4440)
    rng = random.Random(4440)
    pts = [(0, 0, 0), (0, 0, 0.8), (0.05, 0, 1.7), (0.1, 0.05, 2.5)]
    rings = tube(a, pts, [3.8, 3.6, 3.4, 3.25], sides=6 * PER, lobes=6, depth=0.42, twist=TWIST,
                 flare=(0.45, 0.3, 0.16, 0.06), rough=0.03, caps=(None, "cut"), hollow=2.4, shoulder=0.22)
    roots(a, pts[0], 3.8, 6, 6.6, rng, h0=2.3, r0=1.9, azs=lobe_azimuths(rings[0], pts[0]), twist=TWIST)
    spec = dict(soil=7.2, soil_sy=0.92,
                rocks=[(-100, 5.8, 2.5), (-140, 6.0, 1.8), (-50, 5.8, 1.9), (160, 5.6, 1.5), (20, 5.6, 1.6)],
                grass=[(-80, 6.6, 1.5), (-30, 6.6, 1.4), (60, 6.0, 1.4), (-170, 5.6, 1.3), (120, 6.2, 1.3)],
                bushes=[(-122, 5.0, 1.2), (8, 5.0, 1.1)])
    base_dressing(a, rng, spec)
    return finish(kit, a, "part", "hull", 2000,
                  "Buttress-root spread cut at ~2.5 studs (pale heartwood cut top around a deep recessed hollow) with "
                  "boulders, grass, leafy bushes and the sandy soil patch." + HULL_NOTE)


def build_split(kit):
    a = tree(kit, "OldPineSplitTrunk", 4450, split_spec())
    return finish(kit, a, "variant", "hull", 8000,
                  "Fat trunk splits low (~6 studs) into a V of two fluted leaders, the right one snapped into a hollow "
                  "cut top; star pads on both; a hollow stub low on the trunk." + HULL_NOTE)


def build_bent(kit):
    a = tree(kit, "OldPineBent", 4460, bent_spec())
    return finish(kit, a, "variant", "hull", 8000,
                  "Thick S-curved trunk, long near-horizontal elbowed branch out to a far pad; lower and wider than "
                  "the hero." + HULL_NOTE)


def build_broken(kit):
    a = tree(kit, "OldPineBrokenCrown", 4470, broken_spec(), broken=True)
    return finish(kit, a, "variant", "hull", 7000,
                  "Tall fat bare trunk snapped near the top: tall jagged pale heartwood splinters around a wide, deep "
                  "recessed hollow; a few small star pads on lower side branches." + HULL_NOTE)


def build(kit):
    return [build_hero(kit), build_canopy_tier(kit), build_branch(kit), build_forked_trunk(kit),
            build_roots_base(kit), build_split(kit), build_bent(kit), build_broken(kit)]
