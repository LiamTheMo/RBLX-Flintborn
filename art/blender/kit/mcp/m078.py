"""078 Craft Rack (references/078.png, sheet "72 / 132"; no earlier builder) on the shared library (kit_parts /
kit_build): a camp crafting rack with its props. See M078_spec.md.

    import importlib, kit_parts, kit_build, m078
    importlib.reload(kit_parts); importlib.reload(kit_build); importlib.reload(m078); m078.build()

Build frame (studs): front -Y, +X right, ground z 0, the rack centred on x 0 / y 0 (the sack stands outside it on -X,
the folded mat hangs over the +X shelf end).
- Two A-frames (x +-2.44 at the top, the feet 0.30 further out): two square legs each (0.58, chamfer 0.05, horizontal
  sections) from feet at y +-1.33 to level tops at y +-0.38, z 6.00 (cut-wood tops); a cross-tie on the frame's outer
  face (z 4.42-5.20, y +-1.12) and a shelf rail on it lower down (z 0.80-1.09, y +-1.72); iron pegs on the legs and
  rails.
- Top beam (0.50 x 0.78, z 4.42-5.20) passing between each frame's legs (its top edges 0.03 into them) into the
  cross-ties, an end-cap block with a peg on each tie's outer face.
- Rope binding per frame: a flattened 8-sided turn round both legs just over the beam and one just under it (each
  0.02 into beam and tie), an X of two diagonals over the turns on the front leg's front face and on the back leg's
  back face (m073 band()); a red two-tailed cloth tie hanging from the lower turn inside each leg.
- Shelf: three planks (0.52 x 0.34, top 1.42) from x -3.40 to 3.40 between the legs, on the two rails; the support
  brace (0.48 x 0.59) under the middle plank on two feet.
- Cloth: a canvas sling over the beam (0.07 slab), both flaps hanging in a V to z 3.22 at the middle, broad flat folds
  (every other column pushed out), a bunched ridge over the beam.
- Props as the hero view draws them: the sack (3.10, red neck tie) on the ground off the -X end, the jug (orange, blue
  band and neck, handle to +X) and the bowl behind it on the shelf, the rolled mat (along X, brown strap) on the
  shelf's +X half, a folded mat over the +X shelf end with a strap.
Parts: CraftRackSidePost, CraftRackTopBeam, CraftRackBinding, CraftRackShelf, CraftRackBrace, CraftRackCloth,
CraftRackSack, CraftRackJug, CraftRackBowl, CraftRackMat. Stages 5-6: nothing (no glow, light or effect on the sheet).
"""
import math

from mathutils import Matrix, Vector

import kit_build as B
import kit_parts as P

NUM, TITLE = 78, "Craft Rack"
HERO = "CraftRack"
POST_P, BEAM_P, BIND_P, SHELF_P, BRACE_P, CLOTH_P, SACK_P, JUG_P, BOWL_P, MAT_P = (
    HERO + s for s in ("SidePost", "TopBeam", "Binding", "Shelf", "Brace", "Cloth", "Sack", "Jug", "Bowl", "Mat"))

WOOD, WOOD_HI, ROPE, ROPE_DEEP, RED = "m078_wood", "m078_wood_hi", "m078_rope", "m078_rope_deep", "m078_red"
CLOTH, SACK, JUG, BLUE, BOWL = "m078_cloth", "m078_sack", "m078_jug", "m078_blue", "m078_bowl"
MAT, MAT_DEEP, STRAP, IRON, DARK = "m078_mat", "m078_mat_deep", "m078_strap", "m078_iron", "m078_dark"

# key -> (hex, roughness, metal, emission, low specular). Stage 4: sheet swatches / rendered medians (spec), then
# MODEL.calibrate toward TARGETS; the cloth and sack creams set by hand against the hero render (the dome pulls cream
# toward salmon).
PALETTE = {
    WOOD: ("#9A632B", 0.85, 0.0, 0.0, True),
    WOOD_HI: ("#BB7F3E", 0.8, 0.0, 0.0, True),
    ROPE: ("#CC9C42", 0.95, 0.0, 0.0, True),
    ROPE_DEEP: ("#A8752E", 0.95, 0.0, 0.0, True),
    RED: ("#BE3A2C", 0.9, 0.0, 0.0, True),
    CLOTH: ("#C8B190", 0.95, 0.0, 0.0, True),
    SACK: ("#BDA284", 0.95, 0.0, 0.0, True),
    JUG: ("#BE7F48", 0.55, 0.0, 0.0, False),
    BLUE: ("#405880", 0.55, 0.0, 0.0, False),
    BOWL: ("#BF9566", 0.6, 0.0, 0.0, False),
    MAT: ("#696932", 0.95, 0.0, 0.0, True),
    MAT_DEEP: ("#48481F", 0.95, 0.0, 0.0, True),
    STRAP: ("#684E28", 0.9, 0.0, 0.0, True),
    IRON: ("#676A74", 0.5, 0.4, 0.0, False),
    DARK: ("#3A2416", 0.95, 0.0, 0.0, True),
}
TARGETS = {WOOD: ((0xBC, 0x6E, 0x2A), "brown"), WOOD_HI: ((0xEC, 0x96, 0x40), "brown"),
           ROPE: ((0xF0, 0xB8, 0x55), "all"), ROPE_DEEP: ((0xC8, 0x8A, 0x3A), "all"), RED: ((0xD9, 0x37, 0x27), "all"),
           JUG: ((0xF0, 0x99, 0x56), "all"), BLUE: ((0x54, 0x6B, 0x95), "all"), BOWL: ((0xEC, 0xB5, 0x76), "all"),
           MAT: ((0x7E, 0x7C, 0x33), "all"), STRAP: ((0x80, 0x58, 0x28), "all"), IRON: ((0x6E, 0x6C, 0x72), "all")}
