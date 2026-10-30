"""053 Dead Tree (references/053.png): a bare, dead, chunky tree on a massive twisted orange-brown trunk of six rope
strands, flaring into six thick roots with split blunt toes, throwing out six plug-in branch modules at mid height.
Every limb is a chain of straight faceted prisms with hard mitred kinks, forking into short blunt square-cut tines;
dark bore pits pit the trunk, limbs and roots; an oval knot hole with a pale raised rim and a boss sits on the
front-right of the trunk; the left major limb ends in a snapped pale break. Round the foot: pale warm-grey angular
rocks (two tall ones behind), lime moss pads and pointed lime grass tufts. No leaves, no glow.

    import importlib, kit_models, m053; importlib.reload(kit_models); importlib.reload(m053); m053.build()

Build frame: studs, front -Y, +X right, ground z 0, trunk axis at (0, 0), upright. Every object ends with its origin at
its bbox bottom centre; o["m053_offset"] is that origin in the build frame. W05 owns every DeadTree* name, so the names
are TwistedSnag* (spec 8):
- TwistedSnagTrunkCore: the twisted six-strand body (18 facets, square top socket, knot, underside pin), five socket
  collars, five root stubs and the built-in front root RT3 with its toes, exact-unioned in one at a time at the world
  origin: one closed shell.
- TwistedSnagBranchA / B / C: branch modules A (left major, the big Y with the snapped end), B (the kinked up-left
  limb), C (the comb, low left). Each a main ring-stack chain with its peg, side branches and tines as closed shells
  buried in the parent. The leader (top module), the riser (R) and the Y-fork (FR) are built the same way (hero only).
- TwistedSnagRootA / B / C: root modules (3 / 2 / 3 toes), each a six-sided chain from its peg to a fork with toes.
- TwistedSnag (hero): the core, six branch modules, five root modules and the base dressing (rocks, pebbles, moss
  pads, tufts) in one object of closed shells.
Colour (stage 4) is painted by position and role inside the builders (never by facing). Stages 5-6: none (the sheet
shows no glow, light or effect). See M053_spec.md.
"""
import math
import random
import time

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import kit_mcp as K
import kit_models as M
import m012
import m033
import m047

NUM, TITLE, SHEET = 53, "Dead Tree", "M053"
OFF = "m053_offset"
PFX = "_m053_"
HERO = "TwistedSnag"
CORE_P = "TwistedSnagTrunkCore"
BRA_P, BRB_P, BRC_P = "TwistedSnagBranchA", "TwistedSnagBranchB", "TwistedSnagBranchC"
RTA_P, RTB_P, RTC_P = "TwistedSnagRootA", "TwistedSnagRootB", "TwistedSnagRootC"

WOOD, WOOD_DARK, WOOD_LIGHT, HOLLOW = "m053_wood", "m053_wood_dark", "m053_wood_light", "m053_hollow"
ROCK, ROCK_LIGHT, ROCK_DEEP = "m053_rock", "m053_rock_light", "m053_rock_deep"
MOSS, GRASS, GRASS_DEEP = "m053_moss", "m053_grass", "m053_grass_deep"

UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008, min_angle=45.0)
CONTACT = 0.03
BURY = 0.05
BURY_PLACE = 0.03

# key -> (hex, roughness, low specular). Stage 4 (M053_spec.md "Stage 4") writes the calibrated values here.
PALETTE = {
    WOOD: ("#985B2D", 0.9, False),
    WOOD_DARK: ("#6A4427", 0.95, False),
    WOOD_LIGHT: ("#C69B60", 0.85, False),
    HOLLOW: ("#1E0E06", 1.0, False),
    ROCK: ("#9B9894", 0.85, False),
    ROCK_LIGHT: ("#A39E9A", 0.85, False),
    ROCK_DEEP: ("#7C7974", 0.9, False),
    MOSS: ("#9E9610", 0.95, True),
    GRASS: ("#8F9E10", 0.85, True),
    GRASS_DEEP: ("#40530C", 0.85, True),
}
# calibration targets (spec 5.4: rendered sRGB of the sheet's regions), K.sample kinds
TARGETS = {WOOD: ((0xB2, 0x66, 0x34), "brown"), WOOD_DARK: ((0x86, 0x53, 0x31), "brown"),
           WOOD_LIGHT: ((0xF6, 0xBE, 0x70), "brown"), HOLLOW: ((0x2A, 0x16, 0x0A), "all"),
           ROCK: ((0xC6, 0xBC, 0xAE), "all"), ROCK_LIGHT: ((0xD0, 0xC4, 0xB6), "all"),
           ROCK_DEEP: ((0x9B, 0x93, 0x90), "all"), MOSS: ((0xC8, 0xB8, 0x10), "vivid"),
           GRASS: ((0xBE, 0xC2, 0x0D), "vivid"), GRASS_DEEP: ((0x4B, 0x5F, 0x0E), "vivid")}


def palette():
    for k, (hexcol, rough, low) in PALETTE.items():
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
        K.fk().material(k)
        K.set_colour(k, hexcol, rough=rough, low_spec=low)
    for m in list(bpy.data.materials):
        key = m.name[3:] if m.name.startswith("FB_m053_") else None
        if key and "_x_" in key:
            k1, rest = key.split("_x_", 1)
            tail, pct = rest.rsplit("_", 1)
            k2 = next((k for k in PALETTE if k == "m053_" + tail), None) or \
                next((k for k in PALETTE if k.startswith(k1) and k.endswith("_" + tail)), None)
            if k1 in PALETTE and k2 and pct.isdigit():
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


# ---- small helpers -----------------------------------------------------------------------------------------------------
_faces = m033._faces
_mottle = m033._mottle
_zip = m047._zip
_band = m047._band
_basis = m047._basis
_surface_t = m047._surface_t


def _mix(k1, k2, t):
    t = round(max(0.0, min(1.0, t)) * 20) / 20
    return K.mix_key(k1, k2, t)


def _paint(a, faces, key):
    mi = a._mi(key)
    for f in faces:
        if f.is_valid:
            f.material_index = mi


def _tint(a, faces, k):
    for f in faces:
        if not f.is_valid:
            continue
        for l in f.loops:
            t = l[a.tint_layer][0] * k
            l[a.tint_layer] = (t, t, t, 1.0)


def _u(az):
    r = math.radians(az)
    return Vector((math.cos(r), math.sin(r), 0.0))


def _dir(az, rise):
    """Unit axis toward plan azimuth `az`, `rise` degrees above horizontal."""
    a, e = math.radians(az), math.radians(rise)
    return Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))


def _close(a, vs, key):
    vs = [v for v in vs if v.is_valid]
    fs = _faces(vs)
    bmesh.ops.recalc_face_normals(a.bm, faces=fs)
    a._finish(vs, key, tint=1.0)
    return fs


def _vs(faces):
    return list({v for f in faces if f.is_valid for v in f.verts})


def _square(c, u, v, h):
    """Four corners of a square of half-side h round c in the plane (u, v), counter-clockwise from (+, +)."""
    return [c + (u * sx + v * sy) * h for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1))]


# ---- chains (limbs, tines, collars, pegs): straight prisms with hard mitred kinks (spec 4.1) ---------------------------
def chain(a, pts, radii, n, u0=None, rot=0.0, section=None):
    """Rings of n verts at each point of a polyline, each ring in the mitre plane of its kink (the bisector of the two
    segments), so a kink stays hard and never pinches; frames parallel-transported from u0. section: n (x, y) offsets
    in units of the radius (default a regular polygon). Returns dict(rings, side=[faces per segment], frames)."""
    bm = a.bm
    pts = [Vector(p) for p in pts]
    m = len(pts)
    segs = [(pts[i + 1] - pts[i]).normalized() for i in range(m - 1)]
    if u0 is None:
        u0 = _basis(segs[0])[0]
    u = u0 - segs[0] * u0.dot(segs[0])
    u = u.normalized() if u.length > 1e-6 else _basis(segs[0])[0]
    fr = []
    for i, t in enumerate(segs):
        if i:
            u = segs[i - 1].rotation_difference(t) @ u
            u = (u - t * u.dot(t)).normalized()
        fr.append((t, u, t.cross(u)))
    if section is None:
        section = [(math.cos(rot + 2 * math.pi * k / n), math.sin(rot + 2 * math.pi * k / n)) for k in range(n)]
    rings = []
    for i, p in enumerate(pts):
        t, uu, vv = fr[i - 1] if i else fr[0]
        nrm = (segs[i - 1] + segs[i]).normalized() if 0 < i < m - 1 else t
        ring = []
        for sx, sy in section:
            q = p + (uu * sx + vv * sy) * radii[i]
            q = q - t * ((q - p).dot(nrm) / t.dot(nrm))
            ring.append(bm.verts.new(q))
        rings.append(ring)
    side = [_band(bm, rings[i], rings[i + 1]) for i in range(m - 1)]
    return dict(rings=rings, side=side, frames=fr, pts=pts, radii=list(radii), n=n)


def cap(a, ch, which, kind, f_in=0.66, depth=0.1, seed=0):
    """End cap of a chain. kind: "flat" (one face), "cut" (pale cut rim + a paler-mid inner face), "dark" (pale rim,
    the inner face sunk `depth` and hollow), "snap" (a jagged pale break round a sunk dark centre), "socket" (a pale
    cut face round a square hole `f_in` = half-side, `depth` deep: hollow walls and floor). Returns {group: faces}."""
    bm = a.bm
    ring = ch["rings"][0] if which == "s" else ch["rings"][-1]
    t, u, v = ch["frames"][0] if which == "s" else ch["frames"][-1]
    d = -t if which == "s" else t                       # out of the chain
    c = sum((x.co for x in ring), Vector()) / len(ring)
    out = {"cut": [], "inner": [], "hole": [], "flat": []}
    if which == "s":
        ring = list(reversed(ring))
        u, v = v, u                                      # keep (u, v, d) right-handed for the walk
    if kind == "flat":
        out["flat"].append(bm.faces.new(ring))
        return out
    if kind == "socket":
        h = f_in
        sq = [bm.verts.new(p) for p in _square(c, u, v, h)]
        out["cut"] += _zip(bm, ring, sq, c, u, v)
        deep = [bm.verts.new(x.co - d * depth) for x in sq]
        out["hole"] += _band(bm, sq, deep) + [bm.faces.new(list(reversed(deep)))]
        return out
    inner = [bm.verts.new(c + (x.co - c) * f_in) for x in ring]
    out["cut"] += _band(bm, ring, inner)
    if kind == "cut":
        out["inner"].append(bm.faces.new(inner))
    elif kind == "dark":
        for x in inner:
            x.co -= d * depth
        out["hole"].append(bm.faces.new(inner))
    elif kind == "snap":
        rng = random.Random(seed)
        for k, x in enumerate(inner):
            x.co += d * (0.22 if k % 2 == 0 else -0.05) * rng.uniform(0.7, 1.2)
        pit = bm.verts.new(c - d * 0.12)
        n = len(inner)
        out["hole"] += [bm.faces.new((inner[k], inner[(k + 1) % n], pit)) for k in range(n)]
    return out


