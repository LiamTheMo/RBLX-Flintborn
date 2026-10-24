"""Build sheet 03 Furnishings: chests, cabinet, totem, boards, anvils, furnace, containers.

    blender --background --factory-startup --python art/blender/scripts/build_03_furnishings.py
"""

import math
import os
import sys

ROOT = "D:/Projects/Roblox/RBLX-Flintborn/art/blender"
sys.path.insert(0, os.path.join(ROOT, "lib"))

import bmesh  # noqa: E402
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402

import flintkit as fk  # noqa: E402
import vfx  # noqa: E402

PI = math.pi
FRONT = (PI / 2, 0, 0)  # turns a part's local +Z to face -Y (the front)
BACK = (-PI / 2, 0, 0)  # local +Z to +Y
RIGHT = (0, PI / 2, 0)  # local +Z to +X
LEFT = (0, -PI / 2, 0)  # local +Z to -X
YZ = (PI / 2, 0, PI / 2)  # poly_prism: local (x, y) -> world (y, z), extrude along +X
CAT = "Furnishings"


# ---------------------------------------------------------------------------
# Local helpers (all take an fk.Asset)
# ---------------------------------------------------------------------------


def tint(a, var=None):
    v = a.tint_var if var is None else var
    return 1.0 + a.rng.uniform(-v, v)


def rings_to_faces(a, rings, wrap=False, cap0=True, cap1=True):
    """Bridge consecutive point rings (equal length, each a closed loop) with quads."""
    bm = a.bm
    vs = [[bm.verts.new(p) for p in ring] for ring in rings]
    n, m = len(vs[0]), len(vs)
    for i in range(m if wrap else m - 1):
        r1, r2 = vs[i], vs[(i + 1) % m]
        for j in range(n):
            jj = (j + 1) % n
            bm.faces.new((r1[j], r1[jj], r2[jj], r2[j]))
    if not wrap:
        if cap0:
            bm.faces.new(list(reversed(vs[0])))
        if cap1:
            bm.faces.new(vs[-1])
    return [v for r in vs for v in r]


def loft(a, rings, mat, t=None, wrap=False, caps=True):
    return a._finish(rings_to_faces(a, rings, wrap, caps, caps), mat, t)


def lathe(a, prof, sides, mat, off=None, cap0=True, cap1=True, t=None):
    """Revolve a (r, z) profile; by default a flat facet faces -Y."""
    off = -PI / 2 - PI / sides if off is None else off
    rings = [[(r * math.cos(off + 2 * PI * j / sides), r * math.sin(off + 2 * PI * j / sides), z)
              for j in range(sides)] for r, z in prof]
    return a._finish(rings_to_faces(a, rings, False, cap0, cap1), mat, t)


def tim(a, lo, hi, mat="wood", end_mat="wood_end", ends=True, t=None):
    """Axis-aligned hewn timber between corners lo/hi, with lighter cut ends on its long axis."""
    size = [hi[i] - lo[i] for i in range(3)]
    c = [(hi[i] + lo[i]) / 2 for i in range(3)]
    t = tint(a) if t is None else t
    m = min(size)
    v = a.box(size, loc=c, mat=mat, bevel=m * 0.13, jitter=m * 0.035, tint=t)
    if ends:
        ax = size.index(max(size))
        sides = [-1, 1] if ends is True else [ends]
        for s in sides:
            cs = [size[i] * 0.7 for i in range(3)]
            cs[ax] = 0.02
            cl = list(c)
            cl[ax] = c[ax] + s * size[ax] / 2
            v += a.box(cs, loc=cl, mat=end_mat, tint=t)
    return v


# -- painted wood grain ------------------------------------------------------
# Each streak is a thin tapered strip lying just proud of a face, in a darker tone of the
# wood under it (2-4 tris). A loose helper vert inside the solid travels with the part
# through later transforms, so done() can point the strip's normal outward.

GRAIN = {"wood": "wood_dark", "wood_light": "wood", "wood_end": "wood_light", "wood_dark": "charcoal",
         "bark": "wood_dark"}


def streak(a, pts, side, w, mat, inside):
    bm = a.bm
    k = len(pts)
    rows = []
    for i, p in enumerate(pts):
        f = math.sin(PI * i / (k - 1))
        rows.append([bm.verts.new(p)] if f < 1e-3 else
                    [bm.verts.new(p + side * (w / 2 * f)), bm.verts.new(p - side * (w / 2 * f))])
    faces = []
    for r0, r1 in zip(rows, rows[1:]):
        if len(r0) == 1:
            faces.append(bm.faces.new((r0[0], r1[0], r1[1])))
        elif len(r1) == 1:
            faces.append(bm.faces.new((r0[0], r1[0], r0[1])))
        else:
            faces.append(bm.faces.new((r0[0], r1[0], r1[1], r0[1])))
    h = bm.verts.new(inside)
    a.__dict__.setdefault("_streaks", []).append((faces, h))
    verts = [v for r in rows for v in r]
    a._finish(verts, mat, tint=1.0 + a.rng.uniform(-0.05, 0.05))
    return verts + [h]


def grain_lines(a, c, u, v, n, Lu, Lv, mat, count, off=0.012, inside=None):
    """`count` streaks on the face centred at c (long axis u, across v, normal n)."""
    out = []
    inside = Vector(inside) if inside is not None else c - n * 0.02
    for _ in range(count):
        L = Lu * a.rng.uniform(0.35, 0.75)
        x0 = a.rng.uniform(-Lu / 2 + 0.06, max(-Lu / 2 + 0.06, Lu / 2 - 0.06 - L))
        y0 = Lv * a.rng.uniform(-0.3, 0.3)
        w = min(0.045, Lv * 0.16) * a.rng.uniform(0.75, 1.25)
        wob = [a.rng.uniform(-1, 1) * w * 0.7 for _ in range(4)]
        pts = [c + n * off + u * (x0 + L * i / 3) + v * (y0 + wob[i]) for i in range(4)]
        out += streak(a, pts, v, w, mat, inside)
    return out


def grain_box(a, size, loc=(0, 0, 0), mat="wood", faces="-y+y-x+x+z", dens=1.0, off=0.012):
    """Grain on the listed faces of an axis-aligned box (long axis of each face)."""
    gm = GRAIN.get(mat)
    if not gm:
        return []
    out = []
    loc = Vector(loc)
    for i in range(0, len(faces), 2):
        sg = 1 if faces[i] == "+" else -1
        ax = "xyz".index(faces[i + 1])
        oth = [k for k in range(3) if k != ax]
        ku = max(oth, key=lambda k: size[k])
        kv = [k for k in oth if k != ku][0]
        Lu, Lv = size[ku], size[kv]
        if Lu < 0.45 or Lv < 0.12:
            continue
        cnt = max(1, min(3, round(Lv / 0.32 * dens)))
        n = Vector([sg if k == ax else 0 for k in range(3)])
        u = Vector([1 if k == ku else 0 for k in range(3)])
        v = Vector([1 if k == kv else 0 for k in range(3)])
        out += grain_lines(a, loc + n * (size[ax] / 2), u, v, n, Lu, Lv, gm, cnt, off=off, inside=loc)
    return out


def gplank(a, size, loc=(0, 0, 0), rot=(0, 0, 0), mat="wood", faces="-y+y-x+x+z", dens=1.0, bevel=None,
           jitter=None):
    """Plank with painted grain on the listed (local) faces."""
    v = a.plank(size, mat=mat, bevel=bevel, jitter=jitter)
    v += grain_box(a, size, mat=mat, faces=faces, dens=dens, off=0.008 + min(size) * 0.04)
    a.transform(v, loc, rot)
    return v


def gtim(a, lo, hi, mat="wood", faces="-y+y-x+x+z", dens=1.0, **kw):
    """Hewn timber with painted grain."""
    v = tim(a, lo, hi, mat=mat, **kw)
    size = [hi[i] - lo[i] for i in range(3)]
    c = [(hi[i] + lo[i]) / 2 for i in range(3)]
    v += grain_box(a, size, c, mat=mat, faces=faces, dens=dens, off=0.01 + min(size) * 0.04)
    return v


def grain_log(a, length, radius, sides, mat, count=3, z0=0.0):
    """Streaks along a log lying on local +Z from z0 (bmesh cone facets: first vertex at +Y)."""
    gm = GRAIN.get(mat)
    if not gm:
        return []
    out = []
    d = radius * math.cos(PI / sides) + 0.012
    fw = 2 * radius * math.sin(PI / sides)
    for j in a.rng.sample(range(sides), min(count, sides)):
        ph = PI / 2 + (j + 0.5) * 2 * PI / sides
        n = Vector((math.cos(ph), math.sin(ph), 0))
        side = Vector((-math.sin(ph), math.cos(ph), 0))
        c = n * d + Vector((0, 0, z0 + length / 2))
        out += grain_lines(a, c, Vector((0, 0, 1)), side, n, length * 0.9, fw, gm, 1, off=0.0,
                           inside=(0, 0, z0 + length / 2))
    return out


def gbeam(a, p1, p2, radius, sides=7, mat="wood", grain=3, overhang=0.0, **kw):
    """fk beam plus grain streaks along its facets."""
    v = a.beam(p1, p2, radius, sides=sides, mat=mat, overhang=overhang, **kw)
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    length = d.length + 2 * overhang
    g = grain_log(a, length, radius, sides, mat, count=grain)
    bmesh.ops.translate(a.bm, vec=(0, 0, -overhang), verts=g)
    a.transform(g, p1, d.to_track_quat("Z", "Y").to_euler())
    return v + g


def rope_wrap(a, x, y, r, z, count=2, th=0.06, seg=8, rseg=4):
    out = []
    for i in range(count):
        out += a.torus(r + th * 0.6, th, loc=(x, y, z + i * th * 1.9), seg=seg, rseg=rseg,
                       mat="rope", tint=tint(a, 0.05))
    return out


def front_prism(a, pts, y, depth, mat, t=None):
    """Flat shape drawn in world (x, z) on the plane y, extruded toward -Y."""
    return a.poly_prism(pts, depth, loc=(0, y, 0), rot=FRONT, mat=mat, tint=t)


def rot2(pts, ang, cx, cz):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + x * ca - z * sa, cz + x * sa + z * ca) for x, z in pts]


def keyhole_plate(a, x, y, z, w=0.5, h=0.62, rr=0.05):
    """Iron lock plate on the front plane y, with keyhole and corner rivets."""
    a.box((w, 0.07, h), loc=(x, y - 0.035, z), mat="iron_dark", bevel=0.025)
    a.box((w * 0.7, 0.03, h * 0.18), loc=(x, y - 0.075, z + h * 0.38), mat="iron", bevel=0.01)
    a.cyl(w * 0.15, w * 0.15, 0.03, 6, loc=(x, y - 0.07, z + h * 0.06), rot=FRONT, mat="charcoal")
    a.poly_prism([(-w * 0.07, -h * 0.28), (w * 0.07, -h * 0.28), (w * 0.035, 0.02), (-w * 0.035, 0.02)],
                 0.03, loc=(x, y - 0.07, z + h * 0.06), rot=FRONT, mat="charcoal")
    for sx in (-1, 1):
        for sz in (-1, 1):
            rivet_front(a, x + sx * (w / 2 - rr * 1.4), y - 0.07, z + sz * (h / 2 - rr * 1.4), r=rr)


def ell(D, Hl, z0, t, grow=0.0, e=1.0):
    """Point on a chest lid's profile, t=0 front ... t=pi back, in (y, z). e<1 squares the dome off."""
    c, s = math.cos(t), math.sin(t)
    c = math.copysign(abs(c) ** e, c)
    s = abs(s) ** e
    return (-(D / 2 + grow) * c, z0 + (Hl + grow) * s)


def chest_lid(a, W, D, z0, Hl, n=4, pt=0.12, ct=0.13, mat="wood", cap_mat="wood", core=True,
              segs=12, e=1.0, grain=True):
    """Domed plank lid: planks along X laid on the profile, solid end caps."""
    out = []
    for i in range(n):
        p0 = Vector(ell(D, Hl, z0, PI * i / n, e=e))
        p1 = Vector(ell(D, Hl, z0, PI * (i + 1) / n, e=e))
        tan = p1 - p0
        L = tan.length
        tan.normalize()
        nrm = Vector((-tan.y, tan.x))
        ang = math.atan2(-nrm.x, nrm.y)
        c = (p0 + p1) / 2 + nrm * (pt / 2)
        size = (W - 2 * ct + 0.02, L + 0.02, pt)
        if grain:
            out += gplank(a, size, loc=(0, c.x, c.y), rot=(ang, 0, 0), mat=mat, faces="+z-z" if not core else "+z")
        else:
            out += a.plank(size, loc=(0, c.x, c.y), rot=(ang, 0, 0), mat=mat)
    arc = [ell(D, Hl, z0, PI * k / segs, e=e) for k in range(segs + 1)]
    if core:
        out += a.poly_prism(list(reversed(arc)), W - 2 * ct, loc=(-W / 2 + ct, 0, 0), rot=YZ,
                            mat="wood_dark")
    cap = list(reversed([ell(D, Hl, z0, PI * k / segs, grow=pt * 0.85, e=e) for k in range(segs + 1)]))
    for x0 in (-W / 2, W / 2 - ct):
        out += a.poly_prism(cap, ct, loc=(x0, 0, 0), rot=YZ, mat=cap_mat)
    return out


