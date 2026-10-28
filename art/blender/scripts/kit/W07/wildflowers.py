"""W07 row 3 - Wildflowers: purple bells, blue stars, pink blooms over broad leaves."""
import math

from mathutils import Matrix, Vector

SUBJECT = "Wildflowers"
ROW = 3
HERO_AZIMUTH = -22
PALETTE = {
    "w07_leaf": ("#4E9A2C", 0.9, 0, 0),
    "w07_petal_purple": ("#8E5AD8", 0.85, 0, 0),
    "w07_petal_blue": ("#4A62E0", 0.85, 0, 0),
    "w07_petal_pink": ("#F48FB1", 0.85, 0, 0),
    "w07_petal_white": ("#F2EAD2", 0.85, 0, 0),
    "w07_wood": ("#7A4A2A", 0.95, 0, 0),
    "w07_stone": ("#8E8E94", 0.95, 0, 0),
    "w07_root": ("#B8672A", 0.9, 0, 0),
}

LEAF, STEM = "w07_leaf", "w07_leaf"
TAU = 2 * math.pi


# -- low-level helpers ------------------------------------------------------

def _frame(loc, direction=(0, 0, 1), track="Z"):
    """Matrix placing local `track` axis along `direction`, origin at loc."""
    d = Vector(direction).normalized()
    q = d.to_track_quat(track, "Y")
    return Matrix.Translation(Vector(loc)) @ q.to_matrix().to_4x4()


def _place(a, verts, M):
    for v in verts:
        v.co = M @ v.co
        if v.co.z < 0:
            v.co.z = 0.0
    return verts


def _mesh(a, pts, faces, mat, M):
    bm = a.bm
    vs = [bm.verts.new(M @ Vector(p)) for p in pts]
    for v in vs:
        if v.co.z < 0:
            v.co.z = 0.0
    for f in faces:
        bm.faces.new([vs[i] for i in f])
    return a._finish(vs, mat)


def _lathe(a, profile, n, M, mat, mod=None, phase=0.0):
    """Revolve (r, z) profile (r=0 entries are poles). mod(k, theta) -> (rscale, dz)."""
    pts, idx = [], []
    for k, (r, z) in enumerate(profile):
        if r <= 1e-6:
            idx.append(len(pts))
            pts.append((0.0, 0.0, z))
            continue
        ring = []
        for j in range(n):
            th = phase + TAU * j / n
            rs, dz = mod(k, th) if mod else (1.0, 0.0)
            ring.append(len(pts))
            pts.append((r * rs * math.cos(th), r * rs * math.sin(th), z + dz))
        idx.append(ring)
    faces = []
    for k in range(len(idx) - 1):
        U, L = idx[k], idx[k + 1]
        for j in range(n):
            j2 = (j + 1) % n
            if isinstance(U, int):
                faces.append((U, L[j], L[j2]))
            elif isinstance(L, int):
                faces.append((U[j], L, U[j2]))
            else:
                faces.append((U[j], L[j], L[j2], U[j2]))
    return _mesh(a, pts, faces, mat, M)


# -- organic parts ------------------------------------------------------------

