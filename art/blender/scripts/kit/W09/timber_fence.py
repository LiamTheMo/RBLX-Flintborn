"""W09 row 3: TimberFence. Chunky 2-rail ranch fence with rope X lashings,
daisies, grass tufts and grey rocks at the base."""
import math
import random

SUBJECT = "TimberFence"
ROW = 3
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 60   # the sheet's SIDE cell is a steep front-right three-quarter

PALETTE = {
    "w09_boulder": ("#8C8E98", 0.9, 0, 0),  # cool grey rocks, footings, stray stones (all rows)
    "w09_grass": ("#5FA52A", 0.95, 0, 0),  # grass edge strip tops and turf tufts
    "w09_foliage": ("#3F9A2C", 0.9, 0, 0),  # leafy plant blades and bushes round the bases
    "w09_soil": ("#9A6430", 1, 0, 0),  # exposed earth under strips, path edges and tufts
    "w09_petal": ("#F7F3E6", 0.8, 0, 0),  # small white daisy petals
    "w09_flower_eye": ("#F0BE2A", 0.8, 0, 0),  # daisy centres
    "w09_wood": ("#B3622B", 0.85, 0, 0),  # orange-brown timber posts, rails, boards, crosspieces
    "w09_wood_end": ("#7B5A45", 0.9, 0, 0),  # cut end grain, nail notches and cap undersides
    "w09_rope": ("#CFAE6E", 1, 0, 0),  # hemp rope lashings and ties
}

WOOD, END, ROPE = "w09_wood", "w09_wood_end", "w09_rope"
PI = math.pi

POST_W = 1.2
RAIL_Y = -0.8           # rail centre depth (rails pass in front of the posts)
TOP_Z, BOT_Z = 3.8, 1.9
POST_H = 6.0            # posts tower ~1.8 studs above the top rail like the reference


# ----------------------------------------------------------------- helpers
def _rail(a, L, h, d, loc, rot=(0, 0, 0), rng=None, shear=0.22, broken=0):
    """Chunky rail along local X centred at the origin, two slightly kinked
    segments, end-grain plates on the cut ends (diagonal cut via shear).
    broken=+1/-1 replaces that end's plate with splinters."""
    rng = rng or random.Random(1)
    e = 0.1
    half = L / 2
    seg = (L - 2 * e) / 2 + 0.06
    vs = []
    for sx in (-1, 1):
        cx = sx * (seg / 2 - 0.03)
        r = (rng.uniform(-0.02, 0.02), sx * 0.012 + rng.uniform(-0.008, 0.008),
             rng.uniform(-0.012, 0.012))
        vs += a.box((seg, d, h), loc=(cx, 0, rng.uniform(-0.05, 0.05)), rot=r, mat=WOOD,
                    bevel=0.07, jitter=0.03)
        if broken == sx:
            for k in range(4):
                sz = rng.uniform(-h * 0.3, h * 0.3)
                sy = rng.uniform(-d * 0.3, d * 0.3)
                v = a.cyl(rng.uniform(0.12, 0.2), 0.0, rng.uniform(0.35, 0.7), sides=3, mat=WOOD)
                a.transform(v, (sx * (half - e - 0.05), sy, sz),
                            (0, sx * PI / 2 + rng.uniform(-0.3, 0.3), rng.uniform(0, PI)))
                vs += v
            vs += a.box((0.06, d * 0.8, h * 0.8), loc=(sx * (half - e - 0.02), 0, 0), mat=END)
        else:
            vs += a.box((e, d * 0.9, h * 0.88), loc=(sx * (half - e / 2), 0, 0), mat=END,
                        bevel=0.02)
    if shear:
        for v in vs:
            if abs(v.co.x) > half * 0.8:
                s = 1 if v.co.x > 0 else -1
                if broken != s:
                    v.co.x += s * shear * (v.co.z / h)
    a.transform(vs, loc, rot)
    return vs


