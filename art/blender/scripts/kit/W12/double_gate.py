"""W12 row 2: DoubleGate - closed timber double gate with banners and lanterns."""
import math

SUBJECT = "DoubleGate"
ROW = 2
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 135

PALETTE = {
    "w12_wood": ("#8F5A2C", 0.9, 0, 0),
    "w12_tan": ("#C9985A", 0.9, 0, 0),
    "w12_stone": ("#7E7F8C", 0.95, 0, 0),
    "w12_leaf": ("#3F9A2E", 0.9, 0, 0),
    "w12_iron": ("#3B404C", 0.5, 0.5, 0),
    "w12_banner_red": ("#C8202B", 0.8, 0, 0),
    "w12_banner_trim": ("#F2E6D2", 0.8, 0, 0),
    "w12_lantern_glow": ("#FFB23A", 0.4, 0, 1.5),
}

WOOD, TAN, STONE, LEAF, IRON = "w12_wood", "w12_tan", "w12_stone", "w12_leaf", "w12_iron"
RED, TRIM, GLOW = "w12_banner_red", "w12_banner_trim", "w12_lantern_glow"
R90 = math.pi / 2

POST_X = 6.2          # post centres; inner faces at +-5.0 -> 10 stud doorway
LEAF_W, LEAF_H, LEAF_T = 4.9, 8.4, 0.7
LEAF_Z0 = 0.2
LANTERN_Z = 6.8


def _cat(*lists):
    out = []
    for l in lists:
        out += list(l)
    return out


# --------------------------------------------------------------- pieces

def post(a, x, h=11.3, cap=True, rope=True):
    v = list(a.box((2.4, 2.4, h), (x, 0, h / 2), mat=WOOD, bevel=0.08))
    if cap:
        v += a.box((2.3, 2.3, 0.45), (x, -0.05, h + 0.22), mat=WOOD, bevel=0.1)
        v += a.box((1.5, 1.5, 0.3), (x + 0.1, 0, h + 0.55), mat=WOOD, bevel=0.08)
    if rope:
        for z in (8.55, 8.9):
            v += a.box((2.6, 2.6, 0.26), (x, 0, z), mat=TAN, bevel=0.06)
    return v


def lintel(a, x0=-7.2, x1=7.2, ends=(True, True)):
    L = x1 - x0
    cx = (x0 + x1) / 2
    v = list(a.box((L, 2.2, 1.8), (cx, 0, 10.4), mat=WOOD, bevel=0.08))
    # stepped end blocks protruding past the posts
    for side, ok in ((-1, ends[0]), (1, ends[1])):
        if not ok:
            continue
        ex = x0 if side < 0 else x1
        v += a.box((1.5, 2.8, 1.5), (ex - side * 0.15, -0.05, 9.85), mat=WOOD, bevel=0.08)
        v += a.box((0.9, 1.6, 0.9), (ex + side * 0.55, -0.1, 10.0), mat=WOOD, bevel=0.06)
        # rope lashing on the lintel just inboard of the post
        for dx in (0.0, 0.32):
            v += a.box((0.24, 2.4, 2.0), (side * (4.75 - dx), 0, 10.4), mat=TAN, bevel=0.05)
    return v


def leaf(a, side, latch=True):
    """One leaf built with its hinge (outer edge, centre plane) at the origin,
    extending along +x for side=-1 (left leaf) or -x for side=+1 (right)."""
    d = -side   # direction from hinge toward the centre seam
    v = []
    n = 4
    pw = LEAF_W / n
    for i in range(n):
        h = LEAF_H - (0.0, 0.15, 0.05, 0.2)[i if side < 0 else n - 1 - i]
        cx = d * (pw * (i + 0.5))
        v += a.plank((pw - 0.07, LEAF_T, h), (cx, 0, LEAF_Z0 + h / 2), mat=WOOD)
    for z in (1.9, 6.7):
        v += a.box((LEAF_W - 0.2, 0.12, 0.5), (d * LEAF_W / 2, -LEAF_T / 2 - 0.05, z), mat=IRON)
        v += a.box((LEAF_W - 0.4, 0.1, 0.5), (d * LEAF_W / 2, LEAF_T / 2 + 0.04, z), mat=IRON)
        for k in (0.5, 2.45, 4.4):
            v += a.box((0.16, 0.08, 0.16), (d * k, -LEAF_T / 2 - 0.13, z), mat=IRON)
        # hinge strap wraps the outer edge + pin
        v += a.box((0.5, LEAF_T + 0.3, 0.55), (-d * 0.1, 0, z), mat=IRON)
        v += a.cyl(0.13, 0.13, 0.9, sides=6, loc=(-d * 0.28, -0.1, z - 0.45), mat=IRON)
    # ring handle near the seam
    hx = d * (LEAF_W - 0.75)
    v += a.box((0.4, 0.08, 0.4), (hx, -LEAF_T / 2 - 0.04, 4.45), mat=IRON)
    v += a.torus(0.5, 0.1, loc=(hx, -LEAF_T / 2 - 0.14, 3.95), rot=(R90, 0, 0), mat=IRON,
                 seg=10, rseg=4)
    if latch:
        # latch bracket + peg on the rear
        v += a.box((0.5, 0.35, 0.9), (d * (LEAF_W - 1.4), LEAF_T / 2 + 0.17, 4.2), mat=WOOD, bevel=0.04)
    return v


