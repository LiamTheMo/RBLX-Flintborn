"""W01 row 2: ROCK SPIRE, "angular stone spire with broad foot".

A pointed, chiselled obelisk (convex hull of jittered rings that taper nearly
linearly to a narrow slanted chisel tip), two shoulder wedges leaning on it
whose tops slope away from the spire, a fused, jagged collar ring of foot rocks
round its base and a broad spread of foot boulders, so the whole reads as a
broad triangle. Moss is a thin decal clipped onto 1-4 rock facets; rounded
leafy clumps (6-tri leaves on a domed core) bank against the foot, with a few
rubble stones and white flowers.

Assets: RockSpire (hero), RockSpireMain + RockSpireFootCollar (parts),
RockSpireShort / RockSpireTall / RockSpireLeaning (variants). No VFX: the
reference shows none.

One colour per material (the sheet's W01 palette): every rock facet is
w01_rock with a small random Tint (+/-6%), moss is w01_moss, every leafy clump
is w01_leaf. The light tops and blue-grey shadow sides on the reference are
lighting: the facets and the studio / Roblox light shade them.
"""

import math
import random

import bmesh
from mathutils import Vector

SUBJECT = "RockSpire"
ROW = 2
# The W01 sheet palette, copied verbatim (shared by all four W01 modules).
PALETTE = {
    "w01_rock": ("#B29F98", 0.9, 0, 0),  # THE ONLY stone colour on the whole sheet: warm mauve-beige granite of every boulder, spire, cluster rock, slab and pebble (lit mid-tone; median of all rock pixels across the 4 hero cells is #B29F96-#B5A097). The swatches' blue-grey (#8E8E9E) and pale beige (#CAB2A8) are its shadow and lit sides, NOT materials: drop w01_boulder_beige, w01_boulder_blue, w01_rock_light, w01_rock_cool, w01_rock_warm, kit_rock(_light/_dark) and stone. Same value in every module that declares it (this replaces the old #8E7C78). Variety only via a small random Tint (<=1.25x spread), never by face direction.
    "w01_moss": ("#ADBB14", 0.9, 0, 0),  # Lime-yellow moss: moss caps, moss pads, streaks/smudges and thin decals on rock facets (median moss pixel #ADBB08; swatches 3 #8DA418 and 4 #D7CD29 are its shadow and lit sides). Replaces moss, moss_light, moss_dark.
    "w01_leaf": ("#7AAB1E", 0.8, 0, 0),  # Clover / round-leaf ground clumps banked at rock feet and in crevices: a greener, slightly deeper green than the moss so the two read apart. Replaces leaf, leaf_light and grass_light on this sheet (one key for all leafy clumps).
}
# Also used, from the shared flintkit PALETTE (existing keys, not redeclared: the
# runner only accepts w01_-prefixed extra keys): flower_white #F5F2EA (daisy
# petals), flower_yellow #F2C230 (daisy centres).

ROCK, MOSS, LEAF = "w01_rock", "w01_moss", "w01_leaf"
ROCK_TINT = 0.06  # small random per-facet Tint spread, never tied to face direction
Z = Vector((0, 0, 1))
TAU = 2 * math.pi


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def paint(a, faces, mat, tint=1.0, var=0.04):
    mi = a._mi(mat)
    for f in faces:
        f.material_index = mi
        f.smooth = False
        t = tint * (1.0 + a.rng.uniform(-var, var))
        for lp in f.loops:
            lp[a.tint_layer] = (t, t, t, 1.0)


class Piece:
    """A convex chunk in the asset: its faces and its bounding planes (for the
    hidden-face cull and for draping moss / placing clumps on it)."""

    def __init__(self, faces, kind):
        self.faces = faces
        self.kind = kind
        self.planes = [(f.normal.copy(), f.calc_center_median()) for f in faces]

    def contains(self, p, eps=0.02):
        return all(n.dot(p - c) < -eps for n, c in self.planes)

    def ray(self, o, d):
        """First hit of the ray o + t*d on this convex piece: (t, normal) or None."""
        t0, t1, n0 = -1e9, 1e9, None
        for n, c in self.planes:
            nd = n.dot(d)
            dist = n.dot(c - o)
            if abs(nd) < 1e-9:
                if dist < 0:
                    return None
                continue
            t = dist / nd
            if nd < 0:
                if t > t0:
                    t0, n0 = t, n
            elif t < t1:
                t1 = t
        if n0 is None or t0 > t1 or t0 < 0:
            return None
        return t0, n0


def hull(a, pts, merge=4.0):
    """Convex hull of pts into the asset; returns its faces (normals outward)."""
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    res = bmesh.ops.convex_hull(bm, input=vs, use_existing_faces=False)
    junk = list({g for g in res["geom_interior"] + res["geom_unused"]
                 if isinstance(g, bmesh.types.BMVert) and g.is_valid})
    if junk:
        bmesh.ops.delete(bm, geom=junk, context="VERTS")
    vs = [v for v in vs if v.is_valid]
    faces = list({f for v in vs for f in v.link_faces})
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    if merge:
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(merge), verts=vs,
                                 edges=list({e for v in vs for e in v.link_edges}))
        vs = [v for v in vs if v.is_valid]
        faces = list({f for v in vs for f in v.link_faces})
    bm.normal_update()
    return faces


def rock_paint(a, faces, rng):
    """One flat rock colour (w01_rock) with a small seeded random Tint per
    facet: never by height or face direction, the light shades the facets."""
    for f in sorted(faces, key=lambda f: tuple(f.calc_center_median())):
        paint(a, [f], ROCK, rng.uniform(1.0 - ROCK_TINT, 1.0 + ROCK_TINT), 0.0)


def ring_pts(rng, cx, cy, z, rx, ry, n, jit=0.1, rot=None, ajit=0.22):
    rot = rng.uniform(0, TAU) if rot is None else rot
    out = []
    for k in range(n):
        ang = rot + TAU * k / n + rng.uniform(-ajit, ajit)
        rr = rng.uniform(1.0 - jit, 1.0 + jit * 0.6)
        out.append(Vector((cx + math.cos(ang) * rx * rr, cy + math.sin(ang) * ry * rr, z)))
    return out


