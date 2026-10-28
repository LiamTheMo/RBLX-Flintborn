"""W11 row 4: DailyItems (A-frame rack with awning, shelf goods, sack) + parts + variants."""
import math

from mathutils import Vector

SUBJECT = "DailyItems"
ROW = 4
HERO_AZIMUTH = -22
SIDE_AZIMUTH = -90

PALETTE = {
    "w11_wood": ("#B5702C", 0.9, 0, 0),
    "w11_iron": ("#40444F", 0.6, 0.3, 0),
    "w11_rope": ("#C99A55", 1, 0, 0),
    "w11_cloth": ("#E8D3A8", 1, 0, 0),
    "w11_red": ("#C0352E", 1, 0, 0),
    "w11_blue": ("#3E6DB4", 0.7, 0, 0),
    "w11_clay": ("#D0683A", 0.75, 0, 0),
    "w11_green": ("#5B7A38", 1, 0, 0),
}

WOOD, IRON, ROPE, CLOTH, RED, BLUE, CLAY, GREEN = (
    "w11_wood", "w11_iron", "w11_rope", "w11_cloth", "w11_red", "w11_blue", "w11_clay", "w11_green")
AX = (0, math.pi / 2, 0)   # rotate Z-axis primitives onto X
AY = (math.pi / 2, 0, 0)   # rotate Z-axis primitives onto -Y


# ---------------------------------------------------------------- helpers

def bar(a, p1, p2, w, d=None, mat=WOOD, bevel=0.05, jitter=0.02):
    """Square plank-post between two points (w across x-ish, d across the other)."""
    p1, p2 = Vector(p1), Vector(p2)
    v = p2 - p1
    rot = v.to_track_quat("Z", "Y").to_euler()
    return a.box((w, d or w, v.length), loc=(p1 + p2) / 2, rot=tuple(rot), mat=mat,
                 bevel=bevel, jitter=jitter)


def lathe(a, profile, mat, sides=10, loc=(0, 0, 0), rot=(0, 0, 0), jitter=0.0):
    """Surface of revolution from (r, z) points, bottom to top. r=0 points collapse to a pole."""
    bm = a.bm
    rings = []
    for r, z in profile:
        if r < 1e-4:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / sides),
                                        r * math.sin(2 * math.pi * i / sides), z))
                          for i in range(sides)])
    for k in range(len(rings) - 1):
        lo, hi = rings[k], rings[k + 1]
        for i in range(sides):
            j = (i + 1) % sides
            if len(lo) == 1 and len(hi) == 1:
                continue
            if len(lo) == 1:
                bm.faces.new((lo[0], hi[j], hi[i]))
            elif len(hi) == 1:
                bm.faces.new((lo[i], lo[j], hi[0]))
            else:
                bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    verts = [v for ring in rings for v in ring]
    a.transform(verts, loc, rot)
    return a._finish(verts, mat, None, jitter)


def nail(a, loc):
    a.cyl(0.09, 0.09, 0.06, sides=6, loc=loc, rot=AY, mat=IRON)


def rack_side(a, sx, h=6.2, foot=1.65, tip=0.2, w=0.42):
    """One A-frame side: two splayed posts crossing near the top, plus a low side rail."""
    bar(a, (sx - 0.21, -foot, 0), (sx - 0.21, tip, h), w)
    bar(a, (sx + 0.21, foot, 0), (sx + 0.21, -tip, h), w)
    zr = 1.0
    yr = foot * (1 - zr / h * (1 + tip / foot)) + 0.25
    bar(a, (sx, -yr, zr), (sx, yr, zr), 0.36, 0.4)


def rope_wraps(a, xs, z, r=0.44, y=0.0):
    for x in xs:
        a.torus(r, 0.08, loc=(x, y, z), rot=AX, mat=ROPE, seg=10, rseg=4)


def jug(a, loc=(0, 0, 0), s=1.0):
    x, y, z = loc
    prof = [(0, 0), (0.42, 0), (0.6, 0.3), (0.65, 0.65), (0.6, 0.95), (0.36, 1.22),
            (0.25, 1.38), (0.3, 1.58), (0.22, 1.6), (0, 1.5)]
    lathe(a, [(r * s, h * s) for r, h in prof], CLAY, sides=10, loc=loc)
    lathe(a, [(0.62 * s, 0.5 * s), (0.69 * s, 0.55 * s), (0.69 * s, 0.82 * s), (0.62 * s, 0.88 * s)],
          BLUE, sides=10, loc=loc)
    pts = [(x + 0.32 * s, y, z + 1.38 * s), (x + 0.68 * s, y, z + 1.35 * s),
           (x + 0.8 * s, y, z + 1.05 * s), (x + 0.62 * s, y, z + 0.8 * s)]
    a.tube_loop(pts, 0.07 * s, mat=CLAY, rseg=4, closed=False)