def pit(a, face, outdir, along, hint=None, size=0.3, depth=0.07, rim=None):
    """A bore pit in one facet (spec 2.4, decision 7): a square of half-side <= size/2 (and inside the facet) on the
    facet's centre (or pulled toward `hint`), sunk `depth` (negative: a raised boss); the facet's outline is walked
    round to the square by angle. rim = (outer half-side factor, lift): a second, wider square ring first (a raised
    pale rim round the pit). Returns (floor face, rim faces, zip faces) or None."""
    bm = a.bm
    if face is None or not face.is_valid:
        return None
    loop = list(face.verts)
    c = face.calc_center_median()
    face.normal_update()                 # a face just made by bm.faces.new has no normal yet
    nf = face.normal.copy()
    if nf.length < 0.5:
        return None
    if hint is not None:
        c = c.lerp(Vector(hint) - nf * (Vector(hint) - c).dot(nf), 0.55)
    ax = Vector(along) - nf * Vector(along).dot(nf)
    if ax.length < 1e-6:
        ax = (loop[1].co - loop[0].co)
    ax = (ax - nf * ax.dot(nf)).normalized()
    by = nf.cross(ax)
    out = nf if nf.dot(Vector(outdir)) >= 0 else -nf
    md = 1e9
    for i in range(len(loop)):
        p, q = loop[i].co, loop[(i + 1) % len(loop)].co
        e = q - p
        e2 = e - nf * e.dot(nf)
        w = (c - p) - nf * (c - p).dot(nf)
        if e2.length < 1e-6:
            continue
        md = min(md, (w - e2.normalized() * w.dot(e2.normalized())).length)
    hs = min(size / 2, 0.42 * md)
    if hs < 0.06:
        return None
    bmesh.ops.delete(bm, geom=[face], context="FACES_ONLY")
    rim_f = []
    if rim:
        outer = [bm.verts.new(p + out * rim[1]) for p in _square(c, ax, by, hs * rim[0])]
        zf = _zip(bm, loop, outer, c, ax, by)
        sq = [bm.verts.new(p - out * depth) for p in _square(c, ax, by, hs)]
        rim_f = _band(bm, outer, sq)
    else:
        sq = [bm.verts.new(p - out * depth) for p in _square(c, ax, by, hs)]
        zf = _zip(bm, loop, sq, c, ax, by)
    floor = bm.faces.new(sq)
    return floor, rim_f, zf


# ---- trunk core (spec 2.2) ------------------------------------------------------------------------------------------
STRANDS = (55.0, 115.0, 185.0, 240.0, 300.0, 355.0)      # the six root azimuths: each root continues up as a strand
STRAND_K = (1.0, 1.07, 0.98, 1.08, 1.0, 1.05)            # alternating strands a touch thicker
# rings: z, crest diameter, twist (deg, counter-clockwise going up: the front grooves climb "/")
BODY = ((0.0, 6.4, 0.0), (2.0, 5.9, 16.0), (4.2, 5.4, 34.0), (5.6, 5.15, 45.0), (6.9, 5.0, 55.0), (8.4, 5.1, 65.0),
        (9.8, 3.7, 72.0), (11.0, 2.85, 78.0), (11.9, 2.4, 82.0))
GROOVE = 0.42
TOP_AXIS = (58.0, 80.0)                     # the leader socket: tilted 10 deg from vertical toward az 58
TOP_HOLE = (0.31, 0.35)                     # square half-side, depth
KNOT = dict(z=6.9, az=327.0)
# trunk bore pits: (z, azimuth) targets on strand crest facets (mostly the front half and the sides)
TRUNK_PITS = ((5.0, 250.0), (4.9, 20.0), (6.2, 190.0), (7.6, 280.0), (5.2, 125.0), (7.4, 60.0), (9.2, 240.0),
              (6.4, 350.0), (7.8, 160.0), (10.4, 300.0), (10.2, 95.0), (4.9, 315.0))
SOCK = {}
GRID = {}
N18 = 18


def _strand_slots():
    """(azimuth at twist 0, kind, strand, gap) for the 18 body columns: groove, crest 1, crest 2 per strand."""
    al = list(STRANDS)
    n = len(al)
    out = []
    for s in range(n):
        a0 = al[s]
        prev = al[s - 1] - (360.0 if s == 0 else 0.0)
        nxt = al[(s + 1) % n] + (360.0 if s == n - 1 else 0.0)
        gl, gr = a0 - prev, nxt - a0
        out += [(a0 - gl / 2, "g", s, gl), (a0 - 0.2 * gl, "c", s, gl), (a0 + 0.2 * gr, "c", s, gr)]
    return out


def trunk_body(a):
    """The six twisted rope strands: 18 columns (a pulled-in groove vertex, then two crest vertices per strand),
    nine rings twisted 62 deg counter-clockwise from the foot to the top (the front grooves climb "/"). A flat
    underside with a square pin hole; a tilted flat cut top face with the square leader socket. Returns the grid."""
    bm = a.bm
    slots = _strand_slots()
    rng = random.Random(53100)
    rings, groove = [], set()
    dtop = _dir(TOP_AXIS[0], TOP_AXIS[1])
    zt = BODY[-1][0]
    for i, (z, dia, tw) in enumerate(BODY):
        R = dia / 2
        ring = []
        for j, (az0, kind, s, gap) in enumerate(slots):
            az = az0 + tw + rng.uniform(-1.5, 1.5)
            if kind == "g":
                depth = GROOVE * min(1.0, R / 2.5) * (0.5 if i == 0 else 1.0)
                r = R * math.cos(math.radians(0.3 * gap)) * 0.5 * (STRAND_K[s] + STRAND_K[s - 1]) - depth
            else:
                r = R * STRAND_K[s] * (1 + rng.uniform(-0.02, 0.02))
            p = _u(az) * r
            zz = z
            if i == len(BODY) - 1:          # the top ring lies in the leader socket's tilted plane
                zz = zt - (p.x * dtop.x + p.y * dtop.y) / dtop.z
            vv = bm.verts.new(Vector((p.x, p.y, zz)))
            if kind == "g":
                groove.add(vv)
            ring.append(vv)
        rings.append(ring)
    side = [_band(bm, rings[i], rings[i + 1]) for i in range(len(rings) - 1)]
    g = {"rings": rings, "side": side, "groove_v": groove, "slots": slots}
    # bottom: a flat disc at z 0 with a square pin hole in its middle (close-up 2)
    pin = [bm.verts.new(p) for p in _square(Vector((0, 0, 0.0)), Vector((1, 0, 0)), Vector((0, 1, 0)), 0.14)]
    g["disc"] = _zip(bm, rings[0], pin, Vector((0, 0, 0)), Vector((1, 0, 0)), Vector((0, 1, 0)))
    pin_d = [bm.verts.new(x.co + Vector((0, 0, 0.1))) for x in pin]
    g["pin"] = _band(bm, pin, pin_d) + [bm.faces.new(pin_d)]
    # top: the flat cut face round the square leader socket, perpendicular to the leader's axis
    ct = Vector((0.0, 0.0, zt))
    u, v = _basis(dtop, Vector((1, 0, 0)))
    h, dep = TOP_HOLE
    sq = [bm.verts.new(p) for p in _square(ct, u, v, h)]
    g["top"] = _zip(bm, rings[-1], sq, ct, u, v)
    deep = [bm.verts.new(x.co - dtop * dep) for x in sq]
    g["hole"] = _band(bm, sq, deep) + [bm.faces.new(deep)]
    SOCK["TOP"] = dict(F=ct, d=dtop, u=u, v=v, r=1.3, h=h, depth=dep, n=6)
    for k in ("knot_rim", "knot_hole", "boss", "pits", "cut", "socket", "walls", "stub_walls", "rt3"):
        g[k] = []
    return g


def _block(g, i0, i1, j0, k):
    """The boundary loop (counter-clockwise seen from outside), faces and interior verts of the body block of bands
    i0..i1-1 and columns j0..j0+k-1, or None if any of its faces is already taken."""
    rings, side = g["rings"], g["side"]
    faces = []
    for b in range(i0, i1):
        for c in range(j0, j0 + k):
            f = side[b][c % N18]
            if f is None:
                return None
            faces.append((b, c % N18, f))
    loop = [rings[i0][(j0 + c) % N18] for c in range(k + 1)]
    loop += [rings[i][(j0 + k) % N18] for i in range(i0 + 1, i1 + 1)]
    loop += [rings[i1][(j0 + c) % N18] for c in range(k - 1, -1, -1)]
    loop += [rings[i][j0 % N18] for i in range(i1 - 1, i0, -1)]
    interior = [rings[i][(j0 + c) % N18] for i in range(i0 + 1, i1) for c in range(1, k)]
    return loop, faces, interior


def _take(a, g, blk):
    loop, faces, interior = blk
    for b, c, f in faces:
        g["side"][b][c] = None
    bmesh.ops.delete(a.bm, geom=[f for _, _, f in faces], context="FACES_ONLY")
    bmesh.ops.delete(a.bm, geom=[v for v in interior if v.is_valid], context="VERTS")
    return loop


def _vert_block(g, z, az, rows=(1, 7)):
    """The free 2 x 2 block round the grid vertex nearest the bark point at (z, az): (loop, centre)."""
    rings = g["rings"]
    want = Vector((math.cos(math.radians(az)), math.sin(math.radians(az)), 0.0))
    cand = []
    for i in range(rows[0], rows[1] + 1):
        for j in range(N18):
            if not rings[i][j].is_valid:
                continue
            p = rings[i][j].co
            q = Vector((p.x, p.y, 0.0)).normalized()
            cand.append(((1 - q.dot(want)) * 6.0 + abs(p.z - z), i, j))
    for _, i, j in sorted(cand):
        blk = _block(g, i - 1, i + 1, j - 1, 2)
        if blk:
            return blk, rings[i][j].co.copy(), (i, j)
    raise RuntimeError(f"no free block near z {z} az {az}")


def knot(a, g):
    """The knot (spec 2.2, close-up 1): the 2 x 2 facet block round the crest vertex nearest KNOT is replaced by an
    oval ring set: a low swell, a raised pale rim (two rings), then a dark hole 0.32 deep with straight walls and a
    floor. A round pale boss sits on the crest facet below. Built into the body (no boolean)."""
    bm = a.bm
    blk, c, (i, j) = _vert_block(g, KNOT["z"], KNOT["az"], rows=(3, 5))
    loop = _take(a, g, blk)
    nrm = Vector((c.x, c.y, 0.0)).normalized()
    up = Vector((0, 0, 1))
    tang = up.cross(nrm)                               # increasing azimuth (to the right seen from outside)
    spec = ((0.50, 0.74, 0.04), (0.40, 0.60, 0.13), (0.27, 0.40, 0.11), (0.24, 0.35, -0.32))
    rs = []
    for hw, hh, lift in spec:
        rs.append([bm.verts.new(c + nrm * lift + tang * (hw * math.cos(2 * math.pi * k / 8)) +
                                up * (hh * math.sin(2 * math.pi * k / 8))) for k in range(8)])
    g["knot_swell"] = _zip(bm, loop, rs[0], c, tang, up)
    g["knot_rim"] = _band(bm, rs[0], rs[1]) + _band(bm, rs[1], rs[2])
    g["knot_hole"] = _band(bm, rs[2], rs[3]) + [bm.faces.new(rs[3])]
    SOCK["KNOT"] = {"c": c, "n": nrm}
    GRID["knot_ij"] = (i, j)


def _boss(a, g):
    """A round pale boss (a raised square) on the crest facet below the knot."""
    i, j = GRID["knot_ij"]
    c = SOCK["KNOT"]["c"]
    col = j - 1 if j % 3 == 2 else j
    for b in (i - 2, i - 3):
        f = g["side"][b][col % N18] if b >= 0 else None
        if f is not None and f.is_valid:
            r_ = pit(a, f, SOCK["KNOT"]["n"], Vector((0, 0, 1)), hint=c - Vector((0, 0, 1.2)), size=0.5, depth=-0.12)
            if r_:
                g["boss"].append(r_[0])
                return


