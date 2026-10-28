"""W01 row 1: Boulder, a squat large-facet rock with a moss cap.

Assets
  Boulder          hero: broad mauve-grey chiselled rock with a flat plateau top
                   (and a front-left crease), a lumpy lime moss pad on the top right
                   of centre spilling over the front-right shoulder, rubble stones,
                   two bushy clover clumps (front-left, right-front) with white
                   daisies and smaller clumps ringing the foot (~10.5 x 8.5 x 6.2)
  BoulderMainRock  part: the rock alone, with its low moss smudge on the front-left
  BoulderMossCap   part: the moss pad alone (closed shells, sits on the rock top)
  BoulderFlat      variant: wider, lower
  BoulderUpright   variant: taller, blunt plateau top with a moss tuft, a broad
                   moss streak down the face, companion rock at the front-right foot
  BoulderSplit     variant: a taller and a separate shorter piece with an open split

Rocks are the convex hull of jittered rings on an elliptical profile (a near-
vertical lower wall, sloping shoulders, a near-flat plateau ring), so the surface
breaks into big triangular chisel facets (~100 tris); chisel() then pushes
neighbouring hull vertices alternately out and in so adjacent facets get clearly
different normals, and the hero's crease is an extra column of hull points
pulled in. Surface queries use a BVH (ray parity), so they stay right on the
non-convex result. ONE colour per material: every stone is w01_rock, all moss
w01_moss, all clumps w01_leaf (plus flower_white / flower_yellow daisies), with
only a small random Tint per face; the light and dark sides come from the
renderer's and Roblox's lighting, never from the colours. The moss cap is an
irregular cluster of flat leaf-shaped lobes hugging the rock top, the front-right
ones spilling over the shoulder. Base clumps are banks of rounded leaf masses set
against the rock wall at their own heights, shingled with clover leaves. No VFX:
the reference shows none.

Faces of the walk-through dressing (base foliage, flowers, rubble) carry the
face attribute kit_nocollide = 1, so an exporter can split them off as a
non-colliding piece.
"""

import math
import os
import random

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

SUBJECT = "Boulder"
ROW = 1
PALETTE = {
    "w01_rock": ("#B29F98", 0.9, 0, 0),  # THE ONLY stone colour on the whole sheet: warm mauve-beige granite of every boulder, spire, cluster rock, slab and pebble (lit mid-tone; median of all rock pixels across the 4 hero cells is #B29F96-#B5A097). The swatches' blue-grey (#8E8E9E) and pale beige (#CAB2A8) are its shadow and lit sides, NOT materials: drop w01_boulder_beige, w01_boulder_blue, w01_rock_light, w01_rock_cool, w01_rock_warm, kit_rock(_light/_dark) and stone. Same value in every module that declares it (this replaces the old #8E7C78). Variety only via a small random Tint (<=1.25x spread), never by face direction.
    "w01_moss": ("#ADBB14", 0.9, 0, 0),  # Lime-yellow moss: moss caps, moss pads, streaks/smudges and thin decals on rock facets (median moss pixel #ADBB08; swatches 3 #8DA418 and 4 #D7CD29 are its shadow and lit sides). Replaces moss, moss_light, moss_dark.
    "w01_leaf": ("#7AAB1E", 0.8, 0, 0),  # Clover / round-leaf ground clumps banked at rock feet and in crevices: a greener, slightly deeper green than the moss so the two read apart. Replaces leaf, leaf_light and grass_light on this sheet (one key for all leafy clumps).
}
# flower_white (#F5F2EA daisy petals) and flower_yellow (#F2C230 daisy centres) are
# existing flintkit PALETTE keys, so they are not redeclared here (the runner only
# accepts w01_-prefixed extra keys).
ROCK, MOSS, LEAF = "w01_rock", "w01_moss", "w01_leaf"

PI = math.pi
TAU = 2 * PI
Z = Vector((0, 0, 1))
RAY_DIR = Vector((0.131, 0.071, 1.0)).normalized()  # parity ray, off-axis to miss edges
CAT = "Kit W01 Boulder"


def tint(rng):
    return rng.uniform(0.93, 1.07)


# ---------------------------------------------------------------------------
# Convex chiselled rocks
# ---------------------------------------------------------------------------


