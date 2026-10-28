"""W04 row 1: Classic Pine, the archetypal stepped conifer.

Assets
  ClassicPine              hero: 7 stacked scalloped needle skirts over a stout fluted
                           trunk with buttress roots, grey rocks, grass tufts and a
                           cream soil patch (~16 x 16 x 22)
  ClassicPineTopTip        part: the top skirt (one hem)
  ClassicPineCanopyTier3   part: hero skirts 2-3 (two nested hems)
  ClassicPineCanopyTier2   part: hero skirts 4-5
  ClassicPineCanopyTier1   part: hero skirts 6-7 (widest)
  ClassicPineTrunk         part: tapered trunk column with a flat cut top
  ClassicPineRootFoot      part: flared root base cut flat at 2 studs, rocks, tufts, soil
  ClassicPineTallNarrow    variant: 9 hems, narrow spire (~11 x 26)
  ClassicPineShortWide     variant: 5 broad hems, short trunk (~17 x 16)
  ClassicPineAsymmetric    variant: lopsided canopy heavy on -X, tip drifting +X, trunk
                           exposed on +X, broken branch stub

Technique: each skirt follows the lobby pine_tier() (build_05_trees_plants.py): a
ring of 8 broad, drooping, ridge-folded flaps with deep notches, a raised shoulder,
then a cone up to the apex. Under every flap a steep downward-facing keel gives
the dark band under each hem (geometry, one needle colour). Below the top skirt
each cone stops at a collar hidden inside the skirt above, so the tier parts are
domed skirts that re-stack exactly into the hero and no triangles are spent inside
the canopy. The hero's 7 hems form the sheet's 4 tiers (TopTip, Tier3/2/1 = an
inner and an outer hem). The two hems of a tier share one yaw, so the inner
leaf lies on the outer one (one ring of 8 big two-layer leaves per tier), and
each tier turns half a tip from the tier above, so the top view is a layered
star of distinct rings. Leaves are broad, overlapping, blunt spades (a second
narrower edge pair near the tip). Under every skirt a shallow downward cone
(the shaded underside) closes the hem.

Colour: ONE palette key per material (its lit mid-tone); the studio / Roblox sun
shades the facets. All needles (flaps, shoulders, undersides) are w04_needle: the
dark band under every hem is the downward-facing hem underside in shadow. Bark is
w04_bark everywhere; its grooves and fluting are geometry. Cut ends are
w04_wood_end, soil w04_ground, tufts w04_grass, rocks kit_rock. Tints are only a
small random grey variation (the exporter reads Tint.r).

Grass-tuft faces carry the face attribute kit_nocollide = 1 (walk-through dressing).
No VFX: the reference shows no fire, glow or water.
"""

import math
import random

import bmesh
from mathutils import Matrix, Vector

SUBJECT = "ClassicPine"
ROW = 1
PALETTE = {
    "w04_needle": ("#5E8E1A", 0.8, 0, 0),
    "w04_bark": ("#9A6038", 0.9, 0, 0),
    "w04_wood_end": ("#E4A458", 0.85, 0, 0),
    "w04_ground": ("#DCC9A0", 0.95, 0, 0),
    "w04_grass": ("#8DB83A", 0.9, 0, 0),
    # "kit_rock": ("#A89C9C", 0.9, 0, 0),  # Existing KIT_PALETTE key (used as-is; the runner only accepts w04_-prefixed keys here): the pale grey faceted rocks/pebbles at every tree base.
}

CAT = "Kit W04 ClassicPine"
# The sheet lights its trees from the right (dark teal left flanks). The studio
# sun comes from the front-left, so the hero and variants are viewed from the
# front-right, where the sun-shaded flank and the hem undersides show as on the sheet.
HERO_AZIMUTH = 22
SIDE_AZIMUTH = -90  # the side cell from the sunlit left, lit like the sheet's side view (the tree is radially symmetric)
NEEDLE_TINT = 0.8  # per-tree uniform for every needle face (sheet note: darken if the render looks washed out vs the reference); +/-4% random
TAU = 2 * math.pi
Z = Vector((0, 0, 1))
NEEDLE, BARK, ROCK, GRASS, GROUND, WOODEND = 1, 2, 4, 5, 6, 7
DEFAULT_MAT = {NEEDLE: "w04_needle", BARK: "w04_bark", ROCK: "kit_rock",
               GRASS: "w04_grass", GROUND: "w04_ground", WOODEND: "w04_wood_end"}


