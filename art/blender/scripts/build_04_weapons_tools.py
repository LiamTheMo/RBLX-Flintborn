"""Build sheet 04: Weapons & Tools.

Every tool is modelled upright: grip end at the origin, head toward +Z, blade
faces toward -X where it has one, broad faces toward -Y. The contact-sheet
render tilts each one diagonally (head upper-left) to match the reference; the
saved objects keep rotation (0, 0, 0).

    blender --background --factory-startup --python build_04_weapons_tools.py
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))

import bmesh  # noqa: E402
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

import flintkit as fk  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, ".."))
BLEND = os.path.join(ROOT, "assets", "04_weapons_tools.blend")
SHEET = os.path.join(ROOT, "renders", "04_weapons_tools.png")

TAU = 2 * math.pi
Y = Vector((0, 1, 0))
Z = Vector((0, 0, 1))


# ---------------------------------------------------------------------------
# Local helpers (all take an fk.Asset)
# ---------------------------------------------------------------------------


def loft(a, rings, mat="wood", cap0=True, cap1=True, face_mat=None, tint=None, ftv=0.0):
    """Skin consecutive closed rings of points. A ring of one point is a tip.
    face_mat(segment, column) may return a palette key to override a face."""
    bm = a.bm
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
    n = max(len(r) for r in vr)
    faces = []
    for i in range(len(vr) - 1):
        A, B = vr[i], vr[i + 1]
        for j in range(n):
            if len(A) == 1:
                f = bm.faces.new((A[0], B[(j + 1) % n], B[j]))
            elif len(B) == 1:
                f = bm.faces.new((A[j], A[(j + 1) % n], B[0]))
            else:
                f = bm.faces.new((A[j], A[(j + 1) % n], B[(j + 1) % n], B[j]))
            faces.append((f, i, j))
    if cap0 and len(vr[0]) > 2:
        bm.faces.new(list(reversed(vr[0])))
    if cap1 and len(vr[-1]) > 2:
        bm.faces.new(vr[-1])
    verts = [v for r in vr for v in r]
    a._finish(verts, mat, tint, 0.0, ftv)
    if face_mat:
        for f, i, j in faces:
            m = face_mat(i, j)
            if m:
                f.material_index = a._mi(m)
    return verts


def hewn(a, prof, sides=7, mat="wood", end_mat="wood_light", end0=True, end1=True, jit=0.07,
         wob=0.025, chamfer=0.3, x=0.0, y=0.0, tint=None, phase=None, ftv=0.08, bend=None,
         groove=0.13, streak=0.25):
    """Hand-hewn faceted post along +Z through (z, r) profile points, with
    chamfered cut ends. `groove` cuts a shallow V-groove between facets (wood
    grain); `streak` darkens a share of the facet strips. bend(z) -> x offset."""
    rng = a.rng
    phase = rng.uniform(0, TAU) if phase is None else phase
    if groove:
        sides *= 2
    cols = [(1 + rng.uniform(-jit, jit)) * (1 - groove if groove and j % 2 else 1)
            for j in range(sides)]
    dark = {j for j in range(sides) if rng.random() < streak} if mat.startswith("wood") else set()
    t = tint if tint is not None else 1 + rng.uniform(-a.tint_var, a.tint_var)

    def ring(z, r, k=1.0, dx=0.0, dy=0.0):
        bx = bend(z) if bend else 0.0
        return [(x + bx + dx + r * k * cols[j] * math.cos(phase + TAU * j / sides),
                 y + dy + r * k * cols[j] * math.sin(phase + TAU * j / sides), z)
                for j in range(sides)]

    (z0, r0), (z1, r1) = prof[0], prof[-1]
    c0, c1 = r0 * chamfer, r1 * chamfer
    body = [ring(z0 + c0 if end0 else z0, r0)]
    for z, r in prof[1:-1]:
        body.append(ring(z, r, 1 + rng.uniform(-wob, wob), rng.uniform(-wob, wob) * r,
                         rng.uniform(-wob, wob) * r))
    body.append(ring(z1 - c1 if end1 else z1, r1))
    verts = []
    if end0:
        verts += loft(a, [ring(z0, r0, 0.74), body[0]], end_mat, True, False, tint=t)
    verts += loft(a, body, mat, not end0, not end1, tint=t, ftv=ftv,
                  face_mat=(lambda i, j: "wood_dark" if j in dark else None) if dark else None)
    if end1:
        verts += loft(a, [body[-1], ring(z1, r1, 0.74)], end_mat, False, True, tint=t)
    return verts


def sweep(a, pts, rads, sides=4, mat="stone", phase=0.0, cap0=True, cap1=True, ftv=0.05,
          face_mat=None, jit=0.0, tint=None, section=None):
    """Sweep a cross-section along a polyline in the XZ plane. rads[i] = (rw, rt):
    half-size in the curve plane and along Y; rw == 0 makes a tip. `section` is
    an optional list of (cn, cy) unit coefficients replacing the round ring."""
    pts = [Vector(p) for p in pts]
    sec = section or [(math.cos(phase + TAU * j / sides), math.sin(phase + TAU * j / sides))
                      for j in range(sides)]
    rings = []
    for i, p in enumerate(pts):
        tng = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        nrm = tng.cross(Y).normalized()
        rw, rt = rads[i]
        if rw < 1e-4:
            rings.append([tuple(p)])
            continue
        ring = []
        for cn, cy in sec:
            q = p + rw * cn * nrm + rt * cy * Y
            if jit:
                q += Vector([a.rng.uniform(-jit, jit) for _ in range(3)])
            ring.append(tuple(q))
        rings.append(ring)
    return loft(a, rings, mat, cap0, cap1, face_mat, tint, ftv)


def speckle(a, verts, base="stone", p=0.3):
    """Re-colour some faces of a stone part darker/lighter for chiselled facets."""
    for f in fk._faces_of(verts):
        r = a.rng.random()
        if r < p * 0.55:
            f.material_index = a._mi(base + "_dark")
        elif r < p:
            f.material_index = a._mi(base + "_light")
    return verts




def cell_stone(a, half, loc=(0, 0, 0), rot=(0, 0, 0), n=24, jit=0.3, dmin=0.9, cuts=(),
               mat="stone", ftv=0.26, speck=0.22, seam=0.011, tint=None, tilt=0.26, lumpy=0.0,
               up=None):
    """Knapped stone of big flat chipped cells: the intersection of `n` half-spaces
    tangent to the ellipsoid of `half` extents, each tipped by up to `tilt` rad so
    neighbouring chips catch the light differently (plus `cuts`: (normal, offset)
    planes given in unit-sphere space). Built as the polar dual of a convex hull,
    so every cell is a planar 5-7 sided facet like the reference stones.
    `seam` bevels the cell edges into thin dark seams. `lumpy` (0..1) makes an
    irregular chipped lump: uneven chip sizes, a few big random cut planes and
    low-frequency bulges in the plane offsets (facets stay planar). Facets whose
    local normal faces `up` (the display up axis) are tinted a little lighter."""
    rng = a.rng
    big_cuts, lobes = [], []
    if lumpy:
        for _ in range(int(1 + 2 * lumpy)):  # a couple of big knapping scars
            cn = Vector([rng.gauss(0, 1) for _ in range(3)]).normalized()
            big_cuts.append((tuple(cn), rng.uniform(0.78, 0.9)))
        for _ in range(3):
            lobes.append((Vector([rng.gauss(0, 1) for _ in range(3)]).normalized(),
                          rng.uniform(-0.1, 0.3) * lumpy))
    cuts = list(cuts) + big_cuts
    ga = math.pi * (3 - math.sqrt(5))
    off = rng.uniform(0, TAU)
    # chip centres spread evenly over the ellipsoid's surface (dart throwing over
    # a dense spiral of candidates), so flat faces get as many chips as the rim
    hx, hy, hz = half
    pp = 1.6075
    area = 4 * math.pi * (((hx * hy) ** pp + (hx * hz) ** pp + (hy * hz) ** pp) / 3) ** (1 / pp)
    dmin_sep = math.sqrt(0.6 * area / n)
    m = n * 14
    cands = []
    for i in range(m):
        yy = 1 - 2 * (i + 0.5) / m
        rr = math.sqrt(max(0.0, 1 - yy * yy))
        phi = off + i * ga
        d = Vector((math.cos(phi) * rr, yy, math.sin(phi) * rr))
        d += Vector([rng.uniform(-jit, jit) * 0.15 for _ in range(3)])
        d.normalize()
        cands.append(d)
    rng.shuffle(cands)
    unit_cuts = [(Vector(cn).normalized(), co / Vector(cn).length) for cn, co in cuts]
    chosen = []
    for d in cands:
        if any(cn.dot(d) > co - 0.05 for cn, co in unit_cuts):
            continue  # that part of the surface belongs to a cut plane
        q = Vector((d.x * hx, d.y * hy, d.z * hz))
        s = dmin_sep * rng.uniform(1 - 0.4 * lumpy, 1 + 0.55 * lumpy)  # uneven chip sizes
        if all((q - c).length > (s + sc) / 2 for _, c, sc in chosen):
            chosen.append((d, q, s))
    planes = []
    for d, q, _ in chosen:
        t = d + Vector([rng.uniform(-tilt, tilt) for _ in range(3)])  # tip in unit space
        nv = Vector((t.x / hx, t.y / hy, t.z / hz)).normalized()
        bulge = 1 + sum(amp * max(0.0, d.dot(c)) ** 2 for c, amp in lobes)
        planes.append((nv, max(0.02, nv.dot(q)) * rng.uniform(dmin + (0.94 - dmin) * lumpy, 1.0) * bulge))
    for nv, o in cuts:  # unit-sphere planes mapped into the scaled space
        g = Vector((nv[0] / half[0], nv[1] / half[1], nv[2] / half[2]))
        planes.append((g.normalized(), o / g.length))
    tmp = bmesh.new()
    dual = [tmp.verts.new(nv / o) for nv, o in planes]
    bmesh.ops.convex_hull(tmp, input=dual)
    prim = {}
    for f in tmp.faces:
        p1, p2, p3 = (v.co for v in f.verts[:3])
        m = (p2 - p1).cross(p3 - p1)
        e = m.dot(p1)
        if abs(e) > 1e-9:
            prim[f] = m / e
    out = bmesh.new()
    pv = {f: out.verts.new(p)
          for f, p in prim.items()}
    for v in tmp.verts:
        lf = [f for f in v.link_faces if f in pv]
        if len(lf) < 3:
            continue
        nv = v.co.normalized()
        u = nv.orthogonal().normalized()
        w = nv.cross(u)
        c = sum((prim[f] for f in lf), Vector()) / len(lf)
        lf.sort(key=lambda f: math.atan2((prim[f] - c).dot(w), (prim[f] - c).dot(u)))
        try:
            out.faces.new([pv[f] for f in lf])
        except ValueError:
            pass
    tmp.free()
    bmesh.ops.remove_doubles(out, verts=out.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(out, faces=out.faces[:])
    seam_faces = []
    if seam:
        res = bmesh.ops.bevel(out, geom=out.edges[:], offset=seam, segments=1, affect="EDGES",
                              profile=0.5)
        seam_faces = set(res["faces"])
    for f in out.faces:
        f.tag = f in seam_faces
    verts = _merge_tagged(a, out, fk._mat4(loc, rot))
    a._finish(verts, mat, tint, 0.0, ftv)
    if mat == "stone" and speck:
        speckle(a, verts, p=speck)
    upv = Vector(up).normalized() if up else None  # object space, like the normals
    for f in fk._faces_of(verts):
        if f.tag:
            f.material_index = a._mi(mat)
            f.tag = False
            for lp in f.loops:
                c = lp[a.tint_layer]
                lp[a.tint_layer] = (c[0] * 1.12, c[1] * 1.12, c[2] * 1.12, 1.0)
        elif upv is not None:
            f.normal_update()
            k = f.normal.dot(upv)
            if k > 0.3:  # upper facets catch the key light: a touch lighter
                g = 1 + 0.16 * min(1.0, (k - 0.3) / 0.5)
                for lp in f.loops:
                    c = lp[a.tint_layer]
                    lp[a.tint_layer] = (c[0] * g, c[1] * g, c[2] * g, 1.0)
    return verts


def _merge_tagged(a, tmp, matrix):
    vmap = {v: a.bm.verts.new(matrix @ v.co) for v in tmp.verts}
    for f in tmp.faces:
        nf = a.bm.faces.new([vmap[v] for v in f.verts])
        nf.tag = f.tag
    tmp.free()
    return list(vmap.values())


def tip_cuts(px, pz, a_in, a_out):
    """Two unit-space planes meeting at the point (px, 0, pz): one sloping toward
    -X at angle a_in from vertical, one toward +X at a_out."""
    out = []
    for ang, s in ((a_in, -1), (a_out, 1)):
        nv = Vector((s * math.cos(ang), 0, math.sin(ang)))
        out.append((nv, nv.dot(Vector((px, 0, pz)))))
    return out


def cord(a, pts, th, mat="rope", rseg=6, closed=True, normal=None, tint=None):
    """Round rope tube along points. Planar loops pass their plane normal for a
    twist-free frame; open cords use parallel transport."""
    bm = a.bm
    pts = [Vector(p) for p in pts]
    n = len(pts)
    rings, prev = [], None
    for i, p in enumerate(pts):
        if closed:
            t = pts[(i + 1) % n] - pts[i - 1]
        else:
            t = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]
        t.normalize()
        if normal is not None:
            nr = Vector(normal).cross(t).normalized()
        elif prev is None:
            ref = Z if abs(t.z) < 0.9 else Vector((1, 0, 0))
            nr = t.cross(ref).normalized()
        else:
            nr = (prev - t * prev.dot(t)).normalized()
        prev = nr
        bi = t.cross(nr)
        rings.append([bm.verts.new(p + th * (math.cos(TAU * j / rseg) * nr +
                                             math.sin(TAU * j / rseg) * bi)) for j in range(rseg)])
    segs = n if closed else n - 1
    twist = []
    for i in range(segs):
        r1, r2 = rings[i], rings[(i + 1) % n]
        for j in range(rseg):
            f = bm.faces.new((r1[j], r2[j], r2[(j + 1) % rseg], r1[(j + 1) % rseg]))
            if (i + j) % 3 == 0:
                twist.append(f)
    if not closed:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    verts = [v for r in rings for v in r]
    a._finish(verts, mat, tint if tint is not None else 1 + a.rng.uniform(-0.06, 0.06))
    for f in fk._faces_of(verts):
        f.smooth = True  # rope reads as round cord, not flat ribbon
    for f in twist:  # darker diagonal grooves read as twisted strands
        for lp in f.loops:
            c = lp[a.tint_layer]
            lp[a.tint_layer] = (c[0] * 0.72, c[1] * 0.72, c[2] * 0.72, 1.0)
    return verts


def _hull2d(pts):
    pts = sorted(set((round(x, 5), round(y, 5)) for x, y in pts))
    if len(pts) < 3:
        return pts

    def cross(o, p, q):
        return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def display_up(name):
    """The sheet's screen-up axis in the asset's object space (from its POSE)."""
    tilt, lean, spin = (math.radians(v) for v in POSE[name])
    M = Matrix.Rotation(spin, 3, "Z") @ Matrix.Rotation(lean, 3, "X") @ Matrix.Rotation(tilt, 3, "Y")
    return tuple(M.transposed() @ Z)


def bvh_of(a):
    return BVHTree.FromBMesh(a.bm)


def bvh_parts(*vert_lists):
    """BVH of just the faces of the given parts, so a lashing can hug one piece."""
    faces = set()
    for vl in vert_lists:
        faces.update(fk._faces_of([v for v in vl if v.is_valid]))
    verts = list({v for f in faces for v in f.verts})
    idx = {v: i for i, v in enumerate(verts)}
    return BVHTree.FromPolygons([v.co.copy() for v in verts], [[idx[v] for v in f.verts] for f in faces])


def lash(a, bvh, center, normal, th, mat="rope", rays=36, far=4.0, rseg=5, slack=0.0):
    """A rope loop pulled tight around everything the plane (center, normal)
    cuts through: rays find the surface, the loop follows its 2D convex hull."""
    c = Vector(center)
    nrm = Vector(normal).normalized()
    u = nrm.orthogonal().normalized()
    v = nrm.cross(u).normalized()
    pts2 = []
    for i in range(rays):
        ang = TAU * i / rays
        d = math.cos(ang) * u + math.sin(ang) * v
        hit = bvh.ray_cast(c + d * far, -d, far)
        if hit[0] is not None:
            q = hit[0] - c
            pts2.append((q.dot(u), q.dot(v)))
    hull = _hull2d(pts2)
    m = len(hull)
    out = []
    for k in range(m):
        p0, p1, p2 = hull[k - 1], hull[k], hull[(k + 1) % m]
        a1 = math.atan2(-(p1[0] - p0[0]), (p1[1] - p0[1]))
        a2 = math.atan2(-(p2[0] - p1[0]), (p2[1] - p1[1]))
        while a2 < a1:
            a2 += TAU
        steps = max(1, int((a2 - a1) / (math.pi / 3)) + 1)
        rr = th * 0.92 + slack
        for s in range(steps + 1):
            ang = a1 + (a2 - a1) * s / steps
            out.append((p1[0] + rr * math.cos(ang), p1[1] + rr * math.sin(ang)))
    clean = [out[0]]
    for p in out[1:]:
        if math.hypot(p[0] - clean[-1][0], p[1] - clean[-1][1]) > th * 1.3:
            clean.append(p)
    if len(clean) > 3 and math.hypot(clean[0][0] - clean[-1][0], clean[0][1] - clean[-1][1]) < th * 1.3:
        clean.pop()
    pts3 = [c + u * x + v * y for x, y in clean]
    return cord(a, pts3, th, mat, rseg, closed=True, normal=nrm)


def helix(a, center, R, turns, th, axis=(0, 0, 1), mat="rope", pitch=None, per_turn=10,
          rseg=5, phase=0.0, drift=None):
    """Spiral rope wrap of `turns` around an axis through center, radius R to
    the cord centre. drift(s) -> Vector offset bends it along a curved haft."""
    ax = Vector(axis).normalized()
    u = ax.orthogonal().normalized()
    v = ax.cross(u)
    pitch = pitch or th * 2.1
    n = max(3, int(turns * per_turn) + 1)
    length = turns * pitch
    pts = []
    for i in range(n):
        s = i / (n - 1)
        ang = phase + TAU * turns * s
        p = Vector(center) + ax * (s * length - length / 2) + R * (math.cos(ang) * u + math.sin(ang) * v)
        if drift:
            p += drift(s * length - length / 2)
        pts.append(p)
    return cord(a, pts, th, mat, rseg, closed=False)


def wraps(a, r, z, turns, th=0.07, mat="rope", x=0.0, y=0.0, axis=(0, 0, 1)):
    """Grip wrap: a spiral of round cord on a haft of radius r centred at height z."""
    return helix(a, (x, y, z), r + th * 0.9, turns, th, axis=axis, mat=mat,
                 phase=a.rng.uniform(0, TAU))


def bladed(a, left, right, ridge, thick, mat="iron", edge_mat=None, mid=0.22, mid_y=0.45,
           y_jit=0.0, ftv=0.05, chips=False):
    """Flat blade from an outline. left/right: (x, z) edge points from base to tip
    (the tip shared); ridge: (x, z) centre line; thick: ridge half-thickness per
    row. A middle row at `mid` (0 edge .. 1 ridge) with y = thick*mid_y becomes a
    narrow `edge_mat` bevel strip, or random knapping facets when chips=True."""
    bm = a.bm
    rng = a.rng
    n = len(ridge)
    tip = bm.verts.new((ridge[-1][0], 0, ridge[-1][1]))
    allv = [tip]
    edge_faces = []

    def row(pts, ys):
        vs = [bm.verts.new((pts[i][0], ys[i], pts[i][1])) for i in range(n - 1)] + [tip]
        allv.extend(vs[:-1])
        return vs

    def lerp(p, q, f):
        return (p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f)

    def strip(A, B, is_edge):
        for i in range(n - 1):
            if i == n - 2:
                f = bm.faces.new((A[i], A[i + 1], B[i]))
                fs = [f]
            elif chips and rng.random() < 0.5:
                fs = [bm.faces.new((A[i], A[i + 1], B[i + 1])), bm.faces.new((A[i], B[i + 1], B[i]))]
            elif chips:
                fs = [bm.faces.new((A[i], A[i + 1], B[i])), bm.faces.new((A[i + 1], B[i + 1], B[i]))]
            else:
                fs = [bm.faces.new((A[i], A[i + 1], B[i + 1], B[i]))]
            if is_edge:
                edge_faces.extend(fs)

    for outline in (left, right):
        e = row(outline, [0.0] * n)
        midp = [lerp(outline[i], ridge[i], mid) for i in range(n)]
        for sgn in (-1, 1):
            ys = [sgn * thick[i] * (mid_y + (rng.uniform(-y_jit, y_jit) if y_jit else 0)) for i in range(n)]
            m = row(midp, ys)
            rr = row(ridge, [sgn * thick[i] * (1 + (rng.uniform(-y_jit, y_jit) if y_jit else 0))
                             for i in range(n)])
            strip(e, m, True)
            strip(m, rr, False)
            if outline is left:
                if sgn < 0:
                    capf = (e[0], m[0], rr[0])
                else:
                    capb = (e[0], m[0], rr[0])
            else:
                if sgn < 0:
                    capf2 = (e[0], m[0], rr[0])
                else:
                    capb2 = (e[0], m[0], rr[0])
    # base cap (hidden in the haft or socket)
    ring = [capf[0], capf[1], capf[2], capf2[2], capf2[1], capf2[0], capb2[1], capb2[2], capb[2], capb[1]]
    try:
        bm.faces.new(ring)
    except ValueError:
        pass
    a._finish(allv, mat, None, 0.0, ftv)
    if edge_mat:
        for f in edge_faces:
            f.material_index = a._mi(edge_mat)
    if mat == "stone":
        speckle(a, allv, p=0.35)
    return allv




def bone_spike(a, base, direction, r, length, sides=5):
    d = Vector(direction).normalized()
    rot = d.to_track_quat("Z", "Y").to_euler()
    v = a.cyl(r, r * 0.72, length * 0.3, sides, loc=base, rot=rot, mat="bone")
    tip_base = Vector(base) + d * length * 0.3
    v += a.cyl(r * 0.72, 0.0, length * 0.7, sides, loc=tip_base, rot=rot, mat="bone")
    return v


def color_bevels(a, verts, mat):
    """Colour every face of a bevelled box whose normal is off-axis (the worn edges)."""
    for f in fk._faces_of(verts):
        f.normal_update()
        nn = f.normal
        if max(abs(nn.x), abs(nn.y), abs(nn.z)) < 0.95:
            f.material_index = a._mi(mat)


# Blender-side shade grading (multiplies the Tint attribute) so stone reads as
# the reference's blue-grey, iron near-black and rope a mellow tan under the
# bright studio key. Palette keys are unchanged.
GRADE = {"stone": 0.84, "stone_dark": 0.8, "stone_light": 0.72, "rope": 0.8, "rope_dark": 0.9,
         "wood": 0.8, "wood_dark": 0.88, "wood_light": 0.76, "wood_end": 0.72, "iron": 0.74,
         "iron_dark": 0.66, "iron_edge": 0.95}


def grade(a):
    for f in a.bm.faces:
        g = GRADE.get(a.mats[f.material_index], 1.0)
        if g != 1.0:
            for lp in f.loops:
                c = lp[a.tint_layer]
                lp[a.tint_layer] = (c[0] * g, c[1] * g, c[2] * g, 1.0)


def done(a):
    grade(a)
    bmesh.ops.recalc_face_normals(a.bm, faces=a.bm.faces[:])
    return a.finish()




# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------




def grip_cross(a, z, tilt=0.55, th=0.066, mat="rope"):
    """One diagonal crossing turn over a grip wrap."""
    return lash(a, bvh_of(a), (0, 0, z), (math.sin(tilt), 0, math.cos(tilt)), th, mat=mat)


def axe_head_lashing(a, bvh_block, bvh_all, block_c, junction, th, rings=(-0.28, -0.12, 0.04),
                     tilts=(-0.2, 0.0, 0.15, 0.3), bands=1, bind=()):
    """Reference hafted-axe binding: a bundle of tilted turns hugging the split
    haft end, `bind` turns (dz offsets from the junction) that take in the
    stone's shoulder too, and `bands` turns round the block foot."""
    for k, dz in enumerate(rings):
        tl = tilts[k % len(tilts)]
        lash(a, bvh_block, (block_c[0], 0, block_c[2] + dz), (math.sin(tl), 0, math.cos(tl)), th,
             mat="rope_dark" if k == 1 else "rope")
    for k, dz in enumerate(bind):
        tl = (0.18, -0.06, 0.1, -0.14)[k % 4]
        lash(a, bvh_all, Vector(junction) + Vector((0, 0, dz)), (math.sin(tl), 0, math.cos(tl)), th,
             mat="rope_dark" if k % 2 else "rope")
    for k in range(bands):
        c = Vector(junction) + Vector((0, 0, 0.13 * k))
        lash(a, bvh_all, c, (math.sin(0.32), 0, math.cos(0.32)), th, mat="rope_dark" if k else "rope")


