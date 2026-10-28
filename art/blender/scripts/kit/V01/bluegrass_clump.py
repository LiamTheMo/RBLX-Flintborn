"""V01 row 3: Bluegrass Clump - arching folded (V-section) blades with tan seedheads."""
import math
import random

import bmesh
from mathutils import Vector

SUBJECT = "BluegrassClump"
ROW = 3
HERO_AZIMUTH = -22

PALETTE = {
    "v01_blue_blade": ("#1F8A52", 0.85, 0, 0),  # Bluegrass blades (cool teal-green)
    "v01_stem": ("#4C9230", 0.85, 0, 0),  # Stems/stalks/joints
    "v01_seedhead_tan": ("#D0AC70", 0.85, 0, 0),  # Bluegrass seedheads
    "v01_brown": ("#8A5530", 0.9, 0, 0),  # Root bases
    "v01_dry_grass": ("#C9A035", 0.9, 0, 0),  # Bluegrass Dry Late Growth blades
}

BLADE = "v01_blue_blade"
STEM = "v01_stem"
HEAD = "v01_seedhead_tan"
ROOT = "v01_brown"
DRY = "v01_dry_grass"


def _clamp(verts, zmin=0.0):
    for v in verts:
        if v.co.z < zmin:
            v.co.z = zmin
    return verts


def blade(a, base, phi, L, W, theta0, k, mat, segs=6, fold=0.32, rag=0.0, rng=None):
    """Folded V-section blade. phi = azimuth (rad), theta0 = start elevation (rad),
    k = droop (rad per stud). Closed thin chevron section, pointed tip."""
    bm = a.bm
    rng = rng or a.rng
    d_h = Vector((math.cos(phi), math.sin(phi), 0.0))
    side = Vector((-math.sin(phi), math.cos(phi), 0.0))
    p = Vector(base)
    ds = L / segs
    theta = theta0
    rings = []
    tip = None
    thick = 0.035
    for i in range(segs + 1):
        t = i / segs
        d = d_h * math.cos(theta) + Vector((0, 0, math.sin(theta)))
        n = side.cross(d).normalized()
        if n.z < 0:
            n = -n
        if i == segs:
            tip = bm.verts.new(p.copy())
            break
        # width profile: base 0.55W, widest ~35%, taper to point
        if t < 0.45:
            w = W * (0.5 + 0.5 * t / 0.45)
        else:
            w = W * (1.0 - (t - 0.45) / 0.55) ** 0.7
        w = max(w, 0.02)
        if rag:
            w *= 1.0 + rng.uniform(-rag, rag)
        sv = side * (w / 2)
        up = n * (fold * w)
        L_ = bm.verts.new(p + sv + up)
        T_ = bm.verts.new(p.copy())
        R_ = bm.verts.new(p - sv + up)
        B_ = bm.verts.new(p - n * thick)
        rings.append((L_, T_, R_, B_))
        p = p + d * ds
        theta -= k * ds
        if rag:
            theta += rng.uniform(-rag, rag) * 0.5
            p += side * rng.uniform(-rag, rag) * 0.15
    faces = []
    for i in range(len(rings) - 1):
        r1, r2 = rings[i], rings[i + 1]
        for j in range(4):
            faces.append(bm.faces.new((r1[j], r1[(j + 1) % 4], r2[(j + 1) % 4], r2[j])))
    last = rings[-1]
    for j in range(4):
        faces.append(bm.faces.new((last[j], last[(j + 1) % 4], tip)))
    faces.append(bm.faces.new(tuple(reversed(rings[0]))))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    verts = [v for r in rings for v in r] + [tip]
    _clamp(verts, 0.0)
    return a._finish(verts, mat)


def _rot_to(d):
    return Vector((0, 0, 1)).rotation_difference(Vector(d).normalized()).to_euler("XYZ")


