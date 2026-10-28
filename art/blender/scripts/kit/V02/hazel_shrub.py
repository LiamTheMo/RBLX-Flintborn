"""V02 row 3: Hazel shrub (upright multi-stem vase, bright leaves, nut pods)."""
import math
import random

import bmesh

SUBJECT = "HazelShrub"
ROW = 3
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 135

PALETTE = {
    "v02_bark": ("#7B4A28", 0.9, 0, 0),
    "v02_hazel_leaf": ("#80B81C", 0.8, 0, 0),
    "v02_hazel_husk": ("#B9B83A", 0.8, 0, 0),
    "v02_hazel_nut": ("#C48A4E", 0.6, 0, 0),
}
BARK, LEAF, HUSK, NUT = "v02_bark", "v02_hazel_leaf", "v02_hazel_husk", "v02_hazel_nut"
D = math.radians


def _leaf(a, base, yaw, pitch, length, width, roll=0.0, droop=0.12, cup=0.16, mat=LEAF):
    """Closed, folded broad leaf with a pointed tip (24 tris). Local +X = length."""
    bm = a.bm
    L, W = length, width

    def dz(t):
        return -droop * L * t * t

    th = 0.05 * W + 0.02
    b0 = bm.verts.new((0, 0, 0))
    tip = bm.verts.new((L, 0, dz(1.0)))
    Ls, Rs, Ts, Bs = [], [], [], []
    for t, h in ((0.18, 0.82), (0.48, 1.0), (0.78, 0.62)):
        x, y, z = t * L, h * W * 0.5, dz(t)
        Ls.append(bm.verts.new((x, y, z + cup * W * h)))
        Rs.append(bm.verts.new((x, -y, z + cup * W * h)))
        Ts.append(bm.verts.new((x, 0, z)))
        Bs.append(bm.verts.new((x, 0, z - th)))
    faces = []

    def strip(mid, edge):
        A = [b0] + mid + [tip]
        E = [b0] + edge + [tip]
        for i in range(len(A) - 1):
            q = [A[i], A[i + 1], E[i + 1], E[i]]
            uq = []
            for v in q:
                if v not in uq:
                    uq.append(v)
            faces.append(bm.faces.new(uq))

    strip(Ts, Ls)
    strip(Ts, Rs)
    strip(Bs, Ls)
    strip(Bs, Rs)
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    verts = [b0, tip] + Ls + Rs + Ts + Bs
    a.transform(verts, base, (roll, -pitch, yaw))
    return a._finish(verts, mat)


def _pod(a, loc, rot=(0, 0, 0), nut=True, s=1.0):
    """Nut in a toothed husk cup (or the empty cup), built upright then tilted."""
    verts = []
    if nut:  # ico(subdiv=2) first: it invalidates verts made before it
        nv = a.ico((0.4 * s, 0.4 * s, 0.52 * s), loc=(0, 0, 0.95 * s), mat=NUT, subdiv=2)
        top = max(nv, key=lambda v: v.co.z)
        top.co.z += 0.12 * s
        verts += nv
    verts += a.cyl(0.07 * s, 0.06 * s, 0.32 * s, sides=5, mat=HUSK)
    verts += a.cyl(0.16 * s, 0.34 * s, 0.28 * s, sides=6, loc=(0, 0, 0.28 * s), mat=HUSK)
    for k in range(6):
        yaw = D(k * 60 + 15)
        base = (0.24 * s * math.cos(yaw), 0.24 * s * math.sin(yaw), 0.46 * s)
        pitch = D(60 if nut else 56)
        verts += _leaf(a, base, yaw, pitch, 1.0 * s, 0.56 * s, droop=-0.05, cup=0.2, mat=HUSK)
    a.transform(verts, loc, rot)
    return verts


def _pod_rot(loc, tilt=35):
    """Tilt a pod outward, away from the shrub axis."""
    phi = math.atan2(loc[1], loc[0])
    return (D(tilt), 0, phi + math.pi / 2)


