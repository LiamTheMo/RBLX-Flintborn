"""W06 row 1: LowBush, a thick, faceted, low leafy bush with a forked brown trunk.

Assets
  LowBush           hero: irregular dome of broad star-rosette leaf clumps (~8 x 6.5 x 5),
                    a thick trunk forking into limbs, visible through a gap in the lower
                    front and one on the +X side, ~9 white five-petal flowers spread over
                    the outer clumps, two big flat grey rocks in front plus two at the
                    sides, moss tufts and a small soil patch
  LeafClumpLarge    part: one rosette clump, ~2.4 dia
  LeafClumpMedium   part: ~1.8 dia
  LeafClumpSmall    part: ~1.2 dia
  BranchStem        part: open Y-fork trunk with flat cut ends, plus a second straight
                    cut stem with one short side branch (the sheet draws both pieces)
  BushBerries       part: cluster of five red berries on a tiny stem
  BushFlower        part: one white flower with a yellow centre and leaves under it
  DomeBush          variant A: broad, closed round dome (~6.3 x 6 x 4.3), no trunk visible
  HedgeBush         variant B: long hedge segment along X (~9 x 3.5 x 3.7), flat top
  OpenWoodyBush     variant C: open woody bush, bare forking branches, clumps at the tips

Technique
- Foliage uses the shared helpers only: each crown is Asset.canopy (a dense, lumpy
  mass of big star clumps; hero and DomeBush one mass each, HedgeBush four in a row,
  OpenWoodyBush one small mass per branch end) and hand-placed clumps (the hero's low
  ring round the sides/back, leaving the front trunk gap open) and the clump parts are
  Asset.leaf_cluster. Bark and clumps buried inside a canopy are culled.
- Flowers (a cupped five-petal star with a yellow cone centre, 45 triangles) are placed
  by ray-casting onto the finished foliage, so they sit on outer clump faces.
- Faces buried inside another clump (or bark inside a clump) and faces lying flat on
  the ground are culled; everything is clamped to z >= 0.
- ONE colour per material: all foliage is `w06_bushleaf`; lime tops / dark undersides on
  the sheet are lighting. Tint is a small random per-part variation (+/-5%).
- VFX: the bushes are harvestable (berries/leaves), so each bush carries one
  harvest_hit socket on its front face with leaf-green chips. No other effects.
"""

import json
import math

import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

SUBJECT = "LowBush"
ROW = 1
# Sheet palette shared by every W06 module (copied verbatim from the sheet plan).
# flower_white, flower_yellow and berry are existing flintkit keys used as-is.
# w06_bushleaf replaces the plan's `leaf` (#6C9A28) for ALL row-1 foliage: with the studio
# light, #6C9A28 rendered pale olive (lit faces ~#8CBF3C, sat 0.69) against the sheet's
# vivid lime-to-deep-green clumps (lit ~#C4E130, shadow ~#1C5002, sat 0.8-0.97), so the
# plan's own note applies: darken/saturate the foliage base colour. Still ONE leaf colour.
PALETTE = {
    "w06_bushleaf": ("#54A006", 0.8, 0, 0),
    "w06_moss": ("#ACC722", 0.9, 0, 0),
    "w06_stone": ("#B1ADA9", 0.9, 0, 0),
    "w06_bark": ("#8D6237", 0.9, 0, 0),
    "w06_soil": ("#6E4B2B", 0.95, 0, 0),
    "w06_berry": ("#C8201E", 0.5, 0, 0),
    "w06_petal": ("#F4F1E6", 0.8, 0, 0),
    "w06_pollen": ("#E8C23A", 0.8, 0, 0),
}

CAT = "Kit W06 LowBush"
TAU = 2 * math.pi
Z = Vector((0, 0, 1))
LEAF, BARK, STONE, MOSS, SOIL = "w06_bushleaf", "w06_bark", "w06_stone", "w06_moss", "w06_soil"
PETAL, CENTRE, BERRY = "w06_petal", "w06_pollen", "w06_berry"
# harvest_hit particle colours (VFX only, not mesh colours): leaf bits and green dust
LEAF_CHIPS = ["#62A808", "#4A8A0C"]
LEAF_DUST = ["#A6CF5A", "#86B444"]


