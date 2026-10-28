"""W13 row 1: Watchtower - four-post timber lookout with canvas pyramid roof."""
import math

from mathutils import Vector

SUBJECT = "Watchtower"
ROW = 1
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 90

PALETTE = {
    "w13_timber": ("#A9612C", 0.85, 0, 0),
    "w13_canvas": ("#E6D2A4", 0.95, 0, 0),
    "w13_stone": ("#8A9199", 0.9, 0, 0),
    "w13_banner": ("#C3262A", 0.8, 0, 0),
    "w13_moss": ("#4C9A3C", 0.9, 0, 0),
}

T, C, S, B, M = "w13_timber", "w13_canvas", "w13_stone", "w13_banner", "w13_moss"


# ---------------------------------------------------------------- helpers
def sqbeam(a, p1, p2, w, h=None, w2=None, h2=None, mat=T, normal=None):
    """Rectangular beam p1->p2 (w across, h along `normal`), optional taper."""
    h = h if h is not None else w
    w2 = w2 if w2 is not None else w
    h2 = h2 if h2 is not None else h
    p1, p2 = Vector(p1), Vector(p2)
    ax = (p2 - p1).normalized()
    if normal is not None:
        v = Vector(normal)
        v = (v - ax * v.dot(ax)).normalized()
        u = ax.cross(v).normalized()
    else:
        ref = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((0, 1, 0))
        u = ax.cross(ref).normalized()
        v = u.cross(ax).normalized()
    bm = a.bm
    vs = []
    for p, ww, hh in ((p1, w, h), (p2, w2, h2)):
        for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            vs.append(bm.verts.new(p + u * (su * ww / 2) + v * (sv * hh / 2)))
    idx = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    fs = [bm.faces.new([vs[i] for i in q]) for q in idx]
    _orient(bm, fs)
    return a._finish(vs, mat)


def _orient(bm, faces):
    import bmesh
    bmesh.ops.recalc_face_normals(bm, faces=faces)


def tri_faces(a, pts_list, mat):
    """Raw faces from lists of points; returns verts."""
    bm = a.bm
    vs, fs = [], []
    for pts in pts_list:
        fv = [bm.verts.new(p) for p in pts]
        vs += fv
        fs.append(bm.faces.new(fv))
    return a._finish(vs, mat), fs


def clamp_floor(a):
    for v in a.bm.verts:
        if v.co.z < 0:
            v.co.z = 0.0


def lerp(p, q, t):
    return tuple(p[i] + (q[i] - p[i]) * t for i in range(3))


# ---------------------------------------------------------------- pieces
def roof(a, half, eave_z, apex_z, droop=0.45, torn=False, thick=0.25):
    """Canvas pyramid shell with sagging eaves. torn: the +X side is ripped away."""
    apex = (0.0, 0.0, apex_z)
    corners = [(-half, -half), (half, -half), (half, half), (-half, half)]
    bm = a.bm
    for side in range(4):
        (x1, y1), (x2, y2) = corners[side], corners[(side + 1) % 4]
        c1 = (x1, y1, eave_z)
        c2 = (x2, y2, eave_z)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        m = (mx * 0.97, my * 0.97, eave_z - droop)
        r1, r2 = lerp(c1, apex, 0.5), lerp(c2, apex, 0.5)
        rm = lerp(m, apex, 0.5)
        rm = (rm[0] * 0.96, rm[1] * 0.96, rm[2] - 0.25)
        if torn and side == 3:
            # only a ragged upper flap remains on this side
            j1 = lerp(r1, apex, 0.15)
            j2 = (rm[0] * 1.05, rm[1], rm[2] - 0.6)
            j3 = lerp(rm, r2, 0.6)
            top = [[j1, j2, apex], [j2, j3, apex], [j3, lerp(r2, apex, 0.45), apex]]
            for z_off in (0.0, -thick):
                pts = [[(p[0], p[1], p[2] + z_off) for p in t] for t in top]
                tri_faces(a, pts, C)
            continue
        tris = [[c1, m, rm], [c1, rm, r1], [m, c2, r2], [m, r2, rm], [r1, rm, apex], [rm, r2, apex]]
        vs, fs = tri_faces(a, tris, C)
        lo = [[(p[0], p[1], p[2] - thick) for p in t[::-1]] for t in tris]
        vs2, fs2 = tri_faces(a, lo, C)
        # rim strip along the eave
        c1l, ml, c2l = [(p[0], p[1], p[2] - thick) for p in (c1, m, c2)]
        tri_faces(a, [[c1, c1l, ml, m], [m, ml, c2l, c2]], C)


