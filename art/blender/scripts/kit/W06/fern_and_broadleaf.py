"""W06 row 2: FERN AND BROADLEAF, lush jungle-edge undergrowth.

Hero "FernAndBroadleaf" (~7 x 6 x 5.5 studs): a full rosette of 12 large
pinnate fern fronds springing from one root crown, spread evenly round 360
degrees with graded pitch: a tall near-vertical V whose tips arch over, a ring
arching out at 55-62 degrees past the rocks, and front fronds whose tips droop.
3 lighter yellow-green broad kite leaves hang low among the front fronds on
short rising stems. Base: a low dark soil mound, brown root nubs, a ring
of flattish grey boulders and two moss tufts.

Parts: FernFrondLarge / FernFrondMedium / FernFrondSmall (one frond each,
lying along +X with the face tilted to the -Y viewer, scaled to 4.5 / 3.2 /
2.2 studs long), FernRootCluster (stump knob with splayed roots) and
BroadLeafSingle (one kite leaf on a short stem, 2.6 long).
Variants: UprightFern (narrow vase), SpreadFern (low star, lime young fronds at the centre), BroadleafCluster
(three tiers of broad leaves with green fronds behind).

Technique: every leaf is a "sheet": a 2D outline in (u along the midrib, v
across) laid on a bent centreline (start angle th0, drooping by `droop`
towards the tip), V-folded along the midrib (w = fold * |v|) and thickened
into a thin slab (top, bottom and side walls). Fronds have a bare stem then
n blunt saw-tooth pinnae per side whose notches cut ~75% of the way to the
midrib; broad leaves are an angular kite (shoulders near the stem, widest
~40% along, pointed tip) built from big triangles with kinked edge vertices.
One base colour per material; light and shade come from the lighting.
"""

import math

import bmesh
from mathutils import Vector

SUBJECT = "FernAndBroadleaf"
ROW = 2
PALETTE = {
    # Fern fronds (row 2): the deep blue-green of the reference fronds. The sheet plan gave #4E8C2C, but
    # that rendered a medium yellow-green with weak contrast to the lime broad leaves (verifier fail), so
    # the base is darkened to the reference fronds' mid-tone. Only this module uses w06_fern.
    "w06_fern": ("#2F7A33", 0.8, 0, 0),
    "w06_broadleaf": ("#8EC22C", 0.8, 0, 0),  # Broad single leaves (row 2): a lighter yellow-green plant species than the fern. Assets that hold both w06_fern and w06_broadleaf set obj['kit_two_tone_ok'] = 'fern fronds and broad leaves are two different plant species'.
    "w06_moss": ("#ACC722", 0.9, 0, 0),  # Moss cushions and moss tufts (row 4 mainly, small tufts at the base of rows 1-3): the bright yellow-green of sheet swatch 3.
    "w06_stone": ("#B1ADA9", 0.9, 0, 0),  # Light warm-grey stone: ruin wall blocks (rows 3-4), vine attachment pads, the RockCap boulder and the small base rocks around bushes and ferns (sheet swatch 4). One key; facets do the shading.
    "w06_bark": ("#8D6237", 0.9, 0, 0),  # Brown woody material: bush branch stems and trunks, fern root clusters, vine and ivy stems/tendrils (sheet swatch 5).
    "w06_soil": ("#6E4B2B", 0.95, 0, 0),  # Dark earth mounds under the ferns and bushes and around vine/ivy roots on the ground. Small patches only.
}

FERN, BROAD, STONE, BARK, SOIL, MOSS = ("w06_fern", "w06_broadleaf", "w06_stone", "w06_bark",
                                        "w06_soil", "w06_moss")
TWO_TONE = "fern fronds and broad leaves are two different plant species"
Z = Vector((0, 0, 1))
D = math.radians


# ---------------------------------------------------------------------------
# Asset plumbing
# ---------------------------------------------------------------------------


def new_asset(kit, name, seed=None):
    return kit.flintkit.Asset(name, f"Kit {kit.sheet} {kit.subject}", seed=seed, tint_var=0.05)


