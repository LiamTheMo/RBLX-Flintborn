"""W01 row 3: ROCK CLUSTER, three interlocking boulders (independent meshes).

Hero "RockCluster" (~12 x 10 x 9 studs): a tall, chunky, blunt-topped boulder
(A) standing behind a broad front-left boulder (C) and a low, wide, flat-topped
one (B). Each carries a thin moss drape on its top; bright clover mounds fill
the crevices between the boulders (partway up the joins) and band the front of
the base, with white daisies and tiny rubble stones.

Parts: RockClusterA / RockClusterB / RockClusterC, each boulder alone with its
moss (and, as in the reference, a moss streak or a small clover tuft), centred
on the boulder so it rotates and snaps around the rock when kit-bashing.
Variants: RockClusterLinear (in a row), RockClusterCrescent (curved arc, open to
the front), RockClusterTriangular (compact).

Technique: each boulder is a half-space intersection (chisel cuts): a block cut
by a tilted top plane (the flat crown), a ring of steep walls at the widest
girth, a staggered ring of upper bevels, a ring of shoulder chamfers running
from the plateau rim down to the walls and a few tucked base facets. Every face
is one large crisp plane with hard ridges (~20-28 faces, ~70-90 tris). Its
buried bottom cap is removed, and faces hidden inside a neighbouring boulder
are culled. Moss caps are lobed (star-outlined) pads ray-cast onto the top so
they fold over the rim, with a rosette of round moss leaves on them and a few
leaves spilling over the edge; A also has two lobed drips down its facets.
Clover clumps are rosettes of cupped round leaves on short stems (an outer ring
fanned out, a middle tier tilted up, one crowning leaf) over a small hidden
core. Join clumps sit on the lower boulder's shoulder where the taller one's
flank rises out of it, draped onto the rock union by ray casts. Colours are one
base colour per material with a small random Tint (a few quantised levels);
light and shadow come from the lighting, never from paint.

Collision: 'hull' (solid rocks). The exporter makes one solid piece per asset,
so the foliage is kept within ~0.8-1 stud of the boulders' girth and off their
backs, which keeps the hull close to the rocks.
"""

import math
import random

import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

SUBJECT = "RockCluster"
ROW = 3
PALETTE = {
    "w01_rock": ("#B29F98", 0.9, 0, 0),  # THE ONLY stone colour on the whole sheet: warm mauve-beige granite of every boulder, spire, cluster rock, slab and pebble (lit mid-tone; median of all rock pixels across the 4 hero cells is #B29F96-#B5A097). The swatches' blue-grey (#8E8E9E) and pale beige (#CAB2A8) are its shadow and lit sides, NOT materials: drop w01_boulder_beige, w01_boulder_blue, w01_rock_light, w01_rock_cool, w01_rock_warm, kit_rock(_light/_dark) and stone. Same value in every module that declares it (this replaces the old #8E7C78). Variety only via a small random Tint (<=1.25x spread), never by face direction.
    "w01_moss": ("#ADBB14", 0.9, 0, 0),  # Lime-yellow moss: moss caps, moss pads, streaks/smudges and thin decals on rock facets (median moss pixel #ADBB08; swatches 3 #8DA418 and 4 #D7CD29 are its shadow and lit sides). Replaces moss, moss_light, moss_dark.
    "w01_leaf": ("#7AAB1E", 0.8, 0, 0),  # Clover / round-leaf ground clumps banked at rock feet and in crevices: a greener, slightly deeper green than the moss so the two read apart. Replaces leaf, leaf_light and grass_light on this sheet (one key for all leafy clumps).
    # flower_white #F5F2EA (daisy petals) and flower_yellow #F2C230 (daisy
    # centres) are existing flintkit PALETTE keys, used as they are.
}

Z = Vector((0, 0, 1))
ROCK, MOSS, LEAF = "w01_rock", "w01_moss", "w01_leaf"  # one key per material

# The three boulders. size = full extents (x, y, z) in studs; n = hull points
# (facet count ~ 2n); c = height of the widest girth above the ground (as a
# fraction of the vertical semi-axis); taper narrows the upper half; p = the
# super-ellipsoid exponent (higher = squarer); flat = where the top is pressed
# flat (fraction of the raw height); tilt = slope of that top plane (x, y);
# tuck = base ring radius as a fraction of the girth.
ROCKS = {
    # A: tall chunky block, near-vertical walls, broad flat-ish crown
    "A": dict(size=(6.3, 6.5, 9.4), seed=3101, sides=7, wall=(-4, 6), pivot=0.35, plateau=(0.5, 0.6),
              upper=(16, 26), shoulder=(38, 50), low=3, tilt=(0.03, -0.04), lean=(-0.03, 0.02),
              moss=[dict(at=(0.15, -0.2), R=(2.0, 1.85), thick=0.32, spill=5, lobes=7),
                    dict(dir=(-0.85, -0.5, 0.0), h=0.86, R=(0.55, 1.5), thick=0.16, side=True, lobes=5),
                    dict(dir=(0.35, -1.0, 0.0), h=0.87, R=(0.6, 0.95), thick=0.15, side=True, lobes=4)]),
    # B: low, wide, flat-topped
    "B": dict(size=(6.0, 5.0, 4.2), seed=3102, sides=7, wall=(0, 12), pivot=0.3, plateau=(0.5, 0.62),
              upper=(24, 36), shoulder=(44, 58), low=3, tilt=(0.0, -0.04), lean=(0.0, 0.0),
              moss=[dict(at=(0.1, 0.0), R=(1.5, 1.3), thick=0.26, spill=3, lobes=6)]),
    # C: broad front boulder, sloping shoulders, smaller plateau
    "C": dict(size=(7.7, 6.8, 5.5), seed=3103, sides=7, wall=(0, 12), pivot=0.3, plateau=(0.42, 0.55),
              upper=(22, 34), shoulder=(40, 54), low=3, tilt=(0.04, -0.03), lean=(0.015, 0.0),
              moss=[dict(at=(-0.5, -0.3), R=(1.7, 1.4), thick=0.26, spill=4, lobes=6),
                    dict(dir=(-0.95, -0.3, 0.0), h=0.5, R=(0.8, 1.4), thick=0.14, side=True, lobes=5)]),
}


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------


