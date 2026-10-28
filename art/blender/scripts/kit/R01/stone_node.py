"""R01 row 1, STONE: the plain grey stone node.

StoneNode (hero) is one big chiselled grey boulder (broad and planted from the
front with near-vertical lower walls, an upright egg from the side, crown a
little left of centre) with three low, flat-topped angular support rocks seated
against its foot. Parts: StoneNodeMainRock (exactly the hero's rock),
StoneNodeSupportRock. Drops: StoneChunk (a wedge with a broad flat face and a
sharp ridge), StoneChunkB (a rounder faceted lump). Depleted: StoneNodeDepleted
(a low, broken, angular mound on the hero's footprint with angular rocks
clustered at both ends).

Every rock is a convex polyhedron cut from explicit planes, arranged in rings
(near-vertical walls, shoulder rings, crown planes), plus the ground plane z=0.
The main rock's planes touch a target surface (a broad ellipsoid cut at the
ground, egg-shaped from the side, crown leaning left) at chosen heights along
its normal; the small rocks' planes are tangent to ellipsoids. Every plane becomes one big flat chisel face, and neighbouring
planes meet at long straight ridges, giving the reference's few-big-planes look
and an angular polygonal outline from every side.

Colour: one flat stone colour with a small random, quantised Tint per plane.
The reference's light tops and darker sides are lighting on the big planes, so
no plane is painted by its direction.
"""

import json
import math
import random

import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

SUBJECT = "StoneNode"
ROW = 1
# The reference's rendered stone mid-tone (#998882 median on the lit hero) is
# darker than ore_stone renders here, so the node uses a sampled, slightly
# darker warm grey. One flat colour; the renderer does the light and dark.
PALETTE = {
    "r01_stone": ("#877C78", 0.9, 0, 0),  # Stone node rock: reference lit mid-tone, one flat warm grey
}

BASE = "r01_stone"
TINT_VAR = 0.04  # random per-plane Tint jitter, never by face direction
# Chip colours sampled from the reference: lit warm grey and shadow grey.
CHIPS = ["#AA9E99", "#635F60"]
DUST = ["#C9C0BA", "#A39A95"]

# Main rock: a target surface (boulder_surface) cut by plane rings. Each plane
# touches the surface at a chosen height and parametric azimuth, along the
# surface normal there, so the walls stand near vertical to about half height,
# the shoulder rings slope in and the crown leans left (MAIN_PEAK_X).
# The reference is a geodesic boulder: a broad ellipsoid cut flat at the
# ground, walls near vertical through the lower third (widest at ~25% height)
# and a dome curving in steadily above to a crown left of centre.
MAIN_R = (3.02, 2.02, 4.62)  # half-width, half-depth at the base; target height (tangent planes add ~0.1)
MAIN_LEAN = (0.0, 0.03)  # how much the X / Y walls lean in up to the dome
MAIN_Z0X = 1.2  # left/right: vertical wall to the equator, then an elliptic dome
MAIN_Z0Y = 0.9  # front/back start curving in lower: an upright egg from the side
MAIN_PV = (2.0, 1.75)  # dome profile exponent in X (broad elliptic dome) and Y (narrower egg top)
MAIN_PEAK_X = -0.9  # crown leans left; the right shoulder falls long
MAIN_TOP = 4.66  # crown cap height (the main rock is 4.7 tall)
# Few big planes: 30 cuts in 5 staggered rings (normal elevations about 0, 22,
# 45, 65 deg and a small top face), so neighbouring rings read as distinct
# light/dark steps and meet at long straight ridges in a geodesic (triangle,
# diamond and pentagon) pattern. (height, parametric azimuths; -90 = front -Y)
MAIN_RINGS = [
    (1.0, [-112, -70, -28, 15, 58, 100, 142, -178, -145]),  # near-vertical walls (front ridge between -112 and -70)
    (2.6, [-132, -91, -49, -7, 36, 79, 121, 165]),          # lower shoulder ring, staggered: triangular facets
    (3.7, [-112, -62, -10, 45, 100, 155, -160]),            # upper shoulder ring
    (4.3, [-140, -60, 20, 95]),                             # crown ring
    (4.58, [-95]),                                          # small top face (left of centre, with the lean)
]
MAIN_SEED = 7

