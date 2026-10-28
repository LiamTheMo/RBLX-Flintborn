"""W02 row 3: NATURAL RAMP, "broad sloped path through terrain".

A walkable sandy-orange dirt path between two levels. It is about 10 studs wide,
with faint darker cross seams like shallow terraces and pale pebbles. Each side
has a bright grass border (0.6 grass over a 0.4 earth band, a scalloped outer
lip, round bush clumps, flower dots). Under each border is a wall of tall,
narrow, faceted rock columns in the CliffWall style that grows with the slope.
At the low end the walls shrink to pointed shards and ground bushes. A pale
stone wedge (w02_ramp_slab) shows between the columns and under the low path edge.
Rock, slab and seam colours use w02_ramp_* module keys sampled from the reference
(paler and cooler than the shared w02_rock family; see PALETTE).
The high end ends in the sheet's flat grey back connector plate with edge tabs.

Assets
  NaturalRamp              hero: 16 x 32, a 24-long slope from 0 to 12 (26 deg),
                           then an 8-deep flat landing at 12
  NaturalRampStraight      variant A: 16 x 48, from 0 to 12 (14 deg), no landing
  NaturalRampCurved        variant B: a 90 deg arc (centreline radius 20) with
                           short straight lead-ins, 32 x 32, from 0 to 12; it
                           enters heading +X and leaves heading +Y; the outer
                           (front-right) wall columns rise above the grass
  NaturalRampSwitchback    variant C: a flight from 0 to 12 along the front, a
                           flat U-turn landing at 12, and a flight from 12 to 24
                           along the back, with a tall rock wall between them,
                           32 x 32
  NaturalRampGrassBorder   part: one 24-long sloped grass strip
  NaturalRampTopLandingPad part: a 10 x 8 x 1.5 dirt pad
  NaturalRampWedge         part: a pale stone wedge, 10 x 24, from 0 to 12

Everything is built from three pieces: path ribbons (a centreline plus a
height function), edges (a polyline at path height carrying a grass cap,
rock columns and a pale core curtain), and back plates. The walls are convex
hulls of jittered rings. Each column top is clipped by the slope, so the walls
follow the ramp. Every material has ONE colour with a small random Tint; the
path seams and the wedge crack are geometry (steeper risers, a thin ridge) that
the lighting draws. The +X side of the hero's landing is a flat grey connector face.

Faces of the walk-through dressing (bushes, flowers, pebbles, boulders on the
borders) carry the face attribute kit_nocollide = 1. No VFX: the reference
shows none.
"""

import math
import random

import bmesh
from mathutils import Vector

SUBJECT = "NaturalRamp"
ROW = 3
# The W02 sheet palette, copied verbatim so all four W02 modules agree.
PALETTE = {
    "w02_rock": ("#958482", 0.9, 0, 0),
    "w02_rock_light": ("#BBA090", 0.9, 0, 0),
    "w02_rock_cool": ("#686A7C", 0.9, 0, 0),
    "w02_rock_deep": ("#525A6E", 0.9, 0, 0),
    "w02_grass": ("#A9BE26", 0.95, 0, 0),
    "w02_grass_light": ("#C2D23A", 0.95, 0, 0),
    "w02_grass_dark": ("#789428", 0.95, 0, 0),
    "w02_earth": ("#9F6A47", 0.95, 0, 0),
    "w02_path": ("#E2A86E", 0.95, 0, 0),
    "w02_path_dark": ("#C48A52", 0.95, 0, 0),
    "w02_slab": ("#BFAEA8", 0.9, 0, 0),
    "w02_connector": ("#8A858A", 0.95, 0, 0),
    "w02_bush": ("#4F8A3B", 0.8, 0, 0),
    "w02_bush_light": ("#7DAF3E", 0.8, 0, 0),
    "w02_bush_dark": ("#30602C", 0.8, 0, 0),
    # Module keys sampled from the reference row (verifier review): the sheet's rock
    # is a paler, cooler grey-mauve than the shared w02_rock family and the wedge
    # stone a lilac grey. Materials are cached by key name, so changing the shared
    # keys here would not reach a full sheet build (the first module wins); new keys
    # keep every module consistent. ONE colour per material (the runner's rule):
    # rock is one pale grey-mauve, the light/dark the reference shows is lighting.
    "w02_ramp_rock": ("#B9ADA9", 0.9, 0, 0),        # pale grey-mauve rock, lit mid-tone (ref swatch ~#C9B8B0)
    "w02_ramp_slab": ("#B8B0B6", 0.9, 0, 0),        # lilac-grey wedge stone
}

ROCK = "w02_ramp_rock"
GRASS, EARTH = "w02_grass", "w02_earth"
PATH, SLAB, CONN = "w02_path", "w02_ramp_slab", "w02_connector"
BUSH = "w02_bush"
TWO_TONE_OK = ("different materials, not shades: w02_ramp_rock (rock columns) vs w02_ramp_slab (pale stone "
               "wedge core) vs w02_connector (flat man-made connector plate); w02_path (walkable dirt) vs "
               "w02_earth (soil band under the grass, sheet swatch 4) vs flower_yellow (flower dots)")

TAU = 2 * math.pi
Z = Vector((0, 0, 1))

# Cross-section of every ramp, in studs from the centreline (u) and the path top.
HALF_PATH = 5.0       # path faces run to here (the grass lip covers the last 0.3)
REF_U = 6.1            # grass cap reference line
CAP_W = 1.4           # cap width inward from the reference line
BULGE = (0.8, 1.2)     # column outer faces stand this far out past the reference line
COL_RN = 1.45         # column radius across the wall
CURTAIN = 1.5         # pale core curtain depth behind the reference line
UNDER = 0.72          # column tops sit this far under the path height (inside the cap)


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------


def v2(x, y):
    return Vector((x, y))


def paint(a, faces, mat, tint=1.0, var=0.0, rng=None):
    mi = a._mi(mat)
    rng = rng or a.rng
    for f in faces:
        f.material_index = mi
        f.smooth = False
        t = tint * (1.0 + rng.uniform(-var, var)) if var else tint
        for lp in f.loops:
            lp[a.tint_layer] = (t, t, t, 1.0)


def face(a, verts, out=None, ref=None):
    """New face; flipped so its normal points along `out` (or away from `ref`)."""
    f = a.bm.faces.new(verts)
    f.normal_update()
    if out is None and ref is not None:
        out = f.calc_center_median() - ref
    if out is not None and f.normal.dot(out) < 0:
        f.normal_flip()
    return f


def hull(a, pts, merge=3.0):
    """Convex hull of pts into the asset; returns its faces (normals outward)."""
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    res = bmesh.ops.convex_hull(bm, input=vs, use_existing_faces=False)
    junk = list({g for g in res["geom_interior"] + res["geom_unused"]
                 if isinstance(g, bmesh.types.BMVert) and g.is_valid})
    if junk:
        bmesh.ops.delete(bm, geom=junk, context="VERTS")
    vs = [v for v in vs if v.is_valid]
    faces = list({f for v in vs for f in v.link_faces})
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    if merge:
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(merge), verts=vs,
                                 edges=list({e for v in vs for e in v.link_edges}))
        vs = [v for v in vs if v.is_valid]
        faces = list({f for v in vs for f in v.link_faces})
    bm.normal_update()
    return faces