MODEL = B.Model(NUM, TITLE, palette=PALETTE, targets=TARGETS)

Z = Vector((0.0, 0.0, 1.0))


def mix(k1, k2, t):
    return P.mix(k1, k2, t, step=0.05)


# ---- layout (spec "Brief": 0.0327 stud/px from the front cell, post tops 6.00) ----------------------------------------
TOP = 6.00                      # leg tops
XT, LEAN = 2.44, 0.30           # frame x at the top; the feet this much further out
YT, YF = 0.38, 1.33             # leg centre |y| at the top and at the feet
LH, LCH = 0.29, 0.05            # leg half width, chamfer
BEAM_Z = (4.42, 5.20)           # top beam, cross-ties
BH = 0.25                       # beam half width (its top edges sit 0.03 into the legs)
TIE_X = (2.79, 3.05)            # cross-tie |x| (inner face on the legs' outer faces), |y| <= TIE_Y
TIE_Y = 1.12
CAPB = dict(x=(3.03, 3.29), y=0.30, z=(4.47, 5.15))       # beam end-cap block on the tie
BEAM_X = 2.82                   # beam ends 0.03 into the ties
SHELF_Z = (1.08, 1.42)          # plank bottom / top
PLANK_W, PLANK_GAP, SHELF_X = 0.52, 0.04, 3.40
RAIL_Z, RAIL_Y, RAIL_T = (0.80, 1.09), 1.72, 0.40          # shelf rails on the frames' outer faces
BRACE_Z, BRACE_HW, BRACE_X = (0.50, 1.09), 0.24, 2.30      # support brace under the middle plank
FOOT_X, FOOT_HX, FOOT_HY = 2.00, 0.17, 0.30                # its feet


def xc(z):
    """Leg centre |x| at height z (the frames lean in toward the top)."""
    return XT + LEAN * (TOP - z) / TOP


def yc(z):
    """Leg centre |y| at height z."""
    return YT + (YF - YT) * (TOP - z) / TOP


def cut():
    return mix(WOOD, WOOD_HI, 0.5)


# ---- timber -------------------------------------------------------------------------------------------------------------
def leg(a, s, f, name):
    """A square leg of frame s (x sign), f (y sign: -1 front, +1 back): horizontal sections, a flat foot on z 0 and a
    level cut-wood top."""
    return P.leg(a, (s * xc(0.0), f * yc(0.0)), (s * xc(TOP), f * yc(TOP)), TOP, LH, LH, WOOD, ch=LCH,
                 cap_keys=(None, cut()), name=name, kind="leg")


def face_normal(f):
    """The outward normal of a leg's front (f -1) or back (f +1) face (the face y = f (yc(z) + LH) is tilted)."""
    k = (YF - YT) / TOP                         # |y| grows this much per stud down
    return Vector((0.0, f, k)).normalized()


def leg_axis(s, f):
    return (Vector((s * xc(TOP), f * yc(TOP), TOP)) - Vector((s * xc(0.0), f * yc(0.0), 0.0))).normalized()


def face_pt(s, f, z, u, off):
    """A point on (or `off` horizontally off) the outward y face of leg (s, f) at height z, `u` along x from the leg
    centre."""
    return Vector((s * xc(z) + u, f * (yc(z) + LH + off), z))


def rail(a, s, name="rail"):
    """The shelf rail along Y on the frame's outer face (its inner face 0.01 into the legs at mid height)."""
    zc = sum(RAIL_Z) / 2
    x0 = xc(zc) + LH - 0.01
    x = s * (x0 + RAIL_T / 2)
    return P.plank(a, (x, -RAIL_Y, zc), (x, RAIL_Y, zc), RAIL_T, RAIL_Z[1] - RAIL_Z[0], WOOD, ch=0.05,
                   cap_keys=(cut(), cut()), name=name, kind="rail")


def tie(a, s, name="tie"):
    zc = sum(BEAM_Z) / 2
    x = s * sum(TIE_X) / 2
    return P.plank(a, (x, -TIE_Y, zc), (x, TIE_Y, zc), TIE_X[1] - TIE_X[0], BEAM_Z[1] - BEAM_Z[0], WOOD, ch=0.05,
                   cap_keys=(cut(), cut()), name=name, kind="tie")


def bolt(a, c, n, up, name):
    return P.bolt(a, c, n, up, IRON, h=0.10, proud=0.05, dome=0.025, sink=0.03, name=name)


def aframe(a, s, tag=""):
    """One A-frame: two legs, the cross-tie, the shelf rail, pegs on the legs' outer faces and on the rail."""
    for f in (-1, 1):
        leg(a, s, f, f"{tag}leg{'fb'[f > 0]}")
    tie(a, s, f"{tag}tie")
    rail(a, s, f"{tag}rail")
    zb = sum(RAIL_Z) / 2
    for f in (-1, 1):
        bolt(a, face_pt(s, f, zb, 0.0, 0.0), face_normal(f), leg_axis(s, f), f"{tag}peg_leg{'fb'[f > 0]}")
        xo = s * (xc(zb) + LH - 0.01 + RAIL_T)
        bolt(a, (xo, f * yc(zb), zb), (s, 0, 0), Z, f"{tag}peg_rail{'fb'[f > 0]}")


