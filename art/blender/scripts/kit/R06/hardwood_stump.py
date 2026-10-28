"""R06 row 2: HardwoodStump resource node (hero, parts, drops, depleted).

Hero = faceted lofted trunk (alternating-offset rings -> triangular facets and
vertical ridges) + 5 separate convex-hull buttress-root wedges that sweep out
and down into the ground, + leaf tufts sitting in the valleys between roots.
"""
import math
import random

import bmesh
from mathutils import Vector

SUBJECT = "HardwoodStump"
ROW = 2
HERO_AZIMUTH = -22

PALETTE = {
    "r06_cutwood": ("#E0B27C", 0.85, 0, 0),
    "r06_hardbark": ("#5B3D2E", 0.92, 0, 0),
    "r06_leaf": ("#3F9A2C", 0.7, 0, 0),
}

BARK, CUT, LEAF = "r06_hardbark", "r06_cutwood", "r06_leaf"

# root azimuths (deg, CCW from +X; front = 270)
ROOT_AZ = [30, 115, 170, 240, 305]
# valleys between roots where the leaf tufts sit: right, right-rear, front-left, front-centre
VALLEYS = [322, 352, 205, 272]


def _hull(a, pts, mat):
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    res = bmesh.ops.convex_hull(bm, input=vs)
    junk = list({g for g in res.get("geom_interior", []) + res.get("geom_unused", [])
                 if isinstance(g, bmesh.types.BMVert)})
    if junk:
        bmesh.ops.delete(bm, geom=junk, context="VERTS")
    verts = [g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)]
    a._finish(verts, mat)
    return verts


def _root_pts(rng, prof, az=0.0, bend=0.0, hs=1.0, us=1.0):
    """Points of one wedge segment. prof = [(u, half_width_base, ridge_z, half_width_top)].
    Returned in world coords rotated to azimuth az (deg); bend yaws along u."""
    pts = []
    for u, wb, zr, wt in prof:
        u *= us
        zr *= hs
        a_ = math.radians(az + bend * u)
        c, s = math.cos(a_), math.sin(a_)
        loc = [(u, -wb, 0.0), (u, wb, 0.0),
               (u, -wt, zr * 0.82), (u, wt, zr * 0.86),
               (u + rng.uniform(-0.1, 0.1), rng.uniform(-0.12, 0.12), zr)]
        for x, y, z in loc:
            x += rng.uniform(-0.06, 0.06)
            y += rng.uniform(-0.06, 0.06)
            z = max(0.0, z + (rng.uniform(-0.05, 0.05) if z > 0 else 0))
            pts.append((x * c - y * s, x * s + y * c, z))
    return pts


ROOT_A = [(2.0, 2.0, 4.4, 0.9), (3.6, 1.9, 3.5, 0.8), (4.8, 1.55, 2.2, 0.62)]
ROOT_B = [(4.6, 1.55, 2.4, 0.62), (5.7, 1.1, 1.1, 0.42), (6.5, 0.6, 0.35, 0.2)]


def _roots(a, rng, azs, hs=1.0, us=1.0):
    for az in azs:
        az = az + rng.uniform(-4, 4)
        bend = rng.choice([-1, 1]) * rng.uniform(2.0, 4.0)
        _hull(a, _root_pts(rng, ROOT_A, az, bend, hs, us), BARK)
        _hull(a, _root_pts(rng, ROOT_B, az, bend, hs, us), BARK)


