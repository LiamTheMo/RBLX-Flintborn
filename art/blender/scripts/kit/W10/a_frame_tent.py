"""W10 row 2: A-frame canvas tent (hero, parts, 3 variations)."""
import math

from mathutils import Matrix, Vector

SUBJECT = "AFrameTent"
ROW = 2
HERO_AZIMUTH = -22
SIDE_AZIMUTH = -90   # the -X side: the lit canvas slope, as the reference side cell shows

PALETTE = {
    "w10_wood": ("#8A4A22", 0.85, 0, 0),
    # tent canvas: the reference tent reads paler ivory than the shared w10_canvas
    # (#E3CFA0 rendered too yellow); this module uses only this key for canvas
    "w10_tentcanvas": ("#EFE2C4", 0.95, 0, 0),
    "w10_rope": ("#C48A38", 0.8, 0, 0),
    "w10_stone": ("#9A9498", 0.9, 0, 0),
    "w10_iron": ("#575B64", 0.5, 0.4, 0),
    "w10_lantern": ("#FFB022", 0.4, 0, 2),
    "w10_bedroll": ("#2C6A52", 0.95, 0, 0),
}

WOOD, CANVAS, ROPE, STONE = "w10_wood", "w10_tentcanvas", "w10_rope", "w10_stone"
IRON, GLASS, BED = "w10_iron", "w10_lantern", "w10_bedroll"

W = 4.1      # canvas half width at the ground
ZB = 0.2     # canvas bottom edge height
ZT = 7.95    # canvas apex height
YE = 6.4     # canvas half length
PF = 4.5     # pole foot half spread
YP = 6.55    # A-frame plane (|y|)
ZC = 7.5     # pole crossing height
ZR = 7.85    # ridge pole centre height
ZTIP = 8.45  # pole tip height
PR = 0.4     # pole radius
L = math.hypot(W, ZT - ZB)
GLOW = ["#FFB022", "#FF8A1E"]


def _rot_to(d):
    return Vector(d).to_track_quat("Z", "Y").to_euler()


# ---------------------------------------------------------------- pieces

def pole(a, s, y, foot_shift=(0.0, 0.0)):
    """One A-frame pole from its foot (side s) through the crossing to the tip."""
    foot = Vector((s * PF + foot_shift[0], y + foot_shift[1], 0.3))
    cross = Vector((0.0, y, ZC))
    d = cross - foot
    tip = foot + d * ((ZTIP - foot.z) / d.z)
    a.beam(foot, tip, PR, sides=7, mat=WOOD, end_mat=ROPE)
    a.box((0.85, 0.85, 0.45), loc=(foot.x, foot.y, 0), mat=WOOD, base=True, jitter=0.03)
    # rope tie on the lower pole where the canvas edge is lashed
    p = foot + d * 0.25
    a.torus(PR + 0.07, 0.09, loc=p, rot=_rot_to(d), mat=ROPE, seg=8, rseg=3)


def frame_end(a, y, lean=False):
    sh = (1.3, -0.9) if lean else (0.0, 0.0)
    pole(a, 1, y + 0.2 * (1 if y < 0 else -1), sh)
    pole(a, -1, y - 0.2 * (1 if y < 0 else -1))
    a.lashing((0, y, ZC), size=0.6, thickness=0.12, mat=ROPE)


def ridge(a, y0, y1, z):
    a.beam((0, y0, z), (0, y1, z), 0.45, sides=8, mat=WOOD, end_mat=ROPE)


def ridge_wraps(a, ys, z):
    for y in ys:
        a.torus(0.53, 0.09, loc=(0, y, z), rot=(math.pi / 2, 0, 0), mat=ROPE, seg=8, rseg=3)


def panel_matrix(s, off=0.0, w=W, h=None, zb=ZB):
    h = ZT - ZB if h is None else h
    d = Vector((-s * w, 0, h)).normalized()
    n = Vector((s * h, 0, w)).normalized()
    e1 = Vector((0, s, 0))
    base = Vector((s * w, 0, zb)) + n * off
    m = Matrix((
        (e1.x, d.x, n.x, base.x),
        (e1.y, d.y, n.y, base.y),
        (e1.z, d.z, n.z, base.z),
        (0, 0, 0, 1)))
    return m


def panel_piece(a, s, pts, depth=0.15, off=0.0, mat=CANVAS, **geo):
    """Polygon on a sloped panel; pts are (world y, distance up the slope), CCW."""
    loc = [(s * y, u) for y, u in pts]
    if s < 0:
        loc.reverse()
    vs = a.poly_prism(loc, depth, mat=mat)
    m = panel_matrix(s, off, **geo)
    for v in vs:
        v.co = m @ v.co
    return vs