def strap(a, x, w, D, z0, Hl, zb, th, mat, pt=0.12, body_half=None, segs=10, rivet_every=2,
          rivet_mat="iron_dark", rr=0.06, back=True, e=1.0):
    """Band over the lid profile (and down the front/back of the body to zb)."""
    bd = body_half if body_half is not None else D / 2 + pt
    prof = []
    if zb is not None:
        prof += [(-bd, zb), (-bd, z0 - 0.02)]
    prof += [ell(D, Hl, z0, PI * k / segs, grow=pt, e=e) for k in range(segs + 1)]
    if zb is not None and back:
        prof += [(bd, z0 - 0.02), (bd, zb)]
    P = [Vector(p) for p in prof]
    rings, frames = [], []
    for i, p in enumerate(P):
        tvec = P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]
        tvec.normalize()
        nrm = Vector((-tvec.y, tvec.x))
        inn, out = p - nrm * 0.01, p + nrm * th
        rings.append([(x - w / 2, inn.x, inn.y), (x + w / 2, inn.x, inn.y),
                      (x + w / 2, out.x, out.y), (x - w / 2, out.x, out.y)])
        frames.append((out, nrm))
    v = loft(a, rings, mat)
    if rivet_every:
        for i in range(1, len(P) - 1, rivet_every):
            out, nrm = frames[i]
            ang = math.atan2(-nrm.x, nrm.y)
            v += rivet(a, (x, out.x, out.y), (ang, 0, 0), r=rr, mat=rivet_mat)
    return v


def hinge_rotate(a, verts, hinge_y, hinge_z, angle):
    import mathutils
    bmesh.ops.rotate(a.bm, verts=verts, cent=(0, hinge_y, hinge_z),
                     matrix=mathutils.Matrix.Rotation(angle, 3, "X"))


def done(a):
    bm = a.bm
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for faces, h in a.__dict__.get("_streaks", []):
        f0 = faces[0]
        f0.normal_update()
        if (f0.calc_center_median() - h.co).dot(f0.normal) < 0:
            for f in faces:
                f.normal_flip()
        bm.verts.remove(h)
    obj = a.finish()
    d = obj.dimensions
    print(f"FB03 {obj.name}: tris={obj['tris']} studs={obj['studs']} exact={d.x:.3f},{d.y:.3f},{d.z:.3f}")
    return obj


def rivet(a, loc, rot=(0, 0, 0), r=0.06, mat="iron_dark"):
    """Cheap square rivet head (12 tris)."""
    return a.cyl(r * 1.15, r * 0.6, r * 0.65, 4, loc=loc, rot=rot, mat=mat)


def bolt(a, loc, rot=(0, 0, 0), r=0.09, mat="iron_dark"):
    """Round domed bolt head (6 sides)."""
    v = a.cyl(r, r * 0.9, r * 0.35, 6, mat=mat, tint=1.0)
    v += a.cyl(r * 0.9, r * 0.35, r * 0.3, 6, loc=(0, 0, r * 0.35), mat=mat, tint=1.08)
    a.transform(v, loc, rot)
    return v


def edge_band(a, W, D, z0, h, th=0.06, mat="iron_dark", rivets=6, rr=0.055):
    """Iron band right round a box footprint at height z0..z0+h, rivets on the front and back."""
    a.box((W + 2 * th, th, h), loc=(0, -D / 2 - th / 2, z0), base=True, mat=mat, bevel=0.015)
    a.box((W + 2 * th, th, h), loc=(0, D / 2 + th / 2, z0), base=True, mat=mat, bevel=0.015)
    for sx in (-1, 1):
        a.box((th, D, h), loc=(sx * (W / 2 + th / 2), 0, z0), base=True, mat=mat, bevel=0.015)
    for k in range(rivets):
        x = -W / 2 + W / (2 * rivets) + k * W / rivets
        rivet(a, (x, -D / 2 - th, z0 + h / 2), FRONT, r=rr)
        rivet(a, (x, D / 2 + th, z0 + h / 2), BACK, r=rr)


def sweep(a, pts, radii, mat, sides=4, closed=False, phase=PI / 4, up=None, t=None, caps=True):
    """Tube along a 3D polyline; radii is a scalar, a list, or a list of (r_n, r_b) pairs."""
    P = [Vector(p) for p in pts]
    n = len(P)
    if isinstance(radii, (int, float)):
        radii = [radii] * n
    rings = []
    for i, p in enumerate(P):
        if closed:
            tv = P[(i + 1) % n] - P[i - 1]
        else:
            tv = P[min(i + 1, n - 1)] - P[max(i - 1, 0)]
        tv.normalize()
        u = Vector(up) if up is not None else (Vector((0, 0, 1)) if abs(tv.z) < 0.9 else Vector((1, 0, 0)))
        nrm = tv.cross(u).normalized()
        bi = nrm.cross(tv).normalized()
        rr = radii[i] if isinstance(radii[i], (tuple, list)) else (radii[i], radii[i])
        rings.append([p + rr[0] * math.cos(phase + 2 * PI * j / sides) * nrm
                      + rr[1] * math.sin(phase + 2 * PI * j / sides) * bi for j in range(sides)])
    verts = rings_to_faces(a, rings, wrap=closed, cap0=caps, cap1=caps)
    return a._finish(verts, mat, t)


def glyph(a, kind, cx, cy, s, stroke, depth, loc=(0, 0, 0), rot=(0, 0, 0), ang=0.0, mat="ink"):
    """Bold blocky rune made of strokes in a [-1, 1] box, scaled by s around (cx, cy)."""
    lib = [
        [[(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)], [(0, 0.35), (0, -0.35)]],
        [[(-1, 1), (-1, -1)], [(-1, 1), (1, 1)], [(-1, 0), (0.5, 0)], [(-1, -1), (1, -1)]],
        [[(-1, 1), (-1, -1), (1, -1), (1, 1)], [(0, 1), (0, -0.3)]],
        [[(1, 1), (-1, 1), (-1, -1), (1, -1), (1, 0.15), (-0.2, 0.15)]],
        [[(-1, 1), (1, 1), (-1, -1), (1, -1)]],
        [[(0, 1), (0, -1)], [(-1, 0.4), (0, 1), (1, 0.4)], [(-0.8, -0.4), (0.8, -0.4)]],
    ]
    out = []
    ca, sa = math.cos(ang), math.sin(ang)
    for line in lib[kind % len(lib)]:
        pts = [(cx + (x * ca - y * sa) * s, cy + (x * sa + y * ca) * s) for x, y in line]
        out += a.strip(pts, stroke, depth, loc=loc, rot=rot, mat=mat)
    return out


def rivet_front(a, x, y, z, r=0.06, mat="iron_dark"):
    return rivet(a, (x, y, z), FRONT, r=r, mat=mat)


def chunk(a, size, loc, rot=(0, 0, 0), mat="stone", ch=None, t=None, flat_top=False):
    """Chiselled block (20 tris): top edges chamfered, slight jitter. flat_top keeps the top face level."""
    hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
    c = ch if ch is not None else min(size) * 0.22

    def ring(ix, iy, z):
        return [(-ix, -iy, z), (ix, -iy, z), (ix, iy, z), (-ix, iy, z)]

    rings = [ring(hx - c * 0.4, hy - c * 0.4, -hz), ring(hx, hy, hz - c), ring(hx - c, hy - c, hz)]
    verts = rings_to_faces(a, rings)
    j = min(size) * 0.07
    for i, v in enumerate(verts):
        v.co += Vector((a.rng.uniform(-j, j), a.rng.uniform(-j, j), a.rng.uniform(-j, j)))
        if flat_top and i >= 8:
            v.co.z = hz
        if flat_top and i < 4:
            v.co.z = -hz
    a.transform(verts, loc, rot)
    return a._finish(verts, mat, t, 0.0, 0.05)


# ---------------------------------------------------------------------------
# Chests and cabinet
# ---------------------------------------------------------------------------


def chest_body(a, W, D, H, rows=3, pt=0.12, hollow=False, mat="wood"):
    rh = H / rows
    for r in range(rows):
        zc = rh * r + rh / 2
        h = rh - 0.05
        for sy in (-1, 1):
            gplank(a, (W, pt, h), loc=(0, sy * (D / 2 - pt / 2), zc), mat=mat, faces="-y" if sy < 0 else "+y")
        for sx in (-1, 1):
            gplank(a, (pt, D - 2 * pt + 0.02, h), loc=(sx * (W / 2 - pt / 2), 0, zc), mat=mat,
                   faces="-x" if sx < 0 else "+x")
    if not hollow:
        a.box((W - 2 * pt + 0.02, D - 2 * pt + 0.02, H - 0.02), loc=(0, 0, 0.01), base=True,
              mat="wood_dark")
        return
    # dark backer boards, then inner plank lining with visible seams
    bk = 0.03
    for sy in (-1, 1):
        a.box((W - 2 * pt, bk, H - 0.04), loc=(0, sy * (D / 2 - pt - bk / 2), 0.02), base=True, mat="wood_dark")
    for sx in (-1, 1):
        a.box((bk, D - 2 * pt, H - 0.04), loc=(sx * (W / 2 - pt - bk / 2), 0, 0.02), base=True, mat="wood_dark")
    lt = 0.07
    iw, idp = W - 2 * pt - 2 * bk, D - 2 * pt - 2 * bk
    for r in range(rows):
        zc = rh * r + rh / 2
        h = rh - 0.06
        for sy in (-1, 1):
            sz, c = (iw - 2 * lt, lt, h), (0, sy * (idp / 2 - lt / 2), zc)
            a.box(sz, loc=c, mat="wood", jitter=0.004)
            grain_box(a, sz, c, mat="wood", faces="+y" if sy < 0 else "-y", dens=0.7)
        for sx in (-1, 1):
            sz, c = (lt, idp, h), (sx * (iw / 2 - lt / 2), 0, zc)
            a.box(sz, loc=c, mat="wood", jitter=0.004)
            grain_box(a, sz, c, mat="wood", faces="+x" if sx < 0 else "-x", dens=0.7)
    a.box((iw, idp, 0.08), loc=(0, 0, 0.0), base=True, mat="wood_dark")
    n = 4
    fw = (iw - 2 * lt) / n
    for i in range(n):
        sz, c = (fw - 0.05, idp - 2 * lt, 0.12), (-iw / 2 + lt + fw * (i + 0.5), 0, 0.14)
        a.box(sz, loc=c, mat="wood", jitter=0.004)
        grain_box(a, sz, c, mat="wood", faces="+z")


def l_prism(a, sx, sy, A, B, t, w, z0, h, mat, tint_=None):
    """L-shaped corner piece round the body corner (sx*A, sy*B): arms of length w, thickness t."""
    uv = [(A + t - w, B), (A + t - w, B + t), (A + t, B + t), (A + t, B + t - w), (A, B + t - w), (A, B)]
    pts = [(sx * u, sy * v) for u, v in uv]
    if sx * sy < 0:
        pts.reverse()
    return a.poly_prism(pts, h, loc=(0, 0, z0), mat=mat, tint=tint_)


def corner_guards(a, W, D, Hb, gw=0.3, gt=0.08, cap_h=0.34, mat="wood_light", rr=0.05, rivets=1,
                  cap_mat=None, guard=True):
    """Vertical L-shaped corner guards with chunky caps at the bottom and the top of the body."""
    cap_mat = cap_mat or mat
    A, B = W / 2, D / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            t = tint(a)
            if guard:
                l_prism(a, sx, sy, A, B, gt, gw, 0.02, Hb - 0.04, mat, t)
                gm = GRAIN[mat]
                grain_lines(a, Vector((sx * (A + gt - gw / 2), sy * (B + gt), Hb / 2)), Vector((0, 0, 1)),
                            Vector((1, 0, 0)), Vector((0, sy, 0)), Hb - cap_h * 2, gw, gm, 1, off=0.008)
                grain_lines(a, Vector((sx * (A + gt), sy * (B + gt - gw / 2), Hb / 2)), Vector((0, 0, 1)),
                            Vector((0, 1, 0)), Vector((sx, 0, 0)), Hb - cap_h * 2, gw, gm, 1, off=0.008)
            e = 0.05
            for zc in (cap_h / 2, Hb - cap_h / 2):
                l_prism(a, sx, sy, A - 0.005, B - 0.005, gt + e, gw + e, zc - cap_h / 2, cap_h, cap_mat, t * 1.04)
                for j in range(rivets):
                    dz = 0 if rivets == 1 else (j - (rivets - 1) / 2) * cap_h * 0.45
                    rivet(a, (sx * (A + gt + e - (gw + e) / 2), sy * (B + gt + e), zc + dz), FRONT if sy < 0 else BACK,
                          r=rr)
                    rivet(a, (sx * (A + gt + e), sy * (B + gt + e - (gw + e) / 2), zc + dz),
                          RIGHT if sx > 0 else LEFT, r=rr)


def small_chest():
    a = fk.Asset("SmallChest", CAT)
    W, D, Hb, pt, th = 2.84, 1.9, 1.3, 0.12, 0.08
    e = 0.6
    Dl = D - 2 * pt * 0.9
    Hl = 2.2 - Hb - pt - th
    chest_body(a, W, D, Hb, rows=3, pt=pt)
    corner_guards(a, W, D, Hb, gw=0.3, gt=0.08, cap_h=0.34, rr=0.05)
    chest_lid(a, W + 0.06, Dl, Hb, Hl, n=5, pt=pt, ct=0.14, cap_mat="wood", e=e)
    for sx in (-1, 1):
        strap(a, sx * (W / 2 - 0.2), 0.44, Dl, Hb, Hl, None, th, "wood_light", pt=pt, rivet_every=0, e=e)
        # rivets at the lid's front corners and on the crown
        for t, dx in ((0.18, 0.0), (1.45, 0.0)):
            p = Vector(ell(Dl, Hl, Hb, t, grow=pt + th, e=e))
            q = Vector(ell(Dl, Hl, Hb, t + 0.05, grow=pt + th, e=e))
            nrm = Vector((-(q - p).y, (q - p).x)).normalized()
            rivet(a, (sx * (W / 2 - 0.2) + dx, p.x, p.y), (math.atan2(-nrm.x, nrm.y), 0, 0), r=0.05)
    # lock plate hanging from the lid seam, hasp tab on the lid
    keyhole_plate(a, 0, -D / 2, Hb - 0.34, w=0.52, h=0.66, rr=0.045)
    a.box((0.3, 0.05, 0.26), loc=(0, -Dl / 2 - pt - 0.03, Hb + 0.12), mat="iron", bevel=0.015)
    return done(a)


