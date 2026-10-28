"""W04 row 3, SAPLING: a small, chunky young pine about character height.

Sapling (hero, ~5 W x 5 D x 6 H): two foliage tiers on an oversized stubby
trunk. The lower foliage is a double-hem skirt (8 broad drooping tips, with a
second, higher row of tips set in the notches); the top foliage is a pointed
6-tip cone. The trunk is thick for its size, flares at the foot into 4 small
roots, and is hugged by a ring of grey rocks, a few grass tufts and a thin sandy
soil patch.

Parts: SaplingTopFoliage, SaplingLowerFoliage, SaplingTrunk (cut top in
w04_wood_end with a sunken heart), SaplingRootsBase (root flare stump + rock
ring + grass + soil). Variants: SaplingSeedling (one tier on a stub),
SaplingBushy (3 wide overlapping tiers, low and round), SaplingSlender (3
narrow tiers on a thin, taller trunk). No VFX: the sheet shows none and saplings
are not harvestable.

Technique: each tier is star_row(): one closed, solid cone of 6-9 broad panels
that meet edge to edge (two big planes creased on a ridge, a drooping tip, a
raised notch), a thick hem band and a downward-facing under-cone; the double hem
is a second, shorter star_row set in the notches. From above the tips read as a
star. The crown's hem sits below the skirt's apex so the tiers nest with no gap. The trunk is build_05's faceted ring tube
with root flare lobes and pulled-in groove columns, simplified to fewer rings so
the facets stay big and toy-like. Colour: ONE palette key per material
(w04_needle at Tint ~1.15 for the sheet's brightest green, w04_bark, w04_wood_end,
w04_ground, w04_grass, kit_rock), Tint jitter only; the light tops, dark
undersides and dark hem bands come from geometry shaded by the studio light and
Roblox lighting, never from colour.
"""

import math

import bmesh
from mathutils import Matrix, Vector

SUBJECT = "Sapling"
ROW = 3
PALETTE = {
    "w04_needle": ("#6A963E", 0.8, 0, 0),  # ALL conifer needles on every W04 tree (skirts, hems, tip flaps, undersides, old-pine cloud pads). One key: the reference's dark-teal underside (#2E5143), mid (#5A8545) and lime lit tops (#93B63F/#B2C63A) are lighting, not paint. Sapling may push Tint up to ~1.2 for its brighter look; keep Tint variation within one material <= 1.25x.
    "w04_bark": ("#9A6038", 0.9, 0, 0),  # All trunk, root flare, branch and stub bark. Grooves and fluting are GEOMETRY (pulled-in groove vertices, twisted lobes) shaded by the sun, never a darker key.
    "w04_wood_end": ("#E4A458", 0.85, 0, 0),  # Cut heartwood: flat cut tops of trunk parts, cut ends of branch parts, pale rims and splinters of broken stubs/broken crown. Hollows are recessed geometry lined with this key (the dark inside is shadow).
    "w04_ground": ("#DCC9A0", 0.95, 0, 0),  # Thin pale sandy soil patch under each tree base (the cream swatch).
    "w04_grass": ("#8DB83A", 0.9, 0, 0),  # Grass tufts and the leafy fern clumps around the bases (grass class, distinct from needles). Replaces moss/moss_light/moss_dark/w04_olive in tufts; the olive-yellow swatch is the lit grass tip, i.e. lighting.
    # "kit_rock": ("#A89C9C", 0.9, 0, 0),  # Existing KIT_PALETTE key (used as-is; the runner only accepts w04_-prefixed keys here): the pale grey faceted rocks/pebbles at every tree base (one key for all rocks; no kit_rock_light/dark).
}

TAU = 2 * math.pi
Z = Vector((0, 0, 1))
# ONE colour per material: every needle face is w04_needle, every bark face
# w04_bark, every rock kit_rock, every grass blade w04_grass. The light tops and
# dark undersides seen on the reference are lighting: the studio render and
# Roblox shade the facets. Tint is only a small random per-face jitter around a
# per-material level (the sapling is the brightest green on the sheet, so its
# needles sit at Tint ~1.15).
NEEDLE_TINT = 1.15
F_NEEDLE, F_BARK, F_ROCK = 1, 2, 3  # face families (kept for reference; nothing is relit)


# ---------------------------------------------------------------------------
# Asset plumbing
# ---------------------------------------------------------------------------