def done(kit, a, role, collision, budget=None, notes="", caption=None, two_tone=False):
    """Flatten anything below the ground, drop faces lying on it (never seen),
    then finish and tag."""
    bm = a.bm
    for v in bm.verts:
        if v.co.z < 0:
            v.co.z = 0.0
    flat = [f for f in bm.faces if all(v.co.z < 0.002 for v in f.verts) and f.normal.z < -0.5]
    if flat:
        bmesh.ops.delete(bm, geom=flat, context="FACES_ONLY")
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
    obj = a.finish()
    if caption:
        obj["kit_caption"] = caption
    if two_tone:
        obj["kit_two_tone_ok"] = TWO_TONE
    return kit.tag(obj, role, collision=collision, budget=budget, notes=notes)


def fit_long(a, target):
    """Scale the whole asset about the origin so its X extent is `target`."""
    xs = [v.co.x for v in a.bm.verts]
    s = target / (max(xs) - min(xs))
    for v in a.bm.verts:
        v.co *= s


# ---------------------------------------------------------------------------
# Bent centreline + thickened 2D sheets
# ---------------------------------------------------------------------------


class Curve:
    """Centreline of a leaf: starts at `base` heading out along azimuth `az`
    (radians) at `th0` above horizontal, the angle falling by `droop` towards
    the tip (most of it near the tip). `roll` turns the blade about its axis."""

    def __init__(self, base, az, th0, droop, length, roll=0.0, exp=1.6, steps=40):
        self.base = Vector(base)
        self.h = Vector((math.cos(az), math.sin(az), 0))
        self.side = Z.cross(self.h).normalized()  # horizontal, to the blade's left
        self.th0, self.droop, self.L, self.exp, self.roll = th0, droop, length, exp, roll
        self.tab = [(0.0, 0.0, 0.0)]  # (u, x along h, z)
        du = length / steps
        x = z = 0.0
        for i in range(steps):
            th = self.theta((i + 0.5) * du)
            x += math.cos(th) * du
            z += math.sin(th) * du
            self.tab.append(((i + 1) * du, x, z))

    def theta(self, u):
        s = min(max(u / self.L, 0.0), 1.0)
        return self.th0 - self.droop * s ** self.exp

    def at(self, u):
        """Point, tangent, width axis and face normal at arc length u."""
        u = min(max(u, -0.3 * self.L), 1.2 * self.L)
        th = self.theta(u)
        T = math.cos(th) * self.h + math.sin(th) * Z
        if u <= 0:
            x, z = self.tab[0][1] + math.cos(th) * u, self.tab[0][2] + math.sin(th) * u
        elif u >= self.L:
            x, z = self.tab[-1][1] + math.cos(th) * (u - self.L), self.tab[-1][2] + math.sin(th) * (u - self.L)
        else:
            k = min(int(u / self.L * (len(self.tab) - 1)), len(self.tab) - 2)
            u0, x0, z0 = self.tab[k]
            u1, x1, z1 = self.tab[k + 1]
            f = (u - u0) / (u1 - u0)
            x, z = x0 + (x1 - x0) * f, z0 + (z1 - z0) * f
        P = self.base + self.h * x + Z * z
        S = self.side
        N = T.cross(S)
        if self.roll:
            S = S * math.cos(self.roll) + N * math.sin(self.roll)
            N = T.cross(S)
        return P, T, S.normalized(), N.normalized()


def sheet(a, curve, verts2d, polys, fold=0.0, thick=0.07, mat=FERN, tint=None):
    """Lay a 2D outline (u, v, extra lift) on the curve and thicken it."""
    bm = a.bm
    top, bot = [], []
    for (u, v, wx) in verts2d:
        P, T, S, N = curve.at(u)
        c = P + S * v + N * (fold * abs(v) + wx)
        top.append(bm.verts.new(c + N * thick / 2))
        bot.append(bm.verts.new(c - N * thick / 2))
    used = {}
    for poly in polys:
        area = 0.0
        for i in range(len(poly)):
            u1, v1, _ = verts2d[poly[i]]
            u2, v2, _ = verts2d[poly[(i + 1) % len(poly)]]
            area += u1 * v2 - u2 * v1
        if area < 0:
            poly = list(reversed(poly))
        bm.faces.new([top[i] for i in poly])
        bm.faces.new([bot[i] for i in reversed(poly)])
        for i in range(len(poly)):
            e = (poly[i], poly[(i + 1) % len(poly)])
            used.setdefault(frozenset(e), []).append(e)
    for es in used.values():
        if len(es) == 1:
            i, j = es[0]
            bm.faces.new((top[i], bot[i], bot[j], top[j]))
    return a._finish(top + bot, mat, tint)


