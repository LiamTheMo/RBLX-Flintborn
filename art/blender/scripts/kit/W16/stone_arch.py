"""W16 row 1: StoneArch -- freestanding sandstone ruin arch with ivy."""
import math
import random

SUBJECT = "StoneArch"
ROW = 1
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 90

PALETTE = {
    "w16_sandstone": ("#CDA877", 0.9, 0, 0),
    "w16_stone_grey": ("#8F8D86", 0.95, 0, 0),
    "w16_ivy": ("#3F8A1A", 0.8, 0, 0),
    "w16_soil": ("#7A4A2A", 0.95, 0, 0),
    # The shared w16_sandstone renders orange-peach on this row (verifier); the
    # reference arch is pale cream-tan. A module key keeps the other W16 modules
    # untouched. This row uses it for ALL its cut stone instead of w16_sandstone.
    "w16_arch_stone": ("#D6BF9C", 0.9, 0, 0),
}

SAND, GREY, IVY, SOIL = "w16_arch_stone", "w16_stone_grey", "w16_ivy", "w16_soil"
D2R = math.pi / 180.0
XZ = (math.pi / 2, 0, 0)          # poly_prism outline in XZ, extruded toward -Y


def _chamfer(pts, c=0.15):
    """Cut each corner of a convex polygon (CCW) by c studs."""
    out = []
    n = len(pts)
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        for q in (p0, p2):
            dx, dy = q[0] - p1[0], q[1] - p1[1]
            L = math.hypot(dx, dy) or 1.0
            k = min(c, L * 0.3) / L
            out.append((p1[0] + dx * k, p1[1] + dy * k))
    return out


def _slab(a, pts, depth, y=0.0, mat=SAND, spin=0.0, c=0.15):
    """Prism of the XZ outline pts, centred on y; spin = small in-plane rotation (rad)."""
    pts = _chamfer(pts, c)
    v = a.poly_prism(pts, depth, loc=(0, y + depth / 2, 0), rot=XZ, mat=mat)
    if spin:
        cx = sum(p[0] for p in pts) / len(pts)
        cz = sum(p[1] for p in pts) / len(pts)
        a.transform(v, loc=(-cx, 0, -cz))
        a.transform(v, rot=(0, spin, 0))
        a.transform(v, loc=(cx, 0, cz))
    return v


class Ring:
    """Two-centred (or round) arch geometry. half = opening half-width at the
    springing line, rise = intrados apex height above the spring."""

    def __init__(self, half, spring, rise, thick, key_w=1.0):
        if abs(rise - half) < 1e-3:
            self.c, self.R = 0.0, half
        else:
            self.R = (half * half + rise * rise) / (2 * half)
            self.c = half - self.R
        self.Ro = self.R + thick
        self.spring = spring
        self.th_a = math.degrees(math.acos(max(-1.0, min(1.0, -self.c / self.R))))
        th_ko = math.degrees(math.acos(max(-1.0, min(1.0, (key_w - self.c) / self.Ro))))
        self.th_k = min(th_ko, self.th_a - 3.0)
        self.in_apex = spring + math.sqrt(max(0.0, self.R ** 2 - self.c ** 2))
        self.out_apex = spring + math.sqrt(max(0.0, self.Ro ** 2 - self.c ** 2))

    def P(self, r, th, sx):
        return (sx * (self.c + r * math.cos(th * D2R)), self.spring + r * math.sin(th * D2R))