def new_asset(fk, name, seed):
    a = fk.Asset(name, "Kit", seed=seed, tint_var=0.04)
    a.bm.faces.layers.int.new("fam")
    return a


def qt(t):
    """Quantise a Tint to a few levels (keeps the Roblox palette texture small)."""
    return round(t * 40) / 40


def paint(a, faces, mat, fam=0, tint=1.0, var=0.04):
    lay = a.bm.faces.layers.int["fam"]
    mi = a._mi(mat)
    for f in faces:
        f.material_index = mi
        f.smooth = False
        f[lay] = fam
        t = qt(tint * (1 + a.rng.uniform(-var, var)))
        for lp in f.loops:
            lp[a.tint_layer] = (t, t, t, 1.0)
    return faces


def finish(a):
    used = sorted({f.material_index for f in a.bm.faces})
    remap = {old: new for new, old in enumerate(used)}
    for f in a.bm.faces:
        f.material_index = remap[f.material_index]
    a.mats = [a.mats[i] for i in used]
    a.bm.faces.layers.int.remove(a.bm.faces.layers.int["fam"])
    for v in a.bm.verts:
        if v.co.z < 0.0:
            v.co.z = 0.0
    return a.finish()


def polar(r, az, z):
    return Vector((r * math.cos(az), r * math.sin(az), z))


