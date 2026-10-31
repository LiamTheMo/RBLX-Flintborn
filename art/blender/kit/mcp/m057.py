"""057 Ancient Tree (references/057.png): the kit's giant, 32 studs tall. A massive twisted bell trunk of eight
plank-shingled strands (waist 9.4 x 8.0 at z 12.8, 13.6 x 12.0 at the foot, 38 deg CCW twist) is hollow at its foot:
a narrow front slit and a pointed back arch open into a dark cavity with slate rocks and a tuft inside. Eight high
buttress roots (three module shapes) snake out to split toes. Two side branch modules (with bare two-tine forks and
spurs) and two Y modules on the pale cut top feed seven leaf clumps (fix round 2: each a cauliflower cluster of
rounded sub-domes skinned in small leaf domes, toned light -> mid -> dark by height) round an open hub, plus a small
sprout clump on the trunk. Twelve lime
moss strands with bulb tips hang from the clump undersides. Round the foot: slate rocks (two tall slabs), pebbles,
lime moss pads and pointed lime grass tufts.

    import importlib, kit_models, m057; importlib.reload(kit_models); importlib.reload(m057); m057.build()

Build frame: studs, front -Y, +X right, ground z 0, trunk axis at (0, 0). Every object ends with its origin at its bbox
bottom centre; o["m057_offset"] is that origin in the build frame. Nothing sits below z 0, so the hero's trunk foot is
the bbox bottom (offset z 0). Names (spec 8): MonarchTree (hero), MonarchTreeTrunkCore, MonarchTreeBranchModule (BM1),
MonarchTreeCrownModule (the TL shape, BL in the hero), MonarchTreeRootModuleA / B / C. Pegs, bores, bosses and hollow
root ends only on the parts (decision 5). Colour is chosen by position and role, never by facing. Stages 5-6: none
(the sheet shows no effect). See art/blender/renders/models/M057/M057_spec.md.
"""
import math
import random
import time

import bmesh
import bpy
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M
import m012
import m033
import m047

NUM, TITLE, SHEET = 57, "Ancient Tree", "M057"
OFF = "m057_offset"
PFX = "_m057_"
HERO = "MonarchTree"
TRUNK_P, BRANCH_P, CROWN_P = "MonarchTreeTrunkCore", "MonarchTreeBranchModule", "MonarchTreeCrownModule"
ROOT_PA, ROOT_PB, ROOT_PC = "MonarchTreeRootModuleA", "MonarchTreeRootModuleB", "MonarchTreeRootModuleC"
PARTS = (TRUNK_P, BRANCH_P, CROWN_P, ROOT_PA, ROOT_PB, ROOT_PC)

LEAF_L, LEAF_M, LEAF_D = "m057_leaf_light", "m057_leaf_mid", "m057_leaf_dark"
STRAND, STRAND_D = "m057_strand", "m057_strand_deep"
BARK, BARK_L, BARK_D = "m057_bark", "m057_bark_light", "m057_bark_deep"
HOLLOW, CAVITY = "m057_hollow", "m057_cavity"
ROCK, ROCK_L, ROCK_S = "m057_rock", "m057_rock_light", "m057_rock_slate"
MOSS, GRASS, GRASS_D = "m057_moss", "m057_grass", "m057_grass_deep"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
Z = Vector((0.0, 0.0, 1.0))

