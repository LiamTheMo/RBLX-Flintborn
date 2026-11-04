"""073 Barricade (references/073.png, remade sheet; no earlier builder) on the shared library (kit_parts / kit_build):
one tileable module of a lashed timber barricade. See M073_spec.md.

    import importlib, kit_parts, kit_build, m073
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m073); m073.build()

Build frame (studs): front -Y, +X right, ground z 0, the module centred on x 0, the post axes on y 0.
- Four square posts (1.16, vertical edges chamfered 0.12, a shallow V-groove down the middle of each broad face) stand
  on four faceted footing stones (sunk 0.03 into the stone's flat top) up to 5.75, with a chamfered pyramid cap (cut
  wood, half way to the highlight swatch) from 5.33. End posts at x +-4.448, inner posts at +-1.483 (pitch 2.97).
- Top rail (z 3.48-4.52) and bottom rail (1.00-2.00), 0.80 deep, grooved front and back, on the post axes (the
  sheet's notched joint): one span per bay seated 0.03 into the post side faces. The bottom rail also has a stub from
  each end post out to the seam; the top rail stops in the end posts, whose turns wrap their outer faces.
- Rope lashings at the top rail (8-sided rope flattened against the post: turns 0.32 tall x 0.24 thick, diagonals
  0.30 wide x 0.20 thick): turns round each post (three on the end posts, two on the inner posts at 3.60 / 4.40), cut
  where a rail span enters the post: each run follows the side face to the rail's front or rear face and ends 0.04
  into it. On the inner posts an X on the front and on the rear face (both strokes over the turns, one passing 0.12
  under the other at the crossing); on the end posts one diagonal over the turns on each face. Diagonal ends stop at
  the post's front / rear corner over their turn with a short step round the chamfer (no run onto the rail), or, on
  an end post's outer side, go over the turn and tuck into the post face.
- Two rear braces (0.54 x 0.72): from the rear face of posts 2 and 3 (top end cut to that face, highest point 3.40)
  out toward the end posts, back and down to a level foot on the ground about 2.55 behind the wall.
Seam contract: the module tiles at PITCH = 32/3 studs (three modules fill two 16-stud tiles) along X. Only the bottom
rail stubs reach the seams (end faces at x +-5.3313, 0.002 inside; the same section at both ends); the end posts'
turns stop 0.003 inside them; nothing passes +-PITCH/2. Neighbouring modules' stubs meet face to face, leaving a 0.61
gap between end posts that the bottom rail bridges and the two posts' turns nearly close.
Parts: LashedBarricadePost, LashedBarricadeRail, LashedBarricadeBrace, LashedBarricadeLashing, LashedBarricadeStone.
Stages 5-6: nothing (the sheet shows no glow, light or effect).
"""
import math

from mathutils import Matrix, Vector

import kit_build as B
import kit_parts as P

NUM, TITLE = 73, "Barricade"
HERO = "LashedBarricade"
POST_P, RAIL_P, BRACE_P, LASH_P, STONE_P = (HERO + s for s in ("Post", "Rail", "Brace", "Lashing", "Stone"))

WOOD, WOOD_HI, ROPE, ROPE_DEEP, STONE = "m073_wood", "m073_wood_hi", "m073_rope", "m073_rope_deep", "m073_stone"

# key -> (hex, roughness, metal, emission, low specular). Stage 4: sheet swatches / rendered medians (spec), then
# MODEL.calibrate toward TARGETS.
PALETTE = {
    WOOD: ("#A56828", 0.85, 0.0, 0.0, True),     # R1 fix: the lit wood rendered 8 % dark at #995F25
    WOOD_HI: ("#C68744", 0.8, 0.0, 0.0, True),
    ROPE: ("#E5B079", 0.95, 0.0, 0.0, True),
    ROPE_DEEP: ("#B0925A", 0.95, 0.0, 0.0, True),
    STONE: ("#7B7D87", 0.9, 0.0, 0.0, True),
}
TARGETS = {WOOD: ((0xC0, 0x6D, 0x25), "brown"), WOOD_HI: ((0xF5, 0xA0, 0x48), "brown"),
           ROPE: ((0xFC, 0xD7, 0x87), "all"), ROPE_DEEP: ((0xE0, 0xB0, 0x60), "all"),
           STONE: ((0x98, 0x94, 0x9A), "stone")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)

Z = Vector((0.0, 0.0, 1.0))