def frond(a, curve, n, half_w, stem_frac=0.12, fold=0.22, thick=0.13, notch=0.24, mat=FERN, tint=None):
    """Pinnate fern frond along `curve` (its length): bare stem, n blunt pinnae
    per side (notches cut to `notch` x the local half width), pointed tip."""
    L = curve.L
    V, P = [], []

    def add(u, v, w=0.0):
        V.append((u, v, w))
        return len(V) - 1

    u0, u_end = stem_frac * L, 0.92 * L

    def width(u):
        t = min(max((u - u0) / (L - u0), 0.0), 1.0)
        return half_w * math.sin(math.pi * (0.22 + 0.78 * t)) ** 0.7

    stem_r = 0.06 * half_w + 0.035
    M = [add(0, 0)]
    R = [add(0, stem_r)]
    Lf = [add(0, -stem_r)]
    st = [u0 + (u_end - u0) * i / n for i in range(n + 1)]
    for i, u in enumerate(st):
        r = max(stem_r * 0.9, notch * width(u)) if i else stem_r
        M.append(add(u, 0))
        R.append(add(u, r))
        Lf.append(add(u, -r))
    # the rachis is one flat strip (R..Lf); the pinnae fold up from its edges (w = fold * |v|)
    for k in range(len(M) - 1):
        P.append((Lf[k], R[k], R[k + 1], Lf[k + 1]))
    for i in range(n):
        k = i + 1  # index into M/R/Lf (0 is the stem base)
        d = st[i + 1] - st[i]
        W = width(st[i] + d / 2)
        r = V[R[k]][1]
        sweep = 0.5 * (W - r)
        for sgn, side in ((1, R), (-1, Lf)):
            # a pointed leaflet swept towards the tip: shoulders at ~half width, a sharp point
            # at full width, and a wide V notch down to the rachis before the next leaflet
            if i == n - 1:  # the tiny leaflet by the tip is a plain point
                t2 = add(st[i] + 0.5 * d + sweep, sgn * 0.9 * W)
                P.append((side[k], t2, side[k + 1]))
                continue
            t1 = add(st[i] + 0.02 * d + 0.3 * sweep, sgn * 0.68 * W)
            t2 = add(st[i] + 0.60 * d + sweep, sgn * 1.00 * W)
            t3 = add(st[i] + 0.76 * d + 0.5 * sweep, sgn * 0.58 * W)
            P.append((side[k], t1, t2, t3, side[k + 1]))
    tip = add(L, 0)
    P.append((Lf[-1], R[-1], tip))
    return sheet(a, curve, V, P, fold=fold, thick=thick, mat=mat, tint=tint)


# kite outline: (u fraction, v fraction, lift fraction) for the right edge; the left edge mirrors v
KITE_R = ((0.40, 1.00, 0.14), (0.72, 0.56, -0.08))
KITE_L = ((0.38, 1.00, -0.10), (0.70, 0.58, 0.10))
KITE_M = (0.0, 0.2, 0.5, 0.8)
SHOULDER = ((0.08, 0.62, -0.08), (0.07, 0.6, 0.06))  # right, left: (u, v, lift) fractions


def kite_blade(a, curve, blade, half_w, fold=0.26, kink=1.0, thick=0.15, mat=BROAD, tint=None,
               shoulder=False):
    """Angular kite leaf blade along `curve`: 6-vertex outline, pointed at the
    stem, widest ~40% along, a second corner at ~70% and a pointed tip; a centre
    crease and kinked edge corners break each half into big triangular facets.
    `shoulder` adds a corner near the stem on each side (8-vertex spade-kite)."""
    V = []

    def add(u, v, w=0.0):
        V.append((u, v, w))
        return len(V) - 1

    m = [add(f * blade, 0) for f in KITE_M]
    tip = add(blade, 0)
    P = []
    for k, (sgn, edge) in enumerate(((1, KITE_R), (-1, KITE_L))):
        e = [add(f * blade, sgn * vf * half_w, lf * kink * half_w) for f, vf, lf in edge]
        if shoulder:
            fu, fv, fl = SHOULDER[k]
            s = add(fu * blade, sgn * fv * half_w, fl * kink * half_w)
            P += [(m[0], s, m[1]), (m[1], s, e[0])]
        else:
            P += [(m[0], e[0], m[1])]
        P += [(m[1], e[0], m[2]), (m[2], e[0], e[1]), (m[2], e[1], m[3]), (m[3], e[1], tip)]
    return sheet(a, curve, V, P, fold=fold, thick=thick, mat=mat, tint=tint)


