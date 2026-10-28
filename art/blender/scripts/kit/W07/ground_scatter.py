"""W07 row 4: Ground Scatter - fallen leaves, twigs, pinecones and stones."""
import math

SUBJECT = "GroundScatter"
ROW = 4
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 90

PALETTE = {
    "w07_leaf": ("#4E9A2C", 0.9, 0, 0),  # leaves and stems of daisies and wildflowers, plus fresh green scatter leaf
    "w07_leaf_autumn": ("#C0561E", 0.9, 0, 0),  # orange/rust fallen leaves (Leaf Variant, litter)
    "w07_wood": ("#7A4A2A", 0.95, 0, 0),  # twigs and pinecone
    "w07_stone": ("#8E8E94", 0.95, 0, 0),  # small ground pebbles and stones (flower/grass bases too)
}

GREEN, AUTUMN, WOOD, STONE = "w07_leaf", "w07_leaf_autumn", "w07_wood", "w07_stone"
NOTE = "ground scatter, players walk through; no sockets"


# ---------------------------------------------------------------- outlines
def _outline(kind):
    """(angle_deg, radius) points around a leaf whose tip points along +X, CCW
    from the stem (-180)."""
    pts = []
    if kind == "maple":
        # 5 sharp lobes with side teeth, deep notches
        lobes = [(-125, 0.62), (-62, 0.86), (0, 1.0), (62, 0.86), (125, 0.62)]
        notch = {(-125, -62): 0.46, (-62, 0): 0.5, (0, 62): 0.5, (62, 125): 0.46}
        pts.append((-178, 0.18))
        pts.append((-160, 0.3))
        for i, (ang, r) in enumerate(lobes):
            pts.append((ang - 13, r * 0.78))
            pts.append((ang, r))
            pts.append((ang + 13, r * 0.78))
            if i + 1 < len(lobes):
                pts.append(((ang + lobes[i + 1][0]) / 2, notch[(ang, lobes[i + 1][0])]))
        pts.append((160, 0.3))
        pts.append((178, 0.18))
    else:
        # broad green leaf: long pointed tip, two pairs of shallow pointed lobes
        pts = [(-178, 0.22), (-150, 0.4), (-118, 0.74), (-88, 0.52), (-58, 0.88),
               (-28, 0.6), (-10, 0.78), (0, 1.0), (10, 0.78), (28, 0.6), (58, 0.88),
               (88, 0.52), (118, 0.74), (150, 0.4), (178, 0.22)]
    return pts


def leaf(a, kind, length, loc, yaw, mat, tilt=(0.0, 0.0), cup=0.12, thick=0.08, stem=True):
    """Thin faceted leaf slab with a raised midrib, cupped edges. Tip along +X
    before yaw (radians). `length` = stem-to-tip span."""
    bm = a.bm
    R = length * 0.62          # centre sits ~38% from the stem end
    pts = _outline(kind)
    top, bot, angs = [], [], []
    for ang, r in pts:
        t = math.radians(ang)
        x, y = math.cos(t) * r * R, math.sin(t) * r * R
        z = thick + cup * (r ** 2) * (0.6 + 0.4 * abs(math.sin(t)))
        top.append(bm.verts.new((x, y, z)))
        bot.append(bm.verts.new((x, y, z - thick)))
        angs.append(abs(ang))
    C = bm.verts.new((0, 0, thick + 0.05))
    M = bm.verts.new((0.42 * R, 0, thick + 0.05 + cup * 0.25))
    Cb = bm.verts.new((0, 0, 0))
    thr = 16 if kind == "maple" else 25
    n = len(pts)
    for i in range(n - 1):
        p, q = top[i], top[i + 1]
        ga, gb = angs[i] <= thr, angs[i + 1] <= thr
        if ga and gb:
            bm.faces.new((M, p, q))
        else:
            bm.faces.new((C, p, q))
            if gb and not ga:
                bm.faces.new((C, q, M))
            elif ga and not gb:
                bm.faces.new((C, M, p))
    bm.faces.new((C, top[-1], top[0]))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((Cb, bot[j], bot[i]))
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    verts = top + bot + [C, M, Cb]
    if stem:
        s0 = -R * 0.18
        sv = [bm.verts.new(c) for c in (
            (s0, -0.03, 0), (s0, 0.03, 0), (s0 - R * 0.32, 0.03, 0.0), (s0 - R * 0.32, -0.03, 0.0),
            (s0, 0, 0.07), (s0 - R * 0.32, 0, 0.05))]
        bm.faces.new((sv[0], sv[1], sv[4]))
        bm.faces.new((sv[3], sv[5], sv[2]))
        bm.faces.new((sv[1], sv[2], sv[5], sv[4]))
        bm.faces.new((sv[0], sv[4], sv[5], sv[3]))
        verts += sv
    a.transform(verts, loc, (tilt[0], tilt[1], yaw))
    return a._finish(verts, mat)