def split_end(a, z0, z1, r, phase=0.3):
    """Chunky split haft end: a squat 6-sided block plus an offset split-off piece."""
    hewn(a, [(z0, r), (z1, r * 0.95)], sides=6, jit=0.1, chamfer=0.3, end0=False, phase=phase,
         groove=0, streak=0.4)
    a.box((0.3, r * 1.3, (z1 - z0) * 0.72), loc=(r * 0.62, -0.03, (z0 + z1) / 2 + 0.06),
          rot=(0, 0.22, 0.12), mat="wood", bevel=0.04)


# two unit-space planes that thin a stone toward -X into a chopping edge
WEDGE = [((-0.42, 0.91, 0), 0.5), ((-0.42, -0.91, 0), 0.5)]


def stone_axe_basic():
    a = fk.Asset("StoneAxeBasic", "Tools")
    L, r = 3.2, 0.28
    hewn(a, [(0, r * 1.2), (0.3, r * 1.05), (1.3, r), (2.3, r * 0.97), (2.62, r * 0.98)], end1=False)
    split_end(a, 2.55, L, 0.4)
    bvh_block = bvh_of(a)
    # an elongated chipped wedge, longer than it is tall, edge toward -X, its top
    # shoulder tucked under the split haft end
    cell_stone(a, (0.68, 0.3, 0.58), loc=(-0.78, 0, 2.24), rot=(0, 0.12, 0), n=72, lumpy=1.0,
               up=display_up("StoneAxeBasic"), seam=0.0)
    bvh_all = bvh_of(a)
    th = 0.084
    for k, (dz, tl) in enumerate(((-0.3, -0.12), (-0.16, 0.04), (-0.02, -0.06), (0.12, 0.1))):
        lash(a, bvh_block, (0, 0, 2.95 + dz), (math.sin(tl), 0, math.cos(tl)), th,
             mat="rope_dark" if k == 1 else "rope")
    # crossing turns over the stone's shoulder that bind it to the haft
    for k, (c, tl) in enumerate((((-0.24, 0, 2.72), 0.8), ((-0.14, 0, 2.6), 0.62))):
        lash(a, bvh_all, c, (math.sin(tl), 0, math.cos(tl)), th, mat="rope" if k else "rope_dark")
    wraps(a, r * 1.02, 0.78, 3, th=0.068)
    return done(a)


