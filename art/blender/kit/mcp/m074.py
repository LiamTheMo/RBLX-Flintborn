"""074 Fire and Light Station (references/074.png, the sheet titled "71 - Fire and Light Station") on the shared
library (kit_parts / kit_build): a cooking campfire. Three square-ish timber poles stand as a tripod over the fire, a
rope bind of three turns round the crossing, a two-link iron chain hanging from the crotch to the bail of an iron
cauldron; three split logs in the centre (two on the ground, the third leaning on one of them) and a ring of nine
faceted stones round them. The flames are NOT geometry (the sheet: "Fire is a separate VFX element"): a `campfire`
socket and a `heat_glow` socket sit at the fire centre.

    import importlib, kit_parts, kit_build, m074
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m074); m074.build()

Build frame (studs): front -Y, +X right, ground z 0, the fire centre at x 0 / y 0. The layout is drawn in a VIEW frame
whose front (-Y) faces the sheet's hero camera, and placed into the build frame turned by HERO_AZ about Z, so the hero
render at (HERO_AZ, el) sees the tripod's front pair symmetric and a stone straight in front, as the sheet's
front three-quarter draws them (spec "Brief": hero governs over the ortho cells).
Names:
- TripodCookfire (hero): everything above, one object of closed shells (no booleans). Collision hull.
- TripodCookfirePole, TripodCookfireRopeBind, TripodCookfireHangingPot (pot, lugs, bail and the two chain links),
  TripodCookfireLog, TripodCookfireStone.
Colour is by role and position, never by facing. See M074_spec.md.
"""
import math

from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_build as B
import kit_parts as P

NUM, TITLE = 74, "Fire and Light Station"
HERO = "TripodCookfire"
POLE_P, BIND_P, POT_P = "TripodCookfirePole", "TripodCookfireRopeBind", "TripodCookfireHangingPot"
LOG_P, STONE_P = "TripodCookfireLog", "TripodCookfireStone"

WOOD, WOOD_END, WOOD_DEEP = "m074_wood", "m074_wood_end", "m074_wood_deep"
ROPE, ROPE_DEEP = "m074_rope", "m074_rope_deep"
IRON, IRON_IN = "m074_iron", "m074_iron_in"
STONE = "m074_stone"

# key -> (hex, roughness, metal, emission, low specular). Stage 4 (spec "Stage 4"): calibrated against the sheet.
PALETTE = {
    WOOD: ("#8B5429", 0.85, 0.0, 0.0, True),
    WOOD_END: ("#B07443", 0.85, 0.0, 0.0, True),
    WOOD_DEEP: ("#4E2C15", 0.9, 0.0, 0.0, True),
    ROPE: ("#CCAE78", 0.95, 0.0, 0.0, True),
    ROPE_DEEP: ("#93744A", 0.95, 0.0, 0.0, True),
    IRON: ("#383538", 0.55, 0.35, 0.0, False),
    IRON_IN: ("#1C1A1C", 0.7, 0.2, 0.0, False),
    STONE: ("#72727E", 0.9, 0.0, 0.0, True),
}
# calibration targets: the sheet's rendered medians (spec "Stage 4")
TARGETS = {WOOD: ((0xA8, 0x64, 0x2F), "brown"), ROPE: ((0xF0, 0xBE, 0x72), "brown"),
           IRON: ((0x40, 0x3C, 0x3C), "stone"), STONE: ((0x8E, 0x8B, 0x91), "stone")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)

# ---- layout (spec "Brief": stone ring about 8.8 across, tripod top 6.44 since the R1 fix, pot 2.0 across) --------------
HERO_AZ = -30.0                 # the hero camera's azimuth; the view frame is turned by this into the build frame
SEAT = 0.02                     # how far a piece sinks into what holds it
# stones: nine, the three gaps at the pole feet wider (POLE_GAP deg between stone centres) than the other six
N_STONE, RING_R, POLE_GAP = 9, 3.45, 45.0
STONE_W, STONE_D, STONE_H = 2.28, 2.15, 1.25     # tangential, radial, height (Fix R1: 1.40 -> 1.25, flatter)
# (height frac, size frac, points, phase): a squat rounded block, a point on each side's middle of the wide rings so
# neighbours meet; footprints a superellipse (STONE_SQ < 1 squarer) like the sheet's boxy boulders
STONE_RINGS = [(0.0, 0.88, 10, 0.0), (0.22, 1.0, 10, 0.0), (0.62, 0.96, 10, math.pi / 10), (0.88, 0.82, 8, 0.0),
               (1.0, 0.70, 6, math.pi / 6)]   # Fix R1: top ring 0.58 -> 0.70 (the sheet's flat-topped boulders)
