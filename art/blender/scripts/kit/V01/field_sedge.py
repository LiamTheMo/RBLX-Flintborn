"""V01 row 2: FieldSedge. Open radial fan of broad keeled lance blades with
two brown seed spikes on thin stems, plus parts and variations."""
import math
import random

import bmesh
from mathutils import Vector

SUBJECT = "FieldSedge"
ROW = 2
HERO_AZIMUTH = -22

PALETTE = {
    "v01_sedge_blade": ("#8DB82A", 0.85, 0, 0),  # Field sedge blades (yellow-lime)
    "v01_stem": ("#4C9230", 0.85, 0, 0),  # Stems/stalks/joints of every plant
    "v01_brown": ("#8A5530", 0.9, 0, 0),  # Root bases (all plants) and sedge seed spikes
}

BLADE = "v01_sedge_blade"
STEM = "v01_stem"
BROWN = "v01_brown"

# width profile along the blade (t = 0..1), widest in the lower third
_WPROF = [0.55, 0.92, 1.0, 0.92, 0.74, 0.52, 0.30]


def _frame(d):
    ref = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    s = d.cross(ref).normalized()
    n = s.cross(d).normalized()
    return s, n


def _clamp(verts):
    for v in verts:
        if v.co.z < 0.0:
            v.co.z = 0.0


def loft(a, pts, radii, mat, sides=6, jitter=0.0, rng=None):
    """Tube along a polyline; radius 0 at an end makes a point."""
    bm = a.bm
    pts = [Vector(p) for p in pts]
    rings = []
    allv = []
    for i, p in enumerate(pts):
        if i == 0:
            d = pts[1] - pts[0]
        elif i == len(pts) - 1:
            d = pts[-1] - pts[-2]
        else:
            d = pts[i + 1] - pts[i - 1]
        d.normalize()
        s, n = _frame(d)
        r = radii[i]
        if r <= 1e-5:
            v = bm.verts.new(p)
            rings.append([v])
            allv.append(v)
            continue
        ring = []
        for k in range(sides):
            ang = 2 * math.pi * k / sides
            rr = r * (1 + (rng.uniform(-jitter, jitter) if rng and jitter else 0))
            v = bm.verts.new(p + s * (math.cos(ang) * rr) + n * (math.sin(ang) * rr))
            ring.append(v)
        rings.append(ring)
        allv += ring
    for i in range(len(rings) - 1):
        r0, r1 = rings[i], rings[i + 1]
        if len(r0) == 1 and len(r1) == 1:
            continue
        if len(r0) == 1:
            for k in range(sides):
                bm.faces.new((r0[0], r1[k], r1[(k + 1) % sides]))
        elif len(r1) == 1:
            for k in range(sides):
                bm.faces.new((r0[k], r1[0], r0[(k + 1) % sides]))
        else:
            for k in range(sides):
                bm.faces.new((r0[k], r1[k], r1[(k + 1) % sides], r0[(k + 1) % sides]))
    if len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    if len(rings[-1]) > 1:
        bm.faces.new(rings[-1])
    _clamp(allv)
    return a._finish(allv, mat)