def kill(a, faces):
    faces = [f for f in faces if f.is_valid]
    if faces:
        bmesh.ops.delete(a.bm, geom=faces, context="FACES_ONLY")


def sphere_pts(rng, c, r, n=16, squash=0.85, base=None, jit=0.1):
    """Jittered fibonacci sphere (r scalar or (rx, ry, rz)); z floored at base."""
    rx, ry, rz = (r, r, r) if isinstance(r, (int, float)) else r
    ga = math.pi * (3 - math.sqrt(5))
    rot = rng.uniform(0, TAU)
    pts = []
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n
        rr = math.sqrt(max(0.0, 1 - z * z))
        th = rot + ga * i + rng.uniform(-0.25, 0.25)
        k = rng.uniform(1 - jit, 1 + jit)
        p = Vector((c[0] + rr * math.cos(th) * rx * k, c[1] + rr * math.sin(th) * ry * k,
                    c[2] + z * rz * squash * k))
        if base is not None:
            p.z = max(p.z, base)
        pts.append(p)
    return pts


# ---------------------------------------------------------------------------
# centrelines and edges
# ---------------------------------------------------------------------------


class Line:
    """A dense 2D polyline with arc length: at(s) -> (point, unit tangent)."""

    def __init__(self, pts):
        self.p = [Vector(p).to_2d() for p in pts]
        self.s = [0.0]
        for a, b in zip(self.p, self.p[1:]):
            self.s.append(self.s[-1] + (b - a).length)
        self.length = self.s[-1]

    def _seg(self, s):
        s = min(max(s, 0.0), self.length)
        lo, hi = 0, len(self.s) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if self.s[m] <= s:
                lo = m
            else:
                hi = m
        return lo, s

    def at(self, s):
        i, s = self._seg(s)
        a, b = self.p[i], self.p[i + 1]
        L = max(self.s[i + 1] - self.s[i], 1e-9)
        f = (s - self.s[i]) / L
        t = (b - a).normalized()
        # blend the tangent across vertices so curves turn smoothly
        if f < 0.5 and i > 0:
            t0 = (a - self.p[i - 1]).normalized()
            t = (t0 * (0.5 - f) + t * (0.5 + f)).normalized()
        elif f > 0.5 and i + 2 < len(self.p):
            t1 = (self.p[i + 2] - b).normalized()
            t = (t * (1.5 - f) + t1 * (f - 0.5)).normalized()
        return a.lerp(b, f), t


def rib_dz(rib, s):
    """Height offset of the stepped path surface (treads and seam risers) at s."""
    rows = getattr(rib, "rows", None)
    if not rows:
        return 0.0
    for (sa, da), (sb, db) in zip(rows, rows[1:]):
        if sa <= s <= sb:
            f = (s - sa) / max(sb - sa, 1e-6)
            return da + (db - da) * f
    return 0.0


def right(t):
    return v2(t.y, -t.x)


class Ribbon:
    """A path: centreline Line plus height H(s)."""

    def __init__(self, pts, H):
        self.line = Line(pts)
        self.H = H
        self.length = self.line.length

    def at(self, s, u=0.0):
        c, t = self.line.at(s)
        return c + right(t) * u, t

    def p3(self, s, u=0.0, dz=0.0):
        c, _ = self.at(s, u)
        return Vector((c.x, c.y, self.H(s) + dz))

    def edge(self, side, s0=0.0, s1=None, u=REF_U, step=1.1):
        """The grass/rock edge on one side (+1 right of travel, -1 left)."""
        s1 = self.length if s1 is None else s1
        n = max(2, int(round((s1 - s0) / step)))
        pts, nrm = [], []
        for i in range(n + 1):
            s = s0 + (s1 - s0) * i / n
            c, t = self.at(s, side * u)
            pts.append(Vector((c.x, c.y, self.H(s))))
            nrm.append(right(t) * side)
        return Edge(pts, nrm)


class Edge:
    """A polyline at path height with outward normals; s is the xy arc length."""

    def __init__(self, pts, normals):
        self.p = [Vector(p) for p in pts]
        self.n = [Vector(n).normalized() for n in normals]
        self.s = [0.0]
        for a, b in zip(self.p, self.p[1:]):
            self.s.append(self.s[-1] + (b.to_2d() - a.to_2d()).length)
        self.length = self.s[-1]

    def at(self, s):
        s = min(max(s, 0.0), self.length)
        i = 0
        while i < len(self.s) - 2 and self.s[i + 1] < s:
            i += 1
        L = max(self.s[i + 1] - self.s[i], 1e-9)
        f = (s - self.s[i]) / L
        return self.p[i].lerp(self.p[i + 1], f), self.n[i].lerp(self.n[i + 1], f).normalized()

    @staticmethod
    def poly(corners, z, step=1.1):
        """Edge along straight 2D corner points at a constant height; normals point
        to the right of travel, with a diagonal normal on each corner."""
        pts, nrm = [], []
        cs = [Vector(c) for c in corners]
        for k, (a, b) in enumerate(zip(cs, cs[1:])):
            d = b - a
            n = right(d.normalized())
            m = max(1, int(round(d.length / step)))
            for i in range(m + 1):
                if i == 0 and k > 0:
                    nrm[-1] = (nrm[-1] + n).normalized()
                    continue
                pts.append(Vector((a.x + d.x * i / m, a.y + d.y * i / m, z)))
                nrm.append(n)
        return Edge(pts, nrm)


# ---------------------------------------------------------------------------
# the builder
# ---------------------------------------------------------------------------