STONE_SQ = 0.75
# tripod: feet at FOOT_R on the ground at FOOT_AZ (view frame), axes through the crossing at CROSS_Z, each passing
# TWIST to the side of the centre (a twisted tripod: the poles rest on each other instead of crossing through)
FOOT_AZ = (-150.0, -30.0, 90.0)
FOOT_R, CROSS_Z, TWIST = 3.28, 5.30, 0.25
POLE_H, POLE_CH, POLE_EXT = 0.23, 0.06, 1.20      # half width, chamfer, length past the crossing (Fix R1: tops clear of the bind)
POLE_GE, POLE_GD = 0.03, 0.045                     # seam groove half width and depth
# rope bind: closed twisted turns round the three poles, centred at these heights
BIND_R, BIND_SIDES = 0.14, 6
BIND_Z = (CROSS_Z - 0.26, CROSS_Z, CROSS_Z + 0.26)   # Fix R1: centred on the crossing, the chain shows below it
FRAP_AZ = (-90.0, 30.0, 150.0)  # the crossing wraps: one on each face between two poles (view frame)
FRAP_R, FRAP_SPAN = 0.10, 40.0  # rope radius; each diagonal's ends this many deg either side of the face centre
# Fix R1: one long diagonal per face (a neat spiral frapping over the turns), not an X of short straight sticks
FRAP_SG = (1,)                  # the diagonals on each face: (1, -1) an X, (1,) one diagonal
FRAP_T = tuple(k / 4 for k in range(9))   # path samples, in turns from the bottom turn's centreline to the top one's
# chain and pot
LINK_W, LINK_H, LINK_R = 0.08, 0.10, 0.035          # link centreline half width, half straight, wire radius
POT_N = 14
# (radius, z) outer profile from the bottom up, then the inner wall down to the inner floor
POT_OUT = [(0.55, 0.0), (0.80, 0.11), (0.95, 0.39), (1.00, 0.71), (0.95, 1.06), (0.84, 1.31), (0.86, 1.35),
           (0.90, 1.38), (0.90, 1.54), (0.85, 1.59)]
POT_IN = [(0.75, 1.57), (0.76, 1.29), (0.80, 0.92), (0.62, 0.48)]
POT_FLOOR = 0.46
LUG = (0.10, 0.14, 0.24)        # lug half thickness (radial), half width, height
LUG_Z = 1.30                    # lug bottom (pot frame)
BAIL_RISE = 0.80                # bail apex over the lug tops
BAIL_R, BAIL_SIDES = 0.05, 6
# logs (view frame): (p0 xy, p1 xy) of the two ground logs and the leaning one's foot and head
LOG_HU, LOG_HV, LOG_CH = 0.32, 0.28, 0.05
GROOVE_E, GROOVE_D = 0.035, 0.05
LOG_LEFT = ((-1.65, 0.46), (0.46, -0.10))
LOG_RIGHT = ((0.92, 0.14), (2.05, 0.32))
LOG_LEAN = ((0.70, -1.58), (-0.22, 0.48))         # foot (on the ground) toward the camera-right, head over LOG_LEFT
FIRE = (0.0, 0.0, 0.30)          # VFX socket: flames from the logs' middle height
GLOW = (0.0, 0.0, 0.55)

VIEW = Matrix.Rotation(math.radians(HERO_AZ), 4, "Z")


def vxy(az, r, z=0.0):
    a_ = math.radians(az)
    return Vector((r * math.cos(a_), r * math.sin(a_), z))


# ---- stones -----------------------------------------------------------------------------------------------------------
def stone_azimuths():
    """Stone centres (view frame, deg): one straight in front (-90), the gaps at the three feet POLE_GAP wide and the
    other six equal."""
    small = (360.0 - 3 * POLE_GAP) / 6
    out, az = [], -90.0
    # from the front stone counter-clockwise: the gap sequence that centres a wide gap on each foot (-30, 90, 210)
    gaps = [small, POLE_GAP, small, small, POLE_GAP, small, small, POLE_GAP, small]
    for g in gaps:
        out.append(az)
        az += g
    return out, gaps


def stone(a, k, az, name="stone", at_ring=True, flank=False):
    """One ring stone: a squat faceted dome (STONE_RINGS) with its long side along the ring; a stone beside a pole
    foot (flank) a touch narrower so the leaning pole clears it."""
    r = P.rng(f"{name}{k}")
    s = r.uniform(0.95, 1.02)
    if flank:
        s = min(s, 0.92)
    size = (STONE_W * s, STONE_D * r.uniform(0.94, 1.04), STONE_H * r.uniform(0.92, 1.06))
    loc = vxy(az, RING_R) if at_ring else Vector((0, 0, 0))
    rot = math.radians(az + 90.0 + r.uniform(-3, 3)) if at_ring else 0.0
    m = Matrix.Translation(loc) @ Matrix.Rotation(rot, 4, "Z")
    pts = []
    for h_, rf, n, ph in STONE_RINGS:
        for j in range(n):
            th = 2 * math.pi * j / n + ph + r.uniform(-0.07, 0.07)
            c, s_ = math.cos(th), math.sin(th)
            rr = rf * r.uniform(0.96, 1.03) if 0 < h_ < 1 else rf
            x = size[0] / 2 * rr * math.copysign(abs(c) ** STONE_SQ, c)
            y = size[1] / 2 * rr * math.copysign(abs(s_) ** STONE_SQ, s_)
            z = h_ * size[2] * (r.uniform(0.95, 1.05) if 0 < h_ < 1 else 1.0)
            pts.append(m @ Vector((x, y, z)))
    p = P.hull(a, pts, STONE, name=f"{name}{k}", kind="stone", amp=0.03)
    P.texture(a, p.vs, 0.05, P.seed(f"{name}{k}"), scale=0.9)
    return p


