"""W11 row 2: Storage. Reinforced X-braced crate beside an iron-hooped barrel,
its exploded parts and three variations (square crate, long chest, open crate)."""
import math

import bmesh

SUBJECT = "Storage"
ROW = 2
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 180  # reference SIDE/REAR cell shows crate and barrel side by side (rear)

PALETTE = {
    "w11_wood": ("#B5702C", 0.9, 0, 0),  # all planks, posts, logs, staves, poles, handles (one wood colour; planks end grain too)
    "w11_iron": ("#40444F", 0.6, 0.3, 0),  # hoops, straps, nail heads, cauldron, brazier/torch brackets, post base plate, lantern frame
}

W, I = "w11_wood", "w11_iron"
PI = math.pi

# Barrel profile (z, r): bulged, 2.6 at the ends, 3.4 at the belly.
PROFILE = [(0.0, 1.30), (0.8, 1.52), (1.65, 1.66), (2.4, 1.70), (3.15, 1.66), (4.0, 1.52), (4.7, 1.32)]


def prof_r(z, scale=1.0):
    pts = PROFILE
    for (z0, r0), (z1, r1) in zip(pts, pts[1:]):
        if z <= z1:
            t = (z - z0) / (z1 - z0)
            return (r0 + (r1 - r0) * t) * scale
    return pts[-1][1] * scale


# ---------------------------------------------------------------- low-level
def lathe(a, profile, sides, mat, closed=True, loc=(0, 0, 0), phase=0.0):
    """Revolve a (r, z) polyline (counter-clockwise => outward normals)."""
    bm = a.bm
    rings = []
    for (r, z) in profile:
        ring = []
        for j in range(sides):
            t = phase + 2 * PI * j / sides
            ring.append(bm.verts.new((loc[0] + r * math.cos(t), loc[1] + r * math.sin(t), loc[2] + z)))
        rings.append(ring)
    n = len(rings)
    segs = n if closed else n - 1
    for i in range(segs):
        r0, r1 = rings[i], rings[(i + 1) % n]
        for j in range(sides):
            k = (j + 1) % sides
            bm.faces.new((r0[j], r0[k], r1[k], r1[j]))
    verts = [v for ring in rings for v in ring]
    return a._finish(verts, mat)


def barrel_staves(a, loc, sides=12, scale=1.0, top=None):
    """Outer stave surface only: each stave its own strip (own tint)."""
    bm = a.bm
    prof = [(z * scale, r * scale) for z, r in PROFILE]
    if top is not None:
        prof = [(z, r) for z, r in prof if z <= top]
    out = []
    for j in range(sides):
        t0 = 2 * PI * j / sides + PI / sides
        t1 = t0 + 2 * PI / sides
        col0 = [bm.verts.new((loc[0] + r * math.cos(t0), loc[1] + r * math.sin(t0), loc[2] + z)) for z, r in prof]
        col1 = [bm.verts.new((loc[0] + r * math.cos(t1), loc[1] + r * math.sin(t1), loc[2] + z)) for z, r in prof]
        tm = (t0 + t1) / 2
        # convex stave: mid line pushed out so each stave reads as its own board
        colm = [bm.verts.new((loc[0] + r * 1.015 * math.cos(tm), loc[1] + r * 1.015 * math.sin(tm), loc[2] + z)) for z, r in prof]
        for i in range(len(prof) - 1):
            bm.faces.new((col0[i], colm[i], colm[i + 1], col0[i + 1]))
            bm.faces.new((colm[i], col1[i], col1[i + 1], colm[i + 1]))
        out.append(a._finish(col0 + colm + col1, W))
    return out


def hoop_band(a, loc, z0, z1, mat=I, proud=0.12, sides=12, scale=1.0):
    zm = (z0 + z1) / 2
    prof = [(prof_r(z0 / scale, scale) - 0.03, z0), (prof_r(z0 / scale, scale) + proud, z0),
            (prof_r(zm / scale, scale) + proud, zm), (prof_r(z1 / scale, scale) + proud, z1),
            (prof_r(z1 / scale, scale) - 0.03, z1)]
    return lathe(a, prof, sides, mat, closed=True, loc=loc, phase=PI / sides)