def paint(a, faces, mat, tint=1.0, var=0.0):
    mi = a._mi(mat)
    for f in faces:
        f.material_index = mi
        f.smooth = False
        t = tint * (1.0 + a.rng.uniform(-var, var)) if var else tint
        t = round(t / 0.025) * 0.025  # a few Tint levels keep the Roblox palette rows small
        for lp in f.loops:
            lp[a.tint_layer] = (t, t, t, 1.0)


def hull_bm(points):
    """Convex hull of points as a new bmesh (interior/unused points dropped)."""
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


def emit(a, bm, style):
    """Copy a temp bmesh (already in asset space) into the asset.
    style(face, normal) -> (palette key, tint)."""
    bm.normal_update()
    vmap = {v: a.bm.verts.new(v.co) for v in bm.verts}
    out = []
    for f in bm.faces:
        mat, t = style(f, f.normal)
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
        th = phase + 2 * math.pi * (k + rng.uniform(-0.3, 0.3)) / m
        s = 1 + rng.uniform(-jit, jit)
        pts.append(Vector((cx + math.cos(th) * rx * s, cy + math.sin(th) * ry * s, z)))
    return pts


class Solid:
    """A placed convex boulder (asset space): its planes for inside tests."""

    def __init__(self, bm):
        bm.normal_update()
        self.planes = [(f.normal.copy(), f.normal.dot(f.verts[0].co)) for f in bm.faces]

    def inside(self, p, pad=0.03):
        return p.z > pad and all(n.dot(p) - d < -pad for n, d in self.planes)


# ---------------------------------------------------------------------------
# Boulders
# ---------------------------------------------------------------------------


def chisel(bm, n, p):
    """Cut the convex solid by the plane through p with outward normal n,
    capping the cut with one flat n-gon (a crisp chisel plane)."""
    n = Vector(n).normalized()
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-4,
                           plane_co=Vector(p), plane_no=n, clear_outer=True)
    open_e = [e for e in bm.edges if len(e.link_faces) == 1]
    if open_e:
        bmesh.ops.edgeloop_fill(bm, edges=open_e)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.03)
    bmesh.ops.dissolve_degenerate(bm, dist=0.03, edges=bm.edges[:])


