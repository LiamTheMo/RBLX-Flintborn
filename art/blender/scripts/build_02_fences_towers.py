"""Build sheet 02: Fences & Towers.

Run headless:
    blender --background --factory-startup --python art/blender/scripts/build_02_fences_towers.py
"""

import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "lib"))
import flintkit as fk  # noqa: E402
import vfx  # noqa: E402

# Hand-painted tone on top of the palette (linear RGB multipliers): the sheet's
# wood is a deeper, redder brown and its carved tips a warmer, brighter tan.
TONE = {
    "wood": (0.76, 0.62, 0.48),
    "wood_dark": (0.82, 0.68, 0.55),
    "wood_light": (0.84, 0.68, 0.52),
    "wood_end": (1.2, 1.0, 0.86),
    "rope": (1.0, 0.86, 0.68),
    "thatch": (1.62, 1.42, 1.4),
    "thatch_dark": (1.45, 1.26, 1.2),
}
# Per-facet brightness spread: hewn wood reads as many small carved planes.
FACET_VAR = {"wood": 0.16, "wood_dark": 0.1, "wood_light": 0.12, "wood_end": 0.07, "iron": 0.05}
# Per-vertex spread, blended across each facet: painterly streaks and mottling.
VERT_VAR = {"wood": 0.16, "wood_dark": 0.12, "wood_light": 0.14, "wood_end": 0.1}

ROPE_K = 0.21  # rope tube radius as a fraction of the stake radius
ROPE_SINK = 0.7  # how far a wrap bites into the wood, in tube radii (hides its inner facet)
# The sheet draws the fence pieces stockier than their first build: panels about
# 0.8 and the gate 0.85 of their original height (width stays 10 for tiling).
FENCE_H = 0.8
GATE_H = 0.85


# ---------------------------------------------------------------------------
# Low-level helpers (all take an fk.Asset)
# ---------------------------------------------------------------------------


def paint(a, faces, mat, tint=1.0, smooth=False):
    mi = a._mi(mat)
    for f in faces:
        f.material_index = mi
        f.smooth = smooth
        for loop in f.loops:
            loop[a.tint_layer] = (tint, tint, tint, 1.0)


def fix_normals(a, faces):
    bmesh.ops.recalc_face_normals(a.bm, faces=faces)


def tone(a):
    layer = a.tint_layer
    a.bm.verts.index_update()
    vj = [1.0 + a.rng.uniform(-1, 1) for _ in a.bm.verts]
    for f in a.bm.faces:
        m = a.mats[f.material_index]
        k = TONE.get(m, (1.0, 1.0, 1.0))
        var = FACET_VAR.get(m, 0.0)
        vv = VERT_VAR.get(m, 0.0)
        j = 1.0 + a.rng.uniform(-var, var) if var else 1.0
        for loop in f.loops:
            c = loop[layer]
            jj = j * (1.0 + (vj[loop.vert.index] - 1.0) * vv)
            loop[layer] = (c[0] * k[0] * jj, c[1] * k[1] * jj, c[2] * k[2] * jj, 1.0)


def fit_x(a, width):
    """Tiny X rescale so the asset's bounding box is exactly `width` wide."""
    xs = [v.co.x for v in a.bm.verts]
    lo, hi = min(xs), max(xs)
    c, s = (lo + hi) / 2, width / (hi - lo)
    for v in a.bm.verts:
        v.co.x = c + (v.co.x - c) * s


def done(a, width=None):
    if width:
        fit_x(a, width)
    tone(a)
    return a.finish()


def frame_from(d, up_hint=(0, 0, 1)):
    """Rotation (Euler) whose local X runs along d."""
    d = Vector(d).normalized()
    up = Vector(up_hint)
    if abs(d.dot(up)) > 0.95:
        up = Vector((0, 1, 0))
    side = up.cross(d).normalized()
    n = d.cross(side).normalized()
    return Matrix((d, side, n)).transposed().to_euler()


def bar(a, p1, p2, w, t, mat="wood", up=(0, 0, 1), bevel=None):
    """Squared timber (beveled box) from p1 to p2, `w` wide and `t` thick."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    return a.plank((d.length, w, t), loc=(p1 + p2) / 2, rot=frame_from(d, up), mat=mat, bevel=bevel)


# ---------------------------------------------------------------------------
# Rope: twisted cord
# ---------------------------------------------------------------------------


def _axis_out(axis, p):
    """Unit vector from the lashed timber's axis out to point p."""
    kind, u, v = axis
    if kind == "z":
        d = Vector((p.x - u, p.y - v, 0))
    elif kind == "x":
        d = Vector((0, p.y - u, p.z - v))
    else:
        d = Vector((p.x - u, 0, p.z - v))
    return d.normalized()


def cord(a, pts, th, closed=True, tint=None, dark=0.7, axis=None, lump=0.2):
    """Twisted rope: a pentagonal tube with a ridge facing outward. Its facets
    alternate light and dark in a checker and bulge alternately, so the strands
    read as spiralling round the cord. When `axis` names the timber it is wrapped
    round (("z", x, y) for a post, ("x", y, z) / ("y", x, z) for a log), the
    inner facet, buried in the wood, is left out."""
    bm = a.bm
    P = [Vector(p) for p in pts]
    n = len(P)
    S = 5
    t0 = tint if tint is not None else 1.0 + a.rng.uniform(-0.06, 0.06)
    rings = []
    for i, p in enumerate(P):
        if closed:
            tg = P[(i + 1) % n] - P[i - 1]
        else:
            tg = P[min(i + 1, n - 1)] - P[max(i - 1, 0)]
        tg.normalize()
        if axis:
            out = _axis_out(axis, p)
            out = (out - tg * out.dot(tg)).normalized()
        else:
            up = Vector((0, 0, 1)) if abs(tg.z) < 0.9 else Vector((1, 0, 0))
            out = tg.cross(up).normalized()
        side = tg.cross(out).normalized()
        if side.z < 0:
            side = -side
        ring_ = []
        for j in range(S):
            # wraps: one facet faces out, one up, one down-out; the two inner ones
            # are buried in the wood
            ph = 2 * math.pi * j / S + (math.radians(-26) if axis else 0.0)
            k = 1.0 + (lump if (i + j) % 2 else -lump * 0.5) if j in (0, 1) else 1.0
            ring_.append(bm.verts.new(p + th * k * (math.cos(ph) * out + math.sin(ph) * side)))
        rings.append(ring_)
    faces, shade = [], []
    segs = n if closed else n - 1
    for i in range(segs):
        r1, r2 = rings[i], rings[(i + 1) % n]
        c = (P[i] + P[(i + 1) % n]) / 2
        for j in range(S):
            if axis and j in (2, 3):  # inner facets: buried in the wood
                continue
            f = bm.faces.new((r1[j], r1[(j + 1) % S], r2[(j + 1) % S], r2[j]))
            f.normal_update()
            if f.normal.dot(f.calc_center_median() - c) < 0:
                f.normal_flip()
            faces.append(f)
            if (i + j) % 2:
                shade.append(f)
    caps = []
    if not closed:
        for rr, q, sgn in ((rings[0], P[0], -1), (rings[-1], P[-1], 1)):
            f = bm.faces.new(rr)
            f.normal_update()
            tg = (P[1] - P[0]) if sgn < 0 else (P[-1] - P[-2])
            if f.normal.dot(tg) * sgn < 0:
                f.normal_flip()
            caps.append(f)
    light = [f for f in faces if f not in set(shade)] + caps
    # rope is the one smooth-shaded part: the sheet paints it as round cord
    paint(a, light, "rope", t0, smooth=True)
    paint(a, shade, "rope", t0 * dark, smooth=True)
    return [v for r in rings for v in r]


def ring(a, x, y, r, z, th, seg=8):
    """One rope wrap round a post of radius r (centre height z)."""
    R = r + th * (1 - ROPE_SINK)
    a0 = a.rng.uniform(0, 2 * math.pi)
    tilt = a.rng.uniform(-0.04, 0.04)
    pts = [(x + R * math.cos(a0 + 2 * math.pi * k / seg), y + R * math.sin(a0 + 2 * math.pi * k / seg),
            z + tilt * math.sin(2 * math.pi * k / seg)) for k in range(seg)]
    return cord(a, pts, th, axis=("z", x, y))


def band(a, x, y, r, zc, count=2, th=None, gap=None, seg=None):
    """`count` stacked wraps centred on height zc."""
    th = th or r * ROPE_K
    gap = gap or th * 2.25
    seg = seg or (14 if r >= 1.0 else 10)
    out = []
    for i in range(count):
        out += ring(a, x, y, r, zc + (i - (count - 1) / 2) * gap, th, seg=seg)
    return out


def x_lash(a, x, y, r, zc, th=0.13, tilt=0.42, seg=8):
    """Two wraps crossing diagonally round a post (an X lashing)."""
    out = []
    R = r + th * (1 - ROPE_SINK) + 0.04
    for s in (-1, 1):
        a0 = a.rng.uniform(0, 2 * math.pi)
        pts = []
        for k in range(seg):
            ang = 2 * math.pi * k / seg
            pts.append((x + R * math.cos(ang), y + R * math.sin(ang),
                        zc + s * math.tan(tilt) * R * math.cos(ang - a0)))
        out += cord(a, pts, th, axis=("z", x, y))
    out += band(a, x, y, r, zc, 1, th=th, seg=seg)
    return out


def rope_allow(r):
    """How far a wrap sticks out past the stake surface."""
    return r * ROPE_K * (2 - ROPE_SINK)


# ---------------------------------------------------------------------------
# Wood: hand-hewn stakes and posts
# ---------------------------------------------------------------------------