def beam(a, x0=-BEAM_X, x1=BEAM_X, name="beam"):
    zc = sum(BEAM_Z) / 2
    return P.plank(a, (x0, 0.0, zc), (x1, 0.0, zc), 2 * BH, BEAM_Z[1] - BEAM_Z[0], WOOD, ch=0.05,
                   cap_keys=(cut(), cut()), name=name, kind="beam")


def end_cap(a, s, x_in=None, name="cap"):
    """The beam's end-cap block on the cross-tie's outer face, a peg in its outer face."""
    x0, x1 = CAPB["x"]
    if x_in is not None:
        x0, x1 = x_in, x_in + (x1 - x0)
    zc = sum(CAPB["z"]) / 2
    hz = (CAPB["z"][1] - CAPB["z"][0]) / 2
    lo, hi = (min(s * x0, s * x1), -CAPB["y"], zc - hz), (max(s * x0, s * x1), CAPB["y"], zc + hz)
    out = P.box(a, lo, hi, WOOD, name=name, kind="cap")
    P.paint(a, out.fs[1:2] if s > 0 else out.fs[3:4], cut())        # the outer end face: cut wood
    bolt(a, (s * x1, 0.0, zc), (s, 0, 0), Z, name + "_peg")
    return out


def top_beam(a):
    beam(a)
    for s in (-1, 1):
        end_cap(a, s, name=f"cap{s:+d}")


def shelf(a, tag=""):
    """Three planks between the legs, resting 0.01 into the rails (and the brace)."""
    zc = sum(SHELF_Z) / 2
    for k, yk in enumerate((-1, 0, 1)):
        y = yk * (PLANK_W + PLANK_GAP)
        p = P.plank(a, (-SHELF_X, y, zc), (SHELF_X, y, zc), PLANK_W, SHELF_Z[1] - SHELF_Z[0], WOOD,
                    ch=0.05, cap_keys=(cut(), cut()), name=f"{tag}plank{k}", kind="plank")
        P.texture(a, p.vs, 0.03, P.seed(f"{tag}plank{k}"), scale=0.5)


def brace(a):
    zc = sum(BRACE_Z) / 2
    P.plank(a, (-BRACE_X, 0.0, zc), (BRACE_X, 0.0, zc), 2 * BRACE_HW, BRACE_Z[1] - BRACE_Z[0], WOOD, ch=0.05,
            cap_keys=(cut(), cut()), name="brace", kind="brace")
    for s in (-1, 1):
        x = s * FOOT_X
        P.box(a, (x - FOOT_HX, -FOOT_HY, 0.0), (x + FOOT_HX, FOOT_HY, BRACE_Z[0] + 0.01), WOOD,
              name=f"foot{s:+d}", kind="foot")
        bolt(a, (x, -BRACE_HW, zc), (0, -1, 0), Z, f"peg{s:+d}")


# ---- rope (m073 band(): an 8-sided rope flattened against the timber) -------------------------------------------------
RT_SIDES = 8
K8 = P.turn_ext(RT_SIDES)[0]                # 0.924
RT, RT_R = 0.13, 0.10                       # turns: half height, radial half thickness
RD, RD_R = 0.11, 0.08                       # diagonals: in-face half width, half thickness off the face
RT_EXT = K8 * RT                            # a turn's half height to its flats
TURN_OFF = K8 * RT_R - 0.02                 # turn centreline off the faces (inner flat 0.02 in)
ARC_R = K8 * (RT_R + RD_R) - 0.05           # a diagonal's centreline off a turn's (0.05 into it)
O2 = TURN_OFF + ARC_R                       # a diagonal's offset off the face over a turn
Z_HI = BEAM_Z[1] + RT_EXT - 0.02            # the turns: 0.02 into the beam top / bottom (and the tie)
Z_LO = BEAM_Z[0] - RT_EXT + 0.02
XH = 0.22                                   # the X's ends: this far either side of the leg centre
X_UNDER = 0.12                              # the first stroke passes this far under the second at the crossing


def band(a, path, ru, rv, closed=False, name=None, kind="rope"):
    """m073 band(): P.rope (twist off, rings aligned, one strand in ROPE_DEEP) with a flattened section: half `ru`
    along the up axis and half `rv` across it. Open ends get flat caps and are registered for the both-ends check."""
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
        Bv = tout - tin
        bend = Bv.length > 1e-6
        if bend:
            Bv.normalize()
        sc = 1.0 / max(0.5, tin.dot(T)) - 1.0
        ring = []
        for k in range(sides):
            ang = math.pi / sides + 2 * math.pi * k / sides
            off = U * math.cos(ang) * ru + V * math.sin(ang) * rv
            if bend:
                off += Bv * off.dot(Bv) * sc
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
        P.ROPES.append({"name": p.name, "ends": [list(P.XF[-1] @ pts_[0]), list(P.XF[-1] @ pts_[-1])],
                        "rt": max(ru, rv)})
    return p