def _post(a, h, loc=(0, 0, 0), rot=(0, 0, 0), cap=1.4, cap_h=0.5, w=POST_W, slot=True,
          groove=None):
    """Square post on the ground with a proud cap block (or a chamfered top)."""
    vs = []
    body_h = h - cap_h if cap else h - 0.4
    if groove:
        g0, g1 = groove
        vs += a.box((w, w, g0), mat=WOOD, bevel=0.08, jitter=0.03, base=True)
        vs += a.box((w * 0.86, w * 0.86, g1 - g0), loc=(0, 0, g0), mat=END, base=True)
        vs += a.box((w, w, body_h - g1), loc=(0, 0, g1), mat=WOOD, bevel=0.08, jitter=0.03,
                    base=True)
    else:
        vs += a.box((w, w, body_h), mat=WOOD, bevel=0.08, jitter=0.03, base=True)
    if cap:
        vs += a.box((cap, cap, cap_h), loc=(0, 0, body_h + cap_h / 2), mat=WOOD, bevel=0.12,
                    jitter=0.03)
        vs += a.cyl(cap * 0.707, cap * 0.45, 0.14, sides=4, loc=(0, 0, h - 0.02),
                    rot=(0, 0, PI / 4), mat=WOOD)
        # vertical split on the cap front
        vs += a.box((0.07, 0.06, cap_h * 0.75), loc=(0.18, -cap / 2 + 0.01, body_h + cap_h / 2),
                    mat=END)
    else:
        vs += a.cyl(w * 0.707, w * 0.42, 0.4, sides=4, loc=(0, 0, body_h), rot=(0, 0, PI / 4),
                    mat=WOOD)
    if slot:
        # vertical grain notch and a nail slot on the front face
        vs += a.box((0.07, 0.06, body_h * 0.35), loc=(-0.22, -w / 2 + 0.005, body_h * 0.45),
                    mat=END)
        vs += a.box((0.16, 0.06, 0.55), loc=(0.2, -w / 2 + 0.005, body_h * 0.82), mat=END)
    a.transform(vs, loc, rot)
    return vs


def _loop(a, hx, ymin, ymax, z0, z1, t, rseg=4):
    """Rope loop around the rect [-hx,hx]x[ymin,ymax]; z goes z0 (left) -> z1 (right)."""
    c = 0.14
    p2 = [(-hx, ymin + c), (-hx + c, ymin), (hx - c, ymin), (hx, ymin + c),
          (hx, ymax - c), (hx - c, ymax), (-hx + c, ymax), (-hx, ymax - c)]
    pts = [(x, y, z0 + (z1 - z0) * (x + hx) / (2 * hx)) for x, y in p2]
    return a.tube_loop(pts, t, mat=ROPE, rseg=rseg, closed=True)


def _xlash(a, loc, zr, rotz=0.0, rot=None, span=0.45, t=0.12, wraps=(), rail_d=0.7):
    """X lashing binding a rail (in front, -Y) to a post at loc, around rail centre zr.
    wraps: extra horizontal wraps (z values) round the post alone."""
    hw = POST_W / 2 + t * 0.6
    front = RAIL_Y - rail_d / 2 - t * 0.6
    vs = []
    vs += _loop(a, hw, front, hw, zr - span, zr + span, t)
    vs += _loop(a, hw, front, hw, zr + span, zr - span, t)
    vs += _loop(a, hw, front, hw, zr - span - 0.05, zr - span - 0.05, t)
    for z in wraps:
        vs += _loop(a, hw, -hw, hw, z, z, t)
    a.transform(vs, loc, rot if rot is not None else (0, 0, rotz))
    return vs


def _clump(a, loc, r, rng, blades=3, lobes=6):
    """Dense leafy clump: one lobed leaf cluster sitting on the ground plus a few
    broad spiky blades poking out above it."""
    x, y, z = loc
    r *= 1.3
    a.leaf_cluster(r, loc=(x, y, z + r * 0.45), mat="w09_foliage", lobes=lobes, squash=0.85)
    for i in range(blades):
        ang = 2 * PI * i / max(blades, 1) + rng.uniform(-0.5, 0.5)
        h = r * rng.uniform(1.3, 1.75)
        v = a.cyl(0.42 * r, 0.0, h, sides=4, mat="w09_foliage")
        a.transform(v, (x + math.cos(ang) * r * 0.3, y + math.sin(ang) * r * 0.3, z),
                    (rng.uniform(0.2, 0.45), 0, ang + PI / 2), (1, 0.3, 1))