def carved(a, r, h, loc=(0, 0, 0), sides=9, tip=None, flat=False, chamfer=0.32, notch=0.42, top_k=0.74):
    """Hand-hewn post: an irregular faceted body (uneven facet widths, a wobbling
    radius) with either a carved pencil tip, whose pale cut facets end in a
    jagged collar over the bark, or a flat pale chamfered top."""
    bm, rng, N = a.bm, a.rng, sides
    x0, y0, z0 = loc
    t = 1.0 + rng.uniform(-0.07, 0.07)
    base = rng.uniform(0, 2 * math.pi)
    angs = [base + 2 * math.pi * (k + rng.uniform(-0.18, 0.18)) / N for k in range(N)]
    tw = rng.uniform(-0.05, 0.05)

    def V(rad, ang, z, dx=0.0, dy=0.0):
        return bm.verts.new((x0 + dx + rad * math.cos(ang), y0 + dy + rad * math.sin(ang), z0 + z))

    def jr(k=0.045):
        return r * (1 + rng.uniform(-k, k))

    ztop = h - r * chamfer if flat else h - (tip if tip is not None else h * 0.24)
    # body: three stacked sections whose verts wobble independently, so each long
    # facet breaks into a few chisel planes that catch the light differently
    R0 = [V(r * 1.04 * (1 + rng.uniform(-0.03, 0.03)), q, 0) for q in angs]
    body, prev = [], R0
    zs = sorted((ztop * rng.uniform(0.18, 0.3), ztop * rng.uniform(0.42, 0.55), ztop * rng.uniform(0.68, 0.8)))
    for zi, zz in enumerate(zs):
        cur = [V(jr(0.06), q + tw * (zi + 1) / 2 + rng.uniform(-0.04, 0.04), zz + rng.uniform(-0.25, 0.25) * r)
               for q in angs]
        body += [bm.faces.new((prev[k], prev[(k + 1) % N], cur[(k + 1) % N], cur[k])) for k in range(N)]
        prev = cur
    R1 = prev
    pale = []
    if flat:
        R2 = [V(jr(0.03), q + 2 * tw, ztop + rng.uniform(-0.05, 0.05) * r) for q in angs]
        body += [bm.faces.new((R1[k], R1[(k + 1) % N], R2[(k + 1) % N], R2[k])) for k in range(N)]
        R3 = [V(r * top_k * (1 + rng.uniform(-0.04, 0.04)), q + 2 * tw, h + rng.uniform(-0.04, 0.04))
              for q in angs]
        pale += [bm.faces.new((R2[k], R2[(k + 1) % N], R3[(k + 1) % N], R3[k])) for k in range(N)]
        pale.append(bm.faces.new(R3))
    else:
        tp = h - ztop
        C = [V(jr(0.03), q + 2 * tw, ztop + notch * r * rng.uniform(0.55, 1.1)) for q in angs]
        M = []
        for k in range(N):
            c1, c2 = C[k].co, C[(k + 1) % N].co
            m = (c1 + c2) / 2
            M.append(bm.verts.new((m.x, m.y, z0 + ztop - notch * r * rng.uniform(0.45, 0.9))))
        body += [bm.faces.new((R1[k], R1[(k + 1) % N], C[(k + 1) % N], M[k], C[k])) for k in range(N)]
        T = []
        for k in range(N):
            d = Vector((M[k].co.x - x0, M[k].co.y - y0, 0))
            ang = math.atan2(d.y, d.x)
            T.append(V(r * 0.66 * (1 + rng.uniform(-0.06, 0.06)), ang, ztop + tp * 0.44))
        apex = bm.verts.new((x0 + rng.uniform(-0.05, 0.05) * r, y0 + rng.uniform(-0.05, 0.05) * r, z0 + h))
        for k in range(N):
            k1 = (k + 1) % N
            pale.append(bm.faces.new((C[k], M[k], C[k1], T[k])))
            pale.append(bm.faces.new((C[k1], T[k1], T[k])))
            pale.append(bm.faces.new((T[k], T[k1], apex)))
    paint(a, body, "wood", t)
    paint(a, pale, "wood_end", t)
    fix_normals(a, body + pale)
    return list({v for f in body + pale for v in f.verts})


def row_positions(radii, width, overlap=0.06):
    """Scale radii so a straight row of touching stakes with their wraps spans
    exactly `width`. Returns (xs, radii)."""
    def span(k):
        rs = [r * k for r in radii]
        return 2 * sum(rs) - (len(rs) - 1) * overlap + rope_allow(rs[0]) + rope_allow(rs[-1])
    lo, hi = 0.1, 5.0
    for _ in range(50):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if span(mid) < width else (lo, mid)
    rs = [r * lo for r in radii]
    xs = [0.0]
    for i in range(1, len(rs)):
        xs.append(xs[-1] + rs[i - 1] + rs[i] - overlap)
    c = (xs[0] - rs[0] + xs[-1] + rs[-1]) / 2
    return [x - c for x in xs], rs


def palisade(a, pts, radii, heights, bands, tipk=0.24, step=0.07, wraps=2):
    """Stakes with their own rope bands. `bands` is a list of band-centre
    heights, each either a number or a per-stake list."""
    th = sum(radii) / len(radii) * ROPE_K
    for i, ((x, y), r, h) in enumerate(zip(pts, radii, heights)):
        carved(a, r, h, tip=h * tipk, loc=(x, y, 0))
        for b in bands:
            zc = b[i] if isinstance(b, (list, tuple)) else b
            zc += (((i * 7) % 3) - 1) * step + a.rng.uniform(-0.03, 0.03)
            band(a, x, y, r, zc, wraps, th=th)


# ---------------------------------------------------------------------------
# Frames, decks, ladders
# ---------------------------------------------------------------------------


def ladder(a, base, top, across=(1, 0, 0), width=1.7, rungs=6, rail=(0.42, 0.3), rung=(0.36, 0.22),
           extend=0.8):
    """Leaning ladder of squared rails and board rungs with iron bolts."""
    base, top = Vector(base), Vector(top)
    d = top - base
    L = d.length
    d.normalize()
    side = Vector(across).normalized()
    n = side.cross(d).normalized()  # face normal, turned to point away from the wall
    if n.dot(Vector(((base - top).x, (base - top).y, 0))) < 0:
        n = -n
    for sx in (-1, 1):
        p = side * sx * width / 2
        bar(a, base + p, top + d * extend + p, rail[0], rail[1], up=n)
    rot = n.to_track_quat("Z", "Y").to_euler()
    for i in range(rungs):
        s = 0.7 + (L - 1.1) * i / max(rungs - 1, 1)
        p = base + d * s + n * 0.04
        bar(a, p - side * (width / 2 + 0.16), p + side * (width / 2 + 0.16), rung[0], rung[1], up=n)
        for sx in (-1, 1):  # iron bolts where rungs cross the rails
            a.cyl(0.075, 0.06, 0.07, 5, loc=p + side * sx * width / 2 + n * rung[1] * 0.5, rot=rot,
                  mat="iron_edge")


def deck(a, x0, x1, y0, y1, z_top, n, along="x", th=0.42, gap=0.08):
    """Plank floor; planks run `along` x or y with slightly ragged ends."""
    if along == "x":
        w = (y1 - y0 - gap * (n - 1)) / n
        for i in range(n):
            y = y0 + w / 2 + i * (w + gap)
            a.plank((x1 - x0 + a.rng.uniform(-0.2, 0.2), w, th),
                    loc=((x0 + x1) / 2 + a.rng.uniform(-0.1, 0.1), y, z_top - th / 2 + a.rng.uniform(-0.03, 0.03)),
                    rot=(a.rng.uniform(-0.01, 0.01), 0, a.rng.uniform(-0.01, 0.01)), mat="wood_light")
    else:
        w = (x1 - x0 - gap * (n - 1)) / n
        for i in range(n):
            x = x0 + w / 2 + i * (w + gap)
            a.plank((w, y1 - y0 + a.rng.uniform(-0.2, 0.2), th),
                    loc=(x, (y0 + y1) / 2 + a.rng.uniform(-0.1, 0.1), z_top - th / 2 + a.rng.uniform(-0.03, 0.03)),
                    rot=(0, a.rng.uniform(-0.01, 0.01), a.rng.uniform(-0.01, 0.01)), mat="wood_light")


def xbrace(a, p1, p2, p3, p4, r=0.26, normal=(0, -1, 0)):
    """Two crossing braces with an iron bolt at the crossing."""
    a.beam(p1, p2, r, sides=6)
    a.beam(p3, p4, r, sides=6)
    c = (Vector(p1) + Vector(p2) + Vector(p3) + Vector(p4)) / 4
    n = Vector(normal).normalized()
    rot = n.to_track_quat("Z", "Y").to_euler()
    a.cyl(0.2, 0.2, 0.1, 8, loc=c + n * r * 0.9, rot=rot, mat="iron")
    a.cyl(0.1, 0.07, 0.1, 6, loc=c + n * (r * 0.9 + 0.1), rot=rot, mat="iron_edge")


def corner_posts(a, half, r, h, hx=None):
    hx = hx or half
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            carved(a, r, h + a.rng.uniform(-0.12, 0.12), loc=(sx * hx, sy * half, 0), flat=True)
            out.append((sx * hx, sy * half))
    return out


def frame_beam(a, p, q, z, r, overhang=0.45):
    a.beam((p[0], p[1], z + a.rng.uniform(-0.04, 0.04)), (q[0], q[1], z + a.rng.uniform(-0.04, 0.04)),
           r, sides=6, overhang=overhang)