def stone_axe_broad():
    a = fk.Asset("StoneAxeBroadHead", "Tools")
    L, r = 3.4, 0.29
    hewn(a, [(0, r * 1.2), (0.3, r * 1.05), (1.4, r), (2.5, r * 0.97), (2.78, r * 0.98)], end1=False)
    split_end(a, 2.72, L, 0.42, phase=1.0)
    bvh_block = bvh_of(a)
    up = display_up("StoneAxeBroadHead")
    # a big lumpy two-lobed boulder (~2.2x the haft width)
    cell_stone(a, (0.76, 0.4, 0.74), loc=(-0.88, 0, 2.36), rot=(0, 0.2, 0), n=72, lumpy=1.0,
               up=up, seam=0.0)
    cell_stone(a, (0.46, 0.34, 0.4), loc=(-0.7, 0.03, 2.96), rot=(0.3, -0.4, 0.5), n=26,
               lumpy=1.0, up=up, seam=0.0)
    bvh_all = bvh_of(a)
    th = 0.084
    for k, (dz, tl) in enumerate(((-0.26, -0.1), (-0.08, 0.0), (0.1, 0.1))):
        lash(a, bvh_block, (0, 0, 3.06 + dz), (math.sin(tl), 0, math.cos(tl)), th,
             mat="rope_dark" if k == 1 else "rope")
    for k, (c, tl) in enumerate((((-0.14, 0, 2.92), 0.82), ((-0.06, 0, 2.8), 0.64))):
        lash(a, bvh_all, c, (math.sin(tl), 0, math.cos(tl)), th, mat="rope" if k else "rope_dark")
    wraps(a, r * 0.99, 2.42, 2, th=0.07, mat="rope_dark")
    wraps(a, r * 1.02, 0.82, 3, th=0.07)
    return done(a)