def _ico_levels():
    """(subdiv for a 12-vert icosahedron, subdiv for the 42-vert sphere)."""
    bm = bmesh.new()
    n = len(bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)["verts"])
    bm.free()
    return (1, 2) if n == 12 else (0, 1)


LOW, STAR = _ico_levels()


def polar(r, az, z=0.0):
    return Vector((r * math.cos(az), r * math.sin(az), z))


def faces_of(verts):
    fs = set()
    for v in verts:
        fs.update(v.link_faces)
    return fs


def radial(centre, az, el, dist=14.0):
    """Ray (origin, direction) aimed at `centre` from direction (az, el) in degrees."""
    a, e = math.radians(az), math.radians(el)
    d = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))
    return Vector(centre) + d * dist, -d


def harvest(kit, obj, loc):
    """harvest_hit socket with leaf-green chips (the bush is picked for leaves/berries)."""
    em = json.loads(json.dumps(kit.vfx.KINDS["harvest_hit"]["emitters"]))
    for e in em:
        e["color"] = list(LEAF_CHIPS if e["name"] == "Chips" else LEAF_DUST)
        if e["name"] == "Dust":  # leaves shed little dust: a fainter, smaller puff
            e["size"] = [0.5, 1.2]
            e["transparency"] = [0.75, 1.0]
    kit.vfx.add(obj, "harvest_hit", loc, color=LEAF_CHIPS, emitters=em)


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