_panel_piece = panel_piece


def panel(a, s, y0=-YE, y1=YE):
    panel_piece(a, s, [(y0, 0), (y1, 0), (y1, L), (y0, L)])


def tri_end(a, pts, y, depth=0.12, mat=CANVAS):
    """Canvas polygon in the XZ plane at y (extruded toward -y)."""
    a.poly_prism(pts, depth, loc=(0, y, 0), rot=(math.pi / 2, 0, 0), mat=mat)


def edge_ties(a, s, ys):
    for y in ys:
        a.tube_loop([(s * (W + 0.05), y, ZB + 0.15), (s * (W + 0.75), y, 0.06)], 0.07,
                    mat=ROPE, rseg=4, closed=False)


def peg(a, x, y, guy_to=None):
    a.cyl(0.24, 0.16, 1.0, sides=6, loc=(x, y, 0), mat=WOOD)
    a.cyl(0.3, 0.26, 0.22, sides=6, loc=(x, y, 1.0), mat=WOOD)      # peg head
    a.torus(0.36, 0.08, loc=(x, y, 0.8), mat=ROPE, seg=8, rseg=3)
    # rope loop standing up from the peg
    a.torus(0.36, 0.08, loc=(x, y - 0.5, 0.72), rot=(0, math.pi / 2, 0), mat=ROPE, seg=8, rseg=3)
    if guy_to is not None:
        a.tube_loop([(x, y, 0.9), guy_to], 0.05, mat=ROPE, rseg=4, closed=False)


def lantern(a, x, y, z, hang_from=None, k=1.35):
    """Iron lantern centred at (x, y, z); optional rope up to hang_from."""
    a.cyl(0.36 * k, 0.36 * k, 0.12 * k, sides=6, loc=(x, y, z - 0.47 * k), mat=IRON)
    a.cyl(0.27 * k, 0.27 * k, 0.72 * k, sides=6, loc=(x, y, z - 0.36 * k), mat=GLASS)
    a.cyl(0.4 * k, 0.1 * k, 0.34 * k, sides=6, loc=(x, y, z + 0.36 * k), mat=IRON)
    for dx in (-1, 1):   # side bars of the frame
        a.box((0.07 * k, 0.07 * k, 0.72 * k), loc=(x + dx * 0.27 * k, y - 0.05, z - 0.36 * k),
              mat=IRON, base=True)
    a.torus(0.14 * k, 0.04 * k, loc=(x, y, z + 0.8 * k), rot=(math.pi / 2, 0, 0), mat=IRON,
            seg=6, rseg=3)
    if hang_from is not None:
        a.tube_loop([(x, y, z + 0.92 * k), hang_from], 0.05, mat=ROPE, rseg=4, closed=False)


def crate(a, cx, cy, s=1.6, rz=0.0):
    vs = []
    h = s
    vs += a.box((s * 0.9, s * 0.9, h * 0.94), loc=(0, 0, 0.03 * h), mat=WOOD, base=True)
    e = 0.22
    for sx in (-1, 1):
        for sy in (-1, 1):
            vs += a.box((e, e, h), loc=(sx * (s - e) / 2, sy * (s - e) / 2, 0), mat=WOOD,
                        base=True, jitter=0.02)
    for z in (0.0, h - e):
        for sy in (-1, 1):
            vs += a.box((s - 2 * e, e, e), loc=(0, sy * (s - e) / 2, z), mat=WOOD, base=True)
            vs += a.box((e, s - 2 * e, e), loc=(sy * (s - e) / 2, 0, z), mat=WOOD, base=True)
    a.transform(vs, (cx, cy, 0), (0, 0, rz))


def barrel(a, cx, cy, k=1.0):
    a.cyl(0.62 * k, 0.72 * k, 0.9 * k, sides=10, loc=(cx, cy, 0), mat=WOOD)
    a.cyl(0.72 * k, 0.62 * k, 0.9 * k, sides=10, loc=(cx, cy, 0.9 * k), mat=WOOD)
    a.cyl(0.56 * k, 0.56 * k, 0.06, sides=10, loc=(cx, cy, 1.8 * k), mat=ROPE)
    for z, r in ((0.3, 0.68), (0.9, 0.74), (1.5, 0.68)):
        a.torus(r * k, 0.07, loc=(cx, cy, z * k), mat=IRON, seg=10, rseg=3, squash=1.4)


def stone(a, x, y, sz=0.55, rz=0.4):
    a.box((sz, sz * 0.9, sz * 0.8), loc=(x, y, 0), rot=(0, 0, rz), mat=STONE, base=True,
          jitter=0.05)