def stones(a):
    azs, gaps = stone_azimuths()
    return [stone(a, k, az, flank=POLE_GAP in (gaps[k], gaps[k - 1])) for k, az in enumerate(azs)]


# ---- tripod -----------------------------------------------------------------------------------------------------------
def pole_axis(i):
    """(foot, unit axis up, top) of pole i in the view frame."""
    az = FOOT_AZ[i]
    foot = vxy(az, FOOT_R)
    t = Vector((-math.sin(math.radians(az)), math.cos(math.radians(az)), 0.0))
    c = Vector((0.0, 0.0, CROSS_Z)) + t * TWIST
    x = (c - foot).normalized()
    return foot, x, c + x * POLE_EXT


def pole_frame(x):
    """(u, v) across the pole: u horizontal, v the in-plane 'up' square to the axis."""
    v = Vector((0, 0, 1)) - x * x.z
    v.normalize()
    u = v.cross(x)
    return u, v


def pole_sec():
    """The pole's section (u across, v up): a 0.46 square chamfered POLE_CH with a shallow V groove down the middle of
    its upper face and both side faces (the sheet's poles read as split timber with a seam line)."""
    h, c, e, d = POLE_H, POLE_CH, POLE_GE, POLE_GD
    return [(-h + c, -h), (h - c, -h), (h, -h + c), (h, -e), (h - d, 0.0), (h, e), (h, h - c), (h - c, h), (e, h),
            (0.0, h - d), (-e, h), (-h + c, h), (-h, h - c), (-h, e), (-h + d, 0.0), (-h, -e), (-h, -h + c)]


def pole_rings(i):
    """Two rings of pole_sec(): the foot cut flat on z 0, the top cut square to the axis."""
    foot, x, top = pole_axis(i)
    u, v = pole_frame(x)
    bot, tp = [], []
    for su, sv in pole_sec():
        q = foot + u * su + v * sv
        bot.append(q - x * (q.z / x.z))          # slide along the axis to the ground plane
        tp.append(top + u * su + v * sv)
    return bot, tp


def pole(a, i, name="pole"):
    """One tripod pole: side quads (the three grooves WOOD_DEEP), the foot cap, the end grain on top WOOD_END; both
    caps ear-clipped (the grooved section is concave)."""
    bot, tp = pole_rings(i)
    sec = pole_sec()
    n = len(sec)
    tris = P.earclip(sec)
    faces = [[t[2], t[1], t[0]] for t in tris] + [[n + t[0], n + t[1], n + t[2]] for t in tris]
    keys = [WOOD] * len(tris) + [WOOD_END] * len(tris)
    groove = {j for j, (su, sv) in enumerate(sec) if (su, sv) in ((POLE_H - POLE_GD, 0.0), (0.0, POLE_H - POLE_GD),
                                                                  (-POLE_H + POLE_GD, 0.0))}
    for j in range(n):
        faces.append([j, (j + 1) % n, n + (j + 1) % n, n + j])
        keys.append(WOOD_DEEP if (j in groove or (j + 1) % n in groove) else WOOD)
    p = P.shell(a, bot + tp, faces, WOOD, keys=keys, name=f"{name}{i}", kind="pole")
    P.texture(a, p.vs, 0.035, P.seed(f"{name}{i}"), scale=0.6)
    return p


def pole_section(z):
    """The three poles' cross-section points at height z (view frame): each pole's 8 long edges cut by the plane."""
    out = []
    for i in range(3):
        bot, tp = pole_rings(i)
        for b, t in zip(bot, tp):
            f = (z - b.z) / (t.z - b.z)
            out.append(b.lerp(t, f))
    return out