def iron_axe():
    a = fk.Asset("IronAxe", "Tools")
    L, r = 3.6, 0.27
    hewn(a, [(0, r * 1.25), (0.3, r * 1.05), (1.2, r), (2.4, r * 0.95), (L, r * 0.95)])
    zt = L - 0.14
    eye = a.box((0.64, 0.52, 0.62), loc=(0.0, 0, zt - 0.3), mat="iron_dark", bevel=0.06)
    color_bevels(a, eye, "iron")
    cap = a.box((0.46, 0.44, 0.16), loc=(-0.1, 0, zt + 0.06), mat="iron_dark", bevel=0.04)
    color_bevels(a, cap, "iron")
    poll = a.box((0.2, 0.4, 0.44), loc=(0.4, 0, zt - 0.3), mat="iron_dark", bevel=0.05)
    color_bevels(a, poll, "iron")
    # convex bearded blade toward -X, thinning to a broad bright edge
    x0, x1 = -0.3, -1.38
    zb0, zt0, zb1, zt1 = zt - 0.58, zt - 0.02, zt - 1.58, zt + 0.16

    def ring(u, t, nv=6):
        zb = zb0 + (zb1 - zb0) * u ** 1.7
        ztop = zt0 + (zt1 - zt0) * u ** 1.6
        front = []
        for k in range(nv):
            v = k / (nv - 1)
            z = zb + (ztop - zb) * v
            xx = x0 + (x1 - x0) * u - 0.3 * math.sin(math.pi * v) ** 0.8 * u ** 2.5
            front.append((xx, -t, z))
        back = [(p[0], t, p[2]) for p in reversed(front)]
        return front + back

    us = [0.0, 0.35, 0.62, 0.8]
    ts = [0.12, 0.1, 0.078, 0.058]
    loft(a, [ring(u, t) for u, t in zip(us, ts)], "iron_dark", True, False, ftv=0.08)
    loft(a, [ring(0.8, 0.058), ring(1.0, 0.012)], "iron_edge", False, True, ftv=0.04)
    wraps(a, r * 0.95, zt - 0.78, 2, th=0.068)
    wraps(a, r * 0.95, zt - 1.08, 2, th=0.068, mat="rope_dark")
    wraps(a, r * 1.02, 0.85, 3, th=0.068)
    grip_cross(a, 0.85)
    return done(a)