def arch_ring(a, rng, ring, depth, n_side=4, sides=(-1, 1), stop_deg=None, key=True,
              key_top=0.25, gap=0.1):
    """Tight wedge ring: joints ~gap studs, mirrored angles, in-plane tilt <= 0.8 deg."""
    R, Ro = ring.R, ring.Ro
    gdeg = math.degrees(gap / ((R + Ro) / 2))
    step = ring.th_k / n_side
    for sx in sides:
        end = ring.th_k if stop_deg is None else stop_deg
        i = 0
        while i * step < end - 1e-3:
            th0, th1 = i * step, min((i + 1) * step, end)
            g0 = 0.0 if i == 0 else gdeg / 2
            pts = [ring.P(R, th0 + g0, sx), ring.P(Ro, th0 + g0, sx),
                   ring.P(Ro, th1 - gdeg / 2, sx), ring.P(R, th1 - gdeg / 2, sx)]
            if stop_deg is not None and th1 >= end - 1e-3:     # broken end: ragged outer corner
                pts[2] = ring.P(Ro - 0.6, th1 + 4.0, sx)
            if sx < 0:
                pts = list(reversed(pts))
            _slab(a, pts, depth + rng.uniform(-0.05, 0.05), y=rng.uniform(-0.05, 0.05),
                  spin=rng.uniform(-0.8, 0.8) * D2R)
            i += 1
    if key:
        xi, zi = ring.P(R, ring.th_k + gdeg / 2, 1)
        xo, zo = ring.P(Ro, ring.th_k + gdeg / 2, 1)
        xi = max(xi, 0.25)
        top = ring.out_apex + key_top
        pts = [(-xi, zi - 0.15), (xi, zi - 0.15), (xo, zo), (xo, top), (-xo, top), (-xo, zo)]
        _slab(a, pts, depth + 0.3, y=-0.15)     # projects 0.3 in front only
        return top
    return ring.out_apex


def pier(a, rng, x, n, bh, w=3.5, d=3.5, plinth=(4.5, 4.5, 1.4), z0=0.0, split=True):
    """Wide plinth + n stacked blocks (stagger 0.2-0.3, rotation 2-4 deg). Returns top z."""
    if plinth:
        pw, pd, ph = plinth
        # a course of two big base stones, clearly wider than the pier above
        for k in ((-1, 1) if split else (0,)):
            a.stone_block((pw / (2 if split else 1) - 0.06, pd + rng.uniform(-0.15, 0.0), ph - 0.04 + rng.uniform(-0.08, 0.0)),
                          loc=(x + k * pw / 4, rng.uniform(-0.1, 0.1), z0 + ph / 2),
                          rot=(0, 0, rng.uniform(-2.0, 2.0) * D2R), mat=SAND)
        z0 += ph
    for i in range(n):
        s = 1 if i % 2 == 0 else -1
        ox = s * rng.uniform(0.2, 0.3) * 0.6
        oy = -s * rng.uniform(0.2, 0.3) * 0.5
        rz = s * rng.uniform(2.0, 4.0) * D2R
        a.stone_block((w + rng.uniform(-0.08, 0.08), d + rng.uniform(-0.08, 0.04), bh - 0.06),
                      loc=(x + ox, oy, z0 + bh / 2), rot=(0, 0, rz), mat=SAND)
        z0 += bh
    return z0


def clump(a, r, loc, axis, squash=0.75, lobes=6):
    """Bushy ivy clump: the dome rises along axis, base set into the face."""
    n = math.sqrt(sum(c * c for c in axis)) or 1.0
    loc = tuple(loc[i] - axis[i] / n * 0.15 * r for i in range(3))
    a.leaf_cluster(r * 1.12, loc=loc, mat=IVY, lobes=lobes, squash=squash, axis=axis, floor=0.0,
                   depth=0.8)


def ivy_pier(a, rng, x, ztop, outward, front=3, side=3, back=2, w=3.5, d=3.5, z0=1.2):
    """Flat, overlapping clumps wrapping the front, outer side and back of a pier."""
    def zs(n, k):
        return z0 + (ztop - z0) * (k + rng.uniform(0.25, 0.75)) / n
    for k in range(front):
        clump(a, rng.uniform(1.0, 1.35), (x + rng.uniform(-0.25, 0.25) * w + outward * 0.35, -d / 2 - 0.05, zs(front, k)),
              (0, -1, 0.25))
    for k in range(side):
        clump(a, rng.uniform(1.0, 1.35), (x + outward * (w / 2 + 0.05), rng.uniform(-0.3, 0.3) * d, zs(side, k)),
              (outward, 0, 0.25))
    for k in range(back):
        clump(a, rng.uniform(1.0, 1.3), (x + rng.uniform(-0.25, 0.25) * w, d / 2 + 0.05, zs(back, k)),
              (0, 1, 0.25))
    vx = x + outward * w * 0.2
    pts = [(vx + rng.uniform(-0.3, 0.3), -d / 2 - 0.08, 0.4 + (ztop - 0.4) * k / 5) for k in range(6)]
    a.tube_loop(pts, 0.09, mat=SOIL, rseg=4, closed=False)


