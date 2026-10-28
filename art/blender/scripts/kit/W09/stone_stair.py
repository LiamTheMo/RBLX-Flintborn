"""W09 row 2: StoneStair - chunky ashlar stair with sloped buttress walls."""
import math
import random

SUBJECT = "StoneStair"
ROW = 2
HERO_AZIMUTH = -22

PALETTE = {
    "w09_ashlar": ("#B9A590", 0.9, 0, 0),  # stair blocks and walls, greyer taupe-beige than the pavers (row 2)
    "w09_boulder": ("#8C8E98", 0.9, 0, 0),  # cool grey rocks, footings, stray stones (all rows)
    "w09_grass": ("#5FA52A", 0.95, 0, 0),  # grass edge strip tops and turf tufts
    "w09_foliage": ("#3F9A2C", 0.9, 0, 0),  # leafy plant blades and bushes round the bases
    "w09_soil": ("#9A6430", 1, 0, 0),  # exposed earth under strips, path edges and tufts
    "w09_petal": ("#F7F3E6", 0.8, 0, 0),  # small white daisy petals
    "w09_flower_eye": ("#F0BE2A", 0.8, 0, 0),  # daisy centres
}

ST = "w09_ashlar"
BEV = 0.12
JIT = 0.06


def blk(a, size, loc, rot=(0, 0, 0), bevel=BEV, jitter=JIT):
    return a.stone_block(size, loc=loc, rot=rot, mat=ST, bevel=bevel, jitter=jitter)


def blk_z(a, x0, x1, y0, y1, z0, z1, rot=(0, 0, 0), bevel=BEV):
    """Block from extents."""
    return blk(a, (x1 - x0, y1 - y0, z1 - z0),
               ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), rot, bevel)


def prism_yz(a, pts, x0, x1):
    """Extrude a CCW (y, z) outline along X from x0 to x1."""
    v = a.poly_prism(pts, x1 - x0, loc=(x0, 0, 0), rot=(math.pi / 2, 0, math.pi / 2), mat=ST)
    return v


# --------------------------------------------------------------- dressing

def tuft(a, rng, x, y, z=0.0, n=7, h=2.2, spread=0.45, mat="w09_foliage", width=0.34):
    for k in range(n):
        ang = 2 * math.pi * k / n + rng.uniform(-0.35, 0.35)
        hh = h * rng.uniform(0.6, 1.0)
        lean = rng.uniform(0.25, 0.65)
        v = a.cyl(width, 0.0, hh, sides=4, mat=mat, cap=False)
        a.transform(v, scale=(1, 0.3, 1))
        r = spread * rng.uniform(0.2, 1.0)
        a.transform(v, loc=(x + math.cos(ang) * r, y + math.sin(ang) * r, z),
                    rot=(lean, 0, ang + math.pi / 2))


def grass(a, rng, x, y, z=0.0, n=5):
    tuft(a, rng, x, y, z, n=n, h=0.9, spread=0.5, mat="w09_grass", width=0.18)


def leaves(a, rng, x, y, z=0.0, n=9, h=2.4, spread=0.6, w=0.85):
    """Broad pointed leaf blades (thin diamond prisms) fanning out of a clump."""
    for k in range(n):
        ang = 2 * math.pi * k / n + rng.uniform(-0.3, 0.3)
        hh = h * rng.uniform(0.65, 1.0)
        ww = w * rng.uniform(0.8, 1.1)
        v = a.poly_prism([(0, 0), (ww / 2, hh * 0.38), (0, hh), (-ww / 2, hh * 0.38)], 0.07,
                         rot=(math.pi / 2, 0, 0), mat="w09_foliage")
        r = spread * rng.uniform(0.1, 0.8)
        a.transform(v, loc=(x + math.cos(ang) * r, y + math.sin(ang) * r, z),
                    rot=(rng.uniform(0.2, 0.6), 0, ang - math.pi / 2))


def daisy(a, x, y, z):
    a.cyl(0.45, 0.45, 0.08, sides=8, loc=(x, y, z), mat="w09_petal")
    a.cyl(0.17, 0.17, 0.1, sides=6, loc=(x, y, z + 0.04), mat="w09_flower_eye")


def soil(a, x, y, r, z=0.0):
    a.cyl(r, r * 0.92, 0.08, sides=7, loc=(x, y, z), mat="w09_soil")


