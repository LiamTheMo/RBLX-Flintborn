"""Build sheet 06: Rocks, Runes & Camp.

LowBoulder, TallBoulder, SplitBoulder, LongBoulder, LargeRuneStone,
ElongatedRuneStone, TriangularRuneStone, SteppingStone, CutLog, FallenLog,
Stump, ChoppingStump, Campfire, LogBench, TorchPost, StoneBrazier.

Rocks are hewn: a superellipsoid volume cut by one tangent plane per facet gives
many medium chisel facets, each edge chamfered into a pale ridge; tall or lumpy
rocks are a few overlapping chunks. Rune glyphs are carved as real channels (EXACT
boolean) and filled with a pale inlay. Logs carry long, crowned bark strips with
pale chamfered edges over a dark core.

Run headless:
    blender --background --factory-startup --python build_06_rocks_runes_camp.py
"""

import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import flintkit as fk  # noqa: E402
import vfx  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PI = math.pi

# ---------------------------------------------------------------------------
# Generic helpers (all take an fk.Asset)
# ---------------------------------------------------------------------------


def paint(a, faces, mat, tint=1.0, var=0.05):
    mi = a._mi(mat)
    for f in faces:
        f.material_index = mi
        f.smooth = False
        t = tint * (1.0 + a.rng.uniform(-var, var))
        for loop in f.loops:
            loop[a.tint_layer] = (t, t, t, 1.0)


def recolor(a, verts, fn, var=0.04):
    """fn(face) -> palette key or None; repaints matching faces."""
    a.bm.normal_update()
    for f in fk._faces_of(verts):
        m = fn(f)
        if m:
            paint(a, [f], m, var=var)


def xform(a, verts, M):
    bmesh.ops.transform(a.bm, matrix=M, verts=list(verts))
    return verts


def fit(a, dims):
    """Scale the whole asset about its bottom centre to exact (x, y, z) studs."""
    vs = a.bm.verts
    mn = [min(v.co[i] for v in vs) for i in range(3)]
    mx = [max(v.co[i] for v in vs) for i in range(3)]
    c = ((mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2])
    s = [dims[i] / (mx[i] - mn[i]) for i in range(3)]
    for v in vs:
        v.co = Vector(tuple(c[i] + (v.co[i] - c[i]) * s[i] for i in range(3)))
    return s, c


def done(a, dims, sockets=()):
    """Fit, finish, then attach VFX sockets. sockets: [(kind, pre-fit point)] in build
    coordinates; they follow the same fit and bottom-centre re-origin as the mesh."""
    s, c = fit(a, dims)
    bmesh.ops.recalc_face_normals(a.bm, faces=list(a.bm.faces))
    obj = a.finish()
    for kind, p in sockets:
        local = tuple((p[i] - c[i]) * s[i] for i in range(3))
        vfx.add(obj, kind, local)
        print(f"SOCKET {a.name}: {kind} at ({local[0]:.2f}, {local[1]:.2f}, {local[2]:.2f})")
    print(f"ASSET {a.name}: tris={obj['tris']} studs={obj['studs']} fit=({s[0]:.2f},{s[1]:.2f},{s[2]:.2f})")
    return obj


def append_bm(a, src, mats=None, classify=None, default="stone"):
    """Copy src faces into the asset. classify(face) -> (mat, tint) or None; else the
    source material index (into `mats`) and its Tint are kept."""
    tl = src.loops.layers.float_color.get("Tint")
    src.normal_update()
    vmap = {v: a.bm.verts.new(v.co) for v in src.verts}
    for f in src.faces:
        try:
            nf = a.bm.faces.new([vmap[v] for v in f.verts])
        except ValueError:
            continue
        res = classify(f) if classify else None
        if res is None:
            m = mats[f.material_index] if mats and f.material_index < len(mats) else default
            t = f.loops[0][tl][0] if tl else 1.0
            paint(a, [nf], m, t if t > 0.05 else 1.0, 0.0)
        else:
            paint(a, [nf], res[0], res[1], 0.04)
    return list(vmap.values())


def boolean_diff(bm_a, bm_cut, mats=None):
    """EXACT boolean difference of two bmeshes; returns a new bmesh."""
    me_a = bpy.data.meshes.new("_tmpA")
    bm_a.to_mesh(me_a)
    me_b = bpy.data.meshes.new("_tmpB")
    bm_cut.to_mesh(me_b)
    for m in mats or []:
        me_a.materials.append(fk.material(m))
    oa = bpy.data.objects.new("_tmpA", me_a)
    ob = bpy.data.objects.new("_tmpB", me_b)
    sc = bpy.context.scene.collection
    sc.objects.link(oa)
    sc.objects.link(ob)
    mod = oa.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = ob
    mod.solver = "EXACT"
    for attr, val in (("use_self", True), ("material_mode", "INDEX")):
        try:
            setattr(mod, attr, val)
        except (AttributeError, TypeError):
            pass
    dg = bpy.context.evaluated_depsgraph_get()
    ev = oa.evaluated_get(dg)
    me = ev.to_mesh()
    out = bmesh.new()
    out.from_mesh(me)
    ev.to_mesh_clear()
    bpy.data.objects.remove(oa, do_unlink=True)
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.meshes.remove(me_a)
    bpy.data.meshes.remove(me_b)
    return out


# ---------------------------------------------------------------------------
# Chiselled stone
# ---------------------------------------------------------------------------

# Hewn rocks: a superellipsoid volume carved by one tangent plane per facet, so the
# surface breaks into many medium polygonal chisel facets; every facet edge is then
# chamfered into a pale bevelled ridge.

ROCK_MATS = ["stone", "stone_light", "stone_dark"]


def plane_cut(bm, n, co):
    """Keep the side of the plane opposite its normal and cap the hole."""
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=n, clear_outer=True)
    bnd = [e for e in bm.edges if e.is_boundary]
    if bnd:
        bmesh.ops.contextual_create(bm, geom=bnd)