def _daisy(a, loc, rng, r=0.5):
    """White daisy: 6 flat petals (~1 stud across) and a yellow eye on a stem,
    held up above the leaves."""
    x, y, z = loc
    a.cyl(0.04, 0.04, z, sides=3, loc=(x, y, 0), mat="w09_foliage")
    off = rng.uniform(0, PI)
    tilt = rng.uniform(-0.25, 0.25)
    for k in range(6):
        ang = off + 2 * PI * k / 6
        a.ico((r * 0.55, r * 0.24, r * 0.08),
              loc=(x + math.cos(ang) * r * 0.5, y + math.sin(ang) * r * 0.5, z),
              rot=(tilt, 0, ang), mat="w09_petal", subdiv=1)
    a.ico((0.15, 0.15, 0.1), loc=(x, y, z + 0.06), mat="w09_flower_eye", subdiv=1)


def _mound(a, loc, sx, sy, rot=0.0, h=0.45):
    """Irregular soil mound with a visible earth rim (leaves sit on top)."""
    v = a.cyl(1.0, 0.8, h, sides=11, mat="w09_soil", jitter=0.06)
    a.transform(v, loc, (0, 0, rot), (sx, sy, 1))


def _clamp(a):
    for v in a.bm.verts:
        if v.co.z < 0:
            v.co.z = 0.0


def _fence_section(a, rng, x0=-5.0, x1=5.0, rail_l=12.0, top_wraps=True, lash_both=True):
    _post(a, POST_H, loc=(x0, 0, 0), rot=(0, 0, rng.uniform(-0.03, 0.03)), cap=1.5, cap_h=0.6)
    _post(a, POST_H, loc=(x1, 0, 0), rot=(0, 0, rng.uniform(-0.03, 0.03)), cap=1.5, cap_h=0.6)
    cx = (x0 + x1) / 2
    _rail(a, rail_l, 0.85, 0.75, (cx - 0.15, RAIL_Y, TOP_Z), (0.01, 0.01, 0.0), rng)
    _rail(a, rail_l, 0.85, 0.8, (cx + 0.1, RAIL_Y, BOT_Z), (-0.01, -0.012, 0.0), rng)
    _xlash(a, (x0, 0, 0), TOP_Z, t=0.14, rail_d=0.75)
    _xlash(a, (x1, 0, 0), TOP_Z, t=0.14, rail_d=0.75,
           wraps=(5.05, 4.8) if top_wraps else ())