def _smooth01(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def polar(r, th, z, c=(0.0, 0.0)):
    return Vector((c[0] + r * math.cos(th), c[1] + r * math.sin(th), z))


# ---------------------------------------------------------------------------
# Asset plumbing: a face family + shade layer, painted at the end
# ---------------------------------------------------------------------------


def new_asset(kit, name, seed):
    a = kit.flintkit.Asset(name, CAT, seed=seed)
    lay = a.bm.faces.layers
    # all layers before any geometry: adding a layer reallocates the faces
    lay.int.new("w04_fam")
    lay.float.new("w04_sh")
    lay.int.new("kit_nocollide")
    a.kit = kit
    return a


def mark(a, faces, fam, sh=1.0, mat=None, dressing=False):
    bm = a.bm
    lf = bm.faces.layers.int["w04_fam"]
    ls = bm.faces.layers.float["w04_sh"]
    ln = bm.faces.layers.int["kit_nocollide"]
    mi = a._mi(mat or DEFAULT_MAT[fam])
    for f in faces:
        if f is None:
            continue
        f[lf] = fam
        f[ls] = sh
        f[ln] = 1 if dressing else 0
        f.material_index = mi
        f.smooth = False
        for lp in f.loops:
            lp[a.tint_layer] = (1.0, 1.0, 1.0, 1.0)
    return faces


def new_face(bm, verts):
    out = []
    for v in verts:
        if not out or out[-1] is not v:
            out.append(v)
    if len(out) > 1 and out[0] is out[-1]:
        out.pop()
    if len(out) < 3:
        return None
    try:
        return bm.faces.new(out)
    except ValueError:
        return None


def relight(a):
    """Small random Tint variation only (+/-5%), never by face direction, height
    or tier. Light and shadow come from the renderer (studio / Roblox sun)."""
    bm = a.bm
    lf = bm.faces.layers.int["w04_fam"]
    rng = a.rng
    for f in bm.faces:
        k = f[lf]
        if not k:
            continue
        var = {NEEDLE: 0.04, BARK: 0.04, ROCK: 0.04, GRASS: 0.05, GROUND: 0.02, WOODEND: 0.03}[k]
        # one uniform base per material (not by direction): the classic pine's
        # needles sit a touch deeper than the swatch, like the sheet's mid green
        base = NEEDLE_TINT if k == NEEDLE else 1.0
        # five discrete levels per material, so the Roblox palette row stays small
        t = round(base * (1.0 + var * rng.choice((-1.0, -0.5, 0.0, 0.5, 1.0))), 4)
        for lp in f.loops:
            lp[a.tint_layer] = (t, t, t, 1.0)


def finish(a):
    relight(a)
    used = sorted({f.material_index for f in a.bm.faces})
    remap = {old: new for new, old in enumerate(used)}
    for f in a.bm.faces:
        f.material_index = remap[f.material_index]
    a.mats = [a.mats[i] for i in used]
    lay = a.bm.faces.layers
    lay.int.remove(lay.int["w04_fam"])
    lay.float.remove(lay.float["w04_sh"])
    for v in a.bm.verts:
        if v.co.z < 0.0:
            v.co.z = 0.0
    zmin = min(v.co.z for v in a.bm.verts)
    return a.finish(), zmin


# ---------------------------------------------------------------------------
# Needle skirts (lobby pine_tier(), with a hidden collar instead of a tall apex)
# ---------------------------------------------------------------------------


RIDGE = 0.24    # shoulder (leaf root) radius / R, hidden under the skirt above
BEND_U = 0.55  # the ridge bends here (radius / R): a flat-spreading inner leaf, drooping tip
BEND_Z = 0.85  # ridge height at the bend (x drop above the tips): an almost straight, outward-pointing leaf
EDGE_U = 0.62  # where the leaf is widest (radius / R): broad diamond leaves
LEAF_W = 0.34  # half-width of a leaf at its widest (x R): big chunky leaves that overlap their neighbours
EDGE2_U = 0.89  # a second, narrower edge pair near the tip: a blunt spade, a scalloped hem
EDGE2_W = 0.45  # its half-width (x the widest half-width)
FOLD = 0.38    # leaf edges sit this much (x half-width) below the ridge: ~32 deg halves, flat two-tone flaps
NOTCH = 0.45   # notch radius / R: a short valley near the hub, so leaves read as separate kites
NOTCH_Z = 0.75  # notch height above the tips (x drop): a shaded valley between leaves, so each ring reads as separate star points
KEEL = 1.7     # each leaf's underside keel sits this far (studs) below its edges ...
KEEL_K = 0.15  # ... plus this much x drop
KEEL_R = 0.84  # keel radius / R: a deep, steep (~45 deg down) underside under the leaf's outer half
CEIL = 0.2     # underside apex below the tips (studs)


def skirt(a, zt, R, tips, drop, yaw, upper=None, apex=None, c=(0.0, 0.0), rfun=None,
          zfun=None, jag=0.04, tuck=0.35):
    """One needle skirt: a ring of `tips` broad folded flaps (pine_tier style).

    Along each tip axis the flap runs straight down from a raised shoulder
    (RIDGE*R, zt+drop) to the tip (R, zt), so it hangs like a long tongue; its
    edges bow out sideways (BULGE) and fall away from that ridge, so each flap is
    one broad spade folded along its length (two big facets per side). Between
    flaps a deep notch (NOTCH*R) sits 0.7*drop above the tips. Under each flap a keel runs from the
    tip edge down and in to (KEEL_R*R, zt-KEEL): a steep downward-facing face that
    sits in the shade of the hem, so the dark band under every hem is geometry.
    Above the shoulders the cone climbs to a collar hidden inside the skirt
    above (upper = (zt, R, drop) of that skirt); the top skirt rises to `apex`.
    rfun(th) / zfun(th) scale the radius and lift the skirt per direction."""
    bm = a.bm
    # seeded by the skirt itself, so a tier part rebuilds exactly the hero's skirt
    rng = random.Random(int(zt * 1000) * 31 + tips * 7 + int(R * 100))
    n = tips
    if upper:
        zu, Ru, du = upper
        # the shoulder tucks inside the skirt above (never pokes through it): the
        # visible flap length is the hem spacing plus that overlap
        # (an outer hem under its own tier's inner hem may tuck in deeper)
        drop = min(drop, zu + tuck * du - zt)
        # a low collar just over the shoulders, inside the skirt above (over its
        # underside), so a tier part is a low, wide dome
        # (and above the skirt above's underside apex, CEIL below its tips)
        zcol = max(zt + drop + 0.35, zu - CEIL + 0.3)
        rcol = 0.6 * RIDGE * R
    tip, sho, bend, notch, keel, col, eL, eR, fL, fR = [], [], [], [], [], [], [], [], [], []
    rid, bz, ridge_d = RIDGE, BEND_Z, drop
    if not upper:
        # the Top Tip: straight kite leaves running from just under the apex to the
        # tips, so from above it is the sheet's bright 8-point star of broad leaves
        rid = 0.1
        bz = (1 - BEND_U) / (1 - rid)
        ridge_d = apex - zt - 0.35

    def ridge_z(u, d):
        """Ridge height above the tip at radius fraction u: shoulder -> bend -> tip."""
        if u <= BEND_U:
            return d + (bz * d - d) * (u - rid) / (BEND_U - rid)
        return bz * d * (1 - u) / (1 - BEND_U)

    for k in range(n):
        th = yaw + TAU * k / n + rng.uniform(-0.025, 0.025)
        thn = yaw + TAU * (k + 0.5) / n
        rm, rmn = (rfun(th), rfun(thn)) if rfun else (1.0, 1.0)
        dz, dzn = (zfun(th), zfun(thn)) if zfun else (0.0, 0.0)
        Rk = R * rm
        rt = Rk * (1 + rng.uniform(-jag, jag))
        d = ridge_d * rng.uniform(0.92, 1.08) if upper else ridge_d
        ztk = zt + dz
        ax = Vector((math.cos(th), math.sin(th), 0.0))
        side = Vector((-ax.y, ax.x, 0.0))  # +theta
        o = Vector((c[0], c[1], ztk))
        tip.append(bm.verts.new(o + ax * rt))
        sho.append(bm.verts.new(o + ax * (rid * Rk) + Vector((0, 0, d))))
        bend.append(bm.verts.new(o + ax * (BEND_U * Rk) + Vector((0, 0, ridge_z(BEND_U, d)))))
        # the leaf's widest point: edges pushed out sideways and folded down from
        # the ridge, so each leaf is a broad spade with two strongly angled halves
        w = LEAF_W * Rk * rng.uniform(0.94, 1.06)
        ze = ridge_z(EDGE_U, d) - FOLD * w
        w2 = EDGE2_W * w
        ze2 = ridge_z(EDGE2_U, d) - FOLD * w2
        for sgn, out, out2 in ((-1.0, eL, fL), (1.0, eR, fR)):
            out.append(bm.verts.new(o + ax * (EDGE_U * Rk) + side * (sgn * w) + Vector((0, 0, ze))))
            out2.append(bm.verts.new(o + ax * (EDGE2_U * Rk) + side * (sgn * w2) + Vector((0, 0, ze2))))
        # the keel hangs steeply under the leaf's outer half: its faces look out and
        # ~45 deg down, so the sun misses them and they read as the dark hem band
        keel.append(bm.verts.new(o + ax * (KEEL_R * Rk) + Vector((0, 0, min(ze, ze2) - KEEL - KEEL_K * drop))))
        notch.append(bm.verts.new(polar(NOTCH * R * rmn, thn, zt + dzn + NOTCH_Z * drop, c)))
        if upper:
            col.append(bm.verts.new(polar(rcol * rm, th, zcol + 0.5 * dz, c)))
    if upper:
        top_v = bm.verts.new((c[0], c[1], zcol + 0.25))
    else:
        top_v = bm.verts.new((c[0], c[1], apex))
    # the underside is a shallow downward cone (its apex CEIL below the tips): it
    # faces down, so it reads as the dark band under the hem
    centre = bm.verts.new((c[0], c[1], zt - CEIL))
    faces = []
    for k in range(n):
        j = (k + 1) % n
        p = (k - 1) % n
        # folded leaf (upper side): fold along the ridge, bent at the bend so
        # the inner leaf spreads out and the tip droops
        faces += [new_face(bm, (sho[k], notch[p], eL[k])), new_face(bm, (sho[k], eL[k], bend[k])),
                  new_face(bm, (bend[k], eL[k], fL[k])), new_face(bm, (bend[k], fL[k], tip[k])),
                  new_face(bm, (sho[k], bend[k], eR[k])), new_face(bm, (bend[k], fR[k], eR[k])),
                  new_face(bm, (bend[k], tip[k], fR[k])), new_face(bm, (sho[k], eR[k], notch[k]))]
        # keel under the leaf (faces out and steeply down): the dark hem band
        faces += [new_face(bm, (tip[k], fL[k], keel[k])), new_face(bm, (fL[k], eL[k], keel[k])),
                  new_face(bm, (eL[k], notch[p], keel[k])),
                  new_face(bm, (tip[k], keel[k], fR[k])), new_face(bm, (fR[k], keel[k], eR[k])),
                  new_face(bm, (eR[k], keel[k], notch[k]))]
        # underside ceiling, fanned to the axis
        faces += [new_face(bm, (centre, notch[k], keel[k])), new_face(bm, (centre, keel[j], notch[k]))]
        if upper:
            # cone from the shoulders up into the skirt above, closed by a low dome
            faces += [new_face(bm, (col[k], sho[k], notch[k])), new_face(bm, (col[k], notch[k], col[j])),
                      new_face(bm, (col[j], notch[k], sho[j])), new_face(bm, (top_v, col[k], col[j]))]
        else:
            faces += [new_face(bm, (top_v, sho[k], notch[k])), new_face(bm, (top_v, notch[k], sho[j]))]
    # One needle colour for every face: the dark band under the hem is the
    # downward-facing keel in the hem's shade, not paint.
    mark(a, faces, NEEDLE)


def canopy_spec(H, W, bottoms, widths, tips, droop_k=0.34, droop0=0.4, groups=None, yaw0=0.0):
    """Skirt list (top first): dicts of zt, R, tips, drop, yaw, upper/apex.
    bottoms = height of each hem's tip points (fraction of H); widths = hem
    width (fraction of W). groups = tier id per skirt: the hems of one tier keep
    the same yaw (their flaps hang in line), and each new tier turns half a tip,
    so the top view is a layered star of big points. Default: every skirt turns."""
    groups = groups or list(range(len(bottoms)))
    R = [w * W / 2 for w in widths]
    drp = [droop0 + droop_k * r for r in R]
    zt = [b * H for b in bottoms]
    # Each tier turns half a tip from the tier above, and the hems of one tier keep
    # the same yaw: the inner hem's leaf lies on its outer hem's leaf, so a tier
    # reads as ONE ring of 8 big two-layer leaves and the top view is a layered
    # star of distinct rings (not a 16-point fan).
    tier_ids = sorted(set(groups), key=groups.index)
    last = len(tier_ids) - 1
    out = []
    for i in range(len(zt)):
        t = tier_ids.index(groups[i])
        half = math.pi / tips[i]
        yaw = yaw0 + (last - t) * half
        sk = dict(zb=zt[i], R=R[i], tips=tips[i], droop=drp[i], yaw=yaw)
        if i == 0:
            sk["apex"] = H
        else:
            sk["upper"] = (zt[i - 1], R[i - 1], drp[i - 1])
            if groups[i] == groups[i - 1]:
                sk["tuck"] = 0.7  # outer hem: its shoulders hide under the inner hem
        out.append(sk)
    return out


def cluster_tier(a, sk, c=(0.0, 0.0), rfun=None, zfun=None, jag=0.0, tuck=0.0):
    """A tier's inner layer as one shared leaf_cluster: a low, chunky star dome of
    8 broad lobes that bulges out between the pointed flaps of the tier above and
    the tier's own outer hem, so each tier reads as dense, layered needle mass."""
    fk = a.kit.flintkit
    zt, R = sk["zb"], sk["R"]
    zu = sk["upper"][0] if sk.get("upper") else zt + sk["droop"]
    h = zu - zt + 0.15
    ox = 0.0
    if rfun:  # lopsided tier (Asymmetric): push the dome toward the heavy side
        ox = 0.5 * R * (rfun(math.pi) - rfun(0.0)) * -0.5
    seed = int(zt * 1000) * 13 + int(R * 100)
    verts = a.leaf_cluster((R * 0.92, R * 0.92, h), loc=(c[0] + ox, c[1], zt - 0.35), mat="w04_needle",
                           lobes=sk["tips"], squash=1.0, facets=2, depth=1.0, rough=0.06,
                           seed=seed, floor=zt - 0.45)
    mark(a, fk._faces_of(verts), NEEDLE)


def add_skirts(a, specs, **kw):
    for sk in specs:
        if sk.get("cluster"):
            cluster_tier(a, sk, **{**kw, **sk.get("kw", {})})
            continue
        skirt(a, sk["zb"], sk["R"], sk["tips"], sk["droop"], sk["yaw"], upper=sk.get("upper"),
              apex=sk.get("apex"), tuck=sk.get("tuck", 0.35), **{**kw, **sk.get("kw", {})})


def canopy_core_z(specs, i):
    """Height on the axis that sits inside skirt i (for hiding a trunk end)."""
    return specs[i]["zb"] + 0.3 * specs[i]["droop"] + 0.2


# ---------------------------------------------------------------------------
# Trunk, roots, branch stub (lobby trunk()/roots())
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


def trunk(a, pts, radii, sides=9, flare=(), lobes=5, lobe_amp=0.6, grooves=3,
          groove_depth=0.12, twist=0.12, rough=0.03, caps=(False, False), phase=None):
    """Faceted fluted trunk/branch tube; `flare` = per-ring buttress strength from
    the base. Grooves are pulled-in vertex columns (geometry). Returns the rings."""
    bm = a.bm
    pts = [Vector(p) for p in pts]
    frames = _frames(pts)
    phase = a.rng.uniform(0, TAU) if phase is None else phase
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
            r *= 1 + a.rng.uniform(-rough, rough)
            ring.append(bm.verts.new(pts[i] + r * (math.cos(th) * nrm + math.sin(th) * bi)))
        rings.append(ring)
    body = []
    for i in range(len(rings) - 1):
        r1, r2 = rings[i], rings[i + 1]
        for j in range(sides):
            k = (j + 1) % sides
            body.append(bm.faces.new((r1[j], r1[k], r2[k], r2[j])))
    if caps[0]:
        body.append(bm.faces.new(list(reversed(rings[0]))))
    if caps[1]:
        body.append(bm.faces.new(rings[-1]))
    mark(a, body, BARK)  # grooves are pulled-in vertices, shaded by the sun
    return rings


def cut_top(a, ring, inset=0.8, sink=0.04):
    """Flat sawn end on a ring: a pale w04_wood_end rim and a slightly darker,
    slightly sunken heartwood disc (solid, no charcoal)."""
    bm = a.bm
    c = sum((v.co for v in ring), Vector()) / len(ring)
    inn = [bm.verts.new(c + (v.co - c) * inset - Vector((0, 0, sink))) for v in ring]
    n = len(ring)
    rimf = [new_face(bm, (ring[i], ring[(i + 1) % n], inn[(i + 1) % n], inn[i])) for i in range(n)]
    disc = new_face(bm, inn)
    mark(a, rimf + [disc], WOODEND)


def bezier(p0, p1, p2, n):
    p0, p1, p2 = Vector(p0), Vector(p1), Vector(p2)
    return [(1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2
            for t in (i / (n - 1) for i in range(n))]


def roots(a, trunk_r, n, reach, height, r0, phase=0.0, c=(0.0, 0.0)):
    """Buttress roots: thick tapering tubes arcing from the lower trunk out and
    down into the ground."""
    base = Vector((c[0], c[1], 0))
    for k in range(n):
        az = phase + TAU * k / n + a.rng.uniform(-0.22, 0.22)
        rk = reach * a.rng.uniform(0.85, 1.08)
        top = base + polar(trunk_r * 0.3, az, height * a.rng.uniform(0.85, 1.08))
        mid = base + polar(trunk_r * 1.05, az, height * 0.32)
        end = base + polar(rk, az, -0.12)
        trunk(a, bezier(top, mid, end, 5), [r0, r0 * 0.9, r0 * 0.7, r0 * 0.48, r0 * 0.28],
              sides=6, grooves=0, rough=0.05, twist=0.0, caps=(False, True))


TRUNK_ZS = (0.0, 0.5, 1.2, 2.0)            # the buttressed foot (shared by RootFoot)
TRUNK_FOOT = (1.45, 1.22, 1.08, 1.0)        # radius factors of those rings
TRUNK_FLARE = (1.0, 0.6, 0.3, 0.1)       # buttress lobe strength per ring
# 16 sides, every other column pulled in: 8 deep vertical flutes that read at cell size
TRUNK_KW = dict(sides=16, lobes=5, lobe_amp=0.75, grooves=8, groove_depth=0.26, twist=0.03)


def tree_trunk(a, r, z_top, z_hem, c=(0.0, 0.0), lean=(0.0, 0.0), phase=0.35):
    """Main trunk from the ground into the canopy (open top, hidden in the skirts):
    a stout bulging fluted column, buttress-lobed at the foot. Ten sides with every
    other column pulled in = five flutes (geometry)."""
    zs = list(TRUNK_ZS) + [0.6 * z_hem, z_hem, (z_hem + z_top) / 2, z_top]
    radii = [r * f for f in TRUNK_FOOT] + [r * 0.93, r * 0.86, r * 0.72, r * 0.55]
    pts = [(c[0] + lean[0] * z, c[1] + lean[1] * z, z) for z in zs]
    return trunk(a, pts, radii, flare=TRUNK_FLARE, phase=phase, **TRUNK_KW)


# ---------------------------------------------------------------------------
# Base dressing: rocks, grass tufts, soil patch
# ---------------------------------------------------------------------------


def rock(a, x, y, sx, sy, sz, rot=0.0):
    fk = a.kit.flintkit
    verts = a.rock((sx, sy, sz), loc=(x, y, 0.0), rot=(0, 0, rot), mat="kit_rock", subdiv=2,
                   rough=0.1, facets=16, sink=0.12)
    mark(a, fk._faces_of(verts), ROCK)


def soil(a, R, n=18, c=(0.0, 0.0), thick=0.1, squash=1.0):
    """Thin irregular soil disc: a soft bevelled rim and a flat top (no hidden bottom)."""
    bm = a.bm
    rng = a.rng
    ph = [rng.uniform(0, TAU) for _ in range(3)]
    outer, inn = [], []
    for k in range(n):
        th = TAU * k / n
        rr = R * (1 + 0.1 * math.sin(2 * th + ph[0]) + 0.06 * math.sin(3 * th + ph[1])
                  + rng.uniform(-0.05, 0.05))
        p = Vector((c[0] + rr * math.cos(th), c[1] + rr * math.sin(th) * squash, 0.0))
        outer.append(bm.verts.new(p))
        inn.append(bm.verts.new(Vector((c[0], c[1], 0)) + (p - Vector((c[0], c[1], 0))) * 0.9
                                + Vector((0, 0, thick))))
    faces = [new_face(bm, (outer[k], outer[(k + 1) % n], inn[(k + 1) % n], inn[k])) for k in range(n)]
    faces.append(new_face(bm, inn))
    mark(a, faces, GROUND)


def blade(a, base, d0, L, W, mat, curl=0.6, segs=3, thick=0.03, fold=0.25):
    """Closed, V-folded low-poly grass blade that droops outward along its length."""
    bm = a.bm
    d = Vector(d0).normalized()
    sa = d.cross(Z)
    if sa.length < 1e-4:
        sa = Vector((1, 0, 0))
    sa.normalize()
    c = Vector(base)
    step = L / segs
    top, bot, lft, rgt = [], [], [], []
    for k in range(segs + 1):
        t = k / segs
        w = W * (1 - t) ** 0.8 if k < segs else 0.0
        u = sa.cross(d).normalized()
        if w < 1e-4:
            v = bm.verts.new(c)
            top.append(v); bot.append(v); lft.append(v); rgt.append(v)
        else:
            top.append(bm.verts.new(c + u * thick))
            bot.append(bm.verts.new(c - u * thick))
            lft.append(bm.verts.new(c + sa * w + u * fold * w))
            rgt.append(bm.verts.new(c - sa * w + u * fold * w))
        if k < segs:
            c = c + d * step
            d = (Matrix.Rotation(-curl / segs, 3, sa) @ d).normalized()
    faces = []
    for k in range(segs):
        faces.append(new_face(bm, (top[k], lft[k], lft[k + 1], top[k + 1])))
        faces.append(new_face(bm, (top[k], top[k + 1], rgt[k + 1], rgt[k])))
        faces.append(new_face(bm, (bot[k], bot[k + 1], lft[k + 1], lft[k])))
        faces.append(new_face(bm, (bot[k], rgt[k], rgt[k + 1], bot[k + 1])))
    faces.append(new_face(bm, (top[0], bot[0], lft[0])))
    faces.append(new_face(bm, (bot[0], top[0], rgt[0])))
    mark(a, faces, GRASS, mat=mat, dressing=True)


def tuft(a, x, y, s=1.0, n=8, leafy=False):
    s *= 1.4  # the sheet's tufts stand ~1.5-2.5 studs tall
    rng = a.rng
    az0 = rng.uniform(0, TAU)
    if leafy:
        # a chunky lime clump (shared leaf_cluster) with a few blades poking out
        verts = a.leaf_cluster((0.62 * s, 0.62 * s, 0.75 * s), loc=(x, y, 0.0), mat="w04_grass",
                               lobes=6, squash=1.0, facets=1, depth=1.0, floor=0.0)
        mark(a, a.kit.flintkit._faces_of(verts), GRASS, dressing=True)
        n = 4
    for k in range(n):
        az = az0 + TAU * k / n + rng.uniform(-0.3, 0.3)
        centre_blade = k == 0
        pitch = math.radians(rng.uniform(78, 88) if centre_blade else rng.uniform(50, 72))
        d = Vector((math.cos(pitch) * math.cos(az), math.cos(pitch) * math.sin(az), math.sin(pitch)))
        base = Vector((x, y, 0.0)) + polar(0.12 * s, az, 0.0)
        if leafy:
            L = s * rng.uniform(1.5, 2.2)
            W = s * rng.uniform(0.26, 0.34)
        else:
            L = s * rng.uniform(1.1, 1.8) * (1.2 if centre_blade else 1.0)
            W = s * rng.uniform(0.12, 0.17)
        blade(a, base, d, L, W, "w04_grass", curl=rng.uniform(0.4, 0.8), segs=3 if leafy else 2)


def dress(a, rocks, tufts, patch_r, patch_c=(0.0, 0.0), squash=1.0):
    soil(a, patch_r, c=patch_c, squash=squash)
    for r in rocks:
        rock(a, *r)
    for t in tufts:
        tuft(a, *t)


# ---------------------------------------------------------------------------
# Hero layout
# ---------------------------------------------------------------------------

H, W = 24.0, 15.0  # spec: ~24 tall; upper tiers ~6-13 wide, the lowest skirt ~17
# Measured on the sheet's front cell: top hem at ~0.83 H (spire ~3.8 studs), the
# lowest hem tips at ~0.29 H; below the Top Tip the hems come in tier pairs (an
# inner hem ~1.1 studs above the outer one, ~3 studs between tiers) and the
# outline is convex (upper tiers widen fast). Top skirt first; heights = hem tips.
HERO_BOTTOMS = [0.78, 0.6, 0.43, 0.27]
# each tier's inner hem barely wider than the outer hem above (tucked under it), so
# the outline steps out hard at every tier under a visible overhang
HERO_WIDTHS = [0.34, 0.62, 0.82, 1.0]  # the lowest tier spreads wide (overhanging skirt)
HERO_TIPS = [8, 8, 8, 8]
HERO_TRUNK_R = 1.75   # ~2.9 dia under the canopy, ~6.5 dia across the buttresses
# Big grey rocks close in against the roots, mostly front and left (the sheet's two
# big front-left boulders), one smaller at the front-right.
# Two of them sit out at ~radius 7.5 on the left and right, peeking past the
# canopy in the top view as on the sheet.
HERO_ROCKS = [(-5.9, -5.0, 2.9, 2.5, 2.0, 0.4), (6.3, -4.3, 2.5, 2.1, 1.7, 1.1),
              (4.2, 6.6, 2.3, 2.0, 1.6, 0.2)]
# 6 bright clumps, the bigger ones leafy (the sheet's tufts are fist-sized bushes)
HERO_TUFTS = [(-7.4, -1.6, 1.1, 8, True), (0.4, -7.0, 1.0, 7, True), (7.4, 0.8, 1.15, 7, True),
              (-4.4, 5.6, 1.0, 7, True), (1.0, 7.2, 0.9), (-2.6, -5.6, 0.9)]


HERO_GROUPS = [0, 1, 2, 3]   # TopTip, Tier3, Tier2, Tier1 (the parts)
# The whole canopy turns a quarter leaf (22.5 deg), so from the front-right hero
# camera a bottom leaf tip sits on each side of the silhouette (full width), and
# the front view sees the star a little narrower, as on the sheet.
HERO_YAW = math.pi / 8


def hero_specs():
    return canopy_spec(H, W, HERO_BOTTOMS, HERO_WIDTHS, HERO_TIPS, groups=HERO_GROUPS, yaw0=HERO_YAW)


def build_hero(kit, specs):
    a = new_asset(kit, "ClassicPine", 401)
    add_skirts(a, specs)
    tree_trunk(a, HERO_TRUNK_R, canopy_core_z(specs, -3), specs[-1]["zb"])
    roots(a, HERO_TRUNK_R, 6, 5.2, 3.6, 1.25, phase=0.35)
    dress(a, HERO_ROCKS, HERO_TUFTS, 8.4)
    return finish(a)[0]


def build_tier(kit, name, specs, seed):
    a = new_asset(kit, name, seed)
    add_skirts(a, specs)
    return finish(a)


def build_trunk_part(kit):
    a = new_asset(kit, "ClassicPineTrunk", 411)
    # the hero's column from the RootFoot's 2-stud cut up to just under the canopy
    r = HERO_TRUNK_R
    zs = [0.0, 1.5, 3.0, 4.5, 6.0, 7.5]
    radii = [r * 1.0, r * 0.95, r * 0.9, r * 0.85, r * 0.8, r * 0.75]  # ~1.75 -> ~1.3: a clear taper
    kw = {**TRUNK_KW, "lobes": 5}
    rings = trunk(a, [(0, 0, z) for z in zs], radii, caps=(True, False), phase=0.35, **kw)
    cut_top(a, rings[-1])
    o = finish(a)[0]
    o["kit_shading_ok"] = "cut top is w04_wood_end heartwood, a distinct material from the w04_bark sides"
    return o


def build_root_foot(kit):
    a = new_asset(kit, "ClassicPineRootFoot", 412)
    # the hero's buttressed foot, cut flat at 2 studs
    r = HERO_TRUNK_R
    rings = trunk(a, [(0, 0, z) for z in TRUNK_ZS], [r * f for f in TRUNK_FOOT],
                  flare=TRUNK_FLARE, phase=0.35, **TRUNK_KW)
    cut_top(a, rings[-1])
    roots(a, r, 6, 5.0, 1.8, 1.1, phase=0.35)
    # the hero's base dressing: rocks ringed just outside the lowest skirt
    dress(a, HERO_ROCKS, HERO_TUFTS[:5], 8.2)
    o = finish(a)[0]
    o["kit_shading_ok"] = "cut top is w04_wood_end heartwood, a distinct material from the w04_bark roots"
    return o


# ---------------------------------------------------------------------------
# Variants
# ---------------------------------------------------------------------------


def build_tall_narrow(kit):
    Ht, Wt = 26.0, 11.0
    bottoms = [0.84, 0.71, 0.58, 0.46, 0.35, 0.25]
    widths = [0.3, 0.5, 0.64, 0.77, 0.89, 1.0]
    tips = [8] * 6
    specs = canopy_spec(Ht, Wt, bottoms, widths, tips, droop_k=0.45)
    a = new_asset(kit, "ClassicPineTallNarrow", 421)
    add_skirts(a, specs)
    tree_trunk(a, 1.05, canopy_core_z(specs, -3), specs[-1]["zb"], phase=0.9)
    roots(a, 1.05, 5, 3.0, 1.9, 0.72, phase=0.9)
    dress(a, [(-3.4, -1.0, 1.8, 1.6, 1.2, 0.3), (2.6, -2.2, 1.4, 1.2, 0.9, 1.0),
              (3.2, 1.8, 1.2, 1.1, 0.8, 0.4)],
          [(-2.2, -2.4, 0.9), (1.0, -2.8, 0.7), (-3.6, 1.4, 0.8), (3.8, -0.4, 0.9, 6, True),
           (0.6, 3.0, 0.7)], 4.6)
    return finish(a)[0]


def build_short_wide(kit):
    Hs, Ws = 16.0, 17.0
    # 5 broad hems as 4 stepped tiers (the bottom tier doubled), high enough
    # that the short, thick trunk shows under the canopy
    bottoms = [0.78, 0.6, 0.45]
    widths = [0.4, 0.72, 1.0]
    tips = [8] * 3
    specs = canopy_spec(Hs, Ws, bottoms, widths, tips, droop_k=0.4)
    a = new_asset(kit, "ClassicPineShortWide", 431)
    add_skirts(a, specs)
    tree_trunk(a, 1.9, canopy_core_z(specs, -2), specs[-1]["zb"], phase=0.1)
    roots(a, 1.9, 5, 4.5, 2.4, 1.15, phase=0.1)
    dress(a, [(-5.2, -1.2, 2.2, 1.9, 1.4, 0.5), (0.4, -4.4, 1.8, 1.6, 1.1, 1.2),
              (5.0, 1.8, 2.0, 1.7, 1.3, 0.1), (-2.8, 3.8, 1.2, 1.1, 0.8, 2.0)],
          [(-2.8, -3.2, 1.0), (2.4, -3.4, 0.8), (4.8, -1.6, 1.1, 6, True), (-5.0, 1.4, 0.9),
           (2.0, 3.8, 0.8), (-5.2, -0.4, 0.7)], 5.6)
    return finish(a)[0]


def build_asymmetric(kit):
    Ha, Wa = 21.0, 12.6
    bottoms = [0.8, 0.64, 0.48, 0.33]
    widths = [0.3, 0.58, 0.8, 1.0]
    tips = [8] * 4
    specs = canopy_spec(Ha, Wa, bottoms, widths, tips)
    nsk = len(specs)
    for i, sk in enumerate(specs):
        low = i / (nsk - 1)  # 0 top .. 1 bottom
        drift = 1.4 * (1 - low)  # the tip drifts toward +X
        heavy = 0.1 + 0.26 * low  # lower skirts lopsided toward -X
        lift = 1.6 * low ** 2  # lower hems hang a little low on -X, ride up on +X
        sk["kw"] = dict(c=(drift - 0.5 * low, 0.0),
                        rfun=(lambda th, h=heavy: 1.0 - h * math.cos(th)),
                        zfun=(lambda th, l=lift: l * math.cos(th)))
    a = new_asset(kit, "ClassicPineAsymmetric", 441)
    add_skirts(a, specs)
    tree_trunk(a, 1.3, canopy_core_z(specs, -2), specs[-1]["zb"], lean=(0.02, 0.0), phase=0.6)
    roots(a, 1.3, 5, 3.4, 2.1, 0.85, phase=0.6)
    # broken branch stub (~1.3 thick, ~3.5 long) jutting from the exposed +X side of
    # the trunk, mostly sideways (seen in profile from the front-right camera) and a
    # little toward the front, so its pale heartwood break still shows
    stub = trunk(a, [(0.5, -0.1, 3.0), (2.1, -0.5, 3.55), (3.7, -0.95, 4.15)], [0.8, 0.72, 0.68],
                 sides=7, grooves=0, rough=0.04, twist=0.0)
    end = stub[-1]
    for v in end:
        v.co += Vector((a.rng.uniform(-0.12, 0.12), 0, a.rng.uniform(-0.1, 0.1)))
    cut_top(a, end, inset=0.72, sink=0.1)
    dress(a, [(-4.4, -1.2, 1.9, 1.7, 1.2, 0.5), (4.0, 1.6, 2.2, 1.9, 1.6, 0.2),
              (0.2, -3.8, 1.4, 1.2, 0.9, 1.1), (2.6, -2.8, 1.0, 0.9, 0.7, 0.6)],
          [(-2.6, -2.8, 0.9), (1.8, -3.2, 0.8), (-4.6, 1.2, 0.9), (4.8, -1.0, 1.0, 6, True),
           (1.4, 3.4, 0.8)], 5.8)
    return finish(a)[0]


# ---------------------------------------------------------------------------


def build(kit):
    specs = hero_specs()
    hero = kit.tag(build_hero(kit, specs), "hero", collision="hull", budget=5000,
                   notes="grass-tuft faces carry kit_nocollide=1 (walk-through dressing)")
    out = [hero]
    tiers = [("ClassicPineTopTip", specs[0:1]), ("ClassicPineCanopyTier3", specs[1:2]),
             ("ClassicPineCanopyTier2", specs[2:3]), ("ClassicPineCanopyTier1", specs[3:4])]
    for i, (name, sk) in enumerate(tiers):
        obj, z0 = build_tier(kit, name, sk, 402 + i)
        out.append(kit.tag(obj, "part", collision="hull", budget=1500,
                           notes=f"re-stacks into ClassicPine with its origin at z={z0:.2f} "
                                 f"on the trunk axis"))
    out.append(kit.tag(build_trunk_part(kit), "part", collision="hull", budget=800,
                       notes="sits on ClassicPineRootFoot's 2-stud cut; tiers stack on it"))
    out.append(kit.tag(build_root_foot(kit), "part", collision="hull", budget=1500,
                       notes="cut flat at z=2 (w04_wood_end); tuft faces kit_nocollide=1"))
    out.append(kit.tag(build_tall_narrow(kit), "variant", collision="hull", budget=6000,
                       notes="grass-tuft faces carry kit_nocollide=1"))
    out.append(kit.tag(build_short_wide(kit), "variant", collision="hull", budget=5000,
                       notes="grass-tuft faces carry kit_nocollide=1"))
    out.append(kit.tag(build_asymmetric(kit), "variant", collision="hull", budget=5000,
                       notes="lopsided canopy (heavy -X), broken branch stub; tufts kit_nocollide=1"))
    return out