# ---- layout (spec "Brief": 0.0476 stud/px from the side cell's 5-stud figure) -----------------------------------------
PITCH = 32.0 / 3.0
HALF = PITCH / 2
SEAM = HALF - 0.002             # the bottom rail stubs' end faces
PH, PCH = 0.58, 0.12            # post half width, vertical edge chamfer
POST_TOP, CAP_H, CAP_K = 5.75, 0.42, 0.56     # cap from POST_TOP - CAP_H; its flat top is the section x CAP_K
CAP_T = 0.5                     # the cap's key: wood -> wood_hi
GROOVE = (0.035, 0.03)          # V-groove half width, depth (posts, rails, braces)
SEAT = 0.03                     # rail ends into the posts, post feet into the stones, brace top into the post
# footing stones ((base half x, y), height, seed): flared rocks, base 1.74 x 1.90 (the front cell's 1.95 base is more
# than the end stones fit inside the seam: 4.448 + 0.87 = 5.318 < 5.323)
STONES = (((0.87, 0.95), 0.95, 11), ((0.87, 0.95), 0.88, 13), ((0.87, 0.95), 0.90, 17), ((0.87, 0.95), 0.96, 19))
STONE_TOP_K = 1.12              # the stone's flat top: the post section x this
# rings between base and top: (height range x H, size range x base): a near-upright lower body and a steep shoulder
# bevel up to the flat top (the sheet's bell-shaped footing rocks; one waist gave a straight frustum)
STONE_WAIST = (((0.28, 0.34), (0.94, 0.97)), ((0.56, 0.64), (0.85, 0.89)))
STONE_JIT = (0.96, 1.0)         # base ring jitter (shrinks only)
RAIL_HY, RAIL_CH = 0.40, 0.06
RAILS = {"top": (3.48, 4.52), "bot": (1.00, 2.00)}
# rope: 8-sided, flattened against the post (the joint detail's bands): (half height / in-face width, half thickness
# off the face) for the turns and the diagonals
RT_SIDES = 8
RT, RT_R = 0.16, 0.12           # turns: half height, radial half thickness
RD, RD_R = 0.15, 0.10           # diagonals: in-face half width, half thickness off the face
K8 = P.turn_ext(RT_SIDES)[0]                # an 8-sided section's flat-to-centre extent / radius (0.924)
RT_EXT = K8 * RT                            # a turn's half height to its flats (0.148)
TURN_OFF = K8 * RT_R - 0.02                 # turn centreline off the post faces (inner flat sunk 0.02): hugs the post
# the end posts at the R1 layout (their turns then stop 0.02 inside the seam; post spacing and stones unchanged)
END_X = SEAM - (PH + 0.14 + RT) - 0.003
POST_X = (-END_X, -END_X / 3, END_X / 3, END_X)
assert END_X + max(s[0][0] for s in STONES) < HALF - 0.01


def grooved(sec, faces, g=GROOVE):
    """A counter-clockwise section with a V-groove in the middle of each edge whose outward normal is in `faces`
    (unit (u, v) tuples)."""
    out = []
    n = len(sec)
    for i in range(n):
        p0, p1 = Vector(sec[i]), Vector(sec[(i + 1) % n])
        out.append(tuple(p0))
        e = p1 - p0
        if e.length < 4 * g[0]:
            continue
        t = e.normalized()
        nrm = Vector((t.y, -t.x))
        if not any((nrm - Vector(f)).length < 1e-3 for f in faces):
            continue
        m = (p0 + p1) / 2
        out += [tuple(m - t * g[0]), tuple(m - nrm * g[1]), tuple(m + t * g[0])]
    return out


AXES4 = ((1, 0), (0, 1), (-1, 0), (0, -1))


def loft(a, rings, key, cap_keys=(None, None), band_keys=None, **kw):
    """A closed shell through rings of equal length (planar end rings, any shape): side quads, ear-clipped caps."""
    n = len(rings[0])
    pts = [Vector(p) for r in rings for p in r]
    faces, keys = [], []
    for i in range(len(rings) - 1):
        for j in range(n):
            j1 = (j + 1) % n
            faces.append([i * n + j, i * n + j1, (i + 1) * n + j1, (i + 1) * n + j])
            keys.append(band_keys[i] if band_keys else None)
    for end, base in ((0, 0), (1, (len(rings) - 1) * n)):
        ring = [Vector(p) for p in rings[0 if end == 0 else -1]]
        nrm = P.newell(ring).normalized()
        e1 = nrm.orthogonal().normalized()
        e2 = nrm.cross(e1)
        tris = P.earclip([(p.dot(e1), p.dot(e2)) for p in ring])
        for t in tris:
            faces.append([base + i for i in t])
            keys.append(cap_keys[end])
    return P.shell(a, pts, faces, key, keys=keys, **kw)