# radius fraction by height fraction: a near-linear obelisk taper
TAPER = [(0.0, 1.0), (0.24, 0.81), (0.48, 0.61), (0.7, 0.41), (0.87, 0.25)]


def spire_pts(rng, c, r, h, lean=(0.0, 0.0), rings=TAPER, n=7, tip=0.45, tip_n=4, drop=0.9,
              slant=(-0.8, -0.55), zjit=0.02, jit=0.1):
    """Tapered obelisk: jittered rings narrowing nearly linearly, then a narrow
    slanted chisel tip (tip = its half width) whose low side looks along
    `slant`: tip_n=4 points on one plane, so the chisel is one clear face.
    Rings alternate by half a step, so the flanks break into diamond facets
    instead of long vertical slivers. lean shifts the centre per stud of height."""
    pts = []
    rot0 = rng.uniform(0, TAU)
    for i, (fz, fr) in enumerate(rings):
        z = fz * h
        cx, cy = c[0] + lean[0] * z, c[1] + lean[1] * z
        rot = rot0 + (i % 2) * math.pi / n
        for p in ring_pts(rng, cx, cy, z, r[0] * fr, r[1] * fr, n, jit=jit, rot=rot, ajit=0.12):
            if fz:
                p.z = max(0.0, p.z + rng.uniform(-zjit, zjit) * h)
            pts.append(p)
    tx, ty = c[0] + lean[0] * h, c[1] + lean[1] * h
    sd = Vector((slant[0], slant[1], 0.0)).normalized()
    # corners at +-45 / +-135 deg from the slant: two high corners make a short
    # flat crest at the back, two low ones the foot of the sloping chisel face
    rot = math.atan2(sd.y, sd.x) + math.pi / 4
    span = math.cos(math.pi / 4)
    for k in range(tip_n):
        ang = rot + TAU * k / tip_n + rng.uniform(-0.1, 0.1)
        ox, oy = math.cos(ang) * tip * rng.uniform(0.9, 1.05), math.sin(ang) * tip * rng.uniform(0.9, 1.05)
        proj = max(-1.0, min(1.0, (ox * sd.x + oy * sd.y) / (tip * span)))
        pts.append(Vector((tx + ox, ty + oy, h - drop * 0.5 * (1 + proj))))
    return pts


def shoulder_pts(rng, c, r, h, out, tilt=25.0, n=6, lean_in=0.05,
                 rings=((0.0, 1.0), (0.5, 0.84), (1.0, 0.64))):
    """Shoulder wedge leaning on the spire: a tapering block whose top is one
    plane sloping down away from the spire (out) by `tilt` degrees."""
    o = Vector((out[0], out[1], 0.0)).normalized()
    lean = (-o.x * lean_in, -o.y * lean_in)
    pts = []
    for fz, fr in rings:
        z = fz * h
        cx, cy = c[0] + lean[0] * z, c[1] + lean[1] * z
        for p in ring_pts(rng, cx, cy, z, r[0] * fr, r[1] * fr, n, jit=0.12):
            if 0 < fz < 1:
                p.z += rng.uniform(-0.04, 0.04) * h
            pts.append(p)
    rt = max(r) * rings[-1][1]
    k = math.tan(math.radians(tilt))
    tx, ty = c[0] + lean[0] * h, c[1] + lean[1] * h
    for p in pts:
        d = (p.x - tx) * o.x + (p.y - ty) * o.y
        lim = h - k * (d + rt)
        if p.z > lim:
            p.z = max(lim, 0.3 * h)
    return pts


def boulder_pts(rng, c, size, n=14, p=3.0, flat=0.12, yaw=None):
    """Chunky faceted boulder: superellipsoid points over the upper half plus a
    ground ring, clipped flat a little below the crown."""
    sx, sy, sz = size
    rx, ry = sx / 2, sy / 2
    yaw = rng.uniform(0, TAU) if yaw is None else yaw
    cs, sn = math.cos(yaw), math.sin(yaw)
    pts = []
    ga = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        z = 0.12 + 0.88 * (i + 0.5) / n
        rr = math.sqrt(max(0.0, 1 - z * z))
        th = ga * i + rng.uniform(-0.35, 0.35)
        d = Vector((rr * math.cos(th), rr * math.sin(th), z))
        s = (abs(d.x) ** p + abs(d.y) ** p + abs(d.z) ** p) ** (-1 / p)
        d *= s * rng.uniform(0.86, 1.04)
        pts.append(Vector((c[0] + d.x * rx * cs - d.y * ry * sn, c[1] + d.x * rx * sn + d.y * ry * cs,
                           min(d.z * sz, sz * (1 - flat)))))
    for k in range(6):
        ang = TAU * k / 6 + rng.uniform(-0.3, 0.3)
        x, y = math.cos(ang) * rx * 0.92, math.sin(ang) * ry * 0.92
        pts.append(Vector((c[0] + x * cs - y * sn, c[1] + x * sn + y * cs, 0.0)))
    return pts