def finial(a, z, scale=1.0):
    s = scale
    a.box((0.9 * s, 0.9 * s, 0.25 * s), loc=(0, 0, z + 0.125 * s), mat=T, bevel=0.05)
    sqbeam(a, (0, 0, z), (0, 0, z + 1.1 * s), 0.6 * s, w2=0.5 * s, mat=T)
    a.box((0.8 * s, 0.8 * s, 0.2 * s), loc=(0, 0, z + 1.1 * s), mat=T, bevel=0.04)
    a.ico(0.42 * s, loc=(0, 0, z + 1.6 * s), mat=T, subdiv=1)
    a.cyl(0.32 * s, 0.05 * s, 0.6 * s, sides=6, loc=(0, 0, z + 1.9 * s), mat=T)


def deck(a, half, z, plank_n=7, thick=0.6, gap=0.3):
    """Plank deck top at z, planks along X (alternate planks sit 0.1 lower), plus joists."""
    w = (2 * half - gap * (plank_n - 1)) / plank_n
    for i in range(plank_n):
        y = -half + w / 2 + i * (w + gap)
        dz = 0.1 if i % 2 else 0.0
        a.box((2 * half - (0.3 if i % 2 else 0.0), w, thick), loc=(0, y, z - dz - thick / 2),
              mat=T, bevel=0.05)
    jz = z - thick - 0.3
    hj = half - 0.5
    for s in (-1, 1):
        sqbeam(a, (-hj - 0.3, s * hj, jz), (hj + 0.3, s * hj, jz), 0.6, mat=T)
        sqbeam(a, (s * hj, -hj, jz), (s * hj, hj, jz), 0.6, mat=T)
    sqbeam(a, (-hj, 0, jz), (hj, 0, jz), 0.5, mat=T)


def railing_section(a, p1, p2, z0, height, balusters=4, posts=False, post_w=0.8):
    """Rails between p1 and p2 (xy) on top of z0."""
    p1 = Vector((p1[0], p1[1], 0))
    p2 = Vector((p2[0], p2[1], 0))
    if posts:
        for p in (p1, p2):
            sqbeam(a, (p.x, p.y, z0), (p.x, p.y, z0 + height + 0.25), post_w, mat=T)
            a.box((post_w + 0.2, post_w + 0.2, 0.2), loc=(p.x, p.y, z0 + height + 0.35), mat=T)
    zt, zm = z0 + height - 0.25, z0 + height * 0.5
    for zz, ww in ((zt, 0.5), (zm, 0.38)):
        sqbeam(a, (p1.x, p1.y, zz), (p2.x, p2.y, zz), ww, mat=T)
    for i in range(balusters):
        t = (i + 1) / (balusters + 1)
        p = p1.lerp(p2, t)
        sqbeam(a, (p.x, p.y, z0), (p.x, p.y, zt), 0.28, mat=T)