def _pick_z(zc, u, rise, droop):
    return zc + rise * math.sin(math.pi * u * 0.85) - droop * u ** 2.3


def stone_pick_double():
    a = fk.Asset("StonePickaxeDouble", "Tools")
    L, r = 2.75, 0.3
    zc = 1.88  # a big binding block (~1 stud) on a short, stout haft, as on the sheet
    hewn(a, [(0, r * 1.3), (0.3, r * 1.18), (0.9, r * 1.12), (zc - 0.3, r * 1.08)], end1=False)
    core = a.box((0.92, 0.6, 0.98), loc=(0, 0, zc), mat="wood_dark", bevel=0.1, jitter=0.02)
    hewn(a, [(zc + 0.4, r * 1.1), (L, r * 1.05)], sides=6, jit=0.06, end0=False, chamfer=0.35,
         groove=0)  # knob above the head
    rise, droop, reach, x0 = 0.28, 0.82, 1.68, 0.36
    horns = []
    for s in (-1, 1):
        n = 8
        pts, rads = [], []
        for i in range(n):
            u = i / (n - 1)
            pts.append((s * (x0 + reach * u), 0, _pick_z(zc, u, rise, droop)))
            rads.append((0.46 * (1 - u) ** 0.7, 0.25 * (1 - u) ** 0.5))
        v = sweep(a, pts, rads, sides=6, mat="stone", phase=0.2, jit=0.035, ftv=0.16)
        speckle(a, v, p=0.3)
        horns.append(v)
    bvh = bvh_of(a)
    th = 0.08
    # a big X over the block's face, rings round each horn root, bands top and bottom
    for sg, m in ((1, "rope"), (-1, "rope_dark")):
        lash(a, bvh_parts(core), (0, 0, zc), (sg * math.sin(0.8), 0, math.cos(0.8)), th, mat=m)
    for s in (-1, 1):
        for k, dx in enumerate((0.55, 0.68)):
            u = (dx - x0) / reach
            lash(a, bvh, (s * dx, 0, _pick_z(zc, u, rise, droop)), (1, 0, 0), th,
                 mat="rope" if k == 0 else "rope_dark")
    for k, dz in enumerate((-0.4, 0.38)):
        lash(a, bvh_parts(core), (0, 0, zc + dz), (0, 0, 1), th, mat="rope_dark" if k else "rope")
    wraps(a, r * 1.1, 0.5, 2, th=0.072)
    return done(a)


def iron_pickaxe():
    a = fk.Asset("IronPickaxe", "Tools")
    L, r = 2.95, 0.29
    hewn(a, [(0, r * 1.15), (0.3, r * 1.04), (1.2, r), (2.2, r * 0.97), (L, r)])
    zc = L - 0.66
    col = a.box((0.7, 0.58, 0.72), loc=(0, 0, zc), mat="iron_dark", bevel=0.06)
    color_bevels(a, col, "iron")
    a.rivet((0, -0.3, zc), normal_rot=(math.pi / 2, 0, 0), r=0.1, mat="iron_edge")
    # flattened hex section: narrow bright bevel strips on both edges of each arm
    sec = [(1, 0), (0.8, 1), (-0.8, 1), (-1, 0), (-0.8, -1), (0.8, -1)]

    def fm(i, j):
        return "iron_edge" if j in (0, 2, 3, 5) else None

    # left: shorter, rising pick; right: long pick curving down
    for s, length, rise, droop, w in ((-1, 1.42, 0.26, 0.0, 0.3), (1, 1.9, 0.0, 1.05, 0.35)):
        n = 8
        pts, rads = [], []
        for i in range(n):
            u = i / (n - 1)
            pts.append((s * (0.34 + length * u), 0, zc + rise * u ** 1.5 - droop * u ** 2.2))
            rads.append((w * (1 - u) ** 0.55, 0.17 * (1 - u) ** 0.5))
        sweep(a, pts, rads, mat="iron_dark", section=sec, face_mat=fm, ftv=0.07)
    bvh = bvh_of(a)
    for s in (-1, 1):
        for k, dx in enumerate((0.43, 0.53)):
            lash(a, bvh, (s * dx, 0, zc), (1, 0, 0), 0.07, mat="rope" if k == 0 else "rope_dark")
    wraps(a, r * 1.0, 0.62, 2, th=0.07)
    return done(a)