def leaf(a, base, phi, pitch, L=1.8, W=1.0, droop=0.22, fold=0.42, th=0.13, roll=0.0):
    """Broad pointed leaf with a central crease; points along compass angle phi
    (radians from +X), tip raised by pitch (radians)."""
    ts = [0.0, 0.10, 0.26, 0.44, 0.60, 0.75, 0.89, 1.0]
    ws = [0.0, 0.62, 0.93, 1.0, 0.92, 0.70, 0.38, 0.0]
    N = len(ts)

    def zc(t):
        return -droop * t * t

    pts = []
    T = [len(pts) + i for i in range(N)]
    for t in ts:
        pts.append((0.0, t * L, zc(t)))
    R, Lf, B = {}, {}, {}
    for i in range(1, N - 1):
        t, w = ts[i], ws[i] * W / 2
        R[i] = len(pts); pts.append((w, t * L, zc(t) + fold * ws[i] * W * 0.5))
        Lf[i] = len(pts); pts.append((-w, t * L, zc(t) + fold * ws[i] * W * 0.5))
        B[i] = len(pts); pts.append((0.0, t * L, zc(t) - th))
    B[0], B[N - 1] = T[0], T[N - 1]
    f = []
    for mid, rev in ((T, False), (B, True)):
        tri = [(mid[0], R[1], mid[1]), (mid[N - 2], R[N - 2], mid[N - 1]),
               (mid[0], mid[1], Lf[1]), (mid[N - 2], mid[N - 1], Lf[N - 2])]
        for i in range(1, N - 2):
            tri.append((mid[i], R[i], R[i + 1], mid[i + 1]))
            tri.append((mid[i], mid[i + 1], Lf[i + 1], Lf[i]))
        f += [tuple(reversed(x)) for x in tri] if rev else tri
    M = (Matrix.Translation(Vector(base)) @ Matrix.Rotation(phi - math.pi / 2, 4, "Z")
         @ Matrix.Rotation(pitch, 4, "X") @ Matrix.Rotation(roll, 4, "Y"))
    return _mesh(a, pts, f, LEAF, M)


def stem(a, pts, r=0.13):
    return a.tube_loop(pts, r, mat=STEM, rseg=6, closed=False)


def bell(a, top, hang=(0, 0, -1), s=1.0, mat="w07_petal_purple"):
    """Hanging bell: top (calyx) at `top`, mouth along `hang`. ~1.2 wide x 1.4 tall at s=1."""
    prof = [(0.0, 0.04), (0.17, 0.0), (0.36, -0.14), (0.44, -0.48), (0.46, -0.84),
            (0.52, -1.14), (0.62, -1.40), (0.40, -1.10), (0.0, -0.62)]
    prof = [(r * s, z * s) for r, z in prof]

    def mod(k, th):
        if k == 6:   # flared rim: 6 lobe tips, 6 notches
            c = math.cos(6 * th)
            return (0.9 + 0.1 * c, s * (-0.06 * c + 0.06))
        if k == 5:
            return (1.0 + 0.04 * math.cos(6 * th), 0.0)
        return (1.0, 0.0)

    M = _frame(top, [-x for x in hang], "Z")   # local +Z points away from mouth
    _lathe(a, prof, 12, M, mat, mod)
    cv = a.cyl(0.24 * s, 0.09 * s, 0.22 * s, sides=6, mat=LEAF)
    _place(a, a.transform(cv, (0, 0, -0.1 * s)), M)


def star(a, loc, face=(0, 0, 1), s=1.0):
    """Flat 5-point star ~1.2 across with a pale centre, facing `face`."""
    pts = [(0, 0, 0.13 * s), (0, 0, -0.1 * s)]
    for j in range(10):
        th = TAU * j / 10 + math.pi / 2
        r, z = (0.64, 0.12) if j % 2 == 0 else (0.36, 0.02)
        pts.append((r * s * math.cos(th), r * s * math.sin(th), z * s))
    f = []
    for j in range(10):
        a1, a2 = 2 + j, 2 + (j + 1) % 10
        f.append((a1, a2, 0))
        f.append((a2, a1, 1))
    M = _frame(loc, face)
    _mesh(a, pts, f, "w07_petal_blue", M)
    c = a.cyl(0.14 * s, 0.09 * s, 0.1 * s, sides=6, mat="w07_petal_white")
    _place(a, a.transform(c, (0, 0, 0.05 * s)), M)
    k = a.cyl(0.05 * s, 0.17 * s, 0.16 * s, sides=5, mat=LEAF)
    _place(a, a.transform(k, (0, 0, -0.22 * s)), M)