def round_loop(pts, off, z, seg=45.0, min_gap=0.09):
    """A closed loop at height z exactly `off` outside the convex hull of pts (xy): straight runs along the hull's
    edges and every corner rounded on an arc (points every `seg` deg), so a rope round it reads round, not as a
    polygon of flat plates. An even number of points (twisted closed ropes need one)."""
    H = []
    for q in P.hull2([(p.x, p.y) for p in pts]):         # drop near-duplicate corners (a tiny edge's normal is noise)
        if not H or math.hypot(q[0] - H[-1][0], q[1] - H[-1][1]) > 0.03:
            H.append(q)
    if len(H) > 2 and math.hypot(H[0][0] - H[-1][0], H[0][1] - H[-1][1]) <= 0.03:
        H.pop()
    n = len(H)
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(H[i - 1]), Vector(H[i]), Vector(H[(i + 1) % n])
        ea, eb = (p1 - p0).normalized(), (p2 - p1).normalized()
        a0 = math.atan2(-ea.x, ea.y)                # outward normals of a counter-clockwise polygon
        a1 = math.atan2(-eb.x, eb.y)
        turn = (a1 - a0) % (2 * math.pi)
        a1 = a0 + (turn if turn < math.pi else 0.0)     # a hair-reflex corner of near-collinear points: no arc
        k =max(1, math.ceil(math.degrees(a1 - a0) / seg))
        for j in range(k + 1):
            th = a0 + (a1 - a0) * j / k
            q = Vector((p1.x + off * math.cos(th), p1.y + off * math.sin(th), z))
            if not out or (q - out[-1]).length > min_gap:
                out.append(q)
    if (out[0] - out[-1]).length <= min_gap:
        out.pop()
    while len(out) % 2:
        k = max(range(len(out)), key=lambda j: (out[(j + 1) % len(out)] - out[j]).length)
        out.insert(k + 1, (out[k] + out[(k + 1) % len(out)]) / 2)
    return out


def bind(a, name="bind"):
    """Three closed turns (rings aligned, twist=False, so they read as round coils) round the bundle at BIND_Z, centred
    on the crossing, each round its own height's section (the poles spread
    away from the crossing), inner strands sunk SEAT into the poles, neighbours touching."""
    out, loops = [], []
    for t, z in enumerate(BIND_Z):
        loop = round_loop(pole_section(z), BIND_R - SEAT, z)
        loops.append(loop)
        out.append(P.rope(a, loop, BIND_R, ROPE, ROPE_DEEP, sides=BIND_SIDES, closed=True, twist=False, up=(0, 0, 1),
                          name=f"{name}{t}", kind="rope_bind"))
    for az in FRAP_AZ:
        out += frapping(a, loops, az, f"{name}_x{int(az) % 360}")
    return out


def loop_at(loop, az):
    """The point of a closed horizontal loop in direction az (deg) from the z axis (ray against its segments)."""
    d = Vector((math.cos(math.radians(az)), math.sin(math.radians(az))))
    best = None
    for j in range(len(loop)):
        p, q = loop[j].to_2d(), loop[(j + 1) % len(loop)].to_2d()
        e = q - p
        den = d.x * e.y - d.y * e.x
        if abs(den) < 1e-9:
            continue
        t = (p.x * e.y - p.y * e.x) / den               # along the ray
        s = (p.x * d.y - p.y * d.x) / den               # along the segment
        if t > 0 and -1e-6 <= s <= 1 + 1e-6 and (best is None or t < best):
            best = t
    return Vector((d.x * best, d.y * best, loop[0].z))


def frapping(a, loops, az, name):
    """The diagonal wraps over the turns on the face of the bind at az (between two poles; the junction detail's
    crossing loops), one per sign in FRAP_SG: each runs from inside the bottom turn on one side, out over the middle
    turn, into the top turn on the other side, sampled at FRAP_T so it follows the coils; a second (an X) is lifted
    FRAP_R x 1.8 at the crossing so the two lie on each other, not through."""
    out = []
    for k, sg in enumerate(FRAP_SG):
        lift = (2 * FRAP_R - 0.03) if k else 0.0
        pts, rad = [], []
        for t in FRAP_T:
            i0 = min(int(t), 1)
            f = t - i0
            ang = az + sg * FRAP_SPAN * (t - 1.0)
            p = loop_at(loops[i0], ang).lerp(loop_at(loops[i0 + 1], ang), f)
            radial = Vector((p.x, p.y, 0.0)).normalized()
            sink = 0.06 if t in (FRAP_T[0], FRAP_T[-1]) else 0.02   # the ends sit in the outer turns (rope in rope <= 0.08)
            pts.append(p + radial * (BIND_R + FRAP_R - sink + lift * max(0.0, 1.0 - abs(t - 1.0) * 1.6)))
            rad.append(FRAP_R)
        out.append(vrope(a, pts, rad, name=f"{name}{k}", kind="rope_frap"))
    return out


