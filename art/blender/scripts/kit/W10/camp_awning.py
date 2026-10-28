"""W10 row 1: CampAwning - open-sided canvas market/camp stall."""
import math
import random

import bmesh
from mathutils import Vector

SUBJECT = "CampAwning"
ROW = 1
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 90

PALETTE = {
    "w10_wood": ("#8A4A22", 0.85, 0, 0),
    "w10_canvas": ("#E3CFA0", 0.95, 0, 0),
    "w10_rope": ("#C48A38", 0.8, 0, 0),
    "w10_stone": ("#9A9498", 0.9, 0, 0),
    "w10_banner": ("#B8191F", 0.9, 0, 0),
    "w10_iron": ("#575B64", 0.5, 0.4, 0),
    "w10_lantern": ("#FFB022", 0.4, 0, 2),
    "w10_foliage": ("#3F8C24", 0.9, 0, 0),
}

WOOD, CANVAS, ROPE, STONE = "w10_wood", "w10_canvas", "w10_rope", "w10_stone"
BANNER, IRON, GLASS, LEAF = "w10_banner", "w10_iron", "w10_lantern", "w10_foliage"
GLOW = dict(color=["#FFB022", "#FF8A1E"])
PI = math.pi


# ---------------------------------------------------------------- helpers

def place(a, verts, loc=(0, 0, 0), yaw=0.0):
    verts = [v for v in verts if v.is_valid]
    a.transform(verts, loc, (0, 0, yaw))
    return verts


def sheet(a, c00, c10, c11, c01, nu=12, nv=10, sag=0.5, thick=0.12, bays=1,
          mat=CANVAS, floor=0.05, seed=1, pinch=None):
    """Sagging cloth sheet between 4 corners (c00=-u-v, c10=+u-v, c11, c01).
    Edges scallop down between corners; the centre sags most."""
    rng = random.Random(seed)
    bm = a.bm
    c00, c10, c11, c01 = map(Vector, (c00, c10, c11, c01))
    grid = []
    for j in range(nv + 1):
        v = j / nv
        row = []
        for i in range(nu + 1):
            u = i / nu
            p = (1 - u) * (1 - v) * c00 + u * (1 - v) * c10 + u * v * c11 + (1 - u) * v * c01
            su = abs(math.sin(PI * bays * u))
            sv = math.sin(PI * v)
            p.z -= sag * (su + sv) - (sag if pinch is None else pinch) * su * sv
            p.z = max(p.z, floor)
            row.append(bm.verts.new(p))
        grid.append(row)
    # triangulate every quad along the diagonal that points at the sheet
    # centre, so the canvas shows clean creases radiating from the middle
    faces = []
    ci, cj = nu / 2, nv / 2
    for j in range(nv):
        for i in range(nu):
            a0, a1 = grid[j][i], grid[j][i + 1]
            b1, b0 = grid[j + 1][i + 1], grid[j + 1][i]
            if (i + 0.5 < ci) == (j + 0.5 < cj):
                faces += [bm.faces.new((a0, a1, b1)), bm.faces.new((a0, b1, b0))]
            else:
                faces += [bm.faces.new((a0, a1, b0)), bm.faces.new((a1, b1, b0))]
    res = bmesh.ops.solidify(bm, geom=faces, thickness=thick)
    verts = [v for r in grid for v in r]
    verts += [e for e in res["geom"] if isinstance(e, bmesh.types.BMVert)]
    return a._finish(list(set(verts)), mat)


def wood_post(a, x, y, h, r=0.5, notch=False):
    a.cyl(r, r, h - 0.35, sides=8, loc=(x, y, 0), mat=WOOD, jitter=0.02)
    if notch:
        for s in (-1, 1):
            a.box((r * 1.7, r * 0.55, 0.45), loc=(x, y + s * r * 0.55, h - 0.35),
                  mat=WOOD, bevel=0.06, base=True)
    else:
        a.cyl(r, r * 0.5, 0.35, sides=8, loc=(x, y, h - 0.35), mat=WOOD)


def rope_tie(a, x, y, z, r=0.5, tail_dir=(1, 0), tail=1.2, wraps=2):
    for k in range(wraps):
        a.torus(r + 0.1, 0.15, loc=(x, y, z + k * 0.3), seg=8, rseg=3, mat=ROPE)
    if tail:
        dx, dy = tail_dir
        p0 = (x + dx * (r + 0.1), y + dy * (r + 0.1), z + 0.1)
        pts = [p0, (p0[0] + dx * 0.25, p0[1] + dy * 0.25, z - tail * 0.5),
               (p0[0] + dx * 0.3, p0[1] + dy * 0.3, z - tail)]
        a.tube_loop(pts, 0.1, mat=ROPE, rseg=4, closed=False)