# ---- posts and stones -------------------------------------------------------------------------------------------------
def post_sec():
    return grooved(P.sec_rect(PH, PH, PCH), AXES4)


def post(a, x, z0, name="post", top=POST_TOP):
    """A square chamfered post from a flat foot at z0 to a chamfered pyramid cap (the cap is cut wood: half way to
    the highlight swatch, the sheet's caps against its post faces under the same light)."""
    sec = post_sec()
    zs = top - CAP_H
    rings = [[(x + u, v, z0) for u, v in sec], [(x + u, v, zs) for u, v in sec],
             [(x + u * CAP_K, v * CAP_K, top) for u, v in sec]]
    cap = P.mix(WOOD, WOOD_HI, CAP_T)
    return loft(a, rings, WOOD, cap_keys=(None, cap), band_keys=[None, cap], name=name, kind="post")


def stone_points(i):
    """A faceted footing rock: a jittered chamfered base ring on z 0, a near-upright lower body and a shoulder ring
    (STONE_WAIST: a convex bell, the sides flaring out to the base as the front cell's rocks) and a flat top ring (the
    post section x STONE_TOP_K). Jitter only shrinks, so the end stones stay inside the seams."""
    (hx, hy), h, sd = STONES[i]
    r = P.rng(f"stone{sd}")
    base = P.sec_rect(hx, hy, 0.26)
    waist = P.sec_rect(hx, hy, 0.24)
    topr = P.sec_rect(PH * STONE_TOP_K, PH * STONE_TOP_K, PCH * 1.6)
    pts = []
    for (u, v) in base:
        k = r.uniform(*STONE_JIT)
        pts.append(Vector((u * k, v * k, 0.0)))
    for (wz0, wz1), (wk0, wk1) in STONE_WAIST:
        for (u, v) in waist:
            k = r.uniform(wk0, wk1)
            pts.append(Vector((u * k, v * k, h * r.uniform(wz0, wz1))))
    for (u, v) in topr:
        pts.append(Vector((u, v, h)))
    return pts


def stone(a, i, x=None, name=None):
    x = POST_X[i] if x is None else x
    pts = [p + Vector((x, 0.0, 0.0)) for p in stone_points(i)]
    p = P.hull(a, pts, STONE, name=name or f"stone{i}", kind="stone", amp=0.04)
    P.texture(a, p.vs, 0.05, STONES[i][2], scale=0.9)
    return p


# ---- rails ----------------------------------------------------------------------------------------------------------------
def rail_sec(level):
    z0, z1 = RAILS[level]
    hz = (z1 - z0) / 2
    return grooved(P.sec_rect(RAIL_HY, hz, RAIL_CH), ((1, 0), (-1, 0))), (z0 + z1) / 2


def rail(a, level, x0, x1, name):
    """A rail from x0 to x1 on the post axes; (u, v) = (y, z). The stub ends at the seams stay plain wood (they face
    the neighbour's stub; a pale end read as a plate on the end post in the side cell)."""
    sec, zc = rail_sec(level)
    rings = [[(x, u, zc + v) for u, v in sec] for x in (x0, x1)]
    P.GEO.setdefault("rails", {})[name] = [round(x0, 3), round(x1, 3)]
    return loft(a, rings, WOOD, name=name, kind="rail")


def rail_spans(level):
    """[(x0, x1)]: one span per bay, seated SEAT into the post faces; the bottom rail also has a stub from each
    end post out to the seam (the tile's continuous bottom rail). The top rail stops in the end posts, whose turns
    wrap their outer faces (front, side and f34 cells)."""
    out = [] if level == "top" else [(-SEAM, POST_X[0] - PH + SEAT)]
    for i in range(3):
        out.append((POST_X[i] + PH - SEAT, POST_X[i + 1] - PH + SEAT))
    if level != "top":
        out.append((POST_X[3] + PH - SEAT, SEAM))
    return out


def rails(a):
    for level in RAILS:
        for k, (x0, x1) in enumerate(rail_spans(level)):
            rail(a, level, x0, x1, f"rail_{level}{k}")