def ear(a, loc, direction, length=1.05, width=0.6):
    """Faceted tan ear: spindle + spiral of layered scales."""
    verts = list(a.ico((width * 0.28, width * 0.28, length * 0.5), loc=(0, 0, length * 0.5),
                       mat=HEAD, subdiv=1))
    n = 9
    for i in range(n):
        t = (i + 0.5) / n
        z = length * (0.08 + 0.78 * t)
        prof = math.sin(math.pi * min(1.0, 0.25 + t * 0.9)) * 0.75 + 0.25
        s = a.ico((width * 0.34 * prof, width * 0.22 * prof, length * 0.17),
                  loc=(0, 0, 0), mat=HEAD, subdiv=1)
        a.transform(s, loc=(width * 0.17 * prof, 0, z), rot=(0, 0.45, 0))
        a.transform(s, rot=(0, 0, i * 2.4))
        verts += s
    # pointed tip
    verts += a.cyl(width * 0.12, 0.0, length * 0.22, sides=5, loc=(0, 0, length * 0.86), mat=HEAD)
    a.transform(verts, loc=loc, rot=_rot_to(direction))
    return verts


def seed_stalk(a, base, top, lean, head_len=0.9, bend=0.15):
    """Thin green stem from base up to `top` (z), leaning by vector `lean`, ear on top."""
    bx, by, bz = base
    pts = []
    n = 7
    for i in range(n + 1):
        t = i / n
        z = bz + (top - head_len - bz) * t
        off = t ** 1.6
        pts.append((bx + lean[0] * off + bend * math.sin(t * math.pi) * lean[1] * 0.0,
                    by + lean[1] * off, z))
    a.tube_loop(pts, 0.045, mat=STEM, rseg=5, closed=False)
    p1, p0 = Vector(pts[-1]), Vector(pts[-2])
    d = (p1 - p0).normalized()
    ear(a, tuple(p1 - d * 0.05), tuple(d), length=head_len)


def root_hub(a, r=0.35):
    v = a.ico((r, r, 0.14), loc=(0, 0, 0.12), mat=ROOT, subdiv=1)
    _clamp(v)
    for i in range(5):
        ang = i * 2 * math.pi / 5 + 0.4
        c, s = math.cos(ang), math.sin(ang)
        pts = [(c * r * 0.5, s * r * 0.5, 0.12), (c * r * 1.1, s * r * 1.1, 0.06),
               (c * r * 1.5, s * r * 1.5, 0.02)]
        _clamp(a.tube_loop(pts, 0.05, mat=ROOT, rseg=4, closed=False))


def clump(a, rng, n, len_rng, width, tall_frac, mat, spread=1.0, droop=1.0, upright=0.0,
          rag=0.0, front_blade=True):
    """n blades around the hub. tall_frac of them are inner upright blades."""
    golden = 2.39996
    for i in range(n):
        phi = i * golden + rng.uniform(-0.15, 0.15)
        inner = (i % 3 == 0) if tall_frac >= 0.33 else (rng.random() < tall_frac)
        L = rng.uniform(*len_rng)
        rb = rng.uniform(0.08, 0.35)
        base = (math.cos(phi) * rb, math.sin(phi) * rb, 0.05)
        if inner:
            th0 = math.radians(rng.uniform(78, 88) + upright * 0.3)
            k = rng.uniform(0.08, 0.18) * droop * (1 - upright * 0.02)
            L *= 0.92
        else:
            th0 = math.radians(min(86, rng.uniform(64, 80) / spread + upright * 0.5))
            k = rng.uniform(0.42, 0.58) * droop * (L / len_rng[1])
        W = width * rng.uniform(0.85, 1.15)
        blade(a, base, phi, L, W, th0, k, mat, rag=rag, rng=rng)
    if front_blade:
        L = len_rng[1] * 0.7
        blade(a, (0, -0.1, 0.05), -math.pi / 2 + 0.25, L, width * 1.5,
              math.radians(48 + upright * 0.5), 0.45 * droop, mat, rag=rag, rng=rng)


def make_clump(fk, name, label, seed, n, len_rng, width, stalks, mat=BLADE, **kw):
    a = fk.Asset(name, label, seed=seed)
    rng = random.Random(seed)
    root_hub(a)
    clump(a, rng, n, len_rng, width, 0.34, mat, **kw)
    for (lean, top) in stalks:
        seed_stalk(a, (lean[0] * 0.15, lean[1] * 0.15, 0.1), top, lean)
    return a.finish()