def vrope(a, path, radii, sides=6, name=None, kind="rope"):
    """An open rope whose radius changes along the path (m051 vrope, rings aligned and 6-sided since the R1 fix so it
    reads round): one strand ROPE_DEEP, flat end caps, registered in P.ROPES."""
    Pp = [Vector(p) for p in path]
    N = len(Pp)
    upv = P.up_for(Pp)
    rings = []
    for i in range(N):
        tin = (Pp[i] - Pp[max(i - 1, 0)]) if i else (Pp[1] - Pp[0])
        tout = (Pp[min(i + 1, N - 1)] - Pp[i]) if i < N - 1 else tin
        tin, tout = tin.normalized(), tout.normalized()
        T = (tin + tout).normalized()
        U = upv - upv.dot(T) * T
        if U.length < 1e-6:
            U = T.orthogonal()
        U.normalize()
        V = T.cross(U)
        Bv = tout - tin
        bend = Bv.length > 1e-6
        if bend:
            Bv.normalize()
        sc = 1.0 / max(0.5, tin.dot(T)) - 1.0
        ring = []
        for k in range(sides):
            ang = 2 * math.pi * k / sides                   # rings aligned: a round coil, not an antiprism zig-zag
            off = (U * math.cos(ang) + V * math.sin(ang)) * radii[i]
            if bend:
                off += Bv * off.dot(Bv) * sc
            ring.append(Pp[i] + off)
        rings.append(ring)
    pts = [p for rg in rings for p in rg]
    faces, keys = [], []
    for i in range(N - 1):
        for k in range(sides):
            a0, a1 = i * sides + k, i * sides + (k + 1) % sides
            b0, b1 = (i + 1) * sides + k, (i + 1) * sides + (k + 1) % sides
            faces += [[a0, a1, b0], [a1, b1, b0]]
            keys += [ROPE_DEEP if k == 0 else None] * 2
    faces.append(list(reversed(range(sides))))
    faces.append([(N - 1) * sides + k for k in range(sides)])
    keys += [None, None]
    p = P.shell(a, pts, faces, ROPE, keys=keys, recalc=False, name=name, kind=kind, amp=0.03)
    if name:
        P.ROPES.append({"name": p.name, "ends": [list(P.XF[-1] @ Pp[0]), list(P.XF[-1] @ Pp[-1])], "rt": radii[0]})
    return p


# ---- chain, bail and pot ----------------------------------------------------------------------------------------------
def link_path(c, e, n_arc=4):
    """A link's centreline: a stadium in the plane (e, Z) round centre c, straights LINK_H either side of c."""
    pts = []
    for j in range(n_arc):
        th = math.pi * j / (n_arc - 1)
        pts.append(c + e * (LINK_W * math.cos(th)) + Vector((0, 0, LINK_H + LINK_W * math.sin(th))))
    for j in range(n_arc):
        th = math.pi + math.pi * j / (n_arc - 1)
        pts.append(c + e * (LINK_W * math.cos(th)) + Vector((0, 0, -LINK_H + LINK_W * math.sin(th))))
    return pts


def link(a, c, e, name):
    return P.rope(a, link_path(c, e), LINK_R, IRON, None, sides=4, closed=True, twist=False, up=e.cross(Vector((0, 0, 1))),
                  name=name, kind="chain", amp=0.02)


def crotch_z(tree, c, e, ref_z):
    """Lowest hit straight up (from ref_z) over a link's top wire: the height its outer top may rise to."""
    hits = []
    for s in (-1.0, -0.5, 0.0, 0.5, 1.0):
        for w in (-LINK_R, 0.0, LINK_R):
            o = c + e * (s * (LINK_W + LINK_R)) + e.cross(Vector((0, 0, 1))) * w
            o.z = ref_z
            h = tree.ray_cast(P.here(o), Vector((0, 0, 1)), 10.0)
            if h[0] is not None:
                hits.append(h[0].z)
    return min(hits)


def pot_body(a, c, name="pot"):
    """The cauldron: one lathe shell (POT_N sides) of the outer profile up over the thick rim and down the inner wall
    to a floor POT_FLOOR above the bottom; outside IRON, the inner wall and floor IRON_IN."""
    n = POT_N
    prof = POT_OUT + POT_IN
    pts = [c + Vector((0, 0, 0))]
    for r, z in prof:
        for k in range(n):
            th = 2 * math.pi * (k + 0.5) / n
            pts.append(c + Vector((r * math.cos(th), r * math.sin(th), z)))
    pts.append(c + Vector((0, 0, POT_FLOOR)))
    last = len(pts) - 1
    faces, keys = [], []
    for k in range(n):                                # bottom fan
        faces.append([0, 1 + (k + 1) % n, 1 + k])
        keys.append(IRON)
    n_out = len(POT_OUT)
    for i in range(len(prof) - 1):
        for k in range(n):
            k1 = (k + 1) % n
            faces.append([1 + i * n + k, 1 + i * n + k1, 1 + (i + 1) * n + k1, 1 + (i + 1) * n + k])
            keys.append(IRON if i < n_out - 1 else IRON_IN)
    base = 1 + (len(prof) - 1) * n
    for k in range(n):                                # inner floor fan
        faces.append([base + k, base + (k + 1) % n, last])
        keys.append(IRON_IN)
    p = P.shell(a, pts, faces, IRON, keys=keys, name=name, kind="pot", amp=0.02)
    P.texture(a, p.vs, 0.02, P.seed(name), scale=1.6)
    return p


def lug_frame(c, e):
    """(centre of the lug's outer face top, radial e) of the lug on side e."""
    r_rim = POT_OUT[-3][0] * math.cos(math.pi / POT_N)       # the rim band's flat (the lug sits on a facet's middle)
    return c + e * (r_rim + LUG[0] - SEAT) + Vector((0, 0, LUG_Z))