def large_chest():
    a = fk.Asset("LargeChest", CAT)
    W, D, Hb, pt, th = 4.1, 2.6, 1.95, 0.14, 0.1
    e = 0.62
    Dl = D - 2 * pt * 0.9
    Hl = 3.2 - Hb - pt - th
    chest_body(a, W, D, Hb, rows=4, pt=pt)
    chest_lid(a, W, Dl, Hb, Hl, n=5, pt=pt, ct=0.16, e=e)
    bh = 0.36  # iron rim band round the top of the body
    edge_band(a, W, D, Hb - bh, bh, th=0.08, rivets=7, rr=0.085)
    # lid straps over both ends and the centre
    for x, w in ((-(W / 2 - 0.25), 0.5), (0.0, 0.5), (W / 2 - 0.25, 0.5)):
        strap(a, x, w, Dl, Hb, Hl, Hb - bh + 0.02, th, "iron_dark", pt=pt, body_half=D / 2 + 0.08,
              rivet_every=2, rr=0.085, e=e)
    # L-shaped iron corner straps down every vertical edge, rivets on both faces
    cw, ct_ = 0.42, 0.07
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.box((cw, ct_, Hb - bh), loc=(sx * (W / 2 + ct_ - cw / 2), sy * (D / 2 + ct_ / 2), 0), base=True,
                  mat="iron_dark", bevel=0.018)
            a.box((ct_, cw, Hb - bh), loc=(sx * (W / 2 + ct_ / 2), sy * (D / 2 - cw / 2), 0), base=True,
                  mat="iron_dark", bevel=0.018)
            for zz in (0.2, 0.72, 1.24):
                rivet(a, (sx * (W / 2 + ct_ - cw / 2), sy * (D / 2 + ct_), zz), FRONT if sy < 0 else BACK, r=0.09)
                rivet(a, (sx * (W / 2 + ct_), sy * (D / 2 - cw / 2), zz), RIGHT if sx > 0 else LEFT, r=0.09)
    keyhole_plate(a, 0, -D / 2 - 0.08, Hb - 0.3, w=0.86, h=1.12, rr=0.07)
    return done(a)


def open_chest():
    a = fk.Asset("OpenChest", CAT)
    W, D, Hb, pt, th = 3.6, 2.2, 1.8, 0.13, 0.07
    e = 0.6
    Dl = D - 2 * pt * 0.9
    Hl = 0.8
    chest_body(a, W, D, Hb, rows=3, pt=pt, hollow=True)
    for sy in (-1, 1):
        gplank(a, (W - 0.1, pt + 0.04, 0.1), loc=(0, sy * (D / 2 - pt / 2), Hb + 0.03), mat="wood_light", faces="+z")
    for sx in (-1, 1):
        gplank(a, (pt + 0.04, D - 2 * pt, 0.1), loc=(sx * (W / 2 - pt / 2), 0, Hb + 0.03), mat="wood_light",
               faces="+z")
    corner_guards(a, W, D, Hb + 0.06, gw=0.32, gt=0.08, cap_h=0.38, rr=0.06)
    keyhole_plate(a, 0, -D / 2, Hb - 0.5, w=0.56, h=0.7, rr=0.05)
    # hinges: pale iron leaves on the back, knuckle along the hinge line
    hy, hz = Dl / 2 + pt * 0.3, Hb + 0.09
    for sx in (-1, 1):
        a.box((0.36, 0.05, 0.42), loc=(sx * 0.95, D / 2 + 0.025, Hb - 0.12), mat="iron_edge", bevel=0.012)
        a.cyl(0.06, 0.06, 0.36, 6, loc=(sx * 0.95 - 0.18, hy + 0.12, hz), rot=RIGHT, mat="iron_edge")
    # lid built closed, then swung open on the back hinge
    lid = chest_lid(a, W + 0.04, Dl, hz, Hl, n=4, pt=pt, ct=0.24, core=False, e=e)
    for sx in (-1, 1):
        # iron corner plates on the lid's front corners (top when open)
        for t in (0.0,):
            p = Vector(ell(Dl, Hl, hz, 0.0, grow=pt, e=e))
            lid += a.box((0.32, 0.05, 0.34), loc=(sx * (W / 2 - 0.12), p.x - 0.02, hz + 0.13), mat="iron_dark",
                         bevel=0.012)
            lid += a.box((0.05, 0.34, 0.34), loc=(sx * (W / 2 + 0.05), p.x + 0.16, hz + 0.13), mat="iron_dark",
                         bevel=0.012)
            lid += rivet(a, (sx * (W / 2 - 0.12), p.x - 0.045, hz + 0.13), FRONT, r=0.05)
        lid += a.box((0.36, 0.05, 0.4), loc=(sx * 0.95, Dl / 2 + pt + 0.02, hz + 0.18), mat="iron_edge", bevel=0.012)
    hinge_rotate(a, lid, hy, hz, -2.12)
    return done(a)


def pelt(a, cx, cz, y, s=1.0, mat="clay_light"):
    """Small stretched hide: four leg lobes, a darker spot in the middle."""
    half = [(0.0, 0.4), (0.14, 0.4), (0.24, 0.46), (0.33, 0.36), (0.33, 0.18), (0.36, 0.0), (0.33, -0.18),
            (0.36, -0.36), (0.24, -0.44), (0.13, -0.38), (0.0, -0.4)]
    pts = half + [(-x, z) for x, z in reversed(half[1:-1])]
    pts = [(cx + x * s, cz + z * s) for x, z in pts]
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    front_prism(a, pts if area < 0 else list(reversed(pts)), y, 0.05, mat)
    spot = [(cx - 0.07 * s, cz + 0.12 * s), (cx + 0.08 * s, cz + 0.1 * s), (cx + 0.06 * s, cz - 0.04 * s),
            (cx - 0.05 * s, cz - 0.06 * s)]
    front_prism(a, list(reversed(spot)), y - 0.05, 0.012, "bark")