# ---- rope -----------------------------------------------------------------------------------------------------------------
TURNS = {"end": (3.68, 4.00, 4.32), "mid": (3.60, 4.40)}    # mid: the X rises 0.80 over 1.20 (lowest underside 3.45)
END_SINK = 0.04                             # a run's end: this deep into the rail face it meets


def rail_sides(xc):
    """The sides (-1 / +1 along X) of the post at xc that a top-rail span enters."""
    out = []
    for x0, x1 in rail_spans("top"):
        if abs(x1 - (xc - PH + SEAT)) < 1e-6:
            out.append(-1)
        if abs(x0 - (xc + PH - SEAT)) < 1e-6:
            out.append(1)
    return out


def band(a, path, ru, rv, closed=False, name=None, kind="rope"):
    """P.rope (twist off, RT_SIDES rings aligned, one strand in ROPE_DEEP) with a flattened section: half `ru` along
    the up axis (Z projected off the path: a turn's height, a diagonal's width on the face) and half `rv` across it
    (a turn's or diagonal's thickness off the post). Bends are mitred as P.tube's; open ends get flat caps and are
    registered for the both-ends contact check."""
    pts_, n, sides = [Vector(p) for p in path], len(path), RT_SIDES
    rings = []
    for i in range(n):
        prev = pts_[i - 1] if closed else pts_[max(i - 1, 0)]
        nxt = pts_[(i + 1) % n] if closed else pts_[min(i + 1, n - 1)]
        tin = (pts_[i] - prev) if (pts_[i] - prev).length > 1e-9 else (nxt - pts_[i])
        tout = (nxt - pts_[i]) if (nxt - pts_[i]).length > 1e-9 else tin
        tin, tout = tin.normalized(), tout.normalized()
        T = (tin + tout).normalized()
        U = (Z - Z.dot(T) * T).normalized()
        V = T.cross(U)
        B = tout - tin
        bend = B.length > 1e-6
        if bend:
            B.normalize()
        sc = 1.0 / max(0.5, tin.dot(T)) - 1.0
        ring = []
        for k in range(sides):
            ang = math.pi / sides + 2 * math.pi * k / sides
            off = U * math.cos(ang) * ru + V * math.sin(ang) * rv
            if bend:
                off += B * off.dot(B) * sc
            ring.append(pts_[i] + off)
        rings.append(ring)
    pts = [p for rg in rings for p in rg]
    faces, strand = [], []
    for i in range(n if closed else n - 1):
        j = (i + 1) % n
        for k in range(sides):
            a0, a1 = i * sides + k, i * sides + (k + 1) % sides
            b0, b1 = j * sides + k, j * sides + (k + 1) % sides
            faces += [[a0, a1, b1], [a0, b1, b0]]
            strand += [(k - i) % sides] * 2
    if not closed:
        faces.append(list(reversed(range(sides))))
        faces.append([(n - 1) * sides + k for k in range(sides)])
        strand += [-1, -1]
    keys = [ROPE_DEEP if s == 0 else None for s in strand]
    p = P.shell(a, pts, faces, ROPE, keys=keys, recalc=False, name=name, kind=kind, amp=0.03)
    if not closed and name:
        P.ROPES.append({"name": p.name, "ends": [list(P.XF[-1] @ pts_[0]), list(P.XF[-1] @ pts_[-1])], "rt": max(ru, rv)})
    return p


def turn_loop(xc, z):
    sec = [Vector((xc + u, v, z)) for u, v in P.sec_rect(PH, PH, PCH)]
    return P.hull_loop(sec, (xc, 0.0, z), Z, Vector((1, 0, 0)), TURN_OFF, 8)


def turn_runs(xc, z, alone=False):
    """A turn round the post at height z: the mitred offset loop round its octagon, cut on each side face a top-rail
    span enters: the run follows the side face to the rail's front or rear face and ends END_SINK into it (so the
    turn wraps the joint without passing through the rail). alone: the closed loop."""
    loop = turn_loop(xc, z)
    if alone:
        return [(loop, True)]
    sides = rail_sides(xc)
    xo, ye = PH + TURN_OFF, RAIL_HY - END_SINK
    on = lambda p, s: abs(p.x - xc - s * xo) < 1e-4          # noqa: E731
    pts, brk = [], []
    n = len(loop)
    for i in range(n):
        p, q = loop[i], loop[(i + 1) % n]
        pts.append(p)
        for s in sides:
            if on(p, s) and on(q, s):
                c0, c1 = sorted((-ye, ye), key=lambda y: (y - p.y) * (q.y - p.y))
                pts += [Vector((p.x, c0, z)), Vector((p.x, c1, z))]
                brk.append(len(pts) - 2)               # the edge from c0 to c1 crosses the rail
    if not brk:
        return [(loop, True)]
    out = []
    m = len(pts)
    for k, b in enumerate(brk):
        nb = brk[(k + 1) % len(brk)]
        run, i = [], (b + 1) % m
        while True:
            run.append(pts[i])
            if i == nb:
                break
            i = (i + 1) % m
        out.append((run, False))
    return out