def taper_tube(a, pts, radii, sides, mat, cap_end=True, tint=None):
    """Faceted tube with per-point radius along a 3D polyline."""
    bm = a.bm
    pts = [Vector(p) for p in pts]
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        up = Z if abs(t.z) < 0.9 else Vector((1, 0, 0))
        nx = t.cross(up).normalized()
        ny = nx.cross(t).normalized()
        r = radii[i]
        ring = [bm.verts.new(p + r * (math.cos(2 * math.pi * j / sides) * nx +
                                      math.sin(2 * math.pi * j / sides) * ny)) for j in range(sides)]
        rings.append(ring)
    for r1, r2 in zip(rings, rings[1:]):
        for j in range(sides):
            bm.faces.new((r1[j], r2[j], r2[(j + 1) % sides], r1[(j + 1) % sides]))
    if cap_end:
        bm.faces.new(rings[-1])
    return a._finish([v for r in rings for v in r], mat, tint)


# ---------------------------------------------------------------------------
# Clump assembly
# ---------------------------------------------------------------------------


def pinnae_for(L):
    # fewer, bigger blunt lobes on the clump fronds (the reference's lobes are big and swept)
    return 7 if L >= 3.9 else 6


def add_frond(a, az, L, th0, droop, roll=0.0, r=0.25, z=0.45, n=None, hw=None, exp=1.3, mat=FERN):
    azr = D(az)
    base = (r * math.cos(azr), r * math.sin(azr), z)
    # fronds turn their faces partly outward/forward, as fronds do, not flat to the sky
    # (front/back fronds roll too, so the side view sees their faces rather than their edges)
    roll = roll + 35 * math.cos(azr) + 16 * math.sin(azr)
    c = Curve(base, azr, D(th0), D(droop), L, roll=D(roll), exp=exp)
    # narrow blades (~0.34 L across) with distinct lobes, as the reference's fronds
    return frond(a, c, n or pinnae_for(L), hw or 0.17 * L, notch=0.3, mat=mat)


def add_leaf(a, P, az, blade, th0, droop, hw=0.85, roll=0.0, stem_r=0.07, crown_z=0.4, fold=0.2):
    """Broad leaf: a faceted stem rising from the crown to P, then a kite blade
    leaving P along azimuth `az`."""
    azr = D(az)
    P = Vector(P)
    base = Vector((0.18 * math.cos(azr), 0.18 * math.sin(azr), crown_z))
    mid = base.lerp(P, 0.55) + Vector((0, 0, 0.15 * (P - base).length))
    c = Curve(P, azr, D(th0), D(droop), blade, roll=D(roll), exp=1.2)
    taper_tube(a, [base, mid, P, c.at(0.12)[0]], [stem_r * 1.15, stem_r, stem_r * 0.9, stem_r * 0.8], 5, BROAD)
    return kite_blade(a, c, blade, hw, fold=fold, shoulder=True)


def boulder(a, size, loc, rz, sink=0.35):
    """Flattish, irregular chiselled boulder, partly buried; one stone colour,
    default small random tint only."""
    w, d, h = size
    r = (w / 2, d / 2, h / 2)
    c = (loc[0], loc[1], r[2] * (1 - sink))
    a.ico(r, loc=c, rot=(D(a.rng.uniform(-12, 12)), D(a.rng.uniform(-12, 12)), D(rz)), mat=STONE,
          subdiv=1, jitter=0.24, facets=12)