def spear_shaft(a, top, r):
    hewn(a, [(0, r * 1.06), (2.0, r), (4.5, r * 0.96), (top, r * 0.93)], sides=7, end1=False,
         chamfer=0.4)


def wooden_spear():
    a = fk.Asset("WoodenSpear", "Weapons")
    L, r = 7.0, 0.23
    spear_shaft(a, 5.11, r)
    # carved point: flattened, twisted hexagon rings with knife facets
    prof = [(5.08, r * 0.95), (5.25, r * 1.4), (5.5, r * 1.5), (6.1, r * 1.0),
            (6.65, r * 0.42), (L, 0.0)]
    rings = []
    for k, (z, rr) in enumerate(prof):
        if rr == 0:
            rings.append([(0, 0, z)])
            continue
        tw = 0.07 * k
        sec = [(1, 0), (0.5, 0.7), (-0.5, 0.7), (-1, 0), (-0.5, -0.7), (0.5, -0.7)]
        ring = []
        for cx, cy in sec:
            j = 1 + a.rng.uniform(-0.06, 0.06)
            x, y = cx * rr * j, cy * rr * j
            ring.append((x * math.cos(tw) - y * math.sin(tw), x * math.sin(tw) + y * math.cos(tw), z))
        rings.append(ring)
    loft(a, rings, "wood_light", False, False, ftv=0.14,
         face_mat=lambda i, j: "wood" if (i + j) % 4 == 0 else None)
    wraps(a, r * 0.95, 4.86, 3, th=0.062)
    wraps(a, r, 2.1, 3, th=0.064)
    return done(a)


def stone_spear():
    a = fk.Asset("StoneSpear", "Weapons")
    L, r = 7.0, 0.22
    spear_shaft(a, 5.62, r)
    hl = 1.0
    cell_stone(a, (0.4, 0.13, hl), loc=(0, 0, L - hl), n=30, tilt=0.3,
               cuts=tip_cuts(0, 1.0, 0.95, 0.95))
    bvh = bvh_of(a)
    th = 0.07
    for k, z in enumerate((5.18, 5.32, 5.46)):
        lash(a, bvh, (0, 0, z), (0.12 * (k - 1), 0, 1), th, mat="rope_dark" if k == 1 else "rope")
    for s, m in ((1, "rope"), (-1, "rope_dark")):
        lash(a, bvh, (0, 0, 5.4), (s * math.sin(0.6), 0, math.cos(0.6)), th, mat=m)
    wraps(a, r * 0.95, 4.86, 2, th=0.066)
    wraps(a, r * 1.02, 0.9, 4, th=0.062)
    return done(a)


def iron_spear():
    a = fk.Asset("IronSpear", "Weapons")
    L, r = 7.2, 0.21
    spear_shaft(a, 5.0, r)
    a.cyl(r * 1.12, r * 0.82, 0.5, 7, loc=(0, 0, 4.85), mat="iron_dark")  # socket
    a.cyl(r * 0.82, r * 0.62, 0.14, 7, loc=(0, 0, 5.35), mat="iron")
    zb = 5.45
    left = [(-0.12, zb), (-0.45, zb - 0.1), (-0.4, zb + 0.32), (-0.22, zb + 0.95), (0, L)]
    right = [(-x, z) for x, z in left]
    ridge = [(0, zb), (0, zb + 0.05), (0, zb + 0.32), (0, zb + 0.95), (0, L)]
    thick = [0.12, 0.11, 0.1, 0.065, 0.0]
    bladed(a, left, right, ridge, thick, mat="iron_dark", edge_mat="iron_edge", mid=0.22, mid_y=0.3,
           ftv=0.08)
    wraps(a, r * 0.98, 4.68, 2, th=0.064)
    wraps(a, r * 0.98, 4.36, 3, th=0.064, mat="rope_dark")
    wraps(a, r, 1.0, 3, th=0.064)
    return done(a)


def stone_knife():
    a = fk.Asset("StoneKnife", "Weapons")
    L = 1.8
    zb = 0.78  # blade base: the blade is ~55% of the length

    def bend(z):
        return 0.05 * math.sin(math.pi * z / zb)

    cell_stone(a, (0.19, 0.18, 0.14), loc=(0.0, 0, 0.12), n=20, tilt=0.12)  # pommel
    hewn(a, [(0.1, 0.13), (0.4, 0.145), (0.65, 0.14), (zb + 0.08, 0.13)], sides=7, end0=False,
         end1=False, bend=bend)
    hl = 0.6
    cell_stone(a, (0.28, 0.14, hl), loc=(0.0, 0, L - hl), n=48, dmin=0.92, ftv=0.18, tilt=0.38, seam=0.005,
               cuts=[((-0.505, 0, 0.864), 0.67)])
    bvh = bvh_of(a)
    th = 0.044
    for k, z in enumerate((0.78, 0.85, 0.92, 0.99)):
        lash(a, bvh, (0, 0, z), (0.1 * (k - 1.5), 0, 1), th, mat="rope_dark" if k == 2 else "rope")
    wraps(a, 0.145, 0.32, 2, th=0.048, mat="rope", x=bend(0.32))
    return done(a)


def iron_short_sword():
    a = fk.Asset("IronShortSword", "Weapons")
    L = 3.6
    hewn(a, [(0, 0.19), (0.26, 0.19)], sides=6, mat="iron_dark", end_mat="iron", groove=0,
         chamfer=0.35, jit=0.02)  # pommel
    zg = 1.25
    hewn(a, [(0.24, 0.165), (0.7, 0.172), (zg, 0.165)], sides=7, end0=False, end1=False)
    guard = a.box((0.95, 0.44, 0.3), loc=(0, 0, zg + 0.12), mat="iron_dark", bevel=0.08)
    color_bevels(a, guard, "iron_edge")
    # blade: ridge with bright bevels either side, angled point
    zs = [zg + 0.25, 2.2, 3.0, 3.25, L]
    ws = [0.33, 0.34, 0.32, 0.22, 0.0]
    left = [(-w, z) for w, z in zip(ws, zs)]
    right = [(w, z) for w, z in zip(ws, zs)]
    ridge = [(0, z) for z in zs]
    thick = [0.1, 0.1, 0.095, 0.075, 0.0]
    bladed(a, left, right, ridge, thick, mat="iron_dark", edge_mat="iron_edge", mid=0.2, mid_y=0.4,
           ftv=0.08)
    wraps(a, 0.165, zg - 0.22, 3, th=0.048)
    wraps(a, 0.168, 0.34, 1, th=0.05, mat="rope_dark")
    return done(a)