def frame_ring(a, half, z, r, sides=(0, 1, 2, 3), overhang=0.45, hx=None):
    """Beams joining the corner posts at height z. sides: 0 front, 1 right, 2 back, 3 left."""
    hx = hx or half
    c = [(-hx, -half), (hx, -half), (hx, half), (-hx, half)]
    for i in sides:
        frame_beam(a, c[i], c[(i + 1) % 4], z, r, overhang)


# ---------------------------------------------------------------------------
# Fire
# ---------------------------------------------------------------------------


def tongue(a, base, h, r, lean, curl, mat, sides=5):
    """A rounded flame tongue: a tapering loft that leans and curls at the tip."""
    bm = a.bm
    base = Vector(base)
    lean = Vector((lean[0], lean[1], 0))
    prof = [(0.0, 1.0), (0.28, 1.0), (0.55, 0.72), (0.8, 0.38)]
    rings = []
    a0 = a.rng.uniform(0, 2 * math.pi)
    ldir = lean.normalized() if lean.length > 1e-6 else Vector((0, 0, 0))
    for t, k in prof:
        # lean out with height, with a slight S-curl back toward the centre midway
        c = base + Vector((0, 0, h * t)) + lean * (h * t * t) - ldir * curl * h * 0.08 * math.sin(math.pi * t)
        rings.append([bm.verts.new(c + Vector((r * k * math.cos(a0 + 2 * math.pi * j / sides),
                                               r * k * math.sin(a0 + 2 * math.pi * j / sides), 0)))
                      for j in range(sides)])
    tipc = base + Vector((0, 0, h)) + lean * h * 1.25
    tip = bm.verts.new(tipc)
    faces = []
    for i in range(len(rings) - 1):
        for j in range(sides):
            faces.append(bm.faces.new((rings[i][j], rings[i][(j + 1) % sides], rings[i + 1][(j + 1) % sides],
                                       rings[i + 1][j])))
    for j in range(sides):
        faces.append(bm.faces.new((rings[-1][j], rings[-1][(j + 1) % sides], tip)))
    faces.append(bm.faces.new(list(reversed(rings[0]))))
    paint(a, faces, mat, 1.0)
    fix_normals(a, faces)
    return [v for r_ in rings for v in r_] + [tip]


def torch_flame(a, loc, h, r):
    """Painted torch fire: a broad orange body of licking tongues round a yellow
    heart and a pale core, wider at the base like a teardrop."""
    x0, y0, z0 = loc
    out = []
    n = 6
    for i in range(n):
        ph = 2 * math.pi * i / n + a.rng.uniform(-0.25, 0.25)
        dirv = (math.cos(ph), math.sin(ph))
        p = (x0 + dirv[0] * r * 0.52, y0 + dirv[1] * r * 0.52, z0)
        hh = h * (0.78 if i % 2 else 0.5) * a.rng.uniform(0.9, 1.1)  # alternate tall and short licks
        out += tongue(a, p, hh, r * a.rng.uniform(0.5, 0.6), (dirv[0] * 0.05, dirv[1] * 0.05),
                      a.rng.uniform(0.5, 1.0), "fire_outer")
    out += tongue(a, (x0, y0 + r * 0.1, z0), h, r * 0.72, (0.05, -0.04), 0.6, "fire_outer")
    # yellow heart and pale core sit toward the front (-Y) so they show through
    for i, (dx, hk) in enumerate(((-0.32, 0.7), (0.05, 0.85), (0.36, 0.62))):
        out += tongue(a, (x0 + dx * r, y0 - r * 0.42, z0 + 0.03), h * hk, r * 0.46,
                      (dx * 0.25, -0.05), 0.6, "fire_mid")
    out += tongue(a, (x0 + 0.04 * r, y0 - r * 0.62, z0 + 0.05), h * 0.5, r * 0.38, (0, -0.04), 0, "fire_core")
    return out


# ---------------------------------------------------------------------------
# Palisade pieces
# ---------------------------------------------------------------------------


def palisade_panel_a():
    a = fk.Asset("PalisadePanelA", "Fences")
    H = 9.5 * FENCE_H
    xs, rs = row_positions([0.82, 0.84, 0.82, 0.83, 0.82, 0.84], 10.0)
    hs = [h * FENCE_H for h in (9.3, 9.5, 9.35, 9.2, 9.5, 9.4)]
    palisade(a, [(x, 0) for x in xs], rs, hs, [0.17 * H, 0.56 * H])
    return done(a, 10.0)


def palisade_panel_b():
    a = fk.Asset("PalisadePanelB", "Fences")
    H = 9.5 * FENCE_H
    xs, rs = row_positions([0.8, 0.62, 0.78, 0.8, 0.78, 0.68, 0.82], 10.0)
    hs = [h * FENCE_H * 0.95 for h in (9.0, 7.7, 9.4, 10.5, 8.9, 8.1, 9.8)]
    up = [0.55 * H] * 7
    up[4] -= 0.08 * H
    up[5] -= 0.1 * H
    palisade(a, [(x, 0) for x in xs], rs, hs, [0.14 * H, up])
    return done(a, 10.0)


def corner_palisade():
    a = fk.Asset("CornerPalisade", "Fences")
    rp, r = 1.0, 0.9
    d1 = rp + r - 0.08
    p = 2 * r - 0.08
    # corner post at the back right; 3 stakes run left along the back, 4 run
    # toward the front down the right side
    C = Vector((0, 0, 0))
    back = [(C.x - (d1 + p * k), C.y) for k in reversed(range(3))]
    side = [(C.x, C.y - (d1 + p * k)) for k in range(4)]
    pts = back + side
    radii = [r] * 7
    hs = [h * FENCE_H for h in (9.1, 9.4, 8.9, 9.3, 8.8, 9.4, 9.1)]
    palisade(a, pts, radii, hs, [1.9 * FENCE_H, 5.3 * FENCE_H])
    hp = 10.0 * FENCE_H
    carved(a, rp, hp, loc=(C.x, C.y, 0), flat=True)
    band(a, C.x, C.y, rp, hp * 0.7, 2, th=r * ROPE_K)
    return done(a)


def curved_palisade():
    a = fk.Asset("CurvedPalisade", "Fences")
    n, r = 8, 0.68
    pitch = 2 * r - 0.06
    Rc = 6.4  # ~80 degree arc bulging toward the front
    dth = pitch / Rc
    pts = []
    for i in range(n):
        th = (i - (n - 1) / 2) * dth
        pts.append((Rc * math.sin(th), -Rc * math.cos(th)))
    hs = [h * FENCE_H for h in (9.5, 8.8, 8.5, 8.3, 8.5, 9.1, 9.5, 10.1)]
    palisade(a, pts, [r] * n, hs, [1.7 * FENCE_H, 5.4 * FENCE_H])
    return done(a, 10.0)


def palisade_gate():
    a = fk.Asset("PalisadeGate", "Fences")
    W = 10.0
    rp = 1.02
    th = rp * 0.2
    px = W / 2 - rp - rope_allow(rp)
    G = GATE_H
    carved(a, rp * 0.96, 10.0 * G, loc=(-px, 0, 0), flat=True)
    carved(a, rp, 9.4 * G, loc=(px, 0, 0), flat=True)
    band(a, -px, 0, rp * 0.96, 7.4 * G, 3, th=th)  # left (hinge) post: top band only
    band(a, px, 0, rp, 6.6 * G, 3, th=th)
    band(a, px, 0, rp, 1.05, 3, th=th)
    # door leaf: four pointed stakes
    inner = px - rp - 0.02
    n = 4
    r = (2 * inner + 0.15) / (2 * n)
    xs = [-inner + r + i * (2 * r - 0.05) for i in range(n)]
    xs = [x - (xs[0] + xs[-1]) / 2 for x in xs]
    for x, h in zip(xs, [8.1, 8.5, 8.6, 8.2]):
        carved(a, r, h * G - 0.15, tip=1.75, loc=(x, 0.05, 0.15), notch=0.5)
    # Z frame: two chunky boards and a diagonal brace in front of the stakes
    yb = -(r + 0.16)
    rail_w = 2 * inner + 0.1
    zr = (1.3, 5.55 * G)
    for z in zr:
        a.plank((rail_w, 0.38, 0.95), loc=(0, yb - 0.04, z))
    x_lo, x_hi = -inner + 0.55, inner - 0.6
    p1 = Vector((x_lo, yb + 0.02, zr[0] + 0.25))
    p2 = Vector((x_hi, yb + 0.02, zr[1] - 0.25))
    bar(a, p1, p2, 0.85, 0.34, up=(0, -1, 0))
    # iron: hinge brackets round the left post, short straps with two bolts,
    # square plates with one bolt at the latch end
    yf = yb - 0.24
    for z in zr:
        x0 = -inner - 0.05
        a.box((0.5, 0.95, 1.25), loc=(-px + rp * 0.86, -0.05, z), mat="iron", bevel=0.06)
        a.box((1.35, 0.1, 0.8), loc=(x0 + 0.68, yf, z), mat="iron", bevel=0.04)
        for k in range(2):
            a.rivet((x0 + 0.4 + k * 0.62, yf - 0.05, z), normal_rot=(math.pi / 2, 0, 0), r=0.11,
                    mat="iron_edge")
        a.rivet((-px + rp * 0.86, -0.55, z + 0.3), normal_rot=(math.pi / 2, 0, 0), r=0.1, mat="iron_edge")
        a.box((0.75, 0.1, 0.75), loc=(inner - 0.3, yf, z), mat="iron", bevel=0.04)
        a.rivet((inner - 0.3, yf - 0.05, z), normal_rot=(math.pi / 2, 0, 0), r=0.11, mat="iron_edge")
    return done(a, W)