def x_brace(a, pa, pb, pc, pd, normal, w=0.9, thick=0.45, bolt=True, broken=False):
    """Two crossed beams pa->pc and pb->pd (corner points) in a face plane."""
    sqbeam(a, pa, pc, w, thick, mat=T, normal=normal)
    if broken:
        mid = lerp(pb, pd, 0.45)
        sqbeam(a, pb, (mid[0], mid[1], mid[2] + 0.4), w, thick, mat=T, normal=normal)
        # snapped lower stub hanging askew
        lo = lerp(pb, pd, 0.62)
        sqbeam(a, (lo[0] + 0.6, lo[1], lo[2] - 1.2), pd, w, thick, mat=T, normal=normal)
    else:
        sqbeam(a, pb, pd, w, thick, mat=T, normal=normal)
    if bolt:
        c = lerp(lerp(pa, pc, 0.5), lerp(pb, pd, 0.5), 0.5)
        n = Vector(normal)
        cc = Vector(c) + n * (thick * 0.6)
        sqbeam(a, cc - n * 0.2, cc + n * 0.2, 0.55, mat=T)


def banner(a, x, y, ztop, w=3.0, h=7.0, tattered=False):
    """Red swallowtail banner hanging from ztop, front face at y (facing -Y)."""
    rot = (math.pi / 2, 0, 0)
    d = 0.12
    notch = 1.3
    pts = [(-w / 2, -h), (0, -h + notch), (w / 2, -h), (w / 2, 0), (-w / 2, 0)]
    if tattered:
        pts = [(-w / 2, -h + 0.6), (-w * 0.25, -h + 1.4), (-0.1, -h), (w * 0.2, -h + 1.6),
               (w / 2, -h + 0.9), (w / 2, 0), (-w / 2, 0)]
    pts = [(px + x, pz + ztop) for px, pz in pts]
    # poly_prism with rot X+90 maps local (x,y,z)->(x,-z,y): extrudes toward -Y from loc.y
    a.poly_prism(pts, d, loc=(0, y, 0), rot=rot, mat=B)
    # cream diamond emblem: outline frame plus a small solid diamond
    cz = ztop - h * 0.45
    r = w * 0.34
    dia = [(x, cz - r * 1.35), (x + r, cz), (x, cz + r * 1.35), (x - r, cz), (x, cz - r * 1.35)]
    a.strip(dia, 0.22, 0.08, loc=(0, y - d, 0), rot=rot, mat=C)
    ri = r * 0.38
    a.poly_prism([(x, cz - ri * 1.35), (x + ri, cz), (x, cz + ri * 1.35), (x - ri, cz)], 0.08,
                 loc=(0, y - d, 0), rot=rot, mat=C)
    # crossbar with knob ends
    sqbeam(a, (x - w / 2 - 0.5, y - 0.05, ztop + 0.15), (x + w / 2 + 0.5, y - 0.05, ztop + 0.15),
           0.32, mat=T)
    for s in (-1, 1):
        a.ico(0.22, loc=(x + s * (w / 2 + 0.55), y - 0.05, ztop + 0.15), mat=T, subdiv=1)


def ladder(a, x, y_bot, y_top, z_top, width=2.4, rung=1.2, rail_w=0.48):
    for s in (-1, 1):
        sqbeam(a, (x + s * width / 2, y_bot, 0), (x + s * width / 2, y_top, z_top + 0.4), rail_w,
               mat=T)
    n = int((z_top - 0.6) / rung)
    for i in range(n):
        z = 0.7 + i * rung
        t = z / (z_top + 0.4)
        y = y_bot + (y_top - y_bot) * t
        sqbeam(a, (x - width / 2 - 0.15, y, z), (x + width / 2 + 0.15, y, z), 0.32, mat=T)


def base_stone(a, x, y, size=3.6, h=2.0):
    a.stone_block((size, size, h), loc=(x, y, h / 2), mat=S, bevel=0.3)


def rubble(a, pts):
    for (x, y, s) in pts:
        a.rock((s, s * 0.9, s * 0.6), loc=(x, y, 0), mat=S, subdiv=1, facets=10, sink=0.05)