def bloom(a, loc, face=(0, 0, 1), s=1.0):
    """Deep rounded pink cup: 5 petals curling up and in, ~1.2 across, pale centre."""
    prof = [(0.0, 0.24), (0.30, 0.30), (0.56, 0.48), (0.72, 0.72), (0.68, 0.48),
            (0.50, 0.20), (0.22, 0.02), (0.0, -0.04)]
    prof = [(r * s, z * s) for r, z in prof]

    def mod(k, th):
        if k in (2, 3, 4):
            c = math.cos(5 * th)
            rs = 0.8 + 0.2 * math.sqrt(abs(math.cos(2.5 * th)))
            return (rs, s * 0.12 * c if k == 3 else 0.0)
        return (1.0, 0.0)

    M = _frame(loc, face)
    _lathe(a, prof, 20, M, "w07_petal_pink", mod, phase=math.pi / 2)
    c = a.cyl(0.2 * s, 0.13 * s, 0.14 * s, sides=6, mat="w07_petal_white")
    _place(a, a.transform(c, (0, 0, 0.3 * s)), M)
    k = a.cyl(0.08 * s, 0.24 * s, 0.18 * s, sides=5, mat=LEAF)
    _place(a, a.transform(k, (0, 0, -0.1 * s)), M)


def bud(a, loc, face=(0, 0, 1), s=1.0):
    """Closed cup-shaped pink bud, ~0.8 tall."""
    prof = [(0.0, 0.62), (0.22, 0.80), (0.35, 0.46), (0.30, 0.16), (0.12, 0.0), (0.0, -0.06)]
    prof = [(r * s, z * s) for r, z in prof]

    def mod(k, th):
        if k == 1:
            c = math.cos(5 * th)
            return (1.0 + 0.15 * c, s * 0.08 * c)
        return (1.0, 0.0)

    M = _frame(loc, face)
    _lathe(a, prof, 10, M, "w07_petal_pink", mod, phase=math.pi / 2)
    k = a.cyl(0.06 * s, 0.2 * s, 0.2 * s, sides=5, mat=LEAF)
    _place(a, a.transform(k, (0, 0, -0.12 * s)), M)


def rosette(a, specs, z=0.06, k=1.0, kw=1.0, droop=0.08, fold=0.42):
    """specs: (angle_deg, length, width, pitch_deg, r_offset, roll_deg)."""
    for ang, L, W, p, ro, rl in specs:
        phi = math.radians(ang)
        leaf(a, (ro * math.cos(phi), ro * math.sin(phi), z), phi, math.radians(p), L * k, W * k * kw,
             droop=droop * L * k, fold=fold, roll=math.radians(rl))


# -- assets -------------------------------------------------------------------

# 6 separate leaves splayed 30-45 deg, each rolled differently, gaps between them
VAR_LEAVES = [(-120, 1.95, 1.35, 30, 0.12, 6), (-60, 1.95, 1.35, 30, 0.12, -6),
              (-170, 1.95, 1.3, 38, 0.12, -20), (-10, 1.95, 1.3, 38, 0.12, 20),
              (60, 1.85, 1.25, 50, 0.1, 12), (120, 1.85, 1.25, 50, 0.1, -12)]

