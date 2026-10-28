"""W08 row 4: RopeCrossing, a suspension rope bridge between anchor stones.

Orientation: the reference FRONT cell shows the long elevation (posts at both
ends, rope curve between) and SIDE shows it end-on, while the kit renders FRONT
looking along +Y and SIDE along -X. To match those two cells the bridge length
runs along X. (The reference TOP cell is drawn rotated 90 degrees relative to
its own FRONT cell, so it cannot match both.)"""
import math
import random

from mathutils import Vector

SUBJECT = "RopeCrossing"
ROW = 4
HERO_AZIMUTH = -22

PALETTE = {
    "w08_wood": ("#A8582A", 0.88, 0, 0),
    "w08_rope": ("#D4A857", 0.95, 0, 0),
    "w08_stone": ("#9CA2AA", 0.95, 0, 0),
    "w08_nail": ("#C48A3C", 0.5, 0.6, 0),
    "w08_banner": ("#B3202A", 0.85, 0, 0),
}

WOOD, ROPE, STONE, NAIL, FLAG = "w08_wood", "w08_rope", "w08_stone", "w08_nail", "w08_banner"


# ---------------------------------------------------------------- helpers
def twisted_rope(a, pts, r, spacing=0.3, rseg=4, period=None):
    """Two-strand laid rope along a polyline: strands spiral round the path so
    the rope shows twist ridges. Overall radius ~r."""
    P = [Vector(p) for p in pts]
    seg = [(P[i + 1] - P[i]).length for i in range(len(P) - 1)]
    L = sum(seg)
    n = max(4, int(L / spacing))
    period = period or r * 6.5
    samples = []
    for j in range(n + 1):
        s = L * j / n
        acc = 0.0
        for i, l in enumerate(seg):
            if acc + l >= s - 1e-6 or i == len(seg) - 1:
                t = (s - acc) / l if l > 1e-9 else 0.0
                samples.append((s, P[i].lerp(P[i + 1], min(1.0, t)), (P[i + 1] - P[i]).normalized()))
                break
            acc += l
    for k in (0, 1):
        strand = []
        for s, p, tng in samples:
            nrm = tng.cross(Vector((0, 0, 1)))
            if nrm.length < 0.2:
                nrm = tng.cross(Vector((1, 0, 0)))
            nrm.normalize()
            bi = tng.cross(nrm)
            th = 2 * math.pi * s / period + k * math.pi
            off = (nrm * math.cos(th) + bi * math.sin(th)) * (r * 0.42)
            strand.append(tuple(p + off))
        a.tube_loop(strand, r * 0.62, mat=ROPE, rseg=rseg, closed=False)


def anchor_stone(a, size, loc, taper=0.2, seed=0, chip=True):
    """Chunky tapered grey block with big chiselled chamfers, flat top, on z=loc[2]."""
    sx, sy, sz = size
    cx, cy, z0 = loc
    vs = a.stone_block((sx, sy, sz), (cx, cy, z0 + sz / 2), mat=STONE,
                       bevel=min(size) * 0.17, jitter=min(size) * 0.05)
    for v in vs:
        t = max(0.0, min(1.0, (v.co.z - z0) / sz))
        k = 1.0 - taper * t
        v.co.x = cx + (v.co.x - cx) * k
        v.co.y = cy + (v.co.y - cy) * k
        v.co.z = max(z0, v.co.z)
    if chip:
        a.rock((sx * 0.42, sy * 0.38, sz * 0.36), (cx - sx * 0.36, cy - sy * 0.38, z0),
               mat=STONE, subdiv=1, rough=0.06, facets=14, sink=0.0)
    return vs