def blade(a, base, phi, length, width, lean, droop, mat=BLADE, cut=None, roll=0.0,
          segs=6, thick=0.16):
    """One keeled lance blade. lean = angle from vertical at the base, droop =
    extra bend added towards the tip (radians). cut = t where the blade is
    clipped with a flat top (None = pointed tip)."""
    bm = a.bm
    p = Vector(base)
    sphi, cphi = math.sin(phi), math.cos(phi)
    wax = Vector((-sphi, cphi, 0))
    tend = 1.0 if cut is None else cut
    n_ring = segs if cut is None else max(2, int(round(segs * cut)) + 1)
    ds = length * tend / (n_ring if cut is None else (n_ring - 1))
    rings = []
    allv = []
    for i in range(n_ring):
        t = (i / segs) if cut is None else (tend * i / (n_ring - 1))
        th = lean + droop * (t ** 1.6)
        d = Vector((math.sin(th) * cphi, math.sin(th) * sphi, math.cos(th)))
        n = wax.cross(d).normalized()
        s = wax.copy()
        if roll:
            s = (s * math.cos(roll) + n * math.sin(roll)).normalized()
            n = s.cross(d).normalized()
        fi = t * (len(_WPROF) - 1)
        i0 = min(int(fi), len(_WPROF) - 2)
        w = width * 0.5 * (_WPROF[i0] + (_WPROF[i0 + 1] - _WPROF[i0]) * (fi - i0))
        k = w * thick * 2
        ring = [bm.verts.new(p - s * w), bm.verts.new(p + n * k),
                bm.verts.new(p + s * w), bm.verts.new(p - n * k * 0.6)]
        rings.append(ring)
        allv += ring
        p = p + d * ds
    if cut is None:
        tip = bm.verts.new(p)
        allv.append(tip)
    for i in range(len(rings) - 1):
        r0, r1 = rings[i], rings[i + 1]
        for j in range(4):
            bm.faces.new((r0[j], r0[(j + 1) % 4], r1[(j + 1) % 4], r1[j]))
    bm.faces.new(list(reversed(rings[0])))
    if cut is None:
        r = rings[-1]
        for j in range(4):
            bm.faces.new((r[j], r[(j + 1) % 4], tip))
    else:
        bm.faces.new(rings[-1])
    _clamp(allv)
    return a._finish(allv, mat)


def seed_spike(a, base, phi, lean, stem_len, head_len=0.75, head_r=0.17, rng=None):
    b = Vector(base)
    pts = []
    for i in range(5):
        t = i / 4
        th = lean * (0.6 + 0.4 * t)
        d = Vector((math.sin(th) * math.cos(phi), math.sin(th) * math.sin(phi), math.cos(th)))
        pts.append(b + d * (stem_len * t))
    loft(a, pts, [0.05, 0.045, 0.042, 0.04, 0.038], STEM, sides=5)
    top = pts[-1]
    d = (pts[-1] - pts[-2]).normalized()
    hp = [top - d * 0.08 + d * (head_len * f) for f in (0.0, 0.12, 0.35, 0.6, 0.82, 1.0)]
    hr = [0.0, head_r * 0.7, head_r, head_r * 0.92, head_r * 0.55, 0.0]
    loft(a, hp, hr, BROWN, sides=6, jitter=0.12, rng=rng)


def root_base(a, scale=1.0, roots=6, rng=None, knot=True):
    s = scale
    if knot:
        loft(a, [(0, 0, 0), (0, 0, 0.3 * s), (0, 0, 0.6 * s)],
             [0.2 * s, 0.15 * s, 0.13 * s], BROWN, sides=7, jitter=0.08, rng=rng)
    for i in range(roots):
        ph = 2 * math.pi * i / roots + (rng.uniform(-0.3, 0.3) if rng else 0)
        L = (0.75 + (rng.uniform(-0.15, 0.2) if rng else 0)) * s
        c, sn = math.cos(ph), math.sin(ph)
        pts = [(0.05 * c * s, 0.05 * sn * s, 0.28 * s),
               (0.35 * L * c, 0.35 * L * sn, 0.12 * s),
               (0.7 * L * c, 0.7 * L * sn, 0.04 * s),
               (L * c, L * sn, 0.02 * s)]
        loft(a, pts, [0.09 * s, 0.065 * s, 0.04 * s, 0.0], BROWN, sides=4)


