"""W02 row 4: NATURAL ARCH AND CAVE MOUTH, "open rock hole through terrain".

A terrain chunk with a big round-arched hole through its full depth: a Left
and a Right Rock Mass of tall vertical columnar facets (jittered convex hulls)
carry a Top Span whose underside is a ring of big flat facets around the
opening. Pointed shard rocks and boulders stand at the feet; the shared W02
grass cap (scalloped lip over an earth band, slightly domed) crowns the top
with a heavy ring of leafy bush clumps, some hanging over the arch face. A tan
dirt apron fans out of the opening over a pale stone sill, and a flat grey
connector plate with tabs covers the back (and the rear of the +X side, as the
reference's side/rear view shows), cut around the hole so it stays open.

Every rock hull is kept outside the opening by construction: the opening is a
convex polygon (two walls and the arch facets), and each hull's points are
projected into the outer half-plane of one of its edges, so no hull can ever
intrude into the walkable hole.

Assets: NaturalArch (hero); NaturalArchLeftRockMass, NaturalArchRightRockMass,
NaturalArchTopSpan, NaturalArchGroundSill (parts); NaturalArchNarrow,
NaturalArchWide, NaturalArchBroken (variants). No VFX: an open arch implies no
glow, mist or fire.
"""

import math
import random

import bmesh
from mathutils import Vector, geometry

SUBJECT = "NaturalArch"
ROW = 4
# The W02 sheet palette, copied verbatim so every W02 module paints one terrain.
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
}

ROCK, LIGHT, COOL, DEEP = "w02_rock", "w02_rock_light", "w02_rock_cool", "w02_rock_deep"
GRASS, GRASS_L, GRASS_D, EARTH = "w02_grass", "w02_grass_light", "w02_grass_dark", "w02_earth"
PATH, PATH_D, SLAB, CONN = "w02_path", "w02_path_dark", "w02_slab", "w02_connector"
BUSH, BUSH_L, BUSH_D = "w02_bush", "w02_bush_light", "w02_bush_dark"
# one base colour per material: SKIN for every outer rock face (its lit
# mid-tone), SOFFIT for the cool stone lining the arch, LEAF for every clump
SKIN, SOFFIT, LEAF = ROCK, COOL, BUSH
Z = Vector((0, 0, 1))
TAU = 2 * math.pi


# ---------------------------------------------------------------------------
# mesh helpers
# ---------------------------------------------------------------------------


def paint(a, faces, mat, tint=1.0, var=0.04):
    mi = a._mi(mat)
    for f in faces:
        f.material_index = mi
        f.smooth = False
        t = tint * (1.0 + a.rng.uniform(-var, var))
        for lp in f.loops:
            lp[a.tint_layer] = (t, t, t, 1.0)


class Piece:
    """A convex chunk: its faces and bounding planes (for the hidden-face cull)."""

    def __init__(self, faces, kind):
        self.faces = faces
        self.kind = kind
        self.planes = [(f.normal.copy(), f.calc_center_median()) for f in faces if f.is_valid]
        if len(self.planes) < 4:      # a flat (degenerate) hull bounds no volume
            self.kind = "flat"

    def contains(self, p, eps=0.02):
        return all(n.dot(p - c) < -eps for n, c in self.planes)


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


def cull_hidden(a, pieces):
    """Delete faces buried entirely inside another rock chunk."""
    rocks = [p for p in pieces if p.kind == "rock"]
    dead = set()
    for p in pieces:
        for f in p.faces:
            if not f.is_valid:
                continue
            for q in rocks:
                if q is p:
                    continue
                if all(q.contains(v.co) for v in f.verts):
                    dead.add(f)
                    break
    if dead:
        bmesh.ops.delete(a.bm, geom=list(dead), context="FACES_ONLY")
        loose = [v for v in a.bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(a.bm, geom=loose, context="VERTS")


def drop_bottoms(a):
    """Remove ground-contact faces (never seen) and clamp anything below z=0."""
    for v in a.bm.verts:
        if v.co.z < 0.0:
            v.co.z = 0.0
    a.bm.normal_update()
    dead = [f for f in a.bm.faces if f.normal.z < -0.97 and f.calc_center_median().z < 0.03]
    if dead:
        bmesh.ops.delete(a.bm, geom=dead, context="FACES_ONLY")
        loose = [v for v in a.bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(a.bm, geom=loose, context="VERTS")


# ---------------------------------------------------------------------------
# the opening: a convex polygon in XZ (two walls + arch facets)
# ---------------------------------------------------------------------------


class Opening:
    """Hole of half width w2, walls up to the spring line s, then an elliptic
    arch of height rz drawn as flat facets at the given angles (degrees, 180 ->
    0). Half-planes are (nx, nz, d): a point is outside the hole across that
    edge when nx*x + nz*z >= d."""

    def __init__(self, w2, s, rz, angles, cx=0.0):
        self.w2, self.s, self.rz, self.cx = w2, s, rz, cx
        self.top = s + rz
        self.arc = [(cx + w2 * math.cos(math.radians(t)), s + rz * math.sin(math.radians(t))) for t in angles]
        self.left = (-1.0, 0.0, -(cx - w2))   # x <= cx - w2
        self.right = (1.0, 0.0, cx + w2)      # x >= cx + w2
        self.facets = []
        for (x0, z0), (x1, z1) in zip(self.arc, self.arc[1:]):
            nx, nz = -(z1 - z0), (x1 - x0)
            L = math.hypot(nx, nz)
            nx, nz = nx / L, nz / L
            self.facets.append(((x0, z0), (x1, z1), (nx, nz, nx * x0 + nz * z0)))

    def planes(self):
        return [self.left, self.right] + [f[2] for f in self.facets]

    def inside(self, x, z, pad=0.0):
        if z < -pad:
            return False
        return all(nx * x + nz * z < d + pad for nx, nz, d in self.planes())

    def outline(self, grow=0.0):
        """Closed XZ outline of the hole (for the connector cut-out), grown."""
        pts = [(self.cx - self.w2 - grow, 0.0)]
        for x, z in self.arc:
            dx, dz = x - self.cx, z - self.s
            L = math.hypot(dx, dz) or 1.0
            pts.append((x + dx / L * grow, z + dz / L * grow))
        pts.append((self.cx + self.w2 + grow, 0.0))
        return pts


def project(p, planes, it=4):
    """Push an XZ point into the intersection of half-planes (alternating)."""
    x, z = p.x, p.z
    for _ in range(it):
        ok = True
        for nx, nz, d in planes:
            s = nx * x + nz * z - d
            if s < 0:
                x -= s * nx
                z -= s * nz
                ok = False
        if ok:
            break
    p.x, p.z = x, z
    return p


def shift_plane(pl, off):
    nx, nz, d = pl
    return (nx, nz, d + off)


# ---------------------------------------------------------------------------
# point clouds
# ---------------------------------------------------------------------------


def col_pts(rng, cx, cy, rx, ry, h, n=5, rings=((0.0, 1.0), (0.5, 0.94), (0.88, 0.86)),
            point=0.0, slant=0.5, lean=(0.0, 0.0), z0=0.0):
    """Tall faceted column: jittered rings up to height h with a slanted flat
    top (slant studs of tilt), or a pinched pointed top when point > 0."""
    # one set of corner angles for every ring, so the column keeps long straight
    # vertical edges and big flat faces (a prism, not a twisted blob)
    rot = rng.uniform(0, TAU)
    angs = [rot + TAU * k / n + rng.uniform(-0.3, 0.3) for k in range(n)]
    rads = [rng.uniform(0.85, 1.1) for _ in range(n)]
    pts = []
    for fz, fr in rings:
        z = z0 + fz * (h - z0)
        ox, oy = lean[0] * (z - z0), lean[1] * (z - z0)
        for ang, r0 in zip(angs, rads):
            a2 = ang + rng.uniform(-0.05, 0.05)
            rr = fr * r0 * rng.uniform(0.97, 1.03)
            pts.append(Vector((cx + ox + math.cos(a2) * rx * rr, cy + oy + math.sin(a2) * ry * rr, z)))
    ox, oy = lean[0] * (h - z0), lean[1] * (h - z0)
    if point:
        for i in range(2):
            pts.append(Vector((cx + ox + rng.uniform(-0.3, 0.3) * rx * (1 - point),
                               cy + oy + rng.uniform(-0.3, 0.3) * ry * (1 - point), h - i * 0.15 * h * point)))
    else:
        # chamfered, slightly slanted top: a shoulder ring then a smaller top ring
        tilt = rng.uniform(0, TAU)
        fr = rings[-1][1]
        for ang, r0 in zip(angs, rads):
            dz = -slant * (0.5 + 0.5 * math.cos(ang - tilt))
            pts.append(Vector((cx + ox + math.cos(ang) * rx * r0 * fr * 0.98,
                               cy + oy + math.sin(ang) * ry * r0 * fr * 0.98, h + dz - 0.7)))
            pts.append(Vector((cx + ox + math.cos(ang) * rx * r0 * fr * 0.72,
                               cy + oy + math.sin(ang) * ry * r0 * fr * 0.72, h + dz)))
    return pts


def boulder_pts(rng, c, size, n=12, p=3.0, flat=0.12, z0=0.0):
    """Chunky faceted boulder: superellipsoid points over the upper half plus a
    ground ring, clipped flat a little below the crown."""
    sx, sy, sz = size
    rx, ry = sx / 2, sy / 2
    yaw = rng.uniform(0, TAU)
    cs, sn = math.cos(yaw), math.sin(yaw)
    pts = []
    ga = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        z = 0.12 + 0.88 * (i + 0.5) / n
        rr = math.sqrt(max(0.0, 1 - z * z))
        th = ga * i + rng.uniform(-0.35, 0.35)
        d = Vector((rr * math.cos(th), rr * math.sin(th), z))
        s = (abs(d.x) ** p + abs(d.y) ** p + abs(d.z) ** p) ** (-1 / p)
        d *= s * rng.uniform(0.86, 1.04)
        x, y = d.x * rx, d.y * ry
        pts.append(Vector((c[0] + x * cs - y * sn, c[1] + x * sn + y * cs, z0 + min(d.z * sz, sz * (1 - flat)))))
    for k in range(6):
        ang = TAU * k / 6 + rng.uniform(-0.3, 0.3)
        x, y = math.cos(ang) * rx * 0.92, math.sin(ang) * ry * 0.92
        pts.append(Vector((c[0] + x * cs - y * sn, c[1] + x * sn + y * cs, z0)))
    return pts


def blob_pts(rng, c, r, n=12):
    """Rough sphere of n points (fibonacci) for leafy bush lobes."""
    pts = []
    ga = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n
        rr = math.sqrt(max(0.0, 1 - z * z))
        th = ga * i + rng.uniform(-0.3, 0.3)
        k = rng.uniform(0.86, 1.06)
        pts.append(Vector((c[0] + rr * math.cos(th) * r[0] * k, c[1] + rr * math.sin(th) * r[1] * k,
                           c[2] + z * r[2] * k)))
    return pts


def chaikin(pts, it=2):
    for _ in range(it):
        out = []
        n = len(pts)
        for i in range(n):
            p, q = pts[i], pts[(i + 1) % n]
            out.append((0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]))
            out.append((0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1]))
        pts = out
    return pts