# Support rocks: (loc, size (w, d, h), seed, yaw) - front-left, front-right,
# back-left (as in the reference top view).
SUPPORTS = [
    ((-2.65, -1.6), (1.5, 1.3, 0.95), 21, 0.3),
    ((2.7, -1.5), (1.45, 1.25, 0.85), 22, 1.2),
    ((-2.55, 1.55), (1.35, 1.15, 0.8), 23, 2.2),
]


# ---------------------------------------------------------------------------
# Plane polyhedra
# ---------------------------------------------------------------------------


def ell_plane(el, az, centre, radii):
    """Plane (n, d) with n.p <= d, tangent to the ellipsoid at direction (az, el)."""
    e, a = math.radians(el), math.radians(az)
    n = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))
    rx, ry, rz = radii
    d = n.dot(Vector(centre)) + math.sqrt((rx * n.x) ** 2 + (ry * n.y) ** 2 + (rz * n.z) ** 2)
    return n, d


def flat_plane(nx, ny, h):
    """A flat (slightly tilted) top cut through (0, 0, h)."""
    n = Vector((nx, ny, 1.0)).normalized()
    return n, n.z * h


def plane_points(planes):
    """Vertices of the convex polyhedron {p : n.p <= d for all planes, z >= 0}."""
    planes = list(planes) + [(Vector((0, 0, -1)), 0.0)]
    pts = []
    m = len(planes)
    for i in range(m):
        for j in range(i + 1, m):
            for k in range(j + 1, m):
                (n1, d1), (n2, d2), (n3, d3) = planes[i], planes[j], planes[k]
                mat = Matrix((n1, n2, n3))
                if abs(mat.determinant()) < 1e-6:
                    continue
                p = mat.inverted() @ Vector((d1, d2, d3))
                if all(n.dot(p) <= d + 1e-5 for n, d in planes):
                    if all((p - q).length > 1e-3 for q in pts):
                        pts.append(p)
    return pts


def ring_planes(rings, centre, radii, seed, peak_x=0.0, jit_az=7.0, jit_el=3.0, jit_d=0.025):
    """Planes for a ring layout, with small random jitter so no two planes match."""
    rng = random.Random(seed)
    out = []
    for el, azs in rings:
        for az in azs:
            e = el + rng.uniform(-jit_el, jit_el)
            c = (centre[0] + peak_x * math.sin(math.radians(max(0.0, e))) ** 2, centre[1], centre[2])
            n, d = ell_plane(e, az + rng.uniform(-jit_az, jit_az), c, radii)
            out.append((n, d * (1.0 + rng.uniform(-jit_d, jit_d))))
    return out


def boulder_surface(a, z):
    """The target boulder surface at parametric azimuth a (radians) and height z.
    Cross-sections are ellipses. In X the wall stands near vertical (leaning in
    MAIN_LEAN) up to MAIN_Z0X, then a wide low elliptic dome; in Y the dome
    starts lower (MAIN_Z0Y), so the side reads as an egg. The upper part leans
    in X by MAIN_PEAK_X (crown left of centre, long right shoulder)."""
    rx, ry, H = MAIN_R

    def prof(z0, lean, pv):
        if z <= z0:
            return 1.0 - lean * z / z0
        t = min(1.0, (z - z0) / (H - z0))
        return (1.0 - lean) * (1.0 - t ** pv) ** (1.0 / pv)

    # The lean starts at the x wall top, so the left wall stays a wall and the
    # left shoulder still curves in (no vertical cliff on the left).
    u = max(0.0, (z - MAIN_Z0X) / (H - MAIN_Z0X))
    return Vector((MAIN_PEAK_X * u * u + rx * prof(MAIN_Z0X, MAIN_LEAN[0], MAIN_PV[0]) * math.cos(a),
                   ry * prof(MAIN_Z0Y, MAIN_LEAN[1], MAIN_PV[1]) * math.sin(a), z))