def disc_planks(a, R, thick, n, loc, mat=W, gap=0.02):
    """Round board made of n chord planks (top z = loc z + thick, small height steps = seams)."""
    out = []
    xs = [-R + 2 * R * k / n for k in range(n + 1)]
    for k in range(n):
        x0, x1 = xs[k] + gap / 2, xs[k + 1] - gap / 2
        samp = [x0 + (x1 - x0) * s / 3 for s in range(4)]
        def h(x):
            return math.sqrt(max(R * R - x * x, 0.0001)) * 0.999
        pts = [(x, -h(x)) for x in samp] + [(x, h(x)) for x in reversed(samp)]
        th = thick * (1.0 - 0.06 * (k % 2))
        v = a.poly_prism(pts, th, loc=loc, mat=mat)
        out.append(v)
    return out


def nail(a, loc, normal):
    """Iron nail head on a face with outward normal 'x+', 'x-', 'y+', 'y-', 'z+'."""
    rot = {"y-": (PI / 2, 0, 0), "y+": (-PI / 2, 0, 0), "x+": (0, PI / 2, 0),
           "x-": (0, -PI / 2, 0), "z+": (0, 0, 0)}[normal]
    return a.cyl(0.16, 0.11, 0.12, sides=8, loc=loc, rot=rot, mat=I)


def rotz(a, verts_lists, ang, loc=(0, 0, 0)):
    flat = list({v for vl in verts_lists for v in vl if v.is_valid})
    a.transform(flat, loc=loc, rot=(0, 0, ang))


def brace_xz(a, xl, xr, zb, zt, bw, y_in, y_out, flip=False):
    """Diagonal plank in the XZ plane, ends cut horizontal, spanning y_out..y_in (y_out < y_in)."""
    ang = math.atan2(zt - zb, xr - xl)
    dw = bw / math.sin(ang)
    if not flip:
        pts = [(xl, zb), (xl + dw, zb), (xr, zt), (xr - dw, zt)]
    else:
        pts = [(xr - dw, zb), (xr, zb), (xl + dw, zt), (xl, zt)]
    return a.poly_prism(pts, y_in - y_out, loc=(0, y_in, 0), rot=(PI / 2, 0, 0), mat=W)


# ---------------------------------------------------------------- crate pieces
def braced_face(a, w_in, h, y0, fh=0.55, bw=0.6, nails=True, stiles=0.0, planks=3, dp=0.0):
    """Front-facing (-Y) braced face: outer plane y0 (negative). Returns verts lists."""
    vl = []
    # recessed vertical panel planks
    pw = w_in / planks
    yp = y0 + 0.5 + dp  # panel plank outer face
    for k in range(planks):
        x = -w_in / 2 + pw * (k + 0.5)
        vl.append(a.box((pw - 0.03, 0.2, h - 0.1), loc=(x, yp + 0.1, h / 2), mat=W, jitter=0.01))
    # frame boards top/bottom (and optional side stiles): outer face 0.18 behind the posts
    yf = y0 + 0.18 + dp
    vl.append(a.box((w_in, yp + 0.05 - yf, fh), loc=(0, (yf + yp + 0.05) / 2, fh / 2), mat=W, bevel=0.05))
    vl.append(a.box((w_in, yp + 0.05 - yf, fh), loc=(0, (yf + yp + 0.05) / 2, h - fh / 2), mat=W, bevel=0.05))
    xl, xr = -w_in / 2, w_in / 2
    if stiles:
        for sx in (-1, 1):
            vl.append(a.box((stiles, yp + 0.05 - yf, h - 2 * fh), loc=(sx * (w_in - stiles) / 2, (yf + yp + 0.05) / 2, h / 2), mat=W, bevel=0.05))
        xl, xr = xl + stiles, xr - stiles
    zb, zt = fh, h - fh
    # thick X brace standing ~0.25 proud of the panel planks
    # bevelled planks so their edges catch light/shadow against the panel; ends tuck into frame/posts
    dx, dz = xr - xl, zt - zb
    ln, ang = math.hypot(dx, dz), math.atan2(dz, dx)
    vl.append(a.box((ln, 0.3, bw), loc=(0, yp - 0.1, (zb + zt) / 2), rot=(0, -ang, 0), mat=W, bevel=0.08))
    vl.append(a.box((ln, 0.34, bw), loc=(0, yp - 0.13, (zb + zt) / 2), rot=(0, ang, 0), mat=W, bevel=0.08))
    if nails:
        d = bw * 0.6
        for (x, z) in ((xl + d, zb + d * 0.75), (xr - d, zb + d * 0.75), (xl + d, zt - d * 0.75), (xr - d, zt - d * 0.75)):
            vl.append(nail(a, (x, yp - 0.30, z), "y-"))
    return vl