def legs_section(s, z):
    """Both legs' chamfered sections of frame s at height z (3D points)."""
    return [Vector((s * xc(z) + u, f * yc(z) + v, z)) for f in (-1, 1) for u, v in P.sec_rect(LH, LH, LCH)]


def turn_loop(s, z):
    return P.hull_loop(legs_section(s, z), (s * xc(z), 0.0, z), Z, Vector((1, 0, 0)), TURN_OFF, 12)


TIE = dict(z_bot=2.70, notch=2.92, top=(0.02, 0.17), bot=(0.02, 0.31), t=0.045, tuck=0.04)


def red_tie(a, s, f, name):
    """A red two-tailed cloth tie hanging straight down beside the inner face of leg (s, f), broad side to the front:
    its top tucked `tuck` up into the lower turn's inner run (0.02-0.17 in from the leg face, inside the rope), widening
    to 0.29 at the tails; the leg leans away below, so it hangs free of it."""
    c = TIE
    zt = Z_LO - RT_EXT + c["tuck"]
    xin = xc(zt) - LH                            # |x| of the leg's inner face at the top
    zb = c["z_bot"]
    (d0, d1), (e0, e1) = c["top"], c["bot"]
    poly = [(d0, zt), (d1, zt), (e1, zb + 0.06), ((e1 * 2 + e0) / 3, zb), ((e0 + e1) / 2, c["notch"]),
            ((e1 + e0 * 2) / 3, zb), (e0, zb + 0.06)]
    y0 = f * yc(zt)
    p = P.ext(a, [(s * (xin - d), z) for d, z in poly], y0 - c["t"] / 2, y0 + c["t"] / 2, RED,
              to3=lambda u, v, w_: Vector((u, w_, v)), name=name, kind="red_tie", amp=0.03)
    P.texture(a, p.vs, 0.03, P.seed(name), scale=0.6)
    return p


def binding(a, s, tag="", ties=True):
    """The rope binding at frame s: a turn round both legs just over and just under the beam, an X over the turns on
    the front leg's front face and the back leg's back face, and the red ties."""
    for k, z in enumerate((Z_LO, Z_HI)):
        band(a, turn_loop(s, z), RT, RT_R, closed=True, name=f"{tag}turn{k}", kind="rope_turn")
    zm = (Z_LO + Z_HI) / 2
    for f in (-1, 1):
        for k, sg in enumerate((1, -1)):
            path = [face_pt(s, f, Z_HI, -sg * XH, O2), face_pt(s, f, zm, 0.0, O2 - (X_UNDER if k == 0 else 0.0)),
                    face_pt(s, f, Z_LO, sg * XH, O2)]
            band(a, path, RD, RD_R, name=f"{tag}x{'fb'[f > 0]}{k}", kind="rope_diag")
    if ties:
        for f in (-1, 1):
            red_tie(a, s, f, f"{tag}red{'fb'[f > 0]}")


# ---- cloth ----------------------------------------------------------------------------------------------------------
BEAM_CH = 0.05                  # the beam's edge chamfer (P.plank ch)
CL = dict(xw=1.75, nu=7, z_tip=3.22, z_corner=4.45, z_side=5.10, gap=0.003, flare=0.30, fold=0.10, bump=(0.04, 0.14),
          ct=0.07, ts=(0.0, 0.36, 0.68, 1.0))


def cloth_inner():
    """The cloth's inner surface grid [i][j]: columns along x, rows from the back flap's hem over the beam to the front
    flap's hem."""
    c = CL
    g = c["gap"]
    grid = []
    for i in range(c["nu"]):
        x = -c["xw"] + 2 * c["xw"] * i / (c["nu"] - 1)
        zb = c["z_tip"] + (c["z_corner"] - c["z_tip"]) * abs(x) / c["xw"]
        fold = c["fold"] if i % 2 else 0.0

        def flap(sy, t):
            y = sy * (BH + g + c["flare"] * t ** 1.5 + fold * t)
            return Vector((x, y, c["z_side"] - t * (c["z_side"] - zb)))
        # over the beam: its side face, chamfer and top offset `gap` out (mitred corners), so no beam edge reaches the
        # cloth; the middle row bunched up
        k = g * math.tan(math.pi / 8)
        zt = BEAM_Z[1]
        over = [Vector((x, BH + g, zt - BEAM_CH + k)), Vector((x, BH - BEAM_CH + k, zt + g)),
                Vector((x, 0.0, zt + g + c["bump"][i % 2])), Vector((x, -(BH - BEAM_CH + k), zt + g)),
                Vector((x, -(BH + g), zt - BEAM_CH + k))]
        col = [flap(1, t) for t in reversed(c["ts"])] + over + [flap(-1, t) for t in c["ts"]]
        grid.append(col)
    return grid