def hewn_bm(size, center=(0.0, 0.0), n=40, p=2.4, taper=0.0, jitter=0.05, tilt=0.12, seed=0,
            sink=0.1, extra=(), lean=(0.0, 0.0), min_nz=-0.5, lobes=()):
    """Chiselled chunk with full extents `size`, base at z=0. One tangent plane per
    Fibonacci direction (skipping downward ones), pushed in by up to `jitter` of the
    radius and tilted by up to `tilt` rad. extra: [(normal, point)] cuts made first."""
    rng = random.Random(seed)
    sx, sy, sz = size
    rx, ry = sx / 2, sy / 2
    rz = sz / (2 - sink)
    zc = rz * (1 - sink)
    C = Vector((center[0], center[1], zc))

    def F(P):
        tf = max(0.2, 1 - taper * max(0.0, P.z) / sz)
        x = (P.x - C.x - lean[0] * P.z) / (rx * tf)
        y = (P.y - C.y - lean[1] * P.z) / (ry * tf)
        z = (P.z - zc) / rz
        if lobes:  # outline radius modulated by (k, amp, phase) harmonics
            th = math.atan2(y, x)
            w = 1 + sum(amp * math.cos(k * th - ph) for k, amp, ph in lobes)
            x, y = x / w, y / w
        return (abs(x) ** p + abs(y) ** p + abs(z) ** p) ** (1 / p)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    m = 1.3
    for v in bm.verts:
        v.co = Vector((C.x + v.co.x * sx * m + lean[0] * sz * (v.co.z + 0.5),
                       C.y + v.co.y * sy * m + lean[1] * sz * (v.co.z + 0.5),
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
    bmesh.ops.dissolve_degenerate(bm, dist=0.04 * min(size), edges=bm.edges[:])
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.5), verts=bm.verts[:], edges=bm.edges[:])
    for v in bm.verts:
        v.co.z = max(v.co.z, 0.0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def finish_rock(bm, seed=0, bevel=0.019, dark=0.3, light=0.22, post=None, ridge_tint=0.96,
                override=None):
    """Per-facet tones and chamfered pale ridges. Faces get material indices into
    ROCK_MATS and a Tint layer (ready for append_bm / boolean_diff)."""
    rng = random.Random(seed)
    if post:
        post(bm)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.dissolve_degenerate(bm, dist=0.1, edges=bm.edges[:])
    tl = bm.loops.layers.float_color.get("Tint") or bm.loops.layers.float_color.new("Tint")
    bm.normal_update()
    zmin = min(v.co.z for v in bm.verts)

    def put(f, mi, t):
        f.material_index = mi
        f.smooth = False
        for lp in f.loops:
            lp[tl] = (t, t, t, 1.0)

    for f in bm.faces:
        nz = f.normal.z
        u = rng.random()
        if nz < -0.5:
            put(f, 2, 0.85)
        elif nz > 0.7:
            put(f, 1 if u < light else 0, rng.uniform(0.92, 1.1) * (0.88 if u < light else 1.0))
        elif u < dark * (1.2 - nz):
            put(f, 2, rng.uniform(0.98, 1.15))
        else:
            put(f, 0, rng.uniform(0.78, 1.1))
        if override:
            o = override(f)
            if o:
                put(f, *o)
    edges = [e for e in bm.edges if not all(v.co.z < zmin + 0.02 for v in e.verts)]
    if bevel and edges:
        res = bmesh.ops.bevel(bm, geom=edges, offset=bevel, offset_type="OFFSET", segments=1,
                              profile=0.5, affect="EDGES", clamp_overlap=False)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.normal_update()
        key = Vector((-0.49, -0.59, 0.64))  # toward the studio key light
        for f in res["faces"]:
            if f.normal.dot(key) > 0.5 or f.normal.z > 0.35:
                put(f, 0, rng.uniform(1.06, 1.08))
            else:
                put(f, 0, rng.uniform(1.0, 1.04))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def add_chunk(a, bm, M=None, **kw):
    finish_rock(bm, **kw)
    verts = append_bm(a, bm, mats=ROCK_MATS)
    bm.free()
    if M is not None:
        xform(a, verts, M)
    return verts


# ---------------------------------------------------------------------------
# Carved runes
# ---------------------------------------------------------------------------


def seg_dist(px, py, pts):
    best = 1e9
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        dx, dy = x2 - x1, y2 - y1
        L2 = dx * dx + dy * dy or 1e-9
        t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
        best = min(best, math.hypot(px - x1 - t * dx, py - y1 - t * dy))
    return best


def strips_bm(bm, pts, width, z0, z1):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        length = math.hypot(x2 - x1, y2 - y1) + width
        ang = math.atan2(y2 - y1, x2 - x1)
        vs = bmesh.ops.create_cube(bm, size=1.0)["verts"]
        bmesh.ops.scale(bm, vec=(length, width, z1 - z0), verts=vs)
        bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0), matrix=Matrix.Rotation(ang, 3, "Z"))
        bmesh.ops.translate(bm, vec=((x1 + x2) / 2, (y1 + y2) / 2, (z0 + z1) / 2), verts=vs)


def surface_matrix(point, normal, yaw=0.0):
    """Frame on a surface: local Z = normal, local X as close to world X as possible
    (so glyphs keep their reading orientation), local Y up the slope."""
    n = Vector(normal).normalized()
    x = Vector((0, 1, 0)).cross(n)
    if x.length < 1e-4:
        x = Vector((1, 0, 0))
    x.normalize()
    y = n.cross(x).normalized()
    R = Matrix((x, y, n)).transposed().to_4x4()
    return Matrix.Translation(Vector(point)) @ R @ Matrix.Rotation(yaw, 4, "Z")


def diamond(rx, ry, cx=0.0, cy=0.0):
    return [(cx, cy - ry), (cx + rx, cy), (cx, cy + ry), (cx - rx, cy), (cx, cy - ry)]


# ---------------------------------------------------------------------------
# Wood helpers
# ---------------------------------------------------------------------------


def tube(a, pts, radii, sides=10, mat="bark", jitter=0.05, flute=0.07, phase=0.0, var=0.08,
         grooves=False, groove_mat="wood_dark"):
    """Faceted tube along a polyline: returns (rings, frames). Open ends."""
    bm = a.bm
    pts = [Vector(p) for p in pts]
    n = len(pts)
    if grooves:
        step = 2 * PI / sides
        pattern = []
        for p in range(sides):
            base = step * p + phase
            pattern += [(base, 1.0, 0), (base + 0.74 * step, 1.0, 1), (base + 0.87 * step, 0.87, 1)]
    else:
        pattern = [(2 * PI * j / sides + phase, 1 - flute * (j % 2), 0) for j in range(sides)]
    m = len(pattern)
    rings, frames = [], []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        up = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        nrm = t.cross(up).normalized()
        bi = nrm.cross(t).normalized()
        ring = []
        pj = 1.0
        for j, (b, rm, kind) in enumerate(pattern):
            if not grooves or j % 3 == 0:
                pj = 1 + a.rng.uniform(-jitter, jitter)
            r = radii[i] * rm * pj
            ring.append(bm.verts.new(p + r * (math.cos(b) * nrm + math.sin(b) * bi)))
        rings.append(ring)
        frames.append((p, t, nrm, bi))
    plates, gfaces = [], []
    for i in range(n - 1):
        for j in range(m):
            k = (j + 1) % m
            f = bm.faces.new((rings[i][j], rings[i + 1][j], rings[i + 1][k], rings[i][k]))
            (gfaces if pattern[j][2] else plates).append(f)
    paint(a, plates, mat, 1.0, var)
    if gfaces:
        paint(a, gfaces, groove_mat, 0.9, 0.05)
    return rings, frames


def ring_lines(a, center, normal, radius, fracs=(0.62, 0.3), width=0.06, mat="wood", dot=True, n=8):
    """Concentric polygonal growth rings (strips) on a cut face."""
    rot = Vector(normal).to_track_quat("Z", "Y").to_euler()
    out = []
    for f in fracs:
        r = radius * f
        ph = a.rng.uniform(0, PI)
        pts = []
        for j in range(n):
            b = 2 * PI * j / n + ph
            rr = r * (1 + a.rng.uniform(-0.07, 0.07))
            pts.append((rr * math.cos(b), rr * math.sin(b)))
        pts.append(pts[0])
        out += a.strip(pts, width, 0.03, loc=center, rot=rot, mat=mat)
    if dot:
        d = radius * 0.08
        out += a.strip([(-d, 0), (d, 0)], d * 1.6, 0.03, loc=center, rot=rot, mat=mat)
    return out


def cut_end(a, ring, center, out, inset=0.86, recess=0.05, rim="wood_dark", end="wood_end",
            rings=True, fracs=(0.62, 0.3)):
    """Close a tube end with a rim, a recessed pale cut face and rings."""
    bm = a.bm
    out = Vector(out).normalized()
    c = Vector(center)
    inner = [bm.verts.new(c + (v.co - c) * inset - out * recess) for v in ring]
    n = len(ring)
    rim_faces = [bm.faces.new((ring[j], ring[(j + 1) % n], inner[(j + 1) % n], inner[j])) for j in range(n)]
    paint(a, rim_faces, rim, 1.0, 0.05)
    cap = bm.faces.new(inner)
    paint(a, [cap], end, 1.0, 0.0)
    rad = sum((v.co - c).length for v in ring) / n * inset
    if rings:
        ring_lines(a, c - out * (recess - 0.005), out, rad, fracs=fracs, width=max(0.04, rad * 0.06))
    return inner


