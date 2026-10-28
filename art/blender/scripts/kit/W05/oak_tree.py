"""W05 row 1: OakTree, a medium broadleaf oak with a five-clump crown.

Assets
  OakTree            hero: thick twisting trunk (spiral bark ridges, knot hole on the
                     front right), 6 splayed angular roots, a fork at ~10 studs into 5
                     kinked branches, each ending in a leaf clump; the clumps sit as a
                     rosette (back, left, right, front-left, front-right) with an open
                     centre; moss ground patch, grey rocks and grass tufts (~20 x 20 x 22)
  OakLeafClump       part: one canopy clump on a short branch stub (~6 x 6 x 5.5)
  OakBranchModule    part: Y-forked branch, flat cut attach end, two upturned tips (~7 long)
  OakTrunkCore       part: the twisting trunk with a torn, splintered top and the knot hole
  OakRootBase        part: splayed root flare round a cut socket stump (~10 x 10 x 3)
  OakTreeRoundCrown  variant: stocky shorter trunk, six clumps packed into one round dome
  OakTreeWideCrown   variant: flat, wide crown on near-horizontal branches, broad roots
  OakTreeAsymmetric  variant: trunk curves to +X, the crown mass sits on +X, one small
                     clump on -X

Technique
- Trunks, branches and roots are swept tubes. Trunk rings follow a ridge pattern
  (four vertices per ridge: two shoulders round a crest, then a deep groove vertex;
  six ridges, each with its own constant height), and each ring is turned a little
  more than the one below it, so the bark planes spiral ~85 degrees up the trunk
  and the V grooves between them are real geometry (groove vertex at 0.55 of the
  crest radius, ~0.8 stud below the shoulders). The hero trunk is short and stout:
  ~6 across at chest height, ~7 at the flare, forking at ~9. Its top closes into a
  narrow cone the five limbs grow out of.
- Six separate root arms (tall pentagonal wedges, ~3.9 high at the trunk) continue
  the six bark ridges at the foot and dive into the moss patch, with deep valleys
  between them and moss on their low top faces.
- Limbs are straight segments with hard bends. Hero limbs (elbow=True): a
  near-level run out of the fork, a hard elbow into a steep rise, then a lean
  outward into the clump; the variants keep the three-segment limb.
- The hero crown is exactly five puffy clumps (~8 across, ~7 tall): the back lobe
  sits high and pulled in towards the centre (ring 3.0, z 17), the front pair at mid
  height (ring 6.2, z 15) and the left/right pair lowest at the extremes (ring 6.9,
  z 12.3). Neighbours touch, so the crown is one broad dome over the upper ~55% of
  the tree, and the front view reads top-centre / two mid / two low.
- Rev 6: every leaf clump is one Asset.canopy mass (facets 1, 7-10 star-lobed
  clusters, height 2.7 x H), and the five hero masses sit apart so the limbs show
  in the gaps between them (the numbers in the crown comment above are from rev 5).
- ONE colour per material: every leaf face is w05_leaf, every bark face w05_bark,
  moss w05_moss, grass w05_grass, rocks kit_rock, cut wood w05_heartwood, the knot
  void w05_hollow. Faces only get a small random Tint (about +/-6%); the light tops
  and dark undersides of the reference come from the lighting on the facets.
- Grass-tuft faces carry the face attribute kit_nocollide = 1 (walk-through scatter).
- No VFX: the reference shows no fire, glow or harvest effect for the oak.
"""

import math
import random

import bmesh
from mathutils import Matrix, Vector

SUBJECT = "OakTree"
ROW = 1
# Sheet palette shared by every W05 module (copied verbatim from the sheet plan;
# kit_rock is the existing KIT_PALETTE key and is not redeclared).
PALETTE = {
    "w05_leaf": ("#9CBB1C", 0.8, 0, 0),
    "w05_moss": ("#C6CB1F", 0.9, 0, 0),
    "w05_grass": ("#86AC22", 0.95, 0, 0),
    "w05_bark": ("#A5653A", 0.9, 0, 0),
    "w05_heartwood": ("#F0B26E", 0.85, 0, 0),
    "w05_hollow": ("#1C130F", 0.95, 0, 0),
    # Oak foliage: the sheet's w05_leaf renders pale lime against the reference's deeper
    # saturated yellow-green, so the oak (all its assets) uses this one leaf key instead,
    # as the verifier asked (#7FA414). w05_leaf stays declared verbatim for the sheet.
    "w05_oak_leaf": ("#7FA414", 0.8, 0, 0),
}
LEAF_KEY = "w05_oak_leaf"

CAT = "Kit W05 OakTree"
TAU = 2 * math.pi
Z = Vector((0, 0, 1))

BARK, ROOT, LEAF, ROCK = 1, 3, 4, 5
TRUNK_PATTERN = (0.86, 1.0, 0.86, 0.55)  # a ridge of two planes meeting in a crest, then a deep V groove
TWIST = math.radians(85)  # bark planes turn ~75-85 degrees from the root flare to the fork
TINT_VAR = 0.06  # small random per-face Tint, never by face direction