class Bush:
    def __init__(self, kit, name, seed):
        self.a = kit.flintkit.Asset(name, CAT, seed=seed, tint_var=0.04)
        self.rng = self.a.rng
        self.clumps = []  # (centre, r, squash, rotation matrix)
        self.leaf_faces = {}  # face -> clump index
        self.cullable = set()  # bark faces that may hide inside clumps
        self.blobs = []  # (centre, semi-axes) inner ellipsoids of canopy masses
        self.hub = Vector((0, 0.2, 0))

    @property
    def bm(self):
        return self.a.bm

    def _tri(self, vs, out):
        """New triangle facing along `out` (a world direction)."""
        f = self.bm.faces.new(vs)
        f.normal_update()
        if f.normal.dot(out) < 0:
            f.normal_flip()
        return f

    # -- leaves ------------------------------------------------------------------

    def clump(self, c, r, tilt=0.6, up=None, n=6, squash=0.8, facets=1, depth=0.9, sink=0.35):
        """One star-shaped lobed leaf clump (shared Asset.leaf_cluster) of radius r,
        centred about c. `up` (or, if None, the outward direction from the bush hub
        blended by `tilt`) is the clump's face direction; the clump's flat base is set
        `sink` x r below c along `up`, so c is roughly its middle."""
        c = Vector(c)
        if up is None:
            out = Vector((c.x - self.hub.x, c.y - self.hub.y, 0))
            up = (Z + out.normalized() * tilt) if out.length > 1e-3 else Z
        up = Vector(up).normalized()
        base = c - up * (sink * r)
        verts = self.a.leaf_cluster(r, loc=tuple(base), mat=LEAF, lobes=n, squash=squash,
                                    facets=facets, depth=depth, axis=tuple(up), floor=0.0)
        rot = up.to_track_quat("Z", "Y").to_matrix()
        idx = len(self.clumps)
        self.clumps.append((base + up * (0.3 * r), r, 0.6, rot))
        for f in faces_of(verts):
            self.leaf_faces[f] = idx
        return verts

    def shell(self, cen, semi, rings, gap=None, lift=0.4, sink=0.3, depth=0.6):
        """Dome of distinct big star clumps laid in stepped rings on an ellipsoid shell.
        rings: (elevation deg, count, radius, facets). Each clump faces out along the
        shell normal, lifted toward up by `lift`. `gap` (az deg, half-width deg) leaves a
        hole in rings below 20 deg elevation (trunk window)."""
        cen, semi = Vector(cen), Vector(semi)
        for ri, (el, n, r, fac) in enumerate(rings):
            off = self.rng.uniform(0, TAU)
            for k in range(n):
                az = off + TAU * k / n + self.rng.uniform(-0.12, 0.12)
                if gap and el < 20:
                    d = (math.degrees(az) - gap[0] + 180) % 360 - 180
                    if abs(d) < gap[1]:
                        continue
                e = math.radians(el + self.rng.uniform(-5, 5)) if n > 1 else math.radians(90)
                u = Vector((math.cos(e) * math.cos(az), math.cos(e) * math.sin(az), math.sin(e)))
                p = cen + Vector((u.x * semi.x, u.y * semi.y, u.z * semi.z))
                nrm = Vector((u.x / semi.x, u.y / semi.y, u.z / semi.z)).normalized()
                rr = r * (1 + self.rng.uniform(-0.08, 0.08))
                self.clump(p + nrm * 0.3 * rr, rr, up=(nrm + Z * lift), n=7, squash=1.0,
                           facets=fac, depth=depth, sink=sink)

    def canopy(self, centre, size, **kw):
        """A whole dense crown mass (shared Asset.canopy); bark and hand-placed clumps
        buried inside its inner ellipsoid are culled later."""
        kw.setdefault("floor", 0.0)
        verts = self.a.canopy(tuple(centre), tuple(size), mat=LEAF, **kw)
        self.blobs.append((Vector(centre), Vector(size) * 0.5 * 0.72))
        return verts

    # -- wood ----------------------------------------------------------------------

    def tube(self, pts, radii, sides=6, caps=(False, False), mat=BARK, cull=True, jitter=0.05):
        bm = self.bm
        pts = [Vector(p) for p in pts]
        n = len(pts)
        tans = [(pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized() for i in range(n)]
        ref = Vector((1, 0, 0)) if abs(tans[0].x) < 0.9 else Vector((0, 1, 0))
        nrm = tans[0].cross(ref).normalized()
        rings = []
        roll = self.rng.uniform(0, TAU)
        for i in range(n):
            if i:
                axis = tans[i - 1].cross(tans[i])
                if axis.length > 1e-6:
                    nrm = Matrix.Rotation(tans[i - 1].angle(tans[i]), 3, axis.normalized()) @ nrm
                nrm = (nrm - tans[i] * nrm.dot(tans[i])).normalized()
            bi = tans[i].cross(nrm)
            ring = []
            for j in range(sides):
                th = roll + TAU * j / sides
                rr = radii[i] * (1 + self.rng.uniform(-jitter, jitter))
                ring.append(bm.verts.new(pts[i] + rr * (math.cos(th) * nrm + math.sin(th) * bi)))
            rings.append(ring)
        faces = []
        for i in range(n - 1):
            mid = (pts[i] + pts[i + 1]) / 2
            for j in range(sides):
                k = (j + 1) % sides
                f = bm.faces.new((rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]))
                f.normal_update()
                if f.normal.dot(f.calc_center_median() - mid) < 0:
                    f.normal_flip()
                faces.append(f)
        for end, ring, d in ((0, rings[0], pts[0] - pts[1]), (1, rings[-1], pts[-1] - pts[-2])):
            if caps[end]:
                f = bm.faces.new(ring)
                f.normal_update()
                if f.normal.dot(d) < 0:
                    f.normal_flip()
                faces.append(f)
        verts = [v for r in rings for v in r]
        self.a._finish(verts, mat, tint=1.0 + self.rng.uniform(-0.04, 0.04))
        if cull:
            self.cullable.update(faces)
        return verts

    def roots(self, base, n=3, phase=0.0, reach=0.95, r0=0.26, h=0.55, azs=None):
        base = Vector(base)
        azs = azs or [phase + TAU * k / n + self.rng.uniform(-0.3, 0.3) for k in range(n)]
        for az in azs:
            pts = [base + Vector((0, 0, h)), base + polar(reach * 0.55, az, h * 0.3),
                   base + polar(reach, az, 0.0)]
            self.tube(pts, [r0, r0 * 0.7, r0 * 0.3], sides=5, caps=(False, True), cull=False)

    # -- dressing ------------------------------------------------------------------

    def flower(self, p, n, d=0.8, spin=None):
        """Five-petal flower of diameter d at p facing along n: a shallow cupped star
        (20-point outline, top and underside fans) with a yellow cone centre."""
        bm = self.bm
        L = d / 2
        spin = self.rng.uniform(0, TAU) if spin is None else spin
        n = Vector(n).normalized()
        rot = n.to_track_quat("Z", "Y").to_matrix()
        p = Vector(p)

        def V(x, y, z):
            return bm.verts.new(rot @ Vector((x, y, z)) + p)

        up, down = rot @ Z, -(rot @ Z)
        centre = V(0, 0, 0.0)
        under = V(0, 0, -0.07 * L)
        outline = []
        for i in range(5):
            a = spin + i * TAU / 5
            for rr, da, z in ((0.26, -TAU / 10, 0.04), (0.8, -0.33, 0.13), (1.0, 0.0, 0.16),
                              (0.8, 0.33, 0.13)):
                outline.append(V(rr * L * math.cos(a + da), rr * L * math.sin(a + da), z * L))
        m = len(outline)
        for i in range(m):
            o0, o1 = outline[i], outline[(i + 1) % m]
            self._tri((centre, o0, o1), up)
            self._tri((under, o1, o0), down)
        petals = [centre, under] + outline
        self.a._finish(petals, PETAL, tint=1.0)
        # yellow centre: a low five-sided cone rising out of the petals
        tip = V(0, 0, 0.24 * L)
        base = [V(0.26 * L * math.cos(spin + TAU * (i + 0.5) / 5),
                  0.26 * L * math.sin(spin + TAU * (i + 0.5) / 5), 0.0) for i in range(5)]
        for i in range(5):
            b0, b1 = base[i], base[(i + 1) % 5]
            mid = (b0.co + b1.co) / 2
            self._tri((tip, b0, b1), mid - p + up * 0.1)
        self.a._finish([tip] + base, CENTRE, tint=1.0)
        return petals

    def flowers(self, rays, d=0.8):
        """Cull hidden foliage, then ray-cast each (origin, direction) onto the outer
        leaf surface and put a flower there facing out (and a little up/at the ray)."""
        self.cull()
        bm = self.bm
        bm.normal_update()
        bm.faces.ensure_lookup_table()
        tree = BVHTree.FromBMesh(bm)
        leaf_mi = self.a._mi(LEAF)
        spots = []
        for origin, direction in rays:
            direction = Vector(direction).normalized()
            hit, nrm, idx, _ = tree.ray_cast(Vector(origin), direction)
            if hit is None or bm.faces[idx].material_index != leaf_mi:
                continue
            nrm = nrm if nrm.dot(direction) < 0 else -nrm
            face = (nrm * 0.6 - direction * 0.6 + Z * 0.2).normalized()
            spots.append((hit + nrm * 0.07, face))
        for p, n in spots:
            self.flower(p, n, d=d)
        return len(spots)

    def rock(self, loc, size, rotz=0.0, sink=0.12):
        return self.a.rock(size, loc=(loc[0], loc[1], 0), rot=(0, 0, rotz), mat=STONE, subdiv=STAR,
                           rough=0.1, facets=10, sink=sink)

    def moss(self, loc, s=1.0):
        return self.a.ico((0.34 * s, 0.28 * s, 0.17 * s), loc=(loc[0], loc[1], 0.06 * s), mat=MOSS,
                          subdiv=LOW, rot=(0, 0, self.rng.uniform(0, TAU)), jitter=0.12,
                          tint=1.0 + self.rng.uniform(-0.04, 0.04))

    def soil(self, rx, ry, n=11, h=0.05, centre=(0, 0)):
        pts = []
        for i in range(n):
            a = TAU * i / n
            k = 1 + self.rng.uniform(-0.06, 0.06)
            pts.append((centre[0] + rx * k * math.cos(a), centre[1] + ry * k * math.sin(a)))
        return self.a.poly_prism(pts, h, mat=SOIL, tint=1.0)

    # -- output --------------------------------------------------------------------

    def _inside(self, p, skip):
        for i, (c, r, sq, rot) in enumerate(self.clumps):
            if i == skip:
                continue
            q = rot.transposed() @ (p - c)
            q.z /= sq
            if q.length < r * 0.62:
                return True
        for c, s in self.blobs:
            d = p - c
            if (d.x / s.x) ** 2 + (d.y / s.y) ** 2 + (d.z / s.z) ** 2 < 1.0:
                return True
        return False

    def cull(self, keep_ground=False):
        bm = self.bm
        for v in bm.verts:
            if v.co.z < 0:
                v.co.z = 0.0
        dead = []
        for f in bm.faces:
            cen = f.calc_center_median()
            if f in self.leaf_faces or f in self.cullable:
                if self._inside(cen, self.leaf_faces.get(f, -1)):
                    dead.append(f)
                    continue
            if not keep_ground and max(v.co.z for v in f.verts) < 0.005:
                dead.append(f)
        if dead:
            bmesh.ops.delete(bm, geom=dead, context="FACES")
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context="VERTS")
        self.leaf_faces = {f: i for f, i in self.leaf_faces.items() if f.is_valid}
        self.cullable = {f for f in self.cullable if f.is_valid}

    def finish(self, keep_ground=False):
        self.cull(keep_ground)
        return self.a.finish()


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------