def cap_flat(a, ring, mat="bark", tint=0.8):
    f = a.bm.faces.new(list(reversed(ring)))
    paint(a, [f], mat, tint, 0.0)


def bark_strip(a, a0, a1, z0, z1, ri, ro, rng, slope0=0.0, slope1=0.0, mat="bark", tint=1.0):
    """One long bark strip over [a0, a1] around the log axis: a crowned, hand-hewn
    top split into short facets along its length, chamfered long edges (pale
    highlights) and dark sides. z0/z1 ends can be skewed by slope (studs across the
    strip) for diagonal breaks."""
    bm = a.bm
    w = a1 - a0
    e = min(0.22 * w, 0.05 / max(ro, 0.1))
    c = (ro - ri) * 0.4
    am = a0 + w * rng.uniform(0.35, 0.65)
    if rng.random() < 0.45 and w > 0.3:  # a dark split running along the strip
        dd = min(0.03 / max(ro, 0.1), w * 0.08)
        prof = [(a0, ri, "side"), (a0, ro - c, "chamfer"), (a0 + e, ro, "top"), (am - dd, ro, "crack"),
                (am, ro - c * 0.8, "crack"), (am + dd, ro, "top"), (a1 - e, ro, "chamfer"),
                (a1, ro - c, "side"), (a1, ri, "inner")]
    else:
        prof = [(a0, ri, "side"), (a0, ro - c, "chamfer"), (a0 + e, ro, "top"), (am, ro * 1.035, "top"),
                (a1 - e, ro, "chamfer"), (a1, ro - c, "side"), (a1, ri, "inner")]
    L = z1 - z0
    nsec = max(1, min(4, int(L / 1.4 + 0.5)))
    zs = [0.0] + sorted((k + rng.uniform(-0.25, 0.25)) / nsec
                        for k in range(1, nsec)) + [1.0]
    rings = []
    for li, zf in enumerate(zs):
        ring = []
        sl = slope0 if li == 0 else slope1 if li == len(zs) - 1 else 0.0
        for k, (ang, rr, _) in enumerate(prof):
            if rr > ri:
                rr = rr * (1 + rng.uniform(-0.03, 0.03))
            zz = z0 + zf * L + sl * ((ang - a0) / w - 0.5)
            if 0 < li < len(zs) - 1:
                zz += rng.uniform(-0.3, 0.3)
            ring.append(bm.verts.new((rr * math.cos(ang), rr * math.sin(ang), zz)))
        rings.append(ring)
    n = len(prof)
    for li in range(len(rings) - 1):
        for k in range(n):
            j = (k + 1) % n
            f = bm.faces.new((rings[li][k], rings[li][j], rings[li + 1][j], rings[li + 1][k]))
            kd = prof[k][2]
            if kd == "top":
                u = rng.random()
                if u < 0.14:
                    paint(a, [f], "wood_light", tint * 0.92, 0.03)
                elif u < 0.4:
                    paint(a, [f], "bark", tint, 0.03)
                else:
                    paint(a, [f], mat, tint * rng.uniform(0.92, 1.12), 0.0)
            elif kd == "crack":
                paint(a, [f], "wood_dark", 0.8, 0.04)
            elif kd == "chamfer":
                paint(a, [f], "wood_light" if rng.random() < 0.6 else mat, tint * 1.05, 0.03)
            else:
                paint(a, [f], "wood_dark", 1.0, 0.04)
    for ring in (rings[0], rings[-1]):
        f = bm.faces.new(ring)
        paint(a, [f], "wood_dark", 0.95, 0.04)
    return [v for r in rings for v in r]


def bark_log(a, L, r, plates=12, segs=2, thick=None, seed=0, start="rings", end="rings",
             fracs=(0.82, 0.62, 0.42, 0.22)):
    """Log along local +Z (0..L): a faceted ring of long bark strips (each the full
    length or broken once or twice on a diagonal) over a dark core, with recessed
    pale end faces. start/end: 'rings' | 'plain' | 'broken'. Returns verts."""
    rng = random.Random(seed)
    thick = thick or r * 0.16
    rc = r - thick * 0.55
    recess = 0.07
    out = []
    core = a.cyl(rc, rc, L - 2 * recess, plates, loc=(0, 0, recess), mat="wood_dark")

    def cap_mat(f):
        if abs(f.normal.z) < 0.9:
            return None
        which = start if f.normal.z < 0 else end
        return "wood_light" if which == "broken" else "wood_end"

    recolor(a, core, cap_mat)
    out += core
    for which, z, nrm in ((start, recess - 0.005, (0, 0, -1)), (end, L - recess + 0.005, (0, 0, 1))):
        if which == "rings":
            out += ring_lines(a, (0, 0, z), nrm, rc, fracs=fracs, width=max(0.05, rc * 0.055))
    step = 2 * PI / plates
    ga = step * 0.08
    widths = [rng.uniform(0.75, 1.3) for _ in range(plates)]
    tot = sum(widths)
    edges = [0.0]
    for w in widths:
        edges.append(edges[-1] + 2 * PI * w / tot)
    ph = rng.uniform(0, step)
    for p in range(plates):
        a0, a1 = edges[p] + ga / 2 + ph, edges[p + 1] - ga / 2 + ph
        ns = rng.choice([1, 1, 1, 2, 2, 3][:max(1, min(6, segs + 3))])
        bounds = [0.0] + sorted(L * (k + rng.uniform(-0.3, 0.3)) / ns for k in range(1, ns)) + [L]
        slopes = [0.0] + [rng.choice((-1, 1)) * rng.uniform(0.5, 1.1) * r for _ in range(ns - 1)] + [0.0]
        ro = r * (1 + rng.uniform(-0.04, 0.04))
        t = rng.uniform(0.95, 1.12)
        for s in range(ns):
            z0 = bounds[s] + (0.05 if s > 0 else 0.0)
            z1 = bounds[s + 1] - (0.05 if s < ns - 1 else 0.0)
            out += bark_strip(a, a0, a1, z0, z1, r - thick, ro * rng.uniform(0.98, 1.02), rng,
                              slopes[s], slopes[s + 1], mat="wood", tint=t * rng.uniform(0.97, 1.03))
    return out


def axis_matrix(p0, direction):
    d = Vector(direction).normalized()
    return Matrix.Translation(Vector(p0)) @ d.to_track_quat("Z", "Y").to_matrix().to_4x4()


def rooted_trunk(a, r, h, n_roots=7, base_mul=1.4, zm=0.5, plates=10, seed=0):
    """Trunk with bark plates whose base swells smoothly into n_roots buttresses
    (root tips reach base_mul * r). Returns the top ring (at z=h)."""
    rng = random.Random(seed)
    bm = a.bm
    step = 2 * PI / plates
    pattern = []
    for p in range(plates):
        b = step * p
        cr = rng.uniform(0.25, 0.5)
        pattern += [(b, 1.0, 0), (b + cr * step, 1.05, 0), (b + 0.76 * step, 1.0, 1),
                    (b + 0.88 * step, 0.88, 1)]
    levels = sorted({0.0, 0.06, 0.14, 0.24, 0.36, 0.5, 0.62, zm, 0.86, 1.0})
    phi = rng.uniform(0, 2 * PI)
    rings = []
    for zf in levels:
        f = max(0.0, (zm - zf) / zm) ** 1.25
        ring = []
        for b, gm, kind in pattern:
            peak = max(0.0, math.cos(n_roots * (b - phi))) ** 1.3
            lobe = 1 + f * (0.16 + (base_mul - 1.16) * peak)
            rr = r * lobe * gm * (1 + rng.uniform(-0.03, 0.03))
            ring.append(bm.verts.new((rr * math.cos(b), rr * math.sin(b), zf * h)))
        rings.append(ring)
    m = len(pattern)
    plates_f, grooves = [], []
    for i in range(len(levels) - 1):
        for j in range(m):
            k = (j + 1) % m
            fc = bm.faces.new((rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]))
            (grooves if pattern[j][2] else plates_f).append((j, fc))
    # streaky hand-painted plates: each vertical facet column keeps one tone, with
    # the odd pale chip
    cols = {}
    for j, fc in plates_f:
        if j not in cols:
            u = rng.random()
            cols[j] = (("bark", rng.uniform(0.8, 0.92)) if u < 0.25 else
                       ("wood_dark", rng.uniform(1.1, 1.3)) if u < 0.55 else
                       ("wood", rng.uniform(0.85, 1.05)))
        if rng.random() < 0.06:
            paint(a, [fc], "wood_light", 0.9, 0.0)
        else:
            m, t = cols[j]
            paint(a, [fc], m, t * rng.uniform(0.95, 1.05), 0.0)
    grooves = [fc for _, fc in grooves]
    paint(a, grooves, "wood_dark", 0.9, 0.05)
    cap_flat(a, rings[0])
    return rings[-1]