def _hero(kit):
    fk = kit.flintkit
    a = fk.Asset("Wildflowers", "W07 Wildflowers")
    # dense base: 7 big splayed leaves in an outer ring + 3 steeper inner leaves,
    # each with its own yaw / pitch / roll so tips and gaps show in the silhouette
    # front leaves low and arching (top faces toward the viewer), side leaves rolled
    # toward the front, back leaves standing up behind the stems
    rosette(a, [(-125, 2.3, 1.7, 22, 0.3, 6), (-88, 2.4, 1.8, 18, 0.3, -6),
                (-50, 2.3, 1.7, 24, 0.3, 8), (-165, 2.4, 1.7, 32, 0.3, -20),
                (-15, 2.4, 1.7, 32, 0.3, 20), (25, 2.3, 1.6, 42, 0.3, 18),
                (160, 2.3, 1.6, 42, 0.3, -18), (60, 2.2, 1.6, 55, 0.25, 10),
                (115, 2.2, 1.6, 55, 0.25, -10), (88, 1.8, 1.3, 70, 0.1, 0)],
            droop=0.17, fold=0.32)
    # big purple bell: long stem arching over to the top-left
    stem(a, [(-0.3, 0.1, 0), (-0.4, 0.05, 2.0), (-0.55, 0.0, 3.8), (-0.75, 0.0, 4.75),
             (-1.15, -0.05, 4.85), (-1.45, -0.1, 4.5)], r=0.16)
    bell(a, (-1.45, -0.1, 4.5), (-0.25, -0.1, -1), s=1.1)
    # small purple bell centre-left on a short crook
    stem(a, [(-0.15, 0.0, 0), (-0.2, -0.05, 1.8), (-0.35, -0.15, 2.95), (-0.55, -0.25, 3.0),
             (-0.65, -0.3, 2.8)], r=0.13)
    bell(a, (-0.65, -0.3, 2.8), (-0.15, -0.1, -1), s=0.62)
    # blue star, highest, upper right, tilted toward the camera
    stem(a, [(0.3, 0.1, 0), (0.45, 0.05, 2.0), (0.6, 0.0, 3.6), (0.95, -0.1, 4.6)], r=0.15)
    star(a, (0.98, -0.14, 4.68), (0.2, -0.7, 0.85), s=1.3)
    # deep pink cup bloom in the centre (raised) and a second, lower on the right
    stem(a, [(0.0, -0.15, 0), (0.08, -0.25, 1.7), (0.0, -0.4, 3.0)], r=0.15)
    bloom(a, (0.0, -0.42, 3.0), (0.0, -0.7, 1), s=0.9)
    stem(a, [(0.5, -0.2, 0), (0.85, -0.35, 1.3), (1.25, -0.55, 2.15), (1.4, -0.65, 2.35)], r=0.15)
    bloom(a, (1.42, -0.68, 2.35), (0.4, -0.7, 1), s=0.92)
    # small grey stone and orange-brown soil chip tucked under the front leaf tips
    a.rock((0.75, 0.6, 0.5), loc=(-0.95, -1.15, 0), mat="w07_stone", subdiv=1)
    a.rock((0.5, 0.4, 0.32), loc=(1.0, -1.0, 0), mat="w07_root", subdiv=1)
    o = a.finish()
    return kit.tag(o, "hero", collision="none", budget=2000,
                   notes="Mixed wildflower cluster: purple bells, blue star, two pink cups over broad leaves; walk-through scatter, no VFX")


def _stem_part(kit):
    a = kit.flintkit.Asset("WildflowerStem", "W07 Wildflowers")
    stem(a, [(0, 0, 0), (0.04, 0, 1.4), (0.3, 0, 1.95), (0.36, 0, 3.0)], r=0.09)
    return kit.tag(a.finish(), "part", collision="none", budget=100, notes="Kinked 6-sided flower stalk")


def _head_part(kit):
    a = kit.flintkit.Asset("WildflowerFlowerHead", "W07 Wildflowers")
    bell(a, (0, 0, 1.45), (0, 0, -1), s=1.0)
    return kit.tag(a.finish(), "part", collision="none", budget=350,
                   notes="Purple bell head with 6 flared lobes and green calyx")


def _leaf_part(kit):
    a = kit.flintkit.Asset("WildflowerLeaf", "W07 Wildflowers")
    leaf(a, (0, 0, 0.02), math.pi / 2, math.radians(70), L=1.85, W=1.05, droop=0.12)
    return kit.tag(a.finish(), "part", collision="none", budget=150, notes="Broad creased leaf")