def _trunk(a, rng, zs, rs, n, top_z, cap_loops, rim_z=None):
    """Faceted lofted trunk. Rings alternate a half-step offset so the sides
    become triangular facets with vertical ridges. top_z(x, y) is the flat
    (tilted) cut plane, rim_z(x, y, th) optionally overrides the rim height
    (chip notch / jagged break). Cap loops (scale, dz) step inwards."""
    bm = a.bm
    ridge = [(0.22 if j % 2 == 0 else -0.08) + rng.uniform(-0.1, 0.1) for j in range(n)]
    rings = []
    nz = len(zs)
    for i, z in enumerate(zs):
        off = (i % 2) * 0.5
        ring = []
        for j in range(n):
            th = 2 * math.pi * (j + off) / n + 0.13
            r = rs[i] + ridge[j] * (0.5 if off else 1.0) + rng.uniform(-0.06, 0.06)
            x, y = r * math.cos(th), r * math.sin(th)
            if i == nz - 1:
                zz = rim_z(x, y, th) if rim_z else top_z(x, y)
            elif i == 0:
                zz = 0.0
            else:
                zz = z + rng.uniform(-0.12, 0.12)
            ring.append(bm.verts.new((x, y, zz)))
        rings.append(ring)
    side = []
    for i in range(nz - 1):
        lo, hi = rings[i], rings[i + 1]
        lo_off = i % 2
        for j in range(n):
            k = (j + 1) % n
            if lo_off == 0:      # hi is shifted +half: hi[j] sits between lo[j], lo[k]
                side.append(bm.faces.new((lo[j], lo[k], hi[j])))
                side.append(bm.faces.new((lo[k], hi[k], hi[j])))
            else:                # lo shifted +half: lo[j] sits between hi[j], hi[k]
                side.append(bm.faces.new((lo[j], hi[k], hi[j])))
                side.append(bm.faces.new((lo[j], lo[k], hi[k])))
    rim = rings[-1]
    prev = rim
    cap = []
    for s, dz in cap_loops:
        loop = []
        for v in rim:
            x, y = v.co.x * s, v.co.y * s
            loop.append(bm.verts.new((x, y, top_z(x, y) + dz)))
        for j in range(n):
            k = (j + 1) % n
            cap.append(bm.faces.new((prev[j], prev[k], loop[k], loop[j])))
        prev = loop
    cap.append(bm.faces.new(prev))
    verts = list({v for f in side + cap for v in f.verts})
    a._finish(verts, BARK)
    ci = a._mi(CUT)
    for f in cap:
        f.material_index = ci
    bmesh.ops.recalc_face_normals(bm, faces=side + cap)
    return verts


def _leaf_tuft(a, rng, loc, size, n=6):
    """Full leaf tuft: a small multi-lobed clump core plus broad pointed blades."""
    x0, y0, z0 = loc
    a.leaf_cluster(size * 0.5, (x0, y0, z0 + size * 0.25), LEAF, lobes=6, squash=0.75,
                   floor=0.0, seed=rng.randint(0, 999))
    base_az = rng.uniform(0, 360)
    for i in range(n):
        az = math.radians(base_az + i * 360.0 / n + rng.uniform(-15, 15))
        pitch = math.radians(rng.uniform(25, 55))
        L = size * rng.uniform(0.8, 1.05)
        w = L * 0.42
        d = Vector((math.cos(az) * math.cos(pitch), math.sin(az) * math.cos(pitch), math.sin(pitch)))
        side = Vector((-math.sin(az), math.cos(az), 0))
        up = d.cross(side).normalized()
        b = Vector((x0, y0, z0 + 0.15))
        tip = b + d * L
        mid = b + d * (L * 0.45)
        pts = [b, tip, mid + side * w, mid - side * w, mid + up * (w * 0.3), mid - up * (w * 0.1)]
        _hull(a, [(p.x, p.y, max(p.z, 0.02)) for p in pts], LEAF)