def place_leaf(a, side, angle=0.0, crooked=None):
    """Build a leaf and move it onto its hinge at x = side*5.0."""
    v = leaf(a, side)
    if crooked:
        a.transform(v, (0, 0, 0), crooked)
    a.transform(v, (side * 4.98, 0, 0), (0, 0, angle))
    return v


def latch_bar(a, loc=(0, 0.95, 4.2), length=5.0):
    v = list(a.box((length, 0.5, 0.5), loc, mat=WOOD, bevel=0.05))
    v += a.box((0.4, 0.4, 1.2), (loc[0] + length / 2 - 0.3, loc[1] + 0.35, loc[2] + 0.1), mat=WOOD,
               bevel=0.04)
    return v


def banner(a, x, y=-1.25, top=8.6, crossbar=True):
    w, h = 1.3, 4.0
    pts = [(-w / 2, 0), (0, 0.7), (w / 2, 0), (w / 2, h), (-w / 2, h)]
    v = list(a.poly_prism(pts, 0.1, (x, y, top - h), (R90, 0, 0), mat=RED))
    dia = [(0, -0.75), (0.5, 0), (0, 0.75), (-0.5, 0)]
    v += a.poly_prism(dia, 0.05, (x, y - 0.1, top - 1.7), (R90, 0, 0), mat=TRIM)
    inner = [(0, -0.42), (0.28, 0), (0, 0.42), (-0.28, 0)]
    v += a.poly_prism(inner, 0.04, (x, y - 0.14, top - 1.7), (R90, 0, 0), mat=RED)
    v += a.box((w - 0.1, 0.04, 0.12), (x, y - 0.12, top - 0.35), mat=TRIM)
    if crossbar:
        v += a.box((w + 0.4, 0.22, 0.22), (x, y - 0.05, top + 0.05), mat=WOOD)
        v += a.box((0.12, 0.12, 0.4), (x, y + 0.02, top + 0.3), mat=IRON)
    return v


def lantern(a, x, y=-1.9, z=LANTERN_Z, post_y=-1.2):
    """Iron cage 0.9 x 1.4 with glowing glass, hanging from a hook arm."""
    zb, zt = z - 0.75, z + 0.65
    v = list(a.box((0.65, 0.65, 1.0), (x, y, z - 0.05), mat=GLOW))
    v += a.box((0.9, 0.9, 0.18), (x, y, zb + 0.09), mat=IRON)
    v += a.box((0.9, 0.9, 0.16), (x, y, zt - 0.2), mat=IRON)
    v += a.cyl(0.5, 0.12, 0.35, sides=4, loc=(x, y, zt - 0.12), rot=(0, 0, math.pi / 4), mat=IRON)
    for dx in (-0.38, 0.38):
        for dy in (-0.38, 0.38):
            v += a.box((0.1, 0.1, 1.2), (x + dx, y + dy, z - 0.05), mat=IRON)
    # hook arm from the post
    v += a.box((0.14, abs(post_y - y) + 0.2, 0.14), (x, (post_y + y) / 2, zt + 0.6), mat=IRON)
    v += a.box((0.1, 0.1, 0.45), (x, y, zt + 0.35), mat=IRON)
    return v


def brace(a, x, y=0.95):
    """Rear knee brace from the post's outer face down and out to the ground."""
    s = 1 if x > 0 else -1
    return list(a.beam((x + s * 0.7, y, 5.2), (x + s * 2.35, y, 0.36), 0.34, sides=5,
                       mat=WOOD, end_mat=WOOD))