# Low skirt of hand-placed clumps (azimuth deg, z, radius) round the sides and back. They sit
# high and well inside the canopy rim so they overlap it by a third or more: one continuous
# dome from the side, no tier. Azimuth -90 is the front (-Y); -128..-52 stays open for the trunk.
HERO_LOW = [(-150, 1.0, 1.0), (-30, 1.0, 1.0), (90, 1.1, 1.05)]
# flower rays: (azimuth, elevation) aimed at (0, 0.2, 1.2); front is azimuth -90.
HERO_FLOWERS = [(-150, 30), (-125, 48), (-100, 34), (-75, 58), (-55, 30), (-25, 42), (-95, 72), (10, 40)]


def lowbush_hero(kit):
    b = Bush(kit, "LowBush", 601)
    b.hub = Vector((0, 0.1, 0))
    b.soil(0.9, 0.7, h=0.04, centre=(0.0, -0.75))
    base = Vector((0.0, -0.75, 0))
    b.tube([base, base + Vector((0.02, 0, 0.7)), base + Vector((0, 0.05, 1.3))], [0.58, 0.5, 0.46],
           sides=7, cull=False)
    b.roots(base, azs=[-2.3, -0.85, 0.45, 2.55], reach=0.95, r0=0.34, h=0.55)
    F = base + Vector((0, 0.05, 1.1))
    b.tube([F, (-0.8, -1.0, 1.7), (-1.5, -1.2, 2.3)], [0.44, 0.36, 0.28])     # left
    b.tube([F, (0.8, -1.05, 1.65), (1.5, -1.25, 2.2)], [0.43, 0.35, 0.28])    # right
    b.tube([F, (0.1, -1.1, 2.0), (0.05, -1.4, 2.7)], [0.4, 0.32, 0.25])       # up-front
    # the crown: one dense dome of a dozen big star clumps (shared canopy helper)
    # the crown: ~20 big distinct star clumps in stepped rings over a dark inner core
    b.a.ico((1.95, 1.4, 1.7), loc=(0, 0.55, 1.8), mat=LEAF, subdiv=LOW, jitter=0.1)
    b.shell((0, 0.2, 1.2), (2.12, 1.9, 2.05),
            [(90, 1, 1.25, 2), (50, 5, 1.2, 2), (14, 7, 1.15, 2), (-22, 6, 0.95, 1)],
            gap=(-90, 26))
    for az, r in ((-128, 0.85), (-52, 0.8)):  # clumps flanking the trunk gap
        a = math.radians(az)
        b.clump((2.0 * math.cos(a), 2.0 * math.sin(a), 0.8), r, tilt=0.9, depth=0.6)
    b.flowers([radial((0, 0.2, 1.5), az, el) for az, el in HERO_FLOWERS], d=0.85)
    b.rock((-1.25, -2.55), (2.1, 1.4, 0.75), 0.25)    # two big flat front slabs
    b.rock((1.2, -2.5), (1.9, 1.35, 0.8), -0.35)
    b.rock((2.45, -1.4), (0.75, 0.6, 0.4), 0.6)
    for x, y, s in ((-2.3, -2.0, 0.85), (-0.05, -2.75, 0.75), (2.2, -2.2, 0.85),
                    (2.6, -0.3, 0.75), (-2.65, -0.6, 0.8), (-0.7, -1.75, 0.7)):
        b.moss((x, y), s)
    return b.finish()