# side sockets (spec 2.2): bark point height, azimuth of the bark point, the collar's axis (az, rise), its
# protrusion from the bark point to the face along the axis, collar radius, hole half-side, hole depth
SOCKETS = {
    "LM": dict(z=8.8, at=205.0, az=192.0, rise=25.0, out=1.0, r=1.2, h=0.40, depth=0.3, n=6),
    "L1": dict(z=8.2, at=146.0, az=163.0, rise=12.0, out=0.7, r=0.85, h=0.30, depth=0.3, n=6),
    "R": dict(z=8.6, at=15.0, az=13.0, rise=42.0, out=0.85, r=1.1, h=0.37, depth=0.3, n=6),
    "FR": dict(z=9.4, at=292.0, az=290.0, rise=20.0, out=0.7, r=0.95, h=0.32, depth=0.3, n=6),
    "TL": dict(z=10.6, at=150.0, az=150.0, rise=45.0, out=0.7, r=0.8, h=0.27, depth=0.3, n=6),
}


def collar(a, g, name, spec):
    """A socket collar grown out of the bark (no boolean): the 2 x 2 facet block nearest the socket's bark point is
    walked round (by angle) to a six-sided ring at the face F = bark point + axis x out, whose flat cut face holds a
    square hole (pale cut face, hollow walls and floor)."""
    bm = a.bm
    blk, c, ij = _vert_block(g, spec["z"], spec["at"])
    loop = _take(a, g, blk)
    d = _dir(spec["az"], spec["rise"])
    F = c + d * spec["out"]
    u, v = _basis(d)
    ring = [bm.verts.new(F + (u * math.cos(2 * math.pi * k / spec["n"]) + v * math.sin(2 * math.pi * k / spec["n"]))
                         * spec["r"]) for k in range(spec["n"])]
    cl = sum((x.co for x in loop), Vector()) / len(loop)
    g["walls"] += _zip(bm, loop, ring, cl, u, v, cb=F)
    sq = [bm.verts.new(p) for p in _square(F, u, v, spec["h"])]
    g["cut"] += _zip(bm, ring, sq, F, u, v)
    deep = [bm.verts.new(x.co - d * spec["depth"]) for x in sq]
    g["socket"] += _band(bm, sq, deep) + [bm.faces.new(list(reversed(deep)))]
    SOCK[name] = dict(F=F, d=d, u=u, v=v, r=spec["r"], h=spec["h"], depth=spec["depth"], n=spec["n"], bark=c)


# roots (spec 2.3): name, module kind, azimuth, toe reach, toe count, plan kink at the ground (deg)
ROOTS = (("RT1", "A", 185.0, 8.1, 3, -8.0), ("RT2", "B", 240.0, 7.6, 2, 7.0), ("RT3", "core", 300.0, 7.6, 2, -6.0),
         ("RT4", "C", 355.0, 7.9, 3, 8.0), ("RT5", "B", 55.0, 8.0, 2, -7.0), ("RT6", "A", 115.0, 7.5, 3, 8.0))
ROOT_YAW = {"RT5": 4.0, "RT6": -4.0}         # the repeated module instances turn a little (spec 3.6)
ROOT_KIND = {"A": dict(r=(1.35, 1.12, 0.9, 0.7), toe=0.4), "B": dict(r=(1.25, 1.05, 0.84, 0.64), toe=0.38),
             "C": dict(r=(1.3, 1.08, 0.86, 0.66), toe=0.39), "core": dict(r=(1.45, 1.22, 0.96, 0.74), toe=0.42)}
STUB_S = 4.0                           # stub face: plan distance from the axis
# root section (x across, y up, in units of the radius): a narrow top plank, two upper flanks, two lower flanks
# splayed onto the ground, a flat bottom
RSECT = ((0.30, 1.0), (-0.30, 1.0), (-1.0, 0.30), (-1.06, -0.62), (1.06, -0.62), (1.0, 0.30))
TOE_SECT = ((0.0, 1.55), (-1.0, 1.05), (-1.0, 0.0), (1.0, 0.0), (1.0, 1.05))
ROOT_INFO = {}


def _root_az(name):
    r = next(x for x in ROOTS if x[0] == name)
    return r[2] + ROOT_YAW.get(name, 0.0)


def _section_ring(a, c, side, up, r, sect=RSECT, ground=False):
    pts = [c + side * (sx * r) + up * (sy * r) for sx, sy in sect]
    if ground:
        lo = min(p.z for p in pts)
        pts = [Vector((p.x, p.y, 0.0)) if p.z - lo < 0.05 * r + 1e-6 or p.z < 0.0 else p for p in pts]
    return [a.bm.verts.new(p) for p in pts]


def stub(a, g, name, kind, built_in=False):
    """A root stub grown out of the strand's foot (no boolean): the strand's three facet columns over the two
    lowest bands are walked round (by angle) to the root section, upright, at plan distance STUB_S with its flat
    bottom on the ground: the buttress from the strand down onto the ground. Its flat cut face holds the square
    socket for the root module's peg; for the built-in front root RT3 the root runs straight on instead."""
    bm = a.bm
    s_i = STRANDS.index(next(x for x in ROOTS if x[0] == name)[2])
    az = _root_az(name)
    blk = _block(g, 0, 2, 3 * s_i, 3)
    loop = _take(a, g, blk)
    r = ROOT_KIND[kind]["r"][0]
    d = _u(az)
    side = Vector((-d.y, d.x, 0.0))
    up = Vector((0, 0, 1))
    F = d * STUB_S + up * (0.62 * r)
    ring = _section_ring(a, F, side, up, r, ground=True)
    cl = sum((x.co for x in loop), Vector()) / len(loop)
    walls = _zip(bm, loop, ring, cl, side, up, cb=F)
    g["stub_walls"] += walls
    h = 0.30 if kind != "B" else 0.28
    SOCK[name] = dict(F=F, d=d, u=side, v=up, r=r, h=h, depth=0.3, n=6, az=az)
    if built_in:
        return ring
    sq = [bm.verts.new(p) for p in _square(F, side, up, h)]
    g["cut"] += _zip(bm, ring, sq, F, side, up)
    deep = [bm.verts.new(x.co - d * 0.3) for x in sq]
    g["socket"] += _band(bm, sq, deep) + [bm.faces.new(list(reversed(deep)))]
    return ring


def _root_path(name):
    """Stations of a root (spec 2.3) after its base face: (centre, radius) along the ground to the fork, and the toes'
    tips: the base, a plan kink about 6 out, the fork, 2-3 toes splayed 26-30 deg."""
    _, kind, _, reach, ntoe, kink = next(r for r in ROOTS if r[0] == name)
    az = _root_az(name)
    rr = ROOT_KIND[kind]["r"]
    s = SOCK[name]
    F = s["F"]
    u0 = _u(az)
    u1 = _u(az + kink)
    k_s = 6.3 + 0.3 * (reach - 7.8)
    p1 = u0 * 5.2 + Vector((0, 0, 0.62 * rr[1]))
    pk = u0 * k_s + Vector((0, 0, 0.62 * rr[2]))
    pf = u0 * k_s + u1 * max(0.8, reach - k_s - 1.0) + Vector((0, 0, 0.62 * rr[3]))
    st = [(F + s["d"] * 0.015, rr[0] + 0.02), (p1, rr[1]), (pk, rr[2]), (pf, rr[3])]
    tips = []
    rng = random.Random(53400 + int(az))
    spread = (-26.0, 26.0) if ntoe == 2 else (-30.0, 2.0, 30.0)
    for k, sp in enumerate(spread):
        tl = (1.05 if ntoe == 2 else 0.95) * rng.uniform(0.92, 1.08) * (0.88 if abs(sp) > 20 and ntoe == 3 else 1.0)
        tips.append(pf + _u(az + kink + sp) * (tl + 0.35) - Vector((0, 0, pf.z)))
    return st, tips


def root_chain(a, name, start_ring=None):
    """A root module (or, with start_ring, the core's front root RT3 running on from its stub): a six-sided prism
    through its stations (upright sections, flat bottoms on the ground), its toes (five-sided blunt prisms buried 0.35
    in the root's end, flat ends, about half dark), its peg into the stub socket, and 1-2 bore pits. Returns verts
    (for RT3: the chain's verts and its toes' verts separately)."""
    bm = a.bm
    ROOT_INFO[name] = {}
    st, tips = _root_path(name)
    s = SOCK[name]
    kind = next(r for r in ROOTS if r[0] == name)[1]
    if start_ring is not None:
        st = [(s["F"], s["r"])] + st[1:]
    rings = []
    for i, (c, r) in enumerate(st):
        if i == 0:
            if start_ring is not None:
                rings.append(start_ring)
                continue
            side, up = s["u"], s["v"]
        else:
            nxt = st[min(i + 1, len(st) - 1)][0]
            prv = st[max(i - 1, 0)][0]
            t = nxt - prv
            t = Vector((t.x, t.y, 0.0)).normalized()
            side = Vector((-t.y, t.x, 0.0))
            up = Vector((0, 0, 1))
        rings.append(_section_ring(a, c, side, up, r, ground=True))
    sides = [_band(bm, rings[i], rings[i + 1]) for i in range(len(rings) - 1)]
    start = [] if start_ring is not None else [bm.faces.new(list(reversed(rings[0])))]
    end = [bm.faces.new(rings[-1])]
    pits_f = []
    for si, k, hint_t in ((0, 0, 0.55), (len(sides) - 2, 5, 0.5)):
        f = sides[si][k]
        c0, c1 = st[si][0], st[si + 1][0]
        r_ = pit(a, f, (f.calc_center_median() - c0.lerp(c1, 0.5)), c1 - c0, hint=c0.lerp(c1, hint_t),
                 size=0.32, depth=0.06)
        if r_:
            pits_f.append(r_[0])
    vs = [x for r in rings for x in r] + _vs(pits_f)
    vs = list(set(vs) | set(_vs(_faces(vs))))
    if start_ring is None:
        fs = _close(a, vs, WOOD)
    else:
        fs = _faces(vs)                  # RT3 is part of the body: the body's _close orients and colours it
    out_chain = list(vs)
    info = {"chain": fs, "start": start, "end": end, "pits": pits_f, "sides": sides}
    # toes
    pf = st[-1][0]
    tr = ROOT_KIND[kind]["toe"]
    toes = []
    for k, tip in enumerate(tips):
        dv = tip - Vector((pf.x, pf.y, 0.0))
        dv.z = 0.0
        dirn = dv.normalized()
        base = Vector((pf.x, pf.y, 0.004)) - dirn * 0.35
        tip0 = Vector((tip.x, tip.y, 0.004))
        sd_ = Vector((-dirn.y, dirn.x, 0.0))
        r0 = [bm.verts.new(base + sd_ * (sx * tr * 1.1) + Vector((0, 0, sy * tr * 1.1))) for sx, sy in TOE_SECT]
        r1 = [bm.verts.new(tip0 + sd_ * (sx * tr) + Vector((0, 0, sy * tr * 0.9))) for sx, sy in TOE_SECT]
        sd = _band(bm, r0, r1)
        bm.faces.new(list(reversed(r0)))
        e1 = bm.faces.new(r1)                # a flat blunt end: hollow on about half the toes, pale on the rest
        tv = r0 + r1
        _close(a, tv, WOOD)
        for f in sd:
            if f.calc_center_median().z < 0.2:
                f.material_index = a._mi(_mix(WOOD, WOOD_DARK, 0.3))
        _paint(a, [e1], HOLLOW if k % 2 == 0 else WOOD_LIGHT)
        _tint(a, sd, random.Random(53500 + k + int(s["az"])).uniform(0.95, 1.05))
        toes += tv
        ROOT_INFO[name].setdefault("toes", []).append((base.copy(), tip0.copy()))
    ROOT_INFO[name]["stations"] = [(tuple(round(x, 2) for x in c), round(r, 2)) for c, r in st]
    if start_ring is None:
        _paint_root(a, info, s)
        pv = peg(a, s, s["h"] - 0.02)
        return out_chain + toes + pv
    return out_chain, toes, info


