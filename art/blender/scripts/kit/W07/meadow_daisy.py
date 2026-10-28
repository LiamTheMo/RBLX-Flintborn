"""W07 row 2 - Meadow Daisy: 5-petal daisies on slender stems over a leaf rosette."""
import math

import bmesh
from mathutils import Euler, Vector

SUBJECT = "MeadowDaisy"
ROW = 2
HERO_AZIMUTH = -22
PALETTE = {
    "w07_leaf": ("#62B232", 0.8, 0, 0),  # leaves and stems of daisies and wildflowers, plus fresh green scatter leaf
    "w07_petal_white": ("#F2EAD2", 0.85, 0, 0),  # daisy petals
    "w07_daisy_yellow": ("#F5B800", 0.8, 0, 0),  # daisy centers and Yellow Clump petals
}

D = math.radians
LEAF_PROFILE = [(0.0, 0.0), (0.18, 0.62), (0.45, 1.0), (0.72, 0.72), (0.9, 0.3), (1.0, 0.0)]
PETAL_PROFILE = [(0.0, 0.0), (0.15, 0.45), (0.58, 1.0), (0.84, 0.45), (1.0, 0.0)]


def blade(a, L, w, mat, profile=LEAF_PROFILE, crease=0.06, arch=0.1, thick=0.05,
          loc=(0, 0, 0), rot=(0, 0, 0)):
    """Closed faceted blade along +Y (base at origin), top facing +Z, V-crease
    down the middle, gentle arch. Returns verts."""
    bm = a.bm
    n = len(profile)

    def z_of(t):
        return arch * 4.0 * t * (1.0 - t)

    base = bm.verts.new((0, 0, 0))
    tip = bm.verts.new((0, L, z_of(1.0)))
    right, left, spine_t, spine_b = [base], [base], [None], [None]
    for t, hw in profile[1:-1]:
        y, z = t * L, z_of(t)
        right.append(bm.verts.new((hw * w * 0.5, y, z)))
        left.append(bm.verts.new((-hw * w * 0.5, y, z)))
        spine_t.append(bm.verts.new((0, y, z - crease)))
        spine_b.append(bm.verts.new((0, y, z - crease - thick)))
    right.append(tip)
    left.append(tip)

    def side(E, S, flip):
        faces = [(E[0], E[1], S[1])]
        for i in range(1, n - 2):
            faces.append((E[i], E[i + 1], S[i + 1], S[i]))
        faces.append((E[n - 2], E[n - 1], S[n - 2]))
        for f in faces:
            bm.faces.new(tuple(reversed(f)) if flip else f)

    side(right, spine_t, False)
    side(left, spine_t, True)
    side(right, spine_b, True)
    side(left, spine_b, False)
    verts = [base, tip] + right[1:-1] + left[1:-1] + spine_t[1:] + spine_b[1:]
    a.transform(verts, loc, rot)
    return a._finish(verts, mat)


def tube(a, pts, radii, mat="w07_leaf", sides=6):
    """Faceted stalk through pts with per-point radii; top capped, bottom open
    (it sits on the ground)."""
    bm = a.bm
    pts = [Vector(p) for p in pts]
    rings = []
    for i, p in enumerate(pts):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == len(pts) - 1:
            t = pts[-1] - pts[-2]
        else:
            t = (pts[i + 1] - pts[i - 1])
        t.normalize()
        ref = Vector((0, 1, 0)) if abs(t.y) < 0.9 else Vector((1, 0, 0))
        u = t.cross(ref).normalized()
        v = t.cross(u).normalized()
        r = radii[i]
        rings.append([bm.verts.new(p + r * (math.cos(2 * math.pi * k / sides) * u +
                                            math.sin(2 * math.pi * k / sides) * v))
                      for k in range(sides)])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            k2 = (k + 1) % sides
            bm.faces.new((r0[k], r0[k2], r1[k2], r1[k]))
    try:
        bm.faces.new(rings[-1])
    except ValueError:
        pass
    verts = [v for r in rings for v in r]
    bmesh.ops.recalc_face_normals(bm, faces=list({f for v in verts for f in v.link_faces}))
    return a._finish(verts, mat)