# ---------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------


def clump_part(kit, name, r, seed):
    b = Bush(kit, name, seed)
    b.a.leaf_cluster(r, loc=(0, 0, 0), mat=LEAF, lobes=7, squash=0.85, facets=1, depth=1.3,
                     floor=0.0, seed=seed)
    return b.finish()


def branch_stem(kit):
    """The sheet's two stem pieces in one part: an open Y (a short thick stem splitting
    into two splayed branches with flat cut ends) and, beside it, a straight cut stem
    with one short side branch."""
    b = Bush(kit, "BranchStem", 611)
    o = Vector((-0.45, 0, 0))
    F = o + Vector((0, 0, 1.05))
    b.tube([o, o + Vector((0, 0, 0.55)), F + Vector((0, 0, 0.1))], [0.42, 0.36, 0.33], sides=7,
           caps=(False, True), cull=False)
    b.tube([F, o + Vector((-0.4, 0.15, 1.6)), o + Vector((-0.72, 0.3, 2.4))], [0.27, 0.24, 0.22],
           sides=7, caps=(False, True), cull=False)
    b.tube([F, o + Vector((0.38, -0.15, 1.5)), o + Vector((0.68, -0.3, 2.2))], [0.26, 0.23, 0.21],
           sides=7, caps=(False, True), cull=False)
    b.roots(o, azs=[-1.75, 1.45, 3.0], reach=0.65, r0=0.24, h=0.4)
    s = Vector((0.75, 0.15, 0))
    b.tube([s, s + Vector((0.02, 0, 0.9)), s + Vector((-0.04, 0.02, 1.85))], [0.25, 0.22, 0.2],
           sides=6, caps=(False, True), cull=False)
    b.tube([s + Vector((0, 0, 1.0)), s + Vector((0.25, 0, 1.3)), s + Vector((0.45, 0, 1.6))],
           [0.15, 0.13, 0.12], sides=6, caps=(False, True), cull=False)
    return b.finish()