def _paint_root(a, info, s):
    """Root colour by position (never facing): faces low on the root (centre under 0.42) deeper, the top plank a
    touch lighter (its place on the section), the base face pale (a cut face), the end deep, pits hollow."""
    for f in info["chain"]:
        if f.is_valid and f.calc_center_median().z < 0.42:
            f.material_index = a._mi(_mix(WOOD, WOOD_DARK, 0.3))
    for sd in info["sides"]:
        if sd[0].is_valid:
            sd[0].material_index = a._mi(_mix(WOOD, WOOD_LIGHT, 0.15))
    _paint(a, info["start"], WOOD_LIGHT)
    _paint(a, info["end"], WOOD_DARK)
    _paint(a, info["pits"], HOLLOW)
    _mottle(a, [f for f in info["chain"] if f.is_valid], 0.05, 0.45, 53450 + int(s["az"]))


def peg(a, s, h):
    """The square pale peg (spec 2.1): from 0.12 inside the module's base out through the socket mouth, its end 0.015
    above the hole's floor, 0.02 clear of the walls."""
    F, d = s["F"], s["d"]
    u, v = s["u"], s["v"]
    bm = a.bm
    p0 = F + d * 0.12
    p1 = F - d * (s["depth"] - 0.015)
    r0 = [bm.verts.new(p) for p in _square(p0, u, v, h)]
    r1 = [bm.verts.new(p) for p in _square(p1, u, v, h)]
    fs = _band(bm, r0, r1) + [bm.faces.new(r0), bm.faces.new(list(reversed(r1)))]
    vs = r0 + r1
    _close(a, vs, WOOD_LIGHT)
    return vs


def core_part(a):
    """One closed shell grown from the body grid (no booleans): the twisted body, the knot, five socket collars, five
    root stubs and the built-in front root RT3 bridged straight out of the facet grid, the trunk pits; then RT3's two
    toes (closed prisms) are exact-unioned in at the origin (_make_core)."""
    SOCK.clear()
    ROOT_INFO.clear()
    GRID.clear()
    g = trunk_body(a)
    knot(a, g)
    for name, spec in SOCKETS.items():
        collar(a, g, name, spec)
    rt3 = None
    for name, kind, *_ in ROOTS:
        ring = stub(a, g, name, kind, built_in=(kind == "core"))
        if kind == "core":
            rt3 = (name, ring)
    _boss(a, g)
    for z, az in TRUNK_PITS:
        f = _crest_face(g, z, az)
        r = pit(a, f, _u(az), Vector((0, 0, 1)), size=0.34, depth=0.07)
        if r:
            g["pits"].append(r[0])
    chain_vs, toes, info = root_chain(a, rt3[0], start_ring=rt3[1])
    tv = set(toes)
    vs = [x for x in a.bm.verts if x not in tv]
    _close(a, vs, WOOD)
    _paint_body(a, g)
    _paint_root(a, info, SOCK[rt3[0]])
    GRID["body"] = g


def _crest_face(g, z, az):
    """The middle (crest) facet of the strand nearest azimuth az in the band containing z, if still a free quad."""
    rings, side = g["rings"], g["side"]
    i = next((k for k in range(len(BODY) - 1) if BODY[k + 1][0] >= z), len(BODY) - 2)
    best, bd = None, 1e9
    for j, f in enumerate(side[i]):
        if j % 3 != 1 or f is None or not f.is_valid or len(f.verts) != 4:
            continue
        c = f.calc_center_median()
        da = abs((math.degrees(math.atan2(c.y, c.x)) - az + 180) % 360 - 180)
        if da < bd:
            best, bd = f, da
    return best if bd < 35 else None


def _paint_body(a, g):
    """Body colour by role and position (never facing): the flank facets (each touching a pulled-in groove vertex)
    deeper, the stub buttress walls by height (their lowest band deeper), the underside disc wood_dark, cut faces
    pale, holes hollow, the knot rim pale. Per-plank Tint held up each strand column, plus broad mottle."""
    gv = g["groove_v"]
    rng = random.Random(53120)
    tones = [1.0 + rng.uniform(-0.05, 0.05) for _ in range(N18)]
    side = g["side"]
    for i, band in enumerate(side):
        for j, f in enumerate(band):
            if f is None or not f.is_valid:
                continue
            if sum(1 for x in f.verts if x in gv) >= 2:
                f.material_index = a._mi(_mix(WOOD, WOOD_DARK, 0.3))
            _tint(a, [f], tones[j])
    for f in g["stub_walls"] + g["walls"]:
        if f.is_valid:
            if sum(1 for x in f.verts if x in gv) >= 2:
                f.material_index = a._mi(_mix(WOOD, WOOD_DARK, 0.3))
            elif f.calc_center_median().z < 0.42:
                f.material_index = a._mi(_mix(WOOD, WOOD_DARK, 0.3))
    _paint(a, g["disc"], WOOD_DARK)
    _paint(a, g["pin"], HOLLOW)
    _paint(a, g["top"], WOOD_LIGHT)
    _paint(a, g["hole"], HOLLOW)
    _paint(a, g["cut"], WOOD_LIGHT)
    _paint(a, g["socket"], HOLLOW)
    _paint(a, g["knot_rim"], WOOD_LIGHT)
    _paint(a, g["knot_hole"], HOLLOW)
    _paint(a, g["boss"], WOOD_LIGHT)
    _paint(a, g["pits"], HOLLOW)
    _mottle(a, [f for band in side for f in band if f is not None and f.is_valid] + g["stub_walls"] + g["walls"],
            0.03, 0.35, 53130)


# ---- branch modules (spec 2.4) -------------------------------------------------------------------------------------
# limb -> socket, main waypoints after the shoulder with radii, the main end cap, and children: (parent point (on the
# main chain's axis), waypoints, radii, sides, end cap)
LIMBS = {
    "LEAD": dict(sock="TOP", base_r=1.0, sides=6,
                 main=[((0.6, 0.6, 13.6), 0.9), ((1.1, 1.2, 15.2), 0.72), ((1.9, 2.4, 16.4), 0.52),
                       ((2.7, 3.3, 18.0), 0.36)], end="dark",
                 kids=[(2, [(0.75, 0.1, 16.3), (0.5, -0.9, 17.3)], [0.48, 0.33], 5, "cut"),
                       (3, [(3.4, 2.8, 16.9)], [0.31], 4, "dark"), (1, [(-0.4, 0.4, 14.6)], [0.32], 4, "cut")]),
    "TL": dict(sock="TL", base_r=0.8, sides=6,
               main=[((-2.2, 1.7, 12.9), 0.7), ((-3.3, 3.0, 15.6), 0.57), ((-4.1, 3.6, 16.9), 0.45),
                     ((-4.6, 3.9, 17.6), 0.33)], end="cut",
               kids=[(3, [(-4.95, 2.9, 16.95)], [0.31], 4, "dark"), (2, [(-2.95, 3.95, 16.75)], [0.3], 4, "cut"),
                     (1, [(-3.6, 1.6, 14.0)], [0.3], 4, "dark")]),
    "LM": dict(sock="LM", base_r=1.2, sides=6,
               main=[((-5.0, -0.8, 10.1), 0.92), ((-4.8, 1.5, 11.6), 0.8), ((-5.0, 2.3, 12.2), 0.76),
                     ((-5.2, 4.6, 13.4), 0.66), ((-5.4, 6.4, 14.4), 0.58)], end="snap",
               kids=[(3, [(-6.6, 0.2, 12.9), (-7.3, -0.8, 13.9)], [0.52, 0.34], 5, "dark"),
                     (4, [(-6.5, 4.9, 14.3)], [0.32], 4, "cut")],
               grand=[((-6.6, 0.2, 12.9), [(-7.8, -1.6, 12.8)], [0.32], 4, "cut")]),
    "L1": dict(sock="L1", base_r=0.85, sides=6,
               main=[((-4.7, 1.5, 9.1), 0.68), ((-7.0, 2.4, 9.2), 0.5), ((-8.5, 2.9, 10.4), 0.34)], end="dark",
               kids=[(3, [(-8.6, 2.1, 8.4)], [0.32], 4, "cut")],
               grand=[((-5.6, 1.85, 9.14), [(-5.9, 2.6, 10.4)], [0.3], 4, "cut"),
                      ((-6.3, 2.12, 9.17), [(-6.6, 3.4, 8.5)], [0.29], 4, "dark")]),
    "R": dict(sock="R", base_r=1.12, sides=6,
              main=[((4.0, 1.0, 13.1), 0.84), ((6.1, 0.9, 13.5), 0.68), ((6.8, 2.2, 14.8), 0.52),
                    ((7.5, 3.2, 15.4), 0.37)], end="cut",
              kids=[(3, [(7.4, -1.5, 13.1), (8.6, -3.7, 12.8)], [0.5, 0.35], 5, "dark"),
                    (4, [(6.2, 3.1, 15.6)], [0.3], 4, "dark"), (1, [(4.4, 0.6, 14.6)], [0.32], 4, "cut")],
              grand=[((7.4, -1.5, 13.1), [(8.9, -2.4, 12.1)], [0.32], 4, "cut")]),
    "FR": dict(sock="FR", base_r=0.95, sides=6,
               main=[((1.9, -4.8, 10.6), 0.76), ((2.6, -6.8, 11.6), 0.58), ((3.2, -7.9, 12.9), 0.37)], end="cut",
               kids=[(3, [(3.8, -7.4, 11.3)], [0.33], 4, "dark"), (2, [(1.2, -6.0, 11.8)], [0.32], 4, "cut")]),
}
LIMB_PITS = {   # limb -> (main segment index, face index, position along the segment 0-1)
    "LEAD": ((1, 0, 0.8), (2, 3, 0.25), (1, 4, 0.3), (2, 1, 0.75)),
    "TL": ((1, 2, 0.85), (2, 4, 0.2), (2, 1, 0.7), (3, 0, 0.3)),
    "LM": ((1, 1, 0.85), (1, 4, 0.3), (2, 2, 0.6), (3, 0, 0.5), (4, 3, 0.4), (5, 1, 0.5), (2, 5, 0.3)),
    "L1": ((1, 1, 0.8), (2, 4, 0.5), (2, 1, 0.2), (3, 2, 0.4)),
    "R": ((1, 2, 0.8), (2, 0, 0.5), (2, 3, 0.2), (3, 1, 0.5), (1, 5, 0.35)),
    "FR": ((1, 1, 0.75), (2, 3, 0.5), (2, 0, 0.2)),
}
LIMB_INFO = {}
LIMB_THIN, KID_THIN = 0.85, 0.9          # the limbs slimmer than the first pass (fix: pipes -> branches)


def _limb_points(name):
    L = LIMBS[name]
    s = SOCK[L["sock"]]
    F, d = s["F"], s["d"]
    base = F + d * 0.015
    p1 = Vector(L["main"][0][0])
    r_sh = L["base_r"]
    # shoulder long enough that the mitre at it doesn't cut back into the base ring
    th = (p1 - (F + d * 0.4)).angle(d, 0.0)
    sh = max(0.4, r_sh * math.tan(th / 2) * 1.25 + 0.15)
    pts = [base, F + d * sh] + [Vector(p) for p, _ in L["main"]]
    radii = [(s["r"] + 0.02) if L["sock"] != "TOP" else r_sh, r_sh] + [r * LIMB_THIN for _, r in L["main"]]
    return pts, radii, s


def _kid(a, p0, way, radii, n, end, r0, seed):
    """A side branch or tine: a closed n-sided chain from p0 (on the parent's axis, so buried by the parent's radius)
    through its waypoints, a flat cut or dark end."""
    pts = [Vector(p0)] + [Vector(w) for w in way]
    radii = [r * KID_THIN for r in radii]
    rr = [min(r0, radii[0] * 1.08)] + list(radii)
    ch = chain(a, pts, rr, n, rot=math.pi / n)
    c0 = cap(a, ch, "s", "flat")
    c1 = cap(a, ch, "e", "flat")          # one flat square-cut end face: pale (cut) or hollow (dark), no rim
    vs = [x for r in ch["rings"] for x in r]
    _close(a, vs, WOOD)
    _paint(a, c1["flat"], HOLLOW if end == "dark" else WOOD_LIGHT)
    sd = [f for s_ in ch["side"] for f in s_]
    _paint(a, sd, _mix(WOOD, WOOD_LIGHT, 0.1))
    _tint(a, sd, random.Random(seed).uniform(0.95, 1.05))
    return vs, ch