class Rock:
    """A closed rock in its own bmesh (convex hull, then chiselled: some vertices
    pushed in/out), with a BVH tree for surface queries."""

    def __init__(self, bm):
        self.bm = bm
        self.refresh()

    def refresh(self):
        bm = self.bm
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.normal_update()
        self.bvh = BVHTree.FromBMesh(bm)
        n = len(bm.verts)
        self.centre = sum((v.co for v in bm.verts), Vector()) / n
        self.zmax = max(v.co.z for v in bm.verts)
        xs = [v.co.x for v in bm.verts]
        self.rx = (max(xs) - min(xs)) / 2

    def inside(self, p, pad=0.0):
        """Ray parity (robust for the chiselled, non-convex hull), then at least
        pad from the surface."""
        p = Vector(p)
        o, hits = p.copy(), 0
        for _ in range(16):
            loc = self.bvh.ray_cast(o, RAY_DIR)[0]
            if loc is None:
                break
            hits += 1
            o = loc + RAY_DIR * 1e-4
        if hits % 2 == 0:
            return False
        return pad <= 0 or self.bvh.find_nearest(p)[3] > pad

    def top(self, x, y):
        """Height of the upper surface above (x, y) (-1e9 off the rock)."""
        loc = self.bvh.ray_cast(Vector((x, y, self.zmax + 5)), Vector((0, 0, -1)), 100)[0]
        return loc.z if loc is not None else -1e9

    def radial(self, th, z, c=None):
        """Distance from the vertical axis through c (default centre) to the surface."""
        c = self.centre if c is None else c
        dx, dy = math.cos(th), math.sin(th)
        lo, hi = 0.0, 30.0
        if not self.inside((c.x, c.y, z)):
            return 0.0
        for _ in range(30):
            m = (lo + hi) / 2
            if self.inside((c.x + dx * m, c.y + dy * m, z)):
                lo = m
            else:
                hi = m
        return lo

    def cut(self, n, co):
        """Keep the side of the plane opposite its normal; cap the cut flat."""
        bm = self.bm
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=n, clear_outer=True)
        bnd = [e for e in bm.edges if e.is_boundary]
        if bnd:
            bmesh.ops.contextual_create(bm, geom=bnd)
        self.refresh()
        return self

    def move(self, offset):
        for v in self.bm.verts:
            v.co += Vector(offset)
        self.refresh()
        return self

    def dent(self, az, half, zlo, zhi, depth):
        """Push the hull vertices around azimuth az (deg, +-half) between zlo and
        zhi in toward the axis: a concave crease. The planes used for surface
        queries stay those of the convex hull."""
        c = self.centre
        a0 = math.radians(az)
        for v in self.bm.verts:
            dx, dy = v.co.x - c.x, v.co.y - c.y
            r = math.hypot(dx, dy)
            if r < 1e-3 or not (zlo <= v.co.z <= zhi):
                continue
            d = (math.atan2(dy, dx) - a0 + PI) % TAU - PI
            if abs(d) > math.radians(half):
                continue
            k = depth * (1 - (abs(d) / math.radians(half)) ** 2)
            v.co.x -= dx / r * k
            v.co.y -= dy / r * k
        self.bm.normal_update()
        return self


def rock_points(rng, rx, ry, h, spec, jitter=0.06, lean=(0.0, 0.0), crown=1, crown_r=0.1,
                crown_z=(1.0, 1.0)):
    """Jittered rings (t, n, radius factor) on an ellipse, plus crown points."""
    pts = []
    for t0, n, rf in spec:
        ph = rng.uniform(0, TAU)
        for j in range(n):
            th = ph + TAU * (j + rng.uniform(-0.3, 0.3)) / n
            t = 0.0 if t0 == 0 else min(1.0, max(0.04, t0 + rng.uniform(-0.03, 0.02)))
            R = rf * (1 + rng.uniform(-jitter, jitter))
            pts.append(Vector((rx * R * math.cos(th) + lean[0] * t * h,
                               ry * R * math.sin(th) + lean[1] * t * h, t * h)))
    ph = rng.uniform(0, TAU)
    for k in range(crown):
        th = ph + TAU * (k + rng.uniform(-0.2, 0.2)) / max(crown, 1)
        rr = crown_r * (rng.uniform(0.6, 1.0) if crown > 1 else rng.uniform(0, 1))
        pts.append(Vector((rr * rx * math.cos(th) + lean[0] * h,
                           rr * ry * math.sin(th) + lean[1] * h, h * rng.uniform(*crown_z))))
    return pts


def hull_rock(pts, loc=(0, 0, 0)):
    bm = bmesh.new()
    vs = [bm.verts.new(Vector(p) + Vector(loc)) for p in pts]
    res = bmesh.ops.convex_hull(bm, input=vs, use_existing_faces=False)
    kill = list({g for g in res["geom_interior"] + res["geom_unused"]
                 if isinstance(g, bmesh.types.BMVert) and not g.link_faces})
    if kill:
        bmesh.ops.delete(bm, geom=kill, context="VERTS")
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    bottom = [f for f in bm.faces if f.normal.z < -0.999]
    if len(bottom) > 1:
        bmesh.ops.dissolve_faces(bm, faces=bottom)
    return Rock(bm)


def even_rings(rng, rx, ry, h, spec, ajit=0.12, rjit=0.035, tjit=0.015):
    """Like rock_points but with evenly spaced ring angles, each ring turned half
    a step from the one below, and small jitter: a level, symmetric profile (no
    random high shoulder on one side) that still breaks into big facets."""
    pts = []
    ph0 = rng.uniform(0, TAU)
    for i, (t0, n, rf) in enumerate(spec):
        ph = ph0 + (i % 2) * 0.5 * TAU / n
        for j in range(n):
            th = ph + TAU * (j + rng.uniform(-ajit, ajit)) / n
            t = 0.0 if t0 == 0 else min(1.0, t0 + rng.uniform(-tjit, tjit))
            R = rf * (1 + rng.uniform(-rjit, rjit))
            pts.append(Vector((rx * R * math.cos(th), ry * R * math.sin(th), t * h)))
    return pts