def build(kit):
    fk = kit.flintkit
    out = []
    NOTE = "Bluegrass: folded arching blades, tan seedheads. No sockets, no VFX."

    # HERO
    o = make_clump(fk, "BluegrassClump", "V01 BluegrassClump", 31, 27, (2.5, 3.8), 0.60,
                   [((-0.55, 0.15), 4.2), ((0.5, 0.25), 4.05)])
    out.append(kit.tag(o, "hero", collision="none", budget=3000, notes=NOTE))

    # PARTS
    a = fk.Asset("BluegrassLongBlade", "V01 BluegrassLongBlade", seed=5)
    blade(a, (0, 0, 0), 0.0, 3.8, 0.5, math.radians(84), 0.22, BLADE)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes=NOTE))

    a = fk.Asset("BluegrassShortBlade", "V01 BluegrassShortBlade", seed=6)
    blade(a, (0, 0, 0), 0.0, 2.4, 0.42, math.radians(80), 0.04, BLADE)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes=NOTE))

    a = fk.Asset("BluegrassSeedhead", "V01 BluegrassSeedhead", seed=7)
    pts = [(-0.45, 0, 0.02), (-0.15, 0, 0.45), (0.0, 0, 1.0), (0.1, 0, 1.6), (0.25, 0, 2.15)]
    a.tube_loop(pts, 0.05, mat=STEM, rseg=5, closed=False)
    ear(a, (0.23, 0, 2.1), (0.25, 0, 1.0), length=1.05, width=0.55)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes=NOTE))

    a = fk.Asset("BluegrassStem", "V01 BluegrassStem", seed=8)
    pts = [(0, 0, 0), (0, 0, 0.5), (0.05, 0, 0.95)]
    a.tube_loop(pts, 0.07, mat=STEM, rseg=6, closed=False)
    a.cyl(0.1, 0.1, 0.14, sides=6, loc=(0.05, 0, 0.92), rot=(0, 0.2, 0), mat=STEM)
    pts = [(0.07, 0, 1.0), (0.22, 0, 1.5), (0.32, 0, 2.0)]
    a.tube_loop(pts, 0.065, mat=STEM, rseg=6, closed=False)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes=NOTE))

    a = fk.Asset("BluegrassRootBase", "V01 BluegrassRootBase", seed=9)
    a.cyl(0.16, 0.11, 0.6, sides=6, loc=(0, 0, 0), mat=ROOT, jitter=0.01)
    for i in range(5):
        ang = i * 2 * math.pi / 5 + 0.3
        c, s = math.cos(ang), math.sin(ang)
        pts = [(c * 0.08, s * 0.08, 0.3), (c * 0.3, s * 0.3, 0.12), (c * 0.6, s * 0.6, 0.03),
               (c * 0.8, s * 0.8, 0.0)]
        _clamp(a.tube_loop(pts, 0.05, mat=ROOT, rseg=4, closed=False))
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes=NOTE))

    # VARIANTS
    o = make_clump(fk, "BluegrassCompact", "V01 BluegrassCompact", 41, 14, (1.6, 2.3), 0.48,
                   [((-0.35, 0.1), 2.8), ((0.35, 0.15), 2.7)])
    out.append(kit.tag(o, "variant", collision="none", budget=3000, notes=NOTE))

    o = make_clump(fk, "BluegrassWideSpread", "V01 BluegrassWideSpread", 51, 27, (2.6, 3.6),
                   0.55, [((-0.9, 0.1), 3.0), ((0.0, 0.3), 3.05), ((0.9, 0.1), 2.95)],
                   spread=1.5, droop=1.4)
    out.append(kit.tag(o, "variant", collision="none", budget=3000, notes=NOTE))

    o = make_clump(fk, "BluegrassDryLateGrowth", "V01 BluegrassDryLateGrowth", 61, 24,
                   (2.4, 3.4), 0.50, [((-0.45, 0.15), 3.9), ((0.45, 0.2), 3.8),
                                      ((0.05, -0.3), 3.6)],
                   mat=DRY, upright=14, droop=0.7, rag=0.12)
    out.append(kit.tag(o, "variant", collision="none", budget=3000, notes=NOTE))
    return out