def _tufts(a, rng, specs):
    for ang, rad, size in specs:
        th = math.radians(ang)
        _leaf_tuft(a, rng, (rad * math.cos(th), rad * math.sin(th), 0.0), size)


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []
    chips = ["#E0B27C", "#5B3D2E"]
    N = 12
    zs = [0, 1.0, 2.2, 3.5, 4.9, 6.3]
    rs = [4.3, 3.95, 3.55, 3.22, 3.05, 3.05]

    # ---- hero --------------------------------------------------------------
    a = fk.Asset("HardwoodStump", "R06 HardwoodStump")
    rng = random.Random(62)

    def hero_top(x, y):
        return 6.25 + 0.1 * y                  # rear (+Y) slightly higher: tilted cut

    def hero_rim(x, y, th):
        z = hero_top(x, y)
        if 70 <= math.degrees(th) % 360 <= 105:   # chip notch on the rear edge only
            z -= 0.5
        return z

    _trunk(a, rng, zs, rs, N, hero_top,
           [(0.9, 0.0), (0.9, -0.12), (0.66, -0.12), (0.66, 0.0), (0.42, 0.0), (0.42, -0.12)],
           rim_z=hero_rim)
    _roots(a, rng, ROOT_AZ)
    _tufts(a, rng, [(VALLEYS[0], 5.0, 2.3), (VALLEYS[1], 5.6, 2.2),
                    (VALLEYS[2], 5.0, 2.4), (VALLEYS[3], 5.0, 2.2)])
    o = a.finish()
    o["kit_shading_ok"] = "pale r06_cutwood is the real cut-wood top, not a lit shade of the bark"
    vfx.add(o, "harvest_hit", (0, -3.3, 3.2), color=chips)
    vfx.add(o, "harvest_deplete", (0, 0, 0.2))
    out.append(kit.tag(o, "hero", collision="hull", budget=5000,
                       notes="Hardwood stump node. harvest_hit: wood chips on the trunk front at mid "
                             "height; harvest_deplete: burst at the base centre when it becomes the "
                             "LowStump. Cut face is real cut wood (r06_cutwood)."))

    # ---- parts ---------------------------------------------------------------
    a = fk.Asset("HardwoodStumpCutFace", "R06 HardwoodStump")
    rng = random.Random(7)
    bm = a.bm
    M = 10
    rim_b, rim_t = [], []
    for j in range(M):
        th = 2 * math.pi * j / M + 0.15
        r = 3.25 * rng.uniform(0.95, 1.03)
        if j == 3:
            r *= 0.86                            # small notch in the edge
        rim_b.append(bm.verts.new((r * math.cos(th), r * math.sin(th), 0)))
        rim_t.append(bm.verts.new((r * math.cos(th), r * math.sin(th), 0.8)))
    fs = [bm.faces.new(list(reversed(rim_b)))]
    for j in range(M):
        k = (j + 1) % M
        fs.append(bm.faces.new((rim_b[j], rim_b[k], rim_t[k], rim_t[j])))
    prev = rim_t
    for s, z in [(0.86, 0.8), (0.86, 0.7), (0.62, 0.7), (0.62, 0.8), (0.38, 0.8), (0.38, 0.7)]:
        loop = [bm.verts.new((v.co.x * s, v.co.y * s, z)) for v in rim_t]
        for j in range(M):
            k = (j + 1) % M
            fs.append(bm.faces.new((prev[j], prev[k], loop[k], loop[j])))
        prev = loop
    fs.append(bm.faces.new(prev))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    a._finish(list({v for f in fs for v in f.verts}), CUT)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500,
                       notes="Separate cut-face slice with stepped rings; sits on HardwoodStumpBody."))

    a = fk.Asset("HardwoodStumpBody", "R06 HardwoodStump")
    rng = random.Random(62)
    _trunk(a, rng, [0, 1.0, 2.3, 3.6, 4.8, 5.9], rs, N, lambda x, y: 5.9,
           [(0.75, 0.0), (0.75, -0.06)])
    _roots(a, rng, ROOT_AZ)
    _tufts(a, rng, [(VALLEYS[2], 5.0, 2.1)])
    o = a.finish()
    o["kit_shading_ok"] = "pale r06_cutwood is the real cut-wood top, not a lit shade of the bark"
    out.append(kit.tag(o, "part", collision="hull", budget=1500,
                       notes="Stump body with 5 buttress roots, flat lower top for the CutFace slice."))

    a = fk.Asset("HardwoodStumpRoot", "R06 HardwoodStump")
    rng = random.Random(3)
    prof = [(0.0, 1.25, 2.5, 0.5), (1.0, 1.2, 2.2, 0.45), (2.2, 1.0, 1.3, 0.35), (4.0, 0.45, 0.3, 0.12)]
    vs = _hull(a, _root_pts(rng, prof, 0.0, 0.0), BARK)
    a.transform(vs, (-2.0, 0, 0))
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=1500,
                       notes="Single buttress-root wedge module to add around stump bodies."))

    # ---- drops ---------------------------------------------------------------
    a = fk.Asset("HardwoodStumpChunk", "R06 HardwoodStump")
    rng = random.Random(11)
    pts = [(-1.0, -0.55, 0.15), (-1.0, 0.6, 0.1), (-1.0, 0.5, 1.35), (-1.0, -0.45, 1.45),
           (-0.3, -0.85, 0.0), (-0.2, 0.8, 0.0), (-0.4, -0.75, 1.7), (-0.3, 0.7, 1.75),
           (0.6, -0.8, 0.05), (0.7, 0.75, 0.1), (0.5, -0.6, 1.55), (0.6, 0.55, 1.45),
           (1.0, -0.2, 0.3), (1.05, 0.25, 0.9), (0.9, -0.15, 1.2), (0.1, 0.95, 0.9),
           (0.2, -0.95, 0.8), (-0.1, 0.0, 1.9)]
    pts = [(x + rng.uniform(-0.06, 0.06), y + rng.uniform(-0.06, 0.06), z) for x, y, z in pts]
    pts = [(x, y, max(0.0, z)) for x, y, z in pts]
    vs = _hull(a, pts, BARK)
    a.transform(vs, rot=(0, 0, math.radians(90)))
    ci = a._mi(CUT)
    for f in {f for v in vs for f in v.link_faces}:
        f.normal_update()
        if f.normal.y < -0.9:
            f.material_index = ci
    o = a.finish()
    o["kit_shading_ok"] = "one face is the pale cut end of the chunk (real material change)"
    out.append(kit.tag(o, "drop", collision="none", budget=300,
                       notes="Hardwood chunk drop; one pale cut face."))

    a = fk.Asset("HardwoodStumpBarkStrip", "R06 HardwoodStump")
    for dx, rz, L in [(-0.55, 0.6, 2.9), (0.6, 0.5, 2.5)]:
        w, t = 0.75, 0.3
        pts = [(-L / 2, -w / 2, 0), (-L / 2, w / 2, 0), (L / 2, -w * 0.3, 0), (L / 2, w * 0.3, 0),
               (-L / 2, -w / 2, t), (-L / 2, w / 2 * 0.8, t + 0.05), (L / 2, -w * 0.3, t * 0.7),
               (L / 2, w * 0.3, t * 0.75), (0, -w * 0.5, t * 0.5), (0, w * 0.5, t * 0.6)]
        v = _hull(a, pts, BARK)
        a.transform(v, (dx, 0, 0.0), (0, -0.22, rz))
    zmin = min(v.co.z for v in a.bm.verts)
    for v in a.bm.verts:
        v.co.z -= zmin
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="none", budget=300,
                       notes="Pair of tapered hardwood bark strips of slightly different lengths."))

    # ---- depleted -----------------------------------------------------------
    a = fk.Asset("HardwoodStumpLowStump", "R06 HardwoodStump")
    rng = random.Random(5)

    def low_top(x, y):
        return 2.15

    def low_rim(x, y, th):
        return 2.15 + (rng.uniform(0.2, 0.5) if rng.random() < 0.4 else rng.uniform(-0.1, 0.1))

    _trunk(a, rng, [0, 0.8, 1.5, 2.15], [2.7, 2.6, 2.55, 2.5], N, low_top,
           [(0.85, -0.05), (0.62, -0.45), (0.34, -0.85)], rim_z=low_rim)
    _roots(a, rng, ROOT_AZ, hs=0.36, us=0.8)
    _tufts(a, rng, [(VALLEYS[2], 3.6, 1.7), (VALLEYS[0], 3.6, 1.7)])
    o = a.finish()
    o["kit_shading_ok"] = "pale r06_cutwood is the real chopped-wood top, not a lit shade of the bark"
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="Chopped-down low stump: jagged pale top with a hollow dip, flat roots."))
    return out