def twig(a, p1, p2, r=0.125, side=None, ends="wood_end"):
    """Brown stick with cut ends; `side` = (t, dx, dy, length) small branch."""
    p1 = (p1[0], p1[1], p1[2] if len(p1) > 2 else r)
    p2 = (p2[0], p2[1], p2[2] if len(p2) > 2 else r)
    a.beam(p1, p2, r, sides=5, mat=WOOD, end_mat=ends, jitter=0.01)
    if side:
        t, dx, dy, ln = side
        s = tuple(p1[k] + (p2[k] - p1[k]) * t for k in range(3))
        d = math.hypot(dx, dy)
        e = (s[0] + dx / d * ln, s[1] + dy / d * ln, max(r * 0.55, s[2] - 0.05))
        a.beam(s, e, r * 0.55, sides=4, mat=WOOD, end_mat=ends, jitter=0.0)


def bit(a, loc, yaw, ln=0.45, r=0.08):
    """Tiny twig bit lying on the ground."""
    dx, dy = math.cos(yaw) * ln / 2, math.sin(yaw) * ln / 2
    a.beam((loc[0] - dx, loc[1] - dy, r), (loc[0] + dx, loc[1] + dy, r), r, sides=5,
           mat=WOOD, end_mat="wood_end", jitter=0.0)


def pinecone(a, loc=(0, 0, 0), rot=(0, 0, 0), h=1.3, d=1.0, rings=6, per=8):
    """Egg-shaped cone of stacked rings of angled scale wedges, tapering to a tip."""
    bm = a.bm
    verts = []
    rmax = d / 2
    core = a.cyl(rmax * 0.5, rmax * 0.3, h * 0.96, sides=6, mat=WOOD)
    verts += core
    for k in range(rings):
        f = (k + 0.5) / rings
        z0 = h * (0.08 + 0.86 * f)
        prof = math.sin(math.pi * (0.1 + 0.85 * f))  # egg: round base, widest mid, blunt tip
        ro = rmax * max(0.32, prof)
        ri = ro * 0.7
        dz = h / rings
        off = (k % 2) * math.pi / per
        for j in range(per):
            t0 = off + 2 * math.pi * j / per
            t1 = t0 + 2 * math.pi / per
            tm = (t0 + t1) / 2
            aa = bm.verts.new((math.cos(t0) * ri, math.sin(t0) * ri, z0 + dz * 0.55))
            bb = bm.verts.new((math.cos(t1) * ri, math.sin(t1) * ri, z0 + dz * 0.55))
            cc = bm.verts.new((math.cos(tm) * ri * 0.85, math.sin(tm) * ri * 0.85, z0 - dz * 0.5))
            w = (t1 - t0) * 0.22
            t2 = bm.verts.new((math.cos(tm - w) * ro, math.sin(tm - w) * ro, z0 - dz * 0.2))
            t3 = bm.verts.new((math.cos(tm + w) * ro, math.sin(tm + w) * ro, z0 - dz * 0.2))
            bm.faces.new((aa, t2, t3, bb))      # broad rounded scale plate
            bm.faces.new((aa, cc, t2))
            bm.faces.new((bb, t3, cc))
            bm.faces.new((t2, cc, t3))
            verts += [aa, bb, cc, t2, t3]
    a.transform(verts, loc, rot)
    return a._finish(verts, WOOD)


def clamp(a):
    for v in a.bm.verts:
        if v.co.z < 0:
            v.co.z = 0.0