def ivy_ring(a, rng, ring, depth, n_r=6, n_l=3, back=3, th_max=None, sides=(-1, 1)):
    """A continuous string of clumps along the ring: on the front face and the
    extrados flanks (never on the keystone top), heavier on the right."""
    th_max = th_max if th_max is not None else ring.th_k
    rm = ring.R + (ring.Ro - ring.R) * 0.55
    for sx, n in ((1, n_r), (-1, n_l)):
        if sx not in sides or n <= 0:
            continue
        for k in range(n):
            th = 8 + (th_max - 8) * (k + rng.uniform(0.2, 0.8)) / n
            if k % 2 == 0:   # front face of the ring
                x, z = ring.P(rm, th, sx)
                clump(a, rng.uniform(1.0, 1.3), (x, -depth / 2 - 0.05, z), (0, -1, 0.2))
            else:            # over the extrados, draping front
                x, z = ring.P(ring.Ro, th, sx)
                nx, nz = sx * math.cos(th * D2R), math.sin(th * D2R)
                clump(a, rng.uniform(1.0, 1.3), (x - nx * 0.2, rng.uniform(-0.6, 0.2), z - nz * 0.2),
                      (nx, -0.35, nz), squash=0.45)
    for k in range(back):
        sx = sides[k % len(sides)] if len(sides) > 1 else sides[0]
        th = 15 + (th_max - 15) * rng.uniform(0.1, 0.9)
        x, z = ring.P(rm, th, sx)
        clump(a, rng.uniform(1.0, 1.25), (x, depth / 2 + 0.05, z), (0, 1, 0.2))


def rubble(a, rng, spots):
    for (x, y, s, mat) in spots:
        a.stone_block((s, s * 0.8, s * 0.65), loc=(x, y, s * 0.32),
                      rot=(rng.uniform(-0.12, 0.12), rng.uniform(-0.15, 0.15), rng.uniform(0, 6.28)),
                      mat=mat, jitter=s * 0.06)


def base_clumps(a, rng, spots):
    """Bushy leaf clumps (r, upright) and grass tufts (small, tall-lobed)."""
    for (x, y, r) in spots:
        if r >= 0.8:
            a.leaf_cluster(r, loc=(x, y, 0.0), mat=IVY, lobes=7, squash=0.8, floor=0.0)
        else:
            a.leaf_cluster(r, loc=(x, y, 0.0), mat=IVY, lobes=5, squash=1.3, depth=1.2, floor=0.0)


def base_dressing(a, rng, px, pw=4.5, pd=4.5, mirror_bias=1.0):
    """Rubble + clumps + tufts around both plinths (within ~1.5 studs)."""
    e = pw / 2
    f = -pd / 2
    rub = []
    for sx in (-1, 1):
        x0 = sx * px
        rub += [(x0 + sx * (e + 0.5), f + 0.1, 1.4, SAND), (x0 - sx * 0.4, f - 0.45, 1.1, GREY),
                (x0 + sx * (e - 0.5), f - 0.5, 0.9, GREY), (x0 + sx * (e + 0.45), 1.0, 1.2, GREY)]
    rub += [(px + 0.9, pd / 2 + 0.4, 1.1, SAND), (-px - 0.4, pd / 2 + 0.4, 0.9, GREY)]
    rubble(a, rng, [(x + (x > 0) * 0.2 - (x < 0) * 0.2, y, s * 1.55, m) for (x, y, s, m) in rub])
    for sx in (-1, 1):   # a piled chunk on the big front-corner stone
        s = 1.0
        a.stone_block((s, s * 0.8, s * 0.65), loc=(sx * (px + e + 0.5), f + 0.1, 1.4 * 1.55 * 0.65 + 0.3),
                      rot=(0.1, -0.15 * sx, rng.uniform(0, 6.28)), mat=GREY if sx > 0 else SAND, jitter=0.06)
    cl = []
    for sx in (-1, 1):
        x0 = sx * px
        cl += [(x0 + sx * (e + 0.1), f + 1.2, 1.2), (x0 - sx * (e - 0.3), f - 0.2, 1.1),
               (x0 + sx * (e - 0.2), pd / 2 - 0.2, 1.05),
               (x0 + sx * 0.6, f - 0.6, 0.6), (x0 + sx * (e + 1.0), -0.5, 0.6)]
    cl += [(px + 0.1, pd / 2 + 0.4, 1.1), (px - 1.2, f - 0.7, 0.6)]
    base_clumps(a, rng, [(x, y, r * 1.25) for (x, y, r) in cl])