def rock_bm(size, seed, sides=7, wall=(0, 10), pivot=0.35, plateau=(0.5, 0.6), shoulder=(38, 52),
            low=2, tilt=(0.0, 0.0), lean=(0.0, 0.0), upper=(18, 30)):
    """Chunky chisel-faceted boulder: a half-space intersection. A block is cut
    by a tilted top plane (the flat crown), `sides` steep walls around the
    girth, `sides` shoulder chamfers between the walls (from the plateau rim
    down to the walls) and `low` base tucks, so every face is one large crisp
    plane with hard ridges (~16-20 faces, ~60-80 tris). Rescaled to exactly
    `size`; the (never seen) bottom cap is removed. Returns (bm, shape)."""
    rng = random.Random(seed)
    rx, ry, h = size[0] / 2, size[1] / 2, size[2]
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * rx * 3, v.co.y * ry * 3, (v.co.z + 0.5) * h * 1.6))

    def sup(th):
        return math.hypot(rx * math.cos(th), ry * math.sin(th))

    def dirn(th, el):
        e = math.radians(el)
        return Vector((math.cos(th) * math.cos(e), math.sin(th) * math.cos(e), math.sin(e)))

    chisel(bm, (tilt[0], tilt[1], 1.0), (0, 0, h))
    ph = rng.uniform(0, 2 * math.pi)
    step = 2 * math.pi / sides
    # tiers of planes round the girth, staggered by half a step tier to tier so
    # the facets meet in diamond/triangle ridges (the classic chiselled rock):
    # (elevation range deg, pivot height, radius range, azimuth offset)
    tiers = ((wall, pivot, (0.96, 1.02), 0.0),  # steep main walls at the widest girth
             (upper, pivot + (1 - pivot) * 0.45, (0.92, 0.97), 0.5),  # upper bevels
             (shoulder, 1.0, plateau, 0.0))  # shoulder chamfers from the plateau rim
    for el, zf, rr, off in tiers:
        for i in range(sides):
            th = ph + step * (i + off + rng.uniform(-0.18, 0.18))
            r = sup(th) * rng.uniform(*rr)
            chisel(bm, dirn(th, rng.uniform(*el)), (math.cos(th) * r, math.sin(th) * r, h * zf))
    for i in range(low):  # tucked base facets
        th = ph + step * (i * sides / max(1, low) + 0.5 + rng.uniform(-0.3, 0.3))
        r = sup(th) * rng.uniform(0.95, 0.99)
        chisel(bm, dirn(th, rng.uniform(-34, -22)), (math.cos(th) * r, math.sin(th) * r, h * 0.14))
    # rescale to the exact size, centred, then lean (a shear keeps the planes flat)
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    kx, ky, kz = 2 * rx / (max(xs) - min(xs)), 2 * ry / (max(ys) - min(ys)), h / max(zs)
    for v in bm.verts:
        z = max(0.0, v.co.z * kz)
        v.co = Vector(((v.co.x - cx) * kx + lean[0] * z, (v.co.y - cy) * ky + lean[1] * z, z))
    bottom = [f for f in bm.faces if all(v.co.z < 0.02 for v in f.verts)]
    bmesh.ops.delete(bm, geom=bottom, context="FACES_ONLY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # recalc on an open shell can flip everything inward: force outward normals
    for f in bm.faces:
        c = f.calc_center_median()
        if f.normal.dot(Vector((c.x, c.y, c.z - h * 0.4))) < 0:
            f.normal_flip()
    bm.normal_update()
    return bm, dict(rx=rx, ry=ry, h=h)


def rock_style(seed):
    """The one rock colour (w01_rock) with a small random Tint per facet.
    Light tops and cool shadow sides come from the lighting (Roblox or the
    studio), never from paint."""
    rng = random.Random(seed + 7)

    def style(f, nrm):
        return ROCK, rng.uniform(0.94, 1.06)

    return style


# ---------------------------------------------------------------------------
# Moss drapes
# ---------------------------------------------------------------------------


def moss_bm(bvh, origin, ray, t1, t2, R, thick, rng, lobes=6):
    """A lobed moss cap draped on the rock: a star outline of `lobes` rounded
    lobes (tips and notches) ray-cast onto the surface, so it folds over the
    plateau rim and down the facets; a raised centre, an inner ring and a
    short skirt give it a soft thickness. Returns (bmesh, lobe-tip hits) or
    (None, [])."""
    def cast(th, r):
        for _ in range(6):
            o = origin + t1 * math.cos(th) * R[0] * r + t2 * math.sin(th) * R[1] * r
            hit = bvh.ray_cast(o, ray)
            if hit[0] is not None:
                return hit[0], hit[1]
            r *= 0.8
        return None, None

    cl, cn = cast(0.0, 0.0)
    if cl is None:
        return None, []
    ph = rng.uniform(0, 2 * math.pi)
    m = lobes * 2
    ring = []
    for k in range(m):
        th = ph + 2 * math.pi * (k + rng.uniform(-0.15, 0.15)) / m
        r = (1.0 if k % 2 == 0 else 0.74) * rng.uniform(0.88, 1.12)
        ol, on = cast(th, r)
        il, inn = cast(th, r * 0.5)
        if ol is None or il is None:
            continue
        ring.append((ol, on, il, inn, k % 2 == 0))
    if len(ring) < 6:
        return None, []
    bm = bmesh.new()
    C = bm.verts.new(cl + cn * thick)
    I = [bm.verts.new(il + inn * thick * 0.9) for ol, on, il, inn, tip in ring]
    O = [bm.verts.new(ol + on * thick * 0.4) for ol, on, il, inn, tip in ring]
    A = [bm.verts.new(ol - on * 0.04) for ol, on, il, inn, tip in ring]
    n = len(ring)
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new((C, I[i], I[j])))
        faces.append(bm.faces.new((I[i], O[i], O[j], I[j])))
        faces.append(bm.faces.new((O[i], A[i], A[j], O[j])))
    bm.normal_update()
    out = -ray.normalized()
    if sum(f.normal.dot(out) for f in faces[0::3]) < 0:
        for f in faces:
            f.normal_flip()
    bm.normal_update()
    rim = [(ol.copy(), on.copy()) for ol, on, il, inn, tip in ring if tip]
    return bm, rim


def moss_style(rng, out, side=False):
    """The one moss colour (w01_moss) with a small random Tint."""
    def style(f, n):
        return MOSS, rng.uniform(0.95, 1.05)

    return style