def square_post(a, loc, h, w=0.8, flag_dir=0, nail_dir=-1, collar=True, nail=True):
    """Square flat-topped post standing on loc (x, y, z0). The flag hangs on the
    X face pointing flag_dir (toward the span), just under the rope collar."""
    x, y, z0 = loc
    a.box((w, w, h), (x, y, z0 + h / 2), mat=WOOD, bevel=0.06, jitter=0.02)
    top = z0 + h
    if collar:
        a.rope_rings(w * 0.62, top - 1.0, count=collar if collar > 1 else 3, thickness=0.15,
                     loc=(x, y), mat=ROPE)
    if flag_dir:
        fx = x + flag_dir * (w / 2 + 0.04)
        a.box((0.07, 0.6, 0.82), (fx, y, top - 1.2 - 0.41), mat=FLAG)
        # notched tail: two short tabs under the flag (total ~1.1 tall)
        a.box((0.07, 0.22, 0.28), (fx, y - 0.19, top - 2.02 - 0.14), mat=FLAG)
        a.box((0.07, 0.22, 0.28), (fx, y + 0.19, top - 2.02 - 0.14), mat=FLAG)
    if nail:
        d = nail_dir
        a.cyl(0.12, 0.1, 0.08, sides=6, loc=(x, y + d * (w / 2), top - 0.45),
              rot=(-d * math.pi / 2, 0, 0), mat=NAIL)
    return top


def deck_z(x, xe, z_end, sag):
    if abs(x) >= xe:
        return z_end
    return z_end - sag * (1.0 - (x / xe) ** 2)


def deck_slope(x, xe, sag):
    if abs(x) >= xe:
        return 0.0
    return 2.0 * sag * x / (xe * xe)