def palisade_end_post():
    a = fk.Asset("PalisadeEndPost", "Fences")
    H, r = 10.5, 1.2
    th = r * 0.19
    carved(a, r, H, tip=H * 0.22, sides=8)
    band(a, 0, 0, r, H * 0.66 - 0.15, 3, th=th)  # just under the tip
    band(a, 0, 0, r, H * 0.27, 2, th=th)
    return done(a)


def palisade_torch_post():
    a = fk.Asset("PalisadeTorchPost", "Fences")
    H, r = 10.0, 1.05
    th = r * 0.19
    carved(a, r, H, tip=H * 0.18, sides=8)
    zu = 5.7
    band(a, 0, 0, r, 2.5, 3, th=th)
    band(a, 0, 0, r, zu + 0.15, 3, th=th)
    hr, tx = 0.5, 2.2
    cup_r = 1.08
    v = []
    zcl = zu - 0.25
    # grey iron clamp block from the post's side to the handle
    v += a.box((tx - r - hr + 0.35, 0.72, 0.72), loc=((r + tx - hr) / 2 + 0.05, 0, zcl), mat="iron", bevel=0.07)
    v += a.rivet(((r + tx - hr) / 2 + 0.1, -0.37, zcl), normal_rot=(math.pi / 2, 0, 0), r=0.11, mat="iron_edge")
    # J-arm: from under the clamp down and round into the post
    arm = [(r + 0.35, 0, zcl - 0.2), (r + 0.42, 0, zcl - 0.9), (r + 0.38, 0, zcl - 1.55),
           (r + 0.12, 0, zcl - 1.95), (r * 0.8, 0, zcl - 2.05)]
    v += a.tube_loop(arm, 0.17, mat="iron", rseg=6, closed=False)
    # handle with a wooden collar at the clamp, flared iron bowl, coals and flame
    zb, zc, ch = 3.3, 6.4, 0.95
    v += a.cyl(hr * 0.95, hr, zc - zb + 0.1, 8, loc=(tx, 0, zb), mat="wood_dark")
    v += a.cyl(hr + 0.14, hr + 0.14, 0.75, 8, loc=(tx, 0, zcl - 0.38), mat="wood")
    v += a.cyl(hr * 1.1, cup_r * 0.86, ch * 0.45, 10, loc=(tx, 0, zc), mat="iron_dark")  # deep bowl
    v += a.cyl(cup_r * 0.86, cup_r, ch * 0.55, 10, loc=(tx, 0, zc + ch * 0.45), mat="iron_dark")
    v += a.cyl(cup_r * 0.86, cup_r * 0.93, 0.22, 10, loc=(tx, 0, zc + 0.32), mat="iron")
    v += a.cyl(cup_r, cup_r * 1.03, 0.16, 10, loc=(tx, 0, zc + ch - 0.08), mat="iron")
    v += a.cyl(cup_r * 0.9, cup_r * 0.82, 0.16, 9, loc=(tx, 0, zc + ch - 0.24), mat="charcoal")
    v += torch_flame(a, (tx, 0, zc + ch - 0.12), 2.3, cup_r * 0.82)
    swing = -0.3  # swing the torch a little toward the front
    a.transform(v, rot=(0, 0, swing))
    # VFX socket just above the cup, in local studs after finish()'s re-origin
    xs = [p.co.x for p in a.bm.verts]
    ys = [p.co.y for p in a.bm.verts]
    zs = [p.co.z for p in a.bm.verts]
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    fire = Vector((tx * math.cos(swing), tx * math.sin(swing), zc + ch + 0.1)) - off
    obj = done(a)
    vfx.add(obj, "torch_fire", tuple(fire))
    return obj


def palisade_banner_panel():
    a = fk.Asset("PalisadeBannerPanel", "Fences")
    xs, rs = row_positions([0.9, 0.8, 0.8, 0.92], 8.5)
    hs = [9.2, 8.3, 8.6, 9.5]
    palisade(a, [(x, 0) for x in xs], rs, hs, [1.7, 6.15], tipk=0.2)
    rmax = max(rs)
    # dowel hanging pole in front, lashed at each end
    yr = -(rmax + 0.42)
    zr = 6.35
    pr = 0.21
    a.beam((-2.25, yr, zr), (2.25, yr, zr), pr, sides=7)
    for x in (-2.02, 2.02):
        pts = [(x, yr + (pr + 0.05) * math.cos(t), zr + (pr + 0.05) * math.sin(t))
               for t in [2 * math.pi * i / 8 for i in range(8)]]
        cord(a, pts, 0.07, axis=("x", yr, zr))
        pts = [(x + 0.16, yr + (pr + 0.05) * math.cos(t), zr + (pr + 0.05) * math.sin(t))
               for t in [2 * math.pi * i / 8 for i in range(8)]]
        cord(a, pts, 0.07, axis=("x", yr, zr))
    # red cloth with loop tabs over the pole and a ragged V hem
    top = zr - 0.02
    hem = [(1.5, 1.35), (1.3, 1.0), (1.12, 1.25), (0.88, 0.7), (0.62, 0.95), (0.34, 0.45),
           (0.0, 0.0), (-0.3, 0.42), (-0.6, 0.9), (-0.86, 0.62), (-1.12, 1.2), (-1.32, 0.95),
           (-1.5, 1.3)]
    hem = [(x * 1.22, z + 0.3) for x, z in hem]
    outline = [(-1.83, top)] + list(reversed(hem)) + [(1.83, top)]
    cd = 0.1
    yc = yr + pr + 0.14  # the cloth hangs behind the pole...
    a.poly_prism(outline, cd, loc=(0, yc, 0), rot=(math.pi / 2, 0, 0), mat="cloth_red")
    for x in (-1.5, 1.5):  # ...from two loops wrapped over its front
        a.box((0.5, pr * 2 + 0.3, 0.1), loc=(x, yr + 0.05, zr + pr + 0.04), mat="cloth_red", bevel=0.03)
        a.box((0.5, 0.08, 0.55), loc=(x, yr - pr - 0.05, zr - 0.08), mat="cloth_red", bevel=0.02)
    # cream sigil: curling horns over a stem with down-turned spurs and a pointed foot
    ys = yc - cd + 0.005
    rot = (math.pi / 2, 0, 0)
    cz = 4.55
    SG = 1.15
    horn = [(x * SG, y * SG) for x, y in
            ((0.0, 0.0), (0.3, 0.02), (0.56, 0.12), (0.76, 0.33), (0.84, 0.6), (0.76, 0.88))]
    wid = [w * SG for w in (0.22, 0.22, 0.2, 0.16, 0.1, 0.0)]

    def side(pts, ws, s):
        up, lo = [], []
        for i, ((x, y), w) in enumerate(zip(pts, ws)):
            j0, j1 = max(i - 1, 0), min(i + 1, len(pts) - 1)
            dx, dy = pts[j1][0] - pts[j0][0], pts[j1][1] - pts[j0][1]
            L = math.hypot(dx, dy)
            nx, ny = -dy / L, dx / L
            up.append((s * (x + nx * w / 2), cz + y + ny * w / 2))
            lo.append((s * (x - nx * w / 2), cz + y - ny * w / 2))
        return up, lo
    ru, rl = side(horn, wid, 1)
    lu, ll = side(horn, wid, -1)
    shape = rl + list(reversed(ru[1:])) + lu[1:] + list(reversed(ll))
    # keep it CCW (seen from the front, -Y)
    area = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(shape, shape[1:] + shape[:1]))
    if area < 0:
        shape.reverse()
    a.poly_prism(shape, 0.05, loc=(0, ys, 0), rot=rot, mat="cloth_cream")
    stem = [(x * SG, cz + z * SG) for x, z in
            ((0.17, 0.05), (-0.17, 0.05), (-0.13, -0.7), (-0.2, -1.05), (0, -1.75), (0.2, -1.05), (0.13, -0.7))]
    a.poly_prism(list(reversed(stem)), 0.05, loc=(0, ys, 0), rot=rot, mat="cloth_cream")
    spur = [(0.05, 0.0), (0.25, -0.03), (0.42, -0.14), (0.47, -0.36)]
    swid = [w * SG for w in (0.13, 0.12, 0.08, 0.0)]
    for s in (-1, 1):
        u, l = side([(x * SG, (y - 0.62) * SG) for x, y in spur], swid, s)
        sh = u + list(reversed(l))
        ar = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(sh, sh[1:] + sh[:1]))
        if ar < 0:
            sh.reverse()
        a.poly_prism(sh, 0.05, loc=(0, ys, 0), rot=rot, mat="cloth_cream")
    return done(a, 8.5)


# ---------------------------------------------------------------------------
# Lobby perimeter wall (art/reference/lobby_map.png): thick main posts on
# stone footings at every join, split-log sections between them, and lower
# plank and log-rail fences by the entrances. Sections tile at 10 studs; a main
# post stands centred on each join and hides the section ends.
# ---------------------------------------------------------------------------

MP_R, MP_H = 1.3, 12.0  # main post: ~2.6 across, ~12 tall
MP_TH = 0.2  # main post rope: thick, but tight wraps (the master's bands are not stacked tyres)
SEC_W = 10.0