def head(a, loc, tilt, yaw, size=1.0, petal="w07_petal_white", centre="w07_daisy_yellow",
         lift=20, spin=0.0, pw=0.5):
    """5-petal daisy head built facing +Z, then tilted toward -Y by `tilt` deg and
    yawed by `yaw` deg. Returns the head's normal (unit vector)."""
    verts = []
    L, R = 0.64 * size, 0.1 * size
    for i in range(5):
        phi = D(spin + i * 72 + a.rng.uniform(-5, 5))
        lf = D(lift + a.rng.uniform(-5, 5))
        d = Vector((-math.sin(phi) * math.cos(lf), math.cos(phi) * math.cos(lf), math.sin(lf)))
        verts += blade(a, L, pw * size, petal, PETAL_PROFILE, crease=0.07 * size,
                       arch=0.05 * size, thick=0.035 * size,
                       loc=tuple(d * R + Vector((0, 0, 0.02 * size))), rot=(lf, 0, phi))
    verts += a.ico((0.25 * size, 0.25 * size, 0.17 * size), loc=(0, 0, 0.07 * size),
                   mat=centre, subdiv=1, jitter=0.015 * size)
    rot = (D(tilt), 0, D(yaw))
    a.transform(verts, loc, rot)
    n = Vector((0, 0, 1))
    n.rotate(Euler(rot))
    return n


def gem_petal(a, L=1.0, w=0.5, t=0.12, mat="w07_petal_white"):
    """Standing faceted petal (base at z=0, tip at z=L): lozenge outline widest at
    60%, ridge on the front (-Y), shallow crease on the back. 64 tris."""
    bm = a.bm
    hw = w * 0.5
    sec = [(1, 0), (0.55, -1.0), (0, -1.45), (-0.55, -1.0), (-1, 0), (-0.55, 0.55),
           (0, 0.15), (0.55, 0.55)]
    prof = [(0.14, 0.5), (0.36, 0.85), (0.6, 1.0), (0.82, 0.6)]
    base = bm.verts.new((0, 0, 0))
    tip = bm.verts.new((0, 0, L))
    rings = [[bm.verts.new((sx * hw * k, sy * t * k, z * L)) for sx, sy in sec] for z, k in prof]
    n = len(sec)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((base, rings[0][j], rings[0][i]))
        bm.faces.new((tip, rings[-1][i], rings[-1][j]))
        for r0, r1 in zip(rings, rings[1:]):
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    verts = [base, tip] + [v for r in rings for v in r]
    bmesh.ops.recalc_face_normals(bm, faces=list({f for v in verts for f in v.link_faces}))
    return a._finish(verts, mat)


def daisy(a, base, headloc, tilt, yaw, size=1.0, bow=(0, 0), **kw):
    """Stem from base to the head plus the head. bow bends the stem mid-way."""
    n = head(a, headloc, tilt, yaw, size, **kw)
    top = Vector(headloc) - n * 0.1 * size
    b = Vector(base)
    m1 = b.lerp(top, 0.4) + Vector((bow[0] * 0.5, bow[1] * 0.5, 0))
    m2 = b.lerp(top, 0.78) + Vector((bow[0], bow[1], 0))
    r = 0.075
    tube(a, [b, m1, m2, top - n * 0.06, top], [r * 1.15, r, r * 0.95, r * 1.0, r * 1.9])


def rosette(a, specs):
    """specs: (phi_deg, length, width, elev_deg, radial_offset)."""
    for phi, L, w, el, off in specs:
        p, e = D(phi), D(el)
        loc = (-math.sin(p) * off, math.cos(p) * off, 0.03)
        blade(a, L, w, "w07_leaf", crease=0.08 * L / 1.4, arch=0.12 * L / 1.4,
              thick=0.05, loc=loc, rot=(e, 0, p))


