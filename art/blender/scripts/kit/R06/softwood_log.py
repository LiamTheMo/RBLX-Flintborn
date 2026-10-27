"""R06 row 1: SoftwoodLog resource node (hero, parts, drops, depleted stump)."""
import math

import bmesh
from mathutils import Matrix, Vector

SUBJECT = "SoftwoodLog"
ROW = 1
HERO_AZIMUTH = -20
SIDE_AZIMUTH = 54  # long side view with the +X ringed end seen obliquely at the right
HERO_YAW = 24      # degrees the whole hero is yawed so the -X ringed end faces the camera

PALETTE = {
    "r06_cutwood": ("#E0B27C", 0.85, 0, 0),
    "r06_softbark": ("#8A5B3E", 0.9, 0, 0),
    "r06_leaf": ("#3F9A2C", 0.7, 0, 0),
}

BARK, CUT, LEAF = "r06_softbark", "r06_cutwood", "r06_leaf"
CHIP_COLORS = ["#E0B27C", "#8A5B3E"]

# stepped end rings: (radius fraction, height above the end plane)
RINGS = [(0.88, 0.12), (0.68, 0.26), (0.48, 0.40), (0.27, 0.54)]


def _frame(d):
    d = d.normalized()
    u = d.orthogonal().normalized()
    return d, u, d.cross(u)


def loft(a, rings, mat, seg_mats=None, cap0=None, cap1=None):
    """Join rings (lists of points, same count) with quads. seg_mats maps segment
    index -> palette key; cap0/cap1 are palette keys (None = no cap)."""
    bm = a.bm
    rows = [[bm.verts.new(c) for c in ring] for ring in rings]
    n = len(rings[0])
    faces, segf = [], {}
    for i in range(len(rows) - 1):
        r0, r1 = rows[i], rows[i + 1]
        segf[i] = []
        for j in range(n):
            f = bm.faces.new((r0[j], r0[(j + 1) % n], r1[(j + 1) % n], r1[j]))
            faces.append(f)
            segf[i].append(f)
    caps = {}
    if cap0:
        caps[cap0] = caps.get(cap0, []) + [bm.faces.new(list(reversed(rows[0])))]
    if cap1:
        caps[cap1] = caps.get(cap1, []) + [bm.faces.new(rows[-1])]
    for fl in caps.values():
        faces += fl
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    verts = [v for r in rows for v in r]
    a._finish(verts, mat)
    for i, m in (seg_mats or {}).items():
        mi = a._mi(m)
        for f in segf[i]:
            f.material_index = mi
    for m, fl in caps.items():
        mi = a._mi(m)
        for f in fl:
            f.material_index = mi
    return verts


def rod(a, p1, p2, r1, r2, sides=9, segs=4, mat=BARK, cap0=BARK, cap1=CUT, jit=0.08,
        twist=None):
    """Faceted chiselled rod from p1 to p2 (radius r1 -> r2)."""
    p1, p2 = Vector(p1), Vector(p2)
    d, u, w = _frame(p2 - p1)
    L = (p2 - p1).length
    rng = a.rng
    tw = twist if twist is not None else rng.uniform(0, math.pi)
    rings = []
    for k in range(segs + 1):
        t = k / segs
        end = k in (0, segs)
        ax = 0.0 if end else rng.uniform(-0.25, 0.25) * L / segs
        c = p1 + d * (L * t + ax)
        r = r1 + (r2 - r1) * t
        ring = []
        for j in range(sides):
            ang = tw + 2 * math.pi * j / sides + (0 if end else rng.uniform(-0.12, 0.12))
            rr = r * (1 + rng.uniform(-jit, jit) * (0.4 if end else 1.0))
            ring.append(c + rr * (math.cos(ang) * u + math.sin(ang) * w))
        rings.append(ring)
    return loft(a, rings, mat, cap0=cap0, cap1=cap1)