def crate(a, S, loc, post=0.6, fh=0.55, bw=0.6, top=True):
    vl = []
    hw = S / 2
    w_in = S - 2 * post
    for k in range(4):
        face = braced_face(a, w_in, S, -hw, fh=fh, bw=bw)
        rotz(a, face, k * PI / 2)
        vl += face
    # corner posts (proud of every face)
    for sx in (-1, 1):
        for sy in (-1, 1):
            vl.append(a.box((post, post, S), loc=(sx * (hw - post / 2), sy * (hw - post / 2), S / 2), mat=W, bevel=0.05, jitter=0.01))
            for z in (0.35, S - 0.35):
                vl.append(nail(a, (sx * (hw - post / 2), sy * hw - sy * 0.03, z), "y+" if sy > 0 else "y-"))
                vl.append(nail(a, (sx * hw - sx * 0.03, sy * (hw - post / 2), z), "x+" if sx > 0 else "x-"))
            if top:
                vl.append(nail(a, (sx * (hw - post / 2), sy * (hw - post / 2), S - 0.02), "z+"))
    if top:
        n = 4
        span = S - 0.5
        pw = span / n
        for k in range(n):
            y = -span / 2 + pw * (k + 0.5)
            vl.append(a.box((S - 0.4, pw - 0.04, 0.22), loc=(0, y, S - 0.19), mat=W, jitter=0.01))
    a.transform(list({v for x in vl for v in x if v.is_valid}), loc=loc)
    return vl


def barrel(a, loc):
    barrel_staves(a, loc)
    hoop_band(a, loc, 0.5, 0.95)
    hoop_band(a, loc, 3.75, 4.2)
    # open rim: top of staves, rim lip and inner wall down to the inset lid
    lathe(a, [(1.32, 4.7), (1.32, 4.8), (1.12, 4.8), (1.12, 4.5)], 12, W, closed=False, loc=loc, phase=PI / 12)
    disc_planks(a, 1.14, 0.12, 4, (loc[0], loc[1], loc[2] + 4.42))


# ---------------------------------------------------------------- variants
def long_chest(a):
    L, D, Hb = 6.0, 3.0, 2.2
    p = 0.45
    vl = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            vl.append(a.box((p, p, Hb), loc=(sx * (L / 2 - p / 2), sy * (D / 2 - p / 2), Hb / 2), mat=W, bevel=0.04))
    rows = 4
    rh = Hb / rows
    for k in range(rows):
        z = rh * (k + 0.5)
        for sy in (-1, 1):
            a.box((L - 2 * p + 0.02, 0.2, rh - 0.03), loc=(0, sy * (D / 2 - 0.15), z), mat=W, bevel=0.03, jitter=0.01)
        for sx in (-1, 1):
            a.box((0.2, D - 2 * p + 0.02, rh - 0.03), loc=(sx * (L / 2 - 0.15), 0, z), mat=W, bevel=0.03, jitter=0.01)
    # lid: slab + arched cap (outline in YZ, extruded along X)
    a.box((L + 0.1, D + 0.1, 0.4), loc=(0, 0, Hb + 0.2), mat=W, bevel=0.05)
    arch = [(-1.55, 2.6), (1.55, 2.6), (1.25, 2.95), (0.5, 3.18), (-0.5, 3.18), (-1.25, 2.95)]
    a.poly_prism(arch, L + 0.1, loc=(-(L + 0.1) / 2, 0, 0), rot=(PI / 2, 0, PI / 2), mat=W)
    strap = [(-1.62, Hb - 0.05), (1.62, Hb - 0.05), (1.62, 2.66), (1.31, 3.02), (0.52, 3.26),
             (-0.52, 3.26), (-1.31, 3.02), (-1.62, 2.66)]
    for x in (-2.1, 0.0, 2.1):
        a.poly_prism(strap, 0.34, loc=(x - 0.17, 0, 0), rot=(PI / 2, 0, PI / 2), mat=I)
        for sy in (-1, 1):
            a.box((0.34, 0.08, Hb - 0.1), loc=(x, sy * (D / 2 + 0.02), (Hb - 0.1) / 2 + 0.05), mat=I)
            for z in (0.4, 1.4):
                nail(a, (x, sy * (D / 2 + 0.06), z), "y+" if sy > 0 else "y-")