def stone_footing(a, r, h=3.0):
    """Chunky chiselled stone plinth hugging a post's base: two stacked, slightly
    offset blocks, a split face on the front and a chock at the foot."""
    w = 2 * r + 1.0
    v = a.stone_block((w, w * 0.94, h * 0.55), loc=(0, 0, h * 0.275), rot=(0, 0, a.rng.uniform(-0.08, 0.08)),
                      bevel=0.22, mat="stone")
    w2 = 2 * r + 0.75
    v += a.stone_block((w2, w2 * 0.94, h * 0.47), loc=(0.08, -0.04, h * 0.55 + h * 0.225),
                       rot=(0, 0, a.rng.uniform(0.05, 0.1)), bevel=0.2, mat="stone")
    # a chipped front block on the lower course breaks the box silhouette
    v += a.stone_block((w * 0.48, 0.5, h * 0.5), loc=(-w * 0.2, -w * 0.47 - 0.05, h * 0.25),
                       rot=(0, 0, 0.06), bevel=0.15, mat="stone")
    # the master paints the blocks' upper faces pale, like chiselled tops catching the sun
    faces = {f for vv in v for f in vv.link_faces}
    for f in faces:
        f.normal_update()
    paint(a, [f for f in faces if f.normal.z > 0.6], "stone_light", 1.0)
    a.rock((1.2, 1.0, 0.8), loc=(w / 2 + 0.15, -w / 2 + 0.2, 0), subdiv=1, facets=10, mat="stone_dark")


def carve_rune(a, r, zc, kind="chevron", s=1.0):
    """Dark carved glyph on the post's front face (-Y)."""
    rot = (math.pi / 2, 0, 0)
    y = -(r * 0.9)
    if kind == "chevron":
        lines = [[(-0.5, 0.55), (0, -0.05), (0.5, 0.55)], [(-0.5, 0.0), (0, -0.6), (0.5, 0.0)],
                 [(0, -0.05), (0, 0.75)]]
    else:  # crossed lashing mark with a diamond
        lines = [[(-0.45, 0.6), (0.45, -0.6)], [(0.45, 0.6), (-0.45, -0.6)],
                 [(0, 0.95), (0.3, 0.6), (0, 0.25), (-0.3, 0.6), (0, 0.95)]]
    for ln in lines:
        a.strip([(x * s, zc + z * s) for x, z in ln], 0.15, 0.14, loc=(0, y, 0), rot=rot, mat="wood_dark",
                tint=0.85)


def main_post_body(a, h=MP_H, r=MP_R, bands=((0.84, 3), (0.57, 2)), rune="chevron"):
    """Big round log on a stone footing: flat pale cut top with a dark heart,
    thick rope bands, an optional carved glyph."""
    stone_footing(a, r)
    carved(a, r, h, sides=10, flat=True, chamfer=0.12, top_k=0.87)
    a.cyl(r * 0.2, r * 0.16, 0.06, 7, loc=(a.rng.uniform(-0.1, 0.1), a.rng.uniform(-0.1, 0.1), h - 0.03),
          mat="wood_dark")
    # end-grain splits on the cut top and long cracks down the bark
    ang = a.rng.uniform(0, 2 * math.pi)
    a.strip([(0.45 * r * math.cos(ang), 0.45 * r * math.sin(ang)),
             (0.82 * r * math.cos(ang + 0.08), 0.82 * r * math.sin(ang + 0.08))],
            0.05, 0.05, loc=(0, 0, h - 0.025), mat="wood_dark", tint=1.0)
    for dx, z0, z1 in ((-0.55, 3.4, 6.2), (0.45, 7.4, 9.6)):
        crack(a, dx, r, z0, z1)
    th = MP_TH
    for k, n in bands:
        band(a, 0, 0, r, h * k, n, th=th, gap=th * 1.95)
    if rune:
        carve_rune(a, r, 4.4, rune)


def crack(a, x, r, z0, z1, y0=0.0, w=0.09, cx=0.0):
    """Thin dark split running down the front (-Y) of a log of radius r centred
    at (cx, y0), offset x from its axis."""
    yy = y0 - math.sqrt(max(r * r - x * x, 0.01)) * 0.9
    zm = (z0 + z1) / 2
    x += cx
    a.strip([(x, z0), (x + 0.04, zm), (x - 0.02, z1)], w, 0.16,loc=(0, yy + 0.06, 0), rot=(math.pi / 2, 0, 0),
            mat="wood_dark", tint=0.85)


def sigil(a, cx, cz, ys, SG):
    """Cream horned sigil (horns, stem with spurs, pointed foot) on a banner face."""
    rot = (math.pi / 2, 0, 0)
    horn = [(x * SG, y * SG) for x, y in
            ((0.0, 0.0), (0.3, 0.02), (0.56, 0.12), (0.76, 0.33), (0.84, 0.6), (0.76, 0.88))]
    wid = [w * SG for w in (0.22, 0.22, 0.2, 0.16, 0.1, 0.0)]

    def side(pts, ws, s):
        up, lo = [], []
        for i, ((x, y), w) in enumerate(zip(pts, ws)):
            j0, j1 = max(i - 1, 0), min(i + 1, len(pts) - 1)
            dx, dy = pts[j1][0] - pts[j0][0], pts[j1][1] - pts[j0][1]
            L = math.hypot(dx, dy)
            nx, ny = -dy / L, dx / L
            up.append((cx + s * (x + nx * w / 2), cz + y + ny * w / 2))
            lo.append((cx + s * (x - nx * w / 2), cz + y - ny * w / 2))
        return up, lo

    def ccw(sh):
        ar = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(sh, sh[1:] + sh[:1]))
        return sh if ar > 0 else list(reversed(sh))

    ru, rl = side(horn, wid, 1)
    lu, ll = side(horn, wid, -1)
    a.poly_prism(ccw(rl + list(reversed(ru[1:])) + lu[1:] + list(reversed(ll))), 0.05, loc=(0, ys, 0),
                 rot=rot, mat="cloth_cream")
    stem = [(cx + x * SG, cz + z * SG) for x, z in
            ((0.17, 0.05), (-0.17, 0.05), (-0.13, -0.7), (-0.2, -1.05), (0, -1.75), (0.2, -1.05), (0.13, -0.7))]
    a.poly_prism(ccw(stem), 0.05, loc=(0, ys, 0), rot=rot, mat="cloth_cream")
    spur = [(0.05, 0.0), (0.25, -0.03), (0.42, -0.14), (0.47, -0.36)]
    swid = [w * SG for w in (0.13, 0.12, 0.08, 0.0)]
    for s in (-1, 1):
        u, l = side([(x * SG, (y - 0.62) * SG) for x, y in spur], swid, s)
        a.poly_prism(ccw(u + list(reversed(l))), 0.05, loc=(0, ys, 0), rot=rot, mat="cloth_cream")


def tassel(a, x, y, z, length=2.8):
    """Rope drop ending in a knot and a bunch of white feathers."""
    cl = length * 0.35
    cord(a, [(x, y, z), (x + 0.03, y - 0.02, z - cl * 0.5), (x, y, z - cl)], 0.07, closed=False)
    a.cyl(0.17, 0.2, 0.26, 7, loc=(x, y, z - cl - 0.18), mat="rope")
    fl = length - cl - 0.2
    # a loose horsetail of flat white feathers fanning out under the knot
    for k, (ang, tilt, lk) in enumerate(((0, 0.0, 1.0), (60, 0.2, 0.86), (130, 0.24, 0.8), (200, 0.2, 0.9),
                                         (270, 0.24, 0.84), (330, 0.16, 0.92))):
        q = math.radians(ang)
        a.cyl(0.17, 0.02, fl * lk, 4,loc=(x + 0.05 * math.cos(q), y + 0.05 * math.sin(q), z - cl - 0.2),
              rot=(math.pi + tilt * math.sin(q), -tilt * math.cos(q), 0), mat="bone", tint=1.0 - 0.04 * (k % 3))


def red_banner(a, cx, yr, zr, W=2.4, Hh=3.9, pole=3.4, tassel_side=1):
    """Red sigil banner hung from a dowel pole running across the front."""
    pr = 0.18
    a.beam((cx - pole / 2, yr, zr), (cx + pole / 2, yr, zr + 0.04), pr, sides=7)
    top = zr - 0.02
    hem = [(1.5, 1.35), (1.3, 1.0), (1.12, 1.25), (0.88, 0.7), (0.62, 0.95), (0.34, 0.45),
           (0.0, 0.0), (-0.3, 0.42), (-0.6, 0.9), (-0.86, 0.62), (-1.12, 1.2), (-1.32, 0.95), (-1.5, 1.3)]
    kx, kz = W / 3.0, Hh / 6.5
    bottom = top - Hh
    hem = [(cx + x * kx, bottom + z * kz) for x, z in hem]
    outline = [(cx - W / 2, top)] + list(reversed(hem)) + [(cx + W / 2, top)]
    cd = 0.1
    yc = yr + pr + 0.1  # cloth hangs just behind the pole...
    a.poly_prism(outline, cd, loc=(0, yc, 0), rot=(math.pi / 2, 0, 0), mat="cloth_red")
    for x in (cx - W * 0.36, cx + W * 0.36):  # ...from loops wrapped over its front
        a.box((0.45, pr * 2 + 0.26, 0.1), loc=(x, yr + 0.04, zr + pr + 0.04), mat="cloth_red", bevel=0.03)
        a.box((0.45, 0.08, 0.5), loc=(x, yr - pr - 0.04, zr - 0.08), mat="cloth_red", bevel=0.02)
    sigil(a, cx, top - Hh * 0.33, yc - cd - 0.005, W / 2.6)
    if tassel_side:
        tassel(a, cx + tassel_side * (pole / 2 - 0.2), yr, zr - pr)


def palisade_main_post():
    a = fk.Asset("PalisadeMainPost", "Fences")
    main_post_body(a)
    return done(a)