def pot(a, loc=(0, 0, 0), s=1.0, mat=CLAY):
    """Small round clay pot with an open mouth."""
    prof = [(0, 0), (0.32, 0), (0.5, 0.2), (0.53, 0.42), (0.42, 0.62), (0.4, 0.7),
            (0.32, 0.7), (0.3, 0.6), (0, 0.6)]
    lathe(a, [(r * s, h * s) for r, h in prof], mat, sides=10, loc=loc)


def bowl(a, loc=(0, 0, 0), s=1.0):
    prof = [(0, 0), (0.3, 0), (0.48, 0.3), (0.55, 0.6), (0.47, 0.6), (0.4, 0.33),
            (0.24, 0.14), (0, 0.14)]
    lathe(a, [(r * s, h * s) for r, h in prof], CLAY, sides=10, loc=loc)


def rolled_mat(a, x0, x1, y, z, r=0.6):
    """Green roll lying along X with base at z; two rope ties."""
    L = x1 - x0
    a.cyl(r, r, L, sides=10, loc=(x0, y, z + r), rot=AX, mat=GREEN, jitter=0.02)
    # loose outer flap along the front
    a.box((L * 0.96, 0.08, 0.55), loc=(x0 + L / 2, y - r * 0.92, z + r * 0.55),
          rot=(0.25, 0, 0), mat=GREEN, bevel=0.02)
    rope_wraps(a, (x0 + L * 0.22, x1 - L * 0.22), z + r, r=r + 0.03, y=y)


def sack(a, loc=(0, 0, 0), s=1.0, lean=0.0):
    x, y, z = loc
    v = a.ico((1.0 * s, 0.9 * s, 0.85 * s), loc=(x, y, z + 0.85 * s), mat=CLOTH, subdiv=2,
              jitter=0.06 * s)
    for vv in v:
        if vv.co.z < z:
            vv.co.z = z
    a.cyl(0.55 * s, 0.22 * s, 0.6 * s, sides=8, loc=(x + lean * s, y, z + 1.45 * s), mat=CLOTH)
    a.cyl(0.2 * s, 0.45 * s, 0.55 * s, sides=8, loc=(x + lean * 1.4 * s, y, z + 1.95 * s),
          mat=CLOTH, jitter=0.05 * s)
    a.torus(0.25 * s, 0.07 * s, loc=(x + lean * 1.2 * s, y, z + 1.95 * s), mat=RED, seg=10)
    for sgn in (-1, 1):
        a.box((0.14 * s, 0.05 * s, 0.6 * s),
              loc=(x + lean * 1.2 * s + sgn * 0.18 * s, y - 0.27 * s, z + 1.7 * s),
              rot=(0.15, sgn * 0.35, 0), mat=RED, bevel=0.01)


def ribbon(a, x, y, ztop, length=2.1):
    a.ico(0.14, loc=(x, y, ztop), mat=RED, subdiv=1)
    a.box((0.26, 0.05, length), loc=(x, y - 0.03, ztop - length / 2), rot=(0.05, 0, 0.1),
          mat=RED, bevel=0.01)
    a.box((0.22, 0.05, length * 0.8), loc=(x + 0.12, y - 0.06, ztop - length * 0.4),
          rot=(0.05, 0.12, -0.1), mat=RED, bevel=0.01)


def awning(a, beam_z, width=4.3, drop=1.1, point=2.0):
    """Cloth over the beam: top cover + front and back panels with a V hem."""
    hw = width / 2
    a.box((width, 0.9, 0.12), loc=(0, 0, beam_z + 0.38), mat=CLOTH, bevel=0.03)
    pts = [(-hw, -drop), (-hw * 0.5, -drop - (point - drop) * 0.55), (0, -point),
           (hw * 0.5, -drop - (point - drop) * 0.55), (hw, -drop), (hw, 0), (-hw, 0)]
    # front panel (extrudes toward -Y), bottom tilts forward
    a.poly_prism(pts, 0.12, loc=(0, -0.42, beam_z + 0.42), rot=(math.pi / 2 - 0.06, 0, 0), mat=CLOTH)
    # back panel, shorter
    pts_b = [(-hw, -drop * 0.9), (0, -point * 0.8), (hw, -drop * 0.9), (hw, 0), (-hw, 0)]
    a.poly_prism(pts_b, 0.12, loc=(0, 0.54, beam_z + 0.42), rot=(math.pi / 2 + 0.06, 0, 0), mat=CLOTH)


# ---------------------------------------------------------------- assets