def branch_module(a, name):
    """One plug-in branch module (spec 2.4): the peg, the main six-sided chain from its base face (0.015 off the
    collar face, 0.02 wider) through a shoulder along the socket axis and its hard kinks to the end cap (a dark or pale
    square-cut end, or LM's snapped break), its side branches and tines (closed shells from the parent's axis), and
    its bore pits. Colour: the base segment deeper (under the collar), the segments a touch lighter toward the tips."""
    L = LIMBS[name]
    pts, radii, s = _limb_points(name)
    ch = chain(a, pts, radii, L["sides"], u0=s["u"])
    c0 = cap(a, ch, "s", "cut", f_in=0.62)
    c1 = cap(a, ch, "e", L["end"], f_in=0.6, depth=0.1, seed=53600 + len(name))
    pits_f, zips = [], []
    for si, k, at in LIMB_PITS.get(name, ()):
        si += 1
        if si >= len(ch["side"]):
            continue
        f = ch["side"][si][k % L["sides"]]
        a_, b_ = pts[si], pts[si + 1]
        r_ = pit(a, f, f.calc_center_median() - a_.lerp(b_, 0.5), b_ - a_, hint=a_.lerp(b_, at),
                 size=0.34 if radii[si] > 0.45 else 0.26, depth=0.07)
        if r_:
            pits_f.append(r_[0])
            zips.append((si, r_[2]))
    vs = [x for r in ch["rings"] for x in r] + _vs(c0["cut"] + c0["inner"] + c1["cut"] + c1["inner"] + c1["hole"] +
                                                   pits_f)
    vs = list(set(vs) | set(_vs(_faces(vs))))
    fs = _close(a, vs, WOOD)
    nseg = len(ch["side"])
    for si, sd in enumerate(ch["side"]):
        t = si / max(1, nseg - 1)
        key = _mix(WOOD, WOOD_DARK, 0.3) if si == 0 else _mix(WOOD, WOOD_LIGHT, 0.12 * t)
        _paint(a, sd, key)
        _tint(a, sd, random.Random(53610 + si + len(name)).uniform(0.96, 1.04))
    for si, zf in zips:   # the pit's surround keeps its segment's colour
        t = si / max(1, nseg - 1)
        _paint(a, zf, _mix(WOOD, WOOD_DARK, 0.3) if si == 0 else _mix(WOOD, WOOD_LIGHT, 0.12 * t))
    _paint(a, c0["cut"], WOOD_LIGHT)
    _paint(a, c0["inner"], _mix(WOOD_LIGHT, WOOD, 0.4))
    _paint(a, c1["cut"], WOOD_LIGHT)
    _paint(a, c1["inner"], WOOD_LIGHT)
    _paint(a, c1["hole"], HOLLOW)
    _paint(a, pits_f, HOLLOW)
    _mottle(a, [f for sd in ch["side"] for f in sd if f.is_valid], 0.04, 0.4, 53620 + len(name))
    out = list(vs)
    LIMB_INFO[name] = dict(pts=[p.copy() for p in pts], radii=list(radii), tips=[pts[-1].copy()], kids=[],
                           plug=[], pits=len(pits_f))
    # children: from a waypoint of the main chain (index into the main list: 0 = first main waypoint)
    for ki, (pi_, way, rr, n, end) in enumerate(L.get("kids", [])):
        p0 = pts[pi_ + 1]
        vs_k, chk = _kid(a, p0, way, rr, n, end, radii[pi_ + 1] * 0.82, 53630 + ki)
        out += vs_k
        LIMB_INFO[name]["kids"].append([p.copy() for p in chk["pts"]])
        LIMB_INFO[name]["tips"].append(chk["pts"][-1].copy())
    for gi, (p0, way, rr, n, end) in enumerate(L.get("grand", [])):
        vs_k, chk = _kid(a, Vector(p0), way, rr, n, end, 0.3, 53650 + gi)
        out += vs_k
        LIMB_INFO[name]["kids"].append([p.copy() for p in chk["pts"]])
        LIMB_INFO[name]["tips"].append(chk["pts"][-1].copy())
    pv = peg(a, s, s["h"] - 0.02)
    LIMB_INFO[name]["plug"] = [x.co.copy() for x in pv]
    out += pv
    return out


def root_module(a, name):
    return root_chain(a, name)


# ---- base dressing (spec 2.5) --------------------------------------------------------------------------------------
# rock -> centre, (W, D, H), yaw, kind ("tall": pointed, leaning in; "low": a sloping faceted top), seed
ROCKS = {
    "RK1": ((-5.9, 2.7), (2.7, 2.2, 3.8), 20.0, "tall", 53701),
    "RK2": ((5.7, 2.9), (2.5, 2.2, 3.6), -15.0, "tall", 53702),
    "RK3": ((-5.3, -3.7), (2.8, 2.3, 1.9), 30.0, "low", 53703),
    "RK4": ((-0.5, -6.3), (2.4, 2.0, 1.5), -10.0, "low", 53704),
    "RK5": ((5.7, -4.0), (1.6, 1.4, 1.1), 15.0, "low", 53705),
    "RK6": ((0.5, 6.1), (2.3, 1.9, 1.5), 5.0, "low", 53706),
}
PEBBLES = (((-6.8, -1.8), 0.7, 53711), ((1.9, -6.9), 0.55, 53712), ((7.5, -1.4), 0.6, 53713),
           ((-3.1, 6.6), 0.65, 53714), ((7.3, 3.7), 0.5, 53715))
TALL_RINGS = ((0.0, 0.94, 5), (0.38, 1.0, 5), (0.76, 0.76, 4), (1.0, 0.34, 3))
LOW_RINGS = ((0.0, 0.94, 5), (0.42, 1.0, 5), (1.0, 0.58, 4))
PEB_RINGS = ((0.0, 0.92, 4), (0.5, 1.0, 4), (1.0, 0.45, 3))
# moss pads between the roots: centre azimuth, plan distance, radius, seed
MOSS_PADS = ((212.0, 5.2, 1.61, 53721), (270.0, 5.0, 1.61, 53722), (327.0, 5.2, 1.61, 53723), (27.0, 5.0, 1.49, 53724),
             (85.0, 4.8, 1.49, 53725), (148.0, 4.8, 1.49, 53726), (265.0, 7.3, 1.15, 53727), (40.0, 7.3, 1.03, 53728),
             (200.0, 7.6, 1.03, 53729), (130.0, 7.2, 1.03, 53730))
# tufts: centre, blade count, height, spread, lime share, seed
TUFTS = {
    "T1": ((-7.4, -2.6), 7, 2.18, 1.08, 0.6, 53731),
    "T2": ((-3.0, -5.3), 7, 2.07, 1.20, 0.6, 53732),
    "T3": ((0.9, -6.7), 5, 1.26, 0.72, 0.75, 53733),
    "T4": ((4.0, -4.6), 6, 1.72, 0.84, 0.6, 53734),
    "T5a": ((7.0, -0.8), 8, 2.99, 1.32, 0.6, 53735),
    "T5b": ((6.4, 1.0), 6, 2.53, 1.08, 0.6, 53736),
    "T6": ((4.1, 4.7), 6, 1.95, 0.96, 0.6, 53737),
    "T7": ((-1.9, 6.7), 6, 2.18, 0.96, 0.6, 53738),
    "T8": ((-6.5, 4.5), 7, 2.18, 1.20, 0.6, 53739),
}
BASE_INFO = {}
_Solids = m047._Solids
# placement search: the planned spot first, then rings of candidates round it (0.3 apart, 8-16 per ring)
_SEARCH = [Vector((0, 0, 0))] + [Vector((math.cos(2 * math.pi * k / n + 0.3 * i) * r, math.sin(2 * math.pi * k / n +
                                                                                       0.3 * i) * r, 0.0))
                                 for i, (r, n) in enumerate(((0.3, 8), (0.6, 8), (0.9, 12), (1.2, 12), (1.5, 16),
                                                             (1.8, 16), (2.1, 16)))
                                 for k in range(n)]
_HUBS = []


def _rock(a, c, size, yaw, kind, seed, rings=None):
    """A chunky angular rock: the hull of jittered ring stacks with a flat base on the ground (z 0). Tall ones taper to
    a pointed top leaning toward the trunk; low ones have a sloping faceted top. Height bands: rock_light on the top
    30 %, rock_deep on the lowest 25 % (position, never facing)."""
    rng = random.Random(seed)
    W, D, H = size
    rings = rings or (TALL_RINGS if kind == "tall" else LOW_RINGS)
    inward = -Vector((c[0], c[1], 0.0)).normalized()
    m = Matrix.Rotation(math.radians(yaw), 3, "Z")
    il = m.inverted() @ inward
    lean = (0.32 * il.x, 0.32 * il.y) if kind == "tall" else (0.0, 0.0)
    pts = m033._ring_pts(rng, rings, W / 2, D / 2, H, 0.08, lean=lean)
    if kind == "low":
        tilt = rng.uniform(0.10, 0.18)
        for p in pts:
            p.z += tilt * (p.x * il.x + p.y * il.y) * (p.z / H)
    pts = [m @ p + Vector((c[0], c[1], 0.0)) for p in pts]
    for p in pts:
        p.z = max(0.0, p.z)
    vs = m033._hull(a, pts, ROCK)
    fs = _faces(vs)
    for f in fs:
        h = f.calc_center_median().z / H
        if h > 0.70:
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.6))
        elif h > 0.5:
            f.material_index = a._mi(_mix(ROCK, ROCK_LIGHT, 0.3))
        elif h < 0.22:
            f.material_index = a._mi(_mix(ROCK, ROCK_DEEP, 0.3))
    _mottle(a, fs, 0.04, 0.45, seed)
    for f in fs:
        _tint(a, [f], 1.0 + random.Random(seed + f.index).uniform(-0.03, 0.03))
    return vs


def moss_pad(a, c, R, seed):
    """A thin lobed moss pad on the ground: a 7-point lobed outline, a low crowned top (0.08-0.12), bottom just above
    z 0. Its rim a touch greener (grass 15 %)."""
    rng = random.Random(seed)
    bm = a.bm
    n = 7
    off = rng.uniform(0, 6.28)
    rad = [R * (1.0 if k % 2 == 0 else 0.72) * rng.uniform(0.85, 1.12) for k in range(n)]
    sq = (rng.uniform(0.75, 1.0), 1.0)
    rot = Matrix.Rotation(rng.uniform(0, 6.28), 3, "Z")
    out = [rot @ Vector((math.cos(off + 2 * math.pi * k / n) * rad[k] * sq[0],
                         math.sin(off + 2 * math.pi * k / n) * rad[k] * sq[1], 0.0)) for k in range(n)]
    cc = Vector((c[0], c[1], 0.004))
    th = rng.uniform(0.08, 0.12)
    bot = [bm.verts.new(cc + p) for p in out]
    top = [bm.verts.new(cc + p * 0.88 + Vector((0, 0, th * rng.uniform(0.8, 1.0)))) for p in out]
    peak = bm.verts.new(cc + Vector((0, 0, th + 0.04)))
    rim = _band(bm, bot, top)
    topf = [bm.faces.new((top[k], top[(k + 1) % n], peak)) for k in range(n)]
    botf = [bm.faces.new(list(reversed(bot)))]
    vs = bot + top + [peak]
    _close(a, vs, MOSS)
    _paint(a, rim, _mix(MOSS, GRASS, 0.2))
    _mottle(a, topf, 0.03, 0.25, seed)
    return vs