def banner(a, x, y, zb, w=1.6, h=4.0, rod=True):
    """Red swallowtail banner in the XZ plane, front face toward -Y at y-0.1."""
    hw = w / 2
    pts = [(-hw, 0), (0, 0.6), (hw, 0), (hw, h), (-hw, h)]
    a.poly_prism(pts, 0.1, loc=(x, y, zb), rot=(PI / 2, 0, 0), mat=BANNER)
    dm = [(0, -0.55), (0.42, 0), (0, 0.55), (-0.42, 0)]
    a.poly_prism(dm, 0.04, loc=(x, y - 0.1, zb + h * 0.55), rot=(PI / 2, 0, 0), mat=CANVAS)
    dm2 = [(0, -0.3), (0.22, 0), (0, 0.3), (-0.22, 0)]
    a.poly_prism(dm2, 0.03, loc=(x, y - 0.14, zb + h * 0.55), rot=(PI / 2, 0, 0), mat=BANNER)
    if rod:
        a.beam((x - hw - 0.15, y - 0.05, zb + h + 0.05), (x + hw + 0.15, y - 0.05, zb + h + 0.05),
               0.08, sides=5, mat=WOOD, end_mat=WOOD)


def lantern(a, loc=(0, 0, 0), hook=True):
    """Iron-framed lantern ~0.9 x 0.9 x 1.6, bottom centre at loc."""
    x, y, z = loc
    a.box((0.9, 0.9, 0.14), loc=(x, y, z), mat=IRON, base=True, bevel=0.03)
    a.box((0.62, 0.62, 0.9), loc=(x, y, z + 0.14), mat=GLASS, base=True)
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.box((0.1, 0.1, 0.94), loc=(x + sx * 0.34, y + sy * 0.34, z + 0.12),
                  mat=IRON, base=True)
    a.cyl(0.62, 0.14, 0.38, sides=4, loc=(x, y, z + 1.04), rot=(0, 0, PI / 4), mat=IRON)
    if hook:
        a.torus(0.13, 0.04, loc=(x, y, z + 1.5), rot=(PI / 2, 0, 0), seg=8, rseg=3, mat=IRON)


def hung_lantern(a, px, py, z_arm, dirx=0, diry=-1, reach=1.3, r=0.5):
    """Iron bracket from a post with a lantern hanging below. Returns glow pos."""
    sx, sy = px + dirx * (r - 0.1), py + diry * (r - 0.1)
    ex, ey = px + dirx * (r + reach), py + diry * (r + reach)
    a.beam((sx, sy, z_arm), (ex, ey, z_arm), 0.07, sides=4, mat=IRON, end_mat=IRON)
    a.box((0.05, 0.05, 0.35), loc=(ex, ey, z_arm - 0.35), mat=IRON, base=True)
    lz = z_arm - 0.35 - 1.6
    lantern(a, (ex, ey, lz))
    return (ex, ey, lz + 0.7)


def table(a, loc=(0, 0, 0), yaw=0.0, L=5.0, W=2.0, H=2.8):
    vs = []
    pw = W / 3
    for k in (-1, 0, 1):
        vs += a.plank((L, pw - 0.04, 0.25), loc=(0, k * pw, H - 0.125), mat=WOOD)
    ang = math.atan((W - 0.5) / (H - 0.3))
    ln = (H - 0.3) / math.cos(ang) - 0.15
    for sx in (-1, 1):
        for s in (-1, 1):
            vs += a.box((0.25, 0.25, ln), loc=(sx * (L / 2 - 0.6), 0, (H - 0.25) / 2 + 0.05),
                        rot=(s * ang, 0, 0), mat=WOOD)
    vs += a.box((L - 1.0, 0.22, 0.22), loc=(0, 0, 0.9), mat=WOOD)
    return place(a, vs, loc, yaw)


def bench(a, loc=(0, 0, 0), yaw=0.0, L=5.0, W=1.2, H=1.6):
    vs = a.plank((L, W, 0.25), loc=(0, 0, H - 0.125), mat=WOOD)
    for sx in (-1, 1):
        vs += a.box((0.3, W * 0.8, H - 0.25), loc=(sx * (L / 2 - 0.5), 0, 0), mat=WOOD,
                    base=True, bevel=0.04)
    vs += a.box((L - 1.0, 0.18, 0.18), loc=(0, 0, 0.5), mat=WOOD)
    return place(a, vs, loc, yaw)