def chisel(rock, rng, amp, keep=(), band_amp=None):
    """Push the hull's vertices alternately out and in (by ~amp studs) round
    each height band, so neighbouring big triangles get clearly different
    normals: crisp light/shade breaks instead of a smooth convex lump. Base
    vertices move less (the foot stays planted), keep-vertices not at all.
    band_amp (bottom band first) overrides the per-band scale, so the
    shoulder and plateau rings can stay level and symmetric."""
    bm = rock.bm
    c = rock.centre
    zmax = rock.zmax
    vs = sorted((v for v in bm.verts if v not in keep), key=lambda v: v.co.z)
    bands, cur = [], [vs[0]]
    for v in vs[1:]:
        if v.co.z - cur[-1].co.z > 0.08 * zmax:
            bands.append(cur)
            cur = [v]
        else:
            cur.append(v)
    bands.append(cur)
    for bi, band in enumerate(bands):
        band.sort(key=lambda v: math.atan2(v.co.y - c.y, v.co.x - c.x))
        flip = rng.randrange(2)
        for i, v in enumerate(band):
            s = 1 if (i + flip) % 2 == 0 else -1
            m = amp * rng.uniform(0.7, 1.0)
            if band_amp is not None:
                m *= band_amp[min(bi, len(band_amp) - 1)]
            elif v.co.z < 1e-4:
                m *= 0.55
            elif bi == len(bands) - 1:
                m *= 0.6
            dx, dy = v.co.x - c.x, v.co.y - c.y
            r = math.hypot(dx, dy)
            if r > 1e-3:
                v.co.x += dx / r * s * m
                v.co.y += dy / r * s * m
    rock.refresh()
    return rock


def push_in(rock, verts_depths):
    """Pull the given vertices in toward the vertical axis by their depths."""
    c = rock.centre
    for v, d in verts_depths:
        dx, dy = v.co.x - c.x, v.co.y - c.y
        r = math.hypot(dx, dy)
        v.co.x -= dx / r * d
        v.co.y -= dy / r * d
    rock.refresh()


def ring_rf(spec, t):
    """Radius factor of a ring spec at height fraction t (linear between rings)."""
    for (t0, _n0, r0), (t1, _n1, r1) in zip(spec, spec[1:]):
        if t0 <= t <= t1:
            return r0 + (r1 - r0) * (t - t0) / (t1 - t0)
    return spec[-1][2]


def rock_painter(seed):
    """ONE stone colour (w01_rock) on every facet; only a small random Tint
    (+/-7%) per facet, never chosen by face direction, height or region. The
    light and dark sides come from the renderer's / Roblox's lighting."""
    rng = random.Random(seed)
    return lambda face: (ROCK, tint(rng))


def stone_at(a, rng, loc, s, tall=0.56):
    """A chunky faceted rubble stone of about s studs at loc (tall x s high)."""
    pts = rock_points(rng, s * 0.55, s * 0.47, s * tall, jitter=0.12,
                      spec=[(0.0, 6, 0.95), (0.5, 5, 1.0), (0.9, 4, 0.7)], crown=2, crown_r=0.35,
                      crown_z=(0.95, 1.0))
    rk = hull_rock(pts, loc)
    append_rock(a, rk, rock_painter(rng.randrange(1 << 30)))
    rk.bm.free()


class Painter:
    """Face colouring plus the dressing (no-collide) marker."""

    def __init__(self, a):
        self.a = a
        lay = a.bm.faces.layers.int
        self.flag = lay.get("kit_nocollide") or lay.new("kit_nocollide")
        self.dressing = False


def put(a, f, mat, t):
    t = round(t * 40) / 40  # few distinct levels: keeps the exported palette rows small
    f.material_index = a._mi(mat)
    f.smooth = False
    for lp in f.loops:
        lp[a.tint_layer] = (t, t, t, 1.0)
    p = getattr(a, "_w01", None)
    if p is not None:
        f[p.flag] = 1 if p.dressing else 0


class dressing:
    """with dressing(a): faces made inside are walk-through scatter."""

    def __init__(self, a):
        self.p = a._w01

    def __enter__(self):
        self.p.dressing = True

    def __exit__(self, *exc):
        self.p.dressing = False


def append_rock(a, rock, painter):
    """Copy a rock's faces into the asset, toned by painter(face) -> (mat, tint)."""
    src = rock.bm
    src.normal_update()
    vmap = {v: a.bm.verts.new(v.co) for v in src.verts}
    for f in src.faces:
        nf = a.bm.faces.new([vmap[v] for v in f.verts])
        put(a, nf, *painter(f))
    return list(vmap.values())


def smudge(a, rock, az, z, w=1.8, h=1.3, n=9, lift=0.08, seed=0):
    """A soft-edged moss stain on a rock wall: an irregular blob of n rim points
    around (az, z), riding the surface just off it, fanned from its centre.
    One moss colour (w01_moss) with a small random Tint."""
    rng = random.Random(seed)
    c = rock.centre
    th0 = math.radians(az)
    r0 = max(rock.radial(th0, z), 0.5)

    def at(th, zz, extra=0.0):
        r = rock.radial(th, zz) + lift + extra
        return Vector((c.x + math.cos(th) * r, c.y + math.sin(th) * r, zz))

    ctr = a.bm.verts.new(at(th0, z, 0.04))
    inner, outer = [], []
    ph = rng.uniform(0, TAU)
    for k in range(n):
        ang = ph + TAU * (k + rng.uniform(-0.2, 0.2)) / n
        s = rng.uniform(0.75, 1.15)
        dx, dz = math.cos(ang) * w / 2 * s, math.sin(ang) * h / 2 * s
        inner.append(a.bm.verts.new(at(th0 + dx * 0.5 / r0, max(0.05, z + dz * 0.5), 0.02)))
        outer.append(a.bm.verts.new(at(th0 + dx / r0, max(0.02, z + dz))))
    faces = [a.bm.faces.new((ctr, inner[k], inner[(k + 1) % n])) for k in range(n)]
    ring = [a.bm.faces.new((inner[k], outer[k], outer[(k + 1) % n], inner[(k + 1) % n])) for k in range(n)]
    for f in faces + ring:
        f.normal_update()
        mid = f.calc_center_median()
        if f.normal.dot(Vector((mid.x - c.x, mid.y - c.y, 0))) < 0:
            f.normal_flip()
    for f in faces + ring:
        put(a, f, MOSS, tint(rng))