def resample(pts, step):
    n = len(pts)
    seg = [(pts[i], pts[(i + 1) % n]) for i in range(n)]
    L = sum(math.dist(p, q) for p, q in seg)
    k = max(8, int(L / step))
    st = L / k
    out, acc, i, t = [], 0.0, 0, 0.0
    want = 0.0
    for p, q in seg:
        d = math.dist(p, q)
        while want <= acc + d and len(out) < k:
            f = (want - acc) / d if d else 0.0
            out.append((p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f))
            want += st
        acc += d
    return out


def inside_poly(q, ring):
    """Even-odd point-in-polygon test for an XY ring."""
    x, y = q[0], q[1]
    c = False
    n = len(ring)
    for i in range(n):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def offset_ring(pts, offs):
    """Push each point of a closed CCW ring outward along its normal by offs[i]."""
    n = len(pts)
    out = []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        tx, ty = p2[0] - p0[0], p2[1] - p0[1]
        L = math.hypot(tx, ty) or 1.0
        nx, ny = ty / L, -tx / L      # outward for a CCW ring
        out.append((p1[0] + nx * offs[i], p1[1] + ny * offs[i]))
    return out


# ---------------------------------------------------------------------------
# builder
# ---------------------------------------------------------------------------


class Builder:
    def __init__(self, kit, name, seed):
        self.kit = kit
        self.a = kit.flintkit.Asset(name, "Terrain", seed=seed, tint_var=0.03)
        self.rng = random.Random(seed)
        self.pieces = []
        self.holes = []          # Opening objects whose inner faces paint dark
        self.yfront = -8.0       # front of the tunnel (for the cool rim band)
        # legacy tone mixes (callers still pass mix=); every outer rock face is
        # now the one SKIN colour, see tone()
        self.mix = self.core_mix = None
        self.drop = lambda x: 0.0     # how far the top falls away at x (rounded shoulders)
        self.shear = None             # (x, z) -> x: outer walls batter inward as they rise

    # -- rock -----------------------------------------------------------------

    def tone(self, faces, rng, mix=None):
        """Per-face toning: pale peach tops and lit (front-left) faces, mauve
        mid, cool shadow faces (more toward +X and low down), deep crevices;
        faces looking into a hole are cool / deep so the opening reads dark."""
        for f in sorted(faces, key=lambda f: tuple(f.calc_center_median())):
            if not f.is_valid:
                continue
            n = f.normal
            c = f.calc_center_median()
            u = rng.random()
            m, t = SKIN, rng.uniform(0.93, 1.07)
            for o in self.holes:
                probe = c + n * 0.9
                if o.inside(probe.x, probe.z, 0.05) and o.inside(c.x, c.z, 0.6) and c.y > self.yfront - 1.5:
                    m = SOFFIT
                    break
            # ONE rock colour outside (Roblox lighting shades the facets); the
            # soffit / tunnel lining is the sheet's cool swatch-2 stone
            paint(self.a, [f], m, t, 0.0)

    def rock(self, pts, planes=(), ylim=None, xlim=None, zmax=None, merge=3.0, seed=None, mix=None):
        rng = random.Random(seed) if seed is not None else self.rng
        for p in pts:
            if ylim:
                p.y = min(max(p.y, ylim[0]), ylim[1])
            if xlim:
                p.x = min(max(p.x, xlim[0]), xlim[1])
            if zmax is not None:
                p.z = min(p.z, zmax)
            p.z = max(p.z, 0.0)
            if planes:
                project(p, planes)
        faces = hull(self.a, pts, merge)
        self.tone(faces, rng, mix)
        pc = Piece(faces, "rock")
        self.pieces.append(pc)
        return pc

    def column(self, cx, cy, rx, ry, h, planes=(), point=0.0, n=None, lean=(0.0, 0.0), slant=0.5, **kw):
        n = n or self.rng.choice((5, 5, 6))
        rings = ((0.0, 1.0), (0.5, 0.94), (0.86, 0.86)) if not point else \
            ((0.0, 1.0), (0.45, 0.82), (0.75, 0.55))
        pts = col_pts(self.rng, cx, cy, rx, ry, h, n=n, rings=rings, point=point, slant=slant, lean=lean)
        return self.rock(pts, planes, **kw)

    def boulder(self, c, size, planes=(), n=11, **kw):
        return self.rock(boulder_pts(self.rng, c, size, n=n), planes, merge=5.0, **kw)

    def box_rock(self, x0, x1, y0, y1, z0, z1, planes=(), **kw):
        pts = [Vector((x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
        return self.rock(pts, planes, merge=1.0, **kw)

    # -- foliage & scatter --------------------------------------------------------

    def bush(self, x, y, z, s=1.0, hang=0.0, sides=3, n=11):
        """Round leafy clump of lobes, one colour per lobe (a dark lobe or two,
        the main mid-green lobe and a sunny crown lobe), never shaded by
        normal: Roblox lighting rounds them."""
        rng = self.rng
        # one leaf tone per clump (clumps vary, lobes never by height or facing):
        # Roblox lighting gives the light crowns and dark undersides
        mat = LEAF
        lobes = [((0.0, 0.0, 0.62), (1.0, 0.95, 0.8), mat)]
        for k in range(sides):
            ang = rng.uniform(0, TAU) + k * 2.1
            lobes.append(((math.cos(ang) * 0.72, math.sin(ang) * 0.72, 0.45), (0.66, 0.64, 0.56), mat))
        lobes.append(((rng.uniform(-0.25, 0.25), rng.uniform(-0.3, 0.1), 1.1), (0.64, 0.62, 0.5), mat))
        for (ox, oy, oz), r, mat in lobes:
            c = (x + ox * s, y + oy * s - hang * 0.3, z + oz * s - hang * 0.2)
            faces = hull(self.a, blob_pts(rng, c, (r[0] * s, r[1] * s, r[2] * s), n=n), merge=0)
            t = rng.uniform(0.95, 1.05)
            for f in faces:
                paint(self.a, [f], mat, t, 0.03)
            self.pieces.append(Piece(faces, "leaf"))

    def tuft(self, x, y, z, s=1.0):
        rng = self.rng
        for k in range(3):
            ang = rng.uniform(0, TAU)
            h = rng.uniform(0.6, 1.0) * s
            self.a.cyl(0.16 * s, 0.0, h, 3, loc=(x + math.cos(ang) * 0.18 * s, y + math.sin(ang) * 0.18 * s, z - 0.05),
                       rot=(rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), ang), cap=False,
                       mat=GRASS)

    def flower(self, x, y, z, mat=None):
        """A flat upward-facing star dot (two crossed triangles) just above the grass."""
        m = mat or self.rng.choice(("flower_yellow", "flower_white", "flower_white"))
        bm = self.a.bm
        rot = self.rng.uniform(0, TAU)
        faces = []
        for k in range(2):
            vs = [bm.verts.new((x + math.cos(rot + k * math.pi / 3 + i * TAU / 3) * 0.3,
                                y + math.sin(rot + k * math.pi / 3 + i * TAU / 3) * 0.3, z + 0.1 + 0.02 * k))
                  for i in range(3)]
            faces.append(bm.faces.new(vs))
        bm.normal_update()
        for f in faces:
            if f.normal.z < 0:
                f.normal_flip()
        paint(self.a, faces, m, 1.0, 0.0)

    def pebble(self, x, y, z, s=0.5, mat=SKIN):
        faces = hull(self.a, blob_pts(self.rng, (x, y, z + s * 0.2), (s, s * 0.85, s * 0.55), n=7), merge=0)
        paint(self.a, faces, mat, self.rng.uniform(0.95, 1.08), 0.04)

    def rubble(self, x, y, s, planes=()):
        self.boulder((x, y), (s * self.rng.uniform(1.0, 1.4), s, s * self.rng.uniform(0.6, 0.85)), planes, n=7)

    # -- grass cap -----------------------------------------------------------------

    def cap(self, corners, ztop, dome=0.4, over=(0.3, 0.75), step=0.95, clampx=None, clampy=None,
            light=0.3, thick=1.0, smooth=2):
        """Shared W02 grass cap on a CCW XY outline: scalloped lip overhanging
        the rock, 0.6 grass over a 0.4 earth band, the top domed toward the
        middle. Returns the outer ring (for placing bushes)."""
        a, rng = self.a, self.rng
        ring = resample(chaikin(corners, smooth), step)
        offs = [over[0] + (over[1] - over[0]) * (0.5 + 0.5 * math.sin(i * 2.1 + rng.uniform(-0.6, 0.6)))
                for i in range(len(ring))]
        ring = offset_ring(ring, offs)
        if clampx:
            ring = [(min(max(x, clampx[0]), clampx[1]), y) for x, y in ring]
        if clampy:
            ring = [(x, min(max(y, clampy[0]), clampy[1])) for x, y in ring]
        cx = sum(p[0] for p in ring) / len(ring)
        cy = sum(p[1] for p in ring) / len(ring)
        bm = a.bm
        g = thick * 0.6
        dr = self.drop
        n = len(ring)
        top = [bm.verts.new((x, y, ztop - dr(x) + rng.uniform(-0.04, 0.04))) for x, y in ring]
        mid = [bm.verts.new((x, y, ztop - g - dr(x))) for x, y in ring]
        bot = []
        for x, y in ring:
            dx, dy = cx - x, cy - y
            L = math.hypot(dx, dy) or 1.0
            bot.append(bm.verts.new((x + dx / L * 0.22, y + dy / L * 0.22, ztop - thick - dr(x))))
        cbot = bm.verts.new((cx, cy, ztop - thick - dr(cx)))
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((mid[i], mid[j], top[j], top[i]))
            paint(a, [f], GRASS, rng.uniform(0.96, 1.04), 0.0)
            f = bm.faces.new((bot[i], bot[j], mid[j], mid[i]))
            paint(a, [f], EARTH, rng.uniform(0.95, 1.05), 0.0)
            f = bm.faces.new((bot[j], bot[i], cbot))
            paint(a, [f], EARTH, rng.uniform(0.95, 1.05), 0.0)
        # top: constrained Delaunay over the lip ring plus jittered interior
        # points, so the grass reads as a few broad, gently domed facets
        poly = [Vector((x, y)) for x, y in ring]
        inner = []
        xs, ys = [p[0] for p in ring], [p[1] for p in ring]
        sp_ = 3.4
        yy = min(ys) + sp_ * 0.7
        while yy < max(ys) - 0.5:
            xx = min(xs) + sp_ * 0.7 + rng.uniform(0, sp_ * 0.5)
            while xx < max(xs) - 0.5:
                q = Vector((xx + rng.uniform(-0.9, 0.9), yy + rng.uniform(-0.9, 0.9)))
                if inside_poly(q, ring) and min((q - v).length for v in poly) > 1.4:
                    inner.append(q)
                xx += sp_
            yy += sp_ * 0.87
        res = geometry.delaunay_2d_cdt(poly + inner, [(i, (i + 1) % n) for i in range(n)],
                                       [list(range(n))], 1, 1e-6, True)
        overts, ofaces, orig = res[0], res[2], res[3]
        vmap = []
        for k, v in enumerate(overts):
            oi = orig[k][0] if orig[k] else None
            if oi is not None and oi < n:
                vmap.append(top[oi])
            else:
                vmap.append(bm.verts.new((v.x, v.y, 0.0)))
                vmap[-1].co.z = self.cap_z(ztop, dome, ring, (cx, cy), v.x, v.y) + rng.uniform(-0.05, 0.05)
        spots = [(rng.uniform(min(xs) + 3, max(xs) - 3), rng.uniform(min(ys) + 3, max(ys) - 3),
                  rng.uniform(2.0, 3.6)) for _ in range(int(light * 14))]
        for fi in ofaces:
            vs = [vmap[k] for k in fi]
            if len(set(vs)) < 3:
                continue
            f = bm.faces.new(vs)
            f.normal_update()
            if f.normal.z < 0:
                f.normal_flip()
            c = f.calc_center_median()
            lit = any((c.x - sx) ** 2 + (c.y - sy) ** 2 < r * r for sx, sy, r in spots)
            paint(a, [f], GRASS, rng.uniform(0.95, 1.05) * (1.02 if lit else 1.0), 0.0)
        bm.normal_update()
        self.cap_info = (ztop, dome, ring, (cx, cy))
        return ring, (cx, cy)

    def cap_z(self, ztop, dome, ring, centre, x, y):
        """Grass height at (x, y) on the domed cap (matches cap()'s rings)."""
        cx, cy = centre
        ang = math.atan2(y - cy, x - cx)

        def diff(p):
            d = (math.atan2(p[1] - cy, p[0] - cx) - ang) % TAU
            return min(d, TAU - d)
        best = min(ring, key=diff)
        R = math.hypot(best[0] - cx, best[1] - cy) or 1.0
        f = min(1.0, math.hypot(x - cx, y - cy) / R)
        prof = ((0.0, 1.0), (0.4, 0.9), (0.7, 0.6), (0.88, 0.3), (1.0, 0.0))
        for (f0, d0), (f1, d1) in zip(prof, prof[1:]):
            if f <= f1:
                d = d0 + (d1 - d0) * (f - f0) / (f1 - f0)
                break
        return ztop + dome * d - self.drop(x)

    def ground(self, corners, z=0.14, step=1.3, jig=0.5, clampx=None):
        """Thin grass fringe slab round the foot (top n-gon, low sides)."""
        rng = self.rng
        ring = resample(chaikin(corners, 2), step)
        ring = offset_ring(ring, [rng.uniform(-jig, jig * 0.3) for _ in ring])
        if clampx:
            ring = [(min(max(x, clampx[0]), clampx[1]), y) for x, y in ring]
        bm = self.a.bm
        lo = [bm.verts.new((x, y, 0.0)) for x, y in ring]
        hi = [bm.verts.new((x, y, z)) for x, y in ring]
        f = bm.faces.new(hi)
        paint(self.a, [f], GRASS, 1.0, 0.0)
        n = len(ring)
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
            paint(self.a, [f], GRASS, self.rng.uniform(0.95, 1.05), 0.0)
        bm.normal_update()
        return ring

    def flat(self, pts, z0, z1, mat, side=None, tint=1.0):
        """Flat CCW XY polygon prism from z0 to z1 (top n-gon + sides)."""
        bm = self.a.bm
        lo = [bm.verts.new((x, y, z0)) for x, y in pts]
        hi = [bm.verts.new((x, y, z1)) for x, y in pts]
        f = bm.faces.new(hi)
        paint(self.a, [f], mat, tint, 0.0)
        n = len(pts)
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
            paint(self.a, [f], side or mat, tint, 0.0)
        bm.normal_update()

    def plate_xz(self, outline, y0, y1, mat=CONN):
        """Flat plate from an XZ outline (CCW seen from +Y), y0 < y1."""
        bm = self.a.bm
        back = [bm.verts.new((x, y1, z)) for x, z in outline]
        front = [bm.verts.new((x, y0, z)) for x, z in outline]
        faces = [bm.faces.new(back), bm.faces.new(list(reversed(front)))]
        n = len(outline)
        for i in range(n):
            j = (i + 1) % n
            faces.append(bm.faces.new((front[i], front[j], back[j], back[i])))
        bmesh.ops.recalc_face_normals(bm, faces=faces)
        paint(self.a, faces, mat, 1.0, 0.0)
        bm.normal_update()

    def apply_shear(self):
        """Batter the outer walls inward with height (whole mesh, so rock, cap,
        bushes and plates stay together); faces bent out of plane are split."""
        if not self.shear:
            return
        bm = self.a.bm
        for v in bm.verts:
            v.co.x = self.shear(v.co.x, v.co.z)
        bm.normal_update()
        bent = []
        for f in bm.faces:
            if len(f.verts) > 3:
                c = f.calc_center_median()
                if max(abs(f.normal.dot(v.co - c)) for v in f.verts) > 0.01:
                    bent.append(f)
        if bent:
            bmesh.ops.triangulate(bm, faces=bent)
        bm.normal_update()

    def finish(self, role, collision, budget, notes=""):
        cull_hidden(self.a, self.pieces)
        drop_bottoms(self.a)
        self.apply_shear()
        obj = self.a.finish()
        if self.holes:
            obj["kit_shading_ok"] = ("the hole's soffit and tunnel lining is the sheet's cool swatch-2 stone "
                                     "(w02_rock_cool, a specified material change); every outer rock face is "
                                     "one colour (w02_rock)")
        used = {m.get("flintkit_key") for m in obj.data.materials if m}
        why = {SOFFIT: "w02_rock_cool = the cool blue-grey stone lining the arch soffit and tunnel (sheet swatch 2, "
                       "a W02 plan requirement); outer rock is one colour, w02_rock",
               SLAB: "w02_slab = the pale cut-stone floor sill",
               CONN: "w02_connector = the flat grey back connector plate (a kit joint, not rock)",
               PATH: "w02_path = the sandy walkway dirt, w02_earth = the brown soil band under the grass lip"}
        notes = [t for k, t in why.items() if k in used and (k != PATH or EARTH in used)]
        if len(notes) >= 2 or (PATH in used and EARTH in used) or (SOFFIT in used):
            obj["kit_two_tone_ok"] = "; ".join(notes)
        return self.kit.tag(obj, role, collision=collision, budget=budget, notes=notes)


# ---------------------------------------------------------------------------
# the arch
# ---------------------------------------------------------------------------


class Spec:
    """Dimensions of one arch. x runs -W..W, the masses' fronts sit at yf, the
    span's front at yfs (set back for the C-shaped top), the rock back at yb."""

    def __init__(self, **kw):
        self.W = 15.6
        self.yf, self.yfs, self.yb = -7.6, -6.6, 11.2
        self.RT = 19.6          # rock top (lip 20.2, dome 21.1, bush tops ~23)
        self.w2, self.s, self.rz = 6.0, 7.0, 6.0
        self.s, self.rz = 5.6, 7.4      # round arch: 13 tall
        self.angles = (180, 150, 120, 90, 60, 30, 0)   # 6 big soffit facets, apex at the crown
        self.ring = 6.0         # voussoir ring thickness round the opening
        self.shoulder = 6.0     # how far the top falls at the outer edges (rounded mound)
        self.shoulder_from = 0.3
        self.batter = 2.4       # how far the outer walls lean in at the rock top
        self.dome = 0.9
        self.thick = 1.4        # grass cap thickness (grass over an earth band)
        self.apron = 4.6
        self.bushes = 12
        self.base_bushes = 16
        self.side_plate = 0.42  # fraction of the depth the +X connector return covers
        self.hang_size = 2.2    # clumps hanging over the arch (corner clumps a bit bigger)
        self.crown_xs = (-3.0, 3.4)   # extra big clumps over the arch crown, set back from the lip
        self.rim_sizes = (1.6, 2.2)
        self.cap_x = 0.8        # grass cap half width as a fraction of W
        self.shoulder_bushes = 2  # clumps per side perched on the bare shoulder columns
        self.mass_h = (1.0, 1.0)  # per side multipliers of RT for the mass columns
        self.__dict__.update(kw)


def arch_mass(b, sp, side, o, col_top=None, front_cols=True, side_cols=True, shards=True, ledge_bushes=True):
    """Columns, core and foot rocks of one side mass (side -1 left, +1 right).
    Column tops follow b.drop so the outer shoulders round off under the cap."""
    rng = b.rng
    W, yf, yb, RT = sp.W, sp.yf, sp.yb, sp.RT
    top = col_top if col_top is not None else RT
    dr = b.drop
    wall = o.left if side < 0 else o.right
    xin, xout = side * o.w2, side * W
    width = W - o.w2
    ysplit = yb - sp.side_plate * (yb - yf) if side > 0 else yb + 1
    # core: two y segments, the rear one stepped back a little from the hole;
    # its top slopes down with the shoulder (chord of the drop curve)
    for (y0, y1, inset) in ((yf + 1.2, (yf + yb) / 2, 0.15), ((yf + yb) / 2, yb, 0.45)):
        x0 = xin + side * inset
        xo = xout - side * 0.7
        xm = (x0 + xo) / 2
        pts = []
        for x in (x0, xm, xo):
            for y in (y0, y1):
                pts.append(Vector((x, y, 0.0)))
                pts.append(Vector((x, y, top - 1.2 - dr(x))))
        b.rock(pts, [shift_plane(wall, inset)], merge=1.0, mix=b.core_mix)
    # front columns, inner first so the opening's frame is a tall straight column
    if front_cols:
        x = o.w2
        k = 0
        while x < W - 0.8:
            w = min(rng.uniform(3.6, 5.0), W - x)
            if W - x - w < 2.2:
                w = W - x
            cx = side * (x + w / 2)
            ry = rng.uniform(2.0, 2.6)
            # plan rounding: the outer columns step back so the mass bulges
            fx = (x + w / 2 - o.w2) / max(width, 1.0)
            jf = rng.uniform(0.0, 0.7) - 2.2 * max(0.0, (fx - 0.5) / 0.5) ** 2
            h = top - dr(side * (x + w)) - (rng.uniform(0.0, 0.3) if k == 0 else rng.uniform(0.2, 1.4))
            b.column(cx, yf - jf + ry, w / 2 * 1.12, ry, h, [wall], ylim=(yf - 1.2, yb),
                     xlim=(-W, W), zmax=top, slant=0.7)
            x += w * 0.9
            k += 1
        # chunky lower forward columns (stepped, like the reference's front-left)
        for k, (fx, fh) in enumerate(((rng.uniform(0.5, 0.65), rng.uniform(0.55, 0.66)),
                                      (rng.uniform(0.15, 0.3), rng.uniform(0.38, 0.46)))):
            cx = side * (o.w2 + width * fx)
            h = top * fh
            b.column(cx, yf - 0.5, rng.uniform(1.9, 2.4), rng.uniform(1.6, 2.0), h,
                     [wall], ylim=(yf - 2.6, yb), xlim=(-W, W), slant=1.0)
            # a leafy clump perched on the ledge (the reference's mid-face bushes)
            if ledge_bushes and (k == 0 or side < 0):
                b.bush(cx, yf - 0.9, h - 1.0, rng.uniform(0.9, 1.15))
    # outer side columns
    if side_cols:
        y = yf - 0.3
        yend = ysplit if side > 0 else yb - 0.6
        while y < yend - 1.0:
            w = min(rng.uniform(3.4, 4.8), yend - y)
            rx = rng.uniform(1.5, 2.0)
            h = top - dr(side * W) - rng.uniform(0.0, 1.8)
            b.column(side * (W - rx * 0.95), y + w / 2, rx, w / 2 * 1.1, h, [wall],
                     ylim=(yf - 1.0, yend if side > 0 else yb), xlim=(-W, W), zmax=top, slant=0.8)
            y += w * 0.88
        # a second, taller row of shoulder columns behind the outer one, so the
        # rounded flank steps up in columns instead of showing the core's slope
        if dr(side * W) > 3.0:
            xs = W - 3.4
            y = yf + 0.6
            while y < yend - 1.5:
                w = min(rng.uniform(3.6, 5.0), yend - y)
                h = top - dr(side * (xs + 0.5)) - rng.uniform(0.0, 0.7)
                b.column(side * xs, y + w / 2, rng.uniform(1.7, 2.1), w / 2 * 1.1, h, [wall],
                         ylim=(yf - 0.6, yend if side > 0 else yb), xlim=(-W, W), zmax=top, slant=0.8)
                y += w * 0.9
    if shards:
        # pointed leaning shards at the foot
        n = 2 if side < 0 else 1
        for i in range(n):
            f = (i + 0.5) / n
            cx = side * (o.w2 + 0.8 + (width - 1.6) * f + rng.uniform(-0.6, 0.6))
            h = rng.uniform(3.4, 4.6) if i == 0 else rng.uniform(4.8, 6.4)
            b.column(cx, yf - rng.uniform(1.5, 2.2), rng.uniform(1.5, 2.0), rng.uniform(1.2, 1.6), h, [wall],
                     point=0.7, lean=(side * rng.uniform(0.0, 0.06), -rng.uniform(0.02, 0.08)),
                     xlim=(-W, W), ylim=(yf - 4.0, yb))


def pillar(b, x0, x1, y0, y1, h, nx=2, ny=4, hj=(0.0, 1.4)):
    """A block of tall columns on an nx x ny grid round a core, so every face
    (front, back, inner and outer) reads as vertical columnar facets."""
    rng = b.rng
    b.box_rock(x0 + 0.9, x1 - 0.9, y0 + 0.9, y1 - 0.9, 0.0, h - 1.6)
    dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
    for i in range(nx):
        for j in range(ny):
            if 0 < i < nx - 1 and 0 < j < ny - 1:
                continue
            cx = x0 + dx * (i + 0.5) + rng.uniform(-0.2, 0.2)
            cy = y0 + dy * (j + 0.5) + rng.uniform(-0.2, 0.2)
            b.column(cx, cy, dx / 2 * 1.1, dy / 2 * 1.1, h - rng.uniform(*hj), xlim=(x0 - 0.3, x1 + 0.3),
                     ylim=(y0 - 0.3, y1 + 0.3), zmax=h, slant=0.8)


def arch_span(b, sp, o, front=True, bottom_shift=(0.15, 0.45), bulge=0.0):
    """Facet blocks over the opening: full-depth core per facet plus a front
    facade block whose bottom lies exactly on the facet (the visible soffit)."""
    rng = b.rng
    RT, yfs, yb = sp.RT, sp.yfs, sp.yb

    def on_edge(x0, z0, x1, z1, t, off=0.0, nrm=(0.0, 0.0)):
        # a point ON the facet's line (t=0..1 spans the facet, beyond extends
        # it), so every block's underside is exactly its soffit facet; the
        # earlier projection from z=-5 slid points sideways along sloped facets
        # and left the flat crown block hanging below its neighbours
        return x0 + (x1 - x0) * t + nrm[0] * off, z0 + (z1 - z0) * t + nrm[1] * off

    # neighbouring facades overlap a little past each facet end (outside the
    # convex hole); the springer facets are not extended into the walls
    for i, ((x0, z0), (x1, z1), pl) in enumerate(o.facets):
        L = math.hypot(x1 - x0, z1 - z0) or 1.0
        nrm = (pl[0], pl[1])
        # core, two y segments stepped up a little
        ym = (yfs + 1.4 + yb) / 2
        for (y0, y1), off in zip(((yfs + 1.4, ym), (ym, yb)), bottom_shift):
            pts = []
            for t in (0.0, 1.0):
                x, z = on_edge(x0, z0, x1, z1, t, off, nrm)
                for y in (y0, y1):
                    pts.append(Vector((x, y, z)))
                    pts.append(Vector((x, y, RT - 0.25)))
            b.rock(pts, [shift_plane(pl, off)], merge=1.0)
        if not front:
            continue
        # a voussoir: a big chunky block whose underside is the facet and whose
        # outer face lies T out along the facet normal, bulging forward of the
        # wall above, so the opening is framed by a ring of rounded blocks
        # springer blocks (steep facets) stay slimmer, so they don't jut out
        # of the side masses as shelves
        T = max(2.5, min(sp.ring, RT - o.top - 0.3)) * (0.5 + 0.5 * abs(nrm[1]))
        e = 0.45 / L
        ends = (-e if i > 0 else 0.0, 1.0 + e if i < len(o.facets) - 1 else 1.0)
        pts = []
        jf = (rng.uniform(0.5, 0.9) + bulge * rng.uniform(0.6, 1.0)) * (0.5 + 0.5 * abs(nrm[1]))
        for t in (ends[0], 0.5, ends[1]):
            x, z = on_edge(x0, z0, x1, z1, t)
            pts.append(Vector((x, yfs - jf * rng.uniform(0.75, 0.9), z)))
            pts.append(Vector((x, yfs + 1.6, z)))
        for t in ends:
            x, z = on_edge(x0, z0, x1, z1, t, T * rng.uniform(0.92, 1.05), nrm)
            pts.append(Vector((x, yfs - jf * rng.uniform(0.6, 0.8), min(z, RT - rng.uniform(0.0, 0.4)))))
            pts.append(Vector((x, yfs + 1.6, min(z, RT))))
        # the rounded front: the block's face breaks into a few broad facets
        for t, f in ((0.3, 0.4), (0.7, 0.6)):
            x, z = on_edge(x0, z0, x1, z1, t + rng.uniform(-0.08, 0.08), T * f, nrm)
            pts.append(Vector((x, yfs - jf - rng.uniform(0.0, 0.15), min(z, RT - 0.6))))
        b.rock(pts, [pl], ylim=(yfs - 2.4, yb), zmax=RT, merge=4.0)


def arch_cap(b, sp, o, notch=True, x_l=None, x_r=None, ztop=None, dome=None):
    dome = sp.dome if dome is None else dome
    W, yf, yfs, yb = sp.W, sp.yf, sp.yfs, sp.yb
    # the grass covers the top; the rounded outer shoulders stay bare columns
    x_l = -W * sp.cap_x if x_l is None else x_l
    x_r = W * sp.cap_x if x_r is None else x_r
    ztop = sp.RT + 0.6 if ztop is None else ztop
    if notch:
        corners = [(x_l, yf + 2.0), (x_l + 2.4, yf), (o.cx - o.w2 - 1.2, yf), (o.cx - o.w2 - 0.3, yfs),
                   (o.cx + o.w2 + 0.3, yfs), (o.cx + o.w2 + 1.2, yf), (x_r - 2.4, yf), (x_r, yf + 2.0),
                   (x_r, yb + 0.4), (x_l, yb + 0.4)]
    else:
        corners = [(x_l, yf), (x_r, yf), (x_r, yb + 0.4), (x_l, yb + 0.4)]
    ring, c = b.cap(corners, ztop, dome=dome, clampx=(-W - 0.35, W + 0.35), clampy=(-99, yb + 0.4),
                    thick=sp.thick)
    return ring, c, ztop


def top_dress(b, ring, c, ztop, dome, count, hang_xs=(), sizes=(1.6, 2.2), pebbles=5, flowers=14, tufts=6,
              skip=None):
    """Bushes round the rim (heaviest at the corners), a few hanging over the
    front face at hang_xs, pebbles, flowers and tufts on the grass."""
    rng = b.rng
    cx, cy = c
    n = len(ring)
    # rim slots: evenly spaced, nudged toward the corners
    picks = []
    start = rng.uniform(0, n)
    for k in range(count):
        i = int(start + k * n / count + rng.uniform(-0.25, 0.25) * n / count) % n
        picks.append(ring[i])
    for x, y in picks:
        if skip and skip(x, y):
            continue
        dx, dy = cx - x, cy - y
        L = math.hypot(dx, dy) or 1.0
        sz = rng.uniform(*sizes)
        px, py = x + dx / L * (0.4 + 0.5 * sz), y + dy / L * (0.4 + 0.5 * sz)
        b.bush(px, py, b.cap_z(ztop, dome, ring, c, px, py) - 0.3 - 0.25 * sz, sz)
    for h in hang_xs:
        hx, hy = h[0], h[1]
        hs = h[2] if len(h) > 2 else rng.uniform(1.4, 1.75)
        b.bush(hx, hy, b.cap_z(ztop, dome, ring, c, hx, hy + 1.0) - 0.7 - 0.3 * hs, hs, hang=1.0)
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    box = (min(xs) + 1.5, max(xs) - 1.5, min(ys) + 1.5, max(ys) - 1.5)

    def zat(x, y):
        return b.cap_z(ztop, dome, ring, c, x, y)
    for k in range(pebbles):
        x, y = rng.uniform(box[0], box[1]), rng.uniform(box[2], box[3])
        b.pebble(x, y, zat(x, y) - 0.05, rng.uniform(0.3, 0.55))
    for k in range(flowers):
        x, y = rng.uniform(box[0], box[1]), rng.uniform(box[2], box[3])
        b.flower(x, y, zat(x, y) - 0.1)
    for k in range(tufts):
        x, y = rng.uniform(box[0], box[1]), rng.uniform(box[2], box[3])
        b.tuft(x, y, zat(x, y), rng.uniform(0.8, 1.1))


def base_dress(b, sp, o, bushes, spots=None, tufts=18, flowers=16, rubble=9):
    """Small bushes, tufts, flowers and rubble along the foot (front and sides),
    kept clear of the opening's walkway."""
    rng = b.rng
    W, yf, yb = sp.W, sp.yf, sp.yb

    def clear(x, y):
        return abs(x - o.cx) > o.w2 + 1.0 or y > yf + 0.5 or y < yf - sp.apron - 1.0

    spots = spots or []
    if not spots:
        for k in range(bushes):
            for _ in range(40):
                t = rng.random()
                if t < 0.62:
                    x, y = rng.uniform(-W + 0.4, W - 0.4), yf - rng.uniform(1.2, 3.4)
                else:
                    sd = rng.choice((-1, 1))
                    x, y = sd * (W + rng.uniform(-0.6, 0.4)), rng.uniform(yf - 1.0, yb - 3)
                if clear(x, y) and all(math.dist((x, y), s) > 1.7 for s in spots):
                    spots.append((x, y))
                    break
    for x, y in spots:
        b.bush(x, y, 0.1, rng.uniform(0.85, 1.45), sides=3, n=9)
    for k in range(tufts):
        for _ in range(20):
            x, y = rng.uniform(-W, W), yf - rng.uniform(0.6, 3.4)
            if clear(x, y):
                b.tuft(x, y, 0.14, rng.uniform(0.8, 1.2))
                break
    for k in range(flowers):
        for _ in range(20):
            x, y = rng.uniform(-W, W), yf - rng.uniform(0.8, 3.6)
            if clear(x, y):
                b.flower(x, y, 0.14, "flower_yellow" if rng.random() < 0.6 else "flower_white")
                break
    for k in range(rubble):
        for _ in range(20):
            x, y = rng.uniform(-W + 0.5, W - 0.5), yf - rng.uniform(1.4, 3.6)
            if clear(x, y):
                b.rubble(x, y, rng.uniform(0.5, 0.9), [o.left if x < o.cx else o.right])
                break


def floor(b, sp, o, sill=True, pebbles=7):
    """Pale stone sill through the hole with a lip out the front, and the tan
    dirt path running over it and fanning out into the apron; the sill shows
    as pale bands either side of the path and round the fan's root."""
    rng = b.rng
    yf, yb, w2, cx = sp.yf, sp.yb, o.w2, o.cx
    yfr = yf - sp.apron
    fan = w2 + min(3.2, 0.5 * w2 + 1.4)
    if sill:
        lip = w2 + 1.5
        b.flat([(cx - w2 + 0.05, yf), (cx + w2 - 0.05, yf), (cx + w2 - 0.05, yb), (cx - w2 + 0.05, yb)],
               0.0, 0.3, SLAB)
        b.flat([(cx - lip, yf - 2.2), (cx + lip, yf - 2.2), (cx + lip - 0.6, yf + 0.05), (cx - lip + 0.6, yf + 0.05)],
               0.0, 0.3, SLAB)
        wr = max(1.6, w2 * 0.68)
        yb_ap = yb - 0.6
    else:
        wr = w2 - 0.3
        yb_ap = yf + (yb - yf) * 0.62
    m = 8
    arcp = []
    yc = yf - 1.7
    for k in range(m + 1):
        ang = -math.pi * k / m        # 0 -> -pi : right -> front -> left
        x = cx + math.cos(ang) * fan * (rng.uniform(0.95, 1.03) if 0 < k < m else 1.0)
        y = yc + math.sin(ang) * (sp.apron - 1.7) * (rng.uniform(0.94, 1.03) if 0 < k < m else 1.0)
        arcp.append((x, y))
    # the path runs out of the hole at width 2*wr, flares over the sill lip, then fans
    outline = [(cx + wr, yb_ap), (cx + wr, yf - 0.4), (cx + (wr + fan) / 2, yc + 0.6)] + arcp + \
        [(cx - (wr + fan) / 2, yc + 0.6), (cx - wr, yf - 0.4), (cx - wr, yb_ap)]
    area = sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(outline, outline[1:] + outline[:1]))
    if area < 0:
        outline.reverse()
    z0 = 0.3 if sill else 0.14
    b.flat(outline, 0.1, z0 + 0.12, PATH)
    # worn ruts and cross seams
    for k in range(2):
        x = cx + rng.uniform(-0.4, 0.4) * wr
        y0 = yf + rng.uniform(1.0, 4.0)
        b.a.strip([(x, y0), (x + rng.uniform(-1.0, 1.0), y0 - 4.0), (x + rng.uniform(-2.0, 2.0), yfr + 1.2)],
                  0.22, 0.04, loc=(0, 0, z0 + 0.12), mat=PATH)
    for k in range(2):
        y = rng.uniform(yfr + 1.4, yf - 1.0)
        x0 = cx + rng.uniform(-0.7, -0.3) * fan
        b.a.strip([(x0, y), (x0 + fan * 0.6, y + rng.uniform(-0.5, 0.5)), (x0 + fan * 1.1, y + rng.uniform(-0.6, 0.6))],
                  0.2, 0.04, loc=(0, 0, z0 + 0.12), mat=PATH)
    for k in range(pebbles):
        x = cx + rng.uniform(-fan + 0.8, fan - 0.8)
        y = rng.uniform(yfr + 0.8, yf + 3.0)
        b.pebble(x, y, z0 + 0.1, rng.uniform(0.25, 0.45))


def connector(b, sp, o, ztop=None, side=True, xl=None, xr=None):
    """Flat grey back plate inset 0.5 with the hole cut out, tabs on its rear
    vertical edges at 8-stud spacing, and (side=True) the return over the rear
    of the +X side seen in the reference's side/rear view."""
    W, yb, yf = sp.W, sp.yb, sp.yf
    xl = -W + 0.5 if xl is None else xl
    xr = W - 0.5 if xr is None else xr
    zt = (sp.RT - 0.4) if ztop is None else ztop
    dr = b.drop
    # the top edge follows the rounded shoulders so the plate stays under the cap
    tops = [(xr - (xr - xl) * k / 8, zt - dr(xr - (xr - xl) * k / 8)) for k in range(9)]
    if o is not None:
        outline = [(xl, 0.0)] + o.outline(0.1) + [(xr, 0.0)] + tops
    else:
        outline = [(xl, 0.0), (xr, 0.0)] + tops
    b.plate_xz(outline, yb, yb + 0.4)
    for x in (xl + 0.4, xr - 0.4):
        z = 4.0
        while z < zt - dr(x) - 0.8:
            b.a.box((0.5, 0.4, 1.5), loc=(x, yb + 0.6, z), mat=CONN, tint=0.97)
            z += 8.0
    if side:
        ys = yb - sp.side_plate * (yb - yf)
        b.a.box((0.4, yb + 0.4 - ys, zt - dr(W)), loc=(W - 0.2, (ys + yb + 0.4) / 2, 0), mat=CONN, base=True)


def shoulder_fn(sp, cx=0.0):
    def drop(x):
        f = (abs(x - cx) / sp.W - sp.shoulder_from) / (1.0 - sp.shoulder_from)
        f = max(0.0, min(1.05, f))
        # between a parabola and a quarter circle: a broad rounded shoulder
        return sp.shoulder * (0.3 * f * f + 0.7 * (1.0 - math.sqrt(max(0.0, 1.0 - min(f, 0.995) ** 2))))
    return drop


def shear_fn(xin, W, H, batter, cx=0.0, sides=(-1, 1)):
    """Outer walls lean in by `batter` at height H; nothing within xin of cx
    moves, so the opening is never narrowed."""
    def shear(x, z):
        d = x - cx
        sd = 1 if d >= 0 else -1
        if sd not in sides:
            return x
        f = min(1.0, max(0.0, (abs(d) - xin) / max(W - xin, 0.1)))
        return x - sd * batter * f * min(1.0, max(0.0, z / H))
    return shear


def build_arch(kit, name, sp, seed, role, budget, notes, hang=2):
    b = Builder(kit, name, seed)
    o = Opening(sp.w2, sp.s, sp.rz, sp.angles)
    b.holes.append(o)
    b.yfront = sp.yfs
    W, yf, yb = sp.W, sp.yf, sp.yb
    b.drop = shoulder_fn(sp)
    b.shear = shear_fn(sp.w2, W, sp.RT, sp.batter)
    arch_mass(b, sp, -1, o)
    arch_mass(b, sp, 1, o)
    arch_span(b, sp, o)
    # big foot boulders: front-left heaviest, one front-right
    rng = b.rng
    bw = W - o.w2
    b.boulder((-W + 3.0, yf - 1.6), (5.6, 4.6, 5.4), [o.left], ylim=(yf - 4.6, yb))
    b.boulder((-o.w2 - 0.45 * bw, yf - 2.4), (4.4, 3.6, 3.8), [o.left], ylim=(yf - 4.6, yb))
    b.boulder((-o.w2 - 1.3, yf - 1.8), (2.8, 2.4, 2.6), [o.left], ylim=(yf - 4.6, yb))
    b.boulder((W - 2.6, yf - 1.2), (4.2, 3.6, 4.0), [o.right], ylim=(yf - 4.6, yb))
    b.boulder((o.w2 + 1.4, yf - 1.6), (2.8, 2.4, 2.8), [o.right], ylim=(yf - 4.6, yb))
    b.boulder((-W + 0.8, yf + 4.0), (2.6, 3.0, 2.8), [o.left], xlim=(-W - 0.3, W))
    ring, c, ztop = arch_cap(b, sp, o)
    # big clumps hanging over the arch crown and heavy ones on the front corners
    hs = sp.hang_size
    hang_pts = [(o.cx + x, sp.yfs - 0.7, rng.uniform(hs * 0.9, hs * 1.1))
                for x in ((-o.w2 + 0.6, o.w2 - 0.4, 0.2)[:hang])]
    xc = W * sp.cap_x
    hang_pts += [(-xc + 0.6, yf - 0.2, rng.uniform(hs * 1.05, hs * 1.25)),
                 (xc - 0.6, yf - 0.2, rng.uniform(hs * 1.0, hs * 1.2))]
    hang_pts += [(o.cx + x, sp.yfs + 1.4, rng.uniform(hs * 0.85, hs)) for x in sp.crown_xs]
    top_dress(b, ring, c, ztop, sp.dome, sp.bushes, hang_xs=hang_pts, sizes=sp.rim_sizes)
    # clumps perched on the bare shoulder columns, stepping down the flanks
    for sd in (-1, 1):
        for k in range(sp.shoulder_bushes):
            x = sd * (xc + (W - xc) * (0.3 + 0.55 * k / max(1, sp.shoulder_bushes - 1)))
            y = yf + rng.uniform(0.2, 1.2) if k == 0 else rng.uniform(yf + 3.0, (yf + yb) / 2)
            s = rng.uniform(1.2, 1.6)
            b.bush(x, y, sp.RT - b.drop(x + sd * 1.2) - 0.6 - 0.25 * s, s)
    b.ground([(-W - 0.3, yf - sp.apron + 0.4), (W + 0.3, yf - sp.apron + 0.4), (W + 0.3, yb), (-W - 0.3, yb)],
             clampx=(-W - 0.35, W + 0.35))
    floor(b, sp, o)
    base_dress(b, sp, o, sp.base_bushes)
    connector(b, sp, o)
    return b.finish(role, "precise", budget, notes)


# ---------------------------------------------------------------------------
# assets
# ---------------------------------------------------------------------------


def build_hero(kit):
    sp = Spec(bushes=8, crown_xs=(), shoulder_bushes=1)  # 8 rim clumps + 2 over the arch + 2 front corners
    return build_arch(kit, "NaturalArch", sp, 401, "hero", 7000, hang=2, notes=
                      "arch / cave mouth 32x24x22, opening 12x13 through the full depth; precise collision keeps "
                      "the hole walkable; grey connector on +Y (and the rear of +X) joins a cliff behind")


def build_narrow(kit):
    sp = Spec(W=11.6, yf=-4.6, yfs=-4.2, yb=8.4, w2=3.0, s=8.4, rz=3.6, angles=(180, 150, 120, 90, 60, 30, 0),
              apron=4.8, bushes=8, base_bushes=13, shoulder=5.0, shoulder_from=0.3, batter=2.6,
              hang_size=1.9, crown_xs=(), rim_sizes=(1.5, 2.0), cap_x=0.8, shoulder_bushes=1)
    return build_arch(kit, "NaturalArchNarrow", sp, 411, "variant", 6000,
                      "tall narrow 6x12 opening, thick pillars", hang=1)


def build_wide(kit):
    sp = Spec(RT=15.4, shoulder=5.4, shoulder_from=0.36, batter=3.0, w2=9.0, s=3.6, rz=7.4,
              angles=(180, 157, 135, 112, 90, 68, 45, 23, 0), bushes=9, base_bushes=15, hang_size=2.0, crown_xs=(),
              cap_x=0.8)
    return build_arch(kit, "NaturalArchWide", sp, 421, "variant", 7000,
                      "broad squat 18x11 opening under a long thin span, dirt floor")


def build_broken(kit):
    """Collapsed span: tall left mass with a broken stub overhang, a lower
    stepped right mass, a 10-wide gap with fallen chunks at the sides."""
    sp = Spec(W=14.0, yf=-6.0, yfs=-5.4, yb=9.4, RT=17.6, apron=4.0, shoulder=5.0, shoulder_from=0.42,
              batter=2.8)
    b = Builder(kit, "NaturalArchBroken", 431)
    rng = b.rng
    gap_l, gap_r = -4.2, 5.8
    gc = (gap_l + gap_r) / 2
    yf, yfs, yb = sp.yf, sp.yfs, sp.yb
    # the walkway through the gap (clear to 10.5); rock is projected out of it
    o = Opening((gap_r - gap_l) / 2, 9.0, 1.5, (180, 90, 0), cx=gc)
    b.yfront = yf
    full = shoulder_fn(sp)
    b.drop = lambda x: full(x) if x < 0 else 0.0        # only the tall left mass rounds off
    shl = shear_fn(-gap_l, sp.W, sp.RT, sp.batter, sides=(-1,))
    shr = shear_fn(gap_r, sp.W, 12.0, 2.2, sides=(1,))
    b.shear = lambda x, z: shl(x, z) if x < 0 else shr(x, z)
    # -- left mass: full height columns, rounded outer shoulder
    arch_mass(b, sp, -1, Opening(-gap_l, 30.0, 1.0, (180, 0), cx=0.0))
    # -- the broken stub: a lean-over chunk of angled facets jutting over the gap
    root = []
    for y in (yfs - 0.6, yb - 0.4):
        for x, z in ((-7.6, sp.RT - 0.3), (-7.6, 11.6), (-4.2, sp.RT - 0.1), (-4.2, 11.4)):
            root.append(Vector((x, y + rng.uniform(-0.3, 0.3), z)))
    b.rock(root, ylim=(yfs - 1.0, yb), zmax=sp.RT)
    tip = [Vector((-4.6, y, z)) for y in (yfs - 0.4, yb - 1.4) for z in (sp.RT - 0.2, 12.4)]
    tip += [Vector((-1.6 + rng.uniform(-0.4, 0.4), yfs + 0.4 + rng.uniform(0, 1.5), sp.RT - rng.uniform(1.0, 2.2))),
            Vector((-0.9, yfs + 3.0 + rng.uniform(-0.6, 0.6), sp.RT - rng.uniform(2.4, 3.2))),
            Vector((-1.4, yfs + 6.5 + rng.uniform(-0.8, 0.8), sp.RT - rng.uniform(1.4, 2.6))),
            Vector((-2.2, yb - 3.0, sp.RT - rng.uniform(0.6, 1.4))),
            Vector((-2.4, yfs + 2.0, 13.4)), Vector((-1.8, yfs + 5.0, 13.9)),
            Vector((-3.0, yb - 2.6, 12.9))]
    b.rock(tip, merge=4.0)
    # -- right mass: lower and stepped (front ledge ~9, rear block ~12), with
    # columns on every face, the inner (gap) face included
    wr = o.right
    b.box_rock(gap_r + 0.5, sp.W - 1.0, -2.2, yb, 0.0, 11.4, [wr], mix=b.core_mix)
    b.box_rock(gap_r + 0.5, sp.W - 1.2, yf + 1.0, -1.8, 0.0, 8.2, [wr], mix=b.core_mix)
    for (y0, y1, h) in ((yf - 0.4, -2.4, 8.8), (-2.4, 1.4, 12.0), (1.4, 5.4, 10.9), (5.4, yb, 11.7)):
        b.column(gap_r + 1.5, (y0 + y1) / 2, 1.7, (y1 - y0) / 2 * 1.08, h, [wr], ylim=(yf - 1.0, yb),
                 xlim=(-sp.W, sp.W), zmax=12.4, slant=1.2)
    for (x0, x1, h) in ((gap_r, 9.0, 8.4), (9.0, 11.8, 9.3), (11.8, sp.W, 8.7)):
        b.column((x0 + x1) / 2, yf + 1.6, (x1 - x0) / 2 * 1.1, 2.2, h, [wr], ylim=(yf - 1.0, yb),
                 xlim=(-sp.W, sp.W), slant=0.9)
    for (y0, y1, h) in ((-2.6, 1.6, 11.2), (1.6, 5.6, 11.9), (5.6, yb, 10.8)):
        b.column(sp.W - 1.6, (y0 + y1) / 2, 1.7, (y1 - y0) / 2 * 1.08, h, [wr], ylim=(yf - 1.0, yb),
                 xlim=(-sp.W, sp.W), zmax=12.4, slant=0.9)
    # shards at the right mass's foot
    b.column(sp.W - 1.8, yf - 1.2, 1.5, 1.3, 5.6, [wr], point=0.7, lean=(0.04, -0.05), xlim=(-sp.W, sp.W))
    b.column(gap_r + 1.6, yf - 1.6, 1.3, 1.1, 3.8, [wr], point=0.7, lean=(-0.02, -0.06), xlim=(-sp.W, sp.W))
    # -- caps: left (over the stub's root), right rear block and right front step
    ringL, cL = b.cap([(-11.2, yf), (-3.8, yfs), (-3.8, yb + 0.4), (-11.2, yb + 0.4)], sp.RT + 0.6,
                      dome=0.7, clampx=(-sp.W - 0.35, 99), clampy=(-99, yb + 0.4), thick=1.4)
    top_dress(b, ringL, cL, sp.RT + 0.6, 0.7, 3, hang_xs=[(-3.4, yfs - 0.5, 1.9), (-10.6, yf - 0.3, 2.3)],
              pebbles=3, flowers=7, tufts=3)
    for x, y in ((-12.6, yf + 0.6), (-13.0, yf + 6.0)):
        b.bush(x, y, sp.RT - b.drop(x - 1.2) - 1.0, rng.uniform(1.2, 1.5))
    ringR, cR = b.cap([(gap_r, -2.4), (sp.W, -2.4), (sp.W, yb + 0.4), (gap_r, yb + 0.4)], 12.6, dome=0.4,
                      clampx=(gap_r - 0.2, sp.W + 0.35), clampy=(-99, yb + 0.4), thick=1.3)
    top_dress(b, ringR, cR, 12.6, 0.4, 5, pebbles=2, flowers=5, tufts=2, sizes=(1.3, 1.8))
    ringS, cS = b.cap([(gap_r, yf - 0.2), (sp.W, yf - 0.2), (sp.W, -2.2), (gap_r, -2.2)], 9.4, dome=0.25,
                      clampx=(gap_r - 0.2, sp.W + 0.35), clampy=(-99, -1.9), thick=1.2)
    top_dress(b, ringS, cS, 9.4, 0.25, 2, pebbles=1, flowers=3, tufts=2, sizes=(1.0, 1.3))
    # -- fallen chunks of the span at the base of the gap (passage kept >= 5 wide)
    b.boulder((gap_l + 1.3, yf - 0.6), (2.8, 2.4, 2.3))
    b.boulder((gap_r - 1.1, yf + 2.2), (2.4, 2.2, 2.0))
    b.boulder((gc + 2.2, yf - 3.0), (1.8, 1.6, 1.3))
    b.boulder((-sp.W + 2.4, yf - 1.4), (3.8, 3.2, 3.8))
    b.ground([(-sp.W - 0.3, yf - sp.apron + 0.4), (sp.W + 0.3, yf - sp.apron + 0.4), (sp.W + 0.3, yb),
              (-sp.W - 0.3, yb)], clampx=(-sp.W - 0.35, sp.W + 0.35))
    floor(b, sp, o, sill=False, pebbles=5)
    base_dress(b, sp, o, 12, tufts=12, flowers=12, rubble=6)
    connector(b, sp, None, ztop=11.0, side=False, xl=gap_r + 0.3)
    connector(b, sp, None, ztop=sp.RT - 0.4, side=False, xr=gap_l - 0.1)
    obj = b.finish("variant", "precise", 6000, "collapsed span: lean-over broken stub on the left, stepped lower "
                   "right mass, 10-wide walkable gap with fallen chunks")
    return obj


def build_left_mass(kit):
    """Left pillar as the reference explodes it: a narrower columnar pillar
    under a wide bulging capital (the springer of the arch) that overhangs its
    front and inner side, a grass-tuft top and a big boulder at its foot."""
    RT = 18.4
    yf, yb = -7.6, 8.6                     # the shaft spans x -14.6..-5.4
    b = Builder(kit, "NaturalArchLeftRockMass", 441)
    b.yfront = yf
    rng = b.rng
    pillar(b, -14.6, -5.4, yf, yb, 12.6, nx=2, ny=4)
    # the springer: a cluster of chunky faceted lumps bulging ~0.5-0.8 past
    # the shaft from mid-height to the top (a boulder cluster, not a flare)
    b.box_rock(-13.4, -6.6, yf + 1.2, yb - 1.2, 10.0, RT - 0.2)
    lumps = (((-12.3, yf + 2.2, RT - 3.6), (2.6, 3.0, 3.4)),
             ((-7.7, yf + 2.0, RT - 4.4), (2.6, 3.0, 3.9)),
             ((-12.0, (yf + yb) / 2 + 0.6, RT - 3.8), (2.7, 3.2, 3.6)),
             ((-7.6, (yf + yb) / 2 - 0.4, RT - 3.2), (2.6, 3.0, 3.2)),
             ((-12.2, yb - 2.8, RT - 3.2), (2.6, 2.8, 3.2)),
             ((-7.8, yb - 2.6, RT - 3.0), (2.6, 2.8, 3.0)))
    for (cx, cy, cz), r in lumps:
        pts = blob_pts(rng, (cx, cy, cz), r, n=14)
        b.rock(pts, xlim=(-15.0, -5.0), ylim=(yf - 1.0, yb), zmax=RT, merge=6.0)
    ring, c = b.cap([(-14.3, yf + 0.6), (-5.7, yf + 0.6), (-5.7, yb - 0.4), (-14.3, yb - 0.4)],
                    RT + 0.6, dome=0.3, over=(0.2, 0.6), clampx=(-15.1, -4.9))
    top_dress(b, ring, c, RT + 0.6, 0.3, 2, pebbles=2, flowers=4, tufts=4, sizes=(1.1, 1.4))
    # the big chunky boulder at its foot (front-left, as in the reference)
    b.boulder((-11.4, yf - 3.0), (5.8, 4.8, 5.0), n=13, ylim=(yf - 6.0, yb), xlim=(-15.0, -5.0))
    b.boulder((-7.4, yf - 1.6), (2.6, 2.2, 2.2), n=8, ylim=(yf - 6.0, yb))
    return b.finish("part", "hull", 3000, "left pillar with a bulging boulder-cluster springer, grass top and "
                    "a chunky foot boulder")


def build_right_mass(kit):
    sp = Spec(RT=16.0)
    b = Builder(kit, "NaturalArchRightRockMass", 452)
    o = Opening(sp.w2, sp.s, sp.rz, sp.angles)
    b.yfront = sp.yfs
    arch_mass(b, sp, 1, o, ledge_bushes=False)
    # exploded on its own, its inner (hole) face is columns too, not a flat core
    rng = b.rng
    y = sp.yf - 0.2
    while y < sp.yb - 1.0:
        w = min(rng.uniform(3.6, 4.8), sp.yb - y)
        b.column(sp.w2 + 1.5, y + w / 2, 1.7, w / 2 * 1.08, sp.RT - rng.uniform(0.3, 2.2), [o.right],
                 ylim=(sp.yf - 0.8, sp.yb), zmax=sp.RT, slant=0.9)
        y += w * 0.9
    ring, c = b.cap([(o.w2 + 0.4, sp.yf + 0.3), (sp.W - 0.5, sp.yf + 0.3), (sp.W - 0.5, sp.yb - 0.3),
                     (o.w2 + 0.4, sp.yb - 0.3)], sp.RT + 0.6, dome=0.3, over=(0.2, 0.6),
                    clampx=(o.w2 - 0.2, sp.W + 0.2), clampy=(-99, sp.yb + 0.2))
    top_dress(b, ring, c, sp.RT + 0.6, 0.3, 2, pebbles=2, flowers=4, tufts=3, sizes=(1.2, 1.5))
    return b.finish("part", "hull", 3000, "right pillar with grass top and bushes")


def build_span(kit):
    """Bulky lintel as the reference explodes it: one solid rock band the full
    22 wide and 18 deep, cut across into blocks whose undersides are the 5
    soffit facets of a bridge arch rising 4 from springer feet at both ends;
    each block bulges into 2-3 big facets on its front, back and (at the ends)
    its end face. The grass cap only lips 0.3-0.7 over the rock."""
    b = Builder(kit, "NaturalArchTopSpan", 461)
    rng = b.rng
    HW, YF, YB, ZT = 11.0, -8.6, 8.6, 6.5
    o = Opening(7.6, 0.0, 4.0, (180, 144, 108, 72, 36, 0))
    b.holes.append(o)
    b.yfront = YF
    arc = o.arc

    def zb(x):
        if abs(x) >= o.w2:
            return 0.0
        for (x0, z0), (x1, z1) in zip(arc, arc[1:]):
            if x0 <= x <= x1:
                return z0 + (z1 - z0) * (x - x0) / (x1 - x0)
        return 0.0

    def zt(x):
        return ZT + 0.5 * (1 - (x / HW) ** 2)

    xs = [-HW] + [p[0] for p in arc] + [HW]
    ov = 0.3
    for i, (xa, xb) in enumerate(zip(xs, xs[1:])):
        yf = YF + rng.uniform(-0.2, 0.5)
        yb = YB - rng.uniform(-0.2, 0.5)
        top = [zt(x) - rng.uniform(0.0, 0.35) for x in (xa, xb)]
        pts = []
        for k, x in enumerate((xa, xb)):
            outer = abs(x) >= HW - 0.01
            ins = 1.4 if outer else 0.0          # rounded plan at the outer ends
            z0, z1 = zb(x), top[k]
            for y in (yf + ins, yb - ins):
                pts.append(Vector((x, y, z0)))
                pts.append(Vector((x, y, z1 - 0.7)))
            for y in (yf + ins + 0.6, yb - ins - 0.6):
                pts.append(Vector((x, y, z1)))
            if outer:
                # the end face bulges into a couple of big facets
                sd = 1 if x > 0 else -1
                pts.append(Vector((x - sd * 1.0, yf, z0)))
                pts.append(Vector((x - sd * 1.0, yb, z0)))
                pts.append(Vector((x - sd * 1.0, yf + 0.3, z1 - 0.6)))
                pts.append(Vector((x - sd * 1.0, yb - 0.3, z1 - 0.6)))
                pts.append(Vector((x + sd * 0.5, rng.uniform(-3.0, 3.0), (z0 + z1) / 2 + rng.uniform(-0.6, 0.6))))
            else:
                # overlap into the neighbour (inset, so its buried end face culls)
                sd = 1 if x == xb else -1
                xo = x + sd * ov
                for y in (yf + 0.5, yb - 0.5):
                    pts.append(Vector((xo, y, zb(xo) + 0.25)))
                    pts.append(Vector((xo, y, z1 - 0.5)))
        # bulging front and back: big facets, not a flat wall
        for y, sd in ((yf, -1), (yb, 1)):
            for f in (0.35, 0.7):
                xm = xa + (xb - xa) * rng.uniform(0.3, 0.7)
                zm = zb(xm) + (zt(xm) - zb(xm)) * f
                pts.append(Vector((xm, y + sd * rng.uniform(0.7, 1.2), zm + rng.uniform(-0.3, 0.3))))
        b.rock(pts, merge=3.0)
    # grass cap following the rock's plan, a 0.3-0.7 lip
    corners = [(-10.3, YF + 1.2), (-9.2, YF + 0.4), (9.2, YF + 0.4), (10.3, YF + 1.2),
               (10.3, YB - 1.2), (9.2, YB - 0.4), (-9.2, YB - 0.4), (-10.3, YB - 1.2)]
    ztop = ZT + 0.55
    ring, c = b.cap(corners, ztop, dome=0.35, over=(0.2, 0.6), thick=0.8)
    top_dress(b, ring, c, ztop, 0.35, 3, pebbles=3, flowers=6, tufts=3, sizes=(1.1, 1.45))
    return b.finish("part", "precise", 2500, "bulky lintel: full-width rock band whose underside is a 5-facet "
                    "bridge arch rising 4 between springer feet; grass top with 3 clumps")


def build_sill(kit):
    b = Builder(kit, "NaturalArchGroundSill", 471)
    a = b.a
    a.box((14.0, 10.0, 0.6), loc=(0, 0, 0), mat=SLAB, bevel=0.2, base=True)
    # a chipped corner notch and a crack seam across the top
    a.strip([(-7.0, 1.4), (-3.2, 0.6), (-1.0, 1.8), (2.4, 0.2), (7.0, 0.9)], 0.16, 0.05, loc=(0, 0, 0.58),
            mat=EARTH)      # soil caught in the crack: a different material from the slab
    drop_bottoms(a)
    obj = a.finish()
    return kit.tag(obj, "part", collision="box", budget=200, notes="pale stone floor slab under the opening")


def build(kit):
    return [build_hero(kit), build_left_mass(kit), build_sill(kit), build_span(kit), build_right_mass(kit),
            build_narrow(kit), build_wide(kit), build_broken(kit)]
