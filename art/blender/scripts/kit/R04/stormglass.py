"""R04 row 4: Stormglass resource node (teal glass coral tree on a sand mound)."""
import math
import random

from mathutils import Vector

SUBJECT = "Stormglass"
ROW = 4

# Only this module uses these three keys. r04_sand / r04_storm_rock / r04_stormglass were
# retuned from the planner's values (#CF9E62 rendered orange, #4E4244 near-black, #2FC2B4
# pale cyan) at the verifier's request; see shared_lib_requests for the sheet planner.
PALETTE = {
    "r04_stormglass": ("#28BDAA", 0.3, 0, 0.35),  # Stormglass teal-turquoise crystal branches and fragments
    "r04_sand": ("#CFB08C", 1, 0, 0),  # Sand mound base of Stormglass (warm tan)
    "r04_storm_rock": ("#625454", 0.95, 0, 0),  # Dark brown-grey rocks studding the Stormglass sand mound
}

GLASS, SAND, ROCK = "r04_stormglass", "r04_sand", "r04_storm_rock"
GLINT = ["#E8FFFB", "#7FF2E4"]
TEAL = ["#28BDAA", "#8FF0E4"]
SANDC = ["#E0B880", "#C89A60"]
W, D = 8.6, 7.6


def limb(a, pts, radii, sides=8, jitter=0.08, cap=True, seed=0, fat=1.2):
    """Fat faceted coral limb swept along a polyline with a tapering radius,
    ending in a chamfered flat hex-style cut cap."""
    rng = random.Random(seed)
    bm = a.bm
    radii = [r * fat for r in radii]
    P0 = [Vector(p) for p in pts]
    # resample: one extra ring per segment, with coral-like bulges and wobble
    P, R = [P0[0]], [radii[0]]
    for i in range(1, len(P0)):
        m = (P0[i - 1] + P0[i]) / 2 + Vector([rng.uniform(-0.08, 0.08) for _ in range(3)])
        P += [m, P0[i]]
        R += [(radii[i - 1] + radii[i]) / 2 * rng.uniform(1.0, 1.1), radii[i] * rng.uniform(0.94, 1.04)]
    radii = R
    n = len(P)
    tans = []
    for i in range(n):
        t = P[min(i + 1, n - 1)] - P[max(i - 1, 0)]
        tans.append(t.normalized())
    up = Vector((0, 0, 1)) if abs(tans[0].z) < 0.9 else Vector((1, 0, 0))
    nrm = tans[0].cross(up).normalized()
    rings = []
    ph = rng.uniform(0, 1)
    for i in range(n):
        t = tans[i]
        nrm = (nrm - t * nrm.dot(t)).normalized()  # parallel transport
        bi = t.cross(nrm).normalized()
        ring = []
        for j in range(sides):
            b = 2 * math.pi * (j + ph) / sides
            r = radii[i] * (1 + rng.uniform(-0.07, 0.07))
            ring.append(bm.verts.new(P[i] + r * (math.cos(b) * nrm + math.sin(b) * bi)))
        rings.append(ring)
    if cap:
        t = tans[-1]
        ch = radii[-1] * 0.3
        c = P[-1] + t * ch
        ring = [bm.verts.new(c + (v.co - P[-1]) * 0.7) for v in rings[-1]]
        rings.append(ring)
    for i in range(len(rings) - 1):
        r1, r2 = rings[i], rings[i + 1]
        for j in range(sides):
            bm.faces.new((r1[j], r1[(j + 1) % sides], r2[(j + 1) % sides], r2[j]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    verts = [v for r in rings for v in r]
    return a._finish(verts, GLASS, None, jitter=jitter)


def _outline(t):
    return 1 + 0.07 * math.sin(3 * t + 1.1) + 0.045 * math.sin(5 * t + 0.4)


def _prof(rho, h):
    return h * (1 - min(1.0, rho) ** 2) ** 0.65 if rho < 1 else 0.0


def mound(a, w=W, d=D, h=2.3, dent=0.0, dent_r=3.0, seed=3):
    """Low faceted sand dome with an irregular outline, flat underside at z=0 and an
    optional centre crater (depleted state)."""
    rng = random.Random(seed)
    bm = a.bm
    segs = 14
    fr = [0.0, 0.3, 0.55, 0.76, 0.92, 1.0]
    rings = []
    for k, f in enumerate(fr):
        if f == 0:
            z = h - (dent if dent else 0)
            rings.append([bm.verts.new((0, 0, z))])
            continue
        ring = []
        for j in range(segs):
            t = 2 * math.pi * (j + 0.5 * (k % 2)) / segs
            o = _outline(t)
            x, y = math.cos(t) * w / 2 * f * o, math.sin(t) * d / 2 * f * o
            z = _prof(f, h) if f < 1 else 0.0
            if 0 < f < 1:
                z += rng.uniform(-0.12, 0.12)
                x += rng.uniform(-0.15, 0.15)
                y += rng.uniform(-0.15, 0.15)
            if dent:
                r = math.hypot(x, y)
                z -= dent * max(0.0, min(1.0, (dent_r - r) / (dent_r * 0.4)))
            ring.append(bm.verts.new((x, y, max(0.0, z))))
        rings.append(ring)
    c = rings[0][0]
    r1 = rings[1]
    for j in range(segs):
        bm.faces.new((c, r1[j], r1[(j + 1) % segs]))
    for k in range(1, len(rings) - 1):
        ra, rb = rings[k], rings[k + 1]
        for j in range(segs):
            if (k % 2) == 1:
                bm.faces.new((ra[j], rb[j], rb[(j + 1) % segs]))
                bm.faces.new((ra[j], rb[(j + 1) % segs], ra[(j + 1) % segs]))
            else:
                bm.faces.new((ra[j], rb[(j - 1) % segs], rb[j]))
                bm.faces.new((ra[j], rb[j], ra[(j + 1) % segs]))
    bm.faces.new(list(reversed(rings[-1])))
    verts = [v for r in rings for v in r]
    return a._finish(verts, SAND, None)


def surf(x, y, w=W, d=D, h=2.3):
    t = math.atan2(y, x)
    o = _outline(t)
    rho = math.hypot(x / (w / 2 * o), y / (d / 2 * o))
    return _prof(rho, h)


# (angle deg, radial fraction, size, on_top)  -90 = front (-Y)
RIM = [
    (215, 0.97, (3.0, 2.5, 2.3), False),   # front-left big
    (250, 0.98, (2.2, 1.9, 1.7), False),   # front-left / front big
    (290, 1.00, (1.4, 1.2, 1.1), False),   # front
    (322, 0.98, (1.7, 1.5, 1.4), False),   # front-right
    (0, 0.98, (1.9, 1.6, 1.7), False),     # right
    (45, 1.00, (1.3, 1.1, 1.1), False),    # back-right
    (98, 1.00, (1.5, 1.3, 1.2), False),    # back
    (142, 1.00, (1.2, 1.0, 1.0), False),   # back-left
    (178, 0.98, (1.6, 1.4, 1.4), False),   # left
    (268, 0.55, (1.0, 0.9, 0.95), True),   # poking up front
    (120, 0.55, (0.85, 0.8, 0.8), True),   # poking up back-left
]


def rocks(a, w=W, d=D, h=2.3, rim=RIM):
    for i, (ang, fr, size, top) in enumerate(rim):
        t = math.radians(ang)
        o = _outline(t)
        fr = fr if top else fr * 1.06
        size = size if top else tuple(c * 1.18 for c in size)
        x, y = math.cos(t) * w / 2 * fr * o, math.sin(t) * d / 2 * fr * o
        z = max(0.0, surf(x, y, w, d, h) - size[2] * 0.5) if top else 0.0
        a.rock(size, (x, y, z), (0.2 * (i % 3), 0.15 * (i % 2), t + 0.7 * i), ROCK, subdiv=1,
               rough=0.22, facets=12, sink=0.12 if not top else 0.05)


def tree(a, s=1.0, back=True, seed=10):
    """Hero crystal: tall middle trunk leaning slightly back-right, a thick right branch
    splaying up-right toward the front-right, a left branch out-left, a back stub."""
    def S(p):
        return tuple(c * s for c in p)
    # trunk (base buried in the mound)
    limb(a, [S(p) for p in [(0, 0, 0.6), (0.05, 0.05, 2.5), (0.3, 0.3, 4.5), (0.8, 0.75, 6.1), (1.2, 1.1, 7.4)]],
         [1.08 * s, 1.05 * s, 0.98 * s, 0.93 * s, 0.9 * s], seed=seed)
    # right branch: out from the fork then curling upward
    limb(a, [S(p) for p in [(0.1, 0.0, 3.3), (1.1, -0.75, 4.0), (2.0, -1.45, 5.0), (2.7, -1.9, 6.1)]],
         [0.95 * s, 0.92 * s, 0.88 * s, 0.84 * s], seed=seed + 1)
    # left branch: out-left, flatter, shorter
    limb(a, [S(p) for p in [(-0.1, 0.0, 2.8), (-1.4, -0.05, 3.4), (-2.6, -0.15, 4.0), (-3.6, -0.25, 4.8)]],
         [0.9 * s, 0.88 * s, 0.84 * s, 0.8 * s], seed=seed + 2)
    if back:
        limb(a, [S(p) for p in [(0.1, 0.4, 4.0), (-0.25, 1.6, 4.6), (-0.5, 2.8, 5.4)]],
             [0.72 * s, 0.7 * s, 0.66 * s], seed=seed + 3)


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---------------- hero ----------------
    a = fk.Asset("Stormglass", "R04 Stormglass", tint_var=0.05)
    mound(a)
    rocks(a)
    tree(a)
    o = a.finish()
    for p in [(0.1, -1.1, 3.6), (1.25, 1.15, 7.6), (2.8, -2.0, 6.3), (-3.8, -0.25, 5.0), (-0.55, 2.9, 5.6)]:
        vfx.add(o, "ore_glint", p, scale=1.0, color=GLINT)
    vfx.add(o, "heat_glow", (0.2, -0.2, 3.8), scale=1.0, color=["#30D8C8", "#A8FFF0"],
            light={"color": "#30D8C8", "brightness": 1.0, "range": 10, "flicker": False})
    vfx.add(o, "dust", (0, 0, 1.6), scale=1.2, color=SANDC)
    vfx.add(o, "harvest_hit", (0, -3, 4), color=TEAL)
    vfx.add(o, "harvest_deplete", (0, 0, 0.8), color=SANDC)
    out.append(kit.tag(o, "hero", collision="hull", budget=4000,
                       notes="ore_glint: trunk front + 4 branch tips; heat_glow: cyan soft halo + teal "
                             "PointLight at the fork (emissive glass); dust: sand motes over the mound; "
                             "harvest_hit: teal chips on the front strike face; harvest_deplete: base centre"))

    # ---------------- parts ----------------
    a = fk.Asset("StormglassMainBranch", "R04 Stormglass", tint_var=0.05)
    limb(a, [(0, 0, 0), (0.05, 0.05, 2.0), (0.2, 0.2, 4.2), (0.35, 0.3, 6.2)], [1.05, 1.0, 0.94, 0.9], seed=20)
    limb(a, [(0.1, 0, 2.4), (1.3, -0.2, 3.4), (2.3, -0.35, 4.4), (3.0, -0.45, 5.3)], [0.9, 0.86, 0.82, 0.78], seed=21)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=1500, notes="Main Branch: Y-forked trunk"))

    a = fk.Asset("StormglassSideBranch", "R04 Stormglass", tint_var=0.05)
    limb(a, [(0, 0, 0), (-0.1, 0, 1.4), (-0.35, 0, 2.9)], [0.52, 0.5, 0.47], seed=30, fat=1.45)
    limb(a, [(0, 0, 0.8), (0.7, 0, 1.5), (1.25, 0, 2.3)], [0.47, 0.45, 0.43], seed=31, fat=1.45)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=1500, notes="Side Branch: small Y twig"))

    a = fk.Asset("StormglassSandBase", "R04 Stormglass", tint_var=0.05)
    mound(a, h=2.3)
    rocks(a, h=2.3)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500, notes="Sand Base: mound with rim rocks"))

    a = fk.Asset("StormglassBranchStub", "R04 Stormglass", tint_var=0.05)
    limb(a, [(-1.9, 0, 0.9), (-0.6, 0, 1.05), (0.7, 0, 1.3), (1.9, 0, 1.6)], [0.92, 0.9, 0.88, 0.86], seed=40, fat=1.0)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=1500,
                       notes="Branch Stub: broken limb, slight upward tilt, hex cut end"))

    # ---------------- drops ----------------
    a = fk.Asset("StormglassFragment", "R04 Stormglass", tint_var=0.05)
    a.rock((1.5, 1.0, 1.05), (0, 0, 0), (0, 0, 0.4), GLASS, subdiv=1, rough=0.12, facets=8, sink=0.12)
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="none", budget=300, notes="Stormglass Fragment (lying)"))

    a = fk.Asset("StormglassFragmentB", "R04 Stormglass", tint_var=0.05)
    a.rock((1.0, 0.9, 1.6), (0, 0, 0), (0.15, 0.1, 0.3), GLASS, subdiv=1, rough=0.1, facets=8, sink=0.1)
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="none", budget=300, notes="Stormglass Fragment (tall)"))

    # ---------------- depleted ----------------
    a = fk.Asset("StormglassDepleted", "R04 Stormglass", tint_var=0.05)
    mound(a, h=2.0, dent=1.2, dent_r=2.8)
    rocks(a, h=2.0, rim=[r for r in RIM if not r[3]])
    o = a.finish()
    vfx.add(o, "dust", (0, 0, 1.2), scale=1.0, color=SANDC)
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="Depleted (Base): mound with centre crater, rock ring, no crystal; dust motes"))
    return out