def polar(r, az, z=0.0):
    return Vector((r * math.cos(az), r * math.sin(az), z))


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


class Oak:
    def __init__(self, kit, name, seed):
        self.a = kit.flintkit.Asset(name, CAT, seed=seed, tint_var=0.03)
        lay = self.a.bm.faces.layers.int
        self.fam = lay.new("oak_fam")
        self.blob = lay.new("oak_blob")
        self.nocol = lay.new("kit_nocollide")
        self.rng = random.Random(seed)
        self.blobs = []  # (centre, radius, clump index)
        self.clumps = []  # (centre, R, H)
        self.dress = False

    @property
    def bm(self):
        return self.a.bm

    def tint(self):
        return 1.0 + self.rng.uniform(-TINT_VAR, TINT_VAR)

    def mark(self, faces, fam=0, blob=-1):
        for f in faces:
            f[self.fam] = fam
            f[self.blob] = blob
            f[self.nocol] = 1 if self.dress else 0
        return faces

    def put(self, f, mat, tint=None):
        f.material_index = self.a._mi(mat)
        f.smooth = False
        t = self.tint() if tint is None else tint
        for lp in f.loops:
            lp[self.a.tint_layer] = (t, t, t, 1.0)
        f[self.nocol] = 1 if self.dress else 0
        return f

    def paint(self, faces, mat):
        """One key for the whole piece, a small random Tint per face."""
        for f in faces:
            self.put(f, mat)
        return faces


def orient(f, out):
    f.normal_update()
    if f.normal.dot(out) < 0:
        f.normal_flip()
    return f