def mat_set(a, cx=0.0, cy=0.4):
    """Tan woven mat 5x7x0.4, green blanket, rolled bedroll."""
    a.box((5.0, 7.0, 0.4), loc=(cx, cy, 0), mat=ROPE, base=True)
    for dx in (-2.35, 2.35):
        a.box((0.3, 7.0, 0.06), loc=(cx + dx, cy, 0.4), mat=WOOD, base=True)
    for i in range(4):  # weave ribs
        a.box((4.4, 0.12, 0.05), loc=(cx, cy + 1.0 + i * 0.7, 0.4), mat=WOOD, base=True)
    a.box((4.2, 3.4, 0.12), loc=(cx, cy - 1.7, 0.4), mat=BED, base=True)
    # bedroll lying across, on the blanket
    r, ln = 0.8, 4.0
    a.cyl(r, r, ln, sides=10, loc=(cx - ln / 2, cy - 0.6, 0.52 + r), rot=(0, math.pi / 2, 0),
          mat=BED)
    for dx in (-ln / 2 - 0.02, ln / 2 - 0.04):
        a.cyl(r * 0.8, r * 0.8, 0.06, sides=10, loc=(cx + dx, cy - 0.6, 0.52 + r),
              rot=(0, math.pi / 2, 0), mat=CANVAS)
    for dx in (-1.1, 1.1):
        a.torus(r + 0.04, 0.07, loc=(cx + dx, cy - 0.6, 0.52 + r), rot=(0, math.pi / 2, 0),
                mat=ROPE, seg=10, rseg=3)


def canvas_roll(a, x0, x1, y, z, r=0.45):
    a.cyl(r, r, x1 - x0, sides=8, loc=(x0, y, z), rot=(0, math.pi / 2, 0), mat=CANVAS)
    for f in (0.25, 0.75):
        a.torus(r + 0.04, 0.07, loc=(x0 + (x1 - x0) * f, y, z), rot=(0, math.pi / 2, 0),
                mat=ROPE, seg=8, rseg=3)


def tent_core(a, front="open", lean=False, torn=False):
    frame_end(a, -YP, lean=lean)
    frame_end(a, YP)
    ridge(a, -YP - 0.9, YP + 0.9, ZR)
    ridge_wraps(a, (-YP + 0.7, YP - 0.7), ZR)
    panel(a, 1)
    if torn:
        torn_panel(a)
    else:
        panel(a, -1)
    tri_end(a, [(-W, ZB), (W, ZB), (0, ZT - 0.1)], YE + 0.12)   # closed back
    top = (0, ZT - 0.1)
    if front == "open":
        tri_end(a, [(-W, ZB), (-2.6, ZB), top], -YE)
        tri_end(a, [(2.6, ZB), (W, ZB), top], -YE)
    elif front == "closed":
        tri_end(a, [(-W, ZB), (W, ZB), top], -YE)
        tri_end(a, [(-W, ZB), (0.35, ZB), top], -YE - 0.12)          # overlapping flap
        for z in (1.4, 3.0, 4.6):
            xw = 0.35 * (1 - (z - ZB) / (ZT - ZB))
            a.tube_loop([(xw - 0.45, -YE - 0.3, z), (xw + 0.45, -YE - 0.3, z - 0.08)], 0.07,
                        mat=ROPE, rseg=4, closed=False)
    elif front == "rolled":
        zr = 5.4
        tri_end(a, [(-W, ZB), (-3.2, ZB), top], -YE)
        tri_end(a, [(3.2, ZB), (W, ZB), top], -YE)
        hw = W * (1 - (zr - ZB) / (ZT - ZB))
        tri_end(a, [(-hw, zr), (hw, zr), top], -YE)
        canvas_roll(a, -hw - 0.4, hw + 0.4, -YE - 0.45, zr)
    edge_ties(a, 1 if not torn else 1, (-4.8, -1.6, 1.6, 4.8))
    edge_ties(a, -1, (-4.8, -1.6, 1.6, 4.8))
    for sx in (-1, 1):
        for sy in (-1, 1):
            peg(a, sx * 5.4, sy * 7.5, guy_to=(sx * PF * 0.72, sy * (YP + 0.1), 2.2))


