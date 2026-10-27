"""R01 row 2: FLINT resource node.

A pale tan limestone boulder with broad, dark, glossy charcoal flint crystals
lying embedded along its flanks, sitting on a few small warm-grey base rocks.
The player mines it standing up from the front (-Y).

Assets
    FlintNode                hero: shell + 4 flint inserts + 3 grey base rocks
    FlintNodeLimestoneShell  part: the bare limestone shell
    FlintInsert              part: a tall flint crystal with a lower second peak
    FlintInsertSmall         part: a short, broad flint diamond
    FlintInsertThin          part: a slim flint needle
    FlintNodeBaseRock        part: a small grey base rock
    FlintNodeBaseRockSmall   part: a pebble-sized base rock
    FlintFlake               drop: a chunky rhombic flint flake
    FlintFlakeAlt            drop: a second flake shape (random drop look)
    FlintNodeDepleted        depleted: low flat tan limestone slab with grey rocks

The limestone shell is the boolean union (union_bm) of two convex hulls of
hard-jittered points on stacked rings (hull_rock_bm): the main body (straight
steep left flank, short-ridged peak at x ~-1.0) and a lower right shoulder
block whose shelf at z ~3.7 steps out ~0.8 stud past the body, giving ~75 large
crisp planes; the flat underside at z=0 is removed (never seen). FlintInsert is
likewise a union of two hulls (main blade + lower second peak). Base rocks and the depleted slab
are hewn the sheet-06 way (superellipsoid cut by tangent planes).

Each flint crystal gets a flat seat chiselled into the shell (seat_crystal);
the crystal is a convex hull of the footprint corners on that seat plus a 1-2
point apex ridge lifted 0.65-0.8 studs off the seat (0.45-0.57 proud of the
original surface, since the seat is cut ~0.2-0.3 deep), so it reads as a clean 4-6 plane
pyramid/diamond set flat into the rock, never a spike and never swallowed by a
bulge. ONE colour per material, the lit mid-tone: limestone r01_limestone,
flint r01_flint (gloss = low roughness + ore_glint sockets, no painted facet),
grey base rocks r01_stone (the sheet's one stone). Tint is a small random
+/-3% per facet; the lighting shades every face. VFX colour overrides are written into the
emitters themselves (recolour / glint_over): tan + flint chips, cool-white
glints. Every asset is built with its base on z=0.
"""

import json
import math
import random

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

SUBJECT = "FlintNode"
ROW = 2
PALETTE = {
    # sheet keys, verbatim (shared by every R01 module)
    "r01_limestone": ("#C9AE94", 0.9, 0, 0),  # Flint node's pale tan limestone shell and the tan slab of FlintNodeDepleted
    "r01_flint": ("#3A393F", 0.3, 0.1, 0),  # Glossy charcoal flint crystals (inserts) and flint flake drops
    "r01_stone": ("#877C78", 0.9, 0, 0),  # The sheet's one warm-grey stone: every grey base rock under the node
}

PI = math.pi
LIME = ["r01_limestone"]
GREY = ["r01_stone"]
FLINT = ["r01_flint"]
KEY = Vector((-0.49, -0.59, 0.64)).normalized()  # toward the studio key light

HIT_COLORS = ["#C9AE94", "#45444A"]  # tan limestone chips and dark flint chips
DEPLETE_COLORS = ["#C9AE94", "#4A4950"]
GLINT_COLORS = ["#F4F8FF", "#C9D6EA"]  # cool white twinkle on glossy flint
DUST_COLORS = ["#D8C4AE", "#BBA48E"]  # pale limestone dust


def glint_over(kit, rate=0.5):
    """ore_glint overrides with the cool-white colour on the emitter itself."""
    return {"color": GLINT_COLORS, "rate": rate,
            "emitters": recolour(kit, "ore_glint", {"Glint": GLINT_COLORS}, rate=rate)}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def paint(a, faces, mat, tint=1.0):
    mi = a._mi(mat)
    for f in faces:
        f.material_index = mi
        f.smooth = False
        for lp in f.loops:
            lp[a.tint_layer] = (tint, tint, tint, 1.0)


def plane_cut(bm, n, co):
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=n, clear_outer=True)
    bnd = [e for e in bm.edges if e.is_boundary]
    if bnd:
        bmesh.ops.contextual_create(bm, geom=bnd)