def base_dressing(a, soil, rocks, moss=(), roots=5, crown=0.42, root_az0=0.4, sink=0.35):
    """Soil mound, root crown with nubs, boulders and moss tufts."""
    sx, sy, sz = soil
    # a sloped dome cap: the ellipsoid's centre sits below ground so no vertical equator shows
    a.ico((sx, sy, sz * 1.8), loc=(0, 0, -sz * 0.8), mat=SOIL, subdiv=1, jitter=0.04, facets=4)
    a.cyl(crown, crown * 0.7, 0.6, 6, mat=BARK, jitter=0.04)
    for k in range(roots):
        ang = 2 * math.pi * k / roots + root_az0
        c, s = math.cos(ang), math.sin(ang)
        p0 = Vector((crown * 0.6 * c, crown * 0.6 * s, 0.45))
        p1 = Vector(((crown + 0.55) * c, (crown + 0.55) * s, sz + 0.12))
        p2 = Vector(((crown + 1.25) * c, (crown + 1.25) * s, sz * 0.3))
        taper_tube(a, [p0, p1, p2], [0.17, 0.14, 0.07], 5, BARK)
    for (x, y, w, d, h, rz) in rocks:
        boulder(a, (w, d, h), (x, y), rz, sink=sink)
    for (x, y, s) in moss:
        # lumpy multi-lobed moss tuft (shared leaf_cluster helper), flat on the ground
        a.leaf_cluster(s, loc=(x, y, s * 0.35), mat=MOSS, lobes=5, squash=0.6, floor=0.0)


def build_hero(kit):
    a = new_asset(kit, "FernAndBroadleaf")
    base_dressing(
        a, soil=(2.2, 2.0, 0.5), root_az0=D(-60), sink=0.2,
        # big chunky boulders in a ring at r ~2.3 (biggest on the left flank)
        rocks=[(-2.55, -0.45, 2.4, 1.95, 1.9, 20), (-1.35, -2.15, 1.8, 1.55, 1.3, -25),
               (-2.1, 1.35, 1.8, 1.55, 1.35, 40), (0.9, -2.3, 1.5, 1.3, 1.05, 10),
               (2.6, -0.4, 2.2, 1.8, 1.65, -15), (1.95, 1.5, 1.7, 1.45, 1.25, 30)],
        moss=[(-0.25, -2.4, 0.5), (1.75, -1.85, 0.42), (-2.5, -1.4, 0.4)])
    # (az, length, th0, droop, exp): an even 360-degree rosette, balanced front/back for a symmetric
    # vase from the side. Back/flank fronds rise steeply and arch out; the front fronds are lower and
    # spread wide so the big broad leaves sit above them.
    for az, L, th0, dr, ex in [(60, 5.5, 84, 66, 2.2), (120, 5.5, 84, 66, 2.2), (90, 5.0, 84, 66, 2.1),
                               (30, 4.7, 66, 74, 1.8), (150, 4.7, 66, 74, 1.8),
                               (0, 4.3, 56, 72, 1.8), (180, 4.3, 56, 72, 1.8),
                               (-30, 4.3, 62, 74, 1.8), (210, 4.3, 62, 74, 1.8),
                               (-62, 4.5, 66, 72, 1.9), (-118, 4.5, 66, 72, 1.9), (-90, 4.0, 50, 66, 1.7)]:
        add_frond(a, az, L, th0, dr, exp=ex, n=5 if L < 4.5 else 6)
    # 3 lime young fronds unfurling at the centre (lime tissue, like the reference's light centre)
    for az, L, th0, dr in [(100, 2.8, 84, 50), (-20, 2.6, 78, 56), (200, 2.6, 78, 56)]:
        add_frond(a, az, L, th0, dr, exp=1.8, r=0.12, z=0.5, n=4, mat=BROAD)
    # 5 big lime pointed-oval leaves (~3 long x 2 wide) on stems topping at z 2.5-3 round the front
    # half, tilted out and up above the low front fronds so they show from the front and the top
    for P, az, bl, th0, dr in [((0.0, -0.9, 2.9), -90, 3.2, 22, 50),
                               ((-0.95, -0.6, 2.7), -138, 3.1, 20, 48),
                               ((0.95, -0.6, 2.7), -42, 3.1, 20, 48),
                               ((-1.0, 0.2, 2.5), -178, 2.6, 18, 48),
                               ((1.0, 0.2, 2.5), 2, 2.6, 18, 48)]:
        add_leaf(a, P, az, bl, th0, dr, hw=1.0, roll=20 * math.cos(D(az)), fold=0.2, stem_r=0.09)
    return done(kit, a, "hero", "none", budget=3500, two_tone=True,
                notes="Walk-through undergrowth: no collision. 12 fern fronds in an even 360-degree rosette, 3 lime "
                      "young fronds at the centre and 5 big broad pointed-oval leaves raised round the front, on a "
                      "soil mound with 5 root nubs, 6 boulders and 3 moss tufts. No VFX.")