def stool(a, loc=(0, 0, 0), yaw=0.0, S=1.6):
    vs = a.plank((S, S, 0.25), loc=(0, 0, S - 0.125), mat=WOOD)
    for sx in (-1, 1):
        for sy in (-1, 1):
            vs += a.box((0.24, 0.24, S - 0.25), loc=(sx * (S / 2 - 0.25), sy * (S / 2 - 0.25), 0),
                        mat=WOOD, base=True)
    return place(a, vs, loc, yaw)


def crate(a, loc=(0, 0, 0), yaw=0.0, S=2.0):
    vs = a.box((S - 0.16, S - 0.16, S - 0.16), loc=(0, 0, 0.08), mat=WOOD, base=True)
    h = S / 2 - 0.14
    for sx in (-1, 1):
        for sy in (-1, 1):
            vs += a.box((0.3, 0.3, S), loc=(sx * h, sy * h, 0), mat=WOOD, base=True)
    for z in (0.15, S - 0.15):
        for s in (-1, 1):
            vs += a.box((S - 0.4, 0.26, 0.26), loc=(0, s * h, z), mat=WOOD)
            vs += a.box((0.26, S - 0.4, 0.26), loc=(s * h, 0, z), mat=WOOD)
    # diagonal brace on the front face
    vs += a.box((S * 1.15, 0.12, 0.24), loc=(0, -h - 0.02, S / 2), rot=(0, PI / 4, 0), mat=WOOD)
    return place(a, vs, loc, yaw)


def barrel(a, loc=(0, 0, 0), r=1.1, h=2.6):
    x, y, z = loc
    a.cyl(r * 0.86, r, h / 2, sides=10, loc=(x, y, z), mat=WOOD)
    a.cyl(r, r * 0.86, h / 2, sides=10, loc=(x, y, z + h / 2), mat=WOOD, cap=False)
    a.cyl(r * 0.8, r * 0.8, 0.06, sides=10, loc=(x, y, z + h - 0.06), mat=WOOD)
    for zz, rr in ((0.3, 0.9), (h / 2, 1.0), (h - 0.3, 0.9)):
        a.torus(r * rr + 0.02, 0.06, loc=(x, y, z + zz), seg=10, rseg=3, mat=IRON, squash=0.7)


def tuft(a, loc, n=5, ht=0.7, seed=0):
    rng = random.Random(seed)
    x, y, z = loc
    for k in range(n):
        ang = 2 * PI * k / n + rng.uniform(-0.3, 0.3)
        tilt = rng.uniform(0.25, 0.5)
        a.cyl(0.13, 0.0, ht * rng.uniform(0.75, 1.2), sides=3,
              loc=(x + 0.12 * math.cos(ang), y + 0.12 * math.sin(ang), z),
              rot=(-tilt * math.sin(ang), tilt * math.cos(ang), 0), mat=LEAF)


def stones(a, pts, seed=3):
    rng = random.Random(seed)
    for (x, y, s) in pts:
        a.stone_block((s * rng.uniform(0.9, 1.2), s * rng.uniform(0.8, 1.0), s * 0.75),
                      loc=(x, y, s * 0.36), rot=(0, 0, rng.uniform(-0.6, 0.6)), mat=STONE)


def table_items(a, x, y, z, full=True):
    """Cream scrolls and mugs plus a golden pot on the table top."""
    a.cyl(0.18, 0.18, 0.9, sides=6, loc=(x - 1.2, y - 0.6, z + 0.18), rot=(0, PI / 2, 0.3),
          mat=CANVAS)
    mugs = ((0.3, 0.2), (1.1, -0.4), (-0.4, -0.45), (1.8, 0.35))
    for dx, dy in (mugs if full else mugs[:2]):
        a.cyl(0.2, 0.18, 0.4, sides=6, loc=(x + dx, y + dy, z), mat=CANVAS)
    # golden pot (rope tan reads as the reference's ochre crockery)
    a.cyl(0.3, 0.42, 0.35, sides=7, loc=(x - 1.6, y + 0.4, z), mat=ROPE)
    a.cyl(0.42, 0.22, 0.35, sides=7, loc=(x - 1.6, y + 0.4, z + 0.35), mat=ROPE, cap=False)
    if full:
        a.cyl(0.18, 0.18, 0.8, sides=6, loc=(x + 0.6, y + 0.55, z + 0.18), rot=(0, PI / 2, -0.4),
              mat=CANVAS)