def _shrub(a, seed, stems, pods, leaf_len=2.3, nodes=(0.42, 0.6, 0.76, 0.9), r=0.28, fill=12):
    rng = random.Random(seed)
    for p in pods:
        _pod(a, p, _pod_rot(p, 45), s=1.45)
    pod_centres = [(p[0] * 0.9, p[1] * 0.9, p[2] + 1.0) for p in pods]
    for az, tilt, ln in stems:
        az_r, t_r = D(az), D(tilt)
        d = (math.sin(t_r) * math.cos(az_r), math.sin(t_r) * math.sin(az_r), math.cos(t_r))
        p1 = (0.1 * math.cos(az_r), 0.1 * math.sin(az_r), 0.0)
        p2 = tuple(p1[i] + d[i] * ln for i in range(3))
        a.beam(p1, p2, r, sides=6, mat=BARK, end_mat=BARK)
        for j, t in enumerate(list(nodes) + [1.0]):
            p = tuple(p1[i] + d[i] * ln * t for i in range(3))
            tip = t >= 1.0
            out = az + rng.uniform(-35, 35)
            base_pitch = 74 if tip else 50 + 20 * (j / max(1, len(nodes)))
            for dy in ((-55, 0, 55) if not tip else (-70, 0, 70)):
                yaw = D(out + dy + rng.uniform(-10, 10))
                pitch = D(base_pitch - (6 if dy else 0) + rng.uniform(-8, 8))
                ll = leaf_len * rng.uniform(0.85, 1.1)
                if tip and dy == 0:
                    pitch = D(80)
                mid = (p[0] + math.cos(yaw) * math.cos(pitch) * ll * 0.55,
                       p[1] + math.sin(yaw) * math.cos(pitch) * ll * 0.55,
                       p[2] + math.sin(pitch) * ll * 0.55)
                if any(math.dist(mid, c) < 1.4 for c in pod_centres):
                    continue
                _leaf(a, p, yaw, pitch, ll, ll * 0.76, roll=rng.uniform(-0.35, 0.35))
    # filler leaves from the crown core, between the stems, so the vase reads full
    for k in range(fill):
        yaw = D(k * 360.0 / fill + rng.uniform(-12, 12) + 15)
        z = 3.4 + 1.6 * ((k * 7) % fill) / max(1, fill)
        rr = 0.9 + 0.3 * (z - 3.4)
        p = (rr * math.cos(yaw), rr * math.sin(yaw), z)
        pitch = D(rng.uniform(52, 72))
        ll = leaf_len * rng.uniform(0.9, 1.05)
        mid = (p[0] + math.cos(yaw) * math.cos(pitch) * ll * 0.55,
               p[1] + math.sin(yaw) * math.cos(pitch) * ll * 0.55,
               p[2] + math.sin(pitch) * ll * 0.55)
        if any(math.dist(mid, c) < 1.4 for c in pod_centres):
            continue
        _leaf(a, p, yaw, pitch, ll, ll * 0.76, roll=rng.uniform(-0.35, 0.35))


def _clamp(a):
    for v in a.bm.verts:
        if v.co.z < 0:
            v.co.z = 0.0