def build_parts(kit):
    out = []
    for name, cap, L, n, budget in [("FernFrondLarge", "Fern Frond (large)", 4.5, 9, 300),
                                    ("FernFrondMedium", "Fern Frond (medium)", 3.2, 7, 250),
                                    ("FernFrondSmall", "Fern Frond (small)", 2.2, 5, 200)]:
        a = new_asset(kit, name)
        hw = 0.215 * L  # broad chunky blade (rev 4: +15%)
        # lies along +X rising diagonally then arching over, face turned toward the -Y viewer
        # (kept fairly low so the auto-laid parts cell does not stack tall fronds over the others)
        c = Curve((0, 0, hw * 0.85 + 0.05), 0.0, D(26), D(30), L, roll=D(58), exp=1.3)
        frond(a, c, n, hw, notch=0.3, fold=0.14)
        fit_long(a, L)
        out.append(done(kit, a, "part", "none", budget=budget, caption=cap,
                        notes="Single pinnate fern frond, stem end at the origin, face to -Y; rotate and "
                              "plant in a root crown to kit-bash a fern."))
    a = new_asset(kit, "FernRootCluster")
    a.cyl(0.42, 0.4, 1.15, 7, mat=BARK, jitter=0.04)
    for k in range(5):
        ang = 2 * math.pi * k / 5 + 0.3 + a.rng.uniform(-0.15, 0.15)
        c, s = math.cos(ang), math.sin(ang)
        # each root bulges out of the knob, arches and runs splayed along the ground
        taper_tube(a, [(0.22 * c, 0.22 * s, 0.85), (0.55 * c, 0.55 * s, 0.55), (0.8 * c, 0.8 * s, 0.2),
                       (1.05 * c, 1.05 * s, 0.07)], [0.22, 0.2, 0.13, 0.07], 5, BARK)
    out.append(done(kit, a, "part", "hull", budget=400, caption="Root Cluster (base)",
                    notes="Stump-like root crown with 5 splayed roots; sits under a fern clump."))
    a = new_asset(kit, "BroadLeafSingle")
    c = Curve((0.32, 0, 0.42), 0.0, D(20), D(34), 2.35, roll=D(34), exp=1.2)
    taper_tube(a, [(0, 0, 0.06), (0.32, 0, 0.42), c.at(0.2)[0]], [0.08, 0.07, 0.06], 5,
               BROAD)
    kite_blade(a, c, 2.35, 0.84)
    fit_long(a, 2.6)
    out.append(done(kit, a, "part", "none", budget=150, caption="Broad Leaf (single)",
                    notes="One faceted kite/spade leaf on a short stem, stem end at the origin."))
    return out


def build_upright(kit):
    a = new_asset(kit, "UprightFern")
    base_dressing(a, soil=(2.0, 1.8, 0.45), root_az0=D(-50), roots=4,
                  rocks=[(-1.7, -0.9, 1.1, 0.9, 0.65, 15), (1.5, -1.1, 1.0, 0.85, 0.6, -20),
                         (-0.2, -1.8, 0.8, 0.7, 0.5, 30), (1.6, 0.7, 0.9, 0.75, 0.55, 0)],
                  moss=[(0.6, -1.8, 0.25)])
    # a vase: steep fronds that open outward at the top and droop their tips, gaps between them
    # steep fronds with only a slight droop so the tips stop ~2.5 from the axis (~5 wide)
    for az, L, th0, dr in [(24, 5.3, 88, 48), (156, 5.3, 88, 48), (90, 4.8, 85, 44),
                           (-62, 3.6, 62, 56), (-118, 3.6, 62, 56),
                           (45, 4.2, 76, 54), (135, 4.2, 76, 54), (-10, 3.6, 72, 60), (190, 3.6, 72, 60),
                           (-140, 3.2, 70, 58)]:
        add_frond(a, az, L, th0, dr, r=0.2, hw=0.18 * L)
    # lime centre: 4 narrow lime leaves rising steeply through the middle to ~75-90% of the height
    for P, az, bl, th0, dr in [((0.0, -0.4, 2.6), -90, 2.4, 70, 34), ((-0.35, 0.05, 2.5), 175, 2.3, 70, 36),
                               ((0.35, 0.05, 2.5), 5, 2.3, 70, 36), ((0.0, 0.35, 2.8), 90, 2.2, 78, 30)]:
        add_leaf(a, P, az, bl, th0, dr, hw=0.7, stem_r=0.08)
    return done(kit, a, "variant", "none", budget=3000, two_tone=True, caption="A. Upright Fern",
                notes="Narrow vase fern: 10 steep fronds round 4 lime leaves rising through the centre, soil + "
                      "small rocks. No collision.")