def cloth(a, name="cloth"):
    """The canvas sling: one closed ct slab, the outer surface the inner one moved out along the vertex normals (away
    from the beam's axis), every quad split in two, rim faces round the open edges."""
    I = cloth_inner()
    nu, nv = len(I), len(I[0])
    axis_z = sum(BEAM_Z) / 2
    nrm = [[Vector() for _ in range(nv)] for _ in range(nu)]
    for i in range(nu - 1):
        for j in range(nv - 1):
            q = (I[i][j], I[i + 1][j], I[i + 1][j + 1], I[i][j + 1])
            n = (q[2] - q[0]).cross(q[3] - q[1])
            c = sum(q, Vector()) / 4
            if n.dot(Vector((0.0, c.y, c.z - axis_z))) < 0:
                n = -n
            for (ii, jj) in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)):
                nrm[ii][jj] += n
    O = [[I[i][j] + nrm[i][j].normalized() * CL["ct"] for j in range(nv)] for i in range(nu)]
    pts = [p for col in I for p in col] + [p for col in O for p in col]
    ii = lambda i, j: i * nv + j                    # noqa: E731
    oo = lambda i, j: nu * nv + i * nv + j          # noqa: E731
    faces = []
    for i in range(nu - 1):
        for j in range(nv - 1):
            for f in (ii, oo):
                a0, a1, a2, a3 = f(i, j), f(i + 1, j), f(i + 1, j + 1), f(i, j + 1)
                faces += [[a0, a1, a2], [a0, a2, a3]] if (i < (nu - 1) / 2) == (j < (nv - 1) / 2) else \
                    [[a0, a1, a3], [a1, a2, a3]]
    edges = [((i, 0), (i + 1, 0)) for i in range(nu - 1)] + [((i, nv - 1), (i + 1, nv - 1)) for i in range(nu - 1)]
    edges += [((0, j), (0, j + 1)) for j in range(nv - 1)] + [((nu - 1, j), (nu - 1, j + 1)) for j in range(nv - 1)]
    for (i0, j0), (i1, j1) in edges:
        faces += [[ii(i0, j0), ii(i1, j1), oo(i1, j1)], [ii(i0, j0), oo(i1, j1), oo(i0, j0)]]
    p = P.shell(a, pts, faces, CLOTH, name=name, kind="canvas", amp=0.02)
    P.texture(a, p.vs, 0.035, P.seed(name), scale=0.5)
    P.GEO["cloth"] = {"low": round(min(q.z for q in pts), 3), "x": [round(min(q.x for q in pts), 3),
                                                                     round(max(q.x for q in pts), 3)]}
    return p


# ---- props ----------------------------------------------------------------------------------------------------------
def lathe(a, c, prof, n, key, phase=0.0, keys=None, jit=0.0, seed_=1, tri=False, name=None, kind="prop", amp=0.03,
          top=None, scallop=None):
    """A closed solid of revolution about the vertical through c (x, y, z0): prof = [(z, r)] rings from the bottom
    (each an n-gon of corner radius r); keys[i] colours the band from ring i to i + 1; a flat bottom cap and, at the
    last ring, a flat cap or (top = (z, key)) a fan to a centre point. jit: seeded radial jitter (rings with r
    jitter-free when prof entries carry a third value False). tri: split the side quads in two. scallop = {ring: amp}:
    every other corner of that ring out by amp, the rest in (a gathered, ruffled rim)."""
    r_ = P.rng(name or "lathe" + str(seed_))
    cx, cy, cz = c
    rings = []
    for e in prof:
        z, r = e[0], e[1]
        jj = jit if (len(e) < 3 or e[2]) else 0.0
        ring = []
        for k in range(n):
            t = phase + 2 * math.pi * k / n
            rr = r * (1.0 + r_.uniform(-jj, jj))
            if scallop and len(rings) in scallop:
                rr *= 1.0 + scallop[len(rings)] * (1 if k % 2 else -1)
            ring.append(Vector((cx + math.cos(t) * rr, cy + math.sin(t) * rr, cz + z)))
        rings.append(ring)
    pts = [p for rg in rings for p in rg]
    faces, fk = [], []
    for i in range(len(rings) - 1):
        for k in range(n):
            q = [i * n + k, i * n + (k + 1) % n, (i + 1) * n + (k + 1) % n, (i + 1) * n + k]
            kk = keys[i] if keys and i < len(keys) else None
            if tri:
                faces += [[q[0], q[1], q[2]], [q[0], q[2], q[3]]] if k % 2 else [[q[0], q[1], q[3]], [q[1], q[2], q[3]]]
                fk += [kk, kk]
            else:
                faces.append(q)
                fk.append(kk)
    for cf in P._cap(n):
        faces.append(list(reversed(cf)))
        fk.append(None)
    last = (len(rings) - 1) * n
    if top is None:
        for cf in P._cap(n):
            faces.append([last + i for i in cf])
            fk.append(keys[len(rings) - 1] if keys and len(keys) >= len(rings) else None)
    else:
        pts.append(Vector((cx, cy, cz + top[0])))
        ap = len(pts) - 1
        for k in range(n):
            faces.append([last + k, last + (k + 1) % n, ap])
            fk.append(top[1])
    return P.shell(a, pts, faces, key, keys=fk, name=name, kind=kind, amp=amp)


SACK_C = (-4.15, 0.40)
SACK_LEAN = ((0.20, 1.70), -SHELF_X + 0.02)     # pressed 0.02 into the plank ends, 0.007 off the rail end
SACK_PROF = ((0.00, 0.80), (0.26, 0.98), (0.65, 1.02), (1.10, 1.00), (1.60, 0.92), (2.10, 0.76), (2.55, 0.52),
             (2.85, 0.37, False), (3.07, 0.38, False), (3.32, 0.64), (3.56, 0.54))
SACK_RUFFLE = {9: 0.16, 10: 0.22}                # the gathered top: every other corner in / out by this share
SACK_NECK = (3.00, 3.22)        # the red tie band