def build_arch(a, rng, half, pier_w, nblk, bh, rise, thick, plinth, depth=3.5,
               ivy_l=(3, 3, 2), ivy_r=(4, 4, 3), ring_ivy=(6, 3, 3), key_w=1.0):
    px = half + pier_w / 2
    ztop = 0
    for sx in (-1, 1):
        ztop = pier(a, rng, sx * px, nblk, bh, w=pier_w, d=depth, plinth=plinth)
    ring = Ring(half, ztop, rise, thick, key_w=key_w)
    rd = depth - 0.3
    top = arch_ring(a, rng, ring, rd)
    ivy_pier(a, rng, -px, ztop, -1, *ivy_l, w=pier_w, d=depth)
    ivy_pier(a, rng, px, ztop + 0.6, 1, *ivy_r, w=pier_w, d=depth)
    ivy_ring(a, rng, ring, rd, *ring_ivy)
    # ivy over the keystone front (lower half: adds no height)
    xk, zk = ring.P(ring.R, ring.th_k, 1)
    clump(a, 0.9, (0.35, -rd / 2 - 0.35, zk + 0.5), (0, -1, 0.15), squash=0.5)
    base_dressing(a, rng, px, pw=plinth[0], pd=plinth[1])
    return px, ztop, top


def _fin(a):
    o = a.finish()
    o["kit_two_tone_ok"] = ("w16_arch_stone is cut stone and w16_soil is brown vine stems: different "
                            "materials; the checker may file stone/soil as ground.")
    return o