def trunk_top(a, top, h, fracs, rings=True, lip=0.94):
    lipv = [a.bm.verts.new((v.co.x * lip, v.co.y * lip, h + 0.06)) for v in top]
    n = len(top)
    lf = [a.bm.faces.new((top[j], top[(j + 1) % n], lipv[(j + 1) % n], lipv[j])) for j in range(n)]
    paint(a, lf, "wood_dark", 1.0, 0.06)
    cut_end(a, lipv, (0, 0, h + 0.06), (0, 0, 1), inset=0.93, recess=0.02, rim="wood_light",
            rings=rings, fracs=fracs)


# ---------------------------------------------------------------------------
# Fire
# ---------------------------------------------------------------------------


def tongue(a, base, h, r, out_dir, curl, mat, sides=5, side_curl=0.0):
    """One volumetric flame tongue: bulging tapered tube whose tip curls outward."""
    base = Vector(base)
    od = Vector((out_dir[0], out_dir[1], 0.0))
    if od.length > 1e-6:
        od.normalize()
    perp = Vector((-od.y, od.x, 0.0))
    prof = [(0.0, 0.7), (0.16, 1.0), (0.36, 0.9), (0.56, 0.65), (0.74, 0.38), (0.88, 0.16), (1.0, 0.02)]
    pts = [base + od * (curl * t * t) + perp * (side_curl * t ** 3) + Vector((0, 0, h * t)) for t, _ in prof]
    rings, _ = tube(a, pts, [r * m for _, m in prof], sides=sides, flute=0.0, jitter=0.0, mat=mat, var=0.0)
    cap_flat(a, rings[0], mat, 1.0)
    cap_flat(a, rings[-1], mat, 1.0)


def flame(a, loc, h, r, n=7, seed=1, toward=(-0.35, -0.94)):
    """Layered fire: an outer shell of curling tongues, a mid layer and a pale core,
    the inner layers nudged toward the camera so all three read."""
    rng = random.Random(seed)
    x0, y0, z0 = loc
    fw = Vector((toward[0], toward[1], 0)).normalized()
    tongue(a, (x0, y0, z0), h, r * 0.74, (rng.uniform(-1, 1), rng.uniform(-1, 1)), h * 0.08,
           "fire_outer", sides=6, side_curl=r * 0.2)
    for i in range(n):
        ang = 2 * PI * i / n + rng.uniform(-0.25, 0.25)
        d = Vector((math.cos(ang), math.sin(ang), 0))
        tongue(a, (x0 + d.x * r * 0.5, y0 + d.y * r * 0.5, z0), h * rng.uniform(0.5, 0.82),
               r * rng.uniform(0.42, 0.52), d, r * rng.uniform(0.35, 0.6), "fire_outer",
               side_curl=r * rng.uniform(-0.4, 0.4))
    c1 = Vector((x0, y0, z0)) + fw * r * 0.42
    for i in range(4):
        ang = 2 * PI * i / 4 + 0.4
        d = Vector((math.cos(ang), math.sin(ang), 0))
        tongue(a, c1 + d * r * 0.2, h * rng.uniform(0.45, 0.65), r * 0.36, d, r * 0.25, "fire_mid",
               side_curl=r * rng.uniform(-0.2, 0.2))
    c2 = Vector((x0, y0, z0)) + fw * r * 0.62
    for i in range(2):
        d = Vector((math.cos(i * PI + 0.3), math.sin(i * PI + 0.3), 0))
        tongue(a, c2 + d * r * 0.1, h * rng.uniform(0.26, 0.36), r * 0.2, d, r * 0.1, "fire_core")


def spark(a, p, s=0.12, mat="fire_core"):
    out = a.cyl(s * 0.6, 0.0, s, 4, loc=p, mat=mat, tint=1.0)
    out += a.cyl(s * 0.6, 0.0, s, 4, loc=p, rot=(PI, 0, 0), mat=mat, tint=1.0)
    return out


# ---------------------------------------------------------------------------
# Rocks
# ---------------------------------------------------------------------------


def low_boulder():
    a = fk.Asset("LowBoulder", "Rocks")
    # one broad mound, highest at the back right, with two lobes bulging at the
    # front-left and front-right
    top = [((-0.12, 0.06, 1.0), (0, 0, 4.0))]
    for k, (size, c, n) in enumerate((((7.2, 5.6, 4.3), (0.4, 0.25), 190),
                                      ((4.2, 4.2, 3.0), (-1.5, -0.35), 80),
                                      ((3.6, 3.0, 2.5), (1.5, -1.05), 64))):
        add_chunk(a, hewn_bm(size, c, n=n, p=2.8, taper=0.3, sink=0.3, seed=110 + k,
                             extra=top if k == 0 else ()), seed=110 + k)
    return done(a, (8, 6, 4))


def tall_boulder():
    a = fk.Asset("TallBoulder", "Rocks")
    # broad-footed spire with a blunt chiselled top, a shorter chunk leaning on its
    # front-right and a low lobe at its front-left foot
    add_chunk(a, hewn_bm((5.4, 4.6, 9.2), (-0.4, 0.3), n=160, p=2.4, taper=0.6, sink=0.6, seed=21, tilt=0.05,
                         lean=(-0.03, 0.0), extra=[((-0.15, 0.05, 1.0), (0, 0, 8.8))]), seed=21)
    add_chunk(a, hewn_bm((3.4, 3.6, 5.2), (1.5, -0.4), n=80, tilt=0.05, p=2.4, taper=0.35, sink=0.5, seed=22),
              seed=22)
    return done(a, (6.0, 5.0, 8.0))


def split_boulder():
    a = fk.Asset("SplitBoulder", "Rocks")
    H = 5.2
    pivot_z = 0.25 * H
    lean = math.radians(3.5)
    for side, w, seed in ((-1, 3.1, 31), (1, 3.4, 32)):
        bm = hewn_bm((w * 2, 5.5, H * (0.96 if side < 0 else 1.0)), (0, 0), n=96, p=2.6, taper=0.25,
                     sink=0.3, seed=seed)
        plane_cut(bm, Vector((-side, 0, 0)), Vector((0, 0, 0)))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        M = (Matrix.Translation((-0.1, 0, pivot_z)) @ Matrix.Rotation(side * lean, 4, "Y")
             @ Matrix.Translation((0, 0, -pivot_z)))
        verts = add_chunk(a, bm, M, seed=seed,
                          override=lambda f, s=side: (2, 0.55) if f.normal.x * s < -0.9 else None)
        for v in verts:
            v.co.z = max(v.co.z, 0.0)
    return done(a, (6.5, 5.5, 5.2))