def done(kit, a, role, budget, caption=None):
    clamp(a)
    o = a.finish()
    if caption:
        o["kit_caption"] = caption
    return kit.tag(o, role, collision="none", budget=budget, notes=NOTE)


R = math.radians


# ---------------------------------------------------------------- build
def build(kit):
    fk = kit.flintkit
    out = []

    # ---- hero pile
    a = fk.Asset("GroundScatter", "W07 GroundScatter")
    leaf(a, "maple", 2.3, (-1.0, -1.25, 0), R(-120), AUTUMN, cup=0.14)
    leaf(a, "maple", 1.6, (-1.7, 0.8, 0), R(140), AUTUMN)
    leaf(a, "maple", 1.7, (0.3, 1.3, 0), R(80), AUTUMN)
    leaf(a, "maple", 1.5, (1.7, 0.7, 0), R(20), AUTUMN)
    leaf(a, "maple", 1.1, (0.9, -1.55, 0), R(-80), AUTUMN)
    leaf(a, "maple", 1.0, (-2.15, -0.25, 0), R(170), AUTUMN)
    leaf(a, "broad", 2.4, (-1.15, -0.05, 0.1), R(165), GREEN, tilt=(0.0, R(-4)), cup=0.16)
    leaf(a, "broad", 2.4, (1.35, -0.75, 0.1), R(-30), GREEN, tilt=(R(4), 0.0), cup=0.16)
    leaf(a, "broad", 0.8, (-2.2, -1.2, 0), R(-150), GREEN, stem=False)
    twig(a, (-2.0, -0.1, 0.25), (2.4, 0.35, 0.8), r=0.17, side=(0.35, 0.4, 1.0, 0.8))
    twig(a, (-0.9, 1.6, 1.15), (1.2, -0.35, 0.3), r=0.16)
    twig(a, (-1.2, 1.4, 0.2), (0.6, 1.75, 0.2), r=0.1)
    pinecone(a, (-0.2, -1.0, 0.05), (R(-18), R(8), R(20)), h=1.3, d=1.15)
    for loc, yaw in (((-2.3, 0.3), 0.4), ((-1.8, -1.6), 1.2), ((2.3, -1.2), 2.0), ((0.1, -1.8), -0.3)):
        bit(a, loc, yaw)
    a.rock((1.3, 1.05, 0.85), (-1.05, -0.4, 0), (0, 0, R(20)), STONE, subdiv=1, facets=14)
    a.rock((1.5, 1.2, 1.0), (1.1, 0.95, 0), (0, 0, R(-25)), STONE, subdiv=1, facets=14)
    out.append(done(kit, a, "hero", 2500))

    # ---- parts
    a = fk.Asset("ScatterLeaf", "W07 Leaf")
    leaf(a, "broad", 2.4, (0, 0, 0), R(30), GREEN, cup=0.18)
    out.append(done(kit, a, "part", 200))

    a = fk.Asset("LeafVariant", "W07 Leaf (Variant)")
    leaf(a, "maple", 2.2, (0, 0, 0), R(60), AUTUMN, cup=0.16)
    out.append(done(kit, a, "part", 200, "Leaf (Variant)"))

    a = fk.Asset("Twig", "W07 Twig")
    twig(a, (-2.0, -0.3), (0.2, 0.05), side=(0.55, 0.3, 1.0, 0.7))
    twig(a, (0.2, 0.05), (2.0, 0.55))
    out.append(done(kit, a, "part", 150))

    a = fk.Asset("Pinecone", "W07 Pinecone")
    pinecone(a, (0, 0, 0), (0, 0, 0), h=1.3, d=1.0, rings=7, per=8)
    out.append(done(kit, a, "part", 400))

    a = fk.Asset("GroundStone", "W07 Ground Stone")
    a.rock((1.8, 1.4, 1.0), (0, 0, 0), (0, 0, R(10)), STONE, subdiv=2, facets=14)
    out.append(done(kit, a, "part", 300, "Ground Stone (2 sizes)"))

    a = fk.Asset("GroundStoneSmall", "W07 Ground Stone Small")
    a.rock((0.9, 0.7, 0.5), (0, 0, 0), (0, 0, R(-15)), STONE, subdiv=1, facets=14)
    out.append(done(kit, a, "part", 200))

    # ---- variants
    a = fk.Asset("LeafLitter", "W07 Leaf Litter")
    spec = [("maple", 1.7, (-1.3, -0.9), -110, AUTUMN), ("maple", 1.6, (0.2, -1.1), -60, AUTUMN),
            ("maple", 1.7, (1.4, -0.4), -10, AUTUMN), ("maple", 1.5, (-1.5, 0.6), 150, AUTUMN),
            ("maple", 1.6, (0.0, 0.9), 95, AUTUMN), ("maple", 1.4, (1.3, 1.1), 40, AUTUMN),
            ("broad", 1.6, (-0.4, -0.1), 200, GREEN), ("broad", 1.3, (1.0, 0.3), -40, GREEN),
            ("maple", 1.1, (-0.6, 1.4), 120, AUTUMN), ("broad", 0.9, (-1.9, -0.2), 190, GREEN)]
    for i, (k, ln, (x, y), yaw, m) in enumerate(spec):
        leaf(a, k, ln, (x, y, 0.03 * (i % 4)), R(yaw), m, stem=(ln > 1.2))
    twig(a, (-1.2, 0.15, 0.3), (1.3, 0.5, 0.25), r=0.1)
    twig(a, (-0.3, 1.2, 0.25), (0.6, -0.9, 0.3), r=0.09)
    for loc, yaw in (((-2.0, -1.4), 0.5), ((1.9, -1.3), 1.9), ((2.0, 0.6), -0.6)):
        bit(a, loc, yaw, 0.4, 0.07)
    out.append(done(kit, a, "variant", 1200, "Leaf Litter"))

    a = fk.Asset("TwigPatch", "W07 Twig Patch")
    twig(a, (-2.3, -1.5), (2.2, 1.5), r=0.13, side=(0.75, 0.3, 1.0, 0.7))
    twig(a, (-2.2, 1.5, 0.35), (2.2, -1.5, 0.35), r=0.13)
    twig(a, (-1.6, 1.6, 0.6), (-0.2, -1.6, 0.55), r=0.11)
    twig(a, (0.4, 1.7, 0.6), (1.6, -1.5, 0.6), r=0.11)
    twig(a, (-2.3, -0.2, 0.85), (2.3, 0.2, 0.85), r=0.1)
    leaf(a, "maple", 1.5, (0.0, -0.1, 0), R(-80), AUTUMN)
    leaf(a, "maple", 1.3, (-1.4, -1.2, 0), R(-140), AUTUMN)
    leaf(a, "maple", 1.3, (1.5, 1.2, 0), R(50), AUTUMN)
    leaf(a, "broad", 1.3, (-1.7, 0.5, 0), R(160), GREEN)
    a.rock((0.8, 0.65, 0.5), (1.1, 1.6, 0), (0, 0, R(30)), STONE, subdiv=1, facets=14)
    out.append(done(kit, a, "variant", 1200, "Twig Patch"))

    a = fk.Asset("MixedScatterSparse", "W07 Mixed Scatter (Sparse)")
    twig(a, (-2.4, 1.6), (1.7, -1.4), r=0.12, side=(0.6, 0.6, 1.0, 0.6))
    pinecone(a, (-1.1, -0.6, 0), (0, 0, 0), h=1.1, d=0.85, rings=6, per=7)
    a.rock((0.9, 0.75, 0.6), (1.9, 1.2, 0), (0, 0, R(15)), STONE, subdiv=1, facets=14)
    a.rock((0.6, 0.5, 0.4), (0.9, 1.8, 0), (0, 0, R(-20)), STONE, subdiv=1, facets=14)
    leaf(a, "broad", 1.3, (0.2, 1.4, 0), R(100), GREEN)
    leaf(a, "maple", 1.3, (1.3, -0.9, 0), R(-30), AUTUMN)
    leaf(a, "maple", 1.1, (-2.0, 0.2, 0), R(170), AUTUMN)
    leaf(a, "broad", 0.9, (2.3, -0.1, 0), R(10), GREEN, stem=False)
    out.append(done(kit, a, "variant", 1200, "Mixed Scatter (Sparse)"))
    return out