def block_pts(rng, c, yaw, w, d, h, point):
    """Collar rock: a wide, blocky wedge (w along the ring, d radial) with a
    chunky top; point > 0 pulls the top into a jagged upright tooth."""
    cs, sn = math.cos(yaw), math.sin(yaw)
    loc = []
    for k in range(8):  # boxy footprint
        ang = TAU * k / 8 + math.pi / 8 + rng.uniform(-0.2, 0.2)
        ca, sa = math.cos(ang), math.sin(ang)
        s = (abs(ca) ** 4 + abs(sa) ** 4) ** -0.25
        loc.append((ca * s * w / 2 * rng.uniform(0.85, 1.0), sa * s * d / 2 * rng.uniform(0.85, 1.0), 0.0))
    for k in range(7):  # slight bulge low down: extra chunky facets on the walls
        ang = TAU * k / 7 + rng.uniform(-0.25, 0.25)
        ca, sa = math.cos(ang), math.sin(ang)
        s = (abs(ca) ** 3.5 + abs(sa) ** 3.5) ** (-1 / 3.5)
        loc.append((ca * s * w / 2 * rng.uniform(0.95, 1.05), sa * s * d / 2 * rng.uniform(0.95, 1.05),
                    h * rng.uniform(0.22, 0.34)))
    for k in range(6):  # shoulder ring
        ang = TAU * k / 6 + rng.uniform(-0.3, 0.3)
        ca, sa = math.cos(ang), math.sin(ang)
        s = (abs(ca) ** 3 + abs(sa) ** 3) ** (-1 / 3)
        loc.append((ca * s * w / 2 * 0.86, sa * s * d / 2 * 0.82, h * rng.uniform(0.5, 0.68)))
    if point:
        # broken, slanted top: high at one end of the rock, stepping down to
        # the other, so the rock stays a chunky block with a jagged crest
        s = 1 if rng.random() < 0.5 else -1
        loc.append((s * w * 0.28, rng.uniform(-0.12, 0.12) * d, h))
        loc.append((s * w * 0.3, rng.uniform(0.15, 0.25) * d * (-1) ** rng.randrange(2), h * 0.93))
        loc.append((rng.uniform(-0.05, 0.05) * w, rng.uniform(-0.15, 0.15) * d, h * (1 - 0.18 * point)))
        loc.append((-s * w * 0.3, rng.uniform(-0.15, 0.15) * d, h * (1 - 0.32 * point)))
    else:
        for k in range(3):
            ang = TAU * k / 3 + rng.uniform(-0.4, 0.4)
            loc.append((math.cos(ang) * w * 0.26, math.sin(ang) * d * 0.24, h * rng.uniform(0.86, 1.0)))
    return [Vector((c[0] + x * cs - y * sn, c[1] + x * sn + y * cs, z)) for x, y, z in loc]


def frame(n):
    n = Vector(n).normalized()
    t1 = n.cross(Z if abs(n.z) < 0.95 else Vector((1, 0, 0))).normalized()
    return n, t1, n.cross(t1)