def build_boulder(key, M, seed_shift=0, scale=1.0):
    """Boulder `key` with its moss, placed by M (asset space). Returns a dict
    with the rock and moss bmeshes, the leaves spilling off the moss rim, and
    the footprint used for dressing."""
    spec = ROCKS[key]
    seed = spec["seed"] + seed_shift
    size = tuple(s * scale for s in spec["size"])
    bm, shape = rock_bm(size, seed, spec["sides"], spec["wall"], spec["pivot"], spec["plateau"],
                        spec["shoulder"], spec["low"], spec["tilt"], spec["lean"], spec["upper"])
    bvh = BVHTree.FromBMesh(bm)
    rng = random.Random(seed + 11)
    moss, spill, tufts = [], [], []
    for md in spec["moss"]:
        R = (md["R"][0] * scale, md["R"][1] * scale)
        thick = md["thick"] * min(1.0, scale * 1.1)
        if "at" in md:  # cap: cast straight down onto the top
            o = Vector((md["at"][0] * scale, md["at"][1] * scale, size[2] + 2))
            mb, rim = moss_bm(bvh, o, Vector((0, 0, -1)), Vector((1, 0, 0)), Vector((0, 1, 0)), R, thick, rng,
                              md.get("lobes", 6))
            out = Z
            # a few clover leaves spilling over the rim, toward the front
            rim.sort(key=lambda h: h[0].y + rng.uniform(-0.6, 0.6))
            for loc, nrm in rim[:md.get("spill", 0)]:
                d = Vector((loc.x - o.x, loc.y - o.y, 0)).normalized()
                spill.append((loc + nrm * 0.05, (d + Z * 0.15).normalized(), 0.5 * scale ** 0.5, 0.6, nrm.copy()))
            # clover leaves lying on the pad break up its outline into lobes
            # a low tuft of moss clover on the pad (built once the rock is placed)
            tufts.append((Vector((o.x + md.get("tuft", (0, 0))[0] * scale, o.y + md.get("tuft", (0, 0))[1] * scale,
                                  size[2] + 0.3)), (R[0] + R[1]) * 0.5, thick))
            for k in range(md.get("leaves", 0)):
                ang = 2 * math.pi * (k + rng.uniform(-0.3, 0.3)) / md.get("leaves", 6)
                rr = rng.uniform(0.2, 0.65)
                lo = o + Vector((math.cos(ang) * R[0] * rr, math.sin(ang) * R[1] * rr, 0))
                hit = bvh.ray_cast(lo, Vector((0, 0, -1)))
                if hit[0] is not None:
                    d = Vector((math.cos(ang), math.sin(ang), rng.uniform(0.4, 0.8))).normalized()
                    spill.append((hit[0] + hit[1] * (thick * 0.7), d, 0.62 * scale ** 0.5, 0.3, hit[1].copy()))
        else:  # side patch: cast inward from outside, long axis down the slope
            d = Vector(md["dir"]).normalized()
            o = Vector((d.x * size[0], d.y * size[1], md["h"] * size[2] + d.z * size[2]))
            t1 = d.cross(Z).normalized()
            t2 = t1.cross(d).normalized()
            mb, rim = moss_bm(bvh, o, -d, t1, t2, R, thick, rng, md.get("lobes", 5))
            out = d
        if mb is not None:
            moss.append((mb, out, md.get("side", False)))
    # into asset space
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts[:])
    R3 = M.to_3x3()
    moss = [(mb, (R3 @ out).normalized(), side) for mb, out, side in moss]
    for mb, _, _ in moss:
        bmesh.ops.transform(mb, matrix=M, verts=mb.verts[:])
    spill = [(M @ p, (R3 @ d).normalized(), s, cu, (R3 @ n).normalized()) for p, d, s, cu, n in spill]
    tufts = [(M @ p, s, th) for p, s, th in tufts]
    cx, cy = M.translation.x, M.translation.y
    return dict(key=key, bm=bm, moss=moss, spill=spill, tufts=tufts, seed=seed, rng=rng, cx=cx, cy=cy, rx=shape["rx"],
                ry=shape["ry"], h=shape["h"], yaw=M.to_euler().z)


# ---------------------------------------------------------------------------
# Dressing: clover clumps, daisies, rubble
# ---------------------------------------------------------------------------


def leaf(a, base, d, L, W, mat, curl=0.25, fold=0.16, th=0.05, up=None, under=True):
    """Rounded clover-like leaf: a ridged top (midrib raised, edges turned
    down; 12 tris) bending gently along its length, plus a flat underside
    (6 tris) unless `under` is False (leaves shingled onto a mound, whose
    undersides face the mound). `up` is the side the top faces (default +Z)."""
    d = Vector(d).normalized()
    up = Vector(up).normalized() if up is not None else Z
    side = d.cross(up)
    if side.length < 1e-4:
        side = d.orthogonal()
    side.normalize()
    base = Vector(base)
    prof = ((0.0, 0.1), (0.26, 0.44), (0.56, 0.56), (0.82, 0.42), (0.96, 0.0))
    c = base.copy()
    dk = d.copy()
    prev = 0.0
    pts = []
    for t, w in prof:
        c = c + dk * L * (t - prev)
        prev = t
        u = side.cross(dk).normalized()
        if u.dot(up) < 0:
            u = -u
        pts.append((c.copy(), u, w * W))
        dk = (Matrix.Rotation(-curl * 0.45, 3, side) @ dk).normalized()
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
    left = [bm.faces.new(f) for f in ((B, L1, M1), (M1, L1, L2), (M1, L2, M2), (M2, L2, L3), (M2, L3, M3),
                                      (M3, L3, T))]
    right = [bm.faces.new(f) for f in ((B, M1, R1), (M1, R2, R1), (M1, M2, R2), (M2, R3, R2), (M2, M3, R3),
                                       (M3, T, R3))]
    under_f = [bm.faces.new((B, R1, R2, R3, T, L3, L2, L1))] if under else []
    faces = left + right + under_f
    bm.normal_update()
    nu = pts[1][1]
    for f in left + right:
        if f.normal.dot(nu) < 0:
            f.normal_flip()
    for f in under_f:
        if f.normal.dot(nu) > 0:
            f.normal_flip()
    t = 1.0 + a.rng.uniform(-0.05, 0.05)  # one small random Tint per leaf
    paint(a, faces, mat, t)
    return faces