def tuft(a, radius, loc, n=6, lift=(25, 50)):
    """Clump of n pointed faceted leaves fanning out and up from loc."""
    bm, rng = a.bm, a.rng
    loc = Vector(loc)
    verts = []
    spin = rng.uniform(0, math.tau)
    for i in range(n + 1):
        L = radius * rng.uniform(0.85, 1.1) * (0.8 if i == n else 1.0)
        w = 0.58 * L
        pts = [Vector(p) for p in ((0, 0, 0), (0.45 * L, w / 2, 0), (L, 0, 0),
                                   (0.45 * L, -w / 2, 0), (0.45 * L, 0, 0.13 * L))]
        e = math.radians(80 if i == n else rng.uniform(*lift))
        ang = spin + math.tau * i / n + rng.uniform(-0.2, 0.2)
        m = Matrix.Rotation(ang, 3, "Z") @ Matrix.Rotation(-e, 3, "Y")
        vs = [bm.verts.new(loc + m @ p + Vector((0, 0, 0.08))) for p in pts]
        b, l, t, r, c = vs
        fs = [bm.faces.new(q) for q in ((b, l, c), (l, t, c), (t, r, c), (r, b, c), (b, r, t, l))]
        bmesh.ops.recalc_face_normals(bm, faces=fs)
        verts += vs
    a._finish(verts, LEAF)
    return verts


def end_rings(a, centre, direction, R, rings=RINGS):
    """Stepped concentric octagon rings on a cut end (all cut wood)."""
    d = Vector(direction).normalized()
    rot = tuple(d.to_track_quat("Z", "Y").to_euler())
    for rf, h in rings:
        a.cyl(R * rf, R * rf * 0.72, h, sides=8, loc=tuple(centre), rot=rot, mat=CUT)


def flatten(a, z=0.0):
    for v in a.bm.verts:
        if v.co.z < z:
            v.co.z = z