def clump(a, rng, x, y, z=0.0, h=2.4, flowers=1, size=1.0, face=-math.pi / 2):
    """Lush leafy clump: soil disc, leaf cushion and 2 overlapping fans of broad leaves.
    Daisies sit on the outer rim toward `face` (default the -Y front) so they stay visible."""
    soil(a, x, y, 1.4 * size, z)
    a.leaf_cluster(1.0 * size, loc=(x, y, z + 0.6 * size), mat="w09_foliage", lobes=7,
                   squash=0.8, floor=z)
    leaves(a, rng, x, y, z + 0.04, n=10, h=h * 1.15, spread=0.8 * size, w=1.1 * size)
    leaves(a, rng, x + 0.8 * size, y - 0.5 * size, z + 0.04, n=6, h=h * 0.85,
           spread=0.5 * size, w=0.9 * size)
    grass(a, rng, x - 0.8 * size, y + 0.3 * size, z + 0.04)
    for f in range(flowers):
        ang = face + (f - (flowers - 1) / 2) * 0.9 + rng.uniform(-0.2, 0.2)
        daisy(a, x + math.cos(ang) * 1.15 * size, y + math.sin(ang) * 1.15 * size,
              z + 0.55 + 0.25 * f)


# --------------------------------------------------------------- structure

def treads(a, rng, inner, n, rise, run, y0, broken=()):
    """n treads, each split into two blocks with a staggered seam."""
    hw = inner / 2
    for i in range(n):
        yf = y0 + i * run
        z0, z1 = i * rise, (i + 1) * rise
        depth = run + (0.7 if i < n - 1 else 0.9)
        split = (0.18 if i % 2 else -0.22) * inner + rng.uniform(-0.3, 0.3)
        for (xa, xb) in ((-hw, split), (split, hw)):
            if (i, xa < split - 0.01 and xa == -hw) in broken:
                pass
            blk_z(a, xa + 0.02, xb - 0.02, yf, yf + depth, z0, z1)


def back_fill(a, inner, y_land, y_back, h):
    hw = inner / 2
    mid = h * 0.5
    blk_z(a, -hw, 0.4, y_land, y_back, 0, mid)
    blk_z(a, 0.4, hw, y_land, y_back, 0, mid)
    blk_z(a, -hw, -0.8, y_land, y_back, mid, h)
    blk_z(a, -0.8, hw, y_land, y_back, mid, h)


def landing(a, rng, width, y_land, y_back, H, t=0.9, pieces=3):
    hw = width / 2
    xs = [-hw + width * k / pieces for k in range(pieces + 1)]
    for k in range(pieces):
        blk_z(a, xs[k] + 0.02, xs[k + 1] - 0.02, y_land, y_back, H - t, H)


def sloped_wall(a, rng, xc, ww, y0, y_land, y_back, H, rise=0.8, over=1.1, front_len=2.0,
                col_len=2.6, cope=0.6, pier_h=1.0):
    x0, x1 = xc - ww / 2, xc + ww / 2
    zf = 2 * rise + over
    z_end = H + over * 0.4
    # squarer cap block at the low front end
    blk_z(a, x0, x1, y0, y0 + front_len, 0, zf + 0.35)
    yf = y0 + front_len
    tan = (z_end - zf) / (y_land - yf)
    ang = math.atan(tan)

    def zs(y):
        return zf + (y - yf) * tan

    ncol = max(2, round((y_land - yf) / col_len))
    L = (y_land - yf) / ncol
    for j in range(ncol):
        ya, yb = yf + j * L, yf + (j + 1) * L
        top_a = zs(ya)
        # coursed blocks under the slope, staggered per column
        c = 1.2 if j % 2 else 0.8
        z = 0.0
        while z + c < top_a - 0.5:
            blk_z(a, x0, x1, ya + 0.02, yb - 0.02, z, z + c)
            z += c
            c = 1.3
        # sloped top piece
        prism_yz(a, [(ya + 0.02, z), (yb - 0.02, z), (yb - 0.02, zs(yb)), (ya + 0.02, zs(ya))],
                 x0 + 0.04, x1 - 0.04)
        # coping segment along the slope
        ym = (ya + yb) / 2
        seg = L / math.cos(ang) - 0.05
        cy = ym - cope / 2 * math.sin(ang)
        cz = zs(ym) + cope / 2 * math.cos(ang)
        blk(a, (ww + 0.2, seg, cope), (xc, cy, cz), rot=(ang, 0, 0), bevel=0.1)
    # under the landing
    top = z_end + cope
    c1, c2 = top * 0.36, top * 0.7
    ym = y_land + (y_back - y_land) * 0.45
    blk_z(a, x0, x1, y_land, y_back, 0, c1)
    blk_z(a, x0, x1, y_land, ym, c1, c2)
    blk_z(a, x0, x1, ym, y_back, c1, c2)
    blk_z(a, x0, x1, y_land, y_back, c2, top)
    # taller square pier at the back corner
    blk_z(a, x0 + 0.05, x1 - 0.05, y_back - min(2.6, y_back - y_land), y_back, top, top + pier_h,
          bevel=0.15)


