"""V02 row 4: Rosehip Scrub - low sprawling thorny shrub with orange rosehips."""
import math
import random

from mathutils import Vector

SUBJECT = "RosehipScrub"
ROW = 4
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 135

PALETTE = {
    "v02_bark": ("#7B4A28", 0.9, 0, 0),
    "v02_rosehip_leaf": ("#5D8A2C", 0.8, 0, 0),
    "v02_rosehip": ("#EE5A14", 0.5, 0, 0),
}

BARK, LEAF, HIP = "v02_bark", "v02_rosehip_leaf", "v02_rosehip"


# ---------------------------------------------------------------- helpers

def _rot_z(d):
    """Euler that maps local +Z onto direction d."""
    return Vector(d).normalized().to_track_quat("Z", "Y").to_euler()


def seg(a, p1, p2, r1, r2, sides=6, ext=0.0):
    """Stem segment from p1 to p2 (tapering r1->r2), extended back by ext to hide joints."""
    p1, p2 = Vector(p1), Vector(p2)
    d = (p2 - p1).normalized()
    s = p1 - d * ext
    if s.z < 0.02:
        s = p1
    return a.cyl(r1, r2, (p2 - s).length, sides, loc=s, rot=_rot_z(d), mat=BARK)


def thorn(a, base, d, size=0.28):
    """Tiny triangular cone thorn pointing along d."""
    return a.cyl(size * 0.32, 0.0, size, 3, loc=base, rot=_rot_z(d), mat=BARK)


def leaf(a, base, d, length=1.6, width=0.72, fold=0.09, th=0.05):
    """Pointed leaf with raised midrib, a closed thin lens. Local Y = along leaf, Z = up."""
    bm = a.bm
    l, w = length, width * 0.5
    b = bm.verts.new((0, 0, 0))
    L = bm.verts.new((-w, 0.42 * l, 0))
    R = bm.verts.new((w, 0.42 * l, 0))
    t = bm.verts.new((0, l, 0))
    m = bm.verts.new((0, 0.45 * l, fold))
    mb = bm.verts.new((0, 0.45 * l, fold - th))
    for f in ((b, R, m), (b, m, L), (m, R, t), (m, t, L),
              (b, mb, R), (b, L, mb), (mb, t, R), (mb, L, t)):
        bm.faces.new(f)
    vs = [b, L, R, t, m, mb]
    d = Vector(d).normalized()
    a.transform(vs, base, d.to_track_quat("Y", "Z").to_euler())
    return a._finish(vs, LEAF)


def leaf_cluster3(a, base, d, length=1.6, spread=0.9, stalk=0.5):
    """Short stalk then three pointed leaves fanning out along d."""
    d = Vector(d).normalized()
    tip = Vector(base) + d * stalk
    seg(a, base, tip, 0.07, 0.05, 4)
    side = Vector((-d.y, d.x, 0))
    if side.length < 1e-3:
        side = Vector((1, 0, 0))
    side.normalize()
    leaf(a, tip, d, length)
    for s in (-1, 1):
        dd = (d + side * s * spread + Vector((0, 0, -0.15))).normalized()
        leaf(a, tip, dd, length * 0.85)


def rosehip(a, base, d, length=1.0, width=None, stalk=0.15):
    width = width or length * 0.64
    """Teardrop hip whose stalk end sits at base, calyx stub at the far tip along d."""
    rz, rx = length * 0.44, width * 0.5
    vs = a.ico((rx, rx, rz), loc=(0, 0, 0), mat=HIP, subdiv=1)
    for v in vs:  # teardrop: fattest low, narrowing toward the calyx end
        k = (v.co.z / rz)
        f = 1.0 - 0.32 * max(k, 0) + 0.06 * min(k, 0)
        v.co.x *= f
        v.co.y *= f
    a.transform(vs, (0, 0, stalk + rz))
    cal = a.cyl(0.09, 0.06, 0.15, 5, loc=(0, 0, stalk + 2 * rz - 0.04), mat=BARK)
    st = a.cyl(0.05, 0.05, stalk + 0.05, 4, loc=(0, 0, 0), mat=BARK)
    a.transform(vs + cal + st, base, _rot_z(d))


# ---------------------------------------------------------------- shrub