def palisade_main_post_banner():
    a = fk.Asset("PalisadeMainPostBanner", "Fences")
    r, h = MP_R, MP_H
    zr = 9.1
    main_post_body(a, h, r, bands=((0.9, 2), (zr / h, 2), (0.29, 2)), rune=None)
    red_banner(a, 0, -(r + 0.45), zr, W=2.7, Hh=4.7, pole=3.6)
    return done(a)


def palisade_main_post_torch():
    a = fk.Asset("PalisadeMainPostTorch", "Fences")
    r, h = MP_R, 10.9
    main_post_body(a, h, r, bands=((0.75, 3),), rune="cross")
    x_lash(a, 0, 0, r, h * 0.56, th=MP_TH * 0.9, tilt=0.38, seg=12)
    # wooden torch cup set on the cut top, lashed, with coals and fire
    cr = r * 1.08
    a.cyl(r * 0.92, cr, 0.55, 10, loc=(0, 0, h - 0.1), mat="wood_dark")
    a.cyl(cr, cr * 1.07, 0.75, 10, loc=(0, 0, h + 0.45), mat="wood_dark", cap=False)
    a.cyl(cr * 1.07, cr * 1.1, 0.16, 10, loc=(0, 0, h + 1.2), mat="wood_end", cap=False)
    a.cyl(cr * 0.98, cr * 0.9, 0.12, 9, loc=(0, 0, h + 0.95), mat="charcoal")
    band(a, 0, 0, cr * 1.02, h + 0.55, 2, th=r * ROPE_K * 0.9)
    torch_flame(a, (0, 0, h + 1.02), 2.2, cr * 0.8)  # small static flame; the VFX socket adds live fire
    xs = [p.co.x for p in a.bm.verts]
    ys = [p.co.y for p in a.bm.verts]
    zs = [p.co.z for p in a.bm.verts]
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    fire = Vector((0, 0, h + 1.3)) - off
    obj = done(a)
    vfx.add(obj, "torch_fire", tuple(fire))
    return obj


def lash_loop(a, x, r, yr, rr, z, th, wraps=2, gap=None):
    """Rope wraps round a vertical log (at x, y=0) and the rail in front of it
    (at depth yr, radius rr), as in the master's rail lashings."""
    gap = gap or th * 1.9
    R = r + th * 0.35
    yf = yr - rr - th * 0.35
    for w in range(wraps):
        zz = z + (w - (wraps - 1) / 2) * gap + a.rng.uniform(-0.02, 0.02)
        pts = [(x + R * math.cos(math.radians(t)), R * math.sin(math.radians(t)), zz)
               for t in (0, 45, 90, 135, 180)]
        w_ = R * 0.92
        pts += [(x - w_, yf * 0.55, zz), (x - w_ * 0.8, yf + 0.06, zz), (x - w_ * 0.4, yf, zz),
                (x + w_ * 0.4, yf, zz), (x + w_ * 0.8, yf + 0.06, zz), (x + w_, yf * 0.55, zz)]
        cord(a, pts, th, lump=0.12)


def hewn_board(a, x, w, t, h0, h1, y=0.0, tilt=0.0):
    """Vertical hewn plank: an uneven 6-sided section lofted up in three rings,
    with a pale chamfered top cut flat or on a slant (h0 left, h1 right)."""
    bm, rng = a.bm, a.rng
    sec = [(-0.5, -0.32), (-0.12, -0.5), (0.22, -0.47), (0.5, -0.26), (0.5, 0.5), (-0.5, 0.5)]
    sec = [(sx * w + rng.uniform(-0.03, 0.03), sy * t) for sx, sy in sec]
    N = len(sec)
    c = min(w, t) * 0.3

    def top_z(sx):
        return h0 + (h1 - h0) * (sx / w + 0.5)

    def ring_at(zf, k=1.0, j=0.0):
        out = []
        for sx, sy in sec:
            z = zf(sx) + rng.uniform(-j, j)
            out.append(bm.verts.new((x + sx * k + tilt * z, y + sy * k, z)))
        return out

    R0 = ring_at(lambda sx: 0.0)
    R1 = ring_at(lambda sx: top_z(sx) * rng.uniform(0.4, 0.55), 1.02, 0.1)
    R2 = ring_at(lambda sx: top_z(sx) - c, 1.0, 0.03)
    R3 = ring_at(lambda sx: top_z(sx) + rng.uniform(-0.03, 0.03), 0.78)
    body = []
    for A_, B_ in ((R0, R1), (R1, R2)):
        body += [bm.faces.new((A_[k], A_[(k + 1) % N], B_[(k + 1) % N], B_[k])) for k in range(N)]
    pale = [bm.faces.new((R2[k], R2[(k + 1) % N], R3[(k + 1) % N], R3[k])) for k in range(N)]
    pale.append(bm.faces.new(R3))
    tt = 1.0 + rng.uniform(-0.07, 0.07)
    paint(a, body, "wood", tt)
    paint(a, pale, "wood_end", tt)
    fix_normals(a, body + pale)


def palisade_section():
    a = fk.Asset("PalisadeSection", "Fences")
    radii = [0.74, 0.66, 0.8, 0.7, 0.77, 0.64, 0.75]
    xs, rs = row_positions(radii, SEC_W, overlap=0.1)
    hs = [7.5, 6.8, 8.0, 7.1, 7.75, 6.6, 7.4]
    tops = ["flat", "blunt", "flat", "flat", "blunt", "flat", "blunt"]
    for i, (x, r, h, tp) in enumerate(zip(xs, rs, hs, tops)):
        loc = (x, a.rng.uniform(-0.08, 0.08), 0)
        if tp == "flat":
            v = carved(a, r, h, loc=loc, flat=True, chamfer=0.3)
        else:
            v = carved(a, r, h, loc=loc, tip=r * 1.15, notch=0.3)
        # a slight sideways lean: hand-set logs, not a picket fence
        a.transform(v, loc=(-loc[0], -loc[1], 0))
        a.transform(v, loc=(loc[0], loc[1], 0), rot=(0, a.rng.uniform(-0.03, 0.03), 0))
        if i % 2 == 0:  # long splits down every other log, clear of the rails
            z0 = a.rng.uniform(2.3, 2.8)
            crack(a, a.rng.uniform(-0.25, 0.25) * r, r, z0, z0 + a.rng.uniform(1.6, 2.2), y0=loc[1], w=0.07,
                  cx=x)
    # two rail logs across the front, not quite level, lashed to a few stakes
    rr = 0.42
    yr = -(max(rs) * 0.78 + rr * 0.55)
    rails = ((1.55, 1.75), (5.25, 5.55))
    for z0, z1 in rails:
        a.beam((-SEC_W / 2, yr, z0), (SEC_W / 2, yr, z1), rr, sides=7)
    th = 0.13

    def rail_z(i, x):
        z0, z1 = rails[i]
        return z0 + (z1 - z0) * (x + SEC_W / 2) / SEC_W

    for i, k in ((1, 1), (1, 4), (0, 3)):
        lash_loop(a, xs[k], rs[k], yr, rr, rail_z(i, xs[k]), th, wraps=3 if i else 2, gap=rr * 0.62)
    # iron pegs through the rails into the stakes
    for i, k in ((1, 2), (1, 6), (0, 0), (0, 5)):
        a.rivet((xs[k], yr - rr + 0.02, rail_z(i, xs[k])), normal_rot=(math.pi / 2, 0, 0), r=0.12,
                mat="iron_dark")
    return done(a, SEC_W)


def palisade_section_low():
    a = fk.Asset("PalisadeSectionLow", "Fences")
    ws = [1.2, 1.1, 1.25, 1.15, 1.2, 1.1, 1.25, 1.15]
    gap = 0.07
    ws =[w * (SEC_W - gap * (len(ws) - 1)) / sum(ws) for w in ws]
    tops = [(5.5, 5.4), (5.0, 5.15), (5.8, 5.6), (5.25, 5.25), (5.65, 5.3), (4.95, 5.1), (5.55, 5.75),
            (5.2, 5.05)]
    t = 0.55
    x = -SEC_W / 2
    for w, (h0, h1) in zip(ws, tops):
        hewn_board(a, x + w / 2, w, t, h0, h1, y=a.rng.uniform(-0.05, 0.05), tilt=a.rng.uniform(-0.008, 0.008))
        x += w + gap
    rr = 0.36
    yr = -(t / 2 + rr * 0.75)
    a.beam((-SEC_W / 2, yr, 4.35), (SEC_W / 2, yr, 4.5), rr, sides=7)  # top rail
    a.beam((-SEC_W / 2, yr, 1.15), (SEC_W / 2, yr, 1.25), rr * 0.9, sides=7)
    # rope lashings over the top rail at two boards
    for k in (1, 6):
        xc = -SEC_W / 2 + sum(ws[:k]) + gap * k + ws[k] / 2
        lash_loop(a, xc, ws[k] / 2, yr, rr, 4.43, 0.14, wraps=2)
    return done(a, SEC_W)