def bridge(a, length=16.0, deck_w=3.4, sag=1.2, stone=(3.4, 3.4, 3.2), stone_y=1.8,
           post_h=4.6, post_y=2.15, planks=14, hangers=10, rope_drop=2.0, plank_t=0.35,
           posts_per_corner=1, rope_sets=1, rubble=True, damaged=False, seed=1,
           rope_r=0.28, rope_spacing=0.3, end_rise=0.7, chip=True):
    rng = random.Random(seed)
    sx, sy, sz = stone
    half = length / 2
    stone_x = half - sx / 2
    post_x = stone_x - 0.3           # posts stand near the stone centres
    xe = post_x - 0.5                # deck span ends at the end walls
    z_end = sz + end_rise            # deck ends sit on the wooden end walls

    # ---- anchor stones
    for i, (ix, iy) in enumerate([(-1, -1), (-1, 1), (1, -1), (1, 1)]):
        anchor_stone(a, stone, (ix * stone_x, iy * stone_y, 0.0), seed=seed + i, chip=chip)

    # ---- end posts
    post_tops = {}
    for ix in (-1, 1):
        for iy in (-1, 1):
            for k in range(posts_per_corner):
                px = ix * (post_x + k * 0.95)
                h = post_h - k * 0.7
                top = square_post(a, (px, iy * post_y, sz - 0.1), h,
                                  flag_dir=-ix if k == 0 else 0, nail_dir=iy, nail=(k == 0), collar=(True if k == 0 else 2))
                post_tops[(ix, iy, k)] = (px, iy * post_y, top)

    # ---- wooden end walls: two stacked beams between the posts, deck ends on top
    for ix in (-1, 1):
        wy = 2 * post_y + 0.5
        lo = end_rise * 0.5
        a.box((0.75, wy, lo - 0.03), (ix * post_x, 0, sz + lo / 2), mat=WOOD, bevel=0.05, jitter=0.02)
        a.box((0.75, wy - 0.3, end_rise - lo + 0.12), (ix * post_x, 0, sz + lo + (end_rise - lo + 0.12) / 2),
              mat=WOOD, bevel=0.05, jitter=0.02)

    # ---- planks
    n = planks
    step = (2 * xe - 0.6) / (n - 1)
    missing = {3, 4, 9} if damaged else set()
    for i in range(n):
        x = -xe + 0.3 + i * step
        if i in missing:
            continue
        z = deck_z(x, xe, z_end, sag)
        ang = -math.atan(deck_slope(x, xe, sag))
        roll = rng.uniform(-0.03, 0.03)
        yaw = rng.uniform(-0.04, 0.04)
        loc = (x, rng.uniform(-0.05, 0.05), z)
        if damaged and i in (5, 10):
            # loose plank hanging by one rope end
            ang += 0.9 if i == 5 else -0.7
            roll += 0.25
            loc = (x, 0.3, z - 0.5)
        a.plank((0.6, deck_w, plank_t), loc, rot=(roll, ang, yaw), mat=WOOD)

    # ---- side ropes along the deck edges
    for iy in (-1, 1):
        pts = []
        steps = 18
        for j in range(steps + 1):
            x = -post_x + 2 * post_x * j / steps
            pts.append((x, iy * (deck_w / 2 + 0.06), deck_z(x, xe, z_end, sag) + 0.25))
        a.tube_loop(pts, 0.13, mat=ROPE, rseg=5, closed=False)

    # ---- end swag ropes between the post collars
    for ix in (-1, 1):
        px, py, top = post_tops[(ix, 1, 0)]
        zt = top - 0.8
        pts = [(px, -py + 2 * py * j / 8, zt - 0.7 * (1 - ((j / 4) - 1) ** 2)) for j in range(9)]
        a.tube_loop(pts, 0.13, mat=ROPE, rseg=5, closed=False)

    # ---- main ropes + hangers
    for iy in (-1, 1):
        for s in range(rope_sets):
            px, py, top = post_tops[(1, iy, min(s, posts_per_corner - 1))]
            z_top = top - 0.8
            drop = rope_drop + s * 1.0
            y_end = py
            y_mid = iy * (deck_w / 2 + 0.08)
            snapped = damaged and iy == -1 and s == 0

            def rope_pt(x):
                t = abs(x) / px
                zc = deck_z(0.0, xe, z_end, sag) + drop + 0.15
                z = zc + (z_top - zc) * t ** 1.8
                y = y_mid + (y_end - y_mid) * t
                return (x, y, z)

            if snapped:
                for side in (-1, 1):
                    pts = []
                    for j in range(9):
                        x = side * px * (1 - j / 8 * 0.55)
                        p = rope_pt(x)
                        fall = (j / 8) ** 2 * (3.4 if side < 0 else 2.6)
                        pts.append((p[0] + side * fall * 0.35, p[1] - 0.15 * j / 8, p[2] - fall))
                    twisted_rope(a, pts, rope_r, spacing=0.4, rseg=4)
                    fx, fy, fz = pts[-1]
                    for k in range(3):
                        a.tube_loop([(fx, fy, fz), (fx + rng.uniform(-0.2, 0.2),
                                     fy + rng.uniform(-0.15, 0.15), fz - 0.45)],
                                    0.06, mat=ROPE, rseg=3, closed=False)
            else:
                nseg = 24
                pts = [rope_pt(-px + 2 * px * j / nseg) for j in range(nseg + 1)]
                if s == 0:
                    twisted_rope(a, pts, rope_r, spacing=rope_spacing, rseg=4)
                else:
                    a.tube_loop(pts, rope_r * 0.8, mat=ROPE, rseg=4, closed=False)

            if s > 0 or snapped:
                continue
            hx = xe - 0.5
            for h in range(hangers):
                x = -hx + 2 * hx * h / (hangers - 1)
                p = rope_pt(x)
                zb = deck_z(x, xe, z_end, sag) + 0.25
                if p[2] - zb < 0.3:
                    continue
                if damaged and iy == 1 and h == 6:
                    a.tube_loop([p, (x + 0.6, p[1] + 0.25, zb + 0.5)], 0.09, mat=ROPE,
                                rseg=4, closed=False)
                    continue
                a.tube_loop([p, (x, p[1], zb)], 0.09, mat=ROPE, rseg=4, closed=False)
                a.cyl(0.16, 0.16, 0.22, sides=5, loc=(x, p[1], zb + 0.02), mat=ROPE)

    # ---- rubble beside the front-left stone
    if rubble:
        a.rock((1.2, 1.1, 0.9), (-half + 0.3, -stone_y - sy / 2 - 0.25, 0.0), mat=STONE,
               subdiv=1, facets=12)
        a.rock((0.8, 0.75, 0.6), (-half + 1.6, -stone_y - sy / 2 - 0.5, 0.0), mat=STONE,
               subdiv=1, facets=12)