def shrub(a, seed, n_stems, reach, height, n_hips, leaves=True, leaf_per=2,
          branch_p=0.8, thorns_per=2, hip_len=1.0):
    rng = random.Random(seed)
    up = Vector((0, 0, 1))
    # central knot
    a.ico((0.55, 0.5, 0.32), loc=(0, 0, 0.32), mat=BARK, subdiv=1, jitter=0.12)
    tips = []
    leaf_sites = []
    off = rng.uniform(0, math.tau)
    for i in range(n_stems):
        az = off + math.tau * i / n_stems + rng.uniform(-0.25, 0.25)
        u = Vector((math.cos(az), math.sin(az), 0))
        p = Vector((-u.y, u.x, 0))
        R = reach * rng.uniform(0.75, 1.0)
        H = height * rng.uniform(0.55, 1.0)
        prof = [(0.05, 0.12), (0.3, 0.45), (0.55, 0.72), (0.8, 0.9), (1.0, 0.95)]
        pts = []
        for j, (fr, fh) in enumerate(prof):
            zig = 0 if j == 0 else (0.38 if j % 2 else -0.38) * rng.uniform(0.6, 1.2) * (1 if i % 2 else -1)
            pts.append(u * (R * fr) + p * zig + up * (H * fh + rng.uniform(-0.15, 0.15)))
        rads = [0.38, 0.34, 0.29, 0.24, 0.2, 0.15]
        for j in range(len(pts) - 1):
            seg(a, pts[j], pts[j + 1], rads[j], rads[j + 1], 6, ext=rads[j] * 0.8)
            d = (pts[j + 1] - pts[j]).normalized()
            for k in range(thorns_per):
                tt = rng.uniform(0.2, 0.85)
                c = pts[j].lerp(pts[j + 1], tt)
                ang = rng.uniform(0, math.tau)
                side = d.cross(up)
                if side.length < 1e-3:
                    side = Vector((1, 0, 0))
                side.normalize()
                n = (side * math.cos(ang) + d.cross(side) * math.sin(ang)).normalized()
                r = rads[j] * (1 - tt) + rads[j + 1] * tt
                thorn(a, c + n * r * 0.6, (n + d * 0.6).normalized(), 0.4)
        tip_dir = (pts[-1] - pts[-2]).normalized()
        tips.append((pts[-1], tip_dir, u))
        leaf_sites.append((pts[1], u, -p))
        leaf_sites.append((pts[2], u, p))
        leaf_sites.append((pts[3], u, -p))
        # side branch
        if rng.random() < branch_p:
            j0 = rng.choice((1, 2))
            s = 1 if rng.random() < 0.5 else -1
            bd = (u + p * s * 0.9).normalized()
            b0 = pts[j0]
            b1 = b0 + bd * R * 0.28 + up * H * 0.22
            b2 = b1 + bd * R * 0.22 + p * s * 0.3 - up * H * 0.08
            seg(a, b0, b1, 0.19, 0.15, 5, ext=0.1)
            seg(a, b1, b2, 0.15, 0.11, 5, ext=0.12)
            thorn(a, b1 + (b1 - b0).normalized().cross(up).normalized() * 0.12,
                  (b1 - b0).normalized().cross(up).normalized() + up * 0.3, 0.28)
            tips.append((b2, (b2 - b1).normalized(), bd))
            leaf_sites.append((b1, bd, p * s))
    # leaves
    if leaves:
        rng.shuffle(leaf_sites)
        for (c, u, s) in leaf_sites[: int(len(leaf_sites) * leaf_per / 3.0)]:
            d = (u * 0.5 + s * 0.6 + up * rng.uniform(0.2, 0.7)).normalized()
            leaf_cluster3(a, c, d, 1.6 * rng.uniform(0.85, 1.05))
        for (c, td, u) in tips:
            d = (td + up * 0.5).normalized()
            leaf_cluster3(a, c, d, 1.5, stalk=0.3)
    # hips at tips, spread around the edge
    if n_hips:
        order = sorted(range(len(tips)), key=lambda k: math.atan2(tips[k][2].y, tips[k][2].x))
        step = len(order) / float(n_hips)
        for h in range(n_hips):
            c, td, u = tips[order[int(h * step) % len(order)]]
            d = (u * 0.8 + Vector((0, 0, rng.uniform(-0.2, 0.75)))).normalized()
            p = Vector((-u.y, u.x, 0)) * rng.uniform(-0.3, 0.3)
            rosehip(a, c + p + u * 0.45 + Vector((0, 0, 0.1)), d, hip_len)


# ---------------------------------------------------------------- build