# key -> (hex, roughness, low specular). Stage 4 (M057_spec.md "Stage 4") writes the calibrated values here.
PALETTE = {
    LEAF_L: ("#B3C205", 0.8, True),
    LEAF_M: ("#8AB51B", 0.85, True),
    LEAF_D: ("#3A6A26", 0.9, True),
    STRAND: ("#B8B407", 0.9, True),
    STRAND_D: ("#44690D", 0.9, True),
    BARK: ("#BC7B36", 0.9, False),
    BARK_L: ("#F0B868", 0.85, False),
    BARK_D: ("#7A4A24", 0.95, False),
    HOLLOW: ("#0E0803", 1.0, False),
    CAVITY: ("#301A0C", 1.0, False),
    ROCK: ("#9C9590", 0.85, False),
    ROCK_L: ("#B2ABA5", 0.85, False),
    ROCK_S: ("#576374", 0.9, False),
    MOSS: ("#C2C014", 0.95, True),
    GRASS: ("#B4B208", 0.85, True),
    GRASS_D: ("#4A6E13", 0.85, True),
}
# calibration targets (spec 5.4 / decision 13: rendered sRGB of the sheet's regions or swatches), K.sample kinds
TARGETS = {LEAF_L: ((0xD0, 0xDC, 0x07), "vivid"), LEAF_M: ((0x9C, 0xBC, 0x19), "green"),
           LEAF_D: ((0x3A, 0x6E, 0x22), "green"), STRAND: ((0xE0, 0xD8, 0x0A), "vivid"),
           STRAND_D: ((0x4E, 0x7A, 0x0E), "green"), BARK: ((0xB0, 0x6F, 0x35), "brown"),
           BARK_L: ((0xFA, 0xC1, 0x72), "brown"), BARK_D: ((0x6E, 0x40, 0x22), "brown"),
           HOLLOW: ((0x12, 0x0A, 0x04), "all"), CAVITY: ((0x3A, 0x22, 0x12), "all"),
           ROCK: ((0xCE, 0xC2, 0xBB), "all"), ROCK_L: ((0xD9, 0xCF, 0xC8), "all"),
           ROCK_S: ((0x6E, 0x78, 0x87), "all"), MOSS: ((0xCE, 0xCE, 0x17), "vivid"),
           GRASS: ((0xD2, 0xCD, 0x0A), "vivid"), GRASS_D: ((0x4E, 0x74, 0x14), "green")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    for m in list(bpy.data.materials):            # mixed keys from an earlier build: re-mix from the parents
        key = m.name[3:] if m.name.startswith("FB_m057_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = "m057_" + tail
            if k1 in PALETTE and k2 in PALETTE and pct.isdigit():
                K.fk().KIT_PALETTE.pop(key, None)
                K.mix_key(k1, k2, int(pct) / 100)


def calibrate(keys=None, iters=6, out_dir=None):
    """K.calibrate on this model's keys (TARGETS) on the kit's faceted test dome. Returns {key: (hex, rendered)}."""
    keys = keys or list(TARGETS)
    for k in keys:
        K.fk().material(k)
    try:
        return K.calibrate({k: TARGETS[k] for k in keys}, iters=iters, out_dir=out_dir)
    finally:
        for m in [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith("T_Calib")]:
            bpy.data.meshes.remove(m)


# ---- small helpers ----------------------------------------------------------------------------------------------------
_faces = m033._faces
_mottle = m033._mottle
_u = m047._u
_basis = m047._basis
_ring = m047._ring
_band = m047._band
_zip = m047._zip
_frames = m047._frames


def _mix(k1, k2, t):
    t = round(max(0.0, min(1.0, t)) * 4) / 4
    return K.mix_key(k1, k2, t)


def _paint(a, faces, key):
    mi = a._mi(key)
    for f in faces:
        if f.is_valid:
            f.material_index = mi


def _tint(a, faces, k):
    for f in faces:
        for l in f.loops:
            t = l[a.tint_layer][0] * k
            l[a.tint_layer] = (t, t, t, 1.0)


def _close(a, vs, fs, key):
    bmesh.ops.recalc_face_normals(a.bm, faces=[f for f in fs if f.is_valid])
    a._finish(vs, key, tint=1.0)


def _dir(rise, az):
    """Unit axis at plan azimuth az (deg), rising `rise` deg above horizontal."""
    r, p = math.radians(rise), math.radians(az)
    return Vector((math.cos(r) * math.cos(p), math.cos(r) * math.sin(p), math.sin(r)))


def _aspect(f):
    es = [e.calc_length() for e in f.edges]
    return max(es) / max(1e-6, min(es))


def _pit(a, f, size=0.42, depth=0.07):
    """A small square bark pit on face f: inset, the inner face squared to `size` about its centre in the face
    plane and sunk `depth` (hollow), its walls bark_deep."""
    if not f.is_valid or len(f.verts) != 4 or _aspect(f) > 2.4:
        return None
    es = [e.calc_length() for e in f.edges]
    th = max(0.04, 0.5 * min(es) - 0.5 * size - 0.02)
    r = bmesh.ops.inset_individual(a.bm, faces=[f], thickness=th, depth=0.0, use_even_offset=True)
    c = f.calc_center_median()
    n = f.normal.copy()
    vs = list(f.verts)
    e0 = (vs[1].co - vs[0].co)
    e0 = (e0 - n * e0.dot(n)).normalized()
    e1 = n.cross(e0)
    for v, (sx, sy) in zip(vs, ((-1, -1), (1, -1), (1, 1), (-1, 1))):
        v.co = c + e0 * (sx * size / 2) + e1 * (sy * size / 2) - n * depth
    _paint(a, [f], HOLLOW)
    _paint(a, r["faces"], BARK_D)
    return f


# ---- tubes (limbs, arms, tines, spurs, stubs, pegs) -------------------------------------------------------------------
def tube(a, pts, radii, n, u0=None, rot=0.0, start="flat", end="flat", key=BARK, hole=(0.4, 0.3), cap_key=BARK_L):
    """A closed n-sided tube along a polyline (parallel-transported frames, rings mitred on the bisector). Caps:
    "flat" (cut face, cap_key), "socket" (cut rim round a walled hole of radius hole[0] x ring radius, hole[1] deep,
    hollow). Returns (verts, side faces, caps {"cut": [...], "hole": [...]})."""
    bm = a.bm
    pts = [Vector(p) for p in pts]
    fr = _frames(pts, u0 if u0 is not None else _basis(pts[1] - pts[0])[0])
    rings = [[bm.verts.new(q) for q in _ring(p, u, v, r, n, rot)] for p, r, (t, u, v) in zip(pts, radii, fr)]
    side = []
    for i in range(len(rings) - 1):
        side += _band(bm, rings[i], rings[i + 1])
    vs = [v for r in rings for v in r]
    caps = {"cut": [], "hole": []}
    for which, ring, c, d, (t, u, v), r0 in (("s", rings[0], pts[0], -fr[0][0], fr[0], radii[0]),
                                            ("e", rings[-1], pts[-1], fr[-1][0], fr[-1], radii[-1])):
        kind = start if which == "s" else end
        if kind == "socket":
            hn = hole[2] if len(hole) > 2 else n
            inner = [bm.verts.new(q) for q in _ring(c, u, v, hole[0] * r0, hn, rot + 0.3)]
            deep = [bm.verts.new(q - d * hole[1]) for q in _ring(c, u, v, hole[0] * r0, hn, rot + 0.3)]
            caps["cut"] += _zip(bm, ring, inner, c, u, v)
            caps["hole"] += _band(bm, inner, deep) + [bm.faces.new(deep)]
            vs += inner + deep
        else:
            caps["cut"].append(bm.faces.new(ring if which == "e" else list(reversed(ring))))
    _close(a, vs, side + caps["cut"] + caps["hole"], key)
    _paint(a, caps["cut"], cap_key)
    _paint(a, caps["hole"], HOLLOW)
    return vs, side, caps


# ---- trunk core (spec 2.2, decision 6) --------------------------------------------------------------------------------
# outer rows: z, X diameter, Y diameter (strand crests), twist (deg, CCW from above). Rows 0..NWALL-1 carry the cavity.
TRUNK_ROWS = ((0.0, 13.6, 12.0, 0.0), (2.2, 12.9, 11.3, 3.0), (4.4, 12.2, 10.6, 6.0), (6.6, 11.4, 9.9, 9.0),
              (8.6, 10.7, 9.3, 11.5), (10.4, 10.0, 8.6, 14.0), (12.8, 9.4, 8.0, 21.0), (15.6, 9.0, 7.7, 30.0),
              (19.5, 6.6, 6.0, 38.0))
NWALL = 6
TOP_Z = TRUNK_ROWS[-1][0]
ROOT_AZ = (20.0, 60.0, 120.0, 160.0, 200.0, 240.0, 300.0, 340.0)      # strand azimuths at z 0 = root azimuths
CREST = (0.37, 0.63)          # crest columns at these fractions of the strand's groove-to-groove span
GROOVE = 0.75
SLIT_GROOVE = 0.95            # the front groove above the slit, up to row 6
JAMB_PULL = 0.4
INNER_F = 0.66                # cavity inner wall: 0.66 of the crest ellipse (wall 0.17 of the diameter)
DOME_Z = 12.0                 # cavity ceiling apex
OPENINGS = {   # groove azimuth, full width per wall row (rows 0..5; row 5 is the opening's closed top), width above
    "arch": dict(g=90.0, w=(3.4, 3.2, 2.9, 2.4, 1.5, 0.5), above=0.5),
    "slit": dict(g=270.0, w=(1.6, 1.4, 1.2, 0.9, 0.6, 0.4), above=0.42),
}
TRUNK_PITS = ((250.0, 12.0), (110.0, 13.2), (20.0, 11.2), (175.0, 13.6))
TRUNK_MOSS = ((268.0, 13.6), (104.0, 11.6))      # (az, z) of mossy plate cells
TRUNK_INFO = {}


def _row_twist(i):
    return TRUNK_ROWS[i][3]


def _ell_r(rx, ry, az):
    a = math.radians(az)
    return rx * ry / math.sqrt((ry * math.cos(a)) ** 2 + (rx * math.sin(a)) ** 2)


def _twist_at(z):
    for (z0, _, _, t0), (z1, _, _, t1) in zip(TRUNK_ROWS, TRUNK_ROWS[1:]):
        if z <= z1:
            return t0 + (t1 - t0) * max(0.0, (z - z0) / (z1 - z0))
    return TRUNK_ROWS[-1][3]


def _radii_at(z):
    for (z0, x0, y0, _), (z1, x1, y1, _) in zip(TRUNK_ROWS, TRUNK_ROWS[1:]):
        if z <= z1:
            t = max(0.0, (z - z0) / (z1 - z0))
            return (x0 + (x1 - x0) * t) / 2, (y0 + (y1 - y0) * t) / 2
    return TRUNK_ROWS[-1][1] / 2, TRUNK_ROWS[-1][2] / 2


def _columns():
    """Column descriptors round the ring at z 0 (CCW from az 0): ("g", az) grooves, ("c", az, j) strand crests,
    ("jL"/"jR", name) the jambs of an opening (split groove). Strand j spans its two grooves."""
    S = sorted(ROOT_AZ)
    n = len(S)
    gro = [((S[j] + ((S[(j + 1) % n] - S[j]) % 360) / 2)) % 360 for j in range(n)]     # groove after strand j
    cols = []
    for j in range(n):
        gl = gro[j - 1]
        gr = gro[j]
        span = (gr - gl) % 360
        # the groove before strand j
        op = next((k for k, o in OPENINGS.items() if abs(((o["g"] - gl) + 180) % 360 - 180) < 1e-6), None)
        if op:
            cols += [("jL", op, gl), ("jR", op, gl)]
        else:
            cols.append(("g", gl))
        cols += [("c", (gl + CREST[0] * span) % 360, j), ("c", (gl + CREST[1] * span) % 360, j)]
    return cols


def _col_az(col, i, unwrap_ref=None):
    """Plan azimuth of a column at outer row i (twist included; jambs at the opening's half width at that row)."""
    tw = _row_twist(i)
    if col[0] in ("jL", "jR"):
        o = OPENINGS[col[1]]
        z = TRUNK_ROWS[i][0]
        w = o["w"][i] if i < NWALL else o["above"]
        rx, ry = _radii_at(z)
        half = math.degrees((w / 2) / _ell_r(rx, ry, o["g"] + tw))
        return o["g"] + tw + (-half if col[0] == "jL" else half)
    return col[1] + tw


def trunk(a, part=False, cut=None):
    """The hollow-footed twisted eight-strand trunk as one closed shell: an outer ring stack of 26 columns (per strand
    a groove vertex pulled in and two crest verts; the slit and arch grooves split into two jamb columns), a cavity
    inner wall (two 7-vertex arcs between the openings) up to row 5 and a cone ceiling to DOME_Z, radial jamb faces
    round both openings, a bottom annulus, a flat pale cap with dark radial cracks. cut = a wall row index: the cavity
    walls only, up to that row, with a pale cut rim (close-up 3). Returns info dict."""
    bm = a.bm
    rng = random.Random(57100)
    cols = _columns()
    N = len(cols)
    nrows = len(TRUNK_ROWS) if cut is None else cut + 1
    S = sorted(ROOT_AZ)
    thick = {j: (1.05 if j % 2 == 0 else 0.95) for j in range(len(S))}
    jit = [rng.uniform(-1.2, 1.2) for _ in range(N)]
    O = []
    for i in range(nrows):
        z, dx, dy, tw = TRUNK_ROWS[i]
        rx, ry = dx / 2, dy / 2
        ring = []
        for k, col in enumerate(cols):
            az = _col_az(col, i) + (jit[k] if col[0] != "jL" and col[0] != "jR" else 0.0) * (1 if i else 0.4)
            R = _ell_r(rx, ry, az)
            sc = min(1.0, R / 4.0)
            if col[0] == "c":
                r = R * thick[col[2]] * (1 + rng.uniform(-0.012, 0.012))
            elif col[0] == "g":
                r = R - GROOVE * sc
            else:
                deep = SLIT_GROOVE if (col[1] == "slit" and i <= NWALL) else GROOVE
                r = R - (JAMB_PULL if i < NWALL else deep) * sc
            ring.append(bm.verts.new(Vector((math.cos(math.radians(az)) * r, math.sin(math.radians(az)) * r, z))))
        O.append(ring)
    jl = {name: next(k for k, c in enumerate(cols) if c[0] == "jL" and c[1] == name) for name in OPENINGS}
    jr = {name: jl[name] + 1 for name in OPENINGS}
    open_cells = {(i, jl[name]) for name in OPENINGS for i in range(min(NWALL - 1, nrows - 1))}
    outer = {}
    for i in range(nrows - 1):
        for k in range(N):
            if (i, k) in open_cells:
                continue
            outer[(i, k)] = bm.faces.new((O[i][k], O[i][(k + 1) % N], O[i + 1][(k + 1) % N], O[i + 1][k]))
    # cavity inner wall: two arcs between the openings
    arcs = (("arch", "slit"), ("slit", "arch"))
    nwall = min(NWALL, nrows)
    I = []            # I[i] = [arc0 verts, arc1 verts]
    NI = 3
    for i in range(nwall):
        z, dx, dy, tw = TRUNK_ROWS[i]
        rx, ry = dx / 2 * INNER_F, dy / 2 * INNER_F
        row = []
        for s, e in arcs:
            a0 = _col_az(cols[jr[s]], i)
            a1 = _col_az(cols[jl[e]], i)
            if a1 < a0:
                a1 += 360.0
            arc = []
            for m in range(NI + 2):
                az = a0 + (a1 - a0) * m / (NI + 1)
                r = _ell_r(rx, ry, az)
                arc.append(bm.verts.new(Vector((math.cos(math.radians(az)) * r, math.sin(math.radians(az)) * r, z))))
            row.append(arc)
        I.append(row)
    inner = []
    for i in range(nwall - 1):
        for q in range(2):
            A, B = I[i][q], I[i + 1][q]
            for m in range(len(A) - 1):
                inner.append(bm.faces.new((A[m], A[m + 1], B[m + 1], B[m])))
    # jambs: radial faces joining the outer jamb columns to the inner arc ends
    jambs = []
    inner_end = {}         # (opening, side) -> (arc index, vert index)
    for q, (s, e) in enumerate(arcs):
        inner_end[(s, "jR")] = (q, 0)
        inner_end[(e, "jL")] = (q, NI + 1)
    for name in OPENINGS:
        for side, kcol in (("jL", jl[name]), ("jR", jr[name])):
            q, m = inner_end[(name, side)]
            for i in range(min(NWALL - 1, nrows - 1)):
                jambs.append(bm.faces.new((O[i][kcol], O[i + 1][kcol], I[i + 1][q][m], I[i][q][m])))
        if cut is None:
            qL, mL = inner_end[(name, "jL")]
            qR, mR = inner_end[(name, "jR")]
            r5 = NWALL - 1
            jambs.append(bm.faces.new((O[r5][jl[name]], O[r5][jr[name]], I[r5][qR][mR], I[r5][qL][mL])))

    def zip_arc(Arow, Irow):
        """Triangles between the outer row's arc columns and the inner arc, for each of the two arcs, walked by az."""
        fs = []
        for q, (s, e) in enumerate(arcs):
            k0, k1 = jr[s], jl[e]
            ks = [k0]
            k = k0
            while k != k1:
                k = (k + 1) % N
                ks.append(k)
            A = [Arow[k] for k in ks]
            B = Irow[q]

            def ang(v, ref):
                return (math.degrees(math.atan2(v.co.y, v.co.x)) - ref) % 360.0
            ref = math.degrees(math.atan2(A[0].co.y, A[0].co.x)) - 1e-3
            ta = [ang(v, ref) for v in A]
            tb = [ang(v, ref) for v in B]
            ta = [t / ta[-1] for t in ta]
            tb = [t / tb[-1] for t in tb]
            ia = ib = 0
            while ia < len(A) - 1 or ib < len(B) - 1:
                if ib >= len(B) - 1 or (ia < len(A) - 1 and ta[ia + 1] <= tb[ib + 1]):
                    fs.append(bm.faces.new((A[ia], A[ia + 1], B[ib])))
                    ia += 1
                else:
                    fs.append(bm.faces.new((A[ia], B[ib + 1], B[ib])))
                    ib += 1
        return fs
    bottom = zip_arc(O[0], I[0])
    cap, ceiling, cracks = [], [], []
    if cut is None:
        loop = I[NWALL - 1][0] + I[NWALL - 1][1]
        apex = bm.verts.new(Vector((0.0, 0.0, DOME_Z)))
        ceiling = [bm.faces.new((loop[m], loop[(m + 1) % len(loop)], apex)) for m in range(len(loop))]
        ct = bm.verts.new(Vector((0.0, 0.0, TOP_Z)))
        top = O[-1]
        cap = [bm.faces.new((top[k], top[(k + 1) % N], ct)) for k in range(N)]
    else:
        cap = zip_arc(O[-1], I[cut])
    vs = [v for r in O for v in r] + [v for row in I for arc in row for v in arc]
    if cut is None:
        vs += [apex, ct]
    allf = list(outer.values()) + inner + jambs + bottom + cap + ceiling
    _close(a, vs, allf, BARK)
    # ---- colour: per-plate keys by role and position (never by facing)
    kinds = {k: c[0] for k, c in enumerate(cols)}
    for (i, k), f in outer.items():
        k2 = (k + 1) % N
        kk = {kinds[k], kinds[k2]}
        u = rng.random()
        if kk == {"c"}:                                   # the strand's crest plate
            key = BARK if u < 0.45 else _mix(BARK, BARK_L, 0.25) if u < 0.82 else _mix(BARK, BARK_D, 0.25)
        elif "jL" in kk or "jR" in kk:                    # beside an opening / its groove above
            key = _mix(BARK, BARK_D, 0.5) if (i >= NWALL - 1 or "c" not in kk) else _mix(BARK, BARK_D, 0.25)
        else:                                             # a groove flank
            key = _mix(BARK, BARK_D, 0.5) if u < 0.5 else _mix(BARK, BARK_D, 0.25) if u < 0.82 else BARK
        if i == 0 and key == BARK:
            key = _mix(BARK, BARK_D, 0.25)
        f.material_index = a._mi(key)
        _tint(a, [f], 1.0 + rng.uniform(-0.04, 0.04))
    _mottle(a, list(outer.values()), 0.03, 0.25, 57110)
    _paint(a, jambs, HOLLOW)
    _paint(a, inner + ceiling, CAVITY)
    _paint(a, bottom, _mix(BARK, BARK_D, 0.5))
    if cut is None:
        _paint(a, cap, BARK_L)
        for k in (1, 6, 10, 15, 19, 23):                 # radial cracks: thin dark fan wedges of the cap
            _paint(a, [cap[k]], HOLLOW)
        # moss plates (front above the slit, back beside the arch), by position
        for az, z in TRUNK_MOSS:
            tgt = Vector((math.cos(math.radians(az)) * 5, math.sin(math.radians(az)) * 5, z))
            f = min((g for (i, k), g in outer.items() if kinds[k] == "c" and kinds[(k + 1) % N] == "c"),
                    key=lambda g: (g.calc_center_median() - tgt).length)
            _paint(a, [f], MOSS)
        # bark pits on crest plates
        used = set()
        for az, z in TRUNK_PITS:
            tgt = Vector((math.cos(math.radians(az + _twist_at(z))) * 6, math.sin(math.radians(az + _twist_at(z))) * 6, z))
            cand = [g for (i, k), g in outer.items() if kinds[k] == "c" and kinds[(k + 1) % N] == "c" and g not in used
                    and 2.0 < g.calc_center_median().z < 17.5 and g.material_index != a._mi(MOSS) and _aspect(g) <= 2.4]
            f = min(cand, key=lambda g: (g.calc_center_median() - tgt).length)
            used.add(f)
            _pit(a, f, size=0.42, depth=0.08)
    else:
        _paint(a, cap, BARK_L)
    TRUNK_INFO.update(cols=N, rows=nrows, outer=len(outer))
    return [v for v in vs if v.is_valid]


def _trunk_vs_faces(vs):
    return _faces(vs)


# ---- roots (spec 2.3): buttress fins, vertical sections along a snaking plan path -------------------------------------
def ROOT_PROF(w, h):
    """The root's section (absolute offsets across, up): a flat bottom, near-upright lower flanks, two rounded
    shoulder facets and a broad flat crest - a thick log-like buttress, not a thin fin."""
    sh = max(0.35 * h, h - 0.55 * w)        # fix round 2: a rounder log top (steeper shoulders, narrower crest)
    return ((-0.44 * w, 0.0), (0.44 * w, 0.0), (0.5 * w, sh), (0.22 * w, h), (-0.22 * w, h * 0.985), (-0.5 * w, sh))


def TOE_PROF(w, h):
    return ((-0.5 * w, 0.0), (0.5 * w, 0.0), (0.0, h))


# kind -> stations (r, crest z, bottom z, width factor; r <= 0: from the reach), toe start r (from the reach), toe
# height. Fix round 2: the buttresses carry their crest out to r 9-11 at z 4-6.7 (the sheet's root shoulders at h .2
# span .63 of the width) as thick logs (width about 1.0 x at mid) with an S-bend through the kink, then the low run.
ROOT_KIND = {
    "A": dict(st=((4.4, 11.0, 5.4, 0.95), (6.6, 7.8, 0.0, 0.98), (9.0, 6.1, 0.0, 1.05), (-2.6, 3.8, 0.0, 0.95),
                  (-1.6, 2.1, 0.0, 0.78)), toe0=-2.8, th=1.6),
    "B": dict(st=((4.4, 11.6, 5.8, 0.95), (6.6, 8.3, 0.0, 0.98), (9.2, 6.5, 0.0, 1.05), (-2.6, 4.2, 0.0, 0.95),
                  (-1.6, 2.3, 0.0, 0.78)), toe0=-2.8, th=1.7),
    "C": dict(st=((4.4, 10.4, 5.0, 0.95), (6.4, 7.2, 0.0, 0.98), (8.6, 5.6, 0.0, 1.02), (-2.4, 3.5, 0.0, 0.92),
                  (-1.5, 2.0, 0.0, 0.78)), toe0=-2.6, th=1.5),
}
# name, azimuth, reach (toe tips), width, kind, bend at the kink (deg), toes, moss on the ridge (r0, r1)
ROOTS = (("RT1", 20.0, 12.8, 2.7, "A", 12.0, 2, None), ("RT2", 60.0, 12.0, 2.5, "B", -10.0, 2, None),
         ("RT3", 120.0, 11.6, 2.5, "C", 10.0, 2, None), ("RT4", 160.0, 13.4, 2.85, "A", -12.0, 2, None),
         ("RT5", 200.0, 13.8, 2.85, "B", 14.0, 2, (6.0, 8.4)), ("RT6", 240.0, 12.4, 2.7, "A", -10.0, 2, None),
         ("RT7", 300.0, 12.4, 2.7, "C", 10.0, 2, (6.0, 8.6)), ("RT8", 340.0, 13.6, 2.85, "B", -12.0, 2, None))
ROOT_TWIST = (14.0, 8.0, 1.0)        # station azimuth offsets (follow the twisted strand up the bell)
ROOT_SNAKE = (-0.35, 0.55)           # the outer stations swing this x the root's bend: an S through the kink
ROOT_INFO = {}


def _loft(a, stations, prof, key=BARK, start="flat", hole=(0.42, 0.3)):
    """A closed prism of vertical sections: stations = [(bottom centre, lateral unit, width, height)]; the section
    prof(w, h) -> absolute (across, up) offsets from the bottom centre, in the vertical plane through the lateral axis.
    start="socket": a square walled hole in the first section (the part's joining end). Returns (verts, rings, side,
    caps)."""
    bm = a.bm
    rings = [[bm.verts.new(P + s * x + Z * y) for x, y in prof(w, h)] for P, s, w, h in stations]
    side = []
    for i in range(len(rings) - 1):
        side += _band(bm, rings[i], rings[i + 1])
    vs = [v for r in rings for v in r]
    caps = {"cut": [], "hole": []}
    if start == "socket":
        P, s, w, h = stations[0]
        ring = rings[0]
        c = sum((v.co for v in ring), Vector()) / len(ring)
        t = (stations[1][0] - P)
        t = Vector((t.x, t.y, 0)).normalized()
        rad = hole[0] * min((v.co - c).length for v in ring)
        pts = [c + s * (math.cos(0.785 + k * 1.5708) * rad) + Z * (math.sin(0.785 + k * 1.5708) * rad) for k in range(4)]
        inn = [bm.verts.new(q) for q in pts]
        deep = [bm.verts.new(q + t * hole[1]) for q in pts]
        caps["cut"] += _zip(bm, ring, inn, c, s, Z)
        caps["hole"] += _band(bm, inn, deep) + [bm.faces.new(deep)]
        vs += inn + deep
    else:
        caps["cut"].append(bm.faces.new(list(reversed(rings[0]))))
    caps["cut"].append(bm.faces.new(rings[-1]))
    _close(a, vs, side + caps["cut"] + caps["hole"], key)
    _paint(a, caps["hole"], HOLLOW)
    return vs, rings, side, caps


def _plan_lateral(pts, i):
    """Horizontal unit across the plan path at station i."""
    p = [Vector((q.x, q.y, 0)) for q in pts]
    if i == 0:
        t = p[1] - p[0]
    elif i == len(p) - 1:
        t = p[-1] - p[-2]
    else:
        t = (p[i] - p[i - 1]).normalized() + (p[i + 1] - p[i]).normalized()
    t.normalize()
    return Vector((-t.y, t.x, 0.0)), t


def root(a, spec, part=False):
    """One buttress root module: a six-sided fin of vertical sections from deep in the bell flare (its high end and
    joining face buried in the trunk) down the concave buttress to the kink, then 2-3 blunt splayed toes (4-sided,
    flat on z 0, buried in the root end). The part: a square socket hole in the joining end and a pale peg."""
    name, az, reach, w, kind, bend, ntoe, moss = spec
    K_ = ROOT_KIND[kind]
    rng = random.Random(57200 + int(az))
    st = []
    r_prev = 0.0
    for i, (r, zt, zb, wf) in enumerate(K_["st"]):
        r = r if r > 0 else reach + r
        r = max(r, r_prev + 0.9)          # short roots: the stations stay in order (no fold at the kink)
        r_prev = r
        off = ROOT_TWIST[i] if i < len(ROOT_TWIST) else bend * ROOT_SNAKE[i - len(ROOT_TWIST)]
        st.append((Vector((math.cos(math.radians(az + off)) * r, math.sin(math.radians(az + off)) * r, zb)), zt - zb,
                   w * wf * rng.uniform(0.95, 1.05)))
    pts = [p for p, h, ww in st]
    stations = []
    for i, (p, h, ww) in enumerate(st):
        s, t = _plan_lateral(pts, i)
        stations.append((p, s, ww, h))
    vs, rings, side, caps = _loft(a, stations, ROOT_PROF, start="socket" if part else "flat")
    _paint(a, caps["cut"][-1:], _mix(BARK, BARK_D, 0.5))
    _paint(a, caps["cut"][:-1], BARK_L if part else BARK_D)
    nb = len(ROOT_PROF(1.0, 1.0))
    for i, f in enumerate(side):
        k = i % nb                     # section edge: 0 bottom, 1 / 5 lower flanks, 2 / 4 shoulders, 3 crest
        b = i // nb                    # band (plate) along the root
        c = f.calc_center_median()
        u = rng.random()
        if k == 0:
            f.material_index = a._mi(_mix(BARK, BARK_D, 0.5))
        elif k in (1, 5):
            f.material_index = a._mi(_mix(BARK, BARK_D, 0.25) if (u < 0.6 or c.z < 1.2) else BARK)
        elif k == 3:
            f.material_index = a._mi(_mix(BARK, BARK_L, 0.25) if u < 0.6 else BARK)
        else:
            f.material_index = a._mi(BARK if u < 0.6 else _mix(BARK, BARK_L, 0.25) if u < 0.85 else
                                     _mix(BARK, BARK_D, 0.25))
        _tint(a, [f], 1.0 + rng.uniform(-0.04, 0.04))
    if moss:                           # one mossy crest plate where the band's middle lies in the moss range
        for i, f in enumerate(side):
            c = f.calc_center_median()
            r = Vector((c.x, c.y, 0)).length
            if i % nb == 3 and moss[0] <= r <= moss[1]:
                f.material_index = a._mi(_mix(MOSS, BARK, 0.25))
    _mottle(a, side, 0.04, 0.35, 57210 + int(az))
    out = list(vs)
    # toes
    t0 = reach + K_["toe0"]
    base_az = az + bend
    spl = (-24.0, 0.0, 24.0) if ntoe == 3 else (-14.0, 14.0)
    tips = []
    for k, da in enumerate(spl):
        a_ = base_az + da * 0.35 + rng.uniform(-2, 2)
        s0 = Vector((math.cos(math.radians(base_az)) * (t0 - 0.6), math.sin(math.radians(base_az)) * (t0 - 0.6), 0.0))
        s0 += _u(base_az + 90.0) * ((k - (len(spl) - 1) / 2) * 0.55)     # toes start apart (no shared apex)
        dv = _u(base_az + da + rng.uniform(-4, 4))
        L = (reach - (t0 - 0.6)) * rng.uniform(0.92, 1.0) * (0.92 if (ntoe == 3 and k != 1) else 1.0)
        tip = s0 + dv * L
        s_a = Vector((-dv.y, dv.x, 0.0))
        tw_, th_ = 0.62 * w * 0.62, K_["th"]
        tv, trs, tside, tcaps = _loft(a, [(s0 + s_a * 0.0, s_a, tw_, th_), (tip, s_a, tw_ * 0.8, th_ * 0.62)], TOE_PROF)
        _paint(a, tcaps["cut"][1:], BARK_L if k % 2 == 0 else HOLLOW)
        _paint(a, tcaps["cut"][:1], BARK_D)
        for j, f in enumerate(tside):
            if j % 3 == 0:
                f.material_index = a._mi(_mix(BARK, BARK_D, 0.5))
        _mottle(a, tside, 0.04, 0.5, 57220 + k)
        tips.append(tip)
        out += tv
    if part:
        P, s, ww, h = stations[0]
        c = sum((v.co for v in rings[0]), Vector()) / nb
        tdir = (stations[1][0] - P)
        tdir = Vector((tdir.x, tdir.y, 0)).normalized()
        pv, _, _ = tube(a, [c + tdir * 0.32, c - tdir * 0.12], [0.42, 0.42], 6, None, 0.0, cap_key=BARK_L)
        _paint(a, _faces(pv), BARK_L)
        out += pv
    ROOT_INFO[name] = dict(stations=[(p.copy(), h) for p, s, ww, h in stations], tips=tips, kind=kind)
    return out


# ---- branch modules (spec 2.4) ----------------------------------------------------------------------------------------
LIMB_INFO = {}        # visibility polylines: module -> [list of points]
MOD_INFO = {}         # module -> {arm: dict(J, d, clump, pts)}

# main: (points, diameters, sides) from inside the trunk; arms: name -> (points, diameters, sides, feeds clump or None)
# tines: (base, tip, diameter); spur: (points, diameters, end key)
BM = {
    "BM1": dict(main=([(-3.0, -0.3, 15.2), (-7.6, -0.8, 15.9)], (3.4, 2.8), 8),
                arms={"main": ([(-7.4, -0.78, 15.88), (-9.6, -1.4, 16.4), (-11.1, -2.3, 18.6)],
                               (2.3, 1.75, 1.05), 6, "L"),
                      "spur": ([(-7.4, -0.8, 15.9), (-7.3, -3.6, 17.3), (-5.3, -7.8, 20.8)],
                               (1.9, 1.5, 0.9), 6, "FL")},
                tines=[((-9.9, -1.55, 16.5), (-12.6, -2.9, 16.0), 0.95), ((-9.9, -1.55, 16.5), (-12.2, -0.2, 15.4), 0.9)],
                spurs=[], pits=[(-6.0, -2.0, 15.2), (-9.4, -2.3, 16.0)]),
    "BM2": dict(main=([(3.0, 0.3, 15.5), (7.6, 0.6, 16.8)], (3.2, 2.6), 8),
                arms={"main": ([(7.4, 0.6, 16.7), (9.6, 0.9, 18.0), (10.8, 1.4, 19.9)],
                               (2.15, 1.6, 1.0), 6, "R")},
                tines=[((10.0, 1.0, 18.3), (13.0, -0.6, 17.6), 0.95), ((10.0, 1.0, 18.3), (12.7, 2.6, 17.0), 0.9)],
                spurs=[([(7.6, 0.6, 16.8), (8.2, 2.4, 19.0)], (1.4, 0.68), BARK_L)],
                pits=[(6.0, -0.9, 15.4), (9.0, -0.4, 17.0)]),
    "BM3": dict(main=([(-1.4, 0.6, 18.9), (-2.6, 1.8, 22.0)], (3.2, 2.8), 8),
                arms={"up": ([(-2.5, 1.7, 21.8), (-3.5, 2.6, 24.4), (-4.5, 3.4, 26.8)],
                             (2.1, 1.6, 1.0), 6, "BL"),
                      "out": ([(-2.5, 1.7, 21.8), (-5.6, 2.8, 21.6), (-9.1, 4.6, 20.8)],
                              (1.95, 1.45, 0.85), 6, "LB")},
                tines=[], spurs=[], pits=[(-2.4, 0.4, 21.0)]),
    "BM4": dict(main=([(1.4, -0.4, 18.9), (2.4, 0.4, 22.4)], (3.4, 3.0), 8),
                arms={"up": ([(2.35, 0.35, 22.2), (3.0, 4.8, 25.2), (3.5, 9.4, 27.4)],
                             (2.4, 1.8, 1.0), 6, "BR"),
                      "out": ([(2.35, 0.35, 22.2), (3.8, -3.2, 23.6), (4.5, -7.4, 24.5)],
                              (2.0, 1.5, 0.85), 6, "FR")},
                tines=[], spurs=[], pits=[(2.3, -1.2, 21.3)]),
}
SPROUT = dict(base=(-2.8, -3.0, 13.4), d=(232.0, 14.0), L=3.0, r=(0.75, 0.55))


def module(a, name, part=False):
    """One branch module: an 8-sided main run from inside the trunk (the part: a bored base and a pale peg), 6-sided
    arms from inside its knuckle (tapering to <= 0.5 of the module's base and on into their clump cores), 4-sided bare
    tines (flat ends, half pale / half hollow), 5-sided spurs with pale cut ends, a deep ring at the knuckle and pits."""
    B = BM[name]
    pts, dia, n = B["main"]
    pts = [Vector(p) for p in pts]
    out = []
    vs, side, caps = tube(a, pts, [d / 2 for d in dia], n, None, math.pi / n, start="socket" if part else "flat",
                          hole=(0.42, 0.45, 6), cap_key=BARK_L)
    _paint(a, caps["cut"][:1], BARK_L if part else BARK_D)
    _paint(a, caps["cut"][1:], _mix(BARK, BARK_D, 0.25))   # fix round 1: the knuckle end is a joint, not a cut (dec. 5)
    _mottle(a, side, 0.04, 0.4, 57300 + n)
    allside = list(side)
    out += vs
    if part:
        d0 = (pts[1] - pts[0]).normalized()
        pv, _, _ = tube(a, [pts[0] + d0 * 0.47, pts[0] - d0 * 0.35], [0.55, 0.55], 6, None, 0.0, cap_key=BARK_L)
        _paint(a, _faces(pv), BARK_L)
        out += pv
    LIMB_INFO[name] = [list(pts)]
    info = MOD_INFO.setdefault(name, {})
    Kn = pts[-1]
    for arm, (apts, adia, an, feed) in B["arms"].items():
        apts = [Vector(p) for p in apts]
        d0 = (apts[1] - apts[0]).normalized()
        p0 = apts[0] - d0 * 0.35
        av, aside, acaps = tube(a, [p0] + apts[1:], [adia[0] / 2] + [d / 2 for d in adia[1:]], an, None, 0.2,
                                cap_key=BARK_L)
        _paint(a, acaps["cut"][:1], _mix(BARK, BARK_D, 0.25))     # its root end sits in the knuckle: bark, not cut
        _mottle(a, aside, 0.04, 0.45, 57310 + len(out))
        allside += aside
        out += av
        LIMB_INFO[name].append(apts)
        if feed:
            info[arm] = _feed_info(apts, feed)
    for base, tip, dd in B["tines"]:
        base, tip = Vector(base), Vector(tip)
        d0 = (tip - base).normalized()
        tv, tside, tcaps = tube(a, [base - d0 * 0.45, tip], [dd / 2, dd / 4.2], 4, None, 0.4, cap_key=BARK_L)
        _paint(a, tcaps["cut"][1:], BARK_L if tip.y < base.y else HOLLOW)
        _paint(a, tcaps["cut"][:1], _mix(BARK, BARK_D, 0.25))
        _mottle(a, tside, 0.04, 0.5, 57320 + len(out))
        allside += tside
        out += tv
        LIMB_INFO[name].append([base, tip])
    for spts, sdia, ekey in B["spurs"]:
        spts = [Vector(p) for p in spts]
        d0 = (spts[1] - spts[0]).normalized()
        sv, sside, scaps = tube(a, [spts[0] - d0 * 0.4] + spts[1:], [d / 2 for d in sdia], 5, None, 0.0, cap_key=ekey)
        _paint(a, scaps["cut"][:1], _mix(BARK, BARK_D, 0.25))
        allside += sside
        out += sv
        LIMB_INFO[name].append(spts)
    # bark-deep ring at the knuckle (position along the run), pits
    for f in allside:
        if f.is_valid and (f.calc_center_median() - Kn).length < 1.2:
            f.material_index = a._mi(_mix(BARK, BARK_D, 0.25))
    for p in B["pits"]:
        cand = [f for f in allside if f.is_valid and len(f.verts) == 4 and _aspect(f) <= 2.4]
        if not cand:
            continue
        f = min(cand, key=lambda g: (g.calc_center_median() - Vector(p)).length)
        _pit(a, f, size=0.36, depth=0.06)
    return out


def sprout_stub(a, part=False):
    """The trunk sprout's 5-sided stub from inside the trunk front-left, rising out toward az 235."""
    s = SPROUT
    b = Vector(s["base"])
    d = _dir(s["d"][1], s["d"][0])
    tip = b + d * s["L"]
    vs, side, caps = tube(a, [b, tip], list(s["r"]), 5, None, 0.0, cap_key=BARK_L)
    _mottle(a, side, 0.04, 0.5, 57330)
    MOD_INFO.setdefault("SP", {})["stub"] = dict(J=b + d * (s["L"] - 0.6), tip=tip, d=d, clump="SP",
                                                 pts=[b.copy(), tip.copy()])
    return vs


def bosses_part(a):
    """Trunk core part only: the two side bosses (8-sided collars with socket holes) and the two cap sockets."""
    out = []
    for name, rise in (("BM1", 10.0), ("BM2", 12.0)):
        p0, p1 = [Vector(p) for p in BM[name]["main"][0]]
        d = (p1 - p0).normalized()
        A = p0
        # the bark along d from the axis side
        F = p0 + d * 2.3
        vs, side, caps = tube(a, [A, F], [1.85, 1.7], 8, None, math.pi / 8, end="socket", hole=(0.45, 0.45, 6))
        _paint(a, side, _mix(BARK, BARK_L, 0.25))
        out += vs
    for name in ("BM3", "BM4"):
        p0, p1 = [Vector(p) for p in BM[name]["main"][0]]
        c = Vector((p0.x, p0.y, TOP_Z))
        vs, side, caps = tube(a, [c - Z * 0.4, c + Z * 0.18], [1.05, 1.0], 8, None, 0.0, end="socket",
                              hole=(0.62, 0.4, 6))
        _paint(a, side, BARK_L)
        out += vs
    return out


# ---- leaf clumps (spec 2.5; fix round 2: lump clusters) ---------------------------------------------------------------
# Fix round 2 (main-session ruling on the budget block, 2026-10-30): the core IS the foliage. Each clump is a cauliflower
# cluster of overlapping rounded sub-domes (the macro lumps of lump_specs: a filler, a crown lump and two rings turned
# radially outward), skinned as ONE closed shell: the union of the lumps sampled from the clump centre, faceted into
# small leaf domes (spherical Voronoi cells: a raised apex fanned to recessed valley verts, 6 tris per dome). Separate
# lump shells cost 16-20 tris each and hide half of them inside their neighbours; the skin spends every tri on the
# visible surface, so the hero gets about 270 leaf domes (each about 3 studs across, the sheet's lobe pitch) over about
# 85 sub-domes. Leaf tones by height in the clump and by the dome's own height (dark undersides by height, never by
# facing), Tint per sub-dome.
# centre, envelope bottom z, top z, W, D, tone shift, tilt (deg the mound leans out from the trunk, outer side down),
# extra fill domes (the underside and inner sides), seed
CLUMPS = {
    "BR": dict(c=(2.6, 8.6), zc0=23.2, zt=31.2, W=14.6, D=20.0, tone=0.15, tilt=10, fill=2, seed=57401),
    "BL": dict(c=(-4.6, 2.8), zc0=23.0, zt=29.8, W=12.4, D=12.0, tone=0.15, tilt=6, fill=2, seed=57402),
    "FR": dict(c=(4.6, -6.0), zc0=20.0, zt=29.8, W=13.6, D=16.6, tone=0.1, tilt=10, fill=2, seed=57403),
    "LB": dict(c=(-9.8, 4.2), zc0=18.0, zt=25.8, W=12.0, D=12.4, tone=-0.15, tilt=20, fill=2, seed=57404),
    "R": dict(c=(10.2, 1.2), zc0=15.8, zt=24.2, W=13.6, D=12.0, tone=0.05, tilt=26, fill=2, seed=57405),
    "L": dict(c=(-10.2, -1.8), zc0=15.4, zt=22.6, W=13.4, D=11.8, tone=-0.05, tilt=26, fill=2, seed=57406),
    "FL": dict(c=(-4.8, -8.4), zc0=18.8, zt=25.2, W=10.8, D=11.4, tone=-0.15, tilt=22, fill=2, seed=57407),
    # bump_k: full-size dome bumps read as a spiky star on this small clump (verifier round 2, minor 1)
    "SP": dict(c=(-4.7, -5.4), zc0=12.8, zt=16.4, W=4.8, D=4.6, tone=-0.05, tilt=0, fill=2, seed=57408, bump_k=0.45),
}
# per clump: the macro lump rings (polar deg from the top, count, size factor); the filler and the crown lump come first
LUMP_RINGS = {
    "BR": ((48.0, 4, 1.0), (98.0, 8, 1.0)),
    "BL": ((50.0, 3, 1.0), (98.0, 5, 1.0)),
    "FR": ((48.0, 4, 1.0), (98.0, 8, 1.0)),
    "LB": ((50.0, 3, 1.0), (98.0, 7, 1.0)),
    "R": ((48.0, 3, 1.0), (98.0, 8, 1.0)),
    "L": ((48.0, 3, 1.0), (98.0, 8, 1.0)),
    "FL": ((50.0, 3, 1.0), (98.0, 6, 1.0)),
    "SP": ((70.0, 3, 1.0),),
}
LUMP_SQUASH = 0.8             # a lump's vertical radius vs its horizontal one
LUMP_SPREAD = 0.56            # lump radius = this x the ring's lump spacing (neighbours overlap)
LUMP_INSET = 0.15             # a ring lump's centre sits this x its radius inside the envelope
LUMP_UP = 0.55                # a lump's up axis: the envelope normal + this x +Z (rounded tops face the sky a little)
ENV_K = (0.6, 0.72)           # the envelope the lumps sit on: x the clump's W, D and x its height
CORE_K = (0.62, 0.62, 0.55)   # the filler lump: x the envelope's half W, D and height
TOP_K = 0.46                  # the crown lump's horizontal radius: x the envelope's mean half width
DOME_BUMP = (0.38, 0.62)     # a leaf dome's apex: raised this far (studs, random in the range) off the lump union
DOME_DIP = 0.50               # its valley verts: sunk this far below the union
CELL_RELAX = 20               # repulsion steps that even out the fill cells
PETALS = 3                    # leaf domes round each sub-dome's peak dome
PETAL_INNER = -0.35           # a ring lump facing the trunk more than this (cos) gets no petals (hidden side)
PETAL_POLAR = 55.0            # their angle from the sub-dome's up axis (deg)
FILL_SEP = 0.9                # fill cells keep this x the mean cell spacing from every other cell
CLUMP_INFO = {}
CLUMP_DROPPED = []
TONE_STEPS = ((0.30, LEAF_D), (0.40, (LEAF_M, LEAF_D, 0.5)), (0.50, (LEAF_M, LEAF_D, 0.25)), (0.60, LEAF_M),
              (0.70, (LEAF_M, LEAF_L, 0.5)), (0.80, (LEAF_M, LEAF_L, 0.75)), (9.9, LEAF_L))
TONE_FACE, TONE_LUMP, TONE_SUB, TONE_BASE, TONE_NOISE = 0.3, 0.15, 0.55, -0.04, 0.22
TONE_CREASE = 0.3


def _away(c):
    v = Vector((c[0], c[1], 0.0))
    return v.normalized() if v.length > 1e-3 else Vector((0, 1, 0))


def clump_params(name, **over):
    P = dict(CLUMPS[name])
    P.update(over)
    if name == "SP":
        P["small"] = True
    H = P["zt"] - P["zc0"]
    P.update(ax=P["W"] / 2 * ENV_K[0], ay=P["D"] / 2 * ENV_K[0], H=H)
    H *= ENV_K[1]         # the envelope shrinks about its middle height: the lumps stand proud of it
    zm = P["zc0"] + 0.5 * (P["zt"] - P["zc0"])
    zc0 = zm - 0.5 * H
    P.update(zc=zc0 + 0.38 * H, hu=0.62 * H, hd=0.38 * H, zt_env=zc0 + H)
    return P


def _env(P, th, ph):
    """Point and outward normal on the clump envelope (an ellipsoid, flatter below) at polar th and azimuth ph (rad),
    unturned."""
    st, ct = math.sin(th), math.cos(th)
    h = P["hu"] if ct >= 0 else P["hd"]
    p = Vector((P["c"][0] + P["ax"] * st * math.cos(ph), P["c"][1] + P["ay"] * st * math.sin(ph), P["zc"] + h * ct))
    nrm = Vector((st * math.cos(ph) / P["ax"], st * math.sin(ph) / P["ay"], ct / h)).normalized()
    return p, nrm


def lump_specs(name, P):
    """The clump's macro lumps (sub-domes) before the tilt: [(role, centre, up, rx, ry, rz_up, rz_dn)]: the filler, the
    crown lump, then the rings (staggered, azimuths jittered), each turned radially outward."""
    rng = random.Random(P["seed"] + 11)
    ax, ay = P["ax"], P["ay"]
    am = 0.5 * (ax + ay)
    out = [("core", Vector((P["c"][0], P["c"][1], P["zc"])), Z.copy(), CORE_K[0] * ax, CORE_K[1] * ay,
            P["hu"] * 0.72, P["hd"] * 0.9)]
    rt = TOP_K * am
    out.append(("top", Vector((P["c"][0], P["c"][1], P["zt_env"] - rt * LUMP_SQUASH * LUMP_INSET)), Z.copy(), rt,
                rt * 0.95,
                rt * LUMP_SQUASH, rt * LUMP_SQUASH))
    ph0 = rng.uniform(0, 2 * math.pi)
    for ri, (pol, cnt, kk) in enumerate(P.get("rings") or LUMP_RINGS[name]):
        th = math.radians(pol)
        R = LUMP_SPREAD * 2 * math.pi * am * math.sin(th) / cnt * kk
        for k in range(cnt):
            ph = ph0 + 2 * math.pi * (k + 0.5 * ri) / cnt + math.radians(rng.uniform(-9, 9))
            p, nrm = _env(P, th + math.radians(rng.uniform(-6, 6)), ph)
            r = R * rng.uniform(0.9, 1.1)
            up = (nrm + Z * LUMP_UP).normalized()
            out.append(("ring%d" % ri, p - nrm * (LUMP_INSET * r), up, r, r * rng.uniform(0.88, 1.0),
                        r * LUMP_SQUASH, r * LUMP_SQUASH))
    return out


def _lump_exit(o, d, L):
    """Distance along the unit ray o + t d at which it leaves macro lump L (two half ellipsoids about its up axis:
    rz_up above the centre, rz_dn below), or None if it misses."""
    role, c, up, rx, ry, rzu, rzd = L
    u, v = _basis(up)
    p = o - c
    P0 = (p.dot(u) / rx, p.dot(v) / ry, p.dot(up))
    D0 = (d.dot(u) / rx, d.dot(v) / ry, d.dot(up))
    best = None
    for rz, upper in ((rzu, True), (rzd, False)):
        Pz = Vector((P0[0], P0[1], P0[2] / rz))
        Dz = Vector((D0[0], D0[1], D0[2] / rz))
        qa, qb, qc = Dz.dot(Dz), 2 * Pz.dot(Dz), Pz.dot(Pz) - 1.0
        disc = qb * qb - 4 * qa * qc
        if disc < 0:
            continue
        t = (-qb + math.sqrt(disc)) / (2 * qa)
        if t <= 0 or ((P0[2] + D0[2] * t) >= 0) != upper:
            continue
        best = t if best is None else max(best, t)
    return best


def _union_r(C0, d, lumps):
    """The lump union's radius from C0 along unit d (the last exit of any lump: a radial shrink-wrap) and the owner."""
    best, who = 0.0, 0
    for i, L in enumerate(lumps):
        t = _lump_exit(C0, d, L)
        if t is not None and t > best:
            best, who = t, i
    return best, who


def _fib(n, seed):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        zz = 1 - 2 * (i + 0.5) / n
        rr = math.sqrt(max(0.0, 1 - zz * zz))
        ph = i * math.radians(137.508) + rng.uniform(-0.15, 0.15)
        out.append(Vector((rr * math.cos(ph), rr * math.sin(ph), zz)))
    return out


def _relax(pts, fixed, steps, seed):
    """Even out unit vectors by short-range repulsion (fixed ones stay)."""
    n = len(pts)
    if n < 3:
        return pts
    h = math.sqrt(4 * math.pi / n)
    for _ in range(steps):
        new = []
        for i, p in enumerate(pts):
            if i < fixed:
                new.append(p)
                continue
            f = Vector()
            for j, q in enumerate(pts):
                if i == j:
                    continue
                dv = p - q
                L = dv.length
                if L < 2.2 * h:
                    f += dv.normalized() * (1.0 - L / (2.2 * h)) ** 2
            new.append((p + f * 0.18 * h).normalized())
        pts = new
    return pts


def _hull_tris(dirs):
    """Spherical Delaunay of unit vectors: the convex hull's triangles (index triples, wound outward)."""
    bm = bmesh.new()
    vs = [bm.verts.new(d) for d in dirs]
    for i, v in enumerate(vs):
        v.index = i
    bmesh.ops.convex_hull(bm, input=vs, use_existing_faces=False)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
    tris = []
    for f in bm.faces:
        ids = [v.index for v in f.verts]
        a_, b_, c_ = (dirs[i] for i in ids)
        if (b_ - a_).cross(c_ - a_).dot(a_ + b_ + c_) < 0:
            ids = ids[::-1]
        tris.append(tuple(ids))
    bm.free()
    return tris


def clump_skin(a, name, P, guard=None):
    """The clump as one closed shell: N leaf domes (cells) on the union of its macro lumps. Cell seeds in the
    envelope's normalised space: one on each macro lump's peak, the rest Fibonacci, relaxed; their spherical Delaunay
    gives each dome's ring of valley verts (the Voronoi corners). Apexes sit DOME_BUMP above the union, valleys
    DOME_DIP below it; the whole mound is then turned by the clump's tilt. Returns (verts, faces, info)."""
    rng = random.Random(P["seed"])
    lumps = lump_specs(name, P)
    cx, cy, zc = P["c"][0], P["c"][1], P["zc"]
    C0 = Vector((cx, cy, zc))
    S = (P["ax"], P["ay"])

    def to_n(p):
        q = p - C0
        return Vector((q.x / S[0], q.y / S[1], q.z / (P["hu"] if q.z >= 0 else P["hd"]))).normalized()

    def to_w(dn):
        return Vector((dn.x * S[0], dn.y * S[1], dn.z * (P["hu"] if dn.z >= 0 else P["hd"]))).normalized()

    # seeds: each sub-dome's peak and a ring of PETALS around it (a rosette of leaf domes per sub-dome, so the cell
    # borders fall on the creases between sub-domes), then a sparse Fibonacci fill (the hidden underside and inner
    # sides), relaxed with the rosettes held
    seeds = []
    for role, c, up, rx, ry, rzu, rzd in lumps:
        if role == "core":
            continue
        u, v = _basis(up)
        seeds.append(to_n(c + up * rzu))
        ph = rng.uniform(0, 2 * math.pi)
        b = math.radians(PETAL_POLAR)
        hz = Vector((up.x, up.y, 0.0))
        out_k = hz.normalized().dot(_away(P["c"])) if hz.length > 0.2 else 1.0
        for k in range(PETALS if (out_k > PETAL_INNER or role == "top") else 0):     # inner-side lumps: one dome
            f = ph + 2 * math.pi * k / PETALS
            q = c + up * (rzu * math.cos(b)) + (u * (math.cos(f) * rx) + v * (math.sin(f) * ry)) * math.sin(b)
            dn = to_n(q)
            if all(dn.angle(o_) > 0.12 for o_ in seeds):
                seeds.append(dn)
    N = len(seeds) + P.get("fill", 4)
    sep = FILL_SEP * math.sqrt(4 * math.pi / max(N, len(seeds) + 4))
    fill = []
    for d in _fib(N * 4, P["seed"]):
        if len(fill) + len(seeds) >= N:
            break
        if all(d.angle(q) > sep for q in seeds + fill):
            fill.append(d)
    dirs = _relax(seeds + fill, len(seeds), CELL_RELAX, P["seed"])
    tris = _hull_tris(dirs)
    bm = a.bm
    piv, Rm = _turn(P)
    P.update(R=Rm, piv=piv)
    apex, owner = [], []
    for i, dn in enumerate(dirs):
        dw = to_w(dn)
        r, who = _union_r(C0, dw, lumps)
        apex.append(C0 + dw * (r + rng.uniform(*DOME_BUMP) * P.get("bump_k", 1.0)))
        owner.append(who)
    valley, crease = [], []
    for t in tris:
        dn = sum((dirs[i] for i in t), Vector()).normalized()
        dw = to_w(dn)
        r, who = _union_r(C0, dw, lumps)
        valley.append(C0 + dw * max(0.3, r - DOME_DIP * P.get("bump_k", 1.0)))
        # crease depth: how far this corner sits below its three domes' apexes (the creases between sub-domes are
        # deep): a concavity term for the tones, by position, never by facing
        crease.append(sum((apex[i] - C0).length for i in t) / 3 - (valley[-1] - C0).length)
    unturned = apex + valley
    AV = [bm.verts.new(piv + Rm @ (p - piv)) for p in apex]
    WV = [bm.verts.new(piv + Rm @ (p - piv)) for p in valley]
    around = {i: [] for i in range(len(dirs))}
    for ti, t in enumerate(tris):
        for i in t:
            around[i].append(ti)
    fs, cell_of, face_cr = [], [], []
    c_lo = sorted(crease)[len(crease) // 5]
    c_hi = sorted(crease)[-max(1, len(crease) // 10)]
    for i, tl in around.items():
        d = dirs[i]
        u, v = _basis(d)
        cen = {ti: sum((dirs[j] for j in tris[ti]), Vector()) for ti in tl}
        tl = sorted(tl, key=lambda ti: math.atan2(cen[ti].dot(v), cen[ti].dot(u)))
        for k in range(len(tl)):
            f = bm.faces.new((AV[i], WV[tl[k]], WV[tl[(k + 1) % len(tl)]]))
            fs.append(f)
            cell_of.append(i)
            cr = 0.5 * (crease[tl[k]] + crease[tl[(k + 1) % len(tl)]])
            face_cr.append(min(1.0, max(0.0, (cr - c_lo) / max(1e-3, c_hi - c_lo))))
    vs = AV + WV
    _close(a, vs, fs, LEAF_M)
    # tones: height in the clump (unturned frame) blended with the dome's own height; Tint per macro lump (+ a little
    # per dome); broad mottling
    zlo = min(p.z for p in unturned)
    zhi = max(p.z for p in unturned)
    span = max(1e-3, zhi - zlo)
    lump_t = [1.0 + rng.uniform(-0.05, 0.05) for _ in lumps]
    cell_t = [lump_t[owner[i]] + rng.uniform(-0.015, 0.015) for i in range(len(dirs))]
    # one tone per leaf dome (all its faces), like one key per leaf: its apex height in the clump and in its sub-dome,
    # the crease depth round it and position noise; never per face, so the tones don't follow the face normals
    cell_fc = {}
    for i, fc in zip(cell_of, face_cr):
        cell_fc.setdefault(i, []).append(fc)
    cell_key = {}
    for i in range(len(dirs)):
        pu = apex[i]
        hl = (pu.z - zlo) / span
        role, lc, lup, lrx, lry, lrzu, lrzd = lumps[owner[i]]
        hm = min(1.0, max(0.0, ((pu - lc).dot(lup) + lrzd) / (lrzu + lrzd)))      # height within its sub-dome
        fc = sum(cell_fc.get(i, [0.0])) / max(1, len(cell_fc.get(i, [])))
        th, tn = P.get("tone_h", 1.0), P.get("tone_n", TONE_NOISE)
        x = (th * ((TONE_FACE + TONE_LUMP) * hl + TONE_SUB * hm - TONE_CREASE * fc) + (1 - th) * 0.55 + TONE_BASE
             + P["tone"] + tn * noise.noise(pu * 0.3 + Vector((P["seed"] % 97, 3.1, 7.7))))
        cell_key[i] = _tone_key(x)
    for f, i in zip(fs, cell_of):
        f.material_index = a._mi(cell_key[i])
        for l in f.loops:
            l[a.tint_layer] = (cell_t[i], cell_t[i], cell_t[i], 1.0)
    _mottle(a, fs, 0.03, 0.45, P["seed"] + 3)
    info = dict(cells=len(dirs), lumps=len(lumps), tris=len(fs))
    if guard is not None:
        info["moved_off_wood"] = _clear_wood(vs, guard)
        info["in_wood"] = round(guard.depth(vs), 3)
    return vs, fs, info


def _clear_wood(vs, solids, gap=0.06, tries=4):
    """Skin verts inside the wood (an arm entering the clump, the trunk top): each is moved to the nearest wood surface
    point plus `gap` along its normal (a small local dent round the limb), repeated while any is still inside.
    Returns the number moved."""
    moved = 0
    for _ in range(tries):
        bad = 0
        for v in vs:
            d, who = solids.point(v.co)
            if d <= BURY_PLACE * 0.5 or who is None:
                continue
            tree = next(t for nm, lo, hi, t in solids.items if nm == who)
            loc, nrm, _, _ = tree.find_nearest(v.co)
            if loc is None:
                continue
            v.co = loc + nrm.normalized() * gap
            bad += 1
        moved += bad
        if not bad:
            break
    return moved


def _turn(P):
    away = _away(P["c"])
    piv = Vector((P["c"][0], P["c"][1], P["zc0"] + 0.3 * P["H"]))
    Rm = Matrix.Rotation(math.radians(P.get("tilt", 0.0)), 3, Z.cross(away).normalized())
    return piv, Rm


def _tone_key(x):
    for lim, k in TONE_STEPS:
        if x < lim:
            return k if isinstance(k, str) else _mix(*k)
    return LEAF_L


def leaf_clump(a, name, stub=False, pre=None, guard=None):
    """A clump: its skin of leaf domes over the macro lumps (clump_skin). stub (the part): the module's 5-sided stub
    from below into the clump, a bore in its base."""
    P = clump_params(name) if pre is None else pre
    out = []
    vs, fs, info = clump_skin(a, name, P, guard)
    if stub:
        idx = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[idx[v] for v in f.verts] for f in fs])
        for m, ar in MOD_INFO.items():
            for arm, ainfo in ar.items():
                if ainfo.get("clump") != name:
                    continue
                d = ainfo["d"]
                base = ainfo["tip"].copy()           # back down the arm until clear of the clump, then 1.2 more
                for _ in range(60):
                    if not m047._parity_in(tree, base):
                        break
                    base = base - d * 0.2
                base = base - d * 1.2
                J = base + (ainfo["tip"] - base) * 0.45
                sv, sside, scaps = tube(a, [base, J, ainfo["tip"] + d * 0.3], [0.62, 0.58, 0.5], 5, None, 0.0,
                                        start="socket", hole=(0.45, 0.3, 5), cap_key=BARK_L)
                _paint(a, scaps["cut"], BARK_L)
                out += sv
                sg = m047._Solids()
                sg.add_vs(sv, "stub")
                info["moved_off_stub"] = _clear_wood(vs, sg)
    out += vs
    CLUMP_INFO[name] = dict(info, env=(round(P["W"], 2), round(P["D"], 2), round(P["H"], 2)))
    idx = {v: i for i, v in enumerate(vs)}
    P_CORE[name] = (P, [v.co.copy() for v in vs], [[idx[v] for v in f.verts] for f in fs])
    return out


P_CORE = {}


# ---- moss strands (spec 2.5) -------------------------------------------------------------------------------------------
# clump, (x, y), length below the core, sway azimuth
STRANDS = (("L", (-12.7, -3.3), 5.6, 200.0), ("L", (-13.4, 0.8), 4.6, 160.0), ("L", (-8.5, -4.4), 4.0, 250.0),
           ("R", (12.2, 0.6), 5.4, 0.0), ("R", (10.4, -2.2), 4.6, 300.0), ("R", (8.3, 3.3), 3.8, 60.0),
           ("LB", (-11.4, 5.8), 4.2, 150.0), ("LB", (-9.8, 7.1), 3.6, 120.0), ("FR", (5.6, -8.3), 4.4, 300.0),
           ("FR", (3.8, -9.9), 3.8, 270.0), ("FL", (-6.7, -9.55), 4.0, 230.0), ("BR", (7.5, 10.2), 4.0, 60.0))
STRAND_INFO = []


def strand(a, top, L, sway_az, seed):
    """A 3-sided tapered lime drip: a top ring (r 0.55, buried 0.45 in the core underside), a neck (r 0.3), a bulb
    (r 0.46) and a point; the lower half swung 3-6 deg toward sway_az. Toned by length: deep top -> lime bulb."""
    rng = random.Random(seed)
    top = Vector(top)
    sw = _u(sway_az) * math.tan(math.radians(rng.uniform(3, 6)))
    neck = top + Vector((0, 0, -0.62 * L)) + sw * 0.25 * L
    bulb = top + Vector((0, 0, -0.86 * L)) + sw * 0.55 * L
    tipz = top + Vector((0, 0, -L)) + sw * 0.7 * L
    pts = [top, neck, bulb]
    vs, side, caps = tube(a, pts, [0.55, 0.3, 0.46], 3, Vector((1, 0, 0)), rng.uniform(0, 2.0), key=STRAND,
                          cap_key=STRAND_D)
    # replace the end cap by a point: fan the bulb ring to the tip
    bm = a.bm
    endf = caps["cut"][-1]
    ring = list(endf.verts)
    bm.faces.remove(endf)
    tv = bm.verts.new(tipz)
    fan = [bm.faces.new((ring[k], ring[(k + 1) % len(ring)], tv)) for k in range(len(ring))]
    vs = vs + [tv]
    _close(a, vs, _faces(vs), STRAND)
    fs = _faces(vs)
    for f in fs:
        t = (top.z - f.calc_center_median().z) / L
        f.material_index = a._mi(STRAND_D if t < 0.18 else _mix(STRAND_D, STRAND, 0.5) if t < 0.36 else
                                 _mix(STRAND_D, STRAND, 0.75) if t < 0.52 else STRAND)
    _tint(a, fs, 1.0 + rng.uniform(-0.03, 0.03))
    return vs


def strands(a, limb_guard=None):
    """Hang every strand from its clump's underside (top ring buried 0.45 in the lump skin); a strand that would cross
    a limb moves in toward the clump centre (then out), up to 8 tries; dropped if it still crosses."""
    STRAND_INFO.clear()
    out = []
    for i, (cl, xy, L, sway) in enumerate(STRANDS):
        P, cos, polys = P_CORE[cl]
        core = BVHTree.FromPolygons(cos, polys)
        c = Vector((P["c"][0], P["c"][1], 0))
        ok = None
        for k, f in enumerate((0.0, 0.12, -0.08, 0.24, 0.36, -0.16, 0.48, 0.6)):
            p = Vector((xy[0], xy[1], 0))
            p = p + (c - p) * f
            hit = core.ray_cast(Vector((p.x, p.y, P["zc0"] - 5.0)), Z, 20.0)
            if hit[0] is None:
                continue
            top = hit[0] + Z * 0.45
            vs = strand(a, top, L + 0.45, sway, 57500 + i)
            if limb_guard is None or limb_guard.depth(vs) <= 0.0:
                ok = (vs, top, k)
                break
            for v in vs:
                a.bm.verts.remove(v)
        if ok:
            out += ok[0]
            STRAND_INFO.append(dict(clump=cl, top=[round(x, 2) for x in ok[1]], tip_z=round(ok[1].z - L - 0.45, 2),
                                    tries=ok[2]))
        else:
            STRAND_INFO.append(dict(clump=cl, dropped=True))
    return out


# ---- base dressing (spec 2.6) -----------------------------------------------------------------------------------------
ROCKS = {   # centre, (W, D, H), yaw, seed, kind ("slab" tall slate slab, "low", "cave" slate)
    "RK1": ((-11.6, 0.4), (2.4, 2.0, 4.4), 10.0, 57601, "slab"),
    "RK2": ((-8.9, -8.6), (3.6, 2.9, 2.2), 40.0, 57602, "low"),
    "RK3": ((-2.2, -12.4), (3.6, 3.1, 3.0), -10.0, 57603, "low"),
    "RK4": ((9.4, -8.9), (2.5, 2.3, 2.7), 25.0, 57604, "low"),
    "RK5": ((12.9, -0.6), (2.5, 2.2, 1.6), -20.0, 57605, "low"),
    "RK6": ((9.8, 8.2), (2.4, 2.0, 4.0), 50.0, 57606, "slab"),
    "RK7": ((-9.4, 7.9), (2.3, 2.0, 2.0), -30.0, 57607, "low"),
    "CR1": ((0.6, 1.8), (1.6, 1.4, 2.2), 15.0, 57611, "cave"),
    "CR3": ((0.4, -1.6), (1.2, 1.0, 1.4), 40.0, 57613, "cave"),
}
PEBBLES = (((-4.6, -13.0), 1.0, 57621), ((6.0, -11.6), 0.85, 57622), ((3.6, 12.9), 0.8, 57624))
PADS = (   # mid azimuth, radius, length across, depth, seed (fix round 1: larger, for the ground green the sprigs gave)
    (270.0, 10.0, 9.4, 6.0, 57631), (90.0, 9.8, 8.8, 5.8, 57632), (180.0, 12.0, 8.0, 5.8, 57633),
    (0.0, 12.0, 8.0, 5.6, 57634), (222.0, 10.4, 5.8, 4.2, 57635))
PAD_TOP = 0.34
TUFTS = {   # centre, blades, height, spread (fix round 1: 33 blades, was 44)
    "T1": ((-15.2, -2.0), 4, 3.6, 1.5), "T2": ((-4.8, -11.0), 4, 3.0, 1.3), "T3": ((0.6, -8.4), 3, 2.0, 0.9),
    "T4": ((11.8, -6.8), 4, 3.0, 1.4), "T5": ((-0.8, 9.0), 3, 2.2, 0.9), "CT1": ((-0.6, 0.4), 3, 1.6, 0.7),
    "T6": ((-9.6, -9.0), 3, 2.8, 1.2), "T7": ((5.0, -11.6), 3, 2.6, 1.2), "T8": ((9.6, 9.6), 3, 2.6, 1.1),
    "T9": ((-10.5, 8.2), 3, 2.4, 1.0),
}
ROCK_RINGS = ((0.0, 0.92, 5), (0.32, 1.0, 5), (0.72, 0.78, 4), (1.0, 0.36, 2))
SLAB_RINGS = ((0.0, 0.95, 5), (0.35, 1.0, 5), (0.78, 0.86, 4), (1.0, 0.55, 2))
CAVE_RINGS = ((0.0, 0.92, 4), (0.4, 1.0, 4), (0.8, 0.7, 3), (1.0, 0.3, 1))
PEB_RINGS = ((0.0, 0.92, 4), (0.5, 1.0, 3), (1.0, 0.4, 1))
PAD_N = 8
BURY, BURY_PLACE = 0.05, 0.03
BASE_INFO = {}


def _rock(a, c, size, yaw, seed, kind="low", rings=None):
    """A slate rock: the hull of jittered ring stacks (flat base on z 0, widest low, a shoulder, a flat sloping top).
    Tones by height and role: pale lit top, warm grey body, slate foot; tall slabs and cave rocks slate below their
    top 20 %."""
    rng = random.Random(seed)
    W, D, H = size
    rings = rings or (SLAB_RINGS if kind == "slab" else CAVE_RINGS if kind == "cave" else ROCK_RINGS)
    pts = m033._ring_pts(rng, rings, W / 2, D / 2, H, 0.08)
    tilt = rng.uniform(-0.12, 0.12)
    m = Matrix.Rotation(math.radians(yaw), 3, "Z")
    lean = -_away(c) * (0.18 if kind == "slab" else 0.06)
    out = []
    for p in pts:
        q = m @ p
        f = q.z / H
        q += Vector((lean.x * W * 0.5 * f, lean.y * D * 0.5 * f, tilt * q.x * f))
        out.append(q + Vector((c[0], c[1], 0.0)))
    vs = m033._hull(a, out, ROCK)
    z0 = min(v.co.z for v in vs)
    for v in vs:
        v.co.z -= z0
    fs = _faces(vs)
    for f in fs:
        h = f.calc_center_median().z / H
        if kind in ("slab", "cave"):
            key = _mix(ROCK, ROCK_L, 0.5) if h > 0.82 else _mix(ROCK_S, ROCK, 0.25) if h > 0.5 else ROCK_S
        else:
            key = _mix(ROCK, ROCK_L, 0.5) if h > 0.7 else ROCK if h > 0.3 else _mix(ROCK, ROCK_S, 0.5)
        f.material_index = a._mi(key)
    _mottle(a, fs, 0.04, 0.4, seed)
    _tint(a, fs, 1.0 + rng.uniform(-0.03, 0.03))
    return vs


def rock(a, name):
    c, size, yaw, seed, kind = ROCKS[name]
    return _rock(a, c, size, yaw, seed, kind)


def pebble(a, c, s, seed):
    return _rock(a, c, (s, s * 0.85, s * 0.6), random.Random(seed).uniform(0, 180), seed, "low", PEB_RINGS)


def _pad_shell(a, c, ux, uy, Lx, Ly, seed, guard):
    rng = random.Random(seed)
    bm = a.bm
    rim_pts = []
    for k in range(PAD_N):
        ang = 2 * math.pi * k / PAD_N + rng.uniform(-0.08, 0.08)
        rr = (1.0 if k % 2 == 0 else 0.8) * rng.uniform(0.92, 1.05)
        p = c + ux * (math.cos(ang) * Lx / 2 * rr) + uy * (math.sin(ang) * Ly / 2 * rr) + Vector((0, 0, 0.02))
        if guard is not None:
            for _ in range(14):
                if guard.point(p)[0] <= 0.0 and guard.point(p + Vector((0, 0, 0.06)))[0] <= 0.0:
                    break
                p = c + (p - c) * 0.88
                p.z = 0.02
        rim_pts.append(p)
    rim = [bm.verts.new(p) for p in rim_pts]
    top = bm.verts.new(c + Vector((0, 0, PAD_TOP)))
    bot = bm.verts.new(c + Vector((0, 0, 0.0)))
    fs = [bm.faces.new((rim[k], rim[(k + 1) % PAD_N], top)) for k in range(PAD_N)]
    fs += [bm.faces.new((rim[(k + 1) % PAD_N], rim[k], bot)) for k in range(PAD_N)]
    vs = rim + [top, bot]
    _close(a, vs, fs, MOSS)
    return vs, fs, rim, rim_pts, bot


def moss_pad(a, spec, guard=None):
    """A thin lobed lime moss pad (a closed lens: lobed 8-vert rim at z 0.02, top centre 0.13, bottom centre on z 0),
    between two roots; rim verts that would cut a root, the trunk or a rock are pulled in toward the pad centre, and
    a pad that still cuts one moves, then shrinks; one that cannot clear is dropped."""
    az, r, Lx, Ly, seed = spec
    ux, uy = _u(az + 90), _u(az)
    res = None
    c = None
    for dr, sc in ((0.0, 1.0), (0.6, 1.0), (1.2, 0.9), (-0.5, 0.9), (1.8, 0.8), (0.0, 0.7), (2.4, 0.7), (0.6, 0.6),
                   (3.0, 0.6)):
        c = _u(az) * (r + dr)
        res = _pad_shell(a, c, ux, uy, Lx * sc, Ly * sc, seed, guard)
        if guard is None or guard.depth(res[0]) <= BURY_PLACE:
            break
        for v in res[0]:
            a.bm.verts.remove(v)
        res = None
    if res is None:
        BASE_INFO.setdefault("pads_dropped", []).append(az)
        return []
    vs, fs, rim, rim_pts, bot = res
    for k in range(PAD_N):
        if (rim_pts[k] - c).dot(uy) > 0.35 * Ly:
            for f in fs:
                if rim[k] in f.verts and bot not in f.verts:
                    f.material_index = a._mi(_mix(MOSS, GRASS, 0.25))
    _mottle(a, fs, 0.03, 0.2, seed)
    return vs


def blade(a, base, az, pitch, L, W, key, fold=0.28):
    """A closed folded lanceolate grass blade (6 tris): broad near the base, pointed tip; its face turned as close to
    the front / back cameras as its lean allows (never edge-on)."""
    bm = a.bm
    B = Vector(base)
    d = Vector((math.cos(pitch) * math.cos(az), math.cos(pitch) * math.sin(az), math.sin(pitch)))
    side = d.cross(Vector((0, 1, 0)))
    side = side.normalized() if side.length > 0.2 else d.cross(Vector((1, 0, 0))).normalized()
    nrm = side.cross(d).normalized()
    T = bm.verts.new(B + d * L)
    Lp = bm.verts.new(B + d * (0.3 * L) - side * (W / 2) + nrm * (fold * W / 2))
    Rp = bm.verts.new(B + d * (0.3 * L) + side * (W / 2) + nrm * (fold * W / 2))
    Bv = bm.verts.new(B)
    Kv = bm.verts.new(B + d * (0.33 * L) - nrm * (0.05 * L))
    fs = [bm.faces.new((Bv, Lp, T)), bm.faces.new((Bv, T, Rp)), bm.faces.new((Bv, Kv, Lp)),
          bm.faces.new((Lp, Kv, T)), bm.faces.new((T, Kv, Rp)), bm.faces.new((Rp, Kv, Bv))]
    vs = [Bv, Lp, T, Rp, Kv]
    _close(a, vs, fs, key)
    return vs


def tuft(a, name, guard=None):
    """A tall pointed lime tuft: a small 4-sided hub on z 0, blades rising 60-85 deg from it, the taller outer blades
    lime, the inner / lower ones deep green. A blade that cuts a root, the trunk or a rock stands up, turns aside,
    then shortens; one that still cuts after its tries is dropped, never kept."""
    (cx, cy), n, H, R = TUFTS[name]
    rng = random.Random(sum(map(ord, name)) * 7 + 57700)
    bm = a.bm
    if guard is not None and name != "CT1":      # a hub that would sit in a root or rock moves out along its ray
        c0 = Vector((cx, cy, 0.0))
        for k in range(10):
            p = c0 * (1 + 0.06 * k)
            if all(guard.point(p + Vector((dx, dy, 0.17)))[0] <= 0.0 for dx, dy in ((0, 0), (0.6, 0), (-0.6, 0),
                                                                                  (0, 0.6), (0, -0.6))):
                cx, cy = p.x, p.y
                break
    hr, hh = 0.3, 0.34
    yaw0 = rng.uniform(0, 6.28)
    ring = [bm.verts.new(Vector((cx + math.cos(yaw0 + 2 * math.pi * k / 4) * hr,
                                 cy + math.sin(yaw0 + 2 * math.pi * k / 4) * hr, 0.0))) for k in range(4)]
    apex = bm.verts.new(Vector((cx, cy, hh)))
    fs = [bm.faces.new((ring[k], ring[(k + 1) % 4], apex)) for k in range(4)]
    fs.append(bm.faces.new(list(reversed(ring))))
    hub = ring + [apex]
    _close(a, hub, fs, _mix(GRASS_D, BARK_D, 0.25))
    info = BASE_INFO.setdefault(name, {"retried": 0, "dropped": 0})
    if guard is not None:
        info["hub_depth"] = round(guard.depth(hub), 3)
    out = list(hub)
    hs = [H * (rng.uniform(0.86, 1.0) if k % 2 == 0 else rng.uniform(0.55, 0.75)) for k in range(n)]
    for k in range(n):
        yaw = yaw0 + 2 * math.pi * k / n + rng.uniform(-0.25, 0.25)
        tall = hs[k] > 0.8 * H
        pitch = math.radians(rng.uniform(70, 82) if tall else rng.uniform(58, 68))
        L = hs[k] / math.sin(pitch)
        W = L / rng.uniform(3.6, 4.4)
        key = GRASS if tall else _mix(GRASS, GRASS_D, 0.5) if k % 3 else GRASS_D
        up = min(math.radians(86), pitch + math.radians(12))
        tries = [(0.0, pitch, 1.0), (0.0, up, 0.92), (0.4, up, 0.9), (-0.4, up, 0.9), (0.8, up, 0.85),
                 (-0.8, up, 0.85), (0.0, math.radians(86), 0.75)]
        vs = None
        for i, (dy, p_, s_) in enumerate(tries):
            y_ = yaw + dy
            base = (cx + math.cos(y_) * hr * 0.3, cy + math.sin(y_) * hr * 0.3, hh * 0.35)
            vs = blade(a, base, y_, p_, L * s_, W * s_, key)
            if guard is None or guard.depth(vs) <= BURY_PLACE:
                info["retried"] += i > 0
                break
            for v in vs:
                bm.verts.remove(v)
            vs = None
        if vs is None:
            info["dropped"] += 1
            continue
        _tint(a, _faces(vs), 1.0 + rng.uniform(-0.04, 0.04))
        out += vs
    return out


# ---- assemblies -------------------------------------------------------------------------------------------------------
def modules(a, guard=None):
    MOD_INFO.clear()
    LIMB_INFO.clear()
    allv = []
    for name in BM:
        vs = module(a, name)
        allv += vs
        if guard is not None:
            guard.add_vs([v for v in vs if v.is_valid], name)
    vs = sprout_stub(a)
    allv += vs
    if guard is not None:
        guard.add_vs(vs, "sprout")
    return allv


def hero_all(a):
    """The hero: trunk, modules and the sprout stub, the clumps (guarded against the trunk and limbs), the strands
    (guarded against the limbs), then the roots and the base dressing (guarded against the trunk, roots and
    rocks)."""
    BASE_INFO.clear()
    CLUMP_DROPPED.clear()
    tv = trunk(a)
    wood = m047._Solids()
    wood.add_vs(tv, "trunk")
    mv = modules(a, wood)
    for name in CLUMPS:          # fix round 2: lump clusters, each lump guarded against the trunk and limbs
        leaf_clump(a, name, guard=wood)
    # strands must not cross a limb (their tops sit 0.45 inside the lowest lump of their clump)
    sg = m047._Solids()
    for nm, lo, hi, t in wood.items:
        if nm != "trunk":
            sg.items.append((nm, lo, hi, t))
    strands(a, sg)
    guard = m047._Solids()
    guard.add_vs(tv, "trunk")
    for spec in ROOTS:
        vs = root(a, spec)
        guard.add_vs([v for v in vs if v.is_valid], spec[0])
    rk = {}
    for name in ROCKS:
        c0, size, yaw, seed, kind = ROCKS[name]
        vs, moved = None, 0
        c = Vector((c0[0], c0[1], 0.0))
        for k, (dr, dt, sc) in enumerate(((0, 0, 1.0), (0.4, 0, 1.0), (0.8, 0, 1.0), (0.4, 4, 1.0), (0.4, -4, 1.0),
                                          (1.2, 0, 0.92), (0.8, 7, 0.9), (0.8, -7, 0.9), (1.6, 0, 0.85))):
            if kind == "cave" and k:
                break
            r = c.length + dr
            az = math.degrees(math.atan2(c.y, c.x)) + dt
            p = (math.cos(math.radians(az)) * r, math.sin(math.radians(az)) * r)
            vs = _rock(a, p, tuple(x * sc for x in size), yaw, seed, kind)
            if guard.depth(vs) <= BURY:
                moved = k
                break
            if k < 8:
                for v in vs:
                    a.bm.verts.remove(v)
        rk[name] = (round(guard.depth(vs), 3), moved)
        guard.add_vs(vs, name)
    BASE_INFO["rocks_in_wood"] = rk
    for i, (c, s, seed) in enumerate(PEBBLES):
        guard.add_vs(pebble(a, c, s, seed), f"PB{i + 1}")
    for spec in PADS:
        moss_pad(a, spec, guard)
    for name in TUFTS:
        tuft(a, name, guard)


def trunk_part(a):
    trunk(a)
    bosses_part(a)
    MOD_INFO.clear()
    sprout_stub(a)


def branch_part(a):
    MOD_INFO.clear()
    LIMB_INFO.clear()
    module(a, "BM1", part=True)


# the crown part (its own 1000-tri budget): the TL shape (BL in the hero) as a domed lump cluster, W : H about 1.45 like
# the exploded's crown modules, with more, smaller and flatter leaf domes (it is seen close up alone); its tones lean
# less on height and more on position patches (alone, a small dome's height follows its face normals too closely)
PART_CLUMP = dict(W=16.0, D=15.0, zc0=23.0, zt=23.0 + 8.0, tone=-0.1, tilt=0, bump_k=0.6, tone_h=0.38, tone_n=0.34,
                  fill=100, rings=((40.0, 6, 1.0), (88.0, 10, 1.0)))


def crown_part(a):
    """The TL crown module shape (BL in the hero) with its stub (bored base): a denser lump cluster than the hero's
    clumps (the part has its own 1000-tri budget)."""
    MOD_INFO.clear()
    LIMB_INFO.clear()
    for name in BM:
        _mod_info_only(name)
    P = clump_params("BL", **PART_CLUMP)
    leaf_clump(a, "BL", stub=True, pre=P)


def _feed_info(apts, feed):
    """A feeding arm's joint: J where its last segment enters the clump (60 % along it), the tip inside the core."""
    p1, tip = apts[-2], apts[-1]
    return dict(J=p1 + (tip - p1) * 0.6, tip=tip.copy(), d=(tip - p1).normalized(), clump=feed,
                pts=[p.copy() for p in apts])


def _mod_info_only(name):
    B = BM[name]
    info = MOD_INFO.setdefault(name, {})
    for arm, (apts, adia, an, feed) in B["arms"].items():
        if feed:
            info[arm] = _feed_info([Vector(p) for p in apts], feed)


def root_part(kind):
    spec = {"A": ROOTS[3], "B": ROOTS[4], "C": ROOTS[6]}[kind]

    def fn(a):
        root(a, spec, part=True)
    return fn


# ---- objects ----------------------------------------------------------------------------------------------------------
NOTES = {
    HERO: "Ancient Tree: the kit's giant (32 tall). A twisted eight-strand orange-brown bell trunk, hollow at its foot "
          "(front slit, pointed back arch, slate rocks and a tuft in the dark cavity), eight high buttress roots with "
          "split toes, two side branch modules with bare forks and two Y modules on a pale cut top feeding seven "
          "lobed leaf clusters of rounded sub-domes (lime tops, green bodies, dark undersides) round an open hub, a trunk "
          "sprout clump, twelve lime moss strands with bulb tips; slate rocks with pale tops, lime moss pads and tall "
          "lime tufts at the foot. No VFX",
    TRUNK_P: "Trunk Core: the hollow-footed twisted eight-strand bell with its slit and arch, a pale cut top with two "
             "sockets and dark radial cracks, two side bosses with sockets and the sprout stub",
    BRANCH_P: "Branch Module: BM1, the left side module - a bored 8-sided base with a pale peg, the main arm, a spur "
              "arm and a bare two-tine fork",
    CROWN_P: "Crown Module: one leaf clump (the TL shape) with its bored stub: a domed cluster of rounded leaf lumps",
    ROOT_PA: "Root Module A: a high buttress root with a hollow joining end and peg, a long low run and two toes",
    ROOT_PB: "Root Module B: a longer, steeper buttress root with a hollow joining end and peg and three toes",
    ROOT_PC: "Root Module C: a short steep buttress root with a hollow joining end and peg and two toes",
}
COLLISION = {HERO: "precise", TRUNK_P: "precise", BRANCH_P: "hull", CROWN_P: "hull", ROOT_PA: "hull",
             ROOT_PB: "hull", ROOT_PC: "hull"}


def _new(name, fn, role, budget, temp=False):
    old = bpy.data.objects.get(name)
    if old:
        if old.get("kit_sheet") not in (None, SHEET) and not temp:
            raise RuntimeError(f"{name} belongs to {old.get('kit_sheet')}")
        for c in list(old.children_recursive):
            bpy.data.objects.remove(c, do_unlink=True)
        me = old.data
        bpy.data.objects.remove(old, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    a = K.fk().Asset(name, f"{SHEET} {TITLE}", seed=7, tint_var=0.0)
    fn(a)
    o = a.finish(collection=M.coll(NUM, TITLE), mark_asset=not temp, origin=None)
    K.drop_unused_slots(o)
    if "kit_part" in o.data.attributes:
        o.data.attributes.remove(o.data.attributes["kit_part"])
    if not temp:
        K.tag(o, SHEET, TITLE, role, COLLISION[name], budget, NOTES[name])
    o[OFF] = [0.0, 0.0, 0.0]
    o.location = (0, 0, 0)
    bpy.context.view_layer.update()
    return o


def _recentre(o):
    bc = m012._bottom_centre(o)
    if bc.length > 1e-6:
        for v in o.data.vertices:
            v.co -= bc
        o[OFF] = list(Vector(o[OFF]) + bc)
    o.data.update()


def _post(o, uv=True):
    """Stage 2-3 pass for an object of closed shells: triangles, outward normals per shell, flat shading, origin at
    the bbox bottom centre, UVs (angle-based islands, overlaps cut free), bowties split."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    for p in o.data.polygons:
        p.use_smooth = False
    if o.data.has_custom_normals:
        with M._override(o):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
    _recentre(o)
    lg = {"bowties": M.fix_bowties(o)}
    if uv:
        M.smart_uv(o, **UV)
        lg["uv_cut"] = m012._uv_unfold(o)
    K.drop_unused_slots(o)
    return lg


def _make(name, fn, role="part", budget=1000, temp=False, uv=True):
    o = _new(name, fn, role, budget, temp=temp)
    return o, _post(o, uv=uv)


# ---- checks -----------------------------------------------------------------------------------------------------------
def _keys(o):
    return [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]


def _kind(ks, nf):
    if any("strand" in k for k in ks):
        return "strand"
    if any("leaf" in k for k in ks):
        return "lump"
    if any("grass" in k for k in ks) and not any("moss" in k for k in ks):
        return "hub" if any("bark" in k for k in ks) else "blade"
    if any("rock" in k for k in ks):
        return "rock"
    if any(("bark" in k) or ("hollow" in k) or ("cavity" in k) for k in ks):
        return "wood"
    if any("moss" in k for k in ks):
        return "pad"
    return "other"


def _shells(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    ids, n = M._shell_ids(bm)
    keys = _keys(o)
    groups = [[] for _ in range(n)]
    for f in bm.faces:
        groups[ids[f.index]].append(f)
    kinds = []
    for fs in groups:
        ks = {keys[f.material_index] for f in fs}
        kinds.append(_kind(ks, len(fs)))
    wood = [k for k in range(n) if kinds[k] == "wood"]
    if wood:
        big = max(wood, key=lambda k: len(groups[k]))
        z0 = min(v.co.z for v in bm.verts)
        for k in wood:
            nf = len(groups[k])
            zmin = min(v.co.z for f in groups[k] for v in f.verts)
            if k == big and nf > 250:
                kinds[k] = "trunk"
            elif zmin - z0 < 0.1:
                kinds[k] = "root" if nf > 24 else "toe"
            else:
                kinds[k] = "limb" if nf > 14 else "twig"
            if o.name == CROWN_P:            # the crown part's stub is the module's limb end, not a root on the ground
                kinds[k] = "limb"
    return bm, ids, n, groups, kinds


def shells_report(o):
    """Per shell: kind, tris, non-manifold edges / verts, boundary edges, winding errors (manifold edges whose two
    faces don't run the same way round), self-intersections, signed volume."""
    bm, ids, n, groups, kinds = _shells(o)
    out = []
    for k in range(n):
        fs = groups[k]
        es = {e for f in fs for e in f.edges}
        vs = list({v for f in fs for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        tree = BVHTree.FromPolygons([v.co for v in vs], [[vi[v] for v in f.verts] for f in fs])
        hits = sum(1 for a_, b_ in tree.overlap(tree) if a_ < b_ and not set(fs[a_].verts) & set(fs[b_].verts))
        vol = sum(f.calc_center_median().dot(f.normal) * f.calc_area() for f in fs) / 3.0
        out.append({"kind": kinds[k], "tris": len(fs), "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary),
                    "winding_errors": sum(1 for e in es if e.is_manifold and not e.is_contiguous),
                    "self_hits": hits, "volume": round(vol, 4)})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating dressing: per shell, whether it touches another shell (triangles intersect, or a vertex within
    tol of another shell's surface) or the ground, and whether it chains by contact to an anchor (ground shells in
    the hero / root parts; the largest shell in the other parts)."""
    bm, ids, n, groups, kinds = _shells(o)
    fsh = [ids[f.index] for f in bm.faces]
    vsh = {}
    for f in bm.faces:
        for v in f.verts:
            vsh[v.index] = fsh[f.index]
    tree = BVHTree.FromBMesh(bm)
    zmin = [1e9] * n
    for v in bm.verts:
        if v.index in vsh:
            zmin[vsh[v.index]] = min(zmin[vsh[v.index]], v.co.z)
    z0 = min(zmin)
    near = {}
    for i, j in tree.overlap(tree):
        a_, b_ = fsh[i], fsh[j]
        if a_ != b_:
            near[(min(a_, b_), max(a_, b_))] = 0.0
    for v in bm.verts:
        s = vsh.get(v.index)
        if s is None:
            continue
        for loc, _, fi, d in tree.find_nearest_range(v.co, chain_tol):
            t = fsh[fi]
            if t != s:
                kk = (min(s, t), max(s, t))
                near[kk] = min(near.get(kk, 1e9), d)
    gap = [1e9] * n
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    if any(kinds[k] in ("rock", "hub", "trunk") for k in range(n)) or o.name in (ROOT_PA, ROOT_PB, ROOT_PC):
        ground = {k for k in range(n) if zmin[k] - z0 <= 0.12 and kinds[k] in ("trunk", "root", "toe", "rock", "pad",
                                                                                  "hub", "sprig")}
    else:
        ground = {max(range(n), key=lambda k: len(groups[k]))}
    for k in ground:
        gap[k] = 0.0

    def chained(t):
        adj = {k: set() for k in range(n)}
        for (a_, b_), d in near.items():
            if d <= t:
                adj[a_].add(b_)
                adj[b_].add(a_)
        seen = set(ground)
        stack = list(seen)
        while stack:
            k = stack.pop()
            for m_ in adj[k]:
                if m_ not in seen:
                    seen.add(m_)
                    stack.append(m_)
        return n - len(seen)
    floating = [k for k in range(n) if gap[k] > tol]
    res = {"shells": n, "floating": len(floating), "floating_kinds": sorted({kinds[k] for k in floating}),
           "worst_gap": round(max([gap[k] for k in floating], default=0.0), 3),
           "unchained": chained(tol), "kinds": {k: kinds.count(k) for k in sorted(set(kinds))}}
    bm.free()
    return res


def bury_report(o):
    """No buried dressing (STAGES): every tuft blade / hub, moss pad, leaf lump (clump skin) and strand tested by ray
    parity against the trunk, every root and toe and every rock shell (depth = distance from the deepest vert or face
    centre inside to that shell's surface); each rock against the trunk and roots; lump verts also against the limbs
    (the arms end inside their clumps by design, so only verts count) and against the other lumps (none wholly
    inside another)."""
    bm, ids, n, groups, kinds = _shells(o)
    sol = m047._Solids()
    limbs = m047._Solids()
    rocks = []
    for k in range(n):
        vs = list({v for f in groups[k] for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        if kinds[k] in ("trunk", "root", "toe", "rock"):
            sol.add([v.co for v in vs], [[vi[v] for v in f.verts] for f in groups[k]], f"{kinds[k]}{k}")
            if kinds[k] == "rock":
                rocks.append(k)
        elif kinds[k] in ("limb", "twig"):
            limbs.add([v.co for v in vs], [[vi[v] for v in f.verts] for f in groups[k]], f"{kinds[k]}{k}")
    off = Vector(o[OFF]) if OFF in o else Vector()
    res = []
    tested = 0
    for k in range(n):
        if kinds[k] not in ("blade", "hub", "pad", "lump", "strand"):
            continue
        tested += 1
        fs = groups[k]
        pts = list({v.co.copy().freeze() for f in fs for v in f.verts}) + [f.calc_center_median() for f in fs]
        d, who = max((sol.point(Vector(p)) for p in pts), key=lambda r: r[0])
        if d > 0.0:
            c = sum((f.calc_center_median() for f in fs), Vector()) / len(fs) + off
            res.append((round(d, 3), kinds[k], who, [round(x, 2) for x in c]))
    rk = []
    for k in rocks:
        fs = groups[k]
        pts = list({v.co.copy().freeze() for f in fs for v in f.verts}) + [f.calc_center_median() for f in fs]
        d = max(sol.point(Vector(p), skip=[f"rock{j}" for j in rocks])[0] for p in pts)
        if d > 0.0:
            c = sum((f.calc_center_median() for f in fs), Vector()) / len(fs) + off
            rk.append((round(d, 3), [round(x, 2) for x in c]))
    # fix round 2: every leaf lump against the limbs (no lump more than BURY inside one) and against the other lumps
    # (none wholly inside another: at least one vert of each lump outside every other lump)
    lumps = [k for k in range(n) if kinds[k] == "lump"]
    lsol = m047._Solids()
    lvs = {}
    for k in lumps:
        vs = list({v for f in groups[k] for v in f.verts})
        vi = {v: i for i, v in enumerate(vs)}
        lvs[k] = vs
        lsol.add([v.co for v in vs], [[vi[v] for v in f.verts] for f in groups[k]], f"lump{k}")
    hidden, in_limb = [], []
    for k in lumps:
        vs = lvs[k]
        if all(lsol.point(v.co, skip=[f"lump{k}"])[0] > 0.0 for v in vs):
            cen = sum((v.co for v in vs), Vector()) / len(vs)
            hidden.append([round(x, 2) for x in cen + off])
        dl = max(limbs.point(v.co)[0] for v in vs)
        if dl > BURY:
            cen = sum((v.co for v in vs), Vector()) / len(vs)
            in_limb.append((round(dl, 3), [round(x, 2) for x in cen + off]))
    bm.free()
    res.sort(key=lambda r: -r[0])
    rk.sort(key=lambda r: -r[0])
    return {"tested": tested, "solids": len(sol.items), "over_0.05": sum(1 for r in res if r[0] > BURY),
            "max": res[0][0] if res else 0.0, "worst": res[:6],
            "rocks_over_0.05": sum(1 for r in rk if r[0] > BURY), "rocks": rk[:6],
            "lumps": len(lumps), "lumps_hidden": len(hidden), "lumps_hidden_at": hidden[:6],
            "lumps_in_limbs": len(in_limb), "lumps_in_limbs_worst": sorted(in_limb, key=lambda r: -r[0])[:4]}


def winding_total(shells):
    return sum(s["winding_errors"] for s in shells)


LIMB_VIEWS = {"front": (0, 5), "rear": (180, 5), "f34": (0, 13), "r34": (180, 13)}


def _cam(az, el):
    a_, e_ = math.radians(az), math.radians(el)
    return Vector((math.sin(a_) * math.cos(e_), -math.cos(a_) * math.cos(e_), math.sin(e_)))


def limb_visibility(h, views=LIMB_VIEWS, step=0.1):
    """Per module and view: the bare limb length seen (centreline samples whose ray to the camera clears every
    non-wood shell and the trunk), in studs along the limb; per polyline (main run, arms, tines, spurs)."""
    bm, ids, n, groups, kinds = _shells(h)
    off = Vector(h[OFF])
    keep = [f for k in range(n) if kinds[k] not in ("limb", "twig") for f in groups[k]]
    vs = list({v for f in keep for v in f.verts})
    vi = {v: i for i, v in enumerate(vs)}
    tree = BVHTree.FromPolygons([v.co + off for v in vs], [[vi[v] for v in f.verts] for f in keep])
    bm.free()
    out = {}
    for name, lines in LIMB_INFO.items():
        row = {}
        for vn, (az, el) in views.items():
            d = _cam(az, el)
            per = []
            for pts in lines:
                vis = 0.0
                for p, q in zip(pts, pts[1:]):
                    seg = Vector(q) - Vector(p)
                    m = max(1, int(seg.length / step))
                    for i in range(m):
                        c = Vector(p) + seg * ((i + 0.5) / m)
                        if tree.ray_cast(c, d, 200.0)[0] is None:
                            vis += seg.length / m
                per.append(round(vis, 2))
            row[vn] = per
        out[name] = row
    return out


# ---- build ------------------------------------------------------------------------------------------------------------
TARGET_SIZE = ((32.4, 1.4), (30.0, 2.0), (32.0, 0.6))        # W (X), D (Y), H with tolerances
HERO_CEILING = 3950            # main-session ruling, fix round 1 (limit 4000)


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m057_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", "Monarch"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build_hero():
    M.coll(NUM, TITLE)
    palette()
    CLUMP_INFO.clear()
    t0 = time.time()
    h, lg = _make(HERO, hero_all, "hero", 4000)
    lg["secs"] = round(time.time() - t0, 1)
    return h, lg


def _rebuild_info():
    """The hero's MOD_INFO / LIMB_INFO (the parts overwrite them): rebuilt without keeping geometry."""
    a = K.fk().Asset(PFX + "info", "probe", seed=1, tint_var=0.0)
    modules(a)
    a.bm.free()


def build(render=True, parts=True, close=True):
    t0 = time.time()
    h, lh = build_hero()
    log = {"hero": lh}
    objs = {}
    if parts:
        objs[TRUNK_P], log[TRUNK_P] = _make(TRUNK_P, trunk_part)
        objs[BRANCH_P], log[BRANCH_P] = _make(BRANCH_P, branch_part)
        objs[CROWN_P], log[CROWN_P] = _make(CROWN_P, crown_part)
        for kind, nm in (("A", ROOT_PA), ("B", ROOT_PB), ("C", ROOT_PC)):
            objs[nm], log[nm] = _make(nm, root_part(kind))
        _rebuild_info()
    _cleanup_tmp()
    order = [h] + [objs[n] for n in PARTS if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    out = report(order)
    out["log"] = log
    out["build_s"] = round(time.time() - t0, 1)
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


def report(order):
    h = order[0]
    audits = [M.audit(o) for o in order]
    thin = {o.name: m012._thin(o, 2.0) for o in order}
    shells = {o.name: shells_report(o) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = HERO_CEILING if o is h else 1000
        if au["tris"] > lim:
            problems.append(f"{o.name}: {au['tris']} tris over {lim}")
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "wire_edges", "loose_verts",
                  "zero_area_faces", "ngons"):
            if au[k]:
                problems.append(f"{o.name}: {k} {au[k]}")
        if au["normals"] != "outward":
            problems.append(f"{o.name}: normals {au['normals']}")
        if any(abs(x) > 1e-3 for x in au["origin_offset"]):
            problems.append(f"{o.name}: origin offset {au['origin_offset']}")
        for i, s in enumerate(shells[o.name]):
            for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "winding_errors", "self_hits"):
                if s[k]:
                    problems.append(f"{o.name} shell {i} ({s['kind']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['kind']}): not closed outward (volume {s['volume']})")
    contact = {o.name: contact_report(o) for o in order}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} floating shells ({c['floating_kinds']}), {c['unchained']} unchained")
    bury = {o.name: bury_report(o) for o in order if o.name in (HERO, CROWN_P)}
    for n_, b in bury.items():
        if b["over_0.05"]:
            problems.append(f"{n_}: {b['over_0.05']} dressing shells more than {BURY} inside wood / rock "
                            f"(worst {b['worst'][:3]})")
        if b["rocks_over_0.05"]:
            problems.append(f"{n_}: {b['rocks_over_0.05']} rocks more than {BURY} into the trunk / roots")
        if b["lumps_hidden"]:
            problems.append(f"{n_}: {b['lumps_hidden']} lumps wholly inside other lumps ({b['lumps_hidden_at'][:3]})")
        if b["lumps_in_limbs"]:
            problems.append(f"{n_}: {b['lumps_in_limbs']} lumps more than {BURY} inside limbs "
                            f"({b['lumps_in_limbs_worst'][:2]})")
    if sum(1 for s in shells[h.name] if s["kind"] == "trunk") != 1:
        problems.append(f"{HERO}: trunk shells != 1")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 14: none)")
    if any(s.get("dropped") for s in STRAND_INFO):
        problems.append(f"{HERO}: strands dropped {[s for s in STRAND_INFO if s.get('dropped')]}")
    if CLUMP_DROPPED:
        problems.append(f"{HERO}: lumps dropped {CLUMP_DROPPED}")
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    vis = limb_visibility(h)
    kinds = {}
    for s in shells[h.name]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    return {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                          "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                          "ngons", "dup_verts", "origin_offset", "transforms_applied")}
                      for au in audits],
            "hero_shells": kinds, "winding": {o: winding_total(s) for o, s in shells.items()},
            "contact": contact, "bury": bury, "base_info": dict(BASE_INFO), "clumps": dict(CLUMP_INFO),
            "strands": list(STRAND_INFO), "limb_visibility": vis, "thin": thin, "problems": problems, "uv": uv,
            "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
            "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
            "baked_shading": {o.name: o.get("kit_baked_shading") for o in order}}


# ---- renders ----------------------------------------------------------------------------------------------------------
SHEET_VIEWS = {"f34_sheet": (0, 13), "r34_sheet": (180, 13), "front_sheet": (0, 5), "side_sheet": (90, 5),
               "rear_sheet": (180, 5), "top_sheet": (0, 89)}
VIEW_NAMES = ("front", "side", "rear", "top", "underside")
PARTS_SHOT = (-20, 22)
MARKERS = ((0.4, 5.6, 0.0), (-12.6, -4.6, 0.0))       # in the back arch, under the L clump and its strands


def _marker(h, at, name):
    a = K.fk().Asset(PFX + name, "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=ROCK_S, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=ROCK_S, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=ROCK_S, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
    c.location = off @ Vector(at)
    bpy.context.view_layer.update()
    return c


def _at(o, p):
    return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)


def _temp(name, fn):
    return _new(PFX + name, fn, "part", 1000, temp=True)


def _exploded(objs):
    """The parts laid out like the sheet's Exploded Construction: the trunk core in the middle, the four branch modules
    drawn out round its top and sides, crown modules above them, the three root modules below (temporary pieces)."""
    h = objs[0]
    x0, y0 = h.location.x + 90, h.location.y
    by = {o.name: o for o in objs}
    shown = []
    o0 = Matrix.Translation((x0, y0, 0))
    t = by.get(TRUNK_P)
    if t is not None:
        c = bpy.data.objects.new(PFX + "expl_trunk", t.data)
        h.users_collection[0].objects.link(c)
        c.matrix_world = o0 @ Matrix.Translation(Vector(t[OFF]) + Vector((0, 0, 4.0)))
        shown.append(c)
    outs = {"BM1": Vector((-6.0, 0, 3.5)), "BM2": Vector((6.0, 0, 3.5)), "BM3": Vector((-3.0, 0, 9.0)),
            "BM4": Vector((3.0, 0, 9.0))}
    for nm in BM:
        o = _temp("mod_" + nm, lambda a, nm=nm: module(a, nm, part=True))
        o.matrix_world = o0 @ Matrix.Translation(Vector(o[OFF]) + outs[nm])
        shown.append(o)
    MOD_INFO.clear()
    for nm in BM:
        _mod_info_only(nm)
    cl = {"L": Vector((-8, 0, 7)), "R": Vector((8, 0, 7)), "BL": Vector((-4, 0, 11)), "BR": Vector((4, 0, 11)),
          "FR": Vector((6, -6, 10))}
    for nm, dv in cl.items():
        o = _temp("clump_" + nm, lambda a, nm=nm: leaf_clump(a, nm, stub=True))
        o.matrix_world = o0 @ Matrix.Translation(Vector(o[OFF]) + dv)
        shown.append(o)
    for i, (nm, dv) in enumerate(((ROOT_PA, Vector((-9, -6, 0))), (ROOT_PB, Vector((9, -6, 0))),
                                  (ROOT_PC, Vector((0, -12, 0))))):
        r = by.get(nm)
        if r is None:
            continue
        c = bpy.data.objects.new(PFX + f"expl_root{i}", r.data)
        h.users_collection[0].objects.link(c)
        c.matrix_world = o0 @ Matrix.Translation(Vector(r[OFF]) + dv)
        shown.append(c)
    _rebuild_info()
    bpy.context.view_layer.update()
    return shown


def render_views(objs, close=True):
    h = objs[0]
    shown = _exploded(objs) if len(objs) > 1 else []
    marks = [_marker(h, p, f"char{i}") for i, p in enumerate(MARKERS)]
    shade = bpy.data.objects.get("ShadeTree")
    twin = None
    if shade is not None:            # 054's 20-stud ShadeTree beside the hero for scale (a temporary linked copy)
        twin = bpy.data.objects.new(PFX + "shade_twin", shade.data)
        h.users_collection[0].objects.link(twin)
        twin.location = h.location + Vector((30.0, 4.0, 0.0))
        bpy.context.view_layer.update()
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        extra["front34"] = ([h], -28, 12)
        extra["rear34"] = ([h], 152, 12)
        for o in objs[1:]:
            extra["part_" + o.name.replace("MonarchTree", "").lower()] = ([o], *PARTS_SHOT)
        if shown:
            extra["exploded"] = (shown, 0, 14)
        extra["scale"] = ([h] + marks + ([twin] if twin else []), -20, 6)
        extra["scale_rear"] = ([h] + marks, 180, 6)
        kit = K.NS["KIT"]
        orig, kit["render_group"] = m033._long_lens(kit)
        try:
            sheet = M.views(NUM, [h], names=VIEW_NAMES, extra=extra, vfx=True)
        finally:
            kit["render_group"] = orig
        out = {"sheet": sheet}
        if close:
            out.update(render_close_ups(objs))
        return out
    finally:
        for o in shown + marks + ([twin] if twin else []):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def _cut_trunk(a):
    trunk(a, cut=2)


def render_close_ups(objs):
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    by = {o.name: o for o in objs}
    h = objs[0]
    out = {}
    rc = m033.render_close
    out["arch_cu"] = rc([h], f"{d}/arch_cu.png", 180, 6, _at(h, (0.0, 6.0, 5.0)), 5.6)
    out["slit_cu"] = rc([h], f"{d}/slit_cu.png", 8, 6, _at(h, (1.0, -6.4, 5.5)), 5.0)
    out["fork_cu"] = rc([h], f"{d}/fork_cu.png", -10, -8, _at(h, (-9.8, -1.8, 16.6)), 3.4)
    out["fork_r_cu"] = rc([h], f"{d}/fork_r_cu.png", 15, -8, _at(h, (10.4, 0.6, 18.2)), 3.4)
    out["junction_cu"] = rc([h], f"{d}/junction_cu.png", -25, 30, _at(h, (0.0, 0.0, 20.5)), 5.0)
    out["clump_cu"] = rc([h], f"{d}/clump_cu.png", 20, 4, _at(h, (-10.4, -3.0, 18.0)), 6.4)
    out["strand_cu"] = rc([h], f"{d}/strand_cu.png", -10, 2, _at(h, (-13.0, -3.6, 14.6)), 3.0)
    rt = ROOT_INFO.get("RT6")
    if rt:
        p = rt["stations"][2][0]
        out["root_cu"] = rc([h], f"{d}/root_cu.png", -35, 16, _at(h, (p.x, p.y, 3.0)), 5.0)
    cut = _temp("trunkcut", _cut_trunk)
    try:
        cut.location = h.location + Vector((0, -60, 0))
        bpy.context.view_layer.update()
        out["hollow_cu"] = rc([cut], f"{d}/hollow_cu.png", -20, 38, cut.matrix_world @ Vector((0, 0, 2.0)), 4.6)
    finally:
        me = cut.data
        bpy.data.objects.remove(cut, do_unlink=True)
        bpy.data.meshes.remove(me)
    if TRUNK_P in by:
        t = by[TRUNK_P]
        out["junction_part"] = rc([t], f"{d}/junction_part.png", -25, 35, _at(t, (0.0, 0.0, 19.0)), 4.6)
    if ROOT_PA in by:
        r = by[ROOT_PA]
        st = ROOT_INFO.get("RT4")
        p0 = st["stations"][0][0] if st else Vector()
        out["root_end_cu"] = rc([r], f"{d}/root_end_cu.png", 70, 14, _at(r, (p0.x, p0.y, 8.0)), 3.6)
    return out


def preview(names=("f34_sheet", "front_sheet", "rear_sheet", "side_sheet", "top_sheet", "r34_sheet"), vfx=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig


def hero_only():
    h, lg = build_hero()
    _cleanup_tmp()
    others = [bpy.data.objects[n] for n in PARTS if n in bpy.data.objects]
    M.display(NUM, [h] + others, TITLE)
    au = M.audit(h)
    sh = shells_report(h)
    return {"audit": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "normals", "origin_offset")}, "log": lg,
            "winding": winding_total(sh),
            "bad_shells": [(i, s) for i, s in enumerate(sh) if s["winding_errors"] or s["nonmanifold_edges"] or
                           s["boundary_edges"] or s["volume"] <= 0][:8],
            "kinds": {k: [sum(1 for s in sh if s["kind"] == k), sum(s["tris"] for s in sh if s["kind"] == k)]
                      for k in sorted({s["kind"] for s in sh})},
            "clumps": dict(CLUMP_INFO), "strands": list(STRAND_INFO), "dropped": list(CLUMP_DROPPED),
            "base": dict(BASE_INFO)}