def stepped_wall(a, rng, xc, ww, y0, n, rise, run, y_back, H, extra=1.2, top=5.5,
                 ruin=0.0):
    """Wall of stacked block columns stepping up with the treads (narrow/ruined)."""
    x0, x1 = xc - ww / 2, xc + ww / 2
    cols = []
    for j in range(n):
        cols.append((y0 + j * run, y0 + (j + 1) * run, (j + 1) * rise + extra))
    cols.append((y0 + n * run, y_back, top))
    for j, (ya, yb, h) in enumerate(cols):
        if ruin:
            h = max(rise * (j + 1) + 0.3, h + rng.uniform(-ruin, ruin * 0.4))
        z = 0.0
        c = 1.0 if j % 2 else 1.4
        while z < h - 0.05:
            zt = min(h, z + c)
            if h - zt < 0.6:
                zt = h
            if ruin:
                # uneven cubes: split column top courses into two smaller blocks
                if zt > h - 1.6 and (yb - ya) > 1.5 and rng.random() < 0.6:
                    ym = (ya + yb) / 2 + rng.uniform(-0.3, 0.3)
                    tilt = (rng.uniform(-0.12, 0.12), rng.uniform(-0.12, 0.12), rng.uniform(-0.15, 0.15))
                    blk_z(a, x0 + rng.uniform(0, 0.25), x1 - rng.uniform(0, 0.25), ya + 0.03, ym, z, zt,
                          rot=tilt)
                    if rng.random() < 0.7:
                        dz = rng.uniform(-0.4, 0.3)
                        blk_z(a, x0 + 0.1, x1 - 0.1, ym + 0.05, yb - 0.03, z, zt + dz)
                else:
                    blk_z(a, x0, x1, ya + 0.03, yb - 0.03, z, zt)
            else:
                blk_z(a, x0, x1, ya + 0.03, yb - 0.03, z, zt)
            z = zt
            c = 1.2
        # slightly wider cap block on top
        if not ruin:
            blk_z(a, x0 - 0.12, x1 + 0.12, ya + 0.1, yb - 0.1, h, h + 0.5, bevel=0.1)


# --------------------------------------------------------------- assets

def build_stair(fk, name, label, rng, inner, ww, n, rise, run, land_d, style="sloped",
                pier_h=1.0, greens="normal", over=1.1, gap=0.0):
    a = fk.Asset(name, label)
    L = n * run + land_d
    y0 = -L / 2
    y_land = y0 + n * run
    y_back = L / 2
    H = (n + 1) * rise
    W = inner + 2 * ww
    xc = inner / 2 + ww / 2
    treads(a, rng, inner - gap, n, rise, run, y0)
    back_fill(a, inner - gap, y_land, y_back, H - 0.9)
    landing(a, rng, inner + 0.2 - 1.2 * gap, y_land, y_back, H, pieces=2)
    for s in (-1, 1):
        if style == "sloped":
            sloped_wall(a, rng, s * xc, ww, y0, y_land, y_back, H, pier_h=pier_h,
                        rise=rise, over=over)
        else:
            stepped_wall(a, rng, s * xc, ww, y0, n, rise, run, y_back, H, extra=1.3,
                         top=H + 1.0)
    return a, dict(L=L, y0=y0, y_land=y_land, y_back=y_back, H=H, W=W, xc=xc)


def dress_base(a, rng, d, ww, heavy=False):
    W, y0, y_back, H, y_land = d["W"], d["y0"], d["y_back"], d["H"], d["y_land"]
    hw = W / 2
    # front corners of both walls
    clump(a, rng, -hw + 0.3, y0 - 0.2, h=3.0, flowers=2, size=1.6)
    clump(a, rng, hw - 0.3, y0 - 0.2, h=2.9, flowers=2, size=1.6)
    # along the side bases
    for s in (-1, 1):
        clump(a, rng, s * (hw + 0.2), y0 + d["L"] * 0.45, h=2.6, flowers=1, size=1.3)
        if heavy:
            clump(a, rng, s * (hw + 0.2), y0 + d["L"] * 0.2, h=2.4, flowers=1, size=1.2)
            clump(a, rng, s * (hw + 0.2), y0 + d["L"] * 0.72, h=2.2, flowers=0, size=1.1)
    # landing back corners
    for s in (-1, 1):
        # on the landing against the back piers (reads from the hero and the top view)
        clump(a, rng, s * (hw - ww - 0.9), y_back - 0.9, H, h=2.2, flowers=0, size=0.8)
    # dirt patch on the landing edge
    a.box((3.4, 1.6, 0.08), loc=(-0.4, y_back - 0.95, H + 0.04), rot=(0, 0, 0.06), mat="w09_soil")