def streak(a, rock, az, z0, z1, w=0.6, lift=0.1, seed=0):
    """A moss streak on a rock wall: a ribbon of quads riding the surface along
    azimuth az (deg) from z0 to z1, widest in the upper middle."""
    rng = random.Random(seed)
    th = math.radians(az)
    c = rock.centre
    steps = max(2, round((z1 - z0) / 0.55))
    rows = []
    for i in range(steps + 1):
        z = z0 + (z1 - z0) * i / steps
        s = i / steps
        half = w * (0.25 + 0.75 * math.sin(PI * min(1.0, s * 1.15))) / 2 * rng.uniform(0.8, 1.2)
        row = []
        wob = rng.uniform(-0.08, 0.08)
        for sgn in (-1, 1):
            r0 = max(rock.radial(th, z), 0.5)
            t2 = th + wob + sgn * half / r0
            r = rock.radial(t2, z)
            row.append(a.bm.verts.new(Vector((c.x + math.cos(t2) * (r + lift),
                                              c.y + math.sin(t2) * (r + lift), z))))
        rows.append(row)
    for i in range(steps):
        f = a.bm.faces.new((rows[i][0], rows[i][1], rows[i + 1][1], rows[i + 1][0]))
        f.normal_update()
        mid = f.calc_center_median()
        if f.normal.dot(Vector((mid.x - c.x, mid.y - c.y, 0))) < 0:
            f.normal_flip()
        put(a, f, MOSS, tint(rng))


# ---------------------------------------------------------------------------
# Moss slab
# ---------------------------------------------------------------------------


def moss_pad(a, rock, seed, c, R, lobes=5, thick=0.5, closed=False, max_drop=0.5, drape_dir=None,
             drape=0.0, flat=False, droop=0.0):
    """A flat lobed moss pad on the rock top: a round centre lobe and lobes-1
    leaf-shaped petal lobes radiating from it, each the hull of a scalloped
    rim hugging the rock surface, a mid ring and a low crown, so the outline
    is leafy and the top has gentle lumps where lobes overlap. Lobes toward
    drape_dir (deg) reach further and follow the shoulder down, spilling over
    it. closed=False drops the faces under the pad (inside the rock);
    closed=True keeps them (the separate part). flat=True gives each lobe a
    broad flat top with a short bevelled edge (a pad, not a dome); droop lets
    the lobes toward drape_dir hang that much further down the shoulder."""
    rng = random.Random(seed)
    cx, cy = c
    z0 = rock.top(cx, cy)
    ph = rng.uniform(0, TAU)
    # (x, y, heading, semi-length, semi-width, thickness, drop limit): a round centre
    # lobe and leaf-shaped petal lobes radiating from it, the ones toward drape_dir longer
    lobe_specs = [(cx, cy, ph, R * 0.52, R * 0.48, thick * (1.05 if flat else 1.2), max_drop)]
    n = lobes - 1
    for k in range(n):
        # an irregular cluster, not a rosette: uneven angles, reaches, sizes and
        # headings (each lobe turned up to ~45 deg off the radial)
        th = ph + TAU * (k + 0.5 + rng.uniform(-0.3, 0.3)) / n
        sz = rng.uniform(0.75, 1.2)
        d = R * rng.uniform(0.35, 0.62)
        la, lb = R * 0.5 * sz, R * 0.44 * sz
        w = 0.0
        if drape_dir is not None:
            w = max(0.0, math.cos(th - math.radians(drape_dir))) ** 2
            d *= 1 + drape * w
            la *= 1 + 0.25 * drape * w
        lobe_specs.append((cx + d * math.cos(th), cy + d * math.sin(th), th + rng.uniform(-0.8, 0.8),
                           la, lb, thick * rng.uniform(0.7, 1.05), max_drop + droop * w))

    def ground(x, y):
        return rock.top(x, y)

    rings = (((10, 1.0, 0.0, 0.07), (7, 0.72, 0.72, 0.0), (3, 0.36, 1.0, 0.0)) if flat else
             ((10, 1.0, 0.0, 0.07), (6, 0.62, 0.72, 0.0), (2, 0.22, 1.0, 0.0)))
    tip_k = 0.35 if flat else 0.1  # flat pads: clearly pointed leaf tips
    for mx, my, hd, la, lb, t, mdrop in lobe_specs:
        ch, sh = math.cos(hd), math.sin(hd)
        pts = []
        # rim (sunk a little into the rock), mid ring, low crown: a flat leaf pad
        for nn, rf, hf, sink in rings:
            p0 = rng.uniform(0, TAU) if nn < 10 else 0.0
            for k in range(nn):
                ang = p0 + TAU * (k + rng.uniform(-0.12, 0.12)) / nn
                tip = 1 + tip_k * max(0.0, math.cos(ang)) ** 6  # a pointed leaf tip
                u = la * rf * math.cos(ang) * tip * rng.uniform(0.9, 1.08)
                v = lb * rf * math.sin(ang) * rng.uniform(0.9, 1.08)
                s = 1.0
                # keep the lobe on the plateau / shoulder: at most max_drop below the pad centre
                while s > 0.1 and ground(mx + s * (u * ch - v * sh), my + s * (u * sh + v * ch)) < z0 - mdrop:
                    s *= 0.9
                x, y = mx + s * (u * ch - v * sh), my + s * (u * sh + v * ch)
                pts.append(Vector((x, y, ground(x, y) - sink + t * hf * rng.uniform(0.85, 1.15))))
        rk = hull_rock(pts)
        if not closed:
            for f in [f for f in rk.bm.faces if f.normal.z < -0.25]:
                rk.bm.faces.remove(f)
        append_rock(a, rk, lambda f: (MOSS, tint(rng)))
        rk.bm.free()