def open_crate(a):
    X, Y, H = 4.0, 3.5, 3.5
    p = 0.5
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.box((p, p, H), loc=(sx * (X / 2 - p / 2), sy * (Y / 2 - p / 2), H / 2), mat=W, bevel=0.05, jitter=0.01)
    a.box((X - 0.1, Y - 0.1, 0.55), loc=(0, 0, 0.275), mat=W, bevel=0.04)
    slats = [(0.65, 1.35), (1.65, 2.35), (2.7, 3.4)]
    for z0, z1 in slats:
        zc, sh = (z0 + z1) / 2, z1 - z0
        for sy in (-1, 1):
            a.box((X - 2 * p + 0.3, 0.22, sh), loc=(0, sy * (Y / 2 - 0.2), zc), mat=W, bevel=0.04, jitter=0.01)
            for sx in (-1, 1):
                nail(a, (sx * (X / 2 - p - 0.25), sy * (Y / 2 - 0.07), zc), "y+" if sy > 0 else "y-")
        for sx in (-1, 1):
            a.box((0.22, Y - 2 * p + 0.3, sh), loc=(sx * (X / 2 - 0.2), 0, zc), mat=W, bevel=0.04, jitter=0.01)
            for sy in (-1, 1):
                nail(a, (sx * (X / 2 - 0.07), sy * (Y / 2 - p - 0.25), zc), "x+" if sx > 0 else "x-")