def turns(a, xc, zs, tag, alone=False):
    out = []
    for ti, z in enumerate(zs):
        for ri, (path, closed) in enumerate(turn_runs(xc, z, alone)):
            out.append(band(a, path, RT, RT_R, closed=closed, name=f"{tag}turn{ti}_{ri}", kind="rope_turn"))
    return out


ARC_R = K8 * (RT_R + RD_R) - 0.05           # a diagonal's centreline off a turn's, across the face (0.05 into it)
ARC_V = K8 * (RT + RD) - 0.05               # ... and over its top or bottom
O2 = TURN_OFF + ARC_R                       # a diagonal's offset off the post faces where it lies over a turn
TUCK = 0.03                                 # a diagonal's end tucked into a post face this deep
DIVE = 0.12                                 # along the face from the corner to a diagonal's -45 deg point


def _corner(s, f, off):
    """The offset octagon's two corner points (side face first, then front / rear face) at the post corner (s along
    X, f along Y), `off` outside the faces, relative to the post axis."""
    k = PH - PCH + off * math.tan(math.pi / 8)
    return Vector((s * (PH + off), f * k, 0.0)), Vector((s * k, f * (PH + off), 0.0))


TUCK_X = PH - 0.18                          # where an end that can't wrap the corner goes over its turn
ARM_WRAP = 0.12                             # a corner end's last step round the chamfer (its cut end turns away)
ARM_DIP = 0.01                              # ... and that far closer to the turn (into it)


def arm_end(xc, s, f, z, up):
    """A diagonal's end at the post corner (s, f) over the turn at height z (up +1 the top turn, -1 the bottom), from
    its end inward. Where a top-rail span enters side s: at the post's front / rear corner (x +-0.60 from the axis,
    over the turn), then a short step round the chamfer dipping into the turn, so the X stays on the post face (no run
    onto the rail). Else (an end post's outer side, whose turns already reach the seam): over the turn (90 and 45 deg)
    at TUCK_X and tucked into the post face beyond it."""
    if s in rail_sides(xc):
        c1, c2 = _corner(s, f, O2)
        d = Vector((s, -f, 0.0)).normalized()
        n = Vector((s, f, 0.0)).normalized()
        pts = ([c2 + d * ARM_WRAP - n * ARM_DIP, c2] if ARM_WRAP else [c2 - n * ARM_DIP])
        return [Vector((xc + p.x, p.y, z)) for p in pts]
    r = math.radians(45)
    x = xc + s * TUCK_X
    return [Vector((x, f * (PH - TUCK), z + up * ARC_V)), Vector((x, f * (PH + TURN_OFF), z + up * ARC_V)),
            Vector((x, f * (PH + TURN_OFF + ARC_R * math.cos(r)), z + up * ARC_V * math.sin(r))),
            Vector((x, f * (PH + O2), z))]


def diagonal(a, xc, face, sg, zs, mid_off, name, over=False):
    """One diagonal on the post's front (face -1) or rear (+1) face, from the top turn at the corner on side -sg to
    the bottom turn at the corner on side +sg. Each end wraps the post corner over its turn (O2 off the faces) and
    ends in the rail face beside the post (or tucks into the post's side face); between the turns it dives at -45 deg
    round the turn to `mid_off` off the face at the crossing (over=True: it stays over a middle turn, O2 off)."""
    f = face
    top, bot = zs[-1], zs[0]
    path = arm_end(xc, -sg, f, top, 1)
    mid = Vector((xc, f * (PH + mid_off), (top + bot) / 2))
    lo = list(reversed(arm_end(xc, sg, f, bot, -1)))
    if not over:
        r = math.radians(45)
        kx = PH - PCH + O2 * math.tan(math.pi / 8) - DIVE
        path.append(Vector((xc - sg * kx, f * (PH + TURN_OFF + ARC_R * math.cos(r)), top - ARC_V * math.sin(r))))
        path.append(mid)
        lo.insert(0, Vector((xc + sg * kx, f * (PH + TURN_OFF + ARC_R * math.cos(r)), bot + ARC_V * math.sin(r))))
    else:
        path.append(mid)
    path += lo
    return band(a, path, RD, RD_R, name=name, kind="rope_diag")