def storage_cabinet():
    a = fk.Asset("StorageCabinet", CAT)
    W, D, H = 4.4, 2.5, 5.5
    p = 0.6
    px, py = W / 2 - p / 2, D / 2 - p / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            gtim(a, (sx * px - p / 2, sy * py - p / 2, 0), (sx * px + p / 2, sy * py + p / 2, H), ends=1,
                 mat="wood", faces="-y+y-x+x")
    zt0, zt1 = 4.75, 5.2  # top board
    zb0, zb1 = 0.32, 0.72  # bottom rails
    for sy in (-1, 1):
        gtim(a, (-px + p / 2, sy * py - 0.2, zb0), (px - p / 2, sy * py + 0.2, zb1), mat="wood", ends=False,
             faces="-y" if sy < 0 else "+y")
    for sx in (-1, 1):
        gtim(a, (sx * px - 0.2, -py + p / 2, zb0), (sx * px + 0.2, py - p / 2, zb1), mat="wood", ends=False,
             faces="-x" if sx < 0 else "+x")
    # thick two-plank top, set between the posts, which stand proud above it
    for i, yc in enumerate((-D / 4 + 0.03, D / 4 - 0.03)):
        gplank(a, (2 * px + 0.06, D / 2 - 0.02, zt1 - zt0), loc=(0, yc, (zt0 + zt1) / 2),
               mat="wood_light" if i == 0 else "wood", faces="+z-y" if i == 0 else "+z+y")
    a.box((2 * px - 0.1, 2 * py - 0.1, zt0 - zb0), loc=(0, 0, zb0), base=True, mat="wood_dark")
    dz0, dz1 = zb1, zt0
    dh = dz1 - dz0
    # plank sides and back
    sw = (2 * py - p) / 2
    for sx in (-1, 1):
        for i in range(2):
            gplank(a, (0.12, sw - 0.04, dh), loc=(sx * (px + 0.06), -py + p / 2 + sw * (i + 0.5), dz0 + dh / 2),
                   mat="wood" if i % 2 else "wood_light", faces="-x" if sx < 0 else "+x")
    bw = (2 * px - p) / 3
    for i in range(3):
        gplank(a, (bw - 0.04, 0.12, dh), loc=(-px + p / 2 + bw * (i + 0.5), py + 0.06, dz0 + dh / 2), mat="wood",
               faces="+y")
    # door: three wide vertical planks between the front posts
    yf = -py - 0.12
    dw = 2 * (px - p / 2)
    n = 3
    for i in range(n):
        gplank(a, (dw / n - 0.06, 0.14, dh), loc=(-dw / 2 + dw / n * (i + 0.5), yf, dz0 + dh / 2),
               mat="wood", faces="-y", dens=1.4)
    # two square iron hinges on the left edge, each with a pin knob
    for zz in (1.55, 3.85):
        a.box((0.5, 0.07, 0.5), loc=(-px + p / 2 + 0.06, yf - 0.1, zz), mat="iron_dark", bevel=0.025)
        a.cyl(0.1, 0.08, 0.14, 6, loc=(-px + p / 2 + 0.06, yf - 0.13, zz), rot=FRONT, mat="iron_dark")
    # small hide on the door, a wooden handle bar through it
    a.cyl(0.1, 0.1, 1.2, 6, loc=(-0.6, yf - 0.13, 2.85), rot=RIGHT, mat="wood_light")
    for s in (-1, 1):
        a.cyl(0.07, 0.07, 0.02, 6, loc=(s * 0.58 - (0.02 if s > 0 else 0), yf - 0.12, 2.85), rot=RIGHT,
              mat="wood_end")
    pelt(a, 0.02, 2.88, yf - 0.2, s=1.1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            r = p * 0.71
            rope_wrap(a, sx * px, sy * py, r, zt0 - 0.52, count=3 if sy < 0 else 2, th=0.095, rseg=4)
            rope_wrap(a, sx * px, sy * py, r, zb1 + 0.02, count=3 if sy < 0 else 2, th=0.095, rseg=4)
    return done(a)


# ---------------------------------------------------------------------------
# Totem, quest board, lectern, weapon rack
# ---------------------------------------------------------------------------


def wrap_shape(a, R, u_vals, zlo, zhi, th, mat, t=None):
    """Patch wrapped on a cylinder of radius R around the front (-Y): for each arc-length u,
    the patch spans zlo(u)..zhi(u); th is its thickness outward."""
    rings = []
    for u in u_vals:
        ang = -PI / 2 + u / R
        lo, hi = zlo(u), zhi(u)
        if hi - lo < 0.02:
            hi = lo + 0.02
        ci, si = math.cos(ang), math.sin(ang)
        ri, ro = R, R + th
        rings.append([(ri * ci, ri * si, lo), (ri * ci, ri * si, hi), (ro * ci, ro * si, hi), (ro * ci, ro * si, lo)])
    return loft(a, rings, mat, t=t)


def facet_patch(a, pts, phi, d, mat, depth=0.03):
    """Flat shape (local x across, world z up) on the vertical facet facing angle phi at distance d."""
    return a.poly_prism(pts, depth, loc=(d * math.cos(phi), d * math.sin(phi), 0), rot=(PI / 2, 0, phi + PI / 2),
                        mat=mat)


def wrap_prism(a, pts, R, depth, mat, t=None):
    """Flat shape given in (arc-length u, z), wrapped onto a cylinder of radius R facing -Y."""
    bm = a.bm

    def P(u, z, r):
        ang = -PI / 2 + u / R
        return (r * math.cos(ang), r * math.sin(ang), z)

    inner = [bm.verts.new(P(u, z, R)) for u, z in pts]
    outer = [bm.verts.new(P(u, z, R + depth)) for u, z in pts]
    bm.faces.new(list(reversed(inner)))
    bm.faces.new(outer)
    n = len(pts)
    for i in range(n):
        bm.faces.new((inner[i], inner[(i + 1) % n], outer[(i + 1) % n], outer[i]))
    return a._finish(inner + outer, mat, t)


def offset_poly(pts, d):
    """Mitred inward offset of a closed 2D polygon by d (either winding)."""
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sgn = 1.0 if area > 0 else -1.0
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        e1, e2 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n1, n2 = Vector((-e1.y, e1.x)) * sgn, Vector((-e2.y, e2.x)) * sgn
        b = n1 + n2
        b = n1 if b.length < 1e-6 else b.normalized()
        m = d / max(b.dot(n1), 0.35)
        q = p1 + b * m
        out.append((q.x, q.y))
    return out


def carve_prism(a, pts, y, depth, ch, mat, t=None, recede=None):
    """Front-facing carved slab: outline in world (x, z) on plane y, extruded toward -Y, with a
    chamfered front rim of size ch. recede(x, z) pushes the front face back (sloped planes)."""
    rc = recede or (lambda x, z: 0.0)
    inner = offset_poly(pts, ch)
    back = [(x, y, z) for x, z in pts]
    mid = [(x, y - depth + ch + rc(x, z), z) for x, z in pts]
    front = [(x, y - depth + rc(x, z), z) for x, z in inner]
    return loft(a, [back, mid, front], mat, t=t)


def elders_totem(name="EldersTotem", extra=0.0):
    """Owl totem. `extra` lengthens the staved trunk below the rope (the tall lobby variant);
    the head, wings, crest, posts, rope, diamond and base are shared."""
    a = fk.Asset(name, CAT)
    # --- base ring of chunky stones (stone bodies, light tops) ---------------
    a.cyl(1.7, 1.7, 0.5, 10, mat="stone_dark")
    n = 8
    for i in range(n):
        ang = 2 * PI * i / n + PI / n - PI / 2
        r = 1.95 + a.rng.uniform(-0.06, 0.08)
        h = 1.15 + a.rng.uniform(-0.15, 0.12)
        ln = 1.55 + a.rng.uniform(-0.12, 0.12)
        dp = 0.95 + a.rng.uniform(-0.08, 0.1)
        rot = (0, 0, ang + PI / 2 + a.rng.uniform(-0.06, 0.06))
        loc = (r * math.cos(ang), r * math.sin(ang), 0)
        chunk(a, (ln, dp, h - 0.12), (loc[0], loc[1], (h - 0.12) / 2), rot=rot, mat="stone", ch=0.1)
        chunk(a, (ln - 0.12, dp - 0.12, 0.24), (loc[0], loc[1], h - 0.14), rot=rot, mat="stone_light", ch=0.09)
    # --- trunk of vertical staves -------------------------------------------
    R, ns = 1.42, 10
    DROP = 0.35  # the short trunk is this much shorter than the original layout
    zt = 4.19 - DROP + extra
    mats = ["wood_light", "wood", "wood_light", "wood_end", "wood", "wood_light", "wood", "wood_end", "wood_light",
            "wood"]
    for i in range(ns):
        a0 = -PI / 2 + 2 * PI * (i - 0.5) / ns + 0.025
        a1 = -PI / 2 + 2 * PI * (i + 0.5) / ns - 0.025
        zb = 0.35 + a.rng.uniform(-0.1, 0.12)
        ro = R + a.rng.uniform(-0.03, 0.03)
        ri = ro - 0.28
        secs = []
        for z, k in ((zb, 1.0), (2.25 + extra * 0.5, 1.015), (zt, 0.99)):
            o, inn = ro * k, ri * k
            secs.append([(o * math.cos(a0), o * math.sin(a0), z), (o * math.cos(a1), o * math.sin(a1), z),
                         (inn * math.cos(a1), inn * math.sin(a1), z), (inn * math.cos(a0), inn * math.sin(a0), z)])
        loft(a, secs, mats[i], t=tint(a, 0.08))
    a.cyl(R - 0.22, R - 0.22, zt - 0.3, ns, loc=(0, 0, 0.3), mat="wood_dark")
    # solid end-grain cap closing the trunk top (no hollow from above), with two growth rings
    a.cyl(R * 0.99, R * 0.99, 0.06, ns, loc=(0, 0, zt - 0.03), mat="wood_end")
    a.torus(R * 0.55, 0.03, loc=(0, 0, zt + 0.03), seg=10, rseg=3, mat="wood_light", squash=0.5)
    ap =R * 1.015 * math.cos(PI / ns) + 0.005
    if extra:
        # long lobby trunk: a second pair of rope wraps ~2/3 down, and worn patches on the lower staves
        zc = 1.2 + (zt - 1.2) / 3
        for k, z in enumerate((zc - 0.12, zc + 0.12)):
            a.torus(R + 0.08, 0.1, loc=(0, 0, z), seg=16, rseg=4, mat="rope", tint=0.95 + 0.05 * k)
        facet_patch(a, [(-0.3, 1.5), (0.32, 1.65), (0.36, 2.5), (-0.1, 2.75), (-0.36, 2.2)], -PI / 2 + 2 * PI * 2 / ns,
                    ap, "cloth_red")
        facet_patch(a, [(-0.3, 4.4), (0.3, 4.3), (0.34, 5.3), (-0.2, 5.5)], -PI / 2 - 2 * PI * 1 / ns, ap, "wood_dark")
    # --- everything from here sits at the top of the trunk (lifted by `extra`)
    pre = set(a.bm.verts)
    # worn red and charred patches on the left side
    phi_l = -PI / 2 - 2 * PI * 2 / ns
    facet_patch(a, [(-0.38, 2.3), (0.3, 2.45), (0.4, 3.25), (0.05, 3.6), (-0.35, 3.3)], phi_l, ap, "cloth_red")
    phi_l2 = -PI / 2 - 2 * PI * 1 / ns
    facet_patch(a, [(-0.3, 1.65), (0.32, 1.77), (0.36, 2.35), (-0.1, 2.55), (-0.36, 2.2)], phi_l2, ap, "wood_dark")
    facet_patch(a, [(-0.25, 2.8), (0.2, 2.95), (0.25, 3.4), (-0.2, 3.35)], -PI / 2 + 2 * PI * 3 / ns, ap,
                "cloth_red")
    # --- belly: big red diamond hanging from the rope, with a bull-skull sigil
    dia_pre = set(a.bm.verts)
    Rw = R * 1.015 + 0.02
    top, mid, bot, hw, tw = 3.94, 3.09, 1.59, 0.95, 0.62

    def zhi(u):
        u = abs(u)
        return top if u <= tw else top - (top - mid) * (u - tw) / (hw - tw)

    def zlo(u):
        return bot + (mid - bot) * abs(u) / hw

    us = [-0.94, -0.78, -0.62, -0.4, -0.2, 0.0, 0.2, 0.4, 0.62, 0.78, 0.94]
    wrap_shape(a, Rw, us, zlo, zhi, 0.05, "cloth_red")
    # bull-skull sigil, wrapped onto the diamond's curved surface
    Rs = Rw + 0.05
    sig = []
    skull = [(-0.25, 3.46), (-0.19, 3.58), (0.0, 3.62), (0.19, 3.58), (0.25, 3.46), (0.21, 3.24), (0.11, 3.04),
             (-0.11, 3.04), (-0.21, 3.24)]
    sig += wrap_prism(a, list(reversed(skull)), Rs, 0.035, "bone")
    for s in (-1, 1):
        horn = [(s * 0.16, 3.5), (s * 0.36, 3.5), (s * 0.52, 3.6), (s * 0.6, 3.78), (s * 0.56, 4.0),
                (s * 0.48, 3.84), (s * 0.42, 3.72), (s * 0.31, 3.65), (s * 0.14, 3.62)]
        sig += wrap_prism(a, horn if s < 0 else list(reversed(horn)), Rs, 0.035, "bone")
        sig += wrap_prism(a, [(s * 0.06, 3.33), (s * 0.15, 3.33), (s * 0.15, 3.42), (s * 0.06, 3.42)], Rs + 0.035,
                          0.02, "charcoal")
    sig += wrap_prism(a, [(-0.05, 3.06), (0.05, 3.06), (0.05, 2.52), (-0.05, 2.52)], Rs, 0.035, "bone")
    sig += wrap_prism(a, [(-0.2, 2.78), (0.2, 2.78), (0.2, 2.7), (-0.2, 2.7)], Rs, 0.035, "bone")
    a.transform(sig, loc=(0, 0, -0.31))
    dia = [v for v in a.bm.verts if v not in dia_pre]
    a.transform(dia, loc=(0, 0, 3.94 * (1 - 0.88)), scale=(1, 1, 0.88))  # diamond a little shorter
    # --- thick two-wrap rope at the neck -------------------------------------
    for k, z in enumerate((4.01, 4.27)):
        a.torus(R + 0.12, 0.13, loc=(0, 0, z), seg=16, rseg=5, mat="rope", tint=1.0 + 0.05 * k)
    # --- head: carved owl block, about as wide as the trunk and taller than wide.
    # Built at a broader working width, then narrowed by HX in x at the end.
    head_pre = set(a.bm.verts)
    HX, HZ = 0.74, 0.84

    def mirror(right):
        """Right-half outline from the top centre round to the bottom centre -> full closed outline."""
        return right + [(-x, z) for x, z in reversed(right) if abs(x) > 1e-6]

    def hring(r, yf, z, n=12):
        """Solid head cross-section centred on the trunk axis: round back and sides of radius r, front
        flattened at yf for the mask. x is pre-divided by HX so the ring is round after narrowing."""
        pts = []
        for j in range(n):
            th = -PI / 2 + 2 * PI * (j + 0.5) / n
            pts.append((r * math.cos(th) / HX, max(r * math.sin(th), yf), z))
        return pts

    hz0 = 4.15  # sits on the capped trunk top
    # solid carved head block covering the trunk: darker jaw, lighter upper block, crown rounding over
    loft(a, [hring(1.53, -1.44, hz0), hring(1.53, -1.44, 5.9)], "wood_dark", t=1.0)
    loft(a, [hring(1.5, -1.3, 5.7), hring(1.5, -1.36, 7.3), hring(1.44, -1.3, 7.95), hring(1.2, -1.08, 8.33),
             hring(0.88, -0.8, 8.5)], "wood_light")
    # dark grey band across the forehead, dipping into the brow V
    front_prism(a, [(-1.2, 7.98), (-1.68, 7.66), (0.0, 7.0), (1.68, 7.66), (1.2, 7.98), (0.6, 7.86),
                    (0.0, 7.55), (-0.6, 7.86)], -1.3, 0.19, "stone_dark", t=0.72)
    # red shield crest standing in front of the crown, tip pointing down into the brow centre
    crest = [(0.0, 7.1), (0.79, 7.62), (0.82, 8.28), (0.51, 8.64), (-0.51, 8.64), (-0.82, 8.28), (-0.79, 7.62)]
    carve_prism(a, offset_poly(crest, -0.09), -0.95, 0.5, 0.05, "wood_end", t=0.96)
    carve_prism(a, crest, -1.2, 0.38, 0.06, "cloth_red")
    # raised bevelled spine from the crest tip up over the crown
    sweep(a, [(0, -1.59, 7.2), (0, -1.6, 8.28), (0, -1.5, 8.6), (0, -1.2, 8.7), (0, -0.7, 8.6), (0, -0.25, 8.55)],
          [(0.05, 0.07)] * 6, "cloth_red", sides=4, phase=0, up=(1, 0, 0), t=1.18)
    # pale carved face mask, proud of the head; lower cheeks slope back
    ym = -1.3
    mask = mirror([(0.0, 6.78), (0.5, 7.02), (1.2, 7.35), (1.8, 7.62), (1.92, 7.3), (1.9, 6.55), (1.72, 6.0),
                   (1.25, 5.76), (0.75, 5.6), (0.0, 5.48)])
    carve_prism(a, mask, ym, 0.32, 0.07, "wood_end", t=1.0, recede=lambda x, z: max(0.0, 6.25 - z) * 0.22)
    yp = ym - 0.32  # mask front
    # heavy V brows overhanging the eyes
    for s in (-1, 1):
        brow = [(0.0, 6.66), (0.7, 6.9), (1.3, 7.06), (1.72, 7.08), (1.88, 6.45), (2.02, 6.4), (2.02, 7.45),
                (1.96, 7.72), (0.0, 7.1)]  # arches over the eye and curves down its outer side (facial disc)
        brow = [(s * x, z) for x, z in brow]
        carve_prism(a, brow, yp + 0.03, 0.3, 0.09, "wood_end", t=1.06)
    # big slanted almond eyes: thick charcoal sockets, cream whites, small pupils
    for s in (-1, 1):
        sock = [(0.68, 6.55), (0.8, 6.82), (1.25, 6.98), (1.66, 6.98), (1.8, 6.68), (1.66, 6.3), (1.25, 6.12),
                (0.86, 6.22)]
        white = [(x + 0.07, z - 0.03) for x, z in offset_poly(sock, 0.21)]  # crescent toward the outer side
        sock, white = [(s * x, z) for x, z in sock], [(s * x, z) for x, z in white]
        front_prism(a, sock, yp + 0.01, 0.045, "charcoal")
        front_prism(a, white, yp - 0.03, 0.03, "bone")
        pupil = a.cyl(0.15, 0.15, 0.03, 6, rot=FRONT, mat="charcoal")
        a.transform(pupil, loc=(s * 1.12, yp - 0.055, 6.64), scale=(1 / HX, 1, 1))  # stays round after narrowing
    # dominant raptor beak: kite-shaped in front view, lit central ridge facets, darker outer facets,
    # tip hooking down over the mouth
    yb = yp + 0.06
    beak = [(7.0, 0.8, yb - 0.28), (6.7, 0.8, yb - 0.5), (6.35, 0.74, yb - 0.72), (5.95, 0.52, yb - 0.84),
            (5.6, 0.32, yb - 0.86), (5.3, 0.13, yb - 0.78), (5.07, 0.03, yb - 0.55)]
    ridge, sides = [], {-1: [], 1: []}
    for z, hw, yr in beak:
        sh = yr + (yb - yr) * 0.42
        ridge.append([(-hw * 0.6, sh, z), (0.0, yr, z), (hw * 0.6, sh, z), (0.0, yb, z)])
        for s in (-1, 1):
            sides[s].append([(s * hw, yb, z), (s * hw * 0.6, sh, z), (s * hw * 0.6, yb, z)])
    # lit top (upper rings) in pale wood, hook and underside in bark
    loft(a, ridge[:5], "wood_end", t=1.2)
    loft(a, ridge[4:], "bark", t=1.0)
    for s in (-1, 1):
        loft(a, sides[s][:5], "wood_light", t=1.05)
        loft(a, sides[s][4:], "bark", t=0.86)
    # dark carved groove around the beak where it meets the mask, so its kite outline reads
    edge = [(hw + 0.055, z) for z, hw, _ in beak if z > 5.65] + [(0.4, 5.6)]
    groove = [(0.0, 7.08)] + edge + [(0.0, 5.6)] + [(-x, z) for x, z in reversed(edge)]
    front_prism(a, groove, yp + 0.15, 0.18, "wood_dark", t=0.8)
    # closed mouth: a narrow shadow gap under the mask, two blocky tusks beside the beak tip
    front_prism(a, [(-0.75, 5.66), (0.75, 5.66), (0.7, 5.44), (-0.7, 5.44)], -1.38, 0.04, "charcoal")
    for s in (-1, 1):
        a.cyl(0.09, 0.16, 0.46, 4, loc=(s * 0.48, -1.54, 5.2), mat="wood_end", twist=PI / 4)
        # cheek blocks running from under the mask down to the rope
        a.box((0.55, 0.32, 1.1), loc=(s * 1.18, -1.46, 5.2), mat="wood", bevel=0.07, tint=1.1)
    # solid triangular feather wings, attached around eye level and sweeping up and out
    W = [(0.0, -0.8), (0.48, -0.5), (0.54, -0.38), (0.98, -0.06), (1.04, 0.07), (1.45, 0.42), (1.52, 0.56),
         (1.9, 0.82), (1.85, 1.38), (1.0, 1.08), (0.0, 0.82)]
    grooves = [[(0.1, -0.5), (0.54, -0.38)], [(0.1, -0.12), (1.04, 0.07)], [(0.1, 0.3), (1.52, 0.56)]]

    def broad(pts):  # ~15% broader at the root, tapering to no change at the tip
        return [(u, v * (1 + 0.15 * max(0.0, 1 - u / 1.9))) for u, v in pts]

    for s in (-1, 1):
        wing = carve_prism(a, [(s * u, v) for u, v in rot2(broad(W), 0.4, 0, 0)], 0.15, 0.3, 0.07, "wood_light", t=1.02)
        for g in grooves:
            wing += a.strip([(s * u, v) for u, v in rot2(broad(g), 0.4, 0, 0)], 0.06, 0.03, loc=(0, -0.13, 0), rot=FRONT,
                            mat="wood_dark")
        a.transform(wing, loc=(s * 1.62, -0.45, 6.45), rot=(0, 0, -s * math.radians(15)), scale=(1.85, 1.25, 1.3))
    # two square posts at the back corners of the head
    for s in (-1, 1):
        tim(a, (s * 1.0 - 0.3, -0.05, 7.7), (s * 1.0 + 0.3, 0.55, 9.45), mat="wood", ends=1)
        for zz in (8.95, 9.22):
            rivet(a, (s * 1.0, -0.06, zz), FRONT, r=0.05, mat="charcoal")
    a.transform([v for v in a.bm.verts if v not in head_pre], loc=(0, 0, 4.4 * (1 - HZ)), scale=(HX, 1, HZ))
    a.transform([v for v in a.bm.verts if v not in pre], loc=(0, 0, extra - DROP))
    a.transform(list(a.bm.verts), scale=1.07)  # overall size back to ~9 studs
    return done(a)


def elders_totem_tall():
    """Lobby variant: same head and base, much longer staved trunk (~13.5 studs overall)."""
    return elders_totem("EldersTotemTall", extra=4.25)



def quest_board():
    a = fk.Asset("QuestBoard", CAT)
    px, pr = 2.5, 0.3
    for s in (-1, 1):
        gbeam(a, (s * px, 0, 0.0), (s * px, 0, 5.45), pr, sides=7)
    bz, yf, yk = 4.78, -0.5, 0.46  # top logs: front one overhangs well past the posts
    gbeam(a, (-3.0, yf, bz), (3.0, yf, bz), 0.25, sides=7)
    gbeam(a, (-2.82, yk, bz), (2.82, yk, bz), 0.21, sides=7)
    # plank shelf resting on the two top logs
    for i, (yc, w) in enumerate(((-0.27, 0.52), (0.23, 0.48))):
        gplank(a, (4.5, w, 0.1), loc=(0, yc, bz + 0.27), mat="wood_light" if i else "wood", faces="+z")
    # framed board: dark frame, horizontal plank panel, bolts round the frame
    x0, x1, z0, z1, fw = -2.22, 2.22, 1.3, 4.45, 0.3
    for s in (-1, 1):
        gplank(a, (fw, 0.2, z1 - z0), loc=(s * (x1 - fw / 2), 0, (z0 + z1) / 2), mat="wood", faces="-y+y")
    for zc in (z0 + fw / 2, z1 - fw / 2):
        gplank(a, (x1 - x0 - 2 * fw + 0.02, 0.2, fw), loc=(0, 0, zc), mat="wood", faces="-y+y")
    a.box((x1 - x0 - 0.1, 0.05, z1 - z0 - 0.1), loc=(0, 0.11, (z0 + z1) / 2), mat="wood_dark")  # backer
    n = 5
    ph = (z1 - z0 - 2 * fw) / n
    for i in range(n):
        gplank(a, (x1 - x0 - 2 * fw + 0.04, 0.1, ph - 0.03), loc=(0, 0.04, z0 + fw + ph * (i + 0.5)),
               mat="wood_dark" if i % 2 else "wood", faces="-y+y")
    for s in (-1, 1):
        for zz in (1.45, 2.3, 3.2, 4.3):
            bolt(a, (s * (x1 - fw / 2), -0.1, zz), FRONT, r=0.075)
    for xx in (-1.0, 0.6):
        bolt(a, (xx, -0.1, z0 + fw / 2), FRONT, r=0.075)
    # bottom log in front of the board, coiled rope round the posts where it meets them
    gbeam(a, (-2.95, -0.42, 1.12), (2.95, -0.42, 1.12), 0.23, sides=7)
    for s in (-1, 1):
        rope_wrap(a, s * px, 0, pr, 1.36, count=3, th=0.08, seg=8, rseg=3)
    # notices pinned to the panel
    notes = [(-1.2, 3.22, 1.05, 1.32, 0.05), (-0.12, 3.42, 0.7, 0.74, -0.05), (1.05, 3.24, 1.05, 1.22, 0.04),
             (-1.55, 1.97, 0.55, 0.66, -0.06), (-0.48, 2.05, 1.05, 1.0, 0.05), (1.1, 2.02, 1.0, 0.92, -0.07)]
    yb = -0.015
    for k, (cx, cz, w, h, ang) in enumerate(notes):
        j = lambda: a.rng.uniform(-0.04, 0.04)  # noqa: E731
        shape = [(-w / 2 + j(), -h / 2 + j()), (0 + j(), -h / 2 - 0.05), (w / 2 + j(), -h / 2 + j()),
                 (w / 2 + j(), h / 2 + j()), (-w / 2 + j(), h / 2 + j())]
        yk_ = yb - 0.005 - 0.012 * (k % 2)
        front_prism(a, rot2(shape, ang, cx, cz), yk_, 0.03, "parchment", t=tint(a, 0.05))
        gs = min(w, h) * 0.24
        cells = [(-0.18, 0.17), (0.16, -0.2)] if w * h > 0.8 else [(0, -0.05)]
        for gi, (gx, gz) in enumerate(cells):
            p = rot2([(gx * w, gz * h)], ang, 0, 0)[0]
            glyph(a, k * 2 + gi, cx + p[0], cz + p[1], gs, 0.1, 0.02, loc=(0, yk_ - 0.03, 0), rot=FRONT,
                  ang=ang, mat="ink")
        top = rot2([(0, h / 2 - 0.09)], ang, cx, cz)[0]
        rivet_front(a, top[0], yk_ - 0.035, top[1], r=0.06, mat="bark")
    # torn cloth draped over the shelf and the front log, right of centre
    rc = 0.25 + 0.05
    sx0, sw = -0.75, 0.58
    for i in range(4):
        x = sx0 + sw * (i + 0.5)
        drop = 0.45 + a.rng.uniform(0.0, 0.35)
        off = 0.012 * (i % 2)
        prof = [(0.15, bz + 0.33 + off)]
        for k in range(6):
            t = math.radians(80 + 100 * k / 5)
            prof.append((yf + (rc + off) * math.cos(t), bz + (rc + off) * math.sin(t)))
        prof.append((yf - rc - off - 0.02, bz - drop))
        rings = []
        P = [Vector(p) for p in prof]
        for ii, pp in enumerate(P):
            tv = (P[min(ii + 1, len(P) - 1)] - P[max(ii - 1, 0)]).normalized()
            nr = Vector((-tv.y, tv.x))
            o = pp + nr * 0.04
            rings.append([(x - sw / 2, pp.x, pp.y), (x + sw / 2, pp.x, pp.y), (x + sw / 2, o.x, o.y),
                          (x - sw / 2, o.x, o.y)])
        loft(a, rings, "cloth_cream", t=tint(a, 0.06))
        yt = yf - rc - off - 0.02
        tooth = [(x - sw / 2, bz - drop + 0.01), (x + sw / 2, bz - drop + 0.01),
                 (x + sw * a.rng.uniform(-0.1, 0.3), bz - drop - a.rng.uniform(0.12, 0.25))]
        front_prism(a, tooth, yt + 0.02, 0.04, "cloth_cream")
    for s in (-1, 1):
        a.lashing((s * px, yf + 0.15, bz), size=0.42, thickness=0.085)
    return done(a)


def ledger_lectern():
    a = fk.Asset("LedgerLectern", CAT)
    bx, by, cb = 1.3, 1.12, 0.56
    # square base frame: chunky corner blocks joined by low beams
    for sx in (-1, 1):
        for sy in (-1, 1):
            gtim(a, (sx * bx - cb / 2, sy * by - cb / 2, 0), (sx * bx + cb / 2, sy * by + cb / 2, cb), mat="wood",
                 ends=False, faces="-y+y-x+x")
            a.box((cb * 0.7, cb * 0.7, 0.02), loc=(sx * bx, sy * by, cb), mat="wood_end")
    for sy in (-1, 1):
        gtim(a, (-bx + cb / 2, sy * by - 0.19, 0.05), (bx - cb / 2, sy * by + 0.19, 0.44), mat="wood_light",
             ends=False, faces="-y+y+z")
    for sx in (-1, 1):
        gtim(a, (sx * bx - 0.19, -by + cb / 2, 0.05), (sx * bx + 0.19, by - cb / 2, 0.44), mat="wood", ends=False,
             faces="-x+x+z")
    th = math.radians(26)
    yc, zc = 0.02, 3.02

    def under(y):  # underside of the sloped desk at world y
        return zc + (y - yc) * math.tan(th) - 0.17 / math.cos(th)

    # front pair of posts (the pedestal) on a sill, tall back posts at the back corners
    fxp, fyp = 0.5, -0.55
    gtim(a, (-bx + 0.19, fyp - 0.2, 0.44), (bx - 0.19, fyp + 0.2, 0.78), mat="wood", ends=False, faces="-y+z")
    for sx in (-1, 1):
        gtim(a, (sx * fxp - 0.22, fyp - 0.22, 0.78), (sx * fxp + 0.22, fyp + 0.22, under(fyp) + 0.05), mat="wood",
             ends=False, faces="-y+y-x+x")
        gtim(a, (sx * bx - 0.22, by - 0.22, cb), (sx * bx + 0.22, by + 0.22, 4.12), mat="wood", ends=1,
             faces="-y+y-x+x")
    gtim(a, (-fxp + 0.2, fyp - 0.16, 1.25), (fxp - 0.2, fyp + 0.16, 1.55), mat="wood_dark", ends=False, faces="-y")
    gtim(a, (-bx + 0.2, by - 0.16, 1.4), (bx - 0.2, by + 0.16, 1.72), mat="wood_dark", ends=False, faces="+y-y")
    # sloped desk built flat (local y up the slope), then tilted
    desk = []
    for i in range(3):
        desk += gplank(a, (2.7, 0.86, 0.16), loc=(0, -0.86 + i * 0.86, -0.08), mat="wood_dark", faces="+z")
    for s in (-1, 1):  # thick side logs standing proud of the book
        desk += gtim(a, (s * 1.42 - 0.22, -1.2, -0.16), (s * 1.42 + 0.22, 1.32, 0.3), mat="wood", ends=True,
                     faces="+z-x+x")
    desk += gbeam(a, (-1.95, 1.3, 0.08), (1.95, 1.3, 0.08), 0.24, sides=7, mat="wood")
    # front lip log with cut, bolted ends standing out past the sides
    desk += gtim(a, (-1.8, -1.62, -0.24), (1.8, -1.16, 0.24), mat="wood_light", ends=True, faces="+z-y")
    for s in (-1, 1):
        desk += rivet(a, (s * 1.62, -1.63, 0.0), FRONT, r=0.07)
    # thick open book: cover, then two page blocks curling up from the spine
    desk += a.box((2.5, 2.2, 0.08), loc=(0, 0.0, 0.04), mat="wood_dark", bevel=0.025)
    top = [(0.06, 0.2), (0.2, 0.33), (0.42, 0.4), (0.78, 0.41), (1.08, 0.37), (1.18, 0.3), (1.2, 0.18)]
    for s in (-1, 1):
        pts = [(0.03, 0.1), (1.2, 0.1)] + list(reversed(top))[:-1] + [top[0]]
        pts = [(s * x, z) for x, z in pts]
        if s < 0:
            pts = list(reversed(pts))
        desk += a.poly_prism(pts, 2.05, loc=(0, 1.02, 0), rot=(PI / 2, 0, 0), mat="parchment")
        desk += a.box((0.03, 1.95, 0.03), loc=(s * 1.21, 0.0, 0.2), mat="ink")
        # left page: columns of short glyph lines; right page: one big diamond rune
        if s < 0:
            for ci, gx in enumerate((-0.95, -0.7, -0.45, -0.22)):
                for ri in range(4):
                    gy = 0.72 - ri * 0.42 - (0.12 if ci % 2 else 0)
                    desk += a.box((0.07, 0.22 + 0.06 * ((ci + ri) % 2), 0.02), loc=(gx, gy, 0.42), mat="ink")
        else:
            desk += glyph(a, 0, 0.62, 0.15, 0.3, 0.07, 0.022, loc=(0, 0, 0.42), ang=PI / 4)
            desk += glyph(a, 4, 0.62, 0.15, 0.1, 0.05, 0.022, loc=(0, 0, 0.43))
            for gy in (0.78, -0.62):
                desk += a.box((0.7, 0.06, 0.02), loc=(0.62, gy, 0.42), mat="ink")
    desk += a.box((0.08, 2.05, 0.06), loc=(0, 0.0, 0.11), mat="wood_dark")
    desk += a.box((0.1, 0.03, 0.42), loc=(0.12, -1.0, 0.0), mat="cloth_red")
    a.transform(desk, loc=(0, yc, zc), rot=(th, 0, 0))
    # rope lashings where the desk meets the posts
    for sx in (-1, 1):
        a.lashing((sx * bx, by - 0.05, under(by) + 0.12), size=0.34, thickness=0.07, rot=(0, 0, PI / 2))
        a.lashing((sx * fxp, fyp, under(fyp) - 0.2), size=0.3, thickness=0.065)
    rope_wrap(a, -bx, by, 0.3, 2.1, count=2, th=0.07, rseg=3)
    return done(a)


def weapon_rack():
    a = fk.Asset("WeaponRack", CAT)
    fx, foot, top_y, H = 2.45, 1.05, 0.4, 5.1
    zx = H * foot / (foot + top_y)  # where front and back legs cross
    lr = 0.4

    def yleg(z, s):  # leg centre y at height z (s=-1 front leg, +1 back leg)
        return s * (foot - (foot + top_y) * z / H)

    for s in (-1, 1):
        x = s * fx
        gbeam(a, (x, -foot, 0), (x, top_y, H), lr, sides=6)
        gbeam(a, (x, foot, 0), (x, -top_y, H), lr, sides=6)
    # top rail through the crossings, five peg blocks on it
    zr0, zr1 = zx - 0.24, zx + 0.32
    gtim(a, (-3.05, -0.28, zr0), (3.05, 0.28, zr1), mat="wood", faces="-y+y+z")
    for i in range(5):
        x = -1.6 + i * 0.8
        gtim(a, (x - 0.21, -0.2, zr1 - 0.02), (x + 0.21, 0.2, zr1 + 0.36), mat="wood_light", ends=False,
             faces="-y+x-x")
        a.box((0.3, 0.28, 0.02), loc=(x, 0, zr1 + 0.36), mat="wood_end")
    # bottom rail lashed across the front legs, four pegs
    zb0, zb1 = 0.92, 1.38
    yb = yleg((zb0 + zb1) / 2, -1)
    gtim(a, (-2.98, yb - 0.25, zb0), (2.98, yb + 0.25, zb1), mat="wood", faces="-y+y+z")
    for i in range(4):
        x = -1.2 + i * 0.8
        gtim(a, (x - 0.21, yb - 0.19, zb1 - 0.02), (x + 0.21, yb + 0.19, zb1 + 0.38), mat="wood_light", ends=False,
             faces="-y+x-x")
        a.box((0.3, 0.26, 0.02), loc=(x, yb, zb1 + 0.38), mat="wood_end")
    for s in (-1, 1):
        x = s * fx
        a.lashing((x, 0, (zr0 + zr1) / 2), size=0.62, thickness=0.14, rot=(0, 0, PI / 2))
        a.lashing((x, yb, (zb0 + zb1) / 2), size=0.56, thickness=0.13, rot=(0, 0, PI / 2))
    return done(a)


# ---------------------------------------------------------------------------
# Anvils, workbench, furnace
# ---------------------------------------------------------------------------


def anvil(a, s, z0):
    """Chunky blacksmith's anvil, its waist and feet centred on x = y = 0 and the flat foot plate standing
    on z0. Broad faceted horn toward +X, shallower stepped heel toward -X. Returns the top z."""
    body, top = "iron_dark", "iron"

    def P(x, y, z):
        return (x * s, y * s, z0 + z * s)

    def blk(lo, hi, mat, bev):
        size = [(hi[i] - lo[i]) * s for i in range(3)]
        return a.box(size, loc=P(*[(hi[i] + lo[i]) / 2 for i in range(3)]), mat=mat, bevel=bev * s, tint=1.0)

    # flat foot plate, two chunky feet with a recess between them
    blk((-0.98, -0.64, 0.0), (0.98, 0.64, 0.14), body, 0.03)
    for sx in (-1, 1):
        lo, hi = sorted((sx * 0.3, sx * 0.96))
        blk((lo, -0.62, 0.12), (hi, 0.62, 0.52), body, 0.06)
    blk((-0.32, -0.5, 0.12), (0.32, 0.5, 0.4), body, 0.04)

    def rect(z, hx, hy):
        return [P(-hx, -hy, z), P(hx, -hy, z), P(hx, hy, z), P(-hx, hy, z)]

    # narrow waist flaring out under the face
    loft(a, [rect(0.5, 0.58, 0.44), rect(0.66, 0.5, 0.38), rect(0.82, 0.76, 0.52)], body, t=0.95)
    # face block, flat lighter working face; heel shares the top but is shallower
    blk((-0.92, -0.62, 0.8), (0.92, 0.62, 2.0), body, 0.09)
    blk((-0.88, -0.58, 1.99), (0.88, 0.58, 2.03), top, 0.02)
    blk((-1.55, -0.52, 1.3), (-0.88, 0.52, 2.0), body, 0.07)
    blk((-1.51, -0.48, 1.99), (-0.88, 0.48, 2.03), top, 0.02)
    # horn: a broad faceted wedge, flat top a step below the face, tapering to a blunt point
    secs = [(0.86, 0.6, 0.88, 1.92), (1.45, 0.53, 1.16, 1.86), (2.05, 0.38, 1.38, 1.76), (2.5, 0.2, 1.48, 1.68)]
    rings = []
    for x, hw, zb, zt in secs:
        zm = zb + (zt - zb) * 0.5
        rings.append([P(x, -hw * 0.8, zt), P(x, hw * 0.8, zt), P(x, hw, zt - (zt - zb) * 0.18), P(x, hw * 0.8, zm),
                      P(x, hw * 0.55, zb), P(x, -hw * 0.55, zb), P(x, -hw * 0.8, zm), P(x, -hw, zt - (zt - zb) * 0.18)])
    loft(a, rings, body, t=1.0)
    a.box((0.14 * s, 0.14 * s, 0.03 * s), loc=P(0.55, 0.0, 2.035), mat="charcoal")
    for sy, rot in ((-1, FRONT), (1, BACK)):
        for xx in (-0.5, 0.5):
            rivet(a, P(xx, sy * 0.62, 1.45), rot, r=0.09 * s)
    return z0 + 2.03 * s


def anvil_large():
    a = fk.Asset("AnvilLarge", CAT)
    z1, z2 = 0.72, 1.18
    # bottom course: two rows of three big chiselled blocks; top course: a two-block plinth
    mats = [["stone", "stone_dark", "stone"], ["stone_dark", "stone", "stone_dark"]]
    for j, y in enumerate((-0.6, 0.6)):
        for i, x in enumerate((-1.1, 0.0, 1.1)):
            chunk(a, (1.06, 1.14, z1), (x, y, z1 / 2), mat=mats[j][i], ch=0.2, flat_top=True)
    for i, x in enumerate((-0.62, 0.62)):
        chunk(a, (1.2, 1.66, z2 - z1), (x, 0.0, (z1 + z2) / 2), mat="stone" if i else "stone_light", ch=0.15,
              flat_top=True)
    anvil(a, 0.98, z2)
    return done(a)

def anvil_small():
    a = fk.Asset("AnvilSmall", CAT)
    R, H, n = 1.15, 1.42, 13
    for i in range(n):
        a0 = 2 * PI * i / n + 0.025
        a1 = 2 * PI * (i + 1) / n - 0.025
        h = H + a.rng.uniform(-0.1, 0.06)
        secs = []
        for z in (0, h):
            rr = R * (1.04 if z == 0 else 0.96)
            secs.append([(rr * math.cos(a0), rr * math.sin(a0), z), (rr * math.cos(a1), rr * math.sin(a1), z),
                         ((rr - 0.22) * math.cos(a1), (rr - 0.22) * math.sin(a1), z),
                         ((rr - 0.22) * math.cos(a0), (rr - 0.22) * math.sin(a0), z)])
        loft(a, secs, "wood", t=tint(a, 0.1))
        am = (a0 + a1) / 2
        rm = R * 1.0 + 0.012
        nv = Vector((math.cos(am), math.sin(am), 0))
        sd = Vector((-math.sin(am), math.cos(am), 0))
        z0g = a.rng.uniform(0.1, 0.5)
        L = a.rng.uniform(0.5, 0.85)
        pts = [nv * rm + Vector((0, 0, z0g + L * k / 3)) + sd * a.rng.uniform(-0.05, 0.05) for k in range(4)]
        streak(a, pts, sd, 0.05, "wood_dark", (0, 0, 0.7))
    a.cyl(R - 0.17, R - 0.17, H - 0.06, n, mat="wood_dark")
    a.cyl(R - 0.12, R - 0.16, 0.06, n, loc=(0, 0, H - 0.06), mat="wood_end")  # flat top the anvil rests on
    zc = 0.5
    a.cyl(R * 1.03 + 0.06, R * 1.02 + 0.06, 0.28, n, loc=(0, 0, zc), mat="iron_dark")
    for k in range(5):
        ang = -PI / 2 + (k - 2) * 0.5
        rr = R * 1.02 + 0.07
        bolt(a, (rr * math.cos(ang), rr * math.sin(ang), zc + 0.14), (PI / 2, 0, ang + PI / 2), r=0.055)
    anvil(a, 0.66, H)
    return done(a)


def crafting_workbench():
    a = fk.Asset("CraftingWorkbench", CAT)
    zt, tt = 2.75, 0.52
    lx, ly, p = 2.3, 0.92, 0.62
    for i in range(3):
        gplank(a, (6.0 - (0.12 if i == 1 else 0), 0.98, tt), loc=(0, -0.99 + i * 0.99, zt - tt / 2),
               mat="wood", faces=["+z-y-x+x", "+z-x+x", "+z+y-x+x"][i], dens=1.3)
    for sx in (-1, 1):
        gtim(a, (sx * lx - p / 2, -ly - p / 2, 0), (sx * lx + p / 2, -ly + p / 2, zt + 0.26), ends=1,
             faces="-y+y-x+x")
        gtim(a, (sx * lx - p / 2, ly - p / 2, 0), (sx * lx + p / 2, ly + p / 2, zt + 0.55), ends=1,
             faces="-y+y-x+x")
        # light wooden bracket clamping the top's front edge over each front leg
        gplank(a, (0.6, 0.08, 0.86), loc=(sx * lx, -1.49 - 0.04, zt - 0.36), mat="wood_light", faces="-y")
        gplank(a, (0.6, 0.36, 0.07), loc=(sx * lx, -1.35, zt + 0.03), mat="wood_light", faces="+z")
        # low side stretcher
        gtim(a, (sx * lx - 0.2, -ly + p / 2, 0.42), (sx * lx + 0.2, ly - p / 2, 0.8), ends=False, mat="wood_dark",
             faces="-x+x+z")
    # diagonal braces from the legs up under the top, front and back
    for sy in (-1, 1):
        for sx in (-1, 1):
            xa, za = sx * (lx - 0.1), 1.05
            xb, zb = sx * (lx - 1.35), zt - tt
            L = math.hypot(xa - xb, za - zb)
            ang = math.atan2(zb - za, xb - xa)
            gplank(a, (L, 0.26, 0.26), loc=((xa + xb) / 2, sy * (ly + (0.0 if sy > 0 else 0.05)), (za + zb) / 2),
                   rot=(0, -ang, 0), mat="wood_light", faces="-y+y+z")
    for sx in (-1, 1):
        rope_wrap(a, sx * lx, -ly, p * 0.71, 0.95, count=3, th=0.085, rseg=4)
    return done(a)


def smelting_furnace():
    a = fk.Asset("SmeltingFurnace", CAT)
    stones = ["stone", "stone", "stone", "stone_light", "stone", "stone_dark"]

    def block(size, loc, rot=(0, 0, 0), mat=None):
        sz = (size[0], size[1] + a.rng.uniform(-0.04, 0.06), size[2] + a.rng.uniform(-0.05, 0.02))
        r = (rot[0], rot[1], rot[2] + a.rng.uniform(-0.03, 0.03))
        chunk(a, sz, (loc[0], loc[1], loc[2] + (sz[2] - size[2]) / 2), rot=r, mat=mat or a.rng.choice(stones),
              ch=0.15)

    def spans(x0, x1, L):
        n = max(1, round((x1 - x0) / L))
        w = [a.rng.uniform(0.85, 1.15) for _ in range(n)]
        tot = sum(w)
        out, c = [], x0
        for wi in w:
            seg = (x1 - x0) * wi / tot
            out.append((c, c + seg))
            c += seg
        return out

    def row_x(x0, x1, yc, z0, h, d, L=1.4, rot=(0, 0, 0)):
        for s0, s1 in spans(x0, x1, L):
            block((s1 - s0 - 0.08, d, h - 0.08), ((s0 + s1) / 2, yc, z0 + h / 2), rot=rot)

    def row_y(y0, y1, xc, z0, h, d, L=1.4, rot=(0, 0, 0)):
        for s0, s1 in spans(y0, y1, L):
            block((d, s1 - s0 - 0.08, h - 0.08), (xc, (s0 + s1) / 2, z0 + h / 2), rot=rot)

    # broad, battered body: three courses of big blocks, then sloped shoulder stones
    Hc, d = 0.9, 0.82
    courses = [(2.88, -2.25, 2.15), (2.72, -2.15, 2.05), (2.52, -2.02, 1.92)]
    ow = 1.0  # firebox half-width; the arch springs from the top of the first course
    ro = ow + 0.52
    yf0 = courses[0][1]
    for k, (sx, yf, yb) in enumerate(courses):
        z0 = k * Hc
        par = k % 2 == 0
        fx0 = -sx if par else -sx + d
        gap = [ow + 0.02, ro + 0.01, math.sqrt(ro * ro - Hc * Hc) + 0.03][k]
        row_x(fx0, -gap, yf + d / 2, z0, Hc, d)
        row_x(gap, -fx0, yf + d / 2, z0, Hc, d)
        row_x(fx0, -fx0, yb - d / 2, z0, Hc, d)
        ya, yb2 = (yf + d, yb - d) if par else (yf, yb)
        for s in (-1, 1):
            row_y(ya, yb2, s * (sx - d / 2), z0, Hc, d)
        cy0 = yf + 0.1 + d + 0.6
        a.box((2 * sx - 0.2, yb - 0.1 - cy0, Hc + 0.02), loc=(0, (cy0 + yb - 0.1) / 2, z0), base=True,
              mat="stone_dark")
    # front face behind the arch and spandrels (mortar shows through the joints)
    a.box((2 * ro + 0.4, 0.3, 2 * Hc), loc=(0, yf0 + d + 0.45, Hc), base=True, mat="stone_dark")
    # arch ring of five big voussoirs, a keystone block above
    nv = 5
    rc = (ow + ro) / 2
    for i in range(nv):
        ang = PI * (i + 0.5) / nv
        chunk(a, (PI * rc / nv - 0.08, d + 0.12, ro - ow - 0.05),
              (rc * math.cos(ang), courses[1][1] + d / 2 - 0.08, Hc + rc * math.sin(ang)), rot=(0, PI / 2 - ang, 0),
              mat="stone_light" if i % 2 == 0 else "stone", ch=0.1)
    kz0 = Hc + ro + 0.02
    chunk(a, (1.3, d, 3 * Hc - kz0 - 0.04), (0, courses[2][1] + d / 2, (kz0 + 3 * Hc) / 2), mat="stone", ch=0.1)
    zsh, hs = 3 * Hc, 0.58
    shx, shf, shb, sd = 2.15, -1.72, 1.62, 0.72
    tilt = 0.45
    for s0, s1 in spans(-shx, shx, 1.3):
        block((s1 - s0 - 0.08, sd, hs), ((s0 + s1) / 2, shf + sd / 2, zsh + hs / 2 - 0.08), rot=(tilt, 0, 0))
        block((s1 - s0 - 0.08, sd, hs), ((s0 + s1) / 2, shb - sd / 2, zsh + hs / 2 - 0.08), rot=(-tilt, 0, 0))
    for s in (-1, 1):
        for s0, s1 in spans(shf + sd, shb - sd, 1.3):
            block((sd, s1 - s0 - 0.08, hs), (s * (shx - sd / 2), (s0 + s1) / 2, zsh + hs / 2 - 0.08),
                  rot=(0, s * tilt, 0))
    a.box((2 * shx - 0.4, shb - shf - 0.4, hs), loc=(0, (shf + shb) / 2, zsh - 0.05), base=True, mat="stone_dark")
    # hearth sill in front of the firebox
    for x in (-0.6, 0.6):
        chunk(a, (1.14, 0.66, 0.26), (x, yf0 - 0.14, 0.13), mat="stone_dark", ch=0.07)
    # firebox: dark back, ember bed, log pile, flames and loose embers
    cav_back = yf0 + d + 0.6
    a.box((2 * ow + 0.2, 0.06, 2.4), loc=(0, cav_back, 0.0), base=True, mat="charcoal")
    a.box((2 * ow - 0.05, cav_back - yf0 - 0.15, 0.06), loc=(0, (cav_back + yf0 + 0.15) / 2, 0.06), mat="ember")
    yl = yf0 + 0.8
    a.beam((-0.85, yl - 0.25, 0.22), (0.85, yl - 0.1, 0.22), 0.15, sides=5, mat="charcoal", end_mat="ember")
    a.beam((-0.8, yl + 0.2, 0.22), (0.8, yl + 0.3, 0.25), 0.15, sides=5, mat="wood_dark", end_mat="ember")
    a.beam((-0.7, yl - 0.35, 0.3), (0.32, yl + 0.35, 0.74), 0.13, sides=5, mat="charcoal", end_mat="ember")
    a.beam((0.7, yl - 0.35, 0.3), (-0.32, yl + 0.35, 0.74), 0.13, sides=5, mat="wood_dark", end_mat="ember")
    a.flame(1.5, 0.72, loc=(0, yl, 0.24), tongues=5)
    for s in (-1, 1):
        a.flame(0.95, 0.42, loc=(s * 0.6, yl + 0.05, 0.22), tongues=4)
    for (ex, ey) in ((-0.66, -0.3), (-0.25, -0.45), (0.3, -0.4), (0.7, -0.26)):
        a.cyl(0.1, 0.06, 0.08, 5, loc=(ex, yf0 + 0.5 + ey, 0.1), mat="ember")
    # broad square chimney: base course, glowing-slit course, open-topped rim course
    cs, cd, ch_y = 1.2, 0.48, 0.1
    cz = [(2.95, 0.8), (3.75, 0.88), (4.63, 0.84)]
    for k, (z0, h) in enumerate(cz):
        par = k == 1
        span = (-cs, cs) if par else (-cs + cd, cs - cd)
        if k == 1:  # left stone, slit, mullion, slit, right stone
            for x0, x1 in ((-cs, -0.34), (-0.13, 0.13), (0.34, cs)):
                block((x1 - x0 - 0.06, cd, h - 0.08), ((x0 + x1) / 2, ch_y - cs + cd / 2, z0 + h / 2))
            for s in (-1, 1):
                a.box((0.18, 0.05, 0.66), loc=(s * 0.235, ch_y - cs + cd * 0.45, z0 + h / 2), mat="glow_orange")
                a.box((0.22, 0.1, h - 0.1), loc=(s * 0.235, ch_y - cs + cd * 0.75, z0 + h / 2), mat="charcoal")
                for zz in (z0 + 0.06, z0 + h - 0.06):
                    a.box((0.22, cd - 0.06, 0.1), loc=(s * 0.235, ch_y - cs + cd / 2, zz), mat="stone_dark")
        else:
            row_x(span[0], span[1], ch_y - cs + cd / 2, z0, h, cd, L=1.15)
        row_x(span[0], span[1], ch_y + cs - cd / 2, z0, h, cd, L=1.15)
        ya, yb2 = (-cs + cd, cs - cd) if par else (-cs, cs)
        for s in (-1, 1):
            row_y(ch_y + ya, ch_y + yb2, s * (cs - cd / 2), z0, h, cd, L=1.15)
    a.box((2 * cs - 2 * cd + 0.06, 2 * cs - 2 * cd + 0.06, 2.3), loc=(0, ch_y, 3.0), base=True, mat="charcoal")
    co = [v.co for v in a.bm.verts]
    off = Vector(((min(c.x for c in co) + max(c.x for c in co)) / 2,
                  (min(c.y for c in co) + max(c.y for c in co)) / 2, min(c.z for c in co)))
    top = max(c.z for c in co)
    obj = done(a)

    def local(p):
        return tuple(Vector(p) - off)

    vfx.add(obj, "forge_fire", local((0, yl, 0.6)))
    vfx.add(obj, "chimney_smoke", local((0, ch_y, top + 0.1)))
    vfx.add(obj, "heat_glow", local((0, ch_y - cs - 0.15, cz[1][0] + cz[1][1] / 2)))
    for e in vfx.sockets(obj):
        print(f"FB03 socket {e.name}: {tuple(round(c, 2) for c in e.location)}")
    return obj


# ---------------------------------------------------------------------------
# Containers
# ---------------------------------------------------------------------------


def barrel():
    a = fk.Asset("Barrel", CAT)
    H, R0, Rm, n = 2.85, 1.27, 1.56, 14

    def r_at(z):
        return R0 + (Rm - R0) * math.sin(PI * z / H)

    zs = [0, 0.32, 0.8, 1.42, 2.05, 2.53, H]
    for i in range(n):
        a0 = 2 * PI * i / n + 0.012
        a1 = 2 * PI * (i + 1) / n - 0.012
        top = H + a.rng.uniform(-0.04, 0.03)
        secs = []
        for z in zs:
            z = top if z == H else z
            ro, ri = r_at(z), r_at(z) - 0.13
            secs.append([(ro * math.cos(a0), ro * math.sin(a0), z), (ro * math.cos(a1), ro * math.sin(a1), z),
                         (ri * math.cos(a1), ri * math.sin(a1), z), (ri * math.cos(a0), ri * math.sin(a0), z)])
        loft(a, secs, "wood", t=tint(a, 0.12))
        # painted grain running down the stave, between the hoops
        am = (a0 + a1) / 2 + a.rng.uniform(-0.05, 0.05)
        cf = math.cos((a1 - a0) / 2)
        nv = Vector((math.cos(am), math.sin(am), 0))
        sd = Vector((-math.sin(am), math.cos(am), 0))
        z0g = a.rng.uniform(0.9, 1.1)
        L = a.rng.uniform(0.55, 0.85)
        pts = [nv * (r_at(z0g + L * k / 3) * cf + 0.012) + Vector((0, 0, z0g + L * k / 3)) for k in range(4)]
        streak(a, pts, sd, 0.06, "wood_dark", (0, 0, 1.5))
    lathe(a, [(R0 - 0.1, 0.05), (R0 - 0.1, 0.15)], n, "wood_dark", off=0)
    lathe(a, [(R0 - 0.09, H - 0.32), (R0 - 0.09, H - 0.16)], n, "wood_light", off=0)
    for dx in (-0.38, 0.38):
        a.box((0.04, 2.0, 0.03), loc=(dx, 0, H - 0.16), mat="wood_dark")
    for zc, hh in ((0.66, 0.46), (H - 0.45, 0.44)):
        secs = []
        for j in range(n):
            ang = 2 * PI * j / n
            zlo, zhi = zc - hh / 2, zc + hh / 2
            ri0, ri1 = r_at(zlo) - 0.01, r_at(zhi) - 0.01
            secs.append([(ri0 * math.cos(ang), ri0 * math.sin(ang), zlo),
                         ((ri0 + 0.09) * math.cos(ang), (ri0 + 0.09) * math.sin(ang), zlo),
                         ((ri1 + 0.09) * math.cos(ang), (ri1 + 0.09) * math.sin(ang), zhi),
                         (ri1 * math.cos(ang), ri1 * math.sin(ang), zhi)])
        loft(a, secs, "iron_dark", wrap=True)
        for k in range(n):
            ang = 2 * PI * (k + 0.5) / n
            rr = r_at(zc) * math.cos(PI / n) + 0.07
            bolt(a, (rr * math.cos(ang), rr * math.sin(ang), zc), (PI / 2, 0, ang + PI / 2), r=0.1)
    return done(a)


def supply_crate():
    a = fk.Asset("SupplyCrate", CAT)
    S, Hc, b = 3.0, 2.8, 0.36
    h = S / 2
    a.box((S - 0.3, S - 0.3, Hc - 0.3), loc=(0, 0, 0.15), base=True, mat="wood_dark")
    q = h - b / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            gtim(a, (sx * q - b / 2, sy * q - b / 2, b), (sx * q + b / 2, sy * q + b / 2, Hc - b), mat="wood_light",
                 ends=False, faces=("-x" if sx < 0 else "+x") + ("-y" if sy < 0 else "+y"))
    for z in (b / 2, Hc - b / 2):
        for sy in (-1, 1):
            gtim(a, (-h + b, sy * q - b / 2, z - b / 2), (h - b, sy * q + b / 2, z + b / 2),
                 mat="wood_light", ends=False, faces=("-y" if sy < 0 else "+y") + ("+z" if z > 1 else ""))
        for sx in (-1, 1):
            gtim(a, (sx * q - b / 2, -h + b, z - b / 2), (sx * q + b / 2, h - b, z + b / 2),
                 mat="wood_light", ends=False, faces=("-x" if sx < 0 else "+x") + ("+z" if z > 1 else ""))
    # chunky corner blocks, a round bolt on each outer side face
    cbs = b + 0.08
    for sx in (-1, 1):
        for sy in (-1, 1):
            for z in (cbs / 2 - 0.0, Hc - cbs / 2):
                a.plank((cbs, cbs, cbs), loc=(sx * (h - cbs / 2 + 0.04), sy * (h - cbs / 2 + 0.04), z),
                        mat="wood_light")
                bolt(a, (sx * (h - cbs / 2 + 0.04), sy * (h + 0.04), z), FRONT if sy < 0 else BACK, r=0.12, mat="charcoal")
                bolt(a, (sx * (h + 0.04), sy * (h - cbs / 2 + 0.04), z), RIGHT if sx > 0 else LEFT, r=0.12, mat="charcoal")
    # vertical plank panels, recessed
    iw, ih = S - 2 * b, Hc - 2 * b
    m = 4
    pw = iw / m
    for i in range(m):
        c = -iw / 2 + pw * (i + 0.5)
        for sy in (-1, 1):
            gplank(a, (pw - 0.04, 0.1, ih + 0.02), loc=(c, sy * (h - 0.13), Hc / 2), mat="wood",
                   faces="-y" if sy < 0 else "+y")
        for sx in (-1, 1):
            gplank(a, (0.1, pw - 0.04, ih + 0.02), loc=(sx * (h - 0.13), c, Hc / 2), mat="wood",
                   faces="-x" if sx < 0 else "+x")
    tw = iw / 3
    for i in range(3):
        gplank(a, (tw - 0.04, iw + 0.02, 0.1), loc=(-iw / 2 + tw * (i + 0.5), 0, Hc - 0.17), mat="wood", faces="+z")
    # X braces on every side
    L = math.hypot(iw, ih) - 0.12
    ang = math.atan2(ih, iw)
    for sy in (-1, 1):
        for k, s in enumerate((-1, 1)):
            gplank(a, (L, 0.1, 0.3), loc=(0, sy * (h - 0.05 - 0.035 * k), Hc / 2), rot=(0, s * ang, 0),
                   mat="wood_light", faces="-y" if sy < 0 else "+y")
    for sx in (-1, 1):
        for k, s in enumerate((-1, 1)):
            gplank(a, (0.1, L, 0.3), loc=(sx * (h - 0.05 - 0.035 * k), 0, Hc / 2), rot=(s * ang, 0, 0),
                   mat="wood_light", faces="-x" if sx < 0 else "+x")
    return done(a)


def clay_pot():
    a = fk.Asset("ClayStoragePot", CAT)
    n = 12
    prof = [(0.8, 0.0), (1.0, 0.07), (1.17, 0.22), (1.28, 0.42), (1.335, 0.66), (1.345, 0.92), (1.32, 1.17),
            (1.25, 1.38), (1.13, 1.56), (0.98, 1.71), (0.86, 1.83), (0.8, 1.9), (0.83, 1.96)]
    off0 = -PI / 2 - PI / n
    lathe(a, prof, n, "clay", cap0=True, cap1=True)

    def r_at(z):
        for (r0, z0), (r1, z1) in zip(prof, prof[1:]):
            if z0 <= z <= z1:
                return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
        return prof[-1][0]

    # broad flat lid with a raised centre and a chunky octagonal knob
    lathe(a, [(0.84, 1.94), (0.99, 1.98), (1.02, 2.12), (0.97, 2.19), (0.7, 2.21)], n, "clay", t=1.05)
    lathe(a, [(0.68, 2.19), (0.63, 2.25), (0.34, 2.27)], n, "clay", t=1.1, cap0=False)
    a.cyl(0.16, 0.16, 0.08, 8, loc=(0, 0, 2.25), mat="clay", tint=0.86, twist=PI / 8)
    a.cyl(0.31, 0.29, 0.25, 8, loc=(0, 0, 2.31), mat="clay", tint=1.0, twist=PI / 8)
    a.cyl(0.29, 0.19, 0.07, 8, loc=(0, 0, 2.56), mat="clay", tint=1.12, twist=PI / 8)
    # one broad band high on the shoulder, a narrow one near the foot
    for z0, z1, g in ((1.4, 1.52, 0.03), (0.33, 0.4, 0.025)):
        lathe(a, [(r_at(z0) + g, z0), (r_at(z1) + g, z1)], n, "clay_light", cap0=False, cap1=False)

    def folded(phi_e, zc, hw, hh, mat, off):
        """Diamond centred on the vertical edge at angle phi_e, folded flat onto the two facets beside it."""
        r = r_at(zc)
        V0 = Vector((r * math.cos(phi_e), r * math.sin(phi_e), 0))
        for sg in (-1, 1):
            V1 = Vector((r * math.cos(phi_e + sg * 2 * PI / n), r * math.sin(phi_e + sg * 2 * PI / n), 0))
            T = (V1 - V0).normalized()
            pc = phi_e + sg * PI / n
            N = Vector((math.cos(pc), math.sin(pc), 0))
            q = [V0 + Vector((0, 0, zc + hh)), V0 + Vector((0, 0, zc - hh)), V0 + T * hw + Vector((0, 0, zc))]
            inner = [a.bm.verts.new(p + N * off) for p in q]
            outer = [a.bm.verts.new(p + N * (off + 0.016)) for p in q]
            a.bm.faces.new(inner)
            a.bm.faces.new(list(reversed(outer)))
            for i in range(3):
                a.bm.faces.new((inner[i], inner[(i + 1) % 3], outer[(i + 1) % 3], outer[i]))
            a._finish(inner + outer, mat, tint=1.0)

    # big concentric diamonds on every other edge, small diamonds above and below between them
    for j in range(n):
        phi = off0 + 2 * PI * j / n
        if j % 2 == 0:
            for li, (hw, hh, mat) in enumerate(((0.46, 0.43, "clay_light"), (0.34, 0.31, "clay"),
                                                (0.2, 0.18, "clay_light"))):
                folded(phi, 0.9, hw, hh, mat, 0.006 + 0.014 * li)
        else:
            folded(phi, 1.2, 0.11, 0.12, "clay_light", 0.006)
            folded(phi, 0.62, 0.09, 0.1, "clay_light", 0.006)
    return done(a)


def woven_basket():
    a = fk.Asset("WovenBasket", CAT)
    ns, rows = 16, 5
    z0, dz = 0.2, 0.15
    zt = 0.93

    def R(z):
        return 0.98 + 0.3 * (z / zt)

    # closed wall behind the weave: reads as the dark gaps between strands
    rings = []
    for z, dr in ((0.06, 0.05), (zt - 0.02, 0.05), (zt - 0.02, 0.12), (0.1, 0.12)):
        rings.append([((R(z) - dr) * math.cos(2 * PI * j / ns), (R(z) - dr) * math.sin(2 * PI * j / ns), z)
                      for j in range(ns)])
    loft(a, rings, "bark", t=0.8, wrap=True)
    # strands: each row runs over two stakes then tucks behind one, offset row by row
    for k in range(rows):
        z = z0 + k * dz
        for i in range(ns // 2):
            th0 = 2 * PI * (2 * i + (k % 2)) / ns
            span = 2 * PI / ns * 0.84
            pts, radii = [], []
            for t in (-1.0, -0.6, 0.0, 0.6, 1.0):
                th = th0 + t * span
                r = R(z) + 0.045 * (1 - t * t) - 0.015
                pts.append((r * math.cos(th), r * math.sin(th), z))
                f = 1.0 - 0.4 * abs(t) ** 2
                radii.append((0.055 * f, 0.07 * f))
            sweep(a, pts, radii, "wicker", sides=4, phase=0.0, up=(0, 0, 1),
                  t=1.0 + a.rng.uniform(-0.08, 0.08) + (0.04 if k % 2 else -0.03))
    # painted strands on the inside face, staggered the other way
    for k in range(rows):
        z = z0 + k * dz
        for i in range(ns // 2):
            th0 = 2 * PI * (2 * i + 1 - (k % 2)) / ns
            pts = []
            for t in (-1, -0.33, 0.33, 1):
                th = th0 + t * 2 * PI / ns * 0.85
                r = R(z) - 0.135
                pts.append(Vector((r * math.cos(th), r * math.sin(th), z)))
            streak(a, pts, Vector((0, 0, 1)), 0.125, "wicker", (R(z) * 0.95 * math.cos(th0), R(z) * 0.95 * math.sin(th0), z))
    # woven floor with dark spokes
    a.cyl(R(0) - 0.06, R(0) - 0.06, 0.12, ns, mat="wicker", tint=0.9)
    for i in range(6):
        th = PI * i / 6
        p = Vector((math.cos(th), math.sin(th), 0)) * (R(0) - 0.15)
        streak(a, [Vector((0, 0, 0.13)) - p, Vector((0, 0, 0.13)) - p * 0.33, Vector((0, 0, 0.13)) + p * 0.33,
                   Vector((0, 0, 0.13)) + p], Vector((-math.sin(th), math.cos(th), 0)), 0.06, "rope_dark", (0, 0, 0.05))
    # thick rolled rim: two bundled rods, bound by leather wraps
    M = 24
    for zz, dr, rad, sides in ((zt + 0.05, 0.0, (0.105, 0.105), 6), (zt - 0.1, 0.075, (0.08, 0.08), 5)):
        pts = []
        for j in range(M):
            th = 2 * PI * j / M
            r = R(zt) + dr
            pts.append((r * math.cos(th), r * math.sin(th), zz))
        sweep(a, pts, [rad] * M, "wicker", sides=sides, closed=True, phase=0.0, up=(0, 0, 1), t=1.06)
    for i in range(11):
        th = 2 * PI * (i + 0.3) / 11
        c = Vector((math.cos(th), math.sin(th), 0)) * (R(zt) + 0.035)
        v = a.torus(0.13, 0.045, seg=6, rseg=4, mat="bark", squash=1.0)
        a.transform(v, loc=(c.x, c.y, zt - 0.03), rot=(PI / 2, 0, th), scale=(1.0, 1.3, 1.7))
    return done(a)


# ---------------------------------------------------------------------------
# Rendering: per-asset camera angles
# ---------------------------------------------------------------------------

VIEWS = {  # azimuth, elevation (degrees); positive azimuth swings to the asset's right
    "SmallChest": (30, 22), "LargeChest": (30, 20), "OpenChest": (30, 26), "StorageCabinet": (28, 16),
    "EldersTotem": (-14, 5), "QuestBoard": (16, 15), "LedgerLectern": (24, 22), "WeaponRack": (32, 16),
    "AnvilLarge": (24, 18), "AnvilSmall": (24, 18), "CraftingWorkbench": (24, 24),
    "SmeltingFurnace": (26, 18), "Barrel": (20, 18), "SupplyCrate": (30, 20), "ClayStoragePot": (16, 16),
    "WovenBasket": (14, 34), "EldersTotemTall": (-14, 5),
}


def frame_fit(obj, azimuth, elevation, margin=1.12):
    """Like fk.frame, but fits the bounding sphere to the narrower (vertical) field of view."""
    scene = bpy.context.scene
    cam = bpy.data.objects["FB_Cam"]
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    aspect = scene.render.resolution_x / scene.render.resolution_y
    half = cam.data.angle / 2  # sensor fit AUTO: angle spans the wider side
    tan_h = math.tan(half) if aspect >= 1 else math.tan(half) * aspect
    tan_v = tan_h / aspect
    az, el = math.radians(azimuth), math.radians(elevation)
    direction = Vector((math.sin(az), -math.cos(az), math.tan(el))).normalized()
    right = Vector((0, 0, 1)).cross(direction).normalized()
    up = direction.cross(right).normalized()
    # distance so every bbox corner projects inside the frame
    dist = 0.0
    for c in corners:
        o = c - centre
        x, y, z = o.dot(right), o.dot(up), o.dot(direction)
        dist = max(dist, z + abs(x) * margin / tan_h, z + abs(y) * margin / tan_v)
    cam.location = centre + direction * dist
    cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.data.objects["FB_Ground"].location = (centre.x, centre.y, min(c.z for c in corners))


def render_cell(obj, path, res, az, el, samples=32, ortho=None):
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
    cam = bpy.data.objects["FB_Cam"]
    if ortho:  # debug: "front" or "top" orthographic check of alignment
        corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        centre = sum(corners, Vector()) / 8
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = max(obj.dimensions) * 1.25
        if ortho == "front":
            cam.location = centre + Vector((0, -40, 0))
            cam.rotation_euler = (PI / 2, 0, 0)
        else:
            cam.location = centre + Vector((0, 0, 40))
            cam.rotation_euler = (0, 0, 0)
        bpy.data.objects["FB_Ground"].location = (centre.x, centre.y, min(c.z for c in corners))
    else:
        cam.data.type = "PERSP"
        frame_fit(obj, az, el)
    scene.render.filepath = path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    cam.data.type = "PERSP"
    for o in hidden:
        o.hide_render = False


def sheet_fill(cell_path):
    """Backdrop colour of a rendered cell (its top-left pixel), as stored in the PNG."""
    img = bpy.data.images.load(cell_path, check_existing=False)
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(img)
    return px[h - 2, 1, :3]


def render_sheet_views(objs, path, cols=4, cell=(512, 384)):
    base, _ = os.path.splitext(path)
    cell_paths = []
    for i, o in enumerate(objs):
        az, el = VIEWS.get(o.name, (fk.DEFAULT_AZIMUTH, fk.DEFAULT_ELEVATION))
        p = f"{base}_cells/{i + 1:02d}_{o.name}.png"
        render_cell(o, p, cell, az, el)
        cell_paths.append(p)
    rows = math.ceil(len(objs) / cols)
    w, h = cell
    sheet = np.ones((rows * h, cols * w, 4), dtype=np.float32)
    sheet[..., :3] = sheet_fill(cell_paths[0])  # empty cells match the backdrop
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


BUILDERS = None


def main():
    fk.reset_file()
    test = os.environ.get("FB03_TOTEM")  # totem-only preview: no save, one big cell
    if test:
        o = elders_totem()
        az, el = VIEWS["EldersTotem"]
        render_cell(o, test, (640, 640), az, el)
        print("FB03 TEST", test)
        return
    builders = [small_chest, large_chest, open_chest, storage_cabinet, elders_totem, quest_board,
                ledger_lectern, weapon_rack, anvil_large, anvil_small, crafting_workbench,
                smelting_furnace, barrel, supply_crate, clay_pot, woven_basket, elders_totem_tall]
    fast = os.environ.get("FB03_FAST")  # dev preview: build only these builders, cells to FB03_OUT, no save
    if fast:
        out = os.environ["FB03_OUT"]
        for i, b in enumerate(builders):
            if b.__name__ not in fast.split(","):
                continue
            o = b()
            az, el = VIEWS[o.name]
            render_cell(o, f"{out}/{i + 1:02d}_{o.name}.png", (512, 384), az, el)
            for kind in os.environ.get("FB03_ORTHO", "").split(","):
                if kind:
                    render_cell(o, f"{out}/{i + 1:02d}_{o.name}_{kind}.png", (512, 384), 0, 0, ortho=kind)
            o.hide_render = True
        return
    only = os.environ.get("FB03_ONLY")
    objs = [b() for b in builders]
    fk.layout_row(objs)
    for o in objs:
        assert tuple(o.rotation_euler) == (0.0, 0.0, 0.0)
    fk.save(os.path.join(ROOT, "assets", "03_furnishings.blend"))
    render = [o for o in objs if not only or o.name in only.split(",")]
    render_sheet_views(render, os.path.join(ROOT, "renders", "03_furnishings.png"), cols=4)
    print("FB03 DONE", sum(o["tris"] for o in objs))


main()