def top_centre(rock, below=0.5):
    tc = [v.co for v in rock.bm.verts if v.co.z > rock.zmax - below]
    return sum(v.x for v in tc) / len(tc), sum(v.y for v in tc) / len(tc)


# ---------------------------------------------------------------------------
# Clover leaves, clumps, flowers
# ---------------------------------------------------------------------------

# a rounded, slightly heart-tipped leaf outline in (along, across) units
LEAF_OUTLINE = ((0.0, 0.0), (0.26, 0.42), (0.66, 0.52), (0.98, 0.26), (0.9, 0.0),
                (0.98, -0.26), (0.66, -0.52), (0.26, -0.42))


def leaf(a, b, d, L, W, mat, t=1.0, cup=0.13, droop=0.12, face=None):
    """Closed rounded clover leaf (12 tris) from base b along d: a cupped fan
    (rim raised, centre low) over a flat-ish underside, one colour."""
    bm = a.bm
    d = Vector(d).normalized()
    side = d.cross(Vector(face)) if face is not None else d.cross(Z)
    if side.length < 1e-4:
        side = Vector((1, 0, 0))
    side.normalize()
    up = side.cross(d).normalized()
    b = Vector(b)
    rim = []
    for u, v in LEAF_OUTLINE:
        p = b + d * L * u + side * W * v + up * W * cup * abs(v) / 0.52 - up * L * droop * u * u
        rim.append(bm.verts.new(p))
    C = bm.verts.new(b + d * L * 0.55 - up * L * droop * 0.3 + up * W * 0.03)
    n = len(rim)
    tops = [bm.faces.new((C, rim[k], rim[(k + 1) % n])) for k in range(n)]
    under = bm.faces.new(list(reversed(rim)))
    bmesh.ops.recalc_face_normals(bm, faces=tops + [under])
    for f in tops + [under]:
        put(a, f, mat, t)
    return rim + [C]


def leaf_mass(a, rng, c, rx, rz):
    """A rounded faceted leaf mass (~20 tris): the hull of a base ring, a mid
    ring and a two-point crown around c, its buried underside dropped."""
    pts = []
    for n, zf, rf in ((6, -0.45, 1.0), (5, 0.3, 0.85), (2, 0.85, 0.35)):
        ph = rng.uniform(0, TAU)
        for k in range(n):
            th = ph + TAU * (k + rng.uniform(-0.15, 0.15)) / n
            rr = rf * rng.uniform(0.9, 1.08)
            pts.append(Vector((c.x + rx * rr * math.cos(th), c.y + rx * rr * math.sin(th),
                               max(0.0, c.z + rz * zf * rng.uniform(0.9, 1.1)))))
    rk = hull_rock(pts)
    for f in [f for f in rk.bm.faces if f.normal.z < -0.9 and f.calc_center_median().z < 0.02]:
        rk.bm.faces.remove(f)
    append_rock(a, rk, lambda f: (LEAF, tint(rng)))
    rk.bm.free()


def bush(a, rng, rocks, centre, th, width, height, flowers=0, flower_r=0.42):
    """A bushy clover bank at the rock foot along azimuth th, ~width x height
    studs: overlapping rounded leaf masses, each set against the rock wall at
    its own height (so the bank climbs the rock instead of sitting out on the
    ground), shingled with rounded clover leaves that look up and out, with
    optional white daisies on the outermost crowns."""
    W, H = width, height
    big = W >= 2.6
    r_foot = max(edge_radius(rocks, centre, th, zs=(0.1,)), 1.0)
    # (along tangent, centre height, size) in units of W / H / W
    if big:
        lay = [(0.0, 0.66, 0.24), (-0.25, 0.46, 0.24), (0.24, 0.44, 0.24), (-0.42, 0.2, 0.2),
               (0.42, 0.2, 0.2), (-0.13, 0.2, 0.24), (0.14, 0.22, 0.23)]
    else:
        lay = [(0.0, 0.5, 0.3), (-0.28, 0.3, 0.27), (0.28, 0.28, 0.27)]
    crowns = []
    for u, zf, sf in lay:
        t_i = th + u * W * rng.uniform(0.9, 1.1) / r_foot
        out = Vector((math.cos(t_i), math.sin(t_i), 0))
        tang = Z.cross(out)
        rx = sf * W * rng.uniform(0.92, 1.08)
        rz = rx * 0.8
        zc = zf * H * rng.uniform(0.94, 1.06)
        rw = edge_radius(rocks, centre, t_i, zs=(max(0.1, zc - rz * 0.4), zc))
        c = Vector((centre.x, centre.y, 0)) + out * (rw + rx * (0.2 + 0.3 * (1 - zf))) + Z * zc
        leaf_mass(a, rng, c, rx, rz)
        # clover leaves on the mass's upper outer surface
        for k in range(3 if big else 2):
            hor = (out * rng.uniform(0.5, 1.0) + tang * rng.uniform(-0.9, 0.9)).normalized()
            base = c + hor * rx * rng.uniform(0.15, 0.45) + Z * rz * rng.uniform(0.55, 0.75)
            pitch = rng.uniform(0.25, 0.6)
            d = hor * math.cos(pitch) + Z * math.sin(pitch)
            L = min(rx * 1.15, 0.82) * rng.uniform(0.85, 1.1)
            if any(r.inside(base + d * L * 0.6, 0.05) for r in rocks):
                continue
            fn = (Z * 0.9 + hor * 0.45).normalized()
            leaf(a, base - d * L * 0.2, d, L, L, LEAF, tint(rng), cup=0.18,
                 droop=0.15, face=fn)
        crowns.append((c + Z * rz * 0.85, out))
    # flowers on the low front masses of the bank (then the mid ones), where they show
    order = [5, 6, 1, 2] if big else [1, 2, 0]
    for i in order[:flowers]:
        p, out = crowns[i]
        flower(a, rng, p + out * (0.3 + flower_r - 0.42) + Z * (0.25 + flower_r - 0.42), R=flower_r,
               n=out * 0.6 + Z)