def dressing(a, x, side, big=True):
    """Boulders and clover tufts at a post foot (call last: rock invalidates verts)."""
    o = side
    if big:
        a.rock((2.8, 2.3, 2.6), (x + o * 0.5, -1.9, 0), (0, 0, 0.4), mat=STONE, subdiv=1, sink=0.0)
    a.rock((1.7, 1.5, 1.5), (x - o * 1.0, -2.2, 0), (0, 0, 1.1), mat=STONE, subdiv=1, sink=0.0)
    for (dx, dy, r) in ((o * 1.6, -2.6, 0.7), (-o * 1.9, -1.6, 0.55), (o * -0.1, -3.0, 0.6),
                        (o * 1.3, -0.6, 0.55), (-o * 0.6, -3.1, 0.45)):
        a.leaf_cluster(r, (x + dx, dy, r * 0.5), mat=LEAF, lobes=5, floor=0.0)


def frame(a, pairs=(True, True), braces=True, latch=True):
    post(a, -POST_X)
    post(a, POST_X)
    lintel(a)
    if braces:
        brace(a, -POST_X)
        brace(a, POST_X)
    for s, ok in zip((-1, 1), pairs):
        if ok:
            banner(a, s * 6.7)
            lantern(a, s * 5.4)
    if latch:
        latch_bar(a)


def finish_with_sockets(kit, a, lanterns):
    vs = [v.co for v in a.bm.verts]
    cx = (min(c.x for c in vs) + max(c.x for c in vs)) / 2
    cy = (min(c.y for c in vs) + max(c.y for c in vs)) / 2
    o = a.finish()
    for (x, y, z) in lanterns:
        kit.vfx.add(o, "heat_glow", (x - cx, y - cy, z), scale=0.7, color=["#FFB23A", "#FF8A1F"],
                    light={"type": "point", "color": "#FFA040", "range": 12, "brightness": 1.2})
    return o


LANT = [(-5.4, -1.9, LANTERN_Z), (5.4, -1.9, LANTERN_Z)]
SOCKET_NOTE = "heat_glow sockets at each lantern's emissive glass (warm orange point light, range 12)."


# --------------------------------------------------------------- build