def berries(kit):
    b = Bush(kit, "BushBerries", 612)
    a = b.a
    top = Vector((0, 0.05, 0.62))
    b.tube([(0, 0, 0.0), (0, 0.02, 0.3), top], [0.04, 0.035, 0.03], sides=4, cull=False,
           caps=(True, False))
    spots = [(-0.17, -0.05, 0.36), (0.16, -0.08, 0.34), (0.0, 0.14, 0.4), (0.02, -0.12, 0.62),
             (0.22, 0.1, 0.6)]
    for p in spots:
        p = Vector(p)
        b.tube([top, p + Vector((0, 0, 0.12))], [0.022, 0.018], sides=3, cull=False)
        verts = bmesh.ops.create_uvsphere(a.bm, u_segments=6, v_segments=5, radius=0.175)["verts"]
        a.transform(verts, p, (0, 0, b.rng.uniform(0, TAU)))
        a._finish(verts, BERRY, tint=1.0)
    return b.finish(keep_ground=True)


def flower_part(kit):
    b = Bush(kit, "BushFlower", 613)
    a = b.a
    b.tube([(0, 0, 0), (0.0, 0.02, 0.28)], [0.025, 0.022], sides=4, mat=LEAF, cull=False)
    leaf = [(0.0, 0.0), (0.12, -0.07), (0.26, -0.05), (0.34, 0.0), (0.26, 0.05), (0.12, 0.07)]
    for ang, tilt in ((-0.6, 0.35), (2.4, 0.4)):
        a.poly_prism(leaf, 0.03, loc=(0, 0.02, 0.12), rot=(0, -tilt, ang), mat=LEAF, tint=1.0)
    b.flower(Vector((0, 0.02, 0.3)), Vector((0, -0.25, 1)), d=0.62)
    return b.finish(keep_ground=True)