def flower(a, rng, c, R=0.26, n=None):
    """Five-petal white star (closed, 20 tris) with a yellow pyramid centre (10 tris),
    facing n (default straight up; tilt it outward so the daisy faces the viewer)."""
    bm = a.bm
    c = Vector(c)
    e3 = Z.copy() if n is None else Vector(n).normalized()
    e1 = Vector((1, 0, 0)) if abs(e3.x) < 0.9 else Vector((0, 1, 0))
    e1 = (e1 - e3 * e1.dot(e3)).normalized()
    e2 = e3.cross(e1)

    def P(x, y, z):
        return c + e1 * x + e2 * y + e3 * z

    ph = rng.uniform(0, TAU)
    ring = []
    for k in range(10):
        ang = ph + TAU * k / 10
        rr = R if k % 2 == 0 else R * 0.45
        ring.append(bm.verts.new(P(rr * math.cos(ang), rr * math.sin(ang),
                                   R * 0.12 if k % 2 == 0 else 0.0)))
    top = bm.verts.new(P(0, 0, R * 0.08))
    faces = [bm.faces.new((top, ring[k], ring[(k + 1) % 10])) for k in range(10)]
    faces.append(bm.faces.new(list(reversed(ring))))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    for f in faces:
        put(a, f, "flower_white", rng.uniform(0.97, 1.03))
    base = [bm.verts.new(P(R * 0.3 * math.cos(ph + TAU * k / 5 + 0.3),
                           R * 0.3 * math.sin(ph + TAU * k / 5 + 0.3), R * 0.04))
            for k in range(5)]
    apex = bm.verts.new(P(0, 0, R * 0.3))
    pf = [bm.faces.new((apex, base[k], base[(k + 1) % 5])) for k in range(5)]
    pf.append(bm.faces.new(list(reversed(base))))
    bmesh.ops.recalc_face_normals(bm, faces=pf)
    for f in pf:
        put(a, f, "flower_yellow", 1.0)


# ---------------------------------------------------------------------------
# Base dressing
# ---------------------------------------------------------------------------


def edge_radius(rocks, centre, th, zs=(0.15, 0.7, 1.3)):
    """Distance from centre along th to the outside of every rock, at the widest of
    the low heights zs (so dressing clears any bulge above the foot)."""
    dx, dy = math.cos(th), math.sin(th)
    best = 0.0
    for z in zs:
        r, last = 0.0, 0.0
        while r < 12:  # the outermost rock surface (a ray may cross a gap first)
            if any(rk.inside((centre.x + dx * r, centre.y + dy * r, z)) for rk in rocks):
                last = r + 0.05
            r += 0.05
        best = max(best, last)
    return best


def rubble(a, rng, rocks, centre, th, s, out=0.3, tall=0.56):
    """A chunky faceted rubble stone of about s studs at the rock foot along th."""
    r = edge_radius(rocks, centre, th, zs=(0.1, 0.4)) + s * out
    stone_at(a, rng, (centre.x + r * math.cos(th), centre.y + r * math.sin(th), 0.0), s, tall)


def clump(a, rng, rocks, centre, th, width=2.0, height=1.2, flowers=0, flower_r=0.42):
    """A bushy clover clump of about width x height studs at the rock foot along
    azimuth th (see bush), with optional white daisies on its outer crowns."""
    bush(a, rng, rocks, Vector((centre.x, centre.y, 0)), th, width, height, flowers, flower_r)


def dress(a, rng, rocks, centre, clumps, stones, stone_out=0.3, stone_tall=0.56, flower_r=0.42):
    with dressing(a):
        for th, width, height, fl in clumps:
            clump(a, rng, rocks, centre, math.radians(th), width, height, fl, flower_r)
        for th, s in stones:
            rubble(a, rng, rocks, centre, math.radians(th), s, stone_out, stone_tall)


def floor_clamp(a):
    for v in a.bm.verts:
        if v.co.z < 0.0:
            v.co.z = 0.0


def new_asset(kit, name, seed):
    a = kit.flintkit.Asset(name, CAT, seed=seed)
    a._w01 = Painter(a)
    return a


def companion(rng, rock, az, rx, ry, h, overlap=0.5):
    """A chunky faceted companion stone leaning against rock's foot at az."""
    th = math.radians(az)
    r = edge_radius([rock], rock.centre, th, zs=(0.1, h * 0.5)) + rx * 0.9 - overlap
    loc = (rock.centre.x + r * math.cos(th), rock.centre.y + r * math.sin(th), 0.0)
    pts = rock_points(rng, rx, ry, h, jitter=0.07,
                      spec=[(0.0, 8, 1.0), (0.4, 7, 0.97), (0.75, 6, 0.78), (0.95, 4, 0.5)],
                      crown=2, crown_r=0.3, crown_z=(0.95, 1.0))
    return hull_rock(pts, loc)


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