def torn_panel(a, s=-1, yc=-2.6):
    """Ragged hole centred at y=yc on panel s (the side the variant camera sees)."""
    def panel_piece(a, s, pts, **kw):
        sh = [(y if abs(y) == YE else y + yc, u) for y, u in pts]
        return _panel_piece(a, s, sh, **kw)
    panel_piece(a, s, [(-YE, 0), (YE, 0), (YE, 3.5), (1.4, 3.5), (1.1, 3.9), (0.8, 3.4),
                       (0.5, 4.3), (0.2, 3.6), (-0.2, 4.0), (-0.5, 3.3), (-0.8, 4.4),
                       (-1.1, 3.6), (-1.6, 3.5), (-YE, 3.5)])
    panel_piece(a, s, [(-YE, 6.2), (-1.6, 6.2), (-1.3, 5.4), (-1.0, 6.0), (-0.6, 5.2),
                       (-0.3, 5.9), (0.1, 5.1), (0.4, 5.8), (0.8, 5.3), (1.1, 6.0), (1.4, 6.2),
                       (YE, 6.2), (YE, L), (-YE, L)])
    panel_piece(a, s, [(-YE, 3.5), (-1.6, 3.5), (-2.0, 4.0), (-1.5, 4.4), (-2.2, 4.9),
                       (-1.6, 5.3), (-1.9, 5.8), (-1.6, 6.2), (-YE, 6.2)])
    panel_piece(a, s, [(1.4, 3.5), (YE, 3.5), (YE, 6.2), (1.4, 6.2), (1.8, 5.7), (1.3, 5.2),
                       (2.0, 4.6), (1.4, 4.1), (1.7, 3.8)])
    # scorched / worn patches around the hole edge
    for pts in ([(-2.4, 3.9), (-1.7, 3.3), (-1.4, 4.3)],
                [(-2.5, 5.2), (-1.8, 4.7), (-1.6, 5.9)],
                [(0.9, 3.2), (1.9, 3.4), (1.4, 4.0)],
                [(1.6, 5.0), (2.3, 5.6), (1.5, 6.5)],
                [(-0.6, 6.0), (0.5, 5.9), (0.0, 6.6)],
                [(-0.3, 3.0), (0.6, 3.1), (0.2, 3.6)]):
        panel_piece(a, s, pts, depth=0.04, off=0.15, mat=WOOD)
    # frayed strips hanging into the hole
    for y, u0, u1 in ((-1.2, 5.6, 4.5), (-0.45, 5.4, 4.2), (0.25, 5.3, 4.5), (0.95, 5.5, 4.7),
                      (-0.65, 3.6, 4.5), (0.6, 3.7, 4.3)):
        panel_piece(a, s, [(y - 0.13, u1), (y + 0.13, u1), (y + 0.16, u0), (y - 0.16, u0)],
                    depth=0.05, off=-0.06)


def finish(a):
    xs = [v.co.x for v in a.bm.verts]
    ys = [v.co.y for v in a.bm.verts]
    zs = [v.co.z for v in a.bm.verts]
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    return a.finish(), off


def glow(vfx, o, off, p):
    vfx.add(o, "heat_glow", tuple(Vector(p) - off), scale=0.6, color=GLOW)


# ---------------------------------------------------------------- build