def build(kit):
    fk = kit.flintkit
    out = []
    rng = random.Random(9021)

    # ---------------- hero
    a, d = build_stair(fk, "StoneStair", "W09 StoneStair", rng, inner=6.0, ww=3.0, n=5,
                       rise=1.0, run=2.0, land_d=4.0, over=0.7, gap=0.4, pier_h=1.0)
    dress_base(a, rng, d, 3.0, heavy=True)
    a.rock((1.8, 1.5, 1.1), loc=(2.6, d["y0"] - 2.0, 0), rot=(0, 0, 0.4),
           mat="w09_boulder", subdiv=1)
    a.rock((1.7, 1.4, 1.0), loc=(d["W"] / 2 + 1.8, d["y0"] + 4.6, 0), rot=(0, 0, 1.1),
           mat="w09_boulder", subdiv=1)
    o = a.finish()
    out.append(kit.tag(o, "hero", collision="precise", budget=7000,
                       notes="Walkable ashlar stair, 5 treads + landing; precise collision."))

    # ---------------- parts
    a = fk.Asset("StoneStairTopLandingSlab", "W09 StoneStair top landing slab")
    blk_z(a, -4.0, 4.0, -1.45, 2.0, 0, 1.2, bevel=0.12)
    # chiselled front lip: chamfered strip set off by a faint seam, slightly skewed
    v = prism_yz(a, [(-2.0, 0.0), (-1.48, 0.0), (-1.48, 1.17), (-2.0, 0.82)], -3.95, 3.95)
    a.transform(v, rot=(0, 0, 0.012))
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500, notes="Landing slab, chamfered front."))

    a = fk.Asset("StoneStairTreadBlock", "W09 StoneStair tread block")
    blk_z(a, -4.0, 1.6, -1.25, 1.25, 0, 1.2, bevel=0.14)
    blk_z(a, 1.62, 4.0, -1.25, 1.25, 0, 1.2, bevel=0.14)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500, notes="Tread: two fused blocks."))

    a = fk.Asset("StoneStairSideWallBlock", "W09 StoneStair side wall block")
    blk_z(a, -1.5, 1.5, -3.0, -1.05, 0, 1.6, bevel=0.14)
    blk_z(a, -1.5, 1.5, -1.0, 3.0, 0, 1.6, bevel=0.14)
    prism_yz(a, [(-1.0, 1.62), (1.0, 1.62), (1.0, 3.0), (-1.0, 2.1)], -1.48, 1.48)
    prism_yz(a, [(1.03, 1.62), (3.0, 1.62), (3.0, 4.0), (1.03, 3.0)], -1.48, 1.48)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=1500, notes="Sloped wall wedge."))

    a = fk.Asset("StoneStairBaseSupportBlock", "W09 StoneStair base support block")
    blk_z(a, -1.25, 1.25, -1.25, 1.25, 0, 2.5, bevel=0.2)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500, notes="Support cube."))

    # ---------------- narrow
    rng = random.Random(77)
    a, d = build_stair(fk, "StoneStairNarrow", "W09 StoneStair narrow", rng, inner=3.4, ww=1.8,
                       n=4, rise=0.9, run=2.0, land_d=3.0, style="stepped")
    W, y0 = d["W"], d["y0"]
    clump(a, rng, -W / 2, y0 - 0.2, h=2.2, flowers=1, size=0.8)
    clump(a, rng, W / 2, y0 - 0.2, h=2.2, flowers=1, size=0.8)
    for s in (-1, 1):
        clump(a, rng, s * (W / 2 + 0.2), y0 + 5.0, h=2.0, flowers=1, size=0.8)
        tuft(a, rng, s * d["xc"], y0 + 3.0, 2.7 + 0.5, n=5, h=1.4)  # moss tufts on wall tops
        tuft(a, rng, s * d["xc"], d["y_back"] - 1.0, d["H"] + 1.5, n=6, h=1.6)
    o = a.finish()
    out.append(kit.tag(o, "variant", collision="precise", budget=4500,
                       notes="Narrow overgrown stair with tall piers."))

    # ---------------- broad
    rng = random.Random(55)
    a, d = build_stair(fk, "StoneStairBroad", "W09 StoneStair broad", rng, inner=11.0, ww=2.5,
                       n=5, rise=0.8, run=2.2, land_d=3.0, pier_h=1.4, gap=0.2)
    W, y0 = d["W"], d["y0"]
    for s in (-1, 1):
        clump(a, rng, s * (W / 2 - 0.2), y0 - 0.2, h=2.2, flowers=1, size=0.9)
        clump(a, rng, s * (W / 2 + 0.2), y0 + 7.0, h=2.0, flowers=1, size=0.8)
        tuft(a, rng, s * (W / 2 - 1.25), d["y_back"] - 0.4, d["H"] + 1.48, n=5, h=1.5)
    o = a.finish()
    out.append(kit.tag(o, "variant", collision="precise", budget=4500,
                       notes="Broad shallow stair with long sloped copings."))

    # ---------------- ruined
    rng = random.Random(404)
    a = fk.Asset("StoneStairRuined", "W09 StoneStair ruined")
    inner, ww, n, rise, run, land_d = 6.0, 3.0, 5, 0.9, 2.0, 4.0
    L = n * run + land_d
    y0, y_land, y_back, H = -L / 2, -L / 2 + n * run, L / 2, (n + 1) * rise
    hw = inner / 2
    # treads: some halves broken (lower, tilted) but each step keeps one walkable half
    for i in range(n):
        yf = y0 + i * run
        z0, z1 = i * rise, (i + 1) * rise
        split = rng.uniform(-0.8, 0.8)
        broken_side = rng.choice((-1, 1)) if i in (1, 3, 4) else 0
        for side, (xa, xb) in ((-1, (-hw, split)), (1, (split, hw))):
            if side == broken_side:
                blk_z(a, xa + 0.05, xb - 0.15, yf + 0.1, yf + run + 0.6, z0, z1 - 0.3,
                      rot=(rng.uniform(-0.1, 0.1), rng.uniform(-0.1, 0.1), rng.uniform(-0.15, 0.15)))
            else:
                blk_z(a, xa + 0.02, xb - 0.02, yf, yf + run + 0.7, z0, z1,
                      rot=(0, 0, rng.uniform(-0.04, 0.04)))
    back_fill(a, inner, y_land, y_back, H - 0.9)
    blk_z(a, -6.0, -0.2, y_land, y_back, H - 0.9, H)
    blk_z(a, 0.0, 4.0, y_land + 0.4, y_back, H - 0.9, H - 0.2, rot=(0.05, -0.06, 0.04))
    for s in (-1, 1):
        stepped_wall(a, rng, s * (hw + ww / 2), ww, y0, n, rise, run, y_back, H, extra=0.9,
                     top=H + 0.6, ruin=1.1)
    # loose rubble cubes round the base
    for (x, y, sz, r) in ((-2.6, y0 - 1.6, 1.0, 0.4), (-1.0, y0 - 2.4, 0.7, 0.9),
                          (2.2, y0 - 1.5, 1.1, 0.2), (3.6, y0 - 2.5, 0.75, 1.2),
                          (7.3, y0 + 3.5, 0.9, 0.7)):
        soil(a, x, y, sz * 0.9)
        blk(a, (sz, sz * 1.1, sz * 0.85), (x, y, sz * 0.42 + 0.05),
            rot=(rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15), r), bevel=0.08)
    # foliage: base, wall tops and landing
    d = dict(W=12.0, y0=y0, y_back=y_back, H=H, y_land=y_land, L=L)
    clump(a, rng, -6.2, y0 - 0.2, h=2.4, flowers=2)
    clump(a, rng, 6.2, y0 - 0.2, h=2.2, flowers=1)
    for s in (-1, 1):
        soil(a, s * 6.3, y0 + 7.0, 1.1)
        leaves(a, rng, s * 6.3, y0 + 7.0, 0.04, n=8, h=2.0, spread=0.7, w=0.8)
        tuft(a, rng, s * 4.5, y0 + 4.0, 3.0, n=5, h=1.3)
        tuft(a, rng, s * 4.5, y_back - 1.5, H + 0.4, n=6, h=1.6)
    tuft(a, rng, -1.5, y_land + 1.8, H, n=5, h=1.3)
    a.box((2.4, 1.2, 0.08), loc=(1.6, y_back - 0.8, H - 0.12), mat="w09_soil")
    a.rock((1.0, 0.9, 0.7), loc=(-7.2, y0 + 3.0, 0), rot=(0, 0, 0.6), mat="w09_boulder", subdiv=1)
    o = a.finish()
    out.append(kit.tag(o, "variant", collision="precise", budget=4500,
                       notes="Ruined stair: broken treads, ragged walls, rubble; still climbable."))
    return out