HERO_STEMS = [(-95, 24, 5.6), (-35, 30, 5.3), (25, 26, 5.7), (95, 28, 5.4), (155, 30, 5.3), (215, 25, 5.6)]
HERO_PODS = [(0.7, -2.9, 4.8), (-1.0, -2.7, 5.6), (0.1, -2.7, 3.6)]
FRUIT_STEMS = [(-70, 28, 5.5), (-10, 24, 5.7), (50, 30, 5.3), (120, 26, 5.6), (185, 29, 5.4), (245, 24, 5.7)]
FRUIT_PODS = [(-1.5, -2.6, 5.8), (1.4, -2.7, 5.2), (-2.2, -1.8, 3.8), (2.5, -1.3, 4.1)]


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []
    harvest_col = ["#80B81C", "#B9B83A"]

    a = fk.Asset("HazelShrub", "V02 HazelShrub")
    _shrub(a, 3, HERO_STEMS, HERO_PODS)
    _clamp(a)
    o = a.finish()
    vfx.add(o, "harvest_hit", (0, -0.4, 4.5), color=harvest_col)
    out.append(kit.tag(o, "hero", collision="hull", budget=3500,
                       notes="Full & fruiting hazel. harvest_hit socket at the front pods (leaf/husk colours)."))

    a = fk.Asset("HazelStem", "V02 HazelStem")
    a.cyl(0.35, 0.27, 4.0, sides=7, mat=BARK)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes="Single stem section."))

    a = fk.Asset("HazelLeafCluster", "V02 HazelLeafCluster")
    a.cyl(0.08, 0.06, 1.0, sides=5, mat=LEAF)
    for phi in (90, 28, 152):
        _leaf(a, (0, 0, 1.0), 0, D(phi), 1.7, 1.3, roll=D(90), droop=0.05)
    _clamp(a)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes="Three-leaf cluster on a stalk."))

    a = fk.Asset("HazelNutPod", "V02 HazelNutPod")
    _pod(a, (0, 0, 0), nut=True, s=1.0)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes="Nut in its husk."))

    a = fk.Asset("HazelHusk", "V02 HazelHusk")
    _pod(a, (0, 0, 0), nut=False, s=1.05)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes="Empty husk cup."))

    a = fk.Asset("HazelNut", "V02 HazelNut")
    a.ico((0.46, 0.46, 0.43), loc=(0, 0, 0.43), mat=NUT, subdiv=2)
    _clamp(a)
    out.append(kit.tag(a.finish(), "drop", collision="none", budget=300, notes="Harvested hazelnut pickup."))

    a = fk.Asset("HazelShrubSapling", "V02 HazelShrubSapling")
    rng = random.Random(11)
    for az, tilt, ln, r in ((-80, 6, 2.6, 0.17), (30, 20, 2.0, 0.14), (160, 24, 1.7, 0.13)):
        az_r, t_r = D(az), D(tilt)
        d = (math.sin(t_r) * math.cos(az_r), math.sin(t_r) * math.sin(az_r), math.cos(t_r))
        p2 = tuple(d[i] * ln for i in range(3))
        a.beam((0, 0, 0), p2, r, sides=6, mat=BARK, end_mat=BARK)
        leaves = ((170, 58), (-90, 78), (10, 58)) if ln > 2.5 else ((az - 30, 55), (az + 40, 64))
        for yaw, pt in leaves:
            ll = 1.5 * rng.uniform(0.9, 1.05)
            _leaf(a, p2, D(yaw), D(pt), ll, ll * 0.72, roll=rng.uniform(-0.3, 0.3))
    _clamp(a)
    out.append(kit.tag(a.finish(), "variant", collision="hull", budget=3000, notes="Young sapling, no pods."))

    a = fk.Asset("HazelShrubFruiting", "V02 HazelShrubFruiting")
    _shrub(a, 7, FRUIT_STEMS, FRUIT_PODS, nodes=(0.45, 0.65, 0.84), fill=8)
    _clamp(a)
    o = a.finish()
    vfx.add(o, "harvest_hit", (0, -0.4, 4.5), color=harvest_col)
    out.append(kit.tag(o, "variant", collision="hull", budget=3000,
                       notes="Full & fruiting, 4 pods, different layout. harvest_hit socket at the front pods."))

    a = fk.Asset("HazelShrubHarvested", "V02 HazelShrubHarvested")
    _shrub(a, 3, HERO_STEMS, [], nodes=(0.5, 0.74), leaf_len=2.45, fill=10)
    _clamp(a)
    out.append(kit.tag(a.finish(), "depleted", collision="hull", budget=2000,
                       notes="Harvested: hero stems and leaves, no pods."))
    return out