def build_hero(kit):
    fk = kit.flintkit
    a = fk.Asset("DailyItems", "W11 DailyItems", seed=411)
    SX = 2.75
    for sx in (-SX, SX):
        rack_side(a, sx)
    beam_z = 5.7
    bar(a, (-3.3, 0, beam_z), (3.3, 0, beam_z), 0.7)
    rope_wraps(a, (-SX - 0.5, -SX + 0.5, SX - 0.5, SX + 0.5), beam_z)
    for sx in (-SX, SX):
        a.lashing((sx, 0, beam_z), size=0.45, rot=(0, 0, math.pi / 2), mat=ROPE)
    awning(a, beam_z)
    for sx in (-2.35, 2.35):
        ribbon(a, sx, -0.45, beam_z + 0.1)
    # shelf + brace
    a.plank((6.0, 2.6, 0.5), loc=(0, 0, 1.3), mat=WOOD)
    bar(a, (-2.5, -0.5, 0.65), (2.5, -0.5, 0.65), 0.5, 0.6)
    for x in (-2.75, -1.0, 1.0, 2.75):
        nail(a, (x, -1.31, 1.3))
    top = 1.55
    jug(a, (-1.55, -0.5, top))
    pot(a, (-0.25, -0.6, top), s=1.05)
    rolled_mat(a, 0.5, 3.5, -0.45, top)
    sack(a, (-4.0, -0.9, 0), s=1.2, lean=0.12)
    o = a.finish()
    return kit.tag(o, "hero", collision="precise", budget=5000,
                   notes="A-frame market rack with cloth awning, shelf goods and sack. No VFX.")


def build_parts(kit):
    fk = kit.flintkit
    out = []

    a = fk.Asset("DailyItemsRackSide", "W11 DailyItems part", seed=1)
    rack_side(a, 0)
    a.lashing((0, 0, 5.55), size=0.4, rot=(0, 0, math.pi / 2), mat=ROPE)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="One A-frame side."))

    a = fk.Asset("DailyItemsTopBeam", "W11 DailyItems part", seed=2)
    bar(a, (-3, 0, 0.35), (3, 0, 0.35), 0.7)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Top beam."))

    a = fk.Asset("DailyItemsSupportBrace", "W11 DailyItems part", seed=3)
    bar(a, (-2.5, 0, 0.3), (2.5, 0, 0.3), 0.5, 0.6)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Shelf brace."))

    a = fk.Asset("DailyItemsShelfPlanks", "W11 DailyItems part", seed=4)
    a.plank((6.0, 2.6, 0.5), loc=(0, 0, 0.25), mat=WOOD)
    for x in (-2.75, -1.0, 1.0, 2.75):
        nail(a, (x, -1.31, 0.25))
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Shelf board."))

    a = fk.Asset("DailyItemsSack", "W11 DailyItems part", seed=5)
    sack(a, (0, 0, 0), s=1.0)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=800, notes="Cloth sack, red tie."))

    a = fk.Asset("DailyItemsJug", "W11 DailyItems part", seed=6)
    jug(a, (0, 0, 0), s=1.06)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=800, notes="Clay jug, blue band."))

    a = fk.Asset("DailyItemsBowl", "W11 DailyItems part", seed=7)
    bowl(a, (0, 0, 0))
    out.append(kit.tag(a.finish(), "part", collision="box", budget=800, notes="Open clay bowl."))

    a = fk.Asset("DailyItemsRolledMat", "W11 DailyItems part", seed=8)
    rolled_mat(a, -1.5, 1.5, 0, 0)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=800, notes="Green rolled mat."))
    return out


def build_open_shelf(kit):
    a = kit.flintkit.Asset("DailyItemsOpenShelf", "W11 DailyItems variant", seed=21)
    px, py = 2.25, 0.95
    for x in (-px, px):
        for y in (-py, py):
            bar(a, (x, y, 0), (x, y, 4.5), 0.4)
    for z in (1.2, 3.6):
        a.plank((5.0, 2.4, 0.35), loc=(0, 0, z), mat=WOOD)
        for x in (-px, px):
            bar(a, (x, -py - 0.05, z - 0.4), (x, py + 0.05, z - 0.4), 0.32, 0.3)
            nail(a, (x, -py - 0.21, z))
            nail(a, (x, -py - 0.21, z - 0.4))
    a.plank((4.2, 0.3, 0.3), loc=(0, py, 2.4), mat=WOOD)
    top = 1.2 + 0.175
    jug(a, (-1.2, 0, top), s=0.85)
    pot(a, (0.2, -0.1, top), s=1.0)
    bowl(a, (1.35, -0.1, top), s=0.85)
    return kit.tag(a.finish(), "variant", collision="precise", budget=3000,
                   notes="Open two-shelf unit with jug and pots.")