def round_leaf(a, base, d, R, mat, cup=0.18, droop=0.25):
    """Round clover leaf on a short stem: a cupped heart-shaped disc of radius
    R whose stem end sits at `base`, pointing along d (7-vertex outline, the
    rim drooping a little past the centre; 7 tris top + 5 tris underside)."""
    d = Vector(d).normalized()
    side = d.cross(Z)
    if side.length < 1e-4:
        side = d.orthogonal()
    side.normalize()
    u = side.cross(d).normalized()
    if u.z < 0:
        u = -u
    c = Vector(base) + d * R
    bm = a.bm
    hub = bm.verts.new(c + u * cup * R)
    ring = []
    for k, ang in enumerate((180, 128, 72, 18, -18, -72, -128)):
        t = math.radians(ang + (0 if k == 0 else a.rng.uniform(-8, 8)))
        rr = R * (0.72 if k == 0 else a.rng.uniform(0.92, 1.05))  # notch at the stem (heart shape)
        along = math.cos(t) * rr
        p = c + d * along + side * math.sin(t) * rr
        p -= u * droop * R * max(0.0, along / R)  # the far rim droops
        p.z = max(p.z, 0.0)
        ring.append(bm.verts.new(p))
    top = [bm.faces.new((hub, ring[i], ring[(i + 1) % 7])) for i in range(7)]
    bot = bm.faces.new(ring[::-1])
    bm.normal_update()
    if sum(f.normal.dot(u) for f in top) < 0:
        for f in top:
            f.normal_flip()
    if bot.normal.dot(u) > 0:
        bot.normal_flip()
    paint(a, top + [bot], mat, 1.0 + a.rng.uniform(-0.05, 0.05))


def surface_z(bvh, x, y, top=40.0):
    """Height of the rock union (or the ground) under (x, y), below `top`."""
    if bvh is None:
        return 0.0
    hit = bvh.ray_cast(Vector((x, y, top)), Vector((0, 0, -1)))
    return max(0.0, hit[0].z) if hit[0] is not None else 0.0


def clump(a, c, away, s=1.0, n=8, rng=None, bvh=None, top=40.0, mat=LEAF, flat=1.0, lift=0.0, core=True):
    """A bushy clover rosette (~s wide): round leaves on short stems radiating
    from the centre, tilted up and overlapping in two tiers (an outer ring
    of ~5 leaves arching out and down, 2-3 upright leaves in the middle),
    over a small hidden core so no ground shows through; draped on the rocks
    or the ground under it. Returns the crown point."""
    rng = rng or a.rng
    base_az = math.atan2(away[1], away[0])
    cx, cy = c[0] + away[0] * 0.05 * s, c[1] + away[1] * 0.05 * s
    z0 = surface_z(bvh, cx, cy, top) + lift
    if core:
        pts = [Vector((cx, cy, z0 + 0.42 * s * flat))]
        pts += ellipse_pts(cx, cy, 0.26 * s, 0.26 * s, z0 + 0.26 * s * flat, 5, rng, 0.15)
        for p in ellipse_pts(cx, cy, 0.36 * s, 0.36 * s, 0.0, 5, rng, 0.12, phase=0.6):
            p.z = max(surface_z(bvh, p.x, p.y, z0 + 0.3 * s) - 0.06, 0.0)
            pts.append(p)
        bm = hull_bm(pts)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.z < -0.5], context="FACES_ONLY")
        emit(a, bm, lambda f, nn: (mat, rng.uniform(0.95, 1.05)))
        bm.free()
    n3 = 1 if n >= 8 else 0
    n2 = max(2, (n - n3) // 3)
    n1 = n - n2 - n3
    ph = base_az + rng.uniform(-0.4, 0.4)
    crown = z0
    for i in range(n1):  # outer ring: round leaves fanned out on short stems
        az = ph + 2 * math.pi * (i + rng.uniform(-0.2, 0.2)) / n1
        el = math.radians(rng.uniform(18, 34)) * flat
        d = Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el)))
        b = Vector((cx + math.cos(az) * 0.1 * s, cy + math.sin(az) * 0.1 * s, z0 + 0.14 * s * flat))
        round_leaf(a, b, d, s * rng.uniform(0.2, 0.23), mat)
    for i in range(n2):  # middle tier: leaves tilted up between the outer ones
        az = ph + 2 * math.pi * (i + 0.5 + rng.uniform(-0.2, 0.2)) / n2 + math.pi / n1
        el = math.radians(rng.uniform(40, 56)) * flat
        d = Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el)))
        b = Vector((cx, cy, z0 + 0.3 * s * flat))
        R = s * rng.uniform(0.18, 0.21)
        round_leaf(a, b, d, R, mat)
        crown = max(crown, b.z + 2 * R * math.sin(el) * 0.8)
    for i in range(n3):  # one leaf crowning the mound, facing up
        az = ph + rng.uniform(0, 2 * math.pi)
        d = Vector((math.cos(az), math.sin(az), 0.35)).normalized()
        R = s * 0.2
        b = Vector((cx - d.x * R, cy - d.y * R, z0 + 0.5 * s * flat))
        round_leaf(a, b, d, R, mat, droop=0.35)
        crown = max(crown, b.z + 0.1 * s)
    return Vector((cx, cy, crown))


