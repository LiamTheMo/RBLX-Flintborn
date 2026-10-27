"""R01 row 3: CoalNode, a harvestable coal deposit.

A heap of chunky, dark charcoal-black coal lumps (one broad gem-shaped main chunk
flanked by two egg-shaped side chunks leaning outward) sitting on light warm-grey base rocks. Every coal
lump is a gem-cut polytope (gem_bm): explicit tiers of planes (girdle, shoulder, an
apex tier converging to a point, lower) intersected, so it has a few big crisp planes; facet edges
get a thin chamfer that catches the light. The grey rocks are hewn superellipsoids. Faces buried inside a neighbouring chunk and the flat
undersides at z=0 are dropped, so no triangle is spent on hidden geometry.

Assets: CoalNode (hero), CoalMainChunk, CoalSideChunk, CoalNodeBaseRock (parts),
CoalLump and CoalLumpB (drops: a chunky lump and a wedge), CoalNodeDepleted (depleted: the
grey base rocks only). Materials: `coal` (KIT_PALETTE) and `r01_stone` only, one colour each,
with a modest random per-facet Tint (never by face direction); lighting does the shading.
"""

import json
import math
import random

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

SUBJECT = "CoalNode"
ROW = 3
PALETTE = {
    "r01_stone": ("#877C78", 0.9, 0, 0),  # The sheet's one warm-grey stone: every grey base/support rock (same as StoneNode)
}

PI = math.pi
COAL = ("coal",)  # existing KIT_PALETTE key, one colour; thin chamfers stay coal and catch light by geometry
STONE = ("r01_stone",)  # one warm-grey base colour; lighting shades it

# colours of what flies off a strike, sampled from the reference coal facets
CHIP = ["#3A3C43", "#24262B"]
# Tint: a modest random spread per facet (about +/-8%), never chosen by face direction;
# the light/dark facets come from the geometry and the studio light.
COAL_TINT = (0.92, 1.08)
STONE_TINT = (0.94, 1.06)
TINT_STEP = 0.04  # Tint quantum: keeps every colour row within the exporter's tint levels
DUST = ["#55575F", "#3B3D44"]


# ---------------------------------------------------------------------------
# Hewn convex chunks (technique from build_06_rocks_runes_camp.py)
# ---------------------------------------------------------------------------


def plane_cut(bm, n, co):
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=n, clear_outer=True)
    bnd = [e for e in bm.edges if e.is_boundary]
    if bnd:
        bmesh.ops.contextual_create(bm, geom=bnd)