def lug(a, c, e, name):
    """A small iron ear on the rim band, seated SEAT into it: a box LUG[0] proud (radial half thickness), the bail end
    enters its top."""
    m = lug_frame(c, e)
    t = Vector((0, 0, 1)).cross(e)
    pts = []
    for z in (0.0, LUG[2]):
        for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            pts.append(m + e * (su * LUG[0]) + t * (sv * LUG[1]) + Vector((0, 0, z)))
    return P.box_pts(a, pts, IRON, name=name, kind="lug", amp=0.02)


def bail_path(c, e, apex_z, n=11):
    """The bail: from one lug top up over the pot to the other, a round arch in the plane (e, Z) slightly peaked at
    the apex (where it hangs in the lower link); its ends go 0.04 down into the lugs."""
    m0 = lug_frame(c, e)
    half = (m0 - c).dot(e)
    z0 = m0.z + LUG[2] - 0.04
    rise = apex_z - z0
    pts = []
    for j in range(n):
        th = math.pi * j / (n - 1)
        x = half * math.cos(th)
        zz = z0 + rise * (math.sin(th) ** 0.85)
        pts.append(c + e * x + Vector((0, 0, zz - c.z)))
    return pts


def bail(a, c, e, apex_z, name="bail"):
    return P.rope(a, bail_path(c, e, apex_z), BAIL_R, IRON, None, sides=BAIL_SIDES, twist=False,
                  up=e.cross(Vector((0, 0, 1))), name=name, kind="bail", amp=0.02)


def hanging_pot(a, top_z, xy=(0.0, 0.0), tag=""):
    """The chain (two links, the upper one's top at top_z), the bail hooked in the lower link and the pot hung from
    the bail; everything on the vertical through xy. Returns the pot's bottom z."""
    e1, e2 = Vector((1, 0, 0)), Vector((0, 1, 0))
    c1 = Vector((xy[0], xy[1], top_z - LINK_R - LINK_H - LINK_W))
    link(a, c1, e1, tag + "link0")
    low1 = c1.z - LINK_H - LINK_W                       # lower link 0's bottom centreline
    c2 = Vector((xy[0], xy[1], low1 + 2 * LINK_R - 0.01 - LINK_H - LINK_W))      # link 1's top rests on it
    link(a, c2, e2, tag + "link1")
    low2 = c2.z - LINK_H - LINK_W
    apex = low2 + LINK_R + BAIL_R - 0.01            # the bail's apex centreline resting on link 1's bottom wire
    # pot frame: the bail ends 0.04 into the lug tops, the lug tops at LUG_Z + LUG[2] in the pot frame
    z_lugtop = apex - BAIL_RISE + 0.04
    pot_c = Vector((xy[0], xy[1], z_lugtop - LUG_Z - LUG[2]))
    pot_body(a, pot_c, tag + "pot")
    for s, nm in ((1, "lug_r"), (-1, "lug_l")):
        lug(a, pot_c, e1 * s, tag + nm)
    bail(a, pot_c, e1, apex, tag + "bail")
    return pot_c.z


# ---- logs -------------------------------------------------------------------------------------------------------------
def log_section():
    """The split log's section (u across, v up): a chamfered 0.56 x 0.50 block with a V groove along its top (the
    split line, off centre) and one along its +u side (the sheet's log detail)."""
    hu, hv, ch, e, d = LOG_HU, LOG_HV, LOG_CH, GROOVE_E, GROOVE_D
    gt, gs = 0.06, -0.03
    return [(-hu + ch, -hv), (hu - ch, -hv), (hu, -hv + ch), (hu, gs - e), (hu - d, gs), (hu, gs + e), (hu, hv - ch),
            (hu - ch, hv), (gt + e, hv), (gt, hv - d), (gt - e, hv), (-hu + ch, hv), (-hu, hv - ch), (-hu, -hv + ch)]


def log_colour(L):
    """Groove faces WOOD_DEEP, the cut ends WOOD_END, the rest WOOD (by place in the section, never by facing)."""
    def fn(q):
        if q.s < 1e-3 or q.s > L - 1e-3:
            return WOOD_END
        if q.v > LOG_HV - GROOVE_D - 0.005 and abs(q.u - 0.06) < GROOVE_E + 0.005:
            return WOOD_DEEP
        if q.u > LOG_HU - GROOVE_D - 0.005 and abs(q.v + 0.03) < GROOVE_E + 0.005:
            return WOOD_DEEP
        return WOOD
    return fn


def log_beam(a, p0, p1, name):
    """A split log from p0 to p1 (axis): the grooved section's two rings, side quads, and both ends ear-clipped (the
    section is concave, so the library's even-ring cap quads would cross)."""
    sec = log_section()
    n = len(sec)
    x, u, v, L = P._axes(p0, p1, Vector((0, 0, 1)))
    p0 = Vector(p0)
    pts = [p0 + u * su + v * sv for su, sv in sec] + [p0 + x * L + u * su + v * sv for su, sv in sec]
    tris = P.earclip(sec)
    faces = [[t[2], t[1], t[0]] for t in tris] + [[n + t[0], n + t[1], n + t[2]] for t in tris]
    faces += [[j, (j + 1) % n, n + (j + 1) % n, n + j] for j in range(n)]
    fn = log_colour(L)
    keys = []
    for f in faces:
        c = sum((pts[i] for i in f), Vector()) / len(f) - p0
        keys.append(fn(P.Local(c.dot(x), c.dot(u), c.dot(v))))
    p = P.shell(a, pts, faces, WOOD, keys=keys, name=name, kind="log")
    P.texture(a, p.vs, 0.035, P.seed(name), scale=0.6)
    return p


