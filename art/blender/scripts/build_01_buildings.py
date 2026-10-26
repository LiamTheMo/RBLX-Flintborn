"""Build sheet 01 Buildings: VaultHall, AncestralForge, DeployGate,
ThatchMarketStall, HideMarketStall, PrimitiveShelter.

Run headless:
    "D:/Steam/steamapps/common/Blender/blender.exe" --background --factory-startup \
        --python art/blender/scripts/build_01_buildings.py

Env: FB_NORENDER=1 skips the sheet render, FB_STATS=1 prints tris per material.
"""

import math
import os
import sys

sys.path.insert(0, "D:/Projects/Roblox/RBLX-Flintborn/art/blender/lib")

import bmesh  # noqa: E402
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Euler, Matrix, Vector  # noqa: E402

import flintkit as fk  # noqa: E402
import vfx  # noqa: E402

ROOT = "D:/Projects/Roblox/RBLX-Flintborn/art/blender"
PI = math.pi
DOWN = Vector((0, 0, -1))


# ---------------------------------------------------------------------------
# Local helpers (all take an fk.Asset)
# ---------------------------------------------------------------------------


def xf(a, verts, M):
    bmesh.ops.transform(a.bm, matrix=M, verts=verts)
    return verts


def frame_m(P, U, D, N, shear=0.0):
    D2 = D + N * shear
    return Matrix(((U.x, D2.x, N.x, P.x), (U.y, D2.y, N.y, P.y), (U.z, D2.z, N.z, P.z), (0, 0, 0, 1)))


def align_m(p, d):
    """Local +Z -> direction d, local +Y kept as close to world up as possible."""
    d = Vector(d)
    q = d.to_track_quat("Z", "Y")
    return Matrix.Translation(Vector(p)) @ q.to_matrix().to_4x4()


def pick(a, choices):
    r = a.rng.random()
    acc = 0.0
    for m, w in choices:
        acc += w
        if r <= acc:
            return m
    return choices[-1][0]


STONE_MIX = (("stone", 0.62), ("stone_light", 0.30), ("stone_dark", 0.08))
WOOD_MIX = (("wood", 0.72), ("wood_dark", 0.28))
INSIDE = (("wood_light", 0.5), ("wood", 0.5))  # sun-warmed interior planks

_AXES = {
    "y": Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1))),  # face in XZ, depth Y
    "x": Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1))),  # face in YZ, depth X
    "z": Matrix.Identity(4),
}


def cblock(a, size, loc, axis="y", mat="stone", ch=None, jit=None, tint=None, rot=(0, 0, 0)):
    """Chiselled block: chamfered octagon profile in the face plane, extruded
    through the depth axis. size is world (x, y, z) before `rot`."""
    sx, sy, sz = size
    if axis == "y":
        w, h, d = sx, sz, sy
    elif axis == "x":
        w, h, d = sy, sz, sx
    else:
        w, h, d = sx, sy, sz
    c = ch if ch is not None else min(w, h) * 0.17
    hw, hh = w / 2, h / 2
    pts = [(-hw + c, -hh), (hw - c, -hh), (hw, -hh + c), (hw, hh - c),
           (hw - c, hh), (-hw + c, hh), (-hw, hh - c), (-hw, -hh + c)]
    v = a.poly_prism(pts, d, loc=(0, 0, -d / 2), mat=mat, tint=tint)
    xf(a, v, Matrix.Translation(Vector(loc)) @ Euler(rot).to_matrix().to_4x4() @ _AXES[axis])
    j = jit if jit is not None else min(size) * 0.045
    for vv in v:
        vv.co += Vector((a.rng.uniform(-j, j), a.rng.uniform(-j, j), a.rng.uniform(-j, j)))
    return v


def stone_wall(a, run, t0, t1, z0, z1, d0, d1, course_h=1.7, blen=(1.8, 2.9), gap=0.08,
               mats=STONE_MIX, base_out=0.0, first_h=None, ch=None):
    """Coursed wall of chiselled blocks spanning the full depth d0..d1.
    run='x': runs along X (t = x, depth = y); run='y': runs along Y (depth = x)."""
    rng = a.rng
    z, ci = z0, 0
    out = []
    while z < z1 - 0.05:
        h = first_h if (ci == 0 and first_h) else course_h
        if z1 - (z + h) < course_h * 0.45:
            h = z1 - z
        o = base_out if ci == 0 else 0.0
        t = t0 - o
        tend = t1 + o
        first = True
        while t < tend - 0.05:
            L = rng.uniform(*blen)
            if first and ci % 2:
                L *= 0.55
            first = False
            if tend - (t + L) < blen[0] * 0.55:
                L = tend - t
            mid = t + L / 2
            hh = h
            if hh > 0.45:
                jd = rng.uniform(0.0, 0.14)
                depth = (d1 - d0) + 2 * o + jd
                dc = (d0 + d1) / 2
                m = pick(a, mats)
                if run == "x":
                    out += cblock(a, (L - gap, depth, hh - gap), (mid, dc, z + hh / 2), "y", m, ch=ch)
                else:
                    out += cblock(a, (depth, L - gap, hh - gap), (dc, mid, z + hh / 2), "x", m, ch=ch)
            t += L
        z += h
        ci += 1
    return out


def gable(a, cx, y, depth, zb, zpk, slope, course_h=1.25, blen=1.6, gap=0.08, mats=STONE_MIX):
    """Coursed stone gable triangle facing -Y (front face at y, `depth` thick):
    base at zb, apex at zpk, edges falling at `slope`. Each course is split into
    staggered blocks; the outer blocks are cut to the slanted edges."""
    rng = a.rng
    out = []
    z, k = zb, 0
    while zpk - z > 0.5:
        zt = min(z + course_h, zpk)
        hb, ht = (zpk - z) / slope, max((zpk - zt) / slope, 0.0)
        n = max(1, round(2 * hb / blen))
        edges = [-hb + 2 * hb * i / n for i in range(n + 1)]
        if k % 2 and n > 1:
            edges = [edges[0]] + [e + hb / n for e in edges[1:-2]] + [edges[-1]]
        for x0, x1 in zip(edges, edges[1:]):
            g = gap / 2
            bl, br = x0 + g, x1 - g
            tl = max(bl, -ht + g) if x0 <= -hb + 1e-6 else bl
            tr = min(br, ht - g) if x1 >= hb - 1e-6 else br
            tl, tr = max(tl, -ht + g), min(tr, ht - g)
            if tr - tl < 0.05:
                pts = [(bl, 0), (br, 0), ((bl + br) / 2, zt - z - gap)]
            else:
                pts = [(bl, 0), (br, 0), (tr, zt - z - gap), (tl, zt - z - gap)]
            v = a.poly_prism(pts, depth, loc=(cx, y + depth, z + g), rot=(PI / 2, 0, 0),
                             mat=pick(a, mats))
            j = 0.04
            for vv in v:
                vv.co += Vector((rng.uniform(-j, j), rng.uniform(-j, j), rng.uniform(-j, j)))
            out += v
        z, k = zt, k + 1
    return out


def oct_prism(a, w, h, L, mat="wood", end_mat="wood_end", ch=None, jit=0.02, tint=None):
    """Chamfered square timber: octagon (w x h) profile in local XY, length L along
    local Z centred on the origin; the two end faces get the cut-end material."""
    c = ch if ch is not None else min(w, h) * 0.17
    hw, hh = w / 2, h / 2
    pts = [(-hw + c, -hh), (hw - c, -hh), (hw, -hh + c), (hw, hh - c),
           (hw - c, hh), (-hw + c, hh), (-hw, hh - c), (-hw, -hh + c)]
    t = tint if tint is not None else 1 + a.rng.uniform(-0.07, 0.07)
    v = a.poly_prism(pts, L, loc=(0, 0, -L / 2), mat=mat, tint=t)
    if end_mat:
        mi = a._mi(end_mat)
        faces = set()
        for vv in v:
            faces.update(vv.link_faces)
        for f in faces:
            if len(f.verts) == 8:
                f.material_index = mi
    j = min(w, h) * jit
    for vv in v:
        vv.co += Vector((a.rng.uniform(-j, j), a.rng.uniform(-j, j), a.rng.uniform(-j * 0.5, j * 0.5)))
    return v


def sq_post(a, x, y, w, h, z0=0.0, d=None, mat="wood", rz=0.0):
    """Hewn square post (chamfered corners) with a lighter cut top."""
    d = d or w
    v = oct_prism(a, w, d, h, mat=mat, jit=0.025)
    xf(a, v, Matrix.Translation((x, y, z0 + h / 2)) @ Matrix.Rotation(rz, 4, "Z"))
    return v