def build(kit):
    fk = kit.flintkit
    out = []

    # ---- hero
    a = fk.Asset("DoubleGate", "W12 DoubleGate")
    frame(a)
    place_leaf(a, -1)
    place_leaf(a, 1)
    dressing(a, -POST_X, -1)
    dressing(a, POST_X, 1)
    o = finish_with_sockets(kit, a, LANT)
    out.append(kit.tag(o, "hero", collision="precise", budget=6000,
                       notes="Closed double gate, 10x8 doorway. " + SOCKET_NOTE))

    # ---- parts
    a = fk.Asset("GateUprightPost", "W12 DoubleGate part")
    post(a, 0, h=11.3)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Square post 2.4x2.4x12, rope wrap, capped top."))

    a = fk.Asset("GateTopBeam", "W12 DoubleGate part")
    v = lintel(a)
    a.transform(v, (0, 0, -9.1))
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Lintel 16x2.4x2.2 with stepped end blocks and rope lashings."))

    a = fk.Asset("GateHingeBlock", "W12 DoubleGate part")
    a.box((1.2, 1.2, 3.0), (0, 0, 1.5), mat=WOOD, bevel=0.06)
    for z in (0.7, 2.3):
        a.box((1.6, 0.14, 0.45), (0.3, -0.66, z), mat=IRON)
        a.box((0.16, 0.08, 0.16), (0.7, -0.75, z), mat=IRON)
    a.cyl(0.16, 0.16, 2.6, sides=6, loc=(0.75, -0.7, 0.2), mat=IRON)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="Wooden hinge block with iron straps and pin."))

    a = fk.Asset("GateLeaf", "W12 DoubleGate part")
    leaf(a, -1)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500,
                       notes="One gate leaf (mirror for left/right): planks, 2 iron straps, ring handle."))

    a = fk.Asset("GateLatchBar", "W12 DoubleGate part")
    latch_bar(a, loc=(0, 0, 0.25))
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="Rear latch bar 5x0.5x0.5 with peg end."))

    a = fk.Asset("GateLatchPeg", "W12 DoubleGate part")
    a.box((0.4, 0.4, 1.0), (0, 0, 0.5), mat=WOOD, bevel=0.04)
    a.box((0.55, 0.55, 0.2), (0, 0, 1.1), mat=WOOD, bevel=0.04)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="Latch peg 0.4x0.4x1.2."))

    a = fk.Asset("GateRopeWrap", "W12 DoubleGate part")
    for i in range(3):
        a.torus(0.6, 0.13, loc=(0, 0, 0.13 + i * 0.24), mat=TAN, seg=12, rseg=4)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="Tan rope coil / band."))

    a = fk.Asset("GateRingHandle", "W12 DoubleGate part")
    a.box((0.45, 0.1, 0.45), (0, 0.12, 1.15), mat=IRON)
    a.torus(0.5, 0.1, loc=(0, 0, 0.6), rot=(R90, 0, 0), mat=IRON, seg=10, rseg=4)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="Iron ring handle with mount plate."))

    a = fk.Asset("GateBanner", "W12 DoubleGate part")
    banner(a, 0, y=0.05, top=4.0)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500,
                       notes="Red swallowtail banner with cream diamond on a crossbar."))

    # ---- variants
    a = fk.Asset("GateClosed", "W12 DoubleGate variant")
    frame(a, pairs=(True, False))
    place_leaf(a, -1)
    place_leaf(a, 1)
    dressing(a, POST_X, 1)
    o = finish_with_sockets(kit, a, LANT[:1])
    out.append(kit.tag(o, "variant", collision="precise", budget=5000,
                       notes="Standard closed gate, one banner+lantern. " + SOCKET_NOTE))

    a = fk.Asset("GateOpen", "W12 DoubleGate variant")
    frame(a, latch=False)
    place_leaf(a, -1, angle=math.radians(95))
    place_leaf(a, 1, angle=math.radians(-95))
    dressing(a, -POST_X, -1)
    dressing(a, POST_X, 1)
    o = finish_with_sockets(kit, a, LANT)
    out.append(kit.tag(o, "variant", collision="precise", budget=5000,
                       notes="Both leaves swung 95 deg inward, 10x8 opening clear. " + SOCKET_NOTE))

    a = fk.Asset("GateRuined", "W12 DoubleGate variant")
    post(a, POST_X)
    banner(a, POST_X + 0.5)
    lantern(a, POST_X - 0.8)
    brace(a, POST_X)
    # left post: leaning stump broken at half height with jagged top
    v = list(a.box((2.4, 2.4, 5.0), (0, 0, 2.5), mat=WOOD, bevel=0.08))
    v += a.box((1.0, 2.2, 1.0), (-0.6, 0.0, 5.3), (0, 0.3, 0), mat=WOOD)
    v += a.box((0.7, 1.4, 0.8), (0.6, -0.3, 5.1), (0.2, -0.2, 0), mat=WOOD)
    a.transform(v, (-POST_X, 0, 0), (0, math.radians(-9), 0))
    # fallen upper half of left post lying on the ground
    a.box((2.2, 2.2, 5.0), (-7.4, -3.4, 1.1), (R90, 0, math.radians(-30)), mat=WOOD, bevel=0.08)
    # right half of the lintel stays on the right post, sagging
    v = lintel(a, x0=0.0, x1=7.2, ends=(False, True))
    v += a.box((0.8, 1.8, 1.4), (-0.2, 0, 10.6), (0, 0.4, 0), mat=WOOD)
    a.transform(v, (0, 0, 0), (0, math.radians(-4), 0))
    # left half fallen across the ground
    a.box((6.5, 2.0, 1.7), (-2.6, -2.6, 0.85), (0, 0, math.radians(14)), mat=WOOD, bevel=0.08)
    # right leaf hanging crooked off its lower hinge
    place_leaf(a, 1, angle=math.radians(-8), crooked=(0, math.radians(-7), 0))
    # broken planks and split brace on the ground
    a.plank((1.1, 0.6, 3.6), (-1.4, -0.4, 0.3), (R90, 0, math.radians(70)), mat=WOOD)
    a.plank((1.1, 0.6, 2.6), (-3.2, 0.9, 0.3), (R90, 0, math.radians(-20)), mat=WOOD)
    a.plank((1.1, 0.6, 2.0), (0.2, 1.6, 0.6), (math.radians(70), 0.3, math.radians(40)), mat=WOOD)
    a.beam((-6.0, 1.3, 0.35), (-6.4, 3.6, 0.35), 0.3, sides=5, mat=WOOD, end_mat=WOOD)
    a.beam((-5.0, 1.8, 0.3), (-3.6, 3.2, 0.3), 0.28, sides=5, mat=WOOD, end_mat=WOOD)
    # snapped plank leaning from the ground against the stump
    a.plank((1.0, 0.5, 5.2), (-3.4, -0.9, 2.2), (0, math.radians(-38), 0), mat=WOOD)
    a.plank((0.9, 0.5, 2.4), (-0.6, -1.4, 1.0), (0, math.radians(30), 0.2), mat=WOOD)
    dressing(a, -POST_X, -1)
    dressing(a, POST_X, 1, big=False)
    o = finish_with_sockets(kit, a, [(POST_X - 0.8, -1.9, LANTERN_Z)])
    out.append(kit.tag(o, "variant", collision="precise", budget=5000,
                       notes="Partial ruin: left post snapped, lintel half fallen, leaf crooked. "
                             + SOCKET_NOTE))
    return out