def build_log_rack(kit):
    a = kit.flintkit.Asset("DailyItemsLogRack", "W11 DailyItems variant", seed=22)
    for y in (-1.0, 1.0):
        bar(a, (-2.6, y, 0.3), (2.6, y, 0.3), 0.5)
    for sx in (-2.45, 2.45):
        sg = 1 if sx > 0 else -1
        bar(a, (sx - 0.18, -1.2, 0), (sx - 0.18 + sg * 0.3, 0.25, 3.6), 0.38)
        bar(a, (sx + 0.18, 1.2, 0), (sx + 0.18 + sg * 0.3, -0.25, 3.6), 0.38)
        a.lashing((sx + sg * 0.25, 0, 3.05), size=0.35, rot=(0, 0, math.pi / 2), mat=ROPE)
    r = 0.5
    rows = [((-1.5, -0.5, 0.5, 1.5), 0.55 + r),
            ((-1.0, 0.0, 1.0), 0.55 + r + 0.87),
            ((-0.5, 0.5), 0.55 + r + 1.74)]
    for xs, zc in rows:
        for x in xs:
            a.cyl(r * 0.97, r * 0.97, 2.6, sides=8, loc=(x, 1.3, zc), rot=AY, mat=WOOD, jitter=0.03)
    return kit.tag(a.finish(), "variant", collision="precise", budget=3000,
                   notes="Low log rack with crossed end posts holding 9 logs.")


def build_tool_stand(kit):
    a = kit.flintkit.Asset("DailyItemsToolStand", "W11 DailyItems variant", seed=23)
    SX = 2.2
    for sx in (-SX, SX):
        rack_side(a, sx, h=7.0, foot=1.4, tip=0.2)
    bz = 6.5
    bar(a, (-2.7, 0, bz), (2.7, 0, bz), 0.5)
    rope_wraps(a, (-SX - 0.4, SX + 0.4), bz, r=0.33)
    # green cloth strap folded over the bar
    a.box((0.4, 0.08, 1.9), loc=(-1.1, -0.3, bz - 0.85), rot=(0.05, 0, 0), mat=GREEN, bevel=0.02)
    a.box((0.4, 0.08, 1.4), loc=(-1.1, 0.3, bz - 0.6), rot=(-0.05, 0, 0), mat=GREEN, bevel=0.02)
    a.box((0.42, 0.7, 0.1), loc=(-1.1, 0, bz + 0.28), mat=GREEN, bevel=0.02)
    # two axe-like tools hanging from hooks
    for x, ln in ((-0.2, 2.0), (0.6, 1.7)):
        a.torus(0.16, 0.04, loc=(x, 0, bz - 0.25), rot=AY, mat=IRON, seg=8)
        a.cyl(0.08, 0.08, ln, sides=6, loc=(x, 0, bz - 0.4 - ln), mat=WOOD)
        a.box((0.5, 0.12, 0.32), loc=(x + 0.2, 0, bz - 0.4 - ln + 0.1), mat=IRON, bevel=0.03)
    # second strap (green cloth)
    a.box((0.32, 0.08, 1.3), loc=(1.35, -0.3, bz - 0.55), mat=GREEN, bevel=0.02)
    a.box((0.34, 0.65, 0.1), loc=(1.35, 0, bz + 0.27), mat=GREEN, bevel=0.02)
    # bucket at base right
    bx, by = 1.0, -0.2
    lathe(a, [(0, 0), (0.75, 0), (0.9, 1.6), (0.78, 1.6), (0.66, 0.15), (0, 0.15)],
          WOOD, sides=12, loc=(bx, by, 0), jitter=0.01)
    for z0 in (0.3, 1.2):
        r0 = 0.75 + 0.15 * z0 / 1.6
        lathe(a, [(r0 + 0.02, z0), (r0 + 0.06, z0 + 0.04), (r0 + 0.06, z0 + 0.18), (r0 + 0.03, z0 + 0.22)],
              IRON, sides=12, loc=(bx, by, 0))
    arc = [(bx + 0.9 * math.cos(t), by, 1.6 + 0.75 * math.sin(t))
           for t in [math.pi * i / 6 for i in range(7)]]
    a.tube_loop(arc, 0.05, mat=IRON, rseg=4, closed=False)
    sack(a, (3.2, -0.3, 0), s=0.75)
    return kit.tag(a.finish(), "variant", collision="precise", budget=3000,
                   notes="A-frame tool stand with hanging straps/axes, bucket and sack.")


def build(kit):
    out = [build_hero(kit)]
    out += build_parts(kit)
    out += [build_open_shelf(kit), build_log_rack(kit), build_tool_stand(kit)]
    return out