def hull2d(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def clip_poly(poly, n, c):
    """Sutherland-Hodgman: keep the part of poly on the side n.(p - c) >= 0."""
    out = []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        dp, dq = n.dot(p - c), n.dot(q - c)
        if dp >= 0:
            out.append(p)
        if (dp >= 0) != (dq >= 0):
            out.append(p + (q - p) * (dp / (dp - dq)))
    return out


def moss_decal(a, rng, piece, c, n, r, off=0.06, min_dot=0.3):
    """Moss that hugs the facets: an irregular convex outline (radius r, in the
    plane across n) projected along n onto the n-facing faces of a convex
    rock, each clipped piece lifted `off` off its own face."""
    n, t1, t2 = frame(n)
    c = Vector(c)
    rot = rng.uniform(0, TAU)
    k = 7
    outline = hull2d([(math.cos(rot + TAU * i / k + rng.uniform(-0.2, 0.2)) * r * rng.uniform(0.65, 1.0),
                       math.sin(rot + TAU * i / k + rng.uniform(-0.2, 0.2)) * r * rng.uniform(0.65, 1.0))
                      for i in range(k)])
    if len(outline) < 3:
        return []
    planes = []
    for i, (x0, y0) in enumerate(outline):
        x1, y1 = outline[(i + 1) % len(outline)]
        p0 = c + t1 * x0 + t2 * y0
        e = t1 * (x1 - x0) + t2 * (y1 - y0)
        inward = n.cross(e).normalized()  # outline is CCW in (t1, t2), n = t1 x t2
        planes.append((inward, p0))
    faces = []
    for f in list(piece.faces):
        if not f.is_valid or f.normal.dot(n) < min_dot:
            continue
        poly = [v.co.copy() for v in f.verts]
        for pn, pc in planes:
            poly = clip_poly(poly, pn, pc)
            if len(poly) < 3:
                break
        if len(poly) < 3:
            continue
        area = sum(((poly[i] - poly[0]).cross(poly[i + 1] - poly[0])).length for i in range(1, len(poly) - 1))
        if area < 0.02:
            continue
        vs = [a.bm.verts.new(p + f.normal * off) for p in poly]
        nf = a.bm.faces.new(vs)
        nf.normal_update()
        if nf.normal.dot(f.normal) < 0:
            nf.normal_flip()
        paint(a, [nf], MOSS, rng.uniform(0.95, 1.05), 0.0)
        faces.append(nf)
    return faces


def leaf(a, rng, base, d, L, W, droop=0.25, fold=0.12, th=0.08):
    """Broad rounded leaf, 6 tris: a fan round a raised midrib point, edges
    turned down, the tip drooping."""
    bm = a.bm
    d = Vector(d).normalized()
    side = d.cross(Z)
    if side.length < 1e-4:
        side = Vector((1, 0, 0))
    side.normalize()
    u = side.cross(d).normalized()
    if u.z < 0:
        u = -u
    b = Vector(base)

    def at(t):
        return b + d * L * t - Z * L * droop * t * t

    B, T = at(0.0), at(1.0)
    L1 = at(0.3) + side * W * 0.44 - u * fold * W
    R1 = at(0.3) - side * W * 0.44 - u * fold * W
    L2 = at(0.7) + side * W * 0.4 - u * fold * W
    R2 = at(0.7) - side * W * 0.4 - u * fold * W
    M = at(0.45) + u * th
    pts = [B, L1, L2, T, R2, R1]
    for p in pts + [M]:
        p.z = max(p.z, 0.0)
    vs = [bm.verts.new(p) for p in pts]
    m = bm.verts.new(M)
    faces = [bm.faces.new((vs[i], vs[(i + 1) % 6], m)) for i in range(6)]
    for f in faces:
        f.normal_update()
    if sum((f.normal for f in faces), Vector()).dot(u) < 0:
        for f in faces:
            f.normal_flip()
    paint(a, faces, LEAF, rng.uniform(0.95, 1.05), 0.02)
    return faces


# horizontal direction toward the studio camera (front-left): flowers face it
CAM = Vector((-0.38, -0.92, 0.0)).normalized()


def flower(a, rng, c, R=0.36, up=Z):
    """Five-petal white star with a yellow eye (11 tris)."""
    up, t1, t2 = frame(up)
    c = Vector(c)
    bm = a.bm
    mid = bm.verts.new(c + up * 0.03)
    rot = rng.uniform(0, TAU)
    rim = []
    for i in range(10):
        ang = rot + TAU * i / 10
        rr = R if i % 2 == 0 else R * 0.42
        rim.append(bm.verts.new(c + (t1 * math.cos(ang) + t2 * math.sin(ang)) * rr))
    faces = [bm.faces.new((rim[i], rim[(i + 1) % 10], mid)) for i in range(10)]
    for f in faces:
        f.normal_update()
        if f.normal.dot(up) < 0:
            f.normal_flip()
    paint(a, faces, "flower_white", rng.uniform(0.96, 1.04), 0.0)
    eye = [bm.verts.new(c + up * 0.06 + (t1 * math.cos(rot + TAU * i / 3) + t2 * math.sin(rot + TAU * i / 3)) * R * 0.3)
           for i in range(3)]
    ef = bm.faces.new(eye)
    ef.normal_update()
    if ef.normal.dot(up) < 0:
        ef.normal_flip()
    paint(a, [ef], "flower_yellow", 1.0, 0.0)
    return faces + [ef]


CLUMP_FLAT = 0.88  # clumps are leafy banks a little lower than a round ball, so the rock shows


def clump(a, rng, c, r, up=Z, n=None, flowers=0, sz=CLUMP_FLAT):
    """Rounded leaf ball: a faceted green dome (fills the gaps) with broad
    rounded leaves spread over it from crown to ground, each pointing out
    along the dome. sz flattens the dome into a lower bank."""
    up, t1, t2 = frame(up)
    c = Vector(c)
    n = n or (16 if r >= 1.15 else (14 if r >= 0.95 else (12 if r >= 0.8 else 9)))
    rx, rz = 0.68 * r, 0.86 * r * sz
    core = []
    for rr, hz, cnt in ((1.0, 0.0, 6), (0.86, 0.48, 5), (0.45, 0.88, 3)):
        rot = rng.uniform(0, TAU)
        for i in range(cnt):
            ang = rot + TAU * i / cnt + rng.uniform(-0.2, 0.2)
            core.append(c + (t1 * math.cos(ang) + t2 * math.sin(ang)) * rx * rr * rng.uniform(0.9, 1.05)
                        + up * rz * hz)
    faces = hull(a, core, merge=0)
    dead = [f for f in faces if f.normal.dot(up) < -0.85]
    if dead:
        bmesh.ops.delete(a.bm, geom=dead, context="FACES_ONLY")
    faces = [f for f in faces if f.is_valid]
    for f in faces:
        paint(a, [f], LEAF, rng.uniform(0.96, 1.04), 0.0)
    az0 = rng.uniform(0, TAU)
    ga = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        # leaves scale the dome like shingles: crown leaves tilt ~40 deg up,
        # low ones lie nearly flat, so the clump reads as a round leaf ball
        f = (i + 0.5) / n
        el = math.asin(max(0.0, 1.0 - f * 0.92))
        az = az0 + ga * i + rng.uniform(-0.2, 0.2)
        hor = t1 * math.cos(az) + t2 * math.sin(az)
        b = c + hor * math.cos(el) * rx * 0.55 + up * (math.sin(el) * rz * 0.78 + 0.05)
        pitch = 0.25 + 0.6 * el / (math.pi / 2) + rng.uniform(-0.08, 0.08)
        d = hor * math.cos(pitch) + up * math.sin(pitch)
        L = r * rng.uniform(0.55, 0.65)
        faces += leaf(a, rng, b, d, L, L * rng.uniform(1.0, 1.15), droop=rng.uniform(0.1, 0.2), fold=0.1)
    for k in range(flowers):
        # on the crown's front shoulder, tipped toward the viewer so the white
        # star reads at cell scale instead of edge-on
        az = math.atan2(CAM.y, CAM.x) + (k - (flowers - 1) / 2) * 1.1 + rng.uniform(-0.2, 0.2)
        hor = Vector((math.cos(az), math.sin(az), 0.0))
        p = c + up * (rz * 0.88 + 0.16) + hor * rx * 0.55
        faces += flower(a, rng, p, 0.5, up=(Z * 1.1 + hor * 0.8).normalized())
    return faces


def top_face(piece, zmin=0.0, nz=0.55):
    cands = [f for f in piece.faces if f.is_valid and f.normal.z > nz
             and f.calc_center_median().z > zmin]
    if not cands:
        return None
    return max(cands, key=lambda f: f.calc_area() * (0.3 + f.normal.z))


def cull_hidden(a, pieces):
    """Delete faces buried entirely inside another rock chunk."""
    rocks = [p for p in pieces if p.kind == "rock"]
    dead = set()
    for p in pieces:
        for f in p.faces:
            if not f.is_valid:
                continue
            for q in rocks:
                if q is p:
                    continue
                if all(q.contains(v.co) for v in f.verts):
                    dead.add(f)
                    break
    if dead:
        bmesh.ops.delete(a.bm, geom=list(dead), context="FACES_ONLY")
        loose = [v for v in a.bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(a.bm, geom=loose, context="VERTS")


def drop_bottoms(a):
    """Remove ground-contact faces (never seen) and clamp anything below z=0."""
    for v in a.bm.verts:
        if v.co.z < 0.0:
            v.co.z = 0.0
    a.bm.normal_update()
    dead = [f for f in a.bm.faces if f.normal.z < -0.97 and f.calc_center_median().z < 0.03]
    if dead:
        bmesh.ops.delete(a.bm, geom=dead, context="FACES_ONLY")
        loose = [v for v in a.bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(a.bm, geom=loose, context="VERTS")


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------


class Builder:
    def __init__(self, kit, name, seed):
        self.a = kit.flintkit.Asset(name, "Rocks", seed=seed, tint_var=0.04)
        self.rng = random.Random(seed)
        self.pieces = []

    def rocks(self):
        return [p for p in self.pieces if p.kind == "rock"]

    def rock(self, pts, rng, merge=4.0):
        faces = hull(self.a, pts, merge)
        rock_paint(self.a, faces, rng)
        p = Piece(faces, "rock")
        self.pieces.append(p)
        return p

    def spire(self, seed, merge=2.0, **kw):
        rng = random.Random(seed)
        return self.rock(spire_pts(rng, **kw), rng, merge)

    def shoulder(self, seed, merge=4.0, **kw):
        rng = random.Random(seed)
        return self.rock(shoulder_pts(rng, **kw), rng, merge)

    def boulder(self, c, size, seed=None, merge=5.0, **kw):
        rng = random.Random(seed) if seed is not None else self.rng
        return self.rock(boulder_pts(rng, c, size, **kw), rng, merge)

    def block(self, c, yaw, w, d, h, point, seed):
        rng = random.Random(seed)
        return self.rock(block_pts(rng, c, yaw, w, d, h, point), rng, 6.0)

    def surface(self, x, y, n=Z):
        """Highest rock surface above (x, y) along -n: (point, normal) or None."""
        n = Vector(n).normalized()
        o = Vector((x, y, 0.0)) + n * 40.0
        best = None
        for p in self.rocks():
            hit = p.ray(o, -n)
            if hit and (best is None or hit[0] < best[0]):
                best = hit
        if best is None:
            return None
        return o - n * best[0], best[1]

    def moss(self, piece, c, n, r, min_dot=0.3):
        faces = moss_decal(self.a, self.rng, piece, c, n, r, min_dot=min_dot)
        if faces:
            self.pieces.append(Piece(faces, "moss"))

    def cap(self, piece, r, shift=(0.0, 0.0), n=Z):
        """Moss patch on a rock's top facet(s), optionally shifted toward one
        side; n tips the projection so the patch runs over the top edge onto
        the facet below (a patch, never a cap over the whole top)."""
        f = top_face(piece)
        if f is None:
            return
        at = f.calc_center_median()
        self.moss(piece, Vector((at.x + shift[0], at.y + shift[1], at.z)), Vector(n), r, min_dot=0.2)

    def side_moss(self, piece, axis, z, direction, r):
        """Moss smudge on the side of a rock: the outline is centred on the
        line through (axis xy, z) along `direction`."""
        d = Vector(direction).normalized()
        n, t1, t2 = frame(d)
        c = Vector((axis[0], axis[1], z))
        self.moss(piece, c, d, r * 0.75)  # two overlapping lobes: an irregular smudge
        self.moss(piece, c + t1 * r * 0.55 - Z * r * 0.35, d, r * 0.55)

    def clump_at(self, x, y, r, flowers=0):
        """Leafy clump sitting on whatever rock is under (x, y), or the ground."""
        hit = self.surface(x, y)
        if hit is None:
            self.ground_clump(x, y, r, flowers)
            return
        p, nn = hit
        up = (nn + Z * 1.5).normalized()
        self.pieces.append(Piece(clump(self.a, self.rng, p - nn * 0.05, r, up=up, flowers=flowers), "leaf"))

    def ground_clump(self, x, y, r, flowers=0):
        self.pieces.append(Piece(clump(self.a, self.rng, (x, y, 0.0), r, flowers=flowers), "leaf"))

    def rubble(self, x, y, s):
        self.boulder((x, y), (s * self.rng.uniform(1.1, 1.4), s, s * self.rng.uniform(0.75, 0.95)), n=6,
                     merge=8.0)

    def finish(self, kit, role, collision, notes=""):
        cull_hidden(self.a, self.pieces)
        drop_bottoms(self.a)
        obj = self.a.finish()
        return kit.tag(obj, role, collision=collision, notes=notes)


def polar(spec, centre):
    """[(angle deg, radius, value...)] -> [(x, y, value...)] around centre."""
    out = []
    for s in spec:
        t = math.radians(s[0])
        out.append((centre[0] + math.cos(t) * s[1], centre[1] + math.sin(t) * s[1]) + tuple(s[2:]))
    return out


def add_collar(b, centre, radius, spec, seed, depth=1.8):
    """Fused jagged collar ring: blocky wedges overlapping their neighbours.
    spec: [(angle deg, width along ring, height, pointed)]."""
    ps = []
    for i, (ang, w, h, point) in enumerate(spec):
        t = math.radians(ang)
        c = (centre[0] + math.cos(t) * radius, centre[1] + math.sin(t) * radius)
        rng = random.Random(seed * 10 + i)
        ps.append(b.block(c, t + math.pi / 2 + rng.uniform(-0.12, 0.12), w, depth * rng.uniform(0.9, 1.1), h,
                          point, seed * 10 + i))
    return ps


def spire_moss(b, sp, S, spec):
    """Moss patches on a spire: each projected along d from a point on the
    spire's axis at fz * h, shifted sideways by (dx, dy) so the patch sits on
    the facet near an edge rather than in the middle of a face."""
    sc, h = S["c"], S["h"]
    lean = S.get("lean", (0.0, 0.0))
    for m in spec:
        fz, d, r = m[:3]
        dx, dy = m[3] if len(m) > 3 else (0.0, 0.0)
        z = fz * h
        b.moss(sp, Vector((sc[0] + lean[0] * z + dx, sc[1] + lean[1] * z + dy, z)), Vector(d), r, min_dot=0.12)


def assemble(b, L):
    """Build one spire group from a layout dict:
    spire      spire_pts kwargs (c, r, h, lean, rings, tip, drop, slant)
    shoulders  [shoulder_pts kwargs] leaning wedges
    boulders   [(x, y, (sx, sy, sz), yaw)]; the first is the big front boulder
    rubble     [(x, y, size)]
    spire_moss [(height fraction, direction, radius, (dx, dy) side offset)] patches on the spire
    caps       [(piece index into shoulders + boulders, radius, shift[, normal])] moss patches on tops
    clumps     [(x, y, r, flowers, on_rock)]"""
    sp = b.spire(L["seed"], merge=0, **L["spire"])
    if "spire2" in L:  # a second, shorter spire standing beside the main one
        sp2 = b.spire(L["seed"] + 50, merge=0, **L["spire2"])
        spire_moss(b, sp2, L["spire2"], L.get("spire2_moss", []))
    shs =[b.shoulder(L["seed"] + 1 + i, **s) for i, s in enumerate(L["shoulders"])]
    fs = [b.boulder((x, y), size, seed=L["seed"] + 10 + i, yaw=yaw, n=16 if i == 0 else 12,
                    p=2.4 if i == 0 else 3.0, merge=3.0 if i == 0 else 5.0)
          for i, (x, y, size, yaw) in enumerate(L["boulders"])]
    for x, y, s in L["rubble"]:
        b.rubble(x, y, s)
    spire_moss(b, sp, L["spire"], L["spire_moss"])
    pieces = shs + fs
    for cp in L["caps"]:
        b.cap(pieces[cp[0]], cp[1], shift=cp[2], n=cp[3] if len(cp) > 3 else Z)
    for x, y, r, fl, on_rock in L["clumps"]:
        r *= L.get("clump_scale", 1.0)
        if on_rock:
            b.clump_at(x, y, r, fl)
        else:
            b.ground_clump(x, y, r, fl)
    return sp


# Hero layout (front = -Y; the studio camera looks from the front-left). Fits
# ~8 x 7 x 11: a 4.5-wide spire, a tall left wedge and a lower right wedge
# leaning on it, a big faceted front boulder and smaller foot boulders spread
# round the base, leafy clumps banked into the gaps.
def obelisk(fzs, top=0.28, top_z=1.0, k=1.25):
    # top is the radius fraction extrapolated to the full height, matching the
    # chisel tip's half width, so no ring falls inside the hull under the tip.
    """Ring (height, radius) fractions for a near-linear taper with a faint
    bulge (k > 1), so every ring stays on the hull and each ring step makes a
    visible facet break instead of dissolving into one long flat face."""
    a = (1.0 - top) / top_z ** k
    return [(fz, 1.0 - a * fz ** k) for fz in fzs]


SC = (0.1, 0.35)
# Thick obelisk: 4.9 x 4.4 at the foot, ~3.4 wide at mid height, ~1.4 under the
# chisel; 9 rings of 8 points; the chisel's low side looks at the front/camera.
SPIRE = dict(c=SC, r=(2.55, 2.25), h=11.0, lean=(-0.01, -0.01), n=8, tip=0.62, drop=1.9,
             slant=(-0.35, -0.95), jit=0.03, zjit=0.008,
             rings=obelisk((0.0, 0.09, 0.18, 0.27, 0.36, 0.45, 0.54, 0.63, 0.72, 0.81), top=0.25, k=1.08))
WEDGE_RINGS = ((0.0, 1.0), (0.5, 0.9), (1.0, 0.8))  # upright slab: walls nearly vertical
WEDGE_TAPER = ((0.0, 1.0), (0.5, 0.8), (1.0, 0.58))  # hero wedges: sloping outer walls
# moss on the spire: the front-right facet near the right edge at ~63% height
# (projected from the front, so the lime patch faces the light and the camera)
SPIRE_MOSS = (0.62, (0.35, -0.88, 0.3), 1.05, (0.7, -0.1))

HERO = dict(
    seed=1,
    spire=SPIRE,
    # Two separate upright wedges standing against the spire flanks, walls
    # nearly vertical and no inward lean, so a crease opens between each top
    # and the narrowing spire: left top ~61%, right ~45%, tops slope outward.
    # The wedges taper and lean in a little, so their outer walls slope and
    # the outline runs diagonally from the spire down to the foot.
    shoulders=[dict(c=(-2.3, -0.15), r=(1.6, 1.45), h=6.8, out=(-1.0, -0.1), tilt=32, lean_in=0.09, n=5,
                    rings=WEDGE_TAPER),
               dict(c=(2.35, -0.45), r=(1.4, 1.35), h=5.0, out=(1.0, -0.25), tilt=26, lean_in=0.08, n=5,
                    rings=WEDGE_TAPER)],
    # Broad triangle in the front-left view (screen x ~ 0.93x - 0.37y): the
    # outline steps tip -> wedges (6.8 / 5.0) -> a middle row (~3.0) -> LOW
    # corner boulders (~2.2) out at the screen corners, which are the
    # back-left (-x, +y) and front-right (+x, -y) corners of a 9 x 7.6 footprint.
    # Nothing reaches far into the front-left quadrant: it is nearest the
    # camera, so it would only stretch the cell vertically.
    boulders=[(0.3, -1.85, (4.0, 2.8, 3.6), 0.35),    # big front boulder (~4 wide)
              (-3.7, 2.7, (2.1, 1.9, 2.0), 0.8),      # back-left ground corner (screen left), low
              (3.7, -2.85, (2.0, 1.8, 1.9), 1.2),     # front-right ground corner (screen right), low
              (-3.4, 0.7, (2.1, 2.1, 3.1), 0.3),      # middle row, left: between wedge and corner
              (3.5, -1.05, (1.9, 1.9, 3.0), 1.9),     # middle row, right
              (3.3, 1.8, (2.0, 1.9, 2.4), 0.6),       # back right
              (-3.0, -1.35, (1.8, 1.7, 1.6), -0.5)],  # front-left, low
    # rubble: one stone out at each screen corner (the foot's toes), others
    # on open ground at the sides and back
    rubble=[(4.45, -3.5, 0.5), (-4.45, 3.45, 0.5), (1.6, -3.35, 0.55), (4.15, 0.45, 0.5),
            (-4.3, 1.7, 0.45), (0.2, 3.3, 0.55)],
    spire_moss=[SPIRE_MOSS],
    caps=[(0, 0.8, (-0.45, -0.35), (-0.35, -0.55, 0.75)),   # left wedge: patch over its front-left top edge
          (2, 0.7, (-0.7, 0.2), (-0.2, -0.3, 0.9)),         # front boulder top-left
          (1, 0.6, (0.35, -0.45), (0.3, -0.6, 0.75)),       # right wedge front
          (5, 0.5, (0.0, -0.2), (0.0, -0.5, 0.85))],        # middle-left boulder top
    clumps=[(-2.45, -1.75, 0.75, 1, False),  # front-left bank: front-left boulder / front boulder
            (-1.75, -1.9, 0.7, 0, True),    #   ... between them
            (-0.95, -2.15, 0.9, 0, True),   #   ... climbing the front boulder's left shoulder
            (1.2, -2.95, 0.7, 0, False),    # in front of the front boulder's right side
            (-2.95, 0.05, 0.6, 0, True),    # small clump on the left wedge's back-left top corner
            (2.15, -2.95, 0.85, 1, False),  # front-right bank: front boulder / right corner
            (2.3, -1.55, 0.95, 0, True),    #   ... up in the notch above it
            (1.5, -0.55, 0.9, 0, True),     # bank between the front boulder and the spire, right
            (2.7, -0.25, 1.05, 1, True),    # on the right wedge top
            (-3.55, -0.55, 0.85, 0, True),  # left middle row, at the wedge foot
            (-4.05, 1.65, 0.6, 0, False),   # left, between the middle and corner boulders
            (3.85, 0.55, 0.7, 0, False),    # right side ground, between the right boulders
            (3.95, -1.95, 0.65, 0, True),   # on the right corner boulder's shoulder
            (-1.9, 3.05, 0.75, 0, False),   # back ground (top view rim)
            (1.4, 3.05, 0.75, 0, False)],
)

SHORT = dict(
    seed=11,
    spire=dict(c=(0.4, 0.6), r=(2.3, 2.0), h=6.9, lean=(-0.02, 0.0), n=8, tip=0.75, drop=1.35,
               slant=(-0.45, -0.9), jit=0.02, zjit=0.008,
               rings=obelisk((0.0, 0.13, 0.26, 0.39, 0.52, 0.64, 0.76), top=0.33)),
    shoulders=[dict(c=(-1.75, -0.35), r=(1.6, 1.45), h=4.3, out=(-1.0, -0.3), tilt=24, lean_in=0.0, n=5,
                    rings=WEDGE_RINGS)],
    boulders=[(0.6, -1.55, (3.3, 2.6, 2.9), 0.3), (-2.6, -1.35, (2.1, 1.9, 2.0), -0.4),
              (2.6, -0.65, (2.0, 1.8, 2.1), 1.4), (-2.0, 1.6, (1.8, 1.6, 1.8), 0.9),
              (2.35, 1.5, (1.7, 1.5, 1.6), 0.2)],
    rubble=[(-1.55, -2.8, 0.5), (1.95, -2.7, 0.5), (-3.25, 0.3, 0.45)],
    spire_moss=[(0.62, (0.35, -0.88, 0.3), 0.6, (0.6, -0.1))],
    caps=[(0, 0.6, (-0.3, -0.25), (-0.35, -0.55, 0.75)), (2, 0.5, (-0.3, 0.2))],
    clumps=[(-0.55, -2.7, 0.9, 1, False), (0.45, -2.95, 0.75, 0, False),
            (2.6, -2.05, 0.9, 0, False), (2.65, -0.55, 0.85, 1, True),
            (-2.95, -2.3, 0.8, 0, False), (-1.25, -1.2, 0.8, 0, True), (3.1, 0.6, 0.75, 0, False),
            (-3.1, 0.6, 0.75, 0, False)],
)

TALL = dict(
    seed=21,
    # main needle: ~3.6 wide at the foot, ~2.5 at mid height, ~1.2 under its chisel
    spire=dict(c=(0.75, 0.35), r=(1.8, 1.6), h=14.0, lean=(-0.008, 0.0), n=8, tip=0.6, drop=1.6,
               slant=(-0.4, -0.9), jit=0.02, zjit=0.008,
               rings=obelisk((0.0, 0.09, 0.18, 0.27, 0.36, 0.45, 0.54, 0.63, 0.72, 0.8, 0.87), top=0.3)),
    # the second, shorter spire standing to the LEFT of the needle (~57% of its
    # height): a separate obelisk ~2.7 wide with its own slanted chisel tip,
    # its upper half clear of the needle and of every wedge
    spire2=dict(c=(-1.6, 0.55), r=(1.35, 1.25), h=8.0, lean=(-0.015, 0.0), n=7, tip=0.5, drop=1.2,
                slant=(-0.75, -0.65), jit=0.03, zjit=0.01,
                rings=obelisk((0.0, 0.14, 0.28, 0.42, 0.56, 0.7, 0.82), top=0.38)),
    spire2_moss=[(0.6, (-0.2, -0.9, 0.35), 0.55, (0.2, 0.0))],
    # stepped foot: a right wedge (~39%) and LOW boulders (<= 2.5) round the
    # base, so both spires stand clear above them; ~6.3 x 6.7
    shoulders=[dict(c=(2.3, -0.55), r=(1.15, 1.15), h=5.5, out=(1.0, -0.3), tilt=28, lean_in=0.05, n=5,
                    rings=WEDGE_TAPER)],
    boulders=[(0.5, -1.85, (2.4, 2.0, 2.5), 0.3), (-1.85, -1.25, (1.9, 1.7, 2.0), 0.2),
              (2.45, -2.25, (1.6, 1.5, 2.0), 1.1), (-2.3, 2.2, (1.6, 1.4, 1.7), -0.4),
              (2.15, 1.65, (1.6, 1.5, 2.0), 1.6), (0.45, 2.35, (1.6, 1.3, 1.5), 0.7)],
    rubble=[(-2.55, -2.55, 0.45), (2.75, -2.75, 0.4), (-0.95, -2.85, 0.4)],
    spire_moss=[(0.74, (0.35, -0.88, 0.3), 0.6, (0.45, -0.05))],
    caps=[(0, 0.5, (0.2, -0.3), (0.3, -0.6, 0.75))],
    clumps=[(-0.4, -2.55, 0.9, 1, False), (1.55, -2.6, 0.8, 0, False),
            (-1.7, -1.5, 0.85, 0, True), (2.25, -0.65, 0.85, 0, True), (0.75, -1.75, 0.8, 0, True),
            (-2.35, -2.2, 0.7, 0, False), (-2.5, -0.45, 0.6, 0, False),
            (2.2, 2.55, 0.6, 0, False), (-1.0, 2.6, 0.6, 0, False)],
)

LEAN = dict(
    seed=31,
    # tipped ~17 degrees toward -X; a right wedge props it, and big foot
    # boulders with a clump bank sit under the low (left) side
    spire=dict(c=(1.0, 0.45), r=(2.15, 1.85), h=10.0, lean=(-0.3, 0.0), n=8, tip=0.6, drop=1.4,
               slant=(-0.6, -0.8), jit=0.02, zjit=0.008,
               rings=obelisk((0.0, 0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 0.76, 0.84), top=0.28)),
    shoulders=[dict(c=(2.6, -0.2), r=(1.5, 1.4), h=4.6, out=(1.0, -0.3), tilt=22, lean_in=0.0, n=5,
                    rings=WEDGE_RINGS)],
    boulders=[(0.75, -1.65, (3.2, 2.6, 2.8), 0.3), (-1.65, -1.4, (2.5, 2.2, 2.3), -0.4),
              (2.95, 1.35, (1.8, 1.6, 1.7), 1.1), (0.45, 2.15, (1.8, 1.5, 1.4), 0.6),
              (-1.85, 1.15, (1.9, 1.7, 1.8), 0.9)],
    rubble=[(-2.6, -2.6, 0.5), (3.35, -2.0, 0.45), (1.9, 2.65, 0.45)],
    spire_moss=[(0.55, (0.35, -0.88, 0.3), 0.6, (0.45, -0.1))],
    caps=[(1, 0.55, (-0.3, 0.2), (-0.2, -0.3, 0.9)), (0, 0.5, (0.2, -0.3), (0.3, -0.6, 0.75))],
    clumps=[(-2.95, -0.25, 0.95, 0, False), (-2.75, -2.0, 0.85, 1, False), (-0.6, -2.0, 0.8, 0, True),
            (2.75, -0.35, 0.9, 1, True), (2.45, -2.4, 0.85, 0, False),
            (-0.4, -2.85, 0.85, 1, False), (3.6, 0.1, 0.75, 0, False), (-0.6, 2.4, 0.75, 0, False)],
)

# Jagged chunky collar: 5 blocks fused at the bases, low at the front (2.0),
# three peaked teeth at the back (2.9 / 3.4 / 3.5) with notches between them.
COLLAR = [(-90, 3.2, 2.0, 0.3), (-160, 3.0, 2.6, 1), (138, 2.7, 3.4, 1),
          (70, 2.7, 2.9, 1), (8, 2.8, 3.5, 1)]


def build_hero(kit):
    b = Builder(kit, "RockSpire", 201)
    assemble(b, HERO)
    return b.finish(kit, "hero", "hull",
                    "spire, two leaning shoulder wedges, front boulder and foot boulders; hull is a broad cone. "
                    "Leafy clumps and flowers ride along (ideally a no-collide piece)")


def build_main(kit):
    b = Builder(kit, "RockSpireMain", 201)
    sp = b.spire(HERO["seed"], merge=0, **SPIRE)
    spire_moss(b, sp, SPIRE, [SPIRE_MOSS])
    return b.finish(kit, "part", "hull", "main spire mesh alone; sits in RockSpireFootCollar")


def build_collar(kit):
    b = Builder(kit, "RockSpireFootCollar", 201)
    ps = add_collar(b, (0.0, 0.0), 2.45, COLLAR, 5, depth=2.3)
    b.cap(ps[2], 0.55, n=(-0.3, -0.5, 0.8))
    b.cap(ps[4], 0.5, n=(0.3, -0.5, 0.8))
    # a small rock wedged in the notch between two front teeth
    for x, y, s in polar([(-125, 3.0, 0.65), (40, 3.15, 0.55)], (0.0, 0.0)):
        b.rubble(x, y, s)
    for x, y, r, fl in polar([(-40, 3.4, 0.85, 1), (-130, 3.4, 0.75, 0), (190, 3.35, 0.7, 0),
                              (-65, 3.2, 0.6, 0), (105, 3.1, 0.6, 0)], (0.0, 0.0)):
        b.ground_clump(x, y, r, fl)
    # clumps lodged on the ring's top, in the notches between the teeth
    for x, y, r, fl in polar([(39, 2.5, 0.6, 0), (-125, 2.5, 0.6, 1), (104, 2.5, 0.55, 0)], (0.0, 0.0)):
        b.clump_at(x, y, r, fl)
    return b.finish(kit, "part", "precise", "fused ring of 5 low jagged foot rocks, open in the middle for the spire")


def build_short(kit):
    b = Builder(kit, "RockSpireShort", 211)
    assemble(b, SHORT)
    return b.finish(kit, "variant", "hull", "stubby spire")


def build_tall(kit):
    b = Builder(kit, "RockSpireTall", 221)
    assemble(b, TALL)
    return b.finish(kit, "variant", "hull", "high, narrow spire")


def build_leaning(kit):
    b = Builder(kit, "RockSpireLeaning", 231)
    assemble(b, LEAN)
    return b.finish(kit, "variant", "hull", "spire tilted ~17 degrees to the left")


def build(kit):
    return [build_hero(kit), build_main(kit), build_collar(kit),
            build_short(kit), build_tall(kit), build_leaning(kit)]