# ---------------------------------------------------------------------------
# Variants
# ---------------------------------------------------------------------------


def dome_bush(kit):
    b = Bush(kit, "DomeBush", 621)
    b.hub = Vector((0, 0, 0))
    b.soil(1.6, 1.5, h=0.04)
    # a closed round dome down to the ground: one canopy, clipped flat at z=0
    b.a.ico((1.9, 1.8, 1.7), loc=(0, 0, 1.2), mat=LEAF, subdiv=LOW, jitter=0.1)
    b.shell((0, 0, 1.0), (2.05, 2.0, 2.0),
            [(90, 1, 1.2, 2), (48, 5, 1.15, 2), (12, 7, 1.1, 2), (-25, 6, 0.95, 1)])
    b.flowers([radial((0, 0, 1.2), az, el) for az, el in
               ((-150, 18), (-118, 32), (-88, 12), (-60, 34), (-30, 16), (-100, 56))], d=0.75)
    b.rock((-1.8, -2.55), (1.5, 1.0, 0.5), 0.3)
    b.rock((2.0, -2.15), (1.3, 0.9, 0.45), -0.5)
    for x, y in ((-0.7, -2.75), (1.1, -2.6), (2.8, -0.6)):
        b.moss((x, y), 0.85)
    return b.finish()


def hedge_bush(kit):
    b = Bush(kit, "HedgeBush", 622)
    b.hub = Vector((0, 0, 0))
    # three overlapping canopy masses in a row make a long, low hedge with a level,
    # lumpy top line and rounded ends
    b.a.ico((3.1, 1.2, 1.3), loc=(0, 0, 1.2), mat=LEAF, subdiv=LOW, jitter=0.1)
    for x in (-2.25, 0.0, 2.25):
        b.shell((x, 0, 0.9), (1.3, 1.2, 1.5),
                [(90, 1, 1.1, 1), (40, 4, 1.05, 1), (-8, 5, 0.95, 1)])
    b.flowers([((x, -10, z), (0, 1, -0.12)) for x, z in ((-2.1, 2.6), (0.3, 2.0), (2.2, 2.5))],
              d=0.75)
    for x, s in ((-2.3, (0.8, 0.6, 0.35)), (0.8, (0.9, 0.6, 0.4)), (3.0, (0.7, 0.55, 0.3))):
        b.rock((x, -1.85), s, b.rng.uniform(-0.5, 0.5))
    for x in (-3.0, -0.6, 2.0):
        b.moss((x, -1.85), 0.8)
    return b.finish()


def open_woody(kit):
    b = Bush(kit, "OpenWoodyBush", 623)
    b.hub = Vector((0, 0, 1.5))
    b.soil(1.2, 1.0, h=0.04)

    def P(x, y, z):
        return Vector((x * 1.3, y * 1.5, z))

    base = Vector((0, 0, 0))
    A = Vector((0.05, 0.0, 1.3))
    b.tube([base, (0.03, 0, 0.65), A], [0.78, 0.65, 0.58], sides=7, cull=False)
    b.roots(base, n=4, phase=0.5, reach=1.15, r0=0.38, h=0.6)
    L, R = P(-1.2, -0.25, 2.35), P(1.15, 0.15, 2.3)
    b.tube([A + Vector((0, 0, -0.1)), P(-0.6, -0.1, 1.85), L], [0.38, 0.32, 0.27])
    b.tube([L, P(-1.6, -0.35, 2.5), P(-1.95, -0.45, 2.75)], [0.25, 0.21, 0.17])     # low left
    b.tube([L, P(-1.15, 0.35, 3.2), P(-1.05, 0.8, 3.9)], [0.25, 0.21, 0.17])        # high left
    b.tube([A + Vector((0, 0, -0.1)), P(0.6, 0.05, 1.8), R], [0.36, 0.31, 0.26])
    b.tube([R, P(1.6, 0.0, 2.8), P(1.85, 0.1, 3.35)], [0.25, 0.21, 0.17])          # right
    b.tube([A, P(0.15, -0.25, 2.6), P(0.2, -0.5, 4.0)], [0.34, 0.27, 0.2])        # top
    # one canopy mass (separate clump group) on each branch end
    # a group of 3 distinct star clumps on each branch end: airy, separated crown
    for x, y, z in ((-1.95, -0.45, 2.75), (-1.05, 0.8, 3.9), (0.2, -0.5, 4.0), (1.85, 0.1, 3.35)):
        t = P(x, y, z)
        b.clump(t + Vector((0, 0, 0.4)), 0.95, tilt=0.3, facets=2, depth=0.6, squash=1.1)
        ph = b.rng.uniform(0, TAU)
        for k in range(3):
            b.clump(t + polar(0.8, ph + k * 2.1, 0.0), 0.72, tilt=0.7, depth=0.6, squash=1.1)
    b.rock((-0.95, -0.95), (0.8, 0.6, 0.4), 0.4)
    b.rock((1.05, -0.7), (0.7, 0.55, 0.35), -0.3)
    b.rock((0.5, 1.1), (0.6, 0.5, 0.3), 1.0)
    for x, y in ((-0.35, -1.15), (0.6, -1.15), (-1.2, 0.4), (1.3, 0.3)):
        b.moss((x, y), 0.85)
    return b.finish()