def blade(a, base, yaw, pitch, L, W, key, curl=0.12, face=None):
    """A pointed lanceolate grass blade (spec 2.5): a closed folded bipyramid (8 tris) - base, two shoulders at 0.35 L
    (widest), the tip, a raised midrib point on the front and a flatter one behind; rising at `pitch` toward `yaw`,
    the tip arching out and down by `curl`. face: a direction the broad face should turn toward (the front cameras),
    so the blade is never edge-on to them."""
    bm = a.bm
    u = Vector((math.cos(yaw), math.sin(yaw), 0.0))
    cp, sp = math.cos(pitch), math.sin(pitch)
    x = u * cp + Vector((0, 0, sp))
    z = -u * sp + Vector((0, 0, cp))
    if face is not None:
        f = Vector(face) - x * Vector(face).dot(x)
        if f.length > 1e-6:
            f.normalize()
            if f.dot(z) < 0:
                f = -f
            z = (z + f * 1.2).normalized()
            z = (z - x * z.dot(x)).normalized()
    y = z.cross(x)
    B = Vector(base)

    def P(lx, ly, lz):
        t = lx / L
        return bm.verts.new(B + x * lx + y * ly + z * (lz - curl * L * t * t))
    o = [P(0, 0, 0), P(0.35 * L, -W / 2, 0), P(L, 0, 0), P(0.35 * L, W / 2, 0)]
    fr = P(0.4 * L, 0, 0.09 * W + 0.03)
    bk = P(0.4 * L, 0, -0.05)
    fs = [bm.faces.new((o[i], o[(i + 1) % 4], fr)) for i in range(4)] + \
         [bm.faces.new((o[(i + 1) % 4], o[i], bk)) for i in range(4)]
    vs = o + [fr, bk]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    a._finish(vs, key, tint=1.0)
    return vs


CAM_F = Vector((0.0, -1.0, 0.25)).normalized()


def tuft(a, name, guard=None):
    """A tuft of pointed lime blades round a small closed 5-sided hub on the ground (hub 0.3 clear of roots, rocks
    and the trunk, else dropped); the tallest blades lime, the inner and lower ones deeper green (role). A blade that
    cuts a root, toe, the trunk or a rock more than BURY_PLACE stands up, turns aside, shortens; if every try still
    cuts it is dropped, never kept."""
    (cx, cy), n, H, R, lime, seed = TUFTS[name]
    rng = random.Random(seed)
    bm = a.bm
    info = BASE_INFO.setdefault(name, {"retried": 0, "dropped": 0, "moved": 0})
    hr, hh = 0.24, 0.3
    yaw0 = rng.uniform(0, 6.28)
    c = Vector((cx, cy, 0.0))
    # keep the hub 0.3 clear of the solids: the nearest free spot round the planned one
    if guard is not None:
        for off in _SEARCH:
            q = c + off
            probe = [q + Vector((math.cos(2 * math.pi * k / 8) * (hr + 0.3), math.sin(2 * math.pi * k / 8) * (hr + 0.3),
                                 z)) for k in range(8) for z in (0.05, 0.3)] + [q + Vector((0, 0, 0.15))]
            if max(guard.point(p)[0] for p in probe) <= 0.0 and all((q - h).length > 0.9 for h in _HUBS):
                info["moved"] = round(off.length, 2)
                c = q
                break
    _HUBS.append(c.copy())
    ring = [bm.verts.new(c + Vector((math.cos(yaw0 + 2 * math.pi * k / 5) * hr,
                                     math.sin(yaw0 + 2 * math.pi * k / 5) * hr, 0.004))) for k in range(5)]
    apex = bm.verts.new(c + Vector((0, 0, hh)))
    fs = [bm.faces.new((ring[k], ring[(k + 1) % 5], apex)) for k in range(5)] + [bm.faces.new(list(reversed(ring)))]
    hub = ring + [apex]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    a._finish(hub, _mix(GRASS_DEEP, WOOD_DARK, 0.25), tint=1.0)
    info["hub"] = [round(c.x, 2), round(c.y, 2)]
    out = list(hub)
    hs = [H * (rng.uniform(0.85, 1.0) if k % 2 == 0 else rng.uniform(0.55, 0.75)) for k in range(n)]
    order = sorted(range(n), key=lambda k: -hs[k])
    n_lime = max(1, round(lime * n))
    for k in range(n):
        yaw = yaw0 + 0.3 + 2 * math.pi * k / n + rng.uniform(-0.25, 0.25)
        tall = order.index(k) < n_lime
        pitch = math.radians(rng.uniform(66, 80) if hs[k] > 0.8 * H else rng.uniform(52, 64))
        Lb = hs[k] / math.sin(pitch) * 1.08
        Wb = Lb / 3.3 * rng.uniform(0.95, 1.1)
        key = GRASS if tall else _mix(GRASS, GRASS_DEEP, 0.55)
        tries = [(0.0, pitch, 1.0), (0.0, min(math.radians(82), pitch + 0.25), 0.9), (0.4, pitch, 0.9),
                 (-0.4, pitch, 0.9), (0.8, pitch + 0.15, 0.8), (-0.8, pitch + 0.15, 0.8), (0.0, math.radians(84), 0.7)]
        vs = None
        for i, (dy, p_, s_) in enumerate(tries):
            y_ = yaw + dy
            base = c + Vector((math.cos(y_) * hr * 0.3, math.sin(y_) * hr * 0.3, hh * 0.35))
            vs = blade(a, base, y_, p_, Lb * s_, Wb * s_, key, curl=rng.uniform(0.08, 0.15), face=CAM_F)
            if guard is None or guard.depth(vs) <= BURY_PLACE:
                info["retried"] += i > 0
                break
            for x in vs:
                bm.verts.remove(x)
            vs = None
        if vs is None:
            info["dropped"] += 1
            continue
        _tint(a, _faces(vs), 1.0 + rng.uniform(-0.04, 0.04))
        out += vs
    return out


def base_dressing(a, guard):
    """Rocks (each guarded off the roots: moved out 0.15 at a time while it cuts a root more than BURY), pebbles,
    moss pads (shrunk while they cut a root, rock or the trunk), tufts."""
    BASE_INFO.clear()
    rk = {}
    for name, (c, size, yaw, kind, seed) in ROCKS.items():
        c = Vector(c)
        for step in range(10):
            vs = _rock(a, c, size, yaw, kind, seed)
            dep = guard.depth(vs)
            if dep <= BURY_PLACE or step == 9:
                break
            for x in vs:
                a.bm.verts.remove(x)
            c = c + c.normalized() * 0.15
        rk[name] = (round(dep, 3), [round(c.x, 2), round(c.y, 2)])
        guard.add_vs(vs, name)
    BASE_INFO["rocks"] = rk
    for i, (c, s, seed) in enumerate(PEBBLES):
        c = Vector(c)
        for step in range(8):
            vs = _rock(a, c, (s, s * 0.85, s * 0.6), random.Random(seed).uniform(0, 180), "low", seed, rings=PEB_RINGS)
            if guard.depth(vs) <= BURY_PLACE or step == 7:
                break
            for x in vs:
                a.bm.verts.remove(x)
            c = c + c.normalized() * 0.2
        guard.add_vs(vs, f"PB{i + 1}")
    pads = {}
    for az, dist, R, seed in MOSS_PADS:
        c0 = _u(az) * dist
        vs, got = None, None
        for r in (R, 0.85 * R, 0.72 * R, 0.6 * R):
            for off in _SEARCH[:25]:
                vs = moss_pad(a, c0 + off, r, seed)
                if guard.depth(vs) <= BURY_PLACE:
                    got = (round(r, 2), round(off.length, 2))
                    break
                for x in vs:
                    a.bm.verts.remove(x)
                vs = None
            if vs is not None:
                break
        pads[seed] = got
    BASE_INFO["pads"] = pads
    _HUBS.clear()
    for name in TUFTS:
        tuft(a, name, guard)


def _core_guard():
    """The base guard: the built trunk core (body, stubs, RT3) in the build frame."""
    g = _Solids()
    t = bpy.data.objects.get(CORE_P)
    if t is not None and OFF in t:
        off = Vector(t[OFF])
        me = t.data
        g.add([v.co + off for v in me.vertices], [list(p.vertices) for p in me.polygons], "trunk")
    return g


def hero_rest(a):
    """Everything but the trunk core (unioned on its own and joined in): the five root modules (added to the guard as
    built), the six branch modules, then the base dressing."""
    guard = _core_guard()
    LIMB_INFO.clear()
    for name, kind, *_ in ROOTS:
        if kind == "core":
            continue
        vs = root_chain(a, name)
        guard.add_vs(vs, name)
    for name in LIMBS:
        branch_module(a, name)
    base_dressing(a, guard)


# ---- objects -------------------------------------------------------------------------------------------------------
NOTES = {
    HERO: "Dead Tree: a bare chunky snag on a massive twisted six-strand orange-brown trunk; six plug-in branch modules "
          "of straight faceted prisms with hard kinks and blunt square-cut tines; six roots with split toes; bore "
          "pits, an oval knot with a pale rim, a snapped pale limb end; pale grey rocks, lime moss and grass tufts at "
          "the foot. No VFX",
    CORE_P: "Trunk Core: twisted six-strand body with a square top socket, five socket collars, five root stubs, the "
            "built-in front root with two toes, the knot, bore pits and a flat underside with a pin hole",
    BRA_P: "Branch Module A: the big Y (left major limb) with its peg, a forked side branch and a snapped pale end",
    BRB_P: "Branch Module B: the kinked up-left limb with its peg, a spur at the elbow and a two-tine tip",
    BRC_P: "Branch Module C: the comb (low left limb) with its peg, two comb twigs and a forked tip",
    RTA_P: "Root Module A: thick tapering root with its peg, arching onto the ground and splitting into three toes",
    RTB_P: "Root Module B: medium root with its peg, splitting into two toes",
    RTC_P: "Root Module C: long root with its peg, splitting into three toes",
}
COLLISION = {HERO: "precise", CORE_P: "precise", BRA_P: "hull", BRB_P: "hull", BRC_P: "hull", RTA_P: "hull",
             RTB_P: "hull", RTC_P: "hull"}


def _new(name, fn, role, budget, temp=False):
    """Build fn into a fresh tagged kit object in the model's collection, keeping the build frame."""
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


def _post(o):
    """Stage 2-3 pass for an object of closed shells: every face a triangle, normals outward per shell, flat shading,
    origin at the bbox bottom centre, UVs (angle-based islands, overlaps cut free), bowties split."""
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
    M.smart_uv(o, **UV)
    lg["uv_cut"] = m012._uv_unfold(o)
    K.drop_unused_slots(o)
    return lg


def _make_core():
    t0 = time.time()
    o = _new(CORE_P, core_part, "part", 1000)
    lg = {"pre_tris": sum(len(p.vertices) - 2 for p in o.data.polygons)}
    m033._sane(o)
    lg["unions"] = m033._union_fine(o)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3], quad_method="BEAUTY",
                          ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()
    M.repair_nonmanifold(o)
    lg["slivers_forced"] = m012._force_slivers(o, lim=2.0, max_len=0.12)
    lg.update(_post(o))
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


def _make_shells(name, fn, role="part", budget=1000, temp=False):
    o = _new(name, fn, role, budget, temp=temp)
    return o, _post(o)


def _make_hero(core):
    t0 = time.time()
    o = _new(HERO, hero_rest, "hero", 4000)
    c = bpy.data.objects.new(PFX + "core", core.data.copy())
    o.users_collection[0].objects.link(c)
    c.matrix_world = Matrix.Translation(Vector(core[OFF]))
    bpy.context.view_layer.update()
    with M._override(o):
        c.select_set(True)
        with bpy.context.temp_override(selected_objects=[o, c], selected_editable_objects=[o, c]):
            bpy.ops.object.join()
    lg = _post(o)
    lg["secs"] = round(time.time() - t0, 1)
    return o, lg


