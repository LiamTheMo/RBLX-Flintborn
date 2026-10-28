"""W04 row 2: Young Fir, a slim spiky fir in three separated tier groups.

Assets
  YoungFir             hero: ~11 x 11 x 17. Crown cone (1 hem), middle group (2 nested hems),
                       lower skirt (2 hems, widest), each group separated by a dark gap; long
                       sharp drooping tips; reddish-orange trunk visible for the lower third;
                       tall leaning grey boulder on the +X side, 2 pebbles, grass tufts, soil.
  YoungFirCrownTier    part: the pointed crown cone with one spiky hem
  YoungFirMiddleTier   part: the middle group (two nested hems)
  YoungFirLowerSkirt   part: the lower skirt (two hems, long drooping tips)
  YoungFirTrunk        part: tapered trunk with a cut top (wood-end ring, sunken wood-end heart)
  YoungFirRootBase     part: flared roots cut flat at ~1.8, pebbles, tufts, soil patch
  YoungFirSparse       variant: 5 small separated tiers on a visible trunk, bare branch stubs
  YoungFirFull         variant: 7 dense overlapping hems, wide skirt, trunk barely visible
  YoungFirLeaning      variant: bowed trunk leaning ~12 degrees, tip ~2.5 studs toward +X

Technique: each hem is a pleated cone (tier()); on the hero the pleats run from near the
axis, a ring of broad folded flaps ending in sharp tips that droop below shallow V notches; the hems of one tree
turn so their tips interleave (a sharp 8-point star from above). Trunk follows build_05.

Colour: ONE palette key per material (sheet W04 palette, shared by all four modules):
w04_needle for every needle face, w04_bark for trunk/roots/branches, w04_wood_end for
cut tops and stub ends, w04_ground for the soil patch, w04_grass for tufts and kit_rock
for the boulder and pebbles. Needles take one uniform per-tree Tint (0.75); otherwise
Tint is only a small random per-face variation (+/-5%), quantised to 0.025 steps.
The reference's lime tops, dark-teal undersides and dark gaps between tier groups are
LIGHTING: each hem has a downward-facing underside cone and each group's upper cone
sits in the shadow of the group above; bark grooves are pulled-in geometry.

Faces of the walk-through base dressing (grass tufts, pebbles, soil patch) carry the
face attribute kit_nocollide = 1, so an exporter can split them off. No VFX: the
sheet shows none and the fir is not harvestable.
"""

import math

from mathutils import Matrix, Vector

SUBJECT = "YoungFir"
ROW = 2
PALETTE = {
    "w04_needle": ("#6A963E", 0.8, 0, 0),  # ALL conifer needles on every W04 tree (skirts, hems, tip flaps, undersides, old-pine cloud pads). One key: the reference's dark-teal underside (#2E5143), mid (#5A8545) and lime lit tops (#93B63F/#B2C63A) are lighting, not paint. Kept equal to the other three W04 modules; each tree sets its needle depth with one uniform Tint. Sapling may push Tint up to ~1.2 for its brighter look; keep Tint variation within one material <= 1.25x.
    "w04_bark": ("#9A6038", 0.9, 0, 0),  # All trunk, root flare, branch and stub bark. Grooves and fluting are GEOMETRY (pulled-in groove vertices, twisted lobes) shaded by the sun, never a darker key.
    "w04_wood_end": ("#E4A458", 0.85, 0, 0),  # Cut heartwood: flat cut tops of trunk parts, cut ends of branch parts, pale rims and splinters of broken stubs/broken crown. Hollows are recessed geometry lined with this key (the dark inside is shadow).
    "w04_ground": ("#DCC9A0", 0.95, 0, 0),  # Thin pale sandy soil patch under each tree base (the cream swatch).
    "w04_grass": ("#8DB83A", 0.9, 0, 0),  # Grass tufts and the leafy fern clumps around the bases (grass class, distinct from needles). Replaces moss/moss_light/moss_dark/w04_olive in tufts; the olive-yellow swatch is the lit grass tip, i.e. lighting.
    # "kit_rock": ("#A89C9C", 0.9, 0, 0),  # Existing KIT_PALETTE key: the pale grey faceted rocks/pebbles at every tree base (one key for all rocks; no kit_rock_light/dark).
}
# kit_rock is used as-is from flintkit.KIT_PALETTE (#A89C9C); the runner only accepts
# w04_-prefixed keys in a module PALETTE, so it is listed above as a comment.

TAU = 2 * math.pi
Z = Vector((0, 0, 1))
CAT = "Kit W04 YoungFir"
# One key per material; Tint is a small random per-face variation only (never by
# face direction, height or tier). The studio light and Roblox shade the facets.
VAR = 0.05
# Tints are quantised to steps of TINT_STEP around 1.0 (no per-key base Tint): a handful
# of levels per colour, so the Roblox exporter's palette rows never overflow.
TINT_STEP = 0.025
# One uniform key-wide Tint for the fir's needles (every needle face alike, never by
# direction or height): the Young Fir is the sheet's darker conifer, as the Sapling is
# its brighter one (the sheet allows a per-tree Tint): #6A963E x 0.75 ~ the sheet's
# deep mid green. Quantised (TINT_STEP), so the needle row holds ~5 palette levels.
BASE_TINT = {"w04_needle": 0.75}