def bezier(p0, p1, p2, n):
    p0, p1, p2 = Vector(p0), Vector(p1), Vector(p2)
    return [(1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2 for t in (i / (n - 1) for i in range(n))]


# ---------------------------------------------------------------------------
# Foliage tier (build_05 pine_tier, fewer rings for bigger facets)
# ---------------------------------------------------------------------------


def star_row(a, zh, apex, R, n, yaw=0.0, thick=0.22, shoulder=(0.6, 0.5), notch=(0.6, 0.26),
             under=0.25, jag=0.04, corner=0.24, cr=0.8, cz=0.12):
    """One closed, solid row of `n` BROAD drooping panels round a common apex.

    Each panel runs from the apex over a shoulder (radius shoulder[0] x R at
    shoulder[1] of the row height) and then bends down more steeply to a blunt
    hem: two corners either side of a slightly lower centre tip at radius R and
    height zh. Neighbouring panels meet edge to edge at a raised notch (radius
    notch[0] x R, notch[1] of the height up), so the row is one solid cone with
    a scalloped star hem and no gaps. Every panel is two big planes creased on
    its ridge (apex - shoulder - tip), so the sun lights one half and shades the
    other. The hem is a thick band (`thick` studs) closed by a downward-facing
    under-cone: that is the dark band under each hem, from geometry, not paint.
    ~20 triangles per panel."""
    bm = a.bm
    h = apex - zh
    step = TAU / n
    A = bm.verts.new((0, 0, apex))
    S, V, rim = [], [], []
    for i in range(n):
        th = yaw + step * i + a.rng.uniform(-0.04, 0.04)
        rr = R * (1 + a.rng.uniform(-jag, jag))
        S.append(bm.verts.new(polar(rr * shoulder[0], th, zh + shoulder[1] * h)))
        V.append(bm.verts.new(polar(rr * shoulder[0] * 0.84, th + step / 2, zh + (shoulder[1] + 0.05) * h)))
        rim += [bm.verts.new(polar(rr * cr, th - corner * step, zh + cz * h)),    # left corner
                bm.verts.new(polar(rr, th, zh)),                                   # tip (lowest, drooping)
                bm.verts.new(polar(rr * cr, th + corner * step, zh + cz * h)),    # right corner
                bm.verts.new(polar(R * notch[0], th + step / 2, zh + notch[1] * h))]  # notch
    faces = []
    for i in range(n):
        p = i - 1
        CL, T, CR, N = rim[4 * i: 4 * i + 4]
        Np = rim[4 * p + 3]
        faces += [bm.faces.new(f) for f in (
            (A, S[i], V[i]), (A, V[p], S[i]),
            (S[i], V[p], Np), (S[i], Np, CL), (S[i], CL, T),
            (S[i], T, CR), (S[i], CR, N), (S[i], N, V[i]))]
    # thick hem band and under-cone
    m = len(rim)
    bot = []
    for v in rim:
        c = v.co
        k = max(0.0, 1.0 - 0.6 * thick / max(Vector((c.x, c.y)).length, 1e-6))
        bot.append(bm.verts.new((c.x * k, c.y * k, c.z - thick)))
    U = bm.verts.new((0, 0, zh + under * h))
    for j in range(m):
        q = (j + 1) % m
        faces.append(bm.faces.new((rim[j], rim[q], bot[q], bot[j])))
        faces.append(bm.faces.new((U, bot[q], bot[j])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    paint(a, faces, "w04_needle", F_NEEDLE, tint=NEEDLE_TINT, var=0.05)
    return faces


def tier(a, zt, apex, R, tips, yaw=0.0, double=True, thick=0.22, up=(0.84, 0.3), **kw):
    """One foliage tier: a broad-panelled star_row with its hem at zt, plus (if
    `double`) a second, higher and shorter row of panels set in the notches:
    the staggered double hem. From above the tier reads as a pointed star."""
    h = apex - zt
    faces = star_row(a, zt, apex, R, tips, yaw, thick, **kw)
    if double:
        zu = zt + up[1] * h
        faces += star_row(a, zu, apex + 0.04 * h, R * up[0], tips, yaw + TAU / tips / 2, thick * 0.85,
                          under=0.1, **kw)
    return faces


def tiers(a, spec):
    """spec: list of dicts of tier() kwargs."""
    for t in spec:
        tier(a, **t)


# ---------------------------------------------------------------------------
# Trunk and roots (build_05 trunk, simplified)
# ---------------------------------------------------------------------------


def ring_tube(a, pts, radii, sides=9, flare=(), lobes=4, grooves=3, groove_depth=0.12, twist=0.12,
              rough=0.03, caps=(False, True), top_mat="w04_bark"):
    """Faceted tube through pts with per-ring radii. `flare` widens the first
    rings into rounded root lobes; every (sides/grooves)th column is a pulled-in
    groove streak. Returns the top cap face (or None)."""
    bm = a.bm
    pts = [Vector(p) for p in pts]
    n = len(pts)
    tans = [(pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized() for i in range(n)]
    up = Z if abs(tans[0].z) < 0.9 else Vector((1, 0, 0))
    nrm = tans[0].cross(up).normalized()
    frames = []
    for i in range(n):
        if i:
            axis = tans[i - 1].cross(tans[i])
            if axis.length > 1e-6:
                nrm = Matrix.Rotation(tans[i - 1].angle(tans[i]), 3, axis.normalized()) @ nrm
            nrm = (nrm - tans[i] * nrm.dot(tans[i])).normalized()
        frames.append((nrm, tans[i].cross(nrm)))
    phase = a.rng.uniform(0, TAU)
    rings = []
    for i, (nr, bi) in enumerate(frames):
        f = flare[i] if i < len(flare) else 0.0
        ring = []
        for j in range(sides):
            loc = TAU * j / sides
            th = loc + twist * i
            r = radii[i]
            if f:
                lob = ((1 + math.cos(lobes * (th - phase))) / 2) ** 2
                r *= 1 + f * (0.3 + 0.6 * lob)
            if grooves:
                g = ((1 + math.cos(grooves * loc)) / 2) ** 6
                r *= 1 - groove_depth * g
            r *= 1 + a.rng.uniform(-rough, rough)
            ring.append(bm.verts.new(pts[i] + r * (math.cos(th) * nr + math.sin(th) * bi)))
        rings.append(ring)
    body = []
    for i in range(n - 1):
        r1, r2 = rings[i], rings[i + 1]
        for j in range(sides):
            k = (j + 1) % sides
            body.append(bm.faces.new((r1[j], r1[k], r2[k], r2[j])))
    if caps[0]:
        body.append(bm.faces.new(list(reversed(rings[0]))))
    cap = None
    if caps[1]:
        cap = bm.faces.new(rings[-1])
    paint(a, body, "w04_bark", F_BARK)
    if cap is not None:
        paint(a, [cap], top_mat, 0 if top_mat != "w04_bark" else F_BARK)
    return cap


def cut_top(a, cap, r):
    """Turn a cap into a cut log end: a w04_wood_end rim and a sunken heart lined
    with the same key (the hollow reads darker through shadow, not paint)."""
    res = bmesh.ops.inset_region(a.bm, faces=[cap], thickness=r * 0.42, depth=-r * 0.22)
    paint(a, res["faces"] + [cap], "w04_wood_end", 0, tint=1.0, var=0.02)


def roots(a, n, trunk_r, reach, height, r0, phase=0.6, sides=5):
    for k in range(n):
        az = phase + TAU * k / n + a.rng.uniform(-0.2, 0.2)
        rk = reach * a.rng.uniform(0.85, 1.1)
        top = polar(trunk_r * 0.55, az, height * a.rng.uniform(0.9, 1.1))
        mid = polar(trunk_r * 1.05, az, height * 0.35)
        end = polar(rk, az, -0.05)
        ring_tube(a, bezier(top, mid, end, 4), [r0, r0 * 0.85, r0 * 0.62, r0 * 0.3], sides=sides,
                  grooves=0, rough=0.05, twist=0.0, caps=(False, True))


def trunk(a, zs, radii, flare=(0.5, 0.16), sides=9, cut=False):
    cap = ring_tube(a, [(0, 0, z) for z in zs], radii, sides=sides, flare=flare,
                    top_mat="w04_wood_end" if cut else "w04_bark")
    if cut and cap is not None:
        cut_top(a, cap, radii[-1])


# ---------------------------------------------------------------------------
# Base: rocks, grass, soil
# ---------------------------------------------------------------------------


def rock(a, x, y, size, yaw=0.0):
    size = tuple(s * 1.15 for s in size)
    verts = a.rock(size, loc=(x, y, 0.0), rot=(0, 0, yaw), mat="kit_rock", subdiv=1, rough=0.14,
                   facets=12, sink=0.18)
    # one stone colour for every rock; lighting gives the pale tops and dark sides
    paint(a, list({f for v in verts for f in v.link_faces}), "kit_rock", F_ROCK, var=0.05)


def blade(a, base, az, pitch, length, w, mat, tint):
    """One grass blade: a thin three-sided spike (no hidden bottom face)."""
    bm = a.bm
    d = Vector((math.cos(pitch) * math.cos(az), math.cos(pitch) * math.sin(az), math.sin(pitch)))
    side = Vector((-math.sin(az), math.cos(az), 0))
    b = Vector(base)
    p0 = bm.verts.new(b + side * w)
    p1 = bm.verts.new(b - side * w)
    p2 = bm.verts.new(b - Vector((math.cos(az), math.sin(az), 0)) * w * 0.8)
    tip = bm.verts.new(b + d * length)
    faces = [bm.faces.new((p0, p1, tip)), bm.faces.new((p1, p2, tip)), bm.faces.new((p2, p0, tip))]
    paint(a, faces, mat, 0, tint=tint, var=0.03)


def tuft(a, x, y, size=1.0, n=9):
    """A spiky grass tuft: blades fanning out of one spot, all w04_grass."""
    for i in range(n):
        az = TAU * i / n + a.rng.uniform(-0.3, 0.3)
        r = 0.16 * size
        pitch = math.radians(a.rng.uniform(55, 82))
        L = size * a.rng.uniform(0.6, 0.95)
        blade(a, (x + r * math.cos(az), y + r * math.sin(az), 0.0), az, pitch, L, 0.09 * size + 0.02,
              "w04_grass", 1.0)


def soil(a, rx, ry, n=13, thick=0.04, seed_off=0.0):
    """Thin irregular sandy patch (top face + rim, no bottom face)."""
    bm = a.bm
    bot, top = [], []
    for k in range(n):
        th = TAU * k / n + seed_off + a.rng.uniform(-0.12, 0.12)
        s = a.rng.uniform(0.86, 1.08)
        p = (rx * s * math.cos(th), ry * s * math.sin(th))
        bot.append(bm.verts.new((p[0], p[1], 0.0)))
        top.append(bm.verts.new((p[0] * 0.97, p[1] * 0.97, thick)))
    faces = [bm.faces.new(top)]
    for k in range(n):
        j = (k + 1) % n
        faces.append(bm.faces.new((bot[k], bot[j], top[j], top[k])))
    paint(a, faces, "w04_ground", 0, tint=1.0, var=0.02)


def base(a, rocks, tufts, patch):
    soil(a, *patch)
    for x, y, size, yaw in rocks:
        rock(a, x, y, size, yaw)
    for x, y, s in tufts:
        tuft(a, x, y, s * 1.2)


# ---------------------------------------------------------------------------
# Layouts (studs; front = -Y)
# ---------------------------------------------------------------------------

# Hero: crown hem (4.0) sits well below the skirt's apex (4.9) and outside the
# skirt surface there, so the crown is nested into the skirt with no gap.
HERO_TOP = dict(zt=4.05, apex=6.0, R=1.7, tips=6, yaw=0.3, double=False, thick=0.26,
                shoulder=(0.5, 0.4), under=0.05)
HERO_LOWER = [dict(zt=2.45, apex=4.9, R=2.5, tips=8, yaw=0.0, thick=0.24)]
HERO_TRUNK = dict(zs=[0, 0.3, 0.9, 1.8, 2.8, 3.8], radii=[0.82, 0.72, 0.68, 0.64, 0.56, 0.42],
                  flare=(0.45, 0.14), sides=9)
HERO_ROCKS = [(-1.45, -0.5, (1.0, 0.9, 0.75), 0.3),
              (-0.75, -1.3, (0.85, 0.75, 0.55), 1.1),
              (1.5, -0.45, (1.05, 0.9, 0.75), 2.0),
              (0.55, -1.45, (0.6, 0.5, 0.42), 0.7),
              (1.05, 1.2, (0.65, 0.6, 0.5), 2.6),
              (-1.5, 1.45, (0.7, 0.62, 0.5), 1.7)]
HERO_TUFTS = [(-2.1, -0.35, 1.05), (-0.1, -1.85, 0.9), (2.2, -0.5, 1.05), (1.6, 1.6, 0.85)]
HERO_PATCH = (2.5, 2.3)


def hero_roots(a):
    roots(a, 4, 0.85, 1.55, 1.0, 0.4)


def hero_base(a, stump=False):
    if stump:
        trunk(a, [0, 0.3, 0.75], [0.82, 0.72, 0.68], flare=(0.45, 0.14), cut=True)
    hero_roots(a)
    base(a, HERO_ROCKS, HERO_TUFTS, HERO_PATCH)


def shifted(d, dz):
    return dict(d, zt=d["zt"] - dz, apex=d["apex"] - dz)


def build(kit):
    fk = kit.flintkit
    out = []

    # Hero
    a = new_asset(fk, "Sapling", 301)
    trunk(a, **HERO_TRUNK)
    hero_base(a)
    tiers(a, HERO_LOWER + [HERO_TOP])
    out.append(kit.tag(finish(a), "hero", collision="hull", budget=2000,
                       notes="Young pine ~6 studs tall: a squat 6-panel crown nested into a broad 8+8-panel "
                             "double-hem skirt on an oversized stubby trunk with a rock ring. "
                             "No VFX (not harvestable)."))

    # Parts
    a = new_asset(fk, "SaplingTopFoliage", 302)
    tier(a, **shifted(HERO_TOP, HERO_TOP["zt"] - HERO_TOP["thick"]))
    out.append(kit.tag(finish(a), "part", collision="hull", budget=600,
                       notes="Top Foliage: the pointed 6-panel crown cone."))

    a = new_asset(fk, "SaplingLowerFoliage", 303)
    z0 = HERO_LOWER[0]["zt"] - HERO_LOWER[0]["thick"]
    tiers(a, [shifted(d, z0) for d in HERO_LOWER])
    out.append(kit.tag(finish(a), "part", collision="hull", budget=600,
                       notes="Lower Foliage: the wide double-hem skirt (8 broad drooping panels + 8 shorter "
                             "panels in the notches)."))

    a = new_asset(fk, "SaplingTrunk", 304)
    trunk(a, [0, 0.3, 1.1, 2.0, 2.9], [0.82, 0.72, 0.66, 0.6, 0.55], flare=(0.45, 0.14), cut=True)
    roots(a, 4, 0.8, 1.35, 0.85, 0.34)
    o = finish(a)
    # the up-facing cut top is a real material change (pale heartwood vs bark),
    # not painted light: the hue-family check lumps w04_wood_end with w04_bark
    o["kit_shading_ok"] = "cut top is w04_wood_end heartwood, a distinct material from the w04_bark sides"
    out.append(kit.tag(o, "part", collision="hull", budget=300,
                       notes="Trunk: stubby, thick tapered trunk with a flared foot and a cut top "
                             "(w04_wood_end rim and sunken heart)."))

    a = new_asset(fk, "SaplingRootsBase", 305)
    hero_base(a, stump=True)
    out.append(kit.tag(finish(a), "part", collision="none", budget=800,
                       notes="Roots / Base: root flare stump, 4 roots, rock ring, grass tufts and soil patch."))

    # Variants
    a = new_asset(fk, "SaplingSeedling", 306)
    trunk(a, [0, 0.25, 0.8, 1.5, 2.2], [0.5, 0.44, 0.4, 0.34, 0.24], flare=(0.4, 0.1), sides=8)
    roots(a, 4, 0.48, 0.9, 0.55, 0.22)
    base(a, [(-0.95, -0.35, (0.55, 0.5, 0.42), 0.4), (0.95, -0.45, (0.6, 0.52, 0.45), 1.5),
             (0.2, 0.95, (0.45, 0.4, 0.34), 2.2)],
         [(-1.25, -0.55, 0.6), (1.3, 0.1, 0.6), (0.1, -1.25, 0.5)], (1.55, 1.4, 11))
    tier(a, zt=1.55, apex=3.5, R=1.5, tips=7, yaw=0.2, thick=0.18)
    out.append(kit.tag(finish(a), "variant", collision="none", budget=800,
                       notes="SEEDLING: one small double-hem tier on a short thick stub, pebbles and tufts; "
                             "walk-through."))

    a = new_asset(fk, "SaplingBushy", 307)
    trunk(a, [0, 0.3, 0.9, 1.8, 3.0], [0.78, 0.68, 0.62, 0.55, 0.4], flare=(0.45, 0.14))
    roots(a, 4, 0.78, 1.4, 0.8, 0.34)
    base(a, [(-1.55, -0.55, (0.85, 0.75, 0.65), 0.2), (1.5, -0.6, (0.8, 0.72, 0.6), 1.4),
             (0.3, -1.5, (0.5, 0.45, 0.4), 2.4), (-0.65, 1.4, (0.6, 0.55, 0.45), 0.9)],
         [(-2.25, -0.45, 0.95), (2.3, -0.25, 0.9), (0.95, -1.75, 0.75)], (2.7, 2.5))
    tiers(a, [dict(zt=1.75, apex=4.0, R=3.15, tips=9, yaw=0.0, thick=0.28, shoulder=(0.66, 0.5)),
              dict(zt=3.05, apex=5.0, R=2.55, tips=8, yaw=0.2, thick=0.26, double=False,
                   shoulder=(0.64, 0.48), under=0.1),
              dict(zt=4.3, apex=6.0, R=1.75, tips=6, yaw=0.5, double=False, thick=0.22,
                   shoulder=(0.58, 0.45), under=0.05)])
    out.append(kit.tag(finish(a), "variant", collision="hull", budget=2000,
                       notes="BUSHY: three dense, wide, overlapping tiers; low and round."))

    a = new_asset(fk, "SaplingSlender", 308)
    trunk(a, [0, 0.3, 1.2, 2.4, 3.6, 5.4], [0.5, 0.44, 0.4, 0.36, 0.3, 0.2], flare=(0.4, 0.12), sides=8)
    roots(a, 4, 0.5, 0.95, 0.55, 0.21)
    base(a, [(-1.1, -0.4, (0.7, 0.62, 0.55), 0.5), (1.1, -0.3, (0.65, 0.6, 0.5), 1.9),
             (0.2, -1.1, (0.42, 0.4, 0.34), 1.1), (-0.4, 1.05, (0.5, 0.45, 0.38), 2.7)],
         [(-1.65, -0.45, 0.85), (1.7, -0.1, 0.85), (-0.3, -1.45, 0.65)], (2.05, 1.9))
    tiers(a, [dict(zt=2.6, apex=4.9, R=1.95, tips=7, yaw=0.0, thick=0.2),
              dict(zt=4.0, apex=6.15, R=1.5, tips=6, yaw=0.3, thick=0.18),
              dict(zt=5.45, apex=7.5, R=1.05, tips=5, yaw=0.1, double=False, thick=0.16,
                   shoulder=(0.6, 0.45), under=0.05)])
    out.append(kit.tag(finish(a), "variant", collision="hull", budget=2000,
                       notes="SLENDER: three narrow tiers on a thinner, taller trunk."))
    return out