def build(kit):
    fk = kit.flintkit
    out = []

    # ---------------- hero: 3 daisies over a rosette ----------------
    a = fk.Asset("MeadowDaisy", "W07 MeadowDaisy")
    rosette(a, [
        (0, 1.85, 1.15, 44, 0.15), (40, 1.75, 1.1, 40, 0.15), (80, 1.9, 1.15, 38, 0.15),
        (120, 1.75, 1.1, 42, 0.15), (160, 1.9, 1.15, 40, 0.15), (200, 1.8, 1.15, 46, 0.15),
        (240, 1.9, 1.15, 38, 0.15), (280, 1.75, 1.1, 42, 0.15), (320, 1.85, 1.15, 40, 0.15),
        (140, 1.1, 0.7, 18, 0.2), (215, 1.1, 0.7, 16, 0.2), (300, 1.05, 0.7, 18, 0.2),
        (180, 1.3, 0.75, 58, 0.04), (60, 1.25, 0.75, 60, 0.04), (290, 1.25, 0.75, 62, 0.04),
    ])
    daisy(a, (0.05, 0.1, 0), (0.1, 0.1, 2.95), 62, 0, 1.2, bow=(0.12, 0.05), pw=0.5)
    daisy(a, (-0.15, -0.05, 0), (-1.05, -0.5, 2.15), 62, -25, 1.15, bow=(-0.35, 0), pw=0.5)
    daisy(a, (0.2, 0.1, 0), (1.05, 0.35, 2.5), 60, 18, 1.15, bow=(0.35, 0), pw=0.5)
    o = a.finish()
    out.append(kit.tag(o, "hero", collision="none", budget=1500,
                       notes="3 daisies (5 petals each) over a leaf rosette; walk-through scatter"))

    # ---------------- parts ----------------
    a = fk.Asset("Petal", "W07 MeadowDaisy part")
    gem_petal(a)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=100, notes="one daisy petal"))

    a = fk.Asset("Center", "W07 MeadowDaisy part")
    a.ico((0.26, 0.26, 0.2), loc=(0, 0, 0.2), mat="w07_daisy_yellow", subdiv=2, facets=12,
          jitter=0.02)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=100, notes="daisy centre nugget"))

    a = fk.Asset("Stem", "W07 MeadowDaisy part")
    r = 0.075
    tube(a, [(0, 0, 0), (0, 0, 1.1), (0.1, 0, 1.75), (0.22, 0, 2.2), (0.26, 0, 2.4)],
         [r * 1.1, r, r * 0.95, r, r * 2.0])
    out.append(kit.tag(a.finish(), "part", collision="none", budget=100, notes="daisy stem with flared calyx tip"))

    a = fk.Asset("DaisyLeaf", "W07 MeadowDaisy part")
    blade(a, 1.5, 0.8, "w07_leaf", crease=0.1, arch=0.12, thick=0.05, loc=(0, 0, 0.02),
          rot=(D(80), 0, 0))
    out.append(kit.tag(a.finish(), "part", collision="none", budget=150, notes="broad pointed daisy leaf"))

    # ---------------- variations ----------------
    a = fk.Asset("SingleWhite", "W07 MeadowDaisy variant")
    rosette(a, [(60, 1.6, 0.95, 44, 0.08), (-60, 1.6, 0.95, 42, 0.08),
                (150, 1.5, 0.9, 48, 0.08), (-150, 1.5, 0.9, 50, 0.08),
                (10, 0.8, 0.6, 30, 0.05), (-100, 0.8, 0.6, 28, 0.05)])
    daisy(a, (0, 0.05, 0), (0, -0.05, 2.6), 72, 0, 1.05, bow=(0.06, 0), pw=0.5)
    out.append(kit.tag(a.finish(), "variant", collision="none", budget=700,
                       notes="Single White: one daisy, 4 leaves"))

    def clump(name, petal, pw, heads):
        a = fk.Asset(name, "W07 MeadowDaisy variant")
        rosette(a, [
            (0, 1.5, 0.9, 38, 0.1), (45, 1.4, 0.85, 44, 0.1), (90, 1.5, 0.9, 34, 0.1),
            (135, 1.4, 0.85, 42, 0.1), (180, 1.5, 0.9, 38, 0.1), (225, 1.4, 0.85, 46, 0.1),
            (270, 1.5, 0.9, 36, 0.1), (315, 1.4, 0.85, 42, 0.1),
            (175, 1.25, 0.7, 68, 0.04), (330, 1.25, 0.7, 66, 0.04), (60, 1.2, 0.7, 70, 0.04),
        ])
        for base, hl, tilt, yaw, s, bow in heads:
            daisy(a, base, hl, tilt, yaw, s, bow=bow, petal=petal, pw=pw)
        return a.finish()

    o = clump("WhiteClump", "w07_petal_white", 0.5, [
        ((0.0, 0.1, 0), (0.15, 0.15, 2.65), 64, 10, 0.8, (0.05, 0)),
        ((-0.15, 0.05, 0), (-0.85, 0.0, 2.05), 64, -25, 0.78, (-0.3, 0)),
        ((0.15, 0.05, 0), (0.85, 0.05, 2.3), 64, 25, 0.78, (0.25, 0)),
        ((-0.05, -0.1, 0), (-0.4, -0.45, 1.55), 68, -10, 0.7, (-0.1, -0.1)),
    ])
    out.append(kit.tag(o, "variant", collision="none", budget=1400,
                       notes="White Clump: 4 small white daisies over leaves"))

    o = clump("YellowClump", "w07_daisy_yellow", 0.54, [
        ((0.05, 0.1, 0), (0.35, 0.15, 2.65), 62, 15, 0.85, (0.1, 0)),
        ((-0.15, 0.05, 0), (-0.8, 0.0, 2.15), 62, -25, 0.8, (-0.3, 0)),
        ((0.15, 0.0, 0), (0.95, -0.1, 1.85), 66, 28, 0.75, (0.25, 0)),
        ((-0.05, -0.1, 0), (-0.15, -0.4, 1.45), 68, -5, 0.7, (0, -0.1)),
    ])
    out.append(kit.tag(o, "variant", collision="none", budget=1400,
                       notes="Yellow Clump: 4 all-yellow daisies over leaves"))
    return out