def sack(a, c=SACK_C, tag="", lean=True):
    """The cloth sack on the ground: a faceted 8-sided lathe (seeded jitter, flat bottom), a gathered ruffled top (a
    shallow dip to the middle), a red band round the neck (0.02 into it) and two short red tails down its front. lean:
    it slumps against the shelf end (SACK_LEAN: every vertex in that height band pressed flat to x <= that)."""
    n, ph = 8, math.pi / 8
    p = lathe(a, (c[0], c[1], 0.0), SACK_PROF, n, SACK, phase=ph, jit=0.04, tri=True, top=(3.60, mix(SACK, DARK, 0.15)),
              scallop=SACK_RUFFLE, name=f"{tag}sack", kind="sack", amp=0.03)
    if lean:
        (z0, z1), xm = SACK_LEAN
        for v in p.vs:
            if z0 <= v.co.z <= z1 and v.co.x > xm:
                v.co.x = xm
        for f in p.fs:
            f.normal_update()
    P.texture(a, p.vs, 0.04, P.seed(tag + "sack"), scale=0.7)
    rn = SACK_PROF[7][1] * math.cos(math.pi / n)            # the neck's flat radius
    ri, ro = rn - 0.02, rn + 0.07
    z0, z1 = SACK_NECK
    ring = lathe_ring(a, (c[0], c[1]), z0, z1, ri / math.cos(math.pi / n), ro / math.cos(math.pi / n), n, ph, RED,
                      name=f"{tag}sack_tie")
    for k, da in enumerate((-0.32, 0.18)):
        t = -math.pi / 2 + da                             # round the front (-Y)
        d = Vector((math.cos(t), math.sin(t), 0.0))
        e = Vector((-d.y, d.x, 0.0))
        top = Vector((c[0], c[1], z0 + 0.04)) + d * (ro - 0.03)
        bot = Vector((c[0], c[1], 2.42 - 0.10 * k)) + d * (0.70 + 0.01 * k)
        w, th = 0.07, 0.035
        pts = [top - e * w, top + e * w, bot + e * w * 1.2, bot - e * w * 1.2]
        nn = (bot - top).cross(e).normalized()
        if nn.dot(d) < 0:
            nn = -nn
        quad = pts + [q + nn * th for q in pts]
        P.box_pts(a, [quad[0], quad[1], quad[2], quad[3], quad[4], quad[5], quad[6], quad[7]], RED,
                  name=f"{tag}sack_tail{k}", kind="red_tie", amp=0.03)
    return p, ring


def lathe_ring(a, c, z0, z1, ri, ro, n, phase, key, name):
    """A closed band (annulus) round the vertical through c, corner radii ri / ro, z0 to z1."""
    cx, cy = c
    rings = []
    for z, r in ((z0, ro), (z1, ro), (z1, ri), (z0, ri)):
        rings.append([Vector((cx + math.cos(phase + 2 * math.pi * k / n) * r,
                              cy + math.sin(phase + 2 * math.pi * k / n) * r, z)) for k in range(n)])
    pts = [p for rg in rings for p in rg]
    faces = []
    for i in range(4):
        i1 = (i + 1) % 4
        for k in range(n):
            faces.append([i * n + k, i * n + (k + 1) % n, i1 * n + (k + 1) % n, i1 * n + k])
    return P.shell(a, pts, faces, key, name=name, kind="red_tie", amp=0.03)


JUG_C = (-1.10, -0.18)
JUG_PROF = ((0.00, 0.38), (0.10, 0.52), (0.28, 0.62), (0.44, 0.66), (0.60, 0.66), (0.78, 0.60), (0.98, 0.47),
            (1.12, 0.38), (1.34, 0.36), (1.46, 0.46), (1.60, 0.47), (1.60, 0.38), (1.38, 0.33))


def jug(a, c=JUG_C, z0=None, tag=""):
    """The ceramic jug on the shelf: a 10-sided lathe, orange with a blue band (z 0.44-0.60) and a blue neck and lip
    (from z 1.14), a dark mouth; a blue strap handle to +X from the neck to the shoulder, its ends square into the
    surface (0.03)."""
    z0 = SHELF_Z[1] - 0.01 if z0 is None else z0
    n = 10
    keys = [None, None, None, BLUE, None, None, None, BLUE, BLUE, BLUE, mix(BLUE, DARK, 0.5), DARK, DARK]
    # (bands: 0.44-0.60 the blue band at the widest; from 1.12 the blue neck and lip)
    p = lathe(a, (c[0], c[1], z0), JUG_PROF, n, JUG, phase=0.0, keys=keys, name=f"{tag}jug", kind="jug", amp=0.02)
    # handle: from the neck (r 0.32 at z 1.30) out and down to the shoulder (r 0.60 at z 0.74)
    hp = [(0.33, 1.28), (0.48, 1.31), (0.72, 1.24), (0.84, 1.04), (0.78, 0.86), (0.62, 0.79), (0.57, 0.78)]
    path = [Vector((c[0] + r, c[1], z0 + z)) for r, z in hp]
    P.tube(a, path, 0.075, 6, False, BLUE, up=(0, 1, 0), name=f"{tag}jug_handle", kind="jug", amp=0.02)
    return p