def hewn_bm(size, center=(0.0, 0.0), n=30, p=2.2, taper=0.0, jitter=0.05, tilt=0.12, seed=0,
            sink=0.1, extra=(), lean=(0.0, 0.0), min_nz=-0.4, yaw=0.0, crown=0.0, crown_at=0.7,
            apex=(0.0, 0.0)):
    """Convex chiselled chunk with full extents `size`, base at z=0. `crown` pulls
    the sides in above `crown_at` of the height (1.0: to a point at the top) and
    `apex` shifts that tapering crown sideways, so the chunk ends in a gem tip."""
    rng = random.Random(seed)
    sx, sy, sz = size
    rx, ry = sx / 2, sy / 2
    rz = sz / (2 - sink)
    zc = rz * (1 - sink)
    C = Vector((center[0], center[1], zc))
    cy, sy_ = math.cos(-yaw), math.sin(-yaw)

    def F(P):
        tf = max(0.2, 1 - taper * max(0.0, P.z) / sz)
        k = max(0.0, P.z / sz - crown_at) / (1 - crown_at)
        tf *= max(0.25, 1 - crown * k)
        dx = P.x - C.x - lean[0] * P.z - apex[0] * k
        dy = P.y - C.y - lean[1] * P.z - apex[1] * k
        x = (dx * cy - dy * sy_) / (rx * tf)
        y = (dx * sy_ + dy * cy) / (ry * tf)
        z = (P.z - zc) / rz
        return (abs(x) ** p + abs(y) ** p + abs(z) ** p) ** (1 / p)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    m = 1.6 * max(sx, sy)
    for v in bm.verts:
        v.co = Vector((C.x + v.co.x * m + lean[0] * sz * (v.co.z + 0.5),
                       C.y + v.co.y * m + lean[1] * sz * (v.co.z + 0.5),
                       (v.co.z + 0.5) * sz * 1.1))
    for nrm, pt in extra:
        plane_cut(bm, Vector(nrm).normalized(), Vector(pt))
    ga = PI * (3 - math.sqrt(5))
    planes = []
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n
        if z < min_nz:
            continue
        rr = math.sqrt(max(0.0, 1 - z * z))
        th = ga * i + rng.uniform(-0.3, 0.3)
        d = Vector((rr * math.cos(th) * rx, rr * math.sin(th) * ry, z * rz)).normalized()
        lo, hi = 0.0, 3 * max(sx, sy, sz)
        for _ in range(40):
            t = (lo + hi) / 2
            if F(C + d * t) < 1:
                lo = t
            else:
                hi = t
        P = C + d * lo
        e = 1e-3
        g = Vector(((F(P + Vector((e, 0, 0))) - F(P - Vector((e, 0, 0)))),
                    (F(P + Vector((0, e, 0))) - F(P - Vector((0, e, 0)))),
                    (F(P + Vector((0, 0, e))) - F(P - Vector((0, 0, e)))))).normalized()
        g = (g + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * tilt).normalized()
        P = P - g * rng.uniform(0, jitter) * min(rx, ry, rz)
        planes.append((g, P))
    rng.shuffle(planes)
    for g, P in planes:
        plane_cut(bm, g, P)
    bmesh.ops.dissolve_degenerate(bm, dist=0.05 * min(size), edges=bm.edges[:])
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(2.0), verts=bm.verts[:], edges=bm.edges[:])
    for v in bm.verts:
        v.co.z = max(v.co.z, 0.0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def tier(n, phase, r, z, el, jit_az=7.0, jit_el=5.0, jit_r=0.04):
    """One ring of gem-cut planes: n planes spread round the axis (unit space)."""
    return [("tier", phase + k * 360.0 / n, el, r, z, jit_az, jit_el, jit_r) for k in range(n)]


def gem_bm(size, center, planes, seed=0, lean=(0.0, 0.0), yaw=0.0, unit=(1.0, 1.0)):
    """Convex gem-cut chunk: the intersection of explicit half-spaces built in a unit
    space (girdle radius 1, height 1, base at z=0), then scaled to `size`, turned by
    `yaw`, sheared by `lean` (x/y shift per stud of height) and moved to `center`.
    Each plane: ("tier", azimuth deg, elevation deg, radius, z, jitters) or
    ("raw", normal, point). Scale, turn and shear keep every facet planar, so the
    chunk keeps a few large crisp planes and no rounding."""
    rng = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * 4.0, v.co.y * 4.0, (v.co.z + 0.5) * 1.5))
    cuts = []
    for p in planes:
        if p[0] == "raw":
            cuts.append((Vector(p[1]).normalized(), Vector(p[2])))
            continue
        if p[0] == "apex":
            _, az, el, ap, ja, je = p
            a = math.radians(az + rng.uniform(-ja, ja))
            e = math.radians(el + rng.uniform(-je, je))
            n = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))
            # a hair under the apex so the planes meet in a short ridge, not one vertex
            cuts.append((n, Vector(ap) - n * rng.uniform(0.0, 0.015)))
            continue
        _, az, el, r, z, ja, je, jr = p
        a = math.radians(az + rng.uniform(-ja, ja))
        e = math.radians(el + rng.uniform(-je, je))
        r = r + rng.uniform(-jr, jr)
        n = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))
        cuts.append((n, Vector((r * math.cos(a), r * math.sin(a), z))))
    for n, P in cuts:
        plane_cut(bm, n, P)
    rx, ry = size[0] / 2 / unit[0], size[1] / 2 / unit[1]
    cy, sy = math.cos(yaw), math.sin(yaw)
    for v in bm.verts:
        x, y, z = v.co.x * rx, v.co.y * ry, max(0.0, v.co.z) * size[2]
        x, y = x * cy - y * sy, x * sy + y * cy
        v.co = Vector((center[0] + x + lean[0] * z, center[1] + y + lean[1] * z, z))
    bmesh.ops.dissolve_degenerate(bm, dist=0.03, edges=bm.edges[:])
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts[:], edges=bm.edges[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def finish_chunk(bm, mats, seed=0, bevel=0.03, base_tint=(0.94, 1.06)):
    """ONE base material (index 0) on every facet with a small random Tint that never
    depends on face direction (lighting does the light/dark), plus thin chamfers along
    every edge above the ground in the SAME material: they catch light by geometry."""
    rng = random.Random(seed)
    tl = bm.loops.layers.float_color.get("Tint") or bm.loops.layers.float_color.new("Tint")
    bm.normal_update()
    zmin = min(v.co.z for v in bm.verts)

    def put(f, mi, t):
        f.material_index = mi
        f.smooth = False
        for lp in f.loops:
            lp[tl] = (t, t, t, 1.0)

    for f in bm.faces:
        put(f, 0, rng.uniform(*base_tint))
    edges = [e for e in bm.edges if not all(v.co.z < zmin + 0.02 for v in e.verts)]
    if bevel and edges:
        res = bmesh.ops.bevel(bm, geom=edges, offset=bevel, offset_type="OFFSET", segments=1,
                              profile=0.5, affect="EDGES", clamp_overlap=True)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.normal_update()
        for f in res["faces"]:
            put(f, 0, rng.uniform(*base_tint))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def planes_of(bm):
    bm.normal_update()
    return [(f.normal.copy(), f.calc_center_median()) for f in bm.faces if f.normal.length > 0.5]


def inside(co, planes, eps=0.015):
    return all(n.dot(co - c) < -eps for n, c in planes)


def append_chunk(a, bm, mats, hide_in=(), keep_bottom=False):
    """Copy a finished chunk into asset `a`, skipping its ground face and faces
    buried inside any of the convex volumes in `hide_in` (lists of planes)."""
    tl = bm.loops.layers.float_color.get("Tint")
    bm.normal_update()
    vmap = {}
    for f in bm.faces:
        if not keep_bottom and f.normal.z < -0.99 and all(v.co.z < 0.01 for v in f.verts):
            continue
        if any(all(inside(v.co, pl) for v in f.verts) for pl in hide_in):
            continue
        vs = []
        for v in f.verts:
            if v not in vmap:
                vmap[v] = a.bm.verts.new(v.co)
            vs.append(vmap[v])
        try:
            nf = a.bm.faces.new(vs)
        except ValueError:
            continue
        nf.material_index = a._mi(mats[f.material_index])
        nf.smooth = False
        t = f.loops[0][tl][0] if tl else 1.0
        # snap to a fixed step so every colour row fits the exporter's 32 tint levels
        t = round(round(t / TINT_STEP) * TINT_STEP, 4)
        for lp in nf.loops:
            lp[a.tint_layer] = (t, t, t, 1.0)
    return list(vmap.values())


def assemble(kit, name, category, chunks, seed=0, keep_bottom=False):
    """chunks: [(bm, mats)] already finished. Faces hidden inside another chunk are
    dropped (and the ground face unless keep_bottom, for drops that tumble).
    Returns (asset, offset) where offset is the bottom-centre shift."""
    a = kit.flintkit.Asset(name, category, seed=seed)
    pls = [planes_of(bm) for bm, _ in chunks]
    for i, (bm, mats) in enumerate(chunks):
        append_chunk(a, bm, mats, hide_in=[p for j, p in enumerate(pls) if j != i], keep_bottom=keep_bottom)
        bm.free()
    xs = [v.co.x for v in a.bm.verts]
    ys = [v.co.y for v in a.bm.verts]
    zs = [v.co.z for v in a.bm.verts]
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    return a, off


def socket(kit, obj, kind, p, off, scale=1.0, **kw):
    loc = tuple(p[i] - off[i] for i in range(3))
    return kit.vfx.add(obj, kind, loc, scale=scale, **kw)


def recolour(kind, kit, colours):
    """Copy of a VFX kind's emitters with each emitter's colour replaced."""
    ems = json.loads(json.dumps(kit.vfx.KINDS[kind]["emitters"]))
    for em in ems:
        if em["name"] in colours:
            em["color"] = colours[em["name"]]
    return ems


# ---------------------------------------------------------------------------
# Pieces (positions in hero coordinates, studs; front is -Y)
# ---------------------------------------------------------------------------


HEX = (1.155, 1.0)  # unit extents of a hexagonal girdle with a face to the front (-Y)


def apex_tier(n, phase, el, apex, jit_az=6.0, jit_el=3.0):
    """n crown planes that all pass through (or just under) one apex point, so the
    chunk ends in a gem point instead of a flat table (unit space)."""
    return [("apex", phase + k * 360.0 / n, el, apex, jit_az, jit_el) for k in range(n)]


def main_planes():
    # hexagonal gem with a peak: 6 near-vertical girdle planes (one big hexagonal face to
    # the front), 6 steep shoulder planes offset 30 deg (world slope ~60 deg), and 4 crown
    # planes (world slope ~40 deg) meeting at an apex ~0.4 studs left of centre; 6 lower
    # planes tuck in the foot. Unit space is ~2.8x taller than wide, so unit elevations
    # 58/73 deg make ~60/40 deg world slopes: neighbours differ by 20-40 deg, so lighting
    # separates every plane.
    return (tier(6, -90, 1.0, 0.5, 3, jit_el=2.0)
            + tier(6, -60, 0.95, 0.63, 60, jit_el=3.0, jit_r=0.03)
            + apex_tier(5, -90, 79, (-0.24, 0.04, 1.0), jit_az=8.0)
            + tier(6, -60, 0.9, 0.2, -48, jit_el=4.0))


def main_chunk(c=(0.0, 0.5), seed=301):
    bm = gem_bm((3.95, 3.55, 4.9), c, main_planes(), seed=seed, lean=(-0.03, 0.0), yaw=0.08, unit=HEX)
    return finish_chunk(bm, COAL, seed=seed, bevel=0.025, base_tint=COAL_TINT)


def side_planes():
    # egg gem with a point: girdle widest ~40% up, one shoulder tier (world ~64 deg) and
    # three crown planes (world ~50 deg) meeting at a slightly off-centre apex
    return (tier(6, -90, 1.0, 0.4, 3, jit_el=2.0)
            + tier(6, -60, 0.95, 0.5, 55, jit_el=3.0, jit_r=0.03)
            + apex_tier(4, -45, 74, (0.08, -0.05, 1.0))
            + tier(6, -60, 0.9, 0.16, -50, jit_el=4.0))


def side_chunk(c, size, seed, lean=(0.0, 0.0), yaw=0.0):
    bm = gem_bm(size, c, side_planes(), seed=seed, lean=lean, yaw=yaw, unit=HEX)
    return finish_chunk(bm, COAL, seed=seed, bevel=0.025, base_tint=COAL_TINT)


def base_rock(c, size, seed, n=22, yaw=0.0):
    bm = hewn_bm(size, c, n=n, p=2.5, taper=0.28, sink=0.35, seed=seed, tilt=0.1, jitter=0.08, yaw=yaw,
                 extra=[((0.1, -0.15, 1.0), (c[0], c[1], size[2] * 0.92))])
    return finish_chunk(bm, STONE, seed=seed, bevel=0.02, base_tint=STONE_TINT)


# (centre, size, seed, lean, yaw): egg chunks ~0.65 of the main height, set outward and
# forward of the main chunk so a shadow line separates them, leaning a little outward
SIDE = (2.6, 2.2, 3.15)
LEFT = ((-1.85, -0.45), (2.55, 2.2, 3.0), 311, (-0.19, -0.08), -0.35)
RIGHT = ((1.8, -0.5), (2.55, 2.2, 3.2), 312, (0.17, -0.1), 0.12)
ROCKS = [  # (centre, size, seed, planes)
    ((0.0, -1.6), (3.6, 2.0, 1.6), 321, 26),     # wide low front base rock
    ((-2.8, -1.7), (1.4, 1.3, 1.0), 322, 16),      # front-left rock, out past the side chunk
    ((2.8, -1.65), (1.4, 1.3, 1.05), 323, 16),     # front-right rock
    ((-2.45, 1.45), (1.9, 1.6, 1.2), 324, 18),     # back-left, shows in the top view
    ((2.45, 1.5), (1.7, 1.4, 1.0), 325, 18),       # back-right
]


def build(kit):
    out = []

    # -- hero ----------------------------------------------------------------
    main = main_chunk()
    # ray-cast the main chunk's front (-Y) face so the sockets sit on its surface
    bvh = BVHTree.FromBMesh(main)

    def front(x, z, gap):
        hit = bvh.ray_cast(Vector((x, -20.0, z)), Vector((0.0, 1.0, 0.0)))
        y = hit[0].y if hit[0] is not None else -1.2
        return (x, y - gap, z)

    hit_p = front(0.0, 2.7, 0.1)
    glint_p = front(0.0, 3.8, 0.05)
    chunks = [(main, COAL)]
    for c, s, sd, ln, yw in (LEFT, RIGHT):
        chunks.append((side_chunk(c, s, sd, ln, yw), COAL))
    for c, s, sd, n in ROCKS:
        chunks.append((base_rock(c, s, sd, n), STONE))
    a, off = assemble(kit, "CoalNode", "Resources", chunks, seed=3)
    hero = a.finish()
    # strike face: the front of the main chunk at mid height, above the base rock
    socket(kit, hero, "harvest_hit", hit_p, off,
           color=CHIP, emitters=recolour("harvest_hit", kit, {"Chips": CHIP, "Dust": DUST}))
    socket(kit, hero, "harvest_deplete", (off.x, off.y, 0.0), off,
           color=CHIP, emitters=recolour("harvest_deplete", kit, {"Chips": CHIP, "Dust": DUST}))
    socket(kit, hero, "ore_glint", glint_p, off, scale=0.8,
           color=["#C9CED8", "#8E94A2"], rate=0.3, light_emission=0.4,
           emitters=[dict(kit.vfx.KINDS["ore_glint"]["emitters"][0], color=["#C9CED8", "#8E94A2"],
                          rate=0.3, light_emission=0.4, shape=[2.5, 0.4, 2.0])])
    kit.tag(hero, "hero", collision="hull",
            notes="Mine standing at the front (-Y). VFX_harvest_hit: front face of the main chunk at "
                  "mid height, black/dark-grey coal chips and dark dust on each strike. "
                  "VFX_harvest_deplete: base centre, coal chip and dust burst when the node empties "
                  "(swap to CoalNodeDepleted). VFX_ore_glint: faint grey sheen twinkles over the coal.")
    out.append(hero)

    # -- parts ---------------------------------------------------------------
    a, off = assemble(kit, "CoalMainChunk", "Resources", [(main_chunk((0, 0), 331), COAL)], seed=31)
    out.append(kit.tag(a.finish(), "part", collision="hull", notes="Broad gem-shaped main coal chunk, facets climbing to an apex left of centre."))
    a, off = assemble(kit, "CoalSideChunk", "Resources",
                      [(side_chunk((0, 0), SIDE, 332, (0.0, 0.0), 0.0), COAL)], seed=32)
    out.append(kit.tag(a.finish(), "part", collision="hull", notes="Egg-shaped side coal chunk; lean it outward against a main chunk."))
    a, off = assemble(kit, "CoalNodeBaseRock", "Resources",
                      [(base_rock((-0.55, 0.0), (2.6, 1.9, 1.5), 341, 24), STONE),
                       (base_rock((1.0, 0.25), (1.5, 1.4, 1.75), 342, 18), STONE)], seed=34)
    out.append(kit.tag(a.finish(), "part", collision="hull", notes="Grey base rocks under the coal."))

    # -- drop ----------------------------------------------------------------
    lump = (tier(6, -90, 1.0, 0.45, 4) + tier(6, -60, 0.8, 0.72, 50)
            + [("raw", (0.06, -0.1, 1.0), (0.0, 0.0, 0.97))] + tier(6, -60, 0.85, 0.24, -50))
    wedge = (tier(5, -90, 1.0, 0.4, 5) + tier(5, -54, 0.78, 0.7, 48)
             + [("raw", (0.3, -0.1, 1.0), (0.0, 0.0, 0.85))] + tier(5, -54, 0.85, 0.22, -48))
    for name, size, sd, planes, yaw in (("CoalLump", (1.3, 1.05, 0.9), 352, lump, 0.12),
                                        ("CoalLumpB", (1.25, 1.0, 0.95), 356, wedge, -0.15)):
        bm = gem_bm(size, (0, 0), planes, seed=sd, yaw=yaw, unit=HEX)
        a, off = assemble(kit, name, "Resources",
                          [(finish_chunk(bm, COAL, seed=sd - 1, bevel=0.02, base_tint=COAL_TINT), COAL)], seed=sd,
                          keep_bottom=True)  # closed: drops tumble and show every side
        out.append(kit.tag(a.finish(), "drop", collision="box",
                           notes="Coal lump item the player gets (two shapes; pick either per drop)."))

    # -- depleted ------------------------------------------------------------
    chunks = [(base_rock((0.0, 0.3), (3.4, 2.6, 1.6), 361, 26), STONE),
              (base_rock((-1.95, 1.9), (1.6, 1.3, 0.8), 366, 16), STONE),
              (base_rock((1.85, 2.0), (1.6, 1.3, 0.8), 367, 16), STONE),
              (base_rock((-1.75, -0.6), (1.8, 1.5, 1.05), 362, 18), STONE),
              (base_rock((1.8, -0.35), (2.0, 1.7, 1.25), 363, 18), STONE),
              (base_rock((-2.75, -1.35), (1.55, 1.3, 0.9), 364, 14), STONE),
              (base_rock((2.8, -1.3), (1.55, 1.3, 0.95), 365, 14), STONE)]
    a, off = assemble(kit, "CoalNodeDepleted", "Resources", chunks, seed=36)
    dep = a.finish()
    out.append(kit.tag(dep, "depleted", collision="hull",
                       notes="Mined-out base: grey rocks only, same footprint as CoalNode."))
    return out