X_MID = (O2 - 0.12, O2)         # inner posts: the first diagonal passes under the second at the crossing
X_DIVE = False                  # True: the first also dives round the turns at -45 deg (read as a Z in the front cell)
END_MID = O2                                                 # end posts: the diagonal over the middle turn


def lashing(a, i, tag=None):
    """The top-rail lashing of post i: turns, then the X (inner posts) or one diagonal (end posts) on both faces."""
    xc = POST_X[i]
    end = i in (0, 3)
    zs = TURNS["end" if end else "mid"]
    tag = tag if tag is not None else f"p{i}_"
    turns(a, xc, zs, tag)
    for fi, face in enumerate(((0, -1), (0, 1))):
        if end:
            diagonal(a, xc, face[1], -1 if fi == 0 else 1, zs, END_MID, f"{tag}diag{fi}", over=True)
        else:
            for k, sg in enumerate((1, -1)):
                diagonal(a, xc, face[1], sg, zs, X_MID[k], f"{tag}x{fi}{k}", over=k == 1 or not X_DIVE)


# ---- braces ---------------------------------------------------------------------------------------------------------------
BRACE_W, BRACE_CH = (0.54, 0.72), 0.05     # across (horizontal) x deep; edge chamfer
BRACE_FOOT = (2.25, 2.55)       # foot centre: out from the post axis toward the end post, behind the wall (y)
BRACE_TOPZ = 3.40               # the top end's highest point (the lowest turn's underside is 3.45)
BRACE_AXIS_Y = 0.25             # the axis point the brace is aimed from (inside the post)
BRACE_SEAT = 0.012              # the top end this far inside the post's faces (the post's chamfer edge, which the
                                # end's fan cap spans, then sits under 0.05 inside the brace)


def _octagon_planes(xc, inset):
    """(outward normal, offset) of the post's plan octagon moved `inset` inward: n . p <= c inside."""
    sec = [Vector((xc + u, v)) for u, v in P.sec_rect(PH, PH, PCH)]
    out = []
    for i in range(len(sec)):
        e = sec[(i + 1) % len(sec)] - sec[i]
        n = Vector((e.y, -e.x)).normalized()
        out.append((n, n.dot(sec[i]) - inset))
    return out


def _exit(o, x, planes):
    """Where the line o + x t leaves the (vertical) octagon prism going along x: (point, t_in < t_out)."""
    o2, x2 = o.to_2d(), x.to_2d()
    t_out, t_in = 1e9, -1e9
    for n, c in planes:
        d = n.dot(x2)
        if abs(d) < 1e-12:
            continue
        t = (c - n.dot(o2)) / d
        if d > 0:
            t_out = min(t_out, t)
        else:
            t_in = max(t_in, t)
    return o + x * t_out, t_in < t_out


def _brace_rings(xc, T, F):
    """Brace corner lines from the axis point T toward the foot F: the top ring where each leaves the post's
    surface SEAT inside (the rear face or a chamfer), the foot ring on z 0; and the top end's centre."""
    planes = _octagon_planes(xc, BRACE_SEAT)
    x, u, v, L = P._axes(T, F, Z)
    sec = grooved(P.sec_rect(BRACE_W[0] / 2, BRACE_W[1] / 2, BRACE_CH), ((1, 0), (-1, 0)))
    top, foot, hit = [], [], True
    for su, sv in sec:
        o = T + u * su + v * sv
        p, ok = _exit(o, x, planes)
        top.append(p)
        hit = hit and ok
        foot.append(o + x * ((0.0 - o.z) / x.z))
    centre, _ = _exit(T, x, planes)
    return top, foot, centre, hit


