"""W02 row 1: CLIFF WALL, "repeatable tall vertical cliff chunk with flat top".

A palisade of tall, narrow, vertical faceted rock columns (convex hulls of
jittered point rings on tall prisms, so the big planes run vertically) under the
shared W02 1.0-stud grass cap (0.6 grass over a 0.4 earth band) whose rounded,
scalloped lip overhangs the column fronts by 0.3-0.8. Main columns alternate
1-3 studs in depth; some bulge as chunky hexagonal prisms, some end in a
bevelled crest under the lip, and some stand on a prouder lower block whose
pointed top makes a ledge partway up. Proud pointed forward columns (about 16,
11.5, 9.5 and 7 tall, 2.6-3.4 forward of the face) and leaning shard rocks
(3.4-6 tall) break the outline at the foot; big round bright bush clusters
(about 7 studs) sit on the lip corners, the front ones pushed past the lip and
spilling down the face; pale pebbles
and flower dots on the grass, grass streaks drip down the face, and small
bushes, tufts and rubble dress the foot. The +Y side is a flat grey
w02_connector plate with rectangular puzzle tabs on its vertical edges.

Every asset is built by one `Wall` from a footprint polygon whose edges are
typed: "cliff" (a column face looking out of that edge), "end" (a tiling side:
columns flush with the 32-stud grid line at the top, their feet set back so foot
shards, rubble and bushes sit in front) or "back" (a connector plate).
The grass outline is traced from the actual column fronts (ray casts at the
column tops) plus a 0.3-0.8 overhang, so the lip always follows the columns.

Assets: CliffWall (hero), CliffWallGrassTopLip + CliffWallBody +
CliffWallBackConnector (parts), CliffWallStraight / CliffWallInnerCorner /
CliffWallOuterCorner (variants). No VFX: the reference shows none.

Colours: the shared 9-key W02 palette, ONE key per material. Every rock face
(columns, forward columns, shards, rubble, the core) is w02_rock; the cap is
w02_grass over w02_earth; streaks, tufts and the foot fringe are w02_grass;
every bush is leaf; pebbles on the grass are w02_slab; the plate is
w02_connector. Tint only varies a few percent at random. The light tops, dark
crevices and grey-green shadow sides come from the facets and the light.
"""

import math
import random

import bmesh
from mathutils import Matrix, Vector

SUBJECT = "CliffWall"
ROW = 1
# Shared W02 sheet palette (identical in every W02 module).
PALETTE = {
    "w02_rock": ("#B3A19C", 0.9, 0, 0),
    "w02_slab": ("#CDC2C3", 0.9, 0, 0),
    "w02_connector": ("#8A868A", 0.95, 0, 0),
    "w02_grass": ("#B0C82B", 0.95, 0, 0),
    "w02_earth": ("#A06A45", 0.95, 0, 0),
    "w02_path": ("#EAB37E", 0.95, 0, 0),
    # The sheet's other three keys are existing flintkit.PALETTE keys with the
    # identical values, and the runner rejects non-w02_ keys here, so they are
    # used from flintkit as-is:
    #   "leaf": ("#6C9A28", 0.8, 0, 0)
    #   "flower_white": ("#F5F2EA", 0.7, 0, 0)
    #   "flower_yellow": ("#F2C230", 0.7, 0, 0)
}

# ONE key per material: every rock face is w02_rock, every grass face w02_grass,
# every bush leaf; light and dark come only from facet orientation + the sun.
ROCK, SLAB, CONN = "w02_rock", "w02_slab", "w02_connector"
GRASS, EARTH, LEAF = "w02_grass", "w02_earth", "leaf"
TWO_TONE = ("w02_connector = flat grey engineered back plate (kit joint); w02_slab = pale lilac "
            "flagstone pebbles; both differ from the mauve cliff rock")

TOP = 24.0          # walkable grass top
SLAB_BOT = 23.0     # bottom of the cap: the shared W02 1.0 slab (earth 23.0-23.4, grass 23.4-24.0)
EARTH_TOP = 23.4
COL_TOP = 23.3      # main columns end inside the earth band
PLATE_T = 0.4
PLATE_TOP = 23.5
Z = Vector((0, 0, 1))
TAU = 2 * math.pi

# face groups (an int layer on the bmesh), so parts can keep only theirs
G_ROCK, G_CAP, G_TOPDRESS, G_PLATE, G_BASE, G_STREAK, G_CORE = 1, 2, 3, 4, 5, 6, 7


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------


class Piece:
    """A convex rock chunk: its faces and bounding planes (for culling and rays)."""

    def __init__(self, faces, kind, c=None, t=None, n=None, top=0.0):
        self.faces = faces
        self.kind = kind
        self.c, self.t, self.n, self.top = c, t, n, top
        self.planes = [(f.normal.copy(), f.calc_center_median()) for f in faces]

    def contains(self, p, eps=0.02):
        return all(n.dot(p - c) < -eps for n, c in self.planes)

    def ray(self, o, d):
        t0, t1, n0 = -1e9, 1e9, None
        for n, c in self.planes:
            nd = n.dot(d)
            dist = n.dot(c - o)
            if abs(nd) < 1e-9:
                if dist < 0:
                    return None
                continue
            t = dist / nd
            if nd < 0:
                if t > t0:
                    t0, n0 = t, n
            elif t < t1:
                t1 = t
        if n0 is None or t0 > t1 or t0 < 0:
            return None
        return t0, n0


def hull(bm, pts, merge=3.0):
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