def ground_log(a, p0, p1, name):
    return log_beam(a, Vector((p0[0], p0[1], LOG_HV)), Vector((p1[0], p1[1], LOG_HV)), name)


def lean_pose(support):
    """(p0, p1) of the leaning log: its foot's bottom edge on the ground at LOG_LEAN[0], heading over LOG_LEAN[1],
    tilted until it rests SEAT deep on the support log's (view-frame) points. support: [(a, b)] edge segments."""
    f, h = Vector((*LOG_LEAN[0], 0.0)), Vector((*LOG_LEAN[1], 0.0))
    d = (h - f).normalized()
    L = (h - f).length
    samples = [sa.lerp(sb, t / 24) for sa, sb in support for t in range(25)]

    def pose(th):
        x = d * math.cos(th) + Vector((0, 0, math.sin(th)))
        u = Vector((0, 0, 1)).cross(x).normalized()
        v = x.cross(u)
        p0 = f + v * LOG_HV                            # axis start: the foot's bottom edge on the ground
        return p0, x, u, v

    def pen(th):
        p0, x, u, v = pose(th)
        worst = -9.0
        for q in samples:
            r = q - p0
            s, uu, vv = r.dot(x), r.dot(u), r.dot(v)
            if 0.0 < s < L and abs(uu) < LOG_HU:
                worst = max(worst, vv + LOG_HV)
        return worst
    lo, hi = 0.0, math.radians(40)
    for _ in range(40):
        mid = (lo + hi) / 2
        if pen(mid) > SEAT:
            lo = mid
        else:
            hi = mid
    p0, x, u, v = pose(hi)
    return p0, p0 + x * L, x


def log_edges(p0, p1):
    """The ground log's long edges (top and chamfer corners) in the view frame, as segments."""
    p0 = Vector((p0[0], p0[1], LOG_HV))
    p1 = Vector((p1[0], p1[1], LOG_HV))
    x, u, v, L = P._axes(p0, p1, Vector((0, 0, 1)))
    return [(p0 + u * su + v * sv, p1 + u * su + v * sv) for su, sv in log_section()]


def logs(a):
    ground_log(a, *LOG_LEFT, "log_left")
    ground_log(a, *LOG_RIGHT, "log_right")
    p0, p1, x = lean_pose(log_edges(*LOG_LEFT))
    L = (p1 - p0).length
    up = Vector((0, 0, 1))
    # the foot's lowest point: sink the leaning log so its bottom foot corner sits on z 0
    u = up.cross(x).normalized()
    v = x.cross(u)
    zmin = min((p0 + u * su + v * sv).z for su, sv in log_section())
    p0 -= Vector((0, 0, zmin))
    p1 -= Vector((0, 0, zmin))
    log_beam(a, p0, p1, "log_lean")
    P.GEO["log_lean_tilt_deg"] = [round(math.degrees(math.asin(x.z)), 2)]


# ---- assemblies -------------------------------------------------------------------------------------------------------
def tripod(a):
    ps = [pole(a, i) for i in range(3)]
    bind(a)
    return ps


def bm_tree(a):
    """A BVH of everything built so far (build frame), for the rays that find the crotch the chain hangs from."""
    tree = BVHTree.FromPolygons([v.co.copy() for v in a.bm.verts], [[v.index for v in f.verts] for f in a.bm.faces])
    return tree


def hero_all(a):
    with P.frame(VIEW, ""):
        stones(a)
        logs(a)
        tripod(a)
        a.bm.verts.ensure_lookup_table()
        a.bm.verts.index_update()
        tree = bm_tree(a)
        c = Vector((0.0, 0.0, 0.0))
        top = crotch_z(tree, c, Vector((1, 0, 0)), CROSS_Z - 2.0) + SEAT
        P.GEO["chain_top"] = [round(top, 3)]
        bottom = hanging_pot(a, top)
        P.GEO["pot_bottom"] = [round(bottom, 3)]


# ---- parts (the sheet's exploded construction) ------------------------------------------------------------------------
def pole_part(a):
    """Tripod Pole: the hero's front-left pole (feet flat on z 0)."""
    pole(a, 0)


def bind_part(a):
    """Rope Bind: the hero's three turns, without the poles."""
    bind(a)


def pot_part(a):
    """Hanging Pot (+ hanger): the cauldron, lugs, bail and the two chain links, as hung in the hero."""
    hanging_pot(a, 2.20 + 1.62)