def daisy(a, c, nrm, R=0.32):
    """White flower, 6 rounded petals and a yellow centre (~26 tris)."""
    bm = a.bm
    n = Vector(nrm).normalized()
    t1 = n.cross(Z if abs(n.z) < 0.95 else Vector((1, 0, 0))).normalized()
    t2 = n.cross(t1)
    c = Vector(c)
    ph = a.rng.uniform(0, 2 * math.pi)
    hub = bm.verts.new(c + n * 0.02)
    faces = []
    for k in range(6):
        ang = ph + k * math.pi / 3

        def at(da, rr, lift):
            return bm.verts.new(c + (math.cos(ang + da) * t1 + math.sin(ang + da) * t2) * R * rr + n * lift * R)

        l, tip, r = at(-0.42, 0.72, 0.08), at(0.0, 1.0, 0.12), at(0.42, 0.72, 0.08)
        faces.append(bm.faces.new((hub, l, tip)))
        faces.append(bm.faces.new((hub, tip, r)))
    for f in faces:
        if f.normal.dot(n) < 0:
            f.normal_flip()
    paint(a, faces, "flower_white", 1.0, 0.03)
    eul = n.to_track_quat("Z", "Y").to_euler()
    a.cyl(R * 0.3, R * 0.14, R * 0.22, 5, loc=c + n * 0.01, rot=eul, mat="flower_yellow", tint=1.0)


def pebble(a, c, s, rng, flat=0.6):
    """Tiny rubble stone: hull of ~13 points on a squashed ellipsoid (~14 tris)."""
    pts = []
    for k in range(6):
        th = 2 * math.pi * (k + rng.uniform(-0.3, 0.3)) / 6
        ph = rng.uniform(0.15, 0.8)
        pts.append(Vector((math.cos(th) * s * math.cos(ph * 0.9), math.sin(th) * s * 0.85 * math.cos(ph * 0.9),
                           s * flat * math.sin(ph) + s * 0.1)))
    pts.append(Vector((rng.uniform(-0.2, 0.2) * s, rng.uniform(-0.2, 0.2) * s, s * flat * 1.05)))
    pts += ellipse_pts(0, 0, s * 0.85, s * 0.7, 0.0, 5, rng, 0.1)
    bm = hull_bm(pts)
    bottom = [f for f in bm.faces if all(v.co.z < 0.02 for v in f.verts)]
    bmesh.ops.delete(bm, geom=bottom, context="FACES_ONLY")
    M = Matrix.Translation((c[0], c[1], 0)) @ Matrix.Rotation(rng.uniform(0, 6.3), 4, "Z")
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts[:])
    emit(a, bm, rock_style(rng.randrange(1000)))
    bm.free()


def inside(rocks, x, y, margin=0.0, skip=None):
    for i, r in enumerate(rocks):
        if i == skip:
            continue
        dx, dy = x - r["cx"], y - r["cy"]
        cs, sn = math.cos(-r["yaw"]), math.sin(-r["yaw"])
        lx, ly = dx * cs - dy * sn, dx * sn + dy * cs
        if (lx / (r["rx"] + margin)) ** 2 + (ly / (r["ry"] + margin)) ** 2 < 1:
            return True
    return False


def rim_point(r, th, out=0.0):
    """Point on rock r's girth rim at world angle th, pushed out by `out`."""
    cs, sn = math.cos(-r["yaw"]), math.sin(-r["yaw"])
    lx, ly = math.cos(th) * cs - math.sin(th) * sn, math.cos(th) * sn + math.sin(th) * cs
    k = 1 / math.sqrt((lx / r["rx"]) ** 2 + (ly / r["ry"]) ** 2)
    return r["cx"] + math.cos(th) * (k + out), r["cy"] + math.sin(th) * (k + out)


def rim_dist(r, th):
    x, y = rim_point(r, th)
    return math.hypot(x - r["cx"], y - r["cy"])