def log_rail_fence():
    a = fk.Asset("LogRailFence", "Fences")
    rp = 0.55
    px = SEC_W / 2 - rp - 0.35
    carved(a, rp, 4.1, loc=(-px, 0, 0), flat=True, sides=8)
    carved(a, rp, 3.95, loc=(px, 0, 0), flat=True, sides=8)
    carved(a, rp * 0.85, 3.55, loc=(0.2, 0.02, 0), flat=True, sides=8)
    rr = 0.38
    yr = -(rp * 0.8 + rr * 0.6)
    rails = ((1.2, 1.3), (2.5, 2.42), (3.55, 3.45))
    for z0, z1 in rails:
        a.beam((-SEC_W / 2, yr + a.rng.uniform(-0.04, 0.04), z0), (SEC_W / 2, yr, z1), rr, sides=7)
    for i, (z0, z1) in enumerate(rails):
        for x in (-px, px):
            z = z0 + (z1 - z0) * (x + SEC_W / 2) / SEC_W
            lash_loop(a, x, rp, yr, rr, z, 0.11, wraps=2, gap=rr * 0.75)
    # diagonal brace across the front of the right bay, as on the master's east side
    yb = yr - rr - 0.24
    p1, p2 = Vector((px - 0.5, yb, 0.25)), Vector((-0.6, yb, 3.4))  # foot of the right post up to the top rail
    a.beam(p1, p2, 0.3, sides=6)
    for t in (0.14, 0.88):  # pegs where the brace crosses the rails
        p = p1.lerp(p2, t)
        a.rivet((p.x, yb - 0.27, p.z), normal_rot=(math.pi / 2, 0, 0), r=0.1, mat="iron_dark")
    return done(a, SEC_W)


WALL_BUILDERS = [palisade_main_post, palisade_main_post_banner, palisade_main_post_torch,
                 palisade_section, palisade_section_low, log_rail_fence]


# ---------------------------------------------------------------------------
# Towers and bridge
# ---------------------------------------------------------------------------


def watch_platform_open():
    a = fk.Asset("WatchPlatformOpen", "Towers")
    H, half, r = 8.0, 2.85, 0.74
    posts = corner_posts(a, half, r, H)
    zd = H - 0.13 * H  # post stubs above the deck
    zg = 0.15 * H
    frame_ring(a, half, zd - 0.7, 0.36, overhang=0.55)
    deck(a, -half - 0.6, half + 0.6, -half - 0.75, half + 0.75, zd, 7, along="y", th=0.5)
    frame_ring(a, half, zg + 0.05, 0.32)  # low ground rails on every face
    for (x, y) in posts:
        band(a, x, y, r, zg, 3, th=0.16)
        x_lash(a, x, y, r, zd - 0.55, th=0.15)
    x = half + 0.05  # X brace on the right face
    xbrace(a, (x, -half, zg + 0.4), (x, half, zd - 1.0), (x, half, zg + 0.4), (x, -half, zd - 1.0),
           r=0.36, normal=(1, 0, 0))
    # ladder up the front, left of centre
    ladder(a, (-1.1, -half - 3.0, 0), (-1.1, -half - 0.85, zd + 0.05), across=(1, 0, 0),
           width=1.9, rungs=5, extend=0.45)
    return done(a)


def watchtower_tall():
    a = fk.Asset("WatchtowerTall", "Towers")
    H = 10.8
    half, r = 3.2, 0.8
    posts = corner_posts(a, half, r, H)
    zd = 6.95
    zt, zg = 9.75, 2.2
    frame_ring(a, half, zd - 0.72, 0.38, overhang=0.6)  # deck beams
    deck(a, -half - 0.55, half + 0.55, -half - 0.75, half + 0.6, zd, 7, along="x", th=0.48)
    frame_ring(a, half, zt, 0.42, overhang=0.6)  # top rails
    frame_ring(a, half, zg, 0.34)  # ground rails
    for (x, y) in posts:
        band(a, x, y, r, zt, 3, th=0.17)
        band(a, x, y, r, zd - 0.72, 3, th=0.17)
        band(a, x, y, r, zg, 3, th=0.17)
    for (x, y) in ((0.3, -half), (half, 0.2), (-0.2, half), (-half, -0.3)):  # balusters
        a.beam((x, y, zd - 0.05), (x, y, zt - 0.1), 0.24, sides=6)
    x = half + 0.05
    xbrace(a, (x, -half, zg + 0.35), (x, half, zd - 1.05), (x, half, zg + 0.35), (x, -half, zd - 1.05),
           r=0.3, normal=(1, 0, 0))
    y = half + 0.05
    xbrace(a, (-half, y, zg + 0.35), (half, y, zd - 1.05), (half, y, zg + 0.35), (-half, y, zd - 1.05),
           r=0.3, normal=(0, 1, 0))
    ladder(a, (-1.3, -half - 3.7, 0), (-1.3, -half - 0.95, zd + 0.05), across=(1, 0, 0), width=2.2,
           rungs=7, extend=0.7)
    return done(a)


def prism_y(a, xz, y0, y1, mats, tints):
    """Closed prism: an (x, z) outline extruded from y0 to y1. mats/tints:
    (sides, ends)."""
    bm = a.bm
    f_ = [bm.verts.new((x, y0, z)) for x, z in xz]
    b_ = [bm.verts.new((x, y1, z)) for x, z in xz]
    ends = [bm.faces.new(f_), bm.faces.new(list(reversed(b_)))]
    n = len(xz)
    sides = [bm.faces.new((f_[i], f_[(i + 1) % n], b_[(i + 1) % n], b_[i])) for i in range(n)]
    paint(a, sides, mats[0], tints[0])
    paint(a, ends, mats[1], tints[1])
    fix_normals(a, sides + ends)
    return f_ + b_


def straw(a, base, d, n, length, width, mat, tint):
    """A straw blade: two triangles folded along a raised spine (V section)."""
    bm = a.bm
    base, d, n = Vector(base), Vector(d).normalized(), Vector(n).normalized()
    s = d.cross(n).normalized() * width / 2
    bl, br = bm.verts.new(base - s), bm.verts.new(base + s)
    tip = bm.verts.new(base + d * length)
    sp = bm.verts.new(base + d * length * 0.32 + n * width * 0.3)
    faces = [bm.faces.new((bl, sp, tip)), bm.faces.new((sp, br, tip))]
    for f in faces:
        if f.normal.dot(n) < 0:
            f.normal_flip()
    paint(a, faces, mat, tint)


def thatch_roof(a, hx, hy, eave_z, ridge_z, courses=6, pitch_y=0.33):
    """Shaggy gable thatch with the ridge along Y: a solid straw core, courses of
    loose blades laid down each slope with their tips lifting out, a long eave
    fringe, and fringes hanging off both gable rakes."""
    rng = a.rng
    run, drop = hx, ridge_z - eave_z
    L = math.hypot(run, drop)
    al = math.atan2(drop, run)
    ct = 0.85  # thick straw: the gable ends show it as a shaggy edge
    prism_y(a, [(-hx, eave_z - 0.3), (-hx, eave_z), (0, ridge_z), (hx, eave_z), (hx, eave_z - 0.3),
                (0, ridge_z - ct - 0.35)], -hy + 0.1, hy - 0.1, ("thatch_dark", "thatch"), (0.95, 0.9))
    for s in (-1, 1):
        d = Vector((s * math.cos(al), 0, -math.sin(al)))  # down-slope
        nrm = Vector((s * math.sin(al), 0, math.cos(al)))
        for k in range(courses):
            v0 = L * k / courses - 0.25
            span = L / courses
            last = k == courses - 1
            nb = int(2 * (hy + 0.3) / pitch_y)
            for layer in (0, 1):
                for i in range(nb):
                    u = -hy - 0.3 + (i + 0.5 + 0.5 * layer) * (2 * (hy + 0.3) / nb) + rng.uniform(-0.08, 0.08)
                    off = 0.08 + 0.05 * layer + 0.04 * (courses - k)
                    p = Vector((0, u, ridge_z)) + d * (v0 + rng.uniform(-0.15, 0.15)) + nrm * off
                    yaw = rng.uniform(-0.3, 0.3)
                    lift = rng.uniform(0.05, 0.32) + (0.1 if layer else 0)
                    dd = (d * math.cos(yaw) + Vector((0, 1, 0)) * math.sin(yaw) + nrm * lift)
                    if last:
                        dd += Vector((0, 0, -0.3))
                    ln = span * rng.uniform(1.4, 1.9) * (0.75 if last else 1.0) + (0.25 if last else 0)
                    straw(a, p, dd, nrm, ln, rng.uniform(0.38, 0.56),
                          "thatch" if rng.random() > 0.22 else "thatch_dark", rng.uniform(0.9, 1.12))
        # under-eave fringe hanging down
        nb = int(2 * hy / 0.3)
        for i in range(nb):
            u = -hy + (i + 0.5) * (2 * hy / nb) + rng.uniform(-0.08, 0.08)
            q = Vector((0, u, ridge_z)) + d * (L - 0.35) + nrm * 0.02
            straw(a, q, d + Vector((0, rng.uniform(-0.3, 0.3), -0.9)), nrm, rng.uniform(0.8, 1.3),
                  0.28, "thatch_dark" if rng.random() > 0.4 else "thatch", rng.uniform(0.85, 1.02))
    # gable ends: straw poking out past the rakes and hanging over the thick
    # straw edge, so each end reads as a shaggy bundle rather than a flat wall
    for sy in (-1, 1):
        for s in (-1, 1):
            nb = int(L / 0.22)
            for i in range(nb):
                t = (i + 0.5) / nb + rng.uniform(-0.02, 0.02)
                x = s * hx * t
                z = ridge_z + 0.15 - drop * t
                straw(a, (x, sy * (hy + 0.1), z), (s * 0.4 + rng.uniform(-0.3, 0.3), sy * 0.7, -1.0),
                      (0, sy, 0.3), rng.uniform(0.7, 1.25), rng.uniform(0.26, 0.36),
                      "thatch" if rng.random() > 0.3 else "thatch_dark", rng.uniform(0.9, 1.1))
                if i % 2 == 0:
                    zz = z - ct * rng.uniform(0.3, 0.7)
                    straw(a, (x * 0.97, sy * (hy - 0.05), zz),
                          (s * rng.uniform(0.0, 0.5), sy * 0.25, -1.0), (0, sy, 0.1),
                          rng.uniform(0.6, 1.0), 0.3, "thatch_dark", rng.uniform(0.85, 1.0))