def _purple(kit):
    a = kit.flintkit.Asset("PurpleBell", "W07 Wildflowers")
    rosette(a, VAR_LEAVES, droop=0.14, fold=0.32)
    stem(a, [(0, 0, 0), (0.06, 0, 1.5), (0.0, 0, 2.8), (-0.22, 0, 3.45), (-0.55, 0, 3.5),
             (-0.75, -0.05, 3.3)])
    bell(a, (-0.75, -0.05, 3.3), (-0.2, -0.1, -1), s=0.8)
    stem(a, [(0.03, 0, 2.2), (0.3, 0, 2.85), (0.55, 0, 3.05), (0.75, -0.05, 2.9)], r=0.11)
    bell(a, (0.75, -0.05, 2.9), (0.2, -0.1, -1), s=0.72)
    stem(a, [(0.02, 0, 1.5), (-0.3, 0, 2.0), (-0.5, -0.05, 2.15), (-0.62, -0.05, 2.0)], r=0.1)
    bell(a, (-0.62, -0.05, 2.0), (-0.2, -0.1, -1), s=0.5)
    return kit.tag(a.finish(), "variant", collision="none", budget=1200,
                   notes="Purple Bell: 3 drooping bells on arched stems")


def _blue(kit):
    a = kit.flintkit.Asset("BlueStar", "W07 Wildflowers")
    rosette(a, VAR_LEAVES, droop=0.14, fold=0.32)
    stem(a, [(0, 0.05, 0), (0.1, 0.05, 1.6), (-0.02, 0.0, 2.7), (0.05, 0, 3.55)])
    star(a, (0.05, -0.02, 3.6), (0.0, -0.45, 1), s=1.1)
    stem(a, [(-0.15, 0.05, 0), (-0.45, 0.0, 1.5), (-0.7, 0.0, 2.3), (-0.95, -0.02, 2.95)], r=0.11)
    star(a, (-0.97, -0.04, 3.0), (-0.45, -0.45, 1), s=1.0)
    stem(a, [(0.15, 0.05, 0), (0.45, 0.0, 1.4), (0.75, 0.0, 2.4), (0.95, -0.02, 3.15)], r=0.11)
    star(a, (0.97, -0.04, 3.2), (0.45, -0.45, 1), s=1.05)
    leaf(a, (0.08, 0.0, 1.2), math.radians(20), math.radians(40), 0.9, 0.5, droop=0.1)
    leaf(a, (-0.35, 0.0, 1.2), math.radians(160), math.radians(40), 0.9, 0.5, droop=0.1)
    return kit.tag(a.finish(), "variant", collision="none", budget=1200,
                   notes="Blue Star: 3 five-point stars with pale centres")


def _pink(kit):
    a = kit.flintkit.Asset("PinkBloom", "W07 Wildflowers")
    rosette(a, VAR_LEAVES, droop=0.14, fold=0.32)
    stem(a, [(0, 0.05, 0), (0.08, 0.05, 1.5), (-0.02, 0, 2.6), (0.02, -0.05, 3.2)])
    bloom(a, (0.02, -0.08, 3.2), (0.0, -0.6, 1), s=1.1)
    stem(a, [(-0.1, 0.05, 0), (-0.35, 0, 1.3), (-0.6, -0.05, 2.0), (-0.8, -0.1, 2.35)], r=0.11)
    bloom(a, (-0.82, -0.12, 2.35), (-0.6, -0.6, 0.8), s=0.75)
    stem(a, [(0.1, 0.05, 0), (0.4, 0, 1.2), (0.62, -0.03, 1.9)], r=0.11)
    bud(a, (0.62, -0.05, 1.9), (0.3, -0.2, 1), s=0.85)
    leaf(a, (0.05, 0.0, 1.3), math.radians(15), math.radians(40), 0.9, 0.5, droop=0.1)
    leaf(a, (-0.3, 0.0, 1.1), math.radians(165), math.radians(40), 0.9, 0.5, droop=0.1)
    return kit.tag(a.finish(), "variant", collision="none", budget=1200,
                   notes="Pink Bloom: 2 open blooms and a closed bud")


def build(kit):
    return [_hero(kit), _stem_part(kit), _head_part(kit), _leaf_part(kit),
            _purple(kit), _blue(kit), _pink(kit)]