def frames(pts):
    n = len(pts)
    tans = [(pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized() for i in range(n)]
    up = Z if abs(tans[0].z) < 0.9 else Vector((1, 0, 0))
    nrm = tans[0].cross(up).normalized()
    out = []
    for i in range(n):
        if i:
            axis = tans[i - 1].cross(tans[i])
            if axis.length > 1e-6:
                nrm = Matrix.Rotation(tans[i - 1].angle(tans[i]), 3, axis.normalized()) @ nrm
            nrm = (nrm - tans[i] * nrm.dot(tans[i])).normalized()
        out.append((tans[i], nrm, tans[i].cross(nrm)))
    return out


def sweep(o, pts, radii, sides=8, twist=0.0, pattern=(1.0,), squash=1.0, roll=0.0,
          caps=(False, True), fam=BARK, jitter=0.04, cap_mat=None, mat="w05_bark", ridge=None):
    """Faceted tube along a polyline, all one material (`mat`). Returns
    (rings, side faces, cap faces). A ridge `pattern` pulls every third vertex in,
    so the bark planes meet in real V grooves; `ridge` gives each ridge its own
    constant height, so a plane stays one long continuous strip up the trunk."""
    bm = o.bm
    pts = [Vector(p) for p in pts]
    n = len(pts)
    rings = []
    for i, (t, nrm, bi) in enumerate(frames(pts)):
        ring = []
        for j in range(sides):
            th = roll + TAU * j / sides + twist * i / max(n - 1, 1)
            r = radii[i] * pattern[j % len(pattern)] * (1 + o.rng.uniform(-jitter, jitter))
            if ridge:
                r *= ridge[(j // len(pattern)) % len(ridge)]
            ring.append(bm.verts.new(pts[i] + r * (math.cos(th) * nrm + squash * math.sin(th) * bi)))
        rings.append(ring)
    side = []
    for i in range(n - 1):
        mid = (pts[i] + pts[i + 1]) / 2
        for j in range(sides):
            k = (j + 1) % sides
            f = bm.faces.new((rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]))
            orient(f, f.calc_center_median() - mid)
            o.put(f, mat)
            o.mark([f], fam)
            side.append(f)
    capf = []
    for end, ring, d in ((0, rings[0], -(pts[1] - pts[0])), (1, rings[-1], pts[-1] - pts[-2])):
        if caps[end]:
            f = orient(bm.faces.new(ring), d)
            o.put(f, cap_mat or mat)
            o.mark([f], 0 if cap_mat else fam)
            capf.append(f)
    return rings, side, capf


# ---------------------------------------------------------------------------
# Tree pieces
# ---------------------------------------------------------------------------


RIDGES = (1.0, 0.88, 1.08, 0.92, 1.04, 0.86)  # six bark ridges, each its own height
ROOT_AZ = (-90, -30, 30, 90, 150, -150)  # roots continue the ridges at the foot


def trunk(o, path, radii, twist=TWIST, sides=24, top_cap=True, ridge_az=-90.0):
    """Six long bark ridges with V grooves between them, turned `twist` over the
    height. Each ridge is two planes meeting in a crest, so it catches the light on
    one side and shades on the other. The crest of ridge 0 sits on world azimuth
    `ridge_az` at the foot (the sweep's angle 0 points +Y for an upright path), so
    the roots grow out of the ridges."""
    roll = math.radians(ridge_az - 90.0) - TAU * 1.0 / sides
    return sweep(o, path, radii, sides=sides, twist=twist, pattern=TRUNK_PATTERN,
                 caps=(False, top_cap), fam=BARK, jitter=0.012, roll=roll, ridge=RIDGES)


def branch(o, start, end, r0, r1, kink=0.16, sides=6, fam=BARK, caps=(False, True), mid_lift=0.0,
           cap_mat=None):
    """Angular limb: three straight segments with sharp bends."""
    start, end = Vector(start), Vector(end)
    d = end - start
    L = d.length
    side = d.cross(Z)
    side = side.normalized() if side.length > 1e-4 else Vector((1, 0, 0))
    s = 1 if o.rng.random() < 0.5 else -1
    p1 = start + d * 0.36 + side * L * kink * s + Z * mid_lift
    p2 = start + d * 0.7 - side * L * kink * 0.7 * s + Z * mid_lift * 0.6
    pts = [start, p1, p2, end]
    radii = [r0, r0 + (r1 - r0) * 0.35, r0 + (r1 - r0) * 0.7, r1]
    return sweep(o, pts, radii, sides=sides, twist=o.rng.uniform(-0.4, 0.4), caps=caps, fam=fam,
                 jitter=0.06, cap_mat=cap_mat)


def roots(o, azs=ROOT_AZ, foot=2.6, reach=(6.2, 7.0), h0=3.2, base=(0.0, 0.0), r0=1.15,
          moss=True, squash=1.45):
    """Six separate splayed root arms: tall faceted wedges that leave the trunk
    flare at ~h0, run out with a sharp elbow and dive into the ground ~reach out,
    leaving moss-floored valleys between them."""
    base = Vector((base[0], base[1], 0))
    for k, azd in enumerate(azs):
        az = math.radians(azd) + o.rng.uniform(-0.06, 0.06)
        rk = o.rng.uniform(*reach)
        k1, k2 = o.rng.uniform(-0.1, 0.1), o.rng.uniform(-0.14, 0.14)
        pts = [base + polar(foot * 0.45, az, h0),
               base + polar(foot * 1.15, az + k1, h0 * 0.62),
               base + polar(foot + (rk - foot) * 0.5, az + k2, h0 * 0.3),
               base + polar(rk, az + k2 * 0.4, -0.35)]
        radii = [r0, r0 * 0.95, r0 * 0.68, r0 * 0.3]
        _, side, _ = sweep(o, pts, radii, sides=5, roll=-math.pi / 2, squash=squash,
                           caps=(False, True), fam=ROOT, jitter=0.05)
        if not moss:
            continue
        # moss grows on the root crowns near the ground (a different material, w05_moss)
        for f in side:
            f.normal_update()
            if f.normal.z > 0.4 and f.calc_center_median().z < 2.0 and o.rng.random() < 0.3:
                o.put(f, "w05_moss")


def blob(o, c, r, cid, subdiv=1, squash=0.9):
    verts = o.a.ico((r, r, r * squash), c, rot=(o.rng.uniform(0, TAU), o.rng.uniform(0, TAU),
                                                o.rng.uniform(0, TAU)),
                    mat=LEAF_KEY, subdiv=subdiv, jitter=0.1 if subdiv > 1 else 0.09,
                    tint=1.0 + o.rng.uniform(-0.03, 0.03), face_tint_var=0.03)
    o.mark(_faces(verts), LEAF, len(o.blobs))
    o.blobs.append((Vector(c), r, cid))


def _faces(verts):
    fs = set()
    for v in verts:
        fs.update(v.link_faces)
    return list(fs)


def clump(o, c, R=2.9, H=2.5, outer=8, core=True, scale=1.0):
    """One canopy clump: two big core blobs under a puffy shell of smaller lumps
    of mixed sizes, more of them towards the top (cauliflower shape), so the
    outline is notched like the reference. All one leaf colour. The clump spans
    about 2.5 R across."""
    # Rev 6: built with the shared Asset.canopy helper (dense star-lobed cauliflower
    # clusters). R is the half-width, H the half-height of the mass; `outer` is the
    # number of leaf clusters in it.
    c = Vector(c)
    o.clumps.append((c, R, H))
    verts = o.a.canopy(c, (2 * R * scale, 2 * R * scale, 2.7 * H * scale), mat=LEAF_KEY,
                       clumps=outer, facets=1, core=core, inner=False, tilt=0.5, bulge=0.5, flat_bottom=1.0,
                       seed=o.rng.randint(0, 99999))
    fs = _faces(verts)
    o.mark(fs, LEAF, -1)
    return c


def knot(o, centre, outward, r=0.6):
    """Knot hole: a raised bark lip round a near-black void, set into the trunk."""
    d = Vector(outward).normalized()
    rot = d.to_track_quat("Z", "Y").to_euler()
    centre = Vector(centre)
    rim = o.a.torus(r, r * 0.34, loc=centre, rot=rot, seg=8, rseg=4, mat="w05_bark", squash=0.9)
    disc = o.a.cyl(r * 0.95, r * 0.95, 0.06, sides=8, loc=centre - d * 0.08, rot=rot, mat="w05_hollow",
                   tint=1.0)
    for v in rim + disc:
        v.co.z = centre.z + (v.co.z - centre.z) * 1.4
    o.paint(_faces(rim), "w05_bark")
    o.mark(_faces(rim + disc), 0)


def ground(o, R=6.6, n=16, th=0.3, c=(0.0, 0.0), sx=1.0, sy=1.0):
    """Irregular moss patch (one moss colour), no bottom face."""
    bm = o.bm
    c = Vector((c[0], c[1], 0))
    top, bot = [], []
    for k in range(n):
        az = TAU * k / n + o.rng.uniform(-0.12, 0.12)
        r = R * (1 + o.rng.uniform(-0.14, 0.08)) * (1.06 if k % 3 == 0 else 1.0)
        p = c + Vector((r * math.cos(az) * sx, r * math.sin(az) * sy, 0))
        bot.append(bm.verts.new(p))
        top.append(bm.verts.new(p + Vector((0, 0, th * o.rng.uniform(0.85, 1.0)))))
    mid = bm.verts.new(c + Vector((0, 0, th + 0.02)))
    for k in range(n):
        k2 = (k + 1) % n
        f = orient(bm.faces.new((mid, top[k], top[k2])), Z)
        o.put(f, "w05_grass")
        o.mark([f])
        out = (top[k].co + top[k2].co) / 2 - c
        out.z = 0
        f = orient(bm.faces.new((bot[k], bot[k2], top[k2], top[k])), out)
        o.put(f, "w05_grass")
        o.mark([f])


def rock(o, size, loc, sub=1):
    verts = o.a.rock(size, loc, rot=(0, 0, o.rng.uniform(0, TAU)), mat="kit_rock", subdiv=sub,
                     rough=0.14, facets=12, sink=0.2)
    o.paint(_faces(verts), "kit_rock")
    o.mark(_faces(verts), ROCK)


def tuft(o, p, size=1.2):
    """Spiky grass tuft: 5-7 three-sided blades, one grass colour."""
    a = o.a
    o.dress = True
    nb = o.rng.randint(6, 8)
    ph = o.rng.uniform(0, TAU)
    for b in range(nb):
        az = ph + TAU * b / nb + o.rng.uniform(-0.3, 0.3)
        lean = o.rng.uniform(0.15, 0.55) if b else 0.05
        h = size * o.rng.uniform(0.7, 1.0) * (1.0 if b else 1.15)
        d = Vector((math.sin(lean) * math.cos(az), math.sin(lean) * math.sin(az), math.cos(lean)))
        rot = d.to_track_quat("Z", "Y").to_euler()
        base = Vector(p) + polar(0.12 * size, az, 0.15)
        w = 0.2 * size
        v1 = a.cyl(w, w * 0.5, h * 0.6, sides=3, loc=base, rot=rot, mat="w05_grass", cap=False)
        v2 = a.cyl(w * 0.5, 0.0, h * 0.4, sides=3, loc=base + d * h * 0.6, rot=rot, mat="w05_grass",
                   cap=False)
        o.paint(_faces(v1 + v2), "w05_grass")
        o.mark(_faces(v1 + v2), 0)
    o.dress = False


def dressing(o, rocks_spec, tufts_spec, patch=6.6, sx=1.0, sy=1.0):
    ground(o, R=patch, sx=sx, sy=sy)
    for az, r, s in rocks_spec:
        a = math.radians(az)
        size = (s * o.rng.uniform(1.0, 1.25), s * o.rng.uniform(0.85, 1.1), s * o.rng.uniform(0.75, 0.95))
        rock(o, tuple(v * 1.25 for v in size), polar(r, a, 0.15), sub=2 if s > 1.2 else 1)
    for az, r, s in tufts_spec:
        tuft(o, polar(r, math.radians(az), 0.0), s * 1.45)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def cull_hidden(o):
    """Delete leaf faces whose centre is buried inside another blob."""
    bm = o.bm
    dead = []
    for f in bm.faces:
        if f[o.fam] != LEAF:
            continue
        p = f.calc_center_median()
        me = f[o.blob]
        for i, (c, r, _) in enumerate(o.blobs):
            if i != me and (p - c).length < r * 0.86:
                dead.append(f)
                break
    if dead:
        bmesh.ops.delete(bm, geom=dead, context="FACES")
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")


def finish(o):
    cull_hidden(o)
    a = o.a
    used = sorted({f.material_index for f in a.bm.faces})
    remap = {old: new for new, old in enumerate(used)}
    for f in a.bm.faces:
        f.material_index = remap[f.material_index]
    a.mats = [a.mats[i] for i in used]
    for lay in (o.fam, o.blob):
        a.bm.faces.layers.int.remove(lay)
    for v in a.bm.verts:
        if v.co.z < 0.0:
            v.co.z = 0.0
    return a.finish()


# ---------------------------------------------------------------------------
# Trees
# ---------------------------------------------------------------------------


def limb(o, start, end, r0, r1, kink=0.17, sides=6, lift=(0.12, 0.55), elbow=False):
    """Angular main limb: a near-level run out of the fork, a sharp elbow, a steeper
    rise, then a last bend up into the clump. Straight segments, hard bends."""
    start, end = Vector(start), Vector(end)
    d = end - start
    h = Vector((d.x, d.y, 0))
    side = h.cross(Z)
    side = side.normalized() if side.length > 1e-4 else Vector((1, 0, 0))
    s = 1 if o.rng.random() < 0.5 else -1
    L = d.length
    if elbow:
        # gnarled oak limb: a near-level run out of the fork, a hard elbow into a steep
        # rise, then a lean outward into the clump (four straight segments)
        p1 = start + h * 0.42 + Z * min(0.5, d.z * 0.08) + side * L * kink * s
        p2 = start + h * 0.56 + Z * d.z * 0.62 + side * L * kink * 0.4 * s
        p3 = start + h * 0.82 + Z * d.z * 0.84 - side * L * kink * 0.45 * s
        pts = [start, p1, p2, p3, end]
        radii = [r0, r0 + (r1 - r0) * 0.3, r0 + (r1 - r0) * 0.55, r0 + (r1 - r0) * 0.8, r1]
        return sweep(o, pts, radii, sides=sides, twist=o.rng.uniform(-0.3, 0.3), caps=(False, True),
                     fam=BARK, jitter=0.05)
    p1 = start + h * 0.4 + Z * d.z * lift[0] + side * L * kink * s
    p2 = start + h * 0.78 + Z * d.z * lift[1] - side * L * kink * 0.5 * s
    pts = [start, p1, p2, end]
    radii = [r0, r0 + (r1 - r0) * 0.4, r0 + (r1 - r0) * 0.75, r1]
    return sweep(o, pts, radii, sides=sides, twist=o.rng.uniform(-0.3, 0.3), caps=(False, True),
                 fam=BARK, jitter=0.05)


def tree(o, path, radii, crown, split, root_kw, dress_kw, twist=TWIST, knot_at=None, twigs=True,
         br=(1.0, 0.5), lift=(0.12, 0.55), elbow=False, kink=0.17, cone_h=0.9, cone_r=0.22,
         limb_drop=1.5):
    """Trunk along `path`, an angular limb from the fork to every clump, roots and
    dressing. crown: list of (centre, R, H, outer blobs). Each limb ends inside the
    lower inner side of its clump, so the limbs show in the gaps between clumps and
    as a star in the open centre seen from above."""
    # close the trunk top into a blunt cone the limbs grow out of (no flat top disc)
    cone = Vector(path[-1]) + Vector((0, 0, cone_h))
    trunk(o, list(path) + [cone], list(radii) + [radii[-1] * cone_r], twist=twist)
    top = Vector(path[-1])
    for c, R, H, outer in crown:
        c = Vector(c)
        hd = Vector((c.x - top.x, c.y - top.y, 0))
        hd = hd.normalized() if hd.length > 1e-3 else Vector((0, 0, 0))
        end = c - hd * R * 0.3 - Vector((0, 0, H * 0.45))
        start = Vector((top.x, top.y, split - limb_drop)) + hd * 0.6
        limb(o, start, end, br[0], br[1], lift=lift, sides=7, elbow=elbow, kink=kink)
        if twigs and (end - start).length > 4.5:
            mid = start + (end - start) * 0.6 + Vector((0, 0, 0.6))
            side = (end - start).cross(Z)
            side = side.normalized() if side.length > 1e-3 else Vector((1, 0, 0))
            tw = c + side * R * 0.55 * (1 if o.rng.random() < 0.5 else -1) - Vector((0, 0, H * 0.25))
            branch(o, mid, tw, 0.36, 0.2, kink=0.1, sides=5)
        clump(o, c, R, H, outer)
    roots(o, **root_kw)
    if knot_at:
        z, az = knot_at
        # trunk centre and radius at height z (path/radii are piecewise linear)
        pts = [Vector(p) for p in path]
        for i in range(len(pts) - 1):
            if pts[i].z <= z <= pts[i + 1].z:
                t = (z - pts[i].z) / (pts[i + 1].z - pts[i].z)
                cen = pts[i].lerp(pts[i + 1], t)
                r = radii[i] + (radii[i + 1] - radii[i]) * t
                break
        d = polar(1.0, math.radians(az))
        knot(o, cen + d * (r * 0.95 + 0.04), d, r=0.75)
    dressing(o, **dress_kw)
    return finish(o)


def ring_crown(specs):
    """specs: (azimuth deg, radius, z, R, H, outer blobs)."""
    return [(polar(r, math.radians(az), z), R, H, n) for az, r, z, R, H, n in specs]


HERO_PATH = [(0, 0, 0), (0, 0, 1.3), (0.5, -0.15, 2.8), (0.8, 0.0, 4.4), (0.4, 0.2, 6.0),
             (-0.3, 0.15, 7.6), (0, 0.0, 9.2)]
HERO_TWIST = math.radians(125)
# ~7 across at the flare, ~6 at chest height; a short stout trunk whose top closes into
# a narrow cone that the five limbs grow out of, so only a small branch star shows in
# the open centre of the crown
# Rev 7: flared foot, a waist at ~5, then the trunk swells again into the fork
HERO_RADII = [3.7, 3.15, 2.75, 2.45, 2.4, 2.55, 2.4]
HERO_CROWN = [
    # five tall, puffy lobes that touch into one broad dome round a small open centre.
    # Front view (1+2+2): the back lobe is the top-centre clump, the front pair sit at
    # mid height either side of the fork, the left and right lobes hang lowest at the
    # extremes. The crown spans z ~9.5-22, the upper ~55% of the tree. The back lobe is
    # pulled in (ring 3.0) so it also crowns the side view instead of leaving a notch
    # between it and the front pair. The rosette is turned ~-8 degrees.
    # Rev 6: five SEPARATE canopy masses with gaps between them that show the limbs
    # (az, ring, z, half-width, half-height, clusters)
    # Rev 7: much bigger, denser masses that overlap their neighbours a little; the crown
    # spans z ~9-22 (about half the tree) and ~25 across
    # deep in Y too (back mass pushed back, front pair forward) so the side view is broad
    (92, 3.8, 18.4, 5.6, 3.6, 8),      # top (back centre, highest, largest)
    (166, 7.5, 15.4, 4.9, 3.3, 8),     # left (mid)
    (14, 7.5, 15.7, 4.9, 3.3, 8),      # right (mid)
    (-122, 7.2, 12.4, 4.6, 3.1, 7),    # front-left (low)
    (-58, 7.2, 12.8, 4.6, 3.1, 7),     # front-right (low)
]
# rocks and tufts sit in the valleys between the six roots (ROOT_AZ)
HERO_ROCKS = [(0, 6.0, 2.3), (-60, 6.5, 1.6), (-120, 5.9, 1.9), (60, 6.1, 1.7), (180, 6.0, 2.0),
              (-103, 7.4, 1.3), (122, 6.4, 1.5)]
HERO_TUFTS = [(-135, 5.2, 1.9), (-45, 5.2, 1.8), (-75, 7.0, 1.4), (15, 7.1, 1.5), (75, 5.4, 1.7),
              (135, 5.7, 1.7), (-165, 7.0, 1.4), (-112, 4.8, 1.3)]
HERO_ROOTS = dict(foot=2.9, reach=(6.6, 7.4), h0=3.9, r0=1.4)


def build_hero(kit):
    o = Oak(kit, "OakTree", 501)
    return tree(o, HERO_PATH, HERO_RADII, ring_crown(HERO_CROWN), 9.0, HERO_ROOTS,
                dict(rocks_spec=HERO_ROCKS, tufts_spec=HERO_TUFTS, patch=7.7),
                knot_at=(5.0, -70), elbow=True, kink=0.2, cone_h=1.2, cone_r=0.4, limb_drop=1.0,
                br=(1.35, 0.75), twist=HERO_TWIST)


def build_round(kit):
    o = Oak(kit, "OakTreeRoundCrown", 511)
    path = [(0, 0, 0), (0, 0, 1.4), (0.1, 0, 3.2), (0.2, 0.05, 5.2), (0.05, 0.1, 7.2), (0, 0.1, 8.8)]
    radii = [3.4, 2.95, 2.7, 2.55, 2.45, 2.15]
    # six clumps packed into one round dome: a ring of five, alternately high and low,
    # and a crowning clump on top
    # Rev 7: a bigger round dome (~19 across) so the crown dominates the stocky trunk
    crown = ring_crown([(90, 5.0, 13.6, 4.3, 3.1, 7), (162, 5.0, 12.0, 4.3, 3.1, 7),
                        (18, 5.0, 12.2, 4.3, 3.1, 7), (-126, 5.0, 13.0, 4.3, 3.1, 7),
                        (-54, 5.0, 12.6, 4.3, 3.1, 7)])
    crown.append((Vector((0.2, 0.3, 16.6)), 4.0, 3.0, 8))  # crown top
    return tree(o, path, radii, crown, 8.8, dict(foot=2.5, reach=(5.6, 6.2), h0=3.0, r0=1.05),
                dict(rocks_spec=[(0, 5.4, 1.9), (60, 5.8, 1.2), (-120, 5.4, 1.6), (-60, 5.9, 0.9),
                                 (120, 5.3, 1.1)],
                     tufts_spec=[(-150, 4.7, 1.6), (-45, 4.6, 1.5), (-100, 6.0, 1.3), (15, 6.0, 1.4),
                                 (135, 4.9, 1.5), (-165, 6.1, 1.2)], patch=6.8),
                knot_at=(5.0, -55), twigs=False, br=(1.0, 0.5))


def build_wide(kit):
    o = Oak(kit, "OakTreeWideCrown", 521)
    path = [(0, 0, 0), (0, 0, 1.4), (0.1, 0, 3.2), (0.2, 0.05, 5.2), (0.05, 0.1, 7.2), (0, 0.1, 9.2)]
    radii = [3.7, 3.1, 2.75, 2.55, 2.45, 2.2]
    # a flat, wide crown: five clumps spread on near-horizontal limbs plus a low top clump
    crown = [(Vector((-7.2, 0.6, 12.0)), 3.5, 2.6, 7), (Vector((7.3, 0.3, 11.8)), 3.5, 2.6, 7),
             (Vector((-3.9, -5.0, 12.8)), 3.4, 2.6, 7), (Vector((4.1, -4.8, 12.6)), 3.4, 2.6, 7),
             (Vector((0.2, 5.6, 13.4)), 3.4, 2.6, 7), (Vector((0.3, 0.6, 15.4)), 3.3, 2.6, 7)]
    return tree(o, path, radii, crown, 9.2,
                dict(azs=(-90, -38, 14, 66, 118, 170, -142), foot=2.7, reach=(7.0, 8.0), h0=3.2,
                     r0=1.25),
                dict(rocks_spec=[(-12, 6.8, 2.2), (40, 7.4, 1.4), (-115, 6.8, 1.7), (-64, 7.6, 1.0),
                                 (145, 7.0, 1.2), (92, 7.0, 1.0)],
                     tufts_spec=[(-165, 6.0, 1.8), (-128, 7.6, 1.5), (-50, 6.0, 1.7), (-10, 8.0, 1.5),
                                 (40, 5.8, 1.4), (92, 5.8, 1.6), (175, 7.6, 1.3), (-76, 7.8, 1.2)],
                     patch=8.6, sx=1.05, sy=0.95),
                knot_at=(5.0, -55), lift=(0.04, 0.3))


def build_asym(kit):
    o = Oak(kit, "OakTreeAsymmetric", 531)
    path = [(0, 0, 0), (0.05, 0, 1.5), (0.3, 0, 3.5), (0.9, 0.05, 5.5), (1.7, 0.1, 7.3),
            (2.5, 0.1, 9.0), (3.1, 0.15, 10.4)]
    radii = [3.5, 3.0, 2.7, 2.55, 2.45, 2.35, 2.1]
    # a big trio of clumps on +X and one small clump out on -X
    crown = [(Vector((8.2, 0.4, 13.0)), 3.6, 3.0, 8), (Vector((4.6, 3.4, 17.6)), 3.7, 3.1, 8),
             (Vector((5.0, -3.8, 15.2)), 3.5, 3.0, 8), (Vector((-4.6, 0.2, 11.8)), 2.4, 2.1, 6)]
    return tree(o, path, radii, crown, 10.4, dict(HERO_ROOTS, moss=False),
                dict(rocks_spec=HERO_ROCKS[:6], tufts_spec=HERO_TUFTS[:7], patch=7.4),
                knot_at=(5.0, -50))


# -- parts ---------------------------------------------------------------------


def build_leaf_clump(kit):
    o = Oak(kit, "OakLeafClump", 541)
    # a visible stub below the clump, its foot a flat heartwood attach face
    branch(o, (0.15, 0, 0), (0, 0.1, 3.0), 0.5, 0.36, kink=0.1, sides=6, caps=(True, False),
           cap_mat="w05_heartwood")
    clump(o, (0, 0, 3.7), 2.8, 2.3, 10)
    return finish(o)


def build_branch(kit):
    o = Oak(kit, "OakBranchModule", 542)
    root = Vector((-3.6, 0, 0.7))
    fork = Vector((0.4, 0.1, 1.2))
    sweep(o, [root, Vector((-2.0, -0.1, 0.6)), Vector((-0.8, 0.15, 1.05)), fork],
          [0.62, 0.58, 0.52, 0.46], sides=8, pattern=(1.0, 0.82), caps=(True, False),
          cap_mat="w05_heartwood", jitter=0.05)
    # Rev 7: a second fork off the upper tip
    branch(o, Vector((1.9, 1.3, 2.0)), Vector((1.6, 3.4, 4.3)), 0.26, 0.14, kink=0.08, sides=5)
    # the Y: one tip forks up and back, the other out to the front; both turn upward
    branch(o, fork - Vector((0.3, 0, 0.05)), Vector((3.3, 2.5, 3.0)), 0.42, 0.22, kink=0.08,
           sides=6, mid_lift=0.3)
    branch(o, fork - Vector((0.3, 0, 0.05)), Vector((2.6, -2.5, 3.4)), 0.38, 0.2, kink=0.08,
           sides=6, mid_lift=0.3)
    # the short straight stick: a snapped side twig with a pale cut end
    sweep(o, [Vector((-1.6, -0.1, 0.7)), Vector((-1.2, -1.6, 0.9))], [0.26, 0.2], sides=5,
          caps=(False, True), cap_mat="w05_heartwood", jitter=0.04)
    return finish(o)


def build_trunk_core(kit):
    o = Oak(kit, "OakTrunkCore", 543)
    # Rev 7: wider column (~8 across at the flared foot, ~11.5 tall), twisting
    path = [(0, 0, 0), (0, 0, 1.0), (0.2, -0.05, 2.6), (0.35, 0.05, 4.6), (0.15, 0.15, 6.8),
            (-0.1, 0.1, 9.0), (0, 0.1, 10.4)]
    radii = [4.0, 3.3, 2.9, 2.7, 2.6, 2.55, 2.5]  # flared foot that sits on OakRootBase
    rings, side, _ = trunk(o, path, radii, top_cap=False, twist=math.radians(100))
    top = rings[-1]
    c = Vector(path[-1])
    n = len(top)
    # torn top: a ragged rim of short bark teeth, inside it a pale heartwood crown of
    # tall broken splinters standing above the rim
    for j, v in enumerate(top):
        v.co.z += o.rng.uniform(0.2, 0.8) if j % 2 else o.rng.uniform(-0.1, 0.2)
    inner = []
    for j, v in enumerate(top):
        p = c + (v.co - c) * 0.62
        p.z = c.z + (o.rng.uniform(0.9, 1.9) if j % 3 != 1 else o.rng.uniform(0.1, 0.5))
        inner.append(o.bm.verts.new(p))
    mid = o.bm.verts.new(c + Vector((0, 0, 0.5)))
    for j in range(n):
        k = (j + 1) % n
        f = orient(o.bm.faces.new((top[j], top[k], inner[k], inner[j])), Z)
        o.put(f, "w05_heartwood")
        o.mark([f])
        f = orient(o.bm.faces.new((mid, inner[j], inner[k])), Z)
        o.put(f, "w05_heartwood")
        o.mark([f])
    d = polar(1.0, math.radians(-55))
    knot(o, Vector((0.35, 0.05, 4.6)) + d * (2.7 * 0.97 + 0.04), d, r=0.6)
    obj = finish(o)
    obj["kit_shading_ok"] = "the torn top is pale heartwood splinters (cut wood), a material change, not light"
    return obj


def build_root_base(kit):
    o = Oak(kit, "OakRootBase", 544)
    path = [(0, 0, 0), (0, 0, 2.2), (0, 0, 4.8)]  # Rev 7: taller stump (~5 studs)
    rings, _, _ = trunk(o, path, [3.3, 2.85, 2.6], twist=0.6, top_cap=False)
    top = rings[-1]
    c = Vector(path[-1])
    n = len(top)
    # cut top: concentric heartwood bands with thin w05_bark growth-ring lines, the
    # centre slightly sunk to take the trunk (socket)
    bands = [(1.0, 0.0, "w05_heartwood"), (0.86, -0.02, "w05_bark"), (0.79, -0.04, "w05_heartwood"),
             (0.5, -0.1, "w05_bark"), (0.44, -0.12, "w05_heartwood")]
    prev = top
    for i, (s, dz, _mat) in enumerate(bands[1:]):
        cur = [o.bm.verts.new(c + (v.co - c) * s + Vector((0, 0, dz))) for v in top]
        mat = bands[i][2]
        for j in range(n):
            k = (j + 1) % n
            f = orient(o.bm.faces.new((prev[j], prev[k], cur[k], cur[j])), Z)
            o.put(f, mat)
            o.mark([f])
        prev = cur
    mid = o.bm.verts.new(c + Vector((0, 0, -0.16)))
    for j in range(n):
        f = orient(o.bm.faces.new((mid, prev[j], prev[(j + 1) % n])), Z)
        o.put(f, bands[-1][2])
        o.mark([f])
    roots(o, foot=2.7, reach=(5.8, 6.6), h0=4.2, r0=1.45, moss=False, squash=1.6)
    obj = finish(o)
    obj["kit_shading_ok"] = "the cut stump top is heartwood with bark ring lines, a material change, not light"
    return obj


def build(kit):
    hero = kit.tag(build_hero(kit), "hero", collision="precise", budget=8000,
                   notes="trunk, branches and crown collide precisely so players walk under the "
                         "crown; grass-tuft faces carry kit_nocollide=1. No VFX.")
    variants = [
        kit.tag(build_round(kit), "variant", collision="precise", budget=8000,
                notes="Round Crown: stocky trunk, clumps packed in one dome; tufts kit_nocollide=1"),
        kit.tag(build_wide(kit), "variant", collision="precise", budget=8000,
                notes="Wide Crown: flat wide crown on near-horizontal branches; tufts kit_nocollide=1"),
        kit.tag(build_asym(kit), "variant", collision="precise", budget=8000,
                notes="Asymmetric: trunk curves to +X, crown mass on +X; tufts kit_nocollide=1"),
    ]
    parts = [
        kit.tag(build_leaf_clump(kit), "part", collision="hull", budget=1500,
                notes="one canopy clump on a short stub; the flat heartwood end snaps onto a branch tip"),
        kit.tag(build_branch(kit), "part", collision="hull", budget=1500,
                notes="Y-forked branch: the flat heartwood end (-X) attaches to the trunk top"),
        kit.tag(build_trunk_core(kit), "part", collision="hull", budget=1500,
                notes="twisting trunk with a torn top where branches attach; knot hole front-right"),
        kit.tag(build_root_base(kit), "part", collision="precise", budget=1500,
                notes="root flare round a cut socket stump; OakTrunkCore stands on the stump"),
    ]
    return [hero] + variants + parts