def brace_rings(sx):
    """The rear brace of post 2 (sx -1, toward -X) or post 3 (sx +1): its top end cut to the post's surface (BRACE_SEAT
    in), its foot cut level on z 0; the aim point solved so the top end's highest point is BRACE_TOPZ and its
    footprint is centred on the post's rear face (so it lies on that face alone: a planar end)."""
    xc = POST_X[1] if sx < 0 else POST_X[2]
    F = Vector((xc + sx * BRACE_FOOT[0], BRACE_FOOT[1], 0.0))
    zt, xt = 2.6, xc
    for _ in range(60):
        top, foot, c, hit = _brace_rings(xc, Vector((xt, BRACE_AXIS_Y, zt)), F)
        zt += BRACE_TOPZ - max(p.z for p in top)
        xt += xc - (min(p.x for p in top) + max(p.x for p in top)) / 2
    top, foot, c, hit = _brace_rings(xc, Vector((xt, BRACE_AXIS_Y, zt)), F)
    P.GEO.setdefault("brace", {})[f"{sx:+d}"] = {
        "all_lines_hit_post": hit,
        "on_rear_face": all(abs(p.y - (PH - BRACE_SEAT)) < 1e-4 for p in top),
        "top_z": [round(min(p.z for p in top), 3), round(max(p.z for p in top), 3)],
        "top_dx": [round(min(p.x for p in top) - xc, 3), round(max(p.x for p in top) - xc, 3)],
        "top_y": [round(min(p.y for p in top), 3), round(max(p.y for p in top), 3)],
        "foot_x": [round(min(p.x for p in foot), 3), round(max(p.x for p in foot), 3)],
        "foot_y": [round(min(p.y for p in foot), 3), round(max(p.y for p in foot), 3)],
        "deg": round(math.degrees(math.atan2(c.z, (F - c).to_2d().length)), 1)}
    return top, foot, c


def brace(a, sx, name=None):
    """The brace shell: side quads, an ear-clipped foot and a fan top end (its two facets follow the post's rear face
    and chamfer)."""
    top, foot, c = brace_rings(sx)
    n = len(top)
    pts = top + foot + [c]
    faces = [[j, (j + 1) % n, n + (j + 1) % n, n + j] for j in range(n)]
    faces += [[2 * n, (j + 1) % n, j] for j in range(n)]
    nrm = P.newell(foot).normalized()
    e1 = nrm.orthogonal().normalized()
    e2 = nrm.cross(e1)
    faces += [[n + i for i in t] for t in P.earclip([(p.dot(e1), p.dot(e2)) for p in foot])]
    return P.shell(a, pts, faces, WOOD, name=name or f"brace{sx:+d}", kind="brace")


# ---- assemblies -----------------------------------------------------------------------------------------------------------
def hero_all(a):
    for i, x in enumerate(POST_X):
        stone(a, i)
        post(a, x, STONES[i][1] - SEAT, f"post{i}")
    rails(a)
    for i in range(4):
        lashing(a, i)
    for sx in (-1, 1):
        brace(a, sx)


def post_part(a):
    """One post (the end post's length) with its cap, foot on z 0."""
    post(a, 0.0, 0.0, "post", top=POST_TOP - (STONES[0][1] - SEAT))


def rail_part(a):
    """A full module rail, seam to seam (the exploded view's one-piece rail)."""
    rail(a, "top", -SEAM, SEAM, "rail")


def brace_part(a):
    brace(a, -1, "brace")


def lash_part(a):
    """The exploded 'Rope Lashing': three touching closed turns (the hero's flattened turns) round a post-sized
    opening."""
    for t in range(3):
        z = RT_EXT + t * (2 * RT_EXT - 0.02)
        band(a, turn_loop(0.0, z), RT, RT_R, closed=True, name=f"turn{t}", kind="rope_turn")


def stone_part(a):
    stone(a, 3, 0.0, "stone")