def hewn_bm(size, center=(0.0, 0.0), n=40, p=2.4, taper=0.0, jitter=0.05, tilt=0.12, seed=0,
            sink=0.1, lean=(0.0, 0.0), min_nz=-0.4, extra=(), merge=0.04, taper_from=0.0,
            keep_bottom=False):
    """Chiselled chunk with full extents ~`size`, base cut flat at z=0 (after
    sheet 06). `taper` is a number or (tx, ty), applied above z = taper_from *
    height. `keep_bottom` keeps the flat base cap (a closed mesh)."""
    rng = random.Random(seed)
    sx, sy, sz = size
    rx, ry = sx / 2, sy / 2
    rz = sz / (2 - sink)
    zc = rz * (1 - sink)
    C = Vector((center[0], center[1], zc))
    tx, ty = (taper, taper) if isinstance(taper, (int, float)) else taper
    z0 = taper_from * sz

    def F(P):
        h = max(0.0, P.z - z0) / max(1e-3, sz - z0)
        x = (P.x - C.x - lean[0] * P.z) / (rx * max(0.2, 1 - tx * h))
        y = (P.y - C.y - lean[1] * P.z) / (ry * max(0.2, 1 - ty * h))
        z = (P.z - zc) / rz
        return (abs(x) ** p + abs(y) ** p + abs(z) ** p) ** (1 / p)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    m = 1.3
    for v in bm.verts:
        v.co = Vector((C.x + v.co.x * sx * m + lean[0] * sz * (v.co.z + 0.5),
                       C.y + v.co.y * sy * m + lean[1] * sz * (v.co.z + 0.5),
                       (v.co.z + 0.5) * sz * 1.6 - 0.5 * sz))
    plane_cut(bm, Vector((0, 0, -1)), Vector((0, 0, 0)))  # the flat ground cut
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
    bmesh.ops.dissolve_degenerate(bm, dist=merge * min(size), edges=bm.edges[:])
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.5), verts=bm.verts[:], edges=bm.edges[:])
    for v in bm.verts:
        v.co.z = max(v.co.z, 0.0)
    if not keep_bottom:  # the flat underside sits on the ground and is never seen
        for f in [f for f in bm.faces if all(v.co.z < 1e-4 for v in f.verts)]:
            bm.faces.remove(f)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def hull_rock_bm(rings, peak, seed, jitter=0.16, zjit=0.2, p=2.6, egg=0.1, dissolve=6.0,
                 label=None, keep_bottom=False):
    """Angular faceted rock: the convex hull of hard-jittered points on stacked
    rings. Each ring is (z, n, xl, xr, yf, yb, cx): n points on a superellipse
    (exponent p, so the flanks stay broad and flat) with separate left/right/
    front/back half-extents around centre x = cx. Each point is pushed in or out
    radially by up to `jitter` (hard per-vertex noise, so the hull shows crisp
    planes and corners rather than a smooth egg); `egg` swells the front-left
    and pinches the back-right so the top view is an egg. The flat underside at
    z=0 is removed (never seen). Near-coplanar triangles (< `dissolve` deg) are
    merged into larger planes."""
    rng = random.Random(seed)
    bm = bmesh.new()
    vs = []
    for z, n, xl, xr, yf, yb, cx in rings:
        off = rng.uniform(0, 2 * PI)
        for i in range(n):
            th = off + 2 * PI * (i + rng.uniform(-0.28, 0.28)) / n
            c, s = math.cos(th), math.sin(th)
            ex = math.copysign(abs(c) ** (2 / p), c) * (xr if c > 0 else xl)
            ey = math.copysign(abs(s) ** (2 / p), s) * (yb if s > 0 else yf)
            r = (1 + rng.uniform(-jitter, jitter)) * (1 + egg * (-c - s) * 0.707)
            zz = z if z <= 0 else max(0.05, z + rng.uniform(-zjit, zjit))
            vs.append(bm.verts.new(Vector((cx + ex * r, ey * r, zz))))
    for P in peak:
        vs.append(bm.verts.new(Vector(P)))
    res = bmesh.ops.convex_hull(bm, input=vs)
    for g in res.get("geom_interior", []) + res.get("geom_unused", []):
        if isinstance(g, bmesh.types.BMVert) and g.is_valid:
            bm.verts.remove(g)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(dissolve), verts=bm.verts[:], edges=bm.edges[:])
    if not keep_bottom:
        drop_bottom(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    if label:
        shell_stat(bm, label)
    return bm


def union_bm(bms, dissolve=4.0):
    """Boolean union of closed bmeshes (exact solver) into one new bmesh, so two
    convex hulls can make a concave feature (a stepped shoulder, a second peak)
    without hidden interior faces. The inputs are freed."""
    import bpy
    objs = []
    for i, b in enumerate(bms):
        me = bpy.data.meshes.new(f"_flint_tmp{i}")
        b.to_mesh(me)
        b.free()
        ob = bpy.data.objects.new(me.name, me)
        bpy.context.scene.collection.objects.link(ob)
        objs.append(ob)
    base = objs[0]
    for ob in objs[1:]:
        m = base.modifiers.new("union", "BOOLEAN")
        m.operation = "UNION"
        m.object = ob
        m.solver = "EXACT"
    dg = bpy.context.evaluated_depsgraph_get()
    ev = base.evaluated_get(dg)
    me = ev.to_mesh()
    out = bmesh.new()
    out.from_mesh(me)
    ev.to_mesh_clear()
    for ob in objs:
        me = ob.data
        bpy.data.objects.remove(ob)
        bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(out, verts=out.verts[:], dist=1e-4)
    bmesh.ops.dissolve_limit(out, angle_limit=math.radians(dissolve), verts=out.verts[:], edges=out.edges[:])
    bmesh.ops.recalc_face_normals(out, faces=out.faces[:])
    out.normal_update()
    return out


def drop_bottom(bm):
    """Remove the flat underside at z=0 (it sits on the ground, never seen)."""
    for f in [f for f in bm.faces if all(v.co.z < 1e-4 for v in f.verts)]:
        bm.faces.remove(f)
    for v in [v for v in bm.verts if not v.link_faces]:
        bm.verts.remove(v)


def shell_stat(bm, label):
    bm.normal_update()
    angs = [math.degrees(e.link_faces[0].normal.angle(e.link_faces[1].normal))
            for e in bm.edges if len(e.link_faces) == 2]
    print(f"FLINTSTAT {label}: faces={len(bm.faces)} verts={len(bm.verts)} "
          f"mean_dihedral={sum(angs) / max(1, len(angs)):.1f} "
          f"median_dihedral={sorted(angs)[len(angs) // 2]:.1f}")


def seat_crystal(sbm, spec):
    """Chisel a flat seat into the (closed) shell for one crystal and return the
    crystal's points: footprint corners on the seat plane, ridge/apex lifted
    `lift` studs off it. The seat plane's normal is the mean surface normal
    under the footprint, set at the lowest surface point of the footprint, so
    the whole footprint lies on flat limestone and the crystal is a clean 4-6
    plane pyramid/diamond set flat into the rock (never swallowed by a bulge)."""
    tree = BVHTree.FromBMesh(sbm)
    d = Vector(spec["d"]).normalized()
    y0 = spec.get("y0", 0.0)
    plane_pt = (lambda x, z: Vector((x, y0, z))) if abs(d.y) >= abs(d.x) else \
        (lambda x, z: Vector((y0, x, z)))
    foot = spec["foot"]
    hits = [ray_hit(tree, plane_pt(x, z), d) for x, z in foot]
    assert all(hits), f"flint crystal seed {spec['seed']}: a footprint corner misses the shell"
    N = Vector((0, 0, 0))
    for h in hits:
        N += h[1]
    N = (N.normalized() - d * 0.6).normalized()  # lean toward the view it was drawn in
    O = sum((h[0] for h in hits), Vector((0, 0, 0))) / len(hits)
    n = len(foot)
    cx = sum(x for x, _ in foot) / n
    cz = sum(z for _, z in foot) / n
    samples = list(foot) + [(cx, cz)]
    for i in range(n):
        (x1, z1), (x2, z2) = foot[i], foot[(i + 1) % n]
        samples += [((x1 + x2) / 2, (z1 + z2) / 2), ((x1 + cx) / 2, (z1 + cz) / 2)]
    hs = [ray_hit(tree, plane_pt(x, z), d) for x, z in samples]
    heights = [(h[0] - O).dot(N) for h in hs if h]
    # the seat sits part way down the bulge: shallow enough that the shell keeps
    # its volume, while footprint corners in a recess get a short flint side wall
    # down to the surface (the surface hits below join the hull)
    lo = min(heights) + spec.get("seat", 0.45) * (max(heights) - min(heights))
    P0 = O + N * lo
    plane_cut(sbm, N, P0)
    print(f"FLINTSTAT crystal {spec['seed']}: bulge {max(heights) - min(heights):.2f}, "
          f"seat cut {max(heights) - lo:.2f}, apex proud of the old surface "
          f"{max(l for _, _, l in spec['ridge']) - (max(heights) - lo):.2f}")

    def on_plane(x, z, up):
        h = ray_hit(tree, plane_pt(x, z), d)[0]
        return h - N * ((h - P0).dot(N)) + N * up

    pts = [on_plane(x, z, -0.03) for x, z in foot]
    for h in hits:  # corners whose surface lies below the seat: wall down to it
        if (h[0] - P0).dot(N) < -0.05:
            pts.append(h[0] - h[1] * 0.06)
    top = [on_plane(x, z, lift) for x, z, lift in spec["ridge"]]
    return pts, top, N


def tone_stone(bm, seed, var=0.03):
    """One material + a small random Tint per facet (never by face direction):
    the lighting shades the facets."""
    tl = bm.loops.layers.float_color.get("Tint") or bm.loops.layers.float_color.new("Tint")
    rng = random.Random(seed)
    for f in bm.faces:
        t = rng.uniform(1 - var, 1 + var)
        f.material_index = 0
        f.smooth = False
        for lp in f.loops:
            lp[tl] = (t, t, t, 1.0)
    return bm


def append_bm(a, src, mats):
    tl = src.loops.layers.float_color.get("Tint")
    vmap = {v: a.bm.verts.new(v.co) for v in src.verts}
    for f in src.faces:
        try:
            nf = a.bm.faces.new([vmap[v] for v in f.verts])
        except ValueError:
            continue
        t = f.loops[0][tl][0] if tl else 1.0
        paint(a, [nf], mats[f.material_index], t)
    return list(vmap.values())


def add_stone(a, bm, mats, seed, offset=(0, 0, 0)):
    tone_stone(bm, seed)
    bmesh.ops.translate(bm, vec=Vector(offset), verts=bm.verts[:])
    verts = append_bm(a, bm, mats)
    bm.free()
    return verts


def finish(kit, a, role, collision, notes, sockets=(), budget=None):
    """Bottom-centre the mesh, write it, tag it, then add sockets (given in build
    coordinates, shifted with the re-origin)."""
    bm = a.bm
    for v in bm.verts:
        v.co.z = max(v.co.z, 0.0)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    c = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    obj = a.finish(collection=None)
    kit.tag(obj, role, collision=collision, budget=budget, notes=notes)
    for kind, p, scale, over in sockets:
        kit.vfx.add(obj, kind, tuple(Vector(p) - c), scale, **over)
    return obj


# ---------------------------------------------------------------------------
# flint crystals: convex hull, glossy charcoal with lit key facets
# ---------------------------------------------------------------------------


def crystal_bm(pts, seed, open_verts=None, open_dir=None):
    """Convex hull of `pts` in its own bmesh. Faces whose verts are all in
    `open_verts` (indices: the footprint sitting on a host) are removed so the
    crystal is open where it is buried. One glossy flint key, small random Tint:
    the broad soft highlights come from the low roughness, not paint."""
    rng = random.Random(seed)
    bm = bmesh.new()
    tl = bm.loops.layers.float_color.new("Tint")
    vs = [bm.verts.new(Vector(p)) for p in pts]
    res = bmesh.ops.convex_hull(bm, input=vs)
    for g in res.get("geom_interior", []) + res.get("geom_unused", []):
        if isinstance(g, bmesh.types.BMVert) and g.is_valid:
            bm.verts.remove(g)
    if open_verts is not None:
        foot = {vs[i] for i in open_verts if vs[i].is_valid}
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.normal_update()
        for f in [f for f in bm.faces if all(v in foot for v in f.verts)
                  and (open_dir is None or f.normal.dot(open_dir) < -0.5)]:
            bm.faces.remove(f)
        for v in [v for v in bm.verts if not v.link_faces]:
            bm.verts.remove(v)
    # merge the slight folds the curved host leaves, so each crystal reads as a
    # few big planes (a 4-sided pyramid / diamond), not a cluster of slivers
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(7.0), verts=bm.verts[:], edges=bm.edges[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    for f in bm.faces:  # one flint colour; the lighting and low roughness give the gloss
        f.material_index = 0
        t = rng.uniform(0.97, 1.03)
        f.smooth = False
        for lp in f.loops:
            lp[tl] = (t, t, t, 1.0)
    return bm


def recolour(kit, kind, colours, **extra):
    """Copy of a VFX kind's emitters with the named emitters recoloured (the
    top-level `color` override never reaches the emitters)."""
    ems = json.loads(json.dumps(kit.vfx.KINDS[kind]["emitters"]))
    for em in ems:
        if em["name"] in colours:
            em["color"] = colours[em["name"]]
        em.update(extra)
    return ems


def surface_glint(bm, centre, push=0.12):
    """A point just outside the most key-facing side of a crystal bmesh: ray-cast
    from the key light toward `centre` and push it out along the hit normal."""
    tree = BVHTree.FromBMesh(bm)
    c = Vector(centre)
    loc, nrm, _, _ = tree.ray_cast(c + KEY * 10.0, -KEY)
    if loc is None:
        return tuple(c)
    if nrm.dot(KEY) < 0:
        nrm = -nrm
    return tuple(loc + nrm * push)


def ray_hit(tree, through, d):
    """Outermost-side hit of a ray aimed along d through point `through`."""
    d = Vector(d).normalized()
    loc, nrm, _, _ = tree.ray_cast(Vector(through) - d * 20.0, d)
    if loc is None:
        return None
    if nrm.dot(d) > 0:
        nrm = -nrm
    return loc, nrm


# ---------------------------------------------------------------------------
# pieces
# ---------------------------------------------------------------------------

# A tall angular boulder (front view): broad steep base, a straight steep left
# flank, a shouldered peak left of centre (x ~ -0.4), and on the right a stepped
# shoulder (wide at z~3.9, then a sharp step in). Side view: a bullet that
# tapers front and back to a narrow peak. Rings: (z, n, xl, xr, yf, yb, cx).
SHELL_RINGS = [  # main body: straight steep left flank, ridge peak at x ~-1.0
    (0.0, 13, 3.05, 2.3, 2.15, 2.05, 0.0),
    (1.2, 13, 3.15, 2.35, 2.25, 2.15, 0.0),
    (2.5, 13, 3.1, 2.3, 2.0, 2.0, 0.0),
    (3.5, 12, 2.95, 2.3, 1.65, 1.75, 0.0),
    (4.4, 10, 2.6, 2.05, 1.2, 1.3, 0.0),
    (5.05, 7, 1.1, 1.05, 0.7, 0.8, -0.85),
]
SHELL_PEAK = [(-1.55, -0.1, 5.5), (-0.55, 0.1, 5.5)]  # a short ridge left of centre
# right shoulder block: its top at z ~3.7 sticks out ~1 stud past the main
# body, so the union steps in at the right shoulder. It tapers in depth like the
# body so the side view stays one wedge.
SHOULDER_RINGS = [
    (0.0, 10, 1.5, 1.4, 2.1, 2.0, 1.75),
    (1.4, 10, 1.55, 1.45, 2.15, 2.05, 1.75),
    (2.7, 8, 1.5, 1.4, 1.75, 1.7, 1.75),
    (3.35, 5, 1.3, 1.2, 1.35, 1.3, 1.75),  # few points: an angular, not arched, shelf edge
]
# the shelf slopes down toward +X so the side view keeps one wedge
SHOULDER_PEAK = [(1.4, -0.45, 3.95), (1.9, 0.45, 3.9), (2.6, 0.0, 3.7)]
SHELL_SEED = 2111

# Front view coordinates (x, z) read off the reference front cell (24.5 px/stud),
# ~10% larger than measured: the reference crystals dominate the front face.
INSERTS = [
    # big front-left crystal: a triangular pyramid (top up-left of centre, corner
    # out left, broad base low right), apex low-left
    dict(d=(0.0, 1.0, 0.0), foot=[(-1.3, 3.2), (-2.6, 1.05), (-0.4, 0.35), (-0.7, 1.75)],
         ridge=[(-1.5, 1.7, 0.8)], seed=11, seat=0.5),
    # upper crystal: a bold long diamond (~2.9 x 1.4) from near the peak down to mid-right
    dict(d=(0.0, 1.0, 0.0), foot=[(-0.4, 5.15), (-0.75, 4.25), (0.7, 2.55), (1.8, 3.6)],
         ridge=[(-0.25, 4.55, 0.65), (0.75, 3.45, 0.75)], seed=12, seat=0.5),
    # right crystal: a full pyramid (~1.6 wide) on the front-right below the shoulder
    dict(d=(0.08, 1.0, 0.0), foot=[(2.6, 3.0), (1.0, 1.35), (2.5, 0.55), (2.95, 1.7)],
         ridge=[(2.15, 1.7, 0.75)], seed=13, seat=0.5),
    # back crystal: a big flat diamond on the back-right flank (world x, seen from behind)
    dict(d=(0.0, -1.0, 0.0), foot=[(0.6, 3.6), (2.55, 1.9), (2.1, 0.5), (0.2, 0.75)],
         ridge=[(1.3, 1.95, 0.7)], seed=14, seat=0.5),
]

BASE_ROCKS = [  # (size, centre, seed)
    ((1.7, 1.4, 0.95), (-2.6, -2.45), 2201),
    ((1.1, 0.95, 0.65), (2.4, -2.45), 2202),
    ((0.6, 0.55, 0.4), (3.3, -1.55), 2203),
]


def shell_bm(label=None):
    """The limestone shell with a flat seat chiselled for each flint crystal.
    Returns (bmesh, [(footprint pts, ridge pts, normal, seed)])."""
    body = hull_rock_bm(SHELL_RINGS, SHELL_PEAK, SHELL_SEED, jitter=0.09, zjit=0.15, egg=0.05,
                        keep_bottom=True)
    shoulder = hull_rock_bm(SHOULDER_RINGS, SHOULDER_PEAK, SHELL_SEED + 7, jitter=0.08, zjit=0.12,
                            egg=0.0, keep_bottom=True)
    bm = union_bm([body, shoulder], dissolve=5.0)
    seats = []
    for spec in INSERTS:
        pts, top, N = seat_crystal(bm, spec)
        seats.append((pts, top, N, spec["seed"]))
    for v in bm.verts:
        v.co.z = max(v.co.z, 0.0)
    drop_bottom(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if label:
        shell_stat(bm, label)
    return bm, seats


def base_rock_bm(size, centre, seed, keep_bottom=False):
    return hewn_bm(size, centre, n=22, p=2.2, taper=0.35, sink=0.25, seed=seed, jitter=0.08, tilt=0.15,
                   keep_bottom=keep_bottom)


# ---------------------------------------------------------------------------
# assets
# ---------------------------------------------------------------------------


def hero(kit, fk):
    a = fk.Asset("FlintNode", "Kit", seed=21)
    sbm, seats = shell_bm("shell")
    tree = BVHTree.FromBMesh(sbm)
    add_stone(a, sbm, LIME, seed=21)
    glints = []
    for pts, top, N, seed in seats:
        cbm = crystal_bm(pts + top, seed, open_verts=range(len(pts)), open_dir=N)
        append_bm(a, cbm, FLINT)
        cbm.free()
        glints.append((sum(top, Vector((0, 0, 0))) / len(top) + N * 0.15, N))
    for size, c, seed in BASE_ROCKS:
        add_stone(a, base_rock_bm(size, c, seed), GREY, seed)
    front = ray_hit(tree, (0.4, 0.0, 2.4), (0.0, 1.0, 0.0))[0]
    hit = recolour(kit, "harvest_hit", {"Chips": HIT_COLORS, "Dust": DUST_COLORS})
    dep = recolour(kit, "harvest_deplete", {"Chips": DEPLETE_COLORS, "Dust": DUST_COLORS})
    sockets = [("harvest_hit", (front.x, front.y - 0.25, front.z), 1.0,
                {"color": HIT_COLORS, "emitters": hit}),
               ("harvest_deplete", (0, 0, 0.3), 1.0, {"color": DEPLETE_COLORS, "emitters": dep})]
    for g, _ in glints[:2]:
        sockets.append(("ore_glint", tuple(g), 0.5, glint_over(kit)))
    notes = ("harvest_hit: front strike face at mid height, tan limestone + dark flint chips; "
             "harvest_deplete: base centre, burst when the node empties; "
             "ore_glint x2: low-rate cool-white twinkles just off the front-left and upper flint crystals")
    return finish(kit, a, "hero", "hull", notes, sockets)


def shell_part(kit, fk):
    a = fk.Asset("FlintNodeLimestoneShell", "Kit", seed=22)
    add_stone(a, shell_bm()[0], LIME, seed=21)
    return finish(kit, a, "part", "hull", "bare limestone shell; flint inserts sit on its facets")


# Standalone crystals for kit-bashing (local coords, base on z=0, closed bottom).
# Each is a list of convex hulls (point clouds) unioned into one mesh.
INSERT_PARTS = {
    # tall chunky shard (~2.0 x 1.1 x 3.4): broad faceted body, main peak leaning
    # left, a lower second peak to the right
    "FlintInsert": [  # unioned: main blade + a lower second blade on the right
        [(-1.0, -0.3, 0.0), (-0.2, -0.55, 0.0), (0.5, -0.2, 0.0), (0.35, 0.45, 0.0), (-0.45, 0.55, 0.0),
         (-1.0, 0.22, 0.0),                                                      # broad foot
         (-0.75, -0.28, 1.1), (-0.15, -0.47, 1.15), (0.3, -0.14, 1.1), (0.2, 0.38, 1.05), (-0.4, 0.46, 1.1),
         (-0.78, 0.16, 1.1),                                                     # tapering body
         (-0.6, -0.22, 2.3), (-0.1, -0.36, 2.35), (0.1, 0.0, 2.3), (-0.1, 0.32, 2.25), (-0.55, 0.24, 2.3),
         (-0.36, -0.08, 3.4), (-0.2, 0.08, 3.32)],                               # tip near the centre
        [(0.2, -0.5, 0.0), (1.0, -0.25, 0.0), (1.0, 0.25, 0.0), (0.25, 0.45, 0.0),
         (0.25, -0.44, 0.9), (0.95, -0.2, 0.85), (0.95, 0.2, 0.85), (0.3, 0.4, 0.9),
         (0.45, -0.32, 1.65), (0.92, 0.0, 1.6), (0.45, 0.3, 1.65),
         (0.75, 0.0, 2.2)],
    ],
    # short broad diamond (~1.4 x 0.85 x 2.1): narrow foot, wide shoulders, short point
    "FlintInsertSmall": [[(-0.25, -0.12, 0.0), (0.25, -0.1, 0.0), (0.05, 0.22, 0.0), (-0.15, 0.2, 0.0),
                          (-0.7, -0.15, 1.15), (0.1, -0.42, 1.3), (0.7, 0.05, 1.4), (-0.05, 0.42, 1.15),
                          (-0.15, -0.05, 2.0), (0.2, 0.05, 2.1)]],
    # slim needle (~0.8 x 0.6 x 2.5): three-sided blade, thick at the foot, sharp tip
    # slim 3-sided blade (~0.8 x 0.6 x 2.5): full width at the foot, a chunky
    # body to ~1.9, then a short chisel tip ~0.25 wide (not a needle)
    "FlintInsertThin": [[(-0.4, -0.25, 0.0), (0.4, -0.2, 0.0), (0.0, 0.35, 0.0),
                         (-0.36, -0.22, 1.0), (0.37, -0.18, 1.05), (0.0, 0.3, 1.0),
                         (-0.25, -0.14, 1.9), (0.26, -0.12, 1.95), (0.0, 0.2, 1.9),
                         (-0.12, -0.02, 2.5), (0.13, 0.0, 2.46)]],
}


def hull_glint(hulls, seed, frac=0.55):
    """Glint point on the key-facing side of the tallest hull."""
    pts = max(hulls, key=lambda h: max(p[2] for p in h))
    h = max(p[2] for p in pts)
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    bm = crystal_bm(pts, seed)
    g = surface_glint(bm, (cx, cy, h * frac))
    bm.free()
    return g


def insert_part(kit, fk, name, seed):
    a = fk.Asset(name, "Kit", seed=seed)
    hulls = INSERT_PARTS[name]
    bms = [crystal_bm(pts, seed + i) for i, pts in enumerate(hulls)]
    bm = union_bm(bms, dissolve=3.0) if len(bms) > 1 else bms[0]
    tone_stone(bm, seed)
    append_bm(a, bm, FLINT)
    bm.free()
    sockets = []
    if name == "FlintInsert":  # only the big insert twinkles; the small ones stay quiet
        sockets = [("ore_glint", hull_glint(hulls, seed), 0.35, glint_over(kit, 0.4))]
    return finish(kit, a, "part", "none",
                  "flint crystal scatter (no collision); sink the base ~0.3 studs into a host rock"
                  + ("; ore_glint: low-rate cool-white twinkle on its lit face" if sockets else ""),
                  sockets=sockets)


def base_rock_part(kit, fk, name, size, seed):
    a = fk.Asset(name, "Kit", seed=seed)
    add_stone(a, base_rock_bm(size, (0, 0), seed, keep_bottom=True), GREY, seed + 5)
    return finish(kit, a, "part", "hull" if size[0] > 1 else "none", "warm grey base rock scatter")


FLAKES = {
    # chunky rhombic flake ~1.3 x 0.9 x 0.8 lying on a broad face, pointed ends,
    # a faceted ridge along the top
    # a thick rhombic plate (pointed ends at mid-thickness, a chamfered girdle,
    # a two-plane top ridge), tilted ~16 deg so one end is propped up; see flake_pts
    "FlintFlake": dict(
        pts=[(-0.72, 0.0, 0.25), (0.72, 0.0, 0.25),                                  # pointed ends
             (-0.12, -0.46, 0.25), (0.14, 0.46, 0.25),                               # girdle corners
             (-0.52, -0.02, 0.0), (0.52, 0.02, 0.0), (-0.08, -0.32, 0.0), (0.1, 0.32, 0.0),  # base rhomb
             (-0.48, 0.0, 0.55), (0.48, 0.0, 0.55), (-0.1, -0.28, 0.55), (0.12, 0.28, 0.55),  # top rhomb
             (-0.22, 0.0, 0.68), (0.24, 0.02, 0.68)],                                # ridge
        tilt=15.0, cut=0.06),
    # second flake: a fat blunt end (left) tapering to a long point (right)
    "FlintFlakeAlt": dict(
        pts=[(-0.62, -0.3, 0.02), (-0.62, 0.28, 0.0), (-0.66, -0.04, 0.48),        # blunt end
             (-0.3, -0.42, 0.0), (-0.28, 0.4, 0.0), (-0.32, -0.42, 0.42), (-0.3, 0.42, 0.38),  # fat body
             (-0.36, -0.15, 0.78), (-0.3, 0.18, 0.74),                               # fat top
             (0.15, -0.28, 0.0), (0.15, 0.24, 0.0), (0.12, -0.26, 0.4), (0.14, 0.24, 0.36),
             (0.08, -0.02, 0.6),                                                     # taper ridge
             (0.7, 0.0, 0.12)],                                                      # long point
        tilt=-6.0, cut=0.0),
}


def flake_pts(spec):
    """Rotate the flake points about Y by `tilt` degrees and set them on z=0
    (lowered `cut` studs; the hull is then cut flat at z=0)."""
    t = math.radians(spec["tilt"])
    out = []
    for x, y, z in spec["pts"]:
        out.append((x * math.cos(t) - z * math.sin(t), y, x * math.sin(t) + z * math.cos(t)))
    zmin = min(p[2] for p in out) + spec["cut"]
    return [(x, y, z - zmin) for x, y, z in out]


def flake(kit, fk, name, seed):
    a = fk.Asset(name, "Kit", seed=seed)
    pts = flake_pts(FLAKES[name])
    bm = crystal_bm(pts, seed)  # closed: drops can tumble
    if FLAKES[name]["cut"] > 0:  # flatten the propped-up flake's foot at z=0 (closed cap)
        plane_cut(bm, Vector((0, 0, -1)), Vector((0, 0, 0)))
        tone_stone(bm, seed)
    append_bm(a, bm, FLINT)
    bm.free()
    g = hull_glint([pts], seed, frac=0.6)
    return finish(kit, a, "drop", "box",
                  "flint flake drop (inventory item); ore_glint: low-rate cool-white twinkle on its lit face",
                  sockets=[("ore_glint", g, 0.25, glint_over(kit, 0.4))])


def depleted(kit, fk):
    """A long, low, flat-topped limestone lozenge with a stepped faceted top."""
    a = fk.Asset("FlintNodeDepleted", "Kit", seed=31)
    slab = hewn_bm((5.7, 4.5, 2.1), (0.05, 0.05), n=90, p=2.6, taper=0.35, sink=0.2, seed=3101,
                   jitter=0.06, tilt=0.14,
                   extra=[((0.0, 0.0, 1.0), (0.0, 0.0, 1.45)),            # flat cap
                          ((0.22, 0.05, 1.0), (1.2, 0.0, 1.38)),          # stepped top planes
                          ((-0.25, -0.08, 1.0), (-1.6, 0.0, 1.3)),
                          ((0.0, -0.45, 1.0), (0.0, -0.9, 1.4)),
                          ((0.12, 0.4, 1.0), (0.6, 1.0, 1.32)),           # extra top steps
                          ((-0.3, 0.3, 1.0), (-1.9, 0.8, 1.15))])
    add_stone(a, slab, LIME, seed=31)
    for size, c, seed in (((0.95, 0.85, 0.6), (-2.75, -0.6), 3201),
                          ((0.6, 0.55, 0.42), (-2.3, -1.4), 3204),
                          ((0.85, 0.75, 0.55), (2.85, -0.65), 3202)):
        add_stone(a, base_rock_bm(size, c, seed), GREY, seed)
    return finish(kit, a, "depleted", "hull", "mined-out base, same footprint as FlintNode",
                  sockets=[])


def build(kit):
    fk = kit.flintkit
    objs = [hero(kit, fk), shell_part(kit, fk),
            insert_part(kit, fk, "FlintInsert", 41),
            insert_part(kit, fk, "FlintInsertSmall", 42),
            insert_part(kit, fk, "FlintInsertThin", 43),
            base_rock_part(kit, fk, "FlintNodeBaseRock", (1.6, 1.4, 1.1), 51),
            base_rock_part(kit, fk, "FlintNodeBaseRockSmall", (0.8, 0.7, 0.5), 52),
            flake(kit, fk, "FlintFlake", 61), flake(kit, fk, "FlintFlakeAlt", 62),
            depleted(kit, fk)]
    return objs