def join_spots(rocks, bvh, joins):
    """Crevice points: for each (low, tall, side) in `joins`, the back shoulder
    of the lower boulder where it meets the taller one, shifted `side` studs
    sideways (+ = right of the low->tall direction), dropped onto the rock
    union. Returns [(x, y, away)]."""
    by = {r["key"]: r for r in rocks}
    spots = []
    for low, tall, side in joins:
        lo, hi = by[low], by[tall]
        dx, dy = hi["cx"] - lo["cx"], hi["cy"] - lo["cy"]
        th = math.atan2(dy, dx)
        ux, uy = math.cos(th), math.sin(th)
        top = lo["h"] + 0.4  # look under the tall rock's overhang
        # walk from the low rock's centre toward the tall one (shifted `side`)
        # until the tall rock's flank rises out of the low rock's top
        x0, y0 = lo["cx"] + uy * side, lo["cy"] - ux * side
        x, y = x0, y0
        for k in range(60):
            xk, yk = x0 + ux * 0.2 * k, y0 + uy * 0.2 * k
            zk = surface_z(bvh, xk, yk, top)
            if hi["solid"].inside(Vector((xk, yk, zk + 0.7)), 0.0) or zk < 0.3 * lo["h"]:
                break
            x, y = xk, yk
        # face out of the crevice: away from the tall rock, toward the side
        ax, ay = -ux + uy * 0.6 * (1 if side >= 0 else -1), -uy - ux * 0.6 * (1 if side >= 0 else -1)
        n = math.hypot(ax, ay)
        spots.append((x, y, (ax / n, ay / n), top))
    return spots


def dress(a, rocks, bvh, seed, clumps=7, joins=(), flowers=3, rubble=5, s=1.0, front=2.5, cs=2.6,
          inset=0.35, join_scale=0.9, spots=None):
    """Clover mounds wedged into the joins between boulders and banded along the
    front of the base, daisies on some of them, rubble stones on the outer rim.
    Ground clumps sit just inside the boulders' girth (under the overhang) and
    stay off the back, so the foliage hugs the rocks. `spots` adds explicit
    clumps [(x, y, scale)]."""
    rng = random.Random(seed)
    crowns = []
    if bvh is not None and joins:
        for x, y, away, top in join_spots(rocks, bvh, joins):
            crowns.append((clump(a, (x, y), away, join_scale * cs * s * rng.uniform(0.95, 1.1),
                                 n=rng.choice((8, 9)), rng=rng, bvh=bvh, top=top), away))
    cands = []
    ymax = max(r["cy"] + r["ry"] for r in rocks)
    for i, r in enumerate(rocks):
        for k in range(28):
            th = 2 * math.pi * k / 28 + rng.uniform(-0.08, 0.08)
            if math.sin(th) > 0.45:
                continue  # keep the back of each boulder clear
            x, y = rim_point(r, th, -inset * s)
            if inside(rocks, x, y, -0.3, skip=i) or y > ymax - 0.5:
                continue
            near = min([math.hypot(x - o["cx"], y - o["cy"]) - max(o["rx"], o["ry"])
                        for j, o in enumerate(rocks) if j != i] or [9.0])
            join = max(0.0, 1.4 - near)
            score = join * 1.2 + front * (-math.sin(th)) * 0.6 + rng.uniform(0, 0.6)
            cands.append((score, x, y, th, join))
    cands.sort(reverse=True)
    placed = []
    taken = [(c.x, c.y) for c, _ in crowns]
    for sc, x, y, th, join in cands:
        if len(placed) >= clumps:
            break
        if any(math.hypot(x - px, y - py) < 0.72 * cs * s for px, py in taken):
            continue
        placed.append((x, y, th, 1.0))
        taken.append((x, y))
    for x, y, sc in spots or ():
        placed.append((x, y, math.atan2(y, x), sc))
    for x, y, th, sc in placed:
        k = cs * s * sc * rng.uniform(0.85, 1.1)
        cr = clump(a, (x, y), (math.cos(th), math.sin(th)), k, n=rng.choice((10, 11)), rng=rng)
        crowns.append((cr, (math.cos(th), math.sin(th))))
    # daisies on the front-most mounds (and the joins)
    fronts = sorted(crowns, key=lambda q: q[0].y - q[0].z * 0.3)[:max(flowers + 2, 1)]
    rng.shuffle(fronts)
    for cr, away in fronts[:flowers]:
        off = Vector((away[0], away[1], 0)) * 0.22 * cs * s
        c = cr + off + Vector((rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15), 0.0))
        daisy(a, c, Vector((rng.uniform(-0.25, 0.25), -0.45, 1.0)), 0.5 * s)
    # rubble just outside the rim at the front, avoiding clumps
    rc = [q for q in cands if q[4] < 0.6]
    rc.sort(key=lambda q: -(-math.sin(q[3]) * 0.8 + rng.uniform(0, 1.0)))
    stones = []
    for sc, x, y, th, join in rc:
        if len(stones) >= rubble:
            break
        x2, y2 = x + math.cos(th) * (inset + 0.55) * s, y + math.sin(th) * (inset + 0.55) * s
        if any(math.hypot(x2 - px, y2 - py) < 0.7 * cs * s for px, py in taken):
            continue
        if any(math.hypot(x2 - px, y2 - py) < 1.2 * s for px, py in stones):
            continue
        stones.append((x2, y2))
        pebble(a, (x2, y2), rng.uniform(0.38, 0.62) * s, rng)


def place(key, x, y, yaw=0.0, scale=1.0):
    return key, Matrix.Translation((x, y, 0)) @ Matrix.Rotation(yaw, 4, "Z"), scale