class Builder:
    def __init__(self, kit, name, seed):
        self.kit = kit
        self.a = kit.flintkit.Asset(name, "Terrain", seed=seed, tint_var=0.03)
        self.rng = random.Random(seed)
        self.nocol = self.a.bm.faces.layers.int.new("kit_nocollide")

    # -- materials ----------------------------------------------------------

    def dressing(self, faces):
        for f in faces:
            if f.is_valid:
                f[self.nocol] = 1

    def rock_tone(self, faces, t=None, rng=None):
        """Per-face tone from a seeded scatter (never from up / sun direction, which
        Roblox lighting adds itself): mostly peach-light and mauve, some cool
        blue-grey; the narrow crevice faces between columns (facing along the
        wall, a real occlusion region) lean cool / deep."""
        rng = rng or self.rng
        for f in faces:
            # ONE rock colour; a small random Tint per face, never by direction
            paint(self.a, [f], ROCK, rng.uniform(0.93, 1.07))

    # -- path -----------------------------------------------------------------

    def path(self, rib, s0, s1, tread=3.4, seam=0.3, drop=0.3, lip_front=True, lip_back=0.0,
             cols=(-HALF_PATH, -2.6, 0.0, 2.6, HALF_PATH), flat_step=2.5):
        """Path surface over [s0, s1]: sloped parts in treads with darker seams,
        flat parts in plain rows. Tonal patches come from per-cell tint."""
        H = rib.H
        rows = []  # (s, dz, cell material for the interval starting here)
        slope = [s0]
        # split at the slope / flat change
        s = s0
        flat_from = None
        probe = s0
        while probe < s1:
            if abs(H(min(probe + 0.5, s1)) - H(probe)) < 1e-4:
                flat_from = probe
                break
            probe += 0.5
        s_slope_end = s1 if flat_from is None else flat_from
        if s_slope_end - s0 > 1.0:
            n = max(1, int(round((s_slope_end - s0) / tread)))
            T = (s_slope_end - s0) / n
            for k in range(n):
                a = s0 + k * T
                rows.append((a, 0.0, "tread"))
                rows.append((a + (T - seam) * 0.5, -drop * 0.5, "tread"))
                rows.append((a + T - seam, -drop, "seam"))
            s = s_slope_end
        if s1 - s > 0.5:
            n = max(1, int(round((s1 - s) / flat_step)))
            for k in range(n):
                rows.append((s + (s1 - s) * k / n, 0.0, "flat"))
        rows.append((s1, 0.0, "end"))
        del slope
        # remember the stepped profile so dressing can sit on it
        rib.rows = [(r[0], r[1]) for r in rows]
        a = self.a
        grid = []
        phase = self.rng.uniform(0, TAU)
        for i, (s, dz, _) in enumerate(rows):
            row = []
            for j, u in enumerate(cols):
                if 0 < j < len(cols) - 1 and 0 < i < len(rows) - 1:
                    u += self.rng.uniform(-0.35, 0.35)
                row.append(a.bm.verts.new(rib.p3(s, u, dz)))
            grid.append(row)
        for i in range(len(rows) - 1):
            kind = rows[i][2]
            for j in range(len(cols) - 1):
                f = face(a, (grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]), out=Z)
                # one path colour: the seams are a steeper riser strip in the
                # geometry (lighting draws the faint cross line), not paint
                sm, sj = rows[i][0], j
                k = 1.04 + 0.05 * math.sin(0.55 * sm + 1.7 * sj + phase) + self.rng.uniform(-0.02, 0.02)
                paint(a, [f], PATH, k)
        if lip_front:
            self._lip(rib, grid[0], s0, 0.0, -1)
        if lip_back:
            self._lip(rib, grid[-1], s1, lip_back, +1)
        return grid

    def _lip(self, rib, row, s, depth, sign):
        """Vertical end face under a path end, down to z - depth (0 = the ground)."""
        a = self.a
        _, t = rib.at(s)
        out = Vector((t.x * sign, t.y * sign, 0))
        low = [a.bm.verts.new((v.co.x, v.co.y, max(0.0, v.co.z - depth) if depth else 0.0)) for v in row]
        for j in range(len(row) - 1):
            if row[j].co.z - low[j].co.z < 0.01 and row[j + 1].co.z - low[j + 1].co.z < 0.01:
                continue
            f = face(a, (row[j], row[j + 1], low[j + 1], low[j]), out=out)
            paint(a, [f], EARTH, 1.0)

    def pad_path(self, x0, x1, y0, y1, z, nx=2, ny=8):
        """Flat rectangular path patch (the switchback landing)."""
        a = self.a
        g = []
        for i in range(ny + 1):
            row = []
            for j in range(nx + 1):
                x = x0 + (x1 - x0) * j / nx
                y = y0 + (y1 - y0) * i / ny
                if 0 < j < nx and 0 < i < ny:
                    x += self.rng.uniform(-0.3, 0.3)
                    y += self.rng.uniform(-0.3, 0.3)
                row.append(a.bm.verts.new((x, y, z)))
            g.append(row)
        phase = self.rng.uniform(0, TAU)
        for i in range(ny):
            for j in range(nx):
                f = face(a, (g[i][j], g[i][j + 1], g[i + 1][j + 1], g[i + 1][j]), out=Z)
                k = 1.06 + 0.05 * math.sin(0.8 * i + 2.1 * j + phase) + self.rng.uniform(-0.025, 0.025)
                paint(a, [f], PATH, k)

    def pebbles(self, spots):
        """Small pale pebbles at (x, y, z) spots."""
        for x, y, z in spots:
            r = self.rng.uniform(0.3, 0.5)
            pts = sphere_pts(self.rng, (x, y, z + r * 0.25), (r * 1.25, r, r), n=8, squash=0.55,
                             base=z - 0.03)
            fs = hull(self.a, pts, merge=0)
            kill(self.a, [f for f in fs if f.normal.z < -0.9])
            fs = [f for f in fs if f.is_valid]
            for f in fs:
                paint(self.a, [f], ROCK, self.rng.uniform(1.0, 1.07))
            self.dressing(fs)

    def path_pebbles(self, rib, s0, s1, count, umax=4.3):
        spots = []
        for i in range(count):
            s = s0 + (s1 - s0) * (i + self.rng.uniform(0.15, 0.85)) / count
            u = self.rng.uniform(-umax, umax)
            p = rib.p3(s, u, rib_dz(rib, s) - 0.04)
            spots.append((p.x, p.y, p.z))
        self.pebbles(spots)

    # -- grass cap ------------------------------------------------------------

    def cap(self, e, scallop=(0.0, 0.45), close=False, light=0.15, cap_w=CAP_W):
        """Grass cap along an edge: a 0.6 grass layer over a 0.4 earth band, the
        inner lip tucked under the path height, the outer lip scalloped."""
        a = self.a
        rng = self.rng
        CAP_W = cap_w
        rings = []
        for i, (p, n) in enumerate(zip(e.p, e.n)):
            n3 = Vector((n.x, n.y, 0))
            z = p.z
            top = z + 0.22
            bot = max(0.0, top - 1.0)
            d = top - bot
            sc = rng.uniform(*scallop)
            if i in (0, len(e.p) - 1):
                sc = sum(scallop) / 2
            drip = rng.uniform(0.85, 1.2)
            gz = max(bot + 0.08 * d, top - 0.6 * d * drip)
            P = Vector((p.x, p.y, 0))
            ring = [
                P - n3 * CAP_W + Vector((0, 0, z - 0.12)),                     # 0 inner bottom
                P - n3 * (CAP_W - 0.18) + Vector((0, 0, z + 0.12)),            # 1 inner top
                P - n3 * (CAP_W * 0.45) + Vector((0, 0, z + 0.3 + rng.uniform(-0.05, 0.06))),  # 2 crown
                P + n3 * (sc - 0.12) + Vector((0, 0, top)),                    # 3 outer top
                P + n3 * sc + Vector((0, 0, gz)),                              # 4 grass lip bottom
                P + n3 * (sc - 0.14) + Vector((0, 0, bot)),                    # 5 earth bottom
                P - n3 * 0.55 + Vector((0, 0, bot)),                           # 6 under
            ]
            if bot <= 0.0:
                ring[0].z = max(ring[0].z, 0.0)
            rings.append([a.bm.verts.new(q) for q in ring])
        # grass faces (inner lip, top, outer lip) share one scatter of light /
        # mid / dark patches and streaks; lighting, not paint, darkens the lips
        nseg = 7 if close else 6
        for i in range(len(rings) - 1):
            r0, r1 = rings[i], rings[i + 1]
            cen = sum((v.co for v in r0 + r1), Vector()) / 14
            for j in range(nseg):
                j1 = (j + 1) % 7
                quad = (r0[j], r0[j1], r1[j1], r1[j])
                if all(q.co.z < 0.005 for q in quad):
                    continue
                f = face(a, quad, ref=cen)
                # one grass colour with small random Tint patches; one earth colour
                m = GRASS if j <= 3 else EARTH
                paint(a, [f], m, rng.uniform(0.94, 1.08) if j <= 3 else rng.uniform(0.97, 1.03))
        # end caps
        for idx, sgn in ((0, -1), (len(rings) - 1, 1)):
            r = rings[idx]
            other = rings[idx + (1 if sgn < 0 else -1)]
            out = sum((v.co for v in r), Vector()) / 7 - sum((v.co for v in other), Vector()) / 7
            f = face(a, r, out=out)
            paint(a, [f], EARTH, 1.0)
        return rings

    # -- rock walls -----------------------------------------------------------

    def column(self, e, sc, hw, zbase=None, poke=0.0, rng=None, s0=0.0, s1=None, bulge=BULGE, calm=False,
               foot=0.5):
        """One tall faceted column under the edge, centred at edge length sc and
        hw half-wide along the wall. Its top follows the edge height (minus
        UNDER), or rises `poke` above the grass. calm=True gives broad, flatter
        faces (fewer, less jittered ring points)."""
        rng = rng or self.rng
        s1 = e.length if s1 is None else s1
        p, n = e.at(sc)
        t = v2(-n.y, n.x)
        C = p.to_2d() - n * (COL_RN - rng.uniform(*bulge))
        zb = zbase(sc) if zbase else 0.0
        # the part standing out past the grass gets a flat stepped top (the
        # front of each column shows above the slope, the back drops under the
        # cap lip); the part under the cap follows the slope
        flat = e.at(sc + hw * 0.6)[0].z - 0.1 + rng.uniform(-0.2, 0.2)

        def top_at(lx, ln=-9.0):
            q, _ = e.at(sc + lx)
            under = q.z - UNDER
            out = (C - p.to_2d()).dot(n) + ln
            if out > 0.05:  # outside the reference line: stepped flat top, rock tip
                if calm:   # calm walls keep a clean sloped rim just under the grass lip
                    return under + 0.45 + poke
                return max(under, flat) + poke
            if out > -0.25:  # the tip's inner face stands at the grass edge
                return under + poke
            return under   # under the grass cap and the path edge

        pts = []
        h = top_at(0.0, 9.0) - zb
        # (height fraction, radius fraction, points, extra outward flare in studs):
        # the walls splay out toward the foot like the sheet's cliffs
        rings = ((0.0, 1.0, 6, foot), (0.42, 0.98, 6, foot * 0.5), (0.78, 0.95, 6, foot * 0.1),
                 (1.2, 0.9, 4, 0.0))
        aj, rlo = (0.1, 0.96) if calm else (0.25, 0.86)
        for fz, fr, cnt, flare in rings:
            rot = rng.uniform(0, TAU)
            if calm:
                cnt = min(cnt, 5)
            for k in range(cnt):
                ang = rot + TAU * k / cnt + rng.uniform(-aj, aj)
                rr = fr * rng.uniform(rlo, 1.04)
                lx = math.cos(ang) * hw * rr
                ln = math.sin(ang) * COL_RN * rr
                if ln > 0:
                    ln += flare * math.sin(ang)
                lx = min(max(lx, s0 - sc), s1 - sc)
                q = C + t * lx + n * ln
                z = zb + fz * h + (rng.uniform(-0.05, 0.05) * h if 0 < fz < 1 else 0.0)
                z = min(z, top_at(lx, ln))
                if fz == 0.0:
                    z = zb
                pts.append(Vector((q.x, q.y, z)))
        fs = hull(self.a, pts, merge=3.0)
        # cull faces that can never be seen: buried bottoms and faces behind the curtain
        dead = []
        for f in fs:
            if f.normal.z < -0.95:
                dead.append(f)
                continue
            if all(-(v.co.to_2d() - p.to_2d()).dot(n) > CURTAIN + 0.05 and v.co.z < p.z - UNDER + 0.02
                   for v in f.verts):
                dead.append(f)
        kill(self.a, dead)
        fs = [f for f in fs if f.is_valid]
        self.rock_tone(fs, t=t, rng=rng)
        return fs

    def shard(self, x, y, h, w, lean=(0.0, 0.0), rng=None, dress=True):
        """Pointed, leaning rock at ground level."""
        rng = rng or self.rng
        pts = []
        rot = rng.uniform(0, TAU)
        for fz, fr, cnt in ((0.0, 1.0, 6), (0.45, 0.8, 5), (0.8, 0.4, 3)):
            for k in range(cnt):
                ang = rot + TAU * k / cnt + rng.uniform(-0.3, 0.3)
                rr = fr * rng.uniform(0.85, 1.1)
                pts.append(Vector((x + math.cos(ang) * w * 0.5 * rr + lean[0] * fz * h,
                                   y + math.sin(ang) * w * 0.42 * rr + lean[1] * fz * h, fz * h)))
        pts.append(Vector((x + lean[0] * h + rng.uniform(-0.1, 0.1) * w, y + lean[1] * h, h)))
        fs = hull(self.a, pts, merge=3.0)
        kill(self.a, [f for f in fs if f.normal.z < -0.95])
        fs = [f for f in fs if f.is_valid]
        self.rock_tone(fs, rng=rng)
        if dress:
            self.dressing(fs)
        return fs

    def boulder(self, x, y, z, s, rng=None):
        """Rounded pale boulder sitting on the grass."""
        rng = rng or self.rng
        pts = sphere_pts(rng, (x, y, z + s * 0.3), (s * 0.55, s * 0.5, s * 0.6), n=11, squash=0.9,
                         base=z - 0.1, jit=0.12)
        fs = hull(self.a, pts, merge=4.0)
        kill(self.a, [f for f in fs if f.normal.z < -0.95])
        fs = [f for f in fs if f.is_valid]
        self.rock_tone(fs, rng=rng)
        self.dressing(fs)
        return fs

    def curtain(self, e, s0=0.0, s1=None, zbase=None, mat=SLAB, depth=CURTAIN, foot=0.0):
        """Pale core face behind the columns: fills the gaps between them and shows
        as the stone wedge where the walls stop at the low end (there its foot
        splays `foot` studs outward, a chamfered plinth that catches the light)."""
        a = self.a
        s1 = e.length if s1 is None else s1
        n = max(1, int(round((s1 - s0) / 2.2)))
        top, bot = [], []
        for i in range(n + 1):
            s = s0 + (s1 - s0) * i / n
            p, nn = e.at(s)
            q = p.to_2d() - nn * depth
            zb = zbase(s) if zbase else 0.0
            top.append(a.bm.verts.new((q.x, q.y, max(zb, p.z - UNDER - 0.05))))
            qb = q + nn * foot
            bot.append(a.bm.verts.new((qb.x, qb.y, zb)))
        for i in range(n):
            if top[i].co.z - bot[i].co.z < 0.02 and top[i + 1].co.z - bot[i + 1].co.z < 0.02:
                continue
            _, nn = e.at(s0 + (s1 - s0) * (i + 0.5) / n)
            f = face(a, (bot[i], bot[i + 1], top[i + 1], top[i]), out=Vector((nn.x, nn.y, 0)))
            paint(a, [f], mat, self.rng.uniform(0.97, 1.03))

    def ledge(self, e, s0, s1, u_in=-0.3, u_out=1.1, cham=0.35, below=0.85):
        """Pale stone (w02_ramp_slab) ledge under the low path edge: a strip whose
        top sits just under the grass cap's earth band, with a chamfered outer
        edge and an outer face down to the ground. It is the ramp wedge showing
        where the rock walls stop."""
        a = self.a
        rows = []
        n_s = max(2, int(round((s1 - s0) / 1.2)))
        for i in range(n_s + 1):
            s = s0 + (s1 - s0) * i / n_s
            p, n = e.at(s)
            zt = max(0.12, p.z - below)
            P = p.to_2d()
            cz = min(cham, zt * 0.5)
            ring = [P + n * u_in, P + n * (u_out - cham), P + n * u_out, P + n * (u_out + 0.12)]
            zs = [zt, zt, zt - cz, 0.0]
            rows.append([a.bm.verts.new((q.x, q.y, z)) for q, z in zip(ring, zs)])
        cen = None
        out = []
        for i in range(n_s):
            r0, r1 = rows[i], rows[i + 1]
            _, n = e.at(s0 + (s1 - s0) * (i + 0.5) / n_s)
            outs = (Z, (Vector((n.x, n.y, 0)) + Z).normalized(), Vector((n.x, n.y, 0)))
            for j in range(3):
                f = face(a, (r0[j], r0[j + 1], r1[j + 1], r1[j]), out=outs[j])
                out.append(f)
        # end faces (the inner side stays open: it is under the cap / path)
        for r, other in ((rows[0], rows[1]), (rows[-1], rows[-2])):
            tt = r[0].co - other[0].co
            tt.z = 0.0
            low_in = a.bm.verts.new((r[0].co.x, r[0].co.y, 0.0))
            out.append(face(a, (r[0], r[1], r[2], r[3], low_in), out=tt))
        for f in out:
            paint(a, [f], SLAB, self.rng.uniform(0.98, 1.04))
        return out

    def wall(self, e, s0=0.0, s1=None, zbase=None, poke=0.0, poke_from=6.0, wr=(3.0, 5.2),
             shards=True, seed=0, curtain=True, poke_n=3, poke_step=2, bulge=BULGE, calm=False, foot=0.5):
        """A row of columns along the edge; low stretches become shards in front of
        the pale wedge stone. Up to poke_n columns (every poke_step-th one from the
        high end, above poke_from) rise `poke` above the grass as rock tips."""
        rng = random.Random(seed)
        s1 = e.length if s1 is None else s1
        s = s0
        plan = []  # (s, w, sc, is_column)
        while s < s1 - 0.6:
            w = rng.uniform(*wr)
            if s1 - (s + w) < 1.6:
                w = s1 - s
            sc = s + w / 2
            p, n = e.at(sc)
            zb = zbase(sc) if zbase else 0.0
            plan.append((s, w, sc, p.z - UNDER - zb >= 2.8, p.z))
            s += w - rng.uniform(0.5, 0.9)
        cand = [i for i, c in enumerate(plan) if c[3] and c[4] > poke_from]
        cand.sort(key=lambda i: -plan[i][4])
        pokers = set(cand[::poke_step][:poke_n]) if poke else set()
        for i, (s, w, sc, is_col, pz) in enumerate(plan):
            zb = zbase(sc) if zbase else 0.0
            if not is_col:
                if shards and zb <= 0.0:
                    # the pale stone wedge core shows as a chamfered ledge under the
                    # low path edge, with a shard standing on it at its high end
                    self.ledge(e, max(s0, s - 0.3), min(s1, s + w + 0.3))
                    self.low_rocks(e, s, s + w, rng)
            else:
                # tips grow with the slope: the high end pokes up the most
                pk = poke * rng.uniform(0.75, 1.0) * min(1.0, 0.45 + pz / 14.0) if i in pokers else 0.0
                self.column(e, sc, w * 0.5 + 0.35, zbase=zbase, poke=pk, rng=rng, s0=s0, s1=s1,
                            bulge=bulge, calm=calm, foot=foot)
        if curtain:
            self.curtain(e, s0, s1, zbase)

    def low_rocks(self, e, sa, sb, rng):
        """The wall's low end: one or two pointed shards and a ground bush."""
        sm = (sa + sb) / 2
        # one shard at the high end of the stretch, in front of the pale stone (which
        # stands 0.2 outside the reference line), so the stone shows below the lip
        # between it and the front-corner bush
        p, n = e.at(max(sm, sb - 0.6))
        t = v2(-n.y, n.x)
        q = p.to_2d() + n * 0.9
        h = max(1.2, min(2.6, p.z * 0.6 + 0.6)) * rng.uniform(0.9, 1.1)
        self.shard(q.x, q.y, h, rng.uniform(1.2, 1.6), lean=(n.x * 0.15, n.y * 0.15), rng=rng)
        if sb - sa > 6.0:
            q2 = q - t * (sb - sa) * 0.45 - n * 0.05
            self.shard(q2.x, q2.y, h * 0.65, rng.uniform(1.0, 1.4), lean=(n.x * 0.2, n.y * 0.2), rng=rng)

    # -- greenery -------------------------------------------------------------

    def bush(self, x, y, z, r, rng=None, lobes=3):
        """Round leafy clump: a domed main lobe plus side lobes."""
        rng = rng or self.rng
        a = self.a
        out = []
        spec = [(0.0, 0.0, 1.0, 0.75)]
        rot = rng.uniform(0, TAU)
        for k in range(lobes - 1):
            ang = rot + TAU * k / (lobes - 1) + rng.uniform(-0.4, 0.4)
            spec.append((math.cos(ang) * r * 0.72, math.sin(ang) * r * 0.72, rng.uniform(0.6, 0.75), 0.5))
        for dx, dy, fr, hz in spec:
            rr = r * fr
            pts = sphere_pts(rng, (x + dx, y + dy, z + rr * hz), rr, n=16 if fr == 1.0 else 12,
                             squash=0.88, base=z, jit=0.12)
            fs = hull(a, pts, merge=0)
            dead = [f for f in fs if f.normal.z < -0.9 and f.calc_center_median().z < z + 0.05]
            kill(a, dead)
            fs = [f for f in fs if f.is_valid]
            for f in fs:  # one leaf colour; the light falls on the dome by itself
                paint(a, [f], BUSH, rng.uniform(0.93, 1.07))
            out += fs
        self.dressing(out)
        return out

    def flowers(self, x, y, z, rng=None, n=3, yellow=0.3):
        rng = rng or self.rng
        out = []
        base = rng.uniform(0, TAU)
        for k in range(n):
            # a tight cluster of 0.7-0.8 wide dots, legible at cell size
            ang = base + TAU * k / n + rng.uniform(-0.3, 0.3)
            px = x + math.cos(ang) * 0.42
            py = y + math.sin(ang) * 0.42
            vs = self.a.cyl(0.38, 0.3, 0.2, sides=5, loc=(px, py, z), rot=(0, 0, rng.uniform(0, TAU)),
                            mat="flower_yellow" if rng.random() < yellow else "flower_white", tint=1.0)
            out += kit_faces(vs)
        bot = [f for f in out if f.normal.z < -0.9]
        kill(self.a, bot)
        self.dressing(out)

    def dress_cap(self, e, s0=0.0, s1=None, bushes=5, flowers=8, boulders=0, pebbles=2, seed=0,
                  bush_r=(0.9, 1.2), min_z=-1.0, cap_w=CAP_W):
        """Bushes, flower dots, pebbles and boulders spread along a grass cap
        (depths are fractions of the cap width, measured in from its outer line)."""
        rng = random.Random(seed)
        s1 = e.length if s1 is None else s1
        L = s1 - s0

        def spot(frac, depth):
            p, n = e.at(s0 + L * frac)
            q = p.to_2d() - n * depth * cap_w
            return q, p.z

        for i in range(bushes):
            f = (i + rng.uniform(0.25, 0.75)) / bushes
            q, z = spot(f, rng.uniform(0.5, 0.65))
            if z < min_z:
                continue
            self.bush(q.x, q.y, z + 0.22, rng.uniform(*bush_r), rng=rng, lobes=rng.choice((3, 3, 4)))
        for i in range(flowers):
            f = (i + rng.uniform(0.1, 0.9)) / flowers
            q, z = spot(f, rng.uniform(0.25, 0.7))
            self.flowers(q.x, q.y, z + 0.26, rng=rng, n=3)
        for i in range(boulders):
            f = (i + rng.uniform(0.3, 0.7)) / boulders
            q, z = spot(f, rng.uniform(0.35, 0.5))
            self.boulder(q.x, q.y, z + 0.2, rng.uniform(1.2, 1.7), rng=rng)
        spots = []
        for i in range(pebbles):
            f = rng.uniform(0.05, 0.95)
            q, z = spot(f, rng.uniform(0.4, 0.9))
            spots.append((q.x, q.y, z + 0.22))
        self.pebbles(spots)

    # -- connector ------------------------------------------------------------

    def end_plate(self, rib, s, ztop, half=7.0, tabs=True):
        """Flat grey connector plate across a ribbon end (outer face 0.4 past s),
        with 1.5 x 0.5 x 0.4 tabs on its vertical edges every 8 studs."""
        c, t = rib.at(s)
        n = right(t)
        yaw = math.atan2(t.y, t.x) - math.pi / 2
        mid = c + t * 0.2
        vs = self.a.box((half * 2, 0.4, ztop), loc=(mid.x, mid.y, ztop / 2), rot=(0, 0, yaw), mat=CONN,
                        tint=1.0)
        fs = kit_faces(vs)
        kill(self.a, [f for f in fs if f.normal.z < -0.9])
        if tabs:
            z = 2.0
            while z + 0.75 < ztop:
                for sgn in (-1, 1):
                    q = mid + n * sgn * (half + 0.25)
                    vt = self.a.box((0.5, 0.4, 1.5), loc=(q.x, q.y, z), rot=(0, 0, yaw), mat=CONN, tint=0.92)
                z += 8.0

    def side_plate(self, profile, y0, tabs_at=()):
        """Flat grey plate in the XZ plane (outer face at y0, 0.4 thick, toward -Y);
        profile is its (x, z) outline, counter-clockwise seen from +Y."""
        vs = self.a.poly_prism(profile, 0.4, loc=(0, y0, 0), rot=(math.pi / 2, 0, 0), mat=CONN, tint=1.0)
        kill(self.a, [f for f in kit_faces(vs) if f.normal.z < -0.9])
        for x, z in tabs_at:
            self.a.box((0.5, 0.4, 1.5), loc=(x, y0 - 0.2, z), mat=CONN, tint=0.92)

    # -- output ---------------------------------------------------------------

    def finish(self, role, collision, budget, notes="", mirror_x=False):
        a = self.a
        if mirror_x:
            for v in a.bm.verts:
                v.co.x = -v.co.x
            bmesh.ops.reverse_faces(a.bm, faces=list(a.bm.faces))
        for v in a.bm.verts:
            if v.co.z < 0.0:
                v.co.z = 0.0
        a.bm.normal_update()
        dead = [f for f in a.bm.faces if f.normal.z < -0.97 and f.calc_center_median().z < 0.03]
        kill(a, dead)
        loose = [v for v in a.bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(a.bm, geom=loose, context="VERTS")
        obj = a.finish()
        if self.a.mats and EARTH in self.a.mats:
            # The shading check groups w02_earth with w02_path / grass (close hues). The earth
            # band under the grass and on the pad and path-end sides is a real soil
            # layer from the sheet palette, not painted light; every other
            # material is toned by a seeded scatter.
            obj["kit_shading_ok"] = ("w02_earth soil band under the grass caps / pad sides is a real "
                                     "material layer (sheet swatch 4), grouped with w02_path by hue")
        obj["kit_two_tone_ok"] = TWO_TONE_OK
        return self.kit.tag(obj, role, collision=collision, budget=budget, notes=notes)


def kit_faces(verts):
    return list({f for v in verts for f in v.link_faces})


# ---------------------------------------------------------------------------
# assemblies
# ---------------------------------------------------------------------------


#: Wall settings per side, (-X, +X). The -X wall faces the runner's front-left
#: iso camera, so it is the tall feature wall: broad columns that bulge past the
#: grass lip and rise above it toward the high end. The +X wall (the side cell)
#: has broad, calmer faces that read as one big rock face side-on.
FEATURE_WALLS = (dict(poke=2.45, poke_from=4.0, poke_n=8, poke_step=1, wr=(4.0, 5.6), bulge=(1.05, 1.45),
                      foot=1.0),
                 dict(poke=0.0, wr=(5.0, 6.5), bulge=(1.2, 1.45), calm=True, foot=0.9))


def straight_ramp(b, length, rise_len, seed, end=True, walls=FEATURE_WALLS, bushes=6, flowers=8,
                  boulders=(1, 2), pebbles=8, side_plate=False):
    """A straight ribbon from y=-length/2: slope over rise_len to 12, then flat.
    side_plate: the +X side of the flat landing is a flat grey connector face
    (the landing joins level-12 terrain sideways) instead of rock columns."""
    L = length - 0.4 if end else length
    y0 = -length / 2

    def H(s):
        return 0.25 + 11.75 * min(s, rise_len) / rise_len

    rib = Ribbon([(0, y0), (0, y0 + L)], H)
    b.path(rib, 0.0, L)
    for k, side in enumerate((-1, 1)):
        e = rib.edge(side, 0.0, L)
        b.cap(e)
        if side > 0 and side_plate and L - rise_len > 1.0:
            e_slope = rib.edge(side, 0.0, rise_len)
            b.wall(e_slope, seed=seed + 10 * k, **walls[k])
            # flat grey connector face under the landing's grass lip, 0.4 thick
            # (its front edge meets the last column; the rear plate carries the tabs)
            x_out = REF_U + 0.1
            ya, yb = y0 + rise_len, y0 + L
            ztop = 12.25 - 0.95
            b.a.box((0.4, yb - ya, ztop), loc=(x_out - 0.2, (ya + yb) / 2, ztop / 2), mat=CONN, tint=1.0)
        else:
            b.wall(e, seed=seed + 10 * k, **walls[k])
        b.dress_cap(e, bushes=bushes, flowers=flowers, boulders=boulders[k], seed=seed + 20 + k)
        # ground bushes and a tuft at the low corner, by the shards
        p, n = e.at(0.7)
        q = p.to_2d() + n * 0.4
        b.bush(q.x, q.y, 0.0, 0.8, lobes=3)
        b.flowers(q.x + n.x * 0.9, q.y - 0.6, 0.0, n=3)
    if end:
        b.end_plate(rib, L, 11.5)
    b.path_pebbles(rib, 1.5, min(L, rise_len + 6) - 1.0, pebbles)
    return rib


def build_hero(kit):
    b = Builder(kit, "NaturalRamp", 301)
    straight_ramp(b, 32.0, 24.0, 3010, bushes=5, flowers=8, boulders=(1, 2), pebbles=8, side_plate=True)
    return b.finish("hero", "precise", 6000,
                    "walkable 26 deg ramp from 0 to 12 plus an 8-deep landing at 12; grey connector "
                    "plate on +Y; dressing faces carry kit_nocollide=1")


def build_straight(kit):
    b = Builder(kit, "NaturalRampStraight", 311)
    walls = (dict(FEATURE_WALLS[0], poke=1.4, poke_n=3, poke_step=2, poke_from=7.0), dict(FEATURE_WALLS[1], poke=0.0))
    straight_ramp(b, 48.0, 47.6, 3110, walls=walls, bushes=7, flowers=8, boulders=(1, 1),
                  pebbles=10)
    return b.finish("variant", "precise", 5000,
                    "long gentle 14 deg run from 0 to 12, no landing; connector plate on +Y")


def build_curved(kit):
    b = Builder(kit, "NaturalRampCurved", 321)
    R = 20.0
    cx, cy = -12.0, 12.0
    # as on the sheet: starts low at the front-left heading +X, then bends left
    # around a centre at the back-left to climb toward +Y; the outer wall (right of
    # travel) faces the viewer and the connector plate ends the high end on +Y
    pts = [(-16.0, cy - R)]
    for i in range(0, 31):
        a = -math.pi / 2 + (math.pi / 2) * i / 30
        pts.append((cx + R * math.cos(a), cy + R * math.sin(a)))
    pts.append((cx + R, 16.0 - 0.4))
    line = Line(pts)
    L = line.length

    def H(s):
        return 0.25 + 11.75 * s / (L + 0.4)

    rib = Ribbon(pts, H)
    b.path(rib, 0.0, L)
    # right of travel is the outer side: a taller rim with column tips above the grass
    eo = rib.edge(1, 0.0, L, step=1.15)
    b.cap(eo)
    b.wall(eo, poke=3.0, poke_from=2.5, seed=3201, wr=(3.0, 4.6), poke_n=9, poke_step=1)
    b.dress_cap(eo, bushes=7, flowers=10, boulders=1, seed=3202)
    ei = rib.edge(-1, 0.0, L, step=1.0)
    b.cap(ei)
    b.wall(ei, seed=3203, wr=(2.8, 4.2))
    b.dress_cap(ei, bushes=5, flowers=7, boulders=1, seed=3204)
    for e in (eo, ei):
        p, n = e.at(1.0)
        q = p.to_2d() - n * 0.4
        b.bush(q.x, q.y, 0.0, 0.7)
    b.end_plate(rib, L, 11.5)
    b.path_pebbles(rib, 1.5, L - 1.5, 9)
    return b.finish("variant", "precise", 7000,
                    "90 deg arc ramp from 0 to 12 (centreline radius 20); connector plate on the high end (+Y)")


def build_switchback(kit):
    b = Builder(kit, "NaturalRampSwitchback", 331)

    def H1(s):
        return 0.25 + 11.75 * s / 24.0

    def H2(s):
        return 12.0 + 12.0 * s / 24.0

    f1 = Ribbon([(-16.0, -8.0), (8.0, -8.0)], H1)      # front flight, rising toward +X
    f2 = Ribbon([(8.0, 8.0), (-16.0, 8.0)], H2)        # back flight, rising toward -X
    b.path(f1, 0.0, 24.0)
    b.path(f2, 0.0, 24.0, lip_front=False, lip_back=0.8)
    # U-turn landing at 12
    o = 8.0 - REF_U  # outline to reference line
    b.pad_path(8.0, 16.0 - o - CAP_W + 0.2, -16.0 + o + CAP_W - 0.2, 16.0 - o - CAP_W + 0.2, 12.0,
               nx=2, ny=8)

    # front flight: front wall (right of travel), tucked cap against the upper wall (left)
    e1 = f1.edge(1)
    b.cap(e1)
    b.wall(e1, seed=3301, poke=2.2, poke_from=4.0, poke_n=4, poke_step=1, bulge=(1.0, 1.4))
    b.dress_cap(e1, bushes=5, flowers=7, boulders=1, seed=3302)
    e5 = f1.edge(-1)
    # the tucked cap reaches across the gap to the foot of the slim middle wall
    b.cap(e5, scallop=(2.2, 2.2), light=0.2)
    b.dress_cap(e5, bushes=3, flowers=5, seed=3303, min_z=2.0)

    # landing: front, right and back edges in one cap
    el = Edge.poly([(8.0, -16 + o), (16 - o, -16 + o), (16 - o, 16 - o), (8.0, 16 - o)], 12.0)
    b.cap(el, scallop=(0.3, 0.75))
    front_right = el.length - (8.0 - o)
    b.wall(el, 0.0, front_right, seed=3304, poke=2.0, poke_from=4.0, poke_n=4, poke_step=2, bulge=(1.0, 1.4))
    b.dress_cap(el, 0.0, front_right, bushes=4, flowers=7, boulders=1, seed=3305)

    # back flight: back edge over the connector plate, front edge on a tall rock wall
    e3 = f2.edge(1)
    b.cap(e3, scallop=(0.85, 1.0))
    b.dress_cap(e3, bushes=3, flowers=6, seed=3306)
    e4 = f2.edge(-1)
    b.cap(e4)

    def zb4(s):  # the wall stands on the front flight's tucked cap
        return max(0.0, H1(24.0 - s) - 0.85)

    # slim middle wall: narrow columns whose tips rise above the back flight's grass
    b.wall(e4, zbase=zb4, shards=False, seed=3307, wr=(3.0, 4.2), poke=2.0, poke_from=13.0, poke_n=4,
           poke_step=1, bulge=(0.7, 1.0))
    b.dress_cap(e4, bushes=4, flowers=6, boulders=1, seed=3308)
    # the high end (x = -16) drops to the ground as a rock face under the path end
    eend = Edge.poly([(-16 + 1.4, 8.0 + REF_U - 0.3), (-16 + 1.4, 8.0 - REF_U + 0.3)], 24.0)
    b.wall(eend, seed=3309, wr=(3.4, 4.8))

    # back connector plate under the back flight and the landing
    top_r = 12.0 - 0.8
    prof = [(15.5, 0.0), (15.5, top_r), (8.0, top_r), (-15.5, H2(23.5) - 0.8), (-15.5, 0.0)]
    tabs = [(15.5 + 0.25, 2.0), (15.5 + 0.25, 10.0)] + [(-15.5 - 0.25, z) for z in (2.0, 10.0, 18.0)]
    b.side_plate(prof, 16.0, tabs)

    # front corner: ground bush at the low end
    b.bush(-15.0, -15.2, 0.0, 0.75)
    b.path_pebbles(f1, 1.5, 22.5, 6)
    b.path_pebbles(f2, 1.5, 22.5, 5)
    # built rising toward +X and mirrored, so the front flight climbs toward -X, the
    # U-turn landing sits on the left and the back flight climbs back toward +X:
    # from the sheet's front-left view both flights face the viewer
    return b.finish("variant", "precise", 8000,
                    "two flights (0 to 12 along the front, 12 to 24 along the back) and a flat U-turn landing "
                    "at 12; connector plate on +Y", mirror_x=True)


# ---------------------------------------------------------------------------
# parts
# ---------------------------------------------------------------------------


def build_border(kit):
    b = Builder(kit, "NaturalRampGrassBorder", 341)
    z0 = 0.78
    e = Edge([Vector((1.0, -12.0 + 24.0 * i / 22, z0 + 12.0 * i / 22)) for i in range(23)],
             [v2(1, 0)] * 23)
    b.cap(e, close=True, cap_w=2.2)
    b.dress_cap(e, bushes=5, flowers=8, boulders=1, pebbles=3, seed=3410, cap_w=2.2)
    return b.finish("part", "none", 1500,
                    "one side grass strip (grass over an earth band) for the ramp edge; decoration only, "
                    "the ramp carries the collision")


def slab(b, x0, x1, y0, y1, z0, z1, nx=4, ny=3, cham=0.18):
    """Box with a gridded, tinted top, a chamfer band and plain sides (no bottom)."""
    a = b.a
    rng = b.rng
    top = []
    for i in range(ny + 1):
        row = []
        for j in range(nx + 1):
            x = x0 + cham + (x1 - x0 - 2 * cham) * j / nx
            y = y0 + cham + (y1 - y0 - 2 * cham) * i / ny
            if 0 < i < ny and 0 < j < nx:
                x += rng.uniform(-0.3, 0.3)
                y += rng.uniform(-0.3, 0.3)
            row.append(a.bm.verts.new((x, y, z1)))
        top.append(row)
    for i in range(ny):
        for j in range(nx):
            f = face(a, (top[i][j], top[i][j + 1], top[i + 1][j + 1], top[i + 1][j]), out=Z)
            k = 1.0 + 0.03 * math.sin(1.3 * i + 2.2 * j) + rng.uniform(-0.02, 0.02)
            # tonal dirt patches: a small Tint dip on two cells, one path colour
            paint(a, [f], PATH, k * (0.93 if (i, j) in ((1, 1), (0, 3)) else 1.02))
    # boundary loop of the top grid, counter-clockwise
    loop = [top[0][j] for j in range(nx + 1)] + [top[i][nx] for i in range(1, ny + 1)]
    loop += [top[ny][j] for j in range(nx - 1, -1, -1)] + [top[i][0] for i in range(ny - 1, 0, -1)]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    ring, bot = [], []
    for v in loop:
        x = x0 if v.co.x < cx - (x1 - x0) / 2 + cham + 0.01 else (x1 if v.co.x > cx + (x1 - x0) / 2 - cham - 0.01 else v.co.x)
        y = y0 if v.co.y < cy - (y1 - y0) / 2 + cham + 0.01 else (y1 if v.co.y > cy + (y1 - y0) / 2 - cham - 0.01 else v.co.y)
        ring.append(a.bm.verts.new((x, y, z1 - cham)))
        bot.append(a.bm.verts.new((x, y, z0)))
    c = Vector((cx, cy, (z0 + z1) / 2))
    m = len(loop)
    for k in range(m):
        k1 = (k + 1) % m
        f = face(a, (loop[k], loop[k1], ring[k1], ring[k]), ref=c)
        paint(a, [f], PATH, rng.uniform(0.96, 1.04))
        f = face(a, (ring[k], ring[k1], bot[k1], bot[k]), ref=c)
        paint(a, [f], EARTH, rng.uniform(0.9, 1.06))


def build_pad(kit):
    b = Builder(kit, "NaturalRampTopLandingPad", 351)
    slab(b, -5.0, 5.0, -4.0, 4.0, 0.0, 1.5)
    b.pebbles([(-1.2, 0.6, 1.47), (2.1, -1.6, 1.47)])
    # a grass tuft and a small bush on the back corners, as on the sheet
    b.bush(3.9, 3.0, 1.45, 0.6, lobes=2)
    b.flowers(-4.1, 3.2, 1.5, n=2)
    return b.finish("part", "box", 800, "flat dirt landing pad that tops the ramp at 12")


def build_wedge(kit):
    b = Builder(kit, "NaturalRampWedge", 361)
    c = 0.5
    # profile in (y, z): front tip, back foot, back top; inset copy for the chamfer
    prof = [(-12.0, 0.0), (12.0, 0.0), (12.0, 12.0)]
    ins = inset_tri(prof, c)
    pts = []
    for x, pr in ((5.0 - c, prof), (5.0, ins)):
        for sx in (-1, 1):
            for y, z in pr:
                pts.append(Vector((sx * x, y, z)))
    fs = hull(b.a, pts, merge=1.0)
    for f in fs:
        n = f.normal
        paint(b.a, [f], SLAB, b.rng.uniform(0.98, 1.03))
    kill(b.a, [f for f in fs if f.normal.z < -0.95])
    # one crack seam running up the slope from the front
    nrm = Vector((0, -1, 2)).normalized()
    crack = [(-1.6, -9.5), (-0.7, -7.2), (-1.3, -5.0), (-0.2, -2.6), (-0.6, -1.0)]
    for (xa, ya), (xb, yb) in zip(crack, crack[1:]):
        pa = Vector((xa, ya, (ya + 12) / 2)) + nrm * 0.03
        pb = Vector((xb, yb, (yb + 12) / 2)) + nrm * 0.03
        d = (pb - pa).normalized()
        # a thin, steep-sided crack ridge in the same stone: its sides catch the
        # light differently from the slope, so the lighting draws the line
        sd = d.cross(nrm).normalized() * 0.16
        up = nrm * 0.26
        vs = [b.a.bm.verts.new(p) for p in (pa - sd - nrm * 0.03, pa + up, pb + up, pb - sd - nrm * 0.03,
                                            pa + sd - nrm * 0.03, pb + sd - nrm * 0.03)]
        f1 = face(b.a, (vs[0], vs[1], vs[2], vs[3]), out=nrm - sd)
        f2 = face(b.a, (vs[4], vs[5], vs[2], vs[1]), out=nrm + sd)
        paint(b.a, [f1, f2], SLAB, 1.0)
    return b.finish("part", "hull", 300, "pale stone ramp core, 10 x 24 rising from 0 to 12")


def inset_tri(pts, d):
    """Offset a CCW triangle (2D) inward by d."""
    P = [Vector(p) for p in pts]
    lines = []
    for i in range(3):
        a, b = P[i], P[(i + 1) % 3]
        t = (b - a).normalized()
        n = Vector((-t.y, t.x))  # inward for CCW
        lines.append((a + n * d, t))
    out = []
    for i in range(3):
        (p1, t1), (p2, t2) = lines[i - 1], lines[i]
        den = t1.x * t2.y - t1.y * t2.x
        k = ((p2.x - p1.x) * t2.y - (p2.y - p1.y) * t2.x) / den
        q = p1 + t1 * k
        out.append((q.x, q.y))
    return out


def build(kit):
    return [build_hero(kit), build_straight(kit), build_curved(kit), build_switchback(kit),
            build_border(kit), build_pad(kit), build_wedge(kit)]