HERO_SEED = 11
# moss cap: a slab right of centre on the plateau, its lobes draping over the
# front-right shoulder
CAP = dict(c=(0.45, -1.0), R=1.72, lobes=9, thick=0.48, drape_dir=-55, drape=0.6, max_drop=0.4,
           droop=0.6, flat=True)

DRESSED_COLLISION = "precise"
DRESSED_NOTES = ("collision is PreciseConvexDecomposition of the whole mesh, so the rock, moss cap and "
                 "the base clumps, flowers and rubble all collide close to their own surfaces (no hull "
                 "wall around the dressing). The dressing faces carry kit_nocollide=1, which the current "
                 "exporter ignores; once it splits them off, use hull.")


def hero_rock():
    rng = random.Random(HERO_SEED)
    # broad near-vertical lower wall bulging a little at ~1/3 height, long sloping
    # shoulders and a wide flat plateau (the top ring at ~58% of the radius)
    rx, ry, h = 4.35, 3.6, 5.3
    spec = [(0.0, 10, 0.97), (0.3, 10, 1.02), (0.58, 9, 0.96), (0.82, 8, 0.84), (1.0, 7, 0.67)]
    pts = even_rings(rng, rx, ry, h, spec)
    # the front-left crease: a column of extra hull points, pulled in after the chisel
    th = math.radians(CREASE_AZ)
    col = []
    for t, depth in ((0.18, 0.55), (0.5, 0.85), (0.8, 0.6)):
        rf = ring_rf(spec, t) * 1.04
        col.append((Vector((rx * rf * math.cos(th), ry * rf * math.sin(th), t * h)), depth))
    rock = hull_rock(pts + [p for p, _d in col])
    crease = [(min(rock.bm.verts, key=lambda v: (v.co - p).length), d) for p, d in col]
    # full chisel on the walls, gentle on the shoulder and plateau rings (level top)
    chisel(rock, rng, 0.42, keep={v for v, _d in crease}, band_amp=(0.55, 0.85, 0.85, 0.4, 0.25))
    push_in(rock, crease)
    return rock


CREASE_AZ = -116
# (azimuth deg, width, height, flowers): two main bushy banks (front-left, right
# front) climbing ~1/3 up the rock, and smaller clumps filling the ring round the foot
HERO_CLUMPS = [(-152, 3.6, 2.7, 2), (-8, 3.1, 2.7, 1), (-104, 1.7, 1.0, 0),
               (55, 1.8, 1.0, 0), (100, 1.8, 1.0, 0), (140, 1.9, 1.1, 0), (178, 1.8, 1.0, 0)]
# (azimuth deg, size): a big stone at the front-left foot, two at the right foot
HERO_STONES = [(-124, 1.25), (-102, 0.8), (-52, 1.0), (-30, 0.85), (160, 0.9), (35, 0.9)]
SMUDGE = dict(az=-140, z=1.1, w=0.85, h=1.5, n=7, seed=3)


def build_hero(kit, rock, paint):
    a = new_asset(kit, "Boulder", 101)
    append_rock(a, rock, paint())
    smudge(a, rock, **SMUDGE)
    moss_pad(a, rock, 21, **CAP)
    rng = random.Random(31)
    dress(a, rng, [rock], Vector((0, 0, 0)), clumps=HERO_CLUMPS, stones=HERO_STONES,
          stone_out=0.55, stone_tall=0.72, flower_r=0.58)
    floor_clamp(a)
    return a.finish()


def build_main_rock(kit, rock, paint):
    a = new_asset(kit, "BoulderMainRock", 102)
    append_rock(a, rock, paint())
    smudge(a, rock, **SMUDGE)
    floor_clamp(a)
    return a.finish()


def build_moss_cap(kit, rock):
    a = new_asset(kit, "BoulderMossCap", 103)
    moss_pad(a, rock, 21, closed=True, **CAP)
    return a.finish()


def build_flat(kit):
    rng = random.Random(41)
    rock = hull_rock(rock_points(rng, 4.8, 3.7, 3.4, jitter=0.06,
                                 spec=[(0.0, 10, 0.97), (0.35, 9, 1.0), (0.68, 8, 0.9), (1.0, 7, 0.6)],
                                 crown=0))
    chisel(rock, rng, 0.34)
    rock.dent(-120, 22, 0.4, 3.0, 0.5)
    a = new_asset(kit, "BoulderFlat", 104)
    append_rock(a, rock, rock_painter(6))
    moss_pad(a, rock, 22, c=(0.6, -0.4), R=1.9, lobes=7, thick=0.55, drape_dir=-60, drape=0.35, max_drop=0.8)
    dress(a, rng, [rock], Vector((0, 0, 0)),
          clumps=[(-160, 2.9, 1.7, 2), (-22, 2.9, 1.7, 1), (-100, 1.6, 0.9, 0), (40, 1.8, 1.0, 0),
                  (100, 1.7, 0.9, 0), (150, 1.9, 1.0, 0)],
          stones=[(-130, 1.0), (-80, 0.9), (-40, 0.9), (120, 0.9)])
    floor_clamp(a)
    rock.bm.free()
    return a.finish()