# ---- checks ----------------------------------------------------------------------------------------------------------
def _keys(o):
    return [m.get("flintkit_key", m.name[3:]) if m else "" for m in o.data.materials]


def _kind(ks):
    if any(k.startswith("m053_moss") for k in ks):
        return "moss"
    if any("grass" in k for k in ks):
        return "plant"
    if any(k.startswith("m053_rock") for k in ks):
        return "rock"
    return "wood"


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
    kinds = [_kind({keys[f.material_index] for f in fs}) for fs in groups]
    wood = [k for k in range(n) if kinds[k] == "wood"]
    if wood:
        big = max(wood, key=lambda k: len(groups[k]))
        for k in wood:
            nf = len(groups[k])
            if k == big and nf > 300:
                kinds[k] = "trunk"
            elif nf == 12 and all(keys[f.material_index] == WOOD_LIGHT for f in groups[k]):
                kinds[k] = "peg"
    return bm, ids, n, groups, kinds


def shells_report(o):
    """Per shell: kind, tris, non-manifold edges and verts, boundary edges, winding errors (manifold edges whose two
    faces don't run the same way round), self-intersecting face pairs, signed volume."""
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
        out.append({"kind": kinds[k], "tris": len(fs),
                    "nonmanifold_edges": sum(1 for e in es if not e.is_manifold),
                    "nonmanifold_verts": sum(1 for v in vs if not v.is_manifold),
                    "boundary_edges": sum(1 for e in es if e.is_boundary),
                    "winding_errors": sum(1 for e in es if e.is_manifold and not e.is_contiguous),
                    "self_hits": hits, "volume": round(vol, 4), "zmin": round(min(v.co.z for v in vs), 3)})
    bm.free()
    return out


def contact_report(o, tol=CONTACT, chain_tol=0.1):
    """No floating dressing (STAGES): per shell, whether it touches another shell (triangles intersect, or a vertex
    within `tol` of another shell's surface) or the ground, and whether it chains by contact to an anchor (shells on
    the ground; for a branch module, its main chain)."""
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
    pairs = set()
    for i, j in tree.overlap(tree):
        a_, b_ = fsh[i], fsh[j]
        if a_ != b_:
            pairs.add((min(a_, b_), max(a_, b_)))
    near = {}
    for v in bm.verts:
        s = vsh.get(v.index)
        if s is None:
            continue
        for loc, _, fi, d in tree.find_nearest_range(v.co, chain_tol):
            t = fsh[fi]
            if t != s:
                kk = (min(s, t), max(s, t))
                near[kk] = min(near.get(kk, 1e9), d)
    for kk in pairs:
        near[kk] = 0.0
    gap = [1e9] * n
    for (a_, b_), d in near.items():
        gap[a_] = min(gap[a_], d)
        gap[b_] = min(gap[b_], d)
    ground = {k for k in range(n) if zmin[k] - z0 <= tol and z0 < 0.05}
    hz = max(v.co.z for v in bm.verts) - z0
    if not ground or (len(ground) == n and n > 1) or hz > 0 and o.name in (BRA_P, BRB_P, BRC_P):
        wood = [k for k in range(n) if kinds[k] in ("wood", "trunk")]
        ground = {max(wood, key=lambda k: len(groups[k]))} if wood else {0}
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
           "unchained": chained(tol), "unchained_chain_tol": chained(chain_tol),
           "kinds": {k: kinds.count(k) for k in sorted(set(kinds))}}
    bm.free()
    return res


def bury_report(o):
    """STAGES "no floating dressing ... nothing buried": every plant and moss shell tested by ray parity against every
    wood shell (trunk, roots, toes, limbs) and every rock; every rock against the wood. depth = the distance from its
    deepest vert or face centre inside to that shell's surface."""
    bm, ids, n, groups, kinds = _shells(o)
    wood = _Solids()
    rocks = _Solids()
    for k in range(n):
        if kinds[k] in ("wood", "trunk", "rock"):
            vs = list({v for f in groups[k] for v in f.verts})
            vi = {v: i for i, v in enumerate(vs)}
            (rocks if kinds[k] == "rock" else wood).add([v.co for v in vs], [[vi[v] for v in f.verts] for f in groups[k]],
                                                        f"{kinds[k]}{k}")
    res, rk = [], []
    for k in range(n):
        if kinds[k] not in ("plant", "moss", "rock"):
            continue
        fs = groups[k]
        pts = list({v.co.copy().freeze() for f in fs for v in f.verts}) + [f.calc_center_median() for f in fs]
        d1, w1 = max((wood.point(Vector(p)) for p in pts), key=lambda r: r[0])
        if kinds[k] == "rock":
            if d1 > 0:
                rk.append((round(d1, 3), w1))
            continue
        d2, w2 = max((rocks.point(Vector(p)) for p in pts), key=lambda r: r[0])
        d, who = (d1, w1) if d1 >= d2 else (d2, w2)
        if d > 0:
            c = sum((f.calc_center_median() for f in fs), Vector()) / len(fs)
            res.append((round(d, 3), kinds[k], who, [round(x, 2) for x in c]))
    bm.free()
    res.sort(key=lambda r: -r[0])
    rk.sort(key=lambda r: -r[0])
    return {"dressing_shells": sum(1 for k in kinds if k in ("plant", "moss")), "over_0.05": sum(1 for r in res if r[0] > BURY),
            "max": res[0][0] if res else 0.0, "worst": res[:6],
            "rocks_in_wood_over_0.05": sum(1 for r in rk if r[0] > BURY), "rocks_in_wood": rk[:6]}


def plug_report(h):
    """Each branch module's peg corners against the hero's trunk shell: nearest distance (0.02 clearance expected) and
    whether any corner lies inside the trunk's solid (it must not: the peg sits in the hole's cavity)."""
    bm, ids, n, groups, kinds = _shells(h)
    k = kinds.index("trunk")
    fs = groups[k]
    vs = list({v for f in fs for v in f.verts})
    vi = {v: i for i, v in enumerate(vs)}
    off = Vector(h[OFF])
    tree = BVHTree.FromPolygons([v.co + off for v in vs], [[vi[v] for v in f.verts] for f in fs])
    bm.free()
    out = {}
    for name, info in LIMB_INFO.items():
        if not info.get("plug"):
            continue
        ds = [tree.find_nearest(p)[3] for p in info["plug"]]
        inside = sum(1 for p in info["plug"][4:] if m047._parity_in(tree, p))
        out[name] = {"min": round(min(ds), 4), "max": round(max(ds), 4), "end_corners_inside_solid": inside}
    return out


LIMB_VIEWS = {"front": (0, 4), "rear": (180, 4), "side": (90, 4), "f34": (-20, 10), "top": (0, 89)}


def _cam(az, el):
    a_, e_ = math.radians(az), math.radians(el)
    return Vector((math.sin(a_) * math.cos(e_), -math.cos(a_) * math.cos(e_), math.sin(e_)))


def limb_visibility(h, views=LIMB_VIEWS, step=0.1):
    """Per limb and view: the visible length of its main chain (shoulder -> end), i.e. not hidden behind the trunk
    or the base (rays from centreline samples toward the camera against the trunk, root and dressing shells), the
    length on screen, and how many of its tine ends are seen."""
    bm, ids, n, groups, kinds = _shells(h)
    off = Vector(h[OFF])
    keep = [f for k in range(n) if kinds[k] in ("trunk", "rock", "plant", "moss") for f in groups[k]]
    vs = list({v for f in keep for v in f.verts})
    vi = {v: i for i, v in enumerate(vs)}
    tree = BVHTree.FromPolygons([v.co + off for v in vs], [[vi[v] for v in f.verts] for f in keep])
    bm.free()
    out = {"tips": {}}
    for name, info in LIMB_INFO.items():
        pts = info["pts"][1:]
        row, tp = {}, {}
        for vn, (az, el) in views.items():
            d = _cam(az, el)
            vis = scr = tot = 0.0
            for p, q in zip(pts, pts[1:]):
                seg = q - p
                m = max(1, int(seg.length / step))
                for i in range(m):
                    c = p + seg * ((i + 0.5) / m)
                    ln = seg.length / m
                    tot += ln
                    if tree.ray_cast(c, d, 200.0)[0] is None:
                        vis += ln
                        scr += (seg - d * seg.dot(d)).length / m
            row[vn] = (round(vis, 2), round(scr, 2), round(tot, 2))
            tp[vn] = sum(1 for t in info["tips"] if tree.ray_cast(t, d, 200.0)[0] is None)
        out[name] = row
        out["tips"][name] = tp
    return out


def socket_report():
    return {k: {"F": [round(x, 2) for x in s["F"]]} for k, s in SOCK.items() if "F" in s}


# ---- build -------------------------------------------------------------------------------------------------------------
PARTS = ((BRA_P, lambda a: branch_module(a, "LM")), (BRB_P, lambda a: branch_module(a, "TL")),
         (BRC_P, lambda a: branch_module(a, "L1")), (RTA_P, lambda a: root_module(a, "RT1")),
         (RTB_P, lambda a: root_module(a, "RT2")), (RTC_P, lambda a: root_module(a, "RT4")))
TARGET_SIZE = ((17.6, 0.9), (15.5, 1.6), (18.0, 0.4))


def _cleanup_tmp():
    for o in list(bpy.data.objects):
        if o.name.startswith(PFX):
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(me, bpy.types.Mesh) and me.users == 0:
                bpy.data.meshes.remove(me)


def _drop_unused():
    mats = [m for m in bpy.data.materials if m.users == 0 and not m.use_fake_user and m.name.startswith("FB_m053_")]
    for m in mats:
        bpy.data.materials.remove(m)
    meshes = [m for m in bpy.data.meshes if m.users == 0 and m.name.startswith((PFX, "_probe", "T_Calib", "TwistedSnag"))]
    for m in meshes:
        bpy.data.meshes.remove(m)
    return len(mats), len(meshes)