def qtint(t):
    return round(t / TINT_STEP) * TINT_STEP


# ---------------------------------------------------------------------------
# Asset helpers
# ---------------------------------------------------------------------------


def new_asset(kit, name, seed):
    a = kit.flintkit.Asset(name, CAT, seed=seed)
    # layers first: adding a layer later reallocates faces
    a.bm.faces.layers.int.new("kit_nocollide")
    a.dress = False
    return a


def mark(a, faces, mat, tint=1.0, var=VAR):
    """Material + Tint (small random variation per face) + dressing flag."""
    nc_l = a.bm.faces.layers.int["kit_nocollide"]
    mi = a._mi(mat)
    for f in faces:
        if f is None:
            continue
        f.material_index = mi
        t = qtint(BASE_TINT.get(mat, 1.0) * tint * (1 + a.rng.uniform(-var, var)))
        for lp in f.loops:
            lp[a.tint_layer] = (t, t, t, 1.0)
        f.smooth = False
        f[nc_l] = 1 if a.dress else 0
    return faces


def faces_of(verts):
    s = set()
    for v in verts:
        s.update(v.link_faces)
    return list(s)


def face(a, verts):
    out = []
    for v in verts:
        if not out or out[-1] is not v:
            out.append(v)
    if len(out) > 1 and out[0] is out[-1]:
        out.pop()
    if len(out) < 3:
        return None
    try:
        return a.bm.faces.new(out)
    except ValueError:
        return None


def polar(r, az, z=0.0):
    return Vector((r * math.cos(az), r * math.sin(az), z))