def fan(a, rng, n, length, lean_in, lean_out, droop, width, jitter_len=0.25, cut=None,
        hub=0.12):
    """Blades round a hub: inner ones upright, outer ones leaning and drooping."""
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        phi = i * golden + rng.uniform(-0.15, 0.15)
        n_in = max(3, n // 4)
        f = 0.0 if i < n_in else 0.3 + 0.7 * ((i * 0.618) % 1.0)  # inner .. outer
        lean = lean_in + (lean_out - lean_in) * f + rng.uniform(-0.08, 0.08)
        sz = (1.0, 0.82, 0.66)[(i * 7) % 3]
        if f == 0.0:
            sz = max(sz, 0.85)
        L = length * sz * (1 + rng.uniform(-jitter_len, jitter_len) * 0.5)
        r = hub * (0.4 + 0.6 * f)
        base = (r * math.cos(phi), r * math.sin(phi), 0.04)
        blade(a, base, phi, L, width * (0.85 + 0.15 * sz), lean, droop * f * f, cut=cut,
              roll=rng.uniform(-0.25, 0.25))


def _done(a):
    bmesh.ops.recalc_face_normals(a.bm, faces=a.bm.faces[:])
    return a.finish()


def build(kit):
    fk = kit.flintkit
    out = []
    note = "No sockets. Plant only (no water mesh)."

    # --- hero ---
    a = fk.Asset("FieldSedge", "V01 FieldSedge")
    rng = random.Random(21)
    root_base(a, 0.45, roots=5, rng=rng, knot=False)
    fan(a, rng, 18, 3.3, math.radians(12), math.radians(60), math.radians(40), 0.8)
    seed_spike(a, (0.12, 0.05, 0.05), math.radians(10), math.radians(9), 3.35, rng=rng)
    seed_spike(a, (-0.12, -0.05, 0.05), math.radians(190), math.radians(11), 3.15, rng=rng)
    out.append(kit.tag(_done(a), "hero", collision="none", budget=3000, notes=note))

    # --- parts ---
    a = fk.Asset("SedgeBladeLarge", "V01 FieldSedge")
    blade(a, (0, 0, 0), 0.0, 3.5, 0.6, math.radians(2), math.radians(3))
    out.append(kit.tag(_done(a), "part", collision="none", budget=1500, notes=note))

    a = fk.Asset("SedgeBladeMedium", "V01 FieldSedge")
    blade(a, (0, 0, 0), 0.0, 2.6, 0.52, math.radians(4), math.radians(22))
    out.append(kit.tag(_done(a), "part", collision="none", budget=1500, notes=note))

    a = fk.Asset("SedgeBladeSmall", "V01 FieldSedge")
    blade(a, (0, 0, 0), 0.0, 1.8, 0.42, math.radians(25), math.radians(35))
    out.append(kit.tag(_done(a), "part", collision="none", budget=1500, notes=note))

    a = fk.Asset("SedgeSeedSpike", "V01 FieldSedge")
    seed_spike(a, (0, 0, 0), 0.0, math.radians(6), 2.5, head_len=0.8, head_r=0.2,
               rng=random.Random(4))
    out.append(kit.tag(_done(a), "part", collision="none", budget=1500, notes=note))

    a = fk.Asset("SedgeRootBase", "V01 FieldSedge")
    root_base(a, 1.0, roots=6, rng=random.Random(9))
    out.append(kit.tag(_done(a), "part", collision="none", budget=1500, notes=note))

    # --- variations ---
    a = fk.Asset("SedgeShortFan", "V01 FieldSedge")
    rng = random.Random(33)
    root_base(a, 0.35, roots=4, rng=rng, knot=False)
    fan(a, rng, 12, 2.0, math.radians(14), math.radians(62), math.radians(30), 0.6)
    out.append(kit.tag(_done(a), "variant", collision="none", budget=3000,
                       notes="A. Short Fan. " + note))

    a = fk.Asset("SedgeTallArchingFan", "V01 FieldSedge")
    rng = random.Random(44)
    root_base(a, 0.5, roots=5, rng=rng, knot=False)
    fan(a, rng, 18, 3.8, math.radians(14), math.radians(52), math.radians(70), 0.8)
    seed_spike(a, (0.12, 0.05, 0.05), math.radians(15), math.radians(8), 3.7, rng=rng)
    seed_spike(a, (-0.12, -0.05, 0.05), math.radians(195), math.radians(10), 3.5, rng=rng)
    out.append(kit.tag(_done(a), "variant", collision="none", budget=3000,
                       notes="B. Tall Arching Fan. " + note))

    a = fk.Asset("SedgeCutTuft", "V01 FieldSedge")
    rng = random.Random(55)
    root_base(a, 0.3, roots=4, rng=rng, knot=False)
    fan(a, rng, 14, 1.5, math.radians(14), math.radians(58), math.radians(10), 0.26, cut=0.66,
        hub=0.2)
    out.append(kit.tag(_done(a), "depleted", collision="none", budget=2000,
                       notes="C. Cut Tuft: clipped blunt blades. " + note))
    return out