def main_log(a, L=14.0, R=2.75, zc=2.6, nub=True):
    x0, x1 = -L / 2, L / 2
    rod(a, (x0, 0, zc), (x1, 0, zc), R, R * 0.96, sides=10, segs=7, cap0=BARK, cap1=BARK,
        jit=0.13, twist=0.2)
    end_rings(a, (x0, 0, zc), (-1, 0, 0), R * 0.97)
    end_rings(a, (x1, 0, zc), (1, 0, 0), R * 0.93)
    if nub:
        rod(a, (-3.4, 1.0, zc + 1.4), (-3.8, 1.5, zc + 3.4), 0.5, 0.42, sides=7, segs=1)


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---------------- HERO ----------------
    a = fk.Asset("SoftwoodLog", "R06 SoftwoodLog")
    main_log(a)
    # tall angled stub, top-back, leaning right
    rod(a, (-1.2, 0.6, 3.6), (1.3, 1.3, 7.9), 0.98, 0.86, sides=8, segs=2)
    end_rings(a, Vector((1.3, 1.3, 7.9)), Vector((2.5, 0.7, 4.3)), 0.84,
              rings=[(0.6, 0.06)])
    # short stub, front-bottom, poking toward the viewer and down
    rod(a, (-1.8, -1.2, 1.8), (-0.2, -4.9, 0.78), 0.8, 0.72, sides=8, segs=2)
    flatten(a)
    leaves = [(3.0, (-5.2, -3.2, 0.0)), (3.0, (5.3, -2.7, 0.0)), (2.6, (4.3, 0.6, 4.8)),
              (2.6, (6.3, 2.8, 0.0))]
    for r, loc in leaves:
        tuft(a, r, loc)
    yaw = Matrix.Rotation(math.radians(HERO_YAW), 3, "Z")
    bmesh.ops.rotate(a.bm, verts=list(a.bm.verts), cent=(0, 0, 0), matrix=yaw)
    flatten(a)
    xs = [v.co.x for v in a.bm.verts]
    ys = [v.co.y for v in a.bm.verts]
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, 0))
    hit = yaw @ Vector((-7.3, 0, 2.7)) - off
    o = a.finish()
    vfx.add(o, "harvest_hit", tuple(hit), color=CHIP_COLORS)
    vfx.add(o, "harvest_deplete", (0, 0, 0.5), color=CHIP_COLORS)
    out.append(kit.tag(o, "hero", collision="hull", budget=4000,
                       notes="harvest_hit: wood chips on the pale -X cut end (strike face); "
                             "harvest_deplete: bark/chip burst at base centre"))

    # ---------------- PARTS ----------------
    a = fk.Asset("SoftwoodLogMain", "R06 SoftwoodLog main log")
    main_log(a)
    flatten(a)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="bare main log, both ends cut with rings"))

    a = fk.Asset("SoftwoodLogBranchStub", "R06 SoftwoodLog branch stub")
    rod(a, (0, 0, -0.5), (1.1, -0.4, 2.7), 0.72, 0.62, sides=8, segs=2)
    end_rings(a, Vector((1.1, -0.4, 2.7)), Vector((1.1, -0.4, 3.2)), 0.6, rings=[(0.6, 0.06)])
    flatten(a)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500,
                       notes="angled branch stub, pale cut tip, angled flat base"))

    a = fk.Asset("SoftwoodLogCutEnd", "R06 SoftwoodLog cut-end insert")
    R = 2.98  # 5.5 across the flats
    rot = (-math.pi / 2, 0, 0)  # disc face toward -Y
    a.cyl(R, R, 0.4, sides=8, loc=(0, 0.2, 0), rot=rot, mat=CUT, twist=math.pi / 8)
    for rf, h in [(0.8, 0.1), (0.6, 0.21), (0.4, 0.32), (0.2, 0.43)]:
        a.cyl(R * rf, R * rf * 0.82, h, sides=8, loc=(0, -0.2, 0), rot=rot, mat=CUT,
              twist=math.pi / 8)
    bmesh.ops.translate(a.bm, verts=list(a.bm.verts), vec=(0, 0, R * math.cos(math.pi / 8)))
    flatten(a)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="octagonal cut-end insert disc with stepped rings"))

    # ---------------- DROPS ----------------
    a = fk.Asset("SoftwoodLogWoodWedge", "R06 SoftwoodLog wood wedge")
    # split-firewood wedge: wide base, two split faces narrowing to a bark-strip top
    v = a.poly_prism([(-0.75, 0.0), (0.75, 0.0), (0.14, 1.4), (-0.14, 1.4)], 2.5, mat=CUT)
    for vv in v:
        x, y, z = vv.co
        vv.co = Vector((z - 1.25, x, y))
    bi = a._mi(BARK)
    for f in {f for vv in v for f in vv.link_faces}:
        f.normal_update()
        if f.normal.z > 0.9 and f.calc_center_median().z > 1.0:
            f.material_index = bi
    bmesh.ops.rotate(a.bm, verts=v, cent=(0, 0, 0),
                     matrix=Matrix.Rotation(math.radians(30), 3, "Z"))
    out.append(kit.tag(a.finish(), "drop", collision="none", budget=300,
                       notes="split firewood wedge, bark back face"))

    a = fk.Asset("SoftwoodLogBranchStick", "R06 SoftwoodLog branch sticks")
    rod(a, (-1.35, -0.9, 0.32), (1.35, 0.9, 0.32), 0.32, 0.27, sides=6, segs=2, cap0=CUT)
    rod(a, (-1.25, 1.0, 0.55), (1.35, -0.85, 0.8), 0.3, 0.25, sides=6, segs=2, cap0=CUT)
    flatten(a)
    out.append(kit.tag(a.finish(), "drop", collision="none", budget=300,
                       notes="two crossed branch sticks"))

    # ---------------- DEPLETED ----------------
    a = fk.Asset("SoftwoodLogStump", "R06 SoftwoodLog stump")
    n = 9
    tops = [2.5, 1.75, 1.85, 1.7, 2.15, 1.75, 1.7, 2.3, 1.8]
    rings = []
    for z, r, jag in [(0.0, 1.9, None), (0.55, 1.5, None), (None, 1.4, tops),
                      (None, 0.9, [1.62 + 0.1 * ((j * 7) % 3) for j in range(n)])]:
        ring = []
        for j in range(n):
            ang = 2 * math.pi * j / n
            rr = r * (1 + a.rng.uniform(-0.06, 0.06))
            zz = jag[j] if jag else z
            ring.append(Vector((rr * math.cos(ang), rr * math.sin(ang), zz)))
        rings.append(ring)
    loft(a, rings, BARK, seg_mats={2: CUT}, cap0=BARK, cap1=CUT)
    for loc in [(-1.5, -1.0, 0.0), (1.5, -0.5, 0.0)]:
        tuft(a, 1.05, loc, n=6)
    flatten(a)
    o = a.finish()
    o["kit_shading_ok"] = "pale r06_cutwood splintered top is a real material change (cut heartwood), not lighting"
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="broken stump left after harvest"))
    return out