def dressing(a, d, moss=1.0):
    """Base dressing around the four footings at +-d: rubble, leafy clumps, grass, flowers."""
    rub = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            rub += [(sx * (d + 2.2), sy * (d + 0.4), 0.85), (sx * (d - 0.3), sy * (d + 2.2), 0.6)]
    rub += [(-2.0, -(d + 2.4), 0.55), (d + 2.6, 1.5, 0.5)]
    rubble(a, rub)
    clumps = [(-(d + 2.0), -(d - 1.9), 0.95), ((d + 1.9), -(d + 1.6), 0.8),
              ((d + 2.1), (d - 1.8), 0.85), (-(d - 1.6), (d + 2.1), 0.75)]
    for (x, y, r) in clumps:
        a.leaf_cluster(r * moss, loc=(x, y, r * 0.45), mat=M, lobes=6, squash=0.65, floor=0.0)
    # grass tufts: thin green spikes
    for (x, y) in ((-(d + 0.6), -(d + 2.1)), ((d + 2.4), -(d - 0.8)), (1.6, -(d + 2.0))):
        for k, (ox, oy, h) in enumerate(((0, 0, 0.9), (0.25, 0.1, 0.7), (-0.2, 0.15, 0.65))):
            a.cyl(0.14, 0.0, h, sides=4, loc=(x + ox, y + oy, 0),
                  rot=(0.25 * (k - 1), 0.3 * (k - 1), 0), mat=M)
    # little cream flowers on the clumps
    for (x, y, r) in clumps[:3]:
        for k in range(2):
            ang = k * 2.4 + x
            a.cyl(0.22, 0.22, 0.12, sides=5,
                  loc=(x + math.cos(ang) * r * 0.5, y + math.sin(ang) * r * 0.5, r * 1.05), mat=C)