def boulder_shape(n_az=64, n_el=40):
    """Dense samples of the target boulder surface (for tangency)."""
    H = MAIN_R[2]
    return [boulder_surface(2 * math.pi * j / n_az, H * i / n_el) for i in range(n_el + 1) for j in range(n_az)]


def surface_planes(rings, shape, seed, jit_az=7.0, jit_z=0.12):
    """One plane per (height, parametric azimuth) on the target surface, along
    the surface normal there (so facets spread evenly over a non-spherical
    boulder), pushed out to touch the sampled shape."""
    rng = random.Random(seed)
    out = []
    for z, azs in rings:
        for az in azs:
            a = math.radians(az + rng.uniform(-jit_az, jit_az))
            zz = z + rng.uniform(-jit_z, jit_z)
            e = 1e-3
            sa = boulder_surface(a + e, zz) - boulder_surface(a - e, zz)
            sz = boulder_surface(a, zz + e) - boulder_surface(a, zz - e)
            n = sa.cross(sz).normalized()
            out.append((n, max(n.dot(p) for p in shape)))
    return out


def main_points():
    """The main rock's vertices: one definition shared by the hero and the part."""
    planes = surface_planes(MAIN_RINGS, boulder_shape(), MAIN_SEED, jit_az=9.0)
    planes.append(flat_plane(0.06, 0.03, MAIN_TOP))  # cap the crown corners at the spec height
    return plane_points(planes)


def support_points(size, seed):
    """A low, angular support rock: 6 near-vertical walls, 5 bevels and a flat top."""
    rng = random.Random(seed)
    sx, sy, sz = size
    a0 = rng.uniform(0, 60)
    planes = []

    def cut(el, az, rho, z, sxy=(1.0, 1.0)):
        """Plane with normal (az, el) through the point at radius rho (scaled by
        the footprint) and height z."""
        e, a = math.radians(el + rng.uniform(-4, 4)), math.radians(az + rng.uniform(-9, 9))
        n = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))
        p = Vector((rho * sx * math.cos(a), rho * sy * math.sin(a), z))
        planes.append((n, n.dot(p) * (1.0 + rng.uniform(-0.04, 0.04))))

    for k in range(6):  # walls leaning ~16 deg from vertical: a lump, not a prism
        cut(16, a0 + 60 * k, 0.5, 0.0)
    for k in range(5):  # bevels round the flat top
        cut(52, a0 + 30 + 72 * k, 0.24, sz)
    planes.append(flat_plane(rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15), sz))
    return plane_points(planes)


# ---------------------------------------------------------------------------
# Hull rocks
# ---------------------------------------------------------------------------


def hull_rock(a, pts, seed=0, loc=(0.0, 0.0), yaw=0.0, merge=1.5):
    """Convex hull of `pts` into the asset, placed at loc and turned by yaw;
    coplanar hull triangles merged back into the chisel planes, then painted."""
    bm = a.bm
    rng = random.Random(seed * 7 + 3)
    c, s = math.cos(yaw), math.sin(yaw)
    vs = [bm.verts.new((loc[0] + p.x * c - p.y * s, loc[1] + p.x * s + p.y * c, max(0.0, p.z))) for p in pts]
    res = bmesh.ops.convex_hull(bm, input=vs, use_existing_faces=False)
    drop = list({g for g in res["geom_interior"] + res["geom_unused"] if isinstance(g, bmesh.types.BMVert)})
    if drop:
        bmesh.ops.delete(bm, geom=drop, context="VERTS")
    faces = [g for g in res["geom"] if isinstance(g, bmesh.types.BMFace) and g.is_valid]
    verts = list({v for f in faces for v in f.verts})
    if merge:
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(merge), verts=verts,
                                 edges=list({e for v in verts for e in v.link_edges}))
        verts = [v for v in verts if v.is_valid]
    faces = sorted({f for v in verts for f in v.link_faces}, key=lambda f: tuple(f.calc_center_median()))
    bm.normal_update()
    paint(a, faces, rng)
    return verts


def paint(a, faces, rng):
    """One flat stone colour with a small random Tint per plane (lighting does
    the light tops and dark sides; Roblox shades by normal)."""
    tl = a.tint_layer
    for f in faces:
        t = round((1.0 + rng.uniform(-TINT_VAR, TINT_VAR)) * 40) / 40
        f.material_index = a._mi(BASE)
        f.smooth = False
        for lp in f.loops:
            lp[tl] = (t, t, t, 1.0)