def stall(a, X, Y, h_back, h_front, tie, sag, xs=None, bays=1, banner_fl=True,
          banner_fr=True, lantern_at="fr", crossbars=True, seed=1, pinch=None):
    """Posts at x in xs (default (-X, X)) and y=+-Y with a sagging canopy."""
    xs = xs or (-X, X)
    for xi, x in enumerate(xs):
        for y, h in ((-Y, h_front), (Y, h_back)):
            wood_post(a, x, y, h)
            tdir = (math.copysign(1, x) if x else 0, math.copysign(1, y))
            rope_tie(a, x, y, tie - 0.2, tail_dir=tdir if x else (0, tdir[1]))
    inset = -0.25   # sheet corners just past the post centres: a broad drape
    cz = tie
    nu = 6 * bays
    sheet(a, (xs[0] + inset, -Y + inset, cz), (xs[-1] - inset, -Y + inset, cz),
          (xs[-1] - inset, Y - inset, cz), (xs[0] + inset, Y - inset, cz),
          nu=nu, nv=6, sag=sag, bays=bays, seed=seed, pinch=pinch)
    glow = None
    xl, xr = xs[0], xs[-1]
    if crossbars:
        for x in (xl, xr):
            ext = 3.0 if (x == xr and banner_fr) else 1.2
            x0, x1 = (x - 1.2, x + ext)
            a.beam((x0, -Y, h_front - 0.7), (x1, -Y, h_front - 0.7), 0.22, sides=6,
                   mat=WOOD, end_mat=WOOD)
            a.lashing((x, -Y - 0.45, h_front - 0.7), size=0.4, rot=(PI / 2, 0, 0), mat=ROPE)
    if banner_fl:
        a.box((0.1, 0.5, 0.1), loc=(xl, -Y - 0.5, tie - 0.9), mat=IRON)
        banner(a, xl, -Y - 0.55, tie - 5.0)
    if banner_fr and crossbars:
        banner(a, xr + 2.0, -Y - 0.05, h_front - 0.85 - 4.8, w=1.8, h=4.6)
    if lantern_at == "fr":
        glow = hung_lantern(a, xr, -Y, 7.9 if h_front > 9 else h_front - 1.8)
    elif lantern_at == "left":
        glow = hung_lantern(a, xl, -Y, h_front - 1.8, dirx=-1, diry=0, reach=1.0)
    return glow


# ---------------------------------------------------------------- build