def build(render=True, parts=True, close=True):
    t0 = time.time()
    M.coll(NUM, TITLE)
    m033.UNION_RETRIES.clear()
    palette()
    LIMB_INFO.clear()
    objs, log = {}, {}
    core, log[CORE_P] = _make_core()
    objs[CORE_P] = core
    if parts:
        for name, fn in PARTS:
            objs[name], log[name] = _make_shells(name, fn)
    LIMB_INFO.clear()
    h, log["hero"] = _make_hero(core)
    log["union_retries"] = list(m033.UNION_RETRIES)
    log["sockets"] = socket_report()
    _cleanup_tmp()
    order = [h] + [objs[n] for n in (CORE_P, BRA_P, BRB_P, BRC_P, RTA_P, RTB_P, RTC_P) if n in objs]
    M.display(NUM, order, TITLE)
    log["dropped"] = _drop_unused()
    for o in order:
        d = o.dimensions
        o["studs"] = f"{d.x:.1f} x {d.y:.1f} x {d.z:.1f}"
    audits = [M.audit(o) for o in order]
    thin = {o.name: m012._thin(o, 2.0) for o in order}
    shells = {o.name: shells_report(o) for o in order}
    problems = list(K.check(order))
    for o, au in zip(order, audits):
        lim = 3800 if o is h else 1000
        if au["tris"] > lim:
            problems.append(f"{o.name}: {au['tris']} tris over {lim}")
        for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "wire_edges", "loose_verts",
                  "zero_area_faces", "ngons"):
            if au[k]:
                problems.append(f"{o.name}: {k} {au[k]}")
        if au["normals"] != "outward":
            problems.append(f"{o.name}: normals {au['normals']}")
        for i, s in enumerate(shells[o.name]):
            for k in ("nonmanifold_edges", "nonmanifold_verts", "boundary_edges", "winding_errors", "self_hits"):
                if s[k]:
                    problems.append(f"{o.name} shell {i} ({s['kind']}): {k} {s[k]}")
            if s["volume"] <= 0:
                problems.append(f"{o.name} shell {i} ({s['kind']}): not closed outward (volume {s['volume']})")
    contact = {o.name: contact_report(o) for o in order}
    for n_, c in contact.items():
        if c["floating"] or c["unchained"]:
            problems.append(f"{n_}: {c['floating']} shells touch nothing within {CONTACT}, {c['unchained']} have no "
                            f"chain of contact to an anchor")
    bury = {h.name: bury_report(h)}
    for n_, b in bury.items():
        if b["over_0.05"]:
            problems.append(f"{n_}: {b['over_0.05']} dressing shells more than {BURY} inside wood or rock "
                            f"(worst {b['worst'][:3]})")
        if b["rocks_in_wood_over_0.05"]:
            problems.append(f"{n_}: {b['rocks_in_wood_over_0.05']} rocks more than {BURY} into the roots "
                            f"({b['rocks_in_wood'][:3]})")
    if len(shells[CORE_P]) != 1:
        problems.append(f"{CORE_P}: {len(shells[CORE_P])} shells, expected 1")
    if sum(1 for s in shells[HERO] if s["kind"] == "trunk") != 1:
        problems.append(f"{HERO}: {sum(1 for s in shells[HERO] if s['kind'] == 'trunk')} trunk shells, expected 1")
    for (tgt, tol), got, ax in zip(TARGET_SIZE, h.dimensions, "WDH"):
        if abs(got - tgt) > tol:
            problems.append(f"{HERO}: {ax} {got:.2f} outside {tgt} +- {tol}")
    if [c for c in h.children if c.get("vfx_kind")]:
        problems.append(f"{HERO}: has VFX sockets (decision 14: none)")
    winding = {o.name: sum(s["winding_errors"] for s in shells[o.name]) for o in order}
    uv = {o.name: {k: v for k, v in M.uv_stats(o).items() if k in ("islands", "overlap_pairs", "flipped", "min_gap",
                                                                    "border", "density", "stretch_conformal_p95")}
          for o in order}
    for n_, u in uv.items():
        if u.get("overlap_pairs") or u.get("flipped"):
            problems.append(f"{n_}: UV overlaps {u.get('overlap_pairs')} flipped {u.get('flipped')}")
    kinds = {}
    for s in shells[HERO]:
        kk = kinds.setdefault(s["kind"], {"n": 0, "tris": 0})
        kk["n"] += 1
        kk["tris"] += s["tris"]
    out = {"audit": [{k: au[k] for k in ("name", "tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                         "boundary_edges", "wire_edges", "loose_verts", "zero_area_faces", "normals",
                                         "ngons", "dup_verts", "origin_offset", "transforms_applied")} for au in audits],
           "hero_shells": kinds, "contact": contact, "bury": bury, "winding": winding, "base_info": dict(BASE_INFO),
           "thin": thin, "log": log, "problems": problems, "uv": uv,
           "plugs": plug_report(h), "limbs": limb_visibility(h),
           "offsets": {o.name: [round(x, 3) for x in o[OFF]] for o in order},
           "materials": {o.name: [m.name[3:] for m in o.data.materials] for o in order},
           "baked_shading": {o.name: o.get("kit_baked_shading") for o in order},
           "build_s": round(time.time() - t0, 1)}
    if render:
        out["views"] = render_views(order, close=close)
        out["render_s"] = round(time.time() - t0 - out["build_s"], 1)
    return out


# ---- renders -------------------------------------------------------------------------------------------------------
# decision 10: f34_sheet (0, 12) and front_sheet (0, 4) govern; the other sheet views at e 4, floor hidden, 3x lens
SHEET_VIEWS = {"f34_sheet": (-20, 10), "r34_sheet": (160, 10), "front_sheet": (0, 4), "side_sheet": (90, 4),
               "rear_sheet": (180, 4), "top_sheet": (0, 89)}
VIEW_NAMES = ("front", "side", "rear", "top", "underside")
PARTS_SHOT = (-25, 18)
EXPLODE_BRANCH = 3.4
EXPLODE_ROOT = 2.6


def _temp_module(name, fn):
    o, _ = _make_shells(PFX + "mod_" + name, fn, temp=True)
    return o


def _exploded(objs):
    """Copies laid out like the sheet's exploded view: the trunk core in the middle, every branch module drawn out
    of its socket along the socket axis, every root module drawn out along its stub axis (the unlabelled modules
    and the second root instances built on the fly)."""
    by = {o.name: o for o in objs}
    coll = objs[0].users_collection[0]
    shown, temps = [], []
    x0 = objs[0].location.x + 70
    y0 = objs[0].location.y
    base = Matrix.Translation((x0, y0, 0))
    pieces = {"LM": by.get(BRA_P), "TL": by.get(BRB_P), "L1": by.get(BRC_P)}
    for nm in ("LEAD", "R", "FR"):
        t = _temp_module(nm, lambda a, nm=nm: branch_module(a, nm))
        temps.append(t)
        pieces[nm] = t
    roots = {"RT1": by.get(RTA_P), "RT2": by.get(RTB_P), "RT4": by.get(RTC_P)}
    for nm in ("RT5", "RT6"):
        t = _temp_module(nm, lambda a, nm=nm: root_module(a, nm))
        temps.append(t)
        roots[nm] = t

    def put(tag, o, dv):
        c = bpy.data.objects.new(f"{PFX}expl_{tag}", o.data)
        coll.objects.link(c)
        c.matrix_world = base @ Matrix.Translation(dv) @ Matrix.Translation(Vector(o[OFF]))
        shown.append(c)
    if CORE_P in by:
        put("core", by[CORE_P], Vector((0, 0, 0)))
    for nm, o in pieces.items():
        if o is not None:
            put(nm, o, SOCK[LIMBS[nm]["sock"]]["d"] * EXPLODE_BRANCH)
    for nm, o in roots.items():
        if o is not None:
            d = SOCK[nm]["d"]
            put(nm, o, Vector((d.x, d.y, 0.0)).normalized() * EXPLODE_ROOT)
    bpy.context.view_layer.update()
    return shown, temps


def _scale_marker(h, at):
    """A 5.5-stud character stand-in at build-frame point `at` (under the L1 limb)."""
    a = K.fk().Asset(PFX + "char", "probe", seed=1, tint_var=0.0)
    a.cyl(0.6, 0.6, 3.3, sides=8, loc=(0, 0, 0), mat=ROCK_DEEP, tint=0.7)
    a.cyl(0.45, 0.45, 0.9, sides=8, loc=(0, 0, 3.4), mat=ROCK_DEEP, tint=0.7)
    a.cyl(0.55, 0.3, 1.2, sides=8, loc=(0, 0, 4.3), mat=ROCK_DEEP, tint=0.7)
    c = a.finish(collection=h.users_collection[0], mark_asset=False)
    off = h.matrix_world @ Matrix.Translation(-Vector(h[OFF]))
    c.location = off @ Vector(at)
    bpy.context.view_layer.update()
    return c


def render_views(objs, close=True):
    h = objs[0]
    shown, temps = _exploded(objs) if len(objs) > 1 else ([], [])
    marker = _scale_marker(h, (-6.6, 0.4, 0.0))
    try:
        extra = {k: ([h], az, el) for k, (az, el) in SHEET_VIEWS.items()}
        extra["front34"] = ([h], -28, 12)
        extra["rear34"] = ([h], 152, 12)
        for o in objs[1:]:
            extra["part_" + o.name.replace("TwistedSnag", "").lower()] = ([o], *PARTS_SHOT)
        if shown:
            extra["exploded"] = (shown, 0, 22)
        extra["scale"] = ([h, marker], 0, 4)
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
        for o in shown + [marker]:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if o is marker and me.users == 0:
                bpy.data.meshes.remove(me)
        for t in temps:
            me = t.data
            bpy.data.objects.remove(t, do_unlink=True)
            if me.users == 0:
                bpy.data.meshes.remove(me)
        M.display(NUM, objs, TITLE)


def render_close_ups(objs):
    """twist_cu (the trunk's crossing strands), kink_cu (LM's elbow), tines_cu (the leader's V and TL's tips), knot_cu,
    root_cu (RT3 and RT4 toes), base_cu (the foot with rocks, moss and tufts), join_cu (the core's LM collar and Branch
    A's peg end, close-up 1), under_cu (the underside, close-up 2)."""
    d = f"{M.MODEL_RENDERS}/{M.code(NUM)}"
    by = {o.name: o for o in objs}
    h = objs[0]
    out = {}

    def at(o, p):
        return o.matrix_world @ Matrix.Translation(-Vector(o[OFF])) @ Vector(p)
    rc = m033.render_close
    out["twist_cu"] = rc([h], f"{d}/twist_cu.png", 8, 8, at(h, (0.0, -1.5, 6.0)), 3.6)
    out["kink_cu"] = rc([h], f"{d}/kink_cu.png", -20, 10, at(h, (-4.6, -0.6, 10.6)), 2.4)
    out["tines_cu"] = rc([h], f"{d}/tines_cu.png", -20, 10, at(h, (0.5, 1.5, 15.6)), 4.2)
    k = SOCK["KNOT"]["c"]
    out["knot_cu"] = rc([h], f"{d}/knot_cu.png", 30, 6, at(h, k), 1.4)
    out["root_cu"] = rc([h], f"{d}/root_cu.png", 20, 16, at(h, (3.6, -4.6, 1.0)), 3.0)
    out["base_cu"] = rc([h], f"{d}/base_cu.png", -10, 14, at(h, (-2.0, -4.0, 1.2)), 5.0)
    out["under_cu"] = rc([h], f"{d}/under_cu.png", 0, -70, at(h, (0.0, 0.0, 0.5)), 6.0)
    if CORE_P in by:
        t = by[CORE_P]
        out["join_cu"] = rc([t], f"{d}/join_cu.png", -60, 20, at(t, SOCK["LM"]["F"]), 1.8)
    if BRA_P in by:
        b = by[BRA_P]
        out["peg_cu"] = rc([b], f"{d}/peg_cu.png", 120, 12, at(b, SOCK["LM"]["F"]), 1.6)
    return out


def preview(names=("f34_sheet", "front_sheet", "rear_sheet", "side_sheet", "r34_sheet", "top_sheet"), vfx=False):
    """Just the sheet comparison shots of the hero (fast tuning loop)."""
    h = bpy.data.objects[HERO]
    kit = K.NS["KIT"]
    orig, kit["render_group"] = m033._long_lens(kit)
    try:
        return M.views(NUM, [h], names=(), extra={k: ([h], *SHEET_VIEWS[k]) for k in names}, vfx=vfx)
    finally:
        kit["render_group"] = orig


def hero_only():
    """Rebuild just the core and the hero (tuning loop)."""
    M.coll(NUM, TITLE)
    palette()
    LIMB_INFO.clear()
    core, lc = _make_core()
    h, lg = _make_hero(core)
    _cleanup_tmp()
    M.display(NUM, [h] + [bpy.data.objects[n] for n in (CORE_P, BRA_P, BRB_P, BRC_P, RTA_P, RTB_P, RTC_P)
                          if n in bpy.data.objects], TITLE)
    au = M.audit(h)
    ac = M.audit(core)
    return {"hero": {k: au[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                        "boundary_edges", "normals")},
            "core": {k: ac[k] for k in ("tris", "size", "shells", "nonmanifold_edges", "nonmanifold_verts",
                                        "boundary_edges", "normals")}, "log": lg, "core_log": lc,
            "sockets": socket_report()}