def log_part(a):
    """Log Piece: the hero's long ground log, lying on the ground."""
    ground_log(a, (-1.2, 0.0), (1.2, 0.0), "log")


def stone_part(a):
    """Stone: one ring stone."""
    stone(a, 0, -90.0, at_ring=False)


PARTS = ((POLE_P, pole_part), (BIND_P, bind_part), (POT_P, pot_part), (LOG_P, log_part), (STONE_P, stone_part))
NOTES = {
    HERO: "Tripod cookfire (sheet 074, Fire and Light Station): 8.69 x 8.95 x 6.44. Nine faceted stones (2.2 x 2.0 x "
          "1.2) in a packed ring; three 0.46-square grooved poles as a twisted tripod (feet in the ring's three wide "
          "gaps, tops splayed clear of the bind) with a three-turn rope bind on the crossing and three diagonal wraps; "
          "a two-link iron chain from the crotch to the "
          "bail of a 2.0-wide iron cauldron (bottom 1.81); three split logs in the centre. The flames are a campfire "
          "VFX socket, not geometry; heat_glow socket over the logs.",
    POLE_P: "Tripod Pole: one chamfered 0.46-square pole with three seam grooves, foot cut flat, end grain on top",
    BIND_P: "Rope Bind: three round rope turns and three diagonal wraps, as they bind the tripod",
    POT_P: "Hanging Pot (+ hanger): iron cauldron with a thick rim, two lugs, bail and two chain links",
    LOG_P: "Log Piece: a split log, chamfered, with its split groove",
    STONE_P: "Stone: one faceted ring stone",
}
COLLISION = {HERO: "hull", POLE_P: "hull", BIND_P: "none", POT_P: "hull", LOG_P: "box", STONE_P: "hull"}
BUDGETS = {HERO: 4000}
TARGET_SIZE = ((8.9, 0.3), (8.9, 0.3), (6.45, 0.15))
VIEWS = {"f34_sheet": (HERO_AZ, 20), "r34_sheet": (HERO_AZ + 180, 20), "front_sheet": (0, 12),
         "side_sheet": (90, 12), "rear_sheet": (180, 12), "top_sheet": (0, 89.9)}
EXPLODED = {POLE_P: (-1.0, 0.0, 0.0), BIND_P: (1.6, 0.0, 0.0), POT_P: (3.6, 0.0, 0.0), LOG_P: (6.4, 0.0, 0.0),
            STONE_P: (9.0, 0.0, 0.0)}
CLOSE = {"junction_cu": dict(at=(0.0, 0.0, 5.5), r=1.5, az=HERO_AZ, el=15),
         "junction_front_cu": dict(at=(0.0, 0.0, 5.5), r=1.5, az=0, el=12),
         "junction_top_cu": dict(at=(0.0, 0.0, 5.5), r=1.5, az=HERO_AZ, el=75),
         "pot_cu": dict(at=(0.0, 0.0, 3.9), r=1.9, az=HERO_AZ, el=8)}
FX = {HERO: [("campfire", FIRE), ("heat_glow", GLOW)]}
VERIFY = dict(cls="asset", sockets={HERO: ["campfire", "heat_glow"]})
COMPARE = {"f34": {"box": (16, 84, 516, 428), "view": (HERO_AZ, 20)},
           "r34": {"box": (526, 84, 1010, 428), "view": (HERO_AZ + 180, 20)},
           "front": {"box": (16, 488, 258, 708), "view": (0, 12)},
           "side": {"box": (264, 488, 506, 708), "view": (90, 12)},
           "rear": {"box": (510, 488, 754, 708), "view": (180, 12)},
           "top": {"box": (760, 488, 1010, 710), "view": (0, 75)}}


def station_check(objs):
    """Spec "Brief": the pot clear of the logs (the fire's room), the chain hung from the crotch, nothing under z 0."""
    h = objs[HERO]
    off = Vector(h[MODEL.OFF])
    zs = [(v.co + off).z for v in h.data.vertices]
    geo = {k: v for k, v in P.GEO.items()}
    rep = {"zmin": round(min(zs), 4), "zmax": round(max(zs), 3), "geo": geo}
    pr = []
    if min(zs) < -1e-4:
        pr.append(f"{HERO}: geometry under the ground ({min(zs):.4f})")
    return rep, pr


def build(render=True, close=False, spin=False):
    return MODEL.run(hero=(HERO, hero_all), parts=PARTS, notes=NOTES, collision=COLLISION, budgets=BUDGETS,
                     target_size=TARGET_SIZE, fx=FX, views=VIEWS, exploded=EXPLODED, close=CLOSE if close else None,
                     verify=VERIFY, checks=[station_check], render=render, spin=spin)


def preview(names=("f34_sheet", "front_sheet", "top_sheet")):
    return MODEL.preview(HERO, VIEWS, names)


def compare(cells=None, out_dir=None):
    import importlib
    import compare as C
    importlib.reload(C)
    return C.compare(NUM, {k: COMPARE[k] for k in (cells or COMPARE)}, out_dir=out_dir)