def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []
    glow_note = "heat_glow socket = lantern glow (amber, scale 0.6)"

    # ---------------- hero
    a = fk.Asset("CampAwning", "W10 CampAwning")
    X, Y = 6.3, 5.3
    glow = stall(a, X, Y, 9.3, 10.5, 8.6, 2.9, pinch=4.8)
    table(a, (0.2, -0.6, 0))
    table_items(a, 0.2, -0.6, 2.8)
    bench(a, (0.2, -2.6, 0), L=4.2)
    bench(a, (0.2, 1.4, 0), L=4.2)
    stool(a, (2.9, -5.6, 0), yaw=0.3)
    stool(a, (-3.6, 3.2, 0), yaw=-0.2)
    barrel(a, (-4.5, -3.2, 0))
    crate(a, (4.5, 3.6, 0), yaw=0.1)
    crate(a, (4.4, 3.5, 2.0), yaw=-0.25)
    crate(a, (4.7, -1.4, 0), yaw=0.35)
    stones(a, [(-7.3, -4.0, 0.8), (7.4, -6.2, 0.9), (-5.6, 6.3, 0.7)])
    for k, (x, y) in enumerate(((-6.9, -5.9), (5.6, -6.0), (7.0, 4.6), (-7.0, 4.7), (-5.3, -6.1))):
        tuft(a, (x, y, 0), seed=k)
    a.leaf_cluster(0.55, loc=(7.0, 5.9, 0.3), mat=LEAF, lobes=5, floor=0)
    a.leaf_cluster(0.5, loc=(-7.1, -5.3, 0.3), mat=LEAF, lobes=5, floor=0)
    o = a.finish()
    vfx.add(o, "heat_glow", glow, scale=0.6, **GLOW)
    out.append(kit.tag(o, "hero", collision="precise", budget=5000,
                       notes=f"Open camp/market stall, walkable underneath. Sockets: {glow_note} "
                             "at the front-right lantern. No smoke."))

    # ---------------- parts
    a = fk.Asset("CampAwningCanopy", "W10 CampAwning part")
    sheet(a, (-6, -5, 1.5), (6, -5, 1.5), (6, 5, 1.5), (-6, 5, 1.5), nu=6, nv=6, sag=1.2, pinch=1.8)
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.torus(0.32, 0.08, loc=(sx * 6.1, sy * 5.1, 1.25), rot=(PI / 2, 0, PI / 4 * sx * sy),
                    seg=8, rseg=3, mat=ROPE)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Saggy canvas sheet ~12x10 with rope corner loops."))

    a = fk.Asset("CampAwningRidgePole", "W10 CampAwning part")
    a.beam((-6.5, 0, 0.5), (6.5, 0, 0.5), 0.5, sides=8, mat=WOOD, end_mat=WOOD)
    for x in (-5.6, -5.3, 5.3, 5.6):
        a.torus(0.56, 0.09, loc=(x, 0, 0.5), rot=(0, PI / 2, 0), seg=10, rseg=3, mat=ROPE)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Horizontal ridge beam ~13 long with rope wraps at both ends."))

    a = fk.Asset("CampAwningPost", "W10 CampAwning part")
    wood_post(a, 0, 0, 9.0, notch=True)
    rope_tie(a, 0, 0, 7.9, tail_dir=(1, 0), wraps=3)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Single wood post 9 tall, rope collar, notched top."))

    a = fk.Asset("CampAwningPeg", "W10 CampAwning part")
    vs = a.cyl(0.03, 0.15, 1.0, sides=6, mat=WOOD)
    vs += a.cyl(0.2, 0.17, 0.2, sides=6, loc=(0, 0, 1.0), mat=WOOD)
    vs += a.torus(0.2, 0.05, loc=(0, 0, 0.85), seg=8, rseg=3, mat=ROPE)
    vs += a.tube_loop([(0.2, 0, 0.85), (0.5, 0, 0.6), (0.7, 0, 0.25)], 0.05, mat=ROPE,
                      rseg=4, closed=False)
    a.transform([v for v in vs if v.is_valid], (0, 0, 0.05), (0, -0.3, 0))
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="Small angled tent peg with rope loop."))

    a = fk.Asset("CampAwningTable", "W10 CampAwning part")
    table(a)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Long plank bench-table 5x2x2.8 with X legs."))

    a = fk.Asset("CampAwningBench", "W10 CampAwning part")
    bench(a)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Plank bench 5x1.2x1.6."))

    a = fk.Asset("CampAwningStool", "W10 CampAwning part")
    stool(a)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Square stool 1.6."))

    a = fk.Asset("CampAwningCrate", "W10 CampAwning part")
    crate(a)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="2x2x2 plank crate with corner battens."))

    a = fk.Asset("CampAwningLantern", "W10 CampAwning part")
    lantern(a)
    o = a.finish()
    vfx.add(o, "heat_glow", (0, 0, 0.6), scale=0.6, **GLOW)
    out.append(kit.tag(o, "part", collision="none", budget=1500,
                       notes=f"Hanging iron lantern, emissive glass. Sockets: {glow_note}."))

    # ---------------- variations
    a = fk.Asset("CampAwningSquareStall", "W10 CampAwning variant")
    glow = stall(a, 4.2, 4.2, 8.2, 9.2, 7.7, 2.2, banner_fr=False, seed=2, pinch=3.4)
    table(a, (0.3, 0.2, 0), L=3.6, W=1.8, H=2.6)
    table_items(a, 0.6, 0.2, 2.6, full=False)
    barrel(a, (-2.9, -2.6, 0), r=1.0, h=2.4)
    crate(a, (3.0, 3.0, 0), yaw=0.2)
    crate(a, (3.1, 0.6, 0), yaw=-0.3)
    stool(a, (-1.0, -2.6, 0), yaw=0.2)
    stones(a, [(-4.9, -3.4, 0.7), (4.9, 4.8, 0.7)], seed=5)
    for k, (x, y) in enumerate(((-4.8, -4.8), (4.8, -4.8), (-4.8, 4.8))):
        tuft(a, (x, y, 0), seed=10 + k)
    o = a.finish()
    vfx.add(o, "heat_glow", glow, scale=0.6, **GLOW)
    out.append(kit.tag(o, "variant", collision="precise", budget=3000,
                       notes=f"1. Square Stall 10x10. Sockets: {glow_note} at the front-right lantern."))

    a = fk.Asset("CampAwningLongShelter", "W10 CampAwning variant")
    glow = stall(a, 7.8, 4.6, 8.4, 9.2, 8.0, 1.7, xs=(-7.8, 0.0, 7.8), bays=2, pinch=2.8,
                 banner_fl=False, banner_fr=False, lantern_at="left", seed=3)
    a.beam((-8.4, 4.6, 8.65), (8.4, 4.6, 8.65), 0.4, sides=7, mat=WOOD, end_mat=WOOD)
    bench(a, (-0.2, -1.4, 0), L=6.0)
    bench(a, (0.2, 1.6, 0), L=6.0)
    crate(a, (5.6, 2.6, 0), yaw=0.2)
    barrel(a, (-5.6, 2.6, 0), r=1.0, h=2.4)
    stool(a, (5.0, -2.8, 0), yaw=0.3)
    stones(a, [(-8.7, -3.4, 0.7), (8.7, 5.2, 0.8)], seed=6)
    for k, (x, y) in enumerate(((-8.5, -5.2), (0.8, -5.2), (8.5, -5.1), (-0.8, 5.2))):
        tuft(a, (x, y, 0), seed=20 + k)
    o = a.finish()
    vfx.add(o, "heat_glow", glow, scale=0.6, **GLOW)
    out.append(kit.tag(o, "variant", collision="precise", budget=3000,
                       notes=f"2. Long Shelter 18x10, 6 posts, ridge pole. Sockets: {glow_note} "
                             "at the left-end lantern."))

    a = fk.Asset("CampAwningLeanTo", "W10 CampAwning variant")
    # two tall posts on the high (left/back) side; the canvas wedge slopes
    # down to ground pegs on the right, lowest at the front-right corner, so
    # the open front and left show the bench and stool tucked underneath
    PX, PY = -4.0, 3.4
    for y in (-PY, PY):
        wood_post(a, PX, y, 8.6)
        rope_tie(a, PX, y, 7.6, tail_dir=(-1, math.copysign(1, y)))
    a.beam((PX, -PY - 0.9, 7.95), (PX, PY + 0.9, 7.95), 0.32, sides=7, mat=WOOD, end_mat=WOOD)
    pegs = ((5.6, -PY - 0.4, 0.2), (5.0, PY + 0.2, 0.7))
    sheet(a, (PX + 0.3, -PY - 0.3, 7.8), pegs[0], pegs[1], (PX + 0.3, PY + 0.3, 7.8),
          nu=6, nv=6, sag=0.7, floor=0.1, seed=4)
    for (px, py, pz) in pegs:
        qx, qy = px + 0.5, py + math.copysign(0.4, py)
        a.cyl(0.05, 0.15, 0.9, sides=6, loc=(qx, qy, 0), mat=WOOD)
        a.cyl(0.2, 0.17, 0.18, sides=6, loc=(qx, qy, 0.9), mat=WOOD)
        a.torus(0.2, 0.05, loc=(qx, qy, 0.78), seg=8, rseg=3, mat=ROPE)
        a.tube_loop([(px, py, pz + 0.1), (qx, qy, 0.8)], 0.07, mat=ROPE, rseg=4, closed=False)
    bench(a, (-2.2, 0.4, 0), yaw=PI / 2, L=4.0)
    stool(a, (0.2, -1.6, 0), yaw=0.3)
    crate(a, (-2.4, 3.0, 0), yaw=-0.2)
    stones(a, [(-5.2, 4.3, 0.7), (6.4, -2.0, 0.6)], seed=7)
    for k, (x, y) in enumerate(((-4.8, -2.6), (-4.9, 4.4), (6.2, 3.4))):
        tuft(a, (x, y, 0), seed=30 + k)
    # turn the layout so the posts stand at the back-left and the wedge falls
    # toward the front-right, facing the hero camera
    a.transform([v for v in a.bm.verts if v.is_valid], (0, 0, 0), (0, 0, math.radians(-40)))
    out.append(kit.tag(a.finish(), "variant", collision="precise", budget=3000,
                       notes="3. Lean-To: two tall posts on the high side, canvas wedge pegged "
                             "to the ground at the front-right; bench and stool underneath. "
                             "No sockets."))
    return out