def sq_beam(a, p1, p2, w, h=None, mat="wood", caps=True, bevel=True, ext=0.0, jit=0.02):
    """Hewn square beam between two points (w horizontal, h vertical)."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    L = d.length + 2 * ext
    h = h or w
    if bevel:
        v = oct_prism(a, w, h, L, mat=mat, end_mat="wood_end" if caps else None, jit=jit)
    else:
        v = a.box((w, h, L), mat=mat, jitter=min(w, h) * jit)
    xf(a, v, align_m((p1 + p2) / 2, d))
    return v


def log(a, p1, p2, r, sides=8, overhang=0.0, mat="wood", end_mat="wood_end", jit=0.03):
    """Round log between two points: one capped cylinder whose cap faces get the
    lighter cut-end material (28 tris at 8 sides, vs ~84 for the kit's beam)."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    L = d.length + 2 * overhang
    v = a.cyl(r, r * 0.97, L, sides, loc=(0, 0, -overhang), mat=mat, jitter=r * jit)
    mi = a._mi(end_mat)
    faces = set()
    for vv in v:
        faces.update(vv.link_faces)
    for f in faces:
        if len(f.verts) == sides:
            f.material_index = mi
    xf(a, v, align_m(p1, d))
    return v


def lash(a, loc, size=0.75, thickness=0.15, rot=(0, 0, 0)):
    """Bulky X lashing: two crossed, slightly flattened round rope loops."""
    out = []
    for ang in (PI / 4, -PI / 4):
        out += a.torus(size, thickness, rot=(0, ang, 0), seg=6, rseg=4, mat="rope", squash=0.85,
                       tint=1 + a.rng.uniform(-0.05, 0.05))
    xf(a, out, Matrix.Translation(Vector(loc)) @ Euler(rot).to_matrix().to_4x4())
    return out


def rings(a, c, r, axis=(0, 0, 1), count=2, th=None, mat="rope", seg=7):
    """Thick, round stacked rope coils of inner radius r around an axis through c."""
    th = th or max(0.14, r * 0.27)
    gap = th * 1.8
    v = []
    for i in range(count):
        off = (i - (count - 1) / 2) * gap
        v += a.torus(r + th * 0.5, th, loc=(0, 0, off), seg=seg, rseg=4, mat=mat,
                     tint=1 + a.rng.uniform(-0.07, 0.07))
    ax = Vector(axis).normalized()
    if abs(ax.z) > 0.999:
        M = Matrix.Translation(Vector(c))
    else:
        M = align_m(c, ax)
    xf(a, v, M)
    return v


def plank_wall(a, p0, U, length, height, n=None, thick=0.3, pw=0.85, hfun=None, zjit=0.25,
               gap=0.07, mats=WOOD_MIX):
    """Row of vertical planks from p0 along horizontal U."""
    U = Vector(U).normalized()
    p0 = Vector(p0)
    n = n or max(1, round(length / pw))
    w = length / n
    ang = math.atan2(U.y, U.x)
    out = []
    for i in range(n):
        c = p0 + U * (w * (i + 0.5))
        h = hfun(c) if hfun else height
        h -= a.rng.uniform(0, zjit)
        if h < 0.3:
            continue
        out += cblock(a, (w - gap, thick, h), (c.x, c.y, p0.z + h / 2), "y", pick(a, mats),
                      ch=min(w * 0.2, 0.14), jit=0.02, rot=(0, 0, ang))
    return out


# -- thatch ---------------------------------------------------------------------


def strand(a, q0, q1, E, N, w, t, mat, tint, taper=0.6):
    """One straw strand from q0 (tucked under the course above) to its visible
    end q1: a long, flat stick w wide across E (narrowing to w * taper at the
    end) with a crease raised t along N, so its two long facets catch the light
    differently. A closed pyramid on a flat quad: 6 tris."""
    bm = a.bm
    q0, q1 = Vector(q0), Vector(q1)
    vs = [bm.verts.new(p) for p in (q0 - E * (w / 2), q0 + E * (w / 2),
                                    q1 + E * (w * taper / 2), q1 - E * (w * taper / 2))]
    M = bm.verts.new(q0.lerp(q1, 0.45) + N * t)
    for i in range(4):
        bm.faces.new((vs[i], vs[(i + 1) % 4], M))
    bm.faces.new(vs[::-1])
    return a._finish(vs + [M], mat, tint)


def straw(a, P, U, D, wt, wb, length, courses=4, gap=0.42, sw=(0.28, 0.42), layers=2,
          base_t=0.8, lift=0.4, jag=0.45, ov=0.35, dark=0.15, seat=True, slab=True,
          eave=True, eave_len=(1.0, 1.7), eave_gap=None, hang=0.35, sides=(),
          side_len=(0.7, 1.2), side_gap=0.4, side_dir=(0.55, 1.0, 0.35), thick=(0.09, 0.17),
          course_len=(1.1, 1.45), slab_only=False, inset=0.0):
    """Dense, shaggy straw thatch: a dark under-slab covered in overlapping
    courses of individual long strands (each a ridged blade, butt up-slope, tip
    down-slope and lifted so it laps over the course below), with a hanging
    fringe of strands along the eave and optional ragged verges.

    P: centre of the top edge, U: across the panel, D: down the slope.
    wt / wb: widths at the top / bottom edge (wt=0 gives a hip triangle).
    sides: which side edges (-1 = -U side, +1 = +U side) get a hanging verge.
    inset: pulls the under-slab in from the side edges so strands hide its edge.
    """
    rng = a.rng
    P, U, D = Vector(P), Vector(U).normalized(), Vector(D).normalized()
    N = U.cross(D).normalized()
    if N.z < 0:
        N = -N
    if seat:
        P = P + N * base_t

    def half(s):
        s = min(max(s, 0.0), length)
        return (wt + (wb - wt) * s / length) / 2

    def mat():
        r = rng.random()  # golden straw with warm orange-brown strands for depth
        if r < dark:
            return "thatch_dark"
        return "dirt" if r < dark + 0.15 else ("rope" if r < dark + 0.4 else "thatch")

    out = []
    if slab:
        if wt < 0.05:
            pts = [(0, 0), (wb / 2 - inset, length), (-wb / 2 + inset, length)]
        else:
            pts = [(-wt / 2 + inset, 0), (wt / 2 - inset, 0), (wb / 2 - inset, length),
                   (-wb / 2 + inset, length)]
        v = a.poly_prism(pts, base_t, loc=(0, 0, -base_t), mat="rope_dark")
        out += xf(a, v, frame_m(P, U, D, N))

    step = length / max(courses, 1)
    if slab_only:
        courses = 0
    for k in range(courses):
        last = k == courses - 1
        s_end = (k + 1) * step
        for layer in range(layers):
            hw = half(s_end) + ov
            x = -hw + rng.uniform(0, gap) + layer * gap * 0.5
            while x < hw:
                w = rng.uniform(*sw)
                se = s_end + rng.uniform(-jag, jag) * (0.6 if last else 1.0)
                if last:
                    se += rng.uniform(0.15, 0.55)
                L = step * rng.uniform(*course_len)
                ss = max(-0.15, se - L)
                lim = half(ss) + ov * 0.6
                x0 = min(max(x, -lim), lim)
                x1 = x + rng.uniform(-0.18, 0.18)
                h0 = 0.03 + 0.05 * layer
                h1 = lift * rng.uniform(0.75, 1.25) + 0.07 * layer
                q0 = P + U * x0 + D * ss + N * h0
                q1 = P + U * x1 + D * se + N * h1
                if last:
                    q1 += DOWN * rng.uniform(0.05, 0.45)
                out += strand(a, q0, q1, U, N, w, rng.uniform(*thick), mat(), rng.uniform(0.92, 1.24),
                              taper=rng.uniform(0.35, 0.85))
                x += gap * rng.uniform(0.75, 1.25)

    Dh = Vector((D.x, D.y, 0))
    Dh = Dh.normalized() if Dh.length > 1e-4 else Vector((0, -1, 0))
    if eave:
        eg = eave_gap or gap * 1.1
        hw = wb / 2 + ov * 0.7
        x = -hw + rng.uniform(0, eg)
        H = (D + DOWN * (0.45 + hang)).normalized()  # carries on down the slope, drooping
        while x < hw:
            c = P + U * x + D * (length - 0.45) + N * (lift * 0.75)
            hh = (H + U * rng.uniform(-0.12, 0.12) + DOWN * rng.uniform(-0.1, 0.25)).normalized()
            q1 = c + hh * rng.uniform(*eave_len)
            out += strand(a, c, q1, U, N, rng.uniform(*sw), rng.uniform(*thick), mat(),
                          rng.uniform(0.8, 1.16), taper=rng.uniform(0.35, 0.85))
            x += eg * rng.uniform(0.75, 1.25)
    for sg in sides:
        Uh = Vector((U.x, U.y, 0)).normalized() * sg
        s = rng.uniform(0, side_gap)
        while s < length - 0.2:
            c = P + D * s + U * sg * (half(s) + ov * 0.4) + N * (lift * 0.5)
            hh = (Uh * side_dir[0] + DOWN * side_dir[1]
                  + D * (side_dir[2] + rng.uniform(-0.2, 0.2))).normalized()
            q1 = c + hh * rng.uniform(*side_len)
            out += strand(a, c, q1, D, Uh, rng.uniform(*sw), rng.uniform(*thick), mat(),
                          rng.uniform(0.8, 1.16), taper=rng.uniform(0.35, 0.85))
            s += side_gap * rng.uniform(0.75, 1.25)
    return out


# -- other parts ------------------------------------------------------------------


def torch(a, x, y, z, pole_h=2.6, br=0.75, flame_h=3.2):
    """Wooden torch: pole, staved bucket with rope ring, coals and a full flame.
    Returns the flame base position (for the VFX socket)."""
    rng = a.rng
    a.cyl(0.34, 0.38, pole_h + 0.2, 7, loc=(x, y, z), mat="wood_dark")
    bz = z + pole_h
    rings(a, (x, y, bz - 0.45), 0.36, count=2, th=0.13)
    a.cyl(br * 0.7, br * 0.95, 1.45, 8, loc=(x, y, bz), mat="wood_dark")
    for i in range(9):
        ang = 2 * PI * i / 9
        r = br * 0.92
        sh = rng.uniform(1.45, 1.85)
        v = a.box((br * 0.62, 0.17, sh), base=True, mat=pick(a, WOOD_MIX), bevel=0.03)
        xf(a, v, Matrix.Translation((x + r * math.cos(ang), y + r * math.sin(ang), bz))
           @ Euler((0.16, 0, ang + PI / 2)).to_matrix().to_4x4())
    a.torus(br * 1.02, 0.15, loc=(x, y, bz + 0.5), seg=10, rseg=4, mat="rope")
    a.torus(br * 1.12, 0.1, loc=(x, y, bz + 1.15), seg=10, rseg=4, mat="iron_dark")
    a.cyl(br * 1.0, br * 1.0, 0.12, 8, loc=(x, y, bz + 1.2), mat="charcoal")
    a.flame(flame_h, br * 0.95, loc=(x, y, bz + 1.25), tongues=8)
    a.flame(flame_h * 0.6, br * 0.55, loc=(x + br * 0.35, y - br * 0.2, bz + 1.25), tongues=4)
    return Vector((x, y, bz + 1.3))


def front_strip(a, pts, width, depth, cx, y, cz, mat, scale=1.0):
    """Glyph on a face whose normal is -Y; y = face plane, glyph extrudes toward -Y."""
    p = [(px * scale, py * scale) for px, py in pts]
    return a.strip(p, width, depth, loc=(cx, y, cz), rot=(PI / 2, 0, 0), mat=mat)


def glow(a, pts, width, depth, cx, y, cz, core=True, scale=1.0):
    """Emissive glyph on a -Y face: deep-orange stroke with a hot core."""
    out = front_strip(a, pts, width, depth, cx, y, cz, "fire_outer", scale)
    if core:
        out += front_strip(a, pts, width * 0.42, depth + 0.05, cx, y, cz, "glow_orange", scale)
    return out


def band(a, pts, w, h, mat):
    """Chain of thin boxes along a 3D polyline (cloth trims)."""
    out = []
    for p1, p2 in zip(pts, pts[1:]):
        out += sq_beam(a, p1, p2, w, h, mat=mat, caps=False, bevel=False, ext=0.04, jit=0.0)
    return out


def sheet(a, nx, ny, x0, x1, y0, y1, zfun, thick, mat, jit=0.05):
    """Draped cloth/hide sheet: a (nx x ny) faceted grid with thickness."""
    bm = a.bm
    top, bot = [], []
    for j in range(ny + 1):
        rt, rb = [], []
        for i in range(nx + 1):
            x = x0 + (x1 - x0) * i / nx
            y = y0 + (y1 - y0) * j / ny
            z = zfun(x, y)
            if 0 < i < nx and 0 < j < ny:
                z += a.rng.uniform(-jit, jit)
            rt.append(bm.verts.new((x, y, z)))
            rb.append(bm.verts.new((x, y, z - thick)))
        top.append(rt)
        bot.append(rb)
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((top[j][i], top[j][i + 1], top[j + 1][i + 1], top[j + 1][i]))
            bm.faces.new((bot[j][i], bot[j + 1][i], bot[j + 1][i + 1], bot[j][i + 1]))
    ring_t = [top[0][i] for i in range(nx + 1)] + [top[j][nx] for j in range(1, ny + 1)] + \
             [top[ny][i] for i in range(nx - 1, -1, -1)] + [top[j][0] for j in range(ny - 1, 0, -1)]
    ring_b = [bot[0][i] for i in range(nx + 1)] + [bot[j][nx] for j in range(1, ny + 1)] + \
             [bot[ny][i] for i in range(nx - 1, -1, -1)] + [bot[j][0] for j in range(ny - 1, 0, -1)]
    n = len(ring_t)
    for k in range(n):
        bm.faces.new((ring_t[k], ring_b[k], ring_b[(k + 1) % n], ring_t[(k + 1) % n]))
    verts = [v for r in top for v in r] + [v for r in bot for v in r]
    return a._finish(verts, mat, None, 0.0, 0.05)


def done(a):
    """Finish the asset; also return the offset finish() applies (bottom-centre
    re-origin) so VFX sockets can be placed in the asset's local studs."""
    bmesh.ops.recalc_face_normals(a.bm, faces=a.bm.faces[:])
    xs = [v.co.x for v in a.bm.verts]
    ys = [v.co.y for v in a.bm.verts]
    zs = [v.co.z for v in a.bm.verts]
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    return a.finish(), off


def socket(obj, off, kind, p, scale=1.0, name=None):
    return vfx.add(obj, kind, tuple(Vector(p) - off), scale=scale, name=name)


# ---------------------------------------------------------------------------
# VaultHall 26 x 18 x 15  (gable roof with exposed timber)
# ---------------------------------------------------------------------------


def build_vault_hall():
    """Open-fronted hall: a thatched nave between two stone wings, each wing
    with its own front-facing gable (crossed log rafters, stone gable triangle,
    ridge log with post stubs) and a steep outer thatch slope."""
    a = fk.Asset("VaultHall", "Buildings")
    EZ = 7.9                 # eave / tie log centre height
    XI, XO = 7.0, 12.4       # wing inner / outer post lines
    WC = (XI + XO) / 2       # wing ridge line
    PY = 7.0                 # front / back post lines
    ZP = 13.0                # wing rafter crossing (gable peak)
    RS = (ZP - EZ - 0.55) / (WC - XI)   # rafter slope
    YE = 7.7                 # nave eave half-depth
    ZNE, ZN = EZ + 0.45, 9.9            # nave thatch underside at eave / ridge

    # warm flagstone floor on a dark bed, spilling out past the opening
    a.box((2 * XI + 1.2, 14.6, 0.22), loc=(0, -0.9, 0), base=True, mat="stone_dark")
    nx, ny = 4, 3
    for i in range(nx):
        for j in range(ny):
            x = -XI - 0.5 + (2 * XI + 1.0) * (i + 0.5) / nx
            y = -8.1 + 14.0 * (j + 0.5) / ny
            a.box(((2 * XI + 1.0) / nx - 0.16, 14.0 / ny - 0.16, 0.14), loc=(x, y, 0.22), base=True,
                  mat="earth", jitter=0.04,
                  tint=a.rng.uniform(0.78, 0.95))

    for s in (-1, 1):
        xi, xo, wc = s * XI, s * XO, s * WC
        # wing front wall + gable triangle, outer side wall, back wall
        f0, f1 = sorted((s * (XI + 0.5), s * (XO - 0.5)))
        stone_wall(a, "x", f0, f1, 0, EZ - 0.4, -7.45, -6.3, course_h=2.05, first_h=1.85,
                   base_out=0.15, blen=(1.6, 2.2))
        gable(a, wc, -7.45, 1.0, EZ + 0.35, ZP - 0.1, RS)
        o0, o1 = sorted((s * (XO - 0.6), s * (XO + 0.5)))
        stone_wall(a, "y", -6.3, 6.3, 0, EZ + 0.2, o0, o1, course_h=2.7, first_h=2.6,
                   base_out=0.2, blen=(2.8, 3.8))
        stone_wall(a, "x", f0, f1, 0, EZ - 0.4, 6.3, 7.4, course_h=3.8, blen=(4.6, 4.6))
        tri = [((XI - WC) + 0.4, 0), ((XO - WC) - 0.4, 0), (0, ZP - EZ - 1.1)]
        a.poly_prism(tri, 0.9, loc=(wc, 7.35, EZ + 0.35), rot=(PI / 2, 0, 0), mat="stone")
        # plank wall closing the wing toward the nave
        for k in range(9):
            y = -6.0 + 12.0 * (k + 0.5) / 9
            a.box((0.35, 12.0 / 9 - 0.08, EZ - 0.7 - a.rng.uniform(0, 0.3)), base=True,
                  loc=(s * (XI + 0.3), y, 0.2), mat=pick(a, INSIDE), jitter=0.02)

        # big stone plinths, square posts, thick rope coils
        for (x, y, w, bs, bh) in ((xo, -PY, 1.4, 2.9, 2.1), (xi, -PY, 1.3, 2.3, 1.7),
                                  (xo, PY, 1.4, 2.9, 2.1)):
            cblock(a, (bs, bs, bh), (x, y, bh / 2), "y", pick(a, STONE_MIX), ch=0.32)
            sq_post(a, x, y, w, EZ - 0.45 - bh, z0=bh)
            if y < 0:
                rings(a, (x, y, bh + 0.45), w * 0.6, count=2)
                rings(a, (x, y, EZ - 1.2), w * 0.6, count=2)

        # corner plates (round ends facing front), front rafters crossing at the peak
        log(a, (xo, -8.4, EZ + 0.6), (xo, 8.4, EZ + 0.6), 0.55)
        log(a, (xi, -8.4, EZ + 0.6), (xi, -4.8, EZ + 0.6), 0.55)
        for yy in (-7.75, 7.75):
            for (xb, t) in ((xi, -1), (xo, 1)):
                pb = Vector((xb, yy + 0.2 * t, EZ + 0.6))
                pt = Vector((wc, yy + 0.2 * t, ZP))
                d = (pt - pb).normalized()
                log(a, pb - d * 0.3, pt + d * 1.0, 0.58)
            if yy < 0:
                for xb in (xo,):
                    lash(a, (xb, -8.0, EZ + 0.6), size=0.72, thickness=0.15, rot=(0, 0, 0))
        lash(a, (wc, -7.95, ZP), size=0.78, thickness=0.16)
        # wing ridge log riding on the thatch, three post stubs along it
        zr = ZP + 0.35
        log(a, (wc, -8.7, zr), (wc, 8.5, zr), 0.58)
        for (y, top) in ((-7.0, 15.0), (0.0, 14.7), (7.0, 14.4)):
            sq_post(a, wc, y, 1.05, top - (zr - 0.3), z0=zr - 0.3)
            if y < 0:
                rings(a, (wc, y, zr + 0.55), 0.62, count=1)

        # outer wing slope (the visible one) and the short inner slope
        WS = 1.2   # wing thatch slope (shallower than the rafters, so it spreads past them)
        Lw = 3.5 * math.sqrt(1 + WS * WS)
        straw(a, (wc, 0.2, ZP - 1.1), (0, 1, 0), (s, 0, -WS), 15.4, 15.4, Lw, courses=3,
              gap=0.56, sw=(0.4, 0.6), base_t=0.85, lift=0.4, eave_len=(0.9, 1.5), hang=0.25,
              eave_gap=0.9, jag=0.4, layers=1)
        Li = 2.3 * math.sqrt(1 + WS * WS)
        straw(a, (wc, 0.2, ZP - 1.1), (0, 1, 0), (-s, 0, -WS), 15.4, 15.4, Li, courses=1,
              gap=0.85, sw=(0.45, 0.65), layers=1, base_t=0.85, eave=False)

    # back wall of the nave: stone footing course + plank wall with posts and rails
    stone_wall(a, "x", -XI, XI, 0, 1.2, 6.25, 7.3, course_h=1.2, blen=(2.8, 3.8))
    for k in range(11):  # plain plank boxes: only the inner face shows
        x = -XI + 2 * XI * (k + 0.5) / 11
        hh = EZ - 1.0 - a.rng.uniform(0, 0.3)
        a.box((2 * XI / 11 - 0.08, 0.5, hh), loc=(x, 6.7, 1.15), base=True, mat=pick(a, INSIDE),
              jitter=0.02)
    for z in (3.0, 5.7):
        sq_beam(a, (-XI, 6.2, z), (XI, 6.2, z), 0.5, 0.55)
    for x in (-3.0, 3.0):
        sq_post(a, x, 5.95, 1.0, EZ - 0.4, z0=0.35)
    # header over the opening + knee braces
    sq_beam(a, (-XI, -6.6, EZ - 1.25), (XI, -6.6, EZ - 1.25), 0.75, 0.75)
    for s in (-1, 1):
        sq_beam(a, (s * XI, -6.6, EZ - 3.3), (s * (XI - 1.9), -6.6, EZ - 1.55), 0.45, 0.45)
    # front / back eave logs across the whole hall
    for y in (-PY, PY):
        log(a, (-XO - 0.9, y, EZ), (XO + 0.9, y, EZ), 0.56)

    # nave: both slopes fully thatched, since the lobby camera sees the back too
    Ln = math.hypot(YE, ZN - ZNE)
    for dy in (-YE, YE):
        straw(a, (0, 0, ZN), (1, 0, 0), (0, dy, -(ZN - ZNE)), 2 * XI + 1.4, 2 * XI + 1.4, Ln,
              courses=4, gap=0.6, sw=(0.42, 0.62), eave_gap=0.9, base_t=0.9, lift=0.42,
              eave_len=(1.1, 1.8), hang=0.15, jag=0.5)
    # nave ridge log between the wing peaks, centre post stub
    zn = ZN + 0.9 + 0.75
    log(a, (-WC, 0, zn), (WC, 0, zn), 0.6)
    sq_post(a, 0, 0, 1.1, 13.6 - (zn - 0.5), z0=zn - 0.5)
    rings(a, (0, 0, zn + 0.75), 0.66, count=1)
    obj, _ = done(a)
    return obj


# ---------------------------------------------------------------------------
# AncestralForge 30 x 18 x 24
# ---------------------------------------------------------------------------

DIAMOND = [(0, 0.8), (0.65, 0), (0, -0.8), (-0.65, 0), (0, 0.8)]
CHEVRON = [(-0.65, 0.45), (0, -0.45), (0.65, 0.45)]
EMBLEM_GLYPH = (
    [(-0.32, 0.8), (-0.32, 2.05)], [(0.32, 0.8), (0.32, 2.05)],          # 2 parallel bars
    [(0, 0.55), (0.55, 0), (0, -0.55), (-0.55, 0), (0, 0.55)],           # centre diamond
    [(-0.55, 0), (-1.65, 0)], [(-1.55, 0), (-2.05, 0.4)], [(-1.55, 0), (-2.05, -0.4)],
    [(0.55, 0), (1.65, 0)], [(1.55, 0), (2.05, 0.4)], [(1.55, 0), (2.05, -0.4)],
    [(0, -0.55), (0, -1.8)], [(0, -1.75), (-0.38, -2.15)], [(0, -1.75), (0.38, -2.15)],
)


def build_forge():
    a = fk.Asset("AncestralForge", "Buildings")
    AW, FZ, SZ = 4.2, 0.7, 4.3        # arch half-width, floor, springing
    RT = 0.95                         # ring thickness
    CH = (SZ + AW + RT) / 5           # main course height (5 courses to the ring top)
    YF, YB = -5.4, 7.6                # main block front/back
    OW = AW + RT                      # outer half-width of the arch
    MX = 6.5                          # main block half-width

    # --- apron / step in front of the arch ---
    for i in range(6):
        x = -7.4 + 14.8 * (i + 0.5) / 6
        cblock(a, (2.35, 1.7, 0.7), (x, -8.2, 0.35), "y", pick(a, STONE_MIX))
    for x in (-6.0, 6.0):
        cblock(a, (1.6, 1.9, 0.7), (x, -6.45, 0.35), "y", pick(a, STONE_MIX))
    a.box((2 * AW + 0.4, 9.0, FZ - 0.1), loc=(0, -2.9, 0), base=True, mat="stone_dark")
    for i in range(4):  # grey threshold slabs at the mouth
        x = -AW + 2 * AW * (i + 0.5) / 4
        cblock(a, (2 * AW / 4 - 0.12, 1.8, 0.4), (x, -6.45, FZ - 0.2), "y", pick(a, STONE_MIX), ch=0.12)

    # --- main block with a wide arch ---
    for s in (-1, 1):
        x0, x1 = sorted((s * OW, s * MX))
        stone_wall(a, "x", x0, x1, 0, 5 * CH, YF, YB, course_h=CH, blen=(1.4, 1.4))
    stone_wall(a, "x", -MX, MX, 5 * CH, 7 * CH, YF, YB, course_h=CH, blen=(3.0, 4.2))
    TZ = 7 * CH
    a.box((2 * OW, YB - 2.0, 5 * CH), loc=(0, (YB + 2.0) / 2, 0), base=True, mat="stone")
    for s in (-1, 1):  # spandrels behind the ring
        cblock(a, (2.0, 5.8, 2.0), (s * (OW - 1.0), YF + 3.0, 5 * CH - 1.0), "y", "stone")
    # orange brick arch ring + jambs
    rc = AW + RT / 2
    nv = 11
    for i in range(nv):
        th = PI * (i + 0.5) / nv
        Lv = PI * rc / nv - 0.1
        cblock(a, (Lv, 1.7, RT), (rc * math.cos(th), YF - 0.3, SZ + rc * math.sin(th)), "y",
               "clay", rot=(0, PI / 2 - th, 0), tint=a.rng.uniform(0.95, 1.15))
    for s in (-1, 1):
        for k in range(3):
            hz = (SZ - FZ) / 3
            cblock(a, (RT, 1.7, hz - 0.08), (s * rc, YF - 0.3, FZ + hz * (k + 0.5)), "y", "clay",
                   tint=a.rng.uniform(0.95, 1.15))
    # deep brick chamber lit by the fire: glowing bricks over dark clay mortar
    BACK = 2.0
    BH = 0.92
    a.box((2 * AW + 0.2, 0.08, SZ + AW - FZ + 0.2), loc=(0, BACK + 0.02, FZ), base=True, mat="clay",
          tint=0.55)

    def brick_mat(r):
        q = a.rng.random()
        return "clay" if q < 0.14 else ("ember" if (r < 2 and q < 0.45) else "fire_outer")

    bw = 2 * AW / 5
    for r in range(9):
        off = 0.5 * bw if r % 2 else 0.0
        z0 = FZ + BH * r
        for c in range(-1, 6):
            xa = max(-AW, -AW + bw * c + off)
            xb = min(AW, -AW + bw * (c + 1) + off)
            if xb - xa < 0.3:
                continue
            xm = max(abs(xa), abs(xb))
            lim = SZ + (math.sqrt(max(0.0, AW * AW - xm * xm)) if xm < AW else 0.0)
            h = min(BH, lim - z0) - 0.1
            if h < 0.3:
                continue
            a.box((xb - xa - 0.12, 0.4, h), loc=((xa + xb) / 2, BACK - 0.2, z0 + 0.05), base=True,
                  mat=brick_mat(r), jitter=0.03)
    for s in (-1, 1):
        for r in range(3):
            z0 = FZ + (SZ - FZ + 0.4) * r / 3
            hz = (SZ - FZ + 0.4) / 3 - 0.1
            for k in range(2):
                ya = YF + 1.0 + (BACK - YF - 1.0) * k / 2
                yb = YF + 1.0 + (BACK - YF - 1.0) * (k + 1) / 2
                a.box((0.3, yb - ya - 0.12, hz), base=True, mat=brick_mat(r + 1),
                      loc=(s * (AW + 0.05), (ya + yb) / 2, z0 + 0.05))
    for i in range(7):
        th = PI * (i + 0.5) / 7
        r = AW + 0.15
        for (y0, y1) in ((YF + 0.9, BACK),):
            a.box((PI * r / 7 - 0.1, y1 - y0 - 0.12, 0.35),
                  loc=(r * math.cos(th), (y0 + y1) / 2, SZ + r * math.sin(th)),
                  rot=(0, PI / 2 - th, 0), mat="fire_outer" if i % 3 else "clay")
    # warm flagstone floor + a fire on a coal bed against the back wall
    for i in range(4):
        for j in range(3):
            x = -AW + 2 * AW * (i + 0.5) / 4
            y = YF + 0.9 + (BACK - YF - 0.9) * (j + 0.5) / 3
            a.box((2 * AW / 4 - 0.14, (BACK - YF - 0.9) / 3 - 0.14, 0.1), loc=(x, y, FZ - 0.1),
                  base=True, mat="ember" if (j == 2 and 0 < i < 3) else "clay_light", jitter=0.02)
    FY0 = BACK - 1.15
    a.box((3.4, 1.6, 0.3), loc=(0, FY0, FZ), base=True, mat="ember")
    a.flame(3.0, 1.25, loc=(0, FY0, FZ + 0.35), tongues=7)

    # --- upper tower (chimney), cornice, open stone rim with fire ---
    stone_wall(a, "x", -5.0, 5.0, TZ, 20.4, -3.4, 6.2, course_h=1.8, blen=(2.8, 3.6))
    stone_wall(a, "x", -4.3, 4.3, 20.4, 21.6, -2.7, 5.5, course_h=1.2, blen=(2.6, 3.2))
    for (sx, sy, x, y) in ((3.4, 0.8, 0, -1.3), (3.4, 0.8, 0, 1.3), (0.8, 1.8, -1.3, 0),
                           (0.8, 1.8, 1.3, 0)):
        cblock(a, (sx, sy, 1.2), (x, y, 22.2), "y", "clay", tint=0.8)
    a.box((1.9, 1.9, 0.3), loc=(0, 0, 21.6), base=True, mat="charcoal")
    a.flame(2.1, 0.95, loc=(0, 0, 21.85), tongues=6)
    # glow seam down the right of the chimney front, recessed into a slot
    a.box((0.9, 0.3, 20.0 - TZ - 0.4), loc=(3.7, -3.4, TZ + 0.3), base=True, mat="stone_dark")
    glow(a, [(0, 0), (0, 20.0 - TZ - 1.0)], 0.5, 0.15, 3.7, -3.5, TZ + 0.6)

    # --- solid octagonal emblem plaque with a segmented block border ---
    ec, R = Vector((0, -5.9, 14.0)), 3.4
    cblock(a, (4.8, 2.6, 4.2), (0, -4.6, 15.0), "y", "stone")  # backing block onto the tower
    ap = R * math.cos(PI / 8)
    for k in range(8):
        phi = k * PI / 4
        Le = 2 * R * math.sin(PI / 8) + 0.05
        rr = ap - 0.45
        cblock(a, (Le, 1.0, 0.95), (ec.x + rr * math.cos(phi), ec.y, ec.z + rr * math.sin(phi)), "y",
               "stone_light", rot=(0, PI / 2 - phi, 0))
    inner = [((R - 0.75) * math.cos(PI / 8 + k * PI / 4), (R - 0.75) * math.sin(PI / 8 + k * PI / 4))
             for k in range(8)]
    a.poly_prism(inner, 0.9, loc=(ec.x, ec.y + 0.5, ec.z), rot=(PI / 2, 0, 0), mat="stone")
    gy = ec.y - 0.38
    for pts in EMBLEM_GLYPH:
        glow(a, pts, 0.36, 0.2, ec.x, gy, ec.z, scale=1.12)

    # --- rune pillars + hollow-topped square stacks behind them ---
    for s in (-1, 1):
        x0, x1 = sorted((s * MX, s * 10.0))
        stone_wall(a, "x", x0, x1, 0, 12.4, -6.7, 7.6, course_h=2.07, blen=(1.6, 2.0),
                   base_out=0.25)
        cx = s * 8.25
        for (sx, sy, dx, dy) in ((3.0, 0.8, 0, -1.1), (3.0, 0.8, 0, 1.1), (0.8, 1.4, -1.1, 0),
                                 (0.8, 1.4, 1.1, 0)):
            cblock(a, (sx, sy, 3.0), (cx + dx, 1.2 + dy, 13.9), "y", pick(a, STONE_MIX))
        a.box((1.5, 1.5, 0.2), loc=(cx, 1.2, 14.9), base=True, mat="stone_dark")
        gx, gyy = cx, -6.8
        glow(a, DIAMOND, 0.3, 0.22, gx, gyy, 10.0, core=False, scale=1.25)
        a.box((0.4, 0.3, 0.4), loc=(gx, gyy - 0.05, 10.0), rot=(0, PI / 4, 0), mat="fire_outer")
        glow(a, DIAMOND, 0.3, 0.22, gx, gyy, 7.3, core=False, scale=1.25)
        a.box((0.4, 0.3, 0.4), loc=(gx, gyy - 0.05, 7.3), rot=(0, PI / 4, 0), mat="fire_outer")
        glow(a, CHEVRON, 0.3, 0.22, gx, gyy, 5.0, core=False, scale=1.25)
        glow(a, [(-0.3, 0.2), (0, -0.15), (0.3, 0.2)], 0.22, 0.22, gx, gyy, 4.55, core=False,
             scale=1.25)

    # --- wood posts flanking the arch ---
    for s in (-1, 1):
        x = s * (OW + 0.6)
        cblock(a, (1.6, 1.6, 1.0), (x, -6.0, 0.5), "y", pick(a, STONE_MIX))
        sq_post(a, x, -6.0, 1.1, 12.7, z0=1.0, d=1.2)
        rings(a, (x, -6.0, 1.6), 0.68, count=2)
        rings(a, (x, -6.0, 11.0), 0.68, count=3)
        a.box((1.3, 0.22, 1.4), loc=(x, -6.65, 3.2), mat="iron_dark")  # iron bracket
    px = OW + 0.6
    # matching diagonal braces, one per side: from the arch post top down and out to a
    # lashed foot post. They run at one depth just in front of the rune pillars
    # (pillar face y=-6.7, brace back face y=-6.9), so nothing clips into the building.
    BY, BR = -7.4, 0.5
    for s in (-1, 1):
        top, foot = Vector((s * px, BY, 12.9)), Vector((s * 13.4, BY, 8.6))
        log(a, top, foot, BR)
        lash(a, (s * px, BY + 0.3, 12.7), size=0.78, thickness=0.15)
        cblock(a, (1.4, 1.4, 0.9), (s * 13.4, BY, 0.45), "y", pick(a, STONE_MIX))
        sq_post(a, s * 13.4, BY, 0.9, 9.2, z0=0.9, d=0.9)
        rings(a, (s * 13.4, BY, 1.5), 0.55, count=2)
        lash(a, (s * 13.4, BY, 8.7), size=0.7, thickness=0.14)

    # --- side wings: plank walls, rails, corner posts, outward lean-to thatch ---
    for s in (-1, 1):
        xo, xi = s * 13.6, s * 10.0
        x0 = min(xo, xi)
        plank_wall(a, (x0, -5.0, 0), (1, 0, 0), 3.6, 7.6, n=4, thick=0.35)
        plank_wall(a, (xo, -5.0, 0), (0, 1, 0), 12.0, 7.2, n=6, thick=0.35)
        for z in (1.5, 5.6):
            sq_beam(a, (x0, -5.35, z), (x0 + 3.6, -5.35, z), 0.4, 0.45)
        sq_post(a, xo, -5.1, 1.0, 8.6 if s > 0 else 8.2)
        sq_post(a, s * 10.15, -5.1, 1.0, 9.4)

        straw(a, (s * 9.7, 0.6, 10.7), (0, 1, 0), (s * 1.0, 0, -0.55), 13.6, 13.6, 5.3, courses=2,
              gap=0.46, layers=1, base_t=0.85, lift=0.38, eave_len=(0.9, 1.4), hang=0.2, eave_gap=0.75,
              course_len=(1.2, 1.5))
    obj, off = done(a)
    socket(obj, off, "brazier_fire", (0, 0, 23.1))
    socket(obj, off, "chimney_smoke", (0, 0, 24.3))
    socket(obj, off, "heat_glow", (0, FY0, FZ + 1.4))
    socket(obj, off, "glyph_glow", (ec.x, ec.y - 1.2, ec.z))
    socket(obj, off, "heat_glow", (3.7, -3.9, (TZ + 20.0) / 2), scale=0.6, name="VFX_heat_glow_seam")
    return obj


# ---------------------------------------------------------------------------
# DeployGate 26 x 6 x 20 (10-wide opening)
# ---------------------------------------------------------------------------

SIGIL = [
    [(-0.75, 0.8), (-0.85, 0.35), (-0.6, 0.0), (-0.2, -0.15), (0, -0.15)],
    [(0.75, 0.8), (0.85, 0.35), (0.6, 0.0), (0.2, -0.15), (0, -0.15)],
    [(0, -0.15), (0, -1.3)],
    [(-0.35, -0.6), (0.35, -0.6)],
    [(-0.22, -1.15), (0, -1.55), (0.22, -1.15)],
]


def banner(a, cx, top_z, y, w=2.2, h=5.0, notch=0.9):
    pts = [(-w / 2, 0), (w / 2, 0), (w / 2, -h), (0, -h + notch), (-w / 2, -h)]
    a.poly_prism(pts, 0.12, loc=(cx, y, top_z), rot=(PI / 2, 0, 0), mat="cloth_red")
    a.box((w + 0.1, 0.3, 0.4), loc=(cx, y - 0.06, top_z - 0.12), mat="cloth_red")
    for pts in SIGIL:
        front_strip(a, pts, 0.26, 0.06, cx, y - 0.11, top_z - 2.0, "cloth_cream", scale=1.1)


def door_leaf(a, hx, hy, s, width=4.0, height=11.0, angle=math.radians(60)):
    """Plank door hinged at (hx, hy), swung `angle` toward the back. Battens and
    brass hinges on its (closed) front face."""
    rng = a.rng
    dvec = Vector((-s * math.cos(angle), math.sin(angle), 0))
    nvec = Vector((-s * math.sin(angle), -math.cos(angle), 0))
    v = []
    n = 4
    for k in range(n):
        u = width * (k + 0.5) / n
        hh = height - rng.uniform(0, 0.45)
        v += a.box((width / n - 0.07, 0.3, hh), loc=(u, 0, hh / 2), mat=pick(a, WOOD_MIX), jitter=0.025)
    for z in (2.2, height - 2.2):
        v += a.box((width - 0.4, 0.22, 0.75), loc=(width / 2, 0.26, z), mat="wood_light", jitter=0.02)
        v += a.box((1.5, 0.1, 0.42), loc=(0.85, 0.42, z), mat="flower_yellow")
        v += a.cyl(0.17, 0.17, 0.95, 6, loc=(0.0, 0.25, z - 0.47), mat="flower_yellow")
    M = Matrix(((dvec.x, nvec.x, 0, hx), (dvec.y, nvec.y, 0, hy), (0, 0, 1, 0.25), (0, 0, 0, 1)))
    xf(a, v, M)
    return v


def build_deploy_gate():
    a = fk.Asset("DeployGate", "Buildings")
    torches = []
    ZT = 15.0   # pillar top
    ZL = 14.2   # lintel centre
    for s in (-1, 1):
        x0, x1 = sorted((s * 6.9, s * 10.7))
        # wide plinth of large blocks + tall coursed shaft
        bx0, bx1 = sorted((s * 6.3, s * 11.3))
        stone_wall(a, "x", bx0, bx1, 0, 2.4, -2.7, 2.7, course_h=2.4, blen=(2.4, 2.7), ch=0.35)
        stone_wall(a, "x", x0, x1, 2.4, ZT, -2.05, 2.05, course_h=2.1, blen=(1.7, 2.2))
        # raised relief: a chain of diamonds with chevrons inside, same stone tone
        cx = s * 8.8
        for k in range(5):
            cz = 4.0 + 2.1 * k
            front_strip(a, [(0, 1.0), (0.9, 0), (0, -1.0), (-0.9, 0), (0, 1.0)], 0.28, 0.24,
                        cx, -2.07, cz, "stone")
            front_strip(a, [(-0.46, 0.3), (0, -0.2), (0.46, 0.3)], 0.22, 0.22, cx, -2.07, cz, "stone")
            front_strip(a, [(-0.24, 0.65), (0, 0.4), (0.24, 0.65)], 0.17, 0.2, cx, -2.07, cz,
                        "stone_dark")
        # cluster of tall vertical timbers on the opening side, rising past the lintel
        sq_post(a, s * 5.55, -1.35, 1.1, 15.8, d=1.3)
        for k, (dx, hh) in enumerate(((0.7, 16.3), (1.35, 15.6))):
            sq_post(a, s * (5.2 + dx), -1.75 - 0.12 * k, 0.66, hh, d=0.55)
        sq_post(a, s * 6.35, 0.2, 1.0, 16.6, d=1.2)
        sq_post(a, s * 5.6, 1.4, 0.9, 15.0, d=1.0)
        rings(a, (s * 5.55, -1.35, 12.6), 0.72, count=2)
        rings(a, (s * 5.55, -1.35, 0.9), 0.72, count=2)
        torches.append(torch(a, s * 7.7, -0.6, ZT, pole_h=1.0, br=1.0, flame_h=3.0))
        # plank door, swung open toward the back
        door_leaf(a, s * 4.85, -1.1, s, width=4.0, height=11.8)
        # banner pole off the pillar's outer corner, banner hung from two rope loops
        log(a, (s * 9.9, -2.55, 12.4), (s * 13.1, -2.55, 12.4), 0.27, sides=7)
        bx = s * 11.7
        for lx in (bx - 0.8, bx + 0.8):
            v = a.torus(0.43, 0.11, seg=8, rseg=4, mat="rope", rot=(0, PI / 2, 0))
            xf(a, v, Matrix.Translation((lx, -2.6, 12.22)))
        banner(a, bx, 11.85, -2.65, w=2.7, h=6.8, notch=1.2)
    # lintel beam + top plank, rope lashings, square peg blocks at the ends
    sq_beam(a, (-8.4, -1.55, ZL), (8.4, -1.55, ZL), 1.3, 1.2)
    sq_beam(a, (-4.3, -1.35, ZL + 0.9), (4.3, -1.35, ZL + 0.9), 1.8, 0.6)
    for s in (-1, 1):
        rings(a, (s * 4.75, -1.55, ZL), 0.8, axis=(1, 0, 0), count=2)
        rings(a, (s * 7.05, -1.55, ZL), 0.8, axis=(1, 0, 0), count=2)
        cblock(a, (0.8, 0.85, 0.85), (s * 8.75, -1.55, ZL), "x", "wood_light", ch=0.12)
        a.box((0.14, 0.32, 0.32), loc=(s * 9.17, -1.55, ZL), mat="iron_dark")
    obj, off = done(a)
    for k, t in enumerate(torches):
        socket(obj, off, "torch_fire", t, name=f"VFX_torch_fire_{'LR'[k]}")
    socket(obj, off, "dust", (0, 0, 0.3))
    return obj


# ---------------------------------------------------------------------------
# Market stalls 14 x 8 x 10
# ---------------------------------------------------------------------------


def counter(a, x0, x1, yf, yb, h=3.4, studs=5):
    """Market counter: thick overhanging plank slab over a plank front with battens."""
    w = x1 - x0
    for k in range(3):
        y = yf - 0.45 + (yb - yf + 0.6) * (k + 0.5) / 3
        L = w + 0.8 - a.rng.uniform(0, 0.4)
        cblock(a, (L, (yb - yf + 0.6) / 3 - 0.05, 0.5),
               ((x0 + x1) / 2 + a.rng.uniform(-0.15, 0.15), y, h - 0.25), "y", pick(a, WOOD_MIX),
               ch=0.1, jit=0.03)
    plank_wall(a, (x0, yf + 0.25, 0), (1, 0, 0), w, h - 0.5, thick=0.25, pw=0.85, zjit=0.0)
    for s, x in ((1, x0), (-1, x1)):
        plank_wall(a, (x + s * 0.15, yf + 0.25, 0), (0, 1, 0), yb - yf - 0.3, h - 0.5, thick=0.25,
                   pw=0.8, zjit=0.0)
    for i in range(studs):
        x = x0 + 0.3 + (w - 0.6) * i / (studs - 1)
        sq_post(a, x, yf + 0.05, 0.55, h - 0.55, d=0.35)
    sq_beam(a, (x0, yf, 0.35), (x1, yf, 0.35), 0.35, 0.45)
    sq_beam(a, (x0, yf, h - 0.85), (x1, yf, h - 0.85), 0.3, 0.4)


def build_thatch_stall():
    a = fk.Asset("ThatchMarketStall", "Buildings")
    FY, BY, PX = -2.2, 2.6, 5.5
    YT, YE = 3.4, -3.9

    def plane(y):  # roof slab underside
        return 6.95 + (y - YE) * 0.2

    for s in (-1, 1):
        sq_post(a, s * PX, FY, 1.15, plane(FY) - 0.65)
        sq_post(a, s * PX, BY, 1.15, 10.0)
        rings(a, (s * PX, FY, 0.6), 0.62, count=2)
        rings(a, (s * PX, FY, 3.0), 0.62, count=3)
        rings(a, (s * PX, BY, 3.1), 0.62, count=2)
        rings(a, (s * PX, FY, plane(FY) - 1.3), 0.62, count=2)
    sq_post(a, 0, BY, 0.9, 10.0)
    # frame: front beam, back beam, rafters, knee braces
    zf = plane(FY) - 0.45
    sq_beam(a, (-6.3, FY, zf), (6.3, FY, zf), 0.75, 0.6)
    sq_beam(a, (-5.5, BY, 7.5), (5.5, BY, 7.5), 0.6, 0.6)
    for x in (-PX, 0.0, PX):
        sq_beam(a, (x, 3.3, plane(3.3) - 0.28), (x, -3.1, plane(-3.1) - 0.28), 0.55, 0.5)
    for s in (-1, 1):
        sq_beam(a, (s * PX, FY, zf - 2.0), (s * (PX - 1.8), FY, zf - 0.2), 0.45, 0.45)
        sq_beam(a, (s * PX, BY, 5.6), (s * (PX - 1.8), BY, 7.35), 0.45, 0.45)
        sq_beam(a, (s * PX, FY, 4.3), (s * PX, BY, plane(BY) - 0.95), 0.45, 0.45)  # long side brace
        lash(a, (s * PX, FY - 0.1, zf), size=0.72, thickness=0.15)
    # thick layered thatch (mono-pitch to the front) with a hipped left end
    Ls = Vector((0, YT - YE, plane(YT) - plane(YE))).length
    straw(a, (0.15, YT, plane(YT)), (1, 0, 0), (0, YE - YT, plane(YE) - plane(YT)), 11.4, 11.4,
          Ls, courses=4, gap=0.3, base_t=0.7, lift=0.42, jag=0.45, eave_len=(1.0, 1.6), hang=0.2,
          sides=(1,), side_len=(0.6, 1.0), side_gap=0.4)
    straw(a, (-5.4, -0.25, plane(-0.25) + 0.25), (0, 1, 0), (-1.0, 0, -1.25), 6.6, 7.6, 1.2,
          courses=1, gap=0.32, base_t=0.6, lift=0.35, eave_len=(0.9, 1.4), seat=False, hang=0.15,
          course_len=(1.3, 1.8))
    # back ridge beam with three post stubs poking above it
    zr = plane(BY + 0.35) + 0.55
    log(a, (-6.3, BY + 0.35, zr), (6.3, BY + 0.35, zr), 0.42)
    for x in (-PX, 0.0, PX):
        rings(a, (x, BY, zr - 0.05), 0.56, count=1)
    counter(a, -5.0, 5.0, -2.6, -0.7, h=3.4)
    obj, _ = done(a)
    return obj


def build_hide_stall():
    a = fk.Asset("HideMarketStall", "Buildings")
    rng = a.rng
    FY, BY, PX = -2.7, 2.9, 5.8
    ZB, ZS = 6.85, 7.85 # front/back beam and side beam centres (under the canopy)
    for s in (-1, 1):
        for y in (FY, BY):
            sq_post(a, s * PX, y, 1.05, 10.0)
            lash(a, (s * PX, y - 0.05 if y < 0 else y + 0.05, ZB + 0.25), size=0.92, thickness=0.17)
        rings(a, (s * PX, FY, 3.0), 0.66, count=3)
        rings(a, (s * PX, FY, 0.6), 0.66, count=2)
        rings(a, (s * PX, BY, 3.3), 0.66, count=2)
        # knee braces: ends (YZ) and back posts (XZ)
        sq_beam(a, (s * PX, FY, 5.2), (s * PX, FY + 1.9, ZS - 0.2), 0.42, 0.42)
        sq_beam(a, (s * PX, BY, 5.2), (s * PX, BY - 1.9, ZS - 0.2), 0.42, 0.42)
        sq_beam(a, (s * PX, BY, 5.4), (s * (PX - 1.9), BY, ZB - 0.2), 0.42, 0.42)
        sq_beam(a, (s * PX, -3.6, ZS), (s * PX, 3.8, ZS), 0.65, 0.6)
    for y in (FY, BY):
        sq_beam(a, (-6.9, y, ZB), (6.9, y, ZB), 0.72, 0.72)

    # sagging hide canopy
    X0, X1, Y0, Y1 = -6.1, 6.1, -3.3, 3.4

    def zc(x, y):
        u = x / 6.1
        sag = 1.05 * (1 - u * u)
        curl = max(0.0, (-2.4 - y)) * 0.55
        return 8.7 - sag - curl - 0.25 * (1 - ((y - 0.05) / 3.35) ** 2)

    sheet(a, 10, 6, X0, X1, Y0, Y1, zc, 0.12, "clay_light", jit=0.14)  # peachy, crumpled hide
    # thick red border on top, deep red skirt on the front edge
    xs = [X0 + (X1 - X0) * i / 10 for i in range(11)]
    for yy in (Y0 + 0.3, Y1 - 0.3):
        band(a, [(x, yy, zc(x, yy) + 0.06) for x in xs], 0.62, 0.14, "cloth_red")
    ys = [Y0 + (Y1 - Y0) * j / 5 for j in range(6)]
    for xx in (X0 + 0.3, X1 - 0.3):
        band(a, [(xx, y, zc(xx, y) + 0.06) for y in ys], 0.62, 0.14, "cloth_red")
    band(a, [(x, Y0 - 0.03, zc(x, Y0) - 0.36) for x in xs], 0.14, 0.75, "cloth_red")
    # 10 pennants alternating red (larger, in front) / tan, tan straps over the band
    n = 10
    for i in range(n):
        x = X0 + 0.65 + (X1 - X0 - 1.3) * i / (n - 1)
        z = zc(x, Y0) - 0.7
        ry = -math.atan((zc(x + 0.2, Y0) - zc(x - 0.2, Y0)) / 0.4)
        red = i % 2 == 0
        hgt, hw = (1.85, 0.64) if red else (1.5, 0.52)
        pts = [(-hw, 0), (hw, 0), (hw, -hgt * 0.55), (0, -hgt), (-hw, -hgt * 0.55)]
        a.poly_prism(pts, 0.08, loc=(x, Y0 - (0.14 if red else 0.06), z + 0.05),
                     rot=(PI / 2 + 0.08, ry, 0), mat="cloth_red" if red else "wicker")
        if not red:
            a.box((0.42, 0.32, 0.95), loc=(x, Y0 - 0.03, zc(x, Y0) - 0.36), rot=(0, ry, 0),
                  mat="wicker")
    # counter (L-shape: front run + right-end return)
    counter(a, -5.1, 4.0, -2.4, -0.6, h=3.3, studs=5)
    for x in (4.35, 4.85, 5.35):
        a.plank((0.5, 4.6, 0.3), loc=(x - 0.1, 0.0, 3.3 - 0.15), mat=pick(a, WOOD_MIX))
    plank_wall(a, (5.35, -2.3, 0), (0, 1, 0), 4.6, 3.0, thick=0.25, pw=0.8, zjit=0.0)
    plank_wall(a, (4.0, -0.6, 0), (0, 1, 0), 3.0, 3.0, thick=0.25, pw=0.8, zjit=0.0)
    sq_beam(a, (5.55, -2.4, 0.35), (5.55, 2.3, 0.35), 0.35, 0.45)
    # raised back shelf at the left end
    for k in range(3):
        a.plank((3.2 - a.rng.uniform(0, 0.3), 0.42, 0.3), loc=(-4.0, 1.55 + 0.45 * k, 3.95),
                mat=pick(a, WOOD_MIX))
    plank_wall(a, (-5.5, 1.35, 0), (1, 0, 0), 3.0, 3.8, thick=0.25, pw=0.75, zjit=0.0)
    obj, _ = done(a)
    return obj


# ---------------------------------------------------------------------------
# PrimitiveShelter 10 x 10 x 8
# ---------------------------------------------------------------------------


def build_shelter():
    """Open-fronted A-frame hut: two long thatch slopes down to low plank side
    walls on crossed log A-frames, plank back wall inside, ridge beam on top."""
    a = fk.Asset("PrimitiveShelter", "Buildings")
    TOP, SL = 6.55, 0.75   # thatch underside at the ridge / slope

    def plane(x):
        return TOP - SL * abs(x)

    PX, WX, WF, WB = 3.4, 4.3, -3.6, 3.4   # front posts, side walls, front / back lines
    # front posts on stone footings with rope coils; back corner posts
    for s in (-1, 1):
        cblock(a, (1.45, 1.45, 0.8), (s * PX, WF, 0.4), "y", "stone")
        sq_post(a, s * PX, WF, 0.95, plane(PX) + 0.2 - 0.8, z0=0.8)
        rings(a, (s * PX, WF, 1.3), 0.56, count=2)
        rings(a, (s * PX, WF, plane(PX) - 0.7), 0.56, count=2)
        sq_post(a, s * WX, WB, 0.85, plane(WX) + 0.1)
        sq_post(a, s * WX, WF + 0.4, 0.8, plane(WX) + 0.1)
    cblock(a, (1.3, 1.3, 0.7), (0, WB - 0.35, 0.35), "y", "stone")
    sq_post(a, 0, WB - 0.35, 0.95, TOP - 0.2 - 0.7, z0=0.7)
    rings(a, (0, WB - 0.35, 1.35), 0.58, count=2)
    rings(a, (0, WB - 0.35, 4.3), 0.58, count=2)
    # back wall following the roof, low side walls, each with rails
    plank_wall(a, (-WX + 0.4, WB + 0.1, 0), (1, 0, 0), 2 * WX - 0.8, 0,
               hfun=lambda c: plane(c.x) - 0.15, pw=0.8, thick=0.3, mats=INSIDE)
    sq_beam(a, (-WX, WB - 0.3, 1.5), (WX, WB - 0.3, 1.5), 0.38, 0.42)
    sq_beam(a, (-2.6, WB - 0.3, 4.3), (2.6, WB - 0.3, 4.3), 0.38, 0.42)
    for s in (-1, 1):
        plank_wall(a, (s * (WX + 0.1), WF + 0.75, 0), (0, 1, 0), WB - WF - 1.1, plane(WX) - 0.05,
                   pw=0.8, thick=0.3, mats=INSIDE)
        for z in (0.9, plane(WX) - 0.45):
            sq_beam(a, (s * (WX - 0.22), WF + 0.4, z), (s * (WX - 0.22), WB, z), 0.36, 0.4)
    # two long, dense thatch slopes meeting at the ridge, eaves just above the walls,
    # with a shaggy verge poking out past the front A-frame
    ex = 4.95
    Ls = ex * math.sqrt(1 + SL * SL)
    for s in (-1, 1):
        straw(a, (s * 0.05, -0.1, TOP), (0, 1, 0), (s, 0, -SL), 9.4, 9.4, Ls, courses=5,
              gap=0.36, sw=(0.36, 0.55), base_t=1.0, lift=0.65, jag=0.5, ov=0.6, inset=0.5,
              eave_len=(0.7, 1.2), hang=-0.2,
              course_len=(1.0, 1.3), sides=(-1,), side_dir=(0.7, 0.45, 1.0), side_len=(0.9, 1.5),
              side_gap=0.35)
    # A-frame logs crossing above the ridge, front and back, rope wraps on the front pair
    for y in (-4.85, 4.75):
        for s in (-1, 1):
            base = Vector((s * 5.8, y + 0.3 * s, 0.0))
            top = Vector((-s * 1.35, y + 0.3 * s, 8.9))
            log(a, base, top, 0.57)
            if y < 0:
                d = (top - base).normalized()
                rings(a, base + d * 1.6, 0.57, axis=d, count=2)
                rings(a, base + d * (4.6 if s < 0 else 3.9), 0.57, axis=d, count=3)
        lash(a, (0, y - 0.1, 7.22), size=0.95, thickness=0.18)
    # round ridge log in the crotches + square ridge beam on top, both with cut ends
    log(a, (0, -6.0, 7.5), (0, 5.6, 7.5), 0.6)
    sq_beam(a, (0, -5.4, 8.35), (0, 5.2, 8.35), 1.05, 0.95)
    rings(a, (0, -4.1, 7.95), 0.66, axis=(0, 1, 0), count=1)
    obj, _ = done(a)
    return obj


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

VIEWS = {  # per-asset camera (azimuth, elevation, framing margin) to match the sheet
    "VaultHall": (18, 20, 0.97),
    "AncestralForge": (14, 23, 0.95),
    "DeployGate": (-15, 17, 0.95),
    "ThatchMarketStall": (-28, 20, 0.97),
    "HideMarketStall": (20, 20, 0.97),
    "PrimitiveShelter": (17, 17, 0.97),
}


def render_sheet_views(objs, path, cols=3, cell=(560, 420)):
    base, _ = os.path.splitext(path)
    cell_paths = []
    scene = bpy.context.scene
    fk._studio(scene)
    scene.render.resolution_x, scene.render.resolution_y = cell
    scene.render.resolution_percentage = 100
    try:
        scene.eevee.taa_render_samples = 32
    except AttributeError:
        pass
    for i, o in enumerate(objs):
        az, el, margin = VIEWS.get(o.name, (fk.DEFAULT_AZIMUTH, fk.DEFAULT_ELEVATION, 1.1))
        p = f"{base}_cells/{i + 1:02d}_{o.name}.png"
        for other in objs:
            other.hide_render = other is not o
        fk.frame(o, az, el, margin=margin)
        scene.render.filepath = p
        os.makedirs(os.path.dirname(p), exist_ok=True)
        bpy.ops.render.render(write_still=True)
        cell_paths.append(p)
    for other in objs:
        other.hide_render = False
    rows = math.ceil(len(objs) / cols)
    w, h = cell
    img_px = np.ones((rows * h, cols * w, 4), dtype=np.float32)
    for i, p in enumerate(cell_paths):
        img = bpy.data.images.load(p, check_existing=False)
        px = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], 4)
        r, c = divmod(i, cols)
        y0 = (rows - 1 - r) * h
        img_px[y0:y0 + h, c * w:c * w + w] = px[:h, :w]
        bpy.data.images.remove(img)
    out = bpy.data.images.new("FB_Sheet", cols * w, rows * h, alpha=True)
    out.pixels = img_px.ravel()
    out.filepath_raw = path
    out.file_format = "PNG"
    out.save()
    bpy.data.images.remove(out)
    return path


def main():
    fk.reset_file()
    objs = [build_vault_hall(), build_forge(), build_deploy_gate(), build_thatch_stall(),
            build_hide_stall(), build_shelter()]
    for o in objs:
        print(f"BUILT {o.name}: tris={o['tris']} studs={o['studs']}")
        for sk in vfx.sockets(o):
            print(f"    SOCKET {sk.name} {sk['vfx_kind']} at {tuple(round(c, 2) for c in sk.location)}")
        if os.environ.get("FB_STATS") == "1":
            cnt = {}
            for poly in o.data.polygons:
                m = o.data.materials[poly.material_index].name
                cnt[m] = cnt.get(m, 0) + len(poly.vertices) - 2
            print("   ", sorted(cnt.items(), key=lambda kv: -kv[1]))
    fk.layout_row(objs)
    fk.save(os.path.join(ROOT, "assets", "01_buildings.blend"))
    if os.environ.get("FB_NORENDER") != "1":
        render_sheet_views(objs, os.path.join(ROOT, "renders", "01_buildings.png"), cols=3)
    print("DONE 01_buildings")


main()