PARTS = ((POST_P, post_part), (RAIL_P, rail_part), (BRACE_P, brace_part), (LASH_P, lash_part), (STONE_P, stone_part))
NOTES = {
    HERO: "Lashed timber barricade module (sheet 073): four chamfered square posts (1.16, tops 5.75, pyramid caps) on "
          "faceted footing stones, a top and a bottom rail on the post axes (bottom-rail stubs to the seams), rope "
          "lashings at the top rail (turns and X diagonals), two rear braces from the inner posts to the ground behind. "
          "Tiles along X at a 32/3-stud pitch (three modules per two 16-stud tiles); seams at x +-5.333, only the "
          "bottom-rail stubs reach them.",
    POST_P: "Post: 1.16 square chamfered post with a V-groove per face and a lighter chamfered pyramid cap, 4.83 tall",
    RAIL_P: "Rail: one module-length rail (10.66 x 0.80 x 1.04), grooved front and back",
    BRACE_P: "Diagonal brace (rear support): 0.54 x 0.72, top end cut for a post's rear face, foot cut level",
    LASH_P: "Rope lashing: three touching flattened rope turns hugging a post-sized opening",
    STONE_P: "Footing stone: a flared faceted rock with a flat top for a post foot (1.74 x 1.89 x 0.96)",
}
COLLISION = {HERO: "box", POST_P: "box", RAIL_P: "box", BRACE_P: "box", LASH_P: "none", STONE_P: "hull"}
BUDGETS = {HERO: 6000}
TARGET_SIZE = ((2 * SEAM, 0.01), (4.1, 0.3), (POST_TOP, 0.01))
POINTS = {HERO: {"attach_w": ((-HALF, 0.0, 0.0), (-1.0, 0.0, 0.0)), "attach_e": ((HALF, 0.0, 0.0), (1.0, 0.0, 0.0))}}
VIEWS = {"f34_sheet": (-30, 14), "r34_sheet": (150, 14), "front_sheet": (0, 0), "side_sheet": (90, 0),
         "rear_sheet": (180, 0), "top_sheet": (0, 89.9)}
EXPLODED = {POST_P: (-7.5, 0.0, 0.0), STONE_P: (-10.0, -1.5, 0.0), RAIL_P: (0.0, 2.5, 4.0), BRACE_P: (2.0, -1.0, 0.0),
            LASH_P: (7.5, 0.0, 2.0)}
CLOSE = {"lash_cu": dict(at=(-1.51, -0.8, 4.0), r=1.5, az=-25, el=12),
         "end_cu": dict(at=(-4.8, -0.5, 4.0), r=1.8, az=-50, el=12),
         "brace_cu": dict(at=(-2.6, 1.4, 2.2), r=2.6, az=140, el=14)}
VERIFY = dict(cls="structure", seams={"pitch": (PITCH, 0.0, 0.0)},
              stored={HERO: ["attach_w", "attach_e", "m073_pitch", "m073_seams"]})
# compare cells: sheet pixel boxes (spec Brief) and cameras
COMPARE = {"f34": {"box": (12, 108, 508, 392), "view": VIEWS["f34_sheet"][:2]},
           "r34": {"box": (516, 108, 1012, 392), "view": VIEWS["r34_sheet"][:2]},
           "front": {"box": (14, 470, 296, 612), "view": (0, 0)},
           "side": {"box": (318, 470, 420, 612), "view": (90, 0)},
           "rear": {"box": (512, 470, 766, 612), "view": (180, 0)},
           "top": {"box": (772, 482, 1014, 600), "view": (0, 89.9)}}


def after(objs):
    h = objs[HERO]
    h["m073_pitch"] = PITCH
    h["m073_seams"] = [-HALF, HALF]
    # the Post part is the post alone: its cap (cut wood, CAP_T) is the only up-facing area, so the colour/normal
    # correlation reads it as painted light
    objs[POST_P]["kit_shading_ok"] = "the pyramid cap is cut end grain, half way to the wood-highlight swatch"


def build(render=True, close=False, spin=False):
    return MODEL.run(hero=(HERO, hero_all), parts=PARTS, notes=NOTES, collision=COLLISION, budgets=BUDGETS,
                     target_size=TARGET_SIZE, points=POINTS, views=VIEWS, exploded=EXPLODED, close=CLOSE if close else None,
                     verify=VERIFY, render=render, after=after, spin=spin)


def preview(names=("f34_sheet", "front_sheet", "side_sheet")):
    return MODEL.preview(HERO, VIEWS, names)


def compare(cells=None, out_dir=None, height=360):
    import importlib
    import compare as C
    importlib.reload(C)
    return C.compare(NUM, {k: COMPARE[k] for k in (cells or COMPARE)}, out_dir=out_dir, height=height)


TILE_CELL = {"box": (300, 1100, 670, 1250), "view": (0, 0)}


def tile_compare(out_dir=None, height=300):
    """The tiling cell: the hero and a linked copy at +PITCH, against the sheet's cell."""
    import bpy
    h = bpy.data.objects[HERO]
    c = B.linked(h, MODEL.PFX + "tile", h.matrix_world @ Matrix.Translation((PITCH, 0, 0)))
    try:
        import importlib
        import compare as C
        importlib.reload(C)
        return C.compare(NUM, {"tile": TILE_CELL}, objs=[h, c], out_dir=out_dir, height=height)
    finally:
        B.remove([c])