# ---------------------------------------------------------------- parts
def stave_solid(a, height=4.8, width=1.1, thick=0.22):
    """One curved, bulged stave (outer arc + inner arc), front facing -Y."""
    bm = a.bm
    R = 1.7
    half = (width / 2) / R
    cols = 3
    zs = [z * height / 4.7 for z, _ in PROFILE]
    rs = [r for _, r in PROFILE]
    outer, inner = [], []
    for z, r in zip(zs, rs):
        ro, ri = [], []
        # tapered stave: full width at the belly, ~0.75 at the ends (spindle outline)
        half = (width / 2) * (0.7 + 0.3 * (r - 1.3) / 0.4) / R
        for c in range(cols):
            t = -PI / 2 - half + 2 * half * c / (cols - 1)
            ro.append(bm.verts.new((r * math.cos(t), r * math.sin(t) + 1.5, z)))
            ri.append(bm.verts.new(((r - thick) * math.cos(t), (r - thick) * math.sin(t) + 1.5, z)))
        outer.append(ro)
        inner.append(ri)
    n = len(zs)
    faces = []
    for i in range(n - 1):
        for c in range(cols - 1):
            faces.append(bm.faces.new((outer[i][c], outer[i][c + 1], outer[i + 1][c + 1], outer[i + 1][c])))
            faces.append(bm.faces.new((inner[i][c + 1], inner[i][c], inner[i + 1][c], inner[i + 1][c + 1])))
        for c in (0, cols - 1):
            faces.append(bm.faces.new((outer[i][c], outer[i + 1][c], inner[i + 1][c], inner[i][c])))
    for i in (0, n - 1):
        for c in range(cols - 1):
            faces.append(bm.faces.new((outer[i][c], outer[i][c + 1], inner[i][c + 1], inner[i][c])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    verts = [v for row in outer + inner for v in row]
    a._finish(verts, W)
    a.transform([v for v in verts if v.is_valid], rot=(0, 0, 0.45))  # convex face turned to the hero camera


def build(kit):
    fk = kit.flintkit
    out = []

    # ---------------- hero
    a = fk.Asset("Storage", "W11 Storage")
    crate(a, 4.5, (-2.25, 0.2, 0))
    barrel(a, (2.7, -0.45, 0))  # right and forward so the crate does not hide it at az -22
    o = a.finish()
    out.append(kit.tag(o, "hero", collision="hull", budget=4500,
                       notes="X-braced crate (4.5 cube) beside an iron-hooped barrel; no VFX"))

    # ---------------- parts
    a = fk.Asset("StorageTopPanel", "W11 Storage part")
    for k in range(5):
        a.box((4.5, 0.86, 0.3), loc=(0, -1.8 + 0.9 * k, 0.35), mat=W, bevel=0.04, jitter=0.01)
    for x in (-1.7, 1.7):
        a.box((0.5, 4.2, 0.2), loc=(x, 0, 0.1), mat=W)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="crate top: 5 slats on 2 battens"))

    a = fk.Asset("StorageSidePanel", "W11 Storage part")
    braced_face(a, 4.5, 4.5, -0.25, stiles=0.5)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="crate side: framed planks with X brace"))

    a = fk.Asset("StorageXBrace", "W11 Storage part")
    xb = brace_xz(a, -2, 2, 0, 4, 0.55, 0.1, -0.1)
    xb += brace_xz(a, -2, 2, 0, 4, 0.55, -0.1, -0.3, flip=True)
    # exploded: lies flat so the parts grid does not hide the stave behind it
    a.transform(list({v for v in xb if v.is_valid}), loc=(0, 2, 0.3), rot=(PI / 2, 0, 0))
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="two crossed diagonal planks"))

    a = fk.Asset("StorageCornerPost", "W11 Storage part")
    a.box((0.6, 0.6, 4.5), loc=(0, 0, 2.25), mat=W, bevel=0.05)
    nail(a, (0, -0.33, 0.35), "y-")
    nail(a, (0, -0.33, 4.15), "y-")
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="crate corner post"))

    a = fk.Asset("StorageLidTop", "W11 Storage part")
    disc_planks(a, 1.3, 0.35, 4, (0, 0, 0))
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500, notes="barrel lid: 4 planks"))

    a = fk.Asset("StorageWoodenStave", "W11 Storage part")
    stave_solid(a)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500, notes="one bulged barrel stave"))

    a = fk.Asset("StorageMetalHoop", "W11 Storage part")
    lathe(a, [(1.48, 0), (1.7, 0), (1.7, 0.3), (1.48, 0.3)], 20, I, closed=True)
    out.append(kit.tag(a.finish(), "part", collision="precise", budget=1500, notes="iron barrel hoop (hollow ring)"))

    a = fk.Asset("StorageBasePanel", "W11 Storage part")
    disc_planks(a, 1.35, 0.35, 3, (0, 0, 0))
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500, notes="barrel base: 3 planks"))

    # ---------------- variations
    a = fk.Asset("StorageSquareCrate", "W11 Storage variant")
    crate(a, 3.5, (0, 0, 0), post=0.5, fh=0.45, bw=0.52)
    out.append(kit.tag(a.finish(), "variant", collision="box", budget=3000, notes="small X-braced crate"))

    a = fk.Asset("StorageLongChest", "W11 Storage variant")
    long_chest(a)
    out.append(kit.tag(a.finish(), "variant", collision="box", budget=3000, notes="long chest, arched lid, 3 iron straps"))

    a = fk.Asset("StorageOpenCrate", "W11 Storage variant")
    open_crate(a)
    out.append(kit.tag(a.finish(), "variant", collision="box", budget=3000, notes="open-top slatted crate"))
    return out