BOWL_C = (0.02, 0.32)
BOWL_PROF = ((0.00, 0.34), (0.10, 0.46), (0.30, 0.54), (0.44, 0.55), (0.66, 0.51), (0.80, 0.46), (0.86, 0.47),
             (0.86, 0.39), (0.30, 0.33))


def bowl(a, c=BOWL_C, z0=None, tag=""):
    """The deep ceramic bowl behind the jug: a 10-sided lathe, tan with a blue band (z 0.30-0.44) and a shaded inside."""
    z0 = SHELF_Z[1] - 0.01 if z0 is None else z0
    inner = mix(BOWL, DARK, 0.35)
    keys = [None, None, BLUE, None, None, mix(BOWL, WOOD_HI, 0.3), inner, inner, inner]
    return lathe(a, (c[0], c[1], z0), BOWL_PROF, 10, BOWL, phase=math.pi / 10, keys=keys, name=f"{tag}bowl",
                 kind="bowl", amp=0.02)


ROLL = dict(x=(0.62, 2.25), y=-0.05, r=0.75, strap_x=1.35, strap_w=0.28, sides=10, discs=(0.50, 0.24))


def roll(a, tag="", z_floor=None):
    """The rolled mat lying along X on the shelf: a 10-sided log, a dark green end on each side with two proud
    concentric discs (the rolled layers), a brown strap round the middle carrying it (its flat 0.01 into the shelf)."""
    zf = SHELF_Z[1] if z_floor is None else z_floor
    n, r = ROLL["sides"], ROLL["r"]
    ri = r / math.cos(math.pi / n) + 0.004
    ro = ri + 0.05
    zc = zf - 0.01 + ro * math.cos(math.pi / n)
    x0, x1, y = ROLL["x"][0], ROLL["x"][1], ROLL["y"]
    P.log(a, (x0, y, zc), (x1, y, zc), r, MAT, sides=n, end_key=MAT_DEEP, name=f"{tag}roll", kind="mat")
    for sx, xe in ((-1, x0), (1, x1)):
        for k, (rr, key) in enumerate(zip(ROLL["discs"], (MAT, MAT_DEEP))):
            xa = xe - sx * 0.01 + sx * 0.03 * k
            P.log(a, (xa, y, zc), (xa + sx * 0.04, y, zc), rr, key, sides=n, end_key=key,
                  name=f"{tag}roll_disc{sx:+d}{k}", kind="mat", amp=0.02)
    xs, w = ROLL["strap_x"], ROLL["strap_w"] / 2
    P.sleeve(a, (xs - w, y, zc), (xs + w, y, zc), ri * math.cos(math.pi / n), ro * math.cos(math.pi / n), STRAP,
             sides=n, name=f"{tag}roll_strap", kind="strap", amp=0.03)


FOLD = dict(x0=2.40, t=0.32, flap=0.28, z_bot=0.62, hw=0.48)


def folded_mat(a):
    """The folded mat over the +X shelf end: an L section (lying on the planks 0.01 in, hanging 0.003 off the plank and
    rail ends) extruded across, rounded at the fold; a brown strap over its lying part."""
    f = FOLD
    zt = SHELF_Z[1] - 0.01
    xe = SHELF_X + 0.003
    poly = [(f["x0"], zt), (xe, zt), (xe, f["z_bot"]), (xe + f["flap"] - 0.06, f["z_bot"]),
            (xe + f["flap"], f["z_bot"] + 0.08), (xe + f["flap"], zt + f["t"] - 0.12), (xe + f["flap"] - 0.12, zt + f["t"]),
            (f["x0"] + 0.06, zt + f["t"]), (f["x0"], zt + f["t"] - 0.08)]
    p = P.ext(a, poly, -f["hw"], f["hw"], MAT, to3=lambda u, v, w: Vector((u, w, v)), name="fold", kind="mat")
    P.texture(a, p.vs, 0.04, P.seed("fold"), scale=0.8)
    zl, zh = zt + 0.01, zt + f["t"]
    hw, s = f["hw"], 0.03
    u = [(-hw - s, zl), (-hw + 0.01, zl), (-hw + 0.01, zh - 0.01), (hw - 0.01, zh - 0.01), (hw - 0.01, zl),
         (hw + s, zl), (hw + s, zh + s), (-hw - s, zh + s)]
    P.ext(a, u, 2.78, 3.00, STRAP, to3=lambda uu, v, w: Vector((w, uu, v)), name="fold_strap", kind="strap", amp=0.03)


# ---- assemblies -----------------------------------------------------------------------------------------------------------
def hero_all(a):
    for s in (-1, 1):
        tag = "l_" if s < 0 else "r_"
        aframe(a, s, tag)
        binding(a, s, tag)
    top_beam(a)
    shelf(a)
    brace(a)
    cloth(a)
    sack(a)
    jug(a)
    bowl(a)
    roll(a)
    folded_mat(a)


def post_part(a):
    aframe(a, 1)


def beam_part(a):
    """The top beam from cap to cap (the exploded view's beam with its end-cap blocks)."""
    beam(a, -CAPB["x"][0] - 0.03, CAPB["x"][0] + 0.03)
    for s in (-1, 1):
        end_cap(a, s, name=f"cap{s:+d}")


def bind_part(a):
    binding(a, 1)


def shelf_part(a):
    shelf(a)


def brace_part(a):
    brace(a)


def cloth_part(a):
    cloth(a)


def sack_part(a):
    sack(a, (0.0, 0.0), lean=False)