def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []
    HARV = dict(color=["#5D8A2C", "#EE5A14"])

    a = fk.Asset("RosehipScrub", "V02 RosehipScrub")
    shrub(a, 41, 8, 3.3, 3.6, 7, leaf_per=2.4, hip_len=1.35)
    o = a.finish()
    vfx.add(o, "harvest_hit", (0, -2.5, 2.2), **HARV)
    out.append(kit.tag(o, "hero", collision="hull", budget=4000,
                       notes="Low thorny rosehip scrub, 7 hips. harvest_hit: leaf/orange burst on pick."))

    # parts
    a = fk.Asset("RosehipThornStem", "V02 RosehipThornStem")
    pts = [Vector(p) for p in ((0, 0, 0), (0.25, 0, 1.4), (-0.15, 0, 2.6), (0.2, 0, 4.0))]
    rads = [0.34, 0.3, 0.26, 0.22]
    for j in range(3):
        seg(a, pts[j], pts[j + 1], rads[j], rads[j + 1], 7, ext=0.15 if j else 0)
    for (j, tt, n) in ((0, 0.5, (1, -0.3, 0)), (0, 0.8, (-1, 0.2, 0)), (1, 0.4, (0.2, -1, 0)),
                       (1, 0.75, (1, 0.3, 0)), (2, 0.5, (-1, -0.3, 0))):
        c = pts[j].lerp(pts[j + 1], tt)
        n = Vector(n).normalized()
        thorn(a, c + n * rads[j] * 0.65, (n + Vector((0, 0, 0.6))).normalized(), 0.38)
    # short side stub (cut)
    seg(a, pts[1] + Vector((0, 0, 0.3)), pts[1] + Vector((0.75, 0.1, 1.0)), 0.16, 0.13, 6)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="Thorn stem section, cut ends."))

    a = fk.Asset("RosehipLeafCluster", "V02 RosehipLeafCluster")
    seg(a, (0, 0, 0), (0, 0.2, 0.9), 0.09, 0.07, 5)
    tip = Vector((0, 0.2, 0.9))
    leaf(a, tip, (0, 0.35, 1), 1.4, 0.85)
    leaf(a, tip, (-1, 0.15, 0.35), 1.3, 0.8)
    leaf(a, tip, (1, 0.15, 0.35), 1.3, 0.8)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="Three-leaf cluster."))

    a = fk.Asset("RosehipThorn", "V02 RosehipThorn")
    outline = [(-0.25, 0), (0.25, 0), (0.18, 0.35), (0.22, 0.7), (0.34, 1.0), (0.04, 0.68), (-0.1, 0.32)]
    a.poly_prism(outline, 0.16, loc=(0, 0.08, 0), rot=(math.pi / 2, 0, 0), mat=BARK)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=300, notes="Single curved thorn spike."))

    a = fk.Asset("RosehipLeafUnderside", "V02 RosehipLeafUnderside")
    leaf(a, (0, -1.0, 0.06), (0, 1, 0.08), 2.0, 0.75, fold=0.14, th=0.06)
    seg(a, (0, -1.05, 0.1), (0, 0.85, 0.24), 0.045, 0.02, 4)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="Single leaf, raised midrib."))

    # drop
    a = fk.Asset("Rosehip", "V02 Rosehip")
    rosehip(a, (0, 0, 0), (0, 0, 1), 0.9, 0.6, stalk=0.02)
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="none", budget=300, notes="Loose rosehip fruit pickup."))

    # variations
    a = fk.Asset("RosehipScrubCompact", "V02 RosehipScrubCompact")
    shrub(a, 7, 6, 2.2, 2.2, 4, leaf_per=2.6, branch_p=0.6, thorns_per=1, hip_len=1.25)
    o = a.finish()
    vfx.add(o, "harvest_hit", (0, -1.8, 1.5), **HARV)
    out.append(kit.tag(o, "variant", collision="hull", budget=3000,
                       notes="Compact low scrub, 4 hips. harvest_hit: pick burst."))

    a = fk.Asset("RosehipScrubSpreading", "V02 RosehipScrubSpreading")
    shrub(a, 93, 9, 4.0, 3.4, 8, leaf_per=2, branch_p=0.7, thorns_per=1, hip_len=1.25)
    o = a.finish()
    vfx.add(o, "harvest_hit", (0, -2.8, 2.2), **HARV)
    out.append(kit.tag(o, "variant", collision="hull", budget=3000,
                       notes="Widest spreading scrub, 8 hips. harvest_hit: pick burst."))

    a = fk.Asset("RosehipScrubBare", "V02 RosehipScrubBare")
    shrub(a, 41, 8, 3.3, 3.6, 0, leaves=False, branch_p=0.9, thorns_per=2)
    o = a.finish()
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="Bare winter state: thorny stems only."))
    return out