# ------------------------------------------------------------------ build
def build(kit):
    fk = kit.flintkit
    out = []

    # ---------------- hero
    rng = random.Random(9)
    a = fk.Asset("TimberFence", "W09 TimberFence", seed=9)
    _mound(a, (0, -0.45, 0), 6.9, 2.0)
    _fence_section(a, rng)
    # dense overlapping leaf clumps along the front and back, hiding most of the mound
    for p, r, b in [((-6.0, -1.5, 0.3), 1.15, 3), ((-4.9, -1.9, 0.3), 1.0, 2),
                    ((-5.5, -0.4, 0.3), 0.9, 2), ((-0.9, -1.8, 0.3), 0.95, 2),
                    ((0.4, -1.6, 0.3), 0.85, 1), ((1.8, -1.8, 0.3), 1.0, 2),
                    ((3.2, -1.6, 0.3), 0.9, 2), ((4.6, -1.8, 0.3), 1.1, 3),
                    ((6.0, -1.0, 0.3), 1.1, 2),
                    ((5.7, 0.8, 0.3), 1.2, 3), ((4.3, 0.9, 0.3), 1.0, 2),
                    ((2.6, 0.9, 0.3), 0.85, 1), ((-4.6, 0.9, 0.3), 0.9, 2),
                    ((-6.0, 0.8, 0.3), 1.0, 2)]:
        _clump(a, p, r, rng, blades=b)
    a.rock((2.2, 1.8, 1.5), loc=(-2.6, -2.45, 0.5), mat="w09_boulder")
    for p in [(-6.0, -2.9, 1.75), (-5.1, -3.15, 1.45), (-4.2, -3.05, 1.2),
              (-0.9, -3.1, 1.15), (0.1, -2.9, 1.6)]:
        _daisy(a, p, rng, r=0.55)
    _clamp(a)
    o = a.finish()
    out.append(kit.tag(o, "hero", collision="box", budget=5000,
                       notes="2-rail ranch fence section, rope X lashings, daisies and rock"))

    # ---------------- parts
    a = fk.Asset("TimberFencePost", "W09 TimberFence part", seed=11)
    _post(a, 5.5, cap=None, groove=(3.7, 3.95), slot=False)
    a.box((0.2, 0.06, 0.85), loc=(0.15, -POST_W / 2 + 0.005, 4.55), mat=END)
    a.box((0.22, 0.06, 0.3), loc=(-0.15, -POST_W / 2 + 0.005, 1.1), mat=END)
    a.box((0.07, 0.06, 1.6), loc=(-0.25, -POST_W / 2 + 0.005, 2.4), mat=END)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500, notes="fence post"))

    a = fk.Asset("TimberFenceRailTop", "W09 TimberFence part", seed=12)
    _rail(a, 11.0, 0.9, 0.8, (0, 0, 0.5), (0, 0, 0), random.Random(12), shear=0.35)
    _clamp(a)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500, notes="top rail beam"))

    a = fk.Asset("TimberFenceRailBottom", "W09 TimberFence part", seed=13)
    _rail(a, 11.0, 0.9, 0.9, (0, 0, 0.5), (0, 0, 0), random.Random(13), shear=0.35)
    _clamp(a)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500, notes="bottom rail beam"))

    a = fk.Asset("TimberFenceRopeJoint", "W09 TimberFence part", seed=14)
    _post(a, 2.5, cap=None, slot=False, w=1.1)
    hw = 1.1 / 2 + 0.17
    t = 0.26
    for z0, z1 in [(0.7, 1.75), (1.75, 0.7)]:
        _loop(a, hw, -hw - 0.05, hw, z0, z1, t, rseg=5)
    for z in (0.55, 0.85, 1.6, 1.9):
        _loop(a, hw, -hw, hw, z, z, t, rseg=5)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500,
                       notes="post stub with thick X rope lashing (4 turns + X)"))

    a = fk.Asset("TimberFencePostCap", "W09 TimberFence part", seed=15)
    a.box((1.5, 1.5, 1.2), mat=WOOD, bevel=0.15, jitter=0.03, base=True)
    a.box((0.12, 0.06, 0.75), loc=(0.2, -0.75 + 0.01, 0.55), mat=END)
    a.box((0.5, 0.06, 0.25), loc=(0, -0.75 + 0.01, 0.13), mat=END)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="box", budget=1500, notes="post cap block"))

    # ---------------- variants
    rng = random.Random(21)
    a = fk.Asset("TimberFenceStraight", "W09 TimberFence variant", seed=21)
    _mound(a, (0, -0.35, 0), 6.6, 1.7)
    _fence_section(a, rng)
    for p, r, b in [((-5.8, -1.3, 0.3), 1.0, 2), ((-4.6, -1.6, 0.3), 0.8, 1),
                    ((0.3, -1.5, 0.3), 0.75, 1), ((4.6, -1.5, 0.3), 0.9, 2),
                    ((5.9, -0.9, 0.3), 0.95, 2), ((5.6, 0.8, 0.3), 0.95, 2),
                    ((-5.7, 0.8, 0.3), 0.85, 1)]:
        _clump(a, p, r, rng, blades=b, lobes=5)
    _daisy(a, (-3.6, -2.7, 1.2), rng, r=0.5)
    _daisy(a, (3.0, -2.6, 1.1), rng, r=0.5)
    _clamp(a)
    o = a.finish()
    out.append(kit.tag(o, "variant", collision="box", budget=3000, notes="clean straight section"))

    rng = random.Random(22)
    a = fk.Asset("TimberFenceCorner", "W09 TimberFence variant", seed=22)
    # irregular L-shaped mound: a lobe along each leg plus a bulge at the corner
    _mound(a, (4.2, -0.8, 0), 5.0, 1.5, rot=0.05)
    _mound(a, (-0.8, 4.2, 0), 1.5, 4.8, rot=-0.08)
    _mound(a, (-0.4, -0.4, 0), 2.2, 2.0, rot=0.4, h=0.5)
    L = 8.0
    _post(a, 6.9, loc=(0, 0, 0), cap=1.6, cap_h=0.7)
    _post(a, POST_H, loc=(L, 0, 0), cap=1.5, cap_h=0.6)
    _post(a, POST_H, loc=(0, L, 0), cap=1.5, cap_h=0.6)
    _rail(a, L + 1.0, 0.85, 0.75, (L / 2 + 0.1, RAIL_Y, TOP_Z), (0, 0.01, 0), rng)
    _rail(a, L + 1.0, 0.85, 0.8, (L / 2, RAIL_Y, BOT_Z), (0, -0.01, 0), rng)
    _rail(a, L + 0.4, 0.85, 0.75, (RAIL_Y, L / 2 + 0.3, TOP_Z), (0, 0, PI / 2), rng)
    _rail(a, L + 0.4, 0.85, 0.8, (RAIL_Y, L / 2 + 0.3, BOT_Z), (0, 0, PI / 2), rng)
    _xlash(a, (0, 0, 0), TOP_Z, t=0.14, rail_d=0.75, wraps=(5.45,))
    _xlash(a, (L, 0, 0), TOP_Z, t=0.14, rail_d=0.75, wraps=(5.05,))
    _xlash(a, (0, L, 0), TOP_Z, t=0.14, rail_d=0.75, rotz=-PI / 2)
    for p, r, b in [((-1.2, -1.4, 0.3), 1.1, 2), ((0.6, -1.7, 0.3), 0.8, 1),
                    ((L + 0.7, -1.3, 0.3), 1.0, 2), ((L - 0.9, -1.6, 0.3), 0.8, 1),
                    ((-1.5, L + 0.4, 0.3), 1.0, 2), ((-1.6, L - 1.2, 0.3), 0.8, 1),
                    ((3.8, -1.6, 0.3), 0.75, 1)]:
        _clump(a, p, r, rng, blades=b, lobes=5)
    _daisy(a, (1.9, -2.6, 1.2), rng, r=0.5)
    a.rock((1.5, 1.3, 1.0), loc=(5.6, -1.7, 0.35), mat="w09_boulder")
    a.rock((1.2, 1.0, 0.8), loc=(-1.8, 4.6, 0.3), mat="w09_boulder")
    _clamp(a)
    o = a.finish()
    out.append(kit.tag(o, "variant", collision="box", budget=3000,
                       notes="90 degree corner, legs 8 studs, capped taller corner post"))

    rng = random.Random(23)
    a = fk.Asset("TimberFenceDamaged", "W09 TimberFence variant", seed=23)
    _mound(a, (0, -0.6, 0), 6.9, 2.0)
    lean = (0, -0.26, 0)
    _post(a, POST_H, loc=(-5.0, 0, 0), rot=lean, cap=1.5, cap_h=0.6)
    _xlash(a, (-5.0, 0, 0), TOP_Z, t=0.14, rail_d=0.75, rot=lean)
    # stub of the snapped top rail still tied to the leaning post
    _rail(a, 2.6, 0.85, 0.75, (-5.05, RAIL_Y, 3.95), lean, rng, broken=1)
    _post(a, POST_H, loc=(5.0, 0, 0), cap=1.5, cap_h=0.6)
    # snapped top rail hanging from the right post
    _rail(a, 6.5, 0.85, 0.75, (2.0, RAIL_Y, 3.3), (0, -0.24, 0), rng, broken=-1)
    # bottom rail dropped and tilted to the ground
    _rail(a, 9.5, 0.85, 0.8, (0.6, RAIL_Y - 0.1, 1.2), (0, -0.17, 0.05), rng)
    # loose rail lying on the ground, pulled out in front, splintered end
    _rail(a, 4.6, 0.75, 0.75, (1.6, -3.3, 0.38), (0, 0, 0.42), rng, broken=1)
    _xlash(a, (5.0, 0, 0), 3.95, t=0.14, rail_d=0.75, wraps=(5.05,))
    # loose rope end hanging off the right post
    a.tube_loop([(4.35, -0.7, 3.5), (4.15, -0.9, 2.8), (4.3, -1.0, 2.1), (4.1, -1.15, 1.5)],
                0.13, mat=ROPE, rseg=4, closed=False)
    for p, r, b in [((-6.1, -1.3, 0.3), 1.1, 2), ((-4.0, -1.8, 0.3), 0.85, 1),
                    ((5.9, -1.1, 0.3), 1.0, 2), ((5.5, 0.9, 0.3), 1.0, 2),
                    ((-0.6, -1.7, 0.3), 0.75, 1), ((-5.6, 0.9, 0.3), 0.85, 1)]:
        _clump(a, p, r, rng, blades=b, lobes=5)
    _daisy(a, (-4.6, -3.0, 1.3), rng, r=0.5)
    _daisy(a, (6.4, -2.7, 1.4), rng, r=0.5)
    a.rock((1.7, 1.4, 1.1), loc=(-2.7, -1.8, 0.4), mat="w09_boulder")
    _clamp(a)
    o = a.finish()
    out.append(kit.tag(o, "variant", collision="box", budget=3000,
                       notes="broken fence: leaning post, snapped rails, loose rail and rope"))
    return out