def bezier(p0, p1, p2, n):
    p0, p1, p2 = Vector(p0), Vector(p1), Vector(p2)
    return [(1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2
            for t in (i / (n - 1) for i in range(n))]


def smooth01(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def compact_materials(a):
    used = sorted({f.material_index for f in a.bm.faces})
    remap = {old: new for new, old in enumerate(used)}
    for f in a.bm.faces:
        f.material_index = remap[f.material_index]
    a.mats = [a.mats[i] for i in used]


def finish(a):
    compact_materials(a)
    for v in a.bm.verts:
        if v.co.z < 0.0:
            v.co.z = 0.0
    return a.finish()


# ---------------------------------------------------------------------------
# Tiers
# ---------------------------------------------------------------------------


def tier(a, c, zb, apex, R, tips, yaw, droop=0.4, notch=0.6, jag=0.03, alt=1.0,
         wE=0.46, rE=0.76, fold=0.22, s_r=0.34, under=0.05, under_d=None, keel=0.4,
         s_f=0.52, pw=1.7):
    """One hem: a shallow pleated cone (pagoda skirt) whose rim is a ring of BROAD
    flaps, each ending in a long sharp tip that droops below the notches.
    c = (x, y) centre, zb = notch height, apex = cone top, R = tip radius.

    Per flap: a ridge S -> R1 -> T arcing down to the tip, two flanks sloping a little
    away from the ridge (fold) to the flap edges Em / Ep (broad: +/- wE of the tip
    sector at 0.82 R, so neighbouring flaps nearly touch), and a shallow V notch N at
    `notch` R between flaps. A valley line NS -> N runs between the flaps, so the
    cone is pleated: every flap splits into a lit and a shaded half. alt scales the
    odd tips (alt < 1 = alternating long/short points, used for the 4-point crown).
    The underside fans the rim to a centre point `under` h above the notches, so the
    band under each hem faces down and is dark from lighting alone. under_d (studs):
    the bottom hem of a GROUP instead fans to a centre that far BELOW the notches, a
    deep recessed under-cone that meets the trunk; seen through the notches it is the
    dark shadowed gap between the groups. keel (fraction of h): each flap's underside
    folds down to a keel under its ridge, so the flap reads as a chunky wedge with a
    dark underside rather than a thin shard. s_f / pw: the ridges start s_f of the way
    up the hem at s_r R and fall to the tips with exponent pw; the hero uses s_r ~0.1 and
    s_f ~0.9, so the pleats run the full length of the hem from near its apex (the sheet's
    star of long leaf flaps radiating from the axis). All w04_needle."""
    bm = a.bm
    rng = a.rng
    off = Vector((c[0], c[1], 0))
    h = apex - zb
    sec = TAU / tips
    top = bm.verts.new(off + Vector((0, 0, apex)))
    sz = zb + h * s_f
    flaps = []
    for k in range(tips):
        th = yaw + sec * k + rng.uniform(-0.02, 0.02)
        lf = alt if k % 2 else 1.0
        rr = R * lf * (1 + rng.uniform(-jag, jag))
        tz = zb - droop * h * lf * rng.uniform(0.92, 1.08)

        def ridge(rf, rr=rr, tz=tz):
            u = max(0.0, (rf * rr / R - s_r) / (1 - s_r))
            return sz + (tz - sz) * (u ** pw)

        S = bm.verts.new(off + polar(R * s_r, th, sz))
        R1 = bm.verts.new(off + polar(rr * 0.6, th, ridge(0.6)))
        T = bm.verts.new(off + polar(rr, th, tz))
        ez = ridge(rE) - fold * h
        w = wE * sec * (0.85 + 0.15 * lf)
        Em = bm.verts.new(off + polar(rr * rE, th - w, ez))
        Ep = bm.verts.new(off + polar(rr * rE, th + w, ez))
        tn = th + 0.5 * sec
        N = bm.verts.new(off + polar(R * notch, tn, zb + 0.02 * h))
        NS = bm.verts.new(off + polar(R * s_r * 0.85, tn, sz - 0.1 * h))
        K = bm.verts.new(off + polar(rr * 0.66, th, ridge(0.66) - fold * h - keel * h))
        flaps.append((S, R1, T, Em, Ep, N, NS, K))
    cz = zb - under_d if under_d is not None else zb + h * under
    centre = bm.verts.new(off + Vector((0, 0, cz)))
    faces = []
    for k in range(tips):
        S, R1, T, Em, Ep, N, NS, K = flaps[k]
        S2 = flaps[(k + 1) % tips][0]
        Np, NSp = flaps[k - 1][5], flaps[k - 1][6]
        faces += [face(a, (top, S, NS)), face(a, (top, NS, S2)),
                  # right flank (toward the next flap) and the tip
                  face(a, (S, R1, NS)), face(a, (R1, N, NS)), face(a, (R1, Ep, N)),
                  face(a, (R1, T, Ep)),
                  # left flank (toward the previous flap)
                  face(a, (NSp, Np, Em)), face(a, (NSp, Em, R1)), face(a, (NSp, R1, S)),
                  face(a, (Em, T, R1)),
                  # underside (faces down): a keel under each flap, fanned to the centre
                  face(a, (Np, centre, Em)), face(a, (Em, K, T)), face(a, (T, K, Ep)),
                  face(a, (Em, centre, K)), face(a, (K, centre, Ep)),
                  face(a, (Ep, centre, N))]
    mark(a, faces, "w04_needle")


def canopy(a, c_of, tiers, yaw0, droop=0.4, notch=0.68):
    """tiers: (zb, apex, R, tips, droop[, alt[, under_d]]). c_of(z) -> (x, y) centre
    at height z. Tips of consecutive tiers interleave. under_d (studs) marks the bottom
    hem of a group: a deep dark under-cone down to the trunk."""
    yaw = yaw0
    for i, t in enumerate(tiers):
        zb, apex, R, tips, dr = t[:5]
        alt = t[5] if len(t) > 5 else 1.0
        ud = t[6] if len(t) > 6 else None
        tier(a, c_of(zb), zb, apex, R, tips, yaw, droop=dr or droop, notch=notch, alt=alt,
             under_d=ud)
        yaw += TAU / 16   # half of an 8-point sector: successive hems interleave


# ---------------------------------------------------------------------------
# Trunk, roots, branches
# ---------------------------------------------------------------------------


def _frames(pts):
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


def trunk(a, pts, radii, sides=9, flare=(), lobes=4, lobe_amp=0.6, grooves=3,
          groove_depth=0.14, twist=0.12, rough=0.03, caps=(True, True), cut_top=False,
          heart=0.55, sink=0.12):
    """Faceted lobed/grooved trunk tube (build_05 technique), all w04_bark; grooves
    are pulled-in vertex columns (geometry, shaded by the light). cut_top: the top
    cap becomes a w04_wood_end ring around a shallow sunken w04_wood_end heart."""
    bm = a.bm
    rng = a.rng
    pts = [Vector(p) for p in pts]
    frames = _frames(pts)
    phase = rng.uniform(0, TAU)
    rings = []
    for i, (t, nrm, bi) in enumerate(frames):
        f = flare[i] if i < len(flare) else 0.0
        ring = []
        for j in range(sides):
            loc = TAU * j / sides
            th = loc + twist * i
            r = radii[i]
            if f:
                lob = ((1 + math.cos(lobes * (th - phase))) / 2) ** 2
                r *= 1 + f * (0.3 + lobe_amp * lob)
            if grooves:
                g = ((1 + math.cos(grooves * loc)) / 2) ** 6
                r *= 1 - groove_depth * g
            r *= 1 + rng.uniform(-rough, rough)
            ring.append(bm.verts.new(pts[i] + r * (math.cos(th) * nrm + math.sin(th) * bi)))
        rings.append(ring)
    t = 1.0 + rng.uniform(-0.03, 0.03)
    for i in range(len(rings) - 1):
        r1, r2 = rings[i], rings[i + 1]
        for j in range(sides):
            k = (j + 1) % sides
            mark(a, [face(a, (r1[j], r1[k], r2[k], r2[j]))], "w04_bark", t)
    if caps[0]:
        mark(a, [face(a, list(reversed(rings[0])))], "w04_bark", t)
    if caps[1]:
        if cut_top:
            top = rings[-1]
            cen = sum((v.co for v in top), Vector()) / len(top)
            tn = frames[-1][0]
            inner = [bm.verts.new(cen + (v.co - cen) * heart - tn * sink) for v in top]
            for j in range(sides):
                k = (j + 1) % sides
                mark(a, [face(a, (top[j], top[k], inner[k], inner[j]))], "w04_wood_end")
            mark(a, [face(a, inner)], "w04_wood_end")
        else:
            mark(a, [face(a, rings[-1])], "w04_bark", t)
    return rings


def roots(a, base, trunk_r, n, reach, height, r0, bias=None, phase=None):
    """Flared buttress roots arcing from the lower trunk into the ground.
    bias = (azimuth, extra): roots toward that azimuth reach further."""
    base = Vector(base)
    phase = a.rng.uniform(0, TAU) if phase is None else phase
    for k in range(n):
        az = phase + TAU * k / n + a.rng.uniform(-0.2, 0.2)
        rk = reach * a.rng.uniform(0.85, 1.05)
        rr = r0
        if bias:
            w = max(0.0, math.cos(az - bias[0]))
            rk *= 1 + bias[1] * w
            rr *= 1 + 0.35 * bias[1] * w
        top = base + polar(trunk_r * 0.5, az, height * a.rng.uniform(0.85, 1.1))
        mid = base + polar(trunk_r * 1.05, az, height * 0.32)
        end = base + polar(rk, az, -0.12)
        trunk(a, bezier(top, mid, end, 5), [rr, rr * 0.9, rr * 0.72, rr * 0.5, rr * 0.28],
              sides=6, grooves=0, rough=0.05, twist=0.0, caps=(False, True))


def branch(a, p0, p1, r, stub=True):
    """Bare branch from p0 to p1; stubs end in a cut w04_wood_end cap."""
    pts = bezier(p0, (Vector(p0) + Vector(p1)) / 2 + Vector((0, 0, 0.15)), p1, 3)
    trunk(a, pts, [r, r * 0.8, r * 0.6], sides=5, grooves=0, rough=0.04, twist=0.0,
          caps=(False, True), cut_top=stub)


# ---------------------------------------------------------------------------
# Base dressing
# ---------------------------------------------------------------------------


def blade(a, base, az, pitch, L, w, curl):
    """Tapered 3-sided grass blade arching outward (9 tris)."""
    bm = a.bm
    base = Vector(base)
    d0 = Vector((math.cos(pitch) * math.cos(az), math.cos(pitch) * math.sin(az), math.sin(pitch)))
    p1 = base + d0 * L * 0.5
    d1 = Vector((math.cos(pitch - curl) * math.cos(az), math.cos(pitch - curl) * math.sin(az),
                 math.sin(pitch - curl)))
    p2 = p1 + d1 * L * 0.5
    side = Vector((-math.sin(az), math.cos(az), 0))

    def ring(p, d, ww):
        nn = d.cross(side).normalized()
        return [bm.verts.new(p + side * ww), bm.verts.new(p - nn * ww * 0.6),
                bm.verts.new(p - side * ww)]

    r0 = ring(base, d0, w)
    r1 = ring(p1, (d0 + d1).normalized(), w * 0.7)
    tip = bm.verts.new(p2)
    low, high = [], []
    for j in range(3):
        k = (j + 1) % 3
        low.append(face(a, (r0[j], r0[k], r1[k], r1[j])))
        high.append(face(a, (r1[j], r1[k], tip)))
    t = 1 + a.rng.uniform(-0.04, 0.04)
    mark(a, low + high, "w04_grass", t)


def tuft(a, c, size=1.0, n=7, leafy=False):
    rng = a.rng
    cx, cy = c
    for i in range(n):
        az = TAU * i / n + rng.uniform(-0.4, 0.4)
        rr = rng.uniform(0.05, 0.3) * size
        b = (cx + rr * math.cos(az), cy + rr * math.sin(az), 0.06)
        if leafy:
            L, w, pitch, curl = size * rng.uniform(0.8, 1.05), 0.2 * size, math.radians(rng.uniform(50, 70)), 0.7
            blade(a, b, az, pitch, L, w, curl)
        else:
            L = size * rng.uniform(0.75, 1.25)
            w = size * rng.uniform(0.14, 0.2)
            pitch = math.radians(rng.uniform(55, 84))
            blade(a, b, az, pitch, L, w, rng.uniform(0.25, 0.6))


def pebble(a, c, s, rot=0.0):
    verts = a.rock((s, s * 0.85, s * 0.62), loc=(c[0], c[1], 0.0), rot=(0.1, 0.05, rot),
                   mat="kit_rock", subdiv=1, rough=0.1, facets=8, sink=0.2)
    rock_colours(a, verts)


def boulder(a, c, size, lean=0.22, yaw=0.5):
    """Tall leaning slab boulder: the convex hull of a hand-placed chunky prism
    (size = W x D x H), sheared so its top leans `lean` radians away from the trunk
    (+X), flat on z=0. Big clean facets like the sheet's grey rock."""
    import bmesh
    W, D, Hh = size
    rng = a.rng
    prof = [(-0.5, -0.42), (-0.12, -0.5), (0.38, -0.4), (0.5, 0.05), (0.3, 0.48),
            (-0.2, 0.5), (-0.48, 0.15)]
    pts = []
    for (u, v) in prof:   # footprint at the ground
        pts.append(Vector((u * W, v * D, 0.0)))
    for (u, v) in prof[::2] + [prof[3]]:   # shoulder ring, a little narrower
        pts.append(Vector((u * W * 0.92, v * D * 0.88, Hh * rng.uniform(0.5, 0.62))))
    for (u, v) in prof[1::2]:   # upper shoulder: a chunky rounded block, not a slab
        pts.append(Vector((u * W * 0.7, v * D * 0.66, Hh * rng.uniform(0.8, 0.88))))
    # chisel top: a sloping ridge, high on the side away from the trunk
    pts += [Vector((0.18 * W, -0.22 * D, Hh)), Vector((0.05 * W, 0.2 * D, Hh * 0.93)),
            Vector((-0.3 * W, -0.05 * D, Hh * 0.8))]
    shear = math.tan(lean)
    rot = Matrix.Rotation(yaw, 3, "Z")
    verts = []
    for p in pts:
        q = Vector((p.x + shear * p.z, p.y, p.z))
        verts.append(a.bm.verts.new(Vector((c[0], c[1], 0.0)) + rot @ q))
    res = bmesh.ops.convex_hull(a.bm, input=verts)
    hull_faces = [g for g in res["geom"] if isinstance(g, bmesh.types.BMFace)]
    for g in res["geom_interior"] + res["geom_unused"]:
        if isinstance(g, bmesh.types.BMVert) and g.is_valid and not g.link_faces:
            a.bm.verts.remove(g)
    bmesh.ops.recalc_face_normals(a.bm, faces=hull_faces)
    rock_colours(a, [v for f in hull_faces for v in f.verts])


def rock_colours(a, verts):
    """Grey rock: one kit_rock colour, small random Tint per facet."""
    mark(a, faces_of(verts), "kit_rock")


def soil(a, c, R, seed_pts=13, thick=0.1, stretch=(1.0, 1.0)):
    rng = a.rng
    pts = []
    for i in range(seed_pts):
        th = TAU * i / seed_pts + rng.uniform(-0.12, 0.12)
        r = R * rng.uniform(0.82, 1.08)
        pts.append((c[0] + r * math.cos(th) * stretch[0], c[1] + r * math.sin(th) * stretch[1]))
    verts = a.poly_prism(pts, thick, mat="w04_ground", tint=1.0)
    mark(a, faces_of(verts), "w04_ground")


def dressing(a, tufts, pebbles, soil_c=(0.0, 0.0), soil_r=3.5, soil_stretch=(1.0, 1.0),
             tuft_scale=1.3):
    """Soil patch, lush grass tufts and pebbles. tuft_scale enlarges the listed tuft
    sizes (the sheet's clumps are big and leafy); the hero lists final sizes (1.0)."""
    a.dress = True
    soil(a, soil_c, soil_r, stretch=soil_stretch)
    for (x, y, s, kind) in tufts:
        tuft(a, (x, y), s * tuft_scale, n=12 if kind != "leafy" else 8, leafy=(kind == "leafy"))
    for (x, y, s) in pebbles:
        pebble(a, (x, y), s, rot=a.rng.uniform(0, TAU))
    a.dress = False


# ---------------------------------------------------------------------------
# The Young Fir
# ---------------------------------------------------------------------------

H = 17.0
# The sheet draws the hero lit from the left with its shaded side on the right; the
# studio sun is front-left, so the hero camera looks from the front-right.
HERO_AZIMUTH = 22

# Sheet front view (measured): six rows of long leaf flaps in three groups. Crown: a
# small top cone (tips ~14.3) and one spiky hem (tips ~11.7, ~6 wide); a deep waist;
# middle group (tips ~9.9 and ~7.8, ~8.5 wide); a waist; skirt (tips ~6.6 and ~5.6,
# ~11 wide). Each hem: (apex, tip z, R, tips, alt, under_d); its notch height follows
# from the droop. Within a group the hems nest tightly; between groups the upper hem's
# tips hang ~1-1.4 studs clear of the next group's surface over a recessed dark
# under-cone (the shadowed gap). The trunk ends inside the middle group.
HERO_HEMS = [
    ("crown", 17.0, 14.2, 1.9, 6, 1.0, None),
    ("crown", 15.9, 11.6, 3.2, 7, 0.85, 0.9),
    ("middle", 12.6, 9.8, 3.7, 6, 1.0, None),
    ("middle", 12.4, 7.7, 4.6, 7, 1.0, 0.8),
    ("lower", 8.8, 6.6, 4.9, 7, 1.0, None),
    ("lower", 8.4, 5.6, 5.8, 7, 1.0, 0.6),
]
DROOP = 0.4
NOTCH = 0.56
JAG = 0.09   # uneven flap lengths: long, ragged spikes
# Pleats: each flap's two flanks slope away from its ridge, so one flank faces the sun
# (lime) and the other turns away (dark), and a keel gives each flap a thick, dark,
# downward-facing underside: the sheet's chunky two-tone flaps.
FOLD = 0.24
KEEL = 0.3
WE = 0.6
RE = 0.6   # flap edges widest ~60% out, so each broad flap narrows to a long sharp point
FRONT = -math.pi / 2   # azimuth of the front (-Y)
# yaw per hem (crown x2, middle x2, lower x2): the hems turn against each other so
# their tips interleave (a star of 7 big points with smaller points between them from
# above).
HERO_YAWS = [FRONT, FRONT + TAU / 16, FRONT + TAU / 12, FRONT + TAU / 14, FRONT, FRONT + TAU / 16]


def hero_yaws():
    """Yaw of each hero tier, so the parts reuse the hero's exact geometry."""
    return HERO_YAWS


def hero_tiers(a, which=("crown", "middle", "lower")):
    for (nm, apex, tz, R, tips, alt, ud), yaw in zip(HERO_HEMS, hero_yaws()):
        if nm in which:
            zb = (tz + DROOP * apex) / (1 + DROOP)
            tier(a, (0, 0), zb, apex, R, tips, yaw, droop=DROOP, notch=NOTCH, alt=alt,
                 under_d=ud, jag=JAG, fold=FOLD, keel=KEEL, wE=WE, rE=RE, s_r=0.12, s_f=0.9, pw=1.3)


def hero_trunk(a, top=10.8, cut=False):
    # ~1.6 across under the skirt, flaring at the ground; it ends inside the middle
    # group, so no bark shows in the gaps between the canopy groups
    zs = [0, 0.35, 0.9, 2.6, 5.5, 8.0, top]
    radii = [1.25, 1.02, 0.86, 0.8, 0.74, 0.55, 0.38]
    trunk(a, [(0, 0, z) for z in zs], radii, sides=9, flare=(0.36, 0.14, 0.03), lobes=4,
          grooves=3, groove_depth=0.14, twist=0.12, cut_top=cut)


# tufts stand to the sides and behind, clear of the root flare in the front views
HERO_TUFTS = [(-3.0, -0.6, 1.4, "grass"), (-2.3, -2.4, 1.2, "leafy"), (1.9, -3.1, 0.9, "grass"),
              (5.2, -0.6, 1.3, "grass"), (-1.2, 2.5, 1.3, "grass"), (-3.6, 1.1, 1.1, "leafy"),
              (2.4, 1.8, 1.0, "grass")]
HERO_PEBBLES = [(-1.0, -3.0, 0.7), (0.9, -3.3, 0.5)]


def build_hero(kit):
    a = new_asset(kit, "YoungFir", 201)
    hero_trunk(a)
    roots(a, (0, 0, 0), 1.0, 5, 2.3, 1.5, 0.44, phase=0.4)
    hero_tiers(a)
    boulder(a, (3.4, -1.3), (2.3, 2.1, 2.9), lean=0.28, yaw=0.0)
    dressing(a, HERO_TUFTS, HERO_PEBBLES, soil_c=(0.8, -0.5), soil_r=3.9, tuft_scale=1.0)
    return finish(a)


def build_crown(kit):
    a = new_asset(kit, "YoungFirCrownTier", 202)
    hero_tiers(a, ("crown",))
    return finish(a)


def build_middle(kit):
    a = new_asset(kit, "YoungFirMiddleTier", 203)
    hero_tiers(a, ("middle",))
    return finish(a)


def build_lower(kit):
    a = new_asset(kit, "YoungFirLowerSkirt", 204)
    hero_tiers(a, ("lower",))
    return finish(a)


def build_trunk(kit):
    a = new_asset(kit, "YoungFirTrunk", 205)
    # the visible stretch of the hero trunk: from the root base cut (1.8) up to the skirt
    zs = [0, 1.4, 3.0, 4.6]
    radii = [0.86, 0.82, 0.77, 0.72]
    # a wide sloping wood-end ring around a heart sunk well below it, so the cut reads
    trunk(a, [(0, 0, z) for z in zs], radii, sides=9, grooves=3, groove_depth=0.14,
          twist=0.12, cut_top=True, heart=0.42, sink=0.28)
    obj = finish(a)
    obj["kit_shading_ok"] = ("real material change: the flat cut top is pale w04_wood_end "
                             "heartwood, the sides w04_bark; on this short part the cut top "
                             "is a big share of the faces")
    return obj


def build_root_base(kit):
    a = new_asset(kit, "YoungFirRootBase", 206)
    zs = [0, 0.35, 0.9, 1.8]
    radii = [1.2, 1.02, 0.96, 0.92]
    trunk(a, [(0, 0, z) for z in zs], radii, sides=9, flare=(0.3, 0.12, 0.03), lobes=4,
          grooves=3, groove_depth=0.14, twist=0.12, cut_top=True)
    roots(a, (0, 0, 0), 1.0, 5, 2.4, 1.4, 0.42, phase=0.4)
    dressing(a, [(-2.5, -0.8, 1.0, "grass"), (-1.4, -2.0, 0.85, "leafy"), (2.4, -1.0, 0.95, "grass"),
                 (1.0, 2.2, 0.85, "grass")],
             [(-1.9, -1.6, 0.8), (2.2, -2.2, 0.75), (-0.2, -2.6, 0.4)], soil_r=3.4)
    return finish(a)


def build_sparse(kit):
    a = new_asset(kit, "YoungFirSparse", 207)
    zs = [0, 0.35, 0.9, 3.0, 7.0, 11.0, 14.5]
    radii = [1.0, 0.86, 0.8, 0.72, 0.6, 0.46, 0.3]
    trunk(a, [(0, 0, z) for z in zs], radii, sides=8, flare=(0.3, 0.12, 0.03), lobes=4,
          grooves=3, groove_depth=0.14, twist=0.12)
    roots(a, (0, 0, 0), 0.85, 4, 1.9, 1.3, 0.36, phase=0.2)
    # (centre x, zb, apex, R, tips): narrow separated tiers; the two middle ones sit
    # off-axis on short branches like the sheet's side clumps
    # same broad shield flaps as the hero, smaller and well separated
    tiers = [((0.0, 0.0), 13.4, 16.0, 2.2, 8, 0.3), ((0.0, 0.0), 11.3, 13.2, 3.0, 8, 0.55),
             ((-1.2, 0.2), 9.2, 10.8, 2.6, 6, 0.55), ((1.4, -0.2), 7.3, 8.9, 2.7, 6, 0.55),
             ((0.0, 0.0), 5.3, 7.1, 4.1, 8, 0.65)]
    yaw = 0.0
    for i, (c, zb, apex, R, tips, dr) in enumerate(tiers):
        # every tier is its own group: a dark under-cone under each one
        tier(a, c, zb, apex, R, tips, yaw, droop=dr, notch=NOTCH, alt=0.8 if i == 0 else 1.0,
             under_d=0.3 * R)
        yaw += TAU / 16
    branch(a, (0, 0, 9.0), (-1.2, 0.2, 9.6), 0.26, stub=False)
    branch(a, (0, 0, 7.1), (1.4, -0.2, 7.7), 0.28, stub=False)
    # bare stubs
    branch(a, (0, 0, 10.4), (1.25, -0.3, 11.0), 0.18)
    branch(a, (0, 0, 6.3), (-1.35, -0.2, 6.7), 0.2)
    dressing(a, [(-2.0, -0.8, 0.9, "grass"), (-1.0, -1.9, 0.8, "leafy"), (1.3, -1.6, 0.85, "grass"),
                 (2.4, 0.2, 0.9, "grass")],
             [(-0.4, -2.0, 0.6), (1.9, -1.0, 0.5)], soil_r=2.8)
    return finish(a)


def build_full(kit):
    a = new_asset(kit, "YoungFirFull", 208)
    zs = [0, 0.35, 0.9, 2.5, 6.0, 10.0, 13.5]
    radii = [1.35, 1.15, 1.08, 1.0, 0.85, 0.65, 0.45]
    trunk(a, [(0, 0, z) for z in zs], radii, sides=9, flare=(0.32, 0.12, 0.03), lobes=4,
          grooves=3, groove_depth=0.14, twist=0.12)
    roots(a, (0, 0, 0), 1.15, 5, 2.5, 1.5, 0.46, phase=0.9)
    # broad pyramid: the upper hems step in steeply, the lower three are ~12 across
    tiers = [(14.0, 17.0, 2.3, 8, 0.3, 0.8), (12.3, 14.3, 3.0, 8, 0.55), (10.7, 12.7, 3.8, 8, 0.55),
             (9.1, 11.1, 4.6, 8, 0.6), (7.5, 9.5, 5.4, 8, 0.6), (5.9, 7.9, 5.9, 8, 0.65),
             (4.3, 6.3, 6.2, 8, 0.7, 1.0, 1.5)]
    canopy(a, lambda z: (0.0, 0.0), tiers, 0.0, droop=0.38, notch=NOTCH)
    dressing(a, [(-2.8, -1.0, 1.0, "grass"), (-1.4, -2.3, 0.9, "leafy"), (1.0, -2.4, 0.9, "grass"),
                 (2.9, -0.8, 1.0, "grass"), (0.0, 2.6, 0.9, "grass")],
             [(-0.2, -2.7, 0.65), (2.2, -2.0, 0.7), (-2.4, -2.0, 0.5)], soil_r=3.6)
    return finish(a)


def build_leaning(kit):
    a = new_asset(kit, "YoungFirLeaning", 209)
    # bowed axis: upright at the base, bending toward +X low down, then leaning
    # straight (~11 degrees overall); the crown tip sits ~2.7 studs over
    axis = [(0.0, 0.0), (0.05, 1.0), (0.35, 3.0), (0.95, 5.5), (1.6, 8.5), (2.2, 11.5),
            (2.6, 14.0)]

    def axis_x(z):
        for (x0, z0), (x1, z1) in zip(axis, axis[1:]):
            if z <= z1:
                u = max(0.0, (z - z0) / (z1 - z0))
                return x0 + (x1 - x0) * u
        (x0, z0), (x1, z1) = axis[-2], axis[-1]
        return x1 + (x1 - x0) / (z1 - z0) * (z - z1)

    pts = [(x, 0.0, z) for x, z in axis]
    radii = [1.35, 1.15, 1.0, 0.9, 0.78, 0.6, 0.42]
    trunk(a, pts, radii, sides=9, flare=(0.32, 0.12, 0.03), lobes=4, grooves=3,
          groove_depth=0.14, twist=0.12)
    roots(a, (0, 0, 0), 1.05, 5, 2.1, 1.5, 0.44, bias=(math.pi, 0.6), phase=0.0)
    # same three-group layout as the hero (crown | 2 | 2), a little smaller
    tiers = [(12.4, 15.0, 2.8, 8, 0.36, 0.8, 1.4), (9.8, 11.3, 3.3, 8, 0.45),
             (8.6, 10.4, 4.3, 8, 0.6, 1.0, 1.6),
             (6.0, 7.3, 3.9, 8, 0.5), (5.0, 6.6, 5.0, 8, 0.7, 1.0, 1.4)]
    canopy(a, lambda z: (axis_x(z + 0.8), 0.0), tiers, 0.0, droop=DROOP, notch=NOTCH)
    dressing(a, [(-2.8, -0.6, 1.0, "grass"), (-1.6, -2.0, 0.85, "leafy"), (1.4, -1.9, 0.85, "grass"),
                 (2.6, 0.6, 0.9, "grass")],
             [(-0.5, -2.3, 0.6), (2.3, -1.2, 0.75)], soil_c=(-0.4, 0.0), soil_r=3.3)
    return finish(a)


def build(kit):
    hero = kit.tag(build_hero(kit), "hero", collision="hull", budget=4000,
                   notes="tiers + trunk + boulder collide; grass tufts, pebbles and soil "
                         "patch faces carry kit_nocollide=1 (walk-through dressing)")
    parts = [
        kit.tag(build_crown(kit), "part", collision="hull", budget=1500,
                notes="Crown Tier: hero top cone, notches at z=13.6 on the hero; its dark under-cone ends on the trunk above the middle group (gap)"),
        kit.tag(build_middle(kit), "part", collision="hull", budget=1500,
                notes="Middle Tier: two nested hems + dark under-cone; on the hero its bottom sits ~1 stud below the crown gap"),
        kit.tag(build_lower(kit), "part", collision="hull", budget=1500,
                notes="Lower Skirt: two hems, widest, drooping tips, dark under-cone; re-stacks below the middle gap"),
        kit.tag(build_trunk(kit), "part", collision="hull", budget=800,
                notes="Trunk: the visible stretch, sits on YoungFirRootBase cut top (z=1.8) up to the skirt"),
        kit.tag(build_root_base(kit), "part", collision="hull", budget=1500,
                notes="Root Base: roots collide; tufts/pebbles/soil carry kit_nocollide=1"),
    ]
    variants = [
        kit.tag(build_sparse(kit), "variant", collision="hull", budget=4000,
                notes="see-through sparse fir; dressing faces carry kit_nocollide=1"),
        kit.tag(build_full(kit), "variant", collision="hull", budget=4000,
                notes="dense 7-hem fir; dressing faces carry kit_nocollide=1"),
        kit.tag(build_leaning(kit), "variant", collision="hull", budget=4000,
                notes="trunk leans ~12 deg toward +X; the runner centres the origin on the "
                      "footprint, so the trunk base sits ~1.2 studs -X of the origin"),
    ]
    return [hero] + parts + variants