def cull_hidden(a, solids, start):
    """Delete asset faces (from index `start` on) buried inside a boulder."""
    a.bm.faces.ensure_lookup_table()
    kill = []
    for f in a.bm.faces[start:]:
        for so in solids:
            if all(so.inside(v.co) for v in f.verts):
                kill.append(f)
                break
    if kill:
        bmesh.ops.delete(a.bm, geom=kill, context="FACES_ONLY")
    loose = [v for v in a.bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(a.bm, geom=loose, context="VERTS")


def assemble(kit, name, placements, seed, role, collision="hull", budget=None, notes="", dress_on=True,
             **dress_kw):
    fk = kit.flintkit
    a = fk.Asset(name, f"Kit {kit.sheet} {kit.subject}", seed=seed)
    rocks = [build_boulder(key, M, scale=sc) for key, M, sc in placements]
    solids = [Solid(r["bm"]) for r in rocks]
    for r, so in zip(rocks, solids):
        r["solid"] = so
    # union of the boulders for draping clumps into the joins
    verts, polys = [], []
    for r in rocks:
        off = len(verts)
        r["bm"].verts.index_update()
        verts += [v.co.copy() for v in r["bm"].verts]
        polys += [[v.index + off for v in f.verts] for f in r["bm"].faces]
    bvh = BVHTree.FromPolygons(verts, polys)
    for r in rocks:
        emit(a, r["bm"], rock_style(r["seed"]))
        r["bm"].free()
        for mb, out, side in r["moss"]:
            emit(a, mb, moss_style(r["rng"], out, side))
            mb.free()
        for p, s, th in r["tufts"]:
            clump(a, (p.x, p.y), (0.0, -1.0), s * 0.9, n=8, rng=r["rng"], bvh=bvh, top=p.z + 0.5, mat=MOSS,
                  flat=0.75, lift=th * 0.7, core=False)
        for p, d, s, cu, n in r["spill"]:
            L = s * a.rng.uniform(0.85, 1.0)
            round_leaf(a, p - d * L * 0.3, d, L * 0.5, MOSS, droop=0.4)
    if dress_on:
        dress(a, rocks, bvh, seed, **dress_kw)
    cull_hidden(a, solids, 0)
    obj = a.finish()
    return kit.tag(obj, role, collision=collision, budget=budget, notes=notes)


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------


def build(kit):
    objs = []
    # hero: A tall at the back right, C broad at the front left, B low front right
    objs.append(assemble(kit, "RockCluster",
                         [place("A", 1.1, 1.4, 0.2), place("C", -2.0, -0.9, -0.25), place("B", 2.5, -2.2, 0.45)],
                         3300, "hero", notes="three interlocking boulders with moss, clover mounds, daisies",
                         clumps=9, flowers=4, rubble=6,
                         joins=[("C", "A", 1.2), ("B", "A", 0.9), ("C", "A", -1.8), ("B", "A", -0.8),
                                ("B", "C", 0.6)]))
    # parts: each boulder alone with its moss (and a small tuft), centred on the rock
    objs.append(assemble(kit, "RockClusterA", [place("A", 0, 0, 0)], 3310, "part",
                         notes="rock A of the cluster (tall), kit-bash piece", dress_on=False))
    objs.append(assemble(kit, "RockClusterB", [place("B", 0, 0, 0)], 3320, "part",
                         notes="rock B of the cluster (low), kit-bash piece",
                         clumps=0, joins=(), flowers=0, rubble=0, inset=1.0,
                         spots=[(1.75, -1.0, 0.75)]))
    objs.append(assemble(kit, "RockClusterC", [place("C", 0, 0, 0)], 3330, "part",
                         notes="rock C of the cluster (broad), kit-bash piece",
                         clumps=0, joins=(), flowers=0, rubble=0,
                         spots=[(-2.6, -1.4, 0.8)]))
    # variants
    objs.append(assemble(kit, "RockClusterLinear",
                         [place("C", -3.3, -0.4, 0.4, 0.78), place("A", 0.3, 0.5, 0.1, 0.9),
                          place("B", 3.6, -0.4, -0.3, 0.8)],
                         3340, "variant", notes="three boulders in a row", clumps=7, flowers=2, rubble=4,
                         joins=[("C", "A", 0.5), ("B", "A", -0.4)]))
    objs.append(assemble(kit, "RockClusterCrescent",
                         [place("C", -3.2, -1.2, 0.9, 0.74), place("A", 0.0, 1.0, -0.4, 0.88),
                          place("B", 3.2, -1.3, 1.4, 0.8)],
                         3350, "variant", notes="three boulders on a curve, open to the front",
                         clumps=7, flowers=2, rubble=4, joins=[("C", "A", 0.4), ("B", "A", 0.3)]))
    objs.append(assemble(kit, "RockClusterTriangular",
                         [place("A", 0.6, 1.0, 0.6, 0.88), place("C", -1.6, -1.2, 2.0, 0.66),
                          place("B", 2.0, -1.6, -0.8, 0.72)],
                         3360, "variant", notes="compact triangle of boulders", clumps=7, flowers=2,
                         joins=[("C", "A", -0.6), ("B", "A", 0.8)],
                         rubble=3))
    return objs