def stone_war_club():
    a = fk.Asset("StoneWarClub", "Weapons")
    L, r = 3.4, 0.25
    hewn(a, [(0, r * 1.3), (0.3, r * 1.1), (1.2, r), (1.9, r * 1.06), (2.6, r * 1.18)], sides=8,
         end1=False)
    # three chipped lumps gripping the haft top, the biggest in front
    up = display_up("StoneWarClub")
    cell_stone(a, (0.58, 0.4, 0.52), loc=(0.08, 0.06, L - 0.54), rot=(0.4, 0.3, 0.2), n=44,
               tint=0.84, lumpy=1.0, up=up, seam=0.0)
    cell_stone(a, (0.46, 0.38, 0.5), loc=(0.5, 0.08, 2.54), rot=(-0.3, 0.5, 0.9), n=34,
               tint=0.8, lumpy=1.0, up=up, seam=0.0)
    front = (-0.44, -0.12, 2.38)
    fv = cell_stone(a, (0.66, 0.44, 0.56), loc=front, rot=(0.2, -0.35, -0.4), n=54, tint=0.86,
                    lumpy=1.0, up=up, seam=0.0)
    bvh_all = bvh_of(a)
    th = 0.088
    # an X hugging the big front lump, then a band round the whole cluster
    for s, m in ((1, "rope"), (-1, "rope_dark")):
        lash(a, bvh_parts(fv), front, (s * math.sin(0.75), 0, math.cos(0.75)), th, mat=m)
    lash(a, bvh_all, (0, 0, 2.8), (0, 0.1, 1), th)
    wraps(a, r * 1.1, 2.05, 3, th=0.07)
    wraps(a, r * 1.28, 0.5, 3, th=0.07)
    return done(a)


def timber_club_bone():
    a = fk.Asset("TimberClubBone", "Weapons")
    L = 3.4
    prof = [(0, 0.23), (0.3, 0.22), (0.9, 0.24), (1.8, 0.33), (2.6, 0.48), (2.95, 0.57), (3.2, 0.58),
            (L, 0.46)]
    hewn(a, prof, sides=7, jit=0.16, wob=0.08, chamfer=0.3, groove=0.2, streak=0.35)
    # chunky split-log crown
    a.box((0.5, 0.56, 0.28), loc=(-0.1, 0.02, L - 0.02), rot=(0.1, 0.2, 0.3), mat="wood", bevel=0.06)
    a.box((0.34, 0.44, 0.22), loc=(0.26, -0.04, L - 0.06), rot=(-0.1, -0.3, 0.6), mat="wood_dark", bevel=0.05)

    def rad(z):
        for (z0, r0), (z1, r1) in zip(prof, prof[1:]):
            if z0 <= z <= z1:
                return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
        return prof[-1][1]

    bvh = bvh_of(a)
    th = 0.075
    for s, m in ((1, "rope"), (-1, "rope_dark")):
        lash(a, bvh, (0, 0, 2.75), (s * math.sin(0.45), 0, math.cos(0.45)), th, mat=m)
    for z, phis in ((2.5, (-160, -40, 80)), (2.98, (-100, 20, 140))):
        for p in phis:
            phi = math.radians(p)
            d = Vector((math.cos(phi), math.sin(phi), 0.3))
            rr = rad(z) * 0.75
            bone_spike(a, (math.cos(phi) * rr, math.sin(phi) * rr, z), d, 0.23, 0.66)
    wraps(a, 0.235, 0.42, 3, th=0.068)
    return done(a)


def bow_curve(L, depth, recurve=0.0, n=17, flick=0.85):
    pts = []
    for i in range(n):
        s = -1 + 2 * i / (n - 1)
        x = -depth * (1 - s * s) ** 0.85
        z = (s + 1) / 2 * L
        if recurve:
            e = max(0.0, (abs(s) - flick) / (1 - flick))
            x += recurve * e ** 1.5
            z -= recurve * 0.5 * e ** 2 * math.copysign(1, s)
        pts.append((x, 0, z))
    return pts


def _tangent(pts, k):
    return Vector(pts[min(k + 1, len(pts) - 1)]) - Vector(pts[max(k - 1, 0)])


def wooden_bow_simple():
    a = fk.Asset("WoodenBowSimple", "Weapons")
    L = 4.4
    pts = bow_curve(L, 1.3)
    n = len(pts)
    rads = []
    for i in range(n):
        s = abs(-1 + 2 * i / (n - 1))
        k = (1 - s) ** 0.8
        rads.append((0.15 + 0.15 * k, 0.17 + 0.12 * k))
    sweep(a, pts, rads, sides=6, mat="wood", phase=0.4, jit=0.014, ftv=0.1,
          face_mat=lambda i, j: "wood_dark" if j == 4 or (i + j) % 7 == 0 else None)
    mid = n // 2
    for k in (mid - 2, mid + 2):
        R = rads[k][1] + 0.055
        helix(a, pts[k], R, 2, 0.06, axis=_tangent(pts, k), phase=0.3)
    for k in (1, n - 2):  # wrapped cord tip knots
        R = rads[k][1] + 0.05
        helix(a, pts[k], R, 2.5, 0.055, axis=_tangent(pts, k), mat="rope_dark", per_turn=8)
    a.tube_loop([pts[1], pts[-2]], 0.03, mat="cloth_cream", rseg=4, closed=False)
    return done(a)


def wooden_bow_laminated():
    a = fk.Asset("WoodenBowLaminated", "Weapons")
    L = 5.17
    pts = bow_curve(L, 0.98, recurve=0.42, n=23, flick=0.8)
    n = len(pts)
    rads = []
    for i in range(n):
        s = abs(-1 + 2 * i / (n - 1))
        k = (1 - s) ** 0.8
        rads.append((0.18 + 0.13 * k, 0.19 + 0.1 * k))

    def fm(i, j):  # two-tone laminate strips
        return "wood_light" if j == 1 else ("wood_dark" if j == 4 else None)

    sweep(a, pts, rads, sides=6, mat="wood", phase=0.5, jit=0.01, ftv=0.08, face_mat=fm)
    mid = n // 2
    grip = [pts[mid - 1], pts[mid], pts[mid + 1]]
    sweep(a, grip, [(0.34, 0.32)] * 3, sides=8, mat="charcoal", phase=0.2, ftv=0.06)
    for k in (mid - 1, mid + 1):  # pale rims either side of the leather grip
        p = Vector(pts[k])
        sweep(a, [p, p + (p - Vector(pts[mid])).normalized() * 0.1],
              [(0.36, 0.34)] * 2, sides=8, mat="wood_light", phase=0.2)
    for k in (3, 6, n - 7, n - 4):  # flat bound bands along the limbs
        p, t = Vector(pts[k]), _tangent(pts, k).normalized()
        rw, rt = rads[k]
        sweep(a, [p - t * 0.07, p + t * 0.07], [(rw + 0.04, rt + 0.04)] * 2, sides=8, mat="rope",
              phase=0.2, ftv=0.08)
    for k in (2, n - 3):
        R = rads[k][1] + 0.045
        helix(a, pts[k], R, 2.5, 0.05, axis=_tangent(pts, k), mat="rope_dark", per_turn=8)
    a.tube_loop([pts[2], pts[-3]], 0.028, mat="cloth_cream", rseg=4, closed=False)
    return done(a)