def watchtower_roofed():
    a = fk.Asset("WatchtowerRoofed", "Towers")
    half, r = 2.85, 0.84
    hp = 11.5  # post tops, under the roof
    posts = corner_posts(a, half, r, hp)
    zd, zrail, zg = 8.1, 10.0, 1.8
    frame_ring(a, half, zd - 0.72, 0.38, overhang=0.6)
    deck(a, -half - 0.6, half + 0.6, -half - 0.75, half + 0.6, zd, 6, along="x", th=0.48)
    frame_ring(a, half, zrail, 0.32, overhang=0.55)
    frame_ring(a, half, hp - 0.5, 0.36, overhang=0.75)  # roof plate
    frame_ring(a, half, zg, 0.34)
    for (x, y) in posts:
        band(a, x, y, r, zg, 2, th=0.18)
        band(a, x, y, r, zd - 0.72, 3, th=0.17)
        x_lash(a, x, y, r, zrail, th=0.15)
    x = half + 0.05
    xbrace(a, (x, -half, zg + 0.35), (x, half, zd - 1.05), (x, half, zg + 0.35), (x, -half, zd - 1.05),
           r=0.3, normal=(1, 0, 0))
    y = half + 0.05
    xbrace(a, (-half, y, zg + 0.35), (half, y, zd - 1.05), (half, y, zg + 0.35), (-half, y, zd - 1.05),
           r=0.3, normal=(0, 1, 0))
    # roof: shaggy gable thatch, ridge running front to back, ridge log with lashings
    eave = hp + 0.15
    ridge_z = eave + 2.9
    thatch_roof(a, 4.75, 4.6, eave, ridge_z)
    for sy in (-1, 1):  # gable rafters and king post under each end
        for sx in (-1, 1):
            a.beam((sx * (half + 0.4), sy * half, hp - 0.3), (0, sy * half, ridge_z - 0.6), 0.22, sides=6)
        a.beam((0, sy * half, hp - 0.3), (0, sy * half, ridge_z - 0.5), 0.2, sides=6)
    a.beam((0, -5.0, ridge_z + 0.32), (0, 5.0, ridge_z + 0.32), 0.44, sides=8)
    for y in (-4.0, 4.0):
        for k in (-1, 1):
            pts = [(0.5 * math.cos(t), y + k * 0.13, ridge_z + 0.32 + 0.5 * math.sin(t))
                   for t in [2 * math.pi * i / 8 for i in range(8)]]
            cord(a, pts, 0.1, axis=("y", 0, ridge_z + 0.32))
    ladder(a, (-1.2, -half - 3.4, 0), (-1.2, -half - 0.95, zd + 0.05), across=(1, 0, 0), width=2.2,
           rungs=6, extend=0.7)
    return done(a)


def footbridge_small():
    a = fk.Asset("FootbridgeSmall", "Towers")
    L, H = 14.0, 4.4
    hw, pr = 2.85, 0.58
    zd = 2.6
    pt = 0.45
    ys = 1.7  # stringers inside the post lines
    # stringer logs (round ends showing under the deck ends) on low sills
    for y in (-ys, ys):
        a.beam((-6.95, y, zd - pt - 0.42), (6.95, y, zd - pt - 0.42), 0.44, sides=8)
    for x in (-6.0, 6.0):
        a.beam((x, -2.95, 0.45), (x, 2.95, 0.45), 0.42, sides=7)
    # transverse deck planks with slightly ragged ends
    n = 13
    gap = 0.15
    w = (L - 1.6 - gap * (n - 1)) / n
    for i in range(n):
        x = -L / 2 + 0.8 + w / 2 + i * (w + gap)
        a.plank((w, 5.25 + a.rng.uniform(-0.15, 0.15), pt),
                loc=(x, a.rng.uniform(-0.08, 0.08), zd - pt / 2 + a.rng.uniform(-0.03, 0.03)),
                rot=(0, a.rng.uniform(-0.015, 0.015), a.rng.uniform(-0.02, 0.02)), mat="wood_light")
    for sx in (-1, 1):  # lower landing planks at each end
        a.plank((0.85, 5.0, pt), loc=(sx * (L / 2 - 0.42), a.rng.uniform(-0.1, 0.1), zd - pt / 2 - 0.3),
                rot=(0, 0, a.rng.uniform(-0.03, 0.03)))
    # posts, rails, lashings and knee braces from the posts up under the deck
    xs = (-5.6, 0.0, 5.6)
    for y in (-hw, hw):
        for x in xs:
            carved(a, pr, H + a.rng.uniform(-0.1, 0.05), loc=(x, y, 0), flat=True)
            band(a, x, y, pr, 3.6, 3, th=0.13)
            band(a, x, y, pr, zd - 0.15, 2, th=0.13)
            if x != 0.0:
                sx = -1 if x < 0 else 1
                a.beam((x - sx * 0.4, y * 0.93, 0.45), (x - sx * 1.8, ys * (1 if y > 0 else -1), zd - pt - 0.15),
                       0.22, sides=6)
        a.beam((-6.2, y, 3.6), (6.2, y, 3.6), 0.38, sides=7)
    return done(a)


# ---------------------------------------------------------------------------
# Sheet render with per-asset camera
# ---------------------------------------------------------------------------

LENS = 80  # long lens: the reference sheet is drawn with little perspective


def render_cell(obj, path, res, az, el, fill=0.86, samples=32):
    """Like fk.render_asset, but fits the projected mesh to the frame
    (fk.frame fits a sphere with the horizontal FOV, which clips tall assets)."""
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
    cam.data.lens = LENS
    cam.data.clip_end = 2000
    fk.frame(obj, az, el)
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    centre = sum(corners, Vector()) / 8
    direction = (cam.location - centre).normalized()
    rotm = cam.rotation_euler.to_matrix().to_4x4()
    ht = math.tan(cam.data.angle / 2)
    vt = ht * res[1] / res[0]
    mw = np.array(obj.matrix_world)
    co = np.empty(len(obj.data.vertices) * 3)
    obj.data.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]
    co = np.hstack([co, np.ones((len(co), 1))])

    def project(dist):
        inv = np.array((Matrix.Translation(centre + direction * dist) @ rotm).inverted())
        q = co @ inv.T
        us, vs = q[:, 0] / -q[:, 2], q[:, 1] / -q[:, 2]
        return us.min(), us.max(), vs.min(), vs.max()

    lo, hi = 1.0, 1000.0
    for _ in range(50):
        mid = (lo + hi) / 2
        u0, u1, v0, v1 = project(mid)
        if (u1 - u0) / 2 <= ht * fill and (v1 - v0) / 2 <= vt * fill:
            hi = mid
        else:
            lo = mid
    u0, u1, v0, v1 = project(hi)
    cam.location = centre + direction * hi
    cam.data.shift_x = (u0 + u1) / 2 / (2 * ht)
    cam.data.shift_y = (v0 + v1) / 2 / (2 * ht)
    scene.render.filepath = path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    cam.data.shift_x = cam.data.shift_y = 0.0
    for o in hidden:
        o.hide_render = False
    return path


def render_sheet(objs, path, views, cols=4, cell=(384, 288)):
    base, _ = os.path.splitext(path)
    cell_paths = []
    for i, o in enumerate(objs):
        az, el = views.get(o.name, (fk.DEFAULT_AZIMUTH, fk.DEFAULT_ELEVATION))
        p = f"{base}_cells/{i + 1:02d}_{o.name}.png"
        render_cell(o, p, cell, az, el)
        cell_paths.append(p)
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


# (azimuth, elevation) per asset, matched to the reference sheet's views. The
# sheet draws the towers from the front right (ladder on the front face, X brace
# on the right face) and the fences and bridge from the front left.
VIEWS = {
    "PalisadePanelA": (-14, 17),
    "PalisadePanelB": (-14, 17),
    "CornerPalisade": (-45, 18),
    "CurvedPalisade": (-12, 20),
    "PalisadeGate": (-16, 17),
    "PalisadeEndPost": (-14, 17),
    "PalisadeTorchPost": (-14, 17),
    "PalisadeBannerPanel": (-14, 17),
    "WatchPlatformOpen": (40, 25),
    "WatchtowerTall": (32, 24),
    "WatchtowerRoofed": (32, 26),
    "FootbridgeSmall": (-40, 31),
    "PalisadeMainPost": (-14, 22),
    "PalisadeMainPostBanner": (-14, 22),
    "PalisadeMainPostTorch": (-14, 22),
    "PalisadeSection": (-14, 24),
    "PalisadeSectionLow": (-14, 24),
    "LogRailFence": (-18, 26),
}

BUILDERS = [palisade_panel_a, palisade_panel_b, corner_palisade, curved_palisade,
            palisade_gate, palisade_end_post, palisade_torch_post, palisade_banner_panel,
            watch_platform_open, watchtower_tall, watchtower_roofed, footbridge_small] + WALL_BUILDERS


def main():
    fk.reset_file()
    objs = [b() for b in BUILDERS]
    for o in objs:
        assert tuple(o.rotation_euler) == (0.0, 0.0, 0.0)
        print(f"FB02 {o.name}: tris={o['tris']} studs={o['studs']}")
    fk.layout_row(objs)
    fk.save(os.path.join(ROOT, "assets", "02_fences_towers.blend"))
    render_sheet(objs, os.path.join(ROOT, "renders", "02_fences_towers.png"), VIEWS, cols=4)
    print("FB02 done")


if __name__ == "__main__":
    main()