def main_rock(a, loc=(0.0, 0.0)):
    return hull_rock(a, main_points(), seed=11, loc=loc)


def support_rock(a, loc, size, seed, yaw=0.0):
    return hull_rock(a, support_points(size, seed), seed=seed, loc=loc, yaw=yaw)


# ---------------------------------------------------------------------------
# VFX
# ---------------------------------------------------------------------------


def front_point(obj, x, z, out=0.12):
    """Where a ray from the front (-Y) first hits the mesh at (x, z), local studs."""
    me = obj.data
    tree = BVHTree.FromPolygons([v.co.copy() for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
    hit, _n, _i, _d = tree.ray_cast(Vector((x, -100.0, z)), Vector((0, 1, 0)))
    y = hit.y if hit is not None else min(v.co.y for v in me.vertices)
    return (x, y - out, z)


def emitters(kit, kind, chips, dust):
    em = json.loads(json.dumps(kit.vfx.KINDS[kind]["emitters"]))
    for e in em:
        e["color"] = list(chips if e["name"] == "Chips" else dust)
    return em


# ---------------------------------------------------------------------------
# Drops
# ---------------------------------------------------------------------------


def wedge_points():
    """StoneChunk: an angular wedge. A broad flat face slopes up from the front
    to a sharp straight ridge near the back, with a steep back face, chamfered
    ends and short lower walls."""
    P = []

    def pl(nx, ny, nz, px, py, pz):
        n = Vector((nx, ny, nz)).normalized()
        P.append((n, n.dot(Vector((px, py, pz)))))

    pl(-0.12, -0.62, 0.78, 0.0, -0.5, 0.18)   # the broad flat face
    pl(0.08, 0.8, 0.6, 0.0, 0.3, 0.86)        # steep back face -> ridge along X
    pl(0.0, -1.0, 0.12, 0.0, -0.5, 0.0)       # low front wall
    pl(0.0, 1.0, 0.1, 0.0, 0.45, 0.0)         # back wall
    pl(-1.0, 0.1, 0.35, -0.62, 0.0, 0.0)      # left end
    pl(1.0, -0.15, 0.45, 0.6, 0.0, 0.0)       # right end (leans in more)
    pl(-0.7, -0.7, 0.4, -0.5, -0.4, 0.0)      # front-left chamfer
    pl(0.75, 0.6, 0.45, 0.45, 0.35, 0.0)      # back-right chamfer
    pl(0.6, -0.65, 0.5, 0.42, -0.42, 0.05)    # front-right chamfer
    pl(-0.55, 0.45, 0.75, -0.4, 0.25, 0.75)   # broken top-left end of the ridge
    return plane_points(P)


def lump_points():
    """StoneChunkB: a rounder, many-planed lump with a small flat top cap."""
    rings = [
        (8, [-80, -20, 40, 100, 160, -140]),
        (42, [-110, -50, 10, 70, 130, -170]),
    ]
    planes = ring_planes(rings, (0.0, 0.0, 0.45), (0.56, 0.5, 0.6), seed=33, jit_az=10.0, jit_el=5.0)
    planes.append(flat_plane(0.12, -0.1, 0.98))
    return plane_points(planes)


def mound_points():
    """Depleted: a low, wide, broken angular mound ~5 x 4.6 x 2.2 with sloping
    faceted flanks and a flat-ish mined-off top (no vertical walls)."""
    rings = [
        (14, [-90, -45, 0, 45, 90, 135, 180, -135]),
        (38, [-112, -67, -22, 23, 68, 113, 158, -157]),
        (62, [-90, -30, 30, 90, 150, -150]),
    ]
    # Tangent to a squat ellipsoid centred on the ground: the top cut at 2.3
    # sits below every upper-ring tangent point, so it leaves one broad flat face.
    planes = ring_planes(rings, (0.0, 0.0, 0.0), (2.6, 2.15, 2.95), seed=41, jit_az=8.0, jit_el=4.0, jit_d=0.03)

    def thru(nx, ny, px, py, pz):
        n = Vector((nx, ny, 1.0)).normalized()
        return n, n.dot(Vector((px, py, pz)))

    planes.append(thru(0.03, -0.02, 0.0, 0.0, 2.3))     # one broad flat top where the rock was mined off
    planes.append(thru(-0.55, 0.1, -1.25, 0.0, 2.3))    # a broken bevel down the left end
    planes.append(thru(0.5, 0.15, 1.3, 0.0, 2.3))       # and one down the right end
    planes.append(thru(-0.3, -0.75, -0.7, -1.15, 2.3))  # broken notch off the front-left top edge
    planes.append(thru(0.45, 0.7, 0.6, 1.0, 2.3))       # and one off the back-right top edge
    return plane_points(planes)


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------


def build(kit):
    fk = kit.flintkit
    out = []

    # Hero: main rock plus three support rocks seated against its foot.
    a = fk.Asset("StoneNode", "Kit", seed=101)
    main_rock(a)
    for loc, size, seed, yaw in SUPPORTS:
        support_rock(a, loc, size, seed, yaw)
    hero = a.finish()
    hit = front_point(hero, -0.3, 2.4)
    kit.vfx.add(hero, "harvest_hit", hit, color=CHIPS, emitters=emitters(kit, "harvest_hit", CHIPS, DUST))
    kit.vfx.add(hero, "harvest_deplete", (0.0, 0.0, 0.25), color=CHIPS,
                emitters=emitters(kit, "harvest_deplete", CHIPS, DUST))
    kit.tag(hero, "hero", collision="hull",
            notes=("Stone node, mined standing up. VFX: harvest_hit on the front (-Y) strike face at mid "
                   "height (grey stone chips + dust per tool strike); harvest_deplete at the base "
                   "centre (big chip and dust burst when the node empties, then swap to "
                   "StoneNodeDepleted). No ore_glint: plain stone is not glossy."))
    out.append(hero)

    # Parts
    a = fk.Asset("StoneNodeMainRock", "Kit", seed=102)
    main_rock(a)
    out.append(kit.tag(a.finish(), "part", collision="hull",
                       notes="The node's big chiselled rock on its own (same mesh as in StoneNode), for kit-bashing."))

    a = fk.Asset("StoneNodeSupportRock", "Kit", seed=103)
    loc, size, seed, yaw = SUPPORTS[0]
    support_rock(a, (0.0, 0.0), size, seed, 0.0)
    out.append(kit.tag(a.finish(), "part", collision="hull",
                       notes="Low flat-topped angular support rock seated around the node's foot; scale and turn to vary."))

    # Drops: a wedge and a rounder lump.
    a = fk.Asset("StoneChunk", "Kit", seed=104)
    hull_rock(a, wedge_points(), seed=31)
    out.append(kit.tag(a.finish(), "drop", collision="box",
                       notes="Stone Chunk: the item a stone node gives (wedge with a broad flat face)."))

    a = fk.Asset("StoneChunkB", "Kit", seed=106)
    hull_rock(a, lump_points(), seed=33)
    out.append(kit.tag(a.finish(), "drop", collision="box",
                       notes="Stone Chunk, second shape (rounder lump): swap in at random so dropped chunks vary."))

    # Depleted: a low broken angular mound with angular rocks clustered at both ends.
    a = fk.Asset("StoneNodeDepleted", "Kit", seed=105)
    hull_rock(a, mound_points(), seed=41)
    for loc, size, seed, yaw in (((-2.55, -0.85), (1.75, 1.5, 1.05), 42, 0.5),
                                 ((-2.2, 1.2), (1.5, 1.35, 0.85), 45, 1.1),
                                 ((2.55, -0.7), (1.7, 1.5, 0.95), 43, 1.7),
                                 ((2.25, 1.3), (1.55, 1.35, 0.8), 44, 2.6)):
        support_rock(a, loc, size, seed, yaw)
    out.append(kit.tag(a.finish(), "depleted", collision="hull",
                       notes="Mined-out stone node: low broken rubble base shown until the node respawns."))
    return out