# ---------------------------------------------------------------------------

HIT_NOTE = (" VFX_harvest_hit: leaf-green chip burst on the front foliage at chest height, fired on "
            "each pick (berries/leaves).")


def build(kit):
    out = []
    hero = lowbush_hero(kit)
    harvest(kit, hero, (0.0, -0.4, 2.5))
    out.append(kit.tag(hero, "hero", collision="hull", budget=4000,
                       notes="Low leafy bush ~6 x 6 x 4.5: one dense dome of big star leaf clumps "
                             "(canopy plus overlapping side/back clumps), thick trunk forking into 3 limbs seen through the lower front "
                             "gap, ~7 white flowers over the front and sides, two big front "
                             "rocks, side rocks, moss and soil." + HIT_NOTE))
    for name, r, seed, budget, cap in (("LeafClumpLarge", 1.2, 602, 300, "Leaf Clump (large)"),
                                       ("LeafClumpMedium", 0.9, 603, 250, "Leaf Clump (medium)"),
                                       ("LeafClumpSmall", 0.6, 604, 200, "Leaf Clump (small)")):
        out.append(kit.tag(clump_part(kit, name, r, seed), "part", collision="none", budget=budget,
                           notes=f"{cap}: one lobed rosette clump for kit-bashing bushes."))
    out.append(kit.tag(branch_stem(kit), "part", collision="hull", budget=400,
                       notes="Branch Stem (base): open Y-fork trunk with flat cut ends, plus a straight "
                             "cut stem with a short side branch."))
    out.append(kit.tag(berries(kit), "part", collision="none", budget=300,
                       notes="Optional Berries: five red berries on a tiny stem, to stick on clumps."))
    out.append(kit.tag(flower_part(kit), "part", collision="none", budget=200,
                       notes="Flower (optional): white five-petal flower, yellow centre, leaf under it."))
    dome = dome_bush(kit)
    harvest(kit, dome, (0.0, -0.9, 2.0))
    out.append(kit.tag(dome, "variant", collision="hull", budget=3500,
                       notes="A. Dome Bush: closed broad round dome ~6.3 x 6 x 4.3, ~6 flowers, no trunk."
                             + HIT_NOTE))
    hedge = hedge_bush(kit)
    harvest(kit, hedge, (0.0, -0.4, 2.0))
    out.append(kit.tag(hedge, "variant", collision="hull", budget=3500,
                       notes="B. Hedge Bush: hedge segment ~9 x 3.5 x 3.7 along X, flat top row, 4 flowers."
                             + HIT_NOTE))
    woody = open_woody(kit)
    harvest(kit, woody, (0.0, -0.5, 3.7))
    out.append(kit.tag(woody, "variant", collision="hull", budget=3500,
                       notes="C. Open Woody: thick trunk, 4 bare forking branches, clumps only at the tips."
                             + HIT_NOTE))
    return out