def build(kit):
    fk = kit.flintkit
    out = []

    # ---------------- HERO ----------------
    rng = random.Random(1601)
    a = fk.Asset("StoneArch", "W16 StoneArch", seed=1601)
    build_arch(a, rng, half=3.0, pier_w=3.5, nblk=5, bh=1.7, rise=3.2, thick=2.3,
               plinth=(4.5, 4.5, 1.8))
    o = _fin(a)
    out.append(kit.tag(o, "hero", collision="precise", budget=6000,
                       notes="Pointed sandstone ruin arch, walk-through opening 6 x 13.6; ivy, rubble and tufts baked in. No VFX."))

    # ---------------- PARTS ----------------
    rng = random.Random(1611)
    a = fk.Asset("StoneArchKeystone", "W16 StoneArch part", seed=1611)
    _slab(a, [(-0.8, 0.0), (0.8, 0.0), (1.0, 2.5), (-1.0, 2.5)], 2.0, c=0.2)
    out.append(kit.tag(_fin(a), "part", collision="box", budget=1500, notes="Apex keystone, trapezoid."))

    a = fk.Asset("StoneArchWedge", "W16 StoneArch part", seed=1612)
    _slab(a, [(-0.75, 0.0), (0.75, 0.0), (1.05, 3.0), (-1.05, 3.0)], 2.5, c=0.2)
    out.append(kit.tag(_fin(a), "part", collision="box", budget=1500, notes="One tapered arch wedge (voussoir)."))

    a = fk.Asset("StoneArchPier", "W16 StoneArch part", seed=1613)
    pier(a, rng, 0.0, 4, 2.0, plinth=None)
    out.append(kit.tag(_fin(a), "part", collision="box", budget=1500, notes="Pier stack of 4 blocks, 3.5x3.5x8."))

    a = fk.Asset("StoneArchBase", "W16 StoneArch part", seed=1614)
    pier(a, rng, 0.0, 1, 1.8, plinth=(4.5, 4.5, 2.0), split=False)
    out.append(kit.tag(_fin(a), "part", collision="box", budget=1500, notes="Plinth base stone with a pier block on top."))

    # ---------------- VARIATIONS ----------------
    rng = random.Random(1621)
    a = fk.Asset("StoneArchPointed", "W16 StoneArch variant", seed=1621)
    build_arch(a, rng, half=2.5, pier_w=3.0, nblk=5, bh=1.6, rise=4.0, thick=2.0,
               plinth=(3.8, 4.2, 1.8), depth=3.4, ivy_l=(3, 3, 1), ivy_r=(3, 3, 2), ring_ivy=(4, 4, 2),
               key_w=0.9)
    out.append(kit.tag(_fin(a), "variant", collision="precise", budget=6000, notes="POINTED ARCH: tall narrow pointed arch."))

    rng = random.Random(1631)
    a = fk.Asset("StoneArchRound", "W16 StoneArch variant", seed=1631)
    build_arch(a, rng, half=3.0, pier_w=3.5, nblk=5, bh=1.6, rise=3.0, thick=2.3,
               plinth=(4.4, 4.5, 1.8), ivy_l=(2, 3, 1), ivy_r=(3, 3, 2), ring_ivy=(4, 3, 2))
    out.append(kit.tag(_fin(a), "variant", collision="precise", budget=6000, notes="ROUND ARCH: semicircular ring of 8 wedges + keystone."))

    rng = random.Random(1641)
    a = fk.Asset("StoneArchCollapsed", "W16 StoneArch variant", seed=1641)
    half, pw = 3.0, 3.4
    pxl = -(half + pw / 2)
    zt = pier(a, rng, pxl, 5, 1.7, w=pw, plinth=(4.3, 4.4, 1.6))
    zs = pier(a, rng, -pxl, 2, 1.7, w=pw, plinth=(4.3, 4.4, 1.6))
    ring = Ring(half, zt, 3.6, 2.3)
    arch_ring(a, rng, ring, 3.2, n_side=4, sides=(-1,), stop_deg=50.0, key=False)
    # broken top on the right stub: a tilted half block
    a.stone_block((2.2, 2.6, 0.9), loc=(-pxl - 0.4, 0.2, zs + 0.4), rot=(0.1, -0.22, 0.2), mat=SAND)
    # fallen wedge lying on the ground in front of the opening
    v = a.poly_prism(_chamfer([(-0.75, 0.0), (0.75, 0.0), (1.05, 2.8), (-1.05, 2.8)]), 2.2,
                     loc=(0, 0, 0), rot=(0, 0, 0), mat=SAND)
    a.transform(v, rot=(0, 0, 0.5), loc=(0.6, -2.4, 0.0))
    rubble(a, rng, [(1.8, 0.9, 1.3, SAND), (2.6, -2.6, 1.0, GREY), (-1.6, -2.4, 0.9, GREY),
                    (6.6, -2.4, 1.1, SAND), (6.0, 2.2, 0.9, GREY), (-6.6, -2.4, 1.0, GREY), (-1.0, 1.2, 1.0, SAND)])
    ivy_pier(a, rng, pxl, zt + 0.8, -1, 4, 4, 2, w=pw)
    ivy_pier(a, rng, -pxl, zs, 1, 2, 2, 1, w=pw, z0=0.8)
    ivy_ring(a, rng, ring, 3.2, 0, 3, 1, th_max=46.0, sides=(-1,))
    base_clumps(a, rng, [(-0.8, -1.0, 0.9), (2.0, -1.0, 0.95), (-5.6, -2.6, 1.0), (5.0, -2.6, 1.0),
                         (6.6, 0.2, 0.9), (0.4, 1.4, 0.8), (-0.2, -2.6, 0.55), (3.6, -1.6, 0.5),
                         (-7.0, 0.6, 0.55), (5.6, 1.6, 0.5)])
    out.append(kit.tag(_fin(a), "variant", collision="precise", budget=6000,
                       notes="HALF-COLLAPSED: left pier + broken half ring, right stub, fallen wedge and rubble."))
    return out