# ---------------------------------------------------------------- tower
def tower(a, half_b=5.3, half_t=4.4, stone_h=2.0, deck_z=16.5, levels=2, roof_top=21.6,
          rail_h=3.5, roof_half=6.6, apex_z=26.9, banner_top=15.2, banner_h=7.0,
          damaged=False, post_w=2.0, stone=3.6, ladder_x=-3.0, brace_w=1.0):
    z0 = stone_h
    ztop = roof_top
    so = half_b + 0.7  # stones sit a little outward so they show past the eaves

    def ph(z):  # post centre half-offset at height z
        t = (z - z0) / (ztop - z0)
        return half_b + (half_t - half_b) * t

    pw_at = lambda z: post_w + (post_w * 0.85 - post_w) * (z - z0) / (ztop - z0)
    cap_zs = (deck_z - 1.0, deck_z + rail_h + 0.1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            base_stone(a, sx * so, sy * so, size=stone, h=stone_h)
            top = ztop
            if damaged and sx == -1 and sy == -1:
                top = ztop + 1.8  # bare post sticking up through the torn roof
            sqbeam(a, (sx * half_b, sy * half_b, z0 - 0.05), (sx * ph(top), sy * ph(top), top),
                   post_w, w2=pw_at(top), mat=T)
            # chunky bolted corner caps at the deck joint and the rail top
            for cz in cap_zs:
                cw = pw_at(cz) + 0.5
                cx, cy = sx * ph(cz), sy * ph(cz)
                a.box((cw, cw, 0.75), loc=(cx, cy, cz), mat=T, bevel=0.08)
                for (bx, by) in ((sx * (cw / 2 + 0.06), 0), (0, sy * (cw / 2 + 0.06))):
                    a.box((0.32 if bx else 0.5, 0.32 if by else 0.5, 0.32),
                          loc=(cx + bx, cy + by, cz), mat=T, bevel=0.04)
            # post-top cap block poking through the roof corner (brown squares in the top view)
            frac = ph(ztop) / roof_half
            zs = (ztop - 0.2) + (1 - frac) * (apex_z - ztop + 0.2) - 0.9
            cw = pw_at(ztop) + 0.15
            a.box((cw, cw, zs - (ztop - 0.6)), loc=(sx * ph(ztop), sy * ph(ztop), (zs + ztop - 0.6) / 2),
                  mat=T, bevel=0.06)

    # horizontal cross beams: bottom, between levels, under deck
    under = deck_z - 1.0
    beam_zs = [z0 + 0.9]
    span = (under - (z0 + 0.9)) / levels
    beam_zs += [z0 + 0.9 + span * (i + 1) for i in range(levels)]
    faces = [((0, -1, 0)), ((1, 0, 0)), ((0, 1, 0)), ((-1, 0, 0))]
    for n in faces:
        nv = Vector(n)
        tv = Vector((-n[1], n[0], 0))  # along-face direction

        def fp(z, s, out=0.0):
            h = ph(z)
            off = h + post_w / 2 + out
            p = nv * off + tv * (s * h)
            return (p.x, p.y, z)

        for z in beam_zs:
            sqbeam(a, fp(z, -1.25, 0.3), fp(z, 1.25, 0.3), 1.05, 0.7, mat=T, normal=n)
        for i in range(levels):
            za, zb = beam_zs[i] + 0.3, beam_zs[i + 1] - 0.3
            broken = damaged and i == 0 and n == (1, 0, 0)
            x_brace(a, fp(za, -1, 0.5), fp(za, 1, 0.5), fp(zb, 1, 0.5), fp(zb, -1, 0.5), n,
                    w=brace_w, thick=0.5, broken=broken)

    # deck
    dh = ph(deck_z) + 1.5
    deck(a, dh, deck_z, plank_n=7)

    # railing between the roof posts
    rz = deck_z
    for side in range(4):
        if damaged and side == 1:
            continue  # missing railing section on the right
        h = ph(rz + 1)
        cs = [(-h, -h), (h, -h), (h, h), (-h, h)]
        p1, p2 = cs[side], cs[(side + 1) % 4]
        bal = 4
        if side == 0:
            # front: gap above the ladder (left of the banner)
            gx = ladder_x + 1.6
            p1 = (gx, -h)
            sqbeam(a, (gx, -h, rz), (gx, -h, rz + rail_h + 0.2), 0.7, mat=T)
            bal = 3
            if damaged:
                p2 = (gx + 2.6, -h)  # broken front rail: only a stub remains
                bal = 1
        railing_section(a, p1, p2, rz, rail_h, balusters=bal)

    # roof
    if damaged:
        roof(a, roof_half, ztop - 0.2, apex_z, torn=True)
        # bare roof rafters on the torn side, sticking up past the canvas
        sqbeam(a, (-ph(ztop), -ph(ztop), ztop), (-1.2, -0.6, apex_z + 1.4), 0.55, mat=T)
        sqbeam(a, (-ph(ztop), ph(ztop), ztop), (-1.6, 0.8, apex_z + 0.8), 0.55, mat=T)
        sqbeam(a, (-roof_half + 0.6, -0.4, ztop - 0.6), (-1.0, 0.2, apex_z + 2.0), 0.5, mat=T)
        finial(a, apex_z - 0.05, scale=1.4)
    else:
        roof(a, roof_half, ztop - 0.2, apex_z)
        finial(a, apex_z - 0.05, scale=1.4)

    # banner on the front face, in front of the braces
    by = -(ph(banner_top) + post_w / 2 + 1.05)
    banner(a, 0.0, by, banner_top, h=banner_h * (0.72 if damaged else 1.0), tattered=damaged)
    # ladder from the ground up to the deck edge, leaning, left of the banner
    ytop = -(dh + 0.25)
    ladder(a, ladder_x, ytop - 0.11 * deck_z - 0.4, ytop, deck_z)
    dressing(a, so)
    return ph


# ---------------------------------------------------------------- build
def build(kit):
    fk = kit.flintkit
    out = []

    # Hero
    a = fk.Asset("Watchtower", "W13 Watchtower")
    tower(a)
    clamp_floor(a)
    o = a.finish()
    out.append(kit.tag(o, "hero", collision="precise", budget=8000,
                       notes="Banner and ladder are in the mesh; no VFX."))

    # Variants
    a = fk.Asset("WatchtowerShort", "W13 WatchtowerShort")
    tower(a, half_b=5.2, half_t=4.6, deck_z=9.0, levels=1, roof_top=13.8, rail_h=3.2,
          roof_half=6.6, apex_z=18.8, banner_top=7.9, banner_h=4.6)
    clamp_floor(a)
    out.append(kit.tag(a.finish(), "variant", collision="precise", budget=8000,
                       notes="A. Short tower, one bracing level."))

    a = fk.Asset("WatchtowerTall", "W13 WatchtowerTall")
    tower(a, half_b=4.7, half_t=3.8, deck_z=28.0, levels=3, roof_top=33.0, rail_h=3.4,
          roof_half=6.1, apex_z=38.2, banner_top=26.6, banner_h=7.0, post_w=1.85, stone=3.3,
          ladder_x=-2.7)
    clamp_floor(a)
    out.append(kit.tag(a.finish(), "variant", collision="precise", budget=8000,
                       notes="B. Tall tower, narrower, three bracing levels."))

    a = fk.Asset("WatchtowerDamaged", "W13 WatchtowerDamaged")
    tower(a, damaged=True)
    # green leafy sack and moss tufts at the base
    a.ico((1.1, 0.9, 1.0), loc=(8.0, -3.2, 0.95), mat=M, subdiv=1, facets=8)
    a.ico((0.5, 0.5, 0.35), loc=(8.0, -3.2, 1.95), mat=M, subdiv=1)
    for (x, y) in ((5.5, -5.5), (-5.5, -5.5), (5.5, 5.5)):
        a.leaf_cluster(0.7, loc=(x, y, 2.1), mat=M, lobes=5, squash=0.5, floor=1.95)
    a.leaf_cluster(0.6, loc=(-3.0, -3.0, 23.7), mat=M, lobes=5, squash=0.5)
    clamp_floor(a)
    out.append(kit.tag(a.finish(), "variant", collision="precise", budget=8000,
                       notes="C. Damaged tower: torn roof, missing rails, broken brace, moss."))

    # Parts
    def part(name, fn, coll="box", budget=1500, notes=""):
        p = fk.Asset(name, "W13 " + name)
        fn(p)
        clamp_floor(p)
        out.append(kit.tag(p.finish(), "part", collision=coll, budget=budget, notes=notes))

    part("WatchtowerRoofTip", lambda p: finial(p, 0.0, scale=1.25), "hull")
    part("WatchtowerCanvasRoof", lambda p: roof(p, 7.0, 0.5, 5.2), "hull")

    def railing(p):
        railing_section(p, (-4, 0), (4, 0), 0.0, 3.5, balusters=4, posts=True)
    part("WatchtowerRailing", railing, "box")
    part("WatchtowerDeckFloor", lambda p: deck(p, 6.5, 1.0, thick=0.55), "precise")

    def post(p):
        sqbeam(p, (0, 0, 0), (0, 0, 15.6), 1.4, w2=1.25, mat=T)
        p.box((1.65, 1.65, 0.4), loc=(0, 0, 15.8), mat=T, bevel=0.06)
        p.box((1.7, 1.7, 0.5), loc=(0, 0, 9.0), mat=T, bevel=0.06)
    part("WatchtowerPost", post, "box")

    def bracing(p):
        x_brace(p, (-4.2, 0, 0.3), (4.2, 0, 0.3), (4.2, 0, 8.7), (-4.2, 0, 8.7), (0, -1, 0),
                w=1.0, thick=0.5)
    part("WatchtowerBracing", bracing, "hull")
    part("WatchtowerBanner", lambda p: banner(p, 0.0, 0.0, 7.0), "box")
    part("WatchtowerLadder", lambda p: ladder(p, 0.0, -1.2, 0.0, 16.6, width=2.0), "none")
    part("WatchtowerBaseStone", lambda p: base_stone(p, 0, 0, 2.6, 1.8), "box")
    return out