def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []
    front_lantern = (0, -YP - 0.35, 5.3)
    hang = (0, -YP - 0.35, ZC - 0.35)

    # HERO -----------------------------------------------------------
    a = fk.Asset("AFrameTent", "W10 AFrameTent")
    tent_core(a, "open")
    mat_set(a)
    lantern(a, *front_lantern, hang_from=hang)
    canvas_roll(a, 1.2, 2.9, -YP - 0.75, 4.2)
    crate(a, -5.7, -7.9, 1.9, 0.15)
    barrel(a, -3.4, -8.4, 1.15)
    ground_l = (-1.9, -9.0, 0.75)
    lantern(a, *ground_l)
    crate(a, 5.3, 2.8, 1.4, -0.2)
    for x, y, sz, rz in ((-6.0, -6.3, 0.55, 0.3), (-1.0, -8.6, 0.45, 0.9), (-6.6, -9.1, 0.45, 0.2),
                         (5.6, -5.6, 0.5, 0.6), (5.0, 5.2, 0.45, 1.1)):
        stone(a, x, y, sz, rz)
    o, off = finish(a)
    glow(vfx, o, off, front_lantern)
    glow(vfx, o, off, ground_l)
    out.append(kit.tag(o, "hero", collision="precise", budget=4500,
                       notes="Open-front A-frame tent, walkable interior. heat_glow sockets: "
                             "hanging lantern at the front crossing and ground lantern by the barrel."))

    # PARTS ----------------------------------------------------------
    a = fk.Asset("AFrameTentRidgePole", "W10 AFrameTent part")
    a.beam((0, -6.5, 0.45), (0, 6.5, 0.45), 0.45, sides=8, mat=WOOD, end_mat=ROPE)
    ridge_wraps(a, (-5.6, -5.2, 5.2, 5.6), 0.45)
    o, _ = finish(a)
    out.append(kit.tag(o, "part", collision="hull", budget=1500, notes="Ridge pole with rope wraps."))

    for name, s in (("AFrameTentCanvasPanelLeft", -1), ("AFrameTentCanvasPanelRight", 1)):
        a = fk.Asset(name, "W10 AFrameTent part")
        # flat 9.5 x 14 sheet, reclined 48 deg with its face to the parts camera: the
        # grid then sets the two panels side by side in the back row, as two separate
        # hanging sheets like the reference's exploded view
        vs = a.poly_prism([(-4.75, 0), (4.75, 0), (4.75, 14.0), (-4.75, 14.0)], 0.15, mat=CANVAS)
        # rope-tie eyelets along the bottom (outer long) edge
        for y in (1.2, 3.5, 5.8, 8.1, 10.4, 12.7):
            vs += a.torus(0.26, 0.08, loc=(s * 4.55, y, 0.16), mat=ROPE, seg=8, rseg=3)
        # hem rope along the top (ridge) edge
        vs += a.tube_loop([(-s * 4.6, 0.3, 0.2), (-s * 4.6, 13.7, 0.2)], 0.09, mat=ROPE, rseg=4,
                          closed=False)
        a.transform(vs, loc=(0, 0, 0.12), rot=(math.radians(48), 0, 0))
        o, _ = finish(a)
        out.append(kit.tag(o, "part", collision="hull", budget=1500,
                           notes="Sloped canvas panel with rope ties along the bottom edge."))

    a = fk.Asset("AFrameTentFrameEnd", "W10 AFrameTent part")
    frame_end(a, 0.0001)
    o, _ = finish(a)
    out.append(kit.tag(o, "part", collision="precise", budget=1500,
                       notes="Crossed-pole A-frame end with lashing and foot blocks (used 2x)."))

    a = fk.Asset("AFrameTentMat", "W10 AFrameTent part")
    mat_set(a, 0, 0)
    o, _ = finish(a)
    out.append(kit.tag(o, "part", collision="box", budget=1500,
                       notes="Woven tent mat with green blanket and rolled bedroll."))

    a = fk.Asset("AFrameTentPeg", "W10 AFrameTent part")
    peg(a, 0, 0)
    o, _ = finish(a)
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="Tent peg with rope loop (used 4x)."))

    # VARIATIONS -----------------------------------------------------
    a = fk.Asset("AFrameTentClosed", "W10 AFrameTent variant")
    tent_core(a, "closed")
    left_l = (-2.9, -YP - 0.6, 4.2)
    lantern(a, *left_l, hang_from=(-2.9, -YP - 0.3, 5.4))
    a.beam((-2.2, -YP - 0.2, 5.5), (-3.1, -YP - 0.6, 5.5), 0.08, sides=5, mat=IRON, end_mat=IRON)
    stone(a, -5.6, -7.9, 0.5, 0.4)
    stone(a, 5.4, -8.6, 0.45, 1.0)
    o, off = finish(a)
    glow(vfx, o, off, left_l)
    out.append(kit.tag(o, "variant", collision="precise", budget=3000,
                       notes="Front flap lowered and tied shut. heat_glow socket: lantern on the "
                             "left of the front."))

    a = fk.Asset("AFrameTentRolledDoorway", "W10 AFrameTent variant")
    tent_core(a, "rolled")
    mat_set(a)
    fl = (0, -YP - 0.35, 4.1)
    lantern(a, *fl, hang_from=hang)
    stone(a, -5.8, -8.6, 0.5, 0.4)
    o, off = finish(a)
    glow(vfx, o, off, fl)
    out.append(kit.tag(o, "variant", collision="precise", budget=3000,
                       notes="Front flap rolled up over the doorway, mat and bedroll inside. "
                             "heat_glow socket: hanging lantern at the front crossing."))

    a = fk.Asset("AFrameTentTornWorn", "W10 AFrameTent variant")
    tent_core(a, "open", lean=True, torn=True)
    mat_set(a)
    stone(a, -5.8, -8.6, 0.5, 0.4)
    stone(a, 6.6, -6.2, 0.45, 1.0)
    o, _ = finish(a)
    out.append(kit.tag(o, "variant", collision="precise", budget=3000,
                       notes="Torn, worn tent: ragged hole in the camera-facing (-X) panel with worn patches and "
                             "frayed strips, front-right pole leaning. No lantern, no VFX."))
    return out