def crack_cutter(boxes):
    cutter = bmesh.new()
    for c, s, yaw in boxes:
        vs = bmesh.ops.create_cube(cutter, size=1.0)["verts"]
        bmesh.ops.scale(cutter, vec=s, verts=vs)
        bmesh.ops.rotate(cutter, verts=vs, cent=(0, 0, 0), matrix=Matrix.Rotation(yaw, 3, "Z"))
        bmesh.ops.translate(cutter, vec=c, verts=vs)
    return cutter


def long_boulder():
    a = fk.Asset("LongBoulder", "Rocks")
    # a long slab rising to the right: a lower block at the left end, and the main
    # block split by one stepped crack over its top and down its sides
    add_chunk(a, hewn_bm((5.2, 4.6, 4.2), (-2.8, -0.1), n=90, p=2.8, taper=0.26, sink=0.3, seed=41,
                         extra=[((-0.12, 0.03, 1.0), (0, 0, 3.75))]), seed=41)
    main = hewn_bm((8.0, 5.0, 4.8), (1.5, 0.1), n=140, p=3.0, taper=0.3, sink=0.3, seed=42,
                   extra=[((-0.1, 0.03, 1.0), (0, 0, 4.1))])
    finish_rock(main, seed=42)
    boxes = []
    for (xc, y0, y1, yaw) in ((1.7, -3.0, -0.3, 0.1), (2.05, -0.3, 3.0, -0.06)):
        for z0, z1, w in ((1.0, 2.4, 0.08), (2.4, 5.2, 0.16)):
            boxes.append(((xc, (y0 + y1) / 2, (z0 + z1) / 2), (w, y1 - y0, z1 - z0), yaw))
    cutter = crack_cutter(boxes)
    res = boolean_diff(main, cutter, mats=ROCK_MATS)
    cutter.free()
    main.free()
    bmesh.ops.triangulate(res, faces=[f for f in res.faces if len(f.verts) > 4], ngon_method="EAR_CLIP")

    def in_crack(face):
        p = face.calc_center_median()
        for c, s, yaw in boxes:
            q = Matrix.Rotation(-yaw, 3, "Z") @ (p - Vector(c))
            if all(abs(q[i]) <= s[i] / 2 + 0.03 for i in range(3)):
                return ("stone_dark", 0.62)
        return None

    append_bm(a, res, mats=ROCK_MATS, classify=in_crack)
    res.free()
    return done(a, (11, 5, 4.4))


# ---------------------------------------------------------------------------
# Rune slabs
# ---------------------------------------------------------------------------


def slab_planes(T, rx, ry, center=(0.0, 0.0), k=7, r0=0.62, tilt=7.0, seed=0, normal=(0, 0, 1)):
    """A flat top at height T (plane `normal` through the centre) ringed by gently
    tilted plates starting at r0 of the radius."""
    rng = random.Random(seed)
    nn = Vector(normal).normalized()
    out = [(nn, (center[0], center[1], T))]
    for i in range(k):
        ph = 2 * PI * (i + rng.uniform(-0.3, 0.3)) / k
        th = math.radians(tilt * rng.uniform(0.7, 1.3))
        d = Vector((math.cos(ph), math.sin(ph), 0))
        n = (nn * math.cos(th) + d * math.sin(th)).normalized()
        p = Vector((center[0] + d.x * rx * r0 * rng.uniform(0.9, 1.1),
                    center[1] + d.y * ry * r0 * rng.uniform(0.9, 1.1), 0))
        p.z = T - (nn.x * (p.x - center[0]) + nn.y * (p.y - center[1])) / nn.z
        out.append((n, p))
    return out


def carve2(a, slab, M, paths, seed=0):
    """Finish slab as hewn rock, cut glyph/crack channels along surface frame M
    (darkened), and lay a pale inlay into the filled ones. paths: [(pts, w, d, fill)]"""
    finish_rock(slab, seed=seed)
    cutter = bmesh.new()
    for pts, w, d, fill in paths:
        strips_bm(cutter, pts, w, -d, 0.8)
    bmesh.ops.transform(cutter, matrix=M, verts=cutter.verts[:])
    res = boolean_diff(slab, cutter, mats=ROCK_MATS)
    cutter.free()
    slab.free()
    bmesh.ops.triangulate(res, faces=[f for f in res.faces if len(f.verts) > 4],
                          quad_method="BEAUTY", ngon_method="EAR_CLIP")
    Minv = M.inverted()

    def channel(face):
        q = Minv @ face.calc_center_median()
        if q.z > -0.004:
            return None
        for pts, w, d, fill in paths:
            if q.z > -d - 0.03 and seg_dist(q.x, q.y, pts) <= w / 2 + 0.03:
                return ("stone_dark", 0.62 if fill else 0.7)
        return None

    append_bm(a, res, mats=ROCK_MATS, classify=channel)
    res.free()
    for pts, w, d, fill in paths:
        if fill:
            v = a.strip(pts, w - 0.12, d - 0.05, mat="rune_blue")
            xform(a, v, M @ Matrix.Translation((0, 0, -d + 0.005)))


def large_rune():
    a = fk.Asset("LargeRuneStone", "Rocks")
    T = 1.9
    slab = hewn_bm((8.8, 7.4, T * 1.45), (0.3, 0.3), n=110, p=2.6, sink=0.05, seed=51,
                   extra=slab_planes(T, 4.4, 3.7, (0.3, 0.3), k=8, r0=0.66, seed=51))
    M = surface_matrix((0.2, 0.3, T), (0, 0, 1), yaw=math.radians(-15))
    paths = [(diamond(2.15, 2.15), 0.44, 0.16, True), (diamond(1.35, 1.35), 0.36, 0.16, True),
             (diamond(0.55, 0.55), 0.26, 0.16, True)]
    for pts in (((-2.6, 0.2), (-3.3, -0.5), (-4.2, -0.6)), ((-1.1, 2.0), (-1.6, 2.9), (-1.4, 3.6)),
                ((2.4, 0.6), (3.3, 0.9), (4.4, 0.6)), ((1.3, -2.0), (1.9, -2.9), (1.7, -3.6)),
                ((-1.4, -1.6), (-2.2, -2.5), (-2.9, -2.9)), ((1.6, 1.9), (2.4, 2.6), (3.2, 2.7))):
        paths.append((list(pts), 0.08, 0.07, False))
    carve2(a, slab, M, paths, seed=51)
    # lower lobes around the main slab give the lumpy outline and stepped edge
    add_chunk(a, hewn_bm((4.2, 4.0, 2.4), (-2.9, -1.4), n=50, p=2.6, sink=0.05, seed=52,
                         extra=[((0.04, -0.03, 1.0), (0, 0, 1.72))]), seed=52)
    add_chunk(a, hewn_bm((4.0, 4.4, 2.4), (3.1, -0.8), n=50, p=2.6, sink=0.05, seed=53,
                         extra=[((-0.04, -0.03, 1.0), (0, 0, 1.76))]), seed=53)
    return done(a, (10, 8, 1.9), [("rune_glow", M @ Vector((0, 0, 0.3)))])