def stone_arrow():
    a = fk.Asset("StoneArrow", "Weapons")
    L, r = 3.0, 0.066
    a.cyl(r * 1.35, r * 1.2, 0.1, 6, loc=(0, 0, 0), mat="wood_light")  # nock
    hewn(a, [(0.1, r), (1.5, r), (2.6, r)], sides=6, end0=False, end1=False, jit=0.04, groove=0)
    hl = 0.32
    cell_stone(a, (0.19, 0.075, hl), loc=(0, 0, L - hl), n=18, seam=0.0,
               cuts=tip_cuts(0, 1.0, 0.9, 0.9))
    bvh = bvh_of(a)
    th = 0.036
    for k, z in enumerate((2.42, 2.5)):
        lash(a, bvh, (0, 0, z), (0.15 * (2 * k - 1), 0, 1), th, mat="rope_dark" if k else "rope")
    helix(a, (0, 0, 2.3), r + th * 0.9, 2, th, per_turn=8)
    # three long cream feathers with slanted ends, banded in two creams
    z0, fl, h = 0.14, 0.8, 0.22
    inner = ((r * 0.6, z0 + 0.04), (r * 0.6, z0 + fl))
    outer = ((h, z0 - 0.06), (h, z0 + fl - 0.2))

    def lerp(p, q, t):
        return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)

    for k in range(3):
        phi = TAU * k / 3
        for b in range(3):
            t0, t1 = b / 3, (b + 1) / 3
            quad = [lerp(*inner, t0), lerp(*outer, t0), lerp(*outer, t1), lerp(*inner, t1)]
            a.poly_prism(quad, 0.022, loc=(0, 0, 0), rot=(math.pi / 2, 0, phi),
                         mat="bone" if b % 2 else "cloth_cream")
    wraps(a, r, z0 + fl + 0.05, 2, th=0.03)
    return done(a)


def blacksmith_hammer():
    a = fk.Asset("BlacksmithHammer", "Tools")
    L, r = 2.9, 0.26
    hewn(a, [(0, r * 1.35), (0.25, r * 1.12), (0.9, r), (1.8, r * 0.96), (L - 0.02, r * 0.96)],
         sides=7, end1=False)
    zc = L - 0.48
    head = a.box((1.24, 0.86, 0.9), loc=(-0.04, 0, zc), mat="iron_dark", bevel=0.09, jitter=0.012)
    color_bevels(a, head, "iron")
    # the haft end shows through the eye on top, split by a wedge
    a.box((0.5, 0.44, 0.2), loc=(0, 0, zc + 0.5), mat="wood", bevel=0.035)
    a.box((0.06, 0.46, 0.21), loc=(0.04, 0, zc + 0.505), mat="wood_dark")
    wraps(a, r * 0.97, zc - 0.62, 3, th=0.066)
    wraps(a, r * 1.06, 0.5, 3, th=0.068)
    return done(a)


BUILDERS = [stone_axe_basic, stone_axe_broad, iron_axe, stone_pick_double, iron_pickaxe,
            wooden_spear, stone_spear, iron_spear, stone_knife, iron_short_sword,
            stone_war_club, timber_club_bone, wooden_bow_simple, wooden_bow_laminated,
            stone_arrow, blacksmith_hammer]

# Display pose per asset: (tilt about Y in degrees: negative swings the head left,
# lean about X, spin about Z). Read off the reference sheet.
POSE = {
    "StoneAxeBasic": (-60, -20, 0),
    "StoneAxeBroadHead": (-58, -20, 0),
    "IronAxe": (-60, -20, 0),
    "StonePickaxeDouble": (10, -22, 0),
    "IronPickaxe": (14, -30, 0),
    "WoodenSpear": (-61, 22, 0),
    "StoneSpear": (-61, 22, 0),
    "IronSpear": (-61, 22, 0),
    "StoneKnife": (-62, -20, 0),
    "IronShortSword": (-64, -20, 0),
    "StoneWarClub": (-65, -20, 0),
    "TimberClubBone": (-62, -20, 0),
    "WoodenBowSimple": (-69, -20, 0),
    "WoodenBowLaminated": (-71, -20, 0),
    "StoneArrow": (-68, -20, 0),
    "BlacksmithHammer": (-64, -20, 25),
}


# ---------------------------------------------------------------------------
# Sheet render with per-asset display poses
# ---------------------------------------------------------------------------


def frame_tight(obj, azimuth=0.0, elevation=22.0, margin=1.12):
    scene = bpy.context.scene
    cam = bpy.data.objects["FB_Cam"]
    mw = obj.matrix_world
    pts = [mw @ v.co for v in obj.data.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    centre = (lo + hi) / 2
    az, el = math.radians(azimuth), math.radians(elevation)
    direction = Vector((math.sin(az), -math.cos(az), math.tan(el))).normalized()
    rot = (-direction).to_track_quat("-Z", "Y")
    R = rot.to_matrix()
    right, up = R.col[0], R.col[1]
    xs = [(p - centre).dot(right) for p in pts]
    ys = [(p - centre).dot(up) for p in pts]
    centre = centre + right * (max(xs) + min(xs)) / 2 + up * (max(ys) + min(ys)) / 2
    fov = cam.data.angle
    rx, ry = scene.render.resolution_x, scene.render.resolution_y
    tan_h = math.tan(fov / 2)
    tan_v = tan_h * ry / rx
    dist = 0.0
    for p in pts:
        d = p - centre
        xc, yc, zc = d.dot(right), d.dot(up), d.dot(direction)
        dist = max(dist, zc + abs(xc) * margin / tan_h, zc + abs(yc) * margin / tan_v)
    cam.location = centre + direction * dist
    cam.rotation_euler = rot.to_euler()
    bpy.data.objects["FB_Ground"].location = (centre.x, centre.y, lo.z - 0.12)


def render_sheet_posed(objs, path, cols=4, cell=(384, 288), elevation=16.0, samples=32):
    scene = bpy.context.scene
    fk._studio(scene)
    scene.render.resolution_x, scene.render.resolution_y = cell
    scene.render.resolution_percentage = 100
    try:
        scene.eevee.taa_render_samples = samples
    except AttributeError:
        pass
    for o in objs:
        o.hide_render = True
    base, _ = os.path.splitext(path)
    cell_paths = []
    for i, o in enumerate(objs):
        tilt, lean, spin = (math.radians(v) for v in POSE[o.name])
        M = Matrix.Rotation(spin, 3, "Z") @ Matrix.Rotation(lean, 3, "X") @ Matrix.Rotation(tilt, 3, "Y")
        o.rotation_euler = M.to_euler("XYZ")
        o.hide_render = False
        bpy.context.view_layer.update()
        frame_tight(o, elevation=elevation)
        p = f"{base}_cells/{i + 1:02d}_{o.name}.png"
        os.makedirs(os.path.dirname(p), exist_ok=True)
        scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        cell_paths.append(p)
        o.hide_render = True
        o.rotation_euler = (0, 0, 0)
    for o in objs:
        o.hide_render = False
    rows = math.ceil(len(objs) / cols)
    w, h = cell
    sheet = np.ones((rows * h, cols * w, 4), dtype=np.float32)
    for i, p in enumerate(cell_paths):
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
    return path


def main():
    fk.reset_file()
    objs = [b() for b in BUILDERS]
    fk.layout_row(objs, spacing=2.0)
    for o in objs:
        o.rotation_euler = (0, 0, 0)
    fk.save(BLEND)
    for o in objs:
        d = o.dimensions
        print(f"ASSET {o.name:20s} tris={o['tris']:5d} dims={d.x:.3f} x {d.y:.3f} x {d.z:.3f}")
    render_sheet_posed(objs, SHEET)
    print("SHEET", SHEET)


main()