def jug_part(a):
    jug(a, (0.0, 0.0), 0.0)


def bowl_part(a):
    bowl(a, (0.0, 0.0), 0.0)


def mat_part(a):
    roll(a, z_floor=0.01)


PARTS = ((POST_P, post_part), (BEAM_P, beam_part), (BIND_P, bind_part), (SHELF_P, shelf_part), (BRACE_P, brace_part),
         (CLOTH_P, cloth_part), (SACK_P, sack_part), (JUG_P, jug_part), (BOWL_P, bowl_part), (MAT_P, mat_part))
NOTES = {
    HERO: "Camp craft rack (sheet 078): two leaning square-timber A-frames with cross-ties, a top beam with block "
          "end-caps and pegs, rope bindings (turns and an X) with red cloth ties at the top junctions, a three-plank "
          "shelf on rails and a footed support brace, a canvas sling over the beam; props: a cloth sack with a red "
          "tie, an orange jug with a blue band, a deep bowl, a green rolled mat with a strap and a folded mat.",
    POST_P: "Side Post (A-Frame): two 0.58 square legs leaning to level tops 6.0 up, cross-tie, shelf rail, pegs",
    BEAM_P: "Top Beam: 0.50 x 0.78 beam with an end-cap block and peg at each end",
    BIND_P: "Rope binding: two flattened turns round an A-frame's legs, an X on each face, two red cloth ties",
    SHELF_P: "Shelf Plank: three 6.8-long planks, 0.52 x 0.34, side by side",
    BRACE_P: "Support Brace: a 4.6-long beam on two feet, pegged",
    CLOTH_P: "Cloth (Canvas): a cream sling draped over the beam, both flaps hanging in a V with broad flat folds",
    SACK_P: "Sack (Cloth): a faceted cream sack 3.0 tall with a gathered top and a red neck tie",
    JUG_P: "Jug (Ceramic): orange, blue band and neck, strap handle, 1.64 tall",
    BOWL_P: "Bowl (Ceramic): a deep tan bowl with a blue band, 0.95 tall",
    MAT_P: "Rolled Mat (Cloth): a green roll 1.65 long with rolled-layer ends and a brown strap",
}
COLLISION = {HERO: "hull", POST_P: "hull", BEAM_P: "box", BIND_P: "none", SHELF_P: "box", BRACE_P: "hull",
             CLOTH_P: "none", SACK_P: "hull", JUG_P: "hull", BOWL_P: "hull", MAT_P: "hull"}
BUDGETS = {HERO: 4000}
TARGET_SIZE = None
VIEWS = {"f34_sheet": (-24, 16), "r34_sheet": (158, 16), "front_sheet": (0, 0), "side_sheet": (90, 0),
         "rear_sheet": (180, 0), "top_sheet": (0, 70)}
EXPLODED = {POST_P: (-6.5, 0.0, 0.0), BEAM_P: (0.0, 0.0, 6.6), BIND_P: (-3.6, -0.5, 5.2), CLOTH_P: (0.0, 0.0, 4.0),
            SHELF_P: (0.0, 0.0, 2.3), BRACE_P: (0.0, 0.0, 0.0), SACK_P: (5.6, 0.0, 0.0), JUG_P: (8.2, 0.0, 3.2),
            BOWL_P: (8.2, 0.0, 1.8), MAT_P: (8.2, 0.0, 0.0)}
CLOSE = {"junction_cu": dict(at=(-2.45, -0.8, 4.8), r=1.6, az=-35, el=12),
         "props_cu": dict(at=(0.0, -0.2, 2.2), r=3.2, az=-25, el=20)}
VERIFY = dict(cls="asset")
# compare cells: sheet pixel boxes (spec Brief) and cameras
COMPARE = {"f34": {"box": (12, 100, 508, 440), "view": VIEWS["f34_sheet"][:2]},
           "r34": {"box": (516, 100, 1012, 440), "view": VIEWS["r34_sheet"][:2]},
           "front": {"box": (14, 498, 304, 700), "view": (0, 0)},
           "side": {"box": (312, 498, 472, 700), "view": (90, 0)},
           "rear": {"box": (478, 498, 745, 700), "view": (180, 0)},
           "top": {"box": (752, 498, 1012, 700), "view": VIEWS["top_sheet"][:2]}}


def after(objs):
    # The Side Post and Shelf parts' cut-wood ends are the only lighter faces; the colour/normal correlation may read
    # them as painted light (m073's post cap)
    for n in (POST_P, SHELF_P, BEAM_P, BRACE_P):
        objs[n]["kit_shading_ok"] = "cut end grain is half way to the light-timber swatch"


def build(render=True, close=False, spin=False):
    return MODEL.run(hero=(HERO, hero_all), parts=PARTS, notes=NOTES, collision=COLLISION, budgets=BUDGETS,
                     target_size=TARGET_SIZE, views=VIEWS, exploded=EXPLODED, close=CLOSE if close else None,
                     verify=VERIFY, render=render, after=after, spin=spin)


def preview(names=("f34_sheet", "front_sheet", "side_sheet")):
    return MODEL.preview(HERO, VIEWS, names)


def compare(cells=None, out_dir=None, height=360):
    import importlib
    import compare as C
    importlib.reload(C)
    return C.compare(NUM, {k: COMPARE[k] for k in (cells or COMPARE)}, out_dir=out_dir, height=height)