def elongated_rune():
    a = fk.Asset("ElongatedRuneStone", "Rocks")
    T = 1.6
    n = Vector((0.03, -0.12, 1.0)).normalized()
    c0 = (-0.5, 0.2)
    slab = hewn_bm((6.6, 4.6, T * 1.45), c0, n=96, p=2.6, sink=0.05, seed=61,
                   extra=slab_planes(T, 3.3, 2.3, c0, k=7, r0=0.62, seed=61, normal=n))
    M = surface_matrix((c0[0] + 0.1, c0[1] - 0.05, T), n, yaw=math.radians(-18))
    paths = [([(-0.8, -0.8), (0.0, 0.9), (0.8, -0.8)], 0.56, 0.15, True)]
    for pts in (((-1.4, 0.5), (-2.2, 0.9), (-3.0, 0.8)), ((1.3, -0.6), (2.0, -1.2), (2.6, -1.9)),
                ((0.6, 1.2), (0.9, 1.8), (0.7, 2.3))):
        paths.append((list(pts), 0.08, 0.07, False))
    carve2(a, slab, M, paths, seed=61)
    # a lower ledge at the right end
    add_chunk(a, hewn_bm((3.4, 3.8, 1.9), (2.3, 0.25), n=44, p=2.6, sink=0.05, seed=62,
                         extra=[((-0.05, -0.05, 1.0), (0, 0, 1.3))]), seed=62)
    return done(a, (8, 5, 1.6), [("rune_glow", M @ Vector((0, 0, 0.3)))])


def triangular_rune():
    a = fk.Asset("TriangularRuneStone", "Rocks")
    # low triangular mound: long front edge, apex at the back; one chisel plane just
    # grazing the front slope gives the flat facet that carries the glyph
    fn = Vector((-0.12, -1.1, 1.0)).normalized()
    slab = hewn_bm((6.0, 5.6, 2.8), (0.0, 0.0), n=130, p=2.0, taper=0.6, sink=0.05, seed=71,
                   lean=(-0.08, 0.1), lobes=[(3, 0.1, 1.5 * PI)])
    hi = max(v.co.dot(fn) for v in slab.verts)
    plane_cut(slab, fn, fn * (hi - 0.18))
    bmesh.ops.recalc_face_normals(slab, faces=slab.faces[:])
    slab.normal_update()
    gf = max(slab.faces, key=lambda f: f.normal.dot(fn))
    c = gf.calc_center_median()
    M = surface_matrix(c, fn, yaw=math.radians(-18))
    paths = [(diamond(0.36, 0.42, 0.0, 0.55), 0.24, 0.13, True),
             ([(0.0, 0.13), (0.0, -0.4)], 0.24, 0.13, True),
             ([(-0.42, -0.9), (0.0, -0.4), (0.5, -0.95)], 0.24, 0.13, True)]
    carve2(a, slab, M, paths, seed=71)
    return done(a, (6.0, 5.2, 2.5), [("rune_glow", M @ Vector((0, 0, 0.3)))])


def stepping_stone():
    a = fk.Asset("SteppingStone", "Rocks")
    T = 1.75
    c0 = (-0.3, 0.3)
    slab = hewn_bm((7.4, 5.4, T * 1.45), c0, n=100, p=2.6, sink=0.05, seed=81,
                   extra=slab_planes(T, 3.7, 2.7, c0, k=8, r0=0.5, tilt=5.0, seed=81))
    M = surface_matrix((c0[0], c0[1], T), (0, 0, 1))
    paths = []
    for pts in (((-2.9, -0.6), (-1.6, -0.3), (-0.6, -0.8), (0.6, -0.6), (2.0, -1.0), (3.2, -0.9)),
                ((-1.6, -0.3), (-1.4, 0.8), (-1.9, 1.9), (-1.8, 2.6)),
                ((0.6, -0.6), (0.9, 0.5), (0.6, 1.4), (0.9, 2.5)),
                ((0.9, 0.5), (2.0, 0.6), (3.0, 1.1)),
                ((-0.6, -0.8), (-0.8, -1.8), (-0.6, -2.6))):
        paths.append((list(pts), 0.08, 0.07, False))
    carve2(a, slab, M, paths, seed=81)
    # a lower plate stepping down at the front right
    add_chunk(a, hewn_bm((3.6, 3.2, 2.0), (1.9, -1.2), n=44, p=2.6, sink=0.05, seed=82,
                         extra=[((0.03, -0.05, 1.0), (0, 0, 1.45))]), seed=82)
    return done(a, (8, 6, 1.75))


# ---------------------------------------------------------------------------
# Logs and stumps
# ---------------------------------------------------------------------------


def cut_log():
    a = fk.Asset("CutLog", "Camp")
    L, r = 7.4, 1.47
    v = bark_log(a, L, r, plates=11, segs=2, seed=91)
    xform(a, v, axis_matrix((-L / 2, 0, r), (1, 0, 0)))
    return done(a, (7.4, 2.94, 2.94))


def fallen_log():
    a = fk.Asset("FallenLog", "Camp")
    r1 = 1.3
    # main trunk, tapering from the cut end on the left to a blunt end on the right
    v = bark_log(a, 7.7, r1, plates=11, segs=2, seed=101, end="plain")
    xform(a, v, axis_matrix((-4.5, 0, r1), (1, 0, 0)))
    for q in v:
        t = (q.co.x + 4.5) / 7.7
        f = 1 - 0.2 * max(0.0, min(1.0, t))
        q.co.y *= f
        q.co.z = r1 + (q.co.z - r1) * f
        q.co.z -= 0.12 * max(0.0, t - 0.6)
    # thick forked prong rising up and to the right from the top of the trunk
    ang = math.radians(27)
    d2 = Vector((math.cos(ang), 0.12, math.sin(ang))).normalized()
    p2 = Vector((0.2, 0.25, r1 + 0.05))
    v = bark_log(a, 3.6, 0.82, plates=9, segs=1, seed=102, start="plain", fracs=(0.6, 0.3))
    xform(a, v, axis_matrix(p2, d2))
    # chunky angled stub branch propping the log at the front
    rings, fr = tube(a, [(0.3, -0.5, 1.0), (0.95, -1.25, 0.45), (1.25, -1.55, 0.12)], [0.5, 0.46, 0.44],
                     sides=6, grooves=True, jitter=0.04, mat="bark", groove_mat="wood_dark")
    cap_flat(a, rings[0])
    cut_end(a, rings[-1], fr[-1][0], fr[-1][1], rings=True, fracs=(0.55,), recess=0.03)
    return done(a, (9, 3.2, 3.4))


def stump():
    a = fk.Asset("Stump", "Camp")
    r, h = 1.22, 2.3
    top = rooted_trunk(a, r, h, n_roots=7, base_mul=1.6, zm=0.7, plates=12, seed=111)
    trunk_top(a, top, h, fracs=(0.74, 0.48, 0.22))
    return done(a, (3.4, 3.4, 2.4))


def chopping_stump():
    a = fk.Asset("ChoppingStump", "Camp")
    r, h = 0.93, 2.95
    s = fk.Asset("_scratch", "_scratch", seed=7)
    top = rooted_trunk(s, r, h, n_roots=6, base_mul=1.5, zm=0.5, plates=11, seed=121)
    trunk_top(s, top, h, fracs=(), rings=False)
    # V-wedge split from the top down to ~40% of the height
    xa, apex = -0.08, h * 0.6
    wedge = bmesh.new()
    tri = [(xa - 0.5, h + 0.4), (xa + 0.42, h + 0.4), (xa, apex)]
    vs = [wedge.verts.new((x, y, z)) for (x, z) in tri for y in (-2.0, 2.0)]
    f0, b0, f1, b1, f2, b2 = vs
    for q in ((f0, f1, f2), (b0, b2, b1), (f0, b0, b1, f1), (f1, b1, b2, f2), (f2, b2, b0, f0)):
        wedge.faces.new(q)
    bmesh.ops.recalc_face_normals(wedge, faces=wedge.faces[:])
    res = boolean_diff(s.bm, wedge, mats=s.mats)
    wedge.free()
    s.bm.free()

    def in_wedge(face):
        c = face.calc_center_median()
        if c.z < apex - 0.05:
            return None
        hw = (c.z - apex) / (h + 0.4 - apex)
        if xa - 0.5 * hw - 0.04 <= c.x <= xa + 0.42 * hw + 0.04:
            return ("wood_light", 0.95)
        return None

    append_bm(a, res, mats=s.mats, classify=in_wedge)
    res.free()
    # growth-ring arcs on the two halves of the top
    zt = h + 0.06 - 0.02
    for fr in (0.72, 0.44, 0.2):
        rr = r * 0.94 * 0.93 * fr
        for side in (-1, 1):
            arc = []
            for k in range(7):
                b = -PI / 2 + PI * k / 6
                x = side * rr * math.cos(b) + xa
                if side * (x - xa) >= 0.24:
                    arc.append((x, rr * math.sin(b)))
            if len(arc) >= 2:
                a.strip(arc, 0.045, 0.03, loc=(0, 0, zt), mat="wood")
    return done(a, (2.6, 2.6, 3.0))