def build_spread(kit):
    a = new_asset(kit, "SpreadFern")
    base_dressing(a, soil=(1.6, 1.5, 0.4), roots=4, root_az0=D(-45),
                  rocks=[(-1.3, -1.2, 0.8, 0.7, 0.45, 10), (1.3, -1.0, 0.7, 0.6, 0.4, -25),
                         (0.2, -1.6, 0.6, 0.55, 0.35, 0)],
                  moss=[(-0.6, -1.6, 0.22)])
    for i in range(10):
        az = -90 + 36 * i + 18
        add_frond(a, az, 3.8 if i % 2 else 3.5, 44 if i % 2 else 50, 62, (i % 3 - 1) * 6, r=0.25, z=0.35, n=6)
    # young fronds unfurling at the centre are a lighter lime than the mature outer ring
    # (the reference's spread fern reads lime in the middle); the broad-leaf lime is that colour
    for az, L, th0, dr in [(95, 3.3, 74, 62), (-90, 3.2, 66, 66), (15, 3.0, 66, 64), (165, 3.0, 66, 64)]:
        add_frond(a, az, L, th0, dr, 0, r=0.15, z=0.42, n=5, mat=BROAD)
    obj = done(kit, a, "variant", "none", budget=3000, caption="B. Spread Fern",
               notes="Low star of 10 near-horizontal mature fronds + 4 lighter young fronds rising at the "
                     "centre, small mound. No broad leaves. No collision.")
    obj["kit_two_tone_ok"] = ("young unfurling fronds at the centre are a lighter lime tissue than the mature "
                              "outer fronds, as the reference's spread fern shows")
    return obj


def build_cluster(kit):
    a = new_asset(kit, "BroadleafCluster")
    base_dressing(a, soil=(2.2, 2.0, 0.5), root_az0=D(-30), roots=4,
                  rocks=[(-1.9, -0.8, 1.2, 1.0, 0.7, 10), (1.8, -1.0, 1.1, 0.9, 0.65, -20),
                         (0.3, -2.0, 0.9, 0.8, 0.55, 30), (-1.2, 1.3, 0.9, 0.8, 0.55, 0)],
                  moss=[(-0.8, -2.0, 0.25)])
    # green fronds behind the leaves
    # dark fronds behind and between the leaves
    for az, L, th0, dr in [(62, 4.3, 78, 52), (118, 4.3, 78, 52), (92, 4.6, 84, 40), (150, 3.8, 58, 66),
                           (20, 3.8, 58, 66), (-35, 3.4, 50, 62), (215, 3.4, 50, 62)]:
        add_frond(a, az, L, th0, dr, r=0.2, n=6)
    # a tall central lime leaf (~4.5 high) and two tiers of big broad leaves round it
    add_leaf(a, (0.0, -0.2, 2.4), -90, 2.6, 82, 26, hw=0.95, stem_r=0.1)
    for P, az, bl, th0, dr in [((-0.35, -0.6, 0.9), -105, 2.8, 8, 50), ((0.35, -0.6, 0.9), -75, 2.8, 8, 50),
                               ((-0.9, -0.15, 0.85), -165, 2.6, 4, 44), ((0.9, -0.15, 0.85), -15, 2.6, 4, 44),
                               ((-0.6, -0.35, 1.8), -130, 2.6, 34, 54), ((0.6, -0.35, 1.8), -50, 2.6, 34, 54)]:
        add_leaf(a, P, az, bl, th0, dr, hw=0.95)
    return done(kit, a, "variant", "none", budget=3000, two_tone=True, caption="C. Broadleaf Cluster",
                notes="A tall central broad leaf over 6 big broad leaves in 2 tiers, 7 dark fern fronds behind "
                      "and between, soil + rocks. No collision.")


def build(kit):
    return [build_hero(kit), *build_parts(kit), build_upright(kit), build_spread(kit), build_cluster(kit)]