# ---------------------------------------------------------------- build
def build(kit):
    fk = kit.flintkit
    out = []

    a = fk.Asset("RopeCrossing", "W08 RopeCrossing", seed=81)
    bridge(a)
    o = a.finish()
    out.append(kit.tag(o, "hero", collision="precise", budget=8000,
                       notes="Walkable suspension bridge along X; deck sags 1.2 studs between "
                             "wooden end walls on 4 anchor stones. No VFX."))

    # ---- parts
    a = fk.Asset("RopeCrossingMainRope", "W08 RopeCrossing part", seed=82)
    pts = [(-4.0 + 8.0 * j / 20, 0, 2.3 - 1.4 * (2 * j / 20 - 1) ** 2) for j in range(21)]
    twisted_rope(a, pts, 0.28, spacing=0.25, rseg=5)
    for sgn in (-1, 1):
        a.torus(0.34, 0.11, (sgn * 4.25, 0, 0.75), rot=(math.pi / 2, 0, 0), mat=ROPE, seg=8, rseg=4)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="Main catenary rope with end loops."))

    a = fk.Asset("RopeCrossingHangerRope", "W08 RopeCrossing part", seed=83)
    a.cyl(0.1, 0.1, 2.5, sides=6, mat=ROPE)
    for z in (0.15, 0.35, 2.15, 2.35):
        a.torus(0.15, 0.065, (0, 0, z), mat=ROPE, seg=8, rseg=4)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="Vertical hanger with wraps."))

    a = fk.Asset("RopeCrossingPlank", "W08 RopeCrossing part", seed=84)
    a.plank((3.4, 0.6, 0.35), (0, 0, 0.175), mat=WOOD)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500, notes="Single deck plank."))

    a = fk.Asset("RopeCrossingEndPost", "W08 RopeCrossing part", seed=85)
    square_post(a, (0, 0, 0), 5.5, flag_dir=0, nail_dir=-1)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500, notes="End post with rope collar and brass nail."))

    a = fk.Asset("RopeCrossingAnchorStone", "W08 RopeCrossing part", seed=86)
    anchor_stone(a, (3.4, 3.4, 3.4), (0, 0, 0), seed=7, chip=False)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500, notes="Anchor stone block."))

    a = fk.Asset("RopeCrossingSideRope", "W08 RopeCrossing part", seed=87)
    pts = [(-3.0 + 6.0 * j / 16, 0, 0.7 - 0.3 * (1 - ((j / 8) - 1) ** 2)) for j in range(17)]
    twisted_rope(a, pts, 0.18, spacing=0.2, rseg=5)
    for sgn in (-1, 1):
        a.torus(0.22, 0.08, (sgn * 3.2, 0, 0.7), rot=(0, math.pi / 2, 0), mat=ROPE, seg=8, rseg=4)
        a.cyl(0.21, 0.21, 0.3, sides=6, loc=(sgn * 2.9, 0, 0.7), rot=(0, math.pi / 2, 0), mat=ROPE)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="Short side rope with loop knots."))

    # ---- variations
    a = fk.Asset("RopeCrossingNarrow", "W08 RopeCrossing variant", seed=88)
    bridge(a, length=12.0, deck_w=2.0, sag=0.9, stone=(2.6, 2.4, 2.6), stone_y=1.3,
           post_h=4.0, post_y=1.35, planks=12, hangers=6, rope_drop=1.6, rubble=False,
           seed=5, rope_r=0.24, rope_spacing=0.4)
    o = a.finish()
    out.append(kit.tag(o, "variant", collision="precise", budget=5000, notes="A. Narrow crossing."))

    a = fk.Asset("RopeCrossingWide", "W08 RopeCrossing variant", seed=89)
    bridge(a, length=16.0, deck_w=6.0, sag=1.0, stone=(3.4, 3.4, 3.0), stone_y=3.3,
           post_h=4.6, post_y=3.45, planks=11, hangers=5, posts_per_corner=2, rope_sets=2,
           rubble=False, seed=6, rope_spacing=0.6, chip=False)
    o = a.finish()
    out.append(kit.tag(o, "variant", collision="precise", budget=5000, notes="B. Wide crossing, doubled ropes."))

    a = fk.Asset("RopeCrossingDamaged", "W08 RopeCrossing variant", seed=90)
    bridge(a, damaged=True, rubble=True, hangers=9, seed=7, rope_spacing=0.45)
    o = a.finish()
    out.append(kit.tag(o, "variant", collision="precise", budget=5000,
                       notes="C. Damaged: missing planks, snapped front main rope, detached hanger."))
    return out