# ---------------------------------------------------------------------------
# Camp
# ---------------------------------------------------------------------------


def campfire():
    a = fk.Asset("Campfire", "Camp")
    R, n = 2.55, 12
    # a tight ring of chunky hewn stones
    for i in range(n):
        ang = 2 * PI * i / n + 0.1
        k = 1.0 + a.rng.uniform(-0.06, 0.1)
        bm = hewn_bm((1.45 * k, 1.3 * k, 1.12 * k), (0, 0), n=14, p=2.8, taper=0.15, sink=0.2,
                     seed=200 + i, jitter=0.04)
        M = Matrix.Translation((R * math.cos(ang), R * math.sin(ang), 0)) @ Matrix.Rotation(ang, 4, "Z")
        add_chunk(a, bm, M, seed=200 + i, dark=0.2, bevel=0.018)
    a.cyl(1.85, 1.7, 0.16, 10, mat="charcoal")
    for i in range(7):
        ang = a.rng.uniform(0, 2 * PI)
        rr = a.rng.uniform(0.3, 1.4)
        a.ico((0.26, 0.26, 0.14), loc=(rr * math.cos(ang), rr * math.sin(ang), 0.16), subdiv=1,
              mat="ember" if i % 2 else "charcoal")
    # teepee of thick split logs leaning into the fire
    for i in range(6):
        ang = 2 * PI * i / 6 + 0.25
        p1 = (1.85 * math.cos(ang), 1.85 * math.sin(ang), 0.12)
        p2 = (0.2 * math.cos(ang + 0.6), 0.2 * math.sin(ang + 0.6), 2.3)
        a.beam(p1, p2, 0.34, mat="wood" if i % 2 else "wood_dark", sides=6)
    flame(a, (0, 0, 0.25), 4.1, 1.6, n=8, seed=7)
    for p, sz in (((-1.25, -0.3, 3.9), 0.24), ((1.15, -0.4, 4.2), 0.2), ((0.4, 0.6, 4.45), 0.22)):
        spark(a, p, sz, mat="fire_mid" if sz > 0.21 else "fire_core")
    return done(a, (6.5, 6.5, 4.6), [("campfire", (0, 0, 2.0))])


def split_block(a, x, length=1.75, w=0.95, h=0.7):
    """Bench leg: a chunky split block along Y with end grain at the ends."""
    outline = [(-w / 2, 0), (w / 2, 0), (w / 2 + 0.03, h * 0.62), (w * 0.22, h), (-w * 0.3, h * 0.97),
               (-w / 2 - 0.02, h * 0.58)]
    v = a.poly_prism(outline, length, mat="wood_light")
    xform(a, v, Matrix.Translation((x, length / 2, 0)) @ Matrix.Rotation(PI / 2, 4, "X"))

    def pick(f):
        if abs(f.normal.y) > 0.9:
            return "wood_end"
        if f.normal.z > 0.5:
            return "bark"
        return None

    recolor(a, v, pick)
    for yy, nrm in ((-length / 2 - 0.005, (0, -1, 0)), (length / 2 + 0.005, (0, 1, 0))):
        arc = [(0.32 * math.cos(b), 0.32 * math.sin(b)) for b in [PI * k / 5 for k in range(6)]]
        s = a.strip(arc, 0.04, 0.03, mat="wood")
        xform(a, s, Matrix.Translation((x, yy, 0.02)) @ Vector(nrm).to_track_quat("Z", "Y").to_matrix().to_4x4())


def log_bench():
    a = fk.Asset("LogBench", "Camp")
    L, r = 7.0, 0.8
    v = bark_log(a, L, r, plates=10, segs=5, seed=131, fracs=(0.78, 0.52, 0.26))
    xform(a, v, axis_matrix((-L / 2, 0, 0.6 + r - 0.06), (1, 0, 0)))
    for x in (-2.35, 2.35):
        split_block(a, x)
    return done(a, (7, 1.8, 2.15))


def torch_post():
    a = fk.Asset("TorchPost", "Camp")
    pr = 0.5
    # bark-stripped post
    v = bark_log(a, 5.0, pr, plates=7, segs=1, seed=151, start="plain", end="plain", thick=0.09)
    # straight bundle of split sticks around the top, a touch wider than the post
    for i in range(9):
        ang = 2 * PI * i / 9
        p0 = Vector((0.44 * math.cos(ang), 0.44 * math.sin(ang), 4.55))
        p1 = Vector((0.48 * math.cos(ang), 0.48 * math.sin(ang), 6.25 + 0.08 * ((i * 5) % 3)))
        rings, fr = tube(a, [p0, p1], [0.16, 0.16], sides=4, flute=0.0, jitter=0.04,
                         mat="wood_light" if i % 3 == 0 else "wood", phase=ang)
        cap_flat(a, rings[0], "wood")
        cap_flat(a, rings[-1], "charcoal", 1.0)
    a.cyl(0.44, 0.5, 0.2, 9, loc=(0, 0, 6.0), mat="charcoal")
    # thick rope coils binding the bundle, and a hanging loop
    for k in range(4):
        z = 4.75 + k * 0.17
        a.torus(0.66, 0.085, loc=(0, 0, z), rot=(0.06 * (k - 1.5), 0.05 * (1 - k % 2), 0), seg=12, rseg=4,
                mat="rope" if k % 2 == 0 else "rope_dark")
    loop = [(-0.2, -0.66, 4.85), (-0.32, -0.74, 4.4), (-0.18, -0.76, 4.0), (0.08, -0.74, 4.05),
            (0.16, -0.69, 4.45), (0.08, -0.64, 4.85)]
    a.tube_loop(loop, 0.07, closed=False, mat="rope")
    flame(a, (0, 0, 6.05), 1.3, 0.5, n=5, seed=3)
    spark(a, (0.3, -0.15, 7.35), 0.12)
    spark(a, (-0.45, 0.0, 7.05), 0.1, mat="fire_mid")
    return done(a, (1.45, 1.45, 7.0), [("torch_fire", (0, 0, 6.4))])