def build_upright(kit):
    rng = random.Random(51)
    # a tall faceted peak: broad foot tapering to a blunt plateau ~1/3 of the base width
    rock = hull_rock(rock_points(rng, 3.0, 2.8, 7.7, jitter=0.06,
                                 spec=[(0.0, 9, 0.98), (0.28, 8, 1.0), (0.55, 8, 0.86), (0.8, 7, 0.65),
                                       (1.0, 5, 0.38)],
                                 crown=0, lean=(0.03, 0.02)))
    chisel(rock, rng, 0.3)
    comp = companion(rng, rock, -50, 1.3, 1.15, 1.9, overlap=0.6)
    a = new_asset(kit, "BoulderUpright", 105)
    append_rock(a, rock, rock_painter(7))
    append_rock(a, comp, rock_painter(17))
    cx, cy = top_centre(rock)
    moss_pad(a, rock, 23, c=(cx, cy), R=1.2, lobes=5, thick=0.55, max_drop=0.7)
    # a moss streak down the front face, and a short second one
    streak(a, rock, -78, 1.4, 6.8, w=1.0, seed=4)
    streak(a, rock, -112, 0.9, 3.4, w=0.8, seed=5)
    smudge(a, rock, -84, 3.2, w=1.3, h=1.4, n=7, seed=7)  # patches that widen the streak down the face
    smudge(a, rock, -72, 5.2, w=1.0, h=1.2, n=6, seed=8)
    dress(a, rng, [rock, comp], Vector((0, 0, 0)),
          clumps=[(-150, 2.7, 2.0, 1), (-88, 1.9, 1.4, 1), (-15, 2.5, 1.8, 0), (60, 1.7, 0.9, 0),
                  (150, 1.8, 1.0, 0)],
          stones=[(-128, 0.8), (110, 0.7)])
    floor_clamp(a)
    rock.bm.free()
    comp.bm.free()
    return a.finish()


def build_split(kit):
    rng = random.Random(61)
    big = hull_rock(rock_points(rng, 3.1, 2.9, 6.3, jitter=0.05,
                                spec=[(0.0, 9, 1.0), (0.3, 8, 0.97), (0.6, 8, 0.88), (0.82, 7, 0.72),
                                      (1.0, 5, 0.52)], crown=1, crown_r=0.1, lean=(-0.04, 0.0)))
    chisel(big, rng, 0.28)
    # the two split faces lean apart toward the top: an open V-shaped gap
    big.cut(Vector((1, 0.06, 0.12)).normalized(), Vector((0.8, 0, 0)))
    big.cut(Vector((0.15, -0.05, 1)).normalized(), Vector((0, 0, 5.8)))
    # the shorter piece (~half the left one's height), broad at the base, set well apart
    small = hull_rock(rock_points(rng, 2.3, 2.2, 2.6, jitter=0.07,
                                  spec=[(0.0, 8, 1.0), (0.45, 7, 0.98), (0.8, 6, 0.78), (1.0, 4, 0.5)],
                                  crown=0))
    chisel(small, rng, 0.22)
    small.cut(Vector((-1, -0.06, 0.12)).normalized(), Vector((-1.0, 0, 0)))
    small.move((2.3, -0.35, 0))  # open split ~0.7 studs at the foot, wider at the small top
    a = new_asset(kit, "BoulderSplit", 106)
    append_rock(a, big, rock_painter(8))
    append_rock(a, small, rock_painter(9))
    moss_pad(a, big, 24, c=top_centre(big), R=1.3, lobes=5, thick=0.55, max_drop=0.6)
    sx, sy = top_centre(small, 0.6)
    moss_pad(a, small, 25, c=(sx + 0.2, sy - 0.1), R=1.35, lobes=6, thick=0.5, max_drop=1.1,
             drape_dir=-20, drape=0.5)
    smudge(a, big, -150, 1.2, w=1.3, h=1.0, n=7, seed=6)
    with dressing(a):  # rubble in the foot of the split
        stone_at(a, rng, (1.15, -1.9, 0.0), 0.7)
        stone_at(a, rng, (1.2, 1.6, 0.0), 0.55)
    centre = Vector((0.7, 0, 0))
    dress(a, rng, [big, small], centre,
          clumps=[(-160, 2.7, 1.9, 1), (-25, 2.3, 1.6, 1), (-120, 1.7, 1.0, 0), (30, 1.7, 0.9, 0),
                  (160, 1.8, 1.0, 0), (95, 1.6, 0.9, 0)],
          stones=[(-70, 0.7), (165, 0.7)])
    floor_clamp(a)
    big.bm.free()
    small.bm.free()
    return a.finish()


def build(kit):
    rock = hero_rock()

    def paint():  # the same facet colours on the hero and on its main-rock part
        return rock_painter(5)

    hero = kit.tag(build_hero(kit, rock, paint), "hero", collision=DRESSED_COLLISION, notes=DRESSED_NOTES)
    main = kit.tag(build_main_rock(kit, rock, paint), "part", collision="hull",
                   notes="the hero's rock alone (no moss cap, no dressing), with its low moss smudge")
    cap = kit.tag(build_moss_cap(kit, rock), "part", collision="hull",
                  notes="lumpy moss pad (overlapping closed mound shells); sits on BoulderMainRock's top "
                        "at the hero placement")
    rock.bm.free()
    flat = kit.tag(build_flat(kit), "variant", collision=DRESSED_COLLISION, notes=DRESSED_NOTES)
    upright = kit.tag(build_upright(kit), "variant", collision=DRESSED_COLLISION,
                      notes="with a companion stone at its front-right foot; " + DRESSED_NOTES)
    split = kit.tag(build_split(kit), "variant", collision=DRESSED_COLLISION,
                    notes="two rock pieces (precise also keeps the split open, a hull would bridge it); "
                          + DRESSED_NOTES)
    objs = [hero, main, cap, flat, upright, split]
    if os.environ.get("W01_DEBUG"):
        for o in objs:
            print("W01DBG", o.name, [round(d, 2) for d in o.dimensions[:]], o.get("tris"))
    return objs