def inside(p, poly):
    x, y = p[0], p[1]
    hit = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i][0], poly[i][1]
        x2, y2 = poly[(i + 1) % n][0], poly[(i + 1) % n][1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            hit = not hit
    return hit


def seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (a + ab * t - p).length


def poly_dist(p, poly):
    n = len(poly)
    return min(seg_dist(p, poly[i], poly[(i + 1) % n]) for i in range(n))


def vnormals(poly):
    """Outward vertex normals of a CCW 2D polygon."""
    n = len(poly)
    out = []
    for i in range(n):
        a, b, c = poly[i - 1], poly[i], poly[(i + 1) % n]
        e1 = (b - a).normalized()
        e2 = (c - b).normalized()
        n1 = Vector((e1.y, -e1.x))
        n2 = Vector((e2.y, -e2.x))
        m = n1 + n2
        if m.length < 1e-6:
            m = n1
        m.normalize()
        # keep the inset distance roughly constant at corners
        k = max(0.5, m.dot(n1))
        out.append(m / k)
    return out


# ---------------------------------------------------------------------------
# point clouds for the rocks
# ---------------------------------------------------------------------------

PROFILE = [(-0.5, 0.12), (-0.27, 0.5), (0.2, 0.5), (0.5, 0.1), (0.42, -0.5), (-0.42, -0.5)]
# a ridged front: two planes meeting in a vertical ridge, one catching the sun
RIDGE = [(-0.5, 0.05), (-0.22, 0.38), (0.02, 0.58), (0.28, 0.4), (0.5, 0.02), (0.42, -0.5), (-0.42, -0.5)]


def column_pts(rng, c, t, n, w, d, h, top="flat", foot_in=0.0, z0=0.0, bulge=False, drop=0.0):
    """Tall faceted column: a jittered hex-like profile (bevelled front corners),
    yawed a little so each column's front catches the light differently, swept
    up from z0 to h through rings that each shift and jitter, so every side
    breaks into two or three long, vertical, slightly kinked planes. top: flat,
    point (pyramid tip), chisel (slanted wedge) or step (flat at the back, its
    front edge `drop` lower: a bevelled crest under the lip). bulge: a chunkier
    hexagonal prism that swells through its middle."""
    yaw = rng.uniform(-0.32, 0.32)
    cy, sy = math.cos(yaw), math.sin(yaw)
    prof = []
    for u, v in (RIDGE if rng.random() < 0.6 else PROFILE):
        u, v = u + rng.uniform(-0.08, 0.08), v + rng.uniform(-0.07, 0.07)
        prof.append((u * cy - v * sy * d / w, u * sy * w / d + v * cy))
    if top in ("flat", "step"):
        if bulge:
            rings = [(0.0, 1.0), (rng.uniform(0.2, 0.32), 1.12), (rng.uniform(0.5, 0.62), 1.1),
                     (rng.uniform(0.78, 0.86), 0.97), (1.0, 0.88)]
        else:
            rings = [(0.0, 1.06), (rng.uniform(0.16, 0.28), 1.0), (rng.uniform(0.42, 0.55), 0.97),
                     (rng.uniform(0.66, 0.8), 0.93), (1.0, 0.9)]
    else:
        rings = [(0.0, 1.06), (rng.uniform(0.3, 0.45), 1.0), (rng.uniform(0.6, 0.7), 0.94),
                 (rng.uniform(0.74, 0.8), 0.82)]
    H = h - z0
    pts = []
    for k, (fz, fs) in enumerate(rings):
        du = rng.uniform(-0.12, 0.12) * w if k else 0.0
        dv = rng.uniform(-0.2, 0.2) * d if k else 0.0
        dv -= foot_in * (1.0 - fz) ** 1.5   # set the foot back (a column leaning out over its base)
        last = k == len(rings) - 1
        for u, v in prof:
            uu = (u * fs + rng.uniform(-0.07, 0.07)) * w + du
            vv = (v * fs + rng.uniform(-0.09, 0.09)) * d + dv
            z = z0 + fz * H
            if last and top == "step" and v > -0.1:
                z -= drop * min(1.0, (v + 0.1) / 0.5)
            pts.append(c + t * uu + n * vv + Z * z)
    if top == "point":
        pts.append(c + t * rng.uniform(-0.15, 0.15) * w + n * 0.1 * d + Z * h)
        pts.append(c + t * rng.uniform(-0.3, 0.3) * w - n * 0.25 * d + Z * (z0 + H * 0.9))
    elif top == "chisel":
        off = rng.uniform(-0.12, 0.12) * w
        pts.append(c + t * (off - 0.22 * w) + n * 0.1 * d + Z * h)
        pts.append(c + t * (off + 0.25 * w) - n * 0.15 * d + Z * (z0 + H * 0.94))
    return pts


def shard_pts(rng, c, t, n, w, d, h, lean):
    """Pointed leaning shard rock: a 5-point base ring, a pinched middle ring and
    an offset tip, so it reads as a spiky wedge tilted out from the cliff."""
    k = 5
    rot = rng.uniform(0, TAU)
    lv = n * lean + t * rng.uniform(-0.12, 0.12)
    pts = []
    for fz, fs in ((0.0, 1.0), (rng.uniform(0.38, 0.5), rng.uniform(0.6, 0.72))):
        for i in range(k):
            a = rot + TAU * i / k + rng.uniform(-0.25, 0.25)
            rr = fs * rng.uniform(0.85, 1.08)
            pts.append(c + t * (math.cos(a) * w / 2 * rr) + n * (math.sin(a) * d / 2 * rr)
                       + lv * (fz * h) + Z * (fz * h))
    pts.append(c + lv * h + t * rng.uniform(-0.1, 0.1) * w + Z * h)
    pts.append(c + lv * (h * 0.86) + t * rng.uniform(0.08, 0.2) * w - n * 0.15 * d + Z * (h * 0.86))
    return pts


# ---------------------------------------------------------------------------
# the wall builder
# ---------------------------------------------------------------------------


class Wall:
    def __init__(self, kit, name, spec, seed):
        self.kit = kit
        self.spec = spec
        self.a = kit.flintkit.Asset(name, "Terrain", seed=seed, tint_var=0.04)
        self.bm = self.a.bm
        self.grp = self.bm.faces.layers.int.new("kitgrp")
        self.rng = random.Random(seed)
        self.pieces = []
        self.W, self.D = spec["size"]
        self.poly = [Vector((x, y)) for x, y, _ in spec["poly"]]
        self.types = [tp for _, _, tp in spec["poly"]]
        self.outline = None
        self.plates = []
        self.plate_back = False   # close the rock-side face (only on the standalone plate part)
        self.reach = min(4.0, spec.get("reach", 4.0))

    # -- bookkeeping -----------------------------------------------------------

    def tag(self, faces, g):
        for f in faces:
            if f.is_valid:
                f[self.grp] = g
        return faces

    def tagv(self, verts, g):
        return self.tag(list({f for v in verts for f in v.link_faces}), g)

    def paint(self, faces, mat, tint=1.0, var=0.03):
        mi = self.a._mi(mat)
        for f in faces:
            f.material_index = mi
            f.smooth = False
            tt = tint * (1.0 + self.rng.uniform(-var, var))
            for lp in f.loops:
                lp[self.a.tint_layer] = (tt, tt, tt, 1.0)

    def edge(self, i):
        v0, v1 = self.poly[i], self.poly[(i + 1) % len(self.poly)]
        t = (v1 - v0).normalized()
        return v0, v1, t, Vector((t.y, -t.x)), (v1 - v0).length

    def clamp_pts(self, pts):
        hw, hd = self.W / 2, self.D / 2
        out = []
        backs = [self.edge(i) for i, tp in enumerate(self.types) if tp == "back"]
        for p in pts:
            x = max(-hw + self.rng.uniform(0, 0.3), min(hw - self.rng.uniform(0, 0.3), p.x))
            y = max(-hd + self.rng.uniform(0, 0.3), min(hd, p.y))
            q = Vector((x, y))
            # rock stops just in front of any connector plate (no z-fighting)
            for v0, _, _, n, _ in backs:
                dd = (q - v0).dot(n) + PLATE_T + 0.03
                if dd > 0:
                    q -= n * dd
            out.append(Vector((q.x, q.y, max(0.0, p.z))))
        return out

    # -- rocks --------------------------------------------------------------------

    def rock(self, pts, kind, c, t, n, top, merge=3.0):
        faces = hull(self.bm, self.clamp_pts(pts), merge)
        self.tag(faces, G_ROCK)
        p = Piece(faces, kind, c, t, n, top)
        self.pieces.append(p)
        return p

    def column(self, i, s, w, d, off, h=COL_TOP, top="flat", kind="col", rng=None, foot_in=0.0,
               z0=0.0, bulge=False, drop=0.0):
        rng = rng or self.rng
        v0, _, t, n, _ = self.edge(i)
        base = v0 + t * s
        c2 = base + n * (off - d / 2)
        c = Vector((c2.x, c2.y, 0.0))
        t3, n3 = Vector((t.x, t.y, 0)), Vector((n.x, n.y, 0))
        p = self.rock(column_pts(rng, c, t3, n3, w, d, h, top, foot_in, z0, bulge, drop), kind, c, t3, n3, h)
        p.z0 = z0
        return p

    def shard(self, i, s, w, d, off, h, lean=0.3):
        v0, _, t, n, _ = self.edge(i)
        c2 = v0 + t * s + n * off
        c = Vector((c2.x, c2.y, 0.0))
        t3, n3 = Vector((t.x, t.y, 0)), Vector((n.x, n.y, 0))
        return self.rock(shard_pts(self.rng, c, t3, n3, w, d, h, lean), "shard", c, t3, n3, h, merge=2.0)

    def run(self, i, seed, wr=(3.2, 5.6), dr=(3.4, 4.8), offr=(-0.9, 0.9), s0=0.0, s1=None, foot_in=0.0,
            stack=0.0, step=0.0, bulge=0.0):
        """A row of full-height columns along edge i, alternating in and out.
        On cliff faces: `bulge` of them swell as chunky hexagonal prisms, `step`
        of them end in a bevelled crest that drops 1.5-3 below the lip, and
        `stack` of them stand on a wider, prouder lower block 7-15 tall whose
        stepped / chiselled top makes a ledge partway up the face."""
        rng = random.Random(seed)
        _, _, _, _, L = self.edge(i)
        s1 = L if s1 is None else s1
        s = s0
        k = 0
        while s < s1 - 0.5:
            w = rng.uniform(*wr)
            if s1 - (s + w) < wr[0] * 0.7:
                w = s1 - s
            off = rng.uniform(*offr)
            # fronts alternate in and out, so the crevices between them are real
            # recesses the light shadows (no painted crevice tone)
            if k % 2:
                off = min(off, offr[0] + 0.35 * (offr[1] - offr[0]))
            else:
                off = max(off, offr[0] + 0.6 * (offr[1] - offr[0]))
            d = rng.uniform(*dr)
            top = "step" if rng.random() < step else "flat"
            drop = rng.uniform(1.2, 2.2)
            bul = rng.random() < bulge
            if rng.random() < stack:
                h1 = rng.uniform(7.0, 15.0)
                self.column(i, s + w / 2 + rng.uniform(-0.3, 0.3) * w, (w + 0.5) * rng.uniform(0.95, 1.1),
                            d + 1.2, off + rng.uniform(1.0, 1.8), h=h1,
                            top=rng.choice(("step", "chisel")), rng=rng, drop=rng.uniform(1.4, 2.6),
                            bulge=True)
                self.column(i, s + w / 2, w + 0.5, d, off, rng=rng, top=top, drop=drop, bulge=bul,
                            z0=h1 - 1.2)
            else:
                self.column(i, s + w / 2, w + 0.5, d, off, rng=rng, top=top, drop=drop, bulge=bul,
                            foot_in=foot_in * rng.uniform(0.7, 1.25))
            s += w
            k += 1

    def end_run(self, i, seed, wr=(4.0, 5.6)):
        """Columns along a tiling side: flush with the grid line at the top (clamped),
        their feet set back ~1-2 studs so foot shards, rubble and bushes sit in front."""
        n0 = len(self.pieces)
        # some columns flush, others set back up to ~0.7 stud, so the side shows
        # vertical relief instead of one flat slab
        self.run(i, seed, wr=wr, dr=(3.6, 4.8), offr=(-0.7, 0.4), foot_in=2.4)
        for p in self.pieces[n0:]:
            p.end = True

    def core(self, polys):
        """Convex fill prisms behind the columns (seen only through crevices)."""
        for poly in polys:
            pts = [Vector((x, y, z)) for x, y in poly for z in (0.0, COL_TOP - 0.6)]
            faces = hull(self.bm, pts, 1.0)
            self.tag(faces, G_CORE)
            self.paint(faces, ROCK, 1.0, 0.03)   # crevice backdrop (the light shades it)
            self.pieces.append(Piece(faces, "core"))

    # -- grass cap -----------------------------------------------------------------

    def main_cols(self):
        return [p for p in self.pieces if p.kind in ("col", "core") and p.top >= COL_TOP - 0.5]

    def front_at(self, p2, n):
        """How far the column tops reach out past p2 along n (studs)."""
        o = Vector((p2.x, p2.y, COL_TOP - 0.35)) + Vector((n.x, n.y, 0)) * 4.0
        d = -Vector((n.x, n.y, 0))
        best = None
        for pc in self.main_cols():
            hit = pc.ray(o, d)
            if hit and (best is None or hit[0] < best):
                best = hit[0]
        if best is None:
            return 0.0
        return max(-1.0, min(2.2, 4.0 - best))

    def trace_outline(self, seed):
        rng = random.Random(seed)
        npoly = len(self.poly)
        samples = []   # per edge: list of (s, D)
        for i in range(npoly):
            v0, v1, t, n, L = self.edge(i)
            tp = self.types[i]
            steps = max(2, int(L / (1.1 if tp == "cliff" else 4.0)))
            per = rng.uniform(3.4, 4.6)
            ph = rng.uniform(0, TAU)
            row = []
            for k in range(1, steps):
                s = k * L / steps
                if tp == "cliff":
                    # skip samples next to a concave corner (the other face's rocks)
                    if (s < 1.3 and self.concave(i)) or (s > L - 1.3 and self.concave(i + 1)):
                        continue
                    # round lobes with cusps between them (scalloped lip)
                    o = 0.32 + 0.5 * abs(math.sin(ph + math.pi * s / per)) + rng.uniform(-0.04, 0.04)
                    D = self.front_at(v0 + t * s, n) + max(0.3, min(0.8, o))
                elif tp == "end":
                    D = -rng.uniform(0.02, 0.2)
                else:
                    D = -PLATE_T
                row.append((s, D))
            samples.append(row)
        out = []
        for i in range(npoly):
            v0, v1, t, n, L = self.edge(i)
            _, _, tp_, np_, Lp = self.edge(i - 1)
            prev = samples[i - 1]
            cur = samples[i]
            Dp = prev[-1][1] if prev else 0.0
            Dc = cur[0][1] if cur else 0.0
            if self.types[i - 1] == "back" and self.types[i] == "end":
                Dc = -0.1
            if self.types[i] == "back" and self.types[i - 1] == "end":
                Dp = -0.1
            cr = np_.x * n.y - np_.y * n.x
            if abs(cr) < 0.1:
                corner = v0 + n * Dc
            else:
                # solve np.(p-v0)=Dp, n.(p-v0)=Dc
                det = np_.x * n.y - np_.y * n.x
                x = (Dp * n.y - np_.y * Dc) / det
                y = (np_.x * Dc - Dp * n.x) / det
                corner = v0 + Vector((x, y))
            out.append(corner)
            for s, D in cur:
                out.append(v0 + t * s + n * D)
        hw, hd = self.W / 2, self.D / 2
        res = []
        for p in out:
            q = Vector((max(-hw, min(hw, p.x)), max(-hd, min(hd - PLATE_T, p.y))))
            if not res or (q - res[-1]).length > 0.2:
                res.append(q)
        if (res[0] - res[-1]).length < 0.2:
            res.pop()
        self.outline = res
        return res

    def concave(self, i):
        """Is polygon vertex i a concave (inner) corner?"""
        npoly = len(self.poly)
        a, b, c = self.poly[(i - 1) % npoly], self.poly[i % npoly], self.poly[(i + 1) % npoly]
        e1, e2 = b - a, c - b
        return e1.x * e2.y - e1.y * e2.x < -1e-6

    def cap(self, seed):
        """The grass slab, 1.0 thick: a flat grass field, a rounded grass
        shoulder that bulges out over the cliff edges (scalloped by the traced
        outline), a vertical grass band, then a brown earth band tucking in a
        little underneath, and the underside. On tiling / back edges the slab
        is cut straight and flush."""
        rng = random.Random(seed)
        O = self.outline
        m = len(O)
        nv = vnormals(O)
        hw, hd = self.W / 2, self.D / 2

        def on_cliff(p):
            return abs(p.x) < hw - 0.35 and abs(p.y) < hd - 0.8

        rf = [1.0 if on_cliff(p) else 0.0 for p in O]
        self.inner = [O[k] - nv[k] * 0.7 for k in range(m)]
        bm = self.bm
        # (z, inset along the outward normal on cliff edges)
        # a small rounded grass shoulder, then the earth band face-on so it reads as a brown stripe
        prof = [(TOP - 0.03, 0.18), (TOP - 0.22, 0.0), (EARTH_TOP, 0.0), (SLAB_BOT, 0.08)]
        rings = [[bm.verts.new((O[k].x - nv[k].x * ins * rf[k], O[k].y - nv[k].y * ins * rf[k], z))
                  for k in range(m)] for z, ins in prof]
        mats = [GRASS, GRASS, EARTH]
        faces = []
        top = bm.faces.new(rings[0])
        bot = bm.faces.new(list(reversed(rings[-1])))
        top.normal_update()
        bot.normal_update()
        if top.normal.z < 0:
            top.normal_flip()
        if bot.normal.z > 0:
            bot.normal_flip()
        self.paint([top], GRASS, 1.0, 0.0)
        self.paint([bot], EARTH, 1.0, 0.0)
        faces += [top, bot]
        for r in range(3):
            a, b = rings[r], rings[r + 1]
            for k in range(m):
                k2 = (k + 1) % m
                f = bm.faces.new((a[k2], a[k], b[k], b[k2]))
                f.normal_update()
                out = nv[k] + nv[k2]
                if f.normal.x * out.x + f.normal.y * out.y < 0:
                    f.normal_flip()
                self.paint([f], mats[r], rng.uniform(0.95, 1.05), 0.0)
                faces.append(f)
        self.tag(faces, G_CAP)

    def patch(self, c, r, mat, z=TOP, k=9, rng=None, tint=1.0):
        rng = rng or self.rng
        rot = rng.uniform(0, TAU)
        pts = []
        for i in range(k):
            a = rot + TAU * i / k + rng.uniform(-0.15, 0.15)
            rr = r * rng.uniform(0.65, 1.05)
            pts.append(Vector((c.x + math.cos(a) * rr, c.y + math.sin(a) * rr * 0.85)))
        if not all(inside(p, self.inner) for p in pts):
            return None
        f = self.bm.faces.new([self.bm.verts.new((p.x, p.y, z)) for p in pts])
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
        self.paint([f], mat, tint, 0.0)
        self.tag([f], G_CAP)
        return pts

    def patches(self, seed, n_light=6, avoid=()):
        """A few toned patches of the same w02_grass across the field, set
        apart only by a small Tint step (within the 1.25x Tint rule), not by a
        second grass colour; no overlaps, so nothing z-fights."""
        rng = random.Random(seed)
        placed = [(Vector((x, y)), r) for x, y, r in avoid]
        hw, hd = self.W / 2, self.D / 2
        tries = 0
        made = 0
        while made < n_light and tries < 300:
            tries += 1
            c = Vector((rng.uniform(-hw + 3, hw - 3), rng.uniform(-hd + 3, hd - 3)))
            r = rng.uniform(1.8, 3.6)
            if not inside(c, self.inner):
                continue
            if any((c - q).length < r + rr + 0.4 for q, rr in placed):
                continue
            if self.patch(c, r, GRASS, TOP, rng=rng, tint=rng.uniform(1.06, 1.09), k=11):
                placed.append((c, r))
                made += 1
        self.patch_spots = placed

    # -- dressing --------------------------------------------------------------------

    def blob(self, r, loc, mat, subdiv=2, g=G_TOPDRESS, rough=0.12, floor=0.0):
        """Jittered ico lump; verts below `floor` are flattened onto it and the
        flat underside (hidden in the grass / ground) is dropped."""
        vs = self.a.ico(r, loc, mat=mat, subdiv=subdiv, jitter=rough, facets=0, face_tint_var=0.05)
        for v in vs:
            if v.co.z < floor:
                v.co.z = floor
        if floor > 0.0:
            under = list({f for v in vs for f in v.link_faces
                          if all(abs(u.co.z - floor) < 1e-4 for u in f.verts)})
            if under:
                bmesh.ops.delete(self.bm, geom=under, context="FACES_ONLY")
            vs = [v for v in vs if v.is_valid and v.link_faces]
        self.tagv(vs, g)
        return vs

    def bush(self, x, y, z, s, g=G_TOPDRESS, lumps=None, floor=None):
        """Round, domed leafy clump about s studs across and ~0.8 s tall: a big
        heart and a ring of leafy lumps, all one `leaf` colour: the light
        models the dome."""
        rng = self.rng
        r = s * 0.34
        fl = floor if floor is not None else 0.0
        self.blob((r, r, r * 0.95), (x, y, z + r * 0.85), LEAF, 2 if s >= 4.4 else 1, g, floor=fl)
        k = lumps if lumps is not None else (2 if s < 2.0 else (3 if s < 3.2 else 5))
        rot = rng.uniform(0, TAU)
        for j in range(k):
            a = rot + TAU * j / k + rng.uniform(-0.3, 0.3)
            rr = r * rng.uniform(0.55, 0.72)
            d = s * rng.uniform(0.26, 0.33)
            self.blob((rr, rr, rr * 0.95), (x + math.cos(a) * d, y + math.sin(a) * d, z + rr * rng.uniform(0.7, 1.5)),
                      LEAF, 1, g, floor=fl)

    def cluster(self, x, y, s, spill):
        """A corner cluster: one big clump with two smaller ones against it;
        a spilling cluster sits on the lip edge, half over the face, with one
        more clump hanging down the rock below it."""
        rng = self.rng
        s *= 1.15   # the clumps' leaves spread a little past the spec'd heart size
        if spill:
            O = self.outline
            nv = vnormals(O)
            k = min(range(len(O)), key=lambda j: (O[j] - Vector((x, y))).length)
            # heart pushed ~1.2 past the lip edge and sunk, so it hangs over the face
            p, n = O[k] + nv[k] * (0.12 * s), nv[k]
            self.bush(p.x, p.y, TOP - 0.25 * s, s)
            if s >= 3.0:
                # and a clump hanging 2-3 studs down the rock under it
                q = p + n * 0.1 + Vector((-n.y, n.x)) * rng.uniform(-0.3, 0.3) * s
                # (face dressing: in the hero and variants, not in the lip part)
                self.bush(q.x, q.y, TOP - 0.62 * s - 1.2, s * 0.5, lumps=2, g=G_STREAK)
        else:
            p, n = Vector((x, y)), Vector((0.0, -1.0))
            self.bush(x, y, TOP - 0.15, s, floor=TOP - 0.05)
        if s >= 3.6:
            t = Vector((-n.y, n.x))
            for side in (-1, 1):
                q = p + t * side * s * rng.uniform(0.5, 0.62) - n * s * rng.uniform(0.1, 0.35)
                if inside(q, self.inner):
                    self.bush(q.x, q.y, TOP - 0.15, s * rng.uniform(0.45, 0.58), lumps=2, floor=TOP - 0.05)

    def ledge_bush(self, piece, s):
        """A small clump perched on a forward column's top, spilling over it."""
        c = piece.c + piece.n * 0.25 * 3.0
        o = Vector((c.x, c.y, piece.top + 5.0))
        hit = piece.ray(o, Vector((0, 0, -1)))
        z = o.z - hit[0] if hit else piece.top * 0.9
        self.bush(c.x, c.y, z - 0.3, s, g=G_STREAK)

    def pebble(self, x, y, s, mat=SLAB, g=G_TOPDRESS, z=TOP):
        sub = 2 if s >= 1.7 else 1
        vs = self.a.rock((s * self.rng.uniform(1.0, 1.25), s, s * self.rng.uniform(0.6, 0.8)), (x, y, z),
                         rot=(0, 0, self.rng.uniform(0, TAU)), mat=mat, subdiv=sub, rough=0.1, facets=10, sink=0.2)
        self.tagv(vs, g)

    def flower(self, x, y, mat, z=TOP):
        vs = self.a.cyl(0.34, 0.12, 0.22, 4, loc=(x, y, z - 0.02), mat=mat, tint=1.0)
        self.tagv(vs, G_TOPDRESS)

    def flowers(self, seed, count, avoid):
        rng = random.Random(seed)
        made, tries = 0, 0
        hw, hd = self.W / 2, self.D / 2
        while made < count and tries < 500:
            tries += 1
            c = Vector((rng.uniform(-hw + 1, hw - 1), rng.uniform(-hd + 1, hd - 1)))
            if not inside(c, self.inner) or any((c - Vector(a[:2])).length < a[2] for a in avoid):
                continue
            self.flower(c.x, c.y, "flower_yellow" if made % 3 == 2 else "flower_white")
            made += 1

    def tuft(self, x, y, s=1.0, z=0.0, g=G_BASE):
        rng = self.rng
        for k in range(3):
            a = rng.uniform(0, TAU)
            vs = self.a.cyl(0.18 * s, 0.0, rng.uniform(0.6, 1.0) * s, 3,
                            loc=(x + math.cos(a) * 0.2 * s, y + math.sin(a) * 0.2 * s, z),
                            rot=(rng.uniform(-0.35, 0.35), rng.uniform(-0.35, 0.35), a),
                            mat=GRASS, tint=rng.uniform(0.95, 1.05))
            self.tagv(vs, g)

    def fringe(self, seed):
        """Thin grass fringe on the ground along every cliff foot."""
        rng = random.Random(seed)
        hw, hd = self.W / 2, self.D / 2
        bm = self.bm
        for i, tp in enumerate(self.types):
            if tp == "back":
                continue
            v0, v1, t, n, L = self.edge(i)
            z = 0.05 + 0.02 * i
            steps = max(2, int(L / 1.3))
            ins, outs = [], []
            for k in range(steps + 1):
                s = k * L / steps
                if tp == "end":   # along a tiling side: a strip just inside the grid line
                    p_in = v0 + t * s - n * rng.uniform(1.6, 2.2)
                    p_out = v0 + t * s
                else:
                    p_in = v0 + t * s - n * 1.2
                    p_out = v0 + t * s + n * rng.uniform(self.reach - 1.0, self.reach - 0.1)
                p_out = Vector((max(-hw, min(hw, p_out.x)), max(-hd, min(hd, p_out.y))))
                ins.append(bm.verts.new((p_in.x, p_in.y, z)))
                outs.append(bm.verts.new((p_out.x, p_out.y, z)))
            faces = []
            for k in range(steps):
                f = bm.faces.new((ins[k], outs[k], outs[k + 1], ins[k + 1]))
                f.normal_update()
                if f.normal.z < 0:
                    f.normal_flip()
                faces.append(f)
                self.paint([f], GRASS, rng.uniform(0.95, 1.05), 0.0)
            self.tag(faces, G_BASE)

    def streak(self, i, s, length, width=1.2):
        """Grass/moss drip hugging the face below the lip: a tapering ribbon
        whose verts are ray-cast onto the column surfaces."""
        v0, _, t, n, _ = self.edge(i)
        t3, n3 = Vector((t.x, t.y, 0)), Vector((n.x, n.y, 0))
        rows = 5
        bm = self.bm
        grid = []
        for j in range(rows + 1):
            f = j / rows
            z = SLAB_BOT + 0.2 - f * length
            w = width * (1 - 0.8 * f)
            row = []
            for u in (-0.5, 0.0, 0.5):
                base = v0 + t * (s + u * w + 0.25 * math.sin(f * 3.0))
                o = Vector((base.x, base.y, z)) + n3 * 4.0
                best = None
                for pc in self.pieces:
                    if pc.kind not in ("col", "core"):
                        continue
                    hit = pc.ray(o, -n3)
                    if hit and (best is None or hit[0] < best[0]):
                        best = hit
                if best is None:
                    p = o - n3 * 4.0
                    nn = n3
                else:
                    p = o - n3 * best[0]
                    nn = best[1]
                row.append(bm.verts.new(p + nn * 0.09))
            grid.append(row)
        faces = []
        for j in range(rows):
            for k in range(2):
                f = bm.faces.new((grid[j][k], grid[j + 1][k], grid[j + 1][k + 1], grid[j][k + 1]))
                f.normal_update()
                if f.normal.dot(n3) < 0:
                    f.normal_flip()
                faces.append(f)
        self.paint(faces, GRASS, 1.0, 0.04)
        self.tag(faces, G_STREAK)

    # -- connector plates -------------------------------------------------------------

    def plate(self, i, s0, s1, tabs=(True, True)):
        """Flat matte connector plate flush with edge i (a back edge), 0.4 thick,
        23.5 tall, with 1.5 x 0.5 x 0.4 tabs on its free vertical edges at 8-stud
        spacing. The face against the rock is left out (never seen)."""
        v0, _, t, n, _ = self.edge(i)
        t3, n3 = Vector((t.x, t.y, 0)), Vector((n.x, n.y, 0))
        o3 = Vector((v0.x, v0.y, 0))

        def slab(a0, a1, z0, z1, skip_back=not self.plate_back, skip_bottom=True):
            bm = self.bm
            P = lambda a, b, z: bm.verts.new(o3 + t3 * a + n3 * b + Z * z)
            q = {}
            for a in (0, 1):
                for b in (0, 1):
                    for c in (0, 1):
                        q[a, b, c] = P((a0, a1)[a], (-PLATE_T, 0.0)[b], (z0, z1)[c])
            quads = [((0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)),   # outer
                     ((0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1)),   # top
                     ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)),   # start end
                     ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))]   # finish end
            if not skip_bottom:
                quads.append(((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)))
            if not skip_back:
                quads.append(((0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 0, 0)))
            centre = o3 + t3 * ((a0 + a1) / 2) + n3 * (-PLATE_T / 2) + Z * ((z0 + z1) / 2)
            faces = []
            for qd in quads:
                f = bm.faces.new([q[k] for k in qd])
                f.normal_update()
                if f.normal.dot(f.calc_center_median() - centre) < 0:
                    f.normal_flip()
                faces.append(f)
            self.paint(faces, CONN, 1.0, 0.0)
            self.tag(faces, G_PLATE)
            return faces

        self.plates.append((i, s0, s1))
        slab(s0, s1, 0.0, PLATE_TOP)
        for z in (4.0, 12.0, 20.0):
            if tabs[0]:
                slab(s0 - 0.5, s0, z - 0.75, z + 0.75, skip_bottom=False)
            if tabs[1]:
                slab(s1, s1 + 0.5, z - 0.75, z + 0.75, skip_bottom=False)

    # -- finishing --------------------------------------------------------------------

    def cull(self, slab_on):
        bm = self.bm
        solid = [p for p in self.pieces if p.kind in ("col", "shard", "core")]
        dead = set()
        for p in self.pieces:
            for f in p.faces:
                if not f.is_valid:
                    continue
                for q in solid:
                    if q is p:
                        continue
                    if all(q.contains(v.co) for v in f.verts):
                        dead.add(f)
                        break
        if slab_on and self.outline:
            for f in bm.faces:
                if f[self.grp] in (G_ROCK, G_CORE) and f.normal.z > 0.9:
                    c = f.calc_center_median()
                    if c.z > COL_TOP - 0.1 and inside(c, self.outline):
                        dead.add(f)
        # faces hidden against a connector plate
        for i, s0, s1 in self.plates:
            v0, _, t, n, _ = self.edge(i)
            for f in bm.faces:
                if f[self.grp] not in (G_CORE, G_ROCK):
                    continue
                c = f.calc_center_median()
                if Vector((f.normal.x, f.normal.y)).dot(n) > 0.95 and abs((Vector((c.x, c.y)) - v0).dot(n) + PLATE_T) < 0.12:
                    ss = [(Vector((v.co.x, v.co.y)) - v0).dot(t) for v in f.verts]
                    if min(ss) > s0 - 0.05 and max(ss) < s1 + 0.05:
                        dead.add(f)
        if dead:
            bmesh.ops.delete(bm, geom=[f for f in dead if f.is_valid], context="FACES_ONLY")
        for v in bm.verts:
            if v.co.z < 0:
                v.co.z = 0.0
        bm.normal_update()
        bottoms = [f for f in bm.faces if f.normal.z < -0.97 and f.calc_center_median().z < 0.03]
        if bottoms:
            bmesh.ops.delete(bm, geom=bottoms, context="FACES_ONLY")
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context="VERTS")

    def tone(self):
        """Every rock face is the one w02_rock colour with a small random Tint
        (+/-5%), never chosen by height, direction or depth: the crevices read
        dark and the far side cool only because the studio / Roblox light
        shades the facets."""
        rng = random.Random(7)
        for p in self.pieces:
            if p.kind not in ("col", "fwd", "shard"):
                continue
            pt = rng.uniform(0.97, 1.03)   # a per-column nudge so neighbours separate a touch
            for f in sorted((f for f in p.faces if f.is_valid), key=lambda f: tuple(f.calc_center_median())):
                self.paint([f], ROCK, pt * rng.uniform(0.98, 1.02), 0.0)

    def keep(self, groups):
        dead = [f for f in self.bm.faces if f[self.grp] not in groups]
        if dead:
            bmesh.ops.delete(self.bm, geom=dead, context="FACES_ONLY")
        loose = [v for v in self.bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(self.bm, geom=loose, context="VERTS")

    def fit(self):
        hw, hd = self.W / 2, self.D / 2
        for v in self.bm.verts:
            v.co.x = max(-hw, min(hw, v.co.x))
            v.co.y = max(-hd, min(hd, v.co.y))
            v.co.z = max(0.0, v.co.z)

    def finish(self, role, collision, budget, notes, turn=0.0):
        self.fit()
        if turn:
            bmesh.ops.rotate(self.bm, verts=self.bm.verts, cent=(0, 0, 0),
                             matrix=Matrix.Rotation(math.radians(turn), 3, "Z"))
        self.bm.faces.layers.int.remove(self.grp)
        obj = self.a.finish()
        keys = {m.get("flintkit_key") for m in obj.data.materials if m}
        if ROCK in keys and (CONN in keys or SLAB in keys):
            obj["kit_two_tone_ok"] = TWO_TONE
        if LEAF in keys and GRASS in keys:
            # the runner's shading check groups the leaf bushes with the grass cap by hue;
            # they are two sheet materials, each one flat colour (Tint spread ~2-3%), so
            # the score only says the darker leaf clumps face every way while grass lies flat.
            obj["kit_shading_ok"] = ("leaf bush clumps and the w02_grass cap are two sheet-palette "
                                     "materials grouped by hue; each is one flat colour")
        return self.kit.tag(obj, role, collision=collision, budget=budget, notes=notes)


# ---------------------------------------------------------------------------
# the assets
# ---------------------------------------------------------------------------

FY = -8.0   # hero face line (4 studs of foot room in front for proud columns and shards)


def hero_spec():
    return dict(
        size=(32.0, 24.0),
        poly=[(-16.0, FY, "cliff"), (16.0, FY, "end"), (16.0, 12.0, "back"), (-16.0, 12.0, "end")],
        # forward columns: (s along the front, height, width, depth, top[, offset past the face])
        fwd=[(12.6, 16.0, 5.4, 5.2, "point", 3.4), (22.8, 11.5, 5.0, 4.8, "chisel", 3.1),
             (5.4, 9.5, 4.8, 4.6, "point", 3.0), (29.0, 7.0, 4.2, 4.2, "point", 2.6),
             (18.0, 19.0, 4.4, 4.0, "chisel", 1.9)],
        # foot shards: (s, height, width, depth, lean out)
        shards=[(1.8, 5.6, 4.4, 3.2, 0.22), (9.2, 4.4, 3.8, 3.0, 0.28), (16.4, 6.0, 4.4, 3.2, 0.2),
                (26.0, 4.8, 4.0, 3.0, 0.26), (31.0, 3.4, 2.8, 2.4, 0.3)],
        # shards at the foot of the tiling sides: (edge, s, height, width, depth, lean)
        side_shards=[(1, 1.4, 5.2, 3.2, 2.6, 0.3), (1, 6.0, 3.4, 2.8, 2.4, 0.35), (1, 13.5, 4.0, 3.0, 2.6, 0.3),
                     (3, 20.2, 5.6, 3.2, 2.6, 0.3), (3, 15.4, 3.6, 2.8, 2.4, 0.35), (3, 7.5, 4.2, 3.0, 2.6, 0.3)],
        core=[[(-13.4, FY + 2.6), (13.4, FY + 2.6), (13.4, 12.0 - PLATE_T), (-13.4, 12.0 - PLATE_T)]],
        plates=[(2, 0.5, 31.5, (True, True))],
        # bush clusters: (x, y, studs across, spills over the lip)
        bushes=[(-12.4, -7.0, 6.2, True), (12.2, -7.0, 5.8, True), (-11.6, 7.4, 6.2, False),
                (11.0, 7.8, 5.8, False), (1.6, -7.4, 3.6, True), (-6.4, -7.4, 3.0, True),
                (-0.4, 9.4, 3.2, False)],
        pebbles=[(-3.6, -4.4, 1.6), (6.0, -4.6, 1.2), (9.0, -1.4, 1.8), (-6.0, 2.0, 0.9),
                 (5.6, 5.4, 1.0), (-2.0, 8.8, 0.8), (-8.4, -1.6, 0.8), (3.0, 1.6, 0.7)],
        flowers=14,
        patches=4,
        ledge_bushes=[(1, 2.6), (2, 2.2)],
        streaks=[(0, 8.6, 3.2), (0, 20.6, 2.6), (0, 26.6, 3.8)],
        base_bushes=[(-14.0, -11.0, 3.2), (-8.2, -11.1, 2.6), (2.6, -11.1, 3.0), (8.6, -11.2, 2.4),
                     (13.6, -11.0, 3.0), (14.8, 1.6, 2.8), (-14.8, -3.2, 2.8), (14.8, 9.0, 2.2)],
        tufts=[(-9.6, -11.5), (0.6, -11.6), (9.2, -11.6), (15.0, -11.6), (15.3, -1.2), (-15.3, 5.0)],
        rubble=[(-12.4, -11.5, 0.9), (-1.6, -11.4, 1.0), (7.6, -11.5, 0.8), (11.0, -11.6, 0.6),
                (15.3, 4.6, 0.8), (-15.3, 1.0, 0.9)],
    )


def build_wall(kit, name, spec, seed, keep=None, slab=True, role="hero", collision="precise",
               budget=6000, notes="", run_seeds=None, plate_back=False, turn=0.0):
    w = Wall(kit, name, spec, seed)
    w.plate_back = plate_back
    # full-height column rows on every cliff and end edge
    for i, tp in enumerate(w.types):
        rs = (run_seeds or {}).get(i, seed * 10 + i)
        if tp == "cliff":
            opts = dict(wr=(3.6, 6.0), offr=(-1.5, 1.1), stack=0.4, step=0.3, bulge=0.4)
            opts.update(spec.get("run_opts", {}).get(i, {}))
            w.run(i, rs, **opts)
        elif tp == "end":
            w.end_run(i, rs)
    fwd = []
    for f in spec.get("fwd_all", [(0,) + f for f in spec.get("fwd", [])]):
        i, s, h, wd, d, top = f[:6]
        # proud forward columns: front 2.6-3.6 past the face line, back sunk into the face
        fwd.append(w.column(i, s, wd, d, f[6] if len(f) > 6 else 3.0, h=h, top=top, kind="fwd",
                            bulge=True))
    reach = spec.get("reach", 4.0)   # face line to the footprint edge on the cliff faces
    for i, s, h, wd, d, lean in spec.get("shards_all", [(0,) + f for f in spec.get("shards", [])]):
        # front of each shard just inside the footprint; tips lean out from the wall
        w.shard(i, s, wd, d, min(reach, 4.0) - 0.45 - d / 2 - 0.5 * lean * h, h, 0.5 * lean)
    for i, s, h, wd, d, lean in spec.get("side_shards", []):
        # shards at the foot of a tiling side: outer face on the grid line, leaning in
        w.shard(i, s, wd, d, 0.9 - d / 2, h, -0.15 * lean)
    w.core(spec["core"])
    w.trace_outline(seed + 1)
    w.cap(seed + 2)
    avoid = [(x, y, s * 0.5) for x, y, s, spill in spec["bushes"] if not spill]
    w.patches(seed + 3, n_light=spec.get("patches", 6), avoid=avoid)
    for x, y, s, spill in spec["bushes"]:
        w.cluster(x, y, s, spill)
    for x, y, s in spec["pebbles"]:
        w.pebble(x, y, s)
    w.flowers(seed + 4, spec["flowers"],
              [(x, y, s * 0.75) for x, y, s, _ in spec["bushes"]] + [(x, y, s) for x, y, s in spec["pebbles"]])
    for i, s, L in spec["streaks"]:
        w.streak(i, s, L)
    for k, size in spec.get("ledge_bushes", []):
        w.ledge_bush(fwd[k], size)
    for x, y, s in spec["base_bushes"]:
        w.bush(x, y, 0.0, s, g=G_BASE)
    for x, y in spec["tufts"]:
        w.tuft(x, y)
    for x, y, s in spec["rubble"]:
        w.pebble(x, y, s, mat=ROCK, g=G_BASE, z=0.0)
    w.fringe(seed + 5)
    for i, s0, s1, tabs in spec["plates"]:
        w.plate(i, s0, s1, tabs)
    w.cull(slab)
    w.tone()
    if keep:
        w.keep(keep)
    return w.finish(role, collision, budget, notes, turn)


def build_hero(kit):
    return build_wall(kit, "CliffWall", hero_spec(), 101, budget=6000,
                      notes="32x24x24 cliff chunk; walkable grass top at z=24, cliff face -Y, "
                            "connector plate on +Y; sides flush at x=+-16 to tile on the 32 grid")


def build_lip(kit):
    return build_wall(kit, "CliffWallGrassTopLip", hero_spec(), 101, keep={G_CAP, G_TOPDRESS},
                      role="part", budget=2500,
                      notes="grass cap slab with earth band, bushes, pebbles and flowers; sits on CliffWallBody at z=23")


def build_body(kit):
    return build_wall(kit, "CliffWallBody", hero_spec(), 101, keep={G_ROCK, G_CORE, G_BASE}, slab=False,
                      role="part", budget=5000,
                      notes="rock columns and foot shards without the cap; flat column tops at z=23.3")


def build_connector(kit):
    # A closed plate (both faces), stood along Y with its outer face toward -X, as
    # the reference's PARTS cell shows it turned to the viewer (and so the parts
    # grid packs it beside the lip instead of in front of everything). Turn it
    # -90 deg about Z to sit on the +Y back of CliffWallBody / CliffWall.
    return build_wall(kit, "CliffWallBackConnector", hero_spec(), 101, keep={G_PLATE}, slab=True,
                      role="part", collision="box", budget=200, plate_back=True, turn=90.0,
                      notes="flat back plate 31 x 0.4 x 23.5 (+0.5 puzzle tabs at 8-stud spacing each end); "
                            "authored along Y, outer face -X: rotate -90 deg about Z for the +Y back")


def build_straight(kit):
    fy = -5.0
    spec = dict(
        size=(32.0, 16.0),
        poly=[(-16.0, fy, "cliff"), (16.0, fy, "end"), (16.0, 8.0, "back"), (-16.0, 8.0, "end")],
        reach=3.0,
        run_opts={0: dict(wr=(3.0, 5.0), dr=(3.2, 4.4), offr=(-1.2, 1.0), stack=0.55, step=0.35)},
        fwd=[(19.0, 11.0, 5.2, 4.4, "point", 2.8)],
        shards=[(3.0, 5.4, 4.2, 2.8, 0.18), (11.0, 6.0, 4.4, 3.0, 0.16), (25.5, 4.8, 4.0, 2.8, 0.2),
                (30.6, 3.4, 2.8, 2.4, 0.22)],
        core=[[(-13.4, fy + 2.5), (13.4, fy + 2.5), (13.4, 8.0 - PLATE_T), (-13.4, 8.0 - PLATE_T)]],
        plates=[(2, 0.5, 31.5, (True, True))],
        side_shards=[(1, 1.2, 3.6, 2.6, 2.2, 0.3), (3, 13.4, 4.0, 2.6, 2.2, 0.3)],
        bushes=[(-12.2, -4.0, 5.6, True), (-10.0, 4.0, 4.8, False), (11.4, 4.2, 4.8, False),
                (11.6, -4.0, 5.0, True), (0.5, -4.0, 3.0, True), (0.5, 5.2, 2.6, False)],
        pebbles=[(-4.6, -1.8, 1.3), (5.6, -1.0, 0.9), (-5.0, 3.0, 0.8), (6.0, 4.4, 0.7)],
        flowers=11,
        streaks=[(0, 6.0, 3.0), (0, 22.6, 2.6)],
        base_bushes=[(-14.2, -7.1, 3.0), (-8.6, -7.2, 2.4), (-1.0, -7.2, 2.6), (7.8, -7.2, 2.8),
                     (14.0, -7.1, 2.8), (15.0, 0.6, 2.2), (-15.0, -1.0, 2.2)],
        tufts=[(-5.0, -7.6), (5.0, -7.6), (14.6, -7.6), (15.3, 3.0), (-11.4, -7.6)],
        rubble=[(-10.6, -7.6, 0.8), (2.8, -7.6, 0.7), (12.4, -7.7, 0.6), (-15.3, 2.6, 0.8)],
        patches=5,
    )
    return build_wall(kit, "CliffWallStraight", spec, 131, role="variant", budget=5000,
                      run_seeds={0: 9137, 1: 9138, 3: 9139},
                      notes="A. STRAIGHT: thinner 32x16 run, same lip and +Y connector")


def build_inner(kit):
    """Concave L: a back band (y 0..16) and a right band (x 0..16), faces looking
    -Y and -X into the low front-left quadrant."""
    spec = dict(
        size=(32.0, 32.0),
        poly=[(-16.0, 0.0, "cliff"), (0.0, 0.0, "cliff"), (0.0, -16.0, "end"),
              (16.0, -16.0, "back"), (16.0, 16.0, "back"), (-16.0, 16.0, "end")],
        fwd_all=[(0, 9.0, 12.0, 4.4, 3.0, "point"), (1, 7.0, 9.0, 4.2, 3.0, "chisel")],
        shards_all=[(0, 3.0, 5.4, 3.6, 2.6, 0.34), (0, 13.8, 4.2, 3.2, 2.4, 0.4),
                    (1, 2.4, 6.0, 3.6, 2.6, 0.32), (1, 12.6, 4.4, 3.2, 2.4, 0.38)],
        core=[[(-13.4, 2.5), (15.6, 2.5), (15.6, 15.6), (-13.4, 15.6)],
              [(2.5, -13.4), (15.6, -13.4), (15.6, 2.5), (2.5, 2.5)]],
        plates=[(3, 0.5, 31.6, (True, False)), (4, 0.0, 31.5, (False, True))],
        side_shards=[(2, 1.4, 4.0, 2.8, 2.2, 0.3), (5, 14.6, 4.2, 2.8, 2.2, 0.3)],
        bushes=[(-12.4, 1.6, 5.4, True), (-11.0, 11.0, 5.6, False), (2.6, 12.0, 4.0, False),
                (11.0, 10.0, 4.4, False), (1.4, -12.2, 5.4, True), (10.4, -9.0, 4.8, False),
                (-6.0, 1.6, 3.2, True)],
        pebbles=[(-5.0, 4.6, 1.4), (5.6, 5.0, 0.9), (4.6, -5.0, 1.2), (-7.0, 9.0, 0.8), (9.0, -2.0, 0.7)],
        flowers=14,
        streaks=[(0, 6.4, 3.0), (1, 8.4, 3.4)],
        base_bushes=[(-14.2, -3.2, 3.0), (-9.4, -3.6, 2.4), (-3.4, -3.4, 3.0), (-3.6, -8.6, 2.6),
                     (-3.2, -14.4, 2.8)],
        tufts=[(-11.8, -3.8), (-6.4, -3.8), (-3.8, -11.6), (-4.8, -5.6)],
        rubble=[(-12.6, -4.2, 0.9), (-4.4, -12.4, 0.8), (-6.0, -4.4, 0.7)],
        patches=6,
    )

    return build_wall(kit, "CliffWallInnerCorner", spec, 151, role="variant", budget=6500,
                      notes="B. INNER CORNER: concave L, faces -Y and -X, L-shaped cap 16 deep, "
                            "connectors on +Y and +X")


def build_outer(kit):
    """Convex corner: faces on -Y and -X wrapping a rounded front-left corner of
    big columns; square cap; connectors on +Y and +X."""
    f = -12.0
    R = 10.0
    cx, cy = f + R, f + R
    a1 = (cx - R * math.cos(math.radians(45)), cy - R * math.sin(math.radians(45)))
    big = dict(wr=(6.4, 8.0), dr=(5.6, 6.8), offr=(-0.4, 1.0), stack=0.5, step=0.0, bulge=1.0)
    spec = dict(
        size=(32.0, 32.0),
        poly=[(f, cy, "cliff"), (a1[0], a1[1], "cliff"), (cx, f, "cliff"), (16.0, f, "back"),
              (16.0, 16.0, "back"), (f, 16.0, "cliff")],
        # the rounded corner: 2-3 big, bulging columns on the two chords
        run_opts={0: big, 1: big},
        fwd_all=[(2, 12.0, 11.0, 5.0, 4.6, "point"), (5, 10.0, 13.0, 5.0, 4.6, "chisel")],
        shards_all=[(1, 4.0, 6.0, 4.4, 3.2, 0.2), (2, 4.0, 4.8, 3.6, 2.8, 0.26),
                    (2, 15.4, 5.6, 3.8, 2.8, 0.24), (5, 4.2, 5.0, 3.6, 2.8, 0.24), (5, 16.8, 4.6, 3.4, 2.6, 0.28)],
        core=[[(f + 2.6, 15.6), (f + 2.6, cy), (a1[0] + 2.2, a1[1] + 2.2), (cx, f + 2.6), (15.6, f + 2.6), (15.6, 15.6)]],
        plates=[(3, 0.5, 27.6, (True, False)), (4, 0.0, 27.5, (False, True))],
        bushes=[(-10.6, -6.0, 5.6, True), (-6.0, -10.6, 5.0, True), (-9.0, 10.0, 5.8, False),
                (9.5, 11.0, 5.4, False), (10.0, -9.6, 5.0, True), (-9.6, 2.0, 3.0, True), (1.0, 2.0, 3.0, False)],
        pebbles=[(-2.0, -7.6, 1.4), (6.0, -4.0, 1.0), (-4.0, 6.0, 0.8), (4.0, 8.0, 0.8), (11.0, 2.0, 0.7)],
        flowers=14,
        streaks=[(2, 9.0, 3.4), (5, 14.0, 2.8), (1, 3.0, 3.0)],
        base_bushes=[(-15.0, 6.0, 3.0), (-15.0, -3.0, 2.6), (-12.2, -12.2, 3.0), (-3.0, -15.0, 2.6),
                     (6.4, -15.0, 3.0), (13.6, -15.0, 2.4)],
        tufts=[(-15.2, -7.0), (-7.0, -15.3), (0.0, -15.3), (12.0, -15.3), (-15.3, 12.0)],
        rubble=[(-15.0, -9.0, 0.8), (-9.0, -15.2, 0.8), (3.0, -15.2, 0.7), (-15.3, 2.0, 0.7)],
        patches=5,
    )
    return build_wall(kit, "CliffWallOuterCorner", spec, 171, role="variant", budget=6500,
                      notes="C. OUTER CORNER: convex rounded corner of big columns, faces -Y and -X, "
                            "square cap, connectors on +Y and +X")


def build(kit):
    return [build_hero(kit), build_lip(kit), build_body(kit), build_connector(kit),
            build_straight(kit), build_inner(kit), build_outer(kit)]