def stone_brazier():
    a = fk.Asset("StoneBrazier", "Camp")
    W = 3.1
    # two-tier stepped plinth, each tier split into blocks (masonry seams)
    for dx in (-0.775, 0.775):
        a.stone_block((1.53, W, 0.42), loc=(dx, 0, 0.21), bevel=0.06, jitter=0.015)
    for dy in (-0.68, 0.68):
        a.stone_block((2.72, 1.34, 0.3), loc=(0, dy, 0.57), bevel=0.05, jitter=0.015, mat="stone_dark")
    z0, bh = 0.72, 1.7
    b = 1.12
    a.box((2.1, 2.1, bh), loc=(0, 0, z0), base=True, mat="stone_dark")
    for sx in (-1, 1):
        for sy in (-1, 1):
            for k, (zz, hh) in enumerate(((z0, bh * 0.52), (z0 + bh * 0.52, bh * 0.48))):
                a.stone_block((0.54, 0.54, hh - 0.04), loc=(sx * b, sy * b, zz + hh / 2), bevel=0.05,
                              jitter=0.012)
    zc = z0 + bh / 2
    for k in range(4):
        rz = k * PI / 2
        R = Matrix.Rotation(rz, 4, "Z")
        for zz in (z0 + 0.13, z0 + bh - 0.13):  # rails framing the recessed panel
            v = a.stone_block((1.72, 0.3, 0.24), bevel=0.04, jitter=0.0)
            xform(a, v, R @ Matrix.Translation((0, -1.12, zz)))
        v = a.poly_prism([(0, -0.48), (0.34, 0), (0, 0.48), (-0.34, 0)], 0.16, mat="stone")
        xform(a, v, R @ Matrix.Translation((0, -1.04, zc)) @ Matrix.Rotation(PI / 2, 4, "X"))
        v = a.poly_prism([(0, -0.3), (0.21, 0), (0, 0.3), (-0.21, 0)], 0.06, mat="stone_light")
        xform(a, v, R @ Matrix.Translation((0, -1.19, zc)) @ Matrix.Rotation(PI / 2, 4, "X"))
    zt = z0 + bh
    for dx in (-0.69, 0.69):
        a.stone_block((1.36, 2.72, 0.3), loc=(dx, 0, zt + 0.15), bevel=0.05, jitter=0.015)
    zb = zt + 0.3
    for k in range(4):
        rz = k * PI / 2
        v = a.stone_block((1.4, 0.42, 0.42), bevel=0.05, jitter=0.01)
        xform(a, v, Matrix.Rotation(rz, 4, "Z") @ Matrix.Translation((0, -1.07, zb + 0.21)))
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.stone_block((0.6, 0.6, 0.62), loc=(sx * 1.07, sy * 1.07, zb + 0.31), bevel=0.06)
    a.cyl(0.9, 0.9, 0.25, 8, loc=(0, 0, zb), mat="charcoal")
    for i in range(4):
        ang = i * PI / 2 + 0.4
        a.beam((0.7 * math.cos(ang), 0.7 * math.sin(ang), zb + 0.25),
               (-0.1 * math.cos(ang), -0.1 * math.sin(ang), zb + 0.6), 0.12, sides=5, mat="wood_dark")
    flame(a, (0, 0, zb + 0.22), 1.45, 0.62, n=6, seed=5)
    spark(a, (0.45, -0.3, zb + 1.55), 0.12)
    return done(a, (3.1, 3.1, 4.1), [("brazier_fire", (0, 0, zb + 0.35))])


# ---------------------------------------------------------------------------
# Render (per-asset camera)
# ---------------------------------------------------------------------------

VIEWS = {  # name: (azimuth, elevation, fill fraction of the cell)
    "LowBoulder": (-20, 22, 0.74),
    "TallBoulder": (-15, 18, 0.82),
    "SplitBoulder": (-18, 20, 0.74),
    "LongBoulder": (-20, 22, 0.8),
    "LargeRuneStone": (-15, 38, 0.82),
    "ElongatedRuneStone": (-18, 36, 0.72),
    "TriangularRuneStone": (-18, 28, 0.64),
    "SteppingStone": (-18, 32, 0.78),
    "CutLog": (-38, 20, 0.8),
    "FallenLog": (-34, 22, 0.8),
    "Stump": (-20, 22, 0.66),
    "ChoppingStump": (-20, 20, 0.72),
    "Campfire": (-15, 26, 0.8),
    "LogBench": (-30, 20, 0.8),
    "TorchPost": (-20, 18, 0.82),
    "StoneBrazier": (-30, 16, 0.78),
}


def frame_fit(obj, az, el, fill):
    """Like fk.frame, but fits the projected mesh to `fill` of the frame on both axes
    (fk.frame fits a bounding sphere to the horizontal FOV, which crops landscape cells)."""
    from bpy_extras.object_utils import world_to_camera_view
    scene = bpy.context.scene
    cam = bpy.data.objects["FB_Cam"]
    mw = obj.matrix_world
    pts = [mw @ v.co for v in obj.data.vertices]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    target = (lo + hi) / 2
    d = (hi - lo).length * 1.6
    a_, e_ = math.radians(az), math.radians(el)
    direction = Vector((math.sin(a_), -math.cos(a_), math.tan(e_))).normalized()
    aspect = scene.render.resolution_x / scene.render.resolution_y
    for _ in range(8):
        cam.location = target + direction * d
        cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
        bpy.context.view_layer.update()
        co = [world_to_camera_view(scene, cam, p) for p in pts]
        xs, ys = [c.x for c in co], [c.y for c in co]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        ext = max((max(xs) - min(xs)) / fill, (max(ys) - min(ys)) / fill)
        w = 2 * d * math.tan(cam.data.angle / 2)
        rot = cam.matrix_world.to_3x3()
        target = target + rot @ Vector(((cx - 0.5) * w, (cy - 0.5) * w / aspect, 0))
        d *= ext
    bpy.data.objects["FB_Ground"].location = (target.x, target.y, lo.z)


def render_cell(obj, path, res, az, el, fill, samples=32):
    scene = bpy.context.scene
    fk._studio(scene)
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    try:
        scene.eevee.taa_render_samples = samples
    except AttributeError:
        pass
    hidden = []
    for o in scene.objects:
        if o.type == "MESH" and o is not obj and o.name != "FB_Ground" and not o.hide_render:
            hidden.append(o)
            o.hide_render = True
    frame_fit(obj, az, el, fill)
    scene.render.filepath = path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    for o in hidden:
        o.hide_render = False


def render_sheet(objs, path, cols=4, cell=(384, 288), order=None):
    base, _ = os.path.splitext(path)
    cells = []
    for i, o in enumerate(objs):
        idx = order.index(o.name) if order else i  # keep sheet numbering when filtered
        p = f"{base}_cells/{idx + 1:02d}_{o.name}.png"
        az, el, m = VIEWS.get(o.name, (fk.DEFAULT_AZIMUTH, fk.DEFAULT_ELEVATION, 0.8))
        render_cell(o, p, cell, az, el, m)
        cells.append(p)
    rows = math.ceil(len(objs) / cols)
    w, h = cell
    sheet = np.ones((rows * h, cols * w, 4), dtype=np.float32)
    for i, p in enumerate(cells):
        img = bpy.data.images.load(p, check_existing=False)
        px = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], 4)
        r, c = divmod(i, cols)
        y0 = (rows - 1 - r) * h
        sheet[y0:y0 + h, c * w:c * w + w] = px[:h, :w]
        bpy.data.images.remove(img)
    out = bpy.data.images.new("FB_Sheet", cols * w, rows * h, alpha=True)
    out.pixels = sheet.ravel()
    out.filepath_raw = path
    out.file_format = "PNG"
    out.save()
    bpy.data.images.remove(out)


# ---------------------------------------------------------------------------


def main():
    fk.reset_file()
    builders = [low_boulder, tall_boulder, split_boulder, long_boulder,
                large_rune, elongated_rune, triangular_rune, stepping_stone,
                cut_log, fallen_log, stump, chopping_stump,
                campfire, log_bench, torch_post, stone_brazier]
    objs = [b() for b in builders]
    fk.layout_row(objs)
    fk.save(os.path.join(ROOT, "assets", "06_rocks_runes_camp.blend"))
    only = os.environ.get("FB_ONLY")
    robjs = [o for o in objs if not only or o.name in only.split(",")]
    render_sheet(robjs, os.path.join(ROOT, "renders", "06_rocks_runes_camp.png"), cols=4,
                 order=[o.name for o in objs])
    print("DONE")


main()
